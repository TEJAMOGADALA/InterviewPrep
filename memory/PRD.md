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

## What's been implemented — 2026-07-21
- **Backend:** All auth flows, session persistence via httpOnly cookies, refresh, brute-force protection, admin seeding, indexes (users.email unique, TTL on password_reset_tokens, unique settings.user_id + onboarding.user_id).
- **Onboarding persistence:** POST /api/onboarding stores full record and flips `user.onboarding_completed=true`; estimation logic derives `estimated_prep_days`.
- **Frontend:** All routes, gated by ProtectedRoute (auth) and PublicOnlyRoute. All pages ship with proper loading + empty + error states. All interactive elements have `data-testid` attrs.
- **Design:** Custom fonts loaded (Outfit / Manrope / JetBrains Mono). Global grid-noise + ambient blur. Dark glassmorphism cards. Cool indigo accent.
- **Testing:** 15/15 backend pytest passing; frontend flows validated (register→onboarding→dashboard, all 9 nav routes, Cmd+K, AI panel, Settings tabs, Profile, logout).

## Auth credentials
- Admin: `admin@prepos.io / Admin@123`
- See `/app/memory/test_credentials.md`.

## Prioritized backlog

### P0 — Next drop (Phase 2)
- Wire real AI Mentor to Gemini (using per-user API key from Settings).
- Mission Engine v1: generate daily missions from onboarding baseline.
- Global Search backend index (topics / missions / notes).

### P1
- Knowledge Base content model + editor.
- Coding Arena problem model + submission runner.
- Spaced-repetition scheduler for "Upcoming Revision" widget.
- Analytics events pipeline (topic velocity, focus quality).

### P2
- LLD / HLD case-study library + interactive canvas.
- Mock interview flow (voice / text).
- Weekly report email.
- Contest tracker integration.
- Real notifications feed + push (browser).
- Theme = system / light polish.
- Convert frontend to Vite+TypeScript if user still wants it (folder structure is ready).

## Testing
- Backend: `pytest /app/backend/tests/backend_test.py -v`
- Frontend: manual via preview URL. Full flow: `/register` → wizard → `/app/mission-control`.
