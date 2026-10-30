# Chapter 10: Security · 第 10 章：安全

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapter 10 (pp. 507–541)

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译 | 原书第 507-541 页

</div>

---

## Topics Covered in This Chapter · 本章涵盖主题

- **Device security**: three-plane (management/control/data) hardening, control plane policing, supply chain and image integrity
- **Layer 2 security**: reconstructing Layer 2 attack chains, the three 802.1X modes, MACsec, private VLAN
- **Layer 3 security**: routing protocol authentication and key rotation, infrastructure ACLs, the three uRPF modes, RTBH
- **Network coverage and remote access**: IPsec parameter selection, DMVPN/FlexVPN/GET VPN, split tunneling, ZTNA/SASE

<div class="zh" markdown="1">

- **设备安全**：三平面（管理/控制/数据）加固、控制平面监管、供应链与镜像完整性
- **二层安全**：二层攻击链还原、802.1X 三种模式、MACsec、Private VLAN
- **三层安全**：路由协议认证与密钥轮换、基础设施 ACL、uRPF 三模式、RTBH
- **网络覆盖与远程访问**：IPsec 全参数选型、DMVPN/FlexVPN/GET VPN、分离隧道、ZTNA/SASE

</div>

---

## Chapter Introduction: Four Counter-Intuitive Truths About Security Design · 本章导读：安全设计的四条反直觉认知

![The four counter-intuitive truths about security design, each with the belief it replaces](assets/fig/en10-01-four-truths.svg)


### Counter-Intuitive Truth #1: Security Is Not a "Zone", It Is a "Relationship Chain" · 反直觉一：安全不是一个"域"，是一条"关系链"

![A secure zone is the wrong diagram; the trust boundary inventory is the right artifact](assets/fig/en10-02-trust-boundary.svg)


Beginners draw security architectures by drawing a big box labeled "secure zone" and wrapping it around the core switch. That is wrong. **Security exists only at the point where "two entities with different trust levels interact"** — it is inherently **an edge**, not a **surface**.

<div class="zh" markdown="1">

初学者画安全架构，习惯画一个大方框写"安全区"，然后把它套在核心交换机上。这是错的。**安全只在"两个不同信任级别的实体发生交互"的那个点上存在**，它天然是**一条边**，不是一个**面**。

</div>

So the first step in security design is not choosing equipment, it is **listing every flow that crosses a trust boundary**:

<div class="zh" markdown="1">

所以安全设计的第一步不是选设备，是**列出所有跨越信任边界的流量**：

</div>

| Cross-boundary relationship | Change in trust level | What is needed |
|-----------|------------|---------|
| Employee endpoint → internal server | Low → High | Authentication + authorization + inspection |
| Branch → Headquarters | Low → High | Encrypted tunnel + policy |
| Operations staff → network devices | Medium → Highest | Bastion host + two-factor + audit |
| DMZ → internal network | Lowest → High | **One-way**, default deny |
| Partner → specific service | External → internal subset | One-way extranet + least privilege |
| Production network ← office network | High ← Low | Physical/logical isolation, no lateral movement |

<div class="zh" markdown="1">

| 跨边界关系 | 信任级别变化 | 需要什么 |
|-----------|------------|---------|
| 员工终端 → 内网服务器 | 低 → 高 | 认证 + 授权 + 检查 |
| 分支 → 总部 | 低 → 高 | 加密隧道 + 策略 |
| 运维人员 → 网络设备 | 中 → 最高 | 堡垒机 + 双因素 + 审计 |
| DMZ → 内网 | 最低 → 高 | **单向**、默认拒绝 |
| 合作伙伴 → 特定服务 | 外部 → 内部局部 | Extranet 单向 + 最小权限 |
| 生产网 ← 办公网 | 高 ← 低 | 物理/逻辑隔离，禁止横向 |

</div>

**Keep this one sentence from a design perspective**: if a security design has no "trust boundary inventory", it is most likely a collage of product brochures.

<div class="zh" markdown="1">

**设计视角记住这一句**：如果一份安全设计里找不到"信任边界清单"，那它大概率是一堆设备的产品手册拼贴。

</div>

### Counter-Intuitive Truth #2: Encryption Only Solves "Cannot See", Not "Cannot Get In" · 反直觉二：加密只解决"看不见"，不解决"进不来"

![A fully meshed IPsec network still lets one compromised PC reach every site](assets/fig/en10-03-encryption-blindspot.svg)


Many people treat a VPN as a security solution. A VPN does only two things: **confidentiality** (a man in the middle cannot see the content) and **authentication** (confirming who the peer is). It does **not** do:

<div class="zh" markdown="1">

很多人把 VPN 当成安全方案。VPN 只做两件事：**保密性**（中间人看不见内容）和**身份验证**（确认对端是谁）。它**不**做：

</div>

- Authorization (which servers this user may access)
- Threat inspection (whether the file they sent contains a Trojan)
- Lateral movement prevention (whether they can jump to another segment after getting in)

<div class="zh" markdown="1">

- 授权（这个用户能访问哪些服务器）
- 威胁检查（他传过来的文件有没有木马）
- 横向移动阻断（他进来以后能不能跳到别的网段）

</div>

**That is the fundamental reason "encrypted tunnel ≠ security architecture"**. In an enterprise that fully interconnects every branch with IPsec, if one PC inside a branch is compromised, the attacker can still use those encrypted tunnels to move laterally across the whole network — and it is even harder for you to notice, because all traffic looks like legitimate encrypted sessions.

<div class="zh" markdown="1">

**这就是"加密隧道 ≠ 安全架构"的根本原因**。一个把所有分支用 IPsec 全互连的企业，如果分支里有一台被入侵的 PC，攻击者照样可以借助这些加密隧道横向移动到全网 —— 你甚至更难发现，因为流量看起来都是合法的加密会话。

</div>

### Counter-Intuitive Truth #3: The Cost of Security Is Not in "Buying", It Is in "Changing Processes" · 反直觉三：安全的成本不在"买",在"改流程"

![Where the effort really goes in a security project, and the five questions that make default deny operable](assets/fig/en10-04-process-cost.svg)


In an 802.1X project, procurement and configuration take about 30% of the effort; the other 70% goes into: **what to do about this printer that does not support 802.1X, what to do when the medical device vendor refuses to cooperate, how visitors get on, how to fall back when the authentication server dies, and who is on duty when things break**.

<div class="zh" markdown="1">

一个 802.1X 项目，设备采购和配置大概占 30% 的精力；剩下 70% 花在：**这台打印机不支持 802.1X 怎么办、医疗设备厂商拒绝配合怎么办、访客怎么走、认证服务器挂了怎么降级、出问题谁值班**。

</div>

That 70% is what CCDE tests. However elegant the technical design, **without a fallback path, an exception process, and a clear operational owner**, it will be rolled back in its entirety on day one because of one old device.

<div class="zh" markdown="1">

CCDE 考的就是这 70%。技术方案再漂亮，**没有降级路径、没有例外流程、没有运维归属**，上线当天就会因为一台老设备被整体回退。

</div>

### Counter-Intuitive Truth #4: Default Deny Is Easy to Say; the Hard Part Is "Who Owns the Whitelist" · 反直觉四：默认拒绝容易说，难在"谁负责加白名单"

![Default deny is a one-line rule; the whitelist behind it is a permanent operating cost with four questions and three failure modes](assets/fig/en10-05-whitelist-ownership.svg)


"Default deny" is the starting principle of every security design. But implementation runs into an organizational problem: **when a new business goes live, who submits the policy request? Who approves it? How long until it takes effect?**

<div class="zh" markdown="1">

"默认拒绝"（Default Deny）是所有安全设计的起点原则。但实施时会撞上一个组织问题：**新业务上线时，谁来提策略申请？谁来审批？多久生效？**

</div>

| Governance model | How it looks | Consequence |
|---------|------|------|
| **No process** | Anyone can change the firewall | A few thousand rules within six months; nobody dares delete any; default deny exists in name only |
| **Centralized approval (security team)** | Every change needs a ticket, 2–5 days | Business complains that "network slows down delivery", then starts going around it (4G dongles, public cloud drives) |
| **Self-service plus automation** (recommended) | Policy templated, business self-serves, machine approval plus human sampling | Requires upfront investment in policy orchestration |

<div class="zh" markdown="1">

| 治理模式 | 表现 | 后果 |
|---------|------|------|
| **无流程** | 谁都能改防火墙 | 半年后规则几千条，没人敢删，默认拒绝形同虚设 |
| **集中审批（安全团队）** | 变更要走工单，2~5 天 | 业务抱怨"网络拖慢上线"，于是开始偷偷绕（走 4G、走公网云盘） |
| **自助 + 自动化**（推荐） | 策略模板化，业务自助申请，机器审批+人工抽检 | 需要前期投入建设策略编排 |

</div>

> ⚠️ **The most common failure mode**: the security team treats "default deny" as a technical configuration and never builds the accompanying **policy lifecycle management**. Three years later the rule set has grown beyond auditability, and a penetration test finds that "a temporary any-any rule opened for testing in 2019" is still in effect.

<div class="zh" markdown="1">

> ⚠️ **最常见的失败模式**：安全团队把"默认拒绝"当成技术配置，没建设配套的**策略生命周期管理**。三年后规则膨胀到无法审计，一次渗透测试发现"某条 2019 年为测试临时开通的 any-any 规则"一直在生效。

</div>

---

## Security Design Methodology · 安全设计方法论

### The Four-Step Method: From Assets to Technology · 四步法：从资产到技术

![The four-step security method from assets to technology, and the asset classification ladder that sets the budget](assets/fig/en10-06-four-step-method.svg)


```
① Asset identification → ② Threat modeling → ③ Trust boundaries and segmentation → ④ Technology selection and validation
```

<div class="zh" markdown="1">

```
① 资产识别 → ② 威胁建模 → ③ 信任边界与分段 → ④ 技术选型与验证
```

</div>

| Step | Core question | Deliverable | Consequence of skipping it |
|------|---------|--------|------------|
| **① Asset identification** | What data/systems are valuable? How valuable? How bad is it if they fail? | Asset inventory + classification (public/internal/confidential/core) | The most expensive controls protect things that do not matter, while core assets sit exposed |
| **② Threat modeling** | Who would attack? What is their motive? Where do they come in? | Threat list + attack path diagram | Only "external hackers" are defended against; "insiders" and "supply chain" are missed |
| **③ Trust boundaries and segmentation** | What must be kept together? What must be separated? | Zone diagram + cross-zone traffic matrix | There is only one "internal network", so lateral movement is unobstructed |
| **④ Technology selection and validation** | Which technology implements it? How is effectiveness proven? | Technical design + validation test cases | Equipment purchased but policy wrong, or bypass scenarios never tested at all |

<div class="zh" markdown="1">

| 步骤 | 核心问题 | 输出物 | 常见跳过后果 |
|------|---------|--------|------------|
| **① 资产识别** | 什么数据/系统值钱？值多少？坏了影响多大？ | 资产清单 + 分级（公开/内部/机密/核心） | 给不重要的东西上了最贵的控制，核心资产反而裸露 |
| **② 威胁建模** | 谁会攻击？动机是什么？从哪进来？ | 威胁清单 + 攻击路径图 | 只防"外部黑客"，漏掉"内部人员"和"供应链" |
| **③ 信任边界与分段** | 哪些东西必须放在一起？哪些必须隔开？ | 分区图 + 跨区流量矩阵 | 只有一个"内网"，横向移动畅通无阻 |
| **④ 技术选型与验证** | 用什么技术实现？怎么验证有效？ | 技术方案 + 验证用例 | 买了设备但策略没写对，或根本没测过绕过场景 |

</div>

### Asset Classification: The Yardstick That Decides Investment · 资产分级：决定投入的标尺

| Level | Criteria | Protection requirements | Typical systems |
|------|---------|---------|---------|
| **Core (L1)** | Disclosure or outage causes major financial/compliance/safety loss | Strongest controls + least reachability + full audit + redundancy | Payment systems, patient data, industrial PLCs, CA private keys |
| **Confidential (L2)** | Disclosure causes commercial loss | Encryption + access control + audit | Finance systems, HR, source code repositories |
| **Internal (L3)** | Disclosure has limited impact | Authentication + basic isolation | OA, internal wiki, print services |
| **Public (L4)** | Meant to be seen externally anyway | Availability protection (DDoS) | Corporate website, public APIs |

<div class="zh" markdown="1">

| 级别 | 判定标准 | 保护要求 | 典型系统 |
|------|---------|---------|---------|
| **核心（L1）** | 泄露或中断会造成重大财务/合规/人身损失 | 最强控制 + 最小可达 + 全审计 + 冗余 | 支付系统、患者数据、工控 PLC、CA 私钥 |
| **机密（L2）** | 泄露会造成商业损失 | 加密 + 访问控制 + 审计 | 财务系统、HR、源代码库 |
| **内部（L3）** | 泄露影响有限 | 认证 + 基本隔离 | OA、内部 Wiki、打印服务 |
| **公开（L4）** | 本来就是给外部看的 | 可用性保护（DDoS） | 官网、公开 API |

</div>

**Key insight**: security investment should be allocated **by asset level**, not **evenly by network segment**. A 200-person company that spends 80% of its security budget on "a next-generation firewall for every office" while leaving the industrial network and office network in the same VLAN is a textbook case of misallocated resources.

<div class="zh" markdown="1">

**关键洞察**：安全投入应该**按资产级别分配**，而不是**按网段平均分配**。一个 200 人的企业，把 80% 的安全预算花在"给每个办公室装下一代防火墙"，却让工控网和办公网在同一个 VLAN 里 —— 这是典型的资源错配。

</div>

### Threat Models: STRIDE and the Attack Surface · 威胁模型：STRIDE 与攻击面

![STRIDE applied to network infrastructure, with a concrete example and the control that answers each letter](assets/fig/en10-07-stride.svg)


| Threat type | Meaning | Corresponding network defense |
|---------|------|----------------|
| **S**poofing | Impersonating another identity | 802.1X, IPsec, DHCP snooping, uRPF, routing authentication |
| **T**ampering | Modifying data or configuration | MACsec, IPsec ESP, configuration integrity checks, signed images |
| **R**epudiation | Denying having done something | Centralized logging, NTP synchronization, AAA accounting |
| **I**nformation disclosure | Data being seen | Encryption, private VLAN, disabling unnecessary services, traffic isolation |
| **D**enial of service | Service unavailability | CoPP, QoS, rate limiting, scrubbing centers, redundancy |
| **E**levation of privilege | Gaining privileges one should not have | Least privilege, tiered AAA authorization, management plane isolation |

<div class="zh" markdown="1">

| 威胁类型 | 含义 | 网络侧的对应防御 |
|---------|------|----------------|
| **S**poofing（仿冒） | 冒充他人身份 | 802.1X、IPsec、DHCP Snooping、uRPF、路由认证 |
| **T**ampering（篡改） | 修改数据或配置 | MACsec、IPsec ESP、配置完整性校验、签名镜像 |
| **R**epudiation（抵赖） | 否认做过某事 | 集中日志、NTP 同步、AAA 记账 |
| **I**nformation disclosure（信息泄露） | 数据被看到 | 加密、私有 VLAN、关闭不必要服务、流量隔离 |
| **D**enial of service（拒绝服务） | 服务不可用 | CoPP、QoS、限速、清洗中心、冗余 |
| **E**levation of privilege（提权） | 获得不该有的权限 | 最小权限、AAA 授权分级、管理面隔离 |

</div>

**Three dimensions of attack surface inventory**:

<div class="zh" markdown="1">

**攻击面盘点的三个维度**：

</div>

| Dimension | Question to ask | Typical blind spot |
|-----------|-----------|---------|
| **Exposure surface** | How many assets have a public IP/port? | Test environments forgotten, operations VPN gateways forgotten, IoT forgotten |
| **Protocol surface** | How many protocols/services are enabled? | CDP/LLDP leaking topology, SNMP default community strings, HTTP services left running |
| **Trust surface** | Which relationships are "trusted by default"? | Management network fully open, backup network fully open, monitoring network fully open, cross-domain trust everywhere |

<div class="zh" markdown="1">

| 维度 | 要问的问题 | 典型盲区 |
|------|-----------|---------|
| **暴露面** | 有多少资产在公网上有 IP / 端口？ | 忘了测试环境、忘了运维 VPN 网关、忘了 IoT |
| **协议面** | 开了多少协议/服务？ | CDP/LLDP 泄露拓扑、SNMP 默认团体字、未关的 HTTP 服务 |
| **信任面** | 有哪些"默认信任"的关系？ | 管理网全通、备份网全通、监控网全通、跨域信任泛滥 |

</div>

### The SAFE Architecture Model · SAFE 架构模型

![The SAFE model as a placement grid: network places against the three planes, with the control each cell actually needs](assets/fig/en10-08-safe-model.svg)


SAFE is Cisco's security architecture reference model. Its value is not "copy it", but that it provides a **vocabulary of zones** so that discussions share common terms.

<div class="zh" markdown="1">

SAFE 是 Cisco 的安全架构参考模型。它的价值不是"照抄"，而是提供一套**分区语言**，让讨论有共同词汇。

</div>

| Module | Role | Core controls |
|------|------|---------|
| **Management module** | Carries out-of-band management of all devices | Dedicated VRF/OOB, bastion host, two-factor, strict ACLs |
| **Edge module** | Internet boundary | Firewall, IPS, DDoS protection, NAT |
| **Core module** | High-speed forwarding, no complex policy | Keep it as simple as possible; do not put security policy here |
| **Data center module** | Hosts servers and services | Micro-segmentation, ADC, WAF, east-west firewall |
| **Branch module** | Remote sites | Local egress, local security services, SD-WAN security |
| **Campus module** | User access | 802.1X, segmentation, wireless security |
| **WAN module** | Site interconnection | Encryption, routing security, path isolation |
| **Cloud module** | Public/hybrid cloud | Cloud-native security groups, CASB, SASE access |

<div class="zh" markdown="1">

| 模块 | 定位 | 核心控制 |
|------|------|---------|
| **管理模块 (Management)** | 承载所有设备的带外管理 | 独立 VRF/OOB、堡垒机、双因素、严格 ACL |
| **边缘模块 (Edge)** | Internet 边界 | 防火墙、IPS、DDoS 防护、NAT |
| **核心模块 (Core)** | 高速转发，不做复杂策略 | 尽量简单，安全策略不放在这里 |
| **数据中心模块 (Data Center)** | 承载服务器与业务 | 微分段、ADC、WAF、东西向防火墙 |
| **分支模块 (Branch)** | 远程站点 | 本地出口、本地安全服务、SD-WAN 安全 |
| **园区模块 (Campus)** | 用户接入 | 802.1X、分段、无线安全 |
| **WAN 模块** | 站点互联 | 加密、路由安全、路径隔离 |
| **云模块 (Cloud)** | 公有云/混合云 | 云原生安全组、CASB、SASE 接入 |

</div>

**Three design constraints you must remember**:

<div class="zh" markdown="1">

**三个必须记住的设计约束**：

</div>

1. **The management module must be able to survive independently**: the management network must not depend on the network it manages. When the managed network is down you still have to be able to get in and fix it — that is exactly why OOB management is worth more than "a management VLAN inside the production network".
2. **The core module carries no policy**: the core is about forwarding capacity and stability, and nothing requiring per-packet inspection should be pushed onto it. Inserting a firewall in the middle of the core makes core availability equal to firewall availability.
3. **Within a module there is no mutual inspection by default**: the price of modularity is that "lateral traffic inside a module is uncontrolled". Every real project therefore needs **micro-segmentation inside the module** (east-west firewalls in the data center, SGT in the campus).

<div class="zh" markdown="1">

1. **管理模块必须可独立存活**：管理网不能依赖它管理的被管网络。被管网络断了，你还要能上去修 —— 这就是为什么 OOB 管理比"在业务网里开个管理 VLAN"值钱。
2. **核心模块不放策略**：核心追求的是转发能力和稳定性，任何需要逐包检查的东西都不该压在这里。把防火墙插在核心中间，等于让核心的可用性等于防火墙的可用性。
3. **同一模块内默认不互相检查**：模块化的代价是"模块内横向流量不受控"。所以真实项目里都需要在模块内部再做**微分段**（如数据中心内的东西向防火墙、园区内的 SGT）。

</div>

---

## Foundation Topics · 基础内容

### Device Security · 设备安全

#### The Three-Plane Model: The Coordinate System for Hardening · 三平面模型：加固的坐标系

![The three-plane model: what each plane is, how it is attacked, and why management plane loss is total](assets/fig/en10-09-three-planes.svg)


A network device has three independent paths, and security discussions must separate them, because **their threats, attackers, and defenses are completely different**:

<div class="zh" markdown="1">

网络设备自身有三条独立的通路，安全讨论必须分开谈，因为**它们的威胁、攻击者、防护手段完全不同**：

</div>

| Plane | What it carries | Consequence of compromise | Main defenses |
|------|---------|------------|---------|
| **Management plane** | SSH/Telnet, SNMP, NetFlow, Syslog, NTP, TFTP/SCP, AAA | **Highest** — an attacker with device control can change any configuration | Strong authentication, ACLs, OOB, encrypted protocols, disable cleartext services |
| **Control plane** | Routing protocols (OSPF/BGP/IS-IS), STP, ARP, ICMP, LDP/RSVP | High — routing tables can be poisoned so traffic detours or is black-holed | CoPP/CPPr, protocol authentication, TTL security, maximum prefix, prefix filtering |
| **Data plane** | User traffic (transit traffic) | Medium — usually sniffing, spoofing, DoS on shared media | ACLs, uRPF, Layer 2 protections, encryption |

<div class="zh" markdown="1">

| 平面 | 承载什么 | 被攻破的后果 | 主要防护 |
|------|---------|------------|---------|
| **管理平面 (Management Plane)** | SSH/Telnet、SNMP、NetFlow、Syslog、NTP、TFTP/SCP、AAA | **最高** —— 攻击者拿到设备控制权，可以改任何配置 | 强认证、ACL、OOB、加密协议、禁用明文服务 |
| **控制平面 (Control Plane)** | 路由协议（OSPF/BGP/IS-IS）、STP、ARP、ICMP、LDP/RSVP | 高 —— 可以投毒路由表，让流量绕行或黑洞 | CoPP/CPPr、协议认证、TTL 安全、最大前缀、前缀过滤 |
| **数据平面 (Data Plane)** | 用户业务流量（穿越流量） | 中 —— 通常是共享介质上的嗅探、欺骗、DoS | ACL、uRPF、二层防护、加密 |

</div>

**The single most important realization**: **an attack on the data plane can only affect "the traffic passing through it"; an attack on the control plane affects "every service along the entire path"; an attack on the management plane affects "everything about the device itself".**

<div class="zh" markdown="1">

**最重要的一个认知**：**数据平面上的攻击只能影响"经过它的流量"；控制平面上的攻击会影响"整条路径上的所有业务"；管理平面上的攻击会影响"设备本身的一切"。**

</div>

That is why the same "rate limiting" action is worth far more when applied as CoPP (protecting the control plane) than as interface policing.

<div class="zh" markdown="1">

这就是为什么同一个"限速"动作，配在 CoPP（保护控制平面）上的价值，远高于配在接口上的 policing。

</div>

#### Hardening Priorities: P0 / P1 / P2 · 加固优先级：P0 / P1 / P2

![Hardening priorities P0, P1 and P2: what to do first, what it stops, and what to refuse to do at all](assets/fig/en10-10-hardening-p0p1p2.svg)


Device hardening checklists run to hundreds of items, but no project gives you the time to finish them. **Sort by "attacker cost vs your defense cost"** and do the ones that are "easiest for the attacker and worst in consequence" first:

<div class="zh" markdown="1">

设备加固清单动辄上百条，但没有项目会给你做完的时间。**按"攻击者成本 vs 你的防护成本"排序**，优先做那些"攻击者最容易、后果最严重"的：

</div>

| Priority | Measure | Why it ranks this high | Effort |
|--------|------|--------------|--------|
| **P0** | Disable Telnet/HTTP/unused services; keep SSHv2 only | Cleartext protocols are passwords written on the packet; the attack bar is essentially zero | Minutes |
| **P0** | Do not expose management interfaces to the Internet | An exposed management plane gets found and brute-forced by automated tools within hours | Minutes (ACL) |
| **P0** | Strong passwords plus **real encryption** (type 8/9) rather than `service password-encryption` | Type 5 (MD5) can be cracked offline; type 7 is a reversible encoding | Minutes |
| **P0** | Routing protocol authentication (OSPF/BGP/IS-IS) | An unauthenticated BGP session can be forged by anyone; one route hijacks all traffic | Hours |
| **P0** | Disable unused physical ports | An empty port can be plugged into and used to enter a VLAN | Minutes (bulk script) |
| **P1** | Centralized AAA authentication + tiered authorization + accounting | Shared accounts = no accountability = no auditability | Days (depends on the AAA server) |
| **P1** | NTP synchronization (authenticated) | Logs, certificates, and tokens all depend on time | Hours |
| **P1** | CoPP / CPPr | Prevents the control plane from being DoS'd into failure | Days (requires tuning) |
| **P1** | Centralized logging (Syslog → SIEM) | No logs means no security incident response capability | Days |
| **P2** | Image signature verification / Secure Boot | Prevents firmware tampering and supply chain attacks | Depends on platform capability |
| **P2** | Configuration backup and baseline comparison (compliance audit) | Ensures hardening is not rolled back by the next change | Weeks (needs tooling) |

<div class="zh" markdown="1">

| 优先级 | 措施 | 为什么排这么前 | 工作量 |
|--------|------|--------------|--------|
| **P0** | 关闭 Telnet / HTTP / 未使用的服务；只留 SSHv2 | 明文协议等于把密码写在包上；攻击门槛几乎为零 | 分钟级 |
| **P0** | 管理接口不暴露到 Internet | 暴露的管理面会被自动化工具在数小时内扫到并爆破 | 分钟级（ACL） |
| **P0** | 强密码 + 启用 `service password-encryption` 之外的**真加密**（type 8/9） | type 5（MD5）可离线破解，type 7 是可逆编码 | 分钟级 |
| **P0** | 路由协议认证（OSPF/BGP/IS-IS） | 无认证的 BGP 会话可被任意伪造，一条路由就能劫持全站流量 | 小时级 |
| **P0** | 关闭未使用的物理端口 | 空端口插上就能进 VLAN | 分钟级（批量脚本） |
| **P1** | AAA 集中认证 + 分级授权 + 记账 | 共享账号 = 无法追责 = 无法审计 | 天级（依赖 AAA 服务器） |
| **P1** | NTP 同步（认证） | 日志、证书、令牌全部依赖时间 | 小时级 |
| **P1** | CoPP / CPPr | 防止控制平面被 DoS 打瘫 | 天级（要调参） |
| **P1** | 集中日志（Syslog → SIEM） | 没有日志等于没有安全事件响应能力 | 天级 |
| **P2** | 镜像签名验证 / Secure Boot | 防固件篡改与供应链攻击 | 依赖平台能力 |
| **P2** | 配置备份与基线比对（合规审计） | 保证加固不会在下次变更中被回退 | 周级（需工具） |

</div>

> 💡 **A reality check**: finishing all the P0 items is very cheap and blocks the vast majority of automated attacks. In most compromised networks the problem stops right at P0 — an old switch with Telnet enabled and a password of `cisco`, sitting next to a three-tier next-generation firewall, is not a rare combination.

<div class="zh" markdown="1">

> 💡 **现实提醒**：P0 全部做完，成本极低但能挡掉绝大多数自动化攻击。绝大多数被攻破的网络，问题都停在 P0 —— 一台开着 Telnet 且密码是 `cisco` 的老交换机，旁边配了三层下一代防火墙，这个组合并不罕见。

</div>

#### Password Strength: Why Type 5 Is No Longer Safe · 密码强度：为什么 type 5 已经不安全

![Password encoding types compared: which are reversible, which survive an offline attack, and what to use in 2026](assets/fig/en10-11-password-types.svg)


| Type | Algorithm | Reversible? | Actual strength | Recommendation |
|------|------|--------|---------|------|
| **type 0** | Cleartext | Yes | None | Never use |
| **type 4** | SHA-256 (old implementation) | No | Low (unsalted, rainbow tables) | Do not use |
| **type 5** | Salted MD5 hash | No | Low–medium (GPU-crackable at high speed) | Phase out |
| **type 7** | Vigenère variant (reversible encoding) | **Yes** | None | Never use (many people mistake it for encryption) |
| **type 8** | PBKDF2-SHA256 (salted + iterated) | No | High | Recommended |
| **type 9** | scrypt | No | Very high (resistant to GPU/ASIC) | Recommended |

<div class="zh" markdown="1">

| 类型 | 算法 | 可逆？ | 实际强度 | 建议 |
|------|------|--------|---------|------|
| **type 0** | 明文 | 是 | 无 | 绝对不用 |
| **type 4** | SHA-256（旧实现） | 否 | 低（无盐，可彩虹表） | 不用 |
| **type 5** | MD5 加盐哈希 | 否 | 低-中（已可 GPU 高速破解） | 逐步淘汰 |
| **type 7** | Vigenère 变体（可逆编码） | **是** | 无 | 绝对不用（很多人误以为是加密） |
| **type 8** | PBKDF2-SHA256（加盐 + 迭代） | 否 | 高 | 推荐 |
| **type 9** | scrypt | 否 | 很高（抗 GPU/ASIC） | 推荐 |

</div>

Configuration example:

<div class="zh" markdown="1">

配置示例：

</div>

```cfg
! Store local passwords with type 9 (scrypt)
username admin privilege 15 algorithm-type scrypt secret <strong-password>
enable algorithm-type scrypt secret <strong-password>

! Disable cleartext services
no ip http server
no ip http secure-server        ! if the Web UI is not used
line vty 0 15
 transport input ssh            ! allow SSH only
 exec-timeout 10 0
 logging synchronous
```

<div class="zh" markdown="1">

```cfg
! 使用 type 9（scrypt）存储本地密码
username admin privilege 15 algorithm-type scrypt secret <强密码>
enable algorithm-type scrypt secret <强密码>

! 关闭明文服务
no ip http server
no ip http secure-server        ! 若不用 Web UI
line vty 0 15
 transport input ssh            ! 只允许 SSH
 exec-timeout 10 0
 logging synchronous
```

</div>

> ⚠️ **Trap**: `service password-encryption` only converts cleartext passwords in the configuration into **type 7**, which is a **reversible encoding** that anyone with the configuration file can restore with a single command. Its only purpose is to prevent shoulder surfing; it is not a security control. The real approach is to **use `secret` rather than `password` from the outset**, and to upgrade to type 8/9.

<div class="zh" markdown="1">

> ⚠️ **陷阱**：`service password-encryption` 只把配置里的明文密码转成 **type 7**，那是**可逆编码**，任何拿到配置文件的人都能一条命令还原。它的唯一作用是"防肩窥"，不是安全控制。真正的做法是**从一开始就用 `secret` 而不是 `password`**，并升级到 type 8/9。

</div>

#### Time Synchronization: The Severely Underrated Security Infrastructure · 时间同步：被严重低估的安全基础设施

![NTP as security infrastructure: six mechanisms that depend on it, and the cascade when it fails](assets/fig/en10-12-ntp-cascade.svg)


NTP looks unrelated to security, but in reality it underpins four things:

<div class="zh" markdown="1">

NTP 看似与安全无关，实际上它支撑了四件事：

</div>

| Security mechanism depending on NTP | Consequence of time skew |
|-------------------|--------------|
| **Certificate validity checks** (HTTPS, IPsec, 802.1X EAP-TLS) | A skew beyond the validity period or into "certificate not yet valid" → **authentication fails outright** |
| **Kerberos authentication** | 5 minutes of skew is tolerated by default; beyond that tickets are rejected → nobody can log in to the domain |
| **Log correlation and forensics** | Devices disagree on time → the attack timeline cannot be reconstructed |
| **TOTP two-factor tokens** | More than 30 seconds of skew → one-time codes are always wrong |
| **IPsec SA lifetime / replay window** | Severe skew can prevent SA establishment or trigger false replay detection |

<div class="zh" markdown="1">

| 依赖 NTP 的安全机制 | 时间偏差的后果 |
|-------------------|--------------|
| **证书有效性校验**（HTTPS、IPsec、802.1X EAP-TLS） | 偏差超过证书有效期或出现"证书尚未生效" → **认证直接失败** |
| **Kerberos 认证** | 默认允许偏差 5 分钟，超过则票据被拒 → 域内无法登录 |
| **日志关联与取证** | 各设备时间不一致 → 无法还原攻击时间线 |
| **TOTP 双因素令牌** | 偏差超过 30 秒 → 动态码始终错误 |
| **IPsec SA 生命周期 / 重放窗口** | 严重偏差可能导致 SA 无法建立或重放误判 |

</div>

> 🔥 **A real incident: NTP drift caused a network-wide VPN outage**
>
> **Symptom**: IPsec VPNs at 40 branches of a group went down one after another within a day, and dropped again 20–40 minutes after the tunnels were restarted. Business between headquarters and the branches was widely interrupted.
>
> **Troubleshooting**: IKE debugging showed `phase 1 failed: certificate validation failed`. The certificate validity periods were fine. Comparing the time at headquarters with the branches revealed that **the branches' NTP server address pointed at an old IP that had been decommissioned long ago**, so the devices fell back to their local clocks and had drifted 40 minutes over a few months.
>
> **Why they failed "one after another"**: there were multiple certificates (headquarters CA, third-party CA), and each branch certificate had different `notBefore/notAfter` values, so failure only triggered when the drift crossed a particular certificate boundary. That is why it looked like "one device at a time", resembling a hardware problem.
>
> **Why "a restart fixed it for a while"**: when renegotiating, if it happened to hit another certificate or fell back to the PSK configuration, it worked temporarily; the next rekey failed again.
>
> **Root cause**: during a data center relocation two years earlier the NTP server IP changed, the configuration template was never updated, and the branch devices used an **unauthenticated NTP client with a single upstream**; when the upstream became unreachable they **silently used the local clock** (the default `ntp server` produces no alarm at all).
>
> **Fix**:
> ```cfg
> ntp authentication-key 1 sha1 <key>
> ntp authenticate
> ntp trusted-key 1
> ntp server 10.1.1.10 key 1 prefer
> ntp server 10.1.1.11 key 1
> ntp access-group peer 20
> ! The key part: monitoring
> ! Collect "clock offset" and "NTP stratum"; alarm when offset > 1 s and when stratum is 16 (unreachable)
> ```
>
> **Three design lessons**:
> 1. **NTP needs at least two upstreams, and they must cross different network paths** (two addresses on the same core switch do not count).
> 2. **NTP authentication is mandatory**, otherwise NTP itself is a protocol that can be poisoned (a forged NTP response can jump the device clock anywhere, invalidating every certificate).
> 3. **NTP offset must be monitored** — this is a "silent failure", and without monitoring you only discover it when business breaks.

<div class="zh" markdown="1">

> 🔥 **真实故障案例：NTP 漂移导致全网 VPN 中断**
>
> **现象**：某集团 40 个分支的 IPsec VPN 在一天内陆续断开，重启隧道后 20~40 分钟又断。总部与分支之间的业务大面积中断。
>
> **排查**：IKE 调试显示 `phase 1 failed: certificate validation failed`。检查证书有效期正常。对比总部与分支的时间，发现**分支的 NTP 服务器地址指向了一个早已下线的旧 IP**，设备退回到本地时钟，几个月累积漂移了 40 分钟。
>
> **为什么"陆续"断**：证书有多个（总部 CA、第三方 CA），各分支证书的 `notBefore/notAfter` 不同，漂移量跨过某个证书边界时才触发失败。所以现象是"一台一台断"，看起来像硬件问题。
>
> **为什么"重启能好一会"**：重新协商时若命中了另一个证书或走 PSK 的回退配置，暂时能通；等下次 rekey 又失败。
>
> **根因**：两年前一次机房迁移，NTP 服务器换了 IP，配置模板未更新，且分支设备用的是**不带认证的 NTP 客户端 + 单一上游**，上游不可达时**静默使用本地时钟**（默认 `ntp server` 无任何告警）。
>
> **修复**：
> ```cfg
> ntp authentication-key 1 sha1 <密钥>
> ntp authenticate
> ntp trusted-key 1
> ntp server 10.1.1.10 key 1 prefer
> ntp server 10.1.1.11 key 1
> ntp access-group peer 20
> ! 关键：加监控
> ! 采集 "clock offset" 与 "NTP stratum"，偏差 > 1 秒告警，stratum 16（不可达）告警
> ```
>
> **设计层面的三条教训**：
> 1. **NTP 至少两个上游，且要跨不同的网络路径**（同一台核心上的两个地址不算）
> 2. **必须开 NTP 认证**，否则 NTP 本身就是一个可被投毒的协议（伪造 NTP 响应可让设备时间任意跳变，进而让所有证书失效）
> 3. **NTP 偏移量必须进监控** —— 这是"沉默故障"，没有监控就只能在业务故障时才发现

</div>

#### AAA: Authentication, Authorization, Accounting · AAA：认证、授权、记账

![AAA for network devices: the flow, TACACS+ against RADIUS, and the three anti-patterns that undo both](assets/fig/en10-13-aaa.svg)


| Component | Function | Key design questions |
|------|------|------------|
| **Authentication** | Who you are | Local accounts or centralized? Two-factor? What is the fallback policy? |
| **Authorization** | What you may do | Tiered by role (read-only/operations/admin)? Command-level authorization? |
| **Accounting** | What you did | Which commands are recorded? How long are they kept? Who reviews them? |

<div class="zh" markdown="1">

| 组件 | 作用 | 关键设计问题 |
|------|------|------------|
| **Authentication（认证）** | 你是谁 | 本地账号还是集中？双因素？fallback 策略？ |
| **Authorization（授权）** | 你能做什么 | 按角色分级（只读/运维/管理员）？命令级授权？ |
| **Accounting（记账）** | 你做了什么 | 记录什么命令？保留多久？谁看？ |

</div>

**TACACS+ vs RADIUS**:

<div class="zh" markdown="1">

**TACACS+ vs RADIUS**：

</div>

| Dimension | TACACS+ | RADIUS |
|------|---------|--------|
| Transport | TCP 49 | UDP 1812/1813 |
| Encryption scope | **The entire packet body** | The password field only |
| Authorization granularity | **Command-level and parameter-level** | Essentially only "permit/deny" |
| Vendor support | Cisco-native; the de facto standard for network devices | Universal; widely supported by wireless/VPN/servers |
| Best fit | **Device administration (network admin)** | **User access (802.1X, VPN users)** |

<div class="zh" markdown="1">

| 维度 | TACACS+ | RADIUS |
|------|---------|--------|
| 传输 | TCP 49 | UDP 1812/1813 |
| 加密范围 | **整个报文体** | 仅密码字段 |
| 授权粒度 | **支持命令级、参数级** | 基本只支持"通过/拒绝" |
| 厂商支持 | Cisco 原生，网络设备事实标准 | 通用，无线/VPN/服务器广泛支持 |
| 适用 | **设备管理（network admin）** | **用户接入（802.1X、VPN 用户）** |

</div>

**Design recommendations**:

<div class="zh" markdown="1">

**设计建议**：

</div>

- Network device administration → **TACACS+** (command-level authorization is required)
- User access authentication → **RADIUS** (EAP and accounting attributes are required)
- When both coexist, use the same identity source (AD/LDAP) but keep the policies separate

<div class="zh" markdown="1">

- 网络设备管理 → **TACACS+**（需要命令级授权）
- 用户接入认证 → **RADIUS**（需要 EAP、计费属性）
- 两者共存时，用同一套身份源（AD/LDAP），但策略分开

</div>

> ⚠️ **The most dangerous AAA configuration**: `aaa authentication login default group tacacs+ local` followed by a **shared local administrator account**. As soon as the AAA server goes down (or is DoS'd by an attacker), every device falls back to the same local account, and once that account leaks the whole network falls. The correct approach: local accounts are for emergency recovery only, their passwords are vaulted and rotated, and **local authorization does not grant full privilege-15 rights**.

<div class="zh" markdown="1">

> ⚠️ **最危险的 AAA 配置**：`aaa authentication login default group tacacs+ local` 后面配了一个**共享的本地管理员账号**。AAA 服务器一挂（或被攻击者 DoS），所有设备退回到同一个本地账号，这个账号一旦泄露就是全网沦陷。正确做法：本地账号只用于紧急恢复，密码由密码管理系统托管并定期更换，且**本地授权不给 privilege 15 的完整权限**。

</div>

#### Supply Chain and Image Integrity · 供应链与镜像完整性

![The device lifecycle as an attack surface: procurement, image, boot and configuration, with the check that closes each gap](assets/fig/en10-14-supply-chain.svg)


This item is rarely mentioned in traditional network design, but it keeps recurring in recent real-world incidents:

<div class="zh" markdown="1">

这一项在传统网络设计里很少提，但在近年的真实事件中反复出现：

</div>

| Threat | How it appears | Protection |
|------|------|------|
| **Counterfeit devices** | Refurbished or cloned devices bought from secondary/grey channels with backdoored firmware | Authorized channels only; verify serial numbers; check SUDI/micro-electronic identity |
| **Replaced images** | IOS images downloaded from unofficial sources containing backdoors | Download only from official sources; **verify image hashes and digital signatures** |
| **Firmware downgrade attacks** | An attacker downgrades the device to a version with known vulnerabilities | Enable **Secure Boot**, prohibit downgrades, maintain a version baseline |
| **Configuration backdoors** | Factory-preset hidden accounts or debug services | Baseline hardening plus configuration comparison on day one |

<div class="zh" markdown="1">

| 威胁 | 表现 | 防护 |
|------|------|------|
| **伪造设备** | 二手市场/灰色渠道买到翻新或仿冒设备，固件已被植入后门 | 只走授权渠道、验证序列号、检查 SUDI/微电子标识 |
| **镜像被替换** | 从非官方源下载 IOS 镜像，含后门 | 只从官方源下载、**校验镜像的哈希与数字签名** |
| **固件降级攻击** | 攻击者把设备降级到存在已知漏洞的版本 | 开启 **Secure Boot**、禁止降级、配置版本基线 |
| **配置后门** | 出厂预置的隐藏账号、调试服务 | 上架即做基线加固 + 配置比对 |

</div>

```cfg
! Enable image integrity verification (where the platform supports it)
verify /md5 flash:image.bin <known-official-hash>
! Enable Secure Boot (blocks booting unsigned images)
! The command differs by platform, e.g.:
platform security secure-boot enable
```

<div class="zh" markdown="1">

```cfg
! 开启镜像完整性校验（平台支持时）
verify /md5 flash:image.bin <已知官方哈希>
! 开启 Secure Boot（阻止未签名镜像启动）
! 平台命令不同，如：
platform security secure-boot enable
```

</div>

> 🔥 **Case: "compliance drift" across a device fleet**
>
> A retail enterprise had 1,800 store switches. The security team produced a complete hardening baseline (Telnet off, strong passwords, SSH only, unused ports disabled). One year later a compliance audit sampled 50 devices: **31 failed the baseline**.
>
> **The root cause was not that someone deliberately reverted them**:
> - When a store device was replaced, the spares in the depot were **factory default**, and the installer only followed a paper procedure of "make it work" — nobody ran the baseline script
> - The configuration template existed in three versions from three different periods, and legacy store configurations were never upgraded
> - There was no configuration backup, so nobody could compare "where the current state differs from the baseline"
>
> **The fix (this is what real "device hardening" means)**:
> 1. **Version the configuration templates** (Git management plus change review)
> 2. **Automate hardening at deployment** (ZTP + template push; humans cannot skip it)
> 3. **Automated daily baseline comparison with drift alerts** (the only way to stop drift)
> 4. **Pre-configure depot spares** and do not allow "bare metal" onto a site
>
> **Lesson**: hardening is not a one-off project, it is a **continuously verified pipeline**. Without a "detect deviation" mechanism, any baseline degrades into a formality within 12 months.

<div class="zh" markdown="1">

> 🔥 **案例：批量设备的"合规漂移"**
>
> 一家零售企业有 1,800 台门店交换机。安全团队做了完整的加固基线（关 Telnet、强密码、SSH only、关闭未用端口）。一年后合规审计抽检 50 台，**31 台不满足基线**。
>
> **根因不是有人故意改回去**，而是：
> - 门店故障更换设备时，备件库的设备是**出厂配置**，装机人员只按照"能通就行"的纸质流程配置，没人跑基线脚本
> - 配置模板在三个不同时期有过三个版本，老门店的存量配置从未升级
> - 没有配置备份，无法比对"现在跟基线差在哪"
>
> **修复**（这才是真正的"设备加固"）：
> 1. **配置模板版本化**（Git 管理 + 变更评审）
> 2. **上线即自动化加固**（零接触部署 ZTP + 模板下发，人不能跳过）
> 3. **每日自动基线比对**，差异告警（这是唯一能防住漂移的手段）
> 4. **备件库设备预配置**，不允许"裸机"进入现场
>
> **教训**：加固不是一次性的项目，是一条**持续校验的流水线**。没有"检测偏离"的机制，任何基线都会在 12 个月内衰减到形同虚设。

</div>

#### Management Plane Security · 管理平面安全

![Four management architectures in order of resilience, and the access chain that sits on top of whichever one you choose](assets/fig/en10-15-mgmt-plane-ladder.svg)


The core design question for the management plane is: **how far does an attacker have to go before touching the management path?**

<div class="zh" markdown="1">

管理平面的核心设计问题是：**攻击者要走到多远才能碰到管理通路？**

</div>

| Architecture | Topology | Security | Cost | Fit |
|------|------|--------|------|------|
| **In-band management** | Management traffic uses production interfaces and shares links with business traffic | **Low** | Lowest | Small networks, temporary environments |
| **Management VLAN** | A separate VLAN, but on the same physical link | Medium (depends on VLAN isolation quality) | Low | Small and medium campuses |
| **Management VRF** | A separate routing table with interfaces assigned to a VRF | Medium–high (routing domain isolation) | Medium | Medium enterprises |
| **Out-of-band management (OOB)** | Separate physical network + separate devices + separate links | **Highest** | High (needs separate switches, dedicated lines, terminal servers) | Large enterprises, finance, industrial |

<div class="zh" markdown="1">

| 架构 | 拓扑 | 安全性 | 成本 | 适用 |
|------|------|--------|------|------|
| **带内管理 (In-Band)** | 管理流量走业务接口，与业务共用链路 | **低** | 最低 | 小型网络、临时环境 |
| **管理 VLAN** | 独立 VLAN，但在同一物理链路上 | 中（依赖 VLAN 隔离质量） | 低 | 中小型园区 |
| **管理 VRF** | 独立路由表，接口划分到 VRF | 中-高（路由域隔离） | 中 | 中型企业 |
| **带外管理 (OOB)** | 独立物理网络 + 独立设备 + 独立链路 | **最高** | 高（需独立交换机、专线、终端服务器） | 大型企业、金融、工业 |

</div>

**The key judgment**: if the failure scenario is "the production network is down and you need to get in and fix it", then **in-band management fails at exactly that moment**. That is the value of OOB — it is not "more secure", it is **"still available when production has failed"**.

<div class="zh" markdown="1">

**关键判断**：如果故障场景是"业务网瘫痪，你需要进去修"，那么**带内管理在那一刻同时失效**。这就是 OOB 的价值 —— 它不是"更安全"，而是**"在业务故障时仍然可用"**。

</div>

**Layered protection of the management plane**:

<div class="zh" markdown="1">

**管理平面的分层防护**：

</div>

```cfg
! Layer 1: management interfaces are internal-only and ACL-protected
interface GigabitEthernet0/0
 description MGMT-OOB
 vrf forwarding MGMT
 ip address 10.255.0.11 255.255.255.0
 no ip redirects
 no ip proxy-arp
 ip access-group MGMT-IN in

! Layer 2: allow only the bastion host and the monitoring system
ip access-list extended MGMT-IN
 permit tcp 10.255.1.0 0.0.0.255 host 10.255.0.11 eq 22
 permit tcp 10.255.1.0 0.0.0.255 host 10.255.0.11 eq 443
 permit udp host 10.255.2.10 host 10.255.0.11 eq 161
 deny   ip any any log

! Layer 3: VTY restrictions + timeout + logging
line vty 0 15
 access-class MGMT-IN in
 transport input ssh
 exec-timeout 10 0
 logging synchronous
 login authentication TACACS
```

<div class="zh" markdown="1">

```cfg
! 第 1 层：管理接口只在内网，且有 ACL
interface GigabitEthernet0/0
 description MGMT-OOB
 vrf forwarding MGMT
 ip address 10.255.0.11 255.255.255.0
 no ip redirects
 no ip proxy-arp
 ip access-group MGMT-IN in

! 第 2 层：只允许堡垒机和监控系统
ip access-list extended MGMT-IN
 permit tcp 10.255.1.0 0.0.0.255 host 10.255.0.11 eq 22
 permit tcp 10.255.1.0 0.0.0.255 host 10.255.0.11 eq 443
 permit udp host 10.255.2.10 host 10.255.0.11 eq 161
 deny   ip any any log

! 第 3 层：VTY 限制 + 超时 + 日志
line vty 0 15
 access-class MGMT-IN in
 transport input ssh
 exec-timeout 10 0
 logging synchronous
 login authentication TACACS
```

</div>

**Why a bastion host (jump host) is mandatory**:

<div class="zh" markdown="1">

**堡垒机（Jump Host）为什么是必需的**：

</div>

| Without a bastion host | With a bastion host |
|---------|---------|
| Operations staff connect directly to hundreds of devices; accounts are scattered | Only the bastion host can reach devices; accounts are centralized |
| Who logged into which device and when is only in each device's local logs | All logins, commands, and screen recordings are centralized on the bastion |
| Offboarding a person means changing passwords on hundreds of devices | Just disable one account on the bastion |
| No command-level approval or blocking of dangerous commands | Can block `no router bgp`, `reload`, and similar |

<div class="zh" markdown="1">

| 无堡垒机 | 有堡垒机 |
|---------|---------|
| 运维人员直连上百台设备，账号分散 | 只有堡垒机能连设备，账号集中 |
| 谁在什么时候登录了哪台设备，日志在各设备本地 | 所有登录、命令、屏幕录像集中在堡垒机 |
| 人员离职要改上百台设备的密码 | 只禁用堡垒机上一个账号 |
| 无法做命令级审批和高危命令拦截 | 可以拦截 `no router bgp`、`reload` 等 |

</div>

> 🔥 **Case: one "temporary" management interface left open**
>
> **Background**: to let an external integrator debug a newly deployed WLC, a manufacturing enterprise opened an `any → public-IP:8443` rule on the egress firewall, with a promise to "close it in two weeks".
>
> **What happened**: the rule was forgotten for 14 months. The WLC's management page had an unpatched vulnerability, was hit by an automated scanner, and the attacker gained WLC administrative access — and from there the RADIUS shared key and SNMP community strings stored on the device. The attacker then used SNMP RW to change the configuration of several switches and planted a `TCL` script as a persistence backdoor.
>
> **Why it went unnoticed**: device logs only went to the local buffer (4 KB by default, rolling), with no centralized logging, and the SNMP configuration changes raised no alerts.
>
> **The fundamental problems exposed (more memorable than the vulnerability itself)**:
> 1. **Temporary rules had no expiry mechanism** — the firewall has no "rule validity" field, so it relies on human memory
> 2. **The management plane was exposed to the Internet** — debugging should have gone through a bastion/VPN jump host, not an open port
> 3. **Credential management had failed** — the RADIUS shared key was identical network-wide and had never been rotated, so one leak broke everything
> 4. **No configuration change detection** — SNMP RW should be disabled in production (`no snmp-server community <x> RW`)
> 5. **Local-only logging** — no forensics, no way to determine the blast radius
>
> **The right approach at the design level**:
>
> | Requirement | Wrong approach | Right approach |
> |------|---------|---------|
> | External vendor debugging | Open a port on the egress | **A temporary VPN account** (auto-expiring) + bastion + session recording |
> | Remote management | Expose device management ports to the Internet | **Reverse proxy/gateway + strong authentication**; never expose the management plane directly |
> | Temporary policy | Add a rule by hand | Rules carry an **expiry time** (implemented by the automation platform) and are deleted automatically |
> | Configuration change alerts | None | Compare configuration hashes every 5 minutes and alert on any change |
> | SNMP | RW available network-wide | **Read-only + SNMPv3 auth/priv**; RW always disabled |

<div class="zh" markdown="1">

> 🔥 **案例：一台"临时"开放的管理接口**
>
> **背景**：某制造企业为让外部集成商调试新上线的 WLC，在网络出口防火墙上开了一条 `any → 公网IP:8443` 的规则，说好"两周后关闭"。
>
> **发生了什么**：这条规则被遗忘了 14 个月。WLC 的管理页面存在一个未修补的漏洞，被自动化扫描器命中，攻击者获得 WLC 管理权限，进而拿到了设备上保存的 RADIUS 共享密钥和 SNMP 团体字；接着通过 SNMP RW 修改了多台交换机的配置，植入了 `TCL` 脚本作为持久化后门。
>
> **为什么没被发现**：设备日志只发到本地缓冲区（默认 4KB，滚动覆盖），没有集中日志；SNMP 的配置变更没有任何告警。
>
> **暴露的根本问题**（比漏洞本身更值得记）：
> 1. **临时规则没有到期机制** —— 防火墙没有"规则有效期"字段，靠人记
> 2. **管理面被暴露到公网** —— 调试本应通过堡垒机/VPN 跳板，而不是直接开端口
> 3. **凭据管理失效** —— RADIUS 共享密钥全网统一且从未轮换，一处泄露全网失效
> 4. **缺少配置变更检测** —— SNMP RW 应该在生产中禁用（`no snmp-server community <x> RW`）
> 5. **日志本地化** —— 无法取证，无法追溯影响范围
>
> **设计层面的正确做法**：
>
> | 需求 | 错误做法 | 正确做法 |
> |------|---------|---------|
> | 外部厂商调试 | 出口开端口 | 开**临时 VPN 账号**（到期自动失效）+ 堡垒机 + 会话录像 |
> | 远程管理 | 公网暴露设备管理口 | **反向代理/网关 + 强认证**，管理面永不直接暴露 |
> | 临时策略 | 手工加规则 | 规则带**到期时间**（自动化平台实现），到期自动删除 |
> | 配置变更告警 | 无 | 每 5 分钟比对配置哈希，变化即告警 |
> | SNMP | RW 全网可用 | **只读 + SNMPv3 认证加密**，RW 一律关闭 |

</div>

#### Control Plane Security · 控制平面安全

![Four locks on the CPU door: infrastructure ACL, CoPP, control plane protection and GTSM, each asking a different question](assets/fig/en10-17-cpu-door-locks.svg)


The control plane is **the source of every forwarding decision**. Its peculiarity is that **an attacker does not need device privileges — injecting one route or one ARP response is enough to change where traffic goes.**

<div class="zh" markdown="1">

控制平面是**所有转发决策的来源**。它的特殊性在于：**攻击者不需要拿到设备权限，只要能向它注入一条路由或一个 ARP 响应，就能改变流量走向。**

</div>

**Classification of control plane attacks**:

<div class="zh" markdown="1">

**控制平面攻击的分类**：

</div>

| Attack type | Means | Target | Typical consequence |
|---------|------|------|---------|
| **Protocol flooding** | Large volumes of OSPF Hellos / ARP requests / ICMP | Exhaust the CPU and crash protocol processes | Neighbor flapping, route withdrawal, network-wide churn |
| **Route injection** | Forged BGP sessions, unauthenticated OSPF | Change the routing table | **Traffic hijacking / black holing** |
| **Protocol spoofing** | Forged ARP, DHCP, RA (IPv6) | Man in the middle | Data interception/tampering |
| **Topology discovery** | Capture CDP/LLDP/OSPF LSAs | Learn the network structure | Prepares precise follow-on attacks |
| **Protocol vulnerability exploitation** | Exploit a protocol stack implementation flaw | Device control | Full compromise |

<div class="zh" markdown="1">

| 攻击类型 | 手段 | 目标 | 典型后果 |
|---------|------|------|---------|
| **协议洪泛** | 大量 OSPF Hello / ARP 请求 / ICMP | 耗尽 CPU，让协议进程崩溃 | 邻居震荡、路由撤销、全网震荡 |
| **路由注入** | 伪造 BGP 会话、无认证的 OSPF | 改变路由表 | **流量劫持 / 黑洞** |
| **协议欺骗** | 伪造 ARP、DHCP、RA（IPv6） | 中间人 | 数据被窃听/篡改 |
| **拓扑探测** | 抓 CDP/LLDP/OSPF LSA | 获取网络结构 | 为后续精准攻击铺路 |
| **协议漏洞利用** | 利用协议栈实现漏洞 | 设备控制权 | 完全沦陷 |

</div>

##### Protection Mechanism 1: CoPP (Control Plane Policing)

![The CoPP pipeline from the punt path to the CPU, and why a template tuned for steady state breaks at convergence](assets/fig/en10-16-copp-pipeline.svg)


<div class="zh" markdown="1">

##### 保护机制一：CoPP（Control Plane Policing）

</div>

CoPP's idea: **classify and rate-limit "traffic punted to the CPU" at the entry point from the data plane to the control plane**, so that important protocol traffic is not drowned out by junk traffic.

<div class="zh" markdown="1">

CoPP 的思路是：**在数据平面到控制平面的入口处，对"上送 CPU 的流量"做分类限速**，保证重要的协议流量不被垃圾流量淹没。

</div>

```
  data plane ──→ [CoPP policy] ──→ control plane (CPU)
                    │
                    └──→ excess dropped (handled per class)
```

<div class="zh" markdown="1">

```
  数据平面 ──→ [CoPP 策略] ──→ 控制平面 (CPU)
                    │
                    └──→ 超速部分丢弃（按类分别处理）
```

</div>

**The core difficulty of CoPP is not configuration but "how fast to set it"**. This is a classic CCDE exam point:

<div class="zh" markdown="1">

**CoPP 的核心难点不是配置，是"速率定多少"**。这是 CCDE 的典型考点：

</div>

| Traffic class | Typical rate reference | Consequence of setting it too low | Consequence of setting it too high |
|---------|------------|------------|------------|
| **Routing protocols** (OSPF/IS-IS/BGP) | Hundreds of kbps to a few Mbps (depends on neighbor count and route volume) | **Neighbors time out and routes flap** | Protocol floods pass through |
| **Management protocols** (SSH/SNMP/Syslog) | Hundreds of kbps | Operations cannot log in | CPU saturated during brute-force attacks |
| **ICMP** | Low (tens of kbps), but leave headroom for TTL exceeded | `traceroute` breaks, PMTUD black holes | ICMP floods |
| **ARP** | Depends on VLAN size, usually tens to hundreds of kbps | ARP resolution fails, hosts unreachable | ARP broadcast storms |
| **Non-IP / abnormal traffic** | Extremely low, or drop outright | — | Unknown attack surface |

<div class="zh" markdown="1">

| 流量类别 | 典型速率参考 | 定太低的后果 | 定太高的后果 |
|---------|------------|------------|------------|
| **路由协议**（OSPF/IS-IS/BGP） | 数百 kbps ~ 数 Mbps（视邻居数与路由量） | **邻居超时断开，路由震荡** | 允许协议洪泛穿透 |
| **管理协议**（SSH/SNMP/Syslog） | 数百 kbps | 运维登不上设备 | 被爆破时 CPU 被吃满 |
| **ICMP** | 低（几十 kbps），但要给 TTL 超时留余量 | traceroute 失效、PMTUD 黑洞 | ICMP 洪泛 |
| **ARP** | 视 VLAN 规模，通常 数十~数百 kbps | ARP 解析失败，主机不通 | ARP 广播风暴 |
| **非 IP / 异常流量** | 极低或直接丢弃 | — | 未知攻击面 |

</div>

**The right way to design the rates (three steps)**:

<div class="zh" markdown="1">

**速率设计的正确方法（三步）**：

</div>

1. **Measure a baseline**: collect the actual pps/bps of each punted class during normal peak hours (`show policy-map ...` or punt statistics from NetFlow)
2. **Multiply by 2–3× headroom**: account for protocol bursts when neighbors restart (a full BGP table update, OSPF LSA flooding)
3. **Validate under stress**: deliberately trigger routing churn (force a neighbor down/up) and confirm protocols do not time out at 3× load

<div class="zh" markdown="1">

1. **实测基线**：在正常业务高峰下，采集各类上送 CPU 流量的实际 pps/bps（`show policy-map ... ` 或 NetFlow 上送统计）
2. **乘以 2~3 倍余量**：考虑邻居重启时的协议突发（BGP 全表更新、OSPF LSA 泛洪）
3. **压测验证**：故意触发路由震荡（如强制邻居 down/up），确认在 3 倍负载下协议不超时

</div>

```cfg
! Simplified CoPP example (IPv4)
ip access-list extended CPP-ROUTING
 permit ospf any any
 permit tcp any any eq 179
 permit tcp any eq 179 any

ip access-list extended CPP-MGMT
 permit tcp any any eq 22
 permit udp any any eq 161
 permit udp any any eq 514

ip access-list extended CPP-ICMP
 permit icmp any any echo
 permit icmp any any time-exceeded
 permit icmp any any unreachable

ip access-list extended CPP-UNDESIRABLE
 permit udp any any eq 19        ! chargen
 permit tcp any any eq 19
 permit udp any any eq 53        ! DNS to the CPU? usually should not be punted

class-map match-all CM-ROUTING
 match access-group name CPP-ROUTING
class-map match-all CM-MGMT
 match access-group name CPP-MGMT
class-map match-all CM-ICMP
 match access-group name CPP-ICMP
class-map match-all CM-UNDESIRABLE
 match access-group name CPP-UNDESIRABLE

policy-map PM-COPP
 class CM-ROUTING
  police rate 2000000 bps burst 24000 bytes
   conform-action transmit
   exceed-action drop
 class CM-MGMT
  police rate 500000 bps burst 8000 bytes
   conform-action transmit
   exceed-action drop
 class CM-ICMP
  police rate 100000 bps burst 8000 bytes
   conform-action transmit
   exceed-action drop
 class CM-UNDESIRABLE
  police rate 8000 bps
   conform-action drop
   exceed-action drop
 class class-default
  police rate 200000 bps
   conform-action transmit
   exceed-action drop

control-plane
 service-policy input PM-COPP
```

<div class="zh" markdown="1">

```cfg
! CoPP 简化示例（IPv4）
ip access-list extended CPP-ROUTING
 permit ospf any any
 permit tcp any any eq 179
 permit tcp any eq 179 any

ip access-list extended CPP-MGMT
 permit tcp any any eq 22
 permit udp any any eq 161
 permit udp any any eq 514

ip access-list extended CPP-ICMP
 permit icmp any any echo
 permit icmp any any time-exceeded
 permit icmp any any unreachable

ip access-list extended CPP-UNDESIRABLE
 permit udp any any eq 19        ! chargen
 permit tcp any any eq 19
 permit udp any any eq 53        ! 只允许到 CPU 的 DNS? 通常不该上送

class-map match-all CM-ROUTING
 match access-group name CPP-ROUTING
class-map match-all CM-MGMT
 match access-group name CPP-MGMT
class-map match-all CM-ICMP
 match access-group name CPP-ICMP
class-map match-all CM-UNDESIRABLE
 match access-group name CPP-UNDESIRABLE

policy-map PM-COPP
 class CM-ROUTING
  police rate 2000000 bps burst 24000 bytes
   conform-action transmit
   exceed-action drop
 class CM-MGMT
  police rate 500000 bps burst 8000 bytes
   conform-action transmit
   exceed-action drop
 class CM-ICMP
  police rate 100000 bps burst 8000 bytes
   conform-action transmit
   exceed-action drop
 class CM-UNDESIRABLE
  police rate 8000 bps
   conform-action drop
   exceed-action drop
 class class-default
  police rate 200000 bps
   conform-action transmit
   exceed-action drop

control-plane
 service-policy input PM-COPP
```

</div>

> ⚠️ **The critical CoPP detail: how `class-default` is treated**
>
> Many templates configure `class-default` with `police ... exceed-action drop`. That is fine under normal conditions, but if **some legitimate traffic class is not explicitly classified** (a new management protocol, a tunnel keepalive, BFD, LDP), it falls into the default class, gets rate limited, and may be dropped — producing the symptom "some feature mysteriously does not work, but ping is fine".
>
> **The key action when troubleshooting this class of problem**: look at the `exceed` counters on the CoPP policy (`show policy-map control-plane`). If the drop counter of a class is climbing, that is your culprit.
>
> **A safer design**: use `police ... exceed-action transmit` for `class-default` (alert only, no rate limiting) together with monitoring, or set a generous ceiling for `class-default` (e.g. 1–2 Mbps) so that only genuine floods are blocked.

<div class="zh" markdown="1">

> ⚠️ **CoPP 的致命细节：`class-default` 的处置方式**
>
> 很多模板把 `class-default` 配成 `police ... exceed-action drop`。这在正常情况下没问题，但如果**某类合法流量没被显式分类**（比如新的管理协议、某种隧道封装的 keepalive、BFD、LDP），它会落到 default 类里被限速甚至丢弃 —— 于是出现"某个功能莫名其妙不通，但 ping 是通的"。
>
> **排查这类问题的关键动作**：在 CoPP 策略上查看 `exceed` 计数（`show policy-map control-plane`），如果看到某个类的 drop 计数在上涨，就是它。
>
> **更稳妥的设计**：`class-default` 使用 `police ... exceed-action transmit`（只告警不限速），配合监控告警；或者为 `class-default` 设一个宽松的上限（如 1~2 Mbps），只拦真正的洪泛。

</div>

##### Protection Mechanism 2: CPPr (Control Plane Protection)

<div class="zh" markdown="1">

##### 保护机制二：CPPr（Control Plane Protection）

</div>

CoPP is "one entry point, one policy"; CPPr **subdivides it by destination** into three sub-interfaces, each of which can carry its own policy:

<div class="zh" markdown="1">

CoPP 是"一个口进、一个策略"，CPPr 把它**按目的地细分**成三个子接口，可以分别下策略：

</div>

| Sub-interface | What it protects | Traffic carried |
|--------|---------|---------|
| **host** | Traffic destined for the device's own IP | SSH, BGP, SNMP (**needs the strictest limits**) |
| **transit** | Traffic that needs CPU processing but is then forwarded | TTL exceeded, packets needing redirection |
| **CEF-exception** | Abnormal packets that cannot be fast-forwarded by CEF | Fragments, packets needing ARP resolution, IP options |

<div class="zh" markdown="1">

| 子接口 | 保护对象 | 承载流量 |
|--------|---------|---------|
| **host** | 发往设备自身 IP 的流量 | SSH、BGP、SNMP（**最需要严格限速**） |
| **transit** | 需要 CPU 处理但会转发出去的流量 | TTL 超时、需要重定向的包 |
| **CEF-exception** | 无法用 CEF 快速转发的异常包 | 分片、需 ARP 解析、选项字段等 |

</div>

**The value**: when an attacker pounds the CPU with "bulk traffic destined for the device itself", the host sub-interface policy can rate limit precisely without affecting transit processing. With CoPP's single bucket, the two compete with each other.

<div class="zh" markdown="1">

**价值**：攻击者用"大量发往设备本机的流量"打 CPU 时，host 子接口的策略可以精确限速，而不影响 transit 的处理。CoPP 只有一个策略桶时，两者会互相挤占。

</div>

##### Protection Mechanism 3: rACL / iACL (Receive ACL / Infrastructure ACL)

<div class="zh" markdown="1">

##### 保护机制三：rACL / iACL（接收 ACL / 基础设施 ACL）

</div>

An ACL is a "whitelist"; CoPP is "rate limiting". **They are complementary, not substitutes**:

<div class="zh" markdown="1">

ACL 是"白名单"，CoPP 是"限速"。**两者互补，不能替代**：

</div>

| Mechanism | Function | Limitation |
|------|------|------|
| **rACL (Receive ACL)** | Allow only legitimate sources to reach legitimate ports on the device's own IP | Protects only the local device, not transit traffic |
| **iACL (Infrastructure ACL)** | Deployed at the **boundary**, restricting "who can reach the infrastructure address space" | Requires addressing support (infrastructure needs its own address block) |
| **CoPP** | Rate limiting, DoS protection | Does not distinguish "legitimate but voluminous" from "attack" |

<div class="zh" markdown="1">

| 机制 | 作用 | 局限 |
|------|------|------|
| **rACL（Receive ACL）** | 只允许合法源访问设备自身 IP 的合法端口 | 只保护本机，不保护穿越流量 |
| **iACL（Infrastructure ACL）** | 部署在**边界**，限制"谁能访问基础设施地址空间" | 需要地址规划支撑（基础设施要有独立地址段） |
| **CoPP** | 限速，防 DoS | 不区分"合法但量大"与"攻击" |

</div>

**A precondition for iACL (often ignored)**: you must have **separate addressing plans for infrastructure and business**. If device management addresses are mixed into user subnets, you cannot write an ACL that says "only the management network may reach the infrastructure".

<div class="zh" markdown="1">

**iACL 的前提条件（常被忽略）**：必须有**基础设施地址规划和业务地址规划分离**。如果设备管理地址混在用户网段里，你无法写出"只允许管理网访问基础设施"的 ACL。

</div>

```cfg
! iACL example: only the management network and specific business subnets may reach the infrastructure
ip access-list extended iACL
 ! allow the management network to reach device management addresses
 permit ip 10.255.0.0 0.0.255.255 10.0.0.0 0.0.255.255
 ! allow routing protocol neighbors
 permit ospf 10.1.0.0 0.0.255.255 10.1.0.0 0.0.255.255
 permit tcp 10.1.0.0 0.0.255.255 10.1.0.0 0.0.255.255 eq bgp
 ! deny everything else toward the infrastructure address space
 deny   ip any 10.0.0.0 0.0.255.255 log
 permit ip any any
```

<div class="zh" markdown="1">

```cfg
! iACL 示例：只允许管理网和特定业务网段访问基础设施
ip access-list extended iACL
 ! 允许管理网访问设备管理地址
 permit ip 10.255.0.0 0.0.255.255 10.0.0.0 0.0.255.255
 ! 允许路由协议邻居
 permit ospf 10.1.0.0 0.0.255.255 10.1.0.0 0.0.255.255
 permit tcp 10.1.0.0 0.0.255.255 10.1.0.0 0.0.255.255 eq bgp
 ! 拒绝其他所有到基础设施地址空间的流量
 deny   ip any 10.0.0.0 0.0.255.255 log
 permit ip any any
```

</div>

##### Protection Mechanism 4: BGP TTL Security (GTSM, RFC 5082)

<div class="zh" markdown="1">

##### 保护机制四：BGP TTL 安全 (GTSM, RFC 5082)

</div>

**Principle**: BGP neighbors are usually directly connected (one hop). GTSM requires that received BGP packets carry **TTL equal to 255** (or ≥ 254); packets forged by an attacker lose 1 from the TTL on each router they traverse, so they cannot impersonate a directly connected neighbor.

<div class="zh" markdown="1">

**原理**：BGP 邻居通常直连（1 跳）。GTSM 要求收到的 BGP 报文 **TTL 必须等于 255**（或 ≥ 254），而攻击者伪造的报文经过路由器转发后 TTL 会被减 1，因此无法冒充直连邻居。

</div>

```cfg
router bgp 65000
 neighbor 10.1.0.2 remote-as 65001
 neighbor 10.1.0.2 ttl-security hops 1
```

<div class="zh" markdown="1">

```cfg
router bgp 65000
 neighbor 10.1.0.2 remote-as 65001
 neighbor 10.1.0.2 ttl-security hops 1
```

</div>

**Applicability and cost**:

<div class="zh" markdown="1">

**适用范围与代价**：

</div>

| Scenario | Can GTSM be used? | Notes |
|------|-----------|------|
| Directly connected eBGP | ✅ Best | hops 1 |
| Multihop eBGP (e.g. across a firewall) | ✅ But set the hop count correctly | Set it too low and the session will not come up |
| **iBGP to an RR (multihop)** | ⚠️ Use with care | You must know the hop count exactly, and a path change will drop the session |
| Neighbors formed over tunnels | ❌ Usually unusable | Tunneling changes the semantics of TTL |

<div class="zh" markdown="1">

| 场景 | 能否用 GTSM | 说明 |
|------|-----------|------|
| 直连 eBGP | ✅ 最佳 | hops 1 |
| 多跳 eBGP（如跨防火墙） | ✅ 但要设对 hops 数 | 设小了会话起不来 |
| **iBGP 到 RR（多跳）** | ⚠️ 谨慎 | 需要精确知道跳数，且路径变化会导致会话断 |
| 通过隧道建立的邻居 | ❌ 通常不可用 | 隧道封装后 TTL 语义改变 |

</div>

> ⚠️ **A hidden GTSM risk**: `ttl-security hops N` also sets the TTL of sent packets to 255 and requires received packets to have TTL ≥ 255−(N−1). If **the hop count along the path changes** (e.g. the IGP converges onto a longer path), the session **drops immediately**. Multihop scenarios therefore need headroom, and the change process must state "confirm BGP TTL headroom before changing IGP metrics".

<div class="zh" markdown="1">

> ⚠️ **GTSM 的隐性风险**：`ttl-security hops N` 会同时设置发送报文的 TTL 为 255，并要求接收报文 TTL ≥ 255-(N-1)。如果**中间路径的跳数发生变化**（如 IGP 收敛后走了更长的路径），会话会**直接断开**。所以多跳场景必须留余量，且要在变更流程里标注"改 IGP 度量前先确认 BGP TTL 余量"。

</div>

##### Protection Mechanism 5: Routing Protocol Authentication and Key Rotation

![Routing layer protection: authenticated sessions with a key rotation plan, prefix limits, and the policy that stops leakage](assets/fig/en10-18-route-auth-maxprefix.svg)


<div class="zh" markdown="1">

##### 保护机制五：路由协议认证与密钥轮换

</div>

| Protocol | Authentication methods | Strength | Recommendation |
|------|---------|------|------|
| **OSPFv2** | Cleartext / MD5 / **SHA-HMAC** | Cleartext = none | Use SHA-HMAC (`ip ospf authentication message-digest`) |
| **OSPFv3** | IPsec AH/ESP (the protocol itself has no authentication) | Depends on IPsec | Use `authentication ipsec spi ... sha1` |
| **IS-IS** | Cleartext / MD5 / HMAC-SHA | Cleartext = none | Configure per L1/L2/SNP/PDU |
| **BGP** | TCP MD5 / **TCP-AO** | MD5 has known weaknesses | Prefer TCP-AO (RFC 5925); use MD5 on existing devices |
| **EIGRP** | MD5 / HMAC-SHA | — | SHA |

<div class="zh" markdown="1">

| 协议 | 认证方式 | 强度 | 建议 |
|------|---------|------|------|
| **OSPFv2** | 明文 / MD5 / **SHA-HMAC** | 明文=无 | 用 SHA-HMAC（`ip ospf authentication message-digest`） |
| **OSPFv3** | IPsec AH/ESP（协议本身无认证） | 依赖 IPsec | 用 `authentication ipsec spi ... sha1` |
| **IS-IS** | 明文 / MD5 / HMAC-SHA | 明文=无 | 按 L1/L2/SNP/PDU 分别配 |
| **BGP** | TCP MD5 / **TCP-AO** | MD5 有已知弱点 | 优先 TCP-AO（RFC 5925），存量用 MD5 |
| **EIGRP** | MD5 / HMAC-SHA | — | SHA |

</div>

**The real difficulty of key rotation**: a key is not "configured and done" — **rotation itself interrupts the session**. Two approaches exist:

<div class="zh" markdown="1">

**密钥轮换的真实难题**：密钥不是"配上就完事"，**轮换本身就会中断会话**。两种做法：

</div>

| Approach | Method | Cost |
|------|------|------|
| **Hard cutover** | Change the key at both ends at once and `clear ip ospf process` / `clear ip bgp *` | A defined outage window; must be done inside a maintenance window |
| **Smooth rotation (key chain)** | Configure multiple keys with `accept-lifetime` / `send-lifetime` so old and new keys overlap | Requires time synchronization at both ends (back to NTP!), and the configuration is complex |

<div class="zh" markdown="1">

| 方式 | 做法 | 代价 |
|------|------|------|
| **硬切换** | 两端同时改密钥，同时 `clear ip ospf process` / `clear ip bgp *` | 有明确的中断窗口，必须停机窗口操作 |
| **平滑轮换（Key Chain）** | 配置多个 key，带 `accept-lifetime` / `send-lifetime`，新旧 key 重叠生效 | 需两端时间同步（又回到 NTP！），且配置复杂 |

</div>

```cfg
! Smooth rotation example (key chain)
key chain OSPF-KEYS
 key 1
  key-string <old-key>
  send-lifetime 00:00:00 Jan 1 2026 00:00:00 Apr 1 2026
  accept-lifetime 00:00:00 Jan 1 2026 00:00:00 Apr 8 2026   ! keep 7 extra days of acceptance
 key 2
  key-string <new-key>
  send-lifetime 00:00:00 Apr 1 2026 infinite
  accept-lifetime 00:00:00 Mar 25 2026 infinite            ! start accepting 7 days early

interface GigabitEthernet0/1
 ip ospf authentication key-chain OSPF-KEYS
```

<div class="zh" markdown="1">

```cfg
! 平滑轮换示例（Key Chain）
key chain OSPF-KEYS
 key 1
  key-string <旧密钥>
  send-lifetime 00:00:00 Jan 1 2026 00:00:00 Apr 1 2026
  accept-lifetime 00:00:00 Jan 1 2026 00:00:00 Apr 8 2026   ! 多留 7 天接受期
 key 2
  key-string <新密钥>
  send-lifetime 00:00:00 Apr 1 2026 infinite
  accept-lifetime 00:00:00 Mar 25 2026 infinite            ! 提前 7 天开始接受

interface GigabitEthernet0/1
 ip ospf authentication key-chain OSPF-KEYS
```

</div>

> 💡 **Design principle**: every security change that "interrupts sessions" must have its **change window and rollback plan** defined at design time. The sentence "keys rotate every 90 days" in an audit report translates in practice into "one network-wide routing churn window every quarter" — and without automation that promise is abandoned by the second year.

<div class="zh" markdown="1">

> 💡 **设计原则**：所有"会中断会话"的安全变更，都必须在设计阶段就定义**变更窗口与回退方案**。审计报告里"密钥 90 天轮换"这句话，落到实施上是"每季度一次全网路由震荡窗口" —— 如果没有自动化，这个承诺第二年就废了。

</div>

##### Protection Mechanism 6: Maximum Prefix and Routing Policy

<div class="zh" markdown="1">

##### 保护机制六：最大前缀与路由策略

</div>

| Measure | Protects against | Notes |
|------|--------|------|
| **`maximum-prefix`** | A neighbor misconfiguration or attack causing the routing table to explode and exhaust memory | Set a threshold plus an alert; do not just drop the session |
| **Prefix filtering (prefix-list)** | Receiving/sending routes that should not exist | Configure in both directions on eBGP |
| **AS_PATH filtering (bogon)** | Private and reserved AS numbers being injected | Filter the reserved ASes defined in RFC 6996 |
| **RPKI / ROA validation** | BGP prefix hijacking | Requires upstream support; `bgp rpki server` plus a validation policy |
| **`bgp maxas-limit`** | Abnormally long AS_PATH (an attack signature) | — |

<div class="zh" markdown="1">

| 措施 | 防什么 | 注意 |
|------|--------|------|
| **`maximum-prefix`** | 邻居误配置或攻击导致路由表爆炸，耗尽内存 | 设阈值 + 告警，不要直接断会话 |
| **前缀过滤（prefix-list）** | 接收/发送不该有的路由 | eBGP 双向都要配 |
| **AS_PATH 过滤（bogon）** | 私用 AS、保留 AS 被注入 | 过滤 RFC 6996 定义的保留 AS |
| **RPKI / ROA 校验** | BGP 前缀劫持 | 需上游支持，`bgp rpki server` + 验证策略 |
| **`bgp maxas-limit`** | AS_PATH 异常长（攻击特征） | — |

</div>

```cfg
router bgp 65000
 neighbor 10.1.0.2 maximum-prefix 50000 85 restart 5
 neighbor 10.1.0.2 maximum-prefix 50000 warning-only    ! or alert only, without resetting
```

<div class="zh" markdown="1">

```cfg
router bgp 65000
 neighbor 10.1.0.2 maximum-prefix 50000 85 restart 5
 neighbor 10.1.0.2 maximum-prefix 50000 warning-only    ! 或只告警不重置
```

</div>

> ⚠️ **`maximum-prefix` is a double-edged sword**: the default behavior is **to drop the session when the limit is exceeded**. If the peer is a carrier, dropping your session means **the whole network goes dark**. In production, therefore, either use `warning-only` (alert only) or set `restart` so the session recovers automatically — and leave ample headroom in the threshold (if you currently have 40,000 routes, set 50,000, not 41,000).

<div class="zh" markdown="1">

> ⚠️ **`maximum-prefix` 的双刃剑**：默认行为是**超限即断会话**。如果对端是运营商，你的会话断了意味着**全网业务中断**。所以生产上要么用 `warning-only`（只告警），要么设 `restart` 让会话自动恢复，并且阈值必须留足余量（当前 4 万条就设 5 万，不要设 4.1 万）。

</div>

#### Data Plane Security · 数据平面安全

Data plane security measures are really only two categories: **filtering (ACLs)** and **anti-spoofing (uRPF / Source Guard)**. They are the "last line", but also the only means that covers "traffic the device does not participate in deciding".

<div class="zh" markdown="1">

数据平面的安全手段，本质上只有两类：**过滤（ACL）+ 反欺骗（uRPF / Source Guard）**。它们是"最后一道"，但也是唯一能覆盖"设备不参与决策的流量"的手段。

</div>

##### uRPF: Unicast Reverse Path Forwarding

![uRPF modes, the topologies each one breaks in, and the silent way it fails](assets/fig/en10-19-urpf-modes.svg)


<div class="zh" markdown="1">

##### uRPF：单播反向路径转发

</div>

**Principle**: on receiving a packet, check whether the **source IP "should" arrive through this interface**. If not, drop it — because the source address is spoofed.

<div class="zh" markdown="1">

**原理**：收到一个包，检查**源 IP 是否"应该"从这个人来的接口到达**。如果不是，就丢弃 —— 因为源地址是伪造的。

</div>

| Mode | Decision rule | What it stops | What it can wrongly drop | Where to apply |
|------|---------|---------|-----------|---------|
| **Strict** | The source IP's **optimal route outgoing interface** must equal the incoming interface | Strong — blocks the vast majority of source address spoofing | **Asymmetric routing** (different forward/return paths), multihomed access, policy-routing scenarios | Single-egress access layer, stub network edges |
| **Loose** | It is enough that **any reachable route exists** for the source IP (the outgoing interface is not checked) | Weak — only blocks "completely unroutable" sources (e.g. private addresses arriving from the Internet) | Almost never wrongly drops | Multi-egress networks, backbones, peering |
| **Feasible (VRF-aware)** | A route to the source IP exists **within a specified VRF/interface group** | Medium — and it handles MPLS/VPN multi-instance | Relatively complex to configure | VRF environments, MPLS VPNs |

<div class="zh" markdown="1">

| 模式 | 判定规则 | 能防什么 | 会误杀什么 | 适用位置 |
|------|---------|---------|-----------|---------|
| **Strict（严格）** | 源 IP 的**最优路由出接口**必须等于入接口 | 强 — 拦掉绝大多数源地址伪造 | **非对称路由**（去回路径不同）、多宿接入、策略路由场景 | 单出口的接入层、Stub 网络边缘 |
| **Loose（松散）** | 源 IP 的**路由表中存在任意一条可达路由**即可（不检查出接口） | 弱 — 只能拦"完全不可路由"的源（如私网地址从公网进来） | 基本不误杀 | 多出口网络、骨干、对等互联 |
| **Feasible（可行，VRF 感知）** | 在**指定 VRF/接口组**内存在到源 IP 的路由 | 中 — 且能处理 MPLS/VPN 多实例 | 配置相对复杂 | VRF 环境、MPLS VPN |

</div>

```cfg
! Strict
interface GigabitEthernet0/1
 ip verify unicast source reachable-via rx

! Loose
interface GigabitEthernet0/2
 ip verify unicast source reachable-via any

! Feasible (with allow-self-ping, permitting pings to the device itself)
interface GigabitEthernet0/3
 ip verify unicast source reachable-via any allow-self-ping
```

<div class="zh" markdown="1">

```cfg
! Strict
interface GigabitEthernet0/1
 ip verify unicast source reachable-via rx

! Loose
interface GigabitEthernet0/2
 ip verify unicast source reachable-via any

! Feasible（带 allow-self-ping，允许 ping 设备自身）
interface GigabitEthernet0/3
 ip verify unicast source reachable-via any allow-self-ping
```

</div>

> 🔥 **A real incident: strict uRPF killed a dual-egress branch**
>
> **Background**: a retail branch had two egress paths (MPLS as primary, Internet as backup) and PBR was deployed so that "video conferencing uses the Internet and business traffic uses MPLS". The core switch uplinked to two egress routers.
>
> **The change**: a security baseline upgrade required "uRPF strict enabled network-wide" for compliance. The branch applied `ip verify unicast source reachable-via rx` from the template.
>
> **The failure**: heavy packet loss on video conferencing and occasional business interruptions. `ping` worked (small packets, following the primary path), but large-volume, long-lived sessions failed.
>
> **Root cause**:
> - After PBR the video traffic left through the Internet egress, but the **return path came over MPLS** (the far end does not follow your PBR)
> - When return packets entered the MPLS interface, the optimal outgoing interface for that source IP was the **Internet interface** → strict uRPF judged "abnormal source address" → **packet dropped**
> - Small packets and short connections sometimes got through (hitting connected routes or cache), which made it "look like a performance problem"
>
> **Why it took so long to find**: `ping` worked, `traceroute` worked, interfaces showed no errors; only the server side could see "some connections time out". **The uRPF drop counter was the only clue**: the `suppressed` counter in `show ip interface | include verify` was climbing.
>
> **The right approach**:
> ```
> Branch uplinks (multiple egresses) → loose or feasible, never strict
> Pure stub access layer (single egress) → strict (no asymmetry possible there)
> Backbone/peering → loose
> ```
>
> **The more fundamental lesson**: **the correctness of a uRPF mode depends on whether routing is symmetric, and whether routing is symmetric depends on your design.** A compliance requirement to "configure strict everywhere" is guaranteed to break multi-egress networks. Compliance must be translated at the design level into "the right mode at each location plus a verification method", not a template pushed network-wide.

<div class="zh" markdown="1">

> 🔥 **真实事故：strict uRPF 打死了双出口分支**
>
> **背景**：某零售企业分支有两条出口（MPLS 专线为主、Internet 备份），部署了 PBR 让"视频会议走 Internet，业务走 MPLS"。核心交换机上行接两台出口路由器。
>
> **变更**：安全基线升级，全网"必须开启 uRPF strict"（合规要求）。分支按模板配了 `ip verify unicast source reachable-via rx`。
>
> **故障**：视频会议大量丢包，业务偶发中断。`ping` 正常（小包、走主路径），但大流量、长时间会话失败。
>
> **根因**：
> - 视频流量经 PBR 决策后从 Internet 出口出去，但**回程走 MPLS**（对端不遵循你的 PBR）
> - 回程包进入 MPLS 接口时，源 IP 查表的最优出接口是 **Internet 接口**（因为 PBR 只影响转发而不影响 RIB，但此处实际是 RIB 里该源的返回路径更优） → strict uRPF 判定"源地址异常" → **丢包**
> - 小包/短连接因为可能命中了直连路由或缓存，偶尔能通，导致"看起来是性能问题"
>
> **为什么排查慢**：`ping` 通、`traceroute` 通、接口无错包；只有服务器侧能看到"部分连接超时"。**uRPF 丢弃计数是唯一线索**：`show ip interface | include verify` 里的 `suppressed` 计数在飙升。
>
> **正确做法**：
> ```
> 分支上联口（多出口） → loose 或 feasible，不用 strict
> 纯 Stub 接入层（单出口）→ strict（此时不会有非对称）
> 主干/对等互联 → loose
> ```
>
> **更本质的教训**：**uRPF 模式的正确性取决于"路由是否对称"，而路由是否对称取决于你的设计。** 一个"全网统一配 strict"的合规要求，在多出口网络里必然出事。合规要求应该在设计层面翻译成"每个位置用合适的模式 + 有验证方法"，而不是一条模板刷全网。

</div>

##### IP Source Guard and DHCP Snooping

![IP Source Guard depends on a binding table it does not build itself, and three host types that break it](assets/fig/en10-20-ipsg-dhcp-snooping.svg)


<div class="zh" markdown="1">

##### IP Source Guard 与 DHCP Snooping

</div>

These are **access-layer** binding table mechanisms, complementary to uRPF: uRPF is based on the routing table (coarse), while Source Guard is based on the DHCP Snooping binding table (precise down to MAC-IP-port).

<div class="zh" markdown="1">

这两个是**接入层**的绑定表机制，与 uRPF 互补：uRPF 基于路由表（粗粒度），Source Guard 基于 DHCP Snooping 绑定表（精确到 MAC-IP-端口）。

</div>

| Mechanism | What table it builds | What it blocks |
|------|-----------|--------|
| **DHCP Snooping** | A `port ↔ MAC ↔ IP ↔ VLAN ↔ lease` binding table | DHCP server responses on untrusted ports (rogue DHCP) |
| **Dynamic ARP Inspection (DAI)** | Reuses the DHCP Snooping table | ARP whose source MAC-IP does not match (ARP spoofing) |
| **IP Source Guard** | Reuses the DHCP Snooping table | IP traffic whose source IP is not in the binding table (IP impersonation) |

<div class="zh" markdown="1">

| 机制 | 建立什么表 | 拦什么 |
|------|-----------|--------|
| **DHCP Snooping** | `端口 ↔ MAC ↔ IP ↔ VLAN ↔ 租约` 绑定表 | 非信任端口上的 DHCP 服务器响应（防 rogue DHCP） |
| **Dynamic ARP Inspection (DAI)** | 复用 DHCP Snooping 表 | 源 MAC-IP 不匹配的 ARP（防 ARP 欺骗） |
| **IP Source Guard** | 复用 DHCP Snooping 表 | 源 IP 不在绑定表中的 IP 流量（防 IP 冒用） |

</div>

```cfg
ip dhcp snooping
ip dhcp snooping vlan 10-50
no ip dhcp snooping information option          ! usually needs to be disabled (see below)
interface GigabitEthernet1/0/1                   ! uplink, trusted
 ip dhcp snooping trust
interface range GigabitEthernet1/0/2-48          ! access, untrusted
 ip dhcp snooping limit rate 10
 ip arp inspection limit rate 15
 ip verify source port-security

ip arp inspection vlan 10-50
```

<div class="zh" markdown="1">

```cfg
ip dhcp snooping
ip dhcp snooping vlan 10-50
no ip dhcp snooping information option          ! 通常需要关（见下）
interface GigabitEthernet1/0/1                   ! 上联，信任
 ip dhcp snooping trust
interface range GigabitEthernet1/0/2-48          ! 接入，不信任
 ip dhcp snooping limit rate 10
 ip arp inspection limit rate 15
 ip verify source port-security

ip arp inspection vlan 10-50
```

</div>

> ⚠️ **Three high-frequency DHCP Snooping traps**:
> 1. **`information option` incompatible with upstream**: once option 82 is enabled, some upstream DHCP servers (or carriers) drop requests carrying option 82 → users get no address. Either use `no ip dhcp snooping information option` or configure the upstream to accept it.
> 2. **Every static-IP device goes offline**: DAI/Source Guard rely on the binding table, and **devices with static IPs (printers, servers, cameras, medical equipment) are not in it**, so they are dropped outright. You must configure `ip source binding <MAC> <IP> vlan <x> interface <int>` for them, or switch them to static DHCP reservations.
> 3. **It does not work in wireless scenarios**: endpoints behind an AP share one switch port, so the binding table cannot distinguish them (the learned MAC is the AP's port). **Wireless users must be handled by the WLC client table plus wireless-side policy**; switch DHCP Snooping only protects "the AP's uplink port".

<div class="zh" markdown="1">

> ⚠️ **DHCP Snooping 的三个高频坑**：
> 1. **`information option` 与上游不兼容**：开启 option 82 后，某些上游 DHCP 服务器（或运营商）会丢弃带 option 82 的请求 → 用户拿不到地址。要么 `no ip dhcp snooping information option`，要么在上游配置接受。
> 2. **静态 IP 设备全断**：DAI/Source Guard 依赖绑定表，**静态 IP 的设备（打印机、服务器、摄像头、医疗设备）不在表里**，会被直接丢弃。必须为它们配 `ip source binding <MAC> <IP> vlan <x> interface <int>`，或改用静态 DHCP 保留。
> 3. **无线场景失效**：AP 后面的终端在交换机的同一个端口上，绑定表无法区分（MAC 学习到的是 AP 端口）。**无线用户必须靠 WLC 侧的客户端表 + 无线侧的策略**，交换机 DHCP Snooping 只能保护"AP 的上联口"。

</div>

### Layer 2 Security · 二层安全

#### Why Layer 2 Is the Last Blind Spot for Security · 为什么二层是安全的"最后盲区"

![Layer 3 policy needs the traffic to traverse the policy device; traffic inside one VLAN never does, so the VLAN boundary is the smallest security domain](assets/fig/en10-21-l2-blind-spot.svg)


The Layer 3 security system (firewalls, routing policy, subnet isolation) shares one premise: **traffic must pass through the device where you deployed the policy**. The Layer 2 problem is exactly that **traffic within the same VLAN never passes through any Layer 3 device at all**.

<div class="zh" markdown="1">

三层的安全体系（防火墙、路由策略、网段隔离）有一个共同前提：**流量必须经过你部署策略的那个设备**。而二层的问题在于 —— **同一个 VLAN 内的流量，压根不经过任何三层设备**。

</div>

```
    [PC-A] ──┐
             ├── L2 Switch ── (default gateway / firewall)  ← policy lives here
    [PC-B] ──┘
              
    PC-A → PC-B traffic: forwarded only inside the switch, never traversing the firewall
```

<div class="zh" markdown="1">

```
    [PC-A] ──┐
             ├── L2 Switch ── (默认网关 / 防火墙)  ← 策略在这里
    [PC-B] ──┘
              
    PC-A → PC-B 的流量：只在交换机内部转发，永远不经过防火墙
```

</div>

**This is the physical basis for lateral movement.** After an attacker gets onto one PC, they can ARP-spoof to capture traffic on the same subnet, scan the internal network, and reach servers in the same VLAN directly. Every Layer 3 policy is bypassed.

<div class="zh" markdown="1">

**这就是"横向移动"的物理基础**。攻击者进入一台 PC 之后，可以：ARP 欺骗拿到同网段流量、扫内网、直接访问同 VLAN 的服务器。所有三层策略全部失效。

</div>

**The design-level conclusion**: **the VLAN boundary is the smallest security domain boundary**. If a VLAN holds 500 devices and 499 of them do not trust each other, that design has failed security-wise — you have effectively put 500 devices in one "trust domain".

<div class="zh" markdown="1">

**设计层面的结论**：**VLAN 的划分就是最小的安全域边界**。如果一个 VLAN 里有 500 台设备，其中 499 台互不信任，那这个设计在安全上是失败的 —— 你等于把 500 台设备放在同一个"信任域"里。

</div>

#### The Layer 2 Attack Chain: From Access to Lateral Movement · 二层攻击链：从接入到横向移动

![The Layer 2 attack chain in six stages, each with the control that cuts that link](assets/fig/en10-22-l2-attack-chain.svg)


A real Layer 2 attack is not a single point but a chain:

<div class="zh" markdown="1">

真实的二层攻击不是单点，而是一条链：

</div>

| Stage | Attacker action | Goal | Corresponding defense |
|------|---------|------|---------|
| **① Physical access** | Plug in a cable, connect a switch | Obtain a Layer 2 entry point | Disable unused ports, port security, 802.1X |
| **② Topology reconnaissance** | Collect CDP/LLDP/STP BPDUs/DTP | Learn VLANs and device models | Disable CDP/LLDP (facing access), disable DTP |
| **③ VLAN bypass** | VLAN hopping (double tagging / DTP negotiation) | Enter other VLANs | Disable DTP, move the native VLAN to a dedicated VLAN, never trunk to access ports |
| **④ Root bridge takeover** | Send low-priority BPDUs to become root | Force traffic to traverse the attacker | **BPDU Guard**, Root Guard |
| **⑤ Man in the middle** | ARP spoofing / DHCP spoofing / IPv6 RA | Capture traffic | DAI, DHCP Snooping, RA Guard |
| **⑥ Lateral spread** | Scan hosts on the same subnet, exploit vulnerabilities | Expand control | Micro-segmentation (PVLAN / SGT / VXLAN isolation), host protection |

<div class="zh" markdown="1">

| 阶段 | 攻击动作 | 目标 | 对应防御 |
|------|---------|------|---------|
| **① 物理接入** | 插网线、接一个交换机 | 获得二层入口 | 关闭空闲端口、端口安全、802.1X |
| **② 拓扑侦察** | 收 CDP/LLDP/STP BPDU/DTP | 摸清 VLAN、设备型号 | 关闭 CDP/LLDP（面向接入侧）、关闭 DTP |
| **③ 绕过 VLAN** | VLAN 跳跃（双重标签 / DTP 协商） | 进入其他 VLAN | 关闭 DTP、native VLAN 改独立 VLAN、不打 trunk 到接入口 |
| **④ 抢占根桥** | 发低优先级 BPDU 成为 root | 让流量绕经自己 | **BPDU Guard**、Root Guard |
| **⑤ 中间人** | ARP 欺骗 / DHCP 欺骗 / IPv6 RA | 抓到流量 | DAI、DHCP Snooping、RA Guard |
| **⑥ 横向扩散** | 扫同网段主机、利用漏洞 | 扩大控制 | 微分段（PVLAN / SGT / VXLAN 隔离）、主机防护 |

</div>

**Key realization**: **every link in this chain can be blocked independently, and each is cheap**. Conversely, if none of them is done, going from "plugging in a cable" to "controlling a server on the same subnet" can take as little as 10 minutes.

<div class="zh" markdown="1">

**关键认知**：这条链上**每一环都可以被单独阻断**，而每一环的成本都很低。反过来，如果一环都没做，那么从"插上网线"到"控制同网段服务器"可能只需要 10 分钟。

</div>

#### Defenses, Item by Item · 逐项防御

![The eight Layer 2 defenses as one matrix: what each stops, where it is applied and the design gotcha that makes it fail](assets/fig/en10-23-l2-defense-matrix.svg)


##### 1. STP Attacks and BPDU Guard / Root Guard

![Spanning tree attacks and the five guards, with the difference between err-disable, root-inconsistent and a silent drop](assets/fig/en10-24-stp-guards.svg)


<div class="zh" markdown="1">

##### 1. STP 攻击与 BPDU Guard / Root Guard

</div>

| Attack | Principle | Consequence |
|------|------|------|
| **Root bridge takeover** | Connect a switch configured with `spanning-tree vlan 10 priority 0` and win the root election | All traffic detours through the attacker → man in the middle plus a performance collapse |
| **BPDU flooding** | Send BPDUs at high rate | CPU exhaustion, STP churn |

<div class="zh" markdown="1">

| 攻击 | 原理 | 后果 |
|------|------|------|
| **根桥抢占** | 接入一台交换机并配 `spanning-tree vlan 10 priority 0`，抢到 root | 全网流量绕经攻击者 → 中间人 + 性能崩塌 |
| **BPDU 洪泛** | 高速发送 BPDU | CPU 耗尽、STP 震荡 |

</div>

| Defense | Where to deploy | Behavior |
|------|---------|------|
| **PortFast** | Ports facing endpoints | Skips listening/learning and goes straight to forwarding (**no security capability**) |
| **BPDU Guard** | Ports facing endpoints (together with PortFast) | **err-disables the port on receiving a BPDU** — an endpoint port should never see BPDUs |
| **Root Guard** | Ports facing downstream switches / other domains | Rejects superior BPDUs and puts the port into `root-inconsistent` (**does not err-disable; it recovers by itself**) |
| **Loop Guard** | Blocked ports / fiber ports | Prevents the port entering forwarding when a unidirectional link stops BPDUs |
| **BPDU Filter** | Very few scenarios (connecting to a carrier) | **Stops sending and receiving BPDUs**; used wrongly it causes loops, so use with care |

<div class="zh" markdown="1">

| 防御 | 部署位置 | 行为 |
|------|---------|------|
| **PortFast** | 接终端端口 | 跳过 listening/learning，直接 forwarding（**不含安全能力**） |
| **BPDU Guard** | 接终端端口（配合 PortFast） | **收到 BPDU 就把端口 err-disable** —— 因为终端口不该有 BPDU |
| **Root Guard** | 指向下游交换机/其他域的端口 | 收到更优 BPDU 时不接受，把端口置为 `root-inconsistent`（**不 err-disable，恢复后自愈**） |
| **Loop Guard** | 阻塞端口/光纤口 | 单向链路导致 BPDU 停发时，阻止端口进入 forwarding |
| **BPDU Filter** | 极少数场景（对接运营商） | **停止收发 BPDU**，用错会导致环路，慎用 |

</div>

```cfg
! Global: PortFast + BPDU Guard by default on access ports
spanning-tree portfast default
spanning-tree portfast bpduguard default

! Important: use Root Guard (not BPDU Guard) on ports facing downstream
interface GigabitEthernet1/0/24
 spanning-tree guard root

! Loop Guard on ports exposed to unidirectional-link risk
spanning-tree loopguard default
```

<div class="zh" markdown="1">

```cfg
! 全局：接入端口默认 PortFast + BPDU Guard
spanning-tree portfast default
spanning-tree portfast bpduguard default

! 关键：指向下游的端口用 Root Guard（而不是 BPDU Guard）
interface GigabitEthernet1/0/24
 spanning-tree guard root

! 单向链路风险端口用 Loop Guard
spanning-tree loopguard default
```

</div>

> ⚠️ **Typical consequences of swapping BPDU Guard and Root Guard**:
> - Configuring BPDU Guard on a **cascaded port** → the cascaded switch is err-disabled the moment it boots, taking the whole downstream segment offline (and it is hard to diagnose on site, because the port is err-disabled rather than down)
> - Configuring Root Guard on an **access port** → pointless for endpoints (they do not send BPDUs)
>
> **One-line mnemonic**: **facing down (endpoints) = BPDU Guard; facing sideways/downstream switches = Root Guard.**

<div class="zh" markdown="1">

> ⚠️ **BPDU Guard 与 Root Guard 用错的典型后果**：
> - 在**级联口**上配 BPDU Guard → 级联的交换机一开机就被 err-disable，下游整片断网（且现场很难判断，因为端口是 err-disabled 而不是 down）
> - 在**接入口**上配 Root Guard → 对终端无意义（终端不发 BPDU）
>
> **一句话记法**：**朝下（对终端）= BPDU Guard；朝侧面/下游交换机 = Root Guard。**

</div>

##### 2. VLAN Hopping

![How 802.1Q double tagging crosses a VLAN boundary, why the flight is one-way, and the three settings that close it](assets/fig/en10-25-vlan-hopping.svg)


<div class="zh" markdown="1">

##### 2. VLAN 跳跃

</div>

| Technique | Principle | Defense |
|------|------|------|
| **DTP negotiation** | Send DTP frames to turn an access port into a trunk | `switchport mode access` + `switchport nonegotiate` |
| **Double tagging** | Push two 802.1Q tags, with the native VLAN as the outer tag | **Use a dedicated, unused VLAN ID for the native VLAN**; `vlan dot1q tag native` on trunks (force tagging) |
| **Trunks left enabled by mistake** | An access port configured as a trunk during installation | Port templates enforce access; tighten `switchport trunk allowed vlan` |

<div class="zh" markdown="1">

| 手法 | 原理 | 防御 |
|------|------|------|
| **DTP 协商** | 发 DTP 帧让接入口变成 trunk | `switchport mode access` + `switchport nonegotiate` |
| **双重标签（Double Tagging）** | 打两层 802.1Q，外层是 native VLAN | **native VLAN 使用独立、未使用的 VLAN ID**；trunk 上 `vlan dot1q tag native`（强制打标） |
| **Trunk 口误开** | 装机时把接入口配成 trunk | 端口模板强制 access、`switchport trunk allowed vlan` 收紧 |

</div>

```cfg
! Anti-VLAN-hopping
interface GigabitEthernet1/0/1
 switchport mode access
 switchport access vlan 20
 switchport nonegotiate              ! disable DTP
 spanning-tree portfast

! trunk port
interface GigabitEthernet1/0/24
 switchport mode trunk
 switchport trunk native vlan 999     ! dedicated, unused, no SVI
 switchport trunk allowed vlan 20,30  ! minimized
 switchport nonegotiate
```

<div class="zh" markdown="1">

```cfg
! 反 VLAN 跳跃
interface GigabitEthernet1/0/1
 switchport mode access
 switchport access vlan 20
 switchport nonegotiate              ! 关闭 DTP
 spanning-tree portfast

! trunk 口
interface GigabitEthernet1/0/24
 switchport mode trunk
 switchport trunk native vlan 999     ! 独立、不用、无 SVI
 switchport trunk allowed vlan 20,30  ! 最小化
 switchport nonegotiate
```

</div>

> 💡 **Design principle**: **the native VLAN must be a VLAN that carries no service at all** (e.g. 999), and that VLAN must have no SVI and appear on no access port. That way, even a successful double-tagging attack can only jump into this empty VLAN.

<div class="zh" markdown="1">

> 💡 **设计原则**：**native VLAN 必须是一个"不存在任何业务"的 VLAN**（如 999），且该 VLAN 不能有任何 SVI、不能出现在任何 access 口。这样双重标签攻击即使成功，也只能跳到这个空 VLAN。

</div>

##### 3. MAC Flooding and Port Security

![MAC flooding turns a switch into a hub, and port security is the counter - with three violation behaviours and two practical traps](assets/fig/en10-26-mac-flooding-port-security.svg)


<div class="zh" markdown="1">

##### 3. MAC 泛洪与端口安全

</div>

| Attack | Principle | Consequence |
|------|------|------|
| **MAC flooding** | Fill the CAM table with a large number of random source MACs | After CAM overflow the switch **floods every unknown unicast** → the attacker can sniff the entire VLAN |

<div class="zh" markdown="1">

| 攻击 | 原理 | 后果 |
|------|------|------|
| **MAC 泛洪** | 用大量随机源 MAC 打满 CAM 表 | CAM 溢出后交换机**对所有未知单播泛洪** → 攻击者可以嗅探整个 VLAN |

</div>

```cfg
interface GigabitEthernet1/0/5
 switchport port-security
 switchport port-security maximum 2                ! one phone + one PC
 switchport port-security violation restrict       ! drop and alert (no err-disable)
 switchport port-security aging time 60
```

<div class="zh" markdown="1">

```cfg
interface GigabitEthernet1/0/5
 switchport port-security
 switchport port-security maximum 2                ! 一台电话+一台PC
 switchport port-security violation restrict       ! 超限丢弃并告警（不 err-disable）
 switchport port-security aging time 60
```

</div>

**Choosing among the three violation behaviors**:

<div class="zh" markdown="1">

**violation 三种行为的选择**：

</div>

| Mode | Behavior | When to use |
|------|------|------|
| `protect` | Silently drops, no log | Not recommended (undetectable) |
| `restrict` | Drops + SNMP/log alert | **Recommended** (detectable, does not affect others) |
| `shutdown` | err-disables the port | High-security environments, but **high operational cost** (manual recovery) |

<div class="zh" markdown="1">

| 模式 | 行为 | 适用 |
|------|------|------|
| `protect` | 静默丢弃，无日志 | 不推荐（无法发现） |
| `restrict` | 丢弃 + SNMP/日志告警 | **推荐**（可发现，不影响他人） |
| `shutdown` | err-disable 端口 | 高安全场景，但**运维成本高**（要人工恢复） |

</div>

> ⚠️ **Two practical problems with port security**:
> 1. **Setting `maximum` too low** → users change cables, swap USB-C docks, or connect an IP phone plus a PC, and any change in MAC count triggers a violation. The killer is **random MAC addresses** (on by default in Windows/macOS/iOS): the MAC changes every time they join Wi-Fi, and sometimes on wired connections too.
> 2. **The relationship between port security and 802.1X**: once 802.1X is in place, "you cannot use the port until authenticated" already covers the main MAC-flooding scenario, so port security is mostly used to **limit the number of devices per port**. When both are deployed, pay attention to order and exceptions (the voice VLAN for IP phones needs a MAC whitelist).

<div class="zh" markdown="1">

> ⚠️ **端口安全的两个现实问题**：
> 1. **`maximum` 定太小** → 用户换网线、换 USB-C 扩展坞、接 IP 电话 + PC，MAC 数变化就触发 violation。笔记本的**随机 MAC 功能（Windows/macOS/iOS 默认开启）** 是最大的杀手：每次连 Wi-Fi 变 MAC，连有线也可能变。
> 2. **端口安全与 802.1X 的关系**：上了 802.1X 之后，"未认证不能用"已经覆盖了 MAC 泛洪的主要场景，端口安全更多用于**限制单端口设备数量**。两者同时部署时要注意顺序与例外（IP 电话的语音 VLAN 需要 MAC 白名单）。

</div>

##### 4. ARP Spoofing and DAI

![ARP spoofing, the three checks dynamic ARP inspection performs, and the static-address hole that breaks real deployments](assets/fig/en10-27-arp-dai.svg)


<div class="zh" markdown="1">

##### 4. ARP 欺骗与 DAI

</div>

**How ARP spoofing works**: the attacker continuously broadcasts "the MAC for `192.168.1.1` is mine", so every host's ARP table points the gateway at the attacker → all off-subnet traffic passes through the attacker.

<div class="zh" markdown="1">

**ARP 欺骗原理**：攻击者持续广播"`192.168.1.1` 的 MAC 是我"，让所有主机的 ARP 表把网关指向攻击者 → 所有出网流量经过攻击者。

</div>

**Defense comparison**:

<div class="zh" markdown="1">

**防御对比**：

</div>

| Option | Mechanism | Coverage | Limitation |
|------|------|---------|------|
| **DAI** | Verifies that the MAC-IP of ARP packets is in the DHCP Snooping binding table | Switch access layer | Depends on the binding table; **static IPs are not covered** |
| **Dynamic ARP inspection + ACL** | Allows ARP but rate limits it | Same as DAI | Treats the symptom |
| **Static ARP / IP-MAC binding** | Static binding on the gateway | Small scale | Does not scale |
| **Private VLAN / port isolation** | Ports cannot talk to each other | Access layer | Business may not allow it (mutual access may be required) |
| **Encryption (MACsec)** | Layer 2 encryption/decryption | Point to point | Hop by hop, expensive |

<div class="zh" markdown="1">

| 方案 | 机制 | 覆盖范围 | 局限 |
|------|------|---------|------|
| **DAI** | 校验 ARP 的 MAC-IP 是否在 DHCP Snooping 绑定表 | 交换机接入层 | 依赖绑定表，**静态 IP 不覆盖** |
| **动态 ARP 检测 + ACL** | 允许 ARP 但限制速率 | 同 DAI | 治标 |
| **静态 ARP / IP-MAC 绑定** | 网关侧静态绑定 | 小规模 | 无法扩展 |
| **私有 VLAN / 端口隔离** | 端口间不互通 | 接入层 | 业务可能不允许（如需要互访） |
| **加密（MACsec）** | 二层加解密 | 点对点 | 逐跳，成本高 |

</div>

```cfg
ip arp inspection vlan 10-50
ip arp inspection validate src-mac dst-mac ip    ! all three checks on
interface GigabitEthernet1/0/10
 ip arp inspection trust                          ! trust uplinks/servers
 ip arp inspection limit rate 30 burst interval 1
```

<div class="zh" markdown="1">

```cfg
ip arp inspection vlan 10-50
ip arp inspection validate src-mac dst-mac ip    ! 三项校验全开
interface GigabitEthernet1/0/10
 ip arp inspection trust                          ! 上联/服务器口信任
 ip arp inspection limit rate 30 burst interval 1
```

</div>

> 🔥 **Case: DAI go-live took operating-room devices offline**
>
> **Scenario**: a grade-A hospital undergoing compliance remediation was required to enable DHCP Snooping + DAI + IP Source Guard network-wide at the access layer.
>
> **Outcome**: on the night of go-live, **two anesthesia monitors in the operating rooms and three infusion pumps in the ICU** went offline. The vendor's engineers arrived and said "it is a network problem, not our responsibility".
>
> **Root cause**: these medical devices use **static IPs and the vendor does not allow configuration changes** (some are fixed at the factory; changing the IP requires vendor authorization). They were therefore not in the DHCP Snooping binding table, and DAI/Source Guard treated their traffic as illegal and dropped it.
>
> **Why testing missed it**: the pilot was in the administration building (a DHCP environment of PCs and printers) and **did not cover any medical devices**.
>
> **Remediation (three options in theory; a combination was used in practice)**:
> 1. **Static binding**: `ip source binding 0011.2233.4455 10.20.30.40 vlan 20 interface Gi1/0/12` (must be entered one by one, unmaintainable when there are many devices)
> 2. **Exempt the port**: `no ip arp inspection` or set the port as trusted (minimize the scope and accept the residual risk)
> 3. **Give static devices their own VLAN** (recommended): one VLAN for medical devices without DAI, with PVLAN/ACLs as compensating isolation
>
> **The real lessons (from a CCDE perspective)**:
> - **The scope of a network security measure must be produced together with a "business device compatibility list"**. You cannot deliver only the "technical design"; you must also deliver "which devices are not supported and what to do about them".
> - **The peculiarities of IoT/medical/industrial devices**: static IPs, no 802.1X support, uncooperative vendors, no casual reboots, locked firmware. Architecturally such devices should be **segmented separately**, replacing "device-side cooperation" with "network-side isolation".
> - **Rollouts must be phased, and the first phase must include "the hardest devices"**, not the easiest ones.

<div class="zh" markdown="1">

> 🔥 **案例：DAI 上线导致手术室设备离线**
>
> **场景**：某三甲医院做等保整改，要求在接入层全网开启 DHCP Snooping + DAI + IP Source Guard。
>
> **结果**：上线当晚，**手术室的两台麻醉监护仪、ICU 的三台输液泵**离线。厂商工程师到场说"网络问题，不在我们责任范围"。
>
> **根因**：这些医疗设备是**静态 IP 且厂商不允许改配置**（有的甚至是出厂固化，改 IP 需要厂商授权），因此不在 DHCP Snooping 绑定表里，被 DAI/Source Guard 判定为非法流量而丢弃。
>
> **为什么测试没发现**：试点选的是行政楼（PC + 打印机的 DHCP 环境），**没有覆盖医疗设备**。
>
> **修复方案（三选一，实际用了组合）**：
> 1. **静态绑定**：`ip source binding 0011.2233.4455 10.20.30.40 vlan 20 interface Gi1/0/12`（需逐台录入，设备多时不可维护）
> 2. **设备所在端口豁免**：`no ip arp inspection` / 或把端口设为 trust（范围最小化，接受残余风险）
> 3. **为静态设备单独划分 VLAN**（推荐）：医疗设备一个 VLAN、不启用 DAI，用 PVLAN/ACL 做隔离补偿
>
> **真正的教训（CCDE 视角）**：
> - **网络安全措施的覆盖范围必须与"业务设备的兼容性清单"同时产出**。不能只出"技术方案"，还要出"哪些设备不支持、怎么办"。
> - **IoT/医疗/工控设备的特殊性**：静态 IP、不支持 802.1X、厂商不配合、不能随便重启、固件锁死。这类设备在架构上应该**单独分段**，用"网络侧隔离"替代"设备侧配合"。
> - **上线必须分批，且第一批要包含"最难搞的设备"**，而不是最容易的。

</div>

##### 5. DHCP Spoofing and IPv6 RA Spoofing

<div class="zh" markdown="1">

##### 5. DHCP 欺骗与 IPv6 RA 欺骗

</div>

| Attack | Mechanism | Defense |
|------|------|------|
| **Rogue DHCP** | The attacker answers DHCP requests and points the gateway/DNS at itself | **DHCP Snooping** (untrusted ports reject DHCP Offers) |
| **DHCP starvation** | Forged MACs exhaust the address pool | Port security + `ip dhcp snooping limit rate` |
| **IPv6 RA spoofing** | Sends Router Advertisements so hosts treat the attacker as their default gateway (**often completely undefended in IPv4-only networks**) | **RA Guard** + `no ipv6 unicast-routing` (if IPv6 is unused) + disabling RA acceptance on hosts |

<div class="zh" markdown="1">

| 攻击 | 机制 | 防御 |
|------|------|------|
| **Rogue DHCP** | 攻击者响应 DHCP 请求，把网关/DNS 指向自己 | **DHCP Snooping**（非信任端口拒绝 DHCP Offer） |
| **DHCP 饥饿** | 伪造大量 MAC 耗尽地址池 | 端口安全 + `ip dhcp snooping limit rate` |
| **IPv6 RA 欺骗** | 发 Router Advertisement 让主机把攻击者当默认网关（**IPv4 网络常完全没防**） | **RA Guard** + `no ipv6 unicast-routing`（若不用 IPv6）+ 主机侧禁用 RA 接受 |

</div>

> ⚠️ **The most commonly overlooked item**: an enterprise "only uses IPv4", so it has **no IPv6 security policy whatsoever**. But Windows/Linux/macOS **have IPv6 enabled and accept RAs by default**. All an attacker has to do is send an RA and the entire VLAN's IPv6 default route points at them — many attack tools use exactly this for man-in-the-middle attacks (because IPv6 takes precedence over IPv4).
>
> **The right approach** (in a pure IPv4 network):
> ```cfg
> ! Switch/router side: do not send RAs, do not route IPv6
> no ipv6 unicast-routing
> interface range GigabitEthernet1/0/1-48
>  ipv6 nd ra suppress all
> ! RA Guard on the access layer (where the switch supports it)
> ipv6 nd raguard policy HOST
>  device-role host
> ```
> At the same time disable IPv6 or RA acceptance at the host image level (Group Policy / sysctl).

<div class="zh" markdown="1">

> ⚠️ **最容易被忽略的一条**：企业网"只用 IPv4"，于是**没有任何 IPv6 安全策略**。而 Windows/Linux/macOS **默认开启 IPv6 且接受 RA**。攻击者只要发 RA，就能把整个 VLAN 的 IPv6 默认路由指向自己 —— 很多攻击工具正是利用这一点做中间人（因为 IPv6 优先于 IPv4）。
>
> **正确做法**（在纯 IPv4 网络中）：
> ```cfg
> ! 交换机/路由器侧：不发 RA、不路由 IPv6
> no ipv6 unicast-routing
> interface range GigabitEthernet1/0/1-48
>  ipv6 nd ra suppress all
> ! 接入层用 RA Guard（交换机支持时）
> ipv6 nd raguard policy HOST
>  device-role host
> ```
> 同时在主机镜像层面禁用 IPv6 或禁用 RA 接受（组策略 / sysctl）。

</div>

##### 6. 802.1X: Port-Level Admission Control

![802.1X in one page: three roles, four methods, four host modes, three deployment modes and the fallback path](assets/fig/en10-28-8021x.svg)


<div class="zh" markdown="1">

##### 6. 802.1X：端口级准入

</div>

802.1X is **the only mechanism that raises "can I connect" from the physical layer to the identity layer**. It has three roles:

<div class="zh" markdown="1">

802.1X 是**唯一能把"能不能接入"从物理层提升到身份层**的机制。它的三个角色：

</div>

| Role | Location | Responsibility |
|------|------|------|
| **Supplicant (client)** | Endpoint | Provides credentials/certificates |
| **Authenticator** | Switch/AP/WLC | Controls port state, relays EAP |
| **Authentication server** | RADIUS | Validates credentials, returns authorization attributes |

<div class="zh" markdown="1">

| 角色 | 位置 | 职责 |
|------|------|------|
| **Supplicant（客户端）** | 终端 | 提供凭据/证书 |
| **Authenticator（认证者）** | 交换机/AP/WLC | 控制端口开闭，转发 EAP |
| **Authentication Server（认证服务器）** | RADIUS | 验证凭据，返回授权属性 |

</div>

**Choosing among the authentication methods**:

<div class="zh" markdown="1">

**三种认证方式的选型**：

</div>

| Method | Credential | Security | Deployment cost | When to use |
|------|------|--------|---------|------|
| **EAP-TLS** | **Mutual certificates** | Highest (no password to steal) | High (needs PKI + certificate distribution + endpoint management) | Corporate-owned devices, high-security zones |
| **PEAP-MSCHAPv2** | Username/password (server certificate) | Medium (passwords can be brute-forced offline; **vulnerable to evil-twin APs**) | Medium (depends on AD) | Employee BYOD, the common compromise |
| **EAP-FAST / TEAP** | Password + flexible tunnel | Medium–high | Medium | Where PACs or tunnel binding are required |
| **MAB (MAC authentication)** | MAC address | **Low** (MACs are forgeable) | Low (no client needed) | **Devices that do not support 802.1X** (printers, cameras, medical devices) |

<div class="zh" markdown="1">

| 方式 | 凭据 | 安全性 | 部署成本 | 适用 |
|------|------|--------|---------|------|
| **EAP-TLS** | **双向证书** | 最高（无密码可窃） | 高（需 PKI + 证书分发 + 终端管理） | 企业自有设备、高安全区 |
| **PEAP-MSCHAPv2** | 用户名密码（服务器证书） | 中（密码可被离线爆破；**易受恶意 AP 攻击**） | 中（依赖 AD） | 员工 BYOD、常见折中 |
| **EAP-FAST / TEAP** | 密码 + 灵活隧道 | 中-高 | 中 | 需要 PAC 或隧道绑定 |
| **MAB（MAC 认证）** | MAC 地址 | **低**（MAC 可伪造） | 低（无需客户端） | **不支持 802.1X 的设备**（打印机、摄像头、医疗设备） |

</div>

**Deployment modes**:

<div class="zh" markdown="1">

**部署模式**：

</div>

| Mode | Behavior when unauthenticated | When to use |
|------|--------------|------|
| **Monitor mode** | Logs only, does not block | **Must run for 1–3 months first** to find out "who does not support it" |
| **Low-impact mode** | Unauthenticated traffic goes to a restricted VLAN (DHCP/DNS only, plus a remediation server) | Smooth transition, good user experience |
| **Closed mode** | Unauthenticated means no connectivity at all | The end goal, and the highest risk |

<div class="zh" markdown="1">

| 模式 | 未认证时的行为 | 适用 |
|------|--------------|------|
| **Monitor Mode（监控）** | 只记录，不阻断 | **必须先跑 1~3 个月**，摸清"谁不支持" |
| **Low-Impact（低影响）** | 未认证流量放到受限 VLAN（含 DHCP/DNS，仅能访问修复服务器） | 平滑过渡，用户体验好 |
| **Closed Mode（强制）** | 未认证完全不通 | 最终目标，风险最高 |

</div>

```cfg
! Switch side 802.1X
aaa new-model
radius server ISE1
 address ipv4 10.255.5.10 auth-port 1812 acct-port 1813
 key <strong-key>

aaa authentication dot1x default group radius
aaa authorization network default group radius
aaa accounting dot1x default start-stop group radius
dot1x system-auth-control

interface GigabitEthernet1/0/6
 switchport mode access
 switchport access vlan 999              ! isolation VLAN before authentication
 authentication host-mode multi-domain    ! separate data and voice domains
 authentication order dot1x mab
 authentication priority dot1x mab
 authentication port-control auto
 authentication violation restrict
 mab
 dot1x pae authenticator
 dot1x timeout tx-period 10
 spanning-tree portfast
```

<div class="zh" markdown="1">

```cfg
! 交换机侧 802.1X
aaa new-model
radius server ISE1
 address ipv4 10.255.5.10 auth-port 1812 acct-port 1813
 key <强密钥>

aaa authentication dot1x default group radius
aaa authorization network default group radius
aaa accounting dot1x default start-stop group radius
dot1x system-auth-control

interface GigabitEthernet1/0/6
 switchport mode access
 switchport access vlan 999              ! 认证前的隔离 VLAN
 authentication host-mode multi-domain    ! 数据域 + 语音域分离
 authentication order dot1x mab
 authentication priority dot1x mab
 authentication port-control auto
 authentication violation restrict
 mab
 dot1x pae authenticator
 dot1x timeout tx-period 10
 spanning-tree portfast
```

</div>

**Choosing among the four host-mode options (extremely important)**:

<div class="zh" markdown="1">

**host-mode 四种模式的选择（极重要）**：

</div>

| Mode | What is allowed | Scenario |
|------|------|---------|
| **multi-auth** | Every MAC authenticates independently | A small switch/HUB behind one port (**weakest security**) |
| **multi-domain** | **One data domain + one voice domain**, authenticated separately | IP phone with a PC behind it (**most common**) |
| **multi-host** | The first authentication succeeds, everything after it is allowed | **Not recommended** (one device authenticates and the whole HUB gets on) |
| **single-host** | Only one MAC allowed | Single-person office positions |

<div class="zh" markdown="1">

| 模式 | 允许 | 适用场景 |
|------|------|---------|
| **multi-auth** | 每个 MAC 独立认证 | 一个端口接小交换机/HUB（**安全最弱**） |
| **multi-domain** | **一个数据域 + 一个语音域**，各自认证 | IP 电话 + 后接 PC（**最常用**） |
| **multi-host** | 第一个认证通过，后续全部放行 | **不推荐**（一台通过，整个 HUB 都能上） |
| **single-host** | 只允许一个 MAC | 单人办公位 |

</div>

> 🔥 **Case: 802.1X go-live bricked 300 printers**
>
> **Background**: a 5,000-person enterprise ran an admission-control project. After three months of monitor mode it found 1,200 devices that did not support 802.1X. The plan: supported devices use PEAP-MSCHAPv2, unsupported ones use MAB (a MAC whitelist).
>
> **Day one of go-live**: about 300 printers went offline. Their MACs **were already in the MAB whitelist**.
>
> **Root cause (three things stacked)**:
> 1. **The printer whitelist had been exported from an old DHCP Snooping table**, and some printers had **had their NICs replaced** (motherboard swaps during repair), so their MACs had changed
> 2. Some printers **never send a MAB request at all** (certain models do not send EAPOL-Start after link up, so the switch must actively trigger them with `dot1x tx-period`, and some old models do not answer the active request)
> 3. **The ordering problem**: with `authentication order dot1x mab` the switch tries dot1x first (waiting up to 30 seconds before falling back to MAB), and the printer **had already given up and reported "network unavailable"** within those 30 seconds — so the user assumed it was broken and called the helpdesk
>
> **Fix**:
> - For printer-only ports use `authentication order mab` (**MAB before dot1x**), cutting authentication time from 30 s to 3 s
> - Give printers **DHCP static reservations plus automatic synchronization of the MAB whitelist** (generated from IPAM/DHCP tables instead of being maintained by hand)
> - Old devices that cannot do MAB go into a "restricted VLAN" (print server + DHCP/DNS only)
>
> **Four design-level lessons**:
> 1. **The MAC whitelist must be synchronized automatically** (a manually maintained whitelist always rots within six months)
> 2. **Authentication latency must be tested**, not just "whether it connects". A 30-second authentication wait looks like "the network is broken" from the user's point of view
> 3. **Design the fallback path first**: what happens when RADIUS is unavailable (`authentication critical`, or temporarily `authentication open`), otherwise a RADIUS outage takes the whole network down
> 4. **Exceptional devices need a home**: not "whitelist" and not "do nothing", but "put it in a restricted VLAN" so it can only do what it should

<div class="zh" markdown="1">

> 🔥 **案例：802.1X 上线把 300 台打印机打成"砖"**
>
> **背景**：某 5,000 人企业做准入项目，经过 3 个月 monitor mode 收集，发现 1,200 台设备不支持 802.1X。方案定为：支持者走 PEAP-MSCHAPv2，不支持的走 MAB（MAC 白名单）。
>
> **上线第一天**：约 300 台打印机离线。MAB 白名单里**明明有它们的 MAC**。
>
> **根因（三个叠加）**：
> 1. **打印机的 MAC 白名单是从老的 DHCP Snooping 表导出的**，其中有一部分打印机**换过网卡**（维修时更换主板），MAC 已变
> 2. 部分打印机的 MAB 请求**根本不发**（某些型号在链路 up 后不发 EAPOL-Start，需要交换机主动 `dot1x tx-period` 触发，而某些老型号对主动请求不回）
> 3. **MAB 的顺序问题**：`authentication order dot1x mab` 时，交换机先尝试 dot1x（等 30 秒超时才落 MAB），打印机在这 30 秒内**已经放弃并报"网络不可用"**，用户以为坏了就报修
>
> **修复**：
> - 对纯打印机端口 `authentication order mab`（**先 MAB 后 dot1x**），把认证时间从 30 秒降到 3 秒
> - 为打印机建立**DHCP 静态保留 + 定期自动同步 MAB 白名单**（从 IPAM/DHCP 表自动生成，不再手工维护）
> - 无法 MAB 的老设备，划分到"受限 VLAN"（只能访问打印服务器 + DHCP/DNS）
>
> **设计层面的四条教训**：
> 1. **MAC 白名单必须自动化同步**（人工维护的白名单一定会在 6 个月内腐坏）
> 2. **必须测认证时延**，不只是测"能不能通"。30 秒的认证等待在用户视角就是"网坏了"
> 3. **降级路径要先设计好**：RADIUS 不可用时的 fallback（`authentication critical` / 或临时 `authentication open`），否则 RADIUS 一挂全网断
> 4. **例外设备要有归宿**：不是"白名单"或"不做"，而是"放进受限 VLAN"，让它只能做该做的事

</div>

##### 7. Private VLAN (Port Isolation)

![Private VLAN: one primary VLAN split into isolated and community segments behind a promiscuous port, and why it lost to SGT and VXLAN](assets/fig/en10-29-pvlan.svg)


<div class="zh" markdown="1">

##### 7. Private VLAN（端口隔离）

</div>

**Principle**: split one primary VLAN into multiple secondary VLANs, where roles decide whether ports can talk to each other.

<div class="zh" markdown="1">

**原理**：在一个主 VLAN 内划分多个子 VLAN，端口之间按角色决定能否互通。

</div>

| Port type | Can communicate with |
|---------|-----------|
| **Promiscuous** | All ports (usually the gateway/server port) |
| **Isolated** | **Only promiscuous**; isolated ports cannot reach each other at all |
| **Community** | Ports in the same community plus promiscuous |

<div class="zh" markdown="1">

| 端口类型 | 能与谁通信 |
|---------|-----------|
| **Promiscuous（混杂）** | 与所有端口（通常是网关/服务器口） |
| **Isolated（隔离）** | **只能与 promiscuous**，隔离口之间完全不通 |
| **Community（团体）** | 与同 community 的端口 + promiscuous |

</div>

**Where it fits**:

<div class="zh" markdown="1">

**适用场景**：

</div>

| Scenario | Configuration | Benefit |
|------|------|------|
| Hotels/dormitories/apartments | Every room isolated | Residents cannot reach each other while sharing one subnet and gateway |
| Multiple web servers in a DMZ | isolated + one promiscuous as LB/gateway | A compromised server cannot move laterally |
| Carrier access | isolated | Natural customer isolation |

<div class="zh" markdown="1">

| 场景 | 配置 | 收益 |
|------|------|------|
| 酒店/宿舍/公寓 | 每房间 isolated | 住户之间不能互访，共享一个网段和网关 |
| DMZ 多台 Web 服务器 | isolated + 一台 promiscuous 做 LB/网关 | 一台被攻破不能横向到其他 |
| 运营商接入 | isolated | 天然的客户隔离 |

</div>

**Limitations (why it is not widespread)**:

<div class="zh" markdown="1">

**局限（为什么不普及）**：

</div>

1. **Complex configuration**, with significant behavioral differences between vendors
2. **Difficult across switches** (requires VTPv3 or manual synchronization, which easily drifts)
3. **Incompatible with VXLAN/EVPN** (there is no PVLAN concept in an overlay)
4. **Hard to troubleshoot**: when it does not work you cannot quickly tell whether PVLAN, an ACL, or routing is at fault

<div class="zh" markdown="1">

1. **配置复杂**，且各厂商行为差异大
2. **跨交换机难做**（需 VTPv3 或手工同步，容易不一致）
3. **与 VXLAN/EVPN 环境不兼容**（overlay 里没有 PVLAN 概念）
4. **难以排障**：不通时无法快速判断是 PVLAN 还是 ACL 还是路由

</div>

> 💡 **Modern replacements**: **SGT (TrustSec) plus policy** in the campus, **VXLAN plus micro-segmentation (EPG/security groups)** in the data center. PVLAN is only used with "old equipment and simple scenarios".

<div class="zh" markdown="1">

> 💡 **现代替代**：园区用 **SGT（TrustSec）+ 策略**，数据中心用 **VXLAN + 微分段（EPG/安全组）**。PVLAN 只在"设备老旧 + 场景单纯"时使用。

</div>

##### 8. MACsec: Layer 2 Encryption

![MACsec: hop-by-hop Layer 2 encryption with about thirty-two bytes of overhead, its key agreement, and where IPsec or TLS is the right answer instead](assets/fig/en10-30-macsec.svg)


<div class="zh" markdown="1">

##### 8. MACsec：二层加密

</div>

**What problem it solves**: physical eavesdropping on a link (outdoor fiber between buildings, shared data centers, bare fiber leased from a carrier).

<div class="zh" markdown="1">

**解决什么问题**：链路被物理窃听（如楼宇间的室外光纤、共享机房、运营商提供的裸光纤）。

</div>

| Dimension | Description |
|------|------|
| **Standard** | IEEE 802.1AE |
| **Key agreement** | MKA (MACsec Key Agreement, 802.1X derives the CAK) |
| **Encryption scope** | Point to point, **hop by hop** (not end to end) |
| **Performance** | Hardware dependent (line rate with ASIC support, large degradation without) |
| **Difference from IPsec** | MACsec is Layer 2, with low overhead (~32 bytes) and keeps the original IP header; IPsec is Layer 3, with high overhead, and works across any network |

<div class="zh" markdown="1">

| 维度 | 说明 |
|------|------|
| **标准** | IEEE 802.1AE |
| **密钥协商** | MKA（MACsec Key Agreement，802.1X 派生 CAK） |
| **加密范围** | 点对点，**逐跳**（不是端到端） |
| **性能** | 依赖硬件（ASIC 支持则线速，不支持则大幅下降） |
| **与 IPsec 的区别** | MACsec 在二层、开销小（~32 字节）、可保留原始 IP 头；IPsec 在三层、开销大、跨任意网络 |

</div>

**Decision matrix**:

<div class="zh" markdown="1">

**决策矩阵**：

</div>

| Scenario | Choice |
|------|------|
| Fiber between buildings, metro Ethernet, data center interconnect (DCI) | **MACsec** (line rate, low overhead) |
| Site interconnection across the Internet | **IPsec** (MACsec cannot cross a Layer 3 network) |
| Server to switch (high-security zone) | MACsec (NIC support required) |
| End-to-end encryption (across multiple hops) | **Application-layer TLS**; MACsec is hop by hop and cannot cover it |

<div class="zh" markdown="1">

| 场景 | 选择 |
|------|------|
| 楼宇间光纤、城域以太网、数据中心互联（DCI） | **MACsec**（线速、低开销） |
| 跨 Internet 的站点互联 | **IPsec**（MACsec 不能跨三层网络） |
| 服务器到交换机（高安全区） | MACsec（需网卡支持） |
| 端到端加密（跨多跳） | **应用层 TLS**，MACsec 逐跳无法覆盖 |

</div>

> ⚠️ **Real constraints of MACsec**:
> 1. **Both ends must have hardware support**; mixing in old devices degrades the link to cleartext or stops it coming up at all
> 2. **The MTU grows**: SecTAG + ICV add about 32 bytes, so MTU must be increased on MACsec links or large packets get fragmented or dropped
> 3. **Troubleshooting gets harder**: packet captures show no cleartext and can only be decrypted at the ends; when the MKA session misbehaves the link simply appears "completely down", with very few error messages
> 4. **Forwarding performance must be assessed**: a software MACsec implementation can cut throughput to a third or less, so ASIC capability must be confirmed during selection

<div class="zh" markdown="1">

> ⚠️ **MACsec 的真实约束**：
> 1. **必须两端硬件都支持**，混插旧设备时链路会退化为明文或直接起不来
> 2. **MTU 增大**：SecTAG + ICV 增加约 32 字节，跨 MACsec 的链路上必须相应提升 MTU，否则大包被分片或丢弃
> 3. **排障难度上升**：抓包看不到明文，只能在两端解密；且 MKA 会话异常时链路表现为"完全不通"，错误信息很少
> 4. **必须评估转发性能**：软件实现 MACsec 会让吞吐降到 1/3 以下，必须在选型时确认 ASIC 能力

</div>

### Layer 3 Security · 三层安全

Layer 3 security responsibilities differ from Layer 2: **Layer 2 governs "who can see whom inside one subnet", while Layer 3 governs "who can reach where across subnets"**. Layer 3 is where policy is richest and most operable, and it is where the vast majority of enterprise security policy actually lands.

<div class="zh" markdown="1">

三层的安全职责与二层不同：**二层管"同一网段谁能看见谁"，三层管"不同网段谁能到哪去"**。三层是策略最丰富、可运维性最好的一层，也是绝大多数企业安全策略的实际落点。

</div>

#### The Four Enforcement Points of Layer 3 Security · 三层安全的四个作用点

![The four enforcement points of Layer 3 security and where each one sits on the packet path](assets/fig/en10-31-l3-four-enforcement-points.svg)


| Enforcement point | Means | What it blocks |
|--------|------|--------|
| **Filtering along the forwarding path** | Interface ACLs / zoned firewalls / inter-VRF ACLs | Cross-subnet access that is not allowed |
| **Routing-layer control** | Routing policy, prefix filtering, routing authentication, VRF isolation | Routes that should not be learned / forged routes |
| **Identity-to-address mapping** | 802.1X authorization attributes → VLAN/SGT/ACL | Unauthenticated or low-privilege access |
| **Abnormal traffic handling** | NetFlow/flow sampling, RTBH, QoS | DoS, scanning, anomalous outbound connections |

<div class="zh" markdown="1">

| 作用点 | 手段 | 拦什么 |
|--------|------|--------|
| **转发路径上的过滤** | 接口 ACL / 区域防火墙 / VRF 间 ACL | 不允许的跨网段访问 |
| **路由层面的控制** | 路由策略、前缀过滤、路由认证、VRF 隔离 | 不该被学到的路由 / 伪造的路由 |
| **身份到地址的映射** | 802.1X 授权属性 → VLAN/SGT/ACL | 未认证/低权限的接入 |
| **异常流量的处置** | NetFlow/Flow 采样、RTBH、QoS | DoS、扫描、异常外联 |

</div>

#### Where to Deploy ACLs: Where Exactly Should One Policy Live · ACL 部署位置：一条策略应该配在哪

![One intent, five candidate ACL locations: where the policy should actually live, with advantages, costs and a recommendation for each](assets/fig/en10-32-acl-placement.svg)


This is a high-frequency CCDE design question. The same intent ("the office network must not reach the finance servers") can be configured in five places:

<div class="zh" markdown="1">

这是 CCDE 的高频设计题。同一个意图（"办公网不能访问财务服务器"）可以配在五个地方：

</div>

| Location | Advantages | Disadvantages | Recommendation |
|------|------|------|--------|
| **Source access switch (port ACL)** | Traffic is blocked earliest and saves bandwidth | Many devices, scattered policy, hard to audit; ACLs consume TCAM | Only for very specific cases |
| **Source subnet's Layer 3 gateway (SVI/subinterface)** | Centralized and close to the source | Cannot control intra-subnet traffic | ⭐ Commonly used |
| **Between core and aggregation** | Centralized; one configuration covers many subnets | High TCAM pressure on core devices; policy coupled with topology | ⚠️ Use with care |
| **Firewall (between zones)** | Stateful inspection, logging, visibility | Added latency, becomes a single point, traffic must detour | ⭐⭐ Recommended across trust domains |
| **Destination server side (host firewall/micro-segmentation)** | Most precise and aligned with business ownership | Requires host-side cooperation/agents | ⭐⭐ First choice for the data center |

<div class="zh" markdown="1">

| 位置 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **源接入交换机（端口 ACL）** | 流量最早被拦，节省带宽 | 设备多、策略分散、难审计；ACL 下发占 TCAM | 仅用于极精确场景 |
| **源网段的三层网关（SVI/子接口）** | 集中、近源 | 同网段内互访管不到 | ⭐ 常用 |
| **核心/汇聚间** | 集中，一次配置覆盖多网段 | 核心设备 TCAM 压力大；策略与拓扑耦合 | ⚠️ 慎用 |
| **防火墙（zone 间）** | 有状态检查、日志、可视化 | 时延增加、成为单点、流量必须绕行 | ⭐⭐ 推荐用于跨信任域 |
| **目的服务器侧（主机防火墙/微分段）** | 最精确，与业务归属一致 | 需要主机侧配合/agent | ⭐⭐ 数据中心首选 |

</div>

**Design principles**:

<div class="zh" markdown="1">

**设计原则**：

</div>

1. **Put coarse-grained policy at "domain boundaries"** (firewalls, inter-VRF) and fine-grained policy "close to the endpoints" (hosts/ports)
2. **Let each policy take effect in exactly one place**; duplicate configuration produces the troubleshooting classic "I changed it here and it still does not work" (because the other place is also blocking)
3. **Stateless ACLs only do "coarse filtering"**; wherever session state, application identification, or logging is required, use a stateful device

<div class="zh" markdown="1">

1. **粗粒度策略放在"域边界"**（防火墙、VRF 间），细粒度放在"近端"（主机/端口）
2. **同一条策略只在一个地方生效**，重复配置会导致排障时"改了一处还是不通"（因为另一处也拦着）
3. **无状态 ACL 只做"粗筛"**，需要会话状态、应用识别、日志的地方必须用有状态设备

</div>

#### ACL Engineering Details (Only Real Projects Hit These) · ACL 的工程细节（真实项目才会踩到）

| Problem | Symptom | How to handle it |
|------|------|------|
| **TCAM capacity** | With too many ACL entries some are "expanded" into the software path and performance collapses, or the download simply fails | Merge entries, use object-groups; check `show platform ... tcam` before go-live |
| **Implicit deny** | The trailing `deny ip any any` has no `log`, so problems leave no trace | Add `log` or counters to the last line of critical ACLs |
| **Fragmentation** | Non-first fragments carry no L4 information, so `permit tcp ... eq 80` does not match subsequent fragments | Use the `fragments` keyword |
| **`established`** | Only allows return traffic of established connections | Only valid for TCP; UDP/ICMP need separate consideration |
| **ACL and NAT ordering** | ACLs inside and outside the NAT boundary see different addresses (before/after NAT) | State explicitly whether the ACL applies before or after NAT |
| **Interface direction** | `in` and `out` see different addresses and at different moments | Always prefer `in` (before the routing decision, saving forwarding work) |

<div class="zh" markdown="1">

| 问题 | 现象 | 应对 |
|------|------|------|
| **TCAM 容量** | ACL 条目过多时，部分条目被"展开"到软件路径，性能骤降；或直接下发失败 | 合并条目、用 object-group；上线前查 `show platform ... tcam` |
| **隐式 deny** | 末尾 `deny ip any any` 忘了配 `log`，问题无迹可查 | 关键 ACL 的最后一条加 `log` 或计数 |
| **分片** | 非首分片没有 L4 信息，`permit tcp ... eq 80` 不匹配后续分片 | 需要 `fragments` 关键字处理 |
| **established** | 只允许已建立连接的回程 | 仅对 TCP 有效，UDP/ICMP 要单独考虑 |
| **ACL 与 NAT 顺序** | 内外网 ACL 看到的地址不同（NAT 前/后） | 明确"ACL 在 NAT 前还是后生效" |
| **接口方向** | `in` 与 `out` 看到的地址与时机不同 | 一律优先用 `in`（在路由决策前，节省转发） |

</div>

```cfg
! Recommended ACL style: named + commented + counted + explicit logging
ip access-list extended ACL-OFFICE-TO-FIN
 remark === Office network -> finance system: HTTPS to the application only; direct DB access denied ===
 permit tcp 10.10.0.0 0.0.255.255 host 10.30.1.10 eq 443
 deny   tcp 10.10.0.0 0.0.255.255 10.30.0.0 0.0.255.255 eq 3306 log
 deny   ip  10.10.0.0 0.0.255.255 10.30.0.0 0.0.255.255 log
 permit ip  10.10.0.0 0.0.255.255 any
```

<div class="zh" markdown="1">

```cfg
! 推荐的 ACL 写法：命名 + 注释 + 计数 + 明确日志
ip access-list extended ACL-OFFICE-TO-FIN
 remark === 办公网 -> 财务系统：仅允许 HTTPS 访问应用，DB 直连禁止 ===
 permit tcp 10.10.0.0 0.0.255.255 host 10.30.1.10 eq 443
 deny   tcp 10.10.0.0 0.0.255.255 10.30.0.0 0.0.255.255 eq 3306 log
 deny   ip  10.10.0.0 0.0.255.255 10.30.0.0 0.0.255.255 log
 permit ip  10.10.0.0 0.0.255.255 any
```

</div>

> ⚠️ **The governance problem of "ACLs growing forever"**: without lifecycle management an ACL becomes 800 lines in three years and nobody dares delete anything. **The right approach is to automate ACL generation** (generate configuration from a policy management system or change tickets) rather than treating it as hand-written configuration.

<div class="zh" markdown="1">

> ⚠️ **"ACL 越加越长"的治理问题**：ACL 没有生命周期管理，三年后变成 800 行，没人敢删。**正确做法是把 ACL 生成过程自动化**（从策略管理系统/工单生成配置），而不是把它当手写配置。

</div>

#### Routing-Layer Security · 路由层面的安全

| Measure | Goal | Key configuration point |
|------|------|-----------|
| **eBGP prefix filtering (both directions)** | Prevent leaking your own routes / receiving junk routes | `prefix-list` + `route-map` in/out |
| **AS_PATH filtering** | Reject routes containing reserved ASes (anti-injection) | `ip as-path access-list` |
| **`maximum-prefix`** | Prevent routing table explosion | See above |
| **BFD + authentication** | Fast fault detection that cannot be forged | BFD needs authentication too |
| **RTBH (Remotely Triggered Black Hole)** | Drop attack traffic **at the source** during a DoS | See below |

<div class="zh" markdown="1">

| 措施 | 目的 | 关键配置点 |
|------|------|-----------|
| **eBGP 前缀过滤（双向）** | 防自己泄露路由 / 防收到垃圾路由 | `prefix-list` + `route-map` in/out |
| **AS_PATH 过滤** | 拒绝含保留 AS 的路由（防注入） | `ip as-path access-list` |
| **`maximum-prefix`** | 防路由表爆炸 | 见前述 |
| **BFD + 认证** | 快速故障检测且不可伪造 | BFD 也要认证 |
| **RTBH（Remotely Triggered Black Hole）** | DoS 时把攻击流量**丢弃在源头** | 见下 |

</div>

##### RTBH: "Self-Sacrificing" Protection for a Single IP

![Remotely triggered black hole: how a single host is sacrificed at the network entry, what it costs, and where it sits relative to scrubbing](assets/fig/en10-33-rtbh.svg)


<div class="zh" markdown="1">

##### RTBH：一个 IP 的"自杀式"保护

</div>

**The idea**: when a server is under DDoS, make it "disappear from routing" — advertise its /32 with a **`no-export` community** and point that next hop at `null0` on every edge router. Attack traffic is dropped **at the first router it reaches**, protecting both the internal links and the server itself.

<div class="zh" markdown="1">

**思路**：当某个服务器被 DDoS 时，让它"从路由上消失"—— 把它的 /32 路由以 **`no-export` 社区**通告，并在所有边缘路由器的这个下一跳上配 `null0`。攻击流量在**进入网络的第一个路由器**就被丢掉，保护了内部链路和服务器本身。

</div>

```cfg
! Edge router: when BGP receives the RTBH community, rewrite the next hop to discard
router bgp 65000
 ! define the community that triggers discarding
 neighbor 10.0.0.1 send-community
 ! static route pointing at null0
ip route 192.0.2.1 255.255.255.255 Null0
 ! key: accept routes carrying the RTBH community and rewrite the next hop
route-map RTBH-IN permit 10
 match community RTBH
 set ip next-hop 192.0.2.1
```

<div class="zh" markdown="1">

```cfg
! 边缘路由器：BGP 收到 RTBH 社区时，下一跳改为丢弃
router bgp 65000
 ! 定义触发丢弃的社区
 neighbor 10.0.0.1 send-community
 ! 静态路由指向 null0
ip route 192.0.2.1 255.255.255.255 Null0
 ! 关键：接受 RTBH 社区的路由并做下一跳改写
route-map RTBH-IN permit 10
 match community RTBH
 set ip next-hop 192.0.2.1
```

</div>

| Dimension | Description |
|------|------|
| **Advantage** | Attack traffic is dropped at the network entry; internal links and the server are unaffected |
| **Cost** | **That IP's service becomes unavailable to everyone** (including legitimate users) — this is self-inflicted damage |
| **When it fits** | Severe attacks on a single IP/subnet where the business can be sacrificed briefly |
| **When it does not** | The attack targets a large address range, or the business cannot be interrupted |
| **Better alternative** | Traffic scrubbing centers (drop only attack traffic), cloud scrubbing (Anycast diversion) |

<div class="zh" markdown="1">

| 维度 | 说明 |
|------|------|
| **优点** | 攻击流量在网络入口被丢弃，内部链路与服务器不受影响 |
| **代价** | **该 IP 的服务对所有人不可用**（包括正常用户）—— 这是"自损八百" |
| **适用** | 单 IP/单网段的严重攻击，且业务可以短暂牺牲 |
| **不适用** | 攻击目标是大范围地址、或业务不能中断 |
| **更好替代** | 流量清洗中心（只丢攻击流量）、云清洗（Anycast 引流） |

</div>

> 💡 **Design judgment**: RTBH is a **last-resort measure**, not the primary plan. It must work together with scrubbing: divert to scrubbing first, and only RTBH if scrubbing cannot cope or there is no time. A design with RTBH but no scrubbing turns every DDoS problem into "shut down the business".

<div class="zh" markdown="1">

> 💡 **设计判断**：RTBH 是**兜底手段**而不是主方案。它必须与"清洗"配合：先引流清洗，清洗不掉或来不及才 RTBH。一个只有 RTBH 没有清洗的设计，等于把所有 DDoS 问题都变成"关掉业务"。

</div>

#### NetFlow / Telemetry: The Security Searchlight · NetFlow / 遥测：安全的"探照灯"

![Flow telemetry as the security searchlight: the four questions it answers, the export pipeline, the engineering numbers, and what it cannot do](assets/fig/en10-34-netflow.svg)


The item most often cut for cost in Layer 3 security is **visibility**. Without flow data you cannot answer:

<div class="zh" markdown="1">

三层安全里最容易被省钱省掉的是**可见性**。没有流数据，你无法回答：

</div>

- Which internal hosts are talking to suspicious external IPs (are they already compromised?)
- Which hosts are performing lateral scans (are they infected?)
- Who is eating the egress bandwidth (DoS or legitimate business?)
- Did the policy take effect (what are the hit counters?)

<div class="zh" markdown="1">

- 哪些内网主机在与外部可疑 IP 通信（已经被控制了吗？）
- 哪些主机在做横向扫描（中毒了？）
- 出口带宽被谁吃掉了（DoS 还是业务？）
- 策略有没有生效（命中计数是多少？）

</div>

| Means | Sampling rate | Overhead | When to use |
|------|-------|------|------|
| **NetFlow / IPFIX** | Full or 1:1000 | Medium (CPU/bandwidth) | Critical boundaries, DC |
| **sFlow** | 1:1000 – 1:4000 | Low (switch ASIC support) | Network-wide coverage |
| **NetStream / vendor-native** | Configurable | Low–medium | Network-wide coverage |
| **Streaming telemetry (gRPC)** | High-frequency push | Medium | High-volume analysis and DDoS detection |

<div class="zh" markdown="1">

| 手段 | 采样率 | 开销 | 适用 |
|------|-------|------|------|
| **NetFlow / IPFIX** | 全量或 1:1000 | 中（CPU/带宽） | 关键边界、DC |
| **sFlow** | 1:1000 ~ 1:4000 | 低（交换机 ASIC 支持） | 全网覆盖 |
| **NetStream / 厂商原生** | 可配 | 低-中 | 全网覆盖 |
| **流遥测（gRPC/Telemetry）** | 高频推送 | 中 | 大流量分析与 DDoS 检测 |

</div>

> ⚠️ **A practical constraint**: NetFlow significantly increases CPU on high-port-density access layers. **The right approach is tiered sampling**: sFlow at the access layer (low overhead, full coverage), full NetFlow at the boundary and in the DC.

<div class="zh" markdown="1">

> ⚠️ **现实约束**：NetFlow 在高端口密度接入层会显著增加 CPU。**正确做法是分层采样**：接入层 sFlow（低开销全覆盖），边界与 DC 用 NetFlow 全量。

</div>

### Segmentation and Micro-Segmentation · 分段与微分段

#### Why "Segmentation" Is the Highest Leverage in Security Architecture · 为什么"分段"是安全架构的最高杠杆

Every security control faces a cost constraint: **more checkpoints means more security but also more latency and cost**. The value of segmentation is that it **lets you do deep inspection at only a few checkpoints and rely on "cannot reach" everywhere else**.

<div class="zh" markdown="1">

所有安全控制都面临一个成本约束：**检查点越多越安全，但也越慢越贵**。分段的价值就在于：**让你只需要在少数几个检查点上做深度检查，其余地方靠"不通"来保证安全**。

</div>

| No segmentation (flat network) | After segmentation |
|------------------|--------|
| Any device may reach any device | Each zone can reach only what it should |
| Protection has to be installed in front of every device | Only zone boundaries need it |
| One compromise means lateral movement across the network | Compromise is confined to one segment |
| There is no way to establish a "normal traffic baseline" | Per-segment traffic patterns are clear, so anomalies are easy to spot |

<div class="zh" markdown="1">

| 不分段（扁平网络） | 分段后 |
|------------------|--------|
| 每台设备都可能访问任何设备 | 每个区只能访问该访问的 |
| 需要在每台设备前装防护 | 只需要在区边界装 |
| 一处沦陷即横向移动全网 | 沦陷局限于一个段 |
| 无法判断"正常流量基线" | 每段流量模式清晰，异常易发现 |

</div>

#### The Four Technical Layers of Segmentation · 分段的四个技术层次

![The four technical layers of segmentation compared by granularity, isolation strength and scalability, and why the layers stack instead of substituting for each other](assets/fig/en10-35-segmentation-layers.svg)


| Layer | Technology | Granularity | Isolation strength | Scalability |
|------|------|------|---------|---------|
| **Physical isolation** | Separate devices/cables | Highest | Strongest | Poor (expensive) |
| **Logical isolation (L2/L3)** | VLAN + subnet + VRF | Subnet | Strong (no route = no reachability) | Good |
| **Stateful inspection** | Firewall zones, inter-VRF firewalls | Subnet/subnet pair | Strong (controllable and auditable) | Medium (performance bottleneck) |
| **Identity-level isolation** | **SGT/TrustSec, micro-segmentation (EPG/security groups)** | User/host/application | Strong (fine-grained) | Good (centralized policy) |

<div class="zh" markdown="1">

| 层次 | 技术 | 粒度 | 隔离强度 | 可扩展性 |
|------|------|------|---------|---------|
| **物理隔离** | 独立设备/独立线缆 | 最高 | 最强 | 差（成本高） |
| **逻辑隔离（L2/L3）** | VLAN + 子网 + VRF | 网段 | 强（无路由即不通） | 好 |
| **有状态检查** | 防火墙 zone、VRF 间防火墙 | 网段/网段对 | 强（可控且可审计） | 中（性能瓶颈） |
| **身份级隔离** | **SGT/TrustSec、微分段（EPG/安全组）** | 用户/主机/应用 | 强（细粒度） | 好（策略集中） |

</div>

#### SGT (Security Group Tag) and TrustSec · SGT（Security Group Tag）与 TrustSec

![Security group tags: identity becomes a label, the label becomes a policy matrix, and the three ways to carry it across the network](assets/fig/en10-36-sgt-trustsec.svg)


**Core idea**: decouple "who can access whom" from **IP addresses** and bind it to **identity tags**. When an endpoint authenticates, ISE assigns an SGT (e.g. employee = 10, guest = 20, printer = 30), and switches/firewalls permit or deny according to the **matrix** between SGTs.

<div class="zh" markdown="1">

**核心思想**：把"谁能访问谁"从**IP 地址**解耦到**身份标签**。终端认证时由 ISE 分配一个 SGT（如"员工=10、访客=20、打印机=30"），交换机/防火墙按 SGT 之间的**矩阵**放行或拒绝。

</div>

| Advantage | Description |
|------|------|
| **Address independent** | Users change IP, change VLAN, roam — the tag and the policy stay the same |
| **Centralized policy** | One matrix (N×N) network-wide instead of N ACLs per device |
| **Orchestratable** | A new application means changing the matrix, not ACLs across the network |

<div class="zh" markdown="1">

| 优势 | 说明 |
|------|------|
| **地址无关** | 用户换 IP、换 VLAN、漫游，标签不变，策略不变 |
| **策略集中** | 全网一张矩阵（N×N），而不是每台设备 N 条 ACL |
| **可编排** | 新应用上线只改矩阵，不用全网改 ACL |

</div>

**The three ways to implement SGT**:

<div class="zh" markdown="1">

**SGT 的三种实施方式**：

</div>

| Method | Mechanism | Coverage | Limitation |
|------|------|---------|------|
| **Inline tagging** | Adds a CMD (32-bit) field to the Ethernet frame | Layer 2 domain | Requires hardware support; the tag is lost across Layer 3 |
| **SXP (SGT Exchange Protocol)** | Synchronizes IP-to-SGT mappings to devices without inline support | Across devices | Learning delay in the mapping, and **IP reuse (DHCP reassignment) causes errors** |
| **Static mapping** | Manually configure IP/subnet → SGT | Servers/fixed devices | Maintenance cost; changes when addresses change |

<div class="zh" markdown="1">

| 方式 | 机制 | 覆盖范围 | 限制 |
|------|------|---------|------|
| **Inline Tagging（内联标记）** | 以太网帧里加 CMD（32 位）字段 | 二层域 | 需硬件支持；跨三层会丢标 |
| **SXP（SGT Exchange Protocol）** | 用 SXP 把 IP-SGT 映射同步给不支持内联的设备 | 跨设备 | 映射有学习时延，**IP 复用（DHCP 重分配）时会出错** |
| **静态映射** | 手工配 IP/subnet → SGT | 服务器/固定设备 | 维护成本，地址变更要改 |

</div>

> ⚠️ **"SGT can replace the firewall" is the most common misconception**
>
> SGT only performs **authorization** (permit/deny); it does **no threat inspection**. An endpoint tagged "employee" that has already been compromised still accesses everything employees can access — SGT cannot help with that.
>
> The correct relationship is **layered**:
> ```
> 802.1X → confirm identity (who you are)
>   ↓
> SGT    → grant permission (where you may go)      ← authorization layer
>   ↓
> Firewall/IPS → inspect content (what you bring in) ← inspection layer
>   ↓
> Micro-segmentation/host protection → prevent lateral movement (where you spread) ← isolation layer
> ```
> **No layer can replace another.** Compressing all four into "we deployed SGT, so we are secure" means only authorization was done and inspection was skipped.

<div class="zh" markdown="1">

> ⚠️ **"SGT 能替代防火墙"是最常见的误解**
>
> SGT 只做**授权**（允许/拒绝），**不做威胁检查**。一个被授予"员工"标签但已被入侵的终端，仍然会以"员工"权限访问所有员工可访问的资源 —— SGT 对此无能为力。
>
> 正确的关系是**分层**：
> ```
> 802.1X → 确认身份（你是谁）
>   ↓
> SGT   → 授予权限（你能到哪）        ← 授权层
>   ↓
> 防火墙/IPS → 检查内容（你带进来什么）  ← 检查层
>   ↓
> 微分段/主机防护 → 防止横向（你扩散到哪）← 隔离层
> ```
> **任何一层都不能替代其他层**。把四层压成"上了 SGT 就安全了"，就等于只做了授权没做检查。

</div>

#### The Three Routes to Data Center Micro-Segmentation · 数据中心微分段的三条路线

![Three routes to data centre micro-segmentation - fabric, host, and hybrid - and how to choose between them](assets/fig/en10-37-dc-microsegmentation.svg)


| Route | Mechanism | When it fits | Cost |
|------|------|------|------|
| **Network side (EPG/ACI, VXLAN + security groups)** | Policy enforced in the fabric | New DCs, private cloud | Strongly tied to a vendor architecture; high migration cost |
| **Host side (agent / eBPF / container CNI)** | Policy enforced in the OS kernel | Virtualization/container-heavy, hybrid cloud | Requires agents; does not cover bare metal or network devices |
| **Hybrid** (coarse in the network, fine on hosts) | East-west entry coarsely segmented in the fabric, finely segmented inside the host | **Most realistic** | Requires a mapping between two policy systems |

<div class="zh" markdown="1">

| 路线 | 机制 | 适用 | 代价 |
|------|------|------|------|
| **网络侧（EPG/ACI、VXLAN + 安全组）** | 策略在 fabric 上执行 | 新建 DC、私有云 | 强绑定厂商架构，迁移成本高 |
| **主机侧（agent / eBPF / 容器 CNI）** | 策略在操作系统内核执行 | 虚拟化/容器密集、混合云 | 需装 agent，覆盖不到裸金属/网络设备 |
| **混合**（网络管粗、主机管细） | 东西向入口在 fabric 粗分，主机内细分 | **最现实** | 需要两套策略体系的映射 |

</div>

> 💡 **Design advice**: **the bulk of east-west traffic is inside the data center**. If all your security investment goes into north-south traffic (egress firewalls) while the inside of the DC is one big VLAN, then the real exposure is exactly where you cannot see it.

<div class="zh" markdown="1">

> 💡 **设计建议**：东西向流量的**大头在数据中心内部**。如果你的安全投入全在南北向（出口防火墙），而 DC 内部是一个大 VLAN，那么真正的风险敞口在你看不见的地方。

</div>

#### The Relationship Between VRFs and Security Domains (Do Not Confuse Them) · VRF 与安全域的关系（别混淆）

![VLAN, VRF, zone and SGT are four different concepts; what each one isolates, and why a VRF is not a security domain](assets/fig/en10-38-vrf-vs-security-domain.svg)


| Concept | Purpose | Relationship to security |
|------|------|------------|
| **VLAN / subnet** | Layer 2 broadcast domain partitioning | Basic isolation, but needs Layer 3 policy as a supplement |
| **VRF** | Routing table isolation (**address spaces may overlap**) | Strong isolation: with no inter-VRF routing there is no connectivity at all |
| **Zone (firewall)** | Policy boundary (stateful) | Isolation with inspection capability |
| **SGT** | Identity tag | Authorization independent of addresses |

<div class="zh" markdown="1">

| 概念 | 目的 | 与安全的关系 |
|------|------|------------|
| **VLAN / 子网** | 二层广播域划分 | 基础隔离，但需要三层策略补充 |
| **VRF** | 路由表隔离（**地址空间可以重叠**） | 强隔离：没有 VRF 间路由就完全不通 |
| **Zone（防火墙）** | 策略边界（有状态） | 有检查能力的隔离 |
| **SGT** | 身份标签 | 与地址无关的授权 |

</div>

**Key distinction**: **a VRF is routing isolation, not security isolation**. Many designs treat "putting businesses in different VRFs" as a security measure, but if the VRFs exchange `route-target`s or point static routes at each other on the core, the isolation does not exist. **Security is about "policy" (who is allowed where), not about "partitioning" (how the tables are split).**

<div class="zh" markdown="1">

**关键区分**：**VRF 是路由隔离，不是安全隔离**。很多设计把"业务放不同 VRF"当成安全措施，但如果 VRF 之间在核心上做了 `route-target` 互导或静态路由互指，隔离就等于不存在。**安全的本质是"策略"（谁被允许到哪里），不是"分区"（怎么划表）。**

</div>

> 🔥 **Case: the "fake security" of VRF isolation**
>
> **Scenario**: a bank split its network into "office VRF", "production VRF", and "partner VRF" and claimed "the three domains are fully isolated".
>
> **What the audit found**: between the production VRF and the office VRF, the core switch had `ip route vrf PROD 0.0.0.0 0.0.0.0 <office VRF's SVI>` — because years earlier "operations needed to SSH from the office area to production devices", and a default route was added to make SSH work.
>
> **Consequence**: any PC in the office VRF could reach every address in the production VRF (it only had to know the route). On paper the "isolation" existed in the design document; in the configuration it was fake.

<div class="zh" markdown="1">

> 🔥 **案例：VRF 隔离的"假安全"**
>
> **场景**：某银行把网络分为"办公 VRF"、"生产 VRF"、"外联 VRF"，宣称"三个域完全隔离"。
>
> **审计发现**：生产 VRF 与办公 VRF 之间，在核心交换机上配了 `ip route vrf PROD 0.0.0.0 0.0.0.0 <办公VRF的SVI>` —— 因为当年"运维需要从办公区 SSH 到生产设备"，为了让 SSH 通，直接加了一条默认路由。
>
> **后果**：办公 VRF 里任意一台 PC 都能直接访问生产 VRF 的所有地址（只是需要知道路由）。"隔离"在设计文档上是存在的，在配置上是假的。
>
> **为什么这种问题普遍**：因为**"临时打通"比"建设备管通道"便宜太多**。一条静态路由 5 分钟，建一个堡垒机 2 周。
>
> **设计层面的对策**（这三条必须在架构里写死）：
> 1. **VRF 间禁止任何直接路由**，需要跨域访问一律经过**有状态设备**（防火墙 / 堡垒机）
> 2. **配置合规检查项**：自动化巡检"是否存在跨 VRF 的静态路由/路由泄露"，发现即告警
> 3. **运维通道要预先建设**：项目立项时就把"跨域运维通道"作为交付物，否则实施阶段一定会走捷径

</div>

### Network Overlay and Remote Access · 网络覆盖和远程访问

#### IPsec: Five Decisions You Must Settle First · IPsec：必须先想清楚的五个选择

![The five IPsec decisions that must be settled before deployment, and the protocol-mode matrix that explains them](assets/fig/en10-39-ipsec-five-decisions.svg)


IPsec is not a "turn it on and forget it" feature; it has five parameters that must be decided explicitly. **Getting these five wrong usually does not make you "insecure" — it makes the tunnel "not work" or the performance collapse.**

<div class="zh" markdown="1">

IPsec 不是"打开就好"的功能，它有五个必须显式决策的参数。**这五个决策如果做错，通常不是"不安全"，而是"不通"或"性能崩"**。

</div>

| Decision | Options | Recommended | Key consideration |
|--------|------|------|---------|
| **① Protocol** | AH / ESP / **AH+ESP** | **ESP** | AH does not pass NAT and does not encrypt; there is almost no scenario for it |
| **② Mode** | Transport / **Tunnel** | **Tunnel** (site-to-site) | Transport mode only fits "host to host with no NAT in between" |
| **③ IKE version** | IKEv1 / **IKEv2** | **IKEv2** | IKEv2 supports MOBIKE, needs fewer round trips, and has clearer error codes |
| **④ Crypto suite** | DES/3DES/AES-CBC/AES-GCM | **AES-256-GCM** (or AES-CBC + SHA-256) | GCM provides encryption and authentication together, with better performance |
| **⑤ PFS** | On / off | **On** (DH group ≥ 14) | With PFS off, a master key leak decrypts historical traffic |

<div class="zh" markdown="1">

| 决策点 | 选项 | 推荐 | 关键考虑 |
|--------|------|------|---------|
| **① 协议** | AH / ESP / **AH+ESP** | **ESP** | AH 不 NAT 穿透、不加密，几乎无场景 |
| **② 模式** | 传输模式 / **隧道模式** | **隧道模式**（站点间） | 传输模式只在"主机到主机、且中间无 NAT"时 |
| **③ IKE 版本** | IKEv1 / **IKEv2** | **IKEv2** | IKEv2 支持 MOBIKE、更少的往返、更清晰的错误码 |
| **④ 加密套件** | DES/3DES/AES-CBC/AES-GCM | **AES-256-GCM**（或 AES-CBC + SHA-256） | GCM 同时提供加密与认证，性能更好 |
| **⑤ PFS** | 开 / 关 | **开**（DH group ≥ 14） | 关掉 PFS 时，主密钥泄露会导致历史流量被解密 |

</div>

**The relationship between protocol and mode**:

<div class="zh" markdown="1">

**协议与模式的关系**：

</div>

| Combination | Encrypts | Authenticates | Keeps original IP header | Passes NAT | Use |
|------|------|------|-------------|--------|------|
| **AH transport** | ❌ | ✅ | ✅ | ❌ | Almost none (historical) |
| **AH tunnel** | ❌ | ✅ | ✅ | ❌ | Almost none |
| **ESP transport** | ✅ | ✅ | ✅ | ❌ (unless NAT-T) | Host to host (over GRE/L2TP) |
| **ESP tunnel** | ✅ | ✅ | ❌ (new header) | ✅ (NAT-T) | **Site-to-site and remote access: the only mainstream choice** |

<div class="zh" markdown="1">

| 组合 | 加密 | 认证 | 保留原始 IP 头 | 过 NAT | 用途 |
|------|------|------|-------------|--------|------|
| **AH 传输** | ❌ | ✅ | ✅ | ❌ | 几乎无（仅历史） |
| **AH 隧道** | ❌ | ✅ | ✅ | ❌ | 几乎无 |
| **ESP 传输** | ✅ | ✅ | ✅ | ❌（除非 NAT-T） | 主机到主机（GRE/L2TP 之上） |
| **ESP 隧道** | ✅ | ✅ | ❌（新头） | ✅（NAT-T） | **站点间、远程访问：唯一主流选择** |

</div>

```cfg
! IKEv2 + AES-GCM (recommended modern configuration)
crypto ikev2 proposal IKEv2-PROP
 encryption aes-cbc-256
 integrity sha256
 group 19                  ! ECP256, stronger than MODP 2048 and cheaper on CPU
crypto ikev2 policy IKEv2-POL
 proposal IKEv2-PROP
crypto ikev2 keyring KR-SPOKES
 peer SPOKE
  address 0.0.0.0 0.0.0.0
  pre-shared-key <strong-PSK>
crypto ikev2 profile IKEv2-PROF
 match identity remote address 0.0.0.0 0.0.0.0
 identity local address 203.0.113.1
 authentication remote pre-share
 authentication local pre-share
 keyring local KR-SPOKES
 dpd 30 5 on-idle
 nat keepalive 20

crypto ipsec transform-set TS-ESP esp-gcm 256
 mode tunnel

crypto ipsec profile IPSEC-PROF
 set transform-set TS-ESP
 set ikev2-profile IKEv2-PROF
 set pfs group19
```

<div class="zh" markdown="1">

```cfg
! IKEv2 + AES-GCM（推荐现代配置）
crypto ikev2 proposal IKEv2-PROP
 encryption aes-cbc-256
 integrity sha256
 group 19                  ! ECP256，比 MODP 2048 更强且更省 CPU
crypto ikev2 policy IKEv2-POL
 proposal IKEv2-PROP
crypto ikev2 keyring KR-SPOKES
 peer SPOKE
  address 0.0.0.0 0.0.0.0
  pre-shared-key <强PSK>
crypto ikev2 profile IKEv2-PROF
 match identity remote address 0.0.0.0 0.0.0.0
 identity local address 203.0.113.1
 authentication remote pre-share
 authentication local pre-share
 keyring local KR-SPOKES
 dpd 30 5 on-idle
 nat keepalive 20

crypto ipsec transform-set TS-ESP esp-gcm 256
 mode tunnel

crypto ipsec profile IPSEC-PROF
 set transform-set TS-ESP
 set ikev2-profile IKEv2-PROF
 set pfs group19
```

</div>

#### MTU / MSS: IPsec's Classic "Ping Works but the Business Does Not" · MTU / MSS：IPsec 部署最经典的"能 ping 通但业务不通"

![Why IPsec breaks large packets: the encapsulation arithmetic, the four symptoms it produces, and the fix order led by MSS clamping](assets/fig/en10-40-mtu-mss.svg)


**Why it is bound to happen**:

<div class="zh" markdown="1">

**为什么必出问题**：

</div>

```
Original packet:  IP(20) + TCP(20) + Data(1460) = 1500
After IPsec:      IP(20) + ESP(8) + IV(16) + original(1500) + ESP trailer(2) + ICV(16) ≈ 1562
                                    ↑
                          exceeds the 1500 MTU → fragment or drop
```

<div class="zh" markdown="1">

```
原始包：      IP(20) + TCP(20) + Data(1460) = 1500
IPsec 封装：  IP(20) + ESP(8) + IV(16) + 原包(1500) + ESP尾(2) + ICV(16) ≈ 1562
                                    ↑
                          超出 1500 MTU → 分片 或 丢弃
```

</div>

| Symptom | Cause | Signature |
|------|------|------|
| `ping` works, web pages do not open | The TCP handshake (small packets) passes; data (large packets) is dropped | **The most classic MTU problem** |
| SSH login works, then hangs after a large `ls` | Large packets dropped | Same as above |
| HTTPS handshake succeeds, download sticks at 0% | The TLS certificate/handshake is small, the data transfer is large | Same as above |
| Some sites work, others do not | Path MTU differs | Confirm path by path |

<div class="zh" markdown="1">

| 现象 | 原因 | 特征 |
|------|------|------|
| `ping` 通，网页打不开 | TCP 握手（小包）通，数据（大包）被丢 | **最经典的 MTU 问题** |
| SSH 能登录，`ls` 大量输出后卡死 | 大包被丢 | 同上 |
| HTTPS 握手成功，下载卡在 0% | TLS 证书/握手小，数据传输大 | 同上 |
| 某些站点正常，某些站点不通 | 路径 MTU 不同 | 需逐路径确认 |

</div>

**The correct order of fixes**:

<div class="zh" markdown="1">

**修复的正确顺序**：

</div>

```cfg
! 1) Lower the tunnel interface MTU (leave room for the encapsulation overhead)
interface Tunnel0
 ip mtu 1400
 ip tcp adjust-mss 1360      ! Key: let TCP negotiate the MSS and avoid fragmentation
```

<div class="zh" markdown="1">

```cfg
! 1) 隧道接口降低 MTU（留足封装开销）
interface Tunnel0
 ip mtu 1400
 ip tcp adjust-mss 1360      ! 关键：让 TCP 协商 MSS，避免分片
```

</div>

| Measure | Effect | Is it enough |
|------|------|---------|
| `ip mtu 1400` | The tunnel interface no longer emits packets larger than 1400 | Not enough (hosts may still send 1500) |
| **`ip tcp adjust-mss 1360`** | Rewrites the MSS in SYN/SYN-ACK so TCP shrinks proactively | **The key measure** |
| Relying on PMTUD | Depends on ICMP "fragmentation needed" messages | **Unreliable** (many firewalls drop ICMP) |
| DF bit 0 (allow fragmentation) | Lets routers fragment | Poor performance; security devices may drop the fragments |

<div class="zh" markdown="1">

| 措施 | 作用 | 是否足够 |
|------|------|---------|
| `ip mtu 1400` | 隧道接口不再发出 >1400 的包 | 不够（主机仍可能发 1500） |
| **`ip tcp adjust-mss 1360`** | 在 SYN/SYN-ACK 上改写 MSS，让 TCP 主动减小 | **关键措施** |
| 依赖 PMTUD | 靠 ICMP "需要分片" 报文 | **不可靠**（很多防火墙丢 ICMP） |
| DF 位置 0（允许分片） | 让路由器分片 | 性能差、可能被安全设备丢 |

</div>

> 🔥 **Case: after IPsec went live, "the OA system logs in but cannot submit forms"**
>
> **Symptom**: a branch reached the headquarters OA system over IPsec. The login page worked, the list pages worked, but **clicking Submit spun forever and eventually timed out**. The same laptop over 4G (without IPsec) worked fine.
>
> **Troubleshooting**: `ping -l 1400` failed and `ping -l 1200` succeeded → an MTU problem. But `ip mtu 1400` was already in the configuration.
>
> **Root cause**: `ip mtu` applies to the **outbound direction of the tunnel interface** and only affects "packets the router itself emits". Here the traffic was **PC (1500) → branch router → tunnel**, so the branch router needed to fragment during encapsulation because of the MTU limit — but `crypto ipsec df-bit clear` was not enabled, and a device in the path was dropping ICMP, so PMTUD was broken and the large packets were silently dropped.
>
> **Why "login works but submit fails"**: the login request parameters are small (a few hundred bytes); the submit form contains attachments/long text (several KB), which exceed the MSS and need fragmentation. TCP had already negotiated its segment size based on 1500, and the intermediate device dropped rather than fragmented.
>
> **The final fix**:
> ```cfg
> interface Tunnel0
>  ip mtu 1400
>  ip tcp adjust-mss 1360        ! this line is the real fix
> ```
> At the same time `net.ipv4.tcp_mtu_probing=1` was enabled on the headquarters servers as a fallback.
>
> **Design-level lessons**:
> 1. **Any technology that introduces encapsulation (IPsec, GRE, VXLAN, MPLS, PPPoE) requires the MTU/MSS calculation to be written explicitly into the design document** — "it pings after configuration" is not acceptance.
> 2. **Acceptance testing must include large-packet tests** (`ping -l 1400 -f`, large file uploads, long SQL queries). Testing only ping and the HTTP home page misses 90% of MTU problems.
> 3. **PMTUD generally fails in real networks — do not rely on it.**

<div class="zh" markdown="1">

> 🔥 **案例：IPsec 上线后"OA 系统能登录但不能提交表单"**
>
> **现象**：分支通过 IPsec 访问总部 OA。登录页面正常、列表正常，**点击"提交"按钮后一直转圈，最终超时**。同一台电脑走 4G（不经 IPsec）就正常。
>
> **排查过程**：`ping -l 1400` 失败，`ping -l 1200` 成功 → 确认 MTU 问题。但配置里已经写了 `ip mtu 1400`。
>
> **根因**：`ip mtu` 作用在**隧道接口出方向**，只影响"从路由器发出的包"。而这里的流量是 **PC(1500) → 分支路由器 → 隧道**，分支路由器在封装时会因为超 MTU 而需要分片 —— 但配置了 `crypto ipsec df-bit clear` 没开，且路径上有设备丢 ICMP，导致 PMTUD 失效，大包被静默丢弃。
>
> **为什么"登录正常但提交失败"**：登录请求的参数小（几百字节），提交表单包含附件/长文本（几 KB），超过 MSS 后需要分片。TCP 在 MSS 协商时已经按 1500 算好了段大小，中间设备不分片即丢。
>
> **最终修复**：
> ```cfg
> interface Tunnel0
>  ip mtu 1400
>  ip tcp adjust-mss 1360        ! 这一条才是真正的修复
> ```
> 同时把总部侧服务器的 `net.ipv4.tcp_mtu_probing=1` 打开作为兜底。
>
> **设计层面的教训**：
> 1. **凡是引入封装的技术（IPsec、GRE、VXLAN、MPLS、PPPoE），MTU/MSS 必须在设计文档里显式列出计算过程**，不能"配完能 ping 通就算完"
> 2. **验收测试必须包含大包测试**（`ping -l 1400 -f`、大文件上传、长 SQL 查询），只测 ping 和 HTTP 首页会漏掉 90% 的 MTU 问题
> 3. **PMTUD 在真实网络中普遍失效**，不要依赖它

</div>

#### Three Architecture Choices for Site-to-Site VPN · 站点到站点 VPN 的三种架构选型

![Four site-to-site VPN architectures - traditional point-to-point IPsec, DMVPN, FlexVPN and GET VPN - and the three DMVPN phases that decide where spoke traffic goes](assets/fig/en10-41-vpn-architectures.svg)


| Architecture | Topology | Encryption | Scalability | Fit |
|------|------|------|--------|------|
| **Traditional point-to-point IPsec** | Full mesh or hub-and-spoke, statically configured | One tunnel per pair | **Poor** (N sites need N² or N configurations) | Few sites (< 10), stable topology |
| **DMVPN** | Hub-and-spoke + **mGRE + NHRP** | Built dynamically per pair | Good (configure the hub once) | Medium/large enterprise WAN that needs spoke-to-spoke |
| **FlexVPN** | A unified framework based on IKEv2 | Built dynamically per pair | Good, and it unifies site-to-site with remote access | New builds; the most complete feature set |
| **GET VPN** | **Group Encrypted Transport**, no tunnels | Group key, one copy network-wide | Excellent (almost zero overhead on a carrier MPLS) | An existing MPLS/private WAN where you want encryption without tunnels |

<div class="zh" markdown="1">

| 架构 | 拓扑 | 加密 | 扩展性 | 适用 |
|------|------|------|--------|------|
| **传统点对点 IPsec** | 全互连或 Hub-Spoke，静态配置 | 每对一条隧道 | **差**（N 个站点需 N² 或 N 条配置） | 站点少（< 10）、拓扑稳定 |
| **DMVPN** | Hub-Spoke + **mGRE + NHRP** | 每对动态建立 | 好（Hub 配置一次） | 中大型企业 WAN，需要 Spoke 直连 |
| **FlexVPN** | 基于 IKEv2 的统一框架 | 每对动态 | 好，且统一了站点间与远程访问 | 新建网络，功能最全 |
| **GET VPN** | **Group Encrypted Transport**，无隧道 | 组密钥，全网一份 | 极好（运营商 MPLS 上几乎零开销） | 已有 MPLS/私有 WAN，只要加密不要隧道 |

</div>

##### DMVPN: Why It Solves "Spoke-to-Spoke Direct Connectivity"

<div class="zh" markdown="1">

##### DMVPN：为什么它解决了"Spoke 直连"问题

</div>

| Component | Function |
|------|------|
| **mGRE (multipoint GRE)** | One Tunnel interface can map to many peers (no one-to-one requirement) |
| **NHRP** | "ARP for tunnels": spokes register their public addresses with the hub; to reach another spoke they ask the hub for its public address |
| **IPsec** | Encryption on top of mGRE (or combined with GRE as an IPsec profile) |
| **Routing protocol** | Spokes exchange routes over the tunnels (typically EIGRP/OSPF/BGP) |

<div class="zh" markdown="1">

| 组件 | 作用 |
|------|------|
| **mGRE（多点 GRE）** | 一个 Tunnel 接口可以对应多个对端（不需要一对一） |
| **NHRP** | 类似"隧道的 ARP"：Spoke 向 Hub 注册公网地址；要访问另一个 Spoke 时向 Hub 查询对方的公网地址 |
| **IPsec** | 在 mGRE 之上加密（或与 GRE 结合为 IPsec profile） |
| **路由协议** | Spoke 之间通过隧道交换路由（通常 EIGRP/OSPF/BGP） |

</div>

**The three phases of DMVPN**:

<div class="zh" markdown="1">

**DMVPN 的三个阶段**：

</div>

| Phase | Characteristics | The hub's role |
|------|------|-----------|
| **Phase 1** | Spokes can **only reach each other through the hub** (the hub is the only NBMA next hop) | Forwards all spoke-to-spoke traffic |
| **Phase 2** | Spokes **build tunnels directly** between themselves (on the same subnet) | Only does NHRP registration and initial resolution |
| **Phase 3** | Spokes connect directly but **use the hub's address as the next hop** (NHRP shortcut) | Forwards routes while traffic goes direct; **supports spoke summarization** |

<div class="zh" markdown="1">

| 阶段 | 特点 | Hub 的角色 |
|------|------|-----------|
| **Phase 1** | Spoke 之间**只能经 Hub**（Hub 是唯一 NBMA 下一跳） | 转发所有 Spoke 间流量 |
| **Phase 2** | Spoke 之间**直接建隧道**（同一子网） | 只做 NHRP 注册与初始解析 |
| **Phase 3** | Spoke 间直连但**用 Hub 的地址做下一跳**（NHRP shortcut） | 转发路由，流量可直达；**支持 Spoke 汇总** |

</div>

**The key difference between Phase 2 and Phase 3**:

<div class="zh" markdown="1">

**Phase 2 与 Phase 3 的关键差异**：

</div>

| Dimension | Phase 2 | Phase 3 |
|------|---------|---------|
| Spoke-to-spoke traffic | Direct | Direct (first flow via the hub) |
| **Spoke routing table** | Needs **every spoke's detail routes** | Only **summaries/the hub default route** |
| Large-scale scaling | ❌ Detail routes explode | ✅ Recommended |
| Spoke hardware requirement | Must handle network-wide detail | Low |

<div class="zh" markdown="1">

| 维度 | Phase 2 | Phase 3 |
|------|---------|---------|
| Spoke 间流量 | 直连 | 直连（首次经 Hub） |
| **Spoke 路由表** | 需要**所有 Spoke 的明细路由** | 只需**汇总/Hub 默认路由** |
| 大规模扩展 | ❌ 明细路由爆炸 | ✅ 推荐 |
| Spoke 硬件要求 | 需要能承受全网明细 | 低 |

</div>

> ⚠️ **Three high-frequency DMVPN traps**:
> 1. **The hub's `ip nhrp redirect` / the spoke's `ip nhrp shortcut`** are the core of Phase 3; leave one out and it degrades to Phase 2.
> 2. **When spokes use dynamic public IPs** you must configure `ip nhrp registration no-unique` and a correct holdtime, otherwise stale mappings remain on the hub after an address change.
> 3. **Split horizon of the routing protocol over mGRE**: by default EIGRP/OSPF on the hub will not send Spoke A's routes back out of the same interface toward Spoke B (split horizon). You must disable it explicitly (`no ip split-horizon`, or use `ip ospf network point-to-multipoint`, or broadcast plus a DR design).
> 🔥 **Case: DMVPN spokes detoured through the hub and saturated its bandwidth**
>
> **Background**: an enterprise ran 180 branches on DMVPN (designed as Phase 3), with the hub at headquarters and a 200 Mbps egress.
>
> **Symptom**: at month-end, when branches uploaded reports, the headquarters egress was saturated and every branch was extremely slow toward headquarters; but **video conferencing between branches (which was supposed to be direct) was also choppy**.
>
> **Troubleshooting**: on the spokes, `show dmvpn` showed **only IKE/NHRP state and no NHRP cache entries**; `show ip nhrp` showed the resolved next hop between spokes was **the hub's tunnel address** rather than the peer's public address.
>
> **Root cause**: when the configuration was upgraded from Phase 2 to Phase 3, `ip nhrp redirect` was added on the hub, but **`ip nhrp shortcut` was missing on the spokes** (the template was rolled out in two batches and the second batch used the old template). So all spoke-to-spoke traffic still transited the hub — and because spokes only learned summary routes, the problem was hidden: **it "worked", so nobody noticed it was taking the wrong path**.
>
> **Why "video conferencing was choppy too"**: all inter-branch video detoured through headquarters, making the headquarters egress the bottleneck. By design that traffic should have gone direct spoke-to-spoke.
>
> **Fix and verification**:
> ```cfg
> ! Spoke
> interface Tunnel0
>  ip nhrp shortcut              ! the key line
>  ip nhrp redirect
> ! Verify: access a peer spoke, then check the NHRP cache
> show ip nhrp                  ! there should be a "dynamic" entry whose NBMA is the peer's public IP
> ```
>
> **Design-level lessons**:
> 1. **"It works" is not an acceptance criterion.** You must verify that the **traffic path** matches the design (traceroute, NHRP cache, interface counters).
> 2. **Configuration templates must carry version numbers and consistency validation** (the hub and spoke configurations are a "pair"; missing half is a silent degradation).
> 3. **The converged path must be monitored** (e.g. "is inter-spoke traffic still going through the hub" should be a routine check).

<div class="zh" markdown="1">

> ⚠️ **DMVPN 的三个高频坑**：
> 1. **Hub 的 `ip nhrp redirect` / Spoke 的 `ip nhrp shortcut`** 是 Phase 3 的核心，漏配就退化成 Phase 2
> 2. **Spoke 使用动态公网 IP** 时，必须配 `ip nhrp registration no-unique` 和正确的 holdtime，否则地址变更后 Hub 上残留旧映射
> 3. **路由协议在 mGRE 上的 split-horizon**：EIGRP/OSPF 默认在 Hub 上不会把 Spoke A 的路由从同一接口发回给 Spoke B（水平分割），必须显式关闭（`no ip split-horizon` / OSPF 用 point-to-multipoint 或 `ip ospf network broadcast` + DR 设计）
> 🔥 **案例：DMVPN Spoke 之间绕行 Hub，带宽打满**
>
> **背景**：某企业 180 个分支用 DMVPN（设计为 Phase 3），Hub 在总部，出口 200 Mbps。
>
> **现象**：每月月末各分支上传报表时，总部出口带宽打满，所有分支访问总部系统极慢；但分支之间的视频会议（本该直连）也卡顿。
>
> **排查**：在 Spoke 上看 `show dmvpn`，**只有 IKE/NHRP 状态，没有 NHRP 缓存条目**；`show ip nhrp` 显示 Spoke 之间解析出来的下一跳是 **Hub 的隧道地址**，而不是对方的公网地址。
>
> **根因**：配置从 Phase 2 升级到 Phase 3 时，Hub 上加了 `ip nhrp redirect`，但 **Spoke 上的 `ip nhrp shortcut` 漏了**（模板分两批下发，第二批用的旧模板）。结果所有 Spoke 间流量仍然经 Hub 中转 —— 而且因为 Spoke 只学到汇总路由，问题被掩盖了：**"能通"所以没人发现"走错了路"**。
>
> **为什么"视频会议也卡"**：分支间视频全部绕行总部，总部出口成了瓶颈。而在设计预期里，这部分流量应该走 Spoke 直连。
>
> **修复与验证**：
> ```cfg
> ! Spoke
> interface Tunnel0
>  ip nhrp shortcut              ! 关键
>  ip nhrp redirect
> ! 验证：访问对端 Spoke 后检查 NHRP 缓存
> show ip nhrp                  ! 应出现 type "dynamic" 且 NBMA 为对端公网 IP
> ```
>
> **设计层面的教训**：
> 1. **"能通"不是验收标准**。必须验证**流量路径**是否符合设计（traceroute、NHRP 缓存、接口计数器）
> 2. **配置模板必须有版本号和一致性校验**（Hub 与 Spoke 的配置是"成对"的，漏一半就是静默退化）
> 3. **收敛后的路径必须纳入监控**（如"Spoke 间流量是否经 Hub"应有一条巡检项）

</div>

##### GET VPN: Encryption Without Tunnels

<div class="zh" markdown="1">

##### GET VPN：没有隧道的加密

</div>

| Dimension | Description |
|------|------|
| **Mechanism** | Group keys (TEK/KEK) are distributed by a key server to all group members; members encrypt directly with the same key and **no point-to-point tunnel is built** |
| **Advantage** | Keeps the original IP header → **routing follows the carrier network exactly** (MPLS QoS, TE, and any path are preserved); tiny overhead; a new site only has to register |
| **Cost** | Requires the **underlying network to be trustworthy and reachable** (usually a carrier MPLS VPN); a group key leak affects the whole group; does not work across the Internet |
| **Fit** | An existing MPLS/Segment Routing WAN needing compliant encryption, many sites, and strict latency/path requirements |

<div class="zh" markdown="1">

| 维度 | 说明 |
|------|------|
| **机制** | 组密钥（TEK/KEK）由 Key Server 分发给所有组成员，成员间用同一密钥直接加密，**不建立点对点隧道** |
| **优势** | 保留原始 IP 头 → **路由完全按运营商网络走**（可保留 MPLS 的 QoS、TE、任意路径）；开销极小；新站点加入只需注册 |
| **代价** | 需要**底层网络本身是可信可达的**（通常是运营商 MPLS VPN）；组密钥泄露影响全组；不支持跨 Internet |
| **适用** | 已有 MPLS/Segment Routing WAN、需要合规加密、站点数多、对时延/路径有严格要求 |

</div>

**Selection quick reference**:

<div class="zh" markdown="1">

**选型速查**：

</div>

| Your situation | Choose |
|---------|-----|
| Fewer than 10 sites, simple topology, no spoke-to-spoke need | Point-to-point IPsec |
| Many sites, need spoke-to-spoke, across the Internet | **DMVPN Phase 3 / FlexVPN** |
| New build needing site-to-site and remote access unified | **FlexVPN** (the IKEv2 unified framework) |
| Existing carrier MPLS, want encryption without tunnels | **GET VPN** |
| Many sites, multiple links, application-aware path selection | **SD-WAN (with built-in IPsec)** |

<div class="zh" markdown="1">

| 你的情况 | 选 |
|---------|-----|
| 站点 < 10，拓扑简单，无 Spoke 直连需求 | 点对点 IPsec |
| 站点多，需要 Spoke 直连，跨 Internet | **DMVPN Phase 3 / FlexVPN** |
| 新建，需统一站点间与远程访问 | **FlexVPN**（IKEv2 统一框架） |
| 已有运营商 MPLS，只要加密不要隧道 | **GET VPN** |
| 站点多、多链路、要应用感知选路 | **SD-WAN（内建 IPsec）** |

</div>

> 💡 **Trend judgment**: in new builds, **DMVPN is being replaced by SD-WAN and FlexVPN**. DMVPN's value is "an existing fleet of Cisco routers plus a fast, low-cost network build", while SD-WAN has structural advantages in "multiple links + application policy + centralized operations". If you choose DMVPN in a design document, you must explain why not SD-WAN.

<div class="zh" markdown="1">

> 💡 **趋势判断**：新建项目里，**DMVPN 正在被 SD-WAN 和 FlexVPN 取代**。DMVPN 的价值在"已有 Cisco 路由器群 + 需要低成本快速组网"，而 SD-WAN 在"多链路 + 应用策略 + 集中运维"上有结构性优势。设计文档里选 DMVPN 必须说明为什么不用 SD-WAN。

</div>

#### Remote Access VPN · 远程访问 VPN

##### The Three Access Models

![Full tunnel, split tunnel and clientless remote access compared, and the four real risks that make split tunnelling a policy problem rather than a routing one](assets/fig/en10-42-remote-access-models.svg)


<div class="zh" markdown="1">

##### 三种接入模型

</div>

| Model | Client | User experience | Security control | Fit |
|------|--------|---------|-----------|------|
| **Full tunnel** | Client required, **all traffic goes through the enterprise** | Poor (domestic browsing slows down, video stutters) | **Highest** (all traffic can be inspected) | Highly sensitive roles, compliance requirements |
| **Split tunnel** | Client required, **only enterprise traffic goes over the VPN** | Good | Medium (public traffic is uncontrolled; the endpoint may be infected) | The common practice |
| **Clientless (SSL VPN portal)** | Browser | Good (no client) | Low (only published web applications are reachable) | Partners, BYOD, temporary access |

<div class="zh" markdown="1">

| 模型 | 客户端 | 用户体验 | 安全可控性 | 适用 |
|------|--------|---------|-----------|------|
| **Full Tunnel（全隧道）** | 需装客户端，**所有流量走企业** | 差（境内访问变慢、视频卡） | **最高**（全流量可检查） | 高敏感岗位、合规要求 |
| **Split Tunnel（分离隧道）** | 需装客户端，**仅企业流量走 VPN** | 好 | 中（公网流量不受控，终端可能被感染） | 普遍做法 |
| **Clientless（SSL VPN 门户）** | 浏览器 | 好（无客户端） | 低（只能访问发布的 Web 应用） | 合作伙伴、BYOD、临时访问 |

</div>

**The real risks of split tunneling and their mitigation**:

<div class="zh" markdown="1">

**分离隧道的真实风险与缓解**：

</div>

| Risk | Scenario | Mitigation |
|------|------|------|
| **The endpoint becomes a pivot after compromise** | A user browses a malicious site while connected to the VPN | Endpoint detection (EDR compliance checks), split by application rather than by address |
| **DNS leakage** | Under split tunnel DNS goes local, so internal names fail to resolve or queries leak | **Send internal domains to the VPN's DNS**, keep public domains local |
| **IPv6 bypass** | Only IPv4 is tunneled, so IPv6 goes straight to the Internet and bypasses policy | Handle IPv6 too, or disable IPv6 on the endpoint |
| **Policy bypass** | Users can reach internal resources outside the tunnel list (if ACLs are loose) | Still need ACLs on the tunnel side; never use the "split list" as a security control |

<div class="zh" markdown="1">

| 风险 | 场景 | 缓解 |
|------|------|------|
| **终端被入侵后成为跳板** | 用户一边访问恶意网站一边连着 VPN | 端点检测（EDR 合规检查）、按应用分流而非按地址 |
| **DNS 泄露** | 分离隧道下 DNS 走本地，内网域名解析失败或泄露查询 | **内网域名走 VPN 的 DNS**，公网域名走本地 |
| **IPv6 旁路** | 只对 IPv4 做隧道，IPv6 直连公网绕过策略 | 同时处理 IPv6，或终端禁用 IPv6 |
| **策略绕过** | 用户可访问不在隧道列表里的内部资源（若 ACL 不严） | 隧道侧仍需 ACL，不能靠"分流列表"做安全 |

</div>

```cfg
! Split tunnel (be precise, do not use "any")
access-list SPLIT-TUNNEL standard permit 10.0.0.0 0.0.255.255
access-list SPLIT-TUNNEL standard permit 172.16.0.0 0.15.255.255

! AnyConnect / headend side
ipv4 split-include 10.0.0.0 255.0.0.0
ipv4 split-dns <internal-domain>
```

<div class="zh" markdown="1">

```cfg
! 分离隧道（按需精细化，不要用 any）
access-list SPLIT-TUNNEL standard permit 10.0.0.0 0.0.255.255
access-list SPLIT-TUNNEL standard permit 172.16.0.0 0.15.255.255

! AnyConnect / headend 侧
ipv4 split-include 10.0.0.0 255.0.0.0
ipv4 split-dns <内网域名>
```

</div>

##### Authentication Design for Remote Access

<div class="zh" markdown="1">

##### 远程访问的认证设计

</div>

| Element | Options | Recommendation |
|------|------|------|
| **First factor** | Password / certificate | Certificates resist phishing better |
| **Second factor** | TOTP / Push / hardware token / FIDO2 | **Push carries MFA fatigue risk**; FIDO2 is the most phishing-resistant |
| **Endpoint compliance** | Host scan (patches, antivirus, disk encryption, jailbreak/root) | **Mandatory**, otherwise the VPN is "an entrance for any device" |
| **Authorization** | Per-group ACLs/pools/policies | At minimum distinguish employee / contractor / partner |
| **Session control** | Idle timeout, maximum duration, concurrency limits | Prevents long-term residency |

<div class="zh" markdown="1">

| 要素 | 选项 | 建议 |
|------|------|------|
| **第一因素** | 密码 / 证书 | 证书更抗钓鱼 |
| **第二因素** | TOTP / Push / 硬件令牌 / FIDO2 | **Push 有 MFA 疲劳攻击风险**；FIDO2 抗钓鱼最强 |
| **终端合规** | 主机扫描（补丁、杀软、磁盘加密、是否越狱） | **必须**，否则 VPN 就是"任意设备的入口" |
| **授权** | 按组下发 ACL/池/策略 | 至少区分：员工 / 外包 / 合作伙伴 |
| **会话控制** | 空闲超时、最大时长、并发限制 | 防长期驻留 |

</div>

> ⚠️ **MFA fatigue attacks**: after obtaining a password, the attacker **repeatedly pushes MFA requests** until the user accidentally taps Approve. Several well-known intrusions in 2022 took exactly this path. **Countermeasures**: switch to **number matching** or **FIDO2**, and rate limit push notifications.

<div class="zh" markdown="1">

> ⚠️ **MFA 疲劳攻击（MFA Fatigue）**：攻击者拿到密码后，**反复推送 MFA 请求**直到用户误点"批准"。2022 年多起知名入侵事件都是这个路径。**对策**：改用**数字匹配（Number Matching）** 或 **FIDO2**，并限制推送频率。

</div>

##### ZTNA and SASE: An Architectural Change

![Traditional VPN, ZTNA and SASE compared by access path and trust assumption, with the advantages of ZTNA and the four constraints that slow its migration](assets/fig/en10-43-ztna-sase.svg)


<div class="zh" markdown="1">

##### ZTNA 与 SASE：架构层面的变化

</div>

| Model | Access path | Trust assumption | Key difference |
|------|---------|---------|---------|
| **Traditional VPN** | Endpoint → VPN gateway → **into the internal network** (network-level access) | Authenticated means trusted network position | Once connected, the whole internal network can be scanned |
| **ZTNA** | Endpoint → broker → **a specific application** (application-level access) | **Never trust**; authorize each access separately | Users cannot see the internal network and cannot scan laterally |
| **SASE** | Endpoint → nearest PoP (SD-WAN plus cloud security) | As above, plus inspection near the user | Security capabilities move to the cloud and converge with network access |

<div class="zh" markdown="1">

| 模型 | 访问路径 | 信任假设 | 关键差异 |
|------|---------|---------|---------|
| **传统 VPN** | 终端 → VPN 网关 → **进入内网**（网络级访问） | 认证通过即信任网络位置 | 一旦连上，可扫描整个内网 |
| **ZTNA** | 终端 → 代理 → **特定应用**（应用级访问） | **永不信任**，每次访问单独鉴权 | 用户看不到内网，无法横向扫描 |
| **SASE** | 终端 → 就近 PoP（融合 SD-WAN + 云安全） | 同上 + 流量就近检查 | 安全能力云化，与网络接入融合 |

</div>

**Three structural advantages of ZTNA over VPN**:

<div class="zh" markdown="1">

**ZTNA 相对 VPN 的三个结构性优势**：

</div>

1. **No network exposure**: only applications are published, users get no internal routes, and scanning becomes moot
2. **Fine-grained permissions**: per application + per identity + per device posture
3. **Auditable**: every application access is recorded (rather than "one tunnel was open for 8 hours")

<div class="zh" markdown="1">

1. **不暴露网络**：只发布应用，用户拿不到内网路由，扫描无从谈起
2. **权限精细**：按应用 + 按身份 + 按设备状态授权
3. **可审计**：每次应用访问都有记录（而不是"一条隧道开了 8 小时"）

</div>

**The practical constraints of migration**:

<div class="zh" markdown="1">

**迁移的现实约束**：

</div>

| Constraint | Description |
|------|------|
| **Application remediation** | Non-HTTP applications (RDP, SMB, database clients, legacy C/S) need connector support |
| **Performance** | Traffic transits a cloud PoP, so latency must be assessed; critical applications may keep a dedicated line |
| **Hybrid period** | Typically VPN and ZTNA run in parallel for 2–3 years, requiring unified identity and policy |
| **Cost model change** | From "buy appliances" to "per-user subscription", so the long-term TCO must be recalculated |

<div class="zh" markdown="1">

| 约束 | 说明 |
|------|------|
| **应用改造** | 非 HTTP 应用（RDP、SMB、数据库客户端、老旧 C/S）需要连接器支持 |
| **性能** | 流量经云 PoP 中转，需评估时延；关键应用可能要保留专线 |
| **混合期** | 通常 2~3 年 VPN 与 ZTNA 并行，需要统一身份与策略 |
| **成本模型变化** | 从"买设备"变成"按用户订阅"，长期 TCO 要重算 |

</div>

> 💡 **Design judgment**: if the customer's real pain is "**contractors can see far too much**", ZTNA is on point; if the pain is "**remote access is too slow**", what they need is closer access (a SASE PoP) or a dedicated line, not ZTNA. **Do not use an architecture upgrade to solve a performance problem.**

<div class="zh" markdown="1">

> 💡 **设计判断**：如果客户的真实痛点是"**外包人员能看到的太多了**"，ZTNA 是对症的；如果痛点是"**远程访问太慢**"，那可能需要的是就近接入（SASE PoP）或专线，不是 ZTNA。**别用架构升级去解决性能问题。**

</div>

---

## Integrated Case Studies · 综合实战案例

> The following three cases are "design-level" and cover the three main lines: control plane, remote access, and overall architecture restructuring. Their common trait: **nothing was technically misconfigured — the design assumptions were wrong.**

<div class="zh" markdown="1">

> 以下三个案例是"设计级"的，覆盖控制平面、远程访问、整体架构重构三条主线。它们共同的特点是：**技术上都没有配错，错在设计假设**。

</div>

### Case 1: CoPP Rate Limiting Broke a Full BGP Table Update · 案例一：CoPP 限速把 BGP 全表更新打掉

**Background**: at a service provider edge network, one border router had two eBGP sessions upstream and received **about 950,000** IPv4 routes. To pass a compliance assessment the security team deployed CoPP from a "standard template".

<div class="zh" markdown="1">

**背景**：某运营商边缘网络，一台边界路由器与上游有两条 eBGP 会话，接收 **约 95 万条** IPv4 路由。安全团队为通过等保测评，按"标准模板"部署了 CoPP。

</div>

**Template content (excerpt)**:

<div class="zh" markdown="1">

**模板内容（节选）**：

</div>

```cfg
class-map match-all CM-BGP
 match access-group name CPP-BGP
policy-map PM-COPP
 class CM-BGP
  police rate 500000 bps      ! 500 kbps
   conform-action transmit
   exceed-action drop
```

<div class="zh" markdown="1">

```cfg
class-map match-all CM-BGP
 match access-group name CPP-BGP
policy-map PM-COPP
 class CM-BGP
  police rate 500000 bps      ! 500 kbps
   conform-action transmit
   exceed-action drop
```

</div>

**The failure**:

<div class="zh" markdown="1">

**故障现象**：

</div>

| Time | Symptom |
|--------|------|
| Daytime on the deployment day | **Everything normal**, CPU stable |
| 02:10 that night | Upstream maintenance reset the BGP session |
| 02:10 – 02:40 | Router CPU hit 90%, some prefixes were missing, **some users could not reach specific sites** |
| After 02:40 | Recovered on its own |

<div class="zh" markdown="1">

| 时间点 | 现象 |
|--------|------|
| 部署当天白天 | **一切正常**，CPU 平稳 |
| 当天凌晨 02:10 | 上游做维护，BGP 会话复位 |
| 02:10 ~ 02:40 | 路由器 CPU 冲到 90%，部分前缀缺失，**部分用户访问特定站点不通** |
| 02:40 后 | 自行恢复 |

</div>

**Root cause analysis**:

<div class="zh" markdown="1">

**根因分析**：

</div>

1. **Steady state vs burst**: in steady state BGP only sends keepalives (tens of bytes per second), so 500 kbps is plenty. But **a session rebuild requires the full table**: 950,000 routes at roughly 50–100 bytes per UPDATE, plus TCP retransmissions, needs **30–80 Mbps at peak** (depending on the upstream send rate and the TCP window).
2. **CoPP drops caused a TCP retransmission storm**: dropped BGP messages triggered TCP retransmissions, which consumed more bandwidth and caused more drops → convergence time stretched from a normal 2 minutes to over 30 minutes.
3. **Why "some prefixes were missing" yet it "looked usable"**: the default route arrived first so most traffic was fine; only traffic toward specific prefixes took a wrong path or was black-holed — and this class of failure is **extremely hard for users to describe accurately** ("some websites will not open").
4. **Why the CPU spiked**: heavy route computation during BGP convergence plus processing of retransmitted messages after drops. CoPP only limits the inbound rate; it cannot reduce the CPU's computational load.

<div class="zh" markdown="1">

1. **稳态 vs 突发**：BGP 稳态下只有 keepalive（几十字节/秒），500 kbps 绰绰有余。但**会话重建时要接收全表**：95 万条路由，每条 UPDATE 报文约 50~100 字节，加上 TCP 重传，**峰值需要 30~80 Mbps**（取决于上游发送速率和 TCP 窗口）。
2. **CoPP 丢弃导致 TCP 重传风暴**：被丢的 BGP 报文触发 TCP 重传，重传又占用更多带宽，更多被丢 → 收敛时间从正常 2 分钟拉长到 30 分钟以上。
3. **为什么"部分前缀缺失"却"看起来能用"**：默认路由先到了，大部分流量正常；只有去往特定前缀的流量走错或黑洞 —— 这类故障**极难被用户准确描述**（"某些网站打不开"）。
4. **为什么 CPU 冲高**：BGP 收敛过程中大量路由计算 + 大量被丢弃后重传的报文处理。CoPP 只限制入向速率，不能减少 CPU 的计算负担。

</div>

**The correct approach**:

<div class="zh" markdown="1">

**正确做法**：

</div>

| Measure | Description |
|------|------|
| **Set the rate from measured capacity** | The measured full-table convergence peak on this device was ~60 Mbps, so CoPP should be set to **100–200 Mbps** (with headroom), not 500 kbps |
| **Separate "control plane protection" from "routing protocol protection"** | The BGP rate limit must be **generous enough to carry the full table**; real DoS protection comes from the upstream, uRPF, and prefix filtering |
| **Use `class-default` as the backstop instead of strangling key classes** | Give key protocol classes generous quotas and the default class a strict quota (to stop real junk) |
| **Validation must include the "session rebuild" scenario** | Testing only steady state is not testing. The acceptance case: `clear ip bgp *` and observe convergence time and packet loss |
| **Alert before dropping** | Start with `exceed-action transmit` plus monitoring; only change to `drop` once long-term data confirms no anomalies |

<div class="zh" markdown="1">

| 措施 | 说明 |
|------|------|
| **按实测容量设定** | 该设备实测全表收敛峰值 ~60 Mbps，CoPP 应设为 **100~200 Mbps**（留余量），而不是 500 kbps |
| **区分"控制平面保护"与"路由协议保护"** | BGP 的限速应该**宽松到足以承载全表**，真正的 DoS 防护靠上游 + uRPF + 前缀过滤 |
| **用 `class-default` 兜底而非掐死关键类** | 关键协议类给大方额度，default 类给严格额度（拦住真正的垃圾） |
| **验证必须包含"会话重建"场景** | 只测稳态等于没测。验收用例：`clear ip bgp *` 后观察收敛时间与丢包 |
| **告警优先于丢弃** | CoPP 类先 `exceed-action transmit` + 监控告警，确认长期无异常后再改 `drop` |

</div>

**Three design-level conclusions**:

<div class="zh" markdown="1">

**设计层面的三条结论**：

</div>

1. **CoPP rates must be derived from "the protocol load this device actually carries" — templates cannot be reused.** The reasonable value for a core border router and for an access switch differs by three orders of magnitude.
2. **The correct goal of "protecting the control plane" is "guarantee that legitimate protocol traffic gets through", not "limit it to some number".** Get the order wrong and the protection itself becomes the source of the outage.
3. **Every security measure needs an emergency path for "when it fails itself"**: can CoPP be bypassed quickly if misconfigured? There must be explicit rollback commands and an authorized person.

<div class="zh" markdown="1">

1. **CoPP 的速率必须从"该设备实际承载的协议负载"推导，不能套模板。** 一台核心边界路由器和一台接入交换机的合理值差了三个数量级。
2. **"保护控制平面"的正确目标是"保证合法协议流量能过"，而不是"限制到某个数字"。** 顺序搞反了，保护措施本身就变成故障源。
3. **所有安全措施都要有"它自己失效"的应急路径**：CoPP 配错时能否快速旁路？要有明确的回退命令与授权人。

</div>

### Case 2: Split Tunneling + One Compromised Laptop Took Down Headquarters · 案例二：分离隧道 + 一台被入侵的笔记本，导致总部沦陷

**Background**: an enterprise had 3,000 remote employees on SSL VPN with **split tunneling** (only `10.0.0.0/8` went over the VPN; everything else went over local broadband). The VPN side only did "authentication + group ACL" with no endpoint compliance checking.

<div class="zh" markdown="1">

**背景**：某企业 3,000 名远程员工使用 SSL VPN，采用**分离隧道**（只有 `10.0.0.0/8` 走 VPN，其余走本地宽带）。VPN 侧只做了"认证 + 组 ACL"，没有终端合规检查。

</div>

**Reconstruction of the attack chain** (from logs, afterwards):

<div class="zh" markdown="1">

**攻击链还原**（事后从日志重建）：

</div>

| Stage | Action | Why it was not stopped |
|------|------|------------|
| **① Initial infection** | An employee visited a phishing site at home and a browser vulnerability dropped a trojan | Under split tunneling public traffic never traverses the enterprise, so the enterprise **could not see it at all** |
| **② C2 established** | The trojan called back to the attacker's server | Same as above: C2 went over local broadband, with no logs at the enterprise egress |
| **③ Lateral discovery** | After the employee connected to the VPN, the trojan **scanned `10.0.0.0/8`** | The VPN group ACL was "permit all ports across `10.0.0.0/8`" (configured early on for convenience) |
| **④ Credential theft** | A plaintext domain password (hard-coded in an operations script) was taken from a share on a test server | That server had no EDR and the share permissions were too broad |
| **⑤ Privilege escalation and spread** | The domain account was used to reach more servers and eventually the domain controllers | No segmentation: the server zone was one large VLAN; domain admin accounts had been used to log in to ordinary servers |
| **⑥ Persistence** | A hidden account plus scheduled task was created on a domain controller | No configuration/account change monitoring on the domain controllers |

<div class="zh" markdown="1">

| 阶段 | 动作 | 为什么没被拦 |
|------|------|------------|
| **① 初始感染** | 员工在家访问钓鱼站点，浏览器漏洞导致木马落地 | 分离隧道下公网流量不经企业，企业侧**完全看不到** |
| **② 建立 C2** | 木马回连攻击者服务器 | 同上，C2 走本地宽带，企业出口无日志 |
| **③ 横向探测** | 员工连上 VPN 后，木马**扫描 `10.0.0.0/8`** | VPN 组 ACL 是"允许访问 `10.0.0.0/8` 所有端口"（早期为省事配的） |
| **④ 凭据窃取** | 从一台测试服务器的共享目录拿到域账号明文密码（运维脚本里硬编码） | 该服务器无 EDR，共享权限过宽 |
| **⑤ 提权与扩散** | 用域账号访问更多服务器，最终到域控 | 没有分段，服务器区在一个大 VLAN；域管账号曾被用于登录普通服务器 |
| **⑥ 持久化** | 在域控上创建隐藏账号 + 计划任务 | 没有域控的配置/账号变更监控 |

</div>

**How it was discovered**: **by accident**. An operations engineer reviewing firewall sessions noticed an internal host scanning port 445.

<div class="zh" markdown="1">

**发现方式**：**偶然**。一名运维在查看防火墙会话时发现内网有主机在扫描 445 端口。

</div>

**Key failures (ordered by severity)**:

<div class="zh" markdown="1">

**关键失误（按严重程度排序）**：

</div>

| Rank | Failure | What should have been done |
|------|------|-----------|
| 1 | **The VPN group ACL was `permit 10.0.0.0/8 any`** | Deliver **least reachability** per role (which group → which servers → which ports), denied by default |
| 2 | **No endpoint compliance check** | Check before connecting: EDR running, patch level, disk encryption, not jailbroken; non-compliant → a "remediation VLAN" only |
| 3 | **No segmentation in the server zone** | Segment servers by application and forbid default server-to-server reachability |
| 4 | **Hard-coded credentials + domain admin reuse** | Separate service accounts, use LAPS for local admin passwords, and forbid domain admin logins to ordinary servers |
| 5 | **The split-tunnel blind spot was accepted but not compensated** | If split tunneling is required, **EDR on the endpoint must be the backstop** (if you cannot see network traffic, you must see endpoint behavior) |
| 6 | **No EDR / no SIEM correlation** | At minimum EDR + centralized logging + an "internal scanning" detection rule |

<div class="zh" markdown="1">

| 排名 | 失误 | 本应怎么做 |
|------|------|-----------|
| 1 | **VPN 组 ACL 是 `permit 10.0.0.0/8 any`** | 按角色下发**最小可达**（哪个组 → 哪些服务器 → 哪些端口），默认拒绝 |
| 2 | **无终端合规检查** | 连接前检查：EDR 在运行、补丁级别、磁盘加密、非越狱；不合规 → 只给"修复 VLAN" |
| 3 | **服务器区无分段** | 服务器按应用分段，禁止服务器之间默认互通 |
| 4 | **凭据硬编码 + 域管账号滥用** | 服务账号分离、LAPS 管理本地管理员密码、禁止域管登录普通服务器 |
| 5 | **分离隧道的安全盲区被接受但未补偿** | 若必须分离隧道，则**终端侧必须由 EDR 兜底**（企业看不到网络流量，就要看到终端行为） |
| 6 | **无 EDR / 无 SIEM 关联** | 至少要有 EDR + 集中日志 + "内网扫描"检测规则 |

</div>

**The core design-level conclusion**:

<div class="zh" markdown="1">

**设计层面的核心结论**：

</div>

> **Split tunneling outsources "visibility" to the endpoint.**
>
> It is an **unavoidable trade**:
> - Full tunnel → the enterprise has complete network-side visibility, but bandwidth cost and user experience suffer
> - Split tunnel → good user experience, but **endpoint-side controls (EDR + compliance checks) must compensate for the lost network-side visibility**
>
> **Split tunneling without endpoint controls means deliberately giving up security capability in that direction.** Many enterprises do exactly that — because buying EDR is "the IT department's business" and changing the VPN configuration is "the network department's business", and the two were never discussed in one solution.

<div class="zh" markdown="1">

> **分离隧道把"可见性"外包给了终端。**
>
> 这是一个**不可回避的交换**：
> - Full Tunnel → 企业在网络侧有完整可见性，但带宽成本和用户体验差
> - Split Tunnel → 用户体验好，但**必须用终端侧的控制（EDR + 合规检查）来补偿失去的网络侧可见性**
>
> **只做分离隧道而不做终端控制，等于主动放弃这个方向的安全能力。** 很多企业恰恰是这么干的 —— 因为买 EDR 是"IT 部门的事"，改 VPN 配置是"网络部门的事"，两者从来没有在一个方案里被一起讨论过。

</div>

### Case 3: Restructuring from a Flat Network to a Segmented Architecture (the Full Decision Process) · 案例三：从扁平网络到分段架构的重构（完整决策过程）

**Background**: a manufacturing enterprise with a 2,000-person campus, two factories (the OT network), and one data center. The state before:

<div class="zh" markdown="1">

**背景**：某制造企业，园区 2,000 人 + 两个工厂（工控网）+ 一个数据中心。现状：

</div>

- The whole campus used `10.0.0.0/16`, with **every endpoint, server, and printer on one large Layer 2 network** (multiple VLANs but fully routed between them)
- The OT network (PLC, SCADA) **was on the same switches as the office network**, only in different VLANs, with Layer 3 reachability via static routes on the core
- One firewall at the egress with 4,000+ rules and no IPS
- No 802.1X; Wi-Fi on a single PSK

<div class="zh" markdown="1">

- 整个园区使用 `10.0.0.0/16`，**所有终端、服务器、打印机在一个大二层网络**（多个 VLAN 但三层全通）
- 工控网（PLC、SCADA）**与办公网在同一批交换机上**，只是不同 VLAN，三层通过核心互通的静态路由
- 出口一台防火墙，规则 4,000+ 条，无 IPS
- 无 802.1X，Wi-Fi 一个 PSK

</div>

**Trigger event**: a ransomware incident encrypted 3 file servers and some office PCs. The OT network was unaffected purely by luck (the attacker never scanned it).

<div class="zh" markdown="1">

**触发事件**：一次勒索软件事件，加密了 3 台文件服务器 + 部分办公 PC。工控网未受影响纯属运气（攻击者没扫到）。

</div>

**The goal (from management)**: "This must not happen again, and production must not be affected."

<div class="zh" markdown="1">

**目标（管理层给的）**："不能再发生这种事，也不能影响生产。"

</div>

#### Step 1: Asset and Traffic Discovery (4 weeks) · 第一步：资产与流量梳理（4 周）

| Output | Content |
|------|------|
| Asset inventory | 3,200 endpoints, 180 servers, 420 IoT/OT devices, 600 network devices |
| Asset classification | L1: ERP/MES/PLC/domain controllers; L2: file/mail/finance; L3: OA/printing; L4: public website |
| **Cross-zone traffic matrix** | Who accesses whom, over what protocol, at what volume — this is the basis for every later policy |
| List of devices not supporting 802.1X | 187 (printers, medical devices, OT, old time clocks) |

<div class="zh" markdown="1">

| 产出 | 内容 |
|------|------|
| 资产清单 | 3,200 台终端、180 台服务器、420 台 IoT/工控、600 台网络设备 |
| 资产分级 | L1：ERP/MES/PLC/域控；L2：文件/邮件/财务；L3：OA/打印；L4：官网 |
| **跨区流量矩阵** | 谁访问谁、什么协议、多少流量 —— 这是后面所有策略的依据 |
| 不支持 802.1X 的设备清单 | 187 台（打印机、医疗设备、工控、老式考勤机） |

</div>

#### Step 2: Zone Design (3 weeks) · 第二步：分区设计（3 周）

| Zone | Content | Isolation method | Cross-zone policy |
|----|------|---------|---------|
| **OT zone** | PLC, SCADA, HMI, engineering stations | **Physically separate switches + separate egress** | With IT, only through a **one-way data diode / industrial firewall** (MES → ERP one-way data pull) |
| **Data center (DC)** | Servers | VRF + firewall (east-west) | Segmented by application; server-to-server denied by default |
| **Office zone** | Employee endpoints | 802.1X + VLAN + firewall | Can only reach published business ports in the DC |
| **IoT/printing zone** | Devices that cannot authenticate | Separate VLAN + ACL (**no DAI**) | Can only reach the print server / IoT platform |
| **Management zone** | Network device management | **OOB + management VRF** | Only the bastion host may connect |
| **Guest/wireless** | Guests + BYOD | Separate SSID + separate egress (**Internet only**) | No access to the internal network at all |
| **DMZ** | Externally facing services | Firewall DMZ port | Internet → DMZ one-way; DMZ → internal **forbidden** |

<div class="zh" markdown="1">

| 区 | 内容 | 隔离方式 | 跨区策略 |
|----|------|---------|---------|
| **工控区（OT）** | PLC、SCADA、HMI、工程师站 | **物理独立交换机 + 独立出口** | 与 IT 只允许通过**单向数据二极管/工业防火墙**（MES → ERP 单向取数） |
| **数据中心（DC）** | 服务器 | VRF + 防火墙（东西向） | 按应用分段，服务器间默认拒绝 |
| **办公区** | 员工终端 | 802.1X + VLAN + 防火墙 | 只能访问 DC 中已发布的业务端口 |
| **IoT/打印区** | 不支持认证的设备 | 独立 VLAN + ACL（**不做 DAI**） | 只能访问打印服务器 / IoT 平台 |
| **管理区** | 网络设备管理 | **OOB + 管理 VRF** | 只有堡垒机可访问 |
| **访客/无线** | 访客 + BYOD | 独立 SSID + 独立出口（**只走 Internet**） | 完全不能访问内网 |
| **DMZ** | 对外服务 | 防火墙 DMZ 口 | 公网 → DMZ 单向；DMZ → 内网**禁止** |

</div>

**Key decision: why must the OT network be physically decoupled?**

<div class="zh" markdown="1">

**关键决策：工控网为什么必须物理解耦？**

</div>

| Option | Isolation strength | Cost | Decision |
|------|---------|------|------|
| VLAN isolation | Weak (shared devices; a misconfiguration bridges them) | Low | ❌ Does not meet the requirement |
| VRF isolation | Medium (shared devices) | Medium | ❌ Still the same failure domain / attack surface |
| **Physical separation** | Strong | High (new switches, new cabling) | ✅ Adopted |

<div class="zh" markdown="1">

| 方案 | 隔离强度 | 成本 | 决策 |
|------|---------|------|------|
| VLAN 隔离 | 弱（共用设备，配置错误即打通） | 低 | ❌ 不满足要求 |
| VRF 隔离 | 中（共用设备） | 中 | ❌ 仍在同一故障域/攻击面 |
| **物理独立** | 强 | 高（需新交换机、新布线） | ✅ 采用 |

</div>

**The reasoning**: the security requirement for OT is not "confidentiality" but **"availability + human safety"**. An IOS upgrade mistake on an office switch or a single VLAN misconfiguration must not be able to stop the production line. And OT devices have patch cycles measured in **years**, so device hardening cannot be the answer.

<div class="zh" markdown="1">

**理由**：工控网的安全要求不是"保密"，而是**"可用性 + 人身安全"**。一台办公交换机的 IOS 升级失误、一次 VLAN 配置错误，都不能让产线停摆。而且 OT 设备的补丁周期以"年"计，无法靠设备加固。

</div>

#### Step 3: Control Point Selection (2 weeks) · 第三步：控制点选型（2 周）

| Requirement | Solution | Trade-off note |
|------|------|---------|
| Access admission | **802.1X (PEAP + MAB)**, in three phases: monitor → low-impact → closed | You cannot go straight to closed; the 187 unsupported devices must be classified first |
| East-west inspection | **Firewall virtualization (multiple contexts) + application segmentation** inside the DC | Faster to deploy than micro-segmentation (which requires application changes) |
| Egress | Firewall + **IPS** + outbound traffic filtering (to limit C2 callbacks) | Outbound policy is the last line against ransomware |
| Visibility | Network-wide sFlow + boundary NetFlow + **NDR/NTA** | Ransomware's lateral scanning is distinctive and detectable on the traffic side |
| Endpoint | **EDR deployed everywhere** | In split-tunnel/borderless scenarios the endpoint is mandatory |
| Backup | **Offline/immutable backup** + regular restore drills | In ransomware defense, **backup > everything else** |

<div class="zh" markdown="1">

| 需求 | 方案 | 取舍说明 |
|------|------|---------|
| 接入准入 | **802.1X（PEAP + MAB）**，分三阶段：Monitor → Low-Impact → Closed | 不能用 Closed 一把上，187 台不支持设备需先归类 |
| 东西向检查 | DC 内用**防火墙虚拟化（多上下文）+ 应用分段** | 比微分段（需改造应用）落地快 |
| 出口 | 防火墙 + **IPS** + 出向流量过滤（限制 C2 回连） | 出向策略是勒索软件的最后一道 |
| 可见性 | 全网 sFlow + 边界 NetFlow + **NDR/NTA** | 勒索软件的横向扫描特征明显，流量侧可检测 |
| 终端 | **EDR 全场部署** | 分离隧道/无边界场景下，终端是必须 |
| 备份 | **离线/不可变备份** + 定期恢复演练 | 勒索防护里**备份 > 一切** |

</div>

#### Step 4: Migration Order (the key: do not change everything at once) · 第四步：迁移顺序（关键：不能一次全改）

| Phase | Content | Duration | Risk control |
|------|------|------|---------|
| **P0** | Harden the backup system (offline + immutable + drills) | 4 weeks | **Do this first**: it is the only thing that saves you when you are attacked |
| **P1** | Egress policy cleanup (4,000 rules → simplified + default deny) + outbound filtering + IPS | 8 weeks | Run in monitor mode for 4 weeks first to see false positives |
| **P2** | Physical isolation of the OT network | 12 weeks | Batch by production line, using maintenance windows |
| **P3** | 802.1X (monitor → low-impact → closed) | 16 weeks | IoT goes into its own VLAN first and never enters closed mode |
| **P4** | DC segmentation + east-west firewall | 16 weeks | Batch by application, with regression testing per batch |
| **P5** | Management OOB + bastion host | 8 weeks | In parallel with P1 |
| **P6** | Visibility (sFlow/NetFlow/NDR) | 8 weeks | In parallel with P1; the earlier the better |

<div class="zh" markdown="1">

| 阶段 | 内容 | 周期 | 风险控制 |
|------|------|------|---------|
| **P0** | 备份体系加固（离线 + 不可变 + 演练） | 4 周 | **最先做**：这是唯一能在被攻击时救命的 |
| **P1** | 出口策略清理（4,000 条 → 精简 + 默认拒绝）+ 出向过滤 + IPS | 8 周 | 先在 Monitor 模式跑 4 周看误报 |
| **P2** | 工控网物理隔离 | 12 周 | 按产线分批，利用检修窗口 |
| **P3** | 802.1X（Monitor → Low-Impact → Closed） | 16 周 | IoT 先归入独立 VLAN，不进 Closed |
| **P4** | DC 分段 + 东西向防火墙 | 16 周 | 按应用分批，每批做回归测试 |
| **P5** | 管理面 OOB + 堡垒机 | 8 周 | 与 P1 并行 |
| **P6** | 可见性（sFlow/NetFlow/NDR） | 8 周 | 与 P1 并行，越早越好 |

</div>

#### Results and Lessons · 结果与教训

| Metric | Before | After |
|------|--------|--------|
| Egress firewall rules | 4,000+ | 380 (including application identification) |
| Access ports supporting 802.1X | 0% | 92% (8% IoT on restricted VLANs) |
| Connectivity between OT and IT | Fully routed | One-way data interface only |
| Ransomware lateral propagation path | Network-wide | Confined to a single application segment |

<div class="zh" markdown="1">

| 指标 | 改造前 | 改造后 |
|------|--------|--------|
| 出口防火墙规则数 | 4,000+ | 380（含应用识别） |
| 支持 802.1X 的接入端口 | 0% | 92%（8% 为 IoT 走受限 VLAN） |
| 工控网与 IT 的连通 | 三层全通 | 仅单向数据接口 |
| 勒索软件横向传播路径 | 全网可达 | 限于单个应用段 |

</div>

**The three most important lessons**:

<div class="zh" markdown="1">

**三条最重要的教训**：

</div>

1. **Backup comes before security appliances.** Every security control can be bypassed, but **offline immutable backup** is the only means of recovery after "everything has fallen". Many projects spend all their money on firewalls while backups still run on a visible NAS with domain-account credentials — which is the first thing ransomware encrypts.
2. **OT and IT have different security goals**: IT prioritizes "confidentiality", OT prioritizes "**availability and human safety**". Managing OT with IT methods (patching, installing agents, frequent changes) directly causes production stoppages. **Physical isolation plus a one-way gateway is mandatory.**
3. **Migration order matters more than technology selection.** With the same technical solution, doing egress before access versus access before egress carries completely different risk. **Build visibility first (otherwise you do not know what a change affects), build backup first (otherwise you cannot roll back a mistake), and touch admission last (it has the largest blast radius).**

<div class="zh" markdown="1">

1. **备份排在安全设备之前**。所有安全控制都有被绕过的可能，但**离线不可变备份**是唯一能在"全部失守"后恢复的手段。很多项目把钱全花在防火墙上，备份却还在用一台可见的 NAS + 域账号凭据 —— 勒索软件第一个加密的就是它。
2. **OT 与 IT 的安全目标不同**：IT 追求"保密性优先"，OT 追求"**可用性与安全性（人身）优先**"。用 IT 的方法（打补丁、装 agent、频繁变更）去管 OT，会直接导致停产。**必须物理隔离 + 单向网关**。
3. **迁移顺序比技术选型更重要**。同样的技术方案，先做出口再做接入，和先做接入再做出口，风险完全不同。**先建可见性（否则你不知道改了什么影响什么）、先建备份（否则改错了无法回头）、再动准入（影响面最大）**。

</div>

---

## Common Security Design Trade-offs · 安全设计的常见取舍

The core CCDE exam point is "making trade-offs under given constraints". The following are the six most frequent trade-offs in the security domain:

<div class="zh" markdown="1">

CCDE 的核心考点是"给定约束下做取舍"。以下是安全领域最高频的六组取舍：

</div>

| Trade-off | Option A | Option B | How to decide |
|------|--------|--------|---------|
| **Security vs availability** | Stricter controls (default deny, closed mode) | Looser (monitor mode, whitelists) | Which costs more: a business outage or a breach? |
| **Centralized vs distributed** | Centralized firewall (easy to manage, becomes a bottleneck) | Distributed policy (no bottleneck, hard to keep consistent) | Traffic volume and tolerance for failure domains |
| **Encryption overhead vs confidentiality need** | MACsec/IPsec everywhere | Encrypt only sensitive links | Physical exposure of the link + hardware acceleration capability |
| **Visibility vs performance** | Full NetFlow + per-packet IPS | Sampling + inspect only critical paths | Traffic volume + compliance requirements |
| **User experience vs control strength** | Full tunnel + endpoint checks | Split tunnel + lightweight checks | Sensitivity of the role + endpoint management capability (is there EDR) |
| **One-shot rework vs incremental migration** | Get it right in one go (clean architecture) | Batch it (controllable risk) | **Almost always choose incremental**, but with a clearly defined target architecture |

<div class="zh" markdown="1">

| 取舍 | 选项 A | 选项 B | 判断依据 |
|------|--------|--------|---------|
| **安全 vs 可用性** | 更严格的控制（默认拒绝、Closed Mode） | 更宽松（Monitor Mode、白名单） | 业务中断的代价 vs 被攻破的代价，哪个更大？ |
| **集中 vs 分布** | 集中防火墙（好管理、是瓶颈） | 分布式策略（无瓶颈、难一致） | 流量规模与故障域容忍度 |
| **加密开销 vs 保密需求** | MACsec/IPsec 全线加密 | 只加密敏感链路 | 链路的物理暴露程度 + 硬件加速能力 |
| **可见性 vs 性能** | 全量 NetFlow + IPS 逐包检查 | 采样 + 只查关键路径 | 流量规模 + 合规要求 |
| **用户体验 vs 控制强度** | Full Tunnel + 终端检查 | Split Tunnel + 轻量检查 | 岗位敏感度 + 终端管控能力（是否有 EDR） |
| **一次性重构 vs 渐进迁移** | 一次到位（架构干净） | 分批（风险可控） | **几乎总是选渐进**，但要有明确的终点架构 |

</div>

---

## Design Flaws (15 Items) · 本章设计缺陷清单（15 条）

| # | Flaw | Consequence | Correct practice |
|---|------|------|---------|
| 1 | Treating `service password-encryption` as encryption | Type 7 is reversible; the password is effectively cleartext | Use `secret` + type 8/9 |
| 2 | Management interfaces exposed to the Internet / temporary rules with no expiry | Automated brute force; forgotten entry points | Never expose them; rules carry an expiry |
| 3 | NTP without authentication, single upstream, no offset monitoring | Certificate expiry, VPN outages, uncorrelatable logs | Two upstreams + authentication + offset alerts |
| 4 | CoPP from a template with too low a rate | Routing protocol convergence strangled, producing "partially unreachable" symptoms | Measured peak × 2–3; alert before dropping |
| 5 | `class-default` dropping all unclassified traffic | New protocols/features mysteriously fail | Give the default class a generous quota, or alert only |
| 6 | Strict uRPF on a multi-egress network | Asymmetric routing is wrongly dropped and looks like a performance problem | Use loose/feasible on multi-egress networks |
| 7 | BPDU Guard on a cascaded port | The downstream switch is err-disabled and the whole segment goes down | BPDU Guard toward endpoints, Root Guard toward downstream switches |
| 8 | Using a service VLAN as the native VLAN | Double tagging jumps into a service VLAN | Use a dedicated empty VLAN as native |
| 9 | DAI/Source Guard ignoring static-IP devices | Printers/medical/OT devices go offline | Static bindings, or a separate VLAN for static devices |
| 10 | Going straight to closed mode with 802.1X | Large-scale outages among unsupported devices; the project is rolled back | Monitor → low-impact → closed in three phases |
| 11 | Maintaining the MAB whitelist by hand | Rots within six months; every device that had a NIC replaced goes dark | Synchronize automatically from DHCP/IPAM |
| 12 | Authentication order with dot1x first and a long timeout | Printers take 30 seconds to connect and users report it as a fault | Use `authentication order mab` on MAB-only ports |
| 13 | Treating SGT/VRF as a firewall substitute | Authorization without inspection; a compromised endpoint keeps its original permissions | Identity → authorization → inspection → isolation, all four layers |
| 14 | Direct static routes configured between VRFs | The "isolation" is fake in the configuration | Always cross domains through a stateful device, plus automated auditing |
| 15 | Introducing encapsulation (IPsec/GRE/VXLAN) without tuning MTU/MSS | Ping works but the business does not — the hardest class to troubleshoot | `ip mtu` + `ip tcp adjust-mss` + large-packet acceptance tests |

<div class="zh" markdown="1">

| # | 缺陷 | 后果 | 正确做法 |
|---|------|------|---------|
| 1 | `service password-encryption` 被当成加密 | type 7 可逆，密码等同于明文 | 用 `secret` + type 8/9 |
| 2 | 管理接口暴露公网 / 临时规则无到期 | 被自动化爆破、被遗忘的入口 | 永不暴露；规则带有效期 |
| 3 | NTP 无认证、单上游、无偏移监控 | 证书失效、VPN 中断、日志无法关联 | 双上游 + 认证 + 偏移告警 |
| 4 | CoPP 套模板、速率过低 | 路由协议收敛被掐死，出现"部分不通" | 实测峰值 × 2~3 倍；先告警后丢弃 |
| 5 | `class-default` drop 一切未分类流量 | 新协议/新功能莫名不通 | default 给宽松额度或只告警 |
| 6 | 多出口网络用 strict uRPF | 非对称路由被误杀，表现为"性能问题" | 多出口用 loose/feasible |
| 7 | BPDU Guard 配在级联口 | 下游交换机被 err-disable，整片断网 | 朝终端 BPDU Guard，朝下游 Root Guard |
| 8 | native VLAN 用业务 VLAN | 双重标签可跳到业务 VLAN | native 用独立的空 VLAN |
| 9 | DAI/Source Guard 忽略静态 IP 设备 | 打印机/医疗/工控设备离线 | 静态绑定，或为静态设备单独 VLAN |
| 10 | 802.1X 直接上 Closed Mode | 不支持设备大面积断网，项目被回退 | Monitor → Low-Impact → Closed 三阶段 |
| 11 | MAB 白名单手工维护 | 半年后腐坏，换过网卡的设备全断 | 从 DHCP/IPAM 自动同步 |
| 12 | 认证顺序 dot1x 在前且超时长 | 打印机等 30 秒才连上，用户当故障报修 | 纯 MAB 端口用 `authentication order mab` |
| 13 | 把 SGT/VRF 当成防火墙替代品 | 有授权无检查，被入侵终端仍以原权限活动 | 身份 → 授权 → 检查 → 隔离，四层并行 |
| 14 | VRF 间配了直接静态路由 | "隔离"在配置上是假的 | 跨域一律过有状态设备 + 自动巡检 |
| 15 | 引入封装（IPsec/GRE/VXLAN）不调 MTU/MSS | ping 通但业务不通，最难排查 | `ip mtu` + `ip tcp adjust-mss` + 大包验收测试 |

</div>

---

## Lessons from Practice · 实战经验总结

| Lesson | Description |
|------|------|
| **Defend each of the three planes separately** | Management plane (who can log in), control plane (who can punt to the CPU), data plane (who can pass through). Discussing "security" as one lump always leaves one side out |
| **Admission control must be phased** | Monitor → low-impact → closed, with quantified exit criteria per phase (failure rate, ticket volume). Going to closed in one step always ends in rollback |
| **Isolation must survive a "routing check"** | As long as a direct route exists between VRFs/VLANs, the isolation is a configuration illusion. Always cross domains through a stateful device |
| **Encryption and visibility require an explicit trade** | Wherever there is IPsec, there is no IPS. Write it into the document and compensate with endpoint-side means (EDR/log correlation) |
| **Security architectures have hidden single points** | NTP, AAA/RADIUS, certificates/PKI, the log server, the policy center. If any one fails, authentication and auditing across the network fail together |
| **Measure control plane rates** | CoPP, CPPr, and BFD timers must be set from measured peaks; template defaults regularly strangle protocols under real traffic |
| **Think about the "degraded mode" before changing anything** | Before admission/encryption/segmentation go live, you must have ready "how to let a specific business through without disabling the global policy" |
| **Every policy needs an owner** | Rules with no owner never expire and never get cleaned up. Rules must carry an expiry date and a review cycle |

<div class="zh" markdown="1">

| 经验 | 说明 |
|------|------|
| **三个平面分别设防** | 管理平面（谁能登录）、控制平面（谁能上送 CPU）、数据平面（谁能穿过）。混在一起谈"安全"必然漏掉一边 |
| **准入必须分阶段** | Monitor → Low-Impact → Closed，每阶段都有量化退出条件（失败率、工单量），一步到 Closed 必然回退 |
| **隔离要经得起"路由检查"** | VRF/VLAN 之间只要存在直达路由，隔离就是配置上的假象。跨域一律过有状态设备 |
| **加密与可见性必须显式取舍** | 哪里有 IPsec，哪里就没有 IPS。写进文档，用终端侧手段（EDR/日志关联）补偿 |
| **安全体系有隐性单点** | NTP、AAA/RADIUS、证书/PKI、日志服务器、策略中心。任何一个挂了，全网认证与审计一起失效 |
| **控制面速率要实测** | CoPP、CPPr、BFD 计时器都按实测峰值配，模板默认值在真实流量下经常掐死协议 |
| **变更前先想"降级模式"** | 准入/加密/分段上线前，必须准备好"如何在不关掉全局策略的情况下放行个别业务" |
| **每条策略要有人负责** | 没有责任人的规则不会过期，也不会被清理。规则带到期时间与复核周期 |

</div>

---

## Key Terms · 本章关键术语

| Term | Meaning | One-line memory hook |
|------|---------|-----------|
| **Device hardening** | Hardening network devices | Defend the three planes (management/control/data) separately |
| **Management plane** | Management plane | The path with the worst consequences when compromised |
| **Control plane** | Control plane | Decides forwarding; attacking it affects services along the whole path |
| **Data plane** | Data plane | Carries business traffic; where ACLs/uRPF apply |
| **CoPP** | Control plane policing | Rate-limits punting to the CPU per class; rates must be measured |
| **CPPr** | Control plane protection | A finer-grained CoPP (host/transit/CEF-exception separated) |
| **rACL** | Receive ACL | Only legitimate sources may reach the device itself |
| **iACL** | Infrastructure ACL | Restricts at the boundary "who can reach the infrastructure address space" |
| **uRPF** | Unicast reverse path forwarding | strict/loose/feasible; the mode must match routing symmetry |
| **GTSM** | BGP TTL security | Requires TTL=255, preventing forged neighbors |
| **TCP-AO** | TCP authentication option | The modern replacement for BGP MD5 |
| **RTBH** | Remotely triggered black hole | "Erases" the attack target from routing — self-inflicted damage |
| **RPKI / ROA** | Route origin authorization | Prevents BGP prefix hijacking |
| **DHCP Snooping** | DHCP snooping | Builds the MAC-IP-port binding table that DAI/Source Guard depend on |
| **DAI** | Dynamic ARP inspection | Validates ARP with the binding table; depends on DHCP and does not cover static IPs |
| **IP Source Guard** | IP source guard | Validates the source IP with the binding table; likewise only covers DHCP devices |
| **Port security** | Port security | Limits the MAC count per port; watch out for random MACs |
| **BPDU Guard / Root Guard** | BPDU guard / root guard | BPDU Guard toward endpoints, Root Guard toward downstream switches |
| **Private VLAN** | Private VLAN | isolated/community/promiscuous; mostly replaced today by SGT/micro-segmentation |
| **802.1X** | Port-based admission control | EAP-TLS is strongest, PEAP is common, MAB is the fallback |
| **MAB** | MAC authentication bypass | MACs are forgeable; only for devices without 1X support |
| **MACsec** | Layer 2 encryption | Hop by hop, low overhead, needs hardware; cannot cross a Layer 3 network |
| **SGT / TrustSec** | Security group tag | Authorization decoupled from addresses; **does no threat inspection** |
| **Micro-segmentation** | Micro-segmentation | Data center east-west isolation, implemented on the network or host side |
| **IPsec** | IP Security | ESP tunnel mode is the mainstream choice; watch MTU/MSS |
| **IKEv1 / IKEv2** | Key exchange protocol | Always IKEv2 for new builds |
| **PFS** | Perfect forward secrecy | A master key leak does not affect historical sessions |
| **DMVPN** | Dynamic multipoint VPN | mGRE + NHRP; Phase 3 needs nhrp shortcut + redirect |
| **FlexVPN** | Flexible VPN | A unified framework based on IKEv2; the first choice for new builds |
| **GET VPN** | Group encrypted transport VPN | No tunnels, keeps the original IP header; suits MPLS WANs |
| **Split tunneling** | Split tunneling | Good experience but loses network visibility, so EDR must compensate |
| **Full tunnel** | Full tunnel | Best visibility, high bandwidth and experience cost |
| **ZTNA** | Zero trust network access | Application-level access replaces network-level access |
| **SASE** | Secure access service edge | A nearby PoP converges networking and cloud security |
| **MFA fatigue** | MFA fatigue attack | Counter with number matching / FIDO2 |

<div class="zh" markdown="1">

| 术语 | 中文含义 | 一句话记忆 |
|------|---------|-----------|
| **Device Hardening** | 设备加固 | 三平面（管理/控制/数据）分别设防 |
| **Management Plane** | 管理平面 | 被攻破后果最严重的一条通路 |
| **Control Plane** | 控制平面 | 决定转发决策，攻击它影响全路径业务 |
| **Data Plane** | 数据平面 | 承载业务流量，ACL/uRPF 的作用面 |
| **CoPP** | 控制平面监管 | 按类限速上送 CPU 的流量，速率必须实测 |
| **CPPr** | 控制平面保护 | CoPP 的细化版（host/transit/CEF-exception 分开） |
| **rACL** | 接收 ACL | 只允许合法源访问设备自身 |
| **iACL** | 基础设施 ACL | 在边界限制"谁能访问基础设施地址空间" |
| **uRPF** | 单播反向路径转发 | strict/loose/feasible，模式必须匹配路由对称性 |
| **GTSM** | BGP TTL 安全 | 要求 TTL=255，防伪造邻居 |
| **TCP-AO** | TCP 认证选项 | BGP MD5 的现代替代 |
| **RTBH** | 远端触发黑洞 | 把攻击目标从路由上"抹掉"，自损八百 |
| **RPKI / ROA** | 路由源授权 | 防 BGP 前缀劫持 |
| **DHCP Snooping** | DHCP 侦听 | 建立 MAC-IP-端口绑定表，是 DAI/Source Guard 的基础 |
| **DAI** | 动态 ARP 检测 | 用绑定表校验 ARP，依赖 DHCP，静态 IP 不覆盖 |
| **IP Source Guard** | IP 源保护 | 用绑定表校验源 IP，同样只覆盖 DHCP 设备 |
| **Port Security** | 端口安全 | 限制单端口 MAC 数量，注意随机 MAC |
| **BPDU Guard / Root Guard** | BPDU 保护 / 根保护 | 朝终端用 BPDU Guard，朝下游用 Root Guard |
| **Private VLAN** | 私有 VLAN | isolated/community/promiscuous，现代多被 SGT/微分段替代 |
| **802.1X** | 基于端口的准入 | EAP-TLS 最强，PEAP 常用，MAB 兜底 |
| **MAB** | MAC 认证绕过 | MAC 可伪造，只用于不支持 1X 的设备 |
| **MACsec** | 二层加密 | 逐跳、低开销、需硬件；不能跨三层网络 |
| **SGT / TrustSec** | 安全组标签 | 与地址解耦的授权；**不做威胁检查** |
| **Micro-segmentation** | 微分段 | 数据中心东西向隔离，网络侧或主机侧实现 |
| **IPsec** | IP 安全协议 | ESP 隧道模式是主流；注意 MTU/MSS |
| **IKEv1 / IKEv2** | 密钥交换协议 | 新建一律 IKEv2 |
| **PFS** | 完美前向保密 | 主密钥泄露也不影响历史会话 |
| **DMVPN** | 动态多点 VPN | mGRE + NHRP；Phase 3 需 nhrp shortcut + redirect |
| **FlexVPN** | 灵活 VPN | 基于 IKEv2 的统一框架，新建首选 |
| **GET VPN** | 组加密传输 VPN | 无隧道、保留原始 IP 头，适合 MPLS WAN |
| **Split Tunneling** | 分离隧道 | 体验好但失去网络可见性，必须靠 EDR 补偿 |
| **Full Tunnel** | 全隧道 | 可见性最好，带宽与体验代价大 |
| **ZTNA** | 零信任网络访问 | 应用级访问替代网络级访问 |
| **SASE** | 安全访问服务边缘 | 就近 PoP 融合网络与云安全 |
| **MFA Fatigue** | MFA 疲劳攻击 | 用数字匹配/FIDO2 对抗 |

</div>

---

## Chapter Summary · 本章小结

Chapter 10 turns the principles of Chapter 4 into deployable technology. The main thread of the chapter is **three lines of defense plus one verification chain**:

<div class="zh" markdown="1">

第 10 章把第 4 章的原则变成了可部署的技术，全章的主线是**三层防线 + 一条验证链**：

</div>

```
Management plane compromised = total loss of control → hardening, bastion, OOB, MFA, log offloading
Control plane compromised    = all paths lost        → rACL/iACL, CoPP, GTSM/TCP-AO, RPKI, uRPF
Data plane compromised       = lateral movement      → VLAN/ACL, 802.1X+MAB, SGT, micro-segmentation, encryption
                ↓
        Visibility (NetFlow/logs/NTP alignment) → detect → respond
```

<div class="zh" markdown="1">

```
管理平面被攻破 = 全盘失控    → 加固、跳板机、带外、MFA、日志外送
控制平面被攻破 = 全路径失守  → rACL/iACL、CoPP、GTSM/TCP-AO、RPKI、uRPF
数据平面被攻破 = 横向移动    → VLAN/ACL、802.1X+MAB、SGT、微分段、加密
                ↓
        可见性（NetFlow/日志/NTP 对齐）→ 检测 → 响应
```

</div>

The four judgments most worth taking away:

<div class="zh" markdown="1">

四条最该带走的判断：

</div>

| Judgment | Meaning |
|------|------|
| **Encryption ≠ access control** | IPsec/MACsec solve "cannot see"; whether someone can "get in" depends on authentication and authorization. Neither replaces the other |
| **Admission control must be phased** | Monitor → low-impact → closed. Projects that jump straight to closed almost always end in "rollback" |
| **The credibility of segmentation depends on cross-domain paths** | As long as a direct route exists between VRFs, the isolation is a configuration illusion. Always cross domains through a stateful device |
| **Control plane protection rates must be measured** | CoPP from a template strangles routing protocols, producing the hardest-to-diagnose class of failure: "partially unreachable" |

<div class="zh" markdown="1">

| 判断 | 含义 |
|------|------|
| **加密 ≠ 访问控制** | IPsec/MACsec 解决"看不见"，能不能"进得来"取决于认证与授权。两者不可互相替代 |
| **准入必须分阶段上线** | Monitor → Low-Impact → Closed。一步到 Closed 的项目，几乎都以"回退"结束 |
| **分段的可信度取决于跨域路径** | VRF 之间只要有直达路由，隔离就是配置上的假象。跨域一律过有状态设备 |
| **控制面保护速率要实测** | CoPP 套模板会掐死路由协议，表现为"部分不通"这类最难查的故障 |

</div>

> **One sentence to remember**: **the deliverable of security design is not "which boxes were bought", but "on every cross-domain path, who is allowed through under what conditions, and how you prove it works".**

<div class="zh" markdown="1">

> **一句话记忆**：**安全设计的产出不是"买了哪些盒子"，而是"每条跨域路径上，谁在什么条件下被允许通过，以及你怎么证明它有效"。**

</div>

The 15-item flaw list in this chapter is best used directly as a pre-go-live review checklist: they all come from real outages, and **every one of them looks "correct" in the configuration**.

<div class="zh" markdown="1">

本章的 15 条缺陷清单建议直接当作上线前评审表用：它们全部来自真实故障，且**每一条在配置上看起来都是"对的"**。

</div>
