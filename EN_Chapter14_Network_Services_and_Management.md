# Chapter 14: Network Services and Management · 第 14 章：网络服务与管理

> Chinese translation and in-depth commentary on the *CCDE 400-007 Official Cert Guide* | original pages 626–707

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译与精讲 | 原书第 626-707 页

</div>

---

## What This Chapter Covers · 本章涵盖主题

- **IPv6 design considerations**: address planning, SLAAC/DHCPv6, NDP and security, migration and dual stack, routing and multihoming
- **QoS design**: business drivers, the DiffServ model, DSCP and trust boundaries, queueing and bandwidth calculation, end-to-end consistency
- **Network management and services**: management-plane design, SNMP/logging/flows/telemetry, time synchronisation, DHCP/DNS/AAA, observability and alert governance

<div class="zh" markdown="1">

- **IPv6 设计考量**：地址规划、SLAAC/DHCPv6、NDP 与安全、迁移与双栈、路由与多宿主
- **QoS 设计**：业务驱动、DiffServ 模型、DSCP 与信任边界、队列与带宽计算、端到端一致性
- **网络管理与服务**：管理平面设计、SNMP/日志/流/遥测、时间同步、DHCP/DNS/AAA、可观测性与告警治理

</div>

---

## Chapter Roadmap: Twelve Counter-intuitive Truths About Network Services and Management · 本章导读：网络服务与管理的十二个反直觉认知

These three topics (IPv6, QoS, management) sit in one chapter of the blueprint, and many readers treat them as "three unrelated mini-topics". In fact they share one essence:

<div class="zh" markdown="1">

这三块内容（IPv6、QoS、管理）在大纲里被放在同一章，很多读者以为是"三个不相关的小专题"。其实它们共享同一个本质：

</div>

> **None of them is "a function on the forwarding path"; all of them are the supporting systems that make the forwarding path operable and able to express priority.**

<div class="zh" markdown="1">

> **它们都不是"转发路径上的功能"，而是"让转发路径可运营、可表达优先级"的支撑系统。**

</div>

The hard part of designing supporting systems is not the protocol but **dependencies and scale**. Below are the twelve statements most often got wrong in design reviews.

<div class="zh" markdown="1">

支撑系统的设计难点不在协议，而在**依赖关系与规模**。以下是十二个最容易在设计评审里说错的判断。

</div>

### 1. IPv6 Is Not "IPv4 with Longer Addresses" — It Is a Different Set of Operating Rules · IPv6 不是"地址更长的 IPv4"，而是一套不同的运行规则

Treating IPv6 as "addresses going from 32 bits to 128 bits" fails immediately in four places:

<div class="zh" markdown="1">

把 IPv6 当成"地址从 32 位变 128 位"，会在四个地方直接翻车：

</div>

| Difference | IPv4 intuition | IPv6 reality |
|------|------------|------------|
| **Broadcast** | ARP broadcast to find a neighbour | **No broadcast**: NS/NA multicast, hard dependency on ICMPv6 |
| **Fragmentation** | Routers may fragment | **Routers do not fragment**; only the source may fragment, so PMTUD is mandatory |
| **Address acquisition** | DHCP is the norm | SLAAC is the default; DHCPv6 is often used only to "supplement DNS" |
| **Subnet size** | /24 or /25, split as you like | **/64 is inviolable** (SLAAC and ND both assume a 64-bit IID) |
| **Multihoming** | NAT hides everything | No NAT; source address selection (RFC 6724) decides which exit is used |

<div class="zh" markdown="1">

| 差异 | IPv4 的直觉 | IPv6 的现实 |
|------|------------|------------|
| **广播** | ARP 广播找邻居 | **没有广播**，用 NS/NA 组播，强依赖 ICMPv6 |
| **分片** | 路由器可以分片 | **路由器不分片**，只有源端可分片，必须靠 PMTUD |
| **地址获取** | DHCP 是常态 | SLAAC 是默认，DHCPv6 常只用于"补充 DNS" |
| **子网大小** | /24、/25 随便切 | **/64 不可破**（SLAAC 与 ND 都假设 64 位 IID） |
| **多宿主** | NAT 掩盖一切 | 无 NAT，源地址选择（RFC 6724）决定走哪个出口 |

</div>

> ⚠️ **The classic outage**: splitting one /64 into two /72s for two VLANs, "to save addresses". The result is that some terminals get no address, some get an address but cannot reach the gateway — while pinging the gateway works (because that one machine had a static configuration).

<div class="zh" markdown="1">

> ⚠️ **最典型的事故**：把一段 /64 切成两个 /72 给两个 VLAN "省地址"。结果部分终端拿不到地址、部分拿到地址但网关不可达 —— 而 ping 网关却是通的（因为那台机器手工配了静态）。

</div>

### 2. IPv6 Does Not Lack Addresses; It Lacks Planning Discipline · IPv6 不缺地址，缺的是"规划纪律"

Enterprises usually receive a **/48 or /56** from their carrier (a /56 or /60 for residential). One /48 = 65,536 /64s, which looks inexhaustible, but the reality is:

<div class="zh" markdown="1">

企业通常从运营商拿到 **/48 或 /56**（家宽 /56 或 /60）。一个 /48 = 65,536 个 /64，看起来用不完，但现实是：

</div>

- **No address plan = no aggregation in ten years' time**, and routing-table growth is irreversible
- **Changing a prefix hurts more than changing IPv4**: terminals, ACLs, firewalls, DNS, monitoring and certificate SANs are all bound to the address
- **Renumbering is theoretically feasible (RA lifetimes) and practically avoided by everyone**

<div class="zh" markdown="1">

- **没有地址规划 = 十年后无法汇总**，路由表膨胀不可逆
- **改前缀比改 IPv4 更痛**：终端、ACL、防火墙、DNS、监控、证书 SAN 全部绑着地址
- **重新编址理论上可行（RA 生命周期），工程上几乎没人敢做**

</div>

**So the first deliverable of IPv6 design is not a configuration but an address allocation table plus one inviolable rule (always /64).**

<div class="zh" markdown="1">

**所以 IPv6 设计的第一交付物不是配置，是一张地址分配表 + 一条不可破坏的规则（永远 /64）。**

</div>

### 3. QoS Does Not Add Bandwidth — It Decides Who Suffers First When Congested · QoS 不增加带宽，它只决定"拥塞时谁先受苦"

| Link state | What QoS does |
|---------|-----------|
| **Idle** | **Nothing at all** (no queue builds up, the scheduler has nothing to do) |
| **Light congestion (<70%)** | Very little (LLQ shaves a little jitter) |
| **Moderate congestion (70%–100%)** | Clearly visible (decides who is delayed and who is dropped) |
| **Sustained overload (>100%)** | **Limited effect** (every queue overflows; only capacity or policing helps) |

<div class="zh" markdown="1">

| 链路状态 | QoS 的作用 |
|---------|-----------|
| **空闲** | **完全没有作用**（队列不排队，调度器无事可做） |
| **轻度拥塞（<70%）** | 作用很小（LLQ 让抖动略降） |
| **中度拥塞（70%–100%）** | 作用明显（决定谁被延迟、谁被丢） |
| **持续过载（>100%）** | **作用有限**（什么队列都会溢出，只能扩容或限速） |

</div>

> 💡 **The test question**: "This link runs at 40% utilisation — will QoS improve voice?" Answer: "Hardly at all. But twice a month it hits 95%, and QoS decides whether voice breaks during those two periods." **QoS buys insurance, not bandwidth.**

<div class="zh" markdown="1">

> 💡 **判断句**："这条链路平时利用率 40%，上 QoS 能改善语音吗？" 答："几乎不能。但它每月有两次冲到 95%，QoS 决定那两次语音会不会断。" **QoS 是买保险，不是买带宽。**

</div>

### 4. The Value of QoS Lies at the Trust Boundary, Not in Queueing Technique · QoS 的价值在信任边界，不在队列技术

The most common misplacement in reviews: two weeks spent arguing LLQ versus CBWFQ, while nobody answers **"who is allowed to set DSCP"**.

<div class="zh" markdown="1">

评审时最常见的错位：花两周争论 LLQ 与 CBWFQ 的差别，却没人回答"**谁有权标记 DSCP**"。

</div>

- A terminal can mark its packets EF (a registry edit is enough)
- If an access port is configured to `trust dscp`, you have handed **queue-scheduling authority to the user**
- The right approach: **do not trust terminals at the access layer; re-mark or police at the trust boundary**

<div class="zh" markdown="1">

- 终端可以把包标成 EF（改注册表即可）
- 接入端口若 `trust dscp`，等于把**队列调度权交给用户**
- 正确做法：**接入层不信任终端，在信任边界重标记或限速**

</div>

| Boundary location | Trust policy | Rationale |
|---------|---------|------|
| IP phone port | trust DSCP (PC traffic is re-marked to 0 by the phone) | the phone is a controlled device |
| Ordinary PC port | **no trust**; mark everything BE or classify with NBAR | users are untrusted |
| Wireless (WMM) | upstream trusts the UP→DSCP mapping, but rate limiting is required | the terminal can forge the UP |
| Aggregation/core | trust (already cleaned at the boundary) | internal devices are trusted |
| WAN egress | **re-mark** (align with the contract and carrier capability) | semantics differ across domains |
| Across a tunnel | map the inner header to the outer one / duplicate | only the outer header is visible to the transit network |

<div class="zh" markdown="1">

| 边界位置 | 信任策略 | 理由 |
|---------|---------|------|
| IP 话机端口 | trust DSCP（PC 流量被话机重标为 0） | 话机是受控设备 |
| 普通 PC 端口 | **不信任**，一律标 BE 或用 NBAR 分类 | 用户不可信 |
| 无线（WMM） | 上行信任 UP→DSCP 映射，但需限速 | 终端可伪造 UP |
| 汇聚/核心 | 信任（已被边界清洗） | 内部设备可信 |
| WAN 出口 | **重标记**（对齐合同与运营商能力） | 跨域语义不一致 |
| 跨隧道 | 内层映射到外层 / 复制 | 外层才能被中间网络识别 |

</div>

### 5. More Than Eleven Classes Means No QoS at All · 分类超过 11 个，等于没做 QoS

Every additional class costs another slice of "marking consistency, queue configuration, monitoring, troubleshooting, documentation".

<div class="zh" markdown="1">

每多一个类，就多一份"标记一致性、队列配置、监控、排障、文档"的成本。

</div>

| Number of classes | Real-world consequence |
|------|---------|
| 4–6 classes | maintainable, suitable for a mid-sized enterprise |
| **8–11 classes** | **the industry's recommended range** (Cisco's eight-class / eleven-class models) |
| 12–20 classes | needs strong automation, otherwise it drifts quickly |
| >20 classes | effectively unverifiable — "configured, but nobody knows whether it is right" |

<div class="zh" markdown="1">

| 类数 | 现实后果 |
|------|---------|
| 4–6 类 | 可维护，适合中型企业 |
| **8–11 类** | **业界推荐区间**（Cisco 八类/十一类模型） |
| 12–20 类 | 需强自动化支撑，否则很快失真 |
| >20 类 | 事实上无法验证，等于"配了但不知道对不对" |

</div>

**The purpose of classification is not precision but a defensible priority order.** Nobody can prove the business difference between AF31 and AF32, but everybody understands "voice > video > signalling > transactional > bulk > scavenger".

<div class="zh" markdown="1">

**分类目的不是"精确"，而是"给出一个可解释的优先级顺序"。** 没人能证明 AF31 与 AF32 的业务差别，但所有人都理解"语音 > 视频 > 信令 > 事务 > 批量 > scavenger"。

</div>

### 6. The Management Plane Is a Second Network — Its Availability Must Be Designed Separately · 管理平面是"第二张网"，它自己的可用性要单独设计

A beginner treats management as "a feature the device ships with"; an expert treats it as **a network that has to be designed**.

<div class="zh" markdown="1">

新手把管理当"设备自带的功能"，专家把它当**一张必须设计的网络**。

</div>

| Question | The answer without design | The answer with design |
|------|--------------|------------|
| Where does management traffic go | over the service ports (in-band) | **a dedicated management VRF plus dedicated switches (OOB)** |
| How do you log in when the service network is down | you cannot (exactly when you need it most) | **out-of-band + LTE backup + console server** |
| Who can log in | everyone has enable | **TACACS+ role-based authorisation + jump host + four-eyes review** |
| How are configurations backed up | manually | daily automatic plus version archiving |
| Is the management bandwidth sufficient | never calculated | **calculated from mirroring/logging/backup peaks** |

<div class="zh" markdown="1">

| 问题 | 没设计过的答案 | 设计过的答案 |
|------|--------------|------------|
| 管理流量走哪里 | 走业务口（带内） | **独立管理 VRF + 独立管理交换机（OOB）** |
| 业务网断了怎么登录 | 登不上（恰是最需要的时候） | **带外 + LTE 备份 + Console 服务器** |
| 谁能登录 | 所有人都有 enable | **TACACS+ 分级授权 + 跳板机 + 双人复核** |
| 配置怎么备份 | 手动 | 每日自动 + 版本归档 |
| 管理带宽够吗 | 没算过 | **按镜像/日志/备份峰值算过** |

</div>

> ⚠️ **The in-band paradox**: management traffic shares the same network as service traffic. **During a failure, management traffic is affected first — and that is exactly when you need the management channel.**

<div class="zh" markdown="1">

> ⚠️ **带内管理的悖论**：管理流量与业务流量共享同一张网。**故障时管理流量最先受影响，而这时你最需要管理通道。**

</div>

### 7. The Cost of Observability Is "Data Volume × Retention", Not the Tool Price · 可观测性的成本是"数据量 × 保留期"，不是工具价格

```
total cost ≈ licences + collection bandwidth + storage (rate × retention) + people (alert governance + dashboard maintenance)
```

<div class="zh" markdown="1">

```
总成本 ≈ 许可 + 采集带宽 + 存储（速率 × 保留期）+ 人力（告警治理 + 看板维护）
```

</div>

**A real example**: 500 devices, each pushing 1,000 counters every 10 seconds (about 16 B per counter)

<div class="zh" markdown="1">

**算一个真实例子**：500 台设备，每 10 秒推 1,000 个计数器（约 16 B/计数）

</div>

- Per round: 500 × 1,000 × 16 B = **8 MB**
- Rate: 0.8 MB/s ≈ **6.4 Mbps** (excluding protocol overhead)
- Per day ≈ **69 GB**; 90 days of retention ≈ **6.2 TB**

<div class="zh" markdown="1">

- 单轮：500 × 1,000 × 16 B = **8 MB**
- 速率：0.8 MB/s ≈ **6.4 Mbps**（不含协议开销）
- 每天 ≈ **69 GB**；保留 90 天 ≈ **6.2 TB**

</div>

**Conclusion: cost is determined by the sampling interval and the retention policy, not by which platform you bought.** So the design must state explicitly which metrics are at 10-second granularity, which at 5-minute granularity, which are kept only as aggregates, and how many days of raw data are retained.

<div class="zh" markdown="1">

**结论：成本由"采样间隔"和"保留策略"决定，不由"买了哪个平台"决定。** 所以设计必须明确：哪些指标 10 秒级、哪些 5 分钟级、哪些只留聚合、原始数据留几天。

</div>

### 8. More Logs, SNMP and Telemetry Is Not Better: They Compete with the Management-Plane CPU · 日志、SNMP、遥测不是越多越好：它们和管理面 CPU 抢资源

The management-plane CPU of a device is far weaker than its forwarding plane, and all of the following hammer it:

<div class="zh" markdown="1">

设备管理面 CPU 远弱于转发面，以下操作全在打它：

</div>

| Operation | Overhead | The scale-risk action |
|------|------|------------|
| Full SNMP table walk (ifTable/ifXTable) | high | walking 500 devices every 5 minutes |
| Syslog (especially debug) | medium-high | port flapping, thousands of messages per second |
| NetFlow export | medium | unsampled at high pps |
| High-rate telemetry push | medium | 1-second interval × tens of thousands of counters |
| Configuration backup (scp of large configs) | medium | the whole network at the same time |
| TACACS+ authentication | low | blocking timeouts when the server is unreachable |

<div class="zh" markdown="1">

| 操作 | 开销 | 规模风险动作 |
|------|------|------------|
| SNMP 全表 walk（ifTable/ifXTable） | 高 | 每 5 分钟 walk 500 台 |
| Syslog（尤其 debug） | 中高 | 端口 flapping 千条/秒 |
| NetFlow 导出 | 中 | 未采样 + 高 pps |
| 遥测高频推送 | 中 | 1 秒级 × 数万计数器 |
| 配置备份（scp 大配置） | 中 | 全网同时并发 |
| TACACS+ 认证 | 低 | 服务器不可达时超时阻塞 |

</div>

> 💡 **Design action**: the management plane must be **rate-limited and prioritised** (SNMP queue / logging rate-limit / CoPP protection for the management plane / tiered telemetry sampling), and it must be validated against the **incident profile** (a log storm), not the steady-state profile.

<div class="zh" markdown="1">

> 💡 **设计动作**：管理面必须做**限速与优先级**（SNMP queue / logging rate-limit / CoPP 保护管理面 / 遥测采样分级），并按"事故工况"（日志风暴）验证，而不是按"日常工况"验证。

</div>

### 9. An Alert Is Worth Exactly "Someone Will Act on It" — Everything Else Is Noise · 告警的价值等于"有人会因此采取动作"，其余都是噪音

If **nobody will ever act on an alert**, its only effect is to dull the team's sensitivity to alerts.

<div class="zh" markdown="1">

一条告警如果**没有人会去动它**，它的唯一效果是降低团队对告警的敏感度。

</div>

| Alert type | Should it fire | How it is handled |
|---------|---------|---------|
| Single port down (access side, one user) | ❌ | aggregated into a daily report |
| Single port flapping >10 times / 5 minutes | ✅ | ticket |
| Uplink down | ✅ and escalated | phone call |
| CPU 70% for 10 minutes | ⚠️ depends on role | suppressed, trend only |
| CPU 95% for 2 minutes | ✅ | ticket |
| BGP neighbour down (single neighbour, backup available) | ✅ P3 | ticket |
| BGP neighbour down (all) | ✅ P1 | phone + SMS |
| `%DUAL-5-NBRCHANGE` appearing in logs | ❌ | no alert, store only |
| Disk/flash <10% free | ✅ | ticket (otherwise the next upgrade fails) |

<div class="zh" markdown="1">

| 告警类型 | 是否该发 | 处理方式 |
|---------|---------|---------|
| 单口 down（接入端，1 个用户） | ❌ | 汇总为日报 |
| 单口 flap >10 次/5 分钟 | ✅ | 工单 |
| 上行链路 down | ✅ 且升级 | 电话 |
| CPU 70% 持续 10 分钟 | ⚠️ 看角色 | 抑制，只报趋势 |
| CPU 95% 持续 2 分钟 | ✅ | 工单 |
| BGP 邻居 down（单邻居，有备份） | ✅ P3 | 工单 |
| BGP 邻居 down（全部） | ✅ P1 | 电话 + 短信 |
| 日志里出现 `%DUAL-5-NBRCHANGE` | ❌ | 不告警，只入库 |
| 磁盘/闪存 <10% 空间 | ✅ | 工单（否则下次升级失败） |

</div>

**Three actions of alert governance: deduplication, parent-child suppression (do not report child faults while the parent fault exists), and maintenance-window silencing.** A platform without these three is muted within six months.

<div class="zh" markdown="1">

**告警治理的三个动作：去重、父子抑制（父故障存在时不报子故障）、维护窗口静默。** 这三件事没做的平台，半年后一定被关掉声音。

</div>

### 10. Time Synchronisation Is the Hidden Prerequisite of All Operational Data · 时间同步是所有运维数据的隐藏前提

Without an accurate clock, everything below breaks:

<div class="zh" markdown="1">

没有准确的时钟，下面这些全部失效：

</div>

- **Log correlation** (timestamps out of order across devices → you troubleshoot in the wrong direction)
- **Flow analysis** (bad NetFlow timestamps → cannot be aligned with the moment of failure)
- **Certificate validation** (clock skew beyond the validity tolerance → TLS/802.1X failures)
- **One-time passwords / Kerberos** (skew >5 minutes is rejected outright)
- **SLA and billing statistics**
- **Change audit** (who changed what, and when)

<div class="zh" markdown="1">

- **日志关联**（跨设备时序错乱 → 排障方向反了）
- **流数据分析**（NetFlow 时间戳错 → 无法与故障时刻对齐）
- **证书校验**（时间偏差 > 有效期容差 → TLS/802.1X 失败）
- **一次性口令 / Kerberos**（偏差 >5 分钟直接拒绝）
- **SLA 与计费统计**
- **变更审计**（谁在什么时候改的）

</div>

| Option | Accuracy | Where it fits |
|------|------|------|
| NTP (public sources) | 1–50 ms | general operations |
| NTP (internal stratum 1/2 + authentication) | <1 ms (LAN) | the enterprise standard |
| PTP (IEEE 1588) | <1 µs | financial trading, industrial control, 5G fronthaul |

<div class="zh" markdown="1">

| 方案 | 精度 | 适用 |
|------|------|------|
| NTP（公网源） | 1–50 ms | 通用运维 |
| NTP（内网 stratum 1/2 + 认证） | <1 ms（局域网） | 企业标准 |
| PTP（IEEE 1588） | <1 µs | 金融交易、工业控制、5G 前传 |

</div>

> ⚠️ **Anti-pattern**: pointing every device at the public `pool.ntp.org`. The consequences are (1) the egress is abused for NTP amplification attacks; (2) when the egress fails, every clock drifts; (3) there is no authentication, so the source can be spoofed. **The right approach is an internal stratum-2 hierarchy plus NTP authentication plus device-side ACLs.**

<div class="zh" markdown="1">

> ⚠️ **反模式**：全网设备指向公网 `pool.ntp.org`。后果是（1）出口被 NTP 放大攻击滥用；（2）出口断时全体时钟漂移；（3）没有认证，可被伪造。**正确做法是内部 stratum-2 层级 + NTP 认证 + 设备侧 ACL。**

</div>

### 11. Foundational Services (DHCP/DNS/NTP/AAA) Are Where Single Points of Failure Cluster · 基础服务（DHCP/DNS/NTP/AAA）是单点故障的聚集地

The core network has redundancy, paired nodes, BFD and FRR; the foundational services are often "two virtual machines, one VIP, no rehearsals".

<div class="zh" markdown="1">

核心网络有冗余设计、双机、BFD、FRR；而基础服务往往是"两台虚拟机、一个 VIP、没有演练"。

</div>

| Service | Typical weak point | Blast radius |
|------|-----------|---------|
| **DHCP** | single relay, no option 82, leases too long | every new terminal fails to get an address |
| **DNS** | a single forwarder, TTLs too long to switch | **the whole estate slows down or stops (the most insidious)** |
| **NTP** | public sources only | authentication, logging and audit all go wrong |
| **RADIUS/TACACS+** | a single node, no local fallback | wireless authentication fails *and* devices cannot be logged into |
| **IPAM** | an Excel register with no system integration | address conflicts, and nobody knows who holds what |
| **PKI/certificates** | nobody tracks expiry dates | one morning all 802.1X fails at once |

<div class="zh" markdown="1">

| 服务 | 常见脆弱点 | 故障半径 |
|------|-----------|---------|
| **DHCP** | 单中继、无 option 82、租期过长 | 新增终端全部拿不到地址 |
| **DNS** | 单台转发器、TTL 过长无法切换 | **全域业务变慢/不可用（最隐蔽）** |
| **NTP** | 只配公网源 | 认证/日志/审计集体异常 |
| **RADIUS/TACACS+** | 单台、无本地回退 | 无线认证失败 + 无法登录设备 |
| **IPAM** | Excel 台账、无系统对接 | 地址冲突，且无人知道谁在用 |
| **PKI/证书** | 无人管到期日 | 某天早上所有 802.1X 同时失败 |

</div>

> 💡 **The CCDE view**: ask "where is this design most fragile" and the answer is usually not the core layer but **these services that are assumed to need no design**.

<div class="zh" markdown="1">

> 💡 **CCDE 视角**：问"这套设计最脆弱的地方在哪"，答案往往不是核心层，而是**这些被认为"不用设计"的服务**。

</div>

### 12. "Network Services" Are Shared Dependencies: When They Fail, the Blast Radius Is Global · "网络服务"是共享依赖：服务挂了，故障半径是全域

| Dependency | Who uses it | When it fails |
|------|-------|---------|
| DNS | every terminal, every application, every device (name resolution) | presents as "the network is sometimes slow" when in fact the whole estate is unusable |
| DHCP | every access terminal | new attachments fail, existing terminals drop off when their leases expire |
| NTP | every device plus every authentication system | appears gradually (certificate failures an hour later) |
| AAA | wireless, VPN, device login | cannot authenticate *and* cannot operate (a double hit) |
| Logging/monitoring | the operations team | **you fly blind during the incident** |
| IPAM | change process, automation | address conflicts and automation failures |

<div class="zh" markdown="1">

| 依赖 | 谁在用 | 挂了以后 |
|------|-------|---------|
| DNS | 所有终端、所有应用、所有设备（域名解析） | 表现为"网络时快时慢"，实际是全域不可用 |
| DHCP | 所有接入终端 | 新接入失败，老终端续租到期后掉线 |
| NTP | 所有设备 + 所有认证 | 逐步显现（1 小时后证书失败） |
| AAA | 无线、VPN、设备登录 | 无法认证 + 无法运维（双重打击） |
| 日志/监控 | 运维团队 | **故障时变成"盲飞"** |
| IPAM | 变更流程、自动化 | 地址冲突与自动化失败 |

</div>

**So these services carry stricter design requirements than the core network: they must be highly available, must have local fallback, and must keep working while the "main network" is down.** And they cost very little — this is the class of design improvement with the **best return on investment** in the whole book.

<div class="zh" markdown="1">

**所以这些服务的设计要求，本质上比核心网络更严：必须 HA、必须有本地回退、必须能在"主网故障"时继续工作。** 而它们的成本又极低 —— 这是全书里"投入产出比最高"的一类设计改进。

</div>

---

## The Four-Layer Model of Network Services (First Decide Which Layer You Are Designing) · 网络服务的四层模型（先分清你在设计哪一层）

Many proposals discuss IPv6, QoS and management together, which blurs responsibilities. Use this four-layer framework:

<div class="zh" markdown="1">

很多方案把 IPv6、QoS、管理混在一起讲，导致职责不清。用一个四层框架来看：

</div>

| Layer | What it provides | Composition | Design focus | Symptom when it fails |
|----|---------|------|---------|---------|
| **① Foundational services** | "the network can be used" | DHCP/DHCPv6, DNS, NTP, AAA, PKI, IPAM, image servers | high availability, capacity, security, **does it still work when the network is down** | terminals cannot get addresses / resolve names / authenticate |
| **② Policy control** | "who gets priority when congested, who is allowed" | classification and marking, queueing and scheduling, policing and shaping, ACLs, CoPP | trust boundaries, number of classes, end-to-end consistency, verifiability | voice stutters, critical applications starved by bulk traffic |
| **③ Observability** | "knowing what the network is doing" | SNMP, Syslog, NetFlow/IPFIX, gNMI telemetry, IP SLA, alerting | collection scale, retention, alert governance, clock | flying blind during incidents, longer MTTR |
| **④ Management** | "able to change it, able to change it correctly" | NMS/orchestration, configuration backup, SoT, ITSM, change pipeline | authorisation, audit, availability, automation (see Chapter 12) | slow changes, configuration drift, no audit trail |

<div class="zh" markdown="1">

| 层 | 提供什么 | 组成 | 设计关注 | 失效表现 |
|----|---------|------|---------|---------|
| **① 基础服务层** | "网络能被使用" | DHCP/DHCPv6、DNS、NTP、AAA、PKI、IPAM、镜像服务器 | 高可用、容量、安全、**断网时是否还工作** | 终端拿不到地址/解析不了/认证失败 |
| **② 策略控制层** | "拥塞时谁优先、谁被允许" | 分类标记、排队调度、限速整形、ACL、CoPP | 信任边界、类数、端到端一致性、可验证 | 语音卡顿、关键业务被批量流量挤死 |
| **③ 可观测层** | "知道网络在发生什么" | SNMP、Syslog、NetFlow/IPFIX、gNMI 遥测、IP SLA、告警 | 采集规模、保留期、告警治理、时钟 | 故障时盲飞、MTTR 变长 |
| **④ 管理层** | "改得动、改得对" | NMS/编排、配置备份、SoT、ITSM、变更流水线 | 权限、审计、可用性、自动化（见第 12 章） | 变更慢、配置漂移、无法审计 |

</div>

**Recommended design order (which is also the order of a scenario analysis)**:

<div class="zh" markdown="1">

**设计顺序建议（也是情景分析的顺序）**：

</div>

```
first  ①  without foundational services the network is simply unusable (and the blast radius is the largest)
then   ③  without observability you cannot prove whether ① and ② hold
then   ②  only with a baseline and a means of verification dare you touch QoS (it is the easiest to "break invisibly")
finally ④  management builds on the previous three (automation depends on telemetry and the SoT)
```

<div class="zh" markdown="1">

```
先 ①  没有基础服务，网络根本不可用（且故障半径最大）
再 ③  没有可观测性，你无法证明 ① 和 ② 是否成立
然后 ②  有基线、有验证手段之后，才敢动 QoS（它最容易"改坏且看不出"）
最后 ④  管理层建立在前面三者之上（自动化依赖遥测与 SoT）
```

</div>

> ⚠️ In reality enterprises often build in the order "①→②→④→③", leaving observability last. The result: QoS is changed with nobody verifying it, automation goes live with nobody watching it — **every change is a change in the dark**.

<div class="zh" markdown="1">

> ⚠️ 现实中企业常按"①→②→④→③"建，把可观测性放最后。结果 QoS 改了没人验证、自动化上线没人监控 —— **每次变更都是盲改**。

</div>

---

## Foundation Topics · 基础内容

---

## IPv6 Addressing System and Planning · IPv6 地址体系与规划

### Address Types and Their Uses · 地址类型与用途

| Type | Prefix | Routable | Use and design notes |
|------|------|-------|--------------|
| **Global unicast (GUA)** | 2000::/3 | ✅ globally | operational use; request PI/PA from the carrier |
| **Unique local (ULA)** | FC00::/7 (in practice FD00::/8) | ❌ never leaves the domain | stable internal addresses (independent of the ISP) |
| **Link local (LLA)** | FE80::/10 | ❌ single link | **present on every interface**; used for routing-protocol neighbours and next hops |
| **Multicast** | FF00::/8 | within the domain | replaces broadcast; NDP, routing protocols, streaming |
| **Loopback** | ::1/128 | — | device identity (analogous to a 32-bit loopback) |
| **Unspecified** | ::/128 | — | source address for DAD |
| **IPv4-mapped** | ::FFFF:0:0/96 | — | internal representation inside a dual-stack stack, **never configured** |

<div class="zh" markdown="1">

| 类型 | 前缀 | 可路由 | 用途与设计注意 |
|------|------|-------|--------------|
| **全球单播 (GUA)** | 2000::/3 | ✅ 全球 | 运营使用；从运营商申请 PI/PA |
| **唯一本地 (ULA)** | FC00::/7（实际用 FD00::/8） | ❌ 不出域 | 内部稳定地址（与 ISP 无关） |
| **链路本地 (LLA)** | FE80::/10 | ❌ 单链路 | **每个接口必有**；路由协议邻居、下一跳用它 |
| **组播** | FF00::/8 | 域内 | 替代广播；NDP、路由协议、流媒体 |
| **环回** | ::1/128 | — | 设备标识（类似 32 位 loopback） |
| **未指定** | ::/128 | — | DAD 源地址 |
| **IPv4 映射** | ::FFFF:0:0/96 | — | 双栈栈内部表示，**不用于配置** |

</div>

**Common multicast addresses (worth memorising)**:

<div class="zh" markdown="1">

**常见组播地址（必须记住）**：

</div>

| Address | Purpose |
|------|------|
| FF02::1 | all nodes on the link |
| FF02::2 | all routers on the link |
| FF02::1:2 | all DHCPv6 servers and relays |
| FF02::1:FF00:0/104 | solicited-node multicast (used by DAD/NS) |
| FF02::5 / FF02::6 | OSPFv3 (all SPF / all DR) |
| FF02::A | EIGRPv6 |
| FF02::9 | RIPng |
| FF05::1:3 | all DHCP servers in the site (site scope) |

<div class="zh" markdown="1">

| 地址 | 用途 |
|------|------|
| FF02::1 | 链路上所有节点（all-nodes） |
| FF02::2 | 链路上所有路由器（all-routers） |
| FF02::1:2 | 所有 DHCPv6 服务器与中继 |
| FF02::1:FF00:0/104 | 被请求节点组播（solicited-node，DAD/NS 用） |
| FF02::5 / FF02::6 | OSPFv3 (all SPF / all DR) |
| FF02::A | EIGRPv6 |
| FF02::9 | RIPng |
| FF05::1:3 | 站点内所有 DHCP 服务器（site-scope） |

</div>

### Address Planning: Getting the Bit Boundaries Right Once · 地址规划：把三层位数一次说清

The core of enterprise address planning is cutting the 128 bits into four **semantic** fields:

<div class="zh" markdown="1">

企业地址规划的核心是把 128 位切成四段**语义**：

</div>

```
| 2001:0DB8:SSSS | SS |  SSSS | IIII:IIII:IIII:IIII |
  global routing prefix(48)  site  subnet   interface identifier(64)
                            (8)   (16)
```

<div class="zh" markdown="1">

```
| 2001:0DB8:SSSS | SS |  SSSS | IIII:IIII:IIII:IIII |
  全局路由前缀(48)   站点 子网    接口标识(64)
                   (8)  (16)
```

</div>

| Field | Suggested width | Notes |
|------|---------|------|
| **Global routing prefix** | /48 from the carrier (a /56 also works) | determines what can be aggregated |
| **Site ID** | 8 bits = 256 sites | geography / region / campus |
| **Subnet ID** | 16 bits = 65,536 /64s per site | VLANs, point-to-point links, loopbacks |
| **Interface identifier** | fixed at 64 bits | **must never be subdivided** |

<div class="zh" markdown="1">

| 字段 | 建议宽度 | 说明 |
|------|---------|------|
| **全局路由前缀** | /48 来自运营商（也可 /56） | 决定可汇总范围 |
| **站点 ID** | 8 位 = 256 个站点 | 地理/大区/园区 |
| **子网 ID** | 16 位 = 每个站点 65,536 个 /64 | VLAN、点到点、环回 |
| **接口标识** | 64 位固定 | **不可再切** |

</div>

**Worked example (how large a block this enterprise should request)**:

<div class="zh" markdown="1">

**算例（这家企业该向运营商申请多大）**：

</div>

| Requirement | Calculation | Conclusion |
|------|------|------|
| Number of sites | 300 sites | needs ≥ 300 /48s |
| Round up to a power of two | 512 = 2⁹ | 512 /48s = **one /39** |
| What to actually request | carriers often give /40 or /44 | request a **/40** (one doubling of headroom) |
| Per-site planning | /48 → 16-bit subnet field | 60,000+ /64s is enough for a decade |

<div class="zh" markdown="1">

| 需求 | 计算 | 结论 |
|------|------|------|
| 站点数 | 300 个站点 | 需 ≥ 300 个 /48 |
| 向上取 2 的幂 | 512 = 2⁹ | 512 个 /48 = **一个 /39** |
| 实际申请 | 运营商常给 /40 或 /44 | 申请 **/40**（留一倍增长） |
| 单站点规划 | /48 → 16 位子网 | 6 万个 /64 足够用十年级别 |

</div>

**Suggested subnet allocation table (inside one site)**:

<div class="zh" markdown="1">

**子网分配建议表（单站点内部）**：

</div>

| Purpose | Subnet ID plan | Notes |
|------|------------|------|
| Infrastructure (loopbacks, P2P) | 0000–00FF | easy to aggregate into a single ACL line |
| Building/floor user VLANs | 0100–7FFF | encoded hierarchically: building → floor → VLAN |
| Data centre | 8000–BFFF | separate from the campus for independent policy |
| Wireless/guest/IoT | C000–EFFF | security-domain isolation |
| Reserved/DMZ/labs | F000–FFFF | future expansion |

<div class="zh" markdown="1">

| 用途 | 子网 ID 规划 | 说明 |
|------|------------|------|
| 基础设施（环回、P2P） | 0000–00FF | 便于汇总成一条 ACL |
| 楼宇/楼层用户 VLAN | 0100–7FFF | 按楼 → 层 → VLAN 层次编码 |
| 数据中心 | 8000–BFFF | 与园区分开，便于独立策略 |
| 无线/访客/IoT | C000–EFFF | 安全域隔离 |
| 预留/DMZ/实验 | F000–FFFF | 未来扩展 |

</div>

> 💡 **The value of hierarchy is exactly one thing**: it lets ACLs, firewall policies, route aggregation and monitoring be **expressed by prefix** instead of enumerating 500 individual entries. IPv6 addresses are too long for humans to remember, so **if the plan is wrong there is no "manual safety net" left**.

<div class="zh" markdown="1">

> 💡 **层次化的价值只有一个**：让 ACL、防火墙策略、路由汇总、监控能**按前缀表达**，而不是枚举 500 条明细。IPv6 地址长到人眼无法记，**规划错了就没有"人肉兜底"的可能**。

</div>

### Choosing Prefix Lengths for Special Links · 特殊链路的前缀长度选择

| Link type | Recommended prefix | Rationale |
|---------|---------|------|
| User VLAN / LAN | **/64** | a hard assumption of SLAAC and ND |
| Server segment | **/64** | as above (DHCPv6 is usable, but /64 stays the safe choice) |
| **Point-to-point (router interconnect)** | **/127** (RFC 6164) or /64 | /127 blocks subnet-router anycast tricks and saves space; where old devices or some platforms support only /64, use /64 everywhere |
| **Loopback** | **/128** | a single address, no subnet |
| Host routes / service VIPs | /128 | advertised as anycast or from the loopback |
| Tunnels (GRE/6in4) | /64 (or /127) | depends on platform support |

<div class="zh" markdown="1">

| 链路类型 | 推荐前缀 | 理由 |
|---------|---------|------|
| 用户 VLAN / LAN | **/64** | SLAAC、ND 的硬性假设 |
| 服务器网段 | **/64** | 同上（可用 DHCPv6 但保守用 /64） |
| **点到点（路由互联）** | **/127**（RFC 6164）或 /64 | /127 防子网路由攻击、省地址；老设备/部分平台只支持 /64 时统一用 /64 |
| **环回** | **/128** | 单地址，无子网 |
| 主机路由/服务 VIP | /128 | anycast 或 LO 上宣告 |
| 隧道（GRE/6in4） | /64（或 /127） | 视平台支持 |

</div>

> ⚠️ **Do not use /126**: the early "save addresses" practice saved nothing (addresses are plentiful) and created an inconsistency in which platforms are supported. **Either /64 or /127.**

<div class="zh" markdown="1">

> ⚠️ **不要用 /126**：早期"省地址"的做法既没省（地址多得是），又制造了"支持的平台不一致"的问题。**要么 /64，要么 /127。**

</div>

### Choosing How Addresses Are Acquired · 地址获取方式的选择

| Method | Who generates the IID | Server needed | Where it fits |
|------|-----------|--------------|------|
| **SLAAC** | the terminal itself (EUI-64 / stable privacy / random) | ❌ (only RA) | general terminals, IoT |
| **SLAAC + RDNSS** | the terminal | ❌ (DNS also rides in the RA) | a clean option without DHCPv6 (RFC 8106) |
| **Stateful DHCPv6** | the server | ✅ | address auditing, per-user authorisation |
| **Stateless DHCPv6 (M=0, O=1)** | the terminal (SLAAC) | ✅ (DNS/domain only) | you want DNS under control but addresses via SLAAC |
| **Static/manual** | the engineer | ❌ | servers, network devices, VIPs |

<div class="zh" markdown="1">

| 方式 | 谁生成 IID | 是否需要服务器 | 适用 |
|------|-----------|--------------|------|
| **SLAAC** | 终端自己（EUI-64 / 稳定隐私 / 随机） | ❌（只需 RA） | 通用终端、IoT |
| **SLAAC + RDNSS** | 终端 | ❌（DNS 也在 RA 里） | 无 DHCPv6 的干净方案（RFC 8106） |
| **DHCPv6 有状态** | 服务器 | ✅ | 需要地址审计、按用户授权 |
| **DHCPv6 无状态（M=0,O=1）** | 终端（SLAAC） | ✅（只发 DNS/域） | 想审计 DNS 但用 SLAAC 地址 |
| **静态/手动** | 人工 | ❌ | 服务器、网络设备、VIP |

</div>

**The two key flags in the RA**:

<div class="zh" markdown="1">

**RA 里的两个关键标志位**：

</div>

| Flag | Meaning | Terminal behaviour |
|------|------|---------|
| **M (Managed)** | "a DHCPv6 server exists" | obtain the address via DHCPv6 |
| **O (Other)** | "other configuration is in DHCPv6" | address via SLAAC, DNS/domain via DHCPv6 |

<div class="zh" markdown="1">

| 标志 | 含义 | 终端行为 |
|------|------|---------|
| **M（Managed）** | "有 DHCPv6 服务器" | 用 DHCPv6 取地址 |
| **O（Other）** | "其他配置在 DHCPv6" | 地址用 SLAAC，DNS/域用 DHCPv6 |

</div>

> 💡 **The practical test**: Windows by default does "SLAAC plus a DHCPv6 attempt when an RA is present"; Android **does not support stateful DHCPv6** (it only does SLAAC). **If the enterprise has Android devices (it almost certainly does), the design must keep SLAAC — this is the number-one reason IPv6-only designs get rejected.**

<div class="zh" markdown="1">

> 💡 **实操判断**：Windows 默认"有 RA 就 SLAAC + 尝试 DHCPv6"；Android **不支持 DHCPv6 有状态**（只认 SLAAC）。**如果企业里有 Android 设备（大概率有），方案必须保留 SLAAC —— 这是很多 IPv6-only 设计被推翻的第一原因。**

</div>

### The Three Ways to Generate an Interface Identifier (IID) · 接口标识（IID）的三种生成方式

| Method | Example | Privacy | Stability | Design advice |
|------|------|------|-------|---------|
| **EUI-64** | MAC → insert FFFE and flip the U/L bit | ❌ exposes vendor/OUI | ✅ | **not recommended** (fingerprintable) |
| **Stable privacy (RFC 7217)** | hash of prefix + secret + counter | ✅ | ✅ (stable under the same prefix) | **recommended default** |
| **Temporary addresses (RFC 8981, formerly 4941)** | periodically randomised | ✅ | ❌ | on by default in clients, used for outbound access |
| **DHCPv6 assignment** | decided by the server | ✅ | ✅ | when auditing is required |

<div class="zh" markdown="1">

| 方式 | 例子 | 隐私 | 稳定性 | 设计建议 |
|------|------|------|-------|---------|
| **EUI-64** | MAC → 插入 FFFE 并翻转 U/L 位 | ❌ 暴露厂商/OUI | ✅ | **不推荐**（可被指纹追踪） |
| **稳定隐私（RFC 7217）** | 前缀 + 密钥 + 计数器哈希 | ✅ | ✅（同前缀下稳定） | **推荐默认** |
| **临时地址（RFC 8981，原 4941）** | 定期随机更换 | ✅ | ❌ | 客户端默认开启，出站访问用 |
| **DHCPv6 分配** | 服务器决定 | ✅ | ✅ | 需要审计时 |

</div>

**The key point**: a terminal usually **holds several addresses at once** (LLA + stable GUA + a number of temporary GUAs). Therefore:

<div class="zh" markdown="1">

**关键点**：终端通常**同时持有多个地址**（LLA + 稳定 GUA + 若干临时 GUA）。所以：

</div>

- **Never write "the terminal's address" in an ACL** (it changes); write by **prefix/subnet**
- **The source address in a log may be a temporary address**, so tracking has to combine DHCPv6/ND logs or the prefix
- **Never bind DNS records to terminal addresses**

<div class="zh" markdown="1">

- **ACL 不要写"终端地址"**（会变），要按**前缀/子网**写
- **日志里的源地址可能是临时地址**，追踪要结合 DHCPv6/ND 日志或前缀
- **DNS 记录不要绑终端地址**

</div>

### NDP (Neighbour Discovery): Flow and the Five Messages · NDP（邻居发现）流程与五个消息

| Message | ICMPv6 type | Function | IPv4 analogy |
|------|------------|------|----------|
| **RS** (Router Solicitation) | 133 | host asks for an immediate RA | the "hurry up" of DHCP Discover |
| **RA** (Router Advertisement) | 134 | advertises prefixes, default gateway, flags, MTU | no equivalent (IPv4 relies on DHCP) |
| **NS** (Neighbor Solicitation) | 135 | address resolution / DAD probing | ARP Request |
| **NA** (Neighbor Advertisement) | 136 | answers an NS | ARP Reply |
| **Redirect** | 137 | tells the host a better next hop | ICMP Redirect |

<div class="zh" markdown="1">

| 消息 | ICMPv6 类型 | 作用 | 类比 IPv4 |
|------|------------|------|----------|
| **RS**（Router Solicitation） | 133 | 主机请求立即发 RA | DHCP Discover 的"催促" |
| **RA**（Router Advertisement） | 134 | 通告前缀、默认网关、标志位、MTU | 无对应（IPv4 靠 DHCP） |
| **NS**（Neighbor Solicitation） | 135 | 地址解析 / DAD 探测 | ARP Request |
| **NA**（Neighbor Advertisement） | 136 | 应答 NS | ARP Reply |
| **Redirect** | 137 | 告诉主机更优下一跳 | ICMP Redirect |

</div>

**The full address-acquisition sequence (SLAAC)**:

<div class="zh" markdown="1">

**完整地址获取时序（SLAAC）**：

</div>

```
1. The host generates an LLA (FE80::/64, EUI-64 or random)
2. DAD: sends an NS to FF02::1:FFxx:xxxx (source ::), waits 1 s with no NA → LLA usable
3. The host sends an RS (source LLA, destination FF02::2)
4. The router returns an RA (prefix, prefix lifetime, default-route lifetime, M/O flags, MTU, RDNSS)
5. The host combines the RA prefix with an IID to form a GUA
6. DAD is performed again for the GUA
7. (If O/M) DHCPv6 Solicit → Advertise → Request → Reply to obtain DNS/domain
8. Done; the default route points at the RA source (LLA)
```

<div class="zh" markdown="1">

```
1. 主机生成 LLA（FE80::/64，EUI-64 或随机）
2. DAD：向 FF02::1:FFxx:xxxx 发 NS（源为 ::），等 1 秒无 NA → LLA 可用
3. 主机发 RS（源 LLA，目的 FF02::2）
4. 路由器回 RA（含前缀、前缀生存期、默认路由生存期、M/O 标志、MTU、RDNSS）
5. 主机用 RA 前缀 + IID 生成 GUA
6. 对 GUA 再做一次 DAD
7. （若 O/M）发 DHCPv6 Solicit → Advertise → Request → Reply 取 DNS/域
8. 完成；默认路由指向 RA 源（LLA）
```

</div>

**RA parameter defaults and what they mean for design**:

<div class="zh" markdown="1">

**RA 参数的默认值与设计含义**：

</div>

| Parameter | Default | Design implication |
|------|------|---------|
| Max RA interval | 600 s | a new terminal may wait up to 200 s before it sees an RA; **this is exactly why users complain "I plugged in and there is no network"** |
| Router Lifetime | 1800 s (3× Max) | how long terminals keep the default route after RAs stop |
| Prefix Valid Lifetime | 2592000 s (30 days) | when the prefix expires (used for renumbering) |
| Prefix Preferred Lifetime | 604800 s (7 days) | when it stops being used for new connections |
| Cur Hop Limit | 64 | hop limit |
| MTU in the RA | often left empty | when absent, terminals assume 1280 (**a hidden risk, see the next section**) |
| RDNSS lifetime | ≥ 2× RA recommended | avoids DNS timeout flapping |

<div class="zh" markdown="1">

| 参数 | 默认 | 设计含义 |
|------|------|---------|
| Max RA interval | 600 s | 新终端最快 200 s 才收到 RA；**终端抱怨"插上没网"就是这个** |
| Router Lifetime | 1800 s（3×Max） | RA 停止后终端还能用默认路由多久 |
| Prefix Valid Lifetime | 2592000 s（30 天） | 前缀失效时间（renumbering 用） |
| Prefix Preferred Lifetime | 604800 s（7 天） | 停止用于新连接的时间 |
| Cur Hop Limit | 64 | 跳数上限 |
| RA 里的 MTU | 常不填 | 不填时终端默认 1280（**隐患，见下节**） |
| RDNSS lifetime | 建议 ≥ 2×RA | 避免 DNS 超时抖动 |

</div>

> ⚠️ **Two high-frequency field problems**: (1) **"after plugging in the cable it takes 30 seconds to get on the network"** — the RA interval is too long; fix it with `ipv6 nd ra interval msec 30000`; (2) **"IPv6 pings but web pages do not open"** — the RA carries no RDNSS and DHCPv6 is unreachable, so the terminal has no DNS.

<div class="zh" markdown="1">

> ⚠️ **两个高频现场问题**：（1）**"插上网线要等 30 秒才有网"** —— RA 间隔太长，解决：`ipv6 nd ra interval msec 30000`；（2）**"IPv6 能 ping 通但网页打不开"** —— RA 没带 RDNSS 且 DHCPv6 不可达，终端没有 DNS。

</div>

### MTU and PMTUD: The Number-One IPv6 Troubleshooting Killer · MTU 与 PMTUD：IPv6 排障第一杀手

| Fact | Consequence |
|------|------|
| IPv6 **routers do not fragment** (only the source may fragment) | a smaller MTU mid-path must be signalled to the source by ICMPv6 Type 2 |
| ICMPv6 Type 2 (Packet Too Big) blocked by a firewall | **black hole**: small packets pass, large packets do not (ping works, SSH/TLS hangs) |
| The IPv6 minimum MTU is 1280 | if tunnels are not adjusted, you will hit this |
| Tunnel routers do send Type 2 automatically | but many security policies "block ICMP" |

<div class="zh" markdown="1">

| 事实 | 后果 |
|------|------|
| IPv6 **路由器不分片**（只有源端可分段） | 中间链路 MTU 小 → 必须靠 ICMPv6 Type 2 通知源端 |
| ICMPv6 Type 2（Packet Too Big）被防火墙拦 | **黑洞**：小包通、大包不通（ping 通、SSH/TLS 卡死） |
| IPv6 最小 MTU = 1280 | 隧道里若不调整，一定踩 |
| 隧道路由器会自动回 Type 2 | 但很多安全策略"禁 ICMP" |

</div>

**Design rules (put them in the deliverables)**:

<div class="zh" markdown="1">

**设计规则（写进交付物）**：

</div>

1. **ICMPv6 Types 1/2/3/4 and 133–137 must be permitted** (rate limiting is fine, blocking is not), Type 2 above all
2. Use a uniform MTU of 1500 across the network; in tunnel scenarios the inner MTU is 1500 and the outer is reduced by encapsulation (GRE 24 B, 6in4 20 B, IPsec 50–73 B depending on mode)
3. Any "temporary firefighting" MTU of 1400 on terminals must document the reason and the condition for reverting it
4. **Acceptance method**: verify hop by hop with `ping -6 -s 1452 -M do` (`-l` on Windows) rather than a single ping
5. Apply **TCP MSS clamping** on server segments (the MSS option in the IPv6 SYN can be clamped just the same)

<div class="zh" markdown="1">

1. **ICMPv6 Type 1/2/3/4 与 133–137 必须放行**（可限速，不可阻断），Type 2 尤其
2. 全网 MTU 统一 1500；隧道场景内层 MTU 1500、外层按封装减（GRE 24 B、6in4 20 B、IPsec 视模式 50–73 B）
3. 终端侧 MTU 1400 的"临时救火"要写清原因与撤销条件
4. **验收方法**：`ping -6 -s 1452 -M do`（Windows `-l`）逐跳验证，而不是只 ping 一次
5. 服务器网段做 **TCP MSS clamping**（IPv6 SYN 的 MSS option 同样可夹）

</div>

> 🔥 **Troubleshooting mantra**: **with IPv6, when "ping works but the application does not", check MTU and ICMPv6 Type 2 first, then DNS.**

<div class="zh" markdown="1">

> 🔥 **排障口诀**：**IPv6 下"能 ping 通但应用不通"，先查 MTU 与 ICMPv6 Type 2，再查 DNS。**

</div>

### IPv6 First-Hop Security (NDP Has No Authentication, So the Network Side Must Provide It) · IPv6 首跳安全（NDP 无认证，必须靠网络侧）

NDP has none of the "natural trust" of IPv4 ARP, and SEND is not widely deployed, so all protection lives on the switches and routers:

<div class="zh" markdown="1">

NDP 没有 IPv4 ARP 那样的"天然信任"，也没有广泛部署的 SEND，所以防护全在交换机/路由器上：

</div>

| Technique | What it prevents | Where it is deployed |
|------|-------|---------|
| **RA Guard** | rogue RAs (forged default gateway/DNS) | access ports (except uplinks towards routers) |
| **ND Inspection** | forged NAs (address hijacking), NA floods exhausting the ND table | access ports |
| **DHCPv6 Guard** | rogue DHCPv6 servers | access ports |
| **IPv6 Source Guard / SAVI** | source-address spoofing (a simplified RFC 5213) | access ports |
| **Destination Guard** | NS floods aimed at non-existent targets exhausting the ND cache | Layer 3 gateways |
| **Neighbour-cache limits + rate limiting** | ND cache exhaustion (the equivalent of a full ARP table) | gateways |
| **CoPP / control-plane policing** | RS/NS floods hitting the management plane | network-wide |

<div class="zh" markdown="1">

| 技术 | 防什么 | 部署位置 |
|------|-------|---------|
| **RA Guard** | 非法 RA（伪造默认网关/DNS） | 接入端口（除连路由器的上行口） |
| **ND Inspection** | 伪造 NA（地址劫持）、NA 泛洪耗尽 ND 表 | 接入端口 |
| **DHCPv6 Guard** | 非法 DHCPv6 服务器 | 接入端口 |
| **IPv6 Source Guard / SAVI** | 源地址伪造（RFC 5213 简化版） | 接入端口 |
| **Destination Guard** | 针对不存在目标的 NS 泛洪耗尽 ND 缓存 | 三层网关 |
| **邻居缓存限制 + 速率限制** | ND 缓存耗尽（相当于 ARP 表打满） | 网关 |
| **CoPP / 控制面限速** | RS/NS 泛洪打管理面 | 全网 |

</div>

> ⚠️ **The wrong order takes the network down**: enabling RA Guard before marking the uplink as `trusted` kills the default gateway for an entire floor in one go. **Rollout order: capture traffic to see where legitimate RAs come from → configure the trusted uplink → then enable it port by port.**

<div class="zh" markdown="1">

> ⚠️ **顺序错误会断网**：先开 RA Guard 再确认上行口设为 `trusted`，一次就把整个楼层的默认网关断掉。**上线顺序：先抓包看现场有没有合法 RA 源 → 配 trusted 上行 → 再逐端口开。**

</div>

### Coexistence and Migration Strategies for IPv6 and IPv4 · IPv6 与 IPv4 共存的迁移策略

| Strategy | Principle | Advantages | Cost | Where it fits |
|------|------|------|------|------|
| **Dual stack** | both protocols run side by side | cleanest, no translation | double the addresses/policy/troubleshooting, IPv4 space still has to be managed | **first choice** (dual stack whenever possible) |
| **NAT64 + DNS64** | v6-only clients reach v4 services (DNS synthesises AAAA) | clients need no v4 | stateful, needs DNS cooperation, breaks end-to-end, application incompatibilities (literal IPs, IPsec) | mobile / public-cloud v6-only |
| **464XLAT (CLAT+PLAT)** | a CLAT on the terminal provides stateless translation | works with applications that use IPv4 literal addresses | terminal support required (Android has it, Windows needs software) | mobile operators |
| **DS-Lite / MAP-E / MAP-T** | v4 over v6 tunnels plus centralised CGN | saves v4 for the operator | tunnel MTU, CGN logging compliance | ISPs |
| **6rd / 6in4 / ISATAP / Teredo** | static/automatic tunnels | usable for transition | **deprecated**, MTU traps, poor security | not recommended for new deployments |

<div class="zh" markdown="1">

| 策略 | 原理 | 优点 | 代价 | 适用 |
|------|------|------|------|------|
| **双栈（Dual Stack）** | 两套协议同时跑 | 最干净、无转换 | 双份地址/策略/排障成本，IPv4 地址仍需管理 | **首选**（能双栈就双栈） |
| **NAT64 + DNS64** | 纯 v6 客户端访问 v4 服务（DNS 回 AAAA 合成） | 客户端免 v4 | 有状态、需 DNS 配合、破坏端到端、应用不兼容（字面 IP、IPsec） | 移动/公有云 v6-only |
| **464XLAT（CLAT+PLAT）** | 终端侧 CLAT 做无状态翻译 | 兼容 IPv4 字面 IP 应用 | 终端支持要求（Android 有、Windows 需软） | 移动运营商 |
| **DS-Lite / MAP-E / MAP-T** | v4 over v6 隧道 + 集中式 CGN | 运营商节省 v4 | 隧道 MTU、CGN 日志合规 | ISP |
| **6rd / 6in4 / ISATAP / Teredo** | 静态/自动隧道 | 过渡可用 | **已被弃用**，MTU 坑、安全差 | 不推荐新建 |

</div>

**The design decision sequence**:

<div class="zh" markdown="1">

**设计判断顺序**：

</div>

```
if dual stack is possible → dual stack (and define an explicit "IPv6-first or IPv4-first" policy)
if v6-only is mandatory → NAT64/DNS64 (first review the application inventory: hard-coded IPv4 literals? IPsec?)
if only the terminal side lacks v4 → 464XLAT
```

<div class="zh" markdown="1">

```
能用双栈 → 双栈（并且要有"IPv6 优先还是 IPv4 优先"的明确策略）
必须 v6-only → NAT64/DNS64（应用清单先过一遍：有没有写死 IPv4 字面地址？有没有 IPsec？）
只有终端侧缺 v4 → 464XLAT
```

</div>

> 💡 **The hidden problem with dual stack: asymmetry**. Terminals prefer IPv6 by default (RFC 6724), so if the IPv6 path is poor (tunnels, an out-of-region egress), applications "get slower without fully breaking". **Dual stack must deliver equal quality on both paths — otherwise it is better to withdraw the AAAA record first.**

<div class="zh" markdown="1">

> 💡 **双栈的隐藏问题：不对称**。终端默认偏好 IPv6（RFC 6724），如果 IPv6 路径质量差（隧道、跨区出口），业务会"变慢但不完全断"。**双栈必须做到两条路径质量对等，否则宁可先关掉 AAAA。**

</div>

### IPv6 Routing Protocol Essentials · IPv6 路由协议要点

| Protocol | Key difference | Design notes |
|------|---------|---------|
| **OSPFv3** | topology and addressing are **separated**; neighbours use LLAs, configuration is per interface; authentication relies on IPsec (or AH in v3) | one process can serve multiple AFs; virtual links still use the Router-ID |
| **EIGRPv6** | neighbours also use LLAs; requires `ipv6 unicast-routing` plus `ipv6 eigrp` under the interface | named mode matches v4, so management habits carry over |
| **IS-IS** | multi-AF by design (TLVs), IPv6 onboarding is simple | first choice for large networks/carriers, but a high operations bar |
| **MP-BGP** | `address-family ipv6 unicast`; the next hop may be an LLA (RFC 2545) or an IPv4-mapped address (RFC 5549) | **RFC 5549 allows an IPv4 next hop for IPv6 prefixes**, which lets a v4-only core carry v6 |
| **Static/default routes** | the default route is usually `::/0` pointing at the upstream LLA or GUA | consider precedence when it coexists with RAs |

<div class="zh" markdown="1">

| 协议 | 关键差异 | 设计注意 |
|------|---------|---------|
| **OSPFv3** | 拓扑与地址**分离**；邻居用 LLA，配置在接口；认证靠 IPsec（或v3 的 AH） | 同一个进程可跑多个 AF；虚链路仍用 Router-ID |
| **EIGRPv6** | 邻居也用 LLA；需 `ipv6 unicast-routing` + 接口下 `ipv6 eigrp` | 命名模式与 v4 一致，管理习惯延续 |
| **IS-IS** | 天然多 AF（TLV），IPv6 接入简单 | 大网/运营商首选，但运维门槛高 |
| **MP-BGP** | `address-family ipv6 unicast`；下一跳可用 LLA（RFC 2545）或 IPv4 映射（RFC 5549） | **RFC 5549 允许 v6 前缀的下一跳是 v4 地址**，便于 v4-only 核心承载 v6 |
| **静态/默认路由** | 默认路由通常 `::/0` 指向上游 LLA 或 GUA | 与 RA 并存时要考虑优先级 |

</div>

**Two consequences of using LLAs as next hops**:

<div class="zh" markdown="1">

**下一跳用 LLA 的两个影响**：

</div>

1. **Link-local addresses are not routable**, so a next hop of `FE80::x` in the routing table is normal (it must be accompanied by an outgoing interface)
2. **Multi-access links (IXPs, shared VLANs)** require an explicit next hop or `next-hop-self`, otherwise recursion fails

<div class="zh" markdown="1">

1. **链路本地地址不可路由**，所以路由表里看到的下一跳是 `FE80::x`，属正常（需带出接口）
2. **多访问链路（如 IXP、共享 VLAN）**必须显式配置下一跳或使用 `next-hop-self`，否则递归失败

</div>

### Multihoming: PA vs PI, ULA and NPTv6 · 多宿主：PA vs PI，ULA 与 NPTv6

| Option | Address source | Changing carriers | Advantages | Drawbacks |
|------|---------|---------|------|------|
| **PA (Provider Aggregatable)** | a /48 assigned by the carrier | **renumbering is mandatory** | small routing table, carriers are willing to hand them out | painful when changing ISP |
| **PI (Provider Independent)** | requested from the RIR | unchanged | stable | needs BGP multihoming and DFZ acceptance of a /48 (usually a /48 plus multihoming) |
| **ULA + NPTv6** | internal FD00::/8, prefix translation at the boundary | internally unchanged | internal addressing decoupled from the ISP | NPTv6 translates only the prefix (no port translation) and still breaks end-to-end, with checksum implications |

<div class="zh" markdown="1">

| 方案 | 地址来源 | 换运营商 | 优点 | 缺点 |
|------|---------|---------|------|------|
| **PA（Provider Aggregatable）** | 运营商分配 /48 | **必须重新编址** | 路由表小、运营商愿意给 | 换 ISP 痛苦 |
| **PI（Provider Independent）** | RIR 申请 | 不变 | 稳定 | 需要 BGP 多宿主与 /48 的 DFZ 准入（通常要 /48 且多宿主） |
| **ULA + NPTv6** | 内部 FD00::/8，边界做前缀转换 | 内部不变 | 内部地址与 ISP 解耦 | NPTv6 只换前缀（无端口转换），仍破坏端到端、有校验和问题 |

</div>

**Source address selection with dual egress (RFC 6724)**: the terminal scores candidate source addresses by "longest matching prefix → prefer the same address family → prefer an address already in use → the rule table", and **the terminal knows nothing about the router's egress policy**.

<div class="zh" markdown="1">

**双出口的源地址选择（RFC 6724）**：终端选源地址时按"最长匹配前缀 → 优先同一地址族 → 优先已用地址 → 规则表"打分，**终端并不知道路由器的出口策略**。

</div>

> ⚠️ **The classic failure**: dual ISPs, one /48 from A and another from B. The terminal receives A's prefix, but the router sends the traffic out through B → inbound filtering at B (BCP 38/uRPF) drops it → "it works, then it does not". **The fix: inbound policy routing (source-based routing), or a strict rule that each prefix leaves through its own exit.**

<div class="zh" markdown="1">

> ⚠️ **典型故障**：双 ISP，一个 /48 从 A 来、一个 /48 从 B 来。终端从 A 拿到前缀，但路由器把流量从 B 送出 → B 侧入方向过滤（BCP 38/uRPF）丢包 → "时通时不通"。**解决方案：入向策略路由（source-based routing）或严格按"谁的前缀走谁的出口"。**

</div>

### IPv6 Multicast and the Knock-On Effects of "No Broadcast" · IPv6 组播与"没有广播"的连带影响

| Impact | Design action |
|------|---------|
| No broadcast → scanning/worm propagation becomes harder | but **ND/RS flooding** becomes the new DoS surface |
| ARP becomes NS/NA (multicast) | switches need **MLD snooping** (replacing IGMP snooping), otherwise multicast floods the whole VLAN |
| IPv6 streaming uses multicast | needs PIM and MLD; the configuration resembles v4 but the addresses are FF3x::/32 |
| Layer 2 domains still need suppression | use **MLD snooping plus unknown-multicast dropping**, the same thinking as IGMP |

<div class="zh" markdown="1">

| 影响 | 设计动作 |
|------|---------|
| 无广播 → 扫描/蠕虫传播变难 | 但 **ND/RS 泛洪**成为新的 DoS 面 |
| ARP 换成 NS/NA（组播） | 交换机需要 **MLD snooping**（替代 IGMP snooping），否则组播泛洪到全 VLAN |
| IPv6 流媒体用组播 | 需要 PIM 与 MLD，配置与 v4 类似但地址是 FF3x::/32 |
| 二层域仍需抑制 | 用 **MLD snooping + 未知组播丢弃**，思路与 IGMP 一致 |

</div>

### IPv6 Operations Difference Checklist (Ten Items to Train Before Migrating) · IPv6 运维差异清单（迁移前必须培训的 10 条）

1. `ping`/`traceroute` must be told to use v6; many tools default to v4, so **"ping fails" is often the wrong command**
2. **Firewalls/ACLs must permit the key ICMPv6 types** (otherwise ND and PMTUD are both dead)
3. Seeing `FE80::` in logs is normal link-local behaviour, not an error
4. Packet captures must filter on `icmp6`, not `icmp`
5. Addresses are too long → **you must rely on IPAM/automation**; nobody memorises them
6. `show ipv6 neighbors` and the v4 ARP table are two separate tables with independent capacity
7. The absence of NAT → **security policy must be explicit** (you can no longer rely on "the inside is invisible")
8. DAD makes an address "unusable for about 1 second" → matters in fast-failover scenarios
9. Some older devices/versions have incomplete IPv6 ACL/NetFlow support → **build a capability matrix first**
10. Troubleshooting order: **did the address come up → is the gateway reachable → is DNS usable → MTU/PMTUD → application binding (is it listening on v6?)**

<div class="zh" markdown="1">

1. `ping`/`traceroute` 要指定 v6；很多工具默认 v4，**"ping 不通"常是敲错了**
2. **防火墙/ACL 必须放行 ICMPv6 关键类型**（否则 ND 和 PMTUD 全废）
3. 日志里出现 `FE80::` 是正常的链路本地，不代表错误
4. 抓包要过滤 `icmp6`，不是 `icmp`
5. 地址太长 → **必须依赖 IPAM/自动化**，人肉记不住
6. `show ipv6 neighbors` 与 v4 的 ARP 表是两张表，容量独立
7. NAT 缺席 → **安全策略必须显式**（不能再靠"内网不可见"）
8. DAD 会让地址"先不可用约 1 秒" → 快速切换场景需注意
9. 部分老设备/老版本对 IPv6 的 ACL/NetFlow 支持不全 → **先做能力矩阵**
10. 排障顺序：**地址是否拿到 → 网关是否可达 → DNS 是否可用 → MTU/PMTUD → 应用绑定（v6 监听？）**

</div>

> 💡 Item 10 is the most often missed: the application server may **not be listening on v6 at all** (`netstat -an | grep :::`), which presents as "the network is fully working, the service is not".

<div class="zh" markdown="1">

> 💡 第 10 条最容易被忽略：应用服务器可能**根本没监听 v6**（`netstat -an | grep :::`），表现为"网络全通、服务不通"。

</div>

---

## QoS: From Business Requirements to Per-Hop Behaviour · QoS：从业务需求到每跳行为

### The Business Drivers of QoS (Write Down the "Why" First) · QoS 的业务驱动（先写清"为什么"）

| Traffic | Sensitivity to the network | Behaviour without QoS |
|------|--------------|---------------|
| **Voice (VoIP)** | latency <150 ms, jitter <30 ms, loss <1% | clipped syllables, one-way audio, crackle at busy times |
| **Real-time video/conferencing** | latency <150–200 ms, loss <1% | smearing, freezes, mosaic artefacts |
| **Streaming (one-way)** | latency <4–5 s, buffering allowed | slow start, reduced resolution |
| **VDI / interactive** | latency <50 ms (RTT) | typing lag, cursor drag |
| **Transactional (ERP/DB)** | latency-sensitive, low bandwidth | timeouts, retries, batch failures |
| **Bulk (backup/replication)** | bandwidth-sensitive, latency-insensitive | crowds out everything else (**must be rate-limited**) |
| **Scavenger (P2P/updates)** | should be suppressed everywhere | saturates the egress without limit |

<div class="zh" markdown="1">

| 业务 | 对网络的敏感度 | 无 QoS 时的表现 |
|------|--------------|---------------|
| **语音（VoIP）** | 延迟 <150 ms、抖动 <30 ms、丢包 <1% | 忙时断字、单通、杂音 |
| **实时视频/会议** | 延迟 <150–200 ms、丢包 <1% | 花屏、卡顿、马赛克 |
| **流媒体（单向）** | 延迟 <4–5 s、可缓冲 | 起播慢、清晰度下降 |
| **VDI / 交互式** | 延迟 <50 ms（RTT） | 打字延迟、鼠标漂移 |
| **事务型（ERP/DB）** | 延迟敏感、带宽小 | 超时、重试、批量失败 |
| **批量（备份/复制）** | 带宽敏感、延迟不敏感 | 挤占其他业务（**必须被限速**） |
| **scavenger（P2P/更新）** | 都应被压制 | 无节制占满出口 |

</div>

**The key design action: handle "bandwidth-sensitive" and "latency-sensitive" separately.**

<div class="zh" markdown="1">

**关键设计动作：把"带宽敏感"和"延迟敏感"分开处理。**

</div>

- Bandwidth-sensitive → **policing/shaping** (give it a ceiling so it cannot hurt others)
- Latency-sensitive → **a priority queue** (give it low latency and a minimum bandwidth guarantee)
- Neither → the default queue, **using the leftover bandwidth**

<div class="zh" markdown="1">

- 带宽敏感 → **限速/整形**（给它一个上限，避免它伤害别人）
- 延迟敏感 → **优先队列**（给它低延迟与最低带宽保证）
- 两者都不敏感 → 默认队列，**用剩余带宽**

</div>

### DiffServ and IntServ: Why the World Chose DiffServ · DiffServ 与 IntServ：为什么世界选了 DiffServ

| Dimension | IntServ (RSVP) | DiffServ |
|------|----------------|----------|
| Granularity | per-flow | per-class (DSCP) |
| State | every core node keeps per-flow state | the core is stateless and looks only at the DSCP |
| Scalability | ❌ does not scale | ✅ |
| Signalling | RSVP hop by hop | none |
| Real-world use | niche scenarios (small scale, hard guarantees, MPLS TE with RSVP-TE) | **the enterprise/carrier mainstream** |
| Failure mode | reservation fails if signalling breaks | **a wrong marking breaks everything (the trust boundary is the crux)** |

<div class="zh" markdown="1">

| 维度 | IntServ（RSVP） | DiffServ |
|------|----------------|----------|
| 粒度 | 每流（per-flow） | 每类（per-class，DSCP） |
| 状态 | 网络核心保存每流状态 | 核心无状态，只看 DSCP |
| 扩展性 | ❌ 不可扩展 | ✅ |
| 信令 | 需要 RSVP 逐跳 | 不需要 |
| 现实用途 | 特定场景（少量、强保证、MPLS TE 结合 RSVP-TE） | **企业/运营商主流** |
| 失败模式 | 信令中断则预留失效 | **标记错则全盘错（信任边界是命门）** |

</div>

> 💡 **The CCDE judgement**: IntServ's problem is not that the technology is bad but that **it requires the network to remember every single flow** — an impossible cost in a campus with 100,000 concurrent flows. The answer is therefore always DiffServ plus boundary policing plus CAC.

<div class="zh" markdown="1">

> 💡 **CCDE 判断**：IntServ 的问题不是"技术不好"，而是"**它要求网络记住每一条流**"——在 10 万并发的园区里这是不可能的成本。所以答案永远是 DiffServ + 边界限速 + CAC。

</div>

### DSCP Encoding Cheat Sheet · DSCP 编码速查

**6-bit DSCP = class selector (3 bits) + drop precedence (2 bits, AF only) + 1 reserved bit**

<div class="zh" markdown="1">

**6 位 DSCP = 类选择（3 位） + 丢弃优先级（2 位，AF 才有） + 1 位保留**

</div>

| DSCP | Name | Decimal | Binary | Typical traffic |
|------|------|-------|--------|---------|
| 46 | **EF** | 46 | 101110 | voice RTP |
| 44 | VA (Voice Admit) | 44 | 101100 | voice already admitted by CAC |
| 40 | CS5 | 40 | 101000 | broadcast video |
| 34 | AF41 | 34 | 100010 | conferencing video (low drop) |
| 32 | CS4 | 32 | 100000 | real-time interactive (TelePresence) |
| 26 | AF31 | 26 | 011010 | streaming media |
| 24 | CS3 | 24 | 011000 | call signalling |
| 18 | AF21 | 18 | 010010 | transactional data |
| 16 | CS2 | 16 | 010000 | network control (CS6 also works) |
| 10 | AF11 | 10 | 001010 | bulk data |
| 8 | CS1 | 8 | 001000 | scavenger |
| 0 | DF/BE | 0 | 000000 | default |

<div class="zh" markdown="1">

| DSCP | 名称 | 十进制 | 二进制 | 典型业务 |
|------|------|-------|--------|---------|
| 46 | **EF** | 46 | 101110 | 语音 RTP |
| 44 | VA（Voice Admit） | 44 | 101100 | CAC 已准入的语音 |
| 40 | CS5 | 40 | 101000 | 广播视频 |
| 34 | AF41 | 34 | 100010 | 会议视频（低丢弃） |
| 32 | CS4 | 32 | 100000 | 实时交互（TelePresence） |
| 26 | AF31 | 26 | 011010 | 流媒体 |
| 24 | CS3 | 24 | 011000 | 呼叫信令 |
| 18 | AF21 | 18 | 010010 | 事务数据 |
| 16 | CS2 | 16 | 010000 | 网络控制（也可用 CS6） |
| 10 | AF11 | 10 | 001010 | 批量数据 |
| 8 | CS1 | 8 | 001000 | Scavenger |
| 0 | DF/BE | 0 | 000000 | 默认 |

</div>

**The AFxy rule**: `DSCP = 8x + 2y` (x = 1..4 for the class, y = 1..3 for drop precedence)

<div class="zh" markdown="1">

**AFxy 规律**：`DSCP = 8x + 2y`（x=1..4 类，y=1..3 丢弃优先级）

</div>

- AF11=10, AF12=12, AF13=14; AF21=18, AF22=20, AF23=22; AF31=26 … AF43=38
- **Higher drop precedence means WRED drops it earlier** (within a class, the "less important" packets go first)

<div class="zh" markdown="1">

- AF11=10, AF12=12, AF13=14；AF21=18, AF22=20, AF23=22；AF31=26…AF43=38
- **丢弃优先级越高，WRED 越早丢**（同一类内先丢"更不重要"的）

</div>

**How the three marking fields map onto each other (consistency is QoS rule number one)**:

<div class="zh" markdown="1">

**三种标记字段的映射关系（一致性是 QoS 的第一原则）**：

</div>

| Layer | Field | Width | When it matters |
|----|------|------|---------|
| L3 | DSCP (the top 6 bits of the IP ToS byte) | 6 | the end-to-end primary marking |
| L2 | 802.1p CoS (VLAN tag) | 3 | inside a Layer 2 domain, and WMM on wireless |
| MPLS | EXP/TC | 3 | across an MPLS domain there are **only 3 bits**, so EF degrades to 5 |
| Tunnel outer header | outer DSCP | 6 | only the outer header counts across the Internet |

<div class="zh" markdown="1">

| 层 | 字段 | 位宽 | 何时注意 |
|----|------|------|---------|
| L3 | DSCP（IP ToS 高 6 位） | 6 | 端到端的主标记 |
| L2 | 802.1p CoS（VLAN tag） | 3 | 二层域内、无线 WMM |
| MPLS | EXP/TC | 3 | 跨 MPLS 域时**只有 3 位**，EF 会退化为 5 |
| 隧道外层 | 外层 DSCP | 6 | 跨 Internet 时外层才有效 |

</div>

> ⚠️ **The MPLS three-bit trap**: EF(46) → EXP 5 → on leaving the MPLS domain, the default mapping back to DSCP yields CS5(40), so the voice queue no longer matches. **An explicit EXP↔DSCP mapping table is mandatory.**

<div class="zh" markdown="1">

> ⚠️ **MPLS 的 3 位陷阱**：EF(46) → EXP 5 → 出 MPLS 域若按默认映射回 DSCP 会变成 CS5(40)，语音队列匹配失败。**必须显式配置 EXP↔DSCP 映射表。**

</div>

### The Eleven-Class Model (Ready to Use as an Enterprise Standard) · 十一类模型（可直接作为企业标准）

| # | Class | DSCP | Bandwidth (share of WAN) | Queue behaviour | Notes |
|---|------|------|------------------|---------|------|
| 1 | **Voice** | EF 46 | sized by concurrent calls, **≤33%** | **LLQ + policer** (priority police) | the most latency-sensitive |
| 2 | **TelePresence/real-time interactive** | CS4 32 | 10–20% | LLQ (second priority) or AF bandwidth guarantee | real time, like voice |
| 3 | **Broadcast Video** | CS5 40 | 10–30% | bandwidth guarantee + CBWFQ | one-way, bufferable |
| 4 | **Multimedia Conferencing** | AF41 34 | 10–15% | AF41/42/43 + WRED | tolerates some loss |
| 5 | **Multimedia Streaming** | AF31 26 | 5–10% | AF31/32/33 + WRED | VOD/training |
| 6 | **Call Signaling** | CS3 24 | 1–2% | bandwidth guarantee (small queue) | too small and "calls fail to set up" |
| 7 | **Network Control** | CS2 16 (or CS6 48) | 1–3% | bandwidth guarantee | routing/management protocols |
| 8 | **Transactional Data** | AF21 18 | 10–15% | AF21/22/23 + WRED | ERP, DB (**latency-sensitive**) |
| 9 | **Bulk Data** | AF11 10 | 5% | AF11/12/13 + WRED | backup, replication |
| 10 | **Best Effort** | DF 0 | the remainder (≥25%) | default FIFO | Internet/e-mail |
| 11 | **Scavenger** | CS1 8 | **1–2% (hard ceiling)** | tiny bandwidth guarantee + aggressive dropping | P2P, patch distribution |

<div class="zh" markdown="1">

| # | 类别 | DSCP | 带宽（占 WAN 比例） | 队列特性 | 说明 |
|---|------|------|------------------|---------|------|
| 1 | **Voice** | EF 46 | 按并发算，**≤33%** | **LLQ + 限速**（priority police） | 延迟最敏感 |
| 2 | **TelePresence/实时交互** | CS4 32 | 10–20% | LLQ（次优先）或 AF 带宽保证 | 与语音同属实时 |
| 3 | **Broadcast Video** | CS5 40 | 10–30% | 带宽保证 + CBWFQ | 单向、可缓冲 |
| 4 | **Multimedia Conferencing** | AF41 34 | 10–15% | AF41/42/43 + WRED | 允许轻微丢弃 |
| 5 | **Multimedia Streaming** | AF31 26 | 5–10% | AF31/32/33 + WRED | VOD/培训 |
| 6 | **Call Signaling** | CS3 24 | 1–2% | 带宽保证（小队列） | 太小会"打通失败" |
| 7 | **Network Control** | CS2 16（或 CS6 48） | 1–3% | 带宽保证 | 路由/管理协议 |
| 8 | **Transactional Data** | AF21 18 | 10–15% | AF21/22/23 + WRED | ERP、DB（**延迟敏感**） |
| 9 | **Bulk Data** | AF11 10 | 5% | AF11/12/13 + WRED | 备份、复制 |
| 10 | **Best Effort** | DF 0 | 剩余（≥25%） | 默认 FIFO | 互联网/邮件 |
| 11 | **Scavenger** | CS1 8 | **1–2%（硬上限）** | 带宽保证很小 + 强丢 | P2P、补丁分发 |

</div>

**Configuration points**:

<div class="zh" markdown="1">

**配置要点**：

</div>

- The sum of all "bandwidth guarantees" must be **≤ 75%–80%** of the link bandwidth (leaving headroom for LLQ and bursts)
- **LLQ must have a policer**: otherwise EF traffic is unbounded and the other queues **starve** (especially dangerous when the voice class is abused or looped)
- **A scavenger class is mandatory**: without it, P2P/update traffic fills the leftover BE bandwidth
- Queue depth should be **shallow** for voice (to avoid queueing delay) and may be deep for bulk (to absorb bursts)

<div class="zh" markdown="1">

- 所有"带宽保证"之和 **≤ 75%–80%** 链路带宽（给 LLQ 与突发留余量）
- **LLQ 必须带 policer**：否则 EF 流量无上限，其余队列**饿死**（语音类被滥用/环回放大时尤为危险）
- **scavenger 一定要有**：没有它，P2P/更新流量就会占满 BE 剩余带宽
- 队列深度对语音要**浅**（避免排队延迟），对批量可以深（吸收突发）

</div>

### Queueing and Congestion-Management Mechanisms · 排队与拥塞管理机制

| Mechanism | Function | Where it fits | Risk |
|------|------|------|------|
| **FIFO** | simple first-in first-out | BE | no isolation |
| **PQ (priority queueing)** | strict priority | only for small volumes (e.g. signalling) | **high priority can starve everything** |
| **CBWFQ** | per-class bandwidth guarantee + WFQ | most classes | no latency guarantee |
| **LLQ** | strict priority + policing | voice/real time | without a policer it starves the rest |
| **WRED** | drops early, by drop precedence, before the queue is full | AF classes | bad parameters cause TCP jitter |
| **ECN** | marks instead of dropping (needs end-to-end support) | modern DC/WAN | requires support at both ends and in the application |
| **Shaping** | buffers the excess and smooths the output | WAN egress/sub-rate links | adds latency (bufferbloat) |
| **Policing** | drops or downgrades the excess immediately | access boundaries, carriers | causes TCP global synchronisation |

<div class="zh" markdown="1">

| 机制 | 作用 | 适用 | 风险 |
|------|------|------|------|
| **FIFO** | 简单先入先出 | BE | 无隔离 |
| **PQ（优先级队列）** | 严格优先 | 仅小流量（如信令） | **高优先级可饿死全部** |
| **CBWFQ** | 按类保证带宽 + WFQ | 大多数类 | 无延迟保证 |
| **LLQ** | 严格优先 + 限速 | 语音/实时 | 未限速会饿死其他 |
| **WRED** | 队列满之前按丢弃优先级提前丢 | AF 类 | 参数不当导致 TCP 抖动 |
| **ECN** | 用标记代替丢包（需端到端支持） | 现代 DC/WAN | 需两端与应用支持 |
| **整形（Shaping）** | 缓存超额、平滑输出 | WAN 出口/子速率 | 增加延迟（缓冲膨胀） |
| **监管（Policing）** | 超额直接丢/降级 | 接入边界、运营商 | 造成 TCP 全局同步 |

</div>

**Hierarchical QoS (HQoS)**: first shape to the contracted rate (say 1 Gbps physical, 200 Mbps contracted), then hang the child queues underneath it. **Sub-rate links are the most commonly missed QoS scenario** — the physical port is 1 Gbps but the carrier guarantees only 200 Mbps; if the queues are configured for 1 Gbps, congestion happens on the carrier side and your queues are purely decorative.

<div class="zh" markdown="1">

**层级化 QoS（HQoS）**：先整形到合同速率（如物理 1G、合同 200M），再在其下挂子队列。**子速率链路是 QoS 最容易被漏掉的场景** —— 物理口 1G 但运营商只保证 200M，若按 1G 配置队列，拥塞发生在运营商侧，你的队列形同虚设。

</div>

### Bandwidth Calculation: Working Out "How Much Voice Needs" · 带宽计算：把"语音要多少"算出来

**Bandwidth for a single call (G.711, 20 ms packetisation)**:

<div class="zh" markdown="1">

**单路语音带宽（G.711，20 ms 打包）**：

</div>

```
pps = 1000 / 20 = 50
L3 per packet = 160 B payload + 12 B RTP + 8 B UDP + 20 B IP = 200 B
L3 bandwidth = 200 × 8 × 50 = 80 kbps
L2 overhead = (18 B Ethernet header + 20 B preamble/IFG) × 8 × 50 = 15.2 kbps
L2 bandwidth ≈ 95 kbps per call
```

<div class="zh" markdown="1">

```
pps = 1000 / 20 = 50
L3 每包 = 160 B 载荷 + 12 B RTP + 8 B UDP + 20 B IP = 200 B
L3 带宽 = 200 × 8 × 50 = 80 kbps
L2 开销 = (18 B 以太头 + 20 B 前导/IFG) × 8 × 50 = 15.2 kbps
L2 带宽 ≈ 95 kbps/路
```

</div>

| Codec | Payload/packet | pps | L3 bandwidth | Real Ethernet rate | Notes |
|------|--------|-----|--------|-----------|------|
| G.711 (20 ms) | 160 B | 50 | 80 kbps | **≈95 kbps** | the most common |
| G.711 (30 ms) | 240 B | 33 | 64 kbps | ≈78 kbps | slightly higher latency |
| G.729 (20 ms) | 20 B | 50 | 24 kbps | **≈32 kbps** | compressed, needs a DSP |
| G.722 (20 ms) | 160 B | 50 | 80 kbps | ≈95 kbps | wideband voice |
| OPUS (20 ms) | variable | 50 | 24–64 kbps | depends on bitrate | WebRTC |

<div class="zh" markdown="1">

| 编码 | 载荷/包 | pps | L3 带宽 | 以太网实际 | 备注 |
|------|--------|-----|--------|-----------|------|
| G.711 (20 ms) | 160 B | 50 | 80 kbps | **≈95 kbps** | 最常见 |
| G.711 (30 ms) | 240 B | 33 | 64 kbps | ≈78 kbps | 延迟略高 |
| G.729 (20 ms) | 20 B | 50 | 24 kbps | **≈32 kbps** | 压缩，需 DSP |
| G.722 (20 ms) | 160 B | 50 | 80 kbps | ≈95 kbps | 宽带语音 |
| OPUS (20 ms) | 可变 | 50 | 24–64 kbps | 视码率 | WebRTC |

</div>

**Concurrency and link capacity**:

<div class="zh" markdown="1">

**并发与链路容量**：

</div>

```
total voice bandwidth = concurrent calls at the site × per-call bandwidth × 1.2 (signalling + retransmission headroom)
concurrent calls ≈ headcount × concurrency ratio (0.1–0.2, up to 0.3 at peak hour)
```

<div class="zh" markdown="1">

```
语音总带宽 = 站点并发通话数 × 单路带宽 × 1.2（信令+重传余量）
并发数估算 = 员工数 × 并发率（0.1–0.2，峰呼时可达 0.3）
```

</div>

**Worked example**: a 500-person site at a 15% concurrency ratio → 75 calls × 95 kbps ≈ 7.1 Mbps × 1.2 ≈ **8.5 Mbps**; on a 100 Mbps egress, voice takes 8.5% — healthy. If the egress is only 20 Mbps, voice takes 42% → **CAC (call admission control) is mandatory** to cap concurrency, because even LLQ cannot save you.

<div class="zh" markdown="1">

**算例**：500 人站点，并发率 15% → 75 路 × 95 kbps ≈ 7.1 Mbps × 1.2 ≈ **8.5 Mbps**；若出口 100 Mbps，语音占 8.5% —— 健康。若出口只有 20 Mbps，语音占 42% → **必须上 CAC（呼叫准入控制）限制并发**，否则 LLQ 也救不了。

</div>

**Serialisation delay (which decides "can voice run on a low-bandwidth link")**:

<div class="zh" markdown="1">

**序列化延迟（决定"低带宽链路能不能跑语音"）**：

</div>

| Link rate | Serialisation delay of a 1500 B frame | Suitable for voice |
|---------|--------------------|------------|
| 64 kbps | 187 ms | ❌ |
| 256 kbps | 47 ms | ❌ (needs fragmentation/interleaving) |
| 512 kbps | 23 ms | ⚠️ marginal (needs LFI/MLPPP) |
| 1.5 Mbps | 8 ms | ✅ |
| 10 Mbps | 1.2 ms | ✅ |
| 100 Mbps+ | <0.2 ms | ✅ |

<div class="zh" markdown="1">

| 链路速率 | 1500 B 帧的序列化延迟 | 是否适合语音 |
|---------|--------------------|------------|
| 64 kbps | 187 ms | ❌ |
| 256 kbps | 47 ms | ❌（需分片/交错） |
| 512 kbps | 23 ms | ⚠️ 勉强（需 LFI/MLPPP） |
| 1.5 Mbps | 8 ms | ✅ |
| 10 Mbps | 1.2 ms | ✅ |
| 100 Mbps+ | <0.2 ms | ✅ |

</div>

> 💡 **Rule of thumb**: a voice-bearing link should be **≥ 768 kbps** with LLQ enabled; below that you need link fragmentation (LFI) or you simply do not carry voice. **Serialisation delay is a physical constraint that no queueing discipline can remove.**

<div class="zh" markdown="1">

> 💡 **经验判据**：语音链路 **≥ 768 kbps** 且开启 LLQ 才比较安全；低于此需链路分片（LFI）或干脆不承载语音。**序列化延迟是物理约束，QoS 队列无法消除它。**

</div>

### End-to-End Latency Budget (Writing the SLA into the Design) · 端到端时延预算（把 SLA 写进设计）

| Stage | Budget (one-way) |
|------|------------|
| Encoding/packetisation | 20–30 ms |
| Access + aggregation queueing | ≤5 ms |
| Core queueing | ≤5 ms |
| WAN propagation (500 km inter-city ≈ 2.5 ms/100 km of fibre ≈ 12 ms) | 5–40 ms |
| Jitter buffer (de-jitter) | 20–40 ms |
| Decoding | 10–20 ms |
| **Total (G.114 recommendation)** | **≤150 ms one-way, with 300 ms as the tolerance limit** |

<div class="zh" markdown="1">

| 环节 | 预算（单向） |
|------|------------|
| 编码/打包 | 20–30 ms |
| 接入+汇聚排队 | ≤5 ms |
| 核心排队 | ≤5 ms |
| WAN 传播（跨城 500 km ≈ 2.5 ms/100km 光纤 ≈ 12 ms） | 5–40 ms |
| 抖动缓冲（去抖） | 20–40 ms |
| 解码 | 10–20 ms |
| **合计（G.114 建议）** | **≤150 ms（单向），≤300 ms 为容忍上限** |

</div>

**Why the budget table matters**: when someone asks "can we run voice over the satellite backup link", the answer falls straight out (a GEO satellite hop is ~250 ms RTT → 125 ms one-way, plus encoding and buffering → **it necessarily exceeds the budget**).

<div class="zh" markdown="1">

**预算表的作用**：当有人问"能不能上卫星备份链路跑语音"时，答案可以直接算出（GEO 卫星单跳 ~250 ms RTT → 单向 125 ms，加上编码与缓冲 → **必然超标**）。

</div>

### Deployment Models for the Trust Boundary (the Crux of DiffServ) · 信任边界的部署模型（DiffServ 的命门）

**The whole of QoS comes down to one question: within this packet, is the DSCP a trusted fact or a user's wish?**

<div class="zh" markdown="1">

**整个 QoS 只有一个核心问题：DSCP 在这个包里是"可信的事实"还是"用户的愿望"。**

</div>

| Deployment segment | Marking source | Action | Configuration points |
|---------|---------|------|---------|
| **Access (phone port)** | the phone marks EF/CS3; PC traffic is re-marked to 0 by the phone | trust dscp | "PC port re-marking" must be enabled in the phone's configuration |
| **Access (PC port)** | the user can forge anything | **untrust + re-mark to BE**, or NBAR classification | never `trust dscp` |
| **Access (wireless)** | the terminal sets the UP (802.11e) | trust the UP→DSCP mapping but **rate-limit** | per-SSID rate limiting to stop a single client saturating the AP |
| **Aggregation** | already cleaned at the boundary | trust dscp | add a policer as a backstop (against internal scans/anomalies) |
| **Core** | trusted | trust + queues | no classification, scheduling only |
| **WAN egress** | aligned with carrier capability | **re-mark + shape to the contracted rate** | if the carrier honours only 3–6 classes, collapse the classes |
| **Internet egress** | untrusted across domains | only the outbound direction can be guaranteed; inbound cannot | **never** promise QoS for external traffic |
| **Across IPSec/GRE** | the inner header is encrypted | **copy the DSCP to the outer header** (or map by class) | otherwise the transit network cannot see it |

<div class="zh" markdown="1">

| 部署区段 | 标记来源 | 动作 | 配置要点 |
|---------|---------|------|---------|
| **接入层（话机口）** | 话机标 EF/CS3，PC 流量被话机重标 0 | trust dscp | 必须在话机配置里开启"PC 口重标记" |
| **接入层（PC 口）** | 用户可任意伪造 | **untrust + 重标 BE**，或 NBAR 识别 | 绝不 `trust dscp` |
| **接入层（无线）** | 终端标 UP(802.11e) | 信任 UP→DSCP 但**限速** | 每 SSID 限速，防单终端打满 |
| **汇聚层** | 已被边界清洗 | trust dscp | 加 policer 兜底（防内部扫描/异常） |
| **核心层** | 可信 | trust + 队列 | 无分类，只调度 |
| **WAN 出口** | 与运营商能力对齐 | **重标记 + 整形到合同速率** | 运营商只认 3–6 类时要砍类 |
| **Internet 出口** | 跨域不可信 | 只保证"出去的方向"，入向无法保证 | 对外部流量**不要**承诺 QoS |
| **跨 IPSec/GRE** | 内层被加密 | **外层复制 DSCP**（或按类映射） | 否则中间网络看不到 |

</div>

> ⚠️ **The most expensive mistake**: `trust dscp` end to end with nobody managing the terminals. One user then marks their traffic EF with a tool, voice is squeezed out at busy times by its own shadow traffic — and **every queue statistic looks "normal"**.

<div class="zh" markdown="1">

> ⚠️ **最贵的错误**：全程 `trust dscp` 但没人管终端。结果某个用户用工具把流量标成 EF，语音在忙时被自己的影子流量挤掉，而**所有队列统计看起来都"正常"**。

</div>

### Control-Plane and Management-Plane QoS (CoPP) · 控制面与管理面 QoS

Forwarding-plane QoS protects the service; **CoPP protects the device itself**. Without CoPP, a single scan or multicast flood can pin the management-plane CPU and cause routing-protocol timeouts.

<div class="zh" markdown="1">

转发面的 QoS 保护业务；**CoPP 保护设备自己**。没有 CoPP 时，一次扫描或组播泛洪就能把管理面 CPU 打满，导致路由协议超时。

</div>

| Traffic class | Suggested DSCP | Policing policy |
|-------|----------|---------|
| Routing protocols (BGP/OSPF/EIGRP/IS-IS) | CS6 | low rate + high priority (never drop) |
| Management access (SSH/SNMP/NETCONF) | CS2 | medium rate |
| ICMP (including ICMPv6 ND) | CS2 | **ND must always be permitted**; rate-limit only, never drop |
| Layer 2 protocols (STP/LACP/LLDP) | CS6 | low rate, high punt priority |
| Exception/unknown punt | — | **a minimal quota** (dropped by default) |

<div class="zh" markdown="1">

| 流量类 | 建议 DSCP | 限速策略 |
|-------|----------|---------|
| 路由协议（BGP/OSPF/EIGRP/IS-IS） | CS6 | 低速率 + 高优先（不可丢） |
| 管理访问（SSH/SNMP/NETCONF） | CS2 | 中速率 |
| ICMP（含 ICMPv6 ND） | CS2 | **必须放行 ND**，只限速不可丢 |
| 二层协议（STP/LACP/LLDP） | CS6 | 低速率，punt 优先 |
| 异常/未知 punt | — | **最小配额**（默认丢弃） |

</div>

**CoPP design principles**: **deny by default** (give unclassified punt traffic a tiny quota) and **differentiate by interface role** (user ports vs uplinks vs management ports). Well-built CoPP keeps routing protocols alive while "users go mad sending ARP/ND".

<div class="zh" markdown="1">

**CoPP 的设计原则**：**默认拒绝**（未分类的 punt 流量给极小配额），并**按接口角色区分**（用户口 vs 上联口 vs 管理口）。做得好的 CoPP 能在"用户疯狂发 ARP/ND"时保住路由协议。

</div>

### Tunnels and QoS: The Three-Layer Encapsulation Problem · 隧道与 QoS：三层封装问题

| Scenario | Encapsulation overhead | Consequence | Treatment |
|------|---------|------|------|
| **GRE** | 24 B (20 IP + 4 GRE) | MTU must drop to 1476 | **copy the inner DSCP to the outer header** (`qos pre-classify`) |
| **IPsec transport mode** | 50–73 B | MTU 1420–1450 | as above; ESP hides the inner ToS, so **copying to the outer header is mandatory** |
| **DMVPN** | GRE + NHRP + IPsec | double encapsulation | **shape the branch egress below the physical rate** (and at the hub too) |
| **VXLAN** | 50 B (20 outer IP + 8 UDP + 8 VXLAN + 14 inner Ethernet) | needs a 1550 MTU or fragmentation | map the outer DSCP from the inner one |
| **SD-WAN (IPsec over Internet)** | implementation-dependent | the transit network is not under your control | **per-tunnel QoS + application awareness + forward error correction** |

<div class="zh" markdown="1">

| 场景 | 封装开销 | 后果 | 处理 |
|------|---------|------|------|
| **GRE** | 24 B（20 IP + 4 GRE） | MTU 需降到 1476 | 内层 DSCP **复制到外层**（`qos pre-classify`） |
| **IPsec 传输模式** | 50–73 B | MTU 1420–1450 | 同上；ESP 隐藏内层 ToS，**必须复制到外层** |
| **DMVPN** | GRE + NHRP + IPsec | 双重封装 | 分支出口**整形到物理速率以下**（hub 侧也要） |
| **VXLAN** | 50 B（外 20 IP + 8 UDP + 8 VXLAN + 14 内层以太） | 需 1550 MTU 或分片 | 外层 DSCP 按内层映射 |
| **SD-WAN（IPsec over Internet）** | 视实现 | 中间网络不可控 | 用 **每隧道 QoS + 应用感知 + 前向纠错** |

</div>

> 💡 **The test question**: **"does my marking survive the tunnel?"** Capture one outer packet and look at the ToS byte. The overwhelming majority of "voice gets worse across the WAN" cases come down to an outer DSCP of 0.

<div class="zh" markdown="1">

> 💡 **判断句**：**"我的标记在隧道里还活着吗？"** 抓一次外层包看 ToS 字段即可。绝大多数"跨 WAN 语音变差"都源于外层 DSCP = 0。

</div>

### Wireless QoS (WMM) and the Mapping to the Wired Side · 无线 QoS（WMM）与有线的映射

| WMM access category (AC) | 802.11 user priority (UP) | Mapped DSCP | Notes |
|------------------|----------------------|----------|------|
| **Voice (VO)** | 6, 7 | EF 46 | strict priority, **the most expensive in airtime** |
| **Video (VI)** | 4, 5 | AF41/CS4 | video |
| **Best Effort (BE)** | 0, 3 | DF 0 | default |
| **Background (BK)** | 1, 2 | CS1 8 | scanning/backup |

<div class="zh" markdown="1">

| WMM 接入类别（AC） | 802.11 用户优先级（UP） | 映射 DSCP | 说明 |
|------------------|----------------------|----------|------|
| **Voice (VO)** | 6, 7 | EF 46 | 严格优先，**airtime 消耗最贵** |
| **Video (VI)** | 4, 5 | AF41/CS4 | 视频 |
| **Best Effort (BE)** | 0, 3 | DF 0 | 默认 |
| **Background (BK)** | 1, 2 | CS1 8 | 扫描/备份 |

</div>

**Three peculiarities of wireless QoS**:

<div class="zh" markdown="1">

**无线 QoS 的三个特殊性**：

</div>

1. **Airtime is a shared medium**: giving voice priority is not "free"; high-priority frames still consume airtime
2. **Upstream marking is decided by the terminal** (and can be forged), so **per-SSID rate limiting** is mandatory (per-client/per-SSID policing)
3. **Multicast/broadcast frames are sent at the lowest rate** and eat a lot of airtime → **multicast-to-unicast** plus suppression

<div class="zh" markdown="1">

1. **Airtime 是共享介质**：给语音优先不等于"免费"，高优先级帧仍占 airtime
2. **上行标记由终端决定**（可伪造），所以必须**每 SSID 限速**（per-client/per-SSID policing）
3. **组播/广播帧用最低速率发送**，会吃掉大量 airtime → **组播转单播** + 抑制

</div>

### QoS Acceptance: How to Prove It Actually Works · QoS 的验收：怎么证明它真的生效

| Check | Method | Pass criterion |
|--------|------|---------|
| Marking is correct | capture at each segment and read the DSCP (`tcpdump -v` / SPAN) | consistent end to end, with the expected values outside the boundary |
| Queues are hit | class match counters from `show policy-map interface` | every class has counters; not everything lands in class-default |
| Congestion behaviour | drive load to 110% and then measure voice (IXIA/iperf + a voice simulator) | voice MOS ≥4.0, jitter <30 ms |
| Policing works | over-rate testing | scavenger is held at the configured value |
| LLQ ceiling | flood EF traffic | voice does not starve the other classes (the policer works) |
| Across tunnels | capture the outer packet | outer DSCP matches the inner one |
| Reverse direction | measure from the far end back | **verify both directions** (many problems exist on one side only) |

<div class="zh" markdown="1">

| 检查项 | 方法 | 通过标准 |
|--------|------|---------|
| 标记正确 | 各段抓包看 DSCP（`tcpdump -v` / SPAN） | 端到端一致，边界外为预期值 |
| 队列命中 | `show policy-map interface` 的 class 匹配计数 | 每类都有计数，无"全落 class-default" |
| 拥塞行为 | 打流到 110% 再测语音（如 IXIA/iperf + 语音模拟） | 语音 MOS ≥4.0，抖动 <30 ms |
| 限速生效 | 超速测试 | scavenger 被压制在配置值 |
| LLQ 上限 | 灌满 EF 流量 | 语音不挤死其他类（policer 生效） |
| 跨隧道 | 抓外层包 | 外层 DSCP 与内层一致 |
| 反向 | 从对端测回来 | **双向都要验**（大量问题只在一侧） |

</div>

> ⚠️ **Acceptance under congestion is mandatory**. QoS measured on an idle network always "passes", because no queue ever builds up. **A QoS acceptance without congestion injection is not an acceptance at all.**

<div class="zh" markdown="1">

> ⚠️ **必须做"拥塞下的验收"**。空载测 QoS 永远是"通过"的，因为队列没排队。**没有拥塞注入的 QoS 验收等于没验。**

</div>

---

## Network Management: Designing the Management Plane as a Network · 网络管理：把管理平面当一张网来设计

### In-Band vs Out-of-Band (OOB) · 带内 vs 带外

| Option | Path | Advantages | Drawbacks | Where it fits |
|------|------|------|------|------|
| **In-band** | reuses the service ports with a management VRF | zero extra cost | **a service failure also removes management** | the default in most enterprises |
| **Out-of-band (OOB)** | dedicated management switches + dedicated physical ports | you can still log in when the service network is fully down | cabling cost, needs its own address block/ACLs | core, data centre, unmanned sites |
| **Console server** | serial concentration (terminal server) | the last resort when a device is "completely unreachable" | low speed, poor experience | all critical devices |
| **LTE/5G backup** | an independent wireless link | physically separate from the service links | monthly fee, security (strict ACLs required) | branches/unmanned sites |

<div class="zh" markdown="1">

| 方式 | 路径 | 优点 | 缺点 | 适用 |
|------|------|------|------|------|
| **带内（in-band）** | 复用业务口与管理 VRF | 零额外成本 | **业务故障时同时失去管理** | 一般企业默认 |
| **带外（OOB）** | 独立管理交换机 + 独立物理口 | 业务全断仍可登录 | 布线成本、需独立地址段/ACL | 核心/数据中心/无人站点 |
| **Console 服务器** | 串口集中（终端服务器） | 设备"彻底失联"时的最后手段 | 速率低、体验差 | 所有关键设备 |
| **LTE/5G 备份** | 独立无线链路 | 与业务链路物理隔离 | 月租、安全（需严格 ACL） | 分支/无人值守 |

</div>

**The OOB bandwidth budget (frequently overlooked)**:

<div class="zh" markdown="1">

**OOB 的带宽账（经常被忽略）**：

</div>

| Operation | Data per device | 100 devices in parallel | Time on a 10 Mbps management port |
|------|-------------|-----------|------------------|
| Configuration backup (scp) | 50–500 KB | 5–50 MB | 4–40 s |
| System image upgrade | 0.5–2 GB | **50–200 GB** | **11–27 minutes per device (serialised)** |
| Log burst (storm) | peaks of 10–50 Mbps | — | **saturates the OOB link** |
| Telemetry (10 s interval) | see the earlier example | 6.4 Mbps | saturates a 10 Mbps link |

<div class="zh" markdown="1">

| 操作 | 单设备数据量 | 100 台并发 | 10 Mbps 管理口耗时 |
|------|-------------|-----------|------------------|
| 配置备份（scp） | 50–500 KB | 5–50 MB | 4–40 s |
| 系统镜像升级 | 0.5–2 GB | **50–200 GB** | **11–27 分钟/台（串行）** |
| 日志突发（风暴） | 峰值 10–50 Mbps | — | **打满 OOB** |
| 遥测（10 s 级） | 见前算例 | 6.4 Mbps | 打满 10 Mbps 链路 |

</div>

> ⚠️ **Conclusion**: a 10/100 Mbps management switch is enough for a small network, but it inevitably becomes the bottleneck during "a network-wide image upgrade" or a "log storm". **Plan for 1 Gbps management links, and run upgrades in batches with rate limiting.**

<div class="zh" markdown="1">

> ⚠️ **结论**：10/100 Mbps 的管理交换机在小网够用，但在"全网升级镜像"或"日志风暴"时必然成为瓶颈。**管理链路建议 1 Gbps，并且升级要分批 + 限速。**

</div>

### The Five Mandatory Design Actions for the Management Plane · 管理平面的五个必备设计动作

1. **A dedicated management VRF/address block** (such as `10.255.0.0/16` or `fd00:mgmt::/64`), never mixed with service addressing
2. **Management-plane ACLs**: permit only the jump-host/NMS/backup-server subnets, **deny by default**
3. **A jump host**: every login goes through it, with session recording and audit
4. **Tiered AAA**: read-only for the NOC, read-write for engineers, changes through automation accounts; plus **local fallback accounts** (stored offline, rotated regularly)
5. **Verify out-of-band reachability**: **rehearse "log in over OOB after the service network is fully down" every quarter** (an unrehearsed OOB is no OOB at all)

<div class="zh" markdown="1">

1. **独立管理 VRF/地址段**（如 `10.255.0.0/16` 或 `fd00:mgmt::/64`），不与业务地址混用
2. **管理面 ACL**：只允许跳板机/NMS/备份服务器网段，**默认拒绝**
3. **跳板机（Jump Host）**：所有登录经过它，带会话录屏与审计
4. **AAA 分级**：NOC 只读、工程师读写、变更走自动化账号；**本地回退账号**（离线保存、定期改密）
5. **带外可达性验证**：**每季度演练"业务全断后用 OOB 登录"**（没演练的 OOB 等于没有）

</div>

### Where Each Device-Management Protocol Fits (Chapter 12 Covered APIs; Here Is the Operations View) · 设备管理协议的定位（第 12 章讲过 API，这里补运维视角）

| Protocol | Transport/port | Mode | Main use | Operations notes |
|------|----------|------|---------|---------|
| **SNMPv2c** | UDP 161/162 | polling + traps | device health, interface statistics | community strings are cleartext: **isolated segments only** |
| **SNMPv3** | UDP 161/162 | polling + Trap/Inform | as above (recommended) | `authPriv` (SHA-256 + AES); watch engine ID to user binding |
| **Syslog** | UDP 514 / TCP 601 / TLS 6514 | push | event logs | use TCP/TLS to avoid loss; **rate limiting is mandatory** |
| **NetFlow v9 / IPFIX** | UDP 2055/4739 | push | traffic analysis | the template and sampling ratio must be on record |
| **sFlow** | UDP 6343 | packet sampling | throughput distribution (lightweight) | samples headers only, good for very high volume |
| **gNMI/gRPC** | TCP 57400 | push/pull | streaming telemetry, configuration | requires certificates and TLS |
| **NETCONF/RESTCONF** | TCP 830 / 443 | session | configuration (see Chapter 12) | locking and transaction semantics |
| **IP SLA / synthetic probes** | device-initiated | active measurement | end-to-end quality | useless unless the results reach the NMS |
| **Telnet** | TCP 23 | — | **disabled** | cleartext, a compliance liability |
| **TFTP/SCP** | UDP 69 / TCP 22 | file | images, configurations | **use SCP/HTTPS instead of TFTP** |

<div class="zh" markdown="1">

| 协议 | 传输/端口 | 模式 | 主要用途 | 运维注意 |
|------|----------|------|---------|---------|
| **SNMPv2c** | UDP 161/162 | 轮询 + Trap | 设备健康、接口统计 | 团体字=明文，**仅限隔离网段** |
| **SNMPv3** | UDP 161/162 | 轮询 + Trap/Inform | 同上（推荐） | `authPriv`（SHA-256 + AES）；注意引擎 ID 与用户绑定 |
| **Syslog** | UDP 514 / TCP 601 / TLS 6514 | 推送 | 事件日志 | 用 TCP/TLS 防丢；**必须配限速** |
| **NetFlow v9 / IPFIX** | UDP 2055/4739 | 推送 | 流量分析 | 模板 + 采样比要记录在案 |
| **sFlow** | UDP 6343 | 包采样 | 吞吐分布（轻量） | 只采样包头，适合大流量 |
| **gNMI/gRPC** | TCP 57400 | 推送/拉取 | 流式遥测、配置 | 需证书与 TLS |
| **NETCONF/RESTCONF** | TCP 830 / 443 | 会话 | 配置（见第 12 章） | 锁与事务语义 |
| **IP SLA / 合成探测** | 设备发起 | 主动测量 | 端到端质量 | 结果要送到 NMS 才有用 |
| **Telnet** | TCP 23 | — | **禁用** | 明文，合规硬伤 |
| **TFTP/SCP** | UDP 69 / TCP 22 | 文件 | 镜像、配置 | **SCP/HTTPS 替代 TFTP** |

</div>

### SNMP Design Points (More Than "Set a Community String") · SNMP 的设计要点（不只是"配个团体字"）

| Point | Explanation |
|------|------|
| **Version** | v3 `authPriv`; v2c only on isolated management segments |
| **Views (VACM)** | expose only the MIBs you need (`ifTable`, `ifXTable`, CPU, memory, environment) |
| **Trap vs Inform** | Inform is acknowledged (reliable but costly); **use Inform for link/power events and Trap for the rest** |
| **Polling interval** | interfaces every 1–5 minutes; **do not poll** large tables (routing table, ARP table) — use events or telemetry |
| **Bulk requests** | `getbulk` cuts round trips, but an oversized `max-repetitions` can overwhelm the device |
| **Engine ID changes** | SNMPv3 users break after an engine or supervisor swap → **make it part of the swap procedure** |
| **Scale ceiling** | one collector can poll 500–2000 devices (depending on OID count and interval); **partition by device count** |

<div class="zh" markdown="1">

| 要点 | 说明 |
|------|------|
| **版本** | v3 `authPriv`；v2c 只在隔离管理网段 |
| **视图（VACM）** | 只暴露需要的 MIB（`ifTable`、`ifXTable`、CPU、内存、环境） |
| **Trap vs Inform** | Inform 有确认（可靠但耗资源）；**链路/电源类用 Inform，其余 Trap** |
| **轮询周期** | 接口 1–5 分钟；大表（路由表、ARP 表）**不轮询**，用事件或遥测 |
| **Bulk 请求** | `getbulk` 减少往返，但 `max-repetitions` 太大会打爆设备 |
| **引擎 ID 变更** | 换引擎/换板卡后 SNMPv3 用户失效 → **纳入换板流程** |
| **规模上限** | 单采集器轮询 500–2000 台（视 OID 数与周期），**要按设备数分区** |

</div>

**Polling-scale worked example**:

<div class="zh" markdown="1">

**轮询规模算例**：

</div>

```
500 devices × 60 OIDs each × every 5 minutes = 100 requests per second
each request/response round trip is about 300–600 B (including UDP/IP overhead)
→ management-plane bandwidth ≈ 0.5 Mbps (acceptable)
but switch to a full ifTable walk (500 rows per device × 200 B per row)
→ 500 KB per poll × 500 devices / 300 s ≈ 0.83 MB/s ≈ 6.7 Mbps, with a marked rise in CPU
```

<div class="zh" markdown="1">

```
设备 500 台 × 每台 60 个 OID × 每 5 分钟一次 = 每秒 100 个请求
每条请求/响应往返约 300–600 B（含 UDP/IP 开销）
→ 管理面带宽 ≈ 0.5 Mbps（可接受）
但若改成 ifTable 全表 walk（每台 500 行 × 每行 200 B）
→ 每次 500 KB × 500 台 / 300 s ≈ 0.83 MB/s ≈ 6.7 Mbps，且 CPU 显著上升
```

</div>

> 💡 **The judgement**: **"fetch only the columns you need (`ifHCInOctets` and friends); never walk the whole table"** — this single rule removes 80% of SNMP overhead and is often the answer to "the device CPU is high but we cannot find why".

<div class="zh" markdown="1">

> 💡 **判断**：**"只取需要的列（`ifHCInOctets` 等），不要 walk 整张表"** —— 这一条能省掉 80% 的 SNMP 开销，也常是"设备 CPU 高但查不出原因"的答案。

</div>

### Flow Collection: Sampling Ratios and Exporter Capacity Budgets · 流（Flow）采集：采样比与出口容量账

| Parameter | Recommendation | Explanation |
|------|------|------|
| Sampling ratio | 1:1000 (core/100G), 1:100 (edge) | the ratio must be **documented**, otherwise traffic estimates are off by 1000× |
| Active timeout | 30 minutes (long-lived flows) | too short and flows are exported repeatedly |
| Inactive timeout | 15 seconds | governs when a flow is considered finished |
| Export targets | two collectors (primary/backup) | one collector is a single point of failure |
| Aggregation | by AS/prefix/protocol | cuts data volume by 90% |

<div class="zh" markdown="1">

| 参数 | 建议 | 说明 |
|------|------|------|
| 采样比 | 1:1000（核心/100G）、1:100（边缘） | 采样比必须**记录**，否则流量估算错 1000 倍 |
| 活跃超时 | 30 分钟（长连接） | 太短会重复导出 |
| 不活跃超时 | 15 秒 | 影响流结束判定 |
| 导出目标 | 2 个采集器（主备） | 单采集器 = 单点 |
| 聚合 | 按 AS/前缀/协议聚合 | 减少 90% 数据量 |

</div>

**Export-bandwidth worked example**:

<div class="zh" markdown="1">

**导出带宽算例**：

</div>

```
core egress 40 Gbps, average packet size 500 B → about 10 Mpps
at 1:1000 sampling → 10,000 flows per second
each export record ≈ 80 B (including template/header overhead on average)
→ 0.8 MB/s ≈ 6.4 Mbps (acceptable)

with **no sampling** (or 1:1) → 10,000,000 flows per second
→ roughly 6.4 Gbps of export traffic → the collector collapses and the device CPU is pinned
```

<div class="zh" markdown="1">

```
核心出口 40 Gbps，平均包长 500 B → 约 10 Mpps
若采样 1:1000 → 10,000 流/秒
每条导出记录 ≈ 80 B（含模板/头部开销平均）
→ 0.8 MB/s ≈ 6.4 Mbps（可接受）

若**不采样**（或采样 1:1）→ 10,000,000 流/秒
→ 约 6.4 Gbps 导出流量 → 采集器必然崩溃，且设备 CPU 打满
```

</div>

> ⚠️ **The real cause of "the device freezes as soon as NetFlow is enabled" is almost always "no sampling plus high pps"**, not NetFlow itself.

<div class="zh" markdown="1">

> ⚠️ **"NetFlow 一开设备就卡"的真正原因几乎都是"没采样 + 高 pps"**，不是 NetFlow 本身有问题。

</div>

### Streaming Telemetry (gNMI) from an Operations Perspective · 流式遥测（gNMI）的运维视角

| Dimension | Dial-in | Dial-out |
|------|---------------|----------------|
| Who opens the connection | the collector connects to the device | **the device connects to the collector** |
| NAT/firewall friendliness | poor (pinholes per device) | **good** (the device initiates outbound) |
| Scale | connections managed by the collector | targets configured on the device |
| Where it fits | small scale, ad-hoc troubleshooting | **large-scale production** |

<div class="zh" markdown="1">

| 维度 | 拨入（dial-in） | 拨出（dial-out） |
|------|---------------|----------------|
| 谁发起连接 | 采集器连接设备 | **设备连接采集器** |
| NAT/防火墙友好 | 差（需逐设备放通） | **好**（设备主动出站） |
| 规模 | 采集器管理连接数 | 设备侧配置目标 |
| 适用 | 小规模、临时排障 | **大规模生产** |

</div>

**Subscription modes**: `ONCE` (one-shot), `POLL` (pull on demand), `STREAM/SAMPLE` (periodic push), `STREAM/ON_CHANGE` (push only on change).

<div class="zh" markdown="1">

**订阅模式**：`ONCE`（一次性）、`POLL`（按需拉）、`STREAM/SAMPLE`（周期推）、`STREAM/ON_CHANGE`（变化才推）。

</div>

**Design advice**: **use ON_CHANGE for critical state (interface state, neighbour state, optical power out of range) and SAMPLE for performance counters (10–60 s); never run 1-second SAMPLE across a whole table.**

<div class="zh" markdown="1">

**设计建议**：**关键指标用 ON_CHANGE（接口状态、邻居状态、光功率越界），性能计数器用 SAMPLE（10–60 s），禁止对全表做 1 秒级 SAMPLE。**

</div>

### Time Synchronisation: The Coordinate System of All Operational Data · 时间同步：所有运维数据的坐标系

| Option | Port | Accuracy | Design points |
|------|------|------|------|
| **NTP v4** | UDP 123 | <1 ms on a LAN, 1–50 ms across networks | hierarchy (stratum 2/3), **authentication**, device-side ACLs, at least 2 sources |
| **PTP (IEEE 1588v2)** | Ethernet/L3 multicast | <1 µs (hardware timestamping) | needs hardware support and boundary clocks; finance/industry |
| **GPS clock source** | — | reference grade | large sites/OOB cores |

<div class="zh" markdown="1">

| 方案 | 端口 | 精度 | 设计要点 |
|------|------|------|---------|
| **NTP v4** | UDP 123 | 局域网 <1 ms，跨网 1–50 ms | 分层（stratum 2/3）、**认证**、设备侧 ACL、至少 2 个源 |
| **PTP（IEEE 1588v2）** | 以太网/L3 组播 | <1 µs（硬件时间戳） | 需硬件支持与边界时钟；金融/工业 |
| **GPS 时钟源** | — | 参考级 | 大型站点/OOB 核心 |

</div>

**NTP hierarchy design (the enterprise standard practice)**:

<div class="zh" markdown="1">

**NTP 层级设计（企业标准做法）**：

</div>

```
Stratum 0: GPS / atomic clock
Stratum 1: 2 internal NTP servers (fed by GPS or a trusted upstream, authentication enabled)
Stratum 2: regional core switches/routers point at Stratum 1 (2 sources)
Stratum 3: access devices point at the regional Stratum 2
Forbidden: terminals and devices pointing directly at the public pool.ntp.org
```

<div class="zh" markdown="1">

```
Stratum 0：GPS / 原子钟
Stratum 1：2 台内网 NTP 服务器（接 GPS 或受信上游，开启认证）
Stratum 2：各区核心交换机/路由器指向 Stratum 1（2 个源）
Stratum 3：接入设备指向本区 Stratum 2
禁止：终端与设备直接指向公网 pool.ntp.org
```

</div>

**A few hard rules**:

<div class="zh" markdown="1">

**几条硬规则**：

</div>

- **At least 2 NTP sources**, with `ntp access-group` permitting queries only from internal subnets (to prevent amplification attacks)
- **Authentication**: NTP's MD5/SHA authentication is weak, but it blocks most spoofing beyond simple misconfiguration; use PTP or a dedicated timing network where it matters
- **Clock-offset alerting**: alert at offsets >1 s (it is the precursor of "the logs do not line up")
- **Check the clocks before a change**: confirm the network-wide offset is <100 ms before the change window opens, otherwise you cannot reconstruct the sequence afterwards

<div class="zh" markdown="1">

- **至少 2 个 NTP 源**，且 `ntp access-group` 只允许内网段查询（防放大攻击）
- **认证**：NTP 的 MD5/SHA 认证虽弱，但能防误配置外的大多数伪造；关键场景用 PTP 或专用时钟网
- **时间偏移告警**：偏移 >1 s 就要告警（这是"日志对不上"的前兆）
- **变更前校时**：变更窗口开始前确认全网时钟偏差 <100 ms，否则事后无法还原时序

</div>

> ⚠️ **A real case**: the VM hosting the NTP server was "doubly synchronised" by the hypervisor's time mechanism plus its own NTP, so its clock jittered by hundreds of milliseconds. The symptom was "every log timestamp is scrambled and certificates occasionally fail", and it took three days to find. **The NTP servers themselves must be monitored (`ntp offset`, `stratum`, `reach`).**

<div class="zh" markdown="1">

> ⚠️ **一个真实场景**：NTP 服务器所在 VM 因宿主机时间同步机制被"双重同步"（宿主同步 + 自身 NTP），导致时间抖动数百毫秒。表现是"所有日志时间乱、证书偶尔失败"，排查花了三天。**NTP 服务器本身也要被监控（`ntp offset`、`stratum`、`reach`）。**

</div>

### Foundational Service Design: DHCP / DHCPv6 · 基础服务设计：DHCP / DHCPv6

| Design item | Recommendation | Rationale |
|--------|------|------|
| **Server deployment** | 2 per major region (load sharing/failover), with core switches as relays | a single point paralyses the whole region |
| **Relaying** | distributed relaying (every Layer 3 gateway is a relay) pointing at 2 servers | relaying itself introduces no new single point |
| **option 82** | **enabled** (circuit-id + remote-id) | lets you identify "who holds which address" and blocks rogue DHCP |
| **DHCP snooping** | access ports untrusted, uplinks trusted | blocks rogue DHCP servers |
| **Lease time** | wired 8–24 h; wireless 2–8 h; guest 1 h | too long → slow address reclamation; too short → broadcast/server load |
| **T1/T2** | defaults of 50%/87.5% | renewal behaviour |
| **option 43/66/67** | for APs/phones/zero-touch deployment | works with ZTP (see Chapter 12) |
| **DHCPv6** | the `M/O` flags must match the RA; relays must be able to reach `FF02::1:2` | a mismatch means terminals get no address |
| **DHCPv6 PD** | branch routers request a prefix from headquarters | prefix delegation (/56 is common) |

<div class="zh" markdown="1">

| 设计项 | 建议 | 原因 |
|--------|------|------|
| **服务器部署** | 每个大区 2 台（负载均衡/故障转移），核心交换机做中继 | 单点会瘫痪整个区域 |
| **中继** | 分布式中继（每台三层网关都是中继），指向 2 个服务器 | 中继本身不引入新单点 |
| **option 82** | **开启**（circuit-id + remote-id） | 定位"谁拿了哪个地址"、防私接 DHCP |
| **DHCP snooping** | 接入端口 untrusted，上联 trusted | 防私设 DHCP 服务器 |
| **租期** | 有线 8–24 h；无线 2–8 h；访客 1 h | 太长→地址回收慢；太短→广播/服务器负载高 |
| **T1/T2** | 默认 50%/87.5% | 续租行为 |
| **option 43/66/67** | 用于 AP/话机/零接触部署 | 与 ZTP 配合（见第 12 章） |
| **DHCPv6** | `M/O` 标志与 RA 一致；中继需 `FF02::1:2` 可达 | 不一致 = 终端拿不到地址 |
| **DHCPv6 PD** | 分支路由器向总部申请前缀 | 前缀委派（/56 常见） |

</div>

**Capacity worked example**: 10,000 terminals, a pool of 8,000 addresses, an 8-hour lease → about 10,000/8 ≈ 1,250 renewals or new allocations per hour → about 0.35 per second (trivial). **But the "morning login surge" can momentarily hit 500 per second, and that is what capacity must be designed for.**

<div class="zh" markdown="1">

**容量算例**：10,000 终端、地址池 8,000、租期 8 h → 平均每小时续租/新建 ≈ 10,000/8 ≈ 1,250 次 → 约 0.35 次/秒（轻松）。**但"早高峰集中上线"时可能瞬时 500 次/秒，这才是容量设计依据。**

</div>

### Foundational Service Design: DNS · 基础服务设计：DNS

| Design item | Recommendation | Rationale |
|--------|------|------|
| **Architecture** | internal authoritative plus internal recursive (forwarding outwards) | separates the internal and external trust boundaries |
| **Conditional forwarding** | forward per domain (`corp.example.com` resolved internally) | keeps all queries off the public Internet |
| **TTL design** | 3600 s for stable records; **30–60 s for failover records** | long TTLs make failover ineffective |
| **Anycast** | several recursive resolvers share one address | simple client configuration, natural locality and redundancy |
| **DNSSEC** | enabled for external zones; internally, weigh the management cost | a broken validation chain means resolution fails everywhere |
| **Encryption** | DoT/DoH for client egress | watch for the side effect of bypassing enterprise policy |
| **Monitoring** | query volume, NXDOMAIN rate, P95 response time, cache hit ratio | a DNS problem first shows up as "everything is slow" |

<div class="zh" markdown="1">

| 设计项 | 建议 | 原因 |
|--------|------|------|
| **架构** | 内部权威 + 内部递归（转发到外部） | 分离内外信任边界 |
| **条件转发** | 按域转发（`corp.example.com` 内部解析） | 避免全部查询走公网 |
| **TTL 设计** | 稳定记录 3600 s；**故障切换类 30–60 s** | TTL 太长导致切换无效 |
| **Anycast** | 多个递归解析器用同一地址 | 客户端配置简单、天然就近/冗余 |
| **DNSSEC** | 对外域开启；内部视管理成本 | 验证链断 = 全域解析失败 |
| **加密** | DoT/DoH 用于终端出网 | 注意绕过企业策略的副作用 |
| **监控** | 查询量、NXDOMAIN 率、响应时间 P95、缓存命中率 | DNS 故障最先体现在"变慢" |

</div>

**DNS query-capacity worked example**: 20,000 terminals × 3,000 queries per person per day / 8 h ≈ **2,000 QPS** on average, with peaks of 5,000–8,000 QPS. **Size each recursive resolver at 5,000–10,000 QPS, and deploy at least two.**

<div class="zh" markdown="1">

**DNS 查询容量算例**：20,000 终端 × 每人每天 3,000 次查询 / 8 h ≈ **2,000 QPS** 平均，峰值可到 5,000–8,000 QPS。**每台递归解析器按 5,000–10,000 QPS 规划，至少 2 台。**

</div>

> ⚠️ **DNS is the most insidious single point of failure**: when it is 300 ms slow, every application in the company is 300 ms slow, and nobody suspects DNS. **So DNS belongs on the "P1 service list", with its own SLO and capacity dashboard.**

<div class="zh" markdown="1">

> ⚠️ **DNS 是"最隐蔽的单点"**：它慢 300 ms，全公司所有应用都慢 300 ms，但 nobody 会怀疑 DNS。**所以 DNS 必须进"P1 服务清单"，有独立 SLO 与容量看板。**

</div>

### Foundational Service Design: AAA · 基础服务设计：AAA

| Dimension | RADIUS | TACACS+ |
|------|--------|---------|
| Transport | UDP 1812/1813 (TCP/TLS also available) | **TCP 49** |
| Encryption scope | the password only | **the entire payload** |
| Authentication/authorisation | combined (single response) | **separated** (per-command authorisation) |
| Accounting | supported | supported (records at command level) |
| Typical use | **network access** (802.1X/VPN/wireless) | **device management** (CLI authorisation/audit) |
| Scale | high-concurrency access | operations logins (low volume) |

<div class="zh" markdown="1">

| 维度 | RADIUS | TACACS+ |
|------|--------|---------|
| 传输 | UDP 1812/1813（可用 TCP/TLS） | **TCP 49** |
| 加密范围 | 仅密码 | **整个负载** |
| 认证/授权 | 合并（一个响应） | **分离**（可逐条命令授权） |
| 计费 | 支持 | 支持（记录命令级） |
| 典型用途 | **网络接入**（802.1X/VPN/无线） | **设备管理**（CLI 授权/审计） |
| 规模 | 高并发接入 | 运维登录（量小） |

</div>

**Design points**:

<div class="zh" markdown="1">

**设计要点**：

</div>

- **Two servers plus a local fallback** (`aaa authentication login default group tacacs+ local`), with local accounts stored offline
- **Tiered command authorisation**: the NOC gets read-only show, engineers get read-write, automation accounts are restricted to a specific command set
- **Use accounting for audit**: who changed what, and when (together with syslog/NETCONF logs)
- **Timeouts and retries**: `timeout 5s, retries 2` — too long and logins hang, too short and a wobbling server is misread as a failure
- **Rehearse the behaviour when the AAA server is unreachable**: many incidents are "AAA died → nobody could log in → nobody could fix AAA"

<div class="zh" markdown="1">

- **两台服务器 + 本地回退**（`aaa authentication login default group tacacs+ local`），本地账号离线保管
- **命令授权分级**：NOC 只读 show、工程师读写、自动化账号限制在特定命令集
- **计费用于审计**：谁在什么时候改了什么（配合 syslog/NETCONF 日志）
- **超时与重试**：`timeout 5s, retries 2` —— 太长会让登录卡死，太短会在服务器抖动时误判为故障
- **AAA 服务器不可达时的行为要演练**：很多事故是"AAA 挂了 → 没人能登录 → 无法修 AAA"

</div>

### Foundational Service Design: IPAM and PKI · 基础服务设计：IPAM 与 PKI

| Service | Key requirement | Common failure |
|------|---------|---------|
| **IPAM** | bidirectional sync with DHCP/DNS/automation (SoT); manages IPv4 and IPv6 together | an Excel register → address conflicts and automation failures |
| **PKI/certificates** | validity management, automatic renewal, reachable CRL/OCSP, an intact trust chain | **one morning 802.1X fails estate-wide (an expired certificate)** |
| **Image/file service** | internal HTTP/SCP image distribution, local to each site | pulling images across the WAN during upgrades, with no time in the window |

<div class="zh" markdown="1">

| 服务 | 关键要求 | 常见失败 |
|------|---------|---------|
| **IPAM** | 与 DHCP/DNS/自动化（SoT）双向同步；IPv4+IPv6 同管 | Excel 台账 → 地址冲突、自动化失败 |
| **PKI/证书** | 有效期管理、自动续期、CRL/OCSP 可达、信任链完整 | **某天早上 802.1X 全网失败（证书过期）** |
| **镜像/文件服务** | 内网 HTTP/SCP 分发镜像，按站点就近 | 升级时跨 WAN 拖镜像，窗口不够 |

</div>

**Certificate expiry is a predictable time bomb**: every certificate must have **90/30/7-day expiry alerts** and be on the change calendar. **This is the easiest item in operations to do and the easiest to forget.**

<div class="zh" markdown="1">

**证书到期是"可预测的定时炸弹"**：所有证书必须有**到期前 90/30/7 天告警**，并纳入变更日历。**这是运维里最容易做、最容易漏的一项。**

</div>

---

## Observability: From "Device Health" to "Service Health" · 可观测性：从"设备健康"到"业务健康"

### The Five Monitoring Layers (the Lower You Go, the Closer to the User) · 五个监控层次（越往下越接近用户）

| Layer | What is monitored | Typical metrics | Who looks at it |
|----|---------|---------|------|
| **L1 device health** | power/fans/temperature/CPU/memory/flash | 5-minute average CPU, temperature, PSU state | NOC |
| **L2 interfaces and links** | optical power, errors, CRC, up/down, utilisation, drops | RxPower, input errors, errors/discards | NOC |
| **L3 protocols and control plane** | neighbour state, route counts, STP topology, HA state | BGP Established, OSPF Full, STP changes | network engineers |
| **L4 service and end to end** | availability/latency/loss on critical business paths | IP SLA, synthetic transactions, SLA attainment | operations/business |
| **L5 user experience** | application response, VoIP MOS, Wi-Fi experience | MOS, join success rate, application RTT | the business side |

<div class="zh" markdown="1">

| 层 | 监控什么 | 典型指标 | 谁看 |
|----|---------|---------|------|
| **L1 设备健康** | 电源/风扇/温度/CPU/内存/闪存 | CPU 5 分钟均值、温度、PSU 状态 | NOC |
| **L2 接口与链路** | 光功率、误码、CRC、up/down、利用率、丢包 | RxPower、input errors、errors/discards | NOC |
| **L3 协议与控制面** | 邻居状态、路由条目、STP 拓扑、HA 状态 | BGP Established、OSPF Full、STP changes | 网络工程师 |
| **L4 服务与端到端** | 关键业务路径的可用性/延迟/丢包 | IP SLA、合成事务、SLA 达成率 | 运维/业务 |
| **L5 用户体验** | 应用响应、VoIP MOS、Wi-Fi 体验 | MOS、join 成功率、应用 RTT | 业务方 |

</div>

> ⚠️ **Doing only L1/L2 is "device-view monitoring"**: every device is green while users are still complaining. **In a CCDE design question, "how do you prove the design is usable" has to land on L4/L5.**

<div class="zh" markdown="1">

> ⚠️ **只做 L1/L2 是"设备视角监控"**：设备全绿，用户仍然可能在投诉。**CCDE 的设计题里，"如何证明方案可用"必须落到 L4/L5。**

</div>

### SLI / SLO: Defining "Good" as Something Measurable · SLI / SLO：把"好"定义成可测量的

| Service | SLI (metric) | SLO (target) | How it is measured |
|------|-----------|-----------|---------|
| HQ–branch connectivity | loss, RTT | loss <0.1%, RTT <30 ms (P95) | IP SLA / telemetry |
| Voice quality | MOS, jitter, loss | MOS ≥4.0, jitter <30 ms | voice gateway/VoIP probes |
| Wireless access | association success rate, authentication delay | ≥99%, authentication <2 s | wireless controller statistics |
| Internet egress | availability, DNS resolution delay | 99.9%, <100 ms | synthetic probes |
| Change success rate | share of changes that cause no incident | ≥95% | ITSM data |

<div class="zh" markdown="1">

| 业务 | SLI（指标） | SLO（目标） | 测量方式 |
|------|-----------|-----------|---------|
| 总部—分支连通 | 丢包率、RTT | 丢包 <0.1%，RTT <30 ms（P95） | IP SLA / 遥测 |
| 语音质量 | MOS、抖动、丢包 | MOS ≥4.0，抖动 <30 ms | 语音网关/VoIP 探针 |
| 无线接入 | 关联成功率、认证时延 | ≥99%，认证 <2 s | 无线控制器统计 |
| 互联网出口 | 可用性、DNS 解析时延 | 99.9%，<100 ms | 合成探测 |
| 变更成功率 | 未引发事故的变更比例 | ≥95% | ITSM 数据 |

</div>

**The purpose of an SLO is not performance appraisal; it is having one sentence to answer "is the network good?" when someone asks.**

<div class="zh" markdown="1">

**SLO 的作用不是考核，而是"当有人问'网络好不好'时有一句话能回答"。**

</div>

### Designing IP SLA / Synthetic Probes · IP SLA / 合成探测的设计

| Probe type | What it measures | Frequency | Caveats |
|---------|-------|------|------|
| ICMP Echo | reachability, RTT, loss | 30–60 s | the lightest, but distorted when ICMP is rate-limited |
| UDP Jitter | jitter, one-way delay, loss | 60 s | the closest to the voice experience |
| TCP Connect | port reachability, handshake delay | 1–5 min | catches "pings but the port is closed" |
| HTTP/DNS | application-layer delay | 1–5 min | must cover the real DNS/URL |
| **Multi-path probing** | every WAN link plus every SD-WAN tunnel | 30 s | used for path selection (see Chapter 17) |

<div class="zh" markdown="1">

| 探测类型 | 测什么 | 频率 | 注意 |
|---------|-------|------|------|
| ICMP Echo | 连通性、RTT、丢包 | 30–60 s | 最轻量，但被 ICMP 限速时失真 |
| UDP Jitter | 抖动、单向延迟、丢包 | 60 s | 最接近语音体验 |
| TCP Connect | 端口可达、握手时延 | 1–5 min | 能发现"ping 通但端口不通" |
| HTTP/DNS | 应用层时延 | 1–5 min | 需覆盖真实 DNS/URL |
| **多路径探测** | 每个 WAN 链路 + 每条 SD-WAN 隧道 | 30 s | 用于路径选择（见第 17 章） |

</div>

**The scale budget**: 200 sites × 4 probes each × every 30 s = **about 27 per second**, which is negligible for the devices; but **the results need somewhere to live** (otherwise they are just local counters).

<div class="zh" markdown="1">

**规模账**：200 个站点 × 每个站点 4 条探测 × 每 30 s = **约 27 次/秒**，对设备几乎无负担；但**结果必须有地方存**（否则只是一堆本地计数）。

</div>

### Monitoring Platform Architecture (A Deployable Layering) · 监控平台架构（一个可落地的分层）

```
collection: SNMP poller / gNMI collector / syslog receiver / flow collector / IP SLA
   ↓ (each layer scales horizontally, partitioned by site or device)
storage:    time-series DB (metrics, 7–30 days raw + 1 year downsampled)
            log DB (events, 30–90 days, hot/cold tiers)
            flow DB (traffic, 7–30 days, retained 1 year after aggregation)
   ↓
analysis:   thresholds + baselines + correlation (topology-aware)
   ↓
presentation: dashboards (role-based: NOC / engineering / business) + alerting (severity + escalation path) + reports (capacity/compliance)
```

<div class="zh" markdown="1">

```
采集层：SNMP poller / gNMI collector / syslog receiver / flow collector / IP SLA
   ↓（各层水平扩展，按站点或设备分区）
存储层：时序库（指标，7–30 天原始 + 1 年降采样）
        日志库（事件，30–90 天，热/冷分层）
        流库（流量，7–30 天，聚合后保留 1 年）
   ↓
分析层：阈值 + 基线 + 关联（拓扑感知）
   ↓
呈现层：看板（角色化：NOC / 工程 / 业务）+ 告警（分级 + 升级路径）+ 报表（容量/合规）
```

</div>

| Design item | Recommendation | Rationale |
|--------|------|------|
| **Collector HA** | 2 per region, active/standby or load-shared | a dead collector means you are blind |
| **Collector proximity** | collectors close to the devices they poll | polling across the WAN wastes bandwidth |
| **Data retention** | 7–30 days raw, 1 year at 5-minute granularity | troubleshooting needs raw data, trends need the long view |
| **Clock** | NTP/PTP across the whole chain | otherwise nothing correlates |
| **Separate configuration backup** | do not share a host with monitoring | a failure would take out both |

<div class="zh" markdown="1">

| 设计项 | 建议 | 原因 |
|--------|------|------|
| **采集器 HA** | 每区 2 台，主备或分担 | 采集器挂了就"瞎" |
| **采集与设备就近** | 采集器靠近被采设备 | 跨 WAN 轮询浪费带宽 |
| **数据保留** | 原始 7–30 天、5 分钟粒度 1 年 | 排障要原始，趋势要长期 |
| **时钟** | 全链路 NTP/PTP | 否则无法关联 |
| **配置备份独立** | 不要与监控共用一台机器 | 故障时两者都不可用 |

</div>

**Storage estimation formula**:

<div class="zh" markdown="1">

**存储估算公式**：

</div>

```
storage ≈ number of metrics × collection frequency × bytes per point (about 2–16 B compressed) × retention in seconds × number of replicas
example: 50,000 metrics × every 60 s × 4 B × 30 days × 2 replicas
  = 50,000 × (86400/60) × 4 × 30 × 2 ≈ 17 GB (compressed; 20–50 GB in practice)
logs: 500 devices × 2,000 messages/day × 500 B ≈ 0.5 GB/day → 90 days ≈ 45 GB (×2–3 with indexes)
```

<div class="zh" markdown="1">

```
存储 ≈ 指标数 × 采集频率 × 每点字节（约 2–16 B 压缩后） × 保留秒数 × 副本数
例：50,000 指标 × 每 60 s × 4 B × 30 天 × 2 副本
  = 50,000 × (86400/60) × 4 × 30 × 2 ≈ 17 GB（压缩后，实际 20–50 GB）
日志：500 台 × 2,000 条/天 × 500 B ≈ 0.5 GB/天 → 90 天 ≈ 45 GB（含索引 ×2–3）
```

</div>

> 💡 **None of it looks large** — the real cost is in **indexing and query performance**, not in raw volume. So "retention policy + archiving + indexing only key fields" beats "buy a bigger disk".

<div class="zh" markdown="1">

> 💡 **看起来都不大** —— 真正的成本在**索引与查询性能**，不在原始容量。所以"保留策略 + 归档 + 只对关键字段建索引"比"买更大磁盘"更有效。

</div>

### Alert Governance (The Make-or-Break of the Platform) · 告警治理（平台成败的关键）

| Problem | Symptom | Fix |
|------|------|------|
| **Alert storm** | one core failure produces 5,000 alerts | **parent-child suppression** (topology-aware) plus root-cause aggregation |
| **Alert fatigue** | the team mutes the notifications | severity tiers, keeping only alerts "someone will act on" |
| **Flapping alerts** | a port going up/down repeatedly notifies every time | flap detection (alert only after N times in M minutes) |
| **Unreasonable thresholds** | 80% CPU alerts every day | per-role thresholds plus baselines (P95) instead of fixed values |
| **No handling guidance** | an alert arrives and nobody knows what to do | **every alert must carry a Runbook link** |
| **Maintenance windows not silenced** | a planned change fires a flood of alerts | integrate with ITSM and silence automatically |

<div class="zh" markdown="1">

| 问题 | 症状 | 解决 |
|------|------|------|
| **告警风暴** | 一次核心故障产生 5,000 条告警 | **父子抑制**（拓扑感知）+ 根因聚合 |
| **告警疲劳** | 团队把通知静音 | 分级 + 只保留"会有人动作"的告警 |
| **抖动告警** | 端口频繁 up/down 反复通知 | flap 检测（N 次/M 分钟才告警） |
| **阈值不合理** | 80% CPU 天天报 | 按角色设阈值 + 用基线（P95）替代固定值 |
| **无处置指引** | 收到告警不知道做什么 | **每条告警必须挂 Runbook 链接** |
| **维护窗口未静默** | 计划变更触发大量告警 | 与 ITSM 打通，自动静默 |

</div>

**Alert severity (worth writing straight into the operations manual)**:

<div class="zh" markdown="1">

**告警分级（建议直接写进运维手册）**：

</div>

| Level | Criterion | Notification | Response |
|------|------|---------|------|
| **P1** | service outage/core fully down | phone + SMS + wallboard | respond within 15 minutes, escalate immediately |
| **P2** | redundancy lost/severe performance degradation | SMS + IM | 30 minutes |
| **P3** | single-point failure with redundancy available | IM/ticket | next business day |
| **P4** | trend/capacity/compliance | daily report | scheduled |

<div class="zh" markdown="1">

| 级别 | 判据 | 通知方式 | 响应 |
|------|------|---------|------|
| **P1** | 业务中断/核心全断 | 电话 + 短信 + 大屏 | 15 分钟内响应，立即升级 |
| **P2** | 冗余失效/性能严重下降 | 短信 + IM | 30 分钟 |
| **P3** | 单点故障但有冗余 | IM/工单 | 工作日处理 |
| **P4** | 趋势/容量/合规 | 日报 | 排期 |

</div>

### Capacity and Performance Management · 容量与性能管理

| Metric | What to look at | Pitfall |
|------|-------|------|
| **Interface utilisation** | the 5-minute P95, not the average | averages hide peaks; **the P95 peak is the basis for congestion** |
| **PPS** | small-packet attacks/voice hit the pps ceiling first | 1 Gbps line rate with 64 B packets = 1.488 Mpps |
| **Buffer/drops** | egress queue drops, `output drops` | any drop means congestion already happened |
| **Sessions/table entries** | NAT, ARP/ND, MAC, flow tables | a full table means new sessions fail (the hardest to diagnose) |
| **Control plane** | CPU, processes, route-table growth rate | route-table growth is the silent capacity problem |
| **Optical layer** | Rx optical power, error rate | degradation is gradual: **alert on trend, not threshold** |

<div class="zh" markdown="1">

| 指标 | 看什么 | 缺陷 |
|------|-------|------|
| **接口利用率** | 5 分钟 P95（不是平均值） | 平均值掩盖峰值；**95 峰值才是拥塞依据** |
| **PPS** | 小包攻击/语音场景下先撞 pps 上限 | 1G 线速 64 B 包 = 1.488 Mpps |
| **缓冲/丢包** | 出口队列丢弃、`output drops` | 有丢包就说明拥塞已发生 |
| **会话/表项** | NAT、ARP/ND、MAC、流表 | 表满 = 新增业务失败（最难查） |
| **控制面** | CPU、进程、路由条目增速 | 路由表增长是"沉默的容量问题" |
| **光层** | Rx 光功率、误码 | 劣化是渐进的，**要按趋势告警而非阈值** |

</div>

**Two capacity-planning actions**:

<div class="zh" markdown="1">

**容量规划的两个动作**：

</div>

1. **A quarterly trend report**: 90-day P95 and growth slope per link/site, predicting "when will we hit 70%"
2. **Bottleneck ranking**: a two-dimensional ranking of "utilisation × business importance" to produce the upgrade priority (rather than whoever shouts loudest)

<div class="zh" markdown="1">

1. **季度趋势报告**：按链路/站点输出 90 天 P95 与增长斜率，预测"何时到 70%"
2. **瓶颈排序**：把"利用率 × 业务重要性"做二维排序，得到扩容优先级（而不是按谁叫得响）

</div>

### Assets, Software Lifecycle and Compliance · 资产、软件生命周期与合规

| Item | Frequency | Output |
|----|------|------|
| Software version inventory (including EoL/EoS) | quarterly | upgrade plan, risk register |
| Hardware warranty/spares | quarterly | spares gap (key question: **can an RMA replacement ZTP itself into service**) |
| Configuration baseline compliance | daily | drift report (see Chapter 12) |
| Account and privilege review | quarterly | removal of leavers/excess rights |
| Certificate and licence expiry | monthly | 90/30/7-day alerts |
| Log retention and audit | per compliance requirement | PCI/HIPAA typically 1 year |

<div class="zh" markdown="1">

| 项 | 频率 | 输出 |
|----|------|------|
| 软件版本清单（含 EoL/EoS） | 季度 | 升级计划、风险清单 |
| 硬件保修/备件 | 季度 | 备件缺口（关键：**RMA 换机能否 ZTP 自动上线**） |
| 配置基线合规 | 每日 | 漂移报告（见第 12 章） |
| 账号与权限复核 | 季度 | 离职/越权清理 |
| 证书与许可到期 | 月度 | 90/30/7 天告警 |
| 日志保留与审计 | 按合规要求 | PCI/HIPAA 等通常 1 年 |

</div>

> 💡 **The dividing line of operations maturity**: are these reports **generated automatically and actually read**, or **assembled by hand when needed**? The former is an operating model; the latter is a fire brigade.

<div class="zh" markdown="1">

> 💡 **运维成熟度的分水岭**：这些报表是"**自动生成且有人看**"，还是"**需要时手工凑**"。前者是运营体系，后者是救火队。

</div>

---

## From Design to Operations: The Eight Tables This Chapter Must Deliver · 从设计到运营：本章必须交付的 8 张表

If the design document contains only architecture diagrams and protocol choices, the operations team will inevitably fall back on "keeping it in someone's head" once they take over. **The deliverables of a services-and-management design should be tables, not diagrams.**

<div class="zh" markdown="1">

设计文档里如果只有架构图和协议选择，运维团队接手后一定会退回"靠人记"。**服务与管理设计的交付物应该是"表"，而不是"图"。**

</div>

| # | Deliverable | Content | Who uses it |
|---|-------|------|------|
| 1 | **IPv6 address allocation table** | site prefixes, subnet plan, purpose and gateway of every subnet, P2P/loopback blocks | engineering + automation (SoT input) |
| 2 | **DSCP marking table** | 11 classes → DSCP → queue → bandwidth share → boundary action | engineering + monitoring |
| 3 | **Trust boundary diagram** | whether each device/port type "trusts marking", how tunnel outer headers are handled | engineering + audit |
| 4 | **Service tiering table (P1–P4)** | blast radius, RTO/RPO, owner and fallback for each service | NOC + management |
| 5 | **Collection inventory** | what is collected per device type, frequency, protocol, sampling ratio, retention | monitoring team |
| 6 | **Alert catalogue** | alert name + severity + trigger condition + suppression rule + Runbook link | NOC |
| 7 | **Management channel matrix** | site × channel (in-band/OOB/console/LTE) × verification date | operations |
| 8 | **Capacity baseline table** | 90-day P95 per link/site + growth slope + threshold | planning |

<div class="zh" markdown="1">

| # | 交付物 | 内容 | 谁用 |
|---|-------|------|------|
| 1 | **IPv6 地址分配表** | 站点前缀、子网规划、每个子网的用途与网关、P2P/环回段 | 工程 + 自动化（SoT 输入） |
| 2 | **DSCP 标记表** | 11 类 → DSCP → 队列 → 带宽比例 → 边界动作 | 工程 + 监控 |
| 3 | **信任边界图** | 每类设备/端口"是否信任标记"，隧道外层处理方式 | 工程 + 审计 |
| 4 | **服务分级表（P1–P4）** | 每个服务的影响面、RTO/RPO、负责人、回退手段 | NOC + 管理层 |
| 5 | **采集清单** | 每类设备采什么、频率、协议、采样比、保留期 | 监控团队 |
| 6 | **告警目录** | 告警名 + 级别 + 触发条件 + 抑制规则 + Runbook 链接 | NOC |
| 7 | **管理通道矩阵** | 站点 × 通道（带内/OOB/Console/LTE）× 验证日期 | 运维 |
| 8 | **容量基线表** | 各链路/站点 90 天 P95 + 增长斜率 + 阈值 | 规划 |

</div>

### Failure Drill Checklist (A Capability That Is Never Rehearsed Does Not Exist) · 故障演练清单（没演练的能力等于不存在）

| Drill | Method | Pass criterion |
|------|------|---------|
| **All service links down** | shut every service uplink, leaving only OOB | can log in over OOB and localise within 15 minutes |
| **AAA server unreachable** | stop RADIUS/TACACS+ | local fallback accounts work; an emergency SSID exists |
| **All NTP sources fail** | stop the internal NTP | alert fires; no authentication failures within 24 hours |
| **Collector down** | stop the primary collector | the backup takes over; no monitoring blind spot longer than 5 minutes |
| **Log storm** | induce port flapping deliberately | device CPU <60%, the log server loses no critical events |
| **Single DHCP server failure** | stop one server | terminal renewal failure rate <1%, no manual intervention |
| **Certificate expiry** | simulate with a test certificate | expiry alerts fire correctly at 90/30/7 days |
| **QoS congestion** | inject 110% of traffic | voice MOS ≥4.0; critical applications uninterrupted |
| **Dual-stack fallback** | shut the IPv6 egress | terminals fall back to IPv4 automatically (no long stall) |

<div class="zh" markdown="1">

| 演练 | 方法 | 通过标准 |
|------|------|---------|
| **业务链路全断** | 关掉所有业务上联，只留 OOB | 15 分钟内能通过 OOB 登录并定位 |
| **AAA 服务器不可达** | 停 RADIUS/TACACS+ | 本地回退账号可登录；无线有应急 SSID |
| **NTP 源全失效** | 停内网 NTP | 告警触发；24 小时内无认证类故障 |
| **采集器宕机** | 停主采集器 | 备采集器接管；无监控盲区超过 5 分钟 |
| **日志风暴** | 人为制造端口 flap | 设备 CPU <60%，日志服务器不丢关键事件 |
| **DHCP 单台失效** | 停一台服务器 | 终端续租失败率 <1%，无人工介入 |
| **证书过期** | 用测试证书模拟 | 到期告警在 90/30/7 天正确触发 |
| **QoS 拥塞** | 注入 110% 流量 | 语音 MOS ≥4.0；关键业务不中断 |
| **双栈回退** | 关闭 IPv6 出口 | 终端自动回退 IPv4（无长时间卡顿） |

</div>

> 💡 **The value of a drill is not proving the system is robust but finding the gaps in the Runbook.** After every drill the Runbook and the service tiering table must be updated — otherwise the same people fight the next fire from memory.

<div class="zh" markdown="1">

> 💡 **演练的价值不是"证明系统健壮"，而是"发现 Runbook 里的空白"**。每次演练后必须更新 Runbook 与服务分级表 —— 否则下一次还是同一批人凭记忆救火。

</div>

---

## Field Cases (Twelve Real Scenarios) · 实战案例（12 个真实场景）

### 🔥 Case 1: Splitting a /64 into /72s to Save Addresses — Three Months Later "Some Staff Have No Network" · 🔥 案例一：把 /64 切成 /72 省地址，三个月后"部分员工没网"

**Symptom**: after IPv6 went live in a new office building, Windows worked, but some Android and IoT devices got no address; within the same VLAN some machines could reach the Internet and others could not.

<div class="zh" markdown="1">

**现象**：新办公楼 IPv6 上线后，Windows 正常，部分 Android 与 IoT 设备拿不到地址；同一 VLAN 内有的机器能上网、有的不能。

</div>

**Investigation**: RA captures showed a `/72` prefix. Windows got an address over DHCPv6 (M=1); Android supports only SLAAC → no address; IoT devices used SLAAC + EUI-64 → generating a 64-bit IID while the prefix left only 8 usable bits of the 72 → the stack assembled an invalid address and discarded it.

<div class="zh" markdown="1">

**排查**：抓 RA 发现前缀 `/72`；Windows 用 DHCPv6 拿到了地址（M=1），Android 只支持 SLAAC → 无地址；IoT 用 SLAAC + EUI-64 → 生成 64 位 IID，但前缀只有 72 位中的 8 位可用 → 实际拼出非法地址被丢弃。

</div>

**Root cause**: **SLAAC and ND both assume a /64 subnet**; a non-/64 prefix simply fails on most terminal stacks.

<div class="zh" markdown="1">

**根因**：**SLAAC 与 ND 都假设子网为 /64**，非 /64 前缀在多数终端栈上直接失效。

</div>

**What to do instead**:
- Pin every "user/VLAN segment" at /64; **never subdivide the subnet**
- Any "saving" must happen at the **upstream aggregation layer** (/48 → /56 allocation granularity)
- Make "**every LAN prefix length = 64**" a checklist item in design reviews

<div class="zh" markdown="1">

**正确做法**：
- 任何"用户/VLAN 网段"固定 /64，**不做子网切分**
- 需要"节省"只能节省在**上游汇总层**（/48 → /56 分配粒度）
- 设计评审时把"**所有 LAN 前缀长度 = 64**"写成检查项

</div>

### 🔥 Case 2: The Security Policy "Blocks Ping", So IPv6 Can Log In but Cannot Transfer Files · 🔥 案例二：安全策略"禁止 ping"，结果 IPv6 能登录不能传文件

**Symptom**: after the IPv6 rollout SSH connected, but `scp`, large HTTPS downloads and database queries returning large result sets all hung; IPv4 was perfectly fine.

<div class="zh" markdown="1">

**现象**：IPv6 上线后 SSH 能连上，但 `scp`、HTTPS 大文件、数据库查询大结果集全部卡死；IPv4 完全正常。

</div>

**Investigation**: `ping -6 -s 1452` failed while `ping -6 -s 1200` succeeded → an MTU problem. Captures showed a mid-path tunnel with an MTU of 1400; the device returned ICMPv6 Type 2, but **the firewall's global policy blocked all ICMP**, so the source never received the PTB and kept retransmitting 1500-byte packets.

<div class="zh" markdown="1">

**排查**：`ping -6 -s 1452` 失败，`ping -6 -s 1200` 成功 → MTU 问题；抓包看到中间隧道 MTU 1400，设备回 ICMPv6 Type 2，但**防火墙统一策略把 ICMP 全禁**，源端收不到 PTB，一直重传 1500 字节包。

</div>

**Root cause**: IPv6 **routers do not fragment**, so PMTUD is the only mechanism; dropping ICMPv6 Type 2 creates a black hole.

<div class="zh" markdown="1">

**根因**：IPv6 **路由器不分片**，PMTUD 是唯一机制；ICMPv6 Type 2 被丢 = 黑洞。

</div>

**What to do instead**:
- Permit ICMPv6 **Types 1/2/3/4 and 133–137** in the firewall (rate limiting is acceptable)
- Plan tunnel MTUs consistently (inner 1400/1450) and configure MSS clamping on the server side
- Acceptance cases must include "large packets" (>1400 B), not just a 32-byte ping

<div class="zh" markdown="1">

**正确做法**：
- 防火墙放行 ICMPv6 **Type 1/2/3/4 与 133–137**（可限速）
- 隧道场景统一规划 MTU（内层 1400/1450），并在服务器侧配 MSS clamping
- 验收用例必须包含"大包"（>1400 B）而非只 ping 32 字节

</div>

### 🔥 Case 3: After Dual Stack, "Web Pages Are Sometimes Fast, Sometimes Slow" — Because IPv6 Goes All the Way Around the World · 🔥 案例三：双栈上线后"网页时快时慢"，原因是 IPv6 绕地球一圈

**Symptom**: after the dual-stack migration, average load time for internal applications rose from 1.2 s to 3–8 s and was unstable; disabling IPv6 on the terminal restored it immediately.

<div class="zh" markdown="1">

**现象**：双栈改造后，访问内网应用平均加载时间从 1.2 s 涨到 3–8 s，且不稳定；关掉终端 IPv6 立刻恢复。

</div>

**Investigation**: terminals received a GUA from the RA and preferred IPv6 (RFC 6724); but the only IPv6 route was **a tunnel from headquarters down to the branch** (RTT 120 ms), while IPv4 was local and direct (RTT 3 ms). On top of that, the RDNSS in the RA pointed at a branch DNS with no AAAA records → every lookup timed out on AAAA before falling back to A.

<div class="zh" markdown="1">

**排查**：终端从 RA 拿到 GUA 并优先 IPv6（RFC 6724）；但 IPv6 路由只有一条**经总部再到分支的隧道**（RTT 120 ms），而 IPv4 是本地直连（RTT 3 ms）。同时 RA 里的 RDNSS 指向的分支 DNS 没有 AAAA 记录 → 每次先 AAAA 超时再回退 A。

</div>

**Root cause**: **dual stack delivered "protocol reachability" but not "path parity" or "DNS consistency"**.

<div class="zh" markdown="1">

**根因**：**双栈只做了"协议可达"，没做"路径对等"与"DNS 一致"**。

</div>

**What to do instead**:
- Verify **path-quality parity before go-live** (RTT/loss difference <20%)
- Keep egress local: IPv6 and IPv4 at the branch must follow the same egress policy
- DNS must return both A and AAAA, with RDNSS pointing at a usable resolver
- Phase it: publish AAAA only on the internal core first, observe, then roll out network-wide

<div class="zh" markdown="1">

**正确做法**：
- 双栈上线前做**路径质量对等验证**（RTT/丢包差异 <20%）
- 就近出口：分支的 IPv6 与 IPv4 走同一出口策略
- DNS 必须同时返回 A 与 AAAA，且 RDNSS 指向可用解析器
- 分阶段：先只在内网核心开 AAAA，观察后再全网

</div>

### 🔥 Case 4: A User Marks Their Traffic EF and Voice Is Starved Out at Busy Times · 🔥 案例四：用户把流量标成 EF，忙时语音被自己挤死

**Symptom**: poor voice quality in a new office area (MOS 3.2) with only 55% bandwidth utilisation, and the QoS configuration looked completely correct.

<div class="zh" markdown="1">

**现象**：新办公区语音质量差（MOS 3.2），带宽利用率仅 55%，QoS 配置看起来完全正确。

</div>

**Investigation**: the access switch had `mls qos trust dscp` on every port (including PC ports). One department installed a P2P tool that marks its traffic EF by default; the LLQ priority had no policer → the EF class consumed its full 33% ceiling, voice RTP competed with P2P in the same queue → jitter spiked to 80 ms.

<div class="zh" markdown="1">

**排查**：接入交换机对所有端口 `mls qos trust dscp`（含 PC 口）。某部门装了 P2P 工具，默认把 P2P 标为 EF；LLQ 的 priority 没有 policer → EF 类吃满 33% 上限，语音 RTP 与 P2P 在同一队列竞争 → 抖动飙到 80 ms。

</div>

**Root cause**: **the trust boundary was placed on user ports**, and the LLQ had no policer.

<div class="zh" markdown="1">

**根因**：**信任边界放在了用户端口**，且 LLQ 没有限速。

</div>

**What to do instead**:
- `no mls qos trust` on PC ports (re-mark to BE) or classify with NBAR; trust only phone ports
- LLQ must carry a `police` statement (voice bandwidth sized from concurrency, excess downgraded or dropped)
- Monitor the "EF class share" and alert on a sudden rise (itself a signal of attack or looping)

<div class="zh" markdown="1">

**正确做法**：
- PC 口 `no mls qos trust`（重标 BE）或 NBAR 分类；只有话机口 trust
- LLQ 必须配 `police`（如语音按并发算出带宽，超出降级或丢）
- 监控"EF 类占比"，突增即告警（这本身就是攻击/环回的信号）

</div>

### 🔥 Case 5: A Layer 2 Loop Killed Voice While "the Queue Configuration Was Correct" · 🔥 案例五：一次二层环回把语音打死，而"队列配置没错"

**Symptom**: a floor's wiring closet was mis-patched into a loop, producing a broadcast storm during STP convergence; voice was down for 3 minutes while other applications were "just slow".

<div class="zh" markdown="1">

**现象**：某楼层配线间误接成环，STP 收敛期间广播风暴；语音全断 3 分钟，其他业务"只是慢"。

</div>

**Investigation**: `show policy-map interface` showed the EF class dropping large volumes above the policer. Did the storm cause phones to re-mark broadcast packets as EF? No — the real cause was that **the storm drove the uplink to 100%**, LLQ's scheduling opportunities were crowded out by the flood of punted/broadcast traffic, and the policer dropped voice together with the "fake EF".

<div class="zh" markdown="1">

**排查**：`show policy-map interface` 显示 EF 类超出 policer 大量丢弃；风暴期间大量广播包被话机重标为 EF？不是 —— 真正原因是**风暴把上行链路打到 100%**，LLQ 的调度机会被海量 punt/广播挤占，加上 policer 把语音和"伪装的 EF"一起丢。

</div>

**Root cause**: **QoS has limited effect under sustained overload** (see roadmap item 3); the real defence is **storm control + loop detection + BPDU Guard**.

<div class="zh" markdown="1">

**根因**：**QoS 在持续过载时作用有限**（见导读第 3 条）；真正的防线是**风暴控制 + 环回检测 + BPDU Guard**。

</div>

**What to do instead**:
- Enable storm control (broadcast/multicast/unknown unicast) and BPDU Guard at the access layer
- QoS guarantees only "relative priority under congestion"; it is not an overload rescue mechanism
- Correlate "EF class drops" with "broadcast rate spikes" in alerting to localise Layer 2 problems fast

<div class="zh" markdown="1">

**正确做法**：
- 接入层开启 storm-control（广播/组播/未知单播）与 BPDU Guard
- QoS 只保证"拥塞时相对优先"，不作为"过载救援"
- 告警把"EF 类丢包"与"广播速率突增"关联，快速定位到二层问题

</div>

### 🔥 Case 6: Voice Degrades Across the WAN Because the Outer IPSec DSCP Is 0 · 🔥 案例六：跨 WAN 语音变差，因为 IPSec 外层 DSCP 是 0

**Symptom**: HQ–branch voice runs over an IPsec tunnel; the egress LLQ statistics say "the voice queue is almost empty", yet users complain of broken audio.

<div class="zh" markdown="1">

**现象**：总部—分支语音走 IPsec 隧道，出口 LLQ 统计"语音队列几乎为 0"，但用户投诉语音断续。

</div>

**Investigation**: capturing the outer ESP packets showed a ToS field of 0. The branch egress encrypted the inner EF marking **without copying it to the outer header**; the carrier network could not see the priority and treated all ESP as BE; under congestion voice was dropped at random.

<div class="zh" markdown="1">

**排查**：抓外层 ESP 包，ToS 字段 = 0。分支出口把内层 EF 加密后**没有复制到外层**；中间运营商网络看不到优先级，把 ESP 全部当 BE；拥塞时语音被随机丢弃。

</div>

**Root cause**: **encryption hides the inner marking**, so the carrier can only see the outer header.

<div class="zh" markdown="1">

**根因**：**加密隐藏了内层标记**，运营商只能看外层。

</div>

**What to do instead**:
- Configure outer DSCP copying/mapping at the tunnel endpoints (IPsec `qos pre-classify`, SD-WAN per-tunnel QoS)
- Confirm with the carrier how many classes it recognises (often only 3–6)
- Acceptance: capture the outer packet to verify the ToS, and measure MOS under injected congestion

<div class="zh" markdown="1">

**正确做法**：
- 隧道端点配置外层 DSCP 复制/映射（IPsec `qos pre-classify`、SD-WAN per-tunnel QoS）
- 与运营商确认其能识别的类数（常只有 3–6 类）
- 验收：抓外层包验证 ToS；并在拥塞注入下测 MOS

</div>

### 🔥 Case 7: QoS Is Completely Ineffective Because Queues Are Configured Against the Physical Port on a Sub-Rate Link · 🔥 案例七：子速率链路按物理口配队列，QoS 完全失效

**Symptom**: the branch egress is a 1 Gbps physical port with a 200 Mbps carrier contract. LLQ and bandwidth guarantees were configured against 1 Gbps, yet voice is still poor at busy times and `output drops` reads 0.

<div class="zh" markdown="1">

**现象**：分支出口物理 1 Gbps，运营商合同 200 Mbps。分支按 1 Gbps 配了 LLQ + 带宽保证，但忙时语音仍差、`output drops` 为 0。

</div>

**Investigation**: the device itself never congests (a 48-hour peak of only 300 Mbps) — **the congestion happens carrier-side** at the 200 Mbps aggregation point; the device queues never actually queue, so there is no scheduling to speak of.

<div class="zh" markdown="1">

**排查**：设备侧从不拥塞（48 小时峰值仅 300 Mbps），**拥塞发生在运营商侧**的 200 Mbps 汇聚点；设备队列没有排队，自然也没有调度。

</div>

**Root cause**: **there is no shaping down to the contracted rate**, so the queues take effect in the wrong place.

<div class="zh" markdown="1">

**根因**：**没有整形到合同速率**，队列在错误的位置生效。

</div>

**What to do instead**:
- Use **HQoS** on the egress: a parent `shape 200m` (even 190m to leave headroom) with the class queues hanging under it as children
- Confirm CIR/PIR and burst parameters with the carrier
- Monitor the `shaping` queue depth and drops inside the port, not just physical interface utilisation

<div class="zh" markdown="1">

**正确做法**：
- 出口做 **HQoS**：父层 `shape 200m`（甚至 190m 留余量），子层再挂各类队列
- 与运营商确认 CIR/PIR 与突发参数
- 监控口内 `shaping` 的排队与丢弃，而不是只看物理口利用率

</div>

### 🔥 Case 8: A Full-Table SNMP Walk Makes the Core Router's BGP Flap · 🔥 案例八：SNMP 全表 walk，把核心路由器的 BGP 打抖

**Symptom**: every Wednesday morning (reporting job) the core's BGP neighbours flap and `%OSPF-5-ADJCHG` appears occasionally; CPU peaks at 78% while forwarding is unaffected.

<div class="zh" markdown="1">

**现象**：每周三上午（报表任务）核心 BGP 邻居抖动，`%OSPF-5-ADJCHG` 也偶发；CPU 峰值 78%，但转发正常。

</div>

**Investigation**: the monitoring platform walks `ifTable + ifXTable + ipRouteTable` on 500 devices every 5 minutes, and the reporting jobs all land in the same window → the management-plane process occupies the CPU for long stretches, Hello processing is delayed → neighbours time out.

<div class="zh" markdown="1">

**排查**：监控平台对 500 台设备每 5 分钟 walk `ifTable + ifXTable + ipRouteTable`；报表任务集中在同一时段 → 管理面进程长时间占 CPU，路由协议 Hello 处理延迟 → 邻居超时。

</div>

**Root cause**: **the collection design treats "full-table walk" as the default** and has no partitioning or phase staggering.

<div class="zh" markdown="1">

**根因**：**采集设计把"全表 walk"当成了默认做法**，且没有分区与错峰。

</div>

**What to do instead**:
- Fetch only the columns you need (`ifHCInOctets`, `ifHCOutOctets`, `ifOperStatus`); never walk the routing or ARP tables
- Partition collectors by site and stagger phases (different devices at different offsets, never all on the hour)
- Rate-limit SNMP on the device and protect the management plane with CoPP
- Use Trap/telemetry ON_CHANGE for routing-table changes instead of polling

<div class="zh" markdown="1">

**正确做法**：
- 只取需要的列（`ifHCInOctets`、`ifHCOutOctets`、`ifOperStatus`），禁止 walk 路由表/ARP 表
- 采集器分区（按站点），错峰（不同设备不同相位，不要整点齐发）
- 设备侧 SNMP 限速 + CoPP 保护管理面
- 路由表变化用 Trap/遥测 ON_CHANGE，不用轮询

</div>

### 🔥 Case 9: One Flapping Port Takes Down the Log Server and the Switch Together · 🔥 案例九：一个端口 flapping，把日志服务器和交换机一起拖垮

**Symptom**: overnight a port on an access switch goes up/down 200 times per second; switch CPU hits 95%, the log server's disk I/O saturates, the NMS loses alerts for 30 minutes, and every user on that switch is disconnected.

<div class="zh" markdown="1">

**现象**：凌晨某接入交换机端口以 200 次/秒 up/down，交换机 CPU 95%，日志服务器磁盘 IO 打满，NMS 丢告警 30 分钟；同时该交换机上的用户全部掉线。

</div>

**Investigation**: every port event triggers one syslog message plus one SNMP trap, and `logging console`/`logging monitor` were left at high severity → the management plane is crushed by its own logging.

<div class="zh" markdown="1">

**排查**：端口日志每条触发一次 syslog + SNMP trap，且配置了 `logging console`/`logging monitor` 高等级 → 管理面被日志本身压死。

</div>

**Root cause**: **logging has no rate limiting or suppression**, so the log channel becomes a fault amplifier.

<div class="zh" markdown="1">

**根因**：**日志没有限速与抑制**，日志通道成了故障放大器。

</div>

**What to do instead**:
- Device side: `logging rate-limit` (messages per second per category) plus a bounded `logging buffered`
- Disable high-severity console/monitor logging in production (keep only critical)
- Do flap detection in the NMS (N times within M minutes); a single down does not alert
- Rate-limit the log server per source (so one device cannot flood it)

<div class="zh" markdown="1">

**正确做法**：
- 设备侧 `logging rate-limit`（每类每秒条数）+ `logging buffered` 限制
- 关闭 console/monitor 的高等级日志（生产环境只留 critical）
- flap 检测在 NMS 侧做（N 次/M 分钟），单次 down 不告警
- 日志服务器按来源限速（防单设备刷爆）

</div>

### 🔥 Case 10: NTP Pointed at the Public Internet — One Egress Outage Sends the Whole Network Time-Travelling · 🔥 案例十：NTP 指向公网，出口一断全网"时间旅行"

**Symptom**: after two hours of egress maintenance, 802.1X fails en masse on wireless, log timestamps jump back and forth, and troubleshooting is misdirected (everyone suspects the recent change).

<div class="zh" markdown="1">

**现象**：出口链路维护 2 小时后，无线 802.1X 大量失败、日志时间戳前后乱跳，排障方向被误导（以为是新变更导致）。

</div>

**Investigation**: every device points NTP at `pool.ntp.org`; with the egress down the devices free-run their own clocks (roughly 1–5 s of drift per hour), and after recovery certificate validation windows are misaligned and logs cannot be correlated across devices.

<div class="zh" markdown="1">

**排查**：所有设备 NTP 指向 `pool.ntp.org`；出口断后设备靠自身时钟漂移（每小时约 1–5 s），恢复后证书校验窗口错位、日志跨设备无法对齐。

</div>

**Root cause**: **a foundational service depends on the external network**, with no internal hierarchy and no alerting.

<div class="zh" markdown="1">

**根因**：**基础服务依赖了外部网络**，且没有内部分层与告警。

</div>

**What to do instead**:
- Build an internal Stratum-1/2 hierarchy with at least two sources; devices point only at internal servers
- NTP authentication plus device-side ACLs (against amplification and spoofing)
- Alert on offset >1 s; confirm network-wide clock consistency before any change
- Put egress maintenance windows on the "affects foundational services" risk list

<div class="zh" markdown="1">

**正确做法**：
- 内部 Stratum-1/2 层级 + 至少 2 个源，设备只指向内网
- NTP 认证 + 设备侧 ACL（防放大与伪造）
- 偏移 >1 s 告警；变更前确认全网时钟一致
- 出口维护窗口纳入"影响基础服务"的风险清单

</div>

### 🔥 Case 11: At Morning Peak the Third Floor Cannot Get Addresses — the DHCP Relay Is a Single Point · 🔥 案例十一：早高峰三楼拿不到地址，DHCP 中继是单点

**Symptom**: around 08:50 every morning, 60–80 of the 300 people on the third floor fail to get an address (169.254 self-assignment); rebooting the PC fixes it, and by 09:10 everything recovers by itself.

<div class="zh" markdown="1">

**现象**：每早 8:50 左右，三楼 300 人中有 60–80 人拿不到地址（169.254 自配），重启电脑能好；9:10 后自然恢复。

</div>

**Investigation**: the third-floor gateway (a Layer 3 switch) relays DHCP to **a single** DHCP server; that server also handles 10,000 leases, and renewals cluster at morning peak (8-hour lease, everybody online before 09:00) → queue build-up and timeouts; `ip helper-address` lists only one target (no fallback if the primary fails or is overloaded).

<div class="zh" markdown="1">

**排查**：三楼网关（一台三层交换机）做 DHCP 中继指向**单台** DHCP 服务器；该服务器同时处理 10,000 个租约，早高峰续租集中（租期 8 h，全员 9 点前上线）→ 队列堆积 + 超时；中继 `ip helper-address` 只配了一个（主用宕机/过载时无回退）。

</div>

**Root cause**: **capacity and redundancy are both missing**: the lease design creates a renewal spike, the server is a single point, and the relay has a single target.

<div class="zh" markdown="1">

**根因**：**容量与冗余同时缺失**：租期设计导致续租尖峰、服务器单点、中继单目标。

</div>

**What to do instead**:
- Two DHCP servers (failover, or scope-based sharing) plus two relay targets
- Tier the leases (wired 12 h, wireless 4 h) and de-synchronise renewal spikes (randomised T1)
- Design morning-peak capacity from "500 requests per second instantaneously", not from the daily average
- Enable option 82 so you can later identify "who held which address"

<div class="zh" markdown="1">

**正确做法**：
- 两个 DHCP 服务器（故障转移或按网段分担）+ 中继配 2 个目标
- 租期分层（有线 12 h、无线 4 h），并把续租尖峰错开（随机化 T1）
- 早高峰容量以"瞬时 500 次/秒"为设计输入，而不是日均值
- 开启 option 82，事后能定位"谁拿了哪个地址"

</div>

### 🔥 Case 12: NetFlow Without Sampling on a 100G Egress Crashes the Collector and the Device Together · 🔥 案例十二：在 100G 出口开 NetFlow 不采样，采集器和设备同时崩

**Symptom**: NetFlow is enabled on the core egress for traffic analysis; ten minutes later the collector is at 100% CPU and dropping data; thirty minutes later the core router's management-plane CPU is at 85% and routing starts to flap.

<div class="zh" markdown="1">

**现象**：为做流量分析在核心出口开启 NetFlow，10 分钟后采集器 CPU 100%、丢数据；30 分钟后核心路由器管理面 CPU 85%，出现路由抖动。

</div>

**Investigation**: 60 Gbps peak at the egress with a 400 B average packet → about 18 Mpps → roughly 18M flows/s; at 80–120 B per export record that is **about 15 Gbps of export traffic**, all of it generated by the management plane.

<div class="zh" markdown="1">

**排查**：出口峰值 60 Gbps、平均包长 400 B → 约 18 Mpps → 约 18M 流/秒；每条 80–120 B 导出记录 → **约 15 Gbps 导出流量**，且全部由管理面生成。

</div>

**Root cause**: **no sampling and no capacity accounting**.

<div class="zh" markdown="1">

**根因**：**没有采样，也没有容量账**。

</div>

**What to do instead**:
- Set the sampling ratio from interface bandwidth (1:1000–1:4000 at 40G/100G) and record the ratio on the collector side
- Two export targets on a separate management segment, with rate limiting
- Compute "export bandwidth = flow rate × record size" first; if it exceeds 20% of the management link, adjust sampling
- For high-volume scenarios prefer **aggregated flows plus telemetry counters** over per-flow export

<div class="zh" markdown="1">

**正确做法**：
- 采样比按接口带宽设定（40G/100G 用 1:1000–1:4000），并在采集器侧记录采样比
- 导出目标 2 个、独立管理网段、限速
- 先算"导出带宽 = 流速率 × 记录大小"，超过管理链路 20% 就必须调采样
- 高流量场景优先用**聚合流 + 遥测计数器**，而不是逐流导出

</div>

---

## Design Trade-offs · 设计取舍

| Trade-off | Choose A and you get | Choose B and you get | CCDE decision basis |
|------|----------|----------|--------------|
| **A: dual stack / B: NAT64 single stack** | end-to-end, no translation, simple troubleshooting | no IPv4 on endpoints, simple address management | do applications hard-code IP literals or use IPsec; do endpoints speak v6 |
| **A: PI addresses / B: PA addresses** | no renumbering when you change ISP | smaller routing table, better carrier cooperation | are you multihomed; are you willing to run BGP |
| **A: /64 everywhere / B: /127 on point-to-point** | uniform, no exceptions | fewer subnets, mitigates subnet-router attacks | platform consistency vs security — prefer consistency |
| **A: dual stack in parallel / B: v4 first, then v6** | one migration, risk concentrated | lower risk, longer timeline | change windows and team maturity |
| **A: many classes / B: few classes** | finer business separation | maintainable and verifiable | **8–11 classes empirically**; more than that always distorts |
| **A: trust endpoints / B: re-mark at the boundary** | simple deployment | secure, resistant to abuse | are endpoints controlled; any PC port forces B |
| **A: strict LLQ / B: bandwidth guarantee** | lowest latency | fair, nothing starves | voice must use A, everything else B |
| **A: shaping / B: policing** | fewer drops, smoother output | simple, no buffering | shape on egress, police inbound or at the carrier |
| **A: in-band management / B: OOB** | zero cost | operable when broken | any unmanned sites; SLA requirements |
| **A: SNMP polling / B: telemetry** | universal, works on legacy gear | high precision, low overhead | hybrid: poll legacy devices, stream from new ones |
| **A: full flows / B: sampled flows** | exact | scalable | the sampling ratio must be recorded, or the data is unusable |
| **A: self-hosted monitoring / B: SaaS** | controllable, works on the internal network | no ops burden, cross-domain visibility | data compliance + independence during an outage |
| **A: single NMS / B: several stitched tools** | consistent experience | best of each tool | team size: small teams choose A |
| **A: centralized AAA / B: distributed + local fallback** | consistent policy | works when the network is down | **B is mandatory** (otherwise you cannot log in during an outage) |

<div class="zh" markdown="1">

| 取舍 | 选 A 得到 | 选 B 得到 | CCDE 判断依据 |
|------|----------|----------|--------------|
| **A: 双栈 / B: NAT64 单栈** | 端到端、无转换、排障简单 | 终端免 v4、地址管理简单 | 应用是否有字面 IP/IPsec；终端是否支持 v6 |
| **A: PI 地址 / B: PA 地址** | 换 ISP 不用重编址 | 路由表小、运营商配合度高 | 是否多宿主、是否愿意跑 BGP |
| **A: 全 64 子网 / B: P2P 用 127** | 统一、无例外 | 省子网、防子网路由攻击 | 平台一致性 vs 安全性，优先一致性 |
| **A: 双栈并行 / B: 先 v4 后 v6** | 一次改造、风险集中 | 风险小、周期长 | 变更窗口与团队熟练度 |
| **A: 类数多 / B: 类数少** | 业务区分细 | 可维护、可验证 | **经验值 8–11 类**，多了必失真 |
| **A: 信任终端 / B: 边界重标** | 部署简单 | 安全、抗滥用 | 终端是否受控；有 PC 口就必须 B |
| **A: 严格 LLQ / B: 带宽保证** | 延迟最低 | 公平、不会饿死 | 语音必须 A，其余用 B |
| **A: 整形 / B: 监管** | 少丢包、平滑 | 简单、省缓冲 | 出口用整形，入向/运营商用监管 |
| **A: 带内管理 / B: OOB** | 零成本 | 故障可运维 | 是否有无人站点、SLA 要求 |
| **A: SNMP 轮询 / B: 遥测** | 通用、老设备支持 | 精度高、开销低 | 混合：老设备轮询，新设备遥测 |
| **A: 全量流 / B: 采样流** | 精确 | 可扩展 | 采样比必须记录，否则数据不可用 |
| **A: 自建监控 / B: SaaS** | 可控、内网可用 | 免运维、跨域可视 | 数据合规 + 故障时的独立性 |
| **A: 单一 NMS / B: 多工具拼接** | 一致体验 | 各取所长 | 团队规模：小团队选 A |
| **A: 集中 AAA / B: 分布式 + 本地回退** | 一致策略 | 断网可用 | **必须 B**（否则断网无法登录） |

</div>

> 💡 **One universal criterion**: **in supporting systems, "still works when broken" always outranks "more elegant day to day".** The value of a supporting system shows up precisely during failures.

<div class="zh" markdown="1">

> 💡 **一条通用判据**：**在支撑系统里，"故障时还能工作"永远优先于"平时更优雅"。** 因为支撑系统的价值恰恰在故障时体现。

</div>

---

## Design Pitfalls · 设计缺陷

| # | Pitfall | Consequence | How to avoid |
|---|------|------|------|
| 1 | Dividing a /64 smaller "to save addresses" | SLAAC breaks, some endpoints have no network | pin every LAN at /64 |
| 2 | Blocking ICMP/ICMPv6 network-wide | PMTUD black holes, ND stops working | permit the essential types, rate-limit only |
| 3 | Dual stack with no path parity | applications are "sometimes fast, sometimes slow" — worse than v4-only | verify path quality before publishing AAAA |
| 4 | Trusting DSCP on PC ports | users set their own priority, voice is squeezed out | trust only phones and controlled devices |
| 5 | LLQ without a policer | the high-priority class starves the others | priority + police |
| 6 | No shaping on sub-rate links | queues take effect in the wrong place | HQoS with a shaping parent |
| 7 | Tunnels that do not copy DSCP | cross-WAN voice degrades to BE | pre-classify + outer-header marking |
| 8 | Mapping only from MPLS EXP (3 bits) | EF degrades to CS5, the voice queue never matches | an explicit EXP↔DSCP mapping table |
| 9 | Accepting QoS on an idle network | always "passes", then fails in production | congestion injection + MOS measurement |
| 10 | Full-table SNMP walks | management-plane CPU saturated, protocol flapping | fetch only the columns you need + stagger |
| 11 | NetFlow without sampling | export traffic saturates the management link | sampling ratio + capacity accounting |
| 12 | Syslog without rate limiting | a log storm takes down the device and the server | rate-limit + flap detection |
| 13 | NTP pointed at the public Internet | egress down → certificates, logs and audit collapse in sequence | internal hierarchy + authentication + alerting |
| 14 | Single DHCP server / single relay | a whole floor cannot get addresses at morning peak | two servers + two relay targets |
| 15 | DNS TTLs set too long | failover never actually takes effect | 30–60 s TTL on records used for failover |
| 16 | In-band management as the only channel | no operations when the service is down | OOB + console + LTE backup |
| 17 | Monitoring devices but not services | all green while users complain | L4/L5 synthetic probes + SLOs |
| 18 | Alerts without a Runbook | alerts arrive and nobody knows what to do | every alert must link to its procedure |
| 19 | No expiry alerts for certificates or licences | one morning the whole network fails authentication | 90/30/7-day alerts + a change calendar |
| 20 | A single collector | "flying blind" exactly when you most need monitoring | HA collection tier + partitioning |

<div class="zh" markdown="1">

| # | 缺陷 | 后果 | 规避 |
|---|------|------|------|
| 1 | 把 /64 切小"省地址" | SLAAC 失效，部分终端无网 | 所有 LAN 固定 /64 |
| 2 | 全网禁 ICMP/ICMPv6 | PMTUD 黑洞、ND 失效 | 放行关键类型，只限速 |
| 3 | 双栈但路径不对等 | 业务"时快时慢"，比纯 v4 更差 | 先验路径质量再开 AAAA |
| 4 | PC 口 trust DSCP | 用户可自定优先级，语音被挤 | 只信任话机/受控设备 |
| 5 | LLQ 无 policer | 高优先级饿死其他类 | priority + police |
| 6 | 子速率链路不整形 | 队列在错误位置生效 | HQoS 父层整形 |
| 7 | 隧道不复制 DSCP | 跨 WAN 语音退化为 BE | pre-classify + 外层标记 |
| 8 | 只按 MPLS EXP（3 位）映射 | EF 退化成 CS5，语音队列不命 | 显式 EXP↔DSCP 映射表 |
| 9 | 空载验收 QoS | 永远"通过"，上线即翻车 | 拥塞注入 + MOS 测量 |
| 10 | SNMP 全表 walk | 管理面 CPU 打满、协议抖动 | 只取需要的列 + 错峰 |
| 11 | NetFlow 不采样 | 导出流量打满管理链路 | 采样比 + 容量账 |
| 12 | Syslog 不限速 | 日志风暴拖垮设备与服务器 | rate-limit + flap 检测 |
| 13 | NTP 指向公网 | 出口断 → 证书/日志/审计连锁崩 | 内部分层 + 认证 + 告警 |
| 14 | DHCP 单服务器/单中继 | 早高峰整层拿不到地址 | 双服务器 + 双中继目标 |
| 15 | DNS TTL 过长 | 故障切换实际不生效 | 切换类记录 TTL 30–60 s |
| 16 | 带内管理当唯一通道 | 业务断时无法运维 | OOB + Console + LTE 备份 |
| 17 | 只监控设备不监控服务 | 设备全绿但用户投诉 | L4/L5 合成探测 + SLO |
| 18 | 告警不挂 Runbook | 收到告警不知道做什么 | 每条告警必须有处置链接 |
| 19 | 证书/许可无到期告警 | 某天早上全网认证失败 | 90/30/7 天告警 + 变更日历 |
| 20 | 采集器单点 | 故障时"盲飞"（正是最需要监控时） | 采集层 HA + 分区 |

</div>

---

## Key Terms · 本章关键术语

### IPv6

| Term | Meaning |
|------|---------|
| GUA | Global Unicast Address (2000::/3) |
| ULA | Unique Local Address (FC00::/7, commonly FD00::/8) |
| LLA | Link-Local Address (FE80::/10) |
| IID | Interface Identifier (lower 64 bits) |
| SLAAC | Stateless Address Autoconfiguration (RFC 4862) |
| DHCPv6 | Stateful or stateless IPv6 address and parameter assignment |
| NDP | Neighbor Discovery Protocol (RS/RA/NS/NA/Redirect) |
| DAD | Duplicate Address Detection |
| RS / RA | Router Solicitation / Advertisement |
| NS / NA | Neighbor Solicitation / Advertisement (address resolution) |
| RDNSS | DNS server carried in the RA (RFC 8106) |
| PMTUD | Path MTU Discovery (depends on ICMPv6 Type 2) |
| PTB | Packet Too Big (ICMPv6 Type 2) |
| MLD | Multicast Listener Discovery (the IPv6 version of IGMP) |
| RA Guard | Blocks forged router advertisements |
| ND Inspection | Blocks forged neighbor advertisements and address hijacking |
| DHCPv6 Guard | Blocks unauthorised DHCPv6 servers |
| SAVI | Source Address Validation Improvement |
| SEND | Secure Neighbor Discovery (rarely deployed) |
| PI / PA | Provider Independent / Provider Aggregatable addresses |
| NPTv6 | IPv6 prefix translation (port-independent) |
| NAT64 / DNS64 | Translation and DNS synthesis so v6-only hosts reach v4 |
| 464XLAT | CLAT+PLAT stateless translation scheme (RFC 6877) |
| DS-Lite | v4-over-v6 tunnel plus centralized CGN |
| MAP-E / MAP-T | Mapping-based address-and-port multiplexing |
| RFC 6724 | Default address selection rules (source address selection) |
| RFC 5549 | IPv6 prefixes carried with an IPv4 next hop |
| RFC 6164 | /127 on point-to-point links |
| BCP 38 / uRPF | Inbound source-address filtering (the hidden killer in multihoming) |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| GUA | 全球单播地址（2000::/3） |
| ULA | 唯一本地地址（FC00::/7，常用 FD00::/8） |
| LLA | 链路本地地址（FE80::/10） |
| IID | 接口标识（低 64 位） |
| SLAAC | 无状态地址自动配置（RFC 4862） |
| DHCPv6 | 有状态/无状态 IPv6 地址与参数分配 |
| NDP | 邻居发现协议（RS/RA/NS/NA/Redirect） |
| DAD | 重复地址检测 |
| RS / RA | 路由器请求/通告 |
| NS / NA | 邻居请求/通告（地址解析） |
| RDNSS | RA 中携带 DNS 服务器（RFC 8106） |
| PMTUD | 路径 MTU 发现（依赖 ICMPv6 Type 2） |
| PTB | Packet Too Big（ICMPv6 Type 2） |
| MLD | 组播监听发现（IPv6 版 IGMP） |
| RA Guard | 防伪造路由器通告 |
| ND Inspection | 防伪造邻居通告/地址劫持 |
| DHCPv6 Guard | 防非法 DHCPv6 服务器 |
| SAVI | 源地址有效性验证改进 |
| SEND | 安全的邻居发现（部署很少） |
| PI / PA | 独立于运营商 / 运营商聚合地址 |
| NPTv6 | IPv6 前缀转换（无端口） |
| NAT64 / DNS64 | v6-only 访问 v4 的翻译与 DNS 合成 |
| 464XLAT | CLAT+PLAT 的无状态翻译方案（RFC 6877） |
| DS-Lite | v4 over v6 隧道 + 集中 CGN |
| MAP-E / MAP-T | 基于映射的地址+端口复用 |
| RFC 6724 | 默认地址选择规则（源地址选择） |
| RFC 5549 | 用 IPv4 下一跳承载 IPv6 前缀 |
| RFC 6164 | 点到点链路用 /127 |
| BCP 38 / uRPF | 入向源地址过滤（多宿主的隐形杀手） |

</div>

### QoS

| Term | Meaning |
|------|---------|
| DiffServ | Differentiated Services (per-class treatment, stateless core) |
| IntServ / RSVP | Integrated Services / resource reservation (per-flow state) |
| DSCP | Differentiated Services Code Point (6 bits) |
| ToS / Traffic Class | the service field in the IP header |
| 802.1p / CoS | Layer 2 priority (3 bits) |
| EXP / TC | MPLS Experimental / Traffic Class field (3 bits) |
| PHB | Per-Hop Behaviour |
| EF | Expedited Forwarding (46) |
| AFxy | Assured Forwarding (class x, drop precedence y) |
| CSx | Class Selector (CS0–CS7) |
| DF / BE | Default / Best Effort (0) |
| VA | Voice Admit (44, voice after CAC) |
| LLQ | Low Latency Queueing (strict priority plus a policer) |
| CBWFQ | Class-Based Weighted Fair Queueing |
| WRED | Weighted Random Early Detection |
| ECN | Explicit Congestion Notification (RFC 3168) |
| Policing | drops or downgrades traffic above the rate |
| Shaping | buffers excess and smooths the output rate |
| HQoS | Hierarchical QoS (parent shaping + child queues) |
| CAC | Call Admission Control |
| CoPP | Control Plane Policing (protects device CPU) |
| Serialization Delay | frame length divided by link rate |
| MOS | voice quality score (1–5, ≥4.0 is good) |
| G.114 | the recommendation of ≤150 ms one-way delay |
| WMM | Wi-Fi Multimedia (VO/VI/BE/BK) |
| LFI | Link Fragmentation and Interleaving (voice on low-bandwidth links) |
| Scavenger Class | the lowest-priority class (P2P, updates) |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| DiffServ | 区分服务（按类处理，核心无状态） |
| IntServ / RSVP | 集成服务/资源预留（每流状态） |
| DSCP | 差分服务代码点（6 位） |
| ToS / Traffic Class | IP 头中的服务字段 |
| 802.1p / CoS | 二层优先级（3 位） |
| EXP / TC | MPLS 实验位/流类字段（3 位） |
| PHB | 每跳行为 |
| EF | 加速转发（46） |
| AFxy | 确保转发（类 x、丢弃优先级 y） |
| CSx | 类选择器（CS0–CS7） |
| DF / BE | 默认/尽力而为（0） |
| VA | Voice Admit（44，CAC 后语音） |
| LLQ | 低延迟队列（严格优先 + 限速） |
| CBWFQ | 基于类的加权公平队列 |
| WRED | 加权随机早期检测 |
| ECN | 显式拥塞通知（RFC 3168） |
| Policing | 监管（超限丢弃/降级） |
| Shaping | 整形（缓冲超额、平滑输出） |
| HQoS | 层级化 QoS（父整形 + 子队列） |
| CAC | 呼叫准入控制 |
| CoPP | 控制面策略（保护设备 CPU） |
| Serialization Delay | 序列化延迟（帧长/链路速率） |
| MOS | 语音质量评分（1–5，≥4.0 为良好） |
| G.114 | 单向时延 ≤150 ms 的建议 |
| WMM | 无线多媒体（VO/VI/BE/BK 四类） |
| LFI | 链路分片与交错（低带宽语音） |
| Scavenger Class | 最低优先级类（P2P/更新） |

</div>

### Management and Services · 管理与服务

| Term | Meaning |
|------|---------|
| FCAPS | Fault, Configuration, Accounting, Performance, Security (the ISO management domains) |
| OOB | Out-of-Band management |
| Management VRF | a routing instance that isolates management traffic |
| SNMP | Simple Network Management Protocol (v2c/v3) |
| MIB / OID | Management Information Base / Object Identifier |
| VACM | View-Based Access Control Model (SNMPv3) |
| Trap / Inform | unacknowledged trap / acknowledged notification |
| GetBulk | bulk retrieval (fewer round trips) |
| Syslog | system logging (severity 0–7) |
| RFC 5424 | the Syslog protocol format (structured data) |
| NetFlow / IPFIX | flow export (v9 templates / IPFIX, RFC 7011) |
| sFlow | packet-sampling traffic statistics |
| gNMI | gRPC Network Management Interface (configuration + telemetry) |
| Streaming Telemetry | push-model telemetry |
| Dial-in / Dial-out | collector connects to device / device connects to collector |
| ON_CHANGE / SAMPLE | change-triggered / periodic-sample subscriptions |
| IP SLA | active synthetic probing (latency/jitter/loss) |
| SLI / SLO | service level indicator / service level objective |
| MTTD / MTTR | mean time to detect / mean time to repair |
| NTP | Network Time Protocol (stratum hierarchy) |
| PTP | Precision Time Protocol (IEEE 1588, sub-microsecond) |
| NTP authentication | protects against forged time sources |
| DHCP option 82 | relay information (circuit-id/remote-id) |
| DHCP snooping | blocks rogue DHCP servers |
| DHCPv6 PD | prefix delegation (a branch obtains a /56) |
| T1 / T2 | renewal timers (50%/87.5%) |
| DNS recursive/authoritative | resolution on behalf of clients / answering authoritatively for a zone |
| Conditional forwarding | forward per domain to a designated resolver |
| DNSSEC | signed DNS data validation |
| DoT / DoH | DNS over TLS / HTTPS |
| Anycast DNS | one address deployed at many points (locality + redundancy) |
| RADIUS | access authentication (UDP 1812/1813, password encrypted) |
| TACACS+ | device management AAA (TCP 49, full payload encryption, per-command authorisation) |
| IPAM | IP Address Management system |
| PKI / CRL / OCSP | certificate infrastructure / revocation list / online status check |
| Flap Damping | oscillation suppression (N times within M minutes) |
| Parent-Child Suppression | a child alert is suppressed while its parent is active |
| Runbook | the procedure attached to every alert |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| FCAPS | 故障/配置/计费/性能/安全（ISO 管理域） |
| OOB | 带外管理 |
| 管理 VRF | 隔离管理流量的路由实例 |
| SNMP | 简单网络管理协议（v2c/v3） |
| MIB / OID | 管理信息库/对象标识 |
| VACM | 视图访问控制模型（SNMPv3） |
| Trap / Inform | 陷阱（无确认）/通知（有确认） |
| GetBulk | 批量读取（减少往返） |
| Syslog | 系统日志（severity 0–7） |
| RFC 5424 | Syslog 协议格式（结构化数据） |
| NetFlow / IPFIX | 流导出（v9 模板/IPFIX RFC 7011） |
| sFlow | 包采样流量统计 |
| gNMI | gRPC 网络管理接口（配置+遥测） |
| Streaming Telemetry | 流式遥测（推送模型） |
| Dial-in / Dial-out | 采集器连设备 / 设备连采集器 |
| ON_CHANGE / SAMPLE | 变化触发 / 周期采样订阅 |
| IP SLA | 主动合成探测（延迟/抖动/丢包） |
| SLI / SLO | 服务指标/服务目标 |
| MTTD / MTTR | 平均发现时间/平均修复时间 |
| NTP | 网络时间协议（stratum 层级） |
| PTP | 精确时间协议（IEEE 1588，亚微秒） |
| NTP 认证 | 防伪造时间源 |
| DHCP option 82 | 中继信息（circuit-id/remote-id） |
| DHCP snooping | 防私设 DHCP 服务器 |
| DHCPv6 PD | 前缀委派（分支机构获取 /56） |
| T1 / T2 | 续租定时器（50%/87.5%） |
| DNS 递归/权威 | 代查 / 本域权威应答 |
| 条件转发 | 按域转发到指定解析器 |
| DNSSEC | DNS 数据签名验证 |
| DoT / DoH | DNS over TLS / HTTPS |
| Anycast DNS | 同一地址多点部署（就近+冗余） |
| RADIUS | 接入认证（UDP 1812/1813，密码加密） |
| TACACS+ | 设备管理 AAA（TCP 49，全负载加密，命令级授权） |
| IPAM | IP 地址管理系统 |
| PKI / CRL / OCSP | 证书体系/吊销列表/在线状态查询 |
| Flap Damping | 抖动抑制（N 次/M 分钟） |
| Parent-Child Suppression | 父子告警抑制 |
| Runbook | 处置手册（每条告警对应动作） |

</div>

---

## Field-Proven Lessons · 实战经验总结

1. **The first rule of IPv6 is not "how to configure it" but "every LAN prefix must be /64"**; any design that breaks it will be overturned by IoT and Android within three months.
2. **ICMPv6 is not optional**: block it and ND dies together with PMTUD. The correct security policy is "permit the essential types + rate-limit", not "deny everything".
3. **The cost of dual stack is not in the protocol stack but in "two troubleshooting skill sets"**: the team must be able to walk the whole chain — address → gateway → DNS → MTU → application binding — in v6 alone.
4. **Ask three questions before any QoS review**: who may mark? how many classes? who is dropped first under congestion? If you cannot answer, the prettiest queue configuration is meaningless.
5. **QoS only matters under congestion.** So "do we need QoS" is equivalent to "will this link congest", not "is voice important".
6. **The trust boundary must be drawn on a diagram**, annotated "DSCP is trustworthy from here on". Without that diagram, QoS will be broken by some future change.
7. **Every bandwidth promise must become a number**: concurrency × per-call bandwidth × 1.2, plus "LLQ ≤ 33%, the sum of guarantees ≤ 80%".
8. **Sub-rate links must be shaped**, otherwise your queues do unpaid work on behalf of the carrier.
9. **Always verify the outer DSCP inside a tunnel**: one packet capture beats ten design principles.
10. **Acceptance on an idle network is not acceptance**: QoS, redundancy and failover must all be validated under bad conditions.
11. **Design the management plane as a network in its own right**: a dedicated VRF, OOB, jump hosts, tiered AAA and a bandwidth budget — none of them optional.
12. **Three hard constraints on collection design**: fetch only the columns you need, record the sampling ratio, partition and stagger the collectors.
13. **Logging must have a ceiling**: rate limiting on the device, per-source limiting on the server, flap detection in alerting. Otherwise logging becomes a fault amplifier.
14. **NTP is the coordinate system for all data**: internal hierarchy + authentication + offset alerting costs almost nothing and buys you "correlated timelines during troubleshooting".
15. **Foundational services (DHCP/DNS/NTP/AAA) must be more available than the core network**, because their blast radius is the whole estate.
16. **The value of an alert = somebody acts on it**: every alert needs a severity, a Runbook and suppression rules, or it will be muted within six months.
17. **Size observability capacity in advance** (metrics × frequency × retention), or the platform dies slowly under a chorus of "add more monitoring".
18. **Certificates and licences are predictable failures**: an expiry alert is cheaper than any drill.
19. **In a CCDE answer, "how to prove it" matters as much as "how to design it"**: QoS without a measurement plan and management without OOB are both incomplete designs.
20. **The design philosophy of supporting systems**: **least visible in normal times, most critical during a failure**. Hence their first priority is always "still works when broken".

<div class="zh" markdown="1">

1. **IPv6 的第一条规则不是"怎么配"，而是"所有 LAN 前缀必须是 /64"**；违反它的方案会在三个月后被 IoT 和 Android 推翻。
2. **ICMPv6 不是可选项**：禁了它，ND 与 PMTUD 一起死。安全策略的正确写法是"放行关键类型 + 限速"，不是"一律拒绝"。
3. **双栈的成本不在协议栈，在"两套排障能力"**：团队必须能独立用 v6 走完 地址 → 网关 → DNS → MTU → 应用绑定 这条链。
4. **QoS 评审先问三个问题**：谁有权标记？几类？拥塞时谁先丢？答不上来，队列配置再漂亮也没意义。
5. **QoS 只在拥塞时起作用**。所以"要不要上 QoS"等价于"这条链路会不会拥塞"，而不是"语音重不重要"。
6. **信任边界必须画在图上**，并且标注"这里之后 DSCP 可信"。没有这张图，QoS 一定会在某次变更中被破坏。
7. **所有带宽承诺都要落成数字**：并发数 × 单路带宽 × 1.2，以及"LLQ ≤ 33%、保证总和 ≤ 80%"。
8. **子速率链路必须整形**，否则你的队列在替运营商做无用功。
9. **隧道里必须验证外层 DSCP**：抓一次包，比讨论十条设计原则有用。
10. **空载验收等于没验**：QoS、冗余、故障切换都必须在"坏工况"下验证。
11. **管理平面要按一张网来设计**：独立 VRF、OOB、跳板机、AAA 分级、带宽账，一个都不能省。
12. **采集设计的三条硬约束**：只取需要的列、采样比要记录、采集器要分区并错峰。
13. **日志必须有上限**：设备侧限速、服务器侧按来源限速、告警侧做 flap 检测。否则日志会成为故障放大器。
14. **NTP 是所有数据的坐标系**：内部分层 + 认证 + 偏移告警，成本极低，收益是"排障时能对齐时序"。
15. **基础服务（DHCP/DNS/NTP/AAA）的可用性要求应高于核心网络**，因为它们的影响面是全域。
16. **告警的价值 = 有人会动作**：每条告警都要有分级、Runbook、抑制规则，否则半年后一定被静音。
17. **可观测性的容量账要提前算**（指标×频率×保留期），否则平台会在"多加点监控"的呼声中慢慢死掉。
18. **证书与许可是可预测的故障**：到期告警比任何故障演练都便宜。
19. **CCDE 的答案里，"如何证明"和"如何设计"同等重要**：没有测量方案的 QoS 与没有 OOB 的管理设计，都不算完成。
20. **支撑系统的设计哲学**：**平时最不显眼，故障时最关键**。所以它们的第一优先级永远是"故障时还能工作"。

</div>

---

## Design Scenarios · 设计情景演练（服务与管理类，三道）

> The trap in this chapter's scenario questions is **treating a "service" as a "feature toggle"** (switch on DHCP, set a community string). The right approach is to state the blast radius (who depends on it), the degradation path during failure, and "how you will prove that it works".

<div class="zh" markdown="1">

> 本章题型的陷阱是：**把"服务"当成"功能开关"**（开个 DHCP、配个团体字）。正确的做法是先写清影响面（谁的依赖）、故障时的降级路径、以及"如何证明它有效"。

</div>

### Scenario 1: 5,000 Endpoints Must Move to IPv6, but the Inventory Includes Android, IoT and Legacy Apps with Hard-Coded IPs · 情景一：5000 终端要上 IPv6，但清单里有 Android、IoT 和写死 IP 的老应用

**Background**: a 5,000-person enterprise with 30 campus buildings, two data centres and one branch. Endpoint mix: Windows 70%, macOS 10%, Android 15% (BYOD), IoT/printers/cameras 5%. There are 300 servers, 40 of them legacy systems (hard-coded IPv4 literals in application configuration, some using IPsec). The carrier can provide a /48 but **only offers an IPv6 egress; IPv4 must go through CGN or keep the old link for 12 months**. The IT team is six people with no IPv6 operations experience.

<div class="zh" markdown="1">

**背景**：一家 5000 人的企业，园区 30 栋楼、两个数据中心、一个分支。终端构成：Windows 70%、macOS 10%、Android 15%（BYOD）、IoT/打印机/摄像头 5%。服务器 300 台，其中 40 台是老系统（应用配置里写死了 IPv4 字面地址，部分用 IPsec）。运营商可提供 /48，但**只提供 IPv6 出口，IPv4 需走 CGN 或保留旧链路 12 个月**。IT 团队 6 人，无 IPv6 运维经验。

</div>

**Question**: propose a phased IPv6 introduction plan and the address-planning essentials, and answer whether you can go v6-only in one step.

<div class="zh" markdown="1">

**问题**：给出 IPv6 引入的分期方案、地址规划要点，并回答"是否可以一步到位做 v6-only"。

</div>

<details markdown="1">
<summary>Reference analysis</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core idea: dual stack with the internal network going v6 first — not v6-only. The constraint list contains Android (SLAAC only) and legacy applications with hard-coded IPv4 literals plus IPsec; those two rule out NAT64 single stack outright.**

<div class="zh" markdown="1">

**核心思路：先做"双栈 + 内网 v6 先行"，不做 v6-only。原因是约束清单里同时存在 Android（只认 SLAAC）与"写死 IPv4 字面地址 + IPsec"的老应用 —— 这两条直接排除 NAT64 单栈。**

</div>

| Phase | Timing | Deliverable | Key judgement |
|---|---|---|---|
| **1: Planning and capability** | months 0–2 | address allocation table (/48 → site /56 → subnet /64), the **"every LAN is /64" rule**, device/tool capability matrix (ACLs, NetFlow, firewall v6 support) | the address table is the precondition for everything else; the capability matrix finds "devices that cannot do v6" |
| **2: Infrastructure first** | months 2–4 | management network/loopbacks/P2P in v6, OSPFv3, DNS AAAA, dual-stack NTP/AAA, v6 monitoring | the supporting systems must run v6 first, otherwise endpoint v6 is not operable |
| **3: Data centre and servers** | months 4–6 | dual-stack servers (applications confirmed to listen on `::`), A/AAAA published together in DNS, MSS clamping | **server-side AAAA must exist before endpoint v6 means anything** |
| **4: Campus endpoints in batches** | months 6–12 | enable RA per building (SLAAC + RDNSS), IT and pilot floors first | observe each batch for two weeks: address acquisition rate, DNS success rate, application latency |
| **5: Egress and outside world** | month 12+ | IPv6 egress alongside dual stack; IPv4 retained for 12 months | publish AAAA everywhere only once **path quality is at parity** |

<div class="zh" markdown="1">

| 阶段 | 时间 | 交付物 | 关键判断 |
|---|---|---|---|
| **一：规划与能力** | 0–2 月 | 地址分配表（/48 → 站点 /56 → 子网 /64）、**"LAN 必须 /64"规则**、设备/工具能力矩阵（ACL、NetFlow、防火墙 v6 支持） | 地址表是后面一切的前提；能力矩阵找出"不支持 v6 的设备" |
| **二：基础设施先行** | 2–4 月 | 管理网/环回/P2P v6、OSPFv3、DNS AAAA、NTP/AAA 双栈、监控 v6 | 让"支撑系统"先能跑 v6，否则终端的 v6 不可运营 |
| **三：数据中心与服务器** | 4–6 月 | 服务器双栈（应用确认监听 `::`）、DNS 同步发布 A/AAAA、MSS clamping | **先有服务端 AAAA，终端 v6 才有意义** |
| **四：园区终端分批** | 6–12 月 | 按楼分批开 RA（SLAAC + RDNSS），先 IT/试点楼层 | 每批观察 2 周：地址获取率、DNS 成功率、应用时延 |
| **五：出口与外部** | 12 月+ | IPv6 出口 + 双栈并存；IPv4 保留 12 个月 | **路径质量对等**才把 AAAA 全量发布 |

</div>

**Three hard rules for address planning**:

<div class="zh" markdown="1">

**地址规划三条硬规则**：

</div>

1. **A site is a /56 (or /48) and subnets are always /64**, never subdivided
2. **Point-to-point links use /127 and loopbacks /128**, all covered in ACLs by a single "infrastructure aggregate prefix" entry
3. **The site ID is bound to a physical or organisational code** (region-campus-building) so it can still be aggregated ten years from now

<div class="zh" markdown="1">

1. **站点 = /56（或 /48），子网固定 /64**，永不切分
2. **P2P 用 /127、环回 /128**，并在 ACL 中按"基础设施汇总前缀"一条覆盖
3. **站点 ID 与物理/组织编码绑定**（大区-园区-楼），保证十年后可汇总

</div>

**Why you cannot go v6-only**:

<div class="zh" markdown="1">

**为什么不能 v6-only**：

</div>

| Blocker | Explanation | Alternative |
|---|---|---|
| Android supports SLAAC only | cannot audit addresses through stateful DHCPv6 | keep SLAAC (which means keeping /64 and RA) |
| 40 legacy applications hard-code IPv4 literals | NAT64 does nothing for literals unless DNS64 covers them | dual-stack transition, or rework the applications |
| Some IPsec scenarios | NAT64 breaks end-to-end behaviour and some IPsec modes | dual stack |
| The team has no v6 experience | single stack means "a mistake has no v4 safety net" | dual stack as a training ground |

<div class="zh" markdown="1">

| 阻碍项 | 说明 | 替代方案 |
|---|---|---|
| Android 只支持 SLAAC | 无法用 DHCPv6 有状态做地址审计 | 保留 SLAAC（也就保留 /64 与 RA） |
| 40 台老应用写死 IPv4 字面地址 | NAT64 对字面地址无效（除非 DNS64 覆盖） | 双栈过渡，或改造应用 |
| 部分 IPsec 场景 | NAT64 破坏端到端与部分 IPsec 模式 | 双栈 |
| 团队无 v6 经验 | 单栈意味着"出错就没有 v4 兜底" | 双栈练兵 |

</div>

**The point you are most likely to be challenged on**: why not simply use NAT64 + DNS64 and drop IPv4? — **because the cost of NAT64 is underestimated**: it trades "address management" for "translation state + logging + application compatibility work", and troubleshooting those 40 legacy applications costs far more than keeping one IPv4 link.

<div class="zh" markdown="1">

**最容易被追问的一点**：为什么不直接 NAT64 + DNS64 省掉 IPv4？—— **因为 NAT64 的成本被低估**：它把"地址管理"换成"翻译状态 + 日志 + 应用兼容性排查"，而这 40 台老应用的排查成本远高于保留一条 IPv4 链路。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 2: Poor Voice Quality Across 50 Sites While the QoS Configuration "Looks Completely Right" · 情景二：50 个站点语音质量差，QoS 配置"看起来全对"

**Background**: 50 branches on MPLS (sub-rate 10–100 Mbps) with internet IPsec as backup. Voice is centralised at headquarters; branch egress devices already have LLQ (EF priority) and bandwidth guarantees for the AF classes, and the configuration review says it "matches Cisco recommendations". Yet users keep complaining about broken audio at busy times, and `show policy-map` shows almost no traffic in the voice queue.

<div class="zh" markdown="1">

**背景**：50 个分支，MPLS（10–100 Mbps 子速率）为主、互联网 IPSec 为备。语音集中部署在总部，分支出口设备已配置 LLQ（EF 优先）、AF 类带宽保证，配置审阅"符合 Cisco 推荐值"。但用户持续投诉忙时语音断续，`show policy-map` 显示语音队列几乎没流量。

</div>

**Question**: give the corrected end-to-end QoS design and explain why the current configuration has no effect.

<div class="zh" markdown="1">

**问题**：给出端到端 QoS 的修正方案，并说明为什么现有配置不生效。

</div>

<details markdown="1">
<summary>Reference analysis</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core idea: first establish whether the queue is actually doing any work, then talk about parameters. "Almost no traffic in the voice queue" is the key evidence — the voice packets are no longer EF by the time they reach that queue, or that queue is not the congestion point at all.**

<div class="zh" markdown="1">

**核心思路：先定位"队列是否真的在工作"，再谈参数。`语音队列几乎没流量` 是最关键的证据 —— 说明语音包在到达该队列前就已经不是 EF 了，或该队列根本不是拥塞点。**

</div>

| Possible cause | How to verify | Correction |
|---|---|---|
| **① Sub-rate not shaped** | physical port 1G, contract 10–100M; physical `output drops` = 0 | parent `shape` to CIR (5–10% headroom) with the child queues underneath |
| **② Tunnel does not copy DSCP** | capture the outer IPsec ESP packet, ToS=0 | `qos pre-classify` / outer-header mapping; confirm the recognised class count with the carrier |
| **③ Boundary not cleaned** | capture at the access layer, EF share abnormally high or low | trust on phone ports, re-mark PC ports; add a policer to the LLQ |
| **④ MPLS EXP mapping lost** | DSCP changes from 46 to 40 after leaving the MPLS domain | explicit EXP↔DSCP mapping |
| **⑤ Voice bandwidth over budget** | concurrency × 95 kbps against the LLQ's 33% ceiling | add CAC, or upgrade, or switch to G.729 |

<div class="zh" markdown="1">

| 可能原因 | 验证方法 | 修正 |
|---|---|---|
| **① 子速率未整形** | 物理口 1G、合同 10–100M；物理口 `output drops` = 0 | 父层 `shape` 到 CIR（留 5–10% 余量），子队列挂在其下 |
| **② 隧道未复制 DSCP** | 抓 IPsec 外层 ESP，ToS=0 | `qos pre-classify` / 外层映射；与运营商确认可识别类数 |
| **③ 边界未清洗** | 抓接入层包，EF 占比异常高或低 | 话机口 trust，PC 口重标；LLQ 加 policer |
| **④ MPLS EXP 映射丢失** | 出 MPLS 域后 DSCP 从 46 变 40 | 显式 EXP↔DSCP 映射 |
| **⑤ 语音带宽超预算** | 并发数 × 95 kbps 与 LLQ 的 33% 上限 | 上 CAC，或扩容/换 G.729 |

</div>

**Target design (each branch egress)**:

<div class="zh" markdown="1">

**目标设计（每个分支出口）**：

</div>

```
policy-map WAN-PARENT
 class class-default
  shape average <CIR × 0.95>
  service-policy WAN-CHILD

policy-map WAN-CHILD
 class VOICE        → priority percent 30 + police (48 kbps per call × concurrency)
 class SIGNALING    → bandwidth percent 2
 class VIDEO-CONF   → bandwidth percent 15 + random-detect dscp-based
 class TRANSACTION  → bandwidth percent 15 + random-detect
 class BULK         → bandwidth percent 5  + random-detect
 class SCAVENGER    → bandwidth percent 2  + police
 class class-default→ bandwidth percent 25
```

<div class="zh" markdown="1">

```
policy-map WAN-PARENT
 class class-default
  shape average <CIR × 0.95>
  service-policy WAN-CHILD

policy-map WAN-CHILD
 class VOICE        → priority percent 30 + police（48 kbps/路 × 并发）
 class SIGNALING    → bandwidth percent 2
 class VIDEO-CONF   → bandwidth percent 15 + random-detect dscp-based
 class TRANSACTION  → bandwidth percent 15 + random-detect
 class BULK         → bandwidth percent 5  + random-detect
 class SCAVENGER    → bandwidth percent 2  + police
 class class-default→ bandwidth percent 25
```

</div>

**Acceptance (mandatory, otherwise you cannot prove it is fixed)**:

<div class="zh" markdown="1">

**验收（必须做，否则无法证明修好了）**：

</div>

1. **Congestion injection**: drive 110% of CIR with iperf or a test set while running 20 simulated voice calls; MOS ≥4.0 and jitter <30 ms
2. **Both directions**: measure HQ → branch and branch → HQ separately
3. **Across the tunnel**: capture the outer packet and confirm the ToS matches the inner header
4. **Monitoring**: EF drop rate, LLQ policer drops and `shaping` queue depth go on a dashboard with alerts

<div class="zh" markdown="1">

1. **拥塞注入**：用 iperf/测试仪打到 110% CIR，同时跑 20 路语音模拟器，测 MOS ≥4.0、抖动 <30 ms
2. **双向验证**：总部 → 分支、分支 → 总部 各测一次
3. **跨隧道**：抓外层包确认 ToS 与内层一致
4. **监控**：EF 类丢包率、LLQ policer 丢弃计数、`shaping` 队列深度进看板并设告警

</div>

**The point you are most likely to be challenged on**: why not simply add bandwidth? — because **"adding bandwidth" on sub-rate links is usually limited by contract and budget**, and the root cause of broken voice is **marking and shaping**; after an upgrade the next application peak reproduces the problem. **Fix QoS first, then talk about capacity — that is the orderly investment.**

<div class="zh" markdown="1">

**最容易被追问的一点**：为什么不干脆扩容？—— 因为**在子速率链路上"扩容"往往受合同与预算限制**，而且"语音断续"的根因是**标记与整形**，扩容后下一个应用高峰还会复现。**先把 QoS 修对，再谈扩容，才是有序的投资。**

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 3: 2,000 Devices, 5,000 Alerts a Day, No OOB, and SNMP Already Shaking the Core · 情景三：2000 台设备、每天 5000 条告警、没有带外，SNMP 已把核心打抖

**Background**: a manufacturing group with 2,000 devices across 80 sites (20 unmanned). The NOC has six people. Today: a single SNMP collector polls every device (5-minute cycle including full `ifTable` walks), the core router's management-plane CPU peaks at 82%; there are 5,000+ alerts a day and 90% of them are never acted on; all main sites are managed in-band, unmanned sites have only a single 4G backup link; the log server is a single node with no retention policy.

<div class="zh" markdown="1">

**背景**：制造业集团，2000 台设备、80 个站点（20 个无人值守）。NOC 6 人。现状：单台 SNMP 采集器轮询全部设备（5 分钟周期，含 ifTable 全表 walk），核心路由器管理面 CPU 峰值 82%；每天 5000+ 条告警，其中 90% 无人处理；主站全部带内管理，无人站点只有单条 4G 备份链路；日志服务器单台、无保留策略。

</div>

**Question**: give the target architecture, the migration order, and how to prioritise with a limited budget.

<div class="zh" markdown="1">

**问题**：给出目标架构、迁移顺序，以及"如何在预算有限时排优先级"。

</div>

<details markdown="1">
<summary>Reference analysis</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core idea: first stop "flying blind" and stop "crushing the devices" (collection rework + alert governance), then do OOB — because collection rework and alert governance cost no capital while OOB does.**

<div class="zh" markdown="1">

**核心思路：先把"瞎飞"和"打爆设备"解决（采集重构 + 告警治理），再做 OOB。因为采集重构与告警治理不花钱，OOB 花钱。**

</div>

| Priority | Action | Cost | Benefit |
|---|---|---|---|
| **P0** | Collect only the columns needed, partition by site, stagger phases, rate-limit SNMP on devices + CoPP | very low (configuration) | removes the CPU-flapping risk immediately |
| **P0** | Alert governance: severity + parent-child suppression + flap detection + a Runbook per alert; delete alerts "nobody would ever act on" | low (people) | 5,000 → 200–400 per day, which is the only way the NOC actually looks |
| **P1** | Collection-tier HA (two nodes per region), centralised logging + retention + per-source rate limiting | medium | no more "flying blind" during failures |
| **P1** | OOB first for critical sites (the 20 unmanned sites plus core/DC): management switch + console server + LTE | medium-high | operable during an outage |
| **P2** | Move key devices to telemetry (ON_CHANGE + 60 s SAMPLE), keep SNMP on legacy gear | medium | precision and overhead improve together |
| **P2** | SLOs plus synthetic probing (L4/L5), quarterly capacity trends | low | moves from a "device view" to a "business view" |

<div class="zh" markdown="1">

| 优先级 | 动作 | 成本 | 收益 |
|---|---|---|---|
| **P0** | 采集只取需要的列、按站点分区、错峰相位、设备侧 SNMP 限速 + CoPP | 极低（配置） | 立刻消除 CPU 抖动风险 |
| **P0** | 告警治理：分级 + 父子抑制 + flap 检测 + 每条挂 Runbook，砍掉"不会有人动作"的告警 | 低（人力） | 5000 → 200–400 条/天，NOC 才可能真的看 |
| **P1** | 采集层 HA（每区 2 台）、日志集中 + 保留策略 + 按来源限速 | 中 | 故障时不再"盲飞" |
| **P1** | 关键站点（20 个无人站点 + 核心/DC）先做 OOB（管理交换机 + Console 服务器 + LTE） | 中高 | 故障时可运维 |
| **P2** | 关键设备转遥测（ON_CHANGE + 60 s SAMPLE），老设备保留 SNMP | 中 | 精度与开销同时改善 |
| **P2** | SLO 与合成探测（L4/L5），季度容量趋势 | 低 | 从"设备视角"走向"业务视角" |

</div>

**Target architecture**:

<div class="zh" markdown="1">

**目标架构**：

</div>

```
Collection tier (partitioned by site, 2 nodes per region for HA)
  ├─ SNMP poller (only the columns needed, staggered)
  ├─ gNMI collector (key devices: ON_CHANGE + 60s SAMPLE)
  ├─ Syslog receiver (TLS 6514, per-source rate limiting)
  ├─ Flow collector (sampling ratio registered)
  └─ IP SLA aggregation (critical paths per site)
        ↓
Storage tier: time series (30 days raw + 1 year downsampled) / logs (90 days, hot-cold tiers) / flows (30 days aggregated)
        ↓
Analytics tier: thresholds + baselines (P95) + topology-aware parent-child suppression
        ↓
Presentation tier: NOC wallboard (P1/P2) / engineering dashboards / business SLO reports
        ↓
Management channels: management VRF + OOB (critical sites) + console server + tiered AAA + jump hosts
```

<div class="zh" markdown="1">

```
采集层（按站点分区，每区 2 台 HA）
  ├─ SNMP poller（只取需要的列，错峰）
  ├─ gNMI collector（关键设备：ON_CHANGE + 60s SAMPLE）
  ├─ Syslog receiver（TLS 6514，按来源限速）
  ├─ Flow collector（采样比登记在案）
  └─ IP SLA 汇总（每站点关键路径）
        ↓
存储层：时序（原始 30 天 + 1 年降采样）/ 日志（90 天，冷热分层）/ 流（聚合 30 天）
        ↓
分析层：阈值 + 基线（P95）+ 拓扑感知的父子抑制
        ↓
呈现层：NOC 大屏（P1/P2）/ 工程看板 / 业务 SLO 报表
        ↓
管理通道：管理 VRF + OOB（关键站点）+ Console 服务器 + AAA 分级 + 跳板机
```

</div>

**Quantified targets for alert governance**:

<div class="zh" markdown="1">

**告警治理的具体量化目标**：

</div>

| Metric | Today | Target |
|---|---|---|
| Alerts per day | 5,000 | ≤400 |
| Share that triggers an action | 10% | ≥90% |
| Mean time to detect P1 | unknown (user reports) | <2 minutes |
| Single point of collection | 1 node | 2 nodes per region |
| Core management-plane CPU peak | 82% | <40% |

<div class="zh" markdown="1">

| 指标 | 现状 | 目标 |
|---|---|---|
| 日告警量 | 5,000 | ≤400 |
| 有处置动作的比例 | 10% | ≥90% |
| P1 平均发现时间 | 未知（用户投诉） | <2 分钟 |
| 采集器单点 | 1 台 | 每区 2 台 |
| 核心管理面 CPU 峰值 | 82% | <40% |

</div>

**Why this order**: the NOC has six people — **unless the alert volume comes down, any new platform gets muted**; and collection rework plus alert governance is "zero-procurement" engineering that shows results within two weeks, buying budget and trust for the later OOB investment.

<div class="zh" markdown="1">

**为什么这个顺序**：NOC 只有 6 人，**告警量不降下来，任何新平台都会被静音**；而采集重构与告警治理是"零采购"的工程动作，能在两周内见效，为后续 OOB 投入争取预算与信任。

</div>

**The point you are most likely to be challenged on**: why start OOB with core and unmanned sites rather than everywhere? — because OOB cost scales linearly with site count while **the risk is concentrated in those 20 sites: unmanned plus single link**. **Covering the highest-risk part first is the most standard resource-allocation answer in CCDE.**

<div class="zh" markdown="1">

**最容易被追问的一点**：为什么先做 OOB 的核心/无人站点，而不是全部？—— 因为 OOB 的成本与站点数线性相关，而**风险集中在"无人值守 + 单链路"这 20 个站点**。**先覆盖风险最高的部分，是 CCDE 里最标准的资源分配答案。**

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

---

## A Scenario Framework for Services and Management · 情景分析框架：服务与管理类场景的通用套路

```
① List the dependencies first (who depends on this service)
   endpoints → DHCP/DNS/NTP; devices → AAA/NTP/mirroring; business → DNS/egress
② Then write the blast radius (how far the failure spreads)
   estate-wide (DNS/AAA) > regional (a DHCP server) > single point (one device's management port)
③ Answer in layers
   foundational services → observability → policy (QoS) → management layer (automation)
④ State the cost of every choice (trade-off)
   dual stack = double cost; NAT64 = compatibility; OOB = cabling; telemetry = storage
⑤ The last mile: how to prove it
   SLO/SLI, congestion-injection acceptance, failure drills (pull power / cut links / stop AAA), alert drills
⑥ Write down open items and assumptions
   do applications listen on v6, how many classes the carrier recognises, budget and headcount, compliance retention
```

<div class="zh" markdown="1">

```
① 先列依赖（谁依赖这个服务）
   终端 → DHCP/DNS/NTP；设备 → AAA/NTP/镜像；业务 → DNS/出口
② 再写影响面（挂了以后故障半径多大）
   全域（DNS/AAA）> 区域（DHCP 服务器）> 单点（某台设备的管理口）
③ 分层作答
   基础服务 → 可观测性 → 策略（QoS）→ 管理层（自动化）
④ 每个选择都写代价（Trade-off）
   双栈 = 双份成本；NAT64 = 兼容性；OOB = 布线；遥测 = 存储
⑤ 最后一公里：如何证明
   SLO/SLI、拥塞注入验收、故障演练（拔电/断链/关 AAA）、告警演练
⑥ 写清未决项与假设
   应用是否监听 v6、运营商可识别类数、预算与人力、合规保留期
```

</div>

**In one sentence**: **services-and-management scenarios do not test whether you can configure SNMP or QoS; they test whether you can identify the two estate-wide dependencies in the scenario and fix them first when the budget is constrained.**

<div class="zh" markdown="1">

**一句话总结**：**服务与管理类情景题考的不是"你会不会配 SNMP/QoS"，而是"你能不能识别出这个场景里哪两个依赖是全域性的、并且在预算受限时先修它们"。**

</div>

---

## Chapter Summary · 本章小结

IPv6, QoS and network management look like three separate topics but are all **supporting systems**: they forward no packets, yet they decide whether the network **can be used, can express priority, and can be operated**.

<div class="zh" markdown="1">

IPv6、QoS、网络管理看似三个专题，本质上都是**支撑系统**：它们不转发包，但决定了网络**能不能被使用、能不能被表达优先级、能不能被运维**。

</div>

| Topic | Essence | Three questions you must answer | Test of success |
|------|------|------------|---------|
| **IPv6** | a different set of operating rules plus planning discipline | are all subnets /64? is ICMPv6 permitted? is dual-stack path quality at parity? | endpoints get online by themselves and the troubleshooting chain is complete |
| **QoS** | the ordering right under congestion | who may mark? how many classes? who is dropped first? | voice MOS ≥4.0 under injected congestion |
| **Management and services** | a second network that must be designed | can you log in when the service is down? where does the data come from and how long is it kept? does anybody act on the alerts? | observable, operable and provable during an outage |

<div class="zh" markdown="1">

| 主题 | 本质 | 三个必答问题 | 成败判据 |
|------|------|------------|---------|
| **IPv6** | 一套不同的运行规则 + 规划纪律 | 子网是否全 /64？ICMPv6 是否放行？双栈路径是否对等？ | 终端自己就能上网，且排障链完整 |
| **QoS** | 拥塞时的排序权 | 谁有权标记？几类？拥塞时谁先丢？ | 拥塞注入下语音 MOS ≥4.0 |
| **管理与服务** | 一张必须设计的第二网络 | 业务断时能否登录？数据从哪来、留多久？告警有人动作吗？ | 故障时仍可观测、可运维、可证明 |

</div>

**Four judgements that run through the whole chapter**:

<div class="zh" markdown="1">

**四条贯穿全章的判断**：

</div>

1. **The first priority of a supporting system is "still works when broken"** — OOB, local fallback and an independent collection tier are all corollaries of this.
2. **Do the capacity arithmetic in advance**: SNMP polling, flow export, telemetry, logs, storage and OOB bandwidth are all multiplication, not addition.
3. **The trust boundary decides whether QoS succeeds**, just as **data quality decides whether automation succeeds** (Chapter 12) — both are garbage in, garbage out.
4. **A design without measurement is not finished**: QoS needs congestion injection, dual stack needs path-parity verification, observability must prove that it can see failures when they happen.

<div class="zh" markdown="1">

1. **支撑系统的第一优先级是"故障时还能工作"** —— OOB、本地回退、独立采集层，都是这一条的推论。
2. **容量账要提前算**：SNMP 轮询、流导出、遥测、日志、存储、OOB 带宽，全部是"乘法"而不是"加法"。
3. **信任边界决定 QoS 的成败**，就像 **数据质量决定自动化的成败**（第 12 章）——两者都是"垃圾进、垃圾出"。
4. **没有测量的设计不算完成**：QoS 要拥塞注入，双栈要路径对等验证，可观测性要能证明"故障时看得见"。

</div>

From a CCDE perspective, six questions this chapter really has to answer:

<div class="zh" markdown="1">

CCDE 视角下，本章真正要回答的六个问题：

</div>

1. **Will the address plan still aggregate in ten years?** (IPv6 planning discipline)
2. **Do ICMPv6 and PMTUD survive the security policy?** (the hidden precondition of reachability)
3. **Who suffers first under congestion, and is that order designed or accidental?** (QoS trust boundary and class count)
4. **If the whole service is down, can I still log in to the devices?** (OOB and break-glass)
5. **When something breaks, can I see it within two minutes?** (observability and alert governance)
6. **Have I calculated the blast radius of these foundational services (DNS/DHCP/NTP/AAA)?** (shared dependencies)

<div class="zh" markdown="1">

1. **地址规划十年后还能汇总吗？**（IPv6 规划纪律）
2. **ICMPv6 与 PMTUD 在安全策略下还活着吗？**（可达性的隐藏前提）
3. **拥塞时谁先受苦，这个顺序是设计出来的还是碰巧的？**（QoS 信任边界与类数）
4. **业务全断时，我还能登录设备吗？**（OOB 与 break-glass）
5. **故障发生时，我能在 2 分钟内看见它吗？**（可观测性与告警治理）
6. **这些基础服务（DNS/DHCP/NTP/AAA）的故障半径，我算过吗？**（共享依赖）

</div>

Once those six are answered, which NMS you buy and which queueing algorithm you use are implementation details.

<div class="zh" markdown="1">

这六问答清楚，具体选哪家 NMS、用哪个队列算法，都只是实现细节。

</div>

> 📌 **Next chapter (Chapter 15, Scalable Enterprise Campus Architecture Design)** opens Part III: combining all the individual technologies above (Layer 2/Layer 3/wireless/security/QoS/automation) into **a scalable campus architecture** — where you will find that the hardest part of campus design was never a protocol but "**how requirements turn into modules, layers and capacity models**".

<div class="zh" markdown="1">

> 📌 **下一章（第 15 章 可扩展企业园区架构设计）** 将进入 Part III：把前面所有"单点技术"（二层/三层/无线/安全/QoS/自动化）组合成**可扩展的园区架构**——那时你会发现，园区设计里最难的从来不是某个协议，而是"**需求如何转成模块、层次与容量模型**"。

</div>
