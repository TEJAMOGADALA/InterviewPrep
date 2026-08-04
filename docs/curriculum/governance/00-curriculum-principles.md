# PrepOS Curriculum Constitution
**File:** `docs/curriculum/00-curriculum-principles.md`

---

# PrepOS Curriculum Constitution

Version: 1.0

Status: Canonical

Owner: PrepOS Architecture Team

---

# Vision

PrepOS is not an interview preparation website.

PrepOS is an AI-powered Software Engineering Career Operating System that guides learners from absolute beginner to senior software engineer through an adaptive, explainable and production-oriented curriculum.

The curriculum defined in this repository serves as the **single source of truth** for every learning experience inside PrepOS.

Every AI system, recommendation engine, mission planner, dashboard, readiness score, revision engine and future intelligent module must derive its knowledge from this curriculum.

---

# Mission

Enable every learner to progress from

No Programming Knowledge

↓

Software Engineering Foundations

↓

Professional Software Engineer

↓

Top Product-Based Company

↓

Continuous Career Growth

using a structured curriculum rather than disconnected interview topics.

---

# Core Principles

## Principle 1 — Engineering First

PrepOS teaches learners to become excellent software engineers.

Interview success is a natural consequence of engineering excellence.

The curriculum must never optimize purely for interview memorization.

---

## Principle 2 — Strong Prerequisites

No advanced concept may appear before its mandatory prerequisites.

Example:

Software Architecture

↓

Client–Server Architecture

↓

Scalability

↓

Caching

↓

Distributed Systems

↓

CAP Theorem

Never allow:

Student

↓

CAP Theorem

without first understanding Software Architecture.

---

## Principle 3 — Production-Oriented Learning

Every subject should explain:

- What
- Why
- How
- Trade-offs
- Real-world usage
- Interview relevance

The curriculum should always connect theory with production software engineering.

---

## Principle 4 — Adaptive Learning

Every learner follows a different journey.

Recommendations depend on:

- Experience
- Assessment
- Knowledge State
- Confidence
- Mastery
- Weakness
- Target Companies
- Interview Timeline
- Previous Learning

The curriculum must support adaptive navigation.

---

## Principle 5 — Explainability

Every recommendation must be explainable.

The system should always answer:

Why today?

Why this topic?

Why not another topic?

What does this unlock?

Which company benefits?

---

## Principle 6 — Continuous Career Growth

PrepOS is not limited to interview preparation.

The curriculum should continue beyond obtaining the first job.

The knowledge graph must support long-term software engineering growth.

---

## Principle 7 — Single Source of Truth

This curriculum specification is the canonical source.

Roadmap JSON

Mission Planner

AI Mentor

Career Intelligence

Interview Readiness

Dashboard

must remain consistent with this specification.

---

# Curriculum Architecture

Every subject follows the same conceptual lifecycle.

```

Subject

↓

Overview

↓

Learning Objectives

↓

Foundations

↓

Basic

↓

Intermediate

↓

Advanced

↓

Expert

↓

Interview Preparation

↓

Revision

↓

Capstone

```

The UI does not necessarily expose these levels.

They represent the conceptual progression used by the adaptive engine.

---

# Subject Catalog

PrepOS currently defines the following primary subjects.

1. Programming Fundamentals

2. Java

3. Data Structures & Algorithms

4. Database Management Systems

5. Operating Systems

6. Computer Networks

7. Low-Level Design

8. High-Level Design

9. Projects

10. Resume & LinkedIn

11. Behavioral

12. Interview Preparation

Future subjects may include:

Cloud

Docker

Kubernetes

DevOps

Linux

System Programming

AI Engineering

Machine Learning

Data Engineering

Frontend

Backend

Mobile

Security

---

# Learning Levels

Every learning node belongs to one of five difficulty levels.

## Foundation

Target audience:

No programming knowledge.

Goal:

Introduce the subject.

Teach terminology.

Develop intuition.

---

## Basic

Target audience:

Students

Freshers

Goal:

Build core understanding.

Enable solving beginner problems.

---

## Intermediate

Target audience:

0–2 years experience.

Goal:

Professional software engineering knowledge.

Interview readiness.

---

## Advanced

Target audience:

2–5 years experience.

Goal:

Distributed systems.

Performance.

Architecture.

Complex production systems.

---

## Expert

Target audience:

Senior Engineers

Staff Engineers

Top Product Company Interviews

Goal:

System trade-offs.

Optimization.

Large-scale architecture.

---

# Learning Node Standard

Every learning node should eventually support the following metadata.

Mandatory

- Unique Identifier
- Parent Identifier
- Subject
- Difficulty
- Estimated Study Time
- Learning Objectives
- Prerequisites
- Unlock Conditions

Recommended

- Interview Importance
- Company Weighting
- Revision Priority
- Practice Requirement
- Confidence Weight
- Mastery Weight
- Knowledge Dependencies
- Tags

Future

- Recommended Resources
- Interactive Labs
- AI Mentor Hints
- Video References
- Code Templates

---

# Knowledge Graph Rules

The curriculum forms a directed acyclic graph.

Every node should satisfy:

No Cycles

No Duplicate Nodes

No Orphan Nodes

No Broken Prerequisites

No Missing Parent

No Unreachable Nodes

Cross-subject dependencies are encouraged.

Example:

Programming Fundamentals

↓

Java

↓

Collections

↓

HashMap

↓

LRU Cache

---

# Company Awareness

Every node may optionally define company relevance.

Examples:

Google

Microsoft

Amazon

Meta

Apple

Netflix

Uber

Oracle

LinkedIn

Atlassian

Stripe

Databricks

Snowflake

Goldman Sachs

Flipkart

PhonePe

PayPal

Razorpay

Walmart Global Tech

Company preference should influence recommendation ordering.

Company preference must never violate prerequisite ordering.

---

# Adaptive Learning Rules

The adaptive engine should prioritize:

Prerequisite Correctness

↓

Weak Subjects

↓

Interview Timeline

↓

Company Goals

↓

Knowledge Confidence

↓

Revision Due

↓

Mission Continuity

↓

Estimated Study Time

↓

Difficulty Progression

No learner should receive advanced recommendations before foundational mastery.

---

# Curriculum Quality Rules

Every subject must satisfy:

✓ Complete progression

✓ No stage gaps

✓ Interview readiness

✓ Production relevance

✓ Logical ordering

✓ Cross-subject consistency

✓ Clear prerequisites

✓ Beginner accessibility

✓ Expert depth

---

# Curriculum Evolution Policy

The curriculum evolves incrementally.

When adding topics:

Do NOT rename existing nodes unnecessarily.

Do NOT remove production-ready content.

Prefer additive changes.

Preserve backward compatibility.

Maintain stable identifiers.

Review prerequisite relationships.

Validate adaptive behavior.

---

# Review Checklist

Every curriculum update must answer:

Does this improve beginner learning?

Does this improve experienced learners?

Does this improve adaptive planning?

Does this improve interview preparation?

Does this preserve prerequisite correctness?

Does this avoid duplicates?

Does this improve production relevance?

Would this recommendation make sense for a real engineer?

If any answer is "No",

the curriculum change should be reconsidered.

---

# Long-Term Vision

PrepOS should become the world's most comprehensive Software Engineering Knowledge Graph.

Every future module—

AI Mentor

Career Intelligence

Mission Planner

Interview Simulator

Resume Intelligence

Skill Gap Analysis

Learning Analytics

Company Readiness

should consume this curriculum rather than implementing independent learning logic.

This document serves as the constitutional foundation for every future curriculum decision.