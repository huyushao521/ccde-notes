# Chapter 13: Multicast Design · 第 13 章：组播设计

> CCDE 400-007 Official Cert Guide — Chinese translation and deep-dive notes | original pages 589–625

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译与精讲 | 原书第 589–625 页

</div>

---

## Topics Covered in This Chapter · 本章涵盖主题

- **Multicast addresses and Layer 2 mapping**: range planning, the 23-bit mapping and the 32:1 overlap
- **Layer 2 multicast**: IGMP/MLD, IGMP Snooping, PIM Snooping, Querier, MVR
- **Layer 3 multicast**: RPF check, choosing and operating PIM-DM/SM/SSM/BiDir
- **RP design**: static/Auto-RP/BSR/Anycast-RP/Phantom RP, RP placement principles
- **Inter-domain multicast**: MSDP, MBGP, cross-domain and cross-firewall design
- **Advanced design**: Live-Live, FHRP-Aware PIM, multicast inside MVPN and overlays

<div class="zh" markdown="1">

- **组播地址与二层映射**：地址范围规划、23 位映射与 32:1 重叠
- **二层组播**：IGMP/MLD、IGMP Snooping、PIM Snooping、Querier、MVR
- **三层组播**：RPF 检查、PIM-DM/SM/SSM/BiDir 的选择与机制
- **RP 设计**：静态/Auto-RP/BSR/Anycast-RP/Phantom RP，RP 放置原则
- **域间组播**：MSDP、MBGP、跨域与跨防火墙设计
- **高级设计**：Live-Live、FHRP-Aware PIM、MVPN/overlay 中的组播

</div>

---

## Chapter Introduction: Fifteen Counterintuitive Truths About Multicast Design · 本章导读：组播设计的十五个反直觉认知

Multicast is the field where "the shortest configuration produces the longest outage". One line of `ip pim sparse-mode` plus one RP address makes it "run", yet production incidents routinely last hours, because multicast forwarding **does not follow unicast intuition**.

<div class="zh" markdown="1">

组播是网络设计里"配置最短、事故最长"的领域。一条 `ip pim sparse-mode` 加一个 RP 地址就能"跑起来"，但生产事故往往持续数小时，因为组播的转发路径**不遵循单播直觉**。

</div>

### 1. Multicast has no "destination-based routing", only "reverse check of the source" · 组播没有"目的地址选路"，只有"源的反向检查"

Unicast forwarding looks at the **destination** and takes the longest match. Multicast forwarding looks at the **source**: the router checks "did this packet arrive on the **optimal interface toward the source**?" — that is **RPF (Reverse Path Forwarding)**.

<div class="zh" markdown="1">

单播转发看**目的地址**，走最长匹配。组播转发看**源地址**：路由器检查"这个组播包是从**通向源的最优接口**进来的吗？"—— 这就是 **RPF（Reverse Path Forwarding）**。

</div>

**Three consequences follow necessarily**:

<div class="zh" markdown="1">

**由此推出三个必然结果**：

</div>

- Multicast trees are **pulled by receivers** (except PIM-DM), not pushed by sources
- **Unicast routing determines the multicast path**. Change the unicast route and the tree is rebuilt
- When unicast and multicast paths diverge (asymmetric routing, policy routing, multiple exits), **multicast simply breaks** while unicast stays perfectly healthy

<div class="zh" markdown="1">

- 组播树是**由接收者"拉"出来的**（除 PIM-DM 外），不是由源"推"出来的
- **单播路由决定组播路径**。单播路由一变，组播树跟着重建
- 单播与组播路径不一致（非对称路由、策略路由、多出口）时，**组播直接断**，而单播一切正常

</div>

> 💡 **The first question in any multicast troubleshooting is always: "which interface does `show ip rpf <source>` use, and is it the interface the packet arrived on?"** 90% of "multicast does not work" cases die at this step.

<div class="zh" markdown="1">

> 💡 **组播排障第一问永远是："`show ip rpf <源>` 走哪个接口？和进来的接口一致吗？"** 90% 的"组播不通"死在这一步。

</div>

### 2. Multicast is a "broadcast domain problem", not just a "routing problem" · 组播是"广播域问题"，不只是"路由问题"

Multicast frames are sent at Layer 2 using multicast MAC addresses. Without **IGMP Snooping**, a switch treats them as broadcast and **floods them across the whole VLAN** — a 4 Mbps video stream gets pushed to 500 ports.

<div class="zh" markdown="1">

组播帧在二层用组播 MAC 发送。如果交换机没有 **IGMP Snooping**，它会把组播帧当成广播**泛洪到整个 VLAN** —— 一个 4 Mbps 的视频流会推给 500 个端口。

</div>

Conversely, if Snooping is enabled but there is **no Querier** (no PIM router in the VLAN), the snooping entries age out and multicast becomes "works intermittently".

<div class="zh" markdown="1">

反过来，如果 Snooping 开了但**没有 Querier**（VLAN 内没有 PIM 路由器），Snooping 表会被老化掉，组播又变成"时通时断"。

</div>

**Conclusion: a multicast design must design Layer 3 (PIM/RP) and Layer 2 (Snooping/Querier/Mrouter) at the same time.** Do only Layer 3 and the incidents happen in the access layer.

<div class="zh" markdown="1">

**结论：组播设计必须同时设计三层（PIM/RP）和二层（Snooping/Querier/Mrouter）。** 只做三层，事故在接入层。

</div>

### 3. The RP is not an "optional component"; in PIM-SM it is "a single point plus the state centre" · RP 不是"可选组件"，在 PIM-SM 里它是"单点 + 状态中心"

In PIM-SM every (*,G) state converges toward the RP. When the RP dies:
- Established (S,G) shortest-path trees **keep forwarding** (because they already switched to the SPT)
- But **new receivers cannot join** and **new sources cannot register**

<div class="zh" markdown="1">

PIM-SM 里所有（*，G）状态都要往 RP 汇聚。RP 挂了：
- 已建立的（S，G）最短路径树**还能继续转发**（因为已切到 SPT）
- 但**新的接收者无法加入**、**新的源无法注册**

</div>

So **"the RP died and nothing broke" is a dangerous illusion** — it only proves the current session survives. The next person who changes channel gets nothing. The RP must be made redundant (Anycast-RP + MSDP, or BSR with multiple C-RPs).

<div class="zh" markdown="1">

所以**"RP 挂了业务没断"是一个危险的假象** —— 它只说明当前会话还在，下一次有人打开频道就全断。RP 必须做冗余（Anycast-RP + MSDP，或 BSR + 多 C-RP）。

</div>

### 4. The default SPT switchover is not always a good thing · 默认的 SPT 切换不总是好事

PIM-SM by default switches from the shared tree (RPT) to the **shortest-path tree (SPT)** once a receiver gets the first packet. Latency is optimal, at the cost of:
- **N copies of (S,G) state at the source side** (one path per receiver branch)
- Source-side links possibly carrying multiple copies (if the RP sits badly)
- **Exploding router state counts** in large multi-channel deployments

<div class="zh" markdown="1">

PIM-SM 默认在接收者收到第一个包后，从共享树（RPT）切到**最短路径树（SPT）**。这样时延最优，但代价是：
- **源侧要维护 N 份（S，G）状态**（每接收者一份路径）
- 源侧链路可能承载多份流量（如果 RP 位置不好）
- 大规模多频道场景下，**路由器状态数暴增**

</div>

In some scenarios (source close to the RP, very many channels) the shared tree should be kept with `ip pim spt-threshold infinity`. **This is a genuine trade-off, not a case of "the default is best".**

<div class="zh" markdown="1">

某些场景（如源与 RP 很近、频道极多）应保留共享树，用 `ip pim spt-threshold infinity`。**这是一个真实的取舍，不是"默认最好"。**

</div>

### 5. SSM is the modern default answer · SSM 才是现代组播的默认答案

Almost all of PIM-SM's complexity (RP, registration, shared tree, SPT switchover, MSDP) comes from "**not knowing where the source is**". Yet in reality the vast majority of enterprise multicast (IPTV, video conferencing, market-data push, CCTV) **has known, fixed sources**.

<div class="zh" markdown="1">

PIM-SM 的复杂性（RP、注册、共享树、SPT 切换、MSDP）几乎全部来自"**不知道源在哪**"。而现实中绝大多数企业组播（IPTV、视频会议、行情推送、监控）**源是已知的、固定的**。

</div>

**SSM (232.0.0.0/8 + IGMPv3) removes the RP entirely**: receivers join (S,G) directly and follow the shortest-path tree to the source. **If SSM can do the job, do not use PIM-SM** — that is the biggest conceptual shift in multicast design of the past decade.

<div class="zh" markdown="1">

**SSM（232.0.0.0/8 + IGMPv3）把 RP 整个去掉了**：接收者直接 (S,G) 加入，沿最短路径树到源。**能用 SSM 就不要用 PIM-SM**，这是过去十年组播设计最大的理念变化。

</div>

### 6. Multicast has no retransmission and no congestion control · 组播没有重传，也没有拥塞控制

Unicast has TCP retransmission and window control; multicast (usually UDP) **loses a packet permanently**. So multicast quality depends entirely on:
- **A congestion-free path** (QoS reservation or bandwidth planning)
- **A stable tree structure** (switchover means packet loss)
- **No Layer 2 flooding** (flooding causes transient congestion, hence wide-scale loss)

<div class="zh" markdown="1">

单播有 TCP 重传与窗口控制；组播（通常 UDP）**丢一个包就永久丢了**。所以组播的质量完全依赖：
- **路径无拥塞**（需要 QoS 预留或带宽规划）
- **树的结构稳定**（切换 = 丢包）
- **二层不泛洪**（泛洪导致瞬时拥塞 = 大面积丢包）

</div>

**Design implication: multicast must be treated as a real-time service (QoS, bandwidth reservation, fast convergence), never as best-effort data.**

<div class="zh" markdown="1">

**设计含义：组播必须按"实时业务"对待（QoS、带宽预留、快速收敛），而不是当"尽力而为的数据"。**

</div>

### 7. Multicast addresses are a scarce resource and must be planned · 组播地址是稀缺资源，必须规划

- **32 IP multicast addresses map onto a single MAC** → Layer 2 receives traffic for groups it never asked for
- **239.0.0.0/8 is the private range**, yet many enterprises "grab one at random", and years later face address conflicts and unauditable deployments

<div class="zh" markdown="1">

- **32 个 IP 组播地址映射到同一个 MAC** → 二层会收到"不属于自己的组"的流量
- **239.0.0.0/8 是私有范围**，但很多企业"随手取一个"，几年后地址冲突、无法审计

</div>

**The correct approach: plan multicast address blocks the way you plan IP subnets** (by business, region, application), and document the mapping. Otherwise one day you discover that "turning on the meeting-room TV pushed another floor's CCTV recording onto the screen".

<div class="zh" markdown="1">

**正确做法：像规划 IP 子网一样规划组播地址块**（按业务/区域/应用划分），并把映射关系写进文档。否则你会在某天发现"打开会议室电视，另一个楼层的监控录像被推过来了"。

</div>

### 8. The multicast "control plane" and "data plane" are two completely independent states · 组播的"控制面"与"数据面"是两套完全独立的状态

In unicast, "the routing table is right, therefore forwarding is right". In multicast **the two can be fully decoupled**:

<div class="zh" markdown="1">

单播里"路由表对了，转发就对了"。组播里**两者可以完全脱钩**：

</div>

| State | Where it lives | Who maintains it | Symptom when broken |
|------|--------|-------------|-------------|
| **Control plane**: (*,G)/(S,G) entries, outgoing interface lists, RP mapping, IGMP membership | mroute table / IGMP table | PIM and IGMP | Entries exist but no traffic / traffic flowing with no entries |
| **Data plane**: packet replication and forwarding, lookup actions, caching | hardware FIB / multicast replication engine | platform implementation | **Entries correct but hardware does not forward (platform/TCAM/replication engine problem)** |

<div class="zh" markdown="1">

| 状态 | 存在哪 | 谁维护 | 出问题时表现 |
|------|--------|--------|-------------|
| **控制面**：(*,G)、(S,G) 表项、出接口列表、RP 映射、IGMP 组成员 | mroute 表 / IGMP 表 | PIM、IGMP 协议 | 表项有但流量不到 / 表项没有但流量在发 |
| **数据面**：包的复制与转发、查表动作、缓存 | 硬件 FIB / 组播复制引擎 | 平台实现 | **表项正确但硬件不转发（平台/TCAM/复制引擎问题）** |

</div>

**This is the most counterintuitive point in multicast troubleshooting**: `show ip mroute` looks perfect, the "Incoming/Outgoing" counters in `show ip mroute count` are climbing, yet the endpoint receives nothing — at this point the problem may no longer be in the routing protocol layer at all, but in:

<div class="zh" markdown="1">

**这才是组播排障最反直觉的一点**：`show ip mroute` 显示一切正常，`show ip mroute count` 的 "Incoming/Outgoing" 计数也在增长，但终端就是收不到 —— 这时问题可能已经不在路由协议层，而在：

</div>

- **Exhausted hardware multicast replication resources** (MCAST table full, insufficient replication indexes)
- **An outgoing interface list beyond platform capability** (how many interfaces can one router replicate to?)
- **Line card / ASIC multicast forwarding not programmed** (control plane pushed it, hardware failed)
- **Switch snooping table inconsistent with the router's mroute** (Layer 3 forwards, Layer 2 does not)

<div class="zh" markdown="1">

- **硬件组播复制资源耗尽**（如 MCAST 表项满、replication index 不足）
- **出接口 list 超过平台能力**（一台路由器最多能往几个接口复制？）
- **线卡/ASIC 的组播转发未编程**（控制面已下发但硬件失败）
- **交换机 Snooping 表与路由器 mroute 不一致**（三层放了，二层没放）

</div>

> 💡 **Whether you troubleshoot bottom-up or top-down depends on the symptom**:
> - **"Nothing arrives at all"** → start from RPF (control plane)
> - **"The table is right but some interfaces do not forward"** → suspect platform resources and Layer 2 immediately
> - **"It arrives but pixellates or drops"** → suspect bandwidth, QoS and MTU immediately; stop looking at protocol

<div class="zh" markdown="1">

> 💡 **排障顺序必须是"由下往上"还是"由上往下"取决于现象**：
> - **"完全收不到"** → 从 RPF 开始（控制面）
> - **"路由表对但部分接口不转发"** → 直接怀疑平台资源与二层
> - **"通了但花屏/丢包"** → 直接怀疑带宽、QoS、MTU，不要再看协议

</div>

### 9. Multicast is unidirectional: only the **receiver direction** needs a tree · 组播是"单向"的：只有**接收方向**需要建树

Many people picture multicast as two-way communication. In reality: **the receiver pulls and the source only sends**.

<div class="zh" markdown="1">

很多人把组播想成"双向通信"，实际是：**接收者主动拉，源只负责发**。

</div>

| Fact | Design implication |
|------|---------|
| The source does not know who the receivers are (outside the application) | The source side cannot "optimise for a receiver", only guarantee delivery "to the fork point of the tree" |
| A receiver joining is the only action that builds a tree (SM/SSM) | **"Source fine, network fine, nobody joined" is the most common "fault"** |
| Prune is initiated by the receiver | Stopping a stream depends on timeout or an explicit Leave; **the source cannot hang up on a receiver** |
| Multicast has no session state (only the application does) | The network cannot bill or rate-limit per session, only per (S,G) or per interface |

<div class="zh" markdown="1">

| 事实 | 设计含义 |
|------|---------|
| 源不知道谁是接收者（除应用层外） | 源侧无法"针对某接收者优化"，只能保证"送到树的分叉点" |
| 接收者加入是唯一触发建树的动作（SM/SSM） | **"源没问题、网络没问题，但没人 Join"是最常见的"故障"** |
| Prune 是接收者发起的 | 停止收看靠超时或显式 Leave，**源端无法"挂断"某个接收者** |
| 组播无会话状态（应用层才有） | 网络无法"按会话计费/限速"，只能按 (S,G) 或按接口限速 |

</div>

**The most practical corollary**: when the business says "multicast is broken", ask three questions first —

<div class="zh" markdown="1">

**这条最实用的推论**：当业务方说"组播不通"时，先问三个问题 ——

</div>

1. **Did the receiver actually send a Join?** (capture IGMP, or check `show ip igmp groups` on the LHR)
2. **Did the Join reach the RP / the source?** (walk the path looking at `show ip mroute`)
3. **Is the source actually sending?** (Incoming rate in `show ip mroute` on the FHR; note that under SSM the entry exists even when the source is silent)

<div class="zh" markdown="1">

1. **接收者真的发出 Join 了吗？**（抓包看 IGMP，或看 LHR 的 `show ip igmp groups`）
2. **Join 到达 RP / 到达源了吗？**（沿线看 `show ip mroute`）
3. **源真的在发吗？**（FHR 上 `show ip mroute` 的 Incoming rate；注意 SSM 下"源没发"时表项照样存在）

</div>

These three questions shrink "a multicast fault" from "the whole network" to "one segment".

<div class="zh" markdown="1">

这三个问题能把"组播故障"的排查范围从"整张网"缩到"某一段"。

</div>

### 10. DR, Querier, Assert Winner and DF are four **different** roles · DR、Querier、Assert Winner、DF 是四个**不同**的角色

This is the favourite confusion of CCDE multiple-choice questions and a frequent source of real outages:

<div class="zh" markdown="1">

这是 CCDE 选择题最爱混淆的点，也是真实故障的高发点：

</div>

| Role | Scope | Election rule | Which mode only | Consequence of failure |
|------|---------|---------|-----------------|---------|
| **IGMP Querier** | one **Layer 2 segment** (VLAN) | **lowest IP** (can be overridden; a switch with querier enabled competes with routers) | all modes (wherever IGMP exists) | group membership ages out → periodic multicast interruption |
| **PIM DR** | one **Layer 2 segment** (with PIM neighbours) | highest DR priority → highest IP | SM/SSM/Bidir (DM does not need it but still has a DR concept for IGMP) | nobody sends Join/Register on that segment → multicast never goes upstream |
| **Assert Winner** | one **Layer 2 segment**, **per (S,G)** | best RPF metric → if equal, highest IP | all modes (DM/SM/SSM) | duplicate forwarding on the same LAN → duplicate packets |
| **BiDir DF** | one **segment + per group**, and **directional** (toward the RP) | best unicast metric to the RP | BiDir only | traffic cannot go upstream to the RP, or several routers forward upstream at once |

<div class="zh" markdown="1">

| 角色 | 作用范围 | 选举规则 | 只在哪个模式存在 | 失效后果 |
|------|---------|---------|-----------------|---------|
| **IGMP Querier** | 一个**二层网段**（VLAN） | **最低 IP**（可被显式配置覆盖；交换机启用 querier 后与路由器竞争） | 所有模式（只要有 IGMP） | 组成员老化 → 组播周期性中断 |
| **PIM DR** | 一个**二层网段**（有 PIM 邻居） | 最高 DR 优先级 → 最高 IP | SM/SSM/Bidir（DM 不需要，但仍有 DR 概念用于 IGMP） | 该网段无人发 Join/Register → 组播不上行 |
| **Assert Winner** | 一个**二层网段**、**每个 (S,G)** | RPF 度量最优 → 度量相同比 IP | 所有模式（DM/SM/SSM） | 同一 LAN 上重复转发 → 重复包 |
| **BiDir DF** | 一个**网段 + 每个组**，且**有方向性**（朝 RP） | 到 RP 的单播度量最优 | 只有 BiDir | 流量无法上行到 RP，或多台同时上行 |

</div>

**Four real traps**:

<div class="zh" markdown="1">

**四个真实陷阱**：

</div>

1. **Querier and DR can be different boxes**: very common (Querier picks the lowest IP, DR the highest, i.e. opposite directions). If Querier is on A and DR on B, **the Join is sent by B** while **membership maintenance is done by A** — it works, but troubleshooting requires looking at both.
2. **A switch Querier can steal the role from the router**: if the access switch SVI is lower than the gateway address, the switch becomes Querier. Harmless in itself, but if the switch does not run PIM it **only sends queries and never joins PIM**; snooping's mrouter still points at the router, so it works. However, if the switch's `query-interval` differs from the router's, the group table jitters briefly.
3. **Assert only solves "duplicate forwarding on one LAN", not "duplicate paths"**: path redundancy across different LANs must be solved by IGP metrics, or by making the RPF choice unique.
4. **BiDir DF is per-group**: the same interface may be DF for one group and not for another. **BiDir troubleshooting must always name the group**; interface-level conclusions are invalid.

<div class="zh" markdown="1">

1. **Querier 与 DR 是两台不同设备**：很常见（Querier 选最低 IP，DR 选最高 IP，方向相反）。如果 Querier 在 A、DR 在 B，**Join 由 B 发**，而**成员维持由 A 做** —— 功能上可以工作，但排障时"看表"要两台都看。
2. **交换机 Querier 抢走了路由器 Querier**：接入交换机 SVI 地址比网关低时，交换机会成为 Querier。这本身无害，但如果交换机没开 PIM，**它只发查询、不参与 PIM**，Snooping 的 mrouter 仍指向路由器，功能正常。但如果交换机 Querier 的 `query-interval` 与路由器不同，会出现短暂的组表抖动。
3. **Assert 只解决"同一 LAN 重复转发"，不解决"两条路径重复"**：不同 LAN 的路径冗余要靠 IGP 度量或 PIM 的 RPF 唯一性解决。
4. **BiDir 的 DF 是 per-group 的**：同一个接口对不同组可能是 DF 也可能不是。所以 **BiDir 的排障必须带组名**，不能用接口级结论。

</div>

> ⚠️ **The most common class of "mystery failure"**: two Layer 3 switches act as HSRP gateways, both run PIM, both connect to the same access VLAN. **HSRP Active on A, PIM DR on B, IGMP Querier on B**. Result: the Join is sent by B (correct), traffic is forwarded by B to the access layer (correct), but **returning unicast (e.g. a CCTV playback request) goes to the HSRP virtual MAC and lands on A** — which holds no multicast state at all, so the service fails intermittently. The design must state explicitly **whether the multicast forwarding point and the default gateway are the same device**.

<div class="zh" markdown="1">

> ⚠️ **最常见的一类"神秘故障"**：两台三层交换机做 HSRP 网关，都跑 PIM，都连同一个接入 VLAN。**HSRP Active 在 A、PIM DR 在 B、IGMP Querier 在 B**。结果：Join 由 B 发（正确），流量由 B 转给接入层（正确），但**返回的单播（如监控的回看请求）走 HSRP 虚拟 MAC 到 A** —— A 上没有任何组播状态，业务偶发失败。设计时要明确"组播转发点与默认网关是否为同一台"。

</div>

### 11. Multicast "bandwidth" is not "stream bandwidth" but "stream bandwidth × number of branches × (1 + redundancy factor)" · 组播的"带宽"不是"流带宽"，而是"流带宽 × 分支数 × (1 + 冗余系数)"

This is where capacity planning is most often miscalculated. Unicast bandwidth is one end-to-end path; multicast bandwidth must be counted on every edge of the tree.

<div class="zh" markdown="1">

这是容量规划里最容易算错的地方。单播的带宽是"端到端一条"，组播的带宽是"树边上每一段都要算"。

</div>

```
An 8 Mbps multicast stream with 3 fork points in the tree:
  source ──── 8 Mbps ──── R1 ──┬── 8 Mbps ── R2 ── 8 Mbps ── receiver group A (10 hosts)
                                └── 8 Mbps ── R3 ── 8 Mbps ── receiver group B (20 hosts)

Link load:
 source→R1   8 Mbps
 R1→R2       8 Mbps  (not 8×10! replication to ports happens after R2)
 R2→access   8 Mbps  (with correct snooping, only to ports with subscribers)
 R1→R3       8 Mbps

But without IGMP Snooping:
 R2→access   8 Mbps × 24 ports = 192 Mbps   ← replication amplification happens here
```

<div class="zh" markdown="1">

```
一条 8 Mbps 的组播流，树有 3 个分叉点：
  源 ──── 8 Mbps ──── R1 ──┬── 8 Mbps ── R2 ── 8 Mbps ── 接收者组A(10台)
                            └── 8 Mbps ── R3 ── 8 Mbps ── 接收者组B(20台)

链路负载：
 源→R1      8 Mbps
 R1→R2      8 Mbps（不是 8×10！组播在 R2 之后才复制到端口）
 R2→接入    8 Mbps（若接入交换机 Snooping 正常，只到有订阅者的端口）
 R1→R3      8 Mbps

但如果没有 IGMP Snooping：
 R2→接入    8 Mbps × 24 端口 = 192 Mbps   ← 复制放大发生在这里
```

</div>

**Layer 3 replicates along the tree; Layer 2 replicates per port.** Therefore:

<div class="zh" markdown="1">

**三层是"按树复制"，二层是"按端口复制"**。所以：

</div>

| Location | Amplification | Control lever |
|------|---------|---------|
| Between Layer 3 routers | 1 (one copy per link, independent of receiver count) | tree structure (RP placement, SPT switchover) |
| Layer 3 → Layer 2 (router egress) | 1 | — |
| Inside a Layer 2 switch | **number of ports** (no snooping) or **number of subscribed ports** (with snooping) | IGMP Snooping |
| Wireless AP | **lowest rate × number of clients** (multicast-to-unicast conversion) | multicast-to-unicast |
| Across WAN / domains | 1 (with correct MVPN/tunnels) or **N** (if unicast copies are made per site) | MVPN / local caching |

<div class="zh" markdown="1">

| 位置 | 放大倍数 | 控制手段 |
|------|---------|---------|
| 三层路由器之间 | 1（每条链路一份，与接收者数量无关） | 树结构（RP 位置、SPT 切换） |
| 三层 → 二层（路由器出接口） | 1 | — |
| 二层交换机内部 | **端口数**（无 Snooping）或 **订阅端口数**（有 Snooping） | IGMP Snooping |
| 无线 AP | **最低速率 × 客户端数**（组播转单播后变为单播） | 组播转单播 |
| 跨 WAN / 跨域 | 1（若 MVPN/隧道正确）或 **N**（若每站点单独单播复制） | MVPN / 本地缓存 |

</div>

**Planning formulas (put them in the design document)**:

<div class="zh" markdown="1">

**规划公式（写进设计文档）**：

</div>

```
core link bandwidth = Σ (bitrate of each (S,G)) × number of groups crossing that link
access switch uplink ≥ Σ (bitrate of all groups subscribed under that switch)
AP multicast cost = frame size × frames per second × airtime at the lowest basic rate (see Chapter 11)
```

<div class="zh" markdown="1">

```
核心链路带宽 = Σ(每个 (S,G) 的码率) × 经过该链路的组数
接入交换机上行 ≥ Σ(该交换机下所有订阅组的码率)
AP 上组播开销 = 组播帧大小 × 每秒帧数 × 最低基础速率对应的 airtime（见第 11 章）
```

</div>

> 💡 **A real sense of scale**: 1,000 IPTV channels at 4 Mbps means 4 Gbps of standing traffic if the core carries "all channels everywhere". That is why **no production IPTV network lets every channel cross every link** — you need MVR/multicast VLAN aggregation plus per-region channel partitioning (only send a region's channels into that region).

<div class="zh" markdown="1">

> 💡 **一个真实的数量级感受**：1000 路 4 Mbps 的 IPTV 频道，如果核心链路"全频道全通"，就是 4 Gbps 常驻。所以**没有任何生产 IPTV 网络会让所有频道流过所有链路** —— 必须靠 MVR/组播 VLAN 收敛 + 按区域划分频道（只把某区域的频道送到该区域）。

</div>

### 12. Multicast failure modes are silent: no ICMP, no syslog, no retransmission · 组播的故障模式是"沉默的"：没有 ICMP、没有 syslog、没有重传

The feedback loop of the unicast world is entirely missing in multicast:

<div class="zh" markdown="1">

单播世界的"反馈闭环"在组播里全部缺失：

</div>

| What unicast has | What multicast lacks | Consequence |
|---------|---------|------|
| ICMP unreachable / TTL exceeded | **RPF failures drop silently** (counter only) | Cannot tell which hop dropped it |
| TCP retransmission and congestion control | **No retransmission, no congestion control** | A lost packet is lost forever |
| Log lines when a routing neighbour goes down | PIM neighbour loss usually **logs nothing** (unless configured) | Nobody notices adjacency changes |
| Observable interface traffic (unicast NetFlow) | Multicast NetFlow must be enabled explicitly (and sampling is limited on many platforms) | Cannot answer "which path does this group take" |
| ARP/ND records | IGMP membership **produces no logs** | Cannot audit "who is watching what" |

<div class="zh" markdown="1">

| 单播有的 | 组播没有 | 后果 |
|---------|---------|------|
| ICMP 不可达 / TTL 超时 | **RPF 失败静默丢包**（只有计数器） | 无法定位"哪一跳丢了" |
| TCP 重传与拥塞控制 | **无重传、无拥塞控制** | 丢一个包就永久丢 |
| 路由协议邻居 down 有日志 | PIM 邻居 down 通常**不打日志**（除非配了） | 邻居关系变化无人知道 |
| 接口流量可观测（NetFlow 单播） | 组播 NetFlow 需要专门开启（且很多平台采样率有限） | 无法回答"这个组走哪条路" |
| ARP/ND 有记录 | IGMP 组成员**不产生日志** | 无法审计"谁在看什么" |

</div>

**Therefore multicast requires an "active observability" design** (not "investigate after it breaks"):

<div class="zh" markdown="1">

**所以组播必须有"主动可观测性"设计**（不是"出问题再查"）：

</div>

| Layer | Means | Frequency | Criterion |
|------|------|------|------|
| **Protocol** | SNMP polling of `ciscoPimMIB` / `IPMROUTE-MIB` for (S,G) counts and RPF failure counters | 1–5 min | alert when (S,G) count changes > 20% |
| **Traffic** | NetFlow/IPFIX multicast export, interface `multicast` counters | 1–5 min | egress multicast rate > 1.5× baseline |
| **Tree structure** | Periodic `mrinfo`/`mtrace` sampling (key groups every 15 min) | 15 min | alert when the tree deviates from the design baseline |
| **Service** | End-to-end probes with real decoding (RTP probe, video quality probe) | 10–30 s | loss > 0.1%, MOS < 4.0 |
| **Audit** | IGMP membership snapshots into a time-series store | 5–15 min | alert on "groups that should not exist" (outside the address plan) |

<div class="zh" markdown="1">

| 层次 | 手段 | 频率 | 判据 |
|------|------|------|------|
| **协议层** | SNMP 采集 `ciscoPimMIB` / `IPMROUTE-MIB` 的 (S,G) 数、RPF 失败计数 | 1–5 min | (S,G) 数突变 > 20% 告警 |
| **流量层** | NetFlow/IPFIX 组播导出、接口 `multicast` 计数 | 1–5 min | 某接口组播出方向速率 > 基线 1.5 倍 |
| **树结构层** | 定时 `mrinfo`/`mtrace` 采样（关键组每 15 min） | 15 min | 树路径与设计基线不一致告警 |
| **业务层** | 端到端探针（真实解码，如 RTP 探针、视频质量探针） | 10–30 s | 丢包率 > 0.1%、MOS < 4.0 |
| **审计层** | IGMP 组成员快照 → 存入时序库 | 5–15 min | 出现"不该有的组"（地址规划外）告警 |

</div>

**Only when all five layers exist is multicast operable.** A network with only service probes knows "it is broken"; a network with only the protocol layer knows "the entry is there".

<div class="zh" markdown="1">

**只有四层同时具备，组播才算"可运维"。** 只有业务层探针的网络，故障时只能知道"坏了"；只有协议层的网络，故障时只能知道"表在"。

</div>

### 13. The real bottleneck in multicast design is state count, not bandwidth · 组播设计真正的瓶颈是"状态数量"，不是"带宽"

This determines the shape of every large-scale multicast design. **Router and switch multicast state capacity is a hard limit**, and it is limited in **three resource dimensions at once**:

<div class="zh" markdown="1">

这一点决定了所有大规模组播设计的形态。**路由器/交换机的组播状态容量是硬上限**，而且是**三类资源同时受限**：

</div>

| Resource | Unit | Typical limit | Consequence of exceeding it |
|------|------|-----------|---------|
| **(S,G) / (*,G) entries** | entries | hardware TCAM / software hash table | **new groups cannot be created** (symptom: "new channels will not open, old ones are fine") |
| **Outgoing interface list (OIL) length** | interfaces/entries | multicast replication engine | excess interfaces are dropped (one branch silently missing, very hard to spot) |
| **Multicast replication bandwidth (fabric)** | bps | switch fabric / backplane | replication capability drops, packet loss |

<div class="zh" markdown="1">

| 资源 | 单位 | 典型受限点 | 超限后果 |
|------|------|-----------|---------|
| **(S,G) / (*,G) 表项数** | 条 | 硬件 TCAM / 软件 hash 表 | **新组无法建立**（表现为"新频道打不开，老频道正常"） |
| **出接口列表（OIL）长度** | 接口/条 | 组播复制引擎（replication engine） | 超限接口被丢弃（组播少送一路，很难发现） |
| **组播复制带宽（fabric）** | bps | 交换网/背板 | 复制能力下降、丢包 |

</div>

**Estimating state count (must go into the design)**:

<div class="zh" markdown="1">

**状态数量的估算（必须写进设计）**：

</div>

```
PIM-SM with SPT switchover (default):
  state ≈ number of (*,G)   (= groups that have receivers)
        + number of (S,G)   (≈ groups × how many separate receiver subtrees pull distinct paths)

  i.e. state grows with the number of receiver branches, not linearly with receivers
       (100 receivers on the same LAN produce exactly 1 (S,G))

PIM-SSM:
  state ≈ number of (S,G) (= groups × sources), no (*,G)
  key advantage: unaffected by RP state or registration state

BiDir:
  state ≈ number of (*,G) (= groups), independent of the number of sources
  key advantage: constant state in many-to-many scenarios
```

<div class="zh" markdown="1">

```
PIM-SM + SPT 切换（默认）:
  状态 ≈ (*,G) 数（= 有接收者的组数）
       + (S,G) 数（≈ 组数 × 每个组被多少个"接收者子树"拉出独立路径）

  即：状态随"接收者分布的分支数"增长，而不是随接收者数量线性增长
      （同一个 LAN 上的 100 个接收者只产生 1 条 (S,G)）

PIM-SSM:
  状态 ≈ (S,G) 数（= 组数 × 源数），无 (*,G)
  关键优势：不受 RP 状态、不受注册状态影响

BiDir:
  状态 ≈ (*,G) 数（= 组数），与源数量无关
  关键优势：多源场景下状态恒定
```

</div>

> 💡 **A real capacity judgement**: a platform supports 32K mroutes with 32 outgoing interfaces per entry. If the service is **2,000 groups × an average of 40 branches**, that is 80K entries — **2.5× over**. The only correct answer is not "optimise" but **change the architecture**: MVR aggregation + per-region channel partitioning + SSM to remove (*,G) + BiDir where necessary.

<div class="zh" markdown="1">

> 💡 **一个真实的容量判断**：某平台最多 32K 条 mroute、每表项最多 32 个出接口。如果业务是 **2000 个组 × 平均 40 个分支**，就是 80K 条 —— **已经超了 2.5 倍**。这时唯一正确的解法不是"优化"，而是**改架构**：MVR 收敛 + 按区域分频道 + SSM 减少 (*,G) + 必要时 BiDir。

</div>

### 14. "It plays" and "it plays over the right path" are two different things: the design must define the correct tree shape · "能看"和"看对"是两件事：设计必须定义"树的正确形状"

Multicast has an acceptance difficulty shared by no other technology: **a wrong tree still works**.

<div class="zh" markdown="1">

组播有一个和所有其他技术都不同的验收难点：**错误的树也能工作**。

</div>

| Wrong tree | Symptom | Why nobody notices |
|---------|------|-------------|
| Traffic hairpins through the RP (should have switched to the SPT) | 20 ms extra latency, high RP bandwidth | video still plays |
| Traffic takes the backup path (RPF points at a suboptimal route) | wasted bandwidth, higher latency | usually imperceptible |
| Two groups share one link (should be separated) | they interfere at peak | only breaks when busy |
| Live-Live carried only one leg | availability is actually single-path | discovered only when that leg fails |
| Multicast tunnelled over unicast | MTU and latency problems surface late | normal most of the time |

<div class="zh" markdown="1">

| 错误的树 | 现象 | 为什么不报警 |
|---------|------|-------------|
| 流量绕经 RP（本该切 SPT） | 时延多 20 ms、RP 带宽高 | 视频照样播 |
| 走了备用路径（RPF 指向次优） | 带宽浪费、时延上升 | 一般无感知 |
| 两组流量共用一条链路（本该分离） | 峰值时互相影响 | 只在忙时出问题 |
| Live-Live 只走了一路 | 可用性实际是单路 | 直到那一路断了才发现 |
| 组播走单播隧道绕行 | MTU/时延问题延迟暴露 | 平时正常 |

</div>

**So acceptance must verify the shape, not merely reachability**:

<div class="zh" markdown="1">

**所以验收必须"验证形状"，而不是"验证通"**：

</div>

```cfg
! Baseline the key groups (sample weekly, compare with the design)
R1# show ip mroute 232.1.1.1 10.1.1.1
R1# mrinfo 10.1.1.1                ! source-side neighbours and per-interface PIM state
R1# mtrace 10.1.1.1 232.1.1.1 10.20.0.50   ! trace from receiver to source, hop by hop
```

<div class="zh" markdown="1">

```cfg
! 关键组建立基线（每周采样，与设计比对）
R1# show ip mroute 232.1.1.1 10.1.1.1
R1# mrinfo 10.1.1.1                ! 看源侧邻居与各接口的 PIM 状态
R1# mtrace 10.1.1.1 232.1.1.1 10.20.0.50   ! 从接收者追到源，逐跳看丢包
```

</div>

> ⚠️ **`mtrace` is multicast's only path-proof tool**, but it is a mixed multicast/unicast probe protocol that many networks disable "for security". **Decide at design time: is mtrace allowed? If not, what replaces it (static baselines plus NetFlow path analysis)?** A multicast network without path verification is "doing redundancy with your eyes closed".

<div class="zh" markdown="1">

> ⚠️ **`mtrace` 是组播唯一的"路径证明工具"**，但它本身是组播/单播混合的探测协议，很多网络为了"安全"全禁了。**设计阶段就要决定：是否允许 mtrace？如果不允许，用什么替代（静态基线 + NetFlow 路径分析）？** 没有路径验证能力的组播网络，等于"闭着眼睛做冗余"。

</div>

### 15. The last line of defence for multicast is rate limiting and boundaries, not trust · 组播的最后一道防线是"限速与边界"，不是"信任"

Multicast is a natural amplifier: **a 1 Mbps source can saturate 100 gigabit links**, because:

<div class="zh" markdown="1">

组播天生是"放大器"：**一个 1 Mbps 的源可以打满 100 条千兆链路**。因为：

</div>

- one packet can be replicated to N interfaces (router replication)
- one Join can pull the whole tree's traffic (receivers are not authenticated)
- one SA can make your RP join an arbitrary source (MSDP injection when unauthenticated)
- one host's IGMP Report can make a switch deliver multicast to it (unless an IGMP profile exists)

<div class="zh" markdown="1">

- 一个包可以被复制到 N 个接口（路由器复制）
- 一个 Join 可以拉出整棵树的流量（接收者无需认证）
- 一个 SA 可以让你的 RP 去加入任意源（MSDP 无认证时的注入）
- 一台主机的 IGMP Report 可以让交换机把组播送到它（除非做 IGMP profile）

</div>

**So every multicast design must include the four-piece set of "rate limiting and boundaries"**:

<div class="zh" markdown="1">

**所以所有的组播设计都必须包含"限速与边界"四件套**：

</div>

| Measure | Location | What it prevents |
|------|------|--------|
| **Multicast boundary (`ip multicast boundary`)** | all domain edges, access-layer uplinks | group leakage (groups that should not spread, spreading) |
| **Per-group / per-interface IGMP limits** | access layer | one host joining thousands of groups (blowing up the snooping table) |
| **PIM neighbour authentication (MD5)** | all PIM neighbours | forged PIM Hellos stealing DR, or flooding |
| **MSDP SA filtering + `sa-limit`** | between RPs | SA injection, memory exhaustion |
| **Multicast rate limiting (`ip multicast rate-limit` / MQC policer)** | source-side FHR, domain edges | a single source saturating a link |

<div class="zh" markdown="1">

| 措施 | 位置 | 防的是 |
|------|------|--------|
| **组播边界（`ip multicast boundary`）** | 所有域边界、接入层上联 | 组地址越界（不该扩散的组扩散了） |
| **IGMP 每组/每接口限制** | 接入层 | 一台主机加入上千个组（打爆 snooping 表） |
| **PIM 邻居认证（MD5）** | 所有 PIM 邻居 | 伪造 PIM Hello 抢 DR / 注水 |
| **MSDP SA 过滤 + sa-limit** | RP 间 | SA 注入、内存耗尽 |
| **组播速率限制（`ip multicast rate-limit` / MQC policer）** | 源侧 FHR、跨域边界 | 单个源打满链路 |

</div>

**A multicast network without this four-piece set is not "incompletely designed"; it can be taken down by a single endpoint at any time.**

<div class="zh" markdown="1">

**没有这四件套的组播网络，不是"设计不够完善"，而是"随时可能被一个终端打瘫"。**

</div>

---

## Multicast Design Methodology (Seven Steps) · 组播设计方法论（七步）

| Step | What to do | Output | Common mistake |
|------|---------|------|---------|
| **① Application profile** | Single or multiple sources? How many receivers? Real-time? Bandwidth? | Application list + multicast model classification | Designing many-to-many as single-source |
| **② Choose the forwarding mode** | SSM / PIM-SM / BiDir / PIM-DM | PIM mode per application class | Using PIM-SM with a single RP for everything |
| **③ Address planning** | Allocate multicast blocks, avoid 32:1 collisions | Address allocation table | Grabbing addresses at random with no documentation |
| **④ RP design** (if SM is used) | RP count/placement/redundancy/discovery | RP topology + redundancy scheme | Single RP, RP location following office moves |
| **⑤ Layer 2 design** | Snooping, Querier, Mrouter, MVR | Access-layer configuration baseline | Configuring only Layer 3, Layer 2 floods |
| **⑥ Inter-domain and boundaries** | MSDP / MBGP / firewall / IGMP proxy | Inter-domain scheme | Letting PIM through cross-domain with no policy |
| **⑦ Verification and operations** | mroute tables, tree shape, loss monitoring | Acceptance checklist + monitoring baseline | Verifying "it plays", not "the tree is right" |

<div class="zh" markdown="1">

| 步骤 | 要做的事 | 产出 | 常见错误 |
|------|---------|------|---------|
| **① 应用画像** | 单源还是多源？多少接收者？实时性？带宽？ | 应用清单 + 组播模型分类 | 把"多对多"当单源设计 |
| **② 选转发模式** | SSM / PIM-SM / BiDir / PIM-DM | 每类应用的 PIM 模式 | 全部用 PIM-SM + 单 RP |
| **③ 地址规划** | 分配组播地址块、避开 32:1 冲突 | 地址分配表 | 随手取地址，无文档 |
| **④ RP 设计**（若用 SM） | RP 数量/位置/冗余/发现方式 | RP 拓扑 + 冗余方案 | 单 RP、RP 位置随办公室搬迁 |
| **⑤ 二层设计** | Snooping、Querier、Mrouter、MVR | 接入层配置基线 | 只配三层，二层泛洪 |
| **⑥ 域间与边界** | MSDP / MBGP / 防火墙 / IGMP proxy | 域间方案 | 跨域直接放通 PIM，无策略 |
| **⑦ 验证与运维** | mroute 表、树结构、丢包监控 | 验收清单 + 监控基线 | 只验证"能看"，不验证"树对不对" |

</div>

### Expanding the Seven Steps (Inputs, Outputs and the Hurdles You Cannot Skip) · 七步法展开（每步的输入、输出与"过不去的坎"）

#### ① Application profile: turn the word "multicast" into something designable · ① 应用画像：把"组播"这个词拆成可设计的东西

**Multicast is only a transport. The first step in multicast design is not looking at the network, it is looking at the application.** The differences between applications' requirements are larger than the difference between "multicast and unicast".

<div class="zh" markdown="1">

**组播只是一个传输方式。设计组播的第一步不是看网络，而是看应用。** 不同的应用对网络的要求差异，比"组播 vs 单播"的差异还大。

</div>

| Application | Typical protocol | Model | Bitrate | Latency requirement | Loss tolerance | Key constraint |
|------|---------|------|------|---------|---------|---------|
| **IPTV / live** | MPEG-TS over UDP, RTP | one-to-many | 2–15 Mbps per channel | 200–500 ms startup, zap < 2 s | very low (pixellation) | many channels, frequent zapping, needs fast channel change (FCC) |
| **Video conferencing (multi-party)** | RTP/SRTP | **many-to-many** | 0.5–8 Mbps | **< 150 ms** | low | several speakers at once → BiDir; needs QoS |
| **Corporate training / all-hands** | Webex/Zoom internal stream | one-to-many | 1–5 Mbps | 500 ms | low | sudden audience spikes (all-hands meetings) |
| **Financial market data** | in-house UDP multicast | one-to-many + **dual leg** | tens of kbps to a few Mbps | **< 10 ms jitter** | **zero** | Live-Live, sequence numbers detect loss, microbursts |
| **Video surveillance** | RTP over UDP/RTSP | one-to-few (multiple viewers) | 1–8 Mbps per camera | 500 ms | medium (brief stutter acceptable) | enormous camera and group counts |
| **Desktop/OS image distribution** | UDP block transfer (SCCM/MDT) | one-to-many | tens of Mbps bursts | none | medium (has retransmission) | **very high burst bandwidth**, needs rate limiting |
| **Trading engines / replay** | in-house | one-to-many | small | extremely low | zero | designed together with market data |
| **Routing protocols themselves** | OSPF/EIGRP/RIPv2 (224.0.0.x) | link-local | tiny | — | — | **must not be mixed with service groups, must not be blocked by boundaries** |
| **PXE / system boot** | TFTP + optional multicast | one-to-many | small | none | has retransmission | usually does not need multicast |
| **SAN boot / storage sync** | — | — | — | — | — | generally not IP multicast |

<div class="zh" markdown="1">

| 应用 | 典型协议 | 模型 | 码率 | 时延要求 | 丢包容忍 | 关键约束 |
|------|---------|------|------|---------|---------|---------|
| **IPTV / 直播** | MPEG-TS over UDP, RTP | 一对多 | 2–15 Mbps/频道 | 200–500 ms 启动，切换 < 2 s | 极低（花屏） | 频道数多、切换频繁、需要快速频道切换（FCC） |
| **视频会议（多方）** | RTP/SRTP | **多对多** | 0.5–8 Mbps | **< 150 ms** | 低 | 多人同时发言 → BiDir；需要 QoS |
| **企业培训 / 全员直播** | Webex/Zoom 内部推流 | 一对多 | 1–5 Mbps | 500 ms | 低 | 观看人数突发（全员大会） |
| **金融行情** | 自研 UDP 组播 | 一对多 + **双路** | 几十 kbps–数 Mbps | **< 10 ms 抖动** | **零容忍** | Live-Live、序列号可检测、微突发 |
| **视频监控** | RTP over UDP/RTSP | 一对少（多个监看者） | 1–8 Mbps/路 | 500 ms | 中（可接受短暂卡顿） | 摄像头数量巨大、组数巨大 |
| **桌面/OS 镜像分发** | UDP 块传输（如 SCCM/MDT） | 一对多 | 数十 Mbps 突发 | 无 | 中（有重传机制） | **突发带宽极高**，需要限速 |
| **交易撮合 / 撮合行情回放** | 自研 | 一对多 | 小 | 极低 | 零 | 与行情合并设计 |
| **路由协议自身** | OSPF/EIGRP/RIPv2 (224.0.0.x) | 链路本地 | 极小 | — | — | **不能与业务组混用，不能被边界阻断** |
| **PXE / 系统启动** | TFTP + 可选组播 | 一对多 | 小 | 无 | 有重传 | 通常不需要组播 |
| **SAN boot / 存储同步** | — | — | — | — | — | 一般不用 IP 组播 |

</div>

**The six questions of an application profile (a table that belongs in the design document)**:

<div class="zh" markdown="1">

**应用画像的六问（写进设计文档的表格）**：

</div>

| Question | Why ask | Design decision it drives |
|------|---------|---------------|
| **One source or many?** | Determines SM/SSM/BiDir | single source → SSM; many sources → BiDir or SM |
| **Is the source address fixed? Do receivers know the source?** | Determines whether SSM is possible | know it → SSM; do not → SM + SSM Mapping |
| **How many receivers? Where are they?** | Determines state count, tree branches, Layer 2 flooding risk | dispersed → SPT; concentrated → shared tree is acceptable |
| **How many concurrent groups? What is their lifetime?** | Determines state count and ageing strategy | many short-lived groups → state churn, must evaluate the platform |
| **Bitrate and burst characteristics?** | Determines bandwidth planning and QoS | constant low bitrate vs microbursts (market data) are completely different |
| **Can loss or switchover delay be tolerated?** | Determines Live-Live, FCC, QoS strictness | zero tolerance → dual legs + strict QoS |

<div class="zh" markdown="1">

| 问题 | 为什么问 | 影响的设计决策 |
|------|---------|---------------|
| **单源还是多源？** | 决定 SM/SSM/BiDir | 单源 → SSM；多源 → BiDir 或 SM |
| **源地址固定吗？接收者知道源吗？** | 决定能否用 SSM | 知道 → SSM；不知道 → SM + SSM Mapping |
| **多少接收者？分布在哪？** | 决定状态数、树的分支、二层泛洪风险 | 分散 → SPT；集中 → 共享树可接受 |
| **多少并发组？每组的生命周期？** | 决定状态数与老化策略 | 组多且短命 → 状态抖动，需评估平台 |
| **码率与突发特性？** | 决定带宽规划与 QoS | 恒定小码率 vs 微突发（行情）差异极大 |
| **能否容忍丢包/切换时延？** | 决定是否 Live-Live、是否 FCC、是否 QoS 严格 | 零容忍 → 双路 + 严格 QoS |

</div>

> ⚠️ **The most common requirements error**: the business says "we need multicast" when the real requirement is "ten thousand people watching a live stream at once". That may be simpler with **CDN/edge caching plus unicast** (especially across a WAN). **Multicast applies when three conditions hold: identical content, many receivers, controllable network.** Remove one and the maths must be redone.

<div class="zh" markdown="1">

> ⚠️ **最常见的需求错误**：业务方说"我们要组播"，实际需求是"一万人同时看直播"。这用 **CDN/边缘缓存 + 单播** 可能比组播更简单（尤其跨 WAN）。**组播的适用条件是"同一份内容、大量接收者、网络可控"**，三个条件缺一个就要重新算账。

</div>

#### ② Forwarding mode selection: turn step ② into a decision flow · ② 转发模式选择：把七步法第②步做成判定流程

```
              Does the application need "any source may send"?
              ├─ No (source fixed/known) ───────────→ ★ SSM
              │      └─ Terminals only support IGMPv2? → SSM Mapping
              └─ Yes
                 ├─ Is it many-to-many and does it need optimal paths?
                 │   ├─ Yes (several people speaking in real time) ────→ ★ BiDir
                 │   └─ No
                 │      ├─ Receivers extremely dense, small scale ────→ PIM-DM (small networks only)
                 │      └─ Otherwise ─────────────────→ ★ PIM-SM (RP redundancy is mandatory)
                 └─ Note: one network can mix them
                    different group ranges use different modes (e.g. 232/8 → SSM, 239.10/16 → SM, 239.20/16 → BiDir)
```

<div class="zh" markdown="1">

```
              应用是否要求"任意源都能发"？
              ├─ 否（源固定/已知）──────────────→ ★ SSM
              │      └─ 终端只支持 IGMPv2？ → SSM Mapping
              └─ 是
                 ├─ 是否"多对多"且要求路径最优？
                 │   ├─ 是（多人实时发言）────────→ ★ BiDir
                 │   └─ 否
                 │      ├─ 接收者极密集、规模小 ────→ PIM-DM（仅限小网）
                 │      └─ 其他 ─────────────────→ ★ PIM-SM（必须做 RP 冗余）
                 └─ 注意：同一网络可以"混用"
                    不同组范围用不同模式（如 232/8 → SSM，239.10/16 → SM，239.20/16 → BiDir）
```

</div>

**Mixing is normal, and it is the recommended practice**:

<div class="zh" markdown="1">

**混用是正常的，而且是推荐做法**：

</div>

```cfg
! Within one PIM domain, use different modes per group range (Cisco syntax)
ip pim ssm range 232.0.0.0/8              ! 232/8 goes SSM (no RP needed)
ip pim bidir-enable
ip pim rp-address 10.0.0.1 group-list 239.20.0.0/16 bidir
ip pim rp-address 10.0.0.1 group-list 239.10.0.0/16
ip pim rp-address 10.0.0.2 group-list 239.30.0.0/16
! Groups not listed fall back to the static RP or Auto-RP/BSR
```

<div class="zh" markdown="1">

```cfg
! 同一个 PIM 域内，按组范围使用不同模式（Cisco 语法示例）
ip pim ssm range 232.0.0.0/8              ! 232/8 走 SSM（不需要 RP）
ip pim bidir-enable
ip pim rp-address 10.0.0.1 group-list 239.20.0.0/16 bidir
ip pim rp-address 10.0.0.1 group-list 239.10.0.0/16
ip pim rp-address 10.0.0.2 group-list 239.30.0.0/16
! 未列出的组默认走静态 RP 或 Auto-RP/BSR
```

</div>

> 💡 **The key constraint when mixing**: **one group address can belong to only one mode**. 232/8 and BiDir are mutually exclusive; and the RP mapping for a given group must be consistent network-wide (see ④).

<div class="zh" markdown="1">

> 💡 **混用的关键约束**：**同一个组地址只能属于一种模式**。232/8 与 BiDir 互斥；同一组的 RP 映射必须全网一致（见 ④）。

</div>

#### ③ Address planning: three hard rules and three mandatory checks · ③ 地址规划：三条硬规则与三个"必查"

The rules were given above; here are the **executable checks**:

<div class="zh" markdown="1">

上面给了规则，这里补充**可执行的检查方法**：

</div>

| Check | Method | Tool |
|------|------|------|
| **MAC collision detection** | Compute `01:00:5e:<low 23 bits>` for every group; no duplicates within a VLAN | spreadsheet/script (see the code below) |
| **Out-of-range detection** | Service groups must not fall in 224.0.0.0/24; 232/8 and 239/8 must not be mixed | ACL audit + SoT validation |
| **Unplanned group detection** | A group appears in the running network that is not in the documentation → alert immediately | periodic `show ip mroute` snapshot comparison |

<div class="zh" markdown="1">

| 检查 | 方法 | 工具 |
|------|------|------|
| **MAC 冲突检测** | 计算每个组地址的 `01:00:5e:<低23位>`，同 VLAN 内不得重复 | 表格/脚本（见下方代码） |
| **范围越界检测** | 业务组不得落入 224.0.0.0/24、232/8 与 239/8 不得混用 | ACL 审计 + SoT 校验 |
| **规划外组检测** | 运行网中出现"文档里没有的组" → 立即告警 | 定期 `show ip mroute` 快照比对 |

</div>

```python
# Multicast address -> MAC collision detection (drop it into CI)
def mcast_mac(ip: str) -> str:
    o = [int(x) for x in ip.split('.')]
    # take the low 23 bits: low 7 bits of octet 2 + octet 3 + octet 4
    b = [(o[1] & 0x7f), o[2], o[3]]
    return "01:00:5e:" + ":".join(f"{x:02x}" for x in b)

def check(addrs):
    seen = {}
    for a in addrs:
        m = mcast_mac(a)
        if m in seen:
            print(f"collision: {a} <-> {seen[m]}  both map to {m}")
        seen[m] = a
```

<div class="zh" markdown="1">

```python
# 组播地址 → MAC 冲突检测（放进 CI 即可）
def mcast_mac(ip: str) -> str:
    o = [int(x) for x in ip.split('.')]
    # 取低 23 位：第二段低 7 位 + 第三段 + 第四段
    b = [(o[1] & 0x7f), o[2], o[3]]
    return "01:00:5e:" + ":".join(f"{x:02x}" for x in b)

def check(addrs):
    seen = {}
    for a in addrs:
        m = mcast_mac(a)
        if m in seen:
            print(f"冲突: {a} <-> {seen[m]}  同为 {m}")
        seen[m] = a
```

</div>

**IPv6 differences (must be stated explicitly)**:

<div class="zh" markdown="1">

**IPv6 的差异（必须写清）**：

</div>

| Item | IPv4 | IPv6 |
|----|------|------|
| Group address range | 224.0.0.0/4 | **FF00::/8** |
| Layer 2 mapping | 01:00:5E + low 23 bits | **33:33 + low 32 bits** |
| Overlap | **32:1 (severe)** | no practical overlap |
| Private/domain scope | 239.0.0.0/8 (administratively scoped) | **the scope field in FF00::/8** (FF02 link, FF05 site, FF08 organisation, FF0E global) |
| SSM | 232.0.0.0/8 | **FF3x::/32** (x is the scope) |
| Group membership | IGMPv1/v2/v3 | **MLDv1/v2** (ICMPv6 types 130/131/132/143) |
| Layer 2 snooping | IGMP Snooping | **MLD Snooping** (many platforms enable both by default) |
| Common pitfall | 32:1 collisions | **scope confusion** (FF05 forwarded across sites, FF02 misconfigured as a service group) |

<div class="zh" markdown="1">

| 项 | IPv4 | IPv6 |
|----|------|------|
| 组地址范围 | 224.0.0.0/4 | **FF00::/8** |
| 二层映射 | 01:00:5E + 低 23 位 | **33:33 + 低 32 位** |
| 重叠 | **32:1（严重）** | 无实际重叠问题 |
| 私有/域内 | 239.0.0.0/8（Administratively Scoped） | **FF00::/8 的 scope 字段**（FF02 链路、FF05 站点、FF08 组织、FF0E 全球） |
| SSM | 232.0.0.0/8 | **FF3x::/32**（x 为 scope） |
| 组成员协议 | IGMPv1/v2/v3 | **MLDv1/v2**（ICMPv6，类型 130/131/132/143） |
| 二层侦听 | IGMP Snooping | **MLD Snooping**（很多平台默认同时开） |
| 常见坑 | 32:1 冲突 | **scope 混用**（FF05 被跨站点转发、FF02 被误配成业务组） |

</div>

#### ④ RP design: one decision table beats ten principles · ④ RP 设计：一张"决策表"胜过十条原则

| Your constraint | Choose this |
|---------|--------|
| All Cisco, medium scale, want automation | **Auto-RP** (note that 224.0.1.39/40 need dense flooding or `sparse-dense-mode`) |
| Multi-vendor | **BSR** (the standard) |
| Need load sharing plus sub-second failover | **Anycast-RP + MSDP** (RFC 4610) |
| Only active/standby needed, do not want MSDP | **Phantom RP** |
| Very stable topology, small scale | **Static RP** |
| Large multi-region (multi-site WAN) | **one Anycast-RP pair per region**, separated by `group-list` or scoped zones |
| Sources are fixed | **no RP at all** (use SSM) |

<div class="zh" markdown="1">

| 你的约束 | 选这个 |
|---------|--------|
| 全 Cisco、规模中等、希望自动 | **Auto-RP**（注意 224.0.1.39/40 需要 dense 泛洪或 `sparse-dense-mode`） |
| 多厂商 | **BSR**（标准） |
| 要求负载分担 + 秒级切换 | **Anycast-RP + MSDP**（RFC 4610） |
| 只有主备需求、不想引入 MSDP | **Phantom RP** |
| 拓扑极稳定、规模小 | **静态 RP** |
| 跨区域大规模（多站点 WAN） | **每区域一对 Anycast-RP**，用 `group-list` 或 scoped zone 分域 |
| 源固定 | **根本不需要 RP**（用 SSM） |

</div>

#### ⑤ Layer 2 design: an access-layer multicast baseline · ⑤ 二层设计：一份"接入层组播基线"

```cfg
! Access switch multicast baseline (Cisco IOS syntax)
ip igmp snooping                                    ! enable globally
ip igmp snooping vlan 100                           ! enable per VLAN
ip igmp snooping vlan 100 querier                   ! fallback when there is no Layer 3 multicast
ip igmp snooping querier address 10.100.0.254
ip igmp snooping vlan 100 fast-leave                ! fast leave on access ports (careful: disable where a port has many hosts)
ip igmp snooping vlan 100 mrouter interface Gi1/0/49   ! static uplink designation (optional)
ip igmp snooping vlan 100 limit 200                 ! cap the number of groups (protect the table)
ip igmp snooping vlan 100 limit action 2            ! action on exceeding the limit (platform dependent)
! multicast storm control (stop abnormal multicast from saturating a port)
interface Gi1/0/1
 switchport
 storm-control multicast level 10.00                ! careful: this can kill legitimate high-bitrate multicast
```

<div class="zh" markdown="1">

```cfg
! 接入层交换机组播基线（Cisco IOS 语法）
ip igmp snooping                                    ! 全局启用
ip igmp snooping vlan 100                           ! 按 VLAN 启用
ip igmp snooping vlan 100 querier                   ! 无三层组播时的兜底
ip igmp snooping querier address 10.100.0.254
ip igmp snooping vlan 100 fast-leave                ! 接入口快速离开（谨慎：一对多主机场景禁用）
ip igmp snooping vlan 100 mrouter interface Gi1/0/49   ! 上联静态指定（可选）
ip igmp snooping vlan 100 limit 200                 ! 限制组数（防打爆表）
ip igmp snooping vlan 100 limit action 2            ! 超限动作（按平台）
! 组播风暴控制（防止异常组播打满端口）
interface Gi1/0/1
 switchport
 storm-control multicast level 10.00                ! 谨慎：会误杀合法大流量组播
```

</div>

**Five parameters that must be defined explicitly**:

<div class="zh" markdown="1">

**必须明确定义的五个参数**：

</div>

| Parameter | Default (Cisco) | Design recommendation |
|------|--------------|---------|
| IGMP query interval | 125 s | keep the default; video services can shorten to 60 s (faster membership discovery) |
| IGMP max response time | 10 s | shorten in high-density scenarios (lower leave latency) |
| Group membership timeout | 260 s (v2) | tied to the query interval; never less than `3.5 × query-interval` |
| **Fast Leave** | off | **enable only where one host sits on one port**; otherwise it evicts other hosts on the same port |
| **Group limit** | none | **must be set**, otherwise one host can join thousands of groups and blow up the table |

<div class="zh" markdown="1">

| 参数 | 默认（Cisco） | 设计建议 |
|------|--------------|---------|
| IGMP 查询间隔 | 125 s | 保持默认；视频业务可缩短到 60 s（加快成员发现） |
| IGMP 最大响应时间 | 10 s | 高密度场景缩短（减少离开时延） |
| 组超时（Group Membership Timeout） | 260 s（v2） | 与查询间隔联动；不能小于 `3.5 × query-interval` |
| **快速离开（Fast Leave）** | 关闭 | **仅在一台主机一个端口时开启**；否则会误踢同端口其他主机 |
| **组数限制（Limit）** | 无 | **必须设**，否则一台主机可以加入上千组打爆表 |

</div>

#### ⑥ Inter-domain and boundaries: distinguishing three kinds of boundary · ⑥ 域间与边界：三类边界的区分

| Boundary type | Implemented with | What it blocks | Common mistake |
|---------|-----------|--------|---------|
| **Multicast domain boundary (scope)** | `ip multicast boundary <acl>` / admin scope | group address ranges | configured on only one side of a PIM interface; the other side leaks |
| **PIM neighbour boundary** | no `ip pim` on the interface, or PIM authentication + ACL | devices you do not want as PIM neighbours | PIM disabled but IGP still advertising: routes come in, multicast does not (inconsistent) |
| **RP boundary (BSR/Auto-RP scope)** | BSR border / Auto-RP scope ACL + TTL | RP announcements crossing domains | scope forgotten → the other domain learns your RPs and joins the wrong one |
| **Source/group policy boundary** | MSDP `sa-filter`, `ip multicast boundary`, first-hop ACLs | illegitimate sources and groups | no policy → any source can inject |

<div class="zh" markdown="1">

| 边界类型 | 用什么实现 | 拦什么 | 常见错误 |
|---------|-----------|--------|---------|
| **组播域边界（Scope）** | `ip multicast boundary <acl>` / 管理范围 | 组地址范围 | 只配在 PIM 接口一侧，另一侧漏 |
| **PIM 邻居边界** | 接口不配 `ip pim`、或 PIM 认证 + ACL | 不希望建立 PIM 邻居的设备 | 只关 PIM 但 IGP 仍通告，路由进但组播不进（不一致） |
| **RP 边界（BSR/Auto-RP scope）** | BSR border / Auto-RP scope ACL + TTL | RP 通告跨域 | 忘记 scope → 对端域学到你域内的 RP，加入错 RP |
| **源/组策略边界** | MSDP `sa-filter`、`ip multicast boundary`、首跳 ACL | 非法源、非法组 | 无策略 → 任意源可注入 |

</div>

#### ⑦ Verification: an acceptance checklist (details in the acceptance and operations section at the end of this chapter) · ⑦ 验证：一份"验收清单"（详见本章末"验收与运维"节）

**Eight numbers that must appear in the design document**:

<div class="zh" markdown="1">

**设计文档里必须出现的 8 个数字**：

</div>

1. **Bitrate and concurrent group count** for each application class
2. **Peak multicast bandwidth on each key link** (including the redundancy factor)
3. **(S,G) entry peak per core/aggregation device** versus platform limits
4. **Number of subscribed ports** per multicast VLAN
5. **RP carrying bandwidth** (when the shared tree is kept) and RP CPU baseline
6. **Number of tree branches** (average outgoing interfaces per group)
7. **Switchover budget**: how long RP failure, PIM neighbour failure and link failure each take to recover
8. **Access-layer group limits** (per port / per VLAN)

<div class="zh" markdown="1">

1. 每类应用的**码率与并发组数**
2. **每条关键链路**的组播带宽峰值（含冗余系数）
3. 每台核心/汇聚设备的 **(S,G) 表项峰值**与平台上限
4. 每个组播 VLAN 的**订阅端口数**
5. **RP 承载带宽**（保留共享树时）与 RP CPU 基线
6. **树的分支数**（每个组的平均出接口数）
7. **切换预算**：RP 故障、PIM 邻居故障、链路故障各需多久恢复
8. **接入层组数上限**（每端口/每 VLAN）

</div>

---

## Foundation Topics · 基础内容

---

## Multicast Fundamentals · 组播基础

### Multicast Address Ranges (your first "land deed" in the design) · 组播地址范围（设计的第一份"土地证"）

| Range | Block | Forwarding behaviour | Use | Design note |
|------|-------|---------|------|---------|
| **Link-local control** | 224.0.0.0/24 | **TTL=1, not forwarded by routers** | the protocols themselves (PIM/OSPF/IGMP/HSRP) | never allocate to services |
| **Global (Internet)** | 224.0.1.0 ~ 231.255.255.255 | routable | traditional ASM multicast | rarely used inside enterprises |
| **SSM (source-specific)** | **232.0.0.0/8** | routable, (S,G) joins | IPTV, video distribution, market data | **modern enterprises should prefer this block** |
| **GLOP** | 233.0.0.0/8 | routable | global allocation by AS number (233.<AS high>.<AS low>.x/24) | for cross-domain operations |
| **ADMIN scope (private)** | **239.0.0.0/8** | routable (intra-domain) | enterprise internal multicast (the RFC1918 equivalent) | **the main block for enterprises** |
| **Single-hop / local management** | 239.255.0.0/16 | intra-domain | intra-site use | carve per site when multi-site |

<div class="zh" markdown="1">

| 范围 | 地址块 | 转发行为 | 用途 | 设计提示 |
|------|-------|---------|------|---------|
| **链路本地控制** | 224.0.0.0/24 | **TTL=1，路由器不转发** | 协议自身（PIM/OSPF/IGMP/HSRP） | 绝不能分配给业务 |
| **全球范围（Internet）** | 224.0.1.0 ~ 231.255.255.255 | 可路由 | 传统 ASM 组播 | 企业内一般不用 |
| **SSM（源特定）** | **232.0.0.0/8** | 可路由，(S,G) 加入 | IPTV、视频分发、行情 | **现代企业应优先用这段** |
| **GLOP** | 233.0.0.0/8 | 可路由 | 按 AS 号全球分配（233.<AS高>.<AS低>.x/24） | 跨域运营用 |
| **ADMIN 范围（私有）** | **239.0.0.0/8** | 可路由（域内） | 企业内部组播（等同 RFC1918） | **企业主用地段** |
| **单跳/本地管理** | 239.255.0.0/16 | 域内 | 站点内部使用 | 多站点时按站点切块 |

</div>

**Well-known addresses worth memorising**:

<div class="zh" markdown="1">

**几个必须记住的知名地址**：

</div>

| Address | Purpose |
|------|------|
| 224.0.0.1 | All Hosts (all hosts on the segment) |
| 224.0.0.2 | All Routers |
| 224.0.0.5 / 224.0.0.6 | OSPF AllSPFRouters / AllDRouters |
| 224.0.0.9 | RIPv2 |
| **224.0.0.13** | **PIMv2 All PIM Routers** (BSR messages are sent here too) |
| 224.0.0.22 | IGMPv3 reports |
| **224.0.1.39 / 224.0.1.40** | **Auto-RP Announce (C-RP) / Discovery (mapping agent)** |

<div class="zh" markdown="1">

| 地址 | 用途 |
|------|------|
| 224.0.0.1 | All Hosts（本网段所有主机） |
| 224.0.0.2 | All Routers |
| 224.0.0.5 / 224.0.0.6 | OSPF AllSPFRouters / AllDRouters |
| 224.0.0.9 | RIPv2 |
| **224.0.0.13** | **PIMv2 All PIM Routers**（BSR 消息也发这里） |
| 224.0.0.22 | IGMPv3 报告 |
| **224.0.1.39 / 224.0.1.40** | **Auto-RP Announce（C-RP）/ Discovery（Mapping Agent）** |

</div>

### Multicast Address Planning (write executable rules) · 组播地址规划（写出可执行的规则）

One of the most common enterprise multicast incidents is "addresses grabbed at random", which becomes unauditable after a few years. Plan along these lines (directly usable in a design document):

<div class="zh" markdown="1">

企业里最常见的组播事故之一是"地址随手取"，几年后无法审计。建议按下面的规则规划（可直接放进设计文档）：

</div>

```
239.0.0.0/8  ← enterprise internal multicast
├── 239.<site ID>.0.0/16       one block per site (e.g. 239.10.0.0/16 = Beijing HQ)
│   ├── 239.<site>.<service>.0/24 one block per service (10=video conferencing, 20=IPTV, 30=CCTV, 40=market data)
│   └── 239.<site>.<service>.<index>
└── 239.255.0.0/16            reserved (testing/temporary)

232.0.0.0/8  ← SSM only
└── 232.<site ID>.<service>.0/24  planned with the same logic
```

<div class="zh" markdown="1">

```
239.0.0.0/8  ← 企业内部组播
├── 239.<站点ID>.0.0/16       每站点一块（如 239.10.0.0/16 = 北京总部）
│   ├── 239.<站点>.<业务>.0/24 每业务一块（10=视频会议，20=IPTV，30=监控，40=行情）
│   └── 239.<站点>.<业务>.<序号>
└── 239.255.0.0/16            保留（测试/临时）

232.0.0.0/8  ← SSM 专用
└── 232.<站点ID>.<业务>.0/24  按同样的逻辑规划
```

</div>

**Three hard rules**:

<div class="zh" markdown="1">

**三条硬规则**：

</div>

1. **Avoid the 32:1 overlap**: the mapping keeps only the low 23 bits, so **the 5 discarded bits are "the low 4 bits of the second octet plus the top bit of the third"**. Consequently these pairs always collide: `239.10.1.1` and `239.138.1.1` (second octets differ by 128), and `224.10.1.1` and `239.10.1.1` (224–239 differ only in the discarded bit)
2. **Service separation**: video conferencing and IPTV get different /24s so PIM boundaries and QoS are easy
3. **Documentation**: the address table goes into the SoT (IPAM) and changes go through a PR — multicast addresses are configuration data too

<div class="zh" markdown="1">

1. **避开 32:1 重叠**：映射只保留后 23 位，**被丢弃的 5 位是"第二段的低 4 位 + 第三段的最高位"**。因此以下两组必然撞车：`239.10.1.1` 与 `239.138.1.1`（第二段差 128）、`224.10.1.1` 与 `239.10.1.1`（224–239 之间只差被丢弃的位）
2. **业务隔离**：视频会议与 IPTV 用不同 /24，便于做 PIM 边界与 QoS
3. **文档化**：地址表进 SoT（IPAM），变更走 PR —— 组播地址也是"配置数据"

</div>

#### IP Multicast to MAC Address Mapping · IP 组播到 MAC 地址映射

```
multicast MAC = 01:00:5E:XX:XX:XX

IP multicast address 239.1.2.3
-> binary: 11101111.00000001.00000010.00000011
-> take the low 23 bits: 0000001.00000010.00000011
-> MAC: 01:00:5E:01:02:03

Problem: 32 IP multicast addresses map to the same MAC address (5 bits are discarded)
```

<div class="zh" markdown="1">

```
组播 MAC = 01:00:5E:XX:XX:XX

IP 组播地址 239.1.2.3
→ 二进制: 11101111.00000001.00000010.00000011
→ 取后 23 位: 0000001.00000010.00000011
→ MAC: 01:00:5E:01:02:03

问题: 32 个 IP 组播地址映射到同一 MAC 地址（5 位被丢弃）
```

</div>

> ⚠️ **The 5-bit overlap problem**: only 23 of the low 28 bits of an IP multicast address are mapped to the MAC, so **32 different IP multicast addresses map to the same MAC**.

<div class="zh" markdown="1">

> ⚠️ **5 位重叠问题**：IP 组播地址的后 28 位中只有 23 位映射到 MAC，**32 个不同的 IP 组播地址会映射到同一个 MAC**。

</div>

**What this means (design implications)**:

<div class="zh" markdown="1">

**这意味着什么（设计含义）**：

</div>

| Symptom | Mechanism |
|------|------|
| You joined 239.10.1.1 but also receive traffic for 239.138.1.1 | both map to MAC `01:00:5E:0A:01:01` (second octets differ by 128, the top bit is discarded), and the switch forwards by MAC |
| Wasted Layer 2 bandwidth in high-density multicast | unwanted multicast frames arrive and are filtered by the host (burning host CPU) |
| Especially severe on wireless | multicast is sent at the lowest rate, so surplus multicast costs a lot of airtime |

<div class="zh" markdown="1">

| 现象 | 机制 |
|------|------|
| 加入了 239.10.1.1，却同时收到 239.138.1.1 的流量 | 两者 MAC 都是 `01:00:5E:0A:01:01`（第二段差 128，最高位被丢弃），交换机按 MAC 转发 |
| 高密度组播场景下二层带宽浪费 | 收到不需要的组播帧，再由主机侧过滤（消耗主机 CPU） |
| 无线场景尤其严重 | 组播按最低速率发送，多余的组播 = 大量 airtime |

</div>

**How to avoid it**:

<div class="zh" markdown="1">

**规避方法**：

</div>

1. **Do not use two group addresses whose second octets differ by 128 within the same broadcast domain** (e.g. 239.10.1.1 and 239.138.1.1); and do not reuse the same last three octets across 224–239 (e.g. 224.10.1.1 and 239.10.1.1)
2. **Allocate in blocks** (one /24 per service, **with the second octet fixed and < 128 inside a service**), so the plan prevents it structurally
3. **Aggregate multicast at Layer 2 via multicast VLANs** (deliver multicast only to VLANs with subscribers)
4. **Add a CI check**: no two multicast addresses in the same VLAN may compute to the same MAC

<div class="zh" markdown="1">

1. **同一广播域内不要使用"第二段相差 128"的两个组地址**（如 239.10.1.1 与 239.138.1.1）；也不要跨 224–239 使用同一后三段（如 224.10.1.1 与 239.10.1.1）
2. **按块分配**（每个业务一个 /24，**同一业务内第二段固定且 < 128**），从规划上避免
3. **接入层做组播 VLAN 收敛**（只把组播送到有订阅者的 VLAN）
4. **有 CI 时加一条校验**：同一 VLAN 内所有组播地址计算出的 MAC 不得重复

</div>

**How IPv6 improves on this**: an IPv6 multicast MAC is `33:33:` plus the **low 32 bits** of the group address, so **there is no overlap problem** (enough bits are mapped). This is one detail where IPv6 beats IPv4 in Layer 2 multicast behaviour.

<div class="zh" markdown="1">

**IPv6 的改进**：IPv6 组播 MAC 为 `33:33:` + 组地址的**低 32 位**，**没有重叠问题**（因为映射位数足够）。这是 IPv6 在组播二层行为上优于 IPv4 的一个细节。

</div>

---

## Layer 2 Multicast · 二层组播

### Why Layer 2 Breaks More Often Than Layer 3 · 为什么二层比三层更容易出问题

Switches treat **unknown destination MACs** (multicast MACs included) as broadcast and **flood** them. So a 5 Mbps multicast stream on a 500-port access network can be replicated to 500 ports — **total bandwidth = 5 Mbps × 500 = 2.5 Gbps**.

<div class="zh" markdown="1">

交换机默认把**未知目的 MAC**（包括组播 MAC）当广播**泛洪**。所以一个 5 Mbps 的组播流，在一个 500 端口的接入层网络上，可能被复制到 500 个端口 —— **总带宽 = 5 Mbps × 500 = 2.5 Gbps**。

</div>

| Technology | Description | Status |
|------|------|------|
| **CGMP (Cisco Group Management Protocol)** | switch and router cooperate; the router tells the switch who joined which group | **obsolete**, no longer used |
| **IGMP Snooping** | the switch **snoops** IGMP messages and builds a "port → group" table dynamically | **standard practice**, mandatory |
| **PIM Snooping** | the switch snoops PIM Hello/Join and forwards multicast only to ports with PIM neighbours | common in shared VLANs / aggregation layers |
| **MLD Snooping** | the IPv6 equivalent of IGMP Snooping | mandatory in IPv6 environments |
| **MVR (Multicast VLAN Registration)** | one multicast VLAN replicates multicast into many service VLANs | common in IPTV |

<div class="zh" markdown="1">

| 技术 | 说明 | 现状 |
|------|------|------|
| **CGMP（Cisco 组管理协议）** | 交换机与路由器联动，路由器告诉交换机谁加入了哪个组 | **已过时**，不再使用 |
| **IGMP Snooping** | 交换机**侦听** IGMP 报文，动态建立"端口 → 组"表 | **标准做法**，必配 |
| **PIM Snooping** | 交换机侦听 PIM Hello/Join，只把组播送到有 PIM 邻居的端口 | 共享 VLAN / 汇聚层常用 |
| **MLD Snooping** | IPv6 的 IGMP Snooping 等价物 | IPv6 环境必配 |
| **MVR（组播 VLAN 注册）** | 单一组播 VLAN 向多业务 VLAN 复制组播 | IPTV 场景常用 |

</div>

### The Four Key IGMP Snooping Mechanisms · IGMP Snooping 的四个关键机制

| Mechanism | Function | What happens without it |
|------|------|------------|
| **Snooping Join/Report** | adds the port to the multicast forwarding table | multicast floods the whole VLAN |
| **Snooping Leave** | after a Leave, sends a **group-specific query** to confirm membership | multicast keeps being sent after the client left (wasted bandwidth) |
| **Mrouter port** | identifies "the port with a PIM router" and forwards Joins to it | Layer 3 devices never see the Join, multicast never goes upstream |
| **Querier** | sends IGMP queries periodically to maintain group membership | **entries age out, multicast works intermittently** |

<div class="zh" markdown="1">

| 机制 | 作用 | 没有它会怎样 |
|------|------|------------|
| **侦听 Join/Report** | 把端口加入组播转发表 | 组播泛洪到全 VLAN |
| **侦听 Leave** | 收到 Leave 后发**组特定查询**确认是否还有成员 | 客户端离开后组播仍继续送（浪费带宽） |
| **Mrouter 端口** | 识别"有 PIM 路由器的端口"，把 Join 转给它 | 三层设备收不到 Join，组播不上行 |
| **Querier** | 周期性发 IGMP 查询，维持组成员关系 | **表项老化，组播时通时断** |

</div>

**How mrouter ports are learned (three ways)**:

<div class="zh" markdown="1">

**Mrouter 端口怎么来的（三种）**：

</div>

1. **Dynamic learning**: the switch hears IGMP queries or PIM Hellos on the port → marks it as mrouter
2. **Static configuration**: `ip igmp snooping vlan 100 mrouter interface Gi1/0/1`
3. **PIM Snooping**: marks the port after hearing a PIM Hello

<div class="zh" markdown="1">

1. **动态学习**：交换机听到该端口有 IGMP 查询或 PIM Hello → 自动标为 mrouter
2. **静态配置**：`ip igmp snooping vlan 100 mrouter interface Gi1/0/1`
3. **PIM Snooping**：侦听到 PIM Hello 后标记

</div>

> ⚠️ **The most common access-layer multicast fault**: **the VLAN has no Layer 3 multicast router (for example a pure Layer 2 access VLAN), so there is no Querier and the snooping entries keep ageing**. The symptom is "multicast plays, but drops every few minutes; re-opening the channel fixes it". Fix: enable `ip igmp snooping querier` on the switch (give it an SVI address in that VLAN).

<div class="zh" markdown="1">

> ⚠️ **接入层最常见的组播故障**：**VLAN 内没有三层组播路由器（比如是个纯二层接入 VLAN），于是没有 Querier，Snooping 表项不断老化**。表现为"组播能看，但每隔几分钟断一下，重新打开频道又好了"。解决：在交换机上启用 `ip igmp snooping querier`（给它一个该 VLAN 的 SVI 地址）。

</div>

### IGMP Version Comparison · IGMP 版本对比

| Feature | IGMPv1 | IGMPv2 | IGMPv3 |
|------|--------|--------|--------|
| **Joining a group** | Report (join is the report) | Report | Report (with source filtering) |
| **Leaving** | **no Leave** (timeout only) | **has Leave** | has Leave |
| **Source filtering (SSM)** | no | no | **yes** (INCLUDE / EXCLUDE modes) |
| **Querier election** | relies on **PIM DR** | **lowest IP** | **lowest IP** |
| **Default query interval** | 60 s | 125 s | 125 s |
| **Report suppression** | yes | yes | **no** |
| **Typical problem** | slow leave (3-minute timeout) | compatibility mode when mixed with v1 | automatic downgrade when mixed with v2 (source filtering lost) |

<div class="zh" markdown="1">

| 特性 | IGMPv1 | IGMPv2 | IGMPv3 |
|------|--------|--------|--------|
| **加入组** | Report（加入即报告） | Report | Report（含源过滤） |
| **离开** | **无 Leave**（靠超时） | **有 Leave** | 有 Leave |
| **源过滤（SSM）** | 否 | 否 | **是**（INCLUDE / EXCLUDE 模式） |
| **查询器选举** | 依赖 **PIM DR** | **最低 IP** | **最低 IP** |
| **默认查询间隔** | 60 s | 125 s | 125 s |
| **报告抑制（Report Suppression）** | 有 | 有 | **无** |
| **典型问题** | 离开慢（超时 3 分钟） | 与 v1 混跑时兼容模式 | 与 v2 混跑时自动降级（失去源过滤） |

</div>

**Version coexistence rules (a design point)**:

<div class="zh" markdown="1">

**版本共存规则（设计要点）**：

</div>

- Switches and routers work at the **lowest version**: one IGMPv1 host in a VLAN pushes the whole VLAN into v1 compatibility mode (no Leave)
- **IGMPv3 is a prerequisite for SSM**: without v3 there is no (S,G) join, so SSM is unavailable
- For mixed environments: **unify hosts' IGMP version** (via endpoint policy), or at least guarantee "no old v1 devices in critical multicast VLANs"

<div class="zh" markdown="1">

- 交换机/路由器会**按最低版本**工作：VLAN 里出现一个 IGMPv1 主机，整个 VLAN 进入 v1 兼容模式（失去 Leave）
- **IGMPv3 是 SSM 的前提**：没有 v3，就无法 (S,G) 加入，SSM 不可用
- 混合环境建议：**统一主机 IGMP 版本**（通过终端策略），或至少保证"关键组播 VLAN 内没有 v1 老设备"

</div>

**Knock-on effects of report suppression**: IGMPv1/v2 hosts suppress other hosts' reports for the same group. If the switch relies on reports to build its table, suppression means **some ports never enter the multicast table** → those hosts receive nothing. Common counters:
- Enable **IGMP Snooping Querier** on the switch (it actively queries, so every host must answer)
- Or disable report suppression on the hosts (configurable on some operating systems)

<div class="zh" markdown="1">

**报告抑制的连带影响**：IGMPv1/v2 主机会抑制同组其他主机的 Report。如果交换机依赖 Report 建表，抑制会导致**部分端口没有被加入组播表** → 这些主机收不到组播。常见对策：
- 交换机侧开启 **IGMP Snooping Querier**（主动发查询，让每台主机都必须应答）
- 或关闭主机侧的报告抑制（部分操作系统可配）

</div>

### PIM Snooping vs IGMP Snooping

| Dimension | IGMP Snooping | PIM Snooping |
|------|--------------|--------------|
| **What it snoops** | hosts' IGMP messages | routers' PIM Hello/Join/Prune |
| **Problem it solves** | host-side flooding | **when several routers share one VLAN, send multicast only to the routers that need it** |
| **Typical scenario** | access layer | aggregation layer / data centre (dense PIM neighbours) |
| **Prerequisite** | needs a Querier | needs switch support (platform dependent) |

<div class="zh" markdown="1">

| 维度 | IGMP Snooping | PIM Snooping |
|------|--------------|--------------|
| **侦听对象** | 主机的 IGMP 报文 | 路由器的 PIM Hello/Join/Prune |
| **解决问题** | 主机侧泛洪 | **多台路由器共享同一 VLAN 时，只给需要的路由器送组播** |
| **典型场景** | 接入层 | 汇聚层/数据中心（PIM 密集邻居） |
| **前提** | 需要 Querier | 需要交换机支持（部分平台） |

</div>

**Why the aggregation layer needs PIM Snooping**: if 10 routers are interconnected through the same Layer 2 VLAN (e.g. a data-centre underlay), without PIM Snooping a multicast packet arriving at one router is replicated to **all** router ports, wasting bandwidth and CPU for nothing.

<div class="zh" markdown="1">

**为什么汇聚层需要 PIM Snooping**：如果 10 台路由器通过同一个二层 VLAN 互联（如数据中心 underlay），没有 PIM Snooping 时，一台路由器收到的组播会被复制到**所有**路由器端口，白白消耗带宽与 CPU。

</div>

### MVR (Multicast VLAN Registration)

**The problem**: in IPTV, the multicast source is in **VLAN 100** while users are spread across **VLAN 200/300/400**. The traditional answer is to configure PIM in every VLAN — an explosion of configuration.

<div class="zh" markdown="1">

**问题**：IPTV 场景里，组播源在 **VLAN 100**，但用户分布在 **VLAN 200/300/400**。按传统做法，需要给每个 VLAN 都配 PIM —— 配置量爆炸。

</div>

**What MVR does**: it **replicates multicast from the multicast VLAN** into the user VLANs. Users send IGMP joins inside their own VLAN and the switch translates them into subscriptions on the multicast VLAN.

<div class="zh" markdown="1">

**MVR 的做法**：让用户 VLAN 的**组播流量从组播 VLAN 复制过来**，用户在自己 VLAN 里发 IGMP 加入，交换机把它转换成对组播 VLAN 的订阅。

</div>

| Advantages | Disadvantages |
|------|------|
| one multicast VLAN serves all user VLANs | only works for **unidirectional** (receive-only) scenarios |
| simple configuration, clean separation | depends on switch features; large cross-vendor differences |

<div class="zh" markdown="1">

| 优点 | 缺点 |
|------|------|
| 一个组播 VLAN 服务所有用户 VLAN | 只适用于**单向**（用户只收）场景 |
| 配置简单、隔离清晰 | 依赖交换机特性，跨厂商差异大 |

</div>

### IGMP Message Formats and Timers (the foundation of troubleshooting) · IGMP 报文格式与定时器（排障的地基）

**Four message types**:

<div class="zh" markdown="1">

**四种报文**：

</div>

| Type | Code | Sender | Destination | Purpose |
|------|------|--------|---------|------|
| **Membership Query** | 0x11 | Querier (router or switch) | 224.0.0.1 (general) / group address (group-specific, group-and-source-specific) | asks "who is still there" |
| **v1 Membership Report** | 0x12 | host | group address | join (v1, no Leave) |
| **v2 Membership Report** | 0x16 | host | group address | join / answer a query |
| **Leave Group** | 0x17 | host | 224.0.0.2 (All Routers) | leave |
| **v3 Membership Report** | 0x22 | host | 224.0.0.22 | join (with source filtering) |

<div class="zh" markdown="1">

| 类型 | 代码 | 发送方 | 目的地址 | 作用 |
|------|------|--------|---------|------|
| **Membership Query** | 0x11 | Querier（路由器或交换机） | 224.0.0.1（通用）/ 组地址（组特定/组源特定） | 询问"谁还在" |
| **v1 Membership Report** | 0x12 | 主机 | 组地址 | 加入（v1，无 Leave） |
| **v2 Membership Report** | 0x16 | 主机 | 组地址 | 加入/响应查询 |
| **Leave Group** | 0x17 | 主机 | 224.0.0.2（All Routers） | 离开 |
| **v3 Membership Report** | 0x22 | 主机 | 224.0.0.22 | 加入（含源过滤） |

</div>

**IGMPv2's three query types (must be distinguished)**:

<div class="zh" markdown="1">

**IGMPv2 的三种查询（必须区分）**：

</div>

| Query type | Group address field | Purpose | Who answers |
|---------|-----------|------|--------|
| **General query** | 0.0.0.0 | periodic maintenance of all groups | every host with membership |
| **Group-specific query** | the specific group address | **after a Leave, confirm whether anyone is still there** | hosts in that group |
| **Group-and-source-specific query** (v3 only) | group + source list | used for SSM and source filtering | matching hosts |

<div class="zh" markdown="1">

| 查询类型 | 组地址字段 | 用途 | 响应者 |
|---------|-----------|------|--------|
| **通用查询**（General） | 0.0.0.0 | 周期维护所有组 | 所有有成员的主机 |
| **组特定查询**（Group-Specific） | 具体组地址 | **收到 Leave 后确认是否还有人** | 该组的主机 |
| **组源特定查询**（Group-and-Source-Specific，仅 v3） | 组 + 源列表 | 用于 SSM 与源过滤 | 匹配的主机 |

</div>

**Timer table (defaults you must know to design)**:

<div class="zh" markdown="1">

**定时器表（默认值，设计时必须知道）**：

</div>

| Parameter | Default | Purpose | Effect of tuning |
|------|-------|------|---------|
| **General query interval** | 125 s | periodic confirmation of membership | shorter → faster discovery, more overhead |
| **Max response time** | 10 s (v2/v3) | hosts answer after a random delay, avoiding bursts | smaller → faster leave, more bursts |
| **Other Querier Present timeout** | 125 s × 2 + 10 s = **260 s** | how long without hearing another Querier before taking the role | determines Querier failover time |
| **Group membership timeout** | 260 s (v2) | how long without a report before deleting the group | **must be > 3.5 × query interval** |
| **Startup query count** | 2 (at 31 s, 62 s) | build the membership table quickly at boot | — |
| **v1 router present timeout** | 400 s | the degradation window for v1 compatibility | determines how long v1 compatibility lasts |
| **Last Member Query Interval** | 1 s | interval of group-specific queries after a Leave | smaller → faster leave but risks evicting members |
| **Last Member Query Count** | 2 | how many group-specific queries after a Leave | with the interval, sets the leave delay (2 s by default) |

<div class="zh" markdown="1">

| 参数 | 默认值 | 作用 | 调优影响 |
|------|-------|------|---------|
| **通用查询间隔** | 125 s | 周期性确认组成员 | 缩短 → 成员发现更快、开销更大 |
| **最大响应时间（Max Resp）** | 10 s（v2/v3） | 主机随机延迟响应，避免同时上报 | 减小 → 离开更快、突发更多 |
| **其他查询者超时（Other Querier Present）** | 125 s × 2 + 10 s = **260 s** | 多久没听到别的 Querier 就自己当 | 决定 Querier 切换时延 |
| **组超时（Group Membership Timeout）** | 260 s（v2） | 多久没报告就删除组 | **必须 > 3.5 × 查询间隔** |
| **启动查询次数** | 2（间隔 31 s、62 s） | 启动时快速建立成员表 | — |
| **v1 路由器存在超时** | 400 s | 兼容 v1 的退化窗口 | 决定 v1 兼容模式维持多久 |
| **Last Member Query Interval** | 1 s | Leave 后组特定查询间隔 | 减小 → 离开更快但可能误踢 |
| **Last Member Query Count** | 2 | Leave 后发几次组特定查询 | 与间隔共同决定离开时延（默认 2 s） |

</div>

> 💡 **A derivation you can put straight into the design**: with default parameters, **"host stops watching" to "network stops sending" takes up to 260 s** (when no explicit Leave is sent). If the business complains that "bandwidth is still consumed after the player was closed", the answer is not "the network is broken" but "this is IGMP default behaviour". There are only two ways to speed it up: **make the application send a Leave** (most players do) or **shorten the timers** (a network-wide risk).

<div class="zh" markdown="1">

> 💡 **一个可直接用于设计的推导**：默认参数下，**从"主机停止收流"到"网络停止送流"最长需要 260 s**（不显式 Leave 时）。如果业务方抱怨"关了播放器还在耗带宽"，答案不是"网络有问题"，而是"IGMP 默认行为如此"。要加快只有两条路：**让应用发 Leave**（绝大多数播放器会发）或**缩短定时器**（有全网风险）。

</div>

**IGMPv3 source-filtering modes (the core of SSM)**:

<div class="zh" markdown="1">

**IGMPv3 的源过滤模式（SSM 的核心）**：

</div>

| Mode | Meaning | What the host expresses | Network behaviour |
|------|------|---------|------|
| **INCLUDE** | receive only the listed sources | "G, sources {S1,S2}" | build trees only to S1 and S2, reject all other sources |
| **EXCLUDE** | receive all sources except those listed | "G, everything except {S3}" | build trees to all sources except S3 (ASM semantics, requires an RP) |
| **CHANGE_TO_INCLUDE / EXCLUDE** | state transition | incremental update | triggers the corresponding Join/Prune |
| **ALLOW / BLOCK (legacy notation)** | allow/block one source in the list | — | converted internally to INCLUDE/EXCLUDE |

<div class="zh" markdown="1">

| 模式 | 含义 | 主机表达 | 网络行为 |
|------|------|---------|---------|
| **INCLUDE** | 只接收列出的源 | "G，源 {S1,S2}" | 只对 S1、S2 建树，其他源一律拒绝 |
| **EXCLUDE** | 接收除列出的源之外的所有源 | "G，除 {S3} 都收" | 对除 S3 的源建树（ASM 语义，需要 RP） |
| **CHANGE_TO_INCLUDE / EXCLUDE** | 状态切换 | 增量更新 | 触发对应的 Join/Prune |
| **ALLOW / BLOCK（旧写法）** | 源列表中某源允许/阻止 | — | 内部转换为 INCLUDE/EXCLUDE |

</div>

**The key point: INCLUDE mode is a built-in source whitelist.** That is the fundamental reason SSM is more secure than ASM — even if a malicious host can send to that group, **unless it is in the INCLUDE list it is never forwarded to receivers**.

<div class="zh" markdown="1">

**关键点：INCLUDE 模式 = 天然的"源白名单"**。这是 SSM 安全性优于 ASM 的根本原因 —— 一个恶意主机即使能发组播到该组，**只要它不在 INCLUDE 列表里，就不会被转发给接收者**。

</div>

### Implementation Differences in IGMP Snooping (always check across vendors) · IGMP Snooping 的实现差异（跨厂商必查）

IGMP Snooping is **standard behaviour but not a standard implementation**; platform differences are large enough to produce "same configuration, different behaviour":

<div class="zh" markdown="1">

IGMP Snooping 是**标准行为但非标准实现**，各平台的细节差异足以造成"相同配置、不同现象"：

</div>

| Dimension | Implementation A | Implementation B | Design impact |
|------|-----------|-----------|---------|
| **Unknown multicast (no Join)** | flood to the VLAN | drop | flooding is safer (compatibility), dropping saves bandwidth |
| **IGMPv3 support** | full parsing (with source filtering) | treated as v2 (sources ignored) | **when handled as v2, SSM source filtering is lost at Layer 2** → traffic from other sources sharing the MAC is still forwarded |
| **Querier** | off by default, needs explicit enabling | follows/enables by default | "off by default" is the root of "breaks every few minutes" |
| **Report suppression** | proxied and suppressed by the switch | not suppressed | not suppressing → more report frames, but a more accurate snooping table |
| **Behaviour with no Querier** | entries age out and are removed | falls back to flooding | the former "breaks", the latter "floods the link full" |
| **mrouter learning** | snoops Query/PIM Hello/data | needs static configuration | some platforms only honour PIM Hellos |
| **Fast Leave** | supported | unsupported on some platforms | affects channel zap speed |
| **Per-port group limit** | supported | unsupported on some platforms | affects DoS protection |

<div class="zh" markdown="1">

| 维度 | 常见实现 A | 常见实现 B | 设计影响 |
|------|-----------|-----------|---------|
| **未知名组播（无 Join）** | 泛洪到 VLAN | 丢弃 | 泛洪更安全（兼容性），丢弃更省带宽 |
| **IGMPv3 支持** | 完整解析（含源过滤） | 只当 v2 处理（忽略源） | **只按 v2 处理时，SSM 的源过滤在二层失效** → 同 MAC 其他源流量仍被转发 |
| **查询器（Querier）** | 默认关闭，需显式启用 | 默认跟随/启用 | 默认关闭是"每隔几分钟断"的根源 |
| **报告抑制（Report Suppression）** | 交换机代理抑制 | 不抑制 | 不抑制 → 更多报告帧，但 Snoping 表更准 |
| **无 Querier 时的行为** | 表项老化后删除 | 转为泛洪 | 前者"断"，后者"泛洪打满" |
| **mrouter 学习** | 侦听 Query/PIM Hello/组播数据 | 需静态配置 | 部分平台只认 PIM Hello |
| **快速离开（Fast Leave）** | 支持 | 部分平台不支持 | 影响频道切换速度 |
| **每端口组数限制** | 支持 | 部分不支持 | 影响 DoS 防护 |

</div>

**Three recommendations for multi-vendor designs**:

<div class="zh" markdown="1">

**跨厂商设计的三条建议**：

</div>

1. **Do not rely on "unknown multicast is flooded"** (some platforms drop it, some flood) → **configure critical groups statically** (`ip igmp snooping vlan 100 static 239.10.1.1 interface Gi1/0/10`)
2. **Do not assume v3 source filtering works at Layer 2** → in SSM scenarios **the address plan must still avoid MAC collisions** (security cannot rest on Layer 2 alone)
3. **Acceptance must verify Querier/mrouter/Fast Leave behaviour on every platform**, and record it in the low-level design (LLD)

<div class="zh" markdown="1">

1. **不要依赖"未知名组播泛洪"**（有平台丢、有平台泛洪）→ **静态配置关键组**（`ip igmp snooping vlan 100 static 239.10.1.1 interface Gi1/0/10`）
2. **不要假设 v3 源过滤在二层生效** → SSM 场景下**地址规划仍要避免 MAC 冲突**（安全不能只靠二层）
3. **验收必须逐平台验证 Querier/mrouter/Fast Leave 三个行为**，写进低层设计（LLD）

</div>

### Hardening IGMP Snooping (mandatory in production) · IGMP Snooping 的安全加固（生产必须）

Multicast has a larger Layer 2 attack surface than unicast because **IGMP has no authentication**:

<div class="zh" markdown="1">

组播的二层攻击面比单播更大，因为 **IGMP 是无认证的**：

</div>

| Attack | Method | Consequence | Protection |
|------|------|------|------|
| **IGMP table exhaustion** | one host sends reports for thousands of groups | snooping table full → new groups cannot be built / flooding | **per-port group limit** + per-port rate limiting |
| **Querier spoofing** | a host sends IGMP Queries (low IP) | steals the Querier role → group table refreshed wrongly | explicit `ip igmp snooping querier` + ingress ACL blocking Query (224.0.0.1) |
| **Mrouter spoofing** | a host sends PIM Hello / IGMP Query | marked as mrouter → **the whole VLAN's multicast rushes to that port** | ingress ACL blocking 224.0.0.13 and PIM (protocol 103); static mrouter |
| **IGMP report flooding** | high-rate reports | high CPU, control-plane churn | per-port IGMP rate limiting (`ip igmp snooping vlan X limit` + `ip igmp limit`) |
| **Group scanning (listening attack)** | joining many groups to probe services | information disclosure | multicast boundaries + group whitelists + monitoring for unexpected groups |

<div class="zh" markdown="1">

| 攻击 | 手法 | 后果 | 防护 |
|------|------|------|------|
| **IGMP 组表耗尽** | 一台主机发上千个不同组的 Report | Snooping 表满 → 新组无法建立 / 泛洪 | **每端口组数限制**（limit）+ 每端口速率限制 |
| **伪造 Querier** | 主机发 IGMP Query（低 IP） | 抢走 Querier → 组表被错误刷新 | `ip igmp snooping querier` 显式指定 + 接入口 ACL 拦 Query（224.0.0.1） |
| **伪造 Mrouter** | 主机发 PIM Hello / IGMP Query | 被标为 mrouter → **全 VLAN 组播冲向该端口** | 接入口 ACL 拦 224.0.0.13、PIM（协议 103）；静态 mrouter |
| **IGMP Report 洪泛** | 高速发 Report | CPU 高、控制面抖动 | 每端口 IGMP 报文速率限制（`ip igmp snooping vlan X limit` + `ip igmp limit`） |
| **组地址扫描（Listening attack）** | 加入大量组探测业务 | 信息泄露 | 组播边界 + 组白名单 + 监控异常组 |

</div>

```cfg
! Anti-spoofing on access ports (Cisco syntax, ingress ACL blocking control protocols)
ip access-list extended EDGE-IN
 deny   pim any any                       ! block PIM (protocol 103)
 deny   igmp any 224.0.0.1               ! block forged Query
 deny   igmp any 224.0.0.13              ! block the PIM Hello group
 permit ip any any
interface range Gi1/0/1 - 48
 ip access-group EDGE-IN in
 ip igmp limit 20                        ! at most 20 groups per port
```

<div class="zh" markdown="1">

```cfg
! 接入口防伪造（Cisco 语法，接口 ACL 拦控制协议）
ip access-list extended EDGE-IN
 deny   pim any any                       ! 拦 PIM（协议 103）
 deny   igmp any 224.0.0.1               ! 拦伪造 Query
 deny   igmp any 224.0.0.13              ! 拦 PIM Hello 组
 permit ip any any
interface range Gi1/0/1 - 48
 ip access-group EDGE-IN in
 ip igmp limit 20                        ! 每端口最多 20 个组
```

</div>

> ⚠️ **A side effect of setting `ip igmp limit` too low**: a PC driving a monitoring wall may subscribe to 16–24 streams at once. With a limit of 20, some subscriptions are randomly dropped, showing up as "some screens never appear". **The limit must be computed from the application profile, never guessed.**

<div class="zh" markdown="1">

> ⚠️ **`ip igmp limit` 设太小的副作用**：一台运行监控墙的 PC 可能同时订阅 16–24 路？如果 limit 设 20，会随机丢一部分订阅，表现为"有些画面出不来"。**限值要按业务画像算，不能拍脑袋。**

</div>

### Aggregation Layer: PIM Snooping and "Router-Dense Segments" · 汇聚层：PIM Snooping 与 "路由器密集网段"

**Scenario**: 10–20 routers (all running PIM) sit in the **aggregation Layer 2 domain** of a data centre or large campus. Without PIM Snooping:

<div class="zh" markdown="1">

**场景**：数据中心、大型园区的**汇聚层二层域**里有 10–20 台路由器（都跑 PIM）。没有 PIM Snooping 时：

</div>

```
multicast packet reaches the switch -> flooded to all 20 router ports
-> 19 routers fail their RPF check and drop it (20x wasted bandwidth + CPU on 19 devices)
```

<div class="zh" markdown="1">

```
组播包到达交换机 → 泛洪到所有 20 个路由器端口
→ 其中 19 台路由器做 RPF 检查后丢弃（浪费 20 倍带宽 + 19 台设备的 CPU）
```

</div>

**What PIM Snooping does**: the switch snoops PIM Hello/Join/Prune and **forwards only to ports that have sent a Join**.

<div class="zh" markdown="1">

**PIM Snooping 的做法**：交换机侦听 PIM Hello/Join/Prune，**只在有 Join 的端口转发**。

</div>

| Configuration item | Description |
|--------|------|
| Global enable | `ip pim snooping` (on some platforms `ip igmp snooping vlan X mrouter ...`) |
| Which VLANs | normally only "multi-router VLANs"; not needed on access ports |
| Coexistence with IGMP Snooping | complementary: IGMP handles the host side, PIM handles the router side |
| **DR awareness** | the switch should know who was elected DR and send only to it (some platforms are unaware and still send to all) |

<div class="zh" markdown="1">

| 配置项 | 说明 |
|--------|------|
| 全局启用 | `ip pim snooping`（部分平台 `ip igmp snooping vlan X mrouter ...`） |
| 指定 VLAN | 通常只在"多路由器 VLAN"启用，接入口不需要 |
| 与 IGMP Snooping 共存 | 两者互补：IGMP 管主机侧，PIM 管路由器侧 |
| **DR 感知** | 交换机要知道谁被选为 DR，只往 DR 送（部分平台不感知，仍会送全） |

</div>

> 💡 **An alternative**: **do not put that many routers in one Layer 2 domain**. Replace the shared VLAN with point-to-point Layer 3 links and the PIM adjacency becomes "one per link", eliminating flooding by construction. This is the classic case of "killing a feature requirement with design" — rather than tuning PIM Snooping, change the topology.

<div class="zh" markdown="1">

> 💡 **一个替代做法**：**不要让那么多路由器在同一个二层域里**。用点到点三层链路代替共享 VLAN，PIM 邻居关系就变成"每条链路一个"，天然没有泛洪问题。这是"用设计消灭功能需求"的典型例子 —— 与其调 PIM Snooping，不如改拓扑。

</div>

### Complete MVR Design and Configuration Example · MVR 完整设计与配置示例

**Scenario**: IPTV with the source in VLAN 100 (the multicast VLAN) and users in VLAN 200–400.

<div class="zh" markdown="1">

**场景**：IPTV，源在 VLAN 100（组播 VLAN），用户分布在 VLAN 200–400。

</div>

```cfg
! multicast VLAN (source side)
vlan 100
 name MCAST-SOURCE
interface Vlan100
 ip address 10.100.0.1 255.255.255.0
 ip pim sparse-mode
 ip igmp helper-address ...        ! platform dependent

! user VLAN
vlan 200
 name IPTV-USERS-A
interface Vlan200
 ip address 10.200.0.1 255.255.255.0
 ! user VLANs do not need PIM (MVR replicates multicast down from VLAN 100)

! MVR configuration
mvr
 mvr group 239.10.0.0 24            ! group range carried by MVR (/24 = 256 groups)
 mvr vlan 100                       ! the multicast VLAN
 mvr querytime 5
 mvr mode compatible                ! compatibility mode (some platforms)
interface Vlan100
 mvr                            ! source-side interface
interface Vlan200
 mvr                            ! user-side interface (can be many)
```

<div class="zh" markdown="1">

```cfg
! 组播 VLAN（源侧）
vlan 100
 name MCAST-SOURCE
interface Vlan100
 ip address 10.100.0.1 255.255.255.0
 ip pim sparse-mode
 ip igmp helper-address ...        ! 视平台

! 用户 VLAN
vlan 200
 name IPTV-USERS-A
interface Vlan200
 ip address 10.200.0.1 255.255.255.0
 ! 用户 VLAN 不需要 PIM（组播由 MVR 从 VLAN 100 复制下来）

! MVR 配置
mvr
 mvr group 239.10.0.0 24            ! 允许 MVR 承载的组范围（/24 = 256 个组）
 mvr vlan 100                       ! 组播 VLAN
 mvr querytime 5
 mvr mode compatible                ! 兼容模式（部分平台）
interface Vlan100
 mvr                            ! 源侧接口
interface Vlan200
 mvr                            ! 用户侧接口（可多个）
```

</div>

**MVR design constraints (the potholes people fall into)**:

<div class="zh" markdown="1">

**MVR 的设计约束（踩过的坑）**：

</div>

| Constraint | Description | Consequence |
|------|------|------|
| **Unidirectional** | the user side can only receive, not send (default) | if users need to send (e.g. CCTV backhaul) another mechanism is required |
| **Limited group range** | `mvr group` must be declared explicitly per range | forgetting a new group → new channels are black |
| **VLAN count limit** | each switch supports a limited number of MVR VLANs | beyond it you need a layered design |
| **Cross-switch limits** | the multicast VLAN must extend to wherever it is needed | crossing aggregation requires MVR plus Layer 2 extension |
| **Interaction with IGMP Snooping** | MVR user VLANs still need snooping (signalling) | MVR without snooping → some ports get nothing |
| **Accounting and rate limiting** | MVR traffic is hard to rate-limit per user on the user VLAN side | no per-user bandwidth control |

<div class="zh" markdown="1">

| 约束 | 说明 | 后果 |
|------|------|------|
| **单向** | 用户侧只能收，不能发（默认） | 用户想"发"（如监控回传）必须用别的机制 |
| **组范围有限** | `mvr group` 需要逐段声明 | 忘记声明新组 → 新频道全黑 |
| **VLAN 数量限制** | 每台交换机可承载的 MVR VLAN 有限 | 超限需分层设计 |
| **跨交换机限制** | 组播 VLAN 必须延伸到能承载的位置 | 跨汇聚时需 MVR + 二层延伸 |
| **组地址与 IGMP Snooping 的交互** | MVR 用户 VLAN 里仍需 Snooping（信令） | 只配 MVR 不配 Snooping → 部分端口收不到 |
| **统计与限速** | MVR 流量在用户 VLAN 侧不易按用户限速 | 无法做"每用户带宽控制" |

</div>

> ⚠️ **The most common MVR go-live failure**: **after a new channel is added, old channels work and new ones are black**. The cause is almost always that the range declared in `mvr group` does not cover the new group. **That is the inevitable price of a configuration-based whitelist** — where there is a whitelist there is a risk of forgetting to add to it, so "new multicast address → update the `mvr group` declaration" must be written into the change process.

<div class="zh" markdown="1">

> ⚠️ **MVR 最常见的上线失败**：**新频道上线后"老频道正常、新频道全黑"**。原因几乎总是 `mvr group` 声明的范围没覆盖新组。**这是"配置式白名单"的必然代价** —— 有白名单就有"漏加"的风险，所以必须把"新增组播地址 → 同步更新 mvr group 声明"写进变更流程。

</div>

---

## Layer 3 Multicast Routing · 三层组播路由

### RPF (Reverse Path Forwarding): the only criterion for multicast forwarding · RPF（反向路径转发）：组播转发的唯一判据

> RPF is the core concept of multicast routing. On receiving a multicast packet, the router **checks the source address** — it forwards only if the incoming interface is the "optimal path interface toward the source", otherwise it **drops the packet silently**.

<div class="zh" markdown="1">

> RPF 是组播路由的核心概念。路由器收到组播包后，**检查源地址** —— 只有当入接口是"到达源地址的最优路径接口"时，才转发该包；否则**静默丢弃**。

</div>

```
        unicast routing table (toward source 10.1.1.1 via Gi0/1)
                    ↓
source 10.1.1.1 → R1 ──Gi0/1──→ R2 ──→ receivers
                              │
                    RPF check: incoming interface == Gi0/1 ?
                    ├─ yes → forward and create (S,G) state
                    └─ no  → drop (RPF Failure)
```

<div class="zh" markdown="1">

```
        单播路由表（到源 10.1.1.1 走 Gi0/1）
                    ↓
源 10.1.1.1 → R1 ──Gi0/1──→ R2 ──→ 接收者
                              │
                    RPF 检查：包的入接口 == Gi0/1 ?
                    ├─ 是 → 转发，并建立 (S,G) 状态
                    └─ 否 → 丢弃（RPF Failure）
```

</div>

**Three key facts about RPF**:

<div class="zh" markdown="1">

**RPF 的三个关键事实**：

</div>

| Fact | Meaning |
|------|------|
| **RPF uses the unicast routing table** | change unicast routing and the multicast tree follows; unicast/multicast path mismatch = multicast broken |
| **RPF failures are silent** | no ICMP error, no log (only `debug`/mroute counters); the symptom is "the source is sending, nothing arrives" |
| **RPF is checked on ingress** | egress is decided by the multicast routing table (mroute)/OIL, the opposite of unicast |

<div class="zh" markdown="1">

| 事实 | 含义 |
|------|------|
| **RPF 用的是单播路由表** | 单播路由一变，组播树跟着变；单播/组播路径不一致 = 组播断 |
| **RPF 失败是静默的** | 没有 ICMP 错误、没有日志（除 `debug`/`mroute` 计数），表现为"源在发，收不到" |
| **RPF 检查在入方向** | 出口由组播路由表（mroute）/出接口列表决定，与单播相反 |

</div>

#### The four sources of the RPF check (highest priority first) · RPF 检查的四种来源（优先级从高到低）

| Source | Command | Purpose |
|------|------|------|
| **Static mroute** | `ip mroute 10.1.1.1 255.255.255.255 Gi0/1` | override the unicast path (the most common emergency tool) |
| **MBGP (multicast BGP, SAFI 2)** | `address-family ipv4 multicast` | provides a **separate RPF table** for multicast (common across domains) |
| **Multitopology routing (MTR)** | a separate topology | complete separation of multicast and unicast (complex, rarely used) |
| **Unicast RIB** | `show ip route` | the default source |

<div class="zh" markdown="1">

| 来源 | 命令 | 用途 |
|------|------|------|
| **静态 mroute** | `ip mroute 10.1.1.1 255.255.255.255 Gi0/1` | 覆盖单播路径（最常用的应急手段） |
| **MBGP（组播 BGP，SAFI 2）** | `address-family ipv4 multicast` | 为组播提供**独立的 RPF 表**（跨域常用） |
| **多拓扑路由（MTR）** | 独立拓扑 | 组播与单播完全分离（复杂、少用） |
| **单播 RIB** | `show ip route` | 默认来源 |

</div>

#### The three typical causes of RPF failure · RPF 失败的三种典型原因

| Cause | Symptom | Fix |
|------|------|------|
| **Asymmetric unicast/multicast paths** | unicast goes over link A, the multicast packet arrives on link B | correct the IGP metric / use a static mroute / use MBGP |
| **ECMP multipath** | multicast receives on only one path; packets on the other are dropped | enable multicast multipath (`ip multicast multipath`), or collapse to a single path |
| **iBGP next-hop problem** | RPF uses a BGP route whose next hop is unreachable (same as Chapter 8) | `next-hop-self` / static mroute |

<div class="zh" markdown="1">

| 原因 | 现象 | 修复 |
|------|------|------|
| **单播与组播路径不对称** | 单播走 A 链路，组播包从 B 链路进来 | 修正 IGP 度量 / 用静态 mroute / 用 MBGP |
| **ECMP 多路径** | 组播只从一条路径收，另一条路径的包被丢 | 开启组播多路径（如 `ip multicast multipath`），或收敛为单路径 |
| **iBGP 下一跳问题** | RPF 用 BGP 路由但下一跳不可达（与第 8 章同理） | `next-hop-self` / 静态 mroute |

</div>

> 💡 **The three-command troubleshooting drill**: `show ip rpf <source>` → see the RPF interface; `show ip mroute <group>` → see the incoming/outgoing interfaces and flags; `show ip mroute count` → check for an "RPF failed" counter. **If the (S,G) is not in the mroute at all, check RPF first; if it exists but has no outgoing interfaces, check whether the downstream sent a Join.**

<div class="zh" markdown="1">

> 💡 **排障三连**：`show ip rpf <源>` → 看 RPF 接口；`show ip mroute <组>` → 看入接口/出接口与标志位；`show ip mroute count` → 看是否有 "RPF failed" 计数。**如果 mroute 里根本没有这条 (S,G)，先查 RPF；如果有了但没出接口，查下游是否有 Join。**

</div>

#### RPF in depth: five tables, four sources, three priority traps · RPF 深入：五张表、四种来源、三个优先级陷阱

A router's RPF check does not "look at one routing table"; it consults **a prioritised stack of RPF sources**:

<div class="zh" markdown="1">

路由器的 RPF 检查并不是"只查一张路由表"，而是查**一个有优先级的 RPF 来源栈**：

</div>

| Priority | Source | Configuration/origin | Typical use | Danger |
|-------|------|----------|---------|--------|
| **1 (highest)** | **static mroute** | `ip mroute <source> <mask> <interface/next-hop>` | emergency bypass of the unicast path | **a legacy leftover causes permanent RPF failure**, silently |
| **2** | **MBGP (SAFI 2)** | `address-family ipv4 multicast` | multicast over a separate exit | two BGP policy sets to maintain |
| **3** | **MTR (multitopology)** | topology + `ip pim` binding | full separation of multicast and unicast | complex; IGP must support per-topology neighbours/metrics |
| **4** | **unicast RIB** | IGP/BGP/static | default | unicast changes affect multicast directly |
| **5** | **default route** | 0.0.0.0/0 | fallback | **if the source only matches the default route, RPF may point out of the wrong interface** |

<div class="zh" markdown="1">

| 优先级 | 来源 | 配置/来源 | 典型用途 | 危险点 |
|-------|------|----------|---------|--------|
| **1（最高）** | **静态 mroute** | `ip mroute <源> <掩码> <接口/下一跳>` | 应急绕过单播路径 | **历史遗留会导致永久 RPF 失败**，且无日志 |
| **2** | **MBGP（SAFI 2）** | `address-family ipv4 multicast` | 组播走独立出口 | 需要同时维护两套 BGP 策略 |
| **3** | **MTR（多拓扑）** | topology + `ip pim` 绑定 | 组播与单播完全分离 | 复杂、IGP 要为多拓扑做邻居/度量 |
| **4** | **单播 RIB** | IGP/BGP/静态 | 默认 | 单播变化直接影响组播 |
| **5** | **默认路由** | 0.0.0.0/0 | 兜底 | **如果源只匹配默认路由，RPF 可能指向错误出口** |

</div>

**Reading `show ip rpf` output (you must be able to)**:

<div class="zh" markdown="1">

**`show ip rpf` 的输出解读（必须会看）**：

</div>

```
R1# show ip rpf 10.1.1.1
RPF information for 10.1.1.1
  RPF interface: GigabitEthernet0/1
  RPF neighbor: 10.0.0.2
  RPF route/mask: 10.1.1.0/24
  RPF type: unicast (ospf 1)          <- key: the source type
  Doing distance-preferred lookups across tables   <- MBGP / multiple tables are in use
  RPF topology: ipv4 multicast        <- MTR is in use
```

<div class="zh" markdown="1">

```
R1# show ip rpf 10.1.1.1
RPF information for 10.1.1.1
  RPF interface: GigabitEthernet0/1
  RPF neighbor: 10.0.0.2
  RPF route/mask: 10.1.1.0/24
  RPF type: unicast (ospf 1)          ← 关键：来源类型
  Doing distance-preferred lookups across tables   ← 说明启用了 MBGP / 多表
  RPF topology: ipv4 multicast        ← 说明用了 MTR
```

</div>

| Field | Meaning | Anomaly criterion |
|------|------|---------|
| `RPF interface` | the expected ingress interface | differs from the captured ingress → RPF failure |
| `RPF neighbor` | the expected upstream | differs from `show ip pim neighbor` → Join cannot go upstream |
| `RPF route/mask` | the matched route prefix | **more specific or broader than expected can both be a problem** |
| `RPF type` | unicast / static / mbgp / mtrie | **`static` deserves extra suspicion** (possibly a leftover) |
| `Doing distance-preferred lookups` | whether multi-table lookup is enabled | must match the design |

<div class="zh" markdown="1">

| 字段 | 含义 | 异常判据 |
|------|------|---------|
| `RPF interface` | 期望的入接口 | 与实际抓包入接口不一致 → RPF 失败 |
| `RPF neighbor` | 期望的上游 | 与 `show ip pim neighbor` 不一致 → Join 发不上去 |
| `RPF route/mask` | 匹配到的路由前缀 | **比预期更具体或更宽泛都可能是问题** |
| `RPF type` | unicast / static / mbgp / mtrie | **`static` 要特别警惕**（可能是遗留） |
| `Doing distance-preferred lookups` | 是否启用了多表查找 | 与设计是否一致 |

</div>

**Three priority traps**:

<div class="zh" markdown="1">

**三个优先级陷阱**：

</div>

1. **Static mroute beats everything**: you delete the BGP route and fix the IGP metric, and nothing changes — the static mroute is still there.
2. **A more specific static mroute overrides a broader one by distance, not by longest match**: with both `ip mroute 10.1.1.1/32` and `ip mroute 10.0.0.0/8` present, the winner is decided by administrative distance (static mroute follows the same logic as static routes), **not "longest match wins"** — the opposite of unicast, and very easy to misconfigure.
3. **`ip mroute 0.0.0.0 0.0.0.0 <interface>` is a global RPF override**: it makes **every source** use the specified interface. Someone configures it to "fix things quickly", and afterwards all multicast enters through the same interface — complete chaos in a multi-source environment.

<div class="zh" markdown="1">

1. **静态 mroute > 一切**：你删了 BGP 路由、修了 IGP 度量，都没用 —— 静态 mroute 还在。
2. **更具体的静态 mroute 会覆盖更宽的**：`ip mroute 10.1.1.1/32` 与 `ip mroute 10.0.0.0/8` 同时存在时，前者的优先级由管理距离决定（默认静态 mroute 的 AD 与静态路由相同逻辑），**不是"最长匹配优先"** —— 这一点与单播相反，极易配错。
3. **`ip mroute 0.0.0.0 0.0.0.0 <接口>` 是"全局 RPF 覆盖"**：它会让**所有源**都用指定接口做 RPF。有人为了"快速修好"配了它，结果所有组播都从同一个接口进来 → 多源环境全乱。

</div>

**Handling ECMP:**

<div class="zh" markdown="1">

**组播多路径（ECMP）的处理**：

</div>

| Scenario | Default behaviour | Correction |
|------|---------|------|
| Two equal-cost paths to the source | multicast **picks one** (hash based); packets on the other are dropped | `ip multicast multipath` (hashed per source, so different sources use different paths) |
| Two paths with different bandwidth | may still pick the worse one | widen the difference with IGP metrics, or pin it with a static mroute |
| Some paths failing, some healthy | it does switch on single path, but switchover interrupts traffic | multipath + fast convergence (BFD) |

<div class="zh" markdown="1">

| 场景 | 默认行为 | 修正 |
|------|---------|------|
| 两条等价路径到源 | 组播**只选一条**（基于 hash），另一条的包被丢弃 | `ip multicast multipath`（按源 hash，不同源走不同路径） |
| 两条路径带宽不同 | 默认仍可能选较差的一条 | 用 IGP 度量拉开差异，或用静态 mroute 固定 |
| 部分路径故障、部分正常 | 单路径时会切，但切换会中断 | 多路径 + 快速收敛（BFD） |

</div>

> ⚠️ **The real side effect of `ip multicast multipath`**: it selects paths **by hashing the source address**, so **traffic from one source still uses one path**. If that path congests, multicast does not spread the load — you need **multiple sources** to exploit multipath. Decide at design time whether you want "failover" or "load sharing"; multipath only partly delivers both.

<div class="zh" markdown="1">

> ⚠️ **`ip multicast multipath` 的真实副作用**：它**按源地址 hash**选路，所以**同一个源的流量仍只走一条路径**。如果某条路径拥塞，组播不会自动分担 —— 需要"多源"才能利用多路径。设计时要明确：你要的是"故障切换"还是"负载分担"，这两者用多路径都只能部分实现。

</div>

#### PIM messages and timers (one table to remember them) · PIM 报文与定时器（一张表记住）

| Message | Destination | Sent how | Default interval | Purpose |
|------|---------|---------|---------|------|
| **Hello** | 224.0.0.13 | multicast per interface | **30 s** (holdtime 105 s) | neighbour discovery, DR election, capability negotiation (PIM version, join suppression, GenID) |
| **Join/Prune** | 224.0.0.13 | unicast to the upstream RPF neighbour | refresh every 60 s (Join); Prune carries a 210 s timeout | build/prune trees |
| **Register** | the RP's unicast address | unicast (PIM encapsulated) | with data (suppressed) | the FHR sends source traffic to the RP |
| **Register-Stop** | the FHR's unicast address | unicast | event driven | the RP tells the FHR to stop encapsulating |
| **Assert** | 224.0.0.13 | multicast | event driven (once per 30 s, up to 3 times) | elect a single forwarder per LAN |
| **Bootstrap (BSR)** | 224.0.0.13 | hop-by-hop multicast | 60 s | distribute the RP-Set |
| **Candidate-RP-Advertisement** | unicast to the BSR | unicast | **60 s** | a C-RP announces itself to the BSR |
| **Graft / Graft-Ack** | upstream unicast / downstream multicast | — | event driven | PIM-DM fast re-attach |
| **State Refresh** | 224.0.0.13 | multicast | **60 s** (originally 3 min) | PIM-DM maintains pruned state |

<div class="zh" markdown="1">

| 报文 | 目的地址 | 发送方式 | 默认间隔 | 作用 |
|------|---------|---------|---------|------|
| **Hello** | 224.0.0.13 | 每接口组播 | **30 s**（holdtime 105 s） | 邻居发现、DR 选举、能力协商（PIM 版本、Join 抑制、GenID） |
| **Join/Prune** | 224.0.0.13 | 单播给上游 RPF 邻居（下游方向） | 60 s 刷新（Join）；Prune 带超时 210 s | 建树/剪枝 |
| **Register** | RP 单播地址 | 单播（PIM 封装） | 随数据（有抑制） | FHR 把源流量送给 RP |
| **Register-Stop** | FHR 单播 | 单播 | 触发式 | RP 通知 FHR 停止封装 |
| **Assert** | 224.0.0.13 | 组播 | 触发式（30 s 一次，最多 3 次） | 同 LAN 选唯一转发者 |
| **Bootstrap（BSR）** | 224.0.0.13 | 逐跳组播 | 60 s | 分发 RP-Set |
| **Candidate-RP-Advertisement** | BSR 单播 | 单播 | **60 s** | C-RP 向 BSR 报告自己 |
| **Graft / Graft-Ack** | 上游单播 / 下游组播 | — | 触发式 | PIM-DM 快速接回 |
| **State Refresh** | 224.0.0.13 | 组播 | **60 s**（原 3 min） | PIM-DM 维持剪枝状态 |

</div>

**What the timers mean for design**:

<div class="zh" markdown="1">

**定时器设计含义**：

</div>

```
PIM neighbour failure detection = Hello holdtime = 105 s (default)
-> i.e. if a router loses power, the multicast tree may take up to 105 s to notice

To speed it up:
 ① shorten hello-interval / holdtime (e.g. 5 s / 15 s)
    cost: more Hello messages; CPU rises with many neighbours
 ② use BFD for PIM (where supported) -> milliseconds
 ③ let IGP convergence drive it (IGP detects faster and the PIM neighbour clears as soon as the interface drops)
```

<div class="zh" markdown="1">

```
PIM 邻居故障检测 = Hello holdtime = 105 s（默认）
→ 即：一台路由器掉电，组播树最多要 105 秒才知道

要加快：
 ① 调小 hello-interval / holdtime（如 5 s / 15 s）
    代价：Hello 报文增多；大规模邻居时 CPU 上升
 ② 用 BFD for PIM（若平台支持）→ 毫秒级
 ③ 靠 IGP 收敛带动（IGP 更快发现，PIM 邻居随接口 down 立即清除）
```

</div>

> 💡 **A key design judgement**: **multicast "failure detection" is usually not the bottleneck; "tree rebuild" is**. Even with 1-second IGP convergence, PIM still has to resend Joins and rebuild state hop by hop, so end-to-end recovery is typically 2–10 seconds. For truly uninterrupted services that is not enough — you need **Live-Live** or **pre-built redundant trees**.

<div class="zh" markdown="1">

> 💡 **关键设计判断**：**组播的"故障检测"通常不是瓶颈，"树重建"才是**。即使 IGP 1 秒收敛，PIM 还要重新发 Join、逐跳建立状态，端到端恢复常在 2–10 秒。所以对"不可中断"业务，指望"快速收敛"是不够的 —— 必须 **Live-Live** 或 **预先建立的冗余树**。

</div>

#### PIM DR election (details determine behaviour) · PIM DR 选举（细节决定行为）

| Item | Rule |
|----|------|
| **Priority** | compare DR priority first (higher wins, default 1) |
| **IP comparison** | if priorities tie, compare **interface IP** (higher wins) |
| **Prerequisite** | only interfaces **with PIM neighbours** take part in DR election |
| **DR duties** | on that LAN: ① send IGMP queries (if it also wins the Querier logic) ② send Registers to the RP ③ send (*,G) Joins to the RP |
| **Non-DR duties** | **does not Join upstream** when receiving multicast (but still forwards onto the LAN, because there are downstream receivers) |
| **DR vs Assert** | DR decides "who speaks to the upstream on behalf of the LAN"; Assert decides "who puts packets onto the LAN" |

<div class="zh" markdown="1">

| 项 | 规则 |
|----|------|
| **优先级** | 先比 DR 优先级（大者胜，默认 1） |
| **IP 比较** | 优先级相同比**接口 IP**（大者胜） |
| **前提** | 只有**有 PIM 邻居**的接口才参与 DR 选举 |
| **DR 的职责** | 该 LAN 上：①发 IGMP 查询（若它也是 Querier 逻辑的赢家）②向 RP 发 Register ③向 RP 发 (*,G) Join |
| **非 DR 的职责** | 收到组播包时**不向上游 Join**（但仍会转发到 LAN 上，因为有下游在收） |
| **DR 与 Assert 的关系** | DR 只决定"谁代表 LAN 与上游对话"；Assert 决定"谁把包送到 LAN" |

</div>

**Why DR matters only in PIM-SM**:

<div class="zh" markdown="1">

**为什么 DR 只在 PIM-SM 里重要**：

</div>

- **PIM-DM**: no Register and no (*,G) Join to the RP, so DR is only used for IGMP queries
- **PIM-SSM**: no (*,G) Join to an RP, but **a DR is still needed to send the (S,G) Join toward the source on behalf of the LAN**
- **BiDir**: DR is not used; **DF** is

<div class="zh" markdown="1">

- **PIM-DM**：不需要 Register，也不需要向 RP 发 Join，所以 DR 只用于 IGMP 查询
- **PIM-SSM**：不需要 (*,G) Join 到 RP，但**仍需要 DR 代表 LAN 向源发 (S,G) Join**
- **BiDir**：不用 DR，用 **DF**

</div>

**Production configuration example (two routers sharing a VLAN)**:

<div class="zh" markdown="1">

**生产配置示例（双路由器共享 VLAN）**：

</div>

```cfg
! make the DR explicit (avoid "random election")
interface Gi0/0
 ip pim dr-priority 100        ! the host-side gateway router gets the higher priority
! the other (backup) router gets a lower one
interface Gi0/0
 ip pim dr-priority 1
```

<div class="zh" markdown="1">

```cfg
! 明确谁是 DR（避免"选举随机"）
interface Gi0/0
 ip pim dr-priority 100        ! 主机侧网关路由器设高优先级
! 另一台（备份）设低
interface Gi0/0
 ip pim dr-priority 1
```

</div>

> ⚠️ **A hidden problem with DR priority**: if you force the DR onto the "backup router" (common in "gateway on A, multicast on B" designs), then A holds no (*,G) state and **A's mroute table shows no multicast at all**. Operations then misdiagnose it as "multicast was never built". **The DR location must be documented and included in monitoring checks.**

<div class="zh" markdown="1">

> ⚠️ **DR 优先级带来的隐藏问题**：如果把 DR 强制指向"备份路由器"（常见于"网关在 A、组播在 B"的设计），那么 A 上就没有 (*,G) 状态，**A 的 mroute 表看不到组播**。运维查表时容易误判"组播没建立"。**必须把 DR 位置写进文档与监控检查项。**

</div>

#### Join/Prune encoding and Prune Override · Join/Prune 的编码与 Prune Override

A single PIM Join can carry **several (S,G)/(*,G) entries** (an encoded group address list), each with:

<div class="zh" markdown="1">

PIM Join 报文可以**一次携带多个 (S,G)/(*,G)**（encoded group address 列表），每个表项带：

</div>

| Field | Meaning | Design implication |
|------|------|---------|
| **Encoded-Group** | group address + mask | allows group ranges (used by BSR/RP) |
| **Encoded-Source** | source address + mask (source mask can express "group range") | used by SSM/BiDir |
| **S / W / R bits** | Sparse / Wildcard / RP-tree | **`W` = (*,G); `R` = this (*,G) points at the RP** |
| **Holdtime** | validity of this Join (210 s default) | must be refreshed periodically (every 60 s) |

<div class="zh" markdown="1">

| 字段 | 含义 | 设计含义 |
|------|------|---------|
| **Encoded-Group** | 组地址 + 掩码 | 支持组范围（用于 BSR/RP） |
| **Encoded-Source** | 源地址 + 掩码（可用 S 掩码表示"组范围"） | SSM/BiDir 用 |
| **S / W / R 位** | Sparse / Wildcard / RP-tree | **`W` 位 = (*,G)，`R` 位 = 该 (*,G) 指向 RP** |
| **Holdtime** | 该 Join 的有效期（默认 210 s） | 需要周期性刷新（60 s 一次） |

</div>

**Prune Override**: two downstream routers on the same LAN, A wants to Prune while B still wants the stream. The mechanism:

<div class="zh" markdown="1">

**Prune Override（剪枝否决）**：同一 LAN 上有两台下游路由器，A 想 Prune、B 还想收。机制：

</div>

```
A sends Prune →
B hears the Prune and immediately sends a Join to override it (within about 3 s)
→ upstream sees "Prune then Join" and keeps forwarding
```

<div class="zh" markdown="1">

```
A 发 Prune → 
B 听到 Prune → 立即发 Join 覆盖（Prune Override，约 3 秒内）
→ 上游看到"先 Prune 后 Join"，最终保留转发
```

</div>

**Design implication**: **a Prune is not effective immediately**; there is an "override window". So "closing a channel" may take a few seconds to actually save bandwidth. In high-churn scenarios (IPTV zapping) that window leaves upstream briefly holding the old group — harmless, but on devices **close to their state limit** it amplifies state pressure.

<div class="zh" markdown="1">

**设计含义**：**Prune 不是立即生效的**，它有"被否决窗口"。因此"关闭一个频道"可能延迟几秒才真正省带宽。在高频切换场景（IPTV 换台），这个窗口会让上游短暂维持旧组 —— 影响不大，但在**状态数接近上限**的设备上，会放大状态压力。

</div>

#### PIM Join Suppression · PIM 的"Join 抑制"

**The problem**: 10 routers on the same LAN each forward downstream and each sends a Join upstream for the same (S,G) → upstream receives 10 Joins.

<div class="zh" markdown="1">

**问题**：同一 LAN 上 10 台路由器都往下游转发，都要向上游发 Join（同一个 (S,G)）→ 上游收到 10 份 Join。

</div>

**The mechanism**: when a router hears another router on the same LAN send the same (S,G) Join (**if that router's RPF neighbour is the same as its own**), it **suppresses its own Join**. This is what the "join suppression capable" bit in Hello is for.

<div class="zh" markdown="1">

**机制**：路由器听到同 LAN 其他路由器发出同一条 (S,G) Join 后，**抑制自己的 Join**（如果对端的 RPF 邻居与自己的相同）。这是 Hello 中"Join Suppression 能力位"的作用。

</div>

| Symptom | Explanation |
|------|------|
| upstream sees only one Join | normal (suppression working) |
| upstream sees several Joins | suppression disabled, or unsupported on the platform |
| **suppression vs DR** | suppression handles "several routers sharing a LAN"; DR decides "who speaks for the LAN". **Both can apply at once** (in SM: the DR sends the (*,G) Join, suppression reduces duplicates) |

<div class="zh" markdown="1">

| 现象 | 说明 |
|------|------|
| 上游只看到一个 Join | 正常（抑制生效） |
| 上游看到多个 Join | 关闭了抑制能力，或平台不支持 |
| **抑制与 DR 的关系** | 抑制是"多台路由器共享 LAN"的场景，DR 是"谁代表 LAN 说话"，两者**可能同时生效**（在 SM 中：DR 发 (*,G) Join，Join 抑制减少重复） |

</div>

**When to disable Join suppression**: essentially never. If the upstream platform has very tight multicast table limits, suppression reduces upstream pressure — so **suppression on by default is good**; do not start by disabling it when something breaks.

<div class="zh" markdown="1">

**关闭 Join 抑制的场景**：几乎所有场景都不该关。但在"上游平台组播表项限制"很紧时，抑制能减少上游压力 —— 所以**抑制默认开启是好的**，出问题时不要先关它。

</div>

### PIM Mode Selection (the core design decision) · PIM 模式选择（设计决策的核心）

| PIM mode | Mechanism | Tree shape | State | Where it fits | Main drawback |
|---------|------|------|-------|---------|---------|
| **PIM-DM** | push (flood and prune), periodic re-flooding | source tree (one per source) | medium (prune state) | small networks, dense receivers, few sources | flooding waste, timer-driven state refresh, not for large scale |
| **PIM-SM (ASM)** | pull (explicit Join), RP + shared tree + SPT switchover | shared tree + source trees | medium-high ((*,G)+(S,G)) | general purpose, sources not fixed | RP complexity, registration/switchover overhead |
| **PIM-SSM** | pull, direct (S,G) join, **no RP** | pure source trees | low (only (S,G)) | **sources known** (IPTV, CCTV, market data) | needs IGMPv3, needs the application to know the source |
| **BiDir-PIM** | bidirectional shared tree, **no SPT switchover** | shared tree only | **lowest** (only (*,G)) | **many-to-many** (conferencing, multi-party games, collaboration) | needs DF election, traffic must pass the RP, no SSM support |

<div class="zh" markdown="1">

| PIM 模式 | 机制 | 树形 | 状态量 | 适用场景 | 主要缺点 |
|---------|------|------|-------|---------|---------|
| **PIM-DM** | 推（泛洪-剪枝），周期性重泛洪 | 源树（每源一棵） | 中（有剪枝状态） | 小网络、接收者密集、源少 | 泛洪浪费、状态定时刷新、不适合大规模 |
| **PIM-SM（ASM）** | 拉（显式 Join），RP + 共享树 + SPT 切换 | 共享树 + 源树 | 中高（(*,G)+(S,G)） | 通用、源不固定的场景 | RP 复杂、注册/切换开销 |
| **PIM-SSM** | 拉，直接 (S,G) 加入，**无 RP** | 纯源树 | 低（只有 (S,G)） | **源已知**（IPTV、监控、行情） | 需要 IGMPv3、需要应用知道源地址 |
| **BiDir-PIM** | 双向共享树，**无 SPT 切换** | 只有共享树 | **最低**（只有 (*,G)） | **多对多**（视频会议、多方游戏、协同） | 需要 DF 选举、组播必须经 RP、不支持 SSM |

</div>

**Decision tree (citable directly in a design document)**:

<div class="zh" markdown="1">

**决策树（设计文档可直接引用）**：

</div>

```
Is the source address fixed and known?
├─ yes → do terminals support IGMPv3/MLDv2?
│        ├─ yes → ★ PIM-SSM (preferred: simplest, least state)
│        └─ no  → PIM-SM + SSM Mapping (map IGMPv2 joins to (S,G))
└─ no (any source, many sources)
   ├─ is it many-to-many real-time collaboration (several speakers at once)?
   │   └─ yes → ★ BiDir-PIM
   └─ no
      ├─ small scale, dense receivers → PIM-DM (simple, but never for large networks)
      └─ otherwise → ★ PIM-SM (RP redundancy is mandatory)
```

<div class="zh" markdown="1">

```
源地址是否固定且已知？
├─ 是 → 终端支持 IGMPv3/MLDv2？
│        ├─ 是 → ★ PIM-SSM（首选，最简单、最省状态）
│        └─ 否 → PIM-SM + SSM Mapping（把 IGMPv2 加入映射为 (S,G)）
└─ 否（任意源、多源）
   ├─ 是"多对多"实时协作（多人同时发言）？
   │   └─ 是 → ★ BiDir-PIM
   └─ 否
      ├─ 规模小、接收者密集 → PIM-DM（简单但别用于大型网络）
      └─ 其他 → ★ PIM-SM（必须设计 RP 冗余）
```

</div>

**One important rule of thumb**: **80% of enterprise multicast requirements can be met with SSM**. Many networks still run PIM-SM because of "history plus applications that only speak IGMPv2". New projects should push the application side toward SSM, or use SSM Mapping.

<div class="zh" markdown="1">

**一条重要经验**：**企业里 80% 的组播需求可以用 SSM 解决**。之所以很多网络还在用 PIM-SM，是因为"历史原因 + 应用只支持 IGMPv2"。新项目应优先推动应用侧支持 SSM 或使用 SSM Mapping。

</div>

### The Complete PIM-SM Workflow (including the role of each message) · PIM-SM 完整工作流程（含每个报文的作用）

```
[Phase 1: receiver joins (shared tree)]
1. the receiver sends an IGMP Report (joining 239.1.1.1)
2. the last-hop router (LHR) creates (*, G) state and sends a PIM (*, G) Join toward the RP
3. the Join travels hop by hop toward the RP, building the shared tree (RPT, expressed as (*,G))

[Phase 2: source registration]
4. the source starts sending -> the first-hop router (FHR) receives it
5. the FHR encapsulates multicast packets in PIM Register unicast messages to the RP
6. the RP decapsulates and forwards down the shared tree, while sending a PIM (S, G) Join toward the source
7. once the source tree (SPT) is built, the RP sends Register-Stop to the FHR and unicast encapsulation stops

[Phase 3: SPT switchover (default behaviour)]
8. after the LHR receives the first multicast packet it sends an (S, G) Join directly toward the source
9. once the SPT is built the LHR sends an (S,G) rpt-prune to the RP, cutting the shared-tree branch
10. from then on traffic follows the shortest-path tree (source -> LHR -> receivers)

[Phase 4: leaving]
11. the receiver sends an IGMP Leave -> the LHR sends a group-specific query -> nobody answers -> it sends a PIM Prune
12. pruning proceeds hop by hop and routers without (S,G)/(*,G) state drop out
```

<div class="zh" markdown="1">

```
【阶段一：接收者加入（共享树）】
1. 接收者发 IGMP Report（加入 239.1.1.1）
2. 最后一跳路由器（LHR）建立 (*, G) 状态，向 RP 发 PIM (*, G) Join
3. Join 逐跳向 RP 传递，沿途建立共享树（RPT，用 (*,G) 表示）

【阶段二：源注册】
4. 源开始发送组播 → 第一跳路由器（FHR）收到
5. FHR 把组播包**封装在 PIM Register 单播报文**里，发给 RP
6. RP 解封装，沿共享树下发；同时向源方向发 PIM (S, G) Join
7. 源树（SPT）建成后，RP 向 FHR 发 Register-Stop，停止单播封装

【阶段三：SPT 切换（默认行为）】
8. LHR 收到第一个组播包后，直接向源发 (S, G) Join
9. SPT 建成 → LHR 发 (S,G) rpt-prune 给 RP，剪掉共享树分支
10. 此后流量走最短路径树（源 → LHR → 接收者）

【阶段四：离开】
11. 接收者发 IGMP Leave → LHR 发组特定查询 → 无人应答 → 发 PIM Prune
12. 上游逐跳剪枝，无 (S,G)/(*,G) 状态的路由器退出
```

</div>

**Five details you must understand**:

<div class="zh" markdown="1">

**五个必须理解的细节**：

</div>

| Detail | Explanation |
|------|------|
| **DR (designated router)** | when several PIM routers share a LAN, the DR sends Joins/Registers. Election: **highest DR priority, then highest IP** |
| **PIM Hello** | every 30 s; neighbour discovery, DR election, join suppression |
| **Join Suppression** | when several routers want the same (S,G), only the nearest upstream one sends the Join, avoiding duplicates |
| **Risk of Register encapsulation** | before the SPT is built, traffic reaches the RP by unicast encapsulation. If the source sends fast and the RP responds slowly, the RP's CPU and bandwidth suffer (**Register storm**) |
| **Assert** | when several routers on one LAN forward the same multicast downstream, Assert elects one winner and the rest stop forwarding (avoiding duplicates) |

<div class="zh" markdown="1">

| 细节 | 说明 |
|------|------|
| **DR（指定路由器）** | 同一 LAN 上多台 PIM 路由器时，由 DR 负责发 Join/Register。选举：**最高 DR 优先级，其次最高 IP** |
| **PIM Hello** | 每 30 s，用于邻居发现、DR 选举、加入抑制（Join Suppression） |
| **Join Suppression** | 多台路由器同时要同一 (S,G) 时，只由上游最近的发一次 Join，避免重复 |
| **Register 封装的风险** | 在 SPT 建成前，流量靠单播封装送 RP。如果源发送速率高、RP 响应慢，会造成 RP 的 CPU/带宽压力（**Register 风暴**） |
| **Assert** | 同一 LAN 多台路由器都往下游转发同一条组播时，用 Assert 选一个"赢家"，其他停止转发（避免重复） |

</div>

> ⚠️ **Typical symptoms of a "Register storm"**: high RP CPU, `show ip pim rp mapping` looks fine, but multicast works intermittently. The usual cause is a source sending at high rate while the RP's (S,G) Join toward the source cannot be built in time (an RPF problem, or a very slow link). Fixing RPF is the cure; `ip pim register-rate-limit` only limits the damage.

<div class="zh" markdown="1">

> ⚠️ **"Register 风暴"的典型现象**：RP 的 CPU 高、`show ip pim rp mapping` 正常但组播时断时续。原因通常是源在高速发送而 RP 到源的 (S,G) Join 没能及时建立（RPF 问题或链路极慢）。修 RPF 是根本，`ip pim register-rate-limit` 只是限损。

</div>

### SPT Switchover: the Default Behaviour and Its Cost · SPT 切换：默认行为与它的代价

> 💡 PIM-SM by default switches from the shared tree (RPT) to the shortest-path tree (SPT) once a receiver has received the **first multicast packet**, gaining a better path.

<div class="zh" markdown="1">

> 💡 PIM-SM 默认在接收者收到**第一个组播包**后，从共享树（RPT）切换到最短路径树（SPT），获得更优路径。

</div>

| Dimension | Keep the shared tree (`spt-threshold infinity`) | Switch to the SPT (default) |
|------|------------------------------------|----------------|
| **Latency** | higher (hairpins through the RP) | optimal (direct to the source) |
| **Router state** | only (*,G), **minimum state** | one (S,G) per receiver branch, state grows linearly with receivers |
| **RP load** | **the RP carries all traffic** (bandwidth bottleneck) | the RP handles signalling and initial traffic only |
| **Source-side links** | one segment from source to RP | source to every receiver branch (possibly multiple copies) |
| **Where it fits** | very many channels, low per-channel bitrate, source and RP in the same region | video/high bitrate, dispersed receivers |

<div class="zh" markdown="1">

| 维度 | 保留共享树（`spt-threshold infinity`） | 切到 SPT（默认） |
|------|------------------------------------|----------------|
| **时延** | 较高（经 RP 中转） | 最优（直接到源） |
| **路由器状态** | 只有 (*,G)，**状态量最小** | 每个接收者一条 (S,G)，状态量随接收者线性增长 |
| **RP 负载** | **RP 承载全部流量**（带宽瓶颈） | RP 只处理信令与初始流量 |
| **源侧链路** | 源到 RP 一段 | 源到每个接收者的路径（可能多份） |
| **适用** | 频道极多、单频道流量小、源与 RP 同区 | 视频/大流量、接收者分散 |

</div>

**Design judgement**:

<div class="zh" markdown="1">

**设计判断**：

</div>

- **High-bitrate single channels** (IPTV, conferencing) → the default SPT switchover is correct
- **Very many small channels with huge receiver counts** (e.g. financial data: thousands of groups at tens of kbps each) → keeping the shared tree significantly reduces state and CPU
- **Sources concentrated in one data centre with the RP in the same region** → shared tree and SPT differ very little, so keeping the shared tree simplifies state

<div class="zh" markdown="1">

- **大流量单频道**（IPTV、视频会议）→ 默认 SPT 切换是正确的
- **大量小频道 + 巨大接收者数量**（如金融行情，几千个组，每个组几十 kbps）→ 保留共享树能显著减少状态与 CPU
- **源集中在一个数据中心、RP 也在同区** → 共享树与 SPT 差别很小，可保留共享树简化状态

</div>

```cfg
! disable SPT switchover (keep the shared tree)
ip pim spt-threshold infinity group-list 239.10.0.0/16
```

<div class="zh" markdown="1">

```cfg
! 关闭 SPT 切换（保留共享树）
ip pim spt-threshold infinity group-list 239.10.0.0/16
```

</div>

> ⚠️ **SPT switchover causes a path change**: the switchover itself may drop packets briefly (milliseconds to a hundred milliseconds). For latency-critical services (trading data) that jitter must be assessed at design time, and offset with a shared tree plus Live-Live dual paths where necessary.

<div class="zh" markdown="1">

> ⚠️ **SPT 切换会带来一次"路径变化"**：切换瞬间可能出现短暂丢包（毫秒到百毫秒级）。对时延极敏感的业务（如交易行情），切换到 SPT 的抖动需要在设计时评估，必要时用共享树 + Live-Live 双路来对冲。

</div>

### PIM-DM (Dense Mode): Why It Is Rarely Used Today · PIM-DM（密集模式）：为什么现在很少用

PIM-DM's logic is "**flood first, prune later**":

<div class="zh" markdown="1">

PIM-DM 的逻辑是"**先泛洪，再剪枝**"：

</div>

```
1. the source starts sending -> routers flood to all PIM neighbours
2. branches without receivers send Prune back
3. pruned branches are re-evaluated every 3 minutes (State Refresh)
4. when a new receiver appears, Graft re-attaches quickly
```

<div class="zh" markdown="1">

```
1. 源开始发送 → 路由器向所有 PIM 邻居泛洪
2. 没有接收者的分支回 Prune
3. 被剪掉的分支每 3 分钟（State Refresh）重新评估
4. 有新接收者时，用 Graft 快速接回
```

</div>

| Advantages | Disadvantages |
|------|------|
| no RP, no IGMP version coupling | **periodic flooding** (every 3 minutes) wastes bandwidth |
| extremely simple configuration (`ip pim dense-mode` per interface) | state must be refreshed constantly; high CPU at scale |
| fast convergence (Graft is immediate) | first-packet flooding affects the whole network |
| fits "extremely dense receivers, very few sources" | complex when mixed with SM (`sparse-dense-mode`) |

<div class="zh" markdown="1">

| 优点 | 缺点 |
|------|------|
| 无需 RP、无需 IGMP 版本配合 | **周期性泛洪**（每 3 分钟）浪费带宽 |
| 配置极简（每接口 `ip pim dense-mode`） | 状态需持续刷新，规模大时 CPU 高 |
| 收敛快（Graft 立即生效） | 首包泛洪影响全网络 |
| 适合"接收者极密集、源很少" | 与 SM 混合部署复杂（sparse-dense-mode） |

</div>

**In modern designs PIM-DM survives in only two roles**: ① tiny lab/isolated networks; ② as a transitional mode for Auto-RP (`sparse-dense-mode`, because Auto-RP's 224.0.1.39/40 need dense flooding to be discovered). **Do not choose PIM-DM for a new design.**

<div class="zh" markdown="1">

**现代设计中，PIM-DM 的应用场景只剩两类**：①极小的实验/隔离网络；②作为 Auto-RP 的过渡模式（`sparse-dense-mode`，因为 Auto-RP 的 224.0.1.39/40 需要 dense 泛洪来发现）。**新设计不要选 PIM-DM。**

</div>

### PIM-SSM: Multicast Without an RP · PIM-SSM：去掉 RP 的组播

**Prerequisite**: receivers must be able to express "I want (S, G)", which needs **IGMPv3 (IPv4) / MLDv2 (IPv6)**.

<div class="zh" markdown="1">

**前提**：接收者必须能表达"我要 (S, G)"，这需要 **IGMPv3（IPv4）/ MLDv2（IPv6）**。

</div>

```
receiver ──IGMPv3 (S=10.1.1.1, G=232.1.1.1)──→ LHR
LHR ──PIM (S,G) Join (hop by hop toward the source)──→ ... ──→ FHR ──→ source
(no RP, no Register, no shared tree, no SPT switchover)
```

<div class="zh" markdown="1">

```
接收者 ──IGMPv3 (S=10.1.1.1, G=232.1.1.1)──→ LHR
LHR ──PIM (S,G) Join（逐跳指向源）──→ ... ──→ FHR ──→ 源
（无 RP、无 Register、无共享树、无 SPT 切换）
```

</div>

| SSM advantages | SSM limitations |
|-----------|-----------|
| **no RP** → no single point, no RP planning | needs IGMPv3; old terminals/applications do not support it |
| **minimum state** (only (S,G)) | the application must **know the source address** (or use SSM Mapping) |
| **no Register encapsulation** → no Register storm | needs a dedicated address block (232.0.0.0/8) |
| **better security** (receives only the specified source, inherently blocking "any-source injection") | across domains the source address must be reachable (usually via BGP) |
| shortest trees, fast convergence | a source address change = service interruption (re-join required) |

<div class="zh" markdown="1">

| SSM 的优点 | SSM 的限制 |
|-----------|-----------|
| **无 RP** → 没有单点、没有 RP 规划 | 需要 IGMPv3；老终端/老应用不支持 |
| **状态最少**（只有 (S,G)） | 应用必须**知道源地址**（或靠 SSM Mapping） |
| **无 Register 封装** → 无 Register 风暴 | 需要独立地址段（232.0.0.0/8） |
| **安全性更好**（只接收指定源，天然防"任意源注入"） | 跨域时需要明确源地址可达（通常靠 BGP 通告） |
| 树结构最短、收敛快 | 源地址变更 = 业务中断（需重新加入） |

</div>

**SSM Mapping (the key mechanism for legacy terminals)**:

<div class="zh" markdown="1">

**SSM Mapping（兼容老终端的关键机制）**：

</div>

Old terminals only speak IGMPv2 (they can express "I want G" but not the source). **SSM Mapping** configures a static "group → source" mapping on the LHR, turning an IGMPv2 (*,G) into (S,G):

<div class="zh" markdown="1">

老终端只会发 IGMPv2（只能表达 "我要 G"），无法表达源。**SSM Mapping** 在 LHR 上配置"组 → 源"的静态映射，把 IGMPv2 的 (*,G) 转换成 (S,G)：

</div>

```cfg
! map groups in 232.1.1.0/24 to two sources
ip igmp ssm-map enable
ip igmp ssm-map static 1 10.1.1.1
access-list 1 permit 232.1.1.0 0.0.0.255
```

<div class="zh" markdown="1">

```cfg
! 把 232.1.1.0/24 的组映射到两个源
ip igmp ssm-map enable
ip igmp ssm-map static 1 10.1.1.1
access-list 1 permit 232.1.1.0 0.0.0.255
```

</div>

> 💡 **SSM Mapping is the bridge between installed terminals and a modern design.** It lets the network side use SSM (no RP) while terminals keep using IGMPv2 — the most practical transition for many IPTV and CCTV projects.

<div class="zh" markdown="1">

> 💡 **SSM Mapping 是"存量终端 + 现代设计"的桥梁**。它让网络侧用 SSM（无 RP），而终端仍用 IGMPv2 —— 这是很多 IPTV/监控项目最实用的过渡方案。

</div>

### BiDir-PIM: the Only Right Answer for Many-to-Many · BiDir-PIM：多对多的唯一正解

**The problem**: in a video conference anyone may become a speaker (many sources). With PIM-SM every source needs Register plus its own source tree, and state explodes.

<div class="zh" markdown="1">

**问题**：视频会议里每个人都可能是发言者（多源），如果用 PIM-SM，每个源都要 Register + 建源树，状态爆炸。

</div>

**What BiDir does**: builds **a single bidirectional shared tree**; traffic travels "up to the RP and back down", with **no SPT switchover and no source registration**.

<div class="zh" markdown="1">

**BiDir 的做法**：**只建一棵双向共享树**，流量沿树"上行到 RP 再下行"，**不做 SPT 切换、不做源注册**。

</div>

| Mechanism | Explanation |
|------|------|
| **DF (designated forwarder) election** | each segment elects one router to forward traffic **toward the RP** (avoiding duplication) |
| **No Register** | the source sends straight up the shared tree (toward the RP) |
| **No SPT switchover** | state is only (*,G), **optimal at scale** |
| **The RP is a "logical rendezvous point"** | all traffic passes the RP, so RP placement strongly affects latency |
| **No SSM support** | BiDir and SSM are mutually exclusive (one group cannot be both) |

<div class="zh" markdown="1">

| 机制 | 说明 |
|------|------|
| **DF（指定转发者）选举** | 每个网段选一台路由器负责把流量**向 RP 方向**转发（避免重复） |
| **无 Register** | 源直接沿共享树向上（朝 RP）发送 |
| **无 SPT 切换** | 状态只有 (*,G)，**规模最优** |
| **RP 是"逻辑汇聚点"** | 流量必须经过 RP，因此 RP 位置对时延影响很大 |
| **不支持 SSM** | BiDir 与 SSM 互斥（同一组不能既 SSM 又 BiDir） |

</div>

**BiDir design constraints (easily overlooked)**:

<div class="zh" markdown="1">

**BiDir 的设计约束（容易被忽略）**：

</div>

1. **Every PIM router needs `ip pim bidir-enable`**, and the RP must be marked `bidir`
2. **The traffic path may be suboptimal** (up to the RP and back down); assess it for latency-sensitive services
3. **The RP must be highly available** (Phantom RP or Anycast-RP)
4. **Addresses must come from the ASM range** (232/8 cannot be used)

<div class="zh" markdown="1">

1. **所有 PIM 路由器都要配 `ip pim bidir-enable`**，RP 上还要指定 `bidir`
2. **流量路径可能非最优**（上行到 RP 再下来），时延敏感业务要评估
3. **RP 必须高可用**（Phantom RP 或 Anycast-RP）
4. **地址必须用 ASM 范围**（不能用 232/8）

</div>

**BiDir vs PIM-SM quick test**:

<div class="zh" markdown="1">

**BiDir vs PIM-SM 速判**：

</div>

| Scenario | Choice |
|------|------|
| One presenter plus many listeners (webcast, training) | SSM (best) or PIM-SM |
| Several people speaking at once (conferencing, multi-party collaboration) | **BiDir** |
| Bidirectional data distribution (market data: subscriptions plus cancellation broadcasts) | **BiDir** |
| Fixed source, changing receivers (IPTV) | **SSM** |

<div class="zh" markdown="1">

| 场景 | 选择 |
|------|------|
| 一个主讲人 + 很多听众（网络直播、培训） | SSM（最优）或 PIM-SM |
| 多人同时发言（视频会议、多方协同） | **BiDir** |
| 双向数据分发（金融行情：订阅 + 撤单广播） | **BiDir** |
| 源固定、接收者变动（IPTV） | **SSM** |

</div>

### SSM in Depth: Five Details That Must Be Clarified · SSM 深入：五个必须澄清的细节

#### Detail 1: the SSM group range can be changed, but should not be · 细节 1：SSM 的组范围可以改，但不该改

The standard specifies **232.0.0.0/8** (IPv4) / **FF3x::/32** (IPv6) for SSM. Devices usually have a default SSM range, which can be changed:

<div class="zh" markdown="1">

标准规定 SSM 用 **232.0.0.0/8**（IPv4）/ **FF3x::/32**（IPv6）。设备上通常有默认的 SSM range，也可以改：

</div>

```cfg
! default (Cisco)
ip pim ssm default                 ! = 232.0.0.0/8
! custom (not recommended unless you have legacy addresses)
ip pim ssm range 10                ! ACL 10 defines the range
```

<div class="zh" markdown="1">

```cfg
! 默认（Cisco）
ip pim ssm default                 ! = 232.0.0.0/8
! 自定义（不推荐，除非有历史地址）
ip pim ssm range 10                ! ACL 10 定义范围
```

</div>

| Approach | Verdict |
|------|------|
| use 232.0.0.0/8 | ★★★★★ standard, cross-vendor, intuitive to operate, avoids mixing with ASM |
| give part of 239.0.0.0/8 to SSM | ★★☆☆☆ works but dangerous: the same range may be treated as ASM on one box and SSM on another, and **inconsistent configuration across devices breaks everything** |
| mix 232 and 239 for SSM | ★☆☆☆☆ troubleshooting hell |

<div class="zh" markdown="1">

| 做法 | 评价 |
|------|------|
| 用 232.0.0.0/8 | ★★★★★ 标准、跨厂商、运维直观、避免与 ASM 混 |
| 把 239.0.0.0/8 的一部分划给 SSM | ★★☆☆☆ 可用但危险：同一段既可能被当 ASM 又可能被当 SSM，**跨设备配置不一致就全乱** |
| 混用 232 与 239 做 SSM | ★☆☆☆☆ 排障地狱 |

</div>

> ⚠️ **`ip pim ssm range` must be identical network-wide**. If the core uses the default (232/8) while one aggregation switch changes it to 239.10/16, then a receiver under that switch sending an IGMPv3 INCLUDE join for 239.10.1.1 will be treated by the core as ASM → it looks for an RP → finds none → multicast fails. This class of "locally inconsistent configuration" fault is extremely hard to find, because "most devices are the same".

<div class="zh" markdown="1">

> ⚠️ **`ip pim ssm range` 必须全网一致**。如果核心是默认（232/8）而某台汇聚改成了 239.10/16，那么该汇聚下的接收者发 IGMPv3 INCLUDE 加入 239.10.1.1 时，**核心会把它当 ASM 处理 → 去找 RP → 找不到 → 组播不通**。这类"局部配置不一致"的故障极难排查（因为"大部分设备都一样"）。

</div>

#### Detail 2: the three sources of SSM Mapping · 细节 2：SSM Mapping 的三种来源

| Method | Configuration | Advantages | Disadvantages |
|------|------|------|------|
| **Static mapping** | `ip igmp ssm-map static <acl> <source>` | deterministic, no dependencies | a source change needs a configuration change |
| **DNS mapping** | `ip igmp ssm-map dns <domain>` + `ip domain lookup` | flexible (just change DNS) | depends on DNS availability; **DNS failure = multicast failure** |
| **RADIUS/external** | rarely used | — | complex |

<div class="zh" markdown="1">

| 方式 | 配置 | 优点 | 缺点 |
|------|------|------|------|
| **静态映射** | `ip igmp ssm-map static <acl> <源>` | 确定、无依赖 | 源变了要改配置 |
| **DNS 映射** | `ip igmp ssm-map dns <域名>` + `ip domain lookup` | 灵活（改 DNS 即可） | 依赖 DNS 可用性；**DNS 故障 = 组播故障** |
| **RADIUS/外部** | 少用 | — | 复杂 |

</div>

```cfg
! static mapping (one group range -> one source)
ip igmp ssm-map enable
ip igmp ssm-map static 10 10.1.1.1
access-list 10 permit 232.1.1.0 0.0.0.255

! several sources? use several static entries (with different ACLs)
ip igmp ssm-map static 11 10.1.1.2
access-list 11 permit 232.1.2.0 0.0.0.255

! DNS mapping (PTR or an agreed domain format, implementation dependent)
ip igmp ssm-map enable
ip igmp ssm-map dns
```

<div class="zh" markdown="1">

```cfg
! 静态映射（一个组范围 → 一个源）
ip igmp ssm-map enable
ip igmp ssm-map static 10 10.1.1.1
access-list 10 permit 232.1.1.0 0.0.0.255

! 多个源？用多次 static（对应不同 ACL）
ip igmp ssm-map static 11 10.1.1.2
access-list 11 permit 232.1.2.0 0.0.0.255

! DNS 映射（组地址的 PTR/或约定的域名格式，视实现）
ip igmp ssm-map enable
ip igmp ssm-map dns
```

</div>

**Key limitations of SSM Mapping**:

<div class="zh" markdown="1">

**SSM Mapping 的关键限制**：

</div>

| Limitation | Explanation |
|------|------|
| **LHR only** | it "translates an IGMPv2 (*,G) into (S,G)", so it must run on the last hop |
| **Every LHR needs it** | miss one and the users behind it get nothing ("most people can watch") |
| **A wrong mapping raises no error** | mapping to a source that is not sending builds an entry with no traffic (identical to "the source is not sending") |
| **It does not improve security** | the network joins only the specified source, but hosts still accept any source (unless the application validates) |

<div class="zh" markdown="1">

| 限制 | 说明 |
|------|------|
| **只能在 LHR 上做** | 它是"把 IGMPv2 的 (*,G) 翻译成 (S,G)"，必须在最后一跳 |
| **每台 LHR 都要配** | 漏配一台 = 那台下面的用户收不到（"大部分人能看"） |
| **映射错了不会报错** | 映射到一个不发流的源 → 表项建了但没流量（现象与"源没发"完全相同） |
| **不改善安全性** | 网络侧虽然只加入指定源，但主机侧仍接受任意源（如果应用不校验） |

</div>

#### Detail 3: IGMPv3 Lite and URD (the application asks for SSM directly) · 细节 3：IGMPv3 Lite 与 URD（应用层直接要求 SSM）

Some legacy applications cannot use IGMPv3 but can tell the LHR their source through an application-level protocol (**URD = UDP Report to DR**, **IGMPv3 Lite**). These were early carrier IPTV transition mechanisms and have largely been replaced by SSM Mapping. **Know that they exist; you do not need to choose them.**

<div class="zh" markdown="1">

有些老应用无法用 IGMPv3，但可以用应用层协议主动告诉 LHR 它的源（**URD = UDP Report to DR**、**IGMPv3 Lite**）。这是运营商 IPTV 早期的过渡方案，现在基本被 SSM Mapping 取代。**设计时只需知道它存在，不必选它**。

</div>

#### Detail 4: what the mroute table looks like under SSM · 细节 4：SSM 下的 mroute 表长什么样

```
R1# show ip mroute 232.1.1.1
(*, 232.1.1.1), 00:00:12/00:02:47, RP 0.0.0.0, flags: DCL
  Incoming interface: Null, RPF nbr 0.0.0.0
  Outgoing interface list:
    Null0, Forward/Sparse-Dense, 00:00:12/00:00:00

(10.1.1.1, 232.1.1.1), 00:00:12/00:02:59, flags: JT
  Incoming interface: GigabitEthernet0/1, RPF nbr 10.0.0.2
  Outgoing interface list:
    GigabitEthernet0/2, Forward/Sparse-Dense, 00:00:12/00:00:00
```

<div class="zh" markdown="1">

```
R1# show ip mroute 232.1.1.1
(*, 232.1.1.1), 00:00:12/00:02:47, RP 0.0.0.0, flags: DCL
  Incoming interface: Null, RPF nbr 0.0.0.0
  Outgoing interface list:
    Null0, Forward/Sparse-Dense, 00:00:12/00:00:00

(10.1.1.1, 232.1.1.1), 00:00:12/00:02:59, flags: JT
  Incoming interface: GigabitEthernet0/1, RPF nbr 10.0.0.2
  Outgoing interface list:
    GigabitEthernet0/2, Forward/Sparse-Dense, 00:00:12/00:00:00
```

</div>

**Note**: under SSM you still see a `(*,G)` entry, but it is an **empty shell** (`RP 0.0.0.0`, `Incoming: Null`) — it only anchors the (S,G) entries and **forwards no traffic**. This is a common misunderstanding: "SSM has a (*,G)? So there must still be an RP?" — **no**, and `RP 0.0.0.0` proves it.

<div class="zh" markdown="1">

**注意**：SSM 下你仍会看到 `(*,G)` 表项，但它是**空壳**（`RP 0.0.0.0`，`Incoming: Null`）—— 它只用于挂接 (S,G)，**不转发流量**。这是一个常见的误解点："SSM 也有 (*,G)？那还是有 RP 吧？" —— **没有**，`RP 0.0.0.0` 就是证明。

</div>

#### Detail 5: why SSM is simple across domains · 细节 5：SSM 跨域为什么简单

```
SSM across domains needs only two things:
 ① receivers know the source address (application parameter / SSM Mapping / DNS)
 ② the source address is reachable at the network layer (unicast BGP already does this)

Not needed:
 ✗ RP mapping (the most error-prone thing across domains)
 ✗ MSDP (source discovery)
 ✗ MBGP (unless multicast must take a separate path)
 ✗ inter-domain PIM policy negotiation (as long as the PIM adjacency can be built)
```

<div class="zh" markdown="1">

```
SSM 跨域只需要两件事：
 ① 接收者知道源地址（应用层传参 / SSM Mapping / DNS）
 ② 源地址在网络层可达（单播 BGP 已经做到）

不需要：
 ✗ RP 映射（跨域最容易出错的东西）
 ✗ MSDP（源发现）
 ✗ MBGP（除非组播要走独立路径）
 ✗ 双方域间的 PIM 策略协商（只要 PIM 邻居能建）
```

</div>

**This is the textbook case of "reducing cross-domain dependencies"**: degrading control-plane protocol interaction to "as long as unicast routing works" cuts the number of cross-domain failure points from five to one.

<div class="zh" markdown="1">

**这是"减少跨域依赖"的教科书案例**：把"控制面协议交互"降级为"只要单播路由通"，跨域失败点从 5 个降到 1 个。

</div>

### BiDir-PIM in Depth: DF Election and the State Model · BiDir-PIM 深入：DF 选举与状态模型

#### The BiDir tree model · BiDir 的树模型

```
                RP (root of the bidirectional shared tree)
                ▲
        ┌───────┴───────┐
   R1 (DF toward RP)   R2 (DF toward RP)
   ▲     ▲                 ▲
   │     │                 │
  src1  rcv1             src2/rcv2

Traffic from any source flows "up" the tree to the RP and then "down" to receivers.
Any segment has exactly one DF per group, and that DF is responsible for forwarding "toward the RP".
```

<div class="zh" markdown="1">

```
                    RP（10.0.0.1）
                   ╱             ╲
          R1 ──── R2               R3 ──── R4
           │       │               │
         源A     接收者1          源B / 接收者2

关键：所有流量都沿这棵【双向共享树】上/下行
 源A 的流量 → R1 → R2 → RP → R3 → R4 → 接收者
源B 的流量 → R4 → R3 → RP → R2 → 接收者1
（流量必须经过 RP，即使源与接收者在同一侧）
```

</div>

**Two inevitable consequences of the model**:

<div class="zh" markdown="1">

**为什么流量必须过 RP**：BiDir 树是**以 RP 为根的单一树**，没有源树。源的流量"沿树往 RP 方向走"，到 RP 后再"沿树往下分发"。**任何两个接收者之间的流量都可能绕经 RP。**

</div>

| Consequence | Explanation |
|------|------|
| **Paths may be suboptimal** | traffic must detour through the RP, so receiver-to-receiver latency = distance to RP × 2 |
| **The RP must be highly available** | the RP is the tree root; if it goes down every group in that range stops (there is no SPT to fall back on) |

<div class="zh" markdown="1">

| 度量 | BiDir | PIM-SM |
|------|-------|--------|
| 状态条目 | (*,G) 数 = 组数 | (*,G) + (S,G) |
| 与源数量的关系 | **无关** | 线性增长 |
| 路径时延 | 可能非最优（经 RP） | SPT 后最优 |
| 首包时延 | **无 Register**（无单播封装阶段） | 有 Register 阶段 |
| RP 带宽 | **承载全部流量**（长期） | 只在切换前承载 |
| RP 故障影响 | **全部中断**（树根没了） | 已切 SPT 的会话继续 |

</div>

#### DF election (the core mechanism of BiDir) · DF 选举（BiDir 的核心机制）

| Item | Rule |
|----|------|
| **Election basis** | unicast route metric to the RP (best wins) |
| **Tie-break** | highest IP address |
| **Scope** | **per segment + per group**, and **directional** (only "toward the RP" is a DF role) |
| **Discovery** | DF election messages are carried in PIM Hello (a DF election option) |

<div class="zh" markdown="1">

| 项 | 规则 |
|----|------|
| **选举范围** | 每个网段、**每个组**、**每个方向**（朝 RP 的方向） |
| **比较项** | 到 RP 的单播路由度量（metric）→ 若相同，比 IP（大者胜） |
| **获胜者** | 成为该网段该组的 **DF**，负责把该组流量**向 RP 方向**转发 |
| **非 DF** | 不向 RP 方向转发（但仍向下游转发） |
| **选举报文** | 用 PIM Hello 中的 DF 选举选项（Offer/Pass/Winner/Backoff） |

</div>

**Why DF is per-group**: different groups may have different RPs, and "the best path to different RPs" may pass through different routers. Therefore:

<div class="zh" markdown="1">

**为什么 DF 是 per-group 的**：因为不同组可能有不同的 RP，而"到不同 RP 的最优路径"可能经过不同的路由器。所以：

</div>

```
Same segment, same router:
  for group 239.20.1.1 (RP=A) -> I am the DF (my path to A is best)
  for group 239.20.2.1 (RP=B) -> I am not the DF (another router is better to B)
```

<div class="zh" markdown="1">

```
同一网段、同一台路由器：
  对组 239.20.1.1（RP=A）→ 我是 DF（我到 A 最优）
  对组 239.20.2.1（RP=B）→ 我不是 DF（另一台到 B 更优）
```

</div>

**Troubleshooting implication**: the output of `show ip pim df` **must be read per group**. Asking "am I the DF" is the wrong question.

<div class="zh" markdown="1">

**排障含义**：`show ip pim df` 的输出**必须带组名看**。只问"我是不是 DF"是错的。

</div>

#### BiDir configuration example and five constraints · BiDir 配置示例与五个约束

```cfg
! every PIM router network-wide
ip multicast-routing
ip pim bidir-enable                ! enable BiDir globally (MUST be on every device!)

! on the RP: declare that this group range is bidir
ip pim rp-address 10.0.0.1 group-list 239.20.0.0/16 bidir

! interfaces
interface Gi0/0
 ip pim sparse-mode                ! note: BiDir groups still use sparse-mode on interfaces
```

<div class="zh" markdown="1">

```cfg
! 全网所有 PIM 路由器
ip multicast-routing
ip pim bidir-enable                ! 全局启用 BiDir（必须每台都配！）

! RP 上声明该组范围是 bidir
ip pim rp-address 10.0.0.1 group-list 239.20.0.0/16 bidir

! 接口
interface Gi0/0
 ip pim sparse-mode                ! 注意：BiDir 组仍用 sparse-mode 接口配置
```

</div>

| Constraint | Explanation | Consequence of violating it |
|------|------|---------|
| **`ip pim bidir-enable` network-wide** | one device missing it | that device treats the group as SM → multicast fails / inconsistent state |
| **The RP must be marked `bidir`** | declaring with `bidir` on the RP | the group is treated as ASM → (S,G) and Registers appear, state explodes |
| **Group addresses must be in the ASM range** | 232/8 cannot be used | conflicts with SSM |
| **The RP must be highly available** | Phantom RP / Anycast RP | RP failure = total outage (no SPT to fall back on) |
| **`spt-threshold` must not be configured** | BiDir has no concept of an SPT | the configuration is ignored or errors |

<div class="zh" markdown="1">

| 约束 | 说明 | 违反后果 |
|------|------|---------|
| **全网启用 `ip pim bidir-enable`** | 任何一台漏配 | 该设备按 SM 处理 → 组播不通 / 状态不一致 |
| **RP 必须标 `bidir`** | RP 上声明时带 `bidir` | 组被当 ASM → 出现 (S,G)、Register，状态暴涨 |
| **组地址必须在 ASM 范围** | 不能用 232/8 | 与 SSM 冲突 |
| **RP 必须高可用** | Phantom RP / Anycast RP | RP 故障 = 全部中断（无 SPT 可退） |
| **不能配 `spt-threshold`** | BiDir 无 SPT 概念 | 配置被忽略或报错 |

</div>

> ⚠️ **The most dangerous property of BiDir**: **there is no fallback**. In PIM-SM, established SPTs keep working after the RP fails; in BiDir the RP is the root of the tree, so **when the RP is gone all group traffic stops**. RP redundancy for BiDir is not a "recommendation", it is mandatory.

<div class="zh" markdown="1">

> ⚠️ **BiDir 最危险的特性**：**它没有"退路"**。PIM-SM 中 RP 故障后已建立的 SPT 还能继续；BiDir 中 RP 是树根，**RP 没了，所有组的流量都停**。所以 BiDir 的 RP 冗余不是"建议"，是"必须"。

</div>

### PIM-DM Addendum: Graft and State Refresh · PIM-DM 补充：Graft 与 State Refresh

| Mechanism | Function | Timer | Note |
|------|------|------|------|
| **Flood** | floods the first packet to all PIM neighbours | triggered | when multicast is received with no state |
| **Prune** | branches with no receivers send Prune | triggered | prune state must be refreshed |
| **Graft** | **immediately** requests forwarding again when a new receiver appears | triggered (no delay) | **this is why PIM-DM converges fast** |
| **Graft-Ack** | upstream acknowledges the Graft | triggered | reliable recovery |
| **State Refresh** | the source side periodically refreshes prune state | **60 s** default | prevents prune state from timing out and re-flooding |
| **Assert** | elects a single forwarder per LAN | triggered | same as SM |

<div class="zh" markdown="1">

| 机制 | 作用 | 定时 | 说明 |
|------|------|------|------|
| **Flood** | 首包向所有 PIM 邻居泛洪 | 触发 | 收到组播且无状态时 |
| **Prune** | 无接收者的分支回 Prune | 触发 | 剪枝状态需要刷新 |
| **Graft** | 新接收者出现时**立即**请求恢复转发 | 触发（无延迟） | **这是 PIM-DM 收敛快的来源** |
| **Graft-Ack** | 上游确认 Graft | 触发 | 可靠恢复 |
| **State Refresh** | 源侧周期性下发，维持剪枝状态 | 默认 **60 s** | 避免剪枝状态超时导致重新泛洪 |
| **Assert** | 同 LAN 选唯一转发者 | 触发 | 与 SM 相同 |

</div>

**The real state volume of PIM-DM**: it is not "stateless"; it holds **one state per (S,G) per pruned branch** and must refresh periodically. Therefore:

<div class="zh" markdown="1">

**PIM-DM 的真实状态量**：它不是"无状态"，而是"**每个 (S,G) + 每条被剪枝的分支**"都有状态，且需要周期性刷新。所以：

</div>

```
PIM-DM state ≈ number of (S,G) x average branches (INCLUDING pruned branches!)
PIM-SM state ≈ (*,G) + actually forwarding branches
```

<div class="zh" markdown="1">

```
PIM-DM 状态量 ≈ (S,G) 数 × 平均分支数（含被剪枝的分支！）
PIM-SM 状态量 ≈ (*,G) + 实际转发分支
```

</div>

**That is why PIM-DM is worst in networks with "many branches but few receivers"** — the prune state itself consumes resources.

<div class="zh" markdown="1">

**这就是为什么 PIM-DM 在"分支多但接收者少"的网络里最糟糕** —— 剪枝状态本身占资源。

</div>

### PIM Behaviour on Special Links · PIM 在特殊链路上的行为

| Link type | Key issue | Configuration point |
|---------|---------|---------|
| **Shared LAN (multiple routers)** | duplicate forwarding, Join suppression, DR | `ip pim dr-priority` + PIM Snooping |
| **Point-to-point** | no special issue | standard configuration |
| **NBMA / Frame Relay (legacy)** | broadcast emulation, pseudo-broadcast | `ip pim nbma-mode` (maintains the outgoing list per neighbour) |
| **GRE / IPsec tunnels** | **MTU**, RPF, multicast in tunnels | `ip mtu`, `tunnel mode gre multipoint`, `ip pim sparse-mode` on the tunnel interface |
| **IPsec (encrypted tunnels)** | multicast must go **GRE over IPsec** (IPsec itself does not carry multicast) | multicast into GRE, GRE into IPsec |
| **VXLAN (underlay)** | underlay multicast is used for BUM | run PIM in the underlay, or use ingress replication |
| **Wireless (WLC)** | multicast is forwarded at the lowest rate | WLC multicast-to-unicast + IGMP proxy |
| **MPLS (PE-CE)** | CE multicast needs MVPN | choose the MVPN profile |
| **SD-WAN** | most overlays do not support native multicast | multicast over GRE/overlay, or local distribution |

<div class="zh" markdown="1">

| 链路类型 | 关键问题 | 配置要点 |
|---------|---------|---------|
| **共享 LAN（多路由器）** | 重复转发、Join 抑制、DR | `ip pim dr-priority` + PIM Snooping |
| **点到点** | 无特殊问题 | 标准配置 |
| **NBMA / 帧中继（历史）** | 广播模拟、伪广播 | `ip pim nbma-mode`（按邻居维护出接口列表） |
| **GRE / IPsec 隧道** | **MTU**、RPF、隧道组播 | `ip mtu`、`tunnel mode gre multipoint`、`ip pim sparse-mode` 在 tunnel 接口 |
| **IPsec（加密隧道）** | 组播必须走 **GRE over IPsec**（IPsec 本身不支持组播） | 组播进 GRE，GRE 进 IPsec |
| **VXLAN（underlay）** | underlay 组播用于 BUM | underlay 跑 PIM，或改用 ingress replication |
| **无线（WLC）** | 组播被低速转发 | WLC 组播转单播 + IGMP proxy |
| **MPLS（PE-CE）** | CE 组播需 MVPN 承载 | MVPN profile 选择 |
| **SD-WAN** | 多数 overlay 不支持原生组播 | 用组播 over GRE/overlay，或本地分发 |

</div>

#### NBMA mode (rare, but still found in real networks) · NBMA 模式（少见，但真实环境仍会遇到）

```cfg
interface Serial0/0
 ip pim nbma-mode
```

<div class="zh" markdown="1">

```cfg
interface Serial0/0
 ip pim nbma-mode
```

</div>

**What it does**: on an NBMA link (multiple neighbours on one physical link) the mroute "outgoing interface" becomes **per-neighbour** instead of per-interface, so multicast is not replicated to neighbours that do not need it. **Without it, multicast is copied to every PVC.**

<div class="zh" markdown="1">

**作用**：在 NBMA（一条物理链路多邻居）上，mroute 的"出接口"从"接口"细化为"邻居"，避免把组播发给不需要的邻居。**没有它 → 组播在 NBMA 上被复制到所有 PVC**。

</div>

---

## RP Design and RP Discovery · RP 设计与 RP 发现

### Comparing the Four RP Discovery Methods · 四种 RP 发现方式对比

| Method | Standardisation | Mechanism | Advantages | Disadvantages | Fit |
|------|-------|------|------|------|------|
| **Static RP** | standard | configure `ip pim rp-address` manually on every router | simple, deterministic, no protocol overhead | changes need network-wide edits; no automatic redundancy | small networks, stable topology |
| **Auto-RP** | **Cisco proprietary** | C-RPs announce to 224.0.1.39; mapping agents publish the final mapping to 224.0.1.40 | automatic, supports per-group RP sets | proprietary; needs dense flooding (`sparse-dense-mode`) | all-Cisco networks |
| **BSR (BootStrap Router)** | **standard (RFC 5059)** | C-RPs unicast to the BSR; the BSR floods the RP-Set hop by hop (224.0.0.13) | standard, multi-vendor, hierarchical | slower convergence; BSR election needs tuning | multi-vendor environments |
| **Anycast-RP + MSDP** | standard | several RPs share one RP address (usually a /32 loopback) and synchronise (S,G) via MSDP | **load sharing + fast failover** | MSDP peers must be fully meshed; complex | large networks requiring HA |

<div class="zh" markdown="1">

| 方式 | 标准化 | 机制 | 优点 | 缺点 | 适用 |
|------|-------|------|------|------|------|
| **静态 RP** | 标准 | 每台路由器手工配 `ip pim rp-address` | 简单、确定、无协议开销 | 变更需全网改配置；无自动冗余 | 小型网络、拓扑稳定 |
| **Auto-RP** | **Cisco 专有** | C-RP 向 224.0.1.39 宣告；Mapping Agent 向 224.0.1.40 发布最终映射 | 自动、支持多 RP 分组 | 专有；需要 dense 泛洪（`sparse-dense-mode`） | 全 Cisco 环境 |
| **BSR（BootStrap Router）** | **标准（RFC 5059）** | C-RP 单播给 BSR；BSR 把 RP-Set 逐跳泛洪（224.0.0.13） | 标准、跨厂商、层次化 | 收敛较慢；BSR 选举需调优 | 多厂商环境 |
| **Anycast-RP + MSDP** | 标准 | 多个 RP 共享同一 RP 地址（通常 /32 loopback），用 MSDP 同步 (S,G) | **负载分担 + 快速故障切换** | 需要 MSDP peer 全互连；配置复杂 | 大型网络、要求高可用 |

</div>

### RP Placement Principles (more than "put it in the middle") · RP 放置原则（不只是"放中间"）

| Principle | Explanation | Quantitative guidance |
|------|------|---------|
| **Close to the sources** | reduces Register and source-tree setup latency, lowers RP traffic | put the primary RP in the same region as the main sources |
| **Close to the receivers** | reduces shared-tree latency (especially if the RPT is kept) | prioritise the region with the most receivers |
| **Network centre** | a compromise between sources and receivers, minimising the worst path | core layer / DC core |
| **High bandwidth, low latency location** | the RP is a traffic aggregation point (before SPT switchover) | avoid WAN edges |
| **Redundancy** | Anycast-RP + MSDP, or BSR + multiple C-RPs | at least two RPs |
| **Stability** | the RP loopback must be stable (must not follow a flapping link) | dedicated loopback + a static route fallback |
| **Operability** | addresses, roles and backup relationships documented | put them in the SoT |

<div class="zh" markdown="1">

| 原则 | 说明 | 量化建议 |
|------|------|---------|
| **靠近源** | 减少 Register 与源树建立时延，降低 RP 承载的流量 | 主 RP 与主要源同区域 |
| **靠近接收者** | 减少共享树时延（尤其保留共享树时） | 接收者集中区优先 |
| **网络中心** | 在源与接收者之间折中，减少最坏路径 | 核心层/数据中心核心 |
| **高带宽、低时延位置** | RP 是流量汇聚点（未切 SPT 前） | 避免放在 WAN 边缘 |
| **冗余** | Anycast-RP + MSDP，或 BSR + 多 C-RP | 至少 2 个 RP |
| **稳定性** | RP 的 loopback 必须稳定（不能随链路抖动） | 用独立 loopback + 静态路由兜底 |
| **可运维** | 地址、角色、备份关系写进文档 | 纳入 SoT |

</div>

**How many RPs**:

<div class="zh" markdown="1">

**RP 数量怎么定**：

</div>

| Scale | Recommendation |
|------|------|
| Single campus, little multicast | 1 RP + 1 backup (Anycast) |
| Multiple sites across a WAN | **one Anycast-RP pair per region** (register locally, avoid crossing the WAN) |
| Large enterprise / carrier | divide RPs by business domain (one for video, one for market data) so they do not affect each other |

<div class="zh" markdown="1">

| 规模 | 建议 |
|------|------|
| 单园区、少量组播 | 1 个 RP + 1 个备份（Anycast） |
| 多站点、跨 WAN | **每区域一对 Anycast-RP**（就近注册，减少跨 WAN） |
| 大型企业/运营商 | 按业务域划分 RP（视频一套、行情一套），避免互相影响 |

</div>

> ⚠️ **The biggest trap with multiple RPs**: when using a **static RP list** to point different groups at different RPs, **the mapping must be identical on every router**. If any device maps differently, "some receivers join the wrong RP", which shows up as "some people can watch, some cannot" — an extremely hard fault to diagnose, because the configuration "looks complete" everywhere.

<div class="zh" markdown="1">

> ⚠️ **多 RP 的最大陷阱**：**用"静态 RP 列表"给不同组指定不同 RP** 时，必须保证**所有路由器上的映射完全一致**。任何一台设备的映射不同，就会出现"部分接收者加入到了错误的 RP"，表现为"某些人能看、某些人不能看"—— 这类故障极难排查，因为配置看起来"都配了"。

</div>

### How Anycast-RP Works (and why MSDP is required) · Anycast-RP 的工作机制（含 MSDP 的必要性）

```
        RP-1 (RP address 10.0.0.1, router-id 1.1.1.1)
              │  MSDP peer (TCP 639)
              │
        RP-2 (RP address 10.0.0.1, router-id 2.2.2.2)
              │
   receiver A ── LHR-A                LHR-B ── receiver B
   (IGP sends A to RP-1)              (IGP sends B to RP-2)
```

<div class="zh" markdown="1">

```
        RP-1 (RP地址 10.0.0.1, router-id 1.1.1.1)
              │  MSDP peer (TCP 639)
              │
        RP-2 (RP地址 10.0.0.1, router-id 2.2.2.2)
              │
   接收者A ── LHR-A                LHR-B ── 接收者B
   （IGP 让 A 就近到 RP-1）        （IGP 让 B 就近到 RP-2）
```

</div>

**Why MSDP is needed**: receiver A registers on RP-1 and receiver B joins RP-2. Without MSDP, **RP-2 does not know the source exists** and B never receives the stream. MSDP lets RP-1 advertise **(S,G) source-active (SA)** messages to RP-2, which then sends an (S,G) Join toward the source — so traffic reaches receivers on the other side.

<div class="zh" markdown="1">

**为什么需要 MSDP**：接收者 A 在 RP-1 注册，接收者 B 在 RP-2 加入。如果没有 MSDP，RP-2 **不知道源的存在**，B 永远收不到流。MSDP 让 RP-1 把 **(S,G) 源活跃消息（SA）** 通告给 RP-2，RP-2 再向源发起 (S,G) Join —— 流量于是能到达另一侧的接收者。

</div>

```cfg
! RP-1
interface Loopback0
 ip address 10.0.0.1 255.255.255.255      ! Anycast RP address (identical on both)
interface Loopback1
 ip address 1.1.1.1 255.255.255.255       ! unique router-id / MSDP source
ip pim rp-address 10.0.0.1
ip msdp peer 2.2.2.2 connect-source Loopback1
ip msdp originator-id Loopback1

! RP-2 (mirror configuration)
ip msdp peer 1.1.1.1 connect-source Loopback1
ip msdp originator-id Loopback1
```

<div class="zh" markdown="1">

```cfg
! RP-1
interface Loopback0
 ip address 10.0.0.1 255.255.255.255      ! Anycast RP 地址（两台相同）
interface Loopback1
 ip address 1.1.1.1 255.255.255.255       ! 唯一 router-id / MSDP 源
ip pim rp-address 10.0.0.1
ip msdp peer 2.2.2.2 connect-source Loopback1
ip msdp originator-id Loopback1

! RP-2（对称配置）
ip msdp peer 1.1.1.1 connect-source Loopback1
ip msdp originator-id Loopback1
```

</div>

**Four things you must check**:

<div class="zh" markdown="1">

**四个必查项**：

</div>

| Check | Why |
|-------|-------|
| **Same RP address, different router-ids** | same address enables anycast; different ids allow MSDP to peer |
| **MSDP peers built on loopbacks (unique IPs)** | peering on the anycast address will fail |
| **MSDP full mesh or an MSDP mesh-group** | with three or more RPs a hub-and-spoke star will not propagate SAs fully |
| **IGP proximity to the anycast address** | otherwise all receivers go to the same RP and load sharing fails |

<div class="zh" markdown="1">

| 检查项 | 为什么 |
|-------|-------|
| **RP 地址相同、router-id 不同** | 相同才能 Anycast，不同才能建 MSDP |
| **MSDP peer 用 loopback（唯一 IP）** | 用 Anycast 地址建 peer 会失败 |
| **MSDP 全互连或使用 MSDP mesh-group** | 3 个以上 RP 时，星型会导致 SA 传递不全 |
| **IGP 到 Anycast 地址的就近性** | 否则所有接收者都去同一个 RP，负载分担失效 |

</div>

### Other RP High-Availability Options · 其他 RP 高可用方案

| Option | Mechanism | Advantages | Disadvantages |
|------|------|------|------|
| **Phantom RP** | configure an RP address that **exists on no device**, then use IGP longest match to send different regions to different physical RPs | no MSDP, no anycast | failover depends on routing convergence; only active/standby, no load sharing |
| **BSR + multiple C-RPs** | several C-RPs announce at once, divided by group range (group-list) | standard, divisible | no "active/standby for the same group"; failover means BSR reconvergence |
| **Auto-RP + multiple C-RPs** | same as above (Cisco) | automatic | proprietary; behaviour under overlapping ranges depends on priority |
| **Anycast-RP (RFC 4610)** | see above | load sharing + sub-second failover | requires MSDP |

<div class="zh" markdown="1">

| 方案 | 机制 | 优点 | 缺点 |
|------|------|------|------|
| **Phantom RP** | 配置一个**不存在于任何设备**的 RP 地址，用 IGP 最长匹配把不同区域"指向"不同的物理 RP | 不需要 MSDP、不需要 Anycast | 主备切换依赖路由收敛；只适合**主备**，不能负载分担 |
| **BSR + 多 C-RP** | 多台 C-RP 同时宣告，按组范围（group-list）分工 | 标准、可分工 | 无"同一组的主备"，切换靠 BSR 重新收敛 |
| **Auto-RP + 多 C-RP** | 同上（Cisco） | 自动 | 专有；组范围重叠时行为依赖优先级 |
| **Anycast-RP（RFC 4610）** | 见上 | 负载分担 + 秒级切换 | 需要 MSDP |

</div>

**How Phantom RP works (a classic interview question)**:

<div class="zh" markdown="1">

**Phantom RP 的原理（面试常考）**：

</div>

```
RP address: 10.0.0.1/32 (exists on NO device!)
On RP-A: ip pim rp-address 10.0.0.1
         and advertise a more specific route for 10.0.0.0/24 pointing at itself (e.g. 10.0.0.0/25)
On RP-B: point 10.0.0.128/25 at itself
Region A routers have 10.0.0.1 via RP-A (longest match 10.0.0.0/25)
Region B routers have 10.0.0.1 via RP-B (10.0.0.128/25)
-> different regions "see" different physical RPs while the RP address stays uniform
```

<div class="zh" markdown="1">

```
RP 地址：10.0.0.1/32（不存在于任何设备！）
RP-A 上：ip pim rp-address 10.0.0.1
        并把 10.0.0.0/24 的明细路由指向自己（如 10.0.0.0/25 指向自己）
RP-B 上：把 10.0.0.128/25 指向自己
区域A 的路由器路由表中 10.0.0.1 下一跳是 RP-A（因为最长匹配 10.0.0.0/25）
区域B 的路由器路由表中 10.0.0.1 下一跳是 RP-B（10.0.0.128/25）
→ 不同区域"看到"的 RP 是不同设备，但 RP 地址统一
```

</div>

**Fit**: networks with mature IGP hierarchy that do not want MSDP. **Does not fit**: scenarios needing load sharing (Phantom is active/standby only).

<div class="zh" markdown="1">

**适用**：已有成熟的 IGP 分层、不想引入 MSDP 的网络。**不适用**：需要负载分担（Phantom 只是主备）。

</div>

### RP Design Checklist · RP 设计检查清单

| Check | Target |
|-------|------|
| Is the RP redundant | at least two (Anycast or Phantom) |
| Is the RP address stable | dedicated loopback + a static route fallback |
| Is the RP mapping consistent on every router | spot checks + automated comparison |
| Is MSDP fully meshed / mesh-grouped | mandatory with three or more RPs |
| Is the RP reachable through ACLs and firewalls | PIM (protocol 103), MSDP (639), IGMP |
| Is there a CPU/memory baseline for the RP | monitor in high-traffic scenarios |
| Is the RP close to the sources | otherwise Registers and early traffic cross the WAN |

<div class="zh" markdown="1">

| 检查项 | 目标 |
|-------|------|
| RP 是否冗余 | 至少 2 个（Anycast 或 Phantom） |
| RP 地址是否稳定 | 独立 loopback + 静态路由兜底 |
| 所有路由器 RP 映射是否一致 | 抽查 + 自动化比对 |
| MSDP 是否全互连 / mesh-group | 3 个以上 RP 必查 |
| RP 是否被 ACL/防火墙放通 | PIM(协议 103)、MSDP(639)、IGMP |
| RP 的 CPU/内存基线 | 大流量场景要监控 |
| RP 位置是否靠近源 | 否则 Register 与初期流量跨 WAN |

</div>

### The Complete BSR Workflow (the details of the standard approach) · BSR 完整工作流程（标准方案的细节）

```
[1] C-RP starts up
  -> every 60 s it unicasts a Candidate-RP-Advertisement to the BSR
  -> contents: RP address, served group range (group-list), priority, holdtime (150 s default)

[2] BSR election
  -> all BSR candidates send Bootstrap messages to each other (224.0.0.13 multicast)
  -> compare: highest BSR priority -> highest IP
  -> the winner becomes the single BSR ("the BSR bootstraps itself by multicast discovery")

[3] The BSR distributes the RP-Set
  -> the winning BSR sends Bootstrap messages every 60 s (or when a new C-RP appears)
  -> the message is flooded out of all of the BSR's PIM interfaces
  -> each router keeps the version with the highest BSR priority and keeps flooding out its other PIM interfaces

[4] Routers select the RP
  -> per group, choose from the RP-Set: longest matching group-list -> highest priority -> highest IP (hashing optional)
  -> the result goes into the RP mapping table (show ip pim rp mapping)

[5] Failure detection
  -> when the C-RP holdtime expires (150 s default) the BSR removes that C-RP and redistributes the RP-Set
  -> so "RP dies" to "the network knows" takes up to 150 s + 60 s = 210 s
```

<div class="zh" markdown="1">

```
【1】C-RP 启动
  → 每隔 60 s，向 BSR 单播 Candidate-RP-Advertisement（224.0.0.13 为目的的单播）
  → 内容：RP 地址、服务组范围（group-list）、优先级（priority）、holdtime（默认 150 s）

【2】BSR 选举
  → 所有 BSR 候选者互相发 Bootstrap 消息（224.0.0.13 组播）
  → 比较：最高 BSR 优先级 → 最高 IP
  → 胜者成为唯一的 BSR（"BSR 是自举的，靠组播互相发现"）

【3】BSR 分发 RP-Set
  → 胜出的 BSR 每隔 60 s（或收到新 C-RP 后）发 Bootstrap 消息
  → 消息从 BSR 的"所有 PIM 接口"泛洪出去
  → 每台路由器收到后，**保留最高 BSR 优先级的版本**，并向其他 PIM 接口继续泛洪

【4】路由器选 RP
  → 对每个组，从 RP-Set 中选：最长匹配的 group-list → 最高优先级 → 最高 IP（hash 可选）
  → 结果存入 RP 映射表（show ip pim rp mapping）

【5】失效检测
  → C-RP holdtime 到期（默认 150 s）→ BSR 删除该 C-RP → 重新分发 RP-Set
  → 所以"RP 挂了"到"全网知道"最长约 150 s + 60 s = 210 s
```

</div>

**Key BSR tuning parameters**:

<div class="zh" markdown="1">

**BSR 的关键调优参数**：

</div>

| Parameter | Default | Effect of lowering it |
|------|------|-----------|
| BSR message interval | 60 s | faster RP change propagation, more overhead |
| C-RP Advertisement interval | 60 s | — |
| C-RP holdtime | 150 s | faster C-RP failure detection (but network jitter may cause false removal) |
| BSR priority | 0 | used to designate the primary BSR |

<div class="zh" markdown="1">

| 参数 | 默认 | 调小的影响 |
|------|------|-----------|
| BSR 消息间隔 | 60 s | 更快的 RP 变更传播，更多开销 |
| C-RP Advertisement 间隔 | 60 s | — |
| C-RP holdtime | 150 s | 更快检测 C-RP 失效（但网络抖动会误删） |
| BSR 优先级 | 0 | 用于指定主 BSR |

</div>

**Three design flaws of BSR**:

<div class="zh" markdown="1">

**BSR 的三个设计缺陷**：

</div>

1. **BSR messages spread across domains**: Bootstrap messages flood out of every PIM interface, so **without a BSR border your RP-Set leaks into neighbouring domains** and vice versa. A **BSR filter** (`ip pim bsr-border`) or an ACL is mandatory at domain edges.
2. **Multiple BSR candidates cause "partitioning"**: if two BSR candidates cannot reach each other (ACL blocking 224.0.0.13) they each become the BSR and the network splits into two RP views → **some receivers join the wrong RP**.
3. **Propagation delay of RP-Set changes**: BSR propagation is "hop-by-hop flooding at 60 s intervals", so in large networks **a new RP may take minutes to take effect network-wide**. This is where BSR is worse than Anycast-RP (which is routing-convergence grade, i.e. seconds).

<div class="zh" markdown="1">

1. **BSR 消息跨域扩散**：BSR 消息会从所有 PIM 接口泛洪，**如果不做 BSR border，你的域的 RP-Set 会泄漏到邻居域**，反之亦然。必须在域边界配 **BSR filter**（`ip pim bsr-border`）或 ACL。
2. **多 BSR 候选导致"分区"**：如果两台 BSR 候选互不可达（ACL 阻断 224.0.0.13），会各自成为 BSR，网络被分成两个 RP 视图 → **部分接收者加入错误的 RP**。
3. **RP-Set 变更的传播延迟**：BSR 的传播是"逐跳泛洪 + 60 s 间隔"，大规模网络中**新增 RP 到全网生效可能需要几分钟**。这是 BSR 不如 Anycast-RP 的地方（Anycast 是路由收敛级，秒级）。

</div>

```cfg
! basic BSR (Cisco)
ip pim bsr-candidate Loopback0 0            ! this device as a BSR candidate (hash-mask-len 0)
ip pim rp-candidate Loopback0 group-list 20 priority 10
access-list 20 permit 239.10.0.0 0.0.255.255

! block BSR at the domain edge
interface Gi0/0                            ! the outward-facing interface
 ip pim bsr-border
```

<div class="zh" markdown="1">

```cfg
! BSR 基础（Cisco）
ip pim bsr-candidate Loopback0 0            ! 本机作为 BSR 候选（hash-mask-len 0）
ip pim rp-candidate Loopback0 group-list 20 priority 10
access-list 20 permit 239.10.0.0 0.0.255.255

! 域边界阻断 BSR
interface Gi0/0                            ! 朝外的接口
 ip pim bsr-border
```

</div>

### The Complete Auto-RP Workflow (proprietary, but a very clean design) · Auto-RP 完整工作流程（Cisco 专有，但设计清晰）

```
[1] C-RP announces
  -> every 60 s the C-RP sends an announcement to 224.0.1.39 (CISCO-RP-ANNOUNCE)
  -> contents: its own address, served group range, holdtime (180 s default)

[2] Mapping agents aggregate
  -> every MA (mapping agent) joins 224.0.1.39
  -> after collecting all C-RP announcements it selects the RP: longest matching group-list -> highest priority -> highest IP
  -> every 60 s it sends the final RP mapping to 224.0.1.40 (CISCO-RP-DISCOVERY)

[3] Ordinary routers learn
  -> all PIM routers join 224.0.1.40
  -> they learn the RP mapping (show ip pim rp mapping shows "via Auto-RP")
```

<div class="zh" markdown="1">

```
【1】C-RP 宣告
  → C-RP 每 60 s 向 224.0.1.39（CISCO-RP-ANNOUNCE）发宣告
  → 内容：自己的地址、服务的组范围、holdtime（默认 180 s）

【2】Mapping Agent 汇聚
  → 每台 MA（Mapping Agent）加入 224.0.1.39
  → 收到所有 C-RP 宣告后，按"最长匹配 group-list → 最高优先级 → 最高 IP"选 RP
  → 每 60 s 向 224.0.1.40（CISCO-RP-DISCOVERY）发最终 RP 映射

【3】普通路由器学习
  → 所有 PIM 路由器加入 224.0.1.40
  → 学到 RP 映射（show ip pim rp mapping 显示 "via Auto-RP"）
```

</div>

**Why Auto-RP needs dense mode (a classic exam point)**:

<div class="zh" markdown="1">

**为什么 Auto-RP 需要 dense 模式（经典考点）**：

</div>

- 224.0.1.39/40 are **not** inside 224.0.0.0/24, so routers treat them as ordinary multicast
- But **there is no RP yet** (that is exactly what is being discovered), so SSM/SM cannot be used to distribute them
- Solution: **`ip pim sparse-dense-mode`** — dense mode for those two groups (flooding) and sparse mode for everything else
- The more modern solution: **separating Auto-RP "listener" from "forwarder"** (`ip pim autorp listener`), so the Auto-RP groups are handled densely while interfaces stay sparse-mode

<div class="zh" markdown="1">

- 224.0.1.39/40 **不是**在 224.0.0.0/24 内，**会被路由器按普通组播处理**
- 但此时**还没有 RP**（这正是要发现 RP 的过程），所以无法用 SSM/SM 来分发
- 解决：**`ip pim sparse-dense-mode`** —— 对这两个组用密集模式（泛洪），其他组用稀疏模式
- 更现代的解法：**Auto-RP 的 "listener" 与 "forwarder" 分离**（`ip pim autorp listener`），让 Auto-RP 组以 dense 方式处理而接口仍是 sparse-mode

</div>

```cfg
! modern approach (recommended): interfaces stay sparse-mode, autorp listener handles 224.0.1.39/40
ip pim autorp listener
interface range Gi0/0 - 3
 ip pim sparse-mode

! or the legacy approach (not recommended, because dense floods)
interface range Gi0/0 - 3
 ip pim sparse-dense-mode
```

<div class="zh" markdown="1">

```cfg
! 现代写法（推荐）：接口保持 sparse-mode，用 autorp listener 处理 224.0.1.39/40
ip pim autorp listener
interface range Gi0/0 - 3
 ip pim sparse-mode

! 或者传统写法（不推荐，因为 dense 会泛洪）
interface range Gi0/0 - 3
 ip pim sparse-dense-mode
```

</div>

**Auto-RP scope (limiting propagation)**:

<div class="zh" markdown="1">

**Auto-RP 的 scope（限制传播范围）**：

</div>

```cfg
! use TTL to limit Auto-RP announcement propagation (decremented per hop, configured on the boundary interface)
interface Gi0/0
 ip multicast boundary 30                ! block 224.0.1.39/40 and service groups
access-list 30 deny 224.0.1.39
access-list 30 deny 224.0.1.40
access-list 30 permit 239.10.0.0 0.0.255.255
access-list 30 deny any
```

<div class="zh" markdown="1">

```cfg
! 用 TTL 限制 Auto-RP 通告的传播（每跳减 1，配在边界接口上）
interface Gi0/0
 ip multicast boundary 30                ! 阻断 224.0.1.39/40 与业务组
access-list 30 deny 224.0.1.39
access-list 30 deny 224.0.1.40
access-list 30 permit 239.10.0.0 0.0.255.255
access-list 30 deny any
```

</div>

> ⚠️ **The classic Auto-RP failure**: **multiple mapping agents that cannot reach each other** → each publishes a different RP mapping → routers in different regions use different RPs → "some people can watch, some cannot". Diagnosis: **compare `show ip pim rp mapping` on every device**, including both the "Group(s)" and "RP address" columns.

<div class="zh" markdown="1">

> ⚠️ **Auto-RP 的经典故障**：**Mapping Agent 有多台且互不可达** → 各自发布不同的 RP 映射 → 不同区域的路由器使用不同 RP → "部分人能看、部分人不能看"。诊断方法：**在所有设备上比对 `show ip pim rp mapping`**，包括 "Group(s)" 与 "RP address" 两列。

</div>

### Anycast-RP: Three Implementations and the Failover Budget · Anycast-RP：三种实现与切换预算

| Implementation | Mechanism | Needs MSDP | Advantages | Disadvantages |
|------|------|--------------|------|------|
| **RFC 4610 (MSDP-based)** | several RPs share one address and synchronise SAs over MSDP | **yes** | standard, multi-vendor, load sharing | requires an MSDP mesh |
| **Anycast-RP with PIM (another form of RFC 4610 / vendor implementation)** | synchronisation using PIM itself (e.g. "anycast RP with PIM register") | no | no MSDP needed | large vendor differences |
| **Phantom RP** | a virtual RP address plus IGP longest match | no | simple, no MSDP | active/standby only, no load sharing |

<div class="zh" markdown="1">

| 实现 | 机制 | 是否需要 MSDP | 优点 | 缺点 |
|------|------|--------------|------|------|
| **RFC 4610（MSDP-based）** | 多个 RP 共享同一地址 + MSDP 同步 SA | **是** | 标准、跨厂商、负载分担 | 需要 MSDP mesh |
| **Anycast-RP with PIM（RFC 4610 的另一形态 / 厂商实现）** | 用 PIM 自身同步（如 "Anycast RP with PIM register"） | 否 | 无需 MSDP | 厂商差异大 |
| **Phantom RP** | 虚拟 RP 地址 + IGP 最长匹配指向 | 否 | 简单、无需 MSDP | 只主备，无负载分担 |

</div>

#### Complete Anycast-RP deployment steps (do them in order; skip one and you have done nothing) · Anycast-RP 的完整部署步骤（按顺序做，错一步就白做）

| Step | Action | Verification command | Common failure |
|------|------|---------|---------|
| **1** | both RPs get the **same** anycast address (usually a /32 loopback) | `show ip int brief` | different masks → inconsistent routing |
| **2** | each RP gets a **unique** router-id and MSDP source address (a second loopback) | `show ip protocols` / `show run | inc router-id` | **identical router-ids → MSDP peers with itself** |
| **3** | configure `ip pim rp-address <anycast>` network-wide | `show ip pim rp mapping` | missed on some devices → those devices cannot find the RP |
| **4** | build the MSDP peer between the two RPs (using the unique addresses) | `show ip msdp summary` | peering on the anycast address → never establishes |
| **5** | configure `ip msdp originator-id <unique>` | `show ip msdp peer` | without it the SA carries the anycast address → the peer misjudges |
| **6** | IGP makes the anycast address **equal-cost or nearest** on both RPs | `show ip route <anycast>` per region | metrics too far apart → all traffic to one RP (load sharing lost) |
| **7** | `ip msdp cache-sa-state` (if SA caching is needed) | `show ip msdp sa-cache` | without it some scenarios see Join delay |
| **8** | SA filters + limits + authentication | in/out filters in `show ip msdp peer` | without them, a security risk |

<div class="zh" markdown="1">

| 步骤 | 动作 | 检查命令 | 常见失败 |
|------|------|---------|---------|
| **1** | 两台 RP 配置**相同**的 Anycast 地址（通常 /32 loopback） | `show ip int brief` | 掩码不同 → 路由不一致 |
| **2** | 两台 RP 各配**唯一**的 router-id 与 MSDP 源地址（第二个 loopback） | `show ip protocols` / `show run | inc router-id` | **router-id 相同 → MSDP 自己连自己** |
| **3** | 全网配置 `ip pim rp-address <anycast>` | `show ip pim rp mapping` | 漏配 → 部分设备找不到 RP |
| **4** | 两台 RP 之间建 MSDP peer（用唯一地址） | `show ip msdp summary` | 用 anycast 地址建 peer → 建不起来 |
| **5** | 配 `ip msdp originator-id <唯一地址>` | `show ip msdp peer` | 不配 → SA 里带的 RP 地址是 anycast → 对端误判 |
| **6** | IGP 保证两台 RP 的 anycast 地址**等价或就近** | 各区域 `show ip route <anycast>` | 度量差太大 → 所有流量去一台（负载分担失效） |
| **7** | `ip msdp cache-sa-state`（若需要 SA 缓存） | `show ip msdp sa-cache` | 不配 → 部分场景 Join 延迟 |
| **8** | SA 过滤 + 限制 + 认证 | `show ip msdp peer` 的 in/out filter | 不配 → 安全风险 |

</div>

#### The failover time budget (a design input, not theory) · 故障切换的时间预算（这是设计输入，不是理论）

```
Scenario: RP-1 fails (the anycast address can be taken over by RP-2)

① IGP detects RP-1 unreachable:      OSPF 40 s by default (hello 10/dead 40); BFD can bring it under 1 s
② routing converges, anycast -> RP-2:  tens of ms to a few seconds
③ a new receiver sends (*,G) Join -> arrives at RP-2:  immediate
④ RP-2 must know the source (from the MSDP SA cache, or by sending an (S,G) Join):  immediate on a cache hit, otherwise wait for the FHR's Register
⑤ tree built, first packet arrives:   hundreds of ms to a few seconds

Total: over 40 s without BFD; typically under 2 s with BFD + an SA cache
```

<div class="zh" markdown="1">

```
场景：RP-1 故障（Anycast 地址仍可由 RP-2 接管）

① IGP 检测 RP-1 不可达：        OSPF 默认 40 s（hello 10/dead 40），BFD 可到 <1 s
② 路由收敛，anycast 地址指向 RP-2：  几十 ms ~ 数秒
③ 新接收者发 (*,G) Join → 到达 RP-2：  立即
④ RP-2 需要知道源（来自 MSDP SA 缓存 或 向源发 (S,G) Join）：  缓存命中则立即；否则要等 FHR 的 Register
⑤ 树建立，首包到达：            百毫秒 ~ 数秒

总：无 BFD 时可能 40 s 以上；有 BFD + SA 缓存时通常 < 2 s
```

</div>

> 💡 **Design implication**: **"sub-second failover with Anycast-RP" has preconditions** — ① fast IGP detection (BFD) ② the MSDP SA cache already exists (`cache-sa-state`) ③ the FHR will resend Registers (it does by default, via periodic Register probing). **Miss any one and failover degrades to 30 s or more.** So "I deployed Anycast" does not mean "I achieved sub-second failover".

<div class="zh" markdown="1">

> 💡 **设计含义**：**Anycast-RP 的"秒级切换"是有前提的** —— ①IGP 快速检测（BFD）②MSDP SA 缓存已存在（`cache-sa-state`）③FHR 会重发 Register（默认会，因为有周期性 Register 探测）。**少任何一个，切换时间就会退化到 30 秒以上。** 所以"我做了 Anycast"不等于"我实现了秒级切换"。

</div>

### Phantom RP: Complete Configuration and Boundaries · Phantom RP 的完整配置与边界

```cfg
! network-wide: the RP address is 10.0.0.1/32 (exists on no device)
! RP-A (primary): point 10.0.0.0/25 at itself
interface Loopback0
 ip address 10.0.0.1 255.255.255.255      ! careful: configuring this address means it is no longer "phantom"
! correct approach: do not configure 10.0.0.1, configure a more specific route pointing at yourself
ip route 10.0.0.0 255.255.255.128 Null0  ! or advertise 10.0.0.0/25 in the IGP
! RP-A must still have a real PIM identity (router-id and a physical address)

! RP-B (backup): point 10.0.0.128/25 at itself
ip route 10.0.0.128 255.255.255.128 Null0

! network-wide
ip pim rp-address 10.0.0.1
```

<div class="zh" markdown="1">

```cfg
! 全网统一：RP 地址是 10.0.0.1/32（不存在于任何设备）
! RP-A（主）：把 10.0.0.0/25 指向自己
interface Loopback0
 ip address 10.0.0.1 255.255.255.255      ! 注意：配置了这个地址就不是"phantom"了
! 正确做法：不配 10.0.0.1，而是配置更具体的路由指向自己
ip route 10.0.0.0 255.255.255.128 Null0  ! 或用 IGP 通告 10.0.0.0/25
! 同时 RP-A 必须有真实的 PIM 身份（router-id 与物理地址）

! RP-B（备）：把 10.0.0.128/25 指向自己
ip route 10.0.0.128 255.255.255.128 Null0

! 全网
ip pim rp-address 10.0.0.1
```

</div>

**How Phantom RP works (one more time)**:

<div class="zh" markdown="1">

**Phantom RP 的工作原理（再强调一次）**：

</div>

```
Region A routers: longest match for 10.0.0.1 is 10.0.0.0/25 -> next hop RP-A
Region B routers: longest match for 10.0.0.1 is 10.0.0.128/25 -> next hop RP-B

-> every device believes the RP is 10.0.0.1
-> but different physical devices actually handle Registers/Joins
-> no MSDP is needed (the two "half-domain" trees are naturally separate)
```

<div class="zh" markdown="1">

```
区域 A 的路由器：到 10.0.0.1 的最长匹配是 10.0.0.0/25 → 下一跳 RP-A
区域 B 的路由器：到 10.0.0.1 的最长匹配是 10.0.0.128/25 → 下一跳 RP-B

→ 所有设备认为 RP 是 10.0.0.1
→ 但实际处理注册/Join 的是不同的物理设备
→ 不需要 MSDP（因为两棵"半个域"的树天然分开）
```

</div>

| Phantom RP limitation | Explanation |
|------------------|------|
| **Active/standby only, no load sharing** | it partitions by routing, not by equal cost |
| **Failover depends on routing convergence** | primary RP fails → the /25 route must move to the backup → multicast is interrupted during convergence |
| **Requires strict route planning** | the /25 boundaries must be clean and not overridden by other routes |
| **Care needed across regions** | if a region learns both /25s (equal cost) behaviour is undefined |
| **Cannot be combined with "RP proximity"** | logically simple, but only splits in two (more is theoretically possible but operational complexity explodes) |

<div class="zh" markdown="1">

| Phantom RP 的限制 | 说明 |
|------------------|------|
| **只主备，不能负载分担** | 靠路由"分区"，不是靠等价 |
| **切换依赖路由收敛** | 主 RP 故障 → 需要 /25 路由切到备 → 收敛时间内组播中断 |
| **要求严格的路由规划** | /25 与 /25 的边界必须清晰，且不被其他路由覆盖 |
| **跨区域须小心** | 如果某区域的 IGP 学到两个 /25（等价），行为不确定 |
| **不能与"RP 就近性"混用** | 逻辑简单，但只能二分，不能三分以上（理论上可以，但运维复杂度急剧上升） |

</div>

### A Quantitative Example of RP Placement (turning "put it in the middle" into numbers) · RP 放置的量化算例（把"放中间"变成数字）

**Scenario**: four sites (A headquarters, B/C/D branches), WAN is hub-and-spoke (A is the hub). The multicast source is at A; receivers: A=50, B=30, C=20, D=10.

<div class="zh" markdown="1">

**场景**：4 个站点（A 总部、B/C/D 分支），WAN 为 Hub-Spoke（A 为 Hub）。组播源在 A，接收者：A=50、B=30、C=20、D=10。

</div>

**Option 1: RP at A (the hub)**

<div class="zh" markdown="1">

**方案 1：RP 在 A（Hub）**

</div>

| Item | Calculation |
|----|------|
| Register traffic | source→RP is intra-site, **zero WAN crossing** |
| Shared-tree traffic (before switchover) | each group's first packets traverse A→B/C/D, briefly |
| After SPT switchover | one copy each A→B/C/D, **independent of the RP** |
| Impact of RP failure | new receivers cannot join |
| Advantages | no Register traffic across the WAN, RP in the same region as the sources |

<div class="zh" markdown="1">

| 项 | 计算 |
|----|------|
| Register 流量 | 源→RP 同站点，**0 跨 WAN** |
| 共享树流量（切换前） | 每个组的首包经 A→B/C/D，短暂 |
| SPT 切换后 | A→B/C/D 各一份，**与 RP 无关** |
| RP 故障影响 | 新接收者无法加入 |
| 优点 | 无 Register 跨 WAN、RP 与源同区 |

</div>

**Option 2: RP at B (a branch)**

<div class="zh" markdown="1">

**方案 2：RP 在 B（分支）**

</div>

| Item | Calculation |
|----|------|
| Register traffic | source (A)→RP (B): **one copy per source for as long as the SPT takes to build**, possibly sustained across the WAN at peak |
| Shared-tree traffic | traffic arriving at B must be redistributed to A/C/D → **doubled across the WAN** |
| Impact of RP failure | network-wide |
| Verdict | **clearly worse** |

<div class="zh" markdown="1">

| 项 | 计算 |
|----|------|
| Register 流量 | 源（A）→ RP（B）：**每源一份持续到 SPT 建立**，高峰期可能持续跨 WAN |
| 共享树流量 | B 收到的流量要再分发给 A/C/D → **跨 WAN 双倍** |
| RP 故障影响 | 全网 |
| 结论 | **明显更差** |

</div>

**Conclusion (a quantifiable design principle)**: **the RP belongs on the side where sources are most concentrated, not where receivers are most numerous.** The reason: Registers are a **continuous, per-source** cost, whereas shared-tree traffic stops passing through the RP once the SPT is built. Many designs put the RP "in the middle of the users" (because it feels "close to the users"), which actually increases cross-WAN registration traffic.

<div class="zh" markdown="1">

**结论（可量化的设计原则）**：**RP 应放在"源最集中"的一侧，而不是"接收者最多"的一侧。** 原因：Register 是**持续的、按源计**的开销，而共享树流量在 SPT 切换后就不再经过 RP。很多设计把 RP 放在"用户中心"（因为直觉上"离用户近"），实际增加了跨 WAN 的注册流量。

</div>

**If sources are spread across sites**:

<div class="zh" markdown="1">

**如果源分散在多个站点**：

</div>

| Option | Explanation |
|------|------|
| **RP on the same side as LHR/FHR (one Anycast pair per site)** | the most thorough: Registers never leave the site; cross-site via MSDP SA |
| Single RP near the main source | simple, but secondary sources register across the WAN |
| **Switch to SSM** | no RP needed at all (recommended) |

<div class="zh" markdown="1">

| 方案 | 说明 |
|------|------|
| **LHR/FHR 同侧 RP（每站点一对 Anycast）** | 最彻底：Register 不出站点，跨站点靠 MSDP SA |
| 单 RP + 靠近主源 | 简单，但次要源跨 WAN 注册 |
| **改 SSM** | 根本不需要 RP（推荐） |

</div>

### RP Capacity Baseline (the four things you must monitor) · RP 容量基线（必须监控的四项）

| Metric | Meaning | Alert threshold (rule of thumb) |
|------|------|-----------------|
| **(*,G) count** | number of groups the RP carries | alert above 60% of platform capability |
| **Register rate** | Register messages received per second | a 5× spike → look for a new source / Register storm |
| **CPU (the RP process)** | multicast process utilisation | sustained > 50% → optimise or scale |
| **MSDP SA count** | source-active entries received | a spike → look for SA injection / new services |

<div class="zh" markdown="1">

| 指标 | 含义 | 告警阈值（经验） |
|------|------|-----------------|
| **(*,G) 数** | RP 承载的组数 | > 平台能力 60% 告警 |
| **Register 速率** | 每秒收到的 Register 报文 | 突增 5 倍 → 查新源/Register 风暴 |
| **CPU（RP 进程）** | 组播进程占用 | > 50% 持续 → 需优化/扩容 |
| **MSDP SA 数** | 收到的源活跃条目 | 突增 → 查 SA 注入 / 新业务 |

</div>

---

## Inter-Domain Multicast · 域间组播

### Why Inter-Domain Multicast Is So Hard · 为什么域间组播特别难

| Difficulty | Explanation |
|------|------|
| **Source discovery** | the receiver's domain does not know where the source is (PIM-SM RPs are designed per domain) |
| **RPF inconsistency** | the multicast RPF path may differ from the unicast optimum (policy, traffic engineering, egress choice) |
| **Policy and trust** | across domains you must control "who may send and who may receive", and PIM itself has no authentication or authorisation |
| **Addressing** | each domain uses its own private multicast range (239/8), which conflicts across domains |

<div class="zh" markdown="1">

| 难点 | 说明 |
|------|------|
| **源发现** | 接收者所在域不知道源在哪里（PIM-SM 的 RP 是按域设计的） |
| **RPF 不一致** | 组播的 RPF 路径与单播最优路径可能不同（策略、流量工程、出口选择） |
| **策略与信任** | 跨域要控制"谁能发组播、谁能收"，而 PIM 本身没有认证与授权 |
| **地址体系** | 各域用不同的私有组播段（239/8），跨域会冲突 |

</div>

### MSDP (Multicast Source Discovery Protocol) · MSDP（组播源发现协议）

| Item | Content |
|----|------|
| **Purpose** | exchange **(S,G) source-active (SA)** messages between **different PIM-SM domains** |
| **Transport** | **TCP 639**; peers fully meshed or in a mesh-group |
| **Messages** | SA (Source-Active), SA-Request, SA-Response, keepalive |
| **What it solves** | domain A's source being discovered by domain B's receivers (B's RP sends a Join toward the source after receiving the SA) |
| **What it does not solve** | **the RPF path** (that is MBGP's job), policy control, source authentication |

<div class="zh" markdown="1">

| 项 | 内容 |
|----|------|
| **作用** | 在**不同 PIM-SM 域**之间交换 **(S,G) 源活跃（SA）消息** |
| **传输** | **TCP 639**，peer 之间全互连或 mesh-group |
| **消息** | SA（Source-Active）、SA-Request、SA-Response、Keepalive |
| **解决什么** | 域 A 的源被域 B 的接收者发现（B 的 RP 收到 SA 后向源发起 Join） |
| **不解决什么** | **RPF 路径**（那是 MBGP 的事）、策略控制、源认证 |

</div>

**MSDP's RPF check rule (the usual reason for "SA received but no tree built")**: after receiving an SA, the RP checks whether "the address of the MSDP peer that advertised it" matches "the unicast/multicast RPF neighbour toward the source" (the exact rule depends on the implementation and `msdp rpf` configuration). **If they disagree the SA is dropped** — which is why cross-domain MSDP so often shows "peers are established but the SA count is 0".

<div class="zh" markdown="1">

**MSDP 的 RPF 检查规则（导致"SA 收到了但没建树"的常见原因）**：RP 收到 SA 后，会检查"通告该 SA 的 MSDP peer 地址"是否与"到源的单播/组播 RPF 邻居"一致（规则因实现与 `msdp rpf` 配置而异）。**不一致就丢弃 SA** —— 所以跨域 MSDP 常常"peer 是 Establish 的，但 SA 数为 0"。

</div>

```cfg
! basic MSDP plus limits (mandatory in production)
ip msdp peer 203.0.113.1 connect-source Loopback0
ip msdp cache-sa-state
ip msdp sa-filter in 203.0.113.1 list 10     ! accept SAs only from the listed sources (anti-injection)
ip msdp sa-filter out 203.0.113.1 list 20    ! advertise only our own sources
ip msdp sa-limit 203.0.113.1 5000            ! prevent SA flooding from exhausting memory
```

<div class="zh" markdown="1">

```cfg
! MSDP 基础配置 + 限制（生产必备）
ip msdp peer 203.0.113.1 connect-source Loopback0
ip msdp cache-sa-state
ip msdp sa-filter in 203.0.113.1 list 10     ! 只接受指定源的 SA（防注入）
ip msdp sa-filter out 203.0.113.1 list 20    ! 只通告自己的源
ip msdp sa-limit 203.0.113.1 5000            ! 防 SA 泛洪打爆内存
```

</div>

> ⚠️ **The MSDP security risk**: anything that can open TCP 639 to your RP can **advertise arbitrary (S,G)** pairs, making your network join a non-existent or malicious source (resource consumption). In production you must configure `sa-filter` + `sa-limit` + peer authentication (MD5/TCP-AO) + an ACL restricting the source of port 639.

<div class="zh" markdown="1">

> ⚠️ **MSDP 的安全风险**：任何能与你的 RP 建立 TCP 639 的设备都可以**通告任意 (S,G)**，让你的网络去加入一个不存在的源（资源消耗）或恶意源。**生产上必须配 `sa-filter` + `sa-limit` + peer 认证（MD5/TCP-AO）+ ACL 限制 639 端口来源。**

</div>

### MBGP (Multicast BGP, SAFI 2)

**The problem**: the unicast best path and the multicast best path may differ. For example:
- unicast via carrier A (cheaper), multicast required via carrier B (better multicast quality)
- unicast uses a default route, multicast needs exact source prefixes

<div class="zh" markdown="1">

**问题**：单播最优路径与组播最优路径可能不同。例如：
- 单播走运营商 A（便宜），组播要求走运营商 B（组播质量好）
- 单播用默认路由，组播需要精确的源前缀

</div>

**What MBGP does**: BGP maintains **a separate address family for multicast (`address-family ipv4 multicast`, SAFI 2)**, and routers prefer the MBGP table when performing the RPF check.

<div class="zh" markdown="1">

**MBGP 的做法**：在 BGP 中为组播维护**独立的地址族（`address-family ipv4 multicast`，SAFI 2）**，路由器做 RPF 检查时优先使用 MBGP 表。

</div>

```cfg
router bgp 65000
 address-family ipv4
  neighbor 10.0.0.1 activate
 address-family ipv4 multicast
  neighbor 10.0.0.1 activate
  network 10.1.1.0 mask 255.255.255.0
```

<div class="zh" markdown="1">

```cfg
router bgp 65000
 address-family ipv4
  neighbor 10.0.0.1 activate
 address-family ipv4 multicast
  neighbor 10.0.0.1 activate
  network 10.1.1.0 mask 255.255.255.0
```

</div>

**MBGP versus unicast BGP (an easy confusion)**:

<div class="zh" markdown="1">

**MBGP 与单播 BGP 的关系（易混点）**：

</div>

| Item | Unicast BGP | MBGP |
|----|---------|------|
| Address family | `ipv4 unicast` (SAFI 1) | `ipv4 multicast` (SAFI 2) |
| Purpose | unicast forwarding | **used only for the RPF check**, never for unicast forwarding |
| Routing table | unicast RIB | multicast RPF table (visible as a source in `show ip rpf`) |
| Is it required | depends on the network | only when "the multicast path must differ from unicast" |

<div class="zh" markdown="1">

| 项 | 单播 BGP | MBGP |
|----|---------|------|
| 地址族 | `ipv4 unicast`（SAFI 1） | `ipv4 multicast`（SAFI 2） |
| 用途 | 单播转发 | **只用于 RPF 检查**，不用于单播转发 |
| 路由表 | 单播 RIB | 组播 RPF 表（`show ip rpf` 可见来源） |
| 是否必须 | 视网络 | 只在"组播路径需与单播不同"时才需要 |

</div>

### The Four Approaches to Cross-Domain Multicast · 跨域组播的四种方案

| Approach | Mechanism | Fit | Complexity |
|------|------|------|--------|
| **Single domain (no crossing)** | solved inside one PIM domain | inside the enterprise | low |
| **MSDP (ASM across domains)** | exchange SAs between domains, each builds its own tree | traditional cross-domain multicast (e.g. carrier-provided multicast) | medium-high |
| **MBGP + MSDP** | MBGP provides RPF, MSDP provides source discovery | cross-domain requiring a separate multicast path | high |
| **SSM across domains** | no RP, no MSDP; only source-prefix reachability (plain BGP unicast) | **recommended**: multicast distribution between enterprises and carriers | **low** |

<div class="zh" markdown="1">

| 方案 | 机制 | 适用 | 复杂度 |
|------|------|------|--------|
| **单域（无跨域）** | 一个 PIM 域内解决 | 企业内部 | 低 |
| **MSDP（ASM 跨域）** | 域间交换 SA，各自建树 | 传统跨域组播（如运营商提供组播） | 中高 |
| **MBGP + MSDP** | MBGP 提供 RPF，MSDP 提供源发现 | 需要独立组播路径的跨域 | 高 |
| **SSM 跨域** | 无 RP、无 MSDP；只需源前缀可达（BGP 单播即可） | **推荐**：企业与运营商间的组播分发 | **低** |

</div>

> 💡 **Modern recommendation**: **prefer SSM across domains**. SSM needs no RP and no MSDP — only that "the source address is reachable at the network layer" (ordinary BGP is enough). This also explains why IPTV distribution has moved almost entirely to SSM.

<div class="zh" markdown="1">

> 💡 **现代建议**：**跨域优先用 SSM**。因为 SSM 不需要 RP、不需要 MSDP，只要"源地址在网络层可达"（靠普通 BGP 就够）。这也解释了为什么 IPTV 分发几乎全面转向 SSM。

</div>

### Crossing Firewalls and Multicast Boundaries · 跨防火墙与组播边界

Multicast is not "configure PIM and it works": boundary devices (firewalls, inter-domain routers) need specific design.

<div class="zh" markdown="1">

组播不是"配个 PIM 就通了"，边界设备（防火墙、跨域路由器）需要专门设计：

</div>

| Scenario | Approach | Explanation |
|------|------|------|
| **Across a firewall** | **IGMP Proxy** or **PIM static Join** | firewalls usually do not run PIM; a proxy carries the join requests across |
| **Unidirectional distribution** | `ip pim static-join` / static mroute + static outgoing interface | no protocol, maximum control |
| **Across a device that does not support it** | **GRE tunnels** carrying multicast (`tunnel mode gre multipoint`) | a common transitional approach across WANs/cloud |
| **Domain boundary** | PIM boundary ACL / multicast boundary (`ip multicast boundary`) | restricts which groups may cross |
| **TTL threshold** | `ip multicast ttl-threshold` | restricts the propagation range (a "hop-count firewall") |

<div class="zh" markdown="1">

| 场景 | 方案 | 说明 |
|------|------|------|
| **防火墙两侧** | **IGMP Proxy** 或 **PIM 静态 Join** | 防火墙通常不跑 PIM；用 Proxy 把加入请求代理过去 |
| **单向分发** | `ip pim static-join` / 静态 mroute + 静态出接口 | 无需协议，最可控 |
| **跨不支持的中间设备** | **GRE 隧道** 承载组播（`tunnel mode gre multipoint`） | 常见于跨 WAN/云的过渡方案 |
| **域边界** | PIM Boundary ACL / 组播边界（`ip multicast boundary`） | 限制哪些组可以跨边界 |
| **TTL 阈值** | `ip multicast ttl-threshold` | 限制组播传播范围（类似"跳数防火墙"） |

</div>

```cfg
! multicast boundary: allow only 239.10.0.0/16 through, and limit TTL
interface Gi0/0
 ip multicast boundary 30
 ip multicast ttl-threshold 16
access-list 30 permit 239.10.0.0 0.0.255.255
access-list 30 deny any
```

<div class="zh" markdown="1">

```cfg
! 组播边界：只允许 239.10.0.0/16 通过，且限制 TTL
interface Gi0/0
 ip multicast boundary 30
 ip multicast ttl-threshold 16
access-list 30 permit 239.10.0.0 0.0.255.255
access-list 30 deny any
```

</div>

### MSDP in Depth: SA Messages, the RPF Rule and Mesh Groups · MSDP 深入：SA 消息、RPF 规则与 Mesh Group

#### What an SA message actually contains · SA 消息里到底有什么

| Field | Content | Diagnostic value |
|------|------|---------|
| **RP address** | the RP advertising the SA (must match `originator-id`) | mismatch → the peer drops it |
| **(S,G) list** | one SA can carry several source-group pairs | the SA count is not the (S,G) count |
| **Holdtime** | validity of the SA (75 s default, refreshed every 60 s) | timeout → the SA disappears → cross-RP receivers cannot build a tree |
| **Encapsulated data** | optional (carries the original multicast packet on the first registration) | rare |

<div class="zh" markdown="1">

| 字段 | 内容 | 排障价值 |
|------|------|---------|
| **RP address** | 通告该 SA 的 RP（需与 `originator-id` 一致） | 不一致 → 对端丢弃 |
| **(S,G) 列表** | 一个 SA 可携带多个源组对 | SA 数 vs (S,G) 数不是一回事 |
| **Holdtime** | 该 SA 的有效期（默认 75 s，每 60 s 刷新） | 超时 → SA 消失 → 跨 RP 接收者建不了树 |
| **Encapsulated data** | 可选（首次注册时携带原始组播包） | 罕见 |

</div>

**How SAs are refreshed**: while the source stays active, the RP resends the SA every **60 seconds**. Therefore:

<div class="zh" markdown="1">

**SA 的刷新机制**：源持续活跃时，RP 每 **60 秒**重发 SA。所以：

</div>

```
SA "survival" depends on periodic refresh
-> if an MSDP peer flaps without dropping, the SA may "expire" and "reappear"
-> symptom: cross-RP receivers "briefly break roughly every 75 seconds"
```

<div class="zh" markdown="1">

```
SA 的"存活"依赖周期性刷新
→ 如果 MSDP peer 抖动但未断，SA 可能"过期丢失"又"重新出现"
→ 表现为跨 RP 的接收者"每 75 秒左右短暂中断一次"
```

</div>

> ⚠️ **This class of fault is extremely subtle**: cross-RP receivers "stall once a minute", yet `show ip msdp sa-cache` shows SAs when you look. The cause may be SA refreshes dropped by an ACL or CPU, or TCP window congestion on the peer. Check whether the SA send/receive counters in `show ip msdp peer` keep climbing.

<div class="zh" markdown="1">

> ⚠️ **这类故障非常隐蔽**：跨 RP 的接收者"隔一分钟卡一下"，`show ip msdp sa-cache` 看的时候又有 SA。原因可能是 SA 刷新被 ACL/CPU 丢弃，或 peer 的 TCP 窗口拥塞。检查：`show ip msdp peer` 的 SA 收发计数是否持续增长。

</div>

#### The MSDP RPF check rule (the root cause of "peer established but SA count is 0") · MSDP 的 RPF 检查规则（"peer 是 Established 但 SA 为 0"的根因）

When an RP receives an SA it performs the following checks (**the exact rules depend on the implementation and the `ip msdp rpf` setting**; Cisco offers several modes):

<div class="zh" markdown="1">

RP 收到一条 SA 时，做以下检查（**具体规则依实现与 `ip msdp rpf` 配置而变**，Cisco 有多种模式）：

</div>

| Check | Default (Cisco `ip msdp rpf rfc3618` style) | Consequence |
|------|------------------------------------------|------|
| **peer address vs the route to the RP** | the peer that advertised the SA must equal "the best next hop toward the RP address inside the SA" | mismatch → **the SA is dropped** (the most common failure) |
| **originator-id** | the RP address in the SA must be logically consistent with the peer's originator-id | mismatch → dropped |
| **is this our own SA** | SAs you advertised come back (split horizon) | must be filtered correctly |

<div class="zh" markdown="1">

| 检查 | 默认（Cisco `ip msdp rpf rfc3618` 等模式） | 后果 |
|------|------------------------------------------|------|
| **peer 地址 vs 到 RP 的路由** | 通告 SA 的 peer 地址必须等于"到 SA 中 RP 地址的最优下一跳" | 不一致 → **丢弃 SA**（最常见失败） |
| **originator-id** | SA 中的 RP 地址需与 peer 的 originator-id 逻辑一致 | 不一致 → 丢弃 |
| **SA 是否自己发的** | 自己通告的 SA 会回来（水平分割） | 需正确过滤 |

</div>

**The four `ip msdp rpf` modes**:

<div class="zh" markdown="1">

**四种 `ip msdp rpf` 模式的差异**：

</div>

| Mode | What is checked | Fit |
|------|---------|------|
| `rfc3618` (default) | the RPF neighbour toward the RP address in the SA == the peer address | standard, strictest |
| `mbgp` | RPF performed against the MBGP table | when the multicast path differs from unicast |
| `multicast` | RPF performed against the multicast RPF table | — |
| `pim` | RPF derived from the PIM neighbour relationship | special cases |

<div class="zh" markdown="1">

| 模式 | 检查对象 | 适用 |
|------|---------|------|
| `rfc3618`（默认） | 到 SA 中 RP 地址的 RPF 邻居 == peer 地址 | 标准、最严格 |
| `mbgp` | 用 MBGP 表做 RPF | 组播路径与单播不同 |
| `multicast` | 用组播 RPF 表 | — |
| `pim` | 用 PIM 邻居关系 | 特殊情况 |

</div>

**A typical fault and its repair**:

<div class="zh" markdown="1">

**典型故障与修复**：

</div>

```
Symptom: the MSDP peer is Established but sa-cache is 0
Cause: several paths exist between the two RPs; the SA arrives via path A, but the IGP
       says the best next hop toward the peer RP is the device on path B (not the peer address)
Repair (pick one):
 1. fix the IGP metric so the paths agree (best)
 2. peer on loopbacks and ensure route symmetry
 3. change the ip msdp rpf mode (e.g. mbgp), or use a mesh-group
```

<div class="zh" markdown="1">

```
现象：MSDP peer Established，sa-cache 为 0
原因：两台 RP 之间有多条路径，SA 从路径 A 来，但 IGP 认为到对端 RP 的
      最优下一跳是路径 B 的设备（不是 peer 地址）
修复（三选一）：
 ① 修正 IGP 度量，让路径一致（最佳）
 ② 用 loopback 建 peer 且保证路由对称
 ③ 调整 ip msdp rpf 模式（如 mbgp），或使用 mesh-group
```

</div>

#### MSDP Mesh Group (mandatory once you have three or more RPs) · MSDP Mesh Group（3 个以上 RP 时的必需品）

**Without a mesh group (full mesh)**:

<div class="zh" markdown="1">

**没有 mesh group 时（全互连）**：

</div>

```
3 RPs -> 3 peer connections
4 RPs -> 6
5 RPs -> 10
N RPs -> N×(N-1)/2 connections    <- quadratic growth
```

<div class="zh" markdown="1">

```
3 个 RP → 3 条 peer 连接
4 个 RP → 6 条
5 个 RP → 10 条
N 个 RP → N×(N-1)/2 条   ← 平方增长
```

</div>

**With a mesh group**:

<div class="zh" markdown="1">

**有了 mesh group**：

</div>

```
Every RP peers with one "reflection point", or they form a mesh group:
-> an SA arriving from any member reaches all other members, with NO duplicate forwarding
-> N RPs need only N connections (star) or N (full mesh inside the group)
```

<div class="zh" markdown="1">

```
所有 RP 与一个"反射点"建 peer，或组成 mesh 组：
→ SA 从任何成员进来，组内其他成员都收到，且【不重复转发】
→ N 个 RP 只需 N 条（星型）或 N 条（组内全互连）
```

</div>

```cfg
! star plus mesh-group (3 RPs, RP-1 at the centre)
! RP-2 and RP-3 peer only with RP-1 and join the same mesh group
ip msdp peer 1.1.1.1 connect-source Loopback1
ip msdp mesh-group MCAST-CORE 1.1.1.1

! RP-1 (the centre)
ip msdp peer 2.2.2.2 connect-source Loopback1
ip msdp peer 3.3.3.3 connect-source Loopback1
ip msdp mesh-group MCAST-CORE 2.2.2.2
ip msdp mesh-group MCAST-CORE 3.3.3.3
```

<div class="zh" markdown="1">

```cfg
! 星型 + mesh-group（3 台 RP，RP-1 为中心）
! RP-2 与 RP-3 只与 RP-1 建 peer，并加入同一个 mesh group
ip msdp peer 1.1.1.1 connect-source Loopback1
ip msdp mesh-group MCAST-CORE 1.1.1.1

! RP-1（中心）
ip msdp peer 2.2.2.2 connect-source Loopback1
ip msdp peer 3.3.3.3 connect-source Loopback1
ip msdp mesh-group MCAST-CORE 2.2.2.2
ip msdp mesh-group MCAST-CORE 3.3.3.3
```

</div>

**What a mesh group does**: **members do not forward SAs to each other** (avoiding loops and duplicates). Therefore:

<div class="zh" markdown="1">

**mesh group 的作用**：**组内成员之间不互相转发 SA**（避免环路与重复）。所以：

</div>

| Misconfiguration | Consequence |
|---------|------|
| some RPs in the mesh, some not | SAs loop / are duplicated between some RPs |
| inconsistent mesh group names | equivalent to not configuring it |
| star topology with the centre RP failing | **SAs cannot cross between branches** → every cross-RP receiver stops (so the centre must also be redundant) |

<div class="zh" markdown="1">

| 配置错误 | 后果 |
|---------|------|
| 部分 RP 加入 mesh，部分没加 | SA 在某些 RP 间循环 / 重复 |
| mesh group 名不一致 | 等同于没配 |
| 星型但中心 RP 故障 | **SA 无法跨分支传播** → 跨 RP 接收者全断（所以中心也要冗余） |

</div>

#### Administratively Scoped Zones · 管理范围

**The problem**: 239.0.0.0/8 is "private multicast", but **nothing in the protocol stops it crossing a domain**. Without a boundary, your 239.10.1.1 can leak into a neighbour's network and vice versa.

<div class="zh" markdown="1">

**问题**：239.0.0.0/8 是"私有组播"，但**协议层没有任何机制阻止它跨域**。如果不做边界，你的 239.10.1.1 可能泄漏到邻居网络，反之亦然。

</div>

**Two implementations**:

<div class="zh" markdown="1">

**两种实现**：

</div>

| Method | Mechanism | Advantages | Disadvantages |
|------|------|------|------|
| **`ip multicast boundary <acl>`** | filter group addresses on the interface | precise, per-interface control | must be configured per interface, easy to miss one |
| **TTL threshold (`ip multicast ttl-threshold`)** | do not forward when the TTL is below the threshold | coarse, no ACL needed | limits by hop count only, not by address |

<div class="zh" markdown="1">

| 方式 | 机制 | 优点 | 缺点 |
|------|------|------|------|
| **`ip multicast boundary <acl>`** | 在接口上过滤组地址 | 精确、按接口控制 | 需要每接口配，容易漏 |
| **TTL 阈值（`ip multicast ttl-threshold`）** | 组播包 TTL 低于阈值时不转发 | 粗粒度、无需 ACL | 只按"跳数"限制，不按地址 |

</div>

**An example of layered scope planning**:

<div class="zh" markdown="1">

**分层 scope 的规划示例**：

</div>

```
239.0.0.0/8
├── 239.1.0.0/16   site-internal (does not leave the site router)
├── 239.2.0.0/16   campus-internal (does not leave the campus boundary)
├── 239.3.0.0/16   enterprise-global (may cross the WAN)
└── 239.4.0.0/16   exchanged with partners (strict ACL + MSDP filtering)

Implementation: ip multicast boundary on the boundary interface of each tier, plus
                BSR/Auto-RP scope enforcement
```

<div class="zh" markdown="1">

```
239.0.0.0/8
├── 239.1.0.0/16   站点内部（不出站点路由器）
├── 239.2.0.0/16   园区内部（不出园区边界）
├── 239.3.0.0/16   企业全局（可跨 WAN）
└── 239.4.0.0/16   与合作伙伴交换（严格 ACL + MSDP 过滤）

实现：在每个层级的边界接口上配 ip multicast boundary + BSR/Auto-RP 的 scope
```

</div>

### MBGP in Depth: When It Is Genuinely Needed · MBGP 深入：什么时候真的需要它

| Scenario | MBGP needed? | Reason |
|------|------------|------|
| Single domain, single IGP path | **no** | unicast path = multicast path |
| Dual egress, multicast must use a specific exit | **yes** (or a static mroute) | unicast and multicast paths differ |
| Across carriers, multicast carried by carrier B | **yes** | you need a routing view "used only for RPF" |
| SSM across domains, source prefix reachable | **usually no** | plain unicast BGP already provides reachability |
| Multicast source inside a VPN (MVPN) | **no MBGP** | MVPN uses BGP's MVPN address family (SAFI 129) |

<div class="zh" markdown="1">

| 场景 | 需要 MBGP？ | 原因 |
|------|------------|------|
| 单域、IGP 单一路径 | **不需要** | 单播路径 = 组播路径 |
| 双出口，组播要走指定出口 | **需要**（或用静态 mroute） | 单播与组播路径不同 |
| 跨运营商，组播由运营商 B 承载 | **需要** | 需要一个"只给 RPF 用"的路由视图 |
| SSM 跨域，源前缀可达 | **通常不需要** | 单播 BGP 已提供可达性 |
| 组播源在 VPN 内（MVPN） | **不需要 MBGP** | MVPN 用 BGP 的 MVPN 地址族（SAFI 129） |

</div>

**MBGP's "two tables" model (the most misunderstood point)**:

<div class="zh" markdown="1">

**MBGP 的"两个表"模型（最容易误解的地方）**：

</div>

```
BGP maintains two RIBs at once:
  (1) IPv4 unicast RIB   -> used for unicast forwarding (into the FIB)
  (2) IPv4 multicast RIB -> used ONLY for the RPF check, never enters the unicast FIB

On the same router:
  unicast to 10.1.1.0/24 goes via ISP-A (cheaper)
  multicast RPF for 10.1.1.0/24 goes via ISP-B (better quality)
-> the two policies are independent and do not interfere
```

<div class="zh" markdown="1">

```
BGP 同时维护两个 RIB：
  ① IPv4 unicast RIB   → 用于单播转发（进 FIB）
  ② IPv4 multicast RIB → 【只用于 RPF 检查】，不进单播 FIB

同一台路由器：
  单播到 10.1.1.0/24 走 ISP-A（便宜）
  组播 RPF 到 10.1.1.0/24 走 ISP-B（质量好）
→ 两个策略各自独立，互不干扰
```

</div>

**Configuration points**:

<div class="zh" markdown="1">

**配置要点**：

</div>

```cfg
router bgp 65000
 address-family ipv4
  neighbor 203.0.113.1 activate
  neighbor 203.0.113.1 route-map UNICAST-IN in       ! unicast policy
 address-family ipv4 multicast
  neighbor 203.0.113.1 activate
  neighbor 203.0.113.1 route-map MCAST-IN in         ! multicast policy (different!)
  network 10.1.1.0 mask 255.255.255.0

! if MBGP is used for RPF, the RPF lookup must prefer the multicast table
! (platform default behaviour on most modern platforms)
```

<div class="zh" markdown="1">

```cfg
router bgp 65000
 address-family ipv4
  neighbor 203.0.113.1 activate
  neighbor 203.0.113.1 route-map UNICAST-IN in       ! 单播策略
 address-family ipv4 multicast
  neighbor 203.0.113.1 activate
  neighbor 203.0.113.1 route-map MCAST-IN in         ! 组播策略（不同！）
  network 10.1.1.0 mask 255.255.255.0

! 若用 MBGP 做 RPF，需要让 RPF 优先查组播表（平台默认行为，多数现代平台自动）
```

</div>

> ⚠️ **Three MBGP traps**:
> 1. **Forgetting to activate the neighbour under `ipv4 multicast`** → the multicast table is empty → RPF falls back to unicast (which looks fine but means "it never took effect")
> 2. **Different policies in the two address families cause "unicast works, multicast does not"** → the hardest class to diagnose (because `show ip route` is completely normal)
> 3. **RPF table selection is not always automatic** → some platforms need `ip multicast rpf select` or similar to state which table to use

<div class="zh" markdown="1">

> ⚠️ **MBGP 的三个陷阱**：
> 1. **忘记在 `ipv4 multicast` 下 activate 邻居** → 组播表为空 → RPF 退回单播（看似正常，实则是"没生效"）
> 2. **两个地址族的路由策略不一致导致"单播通、组播不通"** → 这是最难查的一类（因为 `show ip route` 完全正常）
> 3. **RPF 表的选择不是自动的** → 某些平台需要 `ip multicast rpf select` 或类似命令显式指定使用哪张表

</div>

### Multicast VPN (MVPN): Choosing Among Five Profiles · 组播 VPN（MVPN）：五种 profile 的选择

MPLS L3VPN does **not forward multicast by default** (PEs only exchange unicast VRF routes). To carry multicast across MPLS you must deploy MVPN.

<div class="zh" markdown="1">

MPLS L3VPN 默认**不转发组播**（PE 之间只有单播 VRF 路由）。要让组播穿越 MPLS，必须部署 MVPN。

</div>

| Profile | Mechanism | Data encapsulation | Control plane | Fit | Complexity |
|---------|------|---------|--------|------|--------|
| **Rosen (GRE, PIM-SM/GRE)** | the MDT (Multicast Distribution Tree) uses GRE tunnels, PIM runs between PEs | GRE over IP | PIM | traditional, good compatibility | medium |
| **Rosen mLDP (Profile 1)** | **mLDP (P2MP LSP)** as the MDT | P2MP LSP labels | BGP MVPN + mLDP | the modern mainstream | medium |
| **Rosen RSVP-TE P2MP (Profile 2)** | RSVP-TE P2MP LSP | LSP | BGP MVPN + RSVP-TE | when traffic engineering is required | high |
| **Partitioned MDT (Profile 3)** | several MDT partitions (reduces PE full mesh) | — | BGP MVPN | very large scale | high |
| **Default MDT vs Data MDT** | Default MDT carries all groups; Data MDT builds a separate tree for high-bandwidth groups | — | — | **mixing them is standard practice** | medium |
| **mVPN with BGP A-D (Profile 14 etc.)** | BGP auto-discovery (A-D routes) + selective trees (S-PMSI) | — | BGP MVPN | modern carriers | high |

<div class="zh" markdown="1">

| Profile | 机制 | 数据封装 | 控制面 | 适用 | 复杂度 |
|---------|------|---------|--------|------|--------|
| **Rosen（GRE，PIM-SM/GRE）** | MDT（Multicast Distribution Tree）用 GRE 隧道，PE 之间跑 PIM | GRE over IP | PIM | 传统、兼容性好 | 中 |
| **Rosen mLDP（Profile 1）** | 用 **mLDP（P2MP LSP）** 作为 MDT | P2MP LSP 标签 | BGP MVPN + mLDP | 现代主流 | 中 |
| **Rosen RSVP-TE P2MP（Profile 2）** | 用 RSVP-TE P2MP LSP | LSP | BGP MVPN + RSVP-TE | 需要流量工程 | 高 |
| **Partitioned MDT（Profile 3）** | 多个 MDT 分区（减少 PE 全互连） | — | BGP MVPN | 大规模 | 高 |
| **Default MDT vs Data MDT** | Default MDT 承载所有组；Data MDT 为高带宽组单独建树 | — | — | **混合使用是标准做法** | 中 |
| **mVPN with BGP A-D（Profile 14/各种）** | 用 BGP 自动发现（A-D route）+ 选择性树（S-PMSI） | — | BGP MVPN | 现代运营商 | 高 |

</div>

**Core concepts (you must be able to tell them apart)**:

<div class="zh" markdown="1">

**核心概念（必须分清）**：

</div>

| Concept | Meaning | Design implication |
|------|------|---------|
| **Default MDT (I-PMSI)** | the "default tunnel" every PE joins; carries all multicast (including low bitrate) | **simple, but every PE receives all multicast** → wasted bandwidth |
| **Data MDT (S-PMSI)** | a separate tree for high-bandwidth groups (only PEs with receivers) | **must be enabled**, otherwise high-bitrate multicast is replicated to every PE |
| **The PE's role** | PIM (or IGMP proxy) between PE and CE, MDT between PE and PE | the CE does not need to know about MPLS |
| **RP location** | on the customer side (CE) or the provider side (PE) | customer side: more autonomy; provider side: transparent to the customer |

<div class="zh" markdown="1">

| 概念 | 含义 | 设计含义 |
|------|------|---------|
| **Default MDT（I-PMSI）** | 所有 PE 都加入的"默认隧道"，承载所有组播（含低带宽） | **简单但会"全 PE 收到全部组播"** → 带宽浪费 |
| **Data MDT（S-PMSI）** | 为高带宽组单独建的树（只包含有接收者的 PE） | **必须启用**，否则高带宽组播会复制到所有 PE |
| **PE 的角色** | PE 与 CE 之间跑 PIM（或 IGMP proxy），PE 与 PE 之间用 MDT | CE 不需要知道 MPLS |
| **RP 的位置** | 可在客户侧（CE）或 provider 侧（PE） | 客户侧：更自主；provider 侧：客户无感 |

</div>

**Why "default MDT only" is a disaster**:

<div class="zh" markdown="1">

**为什么"只用 Default MDT"是灾难**：

</div>

```
Scenario: 100 PEs, one multicast group at 50 Mbps (IPTV)
With only the Default MDT:
  the source PE replicates 50 Mbps to 99 PEs (95 of which have no receivers at all)
  = 50 Mbps x 99 = 4.95 Gbps of useless traffic (across the carrier backbone!)
With a Data MDT:
  build trees only for the 4 PEs that really have receivers
  = 50 Mbps x 4 = 200 Mbps
```

<div class="zh" markdown="1">

```
场景：100 个 PE，其中一个组播 50 Mbps（IPTV）
Default MDT 下：
  源 PE 把 50 Mbps 复制给 99 个 PE（其中 95 个 PE 根本没有接收者）
  = 50 Mbps × 99 = 4.95 Gbps 的无效流量（跨运营商骨干！）
Data MDT 下：
  只为真正有接收者的 4 个 PE 建树
  = 50 Mbps × 4 = 200 Mbps
```

</div>

> 💡 **This is the most expensive form of "replication amplification" in multicast design**: not a few megabits wasted in the access layer, but **several gigabits wasted on a carrier backbone**. So in MVPN design the **Data MDT / S-PMSI threshold** (`mdt threshold`) is a key parameter: it often defaults to 1 kbps or is disabled, and must be set explicitly (e.g. 100 kbps).

<div class="zh" markdown="1">

> 💡 **这是组播设计里"复制放大"最贵的形态**：不是在接入层浪费几兆，而是在**运营商骨干上浪费几个 G**。所以 MVPN 设计中 **Data MDT / S-PMSI 的阈值**（`mdt mtu` / `mdt threshold`）是关键参数：默认常常是 1 kbps 或关闭，必须显式设定（如 100 kbps）。

</div>

```cfg
! Cisco MVPN (Profile 1, mLDP) key configuration
ip multicast-routing vrf CUST-A distributed
!
vrf definition CUST-A
 rd 65000:100
 address-family ipv4
  mdt default mpls p2mp                          ! mLDP as the default MDT
  mdt data 239.1.1.0 0.0.0.255 threshold 100     ! Data MDT: groups above 100 kbps get their own tree
  mdt data mpls p2mp
  route-target both 65000:100
```

<div class="zh" markdown="1">

```cfg
! Cisco MVPN（Profile 1，mLDP）关键配置示例
ip multicast-routing vrf CUST-A distributed
!
vrf definition CUST-A
 rd 65000:100
 address-family ipv4
  mdt default mpls p2mp                  ! 使用 mLDP 作为 default MDT
  mdt data 239.1.1.0 0.0.0.255 threshold 100   ! Data MDT：>100 kbps 的组单独建树
  mdt data mpls p2mp
  route-target both 65000:100
```

</div>

**Multicast inside EVPN/VXLAN (data-centre scenario)**:

<div class="zh" markdown="1">

**EVPN/VXLAN 中的组播（数据中心场景）**：

</div>

| Approach | Mechanism | Advantages | Disadvantages |
|------|------|------|------|
| **Ingress Replication** | the source VTEP replicates one unicast copy per VTEP that has receivers | no underlay multicast needed | **bandwidth amplified N times** (N = number of receiving VTEPs) |
| **Underlay multicast (PIM in the underlay)** | underlay multicast groups carry BUM traffic | one copy replicated to all VTEPs | underlay must support multicast; every VTEP joins (no selectivity) |
| **EVPN multicast (IGMP/MLD Snooping over EVPN, e.g. RFC 9251)** | group membership synchronised via EVPN routes, **trees built on demand** | most bandwidth-efficient and precise | complex; uneven vendor support |
| **Assisted replication** | designate a "replication server" | reduces load on the source | extra devices and design |

<div class="zh" markdown="1">

| 方案 | 机制 | 优点 | 缺点 |
|------|------|------|------|
| **Ingress Replication（入口复制）** | 源 VTEP 为每个有接收者的 VTEP 复制一份单播 | 无需 underlay 组播 | **带宽放大 N 倍**（N = 接收 VTEP 数） |
| **Underlay 组播（PIM in underlay）** | 用 underlay 组播组承载 BUM | 一份流量复制到所有 VTEP | 需要 underlay 支持组播；VTEP 都要加入（无选择） |
| **EVPN 组播（IGMP/MLD Snooping over EVPN，如 RFC 9251）** | 用 EVPN 路由同步组成员，**按需建树** | 最省带宽、精确 | 实现复杂、厂商支持不一 |
| ** assisted replication（辅助复制）** | 指定一台"复制服务器" | 减少源侧负担 | 需要额外设备与设计 |

</div>

**Selection guidance for data-centre multicast**:

<div class="zh" markdown="1">

**数据中心组播的选型建议**：

</div>

| Scenario | Recommendation |
|------|------|
| Little BUM traffic (< 1% of bandwidth), few VTEPs (< 20) | **Ingress Replication** is simplest |
| Heavy BUM traffic (storage, VDI broadcast, market-data multicast) | **underlay multicast** or **EVPN multicast** |
| Many VTEPs (> 50) | multicast or assisted replication is **mandatory** (replication amplification is unacceptable) |
| Across data centres | combine MVPN or direct DWDM |

<div class="zh" markdown="1">

| 场景 | 建议 |
|------|------|
| BUM 流量少（< 1% 带宽）、VTEP 数少（< 20） | **Ingress Replication** 最简单 |
| BUM 流量大（存储、VDI 广播、组播行情） | **Underlay 组播** 或 **EVPN 组播** |
| VTEP 数多（> 50） | **必须**用组播或 assisted replication（复制放大不可接受） |
| 跨数据中心 | 结合 MVPN 或 DWDM 直连 |

</div>

### Crossing Firewalls and IGMP Proxy · 跨防火墙与 IGMP Proxy

**The problem**: firewalls (especially stateful ones) do not support multicast by default, or only support it "one way":

<div class="zh" markdown="1">

**问题**：防火墙（尤其状态化防火墙）默认不支持组播，或者只支持"单向"：

</div>

| Firewall capability | Meaning | Design impact |
|-----------|------|---------|
| **No multicast support** | most traditional firewalls | you must tunnel through GRE, or use IGMP Proxy |
| **Supports IGMP Proxy** | one side acts as a "host" (sends Joins), the other as a "router" | the most common approach |
| **Supports PIM** | a few (some high-end firewalls) | PIM can run directly |
| **Stateful multicast inspection** | a few support "state" for UDP multicast | explicit policy required |

<div class="zh" markdown="1">

| 防火墙能力 | 说明 | 设计影响 |
|-----------|------|---------|
| **不支持组播** | 多数传统防火墙 | 必须用 GRE 隧道绕过，或用 IGMP Proxy |
| **支持 IGMP Proxy** | 一侧当"主机"（发 Join），一侧当"路由器" | 最常用的方案 |
| **支持 PIM** | 少数（如某些高端防火墙） | 可直接跑 PIM |
| **状态化检测组播** | 少数支持 UDP 组播的"状态" | 需要显式策略 |

</div>

**How IGMP Proxy works**:

<div class="zh" markdown="1">

**IGMP Proxy 的工作方式**：

</div>

```
internal network (has receivers)     firewall          external network (source/RP)
  host sends an IGMP Report   ->  downstream interface (proxy upstream)  ->  Join sent on the upstream interface
                                  ^ remembers "which groups are wanted"
```

<div class="zh" markdown="1">

```
内部网络（有接收者）       防火墙          外部网络（有源/RP）
  主机发 IGMP Report  →  下游接口（proxy 上游）  →  上游接口发 Join
                         ↑ 记住"哪个组有需求"
```

</div>

| Advantages | Disadvantages |
|------|------|
| only IGMP plus multicast data needs to be allowed, no PIM | **one-way dependency** (the downstream initiates, the upstream is passive) |
| state is controllable (auditable) | must be configured hop by hop across several firewalls |
| works reasonably with NAT | fast-leave and SSM support vary by implementation |

<div class="zh" markdown="1">

| 优点 | 缺点 |
|------|------|
| 只放通 IGMP + 组播数据，不需要 PIM | **单向依赖**（下游主动，上游被动） |
| 状态可控（可审计） | 跨多个防火墙时需逐段配置 |
| 与 NAT 配合较好 | 快速离开、SSM 支持依实现而异 |

</div>

**Four hard rules for firewall-crossing design**:

<div class="zh" markdown="1">

**跨防火墙设计的四条硬规则**：

</div>

1. **IGMP must be allowed in both directions** (Reports upstream, Queries downstream) — allowing only Reports gives "it joins, then ages out quickly"
2. **Multicast data only needs one direction** (source → receiver), but **that direction is the opposite of the Join direction**
3. **SSM across a firewall requires the firewall to understand IGMPv3** (otherwise the source filtering is lost → it degrades to ASM → an RP must be reachable)
4. **PIM Register (unicast encapsulation) requires protocol 103 and the UDP encapsulation to be allowed** (when SM is used)

<div class="zh" markdown="1">

1. **IGMP 必须双向放通**（Report 上行、Query 下行）—— 只放 Report 会导致"能加入但很快老化"
2. **组播数据流只需单向**（源→接收者），但**方向必须与 Join 方向相反**
3. **SSM 跨防火墙需要防火墙理解 IGMPv3**（否则源过滤信息丢失 → 退化为 ASM → 需要 RP 可达）
4. **PIM Register（单播封装）需要放通协议 103 与 UDP 封装**（如果用 SM）

</div>

> ⚠️ **The firewall root cause of "new channels will not open, old channels are fine"**: the IGMP Proxy state table on the firewall has a **maximum entry count**, and **a new group's Join needs new state**. If the table is full (because the old channels always have viewers and their state is never released), new channels can never be built. **This is the textbook case of "looks like a multicast problem, is really a firewall capacity problem".**

<div class="zh" markdown="1">

> ⚠️ **"新频道打不开、老频道正常"在防火墙场景下的根因**：防火墙上的 IGMP Proxy 状态表有**最大条目数**，且**新组的 Join 需要新的状态**。如果表满（因为老频道一直有人看、状态不释放），新频道就永远建不起来。**这是"看起来像组播问题、实际是防火墙容量问题"的典型案例。**

</div>

---

## Advanced Multicast Design · 高级组播设计

### Live-Live (Dual-Active Multicast) · Live-Live（双活组播）

**Goal**: when one path fails the receiver **notices nothing** (no dropped frames, no re-join).

<div class="zh" markdown="1">

**目标**：一条路径故障时，接收者**无感知**（不丢帧、不重新加入）。

</div>

**Mechanism**: the source sends **the same content on two independent paths, on two different group addresses**; the receiver **joins both groups**, receives both streams, and the application (or decoder) selects or merges them.

<div class="zh" markdown="1">

**机制**：源同时通过**两条独立路径**发送**同一内容但不同组地址**的流；接收者**同时加入两个组**，两个流都收到，由应用层（或解码器）选择/合并。

</div>

| Requirement | Explanation |
|------|------|
| **Two paths** | two **physically non-overlapping** paths (different fibre, different devices, different carriers) |
| **Independent RPs** (when SM is used) | a separate RP per path, avoiding a shared single point |
| **Unique group addresses** | one group per leg (e.g. 239.10.1.1 and 239.10.1.2) |
| **Multi-join receivers** | terminals must join both groups simultaneously (or use two NICs) |
| **Clock/sequence alignment** | the two streams must be comparable (RTP sequence numbers/timestamps) |

<div class="zh" markdown="1">

| 要求 | 说明 |
|------|------|
| **双路径** | 两条**物理不重叠**的路径（不同光纤、不同设备、不同运营商） |
| **独立 RP**（若用 SM） | 每条路径独立 RP，避免共享单点 |
| **唯一组地址** | 每路一个组（如 239.10.1.1 与 239.10.1.2） |
| **接收者多加入** | 终端必须支持同时加入两个组（或双网卡） |
| **时钟/序列对齐** | 两路流需可比较（RTP 序列号/时间戳） |

</div>

**The biggest failure mode**: **two paths that are "logically independent but physically shared"**. For example both links run through the same cable, the same duct, the same optical transport device — one digger cuts both. **The value of Live-Live depends 100% on physical path independence**, and this must be drawn in the design document as a **physical route** (not a logical topology).

<div class="zh" markdown="1">

**最大的失败模式**：**两条路径"逻辑上独立、物理上共享"**。例如两条链路走同一根光缆、同一个管道、同一台传输设备 —— 挖断一次两根全断。**Live-Live 的价值 100% 取决于路径的物理独立性**，这一点必须在设计文档里画出物理路由（而不是逻辑拓扑）。

</div>

| Scenario | Is Live-Live a fit |
|------|-------------------|
| Financial market-data distribution (millisecond, zero loss) | ★★★★★ |
| Broadcast TV / live sports | ★★★★☆ |
| Ordinary enterprise video conferencing | ★★☆☆☆ (too expensive; SSM + QoS is enough) |
| CCTV video | ★☆☆☆☆ (recording can backfill) |

<div class="zh" markdown="1">

| 场景 | 是否适合 Live-Live |
|------|-------------------|
| 金融行情分发（毫秒级、不能丢） | ★★★★★ |
| 广播电视/赛事直播 | ★★★★☆ |
| 普通企业视频会议 | ★★☆☆☆（成本过高，用 SSM + QoS 即可） |
| 监控视频 | ★☆☆☆☆（可用录制回补） |

</div>

#### The technical implementation layers of Live-Live (it is not simply "send it twice") · Live-Live 的技术实现层次（不是"发两份"这么简单）

| Layer | Approach | Advantages | Disadvantages |
|------|------|------|------|
| **Application-level dual send** | the application sends two copies to two groups and the receiver picks one | simple, network-agnostic | the receiver must be modified; switching may not be seamless |
| **ST 2022-7 (seamless protection switching, SMPTE)** | RTP streams replicated onto two paths; the receiver **de-duplicates and merges by RTP sequence number** | **zero-loss switching** (the industry standard) | needs 2022-7 capable senders/receivers |
| **FEC (forward error correction)** | send redundant check packets (e.g. ST 2022-1 1D/2D FEC) | recovers a certain amount of loss (no second path needed) | adds 10–50% bandwidth; only recovers limited loss |
| **AL-FEC / Raptor** | more efficient channel coding | high recovery rate, low overhead | requires terminal support |
| **Application retransmission (NACK/RTX)** | the receiver requests a retransmission | bandwidth-efficient | **unusable for latency-sensitive services** (retransmission is too slow) |

<div class="zh" markdown="1">

| 层次 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| **应用层双发** | 应用自己发两份到两个组，接收端自己选 | 简单、与网络无关 | 接收端要改；切换可能不连续 |
| **ST 2022-7（无缝保护切换，SMPTE）** | RTP 流复制到两条路径，接收端按 RTP 序列号**去重合并** | **零丢包切换**（业界标准） | 需要支持 2022-7 的发送/接收设备 |
| **FEC（前向纠错）** | 发冗余校验包（如 ST 2022-1 的 1D/2D FEC） | 可恢复一定丢包（不需双路径） | 增加带宽 10–50%；只能恢复有限丢包 |
| **AL-FEC / Raptor** | 更高效的信道编码 | 恢复率高、开销低 | 需要终端支持 |
| **应用层重传（NACK/RTX）** | 接收端请求重传 | 省带宽 | **时延敏感业务不可用**（重传太慢） |

</div>

**The core mechanism of ST 2022-7 (exam-level understanding)**:

<div class="zh" markdown="1">

**ST 2022-7 的核心机制（必考级理解）**：

</div>

```
Sender: copies the same RTP stream onto two independent paths (two group addresses / two destination ports)
        every packet carries the same RTP sequence number and SSRC

Receiver: maintains a "reorder buffer"
          packets from both streams enter the buffer, de-duplicated and reordered by sequence number
          whichever arrives first is used (seamless switching)
          if the differential delay between paths exceeds the buffer depth -> "waiting" (added latency)

Key parameters:
  - differential delay: the latency difference between the two paths
  - buffer depth must exceed the differential delay, otherwise packets are wrongly judged lost
```

<div class="zh" markdown="1">

```
发送端：把同一个 RTP 流复制到两条独立路径（两个组地址 / 两个目的端口）
       每个包带相同的 RTP 序列号与 SSRC

接收端：维护"重排序缓冲（reorder buffer）"
       两个流的包都进缓冲，按序列号去重、排序
       谁先到用谁（无缝切换）
       如果一条路径延迟差 > 缓冲深度 → 会出现"等待"（增加时延）

关键参数：
  - 路径差分延迟（differential delay）：两条路径的时延差
  - 缓冲深度必须 > 差分延迟，否则会误判丢包
```

</div>

| Key ST 2022-7 constraint | Explanation |
|---------------------|------|
| **The differential delay between paths must be stable** | if one path's latency fluctuates, the buffer must be deeper → end-to-end latency increases |
| **The two paths must be genuinely independent** | see case 7 (shared physical route = fake redundancy) |
| **Group addresses must differ** | otherwise the receiver cannot tell them apart |
| **The receiver must support it** | this is the last mile of the whole scheme (many players do not) |

<div class="zh" markdown="1">

| ST 2022-7 的关键约束 | 说明 |
|---------------------|------|
| **两条路径的差分延迟要稳定** | 如果一条路径时延波动大，接收端缓冲要加深 → 端到端时延增加 |
| **两条路径必须真正独立** | 见案例七（物理路由共享 = 假冗余） |
| **组地址必须不同** | 否则接收端无法区分 |
| **接收端必须支持** | 这是整个方案的"最后一公里"（很多播放器不支持） |

</div>

#### The cost-benefit calculation for Live-Live (design decisions must be quantified) · Live-Live 的成本-收益计算（设计决策必须量化）

```
Cost of one minute of service interruption: C
Annual failure probability (single path): P1 (e.g. 0.5 per year)
Failure probability with Live-Live: P2 = P1 x P(both paths fail simultaneously)

If the two paths are fully independent: P2 ≈ P1 x P1 = 0.25 per year
   (0.5 -> 0.25 per year; the benefit is limited!)
If the two paths share one point (e.g. the same duct): P2 ≈ P1 (no benefit at all)
If three paths are independent: P3 = P1³ = 0.125 per year

Conclusion:
 (1) the benefit of "single path -> dual path" depends on "path independence", not on "number of paths"
 (2) the benefit of dual paths is often smaller than expected (0.5 -> 0.25 per year)
 (3) the real benefit is "no perception during failure" (no dropped frames), not "failure probability"
```

<div class="zh" markdown="1">

```
业务中断 1 分钟的成本：C
年故障概率（单路）：P1（如 0.5 次/年）
Live-Live 后故障概率：P2 = P1 × P(两条路径同时故障)

若两条路径完全独立：P2 ≈ P1 × P1 = 0.25 次/年（0.5 次 → 0.25 次，收益有限！）
若两条路径共享一处（如同沟）：P2 ≈ P1（完全没有收益）
若三条路径独立：P3 = P1³ = 0.125 次/年

结论：
 ① 单路 → 双路的收益，取决于"路径独立性"而不是"路径条数"
 ② 双路的收益往往小于预期（从 0.5 次/年降到 0.25 次/年）
 ③ 真正的收益在于"故障时无感"（不丢帧），而不是"故障概率"
```

</div>

> 💡 **What that calculation really means**: if the business requirement is "**it must never stop**", Live-Live is necessary (because it turns "interruption" into "seamless switch"); if the requirement is "**reduce the failure probability**", Live-Live is far worse value than "improve single-path reliability (dual power, dual supervisors, redundant links) + fast convergence". **These two requirements are easily confused.**

<div class="zh" markdown="1">

> 💡 **这段计算的真正含义**：如果业务要求是"**不能中断**"，那么 Live-Live 是必要的（因为它把"中断"变成"无感切换"）；如果业务要求是"**降低故障概率**"，那么 Live-Live 的性价比远低于"提升单路可靠性（双电源、双引擎、冗余链路）+ 快速收敛"。**这两个需求容易被混为一谈。**

</div>

### QoS Design for Multicast (end to end; one missing segment and it fails) · 组播的 QoS 设计（端到端，缺一段就失效）

**Multicast QoS is harder than unicast because**:

<div class="zh" markdown="1">

**组播的 QoS 比单播更难，原因**：

</div>

| Difficulty | Explanation |
|------|------|
| Traffic is **aggregated** | one link may carry hundreds of groups; you cannot rate-limit "per session" |
| **No reverse feedback** | you cannot adapt from receiver feedback (no TCP) |
| **Replication happens in the middle** | one packet upstream may become N packets downstream (congestion after amplification) |
| **Layer 2 flooding breaks QoS assumptions** | without snooping, access-layer bandwidth is instantly saturated and no QoS queue can save it |

<div class="zh" markdown="1">

| 难点 | 说明 |
|------|------|
| 流量是"聚合"的 | 一条链路上可能有上百个组，无法按"单个会话"限速 |
| 没有反向反馈 | 无法根据接收者反馈调整（无 TCP） |
| 复制发生在中间 | 上游一个包，下游可能变成 N 个包（带宽放大后的拥塞） |
| 二层泛洪会突破 QoS 假设 | 未开 Snooping 时，接入层带宽被瞬间打满，QoS 队列也救不了 |

</div>

**The five layers of multicast QoS**:

<div class="zh" markdown="1">

**组播 QoS 的五个层次**：

</div>

| Layer | Measure | Key point |
|------|------|--------|
| **① Classification and marking** | set **DSCP** at the source or on the FHR (e.g. 46 EF / 34 AF41) | **multicast packets usually inherit the source's DSCP (often 0)** → you must re-mark at the network edge |
| **② Ingress trust** | `mls qos trust dscp` on access ports (if the terminal is trustworthy) or re-mark with a `policy-map` | never trust uncontrollable terminals |
| **③ Queuing** | put multicast into a **priority queue/LLQ** or a dedicated queue | putting video into LLQ can starve signalling; a dedicated bandwidth queue (e.g. 30%) is preferable |
| **④ Congestion management** | queue length, WRED (for UDP multicast) | too long → jitter; too short → loss |
| **⑤ Shaping/policing** | a `policer` at the source, `shaping` at domain edges | prevents "one source saturating the link" |

<div class="zh" markdown="1">

| 层次 | 措施 | 关键点 |
|------|------|--------|
| **① 分类标记** | 源侧或 FHR 打 **DSCP**（如 46 EF / 34 AF41） | **组播包默认 DSCP 往往继承源（常是 0）** → 必须在网络入口重标记 |
| **② 入口信任** | 接入口 `mls qos trust dscp`（若终端可靠）或 `policy-map` 重标记 | 不能信任不可控终端 |
| **③ 排队** | 组播进 **优先队列/LLQ** 或独立队列 | 视频流放 LLQ 可能饿死信令；建议独立带宽队列（如 30%） |
| **④ 拥塞管理** | 队列长度、WRED（对 UDP 组播） | 队列太长 → 时延抖动；太短 → 丢包 |
| **⑤ 整形/限速** | 源侧 `policer`、跨域边界 `shaping` | 防"一个源打满链路" |

</div>

```cfg
! example multicast QoS on a critical link (core <-> aggregation)
class-map match-any MCAST-VIDEO
 match access-group name MCAST-VIDEO-ACL
class-map match-any MCAST-SIGNAL
 match dscp cs3

policy-map WAN-OUT
 class MCAST-VIDEO
  priority percent 35                    ! video multicast: guaranteed dedicated bandwidth
 class MCAST-SIGNAL
  bandwidth percent 5
 class class-default
  fair-queue

interface Gi0/0
 service-policy output WAN-OUT

! multicast address matching
ip access-list extended MCAST-VIDEO-ACL
 permit ip any 239.10.0.0 0.0.255.255
```

<div class="zh" markdown="1">

```cfg
! 关键业务链路（核心/汇聚之间）的组播 QoS 示例
class-map match-any MCAST-VIDEO
 match access-group name MCAST-VIDEO-ACL
class-map match-any MCAST-SIGNAL
 match dscp cs3

policy-map WAN-OUT
 class MCAST-VIDEO
  priority percent 35                    ! 视频组播：独立带宽保证
 class MCAST-SIGNAL
  bandwidth percent 5
 class class-default
  fair-queue

interface Gi0/0
 service-policy output WAN-OUT

! 组播地址匹配
ip access-list extended MCAST-VIDEO-ACL
 permit ip any 239.10.0.0 0.0.255.255
```

</div>

**Three design flaws in multicast QoS**:

<div class="zh" markdown="1">

**组播 QoS 的三个设计缺陷**：

</div>

1. **QoS configured on only one link**: if any segment of the multicast path (including Layer 2, tunnels and wireless) lacks it → end-to-end failure. **QoS is a whole-path consistency design.**
2. **Carrying high-bitrate multicast in LLQ**: the LLQ policer drops traffic above the limit, and multicast has no retransmission → pixellation. **High-bitrate multicast needs a dedicated queue with guaranteed bandwidth, not LLQ.**
3. **Multicast sharing a queue with unicast**: unicast TCP bursts push multicast out of the queue (TCP fills the buffer) → **multicast must have its own queue**.

<div class="zh" markdown="1">

1. **只在一段链路配了 QoS**：组播路径上的任何一段（含二层、含隧道、含无线）没配 → 端到端失效。**QoS 是全路径一致性设计。**
2. **用 LLQ 承载大流量组播**：LLQ 的 policer 会丢超限流量，而组播丢包无重传 → 花屏。**大流量组播应给"有保证带宽的独立队列"，而不是 LLQ。**
3. **组播与单播共享队列**：单播 TCP 的突发会把组播挤出队列（因为 TCP 会填满缓冲区）→ **组播必须独立队列**。

</div>

> ⚠️ **Microbursts are the hidden killer of multicast**: market-data multicast (small packets, high rate) looks like "only 5% of a 1 Gbps link", yet instantaneous bursts can fill the port buffer → loss. **The fix is port buffer depth + queue scheduling + burst tolerance, not "more bandwidth".**

<div class="zh" markdown="1">

> ⚠️ **微突发（Microburst）是组播丢包的隐藏杀手**：行情类组播（小包、高速率）在 1 Gbps 链路上看似"只用了 5%"，但瞬时突发可能打满端口缓存 → 丢包。**解决：端口缓存深度 + 队列调度 + 增大 burst 容忍**，而不是"加带宽"。

</div>

### Multicast Security (defence in depth) · 组播安全（纵深防御）

| Layer | Threat | Protection |
|----|------|---------|
| **Access layer** | illegal IGMP (forged Query/mrouter/mass Joins) | interface ACLs blocking 224.0.0.1/224.0.0.13, `ip igmp limit`, static mrouter |
| **Access layer** | illegal sources sending multicast (a host streams directly) | **first-hop filtering** (a reversed `ip multicast boundary`, allowing sends only from the source subnet) |
| **PIM layer** | forged PIM Hellos (stealing DR, flooding) | **PIM neighbour authentication (MD5/SHA)**, interface ACLs blocking 224.0.0.13 |
| **PIM layer** | illegal Joins (pulling traffic that should not be sent) | `ip multicast boundary` to restrict group ranges |
| **RP layer** | registration storms, forged Registers | `ip pim register-rate-limit`, ACLs on the RP |
| **MSDP layer** | SA injection, memory exhaustion | `sa-filter in/out`, `sa-limit`, MD5, peer ACLs |
| **RP mapping layer** | forged Auto-RP/BSR (RP hijacking) | **Auto-RP/BSR scope ACLs + TTL**, `ip pim bsr-border` |
| **Data layer** | multicast eavesdropping (joining someone else's group) | **SSM (source whitelist)**, encryption (application layer), multicast VLAN isolation |
| **Data layer** | multicast forwarded where it should not go | `ip multicast boundary` + TTL thresholds |
| **Management plane** | configuration tampering | configuration audit + automated baseline (see Chapter 12) |

<div class="zh" markdown="1">

| 层 | 威胁 | 防护措施 |
|----|------|---------|
| **接入层** | 非法 IGMP（伪造 Query/mrouter/大量 Join） | 接口 ACL 拦 224.0.0.1/224.0.0.13、`ip igmp limit`、静态 mrouter |
| **接入层** | 非法源发组播（主机直接发流） | **首跳过滤**（`ip multicast boundary` 反向 + 只允许"源所在网段"发包） |
| **PIM 层** | 伪造 PIM Hello（抢 DR、注水） | **PIM 邻居认证（MD5 / SHA）**、接口 ACL 拦 224.0.0.13 |
| **PIM 层** | 非法 Join（拉走不该给的流量） | `ip multicast boundary` 限制组范围 |
| **RP 层** | 注册风暴、伪造 Register | `ip pim register-rate-limit`、RP 的 ACL |
| **MSDP 层** | SA 注入、内存耗尽 | `sa-filter in/out`、`sa-limit`、MD5、peer ACL |
| **RP 映射层** | 伪造 Auto-RP/BSR（劫持 RP） | **Auto-RP/BSR 的 scope ACL + TTL**、`ip pim bsr-border` |
| **数据层** | 组播被窃听（加入别人的组） | **SSM（源白名单）**、加密（应用层）、组播 VLAN 隔离 |
| **数据层** | 组播被转发到不该去的地方 | `ip multicast boundary` + TTL 阈值 |
| **管理面** | 配置被改 | 配置审计 + 自动化基线（见第 12 章） |

</div>

```cfg
! PIM neighbour authentication (anti-forged Hello)
interface Gi0/0
 ip pim sparse-mode
 ip pim hello-interval 30000
 ip pim authentication mode md5 key-chain PIM-KEY

key chain PIM-KEY
 key 1
  key-string 7 <encrypted>

! first-hop filtering (on the FHR, only legitimate source subnets may send multicast)
interface Gi0/1                       ! source-facing interface
 ip multicast boundary SRC-ONLY
ip access-list standard SRC-ONLY
 permit 10.1.1.0 0.0.0.255
```

<div class="zh" markdown="1">

```cfg
! PIM 邻居认证（防伪造 Hello）
interface Gi0/0
 ip pim sparse-mode
 ip pim hello-interval 30000
 ip pim authentication mode md5 key-chain PIM-KEY

key chain PIM-KEY
 key 1
  key-string 7 <encrypted>

! 首跳过滤（FHR 上只允许合法源网段发组播）
interface Gi0/1                       ! 面向源的接口
 ip multicast boundary SRC-ONLY
ip access-list standard SRC-ONLY
 permit 10.1.1.0 0.0.0.255
```

</div>

> ⚠️ **Deployment order for PIM authentication: enable it network-wide at the same time.** With authentication configured on only one side the adjacency never comes up → all multicast stops. **It is an all-or-nothing configuration**, which must be rolled out by automation in sync (see Chapter 12). This is the textbook example of "configuration consistency is harder than configuration correctness".

<div class="zh" markdown="1">

> ⚠️ **PIM 认证的部署顺序**：**全网同时启用**。如果只在一侧配了认证，邻居建立不起来 → 组播全断。**这是一个"要么全有、要么全无"的配置**，必须用自动化同步下发（见第 12 章）。这是"配置一致性比配置正确性更难"的典型例子。

</div>

### Ten Best Practices for the Source Side (FHR) · 源侧（FHR）的十项最佳实践

The source side is the "starting point" of multicast and the most neglected part (because everyone focuses on the network):

<div class="zh" markdown="1">

源侧是组播的"起点"，也是最容易被忽略的地方（因为大家把注意力放在网络上）：

</div>

| # | Practice | Reason |
|---|------|------|
| 1 | **Plan a dedicated source interface** (dedicated VLAN/subnet) | makes first-hop filtering and rate limiting easy |
| 2 | **Run PIM on the FHR** (the source's gateway must be the FHR) | otherwise nobody registers the source traffic |
| 3 | **Rate limit at the source (policer)** | stops an application bug from saturating the network |
| 4 | **Mark DSCP at the source** | multicast DSCP is often 0 by default |
| 5 | **Converge MTU at the source** (avoid IP fragmentation) | fragmented multicast is not correctly forwarded on many devices |
| 6 | **Set TTL at the source** | limits the multicast propagation range (application TTL combined with the network) |
| 7 | **Source high availability (dual-active/active-standby)** | source failure = service outage (the network cannot repair it) |
| 8 | **The source address must not change** (it breaks SSM) | use a loopback/virtual address as the source |
| 9 | **Enable NetFlow/sampling at the source side** | the first thing to check when something breaks is "is the source really sending" |
| 10 | **Time-synchronise source and application (NTP)** | required for cross-device log correlation |

<div class="zh" markdown="1">

| # | 实践 | 原因 |
|---|------|------|
| 1 | **源接口单独规划**（专用 VLAN/网段） | 便于做首跳过滤与限速 |
| 2 | **FHR 上开 PIM**（源的网关必须是 FHR） | 否则源流量无人注册 |
| 3 | **源侧限速（policer）** | 防应用 Bug 打满全网 |
| 4 | **源侧打 DSCP** | 组播默认 DSCP 常为 0 |
| 5 | **源侧 MTU 收敛**（避免 IP 分片） | 分片组播在很多设备上不被正确转发 |
| 6 | **源的 TTL 设定** | 限制组播传播范围（应用层 TTL 与网络层配合） |
| 7 | **源的高可用（双活/主备）** | 源故障 = 业务中断（网络无法恢复） |
| 8 | **源地址不能变**（SSM 下变了就断） | 用 loopback/虚拟地址做源 |
| 9 | **源侧开启 NetFlow/采样** | 出问题第一个要看"源真的在发吗" |
| 10 | **源与应用的时间同步（NTP）** | 跨设备日志关联必需 |

</div>

> ⚠️ **A real "source-side trap"**: the application server has **two NICs** (one for business, one for multicast) and the multicast NIC's gateway is not the FHR (or there is no gateway). The source sends at full speed, but **the FHR never learns that this source exists** → the multicast is never registered. **This is the classic "the source never entered the network" case in multicast troubleshooting.**

<div class="zh" markdown="1">

> ⚠️ **一个真实的"源侧陷阱"**：应用服务器用**两个网卡**（一个业务、一个组播），组播网卡的网关不是 FHR（或没配网关）。结果源发得飞快，但**FHR 根本不知道有这个源** → 组播从未注册。**这是"组播不通"排查中"源头就没进网络"的典型。**

</div>

### Multicast Convergence and Switchover Design (a time budget table) · 组播的收敛与切换设计（时间预算表）

| Failure type | Detection mechanism | Detection time | Recovery action | End-to-end interruption (experience) |
|---------|---------|---------|---------|-------------------|
| **Link down** | interface down / BFD | < 1 s (BFD 50 ms × 3) | IGP converges → the multicast tree rebuilds | 1–5 s |
| **PIM neighbour failure (device reboot)** | Hello holdtime 105 s (default) | 105 s | neighbour cleared → re-election | **105 s+** |
| **RP failure (anycast)** | IGP + BFD | < 1 s | routing moves to the standby RP | 1–3 s (with an SA cache) |
| **RP failure (single RP)** | — | — | none | **permanent** (for new groups) |
| **RP failure (phantom)** | IGP convergence | seconds | routing moves to the standby RP | 5–30 s |
| **Unidirectional link / asymmetry** | none (BFD or a protocol is needed) | not automatic | none | **persistent failure** |
| **Layer 2 snooping table expiry** | none | — | Querier queries rebuild it | periodic interruption (every 260 s) |
| **Source switchover (dual-active)** | application layer | — | the new source sends → a new (S,G) | depends on the application |
| **SPT switchover** | triggered | — | build (S,G) + Prune the RPT | milliseconds to hundreds of ms (possible loss) |

<div class="zh" markdown="1">

| 故障类型 | 检测机制 | 检测时间 | 恢复动作 | 端到端中断（经验值） |
|---------|---------|---------|---------|-------------------|
| **链路断开** | 接口 down / BFD | < 1 s（BFD 50 ms×3） | IGP 收敛 → 组播树重建 | 1–5 s |
| **PIM 邻居故障（设备重启）** | Hello holdtime 105 s（默认） | 105 s | 邻居清除 → 重新选举 | **105 s+** |
| **RP 故障（Anycast）** | IGP + BFD | < 1 s | 路由切到备用 RP | 1–3 s（有 SA 缓存） |
| **RP 故障（单 RP）** | — | — | 无 | **永久**（新组） |
| **RP 故障（Phantom）** | IGP 收敛 | 数秒 | 路由切到备 RP | 5–30 s |
| **单向链路 / 非对称** | 无（需 BFD 或协议） | 无法自动 | 无 | **持续故障** |
| **二层 Snooping 表过期** | 无 | — | Querier 查询重建 | 周期性中断（每 260 s） |
| **源切换（双活源）** | 应用层 | — | 新源发流 → 新 (S,G) | 取决于应用 |
| **SPT 切换** | 触发式 | — | 建 (S,G) + Prune RPT | 毫秒–百毫秒（可能丢包） |

</div>

**Design implication (turn the table above into requirements)**:

<div class="zh" markdown="1">

**设计含义（把上表变成要求）**：

</div>

| Service | Allowed interruption | Design that must be in place |
|------|---------|-------------|
| Ordinary enterprise video | 30 s | fast IGP convergence (BFD) + Snooping Querier |
| IPTV | 2 s (channel change) / 10 s (failure) | SSM + FCC + fast convergence + RP redundancy |
| Market data | **0 (imperceptible)** | **Live-Live (ST 2022-7)** + strict QoS |
| Conferencing | 5 s | BiDir + FHRP-Aware PIM + QoS |

<div class="zh" markdown="1">

| 业务 | 允许中断 | 必须做的设计 |
|------|---------|-------------|
| 普通企业视频 | 30 s | 快速 IGP 收敛（BFD）+ Snooping Querier |
| IPTV | 2 s（换台）/ 10 s（故障） | SSM + FCC + 快速收敛 + RP 冗余 |
| 行情 | **0（无感）** | **Live-Live（ST 2022-7）** + 严格 QoS |
| 会议 | 5 s | BiDir + FHRP-Aware PIM + QoS |

</div>

> 💡 **One-sentence summary**: **"fast convergence" solves "second-level" problems; it cannot solve "imperceptible" requirements.** "Imperceptible" only comes from "redundancy + parallel dual paths", never from "converging faster".

<div class="zh" markdown="1">

> 💡 **一句话总结**：**"快速收敛"能解决"秒级"问题，解决不了"无感"需求。** 要"无感"只能靠"冗余 + 双路并行"，不能靠"收敛更快"。

</div>

### FHRP-Aware PIM

**The problem**: when the access gateway uses HSRP/VRRP, only the **Active** router forwards multicast. After a failover to Standby, the new Active **has no (S,G) state** and must re-send Joins and rebuild the tree → multicast is interrupted (hundreds of milliseconds to seconds).

<div class="zh" markdown="1">

**问题**：接入网关用 HSRP/VRRP 时，只有 **Active** 路由器转发组播。Active 故障切换到 Standby 后，新 Active **没有 (S,G) 状态**，必须重新发 Join、重新建树 → 组播中断（几百毫秒到数秒）。

</div>

**What FHRP-Aware PIM does**: it lets the Standby **maintain PIM state in advance** (receiving Joins, keeping the outgoing interface list), so it can forward immediately after the switch.

<div class="zh" markdown="1">

**FHRP-Aware PIM 的做法**：让 Standby 也**预先维护** PIM 状态（接收 Join/维持出接口），切换时立刻能转发。

</div>

| Feature | Explanation |
|------|------|
| **Eliminates Join churn at switchover** | the Standby already holds state, so nothing must be rebuilt |
| **Synchronised with FHRP switchover** | convergence equals the FHRP time (usually < 1 s) |
| **Supports HSRP v2 / VRRP** | IPv4 and IPv6 |
| **Preconditions** | both routers on the same LAN, both running PIM, matching configuration |

<div class="zh" markdown="1">

| 特性 | 说明 |
|------|------|
| **消除切换时的 Join 抖动** | Standby 已有状态，无需重建 |
| **与 FHRP 切换同步** | 收敛时间取决于 FHRP（通常 < 1 s） |
| **支持 HSRP v2 / VRRP** | IPv4/IPv6 |
| **前提** | 两台路由器都在同一 LAN、都跑 PIM、配置匹配 |

</div>

> ⚠️ **Watch the interaction between FHRP and the IGMP Querier**: the IGMP querier election (lowest IP) may not be the same device as the HSRP Active. If the Querier sits on the Standby while forwarding is on the Active, confirm that snooping's mrouter points at the right port — otherwise "join requests go to the device that does not forward".

<div class="zh" markdown="1">

> ⚠️ **注意 FHRP + IGMP Querier 的关系**：IGMP 查询器选举（最低 IP）与 HSRP Active 可能不是同一台设备。如果 Querier 在 Standby 上而转发在 Active 上，需要确认 Snooping 的 mrouter 指向正确 —— 否则会出现"加入请求被送到不转发的设备"。

</div>

### How Multicast Behaves in MPLS / VXLAN / Wireless · 组播在 MPLS / VXLAN / 无线中的表现

| Environment | Mechanism | Design point |
|------|------|---------|
| **MPLS L3VPN (MVPN)** | mLDP (P2MP LSP), PIM-SM/GRE, Rosen (MDT) and other profiles | for high volume choose **mLDP/RSVP-TE P2MP**; avoid per-copy replication between PEs (the bandwidth amplification of ingress replication) |
| **VXLAN/EVPN** | BUM traffic uses **ingress replication** (one copy each) or underlay multicast | with many sources and many receivers, underlay multicast (PIM in the underlay) saves bandwidth compared with ingress replication |
| **Wireless (Wi-Fi)** | multicast is sent at the lowest rate, with no ACK | **multicast-to-unicast is mandatory**; otherwise one video stream eats a large amount of airtime (see Chapter 11) |
| **Cloud (public VPC)** | most clouds do not support multicast (or need a dedicated service) | use an overlay (GRE/VXLAN over UDP), or move to application-layer distribution |

<div class="zh" markdown="1">

| 环境 | 机制 | 设计要点 |
|------|------|---------|
| **MPLS L3VPN（MVPN）** | mLDP（P2MP LSP）、PIM-SM/GRE、Rosen（MDT）等 profile | 大流量选 **mLDP/RSVP-TE P2MP**；避免 PE 间逐份复制（ingress replication 的带宽放大） |
| **VXLAN/EVPN** | BUM 流量用 **ingress replication**（逐份复制）或 underlay 组播 | 组播源多、接收者多时，underlay 组播（PIM in underlay）比 ingress replication 省带宽 |
| **无线（Wi-Fi）** | 组播以最低速率发送、无 ACK | **必须做组播转单播**；否则一个视频流会吃掉大量 airtime（详见第 11 章） |
| **云（公有云 VPC）** | 多数云不支持组播（或需专门服务） | 用 overlay（GRE/VXLAN over UDP）或改用应用层分发 |

</div>

### Multicast Verification Tools (mandatory for acceptance) · 组播的验证工具（验收必用）

| Tool/command | Function |
|----------|------|
| `show ip mroute` | (*,G)/(S,G) state, incoming interface, outgoing interfaces, flags (`s` = SPT, `C` = connected, `P` = pruned) |
| `show ip rpf <source>` | the RPF interface and its source (unicast/static/MBGP) |
| `show ip pim rp mapping` | confirm that RP mappings are consistent |
| `show ip pim neighbor` | neighbours and DR election results |
| `show ip igmp groups` / `show ip igmp snooping` | group membership and the Layer 2 table |
| `mrinfo` / `mtrace` (or compatible tools) | trace the multicast tree and the loss point back from the receiver |
| **NetFlow/IPFIX** | multicast traffic distribution (is replication amplifying it) |
| End-to-end probe | real-service loss/latency (the final judge) |

<div class="zh" markdown="1">

| 工具/命令 | 作用 |
|----------|------|
| `show ip mroute` | 看 (*,G)/(S,G) 状态、入接口、出接口、标志位（`s` = SPT、`C` = 直连、`P` = 剪枝） |
| `show ip rpf <源>` | 看 RPF 接口与来源（单播/静态/MBGP） |
| `show ip pim rp mapping` | 确认 RP 映射是否一致 |
| `show ip pim neighbor` | 邻居与 DR 选举结果 |
| `show ip igmp groups` / `show ip igmp snooping` | 组成员与二层表 |
| `mrinfo` / `mtrace`（或 `mtrace` 兼容工具） | 从接收者反向追踪组播树路径与丢包点 |
| **NetFlow/IPFIX** | 组播流量分布（是否是复制放大） |
| 端到端探针 | 真实业务的丢包/时延（最终判据） |

</div>

---

## Operations and Verification (an inseparable part of multicast design) · 运维与验证（组播设计不可分割的一部分）

### Reading the mroute Flags (the first language of troubleshooting) · mroute 标志位完整解读（排障的第一门语言）

```
R1# show ip mroute 239.10.1.1
(*, 239.10.1.1), 00:10:23/00:02:47, RP 10.0.0.1, flags: SJC
  Incoming interface: GigabitEthernet0/1, RPF nbr 10.0.0.2
  Outgoing interface list:
    GigabitEthernet0/2, Forward/Sparse, 00:10:23/00:00:00
(10.1.1.1, 239.10.1.1), 00:08:11/00:02:59, flags: JT
  Incoming interface: GigabitEthernet0/1, RPF nbr 10.0.0.2
  Outgoing interface list:
    GigabitEthernet0/2, Forward/Sparse, 00:08:11/00:00:00
```

<div class="zh" markdown="1">

```
R1# show ip mroute 239.10.1.1
(*, 239.10.1.1), 00:10:23/00:02:47, RP 10.0.0.1, flags: SJC
  Incoming interface: GigabitEthernet0/1, RPF nbr 10.0.0.2
  Outgoing interface list:
    GigabitEthernet0/2, Forward/Sparse, 00:10:23/00:00:00
(10.1.1.1, 239.10.1.1), 00:08:11/00:02:59, flags: JT
  Incoming interface: GigabitEthernet0/1, RPF nbr 10.0.0.2
  Outgoing interface list:
    GigabitEthernet0/2, Forward/Sparse, 00:08:11/00:00:00
```

</div>

| Flag | Full name | Meaning | Diagnostic value |
|------|------|------|---------|
| **S** | Sparse | this group uses sparse mode | mutually exclusive with D (Dense) |
| **D** | Dense | dense mode | if the group should be SM but shows D → wrong mode |
| **C** | Connected | there is a directly connected receiver (IGMP) | C means somebody local subscribed |
| **L** | Local | this router is the directly connected member | — |
| **J** | Join SPT | **(S,G) is building a tree toward the source** (already switched) | J means the SPT switchover happened |
| **T** | SPT-bit set | traffic from the SPT has already been received | T means the data plane uses the SPT |
| **P** | Pruned | this (S,G) is pruned | **P with no outgoing interface → no receivers** |
| **R** | RP-tree | this (*,G) is on the shared tree (RPT) | — |
| **F** | Register flag | the source is registered (FHR side) | F on the FHR means Register is in progress |
| **s** | SSM | this group falls in the SSM range | s means SSM is in effect |
| **B** | Bidir | bidirectional tree | BiDir scenarios |
| **X** | Proxy Join | joined through a proxy (IGMP proxy) | firewall scenarios |
| **I** | Source specific | source specific | — |
| **m** | MSDP created | created by an MSDP SA | **proof that MSDP worked** |
| **E** | Extranet | cross-VRF multicast | — |

<div class="zh" markdown="1">

| 标志 | 全称 | 含义 | 排障价值 |
|------|------|------|---------|
| **S** | Sparse | 该组用稀疏模式 | 与 D（Dense）互斥 |
| **D** | Dense | 密集模式 | 若组播本该是 SM 却显示 D → 模式配错 |
| **C** | Connected | 有直连接收者（IGMP） | 有 C 说明本地有人订阅 |
| **L** | Local | 本机是成员的直连 | — |
| **J** | Join SPT | **(S,G) 正在向源建树**（已切 SPT） | 有 J 说明切了 SPT |
| **T** | SPT-bit set | 已收到过来自 SPT 的流量 | 有 T 说明数据面走 SPT |
| **P** | Pruned | 该 (S,G) 被剪枝 | **只有 P 没有出接口 → 无接收者** |
| **R** | RP-tree | 该 (*,G) 使用共享树（RPT） | — |
| **F** | Register flag | 有源注册（FHR 侧） | FHR 上看到 F 说明在做 Register |
| **s** | SSM | 该组属于 SSM 范围 | 有 s 说明 SSM 生效 |
| **B** | Bidir | 双向树 | BiDir 场景 |
| **X** | Proxy Join | 通过代理加入（IGMP proxy） | 防火墙场景 |
| **I** | Source specific | 源特定 | — |
| **m** | MSDP created | 由 MSDP SA 触发创建 | **MSDP 生效的证据** |
| **E** | Extranet | 跨 VRF 组播 | — |

</div>

**What four typical combinations mean**:

<div class="zh" markdown="1">

**四种典型组合的含义**：

</div>

| Combination | Meaning | Normal? |
|------|------|---------|
| `(*,G)` has `C`, `(S,G)` missing | receivers exist but the source sends nothing / is not registered | check the source |
| `(*,G)` has `SJC`, `(S,G)` has `JT` | SM plus a completed SPT switchover | normal |
| `(S,G)` has only `P` and no outgoing interface | pruned (no receivers) | normal (the source sends but nobody wants it) |
| `(S,G)` incoming interface `Null` | **RPF failure** | **abnormal** |

<div class="zh" markdown="1">

| 组合 | 含义 | 是否正常 |
|------|------|---------|
| `(*,G)` 有 `C`、`(S,G)` 无 | 有接收者但源没发 / 没注册 | 查源 |
| `(*,G)` 有 `SJC`、`(S,G)` 有 `JT` | SM + SPT 切换完成 | 正常 |
| `(S,G)` 只有 `P` 无出接口 | 被剪枝（无接收者） | 正常（源在发但没人要） |
| `(S,G)` 入接口 `Null` | **RPF 失败** | **异常** |

</div>

### The Multicast Troubleshooting Decision Tree (turn it straight into a runbook) · 组播排障的决策树（可直接做成 Runbook）

```
【Symptom: the receiver gets no multicast】
│
├─ ① Did the receiver join the group?
│    ├─ LHR# show ip igmp groups <group>       → is there an entry?
│    │    ├─ no → capture packets: was the IGMP Report sent? (host issue / IGMP version / ACL)
│    │    └─ yes → continue
│    └─ switch: show ip igmp snooping groups → is there an entry?
│         ├─ no → Querier / mrouter / Snooping not enabled (see case 3)
│         └─ yes → continue
│
├─ ② Is there multicast state on the LHR?
│    └─ LHR# show ip mroute <group>
│         ├─ no (*,G) → the upstream Join was never sent / the RP is unreachable
│         ├─ (*,G) but no (S,G) → the source is not registered (check Register on the FHR)
│         └─ (S,G) present → continue
│
├─ ③ Is RPF correct?
│    └─ LHR# show ip rpf <source>  → does the RPF interface equal the actual ingress?
│         ├─ no → RPF failure (check unicast routes, static mroutes, MBGP, ECMP)
│         └─ yes → continue
│
├─ ④ Has the traffic arrived?
│    └─ show ip mroute count / interface counters → is the ingress packet count climbing?
│         ├─ no → upstream is not sending (walk up the tree hop by hop, or use mtrace)
│         └─ yes → continue
│
├─ ⑤ Is the outgoing interface list right?
│    └─ does the outgoing interface list contain the downstream interface? are the flags Forward?
│         ├─ no (Prune) → the downstream never sent a Join / Prune Override issue
│         └─ yes → continue
│
└─ ⑥ Is the data plane forwarding?
     ├─ are platform resources (MCAST entries, replication engine) exhausted?
     ├─ is Layer 2 really forwarding (port mirror capture)?
     └─ MTU / fragmentation / QoS drops (interface output drops)
```

<div class="zh" markdown="1">

```
【现象：接收者收不到组播】
│
├─ ① 接收者加入了组吗？
│    ├─ LHR# show ip igmp groups <组>       → 有记录？
│    │    ├─ 无 → 抓包看 IGMP Report 是否发出（主机侧问题/IGMP 版本/ACL）
│    │    └─ 有 → 继续
│    └─ 交换机：show ip igmp snooping groups → 有记录？
│         ├─ 无 → Querier / mrouter / Snooping 未启用（见案例三）
│         └─ 有 → 继续
│
├─ ② LHR 上有组播状态吗？
│    └─ LHR# show ip mroute <组>
│         ├─ 无 (*,G) → 上游 Join 没发出去 / RP 不可达
│         ├─ 有 (*,G) 无 (S,G) → 源未注册（看 FHR 是否有 Register）
│         └─ 有 (S,G) → 继续
│
├─ ③ RPF 正确吗？
│    └─ LHR# show ip rpf <源>  → RPF 接口 == 实际入接口？
│         ├─ 否 → RPF 失败（查单播路由、静态 mroute、MBGP、ECMP）
│         └─ 是 → 继续
│
├─ ④ 流量到了吗？
│    └─ show ip mroute count / 接口计数 → 入方向包数在增长？
│         ├─ 否 → 上游没送（沿树逐跳往上查，或用 mtrace）
│         └─ 是 → 继续
│
├─ ⑤ 出接口列表对吗？
│    └─ Outgoing interface list 是否含下行接口？标志是否 Forward？
│         ├─ 否（Prune） → 下游没发 Join / Prune Override 问题
│         └─ 是 → 继续
│
└─ ⑥ 数据面转发正常吗？
     ├─ 平台资源（MCAST 表项、复制引擎）是否耗尽？
     ├─ 二层是否真的转发了（镜像抓包）？
     └─ MTU / 分片 / QoS 丢弃（接口 output drops）
```

</div>

### Using mtrace and mrinfo in Practice · mtrace 与 mrinfo 的实战用法

```cfg
! mrinfo: shows the PIM neighbours and interface state of a source (or router)
R1# mrinfo 10.1.1.1
10.1.1.1 (source) [version 2, ...]
 10.0.0.2 -> 0.0.0.0 [1/0/...]        <- upstream neighbour
 10.0.0.6 -> 0.0.0.0 [1/0/...]

! mtrace: traces the multicast tree from the receiver toward the source, reporting loss per hop
R1# mtrace 10.1.1.1 239.10.1.1 10.20.0.50
Mtrace from 10.20.0.50 to 10.1.1.1 via group 239.10.1.1
  Querying full reverse path...
  0  10.20.0.50 (receiver) ...
  -1 10.20.0.1  PIM  ...  Lost: 0/100
  -2 10.10.0.1  PIM  ...  Lost: 12/100     <- the loss point is here
  -3 10.0.0.2   PIM  ...  Lost: 0/100
  -4 10.1.1.1   PIM  ...  Lost: 0/100
```

<div class="zh" markdown="1">

```cfg
! mrinfo：看某个源（或路由器）的 PIM 邻居与接口状态
R1# mrinfo 10.1.1.1
10.1.1.1 (source) [version 2, ...]
 10.0.0.2 -> 0.0.0.0 [1/0/...]        ← 上游邻居
 10.0.0.6 -> 0.0.0.0 [1/0/...]

! mtrace：从接收者向源追踪组播树，报告每一跳的丢包率
R1# mtrace 10.1.1.1 239.10.1.1 10.20.0.50
Mtrace from 10.20.0.50 to 10.1.1.1 via group 239.10.1.1
  Querying full reverse path...
  0  10.20.0.50 (接收者) ...
  -1 10.20.0.1  PIM  ...  Lost: 0/100
  -2 10.10.0.1  PIM  ...  Lost: 12/100     ← 丢包点在这里
  -3 10.0.0.2   PIM  ...  Lost: 0/100
  -4 10.1.1.1   PIM  ...  Lost: 0/100
```

</div>

| Tool | What it shows | Prerequisite | Common obstacle |
|------|-----------|------|---------|
| **mrinfo** | a source's/router's PIM interfaces and neighbours | 224.0.0.13 and unicast probes must be allowed | blocked by ACLs |
| **mtrace** | hop-by-hop path + loss location + rate | every hop must support mtrace (common in Cisco estates) | may be unsupported across vendors; often disabled by security policy |
| **NetFlow** | traffic distribution, replication amplification | multicast sampling configured | inaccurate at low sampling rates |
| **Interface counters** | multicast packet counts per direction | none | only locates "which segment has no traffic", not "which hop drops" |

<div class="zh" markdown="1">

| 工具 | 能看到什么 | 前提 | 常见阻碍 |
|------|-----------|------|---------|
| **mrinfo** | 源/路由器的 PIM 接口与邻居 | 允许 PIM 的 224.0.0.13 与单播探测 | ACL 阻断 |
| **mtrace** | 逐跳路径 + 丢包位置 + 速率 | 各跳都支持 mtrace（Cisco 生态常用） | 跨厂商可能不支持；常被安全策略禁用 |
| **NetFlow** | 流量分布、复制放大 | 配置组播采样 | 采样率低时不准 |
| **接口计数** | 入/出方向的组播包数 | 无 | 只能定位"哪段没流量"，不能定位"哪一跳丢" |

</div>

> 💡 **Why mtrace matters**: it is the only tool that directly answers "**is the tree right**" and "**which hop is losing packets**". **Add it to the list of permitted operational protocols at design time**; otherwise, when something breaks, you can only guess. If the security team refuses, the alternative is "**periodic mroute snapshot export from every device + NetFlow path analysis**" (weaker, but workable).

<div class="zh" markdown="1">

> 💡 **mtrace 的价值**：它是唯一能直接回答"**树对不对**"和"**在哪一跳丢**"的工具。**设计阶段就要把它列为"允许的运维协议"**，否则出了故障只能靠猜。如果安全团队不允许，替代方案是"**每台设备定期导出 mroute 快照 + NetFlow 路径分析**"（弱一些，但可行）。

</div>

### Monitoring Metrics and Alert Design · 监控指标与告警设计

| Layer | Metric | Collection | Alert condition | Severity |
|------|------|---------|---------|---------|
| **Device capacity** | mroute entries / limit | SNMP (IPMROUTE-MIB) | > 70% | P2 |
| **Device capacity** | multicast replication resource utilisation | platform specific | > 80% | P1 |
| **Protocol health** | change in PIM neighbour count | SNMP | sudden ±1 | P2 |
| **Protocol health** | rate of increase of RPF failure counters | SNMP / CLI | > 100/s for 1 min | P1 |
| **Protocol health** | Register rate | SNMP | > 5× baseline | P2 |
| **Protocol health** | MSDP peer state / SA count | SNMP | peer down or SA count changes 50% | P1 |
| **Protocol health** | RP mapping consistency | periodic scripted comparison | any two devices disagree | P1 |
| **Traffic** | multicast egress rate on key interfaces | SNMP / NetFlow | > 1.5× baseline | P2 |
| **Traffic** | multicast traffic distribution across the topology | NetFlow | multicast appears on a link where it should not | P2 |
| **Service** | end-to-end loss / latency / MOS | probe | loss > 0.1% | P1 |
| **Audit** | group addresses outside the plan appear | mroute snapshot compared with the SoT | any | P2 |

<div class="zh" markdown="1">

| 层次 | 指标 | 采集方式 | 告警条件 | 告警级别 |
|------|------|---------|---------|---------|
| **设备容量** | mroute 表项数 / 上限 | SNMP (IPMROUTE-MIB) | > 70% | P2 |
| **设备容量** | 组播复制资源使用率 | 平台专有 | > 80% | P1 |
| **协议健康** | PIM 邻居数变化 | SNMP | 突变 ±1 | P2 |
| **协议健康** | RPF 失败计数增速 | SNMP / CLI | > 100/s 持续 1 min | P1 |
| **协议健康** | Register 速率 | SNMP | > 基线 5 倍 | P2 |
| **协议健康** | MSDP peer 状态 / SA 数 | SNMP | peer down 或 SA 数突变 50% | P1 |
| **协议健康** | RP 映射一致性 | 定期脚本对比 | 任意两台不一致 | P1 |
| **流量** | 关键接口组播出方向速率 | SNMP / NetFlow | > 基线 1.5 倍 | P2 |
| **流量** | 组播流量拓扑分布 | NetFlow | 出现"不该有的链路有组播" | P2 |
| **业务** | 端到端丢包 / 时延 / MOS | 探针 | 丢包 > 0.1% | P1 |
| **审计** | 出现规划外的组地址 | mroute 快照比对 SoT | 任意 | P2 |

</div>

**Three baselines you must establish**:

<div class="zh" markdown="1">

**必须建立的三个基线**：

</div>

1. **Topology baseline**: the tree shape of each key group (mrinfo/mtrace output)
2. **Capacity baseline**: peak (S,G) count and outgoing-interface count per device
3. **Traffic baseline**: peak and trough multicast bandwidth on key links (including the time distribution)

<div class="zh" markdown="1">

1. **拓扑基线**：每个关键组的树形状（mrinfo/mtrace 结果）
2. **容量基线**：各设备的 (S,G) 数与出接口数峰值
3. **流量基线**：关键链路的组播带宽峰谷（含时间分布）

</div>

### Acceptance Test Cases (usable directly for project delivery) · 验收测试用例（可直接用于项目交付）

| # | Test | Method | Pass criterion |
|---|-------|------|---------|
| 1 | Basic reception | the receiver joins, verify picture/data | receives correctly, no pixellation |
| 2 | **Tree shape** | `mrinfo` / `mtrace` compared with the design | path matches the design (no detour) |
| 3 | **RP mapping consistency** | compare `show ip pim rp mapping` network-wide | identical everywhere |
| 4 | **RP failover** | shut down the primary RP (or cut its link) | a new receiver joins successfully in < 3 s |
| 5 | **PIM neighbour failure** | break one uplink | multicast recovers in < 5 s (or per design) |
| 6 | **Snooping correctness** | capture on a port with no subscription | must not receive multicast |
| 7 | **Querier dependency** | watch the group table for 15 min | entries do not disappear |
| 8 | **Leave latency** | the receiver sends Leave; measure when traffic stops | < design value (usually < 3 s) |
| 9 | **Group limit** | one host joins more groups than the limit | it is limited and other services are unaffected |
| 10 | **Multicast boundary** | send a group that must not leave | it is blocked |
| 11 | **Source switchover (dual-active)** | switch sources | the receiver notices nothing (ST 2022-7) or < designed interruption |
| 12 | **Physical link break** | physically break the path (not `shutdown` on the interface) | matches the Live-Live expectation |
| 13 | **Capacity stress** | all channels concurrent plus all receivers | no loss, CPU < 70%, entries < 70% |
| 14 | **MTU** | multicast at large packet sizes (close to MTU) | no loss, no fragmentation |
| 15 | **QoS verification** | multicast loss under congestion | per design (e.g. < 0.01%) |
| 16 | **Unexpected-multicast detection** | send a group outside the plan | blocked by the boundary/ACL, and an alert fires |
| 17 | **MSDP SA filtering** | inject an illegal SA from the peer | it is filtered |
| 18 | **Monitoring and alerting** | create an RPF failure deliberately | the alert fires (proving observability) |

<div class="zh" markdown="1">

| # | 测试项 | 方法 | 通过标准 |
|---|-------|------|---------|
| 1 | 基本接收 | 接收端加入，验证画面/数据 | 正常接收，无花屏 |
| 2 | **树形状** | `mrinfo` / `mtrace` 与设计比对 | 路径符合设计（无绕行） |
| 3 | **RP 映射一致性** | 全网比对 `show ip pim rp mapping` | 完全一致 |
| 4 | **RP 故障切换** | 关闭主 RP（或断其链路） | 新接收者 < 3 s 加入成功 |
| 5 | **PIM 邻居故障** | 断一条上行链路 | 组播恢复 < 5 s（或符合设计） |
| 6 | **Snooping 正确性** | 无订阅端口抓包 | 不应收到组播 |
| 7 | **Querier 依赖** | 观察 15 min 的组表 | 表项不消失 |
| 8 | **离开时延** | 接收者发 Leave，测流量停止时间 | < 设计值（通常 < 3 s） |
| 9 | **组数限制** | 单主机加入超限数量的组 | 被限制，其他业务不受影响 |
| 10 | **组播边界** | 向边界外发不该出的组 | 被阻断 |
| 11 | **源切换（双活）** | 切源 | 接收端无感（ST 2022-7）或 < 设计中断 |
| 12 | **物理断链** | 真实断开路径（不是 shutdown 接口） | 符合 Live-Live 预期 |
| 13 | **容量压测** | 并发全部频道 + 全接收者 | 无丢包、CPU < 70%、表项 < 70% |
| 14 | **MTU** | 大包（接近 MTU）组播 | 不丢、不分片 |
| 15 | **QoS 验证** | 拥塞下组播丢包率 | 符合设计（如 < 0.01%） |
| 16 | **异常组播检测** | 发规划外的组 | 被边界/ACL 阻断 + 告警 |
| 17 | **MSDP SA 过滤** | 从对端注入非法 SA | 被过滤 |
| 18 | **监控告警** | 人为制造 RPF 失败 | 告警触发（验证可观测性） |

</div>

> ⚠️ **Test 12 (physical link break) is the easiest to skip and the most valuable.** The great majority of "redundancy failures" only appear during a real physical fault (see case 7). **If a physical break is not possible at acceptance, at least do a "pull the line card / power off" test, and record the risk of "physical sharing not verified" in the document.**

<div class="zh" markdown="1">

> ⚠️ **第 12 项（物理断链）是最容易被跳过、也最有价值的一项**。绝大多数"冗余失效"都是在真实物理故障时才暴露（见案例七）。**如果不能在验收时做物理断链，至少要做"拔板卡/关电源"级别的测试，且必须在文档里注明"未验证物理共享"的风险。**

</div>

### Multicast Design Document Template (a mandatory LLD chapter) · 组播设计文档模板（LLD 必备章节）

```
1. Application list and profiles (bitrate, group count, sources, receiver distribution, latency/loss requirements)
2. Address planning (group address table, service partitioning, MAC collision check results)
3. Forwarding mode decision (each application class -> SSM/SM/BiDir/DM, with reasons)
4. RP design (location, count, discovery method, redundancy method, Anycast/MSDP details, failover budget)
5. Layer 2 design (Snooping/Querier/Mrouter/MVR, per-port group limit, Fast Leave policy)
6. Inter-domain and boundaries (MSDP/MBGP/MVPN/tunnels/firewalls, boundary ACLs and scope)
7. QoS design (DSCP plan, per-hop queues, rate-limiting points)
8. Security design (first-hop filtering, PIM authentication, SA filtering, IGMP limits)
9. Capacity planning (per-link bandwidth, per-device entries, replication resources, AP airtime)
10. High availability (failure scenario table + failover time budget + physical redundancy path diagram)
11. Monitoring and alerting (metrics, thresholds, collection method)
12. Acceptance cases (including physical link break tests)
13. Known limitations and risks (e.g. "no physical path separation", "no RP redundancy at a branch")
```

<div class="zh" markdown="1">

```
1. 应用清单与画像（码率、组数、源、接收者分布、时延/丢包要求）
2. 地址规划（组地址表、业务划分、MAC 冲突检查结果）
3. 转发模式决策（每类应用 → SSM/SM/BiDir/DM，含理由）
4. RP 设计（位置、数量、发现方式、冗余方式、Anycast/MSDP 细节、切换预算）
5. 二层设计（Snooping/Querier/Mrouter/MVR、每端口组数限制、Fast Leave 策略）
6. 域间与边界（MSDP/MBGP/MVPN/隧道/防火墙、边界 ACL 与 scope）
7. QoS 设计（DSCP 规划、每跳队列、限速点）
8. 安全设计（首跳过滤、PIM 认证、SA 过滤、IGMP 限制）
9. 容量规划（每链路带宽、每设备表项、复制资源、AP airtime）
10. 高可用（故障场景表 + 切换时间预算 + 冗余物理路径图）
11. 监控与告警（指标、阈值、采集方式）
12. 验收用例（含物理断链测试）
13. 已知限制与风险（例如"未做物理路径分离""某分支无 RP 冗余"）
```

</div>

---

## Real-World Case Studies · 实战案例

### 🔥 Case 1: Turning On the Meeting-Room TV Displayed Another Floor's CCTV Feed · 🔥 案例一：打开会议室电视，另一个楼层的监控画面出现在屏幕上

**Scenario**: an enterprise deployed IPTV and video surveillance, both using private addresses inside 239.0.0.0/8, with no unified plan. One day the meeting-room TV started showing an "uninvited" surveillance picture, and bandwidth behaved abnormally.

<div class="zh" markdown="1">

**场景**：企业部署 IPTV 与视频监控，均使用 239.0.0.0/8 私有组播地址，未做统一规划。某天会议室的电视出现"不请自来"的监控画面，且带宽异常。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. IPTV used `239.10.1.1`, surveillance used `239.138.1.1` (each taken at random by its own team)
2. Compute the MAC:
   - `239.10.1.1` → keep the low 23 bits → `0A:01:01` → MAC `01:00:5E:0A:01:01`
   - `239.138.1.1` → keep the low 23 bits → `0A:01:01` → MAC `01:00:5E:0A:01:01`
   - **the two are identical** (the second octets 10 and 138 differ by 128, and the top bit of the second octet is exactly one of the five discarded bits)
3. The access VLAN had both IPTV and surveillance subscribers → the switch forwarded by MAC → the two groups leaked into each other

<div class="zh" markdown="1">

1. IPTV 用 `239.10.1.1`，监控用 `239.138.1.1`（两个业务各自随手取了一段）
2. 计算 MAC：
   - `239.10.1.1` → 保留后 23 位 → `0A:01:01` → MAC `01:00:5E:0A:01:01`
   - `239.138.1.1` → 保留后 23 位 → `0A:01:01` → MAC `01:00:5E:0A:01:01`
   - **两者完全相同**（第二段 10 与 138 只差 128，而第二段的最高位正是被丢弃的 5 位之一）
3. 接入层 VLAN 内既有 IPTV 又有监控订阅者 → 交换机按 MAC 转发 → 两个组互相串流

</div>

**Quick collision test**: the mapping discards "the low 4 bits of the first octet" plus "the top bit (128) of the second octet". Therefore:

<div class="zh" markdown="1">

**冲突判定速查**：映射丢弃的是「第一段的低 4 位」+「第二段的最高位（128）」。所以：

</div>

| Address pair | Collision? | Why |
|--------|---------|------|
| 239.10.1.1 and 239.138.1.1 | **collision** | second octets differ by 128 (the top bit is discarded) |
| 224.10.1.1 and 239.10.1.1 | **collision** | first octets 224–239 differ only in the discarded low 4 bits |
| 239.10.1.1 and 239.10.1.33 | no | the fourth octets differ, and all of it is kept in the MAC |
| 239.10.1.1 and 239.20.1.1 | no | second octets differ by 10, i.e. differ in the low 7 bits |

<div class="zh" markdown="1">

| 地址对 | 是否冲突 | 原因 |
|--------|---------|------|
| 239.10.1.1 与 239.138.1.1 | **冲突** | 第二段差 128（最高位被丢弃） |
| 224.10.1.1 与 239.10.1.1 | **冲突** | 第一段 224–239 只差被丢弃的低 4 位 |
| 239.10.1.1 与 239.10.1.33 | 不冲突 | 第四段不同，全部保留在 MAC 中 |
| 239.10.1.1 与 239.20.1.1 | 不冲突 | 第二段差 10，二进制低 7 位不同 |

</div>

**Root cause**: during address planning the two services were placed in `239.10.x.x` and `239.138.x.x`, which happen to fall into the same MAC mapping. **The symptom is extremely misleading**: it looks like a "security event" or an "application bug", while it is really an address-planning defect.

<div class="zh" markdown="1">

**根因**：地址规划时把两个业务分在 `239.10.x.x` 与 `239.138.x.x`，恰好落入同一 MAC 映射。**症状极具迷惑性**：看起来像"安全事件"或"应用 Bug"，实际上是地址规划缺陷。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Action | Explanation |
|------|------|
| **Re-plan the addresses** | give each service its own /16 (video 239.10/16, surveillance 239.20/16) and **never reuse the same low 23 bits inside a /16** |
| **Separate service VLANs** | surveillance and IPTV in different VLANs; multicast does not leave the VLAN (except through Layer 3 on demand) |
| **Write it into the SoT** | the multicast address table goes into IPAM; check for mapping collisions before adding any address |
| **Verification script** | add a CI check: no two multicast addresses in the same VLAN may share a MAC |

<div class="zh" markdown="1">

| 动作 | 说明 |
|------|------|
| **重新规划地址** | 按业务分配独立 /16（视频 239.10/16、监控 239.20/16），且**每个 /16 内不复用相同低 23 位** |
| **业务 VLAN 分离** | 监控与 IPTV 不同 VLAN，组播不出 VLAN（除三层按需） |
| **写进 SoT** | 组播地址表纳入 IPAM，新增地址前检查映射冲突 |
| **验证脚本** | CI 中加一条检查：同一 VLAN 内所有组播地址的 MAC 不得重复 |

</div>

**Lesson**: **multicast addresses must be planned like IP subnets**. The 32:1 overlap is not a "theoretical problem"; in networks where addresses are taken at random it is almost certain to happen, and the symptoms are extremely misleading (people assume an attack).

<div class="zh" markdown="1">

**教训**：**组播地址必须像 IP 子网一样规划**。32:1 重叠不是"理论问题"，它在"随手取地址"的网络里几乎必然发生，而且症状极具迷惑性（以为被攻击了）。

</div>

### 🔥 Case 2: The Source Was Sending and the mroute Existed, but Not One Packet Arrived (RPF Failure) · 🔥 案例二：源在发、mroute 有表，但一个包也收不到

**Scenario**: a new data centre's market-data multicast (source 10.1.1.1, group 232.1.1.1, SSM). The sender confirmed it was sending; the receiver's `show ip mroute 232.1.1.1` showed an (S,G) entry, but with incoming interface `Null`, an empty outgoing list, and `show ip mroute count` showed a large number of **RPF failed**.

<div class="zh" markdown="1">

**场景**：新建数据中心的行情组播（源 10.1.1.1，组 232.1.1.1，SSM）。发送端确认在发，接收端的 `show ip mroute 232.1.1.1` 显示有 (S,G)，但入接口 `Null`，出接口为空，`show ip mroute count` 显示大量 **RPF failed**。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. `show ip rpf 10.1.1.1` → pointed at **Gi0/1** (learned through OSPF)
2. Packet capture: multicast packets actually arrived on **Gi0/2**
3. Checking the routing table: the source prefix was covered by a more specific route (a /24) learned via BGP with a next hop on another border router → **unicast used the BGP path (Gi0/2)**, while RPF used the OSPF path (Gi0/1). Wait — the other way round: RPF uses longest match, so it should use the BGP /24…

<div class="zh" markdown="1">

1. `show ip rpf 10.1.1.1` → 指向 **Gi0/1**（经 OSPF 学到）
2. 抓包：组播包实际从 **Gi0/2** 进来
3. 查路由：该源前缀被 BGP 学到的更具体路由（/24）覆盖，下一跳是另一台边界路由器 → **单播走 BGP 路径（Gi0/2）**，但 RPF 用的是 OSPF 路径（Gi0/1）—— 等等，反向：RPF 用最长匹配，所以应该用 BGP 的 /24……

</div>

**The real cause**: `show ip rpf` showed **Gi0/2**, but the device had `ip mroute 10.1.1.1 255.255.255.255 Gi0/1` configured (a legacy static mroute added for the old topology). **A static mroute takes precedence over unicast routes**, so the RPF check failed consistently.

<div class="zh" markdown="1">

**真实原因**：`show ip rpf` 显示的是 **Gi0/2**，但设备上配置了 `ip mroute 10.1.1.1 255.255.255.255 Gi0/1`（历史遗留，为旧拓扑加的静态 mroute）。**静态 mroute 优先级高于单播路由**，于是 RPF 检查恒定失败。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

```cfg
! remove the incorrect static mroute
no ip mroute 10.1.1.1 255.255.255.255 Gi0/1

! if a fixed RPF path is genuinely needed (e.g. multicast must use a separate exit)
ip mroute 10.1.1.1 255.255.255.255 10.0.0.1   ! pointing at a next hop is safer than an interface

! enable multicast multipath where multiple paths exist
ip multicast multipath
```

<div class="zh" markdown="1">

```cfg
! 删除错误的静态 mroute
no ip mroute 10.1.1.1 255.255.255.255 Gi0/1

! 若确实需要固定 RPF 路径（例如组播要走独立出口）
ip mroute 10.1.1.1 255.255.255.255 10.0.0.1   ! 指向下一跳而非接口更稳妥

! 多路径场景开启组播多路径
ip multicast multipath
```

</div>

**Checklist (the standard RPF troubleshooting procedure)**:

<div class="zh" markdown="1">

**排查清单（RPF 类故障的标准流程）**：

</div>

| Step | Command | What to look at |
|------|------|-------|
| 1 | `show ip rpf <source>` | RPF interface and its source (unicast/static/mbgp) |
| 2 | `show ip route <source>` | the unicast best path |
| 3 | `show ip mroute <group>` | whether the incoming interface is `Null`, and the flags |
| 4 | capture / port mirror | the **actual ingress interface** |
| 5 | inspect the configuration | any legacy `ip mroute`, `multicast multipath`, MBGP |

<div class="zh" markdown="1">

| 步骤 | 命令 | 看什么 |
|------|------|-------|
| 1 | `show ip rpf <源>` | RPF 接口、来源（unicast/static/mbgp） |
| 2 | `show ip route <源>` | 单播最优路径 |
| 3 | `show ip mroute <组>` | 入接口是否为 `Null`、标志位 |
| 4 | 抓包/镜像 | **实际入接口** |
| 5 | 查配置 | 是否有历史 `ip mroute`、`multicast multipath`、MBGP |

</div>

**Lesson**: **RPF is multicast's "invisible gatekeeper": when it fails it raises no alarm and logs nothing (apart from counters)**. Troubleshooting must compare three things — "unicast route + actual ingress interface + mroute state" — and in particular must check for legacy static mroutes.

<div class="zh" markdown="1">

**教训**：**RPF 是组播的"隐形门卫"，失败时不报警、不记录（除计数器）**。排障必须"单播路由 + 实际入接口 + mroute 状态"三者对照，尤其要检查历史遗留的静态 mroute。

</div>

### 🔥 Case 3: The Monitoring Wall "Went Black Every Few Minutes", and Re-opening the Channel Fixed It · 🔥 案例三：监控大屏"每隔几分钟黑一下"，重新打开频道又好了

**Scenario**: 200 CCTV cameras on a campus, with a pure Layer 2 access VLAN (no Layer 3 multicast router). Operations reported that the wall picture stalled or went black roughly every 3–5 minutes, and recovered after switching channels.

<div class="zh" markdown="1">

**场景**：园区 200 个监控摄像头，接入层为纯二层 VLAN（无三层组播路由器）。运维反馈：大屏画面大约每 3–5 分钟卡顿/黑屏一次，重新切换频道后恢复。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. The switch's `show ip igmp snooping groups` → entries **appeared and disappeared**
2. The VLAN's SVI was on the core, but **no PIM router interface existed in that VLAN** (PIM was not enabled on the core SVI)
3. Therefore **there was no IGMP Querier** → nobody sent queries → snooping entries aged out after the default 260 s → multicast stopped being forwarded
4. The user switched channels → a new IGMP Report was sent → entries rebuilt → temporary recovery

<div class="zh" markdown="1">

1. 交换机 `show ip igmp snooping groups` → 组表项**时有时无**
2. 该 VLAN 的 SVI 在核心上，但**该 VLAN 内没有 PIM 路由器接口**（核心 SVI 未开 PIM）
3. 因此**没有 IGMP Querier** → 无人发查询 → 交换机 Snooping 表项在老化时间（默认 260 s）后删除 → 组播停止转发
4. 用户重新切频道 → 发出新的 IGMP Report → 表项重建 → 短暂恢复

</div>

**Root cause**: **IGMP Snooping depends on a Querier to maintain group membership**. A Layer 3 multicast router sends queries, but a pure Layer 2 VLAN has none, so entries periodically expire.

<div class="zh" markdown="1">

**根因**：**IGMP Snooping 依赖 Querier 维持组成员关系**。三层组播路由器会发查询，但纯二层 VLAN 里没有，于是表项周期性失效。

</div>

**Fixes (choose one, in order of preference)**:

<div class="zh" markdown="1">

**修复（三选一，按推荐度）**：

</div>

```cfg
! Option 1 (recommended): let the core SVI be the multicast router
interface Vlan200
 ip address 10.20.0.1 255.255.255.0
 ip pim sparse-mode            ! enabling PIM makes it the Querier naturally

! Option 2: enable the Snooping Querier on the switch (when there is no Layer 3 multicast)
ip igmp snooping querier
ip igmp snooping querier address 10.20.0.254
ip igmp snooping querier query-interval 60

! Option 3: static mrouter (only in very few scenarios)
ip igmp snooping vlan 200 mrouter interface Gi1/0/1
```

<div class="zh" markdown="1">

```cfg
! 方案 1（推荐）：让核心 SVI 成为组播路由器
interface Vlan200
 ip address 10.20.0.1 255.255.255.0
 ip pim sparse-mode            ! 开启 PIM，自然成为 Querier

! 方案 2：交换机启用 Snooping Querier（无三层组播时）
ip igmp snooping querier
ip igmp snooping querier address 10.20.0.254
ip igmp snooping querier query-interval 60

! 方案 3：静态 mrouter（极少数场景）
ip igmp snooping vlan 200 mrouter interface Gi1/0/1
```

</div>

**Lesson**: **whenever IGMP Snooping is enabled, there must be a Querier in the VLAN**. This is a classic "if you configure A you must also configure B" dependency, and many networks miss exactly this link when they "migrate Layer 3 into a Layer 2 extension".

<div class="zh" markdown="1">

**教训**：**只要开了 IGMP Snooping，就必须保证 VLAN 内有 Querier**。这是一个"配置了 A 就必须配套 B"的典型依赖，很多网络在"三层迁移到二层延伸"时正好漏掉这一环。

</div>

### 🔥 Case 4: After the RP Crashed, "Old Channels Fine, New Channels Would Not Open at All" · 🔥 案例四：RP 宕机后，"老频道正常、新频道全打不开"

**Scenario**: a single-RP design (PIM-SM). The RP device rebooted for 20 minutes after a power supply failure. During the outage:
- the 20 channels already playing **kept working**
- **switching channels or joining anew** failed for everyone

<div class="zh" markdown="1">

**场景**：单 RP 设计（PIM-SM），RP 所在设备因电源故障重启 20 分钟。故障期间：
- 已经在播放的 20 个频道**一直正常**
- 任何人**切换频道/新加入**都失败

</div>

**Root cause (textbook PIM-SM behaviour)**:

<div class="zh" markdown="1">

**根因（教科书级的 PIM-SM 行为）**：

</div>

| Symptom | Cause |
|------|------|
| old channels fine | already switched to the **SPT**; (S,G) state exists independently on each router and does not depend on the RP |
| new channels will not open | a new receiver must send a (*,G) Join to the **RP** → the RP is unreachable → the shared tree cannot be built |
| a new source cannot register | the Register message cannot reach the RP |

<div class="zh" markdown="1">

| 现象 | 原因 |
|------|------|
| 老频道正常 | 已切换到 **SPT**，(S,G) 状态在各路由器上独立存在，不依赖 RP |
| 新频道打不开 | 新接收者需要发 (*,G) Join 到 **RP** → RP 不可达 → 共享树建不起来 |
| 新源无法注册 | Register 报文发不到 RP |

</div>

**Fix: Anycast-RP + MSDP (dual RPs)**

<div class="zh" markdown="1">

**修复：Anycast-RP + MSDP（双 RP）**

</div>

```cfg
! configure both RPs (same RP address, different router-ids)
interface Loopback0
 ip address 10.0.0.1 255.255.255.255     ! anycast RP address (identical on both)
interface Loopback1
 ip address 1.1.1.1 255.255.255.255      ! unique identity (used by MSDP)
ip pim rp-address 10.0.0.1
ip msdp peer 2.2.2.2 connect-source Loopback1
ip msdp cache-sa-state
ip msdp originator-id Loopback1
```

<div class="zh" markdown="1">

```cfg
! 两台 RP 都配置（RP 地址相同，router-id 不同）
interface Loopback0
 ip address 10.0.0.1 255.255.255.255     ! Anycast RP 地址（两台相同）
interface Loopback1
 ip address 1.1.1.1 255.255.255.255      ! 唯一标识（MSDP 用）
ip pim rp-address 10.0.0.1
ip msdp peer 2.2.2.2 connect-source Loopback1
ip msdp cache-sa-state
ip msdp originator-id Loopback1
```

</div>

**The new problem that appeared after go-live (this is the important part)**: the MSDP peer was `Established`, but `show ip msdp sa-cache` was **0**, and cross-RP receivers still got nothing.

<div class="zh" markdown="1">

**上线后遇到的新问题（这是重点）**：MSDP peer 是 `Established`，但 `show ip msdp sa-cache` **为 0**，跨 RP 的接收者仍收不到流。

</div>

| Check | Result |
|------|------|
| MSDP connectivity | TCP 639 fine |
| Is the source sending | fine |
| SA counters in `show ip msdp peer` | both send and receive were 0 |
| **Discovery** | the two RPs had **the same router-id** (both 10.0.0.1, derived from the anycast loopback) → MSDP thought the peer was itself, so SAs were discarded |

<div class="zh" markdown="1">

| 排查 | 结果 |
|------|------|
| MSDP 连通性 | TCP 639 正常 |
| 源是否在发送 | 正常 |
| `show ip msdp peer` 的 SA 计数 | 收发均为 0 |
| **发现** | 两台 RP 的 **router-id 相同**（都是 10.0.0.1，从 Anycast loopback 派生）→ MSDP 认为对端是自己，SA 被丢弃 |

</div>

**Fix**: explicitly configure a **unique router-id** on each RP (`ip msdp originator-id` and `router-id` from Loopback1), and confirm that the peer address in `show ip msdp peer` is the peer's unique address.

<div class="zh" markdown="1">

**修复**：每台 RP 显式配置**唯一 router-id**（`ip msdp originator-id` + `router-id` 用 Loopback1），并确认 `show ip msdp peer` 的 peer 地址是对方的唯一地址。

</div>

**Lesson**: **the three "must be different" rules of Anycast-RP**: ① router-ids must differ; ② the MSDP peer address must be a unique loopback; ③ `originator-id` must point at the unique address. If any one of them is the same, MSDP "comes up but does nothing" — the most insidious failure in any anycast-RP deployment.

<div class="zh" markdown="1">

**教训**：**Anycast-RP 的三个"必须不同"**：①router-id 必须不同；②MSDP peer 地址必须用唯一 loopback；③`originator-id` 必须指向唯一地址。任何一项相同，MSDP 就"通了但没用"——这是任何cast-RP 部署最隐蔽的故障。

</div>

### 🔥 Case 5: Multicast State Explosion — Core CPU at 60% and 10-Second Channel Zapping · 🔥 案例五：组播状态爆炸，核心路由器 CPU 60% 且频道切换要 10 秒

**Scenario**: hotel IPTV, 600 channels at 3–8 Mbps each, 2,000 rooms. PIM-SM with a single RP, SPT switchover left at the default. After six months the core CPU sat at 50%–60%, channel zapping was slow (8–12 s) with occasional pixellation.

<div class="zh" markdown="1">

**场景**：酒店 IPTV，600 个频道，每频道 3–8 Mbps，2,000 个房间。用 PIM-SM + 单 RP，默认开启 SPT 切换。运行半年后核心 CPU 持续 50%–60%，频道切换慢（8–12 秒），偶发花屏。

</div>

**Root cause**:

<div class="zh" markdown="1">

**根因**：

</div>

1. **State count = channels × receiver distribution**: 600 channels × multiple (S,G) branches, tens of thousands of mroutes on the core
2. **Every channel change**: IGMP Leave → group-specific query → Prune → new group Join → (*,G) to the RP → SPT switchover → several state changes
3. **Default SPT switchover** meant every receiver created its own (S,G) on the core, so state grew linearly with **the number of receivers**
4. **The RP carried the initial traffic of every channel**, becoming a bandwidth hotspot

<div class="zh" markdown="1">

1. **状态数量 = 频道数 × 接收者分布**：600 频道 × 多个 (S,G) 分支，核心维护数万条 mroute
2. **每次频道切换**：IGMP Leave → 组特定查询 → Prune → 新组 Join → (*,G) 到 RP → SPT 切换 → 多次状态变更
3. **默认 SPT 切换**导致每个接收者都在核心建立独立 (S,G)，状态量随"接收者数"线性增长
4. **RP 承载了全部频道的初始流量**，形成带宽热点

</div>

**Optimisation plan (ordered by benefit)**:

<div class="zh" markdown="1">

**优化方案（按收益排序）**：

</div>

| Action | Effect |
|------|------|
| **Move to SSM (232/8 + IGMPv3 or SSM Mapping)** | **no RP, no (*,G), no SPT switchover**; state is only (S,G) and zapping is a single Join |
| **Converge multicast into VLANs (MVR)** | multicast no longer enters every user VLAN; Layer 2 flooding falls sharply |
| **`ip pim spt-threshold infinity` (if SM is kept)** | a large reduction in state (shared tree kept), at the cost of higher latency |
| **Channel pre-join (Fast Channel Change)** | join the target group in advance when zapping, reducing black time |
| **PIM Snooping / multicast boundaries on the core** | restrict multicast to the links that need it |

<div class="zh" markdown="1">

| 动作 | 效果 |
|------|------|
| **改为 SSM（232/8 + IGMPv3 或 SSM Mapping）** | **去掉 RP、去掉 (*,G)、去掉 SPT 切换**，状态只有 (S,G)，切换只发生一次 Join |
| **组播 VLAN 收敛（MVR）** | 组播不再进每个用户 VLAN，二层泛洪大幅减少 |
| **`ip pim spt-threshold infinity`（若保留 SM）** | 大幅减少状态（保留共享树），代价是时延上升 |
| **频道预加入（Fast Channel Change）** | 切换时提前加入目标组，减少黑屏 |
| **核心开启 PIM Snooping / 组播边界** | 限制组播只在必要链路 |

</div>

**Result**: after moving to SSM the core mroute count fell 70%, CPU dropped to 15%, and zapping time went from 10 s to 1.5 s.

<div class="zh" markdown="1">

**结果**：改 SSM 后核心 mroute 条目下降 70%，CPU 降到 15%，频道切换时间从 10 秒降到 1.5 秒。

</div>

**Lesson**: **PIM-SM's complexity is a tax paid for "unknown sources", while IPTV sources are known** — for this class of scenario SSM is a "dimension reduction", not an "optimisation". The question to ask during design is: "is the source fixed?" If it is, SSM is the default answer.

<div class="zh" markdown="1">

**教训**：**PIM-SM 的复杂度是为"未知源"付的税，而 IPTV 的源是已知的** —— 这类场景用 SSM 是"降维"而不是"优化"。设计阶段就该问："源固定吗？"如果固定，SSM 是默认答案。

</div>

### 🔥 Case 6: Cross-Domain Multicast — "Ping Works, PIM Neighbours Are Up, but No Stream" · 🔥 案例六：跨域组播"能 ping 通、PIM 邻居也在，但收不到流"

**Scenario**: headquarters and a new campus interconnected through a third-party carrier MPLS VPN. The source is at headquarters (239.10.1.1) and campus receivers got nothing. PIM neighbours came up normally between PE and CE, and unicast connectivity was fine.

<div class="zh" markdown="1">

**场景**：总部与新建园区之间通过第三方运营商 MPLS VPN 互联。总部有组播源（239.10.1.1），园区接收者收不到。PIM 邻居在 PE-CE 之间正常建立，单播互通正常。

</div>

**Investigation and root cause (several problems stacked)**:

<div class="zh" markdown="1">

**排查与根因（多个问题叠加）**：

</div>

| # | Problem | Symptom |
|---|------|------|
| 1 | **the carrier had not enabled MVPN** (unicast VPN only) | PIM Hellos only between CE and PE; PEs did not forward multicast to each other |
| 2 | after temporarily using a **GRE tunnel**, **the MTU was not adjusted** | large packets dropped; picture pixellated while small packets (signalling) were fine |
| 3 | **the RPF check used the unicast table**, which pointed at the wrong tunnel endpoint | the tunnel came up but RPF failed |
| 4 | **the RP was unreachable** (the RP is at headquarters and the campus had no PIM path to it) | the shared tree could not be built |

<div class="zh" markdown="1">

| # | 问题 | 现象 |
|---|------|------|
| 1 | **运营商未启用 MVPN**（只做单播 VPN） | PIM Hello 只在 CE-PE 之间，PE 之间不转发组播 |
| 2 | 临时用 **GRE 隧道**承载组播后，**MTU 未调整** | 大包丢弃，画面花屏但小包（信令）正常 |
| 3 | **RPF 检查用单播表**，指向 GRE 隧道对端不正确 | 隧道能建，但 RPF 失败 |
| 4 | **RP 不可达**（RP 在总部，园区没有到 RP 的 PIM 路径） | 共享树建不起来 |

</div>

**Fix (the standard cross-domain multicast design)**:

<div class="zh" markdown="1">

**修复（标准跨域组播设计）**：

</div>

```
Options (in priority order):
① the carrier provides MVPN (multicast VPN) -> cleanest; the CE only runs PIM
② build your own GRE/VXLAN tunnel to carry multicast -> watch MTU, RPF and tunnel multicast configuration
③ move to SSM -> no RP needed, only source-prefix reachability (plain unicast BGP usually suffices)
```

<div class="zh" markdown="1">

```
方案选择（按优先级）：
① 运营商提供 MVPN（组播 VPN） → 最干净，CE 只跑 PIM
② 自建 GRE/VXLAN 隧道承载组播 → 需注意 MTU、RPF、tunnel 的组播配置
③ 改用 SSM → 无需 RP，只需源前缀可达（通常单播 BGP 已满足）
```

</div>

```cfg
! key configuration for carrying multicast over a GRE tunnel
interface Tunnel0
 ip address 172.16.0.1 255.255.255.252
 ip pim sparse-mode
 ip mtu 1400                       ! key: reserve room for the GRE header to avoid fragmentation
 tunnel source 203.0.113.1
 tunnel destination 198.51.100.1
 tunnel mode gre ip

! point RPF at the tunnel (when the unicast route does not go through it)
ip mroute 10.1.1.1 255.255.255.255 Tunnel0
```

<div class="zh" markdown="1">

```cfg
! GRE 隧道承载组播的关键配置
interface Tunnel0
 ip address 172.16.0.1 255.255.255.252
 ip pim sparse-mode
 ip mtu 1400                       ! 关键：为 GRE 头预留，避免分片
 tunnel source 203.0.113.1
 tunnel destination 198.51.100.1
 tunnel mode gre ip

! RPF 指向隧道（若单播路由不经隧道）
ip mroute 10.1.1.1 255.255.255.255 Tunnel0
```

</div>

**Acceptance checklist (always check these for cross-domain multicast)**:

<div class="zh" markdown="1">

**验收清单（跨域组播必查）**：

</div>

| Check item | Method |
|-------|------|
| Is multicast carried by the intermediate network | `show ip mroute` on the PE/CE shows whether multicast is forwarded |
| Is the MTU sufficient | large-packet ping (`ping 239.10.1.1 size 1400 df-bit`) |
| Is RPF correct | `show ip rpf <source>` matches the tunnel/actual ingress |
| Is the RP reachable | `show ip pim rp mapping` + `ping` the RP |
| MSDP (if ASM is used) | `show ip msdp sa-cache` has SAs |
| End to end | the receiver really decodes, not merely "the group address answers ping" |

<div class="zh" markdown="1">

| 检查项 | 方法 |
|-------|------|
| 组播是否被中间网络承载 | `show ip mroute` 在 PE/CE 上看是否有组播转发 |
| MTU 是否足够 | 大包 ping（`ping 239.10.1.1 size 1400 df-bit`） |
| RPF 是否正确 | `show ip rpf <源>` 与隧道/实际入接口一致 |
| RP 可达性 | `show ip pim rp mapping` + `ping` RP |
| MSDP（若用 ASM） | `show ip msdp sa-cache` 有 SA |
| 端到端 | 接收端实际解码，而不只是"能 ping 通组播地址" |

</div>

**Lesson**: **cross-domain multicast failures usually mean "four things are false at the same time"**: transport (MVPN/tunnel), MTU, RPF, RP reachability. Verifying each item beats guessing where it broke.

<div class="zh" markdown="1">

**教训**：**组播跨域失败往往是"四件事同时不成立"**：承载（MVPN/隧道）、MTU、RPF、RP 可达。逐项验证比"猜哪里断了"快得多。

</div>

### 🔥 Case 7: Live-Live Dual Paths, and One Construction Job Cut Both Fibres · 🔥 案例七：Live-Live 双路设计，一次施工挖断两根光纤

**Scenario**: a stock exchange's market-data multicast used Live-Live: two sources, two paths, two group addresses, and dual-leg reception. The design document said "physically separated paths, 99.999% availability".

<div class="zh" markdown="1">

**场景**：证券交易所的行情组播采用 Live-Live：两个源、两条路径、两个组地址，接收端双路接收。设计文档写着"路径物理分离，可用性 99.999%"。

</div>

**The event**: municipal construction cut a fibre cable and **both paths went down for 40 minutes**; market data stopped completely.

<div class="zh" markdown="1">

**事件**：市政施工挖断光缆，**两条路径同时中断 40 分钟**，行情完全中断。

</div>

**Root cause (the step the design review skipped)**:

<div class="zh" markdown="1">

**根因（设计评审没做的那一步）**：

</div>

1. The **logical topology** of the two paths was indeed separate (different routers, different carriers)
2. But the **physical route** shared one section of the same duct (both cables ran through the same trench)
3. The design document had only a logical diagram, **no physical route diagram**
4. No single-point-of-failure (SPOF) analysis was done — i.e. "which physical facilities do both paths share"

<div class="zh" markdown="1">

1. 两条路径的**逻辑拓扑**确实分离（不同路由器、不同运营商）
2. 但**物理路由**共用同一个管道井的一段（两条光缆走同一沟）
3. 设计文档只有逻辑图，**没有物理路由图**
4. 也没有做"单点故障分析（SPOF）"—— 即"哪些物理设施被两条路径共享"

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Action | Explanation |
|------|------|
| **Draw the physical route diagram** | duct, manhole, entry room and power for each path, annotated segment by segment |
| **SPOF analysis** | list every physical facility shared by both paths and evaluate alternatives |
| **Add a third path** | different carrier + different physical route (microwave/satellite as a backstop) |
| **Rehearse** | periodic real link-break drills (not "pull the line card", but cut the physical link) |
| **Write the assumption into the SLA** | "99.999% assumes physical route separation; simultaneous trench cuts are outside this scope" |

<div class="zh" markdown="1">

| 动作 | 说明 |
|------|------|
| **画物理路由图** | 每条路径的管道、井、进线室、供电，逐段标注 |
| **SPOF 分析** | 列出被两条路径共享的所有物理设施，评估替代方案 |
| **引入第三条路径** | 不同运营商 + 不同物理路由（如微波/卫星兜底） |
| **演练** | 定期真实断链演练（不是"拔板卡"，而是断物理链路） |
| **把假设写进 SLA** | "99.999% 基于物理路由分离的前提；若施工导致同沟中断，不在此范围" |

</div>

**Lesson**: **the effectiveness of redundancy depends only on "the number of shared points", not on "the number of paths"**. This applies to Live-Live multicast, dual-active data centres and dual-carrier egress alike — **logical redundancy is not physical redundancy**.

<div class="zh" markdown="1">

**教训**：**冗余设计的有效性只取决于"共享点的数量"，不取决于"路径的条数"**。这一条对 Live-Live 组播、双活数据中心、双运营商出口全部适用 —— **逻辑冗余不等于物理冗余**。

</div>

### 🔥 Case 8: SSM Was Configured Correctly, yet the "TV in the Old Meeting Room" Showed Nothing · 🔥 案例八：SSM 明明配好了，但"老会议室的电视"就是看不了

**Scenario**: the campus migrated its video service to SSM (232.10.1.0/24, source 10.1.1.1) and configured `ip pim ssm default` everywhere. Most meeting rooms worked. Yet **the two meeting rooms on the 3rd floor of Building B** stayed black while every other floor was fine.

<div class="zh" markdown="1">

**场景**：园区把视频业务改造为 SSM（232.10.1.0/24，源 10.1.1.1），全网配置 `ip pim ssm default`，大部分会议室正常。但**B 栋 3 楼的两间会议室**始终黑屏，其他楼层正常。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Command / action | Result |
|------|----------|------|
| 1 | LHR of the failing floor: `show ip igmp groups` | 232.10.1.1 is visible, but the **group is shown as an IGMP v2 membership** |
| 2 | Packet capture (access switch port mirror) | the hosts send **IGMPv2 Reports** (type 0x16), **not v3** |
| 3 | What else lives in that VLAN | an **old projection gateway / set-top box** that only supports IGMPv2 |
| 4 | LHR: `show ip igmp interface Vlan300` | **IGMP version: v2** (a v2 Report was received, so the interface entered compatibility mode) |
| 5 | Compare with a healthy floor | that VLAN contains only v3 hosts; `show igmp interface` shows v3 |

<div class="zh" markdown="1">

| 步骤 | 命令/动作 | 结果 |
|------|----------|------|
| 1 | 故障楼层 LHR：`show ip igmp groups` | 能看到 232.10.1.1，但**组显示为 IGMP v2 成员** |
| 2 | 抓包（接入交换机镜像） | 主机发的是 **IGMPv2 Report**（类型 0x16），**不是 v3** |
| 3 | 同一 VLAN 里还有什么设备 | 一台**老式投影网关/机顶盒**只支持 IGMPv2 |
| 4 | LHR：`show ip igmp interface Vlan300` | **IGMP 版本：v2**（因为收到了 v2 Report，进入兼容模式） |
| 5 | 对比正常楼层 | 该 VLAN 内只有 v3 主机，`show ip igmp interface` 显示 v3 |

</div>

**Root cause**:

<div class="zh" markdown="1">

**根因**：

</div>

```
IGMP version negotiation is "backward compatible":
  as soon as one IGMPv2 host appears inside a VLAN
  -> the router interface enters v2 compatibility mode (some implementations per group, some per interface)
  -> the v3 INCLUDE (source filter) information is discarded
  -> the SSM (S,G) cannot be built (the source is unknown)
  -> the symptom is "no picture" (some implementations fall back to ASM and look for an RP, which also fails)
```

<div class="zh" markdown="1">

```
IGMP 版本协商是"向下兼容"：
  只要 VLAN 内出现一个 IGMPv2 主机
  → 路由器该接口进入 v2 兼容模式（部分实现按组进入，部分按接口）
  → v3 的 INCLUDE（源过滤）信息被丢弃
  → SSM 的 (S,G) 无法建立（因为不知道源）
  → 表现为"画面出不来"（有些实现会退化为 ASM 去找 RP，同样失败）
```

</div>

**Fixes (three, in order of preference)**:

<div class="zh" markdown="1">

**修复（三种，按推荐度）**：

</div>

| Option | What to do | Advantage | Drawback |
|------|------|------|------|
| **① Separate VLANs (recommended)** | move the legacy devices into their own VLAN and use **SSM Mapping** there | best experience for the new devices | requires re-cabling / VLAN changes |
| **② SSM Mapping network-wide** | configure `ip igmp ssm-map static` on the LHR to map the v2 (*,G) to (S,G) | no terminal or topology changes | must be configured on every LHR; a source change means a config change |
| **③ Replace the legacy devices** | upgrade to IGMPv3-capable terminals | eliminates the root cause | cost and lead time |

<div class="zh" markdown="1">

| 方案 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| **① 分离 VLAN（推荐）** | 把老设备迁到独立 VLAN，该 VLAN 用 **SSM Mapping** | 新设备体验最佳 | 需要重新布线/改 VLAN |
| **② 全网 SSM Mapping** | 在 LHR 上配 `ip igmp ssm-map static`，把 v2 的 (*,G) 映射为 (S,G) | 不改终端、不改网络结构 | 每台 LHR 都要配；源变更需改配置 |
| **③ 更换老设备** | 升级到支持 IGMPv3 的终端 | 根治 | 成本与工期 |

</div>

```cfg
! Option ②: enable SSM Mapping on the LHR of the failing floors
ip igmp ssm-map enable
ip igmp ssm-map static 50 10.1.1.1
access-list 50 permit 232.10.1.0 0.0.0.255

! Verify
LHR# show ip igmp ssm-map 232.10.1.1
LHR# show ip mroute 232.10.1.1
(the entry (10.1.1.1, 232.10.1.1) should appear)
```

<div class="zh" markdown="1">

```cfg
! 方案②：在故障楼层的 LHR 上启用 SSM Mapping
ip igmp ssm-map enable
ip igmp ssm-map static 50 10.1.1.1
access-list 50 permit 232.10.1.0 0.0.0.255

! 验证
LHR# show ip igmp ssm-map 232.10.1.1
LHR# show ip mroute 232.10.1.1
（应出现 (10.1.1.1, 232.10.1.1)）
```

</div>

**Why only those two meeting rooms failed (one level deeper)**:

<div class="zh" markdown="1">

**为什么只在两间会议室出问题（深入一层）**：

</div>

Those two rooms share **one legacy AV matrix** left over from the room refurbishment. After power-on it periodically sends IGMPv2 Reports. Therefore:

<div class="zh" markdown="1">

这两间会议室接了**同一台老式 AV 矩阵**（会议室改造时遗留），它上电后会周期性地发 IGMPv2 Report。所以：

</div>

- **When the AV matrix is powered off**: only v3 in the VLAN → normal
- **When the AV matrix is powered on**: v2 compatibility → SSM fails for the whole VLAN
- **That device is the source of the "intermittent" behaviour**

<div class="zh" markdown="1">

- **AV 矩阵不开机时**：VLAN 内只有 v3 → 正常
- **AV 矩阵开机后**：进入 v2 兼容 → 全 VLAN 的 SSM 失效
- **"时好时坏"的根源就是这个设备**

</div>

> 💡 **This is the classic shape of a "version compatibility" failure**: one legacy device can drag down a modern feature for an entire VLAN, and it only fails **while that device is powered on** (hence "just reboot it and it works", "it works again today"). When designing SSM you must ask: **are there any v2 devices in this VLAN? Will there be any in the future?**

<div class="zh" markdown="1">

> 💡 **这是"版本兼容"最经典的故障形态**：一台老设备能拖垮整个 VLAN 的现代特性，而且**只在它开机时失效**（所以"重启一下就好了""今天又能用了"）。设计 SSM 时必须问：**这个 VLAN 里有没有 v2 设备？将来会不会有？**

</div>

**Lesson**: **the precondition for SSM is not "the network supports IGMPv3" but "every terminal in the Layer 2 domain is v3".** In a mixed environment the standard answer is not "change the network" but "**VLAN isolation plus SSM Mapping as a safety net**".

<div class="zh" markdown="1">

**教训**：**SSM 的前提不是"网络支持 IGMPv3"，而是"整个二层域的终端都是 v3"。** 混合环境的标准答案不是"改网络"，而是"**VLAN 隔离 + SSM Mapping 兜底**"。

</div>

### 🔥 Case 9: Two Floors, Identical Configuration, but "After 17:30 Only the 6th Floor Loses Video" · 🔥 案例九：两个楼层一样配置，但"17:30 之后只有 6 楼看不了视频"

**Scenario**: dual core + HSRP gateways + several distribution switches. One day the 6th floor reported "video conferences often fail to connect after 5:30 pm"; other floors were fine. A configuration spot check showed "identical configuration" on all floors.

<div class="zh" markdown="1">

**场景**：双核心 + HSRP 网关 + 多台汇聚。某天起，6 楼报告"下午 5 点半之后视频会议经常连不上"，其他楼层正常。配置抽查显示所有楼层"配置一致"。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | 6th floor access switch: `show ip igmp snooping groups` | the group entry **appears and disappears** |
| 2 | The VLAN's mrouter pointer | points at **Core A** |
| 3 | `show ip mroute` on Core A | **no state for that group** |
| 4 | `show ip mroute` on Core B | **the state exists and is forwarding** |
| 5 | `show standby brief` (HSRP) | **A = Active, B = Standby** |
| 6 | `show ip pim neighbor` (access VLAN) | **B is the PIM DR** |
| 7 | Why only after 17:30 | after 17:30 **Core A's CPU spikes because of another service**, and A carries the `ip igmp snooping querier` configuration |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | 6 楼接入交换机 `show ip igmp snooping groups` | 组表**时有时无** |
| 2 | 该 VLAN 的 mrouter 指向 | 指向**核心 A** |
| 3 | 核心 A 上 `show ip mroute` | **没有该组的状态** |
| 4 | 核心 B 上 `show ip mroute` | **有该组状态，且在转发** |
| 5 | `show standby brief`（HSRP） | **A = Active，B = Standby** |
| 6 | `show ip pim neighbor`（接入 VLAN） | **B 是 PIM DR** |
| 7 | 为什么 17:30 之后才出问题 | 17:30 后**核心 A 的 CPU 因另一个业务飙高**，且 A 上有 `ip igmp snooping querier` 配置 |

</div>

**Root cause (two mis-placed roles plus a time trigger)**:

<div class="zh" markdown="1">

**根因（两个角色错位 + 时间触发）**：

</div>

```
Normal: B is the PIM DR -> B sends Joins -> B holds the multicast state -> multicast works
        A is the Querier (low IP) -> A sends queries -> group membership is maintained

After 17:30: A's CPU is high -> IGMP query packets are delayed/dropped
        -> the access switch snooping table starts ageing
        -> the group is removed at the access layer -> multicast breaks
        -> the user rejoins -> brief recovery -> breaks again (periodic)
```

<div class="zh" markdown="1">

```
正常时：B 是 PIM DR → B 发 Join → B 有组播状态 → 组播正常
       A 是 Querier（低 IP）→ A 发查询 → 组成员维持

17:30 后：A 的 CPU 高 → IGMP 查询报文被延迟/丢弃
       → 接入交换机 Snooping 表开始老化
       → 组在接入层被删除 → 组播中断
       → 用户重新加入 → 短暂恢复 → 又断（周期性）
```

</div>

**The core problem is not "high CPU" but "scattered roles"**:

<div class="zh" markdown="1">

**核心问题不是"CPU 高"，而是"角色分散"**：

</div>

| Role | Where | Responsibility | Failure impact |
|------|-------|------|---------|
| HSRP Active | A | unicast default gateway | unicast forwarding |
| PIM DR | B | sends Joins towards the RP/source | multicast upstream |
| IGMP Querier | A | maintains group membership | **group membership ageing** |
| Assert Winner | depends | de-duplication on the same LAN | — |

<div class="zh" markdown="1">

| 角色 | 在哪台 | 职责 | 故障影响 |
|------|-------|------|---------|
| HSRP Active | A | 单播默认网关 | 单播转发 |
| PIM DR | B | 发 Join 到 RP/源 | 组播上行 |
| IGMP Querier | A | 维持组成员 | **组成员老化** |
| Assert Winner | 视情况 | 同 LAN 去重 | — |

</div>

**Fix**:

<div class="zh" markdown="1">

**修复**：

</div>

```cfg
! Plan: consolidate the "multicast-related roles" onto one device
! Core B (the multicast forwarding point): make it PIM DR + Querier + HSRP Active
interface Vlan100
 standby 1 ip 10.100.0.1
 standby 1 priority 120
 standby 1 preempt
 ip pim dr-priority 200                ! make sure B is the DR
 ip igmp version 3

! Core A: backup only (low priority)
interface Vlan100
 standby 1 ip 10.100.0.1
 standby 1 priority 100
 ip pim dr-priority 1

! If organisational constraints force A to be the gateway, keep multicast state on both paths
! or use FHRP-Aware PIM (so the Standby also maintains PIM state)
```

<div class="zh" markdown="1">

```cfg
! 方案：把"组播相关角色"集中到一台设备上
! 核心 B（组播转发点）：设为 PIM DR + Querier + HSRP Active
interface Vlan100
 standby 1 ip 10.100.0.1
 standby 1 priority 120
 standby 1 preempt
 ip pim dr-priority 200                ! 确保 B 是 DR
 ip igmp version 3

! 核心 A：只作为备份（低优先级）
interface Vlan100
 standby 1 ip 10.100.0.1
 standby 1 priority 100
 ip pim dr-priority 1

! 若必须由 A 做网关（组织结构限制），则在两条路径上都保留组播状态
! 或用 FHRP-Aware PIM（让 Standby 也维护 PIM 状态）
```

</div>

**Another (more fundamental) direction**: **move the IGMP Querier from the core down to the access switch** and give it an explicit address, so that membership maintenance no longer depends on the core CPU:

<div class="zh" markdown="1">

**另一个修复方向（更根本）**：**把 IGMP Querier 从核心移到接入交换机**，并显式指定地址，让组成员维持不依赖核心 CPU：

</div>

```cfg
! Access switch
ip igmp snooping querier
ip igmp snooping querier address 10.100.0.250   ! explicit and stable
ip igmp snooping querier query-interval 60
```

<div class="zh" markdown="1">

```cfg
! 接入交换机
ip igmp snooping querier
ip igmp snooping querier address 10.100.0.250   ! 明确、稳定
ip igmp snooping querier query-interval 60
```

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **"Identical configuration" does not mean "identical behaviour"** — the **role assignment** between the two devices in the same VLAN is exactly where the behavioural difference comes from.
2. **HSRP Active, PIM DR and IGMP Querier are three independent elections**, and their directions can even be opposite (HSRP high priority, DR high priority, Querier lowest IP). **CCDE design must plan these three roles explicitly** instead of letting the protocols pick.
3. **For a multicast failure that "only happens at a certain time of day", always ask "what changed at that time"** (CPU, backup jobs, a source starting, a device rebooting) — the root cause is often outside multicast.

<div class="zh" markdown="1">

1. **"配置一致"不等于"行为一致"** —— 同一个 VLAN 内两台设备的**角色分配**才是行为差异的来源。
2. **HSRP Active、PIM DR、IGMP Querier 是三个独立选举**，方向甚至相反（HSRP 高优先级、DR 高优先级、Querier 低 IP）。**CCDE 设计必须显式规划这三个角色**，而不是让协议自己选。
3. **"只在某个时间点出问题"的组播故障，一定要问"那个时间点改变了什么"**（CPU、备份任务、某个源启动、某台设备重启）—— 很多时候根因在组播之外。

</div>

### 🔥 Case 10: One PC's Player "Zapped Channels Suicidally" and Crippled Multicast for the Whole Campus · 🔥 案例十：一台 PC 的播放器"自杀式换台"，打瘫了整个园区的组播

**Scenario**: campus IPTV (PIM-SM + Snooping). From 2 pm one day, **all video on several floors stuttered at the same time**. Core and distribution CPU were low, but the **access uplinks were saturated**.

<div class="zh" markdown="1">

**场景**：园区 IPTV（PIM-SM + Snooping），某天下午 2 点起，**多个楼层的所有视频同时卡顿**，核心与汇聚的 CPU 不高，但**接入层上联链路流量打满**。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | Distribution uplink interfaces | 100% egress utilisation, and it was **all multicast** |
| 2 | Distribution `show ip mroute count` | **(S,G) entries grew from 300 to 4,000+ within 10 seconds** |
| 3 | `show ip igmp snooping groups count` (access) | a single switch had **6,000+ groups** |
| 4 | Per-port inspection | **one port held 3,800 groups**, all different group addresses |
| 5 | Find that host | a PC's player was "channel scanning in a loop" (an application bug, switching every 20 ms) |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | 汇聚上联接口 | 出方向利用率 100%，且**全是组播** |
| 2 | 汇聚 `show ip mroute count` | **(S,G) 条目在 10 秒内从 300 涨到 4,000+** |
| 3 | `show ip igmp snooping groups count`（接入） | 单台交换机 **6,000+ 组** |
| 4 | 逐端口排查 | **某个端口有 3,800 个组**，全部是不同组地址 |
| 5 | 找到那台主机 | 一台 PC 的播放器在"循环扫描频道"（应用 Bug，每 20 ms 切一个） |

</div>

**Root-cause chain**:

<div class="zh" markdown="1">

**根因链**：

</div>

```
The player sends a Join every 20 ms (a different group each time)
-> the access switch snooping table fills instantly (thousands of entries)
-> without a Querier, ageing cannot keep up (Leaves are being blasted out too)
-> the ageing mechanism cannot process them -> some entries are overwritten/flooded
-> groups with no matching entry are 【flooded】 to the whole VLAN
-> 8 Mbps per group x dozens of groups = access uplink saturated
-> the whole campus stutters
```

<div class="zh" markdown="1">

```
播放器每 20 ms 发一次 Join（不同组）
→ 接入交换机 Snooping 表被瞬间填满（数千条）
→ 无 Querier 老化跟不上（Leave 也在狂发）
→ 交换机表项老化机制来不及处理 → 部分表项被覆盖/泛洪
→ 未命中表项的组播被【泛洪】到整个 VLAN
→ 每组 8 Mbps × 数十组 = 接入上联被打满
→ 全网卡顿
```

</div>

**Fix (three layers of defence, all required)**:

<div class="zh" markdown="1">

**修复（三层防线，必须全有）**：

</div>

```cfg
! Defence 1: limit the number of groups per port at the access layer (most effective)
interface range Gi1/0/1 - 48
 ip igmp limit 20                    ! at most 20 groups per port (derive from the service profile)

! Defence 2: limit the IGMP message rate
ip igmp snooping vlan 100 limit 200   ! per-VLAN group limit
! on some platforms: ip igmp rate-limit

! Defence 3: switch-side multicast storm control (careful, it will kill legitimate bulk traffic)
interface Gi1/0/1
 storm-control multicast level 20.00
```

<div class="zh" markdown="1">

```cfg
! 防线 1：接入层限制每端口组数（最有效）
interface range Gi1/0/1 - 48
 ip igmp limit 20                    ! 每端口最多 20 个组（按业务画像定）

! 防线 2：限制 IGMP 报文速率
ip igmp snooping vlan 100 limit 200   ! 每 VLAN 组数上限
! 部分平台：ip igmp rate-limit

! 防线 3：交换机侧的组播风暴控制（谨慎，会误杀大流量）
interface Gi1/0/1
 storm-control multicast level 20.00
```

</div>

**Three things that must be done at the same time (otherwise it recurs)**:

<div class="zh" markdown="1">

**同时要做的三件事（不配就会复发）**：

</div>

| Action | Explanation |
|------|------|
| **Find and fix the player** | the application bug is the root cause ("channel scanning" is application-layer behaviour) |
| **Alert on "sudden group-count change"** | more than 50 groups on a single port, or a 50% rise in network-wide (S,G) count within 5 minutes → P1 alarm |
| **Build a "group whitelist" at the access layer** | allow only planned groups (`ip igmp profile` applied to ports); reject "unplanned groups" outright |

<div class="zh" markdown="1">

| 动作 | 说明 |
|------|------|
| **定位并修复播放器** | 应用 Bug 才是根因（"扫描频道"是应用层行为） |
| **建立"组数突变"告警** | 单端口组数 > 50 或全网 (S,G) 数 5 分钟涨 50% → P1 告警 |
| **在接入层做"组白名单"** | 只允许规划内的组（`ip igmp profile` + 应用到端口），把"未规划组"直接拒绝 |

</div>

```cfg
! Group whitelist (Cisco syntax)
ip igmp profile 10
 permit
 range 239.10.0.0 239.10.255.255
 range 232.10.0.0 232.10.255.255
!
ip igmp profile 20
 deny
 range 0.0.0.0 255.255.255.255
!
interface range Gi1/0/1 - 48
 ip igmp filter 10
```

<div class="zh" markdown="1">

```cfg
! 组白名单（Cisco 语法）
ip igmp profile 10
 permit
 range 239.10.0.0 239.10.255.255
 range 232.10.0.0 232.10.255.255
!
ip igmp profile 20
 deny
 range 0.0.0.0 255.255.255.255
!
interface range Gi1/0/1 - 48
 ip igmp filter 10
```

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **A multicast "capacity attack" needs no malice** — one buggy client is enough to cripple the network.
2. **`ip igmp limit` and the "group whitelist" are the two seat belts at the access layer**; you need both: the first caps the "volume", the second stops "out-of-bounds".
3. **A "sudden group-count change" is the strongest early-warning signal** — it appears earlier than "high traffic" and faster than "user complaints".

<div class="zh" markdown="1">

1. **组播的"容量攻击"不需要恶意** —— 一个有 Bug 的客户端就能打瘫全网。
2. **`ip igmp limit` 和"组白名单"是接入层的两条安全带**，缺一不可：前者防"量"，后者防"越界"。
3. **"组数突变"是最强的早期告警信号** —— 它比"流量高"更早出现，比"用户投诉"更快。

</div>

### 🔥 Case 11: The Data Centre Moved to EVPN, and Market-Data Multicast Latency Went from 200 μs to 8 ms · 🔥 案例十一：数据中心换了 EVPN，组播行情延迟从 200 μs 涨到 8 ms

**Scenario**: a securities firm's data centre migrated from traditional Layer 3 + multicast to VXLAN/EVPN (spine-leaf). After the migration, market-data multicast (multiple sources, small packets, high rate) saw **end-to-end latency rise from 200 μs to 8 ms**, with **packet loss at peak**. The underlay was 100G spine-leaf; bandwidth was nowhere near the bottleneck.

<div class="zh" markdown="1">

**场景**：某证券公司数据中心从传统三层+组播改造为 VXLAN/EVPN（spine-leaf）。行情组播（多播源、小包、高频）在改造后**端到端延迟从 200 μs 上升到 8 ms**，且**峰值时出现丢包**。Underlay 是 100G spine-leaf，带宽完全不是瓶颈。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | VTEP configuration | using **ingress replication** (per-copy unicast) |
| 2 | Number of receiving VTEPs | **48** (every leaf has a set of market-data receivers) |
| 3 | Egress traffic on the source VTEP | the feed is **replicated 48 times**, saturating the egress instantly |
| 4 | Queue statistics | the micro-bursts caused by replication produced **output drops** |
| 5 | Latency analysis | replication queues in the CPU/hardware replication engine → per-packet latency rises from μs to ms |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | VTEP 配置 | 使用 **ingress replication**（逐份复制单播） |
| 2 | 接收 VTEP 数量 | **48 个**（每个 leaf 都有一批行情接收者） |
| 3 | 源侧 VTEP 出口流量 | 行情流 **被复制 48 份**，出口瞬间打满 |
| 4 | 队列统计 | 复制产生的微突发导致 **出方向丢包（output drops）** |
| 5 | 时延分析 | 复制在 CPU/硬件复制引擎排队 → 单包延迟从 μs 级升到 ms 级 |

</div>

**Root cause**:

<div class="zh" markdown="1">

**根因**：

</div>

```
The nature of ingress replication:
  the source VTEP makes one unicast copy for 【every VTEP that has receivers】
  -> the replication happens locally on the ingress VTEP
  -> small-packet, high-rate traffic (market data) creates an enormous "per-packet replication cost"
  -> the replication engine queues -> latency and loss

Order of magnitude:
  peak feed 500k packets/s x 48 VTEPs = 24 million replications/s
  -> no replication engine survives that (and it is "ingress" work, so it cannot be bought with bandwidth)
```

<div class="zh" markdown="1">

```
Ingress Replication 的本质：
  源 VTEP 为【每个有接收者的 VTEP】复制一份单播
  → 复制在 ingress VTEP 本地完成
  → 小包高频流量（行情）会产生巨大的"每包复制开销"
  → 复制引擎排队 → 时延与丢包

数量级：
  行情峰值 500k 包/秒 × 48 个 VTEP = 2400 万次复制/秒
  → 任何复制引擎都扛不住（且这是"入方向"的工作，无法用带宽换）
```

</div>

**Fix options (ordered by effect)**:

<div class="zh" markdown="1">

**修复方案（按效果排序）**：

</div>

| Option | What to do | Effect | Cost |
|------|------|------|------|
| **① Multicast in the underlay (first choice)** | run PIM (SSM) in the underlay; VTEPs receive BUM over underlay multicast | **one copy replicated to all leaves**, replication cost falls from 48 to 1 (performed by the underlay) | the underlay must support multicast (spines too) |
| **② EVPN multicast (IGMP Snooping over EVPN)** | synchronise membership via EVPN and **build trees only towards leaves with receivers** | most bandwidth-efficient and precise | complex, vendor support required |
| **③ Assisted Replication** | nominate "replication servers" (AR-LEAF) | spreads the load off the source VTEP | extra design and capacity |
| **④ Reduce the number of receiving VTEPs** | concentrate market-data receivers on a few leaves | immediate effect | requires redesigning server placement (may not be feasible) |
| **⑤ Fall back to traditional Layer 3 multicast** | carry the feed on a dedicated Layer 3 multicast network (not over VXLAN) | lowest latency | loses the flexibility of VXLAN |

<div class="zh" markdown="1">

| 方案 | 做法 | 效果 | 代价 |
|------|------|------|------|
| **① 组播 in underlay（首选）** | Underlay 跑 PIM（SSM），VTEP 通过 underlay 组播收 BUM | **一份流量复制到所有 leaf**，复制开销从 48 降到 1（由 underlay 网络复制） | Underlay 需要组播（spine 要支持） |
| **② EVPN 组播（IGMP Snooping over EVPN）** | 用 EVPN 同步组成员，**只为有接收者的 leaf 建树** | 最省带宽、最精确 | 实现复杂、需厂商支持 |
| **③ Assisted Replication** | 指定"复制服务器"（AR-LEAF） | 分担源 VTEP 负载 | 需额外设计与容量 |
| **④ 减少接收 VTEP 数** | 把行情接收者集中到少数 leaf | 立竿见影 | 需要改造服务器分布（可能不可行） |
| **⑤ 回退到传统三层组播** | 行情走独立的三层组播网络（不经 VXLAN） | 时延最优 | 失去 VXLAN 的灵活性 |

</div>

**The final hybrid design (what real projects do)**:

<div class="zh" markdown="1">

**最终的混合设计（真实项目做法）**：

</div>

```
Market-data multicast: dedicated VLAN + traditional Layer 3 multicast (not over VXLAN) + strict QoS
          (because the latency requirement is < 1 ms; any overlay encapsulation is unacceptable)

Other multicast (VDI broadcast, OS deployment, monitoring):
          over VXLAN, with the underlay carrying BUM via SSM multicast

Rationale: different services tolerate "encapsulation overhead" very differently
     market data: zero tolerance -> not over the overlay
     monitoring: tolerable -> over the overlay
```

<div class="zh" markdown="1">

```
行情组播：独立 VLAN + 传统三层组播（不经 VXLAN）+ 严格 QoS
          （因为时延要求 < 1 ms，任何 overlay 封装都不可接受）

其他组播（VDI 广播、OS 部署、监控）：
          走 VXLAN，underlay 用 SSM 组播承载 BUM

理由：不同业务对"封装开销"的容忍度差异巨大
     行情：零容忍 → 不过 overlay
     监控：可容忍 → 走 overlay
```

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **Ingress replication's bottleneck is not bandwidth but "per-packet replication cost"** — small-packet, high-rate traffic is its natural enemy.
2. **VXLAN is not "the default answer for all traffic"** — ultra-low-latency services (market data, HPC) may need to bypass the overlay.
3. **Multicast design must distinguish "service classes"** instead of "one transport for everything".

<div class="zh" markdown="1">

1. **Ingress Replication 的瓶颈不是带宽，是"每包复制开销"** —— 小包高频流量是它的死敌。
2. **VXLAN 不是"所有流量的默认答案"** —— 超低时延业务（行情、HPC）可能需要绕过 overlay。
3. **组播设计必须区分"业务类别"**，而不是"统一用一种承载方式"。

</div>

### 🔥 Case 12: After the Firewall Got a New Policy, "Old Channels Work, New Channels Are All Black" · 🔥 案例十二：防火墙换了新策略后，"老频道能看、新频道全黑"

**Scenario**: a stateful firewall sits between headquarters and a branch. The branch receives headquarters multicast (IGMP Proxy across the firewall). After a firewall policy change ("security hardening"), **the channel currently being watched kept working, but no new channel could be opened**.

<div class="zh" markdown="1">

**场景**：总部与分支之间有状态化防火墙。分支接收总部组播（跨防火墙用 IGMP Proxy）。某次防火墙策略变更（"安全加固"）后，**正在看的频道一直正常，任何新频道都打不开**。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | Branch LHR `show ip mroute` | the old group has (S,G) and is forwarding; the new group has **only (*,G), no (S,G)** |
| 2 | Branch LHR `show ip rpf <source>` | points towards the firewall (correct) |
| 3 | Packet capture (branch side) | the **Join for the new group goes out, but no multicast data comes back** |
| 4 | Firewall (proxy side) | **the IGMP Proxy state table is full** (`show ... igmp-proxy` shows max entries reached) |
| 5 | Firewall policy change log | a new rule was added: "only allow multicast for already-established sessions" → **the proxy no longer initiates new subscriptions** |
| 6 | Why old channels still work | their state was created before the policy change and **the session table has not aged out** |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | 分支 LHR `show ip mroute` | 老组有 (S,G) 且在转发；新组**只有 (*,G)，无 (S,G)** |
| 2 | 分支 LHR `show ip rpf <源>` | 指向防火墙方向（正确） |
| 3 | 抓包（分支侧） | 新组的 **Join 发出去了，但没有任何组播数据回来** |
| 4 | 防火墙（代理侧） | **IGMP Proxy 状态表满**（`show ... igmp-proxy` 显示 max entries 达到上限） |
| 5 | 防火墙策略变更记录 | 新增了一条"只允许已建立会话的组播"策略 → **Proxy 不再主动发起新订阅** |
| 6 | 老频道为什么正常 | 它们在策略变更前已建立状态，**会话表未老化** |

</div>

**Root cause (two problems stacked)**:

<div class="zh" markdown="1">

**根因（两个问题叠加）**：

</div>

```
① The policy blocked the "upstream IGMP Report for new groups"
   -> the proxy cannot create new state for 239.10.2.x
   -> the upstream (headquarters) never receives a Join
   -> the multicast tree is never built upstream of the firewall

② The firewall's IGMP Proxy entry limit (e.g. 500)
   -> old channels hold entries permanently (because somebody is always watching)
   -> even if the Report is permitted, a new group cannot squeeze in
```

<div class="zh" markdown="1">

```
① 策略把"新组的 IGMP Report 上行"拦住了
   → Proxy 无法为组 239.10.2.x 建立新状态
   → 上游（总部）从未收到 Join
   → 组播树在防火墙上游就没建

② 防火墙的 IGMP Proxy 条目上限（如 500）
   → 老频道长期占用条目（因为有人一直看）
   → 即使放通了 Report，新组也挤不进去
```

</div>

**Fix list**:

<div class="zh" markdown="1">

**修复清单**：

</div>

| Action | Explanation |
|------|------|
| **Permit IGMP (both directions)** | upstream Reports (destination 224.0.0.22 / the group address) and downstream Queries (source = upstream router, destination 224.0.0.1) |
| **Permit multicast data (one direction)** | source → branch, scoped by group address range (not "any UDP") |
| **Raise the proxy entry limit** | size it from "maximum concurrent groups", never from the default |
| **Configure multicast session ageing** | match the IGMP group timeout (otherwise "still holding the entry after the user stopped watching") |
| **Monitor proxy table utilisation** | alarm above 70% (this is the earliest signal of "new channels will not open") |

<div class="zh" markdown="1">

| 动作 | 说明 |
|------|------|
| **放通 IGMP（双向）** | 上行 Report（目的 224.0.0.22 / 组地址），下行 Query（源为上游路由器，目的 224.0.0.1） |
| **放通组播数据（单向）** | 源 → 分支方向，按组地址范围（不是"任意 UDP"） |
| **提高 Proxy 条目上限** | 按"最大并发组数"规划，不能按默认值 |
| **配置组播会话老化时间** | 与 IGMP 组超时匹配（否则"看完了还占着"） |
| **监控 Proxy 表使用率** | > 70% 告警（这是"新频道打不开"的最早信号） |

</div>

```cfg
! Branch LHR: make sure both IGMP and PIM point at the firewall
interface Gi0/0                       ! towards the firewall
 ip pim sparse-mode
 ip igmp version 3

! If the firewall does not support PIM at all and only offers IGMP Proxy:
! do not run PIM on this link at the branch (the adjacency will not form and it only interferes)
```

<div class="zh" markdown="1">

```cfg
! 分支侧 LHR：确认 IGMP 与 PIM 都指向防火墙
interface Gi0/0                       ! 朝防火墙
 ip pim sparse-mode
 ip igmp version 3

! 如果防火墙根本不支持 PIM，只有 IGMP Proxy：
! 分支侧不要在这条链路上跑 PIM（否则邻居建不起来，且会干扰）
```

</div>

**A more fundamental recommendation**:

<div class="zh" markdown="1">

**一个更根本的建议**：

</div>

| Option | Assessment |
|------|------|
| IGMP Proxy (status quo) | ★★☆☆☆ depends on firewall features and table capacity; with multiple firewalls you configure it segment by segment |
| **GRE tunnel across the firewall** | ★★★☆☆ simple and controllable, but MTU and encryption overhead |
| **SSM + static permits** | ★★★★☆ no proxy state (the source is fixed); the firewall only has to permit specific (S,G) |
| **Local caching/CDN instead of multicast** | ★★★★★ (if the business allows) — many "multicast across the WAN" requirements are really "content distribution" |

<div class="zh" markdown="1">

| 方案 | 评价 |
|------|------|
| IGMP Proxy（现状） | ★★☆☆☆ 依赖防火墙特性与表容量，跨多段防火墙时逐段配置 |
| **GRE 隧道跨防火墙** | ★★★☆☆ 简单可控，但 MTU 与加密开销 |
| **SSM + 静态放通** | ★★★★☆ 无需 Proxy 状态（源固定），防火墙只需放通固定 (S,G) |
| **本地缓存/CDN 替代组播** | ★★★★★（若业务允许）| 跨 WAN 组播的很多需求，本质是"内容分发" |

</div>

**Lesson**: **the firewall is the most easily overlooked "stateful device" in a multicast design**. It does not have a clean mroute table like a router; it has its own proxy state table and capacity limits. **"Old sessions work, new ones do not" is almost always "the state table is full" or "new subscriptions are blocked by policy"** — nothing to do with the multicast protocols themselves.

<div class="zh" markdown="1">

**教训**：**防火墙是组播设计中最容易被忽略的一段"状态设备"**。它不像路由器那样有清晰的 mroute 表，而是有自己的 Proxy 状态表与容量上限。**"老的通、新的不通"几乎总是"状态表满"或"新订阅被策略拦住"** —— 这与"组播协议"本身无关。

</div>

### 🔥 Case 13: The RP's CPU Suddenly Hit 90% and Multicast Became "On-and-Off" · 🔥 案例十三：RP 的 CPU 突然 90%，组播"时断时续"

**Scenario**: a single-RP PIM-SM network. After a new service went live the RP's CPU rose from 10% to 90%, and all multicast became "on-and-off" (freezing every few dozen seconds).

<div class="zh" markdown="1">

**场景**：单 RP 的 PIM-SM 网络，某个新业务上线后，RP 的 CPU 从 10% 涨到 90%，所有组播"时断时续"（每几十秒卡一下）。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | RP `show processes cpu sorted` | **the PIM process is using 80%+** |
| 2 | RP `show ip pim rp mapping` | normal |
| 3 | RP `show ip mroute count` | normal entry count |
| 4 | Register counters on the RP (`show ip pim ... register` / debug) | **thousands of Registers per second** |
| 5 | Look up the new service's source | a high-rate source (40 Mbps) is sending, and **the (S,G) Join from the RP to that source never forms** |
| 6 | RP `show ip rpf <new source>` | **RPF failure** (the source prefix matched the default route on the RP, pointing the wrong way) |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | RP `show processes cpu sorted` | **PIM 进程占用 80%+** |
| 2 | RP `show ip pim rp mapping` | 正常 |
| 3 | RP `show ip mroute count` | 条目数正常 |
| 4 | RP 上的 Register 计数（`show ip pim ... register` / debug） | **每秒数千个 Register** |
| 5 | 查新业务的源 | 一个高码率源（40 Mbps）在发，**RP 到该源的 (S,G) Join 一直建不起来** |
| 6 | RP `show ip rpf <新源>` | **RPF 失败**（源前缀在 RP 上匹配到了默认路由，指向错误方向） |

</div>

**Root-cause chain (a textbook Register storm)**:

<div class="zh" markdown="1">

**根因链（教科书级的 Register 风暴）**：

</div>

```
FHR receives source traffic -> encapsulates it into Register unicasts towards the RP
       ↓
RP receives the Register -> decapsulates -> tries to send an (S,G) Join towards the source
       ↓
RPF on the RP points at the wrong interface -> the Join cannot be sent / the tree cannot be built
       ↓
the RP cannot build (S,G) -> it cannot send Register-Stop
       ↓
the FHR resends Registers every few seconds (and every packet is encapsulated!)
       ↓
40 Mbps x encapsulation overhead = the RP's CPU and bandwidth are saturated
-> processing of every other group is slowed -> campus-wide multicast "on-and-off"
```

<div class="zh" markdown="1">

```
FHR 收到源流量 → 封装成 Register 单播发给 RP
       ↓
RP 收到 Register → 解封装 → 尝试向源发 (S,G) Join
       ↓
RP 上 RPF 指向错误接口 → Join 发不出去 / 建立失败
       ↓
RP 无法建立 (S,G) → 无法发 Register-Stop
       ↓
FHR 每隔几秒重发 Register（并且每个包都被封装！）
       ↓
40 Mbps × 封装开销 = RP 的 CPU 与带宽被打满
→ 其他组的处理被拖慢 → 全网组播"时断时续"
```

</div>

**Fix**:

<div class="zh" markdown="1">

**修复**：

</div>

```cfg
! ① Fix the RPF (the root cause)
RP# show ip rpf 10.1.1.1                 ! confirm where the wrong answer comes from
RP(config)# ip mroute 10.1.1.1 255.255.255.255 10.0.0.2   ! or fix the IGP / static mroute

! ② Limit the Register rate (damage control, not a fix)
ip pim register-rate-limit 100            ! at most 100 Registers per second per (S,G)

! ③ Rate-limit at the source (stop one source from saturating)
interface Gi0/1                          ! interface facing the source
 ip multicast rate-limit ...             ! or an MQC policer
```

<div class="zh" markdown="1">

```cfg
! ① 修复 RPF（根本）
RP# show ip rpf 10.1.1.1                 ! 确认错误来源
RP(config)# ip mroute 10.1.1.1 255.255.255.255 10.0.0.2   ! 或修正 IGP/静态 mroute

! ② 限制 Register 速率（限损，不是修复）
ip pim register-rate-limit 100            ! 每个 (S,G) 每秒最多 100 个 Register

! ③ 源侧限速（防止单个源打满）
interface Gi0/1                          ! 面向源的接口
 ip multicast rate-limit ...             ! 或 MQC policer
```

</div>

**The four causes of a Register storm (troubleshooting checklist)**:

<div class="zh" markdown="1">

**Register 风暴的四个成因（排查清单）**：

</div>

| Cause | Symptom | Check |
|------|------|------|
| **RPF failure from the RP to the source** | Registers continue, no matching (S,G) on the RP | `show ip rpf <source>` |
| **the group exists on the RP but is denied by an ACL** | Registers continue, possibly PIM rejects in the log | the RP's `ip multicast boundary` / ACL |
| **the source rate is so high the RP cannot keep up** | the Register rate is on the same order as the source rate | rate-limit at the source |
| **MTU/fragmentation between FHR and RP** | large Register packets are dropped and retransmitted a lot | `ip mtu` / `ping df-bit` |

<div class="zh" markdown="1">

| 成因 | 特征 | 检查 |
|------|------|------|
| **RP 到源的 RPF 失败** | Register 持续，RP 上无对应 (S,G) | `show ip rpf <源>` |
| **RP 上有该组但被 ACL 拒绝** | Register 持续，日志可能有 PIM 拒绝 | RP 的 `ip multicast boundary` / ACL |
| **源速率极高、RP 处理不过来** | Register 速率与源速率同阶 | 源侧限速 |
| **FHR 与 RP 之间的 MTU/分片** | Register 大包被丢，重传多 | `ip mtu` / `ping df-bit` |

</div>

> ⚠️ **The most dangerous combination**: **a high-rate source plus an RPF failure**. Because Registers encapsulate "per packet", a 40 Mbps source with a failed RPF keeps encapsulating 40 Mbps of data into unicast towards the RP — **the RP's ingress bandwidth is consumed**, and then all multicast suffers. **This is the scale effect of "one source crippling the whole network"**, and it is exactly why "rate-limiting at the source" has to be part of the design.

<div class="zh" markdown="1">

> ⚠️ **最危险的组合**：**高码率源 + RPF 失败**。因为 Register 是"按包封装"，40 Mbps 的源在 RPF 失败时会持续把 40 Mbps 的数据封装成单播打给 RP —— **RP 的入方向带宽被吃满**，然后所有组播都受影响。**这是"一个源拖垮全网"的规模效应**，也是为什么"源侧限速"必须作为设计的一部分。

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **The root cause of a Register storm is almost always RPF**; `register-rate-limit` is only a tourniquet.
2. **The RP is the "control-plane single point" of the whole PIM-SM domain** — when its CPU is slowed, the impact is not limited to new groups but hits processing for every group.
3. **Bringing a high-rate source online requires an "RP-perspective RPF pre-check"**: confirm the route at the source, confirm `show ip rpf` on the RP, then turn the service up.

<div class="zh" markdown="1">

1. **Register 风暴的根因几乎总是 RPF**，`register-rate-limit` 只是止血带。
2. **RP 是整个 PIM-SM 域的"控制面单点"** —— 它的 CPU 被拖慢，影响的不只是新组播，而是所有组的处理。
3. **高码率源上线必须做"RP 视角的 RPF 预检"**：源侧确认路由、RP 上确认 `show ip rpf`，再开通业务。

</div>

### 🔥 Case 14: After an "All-Hands Webcast", a Whole Floor's Wi-Fi Was Down for Two Hours · 🔥 案例十四：开完一场"全网直播"，整个楼层的 Wi-Fi 瘫了两小时

**Scenario**: an all-hands meeting at headquarters (mostly wireless) was streamed internally over multicast (239.10.5.1, 4 Mbps). Five minutes into the meeting, **wireless users on the whole floor could not use the network** (even ping timed out) and AP CPU and channel utilisation were saturated.

<div class="zh" markdown="1">

**场景**：总部全员大会（无线为主），用内部组播推流（239.10.5.1，4 Mbps）。会议开始 5 分钟后，**全楼层无线用户无法上网**（连 ping 都超时），AP 的 CPU 与信道利用率打满。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | WLC multicast configuration | **multicast-to-unicast (Multicast Direct) not enabled** |
| 2 | AP channel utilisation | 95%+ |
| 3 | Over-the-air analysis | a large number of **multicast frames sent at the lowest basic rate (1 Mbps/6 Mbps)** |
| 4 | Client count | **180 clients** on that floor |
| 5 | Airtime calculation | a 4 Mbps stream at the lowest rate consumes **about 60–70% of the airtime** |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | WLC 的组播配置 | **未启用组播转单播（Multicast Direct）** |
| 2 | AP 的信道利用率 | 95%+ |
| 3 | 空口分析 | 大量**以最低基础速率（1 Mbps/6 Mbps）发送的组播帧** |
| 4 | 客户端数量 | 该楼层 **180 个客户端** |
| 5 | airtime 计算 | 4 Mbps 流 × 最低速率开销 → **吃掉约 60–70% 的 airtime** |

</div>

**Root cause (airtime maths)**:

<div class="zh" markdown="1">

**根因（airtime 数学）**：

</div>

```
How multicast behaves on Wi-Fi:
 ① it is sent at the 【lowest basic rate】 (so that every client can demodulate it), e.g. 6 Mbps
 ② no ACK, no retransmission, no rate adaptation
 ③ one multicast frame is received (and must be decoded) by 【every associated client】
 ④ the airtime a multicast frame occupies = frame length / lowest rate + overhead

Calculation (4 Mbps stream, 1500-byte packets):
 packets per second ≈ 4 Mbps / 12,000 bit ≈ 333 pps
 airtime per packet (6 Mbps) ≈ 12,000/6,000,000 ≈ 2 ms + overhead ≈ 2.5 ms
 total airtime ≈ 333 x 2.5 ms = 833 ms per second ≈ 【83% of the airtime】

-> only 17% is left for unicast; the normal traffic of 180 clients all queues
-> the symptom is "Wi-Fi is down"
```

<div class="zh" markdown="1">

```
组播在 Wi-Fi 上的特性：
 ① 以【最低基础速率】发送（为保证所有客户端都能解调），如 6 Mbps
 ② 无 ACK、无重传、无速率自适应
 ③ 一个组播帧被【所有关联客户端】接收（都要解码）
 ④ 组播帧占用 airtime = 帧长 / 最低速率 + 开销

计算（4 Mbps 流，1500 字节包）：
 每秒包数 ≈ 4 Mbps / 12,000 bit ≈ 333 包/秒
 每包 airtime（6 Mbps）≈ 12,000/6,000,000 ≈ 2 ms + 开销 ≈ 2.5 ms
 总 airtime ≈ 333 × 2.5 ms = 833 ms/秒 ≈ 【83% 的 airtime】

→ 只剩 17% 给单播，180 个客户端的正常业务全部排队
→ 表现为"Wi-Fi 瘫了"
```

</div>

**Fix (the complete set is mandatory)**:

<div class="zh" markdown="1">

**修复（必须做完整的一套）**：

</div>

```cfg
! WLC side (Cisco AireOS syntax example)
config multicast mode multicast-to-unicast            ! multicast-to-unicast (the core measure)
config multicast vlan 200 mode multicast-to-unicast
config multicast address 239.10.5.1 mode multicast-to-unicast
! or use IGMP snooping plus multicast optimisation (commands differ by platform)

! Tune the basic rates (drop 1/2/5.5/11 Mbps to reduce multicast overhead)
config 802.11a rate disabled 6
config 802.11a rate disabled 9
config 802.11a rate disabled 12
```

<div class="zh" markdown="1">

```cfg
! WLC 侧（Cisco AireOS 语法示例）
config multicast mode multicast-to-unicast            ! 组播转单播（核心）
config multicast vlan 200 mode multicast-to-unicast
config multicast address 239.10.5.1 mode multicast-to-unicast
! 或者用 IGMP snooping + 组播优化（不同平台命令不同）

! 优化基础速率（去掉 1/2/5.5/11 Mbps 低速率，减少组播开销）
config 802.11a rate disabled 6
config 802.11a rate disabled 9
config 802.11a rate disabled 12
```

</div>

| Measure | Effect | Caveat |
|------|------|------|
| **Multicast-to-unicast (Multicast Direct)** | one unicast per client (can use a high rate and ACKs) | with many clients the unicast cost is also high; limit concurrency |
| **Raise the basic rates** | raises the transmission rate of multicast frames | legacy clients may drop off (coverage edge) |
| **Restrict wireless multicast (only essential groups)** | removes irrelevant multicast (mDNS, SSDP broadcasts) | affects discovery applications |
| **Rate-limit multicast on the wired side** | stops excessive multicast entering the wireless | requires coordination with the business |
| **Steer high-bandwidth clients onto wired** | most effective | meeting rooms need wired ports / dedicated APs |

<div class="zh" markdown="1">

| 措施 | 效果 | 注意 |
|------|------|------|
| **组播转单播（Multicast Direct）** | 按客户端单独发单播（可用高速率 + ACK） | 客户端多时单播开销也大，需限并发 |
| **提高基础速率** | 提升组播帧的发送速率 | 老客户端可能掉线（覆盖边缘） |
| **限制无线组播（只允许必要组）** | 减少无关组播（如 mDNS、SSDP 广播） | 影响发现类应用 |
| **有线侧限速组播** | 防止过量组播进无线 | 需与业务方协调 |
| **引导高带宽客户端用有线** | 最有效 | 会议室应有有线口/专用 AP |

</div>

**A more fundamental design judgement**:

<div class="zh" markdown="1">

**一个更本质的设计判断**：

</div>

> **Wi-Fi is not suitable for "high-volume, long-duration, many-client" multicast.** This is not a "configuration problem" but a **medium characteristic** (shared medium + lowest rate + no ACK). For every "watch the webcast over wireless" requirement, the correct answer is: **distribute the multicast on the wired side to the APs nearest the users → convert to unicast at the AP → or simply use unicast (application-layer distribution/CDN)**.

<div class="zh" markdown="1">

> **Wi-Fi 不适合承载"大流量、长时间、多客户端"的组播。** 这不是"配置问题"，是**介质特性问题**（共享介质 + 最低速率 + 无 ACK）。所有"无线看直播"的需求，正确方案是：**组播在有线侧分发到 AP 附近 → AP 上转单播 → 或者干脆用单播（应用层分发/CDN）**。

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **The cost of multicast on wireless is "airtime", not "bandwidth"** — a 4 Mbps stream can consume 83% of the air.
2. **One multicast stream can take down an entire AP**, dragging unicast traffic down with it (shared medium).
3. **Multicast-to-unicast is mandatory**, but you must also estimate "client count × bitrate" (180 unicast streams are not cheap either).

<div class="zh" markdown="1">

1. **组播在无线上的成本是"airtime"，不是"带宽"** —— 4 Mbps 的流可以吃掉 83% 的空口。
2. **一个组播流可以打瘫整个 AP**，连单播业务一起拖死（因为共享介质）。
3. **组播转单播是必配**，但也要评估"客户端数量 × 码率"的总量（180 个客户端的单播也不便宜）。

</div>

### 🔥 Case 15: The Source Was Made "Dual-Active", and After Failover the Picture Ghosted (the Two Sources' Streams Mixed) · 🔥 案例十五：源做了"双活"，切换后画面是"鬼影"（两个源的流混在一起）

**Scenario**: the video service was made source-dual-active (two encoders pushing to the same group 239.10.5.1 from different source addresses: 10.1.1.1 and 10.1.1.2). After the primary failed over to the backup, **the receivers showed a "double image"**, and it only recovered 30 minutes later.

<div class="zh" markdown="1">

**场景**：视频业务做了源双活（两个编码器推同一个组 239.10.5.1，源地址不同：10.1.1.1 与 10.1.1.2）。主源故障切到备源后，**接收端出现"画面叠影"**，持续 30 分钟后才恢复。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | The receiver | receiving packets from both sources at once (interleaved sequence numbers) |
| 2 | LHR `show ip mroute 239.10.5.1` | **both (10.1.1.1, G) and (10.1.1.2, G) entries exist** |
| 3 | Did the primary really stop | the primary device **is still sending** after the "failure" (only the encoder's service process died; the network stack was still pushing residual buffers / or both units were pushing) |
| 4 | Why the old (S,G) does not disappear | the primary is still sending → the entry never ages → both sources' traffic lives in the tree at the same time |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | 接收端 | 同时收到两个源的包（序列号交错） |
| 2 | LHR `show ip mroute 239.10.5.1` | **同时存在 (10.1.1.1, G) 与 (10.1.1.2, G) 两个表项** |
| 3 | 主源是否真停了 | 主源设备"故障"后**仍在发包**（编码器只是业务进程挂了，网络仍在推残留缓存/或双机都在推） |
| 4 | 老的 (S,G) 为何不消失 | 主源仍在发 → 表项不会老化 → 两个源的流量同时在树里 |

</div>

**Root cause**:

<div class="zh" markdown="1">

**根因**：

</div>

```
The "application-layer semantics" of source dual-active do not match the "network-layer semantics":

Network layer: two sources = two independent (S,G) trees
       -> as long as a source is sending, both trees exist
       -> the LHR forwards the traffic of both trees to the receivers

Application layer: expects "only one path is live"
       -> but the receiver gets two different encoded streams (frame numbers are discontinuous)
       -> the decoder cannot merge them -> double image / artefacts

This is not a network failure; it is "dual-active sources without mutual exclusion".
```

<div class="zh" markdown="1">

```
源双活的"应用层语义"与"网络层语义"不一致：

网络层：两个源 = 两条独立的 (S,G) 树
       → 只要源在发，两条树都存在
       → LHR 会把两条树的流量都转给接收者

应用层：期望"只有一路是活的"
       → 但接收端拿到两路不同的编码数据（帧序号不连续）
       → 解码器无法合并 → 叠影 / 花屏

这不是网络故障，而是"双活源没有做互斥"。
```

</div>

**Three correct approaches**:

<div class="zh" markdown="1">

**三种正确的做法**：

</div>

| Option | Mechanism | Applicable to |
|------|------|------|
| **① Source-side mutual exclusion (recommended)** | the backup only starts streaming after the primary is confirmed dead (heartbeat/arbitration) | the vast majority of cases |
| **② Different group addresses (Live-Live semantics)** | the two sources send to two groups (239.10.5.1 / 239.10.5.2) and the **receivers de-duplicate with ST 2022-7** | when "hitless switching" is required |
| **③ Source filtering on the network** | allow only one source's (S,G) on the LHR (ACL / static mroute / SSM joining only the primary) | a transition measure; switching is manual |

<div class="zh" markdown="1">

| 方案 | 机制 | 适用 |
|------|------|------|
| **① 源侧互斥（推荐）** | 备源只在主源确认失效后才开始推流（心跳/仲裁） | 绝大多数场景 |
| **② 不同组地址（Live-Live 语义）** | 两源发到两个组（239.10.5.1 / 239.10.5.2），**接收端做 ST 2022-7 去重** | 需要"无感切换" |
| **③ 网络侧源过滤** | LHR 上只允许一个源的 (S,G)（ACL / 静态 mroute / SSM 只加入主源） | 过渡方案，切换需人工 |

</div>

```cfg
! Option ③: accept only the primary on the LHR (change manually when switching over)
interface Gi0/1
 ip multicast boundary 40
ip access-list standard 40
 permit 10.1.1.1                ! allow only the primary
```

<div class="zh" markdown="1">

```cfg
! 方案③：LHR 上只接受主源（切换时人工改）
interface Gi0/1
 ip multicast boundary 40
ip access-list standard 40
 permit 10.1.1.1                ! 只允许主源
```

</div>

> ⚠️ **"Two sources sending to the same group" is a design red line**: it makes the network build two parallel trees, every "per-group" policy (QoS, rate limiting, monitoring) double-counts, and receivers get mixed data. **Either "source mutual exclusion" or "two groups plus application-layer merging"; never "one group, two sources".**

<div class="zh" markdown="1">

> ⚠️ **"两个源发同一个组"是设计上的红线**：它会让网络层产生两条并行的树，任何"按组"的策略（QoS、限速、监控）都会重复计算，而接收端会拿到混杂的数据。**要么"源互斥"，要么"两个组 + 应用层合并"，不要"同一组两个源"。**

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **Source redundancy is an application-layer problem, not a network-layer problem**. The network can only "forward what it sees"; it cannot decide "which source is the right one".
2. **"It only recovered 30 minutes after the failure" usually means "leftover state"** — multicast state ageing ((S,G) depends on whether the source is active by default) is longer than people think; the design must evaluate the window where "the source stopped but the state remains".
3. **A dual-active design must state: who is primary? What is the switch-over criterion? How does the receiver tell the two apart?** If any one of the three is unanswered, you get "ghosting".

<div class="zh" markdown="1">

1. **源冗余是应用层问题，不是网络层问题**。网络只能"转发它看到的"，无法判断"哪个源才是对的"。
2. **"故障后 30 分钟才恢复"通常意味着"残留状态"** —— 组播的状态老化时间（(S,G) 默认依赖源是否活跃）比想象中长，设计要评估"源停了但状态还在"的窗口。
3. **双活设计必须明确：谁是主？切换的判据是什么？接收端如何区分两路？** 三个问题任何一个没答清，都会变成"鬼影"。

</div>

### 🔥 Case 16: Security Found "Our Market-Data Stream in the Partner's Network" · 🔥 案例十六：安全团队发现"我们的行情流出现在合作伙伴的网络里"

**Scenario**: the enterprise partners with a brokerage; the two networks are interconnected by a leased line and run PIM (subscribing to each other's multicast). A security audit found that **the enterprise's internal market-data multicast (239.30.1.x) was observed inside the partner's network**, and the partner's operations team could see the enterprise's group names and content.

<div class="zh" markdown="1">

**场景**：企业与一家券商合作，双方网络通过专线互联并跑 PIM（互相订阅组播）。安全审计发现：**企业内部的行情组播（239.30.1.x）在合作伙伴的网络中被观测到**，且合作伙伴的运维能看到企业的组播组名与内容。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | Border interface configuration | only PIM; **no `ip multicast boundary`** |
| 2 | MSDP peer | MSDP is established in both directions, **SA filtering is absent both ways** |
| 3 | Auto-RP/BSR | both sides received the other's RP announcements (**no scope/border configured**) |
| 4 | Why it could be "seen" | the partner's receivers joined 239.30.1.x (they could join, because there is no boundary) |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | 边界接口配置 | 只配了 PIM，**没有 `ip multicast boundary`** |
| 2 | MSDP peer | 双方建立了 MSDP，**SA 双向无过滤** |
| 3 | Auto-RP/BSR | 双方都收到了对方的 RP 通告（**未配 scope/border**） |
| 4 | 为什么会被"看到" | 对方的接收者加入了 239.30.1.x（能加入，因为没有边界） |

</div>

**Root cause (three layers missing at once)**:

<div class="zh" markdown="1">

**根因（三个层面同时缺失）**：

</div>

```
① No group-address boundary
   -> any group can cross the leased line (including internal management multicast)

② No MSDP filtering
   -> the partner's SAs make your RP join the partner's sources
   -> your SAs tell the partner which sources you have (information leak)

③ RP announcements crossing the border
   -> the partner learned your RP mapping (usable as an attack surface)
   -> your devices learned the peer's RP (traffic may be steered towards the peer)
```

<div class="zh" markdown="1">

```
① 组地址边界缺失
   → 任何组都可以跨专线（包括企业内部管理类组播）

② MSDP 无过滤
   → 对方的 SA 让你的 RP 去加入对方的源
   → 你的 SA 让对方知道你有哪些源（信息泄露）

③ RP 通告越界
   → 对方学到了你的 RP 映射（可用作攻击面）
   → 你的设备学了对端的 RP（可能把流量导向对端）
```

</div>

**Fix (four layers of defence, all of them)**:

<div class="zh" markdown="1">

**修复（四层防护，缺一不可）**：

</div>

```cfg
! ① Group-address boundary (both directions, per interface)
interface Gi0/0                       ! towards the partner
 ip multicast boundary 50
ip access-list standard 50
 permit 239.40.0.0 0.0.255.255        ! only the "partner-dedicated range" may pass
 deny   any                            ! everything else is denied

! ② MSDP filtering (both directions)
ip msdp sa-filter in 203.0.113.1 list 60
ip msdp sa-filter out 203.0.113.1 list 70
ip msdp sa-limit 203.0.113.1 500
access-list 60 permit 239.40.0.0 0.0.255.255   ! accept SAs for the partner range only
access-list 70 permit 239.40.0.0 0.0.255.255   ! advertise the partner range only

! ③ RP announcement boundary
interface Gi0/0
 ip pim bsr-border                     ! block BSR
 no ip pim autorp ...                  ! or block 224.0.1.39/40 with a multicast boundary

! ④ PIM neighbour authentication + interface ACL
interface Gi0/0
 ip pim authentication mode md5 key-chain PARTNER
 ip access-group PARTNER-IN in         ! permit only PIM (103) and multicast data
```

<div class="zh" markdown="1">

```cfg
! ① 组地址边界（双向，按接口）
interface Gi0/0                       ! 朝合作伙伴
 ip multicast boundary 50
ip access-list standard 50
 permit 239.40.0.0 0.0.255.255        ! 只允许"合作专用段"通过
 deny   any                            ! 其余全部拒绝

! ② MSDP 过滤（双向）
ip msdp sa-filter in 203.0.113.1 list 60
ip msdp sa-filter out 203.0.113.1 list 70
ip msdp sa-limit 203.0.113.1 500
access-list 60 permit 239.40.0.0 0.0.255.255   ! 只接受合作段的 SA
access-list 70 permit 239.40.0.0 0.0.255.255   ! 只通告合作段

! ③ RP 通告边界
interface Gi0/0
 ip pim bsr-border                     ! 阻断 BSR
 no ip pim autorp ...                  ! 或用 multicast boundary 阻断 224.0.1.39/40

! ④ PIM 邻居认证 + 接口 ACL
interface Gi0/0
 ip pim authentication mode md5 key-chain PARTNER
 ip access-group PARTNER-IN in         ! 只允许 PIM(103) 与组播数据
```

</div>

**The "minimal exposure" design principles for partner scenarios**:

<div class="zh" markdown="1">

**合作场景的"最小暴露"设计原则**：

</div>

| Principle | Practice |
|------|------|
| **A dedicated group address range** | allocate a separate range for inter-company multicast (e.g. 239.40.0.0/16); never mix it with internal groups |
| **A dedicated RP, or no RP at all** | prefer **SSM** (fixed source, no RP interaction, no MSDP) |
| **One direction first** | if the business only needs "one side sends, one side receives", use a **static mroute + static Join** and do not run PIM |
| **Audit** | record "who joined which group, and when" (IGMP snapshots + logs) |
| **Rate limiting** | multicast on the leased line must be rate-limited (to stop the peer flooding your bandwidth) |

<div class="zh" markdown="1">

| 原则 | 做法 |
|------|------|
| **专用组地址段** | 为跨企业组播单独分一段（如 239.40.0.0/16），不与内部混用 |
| **专用 RP 或不用 RP** | 优先 **SSM**（源固定、无 RP 交互、无 MSDP） |
| **单向优先** | 如果业务只需要"一方发一方收"，用 **静态 mroute + 静态 Join**，不跑 PIM |
| **审计** | 记录"谁在什么时候加入了哪个组"（IGMP 快照 + 日志） |
| **限速** | 专线上的组播必须限速（防对端注水打满带宽） |

</div>

> 💡 **The safest inter-company multicast design is "do not use multicast protocols"**: if the requirement is merely "the partner needs to see our market data", then **SSM + precise ACLs + source-side rate limiting**, or even "a dedicated point-to-point unicast distribution", may be simpler and more controllable. **The complexity and risk of cross-domain multicast frequently outweigh the bandwidth it saves.**

<div class="zh" markdown="1">

> 💡 **最安全的跨企业组播方案是"不用组播协议"**：如果只是"合作伙伴需要看我们的行情"，用 **SSM + 精确 ACL + 源侧限速**，甚至用"专用点对点单播分发"都可能更简单可控。**跨域组播的复杂度与风险，往往超过它带来的带宽节省。**

</div>

**Lesson**: **the multicast "administrative range" (239/8) is only private on paper; the protocol layer does nothing to prevent crossing domains**. Inter-company multicast must be isolated with four layers at once — "address boundary + SA filtering + RP scope + authentication" — **and missing any one layer means there is no isolation at all**.

<div class="zh" markdown="1">

**教训**：**组播的"管理范围"（239/8）是纸面上的私有，协议层完全不阻止跨域**。跨企业组播必须靠"地址边界 + SA 过滤 + RP scope + 认证"四层同时实现隔离，**少任何一层就等于没有隔离**。

</div>

### 🔥 Case 17: Bandwidth Was Only 60% Utilised, yet Market-Data Multicast Dropped Packets at Exactly 9:30 Every Day · 🔥 案例十七：带宽只用了 60%，但行情组播每天 9:30 准时丢包

**Scenario**: at the market open (9:30) market-data multicast dropped packets (at a fixed time every day, lasting 5–20 seconds), while average link utilisation was only 60%. Packet captures showed **the loss happened on the core-to-distribution links**.

<div class="zh" markdown="1">

**场景**：交易时段开盘（9:30）瞬间，行情组播出现丢包（每天固定时间，持续 5–20 秒），但链路平均利用率只有 60%。抓包显示**丢包发生在核心到汇聚的链路上**。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | Interface utilisation (5-minute average) | 60% |
| 2 | Interface utilisation (1-second granularity) | **100% at the open** (micro-burst) |
| 3 | Interface `output drops` | growing continuously |
| 4 | QoS configuration | **no QoS on that link** (a single default FIFO queue) |
| 5 | Unicast traffic in the same window | a burst of TCP traffic at the open (order entry, queries) |
| 6 | Queue analysis | the unicast TCP burst fills the buffer → **multicast packets are tail-dropped** |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | 接口利用率（5 分钟平均） | 60% |
| 2 | 接口利用率（1 秒粒度） | **开盘瞬间 100%**（微突发） |
| 3 | 接口 `output drops` | 持续增长 |
| 4 | QoS 配置 | 该链路**未配置 QoS**（默认单一 FIFO 队列） |
| 5 | 同时段的单播流量 | 开盘时有大量 TCP 业务（下单、查询）突发 |
| 6 | 队列分析 | 单播 TCP 突发填满缓冲区 → **组播包被尾丢弃** |

</div>

**Root cause (two factors stacked)**:

<div class="zh" markdown="1">

**根因（两个因素叠加）**：

</div>

```
① Micro-burst
   market data is pushed in a burst at the open: 500k small packets per second
   average bandwidth 60%, but instantaneous (millisecond-scale) above 100%
   -> relies on port buffers to absorb -> without enough buffer, it drops

② Multicast and unicast share a queue
   without QoS everything is one FIFO
   TCP congestion control keeps the buffer full ("filling the pipe")
   multicast (UDP) has no back-pressure, so it can only be tail-dropped
   -> the result: TCP survives and multicast is dropped (and multicast is exactly what cannot be dropped)
```

<div class="zh" markdown="1">

```
① 微突发（Microburst）
   行情数据在开盘瞬间集中推送：500k 包/秒的小包
   平均带宽 60%，但瞬时（毫秒级）超过 100%
   → 依赖端口缓存吸收 → 缓存不足则丢包

② 组播与单播共享队列
   无 QoS 时，所有流量一个 FIFO
   TCP 的拥塞控制会持续填满缓冲区（"填满管道"）
   组播（UDP）没有反压，只能被尾丢弃
   → 结果：TCP 活下来，组播丢掉（而组播恰恰是最不能丢的）
```

</div>

**Fix (three layers)**:

<div class="zh" markdown="1">

**修复（三层）**：

</div>

```cfg
! ① A dedicated multicast queue with guaranteed bandwidth
class-map match-any MQ-FEED
 match access-group name MQ-FEED-ACL
policy-map CORE-OUT
 class MQ-FEED
  bandwidth percent 30
  queue-limit 2000 packets            ! a deeper queue absorbs the micro-burst
 class class-default
  fair-queue
interface Gi0/1
 service-policy output CORE-OUT

ip access-list extended MQ-FEED-ACL
 permit udp any 239.30.0.0 0.0.255.255

! ② Port buffer / queue tuning (platform-dependent)
! ③ Upstream shaping (to "flatten" the micro-burst)
policy-map SHAPE-10G
 class class-default
  shape average 9500000000            ! slightly below line rate to reduce downstream micro-bursts
```

<div class="zh" markdown="1">

```cfg
! ① 组播独立队列 + 保证带宽
class-map match-any MQ-FEED
 match access-group name MQ-FEED-ACL
policy-map CORE-OUT
 class MQ-FEED
  bandwidth percent 30
  queue-limit 2000 packets            ! 更深的队列吸收微突发
 class class-default
  fair-queue
interface Gi0/1
 service-policy output CORE-OUT

ip access-list extended MQ-FEED-ACL
 permit udp any 239.30.0.0 0.0.255.255

! ② 端口缓存 / 队列调优（按平台）
! ③ 上游整形（把微突发"拉平"）
policy-map SHAPE-10G
 class class-default
  shape average 9500000000            ! 略低于线速，减少下游微突发
```

</div>

| Measure | Effect | Caveat |
|------|------|------|
| **Dedicated queue + guaranteed bandwidth** | multicast is not squeezed out by unicast | must be consistent end to end |
| **Larger queue-limit** | absorbs micro-bursts | too deep → more latency (bad for market data!) |
| **Upstream shaping** | flattens the burst | shaping introduces latency |
| **More link bandwidth** | the most direct | cost; micro-bursts may still occur |
| **Application-layer pacing/smoothing** | reduces bursts at the origin | requires application changes |
| **FEC / redundant paths** | tolerates a small amount of loss | extra overhead |

<div class="zh" markdown="1">

| 措施 | 作用 | 注意 |
|------|------|------|
| **独立队列 + 保证带宽** | 组播不被单播挤掉 | 需要端到端一致 |
| **加大 queue-limit** | 吸收微突发 | 队列太深 → 时延增加（对行情敏感！） |
| **上游整形** | 把突发拉平 | 整形会引入时延 |
| **增大链路带宽** | 最直接 | 成本；且微突发可能仍然存在 |
| **应用层限速/平滑** | 从源头减少突发 | 需应用改造 |
| **FEC / 冗余路径** | 容忍少量丢包 | 增加开销 |

</div>

> ⚠️ **"Average utilisation 60% but still dropping" is the signature of a micro-burst**. Monitoring based on 5-minute averages will never find it; you must look at **1-second or even millisecond** interface statistics (`load-interval 30`, NetFlow micro-burst detection, port buffer drop counters).

<div class="zh" markdown="1">

> ⚠️ **"平均利用率 60% 但有丢包"是微突发的典型特征**。用 5 分钟平均看监控永远发现不了，必须看 **1 秒甚至毫秒级**的接口统计（`load-interval 30`、NetFlow 微突发、端口缓存丢弃计数）。

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **Multicast loss is often not "insufficient bandwidth" but "the queue is filled by unicast"** — multicast (UDP) has no say during congestion.
2. **Micro-bursts are a monitoring blind spot**: capacity planning must not use "average bandwidth" but "peak packet rate × packet size".
3. **Multicast must have its own queue, isolated from unicast.** This is the first rule of "end-to-end QoS", and the one most often skipped.

<div class="zh" markdown="1">

1. **组播的丢包往往不是"带宽不足"，而是"队列被单播占满"** —— 组播（UDP）在拥塞中没有"话语权"。
2. **微突发是监控的盲区**：设计容量时不能用"平均带宽"，要用"峰值包速率 × 包大小"。
3. **组播必须有自己的队列**，与单播隔离。这是"端到端 QoS"的第一条，也是最常被跳过的一条。

</div>

### 🔥 Case 18: After the Merger Two Domains Were Joined, "Half the People Can Watch, Half Cannot" · 🔥 案例十八：并购后两个域合并，"一半人能看、一半人不能看"

**Scenario**: after an acquisition, two existing multicast domains (each with its own RP, one using 239.10/16 and the other 239.20/16) were interconnected. Problems appeared during the merge: **users in domain A could watch domain B's channels, but domain B's users could not watch domain A's**; within each domain everything was normal.

<div class="zh" markdown="1">

**场景**：企业并购后，两个原有组播域（各有一套 RP、各用 239.10/16 与 239.20/16）互联。合并过程中出问题：**A 域的用户能看 B 域的频道，但 B 域的用户看不了 A 域的**；A 域内部正常，B 域内部也正常。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

| Step | Check | Result |
|------|------|------|
| 1 | Compare RP mappings network-wide | **domain A's devices have two RP mappings, domain B's devices only one** |
| 2 | Why | domain A uses Auto-RP (learned automatically); domain B uses a **static RP** (configured by hand) |
| 3 | Domain B device `show ip pim rp mapping` | only 239.20.0.0/16 → domain A's 239.10.0.0/16 **has no RP** |
| 4 | Domain A devices | received domain B's Auto-RP announcements (domain B has a C-RP participating in Auto-RP) → domain A has both mappings |
| 5 | Why A can watch B | domain A's devices have B's RP mapping → they can build the tree |
| 6 | Why B cannot watch A | domain B's devices have no mapping for A's groups → (*,G) cannot be built |

<div class="zh" markdown="1">

| 步骤 | 检查 | 结果 |
|------|------|------|
| 1 | 全网 RP 映射比对 | **A 域设备有两条 RP 映射，B 域设备只有一条** |
| 2 | 原因 | A 域用 Auto-RP（自动学），B 域用**静态 RP**（手工配） |
| 3 | B 域设备 `show ip pim rp mapping` | 只有 239.20.0.0/16 → A 域的 239.10.0.0/16 **没有 RP** |
| 4 | A 域设备 | 收到 B 域的 Auto-RP 宣告（B 域有 C-RP 参与了 Auto-RP）→ A 域有了两条映射 |
| 5 | 为什么 A 能看 B | A 域设备有 B 域的 RP 映射 → 能建树 |
| 6 | 为什么 B 看不了 A | B 域设备没有 A 域的 RP 映射 → (*,G) 无法建立 |

</div>

**Root cause**: **inconsistent RP discovery, not unified during the merger**.

<div class="zh" markdown="1">

**根因**：**RP 发现方式不一致 + 合并时没有统一**。

</div>

```
Domain A: Auto-RP (dynamic, learns every announcement)
Domain B: static RP (only the one entry configured by hand)

After the merge:
  domain A devices: Auto-RP learns domain B's groups -> complete
  domain B devices: the static entry covers only its own groups -> missing domain A's groups

-> one-way visibility ("only half the people can watch")
```

<div class="zh" markdown="1">

```
A 域：Auto-RP（动态，能学所有宣告）
B 域：静态 RP（只有手配的那一条）

合并后：
  A 域设备：Auto-RP 学到 B 域的组 → 完整
  B 域设备：静态只覆盖自己的组 → 缺 A 域的组

→ 单向可见（"一半人能看"）
```

</div>

**Fix (must be "unify", not "fill the gap")**:

<div class="zh" markdown="1">

**修复（必须"统一"而不是"补齐"）**：

</div>

| Step | Action | Explanation |
|------|------|------|
| 1 | **Choose one RP discovery method** | multi-vendor → BSR; all-Cisco → Auto-RP; high availability required → Anycast-RP + static RP address |
| 2 | **Unify the address plan** | do the two sides' 239.10/239.20 ranges collide? (very likely) |
| 3 | **Unify the SSM range** | otherwise one side's 232/8 is treated as ASM |
| 4 | **Configure scope/boundaries** | isolate during the merger, then open up service by service |
| 5 | **Compare RP mappings network-wide** | collect `show ip pim rp mapping` from every device with a script and diff them |
| 6 | **Use SSM to reduce dependencies** | move every service that can to SSM (the complexity of RP mappings drops sharply) |

<div class="zh" markdown="1">

| 步骤 | 动作 | 说明 |
|------|------|------|
| 1 | **选定一种 RP 发现方式** | 跨厂商 → BSR；全 Cisco → Auto-RP；要求高可用 → Anycast-RP + 静态 RP 地址 |
| 2 | **统一地址规划** | 两侧的 239.10/239.20 是否冲突？（很可能冲突） |
| 3 | **统一 SSM range** | 否则一侧的 232/8 被当 ASM |
| 4 | **配 scope/边界** | 合并期先隔离，再按业务逐步放通 |
| 5 | **全网比对 RP 映射** | 用脚本从所有设备采集 `show ip pim rp mapping` 做 diff |
| 6 | **用 SSM 减少依赖** | 能改 SSM 的业务全部改掉（合并后 RP 映射的复杂度大幅下降） |

</div>

```cfg
! Example unified design: move the whole network to Anycast-RP + a static RP address (most controllable)
! On all devices (domain A and domain B):
ip pim rp-address 10.0.0.1 10                     ! one anycast address
ip pim ssm default
access-list 10 permit 239.0.0.0 0.255.255.255     ! all ASM groups use the same RP
access-list 10 deny any

! The two RPs (one per domain):
interface Loopback0
 ip address 10.0.0.1 255.255.255.255
interface Loopback1
 ip address <unique per node> 255.255.255.255
ip msdp peer <peer unique address> connect-source Loopback1
ip msdp originator-id Loopback1
```

<div class="zh" markdown="1">

```cfg
! 统一方案示例：全网统一切到 Anycast-RP + 静态 RP 地址（最可控）
! 所有设备（A 域与 B 域）：
ip pim rp-address 10.0.0.1 10                     ! 一个 Anycast 地址
ip pim ssm default
access-list 10 permit 239.0.0.0 0.255.255.255     ! 所有 ASM 组走同一 RP
access-list 10 deny any

! 两台 RP（各域一台）：
interface Loopback0
 ip address 10.0.0.1 255.255.255.255
interface Loopback1
 ip address <各自唯一> 255.255.255.255
ip msdp peer <对端唯一地址> connect-source Loopback1
ip msdp originator-id Loopback1
```

</div>

**Multicast migration checklist for "acquisition/merger" scenarios**:

<div class="zh" markdown="1">

**"并购/合并"场景的组播迁移清单**：

</div>

| Check item | Why |
|-------|--------|
| **Do addresses collide** (both sides use 239.10/16?) | collisions cause "two groups bleeding into each other" (see Case 1) |
| **Is the RP discovery method consistent** | if not → one-way visibility (this case) |
| **Is the SSM range consistent** | if not → some groups find no RP |
| **Is the PIM mode consistent** (BiDir on one side, SM on the other) | if not → the same group behaves differently |
| **Is MSDP needed** | a single-RP design does not need it; multiple RPs do |
| **Layer 2 snooping/querier baseline** | done on one side, not the other → access-layer flooding after the merge |
| **IGMP version** | v2 on one side, v3 on the other → SSM fails on one side (see Case 8) |
| **Boundary ACLs and scope** | after the merge the multicast propagation range is out of control |

<div class="zh" markdown="1">

| 检查项 | 为什么 |
|-------|--------|
| **地址是否冲突**（两侧都用 239.10/16？） | 冲突会导致"两组串流"（见案例一） |
| **RP 发现方式是否一致** | 不一致 → 单向可见（本例） |
| **SSM range 是否一致** | 不一致 → 部分组找不到 RP |
| **PIM 模式是否一致**（一侧 BiDir、一侧 SM） | 不一致 → 同组不同行为 |
| **MSDP 是否需要** | 单 RP 方案不需要；多 RP 需要 |
| **二层 Snooping/Querier 基线** | 一侧做了、一侧没做 → 合并后接入层泛洪 |
| **IGMP 版本** | 一侧 v2、一侧 v3 → SSM 在一侧失效（见案例八） |
| **边界 ACL 与 scope** | 合并后组播扩散范围失控 |

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **Multicast has no "automatic convergence" capability** — merging two independent multicast domains is essentially "redesigning one domain", not "connecting two links".
2. **"One-way visibility" almost always means "inconsistent RP mappings"** — because tree building is symmetric (A reaching B proves the path works), so the difference can only be in the control plane.
3. **A merger project should prioritise "moving to SSM"**: once every "fixed-source" service is on SSM, what needs unifying drops from "RP mapping/discovery/MSDP/scope" to "just the address plan".

<div class="zh" markdown="1">

1. **组播没有"自动融合"能力** —— 两套独立的组播域合并，本质是"重新设计一套"，不是"打通两条链路"。
2. **"单向可见"几乎总是"RP 映射不一致"** —— 因为建树是双向对称的（A 能到 B 说明路径通），差异只能在控制面。
3. **合并项目应该优先"改 SSM"**：把所有"源固定"的业务改成 SSM 后，需要统一的东西从"RP 映射/发现方式/MSDP/scope"降到"只是地址规划"。

</div>

---

## Design Trade-offs · 组播设计的取舍

| Trade-off | Choose A | Choose B | Decision basis |
|---------|------|------|---------|
| **Forwarding mode** | **SSM**: no RP, fewest states, most secure | **PIM-SM**: compatible with legacy terminals, supports any source | if the source is known, always SSM; use SM only for "any source" |
| **Many-to-many scenarios** | **BiDir**: fewest states, suited to many speakers | **PIM-SM**: can optimise paths via SPT | several simultaneous speakers → BiDir; one-way distribution → SSM |
| **RP redundancy** | **Anycast-RP + MSDP**: load sharing + sub-second failover | **Phantom RP**: no MSDP needed | load sharing → Anycast; active/standby only → Phantom |
| **RP discovery** | **Static**: deterministic and simple | **BSR/Auto-RP**: automatic and scalable | small networks static; multi-vendor → BSR |
| **SPT switchover** | **Default (switch to SPT)**: lowest latency | **`spt-threshold infinity`**: fewest states | a few high-rate channels → switch to SPT; thousands of small channels → keep the shared tree |
| **Layer 2 control** | **IGMP Snooping**: precise, saves bandwidth | **Allow flooding**: simple, no state issues | production always uses Snooping + Querier |
| **Cross-domain** | **SSM**: only needs source reachability | **MSDP + MBGP**: supports ASM across domains | new deployments always SSM; interworking with carriers depends on their capabilities |
| **Number of RPs** | **A single pair (Anycast)**: simple to manage | **Multiple pairs per region**: register locally, reduce cross-WAN traffic | large-scale WAN deployments split by region |
| **Multicast over WAN** | **MVPN/tunnels**: carried by the operator | **Local distribution (CDN/cache)**: never crosses the WAN | high-volume distribution prefers "edge cache + local multicast" |
| **Multicast over wireless** | **Multicast-to-unicast**: controllable, higher rates | **Direct multicast**: saves AP processing | production must convert to unicast |
| **Redundancy design** | **Live-Live dual path**: hitless switching | **Single path + fast convergence**: lower cost | only "must not be interrupted" services justify Live-Live |
| **Address allocation** | **A /16 per service**: clear and auditable | **Allocate ad hoc**: convenient | always the former (otherwise 32:1 collisions are certain) |
| **Layer 2 control method** | **IGMP Snooping + Querier**: precise | **MVR**: simplifies across many VLANs | one service across many VLANs → MVR; many services → Snooping |
| **Access-layer protection** | **Group whitelist (IGMP Profile)**: prevents out-of-bounds | **Group-count limit only**: prevents volume | you need both; if you can pick only one, start with the count limit |
| **Data centre transport** | **Underlay multicast / EVPN multicast**: saves bandwidth | **Ingress Replication**: simple | large BUM traffic or many VTEPs → multicast is mandatory |
| **Inter-company multicast** | **SSM + precise ACLs**: no RP interaction | **PIM + MSDP**: flexible | prefer SSM; not using a multicast protocol at all is even better |
| **Source redundancy** | **Source mutual exclusion (active/standby)**: simple, no ghosting | **Live-Live (two groups + 2022-7)**: hitless | use dual paths only when "hitless" is required; otherwise active/standby |
| **Ultra-low-latency services** | **Traditional Layer 3 multicast (no overlay)** | **Carried over VXLAN**: flexible | market data/HPC stays off the overlay |
| **QoS queues** | **A dedicated multicast queue**: isolates unicast bursts | **Shared queue**: simple | production must be dedicated (otherwise multicast dies first under congestion) |
| **Registration cost** | **SSM (no Register)** | **PIM-SM (uses Register)** | fixed source → SSM; otherwise rate-limit Register |

<div class="zh" markdown="1">

| 取舍维度 | 选 A | 选 B | 判断依据 |
|---------|------|------|---------|
| **转发模式** | **SSM**：无 RP、状态最少、最安全 | **PIM-SM**：兼容老终端、支持任意源 | 源已知则一律 SSM；仅"任意源"才用 SM |
| **多对多场景** | **BiDir**：状态最少、适合多方发言 | **PIM-SM**：可 SPT 优化路径 | 多人同时发言选 BiDir；单向分发选 SSM |
| **RP 冗余** | **Anycast-RP + MSDP**：负载分担 + 秒级切换 | **Phantom RP**：无需 MSDP | 要负载分担选 Anycast；只要主备可选 Phantom |
| **RP 发现** | **静态**：确定、简单 | **BSR/Auto-RP**：自动、可扩展 | 小网静态；多厂商选 BSR |
| **SPT 切换** | **默认（切 SPT）**：时延最优 | **`spt-threshold infinity`**：状态最少 | 大流量单频道切 SPT；海量小频道保留共享树 |
| **二层控制** | **IGMP Snooping**：精确、省带宽 | **允许泛洪**：简单、无状态问题 | 生产必用 Snooping + Querier |
| **跨域** | **SSM**：只需源可达 | **MSDP + MBGP**：支持 ASM 跨域 | 新建一律 SSM；与运营商对接看其能力 |
| **RP 数量** | **单一对（Anycast）**：管理简单 | **按区域多对**：就近注册、减少跨 WAN | 跨广域网大规模部署按区域切分 |
| **组播 over WAN** | **MVPN/隧道**：运营商承载 | **本地分发（CDN/缓存）**：不跨 WAN | 大流量分发优先"边缘缓存 + 本地组播" |
| **无线承载组播** | **组播转单播**：可控、速率高 | **直接组播**：省 AP 处理 | 生产必转单播 |
| **冗余设计** | **Live-Live 双路**：无感切换 | **单路 + 快速收敛**：成本低 | 只有"不可中断"业务才值得 Live-Live |
| **地址分配** | **按业务分 /16**：清晰、可审计 | **随手分配**：省事 | 永远选前者（否则 32:1 冲突必然出现） |
| **二层控制方式** | **IGMP Snooping + Querier**：精确 | **MVR**：多 VLAN 简化 | 单业务多 VLAN 用 MVR；多业务用 Snooping |
| **接入层保护** | **组白名单（IGMP Profile）**：防越界 | **仅组数限制**：防量大 | 两者都要；只能选一个时先选组数限制 |
| **组播在无线** | **组播转单播**：可控 | **直接组播**：省 AP 处理 | 生产必转单播（见第 11 章） |
| **数据中心承载** | **Underlay 组播/EVPN 组播**：省带宽 | **Ingress Replication**：简单 | BUM 大或 VTEP 多 → 必须用组播 |
| **跨企业组播** | **SSM + 精确 ACL**：无 RP 交互 | **PIM + MSDP**：灵活 | 优先 SSM；能不用组播协议更佳 |
| **源冗余** | **源互斥（主备）**：简单、无鬼影 | **Live-Live（双组 + 2022-7）**：无感 | 要"无感"才用双路；否则主备 |
| **超低时延业务** | **传统三层组播（不过 overlay）** | **VXLAN 承载**：灵活 | 行情/HPC 不过 overlay |
| **QoS 队列** | **组播独立队列**：隔离单播突发 | **共享队列**：简单 | 生产必独立（否则拥塞时组播先死） |
| **RP 数量** | **全域一对 Anycast**：管理简单 | **按区域多对**：就近注册 | 跨 WAN 大规模按区域切 |
| **注册开销** | **SSM（无 Register）** | **PIM-SM（有 Register）** | 源固定 → SSM；否则限速 Register |

</div>

---

## Design Anti-Patterns · 设计缺陷

| Flaw | Typical symptom | Root cause | How to avoid it |
|------|---------|------|---------|
| **Multicast addresses picked at random** | receiving another service's stream | 32:1 MAC overlap | block per service + SoT + CI validation |
| **Layer 3 configured without Layer 2** | multicast flooding, access congestion | no IGMP Snooping | the access-layer baseline must include Snooping |
| **Snooping enabled without a Querier** | multicast breaks every few minutes | entries age out | enable PIM or configure the Snooping Querier |
| **mrouter not identified** | Layer 3 never receives Joins | missing static config / no PIM queries | static mrouter or PIM Snooping |
| **A single RP** | after an RP failure no new channel opens | no redundancy | Anycast-RP + MSDP, or Phantom RP |
| **Identical router-ids on Anycast-RP** | MSDP comes up but SA count is 0 | both RPs derive the same ID | explicit unique router-id + originator-id |
| **MSDP peering on the anycast address** | the peer will not come up, or it peers with itself | the peer address is not unique | use a unique loopback |
| **MSDP without sa-filter/sa-limit** | memory exhausted, malicious sources received | no policy | sa-filter + sa-limit + MD5 + ACL |
| **RPF failure** | the source is sending, the mroute is empty | unicast and multicast paths disagree | the three-step `show ip rpf` method + static mroute/MBGP |
| **Leftover legacy static mroutes** | multicast dies after a topology change | static routes have the highest priority | clean up during changes; include in config audits |
| **ECMP without multicast multipath** | some traffic lost, latency jitter | multicast is single-path by default | `ip multicast multipath` |
| **PIM-DM in a large network** | periodic flooding, high CPU | wrong mode chosen | large networks use SM/SSM |
| **Poor multicast VLAN design** | Layer 2 flooding, wasted bandwidth | multicast enters every user VLAN | MVR / multicast VLAN convergence |
| **No MVPN across the domain** | PIM neighbours up, no stream | the transit network does not forward multicast | MVPN or GRE/VXLAN encapsulation |
| **Tunnel MTU not adjusted** | artefacts, large packets lost | GRE/VXLAN encapsulation overhead | reserve with `ip mtu` + DF probing |
| **RP location follows an office move** | latency jumps, unnecessary cross-WAN traffic | no architectural constraint on the RP | put the RP in the core/DC and write it into the design |
| **SPT configured where the shared tree is intended** | state explosion, high CPU | default behaviour not evaluated | choose `spt-threshold` from the traffic model |
| **Live-Live paths sharing physical plant** | one construction job breaks both | only the logical topology was drawn | draw the physical route + SPOF analysis |
| **Direct multicast over wireless** | airtime saturated, picture stutters | low-rate multicast with no ACK | multicast-to-unicast |
| **Verifying only "it can be watched"** | the tree is wrong but it works for now | no tree/loss verification | mrinfo/mtrace + probes + acceptance checklist |
| **IGMPv2 devices mixed into an SSM VLAN** | that VLAN is flaky (breaks whenever the legacy device is on) | version negotiation downgrades | VLAN isolation + SSM Mapping |
| **DR / Querier / HSRP roles scattered** | one floor fails periodically, tables do not agree | three independent elections were never planned | explicitly set dr-priority / querier address |
| **No group-count limit** | a single PC cripples the whole network | no `ip igmp limit` | per-port group limit + group whitelist |
| **Many small high-rate packets + ingress replication** | latency rises from μs to ms, plus loss | per-packet replication cost | underlay multicast / EVPN multicast |
| **High-rate source + RPF failure at the RP** | RP CPU at 90%, network-wide multicast jitter | Register storm | pre-check RPF before go-live + register-rate-limit |
| **Direct multicast over wireless** | AP airtime saturated, a whole floor's Wi-Fi down | lowest rate + no ACK | multicast-to-unicast + raise the basic rates |
| **Two sources on one group (dual-active without exclusion)** | ghosting, two streams mixed | the network builds two trees | source mutual exclusion / two groups + 2022-7 |
| **No multicast boundary (inter-company)** | internal streams appear in the peer's network | the protocol layer does not prevent crossing 239/8 | boundary + sa-filter + RP scope + authentication |
| **Multicast sharing a queue with unicast** | 60% average utilisation yet still dropping | UDP has no say in congestion | dedicated queue + deep queue-limit |
| **Inconsistent RP discovery (merger)** | one-way visibility (half the people can watch) | Auto-RP mixed with static | unify discovery + diff the mappings network-wide |
| **MSDP SA expiry flapping** | receivers across RPs freeze every 75 s | SA refresh lost / peer congested | monitor SA send/receive counters + peer stability |
| **Phantom RP used as load sharing when it is only active/standby** | half the traffic crosses the WAN | misunderstanding of the mechanism | use Anycast + MSDP for load sharing |
| **BSR without a border** | RPs learn each other across domains | hop-by-hop flooding has no boundary | `ip pim bsr-border` + scope |

<div class="zh" markdown="1">

| 缺陷 | 典型现象 | 根因 | 规避方法 |
|------|---------|------|---------|
| **组播地址随手取** | 收到别的业务的流 | 32:1 MAC 重叠 | 按业务分块 + SoT + CI 校验 |
| **只配三层不配二层** | 组播泛洪、接入拥塞 | 无 IGMP Snooping | 接入层基线必含 Snooping |
| **开了 Snooping 没 Querier** | 组播每隔几分钟断 | 表项老化 | 开 PIM 或配置 Snooping Querier |
| **mrouter 未识别** | 三层收不到 Join | 静态配置缺失/无 PIM 查询 | 静态 mrouter 或 PIM Snooping |
| **单 RP** | RP 故障后新频道全打不开 | 无冗余 | Anycast-RP + MSDP 或 Phantom RP |
| **Anycast-RP 的 router-id 相同** | MSDP 建立但 SA 为 0 | 两台 RP 派生同一 ID | 显式唯一 router-id + originator-id |
| **MSDP 用 Anycast 地址建 peer** | peer 起不来或自己连自己 | peer 地址不唯一 | 用唯一 loopback |
| **MSDP 无 sa-filter/sa-limit** | 内存被打爆、收到恶意源 | 无策略 | sa-filter + sa-limit + MD5 + ACL |
| **RPF 失败** | 源在发、mroute 空 | 单播/组播路径不一致 | `show ip rpf` 三步法 + 静态 mroute/MBGP |
| **历史静态 mroute 残留** | 拓扑变了组播全断 | 静态优先级最高 | 变更时清理，纳入配置审计 |
| **ECMP 未开组播多路径** | 部分流量丢、时延抖动 | 组播默认单路径 | `ip multicast multipath` |
| **PIM-DM 用于大网** | 周期性泛洪、CPU 高 | 选错模式 | 大网用 SM/SSM |
| **组播 VLAN 设计不当** | 二层泛洪、带宽浪费 | 组播进所有用户 VLAN | MVR / 组播 VLAN 收敛 |
| **跨域未启用 MVPN** | PIM 邻居有、流不通 | 中间网络不转发组播 | MVPN 或 GRE/VXLAN 承载 |
| **隧道 MTU 未调整** | 花屏、大包丢 | GRE/VXLAN 封装开销 | `ip mtu` 预留 + DF 探测 |
| **RP 位置随办公室搬迁** | 时延突增、跨 WAN 流量 | RP 无架构约束 | RP 放核心/数据中心，写进设计 |
| **保留共享树的场景配了 SPT** | 状态爆炸、CPU 高 | 默认行为未评估 | 按流量模型选 `spt-threshold` |
| **Live-Live 路径共享物理设施** | 一次施工双断 | 只画逻辑拓扑 | 画物理路由 + SPOF 分析 |
| **无线直接组播** | airtime 被打满、画面卡 | 组播低速无 ACK | 组播转单播 |
| **只验证"能看"** | 树结构不对但暂时能用 | 无树/丢包验证 | mrinfo/mtrace + 探针 + 验收清单 |
| **IGMPv2 设备混入 SSM VLAN** | 该 VLAN 时好时坏（老设备开机就坏） | 版本协商降级 | VLAN 隔离 + SSM Mapping |
| **DR / Querier / HSRP 角色分散** | 某楼层周期性中断、查表对不上 | 三个独立选举未规划 | 显式配置 dr-priority / querier 地址 |
| **未设组数限制** | 单台 PC 打瘫全网 | 无 `ip igmp limit` | 每端口组数限制 + 组白名单 |
| **大量小包高频组播 + ingress replication** | 时延从 μs 级升到 ms 级、丢包 | 每包复制开销 | underlay 组播 / EVPN 组播 |
| **高码率源 + RP 侧 RPF 失败** | RP CPU 90%、全网组播抖动 | Register 风暴 | 源上线前预检 RPF + register-rate-limit |
| **无线直接组播** | AP 空口打满、整层 Wi-Fi 瘫 | 最低速率 + 无 ACK | 组播转单播 + 提高基础速率 |
| **同组双源（源双活未互斥）** | 画面叠影、两路流量混流 | 网络层建两条树 | 源互斥 / 双组 + 2022-7 |
| **缺少组播边界（跨企业）** | 内部流出现在对端网络 | 239/8 协议层不阻止跨域 | boundary + sa-filter + RP scope + 认证 |
| **组播与单播共享队列** | 平均利用率 60% 却丢包 | UDP 无话语权 | 独立队列 + 深 queue-limit |
| **RP 发现方式不一致（合并）** | 单向可见（一半人能看） | Auto-RP 与静态混用 | 统一发现方式 + 全网映射 diff |
| **MSDP SA 过期抖动** | 跨 RP 接收者每 75 s 卡一下 | SA 刷新被丢/peer 拥塞 | 监控 SA 收发计数 + peer 稳定性 |
| **Phantom RP 只做主备却当负载分担用** | 一半流量跨 WAN | 原理误解 | 要分担用 Anycast + MSDP |
| **BSR 未配 border** | 域间 RP 互相学习 | 逐跳泛洪无边界 | `ip pim bsr-border` + scope |

</div>

---

## Key Terms · 本章关键术语

| Term | Meaning |
|------|---------|
| Multicast | one-to-many delivery: a single stream reaches many receivers |
| IGMP | Internet Group Management Protocol (host-to-router membership signalling) |
| IGMP Snooping | L2 switch listens to IGMP to build per-port multicast forwarding entries |
| PIM | Protocol Independent Multicast (uses the unicast RIB for RPF) |
| PIM-DM | PIM Dense Mode (flood and prune) |
| PIM-SM | PIM Sparse Mode (explicit joins, RP-based shared tree) |
| PIM-SSM | PIM Source-Specific Multicast (no RP, channel = (S,G)) |
| BiDir-PIM | Bidirectional PIM (a single (*,G) tree shared in both directions) |
| RPF | Reverse Path Forwarding (the only forwarding criterion for multicast) |
| RP | Rendezvous Point (the shared-tree root in PIM-SM) |
| Auto-RP | Cisco-proprietary automatic RP discovery (224.0.1.39/40) |
| BSR | Bootstrap Router (standards-based RP discovery, RFC 5059) |
| Anycast-RP | several RPs sharing one address, synchronised via MSDP (RFC 4610) |
| SPT | Shortest Path Tree (the source-based tree) |
| RPT | Rendezvous Point Tree (the shared tree, (*,G)) |
| MSDP | Multicast Source Discovery Protocol (TCP 639, SA messages) |
| MBGP | Multiprotocol BGP (SAFI 2; supplies the multicast RPF table only) |
| Phantom RP | an RP address that does not exist as a host; routing picks the physical RP |
| Live-Live | dual-active multicast (two sources, two paths, de-duplicated at the receiver) |
| FHRP-Aware PIM | PIM that follows the FHRP active/standby state |
| ASM | Any-Source Multicast |
| SFM | Single-source multicast (an early name for source-specific multicast) |
| LHR / FHR | Last Hop Router / First Hop Router |
| DR | PIM Designated Router (sends Joins/Registers on a LAN) |
| DF | Designated Forwarder in BiDir PIM |
| Join / Prune | PIM join / prune messages |
| Register / Register-Stop | PIM-SM source registration / stop registration |
| Assert | PIM assertion (elects a single forwarder on a LAN) |
| Join Suppression | suppressing duplicate Joins on a multi-access LAN |
| State Refresh | PIM-DM state refresh message |
| Graft | PIM-DM message that re-attaches a pruned branch |
| SPT / RPT | shortest path tree / shared tree (RP tree) |
| `spt-threshold` | the threshold for switching from the RPT to the SPT |
| RPF Failure | reverse path check failure (packets dropped silently) |
| Static mroute | static multicast route (overrides the RPF lookup) |
| MBGP / SAFI 2 | multicast BGP / the multicast address family |
| MTR | Multi-Topology Routing |
| SSM Mapping | mapping an IGMPv2 join to an (S,G) |
| IGMP Querier | the IGMP query sender that maintains group membership |
| Mrouter Port | multicast router port (towards the L3 device) |
| Report Suppression | suppressing duplicate reports |
| MVR | Multicast VLAN Registration |
| MVPN | Multicast VPN (MPLS) |
| mLDP | Multipoint LDP (P2MP LSP signalling) |
| Ingress Replication | ingress replication (overlay BUM replication) |
| GRE | Generic Routing Encapsulation (a tunnel that can carry multicast) |
| PIM Boundary | PIM boundary (limits where multicast may propagate) |
| TTL Threshold | multicast TTL threshold |
| SA / SA-Cache | Source-Active message / source-active cache (MSDP) |
| mesh-group | MSDP mesh group (reduces the number of peers) |
| P2MP | point-to-multipoint |
| AAR | application-aware routing (an SD-WAN related concept) |
| SPOF | single point of failure |
| GLOP | globally assigned multicast addresses derived from the AS number (233.0.0.0/8) |
| SSM Range | the group range used for SSM (default 232.0.0.0/8) |
| INCLUDE / EXCLUDE | the two IGMPv3 source-filter modes (whitelist / blacklist) |
| Group-and-Source-Specific Query | IGMPv3 query naming a specific group and sources |
| General Query | general query (source 0.0.0.0) |
| Group-Specific Query | group-specific query (confirms a Leave) |
| Max Response Time | maximum response time (host randomises its reply) |
| Other Querier Present Timeout | other-querier-present timeout (260 s) |
| Last Member Query Interval | last-member query interval (leave latency) |
| Fast Leave | fast leave (delete the port immediately on Leave) |
| IGMP Profile / Filter | IGMP group whitelist (restricts which groups may be joined at access) |
| IGMP Limit | per-port / per-VLAN group limit |
| MLD / MLDv2 | the IPv6 group management protocol |
| MLD Snooping | IPv6 Layer 2 multicast snooping |
| PIM Hello | PIM neighbour discovery and capability negotiation |
| Holdtime | validity period of Join/Hello/SA |
| Join Suppression | join suppression |
| Prune Override | prune override (keep forwarding on a shared LAN) |
| Encoded Group / Source | group/source encoding inside a PIM Join |
| Wildcard (W bit) | the (*,G) flag |
| RP-bit (R bit) | the shared-tree-towards-RP flag |
| SSM-bit (s bit) | marks an SSM entry in the mroute |
| SPT-bit (T bit) | SPT traffic has been received |
| OIL (Outgoing Interface List) | the mroute outgoing interface list |
| MFIB | Multicast Forwarding Information Base (the data plane) |
| RPF Neighbor | the RPF neighbour (upstream) |
| RPF Failure | RPF check failure |
| RPF Override (static mroute) | using a static route to override the RPF decision |
| MPF (Multicast Forwarding) | multicast forwarding |
| Register Rate Limit | Register rate limit (suppresses storms) |
| Register Probe | the FHR's periodic probe after a Register-Stop |
| DR Priority | PIM DR priority |
| Assert Metric | the metric used in the Assert election |
| DF Election | the BiDir designated forwarder election |
| Phantom RP | a non-existent RP address (routing "partitions" the domain to physical RPs) |
| Scoped Zone | administratively scoped zone (hierarchical multicast domains) |
| Multicast Boundary | multicast address boundary (ACL filtering) |
| TTL Threshold | multicast TTL threshold (hop-count scoping) |
| BSR Border | BSR border (stops the RP-Set crossing the border) |
| RP-Set | the set of RPs distributed by BSR |
| C-RP / C-BSR | candidate RP / candidate BSR |
| RP Priority / RP Hash | the RP selection criteria |
| MSDP SA (Source-Active) | source-active message |
| SA Cache | SA cache (the basis for building trees across RPs) |
| SA Request / Response | SA request and response |
| MD5 / TCP-AO | authentication methods for MSDP/PIM |
| MVPN | multicast VPN |
| MDT (Default / Data) | multicast distribution tree (default / data) |
| I-PMSI / S-PMSI | inclusive / selective P-MSI (MVPN trees) |
| A-D Route | auto-discovery route (MVPN BGP) |
| Rosen / Partitioned MDT | MVPN profile variants |
| Ingress Replication | ingress replication (overlay BUM) |
| Assisted Replication | assisted replication (a designated replication server) |
| EVPN Multicast | EVPN-based multicast optimisation |
| IGMP Proxy | IGMP proxy (firewall scenarios) |
| Multicast-to-Unicast | multicast-to-unicast conversion (wireless) |
| Multicast Direct | the Cisco WLC multicast-to-unicast feature |
| FCC (Fast Channel Change) | fast channel change |
| ST 2022-7 | seamless protection switching (the Live-Live standard) |
| FEC (Forward Error Correction) | redundant coding to recover lost packets |
| Microburst | micro-burst (millisecond-scale above line rate) |
| Output Drops | egress drops (queue overflow) |
| PIM over GRE | carrying PIM/multicast over a GRE tunnel |
| mLDP | Multipoint LDP |
| P2MP LSP | point-to-multipoint label-switched path |
| Multicast VRF | multicast VRF (the MVPN customer side) |
| MoFRR | multicast fast reroute (vendor feature) |
| UMH (Upstream Multicast Hop) | upstream multicast hop selection in MVPN |
| RPF Vector | a BGP attribute that assists RPF in MVPN |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| Multicast | 组播 |
| IGMP | Internet 组管理协议 |
| IGMP Snooping | IGMP 侦听 |
| PIM | 协议无关组播 |
| PIM-DM | PIM 密集模式 |
| PIM-SM | PIM 稀疏模式 |
| PIM-SSM | 源特定组播 |
| BiDir-PIM | 双向 PIM |
| RPF | 反向路径转发 |
| RP | 汇聚点 |
| Auto-RP | 自动 RP |
| BSR | 自举路由器 |
| Anycast-RP | 任播 RP |
| SPT | 最短路径树 |
| RPT | 共享路径树 (RP Tree) |
| MSDP | 组播源发现协议 |
| MBGP | 组播 BGP |
| Phantom RP | 幻影 RP |
| Live-Live | 双活组播 |
| FHRP-Aware PIM | FHRP 感知 PIM |
| ASM | 任意源组播（Any-Source Multicast） |
| SFM | 单源组播（Source-Specific Multicast 的早期叫法） |
| LHR / FHR | 最后一跳路由器 / 第一跳路由器 |
| DR | PIM 指定路由器（负责 Join/Register） |
| DF | BiDir PIM 的指定转发者 |
| Join / Prune | PIM 加入 / 剪枝消息 |
| Register / Register-Stop | PIM-SM 源注册 / 停止注册 |
| Assert | PIM 断言（同一 LAN 选唯一转发者） |
| Join Suppression | 加入抑制（避免重复 Join） |
| State Refresh | PIM-DM 的状态刷新 |
| Graft | PIM-DM 的接回消息 |
| SPT / RPT | 最短路径树 / 共享树（RP 树） |
| `spt-threshold` | SPT 切换阈值 |
| RPF Failure | 反向路径检查失败 |
| 静态 mroute | 静态组播路由（覆盖 RPF） |
| MBGP / SAFI 2 | 组播 BGP / 组播地址族 |
| MTR | 多拓扑路由 |
| SSM Mapping | 把 IGMPv2 加入映射为 (S,G) |
| IGMP Querier | IGMP 查询器（维持组成员关系） |
| Mrouter Port | 组播路由器端口 |
| Report Suppression | 报告抑制 |
| MVR | 组播 VLAN 注册 |
| MVPN | 组播 VPN（MPLS） |
| mLDP | 多点标签分发协议（P2MP LSP） |
| Ingress Replication | 入口复制（overlay 的 BUM 复制方式） |
| GRE | 通用路由封装（承载组播的隧道） |
| PIM Boundary | PIM 边界（限制组播扩散） |
| TTL Threshold | 组播 TTL 阈值 |
| SA / SA-Cache | 源活跃消息 / 源活跃缓存（MSDP） |
| mesh-group | MSDP 网状组（减少 peer 数量） |
| P2MP | 点到多点 |
| AAR | 应用感知路由（SD-WAN 关联概念） |
| SPOF | 单点故障 |
| GLOP | 按 AS 号分配全球组播地址（233.0.0.0/8） |
| SSM Range | SSM 使用的组地址范围（默认 232.0.0.0/8） |
| INCLUDE / EXCLUDE | IGMPv3 的两种源过滤模式（白名单 / 黑名单） |
| Group-and-Source-Specific Query | IGMPv3 的组源特定查询 |
| General Query | 通用查询（0.0.0.0） |
| Group-Specific Query | 组特定查询（Leave 后确认） |
| Max Response Time | 最大响应时间（主机随机延迟） |
| Other Querier Present Timeout | 其他查询者存在超时（260 s） |
| Last Member Query Interval | 最后成员查询间隔（离开时延） |
| Fast Leave | 快速离开（收到 Leave 立即删除端口） |
| IGMP Profile / Filter | IGMP 组白名单（接入层限制可加入的组） |
| IGMP Limit | 每端口/VLAN 组数上限 |
| MLD / MLDv2 | IPv6 的组管理协议 |
| MLD Snooping | IPv6 的二层组播侦听 |
| PIM Hello | PIM 邻居发现与能力协商报文 |
| Holdtime | Join/Hello/SA 的有效期 |
| Join Suppression | Join 抑制 |
| Prune Override | 剪枝否决（同 LAN 保留转发） |
| Encoded Group / Source | PIM Join 报文中的组/源编码 |
| Wildcard（W 位） | (*,G) 的标志位 |
| RP-bit（R 位） | 指向 RP 的共享树标志 |
| SSM-bit（s 位） | mroute 中标识 SSM |
| SPT-bit（T 位） | 已收 SPT 流量 |
| OIL（Outgoing Interface List） | mroute 的出接口列表 |
| MFIB | 组播转发信息库（数据面） |
| RPF Neighbor | RPF 邻居（上游） |
| RPF Failure | RPF 检查失败 |
| RPF Override（静态 mroute） | 用静态路由覆盖 RPF 判断 |
| MPF（Multicast Forwarding） | 组播转发 |
| Register Rate Limit | Register 速率限制（抑制风暴） |
| Register Probe | FHR 在 Register-Stop 后的周期性探测 |
| DR Priority | PIM DR 优先级 |
| Assert Metric | Assert 选举使用的度量 |
| DF Election | BiDir 指定转发者选举 |
| Phantom RP | 不存在的 RP 地址（用路由"分区"指物理 RP） |
| Scoped Zone | 管理范围（组播域分层） |
| Multicast Boundary | 组播地址边界（ACL 过滤） |
| TTL Threshold | 组播 TTL 阈值（按跳数限制范围） |
| BSR Border | BSR 边界（阻断 RP-Set 越界） |
| RP-Set | BSR 分发的 RP 集合 |
| C-RP / C-BSR | 候选 RP / 候选 BSR |
| RP Priority / RP Hash | RP 选择依据 |
| MSDP SA（Source-Active） | 源活跃消息 |
| SA Cache | SA 缓存（跨 RP 建树依据） |
| SA Request / Response | SA 请求与响应 |
| MD5 / TCP-AO | MSDP/PIM 的认证方式 |
| MVPN | 组播 VPN |
| MDT（Default / Data） | 组播分发树（默认/数据） |
| I-PMSI / S-PMSI | 包含性/选择性 P-MSI（MVPN 树） |
| A-D Route | 自动发现路由（MVPN BGP） |
| Rosen / Partitioned MDT | MVPN 的 profile 形态 |
| Ingress Replication | 入口复制（overlay BUM） |
| Assisted Replication | 辅助复制（指定复制服务器） |
| EVPN Multicast | 基于 EVPN 的组播优化 |
| IGMP Proxy | IGMP 代理（防火墙场景） |
| Multicast-to-Unicast | 组播转单播（无线） |
| Multicast Direct | Cisco WLC 的组播转单播特性 |
| FCC（Fast Channel Change） | 快速频道切换 |
| ST 2022-7 | 无缝保护切换（Live-Live 标准） |
| FEC（前向纠错） | 冗余校验恢复丢包 |
| Microburst | 微突发（毫秒级超线速） |
| Output Drops | 出方向丢弃（队列溢出） |
| PIM over GRE | 用 GRE 承载组播 |
| mLDP | 多点标签分发协议 |
| P2MP LSP | 点到多点标签交换路径 |
| Multicast VRF | 组播 VRF（MVPN 客户侧） |
| MoFRR | 组播快速重路由（厂商特性） |
| UMH（Upstream Multicast Hop） | MVPN 中的上游组播跳选择 |
| RPF Vector | MVPN 中辅助 RPF 的 BGP 属性 |

</div>

---

## Lessons from the Field · 实战经验总结

1. **The first question in troubleshooting is always RPF.** In "the source is sending but nothing arrives" scenarios, `show ip rpf` plus `show ip mroute` solves 80% of cases. Most of the remaining 20% are Layer 2 (Snooping/Querier).
2. **If SSM is possible, do not use PIM-SM.** Every bit of PIM-SM's complexity (RP, Register, shared tree, SPT switchover, MSDP) is the price of "not knowing the source". A fixed source = use SSM; this is the single decision that most reduces long-term operational cost.
3. **Multicast addresses must be planned.** The 32:1 mapping overlap is not a theoretical problem; it appears reliably in networks that "just pick addresses", and it gets misdiagnosed as a security incident. Blocking per service + writing it into the SoT + CI validation is the only reliable approach.
4. **Layer 2 is multicast's "last-mile trap".** Designing only Layer 3 and ignoring IGMP Snooping and the Querier produces two classic failures: "flooding saturates the access layer" and "it breaks every few minutes".
5. **The RP must be redundant, and Anycast-RP has three "must be different" rules.** router-id, MSDP peer address and originator-id must all be unique — these details determine the insidious "MSDP is up but the SA count is 0" failure.
6. **SPT switchover is a trade-off, not a default optimum.** A few high-rate channels should switch; thousands of small channels save far more state by staying on the shared tree. Compute the state count and RP bandwidth first.
7. **The effectiveness of redundancy depends only on the number of shared points.** Live-Live, dual carriers and dual-active data centres are all the same: **logical topology separation is not physical path separation**. You must draw the physical route diagram and do a SPOF analysis.
8. **Acceptance must verify the "tree", not just "it can be watched".** `mrinfo`/`mtrace` show the tree structure, NetFlow shows replication amplification, probes show real loss — only all three together prove that "the multicast path matches the design".
9. **DR, Querier, HSRP Active, Assert Winner and DF are five independent roles.** "Identical configuration" does not mean "identical behaviour"; mis-placed roles inside one VLAN produce the hardest class of failure to diagnose — "periodic outages". They must be specified explicitly (`dr-priority`, `querier address`); never let the protocols choose.
10. **The precondition for SSM is "every terminal in the Layer 2 domain is IGMPv3".** A single legacy device's v2 Report downgrades the whole VLAN, and it looks like "flaky". The antidote is "VLAN isolation + SSM Mapping", not "change the network configuration".
11. **The access layer's two seat belts: a group-count limit and a group whitelist.** One buggy player can make a single port join thousands of groups and take down the entire network. `ip igmp limit` stops the "volume", `ip igmp profile` stops "out-of-bounds"; you need both.
12. **Micro-bursts are the hidden killer behind multicast loss.** "60% average utilisation yet dropping" is its fingerprint. Multicast must have its own queue, and capacity planning must use "peak packet rate", not "average bandwidth".
13. **The root cause of a Register storm is almost always RPF; `register-rate-limit` is only a tourniquet.** Before a high-rate source goes live, do a `show ip rpf <source>` pre-check on the RP — this single step prevents 90% of "the new service took down the network" incidents.
14. **The cost of multicast on wireless is airtime, not bandwidth.** A 4 Mbps stream can consume more than 80% of the air on an AP with 180 clients. Multicast-to-unicast is mandatory, but you must also estimate "client count × bitrate".
15. **Source redundancy is an application-layer problem.** The network can only forward what it sees; two sources on one group inevitably create two trees, and receivers get mixed data (ghosting). The design must state: who is primary, what the switch-over criterion is, and how the receiver tells them apart.
16. **Inter-company multicast must be isolated on four layers at once** (address boundary, SA filtering, RP scope, authentication). The "private" nature of 239/8 is only a paper convention; the protocol layer does nothing to stop propagation across domains.
17. **Merging two multicast domains is not "connecting the links" but "redesigning one domain".** "One-way visibility" almost always means inconsistent RP mappings; the cheapest merger path is "move every fixed-source service to SSM first", which reduces what must be unified to the address plan alone.
18. **Multicast operability is part of the design, not something to add after go-live.** Without mroute counts, RPF-failure counters, tree-structure baselines and end-to-end probes, you cannot distinguish "nothing works", "partly works" and "it works but the tree is wrong" — and those three have completely different remedies.

<div class="zh" markdown="1">

1. **排障第一问永远是 RPF。** "源在发、收不到" 的场景里，`show ip rpf` + `show ip mroute` 能解决 80% 的问题。剩下 20% 里有大半是二层（Snooping/Querier）。
2. **能 SSM 就不要 PIM-SM。** PIM-SM 的全部复杂度（RP、Register、共享树、SPT 切换、MSDP）都在为"不知道源"买单。源固定 = 用 SSM，这是最能降低长期运维成本的一个决定。
3. **组播地址必须规划。** 32:1 的映射重叠不是理论问题，它会在"随手取地址"的网络里稳定出现，并被误判为安全事件。按业务分块 + 写进 SoT + CI 校验，是唯一可靠的做法。
4. **二层是组播的"最后一公里陷阱"。** 只做三层设计、忽略 IGMP Snooping 与 Querier，会出现"泛洪打满接入"或"每几分钟断一次"这两类典型故障。
5. **RP 必须有冗余，且 Anycast-RP 有三个"必须不同"。** router-id、MSDP peer 地址、originator-id 必须唯一 —— 这些细节决定"MSDP 建立了但 SA 为 0"的隐蔽故障。
6. **SPT 切换是取舍，不是默认最优。** 大流量单频道该切；海量小频道保留共享树更省状态。设计前先算状态量与 RP 带宽。
7. **冗余的有效性取决于共享点的数量。** Live-Live、双运营商、双活数据中心都一样：**逻辑拓扑分离不等于物理路径分离**。必须画物理路由图并做 SPOF 分析。
8. **验收要验证"树"，不只是"能看"。** `mrinfo`/`mtrace` 看树结构、NetFlow 看复制放大、探针看真实丢包 —— 三者合起来才能证明"组播路径符合设计"。
9. **DR、Querier、HSRP Active、Assert Winner、DF 是五个独立角色。** "配置一致"不代表"行为一致"，同一 VLAN 内角色错位会造成"周期性中断"这类最难查的故障。设计时必须显式指定（`dr-priority`、`querier address`），不要让协议自己选。
10. **SSM 的前提是"整个二层域终端都是 IGMPv3"。** 一台老设备的 v2 Report 就能让整个 VLAN 降级，表现为"时好时坏"。解药是"VLAN 隔离 + SSM Mapping"，不是"改网络配置"。
11. **接入层的两条安全带：组数限制 + 组白名单。** 一个有 Bug 的播放器就能让单端口加入几千个组，把整张网打瘫。`ip igmp limit` 防"量"，`ip igmp profile` 防"越界"，缺一不可。
12. **微突发是组播丢包的隐藏杀手。** "平均利用率 60% 却丢包"是它的典型指纹。组播必须有自己的队列，且必须按"峰值包速率"而不是"平均带宽"做容量规划。
13. **Register 风暴的根因几乎总是 RPF，`register-rate-limit` 只是止血带。** 高码率源上线前，必须在 RP 上做一次 `show ip rpf <源>` 的预检 —— 这一步能避免 90% 的"新业务上线打瘫全网"。
14. **无线承载组播的成本是 airtime，不是带宽。** 4 Mbps 的流在 180 个客户端的 AP 上可以吃掉 80% 以上的空口。组播转单播是必配，但也要评估"客户端数 × 码率"的总量。
15. **源冗余是应用层问题。** 网络只能转发它看到的；两个源发同一个组必然产生两条树，接收端会拿到混杂数据（鬼影）。设计必须明确：谁是主、切换判据、接收端怎么区分。
16. **跨企业组播必须四层同时隔离**（地址边界、SA 过滤、RP scope、认证）。239/8 的"私有"只是纸面约定，协议层完全不阻止跨域扩散。
17. **合并两套组播域不是"打通链路"，而是"重新设计一套"。** "单向可见"几乎总是 RP 映射不一致；最省力的合并路径是"先把源固定的业务全改成 SSM"，把需要统一的东西降到只剩地址规划。
18. **组播的可运维性是设计的一部分，不是"上线后再说"。** 没有 mroute 数、RPF 失败计数、树结构基线、端到端探针，你无法区分"完全不通"、"部分不通"和"通了但树不对"——而这三类问题的修法完全不同。

</div>

---

## Design Scenario Drills (Multicast) · 设计情景演练（组播）

> CCDE multicast questions almost never ask "how do you write the configuration"; they ask "given this service and these constraints, which option do you choose, why, and what did you give up".

<div class="zh" markdown="1">

> CCDE 的组播题几乎从不问"配置怎么写"，而是问"在这个业务与约束下，你选哪个方案，为什么，放弃了什么"。

</div>

### Scenario A: Multi-Site Video Conferencing Migration · 情景 A：多站点视频会议改造

**Background**: the enterprise has 1 headquarters + 12 branches (hub-and-spoke WAN). Video conferencing currently uses "separate unicast per site" (the MCU replicates per site), and the WAN saturates during all-hands meetings. The requirement is to migrate to multicast, with "any site able to be the speaker".

<div class="zh" markdown="1">

**背景**：企业有 1 个总部 + 12 个分支（Hub-Spoke WAN），现有视频会议用"每站点单独单播"（MCU 逐站点复制），WAN 带宽在全员会议时打满。要求改造为组播，且"任何站点都可以是发言方"。

</div>

**Key constraints**:
- conferencing is **many-to-many** (any site may speak)
- branch WAN links are limited (50 Mbps)
- the conferencing terminals only support IGMPv2
- the current network has a single RP with no redundancy

<div class="zh" markdown="1">

**关键约束**：
- 会议是**多对多**（每个站点都可能发言）
- 分支 WAN 链路带宽有限（50 Mbps）
- 会议终端只支持 IGMPv2
- 现有网络只有 1 台 RP，无冗余

</div>

**Candidate options and assessment**:

<div class="zh" markdown="1">

**候选方案与判断**：

</div>

| Option | State volume | WAN bandwidth | Complexity | Verdict |
|------|-------|---------|--------|------|
| **PIM-SM (single RP) + SPT** | high ((S,G) per source per receiver) | medium | medium | ✗ terminals are v2-only (workable) but the RP is a single point and state grows with the number of sites |
| **BiDir-PIM** | **lowest** (only (*,G)) | **medium (traffic must traverse the RP)** | medium | **✓ the best match for "many-to-many"** |
| **SSM** | low | low | **low** | ✗ terminals are v2 and the source is not fixed (any site may speak) |
| **PIM-DM** | medium (prune state) | **high (periodic flooding)** | low | ✗ flooding across the WAN is unacceptable |
| **Unicast MCU distribution** | none | **high (per-site replication)** | low | ✗ this is the current problem |

<div class="zh" markdown="1">

| 方案 | 状态量 | WAN 带宽 | 复杂度 | 结论 |
|------|-------|---------|--------|------|
| **PIM-SM（单 RP）+ SPT** | 高（每源每接收者 (S,G)） | 中 | 中 | ✗ 终端只支持 v2（可以）+ RP 单点 + 状态随站点数增长 |
| **BiDir-PIM** | **最低**（只有 (*,G)） | **中（流量必须过 RP）** | 中 | **✓ 最匹配"多对多"** |
| **SSM** | 低 | 低 | **低** | ✗ 终端 v2、源不固定（每个站点都可能发言） |
| **PIM-DM** | 中（剪枝状态） | **高（周期泛洪）** | 低 | ✗ 跨 WAN 泛洪不可接受 |
| **单播 MCU 分发** | 无 | **高（逐站点复制）** | 低 | ✗ 现状就是问题 |

</div>

**Recommendation**: **BiDir-PIM + RP high availability (Anycast or Phantom RP) + the RP placed at headquarters (a compromise between sources and receivers) + multicast rate limiting on each site's uplink**.

<div class="zh" markdown="1">

**推荐**：**BiDir-PIM + RP 高可用（Anycast 或 Phantom RP）+ RP 放在总部（源/接收者的折中点）+ 每站点上联做组播限速**。

</div>

**Three "costs" that must be answered at the same time**:
1. **Traffic must traverse the RP** → higher latency (cross-site conferencing may add ~30 ms) → is that acceptable?
2. **RP failure = total outage** (BiDir has no SPT fallback) → Anycast-RP is mandatory, and the switch-over budget must go into the SLA.
3. **BiDir does not support SSM** → if SSM services are introduced later, they must use a different group range.

<div class="zh" markdown="1">

**必须同时回答的三个"代价"**：
1. **流量必须过 RP** → 时延增加（跨站点会议时延可能 +30 ms）→ 是否可接受？
2. **RP 故障 = 全部中断**（BiDir 没有 SPT 退路）→ 必须做 Anycast-RP，且切换预算要写进 SLA。
3. **BiDir 不支持 SSM** → 将来若要引入 SSM 业务，必须用不同的组地址段。

</div>

### Scenario B: Exchange Market-Data Distribution · 情景 B：交易所行情分发

**Background**: market-data sources (dual-active) distribute to 300 members, requiring end-to-end latency < 2 ms, loss < 1e-6, and no interruption from any single failure.

<div class="zh" markdown="1">

**背景**：行情源（双活）向 300 家会员分发，要求端到端 < 2 ms、丢包率 < 1e-6、任意单点故障不中断。

</div>

**Key constraints**: ultra-low latency, zero tolerance for loss, dual-active sources, members spread across different cities.

<div class="zh" markdown="1">

**关键约束**：超低时延、零容忍丢包、双活源、会员分布在不同城市。

</div>

**Design points (top-down)**:

<div class="zh" markdown="1">

**设计要点（自上而下）**：

</div>

| Layer | Decision | Rationale |
|----|------|------|
| **Addressing** | 232/8 (SSM), two sources and two groups | no RP, no MSDP, no cross-domain control-plane interaction |
| **Mode** | SSM (not SM) | the source is known; fewest states; no Register; switching is a single Join |
| **Transport** | a dedicated Layer 3 multicast network, **not over an overlay** (no VXLAN) | any encapsulation adds latency (see Case 11) |
| **Redundancy** | **Live-Live (ST 2022-7) + physical path separation** | the only way to be "hitless" (not "faster convergence") |
| **QoS** | a dedicated multicast queue + deep queue-limit + source-side rate limiting | micro-bursts are the biggest killer (see Case 17) |
| **Layer 2** | no flooding at access (Snooping + static groups); dedicated circuits on the member side | eliminates replication amplification |
| **Sources** | dual-active but **must be mutually exclusive or use two groups** | avoids "two sources on one group" (see Case 15) |
| **Acceptance** | physical link cuts + micro-burst stress tests + end-to-end probes | look at "peak packet rate", not "average bandwidth" |

<div class="zh" markdown="1">

| 层 | 决策 | 理由 |
|----|------|------|
| **地址** | 232/8（SSM），双源双组 | 无 RP、无 MSDP、无跨域控制面交互 |
| **模式** | SSM（不用 SM） | 源已知；状态最少；无 Register；切换即 Join |
| **承载** | 专用三层组播网络，**不过 overlay**（不用 VXLAN） | 任何封装都增加时延（见案例十一） |
| **冗余** | **Live-Live（ST 2022-7）+ 物理路径分离** | 唯一能做到"无感"的方案（不是"收敛更快"） |
| **QoS** | 组播独立队列 + 深 queue-limit + 源侧限速 | 微突发是最大杀手（见案例十七） |
| **二层** | 接入不做泛洪（Snooping + 静态组）；会员侧专线 | 消除复制放大 |
| **源** | 双活但**必须互斥或使用两个组** | 避免"同组双源"（见案例十五） |
| **验收** | 物理断链 + 微突发压测 + 端到端探针 | 不看"平均带宽"，看"峰值包速率" |

</div>

**"Known limitations" that must appear in the design document**:
- if the two paths share one duct, Live-Live is defeated (a physical route diagram is mandatory)
- if member-side terminals do not support ST 2022-7, it degrades to "active/standby switchover" (with an interruption)
- if a city has only one available path, hitless operation cannot be achieved there

<div class="zh" markdown="1">

**必须写进设计文档的"已知限制"**：
- 若两条路径共享同一段管道 → Live-Live 失效（必须画物理路由图）
- 若会员侧终端不支持 ST 2022-7 → 退化为"主备切换"（有中断）
- 若某城市只有一条可用路径 → 该城市无法实现"无感"

</div>

### Scenario C: Multicast Governance — from "It Works" to "It Is Operable" · 情景 C：从"能通"到"可运营"的组播治理

**Background**: a campus multicast network that has run for 8 years, carrying IPTV, CCTV, conferencing, access-control broadcast and more — 4,000+ group addresses, no unified plan, no monitoring, maintained from "the memory of long-serving staff". The requirement is to "improve stability and reduce outage duration".

<div class="zh" markdown="1">

**背景**：一个运营了 8 年的园区组播网络，有 IPTV、监控、会议、门禁广播等多种业务，共 4,000+ 组地址，无统一规划、无监控、靠"老员工记忆"维护。要求"提高稳定性、降低故障时长"。

</div>

**This is not a technology-selection question but a governance question. Four workstreams**:

<div class="zh" markdown="1">

**这不是技术选型题，而是治理题。四条主线**：

</div>

| Workstream | Action | Output |
|------|------|------|
| **① Visibility** | deploy four layers of monitoring (protocol/traffic/tree/service) + group-address snapshots | able to answer "which groups exist now, which path do they take, who is watching" |
| **② Convergence** | re-plan addresses (blocks per service) + group whitelist + group-count limits | eliminates 32:1 collisions and "out-of-bounds groups" |
| **③ Simplification** | move every fixed-source service to SSM; converge the RPs into an Anycast pair | fewer RP dependencies, less state |
| **④ Boundaries** | fill in every domain boundary (boundary/scope/sa-filter/authentication) | prevents "one bug takes down the network" and information leaks |

<div class="zh" markdown="1">

| 主线 | 动作 | 产出 |
|------|------|------|
| **① 可见性** | 部署四层监控（协议/流量/树/业务）+ 组地址快照 | 能回答"现在有哪些组、走哪条路、谁在看" |
| **② 收敛** | 地址重新规划（按业务分块）+ 组白名单 + 组数限制 | 消除 32:1 冲突与"越界组" |
| **③ 简化** | 源固定的业务全改 SSM；RP 收敛为 Anycast 双活 | 减少 RP 依赖、状态量下降 |
| **④ 边界** | 补上所有域边界（boundary/scope/sa-filter/认证） | 防"一个 Bug 打瘫全网"与信息泄露 |

</div>

**How to prioritise the governance work (the key point)**:
- **do ① (visibility) first**: a migration without monitoring is "surgery with your eyes closed", and you cannot prove the migration worked
- **then ④ (boundaries)**: lowest cost, fastest benefit (one ACL prevents the largest class of incidents)
- **then ② (convergence)**: address re-planning has a wide blast radius, but it must be done (otherwise collisions recur)
- **finally ③ (simplification)**: the biggest benefit but needs business cooperation (terminal upgrades, application changes)

<div class="zh" markdown="1">

**治理的优先级判断（关键）**：
- **先做 ①（可见性）**：没有监控的改造等于"闭眼手术"，且无法证明改造有效
- **再做 ④（边界）**：成本最低、收益最快（一条 ACL 就能防住最大的一类事故）
- **然后 ②（收敛）**：地址重规划影响面大，但必须做（否则冲突必然复发）
- **最后 ③（简化）**：收益最大但需要业务配合（终端升级、应用改造）

</div>

---

## Chapter Summary · 本章小结

The complexity of multicast can be reduced to one thread: **"how to deliver one copy of the traffic to many receivers without broadcasting"**. Every protocol mechanism is a branch of that thread:

<div class="zh" markdown="1">

组播的复杂度可以归纳成一条主线：**"如何在不广播的前提下，把同一份流量送到多个接收者"**。所有协议机制都是这条主线的分支：

</div>

| Question | Mechanism | Design judgement |
|------|------|---------|
| **How do receivers express "I want it"?** | IGMP/MLD (v1/v2/v3) | SSM requires v3; mixed environments downgrade |
| **How do we avoid Layer 2 flooding?** | IGMP/PIM Snooping + Querier | mandatory, and mind the Querier dependency |
| **How do we prevent loops and duplicates?** | **RPF** check + Assert | the unicast routing table decides the multicast path |
| **Where is the source?** | RP (PIM-SM) or "already known" (SSM) | fixed source → SSM; many-to-many → BiDir |
| **How does it scale?** | shared tree/source tree, SPT threshold, state optimisation | trade off against the traffic model |
| **How does it cross domains?** | MSDP + MBGP, or SSM | new deployments prefer SSM |
| **How do we guarantee continuity?** | Anycast-RP, Live-Live, FHRP-Aware PIM | redundancy must be physically separated |
| **How do we stop one bug taking down the network?** | group-count limits, group whitelists, source-side rate limiting, register-rate-limit | the access layer needs both seat belts |
| **How do we avoid packet loss?** | dedicated queues, deep queue-limit, micro-burst assessment, FEC | average bandwidth is not a capacity basis |
| **How do we guarantee "hitless"?** | Live-Live (ST 2022-7) + physical path separation | fast convergence ≠ hitless |
| **How do we go inter-company/inter-domain?** | SSM + boundaries + SA filtering + RP scope + authentication | isolate on four layers; one missing layer means none |
| **How do we keep it operable?** | four layers of monitoring + tree baselines + acceptance cases | observability is part of the design |

<div class="zh" markdown="1">

| 问题 | 机制 | 设计判断 |
|------|------|---------|
| **接收者怎么表达"我要"？** | IGMP/MLD（v1/v2/v3） | 要 SSM 必须 v3；混跑会降级 |
| **二层怎么不泛洪？** | IGMP/PIM Snooping + Querier | 必配，且注意 Querier 依赖 |
| **怎么防止环路与重复？** | **RPF** 检查 + Assert | 单播路由决定组播路径 |
| **源在哪？** | RP（PIM-SM）或"已知"（SSM） | 源固定 → SSM；多对多 → BiDir |
| **怎么扩展？** | 共享树/源树、SPT 阈值、状态优化 | 按流量模型取舍 |
| **怎么跨域？** | MSDP + MBGP，或 SSM | 新建优先 SSM |
| **怎么保证不中断？** | Anycast-RP、Live-Live、FHRP-Aware PIM | 冗余必须物理分离 |
| **怎么防止一个 Bug 打瘫全网？** | 组数限制、组白名单、源侧限速、register-rate-limit | 接入层两条安全带缺一不可 |
| **怎么保证不丢包？** | 独立队列、深 queue-limit、微突发评估、FEC | 平均带宽不是容量依据 |
| **怎么保证"无感"？** | Live-Live（ST 2022-7）+ 物理路径分离 | 收敛快 ≠ 无感 |
| **怎么跨企业/跨域？** | SSM + 边界 + SA 过滤 + RP scope + 认证 | 四层同时隔离，少一层等于没有 |
| **怎么可运维？** | 四层监控 + 树基线 + 验收用例 | 可观测性是设计的一部分 |

</div>

From a CCDE perspective, multicast design really has to answer four questions:

<div class="zh" markdown="1">

CCDE 视角下，组播设计真正要回答的四个问题：

</div>

1. **Is the application "one-to-many", "many-to-many" or "source known"?** (decides the PIM mode)
2. **Where does the RP live, how is it made redundant, how is mapping consistency guaranteed?** (decides availability)
3. **How does Layer 2 deliver multicast only where it is needed?** (decides whether the access layer is overwhelmed)
4. **Across domains or firewalls, how do transport, RPF and RP reachability all hold at the same time?** (decides whether the project ships)

<div class="zh" markdown="1">

1. **应用是"一对多"、"多对多"还是"源已知"？**（决定 PIM 模式）
2. **RP 放在哪里、怎么冗余、映射怎么保证一致？**（决定可用性）
3. **二层如何只把组播送到需要的地方？**（决定接入层是否被打爆）
4. **跨域/跨防火墙时，承载、RPF、RP 可达三件事怎么同时成立？**（决定项目能否上线）

</div>

Once these four are answered, `ip pim sparse-mode` is just the last line of configuration.

<div class="zh" markdown="1">

这四问答清楚，`ip pim sparse-mode` 只是最后一行配置。

</div>

> 📌 **The next chapter (Chapter 14, QoS Design)** discusses another class of "end-to-end consistency" problem: multicast cares about "one copy of traffic reaching many receivers", while QoS cares about "in what order many flows are served". They share one property — **if one segment of the path is not configured to match, the end-to-end design fails**.

<div class="zh" markdown="1">

> 📌 **下一章（第 14 章 QoS 设计）**会讨论另一类"端到端一致性"问题：组播关心"一份流量到多个接收者"，QoS 关心"多份流量按什么顺序被服务"。两者有个共同点 —— **只要链路上有一段没配对，端到端的设计就失效**。

</div>
