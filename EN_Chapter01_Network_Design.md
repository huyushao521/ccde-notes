# Chapter 1: Network Design · 第 1 章：网络设计

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapters 1–2 (pp. 81–140)
>
> Terminology follows the English edition. Every English passage is followed by its Chinese counterpart in the grey block below it, so the two can be checked sentence by sentence.

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译 | 原书第 81-140 页

</div>

---

## Topics Covered · 本章涵盖主题

- **Network design fundamentals**: mindset, requirements, design use cases, the business, constraints
- **Network design principles**: pervasive security, scalability, availability, cost, manageability
- **Network design techniques**: fault isolation, information hiding, modularity, hierarchy
- **Network design pitfalls**: assumptions, over-engineering, the best-practice fallacy

<div class="zh" markdown="1">

- **网络设计基础**：思维模式、需求、设计用例、业务、约束
- **网络设计原则**：安全普适性、可扩展性、可用性、成本、可管理性
- **网络设计技术**：故障隔离、信息隐藏、模块化、层次化设计
- **网络设计缺陷**：假设、过度设计、最佳实践误区

</div>

---

## Chapter Overview: Ten Counterintuitive Lessons · 本章导读：网络设计的十个反直觉认知

There is no protocol, no command line and no topology in this chapter, yet it is the only one where a misreading poisons the following seventeen. The reason is simple: **once the methodology drifts, the more fluent you are with technology, the faster and the more expensively you go wrong.**

<div class="zh" markdown="1">

这一章没有协议、没有命令、没有拓扑图，却是全书唯一一章"如果你读错了，后面十七章都会跟着错"的内容。原因在于：**设计的方法论一旦走偏，技术越熟练，错得越快、越贵。** 下面十句话，每一句都能在真实的项目事故里找到对应。

</div>

**1. Knowing how to configure is not knowing how to design.** Configuration answers "how does this device do it"; design answers "why does this device exist, and what happens when it fails."

<div class="zh" markdown="1">

**1. 会配置不等于会设计。** 配置解决的是"这台设备怎么做"，设计解决的是"为什么要有这台设备、它坏了会发生什么"。一个能把 OSPF 调得飞快的人，完全可能设计出一个收敛很快但业务依然中断的网络。

</div>

**2. A requirement is not the sentence the customer said; it is the phenomenon you have verified.** "We don't have enough bandwidth" is often packet loss; "we need dual cores" is often a single-homed uplink. **An unmeasured requirement is merely an opinion.**

<div class="zh" markdown="1">

**2. 需求不是客户说的那句话，而是你验证过的现象。** 客户说"带宽不够"，实测可能是丢包；说"要双核心"，实测可能是上联单点。**未经测量的需求只是一种意见。**

</div>

**3. Bottom-up almost always fails, yet abandoning it also fails.** Starting from technology ("SD-WAN first", "vendor A first") is usually overturned by the business within six months; ignoring the current state means the design never lands. The correct posture is **push requirements top-down, validate feasibility bottom-up**.

<div class="zh" markdown="1">

**3. 自底向上几乎注定失败，但完全不用它也会失败。** 从技术选型开始（先定"上 SD-WAN"、先定"用 A 厂商"）通常会在半年后被业务需求推翻；而完全不看现状能力，方案又落不了地。正确姿势是**自顶向下推需求、自底向上验可行性**，两个方向都通才动手。

</div>

**4. Redundancy is not availability.** Two links in one conduit, two switches on one PDU, two carriers sharing one municipal duct — all "dual" on the diagram, all "single" in front of a failure. **Redundancy is measured in failure domains, not in device counts.**

<div class="zh" markdown="1">

**4. 冗余不等于可用性。** 两条链路走同一根管道、两台交换机插同一个机柜同一个 PDU、双运营商但共享同一段市政管井——这些在拓扑图上都是"双"，在故障面前都是"单"。**冗余必须以故障域为单位衡量，不是以设备数量衡量。**

</div>

**5. A "best practice" is somebody else's conclusion drawn under somebody else's constraints.** It deserves a hearing, but not a copy. Ask whether its constraint set (scale, budget, team, business model) matches yours; if not, it is an assumption awaiting validation.

<div class="zh" markdown="1">

**5. "最佳实践"是别人在别人的约束下得出的结论。** 它值得听，但不能直接抄。用之前要问：它成立的约束条件（规模、预算、团队、业务模型）和我一样吗？不一样，它就是一条待验证的假设。

</div>

**6. Security is not a module; it is a property of every design decision.** One decision that treats security as "we'll add a firewall later" already caps the security of the whole architecture.

<div class="zh" markdown="1">

**6. 安全不是一个模块，而是每个设计决策的属性。** 只要有一个决策把安全当成"后面再补一层防火墙"，这个架构的安全上限就已经定了。这也是第 4 章要整章展开"安全是普适的"的原因。

</div>

**7. Every additional nine costs more than the previous one.** From 99% to 99.9% may only need redundant power supplies; from 99.99% to 99.999% it touches process, drills, change management and supply chain.

<div class="zh" markdown="1">

**7. 可用性每提高一个 9，代价不是线性增长。** 从 99% 到 99.9% 可能只是加个冗余电源；从 99.99% 到 99.999% 要动的是流程、演练、变更管理和供应链。**先确认业务能承受哪个 9，再谈技术。**

</div>

**8. Cost is not the purchase price.** Real cost is TCO: acquisition + licenses + power + rack space + people + training + migration risk + exit cost five years out. Many "cheaper" options are expensive on Day 2.

<div class="zh" markdown="1">

**8. 成本不等于设备采购价。** 真正的成本是 TCO：采购 + 许可 + 电费 + 机柜 + 人力 + 培训 + 迁移风险 + 五年后的退出成本。很多"更便宜"的方案，贵在 Day 2。

</div>

**9. Defining what is out of scope matters more than defining what is in scope.** Scope creep is the most common way design projects die.

<div class="zh" markdown="1">

**9. 明确"不在范围内"比明确"在范围内"更重要。** 范围蔓延是设计项目最常见的死法：从"加个数据中心"变成"顺便把全网路由重构了"，最后时间、预算、质量三样一起崩。

</div>

**10. Recording why you did not choose X is worth more than recording why you chose Y.** In a year someone will ask "why didn't we go with SD-WAN", and by then the people who remember have moved on.

<div class="zh" markdown="1">

**10. 记录"为什么不选 X"，比记录"为什么选 Y"更有价值。** 因为一年后有人会问"当初为什么不上 SD-WAN"，而那时记得的人已经调岗了。

</div>

> **The chapter in one sentence**: **Design is the act of making traceable, reversible decisions with incomplete information.** Technology is the material of those decisions, not the decision itself.

<div class="zh" markdown="1">

> **一句话概括这一章**：**设计的本质是"在信息不完整的情况下，做可追溯、可回退的决策"。** 技术是这些决策的材料，不是决策本身。

</div>

---

## Foundation Topics · 基础内容

Designing a large-scale network to meet today's dynamic business and IT requirements is a complex task. This is especially true when the network was built years ago around older technologies and requirements, and the business now wants to adopt new IT technologies and architectures that the existing network may not support. The network designer therefore has to apply a structured approach to design.

<div class="zh" markdown="1">

设计大规模网络以满足当今动态的业务和 IT 需求是一项复杂的任务。尤其是当网络是多年前按照旧的技术和需求设计的，而企业决定采用新的 IT 技术和架构来实现其目标时，现有网络可能无法满足新技术的要求。因此，网络设计师必须采用结构化的方法来处理设计。

</div>

### Two Common Approaches to Network Analysis and Design · 两种常见的网络分析与设计方法

**Top-Down Approach**: decomposes the design task to simplify it, keeps the effort focused on the scope of the design, and executes it in a more controlled manner. It ultimately helps the designer view the solution from the business perspective.

<div class="zh" markdown="1">

**自顶向下方法 (Top-down Approach)**：通过拆分设计任务来简化设计过程，使其更专注于设计范围，以更受控的方式执行。这种方法最终帮助网络设计师从业务角度审视网络设计解决方案。

</div>

**Bottom-Up Approach**: starts with the selection of network technologies and design models. This carries a high risk of design failure, because the resulting network may not meet business or application requirements.

<div class="zh" markdown="1">

**自底向上方法 (Bottom-up Approach)**：与之相反，自底向上方法首先关注选择网络技术和设计模型。这会带来很高的设计失败风险，因为网络可能无法满足业务或应用的需求。

</div>

For a successful strategic design, more emphasis must be placed on the business: business priorities, drivers, outcomes, technical objectives, and the current and future services and applications. In today's networks, business requirements drive IT and network initiatives.

<div class="zh" markdown="1">

要实现成功的战略设计，必须更加重视业务。这意味着首要关注业务优先级、驱动力、成果、技术目标以及现有和未来的服务与应用。事实上，在当今的网络中，业务需求正在驱动 IT 和网络计划。

</div>

---

<figure class="fig">
<img src="assets/fig/en01-01-topdown-bottomup.svg" alt="Top-down lane deriving requirements downward and bottom-up lane verifying feasibility upward, converging on one design decision" loading="lazy">
<figcaption><b>Figure 1-1　Top-down and bottom-up are two directions of one design, not rival camps</b><br><span>图 1-1　自顶向下推需求、自底向上验可行性，是同一条路径的两个方向</span></figcaption>
</figure>

## Network Design Fundamentals · 网络设计基础

The design fundamentals are the building blocks every network designer must understand and know how to use:

<div class="zh" markdown="1">

网络设计基础是所有网络设计师应该理解并知道如何利用的基础元素：

</div>

1. **Mindset**
2. **Requirements**
3. **Design Use Cases**
4. **The Business**
5. **Constraints**
6. **"Why"**

<div class="zh" markdown="1">

1. **思维模式 (Mindset)**
2. **需求 (Requirements)**
3. **设计用例 (Design Use Cases)**
4. **业务 (The Business)**
5. **约束 (Constraints)**
6. **"为什么" (Why)**

</div>

<figure class="fig">
<img src="assets/fig/en01-02-six-fundamentals.svg" alt="Five fundamentals cards with a Why bar underneath covering all of them" loading="lazy">
<figcaption><b>Figure 1-2　Five building blocks, and the "why" underneath all of them</b><br><span>图 1-2　五个基础构件，以及压在它们下面的那个"为什么"</span></figcaption>
</figure>

### Mindset · 思维模式

> Above all else, your mindset is the single most critical factor in doing network design well. Knowing the technology is necessary, but it is the comparatively easy part of the journey. Many people who do network design do not have the right design mindset.

<div class="zh" markdown="1">

> 最重要的是，你的思维模式是做好网络设计的最关键因素。了解技术是必要的，但它是这段旅程中相对容易的部分。很多从事网络设计的人并不具备正确的设计思维模式。

</div>

An implementation mindset does not work for network design; you need a network design mindset to succeed in real design scenarios.

<div class="zh" markdown="1">

实施思维模式不适用于网络设计；你需要拥有网络设计思维模式才能在真实的网络设计场景中取得成功。

</div>

### Functional Requirements · 功能需求

Functional requirements form the basis of any system design because they define system and technology functions. Specifically, they identify, from a technical standpoint, what the technology or system will deliver to the business.

<div class="zh" markdown="1">

功能需求构成任何系统设计的基础，因为它们定义了系统和技术功能。具体来说，功能需求从技术角度识别这些技术或系统将向业务交付什么。

</div>

For example, an MPLS-enabled service provider might state a functional requirement such as: "the provider edge routers must send VoIP traffic over 10G fiber links and data traffic over OC-48 links." This implies the network needs a mechanism to send different traffic types over different paths, such as MPLS Traffic Engineering (MPLS-TE).

<div class="zh" markdown="1">

例如，一个启用了 MPLS 的服务提供商可能明确指定这样的功能需求："提供商边缘路由器必须通过 10G 光纤链路发送 VoIP 流量，而数据流量通过 OC-48 链路发送。"这意味着该服务提供商网络需要有能力通过不同路径发送不同类型流量的机制，如 MPLS 流量工程 (MPLS-TE)。

</div>

Functional requirements are sometimes called **behavioral requirements**, because they describe **what** the system does.

<div class="zh" markdown="1">

功能需求有时也被称为**行为需求**，因为它们描述系统**做什么**。

</div>

> ⚠️ A design that does not meet the business functional requirements is a bad design. In reality, however, not all functional requirements are handed to the designer; some are derived indirectly. Most of the time, discovering and documenting them is the designer's job.

<div class="zh" markdown="1">

> ⚠️ 不满足业务功能需求的设计被视为糟糕的设计。然而在现实中，并非所有功能需求都会直接提供给设计师。有时候它们可以基于其他因素间接确定。大多数时候，找到和记录功能需求是网络设计师的责任。

</div>

### Technical Requirements · 技术需求

Technical requirements are the technical aspects the infrastructure must provide in terms of security, availability and integration. They are commonly referred to as **nonfunctional requirements**. Examples include:

<div class="zh" markdown="1">

技术需求是网络基础设施在安全、可用性和集成方面必须提供的技术方面。这些需求通常被称为**非功能需求**。技术需求是多变的，必须用来证明技术选择的合理性。技术需求包括：

</div>

- Higher levels of network availability (for example, First Hop Redundancy Protocols [FHRP])
- Support for integration with network tools and services (for example, a NetFlow collector or a RADIUS authentication server)
- Network infrastructure security mechanisms (for example, control plane protection or infrastructure ACLs)

<div class="zh" markdown="1">

- 更高级别的网络可用性（例如使用首跳冗余协议 [FHRP]）
- 支持与网络工具和服务的集成（例如 NetFlow 收集器或 RADIUS 认证服务器）
- 网络基础设施安全技术（例如控制平面保护机制或基础设施访问控制列表）

</div>

> Technical requirements help the designer specify the required technical specifications (features and protocols) and the software releases that support them, and sometimes influence the hardware platform selection.

<div class="zh" markdown="1">

> 技术需求帮助网络设计师指定所需的技术规格（功能和协议）以及支持这些规格的软件版本，有时还会基于技术需求影响硬件平台的选择。

</div>

### Application Requirements · 应用需求

Application requirements are the deciding factor and, in most cases, constrain the design. If an application requires Layer 2 connectivity, the design is limited to Layer 2 protocols across data centers (for example, extended VLANs).

<div class="zh" markdown="1">

应用需求是决定性因素，在大多数情况下会约束网络设计。如果一个应用需要二层连接，就会将设计限制为跨数据中心的二层协议（如扩展 VLAN）。

</div>

From a business perspective, user experience is one of the top priorities any IT or network design must satisfy. End-user categories include:

<div class="zh" markdown="1">

从业务角度看，用户体验是任何 IT 和网络设计必须满足的首要优先级之一。最终用户类型包括：

</div>

| User Type | Description |
|-----------|-------------|
| **Customer** | An individual (for example, a bank customer) or a collective (for example, the customers of an MPLS service provider). Satisfaction directly affects reputation and revenue |
| **Internal User** | Employees. Their productivity translates into business efficiency and is tied to business success and revenue |
| **Business Partner** | An entity or organization with which goals are achieved jointly. Efficient partner interaction strengthens business success |

<div class="zh" markdown="1">

| 用户类型 | 说明 |
|---------|------|
| **客户** | 可以是个人（如银行客户）或集体（如 MPLS 服务提供商的客户）。客户满意度直接影响企业声誉和收入 |
| **内部用户** | 目标用户是内部员工。他们的生产力可以转化为业务绩效效率，与业务成功和收入直接相关 |
| **业务伙伴** | 共同实现目标的实体或组织。伙伴间的高效互动可以增强业务成功 |

</div>

> A network that cannot deliver the experience users expect means the primary business objective cannot be achieved, and IT will be seen by the business as a **cost center** rather than a **business enabler**.

<div class="zh" markdown="1">

> 无法交付用户期望体验水平的网络意味着无法实现主要业务目标。网络和 IT 技术将被业务视为**成本中心**而非**业务推动者**。

</div>

**Example**: a financial services company wants to differentiate itself with video communication to contact-center agents. If the network team does not account for the network requirements of video, the application will likely fail to deliver the expected experience.

<div class="zh" markdown="1">

**示例**：一家现代金融服务公司希望通过视频与客服坐席进行通信来区别于竞争对手。如果网络团队没有正确考虑视频通信的网络需求，应用很可能无法为最终用户交付期望的体验，从而导致无法实现公司的主要业务成果。

</div>

#### Application Requirements Drive Functional Requirements · 应用需求驱动功能需求

If a service provider has an SLA requiring one-way delay below 150 ms and packet loss below 1% for VoIP, that application requirement drives the functional requirement on the PE devices: use a technology that can deliver the SLA, such as CBTS MPLS-TE with Fast Reroute (FRR).

<div class="zh" markdown="1">

如果服务提供商与客户签订了 SLA，要求 VoIP 流量单向延迟小于 150ms、丢包率小于 1%，那么 VoIP 需求作为应用需求将驱动 PE 设备的功能需求——使用能够交付 SLA 的技术（如 CBTS MPLS-TE 配合快速重路由 FRR）。

</div>

<figure class="fig">
<img src="assets/fig/en01-03-requirement-chain.svg" alt="Application requirements drive functional requirements which force technical requirements, illustrated by a VoIP SLA example" loading="lazy">
<figcaption><b>Figure 1-3　Application requirements drive functional, functional forces technical</b><br><span>图 1-3　应用需求驱动功能需求，功能需求倒逼技术需求</span></figcaption>
</figure>

The designer should also consider:

<div class="zh" markdown="1">

网络设计师还应考虑以下基本问题：

</div>

1. How much network traffic does the application require?
2. How business-critical is the application, and what service levels does it need?
3. Does the application have separation requirements driven by regulation or corporate security policy?
4. What are the characteristics of the application?
5. How long does the application need to reset its state or session after losing connectivity?

<div class="zh" markdown="1">

1. 该应用需要多少网络流量？
2. 该应用对业务的关键程度和服务级别要求是什么？
3. 该应用是否有分离需求以满足行业法规和企业安全策略？
4. 该应用的特征是什么？
5. 该应用在失去连接后需要多长时间重置其状态或会话？

</div>

### Building the Design Requirements · 构建设计需求

This section uses one example to show how the different requirement types combine into the required design:

<div class="zh" markdown="1">

本节通过一个示例展示不同类型的需求如何共同实现所需的网络设计：

</div>

> **Example scenario**: a national retail company plans to expand internationally over the next 12 months by adding several sites. With its current IT infrastructure it faces high costs to manage and maintain two separate data and voice networks. The business also wants to invest in technologies that improve efficiency and employee productivity.

<div class="zh" markdown="1">

> **示例场景**：一家全国性零售公司目前计划在未来 12 个月内扩展业务，增加多个国际站点。然而，以现有的 IT 基础设施，他们在管理和维护现有的两个数据和语音网络方面面临高昂费用。此外，企业希望投资于能提升业务效率和员工生产力的技术。

</div>

### Design Scope · 设计范围

The designer must carefully analyze and evaluate the design scope before gathering information and planning the design. It is essential to determine whether the task is a **Greenfield** network or an existing production network, and whether the design spans a single network module or multiple modules.

<div class="zh" markdown="1">

在任何设计项目中，网络设计师在开始收集信息和规划网络设计之前，必须仔细分析和评估设计范围。因此，确定设计任务是针对**全新网络 (Greenfield)** 还是现有生产网络至关重要。同样重要的是确定设计是跨越单个网络模块还是多个模块。

</div>

| Design Scope | Example of Detailed Scope |
|--------------|---------------------------|
| **Enterprise campus** | Rolling out IP Telephony enterprise-wide may require redesigning VLANs, QoS and so on across LAN, WAN, DC and remote-access edge |
| **Campus only** | Adding multi-tenancy to the campus only requires designing VLAN, IP and path isolation across campus LANs |
| **Optimizing the enterprise edge** | Adding redundant links for remote access may require redesigning the WAN module, remote-site design and overlay tunnels |

<div class="zh" markdown="1">

| 设计范围 | 详细设计范围示例 |
|---------|----------------|
| **企业园区** | 在企业范围内推出 IP 电话，可能需要重新设计 VLAN、QoS 等，覆盖 LAN、WAN、DC 和远程接入边缘 |
| **仅园区** | 向园区添加多租户概念，只需要设计 VLAN、IP 和跨园区 LAN 的路径隔离 |
| **优化企业边缘** | 为远程访问添加冗余链路，可能需要重新设计 WAN 模块和远程站点设计以及覆盖隧道等配置 |

</div>

> ⚠️ **Design point**: identifying the scope is critical. You may face a very large network while the actual design effort is only about adding and integrating one new data center — yet the design must still start from the whole network ("holistic approach").

<div class="zh" markdown="1">

> ⚠️ **设计要点**：识别设计范围非常重要。例如，你可能面临一个大型网络，但实际设计重点只是添加和集成一个新数据中心，那就只需关注该部分。但设计仍要从整个网络出发——"整体方法"。

</div>

It is equally important to identify **what is out of scope**, which prevents scope creep from blocking the project.

<div class="zh" markdown="1">

同样重要的是识别**不在范围内的内容**。这可以防止范围蔓延阻碍项目成功。

</div>

### Design Use Cases · 设计用例

A successful design requires correctly identifying the specific use case.

<div class="zh" markdown="1">

要构建成功的网络设计，需要正确识别特定网络设计用例：

</div>

<figure class="fig">
<img src="assets/fig/en01-04-design-use-cases.svg" alt="Eight use case cards from greenfield through divestment and design failure" loading="lazy">
<figcaption><b>Figure 1-4　Seven use cases, from a blank sheet to the hardest one — divestment</b><br><span>图 1-4　七类设计用例：从一张白纸到最难的剥离</span></figcaption>
</figure>

#### 1. Greenfield · 全新设计

The best situation a designer can face: a blank sheet, designing and building the environment from scratch. Make sure that what you propose is genuinely what the business needs.

<div class="zh" markdown="1">

全新网络设计用例是网络设计师遇到的最佳情况之一。这是一张白纸，你从零开始设计、架构和构建环境。确保你建议的确实是业务所需的！

</div>

#### 2. Brownfield · 改造设计

Most design scenarios involve some form of brownfield work — an existing environment carrying production traffic. Spend time discovering the current state and assessing it properly; this is not only technical discovery of protocols and diagrams, but also discovery of the business and its direction.

<div class="zh" markdown="1">

大多数网络设计场景会包含某种形式的改造设计。改造用例是指已有生产流量运行的现有环境。建议先花时间发现当前状态并正确评估它。这不仅仅是协议和图表的技术发现，还需要发现业务及相关工作方向。

</div>

Once a design decision is made, prepare for migration: limit potential failure and rely on design fundamentals, principles and techniques.

<div class="zh" markdown="1">

一旦做出设计决策，确保为迁移到新设计做好准备。限制潜在故障，并依赖网络设计基础、原则和技术。

</div>

#### 3. Adding a Technology or Application · 添加技术或应用

Adding a technology or application can be very complex. The scope covers the impact of the addition on the existing network. Will the addition break anything? Application requirements in terms of traffic patterns, convergence time and latency must be considered.

<div class="zh" markdown="1">

添加技术或应用可能是一个非常复杂的设计用例。此用例的范围涵盖向现有网络添加技术或应用的影响。新添加会破坏什么吗？必须考虑应用需求在流量模式、收敛时间、延迟等方面的因素。

</div>

#### 4. Replacing a Technology · 替换技术

Replacing a technology covers the many options for replacing an existing technology to meet a specific requirement — WAN technology, routing protocol, security mechanism, underlying core technology, and so on. The impact of the new technology on the current design (improved scalability, or a potential conflict with existing application requirements) forces the designer to adjust the design.

<div class="zh" markdown="1">

替换技术用例涵盖替换现有技术以满足特定需求的多种选项。可能是 WAN 技术、路由协议、安全机制、底层网络核心技术或其他技术。新技术对当前设计的影响（如增强的可扩展性或与现有应用需求的潜在冲突）需要网络设计师调整设计。

</div>

> ⚠️ Make sure you are replacing or adding technology for the right reasons. Deploying SD-WAN to replace a WAN architecture without a solid justification is wrong. Ensure there is a direct business reason and a properly tested migration plan. Migrating from OSPF to EIGRP should come with a plan listing every step, each with verification tasks and a rollback plan.

<div class="zh" markdown="1">

> ⚠️ 确保在替换技术或添加新技术时，你是出于正确的原因。没有充分理由部署 SD-WAN 来替换 WAN 架构是不对的。确保有直接的业务理由。在此设计用例中，确保有经过适当测试的迁移计划。如果从 OSPF 迁移到 EIGRP，应该有一个列出每一步的计划，每一步都应有验证任务和回退计划。

</div>

#### 5. Merge or Divest · 合并或剥离

The merge-or-divest use case covers the impact and challenges of combining or separating networks.

<div class="zh" markdown="1">

合并或剥离用例涵盖合并或分离不同网络的影响和挑战。

</div>

**Merger**: two independent enterprises combine into one with an end-to-end architecture. Watch for overlapping technologies — for example, overlapping subnets. Most companies use RFC 1918 space (10.0.0.0/8, 172.16.0.0/12 or 192.168.0.0/16). Where overlap occurs, define a short-term and a long-term plan. Short term may involve NAT; long term may involve renumbering during a network refresh. Consolidate where possible — if the two companies have four data centers, merge to two (while remembering you may still need four).

<div class="zh" markdown="1">

**合并 (Merger)**：合并两个独立企业，创建一个具有端到端架构的企业。注意重叠技术——例如子网重叠。大多数公司使用 RFC 1918 子网（10.0.0.0/8、172.16.0.0/12 或 192.168.0.0/16）。当出现重叠时，制定短期和长期计划。短期可能包括使用 NAT，长期可能包括在网络升级时重新编号。尽可能整合——如果两个公司有四个数据中心，合并为两个（但注意可能仍需要四个）。

</div>

**Divestment**: the most difficult use case. Forced to split an architecture, you are left with two or more incomplete systems. Ensure every remaining business can still operate along its own direction; each one has to keep running and, in most cases, keep earning.

<div class="zh" markdown="1">

**剥离 (Divestment)**：这是最困难的设计用例。当被迫拆分架构时，你将留下两个或更多不完整的系统。确保所有剩余业务仍能沿着各自的工作方向运作。每个业务都需要继续运营，在大多数情况下意味着要赚钱。

</div>

#### 6. Scaling a Network · 网络扩展

The scaling use case covers different levels of scalability, including physical topology and Layer 2 and Layer 3 scalability considerations. Is the growth planned or organic? Is the growth causing problems? Should the designer stop and redesign the network to accommodate growth? Which design model scales best?

<div class="zh" markdown="1">

扩展用例涵盖不同级别的可扩展性方面，包括物理拓扑以及二层和三层可扩展性设计考量。考虑因素包括：增长是计划性的还是有机的？增长是否导致了问题？网络设计师是否应该停下来重新设计网络以适应增长？什么是最具可扩展性的设计模型？

</div>

#### 7. Design Failure · 设计失败

Nine times out of ten, the design failure use case is why you were called in. Something is broken and must be fixed. A simple technical example is misalignment between Spanning Tree Protocol (STP) and First Hop Redundancy Protocol (FHRP) root roles: if the STP root bridge and the FHRP default gateway are not aligned on the right devices, suboptimal routing follows and eventually the design fails.

<div class="zh" markdown="1">

十有八九，设计失败是你被叫来修复的设计用例。有问题，你必须解决它。一个简单的技术示例是生成树协议 (STP) 和首跳冗余协议 (FHRP) 的关键角色不对齐。如果 STP 根桥和 FHRP 默认网关没有对齐到正确的设备，就会有次优路由问题，最终导致设计失败。

</div>

### The Business · 业务

> Why do we make network design decisions? As designers, everything we do is for the businesses, companies and organizations we support. Specifically, we make decisions so that those businesses can make money.

<div class="zh" markdown="1">

> 我们为什么要做网络设计决策？作为网络设计师，我们所做的一切都是为了我们支持的企业、公司和组织。具体来说，我们为企业做网络设计决策，以便这些企业能够赚钱。

</div>

Not every organization exists to make a profit. Non-profits focus on covering expenses and reducing day-to-day cost; in the public sector many organizations focus on delivering a specific service or outcome rather than on earning.

<div class="zh" markdown="1">

当然，也有企业不以盈利为目的的情况。这些非营利组织更关注覆盖支出和降低日常成本。在公共部门，许多组织专注于提供特定服务或实现特定目标，而非赚钱。

</div>

> 💡 Documenting design decisions and their rationale is becoming standard practice. It lets every team member — past, present and future — understand why a feature, design option or capability was implemented. Remembering why a decision was made six months ago is far easier than remembering why a routing tweak was added two years ago at 2 a.m. during a maintenance window.

<div class="zh" markdown="1">

> 💡 记录所有设计决策及其原因变得越来越普遍。这允许所有团队成员（过去、现在和未来）理解为什么实施了某个功能、设计选项或特性。记住 6 个月前为什么做出设计决策比记住 2 年前凌晨 2 点维护窗口期间为什么添加路由调整要容易得多。

</div>

### Constraints · 约束

When we start designing for a customer, the slate is clean — no requirements, no rules. As we interview the customer we learn the requirements and, more importantly, the specific constraints that limit us. Constraints fall into three categories:

<div class="zh" markdown="1">

当我们为客户设计架构时，开始是干净的——没有需求、没有规则。随着我们采访客户，我们了解到不同的需求，更重要的是，了解到限制我们的特定约束。约束分为三类：

</div>

| Constraint Type | Description | Example |
|-----------------|-------------|---------|
| **Business** | Budget limits, staffing, contractual constraints | Insufficient budget, lack of staff with the required skills, contractual scope or timeline limits |
| **Application** | Limits imposed by how the application was written | Requires Layer 2 connectivity, hard-coded IP addresses, clustering that requires multicast |
| **Technical** | Limits of a specific vendor's hardware or solution | Locked to a vendor, prohibited from proprietary features, dependent on a proprietary solution that cannot be migrated |

<div class="zh" markdown="1">

| 约束类型 | 说明 | 示例 |
|---------|------|------|
| **业务约束** | 资金预算限制、人员配备、合同约束 | 预算不足、缺乏特定技术的人员、合同范围或期限限制 |
| **应用约束** | 应用以特定方式开发所带来的限制 | 需要二层连接、硬编码 IP 地址、需要组播支持的集群技术 |
| **技术约束** | 特定厂商硬件或解决方案的限制 | 被限制在特定厂商、不能使用专有技术或已使用无法迁移的专有方案 |

</div>

<figure class="fig">
<img src="assets/fig/en01-05-constraints.svg" alt="A funnel where business, application and technical constraints successively remove options, plus the five most common constraints" loading="lazy">
<figcaption><b>Figure 1-5　Constraints subtract options; they do not add requirements</b><br><span>图 1-5　约束是在删选项，不是在加需求</span></figcaption>
</figure>

#### The Most Common Design Constraints · 最常见的设计约束

1. **Cost**: the most common limiting factor. Treat cost as a design constraint only when the requirements explicitly call it out, or when it is the tiebreaker between two comparable options. Do not assume technology A is more expensive than B — MPLS circuits are not automatically more expensive than Internet circuits.
2. **Time**: if the project has a completion deadline, time may be the key constraint on technology or architecture choices.
3. **Location**: location introduces indirect limits. A remote site may be in an area without fiber, leaving wireless as the only option.
4. **Infrastructure**: legacy equipment with no refresh plan may be incompatible with new features or protocols.
5. **Staff Expertise**: if the staff lack experience with the new technology there are two choices: (a) train them — risky, because inexperience lengthens problem resolution; or (b) hire experienced staff — usually expensive.

<div class="zh" markdown="1">

1. **成本 (Cost)**：成本是任何设计中最常见的限制因素。但只有当需求中明确提到成本是考虑因素，或它是两个类似方案之间的决胜因素时，才应将成本视为设计约束。不要假设技术 A 比技术 B 贵或便宜——例如，MPLS 线路并不自动比 Internet 线路更贵。
2. **时间 (Time)**：如果项目有完成期限，时间也可能是选择技术或架构时的关键约束。
3. **位置 (Location)**：位置约束可能引入间接影响设计的限制。例如，远程站点可能位于没有光纤基础设施的区域，唯一可用的连接类型是无线。
4. **基础设施 (Infrastructure)**：旧网络设备如果企业没有更换计划，可能对新功能或协议不兼容。
5. **人员专长 (Staff Expertise)**：如果公司员工没有使用新技术的经验，有两个选择：(a) 培训员工——但有风险，因为缺乏经验可能需要更长时间解决问题；(b) 聘请有经验的人员——但通常成本很高。

</div>

### "Why" · "为什么"

> You often hear a customer say "that is a requirement", but when you ask "why?", they cannot give a valid reason. Use the "five whys" concept — keep asking "why" like a five-year-old until you reach an answer you can understand and appreciate.

<div class="zh" markdown="1">

> 你经常听到客户说"这是需求"，但当你问"为什么？"时，他们无法给出有效理由。利用"五个为什么"的概念——像 5 岁孩子一样不断问"为什么"，直到得到你能理解和领会的答案。

</div>

Toyota used the "five whys" system to investigate production problems, asking "why" five times to reveal the root cause.

<div class="zh" markdown="1">

丰田公司使用"五个为什么"系统来调查生产问题，通过问五次"为什么"来揭示问题的根本原因。

</div>

As a designer you need to determine why the business truly needs the solution. The questions below contain no "why" but serve the same purpose:

<div class="zh" markdown="1">

作为网络设计师，你需要确定为什么业务真正需要这些解决方案。以下是一些不包含"为什么"但能达到相同目的的问题：

</div>

- What problem are you solving with this technology?
- What are your staff's/customers' workflows today?
- How will this technology change those workflows?
- How will your business (governance, policy, process and culture) evolve because of this technology?

<div class="zh" markdown="1">

- 你用这项技术解决什么问题？
- 你的员工/客户今天的工作流程是什么？
- 这项技术将如何改变这些工作流程？
- 你的业务（治理、策略、流程和文化）将因为这项技术如何演变？

</div>

---

## Network Design Principles · 网络设计原则

The design principles are:

<div class="zh" markdown="1">

网络设计原则包括以下五个：

</div>

1. **Security**
2. **Scalability**
3. **Availability**
4. **Cost**
5. **Manageability**

<div class="zh" markdown="1">

1. **安全 (Security)**
2. **可扩展性 (Scalability)**
3. **可用性 (Availability)**
4. **成本 (Cost)**
5. **可管理性 (Manageability)**

</div>

### Unstated Requirements · 未明确需求

> Customers increasingly do not state their specific requirements. They assume them, and as a designer you must work out which requirements matter for the design. You must not only identify them but also determine the level of each — does the network need to survive a single failure or a double failure?

<div class="zh" markdown="1">

> 客户越来越不明确表达他们的具体需求。他们假设需求，作为网络设计师，你必须弄清楚哪些需求对网络设计很重要。你不仅要识别需求，还要确定每个需求的级别。例如，这个网络需要没有单点故障还是没有双点故障？

</div>

Every design principle has effectively become an unstated requirement.

<div class="zh" markdown="1">

每个网络设计原则都已成为一个未明确需求。

</div>

### Pervasive Security · 普适安全

Historically security was not treated as a design principle. Because of its impact on the business overall, it is now included as one.

<div class="zh" markdown="1">

历史上，安全并未被识别为网络设计原则。由于安全对整体业务的影响，它被列为网络设计原则。

</div>

**What if the network is compromised? What if data integrity is violated?**

<div class="zh" markdown="1">

**如果网络被攻破会怎样？如果数据完整性受损会怎样？**

</div>

- Business reputation is damaged
- Customers lose trust
- The business loses money and revenue
- The business no longer meets compliance standards and may be fined or shut down
- In extreme cases, the business fails

<div class="zh" markdown="1">

- 业务声誉受损
- 客户失去信任
- 业务损失资金和收入
- 业务不再满足合规标准，可能被罚款或关闭
- 在极端情况下，业务失败

</div>

#### Three Security Models · 三种安全模型

| Model | Characteristics |
|-------|-----------------|
| **Perimeter Security** | Also called the "turtle shell" model. Firewalls at the perimeter, nothing inside. East-west traffic is wide open and insider threats flourish |
| **Session and Transaction Security** | Evolved from perimeter security. Users and devices are pinned down; east-west traffic is protected dynamically based on device, user, location and need. 100% authentication plus 100% authorization of every session and transaction |
| **Zero Trust Architecture** | Adds real-time capture and analytics so that AI/ML decisions can be made in real time. Every device, user, application, server, service and resource — even the data itself — is assigned a trust score derived from what the analytics engine observes |

<div class="zh" markdown="1">

| 模型 | 特点 |
|------|------|
| **边界安全 (Perimeter Security)** | 又称"龟壳"模型。在边界部署防火墙，内部没有其他安全设备。东西向流量完全开放，内部威胁泛滥 |
| **会话和交易安全** | 从边界安全演变而来。用户和设备被锁定，基于设备、用户、位置和需求动态保护东西向流量。100% 认证 + 100% 授权每个会话和交易 |
| **零信任架构 (Zero Trust)** | 添加实时捕获和分析工具，允许实时 AI/ML 决策。每个设备、用户、应用、服务器、服务和资源（甚至数据本身）都被分配一个信任分数。信任分数基于分析引擎看到的动态变化 |

</div>

<figure class="fig">
<img src="assets/fig/en01-06-security-models.svg" alt="Perimeter, session and transaction, and zero trust security models with what each one protects" loading="lazy">
<figcaption><b>Figure 1-6　Three security models: the edge, the session, the continuous score</b><br><span>图 1-6　三种安全模型：守边界、查会话、持续打分</span></figcaption>
</figure>

### Availability · 可用性

Availability encompasses redundancy, resilience and reliability:

<div class="zh" markdown="1">

可用性包括冗余、弹性、可靠性等概念：

</div>

| Concept | Definition |
|---------|------------|
| **Redundancy** | Multiple resources performing the same function/role, so one takes over when another fails |
| **Resilience** | The ability of the network to switch over automatically when a failure occurs |
| **Reliability** | The degree to which data travels from source to destination correctly and within the expected time |

<div class="zh" markdown="1">

| 概念 | 定义 |
|------|------|
| **冗余 (Redundancy)** | 多个资源执行相同功能/角色，一个故障时另一个接管 |
| **弹性 (Resilience)** | 网络在故障发生时自动切换的能力 |
| **可靠性 (Reliability)** | 网络数据在正确时间内从源到达目的地的程度 |

</div>

> As the required level of availability rises, so do complexity and cost. Eliminating single points of failure versus double points of failure: the latter grows cost and complexity exponentially.

<div class="zh" markdown="1">

> 随着可用性水平的提高，复杂性和相关成本也随之增加。消除单点故障 vs 消除双点故障——后者使成本和复杂性呈指数级增长。

</div>

**How much redundancy is too much?** When the added complexity and cost are not worth the corresponding gain in availability. Eight parallel Layer 2 or Layer 3 links between two points make no sense — two is the standard, four needs justification, five or more adds far more complexity than benefit.

<div class="zh" markdown="1">

**多少冗余是过多的？** 当增加的复杂性、成本和可用性的相关回报不值得时，就是过多了。例如，设计八条二层或三层链路之间的连接是不合理的——两条是标准，四条有合理理由，五条或更多增加的复杂性远超收益。

</div>

<figure class="fig">
<img src="assets/fig/en01-07-availability-cost.svg" alt="Availability targets with permitted yearly downtime and typical means, plus a bar chart of two, four and five-plus parallel links" loading="lazy">
<figcaption><b>Figure 1-7　Each additional nine costs more than the previous one</b><br><span>图 1-7　可用性每多一个 9，代价都比上一个更高</span></figcaption>
</figure>

### Scalability · 可扩展性

Scalability ensures the design can accommodate business growth:

<div class="zh" markdown="1">

可扩展性是网络设计原则，确保设计能够适应业务的增长和扩展。网络设计师需要考虑：

</div>

- Does the network support scaling up (more capability per device)?
- Does it support scaling out (more devices)?
- Is growth planned or organic?
- Does the current design need to be redesigned before growth happens?

<div class="zh" markdown="1">

- 网络是否支持纵向扩展（增加设备能力）
- 网络是否支持横向扩展（增加设备数量）
- 增长是计划性的还是有机的
- 当前设计是否需要在增长前重新设计

</div>

### Cost · 成本

Cost is one of the design constraints. The designer needs to understand the following financial concepts:

<div class="zh" markdown="1">

成本是设计约束之一。网络设计师需要理解以下财务概念：

</div>

| Concept | Definition |
|---------|------------|
| **CAPEX** | Capital expenditure — one-off investment in equipment, facilities and so on |
| **OPEX** | Operating expenditure — day-to-day operating and maintenance cost |
| **TCO** | Total cost of ownership — CAPEX plus OPEX |
| **ROI** | Return on investment — the ratio of benefit to cost for an investment |

<div class="zh" markdown="1">

| 概念 | 定义 |
|------|------|
| **CAPEX** | 资本支出——购买设备、建设设施等一次性投资 |
| **OPEX** | 运营支出——日常运营和维护成本 |
| **TCO** | 总拥有成本——CAPEX + OPEX 的总和 |
| **ROI** | 投资回报率——投资带来的收益与成本的比率 |

</div>

### Manageability · 可管理性

Manageability covers how well a design can be operated day to day. A technically perfect design that cannot be managed is not a good design. It includes:

<div class="zh" markdown="1">

可管理性涉及网络设计在日常运营中的可管理程度。一个设计方案如果技术上完美但无法管理，就不是好的设计。可管理性包括：

</div>

- Ease of monitoring and troubleshooting
- Degree to which configuration management is simplified
- Fit with the operations team's skills

<div class="zh" markdown="1">

- 网络监控和故障排查的便利性
- 配置管理的简化程度
- 运维团队的技能匹配度

</div>

---

## Network Design Techniques · 网络设计技术

### Fault Isolation · 故障隔离

Through modular and hierarchical design, ensure that a failure in one module or layer does not spread to the others.

<div class="zh" markdown="1">

故障隔离是网络设计中的关键技术。通过模块化设计和层次化设计，确保一个模块或层次的故障不会扩散到其他部分。

</div>

### Information Hiding · 信息隐藏

Through route summarization, area design and similar mechanisms, reduce the amount of routing information propagated, improving scalability and convergence.

<div class="zh" markdown="1">

信息隐藏通过路由汇总、区域划分等技术，减少网络中传播的路由信息量，提高可扩展性和收敛速度。

</div>

### Modularity · 模块化设计

Divide the network into functional modules, each designed and managed independently. Benefits include fault isolation, scalability, manageability and flexibility.

<div class="zh" markdown="1">

将网络分成多个功能模块，每个模块独立设计和管理。好处包括：
- 故障隔离
- 可扩展性
- 可管理性
- 灵活性

</div>

### Hierarchy · 层次化设计

Hierarchical design splits the network into core, distribution and access layers, each with clear responsibilities.

<div class="zh" markdown="1">

层次化设计将网络分为核心层、分布层和接入层，每层有明确职责。

</div>

---

<figure class="fig">
<img src="assets/fig/en01-08-four-techniques.svg" alt="Four cards for fault isolation, information hiding, modularity and hierarchy, each with mechanism and observable effect" loading="lazy">
<figcaption><b>Figure 1-8　Four techniques, one purpose: keep a failure inside its own box</b><br><span>图 1-8　四项技术，同一个目的：把故障关在自己的盒子里</span></figcaption>
</figure>

## Network Design Pitfalls · 网络设计缺陷

### 1. Assumptions · 假设

> As designers we tend to make assumptions based on our own experience — for example, that MPLS is more expensive than Internet, or that one technology is better than another. Do not make assumptions without factual support.

<div class="zh" markdown="1">

> 作为网络设计师，我们可能会基于自己的经验做出假设。例如假设 MPLS 比 Internet 贵，假设某种技术比另一种更好。不要做没有事实支持的假设。

</div>

### 2. Over-Engineering (Gold Plating) · 过度设计

> Over-engineering means adding unnecessary features, redundancy or complexity. A design should solve the current problem, no more and no less, unless the requirements say otherwise.

<div class="zh" markdown="1">

> 过度设计是指在网络设计中添加不必要的功能、冗余或复杂性。设计应该解决当前问题，不多不少，除非需求另有说明。

</div>

### 3. The Best-Practice Fallacy · 最佳实践误区

> A "best practice" may not apply to every scenario. The designer must understand the reasoning and the applicable conditions behind each best practice instead of applying it blindly.

<div class="zh" markdown="1">

> "最佳实践"可能不适用于所有场景。网络设计师需要理解每个"最佳实践"背后的原理和适用条件，而不是盲目应用。

</div>

---

<figure class="fig">
<img src="assets/fig/en01-09-pitfalls.svg" alt="Three pitfall cards showing symptom, cause and countermeasure for assumptions, over-engineering and the best-practice fallacy" loading="lazy">
<figcaption><b>Figure 1-9　Three ways a good engineer still produces a bad design</b><br><span>图 1-9　好工程师做出坏设计的三种方式</span></figcaption>
</figure>

## Case Studies · 实战案例

### Case 1: "The network is slow" is usually not a bandwidth problem · 案例一："网络太卡"往往不是带宽问题

**Background**: at a new university campus, staff and students complain that the teaching system is slow. Operations produce a monitoring chart: peak utilization of the core egress is only 40% — "bandwidth is clearly sufficient".

<div class="zh" markdown="1">

**背景**：某高校新校区，师生普遍反映教学系统"卡"。运维拿出监控图：核心出口峰值利用率只有 40%，"带宽明明够用"。

</div>

**Disagreement**: one side wants a bigger leased line (CNY 400k per year), the other wants to investigate the application first.

<div class="zh" markdown="1">

**分歧**：一方主张扩容专线（40 万/年），一方主张先查应用。

</div>

**What the investigation found**:

<div class="zh" markdown="1">

**实际排查**：

</div>

| Check | Finding |
|-------|---------|
| Egress utilization | 40% average, but a **3–5 second 100% burst every minute** — invisible to 5-minute averaging |
| Switch queues | Output drops on the uplink at peak |
| Application behavior | Each page load issues 60+ concurrent small requests, extremely sensitive to loss |

<div class="zh" markdown="1">

| 检查项 | 发现 |
|------|------|
| 出口利用率 | 平均 40%，但**每分钟有一次 3–5 秒的 100% 突发**，监控按 5 分钟平均，看不见 |
| 交换机队列 | 高峰期 uplink 出方向有丢包 |
| 应用行为 | 教学平台每次页面加载并发 60+ 个小请求，对丢包极其敏感 |

</div>

**Root cause**: bandwidth was not the bottleneck; **bursty traffic plus insufficient queue buffering** caused loss and repeated TCP retransmission. The real requirement was queueing/shaping and better concurrency behavior, not more bandwidth.

<div class="zh" markdown="1">

**根因**：链路带宽不紧张，但**突发流量 + 队列缓冲不足**导致丢包，TCP 反复重传。真正的需求是**队列/整形与并发收敛**，不是更大带宽。

</div>

**Outcome**: QoS queue tuning plus an uplink port upgrade — CNY 30k — solved it.

<div class="zh" markdown="1">

**结果**：调整 QoS 队列 + 升级上联端口，成本 3 万，问题解决。

</div>

> 💡 **Lesson**: **a requirement is not what the user says, it is what measurement confirms.** 40% average utilization was an **assumption**, not evidence.

<div class="zh" markdown="1">

> 💡 **教训**：**需求不是"用户说的话"，而是"测量之后确认的现象"。** 40% 的平均利用率是一个**假设**，不是证据。

</div>

### Case 2: Does a 200-person branch need "dual cores"? · 案例二：200 人的分部需要"双核心"吗

**Background**: a new 200-person branch, mostly office work plus video conferencing. The branch manager demands "dual cores, dual uplinks, dual carriers — the same standard as headquarters".

<div class="zh" markdown="1">

**背景**：某集团新建分部，200 人，业务以办公 + 视频会议为主。分部负责人要求"双核心、双上联、双运营商，和总部标准一样"。

</div>

**Checking each demand against requirements**:

<div class="zh" markdown="1">

**用需求逐条核对**：

</div>

| Demand | Requirement basis | Verdict |
|--------|-------------------|---------|
| Dual core switches | A single core failure means 4 hours of downtime (spare-parts lead time) | Valid — but achievable at low cost with stacking or a redundant pair |
| Dual carrier circuits | No carrier fiber cut ever recorded at this campus | **Not valid** — single circuit plus 4G/5G backup instead |
| Dual-link load sharing | Peak traffic 180 Mbps; one 1G link is enough | **Not valid** — becomes backup rather than load sharing |

<div class="zh" markdown="1">

| 要求 | 需求依据 | 判断 |
|------|---------|------|
| 双核心交换机 | 单台核心故障时业务中断 4 小时（备件周期） | 成立 → 但可用**堆叠/双机**低成本实现 |
| 双运营商专线 | 该园区历史上无运营商光缆中断记录 | **不成立** → 改为单专线 + 4G/5G 备份 |
| 双链路负载分担 | 峰值流量 180M，单条 1G 足够 | **不成立** → 变为备份而非负载分担 |

</div>

**Outcome**: cost dropped from CNY 2.1M to CNY 850k with the same availability target (under 4 hours of downtime per year).

<div class="zh" markdown="1">

**结果**：方案成本从 210 万降到 85 万，可用性目标（年中断 < 4 小时）不变。

</div>

> 💡 **Lesson**: **"the same as headquarters" is not a requirement, it is a habit.** The best-practice trap and over-engineering both show up in real life under the name of standardization.

<div class="zh" markdown="1">

> 💡 **教训**：**"和总部一样"不是需求，是习惯。** 第 1 章的"最佳实践陷阱"和"过度设计"，现实中都以"标准化"的名义出现。

</div>

---

## Lessons Learned · 实战经验总结

| Lesson | Explanation |
|--------|-------------|
| **Quantify requirements and match metrics to the symptom** | 5-minute averages hide 3-second bursts (Case 1). Monitoring granularity must match the time scale of the user's complaint |
| **Redundancy is decided by failure domain and business impact** | Do not ask "what is the HQ standard"; ask "if this device fails, how much business stops for how long" (Case 2) |
| **Every requirement must be traceable** | A requirement that cannot be traced to a business objective usually comes from habit or a vendor deck and should be challenged |
| **Push top-down, validate bottom-up** | Requirements come down from the business, the solution is verified upward against current capability |
| **Complexity must justify itself** | For every added protocol layer or feature, ask "does the failure it prevents outweigh the risk it introduces?" |
| **Ask who maintains it on Day 2** | A design the team cannot operate becomes technical debt the day it goes live |
| **Record rejected options and why** | "Why not X" is often more valuable than "why Y", and it is the basis for future change |

<div class="zh" markdown="1">

| 经验 | 说明 |
|------|------|
| **需求要量化，指标要匹配现象** | 5 分钟平均利用率看不见 3 秒突发（案例一）。监控粒度必须与用户抱怨的现象同一尺度 |
| **冗余由故障域和业务影响决定** | 不问"总部是什么标准"，只问"这台设备坏了，多少业务停多久"（案例二） |
| **每条要求都要能追溯** | 追溯不到业务目标的要求，通常来自习惯或厂商建议，应被质疑 |
| **自顶向下推、自底向上验** | 需求从业务推下来，方案从现有能力验上去。只在两个方向都成立的设计才可落地 |
| **复杂度必须证明收益** | 每引入一层协议或一个特性，都要回答"它避免的故障比它引入的风险更大吗" |
| **先问"谁在 Day 2 维护"** | 团队接不住的方案，上线那天就是技术债的起点 |
| **记录被否决的方案与理由** | 设计文档里"为什么不选 X"往往比"为什么选 Y"更有价值，也是后续变更的依据 |

</div>

---

## Design Scenarios (3) · 设计情景演练（3 个）

> How to use: read only the **Scenario**, write your own answers to the three questions, then read the **Suggested approach**. It is not an answer key but the **skeleton of a decision**.

<div class="zh" markdown="1">

> 用法：先只看「场景」，自己写出三个问题的答案，再看「参考思路」。参考思路不是标准答案，而是**决策的骨架**——真实项目里信息永远比你想要的多，关键是知道缺哪一块。

</div>

### Scenario 1: "One standard for the whole company" · 情景一：集团要求"全公司一个标准"

**Scenario**: a group has one headquarters (1,200 people), one R&D center (800) and 37 sales offices (8–40 people). The new CIO proposes "the same reference architecture, the same core model and the same dual-carrier circuit at every site, for ease of management". Operations supports it: "when something breaks, knowing one place is enough".

<div class="zh" markdown="1">

**场景**：某集团有 1 个总部（1200 人）、1 个研发中心（800 人）、37 个销售办事处（8–40 人）。CIO 刚上任，提出"所有站点用同一套标准架构、同一型号核心、同一条双运营商专线，方便管理"。运维团队支持，因为"故障时会修一个地方就够了"。

</div>

**What you know**: the 37 offices cost CNY 42k per year each in network spend; over the past three years link failures caused 6 outages at offices, the longest 3 hours (sales can fall back to phone hotspots); the cost of one hour of downtime at HQ and at the R&D center is CNY 1.8M and CNY 400k respectively.

<div class="zh" markdown="1">

**你手上的信息**：37 个办事处年均网络支出 4.2 万元/个；过去三年办事处因链路故障导致的业务中断累计 6 次，最长 3 小时（销售可用手机热点应急）；总部/研发中心的年中断代价分别是 180 万/小时和 40 万/小时。

</div>

**Questions**:

1. What is the real requirement behind "one standard"?
2. Which parts can be standardized, and which must be tiered?
3. What are the cost and the risk of the CIO's proposal?

<div class="zh" markdown="1">

**要回答的问题**：
1. "统一标准"背后真正的需求是什么？
2. 哪些环节可以统一、哪些必须分级？
3. 如果按 CIO 的方案做，成本和风险各是什么？

</div>

**Suggested approach**:

- **The real requirement is "reduce management complexity", not "identical architecture".** Complexity can be reduced with configuration templates, centralized monitoring and automated audits without buying the same box everywhere.
- **Availability must be tiered by business impact.** CNY 1.8M per hour at HQ versus an office outage that a phone hotspot can carry for 3 hours — the targets differ by two or three orders of magnitude; a single redundancy model necessarily wastes at one end and under-delivers at the other.
- **What can be standardized is a standardized option set**: three tiers of templates (micro/small/medium), a common addressing plan, a common management plane and configuration baseline. **What must not be standardized is capacity and redundancy level.**
- **37 dual circuits cost roughly CNY 600–700k more per year**, while the risk it removes is far below the benefit of one extra link at HQ — over-engineering in its classic form.
- **How to land it**: give the CIO a tiered proposal plus a three-year TCO comparison plus a table of "what an outage at each site class costs" — not an objection.

<div class="zh" markdown="1">

**参考思路**：
- **真正的需求是"降低管理复杂度"，不是"架构一致"。** 这两者不等价：管理复杂度可以靠配置模板、集中监控、自动化巡检降低，不需要每个站点买同样的盒子。
- **可用性要按业务影响分级。** 总部 180 万/小时，办事处中断可以靠手机热点撑过 3 小时——这两类站点的可用性目标相差两三个数量级，用同一套冗余方案必然一端浪费、一端不足。
- **可以统一的是"标准化的选项集"**：三层模板（微型/小型/中型）、统一的地址规划、统一的管理平面与配置基线；**不该统一的是容量与冗余等级**。
- **37 × 双专线 ≈ 每年多花 60–70 万**，而它降低的风险（6 次 × 3 小时 × 办事处量级损失）远低于总部多加一条链路的收益。这就是"过度设计"的典型形态：**以标准化之名，花掉了本该投在关键站点上的钱。**
- **落地方式**：给 CIO 的不是"反对"，而是分级方案 + 三年 TCO 对比 + 一张"哪类站点出故障影响多少钱"的表。**用业务语言表达技术判断，是设计师的基本功。**

</div>

### Scenario 2: Network integration after an acquisition · 情景二：并购后的网络整合

**Scenario**: Company A acquires Company B. A uses 10.0.0.0/8; so does B. A's core is multi-area OSPF with two vendors; B's core is single-area EIGRP, pure Cisco. B must keep two data centers for 18 months (customer contracts require local data retention) before consolidation.

<div class="zh" markdown="1">

**场景**：A 公司收购 B 公司。A 用 10.0.0.0/8，B 也用 10.0.0.0/8；A 的核心是 OSPF 多区域 + 双厂商，B 的核心是 EIGRP 单区域 + 纯 Cisco；B 有 2 个数据中心必须保留 18 个月（客户合同要求数据本地留存），之后合并。

</div>

**What you know**: all-office mutual access must work within 6 months of close; B's 5-person IT team knows only EIGRP; A requires "convergence onto A's architecture within 18 months".

<div class="zh" markdown="1">

**你手上的信息**：合并后 6 个月内要打通全部办公互访；B 的 IT 团队 5 人只熟 EIGRP；A 要求"18 个月内统一到 A 的架构"。

</div>

**Questions**:

1. Which design use case is this, and what is its biggest risk?
2. How do you handle the address overlap — short term and long term?
3. How do you transition routing protocols?

<div class="zh" markdown="1">

**要回答的问题**：
1. 这是哪一类设计用例？它的最大风险是什么？
2. 地址重叠怎么处理，短期和长期分别做什么？
3. 路由协议怎么过渡？

</div>

**Suggested approach**:

- **This is a Merge use case; the biggest risks are address overlap and a capability gap in the team.** It also overlays "replace technology" and "prepare to divest" (the data centers split in 18 months), so the complexity multiplies.
- **Stop the bleeding on overlap first, fix the root cause second.** Short term, NAT at the inter-company boundary for only the segments that must talk (never network-wide NAT, or troubleshooting becomes a nightmare). Long term, renumber progressively, starting with low-change systems and leaving the high-change office network for last.
- **Do not convert routing in one step.** B's five engineers cannot absorb multi-area OSPF plus two vendors, so during transition attach B as a separate domain via boundary redistribution plus summarization. Then migrate B site by site, keeping a rollback window for every batch.
- **"Converge in 18 months" is a business goal, not a technical one.** The technical objective should be "remove the dual-domain operations burden within 18 months", so training and documentation handover must run in parallel.
- **What must be written down**: the addressing plan, the verification cases and rollback steps for each batch, and the data-flow diagram after the data centers split at month 18.

<div class="zh" markdown="1">

**参考思路**：
- **这是"合并 (Merge)"用例，最大风险是地址重叠与团队能力断层。** 注意它同时叠加了"替换技术"和"剥离准备"（18 个月后要拆），复杂度是相乘的。
- **地址重叠先止血、再治本**：短期在互访边界做 NAT（只对需要互访的网段，不做全网 NAT，否则故障定位变成噩梦）；长期按新规划的地址块逐步重编号，优先从"变更频率低"的系统开始（数据库、老应用），最后动高频变更的办公网。
- **路由协议不要一步到位。** B 的 5 人团队接不住 OSPF 多区域 + 双厂商，所以过渡期用**边界重分发 + 汇总**把 B 作为独立域接入（A 侧只看到 B 的汇总路由），先实现互通；再按站点批次把 B 迁移到 OSPF，每批都保留回退窗口。
- **"18 个月统一"是商业目标，不是技术目标。** 技术目标应是"18 个月内消除双域运维负担"，因此要同步做团队培训和运维文档移交，否则到了 deadline 网络统一了、人还没跟上。
- **必须写下来的**：短期/长期地址方案、每批迁移的验证用例与回退步骤、18 个月后数据中心拆分的数据流向图。**并购项目的失败几乎都不是协议问题，而是"没人写清楚阶段目标"。**

</div>

### Scenario 3: Operations proposes "replace OSPF with SD-WAN" · 情景三：运维提出"把 OSPF 换成 SD-WAN"

**Scenario**: a manufacturer with 60 plants runs MPLS plus OSPF, stable for 7 years. The new operations manager proposes replacing MPLS entirely with SD-WAN over Internet, citing that peers are doing it, CNY 3M of annual savings, and fast deployment.

<div class="zh" markdown="1">

**场景**：某制造企业 60 个工厂，现网是 MPLS + OSPF，运行 7 年稳定。新任运维经理提出"MPLS 太贵，全换成 SD-WAN + Internet"。给出的理由：同行都在换；每年可省 300 万；部署快。

</div>

**What you know**: critical plants carry MES real-time control traffic (one-way delay under 20 ms, jitter under 5 ms); some plants are in regions with poor network infrastructure; the group has just moved to SAP S/4HANA and expects WAN traffic to triple over two years; the operations team has 12 people with no SD-WAN experience.

<div class="zh" markdown="1">

**你手上的信息**：关键工厂有 MES 实时控制流量（对抖动敏感，要求单向时延 < 20ms、抖动 < 5ms）；部分工厂位于网络基础设施较差的地区；集团刚上 SAP S/4HANA，未来两年 WAN 流量预计增长 3 倍；运维团队 12 人，无 SD-WAN 经验。

</div>

**Questions**:

1. Which design use case is this, and what must be confirmed first?
2. Which sites and traffic flows suit migration, and which do not?
3. If migration proceeds, how are the plan and the rollback designed?

<div class="zh" markdown="1">

**要回答的问题**：
1. 这个提议属于哪一类设计用例，应先确认什么？
2. 哪些站点/流量适合迁移，哪些不适合？
3. 如果最终要迁，迁移计划和回退怎么设计？

</div>

**Suggested approach**:

- **Ask "why" first, and keep asking until the answer is verifiable.** "Save CNY 3M" must be decomposed: circuit fees only, or including operations headcount? Do bigger Internet circuits, encryption gateways and a controller add CAPEX and OPEX? **A cost comparison that is not decomposed is usually wrong.**
- **Do not replace wholesale; migrate in tiers.** Office-type traffic suits SD-WAN over Internet; MES control traffic stays on an SLA-bearing link until delay and jitter targets are met — a hybrid WAN.
- **Technical feasibility is not organizational feasibility.** Twelve people with no experience switching everything at once bets production continuity on a learning curve. Pilot five non-critical plants, build a monitoring baseline and a failure playbook, then proceed in batches.
- **Minimum contents of the migration plan**: the site list per batch, the cutover window, business verification cases (MES transaction success rate, not "can we ping"), and **rollback trigger conditions and duration**.
- **The right deliverable is not yes/no but a migration roadmap split by year and by site class, with its risk exposure stated.**

<div class="zh" markdown="1">

**参考思路**：
- **先问"为什么"，并且要问到能验证的层面。** "省 300 万"必须拆开：省的是线路费还是含了运维人力？换掉 MPLS 后 Internet 线路要不要扩容、要不要加加密网关与集中控制器（这些是新增 CAPEX/OPEX）？**不拆开的成本对比通常是错的。**
- **不要整体替换，做分层迁移。** 办公楼宇类流量（办公、视频会议、上网）适合 SD-WAN + Internet；MES 控制流量在时延/抖动不达标前必须留在有 SLA 保障的链路上，可用"混合 WAN"（MPLS 保关键 + Internet 承载其余）。
- **技术可行 ≠ 组织可行。** 12 人无经验，直接全量切换等于把生产连续性押在学习曲线上。现实路径是：选 5 个非关键工厂试点 → 建立监控基线与故障手册 → 再按批次推进。
- **迁移计划的最小要素**：每批次站点清单、切换窗口、业务验证用例（不是 ping 通，而是 MES 交易成功率）、**回退触发条件与回退耗时**（例如"切换后 30 分钟内 MES 时延超标即回退"）。
- **这类"换技术"的决定，正确产出不是"同意/不同意"，而是一份分三年、分站点类型、带风险敞口的迁移路线图。** 见本章「替换技术」用例与"没有充分理由就不要部署 SD-WAN"的告诫。

</div>

---

## Key Terms · 本章关键术语

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

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| Top-down Approach | 自顶向下方法 |
| Bottom-up Approach | 自底向上方法 |
| Functional Requirements | 功能需求 |
| Technical Requirements | 技术需求 |
| Application Requirements | 应用需求 |
| Greenfield | 全新设计 |
| Brownfield | 改造设计 |
| Design Scope | 设计范围 |
| Constraints | 约束条件 |
| Unstated Requirements | 未明确需求 |
| Pervasive Security | 普适安全 |
| Zero Trust Architecture | 零信任架构 |
| Fault Isolation | 故障隔离 |
| Information Hiding | 信息隐藏 |
| Modularity | 模块化 |
| Hierarchy | 层次化 |
| Gold Plating | 过度设计 |
| CAPEX | 资本支出 |
| OPEX | 运营支出 |
| TCO | 总拥有成本 |
| ROI | 投资回报率 |

</div>

---

## Chapter Summary · 本章小结

Chapter 1 delivers **a method, not a set of conclusions**. The whole chapter compresses into one sequence of actions:

<div class="zh" markdown="1">

第 1 章提供的是**设计的方法而不是设计的结论**，全章可以压缩成一个动作序列：

</div>

<figure class="fig">
<img src="assets/fig/en01-10-design-path.svg" alt="Six-step design path from business objective to pre-build review checklist" loading="lazy">
<figcaption><b>Figure 1-10　The chapter as one sequence of actions, and the artefact each step must leave behind</b><br><span>图 1-10　全章动作序列，以及每一步必须留下的文档</span></figcaption>
</figure>

<div class="zh" markdown="1">

六步动作序列与每步应交付的文档见上图：先问"为什么"，再翻译成三类需求，逼出约束，用原则校验，用技术实现，用缺陷自检。

</div>

> **One-line memory**: **design is the path from "why the business cares" to "how the devices connect"; any hop skipped along the way comes back later as rework.**

<div class="zh" markdown="1">

> **一句话记忆**：**设计是从"业务为什么"推导到"设备怎么连"的过程，中间任何一跳被跳过，最后都会以返工的形式补回来。**

</div>

Two points that are most often confused:

<div class="zh" markdown="1">

两个最容易记反的点：

</div>

| Easily confused | Correct understanding |
|-----------------|-----------------------|
| Top-down vs. bottom-up | Not rival camps but **two directions of the same design**: requirements pushed top-down, feasibility verified bottom-up |
| Requirement vs. constraint | A requirement is "what must be achieved"; a constraint is "how it may not be done". Constraints often shape the architecture more than requirements |

<div class="zh" markdown="1">

| 容易记反的地方 | 正确理解 |
|------|---------|
| 自顶向下 vs 自底向上 | 两者不是对立路线，而是**同一份设计的两个方向**：需求自顶向下推，可行性自底向上验。CCDE 考的是"什么时候该切换方向" |
| 需求 vs 约束 | 需求是"要实现什么"，约束是"不能怎么做"。约束往往比需求更能决定架构形态（合规、预算、遗留系统） |

</div>

Two of these principles echo through the remaining chapters: **security is pervasive**, and **without requirements there are no trade-offs**.

<div class="zh" markdown="1">

本章的两条原则会在后面 17 章反复出现：**安全是普适的**（第 4 章展开为原则、第 10 章展开为技术）、**没有需求就没有取舍**（第 2、5 章给出业务与流程侧的落地方法）。

</div>
