# PrepOS Curriculum Constitution

**File:** `docs/curriculum/08-hld.md`

Version: 1.0

Status: Canonical

Owner: PrepOS Architecture Team

---

# High-Level Design (HLD)

## Vision

High-Level Design teaches software engineers how to architect scalable, reliable, secure, maintainable, and distributed software systems capable of serving millions of users.

Unlike Low-Level Design, which focuses on designing classes and software components, High-Level Design focuses on designing complete production systems by combining distributed computing principles, networking, databases, messaging systems, caching, cloud infrastructure, observability, and scalability.

This curriculum transforms software developers into system architects capable of making engineering trade-offs for real-world applications.

---

# Learning Objectives

After completing this curriculum, the learner should be able to:

- Translate business requirements into scalable architectures
- Estimate system capacity
- Design highly available distributed systems
- Select appropriate storage technologies
- Design scalable APIs
- Build resilient event-driven systems
- Apply consistency and availability trade-offs
- Design cloud-native applications
- Optimize system performance
- Explain architectural decisions during interviews

---

# Curriculum Structure

The curriculum follows five learning stages.

1. Foundation
2. Basic
3. Intermediate
4. Advanced
5. Expert

Every module follows the canonical subject template defined in:

`docs/curriculum/governance/00-subject-template.md`

Each module contains:

- Purpose
- Major Areas
- Learning Outcomes
- Interview Focus
- Production Relevance
- Common Mistakes
- Recommended Practice
- Unlocks

---

# LEVEL 1 — FOUNDATIONS

## Objective

Develop the architectural mindset required to move from designing software components to designing complete software systems.

Learners will understand why distributed systems exist, how production systems evolve, and which engineering trade-offs drive architectural decisions.

Recommended Duration

3 Weeks

Expected Outcome

The learner should confidently understand system design terminology, architectural thinking, scalability fundamentals, and the core building blocks of modern software architectures.

---

## Module 1 — Introduction to System Design

### Purpose

Understand the purpose of High-Level Design, how software systems evolve over time, and why architectural thinking is essential for building scalable applications.

### Major Areas

- What is High-Level Design?
- Why HLD Exists
- Software Architecture vs Software Design
- Functional Requirements
- Non-Functional Requirements
- Quality Attributes
- Scalability
- Reliability
- Availability
- Maintainability
- Performance
- Security
- Cost Optimization
- Evolution of Software Systems

### Learning Outcomes

- Explain High-Level Design.
- Differentiate HLD and LLD.
- Identify architectural goals.
- Analyze system requirements.
- Recognize software quality attributes.

### Interview Focus

- What is HLD?
- Functional vs Non-Functional Requirements
- Architecture vs Design
- Scalability
- Availability

### Production Relevance

- Product Engineering
- Enterprise Platforms
- Cloud Applications
- SaaS Products

### Common Mistakes

- Ignoring non-functional requirements.
- Designing without understanding business goals.
- Premature optimization.
- Overengineering.

### Recommended Practice

- Analyze architectures of popular applications.
- Identify quality attributes in existing products.
- Practice converting requirements into architecture goals.

### Unlocks

- Module 2 — Architectural Thinking

---

## Module 2 — Architectural Thinking

### Purpose

Learn how experienced architects approach large software systems through decomposition, abstraction, trade-off analysis, and iterative design.

### Major Areas

- Architectural Thinking
- System Decomposition
- Abstraction
- Separation of Concerns
- Modularization
- Coupling
- Cohesion
- Layered Thinking
- Architectural Trade-offs
- Design Constraints
- Evolutionary Architecture

### Learning Outcomes

- Break systems into components.
- Evaluate architecture alternatives.
- Reduce coupling.
- Improve maintainability.
- Design modular systems.

### Interview Focus

- Coupling vs Cohesion
- Separation of Concerns
- Layered Architecture
- Trade-off Analysis

### Production Relevance

- Enterprise Applications
- Backend Platforms
- Microservices
- Cloud Systems

### Common Mistakes

- Building monolithic dependencies.
- Ignoring abstraction.
- Excessive coupling.
- Poor module boundaries.

### Recommended Practice

- Decompose existing applications.
- Compare architectural approaches.
- Design modular service boundaries.

### Unlocks

- Module 3 — Scalability Fundamentals

---

## Module 3 — Scalability Fundamentals

### Purpose

Understand how modern systems handle increasing users, requests, data, and infrastructure while maintaining performance and reliability.

### Major Areas

- What is Scalability?
- Vertical Scaling
- Horizontal Scaling
- Throughput
- Latency
- Bottlenecks
- Capacity Planning
- Load Characteristics
- Elasticity
- Auto Scaling
- Performance Metrics

### Learning Outcomes

- Differentiate scaling strategies.
- Estimate capacity requirements.
- Identify bottlenecks.
- Improve system performance.
- Evaluate scalability trade-offs.

### Interview Focus

- Vertical vs Horizontal Scaling
- Throughput
- Latency
- Capacity Planning

### Production Relevance

- Cloud Platforms
- Distributed Applications
- SaaS Products

### Common Mistakes

- Scaling too early.
- Ignoring bottlenecks.
- Measuring the wrong metrics.

### Recommended Practice

- Estimate system capacity.
- Compare scaling strategies.
- Analyze production architectures.

### Unlocks

- Module 4 — Distributed Systems Fundamentals

---

## Module 4 — Distributed Systems Fundamentals

### Purpose

Introduce the principles of distributed computing and explain why modern applications rely on multiple interconnected services instead of single machines.

### Major Areas

- Distributed Systems
- Nodes
- Clusters
- Distributed Communication
- Network Partitions
- Distributed Coordination
- Fault Tolerance
- Replication
- Consensus (Introduction)
- CAP Theorem (Overview)

### Learning Outcomes

- Explain distributed systems.
- Identify distributed system challenges.
- Understand replication concepts.
- Analyze fault tolerance.

### Interview Focus

- CAP Theorem
- Replication
- Fault Tolerance
- Distributed Systems Basics

### Production Relevance

- Kubernetes
- Cloud Computing
- Distributed Databases
- Microservices

### Common Mistakes

- Assuming perfect networks.
- Ignoring failures.
- Tight service dependencies.

### Recommended Practice

- Study distributed architectures.
- Analyze cloud platforms.
- Compare monoliths vs distributed systems.

### Unlocks

- Module 5 — Capacity Estimation

---

## Module 5 — Capacity Estimation

### Purpose

Learn how architects estimate infrastructure requirements before designing production systems.

### Major Areas

- Traffic Estimation
- DAU
- MAU
- QPS
- RPS
- Storage Estimation
- Memory Estimation
- Bandwidth Estimation
- Read/Write Ratio
- Growth Projection
- Cost Estimation

### Learning Outcomes

- Estimate infrastructure needs.
- Calculate storage requirements.
- Evaluate traffic growth.
- Design capacity-aware architectures.

### Interview Focus

- Capacity Estimation
- Traffic Calculation
- Storage Calculation
- QPS Estimation

### Production Relevance

- Cloud Infrastructure
- SaaS Products
- Enterprise Platforms

### Common Mistakes

- Unrealistic assumptions.
- Ignoring future growth.
- Underestimating storage.

### Recommended Practice

- Estimate YouTube architecture.
- Estimate WhatsApp traffic.
- Estimate Instagram storage.

### Unlocks

- LEVEL 2 — DISTRIBUTED ARCHITECTURE

# LEVEL 2 — DISTRIBUTED ARCHITECTURE

## Objective

Master the fundamental architectural building blocks required to design scalable distributed systems.

Learners should understand how requests travel across distributed systems, how data is distributed, how services communicate, and how infrastructure components improve scalability, reliability, and availability.

Recommended Duration

4 Weeks

Expected Outcome

The learner should confidently design scalable architectures using load balancers, proxies, caching, databases, CDNs, and communication patterns while understanding the trade-offs of each architectural decision.

---

## Module 6 — Load Balancing

### Purpose

Understand how incoming requests are distributed across multiple servers to improve scalability, availability, and fault tolerance.

### Major Areas

- Why Load Balancing Exists
- Load Balancer Architecture
- Layer 4 Load Balancing
- Layer 7 Load Balancing
- Reverse Proxy
- Health Checks
- Sticky Sessions
- Session Affinity
- Failover
- Active-Active
- Active-Passive
- Load Balancing Algorithms
- Round Robin
- Weighted Round Robin
- Least Connections
- IP Hash
- Consistent Hashing (Introduction)

### Learning Outcomes

- Explain load balancing.
- Select appropriate algorithms.
- Design highly available systems.
- Eliminate single points of failure.
- Improve system scalability.

### Interview Focus

- L4 vs L7
- Reverse Proxy
- Sticky Sessions
- Health Checks
- Round Robin
- Least Connections

### Production Relevance

- NGINX
- HAProxy
- AWS ELB
- Azure Load Balancer
- Google Cloud Load Balancing

### Common Mistakes

- Single load balancer deployment.
- Ignoring health checks.
- Improper session affinity.
- Uneven traffic distribution.

### Recommended Practice

- Design scalable web architectures.
- Compare load balancing algorithms.
- Analyze production deployments.

### Unlocks

- Module 7 — API Gateway & Reverse Proxy

---

## Module 7 — API Gateway & Reverse Proxy

### Purpose

Learn how modern distributed systems expose APIs securely while centralizing authentication, routing, rate limiting, logging, and request management.

### Major Areas

- API Gateway
- Reverse Proxy
- Request Routing
- Authentication
- Authorization
- JWT Validation
- SSL Termination
- Rate Limiting
- API Versioning
- Request Aggregation
- Circuit Breaking (Introduction)
- Logging
- Monitoring
- Request Transformation

### Learning Outcomes

- Design secure API architectures.
- Route requests efficiently.
- Centralize authentication.
- Apply rate limiting.
- Protect backend services.

### Interview Focus

- API Gateway
- Reverse Proxy
- JWT Validation
- Rate Limiting
- SSL Termination

### Production Relevance

- Kong
- Spring Cloud Gateway
- AWS API Gateway
- Azure API Management
- NGINX

### Common Mistakes

- Business logic inside gateway.
- Missing rate limiting.
- Gateway as bottleneck.
- Poor authentication design.

### Recommended Practice

- Design API Gateway architecture.
- Compare gateway implementations.
- Analyze production APIs.

### Unlocks

- Module 8 — Caching

---

## Module 8 — Caching

### Purpose

Understand how caching improves system performance, reduces latency, and minimizes database load.

### Major Areas

- Why Caching Exists
- Cache Architecture
- Cache Hit
- Cache Miss
- Cache Invalidation
- Cache Eviction Policies
- LRU
- LFU
- FIFO
- TTL
- Write Through
- Write Around
- Write Back
- Client Cache
- CDN Cache
- Application Cache
- Distributed Cache
- Cache Consistency

### Learning Outcomes

- Design cache strategies.
- Improve application performance.
- Reduce database load.
- Select cache eviction policies.
- Analyze cache trade-offs.

### Interview Focus

- Cache Hit Ratio
- LRU
- LFU
- TTL
- Redis
- Cache Invalidation

### Production Relevance

- Redis
- Memcached
- CDN
- Spring Cache
- CloudFront

### Common Mistakes

- Caching everything.
- Ignoring cache invalidation.
- Large cache objects.
- Stale cache problems.

### Recommended Practice

- Design caching for e-commerce.
- Compare caching strategies.
- Analyze cache failures.

### Unlocks

- Module 9 — Distributed Storage

---

## Module 9 — Distributed Storage

### Purpose

Learn how modern applications store massive amounts of data while balancing consistency, availability, durability, and scalability.

### Major Areas

- Storage Fundamentals
- File Storage
- Object Storage
- Block Storage
- Shared Storage
- Database Storage
- Data Partitioning
- Sharding
- Replication
- Read Replicas
- Backup
- Disaster Recovery
- Multi-Region Storage
- Storage Trade-offs

### Learning Outcomes

- Select appropriate storage models.
- Design scalable storage.
- Understand replication strategies.
- Improve data availability.
- Analyze storage trade-offs.

### Interview Focus

- Replication
- Sharding
- Object Storage
- File Storage
- Read Replica

### Production Relevance

- Amazon S3
- Azure Blob Storage
- Google Cloud Storage
- NAS
- SAN

### Common Mistakes

- Single storage node.
- Poor partition strategy.
- Missing backups.
- Ignoring disaster recovery.

### Recommended Practice

- Design storage for Dropbox.
- Compare storage models.
- Analyze backup architectures.

### Unlocks

- Module 10 — Communication Patterns

---

## Module 10 — Communication Patterns

### Purpose

Understand how distributed services communicate efficiently, reliably, and asynchronously across modern architectures.

### Major Areas

- Client-Server Communication
- Request-Response
- Synchronous Communication
- Asynchronous Communication
- RPC
- REST
- GraphQL
- gRPC
- WebSockets
- Long Polling
- Server-Sent Events
- Publish-Subscribe (Introduction)
- Event Notification
- Communication Trade-offs

### Learning Outcomes

- Select communication protocols.
- Compare synchronous and asynchronous systems.
- Design reliable service communication.
- Evaluate protocol trade-offs.

### Interview Focus

- REST vs gRPC
- REST vs GraphQL
- WebSockets
- RPC
- Synchronous vs Asynchronous

### Production Relevance

- REST APIs
- gRPC Services
- GraphQL APIs
- Real-Time Systems
- Enterprise Microservices

### Common Mistakes

- Using synchronous communication everywhere.
- Overusing GraphQL.
- Improper protocol selection.
- Ignoring network latency.

### Recommended Practice

- Design communication architecture.
- Compare protocol implementations.
- Analyze production API ecosystems.

### Unlocks

- LEVEL 3 — DATA & MESSAGING ARCHITECTURES

---

# LEVEL 3 — DATA & MESSAGING ARCHITECTURES

## Objective

Master distributed data management, messaging infrastructure, consistency models, and reliability patterns required to build highly scalable production systems.

Recommended Duration

4 Weeks

Expected Outcome

The learner should confidently design distributed data pipelines, messaging systems, and resilient architectures suitable for enterprise-scale applications.

# LEVEL 3 — DATA & MESSAGING ARCHITECTURES

## Objective

Master distributed data management, messaging infrastructure, consistency models, and service architectures required to build highly scalable, fault-tolerant, and production-ready distributed systems.

Learners should understand how modern internet-scale applications manage data, communicate between services, ensure reliability, and balance consistency with availability.

Recommended Duration

4 Weeks

Expected Outcome

The learner should confidently design distributed data architectures, event-driven systems, microservices, and resilient production systems while understanding the engineering trade-offs involved.

---

## Module 11 — Distributed Databases

### Purpose

Understand how modern databases scale horizontally while maintaining consistency, availability, durability, and fault tolerance across multiple servers and geographic regions.

### Major Areas

- Why Distributed Databases Exist
- Horizontal Scaling
- Vertical Scaling
- Database Replication
- Primary-Replica Architecture
- Multi-Master Replication
- Read Replicas
- Database Sharding
- Partition Keys
- Rebalancing
- Data Locality
- Cross-Shard Queries
- Distributed Transactions (Introduction)
- Global Databases

### Learning Outcomes

- Explain distributed databases.
- Design scalable database architectures.
- Compare replication strategies.
- Understand database partitioning.
- Analyze distributed database trade-offs.

### Interview Focus

- Sharding
- Replication
- Read Replicas
- Partitioning
- Horizontal Scaling

### Production Relevance

- PostgreSQL
- MySQL
- MongoDB
- Cassandra
- CockroachDB
- YugabyteDB

### Common Mistakes

- Poor shard key selection.
- Ignoring cross-region latency.
- Uneven shard distribution.
- Overusing replication.

### Recommended Practice

- Design Instagram database.
- Design WhatsApp storage.
- Compare SQL and NoSQL scaling.

### Unlocks

- Module 12 — Messaging Systems

---

## Module 12 — Messaging Systems

### Purpose

Learn how asynchronous messaging enables scalable, loosely coupled, fault-tolerant distributed systems.

### Major Areas

- Why Messaging Exists
- Message Queues
- Publish Subscribe
- Producers
- Consumers
- Topics
- Partitions
- Ordering Guarantees
- Delivery Semantics
- At Most Once
- At Least Once
- Exactly Once
- Dead Letter Queue
- Retry Mechanisms
- Event Streaming
- Message Retention

### Learning Outcomes

- Design asynchronous architectures.
- Select messaging models.
- Build reliable event pipelines.
- Handle failures gracefully.
- Compare messaging technologies.

### Interview Focus

- Kafka
- RabbitMQ
- Pub/Sub
- DLQ
- Exactly Once
- Message Ordering

### Production Relevance

- Apache Kafka
- RabbitMQ
- AWS SQS
- Google Pub/Sub
- Azure Service Bus

### Common Mistakes

- Ignoring duplicate messages.
- Large message payloads.
- Missing retry strategy.
- Improper partitioning.

### Recommended Practice

- Design order processing.
- Design notification service.
- Compare Kafka and RabbitMQ.

### Unlocks

- Module 13 — Consistency & Distributed Transactions

---

## Module 13 — Consistency & Distributed Transactions

### Purpose

Understand consistency guarantees, distributed transactions, and the trade-offs required when building globally distributed systems.

### Major Areas

- ACID Review
- BASE
- Strong Consistency
- Eventual Consistency
- Causal Consistency
- CAP Theorem
- PACELC Theorem
- Distributed Transactions
- Two Phase Commit
- Three Phase Commit
- Saga Pattern
- Idempotency
- Compensation Transactions
- Conflict Resolution

### Learning Outcomes

- Explain consistency models.
- Apply CAP theorem.
- Compare ACID and BASE.
- Design distributed transactions.
- Select consistency strategies.

### Interview Focus

- CAP Theorem
- ACID vs BASE
- Saga Pattern
- 2PC
- Eventual Consistency

### Production Relevance

- Banking Systems
- E-Commerce
- Distributed Databases
- Microservices

### Common Mistakes

- Using distributed transactions unnecessarily.
- Ignoring eventual consistency.
- Missing idempotency.
- Improper compensation logic.

### Recommended Practice

- Design payment workflow.
- Compare Saga vs 2PC.
- Analyze distributed failures.

### Unlocks

- Module 14 — Microservices Architecture

---

## Module 14 — Microservices Architecture

### Purpose

Learn how large software systems are decomposed into independently deployable services that scale, evolve, and operate autonomously.

### Major Areas

- Why Microservices
- Monolith vs Microservices
- Service Boundaries
- Domain Driven Design (Overview)
- API Contracts
- Service Discovery
- Configuration Management
- Database Per Service
- Shared Database Anti-pattern
- API Composition
- Backend for Frontend
- Event Driven Microservices
- Service Versioning

### Learning Outcomes

- Design microservice architectures.
- Define service boundaries.
- Avoid common anti-patterns.
- Build independently deployable services.
- Evaluate architecture trade-offs.

### Interview Focus

- Monolith vs Microservices
- Service Discovery
- Database Per Service
- API Gateway
- DDD

### Production Relevance

- Spring Boot
- Kubernetes
- Netflix OSS
- Cloud Native Platforms

### Common Mistakes

- Splitting services too early.
- Shared databases.
- Excessive service communication.
- Poor boundary definition.

### Recommended Practice

- Design e-commerce services.
- Design food delivery backend.
- Compare monolith and microservices.

### Unlocks

- Module 15 — Reliability & Resilience

---

## Module 15 — Reliability & Resilience

### Purpose

Learn how production systems remain available despite failures through resilience patterns, fault isolation, and graceful degradation.

### Major Areas

- Reliability
- Availability
- Fault Tolerance
- High Availability
- Redundancy
- Circuit Breaker
- Retry Pattern
- Timeout
- Bulkhead
- Rate Limiting
- Backpressure
- Graceful Degradation
- Health Checks
- Heartbeats
- Failover
- Disaster Recovery

### Learning Outcomes

- Design resilient systems.
- Prevent cascading failures.
- Implement fault isolation.
- Improve availability.
- Build highly reliable architectures.

### Interview Focus

- Circuit Breaker
- Retry
- Timeout
- Bulkhead
- High Availability
- Disaster Recovery

### Production Relevance

- Resilience4j
- Hystrix (Legacy)
- Kubernetes
- Istio
- Service Mesh

### Common Mistakes

- Infinite retries.
- Missing timeout configuration.
- Ignoring cascading failures.
- Single points of failure.

### Recommended Practice

- Design resilient payment systems.
- Implement retry strategies.
- Analyze production outages.

### Unlocks

- LEVEL 4 — CLOUD & SCALABLE SYSTEM DESIGN

---

# LEVEL 4 — CLOUD & SCALABLE SYSTEM DESIGN

## Objective

Apply distributed systems principles to cloud-native infrastructure, observability, security, and large-scale production architectures capable of serving millions of users.

Recommended Duration

4 Weeks

Expected Outcome

The learner should confidently architect cloud-native systems, design globally distributed applications, and prepare for senior software engineer and system design interviews.

# LEVEL 4 — CLOUD & SCALABLE SYSTEM DESIGN

## Objective

Apply distributed systems principles to cloud-native infrastructure, observability, security, and globally scalable architectures capable of serving millions of users.

Learners should understand how production systems are deployed, monitored, secured, and continuously evolved in modern cloud environments.

Recommended Duration

4 Weeks

Expected Outcome

The learner should confidently design cloud-native architectures, build observable systems, secure distributed applications, and understand the infrastructure behind large-scale internet products.

---

## Module 16 — Cloud-Native Architecture

### Purpose

Understand how modern distributed systems leverage cloud infrastructure to achieve elasticity, resilience, global availability, and operational simplicity.

### Major Areas

- Cloud Computing Fundamentals
- IaaS
- PaaS
- SaaS
- Virtual Machines
- Containers
- Docker
- Kubernetes
- Auto Scaling
- Service Discovery
- Infrastructure as Code
- Multi-Region Deployment
- Multi-Cloud
- Cloud Cost Optimization

### Learning Outcomes

- Explain cloud-native architecture.
- Compare deployment models.
- Design scalable cloud systems.
- Evaluate cloud trade-offs.
- Understand container orchestration.

### Interview Focus

- Docker
- Kubernetes
- Auto Scaling
- Containers vs VMs
- Cloud Deployment

### Production Relevance

- AWS
- Azure
- Google Cloud
- Kubernetes
- Docker

### Common Mistakes

- Treating containers as virtual machines.
- Ignoring cloud costs.
- Improper scaling policies.
- Single-region deployments.

### Recommended Practice

- Design cloud-native architecture.
- Deploy applications using containers.
- Compare cloud providers.

### Unlocks

- Module 17 — Observability & Monitoring

---

## Module 17 — Observability & Monitoring

### Purpose

Learn how production systems are monitored, debugged, and analyzed to ensure reliability, performance, and rapid incident resolution.

### Major Areas

- Observability
- Monitoring
- Logging
- Metrics
- Distributed Tracing
- Health Checks
- Alerting
- Dashboards
- Service Level Indicators (SLI)
- Service Level Objectives (SLO)
- Service Level Agreements (SLA)
- Incident Response
- Root Cause Analysis
- Performance Monitoring
- Capacity Monitoring

### Learning Outcomes

- Build observable systems.
- Design monitoring strategies.
- Analyze production failures.
- Interpret metrics and logs.
- Improve operational reliability.

### Interview Focus

- Logging
- Metrics
- Tracing
- SLI
- SLO
- SLA

### Production Relevance

- Prometheus
- Grafana
- ELK Stack
- OpenTelemetry
- Jaeger
- Zipkin

### Common Mistakes

- Logging excessive information.
- Missing business metrics.
- Poor alert configuration.
- Ignoring distributed tracing.

### Recommended Practice

- Design monitoring architecture.
- Analyze production incidents.
- Build dashboards for distributed systems.

### Unlocks

- Module 18 — Security & Reliability

---

## Module 18 — Security & Reliability

### Purpose

Understand how modern distributed systems are protected against failures, attacks, and operational risks while maintaining availability and compliance.

### Major Areas

- Authentication
- Authorization
- OAuth
- OpenID Connect
- API Security
- TLS
- Encryption
- Secrets Management
- Rate Limiting
- WAF
- Zero Trust
- Disaster Recovery
- Backup Strategy
- Compliance
- High Availability

### Learning Outcomes

- Design secure architectures.
- Protect APIs.
- Build highly available systems.
- Understand disaster recovery.
- Evaluate security trade-offs.

### Interview Focus

- OAuth
- JWT
- TLS
- Disaster Recovery
- High Availability

### Production Relevance

- AWS IAM
- Azure AD
- HashiCorp Vault
- Cloudflare
- Kubernetes Security

### Common Mistakes

- Hardcoded secrets.
- Weak authentication.
- Missing backups.
- Ignoring disaster recovery.

### Recommended Practice

- Secure API architecture.
- Design disaster recovery plans.
- Review security best practices.

### Unlocks

- LEVEL 5 — EXPERT SYSTEM DESIGN

---

# LEVEL 5 — EXPERT SYSTEM DESIGN

## Objective

Integrate all High-Level Design concepts into complete production architectures and develop the ability to solve senior-level system design interviews.

Recommended Duration

3 Weeks

Expected Outcome

The learner should confidently design internet-scale systems, justify architectural trade-offs, and communicate solutions like a Staff or Principal Software Engineer.

---

## Module 19 — End-to-End System Design

### Purpose

Apply all previously learned concepts to design complete, production-scale systems from requirements gathering through deployment.

### Major Areas

- Requirement Gathering
- Functional Requirements
- Non-Functional Requirements
- Capacity Planning
- API Design
- Database Design
- Caching Strategy
- Load Balancing
- Messaging
- Microservices
- Security
- Monitoring
- Cost Optimization
- Trade-off Analysis

### Standard System Design Problems

- URL Shortener
- Instagram
- WhatsApp
- Uber
- Netflix
- YouTube
- Google Drive
- Dropbox
- Twitter / X
- Amazon
- PayPal
- Online Banking
- Ride Sharing
- Food Delivery
- Chat Application
- Notification Service
- Search Engine
- News Feed
- Distributed Cache
- API Rate Limiter

### Learning Outcomes

- Design complete distributed systems.
- Justify architecture decisions.
- Compare multiple design alternatives.
- Balance scalability, cost, and reliability.
- Produce interview-ready system designs.

### Interview Focus

- End-to-End System Design
- Scalability
- Trade-offs
- Capacity Planning
- Architecture Reviews

### Production Relevance

- FAANG
- Uber
- Netflix
- Stripe
- Atlassian
- Microsoft
- Amazon

### Common Mistakes

- Jumping directly into architecture.
- Ignoring requirements.
- Missing bottleneck analysis.
- Overengineering simple systems.

### Recommended Practice

- Solve at least 25 complete system design problems.
- Conduct mock architecture interviews.
- Present architecture diagrams.

### Unlocks

- Module 20 — Software Architecture Mastery

---

## Module 20 — Software Architecture Mastery

### Purpose

Develop the architectural mindset required to lead engineering teams, evolve software platforms, and make long-term technology decisions.

### Major Areas

- Architecture Decision Records (ADR)
- Evolutionary Architecture
- Domain-Driven Design (Advanced)
- Event-Driven Architecture
- CQRS
- Event Sourcing
- Service Mesh
- Platform Engineering
- Engineering Governance
- Architecture Reviews
- Technical Leadership
- Cost vs Performance
- Build vs Buy Decisions
- Architectural Trade-offs
- Future-Proof System Design

### Learning Outcomes

- Think like a software architect.
- Evaluate long-term design decisions.
- Lead architecture discussions.
- Design enterprise-scale platforms.
- Mentor engineering teams.

### Interview Focus

- Architecture Reviews
- DDD
- CQRS
- Event Sourcing
- Engineering Trade-offs

### Production Relevance

- Enterprise Platforms
- SaaS Products
- Cloud Infrastructure
- Platform Engineering
- Staff/Principal Engineering

### Common Mistakes

- Chasing trends instead of solving business problems.
- Ignoring operational complexity.
- Overengineering.
- Poor documentation.

### Recommended Practice

- Review architecture case studies.
- Write Architecture Decision Records.
- Compare multiple architectural approaches.
- Conduct design reviews.

### Unlocks

- Staff Engineer
- Principal Engineer
- Software Architect
- Engineering Manager
- Technical Leadership

---

# Exit Criteria

A learner completing this curriculum should be able to:

- Design internet-scale distributed systems.
- Estimate infrastructure capacity.
- Build cloud-native architectures.
- Select appropriate databases and messaging systems.
- Design resilient microservice architectures.
- Apply caching and scalability strategies.
- Build observable and secure production systems.
- Solve senior-level system design interviews.
- Explain architectural trade-offs clearly.
- Design enterprise-grade software platforms.

---

# Prerequisites

- Programming Fundamentals
- Java
- Data Structures & Algorithms
- Database Management Systems
- Operating Systems
- Computer Networks
- Low-Level Design

---

# Unlocks

Completion of this curriculum unlocks:

- Distributed Systems
- Cloud Architecture
- Backend Architecture
- Platform Engineering
- DevOps Engineering
- Site Reliability Engineering
- Staff Software Engineering
- Principal Engineering
- Engineering Management
- Technical Architecture

---

# Curriculum Maintenance Rules

- This curriculum is the canonical source of truth for High-Level Design within PrepOS.
- Every module must follow the canonical subject template defined in `00-subject-template.md`.
- New topics must preserve the learning progression from Foundation → Expert.
- Architectural concepts must always progress from fundamentals → distributed systems → cloud-native architecture → production system design.
- System design case studies should emphasize engineering trade-offs rather than memorized solutions.
- Any additions or modifications must maintain backward compatibility with the curriculum generator and roadmap pipeline.