# Chapter 17: Enterprise WAN Architecture Design · 第 17 章：企业 WAN 架构设计

> English study notes on the *CCDE 400-007 Official Cert Guide* | original pages 774–849
> **Where this chapter sits**: it is the longest chapter in the book and the one with the **least design freedom**. In the campus you can swap hardware, pull fibre and carve VLANs; in the WAN **the circuits are rented, the backbone belongs to somebody else, and the SLA is only paper**. So the central question of WAN design becomes: **given that the last mile is not yours, how do overlays, routing policy and QoS wrap "transport you cannot control" into "a service you can"**.

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译与精讲 | 原书第 774-849 页
> **本章定位**：全书篇幅最大的一章，也是"设计自由度最小"的一章。园区里你可以换设备、加光纤、画 VLAN；WAN 里**线路是租的、骨干是别人的、SLA 是纸上的**。于是 WAN 设计的核心问题变成：**在"最后一公里不归你管"的前提下，如何用覆盖层、路由策略与 QoS，把"不可控的传输"包装成"可控的服务"**。

</div>

---

## Topics Covered · 本章涵盖主题

- **Three WAN transport models**: L2 MPLS VPN (VPLS/VLL), L3 MPLS VPN, Internet; plus metro Ethernet and 4G/5G access
- **WAN edge connectivity design**: single-homed/dual-homed/dual-carrier, CPE redundancy, CE-PE routing options and their failure behaviour
- **Overlay technologies**: IPsec, GRE, the three DMVPN phases, FlexVPN, GET VPN, SD-WAN
- **WAN virtualisation**: Multi-VRF CE (VRF-Lite), CSC, Inter-AS options, and the difference between "segmentation" and "isolation"
- **WAN design options by scale**: a four-level model from single-link branch to regional WAN core
- **QoS and performance**: classification models, shaping versus policing, the hidden cost of TCP and MTU
- **WAN migration (original-book topic)**: phased Frame Relay → MPLS L3VPN migration, backdoor dual-point redistribution, keeping the intermediate state self-consistent
- **(Extensions in these notes)** multicast across the WAN, cloud on-ramps, DIA and hybrid transport, capacity and cost models

<div class="zh" markdown="1">

- **三种 WAN 传输模型**：L2 MPLS VPN（VPLS/VLL）、L3 MPLS VPN、Internet；以及城域以太网、4G/5G 接入
- **WAN 边缘连接设计**：单宿主/双宿主/双运营商、CPE 冗余、CE-PE 路由方式与失效行为
- **覆盖技术（Overlay）**：IPsec、GRE、DMVPN 三阶段、FlexVPN、GET VPN、SD-WAN
- **WAN 虚拟化**：Multi-VRF CE（VRF-Lite）、CSC、Inter-AS 选项，以及"分段"与"隔离"的差别
- **WAN 设计选项（按规模）**：从单链路分支到区域 WAN 核心的四级模型
- **QoS 与性能**：分类模型、整形/丢弃、TCP 与 MTU 的隐性成本
- **WAN 迁移（原文专题）**：Frame Relay → MPLS L3VPN 的分阶段迁移、backdoor 双点重分发、中间态路由自洽
- **（本笔记延伸）** 组播跨 WAN、云 on-ramp、DIA 与混合传输、容量与成本模型

</div>

---

## Chapter Roadmap: Fifteen Counter-intuitive Truths About WAN Design · 本章导读：WAN 设计的十五个反直觉认知

The WAN is the chapter where a beautiful topology diagram is easiest to draw and failure behaviour is hardest to explain. The reason is simple: **you control only the two ends, and for the middle you can only "trust"**. The fifteen points below are the ones most often challenged in design reviews.

<div class="zh" markdown="1">

WAN 是全书里"最容易画出漂亮拓扑、最难解释故障行为"的一章。原因很简单：**你只能控制两端，中间那段只能"相信"**。以下十五条，是设计评审里最常被追问的地方。

</div>

![Fifteen claims about WAN design grouped into five families of failure](assets/fig/en17-01-fifteen-truths.svg)

### 1. The First-Order Question in WAN Design Is Not "MPLS or Internet" — It Is "Who Fills the SLA Gap" · WAN 设计的第一性问题不是"用 MPLS 还是 Internet"，而是"SLA 缺口由谁补"

![The SLA gap across five handoffs and the arithmetic that decides whether an overlay is needed](assets/fig/en17-02-sla-gap.svg)

The SLA your carrier signs covers only **its own segment**, while the business experiences **end to end**. The gap opens in three places: **the last mile, inter-carrier interconnection, and your own CPE and policy**.

<div class="zh" markdown="1">

运营商给你的 SLA 只覆盖"它那段"，而业务感知的是"端到端"。缺口在三处：**最后一公里、跨运营商互联、你自己的 CPE 与策略**。

</div>

| SLA item | What the carrier promises | What end-to-end actually looks like |
|---|---|---|
| 99.9% availability | Its backbone and PE segment | Lower once local loops and CPE are added |
| Latency | PE to PE (the usual basis) | Higher once local loop and queueing are added |
| Loss/jitter | Usually not committed, or loosely committed | Voice and video suffer first |
| Fault response | Measured against ticket time | Business outage starts counting from second one |

<div class="zh" markdown="1">

| SLA 项 | 运营商承诺 | 实际端到端 |
|---|---|---|
| 可用性 99.9% | 其骨干与 PE 段 | 叠加本地环路与 CPE 后更低 |
| 时延 | PE 到 PE（常见口径） | 加上本地环路与排队后更高 |
| 丢包/抖动 | 通常不承诺或宽松 | 语音/视频最先受害 |
| 故障响应 | 按工单时长 | 业务中断从第一秒就算 |

</div>

> 🎯 **Design conclusion**: **first compute how much is left after the carrier's promise, then decide whether you need your own overlay and redundancy**. Do not console yourself with a "99.99%" contract.

<div class="zh" markdown="1">

> 🎯 **设计结论**：**先算"运营商承诺之外还剩多少"，再决定要不要自建覆盖层与冗余**。别用"99.99%"的合同安慰自己。

</div>

### 2. The Difference Between L2 and L3 MPLS VPN Is Not "Speed" — It Is "Who Owns the Routing" · L2 与 L3 MPLS VPN 的差别不在"速度"，而在"谁负责路由"

![L2 and L3 MPLS VPN compared, decided by who owns routing rather than by speed](assets/fig/en17-03-l2-vs-l3.svg)

| Dimension | L2 MPLS VPN (VPLS/VLL) | L3 MPLS VPN |
|---|---|---|
| What the carrier delivers | An "Ethernet segment / LAN" | A "routable VPN" (VRF) |
| Who runs routing | **You do** (between CEs) | Carrier PE peers with your CE |
| Topology freedom | Yours to define (including L2 adjacency) | Constrained by the carrier's VPN topology (hub-spoke / any-to-any) |
| Broadcast/multicast | Yours to handle (including STP risk) | Multicast needs mVPN support |
| Fault localisation | Blurred boundary (you cannot see inside "the cloud") | Clean demarcation (PE-CE is the boundary) |
| Best fit | Need L2 adjacency, protocol interoperability, or preservation during migration | Most enterprises (scalable, simple to operate) |

<div class="zh" markdown="1">

| 维度 | L2 MPLS VPN（VPLS/VLL） | L3 MPLS VPN |
|---|---|---|
| 运营商交付 | 一条"以太网线段/局域网" | 一个"可路由的 VPN"（VRF） |
| 谁跑路由 | **客户自己**（CE 之间） | 运营商 PE 与客户 CE 对接 |
| 拓扑灵活度 | 客户自定义（含二层邻接） | 受运营商 VPN 拓扑约束（hub-spoke / any-to-any） |
| 广播/组播 | 客户自己处理（含 STP 风险） | 组播需 mVPN 支持 |
| 故障定位 | 分界模糊（"云"里发生了什么看不到） | 分段清晰（PE-CE 是明确分界） |
| 适用 | 需要二层邻接、协议互通、迁移期保留 | 大多数企业（可扩展、运维简单） |

</div>

> 💡 **One-line test**: **"Do you have anything that must run at Layer 2 across the WAN?"** Yes (legacy apps, non-IP protocols, routing you must control yourself) → L2. No → L3.

<div class="zh" markdown="1">

> 💡 **一句话判据**：**"你有没有必须在 WAN 上跑二层的东西？"** 有（老应用、非 IP 协议、需要自己掌控路由）→ L2；没有 → L3。

</div>

### 3. "Internet + Overlay" Is Not a Cheap Substitute; It Is a Different Failure Model · "Internet + 覆盖层"不是廉价替代品，而是另一种失效模型

![MPLS failure visibility against the Internet plus overlay failure model](assets/fig/en17-04-overlay-failure-model.svg)

MPLS fails by **the carrier telling you it is down**; the Internet fails by **nobody telling you anything — it simply does not work**.

<div class="zh" markdown="1">

MPLS 的失效是"运营商告诉你断了"；Internet 的失效是"**没人告诉你，但就是不通**"。

</div>

| Dimension | MPLS | Internet + Overlay |
|---|---|---|
| Predictability of quality | High (SLA, queues) | Low (per-hop, cross-domain, invisible congestion) |
| Failure visibility | Carrier alarms plus PE-CE state | Only your own probes (SLA/BFD/application probes) |
| Encryption | Optional (already isolated) | **Mandatory** (runs over the public Internet) |
| Cost | Priced by bandwidth and distance, expensive | Cheap, easy to scale up |
| Multicast | Needs mVPN | Needs GRE/DMVPN to carry it |
| Verdict | For core services that "must be stable" | For general traffic that needs flexibility and multiple paths |

<div class="zh" markdown="1">

| 维度 | MPLS | Internet + Overlay |
|---|---|---|
| 质量可预期性 | 高（有 SLA、有队列） | 低（逐跳、跨域、拥塞不可见） |
| 故障可见性 | 运营商告警 + PE-CE 状态 | 只能靠自己探测（SLA/BFD/应用探测） |
| 加密 | 可选（本就隔离） | **必需**（公网传输） |
| 成本 | 按带宽、距离计价，贵 | 便宜、易扩容 |
| 组播 | 需 mVPN | 需 GRE/DMVPN 承载 |
| 结论 | 适合"必须稳"的核心业务 | 适合"要灵活、可多路径"的通用业务 |

</div>

> ⚠️ **The most common misjudgement**: treating the Internet as "MPLS at a lower price". It has **no** queue guarantees, **no** explicit failure notification and **no** end-to-end latency commitment. An overlay can add encryption and topology; it cannot add underlying quality.

<div class="zh" markdown="1">

> ⚠️ **最常见的误判**：把 Internet 当成"便宜版的 MPLS"。它**没有**队列保证、**没有**明确的故障通知、**没有**端到端时延承诺。覆盖层能补"加密与拓扑"，补不了"底层质量"。

</div>

### 4. Choosing an Overlay Is Really a Trade-off Between Tunnel Count and Control-Plane Complexity · 覆盖技术的选择，本质是"隧道数量与控制面复杂度"的取舍

![Full-mesh tunnel arithmetic against hub-and-spoke scaling with six overlay technologies](assets/fig/en17-05-tunnel-count.svg)

| Technology | Tunnel shape | Tunnel count | Control plane | Best fit |
|---|---|---|---|---|
| IPsec (point to point) | Static | O(n²) when fully meshed | None (manual) | Few sites, strict compliance |
| GRE | Static | O(n²) | None | Need multicast or non-IP |
| DMVPN | mGRE + NHRP | O(n) on the hub; on demand between spokes | NHRP plus a routing protocol | Medium/large hub-spoke needing direct spoke paths |
| FlexVPN | Dynamic SVTI | O(n) | IKEv2 plus routing | Large scale, flexible policy |
| GET VPN | Group key, no tunnel | 0 (overlay rides a private network) | Group key management | Encryption on pure MPLS without tunnel overhead |
| SD-WAN | Dynamic, per application | O(n), orchestrated by controllers | Controller plus policy | Multiple transports, application awareness, cloud access |

<div class="zh" markdown="1">

| 技术 | 隧道形态 | 隧道数 | 控制面 | 适用 |
|---|---|---|---|---|
| IPsec（点对点） | 静态 | O(n²)（全互联时） | 无（手工） | 少量站点、合规要求高 |
| GRE | 静态 | O(n²) | 无 | 需要组播/非 IP |
| DMVPN | mGRE + NHRP | Hub 上 O(n)，Spoke 间按需 | NHRP + 路由协议 | 中大型 hub-spoke，需要直连 |
| FlexVPN | 动态 SVTI | O(n) | IKEv2 + 路由 | 大规模、需要灵活策略 |
| GET VPN | 组密钥、无隧道 | 0（overlay 在私网上） | 组密钥管理 | 纯 MPLS 上的加密（无隧道开销） |
| SD-WAN | 动态、按应用 | O(n)（控制器编排） | 控制器 + 策略 | 多传输、应用感知、云接入 |

</div>

> 🎯 **The test**: **site count × whether spokes must talk directly × whether you have more than one transport** — three questions pick the technology. **Do not choose SD-WAN to look modern, and do not choose a full IPsec mesh to save money.**

<div class="zh" markdown="1">

> 🎯 **判据**：**站点数 × 是否需要 spoke 直连 × 是否有多种传输**，三个问题定技术。**不要为了"先进"选 SD-WAN，也不要为了"省钱"选 IPsec 全互联。**

</div>

### 5. The Three DMVPN Phases Decide "Can I Summarise" and "Can Spokes Talk Directly" · DMVPN 的三个阶段，决定了"能不能汇总"与"能不能直连"

![DMVPN phase one, two and three compared for spoke-to-spoke behaviour and summarisation](assets/fig/en17-06-dmvpn-phases.svg)

This is a high-frequency CCDE topic and the place where configurations most often go wrong:

<div class="zh" markdown="1">

这是 CCDE 的高频考点，也是最容易配错的地方：

</div>

| Phase | Characteristics | Can the hub summarise? | Spoke-to-spoke traffic |
|---|---|---|---|
| Phase 1 | Spokes point a default route at the hub (mGRE, but /32s are not exchanged) | Yes | **Must go through the hub** |
| Phase 2 | Spokes exchange /32 routes and build direct tunnels | **No** (summaries break NHRP resolution) | Direct (requires specific /32 routes) |
| Phase 3 | NHRP shortcut plus redirect | **Yes** (direct paths survive summarisation) | Direct (resolved on demand via NHRP) |

<div class="zh" markdown="1">

| 阶段 | 特性 | 能否 hub 汇总 | Spoke 间流量 |
|---|---|---|---|
| Phase 1 | Spoke 默认路由指向 Hub（mGRE 但 /32 不互告） | 可以 | **必须经 Hub** |
| Phase 2 | Spoke 之间交换 /32 路由，建立直连隧道 | **不行**（汇总会破坏 NHRP 解析） | 直连（需 /32 具体路由） |
| Phase 3 | NHRP Shortcut + Redirect | **可以**（有汇总仍能直连） | 直连（NHRP 按需解析） |

</div>

> 💡 **One rule of thumb**: **"summarise + direct spoke paths" means Phase 3, and only Phase 3.** Many sites that complain "DMVPN is configured but spoke-to-spoke is slow" are really hitting the Phase 2 plus summarisation conflict.

<div class="zh" markdown="1">

> 💡 **一条经验**：**要"汇总 + 直连"，只有 Phase 3。** 很多"配了 DMVPN 但 spoke 互通很慢"的现场，本质是 Phase 2 + 汇总的冲突。

</div>

### 6. The Tunnel's First Hidden Tax Is MTU; the Second Is Encrypted Throughput · 隧道的第一笔"隐形税"是 MTU，第二笔是加密吞吐

![Header overhead per encapsulation, the MSS calculation and the encrypted throughput tax](assets/fig/en17-07-mtu-tax.svg)

| Encapsulation | Extra overhead (approx.) | Consequence |
|---|---|---|
| GRE | 24 bytes | 1500 → 1476 |
| IPsec (tunnel mode, ESP+AES) | 50–73 bytes | 1500 → 1427–1450 |
| GRE + IPsec | 70–100 bytes | 1500 → around 1400 |
| VXLAN | 50 bytes | 1500 → 1450 |
| DMVPN + IPsec | Same as GRE + IPsec | Same as above |

<div class="zh" markdown="1">

| 封装 | 额外开销（约） | 后果 |
|---|---|---|
| GRE | 24 字节 | 1500 → 1476 |
| IPsec（tunnel 模式，ESP+AES） | 50–73 字节 | 1500 → 1427–1450 |
| GRE + IPsec | 70–100 字节 | 1500 → 1400 左右 |
| VXLAN | 50 字节 | 1500 → 1450 |
| DMVPN + IPsec | 同 GRE+IPsec | 同上 |

</div>

**Two ways to deal with it**:

<div class="zh" markdown="1">

**两种应对**：

</div>

| Mechanism | How it works | Side effect |
|---|---|---|
| `ip mtu` + `ip tcp adjust-mss` | Clamp the TCP MSS proactively so packets are never fragmented | Works only for TCP; UDP/ICMP still need PMTUD |
| PMTUD (depends on ICMP type 3 code 4) | Discover the path MTU end to end | Becomes a "big-packet black hole" when ICMP is filtered |

<div class="zh" markdown="1">

| 手段 | 原理 | 副作用 |
|---|---|---|
| `ip mtu` + `ip tcp adjust-mss` | 主动收敛 TCP MSS，避免分片 | 只对 TCP 有效；UDP/ICMP 仍需 PMTUD |
| PMTUD（依赖 ICMP type 3 code 4） | 端到端发现路径 MTU | 策略拦 ICMP 时变"大包黑洞" |

</div>

> ⚠️ **Classic symptom**: **ping works (small packets), the home page loads (small responses), but large uploads/downloads stall and HTTPS handshakes complete with no data** — check MTU/MSS first, not routing.

<div class="zh" markdown="1">

> ⚠️ **经典症状**：**能 ping 通（小包）、能打开首页（小响应）、但下载/上传大文件卡死、HTTPS 握手后无数据** —— 先查 MTU/MSS，不要先查路由。

</div>

### 7. The Hub Is the Most Expensive Single Point in the WAN: Bandwidth by N−1, Hardware by Encrypted Throughput · Hub 是 WAN 里最贵的单点：带宽按"N−1"算，设备按"加密后吞吐"算

![Four hub capacities sized in sequence with the N minus one requirement](assets/fig/en17-08-hub-sizing.svg)

A common mistake: set hub bandwidth = Σ(branch bandwidth) × a convergence ratio, then size it from "average utilisation".

<div class="zh" markdown="1">

一个常见错误：Hub 带宽 = Σ(分支带宽) × 收敛比，然后按"平均利用率"选型。

</div>

```
80 branches × 20 Mbps = 1.6 Gbps (aggregate peak)
Hub egress at a 2:1 ratio = 800 Mbps  -> looks sufficient
But: branch upstream bursts arrive together + multicast/broadcast + 40% loss after encryption
Actually needed: >= 1.6 Gbps, and still compliant after encryption
```

<div class="zh" markdown="1">

```
分支 80 个 × 20 Mbps = 1.6 Gbps（汇聚峰值）
Hub 出口按 2:1 收敛 = 800 Mbps  →  看似够
但：分支上行突发同时到达 + 组播/广播 + 加密后吞吐下降 40%
实际需要：≥1.6 Gbps 且加密后仍达标
```

</div>

> 🎯 **Conclusion**: **size hub bandwidth for "all branches at peak simultaneously", and size hub hardware for "measured throughput with encryption enabled"**. Skip either one and the hub becomes the throttle for the whole network.

<div class="zh" markdown="1">

> 🎯 **结论**：**Hub 的带宽要按"所有分支同时峰值"设计，设备要按"开启加密后的实测吞吐"设计**。这两条都不做，Hub 会成为全网的节流阀。

</div>

### 8. Static Routes with Floating Backup Are Almost Always Wrong in the WAN · 静态路由 + 浮动备份在 WAN 里几乎总是错的

![Time to switch paths by mechanism, from floating static to eBGP with BFD](assets/fig/en17-09-floating-static.svg)

| Approach | What it can detect | Convergence time | Best fit |
|---|---|---|---|
| Static + floating | Link down only | Depends on probes, or on a human | Very small scale, temporary |
| Static + IP SLA tracking | End-to-end probing | Seconds (set by the probe interval) | Dual uplink branches |
| BGP (to the carrier or between CEs) | Prefix withdrawal | Seconds (faster with BFD) | Multihoming, fine-grained path selection |
| IGP (between your own CEs) | Neighbour/interface state | Sub-second to seconds | Your own overlay (DMVPN/FlexVPN) |

<div class="zh" markdown="1">

| 方案 | 检测能力 | 收敛时间 | 适用 |
|---|---|---|---|
| 静态 + 浮动 | 只感知链路 down | 依赖探测或人工 | 极小规模、临时 |
| 静态 + IP SLA track | 端到端探测 | 秒级（探测周期决定） | 分支双上行 |
| BGP（对运营商或 CE 间） | 前缀撤销即失效 | 秒级（+BFD） | 多宿主、需要精细选路 |
| IGP（自有 CE 间） | 邻居/接口 | 亚秒~秒级 | 自有覆盖层（DMVPN/FlexVPN） |

</div>

> ⚠️ **Typical incident**: the primary link fails **on the carrier side** while the interface stays up, the floating static never takes over, and the business is down for 30–180 minutes. **In the WAN, "link up" almost never means "path usable".**

<div class="zh" markdown="1">

> ⚠️ **典型事故**：主链路"运营商侧故障"但接口 up，浮动静态不切，业务中断 30–180 分钟。**在 WAN 里，"链路 up" 几乎不代表"路径可用"。**

</div>

### 9. Multicast Across the WAN Is Not Just "Turn On PIM" · 组播跨 WAN 不是"打开 PIM"就行

![Three ways to carry multicast across a WAN with their replication points and costs](assets/fig/en17-10-multicast-wan.svg)

| Transport option | What it requires | What it costs |
|---|---|---|
| MPLS mVPN | Carrier support (GRE/MLDP/RSVP-TE) | Money and configuration complexity |
| GRE/DMVPN tunnels | Tunnel support for multicast plus hop-by-hop PIM | Hub replication load, tunnel count |
| Internet multicast | Essentially unavailable (not supported across domains) | — |
| Application-layer substitute (CDN/distribution) | No network multicast at all | Application changes |

<div class="zh" markdown="1">

| 承载方式 | 需要什么 | 代价 |
|---|---|---|
| MPLS mVPN | 运营商支持（GRE/MLDP/RSVP-TE） | 费用与配置复杂度 |
| GRE/DMVPN 隧道 | 隧道支持组播 + PIM 逐跳 | Hub 复制开销、隧道数量 |
| Internet 组播 | 基本不可用（跨域不支持） | — |
| 应用层替代（CDN/分发） | 无需网络组播 | 应用改造 |

</div>

> 💡 **The test**: **"few sources, many receivers, concentrated in a handful of sites" → tunnels or application distribution both work; "many sources, scattered receivers, hard real-time requirement" → only then is mVPN worth the money.**

<div class="zh" markdown="1">

> 💡 **判据**：**"组播源少、接收者多、且集中在少数站点" → 用隧道/应用分发都行；"源多、接收者分散、实时性要求高" → 才值得上 mVPN。**

</div>

### 10. Multi-VRF CE Is "Segmentation", Not "Encryption" · Multi-VRF CE 是"分段"不是"加密"

![One CE carrying three VRFs, and the difference between routing separation and encryption](assets/fig/en17-11-multivrf-ce.svg)

| Item | Multi-VRF CE (VRF-Lite) | Real security isolation |
|---|---|---|
| What is isolated | Routing tables (control plane) | Data-plane policy plus encryption |
| What it prevents | Route bleeding, overlapping addresses, accidental reachability | Unauthorised access, eavesdropping, lateral movement |
| What it does not prevent | On-link sniffing, policy mistakes, configuration drift | — |

<div class="zh" markdown="1">

| 项 | Multi-VRF CE（VRF-Lite） | 真正的安全隔离 |
|---|---|---|
| 隔离对象 | 路由表（控制面） | 数据面策略 + 加密 |
| 防什么 | 路由混叠、地址重叠、误可达 | 未授权访问、窃听、横向移动 |
| 不防什么 | 同链路嗅探、策略错误、配置漂移 | — |

</div>

> ⚠️ **In a compliance context**: **"we used VRFs" is not evidence**; the evidence is "every cross-VRF probe fails + policy audit + traffic counters read zero".

<div class="zh" markdown="1">

> ⚠️ **合规场景**：**"我们用了 VRF" 不是证据**，证据是"跨 VRF 的探测全部失败 + 策略审计 + 流量统计为 0"。

</div>

### 11. WAN Optimisation Has Been Pushed to the Edge by "Protocol Evolution + Encryption" · WAN 优化（WAN Optimization）已被"协议演进 + 加密"挤到边缘

![The four classic WAN optimisation promises against their modern status](assets/fig/en17-12-wan-optimisation.svg)

| Traditional value | Where it stands now |
|---|---|
| TCP window tuning / fewer round trips | Modern applications multiplex; HTTP/2 and HTTP/3 already mitigate this |
| Deduplication/compression | Largely defeated by end-to-end encryption (unless you become a man in the middle) |
| Caching | Replaced by CDN and cloud-side caching |
| Still valid | High-latency satellite links, old CIFS/backup traffic, specific applications that need protocol acceleration |

<div class="zh" markdown="1">

| 传统价值 | 现状 |
|---|---|
| TCP 窗口优化 / 减少往返 | 现代应用多路复用、HTTP/2/3 已缓解 |
| 数据去重/压缩 | 全流量加密后基本失效（除非中间人解密） |
| 缓存 | CDN/云侧缓存替代 |
| 仍有效的场景 | 高时延卫星链路、老旧 CIFS/备份流量、需要协议加速的特定应用 |

</div>

> 🎯 **Conclusion**: **do QoS and path engineering first, then consider WAN optimisation appliances** — and you must be able to answer "how does encrypted traffic get optimised?"

<div class="zh" markdown="1">

> 🎯 **结论**：**先做 QoS 与路径优化，再考虑 WAN 优化设备**；且必须回答"加密流量如何被优化"。

</div>

### 12. QoS in the WAN Is Not "Configure a Few Queues" — It Is "Align with the Class You Bought" · QoS 在 WAN 上不是"配几个队列"，而是"与运营商签的等级对齐"

![Six practical QoS classes, the LLQ police and CE shaper percentages, and where enforcement happens](assets/fig/en17-13-qos-alignment.svg)

| Layer | Who does it | The key action |
|---|---|---|
| Application marking | Endpoint or gateway | Mark at the trust boundary (otherwise users can forge it) |
| CE egress shaping | You | **Shape to the contracted CIR** so you are not policed for overspeed |
| Carrier queues | The carrier | Carried per class (for example six classes), and written into the contract |
| Receiving side | You | Pointless (congestion happens at the egress and in the backbone) |

<div class="zh" markdown="1">

| 层 | 谁做 | 关键动作 |
|---|---|---|
| 应用标记 | 终端/网关 | 标记可信边界（否则用户可伪造） |
| CE 出口整形 | 你 | **按合同 CIR 整形**，避免超速被运营商丢弃 |
| 运营商队列 | 运营商 | 按等级（如 6 类）承运，需合同约定 |
| 接收侧 | 你 | 无意义（拥塞发生在出口与骨干） |

</div>

> ⚠️ **The most common error**: implementing QoS only at headquarters. When the branch uplink congests, voice dies anyway. **QoS must exist on every egress that can congest — above all the branch CE uplink.**

<div class="zh" markdown="1">

> ⚠️ **最常见的错**：只在总部做 QoS，分支上行拥塞时语音照样死。**QoS 必须在每个"会拥塞的出口"上做，尤其是分支 CE 的上行。**

</div>

### 13. "Dual Carrier" in the WAN Also Requires Physical Diversity to Be Verified · "双运营商"在 WAN 里同样要验证物理多样性

![Three diversity checks, five connectivity shapes and the WAN single points that hide](assets/fig/en17-14-carrier-diversity.svg)

The same logic as the internet edge: **same duct, same exchange building, same metro ring = a single point**. The WAN adds two single points of its own:

<div class="zh" markdown="1">

与互联网边缘一样的逻辑：**同管道、同局房、同城域网 = 单点**。此外 WAN 还有两个特有单点：

</div>

| Single point | How it shows up | Mitigation |
|---|---|---|
| One CPE carrying both links | A device failure kills everything | Dual CPE |
| A shared last mile | Two carriers leasing the same copper or fibre | Demand different access types (for example fibre plus 5G) |

<div class="zh" markdown="1">

| 单点 | 表现 | 缓解 |
|---|---|---|
| 同一台 CPE 承载两条链路 | 设备故障全断 | 双 CPE |
| 同一段本地环路（last mile） | 两家运营商租用同一段铜/纤 | 要求"接入方式不同"（如光纤 + 5G） |

</div>

### 14. Cloud and SaaS Move the WAN "Exit Point" from Headquarters to "Where the Application Lives" · 云与 SaaS 把 WAN 的"出口位置"从总部挪到了"离应用最近的地方"

![Traditional hub backhaul against destination-steered flows for internal, SaaS and IaaS traffic](assets/fig/en17-15-cloud-exit-point.svg)

| Traffic type | Traditional path | Optimised path |
|---|---|---|
| Internal applications (ERP/file) | Branch → HQ/DC | Keep it (policy and audit still apply) |
| SaaS (M365/Salesforce) | Branch → HQ → Internet → SaaS | Branch-local DIA / cloud security gateway |
| IaaS (public cloud) | Branch → HQ → Internet/dedicated line → cloud | Regional WAN gateway → cloud on-ramp |

<div class="zh" markdown="1">

| 流量类型 | 传统路径 | 优化路径 |
|---|---|---|
| 内网业务（ERP/文件） | 分支 → 总部/DC | 保持（需策略与审计） |
| SaaS（M365/Salesforce） | 分支 → 总部 → Internet → SaaS | 分支本地 DIA / 云安全网关 |
| IaaS（公有云） | 分支 → 总部 → Internet/专线 → 云 | 区域 WAN 网关 → 云 on-ramp |

</div>

> 💡 **The test**: **steer by "destination", not by "site"** — and always keep an explicit path back to the internal network.

<div class="zh" markdown="1">

> 💡 **判据**：**按"目的地"分流，不按"站点"分流**；同时保留"回内网"的明确路径。

</div>

### 15. WAN Scalability = "How Many Places Must Change to Add One Site" · WAN 的可扩展性 = "加一个站点要动几处"

![The five artefacts that change per site and four delivery models with their change counts](assets/fig/en17-16-scalability.svg)

| Action | What does not scale | What scales |
|---|---|---|
| Add a branch | Hand-configure every hub, add static routes, add ACLs, edit QoS | Templates + zero-touch provisioning (ZTP) + dynamic routing or controller orchestration |
| Add a transport | Redesign the topology | A multi-transport abstraction (overlay decoupled from underlay) |
| Grow bandwidth | Replace hardware, change topology | Link aggregation/multipath plus application-aware path selection |
| Add a region | One central hub carries it all | Regional hubs with hierarchical summarisation |

<div class="zh" markdown="1">

| 动作 | 不可扩展的做法 | 可扩展的做法 |
|---|---|---|
| 新增分支 | 手工配每台 Hub、加静态路由、加 ACL、改 QoS | 模板 + 零接触部署（ZTP）+ 动态路由/控制器编排 |
| 新增传输 | 重设计拓扑 | 多传输抽象（overlay 与 underlay 解耦） |
| 扩容带宽 | 换设备、改拓扑 | 链路聚合/多路径 + 应用感知选路 |
| 新增区域 | 中心化 Hub 承载 | 区域 Hub + 分层汇总 |

</div>

> 🎯 **In one line**: **WAN scalability is the scalability of operating cost**, not "how many sites can be configured".

<div class="zh" markdown="1">

> 🎯 **一句话**：**WAN 的可扩展性是"运营成本的可扩展性"**，不是"能装多少站点"。

</div>

---

## The Six-Step WAN Design Method · WAN 设计的六步方法论

![The six-step WAN method with inputs, deliverables, hurdles and the cost of each skipped step](assets/fig/en17-17-six-steps.svg)

The easiest mistake in WAN design is to start by comparing carrier quotes. The correct order is: **business reachability first, then transport model, then redundancy shape, then overlay and virtualisation, then routing and QoS, and finally capacity and verification**.

<div class="zh" markdown="1">

WAN 设计最容易犯的错，是从"比较运营商报价"开始。正确顺序是：**先定业务可达性需求，再定传输模型，再定冗余形态，再定覆盖与虚拟化，再定路由与 QoS，最后定容量与验证**。

</div>

```
1 Set the business map   Site list / density / who talks to whom / latency sensitivity -> topology needs
2 Set the transport      L2 MPLS / L3 MPLS / Internet / hybrid -> carrying option per site class
3 Set the redundancy     Single/dual link, single/dual CPE, single/dual carrier -> availability target
4 Set overlay and segmentation  Encryption, multicast, VRF segmentation? -> DMVPN/SD-WAN/Multi-VRF CE
5 Set routing and QoS    Routing domains, summarisation boundaries, marking and shaping points -> convergence and experience
6 Set capacity and validation  Hub bandwidth / encrypted throughput / tunnel count / convergence budget -> sizing and acceptance
```

<div class="zh" markdown="1">

```
① 定业务地图   站点清单 / 站点密度 / 互访关系 / 时延敏感度 → 拓扑需求
② 定传输模型   L2 MPLS / L3 MPLS / Internet / 混合 → 每类站点的承载
③ 定冗余形态   单/双链路、单/双 CPE、单/双运营商 → 可用性目标
④ 定覆盖与隔离 是否需要加密、组播、分段（VRF）→ DMVPN/SD-WAN/Multi-VRF CE
⑤ 定路由与QoS  路由域划分、汇总边界、标记与整形点 → 收敛与体验
⑥ 定容量验证   Hub 带宽/加密吞吐/隧道数/收敛预算 → 选型与验收
```

</div>

### Expanding the Six Steps: Inputs, Outputs and the Hurdle You Cannot Skip · 六步展开：每步的输入、输出与"过不去的坎"

| Step | Input | Output (deliverable) | The hurdle you must clear on the spot |
|---|---|---|---|
| ① Business map | Site count and spread, application inventory, latency requirements | Site tiers (A/B/C) plus a reachability matrix | **Is there a "any two points must communicate" requirement?** (decides hub-spoke versus any-to-any) |
| ② Transport model | Circuits available at each site, budget, SLA requirements | Transport choice per site class | Can the core business tolerate Internet quality? |
| ③ Redundancy shape | Availability target, acceptable switchover time | A link/CPE/carrier redundancy combination | **Must a "carrier failure" trigger switchover?** (decides BGP versus static) |
| ④ Overlay and segmentation | Encryption, multicast and segmentation requirements | Overlay technology plus VRF scheme | Do summarisation and direct spoke paths conflict? (DMVPN phase) |
| ⑤ Routing and QoS | Routing domains, addressing plan, service classes | IGP/BGP design plus classification and shaping points | At which egress does QoS take effect? (the branch uplink is the usual omission) |
| ⑥ Capacity and validation | Traffic model, encryption overhead, growth forecast | Capacity table + convergence budget + acceptance cases | Is the hub sized for "all sites at peak, after encryption"? |

<div class="zh" markdown="1">

| 步骤 | 输入 | 输出（交付物） | 过不去的坎（必须当场解决） |
|---|---|---|---|
| ① 业务地图 | 站点数量与分布、应用清单、时延要求 | 站点分级（A/B/C）+ 互访矩阵 | **是否存在"任意两点都要通"的需求**（决定 hub-spoke 还是 any-to-any） |
| ② 传输模型 | 各站点可获得的线路、预算、SLA 要求 | 每类站点的承载选型 | 核心业务能否接受 Internet 质量 |
| ③ 冗余形态 | 可用性目标、可接受的切换时间 | 链路/CPE/运营商冗余组合 | **"运营商故障"是否要切**（决定 BGP vs 静态） |
| ④ 覆盖与隔离 | 加密要求、组播需求、分段需求 | 覆盖技术 + VRF 方案 | 汇总与直连是否冲突（DMVPN 阶段） |
| ⑤ 路由与 QoS | 路由域、地址规划、业务等级 | IGP/BGP 设计 + 分类与整形点 | QoS 在哪个出口生效（分支上行最常漏） |
| ⑥ 容量与验证 | 流量模型、加密开销、增长预测 | 容量表 + 收敛预算 + 验收用例 | Hub 是否按"全站点峰值 + 加密后"设计 |

</div>

> 🎯 **The order cannot be reversed**: negotiate bandwidth first and only later ask "do we need encryption", and you will inevitably discover throughput has halved after IPsec goes in.

<div class="zh" markdown="1">

> 🎯 **顺序不能反**：先谈带宽再想"要不要加密"，结果一定是"上了 IPsec 才发现吞吐减半"。

</div>

### The Common "Skipped Steps" and What They Cost · 每一步的常见"跳步"及其后果

| Skipped step | Consequence (usually erupting 3–12 months after go-live) |
|---|---|
| Skip ① and go straight to ② | Hub-spoke is used to carry heavy spoke-to-spoke traffic and the hub becomes the bottleneck |
| Skip ③ and sign the contract | Two carriers share the last mile, so the redundancy exists only on paper |
| Skip ④ and configure tunnels | O(n²) tunnel count, MTU never adjusted, spoke-to-spoke connectivity fails |
| Skip ⑤ and go live | QoS only at headquarters; voice dies the first time a branch congests |
| Skip ⑥ and accept the delivery | Hub encrypted throughput is insufficient and scaling up means new hardware |

<div class="zh" markdown="1">

| 跳步 | 后果（通常在上线后 3–12 个月爆发） |
|---|---|
| 跳过①直接② | 用 hub-spoke 承载了大量 spoke 间流量，Hub 成为瓶颈 |
| 跳过③直接签合同 | 双运营商同 last mile，冗余只存在于纸面 |
| 跳过④直接配隧道 | 隧道数量 O(n²)、MTU 未调、spoke 直连失败 |
| 跳过⑤直接上线 | QoS 只在总部、分支拥塞时语音先死 |
| 跳过⑥直接验收 | Hub 加密后吞吐不足，扩容要换设备 |

</div>

---

## Foundation Topics · 基础内容

---

## 1. The Three WAN Transport Models · 一、三种 WAN 传输模型

![L2 MPLS VPN, L3 MPLS VPN and Internet plus overlay compared over ten dimensions](assets/fig/en17-18-three-models.svg)

### L2 MPLS VPN: VPLS and VLL · L2 MPLS VPN：VPLS 与 VLL

The carrier sells you a "Layer 2 pipe" and you run routing or Layer 2 protocols across it yourself.

<div class="zh" markdown="1">

运营商把"二层管道"卖给你，你自己在上面跑路由/二层协议。

</div>

| Form | Description | Topology | Typical use |
|---|---|---|---|
| **VLL / pseudowire (E-Line)** | Point-to-point Layer 2 transport | Two points | Data centre interconnect, keeping the old design during migration, non-IP protocols |
| **VPLS (E-LAN)** | Multipoint Layer 2 switching (the carrier emulates one switch) | Multipoint | Several sites in one broadcast domain, L2 adjacency |
| **E-Tree** | Point-to-multipoint (the Layer 2 form of hub-spoke) | Tree | Video distribution, one-way collection |

<div class="zh" markdown="1">

| 形态 | 描述 | 拓扑 | 典型用途 |
|---|---|---|---|
| **VLL / Pseudowire（E-Line）** | 点对点二层透传 | 两点 | 数据中心互联、迁移期保留、非 IP 协议 |
| **VPLS（E-LAN）** | 多点二层交换（运营商模拟一台交换机） | 多点 | 多站点同一广播域、需要二层邻接 |
| **E-Tree** | 一点到多点（Hub-Spoke 的二层形态） | 树 | 视频分发、单向采集 |

</div>

| Advantages | Disadvantages |
|---|---|
| The customer fully controls routing and topology | A Layer 2 domain spreads out → loop and broadcast risk becomes yours |
| Supports non-IP, multicast and protocol interoperability | Blurred fault boundary (invisible inside "the cloud") |
| Migration can keep existing addresses and adjacencies | Scale limited by MAC tables and STP |
| The carrier never touches customer routing | Bandwidth granularity and pricing are usually worse |

<div class="zh" markdown="1">

| 优点 | 缺点 |
|---|---|
| 客户完全掌控路由与拓扑 | 二层域扩散 → 环路/广播风险由客户承担 |
| 支持非 IP、组播、协议互通 | 故障分界模糊（"云"里不可见） |
| 迁移期可保留原有地址与邻接 | 规模受 MAC 表与 STP 约束 |
| 运营商不参与客户路由 | 带宽粒度与计费通常更高 |

</div>

> ⚠️ **Running STP over an L2 VPN is common and dangerous**: one customer-side loop propagates across the carrier backbone and the carrier may simply shut your port. **If you can do it at Layer 3, do not do Layer 2 across the WAN.**

<div class="zh" markdown="1">

> ⚠️ **L2 VPN 上跑 STP 是常见但危险的做法**：一次客户侧环路会通过运营商骨干扩散，运营商可能直接切断你的端口。**能做三层就别在 WAN 上做二层。**

</div>

### L3 MPLS VPN: PE-CE Routing and VRFs · L3 MPLS VPN：PE-CE 路由与 VRF

The carrier keeps a VRF per customer and distributes VPN routes between PEs with MP-BGP (RD disambiguates prefixes, RT controls import and export).

<div class="zh" markdown="1">

运营商为每个客户维护 VRF，通过 MP-BGP 在 PE 之间传递 VPN 路由（RD 区分前缀，RT 控制导入导出）。

</div>

| PE-CE routing | Characteristics | Best fit |
|---|---|---|
| Static | Simplest, no protocol overhead | Small branches, single-homed |
| eBGP | Multihoming, policy, inherent loop prevention | Medium/large branches needing path control |
| OSPF / EIGRP | Matches the customer IGP, easy to learn | Customers standardising on one IGP |
| Dual stack/multiprotocol | Needs carrier support | IPv6, multicast |

<div class="zh" markdown="1">

| PE-CE 路由 | 特点 | 适用 |
|---|---|---|
| 静态 | 最简单、无协议开销 | 小型分支、单宿主 |
| eBGP | 可多宿主、可做策略、天然防环 | 中大分支、需要选路控制 |
| OSPF / EIGRP | 与客户 IGP 一致、学习简单 | 客户内部统一 IGP |
| 双栈/多协议 | 需运营商支持 | IPv6、组播 |

</div>

| Advantages | Disadvantages |
|---|---|
| Any-to-any or hub-spoke carried by the carrier | Topology details constrained by the carrier product |
| QoS classes guaranteed by the carrier | Multicast needs mVPN (extra cost) |
| No network-wide tunnels for the customer to maintain | Changes ride a ticket queue, so they are slow |
| Clean demarcation (PE-CE) | Cost rises with bandwidth and site count |

<div class="zh" markdown="1">

| 优点 | 缺点 |
|---|---|
| any-to-any 或 hub-spoke 由运营商承载 | 拓扑细节受运营商产品约束 |
| QoS 等级可由运营商保障 | 组播需 mVPN（额外费用） |
| 客户无需维护全网隧道 | 变更依赖工单，周期长 |
| 分界清晰（PE-CE） | 成本随带宽与站点数上升 |

</div>

### Internet (Public Transport Plus an Overlay) · Internet（公网承载 + 覆盖层）

| Advantages | Disadvantages |
|---|---|
| Cheap, available anywhere, fast to scale | No quality guarantee, no failure notification |
| Naturally supports multipath and multiple carriers | Requires encryption and NAT traversal |
| Local access to cloud and SaaS | Tunnel overhead (MTU, encrypted throughput) |
| Ideal underlay for SD-WAN multi-transport | Troubleshooting needs an end-to-end toolchain |

<div class="zh" markdown="1">

| 优点 | 缺点 |
|---|---|
| 便宜、随处可得、扩容快 | 无质量保证、无故障通知 |
| 天然支持多路径/多运营商 | 需要加密与 NAT 穿透 |
| 云与 SaaS 就近接入 | 隧道开销（MTU/加密吞吐） |
| 适合 SD-WAN 多传输 | 排障需端到端工具链 |

</div>

### Other Access Forms · 其他接入形态

| Form | Characteristics | Typical use |
|---|---|---|
| Metro Ethernet | High bandwidth and low latency inside a metro | Intra-city DC interconnect, campus interconnect |
| 4G/5G | Fast to deploy, billed by volume | Backup, temporary sites, IoT |
| Broadband (fibre/coax) | Cheap, asymmetric up/down | Branch DIA, SOHO |
| Satellite | Wide coverage, high latency | Remote sites (with optimisation/acceleration) |

<div class="zh" markdown="1">

| 形态 | 特点 | 典型用途 |
|---|---|---|
| 城域以太网（Metro Ethernet） | 城域内高带宽、低时延 | 同城 DC 互联、园区互联 |
| 4G/5G | 部署快、按流量计费 | 备份、临时站点、IoT |
| 宽带（光纤/同轴） | 便宜、上下行不对称 | 分支 DIA、SOHO |
| 卫星 | 覆盖广、时延高 | 偏远站点（配优化/加速） |

</div>

### The Three Models Side by Side (Original Table 17-1 Plus Additions) · 三种模型综合对比（原书 Table 17-1 + 补充）

| Dimension | L2 MPLS VPN | L3 MPLS VPN | Internet + Overlay |
|---|---|---|---|
| Customer control | Highest | Medium | High (through the overlay) |
| Carrier involvement | Transport only | Participates in routing | Transport only |
| QoS guarantees | Contract-dependent | Good (classes exist) | Essentially none |
| Multicast | Customer handles it | Needs mVPN | Needs tunnel transport |
| Encryption | Usually unnecessary (isolated) | Usually unnecessary | **Mandatory** |
| Topology freedom | Highest (L2 adjacency) | Constrained by the product | High (set by the overlay) |
| Cost | High | Medium-high | Low |
| Speed of expansion | Slow (tickets) | Slow | Fast |
| Operational complexity | High (you carry the routing) | Low | Medium (tunnels/controllers) |
| Best fit | Special L2 needs, migration | Mainstream enterprise core | Many branches, cloud-first, cost-sensitive |

<div class="zh" markdown="1">

| 维度 | L2 MPLS VPN | L3 MPLS VPN | Internet + Overlay |
|---|---|---|---|
| 客户控制度 | 最高 | 中 | 高（覆盖层） |
| 运营商参与 | 仅传输 | 参与路由 | 仅传输 |
| QoS 保证 | 需合同 | 较好（有等级） | 基本没有 |
| 组播 | 客户自理 | 需 mVPN | 需隧道承载 |
| 加密 | 通常不需要（隔离） | 通常不需要 | **必需** |
| 拓扑灵活度 | 最高（二层邻接） | 受产品约束 | 高（overlay 决定） |
| 成本 | 高 | 中高 | 低 |
| 扩容速度 | 慢（工单） | 慢 | 快 |
| 运维复杂度 | 高（路由自己扛） | 低 | 中（隧道/控制器） |
| 适用 | 特殊二层需求、迁移 | 主流企业核心 | 多分支、云优先、成本敏感 |

</div>

---

## 2. WAN Edge Connectivity Design · 二、WAN 边缘连接设计

### Five Tiers of Single-Site Connectivity · 单站点连接形态的五个层级

![Five capabilities that make a site edge survivable and the failure-to-fix matrix](assets/fig/en17-19-site-edge.svg)

| Form | Redundancy dimension | Consequence of failure | Best fit |
|---|---|---|---|
| Single link, single CPE | None | Total outage | Non-critical branches |
| Dual link, single CPE (same carrier) | Link | CPE or carrier failure = total outage | Ordinary branches |
| Dual link, single CPE (dual carrier) | Link + carrier | **CPE failure = total outage** | Medium branches |
| Dual link, dual CPE (single carrier) | Link + device | Carrier failure = total outage | Medium branches |
| Dual link, dual CPE (dual carrier) | Everything | Only "shared last mile" risk remains | Critical sites/headquarters |

<div class="zh" markdown="1">

| 形态 | 冗余维度 | 故障后果 | 适用 |
|---|---|---|---|
| 单链路单 CPE | 无 | 全断 | 非关键分支 |
| 双链路单 CPE（同运营商） | 链路 | CPE 或运营商故障全断 | 一般分支 |
| 双链路单 CPE（双运营商） | 链路 + 运营商 | **CPE 故障全断** | 中型分支 |
| 双链路双 CPE（单运营商） | 链路 + 设备 | 运营商故障全断 | 中型分支 |
| 双链路双 CPE（双运营商） | 全部 | 仅剩"共享本地环路"风险 | 关键站点/总部 |

</div>

> 💡 **One test**: **before adding each layer of redundancy, ask whether the single point in the layer below has already been removed**. Dual links with a single CPE simply locks availability to one box.

<div class="zh" markdown="1">

> 💡 **一条判据**：**每加一层冗余，先问"上一层的单点是否已经消除"**。双链路但单 CPE，等于把可用性锁在设备上。

</div>

### The CPE's Role and Form Factor · CPE 的角色与形态

| Form | Who manages it | Advantages | Disadvantages |
|---|---|---|---|
| Carrier-managed CPE | The carrier | Clean demarcation, one phone call for faults | Slow change, limited features, no unified policy |
| Self-managed CPE | The enterprise | Unified policy, integrated with the internal network | Needs 24×7 capability, spares and out-of-band access |
| Co-managed | Both | The best of both | Responsibility boundaries must be written down |

<div class="zh" markdown="1">

| 形态 | 谁管理 | 优点 | 缺点 |
|---|---|---|---|
| 运营商托管 CPE | 运营商 | 分界清晰、故障只需打一个电话 | 变更慢、功能受限、无法统一策略 |
| 自管理 CPE | 企业 | 策略统一、与内网一体化 | 需要 7×24 能力、备件与远程带外 |
| 联合管理（co-managed） | 双方 | 兼顾 | 责任边界需写清 |

</div>

**The "survivability" features a CPE must have**:

<div class="zh" markdown="1">

**CPE 必配的"生存能力"**：

</div>

| Capability | Why |
|---|---|
| Out-of-band management (4G/management port) | Rescues you when a configuration error cuts you off |
| Zero-touch provisioning (ZTP) | Consistency and speed across many branches |
| Local survivability | Local switching or internet access continues when the hub is unreachable |
| Config rollback and scheduled backup | The first line of defence against change accidents |
| Traffic telemetry (NetFlow/IPFIX) | Without telemetry you cannot prove QoS is working |

<div class="zh" markdown="1">

| 能力 | 为什么 |
|---|---|
| 带外管理（4G/管理口） | 配置错误导致失联时能救回 |
| 零接触部署（ZTP） | 大规模分支的一致性与速度 |
| 本地存活（Survivability） | 与 Hub 失联时仍能本地交换/上网 |
| 配置回滚与定时备份 | 变更事故的第一道防线 |
| 流量遥测（NetFlow/IPFIX） | 没有遥测就无法证明 QoS 生效 |

</div>

### Failure Behaviour of CE-PE Routing Options · CE-PE 路由方式的失效行为

| Option | Link down | Carrier-side failure (link up) | Multihomed path selection |
|---|---|---|---|
| Static default | Remove the static (needs tracking) | **Not detected → black hole** | Impossible |
| Static + SLA tracking | Seconds | Probe failure triggers switchover | Coarse |
| eBGP | Session drops | Prefix withdrawal → switchover | Fine (attributes under control) |
| IGP (between your own CEs) | Neighbour drops | Depends on probing | Medium |

<div class="zh" markdown="1">

| 方式 | 链路 down | 运营商侧故障（链路 up） | 多宿主选路 |
|---|---|---|---|
| 静态默认 | 移除静态（需 track） | **不感知 → 黑洞** | 无法 |
| 静态 + SLA track | 秒级 | 探测失败可切换 | 粗粒度 |
| eBGP | 会话断 | 前缀撤销 → 切换 | 精细（属性可控） |
| IGP（客户自有 CE 间） | 邻居断 | 取决于探测 | 中 |

</div>

> ⚠️ **The biggest difference from the campus**: in the campus "link up" usually means "reachable"; in the WAN "link up" only means "the local optic or copper port is fine". **This is the fundamental reason WAN designs need dynamic routing or active probing.**

<div class="zh" markdown="1">

> ⚠️ **WAN 与园区最大的差别**：园区里"链路 up"通常意味着"能通"；WAN 里"链路 up"只意味着"本地光模块/电口正常"。**这是 WAN 设计必须用动态路由或主动探测的根本原因。**

</div>

### Three Mandatory Checks with Two Carriers · 双运营商时的三个必查项

| Item | What to check | What failure looks like |
|---|---|---|
| Physical diversity | Same duct, same exchange, same metro ring? | One excavation cuts both |
| Access diversity | Both delivered over "the same fibre"? | One cable fault cuts both |
| Billing and CIR | Committed rate and burst policy of both links | Congestion the moment you switch over |

<div class="zh" markdown="1">

| 项 | 要查什么 | 不合格的表现 |
|---|---|---|
| 物理多样性 | 是否同管道/同局房/同城域网 | 一次施工双断 |
| 接入方式多样性 | 是否都是"同一段光纤" | 光缆故障双断 |
| 计费与 CIR | 两条链路的承诺速率与突发策略 | 切换后立刻拥塞 |

</div>

---

## 3. Overlay Technologies · 三、覆盖技术

![GRE and IPsec compared over eight capabilities with three decision questions](assets/fig/en17-20-gre-vs-ipsec.svg)

### IPsec: The Most Basic — and the Easiest to Configure into Oblivion · IPsec：最基础也最容易"配错到不可维护"

| Form | Description | Best fit |
|---|---|---|
| Crypto map (traditional) | Interface-level policy, static peers | A few point-to-point links |
| SVTI (virtual tunnel interface) | Interface-based tunnel that can carry routing | Mainstream, recommended |
| IKEv2 | Cleaner, multiple SAs, MOBIKE | Always IKEv2 for anything new |
| DMVPN / FlexVPN | IPsec combined with mGRE or dynamic peers | Large scale |

<div class="zh" markdown="1">

| 形态 | 描述 | 适用 |
|---|---|---|
| Crypto Map（传统） | 接口级策略，静态对等 | 少量点对点 |
| SVTI（虚拟隧道接口） | 接口级隧道，可跑路由 | 主流，推荐 |
| IKEv2 | 更简洁、支持多 SA、MOBIKE | 新建一律 IKEv2 |
| DMVPN / FlexVPN | IPsec 与 mGRE/动态对等结合 | 大规模 |

</div>

**Mandatory items**:

<div class="zh" markdown="1">

**必配项**：

</div>

| Item | Why |
|---|---|
| NAT-T (UDP 4500) | Required to traverse NAT |
| `adjust-mss` / `ip mtu` | Prevents the big-packet black hole |
| PFS | Improves forward secrecy (slightly slower) |
| Key and certificate lifecycle | Manual PSKs do not scale → use PKI |
| Replay protection and liveness detection (DPD) | Detects "half-open" tunnels quickly |

<div class="zh" markdown="1">

| 项 | 说明 |
|---|---|
| NAT-T（UDP 4500） | 穿越 NAT 必需 |
| `adjust-mss` / `ip mtu` | 防大包黑洞 |
| PFS | 提升前向安全（性能略降） |
| 密钥与证书生命周期 | 手工 PSK 在大规模下不可维护 → 用 PKI |
| 重放与存活检测（DPD） | 快速发现"半开"隧道 |

</div>

### GRE: What Solves "The Things IPsec Cannot Carry" · GRE：解决"IPsec 不能传的东西"

| Capability | GRE | IPsec |
|---|---|---|
| Multicast | ✅ | ❌ |
| Non-IP protocols | ✅ | ❌ |
| Encryption | ❌ | ✅ |
| State/overhead | Stateless, 24 bytes | Stateful, 50–73 bytes |

<div class="zh" markdown="1">

| 能力 | GRE | IPsec |
|---|---|---|
| 组播 | ✅ | ❌ |
| 非 IP 协议 | ✅ | ❌ |
| 加密 | ❌ | ✅ |
| 状态/开销 | 无状态、24 字节 | 有状态、50–73 字节 |

</div>

**The two combinations, and why they differ (an exam favourite)**:

<div class="zh" markdown="1">

**两种组合的区别（常考）**：

</div>

| Combination | Structure | Characteristics |
|---|---|---|
| **GRE over IPsec** | GRE first, then the whole thing inside IPsec | Multicast and routing protocols ride inside GRE, IPsec protects the outside; **recommended** |
| IPsec over GRE | IPsec first, then wrapped in GRE | Rare, complex to configure, painful to troubleshoot |

<div class="zh" markdown="1">

| 组合 | 结构 | 特点 |
|---|---|---|
| **GRE over IPsec** | 先 GRE 封装，再整体走 IPsec | 组播/路由协议在 GRE 内，IPsec 保护外层；**推荐** |
| IPsec over GRE | 先 IPsec，再套 GRE | 少见、配置复杂、排障难 |

</div>

### DMVPN: The Three Phases and Design Points · DMVPN：三阶段与设计要点

```
                 +----------- Hub (mGRE + NHRP server) -----------+
                 |  Tunnel0: 172.16.0.1/24                         |
                 +---+------------------+------------------+-------+
          Spoke A (dynamic)   Spoke B (dynamic)   Spoke C (static)
          Tunnel 172.16.0.11  Tunnel 172.16.0.12  Tunnel 172.16.0.13
                 +------ NHRP resolution enables spoke-to-spoke ------+
```

<div class="zh" markdown="1">

```
                 ┌─────────── Hub（mGRE + NHRP Server）───────────┐
                 │  Tunnel0: 172.16.0.1/24                        │
                 └───┬───────────────┬───────────────┬───────────┘
          Spoke A（动态地址）   Spoke B（动态地址）   Spoke C（静态）
          Tunnel: 172.16.0.11   Tunnel: 172.16.0.12   Tunnel: 172.16.0.13
                 └────── NHRP 解析后可建立 Spoke-to-Spoke 隧道 ──────┘
```

</div>

| Design point | Recommendation |
|---|---|
| Phase choice | Need "summarisation + direct paths" → Phase 3; pure hub-spoke → Phase 1 |
| Routing protocol | IGP on the spokes (EIGRP/OSPF) with hub summarisation; or BGP |
| IPsec trigger | Establish on demand via NHRP (keeps the SA count down) |
| Spoke addressing | Dynamic addresses depend on NHRP — never assume they are fixed |
| Hub redundancy | Dual hubs on the same mGRE subnet plus routing preference |
| MTU/MSS | Configure on both hub and spokes |
| NAT traversal | Spokes behind NAT need NAT-T and the relevant `nhrp nat` configuration |

<div class="zh" markdown="1">

| 设计点 | 建议 |
|---|---|
| 阶段选择 | 需要"汇总 + 直连" → Phase 3；只有 hub-spoke → Phase 1 |
| 路由协议 | Spoke 侧 IGP（EIGRP/OSPF）+ Hub 汇总；或 BGP |
| IPsec 触发 | 按 NHRP 按需建立（节省 SA 数量） |
| Spoke 地址 | 动态地址必须依赖 NHRP，不能假设固定 |
| Hub 冗余 | 双 Hub + 同一 mGRE 网段 + 路由优先级 |
| MTU/MSS | Hub 与 Spoke 都要配 |
| NAT 穿透 | Spoke 在 NAT 后需 NAT-T + `nhrp nat` 相关配置 |

</div>

> 🎯 **The core value of DMVPN**: **O(n) hub configuration buys on-demand O(n²) direct connectivity.** What it solves is the scaling problem of configuration and operations — not the bandwidth problem.

<div class="zh" markdown="1">

> 🎯 **DMVPN 的核心价值**：**用 O(n) 的 Hub 配置，获得"按需 O(n²)"的直连能力。** 它解决的是"配置与运维的规模问题"，不是"带宽问题"。

</div>

### FlexVPN and GET VPN · FlexVPN 与 GET VPN

| Technology | Control plane | Tunnels | Best fit |
|---|---|---|---|
| FlexVPN | IKEv2 plus dynamic SVTI | One per peer | Large scale, per-peer policy and routing awareness |
| GET VPN | Group keys (GDOL/KS) | **No tunnels** (overlay rides a trusted private network) | Encryption over MPLS where any-to-any must work without changing routing |

<div class="zh" markdown="1">

| 技术 | 控制面 | 隧道 | 适用 |
|---|---|---|---|
| FlexVPN | IKEv2 + 动态 SVTI | 每对等一条 | 大规模、需要 per-peer 策略与路由感知 |
| GET VPN | 组密钥（GDOL/KS） | **无隧道**（overlay 在可信私网上） | MPLS 上加密、要求"任意两点直通"且不想改路由 |

</div>

> ⚠️ **GET VPN assumes "the underlay is trusted and fully meshed"**: it builds no tunnels and changes no routing, so it **cannot be used over the Internet** (unless combined with another encapsulation).

<div class="zh" markdown="1">

> ⚠️ **GET VPN 的前提是"底层可信且全互联"**：它不做隧道、不改路由，因此**不能用于 Internet 承载**（除非配合其他封装）。

</div>

### SD-WAN: Decoupling "Transport" from "Policy" · SD-WAN：把"传输"与"策略"解耦

| Capability | Traditional WAN | SD-WAN |
|---|---|---|
| Use of multiple transports | Active/standby (one link idles) | Real-time path selection per application or per quality |
| Where policy lives | On every device | Central controller (templated) |
| Deployment | Manual or scripted | ZTP |
| Application awareness | Limited (DSCP/port) | Application recognition plus SLA probes |
| Cloud access | Hairpins through headquarters | Local or regional cloud gateway |
| What it costs | Operations headcount | Controller dependency, vendor lock-in, more abstraction to troubleshoot |

<div class="zh" markdown="1">

| 能力 | 传统 WAN | SD-WAN |
|---|---|---|
| 多传输利用 | 主备（一条闲置） | 按应用/质量实时选路 |
| 策略位置 | 逐台设备 | 集中控制器（模板化） |
| 部署 | 手工/脚本 | ZTP |
| 应用感知 | 有限（DSCP/端口） | 应用识别 + SLA 探测 |
| 云接入 | 绕行总部 | 本地/区域云网关 |
| 代价 | 运维人力 | 控制器依赖、供应商锁定、排障抽象层变多 |

</div>

> 💡 **The test**: **many sites + multiple transports + demanding application experience → SD-WAN pays off clearly; few sites + one transport + stable applications → traditional routing is more direct.**

<div class="zh" markdown="1">

> 💡 **判据**：**站点多 + 多传输 + 应用体验要求高 → SD-WAN 收益明显；站点少 + 单传输 + 稳定业务 → 传统路由更直接。**

</div>

### Overlay Technologies Side by Side (Original Table 17-3 Plus Additions) · 覆盖技术综合对比（原书 Table 17-3 + 补充）

| Technology | Tunnel count | Multicast | Encryption | Dynamic addressing | Direct spoke paths | Operational complexity |
|---|---|---|---|---|---|---|
| Point-to-point IPsec | O(n²) when fully meshed | ❌ | ✅ | ❌ | ✅ | Low (few) / high (many) |
| GRE | O(n²) | ✅ | ❌ | ❌ | ✅ | Medium |
| GRE over IPsec | O(n²) | ✅ | ✅ | ❌ | ✅ | Medium-high |
| DMVPN | O(n) on the hub | ✅ (in Phase 3) | ✅ | ✅ | ✅ (P2/P3) | Medium-high |
| FlexVPN | O(n) | Limited | ✅ | ✅ | ✅ | High |
| GET VPN | 0 | ✅ | ✅ | — | ✅ (underlay is fully reachable) | Medium |
| SD-WAN | O(n) via controllers | Implementation-dependent | ✅ | ✅ | ✅ | Medium (abstraction layer) |

<div class="zh" markdown="1">

| 技术 | 隧道数 | 组播 | 加密 | 动态地址 | 直连 | 运维复杂度 |
|---|---|---|---|---|---|---|
| IPsec 点对点 | O(n²) 全互联 | ❌ | ✅ | ❌ | ✅ | 低（少量）/ 高（大量） |
| GRE | O(n²) | ✅ | ❌ | ❌ | ✅ | 中 |
| GRE over IPsec | O(n²) | ✅ | ✅ | ❌ | ✅ | 中高 |
| DMVPN | O(n)（Hub） | ✅（Phase 3 可） | ✅ | ✅ | ✅（P2/P3） | 中高 |
| FlexVPN | O(n) | 有限 | ✅ | ✅ | ✅ | 高 |
| GET VPN | 0 | ✅ | ✅ | — | ✅（底层全通） | 中 |
| SD-WAN | O(n)（控制器） | 视实现 | ✅ | ✅ | ✅ | 中（抽象层） |

</div>

---

## 4. WAN Virtualisation: Multi-VRF CE, CSC and Inter-AS · 四、WAN 虚拟化：Multi-VRF CE、CSC 与 Inter-AS

![Three layers of WAN virtualisation and the three Inter-AS options](assets/fig/en17-21-virtualisation.svg)

### Multi-VRF CE (VRF-Lite)

The CE keeps several VRFs but **runs no MP-BGP towards the carrier**; instead each VRF maps to a "logical link" through a subinterface/802.1Q tag, and the carrier side terminates it in a matching VRF.

<div class="zh" markdown="1">

CE 上维护多个 VRF，但**不向运营商跑 MP-BGP**，而是用子接口/802.1Q 把每个 VRF 映射到一个"逻辑链路"，运营商侧用 VRF 承接。

</div>

```
        +-- CE (VRFs: production / office / guest) --+
        |  Gi0/0.10  -> VRF production  -------------+-- PE (VRF production)
        |  Gi0/0.20  -> VRF office      -------------+-- PE (VRF office)
        |  Gi0/0.30  -> VRF guest       -------------+-- PE (VRF guest)
        +-------------------------------------------+
```

<div class="zh" markdown="1">

```
        ┌── CE（VRF: 生产 / 办公 / 访客）──┐
        │  Gi0/0.10  → VRF 生产  ─────────┼── PE（VRF 生产）
        │  Gi0/0.20  → VRF 办公  ─────────┼── PE（VRF 办公）
        │  Gi0/0.30  → VRF 访客  ─────────┼── PE（VRF 访客）
        └─────────────────────────────────┘
```

</div>

| Advantages | Disadvantages |
|---|---|
| The CE needs no MP-BGP or advanced VRF features | Every extra segment means another subinterface/circuit |
| Clean segmentation boundary (physical/subinterface level) | Subinterface count limits; the carrier side must match |
| Supports overlapping addresses | No global any-to-any; each segment is designed separately |
| Pairs naturally with firewalls and service chaining | Scale bounded by segments × sites |

<div class="zh" markdown="1">

| 优点 | 缺点 |
|---|---|
| CE 不需要 MP-BGP/VRF 高级特性 | 每增加一个分段就多一条子接口/电路 |
| 分段边界清晰（物理/子接口级） | 子接口数量限制、运营商侧需同步配置 |
| 地址重叠场景可支持 | 无全局 any-to-any，需逐段设计 |
| 与防火墙/服务链配合直观 | 扩展性受"段数 × 站点数"约束 |

</div>

> 💡 **When to use it**: **few segments (2–5), many sites, and no appetite for MP-BGP on the CE** → Multi-VRF CE is the best value for money.

<div class="zh" markdown="1">

> 💡 **适用判据**：**分段少（2–5 个）、站点多、且不想在 CE 上跑 MP-BGP** → Multi-VRF CE 是性价比最高的方案。

</div>

### CSC (Carrier Supporting Carrier)

A "carrier's carrier": one carrier (the customer carrier) treats another carrier's MPLS network as its own backbone and keeps selling VPN services from its own PEs.

<div class="zh" markdown="1">

"运营商的运营商"：一家运营商（客户运营商）把另一家（承载运营商）的 MPLS 网络当作自己的骨干，在自己的 PE 上继续提供 VPN 服务。

</div>

| Scenario | Description |
|---|---|
| Wholesale/multinational | A local carrier with no global backbone rents capacity from a tier-1 carrier |
| Regional expansion | Rapid coverage of many countries without building infrastructure |
| Key design points | **Label stack** (outer transport plus inner VPN), MTU (two labels plus customer encapsulation), QoS mapping (aligning the two carriers' classes) |

<div class="zh" markdown="1">

| 场景 | 说明 |
|---|---|
| 批发/跨国 | 本地运营商无全球骨干，租用一级运营商骨干 |
| 跨区域扩展 | 快速覆盖多国家/地区，无需自建 |
| 关键设计点 | **标签栈**（外层承载 + 内层 VPN）、MTU（双层标签 + 客户封装）、QoS 映射（两家等级对齐） |

</div>

> ⚠️ **The hidden cost of CSC is MTU and QoS alignment**: with two labels stacked the usable MTU shrinks, and if the customer already runs GRE/IPsec the MSS must be recalculated.

<div class="zh" markdown="1">

> ⚠️ **CSC 的隐性成本是 MTU 与 QoS 对齐**：两层标签叠加后可用 MTU 变小，若客户侧已有 GRE/IPsec，必须重新核算 MSS。

</div>

### The Three Inter-AS Options (Essential for Large MPLS VPNs) · Inter-AS 的三种选项（大规模 MPLS VPN 必知）

| Option | Method | Advantages | Disadvantages |
|---|---|---|---|
| **A** | "Back-to-back VRF subinterfaces" between ASes | Simple, strong isolation | Configured per VPN, worst scalability |
| **B** | ASBRs exchange VPNv4 routes (MP-eBGP) but **no VPN labels** | Moderate scale, ASBRs need not know every VRF | ASBRs must hold VPN routes |
| **C** | ASBRs exchange only **labelled IPv4 routes**; VPN routes go end to end (multihop MP-eBGP) | Best scalability, light ASBR load | Complex configuration, needs RRs and label forwarding |

<div class="zh" markdown="1">

| 选项 | 方式 | 优点 | 缺点 |
|---|---|---|---|
| **A** | 每个 AS 之间用"背靠背 VRF 子接口" | 简单、隔离强 | 逐 VPN 配置，扩展性最差 |
| **B** | ASBR 之间交换 VPNv4 路由（MP-eBGP），**不交换 VPN 标签** | 中等扩展、ASBR 不需知道所有 VRF | ASBR 需保存 VPN 路由 |
| **C** | ASBR 之间只交换**带标签的 IPv4 路由**，VPN 路由端到端（多跳 MP-eBGP） | 扩展性最好、ASBR 负载轻 | 配置复杂、需 RR 与标签转发 |

</div>

> 🎯 **The test**: **few VPNs and few ASes → A; medium scale → B; large scale/multinational → C.** Questions of the form "A or B?" are almost always decided by VPN count × AS count.

<div class="zh" markdown="1">

> 🎯 **判据**：**VPN 数量少、AS 少 → A；中等规模 → B；大规模/跨国 → C。** 面对「选 A 还是选 B」这类问题，结论几乎都由"VPN 数量 × AS 数量"决定。

</div>

### The Three Layers of WAN Virtualisation (Do Not Mix Them Up) · WAN 虚拟化的三个层次（别混）

| Layer | Mechanism | What it solves |
|---|---|---|
| **Transport virtualisation** | MPLS VPN / VRF / VLAN | Several logical networks over one physical network |
| **Device virtualisation** | Multi-VRF CE, virtual CPE (vCPE) | One device serving several services or tenants |
| **Function virtualisation** | NFV (vFW/vRouter/vWOC) | Decoupling function from hardware, elastic deployment |

<div class="zh" markdown="1">

| 层次 | 手段 | 解决什么 |
|---|---|---|
| **传输虚拟化** | MPLS VPN / VRF / VLAN | 同一物理网络承载多张逻辑网 |
| **设备虚拟化** | Multi-VRF CE、虚拟 CPE（vCPE） | 一台设备服务多个业务/租户 |
| **功能虚拟化** | NFV（vFW/vRouter/vWOC） | 功能与硬件解耦、弹性部署 |

</div>

---

## 5. WAN Design Options by Scale · 五、WAN 设计选项（按规模）

![Four site tiers with their standard kits and the redundancy each covers](assets/fig/en17-22-scale-tiers.svg)

The original book gives a four-tier model based on site size and business criticality. In practice, express it as **site tiers plus a standard kit per tier** rather than designing each site individually.

<div class="zh" markdown="1">

原书按"站点规模与业务关键度"给出四级模型。落地时建议用"**站点分级 + 每级的标准套件**"来表达，而不是"每站点单独设计"。

</div>

### The Standard Kit for Each of the Four Tiers · 四个规模级别的标准套件

| Tier | Site characteristics | Transport | Redundancy | Routing | Typical technology |
|---|---|---|---|---|---|
| **L1 single link** | Small, non-critical branches | One MPLS or Internet circuit | None (optional 4G backup) | Static/default | Single CPE |
| **L2 dual link, single CPE** | Medium branches, ordinary business | MPLS + Internet (or two ISPs) | Link level | Static + SLA / eBGP | Single CPE plus tunnels |
| **L3 dual link, dual CPE** | Large branches/regional centres | Two carriers/two transports | Link + device | eBGP + IGP | Dual CPE plus DMVPN/SD-WAN |
| **L4 regional WAN core** | HQ/regional hub/DC | Multiple transports (MPLS + Internet + dedicated) | Full redundancy plus N−1 capacity | BGP with hierarchical summarisation | WAN core plus regional hubs plus cloud on-ramps |

<div class="zh" markdown="1">

| 级别 | 站点特征 | 传输 | 冗余 | 路由 | 典型技术 |
|---|---|---|---|---|---|
| **L1 单链路** | 小型分支、非关键 | 单条 MPLS 或 Internet | 无（可选 4G 备份） | 静态/默认 | 单 CPE |
| **L2 双链路单 CPE** | 中型分支、一般业务 | MPLS + Internet（或双 ISP） | 链路级 | 静态 + SLA / eBGP | 单 CPE + 隧道 |
| **L3 双链路双 CPE** | 大型分支/区域中心 | 双运营商/双传输 | 链路 + 设备 | eBGP + IGP | 双 CPE + DMVPN/SD-WAN |
| **L4 区域 WAN 核心** | 总部/区域 Hub/DC | 多传输（MPLS + Internet + 专线） | 全冗余 + N−1 容量 | BGP + 分层汇总 | WAN 核心 + 区域 Hub + 云 on-ramp |

</div>

### L1: Single-Link Branch (Minimum Viable) · L1：单链路分支（最小可用）

| Item | Design |
|---|---|
| Transport | A single circuit (fibre broadband preferred; MPLS optional for critical sites) |
| Backup | 4G/5G (floating default with SLA tracking) |
| Routing | Default route plus local VLANs |
| Security | Local firewall/UTM or cloud security |
| Egress | Centralised exit or local DIA, depending on the application |

<div class="zh" markdown="1">

| 项 | 设计 |
|---|---|
| 传输 | 单条（优先光纤宽带；关键站点可选 MPLS） |
| 备份 | 4G/5G（浮动默认 + SLA track） |
| 路由 | 默认路由 + 本地 VLAN |
| 安全 | 本地防火墙/UTM 或云安全 |
| 出口 | 集中出口或本地 DIA（按业务） |

</div>

### L2: Dual Link, Single CPE · L2：双链路单 CPE

| Item | Design |
|---|---|
| Transport | MPLS (primary) + Internet (backup), or two ISPs |
| Routing | eBGP if the carrier supports it, otherwise static + SLA |
| Overlay | IPsec/GRE over the Internet when encryption is required |
| Key targets | Switchover ≤10 s; backup capacity ≥ 60% of peak |

<div class="zh" markdown="1">

| 项 | 设计 |
|---|---|
| 传输 | MPLS（主）+ Internet（备），或双 ISP |
| 路由 | eBGP（若运营商支持）或静态 + SLA |
| 覆盖 | 需加密时用 IPsec/GRE over Internet |
| 关键指标 | 切换 ≤10 s、备链路容量 ≥ 峰值 60% |

</div>

### L3: Dual Link, Dual CPE · L3：双链路双 CPE

| Item | Design |
|---|---|
| Transport | Two carriers with physically separated paths |
| Devices | Dual CPE (VRRP or active/active routing) each facing a different carrier |
| Routing | eBGP to each carrier; IGP inside the enterprise |
| Overlay | DMVPN (Phase 3) or SD-WAN |
| Key targets | Single device or single carrier failure converges in ≤5 s |

<div class="zh" markdown="1">

| 项 | 设计 |
|---|---|
| 传输 | 两家运营商，物理路径分离 |
| 设备 | 双 CPE（VRRP/路由双活），分别接不同运营商 |
| 路由 | eBGP 到各自运营商；内网 IGP |
| 覆盖 | DMVPN（Phase 3）或 SD-WAN |
| 关键指标 | 单设备/单运营商故障 ≤5 s 收敛 |

</div>

### L4: Regional WAN Core · L4：区域 WAN 核心

```
        +------------ Global/national WAN core (multi-transport, multi-carrier) ------------+
        |                                                                                   |
   +----+-----+      +----------+      +----------+      +----------+
   | Regional |      | Regional |      | Regional |      | Cloud    |
   | hub A    |      | hub B    |      | hub C    |      | on-ramp  |
   | (dual CE)|      | (dual CE)|      | (dual CE)|      | (leased/ |
   +----+-----+      +----+-----+      +----+-----+      |  IPsec)  |
        |                 |                 |            +----+-----+
   L1/L2/L3 branches  branch cluster   branch cluster      SaaS/IaaS
```

<div class="zh" markdown="1">

```
        ┌──────────── 全球/全国 WAN 核心（多传输、多运营商）────────────┐
        │                                                                │
   ┌────┴─────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
   │ 区域 Hub A│      │ 区域 Hub B│      │ 区域 Hub C│      │ 云 on-ramp│
   │ (双 CPE)  │      │ (双 CPE)  │      │ (双 CPE)  │      │ (专线/IPsec)│
   └────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     L1/L2/L3 分支      分支集群          分支集群            SaaS/IaaS
```

</div>

| Design point | Requirement |
|---|---|
| Topology | Regional hubs in a hierarchy; avoid a single global hub |
| Summarisation | Each region summarises towards the core; the core holds only regional prefixes |
| Multicast | Enable mVPN or tunnel multicast only in the regions that need it |
| Cloud access | Regional hubs reach the cloud locally (dedicated line or SD-WAN cloud gateway) |
| Capacity | Core links at N−1; hub encrypted throughput compliant |
| Operations | Unified policy templates + tiered alerting + end-to-end probes (at least two probes per region) |

<div class="zh" markdown="1">

| 设计点 | 要求 |
|---|---|
| 拓扑 | 区域 Hub 分层，避免"全球单 Hub" |
| 汇总 | 每个区域汇总后向核心宣告，核心只保留区域前缀 |
| 组播 | 仅在需要的区域启用 mVPN/隧道组播 |
| 云接入 | 区域 Hub 就近接入云（专线或 SD-WAN 云网关） |
| 容量 | 核心链路 N−1；Hub 加密后吞吐达标 |
| 运维 | 统一策略模板 + 分级告警 + 端到端探测（每区域至少 2 个探针） |

</div>

---

## 6. WAN QoS and Performance · 六、WAN QoS 与性能

### The Classification Model: Six Classes Are Enough; Eight Is Usually Overdesign · 分类模型：6 类足够，8 类通常是过度设计

| Class | Typical traffic | Queue policy | Bandwidth guarantee |
|---|---|---|---|
| Voice | VoIP, conference audio | LLQ (priority queue) plus policing | ~100 kbps per call (G.711 with overhead) |
| Interactive video | Video conferencing | Low-latency queue plus guaranteed bandwidth | 1–4 Mbps per stream |
| Business critical | ERP, trading | Guaranteed bandwidth plus WRED | Per application peak |
| Bulk | Backup, replication | Remaining bandwidth, preemptable | No guarantee, rate-limited |
| Default | Web, mail | Fair queueing | Whatever is left |
| Network control | Routing protocols, BFD | Small share at high priority | A small fixed slice (so it never starves) |

<div class="zh" markdown="1">

| 类别 | 典型业务 | 队列策略 | 带宽保障 |
|---|---|---|---|
| 语音 | VoIP、会议音频 | LLQ（优先队列）+ 限速 | 每通话 ~100 kbps（G.711，含开销） |
| 交互视频 | 视频会议 | 低时延队列 + 带宽保障 | 每路 1–4 Mbps |
| 关键业务 | ERP、交易 | 带宽保障 + WRED | 按业务峰值 |
| 批量 | 备份、复制 | 剩余带宽 + 可被抢占 | 无保障，可限速 |
| 默认 | Web、邮件 | 公平队列 | 剩余 |
| 网络控制 | 路由协议、BFD | 小比例高优先级 | 固定小带宽（防饿死） |

</div>

> ⚠️ **Policing voice is a trap**: LLQ must have `police` configured, otherwise a large volume of traffic "marked as voice" starves the other queues. **Give voice a physically sensible ceiling (say 30% of the link).**

<div class="zh" markdown="1">

> ⚠️ **限速语音是个陷阱**：LLQ 必须配 `police`，否则大量"标记为语音"的流量会饿死其他队列。**给语音配一个"物理上合理"的上限（如 30% 链路）**。

</div>

### Where Shaping and Policing Belong · 整形（Shaping）与丢弃（Policing）的位置

| Location | Action | Why |
|---|---|---|
| **CE uplink egress** | Shape to the CIR (slightly below the contract, e.g. 95%) | The carrier's policer drops overspeed traffic; shaping is more controllable than being dropped |
| Carrier side | Policer per contract | Outside your control |
| Receiving side | Usually unnecessary | Congestion does not happen there |

<div class="zh" markdown="1">

| 位置 | 动作 | 原因 |
|---|---|---|
| **CE 上行出口** | 整形到 CIR（略低于合同值，如 95%） | 运营商侧 policer 会丢超速流量，整形比被丢更可控 |
| 运营商侧 | 按合同 policer | 你无法控制 |
| 接收侧 | 通常不需要 | 拥塞不在接收侧 |

</div>

```
! CE uplink shaping (illustrative)
policy-map SHAPE-WAN
 class class-default
  shape average 95000000          ! contract 100M, shape to 95M
  service-policy QUEUE-OUT
```

<div class="zh" markdown="1">

```
! CE 上行整形示例（思路）
policy-map SHAPE-WAN
 class class-default
  shape average 95000000          ! 合同 100M，整形到 95M
  service-policy QUEUE-OUT
```

</div>

> 🎯 **One rule of thumb**: **there is exactly one "shaping point" in the WAN — your own egress.** Every design that hopes the carrier will be nicer to you is weaker than shaping your own traffic below the contract.

<div class="zh" markdown="1">

> 🎯 **一条经验**：**WAN 里"整形点"只有一个：你的出口。** 所有"希望运营商对我好一点"的设计，都不如"自己先把流量整形到合同以内"。

</div>

### Latency, Jitter and What TCP Actually Does · 时延、抖动与 TCP 的真实关系

![The bandwidth-delay product, the 64 kilobyte window ceiling and the symptom-to-cause table](assets/fig/en17-23-tcp-performance.svg)

| Symptom | Cause | Mitigation |
|---|---|---|
| Single-flow throughput will not rise | BDP limit (window / RTT) | Window scaling, multiple flows, front-end caching or acceleration |
| Video pixelation | Jitter plus loss | Jitter buffer, priority queue, FEC |
| Voice "robotic" artefacts | Loss plus jitter | LLQ + shaping + link-quality probing |
| Large files slow, small files fast | Per-flow slow start plus RTT | Concurrent connections, CDN/edge caching |

<div class="zh" markdown="1">

| 现象 | 原因 | 缓解 |
|---|---|---|
| 单流吞吐上不去 | BDP 限制（窗口 / RTT） | 窗口缩放、多流、前置缓存/加速 |
| 视频花屏 | 抖动 + 丢包 | 抖动缓冲、优先队列、FEC |
| 语音"机器人声" | 丢包 + 抖动 | LLQ + 整形 + 链路质量探测 |
| 大文件慢、小文件快 | 每流慢启动 + RTT | 并发连接、CDN/边缘缓存 |

</div>

**Estimating the BDP**:

<div class="zh" markdown="1">

**BDP 估算**：

</div>

```
BDP = bandwidth x RTT
Example: 100 Mbps x 80 ms = 8 Mb ~ 1 MB in flight
If a single flow has only a 64 KB window -> ceiling ~ 6.5 Mbps (no matter how much bandwidth exists)
```

<div class="zh" markdown="1">

```
BDP = 带宽 × RTT
例：100 Mbps × 80 ms = 8 Mb ≈ 1 MB 在途
若单流窗口只有 64 KB → 单流上限 ≈ 6.5 Mbps（无论带宽多大）
```

</div>

### Three Ways to Deliver Multicast Across the WAN · 组播跨 WAN 的三种落地方式

| Method | Requires | Replication point | Best fit |
|---|---|---|---|
| mVPN (carrier) | Carrier support, cost | PE | Many sites, few sources/many receivers, needs SLA |
| GRE/DMVPN tunnel plus PIM | Tunnels that carry multicast | Hub | Medium site count, under your control |
| Application-layer distribution | No network requirement | Server/CDN | Video training, software distribution |

<div class="zh" markdown="1">

| 方式 | 需要 | 复制点 | 适用 |
|---|---|---|---|
| mVPN（运营商） | 运营商支持、费用 | PE | 多站点、源少收多、需 SLA |
| GRE/DMVPN 隧道 + PIM | 隧道支持组播 | Hub | 站点中等、可控 |
| 应用层分发 | 无网络要求 | 服务器/CDN | 视频培训、软件分发 |

</div>

> 💡 **The test**: **only when "real-time + many receivers + network under your control" all hold is network multicast worth it**; otherwise application-layer distribution is less trouble.

<div class="zh" markdown="1">

> 💡 **判据**：**"实时性 + 多接收者 + 网络可控" 三者同时成立才值得网络组播**；否则应用层分发更省事。

</div>

---

## 7. WAN Routing Design · 七、WAN 路由设计

![Three topologies with their routing models, the four hub-spoke questions and redistribution boundaries](assets/fig/en17-24-routing-design.svg)

### Matching Topology to Routing · 三种拓扑与路由的对应关系

| Topology | Routing approach | Advantages | Disadvantages |
|---|---|---|---|
| **Hub-spoke** | Spokes default to the hub; the hub summarises towards spokes | Simple, centralised policy, low cost | Spoke-to-spoke traffic detours, hub bottleneck |
| **Partial mesh (regional hubs)** | Hierarchical summarisation plus inter-region BGP | Balances cost and experience | Complex design, many summarisation points |
| **Full mesh (any-to-any)** | MP-BGP (carrier L3VPN) or iBGP with RRs | Optimal paths, no detours | High cost, large tables, large failure domain |

<div class="zh" markdown="1">

| 拓扑 | 路由方式 | 优点 | 缺点 |
|---|---|---|---|
| **Hub-Spoke** | Spoke 默认路由 → Hub；Hub 汇总 → Spoke | 简单、策略集中、成本低 | Spoke 间流量绕行、Hub 瓶颈 |
| **部分网状（区域 Hub）** | 分层汇总 + 区域间 BGP | 平衡成本与体验 | 设计复杂、汇总点多 |
| **全互联（Any-to-Any）** | MP-BGP（运营商 L3VPN）或 iBGP + RR | 最优路径、无绕行 | 成本高、路由表大、故障域大 |

</div>

### The Four Questions Hub-Spoke Must Answer · Hub-Spoke 的四个必答问题

| Question | Wrong answer | Right answer |
|---|---|---|
| Do spokes need direct paths? | "Yes, build a full mesh" | Look at the traffic matrix first: only above ~30% east-west is direct connectivity (DMVPN Phase 3 / SD-WAN) worth it |
| Does hub summarisation break direct paths? | "No" | In Phase 2 it does; "summarise + direct" requires Phase 3 |
| Is a default route enough on the spokes? | "Yes" | Not with dual uplinks (you need per-prefix or per-attribute selection) |
| What if the hub fails? | "We have a backup hub" | The backup hub needs the same subnet, the same policy and a clear preference, and the spokes must detect the change |

<div class="zh" markdown="1">

| 问题 | 错误答案 | 正确答案 |
|---|---|---|
| Spoke 间要直连吗？ | "要，配全互联" | 先看流量矩阵：>30% 东西向才考虑直连（DMVPN Phase 3 / SD-WAN） |
| Hub 汇总会不会破直连？ | "不会" | Phase 2 会；要"汇总 + 直连"必须 Phase 3 |
| Spoke 用默认路由够吗？ | "够" | 双上行时不够（需按前缀/属性选路） |
| Hub 故障怎么办？ | "有备份 Hub" | 备份 Hub 需同网段/同策略/优先级明确，且 Spoke 要能感知 |

</div>

### The Boundaries of Summarisation and Redistribution · 汇总与重分发的边界

| Location | Action | Risk |
|---|---|---|
| Regional hub → core | Summarise regional prefixes | Suboptimal paths from the summarisation point (detours during failures) |
| Core → regional hub | Advertise only a default or a summary | Regions lose detail and troubleshooting gets harder |
| MPLS ↔ Internet | **Never redistribute in both directions** | Loops, suboptimal paths, leaking |
| IGP ↔ BGP | One direction plus a prefix whitelist | Full-table leaks, routing churn |

<div class="zh" markdown="1">

| 位置 | 动作 | 风险 |
|---|---|---|
| 区域 Hub → 核心 | 汇总区域前缀 | 汇总点的次优路径（故障时绕行） |
| 核心 → 区域 Hub | 只发默认或汇总 | 区域看不到细节，排障变难 |
| MPLS ↔ Internet | **禁止双向重分发** | 环路、次优、泄漏 |
| IGP ↔ BGP | 单向 + 前缀白名单 | 全表泄漏、路由震荡 |

</div>

> ⚠️ **An iron rule**: **redistribution in the WAN must be one-directional, whitelisted and tagged**. Two-way redistribution is the classic source of "it appears to work, but nobody can explain it when it breaks".

<div class="zh" markdown="1">

> ⚠️ **一条铁律**：**WAN 上的重分发必须"单向 + 白名单 + 打标签"**。双向重分发是"看起来能用、故障时无法解释"的典型来源。

</div>

### The Four Uses of BGP in the WAN · BGP 在 WAN 里的四个用途

| Use | Description |
|---|---|
| Multihomed path selection | Attribute-based selection with two carriers (as in Chapter 16) |
| PE-CE for carrier L3VPN | Exchanging site prefixes with the carrier |
| Large-scale iBGP (any-to-any) | RRs carrying site routes for the whole network |
| Cloud access route exchange | Exchanging VPC/VNet prefixes with a cloud gateway |

<div class="zh" markdown="1">

| 用途 | 说明 |
|---|---|
| 多宿主选路 | 双运营商时按属性选路（与第 16 章一致） |
| 运营商 L3VPN 的 PE-CE | 与运营商交换站点前缀 |
| 大规模 iBGP（Any-to-Any） | 用 RR 承载全网站点路由 |
| 云接入路由交换 | 与云网关交换 VPC/VNet 前缀 |

</div>

> 💡 **Scaling test**: **fewer than 50 sites in a hub-spoke topology → an IGP is enough; more than 100 sites or any-to-any → BGP with RRs.**

<div class="zh" markdown="1">

> 💡 **规模判据**：**站点 <50 且拓扑为 hub-spoke → IGP 足够；站点 >100 或需 any-to-any → BGP + RR。**

</div>

---

## 8. Migration: From Traditional WAN to MPLS L3VPN (Original-Book Topic) · 八、迁移：从传统 WAN 到 MPLS L3VPN（原文专题）

![The overlap state during a WAN migration with two clouds, two defaults and a backdoor link](assets/fig/en17-25-migration.svg)

> The book devotes a dedicated section to migration right after WAN virtualisation, for a very direct reason: **WAN projects rarely fail because the target architecture is wrong; they fail because nobody designed the intermediate state**. If the design deliverable contains only the end-state topology, the implementation team will invent its own migration order, and once that order is wrong the problems stay in production as "intermittent loops and suboptimal paths".

<div class="zh" markdown="1">

> 原书在 WAN 虚拟化之后专门用一节讲迁移，理由很直接：**WAN 项目的失败多数不在"目标架构不对"，而在"中间态没人设计"**。设计交付物里如果只有终态拓扑，实施团队就会自己发明迁移顺序，而迁移顺序一旦错了，问题会以"间歇性环路/次优"的形式留到生产。

</div>

### Why Migration Is a Design Problem, Not an Implementation Problem · 为什么迁移是设计问题，不是实施问题

The book's judgement: designers pour all their energy into the "end state", but a good design must include **the strategy that takes you from today's state to that end state**; and the migration plan must answer one technical question — **when only part of the network has been migrated, how do the control-plane protocols and the applications interact?**

<div class="zh" markdown="1">

原文的判断：设计者常把精力全放在"终态"，但一份好的设计必须包含**从现状走到终态的策略**；而且迁移计划要回答一个技术问题——**当网络只迁移了一部分时，控制面协议与应用之间如何交互**。

</div>

| What delivering only the end state causes | How it shows up |
|---|---|
| Dual-point redistribution appears in the intermediate state | The backdoor link and MPLS both advertise, producing loops or suboptimal paths |
| The default-route origin drifts | Halfway through, some sites still default towards a decommissioned hub |
| Summarisation points break mid-migration | A black hole opens between migrated and non-migrated areas |
| Administrative distance decides the path | Which path "wins" is decided by AD by accident rather than by design |
| Long-lived sessions are cut | Voice/video/ERP sessions break, and the business finds the problem before technical acceptance does |

<div class="zh" markdown="1">

| 只交终态的后果 | 具体表现 |
|---|---|
| 中间态出现双点重分发 | backdoor 链路与 MPLS 同时宣告，路由环路 / 次优 |
| 默认路由生成点漂移 | 迁移到一半，部分站点默认指向失效的旧 Hub |
| 汇总点在中间态失效 | 迁移区与非迁移区之间出现黑洞 |
| AD 变化决定选路 | 新旧路径"谁赢"由管理距离偶然决定，而不是由设计决定 |
| 长连接被切换打断 | 语音/视频/ERP 会话中断，业务先于技术验收发现问题 |

</div>

> 🎯 **Design conclusion**: the WAN review checklist must contain a page called **"intermediate-state topology"** — not a list of steps, but a routing and traffic diagram of "the network at 50% migrated".

<div class="zh" markdown="1">

> 🎯 **设计结论**：WAN 方案评审清单里必须有"**迁移中间态拓扑**"这一页——不是步骤清单，而是一张"迁移到 50% 时的路由与流量图"。

</div>

### The Six Rules of Thumb the Book Gives · 原文给出的六条经验规则

| # | Rule | The trap behind it |
|---|---|---|
| 1 | **Large scale, many branches, many exits → always migrate in phases** | A one-shot cutover is a one-shot network-wide risk with the highest rollback cost |
| 2 | In planning, analyse each site's **logical and physical architecture** first: backdoor links, OSPF areas, BGP AS numbers | A backdoor link becomes "a second redistribution point" after migration |
| 3 | For L3VPN, verify how the **PE-CE routing protocol** integrates with the existing routing design so service is not interrupted; **BGP is the most common choice, and often the only one the carrier offers** | With OSPF as PE-CE, areas and LSA types get constrained by carrier policy |
| 4 | Be explicit about **who generates the default route**: locally at the branch, or learned from the MPLS cloud | When defaults exist in two places, AD decides, and failures become inexplicable |
| 5 | Find every **summarisation point** — summaries during migration easily create suboptimal paths or black holes | When the two sides of a summary are at different migration stages, detail routes get eaten |
| 6 | For L2VPN, confirm the **topology** the carrier provides (hub-spoke / full mesh / partial mesh) and the real post-migration traffic path | Moving from FR hub-spoke to VPLS full mesh changes broadcast and STP behaviour completely |

<div class="zh" markdown="1">

| # | 规则 | 背后的坑 |
|---|---|---|
| 1 | **大规模、多分支、多出口 → 一律分阶段迁移** | 一次性切换 = 一次性全网风险，回退代价最高 |
| 2 | 规划阶段先分析**站点的逻辑与物理架构**：backdoor 链路、OSPF 区域划分、BGP AS 编号 | backdoor 链路在迁移后变成"第二个重分发点" |
| 3 | L3VPN 要核对 **PE-CE 路由协议**与现有路由设计的整合方式，确保迁移后不中断业务；**BGP 是最常见、也常是运营商唯一能提供的选择** | 用 OSPF 做 PE-CE 时，区域与 LSA 类型会被运营商策略限制 |
| 4 | 明确**默认路由由谁生成**：分支本地生成，还是从 MPLS 云里学 | 默认路由"两处都有"时，选路由 AD 决定，故障时不可解释 |
| 5 | 找出所有**汇总点**——迁移期汇总容易造成次优路由或汇总黑洞 | 汇总点两侧处于不同迁移阶段时，细节路由被吃掉 |
| 6 | L2VPN 要确认运营商提供的**拓扑**（hub-spoke / full mesh / partial mesh）以及迁移后流量的实际路径 | 从 FR hub-spoke 换到 VPLS full-mesh，广播域与 STP 行为全变 |

</div>

### The Book's Case: An International Media Company (Frame Relay → MPLS L3VPN) · 原文案例：国际媒体公司（Frame Relay → MPLS L3VPN）

**Current state**: two regions, the United States and Europe, each with its own **Frame Relay hub-and-spoke** cloud; the two regional hubs are joined by a carrier Ethernet **VLL (L2VPN)**. Video and broadcast systems had just moved from **TDM to IP**, after which video quality dropped — loss and latency rose.

<div class="zh" markdown="1">

**现状**：美国、欧洲两个区域，各自一个 **Frame Relay hub-and-spoke** 云；两个区域的 Hub 之间通过运营商以太网 **VLL（L2VPN）**互联。视频与广播系统刚从 **TDM 迁到 IP**，随后视频质量下降——丢包与时延上升。

</div>

**Root cause (as the book attributes it)**:

<div class="zh" markdown="1">

**根因（原文归因）**：

</div>

- The volume of video streams is high while **FR link bandwidth is low**;
- **Traffic detours**: two sites in the same region must go through the hub to communicate, and cross-region traffic must additionally cross the VLL to the other hub.

<div class="zh" markdown="1">

- 视频流数量大，而 **FR 链路带宽低**；
- **流量绕行**：同区域两个站点互通必须先到 Hub；跨区域还要再穿 VLL 到对端 Hub。

</div>

**Goal**: replace hub-spoke with **any-to-any** on a **single global MPLS L3VPN**, gaining bandwidth, latency and **consistent end-to-end QoS**.

<div class="zh" markdown="1">

**目标**：用**单一全球 MPLS L3VPN** 把 hub-spoke 改成 **any-to-any**，同时获得带宽、时延与**一致的端到端 QoS**。

</div>

**Current routing** (the critical input to the migration design):

<div class="zh" markdown="1">

**现状路由**（迁移设计的关键输入）：

</div>

| Scope | Protocol |
|---|---|
| US regional WAN | EIGRP |
| European regional WAN | RIPv2 |
| Inside each of the two hub sites | OSPF (area 0) |
| Between the hubs (the VLL link) | OSPF area 0 |

<div class="zh" markdown="1">

| 范围 | 协议 |
|---|---|
| 美国区域 WAN | EIGRP |
| 欧洲区域 WAN | RIPv2 |
| 两个 Hub 站点内部 | OSPF（area 0） |
| Hub 之间（VLL 链路） | OSPF area 0 |

</div>

> 💡 Here is the historical baggage: **the same OSPF area 0 covers both the hub LANs and the inter-hub VLL**. That directly determines why Step 2 has to say "summarisation is unavailable, adjust cost instead".

<div class="zh" markdown="1">

> 💡 这里有个历史包袱：**同一套 OSPF area 0 既覆盖 Hub 的 LAN，又覆盖 Hub 间的 VLL**。这直接决定了 Step 2 里"汇总不可用、只能调 cost"的处理方式。

</div>

**Three migration steps** (performed separately in each region):

<div class="zh" markdown="1">

**三步迁移**（每区域各自执行）：

</div>

| Step | Action | Key point |
|---|---|---|
| **Step 1 · Build the foundation** | Pick one hub per region as the **transit site during migration** → build the physical connection from hub to MPLS PE → bring up **eBGP** between hub (CE) and PE → redistribute **OSPF and BGP** on the hub | Precondition: **addresses and per-site bandwidth were planned with the carrier before work started** |
| **Step 2 · Migrate the first spoke** | Connect the spoke being migrated to MPLS → advertise its local LAN with **eBGP** (use `network` statements, **avoid redistribution**) → eBGP's **AD=20** beats the IGP, so traffic moves to MPLS automatically → after verification, **disconnect the FR link** | At this point "migrated spoke ↔ not-yet-migrated spoke" traffic transits **the transit hub** |
| **Step 3 · Roll through the remaining spokes** | Migrate them one at a time at the same rhythm | **Connectivity between old and new sites is never interrupted** during migration |

<div class="zh" markdown="1">

| 步骤 | 动作 | 关键点 |
|---|---|---|
| **Step 1 · 建底座** | 每个区域选一个 Hub 作为**迁移期的 transit 站点** → 建 Hub 到 MPLS PE 的物理连接 → 建 Hub(CE) 与 PE 的 **eBGP** → 在 Hub 上做 **OSPF 与 BGP 的重分发** | 前提假设：**地址与每站点带宽在开工前已与运营商规划完毕** |
| **Step 2 · 迁第一个 Spoke** | 待迁移 Spoke 接到 MPLS → eBGP 宣告本地 LAN（用 `network` 语句，**尽量不靠重分发**）→ eBGP 的 **AD=20** 低于 IGP，流量自动切到 MPLS → 确认后**断开 FR 链路** | 此时"已迁移 Spoke ↔ 未迁移 Spoke"的流量经 **transit Hub** 中转 |
| **Step 3 · 滚动剩余 Spoke** | 按同样节奏逐个迁移 | 迁移期间**新旧站点连通性不中断** |

</div>

**The trap you must watch after Step 1 (the book's note)**: once MPLS is in place, a **backdoor link (the VLL)** still exists between the two hubs, so the network now has **two redistribution points**, which can introduce **routing loops or suboptimal paths**. The remedy: **the hubs (ASBRs) on both sides of the backdoor link advertise only summaries, never details**, so the MPLS path (more specific) always wins; otherwise you must apply **route filtering** (see Chapter 8, "routing redistribution design considerations").

<div class="zh" markdown="1">

**Step 1 之后必须注意的陷阱（原文 Note）**：迁移到 MPLS 后，两个 Hub 之间存在 **backdoor 链路（VLL）**，于是全网出现**两个重分发点**，可能引入**路由环路或次优路由**。处理办法：**backdoor 链路两侧的 Hub（ASBR）只通告汇总路由、不通告明细**，保证 MPLS 路径（更具体）始终被优选；否则必须做**路由过滤**（见第 8 章"路由重分发设计考量"）。

</div>

**The detailed trap in Step 2**: the hub LAN and the VLL are both in **area 0**, so on the hub/ASBR you **cannot rely on summarisation** to keep inter-hub traffic on the VLL — summarisation inside the same area does nothing. The correct move is to **lower the OSPF cost of the VLL link** so inter-hub traffic always prefers it.

<div class="zh" markdown="1">

**Step 2 的细节陷阱**：Hub LAN 与 VLL 同属 **area 0**，所以 Hub/ASBR 上**不能靠汇总**来保证 Hub 间流量走 VLL——同一区域内的汇总不生效。正确做法是**降低 VLL 链路的 OSPF cost**，让 Hub 之间的流量始终优先走 VLL。

</div>

### Eight Checks for the Migration Plan (Before Delivery) · 迁移方案的八项检查（交付前）

| # | Check | Pass criterion |
|---|---|---|
| 1 | Intermediate-state topology | A routing and traffic diagram exists for "50% migrated" |
| 2 | Dual-point redistribution | Every redistribution point has a "one-way + whitelist + tag" policy |
| 3 | Backdoor links | Only summaries are advertised, or filtering is configured and verified so details do not leak |
| 4 | Default route | One semantic "origin" network-wide, with an explicit source on the branch side |
| 5 | Summarisation boundaries | The two sides of a summary are not at different migration stages, or more specific routes provide a backstop |
| 6 | AD / preference | Path selection is decided by design, not by default AD by accident |
| 7 | Rollback path | Every disconnected legacy link has a "rollback window" (config retained / circuit expiry date) |
| 8 | Business acceptance | Long-lived voice/video/ERP sessions are monitored and reconnection-verified across the cutover window |

<div class="zh" markdown="1">

| # | 检查项 | 通过标准 |
|---|---|---|
| 1 | 中间态拓扑图 | 有"迁移到 50%"时的路由与流量图 |
| 2 | 双点重分发 | 每个重分发点都有"单向 + 白名单 + tag"策略 |
| 3 | backdoor 链路 | 只宣告汇总，或已配置过滤，且验证过明细不发 |
| 4 | 默认路由 | 全网只有一个"生成点"语义，分支侧来源明确 |
| 5 | 汇总边界 | 汇总点两侧不在不同迁移阶段，或用更具体路由兜底 |
| 6 | AD / 优先级 | 路径选择由设计决定，而不是由默认 AD 偶然决定 |
| 7 | 回退路径 | 每条已断开的旧链路都有"回退窗口"（保留配置 / 线路到期日） |
| 8 | 业务验收 | 语音/视频/ERP 长连接在切换窗口有监控与重连验证 |

</div>

> ⚠️ **In one sentence**: **WAN migration is not "moving branches across one by one"; it is designing an intermediate state that is self-consistent at every moment.** At any point you must be able to answer: who is redistributing, where the default route comes from, whether a summary is eating detail, and whether the backdoor will pull traffic back.

<div class="zh" markdown="1">

> ⚠️ **一句话总结**：**WAN 迁移不是"把分支一个个搬过去"，而是"设计一个在任意时点都自洽的中间态"。** 每个时点都要能回答：谁在重分发、默认路由从哪来、汇总有没有吃掉细节、backdoor 会不会把流量带回去。

</div>

---

## 9. Capacity and Cost Models (Extensions in These Notes) · 九、容量与成本模型（本笔记延伸）

### Four Capacities to Compute Before You Choose Hardware · 四种容量，先算清楚再选型

| Capacity | How to compute | Common mistake |
|---|---|---|
| **Hub bandwidth** | Σ branch peak × simultaneity factor, at N−1 | Sizing on average utilisation |
| **Encrypted throughput** | Nameplate × 0.3–0.6 (with IPsec enabled) | Using the nameplate figure |
| **Tunnel/SA count** | Sites × tunnels per site × 1.5 | Ignoring reconnection overlap |
| **Routing table** | Site prefixes + cloud prefixes + summaries | Ignoring RRs and multipath |

<div class="zh" markdown="1">

| 容量 | 计算 | 常见错误 |
|---|---|---|
| **Hub 带宽** | Σ 分支峰值 × 同时率，且 N−1 | 用平均利用率选型 |
| **加密吞吐** | 标称 × 0.3–0.6（开启 IPsec 后） | 用标称值 |
| **隧道/SA 数** | 站点数 × 每站点隧道数 × 1.5 | 忽略重连叠加 |
| **路由表** | 站点前缀 + 云前缀 + 汇总 | 忽略 RR 与多路径 |

</div>

### A Worked Hub Sizing Example (Copy It Directly) · Hub 容量示例（可直接套用）

```
80 branches, 20 Mbps peak each, simultaneity factor 60%
Aggregate peak = 80 x 20 x 0.6 = 960 Mbps
N-1 (dual hubs) -> each hub must handle >= 960 Mbps
Encryption overhead -> device nameplate >= 960 / 0.5 ~ 2 Gbps
Tunnel count = 80 x 1.5 = 120 (per hub)
```

<div class="zh" markdown="1">

```
分支 80 个，每分支峰值 20 Mbps，同时率 60%
汇聚峰值 = 80 × 20 × 0.6 = 960 Mbps
N−1（双 Hub）→ 单 Hub 需 ≥960 Mbps
加密开销 → 设备标称 ≥ 960 / 0.5 ≈ 2 Gbps
隧道数 = 80 × 1.5 = 120（每 Hub）
```

</div>

### The Cost Model: When the Internet Really Is Cheaper · 成本模型：什么时候 Internet 真的更便宜

| Item | MPLS | Internet + Overlay |
|---|---|---|
| Unit bandwidth price | High (by distance/bandwidth) | Low |
| Hardware | Medium | Medium (needs encryption performance) |
| Operations | Low (the carrier runs it) | Medium-high (you run tunnels and probes) |
| Cost of failure | Low (SLA credits) | High (experience-based losses) |
| Cloud egress | Hairpin or buy separately | Naturally local |

<div class="zh" markdown="1">

| 项 | MPLS | Internet + Overlay |
|---|---|---|
| 带宽单价 | 高（按距离/带宽） | 低 |
| 设备 | 中 | 中（需加密性能） |
| 运维 | 低（运营商管） | 中高（自己管隧道/探测） |
| 故障成本 | 低（SLA 赔付） | 高（体验型损失） |
| 云出口 | 需绕行或另购 | 天然就近 |

</div>

> 🎯 **Conclusion**: **the assumption that the Internet is cheaper only holds when the business can tolerate quality variation and your team can operate the overlay itself.** Otherwise the bandwidth savings get spent again as operations headcount and lost user experience.

<div class="zh" markdown="1">

> 🎯 **结论**：**Internet 便宜的假设只在"业务能容忍质量波动 + 团队能自己运维覆盖层"时成立。** 否则省下的带宽费会以运维人力与体验损失的形式花掉。

</div>

---

## 10. From Design to Delivery: The Nine Tables This Chapter Requires · 十、从设计到交付：本章必须的 9 张表

![The nine deliverable tables of a WAN design with their owners, and the cost model](assets/fig/en17-26-nine-tables.svg)

| # | Table | Content | Who uses it |
|---|---|---|---|
| 1 | Site tiering table | Site / tier (L1–L4) / business / endpoints / bandwidth | Design and procurement |
| 2 | Transport selection table | Site → MPLS/Internet/5G → carrier → CIR/SLA | Procurement and architecture |
| 3 | Reachability matrix | Traffic share and direction between sites/regions | Topology decisions |
| 4 | Redundancy and single-point table | Link/CPE/carrier/last mile/power | Availability review |
| 5 | Overlay technology table | Technology / tunnel count / multicast / encryption / phase | Implementation |
| 6 | Segmentation and VRF table | Segment / VRF / RT / permitted paths | Security review |
| 7 | Routing and summarisation table | Regional prefix / summarisation point / advertisement direction / acceptable suboptimality | Operations |
| 8 | QoS table | Class / marking / queue / shaping point / bandwidth | Implementation and acceptance |
| 9 | Acceptance case table | Kill the primary link / kill a carrier / kill the hub / MTU / congestion | Acceptance |

<div class="zh" markdown="1">

| # | 表 | 内容 | 谁用 |
|---|---|---|---|
| 1 | 站点分级表 | 站点 / 级别（L1–L4）/ 业务 / 终端数 / 带宽 | 设计与采购 |
| 2 | 传输选型表 | 站点 → MPLS/Internet/5G → 运营商 → CIR/SLA | 采购与架构 |
| 3 | 互访矩阵 | 站点/区域之间的流量比例与方向 | 拓扑决策 |
| 4 | 冗余与单点表 | 链路/CPE/运营商/本地环路/电源 | 可用性评审 |
| 5 | 覆盖技术表 | 技术 / 隧道数 / 组播 / 加密 / 阶段 | 实施 |
| 6 | 分段与 VRF 表 | 业务段 / VRF / RT / 允许路径 | 安全评审 |
| 7 | 路由与汇总表 | 区域前缀 / 汇总点 / 宣告方向 / 次优可接受度 | 运维 |
| 8 | QoS 表 | 业务类 / 标记 / 队列 / 整形点 / 带宽 | 实施与验收 |
| 9 | 验收用例表 | 断主链路 / 断运营商 / 断 Hub / MTU / 拥塞 | 验收 |

</div>

---

## Real-World Case Studies (12 Scenarios) · 实战案例（12 个真实场景）

### 🔥 Case 1: Hub Sized on "Average Utilisation" — the Whole Network Slows at Morning Peak · 🔥 案例一：Hub 带宽按"平均利用率"选型，早高峰全网变慢

**Symptom**: 80 branches, hub egress 500 Mbps (1 Gbps contracted); every day between 09:30 and 10:30 ERP access across the network is extremely slow.

<div class="zh" markdown="1">

**现象**：80 个分支，Hub 出口 500 Mbps（合同 1 Gbps），每天 9:30–10:30 全网访问 ERP 极慢。

</div>

**Investigation**: branch peaks sum to 1.4 Gbps with a 70% simultaneity factor; hub egress sits above 95% for long periods and every QoS queue overflows.

<div class="zh" markdown="1">

**排查**：分支峰值合计 1.4 Gbps，同时率 70%；Hub 出口长期 95%+，QoS 队列全部溢出。

</div>

**Root cause**: **hub capacity computed on "average" rather than "peak × simultaneity"**, and no N−1 check.

<div class="zh" markdown="1">

**根因**：**Hub 容量按"平均"而不是"峰值 × 同时率"计算**，且未做 N−1。

</div>

**What should have been done**:
- Hub capacity = Σ branch peak × simultaneity factor, validated at N−1
- Shape at the branches to the CIR so bursts cannot stack up
- Give business-critical traffic (ERP) a bandwidth guarantee and confine bulk traffic to off-peak windows

<div class="zh" markdown="1">

**正确做法**：
- Hub 容量 = Σ 分支峰值 × 同时率，并按 N−1 校验
- 分支侧整形到 CIR，防止突发叠加
- 关键业务（ERP）配带宽保障，批量流量限制在低峰窗口

</div>

### 🔥 Case 2: DMVPN Phase 2 Plus Hub Summarisation — Spoke-to-Spoke Works Intermittently · 🔥 案例二：DMVPN Phase 2 + Hub 汇总，Spoke 直连"时通时不通"

**Symptom**: branches frequently time out reaching a file server at another branch, while access to headquarters is normal.

<div class="zh" markdown="1">

**现象**：分支之间访问文件服务器经常超时，但访问总部正常。

</div>

**Investigation**: the hub advertises a summary (/16) to the spokes, so spokes see only the summary → NHRP cannot resolve the peer tunnel address → packets still go to the hub, but the hub points them back per the summary, producing a "half-direct" state.

<div class="zh" markdown="1">

**排查**：Hub 向 Spoke 汇总宣告（/16），Spoke 只看到汇总 → NHRP 无法解析对端隧道地址 → 报文仍发往 Hub，但 Hub 又按汇总回指 Spoke，形成"半直连"状态。

</div>

**Root cause**: **Phase 2 needs specific /32 routes; summarisation breaks NHRP resolution** (point 5 of this chapter).

<div class="zh" markdown="1">

**根因**：**Phase 2 需要 /32 具体路由，汇总会破坏 NHRP 解析**（本章第 5 条）。

</div>

**What should have been done**:
- If you need "summarisation + direct paths" → upgrade to **Phase 3** (NHRP redirect + shortcut)
- Or do not summarise the spoke subnets (sacrificing table size)
- Use `show dmvpn` to verify NHRP state (it should read `UP`, not `NHRP`)

<div class="zh" markdown="1">

**正确做法**：
- 需要"汇总 + 直连" → 升级到 **Phase 3**（NHRP Redirect + Shortcut）
- 或对 Spoke 网段不做汇总（牺牲路由表规模）
- 用 `show dmvpn` 验证 NHRP 状态（应为 `UP`，而非 `NHRP`）

</div>

### 🔥 Case 3: MTU Never Tuned — Ping Works, Web Pages Do Not Open · 🔥 案例三：MTU 没调，能 ping 通但打不开网页

**Symptom**: after a new DMVPN deployment, branches can ping headquarters servers and open the intranet home page, but downloading attachments and HTTPS logins all stall.

<div class="zh" markdown="1">

**现象**：新上 DMVPN，分支能 ping 总部服务器、能打开内网首页，但下载附件、HTTPS 登录全部卡死。

</div>

**Investigation**: the tunnel MTU of 1400 was never set and MSS was never adjusted; large packets are fragmented or dropped, and PMTUD is blocked because the firewall filters ICMP type 3 code 4.

<div class="zh" markdown="1">

**排查**：隧道 MTU 1400 未配、MSS 未调整；大包被分片/丢弃，PMTUD 又被防火墙拦掉 ICMP type 3 code 4。

</div>

**Root cause**: **tunnel encapsulation overhead + blocked ICMP = large-packet black hole** (point 6 of this chapter).

<div class="zh" markdown="1">

**根因**：**隧道封装开销 + ICMP 被拦 = 大包黑洞**（本章第 6 条）。

</div>

**What should have been done**:
- `ip mtu 1400` plus `ip tcp adjust-mss 1360` on the tunnel interface
- Permit the necessary ICMP (type 3 code 4)
- Add a "large packet test" to go-live acceptance (`ping -l 1400 -f`)

<div class="zh" markdown="1">

**正确做法**：
- 隧道口 `ip mtu 1400` + `ip tcp adjust-mss 1360`
- 放行必要的 ICMP（type 3 code 4）
- 上线验收加"大包测试"（`ping -l 1400 -f`）

</div>

### 🔥 Case 4: Active/Standby Floating Static — a Carrier-Side Fault Blacks Out the Network for 40 Minutes · 🔥 案例四：主备浮动静态，运营商侧故障黑了 40 分钟

**Symptom**: the primary link interface is up and the next hop answers ping, yet the business is completely down; the carrier repairs it 40 minutes later.

<div class="zh" markdown="1">

**现象**：主链路接口 up、下一跳 ping 通，但业务全断；40 分钟后运营商修复。

</div>

**Investigation**: static default plus floating backup, sensitive only to interface down; the carrier's metro failure never propagated to the CE interface.

<div class="zh" markdown="1">

**排查**：静态默认 + 浮动备份，只感知接口 down；运营商城域网故障未传导到 CE 接口。

</div>

**Root cause**: **"link up" is not "path usable"** (point 8 of this chapter).

<div class="zh" markdown="1">

**根因**：**"链路 up" ≠ "路径可用"**（本章第 8 条）。

</div>

**What should have been done**:
- Move to eBGP (prefix withdrawal expresses unreachability) or IP SLA with tracking
- Choose probe targets that are multiple, cross-carrier and end-to-end (for example 8.8.8.8, the carrier DNS, a critical SaaS endpoint)
- Write "carrier-side failure" into the acceptance cases and measure the actual switchover time

<div class="zh" markdown="1">

**正确做法**：
- 改用 eBGP（前缀撤销表达不可达）或 IP SLA + track
- 探测目标选"多个、跨运营商、端到端"（如 8.8.8.8、运营商 DNS、关键 SaaS）
- 把"运营商侧故障"写入验收用例，实测切换时间

</div>

### 🔥 Case 5: Running STP over L2 MPLS — One Loop and the Carrier Shuts Your Port · 🔥 案例五：L2 MPLS 上跑 STP，一次环路被运营商切端口

**Symptom**: VPLS connects six sites; one mis-cabling incident causes a broadcast storm and the carrier simply shuts the customer port, taking the whole network down for 25 minutes.

<div class="zh" markdown="1">

**现象**：VPLS 连接 6 个站点，一次误接线造成广播风暴，运营商直接 shutdown 客户端口，全网中断 25 分钟。

</div>

**Investigation**: the customer's Layer 2 domain spans six sites, so the STP diameter is large and convergence slow; the carrier applies broadcast suppression.

<div class="zh" markdown="1">

**排查**：客户侧二层域跨 6 个站点，STP 直径大、收敛慢；运营商侧有广播抑制策略。

</div>

**Root cause**: **doing Layer 2 across the WAN scales a campus-level risk up to the carrier backbone**.

<div class="zh" markdown="1">

**根因**：**在 WAN 上做二层，把园区级的风险放大到运营商骨干**。

</div>

**What should have been done**:
- Move to L3 VPN, or keep Layer 2 only between two points (VLL)
- If Layer 2 must stay: MSTP, root guard, BPDU filtering, storm control, and a cap on domain size
- Confirm with the carrier the suppression thresholds for broadcast/multicast/unknown unicast

<div class="zh" markdown="1">

**正确做法**：
- 改为 L3 VPN 或"L2 只保留两点（VLL）"
- 必须保留二层时：启用 MSTP/根保护/BPDU 过滤/风暴抑制，并限制二层域规模
- 与运营商确认"广播/组播/未知单播的抑制阈值"

</div>

### 🔥 Case 6: One Missing Multi-VRF CE Subinterface — Branches Bypass the Firewall · 🔥 案例六：Multi-VRF CE 漏配一个子接口，分支互访绕过防火墙

**Symptom**: an audit finds that the guest segment can reach production servers, although policy says it should be denied.

<div class="zh" markdown="1">

**现象**：审计发现"访客段能访问生产服务器"，但策略显示应被拒绝。

</div>

**Investigation**: on one branch CE the guest subinterface was accidentally placed in the production VRF; because the two segments do not overlap, routing makes them directly reachable.

<div class="zh" markdown="1">

**排查**：某分支 CE 的访客子接口误接入生产 VRF；由于两段地址不重叠，路由直接可达。

</div>

**Root cause**: **segmentation is held together by configuration consistency alone, with no automated verification**.

<div class="zh" markdown="1">

**根因**：**分段靠"配置一致性"维持，缺少自动化校验**。

</div>

**What should have been done**:
- Export the network-wide VRF/subinterface mapping quarterly and diff it against the baseline
- Use active probes to prove "cross-segment unreachable" rather than reading the config
- Put a three-column, strictly validated "subinterface ↔ VRF ↔ VLAN" table into the change template

<div class="zh" markdown="1">

**正确做法**：
- 每季度导出全网 VRF/子接口映射与基线比对
- 用主动探测证明"跨段不可达"（而非只看配置）
- 变更模板中把"子接口 ↔ VRF ↔ VLAN"做成三列强校验表

</div>

### 🔥 Case 7: Inter-AS Option A — It Collapses as Soon as VPNs Multiply · 🔥 案例七：Inter-AS 选 Option A，VPN 一多就崩

**Symptom**: a multinational group with 5 ASes and 40 VPNs started on Option A (back-to-back subinterfaces); a year in, adding one VPN touches 10 ASBRs and needs a 4-hour change window minimum.

<div class="zh" markdown="1">

**现象**：集团跨国，5 个 AS、40 个 VPN。最初用 Option A（背靠背子接口），运行一年后每次新增 VPN 要动 10 台 ASBR，变更窗口 4 小时起。

</div>

**Investigation**: Option A is "configure per VPN, per AS", so complexity is O(VPN × AS).

<div class="zh" markdown="1">

**排查**：Option A 是"逐 VPN 逐 AS 配置"，复杂度 O(VPN × AS)。

</div>

**Root cause**: **the option was never chosen by evaluating VPN count × AS count**.

<div class="zh" markdown="1">

**根因**：**选项选择未按"VPN 数 × AS 数"评估**。

</div>

**What should have been done**:
- Medium scale → **Option B** (ASBRs exchange VPNv4 routes)
- Large scale/many ASes → **Option C** (ASBRs exchange only labelled IPv4; VPN routes end to end)
- Before any change, use "how many devices must I touch to add one VPN?" as the scalability metric

<div class="zh" markdown="1">

**正确做法**：
- 中等规模改 **Option B**（ASBR 交换 VPNv4 路由）
- 大规模/多 AS 改 **Option C**（ASBR 只交换带标签的 IPv4，VPN 路由端到端）
- 变更前先用"新增一个 VPN 要动几台设备"作为可扩展性指标

</div>

### 🔥 Case 8: Two Carriers, One Last Mile — a Single Excavation Cuts Both · 🔥 案例八：双运营商但同一段 last mile，一次开挖双断

**Symptom**: a construction crew cuts the main cable and both carriers go down simultaneously for eight hours.

<div class="zh" markdown="1">

**现象**：主线缆被施工挖断，两家运营商同时中断 8 小时。

</div>

**Investigation**: both carriers enter the building along the same road segment and use different fibres inside the same duct.

<div class="zh" markdown="1">

**排查**：两家均从同一路段引入，且使用同一根管道内的不同光纤。

</div>

**Root cause**: **redundancy was implemented at the "carrier layer" but not at the "physical layer"** (point 13 of this chapter).

<div class="zh" markdown="1">

**根因**：**冗余只做到"运营商层"，没做到"物理层"**（本章第 13 条）。

</div>

**What should have been done**:
- Require different access types (for example fibre plus 5G/microwave) or different cable routes
- Dual CPE, dual power and separate racks at critical sites
- Draw the physical paths on one diagram for single-point review (many design documents have no such diagram)

<div class="zh" markdown="1">

**正确做法**：
- 要求"接入方式不同"（如光纤 + 5G/微波），或"路由方向不同"
- 关键站点双 CPE + 双电源 + 不同机柜
- 把物理路径画在同一张图上做单点评审（很多设计文档里没有这张图）

</div>

### 🔥 Case 9: MPLS Plus Internet Dual Transport — SaaS Traffic Still Hairpins Through Headquarters · 🔥 案例九：MPLS + Internet 双传输，SaaS 流量绕行总部

**Symptom**: branches have a poor M365 experience (documents take 10 s+ to open), yet neither link is heavily utilised.

<div class="zh" markdown="1">

**现象**：分支用 M365 体验差（打开文档 10 s+），但两条链路利用率都不高。

</div>

**Investigation**: the Internet link serves only as backup; everything, SaaS included, follows the default route to headquarters before going out to the Internet.

<div class="zh" markdown="1">

**排查**：Internet 链路只做备份，所有流量（含 SaaS）按默认路由回总部再出互联网。

</div>

**Root cause**: **dual transport was used for redundancy, not for traffic steering**.

<div class="zh" markdown="1">

**根因**：**双传输只做了"冗余"，没做"分流"**。

</div>

**What should have been done**:
- Steer by application/destination: SaaS out through local DIA (with cloud security), internal traffic over MPLS
- Use application recognition (SD-WAN or router NBAR) instead of guessing by port
- Keep an explicit "back to headquarters" path after steering (compliance and audit)

<div class="zh" markdown="1">

**正确做法**：
- 按应用/目的地分流：SaaS 走本地 DIA（配云安全），内网走 MPLS
- 用应用识别（SD-WAN/路由器 NBAR）而不是"按端口猜"
- 分流后仍保留"回总部"的明确路径（合规与审计）

</div>

### 🔥 Case 10: QoS Only at Headquarters — Voice Dies First When the Branch Uplink Congests · 🔥 案例十：QoS 只在总部做，分支上行拥塞时语音先死

**Symptom**: when a branch uploads a large file, VoIP calls at that same branch break up badly.

<div class="zh" markdown="1">

**现象**：分支上传大文件时，同一分支的 VoIP 通话严重断续。

</div>

**Investigation**: headquarters egress has LLQ, but the branch CE uplink has neither shaping nor queues; during uplink congestion voice shares a queue with bulk traffic.

<div class="zh" markdown="1">

**排查**：总部出口有 LLQ，分支 CE 上行未配置整形与队列；上行拥塞时语音与批量流量同队列。

</div>

**Root cause**: **QoS must take effect on every egress that can congest** (point 12 of this chapter).

<div class="zh" markdown="1">

**根因**：**QoS 必须在"每个会拥塞的出口"生效**（本章第 12 条）。

</div>

**What should have been done**:
- Branch CE uplink: shape to the CIR + classified queues + LLQ
- Mark at the trust boundary (endpoint or access switch); the edge must not trust endpoint markings
- Verify at acceptance by saturating the uplink and measuring voice MOS

<div class="zh" markdown="1">

**正确做法**：
- 分支 CE 上行：整形到 CIR + 分类队列 + LLQ
- 标记在可信边界完成（终端/接入交换机），边缘不信任终端标记
- 验收时用"上行灌满 + 语音 MOS"实测

</div>

### 🔥 Case 11: Multicast Video Training Saturates the Hub · 🔥 案例十一：组播视频培训把 Hub 打满

**Symptom**: headquarters runs HD video training to 80 branches; hub egress instantly hits 100% and all other traffic suffers.

<div class="zh" markdown="1">

**现象**：总部向 80 个分支做高清视频培训，Hub 出口瞬间 100%，全网业务受影响。

</div>

**Investigation**: multicast is carried in GRE tunnels with the hub replicating per branch (80 copies), and no bandwidth limit was applied.

<div class="zh" markdown="1">

**排查**：用 GRE 隧道承载组播，Hub 逐分支复制（80 份），且未做带宽限制。

</div>

**Root cause**: **the replication point for multicast was chosen wrongly** (hub replication = hub bandwidth × branch count).

<div class="zh" markdown="1">

**根因**：**组播的复制点选错**（Hub 复制 = Hub 带宽 × 分支数）。

</div>

**What should have been done**:
- For large-scale distribution, use mVPN (replication at the carrier PE) or application-layer CDN/distribution
- If tunnel multicast must stay: cap per-branch bitrate, use a lower bitrate, and stagger sessions
- For training scenarios prefer application-layer distribution and let the network just carry it

<div class="zh" markdown="1">

**正确做法**：
- 大规模分发用 mVPN（复制点在运营商 PE）或应用层 CDN/分发
- 若保留隧道组播：限制每分支码率 + 使用更低码率 + 错峰
- 培训类场景优先"应用层分发"，网络只做承载

</div>

### 🔥 Case 12: Encrypted Throughput Sized on the Nameplate — Half the Throughput Once IPsec Is On · 🔥 案例十二：加密吞吐按标称选型，开启 IPsec 后吞吐腰斩

**Symptom**: a new hub device rated 10 Gbps delivers only 3.5 Gbps with IPsec on, and even after the upgrade it is not enough.

<div class="zh" markdown="1">

**现象**：新 Hub 设备标称 10 Gbps，实际开启 IPsec 后只有 3.5 Gbps，扩容后仍不够。

</div>

**Investigation**: the nameplate figure is "forwarding without encryption"; with encryption it is limited by CPU or accelerator capacity, and there was no N−1 planning.

<div class="zh" markdown="1">

**排查**：标称值为"无加密转发"，加密后受 CPU/加速卡限制；且未按 N−1 规划。

</div>

**Root cause**: **capacity sized on the nameplate rather than on measured encrypted throughput** (points 7 and 15 of this chapter).

<div class="zh" markdown="1">

**根因**：**容量按"标称"而不是"实测加密吞吐"**（本章第 7、15 条）。

</div>

**What should have been done**:
- Size on "measured encrypted throughput × N−1" and demand encryption test reports from the vendor
- For large scale, consider centralising encryption on a few nodes or using hardware-accelerated platforms
- Validate against a real traffic baseline after going live (re-test quarterly)

<div class="zh" markdown="1">

**正确做法**：
- 选型按"加密后实测吞吐 × N−1"；要求厂商提供加密吞吐测试报告
- 大规模场景考虑"加密集中在少数节点"或使用硬件加速平台
- 上架后用真实流量基线验证（每季度复测）

</div>

---

## Design Trade-offs · 设计取舍

| Trade-off | What A gives you | What B gives you | How CCDE decides |
|---|---|---|---|
| **A: L2 MPLS / B: L3 MPLS** | L2 adjacency, full routing control | Scalable, simple to operate | Is there a business requirement that "must run Layer 2 across the WAN"? |
| **A: MPLS / B: Internet + Overlay** | Quality guarantees, failure notification | Low cost, fast to scale, local cloud access | Can the business tolerate quality variation, and can the team operate an overlay? |
| **A: single CPE / B: dual CPE** | Saves cost, less configuration | Device-level redundancy | How critical is the site (can it accept total outage on a device failure)? |
| **A: static + SLA / B: BGP** | Simple, no carrier cooperation needed | Real reachability, fine-grained path control | Do you need switchover on a "carrier-side failure" too? |
| **A: hub-spoke / B: any-to-any** | Low cost, centralised policy | No detours, better latency | Share of east-west traffic (>30% suggests B) |
| **A: DMVPN P2 / B: DMVPN P3** | Simple configuration | Supports summarisation plus direct paths | Do you need summarisation (if yes, B)? |
| **A: build your own overlay / B: carrier L3VPN** | Flexible, controllable | Less operations, SLA included | Team size and site growth rate |
| **A: traditional routing / B: SD-WAN** | Direct, explainable | Application awareness, multi-transport, ZTP | Site count, transport count, application experience requirements |
| **A: Multi-VRF CE / B: carrier VRF** | No MP-BGP on the CE | Native any-to-any | Number of segments and change frequency |
| **A: Inter-AS B / B: Inter-AS C** | Medium scale, simpler configuration | Large scale, light ASBR load | VPN count × AS count |
| **A: centralised exit / B: local DIA** | Centralised audit | Better experience, less bandwidth used | Steer by destination, not by site |
| **A: tunnel multicast / B: mVPN** | No carrier support needed | Replication at the PE, better scale | Receiver count and real-time requirements |
| **A: 6-class QoS / B: 8-class** | Easy to operate, aligns with the carrier | Finer granularity | How many classes the carrier offers (usually 4–6) |
| **A: WAN optimisation appliances / B: protocol and path engineering** | Acceleration for specific applications | No extra boxes, encryption-compatible | Is traffic encrypted (deduplication dies after encryption)? |
| **A: single primary hub / B: regional hubs** | Simple, low cost | Better latency, smaller failure domain | Geographic spread and east-west traffic |
| **A: build a private cloud circuit / B: IPsec over the Internet to cloud** | SLA, stable bandwidth | Fast, cheap | Business criticality and budget |

<div class="zh" markdown="1">

| 取舍 | 选 A 得到 | 选 B 得到 | CCDE 判断依据 |
|------|----------|----------|--------------|
| **A: L2 MPLS / B: L3 MPLS** | 二层邻接、完全掌控路由 | 可扩展、运维简单 | 是否存在"必须在 WAN 跑二层"的业务 |
| **A: MPLS / B: Internet + Overlay** | 质量保证、故障通知 | 成本低、扩容快、云就近 | 业务能否容忍质量波动 + 团队能否运维覆盖层 |
| **A: 单 CPE / B: 双 CPE** | 省成本、少配置 | 设备级冗余 | 站点是否关键（能否接受设备故障全断） |
| **A: 静态 + SLA / B: BGP** | 简单、无需运营商配合 | 真实可达性、精细选路 | 是否需要"运营商侧故障也切换" |
| **A: Hub-Spoke / B: Any-to-Any** | 成本低、策略集中 | 无绕行、时延优 | 东西向流量占比（>30% 考虑 B） |
| **A: DMVPN P2 / B: DMVPN P3** | 配置简单 | 支持汇总 + 直连 | 是否需要"汇总"（需要则 B） |
| **A: 自建覆盖 / B: 运营商 L3VPN** | 灵活、可控 | 省运维、有 SLA | 团队规模与站点增速 |
| **A: 传统路由 / B: SD-WAN** | 直接、可解释 | 应用感知、多传输、ZTP | 站点数、传输数、应用体验要求 |
| **A: Multi-VRF CE / B: 运营商 VRF** | CE 无需 MP-BGP | 天然 any-to-any | 分段数量与变更频率 |
| **A: Inter-AS B / B: Inter-AS C** | 中等规模、配置较简 | 大规模、ASBR 轻载 | VPN 数 × AS 数 |
| **A: 集中出口 / B: 本地 DIA** | 审计集中 | 体验好、带宽省 | 按目的地分流而非按站点 |
| **A: 隧道组播 / B: mVPN** | 无需运营商支持 | 复制在 PE、扩展性好 | 接收者规模与实时性 |
| **A: 6 类 QoS / B: 8 类** | 易运维、对齐运营商 | 精细 | 运营商等级数（通常 4–6 类） |
| **A: WAN 优化设备 / B: 协议与路径优化** | 特定应用加速 | 无额外设备、加密兼容 | 是否有加密（加密后去重失效） |
| **A: 单一主 Hub / B: 区域 Hub** | 简单、成本低 | 时延优、故障域小 | 地理跨度与东西向流量 |
| **A: 自建云专线 / B: 公网 IPsec 到云** | SLA、稳定带宽 | 快速、便宜 | 业务关键度与预算 |

</div>

> 💡 **One general test**: **"does this design still work if the carrier will not cooperate?"** Many WAN designs depend on the other party (BGP, mVPN, QoS classes, CSC); **whatever breaks must be written into the risks and open items**.

<div class="zh" markdown="1">

> 💡 **一条通用判据**：**"这个方案在'运营商不配合'时还能不能工作？"** WAN 的很多设计依赖对方配合（BGP、mVPN、QoS 等级、CSC），**不能工作的部分必须写进风险与未决项**。

</div>

---

## Design Pitfalls · 设计缺陷

| # | Pitfall | Consequence | Avoidance |
|---|---|---|---|
| 1 | Sizing the hub on average utilisation | The whole network slows at morning peak | Peak × simultaneity, at N−1 |
| 2 | Not tuning tunnel MTU/MSS | Large-packet black hole | `ip mtu` + `adjust-mss` + permit ICMP |
| 3 | Computing encrypted throughput from the nameplate | Half speed from day one | Measured encrypted throughput × N−1 |
| 4 | Treating floating static as redundancy | Carrier-side faults do not trigger switchover | BGP, or SLA with tracking |
| 5 | DMVPN P2 plus summarisation | Spoke-to-spoke connectivity fails | Move to P3 or stop summarising |
| 6 | Two carriers on the same last mile | Both fail together | Physical path and access diversity |
| 7 | One CPE carrying both links | A device failure kills everything | Dual CPE at critical sites |
| 8 | Building a large Layer 2 domain across the WAN | Loops, storms, carrier port shutdowns | Move to L3, or limit the L2 domain |
| 9 | Two-way redistribution | Loops, suboptimal paths, inexplicable behaviour | One-way + whitelist + tags |
| 10 | Placing summarisation points where failures converge | Detours after a failure | Align summarisation points with the topology |
| 11 | QoS only at headquarters | Branch uplink voice dies first | Shaping plus queues on every egress |
| 12 | LLQ for voice without a rate limit | Starves every other queue | LLQ plus policing |
| 13 | Trusting endpoint markings | Users forge EF | Remark at the trust boundary |
| 14 | No baseline verification for Multi-VRF CE | Segmentation fails silently | Periodic diffing plus active probes |
| 15 | Inter-AS Option A at large scale | Change cost explodes | Choose B/C by VPN × AS |
| 16 | Multicast replication point on the hub | The hub saturates | mVPN or application-layer distribution |
| 17 | No out-of-band management | A config error cuts you off | 4G/management port plus rollback |
| 18 | No telemetry | You cannot prove QoS or convergence | NetFlow/IPFIX plus probes |
| 19 | Ignoring IPv6 dual stack | Policy gaps after go-live | Review dual-stack policy in pairs |
| 20 | Never running failure drills | Recovery happens in the wrong order during a real fault | Four case families: link, hub, carrier, congestion |

<div class="zh" markdown="1">

| # | 缺陷 | 后果 | 规避 |
|---|------|------|------|
| 1 | Hub 按平均利用率选型 | 早高峰全网变慢 | 峰值 × 同时率 + N−1 |
| 2 | 隧道不调 MTU/MSS | 大包黑洞 | `ip mtu` + `adjust-mss` + 放行 ICMP |
| 3 | 加密吞吐按标称算 | 上线即半速 | 按实测加密吞吐 × N−1 |
| 4 | 静态浮动当冗余 | 运营商侧故障不切 | BGP 或 SLA + track |
| 5 | DMVPN P2 + 汇总 | Spoke 直连失败 | 改 P3 或不汇总 |
| 6 | 双运营商同 last mile | 同时断 | 物理路径与接入方式多样性 |
| 7 | 单 CPE 承载双链路 | 设备故障全断 | 关键站点双 CPE |
| 8 | 在 WAN 上做大二层 | 环路/风暴/被运营商切端口 | 改 L3，或限制二层域 |
| 9 | 双向重分发 | 环路、次优、不可解释 | 单向 + 白名单 + 标签 |
| 10 | 汇总点选在故障收敛处 | 故障后绕行 | 汇总点与拓扑对齐 |
| 11 | QoS 只在总部 | 分支上行语音先死 | 每个出口整形 + 队列 |
| 12 | 语音 LLQ 不限速 | 饿死其他队列 | LLQ + police |
| 13 | 终端标记直接信任 | 用户伪造 EF | 信任边界重标记 |
| 14 | Multi-VRF CE 无基线校验 | 分段失效（静默） | 定期比对 + 主动探测 |
| 15 | Inter-AS 选 A 做大规模 | 变更成本爆炸 | 按 VPN×AS 选 B/C |
| 16 | 组播复制点在 Hub | Hub 被打满 | mVPN 或应用层分发 |
| 17 | 无带外管理 | 配置错误即失联 | 4G/管理口 + 回滚 |
| 18 | 无遥测 | 无法证明 QoS/收敛 | NetFlow/IPFIX + 探针 |
| 19 | 忽略 IPv6 双栈 | 上线后策略缺口 | 双栈策略成对评审 |
| 20 | 未做故障演练 | 真故障时按错误顺序恢复 | 断链路/断 Hub/断运营商/拥塞 四类用例 |

</div>

---

## Key Terms · 本章关键术语

### Transport and Topology · 传输与拓扑

| Term | Meaning |
|---|---|
| WAN (Wide Area Network) | A network spanning wide geographic areas |
| L2 MPLS VPN | Layer 2 MPLS VPN (the carrier provides an L2 pipe) |
| L3 MPLS VPN | Layer 3 MPLS VPN (the carrier provides VRF-based routing) |
| VPLS (E-LAN) | Virtual private LAN service (multipoint Layer 2) |
| VLL / pseudowire (E-Line) | Virtual leased line (point-to-point Layer 2) |
| E-Tree | Point-to-multipoint Layer 2 service |
| Metro Ethernet | Carrier Ethernet inside a metro area |
| Last mile | The local loop from the carrier to the premises |
| CIR (Committed Information Rate) | The committed information rate in the contract |
| Hub-spoke | Star (hub-and-branch) topology |
| Partial mesh | Some sites interconnected directly |
| Any-to-any | Fully meshed |
| CE / PE / P | Customer edge / provider edge / provider core |
| CPE (Customer Premises Equipment) | Customer-side equipment |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| WAN (Wide Area Network) | 广域网 |
| L2 MPLS VPN | 二层 MPLS VPN（运营商提供二层管道） |
| L3 MPLS VPN | 三层 MPLS VPN（运营商提供 VRF 路由） |
| VPLS (E-LAN) | 虚拟专用局域网服务（多点二层） |
| VLL / Pseudowire (E-Line) | 虚拟租用线路（点对点二层） |
| E-Tree | 一点到多点二层服务 |
| Metro Ethernet | 城域以太网 |
| Last Mile | 最后一公里（本地环路） |
| CIR (Committed Information Rate) | 承诺信息速率 |
| Hub-Spoke | 星型（中心-分支）拓扑 |
| Partial Mesh | 部分网状 |
| Any-to-Any | 全互联 |
| CE / PE / P | 客户边缘 / 运营商边缘 / 运营商骨干 |
| CPE (Customer Premises Equipment) | 客户侧设备 |

</div>

### Overlay and Tunnels · 覆盖与隧道

| Term | Meaning |
|---|---|
| Overlay / underlay | The overlay network / the transport network underneath |
| IPsec | IP security (encryption and authentication) |
| IKEv1 / IKEv2 | Internet Key Exchange |
| SVTI | Static virtual tunnel interface |
| GRE | Generic Routing Encapsulation |
| mGRE | Multipoint GRE |
| NHRP | Next Hop Resolution Protocol (the core of DMVPN) |
| DMVPN | Dynamic Multipoint VPN |
| FlexVPN | A flexible IKEv2-based VPN framework |
| GET VPN | Group Encrypted Transport VPN (no tunnels) |
| SD-WAN | Software-defined WAN |
| ZTP | Zero-touch provisioning |
| DPD | Dead peer detection |
| NAT-T | NAT traversal |
| MSS clamping | Clamping the TCP maximum segment size |
| PMTUD | Path MTU discovery |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| Overlay / Underlay | 覆盖网络 / 底层承载网络 |
| IPsec | IP 安全协议（加密与认证） |
| IKEv1 / IKEv2 | 因特网密钥交换协议 |
| SVTI | 静态虚拟隧道接口 |
| GRE | 通用路由封装 |
| mGRE | 多点 GRE |
| NHRP | 下一跳解析协议（DMVPN 核心） |
| DMVPN | 动态多点 VPN |
| FlexVPN | 基于 IKEv2 的灵活 VPN 框架 |
| GET VPN | 组加密传输 VPN（无隧道） |
| SD-WAN | 软件定义广域网 |
| ZTP | 零接触部署 |
| DPD | 死对等检测 |
| NAT-T | NAT 穿透 |
| MSS Clamping | 最大报文段长度钳制 |
| PMTUD | 路径 MTU 发现 |

</div>

### Virtualisation and Segmentation · 虚拟化与分段

| Term | Meaning |
|---|---|
| VRF | Virtual routing and forwarding instance |
| VRF-Lite / Multi-VRF CE | Lightweight VRF / multiple VRFs on the customer edge |
| RD / RT | Route distinguisher / route target |
| MP-BGP | Multiprotocol BGP (carrying VPNv4/VPNv6) |
| CSC (Carrier Supporting Carrier) | One carrier riding another carrier's backbone |
| Inter-AS Option A/B/C | The three ways of joining MPLS VPN ASes |
| mVPN | Multicast VPN |
| NFV / vCPE | Network function virtualisation / virtual CPE |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| VRF | 虚拟路由转发实例 |
| VRF-Lite / Multi-VRF CE | 轻量 VRF / 多 VRF 客户边缘 |
| RD / RT | 路由区分符 / 路由目标 |
| MP-BGP | 多协议 BGP（承载 VPNv4/VPNv6） |
| CSC (Carrier Supporting Carrier) | 运营商支撑运营商 |
| Inter-AS Option A/B/C | 跨 AS 的三种互联方式 |
| mVPN | 组播 VPN |
| NFV / vCPE | 网络功能虚拟化 / 虚拟 CPE |

</div>

### Routing, QoS and Operations · 路由、QoS 与运维

| Term | Meaning |
|---|---|
| eBGP / iBGP | External / internal BGP |
| Route reflector | A BGP route reflector |
| Route redistribution | Moving routes between routing protocols |
| Route summarisation | Aggregating routes into a shorter prefix |
| LLQ (Low Latency Queueing) | Priority queueing with a bandwidth cap |
| WRED | Weighted random early detection |
| Shaping / policing | Buffering to a rate / dropping above a rate |
| DSCP | Differentiated services code point |
| SLA | Service level agreement |
| BFD | Bidirectional forwarding detection |
| IP SLA | Active IP service-level probes |
| BDP | Bandwidth-delay product |
| DIA | Direct internet access |
| Cloud on-ramp | A dedicated entry point into a cloud provider |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| eBGP / iBGP | 外部 / 内部 BGP |
| Route Reflector | 路由反射器 |
| Route Redistribution | 路由重分发 |
| Route Summarization | 路由汇总 |
| LLQ (Low Latency Queueing) | 低时延队列 |
| WRED | 加权随机早期检测 |
| Shaping / Policing | 整形 / 限速丢弃 |
| DSCP | 差分服务代码点 |
| SLA | 服务等级协议 |
| BFD | 双向转发检测 |
| IP SLA | IP 服务等级探测 |
| BDP | 带宽时延积 |
| DIA | 直接互联网接入 |
| Cloud On-Ramp | 云接入点 |

</div>

---

## Field Notes · 实战经验总结

1. **The first-order WAN question is "who fills the SLA gap"**: the carrier only guarantees its own segment, so end-to-end depends on redundancy, overlay and probing.
2. **L2 versus L3 is decided by one fact**: whether you have a business requirement that "must run Layer 2 across the WAN". Every other reason is a preference.
3. **Do not treat the Internet as "MPLS at a lower price"**: it has no queue guarantees, no failure notification and no end-to-end latency commitment.
4. **Overlay selection = site count × direct-path need × transport count** — three questions give the answer.
5. **"Summarise + direct spoke paths" means DMVPN Phase 3 only.** Phase 2 plus summarisation is the most common silent failure.
6. **The tunnel's first tax is MTU**: GRE 24 bytes, IPsec 50–73 bytes, VXLAN 50 bytes; once stacked you must clamp MSS.
7. **Size hub capacity on "all sites at peak × simultaneity" at N−1, and size hardware on "measured encrypted throughput".**
8. **In the WAN, "link up" almost never means "path usable"**: use BGP, or IP SLA with tracking.
9. **Dual carriers must be verified for physical diversity**: same duct, same exchange, same access type = single point.
10. **Dual links with a single CPE are not high availability**: one device, one rack, one power feed.
11. **QoS belongs on every egress that can congest**, above all the branch uplink; LLQ at headquarters cannot save a branch's voice.
12. **LLQ must be rate-limited**, otherwise traffic "marked as voice" starves the whole network.
13. **There is only one shaping point: your egress.** Shaping to 95% of the contracted CIR is more controllable than being dropped by the carrier.
14. **Redistribution in the WAN must be one-way, whitelisted and tagged**; two-way redistribution is a synonym for "it works but nobody can explain it".
15. **The multicast replication point decides the cost**: hub replication = hub bandwidth × branch count; at scale use mVPN or application distribution.
16. **Multi-VRF CE is segmentation, not encryption**; prove isolation with "active probes + baseline diffing", not with "we configured VRFs".
17. **The Inter-AS option is decided by VPN count × AS count**; never use Option A at large scale.
18. **Size encrypted throughput on measured values**; nameplate figures are usually taken without encryption and with 64-byte packets.
19. **Out-of-band management and rollback are the WAN's lifeline**: one bad route can cut 80 sites off at once.
20. **WAN scalability is the scalability of operating cost**: how many places must change to add one site decides how many years the architecture lives.

<div class="zh" markdown="1">

1. **WAN 的第一性问题是"SLA 缺口由谁补"**：运营商只保它那段，端到端要靠冗余、覆盖层与探测。
2. **L2 还是 L3，只由一个事实决定**：有没有"必须在 WAN 上跑二层"的业务。其余理由都是偏好。
3. **不要把 Internet 当成"便宜版 MPLS"**：它没有队列保证、没有故障通知、没有端到端时延承诺。
4. **覆盖技术选型 = 站点数 × 是否直连 × 传输数量**，三个问题定答案。
5. **要"汇总 + Spoke 直连"，只有 DMVPN Phase 3**。Phase 2 + 汇总是最常见的隐性故障。
6. **隧道的第一笔税是 MTU**：GRE 24 字节、IPsec 50–73 字节、VXLAN 50 字节，叠加后必须钳 MSS。
7. **Hub 容量按"所有站点峰值 × 同时率"并 N−1**；设备按"加密后实测吞吐"。
8. **"链路 up" 在 WAN 里几乎不代表"路径可用"**：要么 BGP，要么 IP SLA + track。
9. **双运营商必须验证物理多样性**：同管道、同局房、同接入方式 = 单点。
10. **单 CPE 双链路不是高可用**：设备是唯一的、机柜是唯一的、电源是唯一的。
11. **QoS 要在每个会拥塞的出口做**，尤其是分支上行；总部的 LLQ 救不了分支的语音。
12. **LLQ 必须限速**，否则"标记为语音"的流量会饿死整个网络。
13. **整形点只有一个：你的出口**。按合同 CIR 的 95% 整形，比被运营商丢包更可控。
14. **WAN 上的重分发必须单向 + 白名单 + 标签**；双向重分发是"能用但不可解释"的同义词。
15. **组播的复制点决定成本**：Hub 复制 = Hub 带宽 × 分支数；大规模要用 mVPN 或应用分发。
16. **Multi-VRF CE 是分段不是加密**；证明隔离靠"主动探测 + 基线比对"，不靠"配了 VRF"。
17. **Inter-AS 选项由"VPN 数 × AS 数"决定**，不要用 Option A 做大规模。
18. **加密吞吐要按实测值选型**，标称值通常在无加密、64 字节小包条件下测得。
19. **带外管理与回滚是 WAN 的生命线**：一条错误路由能让 80 个站点同时失联。
20. **WAN 的可扩展性是"运营成本的可扩展性"**：加一个站点要动几处，决定了这套架构能活几年。

</div>

---

## Design Scenario Exercises (WAN Architecture, Three Problems) · 设计情景演练（WAN 架构类，三道）

> The trap in this chapter's exam questions is **treating "pick a transport" as "design a WAN"** (agonising over MPLS versus SD-WAN) while ignoring the four real inputs: **traffic matrix + site tiering + the team's operational capability + contract constraints**. The correct order is always: business map → transport model → redundancy shape → overlay and segmentation → routing and QoS → capacity and validation.

<div class="zh" markdown="1">

> 本章题型的陷阱是：**把"选传输"当成"设计 WAN"**（纠结 MPLS 还是 SD-WAN），而忽略"流量矩阵 + 站点分级 + 团队运维能力 + 合同约束"这四条真正的输入。正确顺序永远是：业务地图 → 传输模型 → 冗余形态 → 覆盖与隔离 → 路由与 QoS → 容量与验证。

</div>

### Scenario 1: A Global Retailer with 200 Stores — POS Must Be Rock Solid, SaaS Is Slow, and the MPLS Contract Is Expiring · 情景一：全球零售 200 站点，POS 必须稳、SaaS 体验差、MPLS 合同即将到期

**Background**: a retail group with 200 stores (20–80 staff each), 2 regional DCs and 1 headquarters. Today:
- Stores use a single MPLS circuit back to the regional DC, and the DC provides internet egress; POS transactions ride MPLS
- Staff use M365 heavily and stores run video surveillance; they complain that "documents open slowly and playback stutters"
- The MPLS contract expires in 12 months and renewal pricing is up 30%
- Stores are unmanned; IT is 12 people (8 at HQ, 4 regional) with no SD-WAN experience
- Requirements: POS availability must not drop, SaaS experience must improve, and **total network cost must not rise**

<div class="zh" markdown="1">

**背景**：零售集团，200 家门店（每家 20–80 人）、2 个区域 DC、1 个总部。现状：
- 门店用单条 MPLS 回区域 DC，再由 DC 出互联网；POS 交易走 MPLS
- 员工大量使用 M365 与门店视频监控，投诉"打开文档慢、监控回放卡"
- MPLS 合同 12 个月后到期，续约价上涨 30%
- 门店网络无人值守，IT 团队 12 人（总部 8 + 区域 4），无 SD-WAN 经验
- 要求：POS 可用性不降低，SaaS 体验改善，**总网络成本不增加**

</div>

**Question**: propose the transport and topology, the migration route, and how "POS and office traffic coexist".

<div class="zh" markdown="1">

**问题**：给出传输与拓扑方案、迁移路线，以及"POS 与办公流量如何共存"。

</div>

<details markdown="1">
<summary>Reference answer</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core idea: split store traffic into "critical transactions" and "office experience"; replace most MPLS bandwidth with "dual Internet + overlay"; protect POS with a lightweight tunnel plus local survivability; keep MPLS only for DC interconnect.**

<div class="zh" markdown="1">

**核心思路：把门店分成"关键交易"与"办公体验"两条流；用"Internet 双线 + 覆盖层"替换大部分 MPLS 带宽，POS 用"轻量隧道 + 本地存活"保障，MPLS 只保留给 DC 互联。**

</div>

| Decision | Choice | Rationale |
|---|---|---|
| **Store transport** | Two local broadband circuits (different carriers) + 4G/5G backup | Far cheaper than MPLS; dual links cover a single-link failure |
| **Overlay** | SD-WAN (or DMVPN Phase 3 plus application recognition) | Needs multi-transport steering and application steering; with no in-house experience, choose managed SD-WAN |
| **POS protection** | POS on a high-priority dedicated tunnel/queue, and **keep a local card-authorisation degraded mode** | Transactions cannot depend on one link; local survivability must queue offline |
| **DC interconnect** | Keep MPLS or move to dedicated circuits (heavy, must-be-stable inter-DC traffic) | DC interconnect does not tolerate public Internet quality |
| **SaaS egress** | Store-local DIA plus cloud security | Removes the store → DC → Internet round trip |
| **Surveillance playback** | Local NVR with event-only upload (or CDN/cloud storage tiering) | Stops bulk video from saturating the store uplink |
| **Management** | Zero-touch provisioning + central policy + tiered alerting | 200 unmanned sites; headcount cannot grow linearly |

<div class="zh" markdown="1">

| 决策 | 选择 | 理由 |
|---|---|---|
| **门店传输** | 两条本地宽带（不同运营商）+ 4G/5G 备份 | 成本远低于 MPLS；双线可覆盖"单线故障" |
| **覆盖层** | SD-WAN（或 DMVPN Phase 3 + 应用识别） | 需要多传输选路与应用分流；团队无经验则选"托管型 SD-WAN" |
| **POS 保障** | POS 流量走"高优先级 + 专用隧道/前传"，并**保留本地刷卡降级模式** | 交易不能依赖单一链路；本地存活要能离线排队 |
| **DC 互联** | 保留 MPLS 或改专线（DC 之间流量大、要求稳） | DC 互联不适用公网质量 |
| **SaaS 出口** | 门店本地 DIA + 云安全 | 消除"门店→DC→Internet"的往返 |
| **监控回放** | 本地 NVR + 仅事件上传（或用 CDN/云存储分层） | 避免大流量占满门店上行 |
| **管理** | 零接触部署 + 集中策略 + 分级告警 | 200 站点无人值守，人力不可线性增长 |

</div>

**Topology**:

<div class="zh" markdown="1">

**拓扑**：

</div>

```
         +------ Regional DC (MPLS/dedicated interconnect retained) ------+
         |        ^ POS and core business                                  |
    +----+-----+                                   +----------+
    | Store A  |-- broadband 1 --+          +------| Store N  |
    | dual+5G  |-- broadband 2 --+-- SD-WAN overlay --| dual+5G |
    | POS/office|-- 5G backup ----+   (app steering)  | POS/office|
    +----------+         -> local DIA -> SaaS/cloud security <-
```

<div class="zh" markdown="1">

```
         ┌──────── 区域 DC（保留 MPLS/专线互联）────────┐
         │        ↑ POS 与核心业务                       │
    ┌────┴─────┐                                   ┌───┴──────┐
    │ 门店 A    │── 宽带1 ──┐                  ┌──│ 门店 N    │
    │ 双线+5G   │── 宽带2 ──┼─ SD-WAN 覆盖 ────┤  │ 双线+5G   │
    │ POS/办公  │── 5G 备份 ┘   （应用分流）     └──│ POS/办公  │
    └──────────┘        ↘ 本地 DIA → SaaS/云安全 ↗  └──────────┘
```

</div>

**Migration route (12 months, aligned to contract expiry)**:

<div class="zh" markdown="1">

**迁移路线（12 个月，与合同到期对齐）**：

</div>

| Phase | Timing | Action | Risk control |
|---|---|---|---|
| 1 Pilot | Months 1–3 | 10 stores on dual links + SD-WAN with POS running in parallel | Keep the MPLS rollback path |
| 2 Bulk | Months 4–8 | 40 stores per batch, brought up by ZTP | Each batch accepted on "POS success rate + SaaS latency" |
| 3 Wind-down | Months 9–11 | All store MPLS retired; DC interconnect re-signed | Keep 5% of stores on MPLS until the contract ends |
| 4 Stabilise | Month 12 | Review cost and experience, freeze the runbook | Cost comparison report |

<div class="zh" markdown="1">

| 阶段 | 时间 | 动作 | 风险控制 |
|---|---|---|---|
| 1 试点 | 月 1–3 | 10 家门店双线 + SD-WAN，POS 并行运行 | 保留 MPLS 回退路径 |
| 2 批量 | 月 4–8 | 每批 40 家，ZTP 上线 | 每批验收"POS 成功率 + SaaS 时延" |
| 3 收尾 | 月 9–11 | 门店 MPLS 全部下线；DC 互联重新签约 | 保留 5% 门店 MPLS 至合同结束 |
| 4 稳定 | 月 12 | 复盘成本与体验，固化 runbook | 成本对比报告 |

</div>

**Cost model (like-for-like)**:

<div class="zh" markdown="1">

**成本模型（对比口径）**：

</div>

| Item | Current (MPLS) | Target (dual broadband + overlay) |
|---|---|---|
| Store circuits | 200 × MPLS unit price | 200 × 2 broadband (about 30–40% of MPLS) |
| Overlay/controller | None | Subscription (per site) |
| Operations headcount | Low (carrier-run) | Medium (monitoring and policy needed) |
| Hidden cost | Poor SaaS experience, insufficient surveillance bandwidth | Training and process required |

<div class="zh" markdown="1">

| 项 | 现状（MPLS） | 目标（双宽带 + 覆盖） |
|---|---|---|
| 门店线路 | 200 × MPLS 单价 | 200 × 2 宽带（约为 MPLS 的 30–40%） |
| 覆盖/控制器 | 无 | 订阅费（按站点） |
| 运维人力 | 低（运营商管） | 中（需监控与策略） |
| 隐性成本 | SaaS 体验差、监控带宽不足 | 需要培训与流程 |

</div>

> 🎯 **The question you will be asked**: is POS over the public Internet safe? — Transactions already carry TLS or proprietary encryption and SD-WAN adds IPsec on top; **the real risk is not "cipher strength" but "can the store keep trading when every link is down"**, so "local degraded mode + offline queueing" is mandatory.

<div class="zh" markdown="1">

> 🎯 **本题最容易被追问**：POS 走公网安全吗？—— 交易本身有 TLS/专有加密，SD-WAN 再加一层 IPsec；**真正的风险不是"加密强度"，而是"链路全断时能否继续营业"**，所以"本地降级模式 + 离线排队"是必须项。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 2: A Manufacturer with 80 Branches and 2 DCs Moves to Hybrid Cloud and Must Keep Multicast (CCTV/Training) · 情景二：制造业 80 分支 + 2 DC，上混合云，且必须保留组播（监控/培训）

**Background**: a manufacturer with 80 plants/warehouses (some remote with only 4G), 2 DCs, partway through moving ERP and MES to a public cloud (IaaS). Requirements:
- Plant-to-DC MES traffic must be stable (production cannot stop)
- Video surveillance (50–200 cameras per plant) needs centralised cross-region viewing; HQ training must be pushed to every plant
- Cloud application access must be "local and auditable"
- Remote plants have only 4G: little bandwidth, high latency

<div class="zh" markdown="1">

**背景**：制造企业，80 个工厂/仓库（部分偏远，仅 4G 可用）、2 个 DC、正在把 ERP 与 MES 部分迁到公有云（IaaS）。要求：
- 工厂到 DC 的 MES 流量必须稳定（生产不能停）
- 视频监控（每厂 50–200 路）需要跨区域集中查看；总部培训需向所有工厂推送
- 云上应用访问要"就近、可审计"
- 偏远工厂只有 4G，带宽小、时延高

</div>

**Question**: propose the transport/overlay/multicast/cloud-access combination and explain how "4G sites fit in".

<div class="zh" markdown="1">

**问题**：给出传输/覆盖/组播/云接入的组合方案，说明"4G 站点如何融入"。

</div>

<details markdown="1">
<summary>Reference answer</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core idea: replace a single hub with "regional hubs + tiered transport"; split multicast into "surveillance (unicast/edge storage)" and "training (application distribution or mVPN)" instead of forcing one technology to solve everything.**

<div class="zh" markdown="1">

**核心思路：用"区域 Hub + 分级承载"替代"单 Hub"；组播按场景拆成"监控（单播/边缘存储）"与"培训（应用分发或 mVPN）"两类，不要用一种技术解决所有问题。**

</div>

| Requirement | Solution | Rationale |
|---|---|---|
| MES (plant → DC) | Dual plant links (broadband + 4G) with IPsec/DMVPN to the regional hub; MES in its own VRF with a priority queue | Production traffic needs stability and priority |
| Remote 4G sites | 4G as primary + local caching/edge compute; reduce interaction frequency (batch synchronisation) | 4G has little bandwidth and high latency; reduce round trips instead of adding bandwidth |
| Video surveillance | **Edge NVR with event upload**; pull streams on demand by unicast when centralised viewing is needed | 200 streams × per-plant uplink saturates; multicast across the WAN is expensive |
| Live training | Application-layer distribution (CDN/streaming server) or regional mVPN | Put the replication point closest to the receivers |
| Cloud access | Regional hubs reach the cloud over dedicated circuits/IPsec; SaaS uses local DIA plus cloud security | Cloud traffic must not hairpin through HQ |
| Segmentation | Four VRFs: production (MES)/office/surveillance/guest | Isolate production from office; surveillance bulk must not squeeze production |

<div class="zh" markdown="1">

| 需求 | 方案 | 理由 |
|---|---|---|
| MES（工厂 → DC） | 工厂双线（宽带 + 4G）+ IPsec/DMVPN 到区域 Hub；MES 走独立 VRF + 优先队列 | 生产流量需要稳定与优先 |
| 偏远 4G 站点 | 4G 主用 + 本地缓存/边缘计算；降低交互频率（批量同步） | 4G 带宽小、时延高，靠"减少往返"而不是"加大带宽" |
| 视频监控 | **边缘 NVR + 事件上传**；需集中查看时按需单播拉流 | 200 路 × 每厂上行会打满；组播跨 WAN 成本高 |
| 培训直播 | 应用层分发（CDN/流媒体服务器）或区域 mVPN | 复制点放在"离接收者最近"的位置 |
| 云接入 | 区域 Hub 通过专线/IPsec 到云；SaaS 类走本地 DIA + 云安全 | 云流量不绕总部 |
| 分段 | 生产（MES）/办公/监控/访客 四个 VRF | 生产与办公隔离，监控大流量不挤占生产 |

</div>

**Topology layering**:

<div class="zh" markdown="1">

**拓扑分层**：

</div>

```
                 +------- Cloud (IaaS: part of ERP/MES) -------+
                 |      dedicated / IPsec (nearest regional hub)|
        +--------+--------+                    +---------------+
        |   Regional hub  |                    |  Regional hub |
        |   North (dual   |                    |  South (dual  |
        |   CPE)          |                    |  CPE)         |
        +---+---------+---+                    +---+-------+---+
      plant group (broadband+4G)  remote 4G      plant group  warehouse
```

<div class="zh" markdown="1">

```
                 ┌──────── 云（IaaS: ERP/MES 部分）────────┐
                 │        专线 / IPsec（区域 Hub 就近）      │
        ┌────────┴────────┐              ┌────────────────┐
        │   区域 Hub 北    │              │   区域 Hub 南   │
        │  （双 CPE）      │              │  （双 CPE）     │
        └───┬────────┬────┘              └───┬────────┬───┘
      工厂群（宽带+4G）  偏远 4G 站点        工厂群      仓库
```

</div>

**Four engineering levers for 4G sites**:

<div class="zh" markdown="1">

**4G 站点的四个工程手段**：

</div>

| Lever | Effect |
|---|---|
| Fewer round trips (local caching/batch sync) | Directly reduces latency sensitivity |
| Header compression/protocol optimisation | Raises effective throughput |
| Queues and shaping (stricter on small links) | Guarantees MES priority |
| Local survivability (keep producing/queueing when the link drops) | A backstop for unstable 4G |

<div class="zh" markdown="1">

| 手段 | 效果 |
|---|---|
| 减少往返（本地缓存/批量同步） | 直接降低时延敏感度 |
| 头部压缩/协议优化 | 提升有效吞吐 |
| 队列与整形（小带宽下更要严格） | 保证 MES 优先 |
| 本地存活（断网可继续生产/排队） | 4G 不稳时的兜底 |

</div>

**Multicast decision table**:

<div class="zh" markdown="1">

**组播决策表**：

</div>

| Scenario | Receivers | Real-time need | Recommendation |
|---|---|---|---|
| Centralised surveillance viewing | Few (security staff) | Medium | On-demand unicast plus edge storage |
| Live training | All 80 plants | High | Application distribution / regional mVPN |
| Software distribution | All | Low | Application layer (distribution server/CDN) |

<div class="zh" markdown="1">

| 场景 | 接收者 | 实时性 | 推荐 |
|---|---|---|---|
| 监控集中查看 | 少量（安保） | 中 | 按需单播 + 边缘存储 |
| 培训直播 | 全部 80 厂 | 高 | 应用层分发 / 区域 mVPN |
| 软件分发 | 全部 | 低 | 应用层（分发服务器/CDN） |

</div>

> ⚠️ **The question you will be asked**: why not solve surveillance with mVPN? — Because surveillance is "a few people watching many cameras"; mVPN would replicate every stream to every site, which is unacceptable in cost and bandwidth. **Edge storage plus on-demand streaming wins on both cost and experience.**

<div class="zh" markdown="1">

> ⚠️ **本题最容易被追问**：为什么不用 mVPN 解决监控？—— 因为监控是"少数人看多数摄像头"，用 mVPN 会让"每路视频在所有站点复制"，成本与带宽都不可接受；**边缘存储 + 按需拉流**在成本与体验上都更优。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 3: After Three Acquisitions, Three WANs (L3 MPLS, L2 VPLS, Internet DMVPN) Must Become One · 情景三：并购后 3 套 WAN（L3 MPLS、L2 VPLS、Internet DMVPN）要合成一套

**Background**: the group acquired three companies. Current WANs:

<div class="zh" markdown="1">

**背景**：集团并购 3 家公司，WAN 现状：

</div>

| Company | Transport | Sites | Topology | Problem |
|---|---|---|---|---|
| A | L3 MPLS (any-to-any) | 60 | Any-to-any | High cost, slow change |
| B | L2 VPLS | 25 | Large Layer 2 | One loop took the network down for 4 hours |
| C | Internet + DMVPN P2 | 40 | Hub-spoke | Slow spoke-to-spoke, no summarisation |

<div class="zh" markdown="1">

| 公司 | 承载 | 站点数 | 拓扑 | 问题 |
|---|---|---|---|---|
| A | L3 MPLS（任意互通） | 60 | Any-to-Any | 成本高、变更慢 |
| B | L2 VPLS | 25 | 大二层 | 一次环路断网 4 小时 |
| C | Internet + DMVPN P2 | 40 | Hub-Spoke | Spoke 互通慢、无汇总 |

</div>

Requirement: merge into **one WAN architecture** within 18 months, keep the necessary isolation (finance/R&D), do not interrupt production, and do not raise total cost.

<div class="zh" markdown="1">

要求：18 个月内合并为**一套 WAN 架构**，保留必要隔离（财务/研发），不中断生产，且总体成本不上升。

</div>

**Question**: propose the target architecture (transport, overlay, routing, segmentation) plus each company's migration strategy and sequencing.

<div class="zh" markdown="1">

**问题**：给出目标架构（传输、覆盖、路由、分段），以及三家各自的迁移策略与先后顺序。

</div>

<details markdown="1">
<summary>Reference answer</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core idea: the target is "regional hubs + a mix of L3 VPN and overlay"; unify routing and addressing before unifying transport; B's VPLS must be dismantled first (highest risk) and C's DMVPN must be upgraded to Phase 3.**

<div class="zh" markdown="1">

**核心思路：目标形态选"区域 Hub + L3 VPN/覆盖层混合"，先"统一路由与地址"再"统一承载"；B 的 VPLS 必须最先拆（风险最高），C 的 DMVPN 需要升级到 Phase 3。**

</div>

| Decision | Choice | Rationale |
|---|---|---|
| **Target transport** | Core sites: L3 MPLS (or dedicated circuits); ordinary sites: Internet + overlay | Balances cost and experience; avoids the cost of all-MPLS |
| **Overlay** | DMVPN Phase 3 or SD-WAN (with application recognition) | Needs "summarisation + direct paths"; SD-WAN handles multi-transport more easily |
| **Topology** | Two levels: 3–4 regional hubs plus sites | Avoids one hub carrying 125 sites |
| **Routing** | Regional hubs summarise towards the core; the core keeps only regional prefixes | Contains the routing table and the convergence scope |
| **Segmentation** | Separate VRFs for finance/R&D (2 segments) plus a common segment | Isolation needs are limited; avoid overdesign |
| **Addressing** | Unified addressing; overlapping ranges transitioned via VRF or NAT | The first hurdle of any merger |

<div class="zh" markdown="1">

| 决策 | 选择 | 理由 |
|---|---|---|
| **目标承载** | 核心站点：L3 MPLS（或专线）；一般站点：Internet + 覆盖层 | 成本与体验平衡；避免单一 MPLS 的高成本 |
| **覆盖层** | DMVPN Phase 3 或 SD-WAN（含应用识别） | 需要"汇总 + 直连"；SD-WAN 更易多传输 |
| **拓扑** | 两级：区域 Hub（3–4 个）+ 站点 | 避免"单 Hub 承载 125 站点" |
| **路由** | 区域 Hub 汇总后向核心宣告；核心只保留区域前缀 | 控制路由表与收敛范围 |
| **分段** | 财务/研发独立 VRF（2 段） + 通用段 | 隔离需求有限，避免过度设计 |
| **地址** | 统一编址，重叠段用 VRF 或 NAT 过渡 | 并购整合的第一道坎 |

</div>

**Migration order (the key: dismantle the riskiest first, build the shared foundation first)**:

<div class="zh" markdown="1">

**迁移顺序（关键：先拆风险最高的，先建公共底座）**：

</div>

| Phase | Timing | Target | Action | Downtime |
|---|---|---|---|---|
| 0 | Months 1–2 | All | Asset and traffic discovery, address-conflict inventory, site tiering | None |
| 1 | Months 2–5 | All | Build regional hubs (overlay and segmentation included); unify DNS/address plan | None |
| 2 | Months 5–8 | **B (VPLS)** | Split two out of three ways: keep the two points that must stay Layer 2 (VLL), move the rest to L3 at the regional hub | ≤30 min per site (nights) |
| 3 | Months 8–12 | **C (DMVPN)** | Upgrade to Phase 3 (or move to SD-WAN), introduce summarisation, move spokes into regional hubs | None (run in parallel) |
| 4 | Months 12–16 | **A (MPLS)** | Re-contract per region (no more global any-to-any), move sites across one at a time | None (dual advertisement during transition) |
| 5 | Months 16–18 | All | Retire legacy links, clean up old routing domains, run acceptance drills | Within a window |

<div class="zh" markdown="1">

| 阶段 | 时间 | 对象 | 动作 | 停机 |
|---|---|---|---|---|
| 0 | 月 1–2 | 全部 | 资产与流量摸底、地址冲突清单、站点分级 | 无 |
| 1 | 月 2–5 | 全部 | 建区域 Hub（含覆盖层与分段）；统一 DNS/地址规划 | 无 |
| 2 | 月 5–8 | **B（VPLS）** | 二拆三：保留 2 个必须二层的点（VLL），其余改 L3 接入区域 Hub | 每站点 ≤30 min（夜间） |
| 3 | 月 8–12 | **C（DMVPN）** | 升级 Phase 3（或改 SD-WAN），引入汇总，Spoke 迁入区域 Hub | 无（并行运行） |
| 4 | 月 12–16 | **A（MPLS）** | 按区域重新签约（不再全球 any-to-any），站点逐个改挂 | 无（BGP 双宣告过渡） |
| 5 | 月 16–18 | 全部 | 下线旧链路、清理旧路由域、验收演练 | 窗口内 |

</div>

**Why must B be dismantled first?**

<div class="zh" markdown="1">

**为什么 B 必须先拆？**

</div>

| Risk | Explanation |
|---|---|
| Large Layer 2 plus loops | One mis-cabling can take out 25 sites (it already happened) |
| STP diameter | The more sites, the slower convergence and the less controllable broadcast |
| Conflict with the target | A Layer 2 domain cannot naturally fit "regional hubs + summarisation" |
| Cost rises over time | The more sites, the more expensive the split becomes |

<div class="zh" markdown="1">

| 风险 | 说明 |
|---|---|
| 大二层 + 环路 | 一次误接可以打断 25 个站点（已发生过） |
| STP 直径 | 站点越多，收敛越慢，广播越不可控 |
| 与目标架构冲突 | 二层域无法自然融入"区域 Hub + 汇总" |
| 迁移成本随时间上升 | 站点越多，拆分越贵 |

</div>

**Why touch A last?**

<div class="zh" markdown="1">

**为什么 A 最后动？**

</div>

| Reason | Explanation |
|---|---|
| It is the most stable | L3 MPLS any-to-any is the least painful status quo |
| Contract constraints | Re-contracting takes time and negotiation |
| It is the rollback base | While the other two migrate, A's network is temporary transport and a comparison baseline |

<div class="zh" markdown="1">

| 原因 | 说明 |
|---|---|
| 它最稳 | L3 MPLS any-to-any 是"最不痛"的现状 |
| 合同约束 | 重新签约需要时间与谈判 |
| 作为"回退底座" | 其他两家迁移期间，A 的网络可作为临时承载与对照 |

</div>

**Two hard moves for unified routing and addressing**:

<div class="zh" markdown="1">

**统一路由与地址的两个硬动作**：

</div>

| Move | Approach |
|---|---|
| Address conflicts | List overlapping ranges → prefer "change one end" (new sites use new addressing) → where impossible, isolate with VRFs and transition via NAT |
| Route summarisation | One summary prefix per region; the core keeps only regional level; avoid "500 global specifics" |
| Redistribution | One-way plus whitelist; join old and new routing domains with a border router rather than two-way redistribution |

<div class="zh" markdown="1">

| 动作 | 做法 |
|---|---|
| 地址冲突 | 列出重叠段 → 优先"改一端"（新建站点用新编址）→ 无法改的用 VRF 隔离 + NAT 过渡 |
| 路由汇总 | 每个区域一个汇总前缀，核心只保留区域级；避免"全球 500 条明细" |
| 重分发 | 单向 + 白名单；旧路由域与新域之间用"边界路由器"而非"双向重分发" |

</div>

> 🎯 **The question you will be asked**: why not standardise on MPLS any-to-any? — Because **cost rises** (125 sites fully interconnected) while **most sites have no traffic between them**. The point of the target architecture is to **layer by traffic matrix**, not to "standardise on the most expensive option".

<div class="zh" markdown="1">

> 🎯 **本题最容易被追问**：为什么不统一换成 MPLS any-to-any？—— 因为**成本上升**（125 站点全互通）且**大多数站点之间没有流量**。目标架构的核心是"**按流量矩阵分层**"，而不是"统一成最贵的那种"。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

---

## Scenario Analysis Framework: The Standard Route for WAN Architecture Scenarios · 情景分析框架：WAN 架构类场景的通用套路

```
1 Draw the traffic matrix before drawing the topology
   Who talks to whom? In what proportion? Latency-sensitive? -> hub-spoke / partial mesh / any-to-any
2 Tier the sites (L1-L4) with one standard kit per tier
   Once tiered, 200 sites only need to be designed four times
3 Choose transport by "business criticality x available circuits x cost"
   L2 only when Layer 2 is mandatory; Internet always with an overlay and probing
4 Set redundancy layer by layer: link -> CPE -> carrier -> physical path
   Before adding a layer, ask whether the single point below has been removed
5 Choose the overlay: tunnel count x direct-path need x multicast need -> phase/technology
   "summarise + direct" -> Phase 3; "encryption without tunnels" -> GET VPN (private networks only)
6 Set segmentation: VRF/RT matrix plus permitted paths; prove it with probes, not configuration
7 Set routing: summary boundaries, one-way whitelisted redistribution, the role of BGP
8 Set QoS: at most six classes + shaping on every egress + rate-limited LLQ
9 Compute capacity: hub peak x simultaneity, encrypted throughput, tunnel count, routing table
10 Hand over acceptance: kill the primary link / kill a carrier / kill the hub / MTU / congestion, and time each one
```

<div class="zh" markdown="1">

```
① 先画"流量矩阵"，不是先画拓扑
   谁和谁通？比例多少？时延敏感吗？→ 决定 Hub-Spoke / 部分网状 / Any-to-Any
② 站点分级（L1–L4），每级一套标准套件
   分级之后，200 个站点只需要设计 4 次
③ 选传输：按"业务关键度 × 可获得线路 × 成本"
   L2 只在"必须二层"时用；Internet 必须配覆盖层与探测
④ 定冗余：链路 → CPE → 运营商 → 物理路径，逐层消除单点
   每加一层先问"上一层单点消除了吗"
⑤ 定覆盖：隧道数 × 是否直连 × 是否组播 → 阶段/技术
   要"汇总 + 直连" → Phase 3；要"无隧道加密" → GET VPN（仅私网）
⑥ 定分段：VRF/RT 矩阵 + 允许路径；证明靠探测不靠配置
⑦ 定路由：汇总边界、重分发单向白名单、BGP 用途
⑧ 定 QoS：分类（≤6 类）+ 每个出口整形 + LLQ 限速
⑨ 算容量：Hub 峰值×同时率、加密后吞吐、隧道数、路由表
⑩ 给验收：断主链路/断运营商/断 Hub/MTU/拥塞，逐项计时
```

</div>

**In one sentence**: **the WAN architecture question does not test whether you know how many phases DMVPN has; it tests whether, on a limited budget, you can organise 200 sites you do not control into one network that is predictable, operable and scalable.**

<div class="zh" markdown="1">

**一句话总结**：**WAN 架构题考的不是"你知不知道 DMVPN 有几个阶段"，而是"你能不能用有限的预算，把 200 个不可控的站点组织成一张可预测、可运维、可扩展的网络"。**

</div>

---

## Chapter Summary · 本章小结

WAN design looks like choosing between "MPLS or Internet"; in essence it is **using overlays, routing and QoS to turn uncontrollable transport into a controllable service**:

<div class="zh" markdown="1">

WAN 设计表面在选"MPLS 还是 Internet"，本质上在**用覆盖层、路由与 QoS，把不可控的传输变成可控的服务**：

</div>

| Theme | Essence | Three questions you must answer | Pass/fail criterion |
|---|---|---|---|
| **SLA gap** | The carrier guarantees only its own segment | How much is left end to end? Who fills it? | End-to-end availability is measured, not assumed |
| **Transport model** | Who owns the routing decides the architecture | L2 or L3? Who runs the routing? Can it be operated? | Cost and operational complexity both fit the team |
| **Redundancy** | Layer by layer, never in one leap | Link, CPE, carrier, physical path — which single points remain? | Every single-point failure has a defined degradation path |
| **Overlay** | Buying O(n) configuration for O(n²) capability | Tunnels? Multicast? Encryption? MTU? | Convergence and throughput both meet target after failures |
| **Routing** | Summarise at the edge, control at the core | Where do summaries live? Where does redistribution run? | Failures converge in seconds and paths remain explainable |
| **Capacity** | Hub peak × simultaneity, after encryption | Bandwidth, throughput, tunnels, table | No saturated hub under peak load |
| **Migration** | A self-consistent intermediate state | Who redistributes? Where is the default from? | No loops or black holes at any point in the migration |

<div class="zh" markdown="1">

| 主题 | 本质 | 三个必答问题 | 成败判据 |
|---|---|---|---|
| **传输模型** | 谁负责路由、谁负责质量 | 有必须二层的业务吗？核心业务能容忍 Internet 吗？ | 每类站点都有明确承载与 SLA 缺口说明 |
| **连接与冗余** | 逐层消除单点 | 链路/CPE/运营商/物理路径，哪层还有单点？ | 任一单点故障有明确降级与收敛时间 |
| **覆盖技术** | 隧道数 × 控制面复杂度 | 需要直连吗？需要汇总吗？需要组播吗？ | Spoke 直连可用、MTU 无黑洞、SA 数可控 |
| **虚拟化与分段** | 用共享换隔离 | 分段是路由隔离还是安全隔离？ | 探测证明跨段不可达；基线可校验 |
| **规模模型** | 站点分级 + 标准套件 | 加一个站点要动几处？ | 新站点 ZTP 上线、变更模板化 |
| **QoS 与容量** | 每个出口都要整形 | 拥塞发生在哪？谁先死？ | 上行灌满时语音仍达标；Hub 有 N−1 |

</div>

**Four judgements that run through the whole chapter**:

<div class="zh" markdown="1">

**四条贯穿全章的判断**：

</div>

1. **The SLA gap is always yours to fill**: the carrier guarantees its segment only; end-to-end is your problem.
2. **"Link up" is not "path usable"**: in the WAN, state must come from routing or active probing, never from interface status.
3. **Capacity is multiplied by encryption and divided by N−1**: the nameplate is a marketing number; the measurement is the design number.
4. **Migration is part of the design**: if you cannot draw the network at 50% migrated, you have not finished designing.

<div class="zh" markdown="1">

1. **SLA 缺口必须有人补**：运营商只保它那段，端到端是你的责任。
2. **"链路 up" 不等于"路径可用"**：WAN 里必须有主动检测（BGP/BFD/SLA）。
3. **容量按峰值与加密后实测算**：Hub 与隧道是最容易"上线即瓶颈"的地方。
4. **可扩展性 = 运营成本的可扩展性**：能在模板里加一个站点，才是真的可扩展。

</div>
