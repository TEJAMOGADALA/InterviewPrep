# PrepOS Adaptive Learning Engine
# Adaptive Learning Brain

---

# Document Metadata

| Property | Value |
|----------|--------|
| Document | Adaptive Learning Brain |
| Version | 1.0 |
| Status | Draft |
| Owner | Learning Engine |
| Category | Core Architecture |
| Depends On | 01-vision-and-philosophy.md |
| Used By | Strategy Engine, Mission Engine, Revision Engine, Company Intelligence, AI Mentor |
| Last Updated | 2026-08-05 |

---

# Executive Summary

The Adaptive Learning Brain is the central decision-making component of PrepOS.

It acts as the "brain" of the platform by continuously collecting learner signals, evaluating current readiness, determining priorities, selecting an appropriate learning strategy, and producing high-level learning objectives for downstream engines.

The Adaptive Learning Brain never generates missions directly.

Instead, it determines **what should happen** while other engines determine **how it should happen**.

This separation ensures modularity, explainability, scalability, and future extensibility.

---

# Purpose

The purpose of the Adaptive Learning Brain is to convert learner data into strategic learning decisions.

It continuously answers questions such as:

- What should the learner focus on today?
- Which weakness has the highest interview impact?
- Is the learner progressing as expected?
- Has the learner forgotten previously mastered topics?
- Should the learner continue the current module or switch?
- Should coding or theory dominate today's mission?
- Is the current strategy still optimal?

---

# Scope

The Adaptive Learning Brain is responsible for:

- understanding learner state
- collecting learning signals
- selecting learning strategy
- estimating readiness
- prioritizing learning objectives
- coordinating downstream engines

It is **not responsible** for:

- generating missions
- selecting coding problems
- revision scheduling
- UI rendering
- storing learner data

Those responsibilities belong to specialized engines.

---

# High-Level Responsibilities

The Adaptive Learning Brain performs six primary responsibilities.

1. Observe
2. Understand
3. Prioritize
4. Strategize
5. Recommend
6. Explain

Every planning cycle follows this sequence.

---

# Position in System Architecture

```
                 Learner Activity
                        │
                        ▼
             User Signals & Analytics
                        │
                        ▼
          +---------------------------+
          | Adaptive Learning Brain   |
          +---------------------------+
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼
Strategy   Company AI   Memory
 Engine    Intelligence  System
      │
      ▼
 Mission Engine
      │
      ▼
 Daily Mission
```

The Adaptive Learning Brain coordinates the entire learning ecosystem.

---

# Core Design Philosophy

The Adaptive Learning Brain follows five architectural principles.

### 1. Evidence First

No recommendation should rely on assumptions.

Every decision must be supported by measurable learner signals.

---

### 2. Explainability

Every strategic decision must be explainable.

The system should always be capable of answering:

"Why was this chosen?"

---

### 3. Adaptation

Planning is dynamic.

The brain continuously updates its understanding as new learner evidence becomes available.

---

### 4. Separation of Concerns

The brain defines objectives.

Specialized engines perform execution.

---

### 5. Long-Term Optimization

The objective is not maximizing today's productivity.

The objective is maximizing interview readiness over the entire preparation journey.

---

# Inputs

The Adaptive Learning Brain consumes information from multiple subsystems.

## Learner Profile

- experience
- target companies
- preparation timeline
- preferred language
- daily study duration
- current role

---

## Learning Progress

- completed topics
- mastery
- confidence
- attempts
- completion history

---

## Coding Analytics

- solved problems
- difficulty distribution
- success rate
- recent performance
- contest participation

---

## Revision History

- revision frequency
- forgotten topics
- spaced repetition data
- overdue revisions

---

## Company Intelligence

- interview priorities
- company weightings
- topic importance
- curriculum coverage

---

## Memory System

- recent missions
- historical strengths
- persistent weaknesses
- learning velocity

---

## User Behaviour

- study consistency
- skipped topics
- abandoned sessions
- average completion time

---

# Outputs

The Adaptive Learning Brain produces strategic decisions.

Examples include:

- Today's learning objective
- Primary focus area
- Supporting topics
- Coding intensity
- Revision intensity
- Recommended strategy
- Difficulty calibration
- Learning priorities

These outputs become inputs for downstream engines.

---

# Internal Decision Pipeline

Every planning cycle follows the same pipeline.

```
Collect Signals

↓

Normalize Signals

↓

Evaluate Readiness

↓

Estimate Weaknesses

↓

Apply Company Intelligence

↓

Determine Strategy

↓

Generate Priorities

↓

Produce Planning Objectives

↓

Forward to Mission Engine
```

No stage should be skipped.

---

# Learner State Model

The brain continuously estimates learner state.

Example dimensions include:

- Conceptual understanding
- Coding ability
- Interview readiness
- Revision health
- Learning consistency
- Confidence
- Knowledge retention
- Time pressure

These dimensions collectively define the learner's current state.

---

# Strategic Decision Types

The Adaptive Learning Brain makes several categories of decisions.

## Learning Decisions

What concepts should be studied?

---

## Coding Decisions

Should coding dominate today?

---

## Revision Decisions

Should revision be prioritized?

---

## Company Decisions

Should company priorities override weak topics?

---

## Time Decisions

Should the planner optimize for speed or depth?

---

## Difficulty Decisions

Should difficulty increase, remain stable, or decrease?

---

# Signal Hierarchy

Not all learner signals have equal importance.

Signals are evaluated according to priority.

Example hierarchy:

1. Interview Target
2. Available Timeline
3. Company Intelligence
4. Learning Progress
5. Mastery
6. Coding Performance
7. Revision Health
8. Confidence
9. User Preferences

Lower-priority signals may influence planning but should not override higher-priority strategic objectives.

---

# Adaptive Behaviour

The brain should continuously adapt.

Examples include:

- increasing coding intensity after theory stagnation
- increasing revision after rapid forgetting
- postponing low-impact topics
- prioritizing company-critical concepts
- reducing cognitive overload
- revisiting weak prerequisites

The planner is expected to evolve as the learner evolves.

---

# Explainability Requirements

Every strategic decision should include an explanation.

Example:

Objective:
Improve graph algorithms.

Reason:

- Google prioritizes graph problems.
- Confidence is below target.
- Coding performance declined recently.
- Graph module is currently active.

Explainability is a first-class architectural requirement.

---

# Interfaces

The Adaptive Learning Brain communicates with:

## Receives From

- Knowledge Graph
- Memory System
- Company Intelligence
- Coding Arena
- Progress Tracker
- Revision Engine

---

## Sends To

- Strategy Engine
- Mission Engine
- AI Mentor
- Dashboard Analytics

---

# Constraints

The brain must never:

- ignore company priorities
- ignore learner timeline
- generate random recommendations
- repeat identical missions unnecessarily
- rely solely on confidence
- optimize a single metric at the expense of overall readiness

---

# Failure Scenarios

Examples include:

## Missing learner data

Fallback to default curriculum progression.

---

## Sparse coding history

Increase theory weighting until sufficient evidence exists.

---

## New learner

Use onboarding strategy.

---

## Inconsistent activity

Prioritize rebuilding learning momentum.

---

## Conflicting signals

Apply signal hierarchy defined in this document.

---

# Scalability Considerations

The architecture should support:

- additional interview companies
- additional subjects
- AI-generated learning resources
- new scoring metrics
- future ML ranking models
- reinforcement learning based planners

without redesigning the core brain.

---

# Future Extensions

Future versions may include:

- reinforcement learning planners
- predictive interview readiness
- personalized forgetting curves
- adaptive cognitive load estimation
- AI-generated learning strategies
- multi-agent planning

---

# Acceptance Criteria

The Adaptive Learning Brain is considered correct if:

- identical learner states produce identical strategic outputs
- recommendations remain explainable
- strategy changes only when learner evidence changes
- company priorities influence planning
- learner timeline affects strategy
- downstream engines receive sufficient planning objectives
- every decision can be traced back to supporting signals

---

# Dependencies

Required documents:

- 01-vision-and-philosophy.md
- 03-strategy-engine.md
- 05-memory-system.md
- 06-knowledge-graph.md
- 07-company-intelligence.md
- 08-scoring-engine.md

---

# Revision History

| Version | Date | Author | Description |
|----------|------|---------|-------------|
| 1.0 | 2026-08-05 | PrepOS Architecture Team | Initial architecture specification for the Adaptive Learning Brain. |