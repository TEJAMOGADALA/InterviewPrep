# PrepOS Adaptive Learning Engine
# Company Intelligence Engine

---

# Document Metadata

| Property | Value |
|----------|--------|
| Document | Company Intelligence Engine |
| Version | 1.0 |
| Status | Draft |
| Owner | Learning Engine |
| Category | Intelligence Layer |
| Depends On | 01 Vision, 02 Adaptive Brain, 06 Knowledge Graph |
| Used By | Strategy Engine, Mission Engine, Scoring Engine, AI Mentor |
| Last Updated | 2026-08-05 |

---

# Executive Summary

The Company Intelligence Engine transforms generic interview preparation into company-specific interview preparation.

Instead of following a static curriculum, PrepOS continuously adjusts the learner's preparation according to the interview expectations of the learner's target companies.

However, company priorities never act in isolation.

The Company Intelligence Engine contributes one important signal to the Adaptive Learning Brain, where it is balanced with learner readiness, knowledge mastery, revision requirements, interview timeline, and long-term curriculum progression.

---

# Purpose

The Company Intelligence Engine answers questions such as:

- What topics are most important for Google?
- How should Oracle preparation differ from Microsoft?
- Should DSA dominate today's mission?
- Should LLD become the current focus?
- Does this learner have enough Core CS knowledge for the target company?
- Which weaknesses matter most for the selected companies?

---

# Scope

The Company Intelligence Engine is responsible for:

- Company-specific curriculum weighting
- Interview pattern intelligence
- Topic importance estimation
- Multi-company optimization
- Company readiness estimation
- Company-aware recommendation support

It is NOT responsible for:

- Mission generation
- Learner memory
- Knowledge mastery calculation
- Difficulty progression
- Curriculum structure

---

# Design Philosophy

The Company Intelligence Engine follows six principles.

---

## 1. Companies Influence Planning

Company expectations should influence preparation.

They should never completely control it.

---

## 2. Learner State Always Matters

A learner's actual knowledge is more important than company preferences.

Company priorities cannot override missing prerequisites.

---

## 3. Curriculum Integrity

Company optimization should never violate the curriculum DAG.

Prerequisites must always remain valid.

---

## 4. Strategy Before Weight

Company information influences strategy selection.

It should not directly select topics.

---

## 5. Explainability

Every company-driven recommendation must be explainable.

---

## 6. Extensibility

Adding a new company must require only metadata updates.

Planner code should remain unchanged.

---

# Position in Architecture

```
Target Company

↓

Company Intelligence

↓

Adaptive Learning Brain

↓

Strategy Engine

↓

Mission Engine
```

---

# Company Intelligence Pipeline

```
Learner Profile

↓

Target Company

↓

Interview Knowledge Base

↓

Company Weights

↓

Readiness Analysis

↓

Priority Adjustment

↓

Adaptive Planning
```

---

# Company Knowledge Model

Every supported company contains structured metadata.

Example

```
Google

{

Interview Pattern

Core Competencies

Topic Weights

Difficulty Expectations

Coding Emphasis

Design Emphasis

Behavioral Focus

Typical Interview Stages

Revision Priority

}
```

The planner consumes metadata rather than hardcoded company logic.

---

# Company Metadata

Every company stores:

- Company ID
- Company Name
- Company Category
- Interview Style
- Hiring Level
- Preferred Languages
- Topic Importance
- Difficulty Expectations
- Coding Expectations
- Design Expectations
- System Design Importance
- Behavioral Importance
- Revision Sensitivity

---

# Company Categories

Companies may belong to categories.

Examples

Product Companies

- Google
- Meta
- Uber
- Atlassian

Enterprise Companies

- Oracle
- Salesforce
- SAP

Service Companies

- TCS
- Infosys
- Wipro
- Cognizant

FinTech

- Stripe
- Razorpay
- PayPal

The category provides a default baseline.

Each company then overrides specific metadata.

---

# Topic Importance Model

Each curriculum entity stores company-specific importance.

Example

```
Graphs

Google

★★★★★

Microsoft

★★★★☆

Oracle

★★★☆☆

Infosys

★★☆☆☆
```

Importance is represented as metadata rather than planner logic.

---

# Company Readiness

PrepOS continuously estimates readiness for every supported company.

Example

```
Google

82%

Oracle

71%

Amazon

78%

Microsoft

80%
```

Readiness depends on:

- Curriculum coverage
- Mastery
- Coding performance
- Revision health
- Design readiness
- Confidence
- Interview timeline

---

# Company Weighting Philosophy

Company importance is only one component of planning.

Final priority should emerge from multiple signals.

```
Priority

=

Company Importance

×

Knowledge Gap

×

Readiness

×

Timeline Urgency

×

Revision Need

×

Curriculum Readiness
```

No single factor should dominate.

---

# Signal Balance

The planner balances:

- Company importance
- Learner weakness
- Mastery
- Confidence
- Coding evidence
- Revision debt
- Learning continuity
- Difficulty progression
- Available study time

Company importance adjusts the score.

It does not replace the other signals.

---

# Company Strategy Examples

These examples illustrate expected behavior.

They are validation examples only.

They must never be hardcoded.

---

## Example 1

Target

Google

Learner

Strong Programming Fundamentals

Strong Java

Weak DSA

Weak Graphs

Mission

Primary

Graphs

Coding

Medium Graph Problems

Support

Java Collections

Revision

Recursion

Reason

Google heavily values graph-based problem solving.

---

## Example 2

Target

Google

Learner

Strong DSA

Weak Operating Systems

Weak DBMS

Timeline

6 Months

Mission

Primary

Operating Systems

Support

DBMS

Coding

Hard DSA Revision

Reason

DSA is already mastered.

Improving Core CS now increases overall interview readiness.

---

## Example 3

Target

Oracle

Learner

Strong Programming

Strong DSA

Weak LLD

Weak HLD

Mission

Primary

Low Level Design

Support

Operating Systems

Coding

Design Exercise

Revision

Advanced DSA

Reason

Oracle values design competence while maintaining strong engineering fundamentals.

---

## Example 4

Target

Infosys

Learner

Strong Programming

Weak DBMS

Weak Networking

Mission

Primary

DBMS

Support

Computer Networks

Coding

Easy SQL Practice

Reason

Core CS contributes more interview value than advanced algorithms.

---

# Multi-Company Planning

Learners may prepare for multiple companies.

Example

```
Google

Oracle

Microsoft
```

The Company Intelligence Engine computes a combined readiness profile.

Priority should consider:

- Common requirements
- Unique requirements
- Timeline
- Interview order

The planner should maximize preparation efficiency.

---

# Company Evolution

Interview patterns change.

The Company Intelligence Engine must support updating metadata without requiring planner changes.

Examples:

- New interview rounds
- New technologies
- Increased LLD emphasis
- AI interview topics

Only metadata should change.

---

# Explainability

Every company-driven recommendation should include reasoning.

Example

```
Today's Mission

Operating Systems

Reason

Google readiness is below target.

Operating Systems contributes to Google interviews.

Operating Systems also unlocks LLD.

DSA mastery already exceeds expected level.
```

---

# Constraints

The Company Intelligence Engine must never:

- Ignore learner readiness
- Ignore curriculum prerequisites
- Ignore timeline
- Hardcode company behavior
- Override adaptive planning

---

# Future Extensions

Future versions may include:

- Real interview feedback ingestion
- Dynamic interview trend analysis
- Community success statistics
- AI-generated company profiles
- Salary-based optimization
- Region-specific interview variations
- Role-specific weighting (Backend, Frontend, Full Stack, AI)

---

# Acceptance Criteria

The Company Intelligence Engine is considered successful when:

- Company metadata is entirely configuration-driven.
- Adding a new company requires no planner changes.
- Company weights influence—but do not dominate—planning.
- Recommendations remain explainable.
- Curriculum integrity is preserved.
- Multi-company preparation behaves predictably.

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
| 1.0 | 2026-08-05 | PrepOS Architecture Team | Initial architecture specification for the Company Intelligence Engine. |