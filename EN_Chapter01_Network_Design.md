# Chapter 1: Network Design

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapters 1–2 (pp. 81–140)
>
> Terminology follows the English edition. Sections mirror the Chinese chapter one-to-one, so the two can be read side by side.

---

## Topics Covered

- **Network design fundamentals**: mindset, requirements, design use cases, the business, constraints
- **Network design principles**: pervasive security, scalability, availability, cost, manageability
- **Network design techniques**: fault isolation, information hiding, modularity, hierarchy
- **Network design pitfalls**: assumptions, over-engineering, the best-practice fallacy

---

## Chapter Overview: Ten Counterintuitive Lessons

There is no protocol, no command line and no topology in this chapter, yet it is the only one where a misreading poisons the following seventeen. The reason is simple: **once the methodology drifts, the more fluent you are with technology, the faster and the more expensively you go wrong.**

**1. Knowing how to configure is not knowing how to design.** Configuration answers "how does this device do it"; design answers "why does this device exist, and what happens when it fails."

**2. A requirement is not the sentence the customer said; it is the phenomenon you have verified.** "We don't have enough bandwidth" is often packet loss; "we need dual cores" is often a single-homed uplink. **An unmeasured requirement is merely an opinion.**

**3. Bottom-up almost always fails, yet abandoning it also fails.** Starting from technology ("SD-WAN first", "vendor A first") is usually overturned by the business within six months; ignoring the current state means the design never lands. The correct posture is **push requirements top-down, validate feasibility bottom-up**.

**4. Redundancy is not availability.** Two links in one conduit, two switches on one PDU, two carriers sharing one municipal duct — all "dual" on the diagram, all "single" in front of a failure. **Redundancy is measured in failure domains, not in device counts.**

**5. A "best practice" is somebody else's conclusion drawn under somebody else's constraints.** It deserves a hearing, but not a copy. Ask whether its constraint set (scale, budget, team, business model) matches yours; if not, it is an assumption awaiting validation.

**6. Security is not a module; it is a property of every design decision.** One decision that treats security as "we'll add a firewall later" already caps the security of the whole architecture.

**7. Every additional nine costs more than the previous one.** From 99% to 99.9% may only need redundant power supplies; from 99.99% to 99.999% it touches process, drills, change management and supply chain.

**8. Cost is not the purchase price.** Real cost is TCO: acquisition + licenses + power + rack space + people + training + migration risk + exit cost five years out. Many "cheaper" options are expensive on Day 2.

**9. Defining what is out of scope matters more than defining what is in scope.** Scope creep is the most common way design projects die.

**10. Recording why you did not choose X is worth more than recording why you chose Y.** In a year someone will ask "why didn't we go with SD-WAN", and by then the people who remember have moved on.

> **The chapter in one sentence**: **Design is the act of making traceable, reversible decisions with incomplete information.** Technology is the material of those decisions, not the decision itself.

---

## Foundation Topics

Designing a large-scale network to meet today's dynamic business and IT requirements is a complex task. This is especially true when the network was built years ago around older technologies and requirements, and the business now wants to adopt new IT technologies and architectures that the existing network may not support. The network designer therefore has to apply a structured approach to design.

### Two Common Approaches to Network Analysis and Design

**Top-Down Approach**: decomposes the design task to simplify it, keeps the effort focused on the scope of the design, and executes it in a more controlled manner. It ultimately helps the designer view the solution from the business perspective.

**Bottom-Up Approach**: starts with the selection of network technologies and design models. This carries a high risk of design failure, because the resulting network may not meet business or application requirements.

For a successful strategic design, more emphasis must be placed on the business: business priorities, drivers, outcomes, technical objectives, and the current and future services and applications. In today's networks, business requirements drive IT and network initiatives.

---

## Network Design Fundamentals

The design fundamentals are the building blocks every network designer must understand and know how to use:

1. **Mindset**
2. **Requirements**
3. **Design Use Cases**
4. **The Business**
5. **Constraints**
6. **"Why"**

### Mindset

> Above all else, your mindset is the single most critical factor in doing network design well. Knowing the technology is necessary, but it is the comparatively easy part of the journey. Many people who do network design do not have the right design mindset.

An implementation mindset does not work for network design; you need a network design mindset to succeed in real design scenarios.

### Functional Requirements

Functional requirements form the basis of any system design because they define system and technology functions. Specifically, they identify, from a technical standpoint, what the technology or system will deliver to the business.

For example, an MPLS-enabled service provider might state a functional requirement such as: "the provider edge routers must send VoIP traffic over 10G fiber links and data traffic over OC-48 links." This implies the network needs a mechanism to send different traffic types over different paths, such as MPLS Traffic Engineering (MPLS-TE).

Functional requirements are sometimes called **behavioral requirements**, because they describe **what** the system does.

> ⚠️ A design that does not meet the business functional requirements is a bad design. In reality, however, not all functional requirements are handed to the designer; some are derived indirectly. Most of the time, discovering and documenting them is the designer's job.

### Technical Requirements

Technical requirements are the technical aspects the infrastructure must provide in terms of security, availability and integration. They are commonly referred to as **nonfunctional requirements**. Examples include:

- Higher levels of network availability (for example, First Hop Redundancy Protocols [FHRP])
- Support for integration with network tools and services (for example, a NetFlow collector or a RADIUS authentication server)
- Network infrastructure security mechanisms (for example, control plane protection or infrastructure ACLs)

> Technical requirements help the designer specify the required technical specifications (features and protocols) and the software releases that support them, and sometimes influence the hardware platform selection.

### Application Requirements

Application requirements are the deciding factor and, in most cases, constrain the design. If an application requires Layer 2 connectivity, the design is limited to Layer 2 protocols across data centers (for example, extended VLANs).

From a business perspective, user experience is one of the top priorities any IT or network design must satisfy. End-user categories include:

| User Type | Description |
|-----------|-------------|
| **Customer** | An individual (for example, a bank customer) or a collective (for example, the customers of an MPLS service provider). Satisfaction directly affects reputation and revenue |
| **Internal User** | Employees. Their productivity translates into business efficiency and is tied to business success and revenue |
| **Business Partner** | An entity or organization with which goals are achieved jointly. Efficient partner interaction strengthens business success |

> A network that cannot deliver the experience users expect means the primary business objective cannot be achieved, and IT will be seen by the business as a **cost center** rather than a **business enabler**.

**Example**: a financial services company wants to differentiate itself with video communication to contact-center agents. If the network team does not account for the network requirements of video, the application will likely fail to deliver the expected experience.

#### Application Requirements Drive Functional Requirements

If a service provider has an SLA requiring one-way delay below 150 ms and packet loss below 1% for VoIP, that application requirement drives the functional requirement on the PE devices: use a technology that can deliver the SLA, such as CBTS MPLS-TE with Fast Reroute (FRR).

The designer should also consider:

1. How much network traffic does the application require?
2. How business-critical is the application, and what service levels does it need?
3. Does the application have separation requirements driven by regulation or corporate security policy?
4. What are the characteristics of the application?
5. How long does the application need to reset its state or session after losing connectivity?

### Building the Design Requirements

> **Example scenario**: a national retail company plans to expand internationally over the next 12 months by adding several sites. With its current IT infrastructure it faces high costs to manage and maintain two separate data and voice networks. The business also wants to invest in technologies that improve efficiency and employee productivity.

### Design Scope

The designer must carefully analyze and evaluate the design scope before gathering information and planning the design. It is essential to determine whether the task is a **Greenfield** network or an existing production network, and whether the design spans a single network module or multiple modules.

| Design Scope | Example of Detailed Scope |
|--------------|---------------------------|
| **Enterprise campus** | Rolling out IP Telephony enterprise-wide may require redesigning VLANs, QoS and so on across LAN, WAN, DC and remote-access edge |
| **Campus only** | Adding multi-tenancy to the campus only requires designing VLAN, IP and path isolation across campus LANs |
| **Optimizing the enterprise edge** | Adding redundant links for remote access may require redesigning the WAN module, remote-site design and overlay tunnels |

> ⚠️ **Design point**: identifying the scope is critical. You may face a very large network while the actual design effort is only about adding and integrating one new data center — yet the design must still start from the whole network ("holistic approach").

It is equally important to identify **what is out of scope**, which prevents scope creep from blocking the project.

### Design Use Cases

A successful design requires correctly identifying the specific use case.

#### 1. Greenfield

The best situation a designer can face: a blank sheet, designing and building the environment from scratch. Make sure that what you propose is genuinely what the business needs.

#### 2. Brownfield

Most design scenarios involve some form of brownfield work — an existing environment carrying production traffic. Spend time discovering the current state and assessing it properly; this is not only technical discovery of protocols and diagrams, but also discovery of the business and its direction.

Once a design decision is made, prepare for migration: limit potential failure and rely on design fundamentals, principles and techniques.

#### 3. Adding a Technology or Application

Adding a technology or application can be very complex. The scope covers the impact of the addition on the existing network. Will the addition break anything? Application requirements in terms of traffic patterns, convergence time and latency must be considered.

#### 4. Replacing a Technology

Replacing a technology covers the many options for replacing an existing technology to meet a specific requirement — WAN technology, routing protocol, security mechanism, underlying core technology, and so on. The impact of the new technology on the current design (improved scalability, or a potential conflict with existing application requirements) forces the designer to adjust the design.

> ⚠️ Make sure you are replacing or adding technology for the right reasons. Deploying SD-WAN to replace a WAN architecture without a solid justification is wrong. Ensure there is a direct business reason and a properly tested migration plan. Migrating from OSPF to EIGRP should come with a plan listing every step, each with verification tasks and a rollback plan.

#### 5. Merge or Divest

**Merger**: two independent enterprises combine into one with an end-to-end architecture. Watch for overlapping technologies — for example, overlapping subnets. Most companies use RFC 1918 space (10.0.0.0/8, 172.16.0.0/12 or 192.168.0.0/16). Where overlap occurs, define a short-term and a long-term plan. Short term may involve NAT; long term may involve renumbering during a network refresh. Consolidate where possible — if the two companies have four data centers, merge to two (while remembering you may still need four).

**Divestment**: the most difficult use case. Forced to split an architecture, you are left with two or more incomplete systems. Ensure every remaining business can still operate along its own direction; each one has to keep running and, in most cases, keep earning.

#### 6. Scaling a Network

The scaling use case covers different levels of scalability, including physical topology and Layer 2 and Layer 3 scalability considerations. Is the growth planned or organic? Is the growth causing problems? Should the designer stop and redesign the network to accommodate growth? Which design model scales best?

#### 7. Design Failure

Nine times out of ten, the design failure use case is why you were called in. Something is broken and must be fixed. A simple technical example is misalignment between Spanning Tree Protocol (STP) and First Hop Redundancy Protocol (FHRP) root roles: if the STP root bridge and the FHRP default gateway are not aligned on the right devices, suboptimal routing follows and eventually the design fails.

### The Business

> Why do we make network design decisions? As designers, everything we do is for the businesses, companies and organizations we support. Specifically, we make decisions so that those businesses can make money.

Not every organization exists to make a profit. Non-profits focus on covering expenses and reducing day-to-day cost; in the public sector many organizations focus on delivering a specific service or outcome rather than on earning.

> 💡 Documenting design decisions and their rationale is becoming standard practice. It lets every team member — past, present and future — understand why a feature, design option or capability was implemented. Remembering why a decision was made six months ago is far easier than remembering why a routing tweak was added two years ago at 2 a.m. during a maintenance window.

### Constraints

When we start designing for a customer, the slate is clean — no requirements, no rules. As we interview the customer we learn the requirements and, more importantly, the specific constraints that limit us. Constraints fall into three categories:

| Constraint Type | Description | Example |
|-----------------|-------------|---------|
| **Business** | Budget limits, staffing, contractual constraints | Insufficient budget, lack of staff with the required skills, contractual scope or timeline limits |
| **Application** | Limits imposed by how the application was written | Requires Layer 2 connectivity, hard-coded IP addresses, clustering that requires multicast |
| **Technical** | Limits of a specific vendor's hardware or solution | Locked to a vendor, prohibited from proprietary features, dependent on a proprietary solution that cannot be migrated |

#### The Most Common Design Constraints

1. **Cost**: the most common limiting factor. Treat cost as a design constraint only when the requirements explicitly call it out, or when it is the tiebreaker between two comparable options. Do not assume technology A is more expensive than B — MPLS circuits are not automatically more expensive than Internet circuits.
2. **Time**: if the project has a completion deadline, time may be the key constraint on technology or architecture choices.
3. **Location**: location introduces indirect limits. A remote site may be in an area without fiber, leaving wireless as the only option.
4. **Infrastructure**: legacy equipment with no refresh plan may be incompatible with new features or protocols.
5. **Staff Expertise**: if the staff lack experience with the new technology there are two choices: (a) train them — risky, because inexperience lengthens problem resolution; or (b) hire experienced staff — usually expensive.

### "Why"

> You often hear a customer say "that is a requirement", but when you ask "why?", they cannot give a valid reason. Use the "five whys" concept — keep asking "why" like a five-year-old until you reach an answer you can understand and appreciate.

Toyota used the "five whys" system to investigate production problems, asking "why" five times to reveal the root cause.

As a designer you need to determine why the business truly needs the solution. The questions below contain no "why" but serve the same purpose:

- What problem are you solving with this technology?
- What are your staff's/customers' workflows today?
- How will this technology change those workflows?
- How will your business (governance, policy, process and culture) evolve because of this technology?

---

## Network Design Principles

The design principles are:

1. **Security**
2. **Scalability**
3. **Availability**
4. **Cost**
5. **Manageability**

### Unstated Requirements

> Customers increasingly do not state their specific requirements. They assume them, and as a designer you must work out which requirements matter for the design. You must not only identify them but also determine the level of each — does the network need to survive a single failure or a double failure?

Every design principle has effectively become an unstated requirement.

### Pervasive Security

Historically security was not treated as a design principle. Because of its impact on the business overall, it is now included as one.

**What if the network is compromised? What if data integrity is violated?**

- Business reputation is damaged
- Customers lose trust
- The business loses money and revenue
- The business no longer meets compliance standards and may be fined or shut down
- In extreme cases, the business fails

#### Three Security Models

| Model | Characteristics |
|-------|-----------------|
| **Perimeter Security** | Also called the "turtle shell" model. Firewalls at the perimeter, nothing inside. East-west traffic is wide open and insider threats flourish |
| **Session and Transaction Security** | Evolved from perimeter security. Users and devices are pinned down; east-west traffic is protected dynamically based on device, user, location and need. 100% authentication plus 100% authorization of every session and transaction |
| **Zero Trust Architecture** | Adds real-time capture and analytics so that AI/ML decisions can be made in real time. Every device, user, application, server, service and resource — even the data itself — is assigned a trust score derived from what the analytics engine observes |

### Availability

Availability encompasses redundancy, resilience and reliability:

| Concept | Definition |
|---------|------------|
| **Redundancy** | Multiple resources performing the same function/role, so one takes over when another fails |
| **Resilience** | The ability of the network to switch over automatically when a failure occurs |
| **Reliability** | The degree to which data travels from source to destination correctly and within the expected time |

> As the required level of availability rises, so do complexity and cost. Eliminating single points of failure versus double points of failure: the latter grows cost and complexity exponentially.

**How much redundancy is too much?** When the added complexity and cost are not worth the corresponding gain in availability. Eight parallel Layer 2 or Layer 3 links between two points make no sense — two is the standard, four needs justification, five or more adds far more complexity than benefit.

### Scalability

Scalability ensures the design can accommodate business growth:

- Does the network support scaling up (more capability per device)?
- Does it support scaling out (more devices)?
- Is growth planned or organic?
- Does the current design need to be redesigned before growth happens?

### Cost

Cost is one of the design constraints. The designer needs to understand the following financial concepts:

| Concept | Definition |
|---------|------------|
| **CAPEX** | Capital expenditure — one-off investment in equipment, facilities and so on |
| **OPEX** | Operating expenditure — day-to-day operating and maintenance cost |
| **TCO** | Total cost of ownership — CAPEX plus OPEX |
| **ROI** | Return on investment — the ratio of benefit to cost for an investment |

### Manageability

Manageability covers how well a design can be operated day to day. A technically perfect design that cannot be managed is not a good design. It includes:

- Ease of monitoring and troubleshooting
- Degree to which configuration management is simplified
- Fit with the operations team's skills

---

## Network Design Techniques

### Fault Isolation

Through modular and hierarchical design, ensure that a failure in one module or layer does not spread to the others.

### Information Hiding

Through route summarization, area design and similar mechanisms, reduce the amount of routing information propagated, improving scalability and convergence.

### Modularity

Divide the network into functional modules, each designed and managed independently. Benefits include fault isolation, scalability, manageability and flexibility.

### Hierarchy

Hierarchical design splits the network into core, distribution and access layers, each with clear responsibilities.

---

## Network Design Pitfalls

### 1. Assumptions

> As designers we tend to make assumptions based on our own experience — for example, that MPLS is more expensive than Internet, or that one technology is better than another. Do not make assumptions without factual support.

### 2. Over-Engineering (Gold Plating)

> Over-engineering means adding unnecessary features, redundancy or complexity. A design should solve the current problem, no more and no less, unless the requirements say otherwise.

### 3. The Best-Practice Fallacy

> A "best practice" may not apply to every scenario. The designer must understand the reasoning and the applicable conditions behind each best practice instead of applying it blindly.

---

## Case Studies

### Case 1: "The network is slow" is usually not a bandwidth problem

**Background**: at a new university campus, staff and students complain that the teaching system is slow. Operations produce a monitoring chart: peak utilization of the core egress is only 40% — "bandwidth is clearly sufficient".

**Disagreement**: one side wants a bigger leased line (CNY 400k per year), the other wants to investigate the application first.

**What the investigation found**:

| Check | Finding |
|-------|---------|
| Egress utilization | 40% average, but a **3–5 second 100% burst every minute** — invisible to 5-minute averaging |
| Switch queues | Output drops on the uplink at peak |
| Application behavior | Each page load issues 60+ concurrent small requests, extremely sensitive to loss |

**Root cause**: bandwidth was not the bottleneck; **bursty traffic plus insufficient queue buffering** caused loss and repeated TCP retransmission. The real requirement was queueing/shaping and better concurrency behavior, not more bandwidth.

**Outcome**: QoS queue tuning plus an uplink port upgrade — CNY 30k — solved it.

> 💡 **Lesson**: **a requirement is not what the user says, it is what measurement confirms.** 40% average utilization was an **assumption**, not evidence.

---

### Case 2: Does a 200-person branch need "dual cores"?

**Background**: a new 200-person branch, mostly office work plus video conferencing. The branch manager demands "dual cores, dual uplinks, dual carriers — the same standard as headquarters".

**Checking each demand against requirements**:

| Demand | Requirement basis | Verdict |
|--------|-------------------|---------|
| Dual core switches | A single core failure means 4 hours of downtime (spare-parts lead time) | Valid — but achievable at low cost with stacking or a redundant pair |
| Dual carrier circuits | No carrier fiber cut ever recorded at this campus | **Not valid** — single circuit plus 4G/5G backup instead |
| Dual-link load sharing | Peak traffic 180 Mbps; one 1G link is enough | **Not valid** — becomes backup rather than load sharing |

**Outcome**: cost dropped from CNY 2.1M to CNY 850k with the same availability target (under 4 hours of downtime per year).

> 💡 **Lesson**: **"the same as headquarters" is not a requirement, it is a habit.** The best-practice trap and over-engineering both show up in real life under the name of standardization.

---

## Lessons Learned

| Lesson | Explanation |
|--------|-------------|
| **Quantify requirements and match metrics to the symptom** | 5-minute averages hide 3-second bursts (Case 1). Monitoring granularity must match the time scale of the user's complaint |
| **Redundancy is decided by failure domain and business impact** | Do not ask "what is the HQ standard"; ask "if this device fails, how much business stops for how long" (Case 2) |
| **Every requirement must be traceable** | A requirement that cannot be traced to a business objective usually comes from habit or a vendor deck and should be challenged |
| **Push top-down, validate bottom-up** | Requirements come down from the business, the solution is verified upward against current capability |
| **Complexity must justify itself** | For every added protocol layer or feature, ask "does the failure it prevents outweigh the risk it introduces?" |
| **Ask who maintains it on Day 2** | A design the team cannot operate becomes technical debt the day it goes live |
| **Record rejected options and why** | "Why not X" is often more valuable than "why Y", and it is the basis for future change |

---

## Design Scenarios (3)

> How to use: read only the **Scenario**, write your own answers to the three questions, then read the **Suggested approach**. It is not an answer key but the **skeleton of a decision**.

### Scenario 1: "One standard for the whole company"

**Scenario**: a group has one headquarters (1,200 people), one R&D center (800) and 37 sales offices (8–40 people). The new CIO proposes "the same reference architecture, the same core model and the same dual-carrier circuit at every site, for ease of management". Operations supports it: "when something breaks, knowing one place is enough".

**What you know**: the 37 offices cost CNY 42k per year each in network spend; over the past three years link failures caused 6 outages at offices, the longest 3 hours (sales can fall back to phone hotspots); the cost of one hour of downtime at HQ and at the R&D center is CNY 1.8M and CNY 400k respectively.

**Questions**:

1. What is the real requirement behind "one standard"?
2. Which parts can be standardized, and which must be tiered?
3. What are the cost and the risk of the CIO's proposal?

**Suggested approach**:

- **The real requirement is "reduce management complexity", not "identical architecture".** Complexity can be reduced with configuration templates, centralized monitoring and automated audits without buying the same box everywhere.
- **Availability must be tiered by business impact.** CNY 1.8M per hour at HQ versus an office outage that a phone hotspot can carry for 3 hours — the targets differ by two or three orders of magnitude; a single redundancy model necessarily wastes at one end and under-delivers at the other.
- **What can be standardized is a standardized option set**: three tiers of templates (micro/small/medium), a common addressing plan, a common management plane and configuration baseline. **What must not be standardized is capacity and redundancy level.**
- **37 dual circuits cost roughly CNY 600–700k more per year**, while the risk it removes is far below the benefit of one extra link at HQ — over-engineering in its classic form.
- **How to land it**: give the CIO a tiered proposal plus a three-year TCO comparison plus a table of "what an outage at each site class costs" — not an objection.

---

### Scenario 2: Network integration after an acquisition

**Scenario**: Company A acquires Company B. A uses 10.0.0.0/8; so does B. A's core is multi-area OSPF with two vendors; B's core is single-area EIGRP, pure Cisco. B must keep two data centers for 18 months (customer contracts require local data retention) before consolidation.

**What you know**: all-office mutual access must work within 6 months of close; B's 5-person IT team knows only EIGRP; A requires "convergence onto A's architecture within 18 months".

**Questions**:

1. Which design use case is this, and what is its biggest risk?
2. How do you handle the address overlap — short term and long term?
3. How do you transition routing protocols?

**Suggested approach**:

- **This is a Merge use case; the biggest risks are address overlap and a capability gap in the team.** It also overlays "replace technology" and "prepare to divest" (the data centers split in 18 months), so the complexity multiplies.
- **Stop the bleeding on overlap first, fix the root cause second.** Short term, NAT at the inter-company boundary for only the segments that must talk (never network-wide NAT, or troubleshooting becomes a nightmare). Long term, renumber progressively, starting with low-change systems and leaving the high-change office network for last.
- **Do not convert routing in one step.** B's five engineers cannot absorb multi-area OSPF plus two vendors, so during transition attach B as a separate domain via boundary redistribution plus summarization. Then migrate B site by site, keeping a rollback window for every batch.
- **"Converge in 18 months" is a business goal, not a technical one.** The technical objective should be "remove the dual-domain operations burden within 18 months", so training and documentation handover must run in parallel.
- **What must be written down**: the addressing plan, the verification cases and rollback steps for each batch, and the data-flow diagram after the data centers split at month 18.

---

### Scenario 3: Operations proposes "replace OSPF with SD-WAN"

**Scenario**: a manufacturer with 60 plants runs MPLS plus OSPF, stable for 7 years. The new operations manager proposes replacing MPLS entirely with SD-WAN over Internet, citing that peers are doing it, CNY 3M of annual savings, and fast deployment.

**What you know**: critical plants carry MES real-time control traffic (one-way delay under 20 ms, jitter under 5 ms); some plants are in regions with poor network infrastructure; the group has just moved to SAP S/4HANA and expects WAN traffic to triple over two years; the operations team has 12 people with no SD-WAN experience.

**Questions**:

1. Which design use case is this, and what must be confirmed first?
2. Which sites and traffic flows suit migration, and which do not?
3. If migration proceeds, how are the plan and the rollback designed?

**Suggested approach**:

- **Ask "why" first, and keep asking until the answer is verifiable.** "Save CNY 3M" must be decomposed: circuit fees only, or including operations headcount? Do bigger Internet circuits, encryption gateways and a controller add CAPEX and OPEX? **A cost comparison that is not decomposed is usually wrong.**
- **Do not replace wholesale; migrate in tiers.** Office-type traffic suits SD-WAN over Internet; MES control traffic stays on an SLA-bearing link until delay and jitter targets are met — a hybrid WAN.
- **Technical feasibility is not organizational feasibility.** Twelve people with no experience switching everything at once bets production continuity on a learning curve. Pilot five non-critical plants, build a monitoring baseline and a failure playbook, then proceed in batches.
- **Minimum contents of the migration plan**: the site list per batch, the cutover window, business verification cases (MES transaction success rate, not "can we ping"), and **rollback trigger conditions and duration**.
- **The right deliverable is not yes/no but a migration roadmap split by year and by site class, with its risk exposure stated.**

---

## Key Terms

| Term | Meaning in design practice |
|------|----------------------------|
| **Top-Down Approach** | Start from business drivers and derive requirements before choosing technology |
| **Bottom-Up Approach** | Start from technology selection; useful for feasibility checks, risky as the primary method |
| **Functional Requirements** | What the system must do — also called behavioral requirements |
| **Technical Requirements** | Nonfunctional attributes: availability, security, integration, scale |
| **Application Requirements** | Constraints derived from how applications behave; usually decisive |
| **Greenfield** | A brand-new design on a blank sheet |
| **Brownfield** | A design inside an existing production environment |
| **Design Scope** | What the design covers — and, more importantly, what it does not |
| **Constraints** | Business, application and technical limits on the solution space |
| **Unstated Requirements** | Requirements the customer assumes rather than states |
| **Pervasive Security** | Security as a property of every decision, not a perimeter product |
| **Zero Trust Architecture** | Trust scored continuously per identity, device, application and data |
| **Fault Isolation** | Containing a failure inside its module or layer |
| **Information Hiding** | Limiting propagated state (for example via summarization) to improve scale |
| **Modularity** | Functional modules designed and operated independently |
| **Hierarchy** | Core, distribution and access layers with explicit responsibilities |
| **Gold Plating** | Over-engineering: adding capability nobody asked for |
| **CAPEX / OPEX / TCO / ROI** | The financial vocabulary required to defend a design |

---

## Chapter Summary

Chapter 1 delivers **a method, not a set of conclusions**. The whole chapter compresses into one sequence of actions:

```
Ask "why" first (business objective)
    ↓
Translate the objective into three requirement types: functional / technical / application
    ↓
Force out the unstated constraints (budget, compliance, legacy, people, time)
    ↓
Validate the solution against six principles
(pervasive security, availability, scalability, cost, manageability, unstated requirements)
    ↓
Implement it with four techniques (fault isolation, information hiding, modularity, hierarchy)
    ↓
Self-check against three pitfalls (assumptions, over-engineering, best-practice fallacy)
```

> **One-line memory**: **design is the path from "why the business cares" to "how the devices connect"; any hop skipped along the way comes back later as rework.**

Two points that are most often confused:

| Easily confused | Correct understanding |
|-----------------|-----------------------|
| Top-down vs. bottom-up | Not rival camps but **two directions of the same design**: requirements pushed top-down, feasibility verified bottom-up |
| Requirement vs. constraint | A requirement is "what must be achieved"; a constraint is "how it may not be done". Constraints often shape the architecture more than requirements |

Two of these principles echo through the remaining chapters: **security is pervasive**, and **without requirements there are no trade-offs**.
