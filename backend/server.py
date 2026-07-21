"""PrepOS FastAPI backend entrypoint."""
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

import os
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from auth_utils import hash_password, verify_password
from routes_auth import router as auth_router
from routes_user import router as user_router
from routes_missions import router as missions_router

# ------------------------- DB -------------------------
mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

# ------------------------- App -------------------------
app = FastAPI(title="PrepOS API", version="0.1.0")

# CORS — must allow credentials for cookie-based auth. Cannot use wildcard with credentials.
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
cors_env = os.environ.get("CORS_ORIGINS", frontend_url)
if cors_env == "*":
    origins = [frontend_url]
else:
    origins = [o.strip() for o in cors_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------- Health -------------------------
api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "PrepOS API", "version": "0.1.0"}


@api_router.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


app.include_router(api_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(missions_router)

# ------------------------- Startup -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("prepos")


@app.on_event("startup")
async def on_startup():
    # Indexes
    await db.users.create_index("email", unique=True)
    await db.settings.create_index("user_id", unique=True)
    await db.onboarding.create_index("user_id", unique=True)
    await db.login_attempts.create_index("identifier")
    await db.password_reset_tokens.create_index(
        "expires_at", expireAfterSeconds=0
    )
    # Mission engine indexes
    await db.daily_missions.create_index([("user_id", 1), ("date", -1)])
    await db.daily_missions.create_index([("user_id", 1), ("date", 1)], unique=True)
    await db.knowledge_progress.create_index([("user_id", 1), ("topic", 1)], unique=True)
    await db.study_streaks.create_index("user_id", unique=True)
    await db.revisions.create_index([("user_id", 1), ("next_review_date", 1)])
    await db.activity_events.create_index([("user_id", 1), ("ts", -1)])
    # V2 adaptive engine indexes
    await db.problem_assignments.create_index([("user_id", 1), ("mission_id", 1)])
    await db.problem_assignments.create_index([("user_id", 1), ("pattern", 1)])
    await db.problem_feedback.create_index([("user_id", 1), ("submitted_at", -1)])
    await db.problem_feedback.create_index([("user_id", 1), ("pattern", 1)])
    await db.mission_adjustments.create_index([("user_id", 1), ("for_date", -1)])
    await db.weaknesses.create_index([("user_id", 1), ("pattern", 1)])
    logger.info("MongoDB indexes ensured.")

    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@prepos.io")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        import uuid
        admin_id = str(uuid.uuid4())
        await db.users.insert_one({
            "id": admin_id,
            "email": admin_email,
            "name": "PrepOS Admin",
            "password_hash": hash_password(admin_password),
            "role": "admin",
            "avatar_url": None,
            "onboarding_completed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info(f"Seeded admin user: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": hash_password(admin_password)}},
        )
        logger.info(f"Updated admin password hash for {admin_email}")


@app.on_event("shutdown")
async def on_shutdown():
    client.close()
