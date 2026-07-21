# PrepOS – AI Interview Operating System

## Original Problem Statement
Build the production-ready foundation for an AI-powered Interview Operating System called PrepOS. Multi-user premium dark SaaS (Linear/Vercel/Cursor inspired) for Product-Based Company interview prep. Foundation only — no AI logic, no curriculum, no analytics engine yet.

## Stack (as delivered)
- **Frontend:** React (CRA) + JavaScript (JSX) + TailwindCSS + shadcn/ui + Framer Motion + TanStack Query + React Router 7. *(User requested Vite+TS; delivered with CRA+JSX because our supervisor is CRA-bound. Modular folder structure is Vite/TS-ready and easy to migrate later.)*
- **Backend:** FastAPI + Motor (MongoDB) + PyJWT + bcrypt.
- **Auth:** JWT access + refresh, httpOnly cookies (SameSite=None+Secure for HTTPS preview). Custom email/password.
- **Design:** Cool Indigo `#6366F1` primary on Near-Black `#0B0F19` with dark glassmorphism cards. Outfit / Manrope / JetBrains Mono typography.

## Architecture
```
/app/backend
  server.py            entrypoint, startup indexes + admin seed
  auth_utils.py        bcrypt + JWT + cookies + get_current_user dep
  routes_auth.py       /api/auth/{register, login, logout, me, refresh, forgot-password, reset-password}
  routes_user.py       /api/{profile, settings, onboarding}
  models.py            Pydantic models
/app/frontend/src
  App.js               router + providers
  contexts/            Auth, AIPanel, CommandPalette
  services/            api (axios), auth.service
  components/
    layout/            AppShell, Sidebar, MobileNav, Topbar, AIAssistantPanel, CommandPalette, AuthLayout
    common/            Logo, GlassCard, EmptyState, LoadingScreen, PlaceholderPage
    ui/                shadcn primitives
    ProtectedRoute    Protected + PublicOnly routes
  pages/
    auth/              Login, Register, ForgotPassword, ResetPassword
    onboarding/        MissionInit (7 steps)
    dashboard/         MissionControl
    coding, system-design, knowledge, ai-mentor, analytics, notifications, settings, profile
  config/              navigation, companies, featureFlags
  constants/testIds/   testId registry (auth, home, prepos)
  utils/               formatApiError
```

## Personas
- **Aspirant (Student → 5+ yrs)** preparing for FAANG / Product-Based companies. Wants a calm, focused workspace that adapts to their skill baseline and target date.
- **Senior IC returning to interviewing**. Wants a command-center feel, minimal fluff, keyboard-first.
- **Admin** (future) for content curation.

## Core Requirements (static)
- Multi-user, dark-first, mobile-responsive.
- Register / Login / Forgot / Reset password.
- 7-step Mission Initialization onboarding, data persisted per user.
- Mission Control dashboard with 7 placeholder widgets.
- Sidebar (9 nav items) + Topbar (global search + Cmd+K + notifications + user menu).
- Docked AI Assistant panel (UI only) present on every /app page.
- Cmd+K Command Palette.
- Settings (6 tabs) incl. AI Configuration (Provider / Gemini Key / Model / Temperature).
- Profile page with target companies, target date, skill baseline.
- Feature flag architecture, scalable, no business logic yet.

## What's been implemented — 2026-07-21 (iteration 3 · Adaptive Engine + Coding Arena)
- **Curated Problem Bank** (`/app/backend/problem_bank.py`) — 87 problems across 16 patterns with real LeetCode URLs. PATTERN_TO_DOMAIN + PATTERN_PREREQUISITES root-cause map.
- **Mission Engine V2** (adaptive) — analyses last 36h of feedback (confidence, hints, time, could_not_solve) and picks mode:
  - `revise` → force weakest pattern focus + insert prerequisite revisions (e.g. Heap failure → auto-insert Comparator & Comparable revision).
  - `advance` → progress to harder DSA patterns at hard difficulty.
  - `continue` → standard baseline progression. Extra practice yesterday nudges hours up.
- **DSA practice tasks are backed by real problem assignments** on mission generation. Non-DSA missions unchanged.
- **Task toggle** — clicking a task toggles both directions; completed = green background + green check + NO strike-through. Un-toggling reverts mission status if it was completed. Backwards-compat `/complete` endpoint delegates to `/toggle`.
- **Coding Arena** — full page rebuild wired to `/api/coding-arena`: today's pattern header, mission recap, problem cards (title/difficulty/pattern/time/LeetCode link/feedback state), `+ Practice More` button pulls next unseen problem, feedback modal (difficulty/solved-status/confidence/time/notes) → persists ProblemFeedback + knowledge gain + confidence-adjusted revision + WeaknessRecord on low signals.
- **Spaced repetition V2** — 1d/3d/7d/14d/30d/60d ladder × confidence modifier (0.4× for conf≤3, 1.5× for conf≥9).
- **Knowledge Progress drill-down** — dashboard rows expand to reveal per-subtopic progress, problems solved, avg confidence, revision status (fresh/due/mastered). DSA drills into all 16 patterns.
- **Company Readiness** — 12 companies with per-company weighted formulas (Google=DSA-heavy, Oracle=DBMS+Java, Stripe=HLD+Backend, etc.). Dashboard widget shows target companies first.
- **Recent Activity** capped at 5 items on dashboard; full history at `/app/notifications`.
- **New DB collections + indexes**: problem_assignments (by user+mission, user+pattern), problem_feedback (by user+time), mission_adjustments (by user+date), weaknesses (by user+pattern).
- **Testing**: 15/15 iteration-3 pytest passing + 15/15 iter2 + 15/15 iter1. Frontend Playwright validated task-toggle style, Company Readiness, drill-down, Coding Arena feedback dialog, Practice More, LeetCode links.

## What's been implemented — 2026-07-21 (iteration 2 · Mission Engine V1)
- **Mission Engine V1** — deterministic daily mission per (user, date) driven by onboarding (target companies weighted, position, hours, self_assessment, target date). Focus-topic chosen by urgency + company bias. 2–4 tasks (practice / study / revise), plus up to 2 due revision items appended.
- **Backend endpoints**: `GET /api/missions/today`, `POST /api/missions/{id}/tasks/{task_id}/complete`, `POST /api/missions/{id}/complete`, `POST /api/missions/{id}/skip`, `GET /api/missions/history`, `GET /api/revisions/queue`, `GET /api/activity`, `GET /api/dashboard` (aggregated), `PATCH /api/onboarding` (recalcs prep days + regenerates today's mission).
- **Live dashboard**: Mission Control now shows real mission, real streak (7-day grid), computed Interview Readiness (35/15/15/15/6.67/6.67/6.66 weighting), real Knowledge Progress (baseline-seeded, gains per task), real Upcoming Revision queue, real Activity timeline, real notifications preview.
- **Spaced repetition**: 1d → 3d → 7d → 14d → 30d ladder on completion of practice/study tasks; revise tasks advance the ladder.
- **Streak**: idempotent per day, longest tracked, resets on non-consecutive completions.
- **Activity logging**: mission_generated, mission_completed, mission_skipped, task_completed, profile_updated, settings_changed, daily_login (once/day).
- **Profile edit**: users can edit target companies, position, daily study hours, and target date from Profile page → triggers `PATCH /api/onboarding` → today's mission regenerates.
- **Notifications page**: now consumes real activity feed from backend (no mock data).
- **DB models**: DailyMission (+ MissionTask embedded), KnowledgeProgress, StudyStreak, RevisionItem, ActivityEvent, OnboardingPatch.
- **Indexes added**: daily_missions unique(user_id, date), knowledge_progress unique(user_id, topic), study_streaks unique(user_id), revisions(user_id, next_review_date), activity_events(user_id, ts).
- **Tests**: 15/15 mission engine pytest passing + prior 15/15 auth pytest. Frontend flows validated end-to-end (fresh signup → onboarding → dashboard → task complete → mission complete → streak up → revision scheduled → readiness updated → profile edit → mission regenerated).

## What's been implemented — 2026-07-21 (iteration 1 · Foundation)
- **Backend:** All auth flows, session persistence via httpOnly cookies, refresh, brute-force protection, admin seeding, indexes (users.email unique, TTL on password_reset_tokens, unique settings.user_id + onboarding.user_id).
- **Onboarding persistence:** POST /api/onboarding stores full record and flips `user.onboarding_completed=true`; estimation logic derives `estimated_prep_days`.
- **Frontend:** All routes, gated by ProtectedRoute (auth) and PublicOnlyRoute. All pages ship with proper loading + empty + error states. All interactive elements have `data-testid` attrs.
- **Design:** Custom fonts loaded (Outfit / Manrope / JetBrains Mono). Global grid-noise + ambient blur. Dark glassmorphism cards. Cool indigo accent.
- **Testing:** 15/15 backend pytest passing; frontend flows validated (register→onboarding→dashboard, all 9 nav routes, Cmd+K, AI panel, Settings tabs, Profile, logout).

## Auth credentials
- Admin: `admin@prepos.io / Admin@123`
- See `/app/memory/test_credentials.md`.

## Prioritized backlog

### P0 — Next drop (Phase 4)
- **Wire real AI Mentor to Gemini** (using per-user API key from Settings) — AI now has rich adaptive data (feedback, weaknesses, confidence) to consult.
- **Knowledge Base**: content model so Study tasks deep-link into real concept pages (per-subtopic).
- **LLD/HLD case-study library** + interactive canvas.
- **Analytics engine**: topic velocity, focus quality, retention curves powered by ProblemFeedback + ActivityEvent.

### P1
- Mock interview flow (voice / text) using feedback signals.
- Weekly report email combining streak, readiness delta, top weak patterns.
- Cross-user leaderboards on target companies (opt-in social layer).
- Contest tracker integration.

### P2
- Real push notifications.
- Light theme polish.
- Convert frontend to Vite + TypeScript (folder structure ready).
- Upsert semantics for problem feedback (currently keeps append history — good for audit but noisy).
- Cascade cleanup of orphaned problem_assignments on mission delete.
- Decrement knowledge on task un-toggle (currently keeps gain — audit-friendly, but may overstate progress).

## Testing
- Backend: `pytest /app/backend/tests/backend_test.py -v`
- Frontend: manual via preview URL. Full flow: `/register` → wizard → `/app/mission-control`.
