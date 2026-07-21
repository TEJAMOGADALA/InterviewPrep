"""Auth routes: /api/auth/*"""
import os
import uuid
import secrets
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Response, Request, Depends

from auth_utils import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    set_auth_cookies, clear_auth_cookies,
    get_current_user, get_jwt_secret, JWT_ALGORITHM,
)
from models import (
    RegisterRequest, LoginRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    UserPublic,
)
import jwt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _user_public(u: dict) -> dict:
    return {
        "id": u["id"],
        "email": u["email"],
        "name": u["name"],
        "role": u.get("role", "user"),
        "avatar_url": u.get("avatar_url"),
        "onboarding_completed": u.get("onboarding_completed", False),
        "created_at": u["created_at"],
    }


async def _check_brute_force(db, identifier: str):
    now = datetime.now(timezone.utc)
    record = await db.login_attempts.find_one({"identifier": identifier})
    if not record:
        return
    if record.get("locked_until"):
        locked_until = datetime.fromisoformat(record["locked_until"])
        if locked_until > now:
            wait_s = int((locked_until - now).total_seconds())
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed attempts. Try again in {wait_s} seconds.",
            )


async def _register_failure(db, identifier: str):
    now = datetime.now(timezone.utc)
    record = await db.login_attempts.find_one({"identifier": identifier})
    count = (record.get("count", 0) if record else 0) + 1
    update = {"identifier": identifier, "count": count, "last_attempt": now.isoformat()}
    if count >= MAX_FAILED_ATTEMPTS:
        update["locked_until"] = (now + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
        update["count"] = 0
    await db.login_attempts.update_one(
        {"identifier": identifier}, {"$set": update}, upsert=True
    )


async def _clear_failures(db, identifier: str):
    await db.login_attempts.delete_one({"identifier": identifier})


@router.post("/register", response_model=UserPublic)
async def register(payload: RegisterRequest, response: Response, request: Request):
    from server import db
    email = payload.email.lower().strip()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": email,
        "name": payload.name.strip(),
        "password_hash": hash_password(payload.password),
        "role": "user",
        "avatar_url": None,
        "onboarding_completed": False,
        "created_at": _now_iso(),
    }
    await db.users.insert_one(user_doc)

    # Auto-create default settings
    from models import UserSettings
    settings = UserSettings(user_id=user_id).model_dump()
    await db.settings.insert_one(settings)

    access = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    set_auth_cookies(response, access, refresh)
    return _user_public(user_doc)


@router.post("/login", response_model=UserPublic)
async def login(payload: LoginRequest, response: Response, request: Request):
    from server import db
    email = payload.email.lower().strip()
    ip = request.client.host if request.client else "unknown"
    identifier = f"{ip}:{email}"

    await _check_brute_force(db, identifier)

    user = await db.users.find_one({"email": email})
    if not user or not verify_password(payload.password, user["password_hash"]):
        await _register_failure(db, identifier)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    await _clear_failures(db, identifier)

    access = create_access_token(user["id"], user["email"])
    refresh = create_refresh_token(user["id"])
    set_auth_cookies(response, access, refresh)
    return _user_public(user)


@router.post("/logout")
async def logout(response: Response, user: dict = Depends(get_current_user)):
    clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserPublic)
async def me(user: dict = Depends(get_current_user)):
    return _user_public(user)


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    from server import db
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access = create_access_token(user_id, user["email"])
    refresh = create_refresh_token(user_id)
    set_auth_cookies(response, access, refresh)
    return {"message": "Refreshed"}


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    from server import db
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    # Always return success to prevent enumeration
    if user:
        token = secrets.token_urlsafe(32)
        await db.password_reset_tokens.insert_one({
            "token": token,
            "user_id": user["id"],
            "used": False,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "created_at": _now_iso(),
        })
        frontend = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        reset_link = f"{frontend}/reset-password?token={token}"
        logger.info(f"[PASSWORD RESET] link for {email}: {reset_link}")
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    from server import db
    record = await db.password_reset_tokens.find_one({"token": payload.token})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    if record.get("used"):
        raise HTTPException(status_code=400, detail="Token already used")
    if record["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")

    await db.users.update_one(
        {"id": record["user_id"]},
        {"$set": {"password_hash": hash_password(payload.new_password)}},
    )
    await db.password_reset_tokens.update_one(
        {"token": payload.token}, {"$set": {"used": True}}
    )
    return {"message": "Password has been reset successfully."}
