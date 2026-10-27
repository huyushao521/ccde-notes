# Chapter 6: Transport Technologies · 第 6 章：传输技术

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapter 6 (pp. 260–299)

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译 | 原书第 260-299 页

</div>

---

## Topics Covered · 本章涵盖主题

- **Layer 2 media access**: Layer 2 transport and connectivity models
- **Virtual Private Wire Service design considerations**: VPWS models, concepts and the corresponding network design elements
- **EVPN design models**: EVPN concepts, protocols and the corresponding network design elements

<div class="zh" markdown="1">

- **二层介质接入**：二层传输和连接模型
- **虚拟专线服务设计考量**：VPWS 模型、概念和对应的网络设计要素
- **EVPN 设计模型**：EVPN 概念、协议和对应的网络设计要素

</div>

---

## Chapter Overview: Transport Is "Somebody Else's Network" · 本章导读：传输层是"别人家的网"

Chapters 6 and 7 (Layer 2 technologies) are easy to confuse, so let us draw the line first:

<div class="zh" markdown="1">

第 6 章和第 7 章（二层技术）容易混淆，先划清界限：

</div>

| Chapter | Perspective | Focus |
|---------|-------------|-------|
| **Chapter 6, Transport Technologies** | **Looking outward** — the service the carrier sells | What exactly am I buying from the carrier? |
| **Chapter 7, Layer 2 Technologies** | **Looking inward** — the Layer 2 network I build myself | How do I design my own STP, VLANs and trunks |

<div class="zh" markdown="1">

| 章节 | 视角 | 关注点 |
|------|------|--------|
| **第 6 章 传输技术** | **向外看**——运营商提供的服务 | 我从运营商手里买到的到底是什么？ |
| **第 7 章 二层技术** | **向内看**——自己建的二层网络 | 我自己的 STP、VLAN、Trunk 怎么设计 |

</div>

In other words, this chapter is about **service procurement and selection**, not device configuration. That matters especially for CCDE, because the first step in a great many real designs is: **should this site connect over MPLS L2VPN, over L3VPN, or straight over the Internet with SD-WAN?**

<div class="zh" markdown="1">

换句话说，本章讨论的是**服务采购与选型**，而不是设备配置。这对 CCDE 尤其重要，因为大量真实设计的第一步就是：**这个站点应该接 MPLS L2VPN、L3VPN、还是直接走 Internet + SD-WAN？**

</div>

> ⚠️ **The design tension of this chapter**: Layer 2 services deliver maximum flexibility and "migration without anyone noticing", but the price is a **larger failure domain, an invisible control plane and limited scalability**. Almost every design trade-off in this category is fundamentally a balancing act between those two sides.

<div class="zh" markdown="1">

> ⚠️ **本章的设计张力**：二层服务能提供最大的灵活性和"无感迁移"，但代价是**故障域扩大、控制平面不可见、可扩展性受限**。几乎所有这一类的设计取舍，本质都在权衡这一对矛盾。

</div>

---

## Foundation Topics · 基础内容

### Layer 2 Media Access · 二层介质接入

Carriers understand the importance of offering a flexible and responsive network architecture that supports current and future requirements without large-scale change. As a result, nearly every service provider has migrated part or all of its core infrastructure to MPLS. That lets them use the MPLS infrastructure to deliver both L2 and L3 services over one common MPLS core.

<div class="zh" markdown="1">

运营商理解提供灵活和响应迅速的网络架构的重要性，该架构支持当前和未来需求而无需大规模变更。因此，几乎所有服务提供商都已部分或完全将核心基础设施迁移到 MPLS。这使他们能够利用 MPLS 基础设施，通过一个统一的 MPLS 核心为客户提供 L2 和 L3 服务。

</div>

**Key insight**: the core of a modern carrier is **MPLS**, and Layer 2 services are merely "emulation running on top of MPLS". Therefore:

<div class="zh" markdown="1">

**关键理解**：现代运营商的核心是 **MPLS**，二层服务只是"跑在 MPLS 上的仿真"。所以：

</div>

```
What the subscriber sees: a transparent Ethernet wire (or a transparent LAN)
What actually carries it: CE → PE (attachment circuit, AC) → MPLS label switching → PE → CE (pseudowire, PW)
```

<div class="zh" markdown="1">

```
订户看到的：一条透明的以太网线（或一个透明 LAN）
实际承载的：CE → PE（接入电路 AC）→ MPLS 标签交换 → PE → CE（伪线 PW）
```

</div>

> 💡 **Why carriers turn everything into "labels"**: because MPLS lets one core carry different services (L2VPN, L3VPN, multicast VPN) with the same infrastructure, and **economies of scale** are the carrier's core driver. This also explains why EVPN later uses BGP: it follows the mature BGP control-plane approach of L3VPN.

<div class="zh" markdown="1">

> 💡 **为什么运营商要把所有东西都变成"标签"**：因为 MPLS 可复用同一套核心承载不同服务（L2VPN、L3VPN、组播 VPN），**规模经济**是运营商的核心驱动力。这也解释了后面 EVPN 为什么用 BGP——它沿用了 L3VPN 成熟的 BGP 控制平面思路。

</div>

#### Carrier Ethernet · Carrier Ethernet（载波以太网）

Service providers that deliver modern Layer 2 Ethernet services (such as metro Ethernet) are called Carrier Ethernet providers.

<div class="zh" markdown="1">

现代提供二层以太网服务（如城域以太网）的服务商被称为 Carrier Ethernet 提供商。

</div>

**The five Carrier Ethernet attributes defined by the MEF** (the usual test for "is this really a Carrier Ethernet service"):

<div class="zh" markdown="1">

**MEF 定义的 Carrier Ethernet 五大属性**（判断"这是不是真正的 Carrier Ethernet 服务"的常用标准）：

</div>

| Attribute | Meaning | Practical impact on design |
|-----------|---------|---------------------------|
| **Standardized services** | Three standard services: E-Line / E-LAN / E-Tree | Service names are uniform, so you can compare prices and interconnect across carriers |
| **Scalability** | Bandwidth from the 1M range to 10G+, and site counts that scale massively | Supports business growth without re-architecting |
| **Reliability** | Service-level SLAs, including protection switching | Decides whether it can carry voice or transaction-critical traffic |
| **Quality of service (QoS)** | Multiple classes of service, markable per frame | Voice and bulk transfer can share one circuit |
| **Service management** | OAM and SLA measurements (latency, jitter, loss) | **This is the biggest difference from "bare fiber or bare Internet"** |

<div class="zh" markdown="1">

| 属性 | 含义 | 对设计的实际影响 |
|------|------|----------------|
| **标准化服务** | E-Line / E-LAN / E-Tree 三种标准服务 | 服务名称统一，可跨运营商比价与对接 |
| **可扩展性** | 带宽从 1M 级到 10G+，站点数可大规模扩展 | 支持业务增长，不用重新架构 |
| **可靠性** | 服务级 SLA，含保护倒换 | 决定能否承载语音/交易类关键业务 |
| **服务质量 (QoS)** | 多等级 CoS，可按帧标记 | 语音与批量传输可共用一条电路 |
| **服务管理** | 有 OAM 与 SLA 度量（延迟、抖动、丢包） | **这是与"裸光纤/裸互联网"最大的差别** |

</div>

**Business drivers that push providers toward modern L2 services**:

<div class="zh" markdown="1">

**服务商采用现代 L2 服务的业务驱动力**：

</div>

| Driver | Explanation |
|--------|-------------|
| **Flexible products** | Customized solutions that flexibly mix services, data rates and revenue (EPL, EVPL, E-LAN) |
| **Flexible bandwidth** | Configurable 1G/10G Ethernet physical links with SLA-based fractional access rates |
| **Flexible media access** | Supports many access networks: WiMAX, IP DSLAM, fiber Ethernet, copper Ethernet and so on |
| **Cost savings** | Ethernet infrastructure carries lower CAPEX than legacy hardware such as ATM |
| **Scalable services** | Serve a large number of customers over one common infrastructure, growing revenue |

<div class="zh" markdown="1">

| 驱动力 | 说明 |
|--------|------|
| **灵活的产品** | 定制化解决方案，灵活混合服务、数据速率和收入（EPL、EVPL、E-LAN） |
| **灵活的带宽** | 可配置 1G/10G 以太网物理链路，提供基于 SLA 的分数线路接入速率 |
| **灵活的介质接入** | 支持多种接入网络：WiMAX、IP DSLAM、光纤以太网、铜线以太网等 |
| **成本节约** | 与 ATM 等传统硬件相比，以太网基础设施提供更低的 CAPEX |
| **可扩展服务** | 通过一个通用基础设施支持大量客户，增加收入 |

</div>

### Metro Ethernet Service Types · Metro Ethernet 服务类型

| Service type | Topology | Description | Typical thing it replaces |
|--------------|----------|-------------|---------------------------|
| **E-Line** | Point-to-point (P2P) | An Ethernet circuit between two UNIs, for example VPWS | Leased lines, FR/ATM PVCs |
| **E-LAN** | Multipoint-to-multipoint (MP2MP) | An Ethernet circuit among two or more UNIs, for example VPLS | Self-built Layer 2 campus interconnect, ATM LANE |
| **E-Tree** | Point-to-multipoint | A tree structure where leaves can talk only to the root, never to each other. Similar to Private VLAN | Multicast distribution, video source to many receivers |

<div class="zh" markdown="1">

| 服务类型 | 拓扑 | 说明 | 典型替代对象 |
|---------|------|------|------------|
| **E-Line** | 点对点 (P2P) | 两个 UNI 之间的以太网电路，如 VPWS | 租用线路、FR/ATM PVC |
| **E-LAN** | 多点到多点 (MP2MP) | 两个或多个 UNI 之间的以太网电路，如 VPLS | 自建二层园区互联、ATM LANE |
| **E-Tree** | 点对多点 | 树状结构，叶子只能与根通信，不能互相通信。类似 Private VLAN | 组播分发、视频源到多接收点 |

</div>

> 💡 **E-Tree is the most easily overlooked yet very practical service**: it naturally provides "isolation between leaves", which suits **video distribution, content push and cell-site backhaul** — any "one source, many receivers" scenario. If you tried to meet the same need with E-LAN, you would have to build the isolation policy yourself on the customer side.

<div class="zh" markdown="1">

> 💡 **E-Tree 是最容易被忽略但很实用的服务**：它天然实现了"叶子之间隔离"，非常适合**视频分发、内容推送、基站回传**这类"一个源、多个接收者"的场景。若用 E-LAN 实现同类需求，必须在客户侧自己做隔离策略。

</div>

### Metro Ethernet Transport Models · Metro Ethernet 传输模型

| Service type | Port-based | VLAN-based |
|--------------|-----------|------------|
| **E-Line** | Ethernet Private Line (EPL) | Ethernet Virtual Private Line (EVPL) |
| **E-LAN** | Ethernet Private LAN (EPLAN) | Ethernet Virtual Private LAN (EVPLAN) |

<div class="zh" markdown="1">

| 服务类型 | 基于端口 | 基于 VLAN |
|---------|---------|----------|
| **E-Line** | Ethernet Private Line (EPL) | Ethernet Virtual Private Line (EVPL) |
| **E-LAN** | Ethernet Private LAN (EPLAN) | Ethernet Virtual Private LAN (EVPLAN) |

</div>

**There is only one core difference: is the whole port dedicated, or do multiple EVCs share one port?**

<div class="zh" markdown="1">

**核心区别只有一个：整条端口被独占，还是多个 EVC 共享一个端口？**

</div>

```
EPL (port-based)                     EVPL (VLAN-based)
─────────────────                    ─────────────────
CE ──[whole port]── PE               CE ──[VLAN 10]──┐
     every frame uses one EVC                  [VLAN 20]──┼─ PE
     no other service possible                  [VLAN 30]──┘
                                      different VLANs map to different EVCs (or remotes)
```

<div class="zh" markdown="1">

```
EPL（端口型）                         EVPL（VLAN 型）
─────────────                        ─────────────
CE ──[整口]── PE                     CE ──[VLAN 10]──┐
     所有帧走同一条 EVC                        [VLAN 20]──┼─ PE
     不能用其他服务                             [VLAN 30]──┘
                                        不同 VLAN 映射到不同 EVC（或不同远端）
```

</div>

| Dimension | EPL (port-based) | EVPL (VLAN-based) |
|-----------|------------------|-------------------|
| Port utilization | Dedicated, therefore wasted | Reused, therefore saved |
| Transparency | **Fully transparent** — the customer's VLANs and frames pass through unchanged | VLANs must match, and the carrier may rewrite VLAN tags |
| Suited to | Strictly transparent transport (trunk interconnect with tags, DCI) | Cost-sensitive multi-site, multi-service scenarios |
| Cost | High (port dedicated) | Low (billed per EVC) |
| Typical pitfall | You pay even for an idle port | VLAN planning must be coordinated with the carrier; **any VLAN change means a carrier ticket** |

<div class="zh" markdown="1">

| 维度 | EPL（基于端口） | EVPL（基于 VLAN） |
|------|---------------|------------------|
| 端口利用 | 独占，浪费 | 复用，节省 |
| 透传能力 | **完全透明**，客户的 VLAN/帧全部原样传输 | 需要匹配 VLAN，运营商可能改写 VLAN 标签 |
| 适合 | 需要严格透明传输（带标签的 Trunk 互联、DCI） | 多站点、多服务的成本敏感场景 |
| 成本 | 高（端口独占） | 低（按 EVC 计费） |
| 典型陷阱 | 端口闲置也付费 | VLAN 规划必须与运营商协调，**改 VLAN 要联系运营商** |

</div>

### Metro Ethernet Components · Metro Ethernet 组件

| Component | Definition |
|-----------|-----------|
| **UNI (User Network Interface)** | The physical demarcation point between the connection and the subscriber, also called port-based ME |
| **EVC (Ethernet Virtual Connection)** | An association of two or more UNIs that restricts service frames to the EVC. When multiple EVCs share one UNI, 802.1Q VLAN tags are used, which means VLAN-based (EVPL) |
| **NNI (Network Node Interface)** | The interface between carrier networks (often used for carrier-to-carrier interconnection) |
| **CoS / bandwidth profile** | Bandwidth tiers and priority queues definable on each EVC |

<div class="zh" markdown="1">

| 组件 | 定义 |
|------|------|
| **UNI (用户网络接口)** | 连接和订户之间的物理分界点，也称为基于端口的 ME |
| **EVC (以太网虚拟连接)** | 两个或多个 UNI 的关联，限制服务帧在 EVC 内交换。多个 EVC 共享一个 UNI 时使用 802.1Q VLAN 标识，即基于 VLAN (EVPL) |
| **NNI (网络节点接口)** | 运营商网络之间的接口（常用于跨运营商对接） |
| **CoS / 带宽配置文件** | 每个 EVC 上可定义带宽档位与优先级队列 |

</div>

> ⚠️ **The UNI is the dividing line of responsibility**: when something breaks, "is the problem inside the UNI (customer responsibility) or outside it (carrier responsibility)" decides who acts. A design must make the UNI position explicit, and confirm whether the carrier offers UNI-side loopback testing.

<div class="zh" markdown="1">

> ⚠️ **UNI 是责任分界线**：故障发生时，"问题在 UNI 之内（客户责任）还是之外（运营商责任）"决定谁来处理。设计中必须明确 UNI 位置，并确认运营商是否提供 UNI 侧环回测试能力。

</div>

---

## Virtual Private Wire Service (VPWS) Design Considerations · 虚拟专线服务设计考量

VPWS is built on the pseudowire (PW) concept (RFC 3916): a connection between two edge nodes that ties two attachment circuits (ACs) together and emulates a direct AC connection.

<div class="zh" markdown="1">

VPWS 基于伪线 (Pseudowire, PW) 概念（RFC 3916），是两个边缘节点之间的连接，将两条接入电路 (AC) 连接起来，模拟直接 AC 连接。

</div>

**In one sentence**: VPWS = **pulling an "invisible cable" from point A to point B**. It does no MAC learning and no switching — it just moves frames.

<div class="zh" markdown="1">

**一句话理解**：VPWS = **把一条"看不见的网线"从 A 点拉到 B 点**。它不做 MAC 学习，不做交换，只逐帧搬运。

</div>

### Key PW Mechanisms · PW 的关键机制

```
      AC1                PW (pseudowire)                AC2
CE1 ──[attachment circuit]── PE1 ═══════════════════ PE2 ──[attachment circuit]── CE2
                             │  encapsulation: control word + label stack  │
                             └─────────────────────────────────────────────┘
```

<div class="zh" markdown="1">

```
      AC1                PW（伪线）                 AC2
CE1 ──[接入电路]── PE1 ═══════════════════ PE2 ──[接入电路]── CE2
                      │  封装：控制字 + 标签栈  │
                      └────────────────────────┘
```

</div>

| Element | Description |
|---------|-------------|
| **AC (Attachment Circuit)** | The customer-side attachment circuit, which may be a physical port or a VLAN |
| **PW (Pseudowire)** | A logical connection carried over MPLS that encapsulates and transparently forwards AC frames |
| **Control word** | Preserves frame ordering, pads short frames, and handles fragmentation and misordering |
| **Signaling** | LDP (Martini) / BGP (Kompella) / static configuration |

<div class="zh" markdown="1">

| 要素 | 说明 |
|------|------|
| **AC (Attachment Circuit)** | 客户侧接入电路，可以是物理端口或 VLAN |
| **PW (Pseudowire)** | 承载在 MPLS 上的逻辑连接，把 AC 帧封装后透传 |
| **控制字 (Control Word)** | 保证帧顺序、填充短帧，处理分片与乱序 |
| **信令方式** | LDP（Martini 方式）/ BGP（Kompella 方式）/ 静态配置 |

</div>

> 💡 **Two signaling schools** (extended material):
> - **Martini (LDP)**: per-PW signaling, simple and intuitive, requires LDP sessions between PEs. **The mainstream deployment approach**
> - **Kompella (BGP)**: BGP carries the PW information, allows auto-discovery, scales better, and has a more complex configuration model
>
> This distinction reappears in the EVPN section — EVPN essentially takes Kompella's "BGP auto-discovery" idea and develops it fully.

<div class="zh" markdown="1">

> 💡 **两个信令流派**（扩展知识点）：
> - **Martini（LDP）**：逐条 PW 信令，简单直观，PE 间需 LDP 会话。**主流部署方式**
> - **Kompella（BGP）**：BGP 承载 PW 信息，可自动发现，扩展性更好，配置模型复杂
>
> 这个区别在 EVPN 部分会再次出现——EVPN 本质上就是把 Kompella 的"BGP 自动发现"思路发扬光大。

</div>

### PW Transport Connection Models · PW 传输连接模型

| Model | Characteristics | Where it fits |
|-------|-----------------|---------------|
| **VLAN-based** | VLANs defined on one physical port can be switched to different remote PEs | The customer does not have to change routing or IP addresses (similar to a traditional FR/ATM WAN) |
| **Port-based** | Tunnels all traffic entering the AC physical port and delivers it unchanged to the remote PE | Replacing legacy WAN serial links with high-speed P2P links in an L3 network; data center Layer 2 interconnect |

<div class="zh" markdown="1">

| 模型 | 特点 | 适用场景 |
|------|------|---------|
| **基于 VLAN** | 物理端口上定义的 VLAN 可交换到不同的远端 PE | 客户不需要更改路由和 IP 地址（类似传统 FR/ATM WAN） |
| **基于端口** | 隧道化进入 AC 物理端口的所有流量，不变地传输到远端 PE | L3 网络为传统 WAN 串行链路需替换为高速 P2P 链路；数据中心二层互联 |

</div>

> ⚠️ **This is the single most important design decision in VPWS**:
>
> | Choice | Benefit | Risk |
> |--------|---------|------|
> | VLAN-based | One port can serve many sites, low cost | VLAN plans at both ends must match, and carrier-side VLAN changes hit the customer |
> | Port-based | Fully transparent, the customer may use VLANs and trunks freely | A dedicated port is expensive, and **STP BPDUs pass through too** → the two STP domains merge |

<div class="zh" markdown="1">

> ⚠️ **这是 VPWS 最重要的设计决策**：
>
> | 选择 | 好处 | 风险 |
> |------|------|------|
> | 基于 VLAN | 单端口可接多站点，成本低 | 两端 VLAN 规划须一致，运营商改 VLAN 影响客户 |
> | 基于端口 | 完全透明，客户可自由用 VLAN/Trunk | 端口独占成本高，且 **STP BPDU 也会被透传** → 两地 STP 域合并 |

</div>

### PW Transport Modes for L2 Media Access · L2 介质接入的 PW 传输模式

| L2 technology | Transport mode over PW |
|---------------|------------------------|
| **Frame Relay** | Port-based / DLCI-based |
| **ATM** | AAL5 PDU over PW / cell relay over PW |
| **Ethernet** | Protocol-based / VLAN-based |

<div class="zh" markdown="1">

| L2 技术 | PW 上的传输模式 |
|---------|---------------|
| **Frame Relay** | 基于端口 / 基于 DLCI |
| **ATM** | AAL5 PDU over PW / 信元中继 over PW |
| **Ethernet** | 基于协议 / 基于 VLAN |

</div>

> This row is a piece of "legacy baggage" knowledge: early enterprises built networks on FR/ATM, and when they migrated to MPLS they used PWs to carry the old protocols unchanged, **avoiding any change to IP addressing and routing** — the exact counterexample to the "assumption" trap in Chapter 1: never assume "a new technology forces renumbering".

<div class="zh" markdown="1">

> 这一段是"历史包袱"知识点：早期企业用 FR/ATM 组网，迁移到 MPLS 时用 PW 把老协议原样搬运，**避免改 IP 地址和路由**——正是第 1 章"假设"陷阱的反面教材：不要假设"换新技术必须重编地址"。

</div>

### VPWS Design Checklist · VPWS 设计要点清单

| Consideration | Question | Design action |
|---------------|----------|---------------|
| **MTU** | The MPLS label stack shrinks the usable MTU | Verify CE/PE MTU at both ends, or large packets are dropped |
| **Failure detection** | The PW is down, but the CE may not know | Rely on OAM (CFM/LFM), BFD, or routing protocol failure detection |
| **Redundancy** | A single PW is a single point | Dual PE plus dual PW, or rely on carrier protection switching |
| **Multicast** | VPWS is transparent to multicast | If the customer runs PIM, multicast floods across the PW — confirm the bandwidth |
| **STP** | Port-based mode passes BPDUs through | Either accept the merged STP domain, or filter BPDUs on the CE |

<div class="zh" markdown="1">

| 考量 | 问题 | 设计动作 |
|------|------|---------|
| **MTU** | MPLS 标签栈让有效 MTU 变小 | 两端 CE/PE MTU 必须核对，否则大包被丢 |
| **故障检测** | PW 断了，CE 可能不知道 | 依靠 OAM（CFM/LFM）、BFD 或路由协议失效感知 |
| **冗余** | 单 PW 是单点 | 双 PE + 双 PW，或依赖运营商保护倒换 |
| **组播** | VPWS 对组播是透传的 | 若客户用 PIM，组播会跨 PW 泛洪，需确认带宽 |
| **STP** | 端口型会透传 BPDU | 要么接受两站点 STP 域合并，要么在 CE 侧过滤 BPDU |

</div>

> ⚠️ **"Two sites' STP domains merged" is the classic Layer 2 interconnect failure source**: once merged, a topology change at one site destabilizes the other, and because **root bridge election spans sites**, the traffic path becomes unpredictable. The design must explicitly decide: **should STP cross the WAN or not**.

<div class="zh" markdown="1">

> ⚠️ **"两个站点 STP 域合并"是二层互联最经典的故障源**：合并后一个站点的拓扑变化会震荡另一个站点，且**根桥选举跨站点**，流量路径不可预期。设计时必须显式决定：**是否让 STP 跨越 WAN**。

</div>

---

## Virtual Private LAN Service (VPLS) Design Considerations · 虚拟专用 LAN 服务设计考量

VPLS meets the need to interconnect multiple sites over one common Layer 2 network, and supports Layer 2 extension and virtual machine mobility in modern data centers.

<div class="zh" markdown="1">

VPLS 满足通过一个通用二层网络互联多个站点的需求，支持现代数据中心的二层扩展和虚拟机移动性。

</div>

**In one sentence**: VPLS = **the carrier builds "one big switch spanning geographies" for you**, so every site looks like it plugs into the same switch.

<div class="zh" markdown="1">

**一句话理解**：VPLS = **运营商帮你建了一个"跨地域的大交换机"**，所有站点像接在同一台交换机上。

</div>

### VPLS Architectural Components · VPLS 架构组件

| Component | Function |
|-----------|----------|
| **N-PE (network-facing PE)** | Provides VPLS termination and L3 services |
| **U-PE (user-facing PE)** | Provides the customer UNI |
| **CE (customer edge)** | Customer equipment |
| **VSI (virtual switching instance)** | Performs standard LAN bridging, including learning and forwarding based on MAC addresses and VLAN tags |
| **MTU (multi-tenant unit)** | An aggregation device in the hierarchical model that acts in the U-PE role |

<div class="zh" markdown="1">

| 组件 | 功能 |
|------|------|
| **N-PE (网络面向 PE)** | 提供 VPLS 终止/L3 服务 |
| **U-PE (用户面向 PE)** | 提供客户 UNI |
| **CE (客户边缘)** | 客户设备 |
| **VSI (虚拟交换实例)** | 执行标准 LAN 桥接功能，包括基于 MAC 地址和 VLAN 标签的学习和转发 |
| **MTU (多租户单元)** | 分层模型中的汇聚设备，充当 U-PE 角色 |

</div>

### VPLS Control Plane · VPLS 控制平面

The main difference between VPLS and VPWS: VPLS needs a **full mesh of PWs** among all participating PEs. Automatic PE discovery and automatic PW establishment therefore become important factors.

<div class="zh" markdown="1">

VPLS 与 VPWS 的主要区别：VPLS 需要所有参与的 PE 之间建立**全互联 PW**。因此 PE 自动发现和 PW 自动建立是重要因素。

</div>

**Why must it be full mesh?** Because VPLS is essentially one "virtual switch":

<div class="zh" markdown="1">

**为什么必须全互联？** 因为 VPLS 本质是一台"虚拟交换机"：

</div>

```
If PE1–PE2 and PE2–PE3 have PWs but PE1–PE3 does not:
  a frame from CE1 to CE3 arrives at PE1 over the PE2 PW → forwarding it on to PE3 would loop
So either full mesh (every PE reaches every other directly), or explicit loop protection
```

<div class="zh" markdown="1">

```
如果 PE1–PE2、PE2–PE3 有 PW，但 PE1–PE3 没有：
  CE1 发往 CE3 的帧 → PE1 从 PE2 的 PW 收到 → 若再转发给 PE3 就形成环路
因此要么全互联（每个 PE 都能直达），要么必须加环路防护
```

</div>

> ⚠️ **The VPLS "split horizon" rule**: a PE does **not** forward a frame received from one PW out another PW. That is the **only** barrier against loops in a full mesh. Understand this and you understand why **H-VPLS needs an extra layer of hierarchy** — once an intermediate tier appears, split horizon alone is no longer enough.

<div class="zh" markdown="1">

> ⚠️ **VPLS 的"水平分割"（Split Horizon）规则**：PE **不会**把从一个 PW 收到的帧转发到另一个 PW。这是防止全互联环路的**唯一屏障**。理解这点，就能理解为什么 **H-VPLS 需要额外的层次设计**——一旦引入中间层，单靠水平分割就不够了。

</div>

### VPLS Design Models · VPLS 设计模型

#### 1. Basic Model · 基本模型

```
    CE1          CE2          CE3
     │            │            │
    U-PE1        U-PE2        U-PE3
     │            │            │
    ┌──────── N-PE full mesh ────────┐
    │  N-PE1 ═══ N-PE2 ═══ N-PE3 │
    │     ╲    ╱   ╲    ╱       │
    │      ╲  ╱     ╲  ╱         │
    │       ╲╱       ╲╱          │
    └────────────────────────────┘
```

<div class="zh" markdown="1">

```
    CE1          CE2          CE3
     │            │            │
    U-PE1        U-PE2        U-PE3
     │            │            │
    ┌──────── N-PE 全互联 ────────┐
    │  N-PE1 ═══ N-PE2 ═══ N-PE3 │
    │     ╲    ╱   ╲    ╱       │
    │      ╲  ╱     ╲  ╱         │
    │       ╲╱       ╲╱          │
    └────────────────────────────┘
```

</div>

- PWs must be fully meshed between PEs
- Each PE maintains one VSI
- MAC address learning and flooding

<div class="zh" markdown="1">

- PE 间需要全互联 PW
- 每个 PE 维护一个 VSI
- MAC 地址学习和泛洪

</div>

**Counting PWs**: n PEs in full mesh → **n(n-1)/2** PWs. Ten PEs means 45; fifty PEs means 1225. That is the structural scalability problem of VPLS.

<div class="zh" markdown="1">

**PW 数量计算**：n 个 PE 全互联 → **n(n-1)/2** 条 PW。10 个 PE = 45 条，50 个 PE = 1225 条。这就是 VPLS 扩展性的硬伤。

</div>

#### 2. Hierarchical VPLS (H-VPLS) · 分层 VPLS

```
    CE1     CE2          CE3     CE4
     │       │             │       │
    MTU1    MTU2          MTU3    MTU4
     │       │             │       │
     └───┬───┘             └───┬───┘
         │                      │
        N-PE1 ═══════════════ N-PE2
```

<div class="zh" markdown="1">

```
    CE1     CE2          CE3     CE4
     │       │             │       │
    MTU1    MTU2          MTU3    MTU4
     │       │             │       │
     └───┬───┘             └───┬───┘
         │                      │
        N-PE1 ═══════════════ N-PE2
```

</div>

- Multi-tenant units (MTUs) act as U-PEs
- Far fewer PWs are needed (no full mesh)
- Each MTU only needs to reach an N-PE, and the N-PEs are fully meshed among themselves

<div class="zh" markdown="1">

- 多租户单元 (MTU) 作为 U-PE
- 减少 PW 数量（无需全互联）
- MTU 只需连接到 N-PE，N-PE 之间全互联

</div>

**Scale effect**: with m MTUs and n N-PEs, the PW count drops from (m+n)² to n² + m. As sites are added, growth falls from **quadratic to linear**.

<div class="zh" markdown="1">

**扩展效果**：m 个 MTU + n 个 N-PE，PW 数从 (m+n)² 降到 n² + m。站点增加时，增长从**平方级降为线性级**。

</div>

> ⚠️ **What H-VPLS costs you**:
> 1. **The MTU becomes a single point** — if an MTU dies, every site beneath it is cut off (unless dual-homed)
> 2. **A larger failure domain** — STP or a loop at one MTU can affect the whole VPLS domain
> 3. **One more layer to configure** — higher operational complexity (Day 2 cost)
>
> This is exactly the "manageability" principle from Chapter 5 in concrete form.

<div class="zh" markdown="1">

> ⚠️ **H-VPLS 的代价**：
> 1. **MTU 成为单点**——MTU 挂了，其下所有站点失联（除非双归属）
> 2. **故障域扩大**——一个 MTU 的 STP/环路可能影响整个 VPLS 域
> 3. **多一层配置**——运维复杂度上升（Day 2 成本）
>
> 这正是第 5 章"可管理性"原则的具体体现。

</div>

### VPLS Scalability Limits · VPLS 可扩展性限制

| Limit | Description | Mitigation |
|-------|-------------|-----------|
| **MAC learning** | PEs must learn every customer MAC address; memory is constrained at scale | Cap MACs per VPLS, tune aging, **PBB (MAC-in-MAC)** |
| **Full-mesh PWs** | With many PEs the PW count grows as O(n²) | **H-VPLS hierarchy**, EVPN |
| **Flooding** | Unknown unicast, multicast and broadcast flooding consumes bandwidth | ARP proxy, multicast optimization, **EVPN** |
| **No control plane** | MACs are learned only in the data plane, so convergence is slow | **EVPN's BGP MAC advertisement** |

<div class="zh" markdown="1">

| 限制 | 说明 | 缓解手段 |
|------|------|---------|
| **MAC 学习** | PE 需要学习所有客户的 MAC 地址，大规模部署时内存受限 | 限制每 VPLS 的 MAC 数、老化优化、**PBB（MAC-in-MAC）** |
| **PW 全互联** | 大量 PE 时 PW 数量呈 O(n²) 增长 | **H-VPLS 分层**、EVPN |
| **泛洪** | 未知单播、组播和广播泛洪消耗带宽 | ARP 代理、组播优化、**EVPN** |
| **无控制平面** | MAC 只能靠数据面学习，收敛慢 | **EVPN 的 BGP MAC 通告** |

</div>

> 💡 **The key CCDE judgement**: VPLS's problem is **not performance, it is the absence of a control plane**. MAC learning relies on flooding, multihoming on MC-LAG, and recovery on re-flooding — all patches in the data plane. EVPN exists to move that machinery into the control plane.

<div class="zh" markdown="1">

> 💡 **CCDE 的关键判断**：VPLS 的问题**不是性能，而是"缺乏控制平面"**。MAC 学习靠泛洪、多归属靠 MC-LAG、故障恢复靠重新泛洪——都是"数据面打补丁"。EVPN 出现就是为了把这套东西搬到控制平面。

</div>

---

## EVPN Design Models · EVPN 设计模型

EVPN (Ethernet VPN) is the next-generation L2VPN technology. It uses BGP (MP-BGP) as its control plane and removes the scalability limits of VPLS.

<div class="zh" markdown="1">

EVPN（Ethernet VPN）是下一代 L2VPN 技术，基于 BGP（MP-BGP）作为控制平面，解决了 VPLS 的可扩展性限制。

</div>

### Core Idea: Turn MACs into Routes · 核心思想：把 MAC 变成路由

```
The VPLS world: a MAC address = something learned in the data plane (by flooding, by aging)
The EVPN world: a MAC address = a BGP route (with a next hop, attributes, policy control)
```

<div class="zh" markdown="1">

```
VPLS 世界：MAC 地址 = 数据面学到的东西（靠泛洪、靠老化）
EVPN 世界：MAC 地址 = 一条 BGP 路由（有下一跳、有属性、可策略控制）
```

</div>

Once you adopt that view, every EVPN advantage follows naturally:

<div class="zh" markdown="1">

这个视角一旦建立，EVPN 的所有优势都是自然推论：

</div>

| Consequence | Result |
|-------------|--------|
| A MAC is a route | **MAC movement equals a route update** — fast convergence after a VM migration, with no "duplicate MAC" |
| Routes have next hops | **Flooding-based learning disappears** — convergence changes from "re-flood" to "BGP update" |
| Routes have attributes | **Traffic engineering and aliasing (multipath load sharing)** become possible |
| BGP has multihoming mechanisms | **All-Active multihoming is native**, with no MC-LAG needed |
| The control plane knows the MACs | **ARP proxying** becomes possible, and BUM traffic drops sharply |

<div class="zh" markdown="1">

| 推论 | 结果 |
|------|------|
| MAC 是路由 | **MAC 迁移 = 路由更新**，VM 迁移后收敛快，不会出现"双份 MAC" |
| 路由有下一跳 | **不再需要泛洪学习**，收敛从"重新泛洪"变为"BGP 更新" |
| 路由有属性 | 可做**流量工程、aliasing（多路径负载分担）** |
| BGP 有多归属机制 | **All-Active 多归属原生支持**，无需 MC-LAG |
| 控制平面已知 MAC | **ARP 代理**成为可能，BUM 大幅减少 |

</div>

### EVPN versus VPLS · EVPN vs VPLS 对比

| Dimension | VPLS | EVPN |
|-----------|------|------|
| **Control plane** | LDP/RSVP (builds PWs only, carries no MACs) | MP-BGP (carries MAC/IP) |
| **MAC learning** | Flooding in the data plane | BGP advertisement in the control plane |
| **Flooding** | High (unknown unicast, ARP) | Low (ARP proxy) |
| **Multihoming** | Limited (MC-LAG with cross-device coordination) | Native All-Active (ESI plus DF election) |
| **Scalability** | Medium (O(n²) PWs and MAC table pressure) | High (BGP routes, no full mesh required) |
| **MAC mobility** | Limited | Optimized (MAC Mobility extended community plus sequence number) |
| **Failure convergence** | Slow (re-flood and re-learn) | Fast (BGP withdraw plus A-D routes) |

<div class="zh" markdown="1">

| 对比项 | VPLS | EVPN |
|--------|------|------|
| **控制平面** | LDP/RSVP（仅建立 PW，不承载 MAC） | MP-BGP（承载 MAC/IP） |
| **MAC 学习** | 数据平面泛洪学习 | 控制平面 BGP 通告 |
| **泛洪** | 高（未知单播、ARP） | 低（ARP 代理） |
| **多归属** | 有限（需 MC-LAG，跨设备协同） | 原生支持 All-Active（ESI + DF 选举） |
| **可扩展性** | 中（O(n²) PW + MAC 表压力） | 高（BGP 路由，无全互联要求） |
| **MAC 移动性** | 有限 | 优化（MAC Mobility 扩展团体 + 序列号） |
| **故障收敛** | 慢（重新泛洪/重新学习） | 快（BGP 撤消 + A-D 路由） |

</div>

### EVPN Core Concepts · EVPN 核心概念

| Concept | Description |
|---------|-------------|
| **MAC route advertisement** | MAC addresses are advertised as BGP routes in the control plane, so no data-plane flooding is needed to learn them |
| **ARP proxy** | The PE answers ARP requests on behalf of the hosts, cutting flooding |
| **All-Active multihoming** | One CE may connect to several PEs, with all links active at the same time |
| **MAC mobility** | When a VM moves, EVPN updates the MAC location quickly in the control plane |
| **ESI (Ethernet Segment Identifier)** | Identifies "the set of links connecting one CE to several PEs", the basis for detecting multihoming |
| **DF (designated forwarder)** | Decides which PE forwards BUM traffic towards the CE in a multihomed setup, avoiding duplicate flooding |

<div class="zh" markdown="1">

| 概念 | 说明 |
|------|------|
| **MAC 路由通告** | MAC 地址作为 BGP 路由在控制平面通告，无需数据平面泛洪学习 |
| **ARP 代理** | PE 代理响应 ARP 请求，减少泛洪 |
| **All-Active 多归属** | 同一 CE 可连接多台 PE，所有链路同时活跃 |
| **MAC 移动性** | 虚拟机迁移时，EVPN 在控制平面快速更新 MAC 位置 |
| **ESI (以太网段标识)** | 标识"同一 CE 接到多台 PE 的这组链路"，是判断多归属的基础 |
| **DF (指定转发者)** | 多归属场景中由谁向 CE 转发 BUM 流量，避免重复泛洪 |

</div>

### EVPN Route Types (Extended Focus) · EVPN 路由类型（扩展重点）

| Type | Name | Purpose |
|------|------|---------|
| **Type 1** | Ethernet Auto-Discovery (A-D) | Announces "which ESI I own"; used for **fast convergence, aliasing load sharing and mass withdrawal** |
| **Type 2** | MAC/IP Advertisement | **The core type**: advertises a MAC (optionally with its IP) and next hop; enables ARP proxying and MAC mobility |
| **Type 3** | Inclusive Multicast Ethernet Tag (IMET) | Builds the distribution tree for **BUM traffic** (who wants to receive flooded traffic) |
| **Type 4** | Ethernet Segment | **DF election**, deciding who forwards BUM traffic towards a multihomed CE |
| **Type 5** | IP Prefix | Advertises IP prefixes, so EVPN can carry L3VPN functions (one unified L2/L3 control plane) |

<div class="zh" markdown="1">

| 类型 | 名称 | 作用 |
|------|------|------|
| **Type 1** | Ethernet Auto-Discovery (A-D) | 宣告"我拥有哪个 ESI"；用于**快速收敛、aliasing 负载分担、批量撤消** |
| **Type 2** | MAC/IP Advertisement | **最核心**：通告 MAC（可含 IP）与下一跳；支持 ARP 代理与 MAC 移动性 |
| **Type 3** | Inclusive Multicast Ethernet Tag (IMET) | 建立 **BUM 流量**的分发树（谁需要收泛洪流量） |
| **Type 4** | Ethernet Segment | **DF 选举**，决定谁负责向多归属 CE 转发 BUM |
| **Type 5** | IP Prefix | 通告 IP 前缀，使 EVPN 可承载 L3VPN 功能（统一 L2/L3 控制平面） |

</div>

> 💡 **Memory hook**: **1 discovery, 2 MAC, 3 flooding, 4 election, 5 prefix**.
>
> Type 5 matters a lot — it means **EVPN can do Layer 2 and Layer 3 at the same time**, the foundation of "one control plane for everything" in modern data centers and campuses (see the overlay design in Chapter 9 on network virtualization).

<div class="zh" markdown="1">

> 💡 **记忆法**：**1 发现、2 MAC、3 泛洪、4 选举、5 前缀**。
>
> Type 5 很重要——它意味着 **EVPN 可以同时做二层和三层**，这是现代数据中心与园区"一张控制平面搞定一切"的基础（对应第 9 章网络虚拟化的 Overlay 设计）。

</div>

### PBB-EVPN

PBB-EVPN combines PBB (Provider Backbone Bridging) with EVPN:

<div class="zh" markdown="1">

PBB-EVPN 结合了 PBB (Provider Backbone Bridging) 和 EVPN：

</div>

- Hides customer MAC addresses, so only carrier MACs are carried in the core
- Improves scalability further
- Suits scenarios with an enormous number of MAC addresses

<div class="zh" markdown="1">

- 隐藏客户 MAC 地址，只在核心传输运营商 MAC
- 进一步提高可扩展性
- 适合 MAC 地址数量极大的场景

</div>

**In one sentence**: **MAC-in-MAC encapsulation** — customer MACs are wrapped inside carrier MACs, and core PEs look only at the outer (carrier) MAC.

<div class="zh" markdown="1">

**原理一句话**：**MAC-in-MAC 封装**——客户 MAC 被包在运营商 MAC 里面，核心 PE 只看外层（运营商）MAC。

</div>

| Dimension | Plain EVPN | PBB-EVPN |
|-----------|-----------|----------|
| MACs the core PEs must learn | Every customer MAC | **Only carrier B-MACs** |
| Effect of customer MAC count | Directly hits core table sizes | Isolated at the edge BEB |
| Propagation of customer MAC changes | Advertised network-wide | Never crosses the core |
| Suited to | Medium scale, fine-grained policy | **Very large scale, MAC explosion** |

<div class="zh" markdown="1">

| 维度 | 普通 EVPN | PBB-EVPN |
|------|----------|----------|
| 核心 PE 需学习的 MAC | 所有客户 MAC | **只有运营商 B-MAC** |
| 客户 MAC 数量影响 | 直接影响核心表项 | 被隔离在边缘 BEB |
| 客户 MAC 变化传播 | 全网通告 | 不跨核心传播 |
| 适合 | 中等规模、需要精细策略 | **超大规模、MAC 数量爆炸** |

</div>

> ⚠️ **The cost**: another encapsulation layer (MTU shrinks again), more operational complexity and harder troubleshooting. **Worth it only when the MAC scale really is the bottleneck** — otherwise it is the "over-design" from Chapter 1.

<div class="zh" markdown="1">

> ⚠️ **代价**：封装层级增加（MTU 再减小）、运维更复杂、排障更困难。**只有 MAC 规模真的到瓶颈时才值得用**——否则就是第 1 章的"过度设计"。

</div>

### DCI (Data Center Interconnect) Selection · DCI（数据中心互联）选型

| Scenario | Best choice | Reason |
|----------|-------------|--------|
| Few data centers, few interconnect points | VPLS | Simple and mature |
| Many data centers, many interconnect points | EVPN / PBB-EVPN | High scalability |
| Strong MAC mobility requirement | EVPN | MAC advertisement in the control plane |
| An enormous number of MAC addresses | PBB-EVPN | MAC hiding |

<div class="zh" markdown="1">

| 场景 | 最佳选择 | 原因 |
|------|---------|------|
| 少量数据中心，少量互联点 | VPLS | 简单成熟 |
| 大量数据中心，大量互联点 | EVPN / PBB-EVPN | 高可扩展性 |
| MAC 移动性要求高 | EVPN | 控制平面 MAC 通告 |
| MAC 地址数量极大 | PBB-EVPN | MAC 隐藏 |

</div>

---

## Extended: Side-by-Side Comparison of Transport Services · 扩展：传输服务的横向对比

The book focuses on carrier L2 services, but real design questions often require choosing among **a broader set of transport options**. This table is the practical supplement to this chapter:

<div class="zh" markdown="1">

书里聚焦运营商 L2 服务，但真实设计题往往要求在**更广的传输选项**中做选择。这张表是本章的实用补充：

</div>

| Transport | Layer offered | Control | Typical latency | Cost | Where it fits |
|-----------|---------------|---------|-----------------|------|---------------|
| **Dark fiber** | L1 | Highest (you light it yourself) | Lowest (speed of light) | High (distance-based) | Metro data centers, ultra-low-latency trading |
| **DWDM wavelength** | L1 (wavelength) | High | Very low | Very high | High-bandwidth long haul, data center interconnect |
| **MPLS L2VPN (VPWS/VPLS)** | L2 | Low (the carrier's network) | Medium (path dependent) | Medium-high | Layer 2 transparency, multi-site in one subnet |
| **MPLS L3VPN** | L3 | Low | Medium | Medium | The workhorse of enterprise WANs, with the carrier participating in routing |
| **Internet + SD-WAN** | L3 (overlay) | High (you encrypt and steer) | Varies widely | Low | Many branches, cost sensitive, jitter tolerant |
| **5G / LTE wireless** | L2/L3 | Low | Relatively high | Usage-based | Backup links, temporary sites, IoT |

<div class="zh" markdown="1">

| 传输方式 | 提供的层次 | 控制权 | 典型时延 | 成本 | 适用场景 |
|---------|-----------|--------|---------|------|---------|
| **裸光纤 / 暗光纤** | L1 | 最高（自己点灯） | 最低（光速） | 高（按距离） | 同城数据中心、超低时延交易 |
| **DWDM 波长** | L1（波长） | 高 | 很低 | 很高 | 大带宽长距、数据中心互联 |
| **MPLS L2VPN (VPWS/VPLS)** | L2 | 低（运营商的网） | 中（取决于路径） | 中高 | 需要二层透明、多站点同子网 |
| **MPLS L3VPN** | L3 | 低 | 中 | 中 | 传统企业 WAN 主力，路由由运营商参与 |
| **Internet + SD-WAN** | L3（Overlay） | 高（自己加密与选路） | 变化大 | 低 | 分支大量、成本敏感、可容忍抖动 |
| **5G / LTE 无线** | L2/L3 | 低 | 较高 | 按流量 | 备份链路、临时站点、IoT |

</div>

> 💡 **How CCDE thinks about selection**: it is not a contest of "who is better", but a scorecard ordered by **business requirements**:
> - Need **Layer 2 transparency** (one subnet, non-IP protocols, legacy systems) → only L2VPN or dark fiber
> - Need **deterministic latency** (financial trading, industrial control) → dark fiber or DWDM
> - Need **cost and elasticity** (hundreds of branches) → Internet plus SD-WAN
> - Need **simple any-to-any between sites** → MPLS L3VPN

<div class="zh" markdown="1">

> 💡 **CCDE 的选型逻辑**：不是比"谁更好"，而是按**业务需求排序**打分——
> - 要**二层透明**（同子网、非 IP 协议、遗留系统）→ 只能 L2VPN 或暗光纤
> - 要**确定性时延**（金融交易、工业控制）→ 暗光纤/DWDM
> - 要**成本与弹性**（几百个分支）→ Internet + SD-WAN
> - 要**多站点任意互访且简单** → MPLS L3VPN

</div>

---

## Extended: Five Classic Design Flaws of Layer 2 Transport · 扩展：二层传输的五大设计缺陷

| Flaw | Symptom | Consequence | How to avoid it |
|------|---------|-------------|-----------------|
| **STP domains merged across the WAN** | Two sites joined by port-based VPWS without BPDU filtering | A topology change on one side destabilizes the whole network; the root bridge sits at the far end and traffic takes a detour | Prefer Layer 3 between sites, or filter BPDUs explicitly to keep separate STP domains |
| **MTU mismatch** | The MPLS label stack eats bytes and nobody adjusts the MTU | Large packets are dropped — "ping works but files will not transfer" | Verify MTU end to end, and fragment or clamp MSS when needed |
| **Runaway broadcast and unknown-unicast flooding** | Lots of unknown unicast and ARP inside VPLS | Flooding saturates the bandwidth and hurts every site | ARP proxy, control-plane learning (EVPN), broadcast suppression |
| **Black-hole failures** | The PW still shows up during a unidirectional failure | Traffic silently disappears and routing protocols may never notice | Deploy OAM/BFD and run end-to-end connectivity checks |
| **Wasted single-active multihoming** | Multihoming via MC-LAG with only one link forwarding | Half the bandwidth wasted and a hit on failover | EVPN All-Active (ESI) with every link forwarding |

<div class="zh" markdown="1">

| 缺陷 | 表现 | 后果 | 规避 |
|------|------|------|------|
| **STP 域跨 WAN 合并** | 两站点用端口型 VPWS 互联但未过滤 BPDU | 一侧拓扑变化震荡全网；根桥在远端导致流量绕行 | 站点间优先三层互联；或显式过滤 BPDU 形成独立 STP 域 |
| **MTU 不匹配** | MPLS 标签栈吃掉字节，未调 MTU | 大包被丢，"ping 通但文件传不了" | 端到端核对 MTU，必要时分片/调 MSS |
| **广播/未知单播泛洪失控** | VPLS 中大量未知单播与 ARP | 带宽被泛洪打满，影响所有站点 | ARP 代理、控制平面学习（EVPN）、广播抑制 |
| **黑洞故障** | 单向故障时 PW 仍显示 up | 数据静默丢失，路由协议可能不感知 | 部署 OAM/BFD，做端到端连通性检测 |
| **多归属单活浪费** | 用 MC-LAG 做多归属但只有一条链路转发 | 带宽浪费一半，切换有中断 | EVPN All-Active（ESI），所有链路同时转发 |

</div>

> ⚠️ **"Black-hole failures"** are the most easily missed category: the physical and logical layers look fine, but traffic quietly vanishes. The key question is **whether a detection mechanism exists that is independent of the data path**.

<div class="zh" markdown="1">

> ⚠️ 其中 **"黑洞故障"** 是最容易被忽略的一类故障：物理层/逻辑层显示正常，但流量静默消失。判断关键——**是否存在独立于数据面的检测机制**。

</div>

---

## Extended: Why EVPN Converges Faster · 扩展：EVPN 收敛为什么更快

This is the key to appreciating EVPN's value, and it comes up often:

<div class="zh" markdown="1">

这是理解 EVPN 价值的关键，也常被追问：

</div>

```
VPLS failure recovery:
  link down → PW down → MAC table must age → unknown-unicast flooding → relearn
  time = detection + aging timer (tens of seconds) + flooding convergence

EVPN failure recovery:
  link down → BGP withdraws the Type 1/2 routes → upstream removes that next hop immediately
  time = BFD detection (milliseconds to seconds) + BGP update propagation
  multihomed case: Type 1 A-D routes allow "mass withdrawal" — one update removes every MAC of an ESI
```

<div class="zh" markdown="1">

```
VPLS 故障恢复：
  链路断 → PW 断 → MAC 表需老化 → 未知单播泛洪 → 重新学习
  耗时 = 检测 + 老化定时器（数十秒）+ 泛洪收敛

EVPN 故障恢复：
  链路断 → BGP 撤消 Type 1/2 路由 → 上游立即删除该下一跳
  耗时 = BFD 检测（毫秒~秒级）+ BGP 更新传播
  多归属场景：Type 1 的 A-D 路由支持"批量撤消"，一条更新撤掉整个 ESI 的 MAC
```

</div>

> 💡 **Design implication**: EVPN turns "data-plane uncertainty" into "control-plane determinism". This is also why EVPN keeps reappearing in Chapter 9 (virtualization) and Chapter 12 (automation) — **programmable and predictable** is the foundation of modern networks.

<div class="zh" markdown="1">

> 💡 **设计含义**：EVPN 把"数据面的不确定性"转成"控制面的确定性"。这也是第 9 章（虚拟化）与第 12 章（自动化）里 EVPN 反复出现的原因——**可编程、可预测**是现代网络的基础。

</div>

---

## Real-World Cases · 实战案例

### Case 1: A Hospital Group — PACS Imaging Across Campuses · 案例一：三甲医院集团——PACS 影像跨院区

**Background**: one main campus plus two new branches. The PACS imaging system sits in the main campus, while the branches only have CT/MR scanners and viewing workstations. A single CT series is 300–800 MB, and radiology insists on "click and it opens" — anything beyond three seconds draws complaints.

<div class="zh" markdown="1">

**背景**：主院区 + 两个新建分院，PACS 影像系统集中在主院区，分院只有 CT/MR 设备和阅片终端。单次 CT 序列 300–800MB，放射科要求"点开即看"，延迟超 3 秒就开始抱怨。

</div>

**Constraints**:
- PACS uses the proprietary DICOM protocol and devices discover servers by **broadcast** → **they must share one Layer 2 broadcast domain**
- Each branch has exactly one IT person, with no capacity for complex routing policy
- The budget does not allow building private fiber

<div class="zh" markdown="1">

**约束**：
- PACS 用 DICOM 私有协议，设备上线靠**广播**发现服务器 → **必须同一个二层广播域**
- 分院 IT 只有 1 人，没有能力做复杂路由策略
- 预算不允许自建光纤

</div>

**Solution**: branch → main campus over an **E-Line (EVPL, VLAN-based)**, with bandwidth sized from average daily imaging volume, 200M for the first phase.

<div class="zh" markdown="1">

**方案**：分院 → 主院区 用 **E-Line（EVPL，基于 VLAN）**，带宽按日均影像量算，首期 200M。

</div>

**Problems after three months in service**:

<div class="zh" markdown="1">

**上线三个月后的问题**：

</div>

| Symptom | Real cause | Correction |
|---------|-----------|------------|
| "Images occasionally will not open" while ping is always fine | The MPLS label stack plus Layer 2 encapsulation cut the usable MTU from 1500 to 1492, large DICOM packets were dropped, and TCP retransmission showed up as "occasional stalls" | Adjust MTU/MSS at both ends |
| PACS server CPU in the main campus rose noticeably | The three campuses' **broadcast domains merged**, so broadcast and multicast discovery packets flooded everywhere | Broadcast suppression on the PE plus per-site VLANs |

<div class="zh" markdown="1">

| 现象 | 真正原因 | 修正 |
|------|---------|------|
| "偶尔打不开影像"，但 ping 一直正常 | MPLS 标签栈 + 二层封装让有效 MTU 从 1500 降到 1492，DICOM 大包被丢，靠 TCP 重传表现为"偶尔卡" | 两端 MTU/ MSS 调整 |
| 主院区 PACS 服务器 CPU 明显上升 | 三个院区的**广播域合并**了，广播和多播发现报文全网泛洪 | PE 侧广播抑制 + 分站点 VLAN |

</div>

> 💡 **The one sentence worth remembering from this case**: **a Layer 2 service moves LAN problems onto the WAN unchanged.** The broadcast volume and MTU habits you tolerate locally become faults once they cross a wide area network.

<div class="zh" markdown="1">

> 💡 **这个案例最值得记住的一句话**：**二层服务会把"局域网的问题"原封不动地搬到 WAN 上。** 你在本地能容忍的广播量和 MTU 习惯，跨了广域网就变成故障。

</div>

### Case 2: An Auto Parts Manufacturer — Migrating Off Frame Relay · 案例二：汽车零部件工厂——Frame Relay 退网迁移

**Background**: 12 factories connect to headquarters in a star over FR, 256K–1M per link, carrying ERP and MES. The carrier announces that FR will be retired within two years.

<div class="zh" markdown="1">

**背景**：12 个工厂用 FR 星型连总部，每条 256K–1M，跑 ERP 和 MES。运营商通知两年内 FR 退网。

</div>

**Constraints**:
- The MES hosts are 2005-era Unix systems with **hard-coded IP addresses that cannot change**
- There is no IT staff at the factories, and any on-site configuration may be mis-entered
- The only production downtime window is the three days of the Spring Festival

<div class="zh" markdown="1">

**约束**：
- MES 主机是 2005 年的 Unix 系统，**IP 地址全网写死，改不了**
- 工厂端没有 IT 人员，任何现场配置都可能被改错
- 停产窗口只有春节 3 天

</div>

**Solution**: **VPWS port-based plus DLCI-based**, mapping each FR PVC one-to-one onto a PW. IP planning, routing and host configuration **stay untouched**; the factories only swap router interfaces.

<div class="zh" markdown="1">

**方案**：**VPWS 基于端口 + 基于 DLCI**，把每条 FR PVC 一对一映射成一条 PW。IP 规划、路由、主机配置**全不动**，工厂侧只更换路由器接口。

</div>

**Cost and follow-up**:
- Each factory dedicates one physical port (equivalent to EPL), so the monthly fee is about 30% above the old FR service
- Three years later, seven factories that could renumber were migrated to **EVPL with port reuse**, bringing overall cost down about 40%

<div class="zh" markdown="1">

**代价与后续**：
- 每个工厂独占一个物理端口（等效 EPL），月租比原 FR 高约 30%
- 三年后逐渐把能改地址的 7 个工厂改成 **EVPL 复用端口**，整体成本回落 40%

</div>

> 💡 **The first principle of migration projects**: **move first as an equivalent, optimize later.** A migration that wants to "get it right in one shot" usually gets it neither right nor live.

<div class="zh" markdown="1">

> 💡 **迁移项目的第一原则**：**先等价搬迁，再逐步优化。** 想"一次做对"的迁移，通常既做不对也上不了线。

</div>

### Case 3: A Retail Chain With 500 Stores — A Layer 2 Domain Too Large · 案例三：零售连锁 500 门店——二层域划太大

**Background**: stores only run POS terminals, guest WiFi and CCTV backhaul — **all of it IP traffic**. Headquarters wants unified policy and centralized egress.

<div class="zh" markdown="1">

**背景**：门店只有 POS 收银、顾客 WiFi、监控回传，**全部是 IP 业务**。总部希望统一策略、集中出口。

</div>

**Early design (failed)**: headquarters used VPLS to pull all 500 stores into one big Layer 2 domain, on the grounds that "it is simple to configure, like one large LAN".

<div class="zh" markdown="1">

**早期方案（失败）**：总部用 VPLS 把 500 家门店拉成一个大二层，理由是"配置简单，像一个大局域网"。

</div>

**Result**: construction work at one store connected a cable into a loop, **STP convergence propagated across the WAN, and the entire company's network was down for 40 minutes**; on ordinary days, broadcast and ARP from guest WiFi clients kept consuming headquarters link capacity.

<div class="zh" markdown="1">

**结果**：某门店施工把一根网线接成环路，**STP 收敛在广域网上传导，全公司网络瘫痪 40 分钟**；平日门店 WiFi 客户端的广播和 ARP 持续占用总部链路。

</div>

**Redesigned solution**:

<div class="zh" markdown="1">

**重构方案**：

</div>

| Traffic | Transport | Reason |
|---------|-----------|--------|
| POS / WiFi / CCTV (95% of it) | Internet plus SD-WAN (IPsec overlay) | Pure IP, no Layer 2 needed |
| Three legacy weighing devices (proprietary Layer 2 protocol) | EVPL point-to-point | Layer 2 is **genuinely** required, and the scope is tiny |

<div class="zh" markdown="1">

| 业务 | 传输方式 | 理由 |
|------|---------|------|
| POS / WiFi / 监控（占 95%） | Internet + SD-WAN（IPsec Overlay） | 纯 IP，不需要二层 |
| 3 套老旧称重设备（私有二层协议） | EVPL 点对点 | **真的需要**二层，范围极小 |

</div>

**Outcome**: egress bandwidth cost fell about 60%, and the blast radius of a loop went from "the whole company" to "one store".

<div class="zh" markdown="1">

**效果**：出口带宽成本降约 60%；环路故障影响面从"全公司"缩到"单店"。

</div>

> ⚠️ **In one sentence**: **the size of the Layer 2 domain is the size of the failure domain.** Ask first "how big must this Layer 2 segment actually be", not "would flattening it be more convenient".

<div class="zh" markdown="1">

> ⚠️ **一句话**：**二层域的范围 = 故障域的范围。** 设计时先问"这块二层到底必须多大"，而不是"拉平是不是更方便"。

</div>

### Case 4: EVPN Deployed, Yet "It Works but Not Well" · 案例四：EVPN 上线了，但"能用不好用"

**Background**: an Internet company with three data centers in two cities used EVPN plus VXLAN for DCI, deployed exactly per the vendor's best practice.

<div class="zh" markdown="1">

**背景**：某互联网公司两地三中心，用 EVPN + VXLAN 做 DCI，按厂商最佳实践部署完成。

</div>

**Two long-standing annoyances**:

<div class="zh" markdown="1">

**两个长期困扰**：

</div>

| Symptom | Root cause | Correction |
|---------|-----------|------------|
| Occasional 30-second packet loss after a VM migration | During the MAC move two PEs advertised the same MAC at once, with no tuning of the MAC Mobility sequence number and freeze time | Tune the MAC mobility parameters and freeze duration |
| The multihomed links carried traffic **only on one side**, the other sat idle | Multihoming was configured active-standby, with aliasing of A-D routes left disabled | Move to All-Active (ESI) and enable aliasing |

<div class="zh" markdown="1">

| 现象 | 根因 | 修正 |
|------|------|------|
| 虚拟机迁移后偶发 30 秒丢包 | MAC 迁移期间两台 PE 同时通告同一 MAC，缺少 MAC Mobility 序列号与冻结时间的调优 | 调优 MAC mobility 参数与冻结时长 |
| 多归属链路**上行只走一条**，另一条闲置 | 多归属用了 active-standby，且未启用 A-D 路由的 aliasing | 改 All-Active（ESI）+ 启用 aliasing |

</div>

> 💡 **The most counter-intuitive point**: **EVPN does not make anything better just because you deployed it.** It moves complexity from "data-plane flooding" into "control-plane parameters" — with the parameters untuned, behavior can be even harder to predict than VPLS. The benefit comes from "a programmable control plane", and only if you actually do the programming.

<div class="zh" markdown="1">

> 💡 **最反直觉的一点**：**EVPN 不会因为你上了它就自动变好。** 它把复杂度从"数据面泛洪"搬到了"控制面参数"——参数没调好，行为甚至比 VPLS 更难预测。收益来自"控制面可编程"，前提是你真的去编程。

</div>

---

## Lessons Learned · 实战经验总结

| Lesson | Explanation |
|--------|-------------|
| **Ask first "how big must the Layer 2 domain be"** | Keep only what Layer 2 genuinely requires, and send the rest over Layer 3. Layer 2 across sites is a last resort, not a default |
| **Always verify the MTU** | Every encapsulation (MPLS, VXLAN, IPsec, GRE) eats bytes. MTU problems show up as "it connects but will not transfer" |
| **Layer 2 services move LAN problems along** | Broadcast, ARP, STP, loops, MTU — none of them disappear, they just break out somewhere else |
| **Build visibility before talking about optimization** | Tunnels and carrier networks make localization harder, so OAM, BFD and flow analysis must be in place before go-live |
| **Migrate in two steps** | First move as an equivalent to protect the business, then optimize cost and architecture |
| **Do not over-design for "flexibility"** | Taking EVPN/PBB-EVPN into small environments usually costs more in complexity than it returns |
| **Count TCO, not CAPEX** | Carrier-side VLAN coordination, change tickets and fault demarcation are all long-term costs |

<div class="zh" markdown="1">

| 经验 | 说明 |
|------|------|
| **先问"二层域要多大"** | 二层只保留"真的必须"的部分，其余走三层。跨站点二层是最后手段，不是首选 |
| **MTU 永远要核对** | 任何封装（MPLS、VXLAN、IPsec、GRE）都会吃掉字节。MTU 问题表现为"能连但传不了" |
| **二层服务会搬运 LAN 的问题** | 广播、ARP、STP、环路、MTU——一个都不会少，只是换了地方发作 |
| **先建可见性，再谈优化** | 隧道与运营商网络让定位变难，OAM/BFD/流量分析要在上线前就位 |
| **迁移分两步走** | 先等价搬迁保证业务不断，再优化成本与架构 |
| **别为"灵活"过度设计** | 小规模场景上 EVPN/PBB-EVPN，复杂度成本通常大于收益 |
| **算 TCO，不算 CAPEX** | 运营商侧 VLAN 协调、变更工单、故障定界都是长期成本 |

</div>

---

## Design Scenario Exercises (2) · 设计情景演练（2 个）

### Scenario 1: Must an Active-Active Data Center "Extend Layer 2"? · 情景一：双活数据中心"必须二层延伸"吗

**Situation**: a retailer wants active-active data centers within one metro, 38 km apart. The application team states the requirement: "both computer rooms must be in the same Layer 2 domain, otherwise virtual machine migration breaks." Available from the carrier: EPL (1G/10G point-to-point), EVPL (port reuse, multiple VLANs) and an EVPN-based E-LAN service. The current single room has 1200 VLANs, about 60,000 MAC entries, and the largest broadcast domain holds 400 hosts.

<div class="zh" markdown="1">

**场景**：某零售企业要做同城双活，两地相距 38km。应用团队提出需求："两个机房必须在同一个二层域里，否则虚拟机迁移会断。"现有条件：运营商可提供 EPL（1G/10G，点对点）、EVPL（端口复用、多 VLAN）、以及基于 EVPN 的 E-LAN 服务。现网单机房有 1200 个 VLAN、MAC 表约 6 万条，广播域最大 400 台主机。

</div>

**Questions to answer**:
1. Does the premise "VM migration requires Layer 2" hold?
2. If Layer 2 extension really is needed, which service should we buy?
3. What new risks does the extension create, and how do we bound them?

<div class="zh" markdown="1">

**要回答的问题**：
1. "虚拟机迁移必须二层"这个前提成立吗？
2. 若确实需要二层延伸，选哪种服务？
3. 二层延伸后新增哪些风险，如何限制？

</div>

**Reference reasoning**:
- **Challenge the premise first.** Modern virtualization platforms can migrate across Layer 3 (changing IP) routinely; if the application tolerates "a brief outage plus an IP change at migration", no Layer 2 extension is needed. **"It must be one Layer 2 domain" is often historical habit rather than a hard constraint.**
- **If it really is required (for example to keep IP addresses or avoid renumbering a legacy system)**: for point-to-point needs choose **EVPL** (VLAN reuse, cheaper than EPL, several services on one port); consider **E-LAN/EVPN** only when multiple sites must share one broadcast domain. **Do not buy a multipoint network for two sites.**
- **Extending Layer 2 inevitably enlarges the failure domain**: extending all 1200 VLANs means any STP event, broadcast storm or loop on one side hits the other. So the design must **extend only the necessary VLANs** (typically just the migration segment and a few tightly coupled systems, with everything else over Layer 3) and cap broadcast domain size (400 hosts is already near the limit).
- **Consider the control plane and data plane separately**: EVPN learns MACs through a BGP control plane, which is more controllable and converges faster than VPLS flooding plus learning, and it suppresses flooding. Prefer EVPN if the carrier supports it.
- **Constraints that must be written into the design**: a one-way latency budget (active-active write paths usually need < 5 ms), the MAC table size limit and aging policy, loop protection (an STP boundary across sites, or disable STP outright), and split-brain handling when a failure occurs (which side wins).
- **In one sentence**: **Layer 2 extension buys migration convenience by enlarging the failure domain**, so buy it only when the payoff is clear.

<div class="zh" markdown="1">

**参考思路**：
- **先质疑前提。** 现代虚拟化平台跨三层迁移（改 IP）已普遍可行；如果应用能接受"迁移时短暂中断 + IP 变更"，就不需要二层延伸。**"必须同二层"往往是历史习惯，而不是硬约束。**
- **如果确实需要（例如保留 IP、避免重编号的老系统）**：点对点需求选 **EVPL**（按 VLAN 复用，成本低于 EPL，且能一端口跑多业务）；多站点共享同一广播域才考虑 **E-LAN/EVPN**。**不要为了"两个站点"去买一张多点的网。**
- **延伸二层必然放大故障域**：1200 个 VLAN 全部延伸意味着任何一侧的 STP/广播风暴/环路都会打到对面。所以设计必须**只延伸必要的 VLAN**（通常只保留迁移网段与少数紧耦合系统，其余走三层），并限制广播域规模（400 台已接近上限）。
- **控制面与数据面要分离考虑**：EVPN 用 BGP 控制面学 MAC，比 VPLS 的泛洪+学习更可控，收敛更快、抑制泛洪。若运营商支持，优先 EVPN。
- **必须写入设计的限制项**：单向时延预算（双活写入路径通常要求 < 5ms）、MAC 表规模上限与老化策略、环路防护（跨站 STP 边界或直接禁用）、故障时的"脑裂"处理（哪一侧优先）。
- **一句话**：**二层延伸是"用扩大故障域换取迁移便利"，只有在收益明确时才买。**

</div>

### Scenario 2: The Failure Happened — Whose Problem Is It? · 情景二：故障发生了，责任在谁

**Situation**: a manufacturer uses a carrier EVPL between the main plant and a branch plant, reusing one physical port for six VLANs (production, office, video, guest, management, backup). One day the production VLAN shows intermittent packet loss (two or three times an hour, 10–30 seconds each) while the office VLAN is fine. The carrier says "our circuit monitoring is normal and the port has no alarms"; the enterprise blames the carrier, and the standoff lasts two weeks.

<div class="zh" markdown="1">

**场景**：某制造企业用运营商 EVPL 连接总厂与分厂，同一物理端口复用 6 个 VLAN（生产、办公、视频、访客、管理、备份）。某日生产 VLAN 出现间歇性丢包（每小时 2–3 次，每次 10–30 秒），办公 VLAN 正常。运营商称"我们的电路监控正常，端口无告警"；企业认为是运营商问题，双方僵持两周。

</div>

**Questions to answer**:
1. From a design standpoint, why is this dispute so hard to settle?
2. What "determinability" should the design phase have left behind?
3. How should it be changed afterwards to avoid similar disputes?

<div class="zh" markdown="1">

**要回答的问题**：
1. 从设计角度，这次争议为什么难判定？
2. 设计阶段本应留下哪些"可判定性"？
3. 后续怎么改，避免同类争议？

</div>

**Reference reasoning**:
- **The root of the difficulty: port reuse blurs the boundary of responsibility.** With EPL the port is dedicated, so "up or down" is unambiguous; once EVPL shares a port, one VLAN on the same physical link can fail while port-level monitoring on the carrier side sees nothing at all.
- **Determinability the design phase should have provided**:
  - **A demarcation point** stated down to specific ports and VLANs and written into the contract annex;
  - **Per-VLAN SLA targets** (latency, loss, availability) agreed separately, instead of one figure for the whole port;
  - **Per-VLAN probes or performance measurement** on the enterprise side just inside the demarcation (such as Y.1731/CFM or two-way active measurement), able to prove "loss is already present inside my own port";
  - A **change-notification process** and traceable records of the carrier's maintenance windows.
- **The correct troubleshooting order here**: start with continuous per-VLAN measurement just inside the enterprise demarcation → if loss is confirmed inside, the problem is in the carrier domain; if the inside is clean and the application still suffers, the problem is inside the enterprise (queues, policy, uplink congestion).
- **Design improvements afterwards**: stop sharing one port between business-critical VLANs and everything else (or at least give critical traffic its own physical link or sub-port), and treat "fault determinability" as a criterion when selecting a service.
- **In one sentence**: **an SLA is not only a set of numbers, it is also "when something breaks, can we say clearly whose problem it is".**

<div class="zh" markdown="1">

**参考思路**：
- **难判定的根源：复用端口把"责任边界"变模糊了。** EPL 是独占端口，故障时"通/不通"很清楚；EVPL 端口复用后，同一物理链路上的一个 VLAN 出问题，运营商侧的端口级监控可能完全看不出异常。
- **设计阶段应留下的可判定性**：
  - **维护分界点 (Demarcation)** 明确到具体端口与 VLAN，写进合同附件；
  - 每条 VLAN 的 **SLA 指标单独约定**（时延、丢包、可用率），而不是整条端口一个指标；
  - 企业侧在分界点内侧部署**按 VLAN 的探针/性能测量**（如 Y.1731/CFM 或双向主动测量），能证明"我的设备端口内侧已经收到丢包"；
  - **变更通知流程**与运营商侧的维护窗口记录可追溯。
- **本次排查的正确顺序**：先在企业侧分界点内侧做按 VLAN 的连续测量 → 若确认内侧已丢包，问题在运营商域；若内侧正常、应用侧异常，问题在企业内部（队列、策略、上联拥塞）。
- **后续设计改进**：关键业务 VLAN 不再与其他业务共用同一端口（或至少保证关键业务有独立物理链路/独立子端口），并把"故障可判定性"作为服务选型的一项指标。
- **一句话**：**服务的 SLA 不只是数值，还包括"出了事能不能说清是谁的问题"。**

</div>

---

## Key Terms · 本章关键术语

| Term | Chinese meaning | Definition |
|------|-----------------|------------|
| Carrier Ethernet | 载波以太网 | Carrier-grade Ethernet service conforming to the MEF attributes |
| Metro Ethernet | 城域以太网 | Ethernet services delivered within a metro area |
| E-Line | 以太网专线服务 | Point-to-point Ethernet service |
| E-LAN | 以太网局域网服务 | Multipoint Ethernet service |
| E-Tree | 以太网树服务 | Point-to-multipoint service with leaf isolation |
| EPL | 以太网专线（端口型 E-Line） | Port-based E-Line |
| EVPL | 以太网虚拟专线（VLAN 型 E-Line） | VLAN-based E-Line |
| EPLAN | 以太网专用 LAN（端口型 E-LAN） | Port-based E-LAN |
| EVPLAN | 以太网虚拟专用 LAN（VLAN 型 E-LAN） | VLAN-based E-LAN |
| UNI | 用户网络接口 | User Network Interface, the customer demarcation |
| NNI | 网络节点接口 | Network Node Interface between carrier networks |
| EVC | 以太网虚拟连接 | Ethernet Virtual Connection between UNIs |
| AC | 接入电路 | Attachment Circuit on the customer side |
| VPWS | 虚拟专线服务 | Virtual Private Wire Service, point-to-point pseudowire |
| VPLS | 虚拟专用 LAN 服务 | Virtual Private LAN Service, multipoint Layer 2 VPN |
| H-VPLS | 分层 VPLS | Hierarchical VPLS with MTU aggregation |
| MTU | 多租户单元 | Multi-Tenant Unit acting as a U-PE |
| EVPN | 以太网 VPN | Ethernet VPN with a BGP control plane |
| PBB-EVPN | 提供商骨干桥接 EVPN | PBB plus EVPN with MAC-in-MAC hiding |
| Pseudowire (PW) | 伪线 | Emulated circuit carried over MPLS |
| VSI | 虚拟交换实例 | Virtual Switching Instance performing LAN bridging |
| N-PE | 网络面向提供商边缘 | Network-facing provider edge |
| U-PE | 用户面向提供商边缘 | User-facing provider edge |
| CE | 客户边缘 | Customer edge device |
| DCI | 数据中心互联 | Data Center Interconnect |
| MAC Mobility | MAC 移动性 | EVPN mechanism tracking MAC movement across PEs |
| ESI | 以太网段标识 | Ethernet Segment Identifier for multihoming |
| DF | 指定转发者 | Designated Forwarder for BUM traffic |
| A-D Route | 以太网自动发现路由（Type 1） | Ethernet Auto-Discovery route |
| IMET Route | 包含式组播以太网标签路由（Type 3） | Inclusive Multicast Ethernet Tag route |
| Split Horizon | 水平分割 | Rule that a PE never relays between PWs |
| BUM Traffic | 广播/未知单播/组播流量 | Broadcast, Unknown unicast and Multicast traffic |
| Martini / Kompella | 两种 PW 信令方式（LDP / BGP） | The two pseudowire signaling approaches |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| Carrier Ethernet | 载波以太网 |
| Metro Ethernet | 城域以太网 |
| E-Line | 以太网专线服务 |
| E-LAN | 以太网局域网服务 |
| E-Tree | 以太网树服务 |
| EPL | 以太网专线（端口型 E-Line） |
| EVPL | 以太网虚拟专线（VLAN 型 E-Line） |
| EPLAN | 以太网专用 LAN（端口型 E-LAN） |
| EVPLAN | 以太网虚拟专用 LAN（VLAN 型 E-LAN） |
| UNI | 用户网络接口 |
| NNI | 网络节点接口 |
| EVC | 以太网虚拟连接 |
| AC | 接入电路 |
| VPWS | 虚拟专线服务 |
| VPLS | 虚拟专用 LAN 服务 |
| H-VPLS | 分层 VPLS |
| MTU | 多租户单元 |
| EVPN | 以太网 VPN |
| PBB-EVPN | 提供商骨干桥接 EVPN |
| Pseudowire (PW) | 伪线 |
| VSI | 虚拟交换实例 |
| N-PE | 网络面向提供商边缘 |
| U-PE | 用户面向提供商边缘 |
| CE | 客户边缘 |
| DCI | 数据中心互联 |
| MAC Mobility | MAC 移动性 |
| ESI | 以太网段标识 |
| DF | 指定转发者 |
| A-D Route | 以太网自动发现路由（Type 1） |
| IMET Route | 包含式组播以太网标签路由（Type 3） |
| Split Horizon | 水平分割 |
| BUM Traffic | 广播/未知单播/组播流量 |
| Martini / Kompella | 两种 PW 信令方式（LDP / BGP） |

</div>

---

## Chapter Summary · 本章小结

The heart of Chapter 6 is **one thread of technology evolution**:

<div class="zh" markdown="1">

第 6 章的核心是**一条技术演进的主线**：

</div>

```
Leased line (physically dedicated, no reuse)
    ↓ emulate it over MPLS with pseudowires
VPWS (point-to-point transparency, no MAC learning)
    ↓ extend to multipoint
VPLS (full-mesh PWs plus data-plane MAC learning → O(n²), flooding, no control plane)
    ↓ move MACs into BGP
EVPN (control-plane learning, native multihoming, ARP proxy)
    ↓ cope with MAC scale explosion
PBB-EVPN (MAC-in-MAC hides customer MACs)
```

<div class="zh" markdown="1">

```
租用线路（物理独占，无复用）
    ↓ 用伪线在 MPLS 上仿真
VPWS（点到点透传，不学 MAC）
    ↓ 扩展到多点
VPLS（全互联 PW + 数据面 MAC 学习 → O(n²)、泛洪、无控制平面）
    ↓ 把 MAC 搬到 BGP
EVPN（控制面学习 + 原生多归属 + ARP 代理）
    ↓ 应对 MAC 规模爆炸
PBB-EVPN（MAC-in-MAC 隐藏客户 MAC）
```

</div>

> **One-line memory hook**: **VPWS is a cable, VPLS is a switch, EVPN is "a switch managed by a routing protocol", and PBB-EVPN is "a switch wearing two layers of MAC masks".**
>
> Every step in that evolution solved **scalability**, and every step added **operational complexity** — which is exactly why CCDE asks you to trade off "capability" against "manageability".

<div class="zh" markdown="1">

> **一句话记忆**：**VPWS 是网线，VPLS 是交换机，EVPN 是"用路由协议管理的交换机"，PBB-EVPN 是"给交换机戴上两层 MAC 面具"。**
>
> 每一次演进解决的都是**可扩展性**，而每次演进都增加了**运维复杂度**——这就是 CCDE 要求你在"能力"与"可管理性"之间做取舍的原因。

</div>
