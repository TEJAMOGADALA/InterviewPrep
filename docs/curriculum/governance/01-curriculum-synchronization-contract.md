# PrepOS Curriculum Synchronization Contract

**File:** `docs/curriculum/governance/01-curriculum-synchronization-contract.md`

Version: 1.0

Status: Canonical

Owner: PrepOS Architecture Team

---

# Purpose

This document defines the synchronization contract between the canonical curriculum documents and the implementation inside the PrepOS platform.

Its purpose is to ensure that:

- Curriculum
- Roadmap Generator
- roadmap_v1.json
- Adaptive Learning Engine
- Mission Engine
- Dashboard

remain synchronized throughout the lifetime of the project.

This document is implementation governance.

It is NOT part of the learner curriculum.

---

# Canonical Source of Truth

The following subject documents are the ONLY canonical curriculum source.

```
01-programming-fundamentals.md
02-java.md
03-dsa.md
04-dbms.md
05-operating-systems.md
06-computer-networks.md
07-lld.md
08-hld.md
```

Nothing inside the runtime may introduce curriculum that does not exist inside these documents.

---

# Synchronization Rule

The synchronization direction is strictly one-way.

```
Curriculum Markdown
        │
        ▼
Roadmap Generator
        │
        ▼
roadmap_v1.json
        │
        ▼
Roadmap Engine
        │
        ▼
Adaptive Engine
        │
        ▼
Mission Engine
        │
        ▼
Dashboard
```

No runtime component may become a curriculum source.

---

# Curriculum Identity

Every curriculum element must have a unique identity.

The generator shall preserve existing IDs whenever possible to avoid invalidating learner progress.

Every generated roadmap node must be traceable to one canonical curriculum topic.

---

# Required Synchronization Scope

The generator shall synchronize the following information from the curriculum into roadmap_v1.json.

## Subject

- Subject name
- Subject description
- Vision
- Learning objectives
- Prerequisites
- Unlocks

---

## Learning Levels

The canonical learning progression is:

```
Foundations

↓

Basic

↓

Intermediate

↓

Advanced

↓

Expert
```

The runtime implementation may internally map stages differently, but the curriculum hierarchy must remain unchanged.

---

## Modules

For every module synchronize:

- Module name
- Purpose
- Learning level
- Module ordering
- Module prerequisites

---

## Topics

Synchronize:

- Topic name
- Difficulty
- Interview relevance
- Learning objectives

---

## Metadata

Synchronize:

- Difficulty
- Estimated learning time
- Interview frequency
- Company importance
- Mastery weight
- Related topics
- Revision metadata
- Learning objectives

---

## Production Context

Every roadmap node should preserve production relevance when available.

Examples include:

- Production engineering applications
- Real-world systems
- Industry use cases

---

## Interview Context

Synchronize:

- Interview importance
- Common interview patterns
- Frequently asked concepts

---

## Practice Context

Synchronize where applicable:

- Practice recommendations
- Common mistakes
- Revision checklist

---

# Synchronization Rules

The synchronization process may:

- Add missing curriculum nodes
- Add missing metadata
- Add missing prerequisite relationships
- Add unlock relationships
- Improve ordering consistency
- Preserve existing IDs whenever possible

The synchronization process shall NOT:

- Invent curriculum
- Remove canonical curriculum
- Reorder canonical learning progression
- Introduce topics not present in the curriculum
- Break learner progress IDs without migration

---

# Runtime Scope

The synchronization pass is NOT permitted to redesign runtime architecture.

The following components are outside the scope of synchronization:

- Adaptive Engine redesign
- Dashboard redesign
- Markdown parser implementation
- Curriculum compiler
- Generator rewrite
- UI redesign
- Database redesign
- Authentication
- Mission redesign

These items belong to future architectural releases.

---

# Validation Requirements

After synchronization:

The generated roadmap shall satisfy:

- No duplicate IDs
- No broken prerequisites
- No orphan nodes
- No missing metadata
- No learning progression violations
- No prerequisite violations
- No invalid company mappings
- No invalid related-topic mappings

---

# Acceptance Criteria

The synchronization pass is complete only if:

✓ All eight canonical subjects are represented.

✓ Programming Fundamentals exists as a roadmap track.

✓ Java matches the canonical curriculum.

✓ DSA matches the canonical curriculum.

✓ DBMS matches the canonical curriculum.

✓ Operating Systems matches the canonical curriculum.

✓ Computer Networks matches the canonical curriculum.

✓ Low-Level Design matches the canonical curriculum.

✓ High-Level Design matches the canonical curriculum.

✓ Required metadata exists.

✓ Learning progression is preserved.

✓ Prerequisites are valid.

✓ Unlock chains are preserved.

✓ roadmap_v1.json regenerates successfully.

✓ Existing learner progress is preserved wherever possible.

---

# Out of Scope

The following work is intentionally deferred.

- Markdown parser
- Curriculum AST
- Dynamic dashboard
- Generator rewrite
- Curriculum compiler
- Source heading anchors
- Runtime stage redesign
- Dashboard analytics redesign
- Resume / Behavioral / Projects curriculum

These belong to future releases.

---

# Freeze Policy

After successful synchronization:

- Curriculum is frozen.
- Generator is frozen.
- roadmap_v1.json is regenerated.
- Persona validation is executed.
- Phase 2 is considered complete.

Any future curriculum modification must begin from the canonical Markdown documents and repeat the synchronization process.
