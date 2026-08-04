# PrepOS Curriculum Constitution

**File:** `docs/curriculum/subjects/07-lld.md`

Version: 2.0

Status: Canonical

Owner: PrepOS Architecture Team

Subject Code: LLD-701

Difficulty: Foundation → Expert

Estimated Duration: 8–10 Weeks

Prerequisite Subjects:

- Programming Fundamentals
- Java
- Data Structures & Algorithms
- Database Management Systems
- Operating Systems
- Computer Networks

Unlocks:

- High-Level Design
- Backend Engineering
- Microservices
- Spring Boot Architecture
- Enterprise Application Development
- System Design Interviews
- Software Architecture
- Production Engineering

---

# Low-Level Design (LLD)

---

# Vision

Low-Level Design bridges the gap between programming and software architecture.

It teaches learners how to transform business requirements into maintainable, extensible, testable, and production-ready software components.

The objective of this curriculum is not merely to solve machine coding problems or memorize design patterns, but to develop engineering thinking by understanding object-oriented design, software modeling, design principles, reusable architectures, and production-quality implementations.

---

# Subject Philosophy

PrepOS teaches Low-Level Design as an engineering discipline rather than a collection of design patterns.

Instead of memorizing SOLID principles or Gang of Four patterns in isolation, learners progressively understand:

- How to model real-world systems
- How objects collaborate
- Why abstractions exist
- How to build maintainable software
- When to apply design principles
- Why design patterns solve recurring engineering problems
- How production systems evolve over time

Every advanced design concept is built upon previously mastered object-oriented fundamentals.

---

# Learning Objectives

After completing this curriculum, learners should be able to:

- Model real-world software systems.
- Design extensible object-oriented applications.
- Apply SOLID and GRASP principles effectively.
- Select appropriate design patterns.
- Build reusable software components.
- Refactor poorly designed systems.
- Design production-ready machine coding solutions.
- Explain design trade-offs during interviews.
- Build maintainable enterprise applications.
- Connect LLD concepts with backend engineering and system design.

---

# Subject Progression

The curriculum is organized into twenty progressive modules.

Every learner moves through these modules sequentially unless the Adaptive Learning Engine validates sufficient prior mastery.

```
LEVEL 1
Foundations

↓

LEVEL 2
Core Object-Oriented Design

↓

LEVEL 3
Design Principles

↓

LEVEL 4
Production Software Design

↓

LEVEL 5
Expert Low-Level Design
```

Progression is strictly sequential unless validated by the Adaptive Learning Engine.

---

# Learning Methodology

Every topic inside this curriculum follows the same instructional model.

1. Concept
2. Motivation
3. Internal Working
4. UML Representation
5. Real-world Analogy
6. Design Decisions
7. Trade-off Analysis
8. Production Usage
9. Common Mistakes
10. Interview Perspective
11. Refactoring Perspective
12. Revision Checklist

---

# Curriculum Structure

The curriculum contains five progressive learning levels.

| Level | Objective |
|---------|-----------|
| Foundation | Learn software modeling fundamentals |
| Basic | Master object-oriented programming concepts |
| Intermediate | Apply engineering design principles |
| Advanced | Design production-ready software systems |
| Expert | Build enterprise-grade software architectures |

---

# LEVEL 1 — FOUNDATIONS

## Objective

Develop a strong understanding of object-oriented thinking, software modeling, and object collaboration before learning design principles, patterns, and production architectures.

Learners should understand how software systems are decomposed into objects and how those objects interact to solve business problems.

Recommended Duration

2 Weeks

Expected Outcome

The learner should confidently model simple software systems using classes, objects, and relationships while understanding the purpose of object-oriented design.

---

## Module 1 — Introduction to Software Design

### Purpose

Introduce software design as the process of converting business requirements into structured, maintainable, and reusable software systems.

### Major Areas

- What is Software Design?
- Why Software Design Matters
- Software Development Lifecycle
- Requirements Analysis
- Functional Requirements
- Non-Functional Requirements
- Design vs Implementation
- Software Quality Attributes
- Maintainability
- Scalability (Introduction)
- Extensibility

### Learning Outcomes

- Explain software design.
- Differentiate design from implementation.
- Identify software quality attributes.
- Understand requirement analysis.

### Interview Focus

- What is Low-Level Design?
- Functional vs Non-Functional Requirements
- Maintainability
- Scalability
- Extensibility

### Production Relevance

- Enterprise Applications
- Backend Services
- SaaS Platforms
- Cloud Applications

### Common Mistakes

- Starting implementation without proper design.
- Ignoring non-functional requirements.
- Treating design as documentation only.

### Recommended Practice

- Analyze software requirements.
- Identify quality attributes.
- Compare good and poor software designs.

### Unlocks

- Module 2 — Object-Oriented Thinking

---

## Module 2 — Object-Oriented Thinking

### Purpose

Understand how real-world entities are represented as software objects and how object-oriented thinking simplifies software development.

### Major Areas

- Object-Oriented Paradigm
- Objects
- Classes
- Identity
- State
- Behavior
- Responsibilities
- Collaboration
- Object Lifecycle
- Message Passing
- Real-world Modeling

### Learning Outcomes

- Explain object-oriented thinking.
- Model real-world entities.
- Differentiate objects and classes.
- Understand object collaboration.

### Interview Focus

- Class vs Object
- State vs Behavior
- Identity
- Responsibilities

### Production Relevance

- Enterprise Software
- Domain Modeling
- Backend Systems
- Microservices

### Common Mistakes

- Treating classes as data containers only.
- Mixing responsibilities.
- Ignoring object collaboration.

### Recommended Practice

- Model real-world objects.
- Identify responsibilities.
- Draw simple object interactions.

### Unlocks

- Module 3 — Classes & Objects

---

## Module 3 — Classes & Objects

### Purpose

Master the fundamental building blocks of object-oriented software systems.

### Major Areas

- Class Design
- Object Creation
- Constructors
- Fields
- Methods
- Access Modifiers
- Static Members
- Instance Members
- Object Lifecycle
- Object Memory Model
- Initialization

### Learning Outcomes

- Design robust classes.
- Create reusable objects.
- Understand object lifecycle.
- Differentiate static and instance members.

### Interview Focus

- Constructors
- Static vs Instance
- Object Creation
- Memory Allocation

### Production Relevance

- Backend Services
- Domain Entities
- Business Components
- Enterprise Applications

### Common Mistakes

- Overusing static members.
- Large classes with multiple responsibilities.
- Poor encapsulation.

### Recommended Practice

- Design simple domain classes.
- Implement constructors.
- Compare object lifecycles.

### Unlocks

- Module 4 — Relationships Between Objects

---

## Module 4 — Relationships Between Objects

### Purpose

Understand how objects collaborate through relationships to model complex software systems.

### Major Areas

- Association
- Aggregation
- Composition
- Dependency
- Realization
- Generalization
- Has-A Relationship
- Is-A Relationship
- Coupling
- Cohesion

### Learning Outcomes

- Differentiate object relationships.
- Select appropriate relationships.
- Understand coupling and cohesion.
- Model software collaboration.

### Interview Focus

- Association vs Aggregation
- Aggregation vs Composition
- Coupling
- Cohesion
- Is-A vs Has-A

### Production Relevance

- Domain Modeling
- Enterprise Systems
- Object Collaboration
- Backend Design

### Common Mistakes

- Misusing inheritance.
- Tight coupling.
- Poor object boundaries.

### Recommended Practice

- Draw UML relationship diagrams.
- Compare different object models.
- Analyze design trade-offs.

### Unlocks

- Module 5 — Software Modeling

---

## Module 5 — Software Modeling

### Purpose

Learn how to visualize, communicate, and validate software designs before implementation using standard modeling techniques.

### Major Areas

- Introduction to UML
- Why UML
- Class Diagram
- Object Diagram
- Package Diagram
- Sequence Diagram
- Activity Diagram
- State Diagram
- Use Case Diagram
- Modeling Best Practices
- Design Documentation

### Learning Outcomes

- Interpret UML diagrams.
- Model software components.
- Understand software documentation.
- Communicate designs effectively.

### Interview Focus

- UML Basics
- Class Diagram
- Sequence Diagram
- Use Case Diagram

### Production Relevance

- Architecture Reviews
- Technical Documentation
- Enterprise Design
- Software Communication

### Common Mistakes

- Treating UML as implementation.
- Overcomplicating diagrams.
- Ignoring design documentation.

### Recommended Practice

- Draw UML diagrams.
- Model small applications.
- Review existing software designs.

### Unlocks

- LEVEL 2 — CORE OBJECT-ORIENTED DESIGN

# LEVEL 2 — CORE OBJECT-ORIENTED DESIGN

## Objective

Master the fundamental object-oriented principles that enable developers to design flexible, reusable, maintainable, and extensible software systems.

Learners should understand not only how each OOP concept works individually but also how they collaborate to produce clean and production-quality software.

Recommended Duration

3 Weeks

Expected Outcome

The learner should confidently apply object-oriented principles while designing real-world applications and understand the trade-offs between different modeling approaches.

---

## Module 6 — Encapsulation

### Purpose

Understand how encapsulation protects object integrity by controlling access to internal state and exposing only well-defined behaviors.

### Major Areas

- What is Encapsulation?
- Information Hiding
- Data Protection
- Access Modifiers
- Public
- Private
- Protected
- Package-Private
- Getter & Setter Design
- Immutable Objects
- Validation
- Defensive Programming

### Learning Outcomes

- Explain encapsulation.
- Protect object state.
- Design robust APIs.
- Implement controlled data access.
- Build immutable domain objects.

### Interview Focus

- Encapsulation
- Information Hiding
- Access Modifiers
- Immutable Objects

### Production Relevance

- Enterprise Applications
- Domain Models
- REST APIs
- Financial Systems

### Common Mistakes

- Making every field public.
- Blindly generating getters and setters.
- Exposing mutable internal objects.

### Recommended Practice

- Design immutable classes.
- Refactor poorly encapsulated models.
- Compare mutable and immutable objects.

### Unlocks

- Module 7 — Inheritance

---

## Module 7 — Inheritance

### Purpose

Understand how inheritance enables code reuse while recognizing when it becomes an anti-pattern in modern software design.

### Major Areas

- What is Inheritance?
- IS-A Relationship
- Base Class
- Derived Class
- Method Overriding
- Constructor Chaining
- Protected Members
- Abstract Base Classes
- Template Hierarchies
- Inheritance Pitfalls
- Favor Composition Over Inheritance (Introduction)

### Learning Outcomes

- Explain inheritance.
- Design inheritance hierarchies.
- Identify inheritance misuse.
- Apply inheritance appropriately.
- Recognize inheritance limitations.

### Interview Focus

- IS-A Relationship
- Method Overriding
- Constructor Chaining
- Inheritance vs Composition

### Production Relevance

- Framework Development
- SDK Design
- Enterprise Applications
- Shared Domain Models

### Common Mistakes

- Deep inheritance hierarchies.
- Misusing inheritance for code reuse.
- Violating the Liskov Substitution Principle.

### Recommended Practice

- Refactor inheritance hierarchies.
- Compare inheritance with composition.
- Analyze framework class hierarchies.

### Unlocks

- Module 8 — Polymorphism

---

## Module 8 — Polymorphism

### Purpose

Understand how polymorphism enables flexible, extensible, and loosely coupled software through dynamic behavior.

### Major Areas

- What is Polymorphism?
- Compile-Time Polymorphism
- Runtime Polymorphism
- Method Overloading
- Method Overriding
- Dynamic Dispatch
- Virtual Methods
- Interface-Based Programming
- Strategy Selection
- Extensibility

### Learning Outcomes

- Explain polymorphism.
- Differentiate compile-time and runtime polymorphism.
- Implement dynamic behavior.
- Build extensible software.

### Interview Focus

- Method Overloading
- Method Overriding
- Dynamic Dispatch
- Runtime Polymorphism

### Production Relevance

- Payment Systems
- Notification Services
- Plugin Architectures
- Enterprise Frameworks

### Common Mistakes

- Confusing overloading with overriding.
- Ignoring runtime dispatch.
- Tight coupling through concrete implementations.

### Recommended Practice

- Implement polymorphic services.
- Compare interface and implementation.
- Analyze runtime dispatch examples.

### Unlocks

- Module 9 — Abstraction

---

## Module 9 — Abstraction

### Purpose

Understand how abstraction simplifies complex systems by exposing essential behavior while hiding implementation details.

### Major Areas

- What is Abstraction?
- Abstract Classes
- Interfaces
- Behavioral Contracts
- API Design
- Service Contracts
- Interface Segregation
- Domain Abstraction
- Layered Abstractions
- Dependency Inversion (Introduction)

### Learning Outcomes

- Explain abstraction.
- Design stable interfaces.
- Build reusable APIs.
- Separate implementation from behavior.

### Interview Focus

- Interface vs Abstract Class
- Abstraction
- API Design
- Contracts

### Production Relevance

- Microservices
- SDK Development
- Framework Design
- Enterprise Systems

### Common Mistakes

- Creating unnecessary abstractions.
- Large interfaces.
- Leaking implementation details.

### Recommended Practice

- Design service interfaces.
- Compare abstract classes and interfaces.
- Build layered abstractions.

### Unlocks

- Module 10 — Composition over Inheritance

---

## Module 10 — Composition over Inheritance

### Purpose

Learn why modern software architecture prefers object composition over inheritance to improve flexibility, maintainability, and scalability.

### Major Areas

- Has-A Relationship
- Composition
- Aggregation
- Delegation
- Dependency Injection (Introduction)
- Strategy Pattern (Introduction)
- Behavior Reuse
- Loose Coupling
- High Cohesion
- Composition Patterns
- Real-World Design Decisions

### Learning Outcomes

- Explain composition.
- Compare composition and inheritance.
- Design loosely coupled systems.
- Build reusable object collaborations.
- Recognize composition-based architectures.

### Interview Focus

- Composition vs Inheritance
- Aggregation vs Composition
- Loose Coupling
- High Cohesion
- Dependency Injection

### Production Relevance

- Spring Framework
- Microservices
- Plugin Systems
- Enterprise Applications
- Backend Services

### Common Mistakes

- Using inheritance by default.
- Tight coupling through inheritance.
- Ignoring delegation.

### Recommended Practice

- Refactor inheritance into composition.
- Design strategy-based systems.
- Analyze production architectures.

### Unlocks

- LEVEL 3 — DESIGN PRINCIPLES

---

# LEVEL 3 — DESIGN PRINCIPLES

## Objective

Master engineering principles, software craftsmanship, and reusable design techniques required for building maintainable production-grade software systems.

Recommended Duration

4 Weeks

Expected Outcome

The learner should confidently design extensible software using SOLID principles, GRASP patterns, clean code practices, design patterns, and systematic refactoring techniques.

# LEVEL 3 — DESIGN PRINCIPLES

## Objective

Master the engineering principles, software craftsmanship practices, and reusable design techniques required to build maintainable, extensible, and production-grade software systems.

Learners should understand not only *what* a design principle or pattern is, but *why* it exists, what problem it solves, the trade-offs involved, and how it is applied in real-world software.

Recommended Duration

4 Weeks

Expected Outcome

The learner should confidently design extensible software using SOLID principles, GRASP principles, Clean Code practices, Design Patterns, and systematic refactoring techniques.

---

## Module 11 — SOLID Principles

### Purpose

Learn the five SOLID principles that form the foundation of modern object-oriented software design and enable maintainable, scalable, and extensible applications.

### Major Areas

- Why SOLID Exists
- Software Maintainability
- Single Responsibility Principle (SRP)
- Open Closed Principle (OCP)
- Liskov Substitution Principle (LSP)
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)
- Principle Interactions
- Common Violations
- SOLID Trade-offs

### Learning Outcomes

- Explain each SOLID principle.
- Identify violations in existing code.
- Apply SOLID to production software.
- Design extensible object-oriented systems.
- Evaluate trade-offs between simplicity and extensibility.

### Interview Focus

- Explain all SOLID principles.
- SRP Examples
- OCP vs DIP
- LSP Violations
- Interface Segregation
- Dependency Inversion

### Production Relevance

- Spring Boot
- Enterprise Java
- Backend APIs
- Microservices
- Domain-Driven Design

### Common Mistakes

- Applying SOLID everywhere without necessity.
- Creating excessive abstractions.
- Violating SRP through God Classes.
- Misusing inheritance.

### Recommended Practice

- Refactor legacy code using SOLID.
- Identify principle violations.
- Build small systems applying all five principles.

### Unlocks

- Module 12 — GRASP Principles

---

## Module 12 — GRASP Principles

### Purpose

Understand how responsibilities should be assigned between objects to create low-coupled, high-cohesive, and maintainable software systems.

### Major Areas

- Introduction to GRASP
- Information Expert
- Creator
- Controller
- Low Coupling
- High Cohesion
- Polymorphism
- Pure Fabrication
- Indirection
- Protected Variations

### Learning Outcomes

- Assign responsibilities effectively.
- Design loosely coupled systems.
- Improve software maintainability.
- Evaluate object responsibilities.

### Interview Focus

- Information Expert
- Creator
- Controller
- Low Coupling
- High Cohesion
- Protected Variations

### Production Relevance

- Enterprise Applications
- Domain Modeling
- Backend Services
- Large Codebases

### Common Mistakes

- Concentrating responsibilities into one class.
- Ignoring cohesion.
- Excessive object dependencies.

### Recommended Practice

- Analyze responsibility distribution.
- Refactor tightly coupled systems.
- Design domain models using GRASP.

### Unlocks

- Module 13 — Clean Code

---

## Module 13 — Clean Code & Software Craftsmanship

### Purpose

Develop professional coding habits that improve readability, maintainability, collaboration, and long-term software quality.

### Major Areas

- What is Clean Code?
- Naming Conventions
- Method Design
- Class Design
- Code Smells
- DRY
- KISS
- YAGNI
- Boy Scout Rule
- Error Handling
- Logging
- Documentation
- Code Reviews
- Technical Debt

### Learning Outcomes

- Write readable code.
- Identify code smells.
- Apply clean coding principles.
- Improve maintainability.
- Reduce technical debt.

### Interview Focus

- Code Smells
- DRY
- KISS
- YAGNI
- Clean Code Principles

### Production Relevance

- Enterprise Development
- Code Reviews
- Large Teams
- Open Source Projects

### Common Mistakes

- Long methods.
- Large classes.
- Poor naming.
- Duplicate code.
- Overengineering.

### Recommended Practice

- Refactor poorly written code.
- Review production repositories.
- Perform peer code reviews.

### Unlocks

- Module 14 — Design Patterns

---

## Module 14 — Design Patterns

### Purpose

Understand reusable software design solutions and learn when each pattern should be applied based on the underlying engineering problem.

### Major Areas

#### Creational Patterns

- Singleton
- Factory Method
- Abstract Factory
- Builder
- Prototype

#### Structural Patterns

- Adapter
- Bridge
- Composite
- Decorator
- Facade
- Flyweight
- Proxy

#### Behavioral Patterns

- Strategy
- Observer
- Command
- State
- Template Method
- Iterator
- Chain of Responsibility
- Mediator
- Memento
- Visitor
- Interpreter

#### Pattern Selection

- When to Use
- When NOT to Use
- Pattern Trade-offs
- Anti-patterns

### Learning Outcomes

- Explain GoF patterns.
- Select appropriate design patterns.
- Avoid pattern misuse.
- Build reusable architectures.
- Compare multiple pattern choices.

### Interview Focus

- Singleton
- Factory
- Builder
- Strategy
- Observer
- Decorator
- Factory vs Builder
- Strategy vs State

### Production Relevance

- Spring Framework
- Hibernate
- Java SDK
- Enterprise Applications
- Backend Systems

### Common Mistakes

- Using patterns unnecessarily.
- Memorizing patterns without understanding.
- Applying multiple patterns to simple problems.

### Recommended Practice

- Implement every GoF pattern.
- Compare multiple implementations.
- Refactor systems using patterns.

### Unlocks

- Module 15 — Refactoring

---

## Module 15 — Refactoring

### Purpose

Learn systematic techniques for improving software design without changing external behavior.

### Major Areas

- Why Refactoring Matters
- Refactoring Workflow
- Code Smells
- Long Method
- Large Class
- Feature Envy
- Primitive Obsession
- Duplicate Code
- Extract Method
- Extract Class
- Move Method
- Replace Conditional with Polymorphism
- Introduce Parameter Object
- Replace Inheritance with Delegation
- Continuous Refactoring

### Learning Outcomes

- Identify refactoring opportunities.
- Improve maintainability.
- Preserve software behavior.
- Reduce technical debt.
- Refactor safely.

### Interview Focus

- Code Smells
- Extract Method
- Extract Class
- Replace Conditional
- Refactoring Strategies

### Production Relevance

- Legacy Systems
- Enterprise Maintenance
- Continuous Delivery
- Agile Development

### Common Mistakes

- Refactoring without tests.
- Mixing feature development with refactoring.
- Large-scale refactoring in a single iteration.

### Recommended Practice

- Refactor legacy applications.
- Remove code smells.
- Practice behavior-preserving refactoring.

### Unlocks

- LEVEL 4 — PRODUCTION SOFTWARE DESIGN

---

# LEVEL 4 — PRODUCTION SOFTWARE DESIGN

## Objective

Apply object-oriented design principles, design patterns, and software engineering practices to build production-ready systems, machine coding solutions, and enterprise application architectures.

Recommended Duration

4 Weeks

Expected Outcome

The learner should confidently design scalable software components, implement production-grade machine coding solutions, and bridge Low-Level Design with High-Level Design.

# LEVEL 4 — PRODUCTION SOFTWARE DESIGN

## Objective

Apply object-oriented principles, design patterns, and software engineering practices to build production-ready software systems, machine coding solutions, and enterprise application architectures.

Learners should understand how real production systems evolve beyond object modeling into layered architectures, concurrent programming, dependency injection, testing, and maintainability.

Recommended Duration

4 Weeks

Expected Outcome

The learner should confidently design scalable software components, build production-grade machine coding solutions, and prepare for enterprise software development.

---

## Module 16 — Modeling Real Systems

### Purpose

Learn how to convert real-world business requirements into maintainable software models using domain-driven object-oriented design.

### Major Areas

- Requirement Analysis
- Domain Modeling
- Entity
- Value Object
- Aggregate
- Aggregate Root
- Domain Service
- Repository Pattern
- Service Layer
- DTO
- Mapper
- Layered Architecture
- Dependency Graph
- Business Rules

### Learning Outcomes

- Model real-world domains.
- Design layered applications.
- Separate business logic from infrastructure.
- Build maintainable domain models.
- Design reusable software components.

### Interview Focus

- Entity vs DTO
- Entity vs Value Object
- Repository Pattern
- Service Layer
- Layered Architecture

### Production Relevance

- Spring Boot
- Enterprise Applications
- Banking Systems
- ERP Systems
- E-Commerce Platforms

### Common Mistakes

- Mixing business logic with controllers.
- Treating DTOs as entities.
- Anemic domain models.
- Large service classes.

### Recommended Practice

- Design Library Management System.
- Model Food Delivery System.
- Build Employee Management System.
- Design Hospital Management System.

### Unlocks

- Module 17 — Concurrency & Thread Safety

---

## Module 17 — Concurrency & Thread Safety

### Purpose

Understand how multiple threads interact with shared objects and learn to design thread-safe software components.

### Major Areas

- Thread Safety
- Shared Mutable State
- Race Conditions
- Deadlocks
- Synchronization
- Locks
- Reentrant Locks
- Read-Write Locks
- Atomic Variables
- Volatile
- Thread Pools
- Executor Framework
- Producer Consumer
- Immutability
- Concurrent Collections

### Learning Outcomes

- Explain thread safety.
- Identify race conditions.
- Prevent deadlocks.
- Design concurrent software.
- Build scalable multithreaded systems.

### Interview Focus

- Synchronization
- Deadlock
- Race Condition
- Atomic Variables
- Thread Pools
- Volatile

### Production Relevance

- Banking Systems
- Trading Platforms
- High-Performance APIs
- Distributed Systems
- Enterprise Applications

### Common Mistakes

- Synchronizing entire classes.
- Ignoring shared state.
- Creating unnecessary threads.
- Improper locking order.

### Recommended Practice

- Implement Producer-Consumer.
- Build Thread-Safe Cache.
- Design Concurrent Queue.
- Analyze Deadlock Scenarios.

### Unlocks

- Module 18 — Production Components

---

## Module 18 — Production Software Components

### Purpose

Understand reusable architectural building blocks commonly used in production-grade backend systems.

### Major Areas

- Dependency Injection
- Inversion of Control (IoC)
- Configuration Management
- Logging Framework
- Exception Handling Framework
- Authentication Module
- Authorization Module
- Caching Layer
- Session Management
- Notification Framework
- File Storage
- Plugin Architecture
- Validation Framework
- Audit Logging

### Learning Outcomes

- Design reusable infrastructure.
- Build modular software.
- Apply dependency injection.
- Design configurable applications.
- Build enterprise-ready software.

### Interview Focus

- Dependency Injection
- IoC
- Logging
- Authentication
- Caching
- Session Management

### Production Relevance

- Spring Boot
- Enterprise Applications
- SaaS Platforms
- Microservices
- Cloud Applications

### Common Mistakes

- Hardcoding dependencies.
- Ignoring configuration management.
- Poor exception handling.
- Tight coupling.

### Recommended Practice

- Build Authentication Module.
- Design Notification Service.
- Implement Cache Layer.
- Create Logging Framework.

### Unlocks

- LEVEL 5 — EXPERT

---

# LEVEL 5 — EXPERT

## Objective

Consolidate all Low-Level Design concepts into production-quality machine coding solutions and interview-ready software architectures.

Recommended Duration

3 Weeks

Expected Outcome

The learner should confidently solve machine coding interviews, explain design decisions, justify trade-offs, and build production-ready software architectures.

---

## Module 19 — Machine Coding Interviews

### Purpose

Apply Low-Level Design principles to solve end-to-end software design problems under interview constraints.

### Major Areas

- Requirement Analysis
- Class Design
- UML Design
- Object Relationships
- SOLID Application
- Design Patterns
- Extensibility
- Error Handling
- Validation
- Testing Strategy
- Scalability Considerations

### Standard Machine Coding Problems

- Parking Lot
- Splitwise
- BookMyShow
- Elevator System
- Library Management
- ATM
- Hotel Management
- Car Rental
- Cricbuzz
- Snake & Ladder
- Chess
- Food Delivery System

### Learning Outcomes

- Design interview-ready systems.
- Apply object-oriented principles.
- Explain architectural decisions.
- Produce clean production-quality code.

### Interview Focus

- Parking Lot
- Splitwise
- Elevator
- ATM
- BookMyShow
- Chess

### Production Relevance

- Enterprise Software Development
- Product Companies
- Backend Engineering

### Common Mistakes

- Jumping into coding.
- Ignoring extensibility.
- Overengineering.
- Tight coupling.

### Recommended Practice

- Solve at least 15 machine coding problems.
- Conduct mock interviews.
- Explain UML before implementation.

### Unlocks

- Module 20 — Production Architecture

---

## Module 20 — Production Architecture

### Purpose

Bridge Low-Level Design with High-Level Design by understanding how well-designed components evolve into scalable software architectures.

### Major Areas

- Layered Architecture
- Hexagonal Architecture
- Clean Architecture
- Onion Architecture
- Modular Monolith
- Plugin Architecture
- Event-Driven Design
- Domain-Driven Design (Overview)
- Component Boundaries
- Maintainability
- Scalability
- Observability
- Technical Debt
- Evolutionary Architecture

### Learning Outcomes

- Connect LLD with HLD.
- Design maintainable architectures.
- Understand architectural evolution.
- Prepare for distributed system design.

### Interview Focus

- Layered Architecture
- Clean Architecture
- Hexagonal Architecture
- DDD
- Component Design

### Production Relevance

- Enterprise Platforms
- Banking Systems
- SaaS Products
- Cloud Applications
- Microservices

### Common Mistakes

- Mixing architecture with implementation.
- Tight coupling across modules.
- Ignoring maintainability.
- Overusing design patterns.

### Recommended Practice

- Design enterprise architectures.
- Compare architectural styles.
- Review open-source backend projects.

### Unlocks

- High-Level Design
- Distributed Systems
- Software Architecture
- Enterprise Backend Engineering

---

# Exit Criteria

A learner completing this curriculum should be able to:

- Design maintainable object-oriented software.
- Apply SOLID and GRASP principles.
- Select and implement appropriate design patterns.
- Refactor legacy systems confidently.
- Build production-quality machine coding solutions.
- Design layered enterprise applications.
- Write thread-safe software.
- Explain design trade-offs.
- Bridge Low-Level Design with High-Level Design.
- Mentor junior engineers on software design.

---

# Prerequisites

- Programming Fundamentals
- Java
- Data Structures & Algorithms
- Database Management Systems
- Operating Systems
- Computer Networks

---

# Unlocks

Completion of this curriculum unlocks:

- High-Level Design
- Distributed Systems
- Microservices
- Software Architecture
- Enterprise Backend Engineering
- Cloud Architecture
- System Design Interviews
- Production Engineering

---

# Curriculum Maintenance Rules

- This curriculum is the canonical source of truth for Low-Level Design within PrepOS.
- Every module must follow the canonical subject template defined in `00-subject-template.md`.
- New topics must preserve the learning progression from Foundation → Expert.
- Design principles should always precede design patterns.
- Machine coding problems should reinforce production engineering practices rather than interview shortcuts.
- Any additions or modifications must maintain backward compatibility with the curriculum generator and roadmap pipeline.