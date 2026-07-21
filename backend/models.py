"""Pydantic models for PrepOS."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ============ Auth ============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=80)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: EmailStr
    name: str
    role: str = "user"
    avatar_url: Optional[str] = None
    onboarding_completed: bool = False
    created_at: str


# ============ Profile ============

class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=80)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=280)
    headline: Optional[str] = Field(default=None, max_length=120)


# ============ Onboarding ============

class OnboardingSelfAssessment(BaseModel):
    dsa: int = Field(ge=1, le=10, default=5)
    java: int = Field(ge=1, le=10, default=5)
    lld: int = Field(ge=1, le=10, default=5)
    hld: int = Field(ge=1, le=10, default=5)
    operating_systems: int = Field(ge=1, le=10, default=5)
    dbms: int = Field(ge=1, le=10, default=5)
    computer_networks: int = Field(ge=1, le=10, default=5)


class OnboardingPayload(BaseModel):
    target_companies: List[str] = Field(min_length=1, max_length=20)
    current_position: str  # Student | 0-1 | 1-3 | 3-5 | 5+
    daily_study_hours: float = Field(ge=1, le=8)
    self_assessment: OnboardingSelfAssessment
    interview_target_date: str  # ISO date string


class OnboardingRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    target_companies: List[str]
    current_position: str
    daily_study_hours: float
    self_assessment: OnboardingSelfAssessment
    interview_target_date: str
    estimated_prep_days: int
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


# ============ Settings ============

class AIConfig(BaseModel):
    provider: str = "gemini"  # gemini | openai | claude | deepseek
    model_name: str = "gemini-2.5-flash"
    api_key: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0, le=2)


class NotificationPrefs(BaseModel):
    email_daily_digest: bool = True
    email_weekly_report: bool = True
    push_streak_reminders: bool = True
    push_upcoming_revisions: bool = True
    push_mission_updates: bool = True


class UserSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    theme: str = "dark"  # dark | light | system
    ai_config: AIConfig = Field(default_factory=AIConfig)
    notification_prefs: NotificationPrefs = Field(default_factory=NotificationPrefs)
    updated_at: str = Field(default_factory=_now_iso)


class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    ai_config: Optional[AIConfig] = None
    notification_prefs: Optional[NotificationPrefs] = None


# ============ Missions ============

TOPIC_KEYS = ["dsa", "java", "lld", "hld", "operating_systems", "dbms", "computer_networks"]


class MissionTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    kind: str  # 'practice' | 'study' | 'revise'
    topic: str  # one of TOPIC_KEYS
    completed: bool = False
    completed_at: Optional[str] = None


class DailyMission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    date: str  # YYYY-MM-DD (user local date, but stored as UTC date)
    title: str
    focus_area: str
    focus_topic: str  # one of TOPIC_KEYS
    difficulty: str  # easy | medium | hard
    estimated_duration_minutes: int
    learning_objective: str
    tasks: List[MissionTask]
    revision_task_ids: List[str] = []  # ids of tasks that are revision items
    status: str = "in_progress"  # in_progress | completed | skipped
    created_at: str = Field(default_factory=_now_iso)
    completed_at: Optional[str] = None
    skipped_at: Optional[str] = None


class KnowledgeProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    topic: str  # one of TOPIC_KEYS
    score: float = 0.0  # 0-100
    completions: int = 0
    last_updated: str = Field(default_factory=_now_iso)


class StudyStreak(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    current_streak: int = 0
    longest_streak: int = 0
    last_active_date: Optional[str] = None  # YYYY-MM-DD
    updated_at: str = Field(default_factory=_now_iso)


class RevisionItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    task_title: str
    topic: str
    stage: int = 0  # 0..4 (1d, 3d, 7d, 14d, 30d)
    next_review_date: str  # YYYY-MM-DD
    created_at: str = Field(default_factory=_now_iso)
    completed: bool = False


class ActivityEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    kind: str  # mission_completed | mission_skipped | task_completed | profile_updated | settings_changed | daily_login | mission_generated
    title: str
    description: Optional[str] = None
    ts: str = Field(default_factory=_now_iso)


class OnboardingPatch(BaseModel):
    target_companies: Optional[List[str]] = None
    current_position: Optional[str] = None
    daily_study_hours: Optional[float] = Field(default=None, ge=1, le=8)
    interview_target_date: Optional[str] = None
