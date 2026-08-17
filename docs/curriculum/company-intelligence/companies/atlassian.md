# Atlassian — Company Intelligence

> **PrepOS Company Intelligence Profile**
>
> **Profile Status:** Evidence-limited / Production Schema Candidate  
> **Research Basis:** Internal Atlassian interview knowledge, normalized into schema format  
> **Research Mode:** Source-normalized synthesis; no additional live research performed  
> **Audience:** PrepOS Adaptive Learning Engine, Knowledge Graph, Mission Planner, AI Mentor, and learners targeting Atlassian Software Engineering roles  
> **Important:** This document is a company-intelligence knowledge artifact, not an assertion of universal Atlassian hiring policy. Role-specific recruiter communication, job descriptions, and interview invitations supersede this profile.

---

# 1. Metadata

| Field | Value |
|---|---|
| Company Name | Atlassian |
| Company Category | SaaS; Collaboration Software; Developer Tools |
| Headquarters | Sydney, Australia |
| Engineering Scale | Large global engineering organization |
| Primary Engineering Domains | Collaboration, Project Management, Developer Tools, Cloud, SaaS |
| Target Role Family | Software Engineering |
| Covered Levels | New Graduate / Software Engineer, Senior Software Engineer, Principal Engineer |
| Regional Scope | Global, with regional variance explicitly preserved |
| Last Reviewed | 2026-08-14 |
| Research Version | 1.0 |
| Schema Version | 2.1 |
| Profile Version | 1.0 |
| Overall Confidence | Medium |
| Evidence Limitation | Internal knowledge only; no source URLs retained |
| Machine-Readable Status | Structured Markdown |
| Primary Use | Company-aware adaptive interview preparation |

---

# 2. Company Overview

## 2.1 Company Profile

Atlassian is a global software company known for collaboration and developer tools such as Jira, Confluence, Trello, and Bitbucket. Engineering organizations span cloud infrastructure, SaaS platforms, collaboration, project management, developer productivity, and enterprise services.

For PrepOS, Atlassian should be modeled as a **values-driven engineering organization** where technical problem solving, coding, system design, and explicit values alignment are all critical. Atlassian is known for its distinct values interview, which is a formal part of hiring.

## 2.2 Company Categories

```yaml
company_categories:
  - SaaS
  - Collaboration Software
  - Developer Tools
```

## 2.3 Engineering Characteristics

| Characteristic | PrepOS Interpretation | Confidence |
|---|---|---|
| SaaS platform engineering | Strong relevance | Medium |
| Distributed cloud systems | Strong relevance, especially senior roles | Medium |
| Algorithmic problem solving | Core interview preparation area | Medium |
| Software engineering fundamentals | Important foundation | Medium |
| System design | Increasing importance with seniority | Medium |
| Values alignment | Critical, formalized in values interview | Medium-High |
| Customer focus | Strong cultural signal | High |
| Team collaboration | Strong cultural signal | High |
| AI-assisted engineering | Emerging / pilot-dependent | Low |

---

# 3. Engineering Philosophy

## 3.1 Engineering Philosophy Summary

Atlassian engineering philosophy emphasizes:

1. Customer obsession
2. Openness and transparency
3. Team collaboration
4. Pragmatic problem solving
5. Technical excellence
6. Scalable SaaS engineering
7. End-to-end ownership

The exact formal internal terminology should not be treated as permanently fixed.

## 3.2 Engineering Progression

```text
Problem Solving
      ↓
Strong Fundamentals
      ↓
Algorithmic Execution
      ↓
Engineering Judgment
      ↓
Scalable Thinking
      ↓
Technical Ownership
      ↓
Cross-Team Influence
```

## 3.3 Core Engineering Principle

PrepOS should interpret Atlassian preparation as:

> Solve the right problem, explain the reasoning, implement correctly, understand trade-offs, and demonstrate alignment with Atlassian values and customer focus.

**Confidence:** Medium

**Evidence Type:** Internal company knowledge + candidate pattern synthesis

---

# 4. Hiring Philosophy

## 4.1 Hiring Philosophy

Atlassian SWE evaluation is holistic and values-driven. A candidate should not be modeled as interview-ready merely because they can solve algorithmic problems.

PrepOS should evaluate readiness across:

- Problem solving
- Coding
- System design
- Communication
- Collaboration
- Ownership
- Customer focus
- Values alignment
- Learning ability

## 4.2 Hiring Progression

```text
Foundational Competence
        ↓
Technical Execution
        ↓
Independent Engineering
        ↓
Architectural Ownership
        ↓
Technical Leadership
        ↓
Organizational Influence
```

## 4.3 Hiring Philosophy Constraints

PrepOS MUST NOT assume:

- A fixed interview count
- A universal online assessment
- A universal coding platform
- A universal interview format
- A universal system design round for all levels
- A universal values interview format
- A universal team matching process
- A universal AI-assisted interview

These are treated as role-, level-, team-, region-, or cycle-dependent unless stronger evidence becomes available.

**Confidence:** Medium

---

# 5. Interview Pipeline

## 5.1 Pipeline Model

```text
Application / Referral
        ↓
Recruiter / Initial Alignment
        ↓
Potential Online Assessment
        ↓
Technical Screen
        ↓
Interview Loop
        ↓
Values Interview
        ↓
Interview Feedback
        ↓
Hiring Decision
        ↓
Offer
```

Actual sequence may vary by team and role.

## 5.2 Pipeline Stages

| Stage | Purpose | Duration | Evaluation Criteria | Difficulty | Confidence | Evidence Source |
|---|---|---|---|---|---|---|
| Application / Referral | Establish candidate eligibility | Varies | Resume, experience, role fit | Medium | Medium | Internal knowledge |
| Recruiter Screen | Validate role, experience, process | 20–30 min | Fit, communication, motivation | Low–Medium | Medium | Internal knowledge |
| Potential Online Assessment | Pre-screen coding | Varies | Coding, DSA | Medium–High | Medium | Interview Reports |
| Technical Screen | Validate baseline coding | 45–60 min | Coding, reasoning, communication | High | Medium | Interview Reports |
| Interview Loop | Holistic technical evaluation | Varies, often 2–4 technical interviews | Coding, design, technical depth | Very High | Medium | Interview Reports |
| Values Interview | Evaluate alignment with Atlassian values | Reported as formal behavioral interview | Behavioral consistency, values alignment | High | Medium-High | Interview Reports / Official Culture |
| Feedback / Decision | Aggregate interview evaluations | Varies | Holistic evidence | Very High | Medium | Reported Process |
| Offer | Complete hiring process | Varies | Level, role, headcount | Varies | Low | Reported Process |

---

## 5.3 Atlassian Values Interview

### Status

**Reported / Strongly Indicated as Formal Component**

Atlassian is known for a distinct **Values Interview**, which evaluates candidates against the company's stated values.

The values commonly referenced are:

- Open company, no bullshit
- Play as a team
- Don't #@!% the customer
- Build with heart and balance
- Be the change you seek

### PrepOS Rule

Treat the values interview as a high-priority behavioral preparation area. It is not identical to generic behavioral interviews; candidates should prepare examples that demonstrate Atlassian values explicitly.

```yaml
values_interview:
  status: Strongly Reported
  universal_requirement: Likely for most SWE roles
  coding_test: No
  confidence: Medium-High
  planner_behavior: High priority behavioral prep
```

---

# 6. Evaluation Signals

| Signal | Importance | Description | Typical Interview Stage | Confidence |
|---|---|---|---|---|
| Problem Solving | Critical | Structured decomposition, algorithms, reasoning | Technical Screen, Coding | Medium |
| Coding Ability | Critical | Correct, readable, efficient implementation | Coding | Medium |
| System Design | High for Senior+ | Architecture, scale, reliability, trade-offs | Design | Medium |
| Low-Level Design | Medium | OOP, modularity, extensibility | Coding/Design | Medium |
| Technical Depth | High | Systems, technologies, engineering choices | Technical/Design | Medium |
| Communication | Critical | Clear reasoning and concise technical explanation | All stages | Medium |
| Collaboration | High | Working effectively across teams | Behavioral / Values | High |
| Ownership | High | End-to-end responsibility | Behavioral / Values | Medium |
| Customer Focus | Critical | Don't #@!% the customer value | Values Interview / Behavioral | High |
| Values Alignment | Critical | Alignment with Atlassian values | Values Interview | High |
| Learning Ability | High | Adaptation, reflection, updating assumptions | Behavioral / Values | Medium |
| Leadership | High for Senior+ | Influence, ownership, technical leadership | Behavioral / Design | Medium |

---

# 7. Subject Importance

| Subject | Importance | Interview Stage | Experience Level | Reason | Confidence |
|---|---|---|---|---|---|
| Programming Fundamentals | High | Coding | All | Foundation for implementation | Medium |
| Java | Medium | Coding | Role/candidate dependent | Atlassian historically Java-heavy for backend | Medium |
| Data Structures & Algorithms | Critical | Technical Screen / Coding | All | Central technical signal | Medium |
| Database Management Systems | Medium | Design/Technical | Mid+ | Data modeling and system reasoning | Medium |
| Operating Systems | Medium | Technical/Design | Contextual | Systems relevance | Low-Medium |
| Computer Networks | Medium | Design/Technical | Contextual | Distributed systems and networking | Medium |
| Low-Level Design | Medium | Coding/Design | Mid+ | Role-dependent design | Medium |
| High-Level Design | High | Design | Senior+ | Increasingly important with seniority | Medium |

---

# 8. Module Importance

## 8.1 Programming Fundamentals

| Module | Importance | Reason | Confidence | Typical Interview Stage |
|---|---|---|---|---|
| Variables and Data Types | Medium | Basic implementation fluency | Medium | Coding |
| Functions | High | Core decomposition | Medium | Coding |
| Object-Oriented Programming | High | Practical engineering, Java-heavy backend | Medium | Technical/Design |
| SOLID Principles | Medium | Design quality | Medium | Design |
| Exception Handling | Medium | Production-quality code | Medium | Coding/Design |
| Memory Concepts | Medium | Systems reasoning | Low-Medium | Technical |

### Topics

| Topic | Importance | Frequency | Difficulty | Confidence | Notes |
|---|---|---|---|---|---|
| Functions | High | Common | Easy–Medium | Medium | Expected fluency |
| OOP | High | Common | Medium | Medium | More relevant for Java/backend |
| SOLID | Medium | Contextual | Medium | Medium | Avoid over-weighting |
| Error Handling | Medium | Contextual | Medium | Medium | Production signal |

---

## 8.2 Java

| Module | Importance | Reason | Confidence | Typical Interview Stage |
|---|---|---|---|---|
| Collections | Medium-High | Java-heavy backend | Medium | Coding |
| Streams | Medium | Modern Java fluency | Low-Medium | Coding |
| Concurrency | Medium | Systems engineering | Medium | Technical/Design |
| Multithreading | Medium | Concurrency-heavy roles | Medium | Technical |
| JVM | Low-Medium | Role-dependent depth | Low | Technical |
| Generics | Medium | Language fluency | Low-Medium | Coding |

### Topics

| Topic | Importance | Frequency | Difficulty | Confidence | Notes |
|---|---|---|---|---|---|
| Collections | Medium-High | Common | Medium | Medium | Useful for Java roles |
| Concurrency | Medium | Contextual | High | Medium | Increase for backend systems |
| JVM | Low | Contextual | High | Low | Do not over-prioritize |

---

# 9. Data Structures & Algorithms

## 9.1 DSA Module Matrix

| Module | Importance | Reason | Confidence | Typical Interview Stage |
|---|---|---|---|---|
| Arrays | Critical | High-value problem-solving | Medium | Coding |
| Strings | Critical | Frequent algorithmic domain | Medium | Coding |
| Hashing | Critical | Efficient lookup/state tracking | Medium | Coding |
| Linked Lists | High | Foundational data structure | Medium | Coding |
| Trees | Critical | Traversal and recursion | Medium | Coding |
| Graphs | Critical | BFS/DFS/state modeling | Medium | Coding |
| Dynamic Programming | High | Advanced reasoning | Medium | Coding |
| Greedy | High | Optimization reasoning | Medium | Coding |
| Backtracking | High | Search-space reasoning | Medium | Coding |
| Tries | Medium | Specialized string problems | Low-Medium | Coding |
| Heaps / Priority Queues | High | Ordering and scheduling | Medium | Coding |
| Queues / Stacks | High | Traversal and state management | Medium | Coding |

## 9.2 DSA Topic Metadata

| Topic | Importance | Frequency | Difficulty | Confidence | Notes |
|---|---|---|---|---|---|
| Arrays | Critical | High | Medium | Medium | Core preparation |
| Strings | Critical | High | Medium | Medium | Core preparation |
| Hash Maps / Hash Sets | Critical | High | Medium | Medium | Core optimization |
| Linked Lists | High | Medium | Medium | Medium | Fundamental |
| Binary Trees | Critical | High | Medium-High | Medium | Traversal, recursion |
| Graph Traversal | Critical | High | High | Medium | BFS/DFS |
| Dynamic Programming | High | Medium | High | Medium | Pattern recognition |
| Greedy | High | Medium | Medium-High | Medium | Optimization |
| Backtracking | High | Medium | High | Medium | Search |
| Heaps | High | Medium | Medium-High | Medium | Top-K |
| Tries | Medium | Low-Medium | High | Low-Medium | Specialized |
| Complexity Analysis | Critical | High | Medium | Medium | Must verbalize |

---

# 10. Database Management Systems

| Module | Importance | Reason | Confidence | Typical Interview Stage |
|---|---|---|---|---|
| SQL | Medium | Data access fundamentals | Medium | Technical/Design |
| Transactions | Medium | Correctness in distributed/data systems | Medium | Design |
| Indexing | Medium | Performance reasoning | Medium | Design |
| Normalization | Low-Medium | Data modeling | Low | Technical |
| Query Optimization | Medium | Production database reasoning | Low-Medium | Design |

### Topics

| Topic | Importance | Frequency | Difficulty | Confidence | Notes |
|---|---|---|---|---|---|
| SQL | Medium | Contextual | Medium | Medium | Increase for data roles |
| Transactions | Medium | Contextual | Medium-High | Medium | System design |
| Indexing | Medium | Contextual | Medium | Medium | Performance |
| Query Optimization | Medium | Contextual | High | Low-Medium | Role dependent |

---

# 11. Operating Systems

| Module | Importance | Reason | Confidence | Typical Interview Stage |
|---|---|---|---|---|
| Processes | Medium | Systems foundation | Low | Technical |
| Threads | Medium | Concurrency reasoning | Medium | Technical/Design |
| Deadlocks | Medium | Concurrency and reliability | Medium | Technical |
| Scheduling | Low-Medium | Systems fundamentals | Low | Technical |
| Virtual Memory | Low-Medium | Systems depth | Low | Technical |

### Topics

| Topic | Importance | Frequency | Difficulty | Confidence | Notes |
|---|---|---|---|---|---|
| Processes | Medium | Contextual | Medium | Low | Not universal |
| Threads | Medium | Contextual | Medium-High | Medium | Systems roles |
| Deadlocks | Medium | Contextual | Medium-High | Medium | Concurrency |
| Scheduling | Low | Contextual | Medium | Low | Do not over-prioritize |
| Virtual Memory | Low | Contextual | High | Low | Role dependent |

---

# 12. Computer Networks

| Module | Importance | Reason | Confidence | Typical Interview Stage |
|---|---|---|---|---|
| HTTP / HTTPS | Medium | Web architecture | Medium | Design |
| TCP/IP | Medium | Distributed communication | Medium | Design |
| DNS | Medium | Service discovery | Medium | Design |
| Load Balancing | High | Scalability and availability | Medium | System Design |

### Topics

| Topic | Importance | Frequency | Difficulty | Confidence | Notes |
|---|---|---|---|---|---|
| HTTP | Medium | Common in design | Medium | Medium | Architecture primitive |
| HTTPS | Medium | Security | Medium | Medium | Contextual |
| TCP/IP | Medium | Networking | Medium | Medium | Distributed systems |
| DNS | Medium | Service discovery | Medium | Medium | Common design component |
| Load Balancing | High | Scalability | Medium | Medium | Senior design |

---

# 13. Low-Level Design

## 13.1 Importance

**Overall Importance:** Medium

**Senior-Level Importance:** Medium-High

**Confidence:** Medium

Atlassian may evaluate OOD/LLD through role-specific design discussions or embedded coding questions. Not universal for all SWE loops.

## 13.2 Expected Capabilities

- Interface design
- Class responsibility
- Encapsulation
- Modularity
- Extensibility
- Dependency management
- Testability
- Error handling
- Maintainability
- Practical trade-offs

## 13.3 Typical Question Families

PrepOS may use generic design families such as:

- Object modeling
- Component modeling
- Extensible APIs
- State management
- Concurrency-aware components
- Service abstractions

## 13.4 Experience Applicability

| Level | Applicability |
|---|---|
| New Graduate | Low |
| Software Engineer | Medium / Role-dependent |
| Senior | High |
| Principal | High, but broader architecture dominates |

---

# 14. High-Level Design

## 14.1 Importance

**Overall Importance:** High for senior engineering

**Confidence:** Medium

System design importance increases substantially with seniority.

## 14.2 Expected Capabilities

Candidates should be able to:

1. Clarify requirements
2. Identify scale
3. Define APIs/interfaces
4. Select storage models
5. Design service boundaries
6. Reason about consistency
7. Reason about availability
8. Handle failure modes
9. Identify bottlenecks
10. Discuss caching
11. Discuss queues and asynchronous processing
12. Discuss observability
13. Explain operational trade-offs
14. Avoid unnecessary over-engineering

## 14.3 Distributed Concepts

| Concept | Importance | Confidence |
|---|---|---|
| Horizontal scaling | Very High | Medium |
| Load balancing | High | Medium |
| Caching | High | Medium |
| Database scaling | High | Medium |
| Replication | High | Medium |
| Partitioning / Sharding | High | Medium |
| Consistency | High | Medium |
| Availability | High | Medium |
| Fault tolerance | Very High | Medium |
| Queues / Async processing | High | Medium |
| Rate limiting | High | Medium |
| Observability | High | Medium |
| Disaster recovery | Medium-High | Medium |

## 14.4 Typical Systems

Preparation categories, not claims about official Atlassian questions:

- Collaboration platforms
- Project management tools
- Notification systems
- Search systems
- File/document systems
- Distributed storage
- Event-processing platforms
- High-throughput APIs
- Data pipelines
- User permission/access systems

## 14.5 Experience Applicability

| Level | HLD Importance |
|---|---|
| New Graduate | Low |
| Software Engineer | Low-Medium / Role-dependent |
| Senior | Very High |
| Principal | Critical |

---

# 15. Coding Expectations

## 15.1 Coding Difficulty

| Level | Expected Difficulty |
|---|---|
| New Graduate | Medium → Medium-High |
| Software Engineer | Medium-High |
| Senior | High with engineering context |
| Principal | High, but coding is one component |

**Confidence:** Medium

## 15.2 Coding Style

Candidates should demonstrate:

- Correctness
- Readability
- Appropriate abstractions
- Efficient data structures
- Clear variable naming
- Complexity awareness
- Edge-case handling
- Testability
- Incremental refinement

## 15.3 Platforms

No universal coding platform is confirmed. Candidate should confirm actual environment from interview invitation.

```yaml
platform:
  universal_platform: false
  exact_platform: invitation_dependent
  confidence: low
```

## 15.4 Language Preferences

No single programming language is universally required. Atlassian is historically Java-heavy for backend roles, but candidates may use other languages for general interviews.

```yaml
language_policy:
  preferred_language: candidate_fluent_language
  java_heavy_backend: true
  language_trivia: low_priority
  framework_trivia: low_priority
  confidence: medium
```

## 15.5 Time Constraints

Reported approximately 45–60 minute technical interviews.

**Reported Pattern — Medium Confidence**

## 15.6 Problem Distribution

Qualitative preparation priority:

```text
Arrays / Strings
      ↓
Hashing
      ↓
Trees / Graphs
      ↓
BFS / DFS
      ↓
Heaps / Queues
      ↓
Dynamic Programming
      ↓
Greedy / Backtracking
      ↓
Specialized Structures
```

## 15.7 Optimization Expectations

Candidates should:

1. Establish a correct baseline solution
2. Analyze time complexity
3. Analyze space complexity
4. Identify bottlenecks
5. Improve the algorithm where justified
6. Explain why the optimized solution is better
7. Validate edge cases

---

# 16. Behavioral Expectations

## 16.1 Values Alignment

**Importance:** Critical

Candidates must demonstrate alignment with Atlassian values, especially:

- Open company, no bullshit
- Play as a team
- Don't #@!% the customer
- Build with heart and balance
- Be the change you seek

**Confidence:** Medium-High

## 16.2 Communication

**Importance:** Critical

Candidates should:

- Clarify requirements
- State assumptions
- Explain reasoning
- Communicate trade-offs
- Ask relevant questions
- Respond constructively to feedback

## 16.3 Collaboration

**Importance:** High

Examples should demonstrate:

- Working across teams
- Resolving disagreement
- Sharing knowledge
- Supporting peers
- Handling stakeholder conflict

## 16.4 Ownership

**Importance:** High

Candidates should demonstrate:

- Responsibility for outcomes
- Proactive problem identification
- Follow-through
- Operational awareness
- Willingness to address problems beyond narrow task boundaries

## 16.5 Customer Focus

**Importance:** Critical

Strong evidence includes:

- Understanding user impact
- Business context
- Stakeholder awareness
- Delivering value
- Making decisions that benefit the customer

## 16.6 Learning Mindset

**Importance:** High

Strong evidence includes:

- Learning from failures
- Changing a decision when evidence changes
- Seeking feedback
- Improving engineering processes
- Demonstrating intellectual humility

## 16.7 Behavioral Preparation Format

STAR is recommended as a preparation framework:

```text
Situation
   ↓
Task
   ↓
Action
   ↓
Result
   ↓
Lesson / What Changed
```

STAR is a preparation technique, not asserted here as a mandatory Atlassian interview format.

---

# 17. Role Differences

| Level | Coding | Design | Leadership | Values | Expected Autonomy | Confidence |
|---|---|---|---|---|---|---|
| New Graduate | Critical | Low | Low | High | Scoped tasks | Medium |
| Software Engineer | Critical | Medium | Medium | High | Independent execution | Medium |
| Senior | Very High | Very High | High | High | Broad technical ownership | Medium |
| Principal | High | Critical | Critical | High | Cross-team influence | Medium |

---

# 18. Recent Trends

| Trend | Classification | Confidence |
|---|---|---|
| Virtual interviews became standard | Confirmed | Medium-High |
| Some return to in-person loops | Reported | Low-Medium |
| Online assessments for new grad/intern | Strongly Reported | Medium |
| AI-assisted coding in interviews | Insufficient Evidence | Low |
| AI cheating prevention | Insufficient Evidence | Low |
| System design round changes | Insufficient Evidence | Low |

---

# 19. Negative Evidence

Do NOT treat the following as core Atlassian SWE preparation requirements unless role-specific evidence exists:

- Universal LLD for all roles
- Universal HLD for all levels
- Universal OS/DBMS/Networking depth
- One universal interview template
- Universal coding platform
- Universal AI interview
- Universal team matching

---

# 20. Contradiction Register

| Topic | Conflicting Claims | Resolution | Confidence | Requires Verification |
|---|---|---|---|---|
| Values Interview | Some sources report it as mandatory, others embedded | Treat as high priority but confirm actual invitation | Medium | true |
| Online Assessment | Platform varies by region/role | Confirm actual invitation | Medium | true |
| LLD requirement | Some loops embed OOD, others have dedicated design | Treat as role/team dependent | Medium | true |
| System design at mid-level | Some mid-level backend roles report HLD, others do not | Treat as role-dependent | Medium | true |

---

# 21. Preparation Strategy

## 21.1 Core Preparation Sequence

```text
Phase 1: Programming Fundamentals
        ↓
Phase 2: DSA Foundations
        ↓
Phase 3: Advanced DSA
        ↓
Phase 4: Timed Coding + Communication
        ↓
Phase 5: Low-Level Design
        ↓
Phase 6: High-Level System Design
        ↓
Phase 7: Values / Behavioral Preparation
        ↓
Phase 8: Mock Interview Loop
```

## 21.2 Preparation Priorities

### Priority 1 — DSA

Focus on:

- Arrays
- Strings
- Hashing
- Trees
- Graphs
- BFS
- DFS
- Heaps
- Queues
- Recursion
- Dynamic Programming
- Greedy
- Backtracking
- Complexity analysis

### Priority 2 — Coding Execution

Practice:

- Clarifying requirements
- Selecting an approach
- Writing clean code
- Testing
- Debugging
- Complexity analysis
- Optimization

### Priority 3 — System Design

Increase preparation according to seniority.

### Priority 4 — Values / Behavioral

Develop evidence-backed stories that demonstrate Atlassian values explicitly.

### Priority 5 — Core CS

Use role-specific evidence to determine whether OS, DBMS, networking or other fundamentals should receive additional weighting.

---

# 22. Planner Intelligence

## 22.1 Planning Philosophy

### Primary Interview Philosophy

```text
Problem Solving First
        ↓
Strong Fundamentals
        ↓
Algorithmic Execution
        ↓
Scalable Thinking
        ↓
Engineering Judgment
        ↓
Technical Leadership
        ↓
Values Alignment
```

## 22.2 Knowledge Progression Philosophy

```text
Fundamentals
    ↓
Patterns
    ↓
Independent Problem Solving
    ↓
Timed Execution
    ↓
Complex Problem Solving
    ↓
Design
    ↓
Engineering Judgment
    ↓
Values Integration
```

## 22.3 Interview Readiness Philosophy

Readiness should be measured by the learner's ability to:

- Solve unfamiliar problems
- Explain reasoning
- Write correct code
- Analyze complexity
- Handle edge cases
- Design systems appropriate to level
- Explain trade-offs
- Demonstrate behavioral evidence and values alignment

## 22.4 Learning Progression Philosophy

Do not increase difficulty solely because the company is high-bar.

Difficulty should increase when:

- Prerequisites are satisfied
- Mastery is sufficient
- Revision debt is controlled
- Accuracy is stable
- Learner can explain solutions
- Interview timeline requires acceleration

---

# 23. Planning Priority Hierarchy

Default Atlassian hierarchy:

```text
Data Structures & Algorithms
        ↓
Programming / Coding Execution
        ↓
Values / Behavioral
        ↓
System Design
        ↓
Low-Level Design
        ↓
Core CS
        ↓
Role-Specific Knowledge
```

For senior roles:

```text
DSA + Coding
        ↓
System Design
        ↓
Engineering Judgment
        ↓
Values / Leadership
        ↓
Core CS / Specialized Knowledge
```

This hierarchy is guidance only. The Adaptive Learning Engine MUST combine it with learner-specific signals.

---

# 24. Adaptive Biases

## 24.1 Coding Bias

**Default:** High

**Becomes Stronger When:**
- Coding accuracy low
- DSA mastery weak
- Interview date approaching
- Timed performance poor
- Complexity reasoning weak

**Becomes Weaker When:**
- Coding mastery consistently high
- Mock coding performance stable
- Strong communication and optimization demonstrated

## 24.2 Revision Bias

**Default:** Medium

**Becomes Stronger When:**
- Previously mastered topics decay
- Error recurrence increases
- Revision debt grows

**Becomes Weaker When:**
- Retention stable
- Error recurrence decreases

## 24.3 System Design Bias

**Default:** Low for New Graduate; High for Senior+; Critical for Principal

**Becomes Stronger When:**
- Target level increases
- Design mastery weak
- Interview date approaches
- Role emphasizes distributed systems

**Becomes Weaker When:**
- Target role does not require significant design depth
- Learner has demonstrated strong design readiness

## 24.4 Values / Behavioral Bias

**Default:** High

**Becomes Stronger When:**
- Values preparation incomplete
- Learner lacks values-specific stories
- Leadership scope increases
- Interview timeline approaches

**Becomes Weaker When:**
- Values story bank complete
- Mock values interview performance stable

## 24.5 Core CS Bias

**Default:** Medium

**Becomes Stronger When:**
- Target role infrastructure/systems-oriented
- Job description emphasizes OS/DBMS/networking
- Role-specific interview evidence supports it

**Becomes Weaker When:**
- Generalist coding/design signals dominate
- No role-specific evidence exists

## 24.6 Difficulty Bias

Difficulty should increase only after prerequisite mastery.

```text
Prerequisite Mastery
        +
Accuracy
        +
Retention
        +
Interview Timeline
        ↓
Difficulty Adjustment
```

Do not increase difficulty merely because Atlassian is considered a difficult company.

## 24.7 Timeline Bias

**Early Timeline:** Learning, fundamentals, pattern acquisition, conceptual understanding

**Mid Timeline:** Coding volume, weak-area remediation, timed practice, system design, values story development

**Near Interview:** Mock interviews, revision, error correction, communication, values/behavioral readiness, role-specific calibration

## 24.8 Experience Bias

| Level | Bias |
|---|---|
| New Graduate | DSA, fundamentals, coding fluency, basic values |
| Mid-Level | Independent coding, design awareness, ownership, values demonstration |
| Senior | System design, engineering judgment, technical leadership, values leadership |
| Principal | Architecture, cross-team influence, organizational impact, strategic values |

---

# 25. Mission Composition Guidance

| Mission Component | Default Priority |
|---|---|
| Primary Learning | High |
| Support Reading | Medium |
| Coding Practice | Very High |
| Revision | High |
| Interview Preparation | Medium |
| Behavioral / Values Practice | High |

### Level-Specific Composition

| Level | Coding Practice | System Design | Behavioral/Values | LLD | HLD |
|---|---|---|---|---|---|
| New Graduate | Very High | Low | High | Low | Low |
| Software Engineer | Very High | Medium | High | Medium | Low-Medium |
| Senior | High | Very High | High | High | Very High |
| Principal | High | Critical | High | High | Critical |

---

# 26. Explainability Rules

Example:

```text
Recommended Mission:
Graph Algorithms — Advanced BFS/DFS

Reason:
- Atlassian DSA relevance is high.
- Learner has completed graph prerequisites.
- Graph mastery is below target.
- Interview timeline is approaching.
- Coding performance indicates traversal-state errors.
```

Another example:

```text
Recommended Mission:
Values Interview Preparation — Customer Focus Stories

Reason:
- Atlassian values interview is high priority.
- Learner lacks specific customer-focused examples.
- Values alignment is a critical signal.
- Interview timeline is approaching.
```

---

# 27. Evidence Model

| Status | Meaning |
|---|---|
| Confirmed | Supported by strong retained evidence |
| Reported | Explicitly described in internal knowledge but source details not retained |
| Pattern | Recurring non-universal pattern |
| Varies | Depends on role, level, team, region or hiring cycle |
| Historical | Former or potentially outdated practice |
| Pilot | Limited experimental or role-specific practice |
| Insufficient Evidence | Not enough evidence for a durable conclusion |
| Not Supported | Available evidence does not support the claim |

---

# 28. Evidence Summary

| Finding | Classification | Confidence | PrepOS Treatment |
|---|---|---|---|
| Coding and algorithmic reasoning are central | Reported | Medium | High planning priority |
| Structured reasoning matters | Reported | Medium | High |
| Values interview is a formal component | Strongly Reported | Medium-High | High behavioral/values priority |
| Customer focus is culturally critical | Reported | High | Values stories emphasis |
| Design importance increases with seniority | Reported Pattern | Medium | Strong level-dependent bias |
| Java is common for backend roles | Reported | Medium | Contextual Java preparation |
| Team-specific hiring variance | Reported | Medium | Do not hardcode one process |
| Universal AI-assisted interview | Not Supported | Low | Do not hardcode |
| Universal coding platform | Not Supported | Low | Confirm invitation |

---

# 29. Research Limitations

- Internal knowledge only; no source URLs retained.
- Atlassian hiring processes may change by role, level, team, geography, hiring cycle.
- Community experiences are patterns, not universal policy.
- Actual interview invitation, recruiter communication, and job description override this profile.

---

# 30. Machine-Readable Summary

```yaml
company:
  name: Atlassian
  categories:
    - SaaS
    - Collaboration Software
    - Developer Tools

profile:
  version: "1.0"
  last_reviewed: "2026-08-14"
  confidence: Medium

interview:
  coding:
    importance: Critical
    confidence: Medium

  problem_solving:
    importance: Critical
    confidence: Medium

  system_design:
    importance: High
    confidence: Medium
    level_dependency: true

  low_level_design:
    importance: Medium
    confidence: Medium
    role_dependency: true

  behavioral:
    importance: High
    confidence: Medium

  values_interview:
    importance: Critical
    confidence: Medium-High
    formal_component: true

  communication:
    importance: Critical
    confidence: Medium

subjects:
  programming_fundamentals: High
  java: Medium
  dsa: Critical
  dbms: Medium
  operating_systems: Medium
  computer_networks: Medium
  low_level_design: Medium
  high_level_design: High

levels:
  new_grad:
    primary_focus:
      - DSA
      - Coding
      - Fundamentals
      - Values
    system_design: Low

  software_engineer:
    primary_focus:
      - DSA
      - Coding
      - Ownership
      - Values
    system_design: Medium

  senior:
    primary_focus:
      - System Design
      - Engineering Judgment
      - Leadership
      - Values Leadership
    system_design: Very High

  principal:
    primary_focus:
      - Architecture
      - Technical Leadership
      - Cross-Team Influence
      - Strategic Values
    system_design: Critical

trends:
  ai_assisted_interview:
    status: Insufficient Evidence
    confidence: Low

  regional_variation:
    status: Insufficient Evidence
    confidence: Low

planner:
  philosophy:
    - Problem Solving First
    - Strong Fundamentals
    - Algorithmic Execution
    - Engineering Judgment
    - Scalable Thinking
    - Technical Leadership
    - Values Alignment

  priority:
    - DSA
    - Programming
    - Values/Behavioral
    - System Design
    - Core CS
    - Role-Specific

  adaptive:
    learner_readiness_overrides_company_priority: true
    difficulty_requires_prerequisite_mastery: true
    timeline_sensitive: true
    experience_sensitive: true
```

---

# 31. Planner Safety Constraints

The Adaptive Learning Engine MUST NOT:

- Treat company priorities as absolute learner requirements.
- Assign advanced system design to a new-grad learner without prerequisites.
- Treat community reports as official Atlassian policy.
- Hardcode interview round counts.
- Hardcode interview platform behavior.
- Use unsupported numerical topic probabilities.
- Treat a single interview experience as universal.
- Generate preparation missions solely from company metadata.
- Ignore the values interview when personalizing Atlassian preparation.

---

# 32. Company Intelligence Decision Model

```text
                    Atlassian Company Profile
                            │
                            │
                            ▼
                 Company Priority Signals
                            │
                            ▼
                 Target Role / Level
                            │
                            ▼
                  Learner Mastery Model
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
         Weak Areas     Revision Debt   Timeline
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                  Adaptive Learning Brain
                            │
                            ▼
                     Strategy Engine
                            │
                            ▼
                     Mission Planner
                            │
                            ▼
                      Final Mission
```

Company intelligence provides **context**.

Learner intelligence provides **state**.

The Adaptive Learning Brain determines **action**.

---

# 33. Maintenance Triggers

Atlassian intelligence should be re-evaluated when:

- Official Atlassian candidate guidance changes
- Recruiter process instructions change
- Interview invitation contradicts the profile
- A verified current interview format is introduced
- Values interview format changes
- Level expectations materially change
- Regional process differences become verified
- Strong primary evidence establishes a previously uncertain claim
- Existing community consensus materially changes

---

# 34. Version History

| Version | Date | Major Changes |
|---|---|---|
| 1.0 | 2026-08-14 | Initial evidence-limited Atlassian interview intelligence in Google-reference schema |

---

# 35. Final Canonical Summary

Atlassian should be modeled by PrepOS as a **values-driven, high-bar software engineering company centered on problem solving and coding, with a formal values interview, and increasingly strong system-design, engineering-judgment, leadership, and organizational-influence expectations as seniority increases**.

The default planning hierarchy is:

```text
DSA
 ↓
Programming / Coding
 ↓
Values / Behavioral
 ↓
System Design
 ↓
Core CS
 ↓
Role-Specific Knowledge
```

For senior engineers, the hierarchy evolves toward:

```text
System Design
 ↓
Engineering Judgment
 ↓
Technical Leadership
 ↓
Values Leadership
 ↓
Advanced Coding
```

The profile intentionally separates evidence from inference, official guidance from community patterns, current claims from historical claims, global rules from regional variation, standard process from pilot programs, and company priorities from learner-specific planning.

**Canonical principle:**

> Atlassian company intelligence determines what is relevant.  
> Learner intelligence determines what is needed.  
> The Adaptive Learning Engine determines what should happen next.
