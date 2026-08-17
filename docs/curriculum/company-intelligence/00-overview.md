# PrepOS Company Intelligence
# Overview

---

# Document Metadata

| Property | Value |
|----------|--------|
| Document | Company Intelligence Overview |
| Version | 1.0 |
| Status | Draft |
| Owner | Company Intelligence |
| Category | Architecture |
| Last Updated | 2026-08-05 |

---

# Executive Summary

The Company Intelligence subsystem enables PrepOS to prepare learners for specific companies rather than delivering a generic interview curriculum.

Instead of assuming every company evaluates candidates identically, PrepOS models interview expectations as structured, evidence-backed metadata.

This metadata influences—but never dictates—the Adaptive Learning Engine.

The learner remains at the center of every planning decision.

---

# Why Company Intelligence Exists

Different companies prioritize different competencies.

Examples include:

- Google emphasizes algorithmic problem solving and scalable thinking.
- Oracle places stronger emphasis on Java and software design.
- Product companies generally expect stronger system design than service companies.
- FinTech organizations often value distributed systems, reliability, and concurrency.

These differences should influence learning priorities without breaking curriculum integrity.

---

# Architectural Philosophy

Company Intelligence is a knowledge subsystem.

It is **not** a decision engine.

It does not:

- Generate missions
- Select topics
- Calculate mastery
- Modify learner progress

Instead, it provides structured evidence that the Adaptive Learning Engine consumes.

---

# Position in the Architecture

```
Research

↓

Company Knowledge Base

↓

Company Intelligence

↓

Adaptive Learning Brain

↓

Mission Planner

↓

Learner
```

---

# Separation of Responsibilities

## Company Intelligence

Responsible for:

- Interview expectations
- Company-specific priorities
- Engineering philosophy
- Coding expectations
- Design expectations
- Behavioral expectations
- Research evidence

---

## Adaptive Learning Brain

Responsible for:

- Strategy selection
- Learner modeling
- Mission planning
- Difficulty progression
- Revision scheduling
- Personalization

---

# Core Design Principles

The subsystem follows six guiding principles.

## Evidence First

Every recommendation originates from verifiable research.

---

## Metadata Driven

Company behavior is defined through metadata rather than planner code.

---

## Explainability

Every company influence should be explainable.

The planner must always be able to answer:

"Why is this topic recommended?"

---

## Extensibility

Adding a new company should require only:

- Research
- Company profile

No planner modifications should be necessary.

---

## Learner-Centric Planning

Company priorities never override learner readiness.

Missing prerequisites, weak fundamentals, and revision debt remain first-class planning signals.

---

## Continuous Evolution

Interview processes evolve.

The Company Intelligence subsystem must support ongoing updates without architectural changes.

---

# Information Hierarchy

```
Company

↓

Interview Philosophy

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

Behavioral Expectations

↓

Preparation Guidance
```

---

# Relationship with Other Components

The subsystem integrates with:

- Knowledge Graph
- Strategy Engine
- Scoring Engine
- Mission Engine
- Coding Arena
- AI Mentor

Each consumes company metadata differently.

---

# Supported Companies

The initial knowledge base includes:

- Google
- Microsoft
- Uber
- Atlassian
- Adobe
- LinkedIn
- Stripe
- PhonePe
- Flipkart
- Goldman Sachs
- PayPal
- Salesforce
- Oracle
- Zoho

Additional companies may be added without changing the architecture.

---

# Research Methodology

Every company profile is built using:

Tier 1

- Official documentation
- Official engineering blogs
- Recruiter guidance
- Engineering talks

Tier 2

- Community consensus
- Glassdoor
- Reddit
- Blind
- LeetCode Discuss

Tier 3

- Interview preparation platforms

Conflicting information is documented with confidence levels.

---

# Explainability

Every recommendation should be traceable.

Example:

Today's Mission

Graph Algorithms

Reason:

- High relevance for target company.
- Prerequisites satisfied.
- Weak learner mastery.
- Strong interview impact.

---

# Future Vision

The Company Intelligence subsystem will evolve to support:

- Role-specific interview paths
- Region-specific hiring differences
- AI-assisted interview formats
- Live interview trend monitoring
- Automated research updates
- Company readiness scoring

---

# Success Criteria

The subsystem is successful when:

- Company knowledge is evidence-backed.
- Planner logic contains no company-specific branching.
- New companies can be added without code changes.
- Recommendations remain explainable.
- Metadata integrates seamlessly with the Adaptive Learning Engine.

---

# Dependencies

Related Documents:

- Learning Engine Vision
- Adaptive Learning Brain
- Knowledge Graph
- Company Knowledge Schema
- Scoring Engine

---

# Revision History

| Version | Date | Author | Description |
|----------|------|---------|-------------|
| 1.0 | 2026-08-05 | PrepOS Architecture Team | Initial Company Intelligence overview |