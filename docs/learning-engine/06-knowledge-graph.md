# PrepOS Adaptive Learning Engine
# Knowledge Graph

---

# Document Metadata

| Property | Value |
|----------|--------|
| Document | Knowledge Graph |
| Version | 1.0 |
| Status | Draft |
| Owner | Learning Engine |
| Category | Knowledge Architecture |
| Depends On | 01 Vision & Philosophy, 02 Adaptive Learning Brain |
| Used By | Strategy Engine, Mission Engine, Scoring Engine, Company Intelligence, Coding Arena |
| Last Updated | 2026-08-05 |

---

# Executive Summary

The Knowledge Graph is the canonical representation of the interview curriculum inside PrepOS.

Unlike a traditional tree-based curriculum, the Knowledge Graph models interview preparation as a Directed Acyclic Graph (DAG) where every learning concept, dependency, relationship, company requirement, coding problem and revision path is represented as structured metadata.

The Knowledge Graph is the single source of truth for curriculum intelligence.

Every adaptive decision made by PrepOS must originate from this graph rather than hardcoded subject ordering.

---

# Purpose

The Knowledge Graph exists to answer questions such as:

- What should the learner study next?
- Which prerequisites are still missing?
- Which subjects become available after completing this one?
- Which concepts reinforce today's topic?
- Which coding problems belong to this topic?
- Which companies value this concept?
- Which modules depend on this knowledge?
- Which revision topics strengthen today's mission?

---

# Scope

The Knowledge Graph is responsible for:

- Representing curriculum structure
- Maintaining prerequisite relationships
- Maintaining dependency graphs
- Mapping companies to curriculum
- Mapping coding problems
- Supporting adaptive traversal
- Enabling explainable planning

The Knowledge Graph is NOT responsible for:

- Selecting today's strategy
- Mission generation
- Difficulty scoring
- Mastery calculation
- Learner memory

---

# Design Philosophy

The Knowledge Graph is built upon six architectural principles.

---

## 1. Curriculum is a Graph

Interview preparation is not linear.

Different learners may follow different valid learning paths.

The planner should traverse the graph based on learner state rather than a fixed sequence.

---

## 2. Dependencies are Explicit

Every dependency must be represented as metadata.

No prerequisite should exist inside planner code.

The planner must consume graph metadata rather than encode curriculum logic.

---

## 3. Relationships are Rich

A topic can participate in multiple relationships simultaneously.

Examples:

- prerequisite
- unlock
- supports
- reinforces
- revision
- coding
- interview relevance
- company importance

---

## 4. Extensibility

Adding a new subject should require:

- Curriculum definition
- Graph metadata

It should never require planner modifications.

---

## 5. Explainability

Every graph edge should be explainable.

Example:

```
LLD

depends on

Java
DSA
Operating Systems
```

The planner should always be capable of explaining why a topic is currently unavailable or why it has become eligible.

---

## 6. Metadata-Driven Intelligence

Behavior should emerge from metadata.

Never hardcode subject order.

Never hardcode prerequisite chains.

Never hardcode company paths.

---

# Position in Architecture

```
                 Curriculum
                      │
                      ▼
              Knowledge Graph
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
 Strategy Engine   Mission Engine  Company Intelligence
        │
        ▼
  Adaptive Planning
```

---

# Graph Hierarchy

The graph contains multiple abstraction levels.

```
Track (Subject)

↓

Module

↓

Topic

↓

Learning Node

↓

Coding Problems
```

Every level participates in graph relationships.

---

# Graph Entities

The Knowledge Graph contains the following entities.

## Subject

Examples:

- Programming Fundamentals
- Java
- DSA
- DBMS
- Operating Systems
- Computer Networks
- LLD
- HLD

---

## Module

Examples:

Trees

Collections

Transactions

Synchronization

TCP/IP

Design Patterns

---

## Topic

Examples:

Binary Search Tree

Deadlock

ACID

Normalization

Generics

Interfaces

---

## Learning Node

Atomic learning units.

Example:

AVL Tree Rotations

HashMap Collision Resolution

Semaphore vs Mutex

---

## Coding Problem

Represents practical reinforcement.

Each coding problem is attached to one or more learning nodes.

---

# Graph Relationships

Every entity may participate in multiple relationships.

---

## Subject Prerequisites

Represents academic dependencies.

Example

```
Programming Fundamentals

↓

Java

↓

├── DSA
├── DBMS
├── Operating Systems
└── Computer Networks

↓

LLD

↓

HLD
```

These relationships form a Directed Acyclic Graph.

---

## Subject Unlocks

Reverse representation of prerequisite edges.

Example

```
Java

unlocks

DSA

DBMS

Operating Systems

Computer Networks
```

---

## Recommended Next Subjects

Advisory relationship.

Unlike prerequisites, these edges express guidance rather than requirements.

The Strategy Engine may use these recommendations when multiple branches are available.

---

## Module Prerequisites

Modules may depend upon multiple modules.

Example

```
Trees

↓

Balanced Trees

↓

AVL Trees
```

---

## Topic Prerequisites

Topics inherit prerequisite relationships.

Example

```
HashMap

↓

Collision Resolution

↓

Rehashing
```

---

## Related Topics

Represents conceptual similarity.

Examples

```
HashMap

↔

HashSet
```

```
Deadlock

↔

Synchronization
```

Related topics support companion learning.

---

## Reinforcement Relationships

Defines complementary concepts.

Example

Primary

Graphs

Support

Recursion

Coding

DFS

Revision

Hash Maps

---

## Revision Relationships

Represents retrieval pathways.

Revision relationships are not identical to prerequisites.

They represent concepts frequently revised together.

---

## Coding Relationships

Maps learning concepts to Coding Arena.

Each learning node contains:

- Easy problems
- Medium problems
- Hard problems

Difficulty progression is metadata-driven.

---

## Company Relationships

Every node stores company relevance.

Example

```
Graphs

Google

★★★★★

Oracle

★★★

Infosys

★★
```

Company Intelligence consumes these weights.

---

# Graph Metadata

Each graph entity may contain:

- id
- title
- description
- category
- subject
- module
- topic
- prerequisites
- unlocks
- related_topics
- recommended_next_subjects
- coding_tags
- company_importance
- revision_tags
- estimated_duration
- difficulty
- language_support
- learning_stage

The graph should remain language-agnostic.

---

# Graph Traversal Philosophy

Traversal should always begin from learner state.

The planner should never traverse the graph sequentially.

Instead:

```
Learner State

↓

Eligible Subjects

↓

Eligible Modules

↓

Eligible Topics

↓

Rank Candidates

↓

Generate Mission
```

Traversal is adaptive.

---

# Unlock Model

Eligibility depends upon prerequisite satisfaction.

A subject becomes eligible only when all prerequisite subjects are effectively completed.

Module and topic eligibility follow the same principle.

The graph never partially unlocks prerequisite chains.

---

# Dynamic Branch Selection

After Java, multiple branches become available.

Example

```
Java

↓

DSA

DBMS

Operating Systems

Computer Networks
```

The planner chooses the branch that maximizes interview readiness.

Factors include:

- company
- timeline
- mastery
- memory
- strategy
- revision debt

The graph does not prescribe the branch.

It merely exposes the available branches.

---

# Cross-Subject Intelligence

The graph supports relationships across subjects.

Example

```
Operating Systems

supports

Concurrency

↓

Java Threads

↓

LLD
```

Cross-subject relationships improve companion recommendations.

---

# Coding Arena Integration

The Knowledge Graph is the canonical mapping layer between theory and coding.

Example

```
Topic

Binary Search Tree

↓

Coding Arena

Easy

2 Problems

Medium

4 Problems

Hard

3 Problems
```

The Mission Engine consumes these mappings.

---

# Future Subject Expansion

The graph is designed to support unlimited curriculum expansion.

Examples

Programming Languages

- Python
- C++
- Go
- JavaScript

Cloud

- AWS
- Azure
- GCP

AI

- Machine Learning
- LLMs
- RAG
- Vector Databases

Backend

- Spring Boot
- FastAPI
- Node.js

No planner modifications should be required.

---

# Graph Validation

Every graph build must validate:

✓ No cycles

✓ Valid references

✓ No orphan nodes

✓ Deterministic generation

✓ Valid prerequisite chains

✓ Company metadata integrity

✓ Language metadata integrity

✓ Related-topic integrity

---

# Explainability

Every graph traversal should be explainable.

Example

Today's Mission

Operating Systems

Reason

- Java completed
- Programming Fundamentals completed
- Operating Systems has high Google importance
- Operating Systems unlocks LLD
- Revision debt is low

---

# Constraints

The Knowledge Graph must never:

- Contain cyclic dependencies
- Depend on planner implementation
- Encode learner-specific information
- Duplicate curriculum logic
- Require hardcoded traversal

---

# Future Extensions

Future versions may include:

- Semantic graph traversal
- AI-generated graph edges
- Graph embeddings
- Skill similarity scoring
- Dynamic prerequisite inference
- Community learning paths
- Personalized knowledge graphs

---

# Acceptance Criteria

The Knowledge Graph is considered correct when:

- Every prerequisite is metadata-driven.
- Every planner decision originates from graph traversal.
- No subject order exists in code.
- New curriculum can be added without planner modification.
- Company metadata is graph-driven.
- Coding relationships remain consistent.
- Graph validation passes deterministically.

---

# Dependencies

Required Documents

- 01 Vision & Philosophy
- 02 Adaptive Learning Brain
- 03 Strategy Engine
- 04 Mission Engine
- 07 Company Intelligence
- 08 Scoring Engine

---

# Revision History

| Version | Date | Author | Description |
|----------|------|---------|-------------|
| 1.0 | 2026-08-05 | PrepOS Architecture Team | Initial architecture specification for the Knowledge Graph. |