# PrepOS Curriculum Constitution

**File:** `docs/curriculum/subjects/06-computer-networks.md`

Version: 2.0

Status: Canonical

Owner: PrepOS Architecture Team

Subject Code: CN-601

Difficulty: Foundation → Expert

Estimated Duration: 8–10 Weeks

Prerequisite Subjects:

- Programming Fundamentals
- Java
- Data Structures & Algorithms
- Operating Systems

Unlocks:

- Backend Engineering
- Distributed Systems
- Cloud Computing
- Microservices
- DevOps
- Kubernetes
- System Design
- Site Reliability Engineering
- Network Security

---

# Computer Networks

---

# Vision

Computer Networks form the communication backbone of modern software systems.

Every web application, cloud platform, distributed system, mobile application, microservice, database cluster, and AI platform relies on networking principles to exchange information efficiently, securely, and reliably.

The objective of this curriculum is not merely to teach networking protocols, but to help learners understand how computers communicate, how the Internet functions internally, how cloud infrastructure is built, and how networking concepts directly influence backend engineering, distributed systems, scalability, security, and production software.

---

# Subject Philosophy

PrepOS teaches Computer Networks from a software engineering perspective rather than a networking certification perspective.

Instead of memorizing protocol definitions, learners progressively understand:

- How computers communicate
- Why protocols exist
- How data flows across the Internet
- How latency affects applications
- How cloud networking works
- Why backend engineers must understand networking
- How networking influences distributed systems and system design

Every advanced networking concept is built upon previously mastered foundations.

---

# Learning Objectives

After completing this curriculum, learners should be able to:

- Explain how modern computer networks operate
- Understand the Internet architecture
- Analyze packet flow across networks
- Compare networking protocols
- Configure basic network concepts
- Debug networking issues
- Understand cloud networking fundamentals
- Explain backend communication protocols
- Analyze production networking architectures
- Confidently answer networking interview questions
- Apply networking concepts while designing scalable software systems

---

# Subject Progression

The curriculum is organized into twenty progressive modules.

Every learner moves through these modules sequentially unless the Adaptive Learning Engine validates sufficient prior mastery.

```
LEVEL 1
Foundations

↓

LEVEL 2
Basic Networking

↓

LEVEL 3
Intermediate Networking

↓

LEVEL 4
Advanced Networking

↓

LEVEL 5
Expert Networking
```

Progression is strictly sequential unless validated by the Adaptive Learning Engine.

---

# Learning Methodology

Every topic inside this curriculum follows the same instructional model.

1. Concept
2. Motivation
3. Internal Working
4. Visual Explanation
5. Real-world Analogy
6. Packet Flow Analysis
7. Protocol Analysis
8. Production Usage
9. Common Mistakes
10. Interview Perspective
11. Cloud Perspective
12. Revision Checklist

---

# Curriculum Structure

The curriculum contains five progressive learning levels.

| Level | Objective |
|---------|-----------|
| Foundation | Understand networking fundamentals |
| Basic | Learn network layers and protocols |
| Intermediate | Build practical networking knowledge |
| Advanced | Learn production networking systems |
| Expert | Master cloud-native and distributed networking |

---

# LEVEL 1 — FOUNDATIONS

## Objective

Develop a strong understanding of networking fundamentals before learning protocols, cloud networking, and distributed communication.

Learners should understand how computers communicate, why networks exist, and how the Internet is organized.

Recommended Duration

2 Weeks

Expected Outcome

The learner should confidently explain networking fundamentals and understand how data travels between systems.

---

## Module 1 — Introduction to Computer Networks

### Purpose

Introduce the fundamental concepts of computer networking and explain why interconnected systems are essential in modern computing.

### Major Areas

- What is a Computer Network?
- Evolution of Computer Networks
- Why Networks Exist
- Types of Networks
- Internet Overview
- Client-Server Model
- Peer-to-Peer Model
- Network Architecture
- Network Components
- Communication Models
- Real-world Applications

### Learning Outcomes

- Explain the purpose of computer networks.
- Differentiate networking models.
- Identify network components.
- Describe real-world networking applications.

### Interview Focus

- What is a Computer Network?
- Client-Server Architecture
- Peer-to-Peer Architecture
- Types of Networks

### Production Relevance

- Web Applications
- Mobile Applications
- Cloud Computing
- Enterprise Infrastructure
- Distributed Systems

### Common Mistakes

- Assuming the Internet is a single network.
- Confusing Client-Server and Peer-to-Peer models.
- Ignoring communication layers.

### Recommended Practice

- Study Internet architecture.
- Compare networking models.
- Draw communication diagrams.

### Unlocks

- Module 2 — Network Fundamentals

---

## Module 2 — Network Fundamentals

### Purpose

Understand the building blocks of networking, including transmission media, topologies, bandwidth, latency, and communication metrics.

### Major Areas

- Network Topologies
- Physical Media
- Wireless Communication
- Bandwidth
- Throughput
- Latency
- Jitter
- Packet Loss
- Duplex Communication
- Error Detection
- Network Reliability

### Learning Outcomes

- Explain network topologies.
- Compare communication media.
- Analyze network performance metrics.
- Understand transmission characteristics.

### Interview Focus

- Bandwidth vs Throughput
- Latency
- Jitter
- Packet Loss
- Network Topologies

### Production Relevance

- ISP Networks
- Cloud Infrastructure
- Enterprise Networks
- Data Centers

### Common Mistakes

- Confusing bandwidth with throughput.
- Ignoring latency.
- Assuming wireless is always slower.

### Recommended Practice

- Compare different topologies.
- Analyze latency examples.
- Solve networking metric questions.

### Unlocks

- Module 3 — OSI Model

---

## Module 3 — OSI Reference Model

### Purpose

Understand the seven-layer OSI model and the responsibilities of each networking layer.

### Major Areas

- Why OSI Model Exists
- Layered Architecture
- Seven Layers
- Encapsulation
- Decapsulation
- Protocol Interaction
- Data Units
- Layer Responsibilities
- Device Mapping

### Learning Outcomes

- Explain all seven OSI layers.
- Describe encapsulation.
- Identify protocols for each layer.
- Map networking devices to OSI layers.

### Interview Focus

- OSI Layers
- Encapsulation
- Decapsulation
- Layer Responsibilities

### Production Relevance

- Network Troubleshooting
- Protocol Design
- Cloud Infrastructure
- Enterprise Networking

### Common Mistakes

- Memorizing layers without understanding responsibilities.
- Confusing OSI with TCP/IP.

### Recommended Practice

- Draw OSI diagrams.
- Trace packet flow.
- Map protocols to layers.

### Unlocks

- Module 4 — TCP/IP Model

---

## Module 4 — TCP/IP Model

### Purpose

Understand the Internet protocol suite that powers modern communication across the Internet.

### Major Areas

- Internet Architecture
- TCP/IP Layers
- Internet Layer
- Transport Layer
- Application Layer
- Network Interface Layer
- OSI vs TCP/IP
- Encapsulation
- Packet Journey

### Learning Outcomes

- Explain TCP/IP architecture.
- Compare TCP/IP with OSI.
- Understand protocol layering.
- Trace packet movement.

### Interview Focus

- TCP/IP Model
- OSI vs TCP/IP
- Packet Journey

### Production Relevance

- Internet
- Cloud Platforms
- Backend Systems
- Kubernetes Networking

### Common Mistakes

- Assuming OSI is implemented directly.
- Confusing layers.

### Recommended Practice

- Compare OSI and TCP/IP.
- Trace packet encapsulation.

### Unlocks

- Module 5 — Network Devices

---

## Module 5 — Network Devices

### Purpose

Understand the hardware responsible for transmitting, routing, switching, and securing network traffic.

### Major Areas

- Hub
- Switch
- Router
- Bridge
- Repeater
- Gateway
- Modem
- Firewall
- Load Balancer (Introduction)
- Access Point
- Network Interface Card (NIC)

### Learning Outcomes

- Identify networking devices.
- Explain device responsibilities.
- Compare Layer 2 and Layer 3 devices.
- Understand traffic forwarding.

### Interview Focus

- Hub vs Switch
- Switch vs Router
- Gateway
- Firewall
- Load Balancer

### Production Relevance

- Enterprise Networks
- Cloud Infrastructure
- Kubernetes
- Data Centers
- Backend Systems

### Common Mistakes

- Confusing routers and switches.
- Assuming all devices work at the same OSI layer.
- Ignoring gateway functionality.

### Recommended Practice

- Compare networking devices.
- Draw enterprise network diagrams.
- Analyze packet forwarding examples.

### Unlocks

- LEVEL 2 — BASIC NETWORKING

# LEVEL 2 — BASIC NETWORKING

## Objective

Build a comprehensive understanding of how data is transmitted across networks by mastering the core networking layers, addressing mechanisms, transport protocols, and application-level communication.

Recommended Duration

3 Weeks

Expected Outcome

The learner should confidently explain how data travels from one computer to another, understand the responsibilities of each protocol layer, and analyze communication using real-world networking examples.

---

## Module 6 — Physical Layer

### Purpose

Understand how raw bits are transmitted over physical communication media and how hardware enables reliable signal transmission.

### Major Areas

- Physical Layer Responsibilities
- Digital Signals
- Analog Signals
- Signal Encoding
- Transmission Modes
- Simplex
- Half Duplex
- Full Duplex
- Copper Cables
- Fiber Optic Cables
- Wireless Media
- Bandwidth
- Frequency
- Attenuation
- Noise
- Repeaters
- Hubs

### Learning Outcomes

- Explain physical layer responsibilities.
- Compare transmission media.
- Differentiate transmission modes.
- Understand signal degradation.

### Interview Focus

- Transmission Modes
- Fiber vs Copper
- Bandwidth
- Noise
- Attenuation

### Production Relevance

- Data Centers
- ISP Infrastructure
- Enterprise Networks
- Cloud Infrastructure

### Common Mistakes

- Confusing bandwidth with throughput.
- Assuming wireless always performs worse than wired communication.
- Ignoring physical transmission limitations.

### Recommended Practice

- Compare transmission media.
- Analyze networking diagrams.
- Study enterprise network layouts.

### Unlocks

- Module 7 — Data Link Layer

---

## Module 7 — Data Link Layer

### Purpose

Understand how neighboring devices communicate reliably using frames, MAC addresses, switching, and error detection.

### Major Areas

- Data Link Layer Responsibilities
- Frames
- MAC Address
- Physical Address
- Ethernet
- CSMA/CD
- CSMA/CA
- Switching
- VLAN
- ARP
- Error Detection
- CRC
- Flow Control
- Layer-2 Switching
- MAC Address Table

### Learning Outcomes

- Explain frame transmission.
- Understand MAC addressing.
- Analyze Ethernet communication.
- Explain VLAN concepts.
- Understand ARP resolution.

### Interview Focus

- MAC Address
- Ethernet
- ARP
- VLAN
- CSMA/CD
- CRC

### Production Relevance

- Enterprise LANs
- Data Centers
- Campus Networks
- Layer-2 Infrastructure

### Common Mistakes

- Confusing MAC and IP addresses.
- Assuming switches use IP addresses.
- Misunderstanding ARP.

### Recommended Practice

- Trace ARP requests.
- Compare Ethernet switching.
- Analyze Layer-2 packet flow.

### Unlocks

- Module 8 — Network Layer

---

## Module 8 — Network Layer

### Purpose

Understand logical addressing, routing, and packet forwarding across interconnected networks.

### Major Areas

- Network Layer Responsibilities
- IPv4
- IPv6
- IP Addressing
- Public IP
- Private IP
- CIDR
- Subnetting
- Supernetting
- Network Address Translation (NAT)
- ICMP
- Routing
- Routers
- Default Gateway
- TTL
- Fragmentation

### Learning Outcomes

- Explain logical addressing.
- Perform subnet calculations.
- Compare IPv4 and IPv6.
- Understand routing fundamentals.
- Explain NAT and ICMP.

### Interview Focus

- IPv4 vs IPv6
- CIDR
- Subnetting
- NAT
- ICMP
- TTL

### Production Relevance

- Cloud Networks
- Kubernetes
- AWS VPC
- Azure VNets
- Google Cloud Networking

### Common Mistakes

- Confusing MAC and IP addressing.
- Incorrect subnet calculations.
- Misunderstanding NAT behavior.

### Recommended Practice

- Solve subnetting exercises.
- Analyze routing tables.
- Practice CIDR calculations.

### Unlocks

- Module 9 — Transport Layer

---

## Module 9 — Transport Layer

### Purpose

Understand reliable and unreliable communication, end-to-end delivery, and connection management.

### Major Areas

- Transport Layer Responsibilities
- TCP
- UDP
- Connection-Oriented Communication
- Connectionless Communication
- Ports
- Socket
- Three-Way Handshake
- Four-Way Handshake
- Flow Control
- Sliding Window
- Congestion Control
- Retransmission
- Reliability
- Multiplexing
- Demultiplexing

### Learning Outcomes

- Compare TCP and UDP.
- Explain connection establishment.
- Understand congestion control.
- Analyze transport reliability.
- Explain socket communication.

### Interview Focus

- TCP vs UDP
- Three-Way Handshake
- Four-Way Handshake
- Sliding Window
- Congestion Control
- Ports
- Socket

### Production Relevance

- REST APIs
- gRPC
- Database Communication
- Messaging Systems
- Video Streaming
- Online Gaming

### Common Mistakes

- Confusing reliability with speed.
- Assuming UDP is always inferior.
- Ignoring congestion control.

### Recommended Practice

- Trace TCP connections.
- Compare TCP and UDP use cases.
- Analyze packet captures.

### Unlocks

- Module 10 — Application Layer

---

## Module 10 — Application Layer

### Purpose

Understand the protocols and services that enable communication between software applications across the Internet.

### Major Areas

- Application Layer Responsibilities
- HTTP
- HTTPS
- DNS
- DHCP
- FTP
- SFTP
- SMTP
- POP3
- IMAP
- SSH
- Telnet
- SNMP
- NTP
- WebSocket
- gRPC (Introduction)
- MQTT (Introduction)

### Learning Outcomes

- Explain common application protocols.
- Compare HTTP and HTTPS.
- Understand DNS resolution.
- Analyze email protocols.
- Explain secure remote communication.

### Interview Focus

- HTTP vs HTTPS
- DNS
- DHCP
- SMTP
- FTP vs SFTP
- SSH
- WebSocket

### Production Relevance

- Web Applications
- Cloud Platforms
- APIs
- Kubernetes
- Microservices
- Backend Systems

### Common Mistakes

- Confusing DNS with DHCP.
- Assuming HTTPS is a separate protocol from HTTP.
- Ignoring TLS during HTTPS communication.

### Recommended Practice

- Trace DNS lookups.
- Analyze HTTP request-response cycles.
- Compare application protocols.

### Unlocks

- LEVEL 3 — INTERMEDIATE

---

# LEVEL 3 — INTERMEDIATE

## Objective

Master routing, switching, network services, security, and performance concepts required for backend engineering, cloud platforms, distributed systems, and modern production infrastructure.

## Recommended Duration

4 Weeks

## Expected Outcome

The learner should understand how enterprise and cloud networks operate, diagnose networking issues, and connect networking concepts to real-world software engineering systems.

## Module 11 — Routing

### Purpose

Understand how packets are forwarded across multiple interconnected networks using routing algorithms, routing tables, and dynamic routing protocols.

### Major Areas

- What is Routing?
- Routing Table
- Next Hop
- Static Routing
- Dynamic Routing
- Distance Vector Routing
- Link State Routing
- RIP
- OSPF
- BGP
- Default Route
- Route Aggregation
- Equal Cost Multi Path (ECMP)
- Policy-Based Routing
- Routing Convergence

### Learning Outcomes

- Explain how routers forward packets.
- Differentiate static and dynamic routing.
- Compare RIP, OSPF, and BGP.
- Analyze routing tables.
- Explain route convergence.

### Interview Focus

- Static vs Dynamic Routing
- RIP vs OSPF
- OSPF vs BGP
- Route Aggregation
- ECMP

### Production Relevance

- Internet Backbone
- Cloud Networking
- Enterprise Networks
- ISP Infrastructure
- Kubernetes Networking

### Common Mistakes

- Confusing switching with routing.
- Assuming BGP is used only on the Internet.
- Ignoring routing convergence time.

### Recommended Practice

- Read routing tables.
- Compare routing protocols.
- Analyze packet forwarding scenarios.

### Unlocks

- Module 12 — Switching

---

## Module 12 — Switching

### Purpose

Understand how Layer-2 networks efficiently forward frames using MAC addresses and switching technologies.

### Major Areas

- Switching Fundamentals
- Layer-2 Switching
- MAC Learning
- CAM Table
- Flooding
- Forwarding
- VLAN
- Trunk Ports
- Access Ports
- Inter-VLAN Routing
- Spanning Tree Protocol (STP)
- Rapid STP
- Link Aggregation
- Broadcast Domains
- Collision Domains

### Learning Outcomes

- Explain switch operation.
- Understand VLAN implementation.
- Analyze STP behavior.
- Differentiate broadcast and collision domains.
- Explain Layer-2 forwarding.

### Interview Focus

- Switch vs Router
- VLAN
- STP
- CAM Table
- Broadcast Domain
- Collision Domain

### Production Relevance

- Enterprise Networks
- Data Centers
- Campus Networks
- Cloud Infrastructure

### Common Mistakes

- Confusing VLANs with subnets.
- Assuming switches eliminate broadcasts.
- Ignoring spanning tree loops.

### Recommended Practice

- Configure VLAN scenarios.
- Trace frame forwarding.
- Analyze switching diagrams.

### Unlocks

- Module 13 — Network Services

---

## Module 13 — Network Services

### Purpose

Understand the essential services that enable devices and applications to communicate reliably across modern networks.

### Major Areas

- DNS
- Recursive Resolution
- Authoritative DNS
- DNS Records
- A Record
- AAAA Record
- CNAME
- MX
- TXT
- DHCP
- DHCP Lease
- NAT
- PAT
- Proxy Server
- Reverse Proxy
- Load Balancer
- CDN Fundamentals

### Learning Outcomes

- Explain DNS resolution.
- Understand DHCP allocation.
- Differentiate NAT and PAT.
- Explain reverse proxy architecture.
- Understand CDN fundamentals.

### Interview Focus

- DNS Resolution
- DHCP
- NAT
- Reverse Proxy
- CDN

### Production Relevance

- AWS Route 53
- Cloudflare
- Nginx
- HAProxy
- Kubernetes Ingress
- Enterprise Infrastructure

### Common Mistakes

- Confusing DNS and DHCP.
- Assuming reverse proxies are load balancers.
- Ignoring DNS caching.

### Recommended Practice

- Trace DNS lookups.
- Study CDN request flow.
- Compare proxy architectures.

### Unlocks

- Module 14 — Network Security

---

## Module 14 — Network Security

### Purpose

Understand how modern networks ensure confidentiality, integrity, authentication, and secure communication.

### Major Areas

- Security Fundamentals
- CIA Triad
- Authentication
- Authorization
- Encryption
- Symmetric Encryption
- Asymmetric Encryption
- SSL
- TLS
- HTTPS
- SSH
- VPN
- IPSec
- Firewall
- IDS
- IPS
- DDoS
- Man-in-the-Middle Attack
- ARP Spoofing
- DNS Spoofing
- Zero Trust Networking

### Learning Outcomes

- Explain secure communication.
- Compare SSL and TLS.
- Understand VPN technologies.
- Analyze network attacks.
- Explain Zero Trust concepts.

### Interview Focus

- SSL vs TLS
- HTTPS
- VPN
- Firewall
- DDoS
- MITM
- Zero Trust

### Production Relevance

- Cloud Security
- Enterprise Networks
- Banking Systems
- Kubernetes
- API Security

### Common Mistakes

- Confusing encryption with authentication.
- Assuming HTTPS encrypts everything.
- Ignoring certificate validation.

### Recommended Practice

- Study TLS handshake.
- Analyze HTTPS requests.
- Compare security architectures.

### Unlocks

- Module 15 — Network Performance

---

## Module 15 — Network Performance & Optimization

### Purpose

Understand how production systems optimize network communication to achieve scalability, reliability, and high performance.

### Major Areas

- Throughput
- Latency
- RTT
- MTU
- MSS
- Buffering
- Queueing
- Congestion
- Congestion Avoidance
- QoS
- Traffic Shaping
- Rate Limiting
- Compression
- Connection Pooling
- Keep Alive
- HTTP/2 Multiplexing
- HTTP/3
- QUIC

### Learning Outcomes

- Analyze network performance.
- Explain congestion control.
- Understand QoS mechanisms.
- Compare HTTP protocol versions.
- Optimize application communication.

### Interview Focus

- RTT
- MTU
- MSS
- HTTP/2
- HTTP/3
- QUIC
- QoS

### Production Relevance

- CDN
- Cloud Platforms
- Kubernetes
- API Gateways
- High-Performance Backend Systems
- Distributed Systems

### Common Mistakes

- Optimizing bandwidth while ignoring latency.
- Confusing MTU and MSS.
- Assuming HTTP/3 simply replaces TCP.

### Recommended Practice

- Analyze network traces.
- Compare HTTP protocol versions.
- Study production performance incidents.

### Unlocks

- LEVEL 4 — ADVANCED

---

# LEVEL 4 — ADVANCED

## Objective

Master cloud-native networking, distributed communication, modern Internet architecture, and production networking patterns used in large-scale software systems.

## Recommended Duration

4–5 Weeks

## Expected Outcome

The learner should confidently connect networking principles with cloud computing, distributed systems, microservices, Kubernetes, and large-scale backend engineering.

## Module 16 — Cloud Networking

### Purpose

Understand how networking is implemented in modern cloud platforms and how cloud-native applications communicate securely and efficiently.

### Major Areas

- Cloud Networking Fundamentals
- Virtual Private Cloud (VPC)
- Virtual Networks
- Public Subnets
- Private Subnets
- Route Tables
- Internet Gateway
- NAT Gateway
- Bastion Host
- Security Groups
- Network ACLs
- VPC Peering
- Transit Gateway
- VPN Gateway
- Direct Connect
- ExpressRoute
- Hybrid Cloud Networking
- Multi-Region Networking

### Learning Outcomes

- Explain cloud networking architecture.
- Design secure virtual networks.
- Differentiate Security Groups and Network ACLs.
- Understand hybrid cloud connectivity.
- Analyze traffic flow inside cloud environments.

### Interview Focus

- AWS VPC
- Public vs Private Subnet
- Security Groups
- NACL
- NAT Gateway
- Internet Gateway
- VPC Peering
- Transit Gateway

### Production Relevance

- AWS
- Azure
- Google Cloud Platform
- Kubernetes
- Enterprise Cloud Infrastructure

### Common Mistakes

- Confusing Security Groups with NACLs.
- Deploying databases in public subnets.
- Misconfiguring route tables.

### Recommended Practice

- Design a multi-tier cloud network.
- Trace request flow through a VPC.
- Compare networking services across AWS, Azure, and GCP.

### Unlocks

- Module 17 — Distributed Networking

---

## Module 17 — Distributed Networking

### Purpose

Understand how modern distributed systems communicate reliably across multiple services, regions, and clusters.

### Major Areas

- Distributed Communication
- Service Discovery
- API Gateway
- Reverse Proxy
- Load Balancer
- Service Mesh
- East-West Traffic
- North-South Traffic
- Kubernetes Networking
- Ingress Controller
- Egress Controller
- Overlay Networks
- DNS-Based Service Discovery
- Circuit Breaker
- Retry Mechanisms
- Distributed Tracing
- Sidecar Pattern

### Learning Outcomes

- Explain distributed communication models.
- Understand service discovery.
- Compare API Gateway and Load Balancer.
- Analyze Kubernetes networking.
- Understand service mesh architecture.

### Interview Focus

- API Gateway
- Service Mesh
- Kubernetes Networking
- Ingress
- Load Balancer
- Service Discovery

### Production Relevance

- Kubernetes
- Istio
- Linkerd
- Envoy
- Microservices
- Cloud Native Platforms

### Common Mistakes

- Confusing API Gateway with Reverse Proxy.
- Ignoring service discovery.
- Misunderstanding east-west traffic.

### Recommended Practice

- Draw a microservices communication diagram.
- Analyze Kubernetes request flow.
- Compare service mesh implementations.

### Unlocks

- Module 18 — Modern Internet Protocols

---

## Module 18 — Modern Internet Protocols

### Purpose

Master modern communication protocols used by production applications, cloud platforms, and distributed backend systems.

### Major Areas

- HTTP/1.1
- HTTP/2
- HTTP/3
- QUIC
- WebSocket
- Server-Sent Events (SSE)
- gRPC
- Protocol Buffers
- MQTT
- AMQP
- Kafka Networking
- Redis Protocol
- GraphQL over HTTP
- WebRTC (Introduction)

### Learning Outcomes

- Compare modern communication protocols.
- Understand persistent connections.
- Explain multiplexing.
- Analyze real-time communication.
- Select appropriate protocols for production systems.

### Interview Focus

- HTTP/2 vs HTTP/3
- QUIC
- WebSocket
- gRPC
- MQTT
- Kafka Communication

### Production Relevance

- Backend APIs
- Streaming Platforms
- IoT
- Messaging Systems
- AI Platforms
- Cloud Services

### Common Mistakes

- Confusing WebSocket with HTTP polling.
- Assuming HTTP/3 uses TCP.
- Ignoring protocol overhead.

### Recommended Practice

- Compare protocol architectures.
- Analyze protocol selection scenarios.
- Study production communication patterns.

### Unlocks

- LEVEL 5 — EXPERT

---

# LEVEL 5 — EXPERT

## Objective

Apply networking concepts to large-scale production systems, cloud-native architectures, and interview scenarios expected at top product-based companies.

Recommended Duration

2–3 Weeks

Expected Outcome

The learner should confidently analyze, design, troubleshoot, and explain networking architectures used in modern software engineering environments.

---

## Module 19 — Networking in Production Systems

### Purpose

Bridge networking theory with real-world production architectures used by large-scale software platforms.

### Major Areas

- Internet Request Lifecycle
- CDN Architecture
- Reverse Proxy
- Global Load Balancing
- Geo Routing
- Edge Computing
- Cache Networks
- Multi-Region Deployment
- Disaster Recovery Networking
- High Availability
- Fault Tolerance
- Network Observability
- Packet Monitoring
- Distributed Logging
- Network Metrics
- Capacity Planning

### Learning Outcomes

- Explain end-to-end request flow.
- Design highly available network architectures.
- Analyze production networking failures.
- Understand observability in distributed systems.
- Apply networking principles to scalable backend systems.

### Interview Focus

- CDN
- Reverse Proxy
- Load Balancing
- Multi-Region Architecture
- High Availability
- Disaster Recovery

### Production Relevance

- Netflix
- Google
- AWS
- Microsoft Azure
- Uber
- Stripe
- Cloudflare

### Common Mistakes

- Ignoring latency across regions.
- Treating networking as separate from backend design.
- Overlooking observability.

### Recommended Practice

- Design a global application architecture.
- Trace request flow from browser to database.
- Analyze production incident case studies.

### Unlocks

- Module 20 — Expert Interview Preparation

---

## Module 20 — Expert Interview Preparation

### Purpose

Consolidate all networking knowledge required for software engineering interviews and production engineering roles.

### Major Areas

- Networking Revision Roadmap
- Interview Question Patterns
- Protocol Comparison Matrix
- Troubleshooting Methodology
- Packet Flow Analysis
- Case Studies
- System Design Networking
- Cloud Networking Questions
- Backend Networking Questions
- Company-Specific Expectations
- Mock Interviews
- Production Scenarios

### Learning Outcomes

- Answer networking interview questions confidently.
- Explain protocol trade-offs.
- Solve production networking problems.
- Connect networking concepts with backend engineering.
- Demonstrate system-level reasoning.

### Interview Focus

- FAANG Networking Questions
- Cloud Networking
- System Design Networking
- Production Debugging
- Protocol Selection
- Distributed Communication

### Production Relevance

- Software Engineering Interviews
- Backend Engineering
- Distributed Systems
- Cloud Engineering
- Site Reliability Engineering

### Common Mistakes

- Memorizing protocols without understanding.
- Ignoring real-world trade-offs.
- Focusing only on theory.

### Recommended Practice

- Solve networking case studies.
- Conduct mock interviews.
- Explain packet flow on a whiteboard.

### Unlocks

- Distributed Systems
- Cloud Architecture
- Site Reliability Engineering
- Advanced Backend Engineering
- High-Level Design

---

# Exit Criteria

A learner completing this curriculum should be able to:

- Explain the complete lifecycle of network communication.
- Understand the OSI and TCP/IP models in depth.
- Configure and troubleshoot fundamental networking concepts.
- Analyze routing, switching, DNS, DHCP, and transport protocols.
- Apply networking principles to cloud platforms and distributed systems.
- Design scalable, secure, and highly available network architectures.
- Confidently answer networking interview questions.
- Connect networking concepts with backend engineering and system design.

---

# Prerequisites

- Programming Fundamentals
- Java
- Data Structures & Algorithms
- Operating Systems

---

# Unlocks

Completion of this curriculum unlocks:

- Distributed Systems
- Cloud Computing
- Kubernetes
- DevOps
- Site Reliability Engineering
- Microservices
- Low-Level Design
- High-Level Design
- Backend Engineering
- System Design
- Production Engineering

---

# Curriculum Maintenance Rules

- This curriculum is the canonical source of truth for Computer Networks within PrepOS.
- Every module must follow the canonical subject template defined in `00-subject-template.md`.
- New topics must preserve the learning progression from Foundation → Expert.
- Networking concepts should emphasize production engineering, cloud-native systems, and distributed architectures in addition to interview preparation.
- Any additions or modifications must maintain backward compatibility with the curriculum generator and roadmap pipeline.