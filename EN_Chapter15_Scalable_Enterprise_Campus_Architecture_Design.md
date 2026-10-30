# Chapter 15: Scalable Enterprise Campus Architecture Design · 第 15 章：可扩展企业园区架构设计

> English study notes on the *CCDE 400-007 Official Cert Guide* | original pages 708–746
> **Where this chapter sits**: the first chapter of Part III. The previous fourteen chapters answered "how do I choose a single technology" (which Layer 2, which Layer 3, which virtualisation). This chapter answers **how to organise those choices into a campus that can grow**. The same protocol set, placed in a different architecture, behaves completely differently at failure time — the most consistently under-rated point in campus design.

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译与精讲 | 原书第 708-746 页
> **本章定位**：Part III 的第一章。前 14 章解决"单个技术怎么选"（二层用什么、三层用什么、虚拟化用什么），本章解决**"把它们组织成一个能长大的园区"**。同一套协议放在不同架构里，故障时的行为完全不同 —— 这是园区设计最容易被低估的一点。

</div>

---

## What This Chapter Covers · 本章涵盖主题

- **Hierarchical campus design models**: three-tier versus two-tier (collapsed core), and when a dedicated core layer is genuinely required
- **Three access–distribution design models**: multitier STP, routed access, switch clustering; where the L2/L3 boundary belongs
- **Campus Layer 3 routing design**: IGP selection (EIGRP / OSPF) and design, aligning routing with the physical architecture
- **Campus network virtualisation**: many-to-one / one-to-many, fate sharing, four path-isolation techniques
- **Service virtualisation**: firewall virtualisation, VRF-aware NAT, VASI, NFV
- **(Extended in these notes)** capacity models, convergence-time budgets, PoE and wireless, modern fabric (VXLAN/EVPN, SDA)

<div class="zh" markdown="1">

- **园区层次化设计模型**：三层模型（Three-Tier）与二层模型（Two-Tier / Collapsed Core），以及"什么时候真的需要核心层"
- **接入—分布层三种设计模型**：多层 STP、路由接入、交换机集群；L2/L3 分界点放在哪里
- **园区三层路由设计考量**：IGP（EIGRP / OSPF）选型与设计、路由与物理架构对齐
- **园区网络虚拟化**：多对一 / 一对多、命运共享、四种路径隔离技术
- **服务虚拟化**：防火墙虚拟化、VRF-Aware NAT、VASI、NFV
- **（本笔记延伸）** 容量模型、收敛时间预算、PoE 与无线、现代 fabric（VXLAN/EVPN、SDA）

</div>

---

## Chapter Roadmap: Fifteen Counter-intuitive Truths About Campus Design · 本章导读：园区设计的十五个反直觉认知

![Figure 15-1 · Fifteen truths in four themes](assets/fig/en15-01-fifteen-truths.svg)

Most people treat campus design as "draw a topology + configure protocols": three-tier or two-tier, OSPF or EIGRP, vPC or not. What actually decides whether a campus is still healthy in ten years is **how those choices behave together at the moment of failure**. The fifteen statements below are the ones most often got wrong — and most often challenged — in design reviews.

<div class="zh" markdown="1">

很多人把园区设计当成"画拓扑 + 配协议"：选三层还是二层、OSPF 还是 EIGRP、要不要 vPC。真正决定一个园区能活十年的，是**这些选择在故障时刻的联合行为**。以下十五条，是设计评审里最容易说错、也最容易被追问的地方。

</div>

### 1. The First-Order Question Is "How Big Is the Failure Domain", Not "Which Protocol" · 园区设计的第一性问题是"故障域有多大"，不是"用什么协议"

![Figure 15-2 · The failure-domain ladder](assets/fig/en15-02-failure-domain.svg)

Asking "OSPF or EIGRP here?" is like asking "which tyres does this car need?" without asking where you are driving or how bad the roads are.

<div class="zh" markdown="1">

问"这里用 OSPF 还是 EIGRP"，等于问"这台车用什么轮胎"，却没问"你要开去哪、路有多烂"。

</div>

Every design action in a campus is really adjusting one thing: **the blast radius of a failure**.

<div class="zh" markdown="1">

园区里所有设计动作，本质上都在调整一件事：**故障的影响半径**。

</div>

| Design action | What it actually does |
|---|---|
| Splitting into functional blocks (user / DC / WAN / management) | Confines one failure inside one block |
| Position of the L2/L3 boundary | Decides whether "broadcast domain = failure domain" or "subnet = failure domain" |
| Route summarisation | Keeps detail changes outside the area, and creates suboptimal paths while doing so |
| Switch clustering / vPC | Merges two devices' failures into one failure (fate sharing used in the wrong direction) |
| FHRP | Downgrades a gateway failure from "outage" to "switchover" |
| Virtualisation (VRF / VN) | Turns "many services sharing one domain" into "many domains sharing one physical plant" |

<div class="zh" markdown="1">

| 设计动作 | 真实作用 |
|---|---|
| 划分功能块（用户块 / 数据中心块 / WAN 块 / 管理块） | 把一次故障限制在一个块内 |
| L2/L3 分界点位置 | 决定"广播域 = 故障域"还是"子网 = 故障域" |
| 路由汇总 | 把明细变化挡在区域外，同时制造次优路径 |
| 交换机集群 / vPC | 把两台设备的故障合并成一次故障（命运共享的反面用法） |
| FHRP | 把网关故障从"断网"降级为"切换" |
| 虚拟化（VRF / VN） | 把"多个业务共用一个域"变成"多个域共用一套物理" |

</div>

> ⚠️ **The most common review mistake**: treating "high availability" as "buy one more box". Real availability is **failure-domain design × convergence time × detection capability** — miss one and you have none.

<div class="zh" markdown="1">

> ⚠️ **最常见的评审失误**：把"高可用"当成"多买一台设备"。真正的可用性是 **故障域设计 × 收敛时间 × 检测能力**，缺一项等于没有。

</div>

### 2. "Layer 2 Is Simpler" Is the Biggest Illusion in the Campus: the Configuration Is Simple, the Behaviour Is Not · "二层更简单"是园区里最大的错觉：简单的是配置，复杂的是行为

![Figure 15-3 · Nine lines of config, eight pieces of state](assets/fig/en15-03-l2-illusion.svg)

Plug a Layer 2 switch in and it passes traffic; the configuration really is simple. The behavioural complexity only appears when something fails:

<div class="zh" markdown="1">

二层交换机插上就能通，配置确实简单。但二层的行为复杂度在故障时才暴露：

</div>

| Dimension | Layer 2 (STP domain) | Layer 3 (routed domain) |
|---|---|---|
| Will it pass traffic | Depends on STP having converged, no loop, no unidirectional link | Depends on a reachable entry in the routing table |
| Troubleshooting language | MAC table, STP state, broadcast volume | Routing table, neighbour state, traceroute |
| Failure propagation | A loop = broadcast storm, kills the whole VLAN domain in seconds | Route flaps are damped and masked by summarisation |
| Change risk | Adding one cable can create a loop | Adding one cable just adds an equal-cost path |
| Scale ceiling | Bounded by the broadcast domain and STP diameter | Bounded by the routing table and the area design |

<div class="zh" markdown="1">

| 维度 | 二层（STP 域） | 三层（路由域） |
|---|---|---|
| 通不通 | 取决于 STP 是否收敛、是否造环、是否单向链路 | 取决于路由表是否有可达条目 |
| 排障语言 | MAC 表、STP 状态、广播量 | 路由表、邻居状态、traceroute |
| 故障传播 | 环路 = 广播风暴，秒级打死整个 VLAN 域 | 路由抖动有抑制、有汇总遮挡 |
| 变更风险 | 加一根线就可能造环 | 加一根线只多一条等价路径 |
| 规模上限 | 受广播域与 STP 直径约束 | 受路由表与区域设计约束 |

</div>

> 💡 **One-line test**: **if a single link failure can spread across the network and surface as misbehaviour somewhere else, that part of the network is Layer 2.** Layer 3 failures are local by default.

<div class="zh" markdown="1">

> 💡 **一句话判据**：**如果一处链路故障会通过网络"扩散"成多处的行为异常，那它就是二层的。** 三层的故障默认是局部的。

</div>

### 3. Hierarchy Is Not About a Pretty Diagram — It Makes Change Local · 层次化不是为了画图好看，是为了让"变化"局部化

![Figure 15-4 · Hierarchy makes change local](assets/fig/en15-04-change-locality.svg)

The textbook explanation of hierarchy is "clear core / distribution / access responsibilities". Clear responsibility is only the surface; the real benefit is:

<div class="zh" markdown="1">

层次化的标准解释是"核心—分布—接入职责清晰"。但职责清晰只是表象，真正的收益是：

</div>

> **Every expansion, every policy change and every failure affects a predictably small, constant number of devices.**

<div class="zh" markdown="1">

> **每一次扩容、每一次策略变更、每一次故障，影响的设备数量是可预期的小常数。**

</div>

Counter-example: a flat Layer 2 campus of 60 switches. Adding one building (+8 access switches) means moving the STP root, recalculating VLAN pruning, adjusting FHRP priorities, and worrying that a new link's edge port was not configured and will cost 30 seconds of convergence. **Incremental cost rises non-linearly with scale — that is the precise definition of "not scalable".**

<div class="zh" markdown="1">

反例：一个 60 台交换机的扁平二层园区。加一栋楼（+8 台接入）要动 STP 根、要重算 VLAN 裁剪、要调 FHRP 优先级、还要担心新链路的边缘端口没配导致 30 秒收敛。**增量成本随规模非线性上升 —— 这就是"不可扩展"的准确定义。**

</div>

### 4. Convergence Time Is Not "Configured" — It Is the Sum of Every Timer on the Worst Path · 收敛时间不是"配出来的"，是"最坏路径上所有定时器之和"

![Figure 15-5 · Convergence is a sum of timers](assets/fig/en15-05-convergence-waterfall.svg)

Campus outages are almost never a forwarding-performance problem; they are the accumulation of **detection + notification + recomputation + host refresh**. A typical legacy path (multitier STP + FHRP + OSPF):

<div class="zh" markdown="1">

园区中断几乎从来不是转发性能问题，而是 **检测 + 通知 + 重算 + 主机刷新** 的叠加。一条典型的老式路径（多层 STP + FHRP + OSPF）：

</div>

```
Link down → STP detection (BPDU ageing / loss)           1–20 s
          → topology change and reconvergence           1–30 s
          → FHRP detection (HSRP hello 3 s × 3)          9–10 s
          → IGP recomputation (SPF + summarisation)     0.1–5 s
          → host ARP cache invalidation (uncontrolled)  0–300 s
```

<div class="zh" markdown="1">

```
链路断 → STP 检测（BPDU 老化/丢失）        1–20 s
      → 拓扑变化、重新收敛                 1–30 s
      → FHRP 检测（HSRP hello 3 s × 3）    9–10 s
      → IGP 重算（SPF + 汇总）             0.1–5 s
      → 主机 ARP 缓存失效（不可控）         0–300 s
```

</div>

> 🎯 **Design conclusion**: to reach "sub-second switchover", tuning timers only fixes the first two items. **The last mile (host cache, application reconnect) is not yours to control.** The correct campus target is therefore "**≤1 s network convergence + applications that can retry**", not a marketing claim of "50 ms".

<div class="zh" markdown="1">

> 🎯 **设计结论**：想做到"秒级切换"，调小定时器只能解决前两项，**最后一公里（主机缓存、应用重连）你控制不了**。所以园区的正确目标是"**≤1 s 的网络收敛 + 应用可重试**"，而不是"宣称 50 ms"。

</div>

### 5. The Problem With STP Is Not "Slowness" — It Has No Topological Intent · STP 的问题不是"慢"，而是"它没有拓扑意图"

![Figure 15-6 · STP has no topological intent](assets/fig/en15-06-stp-intent.svg)

STP works by "detect a loop, block a port". It does not care about the business. Two classic dilemmas follow:

<div class="zh" markdown="1">

STP 的机制是"发现环路就阻塞一个口"，它不关心业务。于是有两个经典困境：

</div>

1. **Which link gets blocked depends on priority and MAC address**, not on which link is more expensive or faster.
2. **Redundant links sit idle**, and STP still has to be trusted to keep them loop-free — you bought two links, use one, and carry all of the second link's risk.

<div class="zh" markdown="1">

1. **阻塞哪条链路，取决于优先级和 MAC**，而不是"哪条更贵/更快"。
2. **冗余链路平时闲置**，还要靠 STP 保证不出环 —— 买了两条链路只用一条，另一条的风险还全在。

</div>

Later improvements (RSTP fast convergence, MSTP per-instance load sharing, PortFast/BPDU Guard on edge ports) only **contain** the defect; none of them removes it. There are exactly two ways to remove it: **turn L2 into L3 (routed access)**, or **make two devices look like one (switch clustering / vPC)**.

<div class="zh" markdown="1">

后来的改良（RSTP 快速收敛、MSTP 按实例负载分担、PortFast/BPDU Guard 保护边缘）都只是**把缺陷管住**，没有消除它。真正的消除只有两种：**把 L2 变成 L3（路由接入）**，或**让两台设备看起来是一台（交换机集群 / vPC）**。

</div>

> ⚠️ A reality check: even with routed access, **the segment between the access switch and the endpoint is still Layer 2** (endpoints do not run OSPF). "Eliminate Layer 2" is therefore impossible; the correct statement is "**compress Layer 2 into a single wiring closet**".

<div class="zh" markdown="1">

> ⚠️ 现实提醒：即使采用路由接入，**接入交换机到终端之间仍然是二层**（终端不会跑 OSPF）。所以"消灭二层"做不到，正确说法是"**把二层压缩到单个配线间内**"。

</div>

### 6. FHRP Solves "the Gateway Address Never Disappears", Not "the First Hop Never Breaks" · FHRP 解决的是"网关地址不消失"，不是"第一跳不中断"

![Figure 15-7 · What FHRP preserves and what it does not](assets/fig/en15-07-fhrp-reality.svg)

HSRP/VRRP provide a virtual IP plus a virtual MAC. What they solve is: **hosts do not have to change their gateway**. What they do not solve:

<div class="zh" markdown="1">

HSRP/VRRP 提供一个虚拟 IP + 虚拟 MAC，解决的问题是：**主机不用改网关**。它没有解决的问题：

</div>

| Problem | Explanation |
|---|---|
| Packet loss during switchover | Hosts keep sending to the virtual MAC while the new active device has not learned them → brief black hole |
| Partial upstream failure | The active device is alive but its uplink is dead ("a live dead gateway") — needs track / BFD / IP SLA to fail over |
| Asymmetry in active-active forwarding | With vPC + HSRP both forward, so the return path may differ from the forward path |
| Host cache | ARP cache still points at the old MAC until it ages out (uncontrollable) |

<div class="zh" markdown="1">

| 问题 | 说明 |
|---|---|
| 切换期间丢包 | 主备切换时主机仍发往虚拟 MAC，新主未学到 MAC 表 → 短时黑洞 |
| 上行部分失效 | 主设备活着但上行断了（"活着的死网关"），需 track / BFD / IP SLA 才能倒换 |
| 双活转发时的非对称 | vPC + HSRP 时两台都转发，回程可能与去程不同 |
| 主机缓存 | ARP 缓存仍指向旧 MAC，直到老化（不可控） |

</div>

> 💡 **In routed access, FHRP can disappear entirely**: the gateway is the access switch's SVI or routed port, and high availability is delivered by **IGP convergence + BFD** — clearer semantics, zero loop risk.

<div class="zh" markdown="1">

> 💡 **路由接入里 FHRP 可以消失**：网关就是接入交换机的 SVI 或路由口，高可用由 **IGP 收敛 + BFD** 承担，语义更清晰、环路风险为零。

</div>

### 7. Routed Access Moves the Layer 2 Traps Into Layer 3 and Unifies the Troubleshooting Language · 路由接入把二层的坑搬到三层，同时统一了"排障语言"

![Figure 15-8 · Every L2 trap has an L3 twin](assets/fig/en15-08-trap-migration.svg)

Routed access pushes the L2/L3 boundary down to the access switch:

<div class="zh" markdown="1">

路由接入（Routed Access）把 L2/L3 边界下移到接入交换机：

</div>

- **Benefits**: no STP, no FHRP, all uplinks active in ECMP, convergence driven by the IGP (typically an order of magnitude faster than STP), one troubleshooting toolset for the whole campus.
- **Costs**: access switches must run an IGP (platform capability / licensing / CPU), **the same VLAN cannot span multiple access switches** (Layer 2 extension requires an overlay), and every wiring closet becomes its own subnet (IP and DHCP scope counts rise).

<div class="zh" markdown="1">

- **好处**：无 STP、无 FHRP、上行链路 ECMP 全活、收敛由 IGP 决定（通常比 STP 快一个数量级）、全园区一套排障工具。
- **代价**：接入交换机要跑 IGP（设备能力/License/CPU）、**跨接入交换机的同一 VLAN 不存在**（需要 L2 扩展只能靠覆盖网络）、每个配线间变成独立子网（IP 与 DHCP scope 数量上升）。

</div>

> ⚠️ **The most common half-job**: the access switch runs OSPF but all VLAN gateways stay on distribution-layer SVIs. STP dependency is not removed, the routing domain is enlarged, and neither benefit is realised.

<div class="zh" markdown="1">

> ⚠️ **最常见的半吊子**：接入交换机跑了 OSPF，但所有 VLAN 网关仍在分布层 SVI。既没消掉 STP 依赖，又扩大了路由域，两头好处都没拿到。

</div>

### 8. Switch Clustering Is the "Simplest" — and It Welds Two Devices' Failures Into One · 交换机集群最"简单"，但把两台设备的故障绑成一次故障

![Figure 15-9 · Clustering as fate sharing](assets/fig/en15-09-cluster-fate.svg)

Clustering (StackWise / VSS / vPC / mLAG) presents two physical devices as one logical device:

<div class="zh" markdown="1">

集群（StackWise / VSS / vPC / mLAG）把两台物理设备呈现为一台逻辑设备：

</div>

| Benefit | Cost |
|---|---|
| Single management plane (one configuration) | A control-plane fault hits both devices at once (StackWise/VSS especially) |
| No STP blocking, all links active | A full upgrade requires a reload (unless ISSU) |
| Fast convergence (usually sub-second) | **The peer-link / stacking cable becomes a new single point of failure** |
| mLAG supports cross-chassis aggregation | vPC orphan ports, and "dual-active" after a peer-link failure, need a dedicated runbook |

<div class="zh" markdown="1">

| 收益 | 代价 |
|---|---|
| 管理面合一（一份配置） | 控制面故障同时影响两台（StackWise/VSS 尤甚） |
| 无 STP 阻塞、链路全活 | 整机升级需重启（除非 ISSU） |
| 收敛快（通常亚秒） | **peer-link / 堆叠线成为新单点** |
| mLAG 支持跨设备聚合 | vPC orphan 端口、peer-link 故障时的"双主"需专门预案 |

</div>

> 🔥 **Classic clustering incident**: the vPC peer-link fails and peer-keepalive fails too → **dual-active**, both devices answer ARP with the same virtual MAC, gateway/HSRP/STP root all split → broadcast storm plus two gateways. **peer-keepalive must therefore traverse an independent management path** — neither the peer-link nor a service VLAN.

<div class="zh" markdown="1">

> 🔥 **经典集群事故**：vPC peer-link 断、peer-keepalive 也断 → **双主**，两台用同一虚拟 MAC 应答 ARP，网关/HSRP/STP 根同时分裂 → 广播风暴 + 双网关。所以 **peer-keepalive 必须走独立管理链路**（既不是 peer-link，也不是业务 VLAN）。

</div>

### 9. The Three Access Models Differ Not in Bandwidth but in Their Behaviour When Something Fails · 三种接入模型的差别不在带宽，而在"故障时的行为"

![Figure 15-10 · Failure-behaviour matrix](assets/fig/en15-10-three-models-failure.svg)

Beginners compare the three models by calculating bandwidth utilisation (50% versus 100%). In a campus, bandwidth is rarely the bottleneck (1G access with 10G uplinks is the norm). The real differences are:

<div class="zh" markdown="1">

初学者比较三种模型喜欢算带宽利用率（50% vs 100%）。园区里带宽通常不是瓶颈（1G 接入 + 10G 上行是常态），真正的差别是：

</div>

| Failure scenario | Multitier STP | Routed access | Switch clustering |
|---|---|---|---|
| One uplink fails | STP convergence + possible FHRP switchover (10–30 s) | IGP convergence (<1 s, BFD <200 ms) | Member removed from the bundle (<1 s) |
| One distribution switch dies | STP root / gateway switchover (10–30 s) | IGP convergence + ECMP recomputation (<1 s) | Logical device survives (capacity halved) |
| One access switch dies | Only its own attached users | Only its own attached users | If in a stack: **the whole stack reloads**, all users down for 3–10 min |
| Add one cable | May create a loop | Adds one more ECMP path | Joins the bundle automatically |
| Layer 2 loop | **Possible** | Impossible (broadcast domain is bounded) | Impossible |

<div class="zh" markdown="1">

| 故障场景 | 多层 STP | 路由接入 | 交换机集群 |
|---|---|---|---|
| 单条上行断 | STP 收敛 + FHRP 可能切换（10–30 s） | IGP 收敛（<1 s，BFD <200 ms） | 聚合成员减少（<1 s） |
| 单台分布交换机宕 | STP 根/网关切换（10–30 s） | IGP 收敛 + ECMP 重算（<1 s） | 逻辑设备仍在（容量减半） |
| 单台接入交换机宕 | 仅影响本机下挂用户 | 仅影响本机下挂用户 | 若在堆叠中：**整堆重启**，全部用户中断 3–10 min |
| 加一根线 | 可能造环 | 多一条 ECMP 路径 | 自动成为聚合成员 |
| 二层环路 | **可能** | 不可能（广播域被限制） | 不可能 |

</div>

> 🎯 This is the table a review should actually look at. **You are not choosing a bandwidth model, you are choosing failure behaviour.**

<div class="zh" markdown="1">

> 🎯 这张表才是评审该看的。**你选的不是带宽模型，是故障行为。**

</div>

### 10. IGP Selection Is Not "Which Protocol Is Better" but "Team Skill + Convergence Budget + Area/Query Design" · IGP 选型不是"技术优劣"，而是"团队能力 + 收敛预算 + 区域/查询设计"

![Figure 15-11 · IGP selection in three constraints](assets/fig/en15-11-igp-selection.svg)

| Constraint | Leans EIGRP | Leans OSPF |
|---|---|---|
| Vendor and team | Single vendor, team knows DUAL | Multi-vendor, team knows link state |
| Architectural depth | Naturally supports many tiers + summarisation | Requires area design; more tiers = more constraints |
| Convergence control | **stub + summarisation + query scope** | **area design + summarisation + topology hiding** |
| Multi-vendor interoperability | Weak | Strong |
| MPLS-TE | Not supported | Supported (rarely needed inside a campus) |
| Failure-isolation semantics | Distance vector, "trust your neighbour" | Link state, "everyone holds the full map" |

<div class="zh" markdown="1">

| 约束 | 倾向 EIGRP | 倾向 OSPF |
|---|---|---|
| 厂商与团队 | 单一厂商、团队熟 DUAL | 多厂商、团队熟链路状态 |
| 架构层级 | 天然支持多层级 + 汇总 | 需按区域设计，层级越多越受限 |
| 收敛控制 | **stub + 汇总 + 查询范围** | **区域划分 + 汇总 + 拓扑隐藏** |
| 多厂商互操作 | 弱 | 强 |
| MPLS-TE | 不支持 | 支持（园区内基本用不到） |
| 故障隔离语义 | 距离矢量，"信任邻居" | 链路状态，"每台都有全图" |

</div>

> ⚠️ **EIGRP trap**: without query-scope control (stub, summarisation), one flap floods queries network-wide and triggers SIA (three minutes by default) — convergence goes from milliseconds to minutes.
>
> ⚠️ **OSPF trap**: when several ABRs summarise the same prefix, a failure can produce **suboptimal routing** (traffic detours via the other ABR). That is an inherent cost of summarisation, not a configuration error.

<div class="zh" markdown="1">

> ⚠️ **EIGRP 陷阱**：不做查询范围控制（stub、汇总），一次抖动会让查询扩散全网，触发 SIA（默认 3 分钟），收敛从毫秒变分钟。
>
> ⚠️ **OSPF 陷阱**：多个 ABR 同时汇总时，故障后可能出现**次优路由**（流量绕行另一台 ABR），这是汇总的固有代价，不是配置错误。

</div>

### 11. The Real Cost of Campus Virtualisation Is "Operational Mental Load" and "Time to Locate a Fault" · 园区虚拟化的真实成本是"运维心智"和"故障定位时间"

![Figure 15-12 · Virtualisation concentrates work](assets/fig/en15-12-virt-load.svg)

Virtualisation (VRF, VN, MPLS VPN) sells "many logical networks on one physical plant". The on-paper benefits (CAPEX/OPEX, service velocity) look great in a slide deck; the hidden costs rarely make it into the design document:

<div class="zh" markdown="1">

虚拟化（VRF、VN、MPLS VPN）的卖点是"多张逻辑网络共用一套物理"。账面收益（CAPEX/OPEX/开通速度）在 PPT 上很清楚，隐形成本很少写进设计文档：

</div>

| Hidden cost | How it shows up |
|---|---|
| Time to locate a fault | "The application is unreachable" now means checking VRF membership → leak points → service policy → tunnel encapsulation → physical link |
| Change coupling | Changing one VRF's route target (RT) can affect a different network |
| Monitoring semantics | Metrics, logs and flows all need VRF/VN dimensions; legacy platforms often cannot do it |
| Skills | From "configure a VLAN" to "configure a routing instance + policy + service chain" — a steep curve |
| Capacity attribution | One VN's burst steals capacity from other VNs on the same hardware (no hard isolation without QoS) |

<div class="zh" markdown="1">

| 隐形成本 | 具体表现 |
|---|---|
| 故障定位时间 | "业务不通"要依次排除：VRF 归属 → 泄漏点 → 服务策略 → 隧道封装 → 物理链路 |
| 变更耦合 | 改一个 VRF 的路由目标（RT）可能影响另一张网 |
| 监控口径 | 指标/日志/流量都要带 VRF/VN 维度，老平台通常不支持 |
| 人员技能 | 从"配 VLAN"变成"配路由实例 + 策略 + 服务链"，曲线陡峭 |
| 容量归属 | 一张 VN 的突发会挤占同物理设备上的其他 VN（无硬隔离，除非 QoS） |

</div>

> 💡 **Decision rule**: **virtualise only when the business value of isolation exceeds the operational cost of isolation.** If three business domains can be separated with VLANs + ACLs, do not deploy MPLS VPN to prove a point.

<div class="zh" markdown="1">

> 💡 **决策原则**：**只有当"隔离的业务价值 > 隔离的运维成本"时才做虚拟化。** 三个业务域用 VLAN + ACL 能解决，就不要上 MPLS VPN。

</div>

### 12. Path Isolation Is Not Security Isolation (a VRF Is Not a Firewall) · 路径隔离 ≠ 安全隔离（VRF 不是防火墙）

![Figure 15-13 · A VRF is not a firewall](assets/fig/en15-13-vrf-not-firewall.svg)

| Expectation | Reality |
|---|---|
| "Putting them in different VRFs makes it secure" | A VRF is only **routing-table isolation**; once a leak point exists (RT import, shared services, fusion router), Layer 3 reachability exists |
| "Different VRFs cannot reach each other" | Any device that imports both sets of routes enables reachability, and **there is no policy by default** |
| "Isolated, so no ACL or firewall is needed" | Direction, stateful inspection and application-layer control: a VRF provides none of them |

<div class="zh" markdown="1">

| 期望 | 现实 |
|---|---|
| "放到不同 VRF 就安全了" | VRF 只是**路由表隔离**；一旦出现泄漏点（RT 导入、共享服务、fusion router），三层可达就成立 |
| "不同 VRF 不能互访" | 只要有设备同时导入双方路由就能互访，且**默认无策略** |
| "隔离了就不需要 ACL/防火墙" | 方向性、状态检测、应用层控制，VRF 一个都不提供 |

</div>

> ⚠️ **Correct statement**: a VRF provides **separation of addressing and routing**; the security boundary must come from **ACLs / firewalls / micro-segmentation**. The two are orthogonal and cannot substitute for each other.

<div class="zh" markdown="1">

> ⚠️ **正确表述**：VRF 提供**寻址与路由的分离**；安全边界必须由 **ACL / 防火墙 / 微分段** 提供。两者正交，不能互相替代。

</div>

### 13. The Real Bottleneck of Service Virtualisation Is the Return Path, Not Throughput · 服务虚拟化的真正瓶颈是"回流路径"，不是吞吐

![Figure 15-14 · The bottleneck is the return path](assets/fig/en15-14-return-path.svg)

After inserting virtual firewalls or load balancers, the most common failure mode is not "not enough performance" but:

<div class="zh" markdown="1">

引入防火墙/负载均衡虚拟化后，最常见的故障形态不是"性能不够"，而是：

</div>

```
User → service node (vFW) → server
                          ↘ return path straight through the core → user   ← state not synchronised, session dropped
```

<div class="zh" markdown="1">

```
用户 → 服务节点(vFW) → 服务器
                    ↘ 回程直接走核心 → 用户     ← 状态不同步，会话被丢弃
```

</div>

| Symptom | Root cause |
|---|---|
| Connection establishes, then stalls on large transfers | Asymmetric return path; the firewall only sees one direction |
| Large packets fail, small packets fine | MTU/MSS (tunnel or service-chain encapsulation) |
| Slow first time, normal afterwards | Cold session table plus policy matching |
| Some clients cannot connect at all | VRF-aware NAT with overlapping addresses, or pool exhaustion |
| Cannot be troubleshot | Traffic "hops" between VRFs, so capture points are discontinuous |

<div class="zh" markdown="1">

| 症状 | 根因 |
|---|---|
| 连接能建立，传大文件卡死 | 非对称回程，防火墙只看到单向流量 |
| 大包不通、小包正常 | MTU/MSS（隧道或服务链封装） |
| 首次慢、之后正常 | 会话表冷启动 + 策略匹配 |
| 部分客户端全不通 | VRF-Aware NAT 地址重叠或地址池耗尽 |
| 排查不了 | 流量在 VRF 间"跳"，抓包点不连续 |

</div>

> 🎯 **Design action**: a service chain must have its **return path explicitly designed** (symmetric PBR steering, VASI / service insertion, or placing the service node on the VRF's only exit), and both the forward and return arrows must be drawn in the document. One arrow only = an incident later.

<div class="zh" markdown="1">

> 🎯 **设计动作**：服务链必须**显式设计回程**（PBR 对称引流、VASI/服务插入，或把服务放在 VRF 必经路径上），并在文档里画出"去程/回程"两条箭头。只画一条箭头 = 后面一定出事故。

</div>

### 14. Wireless Makes Layer 2 a First-Class Citizen Again · 无线让"二层"重新变成第一公民

![Figure 15-15 · Wireless puts L2 back in charge](assets/fig/en15-15-wireless-l2.svg)

In the wired world, routed access can compress Layer 2 into the wiring closet — but wireless drags Layer 2 back:

<div class="zh" markdown="1">

有线时代可以用路由接入把二层压缩到配线间，但无线把二层又拉回来了：

</div>

| New problem introduced by wireless | Architectural impact |
|---|---|
| Roaming wants the same subnet (L2 roaming) | Needs a large Layer 2 domain across APs/controllers, or L3 roaming (anchoring / fabric) |
| The AP itself is an endpoint | The AP management address and the CAPWAP termination point decide the traffic path |
| Voice is sensitive to roaming interruptions | 802.11r/k/v + fast keys + a controller-level handover budget |
| Guest / BYOD isolation | Separate VN/VLAN + separate policy + separate exit |

<div class="zh" markdown="1">

| 无线引入的新问题 | 对架构的影响 |
|---|---|
| 漫游要求同一子网（L2 漫游） | 需要跨 AP/跨控制器的大二层，或 L3 漫游（锚定/fabric） |
| AP 本身是"终端" | AP 管理地址与 CAPWAP 终结位置决定流量路径 |
| 语音对漫游中断敏感 | 802.11r/k/v + 快速密钥 + 控制器级切换预算 |
| 访客/BYOD 隔离 | 独立 VN/VLAN + 独立策略 + 独立出口 |

</div>

> 💡 **Modern answer**: either **keep the traffic local** (FlexConnect + local VLAN — simple, but the roaming domain is limited), or **put wireless into the fabric** (VXLAN + centralised policy — unified, but dependent on overlay stability).

<div class="zh" markdown="1">

> 💡 **现代解法**：要么"**流量本地出**"（FlexConnect + 本地 VLAN，简单但漫游域受限），要么"**无线进 fabric**"（VXLAN + 集中策略，统一但依赖 overlay 稳定性）。

</div>

### 15. Scalability Means "Is the Incremental Cost Linear", Not "How Many Can It Hold" · 可扩展性 = "增量的成本是否线性"，不是"能装多少台"

![Figure 15-16 · Scalability is the slope, not the maximum](assets/fig/en15-16-scalability-linear.svg)

"How many users can this design support?" is the wrong question. The right question is:

<div class="zh" markdown="1">

"这个设计能支持多少人"是错问题。对的问题是：

</div>

> **Going from 1,000 endpoints to 10,000 endpoints, what exactly do I have to change?**

<div class="zh" markdown="1">

> **从 1,000 终端增加到 10,000 终端，我需要动什么？**

</div>

| Architecture | What 1k → 10k requires |
|---|---|
| Flat Layer 2, single block | Re-plan VLANs, STP and gateways — effectively a rebuild |
| Three-tier with functional blocks | Add functional blocks (copy the template), add core ports and bandwidth |
| Routed access + summarisation | Add wiring closets (copy the template); the IGP converges itself; summaries unchanged |
| Fabric (VXLAN/EVPN) | Add leaves (zero-touch onboarding), control plane discovers them |

<div class="zh" markdown="1">

| 架构 | 从 1k → 10k 需要的动作 |
|---|---|
| 扁平二层单块 | 重规划 VLAN/STP/网关，几乎重做 |
| 三层模型 + 功能块 | 加功能块（复制模板），核心加端口/带宽 |
| 路由接入 + 汇总 | 加配线间（复制模板），IGP 自动收敛，汇总不变 |
| fabric（VXLAN/EVPN） | 加 leaf（零配置上线），控制面自动发现 |

</div>

> 🎯 **The metric for scalability**: **how many non-templated configuration changes does one new "standard unit" (a building / a closet / a floor) require?** If the answer is zero, it is scalable; if it grows with size, it is not.

<div class="zh" markdown="1">

> 🎯 **可扩展性的度量**：**新增一个"标准单元"（一栋楼 / 一个配线间 / 一层楼）需要多少个"非模板化"配置变更？** 答案是 0，就是可扩展；随规模增长，就不是。

</div>

---

## The Six-Step Campus Design Method · 园区设计的六步方法论

![Figure 15-17 · The six-step method](assets/fig/en15-17-six-steps.svg)

The most common mistake in campus design is starting from "choose a protocol". The correct order is: **define the boundaries, then the tiers, then the boundary point, then the routing, then the virtualisation, and finally capacity and validation**.

<div class="zh" markdown="1">

园区设计最容易犯的错，是从"选协议"开始。正确顺序是：**先定边界，再定层次，再定分界点，再定路由，再定虚拟化，最后定容量与验证**。

</div>

```
1 Boundaries  business / security / failure domains → list of functional blocks
2 Tiers       three-tier or two-tier (collapsed core) → does the core exist
3 Boundary    L2/L3 edge at distribution or access → pick one of the three access models
4 Routing     IGP choice + area/query design + summary boundaries + dual stack
5 Virt.       VRF/VN granularity + path-isolation technique + service chaining
6 Capacity    ports / bandwidth / PoE / RIB / VLANs / convergence budget + acceptance plan
```

<div class="zh" markdown="1">

```
① 划边界    业务域 / 安全域 / 故障域  → 功能块清单
② 定层次    三层 or 二层（collapsed core）→ 核心是否存在
③ 定分界点  L2/L3 边界放分布层还是接入层 → 三种接入模型选一
④ 定路由    IGP 选型 + 区域/查询设计 + 汇总边界 + 双栈
⑤ 定虚拟化  VRF/VN 粒度 + 路径隔离技术 + 服务链
⑥ 定容量    端口/带宽/PoE/路由表/VLAN/收敛预算 + 验收方案
```

</div>

### Expanding the Six Steps: Inputs, Outputs and the Hurdle You Cannot Skip · 六步展开：每步的输入、输出与"过不去的坎"

| Step | Input | Output (deliverable) | The hurdle that must be settled on the spot |
|---|---|---|---|
| 1 Boundaries | Org chart, service catalogue, compliance requirements, existing sites | Functional-block list + endpoints/bandwidth/availability class per block | **Whose traffic must reach whom** (decides whether inter-block traffic crosses a policy device) |
| 2 Tiers | Number of functional blocks, building layout, fibre availability | Three-tier or two-tier + core location and form | More than three blocks on a collapsed core is technical debt by design |
| 3 Boundary | Endpoint types, wireless share, cross-building L2 needs | Access model (STP / routed access / clustering) | **Is there Layer 2 that must span closets** (wireless roaming, legacy apps, cluster heartbeats) |
| 4 Routing | Team skills, platform capability, convergence budget | IGP + area/query design + summary table + FHRP/BFD plan | Is EIGRP stub/summarisation actually configured; is OSPF summary suboptimality acceptable |
| 5 Virtualisation | Isolation needs (business/tenant/compliance), shared services | VRF/VN count + isolation technique + service-chain topology | **Where service nodes sit and how the return path flows** (truth 13) |
| 6 Capacity | Endpoint density, application bandwidth, PoE budget, addressing plan | Capacity table + convergence budget + acceptance cases | Have the "invisible" wireless bandwidth and PoE power actually been calculated |

<div class="zh" markdown="1">

| 步骤 | 输入 | 输出（交付物） | 过不去的坎（必须当场解决） |
|---|---|---|---|
| ① 划边界 | 组织架构、业务清单、合规要求、现有站点 | 功能块清单 + 每块的终端数/带宽/可用性等级 | **谁的流量必须互访**（决定块间是否要过策略设备） |
| ② 定层次 | 功能块数量、楼栋分布、光纤资源 | 三层 / 二层模型 + 核心位置与形态 | 功能块 >3 个还要 collapsed core，等于给未来埋债 |
| ③ 定分界点 | 终端类型、无线占比、跨楼 L2 需求 | 接入模型（STP / 路由接入 / 集群） | **是否有必须跨配线间的二层**（无线漫游、老应用、集群心跳） |
| ④ 定路由 | 团队技能、设备能力、收敛预算 | IGP + 区域/查询设计 + 汇总表 + FHRP/BFD 方案 | EIGRP stub/汇总是否真的配了；OSPF 汇总点的次优是否可接受 |
| ⑤ 定虚拟化 | 隔离需求（业务/租户/合规）、服务共享 | VRF/VN 数量 + 隔离技术 + 服务链拓扑 | **服务节点放哪、回程怎么走**（第 13 条） |
| ⑥ 定容量 | 终端密度、应用带宽、PoE 预算、地址规划 | 容量表 + 收敛预算 + 验收用例 | 无线与 PoE 的"隐形带宽/功率"是否算过 |

</div>

> 🎯 **The order cannot be reversed**: pick OSPF first and then wonder "do we need VRFs", and you end up with a pile of routing processes and nowhere to attach policy. **Boundaries determine protocols; protocols do not determine boundaries.**

<div class="zh" markdown="1">

> 🎯 **顺序不能反**：先选 OSPF 再想"要不要 VRF"，结果一定是"路由进程一堆、策略无处落"。**边界决定协议，协议不决定边界。**

</div>

### Common Short-Cuts and Their Consequences · 每一步的常见"跳步"及其后果

| Short-cut | Consequence (usually explodes 6–18 months later) |
|---|---|
| Skip 1, go straight to 2 | Blocks are split by floor, so security and business boundaries do not line up; ACLs compensate forever |
| Skip 3, go straight to 4 | OSPF is chosen but Layer 2 is still multiple STP domains; gateway and routing boundaries disagree, failure domain is enormous |
| Skip 5 and just buy hardware | "Compliance" is implemented with physical separation; rack and licence cost doubles |
| Skip 6 and go live | AP power budget too small, DHCP pools exhausted, nobody has ever measured convergence |

<div class="zh" markdown="1">

| 跳步 | 后果（通常 6–18 个月后爆发） |
|---|---|
| 跳过①直接② | 功能块按"楼层"分，结果安全和业务边界对不上，后期全靠 ACL 补 |
| 跳过③直接④ | 选了 OSPF 但二层仍是多块 STP，网关和路由边界不一致，故障域巨大 |
| 跳过⑤直接买设备 | 用物理隔离实现"合规"，机柜和许可成本翻倍 |
| 跳过⑥直接上线 | 无线 AP 功率预算不足、地址池耗尽、收敛时间没人测过 |

</div>

---

## Foundation Topics · 基础内容

---

## 1. The Campus Hierarchy Model: Three Tiers or Two · 一、园区分层模型：三层还是二层

![Figure 15-18 · Three tiers or two](assets/fig/en15-18-three-vs-two-tier.svg)

A campus network covers a single geographic location (one building or several). The enterprise usually owns the physical cabling inside the campus, so a high-speed infrastructure (1/10/40/100 Gbps) can be deployed — **which is what makes campus design far more free than WAN design**: bandwidth is cheap, latency is controllable, and the bottleneck is almost always "architecture and failure domain" rather than "link speed".

<div class="zh" markdown="1">

园区网络覆盖单一地理位置（一栋楼或多栋楼），企业通常拥有园区内的物理线缆，因此可以部署高速基础设施（1/10/40/100 Gbps）——**这一点决定了园区的设计自由度远高于 WAN**：带宽便宜、时延可控，瓶颈几乎总在"架构与故障域"，而不是"链路速率"。

</div>

### Role Separation in the Three-Tier Model (More Than the Words "Three Tiers") · 三层模型的职责划分（不只是"三层"三个字）

```
              +--------------------------+
              |         Core layer       |  High-speed interconnect between blocks
              |  (no policy, no access)  |
              +---+------------------+---+
        +---------+--+          +----+---------+
        | Block A    |          | Block B      |  Each block has its own
        | Distribution|         | Distribution |  distribution layer
        +---+------+--+         +--+-------+---+
       +----+--++--+----+      +--+---+ +---+--+
       |Access ||Access |      |Access| |Access|  Endpoint attachment
       +-------+--------+      +------+ +------+  (L2 to the desk)
```

<div class="zh" markdown="1">

```
              ┌──────────────────────────┐
              │        核心层 Core        │  高速互连多个功能分布块
              │   （不做策略、不做终端）    │
              └───┬──────────┬───────────┘
        ┌─────────┴──┐   ┌───┴────────┐
        │ 分布块 A    │   │ 分布块 B    │   每个块有独立分布层
        │  Distribution│  │ Distribution│   （用户块/DC块/WAN块/管理块）
        └───┬──────┬──┘   └──┬───────┬─┘
       ┌────┴──┐┌──┴────┐ ┌───┴───┐┌──┴────┐
       │接入层  ││接入层  │ │接入层  ││接入层  │  终端接入（L2 到桌面）
       └───────┘└────────┘ └───────┘└───────┘
```

</div>

| Layer | Responsibility (book definition + practical reading) | What it must not do |
|---|---|---|
| **Core** | Provide high-speed interconnect between functional distribution blocks; recover fast and smoothly from a failure in any core block | No endpoints, no fine-grained ACL/QoS policy, no NAT, no service insertion |
| **Distribution** | Provide policy-based connectivity; the boundary control point between access and core; **traditionally the L2/L3 boundary** | Avoid heavy endpoint attachment; do not redistribute across blocks |
| **Access** | Provide workgroup/user attachment; the first hop of the security boundary (port security, authentication, PoE) | No cross-block routing decisions (except in the routed-access model) |

<div class="zh" markdown="1">

| 层级 | 职责（原书定义 + 落地解读） | 不该做的事 |
|---|---|---|
| **核心层** | 提供高速互连，把多个功能分布块连接起来；具备适当弹性，在任何核心块内故障后快速平稳恢复 | 不接终端、不做 ACL/ QoS 精细策略、不做 NAT、不做服务插入 |
| **分布层** | 提供基于策略的连接，是接入与核心之间的边界控制点；**传统上是 L2/L3 分界点** | 不做过多的终端接入；不承担跨块路由重分发 |
| **接入层** | 提供工作组/用户对网络的接入；安全边界的第一跳（端口安全、认证、PoE） | 不做跨块路由决策（除非路由接入模型） |

</div>

> 💡 **The core "does no policy" not out of dogma but for predictability**: once the core carries policy, every single ACL change carries network-wide change risk — and the core's change window is usually the shortest while its blast radius is the largest.

<div class="zh" markdown="1">

> 💡 **核心层"不做策略"的原因不是教条，而是可预测性**：核心一旦承载策略，任何一条 ACL 的变更都会引入"全网可能受影响"的变更风险；而核心的变更窗口通常最短、影响面最大。

</div>

### The Two-Tier Model (Collapsed Core / Two-Tier) · 二层模型

```
        +------------------------------+
        | Core + distribution collapsed|  Carries both interconnect and the policy edge
        +----+------------------+------+
        +----+----+        +----+----+
        |Access A |        |Access B |
        +---------+        +---------+
```

<div class="zh" markdown="1">

```
        ┌──────────────────────────────┐
        │  核心 + 分布 合一（Collapsed） │  同时承担互连与策略边界
        └────┬──────────────┬──────────┘
        ┌────┴────┐    ┌────┴────┐
        │ 接入层 A │    │ 接入层 B │
        └─────────┘    └─────────┘
```

</div>

**When it fits**: small to medium campuses, with **no more than three functional distribution blocks**.

<div class="zh" markdown="1">

**适用**：小到中型园区，**功能分布块最好不超过 3 个**。

</div>

> 💡 **Definition of a functional distribution block**: any block in the campus that owns its own distribution layer — user access block, WAN block, data centre block, management block, DMZ block. Each counts as one. **Many design incidents come from counting only "user buildings" and forgetting that WAN, DC and DMZ are blocks too.**

<div class="zh" markdown="1">

> 💡 **"功能分布块"（Functional Distribution Block）的定义**：园区中任何拥有自己分布层的块 —— 用户接入块、WAN 块、数据中心块、管理块、DMZ 块，各算一块。**很多设计事故源于只数"用户楼栋"，忘了 WAN/DC/DMZ 也是块。**

</div>

### When a Dedicated Core Layer Is Genuinely Required · 什么时候真的需要独立核心层

The book is explicit: **not every design needs a separate core layer.** Two conditions justify a core (either one is enough if strong enough):

<div class="zh" markdown="1">

原书明确：**不是每个设计都需要独立核心层**。核心层存在的两个条件（同时或任一足够强）：

</div>

| Condition | Quantified signal |
|---|---|
| The number of functional distribution blocks grows | More than three blocks, with any-to-any connectivity requirements |
| The number of inter-block links grows sharply | Full mesh needs n(n−1)/2 links: 10 links at n=5, 28 links at n=8 → physical and control-plane complexity explodes |

<div class="zh" markdown="1">

| 条件 | 量化信号 |
|---|---|
| 功能分布块数量上升 | >3 个块，且块间存在任意互访需求 |
| 块间互连数量显著增长 | 全互联所需链路数 = n(n−1)/2，n=5 时 10 条、n=8 时 28 条 → 物理与控制平面复杂度爆炸 |

</div>

```
No core needed (few blocks, simple mesh)     Core needed (many blocks, complex mesh)
   Block-A ---- Block-B                       Block-A   Block-B   Block-C
      |  \      /  |                             |  \       |      /  |
      |   \    /   |                             |   \      |     /   |
      +----\  /----+                           +-+----\-----+----/----+-+
   Block-C (3 blocks, 3 links)                 |          Core            |
                                               +--------------------------+
                                                 (n blocks need only n uplinks)
```

<div class="zh" markdown="1">

```
不需要核心（块少、互连简单）              需要核心（块多、互连复杂）
   Block-A ──── Block-B                    Block-A   Block-B   Block-C
      │  ╲    ╱  │                            │  ╲       │      ╱  │
      │   ╲  ╱   │                            │   ╲      │     ╱   │
      └────╳─────┘                          ┌─┴────╲────┼────╱────┴─┐
   Block-C（3 块全互联 3 条链路）            │        核心层           │
                                            └────────────────────────┘
                                              （n 块只需 n 条上行）
```

</div>

> ⚠️ **Anti-pattern**: adding a core because "a core is a layer you must have". Three-tier with only two blocks = one extra hop, one extra device pair, one extra failure point, zero benefit.

<div class="zh" markdown="1">

> ⚠️ **反模式**：把"核心"当成"必须有的一层"而硬加。三层模型 + 只有 2 个块 = 多一跳、多一对设备、多一个故障点，收益为零。

</div>

### Two-Tier vs Three-Tier: A Business-Driven Selection Table · 二层 vs 三层：业务驱动的选择表

The book anchors the decision in **business dimensions**, not technical ones. This is the classic CCDE way of thinking:

<div class="zh" markdown="1">

原书把选择依据放在**业务维度**，而不是技术维度。这是 CCDE 的典型思路：

</div>

| Factor | Leans two-tier | Leans three-tier |
|---|---|---|
| Site type | Remote branch, small campus | Regional headquarters, main campus |
| Growth potential | Low (a small site rarely needs three tiers) | High (a headquarters can grow substantially) |
| Cost pressure | CAPEX is a hard constraint (buy fewer boxes) | Long-term OPEX and evolvability matter more |
| Business plans | No expansion or acquisition plans | Acquisitions, rapid growth, new services coming |
| Operations team | Small team, Layer 2 skills | Dedicated network team comfortable with IGPs |
| Buildings and distance | One building, or closely adjacent buildings | Multiple buildings, inter-campus fibre, many blocks |

<div class="zh" markdown="1">

| 因素 | 倾向二层模型 | 倾向三层模型 |
|---|---|---|
| 站点类型 | 远程分支、小型园区 | 区域总部、主园区 |
| 未来扩展潜力 | 低（小站点很少需要三层） | 高（总部可能大幅增长） |
| 成本约束 | CAPEX 是硬约束（少买设备） | 长期 OPEX 与可演进性更重要 |
| 业务计划 | 无扩张/并购计划 | 有并购、快速扩张、新业务上线 |
| 运维团队 | 人少、技能偏二层 | 有专职网络团队、熟悉 IGP |
| 楼栋与距离 | 单楼或紧邻多楼 | 多楼、跨园区光纤、多分布块 |

</div>

#### "Build Today with Tomorrow in Mind" and the Gold-Plating Boundary · "Build Today with Tomorrow in Mind" 与 Gold Plating 的边界

> The book's key reminder: **"build for tomorrow" slides very easily into over-design (gold plating)**. The default CCDE position is: **solve today's problem, no more and no less, unless the scenario explicitly provides a future requirement.**

<div class="zh" markdown="1">

> 原书的关键提醒：**"为明天而建"很容易滑向过度设计（Gold Plating）**。CCDE 的默认立场是：**解决当前问题，不多不少，除非场景明确给出未来需求。**

</div>

Test: a "future requirement" may enter the design inputs only if it satisfies at least one of these —

<div class="zh" markdown="1">

判据：一个"未来需求"能进入设计输入，需要满足至少一条 ——

</div>

1. It is already in a budget or planning document (not "the boss might want it").
2. It is dictated by physical constraints (cabling life of 10–15 years, rack space, fibre strand count).
3. It is dictated by an irreversible decision (addressing plan, AS number, domain name, VRF/VN naming and numbering).
4. It is dictated by a compliance requirement (isolation, retention, audit).

<div class="zh" markdown="1">

1. 已在预算/规划文件中（不是"领导可能会想"）
2. 由物理约束决定（布线寿命 10–15 年、机柜空间、光纤芯数）
3. 由不可逆决策决定（地址规划、AS 号、域名、VRF/VN 命名与编号）
4. 由合规要求决定（隔离、保留期、审计）

</div>

Counter-example (gold plating): jumping straight to a 100G core with MPLS VPN and a full VRF design for a "possible threefold growth" while the site currently has 800 endpoints and 3 VLANs.

<div class="zh" markdown="1">

反例（属于 Gold Plating）：为"可能的三倍增长"直接上 100G 核心 + MPLS VPN + 全套 VRF，而当前只有 800 个终端、3 个 VLAN。

</div>

#### The Real CAPEX vs OPEX Trade-off · CAPEX 与 OPEX 的真实权衡

```
Short-term view: squeeze CAPEX → choose a two-tier collapse (fewer boxes)
        ↓
If designed poorly: growth means "tear it down and start again"
        ↓
Long-term OPEX explodes (migration windows, double operations, migration risk)
```

<div class="zh" markdown="1">

```
短期视角：压低 CAPEX → 选二层 collapse（少设备）
        ↓
若设计不当：业务扩展时只能"推倒重来"
        ↓
长期 OPEX 暴涨（改造窗口、双倍运维、迁移风险）
```

</div>

> 🎯 **The CCDE view**: enterprises usually watch CAPEX and never cost the OPEX caused by poor design. The network designer's job is to **put OPEX in numbers** (migration hours, outage risk, headcount) and win the budget for the correct design — that is a communication deliverable that comes with the design.

<div class="zh" markdown="1">

> 🎯 **CCDE 观点**：企业常常只盯 CAPEX，不计算"设计不当导致的 OPEX"。网络设计师的职责是**把 OPEX 讲成数字**（改造工时、停机风险、人力），争取正确设计所需的预算 —— 这是设计之外的"沟通交付物"。

</div>

---

## 2. The Three Access–Distribution Design Models · 二、接入—分布层三种设计模型

![Figure 15-19 · The three access models](assets/fig/en15-19-three-access-models.svg)

The book offers three ways to connect the access layer to the distribution layer. **The core difference is only two things: where the L2/L3 boundary sits, and who provides the Layer 3 gateway service.**

<div class="zh" markdown="1">

原书给出三种把接入层接到分布层的模型，**核心差异只有两点：L2/L3 边界放哪里、L3 网关服务由谁提供**。

</div>

### Model 1: Multitier STP Based · 模型一：多层 STP

```
  Distribution A (L2+L3, FHRP)        Distribution B (L2+L3, FHRP)
  +------------------+                +------------------+
  | SVI / HSRP gateway|               | SVI / HSRP gateway|
  +---+----------+---+                +---+----------+---+
      |  Trunk   |  Trunk (blocked by STP)  |  Trunk   |
  +---+----------+--------------------------+----------+---+
  |            Access switch (pure L2, STP edge)            |
  +---------------------------+-----------------------------+
                              | access port
                        Endpoint (VLAN 10)
```

<div class="zh" markdown="1">

```
   分布层 A（L2+L3, FHRP）        分布层 B（L2+L3, FHRP）
   ┌──────────────────┐          ┌──────────────────┐
   │ SVI/HSRP 网关      │          │ SVI/HSRP 网关      │
   └───┬──────────┬───┘          └───┬──────────┬───┘
       │  Trunk   │  Trunk（被 STP 阻塞）│  Trunk    │
   ┌───┴──────────┴───────────────────┴───────────┴──┐
   │            接入交换机（纯 L2，STP 边缘）           │
   └───────────────────┬──────────────────────────────┘
                       │ access port
                   终端（VLAN 10）
```

</div>

| Characteristic | Explanation |
|---|---|
| L2/L3 boundary | Distribution layer (SVIs on the distribution switches) |
| Redundancy mechanism | **STP blocks one uplink + FHRP active/standby gateway** |
| Link utilisation | ~50% (one active path per VLAN) |
| Convergence | STP convergence plus FHRP switchover, typically 10–30 s (RSTP can bring it to 2–5 s) |
| Troubleshooting | Needs a network-wide STP view + FHRP state + MAC tables |
| Where it fits | Brownfield upgrades, tight budgets, low endpoint density, Layer 2 required across closets |

<div class="zh" markdown="1">

| 特征 | 说明 |
|---|---|
| L2/L3 边界 | 分布层（SVI 在分布交换机） |
| 冗余机制 | **STP 阻塞其中一条上行 + FHRP 主备网关** |
| 链路利用率 | ~50%（每 VLAN 一条活跃路径） |
| 收敛 | STP 收敛 + FHRP 切换叠加，通常 10–30 s（RSTP 可压到 2–5 s） |
| 排障 | 需要 STP 域全局视图 + FHRP 状态 + MAC 表 |
| 适用 | 存量改造、预算紧、终端密度低、跨配线间需大二层 |

</div>

**Protections you must configure** (miss one and you get "the whole campus mysteriously stalls"):

<div class="zh" markdown="1">

**必须配置的保护**（缺一项就会出现"莫名全网卡顿"）：

</div>

- PortFast + BPDU Guard (ports facing endpoints)
- Root Guard (ports facing downstream switches) and Loop Guard (against STP failure from unidirectional links)
- UDLD aggressive (one-way fibre)
- Storm Control (broadcast / multicast / unknown unicast)
- DHCP Snooping + Dynamic ARP Inspection (as in Chapter 10)

<div class="zh" markdown="1">

- PortFast + BPDU Guard（接终端口）
- Root Guard（接下游交换机的口）、Loop Guard（防止单向链路造成的 STP 失效）
- UDLD aggressive（光纤单通）
- Storm Control（广播/组播/未知单播）
- DHCP Snooping + Dynamic ARP Inspection（呼应第 10 章）

</div>

### Model 2: Routed Access · 模型二：路由接入

```
  Distribution A (L3)          Distribution B (L3)
  +--------------+             +--------------+
  +---+------+---+             +---+------+---+
      | /30  | /31 point-to-point (or /30 aggregate)
  +---+------+---------------------+------+---+
  | Access switch (L3: SVI as gateway / routed uplink) |
  +-------------------+-------------------------+
                      | access port (Layer 2 ends inside this box)
                    Endpoint
```

<div class="zh" markdown="1">

```
   分布层 A（L3）              分布层 B（L3）
   ┌──────────────┐          ┌──────────────┐
   └───┬──────┬───┘          └───┬──────┬───┘
       │ /30  │ /31 point-to-point（或 /30 聚合）
   ┌───┴──────┴──────────────────┴──────┴───┐
   │ 接入交换机（L3：SVI 作网关 / 路由口上行）  │
   └─────────────────┬───────────────────────┘
                     │ access port（本机内的二层到此为止）
                   终端
```

</div>

**The key change: the L2/L3 boundary moves from the distribution layer down to the access layer.**

<div class="zh" markdown="1">

**关键变化：L2/L3 分界点从分布层下移到接入层。**

</div>

| Benefit (explicit in the book) | Expansion |
|---|---|
| Simpler, easier to troubleshoot | One standard routing toolset; no need to reason about STP topology and FHRP state |
| Removes STP and FHRP dependency | Uplinks all active in ECMP; bandwidth utilisation → 100%, loop risk → 0 |
| Faster convergence | Driven by the IGP (+BFD): commonly <1 s, BFD can reach <200 ms |
| Smaller failure domain | Broadcast domain = the endpoints behind a single access switch |

<div class="zh" markdown="1">

| 收益（原书明确列出） | 展开 |
|---|---|
| 更简单、更易排障 | 一套标准路由工具；无需理解 STP 拓扑与 FHRP 状态 |
| 消除 STP 与 FHRP 依赖 | 上行链路 ECMP 全活，带宽利用率→100%，环路风险→0 |
| 收敛更快 | 由 IGP（+BFD）决定，常见 <1 s，BFD 可 <200 ms |
| 故障域更小 | 广播域 = 单台接入交换机下挂的终端 |

</div>

| Limitation | Expansion and mitigation |
|---|---|
| A Layer 2 VLAN cannot span multiple access switches | Use an overlay (VXLAN/EVPN, LISP, GRE) when needed, or reduce the requirement to "inside a single closet" |
| Access switches need Layer 3 capability | Platform selection, licensing, CPU (IGP + ACLs); be careful with entry-level models |
| Subnet count rises | Each closet × each service = many /24s or /25s; requires IPAM and templated configuration |
| Wireless roaming is broken | Wireless needs its own design (local breakout with the controller on the same segment, or L3 roaming / fabric) |

<div class="zh" markdown="1">

| 限制 | 展开与应对 |
|---|---|
| 不支持跨多台接入交换机扩展 L2 VLAN | 需要时用覆盖（VXLAN/EVPN、LISP、GRE），或把需求收敛成"单配线间内" |
| 接入交换机需要 L3 能力 | 设备选型、License、CPU（IGP + ACL）；低端机型慎用 |
| 子网数量上升 | 每个配线间 × 每个业务 = 多个 /24 或 /25；必须靠 IPAM 与模板化配置 |
| 无线漫游被切断 | 无线需单独设计（本地出 + 控制器同网段，或 L3 漫游/fabric） |

</div>

> ⚠️ **Three hidden traps in routed access**
> 1. **/30 uplinks exhaust address space fast**: 16 closets × 2 uplinks = 32 /30s, which consumes a whole /24. Use **/31 (RFC 3021)**, or unnumbered/borrowed addressing on the uplink, or carve uplinks from a dedicated "interconnect pool" that is **never summarised into service prefixes**.
> 2. **Summarisation "beautifies" failures**: access /24s summarised into a /20 remain reachable when one access switch dies → traffic is black-holed. This needs **fast IGP convergence + BFD + correct summary granularity** working together.
> 3. **Legacy assets with static IPs**: routed access changes the gateway; devices with a hard-coded gateway (printers, industrial controllers, cameras) must be inventoried first, or they fail on day one.

<div class="zh" markdown="1">

> ⚠️ **路由接入三个隐蔽坑**
> 1. **上行用 /30 会快速耗尽地址**：16 个配线间 × 2 个上行 = 32 个 /30 = 一个 /24 就没了。用 **/31（RFC 3021）** 或"接入交换机上行用**未编号/借用**"，或直接把上行划进一个 /24 的"互联池"但**不要汇总进业务前缀**。
> 2. **汇总把故障"美化"了**：接入层 /24 汇总成 /20 通告，某接入机挂了网络仍可达 → 流量打到黑洞。需要 **IGP 快速收敛 + BFD + 精确汇总粒度** 三者配合。
> 3. **终端静态 IP 的存量资产**：路由接入意味着网关变化，老设备（打印机、工控、摄像头）写死网关的必须先盘点，否则上线即故障。

</div>

### Model 3: Switch Clustering · 模型三：交换机集群

```
Physical view                                Logical view
 Dist-A ====== Dist-B                     +------------------------+
   | \        /  |                          |  One logical device    |
   |  \      /   |                          |  Single management     |
   |  /      \   |                          |  Single control plane  |
 Acc-1 (stack member) Acc-2                 |  Cross-chassis bundle  |
                                            +------------------------+
```

<div class="zh" markdown="1">

```
物理视图                                    逻辑视图
 Dist-A ══════ Dist-B                     ┌────────────────────────┐
   │ ╲        ╱  │                          │   一个逻辑设备（集群）    │
   │  ╲      ╱   │                          │  单一管理面 / 单一控制面  │
   │  ╱      ╲   │                          │  跨机箱链路聚合（mLAG）   │
 Acc-1（堆叠成员）Acc-2                     └────────────────────────┘
```

</div>

| Characteristic | Explanation |
|---|---|
| Essence | Several physical devices form one logical entity (StackWise / VSS / vPC / mLAG) |
| Flexibility | **Highest**: Layer 2 requirements do not drag in STP or FHRP complexity |
| Redundancy | Node-level and link-level; cross-chassis bundles mean a member or link failure does not trigger STP |
| Convergence | Usually sub-second (bundle membership change) |
| Limitation (book) | Horizontal scale is usually **limited to two distribution switches per cluster** |
| Risk | Shared control plane → **software defects, upgrades and peer-link failures affect the pair together** |

<div class="zh" markdown="1">

| 特征 | 说明 |
|---|---|
| 本质 | 多台物理设备组成一个逻辑实体（StackWise / VSS / vPC / mLAG） |
| 灵活性 | **最高**：需要 L2 时不用引入 STP 或 FHRP 的复杂语义 |
| 冗余 | 节点级 + 链路级；跨机箱聚合，任一成员/链路故障不触发 STP |
| 收敛 | 通常亚秒（聚合成员变化即可） |
| 限制（原书） | 横向扩展通常**限制为每集群 2 台分布交换机** |
| 风险 | 控制面共享 → **软件缺陷、升级、peer-link 故障影响成对** |

</div>

#### What "Active-Active" in vPC Actually Means · vPC 的"活跃-活跃"到底是什么意思

A detail the book calls out specifically:

<div class="zh" markdown="1">

原书特别提醒的一个细节：

</div>

> Although vPC still uses FHRP (for example HSRP), **from the forwarding plane's point of view both upstream switches forward traffic** (active-active), unlike classic active-standby.

<div class="zh" markdown="1">

> vPC 虽然仍使用 FHRP（如 HSRP），但**从转发平面看，两台上游交换机都转发流量**（Active-Active），不同于传统 Active-Standby。

</div>

Expanded:

<div class="zh" markdown="1">

展开来说：

</div>

| Dimension | Classic HSRP (no vPC) | vPC + HSRP |
|---|---|---|
| Virtual MAC ownership | Only the active device answers ARP | Both answer with the same virtual MAC (one dying does not invalidate the peer's MAC table) |
| Data forwarding | Only the active device forwards gateway traffic | Both forward (each hashing over its local port-channel) |
| Uplink bandwidth | The standby switch idles | Both are used |
| Failure semantics | FHRP switchover (10 s class) | Usually no switchover action, just path reconvergence |
| Drawback | — | **The peer-link carries non-vPC unicast and multicast replication**; insufficient peer-link bandwidth causes drops |

<div class="zh" markdown="1">

| 维度 | 传统 HSRP（无 vPC） | vPC + HSRP |
|---|---|---|
| 虚拟 MAC 归属 | 只有 Active 应答 ARP | 两台都用同一虚拟 MAC 应答（任一台宕机，对端 MAC 表不失效） |
| 数据转发 | 只有 Active 转发网关流量 | 两台都转发（各按本地 port-channel 散列） |
| 上行带宽 | 备用交换机闲置 | 两台都用 |
| 故障语义 | FHRP 切换（10 s 级） | 通常无切换动作，只是路径收敛 |
| 缺陷 | — | **peer-link 承载非 vPC 单播/组播复制**，peer-link 带宽不足会导致丢包 |

</div>

> 🔥 **Three iron rules for vPC** (break one and you will have an incident):
> 1. **peer-link at least 2×10G, and carrying vPC traffic only** (no management traffic, no IGP adjacencies)
> 2. **peer-keepalive over a dedicated management network** (Layer 3 reachable, not on the peer-link)
> 3. **An explicit orphan-port plan**: when the peer-link fails, orphan ports are suspended — you must know which single-homed ports will drop

<div class="zh" markdown="1">

> 🔥 **vPC 的三条铁律**（不遵守必出事故）：
> 1. **peer-link 至少 2×10G，且只跑 vPC 流量**（不要塞管理、不要跑 IGP 邻居）
> 2. **peer-keepalive 走独立管理网段**（L3 可达，不在 peer-link 上）
> 3. **明确 orphan 端口预案**：peer-link 故障时 orphan 端口会被挂起，必须知道哪些单归口会断

</div>

### Comparing the Three Models (book Table 15-2 + additional dimensions) · 三种模型的综合对比（原书 Table 15-2 + 补充维度）

| Dimension | Multitier STP | Routed access | Switch clustering |
|---|---|---|---|
| **Design flexibility** | Limited (constrained by topology) | Limited (extending L2 across access needs an overlay) | **High** |
| **Scalability** | Mostly scale-up, limited scale-out | Both scale-up and scale-out | Scale-up and scale-out (clusters usually ≤2 upstream) |
| **Layer 3 gateway location** | Distribution (FHRP) | **Access layer (routed)** | Distribution (FHRP may or may not be needed) |
| **Cross-chassis link aggregation (mLAG)** | Not supported | Not supported (uses L3 ECMP) | **Supported** |
| **Access → distribution convergence** | Depends on STP + FHRP timers (slow) | Depends on the IGP (fast) | **Fastest** |
| **Operational complexity** | High (STP and FHRP together) | Medium (needs routing design skill) | **Low** (single management plane) |
| **Failure domain** | Large (the whole STP domain) | **Small (one access switch)** | Medium (the cluster is one domain) |
| **Upgrade risk** | One device at a time, low | One device at a time, low | **Whole group at once, concentrated** |
| **Address consumption** | Low (VLANs are reused) | Medium-high (one subnet per service per closet) | Low |

<div class="zh" markdown="1">

| 对比维度 | 多层 STP | 路由接入 | 交换机集群 |
|---|---|---|---|
| **设计灵活性** | 有限（受拓扑约束） | 有限（跨接入扩展 L2 需覆盖技术） | **高** |
| **可扩展性** | 纵向扩展为主，横向受限 | 纵向 + 横向均可 | 纵向 + 横向（集群通常 ≤2 台上游） |
| **L3 网关位置** | 分布层（FHRP） | **接入层（路由）** | 分布层（FHRP 可能需要/可能不需要） |
| **跨机箱链路聚合（mLAG）** | 不支持 | 不支持（靠 L3 ECMP） | **支持** |
| **接入→分布收敛** | 取决于 STP + FHRP 定时器（慢） | 取决于 IGP（快） | **最快** |
| **运维复杂度** | 高（同时管 STP 与 FHRP） | 中（需路由设计能力） | **低**（单管理面） |
| **故障域** | 大（整个 STP 域） | **小（单接入交换机）** | 中（集群为一域） |
| **升级风险** | 单台升级，风险低 | 单台升级，风险低 | **整组升级，风险集中** |
| **地址消耗** | 低（VLAN 复用） | 中高（每配线间每业务一子网） | 低 |

</div>

> ⚠️ The book stresses: **all three models are valid options**; the choice depends on requirements. Do not ask "which is best" in a review; ask "**what failure behaviour does this scenario require**".

<div class="zh" markdown="1">

> ⚠️ 原书强调：**三种模型都是有效选项**，选择取决于需求。评审时不要问"哪个最好"，要问"**这个场景的故障行为要求是什么**"。

</div>

### Selection Decision Tree (Usable Directly in a Design Review) · 选择决策树（可直接用于设计评审）

```
1 Is there a Layer 2 requirement that must span closets (wireless roaming / legacy apps / cluster heartbeat)?
   +- Yes -> 2 Are you willing to carry it over an overlay?
   |          +- Yes -> Routed access + VXLAN/EVPN (or fabric)
   |          +- No  -> Switch clustering (confine the L2 requirement inside the cluster)
   +- No  -> 3 Does the team have IGP design skills (areas / query scope / summarisation)?
              +- Yes -> Routed access (first choice for greenfield)
              +- No  -> Multitier STP (brownfield, with hardened STP protections)
```

<div class="zh" markdown="1">

```
① 是否存在必须跨配线间的二层需求（无线漫游/老应用/集群心跳）？
   ├─ 是 → ② 是否愿意用覆盖技术承载它？
   │        ├─ 愿意 → 路由接入 + VXLAN/EVPN（或 fabric）
   │        └─ 不愿意 → 交换机集群（L2 需求收敛在集群内）
   └─ 否 → ③ 团队是否有 IGP 设计能力（区域/查询/汇总）？
            ├─ 是 → 路由接入（新园区首选）
            └─ 否 → 多层 STP（存量改造，强化 STP 保护）
```

</div>

> 🎯 **Where the decision lands**: **"Layer 2 across closets" is the only genuine technical requirement that blocks routed access.** Every other reason ("the team does not know OSPF", "the hardware does not support it") is a constraint that can be removed; the Layer 2 requirement is architectural.

<div class="zh" markdown="1">

> 🎯 **决策的落脚点**：**"跨配线间二层"是唯一真正阻止路由接入的技术需求**。其他所有理由（"团队不熟 OSPF"、"设备不支持"）都是可以消除的约束，而二层需求是架构性的。

</div>

### Convergence-Time Budget (Engineering Values for the Three Models) · 收敛时间预算表（三种模型的工程值）

| Phase | Multitier STP (tuned RSTP) | Routed access (IGP + BFD) | Switch clustering |
|---|---|---|---|
| Link/port failure detection | 1–3 s (BPDU ageing) or <1 s (link down) | 50–200 ms (BFD) | <1 s (bundle member removal) |
| Topology/route convergence | 1–5 s | 200 ms–1 s | <1 s |
| Gateway switchover | 1–10 s (FHRP tunable) | None (ECMP recomputation) | None (active-active) |
| **Network-side total** | **3–18 s** | **<1 s** | **<1.5 s** |
| Host / IP session recovery | 0–300 s (uncontrollable) | 0–300 s | 0–300 s |

<div class="zh" markdown="1">

| 阶段 | 多层 STP（RSTP 优化后） | 路由接入（IGP + BFD） | 交换机集群 |
|---|---|---|---|
| 链路/端口故障检测 | 1–3 s（BPDU 老化）或 <1 s（链路 down） | 50–200 ms（BFD） | <1 s（聚合成员移除） |
| 拓扑/路由收敛 | 1–5 s | 200 ms–1 s | <1 s |
| 网关切换 | 1–10 s（FHRP 可调） | 无（ECMP 重算） | 无（双活） |
| **网络侧合计** | **3–18 s** | **<1 s** | **<1.5 s** |
| 主机/IP 会话恢复 | 0–300 s（不可控） | 0–300 s | 0–300 s |

</div>

> 💡 **Conclusion**: sub-second on the network side is no longer expensive (BFD plus a sane design). **The real gap is in hosts and applications.** So after "network high availability" is done, push one layer up: application reconnect logic, DNS TTLs, load-balancer health checks.

<div class="zh" markdown="1">

> 💡 **结论**：网络侧做到 1 s 以内已经不贵（BFD + 合理设计），**真正的差距在主机与应用**。所以"做完网络高可用"之后，必须往上推一层：应用的连接重试、DNS TTL、负载均衡健康检查。

</div>

---

## 3. Campus Layer 3 Routing Design Considerations · 三、园区三层路由设计考量

### Where the L2/L3 Boundary Can Sit · L2/L3 分界点的三种位置

| Position | Form | Consequence |
|---|---|---|
| **Distribution** (traditional) | SVI + FHRP on the distribution switches | Broadcast domain spans several access switches; STP must exist |
| **Access** (routed access) | Access switch SVI/routed port as the gateway | Broadcast domain = one access switch; no STP/FHRP |
| **Per port / per AP** (fabric / micro-segmentation) | One VRF/VN per user (e.g. SDA VN plus policy) | Finest isolation granularity, dependent on the control plane (LISP/EVPN) |

<div class="zh" markdown="1">

| 位置 | 形态 | 结果 |
|---|---|---|
| **分布层**（传统） | SVI + FHRP 在分布交换机 | 广播域跨多台接入，STP 必须存在 |
| **接入层**（路由接入） | 接入交换机 SVI/路由口作网关 | 广播域 = 单台接入，无 STP/FHRP |
| **每个端口/AP**（fabric/微分段） | 每用户一个 VRF/VN（如 SDA 的 VN + 策略） | 隔离粒度最细，依赖控制面（LISP/EVPN） |

</div>

> ⚠️ **Once the boundary moves down, it never moves back**: addressing plans, DHCP scopes, firewall policies and monitoring semantics all follow it. This is a **one-way decision** and must be made during design — not "do it traditionally for now and revisit later".

<div class="zh" markdown="1">

> ⚠️ **分界点一旦下移，就回不去了**：因为地址规划、DHCP scope、防火墙策略、监控口径都会跟着变。所以这是**一次性决策**，必须在设计阶段定，不要"先按传统做，以后再说"。

</div>

### FHRP Design Details (the Achilles' Heel of the Traditional Model) · FHRP 的设计细节（传统模型的命门）

| Parameter | Default | Recommendation |
|---|---|---|
| HSRP version | v1 | **v2** (IPv6 support, multicast 224.0.0.102, millisecond timers) |
| Hello / Hold | 3 s / 10 s | 250 ms / 750 ms (must be consistent network-wide; watch CPU) |
| Preemption | On by default (v2) | **Delay preemption by 60–180 s** (prevents flapping back and forth) |
| Tracking | None | `track` the uplink interface plus IP SLA (the "live dead gateway" must be solved) |
| Authentication | Clear text | MD5/SHA (prevents a second gateway being misconfigured) |
| STP coordination | None | Keep HSRP active and the STP root on the same switch (removes detours) |

<div class="zh" markdown="1">

| 参数 | 默认值 | 建议 |
|---|---|---|
| HSRP 版本 | v1 | **v2**（支持 IPv6、组播 224.0.0.102、毫秒定时器） |
| Hello / Hold | 3 s / 10 s | 250 ms / 750 ms（需全网一致，且注意 CPU） |
| 抢占 | 默认开启（v2） | **延迟抢占 60–180 s**（防止抖动来回切） |
| 跟踪 | 无 | `track` 上行接口 + IP SLA（"活着的死网关"必须解决） |
| 认证 | 明文 | MD5/SHA（防误配第二台网关） |
| 与 STP 联动 | 无 | 让 HSRP Active 与 STP Root 在同一台（减少绕行） |

</div>

> 🔥 **Classic incident**: HSRP active on switch A while the STP root is on switch B → forward traffic through A, return traffic through B, so the inter-switch link saturates and users report "the internet is slow". **The root bridge and the gateway must be on the same side** — a standing item on every review checklist.

<div class="zh" markdown="1">

> 🔥 **经典事故**：HSRP Active 在 A 台、STP Root 在 B 台 → 去程走 A、回程走 B，跨交换机串联链路被打满，用户感知"上网慢"。**根桥与网关必须同侧**，这是评审清单的固定项。

</div>

### EIGRP: Query-Scope Control Is the Only Real Core Concern · EIGRP：查询范围控制是唯一核心

Whether EIGRP works well in a campus depends almost entirely on three things: **summarisation, stub, and the query boundary**.

<div class="zh" markdown="1">

EIGRP 在园区跑得好不好，几乎只取决于三件事：**汇总、stub、查询边界**。

</div>

| Mechanism | Purpose | Configuration point |
|---|---|---|
| **Summarisation** (`ip summary-address eigrp`) | Shrinks the query domain, shrinks the routing table | Summarise **from distribution upward** |
| **Stub** (`eigrp stub connected summary`) | The access layer advertises only connected/summary routes and **does not forward queries** | Every access switch must be a stub |
| **Query-scope control** | Limits query propagation | stub + summarisation + route-map filters where needed |
| **SIA timer** | 3 minutes by default (active-time) | Do not raise it; design SIA out instead of waiting for it |
| **Load balancing** | Equal-cost by default (`variance` for unequal) | Campuses usually want plain ECMP |

<div class="zh" markdown="1">

| 机制 | 作用 | 配置要点 |
|---|---|---|
| **汇总**（`ip summary-address eigrp`） | 缩小查询域、减小路由表 | 在**分布层向上行**的方向汇总 |
| **Stub**（`eigrp stub connected summary`） | 接入层只通告直连/汇总，**不转发查询** | 所有接入层交换机必须 stub |
| **查询范围控制** | 限制 query 扩散范围 | stub + 汇总 + 必要时 route-map 过滤 |
| **SIA 定时器** | 默认 3 分钟（active-time） | 不建议调大；靠设计消除 SIA 而非等待它 |
| **负载均衡** | 默认等价（`variance` 支持非等价） | 园区通常等价 ECMP |

</div>

```
Bad design: topology change → query floods the network → many neighbours active → SIA → minutes to converge
Good design: access stub + distribution summary → queries stop at the distribution layer → sub-second
```

<div class="zh" markdown="1">

```
设计不当：拓扑变化 → 查询泛洪全网 → 大量邻居 active → SIA → 收敛分钟级
设计正确：接入层 stub + 分布层汇总 → 查询止于分布层 → 亚秒级
```

</div>

### OSPF: Area Design and the Suboptimality Cost of Summarisation · OSPF：区域设计与"汇总的次优代价"

| Design item | Recommendation | Why |
|---|---|---|
| Area layout | Core = Area 0 (backbone); each functional block = its own normal area | Topology changes stay inside the area (SPF only runs there) |
| ABR count | **2 ABRs per area** (one primary, one backup) | A single ABR is a single point; more than two ABRs means summary redundancy and suboptimality |
| Summary point | **Only on ABRs**, and each prefix **summarised on one ABR only** (or with a different metric) | Several ABRs summarising the same prefix causes detours after a failure |
| Area types | Edge areas can be stub / totally-stubby | Fewer LSAs, more stable convergence |
| Timers | Hello 10 / Dead 40 (default) | Small gains from tuning; **BFD is faster and safer** |
| Authentication | MD5/SHA per area | Prevents accidental adjacencies |

<div class="zh" markdown="1">

| 设计项 | 建议 | 原因 |
|---|---|---|
| 区域划分 | 核心 = Area 0（骨干），每个功能块 = 独立普通区域 | 拓扑变化限制在区域内（需 SPF 只在区域内跑） |
| ABR 数量 | 每区域 **2 个 ABR**（一主一备） | 单 ABR = 单点；多 ABR（>2）= 汇总冗余带来次优 |
| 汇总点 | **只在 ABR 上做**，且每个前缀**只在一台 ABR 上汇总**（或用不同 metric） | 多台同时汇总 = 故障后流量绕行 = 次优 |
| 区域类型 | 边缘区域可用 stub / totally-stubby | 减少 LSA，稳定收敛 |
| 计时器 | Hello 10 / Dead 40（默认） | 调小收益有限，**用 BFD 更快更安全** |
| 认证 | 每区域 MD5/SHA | 防误接入 |

</div>

> ⚠️ **An inherent OSPF problem the book calls out explicitly**: **route summarisation on multiple ABRs can create suboptimal routing when a link fails.** This is a structural cost of "multi-ABR summarisation", not a configuration error.
>
> **Mitigations**: (1) summarise each prefix on only one ABR; (2) use the `area range` cost parameter to steer; (3) do not summarise critical prefixes (use specifics plus filtering); (4) accept brief suboptimality (usually 1–2 hops) and state it in the design document.

<div class="zh" markdown="1">

> ⚠️ **原书明确指出的 OSPF 固有问题**：**在多个 ABR 上做路由汇总，可能导致链路故障时的次优路由。** 这是"多 ABR 汇总"的结构性代价，不是配置错误。
>
> **缓解手段**：① 每前缀只在一台 ABR 汇总；② 用 `area range` 的 cost 参数引导；③ 关键前缀不做汇总（用明细 + 过滤）；④ 接受短暂次优（通常 1–2 跳）并在设计文档里写明。

</div>

### IGP vs BGP Division of Labour (the Boundary Inside a Campus) · IGP 与 BGP 的分工（园区里的边界）

IGPs run inside the campus; BGP runs between the campus and the **outside world** (internet edge, WAN, cloud access, partners). The line is normally drawn here:

<div class="zh" markdown="1">

园区内部用 IGP；园区与**外部**（互联网边缘、WAN、云接入、合作伙伴）之间用 BGP。分界线通常画在：

</div>

| Boundary | What runs there | Why |
|---|---|---|
| Access ↔ distribution | EIGRP/OSPF (or static + FHRP) | Intra-domain, high change rate, needs fast convergence |
| Distribution ↔ core | The same IGP | Keeps the campus a single IGP domain |
| Core ↔ WAN / internet edge | **BGP** (eBGP, or iBGP + redistribution) | Policy, path selection, multihoming, address aggregation |
| Core ↔ data centre (when it is its own AS) | BGP, or IGP + a static boundary | A clear autonomous boundary makes independent evolution possible |

<div class="zh" markdown="1">

| 位置 | 用什么 | 为什么 |
|---|---|---|
| 接入 ↔ 分布 | EIGRP/OSPF（或静态 + FHRP） | 域内、变化频繁、需要快速收敛 |
| 分布 ↔ 核心 | 同一 IGP | 保持园区为单一 IGP 域 |
| 核心 ↔ WAN/互联网边缘 | **BGP**（eBGP 或 iBGP + 重分发） | 策略、路径选择、多宿主、地址聚合 |
| 核心 ↔ 数据中心（独立自治域时） | BGP 或 IGP + 静态边界 | 自治边界清晰，便于独立演进 |

</div>

> 🎯 **One review rule**: **the campus IGP routing table should stay stable at the low thousands**. If it grows to tens of thousands, either "things that should be summarised are not" or "the BGP boundary is in the wrong place" (Chapters 16 and 17 take this further).

<div class="zh" markdown="1">

> 🎯 **一条评审准则**：**园区 IGP 的路由表条目数应该稳定在千级以内**。如果园区 IGP 涨到万级，说明"该汇总的没汇总"或"该用 BGP 的边界没画"（第 16/17 章会展开）。

</div>

### Aligning Routing Design With the Physical Architecture (Two Book Scenarios) · 路由设计与物理架构对齐（原书两个场景）

**Scenario 1: the data centre coexists with other modules in the same campus**

<div class="zh" markdown="1">

**场景 1：数据中心与其他模块共存于同一园区**

</div>

```
        +-------- Core (Area 0) --------+
  User block (Area 10)  DC block (Area 20)  WAN block (Area 30)  Mgmt block (Area 40)
```
- IGP areas map **one-to-one** onto functional blocks; ABRs sit in the distribution layer
- One core infrastructure carries every block; the summary boundary equals the area boundary

<div class="zh" markdown="1">

```
        ┌──────── 核心（Area 0）────────┐
   用户块(Area 10)  DC块(Area 20)  WAN块(Area 30)  管理块(Area 40)
```
- IGP 区域与功能块**一一对应**，ABR 落在分布层
- 同一核心基础设施承载所有块，汇总边界 = 区域边界

</div>

**Scenario 2: the data centre connects to the campus over the WAN or dedicated fibre**

<div class="zh" markdown="1">

**场景 2：数据中心通过 WAN / 专用光纤与园区互连**

</div>

```
  Campus core (OSPF Area 0) -- WAN/DWDM -- DC core (separate IGP domain or BGP)
```
- Treat the WAN interconnect as an **external link**: the campus backbone area may extend onto WAN transport devices, but **do not inject DC specifics into the campus IGP**
- Use BGP + summarisation at the boundary, or static + floating static
- Benefit: DC routing churn no longer triggers SPF recomputation in the campus

<div class="zh" markdown="1">

```
   园区核心(OSPF Area 0) ── WAN/DWDM ── DC 核心(独立 IGP 域或 BGP)
```
- WAN 互连视为**外部链路**：园区 IGP 的骨干区域可以延伸到 WAN 传输设备上，但**不建议把 DC 的明细路由灌进园区 IGP**
- 边界用 BGP + 汇总，或静态 + 浮动
- 好处：DC 的路由震荡不会引发园区 SPF 重算

</div>

> 🎯 **The book's central point**: **"there is no single standard design that fits every scenario"**. The designer must balance technical characteristics (protocol capability) against non-technical factors (business priority, future plans, team knowledge, budget) — a sentence that could be pasted at the end of every chapter.

<div class="zh" markdown="1">

> 🎯 **原书核心观点**：**"没有单一标准设计可用于所有场景"**。设计师必须在技术特性（协议能力）与非技术因素（业务优先级、未来计划、团队知识、预算）之间取得平衡 —— 这句话几乎可以贴在每章末尾。

</div>

### Dual Stack and Addressing (Links Back to Chapter 14) · 双栈与地址规划（与第 14 章衔接）

Addressing points for campus Layer 3 design (Chapter 14 covers the protocol details; here we only list the campus-level decisions):

<div class="zh" markdown="1">

园区三层设计的地址侧要点（第 14 章已展开协议细节，这里只列园区场景的决策）：

</div>

| Decision | Recommendation | Why |
|---|---|---|
| Subnet size per closet | IPv4 /24 (≤250 endpoints); IPv6 always /64 | Matches DHCP scopes and broadcast-domain size |
| Routed-access uplinks | IPv4 /31; IPv6 /64 or /127 (vendor dependent) | Saves addresses, no broadcast |
| Summary granularity | /22 per building (IPv4), /56 per site (IPv6) | Aligns with physical buildings, still summarisable in ten years |
| Dual-stack order | Infrastructure first (loopbacks/management/OSPFv3/DNS), endpoints later | Avoids "endpoints have IPv6 but nobody can troubleshoot it" |
| Wireless addressing | A large dedicated subnet (/23 or /22), or on-demand allocation inside the fabric | The practical limits of roaming and DHCP flooding |

<div class="zh" markdown="1">

| 决策 | 建议 | 原因 |
|---|---|---|
| 每配线间子网大小 | IPv4 /24（≤250 终端）；IPv6 固定 /64 | 与 DHCP scope、广播域规模匹配 |
| 路由接入的上行 | IPv4 /31；IPv6 /64 或 /127（视厂商） | 省地址、无广播 |
| 汇总粒度 | 每楼 /22（IPv4）、每站 /56（IPv6） | 与物理楼栋对齐，便于十年后汇总 |
| 双栈顺序 | 先基础设施（环回/管理/IGPv3/DNS），再终端 | 避免"终端有 v6 但无法排障" |
| 无线地址 | 独立大子网（/23 或 /22），或 fabric 内按需分配 | 漫游与 DHCP 洪泛的现实约束 |

</div>

---

## 4. Campus Network Virtualisation · 四、园区网络虚拟化

### Two Virtualisation Models (Get the Direction Right First) · 两种虚拟化模型（先分清方向）

```
Many-to-One                          One-to-Many
+----+ +----+ +----+                +---------------------+
|SW1 | |SW2 | |SW3 |                | Physical box (x86)  |
+--+-+ +--+-+ +--+-+                | +---+ +---+ +---+   |
   +------+------+                  | |vFW| |vLB| |vR |   |
   Presented as one logical unit    | +---+ +---+ +---+   |
   (stack / vPC / cluster / FHRP)   |     Hypervisor      |
                                    +---------------------+
```

<div class="zh" markdown="1">

```
多对一（Many-to-One）                一对多（One-to-Many）
┌────┐┌────┐┌────┐                 ┌─────────────────────┐
│SW1 ││SW2 ││SW3 │                 │  物理设备（x86/高端）  │
└──┬─┘└──┬─┘└──┬─┘                 │ ┌───┐┌───┐┌───┐     │
   └─────┴─────┘                   │ │vFW││vLB││vR │ ... │
   呈现为一个逻辑单元               │ └───┘└───┘└───┘     │
   （堆叠/vPC/集群/FHRP）           │      Hypervisor      │
                                   └─────────────────────┘
```

</div>

| Model | Definition | Campus examples | Main benefit | Main cost |
|---|---|---|---|---|
| **Many-to-one** | Several physical resources presented as one logical unit | StackWise, VSS, vPC, FHRP VIP, firewall clusters | Simpler management, no STP, better availability | Control-plane coupling, concentrated upgrade risk |
| **One-to-many** | One physical resource partitioned into several logical instances | VRF, virtual firewall, NFV, VLAN slicing | Isolation, lower CAPEX, on-demand provisioning | Fate sharing, longer troubleshooting chains |

<div class="zh" markdown="1">

| 模型 | 定义 | 园区例子 | 主要收益 | 主要代价 |
|---|---|---|---|---|
| **多对一** | 多个物理资源呈现为一个逻辑单元 | StackWise、VSS、vPC、FHRP VIP、防火墙集群 | 简化管理、消除 STP、提升可用性 | 控制面耦合、升级风险集中 |
| **一对多** | 一个物理资源切分为多个逻辑实例 | VRF、虚拟防火墙、NFV、VLAN 切片 | 隔离、降 CAPEX、按需开通 | 命运共享、排障链路变长 |

</div>

### The Three Drivers for Network Virtualisation (book) · 采用网络虚拟化的三个驱动因素（原书）

1. **Cost efficiency and design flexibility**: several logical networks share one physical plant → fewer devices and less complexity → lower CAPEX/OPEX
2. **Simplified and flexible security integration**: each logical entity has its own policy → user groups are separated from services → satisfies compliance and audit
3. **Simplified design and operations**: end-to-end **path isolation** per application/group/service instead of isolation achieved by "pulling separate cables"

<div class="zh" markdown="1">

1. **成本效率与设计灵活性**：多个逻辑网络跑在同一套物理上 → 减少设备数量与复杂度 → 降 CAPEX/OPEX
2. **简化且灵活的安全集成**：每个逻辑实体独立策略 → 用户组与服务逻辑分离 → 满足合规与审计
3. **设计与运维简化**：按应用/组/服务做端到端**路径隔离**，而不是靠"物理拉线"实现隔离

</div>

### Fate Sharing (Shared Failure State) · 命运共享

> ⚠️ **The book's main concern**: any physical network failure can take down **several virtual networks at the same time**. So when virtualisation is used, **the availability of the underlying physical network must be raised at the same time**.

<div class="zh" markdown="1">

> ⚠️ **原书点明的主要担忧**：任何物理网络故障，都可能导致运行其上的**多个虚拟网络同时故障**。因此使用虚拟化时，**必须同时提升底层物理网络的高可用性**。

</div>

The argument can be quantified:

<div class="zh" markdown="1">

这个道理可以量化：

</div>

| Physical availability | Number of virtual networks | Availability felt by a single VN |
|---|---|---|
| 99.9% (43 min/month) | 1 | 99.9% |
| 99.9% | 10 (sharing the same physical plant) | Still 99.9%, but **one failure hits 10 services** |
| 99.99% | 10 | 99.99%: large blast radius, but a low probability |

<div class="zh" markdown="1">

| 物理层可用性 | 虚拟网络数量 | 单 VN 感受到的可用性 |
|---|---|---|
| 99.9%（月 43 min） | 1 | 99.9% |
| 99.9% | 10（共享同一物理） | 仍 99.9%，但**一次故障影响 10 个业务** |
| 99.99% | 10 | 99.99%，故障半径大但概率低 |

</div>

> 🎯 **Corollary**: virtualisation **does not improve availability, it only amplifies the failure radius**. The precondition for virtualisation is "the physical layer is already good enough" — not "use virtualisation to obtain high availability" (that is the job of many-to-one designs).

<div class="zh" markdown="1">

> 🎯 **推论**：虚拟化**不提升可用性，只放大故障半径**。所以虚拟化的前提是"物理层可用性已经达标"，而不是"用虚拟化来做高可用"（那是多对一的活）。

</div>

### Extra Complexity in Multi-Tenant Environments · 多租户环境的额外复杂度

| Dimension | Single tenant | Multi-tenant |
|---|---|---|
| Addressing | Globally unique | **May overlap** (everyone loves 10.0.0.0/8) |
| QoS | One policy set | Different SLA per tenant, on shared queues |
| Security | One boundary | One boundary per tenant plus controlled inter-tenant reachability |
| Troubleshooting | One diagram | One physical diagram plus N logical ones |
| Change | Single change | **Coordinating change windows between tenants** |

<div class="zh" markdown="1">

| 维度 | 单租户 | 多租户 |
|---|---|---|
| 地址 | 全局唯一 | **可能重叠**（都爱用 10.0.0.0/8） |
| QoS | 一套策略 | 每租户不同 SLA，且共享队列 |
| 安全 | 一条边界 | 每租户一条边界 + 租户间受控互通 |
| 排障 | 一张图 | 一张物理图 + N 张逻辑图 |
| 变更 | 单点变更 | **租户间变更窗口协调** |

</div>

---

## 5. The Four Path-Isolation Techniques · 五、路径隔离的四种技术

![Figure 15-20 · Four path-isolation techniques](assets/fig/en15-20-path-isolation.svg)

The book lists four end-to-end path-isolation techniques; the choice rests on **scale, complexity and team knowledge**.

<div class="zh" markdown="1">

原书列出四种端到端路径隔离技术，选择依据是**规模、复杂度、团队知识**。

</div>

### Technique 1: End-to-End VLAN + VRF (Traditional, Hop-by-Hop) · 技术 1：端到端 VLAN + VRF（传统逐跳）

```
Access (VLAN 100) --802.1Q-- Distribution (VRF-A) -- Core (VRF-A) -- Distribution (VRF-A) -- Access (VLAN 100)
```

<div class="zh" markdown="1">

```
接入(VLAN 100) ─802.1Q── 分布(VRF-A) ── 核心(VRF-A) ── 分布(VRF-A) ── 接入(VLAN 100)
```

</div>

- Every hop needs VLAN + trunk + VRF configured, **consistently end to end**
- Lowest scalability (4096 VLAN ceiling, VLAN explosion on trunks)
- Highest operational complexity (one missed hop = broken path)
- Routing knowledge required: **basic**

<div class="zh" markdown="1">

- 每一跳都要配 VLAN + Trunk + VRF，**端到端一致**
- 可扩展性最低（VLAN 4096 上限、Trunk 上 VLAN 数量爆炸）
- 运维复杂度最高（任一跳漏配 = 路径断）
- 需要的路由知识：**基础**

</div>

> 💡 Where it fits: small campuses with **only 2–4 isolation domains** and a team with no MPLS or tunnelling experience. Do not look down on it — plenty of projects that "went MPLS VPN and made a mess" would have been fine with VLAN + VRF.

<div class="zh" markdown="1">

> 💡 适用：小型园区、**只有 2–4 个隔离域**、且团队没有 MPLS/隧道经验。别看不起它，很多"上了 MPLS VPN 搞得一团乱"的项目，本来用 VLAN+VRF 就够了。

</div>

### Technique 2: VLAN + VRF + GRE (Point-to-Point Tunnels) · 技术 2：VLAN + VRF + GRE（点对点隧道）

```
Access (VLAN) -- Distribution (VRF) == GRE tunnel == Distribution (VRF) -- Access (VLAN)
                                        ^ removes the end-to-end VRF/trunk dependency
```

<div class="zh" markdown="1">

```
接入(VLAN) ─ 分布(VRF) ══ GRE 隧道 ══ 分布(VRF) ─ 接入(VLAN)
                            ↑ 消除端到端 VRF/Trunk 依赖
```

</div>

- The tunnel crosses the transit network, and transit devices **do not need to know about the VRFs**
- Low scalability (tunnel count = number of site pairs, n(n−1)/2, or a hub-and-spoke star)
- Where it fits: **only part of the path needs isolation**, or the path crosses a third-party network (WAN, partner)

<div class="zh" markdown="1">

- 隧道跨越中间网络，中间设备**不需要知道 VRF**
- 可扩展性低（隧道数 = 站点对数，n(n−1)/2 或星型）
- 适用：**只有部分路径需要隔离**，或跨第三方网络（WAN、合作伙伴）

</div>

### Technique 3: VLAN + VRF + mGRE (Point-to-Multipoint) · 技术 3：VLAN + VRF + mGRE（点对多点）

```
Access -- Distribution (VRF) --+-- mGRE (one tunnel interface, many endpoints) --+-- Distribution (VRF) -- Access
                               +------------------------------------------------+
```

<div class="zh" markdown="1">

```
接入 ─ 分布(VRF) ──┬── mGRE（一个隧道接口连多点）──┬─ 分布(VRF) ─ 接入
                   └──────────────────────────────┘
```

</div>

- One mGRE interface plus NHRP resolution drops the tunnel count from O(n²) to O(n)
- Medium scalability, medium operational effort
- Where it fits: medium networks, DMVPN-style campus interconnect, isolated paths between branches and headquarters

<div class="zh" markdown="1">

- 一个 mGRE 接口 + NHRP 解析对端，隧道数从 O(n²) 降到 O(n)
- 可扩展性中等，运维中等
- 适用：中型网络、DMVPN 式的园区互联、分支与总部之间的隔离路径

</div>

### Technique 4: MPLS VPN (MP-BGP) · 技术 4：MPLS VPN

```
        +----------- MPLS core (P routers) -----------+
   PE (distribution) =========================== PE (distribution)
      |                                              |
   CE (access)                                   CE (access)
   MP-BGP exchanges VPNv4/VPNv6 routes; VRFs live on the PEs
```

<div class="zh" markdown="1">

```
        ┌────────── MPLS 核心（P 路由器）──────────┐
   PE(分布层) ═══════════════════════════════ PE(分布层)
      │                                            │
   CE(接入)                                     CE(接入)
   MP-BGP 交换 VPNv4/VPNv6 路由，VRF 在 PE 上
```

</div>

- The enterprise network "becomes a service-provider network": the core runs MPLS, the distribution switches act as PEs
- MP-BGP exchanges VPN routes; **route reflectors (RR)** reduce full-mesh sessions
- L2VPN (EoMPLS / VPLS) can extend Layer 2
- Highest scalability and highest design flexibility
- Routing knowledge required: **advanced**

<div class="zh" markdown="1">

- 企业网络"变成运营商网络"：核心跑 MPLS，分布层交换机作 PE
- MP-BGP 交换 VPN 路由，可用 **RR** 减少全互联会话
- 可用 L2VPN（EoMPLS / VPLS）扩展二层
- 可扩展性最高、设计灵活性最高
- 需要的路由知识：**高级**

</div>

### Comparing the Four Techniques (book Table 15-4 + additions) · 四种技术综合对比（原书 Table 15-4 + 补充）

| Dimension | End-to-end VLAN+VRF | GRE | mGRE | MPLS VPN |
|---|---|---|---|---|
| **Scalability** | Low | Low | Medium | **High** |
| **Operational complexity** | High | Medium | Medium | Medium–high |
| **Design flexibility** | Low | Medium | Medium | **High** |
| **Architectural form** | Hop-by-hop, end to end | Point-to-point (multi-hop) | Point-to-multipoint (multi-hop) | MPLS L3VPN |
| **Routing knowledge required** | Basic | Medium | Medium | **Advanced** |
| **Do transit devices see the isolation** | Yes (they must be configured) | No | No | No (P routers just swap labels) |
| **MTU impact** | None | Must lower MTU/MSS | Must lower MTU/MSS | Must guarantee MTU ≥ 1500 + labels |
| **Fault-localisation difficulty** | Medium (hop by hop) | High (invisible inside the tunnel) | High | High (labels + VRF + RT) |
| **Typical fit** | Small campus, 2–4 domains | Local isolation / third-party transit | Medium multi-site | Large multi-tenant / multi-service |

<div class="zh" markdown="1">

| 维度 | 端到端 VLAN+VRF | GRE | mGRE | MPLS VPN |
|---|---|---|---|---|
| **可扩展性** | 低 | 低 | 中等 | **高** |
| **运维复杂度** | 高 | 中等 | 中等 | 中—高 |
| **设计灵活性** | 低 | 中等 | 中等 | **高** |
| **架构形态** | 逐跳端到端 | 点对点（多跳） | 点对多点（多跳） | MPLS L3VPN |
| **团队路由知识要求** | 基础 | 中等 | 中等 | **高级** |
| **中间设备是否感知隔离** | 是（必须配） | 否 | 否 | 否（P 只转发标签） |
| **MTU 影响** | 无 | 需降 MTU/MSS | 需降 MTU/MSS | 需保证 MTU ≥ 1500+标签 |
| **故障定位难度** | 中（逐跳可查） | 高（隧道内不可见） | 高 | 高（标签 + VRF + RT） |
| **典型适用** | 小园区 2–4 域 | 局部隔离/跨第三方 | 中型多站点 | 大型多租户/多业务 |

</div>

### (Extended) Modern Alternatives: VXLAN/EVPN and SDA · （延伸）现代替代：VXLAN/EVPN 与 SDA

The book was written against the traditional stack; today's campuses more often use overlay designs. They are not "a fifth technique" — they are **the industrialisation of GRE's isolation idea**:

<div class="zh" markdown="1">

原书写于传统技术栈，今天园区里更常见的是覆盖网络方案。它们不是"第五种技术"，而是**把 GRE 的隔离思想工业化**：

</div>

| Solution | Control plane | Data plane | Characteristics | When to choose |
|---|---|---|---|---|
| **VXLAN + EVPN** (manual or automated) | MP-BGP EVPN | VXLAN (UDP 4789) | Standards-based, multi-vendor, can unify with the DC | You have automation skills and need L2 extension |
| **Cisco SD-Access** | LISP (+ a traditional underlay IGP) | VXLAN | Policy follows the user (SGT), wired and wireless unified | Large campuses, strong policy requirements |
| **ACI** (more DC-oriented) | APIC + IS-IS | VXLAN | Centralised policy model | Mainly DC; campuses use it mostly for DC interconnect |

<div class="zh" markdown="1">

| 方案 | 控制面 | 数据面 | 特点 | 何时选 |
|---|---|---|---|---|
| **VXLAN + EVPN**（手工/自动化） | MP-BGP EVPN | VXLAN（UDP 4789） | 标准、多厂商、可与 DC 统一 | 有自动化能力、需要 L2 扩展 |
| **Cisco SD-Access** | LISP（+ 传统 IGP underlay） | VXLAN | 策略随用户走（SGT）、有线无线统一 | 大型园区、强策略需求 |
| **ACI**（更偏 DC） | APIC + IS-IS | VXLAN | 策略模型中心化 | DC 为主，园区多用于 DC 互联 |

</div>

> ⚠️ **Do not adopt a fabric just because it is new**: fabric demands far more from operations (underlay planning, control-plane troubleshooting, an automation platform, team training) than a traditional campus. **The benefits of a fabric are "policy follows the person" and "automation at scale"; if you do not need those two, the benefit is close to zero.**

<div class="zh" markdown="1">

> ⚠️ **不要为了"新"而上 fabric**：fabric 的运维要求（underlay 规划、控制面排障、自动化平台、团队培训）远高于传统园区。**fabric 的收益在"策略随人走 + 大规模自动化"，如果这两条你不需要，收益接近于零。**

</div>

---

## 6. Service Virtualisation · 六、服务虚拟化

Path isolation solves "services cannot reach each other"; service virtualisation solves "**how several business domains share the same set of services**" (internet exit, file servers, DNS, AD, printing, monitoring).

<div class="zh" markdown="1">

路径隔离解决"业务之间不互通"，服务虚拟化解决"**多个业务域如何共享同一批服务**"（互联网出口、文件服务器、DNS、AD、打印、监控）。

</div>

### The Three Service-Access Models · 服务访问的三种模型

![Figure 15-21 · Three service-access models](assets/fig/en15-21-service-access-models.svg)

```
Model A: independent services per domain      Model B: shared services + service edge
+-------+ +-------+                          +-------+   +-------+
|DomainA| |DomainB|                          |DomainA|   |DomainB|
| vFW-A | | vFW-B |                          +---+---+   +---+---+
| own exit| |own exit|                          +----+-------+
+-------+ +-------+                              +----+-------+
 Simple, expensive, best isolation               | Shared edge |  (vFW + NAT + LB)
                                                 +----+-------+
                                                 Shared services (internet/DC)
```

<div class="zh" markdown="1">

```
模型 A：每域独立服务                     模型 B：共享服务 + 服务边界
┌───────┐ ┌───────┐                    ┌───────┐   ┌───────┐
│域 A   │ │域 B   │                    │域 A   │   │域 B   │
│ vFW-A │ │ vFW-B │                    └───┬───┘   └───┬───┘
│ 独立出口│ │ 独立出口│                       └────┬──────┘
└───────┘ └───────┘                       ┌──────┴──────┐
 简单、贵、隔离最好                        │ 共享服务边界  │（vFW + NAT + LB）
                                          └──────┬──────┘
                                           共享服务（互联网/DC）
```

</div>

| Model | CAPEX | Isolation | Complexity | Where it fits |
|---|---|---|---|---|
| A: per-domain | High | Highest | Low | Strict compliance, few domains |
| B: shared edge | Low | Policy-dependent | Medium | Many domains sharing an internet exit |
| C: service chaining (SFC) | Medium | Policy-dependent | High | Per-flow insertion of several services |

<div class="zh" markdown="1">

| 模型 | CAPEX | 隔离度 | 复杂度 | 适用 |
|---|---|---|---|---|
| A 每域独立 | 高 | 最高 | 低 | 强合规、少量域 |
| B 共享边界 | 低 | 依赖策略 | 中 | 多域、共享互联网出口 |
| C 服务链（SFC） | 中 | 依赖策略 | 高 | 需要"按流"插入多种服务 |

</div>

### Firewall Virtualisation (the Classic One-to-Many) · 防火墙虚拟化（一对多的典型）

```
     Physical firewall pair (HA)
  +---------------------------+
  | +----------+ +----------+ |  One context per tenant/domain
  | | vFW-A    | | vFW-B    | |  Separate policy, routing table, management
  | +----------+ +----------+ |
  +---------------------------+
```

<div class="zh" markdown="1">

```
     物理防火墙对（HA）
   ┌───────────────────────────┐
   │ ┌──────────┐ ┌──────────┐ │  每租户/每域一个上下文（context）
   │ │ vFW-A    │ │ vFW-B    │ │  独立策略、独立路由表、独立管理
   │ └──────────┘ └──────────┘ │
   └───────────────────────────┘
```

</div>

| Advantage | Watch out for |
|---|---|
| One hardware pair serves several domains, lower CAPEX | **No hard resource isolation**: one context can consume the session table or CPU and affect everyone |
| Independent policy and management per tenant | A software upgrade affects every context (same maintenance window) |
| Maps one-to-one onto VRFs, clean path | Traffic between contexts must be **explicitly permitted** (it is not "open by default") |
| Licensing per context is controllable | As contexts multiply, backup and audit complexity rises |

<div class="zh" markdown="1">

| 优势 | 注意 |
|---|---|
| 一套硬件服务多个域，降 CAPEX | **资源不硬隔离**：一个上下文吃满会话表/CPU，全部受影响 |
| 每租户独立策略与管理 | 软件升级影响所有上下文（同一维护窗口） |
| 与 VRF 一一对应，路径清晰 | 上下文间流量若需互通，**必须显式放行**（不是"默认通"） |
| 许可证按上下文计费，可控 | 上下文数量增长后，配置备份/审计复杂度上升 |

</div>

> ⚠️ **The most common design defect**: treating a "context" as an "independent firewall" and forgetting that contexts **share the same CPU, memory and session table**. Production designs should apply **per-context resource limits** (sessions, throughput) and monitor them.

<div class="zh" markdown="1">

> ⚠️ **最常见设计缺陷**：把"上下文"当成"独立防火墙"，忘记它**共享同一份 CPU/内存/会话表**。生产上应配置**每上下文资源限额**（会话数、吞吐）并监控。

</div>

### VRF-Aware NAT and the Fusion Router · VRF-Aware NAT 与 Fusion Router

A universal reality in multi-tenant scenarios: **different domains use overlapping private addresses** (all of them use 10.0.0.0/8).

<div class="zh" markdown="1">

多租户场景的普遍现实：**不同域使用重叠的私有地址**（都用 10.0.0.0/8）。

</div>

```
Tenant A (10.0.0.0/8 -- VRF-A) --+
                                +-- VRF-Aware NAT --> internet / shared services
Tenant B (10.0.0.0/8 -- VRF-B) --+
```

<div class="zh" markdown="1">

```
租户 A（10.0.0.0/8 ── VRF-A）──┐
                              ├── VRF-Aware NAT ──→ 互联网 / 共享服务
租户 B（10.0.0.0/8 ── VRF-B）──┘
```

</div>

- Each VRF has its own NAT pool and translation table → overlapping addresses do not conflict, and **path isolation is preserved**
- When several routing instances are merged into a single instance on **the same device** (to reach shared services or the internet), that device is called a **fusion router**
- A fusion router is a **natural leak point**: it is attached to every VRF at once

<div class="zh" markdown="1">

- 每个 VRF 独立 NAT 池与转换表 → 重叠地址不冲突，且**不破坏路径隔离**
- 当多个路由实例在**同一台设备**上合并到单一实例（用于访问共享服务/互联网）时，该设备称为 **fusion router**
- fusion router 是**天然的泄漏点**：它同时连着所有 VRF

</div>

> 🔥 **Three design constraints for a fusion router**:
> 1. **Allow leakage only in the necessary direction** (domain → shared service); block lateral domain-to-domain traffic with ACLs or a firewall
> 2. **NAT pools and addressing must be centrally managed** (otherwise pool exhaustion or overlap goes unnoticed)
> 3. **Report per VRF** (otherwise, when one domain saturates the exit, nobody can tell which)

<div class="zh" markdown="1">

> 🔥 **fusion router 的三条设计约束**：
> 1. **只允许"必要方向"的泄漏**（域 → 共享服务），禁止域间横向（用 ACL/防火墙兜住）
> 2. **NAT 池与地址规划必须集中管理**（否则池耗尽/重叠无人发现）
> 3. **监控按 VRF 维度出报表**（否则一张域打满出口，查不出是谁）

</div>

### VASI (VRF-Aware Services Infrastructure)

```
        +------------ same router / switch --------------+
        |  VRF-A ----[VASI interface pair]---- VRF-B     |
        |            internal logical link               |
        |  NAT / encryption / ACL / policy between VASIs |
        +------------------------------------------------+
```

<div class="zh" markdown="1">

```
        ┌──────────── 同一台路由器/交换机 ────────────┐
        │  VRF-A ────[VASI 接口对]──── VRF-B          │
        │            内部逻辑连线                      │
        │  可在 VASI 之间应用 NAT/加密/ACL/策略        │
        └────────────────────────────────────────────┘
```

</div>

- Allows services (NAT, IPsec, ACLs) to be applied **inside a single node** between two VRFs
- Configure a pair of VASI virtual interfaces, each in one VRF, logically connected inside the node
- **Available only on some high-end Cisco platforms**

<div class="zh" markdown="1">

- 允许在**同一节点内部**的两个 VRF 之间应用服务（NAT、IPsec、ACL）
- 配置一对 VASI 虚拟接口，各归属一个 VRF，节点内部逻辑相连
- **仅在部分高端 Cisco 平台上可用**

</div>

| Scenario | Use VASI | Use an external firewall |
|---|---|---|
| Between two domains you only need NAT/simple policy | ✅ saves hardware and hops | Over-design |
| You need stateful inspection / IPS / application identification | ❌ not capable enough | ✅ |
| You need audit and compliance-grade isolation evidence | ⚠️ depends on the compliance requirement | ✅ clearer |

<div class="zh" markdown="1">

| 场景 | 用 VASI | 用外部防火墙 |
|---|---|---|
| 两域间只需 NAT/简单策略 | ✅ 省设备、省跳数 | 过度设计 |
| 需要状态检测/IPS/应用识别 | ❌ 能力不足 | ✅ |
| 需要审计与合规隔离证据 | ⚠️ 视合规要求 | ✅ 更清晰 |

</div>

### NFV (Network Functions Virtualisation) · NFV（网络功能虚拟化）

```
Traditional: dedicated appliances        NFV: commodity x86 + virtual instances
+--------+ +--------+                   +--------------------------+
|Firewall| |Load bal|                   | +---+ +---+ +---+ +---+  |
|hardware| |hardware|                   | |vFW| |vLB| |vR | |vWAF| |
+--------+ +--------+                   | +---+ +---+ +---+ +---+  |
                                        |        Hypervisor         |
                                        +--------------------------+
```

<div class="zh" markdown="1">

```
传统：专用硬件                         NFV：通用 x86 + 虚拟实例
┌────────┐ ┌────────┐                ┌──────────────────────────┐
│ 防火墙  │ │ 负载均衡│                │  ┌───┐┌───┐┌───┐┌───┐  │
│ 硬件    │ │ 硬件    │                │  │vFW││vLB││vR ││vWAF│  │
└────────┘ └────────┘                │  └───┘└───┘└───┘└───┘  │
                                      │        Hypervisor        │
                                      └──────────────────────────┘
```

</div>

**The five benefits of NFV (book)**: lower TCO (fewer appliance types and units), lower operating cost (power and space), more economical capital spend, less integration and operational complexity, and **faster service rollout** (especially in multi-tenant scenarios).

<div class="zh" markdown="1">

**NFV 的五条收益（原书）**：降低 TCO（设备种类与数量减少）、降低运维成本（功耗/空间）、资本投入更经济、降低集成与运维复杂度、**缩短业务上线时间**（尤其多租户场景）。

</div>

> ⚠️ **What to watch in large networks (the book stresses this)**: you must account for **hardware resource utilisation and limits** — the throughput of a virtual instance depends on CPU cores, NUMA, SR-IOV and crypto offload. A vFW "rated 10 Gbps" may deliver only 2 Gbps with IPS and logging enabled.

<div class="zh" markdown="1">

> ⚠️ **大规模网络的注意点（原书强调）**：必须考虑**硬件资源利用率与限制** —— 虚拟实例的吞吐取决于 CPU 核数、NUMA、SR-IOV、加密卸载能力。一个"标称 10 Gbps"的 vFW，在开启 IPS + 日志后可能只有 2 Gbps。

</div>

### Service Chaining and the Return Path (Where the Design Actually Lands) · 服务链与回流路径（设计落地的关键）

```
        +------------ service insertion (PBR / policy routing / SFC) ------------+
User -> Access -> Distribution --> [vFW] --> server
                       ^                        |
                       +------------------------+  <- the return path must also cross [vFW]
```

<div class="zh" markdown="1">

```
        ┌──────────── 服务插入（PBR / 策略路由 / SFC）────────────┐
用户 → 接入 → 分布 ──→ [vFW] ──→ 服务器
                    ↑                   │
                    └───────────────────┘  ← 回程必须也经过 [vFW]
```

</div>

| Design point | How to do it |
|---|---|
| **Symmetric steering** | PBR steering in both directions, VASI, or place the service node on the VRF's only exit |
| **Session persistence** | Enable state synchronisation when service nodes run HA; otherwise a failover breaks every session |
| **MTU/MSS** | Service-chain encapsulation shrinks the MTU → apply MSS clamping on the service node or at the boundary |
| **Escape path** | Bypass when all service nodes are down (physical bypass or policy fallback), and **it must be rehearsed** |
| **Observability** | Bytes in/out, session counts and drop reasons per service chain, on a dashboard |

<div class="zh" markdown="1">

| 设计要点 | 做法 |
|---|---|
| **对称引流** | PBR 双向引流、VASI、或把服务节点放在 VRF 唯一的出口上 |
| **会话保持** | 服务节点 HA 时启状态同步；否则切换即断会话 |
| **MTU/MSS** | 服务链封装后 MTU 变小 → 在服务节点或边界做 MSS clamping |
| **逃生路径** | 服务节点全挂时的 bypass（物理 bypass 或策略回退），且**必须演练** |
| **可观测性** | 每条服务链的进出字节/会话数/丢弃原因进看板 |

</div>

> 🎯 **In one line**: **the hard part of service virtualisation is not the virtualisation, it is "letting asymmetric traffic make a round trip and come back".** Any design document without a "return arrow" will meet "ping works but the web page does not load" after go-live.

<div class="zh" markdown="1">

> 🎯 **一句话**：**"服务虚拟化"的技术难点不在虚拟化，而在"让流量非对称地绕一圈还能回来"。** 设计文档里没有"回程箭头"的方案，上线后一定会遇到"能 ping 通但打不开网页"。

</div>

---

## 7. Capacity and Scalability Models (Extended in These Notes) · 七、容量与可扩展性模型（本笔记延伸）

![Figure 15-22 · Four budgets that get skipped](assets/fig/en15-22-capacity-budgets.svg)

The book focuses on architectural decisions; this section adds the part where **the architecture is turned into numbers** — the most frequently mis-calculated and most often skipped content in architecture work.

<div class="zh" markdown="1">

原书侧重架构决策，本章补上"把架构算成数字"的部分 —— 这是架构设计里最容易算错、也最容易被忽略的内容。

</div>

### Endpoint Density and Access Switch Count · 终端密度与接入交换机数量

| Area | Endpoints per port | Port utilisation | Notes |
|---|---|---|---|
| Standard workstation | 1.0–1.3 | 80% | One port per person plus 20% headroom |
| Meeting room | 0.2–0.5 | — | Mostly wireless; wired only for casting or phones |
| Classroom / training room | 0.5–1.0 | — | One port per two seats |
| Printers / IoT / cameras | Fixed count | — | Separate VLAN, include in PoE calculation |

<div class="zh" markdown="1">

| 场所 | 每端口终端数 | 端口利用率 | 说明 |
|---|---|---|---|
| 标准工位 | 1.0–1.3 | 80% | 一人一端口 + 预留 20% |
| 会议室 | 0.2–0.5 | — | 主要靠无线，有线仅投屏/话机 |
| 教室/培训室 | 0.5–1.0 | — | 每 2 座 1 口 |
| 打印机/IoT/摄像头 | 固定数 | — | 单独 VLAN，PoE 计算 |

</div>

```
Access switches = ceil( wired port demand / (24 or 48 x port utilisation) ) x (1 + 15% spare)
```

<div class="zh" markdown="1">

```
接入交换机数 = ⌈ 有线端口需求 / (24 或 48 × 端口利用率) ⌉ × (1 + 15% 备用量)
```

</div>

> 💡 **Closet constraints often become the bottleneck before port count does**: an IDF rack typically holds 4–6 1RU switches plus 2 distribution switches, **and is limited by PoE power and heat**. Design the rack first, then the ports.

<div class="zh" markdown="1">

> 💡 **配线间约束常比端口数更早成为瓶颈**：一个 IDF 机柜通常只能放 4–6 台 1RU 交换机 + 2 台分布交换机，**且受 PoE 电源与散热限制**。设计时先算机柜，再算端口。

</div>

### Wireless and PoE Budget · 无线与 PoE 预算

| Standard | Power available per port | Typical use |
|---|---|---|
| 802.3af (Type 1) | 15.4 W | Phones, ordinary APs |
| 802.3at (Type 2) | 30 W | Wi-Fi 6 APs (typically 802.3at) |
| 802.3bt (Type 3/4) | 60 W / 90 W | Wi-Fi 6E/7 APs, high-power IoT |

<div class="zh" markdown="1">

| 标准 | 每端口可用功率 | 典型用途 |
|---|---|---|
| 802.3af (Type 1) | 15.4 W | 话机、普通 AP |
| 802.3at (Type 2) | 30 W | Wi-Fi 6 AP（典型 802.3at） |
| 802.3bt (Type 3/4) | 60 W / 90 W | Wi-Fi 6E/7 AP、高功率 IoT |

</div>

```
PoE budget = sum( max power per port x probability that port draws power ) x (1 + 20% headroom)
```

<div class="zh" markdown="1">

```
PoE 预算 = Σ(每口最大功率 × 该口供电概率) × (1 + 20% 余量)
```

</div>

Example: a 48-port access switch, expected 20 × 802.3at APs (30 W) plus 20 phones (7 W):

<div class="zh" markdown="1">

实例：48 口接入交换机，预计 20 个 802.3at AP（30 W）+ 20 台话机（7 W）：

</div>

```
APs: 20 x 30 = 600 W; phones: 20 x 7 = 140 W; total 740 W
+20% headroom -> 890 W -> two 740 W+ power supplies (or a 1100 W supply)
```

<div class="zh" markdown="1">

```
AP: 20 × 30 = 600 W；话机: 20 × 7 = 140 W；合计 740 W
含 20% 余量 → 890 W  → 需配 2 个 740 W 以上电源（或选 1100 W 电源）
```

</div>

> ⚠️ **A common incident**: the PoE budget is designed against af (15.4 W) but the APs negotiate at (30 W) → the switch power supply is oversubscribed → **APs that come up later reboot repeatedly**, and the log only says "power denied".

<div class="zh" markdown="1">

> ⚠️ **常见事故**：AP 按 af 预算（15.4 W）设计，实际 AP 协商成 at（30 W）→ 交换机电源超额 → **后上线的 AP 反复重启**，且日志只显示"power denied"。

</div>

### Bandwidth Oversubscription · 带宽收敛比

| Layer | Typical oversubscription | Notes |
|---|---|---|
| Access → distribution | 20:1 ~ 48:1 (1G access / 10G uplink) | Acceptable in a campus because peaks do not coincide |
| Distribution → core | 2:1 ~ 4:1 | Must leave headroom for east-west traffic (DC access, servers) |
| Core → exit | Depends on WAN/internet bandwidth | The exit is the only point that must be designed to the contracted bandwidth |

<div class="zh" markdown="1">

| 层级 | 常见收敛比 | 说明 |
|---|---|---|
| 接入 → 分布 | 20:1 ~ 48:1（1G 接入 / 10G 上行） | 园区可接受，因为峰值不同时 |
| 分布 → 核心 | 2:1 ~ 4:1 | 需要为东西向流量（DC 访问、服务器）留余量 |
| 核心 → 出口 | 视 WAN/互联网带宽 | 出口是唯一必须"按合同带宽"设计的点 |

</div>

> 🎯 **The correct order for campus bandwidth design**: size the **exit** first (contracted bandwidth + peak), then the **core** (east-west + north-south), and only then the access uplinks. Doing it the other way round gives you "10G everywhere at the access layer and a 100M exit that makes everything look like a slideshow".

<div class="zh" markdown="1">

> 🎯 **园区带宽设计的正确顺序**：先算**出口**（合同带宽 + 峰值），再算**核心**（东西向 + 南北向），最后才是接入上行。反着算的结果是"接入全是 10G，出口 100M 卡成 PPT"。

</div>

### VLAN / Subnet / Broadcast-Domain Scale · VLAN / 子网 / 广播域规模

| Item | Practical upper bound | Why |
|---|---|---|
| Endpoints per VLAN/subnet | ≤ 500 (recommended ≤ 250) | ARP/ND table, broadcast, DHCP scope |
| VLANs per closet | ≤ 8 | Trunk pruning complexity, STP instances |
| VLANs per campus | ≤ 200 (much more means the boundary is wrong) | Management complexity, IP planning |
| Spanning-Tree diameter | ≤ 7 hops | RSTP convergence and stability |
| ARP/ND entries per distribution switch | ≤ 8,000 (platform dependent) | Control-plane memory, ARP policing |

<div class="zh" markdown="1">

| 约束 | 建议上限 | 依据 |
|---|---|---|
| 单 VLAN 终端数 | 200–500（IPv4 /24 上限 254） | 广播、ARP 表、DHCP 租约、故障域 |
| 单 VLAN 的 STP 域跨度 | 越短越好（最好单配线间） | 收敛与风暴半径 |
| 单设备 MAC 表利用率 | <50% | 老交换机 8K–16K 表项 |
| 单设备 ARP 表 | <50% | 网关设备的关键隐性资源 |
| DHCP scope | 与 VLAN 一一对应 + 20% 余量 | 避免"地址池耗尽"型故障 |

</div>

### Routing-Table and Virtualisation Scale · 路由表与虚拟化规模

| Item | Practical value | Constraint |
|---|---|---|
| Campus IGP routes | Low thousands | Above that, summarisation or the IGP/BGP boundary is wrong |
| EIGRP neighbours per device | ≤ 50–100 | Query scope and CPU |
| OSPF areas | ≤ 10–15 | More areas means more ABRs and more summary conflicts |
| VRFs per distribution switch | ≤ 50–100 | Memory, policy count, management complexity |
| MPLS VPN VRFs per PE | ≤ 500 (platform dependent) | Route targets, RD planning, RR sessions |

<div class="zh" markdown="1">

| 项目 | 园区典型值 | 上限信号 |
|---|---|---|
| 园区 IGP 路由条目 | 500–5,000 | >10,000 说明汇总缺失或边界没画 |
| VRF 数量 | 3–20 | >50 后配置/审计/监控成本陡增 |
| 每 VRF 路由条目 | 与 IGP 同量级 | 明细泄漏（`redistribute` 无过滤）会爆炸 |
| 隧道/mGRE 对端数 | <200 | 更多时应考虑 fabric |

</div>

### Convergence Budget (Numbers to Put in the Design Document) · 收敛预算（写进设计文档的数字）

| Event | Multitier STP | Routed access | Clustering | Budget target |
|---|---|---|---|---|
| Access uplink failure | 3–18 s | <1 s | <1.5 s | ≤ 1 s (greenfield) |
| Distribution node failure | 10–30 s | 1–3 s | 1–2 s | ≤ 3 s |
| Core link failure | 1–5 s | <1 s | <1 s | ≤ 1 s |
| Wireless roaming | 100–500 ms | Same | Same | ≤ 100 ms (voice ≤ 50 ms) |
| Routing protocol convergence (stub + summary) | — | 200 ms–1 s | — | ≤ 1 s |
| **Application session recovery** | 0–300 s | 0–300 s | 0–300 s | **Cannot be designed; must be validated** |

<div class="zh" markdown="1">

| 场景 | 目标 | 手段 |
|---|---|---|
| 接入上行单链路断 | <1 s | BFD + ECMP |
| 分布交换机单台宕 | <1 s | IGP + BFD + 汇总（避免黑洞） |
| 核心单链路断 | <1 s | ECMP + BFD |
| 网关（FHRP）切换 | <2 s | 毫秒定时器 + 延迟抢占 |
| 无线漫游 | <100 ms（语音） | 802.11r/k/v + 控制器优化 |
| 服务节点切换 | <3 s（允许会话重建） | HA 状态同步 + 健康检查 |

</div>

---

## 8. From Design to Delivery: The Nine Tables This Chapter Must Produce · 八、从设计到交付：本章必须的 9 张表

![Figure 15-23 · The nine deliverable tables](assets/fig/en15-23-nine-tables.svg)

A campus design that is "only a topology diagram" cannot be reviewed or accepted. The book implies, and this note makes explicit, nine tables a campus design deliverable must contain:

<div class="zh" markdown="1">

设计文档不是散文。以下九张表是园区方案的"可评审载体"，缺一张就有一类决策没有被固化。

</div>

| # | Table | Key columns | Who uses it |
|---|---|---|---|
| 1 | Functional-block table | Block name, endpoints, bandwidth, availability class, exit point | Design review, capacity |
| 2 | Tier-selection table | Two-tier or three-tier, justification (business dimension) | Business and design review |
| 3 | Access-model selection table | Model, convergence, failure behaviour, limitation | Design review |
| 4 | L2/L3 boundary table | Which closets are L2, which are L3, gateway location | Implementation |
| 5 | Routing design table | IGP, areas/queries, summary points, FHRP/BFD | Implementation, operations |
| 6 | Addressing table | Subnets, VLANs, pools, summary boundaries | Implementation, IPAM |
| 7 | Virtualisation table | VRF/VN, RT/RD, isolation technique, fusion point | Security, implementation |
| 8 | Capacity and convergence table | Ports, bandwidth, PoE, RIB, convergence budget | Acceptance, operations |
| 9 | Acceptance case table | Fault scenarios, expected behaviour, measured value | Acceptance, operations |

<div class="zh" markdown="1">

| # | 表名 | 内容 | 谁看 |
|---|---|---|---|
| 1 | **功能块清单** | 块名/用途/终端数/带宽/可用性等级/所属区域 | 架构评审 |
| 2 | **楼栋—配线间—设备映射** | 每 IDF 的交换机型号、端口数、PoE 预算、上联方式 | 实施与采购 |
| 3 | **接入模型决策表** | 每块使用的模型（STP/路由接入/集群）+ 理由 + 风险 | 架构评审 |
| 4 | **地址与 VLAN 规划表** | 前缀/VLAN ID/网关/VRF/DHCP scope/汇总边界 | 实施 + IPAM |
| 5 | **IGP 设计表** | 协议/进程/区域或 AS/邻居关系/汇总点/Stub 范围 | 运维 |
| 6 | **路径隔离与服务链表** | VRF/VN ↔ 业务 ↔ 服务节点 ↔ 去程/回程路径 | 安全 + 运维 |
| 7 | **容量与功率表** | 端口/带宽/收敛比/PoE/机柜 U 位/光模块 | 采购 + 实施 |
| 8 | **收敛与可用性目标表** | 场景 → 目标时间 → 检测机制 → 验证方法 | 评审 + 验收 |
| 9 | **验收用例表** | 每类故障的注入方式 + 预期 + 实测结果 | 验收 |

</div>

> 🎯 **A missing table means a design decision has not been made.** If a review asks "what happens if the peer-link fails" and there is no answer on paper, that is not bad luck, it is a design defect.

<div class="zh" markdown="1">

> 💡 第 9 张表最容易被跳过，也最能救命。**"没演练过的高可用等于不存在"**（第 14 章同款结论）。

</div>

---

## Real-World Case Studies (14 Scenarios) · 实战案例（14 个真实场景）

### 🔥 Case 1: Six Functional Blocks Crammed Into a Collapsed Core — One Gateway Switchover "Shakes the Whole Network for 40 Seconds" · 🔥 案例一：collapsed core 里硬塞 6 个功能块，一次网关切换"全网抖 40 秒"

**Symptom**: a mid-size campus (4 buildings, 2,800 endpoints) uses the two-tier model. A single collapsed core/distribution pair carries the user block, wireless block, DC block, WAN block, DMZ block and management block at once. When core A's power module fails, the whole network goes down for about 40 seconds, and for ten minutes afterwards some servers are still unreachable.

<div class="zh" markdown="1">

**现象**：中型园区（4 栋楼、2,800 终端）用二层模型，核心分布合一的一对交换机上同时挂：用户块、无线块、DC 块、WAN 块、DMZ 块、管理块。某次核心 A 电源模块故障，全网中断约 40 秒，恢复后部分服务器访问仍异常 10 分钟。

</div>

**Investigation**: configuration review shows that all six blocks' SVIs live on the same pair (**about 180 VLANs**); the STP root is on A while HSRP active is on B (opposite sides). When A dies, B becomes the STP root **and** takes over 180 gateways, while OSPF recomputes and a large number of hosts lose their ARP entries.

<div class="zh" markdown="1">

**排查**：核对配置发现 —— 6 个块的 SVI 全在这对设备上（**约 180 个 VLAN**），STP 根在 A、HSRP Active 在 B（不同侧）；A 宕机时 B 变 STP 根 + 接管 180 个网关，同时 OSPF 重算、大量主机 ARP 失效。

</div>

**Root cause**: **a two-tier model carrying six functional blocks** (the book recommends ≤3), plus **gateway and root bridge on opposite sides**, so a single failure triggers three simultaneous changes: root, gateway and routing.

<div class="zh" markdown="1">

**根因**：**用二层模型承载了 6 个功能块**（原书建议 ≤3），且**网关与根桥不同侧**，故障时"根 + 网关 + 路由"三重变化叠加。

</div>

**What should have been done**:
- Split: the DC block and WAN block become their own distribution blocks (even if that is only two switches), and introduce a dedicated core layer
- Force the root bridge and HSRP active onto the same side, with `standby track` plus preemption delay
- Spread SVIs across different device pairs by block, keeping SVIs per device below 80
- Rehearse "core A power loss", measure the switchover and write the number into the document

<div class="zh" markdown="1">

**正确做法**：
- 拆分：DC 块与 WAN 块独立成分布块（哪怕只有 2 台交换机），核心层独立出来
- 根桥与 HSRP Active 强制同侧，用 `standby track` + 延迟抢占
- SVI 数量按块拆到不同设备对，单设备 SVI <80 个
- 演练"核心 A 断电"，实测切换时间并写进文档

</div>

### 🔥 Case 2: Routed Access "Half Done" — Convergence Did Not Improve at All · 🔥 案例二："路由接入"做了一半，收敛一点没变快

**Symptom**: a new campus claims "fully routed access", but users complain that "the web page hangs for 10 seconds a few times a day". Monitoring shows frequent STP topology changes.

<div class="zh" markdown="1">

**现象**：新园区宣称"全部路由接入"，但用户投诉"每天总有几次网页卡 10 秒"。监控显示 STP 拓扑变化频繁。

</div>

**Investigation**: the access switches do run OSPF, but **every user gateway is still an SVI on the distribution layer** — the access switches merely forward Layer 3 point-to-point upward. VLANs still span several access switches, so STP still exists; the only change is one extra hop.

<div class="zh" markdown="1">

**排查**：接入交换机确实跑了 OSPF，但**所有用户网关仍在分布层的 SVI 上**，接入交换机只是三层点到点向上转发；VLAN 仍跨多台接入延伸 → STP 依然存在，只是路径变长了一跳。

</div>

**Root cause**: mistaking "the access switch has an IP address" for "routed access". **The definition of routed access is the gateway being at the access layer**; otherwise the STP dependency is unchanged.

<div class="zh" markdown="1">

**根因**：把"接入交换机有 IP 地址"误当成"路由接入"。**路由接入的定义是网关在接入层**，否则 STP 依赖照旧。

</div>

**What should have been done**:
- Move the gateway (SVI) down to the access switch, with /31 routed uplinks or Layer 3 port-channels
- Give every wiring closet its own subnet, generated from a DHCP scope template
- Add one hard acceptance criterion: **"no VLAN may span devices at the access layer"**
- List the exceptions (wireless, cluster heartbeat) separately with a stated reason

<div class="zh" markdown="1">

**正确做法**：
- 网关（SVI）下移到接入交换机，上行用 /31 路由口或三层聚合
- 每配线间独立子网，DHCP scope 模板化生成
- 检查清单加一条硬指标：**"接入层设备上不得出现跨设备的同一 VLAN"**
- 保留的例外（无线、集群心跳）单独列出并标注原因

</div>

### 🔥 Case 3: vPC peer-link and peer-keepalive on the Same Fibre Pair — Eight Minutes of Dual-Active · 🔥 案例三：vPC 的 peer-link 与 peer-keepalive 走同一条光纤，双主 8 分钟

**Symptom**: during a rack relocation an engineer pulls one fibre, and both distribution switches become gateways at the same time (dual-active). The whole campus reports IP address conflicts, broadcast volume explodes, and service is only restored after one switch is manually shut down eight minutes later.

<div class="zh" markdown="1">

**现象**：一次机柜搬迁，运维拔了一根光纤，结果两台分布交换机同时成为网关（双主），全网出现 IP 冲突告警，广播量暴涨，8 分钟后人工关掉一台才恢复。

</div>

**Investigation**: the peer-link is 2×10G fibre, and peer-keepalive is configured on **a subinterface of the same fibre pair** ("to save a pair of optics"). Pulling that fibre kills both the peer-link and the keepalive, so each switch believes its peer is dead and both become active.

<div class="zh" markdown="1">

**排查**：peer-link 是 2×10G 光纤；peer-keepalive 恰好配在**同一对光纤上的子接口**（"省一对光模块"）。光纤被拔 → peer-link 和 keepalive 同时断 → 两台都认为对端已死 → 都升为 Active。

</div>

**Root cause**: **keepalive and peer-link share a failure domain**, which destroys the only thing keepalive provides: independence.

<div class="zh" markdown="1">

**根因**：**keepalive 与 peer-link 共享故障域**，失去了"独立性"这个唯一价值。

</div>

**What should have been done**:
- peer-keepalive must take an **independent physical path** (management switch, out-of-band, OOB link)
- Dual-active protection: `auto-recovery reload-delay` in addition to `peer-gateway`, plus a written runbook for "shut one switch down manually"
- Change management: any change touching the peer-link or keepalive needs two-person review
- Monitoring: alert on peer-keepalive loss and vPC state changes

<div class="zh" markdown="1">

**正确做法**：
- peer-keepalive 必须走**独立物理路径**（管理交换机/带外/OOB 链路）
- 双主防护：配置 `peer-gateway` 之外的 `auto-recovery reload-delay`，并准备"手动关一台"的 Runbook
- 变更管理：任何涉及 peer-link/keepalive 的变更必须双人复核
- 监控：peer-keepalive 丢包率、vPC 状态变化告警

</div>

### 🔥 Case 4: HSRP Active on A, STP Root on B — the Inter-Switch Link Saturates · 🔥 案例四：HSRP Active 在 A、STP 根在 B，串联链路被打满

**Symptom**: every working day between 09:00 and 10:30 the office reports "the internet is slow and the shared drive hangs". The link between the core switches runs at 100% while each of the two uplinks is only at 30%.

<div class="zh" markdown="1">

**现象**：每个工作日 9:00–10:30，办公楼"上网慢、打开共享盘卡"，核心间互联链路利用率 100%，而两条上行各自只有 30%。

</div>

**Investigation**: outbound traffic follows the gateway (HSRP active, switch A) but the return traffic comes back through the STP root on switch B, so traffic crosses **the A→B inter-switch link**, which becomes the bottleneck. The more users, the worse it gets.

<div class="zh" markdown="1">

**排查**：去程流量走网关（HSRP Active，A 机），回程从核心回来时 STP 根在 B，导致流量**经 A→B 的串联链路**再下发，串联链路成为瓶颈。用户越多越明显。

</div>

**Root cause**: **the gateway position and the Layer 2 topology root are inconsistent** (the classic triangular detour).

<div class="zh" markdown="1">

**根因**：**网关位置与二层拓扑根位置不一致**（经典"三角绕行"）。

</div>

**What should have been done**:
- Force "STP root = HSRP active = IGP best exit" onto the same side (configuration alignment plus a periodic audit script)
- Or use vPC so both switches forward, removing the topological basis for the detour altogether
- Acceptance before go-live: at peak hours, capture `load-interval 30` utilisation on both sides and look for "one side saturated, the other idle"

<div class="zh" markdown="1">

**正确做法**：
- 强制"STP 根 = HSRP Active = IGP 最优出口"同侧（配置对齐 + 定期审计脚本）
- 或者干脆用 vPC 让两台都转发（消除绕行的拓扑基础）
- 上线前的验收：在高峰时段抓两端接口的 `load-interval 30` 利用率，看是否出现"单侧满载、对侧空闲"

</div>

### 🔥 Case 5: No EIGRP Stub — One Flapping Link Leaves the Network "Offline for Three Minutes" · 🔥 案例五：EIGRP 没配 stub，一次链路抖动让全网"失联 3 分钟"

**Symptom**: the uplink optic of one floor's access switch flaps (about 2 seconds each time), yet the whole network suffers roughly three minutes of "slow service / some subnets unreachable". `show ip eigrp topology active` shows a large number of active entries.

<div class="zh" markdown="1">

**现象**：某楼层接入交换机上行光模块抖动（每次约 2 秒），但全网有 3 分钟左右的"业务缓慢/部分网段不可达"；`show ip eigrp topology active` 显示大量 active 条目。

</div>

**Investigation**: the access layer has no `eigrp stub` and no summarisation upward, so one uplink change floods queries across the network. Edge routers and branch devices all have to answer, some neighbours time out, and SIA follows (three minutes by default).

<div class="zh" markdown="1">

**排查**：接入层没有 `eigrp stub`，也没有向上汇总；一次上行变化触发 query 向全网扩散，边缘路由器/分支设备都要应答，部分邻居超时 → SIA（默认 3 分钟）。

</div>

**Root cause**: **the query domain is the whole network**. A distance-vector protocol's scalability depends entirely on whether queries can be stopped.

<div class="zh" markdown="1">

**根因**：**查询域 = 全网**。距离矢量协议的可扩展性完全依赖"查询能不能被挡住"。

</div>

**What should have been done**:
- On every access switch: `eigrp stub connected summary` (queries are never forwarded)
- Summarise from the distribution layer toward the core (`ip summary-address eigrp <as> <prefix> <mask>`)
- Add route-map filters at key boundaries to prevent detail routes leaking
- Monitor SIA counts and active entries (both should be zero)

<div class="zh" markdown="1">

**正确做法**：
- 所有接入层：`eigrp stub connected summary`（禁止转发 query）
- 分布层向核心方向做汇总（`ip summary-address eigrp <as> <prefix> <mask>`）
- 关键边界加 route-map 过滤明细，防止泄漏
- 监控 SIA 计数与 active 条目数（应为 0）

</div>

### 🔥 Case 6: Both ABRs Summarise — Traffic Detours 200 km After a Failure · 🔥 案例六：两个 ABR 同时汇总，故障后流量绕行 200 公里

**Symptom**: two campuses (city A and city B) are interconnected by two long-haul links. After an uplink failure in one building in city A, users in that building reach the **local** server by detouring through city B and back. Latency goes from 3 ms to 60 ms and stays there until the link recovers.

<div class="zh" markdown="1">

**现象**：双园区（A 市、B 市）通过两条长途链路互连，A 市某栋楼的上行故障后，该楼用户访问本地服务器变成"绕行 B 市再回来"，时延从 3 ms 变 60 ms，持续到链路恢复。

</div>

**Investigation**: the area containing that building is summarised with `area range` on **both ABRs**. After the failure, one ABR loses its detail path, but the summary route is still advertised by the other ABR (its summary does not depend on the detail), so traffic is pulled to city B and then returns.

<div class="zh" markdown="1">

**排查**：该楼所属区域在**两台 ABR 上都做了 `area range` 汇总**。故障后一台 ABR 的明细路径消失，但汇总路由仍从另一台 ABR 通告（因为它的汇总不依赖明细），于是流量被吸引到 B 市再回程。

</div>

**Root cause**: **suboptimal paths created by multi-ABR summarisation** — a structural OSPF cost the book calls out explicitly.

<div class="zh" markdown="1">

**根因**：**多 ABR 汇总产生的次优路径**（原书明确指出的 OSPF 固有代价）。

</div>

**What should have been done**:
- For critical areas, **summarise on only one ABR** (the other advertises details or uses a different metric)
- Use `area range ... cost` to differentiate, so the backup ABR advertises a higher summary metric
- Do not summarise latency-sensitive prefixes
- Record the "acceptable suboptimality" explicitly in the design document (for example ≤2 hops / ≤10 ms)

<div class="zh" markdown="1">

**正确做法**：
- 关键区域**只在一台 ABR 上汇总**（另一台只通告明细或不同 metric）
- 用 `area range ... cost` 差异化，让备份 ABR 的汇总 metric 更高
- 对时延敏感的前缀不做汇总
- 在设计文档中显式记录"允许的次优程度"（例如 ≤2 跳 / ≤10 ms）

</div>

### 🔥 Case 7: One VLAN Across 3 Buildings and 2,000 Endpoints — One ARP Storm Takes Down the Building · 🔥 案例七：一个 VLAN 跨 3 栋楼 2,000 终端，一次 ARP 风暴拖垮全楼

**Symptom**: after a "unified office VLAN" is extended to 2,000 endpoints, the building occasionally "freezes for 30 seconds". Packet captures show large volumes of ARP requests and unknown unicast flooding.

<div class="zh" markdown="1">

**现象**：某"统一办公 VLAN"扩到 2,000 终端后，偶发全楼"网络卡死 30 秒"；抓包显示大量 ARP 请求/未知单播泛洪。

</div>

**Investigation**: the VLAN spans 3 buildings and 12 access switches, with an STP domain diameter of 5 hops. One endpoint with a faulty NIC floods ARP (hundreds per second), and combined with unknown unicast flooding it saturates the uplinks and switch CPUs.

<div class="zh" markdown="1">

**排查**：该 VLAN 跨 3 栋楼、12 台接入交换机，STP 域直径 5 跳；某台终端的网卡故障持续发 ARP（每秒数百），加上未知单播泛洪，直接打满上行与 CPU。

</div>

**Root cause**: **broadcast domain = failure domain**, and the scale far exceeds the recommendation (≤500 per VLAN).

<div class="zh" markdown="1">

**根因**：**广播域 = 故障域**，且规模远超建议值（单 VLAN ≤500）。

</div>

**What should have been done**:
- Split VLANs by building and by floor (≤250–500 endpoints each) and use summarisation to keep routing simple
- Enable Storm Control on access ports (separate limits for broadcast / multicast / unknown unicast)
- Enable DHCP Snooping + DAI + IP Source Guard (Chapter 10)
- Key point: **treat "a large Layer 2 domain across buildings" as an exception that requires a business justification** — the default is no

<div class="zh" markdown="1">

**正确做法**：
- 按楼/按层拆 VLAN（每 VLAN ≤250–500 终端），用汇总保持路由简洁
- 接入端口开 Storm Control（广播/组播/未知单播分别限速）
- 开 DHCP Snooping + DAI + IP Source Guard（第 10 章）
- 关键：**把"跨楼大二层"当作需要业务理由的例外**，默认不允许

</div>

### 🔥 Case 8: End-to-End VLAN+VRF With One Missing Hop — Business "Randomly Unreachable" · 🔥 案例八：端到端 VLAN+VRF 漏配一跳，业务"随机不通"

**Symptom**: two weeks after a new isolation design (end-to-end VLAN + VRF) goes live, the finance system is "sometimes fine, sometimes not" for users; a few retries usually work.

<div class="zh" markdown="1">

**现象**：新上线的隔离方案（端到端 VLAN + VRF）运行两周后，财务系统的用户"时好时坏"，重试几次又能通。

</div>

**Investigation**: the path crosses 5 devices, and **one distribution switch does not have the VLAN in its trunk allowed list**. That switch happens to be the backup path for one distribution block, so traffic only breaks when load sharing reaches it (about 30% of sessions).

<div class="zh" markdown="1">

**排查**：路径上有 5 跳设备，其中**一台分布交换机的一个 VLAN 没进 Trunk 允许列表**；该交换机恰好是其中一个分布块的备用路径，只有负载分担到它时才断（约 30% 会话）。

</div>

**Root cause**: end-to-end configuration consistency rests entirely on humans, so **one missing link produces "probabilistic failures"**.

<div class="zh" markdown="1">

**根因**：端到端配置的一致性完全靠人工，**缺一条链路就产生"概率性故障"**。

</div>

**What should have been done**:
- Use configuration templates plus automated validation (compare `show vlan brief` and trunk allowed lists across all devices)
- Build a hop-by-hop verification matrix before go-live (source/destination × each hop × forward/reverse)
- Add end-to-end synthetic probing (IP SLA) for critical services instead of only monitoring interface up/down
- If it has to be maintained long term, move to a solution with a control plane (mGRE / MPLS VPN / fabric) to remove hop-by-hop consistency

<div class="zh" markdown="1">

**正确做法**：
- 用配置模板 + 自动化校验（`show vlan brief` / Trunk 允许列表比对，迭代全设备）
- 上线前做"逐跳验证矩阵"（源/目的 × 每跳 × 去程/回程）
- 关键业务加端到端合成探测（IP SLA），而不是只监控设备端口 up
- 若要长期维护，升级到有控制面的方案（mGRE/MPLS VPN/fabric）以消除逐跳一致性

</div>

### 🔥 Case 9: mGRE Isolation "Pings Fine, Web Pages Will Not Load" — MTU · 🔥 案例九：mGRE 隔离后"能 ping 通、打不开网页"，卡在 MTU

**Symptom**: a branch reaches the headquarters isolation domain through mGRE. Ping is fine, Telnet is fine, but HTTPS pages stall halfway through loading and file transfers fail.

<div class="zh" markdown="1">

**现象**：分支通过 mGRE 接入总部隔离域，ping 正常、Telnet 正常，但 HTTPS 页面加载一半卡住、文件传输失败。

</div>

**Investigation**: tunnel encapsulation leaves an effective MTU of about 1,400 B. TCP handshakes (small packets) work; large packets are dropped and **no ICMP Fragmentation Needed comes back** (policy blocks it), so PMTUD fails and large packets fall into a black hole.

<div class="zh" markdown="1">

**排查**：隧道封装后有效 MTU 约 1,400 B；TCP 握手（小包）正常，大包被丢且**路径上没有返回 ICMP Fragmentation Needed**（被策略拦了）→ PMTUD 失效 → 大包黑洞。

</div>

**Root cause**: **MTU/MSS was never designed** — the classic "tunnel + ICMP blocked" combination, the same root as the IPv6 section in Chapter 14.

<div class="zh" markdown="1">

**根因**：**MTU/MSS 未设计**（典型"隧道 + 禁 ICMP"叠加故障，与第 14 章 IPv6 一节同源）。

</div>

**What should have been done**:
- `ip tcp adjust-mss 1360` on the tunnel interface (or calculated from the encapsulation)
- Permit ICMP Type 3 Code 4 (IPv4) / Type 2 (IPv6) through policy
- Probe the MTU at both tunnel ends and record the design value (do not assume 1500)
- Acceptance cases: `ping -l 1400 -f`, a large file transfer, and a full HTTPS page load

<div class="zh" markdown="1">

**正确做法**：
- 隧道口 `ip tcp adjust-mss 1360`（或按封装计算）
- 允许 ICMP Type 3 Code 4（IPv4）/ Type 2（IPv6）通过策略
- 在隧道两端做 MTU 探测并记录设计值（不要用默认 1500）
- 验收用例：大包 `ping -l 1400 -f`、大文件传输、HTTPS 完整加载

</div>

### 🔥 Case 10: The Fusion Router Imports Every VRF — Isolation Exists Only on Paper · 🔥 案例十：fusion router 导入了所有 VRF，隔离名存实亡

**Symptom**: a compliance audit finds that "the production domain can reach the guest domain", while the design document claims "complete isolation".

<div class="zh" markdown="1">

**现象**：合规审计发现"生产域与访客域可以互相访问"，而设计文档写的是"完全隔离"。

</div>

**Investigation**: to reach shared DNS/NTP, the exit device (fusion router) has route import between VRFs (`import map`). Later, to make troubleshooting easier, somebody adds a `permit all` entry to the import map. Both VRFs become fully reachable, **with no ACL as a backstop**.

<div class="zh" markdown="1">

**排查**：出口设备（fusion router）上为了访问共享 DNS/NTP，配置了 VRF 之间的路由导入（`import map`）；后来为方便排障，有人在 import map 里加了一条 `permit all`，两端 VRF 全部互通，且**没有任何 ACL 兜底**。

</div>

**Root cause**: **no default deny at the leak point**, and changes went unreviewed.

<div class="zh" markdown="1">

**根因**：**泄漏点没有默认拒绝**，且变更无复核。

</div>

**What should have been done**:
- Use an **explicit allow list** at the leak point (prefix level plus port level) with default deny
- Route all inter-VRF access through the firewall or a policy device on the fusion router — never directly
- Change management: any change to import/export maps is a high-risk change
- Periodic automated validation: probe from every VRF to targets that must not be reachable — all should fail

<div class="zh" markdown="1">

**正确做法**：
- 泄漏点用**显式允许清单**（前缀级 + 端口级），默认拒绝
- fusion router 与 VRF 间访问一律经过防火墙/策略设备，不直连
- 变更管理：import/export map 的修改纳入高风险变更
- 定期自动化验证：从每个 VRF 发探测到"不该可达"的目标，应全部失败

</div>

### 🔥 Case 11: One Tenant Fills the Virtual Firewall's Session Table — Every Tenant Slows Down · 🔥 案例十一：一个租户打满虚拟防火墙会话表，全部租户同时变慢

**Symptom**: in a multi-tenant campus, all business domains slow down dramatically when reaching the internet on a particular day. Firewall CPU at 95%, session table at 100%.

<div class="zh" markdown="1">

**现象**：多租户园区，某天所有业务域访问互联网都极慢；防火墙 CPU 95%，会话表 100%。

</div>

**Investigation**: one tenant's backup job (a huge number of short-lived connections) creates 1.2 million sessions in 20 minutes. The virtual context **has no resource limits**, so it consumes the whole physical firewall's session table and CPU.

<div class="zh" markdown="1">

**排查**：某租户的备份任务（大量短连接）在 20 分钟内建立 120 万会话，虚拟上下文**未设置资源限额**，吃满整个物理防火墙的会话表与 CPU。

</div>

**Root cause**: **one-to-many virtualisation without hard resource isolation** — the textbook example of fate sharing.

<div class="zh" markdown="1">

**根因**：**一对多虚拟化没有资源硬隔离**（命运共享的典型表现）。

</div>

**What should have been done**:
- Set session, throughput and new-connection-rate limits per context
- Put critical tenants on separate physical firewalls (group by service class)
- Monitor per-context sessions, CPU and new-connection rate, with thresholds and alerts
- Rate-limit "short-connection storm" workloads upstream (load balancer / proxy)

<div class="zh" markdown="1">

**正确做法**：
- 每上下文设置会话数/吞吐/新建速率上限
- 关键租户与普通租户分不同物理防火墙（按等级分组）
- 监控每上下文的会话数、CPU、新建速率，设阈值告警
- 对"短连接风暴"类业务做前置限速（LB/代理）

</div>

### 🔥 Case 12: The Service Chain Only Had a Forward Arrow — the File Server "Logs In But Will Not Download" · 🔥 案例十二：服务链只画了去程，文件服务器"能登录不能下载"

**Symptom**: against a protected file server users can log in and browse directories, but large downloads break at about 90%. Access from the operations subnet to the same server works fine.

<div class="zh" markdown="1">

**现象**：访问受保护的文件服务器：能登录、能看目录，下载大文件到 90% 就断；同一服务器从运维网段访问正常。

</div>

**Investigation**: PBR steers user→server traffic through the vFW, while the return path follows the server's default gateway straight back to the core (**asymmetric**). The vFW only sees one direction, and sessions time out and drop packets. Small files finish before the timeout, so everything "looks fine".

<div class="zh" markdown="1">

**排查**：策略路由把用户 → 服务器的流量引到 vFW，回程则由服务器的默认网关直接回核心（**非对称**）。vFW 只看到单向流，会话超时后丢包；小文件在超时前完成所以"正常"。

</div>

**Root cause**: **the return path was never designed** — truth 13 in the flesh.

<div class="zh" markdown="1">

**根因**：**回程路径未设计**（第 13 条反直觉认知的实景）。

</div>

**What should have been done**:
- Put the service node on the VRF's only exit (topology forces symmetry), or steer both directions with VASI/PBR
- Enable TCP state loosening on the vFW (a temporary mitigation only — it does not replace the design)
- Keep the MTU/MSS consistent on both sides of the service node
- Acceptance cases must include "large file transfer + long-lived connection"

<div class="zh" markdown="1">

**正确做法**：
- 服务节点放在 VRF 唯一出口上（拓扑强制对称），或用 VASI/PBR 双向引流
- vFW 开 TCP 状态宽松模式（仅作临时缓解，不替代设计）
- 服务节点两侧 MTU/MSS 一致
- 验收用例必须包含"大文件传输 + 长连接"

</div>

### 🔥 Case 13: PoE Budget Calculated at af — Half the APs Reboot Repeatedly · 🔥 案例十三：PoE 预算按 af 算，一半 AP 反复重启

**Symptom**: 40 new Wi-Fi 6 APs are installed and 18 of them reboot repeatedly. The switch log shows `power denied` / `insufficient power`.

<div class="zh" markdown="1">

**现象**：新装 40 个 Wi-Fi 6 AP，其中 18 个反复重启，交换机日志 `power denied` / `insufficient power`。

</div>

**Investigation**: the power supply was sized at 802.3af (15.4 W) × 48 ports = 740 W. The APs actually negotiate 802.3at (30 W), so 40 × 30 = 1,200 W, greater than the supply capacity.

<div class="zh" markdown="1">

**排查**：设计时按 802.3af（15.4 W）× 48 口 = 740 W 选电源；实际 AP 协商 802.3at（30 W），40 × 30 = 1,200 W > 电源容量。

</div>

**Root cause**: **the PoE budget used the "standard minimum" instead of the device's actual consumption**.

<div class="zh" markdown="1">

**根因**：**PoE 预算用"标准最小值"而不是"设备实际功耗"**。

</div>

**What should have been done**:
- Budget against the AP model's **maximum power** (all radios on 2.4/5/6 GHz plus cold-start margin)
- Choose dual or high-capacity power supplies with 20% headroom
- Enable PoE priority in critical areas (APs draw power before phones)
- Verify actual allocation with `show power inline` before go-live

<div class="zh" markdown="1">

**正确做法**：
- 预算按 AP 型号的**最大功耗**（含 2.4/5/6 GHz 全开 + 寒冷启动余量）
- 交换机选双电源/大功率电源，并留 20% 余量
- 关键区域开 PoE 优先级（让 AP 优先于话机取电）
- 上线前用 `show power inline` 核对实际分配

</div>

### 🔥 Case 14: Wireless Roaming Across Controllers — Voice Drops 3 Seconds on Every Floor Change · 🔥 案例十四：无线漫游跨控制器，语音每次换楼层掉 3 秒

**Symptom**: an employee on a Wi-Fi call walking from the 3rd to the 4th floor (different controller, different subnet) always loses the call for about 3 seconds.

<div class="zh" markdown="1">

**现象**：员工用 Wi-Fi 打电话，从 3 楼走到 4 楼（不同控制器/不同子网）必掉线约 3 秒。

</div>

**Investigation**: floors 3 and 4 belong to different AP groups, subnets and controllers. 802.11r (fast roaming) and OKC are not enabled, and this is **L3 roaming** (across subnets), requiring a new DHCP lease and a new security tunnel.

<div class="zh" markdown="1">

**排查**：3 楼与 4 楼属不同 AP 组、不同子网、不同控制器；未启用 802.11r（快速漫游）与 OKC，且为**L3 漫游**（跨子网），需要重新 DHCP + 重建安全隧道。

</div>

**Root cause**: **the conflict between roaming-domain design and voice requirements was never solved at the architecture level** (truth 14).

<div class="zh" markdown="1">

**根因**：**漫游域设计与语音要求的矛盾没有在架构层解决**（第 14 条反直觉认知）。

</div>

**What should have been done**:
- Separate the voice SSID from the data SSID; give the voice SSID **a single L2 roaming domain** (same subnet / same controller group)
- Enable 802.11r/k/v plus fast keys (CCKM/OKC) and measure the handover with a test instrument
- Or adopt a fabric/centralised-anchoring design so policy and gateway location are decoupled from roaming
- Write the acceptance criteria down: voice roaming interruption <100 ms, packet loss <1%

<div class="zh" markdown="1">

**正确做法**：
- 语音 SSID 与数据 SSID 分离；语音 SSID 用**单一 L2 漫游域**（同子网/同控制器组）
- 启用 802.11r/k/v + 快速密钥（CCKM/OKC），并用仪表测切换时延
- 或采用 fabric/集中锚定方案，让策略与网关位置与漫游解耦
- 验收标准写死：语音漫游中断 <100 ms、丢包 <1%

</div>

---

## Design Trade-offs · 设计取舍

| Trade-off | Choose A and you get | Choose B and you get | How CCDE decides |
|---|---|---|---|
| **A: three-tier / B: two-tier collapsed** | Scalability, fault isolation, clean blocks | Lower cost, fewer hops, simplicity | Number of functional blocks (>3 → A) and growth plans |
| **A: multitier STP / B: routed access** | Compatible with the installed base, no L3 access needed | No STP, fast convergence, small failure domain | Is there a cross-closet L2 requirement; team IGP skills |
| **A: routed access / B: switch clustering** | Smallest broadcast domain, no control-plane coupling | L2 requirements met, fastest convergence, simplest ops | **Cross-closet Layer 2** is the dividing line |
| **A: vPC / B: VSS/StackWise** | Independent control planes, separate upgrades | Simplest management, one configuration | Change windows and tolerance for upgrade risk |
| **A: EIGRP / B: OSPF** | Hierarchical flexibility, fast convergence (when configured well) | Multi-vendor, standards, natural area isolation | Team skills and vendor strategy |
| **A: summarise / B: specifics** | Small routing table, changes hidden | No suboptimality, failures visible | Is the suboptimality acceptable (latency sensitive → B) |
| **A: large L2 domain / B: subnet per building** | No gateway change when moving, simple | Small broadcast domain, small failure domain | Wireless roaming domain needs vs stability |
| **A: end-to-end VLAN+VRF / B: MPLS VPN** | Simple, no advanced skills needed | Scales to multi-tenant, clean paths | Number of isolation domains and team capability |
| **A: GRE / B: mGRE** | Point-to-point, controllable | Tunnel count O(n) instead of O(n²) | Site count and topology shape |
| **A: centralised gateway / B: distributed (routed access)** | Policy centralised, fewer addresses | Optimal forwarding, small failure domain | East-west traffic share and backbone bandwidth |
| **A: physically separate / B: VRF isolation** | Easiest compliance evidence | Lower cost, faster provisioning | Does compliance explicitly demand physical separation |
| **A: virtual firewall contexts / B: separate physical firewalls** | Lower CAPEX, unified management | Hard resource isolation, independent failure domains | How different are the tenant classes |
| **A: VASI / B: external firewall** | Fewer devices, fewer hops | Stateful inspection/IPS/audit | Do you need L7 capability and audit evidence |
| **A: NFV / B: dedicated hardware** | Elastic, fast provisioning, lower TCO | Deterministic performance, simple troubleshooting | Is throughput constrained by CPU / crypto offload |
| **A: fabric (VXLAN/EVPN) / B: traditional campus** | Policy follows the user, automated scale-out | Low operational bar, intuitive troubleshooting | Do you need large-scale policy and automation |
| **A: self-built wireless anchoring / B: local forwarding** | Traffic centralised, unified policy | Low latency, saves backhaul bandwidth | Branch bandwidth and central exit capacity |
| **A: scale by template / B: case by case** | Linear increments, predictable | Locally optimal | **A is what scalability means** |

<div class="zh" markdown="1">

| 取舍 | 选 A 得到 | 选 B 得到 | CCDE 判断依据 |
|------|----------|----------|--------------|
| **A: 三层模型 / B: 二层 collapse** | 扩展性、故障隔离、块间清晰 | 低成本、少跳数、简单 | 功能块数量（>3 选 A）与未来扩张计划 |
| **A: 多层 STP / B: 路由接入** | 兼容存量、无需 L3 接入 | 无 STP、快收敛、故障域小 | 是否有跨配线间二层需求；团队 IGP 能力 |
| **A: 路由接入 / B: 交换机集群** | 广播域最小、无控制面耦合 | L2 需求可满足、收敛最快、运维最简 | **跨配线间二层**是分水岭 |
| **A: vPC / B: VSS/StackWise** | 控制面独立、可单独升级 | 管理最简、配置一份 | 变更窗口与升级风险承受度 |
| **A: EIGRP / B: OSPF** | 层级灵活、收敛快（配置得当时） | 多厂商、标准、区域天然隔离 | 团队技能与厂商策略 |
| **A: 汇总 / B: 明细** | 路由表小、变化被遮挡 | 无次优、故障可见 | 汇总的次优是否可接受（时延敏感则 B） |
| **A: 大二层 / B: 按楼拆子网** | 移动不变网关、简单 | 广播域小、故障域小 | 无线漫游域需求 vs 稳定性 |
| **A: 端到端 VLAN+VRF / B: MPLS VPN** | 简单、无需高级技能 | 可扩展到多租户、路径清晰 | 隔离域数量与团队能力 |
| **A: GRE / B: mGRE** | 点对点可控 | 隧道数 O(n) 而非 O(n²) | 站点规模与拓扑形态 |
| **A: 集中式网关 / B: 分布式网关（路由接入）** | 策略集中、地址省 | 转发最优、故障域小 | 东西向流量占比与骨干带宽 |
| **A: 独立物理隔离 / B: VRF 隔离** | 合规最容易证明 | 成本低、开通快 | 合规要求是否明确要求物理隔离 |
| **A: 虚拟防火墙多上下文 / B: 独立物理防火墙** | 降 CAPEX、管理统一 | 资源硬隔离、故障域独立 | 租户等级差异是否悬殊 |
| **A: VASI / B: 外部防火墙** | 省设备、省跳数 | 状态检测/IPS/审计 | 是否需要 L7 能力与审计证据 |
| **A: NFV / B: 专用硬件** | 弹性、快速开通、降 TCO | 确定性性能、简单排障 | 吞吐是否受 CPU/加密卸载约束 |
| **A: fabric（VXLAN/EVPN） / B: 传统园区** | 策略随人走、自动化扩展 | 运维门槛低、排障直观 | 是否需要大规模策略与自动化 |
| **A: 自建无线锚定 / B: 本地转发** | 流量集中、策略统一 | 时延低、出口带宽省 | 分支带宽与集中出口容量 |
| **A: 按模板扩容 / B: 一事一议** | 线性增量、可预测 | 局部最优 | **可扩展性的本质就是 A** |

</div>

> 💡 **A universal criterion**: **"is the cost of this choice paid at change time or at failure time?"** Campus design should push cost into "controllable change time" (adding devices, editing configuration, expanding capacity) rather than "uncontrollable failure time" (loops, broadcast storms, dual-active).

<div class="zh" markdown="1">

> 💡 **一条通用判据**：**"这个选择的代价，是发生在变更时还是发生在故障时？"** 园区设计应尽量把代价放在"可控的变更时"（加设备、改配置、扩容量），而不是"不可控的故障时"（环路、广播风暴、双主）。

</div>

---

## Design Pitfalls · 设计缺陷

| # | Pitfall | Consequence | Avoidance |
|---|---|---|---|
| 1 | A two-tier model carrying >3 functional blocks | One core failure takes down the whole network; SVI count runs away | Split the core once you exceed 3 blocks |
| 2 | Core layer doing ACL/NAT/service insertion | Change risk becomes network-wide; performance jitter | Core does high-speed forwarding only |
| 3 | STP root and FHRP active on opposite sides | Triangular detour, inter-switch link saturates | Force them onto the same side + periodic audit |
| 4 | Tuning FHRP timers but ignoring uplink failure | A "live dead gateway" black hole | track + IP SLA/BFD |
| 5 | Routed access but gateways still on distribution | STP dependency unchanged; wasted effort | Move the gateway down to access |
| 6 | Routed-access uplinks all /30 | Address exhaustion, hard to summarise | /31 or a dedicated interconnect pool kept out of service summaries |
| 7 | No EIGRP stub on access | Query flooding + SIA, minutes to converge | stub + summarisation + filtering |
| 8 | Several ABRs summarising the same prefix | Detours after a failure (suboptimal) | Summarise on one ABR, or steer with cost |
| 9 | peer-keepalive on the same path as peer-link | Dual-active, IP conflicts, broadcast storms | keepalive over a dedicated management path |
| 10 | Sizing stacks/clusters as "two devices" | After one failure, capacity halves and overloads | Design for N−1 capacity |
| 11 | One VLAN across buildings with >500 endpoints | Broadcast/ARP storms, huge failure domain | Subnet per building + Storm Control |
| 12 | End-to-end VLAN+VRF consistency by hand | Probabilistic black holes, guesswork troubleshooting | Templates + automated checks + hop-by-hop matrix |
| 13 | Treating a VRF as a firewall | Compliance failure, lateral reachability | Policy from ACLs/firewalls/micro-segmentation |
| 14 | `permit all` in the fusion router import | Isolation exists only on paper | Explicit allow list + default deny |
| 15 | No per-context resource limits on the virtual firewall | One tenant saturates everything | Limits + tiered deployment + monitoring |
| 16 | Service chain designed with only a forward arrow | Large files and long connections fail | Symmetric steering (VASI/PBR/topology) |
| 17 | Tunnels without MSS adjustment, ICMP blocked by policy | Large-packet black hole, HTTPS hangs | adjust-mss + permit the key ICMP types |
| 18 | PoE budget at the af minimum | APs reboot repeatedly, cryptic logs | Maximum device power + 20% headroom |
| 19 | Roaming domain conflicting with voice requirements | 3 s drop on every cross-area move | Separate voice roaming domain + 11r/k/v |
| 20 | Claiming high availability without failure drills | Recovery happens in the wrong order during a real fault | Acceptance case table + power-pull drills |

<div class="zh" markdown="1">

| # | 缺陷 | 后果 | 规避 |
|---|------|------|------|
| 1 | 二层模型承载 >3 个功能块 | 一次核心故障全网中断，SVI 数量失控 | 超过 3 块就拆核心层 |
| 2 | 核心层做 ACL/NAT/服务插入 | 变更风险全网化、性能抖动 | 核心只做高速转发 |
| 3 | STP 根与 FHRP Active 不同侧 | 三角绕行、串联链路打满 | 强制同侧 + 定期审计 |
| 4 | 只调 FHRP 定时器不解决上行失效 | "活着的死网关"长期黑洞 | track + IP SLA/BFD |
| 5 | 路由接入但网关仍在分布层 | STP 依赖照旧，白折腾 | 网关必须下移到接入层 |
| 6 | 路由接入上行全用 /30 | 地址快速耗尽、汇总困难 | /31 或统一互联池且不汇总进业务 |
| 7 | 接入层不配 EIGRP stub | 查询泛洪 + SIA，收敛分钟级 | stub + 汇总 + 过滤 |
| 8 | 多个 ABR 同时汇总同一前缀 | 故障后流量绕行（次优） | 单 ABR 汇总或用 cost 引导 |
| 9 | peer-keepalive 与 peer-link 同路径 | 双主、IP 冲突、广播风暴 | keepalive 走独立管理路径 |
| 10 | 堆叠/集群按"两台设备"做容量规划 | 单台故障后容量减半即过载 | 按 N−1 容量设计 |
| 11 | 单 VLAN 跨多楼且终端 >500 | 广播/ARP 风暴、故障域巨大 | 按楼拆子网 + Storm Control |
| 12 | 端到端 VLAN+VRF 靠人工保证一致性 | 概率性不通、排障靠猜 | 模板 + 自动化校验 + 逐跳矩阵 |
| 13 | VRF 当防火墙用 | 合规失效、横向可达 | 策略由 ACL/防火墙/微分段提供 |
| 14 | fusion router 导入 `permit all` | 隔离名存实亡 | 显式允许清单 + 默认拒绝 |
| 15 | 虚拟防火墙不设上下文资源限额 | 一租户打满，全租户受害 | 限额 + 分级部署 + 监控 |
| 16 | 服务链只设计去程 | 大文件/长连接失败 | 对称引流（VASI/PBR/拓扑强制） |
| 17 | 隧道不调 MSS、策略拦 ICMP | 大包黑洞、HTTPS 卡死 | adjust-mss + 放行 ICMP 关键类型 |
| 18 | PoE 按 af 最小值预算 | AP 反复重启、日志难懂 | 按设备最大功耗 + 20% 余量 |
| 19 | 无线漫游域与语音要求矛盾 | 每次跨区掉线 3 s | 语音 SSID 独立漫游域 + 11r/k/v |
| 20 | 未做故障演练就宣称高可用 | 真故障时按错误顺序恢复 | 验收用例表 + 拔电演练 |

</div>

---

## Key Terms · 本章关键术语

### Architecture and Models · 架构与模型

| Term | Meaning |
|---|---|
| Three-Tier Model | Core / distribution / access separated into three layers |
| Two-Tier Model / Collapsed Core | Core and distribution collapsed into one layer |
| Functional Distribution Block | A block that owns its own distribution layer |
| Access–Distribution Model | The way access connects to distribution |
| Multitier STP Based | Layer 2 extends to the distribution layer, STP provides redundancy |
| Routed Access | Layer 3 gateway at the access layer |
| Switch Clustering | Several switches presented as one logical switch |
| mLAG | Multi-chassis link aggregation (cross-device port-channel) |
| Gold Plating | Over-design beyond the stated requirements |
| Fate Sharing | Sharing the underlay means sharing the failures |
| Many-to-One / One-to-Many | Many physical presented as one / one physical split into many |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| Three-Tier Model | 三层模型（核心/分布/接入） |
| Two-Tier Model / Collapsed Core | 二层模型（核心与分布合一） |
| Functional Distribution Block | 功能分布块（拥有自己分布层的块） |
| Access–Distribution Model | 接入—分布设计模型 |
| Multitier STP Based | 多层 STP 模型（L2 到分布层） |
| Routed Access | 路由接入（L3 网关在接入层） |
| Switch Clustering | 交换机集群（多台呈现为一台） |
| mLAG | 跨设备链路聚合 |
| Gold Plating | 过度设计（超出需求的设计） |
| Fate Sharing | 命运共享（共享底层即共享故障） |
| Many-to-One / One-to-Many | 多对一 / 一对多虚拟化 |

</div>

### Layer 2 and First Hop · 二层与首跳

| Term | Meaning |
|---|---|
| STP / RSTP / MSTP | Spanning Tree / Rapid STP / Multiple STP |
| Root Guard / BPDU Guard / Loop Guard | Root, BPDU and loop protection features |
| UDLD | Unidirectional Link Detection (one-way fibre protection) |
| Storm Control | Broadcast / multicast / unknown-unicast suppression |
| FHRP / HSRP / VRRP | First Hop Redundancy Protocol family |
| vPC / VSS / StackWise | Virtual PortChannel / Virtual Switching System / stacking |
| peer-link / peer-keepalive | vPC peer link / peer keepalive path |
| Orphan Port | A port attached to only one vPC member |
| Dual-Active | Cluster split, both halves active |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| STP / RSTP / MSTP | 生成树 / 快速生成树 / 多实例生成树 |
| Root Guard / BPDU Guard / Loop Guard | 根保护 / BPDU 保护 / 环路保护 |
| UDLD | 单向链路检测（光纤单通防护） |
| Storm Control | 广播/组播/未知单播风暴抑制 |
| FHRP / HSRP / VRRP | 首跳冗余协议 / 热备路由协议 / 虚拟路由冗余协议 |
| vPC / VSS / StackWise | 虚拟端口通道 / 虚拟交换系统 / 堆叠技术 |
| peer-link / peer-keepalive | vPC 对等链路 / 对等保活链路 |
| Orphan Port | 仅归属单台 vPC 成员的端口 |
| Dual-Active | 双主（集群分裂） |

</div>

### Layer 3 and Routing · 三层与路由

| Term | Meaning |
|---|---|
| EIGRP / DUAL | Enhanced IGP / Diffusing Update Algorithm |
| Stub Routing | Stub router that does not forward queries |
| SIA (Stuck-in-Active) | EIGRP convergence timeout state |
| OSPF Area / ABR / ASBR | OSPF area / area border router / AS boundary router |
| Area Range / Summary-address | OSPF area summarisation / EIGRP summarisation |
| Stub / Totally-Stubby Area | Reduced-LSA OSPF area types |
| BFD | Bidirectional Forwarding Detection (millisecond failure detection) |
| ECMP | Equal-Cost Multi-Path |
| Route Summarization | Aggregation of prefixes (with a suboptimality cost) |
| IP SLA | Active probing used for tracking and switchover |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| EIGRP / DUAL | 增强内部网关路由协议 / 扩散更新算法 |
| Stub Routing | 末梢路由（不转发查询） |
| SIA (Stuck-in-Active) | 卡在活跃状态（EIGRP 收敛超时） |
| OSPF Area / ABR / ASBR | OSPF 区域 / 区域边界路由器 / 自治系统边界路由器 |
| Area Range / Summary-address | 区域汇总 / 汇总地址 |
| Stub / Totally-Stubby Area | 末梢 / 完全末梢区域 |
| BFD | 双向转发检测（毫秒级故障检测） |
| ECMP | 等价多路径 |
| Route Summarization | 路由汇总（同时带来次优代价） |
| IP SLA | 主动探测（用于 track 与切换） |

</div>

### Virtualisation and Services · 虚拟化与服务

| Term | Meaning |
|---|---|
| VRF / VRF-Lite | Virtual Routing and Forwarding instance / VRF without MPLS |
| RD / RT | Route Distinguisher / Route Target (controls MP-BGP import/export) |
| MP-BGP / VPNv4 | Multiprotocol BGP / VPN IPv4 address family |
| RR (Route Reflector) | Route reflector that removes the iBGP full mesh |
| GRE / mGRE / NHRP | Generic Routing Encapsulation / multipoint GRE / Next Hop Resolution Protocol |
| VXLAN / EVPN | Virtual Extensible LAN / Ethernet VPN (modern overlay) |
| VNI / VN | VXLAN Network Identifier / Virtual Network |
| Fusion Router | Device merging several VRFs to reach shared services |
| VRF-Aware NAT | Address translation that is aware of the VRF |
| VASI | VRF-Aware Services Infrastructure (intra-node VRF interconnect) |
| vFW / Context | Virtual firewall / firewall virtual context |
| NFV | Network Functions Virtualisation |
| Service Chaining / SFC | Service chaining / Service Function Chaining |
| SGT / SXP | Security Group Tag / Security Group Exchange Protocol (common in SDA) |
| SDA / LISP | Software-Defined Access / Locator-ID Separation Protocol |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| VRF / VRF-Lite | 虚拟路由转发实例 / 无 MPLS 的 VRF |
| RD / RT | 路由区分符 / 路由目标（MP-BGP 控制导入导出） |
| MP-BGP / VPNv4 | 多协议 BGP / VPN IPv4 地址族 |
| RR (Route Reflector) | 路由反射器 |
| GRE / mGRE / NHRP | 通用路由封装 / 多点 GRE / 下一跳解析协议 |
| VXLAN / EVPN | 虚拟可扩展局域网 / 以太网 VPN（现代覆盖） |
| VNI / VN | VXLAN 网络标识 / 虚拟网络 |
| Fusion Router | 融合路由器（合并多个 VRF 访问共享服务） |
| VRF-Aware NAT | 感知 VRF 的地址转换 |
| VASI | VRF 感知服务基础设施（节点内 VRF 互联） |
| vFW / Context | 虚拟防火墙 / 防火墙虚拟上下文 |
| NFV | 网络功能虚拟化 |
| Service Chaining / SFC | 服务链 / 服务功能链 |
| SGT / SXP | 安全组标记 / 安全组交换协议（SDA 常用） |
| SDA / LISP | 软件定义接入 / 位置与身份分离协议 |

</div>

---

## Field Notes · 实战经验总结

1. **Count the functional blocks first, then pick the model.** More than 3 blocks on a collapsed core is the most common — and most expensive — one-off mistake in campus design.
2. **The first deliverable of a campus design is not a topology diagram but a "failure-domain list"**: write down the blast radius of every failure point, or the review has nothing to hold on to.
3. **The L2/L3 boundary is a one-way decision.** It drives addressing, DHCP, policy and monitoring; changing it once means redoing the project once.
4. **"Layer 2 across closets" is the only genuine technical constraint.** Anyone rejecting routed access because "the team is not comfortable with routing" has an organisational problem that can be solved.
5. **Routed access has exactly one acceptance criterion**: no VLAN on access-layer devices may span devices. If that is not true, it is not routed access.
6. **STP root, FHRP active and IGP best exit must be on the same side.** This single rule removes the most common "detour-style slowness" in campuses.
7. **FHRP guarantees the address never disappears; it does not guarantee the service never stops.** Uplink failure needs track/IP SLA/BFD — "the device is alive" is not "the path is alive".
8. **peer-link and peer-keepalive must live in two different failure domains.** Almost every dual-active incident starts with "we saved one cable".
9. **Size clusters for N−1 capacity**: after one member fails, the survivors must still carry peak load, otherwise "high availability" just means "high-probability overload".
10. **EIGRP scalability equals query-scope control; OSPF scalability equals area and summarisation design.** The protocol is not slow; the design decides whether it is fast.
11. **Summarisation always brings suboptimality.** Write down the "acceptable suboptimality" instead of pretending summarisation is free.
12. **A campus IGP table above ten thousand routes is a signal**: something that should be summarised is not, or the BGP boundary is in the wrong place.
13. **Virtualisation adds nothing to availability; it only enlarges the blast radius.** Its precondition is that the physical layer is already solid.
14. **A VRF is routing isolation, not security isolation.** For compliance, the evidence is "policy devices + verification probes", never "we configured a VRF".
15. **Every inter-VRF leak point needs default deny plus explicit allow.** One `permit all` on a fusion router can erase a year of isolation design.
16. **Service virtualisation succeeds or fails on the return path.** A service chain whose design document has only a forward arrow will certainly deliver "ping works, application does not".
17. **One-to-many virtualisation must have resource limits** (sessions, throughput, new-connection rate), or one tenant can take down all of them.
18. **MTU is the hidden tax of overlay networks**: tunnels, service chains and encryption each take a cut; without `adjust-mss`, expect "large packets do not work".
19. **PoE and wireless are the two most commonly under-counted budgets in a campus.** They are not on the topology diagram, but they turn straight into user complaints.
20. **High availability that has never been rehearsed does not exist.** The "pull the power / cut the link / stop the service" cases in the acceptance table are the best value for effort in the entire design.

<div class="zh" markdown="1">

1. **先数功能块，再选模型**。功能块 >3 个却用 collapsed core，是所有园区设计里最常见、代价最高的一次性错误。
2. **园区设计的第一输出不是拓扑图，而是"故障域清单"**：每一处故障的影响半径写清楚，评审才有抓手。
3. **L2/L3 分界点是一次性决策**。它决定了地址规划、DHCP、策略、监控口径，改一次等于重做一次项目。
4. **"跨配线间二层"是唯一真正的技术约束**。凡是拿"团队不熟路由"当理由拒绝路由接入的，都是可以解决的组织问题。
5. **路由接入的验收标准只有一条**：接入层设备上不存在跨设备的同一 VLAN。做不到就是没做。
6. **STP 根、FHRP Active、IGP 最优出口必须同侧**。这一条能消灭园区里最常见的"绕行型缓慢"。
7. **FHRP 解决地址不消失，不解决业务不中断**。上行失效必须靠 track/IP SLA/BFD 感知，"设备活着"不等于"路径活着"。
8. **peer-link 与 peer-keepalive 必须是两个故障域**。双主事故几乎全部源于"省一根线"。
9. **集群按 N−1 容量设计**：单台故障后剩余设备仍要能扛住峰值，否则"高可用"只是"高概率过载"。
10. **EIGRP 的可扩展性等于查询范围控制**；**OSPF 的可扩展性等于区域与汇总设计**。协议本身不慢，设计才决定快慢。
11. **汇总永远伴随次优**。设计时要写清"允许的次优程度"，而不是假设汇总没有代价。
12. **园区 IGP 路由表超过万级就是信号**：该汇总的没汇总，或该画 BGP 边界的地方没画。
13. **虚拟化不给可用性加分，只放大故障半径**。虚拟化的前提是物理层已经够稳。
14. **VRF 是路由隔离，不是安全隔离**。合规场景一律以"策略设备 + 验证探测"作证据，不以"配了 VRF"作证据。
15. **任何 VRF 间泄漏点都要"默认拒绝 + 显式允许"**。fusion router 上的一条 `permit all` 能让整年的隔离设计归零。
16. **服务虚拟化的成败在回程**。设计文档里只有去程箭头的服务链，上线后一定出现"能 ping 不通业务"。
17. **一对多虚拟化必须做资源限额**（会话数、吞吐、新建速率），否则一个租户能拖垮所有租户。
18. **MTU 是覆盖网络的隐形税**：隧道、服务链、加密各收一笔，不 `adjust-mss` 就等着"大包不通"。
19. **PoE 与无线是园区里最容易被漏算的两笔账**，它们不在拓扑图上，但会直接变成用户投诉。
20. **没演练过的高可用等于不存在**。验收用例表里那些"拔电/断链/关服务"的用例，是整个设计里性价比最高的部分。

</div>

---

## Design Scenario Exercises (Campus Architecture, Three Problems) · 设计情景演练（园区架构类，三道）

> The trap in this question type is **mistaking "choosing a model" for "choosing a technology"** (agonising over vPC versus StackWise) while ignoring the three inputs that actually decide the answer: **failure domain + business constraints + team capability**. The correct analysis order is always: boundaries → tiers → boundary point → routing → isolation → capacity → validation.

<div class="zh" markdown="1">

> 本章题型的陷阱是：**把"选模型"当成"选技术"**（纠结 vPC 还是 StackWise），而忽略了"故障域 + 业务约束 + 团队能力"这三条真正决定答案的输入。正确的分析顺序永远是：边界 → 层次 → 分界点 → 路由 → 隔离 → 容量 → 验证。

</div>

### Scenario 1: Four Plants Merging, OT and IT Must Be Isolated, and the Budget Only Covers "One Campus" · 情景一：4 个厂区合并，OT 与 IT 必须隔离，预算只够"一个园区"的钱

**Background**: a manufacturing group where four plants each built their own network (6,000 endpoints plus 2,000 industrial control devices in total). The group requires a single campus architecture:
- **OT (industrial control) and IT must be logically isolated**, and OT must not reach the internet, only the group MES
- Production cannot stop: any change must be **rolled out plant by plant**, with ≤30 minutes of downtime per event
- Wireless demand is concentrated in office areas; the shop floor needs wireline plus a few AGV APs
- The budget is approved as "build one new campus", **with no MPLS line budget**
- The IT network team has 5 people, **none with MPLS/EVPN experience**, but they know OSPF

<div class="zh" markdown="1">

**背景**：制造业集团，原有 4 个厂区各自建网（共 6,000 终端 + 2,000 台工控设备）。集团要求合并为统一园区架构：
- **OT（工控）与 IT 必须逻辑隔离**，且 OT 不允许访问互联网，只允许访问集团 MES
- 生产不能停：任何改造必须**分厂区滚动进行**，单次停机 ≤30 分钟
- 无线需求集中在办公区；车间只做有线 + 少量 AGV AP
- 预算按"新建一个园区"批，**没有 MPLS 专线预算**
- IT 网络团队 5 人，**无人有 MPLS/EVPN 经验**，但有 OSPF 经验

</div>

**Question**: propose the target architecture (tiers and access model), the isolation technology choice and the migration order, and answer "should we go to fabric?".

<div class="zh" markdown="1">

**问题**：给出目标架构（层次与接入模型）、隔离技术选型、迁移顺序，并回答"要不要上 fabric"。

</div>

<details markdown="1">
<summary>Reference solution</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core thinking: solve 90% of the problem with "functional blocks + routed access + VRF-Lite", and explicitly rule out MPLS VPN and fabric — because budget and team capability are hard constraints, and neither technology's benefits apply in this scenario.**

<div class="zh" markdown="1">

**核心思路：用"功能块 + 路由接入 + VRF-Lite"解决 90% 的问题，把 MPLS VPN 与 fabric 明确排除 —— 因为预算与团队能力是硬约束，而这两项的收益在本场景里用不上。**

</div>

| Decision | Choice | Rationale |
|---|---|---|
| **Tier model** | Three-tier (each plant = one user block + one OT block, group core interconnects them) | 4 plants = more than 4 functional blocks, beyond the limit for a collapsed core |
| **Access model** | Office areas: **routed access** (gateway at access); shop floor: switch clustering (stacking) | Office areas need small failure domains and fast convergence; the shop floor has few closets and needs PoE plus industrial switch redundancy |
| **IGP** | OSPF (Area 0 backbone + one area per plant) | The team knows OSPF; areas map naturally onto plants |
| **Isolation technology** | **End-to-end VLAN + VRF-Lite** (one VRF each for IT and OT, i.e. 2 isolation domains) | Only two domains, so VLAN+VRF is enough; MPLS/fabric complexity buys nothing here |
| **OT boundary** | Firewall (with industrial protocol identification) plus one-way/allow-list policy | OT may only reach MES; every other direction is default deny |
| **Wireless** | Office: centralised forwarding (controller); shop-floor AGVs: local forwarding | Offices need unified policy; the shop floor needs low latency |

<div class="zh" markdown="1">

| 决策 | 选择 | 理由 |
|---|---|---|
| **层次模型** | 三层模型（每个厂区 = 一个用户块 + 一个 OT 块，集团核心互连） | 4 个厂区 = 4 个以上功能块，超过 collapsed core 适用上限 |
| **接入模型** | 办公区：**路由接入**（网关在接入层）；车间：交换机集群（堆叠） | 办公区需要小故障域与快收敛；车间配线间少、需 PoE 与工业交换机冗余 |
| **IGP** | OSPF（Area 0 骨干 + 每厂区一个区域） | 团队有 OSPF 经验；区域天然对应厂区 |
| **隔离技术** | **端到端 VLAN + VRF-Lite**（IT 与 OT 各一个 VRF，共 2 个隔离域） | 只有 2 个域，VLAN+VRF 足够；MPLS/fabric 的复杂度买不到收益 |
| **OT 边界** | 防火墙（含工业协议识别） + 单向/白名单策略 | OT 只允许访问 MES，默认拒绝所有其他方向 |
| **无线** | 办公区集中转发（控制器），车间 AGV 用本地转发 | 办公区需要统一策略；车间需要低时延 |

</div>

**Target architecture skeleton**:

<div class="zh" markdown="1">

**目标架构骨架**：

</div>

```
                  +------------ Group core (Area 0, 2 devices) ------------+
       +----------+----------+------------------+-----------------+
   Plant A distribution   Plant B distribution  Plant C         Plant D
   (Area 1)               (Area 2)              (Area 3)        (Area 4)
     +- IT block: routed access (one subnet per closet)
     +- OT block: stacked cluster + industrial firewall -> MES (only exit)
```

<div class="zh" markdown="1">

```
                  ┌──────────── 集团核心（Area 0，2 台）────────────┐
       ┌──────────┴──────────┬──────────────────┬─────────────────┐
   厂区 A 分布块           厂区 B 分布块        厂区 C 分布块      厂区 D 分布块
   （Area 1）              （Area 2）           （Area 3）         （Area 4）
     ├─ IT 块：路由接入（每配线间一子网）
     └─ OT 块：堆叠集群 + 工业防火墙 → MES（唯一出口）
```

</div>

**Migration order (4 weeks per plant, rolling)**:

<div class="zh" markdown="1">

**迁移顺序（每厂区 4 周，滚动）**：

</div>

| Week | Action | Downtime |
|---|---|---|
| 1 | Build the OSPF area and attach the distribution layer to the core; **service paths unchanged** | None (night window) |
| 2 | Build the OT VRF and firewall boundary; migrate OT devices VLAN by VLAN | ≤5 min per device |
| 3 | Switch office areas to routed access closet by closet (move gateways down + migrate DHCP scopes) | 20 min per closet (lunch or night) |
| 4 | Decommission the old STP domain, clean up VLANs, run acceptance (including power-pull drills) | None |

<div class="zh" markdown="1">

| 周 | 动作 | 停机 |
|---|---|---|
| 1 | 建 OSPF 区域、把分布层接入核心；**保持业务路径不变** | 无（夜间窗口） |
| 2 | 新建 OT VRF 与防火墙边界；OT 设备逐个迁移 VLAN | 每台 ≤5 min |
| 3 | 办公区按配线间切换为路由接入（网关下移 + DHCP scope 迁移） | 每配线间 20 min（午休/夜间） |
| 4 | 拆除旧 STP 域、清理 VLAN、验收（含拔电演练） | 无 |

</div>

**Key trade-off: why not fabric?**

<div class="zh" markdown="1">

**关键取舍：为什么不上 fabric？**

</div>

| Fabric benefit | Does it hold here |
|---|---|
| Policy follows the user (SGT) | No: the OT/IT boundary is a **fixed physical boundary**, not "people moving around" |
| Large-scale automated deployment | No: 4 plants, about 120 access switches, templated scripts are enough |
| Unified wired and wireless policy | Partly, but achievable with "separate VLAN + centralised forwarding" |
| **Cost** | Underlay planning + LISP/EVPN troubleshooting + team training (6–12 months) |
| **Conclusion** | **Benefit ≤ cost → not selected** |

<div class="zh" markdown="1">

| fabric 收益 | 本场景是否成立 |
|---|---|
| 策略随用户走（SGT） | 不需要：OT/IT 的边界是**固定物理边界**，不是"人到处走" |
| 大规模自动化部署 | 不需要：4 个厂区、约 120 台接入，模板化脚本足够 |
| 有线无线统一策略 | 部分成立，但可用"独立 VLAN + 集中转发"实现 |
| **代价** | underlay 规划 + LISP/EVPN 排障 + 团队培训（6–12 个月） |
| **结论** | **收益 ≤ 代价 → 不选** |

</div>

**The point most likely to be challenged**: why not physically separate OT (separate cabling)? — Because the path from the shop floor to MES must reuse the backbone fibre, and **physical separation means recabling at a cost far beyond the budget**; "VRF + industrial firewall + allow list" can satisfy compliance, provided you **keep the evidence that OT has no default route and only MES prefixes are reachable**.

<div class="zh" markdown="1">

**最容易被追问的一点**：OT 为什么不直接物理隔离（单独布线）？—— 因为车间到 MES 的路径必须复用主干光纤，**物理隔离需要重新布线，成本远超预算**；而"VRF + 工业防火墙 + 白名单"在合规上可以通过，前提是**保留"OT 侧无默认路由、仅 MES 前缀可达"的验证证据**。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 2: An Eight-Building University Campus — Cross-Building Layer 2, Poor Voice Roaming, and 3 Hours of Downtime per Change · 情景二：8 栋楼的大学校园，跨楼大二层 + 语音漫游差 + 一次改造要停 3 小时

**Background**: a university campus with 8 buildings, 12,000 endpoints and 1,800 APs. Current state: everything is Layer 2, with **one "teaching VLAN" spanning all 8 buildings (about 5,000 endpoints)**; voice runs over Wi-Fi (drops whenever the user walks between buildings); every network change costs the whole university 3 hours of downtime; and the laboratory building has a set of devices using **fixed IP addresses and fixed gateways** (which cannot change). The IT team has 8 people and knows OSPF.

<div class="zh" markdown="1">

**背景**：大学校园，8 栋楼、12,000 终端、1,800 个 AP。现状：全部二层，**一个"教学 VLAN"跨 8 栋楼（约 5,000 终端）**；语音用 Wi-Fi（跨楼走动必掉线）；每次网络改造要停 3 小时全校；实验楼有一批设备使用**固定 IP 与固定网关**（不能改）。IT 团队 8 人，熟悉 OSPF。

</div>

**Question**: propose the target architecture and migration strategy, explain how to reduce "cross-building Layer 2", and how to achieve "≤30 minutes of downtime per change".

<div class="zh" markdown="1">

**问题**：给出目标架构与迁移策略，说明"跨楼二层"如何收敛，以及如何满足"改造停机 ≤30 分钟"。

</div>

<details markdown="1">
<summary>Reference solution</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core thinking: reduce "cross-building Layer 2" from "the whole campus" to "the voice roaming domain + a laboratory island", and convert everything else to routed access; achiev downtime targets by building the new network in parallel and cutting over in batches, not by working overnight.**

<div class="zh" markdown="1">

**核心思路：把"跨楼二层"从"全校园"收敛到"语音漫游域 + 实验楼孤岛"，其余全部改为路由接入；停机时间靠"并行建新网 + 分批割接"而不是靠"夜间抢工"。**

</div>

| Requirement | Approach |
|---|---|
| Teaching endpoints (5,000) | Split into **one subnet per floor per building** (about 40 /24s), routed access, gateway at the access layer |
| Voice roaming | A separate **L2 roaming domain** for the voice SSID (spanning 8 buildings but carrying only voice endpoints, about 600) |
| Laboratory fixed IP/gateway devices | Keep as a **standalone Layer 2 island** (STP domain inside one building), SVI on that building's distribution switch, attached to OSPF with a static route |
| Wireless data | Local forwarding per building (FlexConnect / local WLC) to reduce central exit bandwidth and roaming dependency |
| IGP | Multi-area OSPF: Area 0 core, one area per building (8), the laboratory island as a special area |

<div class="zh" markdown="1">

| 需求 | 处理方式 |
|---|---|
| 教学终端（5,000） | 拆成 **每楼每层一个子网**（约 40 个 /24），路由接入，网关在接入层 |
| 语音漫游 | 语音 SSID 单独一个 **L2 漫游域**（跨 8 栋楼但只承载语音终端，约 600 个） |
| 实验楼固定 IP/网关设备 | 保留为**独立二层孤岛**（单楼内 STP 域），在该楼分布交换机上做 SVI，通过静态路由接入 OSPF |
| 无线数据 | 每楼本地转发（FlexConnect/WLC 本地），减少集中出口带宽与漫游依赖 |
| IGP | OSPF 多区域：核心 Area 0，每栋楼一个区域（8 个），实验楼孤岛作为特殊区域 |

</div>

**Why leave cross-building Layer 2 only for voice**:

<div class="zh" markdown="1">

**为什么"跨楼二层"只留给语音**：

</div>

| Option | Blast radius | Risk |
|---|---|---|
| One VLAN for the whole campus | Broadcasts/loops in any building affect 5,000 endpoints | High (the current problem) |
| **Voice on its own VLAN (600 endpoints)** | Loops affect the voice domain (contained) + needs wireless tuning | Medium (acceptable, because the voice domain is topologically simple with no PC access) |
| Split everything (voice on L3 roaming too) | Optimal, but needs controller support and endpoint cooperation | Low risk but a large amount of change |

<div class="zh" markdown="1">

| 方案 | 影响面 | 风险 |
|---|---|---|
| 全校园一个 VLAN | 任一楼的广播/环路影响全校 5,000 终端 | 高（现状问题） |
| **语音单独 VLAN（600 终端）** | 环路影响语音域（可控）+ 需无线侧优化 | 中（可接受，因为语音域拓扑简单、无 PC 接入） |
| 全拆（语音也 L3 漫游） | 最优，但需要无线控制器支持与终端配合 | 低但改造量大 |

</div>

> 🎯 What this shows is **the trade-off between failure-domain size and business value**: keeping a 600-endpoint Layer 2 domain for voice is far safer than sharing one with 5,000 endpoints, and it delivers results faster than splitting everything to L3 roaming.

<div class="zh" markdown="1">

> 🎯 这里体现的是**"故障域大小与业务价值的权衡"**：为语音保留 600 终端的大二层，比让 5,000 终端共用一个大二层安全得多，也比全拆 L3 漫游更快见效。

</div>

**How to achieve ≤30 minutes of downtime (the key part)**:

<div class="zh" markdown="1">

**停机 ≤30 分钟的实现方式（关键）**：

</div>

```
Phase 1 (no downtime): build a parallel core plus a new distribution pair per building (independent OSPF domain)
Phase 2 (batched): cut over 1-2 buildings per week -- repoint access uplinks from the old network in the building
                   Downtime per building = the building's uplink switch (10-20 min, lunch window)
Phase 3 (clean-up): the old network holds only a few buildings -> decommission in one go (during holidays)
```

<div class="zh" markdown="1">

```
第一阶段（不停机）：新建一套并行核心 + 每楼新增一对分布交换机（新网独立 OSPF 域）
第二阶段（分批）：每周割接 1–2 栋楼 —— 在楼内把接入交换机上行从旧网改到新网
                  单栋停机 = 该楼上行切换（10–20 min，午休窗口）
第三阶段（收尾）：旧网只剩少数楼 → 一次性下线（可在假期）
```

</div>

| Practice | Effect |
|---|---|
| Build in parallel rather than "rework in place" | The rollback for any cutover is "plug the uplink back into the old network" (seconds) |
| Cutover granularity = one building | Blast radius per event ≤1,500 endpoints |
| Templates and pre-generated config (VLAN/subnet/DHCP scope/OSPF interface) | On site you only "plug in and verify" |
| Pre-staged acceptance script per building (gateway ping, DNS, DHCP, wireless association) | Shortens the on-site decision loop |

<div class="zh" markdown="1">

| 做法 | 效果 |
|---|---|
| 并行建网，不做"原地改造" | 每次割接的回退动作 = 把上行插回旧网（秒级） |
| 割接颗粒度 = 一栋楼 | 单次影响面 ≤1,500 终端 |
| 配置模板 + 预生成（VLAN/子网/DHCP scope/OSPF 接口） | 割接现场只做"插线 + 验证" |
| 每栋楼预置验收脚本（网关 ping、DNS、DHCP、无线关联） | 缩短现场判断时间 |

</div>

**The point most likely to be challenged**: why not put voice on L3 roaming? — Because L3 roaming requires **controller or endpoint support for anchoring or fabric**, and this university's 1,800 APs span three hardware generations, so **in a mixed environment the failure rate of L3 roaming exceeds the benefit**. **When the constraints are clear, "a small, contained Layer 2 domain" is more professional than "a theoretically superior solution that will not land reliably".**

<div class="zh" markdown="1">

**最容易被追问的一点**：为什么语音不直接上 L3 漫游？—— 因为 L3 漫游要求**无线控制器/终端支持锚定或 fabric**，而该校 1,800 个 AP 跨 3 代硬件，**混插环境下 L3 漫游的失败率高于收益**。**在约束明确时，选择"小而可控的大二层"比"理论上更先进但落地不稳的方案"更专业。**

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 3: A Group Shared Service Centre — 12 Business Domains, Fully Overlapping Addresses, One Shared Exit · 情景三：集团共享服务中心，12 个业务域、地址全部重叠、出口要共享

**Background**: a group consolidates the IT of 12 subsidiaries into one shared service centre with 15,000 campus endpoints. Constraints:
- Each of the 12 business domains keeps **independent administrative authority** (each subsidiary runs its own policy)
- **All addresses overlap** (all 12 use 10.0.0.0/8)
- Shared resources: internet exit, DNS/NTP, centralised monitoring, shared file services
- Compliance: business domains **must not reach each other**, with auditable evidence
- Two pairs of high-end firewalls already exist (capable of virtualisation), and the core is 4 high-end switches
- The team has 20 people; **one has done MPLS VPN, the rest only know OSPF/VRF-Lite**

<div class="zh" markdown="1">

**背景**：集团把 12 家子公司的 IT 集中到一个共享服务中心，园区内 15,000 终端。约束：
- 12 个业务域各自保持**独立的管理权限**（各子公司自己管策略）
- **地址全部重叠**（12 家都用 10.0.0.0/8）
- 共享资源：互联网出口、DNS/NTP、集中监控、共享文件服务
- 合规要求：业务域之间**不得互访**，且要有可审计证据
- 已有 2 对高端防火墙（可虚拟化），核心为 4 台高端交换机
- 团队 20 人，**有 1 人做过 MPLS VPN，其余只有 OSPF/VRF-Lite 经验**

</div>

**Question**: propose the virtualisation and path-isolation design, the service access design, and "how to prove there is no mutual reachability".

<div class="zh" markdown="1">

**问题**：给出虚拟化与路径隔离方案、服务访问设计、以及"如何证明不互访"。

</div>

<details markdown="1">
<summary>Reference solution</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core thinking: carry the 12 VRFs over MPLS VPN (or EVPN), put virtual firewalls at the boundaries, restrict the fusion zone to the shared exit only, and prove isolation with probe evidence rather than configuration screenshots.**

<div class="zh" markdown="1">

**核心思路：用"MPLS VPN（或 EVPN）承载 12 个 VRF" + "虚拟防火墙做边界" + "fusion 区只做共享出口"，并用"探测证据"而不是"配置截图"来证明隔离。**

</div>

| Decision | Choice | Rationale |
|---|---|---|
| **Isolation technology** | **MPLS VPN (MP-BGP + RR)**, or EVPN as a substitute | 12 domains, overlapping addresses, and precise RT-based import/export control; end-to-end VLAN+VRF cannot support 12 domains with 4096 VLANs and hop-by-hop consistency |
| **Number of VRFs** | 12 business VRFs + 1 shared services VRF + 1 management VRF | One VRF per domain, with rule-based numbering and naming (subsidiary code) |
| **Overlapping addresses** | **Keep native addresses inside the VRF**; apply **VRF-Aware NAT** only when reaching shared services | Avoids global renumbering (extremely high cost and risk) |
| **Boundary policy** | One pair of virtual firewall contexts per domain (or shared contexts on a firewall) | Stateful inspection plus audit logs; contexts aligned with VRFs |
| **Shared service access** | A dedicated **shared services VRF** (DNS/NTP/monitoring/files), one-way "domain → shared" only | One-way access is the easiest model to audit |
| **Internet exit** | Two exit domains (production/guest); NAT pools allocated per domain and managed centrally | Pool exhaustion and overlap must be visible centrally |
| **Management plane** | Management VRF + out-of-band + jump hosts, with RBAC per subsidiary | "12 subsidiaries manage themselves" requires that authority can be partitioned |

<div class="zh" markdown="1">

| 决策 | 选择 | 理由 |
|---|---|---|
| **隔离技术** | **MPLS VPN（MP-BGP + RR）**，或 EVPN 替代 | 12 个域、重叠地址、需按 RT 精确控制导入导出；VLAN+VRF 端到端的 4096 VLAN 与逐跳一致性无法支撑 |
| **VRF 数量** | 12 业务 VRF + 1 共享服务 VRF + 1 管理 VRF | 域与 VRF 一一映射，编号与命名规则化（子公司代码） |
| **重叠地址处理** | **VRF 内保持原生地址**；仅在访问共享服务时做 **VRF-Aware NAT** | 避免全局重编址（成本与风险极高） |
| **边界策略** | 每域一对虚拟防火墙上下文（或共享防火墙的多上下文） | 状态检测 + 审计日志；上下文与 VRF 对齐 |
| **共享服务访问** | 独立 **共享服务 VRF**（DNS/NTP/监控/文件），只允许"域 → 共享"单向 | 单向访问是最容易审计的模型 |
| **互联网出口** | 2 个出口域（生产/访客），NAT 池按域分配并集中管理 | 池耗尽与重叠必须集中可见 |
| **管理面** | 管理 VRF + 带外 + 跳板机，按子公司做 RBAC | 12 家自管的前提是"权限可切分" |

</div>

**Logical view**:

<div class="zh" markdown="1">

**逻辑视图**：

</div>

```
        +------------ Shared services VRF (DNS/NTP/monitoring/files) ------------+
        |        ^ one-way entry only (domain -> shared)                          |
   +----+----+ +----+----+        ...        +----+----+
   | VRF-01  | | VRF-02  |                   | VRF-12  |   each domain: vFW context + NAT
   | 10.0.0/8| | 10.0.0/8|  (overlapping, mutually invisible) | 10.0.0/8|
   +----+----+ +----+----+                   +----+----+
        +-----------+--------- MPLS/EVPN core ------+
                                  |
                        +---------+---------+
                        | Exit VRF (prod/guest) | -> internet (NAT pools per domain)
                        +-------------------+
```

<div class="zh" markdown="1">

```
        ┌─────────── 共享服务 VRF（DNS/NTP/监控/文件）───────────┐
        │        ↑ 只允许单向进入（域 → 共享）                    │
   ┌────┴────┐ ┌────┴────┐        ...        ┌────┴────┐
   │ VRF-01  │ │ VRF-02  │                   │ VRF-12  │   每域：vFW 上下文 + NAT
   │ 10.0.0/8│ │ 10.0.0/8│  （地址重叠，互不可见）│ 10.0.0/8│
   └────┬────┘ └────┬────┘                   └────┬────┘
        └───────────┴──────── MPLS/EVPN 核心 ──────┘
                                  │
                        ┌─────────┴─────────┐
                        │ 出口 VRF（生产/访客）│ → 互联网（NAT 池按域）
                        └───────────────────┘
```

</div>

**How to prove "no mutual reachability" (the compliance evidence chain)**:

<div class="zh" markdown="1">

**如何证明"不互访"（合规证据链）**：

</div>

| Evidence type | How | Audit value |
|---|---|---|
| **Design evidence** | RT import/export matrix (12×12, all explicitly "deny") plus change records | Shows design intent |
| **Configuration evidence** | Automated export of every PE's VRF/RT/import-map, compared against a baseline | Shows it has not been tampered with |
| **Active probing** | A probe agent per domain periodically sends TCP/UDP/ICMP to the probe addresses of the other 11 domains; all must fail | **Most persuasive** |
| **Traffic evidence** | NetFlow/telemetry measuring "cross-domain traffic" per VRF should be 0 (shared services excepted) | Shows no runtime leakage |
| **Log evidence** | Firewall context deny logs retained for 180 days, sampled for audit | Meets retention requirements |

<div class="zh" markdown="1">

| 证据类型 | 具体做法 | 审计价值 |
|---|---|---|
| **设计证据** | RT 导入导出矩阵表（12×12，明确全为"禁止"）+ 变更记录 | 证明设计意图 |
| **配置证据** | 自动化导出每台 PE 的 VRF/RT/import-map 并与基线比对 | 证明未被篡改 |
| **主动探测** | 每个域部署探测 Agent，周期性向其他 11 个域的"探针地址"发起 TCP/UDP/ICMP，结果全为失败 | **最有说服力** |
| **流量证据** | NetFlow/遥测按 VRF 维度统计"跨域流量"应为 0（除共享服务） | 证明运行时无泄漏 |
| **日志证据** | 防火墙上下文拒绝日志留存 180 天，抽样审计 | 满足合规留存 |

</div>

> 🎯 **In one sentence**: **the proof of isolation is not "we configured VRFs", it is "every quarter we run 132 probes and prove they do not pass".**

<div class="zh" markdown="1">

> 🎯 **一句话**：**隔离的证明不是"我们配了 VRF"，而是"我们每季度用 132 条探测证明它不通"。**

</div>

**The point most likely to be challenged**: why not 12 separate physical networks? — Because 12 physical networks mean 12× the devices, racks, power, fibre and staff, and **the CAPEX and OPEX would exceed every benefit of consolidation**; MPLS/EVPN isolation, with the double safety of the control plane (RT) and the policy plane (vFW), can achieve equivalent compliance. **The precondition is that the team has at least one person who can troubleshoot MPLS/EVPN independently** — which is exactly why this must be written into "risks and open items".

<div class="zh" markdown="1">

**最容易被追问的一点**：为什么不用 12 套物理网络？—— 因为 12 套物理网络意味着 12 倍的设备、机柜、电力、光纤与人力，**CAPEX 与 OPEX 会超出集中化的全部收益**；而 MPLS/EVPN 的隔离在"控制面（RT）+ 策略面（vFW）"双保险下，可以达到同等合规效果。**前提是团队至少有一名能独立排障 MPLS/EVPN 的人** —— 这也是本场景必须写进"风险与未决项"的一条。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

---

## Scenario Analysis Framework: The Standard Route for Campus Architecture Scenarios · 情景分析框架：园区架构类场景的通用套路

```
1 Count the "blocks" before talking about "tiers"
   Functional block list (user/DC/WAN/DMZ/management/OT/guest) -> the count decides three-tier vs two-tier
2 Find the "cross-closet Layer 2" requirement; it decides the access model
   None -> routed access (first choice); Some -> clustering / overlay / keep an island (and state why)
3 Fix the L2/L3 boundary, and update the addressing plan at the same time
   Boundary = gateway location = subnet edge = DHCP scope edge = failure-domain edge
4 Choose the IGP, and immediately answer "how are queries/areas controlled, where is summarisation done"
   EIGRP: stub + summarisation; OSPF: areas + single-point summarisation + acceptable suboptimality
5 Decide whether to virtualise (and to what granularity)
   VLAN+ACL is enough -> do not virtualise; overlapping addresses/multi-tenant -> VRF + RT matrix
6 Design service access and "the return path"
   Service node location, forward/reverse arrows, NAT pools, bypass escape, MTU/MSS
7 Do the capacity and budget arithmetic: ports/bandwidth/PoE/racks/routing table/VLANs/convergence
8 Provide acceptance and evidence: fault injection cases + isolation probes + measured summarisation suboptimality
9 Write down open items and assumptions: team skills, budget, compliance, endpoint constraints
```

<div class="zh" markdown="1">

```
① 先数"块"，再谈"层"
   功能块清单（用户/DC/WAN/DMZ/管理/OT/访客）→ 数量决定三层还是二层
② 找"跨配线间二层"需求，它决定接入模型
   无 → 路由接入（首选）；有 → 集群 / 覆盖 / 保留孤岛（并写明理由）
③ 定 L2/L3 分界点，并同步地址规划
   分界点 = 网关位置 = 子网边界 = DHCP scope 边界 = 故障域边界
④ 选 IGP，并立即回答"查询/区域怎么控、汇总在哪做"
   EIGRP: stub + 汇总；OSPF: 区域 + 单点汇总 + 次优可接受度
⑤ 决定要不要虚拟化（以及到什么粒度）
   只用 VLAN+ACL 能解决 → 不虚拟化；重叠地址/多租户 → VRF + RT 矩阵
⑥ 设计服务访问与"回程"
   服务节点位置、去程/回程箭头、NAT 池、bypass 逃生、MTU/MSS
⑦ 算容量与预算：端口/带宽/PoE/机柜/路由表/VLAN/收敛
⑧ 给验收与证据：故障注入用例 + 隔离探测 + 汇总次优实测
⑨ 写未决项与假设：团队技能、预算、合规要求、终端约束
```

</div>

**In one sentence**: **the campus architecture question does not test whether you can configure vPC/OSPF; it tests whether you can derive the one self-consistent failure-domain structure from business and constraints, and prove that it works.**

<div class="zh" markdown="1">

**一句话总结**：**园区架构题考的不是"你会不会配 vPC/OSPF"，而是"你能不能从业务与约束中推导出唯一自洽的故障域结构，并证明它有效"。**

</div>

---

## Chapter Summary · 本章小结

Campus design looks like choosing models (three-tier/two-tier, STP/routed access/clustering); in reality it is **designing the boundaries and the cost of failure domains**:

<div class="zh" markdown="1">

园区设计表面上在选模型（三层/二层、STP/路由接入/集群），本质上在**设计故障域的边界与代价**：

</div>

| Topic | Essence | Three questions you must answer | Test of success |
|---|---|---|---|
| **Hierarchy model** | Confine "change" to a small constant number of devices | How many functional blocks? Is a core genuinely necessary? | Adding a building needs template changes only |
| **Access model** | Choose failure behaviour, not bandwidth | Is there cross-closet Layer 2? Where is the gateway? | Single link/device failure <1 s with no loop risk |
| **Routing design** | Trade summarisation and areas for "change does not spread" | How are queries/areas controlled? Is the summarisation suboptimality acceptable? | Campus IGP stable in the thousands, no SIA |
| **Virtualisation** | Trade physical sharing for isolation, paying with fate sharing | Is the isolation value greater than the operational cost? Where are the leak points? | Probes prove no reachability, and resources are capped |
| **Service virtualisation** | Let many paths share one set of services and still come back | Where is the service node? How does the return path go? | Large files and long connections all pass |

<div class="zh" markdown="1">

| 主题 | 本质 | 三个必答问题 | 成败判据 |
|---|---|---|---|
| **分层模型** | 把"变化"限制在小常数设备内 | 有几个功能块？核心是否真的必要？ | 新增一栋楼只需模板化变更 |
| **接入模型** | 选择故障时的行为，而非带宽 | 有跨配线间二层吗？网关在哪？ | 单链路/单设备故障 <1 s 且无环路风险 |
| **路由设计** | 用汇总与区域换取"变化不扩散" | 查询/区域怎么控？汇总的次优可接受吗？ | 园区 IGP 稳定在千级、无 SIA |
| **虚拟化** | 用物理共享换隔离，代价是命运共享 | 隔离价值 > 运维成本吗？泄漏点在哪？ | 探测证明不互访，且资源有限额 |
| **服务虚拟化** | 让多条路径共用一套服务且能回来 | 服务节点在哪？回程怎么走？ | 大文件/长连接全部通过 |

</div>

**Four judgements that run through the whole chapter**:

<div class="zh" markdown="1">

**四条贯穿全章的判断**：

</div>

1. **Architecture determines failure behaviour**; a protocol only determines how fast recovery happens. Choose the wrong architecture and no protocol will save you.
2. **The L2/L3 boundary is a one-way decision**; it locks in addressing, policy, monitoring and operating model at the same time.
3. **Virtualisation enlarges the blast radius**, so it must rest on "the physical layer is already solid", not replace it.
4. **High availability and isolation without evidence are not finished**: power-pull drills, probe matrices and measured summarisation suboptimality are the last mile of design.

<div class="zh" markdown="1">

1. **架构决定故障行为**，协议只决定故障恢复的速度。选错架构，再好的协议也救不回来。
2. **L2/L3 分界点是一次性决策**，它同时锁定地址、策略、监控与运维方式。
3. **虚拟化放大故障半径**，所以它必须建立在"物理层已够稳"的前提上，而不是替代它。
4. **没有证据的高可用与隔离都不算完成**：拔电演练、探测矩阵、汇总次优实测，才是设计的最后一公里。

</div>

From the CCDE perspective, the six questions this chapter really answers:

<div class="zh" markdown="1">

CCDE 视角下，本章真正要回答的六个问题：

</div>

1. **How many blocks does this campus have?** (the block count decides the tiers)
2. **How far does Layer 2 extend?** (decides the access model and the failure domain)
3. **Where is the gateway, and is the root bridge on the same side?** (removes detours and dual-active)
4. **What stops routing changes from spreading?** (stub/areas/summarisation, which decide convergence time)
5. **Which is larger — the business value of isolation or its operational cost?** (decides whether and how finely to virtualise)
6. **Have you drawn the return arrow of the service chain?** (the difference between "ping works" and "work gets done")

<div class="zh" markdown="1">

1. **这个园区有几块？**（功能块决定层次）
2. **二层最远延伸到哪里？**（决定接入模型与故障域）
3. **网关在哪里，根桥与它在同一侧吗？**（消除绕行与双主）
4. **路由变化会被什么挡住？**（stub/区域/汇总，决定收敛时间）
5. **隔离的业务价值和运维成本，哪个更大？**（决定是否虚拟化、粒度多细）
6. **服务链的回程箭头画了吗？**（决定"能 ping 通"与"能干活"的差别）

</div>

Get these six right, and vPC versus StackWise or EIGRP versus OSPF are just implementation details.

<div class="zh" markdown="1">

这六问答清楚，选 vPC 还是 StackWise、用 EIGRP 还是 OSPF，都只是实现细节。

</div>

> 📌 **Next chapter (Chapter 16, Enterprise Internet Edge Architecture Design)** moves the view from "inside the campus" to "the seam between the campus and the outside world": multihoming, BGP path selection, NAT, DDoS scrubbing, exit high availability. You will find the same three ideas — failure domains, summarisation and the return path — reappearing in a sharper form at the edge.

<div class="zh" markdown="1">

> 📌 **下一章（第 16 章 企业互联网边缘架构设计）** 将把视角从"园区内部"移到"园区与外部世界的接缝"：多宿主、BGP 路径选择、NAT、DDoS 清洗、出口高可用。你会发现本章的"故障域 + 汇总 + 回程"三件事，在边缘会以更尖锐的形式重演。

</div>
