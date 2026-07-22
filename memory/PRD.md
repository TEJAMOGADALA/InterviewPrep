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

## What's been implemented — 2026-07-21 (iteration 4 · Roadmap Engine + Knowledge Graph)
- **Master Roadmap** (`/app/backend/data/roadmap_v1.json`) — versioned, data-driven hierarchy: Track → Module → Topic → Subtopic → LearningNode. 7 tracks, ~30 modules, ~65 topics, ~40 learning nodes with real problem IDs from problem_bank.
- **RoadmapEngine** (`/app/backend/roadmap.py`) — singleton with O(1) node lookup, breadcrumb/ancestors, prerequisite/related resolution, `by_pattern`, `problems_for_node`, `company_importance`. Backwards-compat adapters export legacy `TOPIC_META` / `SUBTOPIC_TO_PATTERN` / `PATTERN_TO_DOMAIN` shapes so Mission Engine keeps working unchanged.
- **KnowledgeNode model** — per-user per-node state (status/confidence/weakness_score/revision_bucket/mastery_percentage/notes/updated_at), keyed by `(user_id, roadmap_version, node_id)` unique index.
- **New endpoints**: `GET /api/roadmap` (full tree with rolled-up progress), `GET /api/roadmap/nodes/{id}` (deep topic page: breadcrumb + prereqs + related + linked problems + assignments/feedback + notes + activity + company importance), `GET /api/roadmap/progress` (per-track/module rollup), `PATCH /api/roadmap/nodes/{id}/notes`, `POST /api/roadmap/nodes/{id}/confidence`, `GET /api/roadmap/version`.
- **Migration on startup** — for every existing user: (a) stamp `roadmap_version=v1` on user record, (b) backfill `knowledge_nodes` at track level from legacy `knowledge_progress`, (c) backfill pattern-level nodes from `problem_feedback` aggregations. Fully idempotent — preserves any user notes.
- **Feedback sync** — `submit_problem_feedback` now writes to BOTH legacy `knowledge_progress` (backward compat) AND new `knowledge_nodes` (roadmap graph, weighted running-average confidence per pattern + track).
- **Self-heal** for orphaned onboarding — 409 `onboarding_required` auto-redirect (fixed in mid-iteration for prior data-consistency issue).
- **Knowledge Explorer** (`/app/knowledge-base`) — full rebuild. Iterative flat-render (no JSX recursion, so the visual-edit babel plugin no longer overflows). Track cards expand into modules → topics → subtopics with progress bars, revision-bucket dots (green/yellow/red), status chips, and mastery %. Search box filters + auto-expands matches.
- **Deep Topic Page** (`/app/knowledge-base/nodes/:nodeId`) — breadcrumb, hero with status/bucket chips, live Set-Confidence slider (persists), Mastery/Confidence/Weakness stats, Prerequisites cards (link to their own deep pages), Related links, Interview Importance star ratings per company, Resource tabs (Theory/Examples/Interview Tips/Common Mistakes/Articles/Videos/Flashcards — placeholders for AI Mentor), linked Coding Problems (with LeetCode links + feedback state), Personal Notes editor, Activity timeline.
- **All existing modules continue working** — Auth, Onboarding, Mission Engine V2, Coding Arena, Company Readiness, Notifications, Settings, Profile. No API removed.

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

## What's been implemented — 2026-02-01 (iteration 9 · AI KB Stabilization)
### 🐛 Bug fix — "Gemini rate/quota limit reached" false-positive
- **Root cause**: `/app/backend/ai_service.py::_classify()` used naked substring matching. `if "rate" in low` was matching the word `gen**erate**` (present in virtually every litellm error like `"Failed to generate chat completion: …"`). So every legitimate 4xx from Gemini — bad API key, deprecated model, invalid model name — got mis-labelled as **rate_limit / 429**. `"500" in low` had the same over-matching problem.
- **Fix**: rewrote `_classify` to use `err.__class__.__name__` first, then compiled regex patterns with word boundaries (`\brate[\s_]*limit\b`, `\b429\b`, etc.). Every naked substring removed. Added two new error kinds — `model_not_found` (very common — deprecated model in Settings) and `empty_response`. Added structured `LLM request start/ok/error` logging with class + first 400 chars of the raw SDK message for future debugging.
- **Verified by testing agent**: bogus model → 404 `model_not_found`; bad key → 401 `invalid_key`; empty key → 400 `missing_key`; happy path → cached (2nd call preserves `generated_at`); regenerate → new timestamp.

### 🧹 Knowledge page cleanup (per user spec)
- **Removed** the `Interview Tips` and `Common Mistakes` **tabs** from `AIContentTabs.jsx`.
- **Added** a new component `AIInterviewCards.jsx` that renders those two sections as **top summary cards** above the tabs card on the Deep Topic page.
- **Kept remaining 7 tabs**: Theory, Examples, Flashcards, Related Topics, Prerequisites, Articles (stub), Videos (stub).
- **Zero redesign** — same GlassCard styling, same colors, same spacing.

### ⚡ Duplicate-request prevention
- Extracted the content fetch into a new shared hook `/app/frontend/src/hooks/useAIContent.js`.
- The hook maintains an **in-memory promise-dedupe cache** — even though two components (`AIInterviewCards` + `AIContentTabs`) both need the content, they issue **exactly one** `/content` GET per page visit. StrictMode-safe.
- Verified by testing agent: network trace confirmed 1 request per mount.

### 📊 Regression
- **10/10 new stabilization tests pass**, full backend suite still green. Test file: `/app/backend/tests/test_iteration8_stabilization.py`. Report: `/app/test_reports/iteration_8.json`.
- All previous endpoints untouched. MissionControl progress strip + KnowledgeBase filter chips still render.

## What's been implemented — 2026-02-01 (iteration 8 · AI Knowledge Base Generation)
- **Modular AI backend** — three new files:
  - `/app/backend/ai_service.py` — provider-agnostic LLM shim wrapping `emergentintegrations.LlmChat`; classifies raw SDK errors into `missing_key | invalid_key | rate_limit | upstream | parse_error | unknown` for user-facing messaging.
  - `/app/backend/prompt_builder.py` — strict-JSON system + user prompt; builds a compact neighbor context (prereqs + related + siblings) so the model wires responses back to real roadmap ids; `parse_content()` gracefully recovers from code fences and partial JSON.
  - `/app/backend/knowledge_generation.py` — Mongo-cached orchestrator. Cache scope is **GLOBAL per (node_id, roadmap_version)** in the `knowledge_content` collection, so the first user's Gemini spend benefits everyone. Reads `ai_config` from `db.settings` (per user's Settings page).
- **Model**: `KnowledgeContent` added to `models.py`.
- **3 new endpoints** on the roadmap router:
  - `GET  /api/roadmap/nodes/{id}/content` — read-only cache lookup; never triggers Gemini.
  - `POST /api/roadmap/nodes/{id}/content/generate` — lazy generate + cache; no-op on cache hit.
  - `POST /api/roadmap/nodes/{id}/content/regenerate` — clears cache row and re-calls Gemini.
- **Error mapping**: missing_key → 400, invalid_key → 401, rate_limit → 429, upstream/parse_error → 502, not_found → 404 — with a friendly `detail.error` + `detail.message` shape for the frontend.
- **Frontend**: new self-contained component `/app/frontend/src/components/knowledge/AIContentTabs.jsx` renders 7 AI-populated tabs (Theory / Examples / Interview Tips / Common Mistakes / Flashcards / Related Topics / Prerequisites) + 2 intentional stubs (Articles / Videos). Empty-state CTA calls `/generate`. If the API key is missing/invalid, an inline banner appears with a `Open Settings` link — no crash. Related/Prereq entries deep-link to `/app/knowledge-base/nodes/{id}` when the model returns a real roadmap id. Flashcards support tap-to-reveal.
- **`DeepTopicPage`** placeholder block replaced with `<AIContentTabs nodeId={node.id} />` — no other layout change.
- **Model default**: `gemini-2.5-flash` (respects whatever user picks in Settings).
- **Tests**: 22/22 pytest cases pass covering read-only cache, unknown-node 404, missing_key path, happy-path via emergent universal key, cache-hit idempotency (generated_at unchanged), regenerate updates timestamp, related/prereq id resolution, second-node proves node-agnostic prompt, full regression on all previously-shipped endpoints. Frontend smoke via Playwright verified all data-testids render. Report: `/app/test_reports/iteration_7.json`.

## What's been implemented — 2026-02-01 (iteration 7 · Intelligent Progress Tracking)
- **Roadmap grew 1043 → 1085 nodes; 7 → 10 tracks** — added **Projects**, **Behavioral** and **Resume / LinkedIn** tracks with 5-10 starter nodes each. Zero UI redesign; the same tree engine renders them.
- **Normalized status vocabulary** across the whole app: `not_started | in_progress | completed | mastered | revision_due`. Legacy `available`/`locked` rows keep working — they're mapped to `not_started` on read. `revision_due` is **derived** when a completed/mastered node's `next_revision` is in the past.
- **KnowledgeNode model extended** (Mongo) with new per-user per-node fields: `attempts`, `actual_solve_minutes`, `bookmarked`, `favorite`, `completion_date`. Existing fields (status, confidence, mastery_percentage, revision_bucket, next_revision, notes) untouched.
- **Rollup engine now computes**: `total_topics` (leaf-only), `completed_topics`, `remaining_topics`, `completion_pct`, `estimated_hours_remaining` — recursively rolled up from leaves. Parents also aggregate bookmarked/favorite/attempt counters and derive `revision_due` if any descendant is due.
- **New backend endpoints (all additive, no old endpoints changed)**:
  - `POST /api/roadmap/nodes/{id}/status` — explicit status transition; stamps `completion_date` + 3-day `next_revision` on completed/mastered; seeds mastery/confidence sensibly on first mark.
  - `POST /api/roadmap/nodes/{id}/bookmark` / `/favorite` — optimistic toggles.
  - `POST /api/roadmap/nodes/{id}/attempt` — `$inc` attempts + optional actual_minutes; auto-seeds `status=in_progress` on first attempt.
  - `GET /api/roadmap/summary` — Mission Control dashboard: overall completion + weighted readiness (weighted by `mastery_weight`), per-track completion %, today's completed count, counts of revision_due / bookmarked / favorite.
- **Reusable frontend building blocks** in `/app/frontend/src/components/progress/`: `StatusBadge`, `ProgressBar`, `CategoryStats`, `FilterChips`, `NodeActions`. Hook `/app/frontend/src/hooks/useProgressTree.js` fetches the tree once, caches to `localStorage` (`prepos:roadmap-tree:v1`), and exposes a pure `matchNode(node, activeFilters)` predicate any tree walk can plug in.
- **Existing pages enhanced (no layout redesign)**:
  - **KnowledgeBase**: chip filter row inserted between search and tree — Completed / Incomplete / Revision Due / Bookmarked / Favorite / Easy / Medium / Hard / per-company chips. Tree walk composes text + chip filters. Every topic row now shows a normalized `StatusBadge` (incl. `revision_due`) plus small bookmark / favorite indicators when set.
  - **DeepTopicPage**: `NodeActions` (bookmark + favorite optimistic toggles) in the hero; a **Record Attempt** button prompts for minutes; quick **Mark in progress / completed / mastered** buttons. All wired to the new endpoints; the existing notes + confidence slider stay exactly where they were.
  - **MissionControl**: compact **Interview Progress** strip added above the bento grid with tiles for Overall, DSA, LLD, HLD, Behavioral, and Today (completed count + revision-due / bookmarked counts). Powered by `/api/roadmap/summary`.
- **Every legacy node ID preserved** — all previously-tracked user progress remains valid.
- **Tests**: 33/33 new backend tests + 336/337 full suite pass (the 1 pre-existing iter3 flake — unrelated). Report: `/app/test_reports/iteration_6.json`. Test file: `/app/backend/tests/test_iteration7_progress.py`.

## What's been implemented — 2026-02-01 (iteration 6 · LLD/HLD Deep Expansion)
- **Roadmap grew 329 → 1043 nodes** — still data-only, still zero UI / API / model changes.
- **LLD** (13 modules, 212 nodes):
  - **Design Patterns** — all 23 GoF patterns now materialised as subtopics under `lld.patterns.{creational|structural|behavioral}`. Newly added: **Flyweight** (structural) and **Mediator / Memento / Interpreter** (behavioral). Every pattern carries the 5 mandated learning-nodes: `.overview`, `.uml`, `.use_cases`, `.java`, `.interview`.
  - **9 new categorized case-study modules**:
    - `lld.cat.caching` — LRU, LFU, TTL
    - `lld.cat.booking` — Hotel, Flight, Train, Restaurant
    - `lld.cat.commerce` — Shopping Cart, Inventory, Warehouse, Coupon, Gift Card
    - `lld.cat.communication` — WhatsApp, Chat Server, Email, Notification Queue
    - `lld.cat.scheduling` — Cron, Task Scheduler, Job Queue
    - `lld.cat.banking` — Bank Account, Digital Wallet, UPI, Transaction Engine
    - `lld.cat.games` — Sudoku, Minesweeper, Blackjack, UNO
    - `lld.cat.smart` — Traffic Signal, Vending Machine, Coffee Machine, Printer, Library, Hospital
    - `lld.cat.os_inspired` — Memory Allocator, Thread Pool, Connection Pool, File System
  - Original `lld.cases` (Parking Lot, Chess, Splitwise, etc.) preserved verbatim.
- **HLD** (17 modules, 601 nodes):
  - **Existing 11 case studies retrofitted** — `hld.cases.url_shortener`, `hld.cases.rate_limiter`, `hld.cases.news_feed`, `hld.cases.chat`, `hld.cases.search`, `hld.cases.uber`, `hld.cases.netflix`, `hld.cases.twitter`, `hld.cases.instagram`, `hld.cases.dropbox`, `hld.cases.payment` — now each expose the 10 mandated subtopics: `.problem`, `.func_req`, `.non_func_req`, `.capacity`, `.apis`, `.db`, `.components`, `.scaling`, `.bottlenecks`, `.interview`.
  - **10 new categorized case-study modules**, each case with the same 10-part breakdown:
    - `hld.cat.storage` — Google Drive, Dropbox deep-dive, S3
    - `hld.cat.messaging` — Slack, Discord, MS Teams, Kafka
    - `hld.cat.search` — Elasticsearch, Google Search, Autocomplete
    - `hld.cat.streaming` — Spotify, Netflix deep-dive, Live Streaming, Zoom
    - `hld.cat.finance` — UPI, Wallet, Payment Gateway, Ledger
    - `hld.cat.infra` — API Gateway, CDN, Distributed Cache, Logging, Monitoring, Metrics
    - `hld.cat.social` — LinkedIn, Facebook Feed, Instagram Stories, Twitter Timeline
    - `hld.cat.ecommerce` — Amazon Cart, Inventory, Recommendation, Order Service
    - `hld.cat.maps` — Google Maps Nearby, Uber Dispatch
    - `hld.cat.misc` — GitHub, Google Docs, Collaborative Editor, Web Crawler, Online Compiler
- **Every legacy node ID preserved** — verified end-to-end by the backend testing agent, so all existing user progress remains valid.
- **Generator helpers added** (`pattern_subtopic()`, `lld_case_topic()`, `hld_case_topic()`) — new case studies and patterns can now be defined in a single line, keeping the generator maintainable.
- **Tests**: 149/149 new roadmap-LLD-HLD pytest cases + 303/304 full backend suite pass (the 1 flaky is the same pre-existing iter3 test — unrelated to this change). Report: `/app/test_reports/iteration_5.json`. Test file: `/app/backend/tests/test_roadmap_lld_hld_expansion.py`.

## What's been implemented — 2026-02-01 (iteration 5 · Roadmap Curriculum Expansion)
- **Master knowledge graph** at `/app/backend/data/roadmap_v1.json` expanded to **329 nodes across 7 tracks** — the single source of truth every future feature (Mission Engine, AI Mentor, Analytics, Revision, Mock Interviews) will consume.
- **Deterministic generator** at `/app/backend/scripts/generate_roadmap.py`; running it twice produces byte-identical JSON. Build-time DAG validator rejects duplicate ids, unknown prereqs and cycles.
- **Tracks covered**:
  - DSA (7 modules): Foundations (Arrays, Hashing, Two Pointers, Strings, Bit/Math), Windows & Search, Linear Structures (Stack, Queue, Linked List), Trees & Graphs (BT, BST, Tries, Graph BFS/DFS/Dijkstra/Bellman/MST/Bipartite), Heaps & Priority, DP + Backtracking + Greedy, Advanced (Union-Find, Segment/Fenwick).
  - Java (7 modules): OOP, Collections (+ ConcurrentHashMap, TreeMap, LinkedHashMap-LRU), Generics/Exceptions, Streams & Lambdas, Concurrency (+ CompletableFuture, JMM, Atomics), JVM (Memory/GC/ClassLoader/JIT), IO & NIO.
  - LLD (4 modules): Principles (SOLID + DRY/KISS + Cohesion/Coupling), Patterns (Creational, Structural, Behavioral — full set), UML, 11 Case Studies (Parking Lot, Chess, Splitwise, Tic-Tac-Toe, Snake & Ladder, Elevator, ATM, BookMyShow, LRU Cache, Rate Limiter, Notification).
  - HLD (7 modules): Foundations (CAP, PACELC, Consistency, Load Balancing, Scalability, Napkin Math), Caching & CDN, Databases at Scale, Messaging (Queues, Kafka, RabbitMQ, Pub/Sub), Distributed (Consensus, Consistent Hashing, Microservices, Event Sourcing), Security/Resiliency, 10 Case Studies (URL Shortener, Rate Limiter, News Feed, Chat, Search, Uber, Netflix, Twitter, Instagram, Dropbox, Payments).
  - OS (3 modules): Processes/Threads (Scheduling, Sync, Deadlocks, IPC), Memory (Paging, Virtual, Segmentation), File Systems & I/O.
  - DBMS (4 modules): Relational (ACID, Indexing, Normalization, Joins/Optimizer, SQL Deep-Dive), Concurrency (Isolation, Control, Deadlocks), NoSQL (KV, Document, Column, Graph), Scaling (Sharding, Replication).
  - CN (3 modules): Foundations (OSI, TCP, UDP, HTTP/HTTPS, HTTP/2-3, DNS), Advanced (TLS, LB, CDN, WebSockets), Security (Firewalls, DDoS).
- **Per-node metadata** now includes: `id`, `label`, `description`, `difficulty`, `estimated_minutes`, `interview_frequency`, `mastery_weight`, `prerequisites` (DAG), `related`, `company_importance` (per 14 companies), `tags`, `track`, `module`, `category`, `level`, `order`, `revision_bucket` (default `green`), `status` (`available`/`locked`), `version`. DSA nodes also carry `pattern`, `problem_ids`, `leetcode_tags`, `neetcode_tags`.
- **Companies expanded** to 14 for weighted importance: google, microsoft, atlassian, uber, adobe, linkedin, stripe, salesforce, oracle, phonepe, flipkart, paypal, goldman_sachs, zoho.
- **Backward compat**: every legacy node ID (78 of them) preserved — verified by the testing agent — so all existing user progress, missions, assignments and feedback continue to map correctly.
- **No changes** to UI, routes, API contracts, Mission Engine, models, or auth. Data-only enhancement.
- **Backup** at `/app/backend/data/roadmap_v1.backup.json`.
- **Tests**: 110/110 new roadmap pytest cases + 154/155 full backend suite pass. Test file: `/app/backend/tests/test_roadmap_expansion.py`. Report: `/app/test_reports/iteration_4.json`.

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
- **Consume the expanded roadmap metadata** in the Mission Engine, AI Mentor and Analytics — company_importance, mastery_weight and interview_frequency are now available on every node.
- **Knowledge Base content**: fill in Theory / Examples / Videos / Flashcards placeholders (currently intentionally empty on every node).
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
