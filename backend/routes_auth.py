"""Auth routes: /api/auth/*"""
import os
import uuid
import secrets
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from fastapi.responses import RedirectResponse

from auth_utils import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, create_email_token, 
    decode_email_token, set_auth_cookies, clear_auth_cookies,
    get_current_user, get_jwt_secret, JWT_ALGORITHM,
)
from models import (
    RegisterRequest, LoginRequest,
    ForgotPasswordRequest, ResetPasswordRequest,ResendVerificationRequest,
    UserPublic, MessageResponse,
)
import jwt
from email_service import (
    send_verification_email,
    send_password_reset_email,
)

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


@router.post("/register", response_model=MessageResponse)
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
        # Email Verification
        "email_verified": False,
        "email_verified_at": None,
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
    
    # -------------------------------------------------------
    # Email Verification
    # -------------------------------------------------------

    verification_token = create_email_token(
        user_id=user_id,
        email=email,
        purpose="email_verification",
        expires_minutes=720,
    )

    backend = os.environ.get(
    "BACKEND_URL",
    "http://localhost:8000"
    )

    verification_link = (
        f"{backend}/api/auth/verify-email?token={verification_token}"
    )

    send_verification_email(
        to_email=email,
        name=user_doc["name"],
        verification_link=verification_link,
    )

    # access = create_access_token(user_id, email)
    # refresh = create_refresh_token(user_id)
    # set_auth_cookies(response, access, refresh)
    # return _user_public(user_doc)
    
    return {
    "message": "Registration successful. Please verify your email before signing in.",
    "email": email,
}


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
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    await _clear_failures(db, identifier)

    # -------------------------------------------------------
    # Email Verification Check
    # -------------------------------------------------------
    if not user.get("email_verified", False):
        raise HTTPException(
            status_code=403,
            detail=(
                "Your email address has not been verified yet. "
                "Please verify your email before signing in."
            )
        )

    access = create_access_token(
        user["id"],
        user["email"]
    )

    refresh = create_refresh_token(
        user["id"]
    )

    set_auth_cookies(
        response,
        access,
        refresh
    )

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
        frontend = os.environ.get(
        "FRONTEND_URL",
        "http://localhost:3000",
       )

        reset_link = (
            f"{frontend}/reset-password?token={token}"
        )

        send_password_reset_email(
            to_email=user["email"],
            name=user["name"],
            reset_link=reset_link,
        )
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/resend-verification")
async def resend_verification(payload: ResendVerificationRequest):
    from server import db

    email = payload.email.lower().strip()

    user = await db.users.find_one({"email": email})

    # Don't reveal whether the email exists
    if not user:
        return {
            "message": "If the account exists and isn't verified, a verification email has been sent."
        }

    # Already verified
    if user.get("email_verified", False):
        return {
            "message": "Email is already verified."
        }

    # Generate a fresh verification token
    verification_token = create_email_token(
        user_id=user["id"],
        email=user["email"],
        purpose="email_verification",
        expires_minutes=60,
    )

    backend = os.environ.get(
        "BACKEND_URL",
        "http://localhost:8000",
    )

    verification_link = (
        f"{backend}/api/auth/verify-email?token={verification_token}"
    )

    send_verification_email(
        to_email=user["email"],
        name=user["name"],
        verification_link=verification_link,
    )

    return {
        "message": "Verification email sent successfully."
    }


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    from server import db
    record = await db.password_reset_tokens.find_one({"token": payload.token})
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    if record.get("used"):
        raise HTTPException(status_code=400, detail="Token already used")
    expires_at = record["expires_at"]
    # Backward compatibility for old Mongo documents
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Token expired"
        )

    await db.users.update_one(
        {"id": record["user_id"]},
        {"$set": {"password_hash": hash_password(payload.new_password)}},
    )
    await db.password_reset_tokens.update_one(
        {"token": payload.token}, {"$set": {"used": True}}
    )
    return {"message": "Password has been reset successfully."}

@router.get("/verify-email")
async def verify_email(token: str):
    from server import db
    try:
        payload = decode_email_token(
            token,
            expected_purpose="email_verification"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Verification link has expired."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification link."
        )
    # Find the user
    user = await db.users.find_one(
        {"id": payload["sub"]}
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )
    
    if user["email"] != payload["email"]:
        raise HTTPException(
            status_code=400,
            detail="Token does not belong to this user."
        )
    if user.get("email_verified"):
        frontend = os.environ.get(
            "FRONTEND_URL",
            "http://localhost:3000"
        )

        return RedirectResponse(
            url=f"{frontend}/login?verified=true",
            status_code=302,
        )
        
    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {
                "email_verified": True,
                "email_verified_at": _now_iso(),
            }
        }
    )
    
    frontend = os.environ.get(
        "FRONTEND_URL",
        "http://localhost:3000"
    )
    return RedirectResponse(
        url=f"{frontend}/login?verified=true",
        status_code=302
    )
