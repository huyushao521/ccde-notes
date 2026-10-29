# Chapter 4: Security Is Pervasive · 第 4 章：安全是普适的

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapter 4 (pp. 209–233)
>
> Terminology follows the English edition. Every English passage is followed by its Chinese counterpart in the grey block below it, so the two can be checked sentence by sentence.

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译 | 原书第 209-233 页

</div>

---

## Topics Covered · 本章涵盖主题

- **Zero Trust Architecture (ZTA)**: the pillars, capabilities and components of zero trust
- **The security CIA triad**: confidentiality, integrity and availability, and their design elements
- **Regulatory compliance**: how to design solutions against compliance standards

<div class="zh" markdown="1">

- **零信任架构 (Zero Trust Architecture)**：零信任架构的支柱、能力和组件
- **安全 CIA 三要素**：机密性、完整性和可用性及其设计要素
- **法规合规**：如何根据合规标准设计解决方案

</div>

---

## Chapter Overview: Security Is a Property of Every Decision, Not a Module · 本章导读：安全是每个决策的属性，不是一个模块

Chapter 1 listed pervasive security as a design principle; this chapter breaks it into something executable: policy sources, trust models, CIA and compliance. The position is one sentence: **as soon as a single design decision treats security as "we will add it later", the security ceiling of the architecture is already fixed.**

<div class="zh" markdown="1">

第 1 章把"普适安全"列为设计原则，这一章把它拆成可执行的东西：策略来源、信任模型、CIA、合规。核心立场只有一句：**只要有一个设计决策把安全当成"后面再补"，这个架构的安全上限就已经定了。**

</div>

Eight lessons that are easy to miss:

<div class="zh" markdown="1">

八个容易踩空的认知：

</div>

**1. Security is fundamentally about changing the defaults.** Default allow plus restrictions added afterwards, versus default deny plus explicit permission, are two entirely different architectures. **What sets the security level is not the device list, it is the default.**

<div class="zh" markdown="1">

**1. 安全的本质是"改变默认值"。** 默认允许 + 事后加限制，与默认拒绝 + 按需放行，是两种完全不同的架构。**决定安全水平的不是设备清单，而是默认值。**

</div>

**2. Security policy has four sources, and their cost of change differs enormously.** Laws and standards (almost non-negotiable), contracts and SLAs (negotiable commercially, but technically binding), internal policy (negotiable but needs time), architecture principles (debatable, but exceptions must be recorded). **Treating internal policy as law wastes budget; treating law as a suggestion gets people fired.**

<div class="zh" markdown="1">

**2. 安全策略有四个来源，变更成本差别极大。** 法规与标准（几乎不可协商）、合同与 SLA（商务可谈、技术必须兑现）、内部制度（可协商但要时间）、架构原则（可讨论，但例外要留痕）。**把"内部制度"当成"法规"会浪费预算，把"法规"当成"建议"会出事。**

</div>

**3. The perimeter model is not dead, but it is no longer sufficient.** Users are at home, applications are in the cloud and data sits in third-party SaaS — the premise "inside equals trusted" has disappeared. Zero trust does not remove the firewall; it **stops using location as the only basis for trust**.

<div class="zh" markdown="1">

**3. 边界模型并没有"死"，但已经不够用。** 用户在家里、应用在云上、数据在第三方 SaaS 里——"内网 = 可信"这个前提消失了。零信任不是把防火墙拆掉，而是**不再用"位置"作为信任的唯一依据**。

</div>

**4. Zero trust is not a product you buy, it is a set of architecture decisions.** It requires at minimum trusted identity, device posture assessment, fine-grained policy (per application, per request) and continuous telemetry with dynamic decisions. **Deploying one "zero trust gateway" without identity governance and log analytics is just a more expensive perimeter.**

<div class="zh" markdown="1">

**4. 零信任不是能买到的产品，是一组架构决策。** 它至少要同时具备：可信身份、设备状态评估、细粒度策略（按应用/按请求）、持续遥测与动态判定。**只上了一个"零信任网关"而没有身份治理和日志分析，等于换了个更贵的边界。**

</div>

**5. The three CIA goals pull against each other, so the design must trade off explicitly.** Encrypting everything everywhere weakens detection (content becomes invisible); strong isolation reduces availability and operational efficiency; keeping too much log data creates a new exposure surface. **No design maximizes all three at once.**

<div class="zh" markdown="1">

**5. CIA 三者会互相拉扯，设计必须显式取舍。** 全链路加密会削弱检测能力（看不见内容）；强隔离会降低可用性与运维效率；过度留存日志又制造新的泄露面。**没有一个方案能同时把三者拉满。**

</div>

**6. Compliance is not security.** An organization that passes a PCI DSS audit can still fall to a phishing email. Compliance is **a floor and a body of evidence**; security is **continuous risk management**. Keep them separate in the design: compliance items are evidence you must have, security items are exposure you must reduce.

<div class="zh" markdown="1">

**6. 合规 ≠ 安全。** 通过 PCI DSS 审计的组织依然可能被钓鱼攻破。合规是**下限与证据**，安全是**持续的风险管理**。设计时要把两者分开：合规项是"必须有的证据"，安全项是"必须降低的敞口"。

</div>

**7. Data sovereignty is one of the hardest technical constraints.** The sentence "data may not leave the country" directly determines application placement, backup strategy, whether cross-border links may exist, and even the access path used by operations staff. **It is an architecture-changing input, not a footnote in the proposal.**

<div class="zh" markdown="1">

**7. 数据主权是最硬的技术约束之一。** "数据不得出境"这一句，会直接决定应用部署位置、备份策略、跨境链路是否存在、甚至运维人员的访问路径。**它属于"改架构"级别的输入，不是一条可以在方案里备注的条款。**

</div>

**8. Rank security spend by exposure × likelihood × impact, not by vendor recommendation.** Ninety percent of budget goes to the schemes that look advanced, while what actually gets exploited is unpatched edge devices, expired accounts and over-privileged operational access.

<div class="zh" markdown="1">

**8. 安全投入应按"敞口 × 概率 × 影响"排序，而不是按厂商推荐排序。** 90% 的预算花在"看起来高级"的方案上，而真正被利用的往往是未打补丁的边界设备、过期的账号和高权限的运维通道。

</div>

> **One-sentence summary**: **the output of security design is not "what we bought", but "which risks we explicitly accepted, and why".**

<div class="zh" markdown="1">

> **一句话概括这一章**：**安全设计的产出不是"我们买了什么"，而是"我们明确接受了哪些风险、以及为什么"。**

</div>

---

## Foundation Topics · 基础内容

Today's converged networks carry a great deal of critical business information — voice, video and data — which makes protecting and assuring that information essential, for two reasons:
1. **Information security and privacy**
2. **Maintaining business continuity** (for example preventing DDoS attacks)

<div class="zh" markdown="1">

当今的融合网络承载着大量关键业务信息（语音、视频或数据），使保护和保障这些信息变得极为重要，原因有两个：
1. **信息安全和隐私**
2. **维持业务连续性**（如防止 DDoS 攻击）

</div>

Network infrastructure and network security **cannot be designed in isolation**. A holistic approach is essential, and **security cannot be an afterthought; it must be at the front of every design decision.**

<div class="zh" markdown="1">

网络基础设施和网络安全的设计**不能孤立进行**。整体方法对于网络安全设计至关重要。**安全不能是事后补充，必须处于每个设计决策的前沿。**

</div>

### Security Policy · 安全策略

A security policy is a formal statement of the rules that anyone granted access to the organization's technical and information assets must follow. Before starting any network design, understanding the organization's security policy and its standards is a key prerequisite.

<div class="zh" markdown="1">

安全策略是关于获得组织技术和信息资产访问权限的人员必须遵守的规则的正式声明。在开始任何网络设计之前，理解组织的安全策略及其标准是关键前提。

</div>

> **Example**: you may propose reusing existing 1G dark fiber as a virtual leased line (VLL) solution. The security policy may state that any traffic crossing networks not owned by the organization must be encrypted, so IPsec or MACsec must be added to deliver an encrypted VLL.

<div class="zh" markdown="1">

> **示例**：你可能建议将现有的 1G 暗光纤重新设计为虚拟租用线 (VLL) 解决方案。但安全策略可能规定：任何穿越非组织拥有网络的流量必须加密。因此需要添加 IPsec 或 MACsec 来提供加密 VLL。

</div>

#### The Four Sources of Security Policy · 安全策略的四类来源

<figure class="fig">
<img src="assets/fig/en04-01-policy-sources.svg" alt="Four sources of policy, each pushing a different requirement onto the same network element, with the tie-break rule beside them" loading="lazy">
<figcaption><b>Figure 4-1　The four sources of security policy, and which one wins when they disagree</b><br><span>图 4-1　安全策略的四类来源，以及冲突时谁优先</span></figcaption>
</figure>


Policy is not one document; it is **the union of four kinds of input**. A designer must be able to say which category every requirement comes from, because their **cost of change is completely different**:

<div class="zh" markdown="1">

策略不是一份文档，而是**四类输入的合集**。设计者必须能说清每条要求来自哪一类，因为它们的**变更成本完全不同**：

</div>

| Source | Typical content | How it is expressed | Negotiability |
|--------|-----------------|---------------------|---------------|
| **Laws and standards** | GDPR, PCI DSS, HIPAA, sector regulators | "Must / must not" clauses | Not negotiable; only the implementation can change |
| **Contracts and SLAs** | Customer-mandated data residency, audit rights, isolation commitments | Contract clauses and penalties | Negotiable commercially, binding technically |
| **Internal policy** | Password and account policy, offboarding, privileged access management, endpoint compliance | Management procedures, checklists | Negotiable, but internal change takes time and mandate |
| **Architecture principles** | Zero trust, least privilege, default deny, defense in depth | Principle plus exception process | The principle is debatable; exceptions must be recorded |

<div class="zh" markdown="1">

| 来源 | 典型内容 | 表达形式 | 可协商性 |
|------|---------|---------|---------|
| **法规与标准** | GDPR、PCI DSS、HIPAA、行业监管要求 | "必须/禁止"式条款 | 不可协商，只能改变实现方式 |
| **合同与 SLA** | 客户要求的数据驻留、审计权、隔离承诺 | 合同条款、罚则 | 商务层面可谈，技术层面必须兑现 |
| **内部制度** | 密码与账号策略、离职流程、特权账号管理、终端合规 | 管理办法、检查表 | 可协商，但推动内部变更需要时间与授权 |
| **架构原则** | 零信任、最小权限、默认拒绝、纵深防御 | 原则 + 例外流程 | 原则本身可讨论，例外必须留痕 |

</div>

> ⚠️ **The most common gap in practice is not "no policy" but "no exception process"**. The policy says "all traffic crossing non-owned networks must be encrypted" but nobody defines who decides whether a new service is an exception and how often it is reviewed. Exceptions then get approved verbally, and three months later nobody remembers why the rule was opened.

<div class="zh" markdown="1">

> ⚠️ **实践中最常见的缺口不是"没有策略"，而是"没有例外流程"**。策略写了"任何跨非自有网络的流量必须加密"，但没人规定"新业务上线时由谁判断是否属于例外、多久复核"。结果是例外靠口头批准，三个月后没人记得为什么放通。

</div>

#### Three Steps from Policy to Technology · 从策略推导到技术的三步

<figure class="fig">
<img src="assets/fig/en04-02-policy-to-means.svg" alt="Three steps from a policy statement to a technical means with what each step can and cannot decide" loading="lazy">
<figcaption><b>Figure 4-2　From policy to technology in three steps, and what each step may and may not decide</b><br><span>图 4-2　从策略到技术的三步，以及每一步能决定什么</span></figcaption>
</figure>


```
① Policy clause (natural language)
      ↓ translate
② Control objective (a verifiable statement: who may access what, under which conditions, logged to what extent)
      ↓ select
③ Technical means (encryption / authentication / segmentation / inspection / logging)
```

<div class="zh" markdown="1">

```
① 策略条款（自然语言）
      ↓ 翻译
② 控制目标（可验证的陈述：谁能访问什么、在什么条件下、被记录到什么程度）
      ↓ 选型
③ 技术手段（加密 / 认证 / 分段 / 检查 / 日志）
```

</div>

Using the policy "data may not leave the country" as an example:

<div class="zh" markdown="1">

以"数据不出境"这条策略为例：

</div>

| Layer | Content |
|-------|---------|
| Policy clause | Customer personal data must not leave the country |
| Control objective | Data storage location constrained; only de-identified aggregates may cross the border; access paths auditable |
| Technical means | In-country isolated zone (VRF/overlay isolation, Chapter 9) + one-way de-identified egress + centralized policy plane (configuration only, no data) + local log retention |

<div class="zh" markdown="1">

| 层次 | 内容 |
|------|------|
| 策略条款 | 客户个人数据不得离开本国境内 |
| 控制目标 | 数据存储位置受限；跨境只允许脱敏汇总；访问路径可审计 |
| 技术手段 | 境内独立区域（第 9 章 VRF/Overlay 隔离）+ 单向脱敏出站 + 集中策略管理面（只下发配置不携带数据）+ 本地日志留存 |

</div>

**The value of this step**: the same policy clause can have several technical implementations (encrypted VLL vs. application-layer encryption vs. no encryption but physically dedicated), **and the cost differs by an order of magnitude**. The designer's job is to lay out the options, not to jump straight to the most expensive one.

<div class="zh" markdown="1">

**这一步的价值在于**：同一个策略条款，可以有多种技术实现（加密 VLL vs 应用层加密 vs 不加密但物理独占），**成本差一个数量级**。设计者的工作是把选项摆出来，而不是直接跳到最贵的那一个。

</div>

### Security Domains and Zones · 安全域和区域

<figure class="fig">
<img src="assets/fig/en04-03-domains-chokepoints.svg" alt="User, server and management domains with the address range each one owns, every crossing marked by a chokepoint, and a policy table giving each crossing its service, action and enforcement point" loading="lazy">
<figcaption><b>Figure 4-3　Domains are cut where trust, rules or blast radius change, and every crossing needs one chokepoint — with the address range each domain owns and the policy row that enforces it</b><br><span>图 4-3　域的划分、地址段与跨域检查点的策略行</span></figcaption>
</figure>


Using a structured, modular approach, divide the network into **security domains** and introduce **chokepoints** between them:

<div class="zh" markdown="1">

使用结构化模块化方法，将网络分成多个**安全域**，在域之间引入**检查点 (Chokepoints)**：

</div>

```
┌─────────────────────────────────────────────┐
│              Enterprise core                 │
├──────┬──────────────┬──────────┬───────────┤
│Internet│  Data center  │ Network  │  WAN      │
│ edge   │  security     │ mgmt     │  security │
│ domain │  domain       │ zone     │  domain   │
│        │ ┌──┐┌──┐┌──┐│          │          │
│Firewall│ │Web││DB││App││ Firewall │ Firewall │
│IPS    │ │zone││zone││zone││        │          │
│        │ └──┘└──┘└──┘│          │          │
└──────┴──────────────┴──────────┴───────────┘
```

<div class="zh" markdown="1">

```
┌─────────────────────────────────────────────┐
│              企业核心层                       │
├──────┬──────────────┬──────────┬───────────┤
│ 互联网│   数据中心     │  网络管理  │  WAN      │
│ 边缘域│   安全域      │  区域     │  安全域    │
│      │ ┌──┐┌──┐┌──┐│          │          │
│ 防火墙│ │Web││DB││App││ 防火墙    │ 防火墙    │
│ IPS  │ │区 ││区││区 ││          │          │
│      │ └──┘└──┘└──┘│          │          │
└──────┴──────────────┴──────────┴───────────┘
```

</div>

Each domain is assigned a trust level, and inter-domain traffic is controlled with iACLs, firewalls, IPS and similar mechanisms.

<div class="zh" markdown="1">

每个域被赋予信任级别，使用 iACL、防火墙、IPS 等机制控制域间流量。

</div>

#### Three Criteria for Drawing Domain Boundaries · 域怎么划：三条依据

<figure class="fig">
<img src="assets/fig/en04-04-domain-boundaries.svg" alt="Three criteria for a boundary beside a curve of isolation gained per added domain against a flat policy cost line" loading="lazy">
<figcaption><b>Figure 4-4　Three criteria for a boundary, and the economic question that decides how many</b><br><span>图 4-4　划域的三条依据，以及决定域数量的经济问题</span></figcaption>
</figure>


| Criterion | Question | Example |
|-----------|----------|---------|
| **Trust level** | If assets here are compromised, what can the attacker do? | User endpoint domain (low trust) vs. server domain (high value) vs. management domain (highest) |
| **Compliance boundary** | Do the rules differ on either side of this boundary? | PCI cardholder data environment, domestic/foreign, production/test |
| **Fault and blast radius** | How far can a compromise or failure spread? | Production and test domains must be separate; factory OT domain and office domain must be separate |

<div class="zh" markdown="1">

| 依据 | 问题 | 例子 |
|------|------|------|
| **信任等级** | 这里的资产被攻破后，攻击者能做什么？ | 用户终端域（低信任）vs 服务器域（高价值）vs 管理域（最高） |
| **合规边界** | 数据在这条边界内外，规则是否不同？ | PCI 持卡人数据环境、境内/境外、生产/测试 |
| **故障与爆炸半径** | 一个域被攻破或出故障，能扩散多远？ | 生产域与测试域必须分开；工厂产线域与办公域必须分开 |

</div>

> 💡 **The counterintuitive point about domains**: **more granular is not better**. Every additional domain adds a set of inter-domain policies, a failure point and a troubleshooting path. A typical enterprise lands at **5–12 domains**; beyond that, policy maintenance cost exceeds the benefit — which is exactly why Chapter 10 replaces "domains inside domains" with SGTs and a policy center for microsegmentation.

<div class="zh" markdown="1">

> 💡 **划分域时的反直觉点**：**域不是越细越好**。每增加一个域，就增加一组域间策略、一个故障点、一条排障路径。典型企业的合理域数量是 **5–12 个**，超过这个数量后，策略维护成本会超过收益——这也是第 10 章微分段用 SGT/策略中心替代"域套域"的原因。

</div>

#### Choosing Chokepoints · 检查点的选型

<figure class="fig">
<img src="assets/fig/en04-05-chokepoint-selection.svg" alt="Five chokepoint types in a matrix of capability, placement and blind spot, with three operational constraints below" loading="lazy">
<figcaption><b>Figure 4-5　Five chokepoint types, what each decides, and what each is blind to</b><br><span>图 4-5　五类检查点的能力、位置与盲区</span></figcaption>
</figure>


Not all inter-domain traffic should cross the same class of device:

<div class="zh" markdown="1">

不是所有跨域流量都该过同一类设备：

</div>

| Chokepoint type | Capability | Where it fits | Cost |
|-----------------|------------|---------------|------|
| **Stateless ACL / iACL** | Five-tuple filtering at line rate | Coarse filtering inside a domain, infrastructure protection | Stateless: no session tracking, no application awareness |
| **Stateful firewall** | Session tracking, NAT, application identification | Every main inter-domain path | State synchronization is complex (HA pairs must sync sessions) |
| **IPS** | Signature detection and blocking of known attacks | Main north-south paths, data center ingress | Blind to encrypted traffic (unless decrypted); false positives need tuning |
| **WAF** | HTTP-layer attacks | Application front ends that are publicly published | Covers web only, does not understand non-HTTP protocols |
| **Proxy / CASB** | Outbound access control and audit | Internet egress | Requires endpoint cooperation (proxy settings or PAC) |

<div class="zh" markdown="1">

| 检查点类型 | 能力 | 适用位置 | 代价 |
|-----------|------|---------|------|
| **无状态 ACL / iACL** | 五元组过滤，线速 | 域内粗筛、基础设施保护 | 无状态：不跟踪会话，不识别应用 |
| **有状态防火墙** | 会话跟踪、NAT、应用识别 | 所有域间主通道 | 状态同步复杂（双机热备必须同步会话） |
| **IPS** | 已知攻击特征检测与阻断 | 南北向主通道、数据中心入口 | 加密流量看不见（除非解密），误报需要调优 |
| **WAF** | HTTP 层攻击 | 对外发布的应用前端 | 只覆盖 Web，不理解非 HTTP 协议 |
| **代理 / CASB** | 出向访问控制与审计 | 互联网出口 | 需要终端配合（代理设置或 PAC） |

</div>

> ⚠️ **Three hard constraints in chokepoint design**:
> 1. **Chokepoints must be few and explicit** — inter-domain traffic has to converge on a small number of points, otherwise policy consistency and capacity planning become impossible;
> 2. **Encryption and inspection are inherently in conflict** — anything inside IPsec/TLS is invisible to IPS and DLP. Either terminate encryption at the chokepoint or accept that the segment is unobservable, **and that trade-off must be written into the design document**;
> 3. **Stateful device pairs must synchronize state** — otherwise every long-lived connection (database, SSH, ERP) breaks at the moment of failover, which presents as "the switchover succeeded but the business is down".

<div class="zh" markdown="1">

> ⚠️ **检查点设计的三条硬约束**：
> 1. **检查点要"少而明确"**——跨域流量必须收敛到少数几个点，否则无法保证策略一致性，也无法对它做容量规划；
> 2. **加密与检查天然冲突**——凡是过 IPsec/TLS 的流量，IPS 与 DLP 都失效。要么在检查点终结加密，要么接受"这段不可见"，**这个取舍必须写进设计文档**；
> 3. **有状态设备的双机必须同步状态**——否则切换瞬间所有长连接（数据库、SSH、ERP）全部中断，表现为"切换成功但业务断了"。

</div>

---

## Zero Trust Architecture (ZTA) · 零信任架构

Traditional security assumes everything inside the perimeter is trusted and only the outside is hostile. Once users, applications and data are spread across the Internet, home networks, public clouds and SaaS, that assumption collapses. Zero trust **treats every access as untrusted by default** and decides every time based on identity, device and context.

<div class="zh" markdown="1">

零信任架构是对安全的范式转变——不再是边界防火墙模型，而是**无边界架构，拒绝所有访问直到明确允许**。

</div>

### The Pillars of Zero Trust · 零信任架构的支柱

<figure class="fig">
<img src="assets/fig/en04-06-zero-trust-pillars.svg" alt="Six zero trust pillars beside the decision loop from subject through enforcement point to resource, fed by inventory and telemetry" loading="lazy">
<figcaption><b>Figure 4-6　The six pillars of zero trust and the decision loop that connects them</b><br><span>图 4-6　零信任的六根支柱与判定回路</span></figcaption>
</figure>


1. **Verify identity, every time**: identity is the new security perimeter, and authentication applies to users and devices alike
2. **Assess device posture**: are patches current, is disk encryption on, is EDR running, is the device managed
3. **Least privilege**: grant only the access needed for the task, never permanent broad access
4. **Microsegmentation**: enforce policy between workloads and applications, not just at the perimeter
5. **Continuous monitoring and response**: log, detect, analyze and respond; trust is dynamically adjusted
6. **Assume breach**: design as if the attacker is already inside — limit lateral movement and shorten dwell time

<div class="zh" markdown="1">

1. **网络始终被假定为敌对的**
2. **外部和内部威胁随时随地在**
3. **每个设备、应用、用户和网络流都被认证和授权**
4. **自动化系统是构建和运营零信任网络的基础**
5. **策略必须是动态的，从尽可能多的数据源计算**
6. **所有活动都被记录**

</div>

### Key Concepts · 零信任架构概念

<figure class="fig">
<img src="assets/fig/en04-07-trust-vs-risk.svg" alt="Subject trust plotted against resource risk with the required trust threshold rising with risk, beside the factors feeding each score" loading="lazy">
<figcaption><b>Figure 4-7　Trust is about the subject, risk is about the resource, and the resource sets the threshold</b><br><span>图 4-7　主体信任与资源风险：阈值由资源设定</span></figcaption>
</figure>


| Concept | Meaning |
|---------|---------|
| **Static factors** | Relatively stable attributes: user identity, role, department, device type |
| **Dynamic factors** | Attributes that change at runtime: location, time, patch state, behavior baseline |
| **Entitled to access** | The resource set a subject is allowed to reach under policy |
| **Trust score** | A continuous measure of how trustworthy the subject is right now |
| **Risk score** | The potential impact if this access goes wrong |
| **Authorization for access** | The final decision: allow, deny, or allow with constraints |
| **Inventory** | The inventory of identities, assets and applications — the prerequisite for policy |
| **Policy Engine** | Evaluates policy and produces the decision |
| **Trust Engine** | Aggregates static and dynamic factors into a trust score |
| **Endpoint device** | The device from which access originates |
| **PEP (Policy Enforcement Point)** | The point that actually enforces the decision |
| **Feedback loop** | Telemetry flows back to update trust and policy continuously |

<div class="zh" markdown="1">

| 概念 | 定义 |
|------|------|
| **静态因素 (Static Factors)** | 我们已知的项目，可预先基于此设定访问和授权。包括凭证、设备信任、网络、物理位置、生物特征、设备方向 |
| **动态因素 (Dynamic Factors)** | 可在访问时分析以改变授权级别的数据源。包括威胁情报、地理速度（当前位置与上次登录位置的差异）、GPS 坐标、实时数据分析 |
| **有权访问 (Entitled to Access)** | 用户基于角色的访问权限。不同角色（如财务用户 vs 人力资源用户）应有不同访问权限。也适用于设备（打印机 vs IoT 设备） |
| **信任分数 (Trust Score)** | 静态和动态因素的组合，持续提供身份保证。确定与资源风险值匹配的访问级别 |
| **风险分数 (Risk Score)** | 资产、应用和网络的风险级别阈值，必须被超过才允许访问 |
| **访问授权 (Authorization for Access)** | 信任分数和授权级别的组合。即使信任分数足够高，如果没有正确的授权级别，也不会被授予访问 |

</div>

### Core Capabilities · 零信任架构能力

| Capability | Description |
|------------|-------------|
| **Identity governance** | Joiner/mover/leaver automation, MFA, privileged account management |
| **Device posture assessment** | Continuous checks on patching, encryption, EDR and management enrolment |
| **Application-level access** | Access granted per application rather than per network segment |
| **Dynamic authorization** | Trust scores recomputed from context, with automatic downgrade or revocation |
| **Visibility and analytics** | Flow, log and behavior intelligence that detects anomalies |

<div class="zh" markdown="1">

| 能力 | 定义 | 也称为 |
|------|------|--------|
| **清单 (Inventory)** | 所有资源（用户、设备、工作负载、应用）的单一真相来源 | 策略信息点 (PIP) |
| **策略引擎 (Policy Engine)** | 实施策略、匹配规则、推送访问授权的位置 | 策略管理点 (PAP) + 策略决策点 (PDP) |
| **信任引擎 (Trust Engine)** | 通过持续分析资源状态动态评估整体信任。利用由静态和动态因素构建的信任分数 | 策略信息点 (PIP) |
| **终端设备 (Endpoint Device)** | 最终用户用来访问企业网络的任何设备 | 策略执行点 (PEP) |
| **基础设施设备 (Infrastructure Devices)** | 企业内的网络设备（交换机、路由器、防火墙） | 策略执行点 (PEP) |
| **策略执行点 (PEP)** | 执行信任和策略的位置 | - |
| **反馈循环 (Feedback Loop)** | 持续信息共享，通过 AI/ML、大数据和数据湖动态更改策略 | - |

</div>

### Migration Steps · 零信任迁移步骤

<figure class="fig">
<img src="assets/fig/en04-08-migration-steps.svg" alt="Five migration steps in order with their outputs, and the three prerequisites beneath them" loading="lazy">
<figcaption><b>Figure 4-8　Five migration steps with their outputs, gated by three prerequisites</b><br><span>图 4-8　零信任迁移五步、每步的产出，以及三个前提</span></figcaption>
</figure>


| Step | Content | Output |
|------|---------|--------|
| **1. Inventory** | Build three inventories: identity, asset, application | Who, with what device, uses which application |
| **2. Identity governance** | MFA coverage, automatic leaver revocation, privileged access management | No orphan accounts |
| **3. Segmentation** | Move from "the whole intranet is reachable" to "each application is reachable" | High-risk applications isolated first |
| **4. Policy and enforcement** | Application-level policy, device posture conditions | Enforceable rules, not just intent |
| **5. Continuous telemetry** | Log correlation, behavior baselines, dynamic adjustment | Trust recalculated in real time |

<div class="zh" markdown="1">

| 步骤 | 内容 |
|------|------|
| **1. 建立信任** | 用户身份多因素、设备上下文和身份、设备状态和健康、位置、相关属性和上下文、开发部署 |
| **2. 提供基于信任的访问** | 网络、应用、资源、用户和物 |
| **3. 持续验证信任** | 用于建立信任的原始条件仍然成立、流量不是威胁流量、任何风险/异常/恶意行为的行为检查、如果被攻破则信任被打破 |

</div>

#### Three Prerequisites · 零信任落地的三个前提（缺一不可）

| Prerequisite | Why it is required |
|--------------|--------------------|
| **A complete inventory** | Without knowing identities, assets and applications there is no way to write fine-grained policy |
| **Strong identity foundation** | MFA and lifecycle management come first; a ZTNA gateway without identity governance just moves the problem |
| **Operations capability** | Policy has to be tuned continuously; a policy that nobody maintains reverts to "allow everything" |

<div class="zh" markdown="1">

| 前提 | 具体是什么 | 没有它会怎样 |
|------|-----------|-------------|
| **身份目录是权威的** | 人员、角色、在职状态来自唯一权威源（HR/AD），离职即时失效 | 策略按"角色"下发，但角色数据过期 → 权限只增不减 |
| **有资产与应用清单** | 知道"有哪些应用、在哪个地址、属于哪个业务" | 无法写策略，只能全通；"最小权限"无从谈起 |
| **设备可被评估** | 终端有代理或证书，可上报补丁、加密、EDR 状态 | 只能验证"人"，不能验证"设备"，被入侵的合规设备仍畅通 |

</div>

> ⚠️ **The most common way zero trust projects fail**: buying a product first and discovering afterwards that the inventory does not exist, the identity data is a mess and the logs cannot be correlated. **Product is the carrier of the last step, not the first.**

<div class="zh" markdown="1">

> ⚠️ **这三个前提都是"非网络"工作，且都在网络团队之外**。这是零信任项目最常见的失败原因：技术方案完备，但主数据、资产清单、终端合规没人负责，项目停在 PoC 阶段。

</div>

#### ZTNA vs. Traditional VPN · 零信任网络访问 (ZTNA) 与传统 VPN 的区别

<figure class="fig">
<img src="assets/fig/en04-09-vpn-vs-ztna.svg" alt="VPN and ZTNA side by side: the VPN exposes a segment and every host in it, ZTNA exposes one named application while the rest stay unreachable" loading="lazy">
<figcaption><b>Figure 4-9　A VPN grants a segment; ZTNA grants an application</b><br><span>图 4-9　VPN 给的是一个网段，ZTNA 给的是一应用</span></figcaption>
</figure>


| Dimension | Traditional VPN | ZTNA |
|-----------|-----------------|------|
| Access granularity | Network-level (once connected, broadly reachable) | Application-level (only what is granted) |
| Trust basis | "Inside the VPN is trusted" | Continuous verification of identity, device and context |
| Exposure surface | The VPN gateway and possibly the whole intranet | Only the specific applications being accessed |
| Lateral movement | Easy after compromise | Constrained by segmentation and policy |
| Experience | Client plus route pushing | Clientless or lightweight client, per-application access |

<div class="zh" markdown="1">

| 维度 | 传统远程访问 VPN | ZTNA |
|------|----------------|------|
| 授权粒度 | **网络级**：拨进来就能访问网段 | **应用级**：只发布应用，不给网段 |
| 攻击面 | VPN 网关是公网暴露的高价值入口 | 应用连接器无需公网暴露，网关被攻破也拿不到网段 |
| 横向移动 | 进入后可在网内横向扫描 | 看不到网内其他资源，横向移动被切断 |
| 用户体验 | 全隧道时所有流量绕回总部（含上网流量） | 分应用接入，上网流量本地直出 |
| 前提 | 账号 + 密码（+ MFA） | 身份 + 设备状态 + 上下文持续评估 |

</div>

> 💡 **Key point**: **ZTNA is not "a better VPN", it turns access from network-centric into identity-centric.** Therefore the migration must be organized by application (the unit of access) rather than by site (the unit of the VPN era).

<div class="zh" markdown="1">

> 💡 **别把零信任理解成"取消分段"**。零信任改变的是**授权依据**（从"你在哪个网段"变成"你是谁、用什么设备、在什么上下文"），它仍然需要分段与检查点来落地。网络侧的分段（第 10 章）与身份侧的授权是**两条并行防线**，不能互相替代。

</div>

---

## The CIA Triad · 安全 CIA 三要素

The CIA triad is the classic model of information security:

<div class="zh" markdown="1">

机密性、完整性和可用性是信息安全的基础。这些元素帮助构建保护信息和资源免受未授权访问、修改、检查或破坏的安全系统。

</div>

| Element | Definition | Typical threats | Design means |
|---------|------------|-----------------|--------------|
| **Confidentiality** | Data is seen only by authorized parties | Eavesdropping, data theft, over-privileged access | Encryption (in transit and at rest), access control, segmentation |
| **Integrity** | Data is modified only by authorized parties and is complete and accurate | Tampering, replay, code injection | Hashing and signatures, change control, immutable logs |
| **Availability** | Authorized parties can use resources when needed | DDoS, device failure, misconfiguration | Redundancy, capacity margin, DDoS mitigation, backup and recovery |

<div class="zh" markdown="1">

| 要素 | 特征 | 实现机制 |
|------|------|---------|
| **机密性 (Confidentiality)** | 防止未授权访问信息，维持传输信息的保密性 | 加密、用户 ID 和密码（双因素认证更常见）、安全令牌 |
| **完整性 (Integrity)** | 端到端维持准确信息，确保未被未授权实体篡改 | 加密、数据校验和、哈希 |
| **可用性 (Availability)** | 确保服务和系统始终可用，授权用户可在需要时访问。现代网络中可用性不仅用上线/下线时间衡量，还用质量衡量（如恶意流量增加延迟导致 VoIP 质量下降） | 高可用性系统设计（网络、存储、计算、应用层），防止 DoS 等攻击 |

</div>

#### Design Means for Each Element and Their Conflicts · 三要素对应的设计手段与代价

<figure class="fig">
<img src="assets/fig/en04-10-cia-tradeoffs.svg" alt="The CIA triangle with the means for each goal and three conflict panels: encryption against detection, availability against confidentiality, integrity against availability" loading="lazy">
<figcaption><b>Figure 4-10　CIA is a triangle of trade-offs: every means takes something from the other two goals</b><br><span>图 4-10　CIA 是取舍三角：手段与代价</span></figcaption>
</figure>


The three CIA goals constantly pull against each other in design: encryption hides traffic from inspection, isolation raises availability risk, and log retention widens the exposure surface. The table below maps each goal to its primary means and to the conflict the means creates.

<div class="zh" markdown="1">

三要素不是并列的口号，而是一组**会互相打架的目标**。设计者的工作是在具体场景里排出优先级：

</div>

| Goal | Primary means | Side effect of the means | How to handle the conflict |
|------|---------------|--------------------------|----------------------------|
| Confidentiality | Encryption, segmentation | Encrypted traffic cannot be inspected, so detection weakens | Terminate encryption at inspection points; compensate unobservable segments with endpoint EDR and behavior baselines |
| Integrity | Signatures, change control, immutable logs | Strict change control slows response to failures | Pre-approve emergency change paths and audit them afterwards |
| Availability | Redundancy, capacity margin | Attack surface and cost rise | Rank availability targets by business function (RTO/RPO) rather than applying the same standard everywhere |

<div class="zh" markdown="1">

| 要素 | 设计手段 | 代价 / 副作用 |
|------|---------|--------------|
| **机密性** | 链路加密（IPsec/MACsec）、存储加密、访问控制、数据分级 | 加密后 IPS/DLP 看不见内容；加解密消耗性能；密钥管理成为新的单点 |
| **完整性** | 数字签名、哈希校验、配置基线与变更审计、防篡改日志 | 需要额外的签名/校验环节；日志本身必须防篡改（否则审计无效） |
| **可用性** | 冗余（设备/链路/运营商）、容量与 DDoS 清洗、限速与队列、快速收敛 | 冗余带来复杂度与成本；清洗中心会改变路径与源地址；限速可能误伤正常突发 |

</div>

> ⚠️ **CIA is a triangle of trade-offs, not three checkboxes**. Every encryption and every segmentation choice **takes something away** from the other two goals. The design document should say which goal was traded for which, or the security design cannot be reviewed or defended.

<div class="zh" markdown="1">

> ⚠️ **最常见的三对冲突**（评审时必须问）：
> 1. **加密 vs 检测**：全链路加密后，IPS 与数据防泄漏形同虚设。解法通常是"在检查点终结加密"，或接受这段不可见并靠终端侧 EDR 补偿。
> 2. **可用性 vs 机密性**：为了抗 DDoS 把所有流量牵引到清洗中心，等于把流量交给第三方可见。
> 3. **完整性 vs 可用性**：严格的配置基线校验会阻止"故障中的应急修改"，而应急修改往往是恢复业务最快的手段。解法是**允许应急但强制事后反哺**（第 12 章漂移检测的做法）。

</div>

---

## Regulatory Compliance · 法规合规

Enterprises today must satisfy a large number of regulatory requirements, and many of them carry **legal liability**. For the network designer, the key is not to memorize every clause but to know how each regulation becomes a design constraint.

<div class="zh" markdown="1">

网络设计师应能够获取任何合规标准，并设计符合其特定约束的解决方案。

</div>

### HIPAA · HIPAA（美国健康保险流通与责任法案）

<figure class="fig">
<img src="assets/fig/en04-11-hipaa-phi-path.svg" alt="PHI on the clinician workstation, in the EHR, in the exchange with insurers and in backups, each with the safeguard it forces, then the four obligations the network owes" loading="lazy">
<figcaption><b>Figure 4-11　Where PHI lives, and the safeguard each place forces on the network</b><br><span>图 4-11　PHI 在哪里，以及每处对网络提出的要求</span></figcaption>
</figure>


The Health Insurance Portability and Accountability Act protects the privacy and security of **protected health information (PHI)** in the United States.

<div class="zh" markdown="1">

1996 年颁布，由民权办公室执行。

</div>

| Requirement | Content |
|-------------|---------|
| **Privacy Rule** | Limits who may access PHI and under what circumstances |
| **Security Rule** | Administrative, physical and technical safeguards for electronic PHI |
| **Breach notification** | Mandatory notification when PHI is breached |
| **Technical safeguards** | Access control, audit logs, transmission security, integrity controls |

<div class="zh" markdown="1">

| 规则 | 内容 |
|------|------|
| **隐私规则** | 保护个人可识别健康信息 (PHI) 的隐私 |
| **安全规则** | 设定电子健康信息的国家安全标准 |
| **患者安全规则** | 保护用于分析患者安全事件和改善安全的可识别信息 |

</div>

For network design this translates into: **encrypted transmission, strict access control, complete audit trails, and isolation of systems that handle PHI.**

<div class="zh" markdown="1">

**适用场景**：医院、诊所、保险机构、与覆盖实体密切合作的服务提供商。

</div>

### PCI DSS · PCI DSS（支付卡行业数据安全标准）

<figure class="fig">
<img src="assets/fig/en04-12-pci-scope.svg" alt="The cardholder data environment before and after segmentation, with the audit scope following the network in one and the data in the other, beside the four levers that shrink it" loading="lazy">
<figcaption><b>Figure 4-12　PCI DSS: the audit follows the network before segmentation, and the data after it</b><br><span>图 4-12　PCI DSS：分段前审计跟着网络走，分段后跟着数据走</span></figcaption>
</figure>


The Payment Card Industry Data Security Standard applies to any organization that stores, processes or transmits cardholder data.

<div class="zh" markdown="1">

由信用卡公司强制要求，确保信用卡交易安全。由 PCI 安全标准委员会开发和管理。

</div>

**The twelve requirements**:

<div class="zh" markdown="1">

**12 项要求**：

</div>

| Group | Requirements |
|-------|--------------|
| **Build and maintain a secure network** | 1. Install and maintain firewall configuration; 2. Do not use vendor defaults for system passwords |
| **Protect cardholder data** | 3. Protect stored cardholder data; 4. Encrypt transmission of cardholder data across open networks |
| **Vulnerability management** | 5. Protect against malware; 6. Develop and maintain secure systems and applications |
| **Access control** | 7. Restrict access by business need to know; 8. Identify and authenticate access to system components; 9. Restrict physical access |
| **Monitoring and testing** | 10. Track and monitor all access; 11. Test security systems and processes regularly |
| **Information security policy** | 12. Maintain a policy addressing information security |

<div class="zh" markdown="1">

| 编号 | 要求 |
|------|------|
| 1 | 安装和维护防火墙配置以保护持卡人数据 |
| 2 | 不使用供应商提供的默认系统密码和安全参数 |
| 3 | 保护存储的持卡人数据 |
| 4 | 加密在开放公共网络上传输的持卡人数据 |
| 5 | 保护所有系统免受恶意软件攻击，定期更新防病毒软件 |
| 6 | 开发和维护安全的系统及应用 |
| 7 | 按业务需要限制对持卡人数据的访问 |
| 8 | 识别和认证对系统组件的访问 |
| 9 | 限制对持卡人数据的物理访问 |
| 10 | 跟踪和监控对网络资源和持卡人数据的所有访问 |
| 11 | 定期测试安全系统和流程 |
| 12 | 维护针对所有人员的信息安全策略 |

</div>

**Network design impact**: separate the cardholder data environment into its own segment, encrypt all traffic crossing public networks, centralize and protect logs, and **limit the scope of the audit** — the smaller the cardholder data environment, the lower the compliance cost.

<div class="zh" markdown="1">

**适用场景**：有销售点系统或在线订购系统的企业——快餐店、零售店、在线商店等所有存储、处理和传输持卡人数据的实体。

</div>

### GDPR · GDPR（通用数据保护条例）

The General Data Protection Regulation protects the personal data of individuals in the EU and applies to any organization handling that data, wherever it is located.
**Core principles**: lawfulness, fairness and transparency; purpose limitation; data minimization; accuracy; storage limitation; integrity and confidentiality; accountability.

<div class="zh" markdown="1">

欧盟数据保护法规，为从个人收集和处理个人信息设定指导原则。

</div>

**Key point**: GDPR gives the data subject the rights of access, rectification, erasure (the right to be forgotten) and portability. **Design implication**: the designer must be able to answer "where is this piece of personal data stored, who can see it, how long is it kept" — which in practice forces data classification and a distributed inventory.

<div class="zh" markdown="1">

**重要**：GDPR 不仅适用于欧盟公司，还适用于向欧盟居民提供产品或服务的任何组织。

</div>

**Special categories of personal data** (higher protection requirements):
- Health and genetic data
- Biometric data
- Racial or ethnic data
- Political opinions
- Sexual orientation

<div class="zh" markdown="1">

**GDPR 保护的个人数据类型**：
- 基本身份信息（姓名、地址、身份证号）
- Web 数据（位置、IP 地址、Cookie 数据、RFID 标签）
- 健康和基因数据
- 生物特征数据
- 种族或民族数据
- 政治观点
- 性取向

</div>

### Data Sovereignty · 数据主权

<figure class="fig">
<img src="assets/fig/en04-13-gdpr-sovereignty.svg" alt="Three GDPR questions with their deliverables, and a border diagram showing what may cross and what must stay local" loading="lazy">
<figcaption><b>Figure 4-13　GDPR's three questions, and the border that decides what may cross</b><br><span>图 4-13　GDPR 三问，以及什么可以过境</span></figcaption>
</figure>


Information is governed by the regulations of the country where it is collected and processed. Information collected and processed in a country must remain within that country's borders and be protected under its law.

<div class="zh" markdown="1">

信息受其收集和处理所在地的法规约束。信息在某个国家收集和处理后，必须留在该国边界内，并按该国法律保护。

</div>

> This is commonly encountered when an enterprise sends data to another country (where its servers or data centers are) or migrates to a cloud provider. The data may not leave the country and must be stored under that country's regulations.

<div class="zh" markdown="1">

> 常见于企业将数据发送到其他国家（服务器/数据中心所在地）或迁移到云提供商时。相关数据不能离开该国，必须按该国法规存储。

</div>

### Translating Compliance into Design Input · 把合规翻译成设计输入

<figure class="fig">
<img src="assets/fig/en04-14-compliance-to-design.svg" alt="Five compliance clauses mapped to the network design element each forces and to the artefact that proves it later" loading="lazy">
<figcaption><b>Figure 4-14　Five clauses, the design element each forces, and the artefact that proves it</b><br><span>图 4-14　五条合规条款、逼出的设计要素与证明它的交付物</span></figcaption>
</figure>


Compliance clauses read as "requirements", while design needs "constraints". The translation method is **three questions**:

<div class="zh" markdown="1">

合规条款读起来都是"要求"，但设计需要的是"约束"。翻译的方法是**三问**：

</div>

| Question | Output | Example (GDPR + China business) |
|----------|--------|--------------------------------|
| **What is the data and where is it** | Data classification and distribution map | Customer identity data (sensitive) / order summaries (can be de-identified) / logs (contain IPs, hence personal data) |
| **Where is the boundary** | Logical and physical boundaries | Domestic/foreign boundary, production/test boundary, supplier access scope |
| **How is it proven** | Evidence chain (audit trail) | Access logs, encryption status, approval records, change records — and **retention must meet the requirement** |

<div class="zh" markdown="1">

| 三问 | 输出 | 例子（GDPR + 中国区业务） |
|------|------|--------------------------|
| **数据是什么、在哪** | 数据分类与分布图 | 客户实名信息（敏感）/ 订单汇总（可脱敏）/ 日志（含 IP，属个人数据） |
| **边界在哪** | 逻辑与物理边界 | 境内/境外边界、生产/测试边界、供应商可访问范围 |
| **怎么证明** | 证据链（audit trail） | 访问日志、加密状态、审批记录、变更记录，且**留存期符合要求** |

</div>

**Typical mapping from compliance clause to network design**:

<div class="zh" markdown="1">

**合规条款 → 网络设计的典型映射**：

</div>

| Compliance requirement | Network design impact |
|------------------------|-----------------------|
| Encryption in transit (PCI DSS requirement 4) | Public links must use IPsec/TLS; internal links are decided by data classification (for example whether MACsec is required) |
| Least-privilege access (PCI DSS requirement 7) | The cardholder data environment is separately segmented (VLAN/VRF); all cross-domain traffic passes a stateful device |
| Log retention and immutability (PCI DSS 10, GDPR) | Dedicated log segment + one-way export + a unified NTP time source (logs with the wrong time have no evidentiary value) |
| Data residency (data sovereignty) | In-country instances + one-way de-identified data flow + local storage, including the monitoring collection points |
| Auditable third-party access (HIPAA, GDPR) | Suppliers connect through a dedicated channel, access is opened temporarily per ticket, sessions are recorded with command auditing |

<div class="zh" markdown="1">

| 合规要求 | 网络设计影响 |
|---------|-------------|
| 传输加密（PCI DSS 第 4 项） | 跨公网链路必须 IPsec/TLS；内部链路由数据分级决定是否需要 MACsec |
| 访问最小化（PCI DSS 第 7 项） | 持卡人数据环境独立分段（VLAN/VRF），跨域一律过有状态设备 |
| 日志留存与不可篡改（PCI DSS 第 10 项、GDPR） | 日志服务器独立网段 + 单向外送 + NTP 统一时间源（时间不准的日志没有证据价值） |
| 数据驻留（数据主权） | 境内实例 + 脱敏单向数据流 + 本地存储，连监控采集点也要在境内 |
| 可审计的第三方访问（HIPAA、GDPR） | 供应商接入走独立通道、按工单临时开通、全程录屏/命令审计 |

</div>

> 💡 **The key action in a compliance project is "evidence chain design", not "control design".** Auditors do not look at what you configured; they look at whether you can prove "it really was that way at any point in time". So **logs, time synchronization, change records and periodic reviews** are part of the design deliverable and must be handed over together with the network design.

<div class="zh" markdown="1">

> 💡 **合规项目的关键动作是"证据链设计"**，而不是"控制措施设计"。审计员不看你配了什么，而是看你能否证明"在任意时刻它确实是那样"。因此**日志、时间同步、变更记录、定期复核**要作为设计交付物的一部分，与网络方案一起交付。

</div>

---

## Case Studies · 实战案例

### Case 1: All the Appliances Were Bought, and a Phishing Email Still Got In · 案例一：设备买齐了，还是被一封钓鱼邮件攻破

**Background**: an enterprise spent about 12M over three years and owned perimeter firewalls, IPS, WAF and sandboxing — yet suffered a ransomware incident that cost three days of production stoppage.

<div class="zh" markdown="1">

**背景**：某企业三年投入约 1200 万，边界防火墙、IPS、WAF、沙箱一应俱全，仍发生一次勒索事件，损失 3 天停产。

</div>

**Reconstructing the attack chain**:

<div class="zh" markdown="1">

**攻击链复盘**：

</div>

```
Phishing email → employee opened it on a personal laptop → laptop plugged into the office network (unmanaged)
        → lateral scanning found an unpatched file server
        → domain administrator account (password unchanged for 5 years, shared by many)
          encrypted files in bulk
```

<figure class="fig">
<img src="assets/fig/en04-15-case1-attack-chain.svg" alt="The five stages of the first case study's attack chain with the missing control beneath each, the same chain plotted on a clock from delivery to the first alarm, and a summary of what was bought against what was missing" loading="lazy">
<figcaption><b>Figure 4-15　The attack chain of Case 1, the control missing at each stage, and the same chain on a clock</b><br><span>图 4-15　案例一的攻击链、每一环缺失的控制，以及同一条链的时间轴</span></figcaption>
</figure>


<div class="zh" markdown="1">

```
钓鱼邮件 → 员工在个人笔记本打开 → 该笔记本接在办公网（未被管理）
        → 横向扫描找到一台未打补丁的文件服务器
        → 用域管理员账号（密码 5 年未换、多人共用）批量加密文件
```

</div>

**Why the security devices did not stop it**:

<div class="zh" markdown="1">

**安全设备为什么没拦住**：

</div>

| Stage | Why it failed | Relevant principle |
|-------|---------------|--------------------|
| Phishing email | The sandbox inspected attachments only, not links to **newly registered domains** | Mail path must integrate with threat intelligence |
| Personal laptop connection | Only **port authentication** was enforced, no **device compliance check** | Zero trust: verify the device before granting access |
| Lateral movement | Office network was **fully open** to the server segment | Missing microsegmentation / least privilege |
| Shared domain administrator account | No privileged account management, no MFA | Identity is the new perimeter |

<div class="zh" markdown="1">

| 环节 | 为什么失效 | 对应原则 |
|------|-----------|---------|
| 钓鱼邮件 | 沙箱只查附件，不查**首次出现的域名**链接 | 需要邮件链路与威胁情报联动 |
| 个人笔记本接入 | 只做了**端口认证**，没做**设备合规检查** | 零信任：先验证设备再给权限 |
| 横向移动 | 办公网到服务器区**全通** | 微分段/最小权限缺失 |
| 域管理员共用账号 | 无特权账号管理、无 MFA | 身份是新的边界 |

</div>

**What actually had to be added was "the non-appliance part"**: device compliance admission, microsegmentation, privileged account management, MFA, and **detection capability** (until then the only alarm was antivirus software).

<div class="zh" markdown="1">

**补齐的其实是"非设备"部分**：设备合规准入、微分段、特权账号管理、MFA、以及**检测能力**（原来只能靠杀毒软件报警）。

</div>

> 💡 **Lesson**: **that security is "pervasive" means it cannot rest on perimeter appliances alone.** The identity, device, least-privilege and visibility topics this chapter stresses are exactly the parts most easily replaced by "buying appliances".

<div class="zh" markdown="1">

> 💡 **教训**：**安全是"普适的"，意味着它不能只靠边界设备。** 本章强调的身份、设备、最小权限、可见性，恰恰是最容易被"买设备"替代掉的部分。

</div>

### Case 2: One "Data May Not Leave the Country" Requirement Redesigned the Whole Architecture · 案例二：一条"数据不出境"的合规要求，改了整个架构

**Background**: the China region of a multinational needed access to the global ERP. Group required a unified architecture, while China compliance required that **customer data may not leave the country**.

<div class="zh" markdown="1">

**背景**：某跨国企业中国区需要访问全球 ERP。集团要求统一架构，中国区合规要求**客户数据不得出境**。

</div>

**Design decisions forced by the constraint**:

<div class="zh" markdown="1">

**约束带来的连锁设计决定**：

</div>

| Constraint | Architectural impact |
|------------|----------------------|
| Data may not leave the country | China must run a **local instance**; remote access alone is not acceptable |
| Consistent global user experience | **Data synchronization** is needed, but only de-identified summary data may be synchronized |
| Unified identity | The identity directory can be global (without personal data), but **logs must be retained locally** |
| Unified operations | Monitoring can be centralized, but **collection points and storage must be domestic** |

<div class="zh" markdown="1">

| 约束 | 架构影响 |
|------|---------|
| 数据不出境 | 中国区必须部署**本地实例**，不能只做远程访问 |
| 全球统一用户体验 | 需要**数据同步**，但只能同步脱敏后的汇总数据 |
| 统一身份 | 身份目录可全球统一（不含个人数据），但**日志必须本地留存** |
| 统一运维 | 监控可集中，但**采集点与存储必须在境内** |

</div>

**Final shape**: an independent in-country zone + one-way de-identified data egress + a global policy management plane (distributing configuration only, carrying no data).

<div class="zh" markdown="1">

**最终形态**：境内独立区域 + 单向脱敏数据出站 + 全球统一策略管理面（只下发配置、不携带数据）。

</div>

> 💡 **Lesson**: **compliance is the hardest constraint, and a single requirement can derive a whole architecture.** Treat it as **design input** (the constraints from Chapter 1), not something to confirm with legal before go-live.

<div class="zh" markdown="1">

> 💡 **教训**：**合规是最硬的约束，它会从一条要求推导出一整套架构。** 处理方式是把它当作**设计输入**（第 1 章的约束），而不是上线前再找法务确认。

</div>

---

## Design Pitfalls · 设计缺陷

| Pitfall | Symptom | Consequence | Correct practice |
|---------|---------|-------------|------------------|
| **Treating security as "one more appliance at the end"** | The security team is asked to "review it" after the design is final | Only perimeter patches are possible; identity and segmentation can no longer be changed | Policy and domain design join at the requirements stage (pervasive security, Chapter 1) |
| **Policy without an exception process** | The policy says "must encrypt / must approve" but never who judges exceptions or how often they are reviewed | Exceptions get approved verbally, and six months later nobody can explain why access was opened | Every control objective gets an exception path: who approves, validity period, review cycle, where it is recorded |
| **Domains too fine or too coarse** | Thirty domains, or a single domain for everything | The first loses control of policy maintenance, the second fails all at once | Draw on trust level + compliance boundary + blast radius; typically 5–12 domains |
| **Endless chokepoints** | A firewall in series on every link | More failure points, longer troubleshooting paths, complex state synchronization | Converge cross-domain traffic to a few explicit chokepoints, designed separately for capacity and HA |
| **Encrypted, therefore assumed "protected"** | IPS policy disabled after end-to-end IPsec | Attacks travel freely inside the tunnel and leave no logs at all | State clearly "which segments are inspectable and which are not"; compensate invisible segments on the endpoint side |
| **Zero trust that authenticates but never inventories** | MFA and NAC are deployed, but no application or asset inventory exists | Policy can only be written as "allow all", so least privilege stays unimplemented | Build the three inventories (identity, asset, application) first, then discuss dynamic authorization |
| **Reading zero trust as "no more segmentation"** | "We have identity now, so we do not need isolation" | A compromised compliant device can still move laterally | Identity authorization and network segmentation run as two parallel lines of defense |
| **RTO/RPO conflicts with security controls left unidentified** | Encryption and chokepoints lengthen recovery, but the RTO target is unchanged | The gap only shows up in an exercise | Recalculate RTO after adding security controls, and write a "degraded mode" into the design |
| **Compliance engaged only at the end** | Legal and compliance see the design two weeks before go-live | Architecture-level rework (cross-border data, log retention location) | Compliance enters the Chapter 1 constraint list as design input, as early as possible |

<div class="zh" markdown="1">

| 缺陷 | 表现 | 后果 | 正确做法 |
|------|------|------|---------|
| **把安全当"最后加一层设备"** | 方案定稿后才请安全团队"评审一下" | 只能靠边界设备补丁式补救，身份与分段层无法回头改 | 策略与域划分在需求阶段就进场（第 1 章的"普适安全"） |
| **有策略无例外流程** | 策略写"必须加密/必须审批"，没写谁来判例外、多久复核 | 例外靠口头批准，半年后无人能解释为什么放通 | 每个控制目标配一条例外流程：谁批准、有效期、复核周期、留痕位置 |
| **域划得过细或过粗** | 划出 30 个域，或全网一个域 | 前者策略维护失控，后者一破全破 | 以信任等级 + 合规边界 + 爆炸半径为据，通常 5–12 个域 |
| **检查点无限增加** | 每条链路都串防火墙 | 故障点多、排障路径长、状态同步复杂 | 跨域流量收敛到少数明确检查点，容量与高可用单独设计 |
| **加密了却以为"被保护"** | 全链路 IPsec 后关闭了 IPS 策略 | 攻击在加密隧道内畅通，且完全无日志 | 明确"哪段可检查、哪段不可见"，不可见段用终端侧手段补偿 |
| **零信任只做认证不做清单** | 上了 MFA 与 NAC，但没有应用/资产清单 | 策略只能写成"全通"，最小权限无法落地 | 先建三类清单（身份、资产、应用），再谈动态授权 |
| **把零信任当"取消分段"** | 认为"有身份了就不需要网络隔离" | 被入侵的合规设备仍可横向移动 | 身份授权与网络分段两条防线并行 |
| **RTO/RPO 与安全控制冲突未识别** | 加密/检查点使恢复时间变长，但 RTO 目标没调整 | 演练时发现做不到 | 加入安全控制后重新计算 RTO，并把"降级模式"写进方案 |
| **合规只在项目末期介入** | 法务/合规在上线前两周才看到方案 | 架构级返工（数据出境、日志留存位置） | 合规作为设计输入进入第 1 章的约束清单，越早越好 |

</div>

---

## Lessons Learned · 实战经验总结

| Lesson | Explanation |
|--------|-------------|
| **Write the control objective before choosing the technology** | "Cross-domain access must be auditable" is a control objective; firewall, WAF and proxy are means. Objectives are stable, means are replaceable |
| **The same policy has several implementations differing by an order of magnitude in cost** | Encrypted VLL, application-layer encryption and physically dedicated circuits all satisfy "must be encrypted"; lay out the options and their costs first |
| **The number of domains is a trade-off, not an ideal** | Finer domains mean stronger isolation and higher maintenance cost. Find the number the team can genuinely maintain |
| **The segment you cannot see needs compensating controls** | When encrypted traffic cannot be inspected by IPS, cover it with endpoint EDR, log correlation and behavior baselines |
| **Compliance deliverables need an evidence chain** | Logs + unified NTP time + change records + periodic review records; miss one and the audit fails |
| **Identity is the new perimeter, but the identity system is not owned by the network team** | Zero trust projects must include HR, IT desktop and the identity team, or they stall at the inventory step |
| **The security design must be acceptable to the business** | Express it in business language: downtime, onboarding time, audit pass rate — not "how many appliances were deployed" |
| **Reject the "security equals buying appliances" path dependency** | Case 1 shows that with every appliance in place the enterprise was still breached; what was missing was admission control, segmentation, privileged accounts and detection |

<div class="zh" markdown="1">

| 经验 | 说明 |
|------|------|
| **先写控制目标，再选技术** | "跨域访问必须可审计"是控制目标，防火墙/WAF/代理是手段。目标稳定，手段可换 |
| **同一策略有多种实现，成本差一个数量级** | 加密 VLL、应用层加密、物理独占都能满足"必须加密"，先把选项与代价摆出来 |
| **域的数量是取舍不是理想** | 域越细，隔离越强，维护成本越高。找"团队真的能维护"的那个数量 |
| **不可见的那一段必须有补偿手段** | 加密流量无法被 IPS 检查时，靠终端 EDR、日志关联、行为基线补上 |
| **合规交付物里要有证据链** | 日志 + NTP 统一时间 + 变更记录 + 定期复核记录，缺一项审计就通不过 |
| **身份是新的边界，但身份系统不在网络团队手里** | 零信任项目必须拉上 HR/IT 桌面/身份团队，否则卡在"清单"环节 |
| **安全方案要能被业务验收** | 用业务语言表达：停机时间、上线周期、审计通过率，而不是"部署了几台设备" |
| **拒绝"安全 = 买盒子"的路径依赖** | 案例一说明：设备齐全仍被攻破，缺的是准入、分段、特权账号与检测 |

</div>

---

## Design Scenarios (2) · 设计情景演练（2 个）

### Scenario 1: One Sentence, "Data May Not Leave the Country", Redesigned Three Layers · 情景一：一句"数据不得出境"，改了三层架构

**Situation**: a multinational medical device company has an R&D center in China (R&D data in a local equipment room). The Asia-Pacific headquarters in Singapore uses the same global PLM system (deployed in Ireland). China employees need PLM access for design reviews; the global operations team needs access to the operations interfaces of the China equipment room for patching and backup. Legal is explicit: R&D data generated in China and patient-related data may not leave the country.

<div class="zh" markdown="1">

**场景**：某跨国医疗器械公司在华有研发中心（研发数据存本地机房），亚太区总部在新加坡使用同一套全球 PLM 系统（部署在爱尔兰）。中国区员工需要访问 PLM 做设计评审；全球运维团队需要访问中国机房的运维接口做补丁与备份。法务明确：中国境内产生的研发数据与患者相关数据不得出境。

</div>

**Questions to answer**:
1. Which traffic is "business essential" and which is simply "convenient"?
2. How far must the network design change?
3. How can the operations channel be preserved without violating data sovereignty?

<div class="zh" markdown="1">

**要回答的问题**：
1. 哪些流量是"业务必需"、哪些是"图省事"？
2. 网络设计要改到什么程度？
3. 运维通道怎么在"不违反数据主权"的前提下保留？

</div>

**Reference approach**:
- **The first step is not design, it is data classification.** Split data into "must stay in country", "may leave (after de-identification or aggregation)" and "irrelevant". **Without classification, every architecture decision turns into a tug of war between legal and IT.**
- **Data decides the architecture position**: since the PLM data may not leave, **move compute next to the data** — deploy a local PLM instance or cache layer in China, or use the provider's in-country regional node — instead of having employees reach Ireland across the border.
- **Only essential traffic crosses the border**: design review deliverables (3D models, drawings) can be synchronized after de-identification, with direction, frequency and approval written into the design. **Do not mirror the whole database across the border** — expensive and non-compliant.
- **Operations channel**: the global team must pass through **an in-country jump host + strong identity + full session recording**, with technical limits on what they can see (system state only, not business data). **"Operations needs it" is not an exemption from data sovereignty; it is a constraint the design must satisfy.**
- **Outputs that must be documented**: a data flow diagram (which data, from where to where, and why), the legal basis for every cross-border path, and how audit evidence is retained.

<div class="zh" markdown="1">

**参考思路**：
- **第一步不是设计，而是数据分类。** 把数据分成"必须留在境内""可以出境（脱敏/聚合后）""无所谓"三类。**没有分类，任何架构决策都会变成法务与 IT 的拉锯。**
- **架构位置由数据决定**：既然 PLM 中的数据不能出境，就让**计算靠近数据**——在中国区部署 PLM 的本地实例/缓存层，或使用供应商的境内区域节点；而不是让员工跨境访问爱尔兰。
- **跨境只走必要流量**：设计评审所需的"共享件"（三维模型、图纸）可以脱敏后同步，同步方向、频率、审批都写进设计；**不做"全库跨境镜像"**（既贵又违规）。
- **运维通道**：全球团队访问境内机房必须经过**境内跳板 + 强身份 + 全程录屏审计**，并对"能看到什么"做技术限制（不看业务数据，只看系统状态）。**"运维需要"不是豁免数据主权的理由，只是一个需要被设计满足的约束。**
- **必须留痕的产出**：数据流图（哪类数据、从哪到哪、为什么）、每条跨境路径的法律依据、审计证据的保存方式。

</div>

### Scenario 2: From "Perimeter + VPN" Toward Zero Trust · 情景二：从"边界 + VPN"走向零信任

**Situation**: a 3,000-person group runs dual firewalls at headquarters plus a VPN for all employees to reach the intranet (inside the VPN everything is trusted). Two incidents in the past two years: a contractor used a VPN account to scan the intranet laterally, and a departing employee's account was not revoked in time. The group wants "zero trust"; the vendor quote is 8M with a 12-month implementation.

<div class="zh" markdown="1">

**场景**：某集团 3000 人，现状是总部双防火墙 + 全员工 VPN 接入内网（VPN 后即"内网可信"）。近两年发生两起事件：外包人员用 VPN 账号横向扫描内网；离职员工账号未及时回收。集团要求"上零信任"，安全厂商报价 800 万，实施周期 12 个月。

</div>

**Questions to answer**:
1. What is the real shortcoming today, and can buying a zero trust product fix it?
2. Which group of people and which set of applications should the migration start with?
3. In the 8M proposal, what is mandatory and what can be deferred?

<div class="zh" markdown="1">

**要回答的问题**：
1. 现状真正的短板是什么？买零信任产品能解决吗？
2. 迁移应该从哪一批人和哪一批应用开始？
3. 800 万的方案里，哪些是必须的、哪些是可后置的？

</div>

**Reference approach**:
- **The shortcoming is not "no zero trust appliance" but "identity lifecycle" and "lateral reachability".** Accounts that are never revoked and a VPN that opens the whole network — unless those two are fixed, any new product just moves the same risks somewhere else.
- **Start with a "minimum viable zero trust"**: ① identity governance (automatic joiner/mover/leaver synchronization, full MFA coverage); ② change "the intranet is reachable" into "each application is reachable" (segment ten high-risk applications first, such as finance, HR and the code repository); ③ add device compliance checks (patching, encryption, EDR state); ④ connect logs and alerting.
- **Roll applications out in batches**: start with "high value + low coupling + concentrated users" (OA, finance), prove out policy, user experience and operations, then move to engineering applications. **Zero trust projects that switch everything at once fail at a very high rate.**
- **Budget ordering**: identity and MFA (mandatory), application segmentation and policy enforcement points (mandatory), device compliance assessment (should do), UEBA/behavior analytics (deferrable), full traffic decryption and inspection (high risk, high cost, proceed carefully).
- **Acceptance criteria must be measurable**: not "deployment complete", but "a contractor account loses all access within 15 minutes of the offboarding process being triggered" and "the success rate of lateral probing from any endpoint to the finance system is zero".
- **One sentence**: **the order for implementing zero trust is "identity → segmentation → policy → telemetry"; products are only the carrier for those steps.**

<div class="zh" markdown="1">

**参考思路**：
- **短板不是"没有零信任设备"，而是"身份生命周期"和"横向可达性"。** 账号不回收、VPN 后能扫全网——这两个问题不解决，任何新产品都只是把同一批风险挪个位置。
- **先做"最小可行零信任"**：① 身份治理（入职/离职/转岗自动同步、MFA 全覆盖）；② 把"内网可达"改成"按应用可达"（先做 10 个高风险应用的分域，例如财务、HR、代码库）；③ 加设备合规检查（补丁、加密、EDR 状态）；④ 打通日志与告警。
- **应用分批**：从"高价值 + 低耦合 + 用户集中"的应用开始（如 OA、财务），跑通策略、体验、运维三件事，再推工程类应用。**一次性全量切换的零信任项目，失败率极高。**
- **预算排序**：身份与 MFA（必须）、应用分域与策略执行点（必须）、设备合规评估（应做）、UEBA/行为分析（可后置）、全流量解密与检测（高风险高成本，谨慎）。
- **验收标准要可测**：不是"部署完成"，而是"外包账号在离职流程触发后 15 分钟内失去全部访问权限""从任一终端到财务系统的横向探测成功率 = 0"。
- **一句话**：**零信任的落地顺序是"身份 → 分域 → 策略 → 遥测"，产品只是这几步的载体。**

</div>

---

## Key Terms · 本章关键术语

| Term | Meaning |
|------|---------|
| Zero Trust Architecture (ZTA) | Architecture that trusts no access by default |
| Static Factors | Stable attributes such as identity, role and device type |
| Dynamic Factors | Runtime attributes such as location, time and posture |
| Entitled to Access | The resource set a subject may reach under policy |
| Trust Score | Continuous measure of current trustworthiness |
| Risk Score | Impact if the access goes wrong |
| Authorization for Access | The allow/deny/constrain decision |
| Inventory | Inventory of identities, assets and applications |
| Policy Engine | Evaluates policy and produces decisions |
| Trust Engine | Aggregates factors into a trust score |
| Endpoint Device | The device from which access originates |
| Policy Enforcement Point (PEP) | Enforces the access decision |
| Feedback Loop | Telemetry that continuously updates trust and policy |
| Confidentiality | Data seen only by authorized parties |
| Integrity | Data changed only by authorized parties |
| Availability | Authorized use possible when needed |
| HIPAA | US health information privacy and security act |
| PCI DSS | Payment card industry data security standard |
| GDPR | EU general data protection regulation |
| Data Sovereignty | Data governed by the law of the country where it is collected |
| Security Domain | A region of the network with a common trust level |
| Zone | A security subdivision inside a domain |
| Chokepoint | A controlled point through which inter-domain traffic passes |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| Zero Trust Architecture (ZTA) | 零信任架构 |
| Static Factors | 静态因素 |
| Dynamic Factors | 动态因素 |
| Entitled to Access | 有权访问 |
| Trust Score | 信任分数 |
| Risk Score | 风险分数 |
| Authorization for Access | 访问授权 |
| Inventory | 清单 |
| Policy Engine | 策略引擎 |
| Trust Engine | 信任引擎 |
| Endpoint Device | 终端设备 |
| Policy Enforcement Point (PEP) | 策略执行点 |
| Feedback Loop | 反馈循环 |
| Confidentiality | 机密性 |
| Integrity | 完整性 |
| Availability | 可用性 |
| HIPAA | 美国健康保险流通与责任法案 |
| PCI DSS | 支付卡行业数据安全标准 |
| GDPR | 通用数据保护条例 |
| Data Sovereignty | 数据主权 |
| Security Domain | 安全域 |
| Zone | 区域 |
| Chokepoint | 检查点 |

</div>

---

## Chapter Summary · 本章小结

Chapter 4 is the **constraints chapter** of the book: it offers no technology, only the boundaries that the other 17 chapters must respect.

<div class="zh" markdown="1">

第 4 章是全书的**约束章**：它不给技术，给的是"其他 17 章都必须遵守的边界"。

</div>

```
Security policy (four sources: law / contract / internal policy / architecture principle)
    ↓ translated into control objectives
Security domains + chokepoints (trust level defines domains; inter-domain traffic converges on a few points)
    ↓ zero trust fills in "the inside is not trustworthy either"
Identity + device + context → trust score → authorization (ZTNA replaces network-level access)
    ↓ the three goals pull against each other
CIA: encryption vs. inspection, availability vs. confidentiality, integrity vs. emergency response
    ↓ everything must ultimately be provable
Compliance evidence chain: logs + time synchronization + change records + periodic review
```

<div class="zh" markdown="1">

```
安全策略（四类来源：法规 / 合同 / 内部制度 / 架构原则）
    ↓ 翻译成控制目标
安全域 + 检查点（信任等级决定域，域间流量收敛到少数检查点）
    ↓ 用零信任补齐"内部也不可信"
身份 + 设备 + 上下文 → 信任分数 → 授权（ZTNA 取代网络级接入）
    ↓ 三条目标互相拉扯
CIA 三要素：加密 vs 检测、可用性 vs 机密性、完整性 vs 应急
    ↓ 最终都要能被证明
合规证据链：日志 + 时间同步 + 变更记录 + 定期复核
```

</div>

Three sentences that must be taken away:

<div class="zh" markdown="1">

三句必须带走的话：

</div>

| Conclusion | Meaning |
|------------|---------|
| **Security cannot be bolted on afterwards** | It must be design input. Bolting it on only adds appliances; it cannot change identity, segmentation or process |
| **Domains and chokepoints should be "few and explicit", not "many and vague"** | 5–12 domains and a handful of chokepoints are maintainable |
| **Compliance looks at evidence, not configuration** | Configured but unprovable is the same as not configured |

<div class="zh" markdown="1">

| 结论 | 含义 |
|------|------|
| **安全不能事后追加** | 它必须是设计输入。事后追加只能加设备，改不了身份、分段与流程 |
| **域与检查点是"少而明确"，不是"多而模糊"** | 5–12 个域、少数几个检查点，才维护得动 |
| **合规看的是证据，不是配置** | 配了但证明不了，等于没配 |

</div>

> **One-line memory hook**: **the deliverable of security design is "boundaries + paths + evidence", not an appliance list.**

<div class="zh" markdown="1">

> **一句话记忆**：**安全设计的交付物是"边界 + 路径 + 证据"，而不是"设备清单"。**

</div>

This chapter expands into concrete technology in Chapter 10 (hardening, admission control, segmentation, encryption) and becomes a layer of constraint inside concrete architectures in Chapters 15–17 (campus segmentation, edge trust levels, WAN encryption boundaries).

<div class="zh" markdown="1">

本章会在第 10 章展开为具体技术（加固、准入、分段、加密），在第 15–17 章变成具体架构里的一层约束（园区分段、边缘信任等级、WAN 加密边界）。

</div>
