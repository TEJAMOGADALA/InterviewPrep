# PrepOS Company Intelligence
# Company Knowledge Schema

---

# Document Metadata

| Property | Value |
|----------|--------|
| Document | Company Knowledge Schema |
| Version | 1.0 |
| Status | Draft |
| Owner | Company Intelligence |
| Category | Metadata Contract |
| Last Updated | 2026-08-05 |

---

# Executive Summary

The Company Knowledge Schema defines the canonical metadata contract for every company supported by PrepOS.

Every company profile must conform to this schema.

The schema ensures:

- Consistency
- Extensibility
- Machine readability
- Explainability
- Versionability

The Adaptive Learning Engine consumes this metadata to personalize interview preparation.

---

# Design Principles

The schema follows these principles:

1. Metadata over code
2. Configuration over hardcoding
3. Explainable intelligence
4. Extensible structure
5. Backward compatibility
6. Evidence-driven knowledge

---

# Required Sections

Every company document MUST contain the following sections.

```
Metadata

↓

Company Overview

↓

Engineering Philosophy

↓

Hiring Philosophy

↓

Interview Pipeline

↓

Evaluation Signals

↓

Subject Importance

↓

Module Importance

↓

Topic Importance

↓

Coding Expectations

↓

Low-Level Design

↓

High-Level Design

↓

Behavioral Expectations

↓

Role Differences

↓

Recent Trends

↓

Preparation Strategy

↓

Evidence Summary

↓

References
```

---

# Metadata

Every company must define:

| Field | Description |
|--------|-------------|
| Company Name | Official company name |
| Company Category | Product, Service, Enterprise, FinTech, etc. |
| Headquarters | Company headquarters |
| Engineering Scale | Approximate engineering organization |
| Last Reviewed | Date research completed |
| Research Version | Documentation version |
| Confidence | Overall research confidence |

---

# Company Categories

Supported categories:

- Product Company
- Service Company
- Enterprise Software
- FinTech
- SaaS
- Cloud Provider
- AI Company

Additional categories may be introduced without changing the schema.

---

# Interview Pipeline

Document every stage.

Each stage contains:

- Name
- Purpose
- Duration
- Evaluation Criteria
- Difficulty
- Confidence
- Evidence Source

---

# Evaluation Signals

Each company must identify the major evaluation signals.

Examples:

- Problem Solving
- Coding Ability
- System Design
- Low-Level Design
- Leadership
- Communication
- Culture Fit
- Ownership
- Learning Ability

Each signal must include:

- Importance
- Description
- Typical Interview Stage
- Confidence

---

# Subject Taxonomy

Every company evaluates the same canonical subject set.

Current subjects:

- Programming Fundamentals
- Java
- Data Structures & Algorithms
- Database Management Systems
- Operating Systems
- Computer Networks
- Low-Level Design
- High-Level Design

Future subjects:

- Python
- Go
- C++
- JavaScript
- Cloud Computing
- AI / Machine Learning
- LLM Engineering
- DevOps

---

# Subject Importance

Each subject must define:

- Importance
- Interview Stage
- Experience Level
- Reason
- Confidence

Allowed importance values:

- Critical
- Very High
- High
- Medium
- Low
- Very Low

---

# Module Taxonomy

Each subject contains modules.

Example:

Programming Fundamentals

- Variables
- Functions
- OOP
- SOLID
- Exception Handling
- Memory

Java

- Collections
- Streams
- Concurrency
- Multithreading
- JVM
- Generics
- Reflection

DSA

- Arrays
- Strings
- Linked Lists
- Trees
- Graphs
- Dynamic Programming
- Greedy
- Backtracking
- Tries
- Heaps

DBMS

- SQL
- Transactions
- Indexing
- Normalization
- Query Optimization

Operating Systems

- Processes
- Threads
- Deadlocks
- Scheduling
- Virtual Memory

Computer Networks

- HTTP
- HTTPS
- TCP/IP
- DNS
- Load Balancing

The taxonomy may expand without schema changes.

---

# Module Metadata

Every module must contain:

- Importance
- Reason
- Confidence
- Typical Interview Stage

---

# Topic Metadata

Topics inherit metadata from modules while allowing company-specific overrides.

Each topic contains:

- Importance
- Frequency
- Difficulty
- Confidence
- Notes

---

# Coding Expectations

Every company documents:

- Coding difficulty
- Coding style
- Platforms
- Language preferences
- Time constraints
- Problem distribution
- Optimization expectations

---

# Design Expectations

Separate:

## Low-Level Design

- Importance
- Typical questions
- Experience applicability

## High-Level Design

- Importance
- Typical systems
- Distributed concepts
- Experience applicability

---

# Behavioral Expectations

Document:

- Leadership
- Communication
- Collaboration
- Ownership
- Problem Solving
- Learning Mindset

---

# Role Matrix

Every company compares:

- New Graduate
- SDE-1
- SDE-2
- Senior Engineer
- Staff Engineer

Each role documents:

- Coding
- Design
- Leadership
- Expected autonomy

---

# Research Confidence

Every conclusion must include one of:

High

Medium

Low

---

# Evidence Types

Every finding should specify its evidence source.

Supported evidence:

- Official Documentation
- Official Careers
- Official Engineering Blog
- Recruiter Guidance
- Engineering Talks
- Community Consensus
- Interview Reports
- Research Platform

---

# Reference Requirements

Every company document must include:

- Official references
- Community references
- Research references

References should support conclusions rather than merely being listed.

---

# Versioning

Every company profile must maintain:

- Version
- Last Updated
- Major Changes

Interview trends evolve over time.

Version history ensures traceability.

---

# Validation Rules

A valid company profile must:

✓ Follow the schema

✓ Include evidence

✓ Include confidence

✓ Distinguish official guidance from community consensus

✓ Avoid unsupported assumptions

✓ Remain machine-readable

---

# Planner Intelligence

Every company profile MUST include a Planner Intelligence section.

This section translates company research into adaptive planning guidance.

Planner Intelligence is consumed by the Adaptive Learning Engine.

It does NOT contain hardcoded learner scenarios.

Instead it defines planning philosophy and weighting guidance.

The planner combines these signals with:

- learner mastery
- progress
- interview timeline
- study hours
- experience
- revision schedule
- company priorities

to generate the final mission.

## Planning Philosophy

Every company profile must define:

- Primary interview philosophy
- Knowledge progression philosophy
- Interview readiness philosophy
- Learning progression philosophy

Example:

Google

Interview Philosophy

Problem Solving First

↓

Strong Fundamentals

↓

Scalable Thinking

↓

Engineering Judgment

## Planning Priority Hierarchy

Every company must define the relative planning hierarchy.

Example

Google

DSA

↓

Programming

↓

System Design

↓

Core CS

↓

Behavioral

Oracle

Java

↓

LLD

↓

Database

↓

Core CS

↓

DSA

This hierarchy is guidance only.

The Adaptive Learning Brain combines it with learner signals.

## Adaptive Biases

Every company profile must document:

Coding Bias

Revision Bias

System Design Bias

Behavioral Bias

Core CS Bias

Difficulty Bias

Timeline Bias

Experience Bias

Each bias should explain:

When it becomes stronger.

When it becomes weaker.

What learner signals influence it.

## Mission Composition Guidance

Every company profile defines preferred mission composition.

Document recommended balance for:

Primary Learning

Support Reading

Coding Practice

Revision

Interview Preparation

Behavioral Practice

The planner adapts this composition according to learner context.

## Coding Arena Guidance

Document:

Preferred coding proportion

Difficulty progression

Problem diversity

Topic distribution

Relationship between today's mission and Coding Arena

Example

70%

Today's primary topic

30%

Revision / reinforcement topics

## Revision Strategy

Every company profile documents:

Revision importance

Spacing recommendations

Revision triggers

Confidence thresholds

Mastery thresholds

Revision priority relative to new learning

## Timeline Adaptation

Every company documents how planning emphasis shifts as interviews approach.

Examples

6 months

↓

Strong foundations

↓

3 months

↓

Balanced preparation

↓

1 month

↓

Interview-focused preparation

↓

2 weeks

↓

Revision

↓

Mock Interviews

↓

Weak-area reinforcement

## Experience Progression

Every company documents expectations for:

Student

Fresher

1–3 Years

3–5 Years

5+ Years

Each level should explain:

Expected coding maturity

Design expectations

Leadership expectations

Interview depth

Mission emphasis

## Planner Heuristics

This section documents high-level planning heuristics.

These are NOT implementation rules.

They describe general planning tendencies.

Examples

Strong DSA

+

Weak Core CS

↓

Core CS gains additional priority.

Strong Programming

+

Weak LLD

↓

Design becomes eligible.

Short timeline

↓

Interview-oriented topics gain additional weight.

High mastery

↓

Revision frequency decreases.

The Adaptive Learning Engine derives decisions from weighted signals rather than explicit scenario matching.

## Adaptive Interpretation

This section explains how the Adaptive Learning Brain should interpret company intelligence.

The planner must never:

- hardcode companies
- hardcode learner roles
- hardcode interview paths

Instead it combines:

Company Intelligence

+

Knowledge Graph

+

Learner Context

+

Mastery

+

Progress

+

Timeline

+

Mission History

+

Revision State

+

Adaptive Weights

to produce today's mission.

## Explainability Metadata

Every recommendation originating from Company Intelligence should be explainable.

The planner should always be capable of answering:

Why was this topic selected?

Why was another topic postponed?

Which company signals influenced the decision?

Which learner signals outweighed company priorities?

This metadata enables future "Why Today's Mission?" features.

## Machine Readiness

Every company profile should remain machine-readable.

Sections should be structured to support:

Knowledge Graph generation

Adaptive Scoring Engine

Mission Planner

Future AI Mentor

Future Recommendation APIs

without requiring document restructuring.

# Adaptive Weight Sources

Every importance value should specify its origin.

Examples:

Official documentation

Engineering blogs

Recruiter guidance

Community consensus

Historical interview frequency

Evidence confidence

If multiple sources disagree, the company profile should document the rationale used to determine the final weight.



# Future Extensions

The schema is designed to support:

- Company-specific role profiles
- Region-specific interview differences
- AI interview formats
- Live coding platform changes
- Company trend versioning

---

# Revision History

| Version | Date | Author | Description |
|----------|------|---------|-------------|
| 1.0 | 2026-08-05 | PrepOS Architecture Team | Initial Company Knowledge Schema |