# PrepOS Adaptive Learning Engine
# Mission Engine

---

# Document Metadata

| Property | Value |
|----------|--------|
| Document | Mission Engine |
| Version | 1.0 |
| Status | Draft |
| Owner | Learning Engine |
| Category | Core Planning Engine |
| Depends On | 01 Vision, 02 Adaptive Brain, 03 Strategy Engine |
| Used By | AI Mentor, Dashboard, Coding Arena, Revision Engine |
| Last Updated | 2026-08-05 |

---

# Executive Summary

The Mission Engine is responsible for transforming a selected learning strategy into a concrete, executable daily learning mission.

It is the final planning stage before information reaches the learner.

Unlike the Adaptive Learning Brain, which decides *what should improve*, and the Strategy Engine, which decides *how the learner should prepare*, the Mission Engine decides *exactly what the learner will do today.*

Every topic, coding problem, revision item, study duration, and AI mentor instruction shown to the learner originates from this engine.

---

# Purpose

The Mission Engine exists to answer one question:

> "Given the selected learning strategy, what is the best possible study plan for today?"

Its objective is to maximize interview readiness while respecting learner context, available study time, company priorities, cognitive load, historical learning behavior, and long-term retention.

---

# Scope

The Mission Engine is responsible for:

- Generating daily missions
- Selecting learning topics
- Selecting coding problems
- Selecting revision topics
- Allocating study time
- Maintaining mission stability
- Preventing unnecessary repetition
- Balancing theory and practice
- Producing explainable missions

The Mission Engine is NOT responsible for:

- Strategy selection
- Company weighting
- Mastery calculation
- Memory persistence
- Knowledge graph construction
- Revision scheduling algorithm

Those responsibilities belong to dedicated engines.

---

# Core Responsibilities

The Mission Engine performs eight responsibilities.

1. Compose today's mission
2. Allocate study budget
3. Select primary learning
4. Select supporting learning
5. Select coding practice
6. Select revision
7. Generate explanations
8. Validate mission quality

---

# High-Level Architecture

```
Adaptive Learning Brain
            │
            ▼
Strategy Engine
            │
            ▼
==========================
      Mission Engine
==========================
            │
            ▼
+-------------------------------+
| Today's Personalized Mission  |
+-------------------------------+
| Primary Learning              |
| Supporting Topics             |
| Coding Practice               |
| Revision                      |
| AI Mentor Guidance            |
+-------------------------------+
```

---

# Inputs

The Mission Engine receives:

## Learner Profile

- Experience
- Daily study duration
- Preferred language
- Target companies

---

## Strategy Engine Output

- Selected strategy
- Mission proportions
- Difficulty target
- Study budget

---

## Knowledge Graph

- Topic hierarchy
- Module structure
- Topic dependencies
- Prerequisites

---

## Memory System

- Recent missions
- Completed topics
- Recently revised topics
- Recently solved coding problems

---

## Company Intelligence

- Topic priorities
- Company importance
- Interview frequency
- Technology focus

---

## Scoring Engine

- Mastery
- Confidence
- Weakness
- Readiness

---

# Outputs

The engine generates a Daily Mission.

Example:

```
Today's Mission

Primary

Trees

Supporting

Java Collections

Coding

2 Medium Tree Problems

Revision

Recursion

Estimated Duration

4 Hours

Mission Goal

Improve Tree mastery while reinforcing Collections and retaining Recursion fundamentals.
```

---

# Mission Composition Model

Every mission consists of four learning blocks.

```
Today's Mission

↓

Primary Learning

↓

Supporting Learning

↓

Coding Practice

↓

Revision
```

Each block serves a unique learning objective.

---

# Primary Learning

Purpose:

Advance the learner's current module.

Characteristics:

- Largest time allocation
- Deep conceptual learning
- Interview-focused
- Company-aware

Only one primary module should exist per mission.

---

# Supporting Learning

Purpose:

Strengthen complementary knowledge without disrupting focus.

Examples:

Primary:

Trees

Supporting:

Java Collections

Primary:

LLD

Supporting:

Design Patterns

Supporting topics should reinforce—not compete with—the primary objective.

---

# Coding Practice

Coding transforms theoretical understanding into problem-solving ability.

Coding should always relate to the learner's current preparation strategy.

Example:

Strategy:

Google Sprint

Coding:

Two Medium Tree Problems

Example:

Strategy:

Oracle Design Focus

Coding:

Implement Parking Lot Design

Coding distribution should follow:

70%

Current primary module

30%

Previously learned modules needing reinforcement

---

# Revision

Revision protects long-term retention.

Revision topics are selected based on:

- Forgetting risk
- Revision schedule
- Historical performance
- Bookmark status
- Weakness score

Revision is not simply a review—it is an active recall process.

---

# Time Budget Allocation

The Mission Engine allocates study time according to the selected strategy.

Example (4-hour study budget):

Primary Learning: 120 min

Supporting Learning: 45 min

Coding Practice: 60 min

Revision: 35 min

Buffer & Reflection: 20 min

Time allocation should adapt dynamically.

---

# Difficulty Calibration

Difficulty should evolve gradually.

Progression:

```
Easy

↓

Easy+

↓

Medium

↓

Medium+

↓

Hard

↓

Mixed Interview

↓

Mock Interview
```

Difficulty should never jump abruptly without evidence.

---

# Topic Selection Rules

The Mission Engine must evaluate:

- Module continuity
- Prerequisite completion
- Company priority
- Weakness score
- Mastery
- Confidence
- Time availability
- Historical repetition

Topic selection is evidence-driven.

---

# Anti-Repetition Rules

The planner should avoid unnecessary repetition.

Rules:

- Do not repeat yesterday's primary topic unless justified.
- Avoid identical coding problems.
- Rotate supporting topics.
- Revisit completed topics only when required for revision or reinforcement.

Mission diversity should improve engagement without sacrificing continuity.

---

# Mission Stability

Missions should evolve gradually.

The planner should avoid switching primary modules unless:

- Module completed
- Critical weakness detected
- Company priority changes
- Timeline changes
- Interview approaching

Consistency builds mastery.

---

# Explainability

Every mission should explain itself.

Example:

```
Today's Primary

Graphs

Reason

- Current DSA module
- Google interview target
- Graph mastery below expected
- Previous mission completed successfully
```

Every block of the mission should be traceable to measurable learner evidence.

---

# Mission Validation

Before delivery, the Mission Engine validates the mission.

Validation checklist:

✓ One primary module

✓ Supporting topics complement primary

✓ Coding aligns with strategy

✓ Revision selected

✓ Study duration respected

✓ No prerequisite violations

✓ Cognitive load acceptable

✓ Mission explainable

---

# Failure Handling

If no valid primary topic exists:

Select next prerequisite topic.

If coding history unavailable:

Assign introductory coding problems.

If learner study time is limited:

Prioritize primary learning and coding.

If company data unavailable:

Use default balanced roadmap.

---

# Constraints

The Mission Engine must never:

- Generate multiple unrelated primary modules.
- Ignore prerequisites.
- Exceed available study time.
- Ignore revision entirely.
- Repeat missions without justification.
- Recommend impossible workloads.

---

# Future Extensions

Future versions may support:

- Weekly mission planning
- Multi-day project missions
- AI-generated coding exercises
- Adaptive mission re-planning during the day
- Team learning missions
- Calendar integration
- Interview simulation weeks

---

# Acceptance Criteria

The Mission Engine is considered successful when:

- Every mission is personalized.
- Every mission is explainable.
- Mission duration matches learner availability.
- Coding aligns with learning objectives.
- Module continuity is preserved.
- Company priorities influence topic selection.
- Revision is included appropriately.
- Missions remain stable yet adaptive.

---

# Dependencies

Required Documents

- 01 Vision & Philosophy
- 02 Adaptive Learning Brain
- 03 Strategy Engine
- 05 Memory System
- 06 Knowledge Graph
- 07 Company Intelligence
- 08 Scoring Engine

---

# Revision History

| Version | Date | Author | Description |
|----------|------|---------|-------------|
| 1.0 | 2026-08-05 | PrepOS Architecture Team | Initial architecture specification for the Mission Engine. |