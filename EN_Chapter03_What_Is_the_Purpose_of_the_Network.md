# Chapter 3: What's the Purpose of the Network? · 第 3 章：网络的目的是什么？ (What's the Purpose of the Network?)

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapter 3 (pp. 181–208)
>
> Terminology follows the English edition. Every English passage is followed by its Chinese counterpart in the grey block below it, so the two can be checked sentence by sentence.

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译 | 原书第 181-208 页

</div>

---

## Topics Covered · 本章涵盖主题

- **Business applications**: business applications and the network design elements they imply
- **Service models**: the service models and their network design characteristics
- **The cloud**: the various forms of cloud and the related network design elements
- **Data management**: data management methodologies

<div class="zh" markdown="1">

- **业务应用**：业务应用及相关的网络设计要素
- **服务模型**：不同服务模型及其网络设计特征
- **云**：各种形式的云及相关网络设计要素
- **数据管理**：数据管理方法论

</div>

---

## Chapter Overview: Applications Set the Ceiling of the Network · 本章导读：网络的上限由应用决定

Chapter 1 said "derive the network from the business". This chapter turns "business" into something analyzable: **applications and data**. Applications are what actually runs on the network, and every network metric — latency, loss, bandwidth, availability — is meaningful only **for a particular application**.

<div class="zh" markdown="1">

第 1 章说"从业务推导网络"，这一章把"业务"具体化成一个可分析的对象：**应用和数据**。因为最终跑在网络上的是应用，网络的所有指标（时延、丢包、带宽、可用性）只有在**某个应用身上**才有意义。

</div>

Eight lessons that are easy to miss:

<div class="zh" markdown="1">

八个容易踩空的认知：

</div>

**1. Application architecture is an input to network design, not an output.** Monolithic, two-tier, three-tier, N-tier, microservices — the architecture decides whether traffic is mostly north-south or mostly east-west, how many hops one user action takes, and how much latency can be tolerated. **Changing the network to fit the application is always cheaper than the reverse.**

<div class="zh" markdown="1">

**1. 应用架构是网络设计的输入，不是输出。** 单体应用、两层、三层、N 层、微服务——它们决定流量是"南北向为主"还是"东西向为主"，决定一次用户操作要经过几跳、能容忍多少时延。**先改网络去适配应用，从来比反过来便宜。**

</div>

**2. The latency budget is measured per business transaction, not per hop.** One click on submit may traverse 30 service calls; 5 ms extra per call means 150 ms of extra waiting. In a three-tier model, every cross-tier call consumes the budget.

<div class="zh" markdown="1">

**2. 时延预算要按"一次业务事务"算，不是按"一跳"算。** 用户点一次提交，可能经过 30 次服务调用；每次多 5ms，用户就多等 150ms。三层模型里每个跨层调用都是预算的消耗点。

</div>

**3. The more "modern" the application model, the harder the network work.** A monolith only needs reachability; microservices need service discovery, east-west policy, distributed tracing and finer fault isolation. **Architecture evolution is not free — cost moves from servers into the network and into observability.**

<div class="zh" markdown="1">

**3. 应用模型越"现代"，网络越难做。** 单体应用只需要"通"；微服务需要服务发现、东西向策略、分布式追踪、更细的故障隔离。**架构演进不是免费的，成本会从服务器转移到网络和可观测性上。**

</div>

**4. The service model (IaaS/PaaS/SaaS) decides how much control you have left.** Choosing SaaS means handing part of availability, performance and security responsibility to the provider, and your design focus shifts from "build" to "select + integrate + backstop". **Do not design SaaS assurance with an IaaS mindset.**

<div class="zh" markdown="1">

**4. 服务模型（IaaS/PaaS/SaaS）决定你还剩下多少控制权。** 选 SaaS 等于把可用性、性能、安全的一部分责任交给供应商，你的设计重点从"建"变成"选 + 集成 + 兜底"。**别用 IaaS 的思路去设计 SaaS 的保障。**

</div>

**5. Moving to cloud is not "moving servers elsewhere", it is "changing the shape of the failure domain".** There is no longer a "my data center" boundary; instead there are regions, availability zones and the shared responsibility model. **The old single point disappears, but new shared failures appear (region-level failure, single sign-on, DNS).**

<div class="zh" markdown="1">

**5. 上云不是"把服务器搬到别处"，是"改变故障域的形状"。** 云上不再有"我的机房"这个边界，取而代之的是区域、可用区、云服务共享责任模型。**原来的单点消失了，但新的共享故障（云区域级故障、单点登录、DNS）出现了。**

</div>

**6. The core of choosing a cloud connection model is determinism, not bandwidth.** The difference between Internet, VPN, dedicated circuits and cloud exchange lies mainly in whether latency and loss are predictable and who carries the SLA. **Business that demands determinism cannot be satisfied by "plenty of bandwidth".**

<div class="zh" markdown="1">

**6. 云连接模型的选择核心是"确定性"，不是"带宽"。** Internet、VPN、专线、云交换的差别，主要在于时延与丢包是否可预期、SLA 由谁承担。**要求确定性的业务，不能靠"带宽够大"来满足。**

</div>

**7. Cloud-agnostic has a price.** Avoiding vendor lock-in means giving up that cloud's managed services, native networking and native security, and implementing your own abstraction layer instead. **You gain portability and pay in operational complexity and performance loss.** It is a deliberate trade-off, not a more advanced practice.

<div class="zh" markdown="1">

**7. Cloud-agnostic 是有代价的。** 不绑定云厂商，意味着放弃该云的托管服务、原生网络与安全能力，转而自己实现一层抽象——**换来的是可迁移性，付出的是运维复杂度和性能折损**。这是一个明确的取舍，不是"更高级的做法"。

</div>

**8. Data management drives compliance and backup design, yet it is often outside the network team's field of view.** Classification, residency, retention, encryption, backup and destruction — at least half of the eleven pillars turn directly into network requirements (which path, may it leave the country, who may access it).

<div class="zh" markdown="1">

**8. 数据管理决定合规与备份设计，而它常常不在网络团队的视野里。** 数据分级、驻留、留存、加密、备份、销毁——这 11 个支柱里至少有一半会直接变成网络要求（走哪条路径、能不能出境、谁能访问）。

</div>

> **One-sentence summary**: **first understand which applications run, where the data sits and who provides the service; only then discuss how the network connects. Reverse the order and design becomes guesswork.**

<div class="zh" markdown="1">

> **一句话概括这一章**：**先看清"跑的是什么应用、数据放在哪、服务由谁提供"，再谈网络怎么连——顺序反了，设计就只能靠猜。**

</div>

---

## Foundation Topics · 基础内容

> What is the purpose of the network? Why do we need a network? A network designer should keep these questions in mind at all times, because understanding the purpose and goals of the network is essential to designing it correctly.

<div class="zh" markdown="1">

> 网络的目的是什么？为什么需要网络？这些问题应始终在网络设计师脑海中，因为理解网络的目的和目标对正确设计至关重要。

</div>

From a purely technical angle, the purpose of the network is to move data from point A to point B at the right time. From a design angle we must go further: **the fundamental purpose of moving that data is to achieve business outcomes and goals — to make the business successful.**

<div class="zh" markdown="1">

从技术角度回答：网络的目的是在正确的时间内将数据从 A 点传输到 B 点。但从网络设计角度，我们需要更进一步——**网络传输数据的根本目的是实现业务成果和目标，让业务成功！**

</div>

Enterprises now depend on the network so heavily that its availability, and that of the services attached to it, must be designed to a very high level. The traditional telephone network (POTS) is the precedent: people relied on it so completely that overall availability had to be engineered to an extreme level.

<div class="zh" markdown="1">

企业对网络的依赖已经到了必须将网络及其相关服务的可用性设计到极高水平的地步。就像传统电话网络 (POTS) 一样——人们如此依赖它，以至于整体可用性必须设计到极高水平。

</div>

---

## Business Applications · 业务应用

The network is the information highway of today's business applications. For the business to succeed, those applications must communicate correctly and on demand between users, devices, data, databases and other application components.

<div class="zh" markdown="1">

网络是当今业务应用的"信息高速公路"。为了让业务成功，这些应用必须能在用户、设备、数据、数据库和其他应用组件之间按需正确通信。

</div>

### Application Models · 应用模型

A network designer needs to understand how applications are built in order to design a network that supports them properly.

<div class="zh" markdown="1">

网络设计师需要了解应用的构建方式，以便正确设计支持该应用的网络。

</div>

#### 1. Single-Server Model · 单服务器模型

The simplest application model, equivalent to running an application on a personal computer. Every component the application needs runs on a single application server.

<div class="zh" markdown="1">

最简单的应用模型，相当于在个人计算机上运行应用。应用运行所需的所有组件都在单个应用或服务器上。

</div>

#### 2. 2-Tier Model · 二层模型

Similar to client/server architecture. The presentation layer (user interface) runs on the client, while the data set layer executes and stores on the server. There is no intermediate application layer between client and server.

<div class="zh" markdown="1">

类似客户端/服务器架构。表示层（用户界面层）运行在客户端，数据集层在服务器端执行和存储。客户端和服务器之间没有中间层（应用层）。

</div>

#### 3. 3-Tier Model · 三层模型

The most common application model today, made up of three tiers:

<div class="zh" markdown="1">

目前最常见的应用模型，包含三层：

</div>

| Tier | Name | Function |
|------|------|----------|
| **Presentation** | Web tier / GUI tier | The front end where end users access and interact. Translates tasks and results into something the user understands |
| **Intermediate** | Application tier / logic tier | Processes tasks, functions and commands; makes decisions and evaluations; performs computation; moves data between the presentation and database tiers |
| **Database** | Data tier | Stores and retrieves information and returns it to the intermediate tier, and eventually to the end user |

<div class="zh" markdown="1">

| 层级 | 名称 | 功能 |
|------|------|------|
| **表示层 (Presentation)** | Web 层 / GUI 层 | 前端，最终用户访问和交互的界面。将任务和结果翻译为用户可理解的形式 |
| **中间层 (Intermediate)** | 应用层 / 逻辑层 | 应用的功能和逻辑处理层。处理任务、函数和命令，做出决策和评估，执行计算。在表示层和数据库层之间移动数据 |
| **数据库层 (Database)** | 数据层 | 存储和检索信息，传回中间层，最终返回给最终用户 |

</div>

> 💡 Splitting an application into tiers (n-tier architecture) lets a network designer **design the network for each tier separately**. Each tier may need its own load balancing, source NAT, DNS, source routing and traffic engineering.

<div class="zh" markdown="1">

> 💡 将应用拆分为不同层级（n 层架构）使网络设计师可以**为每层单独设计网络**。每层可能需要自己的负载均衡、源 NAT、DNS、源路由和流量工程设计。

</div>

<figure class="fig">
<img src="assets/fig/en03-01-app-models.svg" alt="Single server, two tier, three tier and microservices shown side by side with hop counts and a network-work gauge rising left to right" loading="lazy">
<figcaption><b>Figure 3-1　Four application models, and what each one costs the network</b><br><span>图 3-1　四种应用模型，以及各自让网络付出的代价</span></figcaption>
</figure>

### Network Design Elements of the 3-Tier Model · 三层模型的网络设计要素

| Tier | Traffic pattern | Network design elements | Questions to consider |
|------|-----------------|-------------------------|-----------------------|
| **Web tier** | End users ↔ web tier | No database-tier access. Usually placed in a DMZ | How do end users reach the web tier globally? How is the web tier's specific network or IP routed? What HA design does the web tier use (active/active, active/standby, anycast)? |
| **Application tier** | Web tier ↔ application tier | Internal access only, no external addresses or routing. Load balancing applied. Usually behind multiple layers of internal security | How does the web tier talk to the application tier? How does the database tier talk to the application tier (SNAT, NAT, stickiness)? |
| **Database tier** | Application tier ↔ database tier | Internal access only. Usually behind multiple layers of internal security | How do database member servers replicate? How are database changes synchronized (especially across data centers)? |

<div class="zh" markdown="1">

| 层级 | 流量模式 | 网络设计要素 | 需要考虑的问题 |
|------|---------|------------|--------------|
| **Web 层** | 最终用户 ↔ Web 层 | 无数据库层访问。通常位于 DMZ | 最终用户如何全球访问 Web 层？Web 层特定网络/IP 如何路由？Web 层高可用架构如何？(Active/Active, Active/Standby, Anycast 等) |
| **应用层** | Web 层 ↔ 应用层 | 仅内部访问，无外部地址或路由。实施负载均衡。通常位于内部多层安全之后 | Web 层如何与应用层通信？数据库层如何与应用层通信？(SNAT, NAT, Sticky 等) |
| **数据库层** | 应用层 ↔ 数据库层 | 仅内部访问。通常位于内部多层安全之后 | 不同数据库成员服务器之间如何复制？数据库变更如何同步？(多数据中心场景尤为重要) |

</div>

<figure class="fig">
<img src="assets/fig/en03-02-three-tier-design-elements.svg" alt="Global users, Internet edge and firewall above a DMZ web tier, then an internal application tier and database tier, each annotated with its network elements and open questions" loading="lazy">
<figcaption><b>Figure 3-2　Three tiers, three access scopes, three sets of network elements</b><br><span>图 3-2　三层、三套访问范围、三组网络要素</span></figcaption>
</figure>

### Application Constraints and Requirements · 应用约束和需求

Common application constraints and requirements a network designer should know:

<div class="zh" markdown="1">

网络设计师需要了解的常见应用约束和需求：

</div>

| Constraint / requirement | Description |
|--------------------------|-------------|
| **Multicast** | Often used to keep server clusters synchronized (for example back-end database replication) or as the transport for streaming applications (IPTV, real-time stock updates). An application breaks if multicast is not supported |
| **Layer 2 extension** | One of the most common network design requirements. Application servers do not communicate outside their Layer 2 segment. The designer has to provide Layer 2 extension options — which leads to poor designs with large Layer 2 failure domains, but it does solve the application's problem |
| **Hardcoded items** | IP addresses, host names and similar values embedded in code. They must be mitigated with NAT, traffic engineering and source routing |
| **High availability** | How the application is designed for HA directly shapes the network. Multiple sites? How is data synchronized? Active/standby or active/active? What load-balancing method? Is SNAT required? |

<div class="zh" markdown="1">

| 约束/需求 | 说明 |
|-----------|------|
| **组播 (Multicast)** | 通常用于服务器集群间保持数据同步（如后端数据库复制），或作为数据流应用的传输机制（如 IPTV 和实时股市更新）。不支持组播会破坏应用 |
| **二层扩展 (Layer 2 Extension)** | 最常见的网络设计需求之一。应用服务器不在其二层段外通信。网络设计师需要提供二层扩展选项——这导致大型二层故障域的糟糕网络设计，但确实解决了应用需求 |
| **硬编码项 (Hardcoded Items)** | 代码中硬编码的 IP 地址、主机名等。需要通过 NAT、流量工程和源路由来缓解 |
| **高可用性 (High Availability)** | 应用如何设计高可用直接影响网络。多地点？数据如何同步？Active/Standby 还是 Active/Active？负载均衡方式？是否需要 SNAT？ |

</div>

> ⚠️ **Note for network designers**: many network design problems originate in poor application development. Being forced to provide Layer 2 extension as a band-aid is the classic example — a short-term fix that becomes permanent. Network designers and security specialists should take part in the application build and review process.

<div class="zh" markdown="1">

> ⚠️ **网络设计师应注意**：很多网络设计问题源于应用开发不当。例如被迫提供二层扩展作为"创可贴"方案——本应是短期方案却变成了永久方案。网络设计师和安全专家应参与应用构建和审查过程。

</div>

---

<figure class="fig">
<img src="assets/fig/en03-03-application-trait-matrix.svg" alt="Matrix of seven traits against video conferencing, file backup, ERP transactions and database replication, with colour marking the critical cells" loading="lazy">
<figcaption><b>Figure 3-3　Describe an application by its traits, never by its name</b><br><span>图 3-3　用特征描述应用，而不是用名字</span></figcaption>
</figure>

## Service Models · 服务模型

The service model determines where the application lives and which elements of it the enterprise owns and manages.

<div class="zh" markdown="1">

服务模型决定了应用的位置以及应用的哪些元素由企业拥有和管理。

</div>

### The Four Main Service Models · 四种主要服务模型

#### 1. On-Premises · 本地部署

The enterprise owns and manages the application. It buys all the infrastructure needed to run the service and then manages, maintains and operates it completely.

<div class="zh" markdown="1">

企业拥有和管理应用。企业采购运行服务所需的所有基础设施，然后完全管理、维护和运营。

</div>

**Characteristics**:
- Full control over every component
- Available locally
- Hosted in the enterprise server environment

<div class="zh" markdown="1">

**特点**：
- 完全控制所有组件
- 本地可用
- 托管在企业服务器环境中

</div>

**When to use**: when full control of all application components is required, commonly driven by security, compliance and data classification requirements.

<div class="zh" markdown="1">

**适用场景**：需要完全控制应用所有组件时，常见于安全合规和数据分类要求

</div>

#### 2. Software as a Service (SaaS) · 软件即服务

The provider delivers software to users over the Internet, usually on a monthly or annual subscription.

<div class="zh" markdown="1">

供应商通过 Internet 向用户提供软件，通常按月或年订阅。

</div>

**Characteristics**:
- Nothing to install or run on any computer
- Everything is accessed over the Internet
- Accessible from any device, at any time, anywhere with an Internet connection
- Scalable, delivered on demand

<div class="zh" markdown="1">

**特点**：
- 无需在任何计算机上安装和运行软件
- 一切通过 Internet 访问
- 可从任何设备、任何时间、有 Internet 连接的地方访问
- 可扩展，按需提供服务

</div>

**When to use**: when you want the application to assure availability but do not want to maintain the application.

<div class="zh" markdown="1">

**适用场景**：希望应用确保可用性但不想维护应用时

</div>

#### 3. Platform as a Service (PaaS) · 平台即服务

The provider supplies the hardware and software tools, and the customer uses those tools to develop applications. PaaS users are typically application developers.

<div class="zh" markdown="1">

供应商提供硬件和软件工具，用户使用这些工具开发应用。PaaS 用户通常是应用开发者。

</div>

**Characteristics**:
- Primarily for developers creating software and applications
- Scalable
- Built on virtualization technology
- Applications can be created without starting from scratch
- Easy to run without deep IT knowledge

<div class="zh" markdown="1">

**特点**：
- 主要供开发者创建软件和应用
- 可扩展
- 基于虚拟化技术构建
- 无需从头开始即可创建应用
- 易于运行，无需深入 IT 知识

</div>

**When to use**: when you want to build a distinctive application without large capital outlay or full responsibility.

<div class="zh" markdown="1">

**适用场景**：希望创建独特应用但不想花费大量资金或承担全部责任时

</div>

#### 4. Infrastructure as a Service (IaaS) · 基础设施即服务

An on-demand, pay-as-you-go model for storage, networking and virtualization services — covering the enterprise's infrastructure needs.

<div class="zh" markdown="1">

按需付费的存储、网络和虚拟化服务模型——满足企业所有基础设施需求。

</div>

**Characteristics**:
- Highly flexible
- Highly scalable
- Accessible by multiple tenants
- Cost-effective
- The enterprise keeps control of the infrastructure

<div class="zh" markdown="1">

**特点**：
- 高度灵活
- 高度可扩展
- 多用户可访问
- 成本效益高
- 企业保持对基础设施的控制

</div>

**When to use**: when you need full control of the virtual infrastructure but want to pay as you go.

<div class="zh" markdown="1">

**适用场景**：需要完全控制虚拟基础设施但希望按需付费时

</div>

### Service Model Comparison · 服务模型对比

| Model | Characteristic | Advantage | When it fits |
|-------|----------------|-----------|--------------|
| **On-premises** | Owned and managed by the enterprise | Full control of all components | When full control is required (security, compliance, data classification) |
| **SaaS** | Available over the Internet | Nothing to install, available everywhere | When you want assurance without maintenance |
| **PaaS** | Multi-tenant access | Developers do not start from zero | When you want a distinctive application without full responsibility |
| **IaaS** | Highly flexible and scalable | Pay as you go while keeping control | When you need infrastructure control with on-demand cost |

<div class="zh" markdown="1">

| 模型 | 特点 | 优势 | 适用场景 |
|------|------|------|---------|
| **本地部署** | 企业拥有和管理 | 完全控制所有组件 | 需要完全控制（安全合规、数据分类） |
| **SaaS** | 通过 Internet 可用 | 无需安装，一切可用 | 希望应用确保可用但不想维护 |
| **PaaS** | 多用户可访问 | 开发者无需从零开始 | 想创建独特应用但不想承担全部责任 |
| **IaaS** | 高度灵活可扩展 | 按需付费，保持控制 | 需要完全控制基础设施但希望按需付费 |

</div>

---

<figure class="fig">
<img src="assets/fig/en03-04-service-model-stack.svg" alt="Four columns for on-premises, IaaS, PaaS and SaaS, seven layers each shaded by whether the enterprise or the provider operates it, ending in what the network still owes" loading="lazy">
<figcaption><b>Figure 3-4　Who operates which layer, and what the network still owes</b><br><span>图 3-4　谁运维哪一层，以及网络还欠什么</span></figcaption>
</figure>

## The Cloud · 云

When an enterprise starts using any form of cloud, a network designer should consider three use cases:

<div class="zh" markdown="1">

当企业开始利用任何形式的云时，网络设计师应考虑三个用例：

</div>

1. **Securely extend the private network into one or more public cloud environments**: multi-cloud, multi-region and multi-VPC connectivity; VPN; extending the data center into the cloud; branch-to-cloud direct connectivity
2. **Optimize connectivity performance from the data center and branches to cloud IaaS and SaaS**: best-path selection, cloud segmentation, monitoring, shaping and QoS
3. **Secure access from branches to the Internet and SaaS**: use direct Internet access (DIA) to connect branch users securely to multi-cloud environments

<div class="zh" markdown="1">

1. **安全地将私有网络扩展到单个或多个公有云环境**：包括多云、多区域、多 VPC 连接；VPN；扩展数据中心到云；启用分支到云的直接连接
2. **优化数据中心和分支到云 IaaS 和 SaaS 的连接性能**：包括最佳路径选择、云分段、监控、流量整形/QoS
3. **保护从分支到 Internet 和 SaaS 的访问**：使用直接互联网接入 (DIA) 安全地连接分支用户到多云环境

</div>

### Cloud Connection Models · 云连接模型

#### 1. Direct Cloud Access (DCA) · 直接云接入

Lets remote sites reach SaaS applications directly over the Internet through a dedicated private connection.

<div class="zh" markdown="1">

允许远程站点直接从 Internet 访问 SaaS 应用，通过专用私有连接。

</div>

- The cloud allows only specified application traffic onto the directly connected Internet transport
- Other Internet traffic follows the usual path (through a regional hub, data center or CNF)
- The edge router selects the best Internet path to the SaaS application
- Different applications can take different paths (per-application path selection)
- A path is removed from the candidate set if it is unreachable or underperforms
- Commonly called **direct Internet access (DIA)**

<div class="zh" markdown="1">

- 云仅允许指定应用流量使用直接连接的 Internet 传输
- 其他 Internet 流量走通常路径（通过区域中心、数据中心或 CNF）
- 边缘路由器选择最优 Internet 路径访问 SaaS 应用
- 不同应用可以走不同路径（按应用选择路径）
- 如果路径不可达或性能不达标，移除该路径候选
- 通常称为**直接互联网接入 (DIA)**

</div>

#### 2. Cloud Access Through a Gateway · 通过网关的云接入

Many enterprises do not use DIA at the branch, either because they connect only through a private provider or because centralized policy and security requirements forbid it.

<div class="zh" markdown="1">

许多企业不在分支使用 DIA（因为仅通过私有提供商连接，或集中策略/安全要求不允许）。

</div>

- SaaS traffic is tunneled to the gateway site with the best performance
- At the gateway site it is routed to the Internet to reach the SaaS application
- Remote sites that use a gateway site are called **client sites**
- Different remote sites and applications can use different gateway sites and paths

<div class="zh" markdown="1">

- SaaS 流量通过隧道发送到最佳性能的网关站点
- 在网关站点路由到 Internet 访问 SaaS 应用
- 使用网关站点的远程站点称为**客户端站点 (Client Sites)**
- 不同远程站点和应用可使用不同网关站点和路径

</div>

#### 3. Hybrid Approach · 混合方法

A combination of DIA and client/gateway sites. SaaS applications can egress via DIA or via a gateway site, depending on which path delivers the best performance.

<div class="zh" markdown="1">

DIA 和客户端/网关站点的组合。SaaS 应用可以使用 DIA 出口或网关站点，取决于哪条路径提供最佳性能。

</div>

<figure class="fig">
<img src="assets/fig/en03-05-cloud-connection-models.svg" alt="Direct cloud access, gateway hairpin and hybrid shown as three traffic paths, beside a panel on determinism, SLA ownership and what to write into the design" loading="lazy">
<figcaption><b>Figure 3-5　Three cloud connection models — determinism decides, not bandwidth</b><br><span>图 3-5　云连接三模型：决定因素是对确定性，而不是带宽</span></figcaption>
</figure>

### Cloud Types · 云类型

| Cloud type | Definition | Characteristic |
|------------|------------|----------------|
| **Private cloud** | Cloud resources dedicated to a single enterprise. May live inside the enterprise data center or be hosted by a CSP | Resources are kept on a private network and all equipment is dedicated to that enterprise |
| **Public cloud** | The most common form of cloud computing. Resources are owned and operated by a CSP | Hardware, storage, virtualization and network devices are shared with other enterprises |
| **Hybrid cloud** | Uses private and public cloud at the same time | Gets the benefits of both environments while limiting their downsides |
| **Multi-cloud** | Uses two or more CSPs | Workloads can be moved between cloud environments in real time |

<div class="zh" markdown="1">

| 云类型 | 定义 | 特点 |
|--------|------|------|
| **私有云 (Private Cloud)** | 云计算资源由一个企业专用。可在企业数据中心内或由 CSP 托管 | 资源在私有网络上维护，所有设备专用于该企业 |
| **公有云 (Public Cloud)** | 最常见的云计算类型。资源由 CSP 拥有和运营 | 与其他企业共享硬件、存储、虚拟化和网络设备 |
| **混合云 (Hybrid Cloud)** | 同时使用私有云和公有云 | 获得两种云环境的优势同时限制其负面影响 |
| **多云 (Multi-cloud)** | 使用两个或更多 CSP | 可在不同云环境间实时移动工作负载 |

</div>

### Cloud Type Comparison in Detail · 云类型详细对比

| Cloud type | Control | Maintenance | Flexibility | Scalability | Migration | Cost |
|------------|---------|-------------|-------------|-------------|-----------|------|
| **Private cloud** | Most control | High | Lowest flexibility | Highly scalable | Hard to migrate | High cost |
| **Public cloud** | Least control | None | Flexible | Highly scalable | Hard to migrate | Lowest cost |
| **Hybrid cloud** | Mixed | Medium | Flexible | Lowest scalability | Easy to migrate | High cost |
| **Multi-cloud** | Least control | High, per CSP | Highest flexibility across CSPs | Highest scalability | Hardest to migrate | Highest cost |

<div class="zh" markdown="1">

| 云类型 | 控制权 | 维护 | 灵活性 | 可扩展性 | 迁移 | 成本 |
|--------|--------|------|--------|---------|------|------|
| **私有云** | 最多控制 | 高 | 最低灵活性 | 高可扩展性 | 难迁移 | 高成本 |
| **公有云** | 最少控制 | 无 | 灵活 | 高可扩展性 | 难迁移 | 最低成本 |
| **混合云** | 两者混合 | 中等 | 灵活 | 最低可扩展性 | 易迁移 | 高成本 |
| **多云** | 最少控制 | 每个 CSP 维护高 | 跨 CSP 最高灵活性 | 最高可扩展性 | 最难迁移 | 最高成本 |

</div>

<figure class="fig">
<img src="assets/fig/en03-06-cloud-types-tradeoff.svg" alt="Private, public, hybrid and multi-cloud positioned on control against cost, with a table of the strength and price of each type" loading="lazy">
<figcaption><b>Figure 3-6　Four cloud types: control and cost trade against each other</b><br><span>图 3-6　云类型四选一：控制力与成本此消彼长</span></figcaption>
</figure>

### Cloud-Agnostic Architecture · 云无关架构

A cloud-agnostic architecture avoids vendor-specific proprietary features and focuses on using the same cloud capabilities across different cloud providers.

<div class="zh" markdown="1">

云无关架构不使用厂商特定的专有功能。专注于在不同云提供商之间利用相同的云能力。

</div>

#### The Three Core Concerns · 三大核心关注点

| Concern | Definition | Value |
|---------|------------|-------|
| **Portability** | The ability to move applications and services between CSPs | Movement across CSPs through an appropriate abstraction layer |
| **Abstraction** | Decoupling from underlying cloud-specific platform features using an abstraction layer | Directly lowers cost and increases flexibility |
| **Interoperability** | Building applications and services that are not bound to a specific cloud feature set | Allows use of different cloud platforms without major rework |

<div class="zh" markdown="1">

| 关注点 | 定义 | 价值 |
|--------|------|------|
| **可移植性 (Portability)** | 在不同 CSP 之间移动应用和服务的能力 | 通过适当的抽象层实现跨 CSP 移动 |
| **抽象 (Abstraction)** | 使用抽象层与底层云特定平台功能解耦 | 直接降低成本，增加灵活性 |
| **互操作性 (Interoperability)** | 开发不被绑定到特定云功能集的应用和服务 | 允许利用不同云平台而无需重大重新开发 |

</div>

#### Practices That Deliver Cloud Agnosticism · 实现云无关的实践

1. **Decoupling**:
   - Decouple the application from the underlying cloud platform (through service-oriented architecture, SOA)
   - Decouple the cloud components from the applications that consume them
2. **Containerization**:
   - All applications should follow a containerized architecture
   - Containers help decouple applications from a cloud-specific environment
   - They make it relatively easy to move applications between cloud providers
3. **Cloud-agnostic vs. proprietary cloud services**:
   - Distinguish how cloud-agnostic services and cloud-proprietary services interact with the application
   - Plan how the application will be migrated to a CSP

<div class="zh" markdown="1">

1. **解耦 (Decoupling)**：
   - 应用与底层云平台解耦（通过面向服务架构 SOA）
   - 云组件与使用它们的应用解耦
2. **容器化 (Containerization)**：
   - 所有应用应遵循容器化架构
   - 容器帮助将应用与云特定环境解耦
   - 确保在不同云厂商之间迁移应用相对容易
3. **云无关 vs 专有云服务**：
   - 需要区分云无关服务和云专有服务如何与应用交互
   - 规划应用迁移到 CSP 的方式

</div>

<figure class="fig">
<img src="assets/fig/en03-07-cloud-agnostic-tradeoff.svg" alt="An application above an abstraction layer of SOA, containers and declarative configuration, feeding two cloud providers and the own data centre, with gains and losses listed and the three concerns explained" loading="lazy">
<figcaption><b>Figure 3-7　Cloud agnosticism is a trade, not an upgrade</b><br><span>图 3-7　云无关是一场交易，而不是一次升级</span></figcaption>
</figure>

### Service-Oriented Architecture (SOA) · 面向服务架构

SOA is the key software design style that makes a cloud-agnostic architecture succeed.

<div class="zh" markdown="1">

SOA 是确保云无关架构成功的关键软件设计风格。

</div>

**The core of SOA**: services are offered to other parts of the application through network communication protocols. The underlying principles are vendor- and technology-neutral.

<div class="zh" markdown="1">

**SOA 的核心**：服务通过网络通信协议提供给应用组件的其他部分。底层原则是厂商和技术无关的。

</div>

**Ways services communicate**:
1. Passing data between different services
2. Coordinating events between two or more services

<div class="zh" markdown="1">

**服务间通信方式**：
1. 在不同服务之间传递数据
2. 在两个或多个服务之间协调活动事件

</div>

**Benefits of SOA**:
- Reusable code, which shortens development time
- Support for multiple coding languages through a central interface
- A standard communication flow
- Better scalability by limiting client-server interactions

<div class="zh" markdown="1">

**SOA 的好处**：
- 代码可复用，减少开发时间
- 支持多种编码语言（使用中央接口）
- 创建标准通信流程
- 更高的可扩展性，限制客户端-服务器交互

</div>

### Cloud Containerized Architecture · 云容器化架构

The evolution from traditional deployment to containerized cloud deployment:

<div class="zh" markdown="1">

从传统部署到容器化云部署的演进：

</div>

```
Traditional            Virtualized            Containerized
┌──────────┐         ┌──────────────┐      ┌──────────────┐
│ Physical  │         │  Physical     │      │  Physical     │
│ server    │         │  server       │      │  server       │
│ App A     │         │ ┌──────────┐ │      │ ┌──────────┐ │
│ App B     │         │ │ VM1      │ │      │ │Container1│ │
│ (resource │         │ │ App A OS │ │      │ │ App A    │ │
│  contention)│       │ └──────────┘ │      │ ├──────────┤ │
│           │         │ ┌──────────┐ │      │ │Container2│ │
│           │         │ │ VM2      │ │      │ │ App B    │ │
│           │         │ │ App B OS │ │      │ ├──────────┤ │
│           │         │ └──────────┘ │      │ │ Shared OS│ │
│           │         │  Hypervisor   │      │ └──────────┘ │
└──────────┘         └──────────────┘      └──────────────┘
```

<div class="zh" markdown="1">

```
传统部署               虚拟化部署              容器部署
┌──────────┐         ┌──────────────┐      ┌──────────────┐
│ 物理服务器 │         │  物理服务器    │      │  物理服务器    │
│          │         │ ┌──────────┐ │      │ ┌──────────┐ │
│ 应用A     │         │ │ VM1      │ │      │ │ 容器1    │ │
│          │         │ │ 应用A OS │ │      │ │ 应用A    │ │
│ 应用B     │         │ └──────────┘ │      │ ├──────────┤ │
│          │         │ ┌──────────┐ │      │ │ 容器2    │ │
│ (资源竞争) │         │ │ VM2      │ │      │ │ 应用B    │ │
│          │         │ │ 应用B OS │ │      │ ├──────────┤ │
│          │         │ └──────────┘ │      │ │ 共享 OS   │ │
│          │         │  Hypervisor  │      │ └──────────┘ │
└──────────┘         └──────────────┘      └──────────────┘
```

</div>

| Deployment style | Characteristic |
|------------------|----------------|
| **Traditional** | Applications run on physical servers. Resources cannot be limited or controlled properly. Each server is usually dedicated to a single application |
| **Virtualized** | Multiple VMs on one physical server. Each VM is isolated with its own resources and security controls, and each runs every component (application plus operating system) |
| **Containerized** | Similar to VMs but with looser isolation, allowing a shared operating system. Lightweight, with its own file system and shared CPU time, memory and process space. Portable across infrastructure |

<div class="zh" markdown="1">

| 部署方式 | 特点 |
|---------|------|
| **传统部署** | 应用在物理服务器上运行。无法正确限制资源或设置控制。通常每台服务器专用于单个应用 |
| **虚拟化部署** | 多个 VM 在单台物理服务器上。每个 VM 独立隔离，有自己的资源和安全控制。每个 VM 运行所有组件（应用 + 操作系统） |
| **容器部署** | 类似 VM 但隔离控制不那么严格，允许共享操作系统。轻量级。有自己的文件系统、共享 CPU 时间、内存、进程空间。可在不同基础设施间移动 |

</div>

**Benefits of containers**:
- Agile application creation and deployment (CI/CD)
- Separation of development and operations duties
- Real-time application-level health analytics
- Consistency across all environments
- Real-time distribution to other operating systems and locations
- Better predictability of application performance
- Better resource efficiency

<div class="zh" markdown="1">

**容器的好处**：
- 敏捷的应用创建和部署 (CI/CD)
- 开发和运维任务职责分离
- 实时应用级健康分析
- 跨所有环境的一致性
- 实时分发到其他操作系统和位置
- 提高应用性能的可预测性
- 提高资源效率

</div>

<figure class="fig">
<img src="assets/fig/en03-08-deployment-evolution.svg" alt="Traditional, virtualised and containerised stacks side by side, with what each changes for the network: one address, MAC and VLAN growth, or thousands of short-lived east-west endpoints" loading="lazy">
<figcaption><b>Figure 3-8　Traditional, virtualised, containerised — and what the network inherits</b><br><span>图 3-8　传统、虚拟化、容器化：网络继承了什么</span></figcaption>
</figure>

### Cloud Application Strategy · 云应用策略

When an enterprise prepares to migrate applications to the cloud, an **application assessment process** should be built in. Form an application assessment team:

<div class="zh" markdown="1">

企业准备将应用迁移到云时，建议纳入**应用评估流程**。创建应用评估团队：

</div>

| Role | Responsibility |
|------|----------------|
| **Business line owner** | The business stakeholder for the application, who understands its business role and impact |
| **Security specialist / compliance auditor** | Owns security controls, regulatory compliance and code audit |
| **Application owner / developer** | The software engineering member who creates and changes the code |
| **Network engineer / designer / architect** | Provides the network resources that serve the application correctly |

<div class="zh" markdown="1">

| 角色 | 职责 |
|------|------|
| **业务线负责人** | 应用的业务利益相关者。理解应用的业务角色和影响 |
| **安全专家/合规审计员** | 负责安全控制、合规法规和代码审计 |
| **应用负责人/开发者** | 软件工程成员，负责创建和修改代码 |
| **网络工程师/设计师/架构师** | 提供网络资源以正确服务应用 |

</div>

---

## Data Management · 数据管理

> Data is the most critical resource that all other resources will consume. All data must be managed effectively, accurately and securely so that other resources can use it correctly, preserving integrity, availability and confidentiality.

<div class="zh" markdown="1">

> 数据是所有其他资源将利用的最关键资源。必须有效、准确、安全地管理所有数据，使其他资源能够正确利用数据，确保完整性、可用性和机密性。

</div>

Data management lays the foundation for data analytics. Without good data management there is no data analytics.

<div class="zh" markdown="1">

数据管理为数据分析奠定基础。没有良好的数据管理，就没有数据分析。

</div>

### The Eleven Pillars of Data Management · 数据管理的 11 大支柱

| Pillar | Definition |
|--------|------------|
| 1. **Data governance** | Planning every aspect of data management, including availability, usability, consistency, integrity and security |
| 2. **Data architecture** | The overall structure of enterprise data and how it fits into enterprise architecture |
| 3. **Data modeling and design** | Data analysis and the corresponding analytical systems, including design, build, test and ongoing maintenance |
| 4. **Data storage and operations** | The physical hardware used to store and manage data |
| 5. **Data security** | All security requirements, controls and components that keep data protected and accessible only to authorized users |
| 6. **Data integration and interoperability** | Transforming data into structured form so other systems and resources can use it |
| 7. **Documents and content** | All forms of unstructured data and the work needed to make it accessible |
| 8. **Reference and master data** | Managing data in a way that allows redundancy, with errors normalized through standard values |
| 9. **Data warehousing and business intelligence** | Managing and applying data for analytics and business decisions |
| 10. **Metadata** | Creating, collecting, organizing and managing metadata (data that references other data) |
| 11. **Data quality** | Data monitoring practices that keep the integrity of delivered data intact |

<div class="zh" markdown="1">

| 支柱 | 定义 |
|------|------|
| 1. **数据治理 (Data Governance)** | 规划数据管理的所有方面，包括可用性、可用性、一致性、完整性和安全性 |
| 2. **数据架构 (Data Architecture)** | 企业数据的整体结构及其如何融入企业架构 |
| 3. **数据建模和设计 (Data Modeling and Design)** | 数据分析及相应的分析系统，包括设计、构建、测试和持续维护 |
| 4. **数据存储和运营 (Data Storage and Operations)** | 用于存储和管理数据的物理硬件 |
| 5. **数据安全 (Data Security)** | 确保数据受保护且仅被授权用户访问的所有安全要求、控制 and 组件 |
| 6. **数据集成和互操作性 (Data Integration and Interoperability)** | 将数据转换为结构化形式以供其他系统和资源利用 |
| 7. **文档和内容 (Documents and Content)** | 所有形式的非结构化数据及其可访问性工作 |
| 8. **参考和主数据 (Reference and Master Data)** | 以允许冗余的方式管理数据，错误可通过标准值归一化 |
| 9. **数据仓库和商业智能 (Data Warehousing and Business Intelligence)** | 管理和应用数据用于分析和业务决策 |
| 10. **元数据 (Metadata)** | 创建、收集、组织和管理元数据（引用其他数据的数据） |
| 11. **数据质量 (Data Quality)** | 数据监控实践，确保交付的数据完整性得到维护 |

</div>

> ⚠️ A real data management model must contain all eleven pillars. Miss one and part of the data management domain is uncovered. Without metadata management, for example, the enterprise loses the ability to classify data easily; without data quality assurance, all data is at risk and analytics become useless.

<div class="zh" markdown="1">

> ⚠️ 真正的数据管理模型需要包含所有 11 个支柱。缺少任何一个，就有数据管理领域未被覆盖。例如，没有元数据管理，企业失去轻松分类数据的能力；没有数据质量保证，所有数据都处于风险中，分析变得无用。

</div>

---

<figure class="fig">
<img src="assets/fig/en03-09-eleven-pillars.svg" alt="Eleven data capabilities grouped into plan, run, move and read clusters, with security, integration and quality highlighted as the three the network contributes to" loading="lazy">
<figcaption><b>Figure 3-9　Eleven data capabilities: three of them fall partly on the network</b><br><span>图 3-9　数据管理十一项能力，其中三项网络直接参与</span></figcaption>
</figure>

## Case Studies · 实战案例

### Case 1: Bandwidth Doubled, Video Conferencing Still Stutters · 案例一：带宽翻倍，视频会议还是卡

**Background**: a company suffered frequent video conference stutter. IT raised bandwidth from 100M to 300M and the problem remained.

<div class="zh" markdown="1">

**背景**：某公司视频会议频繁卡顿，IT 把带宽从 100M 升到 300M，问题依旧。

</div>

**Breaking it down by application characteristics**:

<div class="zh" markdown="1">

**按应用特征拆开看**：

</div>

| Characteristic | Video conferencing | File sharing |
|----------------|--------------------|--------------|
| Protocol | UDP/RTP | TCP |
| Sensitivity to loss | **Extremely sensitive** (1% loss shows as artifacts) | Insensitive (retransmission handles it) |
| Sensitivity to jitter | **Extremely sensitive** | Insensitive |
| Bandwidth demand | Moderate (2–4M per stream) | High |

<div class="zh" markdown="1">

| 应用特征 | 视频会议 | 文件共享 |
|---------|---------|---------|
| 协议 | UDP/RTP | TCP |
| 对丢包 | **极敏感**（1% 丢包画面即花屏） | 不敏感（重传即可） |
| 对抖动 | **极敏感** | 不敏感 |
| 对带宽 | 中等（每路 2–4M） | 高 |

</div>

**The three real causes**:

<div class="zh" markdown="1">

**真正的三个原因**：

</div>

1. Video traffic and backup jobs **shared the same queue**, and backup filled it
2. Branch to head office had **45 ms single-hop latency and 30 ms jitter**, beyond what the endpoints could adapt to
3. Some branch uplinks had **asymmetric bandwidth** (300M down, 20M up), while conferencing is symmetric bidirectional traffic

<div class="zh" markdown="1">

1. 视频流量与备份任务**共用同一条队列**，备份把队列打满
2. 分支到总部**单跳延迟 45ms，抖动 30ms**，超出终端自适应范围
3. 部分分支出口是**非对称带宽**（下行 300M、上行 20M），而会议是双向对称流量

</div>

<figure class="fig">
<img src="assets/fig/en03-10-case1-bandwidth-not-latency.svg" alt="Measured throughput, round-trip time, jitter, loss and uplink asymmetry beside the three real causes and a four-step fix ordered by effect" loading="lazy">
<figcaption><b>Figure 3-10　Doubling the circuit did not fix a jitter and upstream problem</b><br><span>图 3-10　带宽翻倍解决不了抖动与上行问题</span></figcaption>
</figure>

**Fix**: a dedicated queue for real-time traffic + branch uplink upgrade + jitter buffering. **Total bandwidth did not increase, yet the experience improved.**

<div class="zh" markdown="1">

**修正**：为实时流量单独队列 + 分支上行扩容 + 开启抖动缓冲。**总带宽没增，体验反而好了。**

</div>

> 💡 **Lesson**: **ask first what this application cares about, then ask whether the network can deliver it.** Bandwidth is only one dimension; loss, jitter, latency and symmetry matter just as much.

<div class="zh" markdown="1">

> 💡 **教训**：**先问"这个应用在意什么"，再问"网络给不给得起"。** 带宽只是其中一个维度，丢包、抖动、时延、对称性同样关键。

</div>

### Case 2: Slower After Moving to the Cloud · 案例二：上云之后，系统反而更慢了

**Background**: an enterprise migrated its ERP to a public cloud with more generous resources, yet users complained that "opening a document list takes 8 seconds" (it took 2 seconds in the original on-premises data center).

<div class="zh" markdown="1">

**背景**：某企业把 ERP 迁移到公有云，云上资源更充足，但用户投诉"打开单据列表要 8 秒"（原来自建机房 2 秒）。

</div>

**Troubleshooting**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Layer | Finding |
|-------|---------|
| Cloud host performance | CPU, memory and disk all had headroom — not a resource problem |
| Network latency | Office to cloud: RTT went from 1 ms to 35 ms |
| Application behavior | The list page **issued 40 serial database queries** (N+1 queries), one round trip each |
| Arithmetic | 40 × 35 ms × 2 ≈ **2.8 seconds of pure round-trip overhead**, which on top of the original logic gives 8 seconds |

<div class="zh" markdown="1">

| 层面 | 现象 |
|------|------|
| 云主机性能 | CPU/内存/磁盘均有余量，不是资源问题 |
| 网络时延 | 办公区到云：RTT 从 1ms 变成 35ms |
| 应用行为 | 单据列表页**串行发起 40 次数据库查询**（N+1 查询），每次一个往返 |
| 计算 | 40 × 35ms × 2 ≈ **2.8 秒只是往返开销**，叠加原有逻辑即 8 秒 |

</div>

<figure class="fig">
<img src="assets/fig/en03-11-case2-round-trips.svg" alt="Forty sequential queries each paying a 35 ms crossing, giving 2.8 seconds per page load against 8 ms locally, with remedy options ranked as bars" loading="lazy">
<figcaption><b>Figure 3-11　Forty round trips turn 35 ms into 2.8 s per page load</b><br><span>图 3-11　四十次往返，把 35 ms 放大成每次 2.8 s</span></figcaption>
</figure>

**Root cause**: the application architecture is **chatty** (many small round trips). It was invisible at LAN latency, and the move to WAN multiplied the latency by 40.

<div class="zh" markdown="1">

**根因**：应用架构是**chatty**（大量小往返）型，在局域网低时延下看不出来，跨广域网后时延被放大 40 倍。

</div>

**Fix direction**: on the application side, batch the queries and add caching; on the network side, use a dedicated cloud circuit to bring RTT under 10 ms; separate database reads from writes to cut cross-region access.

<div class="zh" markdown="1">

**修正方向**：应用侧改为批量查询/缓存；网络侧用云专线把 RTT 压到 10ms 以内；数据库读写分离减少跨区域访问。

</div>

> 💡 **Lesson**: **moving to the cloud is not moving machines, it is moving distance.** The application architecture traits this chapter highlights (chatty vs. bulk, whether state is externalized) directly determine post-migration performance; the network can mitigate architecture problems but cannot fix them.

<div class="zh" markdown="1">

> 💡 **教训**：**上云不是搬机器，是搬"距离"。** 第 3 章强调的应用架构特征（chatty vs bulk、状态是否外置）直接决定云化后的性能表现，网络只能缓解、不能修复架构问题。

</div>

---

## Design Pitfalls · 设计缺陷

| Pitfall | Symptom | Consequence | Correct practice |
|---------|---------|-------------|------------------|
| **Designing from the application name instead of its behavior** | "Video conferencing needs bandwidth" → only bandwidth is added | Artifacts persist after the upgrade, because loss, jitter and asymmetry are the real causes | Describe applications with a trait matrix: protocol, loss sensitivity, jitter sensitivity, latency ceiling, traffic symmetry, statefulness |
| **Treating cloud migration as a move** | The cloud has more resources, but RTT went from 1 ms to 35 ms | Chatty applications collapse (Case 2) | Assess the application architecture first (chatty vs. bulk, externalized state, caching), then choose the cloud connection |
| **Chasing cloud agnosticism too far** | Everything is rebuilt on IaaS so it "can move at any time", giving up native PaaS | Portability gained, operational burden and cost doubled | Apply cloud agnosticism only to **the layer that truly needs cross-cloud portability** (data and identity); choose the best option per scenario for compute and network |
| **Choosing the service model at the wrong layer** | Building on IaaS what should be SaaS, buying SaaS where IaaS fits | You carry operations you should not, or you get locked in | Choose by "who is best at this": outsource non-differentiating capability, build what differentiates |
| **Calling storage and backup "data management"** | Only one or two of the eleven pillars are covered | Data is available but untrustworthy, unsearchable and non-compliant | Work through all eleven pillars, fill the gaps, prioritizing metadata and data quality |
| **Containerizing only the deployment format** | A monolith is stuffed into a container but still shares one database | None of the elasticity or fault-isolation benefit materializes | Containerization presupposes **statelessness + externalized configuration + layered data**; otherwise it is only a new package format |

<div class="zh" markdown="1">

| 缺陷 | 表现 | 后果 | 正确做法 |
|------|------|------|---------|
| **按应用名字而不是应用行为做设计** | "视频会议需要带宽"→ 只扩带宽 | 扩了带宽依然花屏（丢包/抖动/非对称才是主因） | 用特征矩阵描述应用：协议、丢包敏感度、抖动敏感度、时延上限、流量对称性、是否有状态 |
| **把上云当搬家** | 云上资源更足，却忽略了 RTT 从 1ms 变 35ms | chatty 应用性能崩塌（案例二） | 先评估应用架构（chatty vs bulk、状态外置、缓存策略），再决定云连接方式 |
| **过度追求云无关** | 为了"能随时迁走"，放弃云原生 PaaS 能力，全部自建在 IaaS 上 | 可移植性拿到了，运维负担与成本翻倍 | 云无关只应用于**真正需要跨云的那一层**（数据与身份），计算/网络层按场景选最优 |
| **服务模型选错层次** | 该用 SaaS 的用了 IaaS 自建，该用 IaaS 的买了 SaaS | 承担了不该承担的运维责任，或被供应商锁定 | 按"谁最擅长这件事"选模型：非差异化能力外购，差异化能力自建 |
| **只做存储与备份就称数据管理** | 11 个支柱只覆盖 1–2 个 | 数据可用但不可信、不可查、不可合规 | 11 支柱逐条对照，缺哪条补哪条，优先补元数据与数据质量 |
| **容器化只改部署方式** | 单体应用直接塞进容器，仍共享同一数据库 | 弹性与故障隔离的收益全部拿不到 | 容器化的前提是**无状态化 + 配置外置 + 数据分层**，否则只是换了包格式 |

</div>

---

## Lessons Learned · 实战经验总结

| Lesson | Explanation |
|--------|-------------|
| **Build a "trait profile" for every application** | One row per application class: latency ceiling, loss tolerance, jitter tolerance, bandwidth shape, direction (north-south or east-west), statefulness. That table is the shared input for QoS, cloud connectivity and WAN selection |
| **The network mitigates; only architecture fixes** | A chatty application across a WAN will not be fixed by more bandwidth; batch queries, caching or read-write separation are required |
| **Traffic direction drives architecture** | North-south (user to server) is about egress and the edge; east-west (server to server) is about the data center fabric and segmentation. The two designs are entirely different |
| **Latency is set by geography** | The speed of light sets the RTT floor; any "optimization" only moves RTT from 200 ms to 60 ms. Cross-continent active-active must be split by business function rather than by forcing low latency everywhere |
| **Do the "distance arithmetic" before moving to cloud** | The physical location of the cloud region, the distance between availability zones and cross-zone traffic charges all belong in the TCO at proposal stage |
| **Portability has a price** | Every added abstraction layer costs some native cloud capability; buy it only where it is warranted |
| **Use the eleven pillars as a checklist** | You do not need to memorize them, but in review ask "who owns this one" for each — that surfaces the neglected areas |

<div class="zh" markdown="1">

| 经验 | 说明 |
|------|------|
| **先给应用建"特征档案"** | 每类应用一行：时延上限、丢包容忍、抖动容忍、带宽形态、流向（南北/东西）、是否有状态。这张表是后面 QoS、云连接、WAN 选型的共同输入 |
| **网络只能缓解，架构才能修复** | chatty 应用跨广域网的性能问题，靠加带宽解决不了，必须改批量查询、缓存或读写分离 |
| **流向决定架构** | 南北向（用户到服务器）看出口与边缘，东西向（服务器之间）看数据中心 fabric 与分段，两者设计完全不同 |
| **时延是地理决定的** | 光速决定了 RTT 下限，任何"优化"都只是把 RTT 从 200ms 压到 60ms。跨洲双活必须按业务切分，不能强求全网低延迟 |
| **上云前先算"距离账"** | 云区域的物理位置、可用区之间的距离、跨区流量费用，三项在方案阶段就要算进 TCO |
| **可移植性是有成本的** | 每增加一个抽象层都会损失一部分云原生能力，只在该买的地方买 |
| **数据管理 11 支柱当检查表用** | 不用背全，但评审时逐条问"这条谁负责"，能问出被忽略的领域 |

</div>

---

## Design Scenarios (2) · 设计情景演练（2 个）

### Scenario 1: Moving a Twelve-Year-Old ERP to the Cloud · 情景一：把 12 年前的 ERP 搬上云

**Situation**: a manufacturer's core ERP went live in 2012 as a three-tier architecture: 4 web servers, 8 application servers, 2 database servers (active/standby), all in its own data center. The database uses shared storage and a private protocol heartbeat, and the application tier makes a very large number of small transactions against the database (24 million per day, average 3 ms per round trip, 0.2 ms RTT inside the data center). The group requires migration to the cloud within 18 months, and the budget covers IaaS hosting only.

<div class="zh" markdown="1">

**场景**：某制造企业的核心 ERP 是 2012 年上线的三层架构：Web 层 4 台、应用层 8 台、数据库 2 台（主备），全部在自建机房。数据库用了共享存储和私有协议心跳，应用层与数据库之间有大量小事务（日均 2400 万次，单次往返平均 3ms，机房内 RTT 0.2ms）。集团要求 18 个月内完成上云，预算只覆盖 IaaS 托管。

</div>

**Questions to answer**:
1. Can this application be lifted and shifted to public cloud IaaS? Where is the bottleneck?
2. Which connection model should be chosen?
3. If the application cannot change, how far can the network compensate, and where can it not?

<div class="zh" markdown="1">

**要回答的问题**：
1. 这个应用适合直接"平移"到公有云 IaaS 吗？瓶颈会在哪？
2. 连接模型怎么选？
3. 如果不改应用，网络能补到什么程度、补不到什么程度？

</div>

<figure class="fig">
<img src="assets/fig/en03-12-scenario1-tier-migration.svg" alt="Web tier marked as movable, application tier movable only with its database, database tier staying, over a 200 ms per-transaction budget bar and a five-step migration order" loading="lazy">
<figcaption><b>Figure 3-12　One ERP, three tiers, three answers</b><br><span>图 3-12　一个 ERP，三层，三个答案</span></figcaption>
</figure>

**Reference approach**:
- **Compute the latency budget before discussing the move.** 24 million per day ≈ 278 per second at 0.2 ms per round trip; if RTT rises to 2 ms, each transaction adds about 1.8 ms, and under concurrency limits that directly depresses throughput. **This combination of high-frequency small transactions and tightly coupled application/database tiers is the hardest case in cloud migration.**
- **The usual conclusion is "migrate by tier", not a wholesale lift and shift**: the web tier (stateless, sensitive to user-side latency but not to back-end RTT) moves first; the application and database tiers must stay inside one low-latency domain (same campus, same availability zone, or a dedicated circuit with measured RTT that meets target).
- **Choose the connection model on determinism**: if the application tier and database span cloud and data center, Internet VPN jitter is unacceptable, so use a **dedicated circuit or cloud exchange** and demand latency and loss figures in the SLA rather than bandwidth alone (10 Gbps with 3% loss can be far worse for small transactions than 1 Gbps with 0.05% loss).
- **What the network can deliver**: path optimization, QoS guarantees, TCP parameter tuning, connection reuse on the application side, and local points of presence.
- **What the network cannot deliver**: N+1 queries per call between tiers, repeated round trips caused by missing caches, and poorly split transactions. **Those can only be fixed in the application.**
- **The right deliverable**: a per-tier cloud feasibility table (latency sensitivity, statefulness, migration risk, target location for each tier) plus an explicit list of what the application side must do. **Never promise that the network will solve an application problem.**

<div class="zh" markdown="1">

**参考思路**：
- **先算时延预算，再谈搬家。** 2400 万次/天 ≈ 278 次/秒，单次往返 0.2ms → 若 RTT 升到 2ms，单事务耗时增加约 1.8ms；在并发受限的场景下，这会直接压低吞吐。**这类"高频小事务 + 紧耦合应用层/数据库"的组合，是上云最典型的硬骨头。**
- **结论通常是"分层上云"而不是整体平移**：Web 层（无状态、用户侧时延敏感但对后端 RTT 不敏感）优先上云；应用层与数据库必须在同一低时延域内（同园区、同可用区、或专线直连且实测 RTT 达标）。
- **连接模型选择看确定性**：若应用层与数据库跨"云—机房"，Internet VPN 的抖动不可接受，应选**专线/云交换**，并要求 SLA 中的时延与丢包指标，而不是只看带宽（10Gbps + 3% 丢包的小事务性能，可能远不如 1Gbps + 0.05% 丢包）。
- **网络补得到的**：路径优化、QoS 保障、TCP 参数调优、连接复用（应用侧）、就近接入。
- **网络补不到的**：应用层与数据库之间每次调用的 N+1 查询问题、缺少缓存导致的重复往返、事务拆分不合理。**这些只能改应用。**
- **正确产出**：一张"按层拆解的上云可行性表"（每层标注时延敏感度、状态性、迁移风险、目标位置）+ 明确的"需要应用侧配合的清单"。**不要承诺网络能解决应用的问题。**

</div>

### Scenario 2: "The Network Got Slower" After Microservices · 情景二：微服务化之后"网络变慢了"

**Situation**: an internet company split its monolith into 120 microservices running across two clouds (A active, B for disaster recovery) plus its own data center. After go-live three problems appeared: cross-cloud P99 latency rose from 40 ms to 260 ms; mean time to localize a fault went from 20 minutes to 3 hours; and the security team could not state whether service A may access service B.

<div class="zh" markdown="1">

**场景**：某互联网公司把单体拆成 120 个微服务，跑在双云（A 云为主、B 云做灾备）+ 自建机房混合环境。上线后出现三类问题：跨云调用 P99 时延从 40ms 涨到 260ms；故障定位平均耗时从 20 分钟涨到 3 小时；安全团队无法说清"服务 A 能否访问服务 B"。

</div>

**Questions to answer**:
1. What common root cause underlies all three symptoms?
2. Which capabilities must the network design add?
3. Should the "two clouds plus data center" architecture be adjusted?

<div class="zh" markdown="1">

**要回答的问题**：
1. 这三个现象的共同根因是什么？
2. 网络设计要补哪些能力？
3. "双云 + 机房"的架构是否应该调整？

</div>

<figure class="fig">
<img src="assets/fig/en03-13-scenario2-east-west.svg" alt="Monolith with one north-south flow and one log, compared with thirty services behind a gateway whose east-west calls no single log records, plus the five capabilities the design must add" loading="lazy">
<figcaption><b>Figure 3-13　East-west traffic removed the only log that saw the whole request</b><br><span>图 3-13　东西向流量带走了唯一能看见整条请求的日志</span></figcaption>
</figure>

**Reference approach**:
- **The common root cause is loss of control over east-west traffic.** In the monolith era traffic was mostly north-south with fixed paths; in the microservices era it is mostly east-west with dynamic call relationships. The old design assumptions — edge-centric, IP-identified, static ACL policy — all fail in the new shape.
- **Latency**: a large part of the 260 ms is not the link but **serial calls plus missing locality routing plus no connection pooling**. The first step is not more bandwidth but **flattening the call chain** (same-domain first, locality routing, caching), then re-evaluating whether the cross-cloud call is needed at all.
- **Observability**: correlate distributed tracing, service-level metrics and network flow logs. **Network device logs alone will never tell you which service is slow.**
- **Security policy**: move from "IP + port" to "identity + service" (service mesh mTLS, workload-identity policy); otherwise an access matrix for 120 services cannot be maintained by hand.
- **The two-cloud trade-off**: fully active cross-cloud brings cross-cloud consistency and latency problems. The usual design is **"close the loop inside each domain, synchronize only what is necessary across domains"** — each cloud region is self-contained for calls, and the cross-cloud path carries asynchronous replication and a small number of critical queries.
- **In one sentence**: **microservices redefine the network problem as a joint problem of topology, identity and observability** — adding bandwidth alone or firewalls alone solves nothing.

<div class="zh" markdown="1">

**参考思路**：
- **共同根因：东西向流量失控。** 单体时代是"南北向为主、路径固定"；微服务时代是"东西向为主、调用关系动态"。原来的网络设计（以边界为中心、以 IP 为标识、以静态 ACL 为策略）在新形态下全部失效。
- **时延**：跨云调用 260ms 中有很大一部分不是链路，而是**多次串行调用 + 缺少就近路由 + 无连接池**。第一步不是扩带宽，而是把**调用链压平**（同域优先、就近路由、缓存），再评估跨云调用是否必要。
- **可观测性**：需要分布式追踪、服务级指标、网络流日志三者的关联。**只有网络设备日志，永远定位不到"哪个服务慢"。**
- **安全策略**：从"IP + 端口"转向"身份 + 服务"（服务网格 mTLS、基于工作负载身份的策略），否则 120 个服务的访问矩阵无法人工维护。
- **双云架构的取舍**：双云"同时活跃"会带来跨云数据一致性与时延问题，通常应设计为**"同域内闭环、跨域只做必要同步"**，即每个云区域内自成调用闭环，跨云只承载异步复制与少量关键查询。
- **一句话**：**微服务化把"网络问题"重新定义为"拓扑 + 身份 + 可观测性"的联合问题**，只加带宽或只加防火墙都无解。

</div>

---

## Key Terms · 本章关键术语

| Term | Meaning |
|------|---------|
| Single-Server Model | Application where every component runs on one server |
| 2-Tier Model | Client/server model with presentation on the client and data on the server |
| 3-Tier Model | Presentation, application and database tiers |
| Web Tier | The presentation tier that end users interact with |
| Application Tier | The logic tier that processes tasks and decisions |
| Database Tier | The data tier that stores and retrieves information |
| On-Premises | The enterprise owns and operates the application |
| SaaS (Software as a Service) | Provider-delivered software over the Internet |
| PaaS (Platform as a Service) | Provider-supplied tools on which customers build applications |
| IaaS (Infrastructure as a Service) | On-demand storage, networking and virtualization |
| DCA (Direct Cloud Access) | Direct SaaS access from a site over the Internet |
| DIA (Direct Internet Access) | Direct Internet egress from the branch |
| Private Cloud | Cloud resources dedicated to a single enterprise |
| Public Cloud | Shared cloud resources owned by a CSP |
| Hybrid Cloud | Combined private and public cloud use |
| Multi-Cloud | Use of two or more CSPs |
| Cloud-Agnostic | Architecture free of vendor-specific features |
| Portability | Ability to move workloads between CSPs |
| Abstraction | Decoupling from cloud-specific platform features |
| Interoperability | Building services not bound to one cloud feature set |
| Decoupling | Separating application from platform and cloud components from consumers |
| Containerization | Packaging applications with a shared operating system |
| SOA (Service-Oriented Architecture) | Services offered to other components over the network |
| Data Governance | Planning every aspect of data management |
| Data Architecture | The overall structure of enterprise data |
| Data Security | Controls keeping data protected and access authorized |
| Metadata | Data that references other data |
| Data Quality | Monitoring that keeps delivered data trustworthy |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| Single-server Model | 单服务器模型 |
| 2-Tier Model | 二层模型 |
| 3-Tier Model | 三层模型 |
| Web Tier | Web 层（表示层） |
| Application Tier | 应用层（逻辑层） |
| Database Tier | 数据库层 |
| On-premises | 本地部署 |
| SaaS (Software as a Service) | 软件即服务 |
| PaaS (Platform as a Service) | 平台即服务 |
| IaaS (Infrastructure as a Service) | 基础设施即服务 |
| DCA (Direct Cloud Access) | 直接云接入 |
| DIA (Direct Internet Access) | 直接互联网接入 |
| Private Cloud | 私有云 |
| Public Cloud | 公有云 |
| Hybrid Cloud | 混合云 |
| Multi-cloud | 多云 |
| Cloud-Agnostic | 云无关 |
| Portability | 可移植性 |
| Abstraction | 抽象 |
| Interoperability | 互操作性 |
| Decoupling | 解耦 |
| Containerization | 容器化 |
| SOA (Service-Oriented Architecture) | 面向服务架构 |
| Data Governance | 数据治理 |
| Data Architecture | 数据架构 |
| Data Security | 数据安全 |
| Metadata | 元数据 |
| Data Quality | 数据质量 |

</div>

---

## Chapter Summary · 本章小结

Chapter 3 answers what the network is actually serving, and the whole chapter condenses into one chain of judgment:

<div class="zh" markdown="1">

第 3 章解决的是"网络到底在为什么服务"这个问题，全章可以整理成一张判断链：

</div>

```
Application (model + traits) → decides what the network must provide
    ↓
Service model (SaaS / PaaS / IaaS / on-premises) → decides who operates what
    ↓
Cloud type and connectivity (public/private/hybrid/multi-cloud, DCA/DIA/dedicated) → decides where traffic flows
    ↓
Data (eleven pillars) → decides what the network must guarantee (compliance, quality, availability)
```

<div class="zh" markdown="1">

```
应用（模型 + 特征）→ 决定网络需要什么
    ↓
服务模型（SaaS / PaaS / IaaS / 本地）→ 决定谁运维什么
    ↓
云类型与连接（公有/私有/混合/多云，DCA/DIA/专线）→ 决定流量从哪里走
    ↓
数据（11 支柱）→ 决定网络必须保证什么（合规、质量、可用）
```

</div>

Three conclusions to remember:

<div class="zh" markdown="1">

三句必须记住的结论：

</div>

| Conclusion | Meaning |
|------------|---------|
| **Application traits determine network metrics** | The question is not "is there enough bandwidth" but whether loss, jitter, latency, symmetry and session patterns match. Video conferencing and backup are different species |
| **Deployment location sets the latency floor** | The speed of light cannot be optimized. Cross-region and cross-cloud architecture must be split by business function, keeping what must be low-latency close |
| **Cloud agnosticism is a trade-off with a price** | The more abstraction layers, the more portable and the less you use native cloud capability. Buy it only where it is warranted |

<div class="zh" markdown="1">

| 结论 | 含义 |
|------|------|
| **应用特征决定网络指标** | 不是"带宽够不够"，而是"丢包、抖动、时延、对称性、会话模式"是否匹配。视频会议和备份是两个物种 |
| **部署位置决定时延下限** | 光速不可优化。跨区域/跨云的架构必须按业务切分，把"必须低延迟"的部分留在近端 |
| **云无关是有成本的取舍** | 抽象层越多，越可移植，也越用不到云的原生能力。只在该买的地方买 |

</div>

> **One-line memory hook**: **Chapter 1 asks "why do it", Chapter 2 asks "is it worth it", Chapter 3 asks "who is it for".** Once those three are answered, the technology choices in Chapters 6–14 have criteria to test against.

<div class="zh" markdown="1">

> **一句话记忆**：**第 1 章问"为什么做"，第 2 章问"值不值"，第 3 章问"为谁而做"。** 这三问答完，第 6–14 章的技术选型才有判据。

</div>

The application trait table from this chapter is reused directly in Chapter 14 (QoS classification and queues) and Chapter 17 (WAN selection) — **one table, three uses**, which is rare in this book.

<div class="zh" markdown="1">

本章的应用特征表会在第 14 章（QoS 分类与队列）、第 17 章（WAN 选型）被直接复用——**同一张表，三个用途**，这是本书少见的"一鱼三吃"。

</div>
