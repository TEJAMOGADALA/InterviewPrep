# PrepOS Knowledge Graph Topic Schema
**File:** `docs/curriculum/00-topic-schema.md`

---

# PrepOS Knowledge Graph Topic Schema

Version: 1.0

Status: Canonical

Owner: PrepOS Architecture Team

---

# Purpose

This document defines the canonical schema that every learning topic inside PrepOS must follow.

It acts as the contract between:

- Curriculum
- Knowledge Graph
- Adaptive Engine
- AI Mentor
- Mission Planner
- Career Intelligence
- Interview Readiness
- Resume Intelligence
- Dashboard
- Revision Engine

Every learning node in PrepOS should be capable of supporting this schema, even if some fields are populated in future releases.

---

# Philosophy

A topic is NOT merely a title.

A topic represents a complete unit of knowledge.

Example:

Instead of

HashMap

PrepOS defines

HashMap

↓

Concept

↓

Internal Working

↓

Visualization

↓

Complexity

↓

Production Usage

↓

Interview Questions

↓

Practice

↓

Revision

↓

Unlocks

---

# Universal Topic Schema

Every topic should conceptually support the following sections.

---

# 1. Topic Metadata

Purpose

Basic information describing the topic.

Fields

- Unique ID
- Title
- Slug
- Subject
- Category
- Module
- Section
- Difficulty
- Learning Level
- Estimated Study Time
- Estimated Practice Time
- Created Version

---

# 2. Learning Context

Purpose

Help learners understand where this topic fits.

Fields

- Overview
- Why Learn This?
- Real World Importance
- Industry Relevance
- Interview Importance
- Typical Experience Level
- Companies That Frequently Ask This Topic

---

# 3. Learning Objectives

Purpose

Define measurable outcomes.

Example

After completing this topic the learner should be able to:

- Explain the concept
- Solve related interview questions
- Apply it in production
- Identify trade-offs
- Debug common issues

---

# 4. Prerequisites

Purpose

Prevent learners from studying advanced topics prematurely.

Fields

Mandatory Prerequisites

Recommended Prerequisites

Cross-Subject Dependencies

Example

HashMap

requires

Arrays

↓

Objects

↓

Hash Functions

---

# 5. Unlocks

Purpose

Describe which topics become available after mastering this topic.

Example

Arrays

↓

Sliding Window

↓

Prefix Sum

↓

Binary Search

↓

Kadane Algorithm

---

# 6. Core Concepts

Purpose

Define the theoretical content.

Every topic should answer:

- What?
- Why?
- How?
- When?
- Where?
- Trade-offs?

---

# 7. Internal Working

Purpose

Explain implementation details.

Examples

HashMap

↓

Buckets

↓

Hash Function

↓

Collision Handling

↓

Rehashing

↓

Load Factor

Every topic should expose implementation details appropriate for its level.

---

# 8. Visual Mental Model

Purpose

Help learners build intuition.

Examples

- Diagrams
- Flowcharts
- Execution Flow
- Memory Layout
- Object Relationships

---

# 9. Real World Analogy

Purpose

Improve conceptual understanding.

Every topic should contain at least one intuitive analogy where appropriate.

---

# 10. Code Examples

Purpose

Show practical implementation.

Requirements

- Beginner Example
- Production Example
- Optimized Example

Languages

Initially

- Java

Future

- Python
- C++
- JavaScript
- Go

---

# 11. Dry Run

Purpose

Walk through execution step by step.

Include

Input

↓

Execution

↓

Output

↓

State Changes

---

# 12. Complexity Analysis

Purpose

Teach algorithmic efficiency.

Include

Time Complexity

Space Complexity

Best Case

Average Case

Worst Case

---

# 13. Memory Behaviour

Purpose

Explain memory implications.

Include where applicable

- Stack
- Heap
- Object Allocation
- References
- Garbage Collection
- Cache Locality

---

# 14. Performance Considerations

Purpose

Explain optimization.

Examples

When to use

When not to use

Trade-offs

Bottlenecks

Scalability

---

# 15. Production Usage

Purpose

Bridge interview learning with software engineering.

Examples

HashMap

↓

Caching

↓

Database Indexing

↓

Authentication

↓

Configuration Storage

↓

Routing Tables

---

# 16. Best Practices

Purpose

Teach production-quality engineering.

Examples

Naming

Maintainability

Readability

Defensive Coding

Thread Safety

Resource Management

---

# 17. Common Mistakes

Purpose

Help learners avoid frequent errors.

Examples

- Forgetting equals/hashCode
- Null handling
- Incorrect complexity assumptions
- Memory leaks
- Off-by-one errors

---

# 18. Debugging Guide

Purpose

Teach diagnosis.

Include

Symptoms

Root Causes

Debugging Strategy

Common Logs

Common Stack Traces

---

# 19. Interview Preparation

Purpose

Connect the topic with interviews.

Include

Frequently Asked Questions

Follow-up Questions

Expected Depth

Whiteboard Questions

Coding Questions

System Design Relevance

Behavioral Relevance (if applicable)

---

# 20. Company Mapping

Purpose

Prioritize topics.

Examples

Google

★★★★★

Microsoft

★★★★☆

Amazon

★★★★★

Uber

★★★★★

Oracle

★★★☆☆

Atlassian

★★★★★

This data is consumed by the Adaptive Engine.

---

# 21. Practice Roadmap

Purpose

Recommend progression.

Example

Easy

↓

Medium

↓

Hard

↓

Company Tagged

↓

Contest Problems

---

# 22. Mini Projects

Purpose

Connect concepts with implementation.

Examples

HashMap

↓

LRU Cache

↓

URL Shortener

↓

Caching Layer

↓

Configuration Service

---

# 23. Revision Strategy

Purpose

Enable long-term retention.

Fields

Revision Priority

Revision Frequency

Flash Cards

Cheat Sheet

One Minute Revision

Spaced Repetition

---

# 24. AI Mentor Guidance

Purpose

Support AI explanations.

Fields

Common Confusions

Recommended Analogies

Recommended Visualizations

Common Misconceptions

Suggested Learning Path

---

# 25. Assessment

Purpose

Evaluate mastery.

Examples

MCQs

Coding Exercises

Scenario Questions

Debugging Tasks

Conceptual Questions

---

# 26. Completion Criteria

A learner completes this topic only if they can:

- Explain it
- Implement it
- Debug it
- Optimize it
- Apply it in production
- Solve interview questions
- Teach it to another learner

---

# 27. Knowledge Graph Metadata

Every topic should expose:

- Parent Node
- Child Nodes
- Sibling Nodes
- Related Topics
- Cross Subject Links
- Difficulty Weight
- Interview Weight
- Company Weight
- Revision Weight
- Confidence Weight
- Mastery Weight

These values power:

- Mission Planner
- AI Mentor
- Career Intelligence
- Dashboard
- Analytics

---

# Topic Lifecycle

Every topic follows the same learner journey.

Locked

↓

Unlocked

↓

Learning

↓

Practicing

↓

In Progress

↓

Completed

↓

Mastered

↓

Revision Due

↓

Interview Ready

↓

Production Ready

---

# Quality Checklist

Every topic must satisfy:

✓ Has prerequisites

✓ Has unlocks

✓ Has learning objectives

✓ Has production relevance

✓ Has interview relevance

✓ Has practice roadmap

✓ Has revision strategy

✓ Has company mapping

✓ Has completion criteria

✓ Fits the knowledge graph

---

# Future Extensions

The schema is intentionally extensible.

Future versions may include:

- AI-generated explanations
- Interactive visualizations
- Coding playgrounds
- Video references
- Community discussions
- Learning analytics
- Personalized recommendations
- Adaptive assessments
- Voice explanations
- AR/VR simulations

without changing the core structure.

---

# Final Principle

Every topic in PrepOS should answer one question:

"After learning this topic, what new engineering capability has the learner gained?"

If the answer is unclear,

the topic should be redesigned.

The objective of PrepOS is not to help learners memorize concepts.

The objective is to transform learners into excellent software engineers through a structured, explainable, adaptive and production-oriented knowledge graph.