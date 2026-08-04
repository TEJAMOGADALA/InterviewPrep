# PrepOS Subject Template

**File:** `docs/curriculum/governance/00-subject-template.md`

Version: 1.0

Status: Canonical

Owner: PrepOS Architecture Team

---

# Purpose

This document defines the canonical authoring template for every subject in the PrepOS Curriculum.

Every curriculum document MUST follow this structure.

This ensures:

- Consistency across all subjects
- Predictable parsing
- Stable JSON generation
- Uniform Adaptive Learning behavior
- Maintainable curriculum evolution
- Single Source of Truth

No subject may introduce its own document structure unless this specification is updated.

---

# Subject Lifecycle

Every subject follows the same lifecycle.

```
Subject

↓

Vision

↓

Subject Philosophy

↓

Learning Objectives

↓

Learning Progression

↓

Curriculum Modules

↓

Exit Criteria

↓

Prerequisites

↓

Unlocks

↓

Curriculum Maintenance Rules
```

---

# Canonical Subject Structure

Every curriculum document MUST contain the following sections in the same order.

---

# 1. Header

Required

```
# PrepOS Curriculum Constitution

File:
Version:
Status:
Owner:
```

---

# 2. Subject Title

Example

```
# Database Management Systems
```

---

# 3. Vision

Purpose

Explain WHY this subject exists.

Describe

- Engineering importance
- Production relevance
- Interview relevance
- Long-term value

This section should inspire the learner.

---

# 4. Subject Philosophy

Purpose

Explain HOW PrepOS teaches this subject.

Examples

Traditional education

↓

Memorization

PrepOS

↓

Engineering Understanding

↓

Production Thinking

↓

Interview Readiness

---

# 5. Learning Objectives

Purpose

Define measurable outcomes.

Every objective should begin with an action verb.

Examples

- Explain
- Design
- Analyze
- Implement
- Optimize
- Debug
- Evaluate

---

# 6. Subject Progression

Purpose

Show the complete learning journey.

Use an ASCII progression.

Example

```
Foundation

↓

Basic

↓

Intermediate

↓

Advanced

↓

Expert
```

This progression should match the Learning Progression Framework.

---

# 7. Curriculum Modules

Purpose

Break the subject into progressively ordered modules.

Every module must follow the exact same internal structure.

---

## Module Template

Every module MUST contain the following sections.

---

### Module Name

Example

```
## Module 4 — Indexing
```

---

### Purpose

Explain

Why this module exists.

---

### Major Areas

List all major concepts.

Example

- Clustered Index
- Non-Clustered Index
- Composite Index
- Covering Index

---

### Learning Outcomes

Learner should be able to

- Explain
- Design
- Compare
- Optimize
- Debug

---

### Interview Focus

Mention

- Beginner
- Intermediate
- Advanced

or

Low

Medium

High

Critical

---

### Production Relevance

Explain where this module appears in production software.

Example

Caching

Database Engines

Search Engines

Distributed Systems

Microservices

Cloud

Analytics

---

### Common Mistakes

Mention common misconceptions.

---

### Recommended Practice

Examples

MCQs

Implementation

Debugging

Case Studies

Interview Problems

Mini Projects

---

### Unlocks

Mention what this module enables next.

Example

```
Indexing

↓

Query Optimization

↓

Database Internals
```

---

# 8. Exit Criteria

Purpose

Define what mastery means.

Examples

Learner should be able to

- Explain concepts
- Solve interview problems
- Build production software
- Analyze trade-offs
- Debug systems

---

# 9. Prerequisites

List prerequisite subjects.

Example

Programming Fundamentals

↓

Java

↓

DSA

---

# 10. Unlocks

List subjects unlocked after completion.

Example

Operating Systems

Computer Networks

System Design

Backend Engineering

Distributed Systems

Cloud

---

# 11. Curriculum Maintenance Rules

Purpose

Ensure long-term consistency.

Rules

- Preserve prerequisite ordering.
- Never introduce advanced concepts before foundations.
- Prefer additive changes.
- Avoid duplicate topics.
- Maintain stable module identifiers.
- Preserve logical progression.
- Update dependencies when introducing new modules.
- Keep production relevance aligned with modern engineering.
- Maintain interview relevance across supported companies.

---

# Canonical Module Ordering Rules

Every subject should move from

```
Terminology

↓

Core Concepts

↓

Internal Working

↓

Implementation

↓

Optimization

↓

Advanced Concepts

↓

Production Engineering

↓

Interview Preparation
```

No subject may violate this progression.

---

# Curriculum Quality Checklist

Before a subject is considered complete, verify

✓ Complete progression

✓ Beginner friendly

✓ Expert depth

✓ Production relevance

✓ Interview relevance

✓ No duplicate topics

✓ Logical ordering

✓ Strong prerequisites

✓ Clear learning outcomes

✓ Consistent module template

✓ Exit criteria defined

✓ Unlock path defined

✓ Maintenance rules included

---

# Parser Expectations

The parser should assume every subject follows this template.

No subject-specific parsing logic should exist.

All curriculum documents must be parseable using the same pipeline.

---

# Future Compatibility

This template is intentionally extensible.

Future sections may include

- AI Mentor Guidance
- Visual Learning Assets
- Interactive Labs
- Practice Repositories
- Video References
- Company Learning Paths
- Adaptive Assessments
- Capstone Projects

These additions must preserve backward compatibility.

---

# Final Principle

Every curriculum document should answer one question:

**"If a learner completes this subject, what new engineering capabilities have they gained?"**

If the answer is unclear,

the curriculum should be redesigned.

This template serves as the canonical blueprint for every present and future PrepOS subject.