# Chapter 11: Wireless · 第 11 章：无线

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapter 11 (pp. 542–564)

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译与精讲 | 原书第 542–564 页

</div>

---

## Topics Covered in This Chapter · 本章涵盖主题

- **IEEE 802.11 standards and spectrum**: protocol evolution, bands, channel width, real throughput
- **The time model of the wireless medium**: why airtime, not bits per second, is the "bandwidth" of wireless
- **CSMA/CA timing and frame overhead**: DIFS/backoff/preamble/ACK/aggregation, and a line-by-line breakdown of per-frame airtime
- **RF engineering fundamentals**: EIRP, link budget, wall attenuation, antenna gain and polarization, reverse-engineering the coverage radius
- **Enterprise wireless architecture**: controller deployment models, CAPWAP, FlexConnect, redundancy and the AP onboarding flow
- **Wireless security**: WPA3/SAE, 802.1X/EAP, guest networks, wIPS, threat models and compliance baselines
- **Roaming design**: Layer 2/Layer 3 roaming, PMK caching, 802.11r, mobility domains, roaming failure modes
- **High-density design**: capacity estimation, power and channel planning, BSS Coloring, OFDMA, venue engineering
- **Voice and video**: WMM/EDCA, end-to-end QoS, CAC, roaming latency budgets, wireless multicast and screen mirroring
- **Survey and acceptance**: predictive survey, AP-on-a-stick, quantifiable acceptance metrics, stress-test methods
- **Troubleshooting methodology**: the four-layer model, fault trees, command map
- **Twelve real-world case studies**: launch events, voice roaming, WAN link failure, APs that will not join, WPA3 migration, multicast meltdown, sticky clients, high-bay warehouses, Layer 3 roaming, first 6 GHz deployment, stadiums, medical IoT

<div class="zh" markdown="1">

- **IEEE 802.11 标准与频谱**：协议演进、频段、信道宽度、真实吞吐
- **无线介质的时间模型**：airtime（介质时间）为什么才是无线的"带宽"
- **CSMA/CA 时序与帧开销**：DIFS/退避/前导码/ACK/聚合，单帧 airtime 的逐项拆解
- **RF 工程基础**：EIRP、链路预算、墙体衰减、天线增益与极化、覆盖半径反推
- **企业无线架构**：控制器部署模型、CAPWAP、FlexConnect、冗余与上线流程
- **无线安全**：WPA3/SAE、802.1X/EAP、访客网络、wIPS、威胁模型与合规基线
- **漫游设计**：二层/三层漫游、PMK 缓存、802.11r、漫游域、漫游失败模式
- **高密度设计**：容量估算、功率与信道规划、BSS Coloring、OFDMA、场馆工程
- **语音与视频**：WMM/EDCA、端到端 QoS、CAC、漫游时延预算、无线组播与投屏
- **勘测与验收**：预测性勘测、AP-on-a-stick、可量化验收指标、压测方法
- **故障定位方法论**：四层排查、故障树、命令地图
- **实战案例 12 个**：发布会、语音漫游、WAN 断链、AP 不上线、WPA3 迁移、组播瘫网、粘滞客户端、立体仓库、三层漫游、6 GHz 首部署、体育馆、医疗 IoT

</div>

---

## Chapter Introduction: Twelve Counter-Intuitive Truths About Wireless · 本章导读：无线的十二个反直觉认知

The mistake a wired engineer makes most often when moving into wireless is carrying wired thinking over unchanged: assuming that adding APs adds bandwidth, that "the signal associates" means "the coverage is done", and that 5 GHz is automatically better than 2.4 GHz because it is newer. The twelve truths below are the underlying logic behind every technical detail in this chapter.

<div class="zh" markdown="1">

有线工程师转做无线，最容易犯的错是把"有线思维"直接搬过来：以为加了 AP 就有带宽、以为信号能连上就算覆盖、以为 5 GHz 比 2.4 GHz"高级所以更好"。以下七条是本章所有技术细节的底层逻辑。

</div>

### 1. Wireless "Bandwidth" Is Not a Bit Rate, It Is Airtime · 无线的"带宽"不是比特率，是介质时间

Wired is full duplex with a dedicated medium; wireless is **half duplex with a shared medium**. A single radio can serve exactly one client in any given millisecond. So a "1.2 Gbps" AP does not hand out 1200 Mbps of bandwidth — it hands out **1,000,000 microseconds of airtime per second**. **Client count, frame size, signal quality and management-frame overhead all consume that same pool of airtime.**

<div class="zh" markdown="1">

有线是全双工、独享介质；无线是**半双工、共享介质**。一块射频在同一毫秒只能服务一个客户端。所以一台标称 1.2 Gbps 的 AP，真实可分配的不是"1200 Mbps 带宽"，而是"每秒 1,000,000 微秒的 airtime"。**客户端数量、帧大小、信号质量、管理帧开销，全部在消耗同一份 airtime。**

</div>

> 💡 **In one sentence**: the scarce resource in wired networks is **bandwidth**; the scarce resource in wireless is **time**. If you cannot make that mental switch, every capacity calculation that follows will be wrong.

<div class="zh" markdown="1">

> 💡 **一句话**：有线的稀缺资源是**带宽**，无线的稀缺资源是**时间**。这个思维切换不过来，后面所有容量计算都会算错。

</div>

### 2. "It Associates" and "It Works" Are Two Different Things · 信号"能连上"和"能用"是两件事

802.11 modulation and coding is adaptive: weak signal means a lower rate. A client at −85 dBm can still associate, but it transmits at the lowest basic rate (say 6 Mbps), so a single 1500-byte packet consumes **more than 100× the airtime** of the same packet from a −55 dBm client (866 Mbps).

<div class="zh" markdown="1">

802.11 的调制编码是自适应的：信号弱就降速率。一个 -85 dBm 的客户端仍然能连上，但它用最低速率（如 6 Mbps）发送，发一个 1500 字节的包要占用比 -55 dBm 客户端（866 Mbps）**长 100 倍以上的 airtime**。

</div>

**Conclusion: a weak client does not just make itself slow, it makes the whole AP slow.** That is why enterprise designs must specify a **−67 dBm cell-edge design value** (voice −65 dBm, SNR ≥ 25 dB) instead of "as long as it associates".

<div class="zh" markdown="1">

**结论：弱信号客户端不是"自己慢"，而是"拖慢整个 AP"。** 这就是为什么企业设计必须定 **-67 dBm 边界设计值**（语音 -65 dBm、SNR ≥ 25 dB），而不是"能连上就行"。

</div>

### 3. Wider Channels Are Not Automatically Better · 信道宽度越大不等于越好

Turning 80 MHz into 160 MHz doubles the theoretical rate, but:
- the number of usable channels drops from 14 (6 GHz at 80 MHz) to 7 (at 160 MHz), so **co-channel reuse distance shrinks**;
- each channel occupies twice the spectrum, so the probability of **co-channel interference (CCI) doubles**;
- in dense deployments, real throughput often **decreases**.

<div class="zh" markdown="1">

把 80 MHz 改成 160 MHz，理论速率翻倍，但：
- 可用信道数从 14 个（6 GHz 80 MHz）降到 7 个（160 MHz），**同频复用距离缩短**；
- 每个信道占用的频谱翻倍，**同频干扰（CCI）概率翻倍**；
- 在密集部署里，实际吞吐往往**下降**。

</div>

**The standard answer for high-density is 20 MHz (in 5 GHz, sometimes 20 MHz only)**. Channel width is a spectrum-budget decision, not a performance decision.

<div class="zh" markdown="1">

**高密度场景的标准答案是 20 MHz（甚至 5 GHz 只用 20 MHz）**。信道宽度是"频谱预算"问题，不是"性能"问题。

</div>

### 4. The Bottleneck Is the Client, Not the AP · 客户端才是短板，不是 AP

An AP can do 4x4 MIMO, 160 MHz and MU-MIMO, but the phone in the user's hand is typically **2x2, 80 MHz**. Link rate is always set by the weaker of the two ends. **Buying a more expensive AP does not give users a faster network**; the value of the AP is the **number of clients it can serve** and its **uplink/multi-gigabit ports**.

<div class="zh" markdown="1">

AP 可以 4x4 MIMO、160 MHz、MU-MIMO，但用户手上的手机通常是 **2x2、80 MHz**。链路速率永远由双方较差的一方决定。**买更贵的 AP 不等于给用户更快的网**，AP 的价值在于**服务的客户端数量**与**上行链路/多千兆口**。

</div>

### 5. Management Frames and Overhead Are Not Rounding Errors · 管理帧和开销不是"零头"

The real cost of one data frame includes DIFS + random backoff + preamble (20–40 µs) + MAC header + interframe space + ACK. At 1500 bytes, overhead is roughly 20–30%; at 150 bytes (VoIP, POS, IoT heartbeats) overhead can exceed **80%**. So the "voice only needs 100 kbps" calculation is completely invalid in wireless — what matters is **how many frames per second**.

<div class="zh" markdown="1">

一个数据帧的真实开销包括：DIFS + 随机退避 + 前导码（20–40 µs）+ MAC 头 + 帧间间隔 + ACK。传 1500 字节时开销约占 20–30%；传 150 字节（VoIP、POS、IoT 心跳）时开销可能占 **80% 以上**。所以"语音只占 100 kbps"这种算法在无线上完全不成立 —— 要看**每秒多少帧**。

</div>

### 6. Roaming Is Not a Protocol Feature, It Is a Coverage Design Result · 漫游不是"协议特性"，是"覆盖设计的结果"

Even a perfect 802.11r implementation cannot rescue a bad coverage plan. Roaming must happen where **the two APs have similar signal strength (difference < 5 dB) and both are strong enough (> −67 dBm)**. If APs are configured for "maximum power, farthest reach", the client is forced to switch only after the signal is already bad, and every roam becomes a service interruption.

<div class="zh" markdown="1">

再好的 802.11r 也救不了覆盖规划错误。漫游发生的位置必须是**两个 AP 信号强度接近（差值 < 5 dB）且都足够强（> -67 dBm）的地方**。如果 AP 按"最大功率、最远覆盖"配，客户端会在信号已经很差时才被迫切换，每次漫游都是一次业务中断。

</div>

### 7. Seventy Percent of Wireless Faults Are Not on Wireless Equipment · 无线故障 70% 不在无线设备上

DHCP pool exhaustion, RADIUS timeouts, CAPWAP tunnel MTU, DNS failing to resolve the controller, upstream switch ports missing trunk VLANs, multicast/broadcast suppression — all of these "wired-side" problems surface in wireless as "the Wi-Fi is broken". **Wireless troubleshooting must watch four layers at once: RF, controller, wired side and authentication side.**

<div class="zh" markdown="1">

DHCP 池耗尽、RADIUS 超时、CAPWAP 隧道 MTU、DNS 解析不到控制器、上游交换机端口没有 trunk 全部 VLAN、组播/广播抑制——这些"有线侧"问题在无线里表现为"Wi-Fi 有问题"。**无线排障必须同时看 RF、控制器、有线侧、认证侧四层。**

</div>

### 8. Up/Downlink Asymmetry Is Physics, Not Configuration · 无线的"上下行不对称"是物理事实，不是配置问题

Phones are limited by SAR regulations to roughly **14–15 dBm** of transmit power, and some models reduce power further when the hand covers the antenna; the AP can transmit at **20 dBm**. That means:

<div class="zh" markdown="1">

手机受 SAR 法规限制，发射功率通常 **14–15 dBm**，且部分机型在天线被手握遮挡时还会降功率；AP 可以打 **20 dBm**。这意味着：

</div>

- **Good downlink coverage does not mean the uplink gets through.** A client showing "full bars" can still lose packets when it transmits; the symptom is "it associates, but pages spin and uploads crawl".
- What defines the cell boundary is not the AP's power but **whether the client can shout back**.
- The design consequence is to **turn AP power down to match the client** (5–14 dBm) so that coverage is symmetric and the cell edge becomes controllable.

<div class="zh" markdown="1">

- **下行覆盖好 ≠ 上行能通**。客户端"看到满格"却在发送时丢包，表现是"能连上、网页转圈、上传极慢"
- 决定蜂窝边界的不是 AP 的功率，而是**客户端能不能喊回来**
- 设计上必须把 AP 功率**压到与客户端相当的水平**（5–14 dBm），让两端覆盖对称，蜂窝边界才可控

</div>

> 💡 A field rule of thumb: if **downlink RSSI is −60 dBm but the retry rate exceeds 30%**, nine times out of ten it is fake coverage caused by AP power set too high and an uplink that cannot keep up.

<div class="zh" markdown="1">

> 💡 一条现场经验：**下行 RSSI -60 dBm 但重传率 > 30%** 的场景，九成是 AP 功率过高、上行不足造成的假覆盖。

</div>

### 9. Management Frames Are Fixed Cost, Independent of Traffic · 管理帧是"固定成本"，跟有没有流量无关

Even with nobody online, a radio keeps burning airtime:

<div class="zh" markdown="1">

即使没有一个人上网，一块射频也在持续消耗 airtime：

</div>

| Fixed overhead | Default | Airtime share |
|---|---|---|
| **Beacon** | One frame per SSID every 102.4 ms | Single SSID at 20 MHz lowest rate ≈ **3%–5%**; four SSIDs can reach **15%+** |
| **Probe Response** | One frame per probe request | **10%–20%** in dense client populations |
| **Management/control frames (ACK, BA, CTS)** | One per data frame | The shorter the data frame, the higher the share |

<div class="zh" markdown="1">

| 固定开销 | 默认值 | 折算 airtime |
|---|---|---|
| **Beacon** | 每 SSID 每 102.4 ms 一帧 | 单 SSID 20 MHz 最低速率 ≈ **3%–5%**；4 个 SSID 可到 **15%+** |
| **探测响应（Probe Response）** | 每个探测请求回一帧 | 客户端密集时可达 **10%–20%** |
| **管理/控制帧（ACK、BA、CTS）** | 每数据帧必带 | 数据帧越短，占比越高 |

</div>

**Conclusion: multiple SSIDs are not free.** Every additional SSID adds another Beacon (broadcast frames go out at the lowest mandatory rate and therefore occupy the most time). "One SSID per department" is a textbook design error — the correct approach is **one SSID plus dynamic VLAN/role assignment**.

<div class="zh" markdown="1">

**结论**：**多 SSID 是有成本的**。每加一个 SSID，Beacon 就多一份（广播帧以最低强制速率发送，占用时间最长）。所以"按部门开 SSID"是典型的错误设计——正确做法是**一个 SSID + 动态 VLAN/角色下发**。

</div>

### 10. Multicast on Wireless Means "Sent to Everyone at the Slowest Speed" · 无线上的组播，是"用最慢的速度发给所有人"

802.11 multicast/broadcast frames have **no ACK, no rate adaptation and no aggregation**; they can only be sent at **the BSS's lowest mandatory rate** (6 Mbps in common configurations, 1 Mbps when low rates have not been disabled).

<div class="zh" markdown="1">

802.11 的组播/广播帧**没有 ACK、没有速率自适应、不能聚合**，只能以**该 BSS 的最低强制速率**发送（常见配置下是 6 Mbps，未禁用低速率时可能是 1 Mbps）。

</div>

Do the math: a 2 Mbps multicast video stream occupies only 2 Mbps on the wired side; on the wireless side, sent at a 6 Mbps PHY rate, it **consumes more than 33% of that radio's airtime** (before counting preambles and interframe gaps). Three such streams on one AP and the radio is full.

<div class="zh" markdown="1">

换算一下：一段 2 Mbps 的组播视频流，在有线侧只占 2 Mbps；在无线侧以 6 Mbps 的 PHY 速率发送，**消耗掉该射频 33% 以上的 airtime**（还不算前导码与帧间隔）。一个 AP 上有 3 路这样的流，射频就满了。

</div>

**This explains the most counter-intuitive rule in wireless design**: **"multicast bandwidth requirement" is not a bandwidth problem at all on the wireless side, it is an airtime problem**. The countermeasure is always the same trio: access-layer IGMP Snooping (stop the flooding) → controller **multicast-to-unicast** (send at unicast rates) → where needed, multicast direct/local switching so the AP replicates locally.

<div class="zh" markdown="1">

**这解释了无线设计里最反直觉的一条**：**"组播带宽需求"在无线侧根本不是带宽问题，是 airtime 问题**。对策永远是三件套：接入层 IGMP Snooping（不让它泛洪）→ 控制器**组播转单播**（用单播速率发）→ 必要时用组播直通/Direct 模式在 AP 本地复制。

</div>

### 11. You Cannot Design Client Behaviour, You Can Only Steer It · 客户端行为你设计不了，只能"引导"

Half of the control in wireless sits in the endpoint: roaming decisions, band preference, power-save strategy, probe frequency, private MAC randomization — all decided by the handset vendor's algorithms, and **wildly different between vendors**.

<div class="zh" markdown="1">

无线的另一半控制权在终端手里：漫游决策、频段选择、省电策略、探测频率、私有 MAC 随机化，全部由终端厂商的算法决定，且**不同品牌差异巨大**。

</div>

| Client behaviour | What design can do |
|---|---|
| Sticky client (refuses to leave) | MIN RSSI forced disassociation + 802.11v BTM steering |
| 2.4 GHz addiction | Band steering (some clients refuse) + simply do not broadcast a 2.4 GHz SSID |
| Private MAC randomization | Use 802.1X instead of MAC authentication; shorten DHCP leases; drop MAC-binding policies |
| Aggressive power save (PSM/U-APSD) | Tune DTIM interval; support WMM-PS for voice |
| Probe storms | Disable low rates, enable probe suppression, reduce SSID count |

<div class="zh" markdown="1">

| 终端行为 | 设计上能做的 |
|---|---|
| Sticky Client（赖着不走） | MIN RSSI 强制断开 + 802.11v BTM 引导 |
| 只爱 2.4 GHz | Band Steering（部分终端拒绝）+ 干脆不广播 2.4 GHz SSID |
| 私有 MAC 随机化 | 用 802.1X 而非 MAC 认证；DHCP 租期缩短；关闭 MAC 绑定类策略 |
| 激进省电（PSM/U-APSD） | 调整 DTIM 周期；对语音用 WMM-PS 支持 |
| 探测风暴 | 关闭低速率、开启探测抑制、减少 SSID 数 |

</div>

**Design principle**: betting on "the client will optimize itself" always fails; but the only legitimate levers for steering are **RF parameters + standard mechanisms (k/v/r) + coverage shape**, never "asking users to change their settings".

<div class="zh" markdown="1">

**设计原则**：把希望寄托在"终端会自己优化"上必然失败；但要引导，也只能通过**RF 参数 + 标准机制（k/v/r）+ 覆盖形状**去引导，而不是"要求用户改设置"。

</div>

### 12. Wireless Acceptance Tests the Business, Not the Signal · 无线验收的对象是"业务"，不是"信号"

"All green on the coverage map" is the least convincing acceptance evidence there is. The metrics that actually protect you are all **business outcomes**:

<div class="zh" markdown="1">

"覆盖图上全绿"是最没有说服力的验收材料。真正能保护你的验收指标都是**业务结果**：

</div>

| Acceptance object | Metric | Why |
|---|---|---|
| Access | Association success > 99%, DHCP success > 99% | The user's first door |
| Service availability | Success rate and P95 latency of key applications at peak | What the user actually cares about |
| Capacity | Peak airtime < 60%, clients per AP below design value | Leaves headroom for bursts |
| Mobility | Roaming interruption < 50 ms (voice) / < 200 ms (data) | The only hard metric in mobile scenarios |
| Stability | 24 h retry rate < 10%, no frequent DFS channel changes | Long-term experience |

<div class="zh" markdown="1">

| 验收对象 | 指标 | 为什么 |
|---|---|---|
| 接入能力 | 关联成功率 > 99%、DHCP 成功率 > 99% | 用户第一道门 |
| 业务可用 | 关键应用在峰值时段的成功率/时延 P95 | 才是用户在意的 |
| 容量 | 峰值 airtime < 60%、单 AP 客户端不超设计值 | 保证还有余量应对突发 |
| 移动性 | 漫游中断 < 50 ms（语音）/ < 200 ms（数据） | 移动场景的唯一硬指标 |
| 稳定性 | 24h 重传率 < 10%、无频繁 DFS 切换 | 长期体验 |

</div>

**Acceptance must be performed at the worst moment** (30 minutes after the working day starts, just before a meeting, at the moment a hall empties). Beautiful numbers from an empty building guarantee nothing in production.

<div class="zh" markdown="1">

**验收必须在最坏时刻做**（上班后 30 分钟、会议开始前、散场瞬间）。空场测试出来的漂亮数字，对生产没有任何保证。

</div>

---

## Wireless Design Methodology (Six Steps) · 无线设计方法论（六步）

The CCDE does not test how to configure an SSID; it tests how, given a business scenario, you derive how many APs, how many controllers, which bands and which security policy are needed. The flow below can be dropped straight into a design document.

<div class="zh" markdown="1">

CCDE 不考"怎么配 SSID"，考的是"给一个业务场景，你怎么算出需要多少 AP、多少控制器、什么频段、什么安全策略"。下面这套流程可以直接放进设计文档。

</div>

| Step | What to do | Deliverable | Common mistake |
|------|---------|--------|---------|
| **① Business profile** | Who uses it, which applications, concurrency ratio, peak hours | Application list + concurrency assumptions | Using total headcount as the concurrency number (real concurrency is 30–60%) |
| **② Capacity estimation** | Size APs from an **airtime budget**, not from floor area | APs per zone, client ceiling per AP | "50 users per AP" by gut feeling, with no application analysis |
| **③ Coverage design** | Set edge RSSI/SNR, then derive AP power and placement | Coverage plots + power settings | Chasing "maximum reach", leaving roaming points with terrible signal |
| **④ Spectrum planning** | Choose bands, channel width, channel reuse plan | Channel assignment table | Everything at 80 MHz, causing CCI |
| **⑤ Architecture selection** | Centralized/distributed/cloud; Local/FlexConnect | Controller and AP modes, redundancy plan | Centralized tunnels at branches, so a WAN cut takes everything down |
| **⑥ Validation loop** | Survey, acceptance metrics, monitoring baseline | Survey report + acceptance sheet + alarm thresholds | Testing only "can it associate", never airtime or roaming |

<div class="zh" markdown="1">

| 步骤 | 要做的事 | 产出物 | 常见错误 |
|------|---------|--------|---------|
| **① 业务画像** | 谁在用、用什么应用、并发比例、高峰时段 | 应用清单 + 并发率假设 | 直接用"员工总数"当并发数（实际并发率 30–60%） |
| **② 容量估算** | 按 **airtime 预算** 算 AP 数，而非按面积 | 每区域 AP 数、每 AP 客户端上限 | 按"每 AP 50 人"拍脑袋，不看应用 |
| **③ 覆盖设计** | 定边界 RSSI/SNR，反推 AP 功率与位置 | 覆盖图 + 功率设置 | 追求"最远覆盖"，结果漫游点信号太差 |
| **④ 频谱规划** | 选频段、定信道宽度、定信道复用图 | 信道分配表 | 全用 80 MHz 导致 CCI |
| **⑤ 架构选型** | 集中式/分布式/云、Local/FlexConnect | 控制器与 AP 模式、冗余方案 | 分支用集中式隧道，WAN 断全线瘫 |
| **⑥ 验证闭环** | 勘测、验收指标、监控基线 | 勘测报告 + 验收表 + 告警阈值 | 只测"能连上"，不测 airtime 与漫游 |

</div>

**One iron law runs through all of it**: **compute airtime first, then AP count, and only then talk about coverage.** Reversing the order (draw coverage first, think about capacity later) is the most common cause of rework in campus wireless projects.

<div class="zh" markdown="1">

**贯穿全程的一条铁律**：**先算 airtime，再算 AP 数，最后才谈覆盖。** 顺序颠倒（先画覆盖、再想容量）是园区无线项目最常见的返工原因。

</div>

### Quick Airtime Budget Math (a formula you can cite directly in a design document) · airtime 预算速算（设计文档里可以直接引用的公式）

```
Airtime available per AP per second = 1,000,000 µs
Actually usable (after management frames/Beacon/probes/retries) ≈ 60% ~ 75%
Per-client throughput ≈ AP effective throughput × (that client's airtime share)
```

<div class="zh" markdown="1">

```
单个 AP 每秒可用 airtime = 1,000,000 µs
实际可用（扣管理帧/Beacon/探测/重传）≈ 60% ~ 75%
单客户端可用吞吐 ≈ AP 有效吞吐 × (该客户端 airtime 占比)
```

</div>

| Scenario | AP effective throughput (real TCP) | Target clients per AP | Per-user available |
|------|----------------------|----------------|---------|
| Office (web/mail/video conferencing) | 350–450 Mbps (5 GHz 40 MHz, 2SS) | 30–40 | 10–15 Mbps |
| High density (auditorium/classroom) | 300–400 Mbps (5 GHz 20 MHz) | 60–80 (bursty applications only) | 4–6 Mbps |
| Voice-first (warehouse/healthcare) | 250–350 Mbps | 20–25 | Guarantee < 1% airtime per call |
| IoT/industrial | 100–200 Mbps (2.4 GHz) | 100+ (small frames dominate) | Very low bandwidth but very many frames |

<div class="zh" markdown="1">

| 场景 | AP 有效吞吐（真实 TCP） | 目标客户端数/AP | 人均可用 |
|------|----------------------|----------------|---------|
| 办公（网页/邮件/视频会议） | 350–450 Mbps（5 GHz 40 MHz, 2SS） | 30–40 | 10–15 Mbps |
| 高密度（会场/教室） | 300–400 Mbps（5 GHz 20 MHz） | 60–80（仅短时突发应用） | 4–6 Mbps |
| 语音优先（仓储/医疗） | 250–350 Mbps | 20–25 | 保证每呼叫 < 1% airtime |
| IoT/工业 | 100–200 Mbps（2.4 GHz） | 100+（小包为主） | 极低带宽但极多帧 |

</div>

> ⚠️ The table above is a **design starting point**, not a guarantee. Real projects must be corrected with survey data (see "Survey and Acceptance"). Any vendor claim of "200 users per AP" is a laboratory number measured with **zero retries, no interference and uniformly tiny flows**.

<div class="zh" markdown="1">

> ⚠️ 上表是**设计起点**，不是保证值。真实项目必须用勘测数据校正（见"勘测与验收"一节）。任何"每 AP 支持 200 用户"的厂商标称值，都是在**零重传、无干扰、全小流量**条件下的实验室数字。

</div>

### Converting "Application Bandwidth" into Airtime: Frame by Frame · 把"业务带宽"换算成 airtime：逐帧算一遍

This is the single exercise in the chapter most worth doing by hand, because **the scarce resource in wireless is time** while applications speak in bits per second — and the conversion has to pass through a layer of "frames per second".

<div class="zh" markdown="1">

这是整章最值得亲手算一次的练习。因为**无线的稀缺资源是时间**，而应用给的是"每秒多少比特"，中间必须经过"每秒多少个帧"这一层。

</div>

**Example: how much airtime does a 4 Mbps video stream consume on a 5 GHz, 20 MHz, 11ax, 2SS AP?**

<div class="zh" markdown="1">

**例：一个 4 Mbps 的视频流，在一个 5 GHz 20 MHz / 11ax / 2SS 的 AP 上占多少 airtime？**

</div>

```
① Framing: Ethernet MTU 1500 B → 802.11 frame payload ≈ 1500 B
② PHY time per frame (MCS 7, 20 MHz, 2SS ≈ 86 Mbps PHY rate)
   1500 B = 12000 bit ÷ 86 Mbps ≈ 140 µs (data portion)
③ Fixed overhead per frame
   Preamble (11ax HE-SU) ≈ 40 µs
   MAC header + FCS ≈ 36 B → 3 µs
   SIFS + Block ACK ≈ 16 + 32 µs ≈ 48 µs
   Average backoff (half the contention window) ≈ 67 µs/frame (longer under heavy contention)
   → total fixed overhead ≈ 160 µs
④ Total per frame ≈ 140 + 160 ≈ 300 µs, of which "payload" is only 47%
⑤ 4 Mbps needs 4000000 ÷ (1500×8) ≈ 333 frames/s
⑥ airtime = 333 × 300 µs ≈ 100,000 µs/s ≈ 10% of the radio
```

<div class="zh" markdown="1">

```
① 帧化：以太网 MTU 1500 B → 802.11 帧载荷 ≈ 1500 B
② 每帧 PHY 时间（MCS 7, 20 MHz, 2SS ≈ 86 Mbps 的 PHY 速率）
   1500 B = 12000 bit ÷ 86 Mbps ≈ 140 µs（数据部分）
③ 每帧固定开销
   前导码（11ax HE-SU） ≈ 40 µs
   MAC 头 + FCS ≈ 36 B → 3 µs
   SIFS + Block ACK ≈ 16 + 32 µs ≈ 48 µs
   平均退避（竞争窗口一半） ≈ 67 µs / 帧（争用激烈时更长）
   → 固定开销合计 ≈ 160 µs
④ 单帧总占用 ≈ 140 + 160 ≈ 300 µs，其中"有效载荷"只占 47%
⑤ 4 Mbps 需要 4000000 ÷ (1500×8) ≈ 333 帧/秒
⑥ airtime = 333 × 300 µs ≈ 100,000 µs/s ≈ 10% 的射频
```

</div>

**Now apply the same arithmetic to 150-byte small frames (VoIP, PDA scanning, IoT heartbeats)**:

<div class="zh" markdown="1">

**把同样的算法用在 150 字节的小包（VoIP、PDA 扫码、IoT 心跳）上**：

</div>

```
150 B ≈ 1200 bit ÷ 86 Mbps ≈ 14 µs
Fixed overhead is still ≈ 160 µs (essentially unchanged!)
→ payload is only 8% of the 174 µs per frame
For 100 kbps (G.711 voice plus headers) ≈ 100 frames/s
→ airtime ≈ 17,400 µs ≈ 1.7% per voice call
```

<div class="zh" markdown="1">

```
150 B ≈ 1200 bit ÷ 86 Mbps ≈ 14 µs
固定开销仍是 ≈ 160 µs（几乎不变！）
→ 单帧 174 µs 中，有效载荷只占 8%
若要 100 kbps（G.711 语音 + 头开销）≈ 100 帧/秒
→ airtime ≈ 17,400 µs ≈ 1.7% 每通语音
```

</div>

**This comparison is the single most important page in wireless design**:

<div class="zh" markdown="1">

**这张对比就是无线设计最重要的一张纸**：

</div>

| Frame size | Payload share | Airtime sensitivity | Design response |
|---|---|---|---|
| 1500 B (bulk downloads, video) | ≈ 45%–60% | Low | Watch total bandwidth and channel width |
| 500 B (mixed web) | ≈ 25%–35% | Medium | Watch client count and retries |
| 150 B and below (voice, scanners, IoT) | **5%–15%** | **Extremely high** | Watch **pps**, aggregation, OFDMA, disabled low rates |

<div class="zh" markdown="1">

| 帧大小 | 有效载荷占比 | airtime 敏感度 | 设计对策 |
|---|---|---|---|
| 1500 B（大包下载、视频） | ≈ 45%–60% | 低 | 关注总带宽与信道宽度 |
| 500 B（网页混合） | ≈ 25%–35% | 中 | 关注客户端数与重传 |
| 150 B 及以下（语音、扫码、IoT） | **5%–15%** | **极高** | 关注 **pps**、聚合、OFDMA、禁低速率 |

</div>

**So the sentence "we need 100 Mbps of bandwidth" must be rewritten in wireless as**:

<div class="zh" markdown="1">

**所以"我们有 100 Mbps 带宽需求"这句话在无线里必须改写为**：

</div>

> "At peak there are X clients, each generating Y pps at an average frame size of Z bytes and a retry rate of R; the resulting peak airtime demand is ______ %, and the target is to stay under 60%."

<div class="zh" markdown="1">

> "峰值有 X 个客户端，每客户端 Y pps，平均帧大小 Z 字节，重传率 R；折算峰值 airtime 需求 = ______ %，目标不超过 60%。"

</div>

If you cannot answer that sentence, the capacity design is not finished.

<div class="zh" markdown="1">

答不出这句话，容量设计就还没做完。

</div>

### Wireless Requirements Checklist (page one of the design document) · 无线需求收集清单（设计文档第 1 页）

In CCDE scenarios the wireless information is always half-given and half-withheld. The checklist below exists to drive the **follow-up questions**:

<div class="zh" markdown="1">

CCDE 场景题里，无线部分的信息永远是"半给半不给"。下面这份清单是用来**主动追问**的：

</div>

| Category | What must be pinned down | What it changes once known |
|---|---|---|
| **User scale** | **Peak concurrent users** per zone (not headcount), concurrency assumptions | AP count, DHCP pools, controller licences |
| **Endpoint mix** | Ratio of laptops/phones/tablets/IoT; 11ax/6E support; private MAC randomization | Band policy, security mode, roaming mechanism |
| **Application profile** | Bandwidth/latency/jitter needs of key apps; voice/video/mirroring/AR | CAC, QoS, airtime budget |
| **Business continuity** | Can the business stop when the WAN link fails? For how long? | FlexConnect + local auth/DHCP |
| **Physical conditions** | Ceiling height, partition materials, racking, metal, glass, cabling feasibility, ceiling access | Coverage model, AP placement, antenna type |
| **Compliance** | Local regulatory baseline / PCI-DSS / HIPAA, guest log retention, whether wireless is banned | Encryption mode, auditing, SSID policy |
| **Operations capability** | How many network engineers? 7×24? Is there a NOC? | Centralized vs cloud-managed, monitoring depth |
| **Growth forecast** | Three-year endpoint growth, new floors or sites | Controller headroom, licence purchases |

<div class="zh" markdown="1">

| 类别 | 必须问清 | 拿到后影响什么 |
|---|---|---|
| **用户规模** | 各区域**峰值并发人数**（不是总人数）、并发率假设 | AP 数量、DHCP 池、控制器许可 |
| **终端构成** | 笔记本/手机/平板/IoT 比例；是否支持 11ax/6E；是否自带私有 MAC 随机化 | 频段策略、安全模式、漫游机制 |
| **应用画像** | 关键应用的带宽/时延/抖动要求；有无语音/视频/投屏/AR | CAC、QoS、airtime 预算 |
| **业务连续性** | WAN 断链能否停业？可接受时长？ | FlexConnect + 本地认证/DHCP |
| **空间条件** | 层高、隔断材质、货架、金属、玻璃、是否可布线、是否可上吊顶 | 覆盖模型、AP 位置、天线类型 |
| **合规要求** | 等保/PCI-DSS/HIPAA、访客日志留存、是否禁无线 | 加密模式、审计、SSID 策略 |
| **运维能力** | 有几个网络工程师？是否 7×24？是否有 NOC | 集中 vs 云管、监控深度 |
| **增长预期** | 3 年终端增长、是否新增楼层/站点 | 控制器容量余量、许可采购 |

</div>

### Wireless Design Document Skeleton (a table of contents you can reuse) · 无线设计文档骨架（可直接套用的目录）

```
1. Business goals and scope        (which zones, which services, SLA)
2. Requirements and assumptions    (concurrency, endpoint matrix, growth; state assumptions explicitly)
3. Capacity design                 (airtime budget table → APs per zone → client ceiling per AP)
4. Coverage design                 (edge RSSI/SNR, AP placement plot, antenna selection, power values)
5. Spectrum design                 (band split, channel width, channel plan, 6 GHz strategy)
6. Architecture design             (controller deployment, Local/Flex, redundancy, WAN dependency, tunnel bandwidth)
7. Security design                 (SSID matrix, encryption, authentication flow, guest, IoT isolation, compliance)
8. Roaming design                  (mobility domain, Layer 2 boundary, k/v/r, voice specifics)
9. QoS design                      (WMM mapping, end-to-end DSCP, CAC parameters)
10. Wired and IP planning          (AP management VLAN, service VLANs, mGig, PoE, DHCP/DNS)
11. High availability and degradation (WLC HA, WAN-cut behaviour, DFS events, AP failure redundancy)
12. Acceptance criteria            (quantifiable metrics + test methods + definition of the worst moment)
13. Operations and monitoring      (alarm thresholds, backups, upgrade windows, fault severity levels)
14. Risks and open items           (explicitly state what this design does not cover or depends on third parties)
```

<div class="zh" markdown="1">

```
1. 业务目标与范围        （哪些区域、哪些业务、SLA）
2. 需求与假设            （并发率、终端矩阵、增长预期，明确列出假设）
3. 容量设计              （airtime 预算表 → 每区域 AP 数 → 每 AP 客户端上限）
4. 覆盖设计              （边界 RSSI/SNR、AP 位置图、天线选型、功率值）
5. 频谱设计              （频段分工、信道宽度、信道分配图、6 GHz 策略）
6. 架构设计              （控制器部署、Local/Flex、冗余、WAN 依赖、隧道带宽）
7. 安全设计              （SSID 矩阵、加密、认证流程、访客、IoT 隔离、合规）
8. 漫游设计              （移动域、二层域边界、k/v/r、语音专项）
9. QoS 设计              （WMM 映射、DSCP 端到端、CAC 参数）
10. 有线与 IP 规划       （AP 管理 VLAN、业务 VLAN、mGig、PoE、DHCP/DNS）
11. 高可用与降级策略     （WLC HA、WAN 断链行为、DFS 事件、AP 故障冗余度）
12. 验收标准             （可量化指标 + 测试方法 + 最坏时刻定义）
13. 运维与监控           （告警阈值、备份、升级窗口、故障分级）
14. 风险与未决项         （明确写出"本设计未覆盖/依赖第三方"的部分）
```

</div>

> 💡 **Item 14 reveals the most about design maturity**: a design document that cannot state where its own boundaries lie will always end up absorbing blame during implementation.

<div class="zh" markdown="1">

> 💡 **第 14 项最能体现设计水平**：一份说不出"自己边界在哪"的设计文档，在实施阶段一定会被动背锅。

</div>

---

## Foundation Topics · 基础内容

### IEEE 802.11 Standards and Protocols · IEEE 802.11 标准与协议

| Standard | Alias | Band | Theoretical max rate | Key modulation/technology | Channel width | Practical meaning |
|------|------|------|------------|-------------|---------|---------|
| **802.11b** | — | 2.4 GHz | 11 Mbps | DSSS/CCK | 20 MHz | Obsolete, legacy IoT only |
| **802.11a** | — | 5 GHz | 54 Mbps | OFDM | 20 MHz | First 5 GHz standard, created the 5 GHz ecosystem |
| **802.11g** | — | 2.4 GHz | 54 Mbps | OFDM | 20 MHz | Backward compatible with b, which introduced 2.4 GHz protection overhead |
| **802.11n** | Wi-Fi 4 | 2.4/5 GHz | 600 Mbps | OFDM + MIMO (4SS) | 20/40 MHz | Established MIMO and frame aggregation (A-MPDU); efficiency rose for the first time |
| **802.11ac** | Wi-Fi 5 | 5 GHz | 6.9 Gbps | OFDM + DL MU-MIMO | 20/40/80/160 MHz | 5 GHz only; 80 MHz became mainstream |
| **802.11ax** | Wi-Fi 6 / 6E | 2.4/5/6 GHz | 9.6 Gbps | **OFDMA** + UL/DL MU-MIMO + BSS Coloring + TWT | 20/40/80/160 MHz | The point is **high-density efficiency**, not peak rate |
| **802.11be** | Wi-Fi 7 | 2.4/5/6 GHz | 46 Gbps | OFDMA + **MLO** + 4096-QAM | 20/40/80/160/320 MHz | Multi-link aggregation improves latency and reliability together |

<div class="zh" markdown="1">

| 标准 | 别名 | 频段 | 理论最大速率 | 关键调制/技术 | 信道宽度 | 现实意义 |
|------|------|------|------------|-------------|---------|---------|
| **802.11b** | — | 2.4 GHz | 11 Mbps | DSSS/CCK | 20 MHz | 已淘汰，仅遗留 IoT |
| **802.11a** | — | 5 GHz | 54 Mbps | OFDM | 20 MHz | 首个 5 GHz 标准，开创 5 GHz 生态 |
| **802.11g** | — | 2.4 GHz | 54 Mbps | OFDM | 20 MHz | 与 b 兼容，导致 2.4 GHz 保护机制开销 |
| **802.11n** | Wi-Fi 4 | 2.4/5 GHz | 600 Mbps | OFDM + MIMO（4SS） | 20/40 MHz | MIMO 与帧聚合（A-MPDU）奠基，效率首次上来 |
| **802.11ac** | Wi-Fi 5 | 5 GHz | 6.9 Gbps | OFDM + DL MU-MIMO | 20/40/80/160 MHz | 只做 5 GHz，80 MHz 成为主流 |
| **802.11ax** | Wi-Fi 6 / 6E | 2.4/5/6 GHz | 9.6 Gbps | **OFDMA** + UL/DL MU-MIMO + BSS Coloring + TWT | 20/40/80/160 MHz | 重点不是峰值而是**高密度效率** |
| **802.11be** | Wi-Fi 7 | 2.4/5/6 GHz | 46 Gbps | OFDMA + **MLO** + 4096-QAM | 20/40/80/160/320 MHz | 多链路聚合，时延与可靠性同时改善 |

</div>

**How to read this table correctly**: do not memorise the peak rates (those are laboratory numbers with 8 spatial streams, 160 MHz, a perfect channel and zero overhead). Memorise **which structural problem each generation solved**:

<div class="zh" markdown="1">

**读这张表的正确姿势**：不要记峰值速率（那是 8 空间流、160 MHz、理想信道、零开销的实验室数字）。要记**每一代解决了什么结构性问题**：

</div>

| Generation | Core problem solved | Why it matters |
|------|--------------|-----------|
| 11n | MIMO + aggregation to raise **single-user efficiency** | Cut overhead from 70% to 30%; wireless became usable for the first time |
| 11ac | **Wide channels** to buy peak rate | Peaks looked good, but in high density they created CCI |
| 11ax | **OFDMA** so multiple users share one transmission opportunity | Genuinely solved "more people, slower"; the watershed for high density |
| 11be | **MLO** to use several bands simultaneously | Lower latency and shorter roaming interruptions; benefits AR/VR and industrial use cases |

<div class="zh" markdown="1">

| 代际 | 解决的核心问题 | 为什么重要 |
|------|--------------|-----------|
| 11n | 用 MIMO + 聚合提高**单用户效率** | 把开销从 70% 降到 30%，第一次让无线"能用" |
| 11ac | 用**宽信道**换峰值速率 | 峰值好看，但高密度下反而制造 CCI |
| 11ax | 用 **OFDMA** 让多用户共享同一次传输机会 | 真正解决"人多就慢"，是高密度场景的分水岭 |
| 11be | 用 **MLO** 同时用多个频段 | 降低时延与漫游中断，AR/VR、工业场景受益 |

</div>

> ⚠️ **The trap designers fall into most often**: the customer says "we deployed Wi-Fi 6, why is it still slow". The usual answers are: the endpoints are Wi-Fi 4/5, the channel width was set to 80 MHz causing CCI, or the AP uplink is only 1 Gbps. **Wi-Fi 6 gains (OFDMA/BSS Coloring) only materialise when the far end supports them and the channel plan is correct**.

<div class="zh" markdown="1">

> ⚠️ **设计上最容易踩的坑**：客户说"我们上了 Wi-Fi 6，为什么还是慢"。答案通常是：终端是 Wi-Fi 4/5、信道宽度设成 80 MHz 导致 CCI、或者 AP 上行只有 1 Gbps —— **Wi-Fi 6 的增益（OFDMA/BSS Coloring）只有在对端也支持、且信道规划正确时才生效**。

</div>

#### How the Rate Is Calculated (a mandatory interview and design-review question) · 速率是怎么算出来的（面试与设计答辩必问）

```
Theoretical PHY rate = subcarriers × bits per subcarrier (MCS) × spatial streams × coding rate / symbol time
```

<div class="zh" markdown="1">

```
理论 PHY 速率 = 子载波数 × 每子载波比特数(MCS) × 空间流数 × 编码率 / 符号时间
```

</div>

In practice you only need the "common combinations" table below (2 spatial streams, which is the ceiling for the vast majority of endpoints):

<div class="zh" markdown="1">

工程上只需要记下面这张"常见组合"表（2 空间流，这是绝大多数终端的天花板）：

</div>

| Standard | Channel width | MCS | Theoretical PHY | Real TCP throughput (single client) |
|------|---------|-----|---------|----------------------|
| 11ac | 20 MHz | 9 | 173 Mbps | 90–110 Mbps |
| 11ac | 40 MHz | 9 | 400 Mbps | 200–240 Mbps |
| 11ac | 80 MHz | 9 | 867 Mbps | 420–500 Mbps |
| 11ax | 20 MHz | 11 | 287 Mbps | 150–180 Mbps |
| 11ax | 40 MHz | 11 | 574 Mbps | 300–350 Mbps |
| 11ax | 80 MHz | 11 | 1201 Mbps | 600–700 Mbps |
| 11ax | 160 MHz | 11 | 2402 Mbps | 900–1100 Mbps (and almost impossible to reuse in high density) |

<div class="zh" markdown="1">

| 标准 | 信道宽度 | MCS | 理论 PHY | 实际 TCP 吞吐（单客户端） |
|------|---------|-----|---------|----------------------|
| 11ac | 20 MHz | 9 | 173 Mbps | 90–110 Mbps |
| 11ac | 40 MHz | 9 | 400 Mbps | 200–240 Mbps |
| 11ac | 80 MHz | 9 | 867 Mbps | 420–500 Mbps |
| 11ax | 20 MHz | 11 | 287 Mbps | 150–180 Mbps |
| 11ax | 40 MHz | 11 | 574 Mbps | 300–350 Mbps |
| 11ax | 80 MHz | 11 | 1201 Mbps | 600–700 Mbps |
| 11ax | 160 MHz | 11 | 2402 Mbps | 900–1100 Mbps（且几乎无法在高密度复用） |

</div>

**Rules of thumb**: **real TCP throughput ≈ theoretical PHY rate × 50%–60%** (half duplex, ACKs, backoff, management frames and retries all included). Every vendor figure of "X Gbps per AP" is a PHY number; when you write a design document you must convert it to TCP before doing capacity math.

<div class="zh" markdown="1">

**经验换算**：**实际 TCP 吞吐 ≈ 理论 PHY 速率 × 50%–60%**（半双工、ACK、退避、管理帧、重传全部算在内）。所有厂商的"每 AP 支持 X Gbps"都用的是 PHY 值，你写设计文档时必须换算成 TCP 值再算容量。

</div>

### CSMA/CA: Why Wireless Contends Instead of Scheduling · CSMA/CA：无线为什么"抢"而不"排"

Wired Ethernet is full duplex and has no collisions; wireless shares a medium and must **listen before talking**. 802.11 media access is **CSMA/CA (collision avoidance)** because a radio **cannot transmit and listen at the same time** (its own signal would drown out the other party), so the collision detection of CSMA/CD is impossible.

<div class="zh" markdown="1">

有线以太网全双工，不存在冲突；无线共享介质，必须**先听后说**。802.11 的介质访问是 **CSMA/CA（冲突避免）**，因为无线**无法边发边听**（自己的信号会盖住对方），所以不能用 CSMA/CD 的冲突检测。

</div>

**The complete timeline of one successful transmission**:

<div class="zh" markdown="1">

**一次成功发送的完整时序**：

</div>

```
[idle] DIFS(34 µs) [random backoff N×SlotTime(9 µs)] [preamble+PLCP] [data frame] SIFS(16 µs) [ACK]
       ↑                                     ↑
   must sense the channel idle           the receiver answers first (SIFS is shorter than DIFS,
   for one DIFS period                    so its ACK outruns other stations' data frames)
```

<div class="zh" markdown="1">

```
[空闲] DIFS(34 µs) [随机退避 N×SlotTime(9 µs)] [前导码+PLCP] [数据帧] SIFS(16 µs) [ACK]
       ↑                                     ↑
   必须听到信道空闲                      接收方优先回复（SIFS 比 DIFS 短，
   一个 DIFS 时间                        所以 ACK 抢得过别人的数据帧）
```

</div>

| Parameter | 20 MHz value | Design implication |
|---|---|---|
| **Slot Time** | 9 µs (5 GHz) / 20 µs (2.4 GHz) | Granularity of backoff; longer slots in 2.4 GHz mean lower efficiency |
| **SIFS** | 16 µs | Priority gap for ACK, CTS, fragment bursts |
| **DIFS** | 34 µs (5 GHz) | Mandatory wait before contending for a data frame |
| **CWmin** | 15 (smaller for voice/video queues) | The "more urgent" the queue, the smaller the window and the faster it wins |
| **NAV (virtual carrier sense)** | Set by the Duration field | The time that has been "reserved"; other stations must stay silent |

<div class="zh" markdown="1">

| 参数 | 20 MHz 值 | 设计含义 |
|---|---|---|
| **Slot Time** | 9 µs（5 GHz）/ 9 µs（2.4 GHz 为 20 µs） | 退避的粒度；2.4 GHz 的槽更长 → 效率更低 |
| **SIFS** | 16 µs | ACK、CTS、分片突发的优先间隔 |
| **DIFS** | 34 µs（5 GHz） | 数据帧竞争前必须等待 |
| **最小竞争窗口 CWmin** | 15（语音/视频队列更小） | 队列越"急"，窗口越小，抢得越快 |
| **NAV（虚拟载波侦听）** | 由 Duration 字段设定 | 被"预约"的时间，其他站必须沉默 |

</div>

**Four design facts that follow**:

<div class="zh" markdown="1">

**四个由此推出的设计事实**：

</div>

1. **More clients means more backoff collisions and lower efficiency** — and the degradation is non-linear. With one client efficiency is close to theoretical; with 30 clients contending at once, **collisions and backoff eat 20%–40% of airtime**.
2. **Small-frame workloads are inherently inefficient** — because DIFS + backoff + preamble + SIFS + ACK is a fixed per-frame cost (see the worked example above).
3. **RTS/CTS is not "more reliable", it is "more expensive"** — it spends two frames to avoid the collision cost of a long data frame, so it only pays off with large frames plus hidden terminals; enabling it in dense small-packet environments reduces capacity.
4. **2.4 GHz uses a 20 µs slot time** — the same frame carries more fixed overhead on 2.4 GHz, and that is the second reason 2.4 GHz is slow (the first being interference).

<div class="zh" markdown="1">

1. **客户端越多，退避碰撞越多，效率越低** —— 这不是线性劣化。1 个客户端时效率接近理论值，30 个客户端同时争用时，**碰撞与退避会吃掉 20%–40% 的 airtime**。
2. **小包多的场景效率天然差** —— 因为 DIFS + 退避 + 前导码 + SIFS + ACK 是每帧固定成本（见上节算例）。
3. **RTS/CTS 不是"更可靠"，而是"更贵"** —— 它用两帧换掉长数据帧的碰撞代价，只在大帧 + 隐藏终端场景划算；高密度小包场景开启反而降容量。
4. **2.4 GHz 的 Slot Time 是 20 µs** —— 同样的帧在 2.4 GHz 上固定开销更大，这是"2.4 GHz 慢"的第二个原因（第一个是干扰）。

</div>

#### Hidden Terminals and Exposed Terminals · 隐藏终端与暴露终端

| Problem | Mechanism | Symptom | Countermeasure |
|---|---|---|---|
| **Hidden terminal** | A and B can both reach the AP but cannot hear each other → they transmit simultaneously and collide at the AP | High retries, rate collapses, some clients are "always slow" | RTS/CTS (enable in small areas), lower power for more predictable coverage, higher AP density |
| **Exposed terminal** | C hears B transmitting and assumes the channel is busy when it is not | It stays silent while idle, wasting throughput | Also relieved by "smaller cells + higher reuse" |

<div class="zh" markdown="1">

| 问题 | 机制 | 现象 | 对策 |
|---|---|---|---|
| **隐藏终端** | A、B 都能与 AP 通信，但互相听不到 → 同时发送在 AP 处碰撞 | 高重传、速率骤降、部分客户端"总是慢" | RTS/CTS（小范围启用）、降低功率让覆盖更可预测、增加 AP 密度 |
| **暴露终端** | C 听到 B 在发送就以为信道忙，其实不冲突 | 明明空闲却不敢发，吞吐浪费 | 同样靠"缩小蜂窝 + 提高复用"缓解 |

</div>

> 💡 **Hidden terminals are another consequence of too much power**: the higher the power, the more neighbours you can hear — but also the more "cannot hear yet can still interfere" relationships you create. **Low-power design for high density improves the hidden-terminal problem at the same time**.

<div class="zh" markdown="1">

> 💡 **隐藏终端是"功率过大"的另一个后果**：功率越大，能听到的邻居越多；但"听不到却打得着"的隐藏关系也越多。**高密度场景的低功率设计同时改善了隐藏终端问题**。

</div>

### Frame Types and Overhead Structure · 帧类型与开销结构

| Class | Typical frames | Does it consume airtime when there is no data? | Design focus |
|---|---|---|---|
| **Management frames** | Beacon, Probe Request/Response, Auth, Assoc/Reassoc, Action (11k/v/r) | **Consume continuously** (Beacons are sent on a timer) | SSID count, Beacon interval, probe suppression |
| **Control frames** | ACK, Block ACK (BA), RTS/CTS, PS-Poll, Trigger (11ax) | One per data frame | Aggregation efficiency, MU scheduling |
| **Data frames** | Data, QoS Data, Null Data (power-save notification) | The payload itself | Frame size, aggregation, retries |
| **Extension frames** | DMG Beacon, Action variants | Depends on the feature | Positioning, spectrum measurement |

<div class="zh" markdown="1">

| 类别 | 典型帧 | 是否消耗 airtime（有无数据时） | 设计关注点 |
|---|---|---|---|
| **管理帧** | Beacon、Probe Request/Response、Auth、Assoc/Reassoc、Action（11k/v/r） | **持续消耗**（Beacon 定时发送） | SSID 数量、Beacon 间隔、探测抑制 |
| **控制帧** | ACK、Block ACK（BA）、RTS/CTS、PS-Poll、Trigger（11ax） | 每数据帧必带 | 聚合效率、MU 调度 |
| **数据帧** | Data、QoS Data、Null Data（省电通知） | 业务本体 | 帧大小、聚合、重传 |
| **扩展帧** | DMG Beacon、各种 Action 变体 | 视功能 | 定位、频谱测量 |

</div>

**Frame aggregation is the real source of efficiency gains after 11n** (more important than MIMO):

<div class="zh" markdown="1">

**帧聚合是 11n 之后效率提升的真正来源**（比 MIMO 更关键）：

</div>

| Mechanism | Function | Effect |
|---|---|---|
| **A-MPDU** | Packs many MPDUs into one PHY transmission sharing one preamble and one Block ACK | Preamble and backoff overhead are amortised over dozens of frames; efficiency rises from ~50% to 80%+ |
| **A-MSDU** | Merges several Ethernet frames into one MPDU at the MAC layer | Further reduces MAC header overhead, but one error retransmits the whole thing — worse under weak signal |
| **Block ACK** | One ACK acknowledges a whole batch | Eliminates the per-frame SIFS+ACK (about 48 µs per frame) |

<div class="zh" markdown="1">

| 机制 | 作用 | 效果 |
|---|---|---|
| **A-MPDU** | 把多个 MPDU 塞进一次 PHY 传输，共用一个前导码与一个 Block ACK | 前导码与退避开销被"摊薄"到几十帧上，效率从 ~50% 提到 80%+ |
| **A-MSDU** | 在 MAC 层把多个以太网帧合成一个 MPDU | 进一步减少 MAC 头开销，但一帧出错全帧重传，弱信号下反而更糟 |
| **Block ACK** | 一次 ACK 确认整批帧 | 省掉每帧的 SIFS+ACK（约 48 µs/帧） |

</div>

> ⚠️ **The boundary conditions of aggregation**: A-MPDU needs **enough queued frames** to fill. Therefore:
> - **Small-frame traffic (voice/IoT) barely aggregates** → efficiency is inherently low, which is exactly why voice must be sized as "calls per AP";
> - **A single client downloading a large file** aggregates well, but is then usually limited by the client (2SS, 80 MHz);
> - **MU-MIMO/OFDMA only make sense when several clients all have frames to send**; a single-client scenario gains nothing.

<div class="zh" markdown="1">

> ⚠️ **聚合的边界条件**：A-MPDU 需要**足够多的待发帧**才能填满。因此：
> - **小包业务（语音/IoT）几乎无法聚合** → 效率天生低，这才是语音只能按"每 AP 多少通"算的原因；
> - **单客户端大文件下载**能聚合得很好，但此时往往受限于客户端能力（2SS、80 MHz）；
> - **MU-MIMO/OFDMA 才有意义的前提是"多客户端都有帧要发"**，单客户端场景无增益。

</div>

### Rate Adaptation: Why One Weak Client Can Drag Down the Whole AP · 速率自适应：为什么一个弱客户端能拖垮整个 AP

The AP maintains a **rate-selection algorithm** per client (Minstrel, AARF, vendor proprietary). It picks the MCS dynamically based on ACK success and retry counts. **It optimises only whether that one client gets through; it does not care about the airtime of the whole radio.**

<div class="zh" markdown="1">

AP 为每个客户端维护一个**速率选择算法**（Minstrel、AARF、厂商私有）。它根据 ACK 成功率、重传次数动态选 MCS。**它只优化"这个客户端自己能不能通"，不关心"整块射频的 airtime"**。

</div>

That produces the "**airtime black hole**" effect:

<div class="zh" markdown="1">

由此产生"**airtime 黑洞**"效应：

</div>

```
A client at −85 dBm (MCS 0, 20 MHz, 1SS ≈ 6.5 Mbps PHY)
to send one 1500 B frame needs: 12000 bit ÷ 6.5 Mbps ≈ 1846 µs of data + 160 µs overhead ≈ 2 ms
while a client at −55 dBm (MCS 9, 86 Mbps; MCS 11 with 2SS is higher) needs only ≈ 300 µs for the same frame
→ the weak client consumes 6–7× the airtime per frame of a healthy client
→ if it is downloading torrents or watching video, it takes the place of seven normal users
```

<div class="zh" markdown="1">

```
一个 -85 dBm 的客户端（MCS 0, 20 MHz, 1SS ≈ 6.5 Mbps PHY）
发 1 个 1500 B 帧需要：12000 bit ÷ 6.5 Mbps ≈ 1846 µs 数据 + 160 µs 开销 ≈ 2 ms
而一个 -55 dBm 客户端（MCS 9, 86 Mbps，2SS MCS 11 更高）同样一帧只需 ≈ 300 µs
→ 弱客户端每帧占用 airtime 是正常客户端的 6–7 倍
→ 若它在下 BT、看视频，等于替 7 个正常用户占位
```

</div>

**Four lines of defence (all of them are required)**:

<div class="zh" markdown="1">

**四道防线（缺一不可）**：

</div>

| Defence | Configuration | Function |
|---|---|---|
| **MIN RSSI** | Controller RF Profile set to −67 dBm | Force disassociation below the threshold, pushing the client toward a closer AP |
| **Disable low rates** | Turn off 1/2/5.5/11 Mbps (2.4 GHz) and 6/9 Mbps (5 GHz) | Raise the rate floor; a weak client "cannot get out" and therefore cannot occupy airtime |
| **Airtime Fairness** | Enabled on the controller | Allocate opportunities by **time** rather than by frame count, suppressing slow clients |
| **Band Steering / 11v** | Steer to 5/6 GHz | Reduce 2.4 GHz congestion and slow-client load |

<div class="zh" markdown="1">

| 防线 | 配置 | 作用 |
|---|---|---|
| **MIN RSSI** | 控制器 RF Profile 设 -67 dBm | 低于阈值强制断开，逼客户端去找更近的 AP |
| **禁用低速率** | 关闭 1/2/5.5/11 Mbps（2.4 GHz）、关闭 6/9 Mbps（5 GHz） | 抬高速率下限，弱信号客户端"发不出去"就不会占位 |
| **Airtime Fairness** | 控制器开启 | 按**时间**而不是按**帧数**分配机会，抑制低速客户端 |
| **Band Steering / 11v** | 引导到 5/6 GHz | 减少 2.4 GHz 拥挤与低速终端 |

</div>

> ⚠️ **The side effect of disabling low rates**: edge clients will complain that they "cannot connect". That is not a bug, it is a design trade-off — **trading coverage for a few edge users against capacity for everyone**. So coverage design (−67 dBm cell edge) must be secured first and low rates disabled afterwards; reversing that order is how outages happen.

<div class="zh" markdown="1">

> ⚠️ **关低速率的副作用**：边缘客户端会因为"连不上"而投诉。这不是 bug，而是设计取舍 —— **用少数边缘用户的覆盖，换全场用户的容量**。所以必须先保证覆盖设计（-67 dBm 边界），再关低速率；顺序反了就是事故。

</div>

### Over-the-Air Efficiency: From 100% Theory to Every Loss Layer on the Speedometer · 空口效率：从 100% 理论到时速表的每一层损耗

| Loss layer | Typical value | Explanation |
|---|---|---|
| PHY theoretical rate | 100% | Vendor headline number (8SS/160 MHz/zero overhead) |
| Real spatial streams and bandwidth (endpoint capability) | 30%–60% | Most phones are 2SS, 80 MHz |
| Preamble + interframe gap + backoff + ACK | 50%–75% left | See the worked example above |
| Management frames (Beacon/probes) | Another 3%–15% | Depends on SSID count and client density |
| Retries (interference, weak signal) | Another 5%–30% | Significant in high density |
| TCP/IP and upper-layer overhead | Another 5%–10% | Includes TCP ACKs and TLS handshakes |
| **End-user usable (relative to PHY)** | **Roughly 20%–35%** | Why a "1.2 Gbps AP" measures 300–400 Mbps |

<div class="zh" markdown="1">

| 损耗层 | 典型值 | 说明 |
|---|---|---|
| PHY 理论速率 | 100% | 厂商标称值（8SS/160MHz/零开销） |
| 实际空间流与带宽（终端能力） | 30%–60% | 手机多为 2SS、80 MHz |
| 前导码 + 帧间隔 + 退避 + ACK | 剩 50%–75% | 见上文算例 |
| 管理帧（Beacon/探测） | 再减 3%–15% | SSID 数量与客户端密度相关 |
| 重传（干扰、弱信号） | 再减 5%–30% | 高密度下显著 |
| TCP/IP 与上层开销 | 再减 5%–10% | 含 TCP ACK、TLS 握手 |
| **最终用户可用（相对 PHY）** | **约 20%–35%** | 这就是为什么"1.2 Gbps 的 AP"实测只有 300–400 Mbps |

</div>

**This table is the most powerful communication tool you have**: when a customer waves "the AP says 5.4 Gbps, so why do we only see 400 Mbps", walk down the layers one by one and every line has evidence behind it.

<div class="zh" markdown="1">

**这张表是最有力的沟通工具**：当客户拿着"AP 标称 5.4 Gbps，为什么我们只有 400 Mbps"来质问时，逐层对下来，每一层都有依据。

</div>

### 2.4 GHz Band · 4 GHz 频段

- Channels 1–13 (14 in some regions), each 20 MHz, and **only three are non-overlapping: 1, 6 and 11**
- Long wavelength, strong diffraction, low penetration loss → **large coverage radius** (about 10–15 dB through a load-bearing wall, versus 20–30 dB at 5 GHz under the same conditions)
- Dense interference sources: Bluetooth, microwave ovens, wireless mice/cameras, Zigbee, neighbouring APs
- Only three non-overlapping channels → **co-channel reuse is almost impossible to plan**, CCI is unavoidable

<div class="zh" markdown="1">

- 信道 1–13（部分地区含 14），每个 20 MHz，**互不重叠只有 3 个：1、6、11**
- 波长长、绕射强、穿透损耗小 → **覆盖半径大**（穿一堵承重墙约衰减 10–15 dB，5 GHz 同条件 20–30 dB）
- 干扰源密集：蓝牙、微波炉、无线鼠标/摄像头、Zigbee、邻居 AP
- 只有 3 个不重叠信道 → **同频复用几乎不可能规划**，CCI 不可避免

</div>

**The three correct uses of 2.4 GHz**:

<div class="zh" markdown="1">

**2.4 GHz 的正确用法（三条）**：

</div>

1. **Carry only devices that must use it**: legacy IoT (wireless printers, tags, medical telemetry) and guest fallback
2. **Channel width fixed at 20 MHz** (never 40 MHz, which collapses you to a single usable channel)
3. **Turn off mandatory support for low rates** (disable 1/2/5.5/11 Mbps) so weak clients leave voluntarily instead of wrecking airtime

<div class="zh" markdown="1">

1. **只承载"必须用它"的设备**：老 IoT（无线打印机、标签、医疗遥测）、访客兜底
2. **信道宽度固定 20 MHz**（绝不开 40 MHz，那等于只用 1 个信道）
3. **关闭低速率的强制支持**（disable 1/2/5.5/11 Mbps），让弱信号客户端主动离开而不是拖垮 airtime

</div>

> ⚠️ **Never move important services to 2.4 GHz "for better coverage"**. The coverage advantage of 2.4 GHz is an illusion in metal-heavy, partition-heavy environments such as meeting rooms and warehouses: the signal arrives, but airtime does not.

<div class="zh" markdown="1">

> ⚠️ **不要为了"更好覆盖"把重要业务放 2.4 GHz**。2.4 GHz 的覆盖优势在会议室/仓库这类多金属、多隔断环境里是假象：信号到了，airtime 却挤不进去。

</div>

### 5 GHz Band · 5 GHz 频段

| UNII sub-band | Channels | Characteristics | Design requirement |
|-----------|------|------|---------|
| **UNII-1** | 36–48 | Indoor, no DFS | First choice, can run 80 MHz |
| **UNII-2** | 52–64 | **Requires DFS + TPC** | Radar channels; a radar event can force you off |
| **UNII-2e** | 100–144 | **Requires DFS** | The bulk of the capacity pool, but false radar detection silences the whole channel |
| **UNII-3 / ISM** | 149–165 | Higher power ceiling | Restricted in some countries; often used for outdoor bridging |

<div class="zh" markdown="1">

| UNII 子带 | 信道 | 特性 | 设计要求 |
|-----------|------|------|---------|
| **UNII-1** | 36–48 | 室内、无 DFS | 首选，可做 80 MHz |
| **UNII-2** | 52–64 | **需 DFS + TPC** | 雷达信道，可能因雷达事件被强制切走 |
| **UNII-2e** | 100–144 | **需 DFS** | 容量池主体，但雷达误检会引发整信道静默 |
| **UNII-3 / ISM** | 149–165 | 功率上限较高 | 部分国家受限，常做室外桥接 |

</div>

- 20 MHz non-overlapping channels: **about 25** (depending on national regulation)
- 80 MHz channels: **about 6**; 160 MHz: **about 2**
- Far less interference than 2.4 GHz, but **higher wall attenuation** (assume 3–5 dB per partition, more for concrete)

<div class="zh" markdown="1">

- 20 MHz 不重叠信道：**约 25 个**（视国家法规）
- 80 MHz 信道：**约 6 个**；160 MHz：**约 2 个**
- 干扰远小于 2.4 GHz，但**墙体衰减大**（设计时按每个隔断 3–5 dB 估算，混凝土墙更高）

</div>

**DFS is the biggest hidden risk in 5 GHz**:

<div class="zh" markdown="1">

**DFS 是 5 GHz 最大的隐性风险**：

</div>

> 🔥 **Typical symptom**: a meeting room loses Wi-Fi for a dozen seconds at random times each day, and the AP log shows `Channel changed due to radar detection`. Cause: the DFS channel detected a radar pulse (weather radar, airport radar, or a false detection from a neighbouring AP), and regulation requires **vacating the channel within 30 minutes** — the AP must move channels and every client is forced to re-associate.

<div class="zh" markdown="1">

> 🔥 **典型现象**：某个会议室每天不定时"Wi-Fi 掉十几秒"，日志里 AP 显示 `Channel changed due to radar detection`。原因：DFS 信道检测到雷达脉冲（可能来自气象雷达、机场雷达，也可能是相邻 AP 的误检），法规要求 **30 分钟内静默该信道**，AP 必须换信道 —— 所有客户端被迫重新关联。

</div>

**Design countermeasures**: ① in high-density areas prefer UNII-1 and UNII-3 (non-DFS); ② use DFS channels as capacity top-up, and enable **channel reuse / selective channel assignment** on the controller to avoid chained channel hops caused by false detection; ③ never deploy **critical real-time services** on a single DFS channel only.

<div class="zh" markdown="1">

**设计对策**：①高密度区域优先用 UNII-1 与 UNII-3（非 DFS）；②DFS 信道用于容量补充，并在控制器上开启 **channel reuse / 选择性信道分配**，避免雷达误检引发的连续跳变；③不要把**关键实时业务**只部署在单一 DFS 信道上。

</div>

### 6 GHz Band (Wi-Fi 6E / 7) · 6 GHz 频段

| Resource | Quantity |
|------|------|
| 20 MHz channels | 59 (5925–7125 MHz, depending on national availability) |
| 40 MHz channels | 29 |
| 80 MHz channels | 14 |
| 160 MHz channels | 7 |
| 320 MHz channels (Wi-Fi 7) | 3 (in some regions) |

<div class="zh" markdown="1">

| 资源 | 数量 |
|------|------|
| 20 MHz 信道 | 59 个（5925–7125 MHz，视国家开放范围） |
| 40 MHz 信道 | 29 个 |
| 80 MHz 信道 | 14 个 |
| 160 MHz 信道 | 7 个 |
| 320 MHz 信道（Wi-Fi 7） | 3 个（部分地区） |

</div>

**6 GHz is the only "clean" spectrum in a decade**: no legacy devices, no Bluetooth, no microwave ovens, so in theory you can deploy "all 80 MHz with zero CCI". But it brings four **new design constraints**:

<div class="zh" markdown="1">

**6 GHz 是近十年唯一"干净"的频谱**：没有老设备、没有蓝牙、没有微波炉，理论上可以做"全 80 MHz + 零 CCI"的部署。但它带来四个**设计层面的新约束**：

</div>

| Constraint | Explanation | Design impact |
|------|------|---------|
| **Visible only to Wi-Fi 6E/7 endpoints** | Older endpoints cannot see a 6 GHz SSID at all | 5 GHz coverage must be retained; 6 GHz can only be **incremental capacity** |
| **Mandatory WPA3 + PMF** | 6 GHz does not allow WPA2 or open (other than OWE) | Old endpoints cannot join; PSK must become WPA3-SAE |
| **Power class tiers** | LPI (indoor low power), VLP (very low power), Standard Power (requires **AFC** lookup) | Outdoor or standard-power deployments must pass AFC, extending the project timeline |
| **No SSIDs of its own (no Beacons on the old band)** | 6 GHz SSIDs are advertised through the **RNR element** in 5 GHz Beacons | Client scanning logic changes; some older clients "not seeing 6 GHz" is expected behaviour |

<div class="zh" markdown="1">

| 约束 | 说明 | 设计影响 |
|------|------|---------|
| **仅 Wi-Fi 6E/7 终端可见** | 老终端完全看不到 6 GHz 的 SSID | 必须保留 5 GHz 覆盖，6 GHz 只能做"增量容量" |
| **强制 WPA3 + PMF** | 6 GHz 不允许 WPA2、不允许开放（除 OWE） | 老终端无法接入；PSK 也要改成 WPA3-SAE |
| **功率等级分级** | LPI（室内低功率）、VLP（超低功率）、Standard Power（需 **AFC** 查询） | 室外/标准功率部署必须通过 AFC 服务，项目周期增加 |
| **不广播 SSID（无 Beacon 于旧频段）** | 6 GHz 的 SSID 通过 **RNR 元素**在 5 GHz Beacon 中指示 | 客户端扫描逻辑变化，部分老终端"看不到 6 GHz"是正常的 |

</div>

**6 GHz planning recommendations (ready to paste into a proposal)**:

<div class="zh" markdown="1">

**6 GHz 的规划建议（可以直接写进方案）**：

</div>

- **New builds**: keep 5 GHz at 20/40 MHz for coverage and compatibility, and use 6 GHz at 80 MHz as the capacity layer — a "coverage layer + capacity layer" split
- **Brownfield upgrades**: first confirm the endpoint mix (6E endpoints are usually < 30%), then decide whether dedicated 6 GHz APs are worth it
- **The knock-on effect of mandatory WPA3**: RADIUS and client configuration must be upgraded in step, and **WPA3 transition mode (WPA2/WPA3 mixed)** must be enabled to avoid dropping legacy endpoints
- **Do not expect 6 GHz to solve the 2.4 GHz IoT problem**: IoT devices are almost all 2.4 GHz-only

<div class="zh" markdown="1">

- **新项目**：5 GHz 用 20/40 MHz 保覆盖与兼容，6 GHz 用 80 MHz 做容量层，形成"覆盖层 + 容量层"双频分工
- **存量改造**：先确认终端比例（6E 终端通常 < 30%），再决定是否值得为 6 GHz 单独加 AP
- **WPA3 强制**的连带影响：必须同步升级 RADIUS 与客户端配置，且**开启 WPA3 过渡模式（WPA2/WPA3 混合）**以避免老终端掉线
- **不要指望 6 GHz 解决 2.4 GHz 的 IoT 问题**：IoT 设备几乎全是 2.4 GHz 单频

</div>

### RF Engineering Fundamentals: Turning "Is the Signal Good" into a Number · RF 工程基础：把"信号好不好"变成可计算的数

Wireless design often degenerates into folklore because most people skip this layer. **Coverage is not a feeling, it is a link-budget equation.**

<div class="zh" markdown="1">

无线设计之所以经常变成玄学，是因为多数人跳过了这一层。**覆盖不是"感觉"，是一条链路预算等式**。

</div>

#### Four Power Concepts You Must Know by Heart · 四个必背的功率概念

| Concept | Definition | Typical value | Design meaning |
|---|---|---|---|
| **Tx Power** | Radio port output | AP 5–20 dBm; phone 14–15 dBm | Determines "how far you can shout" |
| **Antenna Gain** | Focusing ability in a given direction | Omni 2–5 dBi; directional 8–14 dBi | It does not amplify power, it concentrates energy in one direction |
| **EIRP** | Tx Power + antenna gain − feeder loss | Capped by regulation (often 20 dBm at 2.4 GHz; band-dependent at 5 GHz) | **EIRP is what regulation and real coverage depend on** |
| **Receiver sensitivity** | Lowest signal level that can still be demodulated | About −92 dBm at 6 Mbps; about −60 dBm at MCS 11/80 MHz | **Higher rates need stronger signal** |

<div class="zh" markdown="1">

| 概念 | 定义 | 典型值 | 设计意义 |
|---|---|---|---|
| **发射功率（Tx Power）** | 射频口输出 | AP 5–20 dBm；手机 14–15 dBm | 决定"能喊多远" |
| **天线增益（Antenna Gain）** | 天线在某方向的聚焦能力 | 全向 2–5 dBi；定向 8–14 dBi | 不是"放大功率"，是把能量集中到某个方向 |
| **EIRP** | Tx Power + 天线增益 − 馈线损耗 | 受法规上限约束（2.4 GHz 常 20 dBm，5 GHz 因频段而异） | **EIRP 才是法规与实际覆盖的决定量** |
| **接收灵敏度** | 能解调的最低信号电平 | 6 Mbps 约 -92 dBm；MCS 11/80 MHz 约 -60 dBm | **速率越高，要求信号越强** |

</div>

> 💡 **The most commonly overlooked point**: receiver sensitivity varies with rate. So "coverage down to −85 dBm" means "it associates but can only run the lowest rate", not "it works". That is the physical basis of the −67 dBm cell-edge design — it corresponds to the signal range where most MCS levels are usable.

<div class="zh" markdown="1">

> 💡 **最容易被忽略的一条**：接收灵敏度随速率变化。所以"覆盖到 -85 dBm"意味着"能连上但只能跑最低速率"，不是"能用"。这就是 -67 dBm 边界设计的物理依据 —— 它对应"大部分 MCS 可用"的信号区间。

</div>

#### Link Budget Formula · 链路预算公式

```
Received power (dBm) = AP EIRP (dBm) − path loss (dB) + client antenna gain (dBi)
Path loss (dB) ≈ free-space loss + wall/body/furniture attenuation

Free space: FSPL (dB) = 32.44 + 20·log10(f_MHz) + 20·log10(d_km)
  5 GHz / 10 m ≈ 66 dB
  5 GHz / 30 m ≈ 76 dB
  2.4 GHz at the same distance is about 6.7 dB lower
```

<div class="zh" markdown="1">

```
接收功率(dBm) = AP EIRP(dBm) − 路径损耗(dB) + 客户端天线增益(dBi)
路径损耗(dB) ≈ 自由空间损耗 + 墙体/人体/家具衰减

自由空间：FSPL(dB) = 32.44 + 20·log10(f_MHz) + 20·log10(d_km)
  5 GHz / 10 m ≈ 66 dB
  5 GHz / 30 m ≈ 76 dB
  2.4 GHz 同距离少约 6.7 dB
```

</div>

**Common attenuation references (5 GHz, for quick estimation)**:

<div class="zh" markdown="1">

**常用衰减参考（5 GHz，用于快速估算）**：

</div>

| Obstacle | Attenuation | Note |
|---|---|---|
| Drywall / plasterboard partition | 3–5 dB | Typical office partition |
| Brick wall | 6–10 dB | |
| Concrete load-bearing wall | 12–20 dB | Assume 15–25 dB per floor slab |
| Metal racking / dense metal | 10–20 dB (sometimes a Faraday cage) | Warehouses must be measured on site |
| Human body | 3–5 dB per person (significant in crowds) | One reason venues "get worse when people arrive" |
| Low-E glass | **20–35 dB** | The invisible killer in modern office buildings |
| Lift shaft / plant room | 20–30 dB | Essentially impenetrable |

<div class="zh" markdown="1">

| 障碍 | 衰减 | 备注 |
|---|---|---|
| 干墙 / 石膏板隔断 | 3–5 dB | 办公隔断常见 |
| 砖墙 | 6–10 dB | |
| 混凝土承重墙 | 12–20 dB | 每层楼板按 15–25 dB |
| 金属货架 / 密集金属 | 10–20 dB（甚至"法拉第笼"） | 仓库必须实测 |
| 人体 | 3–5 dB/人（密集人群显著） | 会场"人一多就变差"的原因之一 |
| 低辐射（Low-E）玻璃 | **20–35 dB** | 现代写字楼的隐形杀手 |
| 电梯井 / 机房 | 20–30 dB | 基本不可穿透 |

</div>

> 🔥 **The single nastiest item in real projects**: **Low-E glass**. Newly renovated meeting rooms and curtain-wall offices have a metallic coating on the inner glass surface for thermal insulation, which can attenuate 5 GHz by 30 dB — the equivalent of a load-bearing wall. The symptom is "great signal in the corridor, −78 dBm the moment you step into the meeting room". **This can only be found by an on-site survey; it is completely invisible on drawings.**

<div class="zh" markdown="1">

> 🔥 **真实项目里最坑的一项**：**Low-E 玻璃**。新装修的会议室、玻璃幕墙办公室，玻璃内侧镀了金属膜用于隔热，对 5 GHz 的衰减可达 30 dB —— 相当于一堵承重墙。表现是"走廊信号很好，一进会议室就掉到 -78 dBm"。**这类问题只能靠现场勘测发现，图纸上完全看不出来。**

</div>

#### Deriving the Coverage Radius (an algorithm you can use directly in a design document) · 覆盖半径反推（设计文档里可以直接用的算法）

**Example: 5 GHz, AP EIRP 17 dBm, target cell edge −67 dBm, clients in an open office area**

<div class="zh" markdown="1">

**例：5 GHz，AP EIRP 17 dBm，目标边界 -67 dBm，客户在开放办公区**

</div>

```
Allowed path loss = 17 − (-67) = 84 dB
Wall budget: expect to cross 1 drywall (4 dB) → 80 dB left for free-space propagation
Look up FSPL: 80 dB at 5.5 GHz corresponds to ≈ 25 m
→ single-AP coverage radius ≈ 25 m (line of sight); use 15–18 m with many partitions
→ coverage area ≈ π·r² ≈ 700–1900 m² (ideal LOS; in practice budget 150–250 m² per AP)
```

<div class="zh" markdown="1">

```
允许路径损耗 = 17 − (-67) = 84 dB
墙体预算：预计穿过 1 堵干墙（4 dB）→ 可用于空间传播 80 dB
查 FSPL：80 dB @ 5.5 GHz 对应距离 ≈ 25 m
→ 单 AP 覆盖半径约 25 m（视距），隔断多时按 15–18 m 取
→ 覆盖面积 ≈ π·r² ≈ 700–1900 m²（视距理想值，实际按 150–250 m²/AP 折算）
```

</div>

**Why the calculated area is so far from reality**: because **coverage radius ≠ service radius**. Capacity, human bodies, furniture, non-line-of-sight and uplink limitations all shrink the usable area. **So in engineering practice you always size the AP count from capacity first, then verify coverage with RF** (the order of the six-step method).

<div class="zh" markdown="1">

**为什么算出来的面积和实际差这么多**：因为**覆盖半径 ≠ 服务半径**。容量、人体、家具、非视距、上行受限都会缩小实际可用范围。**所以工程上永远先用容量算 AP 数，再用 RF 校核覆盖**（六步法的顺序）。

</div>

#### Antenna Selection · 天线选型

| Antenna type | Gain | Horizontal beam | Where it fits | Watch out |
|---|---|---|---|---|
| **Omni** | 2–5 dBi | 360° | Open office, ceiling mount | Mounting inside a ceiling adds 3–10 dB of loss |
| **Directional (patch/panel)** | 6–14 dBi | 60°–90° | Corridors, warehouse aisles, venue zoning | Aiming must be explicit; mounted wrong means no coverage |
| **Downtilt directional** | 8–12 dBi | 60° | High-ceiling venues, stadium seating | The core tool of venue design |
| **Yagi / panel (point-to-point)** | 12–24 dBi | Under 30° | Building-to-building bridging | Requires LOS and precise alignment |
| **Leaky feeder** | — | Uniform along the cable | Tunnels, mines, long corridors | Specialised scenario, needs professional design |

<div class="zh" markdown="1">

| 天线类型 | 增益 | 水平波束 | 适用 | 注意 |
|---|---|---|---|---|
| **全向（Omni）** | 2–5 dBi | 360° | 开放办公、吸顶 | 天花板内安装会额外损耗 3–10 dB |
| **定向（Patch/Panel）** | 6–14 dBi | 60°–90° | 走廊、仓库过道、会场分区 | 需要明确朝向，装错等于没覆盖 |
| **下倾定向（Downtilt）** | 8–12 dBi | 60° | 高挑高场馆、体育馆座席 | 场馆设计的核心手段 |
| **八木 / 平板（点对点）** | 12–24 dBi | 30° 以下 | 楼间桥接 | 必须视线（LOS）与精确对准 |
| **漏缆（Leaky Feeder）** | — | 沿线均匀 | 隧道、矿井、长走廊 | 特殊场景，需专业设计 |

</div>

**Polarization and MIMO**: the polarization of the AP and client antennas must line up. Ceiling APs usually contain ±45° dual-polarized elements, and a phone held sideways can see a 3–6 dB difference — this is the root cause of "the signal drops when I turn my phone sideways", a device-form-factor issue that no configuration can fix.

<div class="zh" markdown="1">

**极化与 MIMO**：AP 与客户端天线的极化方向要"对得上"。吸顶 AP 内部通常是斜 45° 双极化，客户端横向持握手机时会有 3–6 dB 差异 —— 这也是"手机横过来信号就变差"的根本原因，属于终端形态问题，无法通过配置解决。

</div>

#### Endpoint Capability Matrix: The Link Bottleneck Is Always the Endpoint · 终端能力矩阵：链路的瓶颈永远在终端

| Endpoint type | Typical capability | Peak PHY | Real TCP | Design implication |
|---|---|---|---|---|
| Recent laptop (11ax/6E) | 2SS, 80/160 MHz | 1.2–2.4 Gbps | 600–1000 Mbps | Only these can use wide channels |
| Mainstream phone (11ac/ax) | 2SS, 80 MHz | 867 Mbps | 400–500 Mbps | Phones are the vast majority of users |
| Old phone / tablet (11n) | 1–2SS, 40 MHz | 150–300 Mbps | 80–150 Mbps | **Does not participate in OFDMA/MU-MIMO** |
| Wireless handset | 1SS, 20 MHz, 11a/n | 65–72 Mbps | 30–40 Mbps | Voice needs only 100 kbps, but **fixed airtime per call** |
| Scanner / PDA | 1SS, 20 MHz, 2.4 GHz | 72 Mbps | 20–30 Mbps | Roams constantly, extremely small frames |
| Medical telemetry / IoT | 1SS, 2.4 GHz, low duty cycle | 65 Mbps or less | Very low | Huge numbers, high management-frame overhead |
| Wireless camera | 1–2SS, continuous uplink | 150–300 Mbps | 60–120 Mbps | **Holds airtime continuously — the most damaging load** |

<div class="zh" markdown="1">

| 终端类型 | 典型能力 | 峰值 PHY | 实际 TCP | 设计含义 |
|---|---|---|---|---|
| 新款笔记本（11ax/6E） | 2SS，80/160 MHz | 1.2–2.4 Gbps | 600–1000 Mbps | 只有它们能用上宽信道 |
| 主流手机（11ac/ax） | 2SS，80 MHz | 867 Mbps | 400–500 Mbps | 手机是绝大多数用户 |
| 旧手机 / 平板（11n） | 1–2SS，40 MHz | 150–300 Mbps | 80–150 Mbps | **不参与 OFDMA/MU-MIMO** |
| 无线话机 | 1SS，20 MHz，11a/n | 65–72 Mbps | 30–40 Mbps | 语音只要 100 kbps，但**每通固定 airtime** |
| 扫码枪 / PDA | 1SS，20 MHz，2.4 GHz | 72 Mbps | 20–30 Mbps | 漫游频繁、包极小 |
| 医疗遥测 / IoT | 1SS，2.4 GHz，低占空比 | 65 Mbps 或更低 | 极低 | 数量巨大、管理帧开销高 |
| 摄像头（无线） | 1–2SS，持续上行 | 150–300 Mbps | 60–120 Mbps | **持续占 airtime，是最伤的负载** |

</div>

> ⚠️ **The direct design inference**: if **more than 30% of the client population is legacy**, raising channel width from 20 MHz to 80 MHz only helps the other 70% (the ones with good signal), while **CCI risk applies to everyone** — which is exactly why high-density designs stay at 20 MHz.

<div class="zh" markdown="1">

> ⚠️ **设计上的直接推论**：如果客户群体中有 **30% 以上的旧终端**，那么把信道宽度从 20 MHz 提到 80 MHz 只对剩下 70%（且信号好的）用户有效，而 **CCI 风险对所有用户生效** —— 这就是高密度场景坚持 20 MHz 的原因。

</div>

### Channel Planning: From "Assigning Channels" to "Assigning Reuse Distance" · 信道规划：从"分配信道"到"分配复用距离"

What really determines wireless capacity is not "how many channels exist" but **the physical separation between co-channel cells (the reuse distance)**.

<div class="zh" markdown="1">

真正决定无线容量的不是"有几个信道"，而是**同频信道的物理间隔（复用距离）**。

</div>

| Deployment shape | Recommended channel width | Reuse pattern | Target co-channel separation |
|---------|------------|--------|------------|
| Normal office (AP spacing 15–20 m) | 5 GHz 40 MHz | 1-6-11 style interleave (non-overlapping sets in 5 GHz) | ≥ 2 AP layers |
| High density (AP spacing 8–12 m) | 5 GHz **20 MHz** | Strict interleave, adjacent same-channel forbidden | ≥ 3 AP layers |
| Warehouse/lobby (high ceiling, few partitions) | 5 GHz 40 MHz + directional antennas | Zone by area | Depends on coverage radius |
| 6 GHz capacity layer | 80 MHz | Few APs, almost no reuse pressure | ≥ 1 layer |

<div class="zh" markdown="1">

| 部署形态 | 推荐信道宽度 | 复用图 | 目标同频间隔 |
|---------|------------|--------|------------|
| 普通办公（AP 间距 15–20 m） | 5 GHz 40 MHz | 1-6-11 式交错（5 GHz 用非重叠组） | ≥ 2 层 AP |
| 高密度（AP 间距 8–12 m） | 5 GHz **20 MHz** | 严格交错，禁止相邻同信道 | ≥ 3 层 AP |
| 仓库/大堂（高挑高、少隔断） | 5 GHz 40 MHz + 定向天线 | 按区域分区 | 视覆盖半径 |
| 6 GHz 容量层 | 80 MHz | 少量 AP，几乎无复用压力 | ≥ 1 层 |

</div>

**Power and channel must be tuned together**: channel width determines spectrum occupancy, transmit power determines coverage radius. If power is not reduced, then even a correct channel plan leaves **adjacent APs hearing each other** (co-channel overlap); BSS Coloring mitigates this but cannot eliminate it.

<div class="zh" markdown="1">

**功率与信道必须一起调**：信道宽度决定"频谱占用"，发射功率决定"覆盖半径"。如果功率不降，即使信道规划正确，**相邻 AP 仍会互相听到**（co-channel overlap），BSS Coloring 只能缓解而不能消除。

</div>

> 💡 **The golden combination**: high-density areas = **low power (5–8 dBm) + 20 MHz + MIN RSSI −67 dBm**. All three must be set together; tuning only one of them is the same as tuning none.

<div class="zh" markdown="1">

> 💡 **黄金组合**：高密度区域 = **低功率（5–8 dBm）+ 20 MHz + MIN RSSI -67 dBm**。这三项必须同时设置，只调其中一项等于没调。

</div>

---

## Enterprise Wireless Architecture · 企业无线架构

### Why Wireless Needs a Controller · 为什么无线需要一个"控制器"

In the wired world, switch control planes are distributed (each box runs its own STP and learns its own MACs). Why can wireless not do the same? Three structural reasons:

<div class="zh" markdown="1">

有线网络里，交换机的控制面是分布式的（每台自己跑 STP、自己学 MAC）。无线为什么不能照做？三个结构性原因：

</div>

| Reason | Explanation |
|------|------|
| **RF is a global resource** | Channels, power and client load must be coordinated with a **global view**. Two neighbouring APs each "cleverly" choosing maximum power simply jam each other |
| **Authentication state must be shared** | A roaming client must reuse the PMK (key cache); otherwise every AP change means a fresh 802.1X run (hundreds of milliseconds to seconds) |
| **Policy must be pushed consistently** | SSIDs, ACLs, QoS and VLAN mappings configured box by box cannot be kept consistent across thousands of APs |

<div class="zh" markdown="1">

| 原因 | 说明 |
|------|------|
| **RF 是全局资源** | 信道、功率、客户端负载必须在**全局视野**下协调。两台相邻 AP 各自"聪明地"选最强功率，结果就是互相干扰 |
| **认证状态需要共享** | 客户端漫游时必须复用 PMK（密钥缓存），否则每次换 AP 都要重新做 802.1X（几百毫秒到数秒） |
| **策略需要统一下发** | SSID、ACL、QoS、VLAN 映射若逐台配置，几千台 AP 的配置漂移无法管理 |

</div>

**So the controller owns three things: RF coordination, authentication/key-state sync, and consistent policy distribution.** Whether data also passes through the controller is optional — and that choice is exactly the dividing line between Local Mode and FlexConnect.

<div class="zh" markdown="1">

**所以控制器管三件事：RF 协调、认证/密钥状态同步、策略统一下发。** 数据是否也经过控制器，是可以选择的 —— 这就是 Local Mode 与 FlexConnect 的分野。

</div>

### Control Plane and Data Plane: Four Combinations · 控制面与数据面：四种组合

| Combination | Control plane | Data plane | Example |
|------|--------|--------|------|
| **Central control + central forwarding** | WLC | CAPWAP tunnel back to the WLC | Local Mode (classic campus) |
| **Central control + local forwarding** | WLC | AP bridges locally to the access switch | FlexConnect / local forwarding |
| **Central control + distributed forwarding (edge)** | WLC | Local forwarding + local policy | FlexConnect + local authentication (branch) |
| **Cloud control + local forwarding** | Cloud (Meraki and similar) | Local | Multi-branch / SMB |

<div class="zh" markdown="1">

| 组合 | 控制面 | 数据面 | 代表 |
|------|--------|--------|------|
| **集中控制 + 集中转发** | WLC | CAPWAP 隧道回 WLC | Local Mode（传统园区） |
| **集中控制 + 本地转发** | WLC | AP 本地桥接到接入交换机 | FlexConnect / 本地转发 |
| **集中控制 + 分布式转发（边缘）** | WLC | 本地转发 + 本地策略 | FlexConnect + 本地认证（分支） |
| **云控制 + 本地转发** | 云（Meraki 等） | 本地 | 多分支/中小企业 |

</div>

> 💡 **The key design question is not "which is more advanced" but "how much bandwidth and how many failure points sit on the data path back"**. Tunnelling user traffic from 100 branches back to a headquarters WLC builds a dual single point of failure in bandwidth and availability at headquarters.

<div class="zh" markdown="1">

> 💡 **设计判断的关键问题不是"哪种先进"，而是"数据回传的路径上有多少带宽、多少故障点"**。100 个分支把用户流量全部隧道回总部 WLC，等于给总部造了一个带宽与可用性的双单点。

</div>

### Wireless Controller Deployment Models · 无线控制器部署模型

| Model | Characteristics | Advantages | Cost | Where it fits |
|------|------|------|------|---------|
| **Centralized** | All AP CAPWAP tunnels terminate on a data-centre WLC | Unified policy, simple roaming, global RF visibility | **Backhaul bandwidth** and **WAN dependency**; the controller is a single point | Single campus, multiple buildings, multiple sites inside one LAN |
| **Distributed** | A WLC per site or per region | Data stays local, resilient to WAN failure | Many controllers; configuration consistency is hard | Large multi-site enterprises (> 100 APs per site) |
| **Cloud-managed** | Control plane in the cloud (Meraki, cloud AC) | Zero on-site operations, fast branch turn-up | Depends on internet reachability; limited deep customisation | Many branches, thin IT staffing |
| **Embedded** | Controller function inside a switch or router | Low cost, single-box delivery | Limited scale, trimmed features | Small sites, retail stores |
| **Controller-less (Mobility Express / virtual WLC)** | One AP acts as "master", or the WLC runs in a VM/cloud | Minimal deployment / elastic scaling | Weak scale and HA | Small offices, temporary scenarios |

<div class="zh" markdown="1">

| 模型 | 特点 | 优势 | 代价 | 适用场景 |
|------|------|------|------|---------|
| **集中式 (Centralized)** | 所有 AP 的 CAPWAP 隧道回数据中心 WLC | 策略统一、漫游简单、RF 全局可视 | **数据回传带宽**与**WAN 依赖**；控制器是单点 | 单园区、多楼栋、局域网内多站点 |
| **分布式 (Distributed)** | 每站点/每区域部署 WLC | 数据本地、抗 WAN 故障 | 控制器数量多，配置一致性难保证 | 大型多站点企业（每站点 > 100 AP） |
| **云管理 (Cloud)** | 控制面在云（Meraki、云 AC） | 零现场运维、多分支快速上线 | 依赖互联网可达；深度定制受限 | 分支多、IT 人力少 |
| **嵌入式 (Embedded)** | 控制器功能内嵌于交换机/路由器 | 成本低、单箱交付 | 规模有限、功能裁剪 | 小型站点、零售门店 |
| **无控制器（Mobility Express / 虚拟化 WLC）** | 一台 AP 当"主"，或 WLC 跑在 VM/云 | 部署极简 / 弹性伸缩 | 规模与高可用弱 | 小型办公、临时场景 |

</div>

**Selection decision tree (usable directly in a proposal)**:

<div class="zh" markdown="1">

**选型决策树（写方案时可以直接用）**：

</div>

```
Multi-site enterprise
│
├─ More than 100 APs per site, with dedicated inter-site links?
│  ├─ Yes ──→ per-site WLC (distributed) + unified management platform (DNA Center / cloud)
│  └─ No
│     ├─ Branch WAN < 50 Mbps or unreliable?
│     │  ├─ Yes ──→ FlexConnect local forwarding + local authentication (survives a WAN cut)
│     │  └─ No ──→ centralized WLC + Local Mode (most consistent policy)
│     └─ Fewer than 10 sites and no dedicated network team?
│        └─ Yes ──→ cloud-managed (Meraki / cloud AC)
└─ Single campus, multiple buildings ──→ centralized WLC (HA SSO pair) + dual uplinks
```

<div class="zh" markdown="1">

```
多站点企业
│
├─ 站点内 AP 数 > 100，且站点间有专线？
│  ├─ 是 ──→ 每站点独立 WLC（分布式）+ 统一管理平台（DNA Center / 云）
│  └─ 否
│     ├─ 分支 WAN 带宽 < 50 Mbps 或不可靠？
│     │  ├─ 是 ──→ FlexConnect 本地转发 + 本地认证（WAN 断网仍可上网）
│     │  └─ 否 ──→ 集中式 WLC + Local Mode（策略最统一）
│     └─ 站点 < 10 个且无专职网络团队？
│        └─ 是 ──→ 云管理（Meraki / 云 AC）
└─ 单园区多楼栋 ──→ 集中式 WLC（HA SSO 双机）+ 双上行
```

</div>

### CAPWAP: The Protocol Between AP and Controller · CAPWAP：AP 与控制器之间的协议

| Item | Detail |
|------|------|
| **Full name** | Control and Provisioning of Wireless Access Points (RFC 5415) |
| **Transport** | UDP — **control plane 5246**, **data plane 5247** (IP protocol 136 encapsulation is possible but rare) |
| **Control tunnel** | Carries configuration push, AP state, RF information, client context, key sync |
| **Data tunnel** | Carries 802.3 encapsulation of client 802.11 frames (Local Mode only) |
| **Encryption** | DTLS on the control plane; optional DTLS on the data plane |
| **Keepalive** | Echo Request/Reply (30 s by default; four missed intervals declare the link down) |

<div class="zh" markdown="1">

| 项目 | 内容 |
|------|------|
| **全称** | Control and Provisioning of Wireless Access Points（RFC 5415） |
| **传输** | UDP，**控制面 5246**、**数据面 5247**（可用 IP 协议 136 封装，但少见） |
| **控制隧道** | 承载配置下发、AP 状态、RF 信息、客户端上下文、密钥同步 |
| **数据隧道** | 承载客户端 802.11 帧的 802.3 封装（Local Mode 才有） |
| **加密** | 控制面 DTLS 加密；数据面可选 DTLS |
| **心跳** | Echo Request/Reply（默认 30 s，超时 4 次判定断链） |

</div>

> ⚠️ **Something that must go into the design document**: the CAPWAP data tunnel encapsulates complete 802.11 frames inside UDP/IP, **adding 40+ bytes per frame**. If the client MTU is 1500, the tunnel will fragment. The standard production practice is to **raise the path MTU between AP and WLC (≥ 1550)**, or enable `pmtu`/`fragment` on the WLC so the AP fragments (at a performance cost).

<div class="zh" markdown="1">

> ⚠️ **必须写进设计文档的一条**：CAPWAP 数据隧道会把 802.11 帧完整封装在 UDP/IP 里，**每帧额外增加 40+ 字节**。如果客户端 MTU 是 1500，隧道内会出现分片。生产上标准的做法是**把 AP 与 WLC 之间的路径 MTU 统一放大（≥ 1550）**，或在 WLC 上启用 `pmtu`/`fragment` 让 AP 自己分片（代价是性能下降）。

</div>

#### The Full AP Onboarding Flow (which is also your troubleshooting order) · AP 上线全流程（排障顺序就是它）

```
① AP powers up → gets an IP from DHCP (it MUST get an address!)
② Discovers the controller, in this order:
   a. DHCP Option 43 (vendor proprietary; Cisco uses a hex IP list)
   b. DNS resolution of CISCO-CAPWAP-CONTROLLER.<domain>
   c. Local subnet broadcast (same broadcast domain)
   d. The last remembered controller (the AP caches it)
③ Establishes the CAPWAP control tunnel (UDP 5246), DTLS handshake + certificate validation (optional)
④ Downloads image and control configuration → may reboot
⑤ Joins the WLC and binds configuration via AP Group / Site Tag / Policy Tag
⑥ Data tunnel comes up, SSIDs start beaconing
```

<div class="zh" markdown="1">

```
① AP 上电 → 从 DHCP 拿到 IP（必须能拿到地址！）
② 发现控制器，顺序：
   a. DHCP Option 43（厂商私有，Cisco 是十六进制 IP 列表）
   b. DNS 解析 CISCO-CAPWAP-CONTROLLER.<domain>
   c. 本地子网广播（同一广播域）
   d. 上次记住的控制器（AP 会缓存）
③ 与 WLC 建立 CAPWAP 控制隧道（UDP 5246），DTLS 握手 + 证书校验（可选）
④ 下载镜像与控制配置 → 可能重启
⑤ 加入 WLC，按 AP Group / Site Tag / Policy Tag 绑定配置
⑥ 数据隧道建立，SSID 开始广播
```

</div>

**Troubleshooting mapping table** (this one table solves 80% of "the AP will not come up"):

<div class="zh" markdown="1">

**排障映射表**（这一张表能解决 80% 的"AP 不上线"）：

</div>

| Symptom | Most likely cause | Verification command |
|------|------------|---------|
| AP gets no IP | Wrong access-port VLAN, missing DHCP relay, port-security restriction | Switch `show interface status`, AP console |
| IP obtained but no WLC found | Option 43 not configured / DNS unreachable / no route across subnets | AP `debug capwap client`, `ping` the WLC |
| WLC found but stuck at join | Clock/certificate mismatch, WLC AP limit reached, insufficient licences | WLC `show ap join stats summary`, `show license` |
| Reboot loop after join | Image download interrupted (MTU/bandwidth), mismatched config template | `show ap image`, WLC `show ap logs` |
| Online but SSID not broadcasting | AP Group/Tag not bound to the WLAN, RF Profile disabling that band | `show ap config general` |
| Client associates but gets no address | Interface/VLAN not created on the WLC, external DHCP relay not pointed there | WLC `show interface`, `debug dhcp` |

<div class="zh" markdown="1">

| 现象 | 最可能的原因 | 验证命令 |
|------|------------|---------|
| AP 拿不到 IP | 接入端口 VLAN 错、DHCP 中继缺失、端口安全限制 | 交换机 `show interface status`、AP console |
| 拿到 IP 但找不到 WLC | Option 43 未配 / DNS 不可达 / 跨网段无路由 | AP 上 `debug capwap client`、`ping` WLC |
| 找到 WLC 但卡在 join | 证书时间不同步、WLC 已达到 AP 数量上限、授权不足 | WLC `show ap join stats summary`、`show license` |
| join 后反复重启 | 镜像下载中断（MTU/带宽）、配置模板不匹配 | `show ap image`、WLC `show ap logs` |
| 上线但 SSID 不广播 | AP Group / Tag 未绑定 WLAN、RF Profile 禁用该频段 | `show ap config general` |
| 客户端能连但拿不到地址 | 接口/VLAN 未在 WLC 上创建、外置 DHCP 中继未指 | WLC `show interface`、`debug dhcp` |

</div>

### AP Operating Modes · AP 工作模式

| Mode | Function | Design use | Watch out |
|------|------|---------|------|
| **Local** | Both data and control go over CAPWAP to the WLC | Standard campus mode | Needs enough backhaul bandwidth and low latency |
| **FlexConnect** | Control to the WLC, **data switched locally** | Branches, sites with unreliable WAN | Requires local VLAN configuration + local DHCP |
| **Monitor** | Receive only, scanning all channels | wIPS, RF analysis, CleanAir | Serves no clients; it is a "sensor" |
| **Sniffer** | Captures and forwards to an analyser (Wireshark/ACI) | Hard-to-find faults | Captures only the specified channel; manual hopping required |
| **Bridge / Mesh** | Wireless backhaul between APs | Areas that cannot be cabled (warehouses, plazas) | Each backhaul hop costs half the throughput |
| **Sensor (dedicated)** | Purpose-built wIPS sensor hardware | High-security sites | Expensive, listen-only |
| **Sniffer + Monitor hybrid (SE-Connect)** | Scanning + remote spectrum analysis | Spectrum troubleshooting | One dedicated unit |

<div class="zh" markdown="1">

| 模式 | 功能 | 设计用途 | 注意 |
|------|------|---------|------|
| **Local** | 数据与控制都走 CAPWAP 到 WLC | 园区标准模式 | 需要足够回传带宽与低时延 |
| **FlexConnect** | 控制走 WLC，**数据本地交换** | 分支、WAN 不可靠站点 | 需本地 VLAN 配置 + 本地 DHCP |
| **Monitor** | 只收不发，全信道扫描 | wIPS、RF 分析、CleanAir | 不服务客户端，属于"传感器" |
| **Sniffer** | 抓包转发给分析器（如 Wireshark/ACI） | 疑难故障定位 | 只抓指定信道，需人工切换 |
| **Bridge / Mesh** | AP 间无线回传 | 无法布线的区域（仓库、广场） | 每次回传跳数消耗一半吞吐 |
| **Sensor（专用）** | 专用 wIPS 传感器硬件 | 高安全场所 | 成本高，纯监听 |
| **Sniffer + Monitor 混合（SE-Connect）** | 扫描 + 远程频谱分析 | 频谱排障 | 单台专用 |

</div>

#### The Four FlexConnect Settings That Must Be Paired · FlexConnect 的四个必须配对的设置

FlexConnect is not "flip one switch and data is local"; four things must be correct at the same time:

<div class="zh" markdown="1">

FlexConnect 不是"打开一个开关就本地转发"，它需要四件事同时正确：

</div>

| Setting | Location | What happens if it is wrong |
|------|------|-----------|
| **Local Switching on the WLAN** | WLAN config on the WLC | Data still goes back through the tunnel — FlexConnect does nothing |
| **VLAN mapping (VLAN-ACL mapping)** | On the AP: `flexconnect vlan-name → vlan-id` | Clients land in the AP's management VLAN, cross-contaminating services |
| **Trunk the access switch port** | Switch side | Service VLANs other than the AP management VLAN do not pass |
| **Local DHCP / local auth (optional)** | Branch-side server | New clients get no address when the WAN link is down |

<div class="zh" markdown="1">

| 设置 | 位置 | 错了会怎样 |
|------|------|-----------|
| **WLAN 的本地交换（Local Switching）** | WLC 上 WLAN 配置 | 数据仍然回隧道，等于没用 FlexConnect |
| **VLAN 映射（VLAN-ACL Mapping）** | AP 上 `flexconnect vlan-name → vlan-id` | 客户端被塞进 AP 的管理 VLAN，跨业务串网 |
| **接入交换机端口 Trunk 化** | 交换机侧 | 除 AP 管理 VLAN 外的业务 VLAN 不通 |
| **本地 DHCP / 本地认证（可选）** | 分支侧服务器 | WAN 断链时新客户端拿不到地址 |

</div>

**FlexConnect link-failure behaviour matrix** (the SLA a branch design must spell out):

<div class="zh" markdown="1">

**FlexConnect 断链行为矩阵**（这是分支设计必须写清的 SLA）：

</div>

| WAN state | Already-associated clients | New clients | Authentication | Roaming |
|---------|------------|---------|------|------|
| Normal | Normal | Normal | Centralized (RADIUS) | Cross-AP normal (local) |
| Down (Local Auth enabled) | **Stay online** | Can associate | **Local authentication (pre-staged credentials needed)** | Normal within the same AP group |
| Down (Local Auth disabled) | Stay online (data forwarded locally) | Can associate but may fail auth | Fails | Restricted |
| Down (local forwarding not enabled) | **All offline** | Cannot associate | Fails | Fails |

<div class="zh" markdown="1">

| WAN 状态 | 已关联客户端 | 新客户端 | 认证 | 漫游 |
|---------|------------|---------|------|------|
| 正常 | 正常 | 正常 | 集中（RADIUS） | 跨 AP 正常（本地） |
| 断链（Local Auth 开启） | **保持在线** | 可关联 | **本地认证（需预置凭据）** | 同 AP 组内正常 |
| 断链（Local Auth 关闭） | 保持在线（数据本地转发） | 可关联但可能无法认证 | 失败 | 受限 |
| 断链（未启用本地转发） | **全部离线** | 无法关联 | 失败 | 失败 |

</div>

> ⚠️ **The most common branch design error**: FlexConnect configured without local authentication and local DHCP. When the WAN drops, existing clients keep working (they are already associated), but **next morning when everyone comes back nobody can connect** — and that failure always lands at the worst possible time.

<div class="zh" markdown="1">

> ⚠️ **分支设计最常见的错误**：只配了 FlexConnect 但没配本地认证与本地 DHCP。WAN 一断，老客户端还能用（因为已关联），但**第二天早上所有人重新上班时全部连不上** —— 这个故障总是在最糟的时间出现。

</div>

### The CAPWAP Tunnel Bandwidth Ledger (an unavoidable calculation for Local Mode) · CAPWAP 隧道的带宽账（Local Mode 必须算的一笔）

In Local Mode **all client data is encapsulated into CAPWAP and sent back to the WLC**. That bandwidth must be calculated in the design document, otherwise the first bottleneck after go-live is the WAN or the aggregation link.

<div class="zh" markdown="1">

Local Mode 下**客户端的所有数据都要封装进 CAPWAP 回到 WLC**，这笔带宽必须在设计文档里算清，否则上线后第一个瓶颈就是 WAN/汇聚链路。

</div>

**Per-frame overhead (IPv4, unencrypted)**:

<div class="zh" markdown="1">

**单帧开销（IPv4，未加密）**：

</div>

| Layer | Bytes |
|---|---|
| Original 802.11 data frame (including 24–36 B of 802.11 header) | 1500 |
| CAPWAP data header | 8 |
| UDP (5247) | 8 |
| Outer IP | 20 |
| **Total (DTLS disabled)** | **≈ 1536** |
| With DTLS (data-plane encryption) | **≈ 1560–1580** |

<div class="zh" markdown="1">

| 层 | 字节 |
|---|---|
| 原始 802.11 数据帧（含 802.11 头 24–36 B） | 1500 |
| CAPWAP 数据头 | 8 |
| UDP (5247) | 8 |
| 外层 IP | 20 |
| **合计（DTLS 未启用）** | **≈ 1536** |
| 启用 DTLS（数据面加密） | **≈ 1560–1580** |

</div>

**Worked example: one floor with 40 Wi-Fi 6 APs, 300 Mbps of peak user traffic each**

<div class="zh" markdown="1">

**算例：一个 40 台 Wi-Fi 6 AP 的楼层，每 AP 峰值 300 Mbps 用户流量**

</div>

```
① Bandwidth inflation after tunnelling ≈ 1536/1500 ≈ 1.024 → about +2.4% (negligible without DTLS)
② The real problem is aggregation:
   40 × 300 Mbps = 12 Gbps of tunnel traffic all rushing at the WLC
③ The WLC-side attach capacity must be ≥ 12 Gbps (a WLC with only 10G uplinks is an immediate bottleneck)
④ The link from the aggregation switch to the WLC needs 2×10G LAG or 100G
⑤ If you switch to FlexConnect local forwarding: only control plane plus a little management traffic remains (< 200 Mbps)
```

<div class="zh" markdown="1">

```
① 隧道化后带宽膨胀 ≈ 1536/1500 ≈ 1.024 → 约 +2.4%（不含 DTLS 时几乎可忽略）
② 真正的问题是"汇聚"：
   40 × 300 Mbps = 12 Gbps 隧道流量全部涌向 WLC
③ WLC 侧接入能力必须 ≥ 12 Gbps（若 WLC 只有 10G 上行 → 直接瓶颈）
④ 汇聚交换机到 WLC 的链路需要 2×10G LAG 或 100G
⑤ 若改用 FlexConnect 本地转发：WLC 侧只剩控制面 + 少量管理流量（< 200 Mbps）
```

</div>

**Run this ledger and the conclusion is usually obvious**:

<div class="zh" markdown="1">

**这张账算下来，结论往往很清晰**：

</div>

| Situation | Recommendation |
|---|---|
| APs and WLC in the same campus, core with 100G headroom | Local Mode (consistent policy, centralized auditing; the cost is acceptable) |
| APs at branches, WAN < 1 Gbps | FlexConnect local forwarding (otherwise the tunnel saturates the WAN) |
| High-density venues (auditoria, stadiums) | Local forwarding + local DHCP, control plane back to the WLC |
| Centralized security auditing required (e.g. finance) | Local Mode + out-of-path audit appliances at the core |

<div class="zh" markdown="1">

| 情形 | 推荐 |
|---|---|
| AP 与 WLC 同处一个园区、核心有 100G 余量 | Local Mode（策略统一、审计集中，代价可接受） |
| AP 在分支、WAN < 1 Gbps | FlexConnect 本地转发（否则隧道直接打满 WAN） |
| 高密度场所（会场/体育馆） | 本地转发 + 本地 DHCP，控制面回 WLC |
| 需要集中安全审计（如金融） | Local Mode + 核心侧旁路审计设备 |

</div>

> ⚠️ **The second MTU trap**: after tunnelling, 1536 B > 1500 B. If the AP–WLC path MTU is 1500 you get **fragmentation or silent drops**, which shows up as "small packets fine, large packets stuck" (the login page opens, video freezes). Standard practice: **set the AP–WLC path MTU to ≥ 1550** (1600 recommended with DTLS), or enable fragmentation on the WLC (sacrificing performance). This belongs in the implementation checklist.

<div class="zh" markdown="1">

> ⚠️ **MTU 的第二层坑**：隧道化后 1536 B > 1500 B。如果 AP–WLC 路径 MTU 是 1500，会出现**分片或静默丢包**，表现为"小包正常、大包卡住"（登录界面能开、视频卡死）。标准做法：**AP–WLC 路径 MTU 调到 ≥ 1550**（含 DTLS 建议 1600），或在 WLC 侧启用分片（牺牲性能）。这条必须写进实施检查表。

</div>

### Software Versions, Lifecycle and Upgrade Strategy · 软件版本、生命周期与升级策略

Wireless is the most **version-coupled** area in the whole book: AP firmware, WLC release, endpoint capability, authentication server and licences must all be compatible.

<div class="zh" markdown="1">

无线是全书里**版本耦合度最高**的领域：AP 固件、WLC 版本、终端能力、认证服务器、许可证，五者必须兼容。

</div>

| Concern | Explanation | Design action |
|---|---|---|
| **APSP (AP Service Pack)** | Cisco AP firmware must match the WLC release | Check the compatibility matrix before upgrading the WLC; reserve a window for the APSP download |
| **AP image distribution** | APs download images from the WLC they last joined; cross-site downloads consume WAN bandwidth | Pre-stage with a master AP or a local image server before major upgrades |
| **EOL / EoS** | Last-sale and end-of-support dates for controllers and APs | The three-year plan must state replacement batches |
| **Licences** | AP count licences, DNA/cloud licences (subscription) | Licence expiry means new APs cannot join — a classic cause of "everything collapsed at once" |
| **Rollback capability** | Reverting a release needs the old image and a configuration backup | Export config and keep the old image before every upgrade |
| **Maintenance window** | Wireless is usually a 7×24 service, so upgrades must be phased | Phase by building/floor, non-critical areas first |

<div class="zh" markdown="1">

| 关注点 | 说明 | 设计动作 |
|---|---|---|
| **APSP（AP Service Pack）** | Cisco 的 AP 固件与 WLC 版本必须匹配 | 升级 WLC 前先查兼容矩阵，预留 APSP 下载窗口 |
| **AP 镜像分布** | AP 从上一次 join 的 WLC 下载镜像；跨站点会消耗 WAN 带宽 | 大版本升级前用主控 AP/本地镜像服务器预置 |
| **EOL / EoS** | 控制器与 AP 的停售停服时间 | 3 年规划里必须写清替换批次 |
| **许可证** | AP 数量许可、DNA/云许可（订阅制） | 许可到期 = 新 AP 无法 join，是"突然全崩"的经典原因 |
| **回滚能力** | 版本回退需要旧镜像与配置备份 | 每次升级前导出配置 + 保留旧镜像 |
| **维护窗口** | 无线通常是 7×24 业务，只能分批升级 | 按楼栋/楼层分批，先升非关键区 |

</div>

**Three iron laws of upgrades**:

<div class="zh" markdown="1">

**升级的三条铁律**：

</div>

1. **An HA SSO pair must be upgraded together**; do not leave the two units on different releases (the switchover will fail);
2. **Sites with voice** must re-test roaming interruption after the upgrade (new releases can change FT/RRM default behaviour);
3. **Capture a baseline before the upgrade** (airtime, retry rate, client count, channel plan) and compare afterwards — otherwise "it got worse after the upgrade" can never be proven or refuted.

<div class="zh" markdown="1">

1. **HA SSO 双机必须同步升级**，不能长期版本不一致（否则主备切换会失败）；
2. **带语音的场所**必须在升级后复测漫游中断（新版本可能改变 FT/RRM 默认行为）；
3. **升级前抓一份基线**（airtime、重传率、客户端数、信道图），升级后对比 —— 否则"升级后变差了"永远无法证明或反驳。

</div>

### AP Installation Engineering: The 80% of Problems You Cannot See on a Drawing · AP 安装工程：图纸上看不出来的 80% 问题

Half of RF design is a **physical installation** problem. It is almost never written into design documents, yet it is the largest source of site rework.

<div class="zh" markdown="1">

RF 设计有一半是"物理安装"问题，这部分几乎从不写进设计文档，但它是现场返工最多的来源。

</div>

| Installation problem | Consequence | Rule |
|---|---|---|
| **Mounted inside a metal ceiling** | 10–20 dB of loss; half your coverage vanishes | The antenna face must be exposed; use a ceiling mounting kit for metal ceilings |
| **Too close to metal pipes/ducts/fire mains** | Distorted pattern, new blind spots | At least 30 cm from large metal bodies |
| **Mounted in a corner or on a column** | Half-space coverage, blind spot behind it | Centre-mount on the ceiling, avoid corners |
| **Spacing not per the RF plan (chosen for "looks" or "where the ports are")** | Uneven coverage, capacity deviation | The survey drawing wins; port location yields to RF requirements |
| **Hung too high in high-ceiling spaces** | Excessive coverage radius, low edge rates | Downtilt directional antennas in venues; keep ordinary spaces ≤ 4–5 m |
| **Outdoor orientation / weatherproofing** | Water ingress, lightning damage, thermal throttling | Outdoor-rated AP + surge protection + sun shield |
| **Insufficient power (802.3af with Wi-Fi 6)** | The AP degrades itself (2.4 GHz off, MIMO reduced, power capped) | Check the AP's PoE class; use at/bt |
| **Long antenna feeder runs** | Feeder loss 0.3–0.5 dB/m; 20 m costs 6–10 dB | Prefer integrated-antenna APs; use local power + fibre for long runs |

<div class="zh" markdown="1">

| 安装问题 | 后果 | 规范 |
|---|---|---|
| **装在金属吊顶内** | 衰减 10–20 dB，等于凭空少了一半覆盖 | 天线面必须外露；金属吊顶用吸顶安装件 |
| **贴近金属管道/风管/消防管** | 方向图畸变、出现盲区 | 距大型金属体 ≥ 30 cm |
| **装在墙角/柱边** | 半面覆盖、后方盲区 | 吸顶居中安装，避开墙角 |
| **AP 间距不按 RF 规划（按"美观"或"网口位置"）** | 覆盖不均、容量偏差 | 以勘测图为准，网口位置让位于 RF 需求 |
| **高挑高空间吊装过高** | 覆盖半径过大、边缘速率低 | 场馆用下倾定向天线；普通空间控制高度 ≤ 4–5 m |
| **室外朝向/防水** | 进水、雷击、日照过热降频 | 室外型 AP + 防雷 + 遮阳 |
| **供电不足（802.3af 带 Wi-Fi 6）** | AP 自动降级（关 2.4G、降 MIMO、限功率） | 核对 AP 的 PoE 等级，用 at/bt |
| **AP 与天线馈线过长** | 馈线损耗 0.3–0.5 dB/m，20 m 就损失 6–10 dB | 尽量用内置天线 AP；远距离改本地供电+光纤 |

</div>

> 💡 **One action that eliminates a lot of rework**: mark on the drawings the areas where "**the AP position equals the network port position**" and confirm them early with the construction and fit-out teams. Many projects discover only after the fit-out is finished that "there is no port above the ceiling, so the AP has to go in the corridor" — by then the RF design is void.

<div class="zh" markdown="1">

> 💡 **一个能省掉大量返工的动作**：在图纸上标出"**AP 位置等于网口位置**"的区域，提前和土建/装修方确认。很多项目是在装修完成后才发现"吊顶里没有网口，AP 只能装在走廊"，这时 RF 设计已经作废。

</div>

### Operations Model: Centralized, Cloud-Managed, or Hybrid? · 运维模型：集中、云管、还是"混合"？

| Model | Day-to-day operations | Organisation it fits | Hidden cost |
|---|---|---|---|
| **Fully on-premises centralized** | Own WLC, own upgrades, own monitoring | Dedicated network team, strict compliance | Staff cost, release tracking, spares |
| **Cloud-managed (Meraki-style)** | Cloud configuration, automatic upgrades, cloud monitoring | Thin IT, many branches | Subscription fees; the management plane dies if the internet is unreachable (the data plane usually stays local) |
| **Hybrid (local data + cloud monitoring)** | On-premises controller + cloud analytics (DNA Center/Cloud Monitoring) | Mid-to-large enterprises | Integration complexity |
| **Fully outsourced (MSP)** | The provider operates it; you only manage the SLA | SMBs | Change responsiveness depends on the contract |

<div class="zh" markdown="1">

| 模型 | 日常运维动作 | 适合的组织 | 隐形成本 |
|---|---|---|---|
| **全本地集中管理** | 自建 WLC、自管升级、自建监控 | 有专职网络团队、合规要求高 | 人力成本、版本跟踪、备件 |
| **云管理（Meraki 类）** | 云端配置、自动升级、云端监控 | IT 人力少、分支多 | 订阅费；互联网不可达时管理面失效（数据面通常本地不受影响） |
| **混合（本地数据 + 云监控）** | 本地控制器 + 云分析（如 DNA Center/Cloud Monitoring） | 大中型企业 | 集成复杂度 |
| **完全外包（MSP）** | 服务商运维，企业只管 SLA | 中小企业 | 变更响应速度依赖合同 |

</div>

**The decision sentence**: **"If the management plane (cloud/controller) dies, can the service plane still run?"** If yes → cloud management is acceptable; if no → you need a local control plane plus local forwarding as a fallback.

<div class="zh" markdown="1">

**选择的判断句**：**"如果管理面（云/控制器）挂了，业务面还能不能跑？"** 能跑 → 云管可接受；不能跑 → 必须本地控制面 + 本地转发兜底。

</div>

### Controller High-Availability Design · 控制器高可用设计

| Option | Mechanism | Switchover time | Impact on APs | Cost |
|------|------|---------|---------|------|
| **HA SSO (Active/Standby)** | Two WLCs sync client/AP state over the RP port; APs maintain sessions to both | **< 1 s** (APs unaware) | No re-join | Two units + direct/redundant ports |
| **N+1** | Several Active controllers share one Standby | 30–60 s (APs re-join) | Brief outage, config re-download | Lower |
| **N+N** | Each Active has its own backup | Same as N+1 | Same as N+1 | High |
| **Mutual backup inside a Mobility Group** | Several WLCs form a mobility domain; on failure APs can join another controller | Tens of seconds | Re-join + client re-association | Medium |

<div class="zh" markdown="1">

| 方案 | 机制 | 切换时间 | AP 影响 | 成本 |
|------|------|---------|---------|------|
| **HA SSO（Active/Standby）** | 两台 WLC 通过 RP 端口同步客户端/AP 状态，AP 同时与主备建会话 | **< 1 s**（AP 无感知） | 无重新 join | 两台设备 + 直连/冗余端口 |
| **N+1** | 多台 Active 共享一台 Standby | 30–60 s（AP 重新 join） | 短暂断连、重新下载配置 | 较少 |
| **N+N** | 每台 Active 有对应备份 | 同 N+1 | 同 N+1 | 高 |
| **Mobility Group 内互备** | 多台 WLC 组成移动域，故障时 AP 可加入其他控制器 | 数十秒 | 重新 join + 客户端重关联 | 中等 |

</div>

**Physical requirements for HA SSO (must be explicit in the proposal)**:

<div class="zh" markdown="1">

**HA SSO 的物理要求（写方案时必须明确）**：

</div>

- Both WLCs must be the **same model, same software release, same licences**;
- Requires a **direct Redundancy Port (RP) connection**, or Layer 2 reachability over a dedicated VLAN;
- Requires a **Peer RK and Mobility MAC in the same Layer 2 domain**;
- Upgrades must be **performed on both units together** (never leave them out of step for long).

<div class="zh" markdown="1">

- 两台 WLC 必须**同型号、同软件版本、同许可**；
- 需要 **Redundancy Port（RP）直连**或通过专用 VLAN 二层可达；
- 需要**同一二层域内的 Peer RK 与 Mobility MAC**；
- 升级必须**主备同步升级**（不能长期版本不一致）。

</div>

### Controller Capacity Planning Checklist · 控制器容量规划清单

| Dimension | Question to ask | Typical bottleneck |
|------|-----------|---------|
| **AP count** | Current APs plus three-year growth | Licences hit the ceiling before the hardware does |
| **Client count** | Peak concurrent clients | High density fills the client table first |
| **Throughput** | Sum of all AP peaks × oversubscription ratio | In Local Mode all traffic crosses the controller |
| **Tunnel count** | AP count (one control + one data tunnel per AP) | The WLC's CAPWAP session table |
| **Mobility domain size** | Members inside the Mobility Group | Database sync cost of cross-controller roaming |
| **Management plane** | Time to push template/config changes in bulk | With thousands of APs, one WLAN change can take a long time |

<div class="zh" markdown="1">

| 维度 | 要问的问题 | 典型瓶颈 |
|------|-----------|---------|
| **AP 数** | 当前 AP 数与 3 年增长 | 授权（License）比硬件更早到顶 |
| **客户端数** | 峰值并发客户端 | 高密度会先在客户端表打满 |
| **吞吐** | 所有 AP 峰值之和 × 收敛比 | Local Mode 下所有流量都过控制器 |
| **隧道数** | AP 数（每 AP 一条控制隧道 + 一条数据隧道） | WLC 的 CAPWAP 会话表 |
| **漫游域规模** | Mobility Group 内成员数 | 跨控制器漫游的数据库同步开销 |
| **管理面** | 模板/配置变更的批量下发时间 | 上千 AP 时一次改 WLAN 可能耗时很久 |

</div>

#### Controller Sizing Worked Example (derive the spec from real numbers instead of "buy a bigger one") · 控制器选型算例（用真实数字推规格，而不是"买大一点"）

**Scenario**: a single campus with 3 buildings, 360 APs in total, 9,000 peak concurrent clients, 40% of which are voice/AIoT.

<div class="zh" markdown="1">

**场景**：单园区 3 栋楼，共 360 台 AP，峰值 9,000 并发客户端，其中 40% 是语音/AIoT。

</div>

```
① APs = 360 → controller AP licences ≥ 400 (10% headroom)
② Clients = 9,000 → controller client table ≥ 12,000
③ Throughput (Local Mode) = 360 × 200 Mbps (average peak) × 0.3 oversubscription ≈ 21.6 Gbps
   → if a single WLC has no 20G+ uplink, you must use FlexConnect or split across two
④ Tunnels = 360 control + 360 data = 720 CAPWAP sessions
⑤ Mobility domain = needs two WLCs in HA SSO plus the same Mobility Group
   → suggest 2×(active/standby) + 1 N+1 spare, or 2 HA pairs split by building
⑥ Management plane: pushing one WLAN change to 360 APs typically measures 1–5 minutes
   → budget a 15-minute change window (including verification)
```

<div class="zh" markdown="1">

```
① AP 数 = 360 → 控制器 AP 许可 ≥ 400（留 10% 余量）
② 客户端 = 9,000 → 控制器客户端表 ≥ 12,000
③ 吞吐（Local Mode）= 360 × 200 Mbps（峰值均摊）× 0.3 收敛 ≈ 21.6 Gbps
   → 单台 WLC 若无 20G+ 上行，必须 FlexConnect 或分两台
④ 隧道数 = 360 控制 + 360 数据 = 720 条 CAPWAP
⑤ 漫游域 = 需要两台 WLC 做 HA SSO + 同 Mobility Group
   → 建议 2×(主备) + 1 台 N+1 备用，或按楼栋分 2 对 HA
⑥ 管理面：一次 WLAN 变更下发到 360 台 AP，实测通常 1–5 分钟
   → 变更窗口按 15 分钟估（含验证）
```

</div>

**The usual misjudgement**: checking only "are there enough AP licences" while ignoring the **client table** (high density fills it first), the **tunnel session count** (AP count ×2) and **throughput** (the hidden bottleneck of Local Mode). Whichever of those three saturates first, the symptom is the same: "controller CPU mysteriously at 100%".

<div class="zh" markdown="1">

**常见误判**：只看"AP 许可够不够"，忽略**客户端表**（高密度先打满）、**隧道会话数**（AP 数 ×2）、**吞吐**（Local Mode 的隐性瓶颈）。三条里任何一条到顶，表现都是"控制器 CPU 莫名 100%"。

</div>

---

## Wireless Roaming Design · 无线漫游设计

### What Actually Happens During a Roam · 漫游到底发生了什么

When a client moves from one AP to another it is not "switching a signal", it is a complete three-step process:

<div class="zh" markdown="1">

客户端从一个 AP 换到另一个 AP，不是"切换一个信号"，而是完整的三步过程：

</div>

| Phase | Action | Duration | Optimisation |
|------|------|------|---------|
| **① Scan/discovery** | The client scans channels looking for candidate APs | **35–200 ms** (full-channel scan is worst) | **802.11k** Neighbor Report (tells the client which channels to scan) |
| **② Authentication/association** | 802.11 Open authentication (no real security) + Reassociation Request → Response | 5–30 ms | **802.11r** (FT, moves key negotiation earlier), **802.11v** BSS Transition |
| **③ Key negotiation** | Four-way handshake (if the PMK is not cached) or direct PTK derivation | **20–150 ms** (a full 802.1X run can take seconds) | **PMK caching (OKC/PKC/CCKM)**, **802.11r** |

<div class="zh" markdown="1">

| 阶段 | 动作 | 耗时 | 优化手段 |
|------|------|------|---------|
| **① 扫描/发现** | 客户端扫描信道，寻找候选 AP | **35–200 ms**（全信道扫描最慢） | **802.11k** Neighbor Report（告诉客户端"该扫哪些信道"） |
| **② 认证/关联** | 802.11 Open 认证（无实际意义）+ Reassociation Request → Response | 5–30 ms | **802.11r**（FT，把密钥协商提前）、**802.11v** BSS Transition |
| **③ 密钥协商** | 4 次握手（若 PMK 未缓存）或直接派生 PTK | **20–150 ms**（完整 802.1X 可达数秒） | **PMK 缓存（OKC/PKC/CCKM）**、**802.11r** |

</div>

**Total latency budget**:

<div class="zh" markdown="1">

**总时延预算**：

</div>

| Service | Acceptable roaming interruption | Must enable |
|------|--------------|---------|
| Web/mail | < 1 s (barely noticeable) | Nothing special |
| **Voice (VoIP)** | **< 50 ms** (otherwise audio drops) | 802.11k + 802.11r (or CCKM) + WMM CAC |
| Video conferencing | < 150 ms | 802.11k + 802.11r + QoS |
| Real-time industrial control | < 20 ms | 802.11r + single band/dedicated SSID + MLO (Wi-Fi 7) |

<div class="zh" markdown="1">

| 业务 | 可接受漫游中断 | 必须启用 |
|------|--------------|---------|
| 网页/邮件 | < 1 s（感知不明显） | 无特殊要求 |
| **语音（VoIP）** | **< 50 ms**（否则丢音） | 802.11k + 802.11r（或 CCKM）+ WMM CAC |
| 视频会议 | < 150 ms | 802.11k + 802.11r + QoS |
| 实时工业控制 | < 20 ms | 802.11r + 单一频段/专用 SSID + MLO（Wi-Fi 7） |

</div>

> ⚠️ **The most common voice fault**: "the Wi-Fi call drops for a moment when I walk into the corridor". Nine times out of ten the cause is **802.11k/v enabled but no 802.11r and no PMK caching** — every roam performs a full 802.1X run, the interruption exceeds 300 ms and the voice stream loses packets outright.

<div class="zh" markdown="1">

> ⚠️ **最常见的语音故障**："Wi-Fi 通话走到走廊就断一下"。九成原因是**只开了 802.11k/v，没开 802.11r 也没做 PMK 缓存** —— 每次漫游都要重新做完整 802.1X，中断 300 ms 以上，语音流直接丢包。

</div>

### Roaming Type Matrix · 漫游类型矩阵

| Type | Scenario | Client IP change | Key mechanism |
|------|------|--------------|---------|
| **Intra-AP roaming (BSSID change on the same AP)** | Different radios on one AP | None | No special handling |
| **Intra-controller Layer 2 roaming** | Same WLC, same VLAN | None | Internal re-association, PMK cache hit |
| **Inter-controller Layer 2 roaming** | Different WLCs, same VLAN (Layer 2 connected) | None | **Mobility Group**: syncs the client table and PMK |
| **Inter-controller Layer 3 roaming** | Different WLCs, different subnets | **Keeps the old IP** (via tunnel) | **Anchor / Foreign** (traffic hairpins to the original anchor) |
| **Cross-mobility-domain roaming** | Different Mobility Domains | Usually needs a new IP | Not seamless; service interruption |

<div class="zh" markdown="1">

| 类型 | 场景 | 客户端 IP 变化 | 关键机制 |
|------|------|--------------|---------|
| **AP 内漫游（同 AP 换 BSSID）** | 同一 AP 不同射频 | 不变 | 无需特殊处理 |
| **控制器内二层漫游** | 同一 WLC、同一 VLAN | 不变 | 控制器内部重关联，PMK 缓存命中 |
| **控制器间二层漫游** | 不同 WLC、同一 VLAN（二层连通） | 不变 | **Mobility Group**：同步客户端表与 PMK |
| **控制器间三层漫游** | 不同 WLC、不同子网 | **保持旧 IP**（靠隧道） | **Anchor / Foreign**（流量折返原锚点） |
| **跨移动域漫游** | 不同 Mobility Domain | 通常要重新获取 IP | 不支持无缝，业务中断 |

</div>

#### Layer 2 Roaming: Mobility Group · 二层漫游：Mobility Group

**Preconditions (all four are mandatory)**:

<div class="zh" markdown="1">

**前置条件（四条，缺一不可）**：

</div>

1. All WLCs join the **same Mobility Group** and are configured with the **same Mobility Domain name**
2. The WLANs have **identical SSID and security policy** (same name, different policy = roaming failure)
3. The **same VLAN/subnet exists on both sides** (Layer 2 connectivity)
4. **Ports 16666/16667 (mobility) are reachable** between the WLCs, with latency < 100 ms

<div class="zh" markdown="1">

1. 所有 WLC 加入**同一 Mobility Group**，并配置**同一 Mobility Domain 名称**
2. WLAN **SSID 与安全策略完全一致**（同名不同策略 = 漫游失败）
3. **同一 VLAN/子网**在两端都存在（二层连通）
4. WLC 之间 **16666/16667（mobility）端口可达**，且时延 < 100 ms

</div>

**What gets synchronised**: client MAC, IP, QoS state, **PMK cache (PMKID)** and 802.11r key material. Because the PMK is synchronised, cross-controller roaming does not need a new 802.1X run.

<div class="zh" markdown="1">

**同步了什么**：客户端 MAC、IP、QoS 状态、**PMK 缓存（PMKID）**、802.11r 密钥信息。正因为 PMK 同步了，跨控制器漫游才不需要重新做 802.1X。

</div>

#### Layer 3 Roaming: The Cost of Anchor / Foreign · 三层漫游：Anchor / Foreign 的代价

Layer 3 roaming works like this: the client associates on the Foreign controller, which "hangs" it off the original **Anchor**, and **all traffic hairpins through a tunnel back to the anchor's gateway**.

<div class="zh" markdown="1">

三层漫游的机制是：客户端在 Foreign 控制器上关联，但控制器把它"挂"在原来的 **Anchor** 上，**所有流量经隧道折返 Anchor 的网关**。

</div>

| Advantage | Cost |
|------|------|
| Client IP is preserved, sessions survive (VoIP, video, database connections) | **Traffic hairpinning**: longer physical path, higher latency |
| No client-side Mobile IP support needed | **The anchor becomes a bandwidth and failure single point** |
| Decouples from existing subnet planning | Complex troubleshooting (`show client detail` to inspect the anchor relationship) |
| | At scale, tunnel count and state pressure are significant |

<div class="zh" markdown="1">

| 优点 | 代价 |
|------|------|
| 客户端 IP 不变，会话不断（VoIP、视频、数据库连接） | **流量折返**：物理路径变长，时延增加 |
| 无需客户端支持移动 IP | **Anchor 成为带宽与故障单点** |
| 与现有子网规划解耦 | 排障复杂（`show client detail` 要看 anchor 关系） |
| | 大规模漫游时隧道数量与状态压力大 |

</div>

> 💡 **Modern design advice**: if a **single Layer 2 mobility domain (one large VLAN or a unified subnet)** can solve it, do not use Layer 3 roaming. Layer 3 roaming fits "across buildings or campuses where a single large Layer 2 domain is impossible" and where the application genuinely cannot tolerate an IP change. With Wi-Fi 7 MLO and 802.11r, "fast reconnect + session re-establishment" has become acceptable for some applications, so Layer 3 roaming is becoming less necessary.

<div class="zh" markdown="1">

> 💡 **现代设计建议**：能用**单一二层漫游域（大 VLAN 或统一子网）**解决的，就不要用三层漫游。三层漫游的适用场景通常是"跨楼栋/跨园区，无法统一大二层"，且业务确实不能容忍 IP 变化。Wi-Fi 7 的 MLO 与 802.11r 使"快速重连 + 重建会话"在某些应用上已可接受，三层漫游的必要性在下降。

</div>

### Comparing Four Key Caching Mechanisms · 四种密钥缓存机制对比

| Mechanism | Standardisation | Who caches | Principle | Compatibility |
|------|-------|--------|------|--------|
| **OKC (Opportunistic Key Caching)** | Vendor consensus (not an 802.11 standard) | Client + controller | Derives PMK-R0/R1 from the PMK; the client reuses it | Widely supported by 802.11i-capable endpoints |
| **PKC (Proactive Key Caching, Cisco 802.11i)** | Cisco extension | Controller | Proactively distributes the PMK to neighbour controllers via RADIUS | Needs RADIUS support (Cisco ACS/ISE) |
| **CCKM (Cisco Centralized Key Management)** | Cisco proprietary | Controller | The client uses a CCKM IE to request keys from the new AP, bypassing 802.1X | Cisco clients only / some third parties |
| **802.11r FT (Fast BSS Transition)** | **Standard** | Whole network (Mobility Domain) | Pre-distributes PMK-R1 to neighbour APs; PTK is derived directly at re-association | Needs endpoint FT support (recent iOS/Android generally support it) |

<div class="zh" markdown="1">

| 机制 | 标准化 | 谁缓存 | 原理 | 兼容性 |
|------|-------|--------|------|--------|
| **OKC（Opportunistic Key Caching）** | 厂商共识（非 802.11 标准） | 客户端 + 控制器 | 从 PMK 派生 PMK-R0/R1，客户端复用它 | 支持 802.11i 的终端普遍支持 |
| **PKC（Proactive Key Caching，Cisco 802.11i）** | Cisco 扩展 | 控制器 | 通过 RADIUS 主动把 PMK 分发给邻居控制器 | 需要 RADIUS 支持（Cisco ACS/ISE） |
| **CCKM（Cisco Centralized Key Management）** | Cisco 专有 | 控制器 | 客户端用 CCKM IE 请求新 AP 的密钥，跳过 802.1X | 仅 Cisco 客户端/部分第三方 |
| **802.11r FT（Fast BSS Transition）** | **标准** | 全网（Mobility Domain） | 预先把 PMK-R1 分发给邻居 AP，重关联时直接派生 PTK | 需要终端支持 FT（iOS/Android 新机型基本支持） |

</div>

**The two 802.11r modes**:

<div class="zh" markdown="1">

**802.11r 的两种模式**：

</div>

- **Over-the-Air (FT-OA)**: the client exchanges FT authentication frames directly with the new AP. Lowest latency (< 50 ms); recommended.
- **Over-the-DS (FT-ODS)**: FT frames are relayed via the old AP over the DS (wired side). Useful when the client cannot talk to the new AP directly, but it needs extra tunnelling machinery.

<div class="zh" markdown="1">

- **Over-the-Air（FT-OA）**：客户端直接与新 AP 交换 FT 认证帧。延迟最低（< 50 ms），推荐。
- **Over-the-DS（FT-ODS）**：通过旧 AP 经 DS（有线侧）转发 FT 帧。适用于客户端无法直接与新 AP 通信的场景，但需要额外的隧道机制。

</div>

> ⚠️ **The 802.11r compatibility trap**: some older endpoints (certain IoT devices, older Android handsets, some printers) **fail to associate or flap repeatedly** once 802.11r is enabled. The standard production answer is **Adaptive 11r**: endpoints that do not support FT fall back to classic roaming, while those that do use FT. Also note that **WPA3 mandates PMF** and 802.11r needs PMF alongside it, so validate them together.

<div class="zh" markdown="1">

> ⚠️ **802.11r 的兼容性陷阱**：部分老终端（尤其是某些 IoT、老款 Android、部分打印机）在开启 802.11r 后**无法关联或反复掉线**。生产上的标准解法是开启 **Adaptive 11r（自适应 802.11r）**：对不支持 FT 的终端自动回退到传统漫游，对支持的使用 FT。同时 **WPA3 强制 PMF**，而 802.11r 需要 PMF 配合，配置时要一起验证。

</div>

### The Division of Labour Between 802.11k / v / r · 11k / v / r 三件套的分工

| Standard | Name | What it solves | What happens without it |
|------|------|---------|------------|
| **802.11k** | Radio Resource Measurement | Gives the client a **neighbour AP list** (Neighbor Report) | The client blind-scans every channel, costing 100–200 ms before each roam |
| **802.11v** | BSS Transition Management | The controller/AP can **suggest** that the client move to a better AP | Clients stick to weak APs (sticky client) |
| **802.11r** | Fast BSS Transition | Distributes keys in advance, skipping 802.1X at re-association | Every roam re-authenticates, interrupting for 300 ms+ |

<div class="zh" markdown="1">

| 标准 | 名称 | 解决什么 | 没有它会怎样 |
|------|------|---------|------------|
| **802.11k** | Radio Resource Measurement | 给客户端一份**邻居 AP 列表**（Neighbor Report） | 客户端盲扫全信道，漫游前扫描耗时 100–200 ms |
| **802.11v** | BSS Transition Management | 控制器/AP 可以**建议**客户端换到更好的 AP | 客户端"粘"在弱信号 AP 上不走（sticky client） |
| **802.11r** | Fast BSS Transition | 提前分发密钥，重关联时跳过 802.1X | 每次漫游都重做认证，中断 300 ms+ |

</div>

**The relationship between them**: k decides "where to scan", v decides "you should leave", r decides "leave quickly". **Enabling only one has limited effect**; for voice, enable all three (with Adaptive 11r).

<div class="zh" markdown="1">

**三者的关系**：k 解决"往哪扫"，v 解决"该走了"，r 解决"走得快"。**只开其中一个效果都有限**，语音场景建议三个全开（配合 Adaptive 11r）。

</div>

#### How 802.11v BTM Actually Interacts (and why it sometimes "will not move") · 11v BTM 的实际交互（为什么有时候"叫不动"）

```
① AP/WLC detects client RSSI < threshold (or load imbalance / steering back to 5 GHz)
② The AP sends a BSS Transition Management Request (with a candidate AP list)
③ The client picks one of three responses:
   a. Accept (move to the suggested AP) — ideal
   b. Reject (with a reason)
   c. Silence (most common!)
④ If the client stays silent, the controller can only "hard disconnect" it when MIN RSSI triggers (Disassociation)
```

<div class="zh" markdown="1">

```
① AP/WLC 检测到客户端 RSSI < 阈值（或负载不均 / 需要踢回 5 GHz）
② AP 发 BSS Transition Management Request（附带候选 AP 列表）
③ 客户端三选一：
   a. Accept（去建议的 AP）—— 理想
   b. Reject（拒绝，附带原因）
   c. 沉默（最常见！）
④ 若持续沉默，控制器只能在 MIN RSSI 触发时"硬断开"（Disassociation）
```

</div>

**Silence is the norm**: plenty of endpoints (older Android, some IoT, some Windows NIC drivers) do not implement 11v at all. Therefore:

<div class="zh" markdown="1">

**"沉默"是常态**：大量终端（尤其是老 Android、部分 IoT、Windows 网卡驱动）根本不实现 11v。所以：

</div>

> ⚠️ **Never promise in a proposal that "11v load balancing will automatically move people onto idle APs"**. The real capability is: **persuade where you can, and hard-disconnect at −67 dBm where you cannot**. A hard disconnect looks like "the Wi-Fi icon blinks", and for voice it means dropped audio — so for voice, add AP density rather than relying on hard disconnects.

<div class="zh" markdown="1">

> ⚠️ **不要在方案里承诺"11v 负载均衡能自动把人赶到空闲 AP"**。真实能力是：**能劝的劝，劝不动就在 -67 dBm 硬断**。硬断的体验是"Wi-Fi 图标闪一下"，对语音是丢音 —— 所以语音场景宁可加密 AP，也不要依赖硬断。

</div>

#### The Roaming Timeline: A Microsecond-Level Breakdown (the optimisation target for voice) · 漫游时间线：µs 级拆解（语音场景优化目标）

| Phase | No optimisation | With k | With k + r + PMK cache | Explanation |
|---|---|---|---|---|
| Channel scan (find candidates) | 100–200 ms | 20–40 ms | 20–40 ms | Full-channel scan is worst; k's Neighbor Report narrows it |
| Authentication + re-association | 10–30 ms | 10–30 ms | 10–30 ms | With r, FT authentication frames replace the classic exchange |
| Full 802.1X authentication | **200–2000 ms** | Same | **0 ms** (PMK cache hit) | This is the great watershed |
| Four-way handshake / FT PTK derivation | 20–50 ms | Same | 10–50 ms | FT pre-derives PMK-R1 |
| Uplink path switch (AP forwarding table) | 1–5 ms | Same | 1–5 ms | Cross-controller adds tunnel re-establishment |
| **Total** | **0.3–3 s** | 0.1–0.2 s | **30–60 ms** | Voice requires < 50 ms (including retransmission and jitter margin) |

<div class="zh" markdown="1">

| 阶段 | 无优化 | 开 k | 开 k + r + PMK 缓存 | 说明 |
|---|---|---|---|---|
| 信道扫描（发现候选） | 100–200 ms | 20–40 ms | 20–40 ms | 全信道扫描最慢；k 的 Neighbor Report 限定范围 |
| 认证 + 重关联 | 10–30 ms | 10–30 ms | 10–30 ms | 开 r 时用 FT 认证帧替代 |
| 802.1X 完整认证 | **200–2000 ms** | 同 | **0 ms**（PMK 缓存命中） | 这是最大的分水岭 |
| 4 次握手 / FT 派生 PTK | 20–50 ms | 同 | 10–50 ms | FT 提前派生 PMK-R1 |
| 上行路径切换（AP 侧转发表） | 1–5 ms | 同 | 1–5 ms | 跨控制器时含隧道重建 |
| **合计** | **0.3–3 s** | 0.1–0.2 s | **30–60 ms** | 语音要求 < 50 ms（含重传与抖动余量） |

</div>

**This table is the entire argument for "voice must have r plus PMK caching"**. Enabling only k/v takes 0.3 s down to 0.2 s, which still misses the voice threshold.

<div class="zh" markdown="1">

**这张表就是"为什么语音必须开 r + PMK 缓存"的全部论证**。只开 k/v 只能把 0.3 s 降到 0.2 s，跨不过语音的门槛。

</div>

#### The Five Roaming Failure Modes · 漫游失败的五种模式

| Mode | Symptom | Root cause | Verification |
|---|---|---|---|
| **Sticky client** | Stays on the old AP far too long at a very low rate and never switches | Insufficient coverage overlap / conservative client algorithm / MIN RSSI not set | Walk the path and record the RSSI curve |
| **Ping-pong** | Flips back and forth between two APs, briefly interrupting each time | The two APs are too close in signal (difference < 3 dB) and both sit near the threshold | Check the client association history (flap counters) |
| **Authentication failure after roam** | Re-association succeeds, then it drops immediately and retries | Mobility Group not built / PMK not synced / SSID security policies differ | `show client detail` on the WLC, check the auth failure reason |
| **No address after roam** | Associates but has no IP, or the IP does not match the VLAN | Dynamic VLAN assignment failed / target AP lacks that VLAN / DHCP pool exhausted | The switch sees DHCP Discover but no Offer |
| **Service dies after roam (IP changed)** | Roam succeeds but every session breaks (VPN, database) | Cross-subnet roam with no anchor / client has no Mobile IP | Compare the client IP before and after the roam |

<div class="zh" markdown="1">

| 模式 | 现象 | 根因 | 验证 |
|---|---|---|---|
| **粘滞不漫游** | 走到很远还在用旧 AP，速率极低但不切换 | 覆盖重叠不足 / 客户端算法保守 / MIN RSSI 未设 | 走一遍路径，记录 RSSI 变化曲线 |
| **反复横跳（Ping-Pong）** | 在两个 AP 间来回切换，每次短暂中断 | 两个 AP 信号过于接近（差值 < 3 dB）且都在阈值附近 | 看客户端关联历史（flap 计数） |
| **漫游后认证失败** | 重关联成功但立刻掉线，反复重试 | Mobility Group 未建 / PMK 未同步 / SSID 安全策略不一致 | WLC 上 `show client detail`，看认证失败原因 |
| **漫游后拿不到地址** | 关联成功但无 IP，或 IP 与 VLAN 不匹配 | 动态 VLAN 下发失败 / 目标 AP 无该 VLAN / DHCP 池耗尽 | 交换机抓到 DHCP Discover 但无 Offer |
| **漫游后业务断（IP 变）** | 漫游成功但会话全断（VPN、数据库） | 跨子网漫游且无 Anchor / 客户端未用移动 IP | 对比漫游前后客户端 IP |

</div>

> 💡 **Ping-pong is the hardest to explain**: users only feel that "it is good sometimes and bad sometimes". The design answer is **hysteresis**: leave a 5–8 dB gap between MIN RSSI and the threshold for switching back, so the client does not oscillate on the equal-signal contour.

<div class="zh" markdown="1">

> 💡 **"反复横跳"是最难解释的一种**：用户只觉得"时好时坏"。设计上的解法是**设置滞回（hysteresis）**：MIN RSSI 与"切回原 AP 的门槛"之间留 5–8 dB 差，避免在等信号线上震荡。

</div>

#### Mobility Domain Planning: One Big Layer 2 or Layer 3? · 漫游域规划：大二层还是三层？

| Option | Approach | Advantages | Cost | Where it fits |
|---|---|---|---|---|
| **Single large Layer 2 domain (preferred)** | One VLAN/subnet across the campus (or a few large VLANs) | Fastest roaming, no tunnels, no hairpinning | Large broadcast domain, large failure domain, strict broadcast suppression needed | Single building, small-to-medium campus |
| **Multiple VLANs + Layer 2 connectivity** | Different VLAN per floor, same Mobility Group | Broadcast domain stays controllable | Cross-VLAN needs Layer 3 roaming or client reconnect | Large campuses (VLAN per building) |
| **Layer 3 roaming (Anchor)** | Client keeps its IP, traffic hairpins to the anchor | IP preserved, sessions survive | Detour path, anchor single point, bandwidth amplification | Cross-campus where a unified Layer 2 is impossible |
| **Re-addressing (no roaming)** | New subnet means a new IP | Simplest, no tunnels | Sessions break (VPN reconnect, video drops) | Data-centric services with no real-time sessions |

<div class="zh" markdown="1">

| 方案 | 做法 | 优点 | 代价 | 适用 |
|---|---|---|---|---|
| **单一大二层（推荐优先）** | 全园区同一 VLAN/子网（或几个大 VLAN） | 漫游最快、无隧道、无折返 | 广播域大、故障域大、需严格抑制广播 | 单栋楼、中小园区 |
| **多 VLAN + 二层连通** | 不同楼层不同 VLAN，但同 Mobility Group | 广播域可控 | 跨 VLAN 需三层漫游或客户端重连 | 大园区（按楼栋 VLAN） |
| **三层漫游（Anchor）** | 客户端保持原 IP，流量折返 Anchor | IP 不变、会话不断 | 流量绕行、Anchor 单点、带宽放大 | 跨园区、无法统一二层 |
| **重新寻址（无漫游）** | 换子网就重拿 IP | 最简单、无隧道 | 会话中断（VPN 重连、视频断） | 数据业务为主、无实时会话 |

</div>

**The deciding sentence**: **"Do we have services that must survive while moving?"** If yes (voice, mobile clinical rounds, AGVs) → you need a Layer 2 mobility domain or an anchor. If no → letting the client take a new IP is the cheapest option; do not build Layer 3 roaming just because it sounds advanced.

<div class="zh" markdown="1">

**判决句**：**"有没有必须在移动中保持会话的业务？"** 有（语音、移动查房、AGV）→ 必须二层漫游域或 Anchor；没有 → 让客户端重新拿 IP 是成本最低的方案，不要为了"技术先进"去造三层漫游。

</div>

#### Cross-Site Roaming (Between Buildings / Between Cities) · 跨站点漫游（大楼之间 / 城市之间）

| Distance | Seamless roaming possible? | Explanation |
|---|---|---|
| Same building, different floors | Yes | Same Mobility Group, same subnet |
| Adjacent buildings (same campus, Layer 2 reachable) | Yes | Needs a Mobility Group + latency < 100 ms |
| Cross-campus (Layer 3 reachable) | Technically yes (Anchor) | Hairpinning is expensive; generally not recommended |
| Cross-city | **Should not be attempted** | Latency and bandwidth rule it out; design for "re-associate + application-layer reconnect" |

<div class="zh" markdown="1">

| 距离 | 是否可能无缝漫游 | 说明 |
|---|---|---|
| 同楼不同楼层 | 是 | 同 Mobility Group、同子网 |
| 相邻楼栋（同园区，二层可通） | 是 | 需 Mobility Group + 时延 < 100 ms |
| 跨园区（三层可达） | 技术上可（Anchor） | 流量折返代价大，通常不建议 |
| 跨城市 | **不应尝试** | 时延与带宽都不允许；应设计成"重新关联 + 应用层重连" |

</div>

> ⚠️ **A common bad requirement**: "our staff want seamless roaming between headquarters and the branch." This is not a wireless problem, it is **application session persistence**. The correct answer: use the same SSID and the same authentication (same-domain credentials) so the client re-authenticates quickly at the new site; as for sessions, leave that to the application layer (cloud applications handle it natively; on-premises client/server applications need redesign).

<div class="zh" markdown="1">

> ⚠️ **一个常见的错误需求**："我们员工在总部和分公司之间也想无缝漫游。" 这不是无线问题，是**应用会话保持问题**。正确回答是：用同一 SSID + 同一认证（同域凭据），让客户端在新站点快速重新认证上网；至于会话，交给应用层（云应用天然支持，本地 C/S 应用需要重新设计）。

</div>

### Roaming Design Checklist · 漫游设计检查清单

| Check item | Target value | How to verify |
|--------|--------|---------|
| **Adjacent AP coverage overlap** | **15%–20%** overlap area | Survey plot; RSSI in the overlap area both > −67 dBm |
| **Signal difference at the roam point** | Adjacent APs differ by **≤ 5 dB** at the roam point | Active survey walking the path and recording |
| **MIN RSSI (forced disconnect)** | −67 dBm (voice −65 dBm) | Controller RF Profile |
| **Data rate floor** | 1/2/5.5/11 Mbps disabled | WLC `data-rate` configuration |
| **PMK cache / 802.11r** | Mandatory on voice SSIDs | Packet capture: does Reassoc go straight to 4-way (no 802.1X)? |
| **802.11k/v** | Recommended | Packet capture: are there Neighbor Reports / BTM Requests? |
| **Mobility domain consistency** | Same SSID, same security, same VLAN | Diff configurations across controllers |
| **Fallback capability** | Adaptive 11r / WPA2+WPA3 transition | Test with genuinely old endpoints |

<div class="zh" markdown="1">

| 检查项 | 目标值 | 怎么验证 |
|--------|--------|---------|
| **相邻 AP 覆盖重叠** | **15%–20%** 的覆盖交叠区 | 勘测图，交叠区 RSSI 均 > -67 dBm |
| **漫游点信号差** | 相邻 AP 在漫游点 **差值 ≤ 5 dB** | 主动勘测沿路径走动记录 |
| **MIN RSSI（强制断开）** | -67 dBm（语音 -65 dBm） | 控制器 RF Profile |
| **数据速率下限** | 关闭 1/2/5.5/11 Mbps | WLC `data-rate` 配置 |
| **PMK 缓存 / 802.11r** | 语音 SSID 必开 | 抓包看 Reassoc 后是否直接 4-way（无 802.1X） |
| **802.11k/v** | 建议开启 | 抓包看是否有 Neighbor Report / BTM Request |
| **移动域一致性** | 同 SSID、同安全、同 VLAN | 跨控制器检查配置差异 |
| **回退能力** | Adaptive 11r / WPA2+WPA3 过渡 | 用老终端实测 |

</div>

---

## Wireless Security and Authentication · 无线安全与认证

### Security Protocol Evolution · 安全协议演进

| Protocol | Encryption/integrity | Key management | Resists offline dictionary attack | Status |
|---------|-----------|---------|-----------|------|
| **WEP** | RC4 + CRC32 | Static keys (40/104 bit) | No | **Broken (minutes to crack)**, disable |
| **WPA (WPA1)** | TKIP + Michael MIC (RC4) | PSK / 802.1X | No | Transitional, legacy compatibility only |
| **WPA2-Personal** | AES-CCMP | PSK (four-way handshake) | **No** (capture the handshake and brute-force offline) | Current mainstream (but PSK carries risk) |
| **WPA2-Enterprise** | AES-CCMP | 802.1X/EAP + RADIUS | Not applicable (per-user credentials) | The enterprise standard |
| **WPA3-Personal** | AES-CCMP / GCMP | **SAE** (peer authentication) | **Yes** (per-session, forward secrecy) | First choice for new deployments |
| **WPA3-Enterprise** | AES-GCMP-256 | 802.1X + 192-bit suite | Not applicable | High security (government/finance) |
| **OWE (enhanced open)** | AES-CCMP | No authentication, encryption only | Not applicable | The guest "encrypted open network" |

<div class="zh" markdown="1">

| 安全协议 | 加密/完整性 | 密钥管理 | 抗离线字典 | 状态 |
|---------|-----------|---------|-----------|------|
| **WEP** | RC4 + CRC32 | 静态密钥（40/104 bit） | 否 | **已被攻破（几分钟可破）**，禁用 |
| **WPA（WPA1）** | TKIP + Michael MIC（RC4） | PSK / 802.1X | 否 | 过渡方案，仅兼容老设备 |
| **WPA2-Personal** | AES-CCMP | PSK（4 次握手） | **否**（抓到握手包可离线爆破） | 当前主流（但 PSK 有风险） |
| **WPA2-Enterprise** | AES-CCMP | 802.1X/EAP + RADIUS | 不适用（用户级凭据） | 企业标准 |
| **WPA3-Personal** | AES-CCMP / GCMP | **SAE**（对等认证） | **是**（每会话独立，前向保密） | 新部署首选 |
| **WPA3-Enterprise** | AES-GCMP-256 | 802.1X + 192 位套件 | 不适用 | 高安全（政府/金融） |
| **OWE（增强开放）** | AES-CCMP | 无认证，仅加密 | 不适用 | 访客网"加密的开放网络" |

</div>

> ⚠️ **You must separate "encryption" from "authentication"**: WEP and WPA2 are **encryption** schemes; "does this Wi-Fi need a password" is an **authentication** question. Using OWE on a guest network only fixes over-the-air eavesdropping, not "who is allowed to connect" — the latter still needs a portal / PPSK / MAC filter plus higher-layer policy.

<div class="zh" markdown="1">

> ⚠️ **必须区分"加密"与"认证"**：WEP/WPA2 都是**加密**方案；"这个 Wi-Fi 要不要密码"是**认证**问题。访客网用 OWE 只解决"空口被窃听"，不解决"谁能连"——后者仍要靠 Portal / PPSK / MAC 过滤 + 上层策略。

</div>

### Enterprise Authentication: The Full 802.1X/EAP Flow · 企业认证：802.1X/EAP 全流程

```
       Client (Supplicant)        AP/WLC (Authenticator)        RADIUS (Auth server)
             |                            |                            |
             |--- EAPOL-Start ----------->|                            |
             |<-- EAP-Request/Identity ---|                            |
             |--- EAP-Response/Identity ->|                            |
             |                            |--- Access-Request -------->|
             |<-- EAP-Request(method) ----|<-- Access-Challenge -------|
             |      ... several EAP exchanges (TLS tunnel/cert/password) ...
             |                            |--- Access-Accept --------->|
             |                            |    (+ MS-MPPE master key)  |
             |<== four-way handshake (derive PTK) ===>|                 |
             |<== encrypted data path ================>|                 |
```

<div class="zh" markdown="1">

```
       客户端(Supplicant)          AP/WLC(Authenticator)         RADIUS(认证服务器)
             |                            |                            |
             |--- EAPOL-Start ----------->|                            |
             |<-- EAP-Request/Identity ---|                            |
             |--- EAP-Response/Identity ->|                            |
             |                            |--- Access-Request -------->|
             |<-- EAP-Request(方法) ------|<-- Access-Challenge -------|
             |      ... 多轮 EAP 交换（TLS 隧道/证书/密码） ...           |
             |                            |--- Access-Accept --------->|
             |                            |    (+ MS-MPPE 主密钥)      |
             |<== 4 次握手（派生 PTK）====>|                            |
             |<== 加密数据通道 ===========>|                            |
```

</div>

**Four key insights**:

<div class="zh" markdown="1">

**四个关键认知**：

</div>

1. **The AP is a relay**: EAP messages are wrapped by the client in 802.11 frames and the AP forwards them to the server in **RADIUS encapsulation**. The AP does not understand the credentials.
2. **The key is generated in RADIUS**: Access-Accept carries `MS-MPPE-Recv-Key`/`Send-Key` (the PMK material), and that is the root of the four-way handshake.
3. **This is the basis of PMK caching**: once derived, the PMK can be cached (OKC/PKC/802.11r), so roaming no longer touches RADIUS.
4. **RADIUS down = every new user down**: associated clients are unaffected, but any new association or roam to an AP with no cached PMK fails. This is the **number one single point of failure** in wireless authentication.

<div class="zh" markdown="1">

1. **AP 是"二传手"**：EAP 报文由客户端封装在 802.11 帧里，AP 用 **RADIUS 封装**转给服务器。AP 不理解凭据内容。
2. **密钥在 RADIUS 里生成**：Access-Accept 会带 `MS-MPPE-Recv-Key`/`Send-Key`（即 PMK 材料），这才是 4 次握手的根。
3. **PMK 缓存的基础就在这**：PMK 一旦算出，可以被缓存（OKC/PKC/802.11r），漫游时不再访问 RADIUS。
4. **RADIUS 挂了 = 新用户全挂**：已关联客户端不受影响，但任何新关联/漫游到未缓存 AP 都会失败。这是无线认证的**头号单点**。

</div>

### EAP Method Selection · EAP 方法选型

| Method | Credential | Server certificate | Client certificate | MitM resistance | Where it fits |
|------|------|-----------|-----------|---------|------|
| **EAP-TLS** | Mutual certificates | Required | **Required** | Strongest | Corporate devices (domain PCs, managed mobile devices) |
| **PEAP-MSCHAPv2** | Username/password | Required | Not needed | Medium (depends on the client validating the certificate) | General enterprise (most common) |
| **EAP-TTLS** | Any (multi-factor possible) | Required | Not needed | Medium | When a flexible inner method is needed |
| **EAP-FAST** | Username/password + PAC | Optional | PAC file | Medium | Legacy Cisco environments |
| **TEAP** | Certificate + password (chained) | Required | Optional | Strong | When "machine + user" dual authentication is needed |

<div class="zh" markdown="1">

| 方法 | 凭据 | 服务端证书 | 客户端证书 | 抗中间人 | 适用 |
|------|------|-----------|-----------|---------|------|
| **EAP-TLS** | 双向证书 | 必须 | **必须** | 最强 | 企业设备（域内 PC、受管移动设备） |
| **PEAP-MSCHAPv2** | 用户名/密码 | 必须 | 不需要 | 中（依赖客户端校验证书） | 通用企业（最常见） |
| **EAP-TTLS** | 任意（可多因素） | 必须 | 不需要 | 中 | 需要灵活内层认证 |
| **EAP-FAST** | 用户名/密码 + PAC | 可选 | PAC 文件 | 中 | Cisco 遗留环境 |
| **TEAP** | 证书 + 密码（链式） | 必须 | 可选 | 强 | 需要"机器 + 用户"双重认证 |

</div>

> ⚠️ **The most classic PEAP misconfiguration**: the client has **not ticked "validate server certificate" or has no trusted CA configured**, so any phishing AP with a spoofed SSID can harvest the user's domain credentials. That is not an AP problem, it is a **client configuration baseline** problem — the design document must list "endpoint 802.1X configuration baseline (server certificate validation, CA trust chain, SSID whitelist)" as a deliverable.

<div class="zh" markdown="1">

> ⚠️ **PEAP 最经典的配置错误**：客户端**没有勾选"验证服务器证书"或没有指定信任的 CA**，于是任何伪造 SSID 的钓鱼 AP 都能骗到用户的域凭据。这不是无线设备的问题，是**终端配置基线**的问题 —— 设计文档里必须把"终端 802.1X 配置基线（含服务端证书校验、CA 信任链、SSID 白名单）"写成交付项。

</div>

### Design Points on the RADIUS Side · RADIUS 侧的设计要点

| Point | Practice | Risk |
|------|------|------|
| **Redundancy** | At least two RADIUS servers (ISE nodes/cluster); configure multiple RADIUS servers on the WLC | One RADIUS failure = all new associations across the network fail |
| **Shared secrets** | Strong secrets, rotated periodically, **a distinct secret per device** | One network-wide secret leaks everywhere at once |
| **CoA (RFC 5176)** | Support dynamic authorisation changes (VLAN/ACL change, re-authentication) | Without CoA, policy changes require the user to reconnect |
| **Accounting** | Record Start/Interim/Stop | Without accounting you cannot audit or analyse capacity |
| **Latency budget** | RADIUS round trip < 200 ms (ideally < 100 ms) | Authentication across a WAN causes association timeouts |
| **Attribute design** | Use Tunnel-Type/Private-Group-ID to assign the dynamic VLAN | A wrong attribute lands the client in the wrong VLAN while "still connecting" |
| **Certificate validity** | Put it under monitoring (expired EAP certificates are a classic "everyone suddenly cannot connect") | A network-wide outage on the expiry date |

<div class="zh" markdown="1">

| 要点 | 做法 | 风险 |
|------|------|------|
| **冗余** | 至少两台 RADIUS（ISE 节点/集群），WLC 上配多个 RADIUS server | 单台 RADIUS 故障 = 全网新关联失败 |
| **共享密钥** | 强密钥 + 定期轮换，**每台设备独立密钥** | 全网一个密钥，泄露即全泄 |
| **CoA（RFC 5176）** | 支持动态改授权（改 VLAN/ACL/重认证） | 不支持 CoA 则策略变更需用户重连 |
| **计费（Accounting）** | 记录 Start/Interim/Stop | 缺计费无法做审计与容量分析 |
| **时延预算** | RADIUS 往返 < 200 ms（理想 < 100 ms） | 跨广域网认证导致关联超时 |
| **属性设计** | 用 Tunnel-Type/Private-Group-ID 下发动态 VLAN | 属性写错 → 客户端进错 VLAN 却"能连上" |
| **证书有效期** | 纳入监控（EAP 证书过期是"突然全部连不上"的经典原因） | 到期当天全网故障 |

</div>

### The PSK Scaling Problem and Its Alternatives · PSK 的规模问题与替代方案

In an enterprise, WPA2-PSK inevitably degrades into "the key circulating in the ex-employee group chat". Three alternatives:

<div class="zh" markdown="1">

WPA2-PSK 在企业里几乎必然演变成"密钥在离职群里流传"。三种替代：

</div>

| Option | Mechanism | Scale | Cost |
|------|------|------|------|
| **iPSK / dPSK (per-device PSK)** | One PSK per device, mapped to different VLANs/ACLs | Hundreds to thousands | Requires WLC support + a device onboarding process |
| **PPSK + portal** | Users self-register and receive a personal PSK | Thousands (guests/contractors) | Needs a portal/cloud service |
| **Move to 802.1X** | Per-user credentials | Unlimited | IoT devices often do not support 802.1X |

<div class="zh" markdown="1">

| 方案 | 机制 | 规模 | 代价 |
|------|------|------|------|
| **iPSK / dPSK（每设备 PSK）** | 每台设备一个 PSK，映射到不同 VLAN/ACL | 数百到数千 | 需要 WLC 支持 + 设备注册流程 |
| **PPSK + Portal** | 用户自助注册获取专属 PSK | 数千（访客/承包商） | 需 Portal/云服务 |
| **改用 802.1X** | 用户级凭据 | 无限 | IoT 设备常不支持 802.1X |

</div>

**The realistic choice for IoT**: a large share of IoT (printers, cameras, tags, medical devices) only supports WPA2-PSK. The standard practice is to give IoT **its own SSID + a separate VLAN + iPSK**, then use ACLs/firewalls to isolate it so it "can only reach the specified servers". Putting IoT on the employee SSID is the most common hole in a zero-trust architecture.

<div class="zh" markdown="1">

**IoT 的现实选择**：大量 IoT（打印机、摄像头、标签、医疗设备）只支持 WPA2-PSK。标准做法是**为 IoT 单开一个 SSID + 独立 VLAN + iPSK**，再用 ACL/防火墙把它隔离到"只能访问指定服务器"。把 IoT 塞进员工 SSID 是零信任架构里最常见的一处破口。

</div>

### The Three Modes of WPA3 · WPA3 的三个模式

| Mode | Characteristics | Explanation | Migration note |
|------|------|------|---------|
| **WPA3-Personal (SAE)** | Peer authentication (Dragonfly handshake), forward secrecy | Even knowing the password does not decrypt past traffic; resists offline brute force | Old endpoints do not support it → needs **WPA2/WPA3 transition mode** |
| **WPA3-Enterprise (192-bit)** | GCMP-256 + SHA-384 + 384-bit ECDHE/ECDSA | Government/financial compliance requirement | Very few endpoints support it; usually a dedicated SSID |
| **OWE (Opportunistic Wireless Encryption)** | Open network with automatic encryption (no authentication) | Guest "passwordless but encrypted" | Used together with a portal |

<div class="zh" markdown="1">

| 模式 | 特性 | 说明 | 迁移注意 |
|------|------|------|---------|
| **WPA3-Personal（SAE）** | 对等认证（Dragonfly 握手），前向保密 | 即使知道密码，也无法解密历史流量；抗离线爆破 | 老终端不支持 → 需**WPA2/WPA3 过渡模式** |
| **WPA3-Enterprise（192 位）** | GCMP-256 + SHA-384 + 384 位 ECDHE/ECDSA | 政府/金融合规要求 | 极少数终端支持，通常单开 SSID |
| **OWE（Opportunistic Wireless Encryption）** | 开放网络自动加密（无认证） | 访客网"无密码但加密" | 与 Portal 配合使用 |

</div>

**Mandatory companions**:

<div class="zh" markdown="1">

**配套的强制项**：

</div>

- **PMF (802.11w, management frame protection)**: mandatory with WPA3, it prevents **deauthentication attacks (deauth floods)**. Under WPA2 it could be "optional/required"; under WPA3 it must be "required".
- **6 GHz mandates WPA3 + PMF**: that is a regulatory requirement for 6 GHz and one of the technical reasons "old endpoints cannot see 6 GHz SSIDs".

<div class="zh" markdown="1">

- **PMF（802.11w，管理帧保护）**：WPA3 强制开启，防**去认证攻击（deauth flood）**。WPA2 时代可设"可选/必需"，WPA3 必须"必需"。
- **6 GHz 强制 WPA3 + PMF**：这是 6 GHz 的法规性要求，也是"老终端看不到 6 GHz SSID"的技术原因之一。

</div>

### Guest Network Design: Four Models · 访客网络设计：四种模型

| Model | Approach | Isolation strength | Where it fits |
|------|------|---------|------|
| **Local breakout (recommended)** | Guest SSID maps straight to a DMZ VLAN and exits to the internet locally | High (never touches the internal network) | Branches with a local internet exit |
| **Guest Anchor (central tunnel)** | Guest traffic is tunnelled back to an anchor WLC in the DMZ | High | Centralized management, unified portal |
| **PPSK + firewall** | One PSK per guest, pointing at an isolated VLAN | Medium | No portal infrastructure |
| **Portal + SMS/WeChat authentication** | Traffic is only released after portal authentication | Medium (needed for compliance auditing) | Malls, hotels, public venues |

<div class="zh" markdown="1">

| 模型 | 做法 | 隔离强度 | 适用 |
|------|------|---------|------|
| **本地 breakout（推荐）** | 访客 SSID 直接映射到 DMZ VLAN，本地出互联网 | 高（不碰内网） | 分支、有本地互联网出口 |
| **Guest Anchor（集中隧道）** | 访客流量隧道回 DMZ 的 Anchor WLC | 高 | 集中管理、统一 Portal |
| **PPSK + 防火墙** | 每访客一个 PSK，指向隔离 VLAN | 中 | 无 Portal 基础设施 |
| **Portal + 短信/微信认证** | 强制 Portal 认证后再放行 | 中（合规审计需要） | 商场、酒店、公共场所 |

</div>

**The six hard requirements for guest networks (to write into the design document)**:

<div class="zh" markdown="1">

**访客网的六条硬要求（写进设计文档）**：

</div>

1. **Layer 2 isolation** (`peer-to-peer blocking` or AP isolation) so guests cannot scan each other
2. **Internet only**; no access to any internal subnet (including management subnets)
3. **Separate DNS** (public DNS or a DMZ resolver)
4. **Rate limiting** (per-client up/down) so one user cannot consume the whole radio's airtime
5. **Multicast/broadcast flooding suppressed** (`multicast/broadcast suppression`)
6. **Session timeouts + log retention** (compliance usually requires six months)

<div class="zh" markdown="1">

1. **二层隔离**（`peer-to-peer blocking` 或 AP 隔离），防访客互扫
2. **只能到互联网**，禁止访问内网任意网段（含管理网段）
3. **独立 DNS**（可用公共 DNS 或 DMZ 解析器）
4. **限速**（每客户端上下行），防单用户占满 airtime
5. **禁止组播/广播泛洪**（`multicast/broadcast suppression`）
6. **会话超时 + 日志留存**（合规要求通常 6 个月）

</div>

### Wireless Threat Model (list the threats first, then talk about configuration) · 无线威胁模型（先列威胁，再谈配置）

| Threat | Mechanism | Impact | Countermeasure |
|---|---|---|---|
| **Evil twin (phishing AP)** | Spoofs an SSID with the same name, relaying or phishing | Domain credential theft | Mandatory server certificate validation + CA trust chain + SSID whitelist; wIPS detection; endpoint baseline |
| **Deauth flood** | Forged disassociation frames kick users offline | Denial of service / pairs with phishing | **PMF (802.11w) is mandatory** |
| **KRACK (key reinstallation)** | Replays the third frame of the four-way handshake | Traffic decryption | Patch clients/APs; WPA3 is immune by design |
| **PMKID / offline handshake cracking** | Capture the handshake and guess the PSK offline | PSK disclosure | Move to 802.1X; PSK of at least 20 random characters; iPSK |
| **SAE downgrade attack** | Coaxes WPA3 back down to WPA2 | Loss of forward secrecy | Disable "WPA2/WPA3 mixed" (6 GHz-only already enforces WPA3) |
| **Rogue AP / unauthorised home router** | An employee plugs in a home router | Bypasses the security boundary, DHCP conflicts | Switch port security + wIPS + wired-side correlation and location |
| **Ad-hoc / hotspot sharing** | A phone hotspot bridges the internal network out | Data exfiltration | Policy prohibition + MDM + detection alerts |
| **Portal bypass** | Crafting raw IP traffic to skip authentication | Guest policy defeated | Couple the portal with gateway ACLs (the unauthenticated VLAN reaches only the portal) |
| **Exposed management plane** | Controller GUI reachable from the internet | Compromise | Management VLAN + ACL + two-factor + no public reachability |

<div class="zh" markdown="1">

| 威胁 | 机制 | 影响 | 对策 |
|---|---|---|---|
| **Evil Twin（钓鱼 AP）** | 伪造同名 SSID 诱导连接，中继或钓鱼 | 窃取域凭据 | 强制服务端证书校验 + CA 信任链 + SSID 白名单；wIPS 检测；终端基线 |
| **Deauth 洪泛** | 伪造断开帧踢用户下线 | 拒绝服务 / 配合钓鱼 | **PMF（802.11w）必需** |
| **KRACK（密钥重装）** | 重放 4 次握手第 3 帧 | 解密流量 | 客户端/AP 补丁；WPA3 天然免疫 |
| **PMKID / 握手离线爆破** | 抓取握手包离线猜 PSK | PSK 泄露 | 改用 802.1X；PSK 至少 20 字符随机；iPSK |
| **SAE 降级攻击** | 诱导 WPA3 回落到 WPA2 | 失去前向保密 | 关闭"WPA2/WPA3 混合"（纯 6 GHz 场景本已强制 WPA3） |
| **Rogue AP / 私接路由** | 员工私接家用路由器 | 绕过安全边界、DHCP 冲突 | 交换机端口安全 + wIPS + 有线侧联动定位 |
| **Ad-hoc / 热点共享** | 手机开热点把内网桥出 | 数据外泄 | 策略禁止 + 终端管控（MDM）+ 检测告警 |
| **Portal 绕过** | 直接构造 IP 流量跳过认证 | 访客策略失效 | Portal 与网关 ACL 联动（未认证 VLAN 仅放行 Portal） |
| **管理面暴露** | 控制器管理界面暴露在互联网 | 被入侵 | 管理 VLAN + ACL + 双因素 + 禁公网可达 |

</div>

> ⚠️ **The knock-on effect of PMF**: once PMF is required, some older endpoints (especially pre-2014 devices and certain IoT modules) **cannot associate**. Stacked on the WPA3 compatibility problem, this is why "security upgrades" must always be **per SSID + phased + field tested**; there is no one-shot cutover.

<div class="zh" markdown="1">

> ⚠️ **PMF 的连带影响**：开启 PMF 必需后，部分老终端（尤其 2014 年前的设备、某些 IoT 模块）**无法关联**。这与 WPA3 的兼容性问题叠加，所以"安全升级"永远是**分 SSID + 分批 + 实测**，不可能一次切换。

</div>

### 802.1X Timing Parameters and Timeouts (misconfigure them and you get "random connection failures") · 1X 的时间参数与超时（配错了就是"随机连不上"）

| Parameter | Common default | Flaw | Recommendation |
|---|---|---|---|
| **WLC RADIUS timeout** | 5 s, 3 retries | Too short → false timeouts under load; too long → users wait | 2–3 s × 2 retries, plus multiple servers |
| **RADIUS dead-time** | 5–10 min (or 0 = disabled) | If disabled, one dead RADIUS server keeps failing half the requests | Enable dead-time (1–2 min) with failover |
| **EAP retransmission timeout** | 30 s | The session stays occupied after the client has given up | Tune from field measurements |
| **Client re-authentication (Session Timeout)** | 8–24 h | Too short → constant re-auth drops; none → no reclamation | 8 h (use CoA for policy changes) |
| **Accounting Interim** | 5–10 min | No accounting → no audit and no capacity analysis | 10 min |
| **RADIUS latency budget** | — | Authentication across a WAN > 500 ms feels slow | < 200 ms, worst case < 500 ms |

<div class="zh" markdown="1">

| 参数 | 常见默认 | 缺陷 | 建议 |
|---|---|---|---|
| **WLC 侧 RADIUS 超时** | 5 s，重试 3 次 | 太短 → 高负载时假超时；太长 → 用户干等 | 2–3 s × 2 次，并配多台 server |
| **RADIUS dead-time** | 5–10 min（或 0=禁用） | 禁用后：一台 RADIUS 挂了，一半请求持续失败 | 启用 dead-time（1–2 min），并配 fallback |
| **EAP 重传超时** | 30 s | 客户端放弃后仍占着会话 | 按终端实测调整 |
| **客户端重认证周期（Session Timeout）** | 8–24 h | 太短 → 频繁重认证导致掉线；无 → 无法回收 | 8 h（配合 CoA 做策略变更） |
| **Accounting Interim** | 5–10 min | 无计费 → 无法审计与容量分析 | 10 min |
| **RADIUS 时延预算** | — | 跨 WAN 认证 > 500 ms 就明显慢 | < 200 ms，最差 < 500 ms |

</div>

**Three typical causes of "random connection failures"**:

<div class="zh" markdown="1">

**典型的"随机连不上"三种成因**：

</div>

1. RADIUS **dead-time not enabled**, so after one node fails half the clients keep failing (it looks like "some people cannot connect", but really it means "the people pointed at that one server fail");
2. RADIUS **certificate/shared secret expired or a rotation not synced** (the secret was changed on one side only);
3. Controller **session timeout inconsistent with CoA configuration**, concentrating re-authentications just before and after the hour (micro-bursts).

<div class="zh" markdown="1">

1. RADIUS **dead-time 未启用**，一台节点故障后一半客户端持续失败（看似"部分人连不上"，实际是"连到某台 server 的人失败"）；
2. RADIUS **证书/共享密钥过期或轮换未同步**（换了密钥但只改了一侧）；
3. 控制器 **session timeout 与 CoA 配置不一致**，导致重认证集中在整点前后（微突发）。

</div>

### Dynamic Policy Assignment: One SSID Serving the Whole Company · 动态策略下发：一个 SSID 服务全公司

Using RADIUS return attributes to steer users of the **same SSID** into different VLANs/ACLs is the correct alternative to "many SSIDs" (because multiple SSIDs cost Beacons — see introduction item #9).

<div class="zh" markdown="1">

用 RADIUS 返回的属性把"同一个 SSID"的用户分流到不同 VLAN/ACL，是替代"多 SSID"的正确做法（因为多 SSID 有 Beacon 成本，见导读 #9）。

</div>

| What is pushed | Attribute/mechanism | Effect |
|---|---|---|
| **Dynamic VLAN** | `Tunnel-Type=VLAN`, `Tunnel-Medium-Type=802`, `Tunnel-Private-Group-ID=<vlan>` | Employees/contractors/devices land in different VLANs |
| **Dynamic ACL** | `Filter-Id` / `Airespace-ACL-Name` | Differentiation inside one VLAN (e.g. only ERP access) |
| **SGT (TrustSec)** | `cts:security-group-tag` | Assign a security group tag on the wireless side and use SGACLs for micro-segmentation |
| **QoS role** | Vendor proprietary attributes | Voice clients automatically land in Platinum |
| **Session timeout/bandwidth** | `Session-Timeout`, `WLAN-*` attributes | Rate limits per role |

<div class="zh" markdown="1">

| 下发内容 | 属性/机制 | 效果 |
|---|---|---|
| **动态 VLAN** | `Tunnel-Type=VLAN`、`Tunnel-Medium-Type=802`、`Tunnel-Private-Group-ID=<vlan>` | 员工/承包商/设备各进不同 VLAN |
| **动态 ACL** | `Filter-Id` / `Airespace-ACL-Name` | 同一 VLAN 内也能差异化（如只允许访问 ERP） |
| **SGT（TrustSec）** | `cts:security-group-tag` | 无线侧直接赋予安全组标签，配合 SGACL 做微隔离 |
| **QoS 角色** | 厂商私有属性 | 语音客户端自动进 Platinum |
| **会话超时/带宽** | `Session-Timeout`、`WLAN-*` 属性 | 按角色限速 |

</div>

> 💡 **The one-sentence design argument**: **"the SSID is a broadcast resource; the role is an authentication result"**. Anything you can differentiate with RADIUS attributes should never be differentiated with a new SSID.

<div class="zh" markdown="1">

> 💡 **设计上的一句话论证**：**"SSID 是广播资源，角色是认证结果"**。凡是能用 RADIUS 属性区分的，都不要用新 SSID 区分。

</div>

### Wireless IPS and Rogue AP Protection · 无线 IPS 与非法 AP 防护

| Capability | Explanation | How to implement |
|------|------|---------|
| **Rogue AP detection** | Finds unauthorised APs "plugged into the same wired network" | AP scanning + switch-side MAC/port correlation (wired-side correlation) |
| **Rogue containment** | Sends deauth to the rogue AP (legal and collateral-damage risk) | Find the port on the switch and shut it down first (safer) |
| **Ad-hoc / hotspot detection** | Clients creating their own hotspots (employee tethering) | Policy prohibition + detection alerts |
| **Deauth attack detection** | Abnormal volumes of management frames | 802.11w/PMF + wIPS alerts |
| **Spectrum attack detection** | Interference sources (microwaves, wireless cameras) | CleanAir / spectrum analysis |
| **Client anomaly behaviour** | Excessive probing, abnormal DHCP | wIPS + NetFlow |

<div class="zh" markdown="1">

| 能力 | 说明 | 落地方式 |
|------|------|---------|
| **Rogue AP 检测** | 发现"连在同一有线网上的非法 AP" | AP 扫描 + 交换机侧 MAC/端口关联（有线侧联动） |
| **Rogue 抑制** | 对非法 AP 发 deauth（有法律与误伤风险） | 必须先在交换机侧找到端口并 shutdown（更安全） |
| **Ad-hoc / Hotspot 检测** | 客户端自建热点（员工私接） | 策略禁止 + 检测告警 |
| **Deauth 攻击检测** | 大量管理帧异常 | 802.11w/PMF + wIPS 告警 |
| **频谱攻击检测** | 干扰源（微波、无线摄像头） | CleanAir / 频谱分析 |
| **客户端异常行为** | 大量探测、异常 DHCP | wIPS + NetFlow |

</div>

> 💡 **The correct order for rogue containment**: **locate the wired port → shut down / isolate the port on the switch → only then consider over-the-air containment**. Sending deauth over the air indiscriminately hits neighbouring legitimate clients and may violate local radio regulations.

<div class="zh" markdown="1">

> 💡 **Rogue 抑制的正确顺序**：**先定位有线端口 → 交换机上 shutdown / 端口隔离 → 再考虑空口抑制**。直接在空口发 deauth 会误伤邻近合法客户端，还可能违反当地无线电管理规定。

</div>

### Wireless Segmentation for IoT and OT · IoT 与 OT 的无线分段

IoT is the part of wireless security most often sacrificed: devices do not support 802.1X, firmware cannot be upgraded, MAC randomization does not apply, vendors ship default passwords. **The conclusion is: do not try to "protect the devices", try to "isolate the devices"**.

<div class="zh" markdown="1">

IoT 是无线安全里最容易被牺牲的一环：设备不支持 802.1X、固件不能升级、MAC 随机化不适用、厂商默认密码。**结论是：不要试图"保护设备"，而要"隔离设备"**。

</div>

| Design element | Practice | Reason |
|---|---|---|
| **Separate SSID + separate VLAN** | One per class of IoT (or per vendor/purpose) | Keeps the blast radius small; also simplifies rate limiting and auditing |
| **Authentication** | iPSK/dPSK (per-device key) beats a shared PSK | One leaked device does not compromise everyone; per-device revocation |
| **Layer 2 isolation** | AP isolation + client isolation | Stops IoT lateral scanning (the main ransomware path) |
| **Egress whitelist** | Allow only the specified servers (MQTT/HTTPS/vendor cloud) | Default deny; implemented with firewall/ACL |
| **Rate limits and session caps** | 256 kbps–1 Mbps per device, connection count limited | Stops one compromised device from saturating airtime |
| **2.4 GHz dedicated** | Do not push IoT to 5/6 GHz | Many IoT devices are 2.4 GHz only |
| **Disable 11r/11v** | IoT has terrible FT compatibility | Avoids "everything dropped after enabling 11r" |

<div class="zh" markdown="1">

| 设计要素 | 做法 | 原因 |
|---|---|---|
| **独立 SSID + 独立 VLAN** | 每类 IoT 一个（或按厂商/用途） | 爆炸半径可控；也便于限速与审计 |
| **认证** | iPSK/dPSK（每设备密钥）优于共享 PSK | 单设备泄露不影响全员；可按设备回收 |
| **二层隔离** | AP 隔离 + 客户端隔离 | 阻止 IoT 横向扫描（这是勒索软件的主要路径） |
| **出口白名单** | 只允许访问指定服务器（MQTT/HTTPS/厂商云） | 默认拒绝；用防火墙/ACL 实现 |
| **限速与 session 上限** | 每设备 256 kbps–1 Mbps，限制连接数 | 防一台被入侵的设备打满 airtime |
| **2.4 GHz 专用** | 不要把 IoT 推到 5/6 GHz | 大量 IoT 只支持 2.4 GHz |
| **关闭 11r/11v** | IoT 对 FT 兼容性极差 | 避免"开了 11r 后 IoT 全掉" |

</div>

**Additional requirements for medical/industrial OT**:

<div class="zh" markdown="1">

**医疗/工业 OT 的额外要求**：

</div>

- **Vendor acceptance testing**: new medical devices must pass a 72-hour stability test on an isolated SSID before go-live (many devices have flawed roaming implementations);
- **Roaming behaviour validation**: infusion pumps and monitors must stay connected while being wheeled around, so every model must be measured;
- **Never share an SSID**: mixing "medical telemetry" and "employee internet" on one SSID is the most common hospital wireless design error (both an airtime and a security risk).

<div class="zh" markdown="1">

- **供应商准入测试**：新医疗设备上线前必须在隔离 SSID 上做 72 h 稳定性测试（很多设备的漫游实现有缺陷）；
- **漫游行为验证**：输液泵、监护仪在推床移动时必须保持连接，需实测每个型号；
- **不共用 SSID**：把"医疗遥测"和"员工上网"混在一个 SSID，是医院无线最常见的设计错误（airtime 与安全双重风险）。

</div>

### mDNS / Bonjour Across VLANs: Why Screen Mirroring "Sometimes Finds the Device" (and sometimes not) · mDNS / Bonjour 跨 VLAN：投屏为什么"有时候能找到"（有时候不能）

Wireless screen mirroring (AirPlay, Google Cast, Miracast), printer discovery and Apple TV all depend on **mDNS (224.0.0.251:5353)**, and mDNS is **link-local multicast that does not cross subnets**.

<div class="zh" markdown="1">

无线投屏（AirPlay、Google Cast、MiraCast）、打印机发现、Apple TV 全部依赖 **mDNS（224.0.0.251:5353）**，而 mDNS 是**链路本地组播，不跨子网**。

</div>

| Symptom | Cause | Countermeasure |
|---|---|---|
| Mirroring works inside one VLAN but not across VLANs | mDNS does not cross Layer 3 | Deploy an **mDNS gateway/reflector** (Cisco mDNS Gateway, Avahi reflector, Bonjour Gateway) |
| Intermittent behaviour | mDNS flooding affected by multicast suppression or multicast-to-unicast conversion | Keep a service cache (Service Directory) at the gateway instead of relying on over-the-air multicast flooding |
| Mirroring stutters or shows artefacts | Mirroring is **high-bitrate uplink plus a multicast/unicast mix** | Have the mirroring gateway convert streams to unicast; keep source and display in the same AP/VLAN |
| Wi-Fi slows down when the whole room mirrors | Multicast/broadcast flooding + high-bitrate uplink | Cap the bitrate per mirroring session; dedicated AP per meeting room |

<div class="zh" markdown="1">

| 现象 | 原因 | 对策 |
|---|---|---|
| 同一 VLAN 能投屏，跨 VLAN 找不到设备 | mDNS 不跨三层 | 部署 **mDNS 网关/反射器**（如 Cisco mDNS Gateway、Avahi reflector、Bonjour Gateway） |
| 时好时坏 | mDNS 泛洪被组播抑制/无线组播转单播影响 | 在网关侧做服务缓存（Service Directory），不要依赖空口组播泛洪 |
| 投屏卡顿、花屏 | 投屏是**高码率上行 + 组播/单播混合** | 投屏网关把流改单播；把投屏设备与显示端放在同 AP/同 VLAN |
| 全场都在投屏时 Wi-Fi 变慢 | 多播/广播泛洪 + 高码率上行 | 限制每组投屏的码率；会议室单独 AP |

</div>

> ⚠️ **Screen mirroring is the most underestimated load in wireless design**: a single 1080p mirroring session is a sustained 4–8 Mbps uplink and is jitter-sensitive. Meeting rooms must be designed as "at least one AP per room + uplink headroom", not "sized by headcount".

<div class="zh" markdown="1">

> ⚠️ **投屏是无线设计里最容易被低估的负载**：一次 1080p 投屏的上行是 4–8 Mbps 持续流，且对抖动敏感。会议室设计必须按"每间至少 1 个 AP + 上行余量"考虑，而不是"按人数算"。

</div>

### Wireless Through a Compliance Lens (local regulatory baseline / PCI-DSS / HIPAA) · 合规视角的无线（等保 / PCI-DSS / HIPAA）

| Requirement | Direction of the clause | How the design satisfies it |
|---|---|---|
| **Strong encryption** | WEP/WPA prohibited; AES required | Start from WPA2-Enterprise; WPA3 for new builds |
| **Identity verification** | A unique credential per person | 802.1X + RADIUS (never share a PSK with employees) |
| **Guest isolation** | Guests isolated from the business network | Separate VLAN + firewall + internet only |
| **Log retention** | Usually ≥ 6 months | RADIUS Accounting + controller syslog + web activity logs |
| **Wireless scanning (PCI)** | Quarterly rogue AP scans | wIPS + periodic reports (can be auto-exported) |
| **Key management** | Shared keys rotated, need-to-know only | iPSK/802.1X instead of a shared PSK |
| **Change auditing** | Configuration changes traceable | Config backups + change tickets + version comparison |

<div class="zh" markdown="1">

| 要求 | 具体条款方向 | 设计落地 |
|---|---|---|
| **强加密** | 禁止 WEP/WPA；要求 AES | WPA2-Enterprise 起步，新项目 WPA3 |
| **身份鉴别** | 每人唯一凭据 | 802.1X + RADIUS（禁止共享 PSK 给员工） |
| **访客隔离** | 访客与业务网隔离 | 独立 VLAN + 防火墙 + 仅互联网 |
| **日志留存** | 通常 ≥ 6 个月 | RADIUS Accounting + 控制器 syslog + 上网行为日志 |
| **无线扫描（PCI）** | 季度 rogue AP 扫描 | wIPS + 定期报告（可自动导出） |
| **密钥管理** | 共享密钥定期更换、最小知悉 | iPSK/802.1X 替代共享 PSK |
| **变更审计** | 配置变更可追溯 | 配置备份 + 变更工单 + 版本对比 |

</div>

### Wireless Security Hardening Baseline (an implementation checklist to tick off item by item) · 无线安全加固基线（实施检查表，逐项打勾）

```
□ Disable WEP / WPA1 / TKIP; disable WPA2-PSK (at least on the employee side)
□ Employee SSID: WPA3-Enterprise or WPA2-Enterprise + EAP-TLS/PEAP + mandatory server cert validation
□ Enable PMF (802.11w); separate SSID for voice/OEM devices as a compatibility fallback
□ Turn off unnecessary SSIDs; total SSIDs ≤ 4 (Beacon cost)
□ Do not treat hidden SSIDs as a security control (they are not one)
□ Guest: OWE or portal + Layer 2 isolation + internet only + rate limit + logging
□ IoT: separate SSID + iPSK + egress whitelist + client isolation
□ Management plane: separate management VLAN + source-restricted ACL + AAA + two-factor + no public exposure
□ Disable unused services: Telnet, HTTP, SNMPv1/v2c, weak AP console passwords
□ Enable wIPS; configure rogue detection alerts; export scan reports periodically
□ RADIUS: multiple nodes + dead-time + distinct shared secrets + certificate monitoring (alert ≥ 60 days ahead)
□ 802.1X: session timeout 8 h + CoA support + accounting enabled
□ Firmware: APSP matched to the WLC release; maintain an EOL register
□ Config backup: export controller configuration daily; every change has a ticket and a rollback plan
□ Periodic penetration testing: at least once a year on the wireless side (including phishing AP and deauth tests)
```

<div class="zh" markdown="1">

```
□ 禁用 WEP / WPA1 / TKIP；禁用 WPA2-PSK（至少员工侧）
□ 员工 SSID：WPA3-Enterprise 或 WPA2-Enterprise + EAP-TLS/PEAP + 强制服务端证书校验
□ 开启 PMF（802.11w）；语音/OEM 设备单独 SSID 做兼容性回退
□ 关闭不必要的 SSID；SSID 总数 ≤ 4（Beacon 成本）
□ 隐藏 SSID 不当作安全手段（它不是）
□ 访客：OWE 或 Portal + 二层隔离 + 仅互联网 + 限速 + 日志
□ IoT：独立 SSID + iPSK + 出口白名单 + 客户端隔离
□ 管理面：独立管理 VLAN + ACL 限制源 + AAA + 双因素 + 禁公网
□ 关闭未使用的服务：Telnet、HTTP、SNMPv1/v2c、AP console 弱口令
□ 开启 wIPS；配置 rogue 检测告警；定期导出扫描报告
□ RADIUS：多节点 + dead-time + 独立共享密钥 + 证书监控（到期告警 ≥ 60 天）
□ 802.1X：session timeout 8h + CoA 支持 + Accounting 开启
□ 固件：APSP 与 WLC 版本匹配；建立 EOL 台账
□ 配置备份：控制器配置每日导出；变更有工单与回滚方案
□ 定期渗透测试：至少每年一次无线侧（含钓鱼 AP 与 deauth 测试）
```

</div>

---

## High-Density Design · 高密度设计

### What "High Density" Actually Means · 什么叫"高密度"

High density is not "lots of APs"; it is **airtime demand per unit area exceeding what the spectrum can supply**. The judgement rests on a combination of three numbers:

<div class="zh" markdown="1">

高密度不是"AP 装得多"，而是**单位面积内的 airtime 需求超过频谱能提供的总量**。判断依据是三个数的组合：

</div>

| Metric | Normal office | High density | Extreme density |
|------|---------|--------|---------|
| **Concurrent clients / 100 m²** | 3–8 | 15–30 | 30–60+ |
| **AP spacing** | 15–25 m | 8–15 m | 5–10 m |
| **Peak airtime utilisation** | < 30% | 40–60% | **> 60% (already degrading)** |
| **Typical venue** | Open office | Lecture theatres, meeting-room clusters | Stadiums, concerts, large launch events, hospital outpatient |

<div class="zh" markdown="1">

| 指标 | 普通办公 | 高密度 | 极高密度 |
|------|---------|--------|---------|
| **并发客户端 / 100 m²** | 3–8 | 15–30 | 30–60+ |
| **AP 间距** | 15–25 m | 8–15 m | 5–10 m |
| **峰值 airtime 利用率** | < 30% | 40–60% | **> 60%（已进入劣化区）** |
| **典型场所** | 开放办公 | 阶梯教室、会议室群 | 体育馆、演唱会、大型发布会、医院门诊 |

</div>

> ⚠️ **Once airtime utilisation sits above 60%, user experience degrades non-linearly** — rising retry rates consume even more airtime, creating positive feedback. That threshold is both a design red line and an acceptance metric.

<div class="zh" markdown="1">

> ⚠️ **airtime 利用率一旦稳定超过 60%，用户体验会非线性下降** —— 因为重传率上升会进一步消耗 airtime，形成正反馈。这个阈值是设计红线，也是验收指标。

</div>

### The Quantitative High-Density Workflow (with a worked example) · 高密度设计的量化流程（带算例）

**Scenario**: a 300-seat lecture theatre, students mostly on laptops/phones watching courseware and video, 80% peak concurrency, 3 Mbps required per client.

<div class="zh" markdown="1">

**场景**：一个 300 人的阶梯教室，学生普遍用笔记本/手机看课件与视频，峰值并发率 80%，每客户端需求 3 Mbps。

</div>

```
① Concurrent clients = 300 × 80% = 240
② Total throughput demand = 240 × 3 Mbps = 720 Mbps
③ Effective throughput per AP (5 GHz 20 MHz, 2SS, 11ax) = about 160 Mbps
④ Conservatively 70% of airtime usable = 112 Mbps
⑤ APs needed = 720 / 112 ≈ 6.4 → round up to 7
⑥ Load per AP ≈ 34 clients → inside the healthy 30–40 range
⑦ Spectrum check: 5 GHz 20 MHz offers 25 channels, 7 APs need no reuse → safe
```

<div class="zh" markdown="1">

```
① 并发客户端 = 300 × 80% = 240
② 总吞吐需求 = 240 × 3 Mbps = 720 Mbps
③ 单 AP 有效吞吐（5 GHz 20 MHz, 2SS, 11ax）= 约 160 Mbps
④ 保守按 70% airtime 可用 = 112 Mbps
⑤ 需要的 AP 数 = 720 / 112 ≈ 6.4 → 取 7 台
⑥ 每 AP 承载 ≈ 34 客户端 → 在 30–40 的健康区间内
⑦ 频谱检查：5 GHz 20 MHz 有 25 个信道，7 台 AP 无需复用 → 可放心
```

</div>

**If 80 MHz had been chosen by mistake here**: per-AP rate rises (about 500 Mbps), but usable channels drop to 6, so 7 APs must reuse — **co-channel interference halves real throughput**, and the wider channel makes adjacent APs overlap → the outcome is usually worse than 20 MHz. **This is the most counter-intuitive and most frequently made error in high-density design.**

<div class="zh" markdown="1">

**如果这里错误地选了 80 MHz**：单 AP 速率上升（约 500 Mbps），但可用信道降到 6 个，7 台 AP 必然复用，**同频干扰（CCI）导致实际吞吐腰斩**，同时信道宽度使相邻 AP 重叠 → 最终结果往往比 20 MHz 更差。**这是高密度设计里最反直觉、也最常犯的错误。**

</div>

### High-Density Technology Matrix · 高密度关键技术矩阵

| Technology | What it solves | Preconditions | Effect |
|------|---------|---------|------|
| **20 MHz channels** | Spectrum reuse and CCI | None (always available) | ★★★★★ best value for effort |
| **Lower transmit power (5–8 dBm)** | Smaller coverage radius, more and smaller cells | Must be paired with power planning | ★★★★★ |
| **MIN RSSI (forced disconnect)** | Evicts weak-signal sticky clients | Around −67 dBm | ★★★★☆ |
| **Band Steering** | Pushes dual-band clients to 5/6 GHz | Works with MIN RSSI | ★★★★☆ |
| **OFDMA (Wi-Fi 6)** | Serves several small-frame clients in one transmission opportunity | Endpoints must also support 11ax | ★★★★☆ (dramatic for small frames) |
| **MU-MIMO (DL/UL)** | Transmit to several clients at once | Client antenna count, channel conditions | ★★★☆☆ |
| **BSS Coloring** | Same-channel AP frames can be sent "in parallel" | 11ax + both ends supporting it | ★★★★☆ |
| **TWT (target wake time)** | Scheduled IoT wake-ups reduce contention | Endpoint supports 11ax | ★★★☆☆ (★★★★★ for IoT) |
| **Airtime Fairness** | Stops slow clients from consuming all airtime | Enabled on the controller | ★★★★☆ |
| **Multicast-to-unicast / broadcast suppression** | Prevents low-rate multicast from crippling the network | Enabled on the controller | ★★★★☆ (critical for video/IPTV) |
| **Load balancing** | Steers clients toward idle APs | Client cooperation (some refuse) | ★★★☆☆ |
| **Disable low rates (1/2/5.5/11 Mbps)** | Raises the minimum modulation tier | Good coverage | ★★★★☆ |

<div class="zh" markdown="1">

| 技术 | 解决什么 | 生效条件 | 效果 |
|------|---------|---------|------|
| **20 MHz 信道** | 频谱复用与 CCI | 无（随时可做） | ★★★★★ 最高性价比 |
| **降低发射功率（5–8 dBm）** | 缩小覆盖半径，让"蜂窝"变小变多 | 必须配合功率规划 | ★★★★★ |
| **MIN RSSI（强制断开）** | 驱逐弱信号"粘滞客户端" | -67 dBm 左右 | ★★★★☆ |
| **Band Steering（频段引导）** | 把双频终端推向 5/6 GHz | 与 MIN RSSI 配合 | ★★★★☆ |
| **OFDMA（Wi-Fi 6）** | 一次传输机会服务多个小包终端 | 终端也支持 11ax | ★★★★☆（小包场景显著） |
| **MU-MIMO（DL/UL）** | 同时向多终端发送 | 终端天线数、信道条件 | ★★★☆☆ |
| **BSS Coloring** | 同频 AP 的帧可"并行发送" | 11ax + 双方支持 | ★★★★☆ |
| **TWT（目标唤醒时间）** | IoT 定时唤醒，减少竞争 | 终端支持 11ax | ★★★☆☆（IoT 场景 ★★★★★） |
| **Airtime Fairness** | 防止低速客户端占满 airtime | 控制器开启 | ★★★★☆ |
| **组播转单播 / 广播抑制** | 避免低速率组播拖垮全网 | 控制器开启 | ★★★★☆（视频/IPTV 关键） |
| **负载均衡（Load Balancing）** | 引导客户端到较空闲 AP | 客户端配合（部分终端拒绝） | ★★★☆☆ |
| **禁用低速率（1/2/5.5/11 Mbps）** | 抬高最小调制档位 | 覆盖良好 | ★★★★☆ |

</div>

### Power Design: Up/Downlink Asymmetry Is the Real Problem · 功率设计：上下行不对称才是真问题

A wireless link is bidirectional, yet **the AP's transmit power (usually up to 20 dBm) far exceeds the phone's (typically 14–15 dBm, capped by SAR)**. The common mistake is "run the AP at full power", with these results:

<div class="zh" markdown="1">

无线的链路是双向的，而**AP 的发射功率（通常可到 20 dBm）远大于手机（通常 14–15 dBm，且受 SAR 限制）**。常见的错误设计是"AP 满功率"，结果：

</div>

| Consequence | Mechanism |
|------|------|
| **Uplink coverage 5–8 dB smaller than downlink** | The client "hears" the AP but cannot "shout back", producing "full bars but slow uploads / stalls" |
| **Cells are too large** | One AP serves too many clients, so airtime is shared out thinly |
| **Roam points are terrible** | Clients only switch when the signal is already weak, destroying the roaming experience |
| **Severe CCI** | Adjacent APs hear each other, intensifying medium contention |

<div class="zh" markdown="1">

| 后果 | 机制 |
|------|------|
| **上行覆盖比下行小 5–8 dB** | 客户端"听到"AP 却"喊不到"AP，出现"信号满格但上传慢/断流" |
| **蜂窝过大** | 一台 AP 服务过多客户端，airtime 被均摊 |
| **漫游点太差** | 客户端直到信号极弱才切换，漫游体验崩坏 |
| **CCI 严重** | 相邻 AP 互相听到，介质竞争加剧 |

</div>

**Correct power/coverage design values**:

<div class="zh" markdown="1">

**正确的功率/覆盖设计值**：

</div>

| Parameter | Normal office | High density / voice |
|------|---------|-----------|
| **Cell-edge RSSI** | −67 dBm | −65 dBm |
| **SNR** | ≥ 25 dB | ≥ 25 dB (voice ≥ 25–30 dB) |
| **AP transmit power** | Automatic (RRM) or 11–14 dBm | **Manual/automatic floor 5–8 dBm** |
| **Adjacent coverage overlap** | 15%–20% | 15%–20% (with a difference ≤ 5 dB) |
| **Data rate floor** | 12 Mbps | 12–24 Mbps |

<div class="zh" markdown="1">

| 参数 | 普通办公 | 高密度/语音 |
|------|---------|-----------|
| **边界 RSSI** | -67 dBm | -65 dBm |
| **SNR** | ≥ 25 dB | ≥ 25 dB（语音 ≥ 25–30 dB） |
| **AP 发射功率** | 自动（RRM）或 11–14 dBm | **手动/自动下限 5–8 dBm** |
| **相邻覆盖重叠** | 15%–20% | 15%–20%（且差值 ≤ 5 dB） |
| **数据速率下限** | 12 Mbps | 12–24 Mbps |

</div>

> 💡 **RRM is not a magic bullet**: automatic channel/power works well in **sparse deployments**, but in **high-density scenarios that were manually planned** it often "cleverly" raises power back. The usual approach in high-density areas is **disable automatic power (fixed low power) + keep automatic channel selection**, or clamp the RRM power range to a narrow band (e.g. 5–8 dBm).

<div class="zh" markdown="1">

> 💡 **RRM（Radio Resource Management）不是万能**：自动信道/功率在**稀疏部署**下表现不错，但在**高密度人工规划过的场景**里往往会"自作聪明"地把功率调回去。高密度区域通常的做法是**关闭自动功率（固定低功率）+ 保留自动信道**，或把 RRM 的功率范围锁死在很窄的区间（如 5–8 dBm）。

</div>

### Wired-Side Dependencies (the section most often forgotten) · 有线侧配套（最容易被漏掉的一段）

The "upstream" of a wireless AP is the wired network, and it often becomes the bottleneck before the RF does:

<div class="zh" markdown="1">

无线 AP 的"上游"是有线网，它经常比 RF 先成为瓶颈：

</div>

| Item | Requirement | Explanation |
|------|------|------|
| **AP uplink speed** | Wi-Fi 6 AP ≥ **2.5 G**, Wi-Fi 6E/7 ≥ **5 G/10 G** | A 1 G uplink throttles a 1.2 Gbps AP outright |
| **Cabling category** | **Cat6a** (needed for mGig 2.5/5/10G) | Cat5e only supports 1G/2.5G (short runs) |
| **PoE** | Wi-Fi 6: **802.3at (PoE+, 30 W)**; Wi-Fi 6E/7: **802.3bt (60–90 W)** | Insufficient power degrades the AP (radios off, MIMO reduced) |
| **Access switch uplink** | Oversubscription 1:10–1:20 (office), 1:5 (high density) | 40 APs × 2.5 G = 100 G, so it must be oversubscribed |
| **VLAN/trunk** | AP management VLAN + all service VLANs | FlexConnect depends on this heavily |
| **DHCP pool** | Size at peak concurrency × 1.5, short leases (2–4 h) | Pool exhaustion means "it connects but there is no internet" |
| **Multicast/broadcast suppression** | Enabled on access ports | Prevents flooding from saturating airtime |

<div class="zh" markdown="1">

| 项目 | 要求 | 说明 |
|------|------|------|
| **AP 上行端口速率** | Wi-Fi 6 AP ≥ **2.5 G**，Wi-Fi 6E/7 ≥ **5 G/10 G** | 1 G 上行会直接卡死 1.2 Gbps 的 AP |
| **布线等级** | **Cat6a**（mGig 2.5/5/10G 需要） | Cat5e 只能跑 1G/2.5G（短距离） |
| **PoE 供电** | Wi-Fi 6：**802.3at（PoE+，30 W）**；Wi-Fi 6E/7：**802.3bt（60–90 W）** | 供电不足会让 AP 降级（关射频/降 MIMO） |
| **接入交换机上行** | 收敛比 1:10 ~ 1:20（办公）、1:5（高密度） | 40 台 AP × 2.5 G = 100 G，必须收敛 |
| **VLAN/Trunk** | AP 管理 VLAN + 所有业务 VLAN | FlexConnect 尤其依赖 |
| **DHCP 池** | 按峰值并发 × 1.5 规划，租期缩短（2–4 h） | 池耗尽 = "连上但上不了网" |
| **组播/广播抑制** | 接入端口开启 | 防泛洪打满 airtime |

</div>

### Capacity Baselines by Venue (a reference table you can cite directly) · 不同场所的容量基线（可直接引用的设计参考表）

| Venue | Concurrency | Bandwidth per user | Coverage per AP | Clients per AP | Main risk |
|------|-------|---------|-----------|------------|---------|
| Open office | 50%–70% | 2–5 Mbps | 150–250 m² | 30–40 | Coverage holes from partitions |
| Meeting room (10–20 people) | 90% | 5–10 Mbps | 1 AP/room (1 AP per 2 small rooms) | 10–20 | High-power APs interfering through walls |
| Lecture theatre (200–400) | 80% | 2–3 Mbps | 1 AP per 40–60 seats | 30–40 | Insufficient uplink power, body absorption |
| Stadium/arena | 70%–90% | 1–2 Mbps | Zoned directional antennas | 50–80 | High mounting, no close-in coverage |
| Hospital outpatient/ward | 60% | 3–5 Mbps (including medical devices) | 100–150 m² | 20–30 | Medical devices 2.4 GHz only, roaming (mobile rounds) |
| Warehouse/manufacturing | 30%–50% | 1–3 Mbps (scanning/PDA) | Depends on rack height and metal | 20–30 | Metal reflections, roaming (forklifts) |
| Hotel guest rooms | 60% | 2–4 Mbps | 1 AP per 4–8 rooms | 10–20 | Corridor coverage, wall attenuation |

<div class="zh" markdown="1">

| 场所 | 并发率 | 人均带宽 | AP 覆盖面积 | 每 AP 客户端 | 主要风险 |
|------|-------|---------|-----------|------------|---------|
| 开放办公 | 50%–70% | 2–5 Mbps | 150–250 m² | 30–40 | 隔断多导致覆盖空洞 |
| 会议室（10–20 人） | 90% | 5–10 Mbps | 1 AP/间（小间隔 1AP/2 间） | 10–20 | 高功率 AP 跨墙干扰 |
| 阶梯教室（200–400 人） | 80% | 2–3 Mbps | 1 AP / 40–60 座 | 30–40 | 上行功率不足、人体吸收 |
| 体育馆/场馆 | 70%–90% | 1–2 Mbps | 定向天线分区 | 50–80 | 高空安装、无法近距覆盖 |
| 医院门诊/病房 | 60% | 3–5 Mbps（含医疗设备） | 100–150 m² | 20–30 | 医疗设备 2.4 GHz 专用、漫游（移动查房） |
| 仓储/制造 | 30%–50% | 1–3 Mbps（扫码/PDA） | 按货架高度与金属 | 20–30 | 金属反射、漫游（叉车移动） |
| 酒店客房 | 60% | 2–4 Mbps | 1 AP / 4–8 间房 | 10–20 | 走廊式覆盖、墙体衰减 |

</div>

### The Complete High-Density Capacity Model (four-layer derivation + two worked examples) · 高密度的完整容量模型（四层推演 + 两个算例）

The earlier example used the simplified "bandwidth → throughput" path. Real high-density design must be more rigorous, because **pps often saturates before Mbps does**.

<div class="zh" markdown="1">

前面的算例用的是"带宽 → 吞吐"的简化路径。真实高密度设计要更严谨，因为**pps 常常比 Mbps 更早到顶**。

</div>

```
Layer 1: service layer   concurrent clients × per-user application mix → total Mbps + total pps
Layer 2: frame layer     average frame size → pps per client → pps per AP
Layer 3: airtime layer   pps × per-frame airtime (including overhead/retries) → airtime utilisation
Layer 4: RF layer        channel count / reuse distance / power → spectrum available per AP
```

<div class="zh" markdown="1">

```
第 1 层：业务层      并发客户端数 × 每人应用组合 → 总 Mbps + 总 pps
第 2 层：帧层        平均帧大小 → 每客户端 pps → 每 AP pps
第 3 层：airtime 层  pps × 单帧 airtime（含开销/重传） → airtime 占用率
第 4 层：RF 层       信道数 / 复用距离 / 功率 → 每 AP 能分到多少频谱
```

</div>

**Example A: very large classroom (250 people, interactive teaching + video)**

<div class="zh" markdown="1">

**算例 A：超大教室（250 人，教学互动 + 视频）**

</div>

```
① Concurrency: 250 × 0.9 = 225 devices
② Service: 2 Mbps down + 0.3 Mbps up per person → 517 Mbps downlink
       pps per person ≈ 250 (mixed traffic, average frame 700 B)
③ Target 35 devices per AP → 7 APs needed (6.4 rounded up)
④ pps check: 225 × 250 = 56,250 pps ÷ 7 APs ≈ 8,000 pps/AP
   average airtime per frame (700 B @ 86 Mbps + 160 µs overhead) ≈ 225 µs
   8,000 × 225 µs = 1,800,000 µs/s → 180%?! Over 100%
⑤ Correction: aggregation (A-MPDU of 4–8 frames) amortises the fixed overhead,
   at 4-frame aggregation → effective airtime per frame ≈ 90 µs
   8,000 × 90 µs = 720,000 µs/s = 72% → still high, so 9–10 APs are needed
⑥ Conclusion: 7 APs by bandwidth, 9–10 by pps/airtime — take 10
```

<div class="zh" markdown="1">

```
① 并发：250 × 0.9 = 225 台
② 业务：每人下行 2 Mbps + 上行 0.3 Mbps → 517 Mbps 下行
       每人 pps ≈ 250（混合流量，平均帧 700 B）
③ 每 AP 承载目标 35 台 → 需要 7 台 AP（6.4 取整）
④ pps 校核：225 × 250 = 56,250 pps ÷ 7 AP ≈ 8,000 pps/AP
   单帧平均 airtime（700 B @ 86 Mbps + 160 µs 开销）≈ 225 µs
   8,000 × 225 µs = 1,800,000 µs/s → 180% ?! 超过 100%
⑤ 修正：实际会通过聚合（A-MPDU 4–8 帧）把固定开销摊薄，
   按 4 帧聚合 → 单帧等效 airtime ≈ 90 µs
   8,000 × 90 µs = 720,000 µs/s = 72% → 仍偏高，需要 9–10 台 AP
⑥ 结论：按带宽算 7 台，按 pps/airtime 算 9–10 台 —— 取 10 台
```

</div>

**This example makes the single most important point**: **bandwidth-only sizing underestimates the AP count**. Anything that is "small frames + many people" (interactive teaching, scanning, IoT, voting, social feeds) must be checked with pps.

<div class="zh" markdown="1">

**这个算例说明了最重要的一件事**：**带宽算法会低估 AP 需求**。凡是"小包 + 多人"的场景（教学互动、扫码、IoT、投票、弹幕），都要用 pps 校核。

</div>

**Example B: stadium (8,000 seats, full house for 2 hours)**

<div class="zh" markdown="1">

**算例 B：体育馆（8,000 座，满场 2 小时）**

</div>

```
① Concurrency: 8,000 × 0.85 = 6,800
② Service: mostly social sharing/short video, 1 Mbps down + 0.3 Mbps up per person
       → 8.8 Gbps total demand (note: this figure is almost impossible to deliver in wireless)
③ Realistic framing: the goal is not "1 Mbps for everyone" but "everyone can get their content out"
   → design at 0.5 Mbps per person → 4.4 Gbps
④ Effective throughput per AP (5 GHz 20 MHz + zoned directional antennas) ≈ 130 Mbps
   → 34 APs by capacity, but seating-zone coverage needs ≥ 60 APs
⑤ Spectrum check: 60 APs, 25 non-overlapping 20 MHz channels in 5 GHz → 2.4 layers of reuse, acceptable
⑥ Uplink check: 60 × 2.5G uplinks → 100G aggregation; or 1:4 oversubscription → 40G
⑦ Conclusion: 34 APs by capacity, 60 by coverage → take 60; the eventual bottleneck is aggregation and the internet edge
```

<div class="zh" markdown="1">

```
① 并发：8,000 × 0.85 = 6,800
② 业务：以社交分享/短视频为主，人均 1 Mbps 下行 + 0.3 Mbps 上行
       → 8.8 Gbps 总需求（注意：这个数字在无线里几乎不可能满足）
③ 现实定位：场馆设计的目标不是"人人 1 Mbps"，而是"人人能发得出去"
   → 按人均 0.5 Mbps 设计 → 4.4 Gbps
④ 每 AP 有效吞吐（5 GHz 20 MHz + 定向天线分区）≈ 130 Mbps
   → 需要 34 台 AP（按容量），但座席分区覆盖需要 ≥ 60 台
⑤ 频谱校核：60 台 AP、5 GHz 25 个 20 MHz 信道 → 复用度 2.4 层，可接受
⑥ 上行校核：60 × 2.5G 上行 → 汇聚需 100G；或按 1:4 收敛 → 40G
⑦ 结论：容量 34 台、覆盖 60 台 → 取 60 台；瓶颈最终落在"汇聚与出口"
```

</div>

> 💡 **The truth about venues**: **wireless will not be the first bottleneck; the internet edge and aggregation will be**. With 8,000 people uploading photos simultaneously, even a 10 Gbps edge fills up. So a venue design must state its **service ceiling** explicitly (e.g. "supports 0.5 Mbps social sharing per person, does not support high-definition live uplink") and write that expectation management into the document.

<div class="zh" markdown="1">

> 💡 **场馆的真相**：**无线不会是第一个瓶颈，出口带宽与汇聚才是**。8,000 人同时上传照片，出口 10 Gbps 也会满。所以场馆方案必须明确写"业务上限"（例如"支持每人 0.5 Mbps 的社交分享，不支持高清直播上行"），把期望值管理写进文档。

</div>

### High-Density Parameter Checklist (one-page version) · 高密度参数清单（一页纸版本）

| Parameter | Normal office | High density | Explanation |
|---|---|---|---|
| **Channel width** | 5 GHz 40 MHz | **5 GHz 20 MHz** (6 GHz may use 80) | Spectrum reuse first |
| **Transmit power** | Auto/11–14 dBm | **Fixed 5–8 dBm** | Small, many cells |
| **MIN RSSI** | Disabled or −72 | **−67 dBm** | Evict weak clients |
| **Data rate floor** | 12 Mbps | **12–24 Mbps** | Kill the slow-rate black hole |
| **Beacon interval** | 100 ms | 100–200 ms (careful) | Larger saves airtime but affects discovery and roaming |
| **DTIM period** | 2–3 | 3 (5 with many IoT devices) | Larger saves power but adds multicast delay |
| **SSID count** | ≤ 4 | **≤ 2** | One Beacon per SSID |
| **Probe suppression** | Off | On (careful; old endpoints affected) | Reduces Probe Response storms |
| **RX-SOP** | Off | Can be enabled (−76 to −82 dBm) | Improves spatial reuse but "stops hearing" distant clients |
| **Band Steering** | On | Force 5/6 GHz preference | Reduces 2.4 GHz congestion |
| **Load balancing** | Optional | On (gentle thresholds) | Endpoints may refuse |
| **Airtime Fairness** | On | **Mandatory** | Suppresses slow clients |
| **Multicast-to-unicast** | As needed | **Mandatory** | Critical for video/mirroring |
| **Broadcast/multicast suppression** | 20–30 pps | 10–20 pps (careful) | Too low breaks DHCP/mDNS |
| **WMM** | On | On + CAC | |

<div class="zh" markdown="1">

| 参数 | 普通办公 | 高密度 | 说明 |
|---|---|---|---|
| **信道宽度** | 5 GHz 40 MHz | **5 GHz 20 MHz**（6 GHz 可 80） | 频谱复用优先 |
| **发射功率** | 自动/11–14 dBm | **固定 5–8 dBm** | 蜂窝小而多 |
| **MIN RSSI** | 不启用或 -72 | **-67 dBm** | 驱逐弱信号 |
| **数据速率下限** | 12 Mbps | **12–24 Mbps** | 杀低速黑洞 |
| **Beacon 间隔** | 100 ms | 100–200 ms（谨慎） | 增大可省 airtime，但影响发现与漫游 |
| **DTIM 周期** | 2–3 | 3（IoT 多时 5） | 越大越省电，但组播延迟增加 |
| **SSID 数** | ≤ 4 | **≤ 2** | 每 SSID 一份 Beacon |
| **探测抑制** | 关闭 | 开启（谨慎，老终端受影响） | 减少 Probe Response 风暴 |
| **RX-SOP** | 关闭 | 可开启（-76 ~ -82 dBm） | 提高空间复用，但会"听不到"远处客户端 |
| **Band Steering** | 开启 | 强制 5/6 GHz 优先 | 减少 2.4 GHz 拥挤 |
| **负载均衡** | 可选 | 开启（温和阈值） | 终端可能拒绝 |
| **Airtime Fairness** | 开启 | **必须开启** | 抑制低速客户端 |
| **组播转单播** | 按需 | **必须开启** | 视频/投屏场景关键 |
| **广播/组播抑制** | 20–30 pps | 10–20 pps（谨慎） | 太低会断 DHCP/mDNS |
| **WMM** | 开启 | 开启 + CAC | |

</div>

> ⚠️ **These parameters are not "turn everything on"**: `RX-SOP` and `probe suppression` both cause some endpoints to "fail to connect", and overly aggressive `broadcast suppression` breaks DHCP and mDNS. **High-density tuning must be validated on site with real endpoints**, and you must keep a one-click rollback configuration template.

<div class="zh" markdown="1">

> ⚠️ **这些参数不是"全开就好"**：`RX-SOP` 与`探测抑制`都会让部分终端"连不上"，`广播抑制`过低会打断 DHCP 与 mDNS。**高密度调优必须在现场用真实终端实测**，且要保留一键回退的配置模板。

</div>

### Client-Side Problems: The Half You Do Not Control · 客户端侧的问题：你控制不了的那一半

| Symptom | Client mechanism | Response |
|---|---|---|
| **Private MAC randomization** | iOS/Android/Windows use a random MAC per SSID by default and rotate it periodically | Never authenticate/authorise by MAC; shorten DHCP leases; use certificates for NAC; expect inflated "devices per person" counts |
| **Aggressive power save (PSM/U-APSD)** | Phones enter power save with the screen off, delaying buffered downlink | Reduce DTIM (the opposite for IoT); use WMM-PS for voice; optimise AP buffering parameters |
| **Scanning slows roaming** | Some Android devices only scan when the signal is already terrible | Enable 11k Neighbor Report; guarantee coverage overlap |
| **Band preference** | Some endpoints "remember" the last 2.4 GHz BSSID | Band steering + MIN RSSI + simply not offering a 2.4 GHz employee SSID |
| **Driver differences** | The same model with different driver versions has different roaming thresholds | Standardise endpoints (single model/driver version) in the IT baseline |
| **Wi-Fi 6 feature negotiation failure** | Old drivers are poor at OFDMA/TWT | Disable TWT or disable 11ax features per SSID (compatibility mode) |

<div class="zh" markdown="1">

| 现象 | 客户端机制 | 应对 |
|---|---|---|
| **私有 MAC 随机化** | iOS/Android/Windows 默认对每个 SSID 使用随机 MAC，且会定期更换 | 不用 MAC 做认证/授权；DHCP 租期缩短；NAC 用证书；注意"每人多设备"计数膨胀 |
| **激进省电（PSM/U-APSD）** | 手机息屏后进入省电，下行缓存延迟 | DTIM 调小（IoT 场景相反）；语音用 WMM-PS；AP 侧缓存参数优化 |
| **扫描拖慢漫游** | 部分 Android 只在信号极差时才扫描 | 开 11k Neighbor Report；保证覆盖重叠 |
| **频段偏好** | 部分终端"记得"上次的 2.4 GHz BSSID | Band Steering + MIN RSSI + 干脆不提供 2.4 GHz 员工 SSID |
| **驱动差异** | 同一型号不同驱动版本，漫游阈值不同 | 终端标准化（企业统一机型/驱动版本）写进 IT 基线 |
| **Wi-Fi 6 特性协商失败** | 老驱动对 OFDMA/TWT 兼容性差 | 关闭 TWT 或按 SSID 关闭 11ax 特性（兼容模式） |

</div>

> 💡 **An engineering consensus we have to live with**: **30% of the wireless experience is decided by endpoints, and endpoints are outside your management scope**. So the design goal is "make bad clients still usable" (reliable baseline coverage + sensible minimum rate + not over-depending on new features), and those "client-side assumptions" must appear explicitly in the risk section of the design document.

<div class="zh" markdown="1">

> 💡 **一条无奈的工程共识**：**无线体验的 30% 由终端决定，而终端不在你的管理范围内**。所以设计上要做的是"让差终端也还能用"（保底覆盖 + 最低速率合理 + 不要过度依赖新特性），并把这些"终端侧假设"明确写进设计文档的风险项。

</div>

### On-Site Support for Large Events (sports, annual parties, product launches) · 大型活动的现场保障（赛事/年会/发布会）

The real test of a high-density project is not the design but **the two hours on the day**. A mature support process looks like this:

<div class="zh" markdown="1">

高密度项目真正的考验不是设计，而是**活动当天的 2 小时**。成熟的保障流程包含：

</div>

| Phase | Actions |
|---|---|
| **T-30 days** | Complete an AP-on-a-stick survey; finalise seating zones and directional antenna aiming; issue the final channel/power plan |
| **T-7 days** | Empty-venue stress test (dozens of endpoints simulating real people: video, uploads, roaming); validate DHCP/authentication capacity; back up configuration |
| **T-1 day** | On-site walkthrough (are APs obstructed, power, uplinks); build the monitoring wall (airtime, client count, auth failure rate, DHCP pool headroom); prepare rollback configuration |
| **Event day** | Check the four metrics every 15 minutes; playbook: disable non-critical SSIDs, cap video uplink, temporarily raise broadcast suppression, steer to 6 GHz |
| **T+1 day** | Export the data (peak airtime, client distribution, top-5 failure reasons) → post-mortem and baseline correction |

<div class="zh" markdown="1">

| 阶段 | 动作 |
|---|---|
| **T-30 天** | 完成 AP-on-a-stick 勘测；确定座席分区与定向天线朝向；输出信道/功率终版图 |
| **T-7 天** | 空场压力测试（用几十台终端模拟真人：视频、上传、漫游）；校验 DHCP/认证容量；备份配置 |
| **T-1 天** | 现场巡检（AP 是否被遮挡、供电、上行链路）；搭建监控大屏（airtime、客户端数、认证失败率、DHCP 池余量）；准备回退配置 |
| **活动当天** | 每 15 分钟看一次四个指标；预案：关闭非关键 SSID、限制视频上行、临时提高广播抑制、引导到 6 GHz |
| **T+1** | 导出数据（airtime 峰值、客户端分布、失败原因 top5）→ 复盘并修正基线 |

</div>

**The four metrics you must watch on the day**:

<div class="zh" markdown="1">

**四个"活动当天必须盯"的指标**：

</div>

1. **Airtime per AP** (find the hot APs rather than looking at the average)
2. **Authentication failure rate** (is RADIUS saturated?)
3. **DHCP pool headroom** (the thing most likely to run out in the first 10 minutes)
4. **Uplink utilisation** (are the aggregation ports full?)

<div class="zh" markdown="1">

1. **每 AP airtime**（找热点 AP，而不是看平均）
2. **认证失败率**（RADIUS 是否被打满）
3. **DHCP 池余量**（最容易在开场 10 分钟内耗尽）
4. **上行链路利用率**（汇聚口是否打满）

</div>

### Eight High-Density Design Fallacies · 高密度设计的八个误区

| Fallacy | Reality |
|------|------|
| "More APs is always better" | Too many APs cause CCI and constant roaming, which is worse; density must match power/channel settings |
| "Wi-Fi 6 solves crowds" | Old endpoints do not participate in OFDMA; the uplink is still limited by endpoint power |
| "80/160 MHz is faster" | In high density there is not enough spectrum for reuse; 20 MHz is capacity-optimal |
| "Stronger signal is better" | Strong signal = large cell = diluted airtime + degraded roam points |
| "RRM will sort itself out" | High density needs manual planning; RRM only trims |
| "As long as clients can associate" | Weak clients drag down the whole AP's airtime |
| "Just look at downlink bandwidth" | The uplink (client → AP) is often the real bottleneck |
| "Wireless problems are in wireless gear" | DHCP, RADIUS, MTU and multicast suppression all live on the wired side |

<div class="zh" markdown="1">

| 误区 | 现实 |
|------|------|
| "AP 越多越好" | 过多 AP 导致 CCI 与漫游频繁，反而更差；密度必须与功率/信道配套 |
| "上 Wi-Fi 6 就能解决人多" | 老终端不参与 OFDMA；上行仍受终端功率限制 |
| "80/160 MHz 更快" | 高密度下频谱不够复用，20 MHz 才是容量最优 |
| "信号越强越好" | 强信号 = 大蜂窝 = airtime 均摊 + 漫游点恶化 |
| "自动 RRM 会自己搞定" | 高密度需人工规划，RRM 只做微调 |
| "客户端能连上就行了" | 弱信号客户端拖垮整个 AP 的 airtime |
| "只看下行带宽" | 上行（客户端→AP）常是真正的瓶颈 |
| "无线问题都在无线设备" | DHCP、RADIUS、MTU、组播抑制都在有线侧 |

</div>

---

## Voice and Video Design · 语音和视频设计

### The End-to-End QoS Chain (Wireless Is Only One Segment) · 端到端 QoS 链路（无线只是其中一段）

```
endpoint → [WMM/EDCA queues] → [AP: 802.11 UP → DSCP mapping] → [CAPWAP/local forwarding]
     → [wired QoS: DSCP classification/queuing] → [WAN QoS] → [call server/gateway]
```

<div class="zh" markdown="1">

```
终端 → [WMM/EDCA 队列] → [AP: 802.11e UP → DSCP 映射] → [CAPWAP/本地转发]
     → [有线 QoS: DSCP 分类/排队] → [WAN QoS] → [呼叫服务器/网关]
```

</div>

**If any single segment is misconfigured, end-to-end QoS collapses.** The key wireless action is to **trust and map correctly**:

<div class="zh" markdown="1">

**任何一段没配对，端到端 QoS 就失效。** 无线侧的关键动作是"**信任并正确映射**"：

</div>

| Layer | Mechanism | Configuration points |
|------|------|---------|
| **WMM (802.11e)** | Four access categories (AC) | Must be enabled (on by default); voice uses AC_VO |
| **UP → DSCP mapping** | 802.11 user priority → IP DSCP | Controller QoS Profile (Platinum/Gold/Silver/Bronze) |
| **CAPWAP outer header** | DSCP inherited inside the tunnel | Ensure the outer value is not reset (`tunnel dscp`) |
| **Wired-side trust** | Switch/router trusts the DSCP coming from the AP | Port `mls qos trust dscp` (the AP has already marked it) |
| **Upstream queuing** | Voice queue (LLQ/Priority) | Guarantee EF a bandwidth ceiling and priority scheduling |

<div class="zh" markdown="1">

| 层次 | 机制 | 配置要点 |
|------|------|---------|
| **WMM（802.11e）** | 4 个接入类别（AC） | 必须启用（默认开启）；语音走 AC_VO |
| **UP → DSCP 映射** | 802.11 用户优先级 → IP DSCP | 控制器 QoS Profile（Platinum/Gold/Silver/Bronze） |
| **CAPWAP 外层** | 隧道内 DSCP 继承 | 确保外层不被重置（`tunnel dscp`） |
| **有线侧信任** | 交换机/路由信任 AP 发来的 DSCP | 端口 `mls qos trust dscp`（AP 已做标记） |
| **上游队列** | 语音队列（LLQ/Priority） | 保证 EF 有带宽上限与优先调度 |

</div>

**The four WMM access categories**:

<div class="zh" markdown="1">

**WMM 的四个接入类别**：

</div>

| AC | 802.11 UP | Typical applications | Default DSCP |
|----|-----------|---------|----------|
| **Voice (AC_VO)** | 6, 7 | VoIP, voice signalling | EF (46) / CS5 (40) |
| **Video (AC_VI)** | 4, 5 | Video conferencing, streaming | AF41 (34) |
| **Best Effort (AC_BE)** | 0, 3 | Ordinary data, web | 0 |
| **Background (AC_BK)** | 1, 2 | Backup, printing, updates | CS1 (8) |

<div class="zh" markdown="1">

| AC | 802.11 UP | 典型应用 | 默认 DSCP |
|----|-----------|---------|----------|
| **Voice（AC_VO）** | 6、7 | VoIP、语音信令 | EF (46) / CS5 (40) |
| **Video（AC_VI）** | 4、5 | 视频会议、流媒体 | AF41 (34) |
| **Best Effort（AC_BE）** | 0、3 | 普通数据、网页 | 0 |
| **Background（AC_BK）** | 1、2 | 备份、打印、更新 | CS1 (8) |

</div>

> ⚠️ **The VIDEO vs VOICE distinction matters**: video is usually "high bandwidth, tolerates some loss", while voice is "low bandwidth, tolerates almost no loss or jitter". Putting video conferencing into AC_VO squeezes out real voice — which is the true cause behind many "voice quality is poor" complaints.

<div class="zh" markdown="1">

> ⚠️ **VIDEO 与 VOICE 的区别很重要**：视频通常是"高带宽 + 可容忍少量丢包"，语音是"低带宽 + 极不容忍丢包与抖动"。把视频会议放进 AC_VO 会挤掉真正的语音 —— 这是很多"语音质量差"投诉的真实原因。

</div>

### Call Admission Control (CAC) · 呼叫准入控制

**The problem**: an AP's airtime is finite. When the 20th voice call arrives, refusing it is the only way to stop all 20 calls degrading **together**.

<div class="zh" markdown="1">

**问题**：一台 AP 的 airtime 是有限的。第 20 个语音呼叫进来时，如果不拒绝，20 个呼叫**全部**劣化。

</div>

| CAC type | Mechanism | Advantage | Disadvantage |
|---------|------|------|------|
| **Bandwidth-based** | Reserves a fixed airtime percentage for AC_VO (e.g. 75%) | Simple, client-independent | Coarse estimation |
| **Call-count / SIP** | Works with the call server; computed from actual call count and codec | Accurate | Needs SIP interworking/call server support |
| **Load-based** | Decides dynamically from measured channel utilisation | Adaptive | Parameters are hard to tune |
| **802.11v BSS Load** | The AP advertises load and clients decide | Client participation | Depends on client implementation |

<div class="zh" markdown="1">

| CAC 类型 | 机制 | 优点 | 缺点 |
|---------|------|------|------|
| **基于带宽（Bandwidth-based）** | 为 AC_VO 预留固定 airtime 比例（如 75%） | 简单、终端无关 | 估算粗糙 |
| **基于呼叫数（Call-count / SIP）** | 与呼叫服务器联动，按实际呼叫数与编码计算 | 精确 | 需要 SIP 互通/呼叫服务器支持 |
| **负载型（Load-based）** | 按实测信道利用率动态判断 | 自适应 | 参数难调 |
| **802.11v BSS Load** | AP 广播负载，终端自行决策 | 终端参与 | 依赖终端实现 |

</div>

**Typical configuration target**: reserve **70%–75%** of airtime for AC_VO; the per-AP call ceiling follows from the codec:

<div class="zh" markdown="1">

**典型配置目标**：AC_VO 预留 **70%–75%** 的 airtime；每 AP 语音呼叫上限按编码算：

</div>

```
G.711 (uncompressed, ~80 kbps + overhead ≈ 100 kbps one way) → about 1.5%–2% airtime per call
G.729 (compressed, ~30 kbps) → about 0.6%–1% airtime per call
```

<div class="zh" markdown="1">

```
G.711（无压缩，~80 kbps + 开销 ≈ 100 kbps 单向）→ 每呼叫约占 1.5%–2% airtime
G.729（压缩，~30 kbps）→ 每呼叫约占 0.6%–1% airtime
```

</div>

### The Voice Roaming Latency Budget · 语音的漫游时延预算

| Stage | Target | Means |
|------|------|------|
| Scan and discovery | < 30 ms | 802.11k Neighbor Report |
| Re-association | < 20 ms | 802.11r FT (over-the-air) |
| Key derivation | < 10 ms | PMK cache + FT |
| **Total roaming interruption** | **< 50 ms** | All of the above + 15%–20% coverage overlap |
| Packet-loss tolerance | < 1% (< 3 consecutive packets) | WMM + CAC + no retry storms |

<div class="zh" markdown="1">

| 环节 | 目标 | 手段 |
|------|------|------|
| 扫描发现 | < 30 ms | 802.11k Neighbor Report |
| 重关联 | < 20 ms | 802.11r FT（Over-the-Air） |
| 密钥派生 | < 10 ms | PMK 缓存 + FT |
| **总漫游中断** | **< 50 ms** | 以上全部 + 覆盖重叠 15%–20% |
| 丢包容忍 | < 1%（< 3 个连续包） | WMM + CAC + 无重传风暴 |

</div>

### Voice Capacity in Detail: How Many Calls Can One AP Really Carry · 语音容量精算：每 AP 到底能带多少通

What matters for voice is **the fixed airtime per call** (small frames that cannot be aggregated), not bandwidth.

<div class="zh" markdown="1">

语音的关键在于**每通呼叫的固定 airtime**（小包，无法聚合），而不是带宽。

</div>

```
G.711: RTP payload 160 B / 20 ms → 50 pps per direction
      802.11 frame ≈ 160 B payload + 36 B header ≈ 196 B ≈ 1568 bit
      At MCS 7 (86 Mbps) ≈ 18 µs of data
      Fixed overhead (preamble 40 + IFS/ACK 48 + backoff ~30) ≈ 118 µs
      → one uplink frame ≈ 136 µs; both directions on air → about 272 µs per 20 ms
      → about 1.36% airtime per call

Target: voice below 60% of airtime (leaving margin for signalling, retries, roaming, Beacons)
→ per-AP ceiling ≈ 60% ÷ 1.36% ≈ 44 calls (G.711)
→ with G.729 (30 kbps, smaller frames) ≈ 60–70 calls, but fixed overhead dominates, so the gain is limited
→ conservative engineering value: **20–25 calls per AP** (allowing for retries, roaming, utilisation swings)
```

<div class="zh" markdown="1">

```
G.711：RTP 载荷 160 B / 20 ms → 50 pps / 方向
      802.11 帧 ≈ 160 B 载荷 + 36 B 头 ≈ 196 B ≈ 1568 bit
      按 MCS 7（86 Mbps）算 ≈ 18 µs 数据
      固定开销（前导码 40 + 帧间隔/ACK 48 + 退避 ~30）≈ 118 µs
      → 单向上行帧 ≈ 136 µs；双向都走空口 → 约 272 µs / 20 ms
      → 每通呼叫 ≈ 1.36% 的 airtime

目标：语音不超过 airtime 的 60%（留余量给信令、重传、漫游、Beacon）
→ 单 AP 上限 ≈ 60% ÷ 1.36% ≈ 44 通（G.711）
→ 若用 G.729（30 kbps，帧更小）≈ 60–70 通，但固定开销占比更高，收益有限
→ 工程保守值：**每 AP 20–25 通**（考虑重传、漫游、信道利用率波动）
```

</div>

| Codec | Bit rate | pps | Airtime per call | Per-AP theoretical/engineering ceiling |
|---|---|---|---|---|
| G.711 | 64 kbps | 50 | ≈ 1.36% | 44 / **20–25** |
| G.729 | 8 kbps | 50 (20 ms packets) | ≈ 1.0% | 60 / **30** |
| G.722 / OPUS (wideband) | 48–64 kbps | 50 | ≈ 1.4% | 42 / **20** |
| Video call (720p) | 1–2 Mbps | — | ≈ 5%–10% | **6–10** |

<div class="zh" markdown="1">

| 编码 | 码率 | pps | 每通 airtime | 单 AP 理论/工程上限 |
|---|---|---|---|---|
| G.711 | 64 kbps | 50 | ≈ 1.36% | 44 / **20–25** |
| G.729 | 8 kbps | 50（20 ms 包） | ≈ 1.0% | 60 / **30** |
| G.722 / OPUS（宽带） | 48–64 kbps | 50 | ≈ 1.4% | 42 / **20** |
| 视频通话（720p） | 1–2 Mbps | — | ≈ 5%–10% | **6–10** |

</div>

**Two counter-intuitive conclusions**:

<div class="zh" markdown="1">

**两个反直觉结论**：

</div>

1. **Compression helps airtime very little** — because the bottleneck for small frames is the fixed overhead, not the payload;
2. **The real voice ceiling is "concurrent calls × pps", hardly related to "bandwidth utilisation"** — a 100 Mbps radio still only carries 20–25 G.711 calls.

<div class="zh" markdown="1">

1. **压缩编码对 airtime 帮助很小** —— 因为小包的瓶颈是固定开销，不是载荷；
2. **语音的真正上限是"并发通话数 × pps"，与"带宽利用率"关系不大** —— 100 Mbps 的射频也只能带 20–25 通 G.711。

</div>

### End-to-End QoS Configuration Example (Wireless → Wired → WAN) · 端到端 QoS 配置示例（无线 → 有线 → WAN）

```
# ① WLC/controller side: QoS Profile (Platinum for voice)
qos platinum
  average-data-rate 0
  burst-data-rate 0
  # trust client DSCP (managed endpoints) or remark by AVC/protocol identification
wlan VOICE 1 VOICE
  qos platinum
  cac voice tspec-inactivity-timeout 30
  cac voice max-calls 20          # aligned with the engineering ceiling above
  cac voice sip call-snooping

# ② AP uplink (switch): trust the DSCP marked by the AP
interface GigabitEthernet1/0/5
  description AP-3F-0512
  switchport mode trunk
  power inline auto
  mls qos trust dscp              # the AP has already mapped 802.11 UP → DSCP
  ip igmp snooping vlan 120 mrouter learn pim-dvmrp

# ③ Aggregation/core: voice queue (LLQ)
class-map match-any VOICE
  match dscp ef
policy-map WAN-EDGE
  class VOICE
    priority percent 15
  class VIDEO-CONF
    bandwidth percent 20
    random-detect dscp-based
  class class-default
    fair-queue

# ④ Wireless mapping verification (must be consistent, or some segment will reset it)
#   802.11 UP 6/7 → DSCP EF(46)   voice
#   802.11 UP 4/5 → DSCP AF41(34) video
#   802.11 UP 0/3 → DSCP 0       best effort
```

<div class="zh" markdown="1">

```
# ① WLC/控制器侧：QoS Profile（Platinum 给语音）
qos platinum
  average-data-rate 0
  burst-data-rate 0
  # 信任客户端 DSCP（受管终端）或按 AVC/协议识别重标记
wlan VOICE 1 VOICE
  qos platinum
  cac voice tspec-inactivity-timeout 30
  cac voice max-calls 20          # 与上表工程上限一致
  cac voice sip call-snooping

# ② AP 上联（交换机）：信任 AP 标记的 DSCP
interface GigabitEthernet1/0/5
  description AP-3F-0512
  switchport mode trunk
  power inline auto
  mls qos trust dscp              # AP 已完成 802.11 UP → DSCP 映射
  ip igmp snooping vlan 120 mrouter learn pim-dvmrp

# ③ 汇聚/核心：语音队列（LLQ）
class-map match-any VOICE
  match dscp ef
policy-map WAN-EDGE
  class VOICE
    priority percent 15
  class VIDEO-CONF
    bandwidth percent 20
    random-detect dscp-based
  class class-default
    fair-queue

# ④ 无线侧映射核对（必须一致，否则中间某段会重置）
#   802.11 UP 6/7 → DSCP EF(46)  语音
#   802.11 UP 4/5 → DSCP AF41(34) 视频
#   802.11 UP 0/3 → DSCP 0       尽力而为
```

</div>

> ⚠️ **The most common QoS break point**: the AP already marks DSCP, but the access switch port lacks `mls qos trust dscp` (untrusted by default), so **every marking is wiped to 0 at the first hop**. No matter how the queues are configured downstream, voice then gets best effort — which shows up as "voice breaks up as soon as the room fills".

<div class="zh" markdown="1">

> ⚠️ **最常见的 QoS 断裂点**：AP 已经标好 DSCP，但接入交换机端口没有 `mls qos trust dscp`（默认不信任），**所有标记在第一个跳就被抹成 0**。此后无论后面怎么配队列，语音都是尽力而为 —— 表现为"人一多语音就破音"。

</div>

### Wireless Design Points for Video Conferencing (Teams / Zoom / Webex) · 视频会议（Teams / Zoom / Webex）的无线设计要点

| Characteristic | Behaviour | Design implication |
|---|---|---|
| **Adaptive bitrate** | Detects loss and lowers resolution/frame rate | "Lag" often appears as "blur", so users may not report it |
| **Multiple streams** | One uplink + N downlinks per person (SFU mode) | Downlink pressure exceeds uplink, especially in meeting rooms |
| **Bandwidth estimate** | 720p ≈ 1.5 Mbps, 1080p ≈ 3 Mbps per stream | A 10-person room peaks at 20–30 Mbps |
| **Jitter sensitivity** | Noticeable above 30 ms of jitter | WMM AC_VI + upstream queuing |
| **Mostly UDP with TCP fallback** | Falling back to 443 degrades experience sharply | Do not block UDP; do not funnel all traffic into a proxy |
| **Screen sharing** | Bursty high bitrate (especially 4K sharing) | Designing "one AP per room" is more robust |

<div class="zh" markdown="1">

| 特性 | 行为 | 设计含义 |
|---|---|---|
| **自适应码率** | 检测到丢包就降分辨率/降帧 | "卡"往往表现为"模糊"，用户不一定报障 |
| **多流** | 每人 1 路上行 + N 路下行（SFU 模式） | 下行压力大于上行；会议室场景尤其明显 |
| **带宽估算** | 720p ≈ 1.5 Mbps，1080p ≈ 3 Mbps/流 | 一间 10 人会室峰值 20–30 Mbps |
| **对抖动敏感** | > 30 ms 抖动即明显 | WMM AC_VI + 上游队列 |
| **UDP 为主 + TCP 回落** | 443 回落后体验骤降 | 不要阻断 UDP；不要把所有流量塞进代理 |
| **共享屏幕** | 突发高码率（尤其 4K 屏共享） | 会议室按"每间 1 AP"设计更稳 |

</div>

**Practical rules for meeting-room design**:

<div class="zh" markdown="1">

**会议室设计的实用规则**：

</div>

```
Small room (4–6 people)   : 1 AP per 1–2 rooms, 20–40 MHz, low power (avoid cross-wall interference)
Medium room (8–12 people) : 1 AP per room; a dedicated SSID is optional but QoS must be Platinum/Gold
Large room (20–40 people) : 1–2 APs per room, 20 MHz, uplink ≥ 2.5G, Airtime Fairness enabled
Boardroom/video room      : dedicated AP + dedicated VLAN + dedicated SSID (so crowds cannot steal airtime)
```

<div class="zh" markdown="1">

```
小会室（4–6 人）  ：1 AP / 1–2 间，20–40 MHz，低功率（避免跨墙干扰）
中会室（8–12 人） ：1 AP / 间，独立 SSID 可不必，但 QoS 必须 Platinum/Gold
大会室（20–40 人）：1–2 AP / 间，20 MHz，上行 ≥ 2.5G，开启 Airtime Fairness
董事会/视频会议室 ：专用 AP + 专用 VLAN + 独立 SSID（避免被人多挤占）
```

</div>

### Special Considerations for Video and Streaming · 视频/流媒体设计的特殊点

| Problem | Mechanism | Countermeasure |
|------|------|------|
| **Multicast video cripples the network** | Multicast is sent at the lowest rate and eats airtime | **Multicast-to-unicast** + multicast suppression |
| **Retransmissions cause artefacts** | Video tolerates loss but not jitter | Enable Airtime Fairness, cap video streams per AP |
| **Many concurrent streams** | Each stream needs stable airtime | IGMP snooping + planned multicast VLANs |
| **Bandwidth bursts** | 4K streams burst at start-up | Upstream shaping + buffering (client-side DASH/HLS buffering) |

<div class="zh" markdown="1">

| 问题 | 机制 | 对策 |
|------|------|------|
| **组播视频拖垮全网** | 组播以最低速率发送，占用大量 airtime | **组播转单播（Multicast-to-Unicast）** + 组播抑制 |
| **重传导致花屏** | 视频容忍丢包但对抖动敏感 | 开 Airtime Fairness、限制每 AP 视频流数 |
| **大量并发流** | 每流需稳定 airtime | 用 IGMP snooping + 组播 VLAN 规划 |
| **带宽突发** | 4K 流启动时突发 | 上游整形 + 缓冲（DASH/HLS 客户端侧缓冲） |

</div>

### A Dedicated Section on Wireless Multicast: Why It Is the Hidden Bomb of Wireless Design · 无线组播专节：为什么它是无线设计的"隐形炸弹"

**Wired multicast thinking is "replicate along a tree"** (one copy per link); **wireless multicast reality is "broadcast at the lowest rate"** (one copy saturating the whole radio). The gap between the two is an order of magnitude.

<div class="zh" markdown="1">

**有线组播的思维是"按树复制"**（一条链路上只有一份流）；**无线组播的现实是"按最低速率广播"**（一份流占满整块射频）。这两者的差距是数量级的。

</div>

#### The Three Wireless Multicast Handling Modes · 三种无线组播处理模式

| Mode | Mechanism | Airtime cost | Where it fits |
|---|---|---|---|
| **Multicast Direct** | The controller sends multicast frames over the air at the **lowest mandatory rate**; clients receive them individually | **Extremely high** (lowest rate, no ACK, no retransmission protection) | Very low-rate control multicast in small amounts, or scenarios that must broadcast |
| **Multicast-to-Unicast** | The controller converts each multicast stream into **one unicast copy per client** | Medium (one copy per client, but at high rate + with ACKs + aggregatable) | **Recommended**: IPTV, training broadcasts, camera viewing |
| **Multicast/broadcast optimisation (Client Link / multicast caching)** | The AP caches multicast and sends it at unicast/high rate after the DTIM | Low–medium | Default optimisation for mixed scenarios |

<div class="zh" markdown="1">

| 模式 | 机制 | airtime 代价 | 适用 |
|---|---|---|---|
| **组播直通（Multicast Direct）** | 控制器以**最低强制速率**把组播帧发到空口，客户端各自接收 | **极高**（速率最低、无 ACK、无重传保护） | 极低码率的控制类组播（少量），或必须广播的场景 |
| **组播转单播（Multicast-to-Unicast）** | 控制器把每个组播流转成**每个客户端一份单播** | 中（每客户端一份，但用高速率 + 有 ACK + 可聚合） | **推荐**：IPTV、培训直播、监控查看 |
| **组播/广播优化（Client Link / 组播缓存）** | AP 缓存组播并在 DTIM 后以单播/高速率发出 | 低–中 | 混合场景的默认优化 |

</div>

**The key conversion (the quantified "bomb")**:

<div class="zh" markdown="1">

**关键换算（这就是"炸弹"的量化）**：

</div>

```
One 2 Mbps multicast video stream (trivially easy on the wired side)
  Multicast Direct @ 6 Mbps PHY: occupies ≈ 2/6 ≈ 33% of airtime (before overhead and retries)
  Multicast-to-Unicast (30 clients watching)
    one 2 Mbps copy per client at MCS 7 (86 Mbps) unicast
    → 30 × 2/86 ≈ 70% of airtime (worse than Direct!)
  → correct approach: cap the number of simultaneous viewers + raise the unicast rate (40/80 MHz) + use local forwarding
     or simply switch to "unicast on demand (independent HTTP stream per client) + CDN"
```

<div class="zh" markdown="1">

```
一路 2 Mbps 的组播视频（有线侧毫无压力）
  组播直通 @ 6 Mbps PHY：占用 ≈ 2/6 ≈ 33% 的 airtime（还没算开销与重传）
  组播转单播 (30 个客户端观看)
    每客户端 1 份 2 Mbps，用 MCS 7（86 Mbps）单播
    → 30 × 2/86 ≈ 70% 的 airtime（比直通更差！）
  → 正确做法：限制同时观看人数 + 提高单播速率（40/80 MHz）+ 用本地转发
     或干脆改成"单播点播（每客户端独立 HTTP 流）+ CDN"
```

</div>

> 🔥 **This is the most counter-intuitive conclusion about wireless multicast**: **multicast-to-unicast is not a panacea**. With a large audience (e.g. 30+ people watching the same live stream), the airtime cost of converting to unicast can exceed Direct. **The real answer: many viewers → use wired (casting puck/HDMI) or a local CDN/edge cache; few viewers → unicast conversion; very low bitrate → Direct.**

<div class="zh" markdown="1">

> 🔥 **这是无线组播最反直觉的结论**：**"组播转单播"不是万能药**。当观众很多时（如 30+ 人看同一路直播），转单播的 airtime 消耗可能超过直通。**真正的答案是：人数多 → 用有线（投屏器/HDMI）或本地 CDN/边缘缓存；人数少 → 转单播；极低码率 → 直通。**

</div>

#### The Layer 2 and Layer 3 Supporting Configuration · 二层与三层的配套

| Location | Configuration | Purpose |
|---|---|---|
| **Access switch** | `ip igmp snooping` + querier (a VLAN with a multicast router may skip the querier) | Multicast only goes to ports with subscribers, no flooding |
| **AP uplink port** | Static mrouter configuration or PIM learning | The AP joins as a multicast receiver |
| **Wireless controller** | Multicast forwarding mode (Direct / Multicast-to-Unicast / Disabled) | Decides how frames go out over the air |
| **Wireless-side IGMP** | Controller/AP snoops client IGMP Reports | Decides which APs need that group (avoids flooding every AP) |
| **VLAN planning** | A separate VLAN for multicast services | Simplifies boundary control and rate limiting |

<div class="zh" markdown="1">

| 位置 | 配置 | 作用 |
|---|---|---|
| **接入交换机** | `ip igmp snooping` + querier（有组播路由器的 VLAN 可不配 querier） | 组播只送到有订阅者的端口，不泛洪 |
| **AP 上联端口** | mrouter 静态配置或 PIM 学习 | AP 作为组播接收者加入 |
| **无线控制器** | 组播转发模式（Direct / Multicast-to-Unicast / Disabled） | 决定空口如何发 |
| **无线侧 IGMP** | 控制器/AP 监听客户端 IGMP Report | 决定哪些 AP 需要该组流（避免全 AP 泛洪） |
| **VLAN 规划** | 组播业务独立 VLAN | 便于边界控制与限速 |

</div>

#### A Real Worked Example (which is also Case Six later) · 一个真实算例（也是后面的案例六）

**A factory floor pushes 12 camera feeds (1.5 Mbps multicast each) to 20 handheld terminals**:

<div class="zh" markdown="1">

**工厂车间用无线推送 12 路监控画面（每路 1.5 Mbps 组播）到 20 台手持终端**：

</div>

```
Multicast Direct: each feed sent at 6 Mbps → 12 × 1.5/6 = 300% airtime → the shop-floor Wi-Fi collapses outright
Multicast-to-Unicast: 20 terminals × 12 feeds × 1.5 Mbps = 360 Mbps of unicast demand → beyond a single AP
What actually works:
  ① Let terminals subscribe only to the 1–2 feeds they are currently viewing (application change, fewer subscriptions)
  ② Raise the unicast rate (5 GHz 40 MHz, MCS 9 → 200 Mbps effective)
  ③ More APs per zone + local forwarding, spreading the 360 Mbps over 6–8 APs
  ④ Move critical feeds to wired terminals (fixed-position displays over copper)
```

<div class="zh" markdown="1">

```
组播直通：每路按 6 Mbps 发送 → 12 × 1.5/6 = 300% airtime → 车间 Wi-Fi 直接瘫
组播转单播：20 台 × 12 路 × 1.5 Mbps = 360 Mbps 单播需求 → 超出单 AP 能力
真正可行：
  ① 只让终端订阅当前查看的 1–2 路（应用改造，减少订阅）
  ② 提高单播速率（5 GHz 40 MHz，MCS 9 → 200 Mbps 有效）
  ③ 每个区域多 AP + 本地转发，把 360 Mbps 分散到 6–8 台 AP
  ④ 关键画面改用有线终端（固定位置的大屏走网线）
```

</div>

**Lesson**: **carrying multicast over wireless requires changing the application (subscription count) + scaling out (AP density) + optimising the transmission method (unicast conversion) — all three, no exceptions.**

<div class="zh" markdown="1">

**教训**：**无线侧承接组播，必须同时改造应用（订阅数量）+ 扩容（AP 密度）+ 优化发送方式（转单播）**，三者缺一不可。

</div>

---

## Survey and Acceptance: Turning "Feels Good" into "Measurable" · 勘测与验收：把"感觉好"变成"可测量"

### The Four Survey Methods · 四种勘测方式

| Method | How it is done | Advantages | Disadvantages | When to use |
|------|------|------|------|---------|
| **Predictive survey** | Simulation using CAD drawings + material attenuation models | Fast, cheap, easy to compare design options | Model differs greatly from reality (furniture, people, metal) | Design phase, tendering |
| **Passive survey** | Listen only, recording existing AP coverage and interference | Reflects the real RF environment | Only shows signals that already exist | Pre-upgrade assessment |
| **Active survey** | Associate to the SSID and measure throughput/latency/roaming | Closest to the user experience | Time-consuming, requires walking the whole site | Acceptance |
| **AP-on-a-stick** | Use one AP in temporary positions to simulate the final deployment | Most accurate in empty or newly built sites | Repeated relocation, labour intensive | High-density / critical venue acceptance |
| **Continuous validation (sensor)** | Monitor-mode APs collect data continuously after go-live | Finds problems that only appear at peak | Requires extra APs/sensors | Operational phase |

<div class="zh" markdown="1">

| 方式 | 做法 | 优点 | 缺点 | 使用阶段 |
|------|------|------|------|---------|
| **预测性勘测（Predictive）** | 用 CAD 图纸 + 材质衰减模型仿真 | 快、便宜、可对比多种方案 | 模型与实际差异大（家具、人体、金属） | 方案阶段、投标 |
| **被动勘测（Passive）** | 只听不发，记录现有 AP 的覆盖与干扰 | 反映真实 RF 环境 | 只能看已有信号 | 改造前评估 |
| **主动勘测（Active）** | 关联 SSID 后测吞吐/时延/漫游 | 最接近用户体验 | 耗时，需要走遍全场 | 验收 |
| **AP-on-a-stick** | 用一台 AP 在临时位置模拟最终部署 | 在空场地/新建场地最准确 | 需往返移动，人力大 | 高密度/关键场所验收 |
| **持续监测（Validation/Sensor）** | 部署后由 Monitor 模式 AP 持续采集 | 可发现"只在高峰期出现"的问题 | 需额外 AP/传感器 | 运行期 |

</div>

### Quantifiable Acceptance Metrics (to be written into the contract/delivery documents) · 可量化验收指标（写进合同/交付文档）

| Metric | Target | Measurement method |
|------|-------|---------|
| **Coverage RSSI** | Target area ≥ **−67 dBm** | Active survey, gridded (every 5–10 m) |
| **SNR** | ≥ **25 dB** | Survey tool |
| **Co-channel interference (CCI)** | Second-strongest AP ≥ **5–10 dB** below the primary | Survey tool (second strongest on the same channel) |
| **Downlink throughput** | ≥ 80% of design value | iperf3 (multi-stream, bidirectional) |
| **Uplink throughput** | ≥ 70% of design value | iperf3 reverse |
| **Latency/jitter** | Idle RTT < 10 ms; voice jitter < 30 ms | Traffic generation + packet capture |
| **Roaming interruption** | Voice < 50 ms, data < 200 ms | Continuous ping while walking / dedicated roaming test tools |
| **Airtime utilisation** | Peak **< 60%** | Controller statistics / spectrum analysis |
| **Channel utilisation (per AP)** | < 50% | Controller `show ap stats` |
| **Concurrent clients** | Per AP, not exceeding design value | Controller statistics |
| **Retry rate** | < 10% (ideally < 5%) | Controller / packet capture |
| **DHCP success rate** | > 99% | Log statistics |

<div class="zh" markdown="1">

| 指标 | 目标值 | 测量方法 |
|------|-------|---------|
| **覆盖 RSSI** | 目标区域 ≥ **-67 dBm** | 主动勘测，网格化（每 5–10 m） |
| **SNR** | ≥ **25 dB** | 勘测工具 |
| **同频干扰（CCI）** | 第二强 AP 信号比主 AP 低 ≥ **5–10 dB** | 勘测工具（同信道第二强） |
| **下行吞吐** | ≥ 设计值的 80% | iperf3（多流，双向） |
| **上行吞吐** | ≥ 设计值的 70% | iperf3 反向 |
| **时延/抖动** | 空载 RTT < 10 ms；语音抖动 < 30 ms | 打流 + 抓包 |
| **漫游中断** | 语音 < 50 ms、数据 < 200 ms | 边走边 ping / 专用漫游测试工具 |
| **airtime 利用率** | 峰值 **< 60%** | 控制器统计 / 频谱分析 |
| **信道利用率（单 AP）** | < 50% | 控制器 `show ap stats` |
| **并发客户端** | 单 AP 不超过设计值 | 控制器统计 |
| **重传率** | < 10%（理想 < 5%） | 控制器/抓包 |
| **DHCP 成功率** | > 99% | 日志统计 |

</div>

> 💡 **Acceptance must happen at the worst moment**: 30 minutes after the working day starts, 5 minutes before a meeting, the instant a class ends or a venue empties. Beautiful numbers measured in an empty hall mean nothing.

<div class="zh" markdown="1">

> 💡 **验收必须在"最坏时刻"做**：工作日上班后 30 分钟、会议开始前 5 分钟、下课/散场瞬间。在空场测出的漂亮数字没有任何意义。

</div>

### Post-Launch Monitoring Baseline · 上线后的监控基线

| Monitoring item | Alarm threshold | Explanation |
|-------|---------|------|
| APs offline | > 0 (immediately) | Individual failure, or power/uplink problem |
| Client association failure rate | > 5% | RADIUS, DHCP, capacity |
| Airtime utilisation | > 70% sustained for 5 min | Signal to scale out |
| Channel utilisation / retry rate | Retries > 15% | RF interference or coverage problem |
| RADIUS response latency | > 500 ms | Authentication bottleneck |
| Controller CPU / client table | > 70% | Capacity planning |
| DFS channel change events | Occurring frequently | RF stability risk |

<div class="zh" markdown="1">

| 监控项 | 告警阈值 | 说明 |
|-------|---------|------|
| AP 离线数 | > 0（立即） | 单体故障或供电/上行问题 |
| 客户端关联失败率 | > 5% | RADIUS、DHCP、容量 |
| airtime 利用率 | > 70% 持续 5 min | 扩容信号 |
| 信道利用率 / 重传率 | 重传 > 15% | RF 干扰或覆盖问题 |
| RADIUS 响应时延 | > 500 ms | 认证瓶颈 |
| 控制器 CPU / 客户端表 | > 70% | 容量规划 |
| DFS 信道切换事件 | 频繁发生 | RF 稳定性风险 |

</div>

### The Survey Execution Flow (ten steps from drawings to report) · 勘测实施流程（从图纸到报告的 10 步）

```
① Collect drawings (ceiling heights, partition materials, Low-E glass, metal racking positions) → build the attenuation model
② Predictive survey: place APs against the target RSSI, output an initial AP count and layout
③ Confirm critical areas with the business (meeting rooms, executive offices, production areas, racking aisles)
④ On-site validation: AP-on-a-stick, mount one AP in candidate positions at the planned power
⑤ Grid measurement (a point every 5–10 m, every 3 m in critical areas): record RSSI, SNR, second-strongest AP
⑥ Capacity validation: multi-client traffic generation at each AP position (not single-client iperf)
⑦ Roaming validation: walk the real paths (not the straight corridors) and measure interruption and switch points
⑧ Interference scan: spectrum analysis for non-Wi-Fi interferers (microwaves, cameras, radar, DECT)
⑨ Correct the design: feed measured deviations back into power/position/channel; produce the final plot
⑩ Produce the survey report: coverage heat map + channel map + power table + deviation notes + acceptance comparison
```

<div class="zh" markdown="1">

```
① 收集图纸（含层高、隔断材质、Low-E 玻璃、金属货架位置）→ 建立衰减模型
② 预测性勘测：按目标 RSSI 布点，输出初版 AP 位置与数量
③ 与业务确认关键区域（会议室、领导办公室、生产区、货架通道）
④ 现场验证：AP-on-a-stick，在候选位置架设 1 台 AP，按规划功率发射
⑤ 网格化测量（每 5–10 m 一点，关键区域每 3 m）：记录 RSSI、SNR、第二强 AP
⑥ 容量验证：在每 AP 位置做多客户端打流（不是单客户端 iperf）
⑦ 漫游验证：沿真实行走路径（不是走廊直线）测漫游中断与切换点
⑧ 干扰扫描：频谱分析找非 Wi-Fi 干扰（微波、摄像头、雷达、DECT）
⑨ 修正设计：把实测偏差反推回功率/位置/信道，输出终版图
⑩ 输出勘测报告：覆盖热图 + 信道图 + 功率表 + 偏差说明 + 验收对比
```

</div>

**The two things people cut corners on most, with the most serious consequences**:

<div class="zh" markdown="1">

**勘测中最容易偷懒、后果最严重的两项**：

</div>

| Shortcut | Consequence |
|---|---|
| **Measuring only in an empty venue (no people)** | Human attenuation is 3–5 dB per person; with a full hall the coverage boundary shrinks by 3–8 m overall, and it collapses at peak |
| **Measuring downlink RSSI only** | Scenarios limited by the uplink (high AP power) are completely invisible, producing "full bars but uploads fail" after go-live |

<div class="zh" markdown="1">

| 偷懒做法 | 后果 |
|---|---|
| **只在空场（无人）测** | 人体衰减 3–5 dB/人，会场满座时覆盖边界整体内缩 3–8 m，高峰即崩 |
| **只测下行 RSSI** | 上行受限的场景（AP 高功率）完全测不出来，上线后"信号满格上传失败" |

</div>

### Acceptance Test Cases (usable directly as a delivery annex) · 验收测试用例（可直接作为交付附件）

| # | Case | Method | Pass criteria |
|---|---|---|---|
| 1 | Coverage and SNR | Gridded active survey | ≥ 95% of sample points with RSSI ≥ −67 dBm and SNR ≥ 25 dB |
| 2 | Co-channel interference | Survey tool, second-strongest AP on the same channel | ≥ 5–10 dB below the primary AP |
| 3 | Downlink throughput | iperf3 multi-stream, at least 3 concurrent clients per AP | ≥ 80% of design value |
| 4 | Uplink throughput | iperf3 -R reverse | ≥ 70% of design value |
| 5 | Latency and jitter | Three load levels: idle / 50% / peak | Idle RTT < 10 ms; voice jitter < 30 ms |
| 6 | Association and DHCP | 50 endpoints connecting simultaneously | Association > 99%, DHCP > 99% |
| 7 | Authentication capacity | Simultaneous 802.1X at peak concurrency | Success > 99%, P95 < 2 s |
| 8 | Roaming interruption | Walk the path with ping + a voice call | Voice < 50 ms, data < 200 ms, no dropped calls |
| 9 | Cross-controller roaming | Walk across buildings/WLCs | As above, and the IP must not change (if designed as one Layer 2 domain) |
| 10 | Airtime baseline | Observe 30 min during peak | Per AP < 60%, channel utilisation < 50% |
| 11 | Retry rate | Controller statistics | < 10% (target < 5%) |
| 12 | Degradation drill | Disconnect the WAN / primary WLC / one RADIUS node | Behaves as designed (record the real switchover time) |
| 13 | Multicast/screen mirroring | Several endpoints mirroring and streaming simultaneously | No artefacts; per-AP airtime stays under threshold |
| 14 | Long-duration stability | Monitor for 24–72 h continuously | No flaps, no abnormal DFS, no memory leak |
| 15 | Management plane | Bulk WLAN change propagation time, config backup/restore | Change < 15 min; restore drill succeeds |

<div class="zh" markdown="1">

| # | 用例 | 方法 | 通过标准 |
|---|---|---|---|
| 1 | 覆盖与 SNR | 网格化主动勘测 | ≥ 95% 采样点 RSSI ≥ -67 dBm 且 SNR ≥ 25 dB |
| 2 | 同频干扰 | 勘测工具看第二强 AP（同信道） | 比主 AP 低 ≥ 5–10 dB |
| 3 | 下行吞吐 | iperf3 多流，每 AP 至少 3 客户端并发 | ≥ 设计值的 80% |
| 4 | 上行吞吐 | iperf3 -R 反向 | ≥ 设计值的 70% |
| 5 | 时延与抖动 | 空载/50% 负载/峰值三档 | 空载 RTT < 10 ms；语音抖动 < 30 ms |
| 6 | 关联与 DHCP | 50 台终端同时上线 | 关联成功率 > 99%，DHCP 成功率 > 99% |
| 7 | 认证容量 | 峰值并发同时 802.1X 认证 | 认证成功率 > 99%，P95 < 2 s |
| 8 | 漫游中断 | 沿路径行走，ping + 语音通话 | 语音 < 50 ms，数据 < 200 ms，无掉话 |
| 9 | 跨控制器漫游 | 跨楼/跨 WLC 行走 | 同上，且 IP 不变（若设计为二层域） |
| 10 | airtime 基线 | 峰值时段观测 30 min | 单 AP < 60%，信道利用率 < 50% |
| 11 | 重传率 | 控制器统计 | < 10%（目标 < 5%） |
| 12 | 降级演练 | 断开 WAN / 主 WLC / 单台 RADIUS | 按设计预期工作（记录真实切换时间） |
| 13 | 组播/投屏 | 多终端同时投屏 + 直播 | 无花屏、apoint airtime 不超阈值 |
| 14 | 长时间稳定性 | 连续 24–72 h 监控 | 无 flap、无异常 DFS、无内存泄漏 |
| 15 | 管理面 | 批量改 WLAN 生效时间、配置备份/恢复 | 变更 < 15 min；恢复演练成功 |

</div>

### How to Stress Test (it is not "run an iperf and you are done") · 压力测试怎么做（不是"跑个 iperf 就算完"）

```
① Simulate client count: use 30–50 real endpoints (different models), not one device with many streams
   → because the bottleneck is usually per-client fixed overhead and contention, which single-client multi-stream cannot reproduce
② Three load levels: idle baseline → 50% target load → 120% overload
   Record airtime, retry rate, P95 latency and per-client throughput at each level
③ Mixed services: video + voice + uploads + roaming simultaneously
   (a pure download test produces conclusions that are far too optimistic)
④ Interleave roaming: at least two people walking and talking continuously, observing whether others are affected
⑤ Record the "degradation knee": at what airtime does P95 latency start rising non-linearly
   → that knee minus 10% is your capacity red line (far more reliable than vendor datasheets)
```

<div class="zh" markdown="1">

```
① 客户端数量模拟：用 30–50 台真实终端（不同型号），而不是 1 台跑多流
   → 因为瓶颈常在"每客户端的固定开销与竞争"，单客户端多流测不出来
② 三档负载：空载基线 → 50% 目标负载 → 120% 过载
   记录每档的 airtime、重传率、时延 P95、每客户端吞吐
③ 混合业务：视频 + 语音 + 上传 + 漫游 同时进行
   （纯下载测试会给出过于乐观的结论）
④ 漫游穿插：至少 2 人持续走动通话，观察其他人的体验是否受影响
⑤ 记录"劣化拐点"：airtime 到多少时，时延 P95 开始非线性上升
   → 这个拐点减 10% 就是你的容量红线（比厂商标称值可靠得多）
```

</div>

### The Delivery Document Set (the complete deliverable list of a wireless project) · 交付文档清单（无线项目的完整交付物）

| Document | Content | Audience |
|---|---|---|
| **Wireless design document** | The 14-section skeleton shown earlier | Customer IT + reviewers |
| **RF survey report** | Heat maps, channel maps, power tables, interference source inventory | Customer + installers |
| **IP and VLAN plan** | AP management subnets, SSID VLANs, DHCP pools, DNS | Operations |
| **SSID/security matrix** | Per SSID: authentication, encryption, VLAN, ACL, rate limit | Security + operations |
| **Acceptance test report** | Measured data and conclusions for the 15 cases | Customer sign-off |
| **Operations manual** | Monitoring items, alarm thresholds, common fault handling, upgrade procedure | NOC |
| **Configuration baseline** | Controller/switch configuration exports + change process + rollback steps | Operations |
| **Training and handover** | On-site training records, open issues list, risks and pending items | Project manager |

<div class="zh" markdown="1">

| 文档 | 内容 | 谁看 |
|---|---|---|
| **无线设计文档** | 见前文 14 项骨架 | 客户 IT + 评审 |
| **RF 勘测报告** | 热图、信道图、功率表、干扰源清单 | 客户 + 施工方 |
| **IP 与 VLAN 规划表** | AP 管理网段、各 SSID VLAN、DHCP 池、DNS | 运维 |
| **SSID/安全矩阵** | 每 SSID 的认证方式、加密、VLAN、ACL、限速 | 安全 + 运维 |
| **验收测试报告** | 15 项用例的实测数据与结论 | 客户签字 |
| **运维手册** | 监控项、告警阈值、常见故障处置、升级流程 | NOC |
| **配置基线** | 控制器/交换机配置导出 + 变更流程 + 回滚步骤 | 运维 |
| **培训与移交** | 现场培训记录、遗留问题清单、风险与未决项 | 项目经理 |

</div>

---

## Wireless Troubleshooting Methodology · 无线故障定位方法论

Wireless faults feel "hard to diagnose" because **symptoms and layers are mismatched**: the user reports "I cannot get online", while the root cause may sit in DHCP, RADIUS, MTU, airtime or DFS — any layer at all. So troubleshooting must first **locate the layer**, then **locate the device**.

<div class="zh" markdown="1">

无线故障之所以"难查"，是因为**症状与层次错位**：用户报的是"上不了网"，而根因可能在 DHCP、RADIUS、MTU、airtime、DFS 任意一层。所以排障必须先**定位层次**，再**定位设备**。

</div>

### The Four-Layer Investigation Model (run through this order for every fault) · 四层排查模型（每次故障都按这个顺序过一遍）

| Layer | What to look at | Key question | Typical root causes |
|---|---|---|---|
| **① Access layer (RF/802.11)** | Can the client associate? RSSI/SNR? Retry rate? Airtime? | "Is the signal sufficient and the medium congested?" | Coverage holes, excessive power, CCI, slow-rate black holes, multicast flooding |
| **② Control layer (WLC/AP state)** | Is the AP online? Client table? Is configuration being pushed? | "Are the controller and APs healthy?" | APs offline, insufficient licences, tags unbound, WLC overloaded |
| **③ Network layer (wired/IP)** | VLAN, DHCP, gateway, MTU, routing, ACL | "Are the address and path working?" | VLAN not allowed, DHCP pool exhausted, MTU fragmentation, firewall blocking |
| **④ Authentication and policy layer** | 802.1X flow, RADIUS response, dynamic VLAN/ACL delivery | "Are identity and authorisation correct?" | RADIUS timeouts, expired certificates, wrong attributes, CoA failures |

<div class="zh" markdown="1">

| 层 | 看什么 | 关键问题 | 典型根因 |
|---|---|---|---|
| **① 接入层（RF/802.11）** | 客户端能否关联？RSSI/SNR？重传率？airtime？ | "信号是否足够、介质是否拥塞" | 覆盖空洞、功率过大、CCI、低速黑洞、组播泛洪 |
| **② 控制层（WLC/AP 状态）** | AP 是否在线？客户端表？配置是否下发？ | "控制器与 AP 是否健康" | AP 离线、许可不足、Tag 未绑定、WLC 过载 |
| **③ 网络层（有线/IP）** | VLAN、DHCP、网关、MTU、路由、ACL | "地址与路径是否通" | VLAN 未放通、DHCP 池耗尽、MTU 分片、防火墙阻断 |
| **④ 认证与策略层** | 802.1X 流程、RADIUS 响应、动态 VLAN/ACL 下发 | "身份与授权是否正确" | RADIUS 超时、证书过期、属性错误、CoA 失败 |

</div>

**The iron rule of troubleshooting**: **first use one question to decide which layer you are stuck at, then dig into that layer**. The question is:

<div class="zh" markdown="1">

**排障铁律**：**先用一条命令判断"卡在第几层"，再深入那一层**。判断方法就一句话：

</div>

> **Did the client get an IP address?**
> - No IP → stuck at layer 1/2/3 (associated but DHCP failed → layer 3; cannot even associate → layer 1/2)
> - Has an IP but services fail → layer 4 or a policy/routing problem
> - Has an IP, can ping the gateway, but is slow → layer 1 (airtime/interference); it is not a "network problem"

<div class="zh" markdown="1">

> **客户端有没有拿到 IP？**
> - 拿不到 IP → 停在第 1/2/3 层（关联成功但 DHCP 失败 → 第 3 层；关联都失败 → 第 1/2 层）
> - 拿到 IP 但业务不通 → 第 4 层或策略/路由问题
> - 拿到 IP、能 ping 通网关、但慢 → 第 1 层（airtime/干扰），不是"网络问题"

</div>

### Fault Tree One: The Client Cannot Connect (Association Failure) · 故障树一：客户端连不上（关联失败）

```
Client cannot see the SSID
├─ Only some areas cannot see it → that AP is not broadcasting the WLAN (tag binding) / that band is disabled
├─ No one anywhere can see it → the WLAN is shut down / APs have not joined / the RF Profile disables the band
└─ Only a certain class of endpoint cannot see it → 6 GHz (6E/7 endpoints only) / hidden SSID / the endpoint does not support an 11ax-only profile

Visible but association fails
├─ Authentication failure → see "Fault Tree Four: authentication problems"
├─ Association rejected (AP full) → client limit / CAC rejection / load-balancing threshold too aggressive
├─ Stuck at "obtaining IP address" → DHCP pool exhausted / VLAN not allowed / missing relay / Option 82 problem
└─ Associates then immediately disconnects → PMF/11r compatibility / key mismatch / duplicate MAC (private MAC collision)
```

<div class="zh" markdown="1">

```
客户端看不到 SSID
├─ 只有部分区域看不到 → 该 AP 未广播该 WLAN（Tag 绑定）/ 该频段被禁用
├─ 全场都看不到 → WLAN 被关闭 / AP 未 join / RF Profile 禁用了频段
└─ 只有某类终端看不到 → 6 GHz（仅 6E/7 终端）/ 隐藏 SSID / 该终端不支持 11ax only 配置

看得到但关联失败
├─ 认证失败 → 见"故障树四：认证问题"
├─ 关联被拒（AP 满载）→ 客户端数上限 / CAC 拒绝 / 负载均衡阈值过激
├─ 一直"正在获取 IP" → DHCP 池耗尽 / VLAN 未放通 / 中继缺失 / Option 82 问题
└─ 关联成功立刻断开 → PMF/11r 兼容性 / 密钥不匹配 / 重复 MAC（私有 MAC 冲突）
```

</div>

### Fault Tree Two: Connects but Slow (Performance Problems) · 故障树二：能连上但慢（性能问题）

```
Look at three numbers first: airtime utilisation, retry rate, clients per AP
├─ airtime > 70% with low retries → insufficient capacity (add APs / reduce channel width / rate limit / suppress multicast)
├─ High airtime + high retries (> 20%) → interference or weak-signal clients
│   ├─ Second-strongest AP within 5 dB of the primary → CCI (channel planning problem)
│   ├─ Clients below −80 dBm present → weak-signal black hole (MIN RSSI + disable low rates)
│   └─ Non-Wi-Fi energy in the spectrum plot → external interferer (microwave/camera/radar/DECT)
├─ Low airtime but users are still slow → not on the wireless side
│   ├─ Uplink/aggregation saturated → check switch interface utilisation
│   ├─ WAN/egress congestion → check the egress and QoS
│   └─ Application/DNS/authentication latency → check end to end
└─ Only one class of application is slow → QoS not trusted/not configured (check whether DSCP is reset at the first hop)
```

<div class="zh" markdown="1">

```
先看三个数：airtime 利用率、重传率、每 AP 客户端数
├─ airtime > 70% 且重传低 → 容量不足（加 AP / 降信道宽度 / 限速 / 抑制组播）
├─ airtime 高 + 重传高（>20%）→ 干扰或弱信号客户端
│   ├─ 第二强 AP 与主 AP 差值 < 5 dB → CCI（信道规划问题）
│   ├─ 存在 -80 dBm 以下客户端 → 弱信号黑洞（MIN RSSI + 禁低速率）
│   └─ 频谱图有非 Wi-Fi 能量 → 外部干扰源（微波/摄像头/雷达/DECT）
├─ airtime 低但用户仍慢 → 不在无线侧
│   ├─ 上行链路/汇聚打满 → 查交换机接口利用率
│   ├─ WAN/出口拥塞 → 查出口与 QoS
│   └─ 应用/DNS/认证时延 → 查端到端
└─ 只有某类业务慢 → QoS 未信任/未配对（查第一个跳的 DSCP 是否被重置）
```

</div>

### Fault Tree Three: Sessions Drop While Roaming · 故障树三：漫游时断流

```
① Capture packets: after the roam, is a full 802.1X run repeated? → Yes: PMK caching / 11r is not working
② Check RSSI on both sides of the roam point → one side < −75 dBm: insufficient coverage overlap
③ Check for ping-pong → the two APs within 3 dB and oscillating around the threshold (add hysteresis)
④ Check whether cross-controller roams share the Mobility Group/Domain and identical SSID security
⑤ Check whether the IP changes after the roam → cross-subnet with no Anchor: sessions must break
```

<div class="zh" markdown="1">

```
① 抓包看漫游后是否重做完整 802.1X → 是：PMK 缓存/11r 未生效
② 看漫游点的两侧 RSSI → 一侧 < -75 dBm：覆盖重叠不足
③ 看是否 ping-pong → 两 AP 差值 < 3 dB 且阈值附近震荡（加滞回）
④ 看跨控制器是否同 Mobility Group/Domain、SSID 安全是否一致
⑤ 看漫游后 IP 是否变化 → 跨子网且无 Anchor：会话必然断
```

</div>

### Fault Tree Four: Authentication Problems (the most common and the most time-consuming) · 故障树四：认证问题（最常见，也最花时间）

```
Association failure / authentication timeout
├─ RADIUS unreachable (network/ACL/ports 1812-1813) → capture packets: is there any response to Access-Request?
├─ RADIUS reachable but timing out → server overloaded / slow certificate chain validation / slow LDAP backend
├─ Some users fail → domain account/password/certificate issues; or one RADIUS node has failed (dead-time not enabled)
├─ All users suddenly fail → expired certificate (most common) / changed shared secret / server clock drift
└─ Authentication succeeds but the wrong VLAN is assigned → wrong RADIUS attribute (Tunnel-Private-Group-ID) / the WLC interface does not exist
```

<div class="zh" markdown="1">

```
关联失败 / 认证超时
├─ RADIUS 不可达（网络/ACL/端口 1812-1813）→ 抓包看 Access-Request 有无响应
├─ RADIUS 可达但超时 → 服务器过载 / 证书链校验慢 / LDAP 后端慢
├─ 部分用户失败 → 域账号/密码/证书问题；或某台 RADIUS 节点故障（dead-time 未启用）
├─ 全部用户突然失败 → 证书过期（最常见）/ 共享密钥被改 / 服务器时间漂移
└─ 认证成功但进错 VLAN → RADIUS 属性（Tunnel-Private-Group-ID）错误 / WLC 接口不存在
```

</div>

### Command and Data Map (collect data by layer while troubleshooting) · 命令与数据地图（排障时按层取数）

| Layer | Data source | Command/action |
|---|---|---|
| **RF** | Controller | `show ap stats` (airtime, retries, client count), `show ap auto-rf` (channel/power), `show ap spectrum` |
| **RF (client perspective)** | Client / packet capture | RSSI/SNR records, over-the-air capture (Monitor/Sniffer mode AP) |
| **Controller** | WLC | `show ap summary`, `show ap join stats`, `show client detail <mac>`, `show wlan summary` |
| **Wired side** | Switch | `show interface`, `show power inline`, `show mac address-table`, `show ip dhcp snooping binding` |
| **IP services** | DHCP/DNS | Pool utilisation, lease table, Option 43, DNS record resolution |
| **Authentication** | RADIUS/ISE | Authentication logs (failure reason codes), `show radius statistics`, certificate expiry dates |
| **Policy** | Firewall/ACL | Session table, deny logs, MTU/fragmentation counters |

<div class="zh" markdown="1">

| 层 | 数据来源 | 命令/操作 |
|---|---|---|
| **RF** | 控制器 | `show ap stats`（airtime、重传、客户端数）、`show ap auto-rf`（信道/功率）、`show ap spectrum` |
| **RF（客户端视角）** | 客户端/抓包 | RSSI/SNR 记录、空口抓包（Monitor/Sniffer 模式 AP） |
| **控制器** | WLC | `show ap summary`、`show ap join stats`、`show client detail <mac>`、`show wlan summary` |
| **有线侧** | 交换机 | `show interface`、`show power inline`、`show mac address-table`、`show ip dhcp snooping binding` |
| **IP 服务** | DHCP/DNS | 池利用率、租约表、Option 43、DNS 记录解析 |
| **认证** | RADIUS/ISE | 认证日志（失败原因码）、`show radius statistics`、证书到期时间 |
| **策略** | 防火墙/ACL | 会话表、拒绝日志、MTU/分片计数 |

</div>

### The Five Disciplines of Troubleshooting · 排障的五条纪律

1. **Establish the blast radius first**: one person / one floor / the whole campus — the radius maps to the layer (an individual → endpoint or credentials; a floor → AP or switch; the whole campus → WLC/RADIUS/DHCP).
2. **Look at the timeline first**: "when did it start" often hands you the root cause directly (just upgraded? just changed policy? just finished renovation? certificate just expired?).
3. **Never "try it and see" in production**: wireless parameters (power/channel/11r) have an enormous blast radius — validate on a small AP Group first.
4. **Packet capture beats speculation**: an over-the-air capture plus a switch-side capture distinguishes "lost on air" from "lost on wire" in one shot.
5. **Write every fix back into the baseline**: put root causes into monitoring alarms and acceptance cases, otherwise the same fault replays at the next site.

<div class="zh" markdown="1">

1. **先确认影响面**：一个人 / 一层楼 / 全园区 —— 影响面对应层次（个人 → 终端/凭据；一层 → AP/交换机；全园区 → WLC/RADIUS/DHCP）。
2. **先看时间线**："什么时候开始的" 往往直接给出根因（刚升级？刚改策略？刚装修？证书刚过期？）。
3. **不要在生产上做"试试看"**：无线参数（功率/信道/11r）的改动影响面极大，先在小范围 AP Group 验证。
4. **抓包胜过猜测**：空口抓包 + 交换机侧抓包，能一次性区分"空口丢"还是"有线丢"。
5. **修完要写进基线**：把根因写进监控告警与验收用例，否则同一个故障会在下一个站点重演。

</div>

---

## Real-World Case Studies (Twelve Real Scenarios) · 实战案例（12 个真实场景）

> The twelve cases below cover the six typical battlefields of wireless design: **high-density capacity (1, 11), mobility and roaming (2, 8, 9), availability and degradation (3), engineering and go-live (4, 10), security and compatibility (5, 12), multicast and special loads (6), client behaviour (7)**. The way to read each case is: look at "scenario and symptoms", decide the root cause yourself, then check whether "the investigation" matches yours — that is the core training method of scenario drills.

<div class="zh" markdown="1">

> 以下 12 个案例覆盖无线设计的六类典型战场：**高密度容量（一、十一）、移动性与漫游（二、八、九）、可用性与降级（三）、工程与上线（四、十）、安全与兼容（五、十二）、组播与特殊负载（六）、终端行为（七）**。每个案例的读法是：先看"场景与现象"，自己判断根因，再看"排查过程"对不对得上 —— 这是情景演练的核心训练方式。

</div>

### Case 1: A Thousand-Person Launch Event — "We Installed Enough Wi-Fi 6 APs, But Everyone Is Spinning" · 🔥 案例一：千人发布会，"Wi-Fi 6 AP 装够了，但所有人都在转圈"

**Scenario**: a 1,200 m² venue, 24 dual-band Wi-Fi 6 APs, 800 people on site. During testing it was "20 Mbps per person"; once the event started nobody could open a web page and the live streams froze.

<div class="zh" markdown="1">

**场景**：会场 1,200 m²，部署 24 台 Wi-Fi 6 AP，双频。现场 800 人。测试时"每人 20 Mbps"，实际开始后所有人网页打不开、直播卡死。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. The controller showed **airtime utilisation above 95%**, with 33 clients per AP on average (which looks unremarkable)
2. Channel plan check: **everything at 80 MHz** → only 6 usable channels in 5 GHz, so 24 APs reuse heavily
3. Power check: **automatic RRM had pushed power to the 20 dBm maximum** → each AP covered 40 m+, so the entire venue could hear every AP
4. Low-rate check: 1/2/5.5/11 Mbps **not disabled** → some old and weak-signal endpoints transmitted at 6 Mbps, and one small frame consumed 20× the airtime of a high-rate frame
5. Multicast/broadcast: iPads were mirroring (mDNS/Bonjour), **flooding multicast at the lowest rate**

<div class="zh" markdown="1">

1. 控制器显示 **airtime 利用率 95%+**，每 AP 平均 33 客户端（看似不高）
2. 信道规划检查：**全部 80 MHz** → 5 GHz 只有 6 个可用信道，24 台 AP 严重复用
3. 功率检查：**自动 RRM 把功率拉到最大 20 dBm** → 每台 AP 覆盖半径 40 m+，整个会场互相听得见
4. 低速检查：1/2/5.5/11 Mbps **未禁用** → 部分老终端与弱信号终端以 6 Mbps 发送，单个小包占用 airtime 是高速率的 20 倍以上
5. 组播/广播：现场有 iPad 投屏（mDNS/Bonjour）**大量组播泛洪，且以最低速率发送**

</div>

**Root cause**: this was not "not enough APs", it was **spectrum saturated by our own design**. Twenty-four 80 MHz APs in one venue deliver far less usable capacity than twenty-four 20 MHz APs.

<div class="zh" markdown="1">

**根因**：这不是"AP 不够"，而是**频谱被自己占满**。24 台 80 MHz AP 在一个会场里，实际可用容量远低于 24 台 20 MHz AP。

</div>

**Fixes (ordered by impact)**:

<div class="zh" markdown="1">

**修复（按效果排序）**：

</div>

| Action | Effect |
|------|------|
| **80 MHz → 20 MHz** | Usable channels go from 6 to 25 and CCI drops sharply (lower per-AP rate, but higher total capacity) |
| **Disable 1/2/5.5/11 Mbps, minimum 12 Mbps** | Eliminates the low-rate "airtime black hole" |
| **Fix power at 5–8 dBm** | Smaller cells, more even client distribution, more sensible roaming |
| **Enable multicast-to-unicast + broadcast suppression** | mDNS/mirroring no longer floods |
| **MIN RSSI −67 dBm** | Forces weak clients to roam or disconnect |
| **Band Steering** | Pushes dual-band endpoints onto 5 GHz |

<div class="zh" markdown="1">

| 动作 | 效果 |
|------|------|
| **80 MHz → 20 MHz** | 可用信道从 6 增至 25，CCI 大幅下降（单 AP 速率降，但总容量升） |
| **禁用 1/2/5.5/11 Mbps，最小 12 Mbps** | 消灭低速"airtime 黑洞" |
| **功率固定 5–8 dBm** | 蜂窝变小、客户端更均匀分布、漫游更合理 |
| **开启组播转单播 + 广播抑制** | mDNS/投屏不再泛洪 |
| **MIN RSSI -67 dBm** | 强制弱信号客户端漫游或断开 |
| **Band Steering** | 把双频终端推上 5 GHz |

</div>

**Result**: airtime utilisation fell from 95% to 55%, and per-user available throughput rose from under 1 Mbps to 6–8 Mbps.

<div class="zh" markdown="1">

**结果**：airtime 利用率从 95% 降到 55%，人均可用速率从 < 1 Mbps 升到 6–8 Mbps。

</div>

**Lesson**: **the bottleneck in high-density scenarios is always airtime, never the AP count.** Channel width, power, disabled low rates and multicast suppression together deliver far more than "ten more APs".

<div class="zh" markdown="1">

**教训**：**高密度场景的瓶颈永远是 airtime，不是 AP 数量。** 信道宽度、功率、低速禁用、组播抑制，这四项加起来的效果远大于"再多装 10 台 AP"。

</div>

### Case 2: Wi-Fi Voice — "It Drops for 2 Seconds at the Stairwell" · 🔥 案例二：Wi-Fi 语音"走到楼梯口就断 2 秒"

**Scenario**: hospital mobile rounds plus wireless handsets, 600 endpoints. Users report that calls lose audio for 1–3 seconds while walking in corridors and sometimes drop outright. Quality is excellent when standing still.

<div class="zh" markdown="1">

**场景**：医院移动查房 + 无线话机，共 600 台终端。用户反馈：在走廊走动时通话丢音 1–3 秒，有时直接掉话。静止时质量很好。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. Packet capture: at roam time the client sent a Reassociation and then **performed a full four-way handshake plus EAP re-authentication**, interrupting for 380 ms
2. Controller check: **PMK caching not enabled, 802.11r not enabled**, and 802.11k/v also off
3. Coverage check: corridor AP spacing 25 m; **one side of the roam point was already at −78 dBm before the switch happened** (insufficient overlap)
4. Mobility domain check: the two floors were on **different controllers**, and **no Mobility Group existed** (roaming had only ever been tested within one controller)

<div class="zh" markdown="1">

1. 抓包：漫游时客户端发 Reassociation 后，**执行了完整 4 次握手 + EAP 重认证**，中断 380 ms
2. 控制器检查：**PMK 缓存未启用、802.11r 未开启**、802.11k/v 也未开启
3. 覆盖检查：走廊 AP 间距 25 m，**漫游点一侧 AP 已 -78 dBm 才开始切换**（重叠不足）
4. 移动域检查：两层楼属于**不同控制器**，且 **Mobility Group 未建**（只做了同控制器内漫游测试）

</div>

**Root cause**: three problems superposed — ① terrible signal at the roam point (a coverage design problem); ② cross-controller PMK not synchronised (an architecture problem); ③ 802.11r not enabled (a protocol configuration problem).

<div class="zh" markdown="1">

**根因**：三个问题叠加 —— ①漫游点信号太差（覆盖设计问题）；②跨控制器 PMK 未同步（架构问题）；③未启用 802.11r（协议配置问题）。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Action | Implementation |
|------|------|
| **Add APs / lower power so overlap reaches 15–20%** | Both APs at the roam point differ by ≤ 5 dB and both exceed −67 dBm |
| **Build a Mobility Group + the same Mobility Domain** | Cross-controller PMK synchronisation |
| **Enable 802.11k + 802.11v + Adaptive 802.11r** | FT mandatory on the voice SSID |
| **Enable WMM + voice CAC (75% reservation)** | Stops voice being squeezed under congestion |
| **Disable low rates (minimum 12 Mbps)** | Reduces wasted airtime |

<div class="zh" markdown="1">

| 动作 | 落地 |
|------|------|
| **加 AP / 调低功率，重叠提到 15–20%** | 漫游点两 AP 差值 ≤ 5 dB，均 > -67 dBm |
| **建 Mobility Group + 同 Mobility Domain** | 跨控制器 PMK 同步 |
| **开启 802.11k + 802.11v + Adaptive 802.11r** | 语音 SSID 强制 FT |
| **开启 WMM + 语音 CAC（75% 预留）** | 防拥塞时语音被挤 |
| **禁用低速率（最小 12 Mbps）** | 减少 airtime 浪费 |

</div>

**Result**: roaming interruption fell from 380 ms to 35 ms, and voice MOS rose from 3.2 to 4.2.

<div class="zh" markdown="1">

**结果**：漫游中断从 380 ms 降到 35 ms，语音 MOS 从 3.2 提升到 4.2。

</div>

**Lesson**: **"slow roaming" is never a single cause.** Coverage (RF layer) + mobility domain (architecture layer) + fast roaming (protocol layer) + QoS (policy layer) must all be designed together. Configuring 802.11r without fixing coverage is like putting a great navigation system in a car on a broken road.

<div class="zh" markdown="1">

**教训**：**"漫游慢"从来不是单一原因**。覆盖（RF 层）+ 移动域（架构层）+ 快速漫游（协议层）+ QoS（策略层）四层必须一起设计。只配 802.11r 而不改覆盖，等于给一条烂路装了个好导航。

</div>

### Case 3: Branch WAN Down for 4 Hours — "Next Morning Nobody Could Connect" · 🔥 案例三：分支 WAN 断链 4 小时，第二天全员连不上 Wi-Fi

**Scenario**: 30 retail stores, a centralized WLC at headquarters, APs using FlexConnect with local switching. A fibre cut took one store's WAN down for 4 hours.

<div class="zh" markdown="1">

**场景**：30 个零售门店，集中式 WLC 在总部，AP 用 FlexConnect 本地转发。某门店光缆被挖断，WAN 中断 4 小时。

</div>

**Symptoms**: on the day of the outage, already-associated clients **kept working normally** (local switching was doing its job). But the next morning at opening, **every employee and every POS terminal failed to connect**, POS could not transact, and the store was closed for half a day.

<div class="zh" markdown="1">

**现象**：断链当天，已有客户端**仍能正常上网**（本地转发生效）。但第二天开业时，**所有员工和 POS 都连不上 Wi-Fi**，POS 无法交易，门店停业半天。

</div>

**Root cause**:

<div class="zh" markdown="1">

**根因**：

</div>

1. FlexConnect had **local switching** configured, but **local authentication was not enabled** → with the WAN down, new associations could not complete 802.1X
2. **DHCP only existed at headquarters**, with none locally → new clients could not obtain an IP
3. The AP's `flexconnect` configuration had **no pre-staged local authentication credentials** (`flexconnect local-auth` plus users/PSK)

<div class="zh" markdown="1">

1. FlexConnect 只配了**本地转发**，但**未开本地认证**（Local Authentication）→ WAN 断链时新关联无法完成 802.1X
2. **DHCP 只在总部**，本地没有 DHCP → 新客户端拿不到 IP
3. AP 的 `flexconnect` 配置里**没有预置本地认证凭据**（`flexconnect local-auth` + 用户/PSK）

</div>

> The frightening part of this combination is that **the failure is not immediate**. Everything is fine at the moment the WAN drops; the problem only surfaces at "the next client re-association" — possibly hours later, possibly the next morning.

<div class="zh" markdown="1">

> 这一组合的可怕之处在于：**故障不是立刻发生的**。WAN 断的当下一切正常，问题要等到"客户端下一次重新关联"才暴露 —— 可能是几小时后，可能是第二天早上。

</div>

**Fixes (the standard branch configuration template)**:

<div class="zh" markdown="1">

**修复（分支标准配置模板）**：

</div>

```cfg
! WLC side: enable FlexConnect local switching + local auth on the WLAN
wlan GUEST-STORE 1 STORE
 flexconnect local-switching
 flexconnect local-auth
 no flexconnect central-dhcp
 accounting-list local-acct

! AP side: VLAN mapping
ap name STORE-AP-01
 flexconnect vlan-name DATA vlan-id 110
 flexconnect vlan-name POS  vlan-id 120

! Branch switch: local DHCP (the critical piece)
ip dhcp pool STORE-DATA
 network 10.20.10.0 255.255.255.0
 default-router 10.20.10.1
 dns-server 10.20.10.1
```

<div class="zh" markdown="1">

```cfg
! WLC 侧：WLAN 开启 FlexConnect 本地交换 + 本地认证
wlan GUEST-STORE 1 STORE
 flexconnect local-switching
 flexconnect local-auth
 no flexconnect central-dhcp
 accounting-list local-acct

! AP 侧：VLAN 映射
ap name STORE-AP-01
 flexconnect vlan-name DATA vlan-id 110
 flexconnect vlan-name POS  vlan-id 120

! 分支交换机：本地 DHCP（关键）
ip dhcp pool STORE-DATA
 network 10.20.10.0 255.255.255.0
 default-router 10.20.10.1
 dns-server 10.20.10.1
```

</div>

**The mandatory requirements list for branch wireless design**:

<div class="zh" markdown="1">

**分支无线设计的强制要求清单**：

</div>

| Requirement | Reason |
|------|------|
| Local DHCP (switch or local server) | New clients can still get an address when the WAN is down |
| Local authentication (Local Auth) or pre-staged PSK | Authentication works without RADIUS |
| Local DNS or a public DNS fallback | Name resolution no longer depends on headquarters |
| Local internet breakout | Cloud POS/SaaS remains reachable when the WAN is down |
| FlexConnect AP Group + pre-staged configuration | Centralized management with link-down autonomy |
| Link-down drills (quarterly) | Redundancy nobody has drilled is not redundancy |

<div class="zh" markdown="1">

| 要求 | 原因 |
|------|------|
| 本地 DHCP（交换机或本地服务器） | WAN 断链时新客户端仍能拿地址 |
| 本地认证（Local Auth）或预置 PSK | 无 RADIUS 也能认证 |
| 本地 DNS 或公共 DNS 兜底 | 域名解析不依赖总部 |
| 本地互联网出口（breakout） | WAN 断链仍可访问云 POS/SaaS |
| FlexConnect AP Group + 预置配置 | 集中管理、断链自治 |
| 断链演练（每季度） | 没人演练过的冗余等于没有冗余 |

</div>

**Lesson**: **FlexConnect only solves "data does not need to be backhauled"; it solves neither "authentication" nor "addressing".** Designs for sites with unreliable WAN must assume "the WAN can drop at any time, and a batch of new clients will come online while it is down".

<div class="zh" markdown="1">

**教训**：**FlexConnect 只解决"数据不回传"，不解决"认证与地址"**。WAN 不可靠站点的设计必须假设"WAN 随时会断、且断的时候会有一批新客户端上线"。

</div>

### Case 4: Forty APs in a New Building All Fail to Join the Controller · 🔥 案例四：新楼 40 台 AP 全部 join 不上控制器

**Scenario**: a new office building goes live and all 40 APs fail to join the WLC. The APs obtain IP addresses and can ping the WLC's management address, but they stay stuck in the `Join` stage.

<div class="zh" markdown="1">

**场景**：新办公楼启用，40 台 AP 全部无法加入 WLC。AP 能拿到 IP、能 ping 通 WLC 管理地址，但一直卡在 `Join` 阶段。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. `debug capwap client` on the AP: the control tunnel is established and then **times out immediately**
2. There is a firewall between the building and the data centre → policy check: **UDP 5246 was permitted in one direction only**
3. At the same time: **UDP 5247 (data) was not permitted**, and **ICMP was not permitted either (needed for PMTUD)**
4. Another batch of APs sat in a different subnet in the new building where **DHCP Option 43 was not configured**, so broadcast discovery failed

<div class="zh" markdown="1">

1. AP 上 `debug capwap client`：控制隧道建立后**立刻超时**
2. 中间有防火墙（新楼与数据中心之间）→ 检查策略：**UDP 5246 只放行了单向**
3. 同时发现：**UDP 5247（数据）未放行**、且**未放行 ICMP（PMTUD 需要）**
4. 另有一批 AP 在新楼的另一个网段，**DHCP Option 43 未配置**，靠广播发现失败

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Item | Configuration |
|------|------|
| Firewall | Bidirectional UDP 5246 (control) and 5247 (data); ICMP type 3 code 4 |
| DHCP | `option 43 hex f1040a0a0a0a` (hex IP list) or a DNS pointer |
| MTU | Path MTU between AP and WLC ≥ 1550 (avoid CAPWAP fragmentation) |
| Certificates/time | NTP synchronisation (DTLS certificate validation depends on time) |

<div class="zh" markdown="1">

| 项目 | 配置 |
|------|------|
| 防火墙 | 双向 UDP 5246（控制）、5247（数据）；ICMP type 3 code 4 |
| DHCP | `option 43 hex f1040a0a0a0a`（十六进制 IP 列表）或 DNS 指向 |
| MTU | AP 与 WLC 之间路径 MTU ≥ 1550（避免 CAPWAP 分片） |
| 证书/时间 | NTP 同步（DTLS 证书校验依赖时间） |

</div>

**Lesson**: **AP onboarding is a cross-domain problem**: DHCP (network layer) → discovery (application layer) → firewall (security layer) → MTU (link layer) → certificates (time). Troubleshooting must verify along that chain segment by segment instead of repeatedly hunting for a cause on the controller.

<div class="zh" markdown="1">

**教训**：**AP 上线是"跨域"问题**：DHCP（网络层）→ 发现（应用层）→ 防火墙（安全层）→ MTU（链路层）→ 证书（时间）。排障必须按这个链条逐段验证，而不是反复在控制器上找原因。

</div>

### Case 5: After the WPA3 Upgrade, Half the Old Endpoints Go from "Full Bars" to "Cannot See the SSID" · 🔥 案例五：升级 WPA3 后，一半老终端从"信号满格"变成"看不到 SSID"

**Scenario**: to satisfy compliance, the enterprise SSID was moved from WPA2-Enterprise to **WPA3-Enterprise (192-bit)**. After the upgrade, a batch of old laptops, some medical devices and barcode scanners could not connect at all.

<div class="zh" markdown="1">

**场景**：为满足合规，把企业 SSID 从 WPA2-Enterprise 改为 **WPA3-Enterprise（192 位）**。升级后，一批老笔记本、部分医疗设备、扫码枪完全无法连接。

</div>

**Root cause** (three layers superposed):

<div class="zh" markdown="1">

**根因**（三层原因叠加）：

</div>

| Layer | Cause |
|----|------|
| **Endpoint** | Old NICs do not support WPA3, and some do not support PMF (802.11w) |
| **SSID configuration** | Switched straight to pure WPA3, **with no transition mode** |
| **6 GHz** | 6 GHz was enabled at the same time; since 6 GHz mandates WPA3 + PMF, old endpoints were affected by policy even on the 5 GHz instance of the same SSID |

<div class="zh" markdown="1">

| 层 | 原因 |
|----|------|
| **终端** | 老网卡不支持 WPA3，部分不支持 PMF（802.11w） |
| **SSID 配置** | 直接改成纯 WPA3，**未使用过渡模式** |
| **6 GHz** | 同时开启 6 GHz，而 6 GHz 强制 WPA3 + PMF，老终端连 5 GHz 的同一 SSID 也被策略影响 |

</div>

**Remediation strategy (per-SSID, phased migration)**:

<div class="zh" markdown="1">

**修复策略（分 SSID 分阶段迁移）**：

</div>

| SSID | Security policy | Endpoints carried |
|------|---------|---------|
| `CORP-WPA3` | WPA3-Enterprise (192-bit optional) | Managed new devices (domain PCs, new phones) |
| `CORP-TRANS` | **WPA2/WPA3 transition mode + PMF optional** | Un-upgraded legacy devices (6–12 month transition) |
| `IOT` | WPA2-PSK + iPSK + separate VLAN | Medical devices, scanners, printers |
| `GUEST` | OWE or portal | Visitors |

<div class="zh" markdown="1">

| SSID | 安全策略 | 承载终端 |
|------|---------|---------|
| `CORP-WPA3` | WPA3-Enterprise（可选 192 位） | 受管新设备（域 PC、新手机） |
| `CORP-TRANS` | **WPA2/WPA3 过渡模式 + PMF 可选** | 未升级的老设备（过渡期 6–12 个月） |
| `IOT` | WPA2-PSK + iPSK + 独立 VLAN | 医疗设备、扫码枪、打印机 |
| `GUEST` | OWE 或 Portal | 访客 |

</div>

**Lesson**: **security upgrades must be batched according to an endpoint capability matrix.** A compliance requirement to "use WPA3" can usually be interpreted as "new SSIDs use WPA3 and legacy devices get a transition period", but cutting the only SSID over to WPA3 in one step guarantees a large-scale incident. A design document should contain an **endpoint compatibility list** and a **rollback plan**.

<div class="zh" markdown="1">

**教训**：**安全升级必须按"终端能力矩阵"分批**。合规要求"用 WPA3"往往可以解释为"新建 SSID 用 WPA3、存量设备有过渡期"，但直接把唯一 SSID 切成 WPA3 一定会引发大面积事故。设计文档里应该有**终端兼容性清单**与**回滚方案**。

</div>

### Case 6: One Factory's Multicast Brought the Entire Shop-Floor Wi-Fi to Its Knees · 🔥 案例六：一家工厂的组播把整个车间的 Wi-Fi 打瘫

**Scenario**: a factory carries AGV scheduling and handheld scanning over Wi-Fi. Every morning after the 8 a.m. shift start, AGVs lose connectivity frequently and scanning latency is high.

<div class="zh" markdown="1">

**场景**：工厂用 Wi-Fi 承载 AGV 调度与手持扫码。每天早上 8 点开工后，AGV 频繁失联、扫码延迟高。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. The controller showed airtime utilisation **jumping from 20% to 85% after 8 a.m.**
2. Packet capture revealed **large volumes of multicast** (camera previews, device discovery protocols SSDP/mDNS)
3. The key mechanism: **multicast frames must be sent at the lowest mandatory rate** (6 Mbps by default) and have **no ACK and no retransmission**, so one multicast frame consumes tens of times the airtime of a unicast frame
4. The shop floor had three camera previews permanently open, generating hundreds of multicast packets per second

<div class="zh" markdown="1">

1. 控制器显示 airtime 利用率 8 点后**从 20% 跳到 85%**
2. 抓包发现**大量组播包**（视频监控预览、设备发现协议 SSDP/mDNS）
3. 关键机制：**组播帧必须以最低强制速率发送**（默认 6 Mbps），且**没有 ACK、没有重传**，一帧组播占用 airtime 是单播的数十倍
4. 车间有 3 路摄像头预览常开，每秒数百个组播包

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Action | Explanation |
|------|------|
| **Multicast-to-Unicast** | One copy per client, at a high rate with retransmissions |
| **IGMP Snooping** | The wired side only forwards multicast to ports that actually have subscribers |
| **Suppress unnecessary mDNS/SSDP flooding** | Or proxy it with an mDNS gateway |
| **Raise the multicast rate** (if multicast must be retained) | Set 24 Mbps to cut the airtime cost |
| **Deploy AGVs and cameras in separate zones** | Different SSIDs/APs isolate the airtime competition |

<div class="zh" markdown="1">

| 动作 | 说明 |
|------|------|
| **组播转单播（Multicast-to-Unicast）** | 每个客户端单独发一份，可用高速率 + 重传 |
| **IGMP Snooping** | 有线侧只把组播送到真正有订阅者的端口 |
| **关闭不必要的 mDNS/SSDP 泛洪** | 或用 mDNS gateway 代理 |
| **提高组播速率**（若必须保留组播） | 设为 24 Mbps，减少 airtime 占用 |
| **AGV 与摄像头分区部署** | 不同 SSID/不同 AP，隔离 airtime 竞争 |

</div>

**Lesson**: **multicast is the most invisible capacity killer in wireless.** The design question you must ask is: "how many multicast/broadcast sources exist in this network?" (video surveillance, screen mirroring, mDNS, DHCP, ARP, industrial protocol discovery — all count). Enabling multicast suppression and unicast conversion by default is cheap insurance.

<div class="zh" markdown="1">

**教训**：**组播是无线最隐蔽的容量杀手**。设计时必须问："这个网络里有多少组播/广播源？"（视频监控、投屏、mDNS、DHCP、ARP、工业协议发现 —— 全部算）。默认开启组播抑制与转单播，是低成本的保险。

</div>

### Case 7: The Client "Sticks" to 2.4 GHz and Will Not Leave · 🔥 案例七：客户端"粘"在 2.4 GHz 不走

**Scenario**: office users report "fast at my desk, slow at the meeting room across the floor". Investigation shows the client stays associated to the **2.4 GHz radio of an AP back at the desk**, with signal already at −79 dBm, refusing to roam to the 5 GHz AP right next to the meeting room.

<div class="zh" markdown="1">

**场景**：办公室用户反馈"在工位上网很快，去另一头会议室就很慢"。检查发现该客户端一直关联在**远处工位的 2.4 GHz 射频**上，信号已 -79 dBm，却不肯漫游到会议室旁边 5 GHz 的 AP。

</div>

**Root cause** (four mechanisms together):

<div class="zh" markdown="1">

**根因**（四个机制共同作用）：

</div>

1. **Band Steering not enabled** → the client prefers 2.4 GHz (probe responses come back faster and the signal looks stronger)
2. **MIN RSSI not set** → staying associated at −79 dBm is still permitted
3. **The client's own roaming algorithm is conservative** (many endpoints only scan when loss becomes severe)
4. **Low rates not disabled on 2.4 GHz** → the client transmits at 6 Mbps, consuming a great deal of airtime

<div class="zh" markdown="1">

1. **Band Steering 未启用** → 客户端优先选 2.4 GHz（探测响应更快、信号看似更强）
2. **MIN RSSI 未设置** → -79 dBm 仍被允许保持关联
3. **客户端自身漫游算法保守**（很多终端只在丢包严重时才扫描）
4. **2.4 GHz 未禁用低速率** → 该客户端以 6 Mbps 发送，占用了大量 airtime

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

```cfg
! 1. Band steering + minimum rate
ap dot11 24ghz rate RATE_1 disable
ap dot11 24ghz rate RATE_2 disable
ap dot11 24ghz rate RATE_5.5 disable
ap dot11 24ghz rate RATE_11 disable
ap dot11 24ghz band-steering

! 2. MIN RSSI (RF Profile)
ap dot11 5ghz rrm profile RF-HD
 min-rssi -67
! 3. 802.11v BSS Transition lets the AP proactively "suggest" that the client leave
```

<div class="zh" markdown="1">

```cfg
! 1. 频段引导 + 最小速率
ap dot11 24ghz rate RATE_1 disable
ap dot11 24ghz rate RATE_2 disable
ap dot11 24ghz rate RATE_5.5 disable
ap dot11 24ghz rate RATE_11 disable
ap dot11 24ghz band-steering

! 2. MIN RSSI（RF Profile）
ap dot11 5ghz rrm profile RF-HD
 min-rssi -67
! 3. 802.11v BSS Transition 让 AP 主动"建议"客户端离开
```

</div>

**Effect**: the share of dual-band endpoints associated on 5 GHz rose from 55% to 92%, and network-wide airtime utilisation dropped 15 percentage points.

<div class="zh" markdown="1">

**效果**：双频终端在 5 GHz 关联比例从 55% 提升到 92%，全网 airtime 利用率下降 15 个百分点。

</div>

**Lesson**: **"sticky clients" are a design gap, not an endpoint defect.** Configure band steering, MIN RSSI, 802.11v and disabled low rates together and stickiness largely disappears. Conversely, band steering without MIN RSSI merely "pushes" the client onto 5 GHz, where it falls back again because the signal is weak.

<div class="zh" markdown="1">

**教训**：**"粘滞客户端"是设计缺失，不是终端缺陷**。频段引导、MIN RSSI、802.11v、禁用低速率这四项配好，粘滞问题基本消失。反过来，只配 band steering 不配 MIN RSSI，客户端被"推"上 5 GHz 后仍会因信号弱而掉回来。

</div>

### Case 8: A High-Bay Warehouse — "Once the Racking Went Up to 12 Metres, Forklifts Dropped Off Mid-Aisle" · 🔥 案例八：立体仓库——"货架一装到 12 米，叉车走到通道中间就掉线"

**Scenario**: a new automated high-bay warehouse, 40 m × 120 m, racking 12 m high, six aisles, all-steel racking with a metal roof. Sixty forklift-mounted terminals (2.4 GHz single-band scanners + Wi-Fi tablets), with a business requirement of "scan and transmit instantly; a dropped link stops the line".

<div class="zh" markdown="1">

**场景**：新建自动化立体仓库，40 m × 120 m，货架高 12 m、6 条通道，全部钢制货架 + 金属顶棚。60 台叉车车载终端（2.4 GHz 单频扫码枪 + Wi-Fi 平板），业务要求"扫码即传，掉线即停线"。

</div>

**Symptoms**:

<div class="zh" markdown="1">

**现象**：

</div>

- Signal is excellent at the aisle entrance (−52 dBm), but **drops to −82 dBm mid-aisle**, and the scanners report "network timeout"
- Forklifts reconnect constantly when turning between aisles, 2–5 s each time
- APs were mounted in the 12 m ceiling and the coverage plot showed "all green"

<div class="zh" markdown="1">

- 通道入口信号很好（-52 dBm），**走到通道中段掉到 -82 dBm**，扫码枪报"网络超时"
- 叉车在通道间转向时频繁重连，每次 2–5 s
- AP 装在 12 m 高吊顶，覆盖图上"全绿"

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. **On-site survey (AP-on-a-stick)**: re-measured with the AP lowered to 4 m; mid-aisle improved from −82 dBm to −68 dBm → **mounting height was the primary root cause**
2. **Material verification**: the racking is densely packed steel (with goods it approximates a solid metal wall); measured attenuation through a single racking row was **18–25 dB**, not the 8 dB assumed on the drawings
3. **Channel check**: 2.4 GHz used only 1/6/11, and six aisles with dual rows of APs gave 12 coverage zones — **severe co-channel reuse**
4. **Endpoint side**: the scanners are 802.11n single-band single-stream, **supporting 2.4 GHz only** and not supporting 802.11r
5. **Roaming check**: forklifts travel at 1.5 m/s along 120 m aisles, so **one pass crosses 6–8 APs**, each roam taking 2.5 s → 8 × 2.5 s = 20 s of service interruption per trip

<div class="zh" markdown="1">

1. **现场勘测（AP-on-a-stick）**：把 AP 降到 4 m 高度重测，通道中段从 -82 dBm 改善到 -68 dBm → **安装高度是第一根因**
2. **材质确认**：货架是密排钢制（含货物后近似实心金属墙），单排货架衰减实测 **18–25 dB**，不是图纸假设的 8 dB
3. **信道检查**：2.4 GHz 只用 1/6/11，6 条通道 + 双排 AP = 12 个覆盖区，**严重同频复用**
4. **终端侧**：扫码枪是 802.11n 单频单流，**只支持 2.4 GHz**，且不支持 802.11r
5. **漫游检查**：叉车速度 1.5 m/s，通道长 120 m，**一次穿行要跨 6–8 个 AP**，每次漫游 2.5 s → 8 次 × 2.5 s = 20 s/趟的业务中断

</div>

**Root cause** (four superposed):

<div class="zh" markdown="1">

**根因**（四个叠加）：

</div>

| Root cause | Nature |
|---|---|
| APs mounted in a 12 m ceiling, too far from terminals and shielded by racking | Installation/RF design error |
| Racking attenuation badly underestimated (assumed 8 dB, actually 20 dB) | Survey assumption error |
| Terminals support 2.4 GHz only, so 14 channels cannot serve 12 coverage zones | Endpoint capability constraint |
| Terminals do not support 11r/PMK caching, making roaming extremely expensive | Protocol capability constraint |

<div class="zh" markdown="1">

| 根因 | 性质 |
|---|---|
| AP 装在 12 m 吊顶，距离终端过远且被货架遮挡 | 安装/RF 设计错误 |
| 货架衰减被严重低估（假设 8 dB，实际 20 dB） | 勘测假设错误 |
| 末端只支持 2.4 GHz 单频，14 个信道无法支撑 12 个覆盖区 | 终端能力约束 |
| 终端不支持 11r/PMK 缓存，漫游代价极高 | 协议能力约束 |

</div>

**The solution (a redesign, not parameter tuning)**:

<div class="zh" markdown="1">

**方案（重新设计，不是调参）**：

</div>

```
① Lower the APs: from the 12 m ceiling to aisle side walls at 4–5 m, using directional antennas strung along the aisle
   → 3 APs per aisle (40 m spacing), 60° directional coverage along the aisle axis
② Re-plan 2.4 GHz channels: the six aisles interleave 1/6/11, with same-channel APs at least 2 spans apart
③ Disable 2.4 GHz low rates (1/2/5.5/11 Mbps), minimum 12 Mbps
   → "cannot connect" at the edge beats "connects and eats airtime"
④ Upgrade forklift terminals to dual-band with 11k/11v support (write it into the procurement terms)
   → dedicated 5 GHz channels, separated from the 2.4 GHz scanners
⑤ Add three "roaming anchor" APs at critical points (aisle entrances) to reduce switch counts while turning
⑥ Add local caching and resumable transmission on the application side (scanning does not depend on an immediate cloud acknowledgement)
```

<div class="zh" markdown="1">

```
① AP 下沉：从吊顶 12 m 改到通道侧壁 4–5 m，用定向天线沿通道"串糖葫芦"
   → 每通道 3 台 AP（间距 40 m），定向 60° 沿通道轴向覆盖
② 2.4 GHz 信道重规划：6 条通道交错使用 1/6/11，同通道 AP 间隔 ≥ 2 跨
③ 关闭 2.4 GHz 低速率（1/2/5.5/11 Mbps），最小 12 Mbps
   → 边缘区域"连不上"好过"连上但占 airtime"
④ 叉车终端升级到双频 + 支持 11k/11v（供应商准入条款写进采购）
   → 5 GHz 独享通道，与扫码枪 2.4 GHz 分离
⑤ 关键点位补 3 台"漫游锚点"AP（通道口），减少转向时的切换次数
⑥ 应用侧增加本地缓存与断点续传（扫码不依赖即时云端确认）
```

</div>

**Result**: mid-aisle RSSI −68 dBm, roaming interruption fell from 2.5 s to 180 ms (60 ms after the terminal upgrade), and the scan timeout rate fell from 7% to 0.2%.

<div class="zh" markdown="1">

**结果**：通道中段 RSSI -68 dBm，漫游中断从 2.5 s 降到 180 ms（终端升级后 60 ms），扫码超时率从 7% 降到 0.2%。

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

> **In warehouse/factory wireless design, the first priority is "mounting position and antenna orientation"; capacity comes second.** Ceiling mounting is an office habit, and in a 12 m high warehouse with densely packed steel racking it is a fatal mistake. In addition, **endpoint capability must be locked down at procurement** (dual-band or not, 11r/k/v support or not, is the roaming implementation reliable) — once the devices are bought, the wireless design has no cards left to play.

<div class="zh" markdown="1">

> **仓库/工厂的无线设计，第一位是"安装位置与天线朝向"，第二位才是容量。** 吊顶安装是办公场景的习惯，在 12 m 高、密排钢制货架的仓库里是致命错误。另外，**"终端能力"必须在采购阶段就锁定**（是否双频、是否支持 11r/k/v、漫游实现是否可靠）—— 等设备买回来，无线设计已经没有牌可打。

</div>

### Case 9: Cross-Campus Layer 3 Roaming — "To Keep the Same IP, We Filled Up the Inter-Campus Link" · 🔥 案例九：跨园区三层漫游——"为了不换 IP，我们把两个园区之间的链路打满了"

**Scenario**: a manufacturer has two campuses 8 km apart, each with a WLC pair, interconnected by a 1 Gbps leased line. The business requirement: "AGVs and handheld terminals must not disconnect when moving between campus A and B, and the IP must stay the same."

<div class="zh" markdown="1">

**场景**：制造企业两个园区相距 8 km，各有一对 WLC，通过 1 Gbps 专线互联。业务需求："AGV 与手持终端在 A/B 园区之间移动时不能断，IP 必须保持不变。"

</div>

**Design (the initial proposal)**: campus A's WLC acted as Anchor and campus B's as Foreign, so **all cross-campus client traffic was tunnelled back to campus A**.

<div class="zh" markdown="1">

**设计（最初方案）**：A 园区 WLC 为 Anchor，B 园区 WLC 为 Foreign，**所有跨园区客户端的流量经 CAPWAP 隧道折返 A 园区**。

</div>

**Symptoms (three weeks after go-live)**:

<div class="zh" markdown="1">

**现象（上线 3 周后）**：

</div>

- Inter-campus leased-line utilisation rose from 15% to **over 85%**, following an "saturated the moment work starts" pattern
- Campus B visitors complained that "the internet is slow", yet a local speed test was normal
- One 30 s leased-line jitter event **disconnected every AGV that had roamed over** (tunnel re-establishment failed)
- Latency: campus B clients accessing a local server (same campus) still detoured to A, so RTT went from 2 ms to 18 ms

<div class="zh" markdown="1">

- 园区间专线利用率从 15% 涨到 **85%+**，且呈"上班即满"规律
- B 园区访客抱怨"上网很慢"，但本地测速正常
- 一次专线抖动 30 s，**B 园区所有漫游过来的 AGV 全部断线**（隧道重建失败）
- 时延：B 园区客户端访问本地服务器（同园区）也要绕回 A，RTT 从 2 ms 变 18 ms

</div>

**Investigation and quantification**:

<div class="zh" markdown="1">

**排查与量化**：

</div>

```
Roamed clients in campus B: about 320 (80 AGVs + 180 handhelds + 60 others)
Average traffic: 1.2 Mbps each (AGV image upload 2 Mbps, handheld 0.5 Mbps)
→ total hairpinned traffic ≈ 320 × 1.2 ≈ 384 Mbps (one way), about 768 Mbps bidirectional
→ 77% of the 1 Gbps leased line — consistent with the observed 85%
→ and this traffic was "generated locally and consumed locally", detouring 8 km purely because of the Anchor design
```

<div class="zh" markdown="1">

```
B 园区漫游客户端数：约 320 台（AGV 80 + 手持 180 + 其他 60）
平均流量：每台 1.2 Mbps（AGV 上传图像 2 Mbps，手持 0.5 Mbps）
→ 折返总流量 ≈ 320 × 1.2 ≈ 384 Mbps（单向），双向 ≈ 768 Mbps
→ 占 1 Gbps 专线的 77% —— 与观测的 85% 吻合
→ 且这些流量"本地产生、本地消费"，纯粹因为 Anchor 设计而绕行 8 km
```

</div>

**The true root cause was not bandwidth, it was using the wrong tool**:

<div class="zh" markdown="1">

**真正的根因不是带宽，而是"用错了工具"**：

</div>

| Requirement | Does it really need Layer 3 roaming? |
|---|---|
| AGVs keeping their IP | **Yes** (but "same subnet + Layer 2 extension" or "application-layer reconnect" are alternatives) |
| Handhelds keeping their IP | **No** (handhelds run web/app clients and reconnect invisibly) |
| A unified SSID/authentication across campuses | Yes (but that is "same SSID + same RADIUS domain", unrelated to roaming) |

<div class="zh" markdown="1">

| 需求 | 是否真的需要三层漫游 |
|---|---|
| AGV 保持 IP | **需要**（但可以改用"同子网 + 二层延伸"或"AGV 应用层重连"） |
| 手持终端保持 IP | **不需要**（手持终端跑的是 Web/App，重连无感） |
| 跨园区统一 SSID/认证 | 需要（但这是"同 SSID + 同 RADIUS 域"，与漫游无关） |

</div>

**The corrected design**:

<div class="zh" markdown="1">

**修正方案**：

</div>

```
① Handhelds: drop the Anchor; re-associate and take a new IP across campuses — invisible to the business
   → leased-line traffic immediately drops by about 220 Mbps
② AGVs: independent subnet per campus + the AGV controller maintains the session
   (AGVs only move inside a campus; crossing campuses is a manual transfer and needs no network-layer roaming)
   → another 160 Mbps gone, and the Anchor is eliminated entirely
③ Keep the capability: retain the Mobility Group (for intra-campus cross-building roaming), build no cross-campus Anchor
④ Leased-line QoS: guarantee production-system traffic priority even during bursts
⑤ Latency: campus B local traffic no longer detours, so RTT returns to 2 ms
```

<div class="zh" markdown="1">

```
① 手持终端：取消 Anchor，改为"跨园区重新关联 + 重新拿 IP"，业务无感
   → 专线流量立刻下降 约 220 Mbps
② AGV：改为"每园区独立子网 + AGV 控制器做会话保持"
   （AGV 只在园区内移动，跨园区是人工转运，不需要网络层漫游）
   → 再降 160 Mbps，Anchor 完全取消
③ 保留能力：Mobility Group 保留（用于同园区跨楼漫游），跨园区不建 Anchor
④ 专线 QoS：即使有突发，也保证生产系统流量优先
⑤ 时延：B 园区本地流量不再绕行，RTT 回到 2 ms
```

</div>

**Result**: leased-line utilisation fell from 85% to 22%, local RTT returned to 2 ms, and AGV disconnections went to zero.

<div class="zh" markdown="1">

**结果**：专线利用率从 85% 降到 22%，本地访问 RTT 2 ms，AGV 断线事件归零。

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

> **Layer 3 roaming (Anchor) is the expensive price paid "to keep the IP": traffic hairpinning + a single point + latency.** Design must first ask three questions:
> ① **Can this application really not tolerate an IP change?** (most web/app traffic can)
> ② **Can "the same subnet" replace "Layer 3 roaming"?** (usually yes for cross-building within one campus)
> ③ **Can the link carry the hairpinned traffic, and does that traffic even need to cross the link?** (in this case, not at all)
>
> **"Technically possible" and "the right design" are two different things.** If session persistence can be solved at the application layer, do not force it with network-layer tunnels.

<div class="zh" markdown="1">

> **三层漫游（Anchor）是"为了保持 IP"付出的昂贵代价：流量折返 + 单点 + 时延**。设计时必须先问三个问题：
> ① **这个业务真的不能容忍 IP 变化吗？**（多数 Web/App 业务可以）
> ② **能不能用"同子网"代替"三层漫游"？**（同园区跨楼通常可以）
> ③ **折返流量能不能被链路承受，且这些流量本来需要跨链路吗？**（本例中完全不需要）
>
> **"技术上能做"与"设计上应该做"是两件事。** 能用应用层解决的会话保持，不要用网络层的隧道去硬扛。

</div>

### Case 10: First 6 GHz Deployment — "Half the Users Cannot See the SSID, the Other Half Drop Right After Connecting" · 🔥 案例十：6 GHz 首部署——"买了 Wi-Fi 6E AP，一半人看不到 SSID，另一半人连上就断"

**Scenario**: a tech company's newly renovated headquarters bought tri-band Wi-Fi 6E APs and required "6 GHz enabled building-wide for maximum bandwidth". The design used 5 GHz at 40 MHz for coverage, 6 GHz at 80 MHz as the capacity layer, with WPA3 enabled building-wide.

<div class="zh" markdown="1">

**场景**：科技公司总部新装修，采购 Wi-Fi 6E AP（三频），要求"全楼启用 6 GHz 获得最大带宽"。设计：5 GHz 40 MHz 保覆盖 + 6 GHz 80 MHz 做容量层，全楼统一开 WPA3。

</div>

**Three problems exploded on go-live day**:

<div class="zh" markdown="1">

**上线当天三个问题同时爆发**：

</div>

| Problem | Scope | Symptom |
|---|---|---|
| Some endpoints cannot see the SSID at all | About 45% of devices | Old laptops, pre-iPhone-11 models, most IoT |
| Visible but cannot connect / connects then drops | About 20% of devices | 6E-capable but with old drivers/firmware |
| Meeting rooms disconnect frequently | Site-wide | Unrelated to 6 GHz: DFS + WPA3-PMF compatibility stacking |

<div class="zh" markdown="1">

| 问题 | 影响面 | 表象 |
|---|---|---|
| 部分终端完全看不到 SSID | 约 45% 设备 | 老笔记本、iPhone 11 之前机型、大部分 IoT |
| 能看到但连不上 / 连上即断 | 约 20% 设备 | 支持 6E 但驱动/固件较老 |
| 会议室频繁掉线 | 全场 | 与 6 GHz 无关，是 DFS + WPA3-PMF 兼容叠加 |

</div>

**Item-by-item investigation**:

<div class="zh" markdown="1">

**逐项排查**：

</div>

1. **Not seeing the SSID is "normal"** — 6 GHz **does not broadcast traditional Beacons**; its presence is indicated by the RNR element inside 5 GHz Beacons. Endpoints without 6E never scan 6 GHz. **This is specified behaviour, not a fault.**
2. **Connecting then dropping** — 6 GHz **mandates WPA3 + PMF**. Some endpoints have flawed WPA3 implementations (especially early 6E NIC drivers), and they fail repeatedly in required-PMF mode.
3. **Meeting rooms disconnecting** — some 5 GHz channels used DFS, and with weather/airport radar in that direction, **three channel switches were triggered in a single day**; meanwhile WPA3's PMF prevented a few old endpoints from associating.
4. **AFC not applied for** — the original plan used Standard Power mode for outdoor locations, but the AFC service had not been applied for in advance, so three outdoor locations **could not enable 6 GHz**.

<div class="zh" markdown="1">

1. **看不到 SSID 是"正常"的** —— 6 GHz **不广播传统 Beacon**，通过 5 GHz Beacon 中的 RNR 元素指示；不支持 6E 的终端根本不会去 6 GHz 扫描。**这是规范行为，不是故障**。
2. **连上即断** —— 6 GHz **强制 WPA3 + PMF**。部分终端的 WPA3 实现有问题（尤其早期 6E 网卡驱动），PMF 必需模式下反复失败。
3. **会议室掉线** —— 5 GHz 部分信道用了 DFS，楼内有气象/机场雷达方向，**一天内触发 3 次信道切换**；同时 WPA3 的 PMF 让少数老终端无法关联。
4. **AFC 未申请** —— 原方案计划室外点位用 Standard Power 模式，但 AFC 服务未提前申请，导致室外 3 个点位**无法启用 6 GHz**。

</div>

**Remediation plan (layered)**:

<div class="zh" markdown="1">

**修复方案（分层）**：

</div>

| Layer | Action |
|---|---|
| **Band policy** | Open 6 GHz only to a "certified endpoint group" (distinguished by RADIUS attributes/endpoint grouping); every other endpoint sees 5 GHz only |
| **SSID split** | Employee SSID: 5 GHz (WPA2/WPA3 transition) + 6 GHz (WPA3); IoT SSID: 2.4 GHz only + WPA2-PSK/iPSK |
| **PMF policy** | 5 GHz uses "optional PMF" for compatibility; 6 GHz stays "required" (per specification) |
| **DFS** | Pin high-priority areas (meeting rooms, voice zones) to **UNII-1 + UNII-3 non-DFS channels**; use DFS only as capacity top-up |
| **AFC** | Start the AFC application process (typically several weeks) and run outdoor locations at LPI/VLP reduced power meanwhile |
| **Endpoint baseline** | Publish a "6 GHz compatible endpoint list", fold it into procurement and the IT standard image, and upgrade drivers on old devices |

<div class="zh" markdown="1">

| 层次 | 动作 |
|---|---|
| **频段策略** | 6 GHz 只对"认证过的终端组"开放（用 RADIUS 属性/终端分组区分）；其余终端只见 5 GHz |
| **SSID 拆分** | 员工 SSID：5 GHz（WPA2/WPA3 过渡）+ 6 GHz（WPA3）；IoT SSID：仅 2.4 GHz + WPA2-PSK/iPSK |
| **PMF 策略** | 5 GHz 用"可选 PMF"保兼容；6 GHz 保持"必需"（规范要求） |
| **DFS** | 高优先级区域（会议室、语音区）**锁定 UNII-1 + UNII-3 非 DFS 信道**；DFS 只做容量补充 |
| **AFC** | 启动 AFC 申请流程（周期通常数周），室外点位先按 LPI/VLP 降功率运行 |
| **终端基线** | 输出"6 GHz 兼容终端清单"，纳入采购与 IT 标准镜像；老设备升级驱动 |

</div>

**Result**: 6E endpoints (about 35%) run on 6 GHz at 80 MHz (measuring 600–800 Mbps); everything else sits stably on 5 GHz; disconnect complaints went to zero; outdoor locations were enabled after AFC approval.

<div class="zh" markdown="1">

**结果**：6E 终端（约 35%）跑在 6 GHz 80 MHz（实测 600–800 Mbps）；其余终端稳定在 5 GHz；掉线投诉归零；室外点位在 AFC 批复后启用。

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

> **6 GHz is not "a bigger 5 GHz" but a new band with an entry barrier**: endpoint penetration (deciding whether it deserves dedicated deployment), mandatory WPA3+PMF (deciding compatibility), and power classes with AFC (deciding project duration and coverage). **The design document must state clearly "which endpoints can use 6 GHz and what happens to those that cannot"**, otherwise go-live day will be swamped by "cannot see the SSID" tickets.

<div class="zh" markdown="1">

> **6 GHz 不是"更大的 5 GHz"，而是一个有准入门槛的新频段**：终端渗透率（决定了它是否值得单独部署）、强制 WPA3+PMF（决定了兼容性）、功率等级与 AFC（决定了项目周期与覆盖）。**设计文档里必须写清"哪些终端能上 6 GHz、上不去怎么办"**，否则上线当天就会被"看不到 SSID"的工单淹没。

</div>

### Case 11: An 8,000-Seat Arena — "The Design Was Right, But the DHCP Pool Emptied Ten Minutes After Doors Opened" · 🔥 案例十一：8,000 人体育馆——"设计没错，但开场 10 分钟 DHCP 池就空了"

**Scenario**: a municipal arena with 8,000 seats hosting esports events and concerts. The capacity model produced 60 APs (5 GHz 20 MHz plus some 6 GHz), with downtilt directional antennas zonally deployed in the seating areas and a 10 Gbps egress.

<div class="zh" markdown="1">

**场景**：市级体育馆，8,000 座，承办电竞赛事 + 演唱会。设计按容量模型做了 60 台 AP（5 GHz 20 MHz + 部分 6 GHz），座席分区用下倾定向天线，出口 10 Gbps。

</div>

**Timeline on event day**:

<div class="zh" markdown="1">

**活动当天时间线**：

</div>

| Time | Symptom |
|---|---|
| T-60 min | Doors open; airtime rises from 5% to 25%; everything normal |
| **T-10 min** | **DHCP pool exhaustion alarm**; arriving spectators "connect but have no network" |
| T-0 (start) | Phones reconnect en masse plus heavy short-video uploads; airtime hits 78% and P95 latency rises from 20 ms to 400 ms |
| T+5 min | Authentication success falls from 99.8% to 92% (RADIUS queueing) |
| T+20 min | The 10 Gbps egress saturates; everyone is "connected but slow" |

<div class="zh" markdown="1">

| 时间 | 现象 |
|---|---|
| T-60 min | 观众开始入场，airtime 从 5% 升到 25%，一切正常 |
| **T-10 min** | **DHCP 池耗尽告警**，新入场观众"连上但无网络" |
| T-0（开场） | 手机集中重连 + 大量短视频上传，airtime 冲到 78%，时延 P95 从 20 ms 涨到 400 ms |
| T+5 min | 认证成功率从 99.8% 掉到 92%（RADIUS 排队） |
| T+20 min | 出口 10 Gbps 打满，所有人"能动但很慢" |

</div>

**Root cause analysis (four independent problems, none of them "not enough APs")**:

<div class="zh" markdown="1">

**根因分析（四个独立问题，全部不是"AP 不够"）**：

</div>

| Problem | Number | Root cause |
|---|---|---|
| **DHCP pool exhausted** | 8,000 people designed, pool sized as "people × 1.2 = 9,600" | Private MAC randomisation caused **multiple requests per device** (entry reconnects + OS randomisation = 1.8 leases per person) → actual demand 14,400 |
| **RADIUS queueing** | 4,000 authentications/minute at peak | Authentication concentrated in the first 10 minutes; a single cluster was capped at 2,500 QPS |
| **Airtime 78%** | Uplink short video | Uplink traffic was underestimated (design assumed 8:2 down:up, reality 6:4) |
| **Egress saturated** | 10 Gbps at 100% | Design assumed "0.5 Mbps per person"; actual peak was 1.2 Mbps per person |

<div class="zh" markdown="1">

| 问题 | 数字 | 根因 |
|---|---|---|
| **DHCP 池耗尽** | 设计 8,000 人，池子按"人数 × 1.2 = 9,600"配 | 私有 MAC 随机化导致**每台设备多次申请**（进场重连 + 系统随机化 = 人均 1.8 个租约）→ 实际需求 14,400 |
| **RADIUS 排队** | 峰值 4,000 次认证/分钟 | 认证集中在前 10 分钟；单集群 QPS 上限 2,500 |
| **airtime 78%** | 上行短视频 | 上行流量被低估（设计假设下行 8:2，实际 6:4） |
| **出口打满** | 10 Gbps 利用率 100% | 设计假设"人均 0.5 Mbps"，实际峰值人均 1.2 Mbps |

</div>

**On-site handling (while the event was running)**:

<div class="zh" markdown="1">

**现场处置（活动进行中）**：

</div>

```
① Scale DHCP immediately: add a second pool (same VLAN, wider mask) + shorten leases to 30 minutes
② Shut down the guest SSID (give airtime back to the primary SSID) + cap each client's uplink at 1 Mbps
③ Raise the broadcast suppression threshold to reduce probe and mDNS flooding
④ Ask the organiser to disable on-site screen "scan-to-interact" (cut the instant authentication spike)
⑤ Enable application-based rate limiting at the egress (cap short-video classes at 2 Mbps per person)
```

<div class="zh" markdown="1">

```
① 立即扩容 DHCP：临时增加第二个池（同 VLAN 加大掩码）+ 缩短租期到 30 分钟
② 关闭访客 SSID（把 airtime 让给主 SSID）+ 限制每客户端上行 1 Mbps
③ 提高广播抑制阈值，减少探测与 mDNS 泛洪
④ 通知运营方关闭现场大屏的"扫码互动"（减少瞬时认证洪峰）
⑤ 出口侧启用基于应用的限速（短视频类限 2 Mbps/人）
```

</div>

**Formal design corrections afterwards (T+1)**:

<div class="zh" markdown="1">

**赛后（T+1）的正式设计修正**：

</div>

| Correction | Before | After |
|---|---|---|
| DHCP pool | people × 1.2 | **people × 2.5** (allowing for private MAC and multiple devices), 60 min leases |
| RADIUS capacity | sized by concurrent clients | sized by **peak authentication rate** (first auth + re-auth + CoA), more nodes + connection-pool tuning |
| Uplink budget | 20% | **40%** (social sharing and live uplink dominate) |
| Egress bandwidth | 0.5 Mbps per person | 0.8 Mbps per person + application rate-limit policy |
| Acceptance | empty-venue stress test | **stress test with 200 real endpoints + simulated authentication spikes** |
| On-site support | none | monitoring wall + five playbooks (rate limiting / shut SSIDs / expand pools / change bands / limit applications) |

<div class="zh" markdown="1">

| 修正项 | 修正前 | 修正后 |
|---|---|---|
| DHCP 池 | 人数 × 1.2 | **人数 × 2.5**（含私有 MAC 与多设备），租期 60 min |
| RADIUS 容量 | 按并发客户端 | 按 **峰值认证速率**（首次 + 重认证 + CoA）设计，加节点 + 连接池调优 |
| 上行预算 | 20% | **40%**（社交分享与直播上行是主负载） |
| 出口带宽 | 人均 0.5 Mbps | 人均 0.8 Mbps + 应用限速策略 |
| 验收 | 空场压测 | **带 200 台真实终端 + 模拟洪峰认证**压测 |
| 现场保障 | 无 | 监控大屏 + 五个预案（限速/关 SSID/扩池/切频段/限应用） |

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

> **Large events almost always fail in the "peripheral systems": DHCP, RADIUS, egress bandwidth.** The RF is usually the healthiest part because it was designed carefully, while DHCP/RADIUS are treated as "configure it in passing". **A complete high-density design checklist must include: DHCP scale, authentication throughput, egress bandwidth, NAT/session tables and DNS performance** — any omission is a break point.
>
> One more frequently ignored point: **private MAC randomisation means "people → leases" is no longer 1:1.** That is the main reason DHCP pools have "somehow not been enough" in recent years.

<div class="zh" markdown="1">

> **大型活动的失败点几乎总在"外围系统"：DHCP、RADIUS、出口带宽。** 无线 RF 往往是最健康的一环，因为它被认真设计过；而 DHCP/RADIUS 通常被当作"顺手配一下"的配套。**高密度设计的完整清单必须包含：DHCP 规模、认证吞吐、出口带宽、NAT/会话表、DNS 性能** —— 少一项就是一个断点。
>
> 还有一条常被忽略的：**私有 MAC 随机化让"人数 → 租约数"不再是 1:1**。这是近几年 DHCP 池"明明够却不够"的最主要原因。

</div>

### Case 12: Hospital Telemetry — "Every Monitor Drops Together for 30 Seconds at 2 a.m." · 🔥 案例十二：医院医疗遥测——"监护仪每天凌晨 2 点集体掉线 30 秒"

**Scenario**: a tertiary hospital's inpatient building, 12 floors, 40 wireless monitors per floor (2.4 GHz single-band, WPA2-PSK, static IPs, no 11r/11kv support), plus a staff SSID (5 GHz) and a guest SSID.

<div class="zh" markdown="1">

**场景**：三甲医院住院部 12 层，每层 40 台无线监护仪（2.4 GHz 单频，WPA2-PSK，固定 IP，不支持 11r/11kv），另有员工 SSID（5 GHz）与访客 SSID。

</div>

**Symptoms**:

<div class="zh" markdown="1">

**现象**：

</div>

- **Around 2 a.m. every day**, monitors across multiple floors drop together for 20–40 s and then recover on their own
- Occasional single-monitor drops during the day (the nurses' station "cannot see the waveform")
- The staff SSID is largely normal; guests complain more

<div class="zh" markdown="1">

- **每天凌晨 2 点左右**，多楼层监护仪集体掉线 20–40 s，随后自动恢复
- 白天偶发单个监护仪掉线（护士站"看不到波形"）
- 员工 SSID 基本正常，访客抱怨较多

</div>

**Investigation (following the four-layer model)**:

<div class="zh" markdown="1">

**排查过程（按四层模型）**：

</div>

1. **Layer 1, RF**: no anomaly in the 2 a.m. airtime curve and no channel-switch records → congestion and DFS ruled out
2. **Layer 2, controller**: a **scheduled task** at 02:00 — the campus AP group runs daily "automatic channel optimisation (RRM DCA)" configured in **full mode (recompute all channels)**
3. **Layer 2, controller** (second clue): the IoT WLAN carrying the monitors had **802.11r and 11k/v enabled**, yet most monitor firmware does not support FT → this explains the daytime single-monitor drops
4. **Layer 3, network**: DHCP pools were sized by "bed count" without allowing for monitors + tablets + infusion pumps; pool utilisation sat at 92% long term
5. **Layer 4, authentication**: 02:00 was also **ISE's certificate/CRL refresh task**; although PSK is unaffected, the WLC performs a full client policy re-push → amplifying the momentary instability

<div class="zh" markdown="1">

1. **第 1 层 RF**：凌晨 airtime 曲线无异常，信道也无切换记录 → 排除拥塞与 DFS
2. **第 2 层控制器**：发现凌晨 2:00 有一条**定时任务**记录 —— 全院 AP 组每日执行"自动信道优化（RRM DCA）"，且配置为 **full 模式（全信道重算）**
3. **第 2 层控制器**（第二条线索）：监护仪所在的 IoT WLAN 开启了 **802.11r 与 11k/v**，而多数监护仪固件不支持 FT → 白天单个掉线由此解释
4. **第 3 层网络**：DHCP 池按"床位数"配置，未考虑监护仪 + 平板 + 输液泵，池利用率长期 92%
5. **第 4 层认证**：凌晨 2:00 同时是 **ISE 的证书/CRL 更新任务**，PSK 虽不受影响，但 WLC 会做一次全量客户端策略重下发 → 加剧瞬时抖动

</div>

**Root cause**: **the 02:00 DCA full-channel recompute changed the channels of entire floors of APs at the same moment**, forcing every 2.4 GHz monitor to re-associate; and those devices **reconnect slowly (15–30 s) and do not support fast roaming**, so the result was a collective dropout.

<div class="zh" markdown="1">

**根因**：**凌晨 2 点的 DCA 全信道重算，把整层 AP 的信道同时改掉**，所有 2.4 GHz 监护仪被迫重新关联；而这些设备**重连慢（15–30 s）且不支持快速漫游**，所以表现为"集体掉线"。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Action | Explanation |
|---|---|
| **Move RRM DCA to off-hours with limited amplitude** | Only in maintenance windows, **at most one channel change at a time**, avoiding the 00:00–06:00 nursing peak |
| **Disable 11r and 11k/v on the IoT WLAN** | Old firmware does not support them, and enabling them actually causes association failures |
| **Separate IoT SSID + iPSK** | A unique key per device, simplifying single-device revocation and auditing |
| **Grow DHCP pools to "beds × 3"** | Covering monitors/infusion pumps/tablets/staff phones; 8 h leases for fixed devices |
| **IoT on a dedicated 2.4 GHz SSID + client isolation + egress whitelist** | Allow access only to the central monitoring station and the vendor cloud |
| **Disable multicast flooding on that VLAN** | The monitors do not use multicast; suppressing it cut airtime by 6% |
| **Add two monitoring alarms** | "single-AP client count drops > 30%" and "IoT SSID association failure rate > 1%" |

<div class="zh" markdown="1">

| 动作 | 说明 |
|---|---|
| **RRM DCA 改为 off-hours + 限制幅度** | 只在维护窗口做，且**每次最多移动 1 个信道**、避开 00:00–06:00 的护理高峰 |
| **IoT WLAN 关闭 11r、11k/v** | 老固件不支持，开启反而导致关联失败 |
| **IoT 独立 SSID + iPSK** | 每台设备独立密钥，便于单台回收与审计 |
| **DHCP 池扩到"床位数 × 3"** | 含监护仪/输液泵/平板/员工手机；租期 8 h（固定设备） |
| **IoT 走 2.4 GHz 专用 + 客户端隔离 + 出口白名单** | 只允许访问监护中央站与厂商云 |
| **关闭该 VLAN 的组播泛洪** | 监护仪不用组播，抑制后 airtime 降 6% |
| **监控加两条告警** | "单 AP 客户端数骤降 > 30%" 与 "IoT SSID 关联失败率 > 1%" |

</div>

**Result**: the 2 a.m. collective dropout disappeared; daytime single drops fell from 5–8 per day to about once a week (mostly genuine device faults); 2.4 GHz peak airtime fell from 62% to 48%.

<div class="zh" markdown="1">

**结果**：凌晨集体掉线消失；白天单个掉线从每天 5–8 次降到每周 1 次（多为设备自身故障）；2.4 GHz airtime 峰值从 62% 降到 48%。

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

> **Medical/IoT wireless fears "well-intentioned automation" most of all**: automatic channel optimisation, automatic power adjustment and automatic policy re-pushes are optimisations for staff endpoints and **disasters for old devices that do not support fast roaming**. Design must do two things:
> ① **"Freeze" the SSIDs of critical IoT** (disable 11r/11kv and any automatic optimisation of that VLAN);
> ② **Every automated action needs a "time window + amplitude limit + rollback"**.
>
> One more universal point: **the time pattern of a fault (2 a.m. every day) points at the root cause faster than any command** — first ask "what scheduled task runs at that time".

<div class="zh" markdown="1">

> **医疗/IoT 无线最怕"善意的自动化"**：自动信道优化、自动功率调整、自动策略重下发，对员工终端是优化，对**不支持快速漫游的老设备是灾难**。设计上必须做到两点：
> ① **关键 IoT 的 SSID 要"冻结"**（关闭 11r/11kv、关闭对该 VLAN 的自动优化）；
> ② **所有自动化动作都要有"时间窗 + 幅度限制 + 可回退"**。
>
> 另一条更普适的：**故障的时间规律（每天凌晨 2 点）比任何命令都更快指向根因** —— 先问"这个时间有什么定时任务"。

</div>

---

## Wireless Design Trade-offs · 无线设计的取舍

| Trade-off dimension | Option A | Option B | Decision criteria |
|---------|------|------|---------|
| **Channel width** | **20 MHz**: more reuse, CCI-resistant, optimal for high density | **80/160 MHz**: higher single-user peak | Choose 20 for dense/multi-user; wide is acceptable for single-user, low-density or 6 GHz |
| **Transmit power** | **Low power**: smaller cells, higher capacity, better roaming | **High power**: longer reach, fewer APs, lower cost | Choose low power where capacity matters; high power only where coverage is the sole goal (warehouses/outdoors) |
| **Coverage boundary** | **Strict −67 dBm boundary**: stable capacity and experience | **Loose −75 dBm boundary**: fewer APs | Strict is mandatory for voice/video/dense users |
| **Controller** | **Centralized**: consistent policy, simple roaming | **Distributed/cloud**: local forwarding, WAN-failure resilient | Centralized for a single campus; distributed/Flex for many branches with unreliable WAN |
| **Roaming method** | **A large Layer 2 mobility domain**: simple, low latency | **Layer 3 roaming (Anchor)**: same IP, cross-subnet | Use Layer 2 wherever possible; if Layer 3, accept hairpinned traffic |
| **Band policy** | **2.4 GHz as fallback only**: airtime is precious | **Broad 2.4 GHz coverage**: legacy compatibility | Keep 2.4 GHz for IoT; push staff endpoints to 5/6 GHz |
| **Security mode** | **WPA3 + PMF**: security and compliance | **WPA2/WPA3 transition**: legacy compatibility | WPA3 for new builds; split SSIDs for the transition on brownfield |
| **Authentication** | **802.1X/EAP-TLS**: strongest, per-user | **PSK/iPSK**: simple, IoT-friendly | 802.1X for staff; iPSK + isolation for IoT |
| **AP mode** | **Local**: centralized control, full features | **FlexConnect**: local forwarding, link-down resilient | Depends on WAN quality and backhaul cost |
| **Data forwarding** | **Tunnel back to the controller**: centralized policy/audit | **Local forwarding**: saves bandwidth, lower latency | Tunnel where centralized security auditing is required |
| **Monitoring** | **Dedicated Monitor APs**: continuous wIPS/RF visibility | **Regular APs scanning part-time**: lower cost | Dedicated in high-security sites; part-time elsewhere |
| **Survey method** | **AP-on-a-stick measurement**: most accurate | **Predictive simulation**: fast and cheap | Real measurement is mandatory in critical venues |
| **New band** | **Adopt 6 GHz immediately**: clean spectrum, high bandwidth | **Wait and see**: low endpoint penetration | Judge by endpoint ratio (limited gain below 30%) |
| **SSID count** | **Few SSIDs + dynamic VLAN/role**: fewer Beacons, easier management | **Many SSIDs**: intuitive, clean separation | SSID ≤ 4; if RADIUS attributes can differentiate it, do not add an SSID |
| **Multicast handling** | **Multicast-to-unicast**: ACKs, high rate | **Multicast Direct**: saves controller CPU, simple | Unicast conversion for small audiences (< 10); wired/edge cache for large audiences; Direct only for very low rates |
| **RF automation** | **Fully automatic RRM/DCA**: less labour, adaptive | **Manual planning + automatic trimming**: stable, predictable | Limit automation amplitude and windows where voice or old IoT exists |
| **Fast roaming features** | **802.11r fully enabled**: optimal for voice | **11r off/adaptive**: legacy compatibility | Enable (Adaptive) on staff SSIDs; disable on IoT SSIDs |
| **Endpoint admission** | **Strict authentication (802.1X + certificates)**: secure | **Loose (PSK/portal)**: quick onboarding, fewer tickets | Strict for staff; iPSK as the IoT compromise; portal for guests |
| **Event support** | **Full lifecycle support (stress test + monitoring wall + playbooks)**: robust | **Routine operations**: saves labour | Mandatory for single events over 2,000 people or business-critical services |
| **IoT security** | **Dedicated SSID + iPSK + egress whitelist**: safest | **Share the staff SSID**: cheapest | Always separate; IoT firmware is uncontrollable |
| **Acceptance depth** | **15 test cases + worst-moment stress test**: high confidence | **Coverage plus association test**: fast | Full set for critical services; simplified for offices |
| **Redundancy investment** | **HA SSO + dual RADIUS + local survivability**: high availability | **Single nodes**: lower cost | Where the business cannot stop, redundancy is not optional |

<div class="zh" markdown="1">

| 取舍维度 | 选 A | 选 B | 判断依据 |
|---------|------|------|---------|
| **信道宽度** | **20 MHz**：多复用、抗 CCI、高密度最优 | **80/160 MHz**：单用户峰值高 | 高密度/多人场景选 20；单人/低密度/6 GHz 可选宽 |
| **发射功率** | **低功率**：蜂窝小、容量高、漫游好 | **高功率**：覆盖远、AP 少省成本 | 有容量诉求选低功率；只有覆盖诉求（仓库/户外）可选高 |
| **覆盖边界** | **-67 dBm 严格边界**：容量与体验稳定 | **-75 dBm 宽松边界**：省 AP | 有语音/视频/密集用户时必须严格 |
| **控制器** | **集中式**：策略统一、漫游简单 | **分布式/云**：本地转发、抗 WAN 故障 | 单园区选集中；多分支且 WAN 不可靠选分布/Flex |
| **漫游方式** | **二层大漫游域**：简单、时延低 | **三层漫游（Anchor）**：IP 不变、支持跨子网 | 能统一二层就不要三层；三层要接受流量折返 |
| **频段策略** | **2.4 GHz 仅兜底**：airtime 宝贵 | **2.4 GHz 广覆盖**：兼容老设备 | IoT 必须留 2.4；员工终端强推 5/6 GHz |
| **安全模式** | **WPA3 + PMF**：安全合规 | **WPA2/WPA3 过渡**：兼容老终端 | 新项目 WPA3；存量分 SSID 过渡 |
| **认证方式** | **802.1X/EAP-TLS**：最强、用户级 | **PSK/iPSK**：简单、IoT 友好 | 员工用 802.1X；IoT 用 iPSK + 隔离 |
| **AP 模式** | **Local**：集中控制、功能全 | **FlexConnect**：本地转发、抗断链 | 看 WAN 质量与流量回传成本 |
| **数据转发** | **隧道回控制器**：可集中做策略/审计 | **本地转发**：省带宽、低时延 | 有集中安全审计诉求选隧道 |
| **监视手段** | **专用 Monitor AP**：持续 wIPS/RF | **普通 AP 兼职扫描**：省成本 | 高安全场所用专用；一般场所兼职 |
| **勘察方式** | **AP-on-a-stick 实测**：最准 | **预测性仿真**：快、便宜 | 关键场所必须实测 |
| **新频段** | **6 GHz 立即上**：干净频谱、大带宽 | **观望**：终端渗透率低 | 看终端比例（< 30% 时增益有限） |
| **SSID 数量** | **少 SSID + 动态 VLAN/角色**：省 Beacon、易管理 | **多 SSID**：直观、隔离清晰 | SSID ≤ 4；能靠 RADIUS 属性区分就不要新开 SSID |
| **组播处理** | **组播转单播**：有 ACK、高速率 | **组播直通**：省控制器 CPU、实现简单 | 观众少（<10）用转单播；观众多用有线/边缘缓存；极低码率可直通 |
| **RF 自动化** | **全自动 RRM/DCA**：省人力、自适应 | **人工规划 + 自动微调**：稳定、可预期 | 有语音/老 IoT 的场所限制自动化幅度与时间窗 |
| **快速漫游特性** | **802.11r 全开**：语音最优 | **11r 关闭/自适应**：兼容老设备 | 员工 SSID 开（Adaptive），IoT SSID 关 |
| **终端准入** | **严格认证（802.1X + 证书）**：安全 | **宽松（PSK/Portal）**：接入快、工单少 | 员工严格；IoT 用 iPSK 折中；访客 Portal |
| **监控深度** | **专用 Monitor/wIPS AP**：持续可视 | **普通 AP 兼职扫描**：省成本 | 高安全/高密度场所用专用传感器 |
| **活动保障** | **全流程保障（压测+大屏+预案）**：稳 | **常规运维**：省人力 | 单场 > 2,000 人或关键业务时必须做保障 |
| **数据转发** | **集中隧道**：审计与策略集中 | **本地转发**：省带宽、低时延、抗断链 | 有合规审计诉求才选集中；高密度选本地 |

</div>

---

## Design Flaws · 设计缺陷

| Flaw | Typical symptom | Root cause | How to avoid it |
|------|---------|------|---------|
| **Sizing APs by floor area** | Enough APs installed but peak is still slow | Capacity must be computed from airtime, not area | Six-step method: business profile → airtime → AP count |
| **80/160 MHz in high density** | Everything interferes with everything; total capacity falls | Insufficient spectrum reuse | Use 20 MHz uniformly in high density |
| **Running APs at full power** | Cells too large, terrible roam points, severe CCI | No power plan; RRM drove power to maximum | Fix 5–8 dBm in high density + MIN RSSI |
| **Only checking "it associates"** | Weak clients slow the whole network | No boundary RSSI requirement | −67 dBm boundary design + disabled low rates |
| **40 MHz on 2.4 GHz** | Only one usable channel remains | Misunderstanding "wider is faster" | 2.4 GHz is always 20 MHz |
| **PMK caching/802.11r not enabled** | Roaming interruptions of 300 ms+, voice drops | A full 802.1X run on every roam | Enable the k + v + r trio; mandatory for voice |
| **No Mobility Group** | Cross-controller roams require re-authentication | PMK not synchronised | Same SSID/security/domain + build the mobility domain |
| **Insufficient coverage overlap** | Clients switch only after travelling far | AP spacing designed for "maximum reach" | 15%–20% overlap; roam-point difference ≤ 5 dB |
| **FlexConnect local switching only at branches** | After a WAN cut, nobody can connect | No local DHCP / local authentication | Local DHCP + Local Auth + link-down drills |
| **CAPWAP tunnel MTU not planned** | Large packets dropped, abnormal performance | Tunnel encapsulation + fragmentation | AP–WLC path MTU ≥ 1550 |
| **Firewall not permitting CAPWAP** | APs stuck in Join | UDP 5246/5247 one-way or blocked | Permit both directions + ICMP + NTP |
| **DHCP Option 43 missing** | Cross-subnet APs cannot find the controller | Relies on broadcast discovery | Option 43 or a DNS pointer |
| **Single RADIUS server** | All new associations network-wide fail | Authentication server not redundant | At least 2 nodes + multiple servers configured |
| **EAP clients not validating the server certificate** | A phishing AP can harvest domain credentials | Missing endpoint configuration baseline | Mandatory certificate validation + SSID whitelist |
| **Multicast/broadcast not suppressed** | Camera/mirroring traffic saturates airtime | Multicast is sent at the lowest rate | Multicast-to-unicast + IGMP Snooping |
| **DHCP pool sized by headcount** | "Connects but no internet" | Concurrency and lease duration ignored | Peak concurrency × 1.5–2.5, shorter leases |
| **Only 1 G AP uplinks** | Wi-Fi 6 AP rates throttled upstream | No mGig | 2.5G/5G uplinks + Cat6a |
| **Insufficient PoE** | AP degrades (radios off, MIMO reduced) | 802.3af powering a Wi-Fi 6 AP | 802.3at/bt, verify AP power requirements |
| **Cutting straight to pure WPA3** | A batch of old endpoints loses connectivity | No endpoint compatibility matrix | Per-SSID transition + rollback plan |
| **Expecting 6 GHz to provide coverage** | Endpoints cannot see the SSID | 6 GHz is for 6E/7 endpoints only and mandates WPA3 | 5 GHz provides coverage, 6 GHz provides capacity |
| **Ignoring 6 GHz AFC** | Outdoor/standard-power deployment cannot be enabled | AFC service not applied for in advance | Confirm power class and AFC early in the project |
| **Selecting by "N users per AP"** | Guaranteed to collapse at peak | Vendor figures are laboratory numbers | Compute with an airtime/pps model (the worked examples in this chapter) |
| **One SSID per department** | Over 10% of airtime eaten by Beacons | One Beacon per SSID, broadcast at the lowest rate | SSID ≤ 4 + dynamic VLAN/role assignment |
| **Computing bandwidth but not pps** | Bandwidth math says fine, airtime explodes after go-live | Fixed overhead dominates for small frames | Verify with pps × per-frame airtime |
| **Ignoring Low-E glass/metal racking** | All green on drawings, blind spots on site | Material attenuation assumptions off by 20 dB+ | On-site survey is mandatory; never finalise with the drawing model |
| **APs inside ceilings or behind metal** | Half the coverage vanishes | Installation engineering not part of the design | Put installation standards into the construction briefing |
| **Fully automatic RRM in IoT/voice scenarios** | Collective 2 a.m. dropouts, dropped calls | Full DCA recompute + old devices without fast roaming | Limit amplitude/windows; freeze critical SSIDs |
| **IoT lumped into the staff SSID** | Lateral attacks, airtime dragged down | No device segmentation | Separate SSID + iPSK + client isolation + egress whitelist |
| **DHCP pool at 1.2× headcount** | Pool exhausted 10 minutes into an event | Private MAC randomisation makes leases 1.5–2× | Size at 2.5× headcount and shorten leases |
| **RADIUS capacity sized by concurrency** | Queues at the opening authentication spike | First auth + re-auth + CoA ignored | Design by peak authentication rate; add nodes and connection pools |
| **Layer 3 roaming abuse** | Leased lines saturated, latency doubled, single point | Forcing session persistence with network-layer tunnels | First ask "can the application tolerate an IP change"; prefer application-layer reconnect |
| **Multicast Direct by default** | One video stream eats a third of the radio | Multicast has no ACK and is sent at the lowest rate | Unicast conversion + IGMP Snooping + limited concurrent viewers |
| **No dynamic VLAN assignment for static-IP IoT** | Devices drop when CoA changes their VLAN | RADIUS CoA conflicts with static addressing | Pin static-IP devices to a fixed VLAN |
| **Accepting in an empty venue** | Collapses at peak after go-live | Tests do not represent real load | Worst moment + real endpoints + mixed-service stress test |
| **Technical delivery without operational handover** | Out of control three months after go-live | No baseline, no alarms, no playbooks | The delivery document set + thresholds + drills |
| **Uplink asymmetry not planned** | Full bars but uploads fail | AP power far above client power | Match AP power to endpoints (5–14 dBm) |
| **Layer 2 isolation not enabled on guest** | Guests can scan each other | Client isolation not enabled | AP isolation / peer-to-peer blocking |

<div class="zh" markdown="1">

| 缺陷 | 典型现象 | 根因 | 规避方法 |
|------|---------|------|---------|
| **按面积算 AP 数** | AP 装够了但高峰还是慢 | 容量按 airtime 算，不按面积 | 六步法：业务画像 → airtime → AP 数 |
| **高密度用 80/160 MHz** | 全场互相干扰、总容量反而下降 | 频谱复用不足 | 高密度统一 20 MHz |
| **AP 满功率运行** | 蜂窝过大、漫游点极差、CCI 严重 | 未做功率规划，RRM 自动拉满 | 高密度固定 5–8 dBm + MIN RSSI |
| **只看"能连上"** | 弱信号客户端拖慢全网 | 无边界 RSSI 要求 | -67 dBm 边界设计 + 禁用低速率 |
| **2.4 GHz 开 40 MHz** | 可用信道只剩 1 个 | 误解"更宽更快" | 2.4 GHz 永远 20 MHz |
| **未启用 PMK 缓存/802.11r** | 漫游断 300 ms+，语音丢音 | 每次漫游重做 802.1X | k + v + r 三件套，语音必配 |
| **Mobility Group 未建** | 跨控制器漫游要重新认证 | PMK 未同步 | 同 SSID/同安全/同 Domain + 组建移动域 |
| **覆盖重叠不足** | 客户端走到很远才切换 | AP 间距按"最远覆盖"设计 | 重叠 15%–20%，切换点差值 ≤ 5 dB |
| **分支只用 FlexConnect 本地转发** | WAN 断链次日全员连不上 | 无本地 DHCP / 本地认证 | 本地 DHCP + Local Auth + 断链演练 |
| **CAPWAP 隧道 MTU 未规划** | 大包丢、性能异常 | 隧道封装 + 分片 | AP-WLC 路径 MTU ≥ 1550 |
| **防火墙未放行 CAPWAP** | AP 卡在 Join | UDP 5246/5247 单向或未放行 | 双向放行 + ICMP + NTP |
| **DHCP Option 43 缺失** | 跨网段 AP 找不到控制器 | 依赖广播发现 | Option 43 或 DNS 指向 |
| **RADIUS 单点** | 全网新关联失败 | 认证服务器未冗余 | 至少 2 节点 + 多 server 配置 |
| **EAP 客户端未校验服务端证书** | 钓鱼 AP 可窃取域凭据 | 终端配置基线缺失 | 强制证书校验 + SSID 白名单 |
| **组播/广播未抑制** | 视频监控/投屏把 airtime 打满 | 组播以最低速率发送 | 组播转单播 + IGMP Snooping |
| **DHCP 池按人数配** | "连上但上不了网" | 未考虑并发 + 租期 | 按峰值 × 1.5，缩短租期 |
| **AP 上行只有 1 G** | Wi-Fi 6 AP 速率被上游卡住 | 未上 mGig | 2.5G/5G 上行 + Cat6a |
| **PoE 功率不足** | AP 降级（关射频/降 MIMO） | 用 802.3af 带 Wi-Fi 6 AP | 802.3at/bt，核对 AP 功率需求 |
| **直接切纯 WPA3** | 一批老终端失联 | 未做终端兼容矩阵 | 分 SSID 过渡 + 回滚方案 |
| **6 GHz 期待覆盖兜底** | 终端看不到 SSID | 6 GHz 仅 6E/7 终端、强制 WPA3 | 5 GHz 保覆盖，6 GHz 做容量 |
| **验收在空场测** | 上线后高峰崩 | 测试场景不代表真实负载 | 在最坏时刻做主动勘测 |
| **忽略 6 GHz 的 AFC** | 室外/标准功率部署无法启用 | 未提前申请 AFC 服务 | 项目早期确认功率等级与 AFC |
| **按"每 AP 支持 N 人"选型** | 高峰必崩 | 厂商标称值是实验室数字 | 用 airtime/pps 模型自算（本章算例） |
| **SSID 按部门开** | 空口被 Beacon 吃掉 10%+ | 每 SSID 一份 Beacon，广播用最低速率 | SSID ≤ 4 + 动态 VLAN/角色下发 |
| **只算带宽不算 pps** | 按带宽算够了，实际上线后 airtime 爆表 | 小包场景固定开销占比极高 | 用 pps × 单帧 airtime 校核 |
| **忽略 Low-E 玻璃/金属货架** | 图纸全绿、现场有盲区 | 材料衰减参数与假设偏差 20 dB+ | 必须现场勘测，不用图纸模型定案 |
| **AP 装在吊顶内/金属遮挡** | 覆盖凭空少一半 | 安装工程未纳入设计 | 安装规范写进施工交底 |
| **AP 功率拉满** | 上下行不对称、假覆盖、漫游差 | 未做功率规划 | AP 功率匹配终端（5–14 dBm） |
| **RRM 全自动开在 IoT/语音场景** | 凌晨集体掉线、通话中断 | DCA 全信道重算 + 老设备不支持快速漫游 | 限制幅度/时间窗，关键 SSID 冻结 |
| **IoT 塞进员工 SSID** | 横向攻击、airtime 被拖垮 | 未做设备分段 | 独立 SSID + iPSK + 客户端隔离 + 出口白名单 |
| **DHCP 池按人数配 1.2 倍** | 活动开始 10 分钟池耗尽 | 私有 MAC 随机化使租约数 1.5–2 倍 | 按人数 × 2.5 配，缩短租期 |
| **RADIUS 容量按并发数算** | 开场认证洪峰排队 | 未考虑首次+重认证+CoA | 按峰值认证速率设计，加节点与连接池 |
| **三层漫游滥用** | 专线被打满、时延翻倍、单点 | 用网络层隧道硬扛会话保持 | 先问"业务能否容忍 IP 变化"，优先应用层重连 |
| **组播直通当默认** | 一路视频吃掉 1/3 射频 | 组播无 ACK、按最低速率发 | 转单播 + IGMP Snooping + 限制并发观看 |
| **验收在空场测** | 上线高峰崩 | 测试不代表真实负载 | 最坏时刻 + 真实终端 + 混合业务压测 |
| **只做技术交付不做运维移交** | 上线 3 个月后失控 | 无基线、无告警、无预案 | 交付文档八件套 + 监控阈值 + 演练 |

</div>

---

## Key Terms · 本章关键术语

| Term | Meaning |
|------|---------|
| 802.11ax | Wi-Fi 6/6E |
| 802.11be | Wi-Fi 7 |
| WLC | Wireless LAN Controller |
| CAPWAP | Control and Provisioning of Wireless Access Points |
| Local Mode | Local mode (data and control tunnelled back to the WLC) |
| FlexConnect | Flexible Connect mode (local switching) |
| WPA3 | Wi-Fi Protected Access version 3 |
| SAE | Simultaneous Authentication of Equals |
| 802.1X/EAP | Port-based authentication |
| High-Density Design | High-density design |
| BSS Coloring | BSS colouring |
| CAC | Call Admission Control |
| Fast Roaming | Fast roaming |
| 802.11r | Fast BSS Transition |
| Band Steering | Band steering |
| Airtime | Medium time (the real scarce resource in wireless) |
| CCI | Co-Channel Interference |
| SNR | Signal-to-Noise Ratio |
| RSSI | Received Signal Strength Indicator |
| MIN RSSI | Minimum RSSI (forced-disconnect threshold) |
| RRM | Radio Resource Management (automatic channel/power) |
| BSS / BSSID / SSID | Basic Service Set / BSS identifier (AP radio MAC) / network name |
| ESS | Extended Service Set (multiple BSSs sharing one SSID) |
| DFS | Dynamic Frequency Selection (radar channels) |
| TPC | Transmit Power Control |
| UNII | The 5 GHz unlicensed band subdivisions |
| LPI / VLP / AFC | 6 GHz low-power indoor / very low power / Automatic Frequency Coordination |
| OFDMA | Orthogonal Frequency Division Multiple Access (the core efficiency feature of Wi-Fi 6) |
| MU-MIMO | Multi-User Multiple Input Multiple Output |
| MLO | Multi-Link Operation (Wi-Fi 7) |
| TWT | Target Wake Time (IoT power saving) |
| A-MPDU | Frame aggregation (aggregating multiple MPDUs) |
| MCS | Modulation and Coding Scheme (determines the rate tier) |
| Spatial Stream | Spatial stream |
| WMM / EDCA | Wi-Fi Multimedia / Enhanced Distributed Channel Access |
| AC_VO / AC_VI / AC_BE / AC_BK | The four WMM access categories |
| UP | User Priority (the 802.11 QoS marking) |
| DSCP / EF / AF41 | IP-layer QoS markings |
| DIFS / SIFS | Distributed / Short Interframe Space |
| CSMA/CA | Carrier Sense Multiple Access with Collision Avoidance |
| Slot Time | Slot time (backoff granularity: 9 µs in 5 GHz / 20 µs in 2.4 GHz) |
| NAV | Network Allocation Vector (virtual carrier sense reserving channel time) |
| Hidden / exposed terminal | Cannot hear each other and collide / wrongly believes the channel is busy |
| RTS / CTS | Request To Send / Clear To Send (trading two frames for the collision cost of a long frame) |
| A-MSDU | MSDU-level aggregation |
| Block ACK | Block acknowledgement (acknowledging a whole batch at once) |
| Preamble | Preamble (fixed per-frame overhead, about 40 µs in 11ax) |
| Minstrel | A common rate adaptation algorithm (per-client MCS selection) |
| Airtime black hole | Weak-signal low-rate clients consuming huge amounts of medium time |
| EIRP | Equivalent Isotropically Radiated Power (Tx + antenna gain − feeder loss) |
| FSPL | Free Space Path Loss |
| Low-E glass | Low-emissivity coated glass (can attenuate 5 GHz by up to 30 dB) |
| Downtilt | Downtilt antenna (for venues and high-ceiling spaces) |
| DTIM | Delivery Traffic Indication Message period (balance between power saving and multicast delay) |
| DCA | Dynamic Channel Allocation (RRM channel optimisation) |
| RX-SOP | Receiver Start of Packet threshold (improves spatial reuse, may "not hear" distant clients) |
| Probe Request / Response | Probe request/response (client scanning and AP replies, consuming airtime) |
| RNR element | Reduced Neighbor Report (6 GHz SSIDs are indicated inside 5 GHz Beacons) |
| BTM | BSS Transition Management (the 802.11v steering message) |
| Hysteresis | Hysteresis (the threshold gap that prevents ping-pong roaming) |
| Ping-Pong Roaming | Ping-pong roaming (flapping between two APs) |
| Sticky Client | Sticky client (lingering on a weak-signal AP) |
| mDNS / Bonjour | Link-local multicast name resolution (relied on by screen mirroring and printer discovery) |
| Multicast-to-Unicast | Multicast-to-unicast (sending multicast streams as unicast over the air) |
| Multicast Direct | Multicast Direct (broadcast at the lowest rate) |
| iPSK / dPSK / PPSK | Per-device / dynamic / per-user pre-shared key |
| SGT / TrustSec | Security Group Tag (used for micro-segmentation) |
| CoA | Change of Authorization (dynamic RADIUS policy change) |
| Dead Time | The period during which a failed authentication server is skipped |
| Session Timeout | Session timeout (re-authentication interval) |
| Private MAC Randomization | Private MAC randomisation (breaks MAC-based counting and authentication) |
| AP-on-a-stick | Single-AP on-site survey method |
| WLC HA SSO | Controller active/standby state synchronisation (switchover < 1 s) |
| APSP | AP Service Pack (AP firmware bundle that must match the WLC release) |
| PMK / PTK | Pairwise Master Key / Pairwise Transient Key |
| OKC / PKC / CCKM | Opportunistic / Proactive Key Caching / Cisco Centralized Key Management |
| 802.11k | Radio Resource Measurement (neighbour reports) |
| 802.11v | BSS Transition Management (steering clients to another AP) |
| 802.11r / FT | Fast BSS Transition |
| 802.11w / PMF | Management Frame Protection |
| Adaptive 11r | Adaptive 802.11r (falls back for unsupported endpoints) |
| Mobility Group / Domain | Mobility group / mobility domain |
| Anchor / Foreign | Anchor / foreign controller (Layer 3 roaming) |
| DTLS | Transport-layer encryption for CAPWAP |
| AP Group / Tag | AP grouping / tags (Site/Policy/RF Tag) |
| Local Switching | Local switching (data stays at the AP) |
| Local Auth | Local authentication (site autonomy when the link is down) |
| Rogue AP | Rogue access point |
| wIPS | Wireless Intrusion Prevention System |
| OWE | Opportunistic Wireless Encryption |
| GCMP | Galois/Counter Mode Protocol (WPA3 cipher) |
| Supplicant / Authenticator | Client / authenticator (the AP) in 802.1X |
| EAP-TLS / PEAP / EAP-TTLS / TEAP / EAP-FAST | EAP authentication methods |
| RADIUS | Remote Authentication Dial-In User Service |
| Portal authentication | Captive portal authentication (guests) |
| Airtime Fairness | Airtime fairness (sharing by time rather than by frame count) |
| mDNS gateway | mDNS proxy/reflector (lets Bonjour cross Layer 3 boundaries) |
| IGMP Snooping | Layer 2 multicast listener discovery (stops multicast flooding) |
| PoE / 802.3af / at / bt | Power over Ethernet (15.4 W / 30 W / 60–90 W per port) |
| mGig | Multi-Gigabit Ethernet (2.5G/5G/10G over copper) |
| P95 latency | 95th-percentile latency (the standard way to express tail latency) |
| Worst moment | The worst moment (the moment acceptance must be performed) |
| Service ceiling | The service ceiling (the boundary of what the design commits to deliver) |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| 802.11ax | Wi-Fi 6/6E |
| 802.11be | Wi-Fi 7 |
| WLC | 无线局域网控制器 |
| CAPWAP | 无线接入点控制和配置协议 |
| Local Mode | 本地模式 |
| FlexConnect | 弹性连接模式 |
| WPA3 | Wi-Fi 保护访问第 3 版 |
| SAE | 对等同步认证 |
| 802.1X/EAP | 基于端口的认证 |
| High-Density Design | 高密度设计 |
| BSS Coloring | BSS 着色 |
| CAC | 呼叫准入控制 |
| Fast Roaming | 快速漫游 |
| 802.11r | 快速 BSS 切换 |
| Band Steering | 频段引导 |
| Airtime | 介质时间（无线真正的稀缺资源） |
| CCI | 同频干扰（Co-Channel Interference） |
| SNR | 信噪比 |
| RSSI | 接收信号强度 |
| MIN RSSI | 最小接收信号强度（强制断开阈值） |
| RRM | 无线资源管理（自动信道/功率） |
| BSS / BSSID / SSID | 基本服务集 / BSS 标识（AP 射频 MAC）/ 网络名 |
| ESS | 扩展服务集（同一 SSID 的多个 BSS） |
| DFS | 动态频率选择（雷达信道） |
| TPC | 发射功率控制 |
| UNII | 5 GHz 的非授权频段划分 |
| LPI / VLP / AFC | 6 GHz 低功率室内 / 超低功率 / 自动频率协调 |
| OFDMA | 正交频分多址（Wi-Fi 6 的核心效率特性） |
| MU-MIMO | 多用户多入多出 |
| MLO | 多链路操作（Wi-Fi 7） |
| BSS Coloring | BSS 着色（同频并行传输） |
| TWT | 目标唤醒时间（IoT 省电） |
| A-MPDU | 帧聚合（聚合多个 MPDU） |
| MCS | 调制与编码策略（决定速率档位） |
| Spatial Stream | 空间流 |
| WMM / EDCA | Wi-Fi 多媒体 / 增强分布式信道访问 |
| AC_VO / AC_VI / AC_BE / AC_BK | WMM 的四个接入类别 |
| UP | 用户优先级（802.11 QoS 标记） |
| DSCP / EF / AF41 | IP 层 QoS 标记 |
| CAC | 呼叫准入控制 |
| DIFS / SIFS | 分布式/短帧间间隔 |
| CSMA/CA | 载波侦听多路访问/冲突避免 |
| PMK / PTK | 成对主密钥 / 成对临时密钥 |
| OKC / PKC / CCKM | 机会密钥缓存 / 主动密钥缓存 / 集中密钥管理 |
| 802.11k | 无线资源测量（邻居报告） |
| 802.11v | BSS 过渡管理（引导客户端换 AP） |
| 802.11r / FT | 快速 BSS 过渡 |
| 802.11w / PMF | 管理帧保护 |
| Adaptive 11r | 自适应 802.11r（对不支持的终端回退） |
| Mobility Group / Domain | 移动组 / 移动域 |
| Anchor / Foreign | 锚点 / 外地控制器（三层漫游） |
| WLC | 无线局域网控制器 |
| CAPWAP | 无线接入点控制和配置协议（UDP 5246/5247） |
| DTLS | CAPWAP 的传输层加密 |
| AP Group / Tag | AP 分组 / 标签（Site/Policy/RF Tag） |
| FlexConnect / H-REAP | 弹性连接（本地转发） |
| Local Switching | 本地交换 |
| Local Auth | 本地认证（断链自治） |
| Rogue AP | 非法 AP |
| wIPS | 无线入侵防御系统 |
| MFP / Management Frame Protection | 管理帧保护（同 802.11w） |
| PPSK / iPSK / dPSK | 每用户/每设备预共享密钥 |
| SAE | 对等同步认证（WPA3-Personal） |
| OWE | 机会无线加密（开放网络加密） |
| GCMP | Galois/Counter 模式协议（WPA3 加密算法） |
| 802.1X / Supplicant / Authenticator | 端口认证 / 客户端 / 认证者（AP） |
| EAP-TLS / PEAP / EAP-TTLS / TEAP / EAP-FAST | EAP 认证方法 |
| RADIUS / CoA | 远程认证拨号用户服务 / 授权变更 |
| Portal 认证 | 门户认证（访客） |
| Multicast-to-Unicast | 组播转单播 |
| Airtime Fairness | 介质时间公平性 |
| Sticky Client | 粘滞客户端 |
| AP-on-a-stick | 临时单 AP 实地勘测法 |
| CMX / 定位服务 | 无线定位与位置分析（可选扩展） |
| CSMA/CA | 载波侦听多路访问/冲突避免（无线介质访问机制） |
| Slot Time | 时隙（退避粒度，5 GHz 9 µs / 2.4 GHz 20 µs） |
| NAV | 网络分配向量（虚拟载波侦听，预约信道时间） |
| 隐藏终端 / 暴露终端 | 互相听不到导致碰撞 / 误以为信道忙而不敢发 |
| RTS / CTS | 请求发送 / 允许发送（用两帧换长帧的碰撞代价） |
| A-MPDU / A-MSDU | 帧聚合（MPDU 级 / MSDU 级） |
| Block ACK | 块确认（一次确认整批帧） |
| Preamble | 前导码（每帧固定开销，11ax 约 40 µs） |
| Minstrel | 常用的速率自适应算法（按客户端独立选 MCS） |
| Airtime 黑洞 | 弱信号低速客户端占用大量介质时间 |
| EIRP | 等效全向辐射功率（Tx + 天线增益 − 馈线损耗） |
| FSPL | 自由空间路径损耗 |
| Low-E 玻璃 | 低辐射镀膜玻璃（对 5 GHz 衰减可达 30 dB） |
| Downtilt | 下倾天线（场馆/高挑高空间用） |
| DTIM | 交付流量指示消息周期（省电与组播延迟的平衡） |
| DCA | 动态信道分配（RRM 的信道优化） |
| RX-SOP | 接收信号起始阈值（提高空间复用，也可能"听不到"远端） |
| Probe Request / Response | 探测请求/响应（客户端扫描与 AP 应答，消耗 airtime） |
| RNR 元素 | 缩减邻居报告（6 GHz 的 SSID 通过 5 GHz Beacon 指示） |
| BTM | BSS 过渡管理（802.11v 的引导换 AP 消息） |
| Hysteresis | 滞回（防止乒乓漫游的阈值差） |
| Ping-Pong Roaming | 乒乓漫游（在两 AP 间反复切换） |
| Sticky Client | 粘滞客户端（赖在弱信号 AP 不走） |
| mDNS / Bonjour | 链路本地组播域名解析（投屏、打印机发现依赖它） |
| Multicast-to-Unicast | 组播转单播（无线侧把组播流改为单播发送） |
| Multicast Direct | 组播直通（以最低速率在空口广播） |
| iPSK / dPSK | 每设备预共享密钥 |
| SGT / TrustSec | 安全组标签（用于微隔离） |
| CoA | 授权变更（RADIUS 动态改策略） |
| Dead Time | 认证服务器失效期间（跳过该服务器的时长） |
| Session Timeout | 会话超时（重认证周期） |
| Private MAC Randomization | 私有 MAC 随机化（导致租约数与 MAC 认证失效） |
| AP-on-a-stick | 单 AP 实地勘测法 |
| WLC HA SSO | 控制器主备状态同步（切换 < 1 s） |
| APSP | AP Service Pack（AP 固件包，需与 WLC 版本匹配） |

</div>

---

## Practical Experience Summary · 实战经验总结

1. **The first principle of wireless design is airtime, not coverage area.** First compute "how many microseconds per second can be shared out", then compute how many APs are needed. Any design that skips airtime and starts drawing coverage maps will be reworked in high-density scenarios.
2. **Power, channel width, MIN RSSI and disabled low rates must be tuned together.** Changing any one of them alone produces almost no effect, while changing all four together can double the capacity of the same hardware. This is the highest return-on-effort set of actions available.
3. **Roaming experience is a product of coverage design; protocols are only an accelerator.** 802.11r/k/v can save a few hundred milliseconds, but if the signal at the switch point is only −80 dBm, being faster still means disconnecting. Fix coverage overlap first, then talk about fast roaming.
4. **Branch wireless must assume "the WAN can drop at any moment".** FlexConnect only solves data backhaul; local DHCP + local authentication are what determine "whether people can work after the link drops". Redundancy that has never been drilled is no redundancy at all.
5. **Security upgrades must be staged by endpoint capability, never cut over in one step.** WPA3 is the direction, but existing endpoints, IoT and medical devices will not upgrade on the same day. Split SSIDs + transition mode + a rollback plan is the only executable path.
6. **Wireless faults must always be examined across four layers**: RF (signal/interference/airtime), controller (AP state/configuration), wired (DHCP/VLAN/MTU/multicast) and authentication (RADIUS/certificates/policy). Hunting for causes only on wireless gear misses most real root causes.
7. **Acceptance must happen at the worst moment, and metrics must be quantifiable.** "−67 dBm / SNR 25 dB / airtime < 60% / roaming < 50 ms / retries < 10%" — writing those five numbers into the delivery document is ten thousand times more useful than "the user experience is good".
8. **Bandwidth math systematically underestimates AP requirements; always verify with pps.** For small-frame workloads (voice, scanning, IoT, live comments, interactive teaching) the cost sits in **per-frame fixed overhead**, not in the number of bits. Whenever a scenario involves "many people + small frames", add 20%–40% to the AP count computed from bandwidth.
9. **The capacity of peripheral systems matters as much as the wireless itself.** DHCP (people × 2.5), RADIUS (peak authentication rate), egress bandwidth (0.8 Mbps per person) and NAT session tables — if any one of those is short, perfect wireless design is still useless. That is exactly where large events fail.
10. **Automation must leave an escape route for fragile devices.** RRM/DCA, automatic policy re-push and scheduled optimisation are improvements for staff endpoints and potentially catastrophic for old IoT and medical devices. The rule: **freeze automation for critical SSIDs; give automation an amplitude ceiling, a time window and a rollback.**
11. **Layer 3 roaming is a last resort, not an advanced option.** When faced with "the IP cannot change", ask three questions first: can the application tolerate a reconnect? can the same subnet be used? can the application layer preserve the session? Only when all three fail should you use an Anchor — and be prepared to carry the hairpinned bandwidth and single-point risk.
12. **Endpoint capability must be locked down at procurement.** Dual/tri-band, 11ax/6E support, 11k/v/r support, reliability of the roaming implementation, 802.1X support — those attributes determine how many cards the wireless design has to play. **Changing the design after the devices are bought costs you the whole solution.**
13. **The time pattern of a fault is worth more than any command.** "2 a.m. every day", "Monday morning", "whenever it rains" — those patterns point directly at scheduled tasks, backup windows and environmental factors. The first step of troubleshooting should be **asking about the timeline**, not logging into devices.

<div class="zh" markdown="1">

1. **无线设计的第一性原理是 airtime，不是覆盖面积。** 先算"每秒有多少微秒可以分"，再算需要多少 AP。任何跳过 airtime 直接画覆盖图的设计，都会在高密度场景返工。
2. **功率、信道宽度、MIN RSSI、禁用低速率，这四项必须一起调。** 单独改任何一项都几乎没有效果，四项同调能让同一套硬件容量翻倍。这是投入产出比最高的一组动作。
3. **漫游体验是覆盖设计的产物，协议只是加速器。** 802.11r/k/v 能省下几百毫秒，但如果切换点信号只有 -80 dBm，再快也是断。先修覆盖重叠，再谈快速漫游。
4. **分支无线必须假设"WAN 随时会断"。** FlexConnect 只解决数据回传，本地 DHCP + 本地认证才解决"断链后还能不能上班"。冗余没演练过，等于没有。
5. **安全升级要按终端能力分批，不要一刀切。** WPA3 是方向，但存量终端、IoT、医疗设备不会同一天升级。分 SSID + 过渡模式 + 回滚方案，是唯一可执行路径。
6. **无线故障永远要跨四层看**：RF（信号/干扰/airtime）、控制器（AP 状态/配置）、有线（DHCP/VLAN/MTU/组播）、认证（RADIUS/证书/策略）。只在无线设备上找原因，会错过大部分真实根因。
7. **验收必须在最坏时刻做，指标必须可量化。** "-67 dBm / SNR 25 dB / airtime < 60% / 漫游 < 50 ms / 重传 < 10%"，这五个数字写进交付文档，比"用户体验良好"有用一万倍。
8. **带宽算法会系统性低估 AP 需求，必须用 pps 校核。** 小包业务（语音、扫码、IoT、弹幕、互动教学）的成本在"每帧固定开销"，不在比特数。凡是"人多 + 小包"的场景，按带宽算出的 AP 数通常要再加 20%–40%。
9. **外围系统的容量与无线同等重要。** DHCP（按人数 ×2.5）、RADIUS（按峰值认证速率）、出口带宽（按人均 0.8 Mbps）、NAT 会话表 —— 这四项任何一个不够，无线做得再好也白搭。大型活动的失败点几乎都在这里。
10. **自动化要为"脆弱设备"留退路。** RRM/DCA、自动重下发、定时优化，对员工终端是优化，对老 IoT 与医疗设备可能是灾难。规则：**关键 SSID 冻结自动优化、自动化有幅度上限、有时间窗、有回滚**。
11. **三层漫游是最后手段，不是高级选项。** 遇到"IP 不能变"的需求，先问三问：业务能否容忍重连？能否用同子网？应用层能否保持会话？三条都走不通，才用 Anchor，并准备好承担折返带宽与单点风险。
12. **终端能力要在采购阶段就锁定。** 双频/三频、是否支持 11ax/6E、是否支持 11k/v/r、漫游实现是否可靠、是否支持 802.1X —— 这些属性决定了无线设计有多少牌可打。**设备买回来之后再改设计，代价是重构整个方案。**
13. **故障时间规律比任何命令都值钱。** "每天凌晨 2 点""每周一早上""每次下雨"——这些规律直接指向定时任务、备份窗口、环境因素。排障第一步应该是**问时间线**，而不是登设备。

</div>

---

## Design Scenario Drills (Wireless, Three Exercises) · 设计情景演练（无线，三道）

These scenarios share one characteristic: **half the information is given, there is no single correct answer, and what is being tested is trade-offs and constraint identification.** The three below are based on real project scenarios — work them yourself first, then read the reference approach.

<div class="zh" markdown="1">

这类情景的特点是：**信息给一半，答案不唯一，看的是取舍与约束识别**。下面三道按真实项目场景编写，先自己做，再看参考思路。

</div>

### Scenario 1: Wireless Architecture for a Multi-Site Retail Enterprise · 情景一：多站点零售企业的无线架构

**Background**: a retail chain with 400 stores (2–8 APs each) and one headquarters (300 APs). Stores use MPLS plus an internet backup path; some stores have only 20 Mbps of WAN bandwidth and average two outages per month (1–4 hours each). Stores run wireless POS terminals, electronic shelf labels (2.4 GHz), customer Wi-Fi and inventory scanners. The IT team has 5 people covering the whole country.

<div class="zh" markdown="1">

**背景**：连锁零售企业 400 家门店（每店 2–8 台 AP）+ 1 个总部（300 台 AP）。门店使用 MPLS + 互联网双出口，部分门店 WAN 带宽 20 Mbps 且月均中断 2 次（每次 1–4 小时）。门店有 POS 收银（无线）、电子价签（2.4 GHz）、顾客 Wi-Fi、库存扫码枪。IT 团队 5 人，覆盖全国。

</div>

**Question**: propose the wireless architecture (controller deployment, forwarding mode, authentication, redundancy) and explain the cost of every choice you give up.

<div class="zh" markdown="1">

**问题**：给出无线架构（控制器部署、转发模式、认证、冗余），并说明每个选择放弃的代价。

</div>

<details markdown="1">
<summary>Reference analysis (write yours first)</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析（先自己写完再看）</summary>

</div>

**Constraint identification (list them before answering)**:
1. 400 sites with a 5-person IT team → **per-site operational cost must be extremely low**
2. 20 Mbps WAN that breaks often → **cannot depend on tunnelled backhaul or centralized authentication**
3. POS is the revenue system → **the business must not stop when the network drops**
4. Electronic shelf labels are 2.4 GHz → 2.4 GHz must be retained and supported long term
5. Customer Wi-Fi → needs isolation, rate limiting and compliant logging

<div class="zh" markdown="1">

**约束识别（先列，再答）**：
1. 400 个站点、5 人 IT 团队 → **单站点运维成本必须极低**
2. WAN 20 Mbps 且经常中断 → **不能依赖隧道回传与集中认证**
3. POS 是收银业务 → **断网不能停止营业**
4. 电子价签 2.4 GHz → 必须保留 2.4 GHz 且需长期支持
5. 顾客 Wi-Fi → 需要隔离、限速、合规日志

</div>

**Recommended architecture**:

<div class="zh" markdown="1">

**推荐架构**：

</div>

| Dimension | Choice | What it gives up |
|---|---|---|
| Control plane | **Cloud-managed** (or centralized at HQ + local survivability) | Depends on internet reachability; deep customisation is limited |
| Data plane | **Local forwarding (FlexConnect-style)** | No centralized auditing; local troubleshooting skills required |
| Authentication | **Centralized RADIUS + local survivability (fall back locally when the link drops)** | Two sets of credentials/certificates to maintain; more complex decisions |
| DHCP/DNS | **Local at each store (switch or router)** | Scattered configuration; requires unified templating |
| POS | **Separate SSID + separate VLAN + wired/4G backup** | Extra cost (4G modules); two paths to manage |
| Guest | **Local breakout to the internet + cloud portal** | Store egress IPs vary, complicating site selection policy |
| Electronic shelf labels | Separate 2.4 GHz SSID + iPSK + 11r disabled | Beacon cost; IoT security relies purely on isolation |

<div class="zh" markdown="1">

| 维度 | 选择 | 放弃的代价 |
|---|---|---|
| 控制面 | **云管理**（或总部集中管理 + 本地生存） | 依赖互联网可达；深度定制受限 |
| 数据面 | **本地转发（FlexConnect 类）** | 无集中审计；本地排障要求高 |
| 认证 | **本地生存 + 集中认证（RADIUS 在总部，断链回落本地）** | 需维护两套凭据/证书；决策复杂 |
| DHCP/DNS | **每店本地（交换机或路由器）** | 配置分散，需模板化统一 |
| POS | **独立 SSID + 独立 VLAN + 有线备份（4G）** | 成本（4G 模块）；管理两套路径 |
| 访客 | **本地 breakout 到互联网 + Portal（云端）** | 门店出口 IP 多变，选址策略复杂 |
| 电子价签 | 2.4 GHz 独立 SSID + iPSK + 关闭 11r | 空口 Beacon 成本；IoT 安全边界靠隔离 |

</div>

**Degradation behaviour that must be written into the proposal**: WAN down → existing clients stay up, new clients authenticate locally (pre-staged credentials), POS switches to the 4G backup, shelf labels continue updating locally.

<div class="zh" markdown="1">

**必须写进方案的降级行为**：WAN 断链 → 已有客户端保持、新客户端本地认证（预置凭据）、POS 走 4G 备份、价签本地更新。

</div>

**Common pitfalls**: tunnelling every store back to HQ (a WAN cut closes the store), centralized authentication only (nobody can work after a link drop), and five SSIDs for five device classes (Beacon cost).

<div class="zh" markdown="1">

**常见坑**：把所有门店隧道回总部（WAN 断即停业）、只做集中认证（断链后无法上班）、为每类设备开 5 个 SSID（Beacon 成本）。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 2: Coexistence of Voice and Medical IoT in an Inpatient Building · 情景二：医院住院部的语音 + 医疗 IoT 共存

**Background**: a 12-floor inpatient building must simultaneously support ① 900 wireless handsets (mobile rounds, roaming < 50 ms required); ② 1,200 medical telemetry devices (2.4 GHz, no 11r support, static IPs); ③ 3,000 staff laptops/phones; ④ guests. Existing 5 GHz coverage is good; 2.4 GHz is congested.

<div class="zh" markdown="1">

**背景**：住院部 12 层，需同时支持：①无线话机 900 台（移动查房，要求漫游 < 50 ms）；②医疗遥测 1,200 台（2.4 GHz，不支持 11r，固定 IP）；③员工笔记本/手机 3,000 台；④访客。现有 5 GHz 覆盖良好，2.4 GHz 拥挤。

</div>

**Question**: how should bands and SSIDs be divided? Which features must be enabled and which must be disabled? Give the acceptance metrics.

<div class="zh" markdown="1">

**问题**：频段与 SSID 如何划分？哪些特性必须开、哪些必须关？给出验收指标。

</div>

<details markdown="1">
<summary>Reference analysis</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Division principle: split SSIDs by "capability", split VLANs by "service", and never split SSIDs by department.**

<div class="zh" markdown="1">

**划分原则：按"能力"分 SSID，按"业务"分 VLAN，绝不按部门分 SSID。**

</div>

| SSID | Band | Security | Must enable | Must disable |
|---|---|---|---|---|
| Staff voice/data | 5 GHz (+6 GHz optional) | WPA3-Enterprise / 802.1X | 11k, 11v, Adaptive 11r, WMM+CAC, PMK caching, MIN RSSI −65 | — |
| Medical telemetry | **2.4 GHz dedicated** | WPA2-PSK/iPSK | Client isolation, egress whitelist, multicast suppression | **11r, 11k/v, RRM automatic channel optimisation on that VLAN** |
| Guest | 5 GHz | OWE/portal | Layer 2 isolation, rate limiting, internet only | Any internal reachability |

<div class="zh" markdown="1">

| SSID | 频段 | 安全 | 必须开 | 必须关 |
|---|---|---|---|---|
| 员工语音/数据 | 5 GHz（+6 GHz 可选） | WPA3-Enterprise / 802.1X | 11k、11v、Adaptive 11r、WMM+CAC、PMK 缓存、MIN RSSI -65 | — |
| 医疗遥测 | **2.4 GHz 独占** | WPA2-PSK/iPSK | 客户端隔离、出口白名单、组播抑制 | **11r、11k/v、RRM 自动信道对该 VLAN 的优化** |
| 访客 | 5 GHz | OWE/Portal | 二层隔离、限速、仅互联网 | 内网可达性 |

</div>

**Key trade-off notes**:
- Enabling 11r for voice is mandatory (roaming < 50 ms), but **it cannot be enabled on every SSID** (it would break telemetry) → **differentiate per SSID**
- The answer to congested 2.4 GHz is not "push telemetry onto 5 GHz" (the devices do not support it) but **dedicated 2.4 GHz channel planning for telemetry plus turning off 2.4 GHz broadcast for the staff SSID**
- Telemetry devices with static IPs **must not use dynamic VLAN assignment**: a CoA-driven VLAN change drops the device offline

<div class="zh" markdown="1">

**关键取舍说明**：
- 语音开 11r 是硬要求（漫游 < 50 ms），但**不能全 SSID 开**（会把遥测打掉）→ **按 SSID 差异化**
- 2.4 GHz 拥挤的解法不是"把遥测推到 5 GHz"（设备不支持），而是**给遥测专用 2.4 GHz 信道规划 + 关闭员工 SSID 的 2.4 GHz 广播**
- 固定 IP 的遥测设备**不能走动态 VLAN**（CoA 改 VLAN 会让设备失联）

</div>

**Acceptance metrics (signable)**:
| Item | Metric |
|---|---|
| Voice roaming | < 50 ms; MOS ≥ 4.0; dropped-call rate < 0.5% |
| Telemetry stability | 72 h with zero drops; single drops < 1 per week |
| 2.4 GHz airtime | Peak < 55% |
| Staff association success | > 99.5% |
| Telemetry association success | > 99.9% (critical devices) |

<div class="zh" markdown="1">

**验收指标（可签字）**：
| 项 | 指标 |
|---|---|
| 语音漫游 | < 50 ms，MOS ≥ 4.0，掉话率 < 0.5% |
| 遥测稳定性 | 72 h 零掉线；单个掉线 < 1 次/周 |
| 2.4 GHz airtime | 峰值 < 55% |
| 员工关联成功率 | > 99.5% |
| 遥测关联成功率 | > 99.9%（关键设备） |

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 3: One-Off Event Support for a Large Venue · 情景三：大型场馆的一次性活动保障

**Background**: an 8,000-seat arena hosting 20 events a year (matches and concerts), otherwise empty. The requirement is that during events "everyone can post to social media and watch live streams", with a limited budget, and no appetite for buying permanent equipment sized for the peak.

<div class="zh" markdown="1">

**背景**：体育馆 8,000 座，一年 20 场活动（赛事/演唱会）。日常空置。要求活动期间"人人能发朋友圈、能看直播"，预算有限，不希望为峰值采购永久设备。

</div>

**Question**: how do you meet the peak with three layers — "permanent + temporary + policy"? Which metrics must be locked down in advance?

<div class="zh" markdown="1">

**问题**：如何用"永久 + 临时 + 策略"三层满足峰值？哪些指标必须提前锁定？

</div>

<details markdown="1">
<summary>Reference analysis</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core idea: do not buy 100% of the permanent capacity for "20 days of peak per year".**

<div class="zh" markdown="1">

**核心思路：不要为"一年 20 天的峰值"买 100% 的永久容量。**

</div>

| Layer | Approach | Explanation |
|---|---|---|
| **Permanent base** | Zonal seating APs (downtilt directional) + public-area coverage, sized for "daily + medium events" (about 60% of peak) | Guarantees day-to-day and small events; it is the floor |
| **Temporary augmentation** | Extra APs during events (temporary rigging/carts) + temporary spectrum (6 GHz fully open) + temporary egress bandwidth (carrier day-by-day upgrades) | Per-event cost, no capital expenditure |
| **Policy layer** | Application rate limiting (2 Mbps per person for video classes), uplink live-stream limits, rate tiers by seating zone, authentication warm-up before doors open | Use policy to compress "per-person demand" into what can be carried |

<div class="zh" markdown="1">

| 层次 | 做法 | 说明 |
|---|---|---|
| **永久基础** | 座席分区 AP（下倾定向）+ 公共区域覆盖，按"日常 + 中等活动"容量设计（约 60% 峰值） | 保证日常与小型活动；是地板 |
| **临时增强** | 活动时增补 AP（临时吊装/推车）+ 临时频谱（6 GHz 全开）+ 临时出口带宽（运营商按天扩容） | 按天/按场次成本，不占资本开支 |
| **策略层** | 应用限速（视频类 2 Mbps/人）、限制上行直播、按票区划分 SSID/限速档、开场前预热认证 | 用策略把"人均需求"压到可承载范围 |

</div>

**Five numbers that must be locked down in advance**:
1. Peak concurrent clients (ticketing system + entry curve, at 85%)
2. Egress bandwidth (0.8 Mbps per person × peak concurrency) and the upgrade lead time (carriers usually need 3–7 days)
3. DHCP pools (people × 2.5) and the peak RADIUS authentication rate
4. The airtime red line (< 60%) and the corresponding AP count and channel width
5. A written statement of the service ceiling ("social sharing and standard-definition streaming supported; high-definition uplink not committed")

<div class="zh" markdown="1">

**必须提前锁定的五个数字**：
1. 峰值并发客户端（票务系统 + 入场曲线推算，按 85%）
2. 出口带宽（人均 0.8 Mbps × 峰值并发）与扩容周期（运营商通常 3–7 天）
3. DHCP 池（人数 × 2.5）与 RADIUS 峰值认证速率
4. airtime 红线（< 60%）与对应的 AP 数/信道宽度
5. 业务上限的书面声明（"支持社交分享与标清直播，不承诺高清上行"）

</div>

**The question you are most likely to be asked**: why not just rent all the APs temporarily? — Because **cabling, power, installation and surveying all take time**; temporary augmentation only adds capacity on top of existing infrastructure, and cannot replace base coverage.

<div class="zh" markdown="1">

**最容易被追问的一点**：为什么不干脆全部租用临时 AP？—— 因为**布线、供电、安装、勘测都需要时间**，临时增补只能覆盖"已有基础设施之上"的增量，不能替代基础覆盖。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

---

## Scenario Analysis Framework: The Generic Pattern for Wireless Scenarios · 情景分析框架：无线类场景的通用套路

```
① Write the constraints first      site count, WAN quality, endpoint capability, compliance, staffing, budget
② Then write the invariants        can the business run when the link drops, roaming latency, isolation requirements
③ Answer in layers                 RF → architecture → security → mobility → operations
④ State the cost of every choice   this is the dividing line between CCDE and CCIE
⑤ List the open issues             endpoint capability unconfirmed, AFC not approved, WAN SLA unsigned
⑥ Give acceptance and degradation  metrics + failure behaviour, proving the design is operable
```

<div class="zh" markdown="1">

```
① 先写约束（Constraint）       站点数、WAN 质量、终端能力、合规、人力、预算
② 再写不变量（What must hold）  断链能否营业、漫游时延、隔离要求
③ 分层作答                      RF → 架构 → 安全 → 移动性 → 运维
④ 每个选择都写代价（Trade-off）  这是 CCDE 与 CCIE 的分水岭
⑤ 写清未决项（Open issues）     终端能力未确认、AFC 未批、WAN SLA 待签
⑥ 给出验收与降级               指标 + 故障行为，证明方案"可运营"
```

</div>

**In one sentence**: **a wireless scenario question does not test "can you configure 802.11r", it tests "can you identify which three constraints in this scenario are non-negotiable and satisfy them at the lowest cost".**

<div class="zh" markdown="1">

**一句话总结**：**无线情景题考的不是"你会不会配 802.11r"，而是"你能不能识别出这个场景里哪三个约束是不可让步的，并用最小代价满足它们"。**

</div>

---

## Chapter Summary · 本章小结

Wireless looks like "a pile of protocols and standards", but its essence is the **engineering of three physical constraints**:

<div class="zh" markdown="1">

无线看起来是"一堆协议和标准"，本质却是**三个物理约束的工程化**：

</div>

| Constraint | Manifestation | Design response |
|------|------|---------|
| **Shared medium (half duplex)** | Capacity is determined by airtime, not by PHY rate | 20 MHz, low power, disabled low rates, multicast suppression, OFDMA |
| **The wireless link is probabilistic** | The rate varies with SNR; weak signals drag down the whole network | Cell-edge RSSI, MIN RSSI, coverage overlap, rate floor |
| **Mobility implies state migration** | Roaming must migrate keys, IP and QoS state | PMK caching, 802.11k/v/r, mobility domains, Layer 2 domains preferred |

<div class="zh" markdown="1">

| 约束 | 表现 | 设计应对 |
|------|------|---------|
| **共享介质（半双工）** | 容量由 airtime 决定，不由 PHY 速率决定 | 20 MHz、低功率、禁低速、组播抑制、OFDMA |
| **无线链路是概率性的** | 速率随 SNR 变化，弱信号拖累全网 | 边界 RSSI、MIN RSSI、覆盖重叠、速率下限 |
| **移动性带来状态迁移** | 漫游要迁移密钥、IP、QoS 状态 | PMK 缓存、802.11k/v/r、移动域、二层域优先 |

</div>

From the CCDE perspective, wireless design really has to answer six questions:

<div class="zh" markdown="1">

CCDE 视角下，无线设计真正要回答的六个问题：

</div>

1. **Is the airtime budget in each zone sufficient?** (Capacity — verify with pps, not just bandwidth)
2. **Do the coverage boundary and overlap support "roaming only when it is time to roam"?** (RF — −67 dBm boundary + 15%–20% overlap)
3. **Can this site still do business when the WAN or the controller fails?** (Availability — local forwarding + local authentication/DHCP)
4. **Does the endpoint capability matrix support the chosen encryption and roaming features?** (Security and compatibility — the entry conditions for 6 GHz/WPA3/11r)
5. **Is the capacity of peripheral systems (DHCP/RADIUS/egress) matched to the wireless?** (Operability — the real break point of large events)
6. **Can the acceptance metrics be reproduced and signed at the worst moment?** (Verifiability — the 15 test cases + stress-test method)

<div class="zh" markdown="1">

1. **每个区域的 airtime 预算够不够？**（容量 —— 用 pps 校核，不只用带宽）
2. **覆盖边界与重叠是否支撑"该漫游时才漫游"？**（RF —— -67 dBm 边界 + 15%–20% 重叠）
3. **WAN/控制器故障时，这个站点还能不能营业？**（可用性 —— 本地转发 + 本地认证/DHCP）
4. **终端能力矩阵是否支撑所选的加密与漫游特性？**（安全与兼容 —— 6 GHz/WPA3/11r 的准入）
5. **外围系统（DHCP/RADIUS/出口）的容量是否与无线匹配？**（可运营性 —— 大型活动的真正断点）
6. **验收指标能否在最坏时刻被复现、被签字？**（可验证性 —— 15 项用例 + 压测方法）

</div>

Answer those six questions clearly and which controller or which AP model to buy becomes an implementation detail.

<div class="zh" markdown="1">

这六问答清楚，具体选哪家控制器、哪款 AP 只是实现细节。

</div>

> 📌 **Next chapter (Chapter 12, Automation)** moves from "point design" to "operations at scale": with thousands of devices and hundreds of sites, CLI plus manual verification is no longer possible, and configuration models, templates, CI/CD and infrastructure as code become part of the design.

<div class="zh" markdown="1">

> 📌 **下一章（第 12 章 自动化）**将从"单点设计"转向"规模化运维"：当网络有几千台设备、上百个站点时，靠 CLI 与人工核对已经不可能，配置模型、模板、CI/CD 与基础设施即代码成为设计的一部分。

</div>
