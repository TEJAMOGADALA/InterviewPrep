# PrepOS Adaptive Learning Engine
# Memory System

---

# Document Metadata

| Property | Value |
|----------|--------|
| Document | Memory System |
| Version | 1.0 |
| Status | Draft |
| Owner | Learning Engine |
| Category | Core Intelligence |
| Depends On | 01 Vision & Philosophy, 02 Adaptive Learning Brain |
| Used By | Strategy Engine, Mission Engine, Revision Engine, AI Mentor, Dashboard Analytics |
| Last Updated | 2026-08-05 |

---

# Executive Summary

The Memory System is responsible for preserving the learner's historical learning journey.

Unlike conventional learning platforms that primarily record topic completion percentages, PrepOS continuously accumulates evidence about how the learner studies, remembers, applies, and forgets knowledge.

This memory allows PrepOS to behave like an experienced mentor who remembers every important interaction with the learner.

Rather than treating each day's mission independently, the planner continuously references historical evidence to improve future decisions.

---

# Purpose

The Memory System exists to answer questions that cannot be answered using only the learner's current progress.

Examples include:

- What has the learner been studying recently?
- Which concepts are repeatedly forgotten?
- Which modules were abandoned?
- Which coding topics consistently cause difficulty?
- Is the learner improving?
- Is motivation decreasing?
- Is revision effective?
- Should today's mission continue yesterday's work?

Without memory, true personalization is impossible.

---

# Scope

The Memory System is responsible for:

- Recording learning history
- Tracking mission history
- Tracking coding history
- Tracking revision history
- Measuring learning velocity
- Detecting momentum
- Detecting stagnation
- Measuring forgetting
- Supporting adaptive planning

The Memory System is NOT responsible for:

- Mission generation
- Topic ranking
- Company weighting
- Knowledge graph traversal
- Difficulty calculation

---

# Design Philosophy

The Memory System is built upon four principles.

## 1. Learning is Continuous

Learning should never be viewed as isolated daily sessions.

Every study activity contributes to a continuous preparation journey.

---

## 2. Evidence Accumulates

A learner should never need to repeatedly prove the same knowledge.

Every successful interaction strengthens the learner's evidence profile.

---

## 3. Knowledge Decays

Memory naturally weakens over time.

The planner should anticipate forgetting rather than react to it.

---

## 4. History Improves Decisions

Historical learner behaviour is often more valuable than onboarding information.

As evidence grows, historical performance should gradually outweigh initial self-assessment.

---

# Position in Architecture

```
Learner Activity
        │
        ▼
Memory System
        │
        ▼
Adaptive Learning Brain
        │
        ▼
Strategy Engine
        │
        ▼
Mission Engine
```

The Memory System continuously enriches every planning cycle.

---

# Memory Layers

PrepOS maintains three complementary memory horizons.

---

# Short-Term Memory

Purpose

Maintain immediate learning continuity.

Typical duration

5–10 recent missions.

Contains

- Recent primary topics
- Recent coding problems
- Recent revisions
- Recent AI conversations
- Recent bookmarks
- Recent confidence updates

Typical use cases

- Prevent repetition
- Maintain module continuity
- Continue unfinished learning
- Detect immediate struggles

---

# Medium-Term Memory

Purpose

Capture learning trends.

Typical duration

2–8 weeks.

Contains

- Module completion trends
- Confidence evolution
- Coding improvement
- Revision effectiveness
- Learning consistency
- Study habits

Typical use cases

- Detect stagnation
- Detect improvement
- Adapt learning strategy
- Adjust difficulty

---

# Long-Term Memory

Purpose

Represent the learner's permanent knowledge profile.

Contains

- Mastered modules
- Historical strengths
- Historical weaknesses
- Career preparation history
- Overall interview readiness
- Company readiness

Long-Term Memory changes slowly and represents accumulated evidence.

---

# Memory Components

The Memory System maintains several evidence categories.

## Learning Memory

Stores

- Completed topics
- Time spent
- Completion quality
- Learning frequency

---

## Coding Memory

Stores

- Solved problems
- Difficulty
- Success rate
- Languages
- Categories
- Attempts

---

## Revision Memory

Stores

- Revision count
- Revision intervals
- Retention success
- Forgotten concepts

---

## Confidence Memory

Stores

Learner confidence after every interaction.

Confidence changes over time.

High confidence without evidence gradually decreases.

---

## Behaviour Memory

Stores

- Skipped missions
- Partial completions
- Consistency
- Study streaks
- Preferred study patterns

---

# Memory Pipeline

Every learner interaction follows the same pipeline.

```
Learner Action

↓

Evidence Collection

↓

Memory Update

↓

Trend Analysis

↓

Retention Update

↓

Signal Generation

↓

Adaptive Planning
```

Memory is updated continuously.

---

# Learning Velocity

The Memory System continuously estimates learning velocity.

Velocity measures how efficiently the learner is progressing.

Factors include

- Topics completed
- Coding success
- Revision quality
- Consistency
- Confidence growth

Learning velocity influences future mission difficulty.

---

# Momentum Detection

Momentum measures sustained learning progress.

Positive indicators

- Daily consistency
- Increasing mastery
- Coding improvement
- Revision success

Negative indicators

- Missed sessions
- Repeated failures
- Declining confidence
- Frequent skips

Momentum influences:

- difficulty
- mission intensity
- revision frequency

---

# Stagnation Detection

The planner should detect stagnation.

Examples

- Same mastery for weeks
- Repeated failures
- No coding improvement
- Repeated revision failures

Detected stagnation should trigger strategy changes.

---

# Forgetting Model

Knowledge naturally decays.

The Memory System continuously estimates forgetting probability.

Signals

- Time since last revision
- Previous confidence
- Coding inactivity
- Historical retention

Higher forgetting probability increases revision priority.

---

# Reinforcement Model

Repeated successful retrieval strengthens memory.

Successful reinforcement occurs through:

- Revision
- Coding
- AI questioning
- Interview simulations

Repeated reinforcement gradually increases long-term mastery.

---

# Memory Decay

Not all evidence remains equally important forever.

Recent evidence carries greater influence than very old evidence.

Examples

Yesterday's coding session influences today's mission more than coding completed six months ago.

However, long-term mastery remains part of the learner profile.

---

# Evidence Reliability

Different evidence types have different reliability.

Example hierarchy

1. Coding Performance
2. Successful Revision
3. Topic Completion
4. AI Mentor Assessment
5. Learner Confidence
6. Initial Self Assessment

As preparation progresses, objective evidence increasingly outweighs subjective inputs.

---

# Memory Retrieval

Every planning cycle retrieves memory in three stages.

```
Recent Memory

↓

Relevant Memory

↓

Historical Memory
```

Only memory relevant to the current planning context should influence decisions.

---

# Memory Pruning

The system should never grow indefinitely.

Low-value transient events may be archived while preserving high-value evidence.

Examples

Archive

- temporary UI interactions
- abandoned searches

Preserve

- coding history
- mastery evolution
- revision outcomes
- interview simulations

---

# Memory Interfaces

The Memory System provides:

- Recent mission history
- Learning trends
- Momentum score
- Forgetting probability
- Historical mastery
- Behavioural insights
- Revision history

These become planning signals for downstream engines.

---

# Explainability

Memory should always be explainable.

Example

Today's revision includes Hash Maps because:

- Last revised 18 days ago
- Confidence decreased
- Two coding mistakes involved Hash Maps
- Retention probability below threshold

Every memory-driven recommendation must provide supporting evidence.

---

# Constraints

The Memory System must never:

- Forget permanent mastery without evidence
- Repeat identical missions unnecessarily
- Ignore learner improvement
- Ignore behavioural history
- Treat all historical evidence equally

---

# Failure Handling

If memory is unavailable

Fallback

Use onboarding profile and curriculum defaults.

If learner is new

Initialize memory from onboarding.

If historical evidence is sparse

Increase reliance on current performance.

---

# Future Extensions

Future versions may include

- Reinforcement learning memory
- Semantic memory graphs
- AI-generated learning summaries
- Personalized forgetting curves
- Cognitive load estimation
- Cross-device memory synchronization
- Interview performance memory

---

# Acceptance Criteria

The Memory System is considered successful when:

- It remembers recent learning context.
- It detects learning momentum.
- It identifies stagnation.
- It estimates forgetting.
- It improves adaptive planning.
- Historical evidence gradually outweighs onboarding assumptions.
- Memory-driven decisions remain explainable.

---

# Dependencies

Required Documents

- 01 Vision & Philosophy
- 02 Adaptive Learning Brain
- 03 Strategy Engine
- 04 Mission Engine
- 06 Knowledge Graph
- 08 Scoring Engine

---

# Revision History

| Version | Date | Author | Description |
|----------|------|---------|-------------|
| 1.0 | 2026-08-05 | PrepOS Architecture Team | Initial architecture specification for the Memory System. |