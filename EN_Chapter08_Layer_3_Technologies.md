# Chapter 8: Layer 3 Technologies · 第 8 章：三层技术

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapter 8 (pp. 322–433)

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译 | 原书第 322-433 页

</div>

---

## Topics Covered in This Chapter · 本章涵盖主题

- **Enterprise Layer 3 routing**: link-state routing (OSPF/IS-IS), EIGRP, route summarization, traffic engineering and path selection
- **BGP routing**: BGP fundamentals, BGP as the core routing protocol, scalability options, route redistribution
- **Enterprise routing design recommendations**: how to choose the right routing protocol

<div class="zh" markdown="1">

- **企业三层路由**：链路状态路由（OSPF/IS-IS）、EIGRP、路由汇总、流量工程与路径选择
- **BGP 路由**：BGP 基础、BGP 作为核心路由协议、可扩展性选项、路由重分发
- **企业路由设计建议**：如何选择正确的路由协议

</div>

---

## Chapter Introduction: Five Counter-Intuitive Truths About Layer 3 Design · 本章导读：三层设计的五条反直觉认知

![Five counter-intuitive truths about Layer 3 design, with the mechanism behind each](assets/fig/en08-01-five-truths.svg)

### Counter-Intuitive Truth #1: Your Carefully Designed BGP Policy Can Be Silently Overridden by an IGP Metric · 反直觉一：你精心设计的 BGP 策略，会被 IGP 度量悄悄推翻

BGP path selection has 13 criteria, and the first six look precise enough — Weight, Local Preference, locally originated, AS_PATH, Origin, MED. Engineers usually build a complete design on those six, then discover during acceptance testing that "**nothing I change makes any difference**".

<div class="zh" markdown="1">

BGP 选路有 13 条判据，前 6 条看起来已经足够精细——Weight、Local Preference、本地起源、AS_PATH、Origin、MED。工程师通常在这六条上做完整设计，然后在验收时发现"**改了什么都没用**"。

</div>

The reason is usually criterion 8:

<div class="zh" markdown="1">

原因往往在第 8 条：

</div>

```
Criterion 8: lowest IGP metric to the NEXT_HOP
```

<div class="zh" markdown="1">

```
第 8 条：到 NEXT_HOP 的 IGP metric 最小
```

</div>

It sits **after MED**, which means that when the first seven are all tied, **the decision is handed to the IGP topology**. And the IGP metric is usually something nobody ever designed on purpose — a pile of default numbers derived from bandwidth.

<div class="zh" markdown="1">

它**排在 MED 之后**，意味着前面七条全平局时，**决定权交给 IGP 拓扑**。而 IGP 度量往往是谁也没特意设计过的东西——一堆默认按带宽算出来的数字。

</div>

| The control chain you think you have | The actual decision chain |
|--------------|------------|
| LP/MED decides the egress | LP ties → MED may be incomparable across ASes → **the IGP decides according to wherever it points** |
| "Paths inside one AS must be consistent" | Different border routers have different IGP costs → **one AS exits through different doors** |
| "Changing a BGP attribute takes effect" | `show ip bgp` shows a new best path, but the FIB does not change (recursion/multipath) |

<div class="zh" markdown="1">

| 你以为的控制链 | 实际的决策链 |
|--------------|------------|
| LP/MED 决定出口 | LP 平局 → MED 可能跨 AS 不可比 → **IGP 说到哪就去哪** |
| "同一个 AS 内路径一定一致" | 不同边界路由器上的 IGP 开销不同 → **同一个 AS 内走出不同的口** |
| "改了 BGP 属性就生效" | `show ip bgp` 显示 best 变了，但 FIB 没变（递归/多路径） |

</div>

> 💡 **Working principle number one in this chapter**: **When designing Layer 3 paths, you must look at BGP attributes and IGP metrics at the same time.** Look at only one of them and you will never be able to explain "why it won't move".

<div class="zh" markdown="1">

> 💡 **本章第一条工作原则**：**做三层路径设计时，必须同时看 BGP 属性和 IGP 度量。** 只看其中一个，你永远解释不了"为什么改不动"。

</div>

### Counter-Intuitive Truth #2: Choosing a Routing Protocol Is Not a Technical Question, It Is an "Operating Model" Question · 反直觉二：路由协议的选择不是技术问题，是"运维模型"问题

CCDE loves to ask "should this scenario use OSPF, IS-IS, or EIGRP". Beginners answer in terms of "which one is faster/better". The answer in a real project depends on **what you can maintain**:

<div class="zh" markdown="1">

CCDE 最爱问"这个场景该选 OSPF 还是 IS-IS 还是 EIGRP"。新手按"哪个更快/更好"回答。真实项目的答案取决于**你能维护什么**：

</div>

| Decision factor | Real weight |
|---------|---------|
| Which protocol the team knows | **Highest** (being able to troubleshoot beats theoretical optimality) |
| Whether the network is multivendor | High (EIGRP is now open but is still mostly Cisco) |
| What kind of path control is needed | Medium (fine-grained control → BGP) |
| Convergence speed | Medium (all of them can do sub-second, the difference is small) |
| Theoretical scalability of the protocol | **Low** (enterprise networks rarely actually hit protocol limits) |

<div class="zh" markdown="1">

| 决策因素 | 真实权重 |
|---------|---------|
| 团队熟悉哪个协议 | **最高**（能排障比理论最优更重要） |
| 是否有多厂商 | 高（EIGRP 已开放但仍以 Cisco 为主） |
| 需要什么样的路径控制 | 中（要精细控制 → BGP） |
| 收敛速度 | 中（都能做到亚秒，差异不大） |
| 协议的理论可扩展性 | **低**（企业网很少真的撞到协议上限） |

</div>

**A harsh but true judgment**: a network where the team has truly mastered OSPF troubleshooting but can only configure EIGRP without being able to debug it will be far more available than a network that "chose the theoretically better protocol that nobody understands".

<div class="zh" markdown="1">

**一个残酷但真实的判断**：一个团队能把 OSPF 排障搞透、但 EIGRP 只会配不会查的网络，比一个"选了理论上更优协议但没人懂"的网络可用性高得多。

</div>

> ⚠️ **The design document must state "why this protocol was chosen", and the reasoning must include operational capability**. Writing only "because OSPF is a standard protocol" is the same as writing nothing.

<div class="zh" markdown="1">

> ⚠️ **设计文档里必须写明"为什么选这个协议"，且理由要包含运维能力**。只写"因为 OSPF 是标准协议"，等于没写。

</div>

### Counter-Intuitive Truth #3: The Essence of Summarization Is "Hiding Information", and the Price Is "Losing Visibility" · 反直觉三：汇总的本质是"信息隐藏"，代价是"失去可见性"

Summarization is listed as a best practice and described with five benefits: saves memory, reduces flooding, isolates instability, speeds up convergence, improves security. But all of those benefits come from **one single action**: **throwing away the details**.

<div class="zh" markdown="1">

汇总被列为"最佳实践"，被讲成五个好处：省内存、少泛洪、隔离不稳定、加快收敛、提高安全性。但所有这些好处来自**同一个动作**：**把细节丢掉**。

</div>

```
Without summarization: the core knows every /24 in every area → one link fails, the core knows immediately, traffic detours
With summarization:    the core only knows 10.1.0.0/16 → a /24 fails, the core has no idea
        → as long as one more /24 is still reachable, the summary route stays up
        → traffic keeps being sent to that area → dropped inside the area (black hole)
```

<div class="zh" markdown="1">

```
不汇总：核心知道每个区域的每一条 /24 → 某条断了，核心立刻知道，流量绕行
汇总：  核心只知道 10.1.0.0/16 → 某条 /24 断了，核心完全不知道
        → 只要还有一条 /24 可达，汇总路由就还在
        → 流量继续送往那个区域 → 在区域内被丢弃（黑洞）
```

</div>

| What you gain | What you lose |
|---------|---------|
| A small routing table | Visibility of detailed failures |
| A small flooding domain | The ability to localize faults ("which subnet is actually broken") |
| Instability is isolated | The meaning of end-to-end verification (pinging the summary address works ≠ the service works) |
| Fast convergence | **Path correctness during the failure** |

<div class="zh" markdown="1">

| 你获得了 | 你失去了 |
|---------|---------|
| 路由表小 | 明细故障的可见性 |
| 泛洪范围小 | 故障定位能力（"到底哪个子网有问题"） |
| 不稳定性被隔离 | 端到端验证的意义（ping 汇总地址通≠业务通） |
| 收敛快 | **故障期间的路径正确性** |

</div>

> ⚠️ **The golden pairing for summarization is null0**: the summarizing router should also install a summary route pointing at null0, so that when "all details disappear" the summary route disappears too and no black hole is left behind. **A summary without null0 is a design flaw.**

<div class="zh" markdown="1">

> ⚠️ **汇总的黄金搭配是 null0**：汇总路由器上同时生成一条指向 null0 的汇总路由，这样"明细全部消失"时汇总路由也随之消失，不留下黑洞。**没有 null0 的汇总，是设计缺陷。**

</div>

### Counter-Intuitive Truth #4: Faster Convergence Is Not Always Better · 反直觉四：收敛不是"越快越好"

Cranking BFD down to 50 ms, Hello down to 1 s, and turning off all SPF throttling gives you a network that is **extremely fast to converge and extremely unstable**:

<div class="zh" markdown="1">

把 BFD 调到 50ms、Hello 调到 1s、SPF 节流全关掉，会得到一个**收敛极快但极不稳定**的网络：

</div>

| Symptom | Mechanism |
|------|------|
| A 200 ms link flap triggers an SPF run across the whole network | Frequent recomputation → CPU spikes → even slower |
| Route flapping causes traffic to switch back and forth | Every switch means packet loss + session resets |
| Multipath hashing is redistributed | The egress of the same TCP flow changes → **reordering, retransmissions, collapsed throughput** |

<div class="zh" markdown="1">

| 现象 | 机制 |
|------|------|
| 链路抖动 200ms 就触发全网 SPF | 频繁重算 → CPU 飙升 → 更慢 |
| 路由 flapping 导致流量反复切换 | 每次切换都是丢包 + 会话中断 |
| 多路径哈希重新分配 | 同一 TCP 流出口变了 → **乱序、重传、吞吐崩塌** |

</div>

**The correct approach is "tiered response"**:

<div class="zh" markdown="1">

**正确做法是"分级响应"**：

</div>

| Time scale | Tool | Purpose |
|---------|------|------|
| Milliseconds | Link detection (BFD, physical-layer alarms) | Fast detection, but **no immediate network-wide recomputation** |
| Hundreds of milliseconds | Local repair (FRR, TI-LFA, backup paths) | Switch over nearby, without disturbing the whole network |
| Seconds | IGP convergence (SPF recomputation) | Only happens when the first two tiers fail |
| Tens of seconds | BGP convergence, routing policy recomputation | Macro path adjustment |

<div class="zh" markdown="1">

| 时间尺度 | 手段 | 目的 |
|---------|------|------|
| 毫秒级 | 链路检测（BFD、物理层告警） | 快检测，但**不立即全网重算** |
| 百毫秒级 | 本地修复（FRR、TI-LFA、备份路径） | 就近切换，不惊动全网 |
| 秒级 | IGP 收敛（SPF 重算） | 只在前两级失败时发生 |
| 十秒级 | BGP 收敛、路由策略重算 | 宏观路径调整 |

</div>

> 💡 **Design principle**: the goal of convergence tuning is not "the shortest time" but "**recovery in the shortest time without letting a single flap shake the entire network**". Throttling is therefore not conservatism, it is a requirement.

<div class="zh" markdown="1">

> 💡 **设计原则**：收敛优化的目标不是"最短时间"，而是"**最短时间内恢复，同时不让一次抖动引发全网震荡**"。所以节流（throttling）不是保守，是必需。

</div>

### Counter-Intuitive Truth #5: Every Additional Protocol Doubles the Complexity, It Does Not Add One · 反直觉五：协议每增加一个，复杂度不是加一，是乘二

Single-protocol network: 1 path, 1 set of policies, 1 troubleshooting approach. Two-protocol network: **redistribution in 2 directions + loop risk + incomparable metrics + suboptimal paths**. Three-protocol network: **redistribution in 6 directions**.

<div class="zh" markdown="1">

单协议网络：1 条路径，1 套策略，1 种排障思路。双协议网络：**2 个方向的重分发 + 环路风险 + 度量不可比 + 次优路径**。三协议网络：**6 个方向的重分发**。

</div>

```
1 protocol:   A
2 protocols:  A↔B                    (2 directions)
3 protocols:  A↔B, A↔C, B↔C          (6 directions, and B↔C is usually created by accident)
```

<div class="zh" markdown="1">

```
1 个协议：  A
2 个协议：  A↔B                    （2 个方向）
3 个协议：  A↔B, A↔C, B↔C          （6 个方向，且 B↔C 往往是被动产生的）
```

</div>

**Incomparable metrics** are the core difficulty:

<div class="zh" markdown="1">

**度量不可比**是核心难题：

</div>

| From | To | Problem |
|----|----|------|
| OSPF (cost 1–65535) | EIGRP (composite metric, in the millions) | Cannot be converted, you can only guess a seed metric |
| EIGRP | BGP (AS_PATH + attributes) | The same prefix has different ADs in the two protocols — which one wins? |
| BGP | OSPF | Feeding BGP-learned routes into OSPF makes the IGP carry Internet-scale routes |

<div class="zh" markdown="1">

| 从 | 到 | 问题 |
|----|----|------|
| OSPF（cost 1–65535） | EIGRP（复合度量，百万级） | 无法换算，只能拍一个种子度量 |
| EIGRP | BGP（AS_PATH + 属性） | 同一前缀在两个协议里 AD 不同，选谁？ |
| BGP | OSPF | BGP 学来的路由再进 OSPF，会让 IGP 承担互联网规模路由 |

</div>

> ⚠️ **The single most important design recommendation in this chapter**: **keep the number of protocols small**. The complexity that dual-point, dual-direction redistribution brings almost always exceeds the problem it solves. If you can unify the core with BGP, do not stack another protocol conversion layer on top.

<div class="zh" markdown="1">

> ⚠️ **本章最重要的一条设计建议**：**协议数量要少**。双点双向重分发带来的复杂度，几乎永远超过它解决的问题。能用 BGP 统一核心，就不要叠一层协议转换。

</div>

---

## Layer 3 Design Methodology: Six Steps in Order · 三层设计方法论：六步定序

![The six steps of Layer 3 design, and what each one locks in](assets/fig/en08-02-six-steps.svg)

| Step | What must be decided | Consequence of getting it wrong |
|------|---------|-----------|
| **① Addressing plan and summarizability** | Does every area/site get a contiguous address block? | Not summarizable → the routing table explodes and every later design decision becomes damage control |
| **② Domain and hierarchy split** | How many IGP domains/areas? Where are the boundaries? | Too large → a big flooding domain; too small → complex summarization and paths |
| **③ Protocol selection** | Which IGP? Is BGP needed? | Wrong choice → operations cannot keep up (counter-intuitive truth #2) |
| **④ Path design** | How are primary/backup, load sharing, and traffic engineering done? | You draw lots with default tie-breakers → unpredictable behavior |
| **⑤ Convergence and stability** | Time budgets per stage, flap suppression strategy | Slow convergence or continuous flapping |
| **⑥ Boundaries and redistribution** | How do domains interact? One-way or two-way? | Loops, suboptimal paths, metric pollution |

<div class="zh" markdown="1">

| 步骤 | 要定的事 | 定错的后果 |
|------|---------|-----------|
| **① 地址规划与可汇总性** | 每个区域/站点分配连续地址块吗？ | 不可汇总 → 路由表爆炸，后面所有设计都在补救 |
| **② 域与层级划分** | 几个 IGP 域/区域？边界在哪？ | 区域过大 → 泛洪域大；过小 → 汇总与路径复杂 |
| **③ 协议选择** | IGP 选什么？要不要 BGP？ | 选错 → 运维跟不上（反直觉二） |
| **④ 路径设计** | 主备/负载分担/流量工程怎么做？ | 靠默认判据抽签 → 行为不可预测 |
| **⑤ 收敛与稳定性** | 各段时间预算、抖动抑制策略 | 收敛慢或持续震荡 |
| **⑥ 边界与重分发** | 域之间怎么交互？单向还是双向？ | 环路、次优、度量污染 |

</div>

**Why the addressing plan comes first**: **summarization capability is a product of the addressing plan, not of the protocol**. With contiguous addressing, any protocol can summarize; with messy addressing, no protocol can save you.

<div class="zh" markdown="1">

**为什么地址规划排第一**：**汇总能力是地址规划的产物，不是协议的产物**。地址分配连续，任何协议都能汇总；地址分配混乱，任何协议都救不了。

</div>

**Four hard rules for the addressing plan**:

<div class="zh" markdown="1">

**地址规划的四条硬规则**：

</div>

| Rule | Description |
|------|------|
| **Allocate hierarchically** (core → region → building → floor) | Ensures every layer can be covered by one prefix of the layer below |
| **Reserve growth space** (plan 2–3× per region) | Avoids "we added a building but its addresses are not contiguous, so we had to add routes" |
| **Give loopbacks/management addresses their own block** | Makes ACLs, iACLs, and routing policies easy to reference uniformly (Chapter 10) |
| **Plan Internet egress and the DMZ separately** | Simplifies NAT, security policy, and BGP advertisement |

<div class="zh" markdown="1">

| 规则 | 说明 |
|------|------|
| **按层次分配**（核心→区域→楼栋→楼层） | 保证每一层都能用一条前缀概括下一层 |
| **预留增长空间**（每区域按 2–3 倍规划） | 避免"新加一栋楼但地址不连续，只能新增路由" |
| **Loopback/管理地址单独成块** | 便于 ACL、iACL、路由策略统一引用（第 10 章） |
| **Internet 出口与 DMZ 单独规划** | 便于 NAT、安全策略、BGP 通告 |

</div>

---

## Foundation Topics · 基础内容

### IP Routing and Forwarding Concepts Review · IP 路由和转发概念回顾

The main goal of a routing protocol is to act as the delivery mechanism that routes packets to their destination. The end-to-end routing process is based on the concept of a **distributed database**: every Layer 3 node maintains its own copy of the database and, through protocol interaction, converges to a consistent (or consistent enough) state.

<div class="zh" markdown="1">

路由协议的主要目标是作为交付机制，将数据包路由到目的地。端到端路由过程基于**分布式数据库**的概念：每台三层节点各自维护一份数据库，通过协议交互使其收敛到一致（或足够一致）的状态。

</div>

| Concept | Definition | Design implication |
|------|------|---------|
| **RIB (Routing Information Base)** | The IP address database maintained on each Layer 3 node, containing destination IPs and next-hop IPs | The "candidate pool" of all protocols; **path selection means picking one entry from the results of multiple protocols** |
| **FIB (Forwarding Information Base)** | The forwarding table, containing destination addresses and the interfaces needed to reach them | The table actually used for forwarding; **a RIB change does not always change the FIB immediately** (recursion/multipath) |

<div class="zh" markdown="1">

| 概念 | 定义 | 设计含义 |
|------|------|---------|
| **RIB（路由信息库）** | 每个三层节点上维护的 IP 地址数据库，包含目的 IP 和下一跳 IP | 所有协议的"候选池"；**选路就是从多个协议的结果里挑一个装表** |
| **FIB（转发信息库）** | 转发表，包含目的地址和到达该目的所需的接口 | 实际转发用的表；**RIB 变了 FIB 不一定马上变**（递归/多路径） |

</div>

#### From RIB to FIB: Four Mechanisms You Must Understand · 从 RIB 到 FIB：必须理解的四个机制

![RIB to FIB: longest match, administrative distance, metric and recursion](assets/fig/en08-03-rib-to-fib.svg)

| Mechanism | Meaning | Design impact |
|------|------|---------|
| **Longest match** | When several entries match, the one with the longest mask wins | A summary route always yields to a more specific route; the default route always comes last |
| **Administrative distance (AD)** | For the same prefix from different sources, the smaller AD wins | Determines the priority order of "static vs OSPF vs BGP" |
| **Metric** | Compares path quality **within the same protocol** | **Metrics are not comparable across protocols** (the fundamental problem of redistribution) |
| **Recursive lookup** | The next hop is "another next hop", resolved layer by layer down to a connected network | A BGP next hop must be resolvable through the IGP or a connected route before it is installed (case 2) |

<div class="zh" markdown="1">

| 机制 | 含义 | 设计影响 |
|------|------|---------|
| **最长匹配** | 有多条匹配时选掩码最长的 | 汇总路由永远让位于明细路由；默认路由永远最后 |
| **管理距离 (AD)** | 不同来源的同一前缀，AD 小的胜 | 决定"静态 vs OSPF vs BGP"的优先级顺序 |
| **度量（metric）** | **同一协议内**比较路径优劣 | **跨协议度量不可比**（重分发的根本难题） |
| **递归查找** | 下一跳是"另一个下一跳"，逐层解析到直连 | BGP 下一跳必须能递归到 IGP/直连才装表（案例二） |

</div>

**Default administrative distance quick reference (Cisco)**:

<div class="zh" markdown="1">

**默认管理距离速查（Cisco）**：

</div>

| Source | AD | Notes |
|------|-----|------|
| Connected | 0 | Highest |
| Static (to an interface) | 1 | |
| eBGP | 20 | **Better than most IGPs** (important!) |
| EIGRP (internal) | 90 | |
| OSPF | 110 | |
| IS-IS | 115 | |
| RIP | 120 | |
| EIGRP (external/redistributed) | 170 | |
| iBGP | 200 | **Worst** (worse than RIP) |
| Unknown | 255 | Not installed |

<div class="zh" markdown="1">

| 来源 | AD | 说明 |
|------|-----|------|
| 直连 | 0 | 最高 |
| 静态（指向接口） | 1 | |
| eBGP | 20 | 比多数 IGP **更优**（重要！） |
| EIGRP（内部） | 90 | |
| OSPF | 110 | |
| IS-IS | 115 | |
| RIP | 120 | |
| EIGRP（外部/重分发） | 170 | |
| iBGP | 200 | **最劣**（比 RIP 还差） |
| 未知 | 255 | 不装表 |

</div>

> ⚠️ **Two traps in the AD table**:
> 1. **eBGP (20) beats OSPF (110)**: a route learned from eBGP **overrides** the same prefix learned from OSPF. If a BGP neighbor accidentally advertises one of your internal prefixes, the internal route is overwritten. **This is why eBGP must always have prefix filtering** (not only to protect against others, but also against yourself).
> 2. **iBGP (200) is the worst**: routes learned from iBGP have the lowest priority. If the same prefix is also learned from an IGP, the IGP wins. When you design "BGP carries the core", watch out — **do not let the IGP and BGP advertise the same prefixes**, otherwise what is actually in effect may be the IGP.

<div class="zh" markdown="1">

> ⚠️ **AD 表的两个陷阱**：
> 1. **eBGP（20）优于 OSPF（110）**：从 eBGP 学到的路由会**压掉** OSPF 学到的同前缀。如果 BGP 邻居不小心通告了你的内部前缀，内部路由会被覆盖。**这就是 eBGP 必须做前缀过滤的原因**（不只防别人，也防自己）。
> 2. **iBGP（200）最劣**：iBGP 学到的路由优先级最低。如果同时从 IGP 学到同前缀，IGP 会赢。设计"BGP 承载核心"时要注意——**不要让 IGP 和 BGP 通告同一批前缀**，否则实际生效的可能是 IGP。

</div>

#### Classification of Routing Protocols · 路由协议的分类

![Three routing protocol families and what each one distributes](assets/fig/en08-04-protocol-classification.svg)

| Category | Protocols | Mechanism | Source of scalability |
|------|------|------|------------|
| **Link state** | OSPF, IS-IS | Flood the topology → each node runs SPF | Hierarchy (areas/levels + summarization) |
| **Path vector** | BGP | Propagates only paths (AS_PATH), not topology | Policy control + trust only your neighbors |
| **Distance vector** (hybrid) | RIP, EIGRP | Propagates "my distance to X" | Summarization + controlling the query scope |

<div class="zh" markdown="1">

| 类别 | 协议 | 机制 | 可扩展性来源 |
|------|------|------|------------|
| **链路状态** | OSPF、IS-IS | 泛洪拓扑 → 各自算 SPF | 分层（区域/层级 + 汇总） |
| **路径矢量** | BGP | 只传路径（AS_PATH），不传拓扑 | 策略控制 + 只信邻居 |
| **距离矢量**（混合） | RIP、EIGRP | 传"我到 X 的距离" | 汇总 + Query 范围控制 |

</div>

> 💡 **One sentence to tell them apart**: in a link-state protocol, **every router knows the whole topology** and computes paths itself; in a distance-vector protocol, **every router only knows the distance its neighbor told it**, without asking why. Link state therefore has stronger fault localization (it can see the topology), while distance vector has simpler convergence logic (DUAL guarantees loop freedom).

<div class="zh" markdown="1">

> 💡 **一句话区分**：链路状态协议里，**每台路由器都知道全网拓扑**，自己算路；距离矢量协议里，**每台路由器只知道邻居告诉它的距离**，不问为什么。所以链路状态的故障定位能力强（能看到拓扑），距离矢量的收敛逻辑简单（DUAL 保证无环）。

</div>

---

## Link-State Routing · 链路状态路由

Link-state routing protocols use the Dijkstra shortest path first (SPF) algorithm to compute the best path. OSPF and IS-IS are the typical link-state protocols.

<div class="zh" markdown="1">

链路状态路由协议使用 Dijkstra 最短路径优先 (SPF) 算法计算最佳路径。OSPF 和 IS-IS 是典型的链路状态协议。

</div>

### The Link-State Database (LSDB) Build Process · 链路状态数据库 (LSDB) 构建过程

![Building the link-state database in five steps, and the three corollaries](assets/fig/en08-05-lsdb-build.svg)

| Step | Action | Key point |
|------|------|--------|
| 1 | Routers discover neighbors and form adjacencies | Parameters must match (Hello/Dead, area, authentication, MTU) |
| 2 | Exchange link-state advertisements (LSA / LSP) | Each router describes "who I am connected to, at what cost" |
| 3 | Each LSA contains router links, interfaces, link state, and cost information | **Cost is distributed**, so the meaning of the metric must be identical network-wide |
| 4 | Build the LSDB | The LSDB of all routers in an area must be **exactly identical** |
| 5 | Run the Dijkstra algorithm to compute the shortest path tree (SPT) | Root the tree at yourself and compute the shortest path to every node/prefix |

<div class="zh" markdown="1">

| 步骤 | 动作 | 关键点 |
|------|------|--------|
| 1 | 路由器发现邻居并建立邻接关系 | 参数必须匹配（Hello/Dead、区域、认证、MTU） |
| 2 | 交换链路状态通告 (LSA / LSP) | 每台路由器描述"我连着谁、开销多少" |
| 3 | 每个 LSA 包含路由器链路、接口、链路状态和成本信息 | **成本是分发出去的**，度量语义必须全网一致 |
| 4 | 构建 LSDB | 区域内所有路由器的 LSDB 必须**完全一致** |
| 5 | 运行 Dijkstra 算法计算最短路径树 (SPT) | 以自己为根，算出到每个节点/前缀的最短路径 |

</div>

**Three design corollaries**:

<div class="zh" markdown="1">

**三个设计推论**：

</div>

| Corollary | Reason |
|------|------|
| **LSDB consistency is a hard requirement** | Inconsistency means routers see different topologies → paths may loop |
| **The flooding domain size drives convergence and memory** | Every topology change is flooded across the whole area and every router recomputes |
| **Cost/metric is the primary design knob** | In a link-state protocol the only levers you have over paths are: metric, areas, summarization |

<div class="zh" markdown="1">

| 推论 | 原因 |
|------|------|
| **LSDB 一致性是刚性要求** | 不一致意味着各路由器看到的拓扑不同 → 路径可能回环 |
| **泛洪域规模决定收敛和内存** | 每次拓扑变化要泛洪到整个区域，所有路由器重算 |
| **成本（cost/metric）是核心设计旋钮** | 链路状态协议里你能控制路径的手段只有：度量、区域、汇总 |

</div>

### Link-State Design in Hub-and-Spoke Topologies · Hub-and-Spoke 拓扑中的链路状态设计

![Summarization in a hub-and-spoke link-state network makes a branch transit](assets/fig/en08-06-hub-spoke-loop.svg)

Hub-and-spoke (star) topologies are extremely common in retail and branch networks. Using a link-state protocol in them raises three structural problems:

<div class="zh" markdown="1">

Hub-and-Spoke（星型）在零售、分支网络中极为常见。用链路状态协议时会遇到三个结构性问题：

</div>

| Problem | Mechanism | Solution |
|------|------|---------|
| **Scalability** | Every spoke receives the link-state information of all other spokes (LSA/LSP flooding across the area) | Use a **multi-area/multi-flooding-domain** design; put spokes in their own areas |
| **Suboptimal routing** | After summarization, traffic may transit through a remote site | ABRs need an **unsummarized link** between them to exchange specific routing information |
| **Transit traffic** | A spoke may be used as a spoke-to-spoke transit (SPF only looks at cost) | Configure the spoke routers as a **stub area** |

<div class="zh" markdown="1">

| 问题 | 机制 | 解决方案 |
|------|------|---------|
| **可扩展性** | 每个 Spoke 接收所有其他 Spoke 的链路状态信息（LSA/LSP 泛洪到全区域） | 使用**多区域/多泛洪域**设计；Spoke 划入独立区域 |
| **次优路由** | 汇总后，流量可能使用远程站点作为中转路径 | ABR 之间需要**非汇总链路**交换特定路由信息 |
| **中转流量** | Spoke 可能被用作 Spoke-to-Spoke 的中转（SPF 只看 cost） | 在 Spoke 路由器上设置 **stub 区域** |

</div>

> ⚠️ **Key design point**: in a multi-area design, ABRs need an unsummarized link between them to exchange specific routing information, so that a spoke site is never used as a transit path.

<div class="zh" markdown="1">

> ⚠️ **关键设计要点**：在多区域设计中，ABR 之间需要一条非汇总链路来交换特定路由信息，避免使用 Spoke 站点作为中转路径。

</div>

**Why "summarization" leads to "using a branch as transit"** — this mechanism is worth expanding, because it explains that awkward sentence in the book:

<div class="zh" markdown="1">

**为什么"汇总"会导致"用分支做中转"**——这段机制值得展开，因为它解释了书里那句拗口的话：

</div>

```
【No summarization】
  Spoke-A ── Hub-1 ═══ Hub-2 ── Spoke-B
  Hub-1 → Spoke-B: via Hub-2, cost = 20 → only path, normal

【Hub-1 summarizes spoke routes and advertises them into the Spoke-A area】
  Spoke-A receives "spoke networks/16 via Hub-1"
  To reach Spoke-B: go to Hub-1 → Hub-1 forwards on → ✅ correct

【But if a backup link exists between Spoke-A and Spoke-B (backup circuit/Internet)】
  Spoke-A only has the summary → everything goes to Hub-1
  Hub-1 may compute "via Spoke-A is closer to Spoke-B" (that backup link exists in the topology)
  → Hub-1 sends traffic back to Spoke-A → Spoke-A only has the summary → sends it back to Hub-1 → loop

【Fix】
  Option 1: make the spoke stub/totally stub (only a default route, no detailed path selection)
  Option 2: ensure the unsummarized links between ABRs provide the correct detail
  Option 3: filter out summaries that should not be received by using a distribute-list on the spoke
```

<div class="zh" markdown="1">

```
【无汇总】
  Spoke-A ── Hub-1 ═══ Hub-2 ── Spoke-B
  Hub-1 到 Spoke-B：经 Hub-2，cost = 20 → 只有这一条路，正常

【Hub-1 把 Spoke 路由汇总后通告给 Spoke-A 区域】
  Spoke-A 收到 "Spoke 网段/16 via Hub-1"
  访问 Spoke-B 时：走 Hub-1 → Hub-1 再转发 → ✅ 正确

【但若 Spoke-A 与 Spoke-B 之间存在备用链路（备份专线/Internet）】
  Spoke-A 只有汇总路由 → 全部送 Hub-1
  而 Hub-1 算路时可能认为"经 Spoke-A 到 Spoke-B 更近"（拓扑里存在那条备份链路）
  → Hub-1 把流量送回 Spoke-A → Spoke-A 只有汇总路由 → 又送回 Hub-1 → 回环

【修复】
  方案一：Spoke 用 stub/Totally Stub（只有默认路由，不参与详细选路）
  方案二：保证 ABR 之间的非汇总链路提供正确的明细
  方案三：在 Spoke 上用分发列表过滤掉不该收到的汇总
```

</div>

> 💡 **A practical rule of thumb**: **when Hub-and-Spoke uses a link-state protocol, "the spoke must be a pure leaf"** — it should have exactly one egress route (default or summary) and make no transit decisions at all. Any design that lets a spoke "choose a path" introduces suboptimal routing or loops.

<div class="zh" markdown="1">

> 💡 **实践口诀**：**Hub-and-Spoke 用链路状态协议时，"Spoke 必须是纯终端"** —— 它只应有一条出口路由（默认或汇总），不做任何中转决策。任何让 Spoke 参与"选择路径"的设计都会引入次优或回环。

</div>

### The Size of the Flooding Domain: An Underestimated Quantitative Constraint · 泛洪域的规模：一个被低估的量化约束

![Flooding domain size against the cost of one topology change](assets/fig/en08-07-flooding-domain.svg)

The scalability of a link-state protocol is fundamentally determined by **the number of routers inside the flooding domain**:

<div class="zh" markdown="1">

链路状态协议的可扩展性，本质上是**泛洪域内的路由器数量**决定的：

</div>

| Flooding domain size | Cost per topology change | Design recommendation |
|-----------|-----------------|---------|
| < 50 routers | Very small, negligible | A single area is perfectly viable |
| 50–200 routers | Noticeable (CPU peaks, LSA flooding bandwidth) | Start partitioning; give the core its own area |
| 200–500 routers | Large (long SPF runs, slow convergence) | Partitioning + summarization + strict control over LSA generation are mandatory |
| > 500 routers | Likely to hit SPF time and memory limits | Move to IS-IS (better TLV extensibility) or let BGP carry the core |

<div class="zh" markdown="1">

| 泛洪域规模 | 每次拓扑变化的开销 | 设计建议 |
|-----------|-----------------|---------|
| < 50 台 | 很小，可忽略 | 单区域也完全可行 |
| 50–200 台 | 明显（CPU 峰值、LSA 泛洪带宽） | 开始分区；核心单独成区 |
| 200–500 台 | 大（SPF 时间长、收敛慢） | 必须分区 + 汇总 + 严格控制 LSA 产生 |
| > 500 台 | 很可能撞上 SPF 时间与内存瓶颈 | 改用 IS-IS（TLV 扩展性更好）或 BGP 承载核心 |

</div>

**How often LSAs are generated matters more than how many there are**: in an area with 100 routers, if every interface is flapping, LSA flooding will continuously saturate the bandwidth. Therefore:

<div class="zh" markdown="1">

**LSA 产生的频率比数量更重要**：一个 100 台路由器的区域，如果每台接口都在抖动，LSA 泛洪会持续吃满带宽。所以：

</div>

| Suppression tool | Effect |
|---------|------|
| **SPF throttling** | Limits the SPF recomputation rate (initial wait + incremental interval + maximum interval) |
| **LSA throttling and arrival suppression** | Limits the LSA generation rate and discards duplicate arrivals |
| **Sensible Hello/Dead values** | Too short a Hello means an optic flap drops the neighbor |
| **BFD + interface suppression (carrier-delay)** | Fast detection without reporting short flaps |
| **Keep access-side interfaces out of the core area** | A user port flapping should not affect core SPF |

<div class="zh" markdown="1">

| 抑制手段 | 作用 |
|---------|------|
| **SPF 节流（throttle）** | 限制 SPF 重算频率（初始等待 + 递增间隔 + 最大间隔） |
| **LSA 节流与到达抑制** | 限制 LSA 生成频率、丢弃重复到达 |
| **合理设置 Hello/Dead** | Hello 太短 → 光模块抖动就断邻居 |
| **BFD + 接口抑制（carrier-delay）** | 快检测但不上报短暂抖动 |
| **不把接入侧接口放进核心区域** | 用户端口抖动不应影响核心 SPF |

</div>

```cfg
! OSPF throttling and stability production baseline
router ospf 1
 router-id 10.255.0.1
 timers throttle spf 50 200 5000      ! first 50ms, increments 200ms, max 5s
 timers throttle lsa 50 200 5000
 timers lsa arrival 100               ! drop duplicate arrivals of the same LSA within 100ms
 auto-cost reference-bandwidth 100000 ! 100G reference bandwidth (see below)
 log-adjacency-changes detail
!
! Access-side interfaces: suppress short flaps
interface GigabitEthernet1/0/1
 carrier-delay msec 2000
 ip ospf cost 100
```

<div class="zh" markdown="1">

```cfg
! OSPF 节流与稳定性生产基线
router ospf 1
 router-id 10.255.0.1
 timers throttle spf 50 200 5000      ! 初次50ms，递增200ms，上限5s
 timers throttle lsa 50 200 5000
 timers lsa arrival 100               ! 同一LSA 100ms 内重复到达则丢弃
 auto-cost reference-bandwidth 100000 ! 100G 参考带宽（见后文）
 log-adjacency-changes detail
!
! 接入侧接口：抑制短暂抖动
interface GigabitEthernet1/0/1
 carrier-delay msec 2000
 ip ospf cost 100
```

</div>

---

## OSPF Design Considerations · OSPF 设计考量

### OSPF LSA Types · OSPF LSA 类型

![OSPF LSA types by generator, scope and design consequence](assets/fig/en08-08-lsa-types.svg)

| LSA type | Name | Generator | Scope | Design implication |
|---------|------|--------|---------|---------|
| Type 1 | Router LSA | Every router | Within the area | Describes "who I am connected to, at what cost"; **an interface flap generates a new LSA** |
| Type 2 | Network LSA | DR | Within the area | Describes the set of routers on a broadcast segment |
| Type 3 | Summary LSA | ABR | Inter-area (except totally stub) | **The "route" between areas**; summarization happens at this layer |
| Type 4 | Summary ASBR LSA | ABR | Inter-area | Tells other areas "where the ASBR is", used to recurse Type 5 |
| Type 5 | AS External LSA | ASBR | Whole AS (except stub areas) | External routes; **this is what redistribution produces** |
| Type 7 | NSSA External LSA | ASBR (inside NSSA) | Inside the NSSA (converted to Type 5 by the ABR) | Lets a stub-like area import external routes |
| Type 9–11 | Opaque LSA | — | Depends on type | Carries extensions (MPLS-TE, GR, Segment Routing) |

<div class="zh" markdown="1">

| LSA 类型 | 名称 | 生成者 | 传播范围 | 设计含义 |
|---------|------|--------|---------|---------|
| Type 1 | Router LSA | 每台路由器 | 区域内 | 描述"我连着谁、cost 多少"；**接口抖动会产生新 LSA** |
| Type 2 | Network LSA | DR | 区域内 | 描述广播网段上的路由器集合 |
| Type 3 | Summary LSA | ABR | 跨区域（除完全末节外） | **区域间的"路由"**；汇总就在这一层做 |
| Type 4 | Summary ASBR LSA | ABR | 跨区域 | 告诉其他区域"ASBR 在哪"，用于递归 Type 5 |
| Type 5 | AS External LSA | ASBR | 整个 AS（stub 区除外） | 外部路由；**重分发产生的就是这个** |
| Type 7 | NSSA External LSA | ASBR（NSSA 内） | NSSA 内（ABR 转成 Type 5） | 让末节区域也能引入外部路由 |
| Type 9–11 | Opaque LSA | — | 按类型 | 承载扩展能力（MPLS-TE、GR、Segment Routing） |

</div>

**Why Type 4 exists** (many people do not know): a Type 5 LSA only contains the ASBR's Router ID, so routers in other areas need to know the ASBR's **reachable address** in order to compute "how to get to the ASBR". Type 4 is the "location sheet" the ABR writes on behalf of the ASBR. **Stub areas do not need Type 4/5, because external routes are not allowed there.**

<div class="zh" markdown="1">

**Type 4 为什么存在**（很多人不知道）：Type 5 里只写了 ASBR 的 Router ID，其他区域的路由器要算"到 ASBR 怎么走"，就需要知道 ASBR 的**可达地址**。Type 4 就是 ABR 替 ASBR 做的"位置说明书"。**stub 区域不需要 Type 4/5，因为那里不允许外部路由。**

</div>

### OSPF Area Types · OSPF 区域类型

![OSPF area types and the decision path for choosing one](assets/fig/en08-09-area-types.svg)

| Area type | Characteristics | Allowed LSAs | Where it is used |
|---------|------|-----------|--------|
| **Backbone (Area 0)** | The core area; all other areas must connect to it | All types | Carries inter-area traffic, **must be contiguous** |
| **Normal Area** | Standard area | All types | Ordinary office/data center areas |
| **Stub Area** | Does not accept external routes (Type 5), replaced by a default route | Type 1, 2, 3 | Branch/edge sites (no need for external detail) |
| **Totally Stub** | Accepts neither external nor inter-area routes, uses only a default route | Type 1, 2 | **Spoke sites** (the most common optimization) |
| **NSSA** | Does not accept Type 5 but allows Type 7 (locally defined external routes) | Type 1, 2, 3, 7 | Edge sites that **do** need to import local routes |
| **Totally NSSA** | NSSA + no Type 3 | Type 1, 2, 7 | Edge sites plus a minimal routing table |

<div class="zh" markdown="1">

| 区域类型 | 特点 | 允许的 LSA | 用在哪 |
|---------|------|-----------|--------|
| **Backbone (Area 0)** | 核心区域，所有其他区域必须连接 | 所有类型 | 承载区域间流量，**必须连续** |
| **Normal Area** | 标准区域 | 所有类型 | 一般办公/数据中心区域 |
| **Stub Area** | 不接收外部路由（Type 5），用默认路由替代 | Type 1, 2, 3 | 分支/边缘站点（不需要外部明细） |
| **Totally Stub** | 不接收外部和跨区域路由，只用默认路由 | Type 1, 2 | **Spoke 站点**（最常用优化） |
| **NSSA** | 不接收 Type 5，但允许 Type 7（自定义外部路由） | Type 1, 2, 3, 7 | 边缘站点**需要**引入本地路由 |
| **Totally NSSA** | NSSA + 不接收 Type 3 | Type 1, 2, 7 | 边缘站点 + 最小化路由表 |

</div>

**The practical logic for choosing an area type**:

<div class="zh" markdown="1">

**区域类型的实际选择逻辑**：

</div>

```
Does this site need to know the details of external routes?
  ├─ No, everything goes out through headquarters → Stub or Totally Stub
  └─ Yes (local Internet egress / local external routes) → NSSA or Totally NSSA
                 ↓
           Does it need the details of other areas?
             ├─ No  → choose the Totally variant (smallest routing table)
             └─ Yes → plain Stub / NSSA
```

<div class="zh" markdown="1">

```
这个站点需要知道外部路由的明细吗？
  ├─ 不需要，统一走总部出去 → Stub 或 Totally Stub
  └─ 需要（有本地 Internet 出口 / 本地外部路由） → NSSA 或 Totally NSSA
                 ↓
           需要知道其他区域的明细吗？
             ├─ 不需要 → 选 Totally 版本（路由表最小）
             └─ 需要   → 普通 Stub / NSSA
```

</div>

> ⚠️ **Three hard constraints on stub areas** (get them wrong and the adjacency will not come up):
> 1. **It cannot be Area 0** (the backbone area must carry all information)
> 2. **There can be no ASBR inside the area** (redistribution is not allowed — otherwise Type 5 would be needed)
> 3. **All routers in the area must be configured as stub** (a mismatch means no adjacency)
>
> If the site has a local Internet egress that requires redistribution, **you can only use NSSA**, not Stub.
> 🔥 **Case: a branch was configured as Stub, and the branch's local Internet egress stopped working entirely**
>
> **Background**: a retail enterprise with 800 stores, one router per store, running OSPF with headquarters. An optimization project configured `area 10 stub` on every store, which cut the branch routing table from 3,000 entries to 20 and clearly improved convergence.
>
> **Failure**: after the 30 "flagship stores" (which have a local Internet backup link plus a local firewall) went live, **the backup egress did not work at all**. When the primary link failed, the store simply went dark instead of switching to its local Internet.
>
> **Root cause**: the flagship store's local Internet egress requires redistributing a static default route on the store router (`redistribute static subnets`), but **a stub area does not allow an ASBR**:
> - After stub was configured, `redistribute static` was **silently ignored** (some platforms only print a warning)
> - The backup path's default route never entered OSPF
> - Primary link fails → the store only has the headquarters default route learned through OSPF → headquarters unreachable → **the whole store goes dark**
>
> **Why testing missed it**: acceptance testing only checked "does it work while the primary link is up" and "did the routing table get smaller". **Nobody tested "does it switch to the backup when the primary link fails"**.
>
> **Fix**:
> ```cfg
> ! Store (flagship): change to Totally NSSA to allow redistributing the local default route
> router ospf 1
>  area 10 nssa no-summary          ! Totally NSSA
>  redistribute static subnets route-map LOCAL-EXIT
> !
> route-map LOCAL-EXIT permit 10
>  match ip address prefix-list PL-DEFAULT
> ```
> Non-flagship stores keep Totally Stub (no ASBR needed).
>
> **Three lessons**:
> 1. **The area type must match the number of exits at the site**: a single exit → Stub; multiple exits (including local Internet) → NSSA.
> 2. **Silently ignored configuration is the most dangerous kind**: `redistribute` does not take effect in a stub area and produces almost no warning. Acceptance must check the **actual routing table**, not merely that the configuration line exists.
> 3. **A "backup path" must be accepted separately**: testing only the primary path means the backup was never tested. **Every redundancy design needs a corresponding fault-injection test case.**

<div class="zh" markdown="1">

> ⚠️ **Stub 区域的三个硬约束**（配错就起不来）：
> 1. **不能是 Area 0**（骨干区域必须承载全部信息）
> 2. **区域内不能有 ASBR**（不能重分发——否则需要 Type 5）
> 3. **区域内所有路由器必须都配成 stub**（不匹配就不建邻居）
>
> 如果站点有本地 Internet 出口需要重分发，就**只能用 NSSA**，不能用 Stub。
> 🔥 **案例：给分支配了 Stub，分支的本地 Internet 出口直接失效**
>
> **背景**：某零售企业 800 家门店，每家门店一台路由器，与总部跑 OSPF。优化项目给全部门店配 `area 10 stub`，分支路由表从 3,000 条降到 20 条，收敛明显改善。
>
> **故障**：30 家"旗舰店"（有本地 Internet 备份链路 + 本地防火墙）上线后，**备份出口完全没起作用**。主链路断时门店直接失联，而不是切到本地 Internet。
>
> **根因**：旗舰店的本地 Internet 出口需要在门店路由器上重分发静态默认路由（`redistribute static subnets`），但 **Stub 区域不允许 ASBR**：
> - 配了 stub 后，`redistribute static` 被**静默忽略**（有的平台只给一条 warning）
> - 备份路径的默认路由从未进入 OSPF
> - 主链路断 → 门店只剩 OSPF 学到的总部默认路由 → 总部不可达 → **全网失联**
>
> **为什么测试没发现**：验收只测了"主链路正常时能不能通"和"路由表是否变小"。**没有测"主链路断开时是否会切到备份"**。
>
> **修复**：
> ```cfg
> ! 门店（旗舰店）：改为 Totally NSSA，允许重分发本地默认路由
> router ospf 1
>  area 10 nssa no-summary          ! Totally NSSA
>  redistribute static subnets route-map LOCAL-EXIT
> !
> route-map LOCAL-EXIT permit 10
>  match ip address prefix-list PL-DEFAULT
> ```
> 非旗舰店保持 Totally Stub（不需要 ASBR）。
>
> **教训（三条）**：
> 1. **区域类型要和站点的"出口数量"匹配**：单出口 → Stub；多出口（含本地 Internet）→ NSSA。
> 2. **配置被静默忽略是最危险的**：`redistribute` 在 stub 区域不生效且几乎无告警。验收必须查**实际路由表**，不能只看配置命令在不在。
> 3. **"备份路径"必须单独验收**：只测主路径等于没测备份。**每一个冗余设计，都要有对应的故障注入用例。**

</div>

### OSPF Network Types · OSPF 网络类型

![OSPF network types and the three scenarios where the default is wrong](assets/fig/en08-10-network-types.svg)

| Network type | DR/BDR election | Hello/Dead | Suitable for |
|---------|------------|-----------|---------|
| **Broadcast** | Yes | 10 / 40 s | Ethernet (default) |
| **Point-to-Point** | No | 10 / 40 s | Serial links, point-to-point Ethernet, **GRE tunnels** |
| **Point-to-Multipoint** | No | 30 / 120 s | NBMA, **the hub side of a hub-and-spoke** |
| **Nonbroadcast (NBMA)** | Yes | 30 / 120 s | Requires manual neighbor configuration (Frame Relay, obsolete) |
| **P2MP Nonbroadcast** | No | 30 / 120 s | Hub-and-spoke designs that do not support multicast |

<div class="zh" markdown="1">

| 网络类型 | DR/BDR 选举 | Hello/Dead | 适用场景 |
|---------|------------|-----------|---------|
| **Broadcast** | 是 | 10 / 40 秒 | 以太网（默认） |
| **Point-to-Point** | 否 | 10 / 40 秒 | 串行链路、点对点以太网、**GRE 隧道** |
| **Point-to-Multipoint** | 否 | 30 / 120 秒 | NBMA、**Hub-and-Spoke 的 Hub 侧** |
| **Nonbroadcast (NBMA)** | 是 | 30 / 120 秒 | 需手动配邻居（帧中继，已淘汰） |
| **P2MP Nonbroadcast** | 否 | 30 / 120 秒 | 不支持组播的 Hub-and-Spoke |

</div>

**The network type is a design variable, not an "auto-detected result"**:

<div class="zh" markdown="1">

**网络类型是设计变量，不是"自动检测结果"**：

</div>

| Scenario | Problem with the default type | Correct configuration |
|------|--------------|---------|
| **Hub-and-Spoke (the hub is a mGRE multipoint tunnel)** | Under Broadcast all spokes are in the same subnet, so **one spoke is elected DR** → spoke-to-spoke traffic detours | Configure `ip ospf network point-to-multipoint` on the hub |
| Two routers directly connected over Ethernet | Broadcast still elects a DR (meaningless, plus one extra LSA) | Configure `point-to-point` → faster convergence, one LSA less |
| An SVI for servers/terminals | A DR is needed (multiple devices) | Keep Broadcast |

<div class="zh" markdown="1">

| 场景 | 默认类型的问题 | 正确配置 |
|------|--------------|---------|
| **Hub-and-Spoke（Hub 是 mGRE 多点隧道）** | Broadcast 下所有 Spoke 在同一网段，会**选出一个 Spoke 做 DR** → Spoke 间流量绕行 | Hub 侧配 `ip ospf network point-to-multipoint` |
| 两台路由器直连的以太网 | Broadcast 下仍要选 DR（无实际意义，多一个 LSA） | 配 `point-to-point` → 收敛更快、少一个 LSA |
| 服务器/终端接入的 SVI | 需要 DR（有多台设备） | 保持 Broadcast |

</div>

```cfg
! Layer 3 interconnection port: point-to-point, one Type 2 LSA less, faster convergence
interface TenGigabitEthernet1/1/1
 no switchport
 ip address 10.1.1.1 255.255.255.254
 ip ospf network point-to-point
 ip ospf hello-interval 3
 ip ospf dead-interval 9
 ip ospf bfd

! Hub side (mGRE / DMVPN): P2MP, avoid electing a spoke as DR
interface Tunnel0
 ip ospf network point-to-multipoint
 ip ospf hello-interval 10
 ip ospf dead-interval 40
```

<div class="zh" markdown="1">

```cfg
! 三层互联口：点对点，少一个 Type 2 LSA，收敛更快
interface TenGigabitEthernet1/1/1
 no switchport
 ip address 10.1.1.1 255.255.255.254
 ip ospf network point-to-point
 ip ospf hello-interval 3
 ip ospf dead-interval 9
 ip ospf bfd

! Hub 侧（mGRE / DMVPN）：P2MP，避免选出 Spoke 做 DR
interface Tunnel0
 ip ospf network point-to-multipoint
 ip ospf hello-interval 10
 ip ospf dead-interval 40
```

</div>

> 💡 **The hidden benefit of `point-to-point`**: it eliminates the Type 2 (Network LSA) and the DR/BDR election. In a network with hundreds of Layer 3 interconnections, that saves hundreds of LSAs and the associated SPF computation. **This is a zero-cost optimization.**

<div class="zh" markdown="1">

> 💡 **`point-to-point` 的隐性收益**：它省掉了 Type 2（Network LSA）和 DR/BDR 选举。在几百条三层互联的网络里，这能省掉几百个 LSA 和相应的 SPF 计算量。**这是"零成本优化"。**

</div>

### OSPF Fast Convergence Techniques · OSPF 快速收敛技术

![Shrinking Hello timers versus BFD, and the four tiers of a convergent response](assets/fig/en08-11-fast-convergence.svg)

| Technique | Description | Design recommendation |
|------|------|---------|
| **SPF delay and throttling** | Controls how often SPF runs, avoiding frequent computation | Mandatory, e.g. `50 200 5000` |
| **Incremental SPF (iSPF)** | Recomputes only the affected part (on some platforms/area types) | Enable where the platform supports it |
| **Partial route calculation (PRC)** | Updates only the routing table without recomputing the SPT (when a prefix change does not affect topology) | Takes effect automatically |
| **LSA delay and arrival suppression** | Controls the LSA generation rate | `timers throttle lsa` + `timers lsa arrival` |
| **BFD** | Provides sub-second neighbor failure detection | **Preferable to shrinking the Hello timer** |
| **Router LSA throttling** | Limits how often Type 1 LSAs are generated | Same as above |
| **FRR / TI-LFA** | Pre-computes a backup path and switches locally on failure | Large-network cores (not covered in this book, but modern practice) |

<div class="zh" markdown="1">

| 技术 | 说明 | 设计建议 |
|------|------|---------|
| **SPF 延迟和抑制（throttle）** | 控制 SPF 计算频率，避免频繁计算 | 必配，如 `50 200 5000` |
| **增量 SPF (iSPF)** | 只重算受影响的部分（部分平台/区域类型） | 平台支持时启用 |
| **部分路由计算 (PRC)** | 只更新路由表，不重算 SPT（前缀变化不影响拓扑时） | 自动生效 |
| **LSA 延迟与到达抑制** | 控制 LSA 生成速率 | `timers throttle lsa` + `timers lsa arrival` |
| **BFD** | 提供亚秒级邻居故障检测 | **优先于调小 Hello** |
| **路由器 LSA 节流** | 限制 Type 1 LSA 生成频率 | 同上 |
| **FRR / TI-LFA** | 预先计算备份路径，故障时本地切换 | 大网核心（书未展开，属现代实践） |

</div>

**"Tune the Hello timer" vs "turn on BFD"**:

<div class="zh" markdown="1">

**"调 Hello" vs "上 BFD"的取舍**：

</div>

| Dimension | Shrink Hello/Dead | Turn on BFD |
|------|---------------|--------|
| Detection speed | Down to 1 s/3 s (below that the risk grows) | 50–300 ms |
| CPU cost | **Every neighbor** processes Hellos at a faster rate | BFD packets are very light, on an independent fast path |
| Risk of false failover | High (flaps, missed Hellos when the CPU is busy) | Low (BFD has its own detection logic) |
| Configuration complexity | Low (one command) | Medium (both ends must support it and be paired) |
| **Conclusion** | Only in very simple environments | **Recommended in production** |

<div class="zh" markdown="1">

| 维度 | 调小 Hello/Dead | 上 BFD |
|------|---------------|--------|
| 检测速度 | 可到 1s/3s（再低风险大） | 50–300ms |
| CPU 开销 | **每个邻居**都要按更快频率处理 Hello | BFD 报文极轻，独立快速通道 |
| 误切换风险 | 高（抖动、CPU 忙时漏 Hello） | 低（BFD 独立检测逻辑） |
| 配置复杂度 | 低（一条命令） | 中（需两端支持并配对） |
| **结论** | 只在极简环境用 | **生产推荐** |

</div>

> ⚠️ **A common bad combination**: Hello set to 1 s and Dead to 3 s **without** any SPF throttling. The result: an optic flap → neighbor down → SPF run → neighbor back → another SPF run → repeat. The CPU is saturated by SPF and everything gets slower. **Fast detection must be paired with flap suppression, otherwise you are just amplifying noise.**

<div class="zh" markdown="1">

> ⚠️ **一个常见错误组合**：把 Hello 调到 1s、Dead 调到 3s，**同时**没配 SPF 节流。结果是：光模块抖动 → 邻居断 → SPF 重算 → 邻居恢复 → SPF 再重算 → 反复。CPU 被 SPF 吃满，反而更慢。**快检测必须配抖动抑制，否则是把噪声放大。**

</div>

### OSPF Metric Design: `auto-cost` Must Be a Network-Wide Decision · OSPF 度量设计：`auto-cost` 必须是全网一致的决策

![OSPF cost formula: default reference bandwidth versus a 100G reference](assets/fig/en08-12-auto-cost.svg)

OSPF's default cost is `reference bandwidth / interface bandwidth`, with the reference bandwidth defaulting to **100 Mbps**. That creates a serious historical problem:

<div class="zh" markdown="1">

OSPF 的默认 cost 计算是 `参考带宽 / 接口带宽`，参考带宽默认 **100 Mbps**。这带来一个历史上的严重问题：

</div>

| Interface bandwidth | Default cost (100M reference) | Consequence |
|---------|---------------------|------|
| 100M | 1 | Baseline |
| 1G | 1 | **Same as 100M!** |
| 10G | 1 | **Still the same!** |
| 100G | 1 | **Still the same!** |

<div class="zh" markdown="1">

| 接口带宽 | 默认 cost（参考 100M） | 后果 |
|---------|---------------------|------|
| 100M | 1 | 基准 |
| 1G | 1 | **与 100M 相同！** |
| 10G | 1 | **仍然相同！** |
| 100G | 1 | **仍然相同！** |

</div>

**This means that under the default configuration, a 100M link and a 100G link have exactly the same cost** (both 1), and SPF treats them as equal-cost paths for load sharing — **this is almost always a serious design error**.

<div class="zh" markdown="1">

**这意味着在默认配置下，一条 100M 链路和一条 100G 链路的 cost 完全一样**（都是 1），SPF 会把它们当作等价的等开销路径做负载分担 —— **这几乎总是一个严重的设计错误**。

</div>

```cfg
! The reference bandwidth must be changed consistently across the entire network (100G recommended, or at least 10G)
router ospf 1
 auto-cost reference-bandwidth 100000     ! in Mbps, 100000 = 100G
!
! After the change the costs become:
! 1G   → 100
! 10G  → 10
! 100G → 1
! 1M   → 100000 (note: low-speed links get a very large cost, which is still acceptable)
```

<div class="zh" markdown="1">

```cfg
! 必须全网统一修改参考带宽（建议 100G 或至少 10G）
router ospf 1
 auto-cost reference-bandwidth 100000     ! 单位 Mbps，100000 = 100G
!
! 修改后 cost 变成：
! 1G   → 100
! 10G  → 10
! 100G → 1
! 1M   → 100000（注意：低速链路 cost 会很大，仍可接受）
```

</div>

> ⚠️ **The reference bandwidth must be identical network-wide**. If half the devices use the default and half use 100G, **the same pair of links gets different costs on each end** — the result is directional suboptimal routing (or even transient loops). This is the classic case of "changing one optimization parameter actually created an asymmetric network". **Changing the reference bandwidth is a network-wide change and must go through the change process.**

<div class="zh" markdown="1">

> ⚠️ **参考带宽必须全网一致**。如果一半设备用默认值、一半用 100G，**同一对链路在两端算出不同 cost** —— 结果是有方向性的次优路径（甚至短暂环路）。这是"看起来改了一个优化参数，实际制造了不对称网络"的典型。**修改参考带宽属于全网变更，要走变更流程。**

</div>

**Manual cost design** (when automatic calculation does not match your intent):

<div class="zh" markdown="1">

**cost 的手工设计**（当自动计算不符合意图时）：

</div>

| Intent | Approach |
|------|------|
| Define clear primary/backup paths | Small cost on the primary, large on the backup (e.g. primary 10 / backup 100) |
| Base cost on business importance instead of bandwidth | Assign manually, e.g. cost 1 on core interconnects and cost 100 on edge links |
| Exclude a link from forwarding | Set the cost very high (65535) — but **do not use this instead of shutdown** |
| Make a link backup-only | Use cost plus routing policy, or simply do not include the interface in OSPF |

<div class="zh" markdown="1">

| 意图 | 做法 |
|------|------|
| 明确主备路径 | 主路径 cost 小，备路径 cost 大（如主 10 / 备 100） |
| 按业务重要性而非带宽 | 手工指定，如核心互联 cost 1，边缘链路 cost 100 |
| 排除某条链路转发 | 把 cost 设到极大（65535）——但**不要用这个代替 shutdown** |
| 让某条链路只做备份 | 用 cost + 路由策略，或直接不把该接口放进 OSPF |

</div>

> 💡 **A practical design habit**: write an explicit **cost table for every link** in the documentation (instead of "auto-cost computes it"). Once someone changes an interface bandwidth or the reference bandwidth, paths change silently, and only a table in the documentation lets you spot the deviation.

<div class="zh" markdown="1">

> 💡 **一个实用的设计习惯**：在文档里显式写出**每条链路的 cost 表格**（而不是"由 auto-cost 自动算"）。因为一旦有人改了接口带宽或参考带宽，路径会静默改变，而文档里有表格才能发现偏离。

</div>

### OSPF Summarization · OSPF 汇总

![Summarization with null0, and the three states it changes](assets/fig/en08-13-summarization.svg)

| Summary type | Where it is configured | Command | Description |
|---------|---------|------|------|
| **Inter-area summary** | ABR | `area X range <prefix> <mask>` | Summarizes the details of an area before advertising them to other areas |
| **External route summary** | ASBR | `summary-address <prefix> <mask>` | Summarizes redistributed external routes |

<div class="zh" markdown="1">

| 汇总类型 | 配置位置 | 命令 | 说明 |
|---------|---------|------|------|
| **区域间汇总** | ABR | `area X range <prefix> <mask>` | 把某区域的明细汇总后通告给其他区域 |
| **外部路由汇总** | ASBR | `summary-address <prefix> <mask>` | 汇总重分发进来的外部路由 |

</div>

```cfg
! Summarize area 10 routes on the ABR
router ospf 1
 area 10 range 10.10.0.0 255.255.0.0
 ! A summary route pointing at Null0 is generated by default (Cisco behavior)
 ! Confirm explicitly: show ip route 10.10.0.0 should show the Null0 entry

! Summarize external routes on the ASBR
router ospf 1
 summary-address 172.16.0.0 255.255.0.0
```

<div class="zh" markdown="1">

```cfg
! ABR 上汇总区域 10 的路由
router ospf 1
 area 10 range 10.10.0.0 255.255.0.0
 ! 默认会生成指向 Null0 的汇总路由（Cisco 行为）
 ! 显式确认：show ip route 10.10.0.0 能看到 Null0 条目

! ASBR 上汇总外部路由
router ospf 1
 summary-address 172.16.0.0 255.255.0.0
```

</div>

**Five "correct practices" for summarization and their costs**:

<div class="zh" markdown="1">

**汇总的五条"正确做法"与对应的代价**：

</div>

| Practice | Benefit | Cost / precondition |
|------|------|------------|
| Summarize only **contiguous** address blocks | The summary route is accurate | Requires an addressing plan; if blocks are not contiguous the summary covers unused addresses → black hole |
| Pair the summary with **null0** | The summary route disappears when every detail disappears | Platform behavior varies, verify explicitly |
| Do not summarize **too coarsely** | Preserves some fault visibility | Over-summarization = complete loss of detail |
| Summarize on the **ABR**, not on an arbitrary router | Correct location, predictable effect | Requires clear area boundaries |
| **Re-validate convergence after summarizing** | Traffic is still sent into the area when a detail fails | Requires an "no leakage of failures" design inside the area (stub + intra-area default route) |

<div class="zh" markdown="1">

| 做法 | 收益 | 代价 / 前提 |
|------|------|------------|
| 只汇总**连续**的地址块 | 汇总路由准确 | 需要地址规划支撑；不连续时汇总会包含未使用的地址 → 黑洞 |
| 汇总后配 **null0** | 明细全消失时汇总路由也消失 | 平台行为差异，需显式确认 |
| 汇总的**粒度不要过粗** | 保留一定的故障可见性 | 过度汇总 = 完全失去明细信息 |
| 在 **ABR** 而非任意路由器上汇总 | 位置正确、生效可预测 | 需要清晰的区域边界 |
| 汇总后**重新检查故障收敛** | 明细故障时流量仍然送往该区域 | 需要在区域内做"故障不外溢"的设计（stub + 区域内默认路由） |

</div>

> ⚠️ **The most insidious consequence of summarization: "normal" during a failure**. After summarizing, when one detailed link fails the core has no idea at all — the summary route is still there, traffic keeps being sent into that area, and then gets dropped inside it. Users report "some subnets are unreachable", while `show ip route` on the core looks perfectly healthy and `ping` to the summary address succeeds. **When troubleshooting, you must look inside the area, not at the core.**

<div class="zh" markdown="1">

> ⚠️ **汇总的最隐蔽后果：故障期间的"正常"**。汇总后，某条明细链路断了，核心完全感知不到——汇总路由还在，流量继续送往那个区域，然后在区域内部被丢弃。用户报"某几个网段不通"，而核心的 `show ip route` 一切正常，`ping 汇总地址` 也通。**排障时必须在区域内部看，不能在核心看。**

</div>

---

## IS-IS Design Considerations · IS-IS 设计考量

IS-IS is another link-state protocol. It is conceptually very similar to OSPF but differs noticeably in **scalability, encapsulation layer, and vendor ecosystem**.

<div class="zh" markdown="1">

IS-IS 是另一个链路状态协议，与 OSPF 在概念上高度相似，但在**扩展性、封装层级、厂商生态**上有明显差异。

</div>

### OSPF vs IS-IS · OSPF 与 IS-IS 的对比

![OSPF and IS-IS compared on the seven dimensions that decide it](assets/fig/en08-14-ospf-vs-isis.svg)

| Dimension | OSPF | IS-IS | Design implication |
|------|------|-------|---------|
| **Encapsulation layer** | Above IP (protocol number 89) | **Runs directly on Layer 2** (CLNS) | IS-IS can form neighbors without IP reachability (**it may survive while IP is under attack**); but it is also harder to run across non-transparent networks |
| **Hierarchy** | Areas (Area 0 must be contiguous) | **Level 1 / Level 2** (the backbone is a contiguous L2) | The IS-IS backbone is formed naturally by L2 routers, **no special "Area 0 must be contiguous" rule** |
| **Area boundaries** | ABRs have interfaces both **inside and between** areas | An L1/L2 router **can have a single interface** (one device belongs to both L1 and L2) | IS-IS boundaries are more flexible |
| **Extensibility** | Fixed LSA types (Type 1–11) | **TLV structure**, easy to extend | IS-IS is the first choice for large SP backbones (it carries TE, SR, and IPv6 without protocol changes) |
| **Metric** | 16 bits by default (24-bit extension) | 6 bits by default (**wide metrics must be enabled**) | IS-IS absolutely requires `metric-style wide` |
| **Multi-topology (MT)** | No native support (IPv6 and IPv4 share a topology) | **Supports multiple topologies** (IPv4/IPv6 can take different paths) | Only IS-IS allows separate IPv4/IPv6 paths |
| **DR concept** | DR/BDR (elected, with a waiting time) | **DIS** (no backup, preemptive, faster convergence) | The IS-IS DIS has no BDR, so failover is faster but re-floods |

<div class="zh" markdown="1">

| 维度 | OSPF | IS-IS | 设计含义 |
|------|------|-------|---------|
| **封装层次** | IP 之上（协议号 89） | **直接跑在二层**（CLNS） | IS-IS 不依赖 IP 可达即可建邻居（**IP 被攻击时 IS-IS 可能仍存活**）；但也更难跨非透传网络 |
| **层级** | 区域（Area 0 必须连续） | **Level 1 / Level 2**（骨干是连续的 L2） | IS-IS 的骨干由 L2 路由器自然形成，**不需要"区域 0 连续"的特殊规则** |
| **区域边界** | ABR 在**区域内+区域间**都有接口 | L1/L2 路由器**可以只有一个接口**（一台设备同时属于 L1 和 L2） | IS-IS 的边界更灵活 |
| **可扩展性** | LSA 类型固定（Type 1–11） | **TLV 结构**，易扩展 | IS-IS 是大型 SP 骨干的首选（能承载 TE、SR、IPv6 而不改协议） |
| **度量** | 默认 16 位（可扩展 24 位） | 默认 6 位（**必须开宽度量**） | IS-IS 一定要配 `metric-style wide` |
| **多拓扑（MT）** | 无原生支持（IPv6 与 IPv4 同拓扑） | **支持多拓扑**（IPv4/IPv6 可走不同路径） | 需要 IPv4/IPv6 分离路径时只能用 IS-IS |
| **DR 概念** | DR/BDR（选举，有等待时间） | **DIS**（没有备份，抢占式，收敛更快） | IS-IS 的 DIS 无 BDR，切换更快但会重新泛洪 |

</div>

### Key IS-IS Design Details · IS-IS 的关键设计细节

![IS-IS specifics: NET, levels, metric styles and four traps](assets/fig/en08-15-isis-details.svg)

| Detail | Description | Common mistake |
|------|------|---------|
| **NET / System ID** | The unique identity of each router (similar to a Router ID) | Duplicated in the network → adjacencies fail or the LSDB goes wrong |
| **Level 1 / Level 2** | L1 inside the area, L2 for the backbone | Configuring every access device as L2 → the backbone flooding domain becomes too large |
| **`metric-style wide`** | Must be enabled to use large metrics and TE | Without it the metric is capped at 63 and 10G cannot be distinguished from 100G |
| **Overload bit** | Marks "I am not forwarding transit traffic for now" | Used for maintenance windows (not attracting traffic before BGP converges) — **many projects never use it** |
| **LSP flooding and refresh** | Similar to OSPF LSAs | The default refresh interval is 15 minutes, watch the bandwidth |
| **Authentication** | L1/L2/PDU each support cleartext/MD5/HMAC-SHA | Only part of it is configured (e.g. only L2, leaving L1 wide open) |

<div class="zh" markdown="1">

| 细节 | 说明 | 常见错误 |
|------|------|---------|
| **NET / System ID** | 每台路由器的唯一标识（类似 Router ID） | 全网重复 → 邻居起不来或 LSDB 异常 |
| **Level 1 / Level 2** | L1 区域内，L2 骨干 | 把接入设备全配成 L2 → 骨干泛洪域过大 |
| **`metric-style wide`** | 必须开启才能用大度量与 TE | 不开则度量上限 63，无法区分 10G/100G |
| **过载位（Overload Bit）** | 标记"我暂时不转发中转流量" | 用于维护窗口（BGP 收敛完成前不吸引流量），**很多项目没利用** |
| **LSP 泛洪与刷新** | 类似 OSPF 的 LSA | 默认刷新周期 15 分钟，需注意带宽 |
| **认证** | L1/L2/PDU 分别支持明文/MD5/HMAC-SHA | 只配了一部分（如只配 L2，L1 裸奔） |

</div>

```cfg
! IS-IS production configuration essentials
router isis CORE
 net 49.0001.0100.2550.0001.00
 metric-style wide                          ! mandatory
 is-type level-2-only                       ! the core is L2 only
 log-adjacency-changes
 authentication mode hmac-sha-256 CORE-KEY  ! at least SHA
!
interface TenGigabitEthernet1/1/1
 ip router isis CORE
 isis metric 10 level-2
 isis hello-interval 3
 isis hello-multiplier 3
 isis bfd
 isis authentication mode hmac-sha-256 L2-KEY level-2
```

<div class="zh" markdown="1">

```cfg
! IS-IS 生产配置要点
router isis CORE
 net 49.0001.0100.2550.0001.00
 metric-style wide                          ! 必须
 is-type level-2-only                       ! 核心只做 L2
 log-adjacency-changes
 authentication mode hmac-sha-256 CORE-KEY  ! 至少 SHA
!
interface TenGigabitEthernet1/1/1
 ip router isis CORE
 isis metric 10 level-2
 isis hello-interval 3
 isis hello-multiplier 3
 isis bfd
 isis authentication mode hmac-sha-256 L2-KEY level-2
```

</div>

> 💡 **The biggest hidden advantage of IS-IS**: it runs on Layer 2 and has **no IP header**. That means:
> - IS-IS adjacencies can come up even when no IP reachability exists yet (**very useful during initial configuration and disaster recovery**)
> - IP-targeted DoS attacks (ICMP floods, IP fragment attacks) **do not affect IS-IS adjacencies**
> - But it also means: **you cannot form IS-IS neighbors directly across a Layer 3 network (such as a carrier IP network)** — you need a tunnel

<div class="zh" markdown="1">

> 💡 **IS-IS 的最大隐性优势**：它跑在二层，**没有 IP 头**。这意味着：
> - 即使设备上还没有任何 IP 可达性，IS-IS 邻居也能建立（**首次配置/灾后重建时非常有用**）
> - 针对 IP 的 DoS 攻击（如 ICMP 洪泛、IP 分片攻击）**不影响 IS-IS 的邻居关系**
> - 但也意味着：**跨三层网络（如跨运营商的 IP 网）无法直接建 IS-IS 邻居**，必须靠隧道

</div>

**Selection guidance**:

<div class="zh" markdown="1">

**选型建议**：

</div>

| Scenario | Choose |
|------|-----|
| Enterprise campus/branches (possibly multivendor) | **OSPF** (broad ecosystem, many engineers, plenty of troubleshooting material) |
| Carrier backbones, very large cores | **IS-IS** (TLV extensibility, multi-topology, no IP dependency) |
| Need separate IPv4/IPv6 paths (e.g. v6 over different links) | **IS-IS multi-topology** |
| The team only knows OSPF | **OSPF** (see counter-intuitive truth #2 in the introduction) |

<div class="zh" markdown="1">

| 场景 | 选 |
|------|-----|
| 企业园区/分支（多厂商可能） | **OSPF**（生态广、工程师多、排障资料多） |
| 运营商骨干、超大规模核心 | **IS-IS**（TLV 扩展性、多拓扑、无 IP 依赖） |
| 需要 IPv4/IPv6 分离路径（如 v6 走不同链路） | **IS-IS 多拓扑** |
| 团队只熟悉 OSPF | **OSPF**（见导读反直觉二） |

</div>

---

## EIGRP Design Considerations · EIGRP 设计考量

EIGRP is Cisco's advanced distance-vector (hybrid) protocol, built around **DUAL (Diffusing Update Algorithm)**. Its fundamental difference from link-state protocols is that **it does not build a topology map; it maintains a "set of feasible paths to each destination" and relies on the feasibility condition to guarantee loop freedom.**

<div class="zh" markdown="1">

EIGRP 是 Cisco 的高级距离矢量（混合型）协议，核心是 **DUAL（扩散更新算法）**。它与链路状态协议的根本差异在于：**它不构建拓扑图，而是维护"到每个目的地的可行路径集合"，靠可行性条件保证无环。**

</div>

### The Four Tables and Three Terms of EIGRP · EIGRP 的四张表与三个术语

![EIGRP three tables and the feasible successor inequality](assets/fig/en08-16-eigrp-tables.svg)

| Table | Contents |
|----|------|
| **Neighbor table** | Who my EIGRP neighbors are, their state, and hold time |
| **Topology table** | **All** learned paths per destination, with metrics, successors, and feasible successors |
| **Routing table** | The best paths selected from the topology table |
| (implicit) **Send/receive buffers** | Internal mechanism |

<div class="zh" markdown="1">

| 表 | 内容 |
|----|------|
| **邻居表** | 谁是我的 EIGRP 邻居、状态、保持时间 |
| **拓扑表** | 每个目的地**所有**学到的路径及其度量、后继、可行后继 |
| **路由表** | 从拓扑表优选出来的最佳路径 |
| （隐含）**发送/接收缓存** | 内部机制 |

</div>

| Term | Meaning | Design significance |
|------|------|---------|
| **Feasible distance (FD)** | The shortest metric to the destination (through the best neighbor) | The entry that appears in the routing table |
| **Reported distance / advertised distance (RD/AD)** | The metric the neighbor claims it has to that destination | Used only for the feasibility test, not directly for path selection |
| **Feasible successor (FS)** | A backup neighbor satisfying the **feasibility condition** (RD < current FD) | **With an FS, repair is local and the network is not disturbed** — this is the root of fast EIGRP convergence |

<div class="zh" markdown="1">

| 术语 | 含义 | 设计意义 |
|------|------|---------|
| **可行距离 (FD)** | 到目的地的最短度量（经最优邻居） | 出现在路由表里的那条 |
| **报告距离 / 通告距离 (RD/AD)** | 邻居声称"我到该目的地的度量" | 只用于可行性判断，不直接用于选路 |
| **可行后继 (FS)** | 满足**可行性条件**（RD < 当前 FD）的备用邻居 | **有 FS 时本地修复，不惊动全网**——这是 EIGRP 收敛快的根源 |

</div>

**The meaning of the feasibility condition** (in one sentence): **the next-hop neighbor of the backup path must be closer to the destination than I am**. If that holds, it is proven that "going through it cannot loop back to me", so the path is loop-free.

<div class="zh" markdown="1">

**可行性条件的含义**（用一句话记住）：**备用路径的下一跳邻居，必须比我自己离目的地更近**。满足这个条件，就证明"走它不会绕回我这里"，因此无环。

</div>

```
        FD = 1000 (via A)
   me ──┤
        └─ metric via B = 2000, B says its RD = 800
             800 < 1000 → feasible → B is a feasible successor (backup path, ready to use)
             if B's RD = 1200 (> my FD of 1000) → not feasible → cannot be used as a backup
```

<div class="zh" markdown="1">

```
        FD = 1000（经 A）
   我 ──┤
        └─ 经 B 的度量 = 2000，B 说它的 RD = 800
             800 < 1000 → 可行 → B 是可行后继（备份路径，随时可用）
             若 B 的 RD = 1200（> 我的 FD 1000）→ 不可行 → 不能做备份
```

</div>

### The Query Domain: The Part of EIGRP That Most Needs Design · Query 域：EIGRP 最需要设计的部分

![How an EIGRP query spreads, and the four ways to bound it](assets/fig/en08-17-eigrp-query.svg)

When a path fails and there is **no feasible successor**, the router enters the **Active** state and sends a **Query** to all neighbors: "do you have a route to X?" If a neighbor does not, it queries its own neighbors — **this is query diffusion**.

<div class="zh" markdown="1">

当一条路径失效且**没有可行后继**时，路由器进入 **Active** 状态，向所有邻居发 **Query**："你有到 X 的路吗？" 邻居如果没有，继续向它们的邻居查 —— **这就是 Query 扩散**。

</div>

| Problem | Consequence |
|------|------|
| Queries spread across the whole network | Every router participates in the computation, CPU spikes, convergence slows down |
| No answer found | It enters **SIA (Stuck In Active)**, neighbors are reset, routes flap |

<div class="zh" markdown="1">

| 问题 | 后果 |
|------|------|
| Query 扩散到整个网络 | 所有路由器参与计算，CPU 飙升，收敛变慢 |
| 找不到答案 | 进入 **SIA（Stuck In Active）**，邻居被重置，路由抖动 |

</div>

**Four ways to control the query scope**:

<div class="zh" markdown="1">

**控制 Query 范围的四个手段**：

</div>

| Tool | Mechanism | Effect |
|------|------|------|
| **Summarization** | Upstream only sees the summary route, so queries about a detail failure are "absorbed" by the summary | **Most effective** — a detail failure never spreads upward |
| **EIGRP stub routing** | Tells neighbors "I am a leaf, do not ask me" | Cuts queries off completely |
| **Distribute lists / route filtering** | Fewer route entries → fewer query trigger points | Complementary |
| **A well-designed topology hierarchy** | Clear hub-spoke, avoid multipath redundancy | An architectural tool |

<div class="zh" markdown="1">

| 手段 | 机制 | 效果 |
|------|------|------|
| **汇总（Summary）** | 上游只看到汇总路由，明细故障的 Query 被汇总路由"吸收" | **最有效**——明细失效不会向上扩散 |
| **Stub 路由（EIGRP Stub）** | 告诉邻居"我是末端，不用问我" | 彻底截断 Query |
| **分发列表 / 路由过滤** | 减少路由条目 → 减少 Query 触发点 | 辅助 |
| **合理设计拓扑层级** | 明确的 Hub-Spoke，避免多路径冗余 | 架构手段 |

</div>

```cfg
! EIGRP named mode production configuration
router eigrp CAMPUS
 !
 address-family ipv4 unicast autonomous-system 100
  !
  network 10.0.0.0 0.255.255.255
  eigrp router-id 10.255.0.1
  !
  ! Key point: truncate the query scope
  stub connected summary redistribute static
  !
  ! Interface-level tuning
  af-interface default
   passive-interface
   bfd
  exit-af-interface
  !
  af-interface TenGigabitEthernet1/1/1
   no passive-interface
   hello-interval 3
   hold-time 9
  exit-af-interface
  !
  ! Summarization (also suppresses details, reducing query triggers)
  topology base
   auto-summary
  exit-af-topology
 exit-address-family
```

<div class="zh" markdown="1">

```cfg
! EIGRP 命名模式生产配置
router eigrp CAMPUS
 !
 address-family ipv4 unicast autonomous-system 100
  !
  network 10.0.0.0 0.255.255.255
  eigrp router-id 10.255.0.1
  !
  ! 关键：截断 Query 范围
  stub connected summary redistribute static
  !
  ! 接口级调优
  af-interface default
   passive-interface
   bfd
  exit-af-interface
  !
  af-interface TenGigabitEthernet1/1/1
   no passive-interface
   hello-interval 3
   hold-time 9
  exit-af-interface
  !
  ! 汇总（同时抑制明细，减少 Query 触发）
  topology base
   auto-summary
  exit-af-topology
 exit-address-family
```

</div>

> ⚠️ **The four EIGRP stub options must be chosen correctly**:
> | Option | Meaning | Used for |
> |------|------|------|
> | `connected` | Advertises only connected routes | Leaf sites (most common) |
> | `summary` | Advertises connected + summary routes | Sites with downstream routers |
> | `static` | Also advertises redistributed statics | Sites needing a local egress default route |
> | `redistributed` | Also advertises redistributed routes | Sites with local external routes |
> | `receive-only` | Receives only, never sends (does not take part in queries) | Extreme leaves (e.g. management-network devices) |
>
> A site configured with `stub connected` that **depends on a local static default route** will lose the default route when the primary link fails → exactly the same class of mistake as the OSPF stub case.

<div class="zh" markdown="1">

> ⚠️ **EIGRP Stub 的四个选项要选对**：
> | 选项 | 含义 | 用于 |
> |------|------|------|
> | `connected` | 只通告直连 | 末端站点（最常见） |
> | `summary` | 通告直连 + 汇总 | 有下级的站点 |
> | `static` | 也通告重分发的静态 | 需要本地出口默认路由 |
> | `redistributed` | 也通告重分发的路由 | 有本地外部路由 |
> | `receive-only` | 只收不发（不参与 Query） | 极末端（如管理网设备） |
>
> 配 `stub connected` 却**依赖本地静态默认路由**的站点，主链路断后会失去默认路由 → 与 OSPF Stub 那个案例是同一类错误。

</div>

### EIGRP Metrics and "Why It Does Not Route by Bandwidth" · EIGRP 度量与"为什么它不按带宽选路"

![The EIGRP composite metric and one slow hop capping a fast path](assets/fig/en08-18-eigrp-metric.svg)

The classic EIGRP composite metric:

<div class="zh" markdown="1">

EIGRP 的经典复合度量：

</div>

```
metric = 256 × ( 10^7 / minimum bandwidth (kbps)  +  accumulated delay (10μs) / 10 )
                       ↑                      ↑
                  only the smallest bandwidth   the sum of delays of all links
                  along the path
```

<div class="zh" markdown="1">

```
metric = 256 × ( 10^7 / 最小带宽(kbps)  +  累计延迟(10μs) / 10 )
                       ↑                      ↑
                  只看路径上最小带宽        所有链路延迟之和
```

</div>

| Characteristic | Design implication |
|------|---------|
| **Only the minimum bandwidth counts** | If one link in the path is 10M and the rest are 100G, the path is computed as 10M → **the "leaky bucket" effect** |
| **Delay accumulates** | More links significantly increase the metric |
| **Load/reliability are excluded by default** | The K values enable only bandwidth and delay by default (K1=1, K3=1, the rest 0) — **changing K values requires network-wide consistency, otherwise adjacencies fail** |

<div class="zh" markdown="1">

| 特性 | 设计含义 |
|------|---------|
| **只看最小带宽** | 路径上有一条 10M，后面全是 100G，也按 10M 算 → **"木桶效应"** |
| **延迟累加** | 链路数量多会显著增加度量 |
| **默认不算负载/可靠性** | K 值默认只启用带宽和延迟（K1=1, K3=1，其余 0）——**改 K 值必须全网一致，否则邻居起不来** |

</div>

> 💡 **EIGRP metrics compared with OSPF cost**: OSPF is **hop-by-hop additive**, EIGRP is "minimum bandwidth + delay sum". That leads to a counter-intuitive effect: **in a network with widely varying bandwidths, the two can produce completely opposite path selections**. This is also one of the sources of suboptimal paths in mixed deployments.

<div class="zh" markdown="1">

> 💡 **EIGRP 的度量与 OSPF cost 相比**：OSPF 是**逐跳相加**，EIGRP 是"最小带宽 + 延迟和"。这导致一个反直觉的现象：**在带宽差异大的网络中，两者的选路结果可能完全相反**。混合部署时这也是次优路径的来源之一。

</div>

### Choosing Between EIGRP and OSPF · EIGRP 与 OSPF 的选择

| Dimension | OSPF | EIGRP |
|------|------|-------|
| Vendor support | All vendors | Mostly Cisco (partially opened) |
| Fault localization | **Strong** (the LSDB shows the topology) | Medium (only the path set in the topology table) |
| Convergence | Fast (SPF + BFD) | **Fast (local repair with an FS, the fastest)** |
| Design complexity | Many area, LSA type, and area type choices | Relatively simple (no areas, rely on AS + summarization + stub) |
| Large-scale flooding | Yes (full flooding within an area) | No (only distances are propagated) |
| **Typical fit** | Multivendor, needs a clear topology view | Cisco-only, hub-and-spoke branches, simplicity |

<div class="zh" markdown="1">

| 维度 | OSPF | EIGRP |
|------|------|-------|
| 厂商支持 | 所有厂商 | 以 Cisco 为主（已部分开放） |
| 故障定位 | **强**（LSDB 能看到拓扑） | 中（只能看拓扑表的路径集合） |
| 收敛 | 快（SPF + BFD） | **快（有 FS 时本地修复，最快）** |
| 设计复杂度 | 区域、LSA 类型、区域类型较多 | 相对简单（无区域概念，靠 AS + 汇总 + Stub） |
| 大规模泛洪 | 有（区域内全泛洪） | 无（只传距离） |
| **典型适用** | 多厂商、需清晰拓扑视图 | 纯 Cisco、星型分支、追求简单 |

</div>

> 💡 **A genuine advantage of EIGRP**: it has **no hard constraint like "Area 0 must be contiguous"**, so the design has more freedom; and **when a feasible successor exists, failure recovery is a millisecond-level local switch** requiring no protocol interaction at all. OSPF (which must recompute SPF) cannot do that.

<div class="zh" markdown="1">

> 💡 **EIGRP 的一个真实优势**：它**没有"区域 0 必须连续"这类硬约束**，网络设计自由度更高；而且**有可行后继时故障恢复是"毫秒级本地切换"**，不需要任何协议交互。这是 OSPF（必须重算 SPF）做不到的。

</div>

---

## Traffic Engineering and Path Selection · 流量工程和路径选择

### Why Paths Need to Be Designed Explicitly · 为什么要专门设计路径

The IGP's SPF looks only at **topology and metric** — not at bandwidth utilization, not at business importance. The classic **10:1 bandwidth mismatch**:

<div class="zh" markdown="1">

IGP 的 SPF 只看**拓扑和度量**，不看带宽利用率、不看业务重要性。经典的 **10:1 带宽不匹配**：

</div>

```
        ┌──── 1G link (same cost) ────┐
   R1 ──┤                              ├── R2
        └──── 10G link (same cost) ───┘

SPF considers them equal → 50/50 load sharing
→ the 1G link is instantly congested while the 10G link runs at 5%
→ what users feel: the network is "slow overall", but neither link shows an obvious alarm
```

<div class="zh" markdown="1">

```
        ┌──── 1G 链路（cost 相同）────┐
   R1 ──┤                              ├── R2
        └──── 10G 链路（cost 相同）───┘

SPF 认为等价 → 负载分担 50/50
→ 1G 链路瞬间拥塞，10G 链路只用 5%
→ 用户感知：整体"网络慢"，但两条链路的告警都不明显
```

</div>

**Every designer reading this book must remember**: **the default IGP metric is almost never equivalent to "real available bandwidth"**. There are three reasons:

<div class="zh" markdown="1">

**读这本书的设计师必须记住**：**默认的 IGP 度量几乎从不等价于"真实可用带宽"**。原因有三：

</div>

1. `auto-cost` uses a 100M reference bandwidth by default (see above), so everything at 1G and above gets cost=1
2. Multipath load sharing is **per-flow hashing**, not proportional to actual traffic volume
3. Metrics do not reflect "reservations" and "policy" (e.g. voice priority, backup links that should not carry production traffic)

<div class="zh" markdown="1">

1. `auto-cost` 参考带宽默认 100M（见前文），G 以上全部 cost=1
2. 多路径负载分担是**按流哈希**，不是按流量的实际大小
3. 度量不反映"预留"与"策略"（如语音优先级、备份链路不应承载业务）

</div>

### The Four Layers of Path Control · 路径控制的四个层次

![Four layers of path control, and equal cost hiding a ten to one gap](assets/fig/en08-19-path-control.svg)

| Layer | Tool | Granularity | Visibility |
|------|------|------|--------|
| **① Metric tuning** | `ip ospf cost`, `bandwidth`, EIGRP metric | Link | Good (visible in `show ip route`) |
| **② Protocol policy** | Distribute lists, route maps, offset lists, AD changes | Prefix | Medium |
| **③ Summarization and area design** | Summaries, area types, stub | Set of prefixes | Medium |
| **④ Explicit paths** | MPLS-TE, SR-TE, PBR, SD-WAN policies | Flow/application | Poor (requires dedicated tooling) |

<div class="zh" markdown="1">

| 层次 | 手段 | 粒度 | 可见性 |
|------|------|------|--------|
| **① 度量调整** | `ip ospf cost`、`bandwidth`、EIGRP metric | 链路 | 好（`show ip route` 可见） |
| **② 协议策略** | 分发列表、路由映射、偏移列表、AD 调整 | 前缀 | 中 |
| **③ 汇总与区域设计** | 汇总、区域类型、stub | 前缀集合 | 中 |
| **④ 显式路径** | MPLS-TE、SR-TE、PBR、SD-WAN 策略 | 流/应用 | 差（需要专门工具验证） |

</div>

**Recommended design order**: do ① (metric and topology) first, then ② (policy), and only reach for ④ when ① and ② cannot achieve it. **PBR and tunnels are the last resort**, because they make the forwarding path deviate from the routing table and sharply increase troubleshooting difficulty (see the uRPF case in Chapter 10 — PBR combined with asymmetric paths directly causes uRPF to drop legitimate traffic).

<div class="zh" markdown="1">

**设计顺序建议**：先做 ①（度量与拓扑），再做 ②（策略），只有在 ① ② 做不到时才上 ④。**PBR 和隧道是"最后手段"**，因为它们让转发路径偏离路由表，排障难度陡增（见第 10 章 uRPF 案例——PBR 与非对称路径直接导致 uRPF 误杀）。

</div>

### Design Choices for Primary/Backup and Load Sharing · 主备与负载分担的设计选择

| Mode | Approach | Advantages | Disadvantages |
|------|------|------|------|
| **Equal-cost load sharing** | Keep the metrics identical (default behavior) | Zero configuration, high bandwidth utilization | **Per-flow hashing**, a single flow does not speed up; badly unbalanced when link bandwidths differ |
| **Unequal-cost primary/backup** | Set costs explicitly (primary 10 / backup 100) | Deterministic path, clear backup | The backup link sits idle long-term (wasted investment) |
| **Split by VLAN/subnet** | Different prefixes take different paths (policy or partitioning) | Bidirectional utilization, strong determinism | Complex configuration, needs addressing support |
| **Split by application (PBR/SD-WAN)** | Voice over the low-latency link, backups over the high-bandwidth link | Closest to business requirements | Complex, requires ongoing maintenance |
| **MPLS-TE / SR-TE** | Explicit path + bandwidth reservation | Precise control | Large state volume, vendor differences (see Chapter 9) |

<div class="zh" markdown="1">

| 模式 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| **等开销负载分担** | 保持度量相同（默认行为） | 零配置、带宽利用率高 | **按流哈希**，单流不加速；链路带宽不等时严重失衡 |
| **不等开销主备** | 显式设置 cost（主 10 / 备 100） | 路径确定、备份清晰 | 备份链路长期闲置（浪费投资） |
| **按 VLAN/网段分流** | 不同前缀走不同路径（策略或分区） | 双向利用、确定性强 | 配置复杂，需地址规划支撑 |
| **按业务分流（PBR/SD-WAN）** | 语音走低延迟链路，备份走大带宽 | 最贴近业务诉求 | 复杂、需持续维护 |
| **MPLS-TE / SR-TE** | 显式路径 + 带宽预留 | 精确控制 | 状态量大、厂商差异（见第 9 章） |

</div>

**What `max-path` (the ECMP limit) means**:

<div class="zh" markdown="1">

**`max-path`（ECMP 条数）的意义**：

</div>

| Platform | Default ECMP | Notes |
|------|----------|------|
| Most Cisco routers | 4 | Additional paths are not installed |
| Some platforms are configurable | 8 / 16 / 32 | Evaluate FIB capacity and hash quality |

<div class="zh" markdown="1">

| 平台 | 默认 ECMP | 说明 |
|------|----------|------|
| 多数 Cisco 路由器 | 4 | 超过则不装表 |
| 部分平台可调 | 8 / 16 / 32 | 需评估 FIB 容量与哈希质量 |

</div>

> ⚠️ **More ECMP paths is not better**: with more than 4 paths, poor hash quality (e.g. using only src-dst MAC) produces a very uneven distribution. **Confirm the hash factors before increasing the number of paths.**

<div class="zh" markdown="1">

> ⚠️ **ECMP 条数不是越多越好**：4 条以上时，如果哈希质量差（例如只用 src-dst MAC），实际分布会非常不均。**先确认哈希因子，再增加路径数。**

</div>

### Verifying That Paths Follow the Design (a Mandatory Acceptance Step) · 验证路径是否按设计走（设计验收的必做动作）

| What to verify | Command / method |
|-----------|------------|
| Is the route selected as expected | `show ip route <prefix>` (check AD/metric/next hop) |
| BGP's best path and the reason | `show ip bgp <prefix>` (it shows the reason for the selection) |
| The actual FIB entry | `show ip cef <prefix> detail` |
| Does forwarding use the expected interface | `traceroute` (note: ICMP may be blocked by ACLs/firewalls) |
| Per-hop interfaces and queues | `show interface` counters, `show policy-map interface` on each hop |
| **End-to-end traffic matrix** | NetFlow/sFlow (the only way to prove the actual path) |

<div class="zh" markdown="1">

| 要验证什么 | 命令 / 方法 |
|-----------|------------|
| 路由是否按预期选优 | `show ip route <prefix>`（看 AD/度量/下一跳） |
| BGP 的最佳路径及原因 | `show ip bgp <prefix>`（会显示选路理由） |
| 实际的 FIB 表项 | `show ip cef <prefix> detail` |
| 转发是否走了预期接口 | `traceroute`（注意：可能被 ACL/防火墙拦 ICMP） |
| 逐跳的接口与队列 | 各跳 `show interface` 计数器、`show policy-map interface` |
| **端到端流量矩阵** | NetFlow/sFlow（这是唯一能证明"实际路径"的手段） |

</div>

> 💡 **A counter-intuitive acceptance fact**: the path shown by `traceroute` is **not necessarily** the real path of the data flow (it depends on the return path of ICMP TTL-exceeded messages, and rate limiting of TTL-exceeded replies on many devices causes missing hops). **To verify the real path you must look at flow data (NetFlow) or capture packets hop by hop.**

<div class="zh" markdown="1">

> 💡 **一个反直觉的验收事实**：`traceroute` 显示的路径**不一定**就是数据流的真实路径（它依赖 ICMP TTL 超时的回程，且很多设备对 TTL 超时的限速会导致缺跳）。**要验证真实路径，必须看流数据（NetFlow）或逐跳抓包。**

</div>

---

## BGP Routing · BGP 路由

### BGP Fundamental Concepts · BGP 基础概念

BGP is a **path-vector** protocol that runs over TCP 179. Its fundamental differences from an IGP:

<div class="zh" markdown="1">

BGP 是**路径矢量**协议，运行在 TCP 179 之上。它与 IGP 的根本差异：

</div>

| Dimension | IGP (OSPF/IS-IS/EIGRP) | BGP |
|------|------------------------|-----|
| **Goal** | Find the **optimal** path | Enforce **policy** and find the path that **matches intent** |
| **Topology** | Every node knows the whole topology | Only knows "which ASes are traversed" |
| **Metric** | A single cost | A dozen attributes compared in a fixed order |
| **Scale** | Thousands of routes | **Millions** of routes (the full Internet table) |
| **Convergence** | Seconds | Seconds to minutes (depends on session count and prefix volume) |
| **Trust model** | Internal, trusted by default | **Untrusted by default, trust only your neighbors** |

<div class="zh" markdown="1">

| 维度 | IGP（OSPF/IS-IS/EIGRP） | BGP |
|------|------------------------|-----|
| **目标** | 找到**最优**路径 | 执行**策略**，找到**符合意图**的路径 |
| **拓扑** | 每个节点都知道全网拓扑 | 只知道"经过哪些 AS" |
| **度量** | 单一的 cost | 十几种属性，按固定顺序比较 |
| **规模** | 数千条路由 | **百万级**路由（互联网全表） |
| **收敛** | 秒级 | 秒到分钟级（取决于会话数与前缀量） |
| **信任模型** | 内部、默认可信 | **默认不可信，只信邻居** |

</div>

#### Key Terms · 关键术语

| Term | Meaning |
|------|------|
| **AS (autonomous system)** | A set of networks under a single administrative domain |
| **eBGP** | A session between ASes (TTL defaults to 1, directly connected) |
| **iBGP** | A session inside the same AS (**must be fully meshed or use RRs/confederations**) |
| **Synchronization** | A historical requirement that iBGP routes be learned through the IGP before use. **Disabled by default today** (`no synchronization`) |
| **Next hop** | For routes learned over eBGP the next hop is usually **unchanged** (unless `next-hop-self` is configured) |

<div class="zh" markdown="1">

| 术语 | 含义 |
|------|------|
| **AS（自治系统）** | 单一管理域下的网络集合 |
| **eBGP** | AS 之间的会话（TTL 默认 1，直连） |
| **iBGP** | 同一 AS 内的会话（**必须全互连或经 RR/联盟**） |
| **同步（Synchronization）** | 历史要求：iBGP 路由需经 IGP 学到才可用。**现代默认关闭**（`no synchronization`） |
| **下一跳** | eBGP 学到的路由，下一跳通常**不改变**（除非 `next-hop-self`） |

</div>

> ⚠️ **The iBGP full-mesh rule** (the most commonly misunderstood one): a route learned over iBGP **is not passed on to another iBGP neighbor** (loop prevention). So N routers need **N(N−1)/2** sessions. That is exactly why route reflectors exist.

<div class="zh" markdown="1">

> ⚠️ **iBGP 全互连规则**（最容易被误解的一条）：iBGP 学的路由**不会再传给另一个 iBGP 邻居**（防环）。所以 N 台路由器需要 **N(N−1)/2** 条会话。这就是 RR 存在的理由。

</div>

| Number of routers | Full-mesh sessions | Notes |
|---------|------------|------|
| 5 | 10 | Acceptable |
| 10 | 45 | Starts to become hard to maintain |
| 50 | 1,225 | Unacceptable |
| 200 | 19,900 | Route reflectors are mandatory |

<div class="zh" markdown="1">

| 路由器数 | 全互连会话数 | 说明 |
|---------|------------|------|
| 5 | 10 | 可接受 |
| 10 | 45 | 开始难维护 |
| 50 | 1,225 | 不可接受 |
| 200 | 19,900 | 必须用 RR |

</div>

### BGP as the Core Routing Protocol: When to Use It · BGP 作为核心路由协议：什么时候该用

| Scenario | Why BGP |
|------|-------------|
| **Multihomed Internet egress** | You need egress selection by LP/MED/AS_PATH |
| **Large enterprise core** | The IGP flooding domain cannot scale; BGP carries only reachability |
| **Interconnecting multiple IGP domains or vendor domains** | BGP is the only "common language" |
| **Fine-grained policy control is needed** | The IGP has one knob (cost), BGP has a dozen attributes |
| **MPLS L3VPN / EVPN** | BGP carries VPN routes (Chapter 9) |
| **SD-WAN / cloud interconnection** | The common transport for policy routing |

<div class="zh" markdown="1">

| 场景 | 用 BGP 的理由 |
|------|-------------|
| **多宿主 Internet 出口** | 需要按 LP/MED/AS_PATH 做出口选择 |
| **大型企业核心** | IGP 泛洪域无法承受规模，BGP 只传可达性 |
| **多个 IGP 域/多个厂商域互联** | BGP 是唯一的"通用语言" |
| **需要精细的策略控制** | IGP 只有 cost 一个旋钮，BGP 有十几个属性 |
| **MPLS L3VPN / EVPN** | 用 BGP 承载 VPN 路由（第 9 章） |
| **SD-WAN / 云互联** | 策略路由的通用载体 |

</div>

| Scenarios where BGP should not be used | Reason |
|-----------------|------|
| Single-egress, single-domain enterprise network | Complexity far exceeds the benefit |
| Small networks (< 20 devices) | An IGP is enough; BGP only adds operational cost |
| The team is unfamiliar with BGP and there is no external requirement | Without troubleshooting skills, BGP is a risk |

<div class="zh" markdown="1">

| 不该用 BGP 的场景 | 原因 |
|-----------------|------|
| 单出口的单域企业网 | 复杂度远超收益 |
| 小型网络（< 20 台） | IGP 足矣，BGP 只会增加运维成本 |
| 团队不熟悉 BGP 且无外部需求 | 排障能力不足时 BGP 是风险 |

</div>

> 💡 **A rule of thumb**: **use BGP when you need "policy", use an IGP when you only need "reachability".** Put another way — if all paths are equally good, you do not need BGP; if "which path is better" depends on the business rather than the topology, you need BGP.

<div class="zh" markdown="1">

> 💡 **判断口诀**：**需要"策略"就用 BGP，只需要"可达性"就用 IGP。** 换句话说——如果所有路径一样好，你不需要 BGP；如果"哪条路径更好"取决于业务而不是拓扑，你需要 BGP。

</div>

### BGP Scalability Options · BGP 可扩展性选项

![iBGP full mesh growth and the route reflector alternative](assets/fig/en08-20-bgp-scaling.svg)

#### Route Reflector (RR) · 路由反射器

| Concept | Description |
|------|------|
| **RR** | Allowed to reflect routes learned over iBGP to other iBGP neighbors (breaking the full-mesh rule) |
| **Client** | A client of the RR (does not need to be fully meshed) |
| **Non-client** | Has an ordinary iBGP relationship with the RR |
| **Cluster ID** | The RR cluster identifier, used for **loop prevention** (routes carry a Cluster List; a route containing your own Cluster ID is discarded) |
| **Originator ID** | The Router ID of the original advertiser, the second loop-prevention mechanism |

<div class="zh" markdown="1">

| 概念 | 说明 |
|------|------|
| **RR** | 允许把从 iBGP 学到的路由反射给其他 iBGP 邻居（打破全互连规则） |
| **Client** | RR 的客户端（不需要全互连） |
| **Non-client** | 与 RR 是普通 iBGP 关系 |
| **Cluster ID** | RR 集群标识，**防环**（路由带 Cluster List，收到自己 Cluster ID 的路由丢弃） |
| **Originator ID** | 原始通告者的 Router ID，防环的第二道 |

</div>

**Key design constraints for RRs**:

<div class="zh" markdown="1">

**RR 的关键设计约束**：

</div>

| Constraint | Consequence |
|------|------|
| **The RR must be in the same IGP area (link-state protocols)** | An RR and its clients in different areas → depends on inter-area routes, which may produce suboptimal or unreachable paths |
| **Cluster IDs must be unique** (across RR clusters) | Duplicates → routes are wrongly considered loops and discarded |
| **RR redundancy must be paired, and clients must connect to both RRs** | A single RR failure → routes through that cluster are lost |
| **An RR is not a "forwarding node"** | The RR reflects only the control plane; the data plane still follows the IGP |

<div class="zh" markdown="1">

| 约束 | 后果 |
|------|------|
| **RR 必须在 IGP 的同一区域内（链路状态协议）** | RR 与客户端跨区域 → 依赖区域间路由，可能出现次优或路由不可达 |
| **Cluster ID 必须唯一**（不同 RR 集群之间） | 相同 → 路由被误判为环而丢弃 |
| **RR 冗余要成对，且客户端要连两个 RR** | 单 RR 故障 → 该集群路由中断 |
| **RR 不是"转发节点"** | RR 只反射控制面，数据面仍按 IGP 走 |

</div>

```cfg
! RR configuration
router bgp 65000
 bgp cluster-id 1.1.1.1
 bgp log-neighbor-changes
 !
 neighbor 10.0.0.1 remote-as 65000
 neighbor 10.0.0.1 update-source Loopback0
 neighbor 10.0.0.1 route-reflector-client
 !
 neighbor 10.0.0.2 remote-as 65000
 neighbor 10.0.0.2 update-source Loopback0
 neighbor 10.0.0.2 route-reflector-client
 !
 ! Optional: disable client-to-client reflection (depends on requirements)
 no bgp client-to-client reflection    ! if the clients already have direct iBGP sessions between them
```

<div class="zh" markdown="1">

```cfg
! RR 配置
router bgp 65000
 bgp cluster-id 1.1.1.1
 bgp log-neighbor-changes
 !
 neighbor 10.0.0.1 remote-as 65000
 neighbor 10.0.0.1 update-source Loopback0
 neighbor 10.0.0.1 route-reflector-client
 !
 neighbor 10.0.0.2 remote-as 65000
 neighbor 10.0.0.2 update-source Loopback0
 neighbor 10.0.0.2 route-reflector-client
 !
 ! 建议：关闭客户端到客户端的反射（视需求）
 no bgp client-to-client reflection    ! 若客户端之间已有直连 iBGP
```

</div>

> ⚠️ **The `no bgp client-to-client reflection` trap**: after you disable it (to reduce RR load), if the clients do **not** have direct iBGP sessions between them, routing breaks. This is a textbook case of an "optimization" becoming an outage — **confirm the client connectivity model before changing it**.

<div class="zh" markdown="1">

> ⚠️ **`no bgp client-to-client reflection` 的陷阱**：关掉它（为了减少 RR 负担）后，如果客户端之间**没有**直连 iBGP，路由就断了。这是"优化"变成故障的典型案例 —— **改之前必须确认客户端的连通性模型**。

</div>

#### Confederation · 联盟

| Characteristic | Description |
|------|------|
| Splits one large AS into multiple sub-ASes | Sessions between sub-ASes are eBGP sessions (but keep iBGP attributes) |
| Reduces the iBGP full-mesh requirement | Each sub-AS still needs a full mesh or RRs of its own |
| **Appears as a single AS externally** | Sub-ASes are invisible outside |
| Complexity | **High** (special AS_PATH handling, hard to troubleshoot) |

<div class="zh" markdown="1">

| 特点 | 说明 |
|------|------|
| 把一个大 AS 拆成多个子 AS（sub-AS） | 内部子 AS 之间是 eBGP 会话（但保留 iBGP 属性） |
| 减少 iBGP 全互连需求 | 每个子 AS 内部仍需全互连或再用 RR |
| **对外表现为一个 AS** | 外部看不到子 AS |
| 复杂度 | **高**（AS_PATH 处理特殊、排障困难） |

</div>

> 💡 **Confederation vs RR**: **choose RR almost always**. The complexity of confederations (sub-AS numbering, the `( )` notation in AS_PATH, cross-sub-AS policy) is far higher than the benefit. Confederations are used only in a very small number of very large SP environments. The book lists it as an option, but the practical design advice is "know that it exists, avoid using it".

<div class="zh" markdown="1">

> 💡 **联盟 vs RR 的选择**：**几乎总是选 RR**。联盟的复杂度（子 AS 编号、AS_PATH 中的 `( )` 表示、跨子 AS 的策略）远高于收益。联盟只在极少数超大型 SP 环境使用。书里把它列为选项，但实际设计建议是"知道它存在，尽量不用"。

</div>

#### Peer Groups / Peer Templates · Peer Group / 邻居模板

| Tool | Effect | Benefit |
|------|------|------|
| **Peer Group** | Groups neighbors that share the same policy, with policy applied to the group | Configuration shrinks from N entries to 1 |
| **Peer Template** | More flexible (inheritance plus override) | Supports inheritance hierarchies |
| **Dynamic neighbors (BGP listen / dynamic neighbor)** | Configure only a subnet range and neighbors form automatically | Suitable for large-scale/cloud environments (but high security risk) |

<div class="zh" markdown="1">

| 手段 | 作用 | 收益 |
|------|------|------|
| **Peer Group** | 把相同策略的邻居分组，策略配在组上 | 配置量从 N 条降到 1 条 |
| **Peer Template** | 更灵活（可继承 + 覆盖） | 支持继承层次 |
| **动态邻居（BGP Listen / Dynamic Neighbor）** | 只配一个网段范围，邻居自动建立 | 适合大规模/云环境（但安全风险高） |

</div>

```cfg
! Peer Group: all eBGP upstreams share one policy
router bgp 65000
 neighbor UPSTREAM peer-group
 neighbor UPSTREAM remote-as 65100
 neighbor UPSTREAM description ISP-A
 neighbor UPSTREAM password <strong-key>
 neighbor UPSTREAM ttl-security hops 1
 neighbor UPSTREAM route-map RM-UPSTREAM-IN in
 neighbor UPSTREAM route-map RM-UPSTREAM-OUT out
 neighbor UPSTREAM maximum-prefix 900000 90 warning-only
 !
 neighbor 203.0.113.1 peer-group UPSTREAM
```

<div class="zh" markdown="1">

```cfg
! Peer Group：所有 eBGP 上游共用策略
router bgp 65000
 neighbor UPSTREAM peer-group
 neighbor UPSTREAM remote-as 65100
 neighbor UPSTREAM description ISP-A
 neighbor UPSTREAM password <强密钥>
 neighbor UPSTREAM ttl-security hops 1
 neighbor UPSTREAM route-map RM-UPSTREAM-IN in
 neighbor UPSTREAM route-map RM-UPSTREAM-OUT out
 neighbor UPSTREAM maximum-prefix 900000 90 warning-only
 !
 neighbor 203.0.113.1 peer-group UPSTREAM
```

</div>

**Three things to watch with peer groups**:

<div class="zh" markdown="1">

**Peer Group 的三个注意点**：

</div>

1. **Only neighbors with the same `remote-as` can share a group** (every eBGP upstream has a different AS, so in practice you group by "policy" rather than by "AS" and then override `remote-as` per neighbor)
2. **Policy inside a group is uniform** — one `route-map` affects the whole group, so changes are risky
3. **Check that `update-source` and `ebgp-multihop` are consistent inside the group**, otherwise some neighbors will not come up

<div class="zh" markdown="1">

1. **`remote-as` 相同的才能进同一组**（eBGP 每家上游的 AS 都不同，实际常按"策略"而不是"AS"分组，需要 `remote-as` 逐条覆盖）
2. **组内策略是统一的**——一条 `route-map` 影响全组，改动风险大
3. **组内成员的 `update-source`、`ebgp-multihop` 一致性**要检查，否则部分邻居起不来

</div>

### The BGP Best Path Selection Process (the 13 Criteria in Detail) · BGP 选路过程（13 条判据详解）

![BGP best path: twelve criteria in order, with criterion eight highlighted](assets/fig/en08-21-bgp-bestpath.svg)

BGP picks the best path out of several candidates by comparing the following criteria **one by one in order, stopping at the first difference**:

<div class="zh" markdown="1">

BGP 从多条路径中选择最佳路径，按以下顺序**逐条比较，遇到不同即停止**：

</div>

| # | Criterion | Direction | Scope | Notes |
|---|------|------|--------|------|
| **1** | **Weight** | **Higher wins** | Local only | Cisco proprietary; not propagated; locally originated routes default to 32768, everything else 0 |
| **2** | **Local Preference** | **Higher wins** | Whole AS | Default 100; **the main tool for controlling which exit you leave through** |
| **3** | **Locally originated** (network / aggregate / redistribute) | Local wins | Local | Locally generated routes beat learned routes |
| **4** | **AS_PATH length** | **Shorter wins** | Whole AS | Note: can be affected by `as-override`/`allowas-in`; confederation sub-ASes are not counted |
| **5** | **Origin** | IGP < EGP < Incomplete | Whole AS | `network` produces IGP, `redistribute` produces Incomplete |
| **6** | **MED (multi-exit discriminator)** | **Lower wins** | Adjacent AS (default) | By default compared only **within the same neighbor AS**; a hint for ingress selection |
| **7** | **eBGP over iBGP** | eBGP preferred | — | Because eBGP is closer to the destination |
| **8** | **IGP metric to the NEXT_HOP** | Lower wins | Local | **This is the one from counter-intuitive truth #1** |
| **9** | **Oldest eBGP path** (Cisco) | First learned wins | Local | Reduces churn; `bgp bestpath compare-routerid` changes this |
| **10** | **Lowest Router ID / Originator ID** | Lower wins | — | Routes learned from an RR compare Originator IDs |
| **11** | **Shortest Cluster List** | Shorter wins | — | Fewer RRs traversed |
| **12** | **Lowest neighbor IP address** | Lower wins | — | The final tie-breaker |

<div class="zh" markdown="1">

| # | 判据 | 方向 | 作用域 | 说明 |
|---|------|------|--------|------|
| **1** | **Weight（权重）** | **大者优** | 本机有效 | Cisco 专有；不传递；默认本地起源 32768，其它 0 |
| **2** | **Local Preference（本地优先）** | **大者优** | 整个 AS | 默认 100；**控制"从哪个出口出去"的主要工具** |
| **3** | **本地起源**（network / aggregate / redistribute） | 本地优先 | 本机 | 本地产生的路由优于学来的 |
| **4** | **AS_PATH 长度** | **短者优** | 整个 AS | 注意：可被 `as-override`/`allowas-in` 影响；联盟子 AS 不计入 |
| **5** | **Origin（起源）** | IGP < EGP < Incomplete | 整个 AS | `network` 产生 IGP，`redistribute` 产生 Incomplete |
| **6** | **MED（多出口判别器）** | **小者优** | 相邻 AS（默认） | 默认只在**同一邻居 AS** 内比较；控制"入口选择"的提示 |
| **7** | **eBGP 优于 iBGP** | eBGP 优先 | — | 因为 eBGP 更接近目的地 |
| **8** | **到 NEXT_HOP 的 IGP metric** | 小者优 | 本机 | **这就是导读反直觉一说的那条** |
| **9** | **最老的 eBGP 路径**（Cisco） | 先学到者优 | 本机 | 减少抖动；`bgp bestpath compare-routerid` 可改变 |
| **10** | **最低 Router ID / Originator ID** | 小者优 | — | 从 RR 学来的用 Originator ID 比较 |
| **11** | **最短 Cluster List** | 短者优 | — | 经过的 RR 少 |
| **12** | **最低邻居 IP 地址** | 小者优 | — | 最后的兜底 |

</div>

> 💡 **A mnemonic**: **"me" in (Weight) → "us" out (Local Pref) → who gave birth (locally originated) → short path (AS_PATH) → good pedigree (Origin) → the guest follows the host (MED) → family is worse than strangers (eBGP > iBGP) → take the short cut (IGP) → old is stable (oldest) → small name (Router ID) → fewer detours (Cluster List) → small neighbor (neighbor IP)**.

<div class="zh" markdown="1">

> 💡 **记忆口诀**：**"我"In（Weight）→ "我们"出（Local Pref）→ 谁生（本地起源）→ 路短（AS_PATH）→ 出身好（Origin）→ 客随主便（MED）→ 自己人不如外人（eBGP > iBGP）→ 走近路（IGP）→ 老的稳（oldest）→ 名字小（Router ID）→ 少绕圈（Cluster List）→ 邻居小（neighbor IP）**。

</div>

#### Practical Use of the First Six Criteria · 前六条的实战用法

| What you want | Which criterion | Where it is configured | Watch out |
|------------|--------|--------|------|
| **Exit only through one specific egress** (hard control) | Weight | Locally | Affects only this router; multiple devices must each be configured |
| **The whole AS exits through one egress** | Local Preference | Inbound (from eBGP neighbors) | Propagated across the AS; setting LP outbound toward eBGP has no effect |
| **Influence only your own ingress** (which way neighbors come in) | MED | Outbound (on routes you advertise) | Only effective toward **the same neighbor AS**, not comparable across ASes |
| **Prefer locally generated routes** | Locally originated | Automatic | — |
| **Demote a path by lengthening AS_PATH** | AS_PATH prepend | Outbound | Wide blast radius, easily affects your own downstreams |
| **Distinguish IGP/EGP/Incomplete** | Origin | Set automatically on redistribution | `redistribute` defaults to Incomplete; `route-map set origin igp` changes it |

<div class="zh" markdown="1">

| 想达到的目的 | 用哪条 | 配在哪 | 注意 |
|------------|--------|--------|------|
| **只用某个出口出去**（强控制） | Weight | 本机 | 只影响本机，多台设备要逐台配 |
| **整个 AS 从某出口出去** | Local Preference | 入方向（对 eBGP 邻居 inbound） | AS 内全传；出方向配 LP 对 eBGP 无效 |
| **只影响自己的入口**（邻居进来走哪） | MED | 出方向（对自己通告的路由） | 只对**同一邻居 AS** 有效，跨 AS 不可比 |
| **本地产生的路由优先** | 本地起源 | 自动 | — |
| **通过加长 AS_PATH 降级某条** | AS_PATH prepend | 出方向 | 影响范围大，容易波及自己的下游 |
| **区分 IGP/EGP/Incomplete** | Origin | 重分发时自动设置 | `redistribute` 默认 Incomplete，可用 `route-map set origin igp` |

</div>

**Where to configure Local Preference (a high-frequency mistake)**:

<div class="zh" markdown="1">

**Local Preference 的配置位置（高频错误）**：

</div>

```
Toward an eBGP neighbor:
  LP configured inbound  → effective (affects this AS's egress selection) ✅
  LP configured outbound → no effect (LP is not propagated across an AS) ❌

Toward an iBGP neighbor:
  Usually set on the RR / border routers and propagated across the AS by iBGP
```

<div class="zh" markdown="1">

```
对 eBGP 邻居：
  inbound 方向配 LP → 有效（影响本 AS 的出口选择）✅
  outbound 方向配 LP → 无效（LP 不跨 AS 传递）❌

对 iBGP 邻居：
  通常在 RR / 边界路由器上设置，由 iBGP 传给全 AS
```

</div>

**The three limitations of MED (memorize these)**:

<div class="zh" markdown="1">

**MED 的三条限制（务必记住）**：

</div>

1. **By default it is compared only among multiple paths from the same neighbor AS** — MEDs from different ASes are not comparable
2. **MED is a "hint", not a "command"** — the neighbor may ignore it (`always-compare-med` is a double-edged sword)
3. **Setting MED inbound toward eBGP has no effect** (MED only makes sense when you send it out)

<div class="zh" markdown="1">

1. **默认只在同一邻居 AS 的多条路径之间比较**——来自不同 AS 的 MED 不可比
2. **MED 是"提示"不是"命令"**——邻居可以忽略（`always-compare-med` 是把双刃剑）
3. **入方向设置 MED 对 eBGP 无效**（MED 要发出去才有意义）

</div>

```cfg
! Egress selection: prefer ISP-A
route-map RM-FROM-ISP-A permit 10
 set local-preference 200

route-map RM-FROM-ISP-B permit 10
 set local-preference 150

router bgp 65000
 neighbor 203.0.113.1 remote-as 65100
 neighbor 203.0.113.1 route-map RM-FROM-ISP-A in
 neighbor 198.51.100.1 remote-as 65200
 neighbor 198.51.100.1 route-map RM-FROM-ISP-B in
```

<div class="zh" markdown="1">

```cfg
! 出口选择：优先 ISP-A
route-map RM-FROM-ISP-A permit 10
 set local-preference 200

route-map RM-FROM-ISP-B permit 10
 set local-preference 150

router bgp 65000
 neighbor 203.0.113.1 remote-as 65100
 neighbor 203.0.113.1 route-map RM-FROM-ISP-A in
 neighbor 198.51.100.1 remote-as 65200
 neighbor 198.51.100.1 route-map RM-FROM-ISP-B in
```

</div>

```cfg
! Ingress influence: tell ISP-A to come in through the closer link (MED)
route-map RM-TO-ISP-A permit 10
 match ip address prefix-list PL-LOCAL
 set metric 50

route-map RM-TO-ISP-B permit 10
 match ip address prefix-list PL-LOCAL
 set metric 100

! Note: send the smaller MED on the link you want others to prefer
```

<div class="zh" markdown="1">

```cfg
! 入口影响：告诉 ISP-A 从更近的链路进来（MED）
route-map RM-TO-ISP-A permit 10
 match ip address prefix-list PL-LOCAL
 set metric 50

route-map RM-TO-ISP-B permit 10
 match ip address prefix-list PL-LOCAL
 set metric 100

! 注意：这是在"希望别人优先进来的那条链路上"发较小的 MED
```

</div>

> ⚠️ **The most classic MED misunderstanding**: many people believe that "sending MED 50 to ISP-A and MED 100 to ISP-B makes the ISPs prefer A for ingress". In reality **A and B are two different ASes and their MEDs are not comparable** (unless the peer has configured `always-compare-med` in the same decision context). **MED is only effective among multiple links to the same neighbor AS** — that is, two links to the same ISP. Cross-ISP ingress control can only rely on AS_PATH prepend (and even that may be overridden).

<div class="zh" markdown="1">

> ⚠️ **MED 的最经典误解**：很多人以为"给 ISP-A 发 MED 50、给 ISP-B 发 MED 100，ISP 就会优选 A 进来"。实际上 **A 和 B 是两个不同的 AS，它们各自的 MED 不可比**（除非对方配了 `always-compare-med` 且在同一决策上下文）。**MED 只对"同一个邻居 AS 的多条链路"有效**——也就是同一个 ISP 的两条链路。跨 ISP 的入口控制只能靠 AS_PATH prepend（而且对方也可能覆盖）。

</div>

### Vendor Differences in BGP (Must Be Confirmed During Design) · BGP 的厂商差异（设计时必须确认）

| Behavior | Cisco default | Standard / other vendors | Risk |
|------|-----------|---------------|------|
| **`default local-preference`** | 100 | Some vendors 100, some configurable | Inconsistency leads to confused egress selection |
| **MED comparison** | Compared only within the same neighbor AS (`deterministic-med` behavior) | Some vendors compare always | The two sides expect different things |
| **`always-compare-med`** | Off | Can be enabled | Once on, MED is compared across ASes and results may differ from the peer |
| **Confederation sub-AS in AS_PATH** | Not counted in the length by default | Counted by some vendors | Different length results |
| **`bgp bestpath as-path ignore`** | Off | — | Enabling it ignores AS_PATH length → inconsistent with the rest of the network |
| **Router ID election** | Highest loopback IP, then highest physical interface IP | Different on some vendors | Affects criterion 10 |
| **When `bgp router-id` is missing by default** | Uses the highest interface IP | Some vendors require it explicitly | Neighbors may fail to come up |
| **`next-hop-self` default** | Off | — | An unreachable next hop in iBGP is a high-frequency failure |

<div class="zh" markdown="1">

| 行为 | Cisco 默认 | 标准 / 其他厂商 | 风险 |
|------|-----------|---------------|------|
| **`default local-preference`** | 100 | 部分厂商 100，部分可配 | 不一致导致出口选择混乱 |
| **MED 比较** | 只在同一邻居 AS 内比较（`deterministic-med` 行为） | 部分厂商默认全比较 | 双方预期不同 |
| **`always-compare-med`** | 关闭 | 可开 | 开启后跨 AS 比 MED，结果可能与对方不同 |
| **AS_PATH 中的联盟子 AS** | 默认不计入长度 | 部分厂商计入 | 长度计算结果不同 |
| **`bgp bestpath as-path ignore`** | 关闭 | — | 开启会忽略 AS_PATH 长度 → 与全网不一致 |
| **Router ID 选举** | 最高 Loopback IP，其次最高物理接口 IP | 部分厂商不同 | 影响第 10 条判据 |
| **默认 `bgp router-id` 缺失时** | 用最高接口 IP | 部分厂商必须显式配置 | 邻居可能起不来 |
| **`next-hop-self` 默认** | 关闭 | — | iBGP 里下一跳不可达是高频故障 |

</div>

> 💡 **Practical advice for multivendor BGP interconnection**: before peering, go through the table above item by item with the other side and write it into the interconnection document. **BGP is "standard" only in attribute format; it is not fully unified in default decision behavior.**

<div class="zh" markdown="1">

> 💡 **多厂商 BGP 互联的实操建议**：在互联前，把上表逐项与对方核对并写进互联文档。**BGP 的"标准"只在属性格式上标准，在"默认决策行为"上并不完全统一。**

</div>

### Egress and Ingress Traffic Policies · 出口和入口流量策略

BGP traffic control is fundamentally **designed separately for the two directions**:

<div class="zh" markdown="1">

BGP 的流量控制本质是**两个方向分别设计**：

</div>

| Direction | What you want to control | Available tools | Effectiveness |
|------|------------|---------|--------|
| **Egress (from you to them)** | Which exit my traffic leaves through | Weight, Local Preference, AS_PATH prepend | **Fully controllable** (your devices, your decision) |
| **Ingress (from them to you)** | Which path others take to reach you | MED, AS_PATH prepend, more specific advertisements (/24 vs /23) | **Partially controllable** (the peer may ignore it) |

<div class="zh" markdown="1">

| 方向 | 你要控制什么 | 可用工具 | 有效性 |
|------|------------|---------|--------|
| **出向（Egress，你去别人）** | 我的流量从哪个出口出去 | Weight、Local Preference、AS_PATH prepend | **完全可控**（自己的设备自己说了算） |
| **入向（Ingress，别人来你）** | 别人进来走哪条路 | MED、AS_PATH prepend、更具体的通告（/24 vs /23） | **部分可控**（对方可能不理） |

</div>

**Realistic means of ingress control (ordered by effectiveness)**:

<div class="zh" markdown="1">

**入向控制的现实手段（按有效性排序）**：

</div>

| Tool | Effectiveness | Cost |
|------|--------|------|
| **Advertise a more specific prefix** (advertise /24 on the preferred inbound link and only /23 on the other) | **Highest** (longest match always wins) | More routing table entries; may be blocked by prefix filters |
| **AS_PATH prepend** (lengthen the path you do not want used) | Medium (the peer may have `bgp bestpath as-path ignore`) | Pollutes AS_PATH and affects downstreams |
| **MED** (multiple links to the same ISP) | Medium (the peer may ignore it) | Ineffective across ASes |
| **Contract with the ISP / submit BGP communities** | Depends on the ISP | Requires commercial coordination |
| **Just pick one link** (no ingress splitting) | Deterministic | Give up ingress utilization of the other link |

<div class="zh" markdown="1">

| 手段 | 有效性 | 代价 |
|------|--------|------|
| **通告更具体的前缀**（在希望的入链路上只通告 /24，另一条只通告 /23） | **最高**（最长匹配必胜） | 增加路由表条目；可能被前缀过滤器拦 |
| **AS_PATH prepend**（不希望走的路径加长） | 中（对方可能配 `bgp bestpath as-path ignore`） | 污染 AS_PATH，影响下游 |
| **MED**（同一 ISP 的多链路） | 中（对方可忽略） | 跨 AS 无效 |
| **与 ISP 签协议 / 提交社区（BGP Community）** | 取决于 ISP | 需商务配合 |
| **就选一条链路**（不做入口分流） | 确定 | 放弃另一条链路的入口利用 |

</div>

> ⚠️ **A fact that must go into the design document**: **for ingress traffic you can only "request", never "command"**. Any claim that "we implemented dual-egress load sharing" is, without control over the far end, actually "egress is balanced, ingress is not" — which regularly causes disputes at acceptance time.

<div class="zh" markdown="1">

> ⚠️ **一条必须写进设计文档的事实**：**入向流量你只能"请求"，不能"命令"**。任何"我们做了双出口负载分担"的说法，在不控制对端的前提下，实际效果是"出向分担了，入向没分担"——这在验收时经常引发争议。

</div>

### BGP Convergence and Stability · BGP 收敛与稳定性

| Mechanism | Effect | Design recommendation |
|------|------|---------|
| **`bgp update-delay`** | Waits N seconds after startup before selecting paths (waiting for all neighbors) | Mandatory in large networks (e.g. 300–600 s), avoids "forwarding with an incomplete table" |
| **`bgp scan-time`** | Next-hop validity check interval | Default 60 s, can be reduced to 10–20 s |
| **Next-hop tracking** | Withdraws routes proactively when the next hop becomes unreachable | Enabled by default on modern platforms (`bgp nexthop trigger enable`) |
| **Route dampening** | Suppresses repeatedly flapping prefixes | **Use with care**: prefix flaps are common on today's Internet and over-suppression causes long black holes |
| **Maximum prefix** | Protects against routing table explosion | See Chapter 10 |
| **`maximum-paths`** | Number of ECMP paths | According to platform capability |
| **BGP graceful restart (GR/NSF)** | Keeps forwarding while the control plane restarts | Requires neighbor support |
| **BFD** | Fast neighbor failure detection | Better than shrinking Keepalive |

<div class="zh" markdown="1">

| 机制 | 作用 | 设计建议 |
|------|------|---------|
| **`bgp update-delay`** | 启动后等待 N 秒再开始选路（等所有邻居建立） | 大网必配（如 300–600 秒），避免"用不完整的表转发" |
| **`bgp scan-time`** | 下一跳有效性检查周期 | 默认 60s，可降至 10–20s |
| **下一跳跟踪（nexthop tracking）** | 下一跳不可达时主动撤销 | 现代默认开启（`bgp nexthop trigger enable`） |
| **Route Dampening** | 抑制反复 flapping 的前缀 | **慎用**：现代互联网 prefix flap 很常见，过度抑制会造成长时间黑洞 |
| **最大前缀** | 防路由表爆炸 | 见第 10 章 |
| **`maximum-paths`** | ECMP 条数 | 按平台能力 |
| **BGP 优雅重启（GR/NSF）** | 控制面重启时不中断转发 | 需邻居支持 |
| **BFD** | 快速检测邻居失效 | 优于调小 Keepalive |

</div>

```cfg
! BGP stability production baseline
router bgp 65000
 bgp router-id 10.255.0.1
 bgp log-neighbor-changes
 bgp update-delay 300                  ! wait for neighbors and routes to converge
 bgp graceful-restart
 no bgp default ipv4-unicast           ! enable explicitly, avoiding unintended advertisements
 !
 neighbor 10.0.0.1 remote-as 65000
 neighbor 10.0.0.1 update-source Loopback0
 neighbor 10.0.0.1 fall-over bfd       ! fast detection
 neighbor 10.0.0.1 maximum-prefix 2000 90 warning-only
 !
 address-family ipv4 unicast
  neighbor 10.0.0.1 activate
  neighbor 10.0.0.1 soft-reconfiguration inbound   ! convenient for inspecting/adjusting policy (uses memory)
 exit-address-family
```

<div class="zh" markdown="1">

```cfg
! BGP 稳定性生产基线
router bgp 65000
 bgp router-id 10.255.0.1
 bgp log-neighbor-changes
 bgp update-delay 300                  ! 等邻居与路由收敛
 bgp graceful-restart
 no bgp default ipv4-unicast           ! 显式启用，避免误通告
 !
 neighbor 10.0.0.1 remote-as 65000
 neighbor 10.0.0.1 update-source Loopback0
 neighbor 10.0.0.1 fall-over bfd       ! 快速检测
 neighbor 10.0.0.1 maximum-prefix 2000 90 warning-only
 !
 address-family ipv4 unicast
  neighbor 10.0.0.1 activate
  neighbor 10.0.0.1 soft-reconfiguration inbound   ! 便于查看/调整策略（占内存）
 exit-address-family
```

</div>

> ⚠️ **`soft-reconfiguration inbound` has a cost**: it keeps a second copy of the **unfiltered original routes** in memory, which can consume several GB with millions of prefixes. For large tables, use **route refresh** instead (`clear ip bgp <neighbor> soft in` does not need `soft-reconfig` when the neighbor supports the route refresh capability).

<div class="zh" markdown="1">

> ⚠️ **`soft-reconfiguration inbound` 是有代价的**：它会把**未经过滤的原始路由**也存一份在内存里，百万级前缀时可能占用数 GB。大表场景应改用 **Route Refresh**（`clear ip bgp <neighbor> soft in` 在支持 RR 能力的邻居上不需要 `soft-reconfig`）。

</div>

---

## Route Redistribution · 路由重分发

### Why Redistribution Is the Easiest Part of a Design to Lose Control Of · 为什么重分发是"设计里最容易失控的部分"

![What redistribution loses, and the tag pattern that prevents feedback](assets/fig/en08-22-redistribution.svg)

Redistribution "translates" the routes of one protocol into another. The trouble comes from three things:

<div class="zh" markdown="1">

重分发把一个协议的路由"翻译"给另一个协议。麻烦来自三件事：

</div>

| Problem | Description | Consequence |
|------|------|------|
| **Incomparable metrics** | OSPF cost ≠ EIGRP composite metric ≠ BGP AS_PATH | You can only invent a "seed metric", and path quality loses all meaning |
| **AD differences** | The same prefix has different priority depending on the source protocol | You may select the "technically optimal but design-wise wrong" path |
| **Bidirectional feedback** | A redistributes into B, and B redistributes back into A | **Feedback → loops or suboptimal routing** |

<div class="zh" markdown="1">

| 问题 | 说明 | 后果 |
|------|------|------|
| **度量不可比** | OSPF cost ≠ EIGRP 复合度量 ≠ BGP AS_PATH | 只能拍一个"种子度量"，路径优劣失去意义 |
| **AD 差异** | 同一前缀从两个协议学到的优先级不同 | 可能选到"技术最优但设计不对"的路径 |
| **双向反馈** | A 重分发进 B，B 又重分发回 A | **回馈（feedback）→ 环路或次优** |

</div>

**The practical result of metric translation**:

<div class="zh" markdown="1">

**度量翻译的实际结果**：

</div>

```
10.1.0.0/24 learned by OSPF (cost 20) → redistributed into EIGRP
  → EIGRP needs a "seed metric" (e.g. bandwidth 10000 delay 100)
  → every route coming from OSPF "looks equally good" inside EIGRP
  → EIGRP can no longer distinguish "good" from "bad" OSPF routes → path selection becomes meaningless
```

<div class="zh" markdown="1">

```
OSPF 学到的 10.1.0.0/24（cost 20）→ 重分发进 EIGRP
  → EIGRP 需要一个"种子度量"（如 bandwidth 10000 delay 100）
  → 所有从 OSPF 来的路由在 EIGRP 里"看起来一样好"
  → EIGRP 无法区分"优质的"和"劣质的" OSPF 路由 → 选路失去意义
```

</div>

### Single-Point and Dual-Point Redistribution · 单点重分发与双点重分发

| Model | Topology | Risk | Protection |
|------|------|------|---------|
| **Single-point redistribution** | Only one border router (ASBR) connects the two protocol domains | Low (no loops, one-way translation) | Basically no additional measures needed |
| **Dual-point redistribution** | **Two** border routers redistribute at the same time | **High** (route feedback, suboptimal routing, loops) | Route tags + distribute-list filtering + prefix filtering |

<div class="zh" markdown="1">

| 模型 | 拓扑 | 风险 | 保护手段 |
|------|------|------|---------|
| **单点重分发** | 只有一个边界路由器（ASBR）连接两个协议域 | 低（无环路，单向翻译） | 基本不需要额外手段 |
| **双点重分发** | **两台**边界路由器同时重分发 | **高**（路由回馈、次优、环路） | route tag + distribute-list 过滤 + 前缀过滤 |

</div>

**Why dual-point, dual-direction redistribution is dangerous** (illustrated):

<div class="zh" markdown="1">

**双点双向重分发为什么危险**（用图说明）：

</div>

```
        [protocol A domain]        [protocol B domain]
            │                          │
        R1 (ASBR)   ═══════════  R2 (ASBR)
            │                          │
        A's route X ──redistribute──→ B
                                B then redistributes X back ──→ A
                                        ↓
        R1 receives "X, originally from A, learned back from B"
        → AD comparison: B's AD (e.g. iBGP 200 / EIGRP external 170) vs A's AD (e.g. OSPF 110)
        → if B's AD is smaller → **R1 replaces its local A route with the route learned from B**
        → but that route's original information came from A itself → **the next hop may point at R2**
        → R1 sends traffic to R2, R2 sends it back → loop / suboptimal
```

<div class="zh" markdown="1">

```
        [协议 A 域]                [协议 B 域]
            │                          │
        R1（ASBR）  ═══════════  R2（ASBR）
            │                          │
        A 的路由 X ──重分发──→ B
                                B 再把 X ──重分发──→ A
                                        ↓
        R1 收到"从 B 学来的 A 自己通告的 X"
        → AD 比较：B 的 AD（如 iBGP 200 / EIGRP 外部 170）vs A 的 AD（如 OSPF 110）
        → 若 B 的 AD 更小 → **R1 用从 B 学来的路由替换本地 A 路由**
        → 但那条路由的原始信息来自 A 自己 → **下一跳可能指向 R2**
        → R1 把流量送给 R2，R2 又送回来 → 环路 / 次优
```

</div>

**The only correct answer is "tag it, then reject by tag"**:

<div class="zh" markdown="1">

**唯一的正解是"打标签 + 按标签拒收"**：

</div>

```cfg
! ── R1 (injects OSPF into BGP and tags it) ──
route-map RM-OSPF-TO-BGP permit 10
 match ip address prefix-list PL-INTERNAL
 set tag 100                      ! tag routes coming from OSPF
!
! ── R2 (when injecting BGP into OSPF, rejects routes tagged 100) ──
route-map RM-BGP-TO-OSPF deny 10
 match tag 100                    ! reject routes that originally came from OSPF
!
route-map RM-BGP-TO-OSPF permit 20
 set metric 100                   ! seed metric
 set metric-type type-2
 set tag 200
```

<div class="zh" markdown="1">

```cfg
! ── R1（把 OSPF 引入 BGP，并打 tag）──
route-map RM-OSPF-TO-BGP permit 10
 match ip address prefix-list PL-INTERNAL
 set tag 100                      ! 给来自 OSPF 的路由打标
!
! ── R2（从 BGP 引入 OSPF 时，拒绝带 tag 100 的路由）──
route-map RM-BGP-TO-OSPF deny 10
 match tag 100                    ! 拒绝"本来来自 OSPF 的路由"
!
route-map RM-BGP-TO-OSPF permit 20
 set metric 100                   ! 种子度量
 set metric-type type-2
 set tag 200
```

</div>

> ⚠️ **The propagation limits of tags**: **a tag is only propagated reliably within one protocol; across redistribution you must set and read it explicitly**. Set the tag when redistributing and match the tag in the opposite direction — this is the **only standard solution** for dual-point redistribution.

<div class="zh" markdown="1">

> ⚠️ **tag 的传播限制**：**tag 只在同一个协议内可靠传播，跨协议重分发时要显式设置/读取**。用 `set tag` 在重分发时打标，用 `match tag` 在反方向拒收——这是双点重分发的**唯一标准解法**。

</div>

**"Prefix filtering" is the second line of defense** (simpler and more reliable):

<div class="zh" markdown="1">

**"前缀过滤"是第二道防线**（更简单也更可靠）：

</div>

| Practice | Description |
|------|------|
| **Do not put production routes on the direct link between ASBRs** | Let the ASBRs talk to each other over a dedicated prefix only; routes can cross between domains only through redistribution |
| **State explicitly "which prefixes each domain owns"** | Redistribute with a prefix-list whitelist instead of `redistribute all` |
| **Never run `redistribute connected` without filtering** | It floods every connected network (including ISP interconnection addresses) into the IGP |

<div class="zh" markdown="1">

| 做法 | 说明 |
|------|------|
| **ASBR 之间的直连链路上不放业务路由** | 只让 ASBR 之间通过一个"独立前缀"互通，路由在两个域之间的传递只能经重分发 |
| **明确"每个域自己拥有哪些前缀"** | 用 prefix-list 白名单重分发，而不是 `redistribute all` |
| **禁止 `redistribute connected` 无过滤** | 会把所有直连（包括 ISP 互联地址）灌进 IGP |

</div>

```cfg
! Whitelist redistribution (recommended)
ip prefix-list PL-OWNED-OSPF seq 10 permit 10.10.0.0/16 le 24
ip prefix-list PL-OWNED-OSPF seq 20 permit 10.20.0.0/16 le 24
!
route-map RM-OSPF-INTO-BGP permit 10
 match ip address prefix-list PL-OWNED-OSPF
 set tag 100
!
router bgp 65000
 redistribute ospf 1 route-map RM-OSPF-INTO-BGP
```

<div class="zh" markdown="1">

```cfg
! 白名单式重分发（推荐）
ip prefix-list PL-OWNED-OSPF seq 10 permit 10.10.0.0/16 le 24
ip prefix-list PL-OWNED-OSPF seq 20 permit 10.20.0.0/16 le 24
!
route-map RM-OSPF-INTO-BGP permit 10
 match ip address prefix-list PL-OWNED-OSPF
 set tag 100
!
router bgp 65000
 redistribute ospf 1 route-map RM-OSPF-INTO-BGP
```

</div>

### Standard Practices for Common Redistribution Scenarios · 常见重分发场景的标准做法

| Scenario | Direction | Key configuration |
|------|------|---------|
| **OSPF → BGP** (advertise internal routes to the Internet/MPLS) | Out | prefix-list whitelist + `set tag` + `summary-only` (summarization) |
| **BGP → OSPF** (inject external/default routes into the IGP) | In | **Inject only the default route** (`default-information originate`) or a few summaries, never the full table |
| **EIGRP → OSPF** | Both | Seed metric + tag + summarization |
| **Static → OSPF** (branch default route) | In | `default-information originate` + `route-map` for conditions |
| **Connected → BGP** | Out | Only when loopbacks/server subnets must be advertised; the `network` command is more precise |

<div class="zh" markdown="1">

| 场景 | 方向 | 关键配置 |
|------|------|---------|
| **OSPF → BGP**（把内部路由通告给 Internet/MPLS） | 出 | prefix-list 白名单 + `set tag` + `summary-only`（汇总） |
| **BGP → OSPF**（把外部/默认路由引入 IGP） | 入 | **只引入默认路由**（`default-information originate`）或少量汇总，绝不引入全表 |
| **EIGRP → OSPF** | 双向 | 种子度量 + tag + 汇总 |
| **静态 → OSPF**（分支默认路由） | 入 | `default-information originate` + `route-map` 控制条件 |
| **Connected → BGP** | 出 | 只在需要通告 Loopback/服务器网段时；用 `network` 命令更精确 |

</div>

> ⚠️ **The single most dangerous item**: **redistributing the full BGP table into an IGP**. Pouring 950,000 Internet routes into OSPF instantly exhausts the memory and SPF capacity of every router in the area and takes the whole network down. **Never configure this.** If "the internal network must reach the Internet", inject only a **default route** or **your own public prefixes**.

<div class="zh" markdown="1">

> ⚠️ **最危险的一条**：**把 BGP 全表重分发进 IGP**。互联网 95 万条路由灌进 OSPF，会瞬间耗尽区域内所有路由器的内存和 SPF 计算能力，导致全网瘫痪。**永远不要这样配。** 如果需要"内网能访问互联网"，只引入**默认路由**或**你自己的公网前缀**。

</div>

---

## Enterprise Routing Design Recommendations · 企业路由设计建议

### Protocol Selection Matrix · 协议选择矩阵

![Protocol selection matrix by requirement](assets/fig/en08-23-protocol-matrix.svg)

| Network layer | Recommended protocol | Reason |
|---------|---------|------|
| **Campus access/distribution** | OSPF or EIGRP (single area/small area) | Small scale, simplicity required |
| **Campus core** | Multi-area OSPF / IS-IS (large scale) | Needs hierarchy and summarization |
| **WAN (hub-and-spoke)** | OSPF/EIGRP plus a distributed default route; branches as stub | Branches do not need network-wide detail |
| **WAN (multipath/multi-carrier)** | **BGP** | Path selection must follow policy |
| **Data center** | BGP (EVPN/VXLAN scenarios) / OSPF (traditional Layer 3) | Needs scale and policy |
| **Internet edge** | **BGP** | The only option |
| **Management network/OOB** | Static routes | Minimal, independent of production protocols |

<div class="zh" markdown="1">

| 网络层次 | 推荐协议 | 理由 |
|---------|---------|------|
| **园区接入/分布** | OSPF 或 EIGRP（单区域/小区域） | 规模小，需要简单 |
| **园区核心** | OSPF 多区域 / IS-IS（大规模） | 需要层次化与汇总 |
| **WAN（Hub-Spoke）** | OSPF/EIGRP + 默认路由下发；分支用 Stub | 分支不需要知道全网明细 |
| **WAN（多路径/多运营商）** | **BGP** | 需要按策略选路 |
| **数据中心** | BGP（EVPN/VXLAN 场景）/ OSPF（传统三层） | 需要大规模与策略 |
| **Internet 边界** | **BGP** | 唯一选择 |
| **管理网/OOB** | 静态路由 | 极简、不依赖业务协议 |

</div>

### Six Design Principles · 六条设计原则

| # | Principle | Description |
|---|------|------|
| 1 | **Minimize the number of protocols** | Each extra protocol grows the number of redistribution directions as n(n−1) |
| 2 | **Prefer one-way inter-domain redistribution** | One-way = no feedback = no loops; use two-way only when necessary and always with tags |
| 3 | **Branches use stub/default routing** | Branches do not need network-wide routes; a small table = fast convergence = fewer failures |
| 4 | **A summary must have null0** | Avoids a black hole after the details disappear |
| 5 | **The addressing plan must support summarization** | This is the only thing that pays off more the earlier you do it |
| 6 | **Control paths with metrics first, then policy, and PBR/tunnels last** | The later in the list, the harder to troubleshoot |

<div class="zh" markdown="1">

| # | 原则 | 说明 |
|---|------|------|
| 1 | **协议数量最小化** | 每增加一个协议，重分发方向数按 n(n−1) 增长 |
| 2 | **域间单向重分发优先** | 单向 = 无回馈 = 无环路；双向只在必要时用，且必须打 tag |
| 3 | **分支用 Stub/默认路由** | 分支不需要全网路由，路由表小 = 收敛快 = 故障少 |
| 4 | **汇总必须有 null0** | 避免明细消失后的黑洞 |
| 5 | **地址规划支撑汇总** | 这是唯一"做得越早越值钱"的事 |
| 6 | **路径控制优先用度量，其次策略，最后 PBR/隧道** | 越靠后越难排障 |

</div>

### Routing Design Acceptance Checklist · 路由设计的验收清单

![Eight-item acceptance checklist with the evidence required for each](assets/fig/en08-24-acceptance.svg)

| # | Check item | Verification method |
|---|--------|---------|
| 1 | Every area/domain boundary is clear and has a documented reason | Topology diagram + design document |
| 2 | Every prefix can be summarized by the layer above | Check whether inter-area routes in `show ip route` are only summaries |
| 3 | Summary routes are backed by null0 | Check `show ip route <summary>` for Null0 |
| 4 | Primary/backup paths in every VRF/domain match the design | Per-path traceroute cross-checked with NetFlow |
| 5 | Bidirectional redistribution has tags and prefix-lists | Check the direction and order of every route-map |
| 6 | BGP neighbors have maximum-prefix, authentication, and TTL security | `show ip bgp summary` + configuration review |
| 7 | A "fault injection test record" exists | Packet loss and convergence time after pulling links/shutting devices |
| 8 | Convergence time meets the per-stage targets | See the acceptance method in Chapter 7 (packet loss counted with long pings) |

<div class="zh" markdown="1">

| # | 检查项 | 验证方法 |
|---|--------|---------|
| 1 | 每个区域/域的边界清晰且有明确理由 | 拓扑图 + 设计文档 |
| 2 | 所有前缀都能被上层汇总 | `show ip route` 里区域间路由是否只有汇总 |
| 3 | 汇总路由有 null0 兜底 | `show ip route <summary>` 看是否为 Null0 |
| 4 | 每个 VRF/域的主备路径符合设计 | 逐个 traceroute + NetFlow 交叉验证 |
| 5 | 双向重分发有 tag 与 prefix-list | 检查 route-map 应用方向与顺序 |
| 6 | BGP 邻居有最大前缀、认证、TTL 安全 | `show ip bgp summary` + 配置核对 |
| 7 | 存在"故障注入测试记录" | 拔链路/关设备后的丢包数与收敛时间 |
| 8 | 收敛时间分段达标 | 见第 7 章的验收方法（长 ping 计丢包） |

</div>

---

## Case Studies · 实战案例

### Case 1: A 1G and a 10G Link Treated as Equal, So SPF Splits Traffic 50/50 · 案例一：1G 与 10G 链路等价，SPF 各分一半

**Background**: between a group headquarters and a data center there were two links: one 1G (an old link over the metro network) and one 10G (newly built, direct fiber). Both were Layer 3 interconnects running OSPF. After go-live, applications toward the data center were "normal during the day but extremely slow at month-end settlement".

<div class="zh" markdown="1">

**背景**：某集团总部到数据中心之间有两条链路：一条 1G（旧链路，走城域网），一条 10G（新建，直连光纤）。两条都是三层互联，跑 OSPF。上线后，数据中心方向的应用"白天正常，月末结算时极慢"。

</div>

**Troubleshooting**:

<div class="zh" markdown="1">

**排查**：

</div>

| Check | Result |
|------|------|
| `show ip route` | Both links appear as ECMP, `[110/2]` and `[110/2]`, **exactly identical** |
| `auto-cost reference-bandwidth` | **Not configured** (default 100 Mbps) |
| Interface bandwidth | Both 1G and 10G have cost **1** (100/1000 and 100/10000 both round to 1) |
| Link utilization | 1G link at **100%** (congestion loss), 10G link at **8%** |

<div class="zh" markdown="1">

| 检查 | 结果 |
|------|------|
| `show ip route` | 两条链路作为 ECMP，`[110/2]` 与 `[110/2]` **完全相同** |
| `auto-cost reference-bandwidth` | **未配置**（默认 100 Mbps） |
| 接口带宽 | 1G 与 10G 的 cost 都是 **1**（100/1000 与 100/10000 取整都是 1） |
| 链路利用率 | 1G 链路 **100%**（拥塞丢包），10G 链路 **8%** |

</div>

**Root cause**: with the default 100 Mbps reference bandwidth, **every interface of 100M or higher gets cost 1**. SPF considers the two links equal and load-shares across them equally → half the traffic is sent down the 1G link → congestion.

<div class="zh" markdown="1">

**根因**：默认参考带宽 100 Mbps 下，**所有 ≥100M 的接口 cost 都是 1**。SPF 认为两条链路等价，做等开销负载分担 → 一半流量被送到 1G 链路 → 拥塞。

</div>

**Why it is only slow "at month-end"**: hashing is per flow. Day-to-day traffic consists of many flows, so even though the distribution is uneven the 1G link copes; month-end settlement involves only a few large flows (backups, report exports), and hashing put one large flow onto the 1G link → that link saturates → every user of that flow experiences "extreme slowness".

<div class="zh" markdown="1">

**为什么"月末才慢"**：哈希是按流的。日常流量流数多，分布虽不均但 1G 尚能承载；月末结算只有少数几条大流（备份、报表导出），哈希把某条大流分到 1G 链路 → 那条链路直接打满 → 该流的所有用户感知"极慢"。

</div>

**Fix**:

<div class="zh" markdown="1">

**修复**：

</div>

```cfg
! Change the reference bandwidth consistently across the entire network (not just these two)
router ospf 1
 auto-cost reference-bandwidth 100000    ! 100G
```

<div class="zh" markdown="1">

```cfg
! 全网（不止这两台）统一修改参考带宽
router ospf 1
 auto-cost reference-bandwidth 100000    ! 100G
```

</div>

After the change: 1G → cost 100, 10G → cost 10. SPF uses only the 10G link and the 1G link becomes a backup (used only if the 10G fails).

<div class="zh" markdown="1">

修改后：1G → cost 100，10G → cost 10。SPF 只走 10G，1G 成为备份（当 10G 故障时才启用）。

</div>

**Three lessons (in increasing order of value)**:

<div class="zh" markdown="1">

**教训（三条，价值依次递增）**：

</div>

1. **`auto-cost reference-bandwidth` is a parameter that must be designed explicitly and configured consistently network-wide**, not something that "works fine by default".
2. **"Equal-cost load sharing" is an optimization only when the link speeds are equal**. Equal-cost sharing across unequal links wastes half the capacity of the fast link while saturating the slow one.
3. **Troubleshooting "slowness" must start with the routing table and interface utilization**, not with the application. **In this case the application side was completely innocent — the problem was the default cost value.**

<div class="zh" markdown="1">

1. **`auto-cost reference-bandwidth` 是一项必须显式设计并全网一致配置的参数**，不是"默认就行的东西"。
2. **"等开销负载分担"只在链路速率相等时才是优化**。速率不等时的等开销分担，是把快链路的一半容量浪费掉、同时把慢链路打爆。
3. **排查"慢"必须先看路由表和接口利用率**，而不是先看应用。**这个案例里应用侧完全无辜——问题在 cost 的默认值上。**

</div>

### Case 2: iBGP Routes "Learned but Not Installed" · 案例二：iBGP 路由"学得到但不装表"

**Background**: an enterprise used BGP as its core routing protocol. Two border routers (BR1, BR2) established eBGP with the Internet and iBGP full mesh with the core routers (CR1, CR2). After cutover, `show ip bgp` on CR1 showed all 900,000 routes with status `*>i` (valid, learned over iBGP), but **`show ip route` had none of them** — users had no Internet access at all.

<div class="zh" markdown="1">

**背景**：某企业用 BGP 作为核心路由协议。两台边界路由器（BR1、BR2）与 Internet 建立 eBGP，同时与核心路由器（CR1、CR2）建立 iBGP 全互连。割接后，`show ip bgp` 在 CR1 上能看到全部 90 万条路由且状态为 `*>i`（有效、iBGP 学来），但 **`show ip route` 里一条都没有** —— 用户完全上不了网。

</div>

**Troubleshooting**:

<div class="zh" markdown="1">

**排查**：

</div>

| Check | Result |
|------|------|
| `show ip bgp summary` | All neighbors Established |
| `show ip bgp` | Routes exist, best path marked correctly |
| `show ip bgp 8.8.8.8` | Next hop is **BR1's public interface address** (e.g. 203.0.113.2) |
| `show ip route 203.0.113.2` | **Does not exist!** |
| `show ip cef 8.8.8.8` | No entry |

<div class="zh" markdown="1">

| 检查 | 结果 |
|------|------|
| `show ip bgp summary` | 邻居全部 Established |
| `show ip bgp` | 路由存在，best 路径标记正确 |
| `show ip bgp 8.8.8.8` | 下一跳为 **BR1 的公网接口地址**（如 203.0.113.2） |
| `show ip route 203.0.113.2` | **不存在！** |
| `show ip cef 8.8.8.8` | 无条目 |

</div>

**Root cause**: the iBGP rule is that **a route learned over eBGP keeps its next hop when passed to iBGP neighbors**. So the route CR1 received has next hop `203.0.113.2`, BR1's public interface address — and `203.0.113.2` belongs to the **/30 interconnect between the border routers and the ISP**, a subnet that is **not advertised into the IGP** (correctly so: interconnect addresses should not go into the IGP).

<div class="zh" markdown="1">

**根因**：iBGP 的规则是 —— **从 eBGP 学到的路由，传给 iBGP 邻居时下一跳不变**。所以 CR1 收到的路由下一跳是 BR1 的公网接口地址 `203.0.113.2`，而 `203.0.113.2` 是**两台边界路由器与 ISP 互联的 /30 网段**，这个网段**没有在 IGP 里通告**（合理：互联地址不该进 IGP）。

</div>

The result: **next hop unreachable → recursive lookup fails → the BGP route is not installed in the FIB** (even though it appears as `*>` in the BGP table).

<div class="zh" markdown="1">

结果：**下一跳不可达 → 递归查找失败 → BGP 路由不装 FIB**（虽然 BGP 表里是 `*>`）。

</div>

**Why the routes "look fine" while not being installed**: `show ip bgp` shows `*>` (best + valid) because BGP itself considers the path valid, but **the final criterion for "valid" is that the next hop is resolvable (next-hop reachable)**. On many platforms `show ip bgp` still shows the path as best while it is absent from the RIB — this is the classic cause of "BGP has the route but ping fails".

<div class="zh" markdown="1">

**为什么不装表却"看起来路由是好的"**：`show ip bgp` 显示 `*>`（best + valid）是因为 BGP 自己认为路径有效，但**"有效"的最终判据是下一跳可解析（next-hop reachable）**。很多平台的 `show ip bgp` 仍显示为 best，只是 RIB 里没有它 —— 这就是"BGP 有路由但 ping 不通"的经典成因。

</div>

**Three fix options**:

<div class="zh" markdown="1">

**三种修复方案**：

</div>

| Option | Configuration | Cost |
|------|------|------|
| **① `next-hop-self`** (most common) | BR1/BR2 set `neighbor CR1 next-hop-self` toward iBGP neighbors | The border routers become the next hop → all traffic is forwarded through them (**they become part of the traffic path** and may be a bottleneck) |
| **② Advertise the interconnect addresses into the IGP** | Put `203.0.113.0/30` into OSPF | Violates the principle "interconnect addresses do not go into the IGP"; and every new uplink needs another IGP route |
| **③ Static routes pointing at the border routers** | `ip route 203.0.113.2 255.255.255.255 BR1` | Simple and reliable, but must be maintained one by one |

<div class="zh" markdown="1">

| 方案 | 配置 | 代价 |
|------|------|------|
| **① `next-hop-self`**（最常用） | BR1/BR2 对 iBGP 邻居设置 `neighbor CR1 next-hop-self` | 边界路由器成为下一跳 → 所有流量经边界路由器转发（**它们变成流量路径的一部分**，可能是瓶颈） |
| **② 在 IGP 里通告互联地址** | 把 `203.0.113.0/30` 放进 OSPF | 违反"互联地址不进 IGP"的原则；且每增加一条上行就要加一条 IGP 路由 |
| **③ 静态路由指向边界路由器** | `ip route 203.0.113.2 255.255.255.255 BR1` | 简单可靠，但需逐条维护 |

</div>

Option **①** was used in practice:

<div class="zh" markdown="1">

实际采用 **①**：

</div>

```cfg
router bgp 65000
 address-family ipv4 unicast
  ! BR1 / BR2 set next-hop-self toward the core iBGP neighbors
  neighbor 10.255.0.11 next-hop-self
  neighbor 10.255.0.12 next-hop-self
 exit-address-family
```

<div class="zh" markdown="1">

```cfg
router bgp 65000
 address-family ipv4 unicast
  ! BR1 / BR2 对核心的 iBGP 邻居设置下一跳自指
  neighbor 10.255.0.11 next-hop-self
  neighbor 10.255.0.12 next-hop-self
 exit-address-family
```

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **The iBGP next-hop rule is the most commonly stepped-on trap**: a route learned over eBGP keeps its next hop when passed to iBGP. Either use `next-hop-self` or guarantee that the next hop is reachable.
2. **`*>` in `show ip bgp` does not mean it can be forwarded**. You must check `show ip route` / `show ip cef`.
3. **The acceptance criterion for "BGP works" is an entry in `show ip cef <public address>`**, not a prefix in `show ip bgp`. This is the general check for "the control plane looks right but the data plane is broken".

<div class="zh" markdown="1">

1. **iBGP 的下一跳规则是最容易踩的坑**：eBGP 学来的路由传给 iBGP 时下一跳不变。要么 `next-hop-self`，要么保证下一跳可达。
2. **`show ip bgp` 有 `*>` 不等于能转发**。必须查 `show ip route` / `show ip cef`。
3. **验收 BGP"通了"的标准是 `show ip cef <公网地址>` 有条目**，而不是 `show ip bgp` 有前缀。这是"控制面看起来对、数据面不通"的通用检查法。

</div>

### Case 3: A Discontiguous Area 0 "Patched" with a Virtual Link for Three Years · 案例三：区域 0 不连续，用虚链路"糊"了三年

**Background**: an enterprise ran multi-area OSPF with Area 0 at headquarters. Three years earlier a new R&D center (Area 5) was built; its ABR connected both Area 5 and Area 3 (an old branch area), **but there was no path at all to Area 0** — because traffic between the R&D center and headquarters went through a "Layer 3 firewall NAT" and OSPF cannot cross NAT.

<div class="zh" markdown="1">

**背景**：某企业多区域 OSPF，初始设计时 Area 0 在总部。三年前新建了一个研发中心（Area 5），它的 ABR 同时连 Area 5 和 Area 3（老分支区域），**但没有任何一条路径连到 Area 0** —— 因为当时研发中心和总部之间走的是"三层防火墙 NAT"，OSPF 不能穿过 NAT。

</div>

The solution at the time: **configure an OSPF virtual link between ABR1 (the Area 0/3 boundary) and ABR2 (the Area 3/5 boundary)**, so that Area 5 was connected to Area 0 "logically".

<div class="zh" markdown="1">

当时的解决方案：**在 ABR1（Area 0/3 边界）和 ABR2（Area 3/5 边界）之间配置 OSPF virtual-link**，让 Area 5 "逻辑上"连到 Area 0。

</div>

**The failure three years later**: R&D users gradually reported that "some headquarters systems need a retry before they connect" and that "VoIP calls occasionally drop". The network raised no alarms; it was simply "unstable".

<div class="zh" markdown="1">

**三年后的故障**：研发中心的用户逐渐反馈"访问总部某些系统需要重试一次才能连上"、"VoIP 通话偶尔断"。网络"不报警"，只是"不稳"。

</div>

**Troubleshooting and root cause**:

<div class="zh" markdown="1">

**排查与根因**：

</div>

| Symptom | Root cause |
|------|------|
| Occasional retries | **The virtual link path detours through Area 3** → traffic crosses Area 3 twice → long path, many hops, possibly inconsistent MTU |
| Packet loss | One carrier link with MTU 1400 in the Area 3 path used by the virtual link → large packets are dropped |
| Slowness | ABR2 is the boundary of both Area 3 and Area 5, **carrying a double ABR role**; its CPU reached 70% during peak hours |
| No summarization | Routes through a virtual link **cannot be summarized like those of a normal ABR** (a virtual link essentially "extends" the ABR interface into Area 0, and LSA propagation is restricted) |

<div class="zh" markdown="1">

| 现象 | 根因 |
|------|------|
| 偶发重试 | **virtual-link 的路径绕经 Area 3** → 流量要两次穿过 Area 3 → 路径长、跳数多、MTU 可能不一致 |
| 丢包 | virtual-link 经过的 Area 3 链路上有个 MTU 1400 的运营商链路 → 大包被丢 |
| 收慢 | ABR2 同时是 Area 3 和 Area 5 的边界，**承担了双重 ABR 职责**，CPU 在高峰期达到 70% |
| 无法汇总 | 经 virtual-link 的路由**不能像正常 ABR 那样汇总**（虚链路本质是把 ABR 的接口"延伸"到 Area 0，LSA 传播受限） |

</div>

**Why nobody stopped it at the time**: the virtual link **worked**. After configuration, `show ip ospf virtual-links` showed UP and the business worked. Every acceptance metric (ping, access) passed.

<div class="zh" markdown="1">

**为什么当初没被制止**：virtual-link **能用**，配置完 `show ip ospf virtual-links` 显示 UP，业务通。所有验收指标（能 ping、能访问）都通过。

</div>

**The real fix (implemented a year later)**:

<div class="zh" markdown="1">

**真正的修复（一年后做了）**：

</div>

| Measure | Detail |
|------|------|
| **Remove the NAT obstacle** | Move the R&D center to an MPLS L3VPN or a dedicated circuit so OSPF can form direct adjacencies |
| **Connect Area 5 directly to Area 0** | Make ABR2 a real ABR (one interface in Area 0, one in Area 5) |
| **Make the R&D center Totally Stub** | It only needs a default route |
| **Remove the virtual link** | Along with all routing policies that depended on it |

<div class="zh" markdown="1">

| 措施 | 内容 |
|------|------|
| **打破 NAT 障碍** | 研发中心与总部之间改走 MPLS L3VPN 或专线，让 OSPF 能直接建立邻接 |
| **Area 5 直连 Area 0** | 让 ABR2 成为真正的 ABR（一个接口在 Area 0，一个在 Area 5） |
| **研发中心划为 Totally Stub** | 只需要默认路由 |
| **删除 virtual-link** | 连带删除所有依赖它的路由策略 |

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **A virtual link is an "emergency patch", not a "design option"**. It violates OSPF's hierarchical premise (Area 0 must be contiguous) and brings longer paths, broken summarization, and MTU traversal problems.
2. **"It works" is an extremely low standard**. Acceptance of a virtual link must additionally check path hop count, MTU, whether summarization takes effect, and the ABR's CPU.
3. **Any solution that "works around an architectural constraint" must be recorded in the documentation as technical debt**, together with "when it will be eliminated" (cf. Chapter 7: temporary solutions must have an expiry mechanism).

<div class="zh" markdown="1">

1. **virtual-link 是"应急补救"，不是"设计选项"**。它违反了 OSPF 的层次化前提（Area 0 必须连续），带来越长路径、无法正常汇总、MTU 穿透问题。
2. **"能通"是极低的标准**。virtual-link 的验收必须额外检查：路径跳数、MTU、汇总是否生效、ABR 的 CPU。
3. **凡是"绕过架构约束"的方案，都要在文档里标注为技术债**，并写明"何时消除"（对应第 7 章"临时方案必须有到期机制"）。

</div>

### Case 4: Dual-Point, Dual-Direction Redistribution and a 40-Minute Loop · 案例四：双点双向重分发，环路持续 40 分钟

**Background**: an enterprise acquired another company; the two networks ran OSPF (headquarters, inside the AS) and EIGRP (what the acquired company used, a legacy of history). To merge them, **bidirectional redistribution** was configured on **two** border routers.

<div class="zh" markdown="1">

**背景**：某企业收购了一家公司，两边的网络分别跑 OSPF（总部，AS 内部）和被收购方用的 EIGRP（历史遗留）。为了融合，在**两台**边界路由器上做了**双向重分发**。

</div>

**The incident**: one day the uplink of one border router (BR1) flapped and triggered route recomputation. Both the OSPF and EIGRP domains then **had loops at the same time**, traffic bounced between BR1 and BR2, the CPU on both devices hit 99%, some services were down for 40 minutes, and recovery only came after **manually shutting one interface on BR1**.

<div class="zh" markdown="1">

**事故**：某天一台边界路由器（BR1）的上联链路抖动，触发路由重算。随后 **OSPF 与 EIGRP 两个域同时出现环路**，流量在 BR1/BR2 之间来回，两台设备的 CPU 冲到 99%，部分业务中断 40 分钟，最后靠**手工 shutdown BR1 的一个接口**才恢复。

</div>

**Root cause analysis (reconstructed step by step)**:

<div class="zh" markdown="1">

**根因分析（逐步还原）**：

</div>

```
① BR1's uplink flaps → the detail of prefix P briefly disappears on the OSPF side
② BR1 redistributes "P learned from EIGRP" (which originally got there from OSPF) back into OSPF
   — because BR1's EIGRP table still "has P" (learned from BR2)
③ BR1 advertises P into OSPF with a next hop pointing toward BR2
④ BR2 learns P from OSPF and redistributes it back into EIGRP with a next hop pointing at BR1
⑤ Traffic circulates between BR1 ↔ BR2 and both links are saturated at once
⑥ Because these are "redistribution-generated routes", their AD differs from the original → the original routes cannot override them → the loop persists
```

<div class="zh" markdown="1">

```
① BR1 的上联抖动 → OSPF 侧某前缀 P 的明细短暂消失
② BR1 把"EIGRP 学来的 P"（原本是从 OSPF 重分发过去的）重新重分发回 OSPF
   —— 因为 BR1 的 EIGRP 表里确实"还有 P"（从 BR2 学来的）
③ BR1 把这个 P 通告进 OSPF，下一跳指向 BR2 方向
④ BR2 从 OSPF 学到 P，又重分发回 EIGRP，下一跳指向 BR1
⑤ 流量在 BR1 ↔ BR2 之间打转，两条链路同时打满
⑥ 因为是"重分发产生的路由"，AD 值与原始路由不同 → 无法被原有路由覆盖 → 环路持续
```

</div>

**The critical gaps (none of the four were in place)**:

<div class="zh" markdown="1">

**关键缺失（四个都没做）**：

</div>

| Gap | Consequence |
|------|------|
| **No route tags** | Cannot distinguish "locally originated" from "redistributed in from the other side" |
| **No prefix-list whitelist** | The `redistribute` scope was too wide and pulled in the feedback routes |
| **No AD planning** | The feedback routes happened to have a better AD than the original routes |
| **No "isolation" between the two border routers** | The two could exchange routes freely → a physical channel for the loop |

<div class="zh" markdown="1">

| 缺失 | 后果 |
|------|------|
| **没有 route tag** | 无法区分"本地产生的"和"从对端重分发进来的" |
| **没有 prefix-list 白名单** | `redistribute` 范围过宽，把回馈路由也带进来了 |
| **没有 AD 规划** | 回馈路由的 AD 恰好比原始路由更优 |
| **两条边界路由器之间的链路没有"隔离"** | 两者之间可以自由交换路由 → 提供了环路通道 |

</div>

**The correct design (rebuilt afterwards)**:

<div class="zh" markdown="1">

**正确的设计（事后重构）**：

</div>

```cfg
! ── BR1: tag OSPF → EIGRP with 300 ──
route-map RM-OSPF-TO-EIGRP permit 10
 match ip address prefix-list PL-OSPF-OWNED
 set tag 300
 set metric 10000 100 255 1 1500
!
! ── BR1: routes learned from EIGRP carrying tag 300 must not flow back into OSPF ──
route-map RM-EIGRP-TO-OSPF deny 10
 match tag 300
!
route-map RM-EIGRP-TO-OSPF permit 20
 match ip address prefix-list PL-EIGRP-OWNED
 set tag 400
 set metric 100
!
router eigrp 100
 redistribute ospf 1 route-map RM-OSPF-TO-EIGRP
!
router ospf 1
 redistribute eigrp 100 subnets route-map RM-EIGRP-TO-OSPF
```

<div class="zh" markdown="1">

```cfg
! ── BR1：OSPF → EIGRP 打 tag 300 ──
route-map RM-OSPF-TO-EIGRP permit 10
 match ip address prefix-list PL-OSPF-OWNED
 set tag 300
 set metric 10000 100 255 1 1500
!
! ── BR1：从 EIGRP 学来带 tag 300 的路由，不准回灌 OSPF ──
route-map RM-EIGRP-TO-OSPF deny 10
 match tag 300
!
route-map RM-EIGRP-TO-OSPF permit 20
 match ip address prefix-list PL-EIGRP-OWNED
 set tag 400
 set metric 100
!
router eigrp 100
 redistribute ospf 1 route-map RM-OSPF-TO-EIGRP
!
router ospf 1
 redistribute eigrp 100 subnets route-map RM-EIGRP-TO-OSPF
```

</div>

**A stronger line of defense**: make the link between BR1 and BR2 **carry no production routes at all**, only the /30 prefix that makes the two devices reachable to each other. The two redistribution paths are then separated topologically and the physical channel for the loop disappears.

<div class="zh" markdown="1">

**更强的一条防线：** 让 BR1 与 BR2 之间的链路**不参与任何业务路由交换**，只承载"两台设备互相可达"的 /30 前缀。这样两条重分发路径在拓扑上被隔开，环路的物理通道就消失了。

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **Dual-point, dual-direction redistribution requires three things at once**: route tags, a prefix-list whitelist, and explicit AD planning. Miss one and there is loop risk.
2. **"Normally fine" is the most dangerous property of dual-point, dual-direction redistribution**. It only blows up under a specific failure sequence (link flap + detail disappearing + feedback), and once it blows up it is nearly impossible to localize quickly.
3. **Eliminating redistribution architecturally is worth more than managing it technically**: the final solution in this case was to migrate the acquired company's EIGRP entirely to OSPF, **eliminating the redistribution**. The migration cost three months, but that is cheaper than keeping a dual-point, dual-direction structure that can loop at any time.

<div class="zh" markdown="1">

1. **双点双向重分发必须同时具备三件事**：tag 标记、prefix-list 白名单、明确的 AD 规划。缺一个就有环路风险。
2. **"平时正常"是双点双向重分发最危险的特性**。它只在特定故障序列下爆（链路抖动 + 明细消失 + 回馈），一旦爆了现场几乎无法快速定位。
3. **架构上消灭重分发比技术上管好重分发更值钱**：这个案例最终的解决方案是把被收购方的 EIGRP 整体迁移到 OSPF，**消灭了重分发**。迁移成本是 3 个月，但比保留一个随时可能环路的双点双向结构更省。

</div>

### Case 5: One `redistribute bgp` Took the Whole Network Down for 25 Minutes · 案例五：一条 `redistribute bgp` 让全网瘫痪 25 分钟

**Background**: an enterprise's new core was a BGP domain, and at the edge there was a small legacy OSPF area (a few old branches). To let the old branches reach the Internet, operations ran one "seemingly reasonable" command on the OSPF ASBR:

<div class="zh" markdown="1">

**背景**：某企业核心是新上的 BGP 域，边缘有一小块遗留的 OSPF 区域（几个老分支）。为了让老分支能访问互联网，运维在 OSPF 的 ASBR 上执行了一条"看起来合理"的命令：

</div>

```
router ospf 1
 redistribute bgp 65000 subnets
```

<div class="zh" markdown="1">

```
router ospf 1
 redistribute bgp 65000 subnets
```

</div>

**Within 3 minutes of execution**:

<div class="zh" markdown="1">

**执行后的 3 分钟内**：

</div>

| Symptom | Data |
|------|------|
| CPU on every OSPF router | Jumped from 20% to **98%** |
| OSPF neighbors | Mass **DOWN** (Hello processing could not keep up, so the Dead timer expired) |
| Memory | Memory **exhausted** on several access routers, with `%SYS-2-MALLOCFAIL` |
| Convergence | Stopped entirely; SPF recomputed over and over |

<div class="zh" markdown="1">

| 现象 | 数据 |
|------|------|
| 所有 OSPF 路由器 CPU | 从 20% 冲到 **98%** |
| OSPF 邻居 | 大量 **DOWN**（Hello 来不及处理导致 Dead 超时） |
| 内存 | 几台接入路由器内存 **耗尽**，出现 `%SYS-2-MALLOCFAIL` |
| 收敛 | 完全停止，SPF 反复重算 |

</div>

**Root cause**: the BGP table held **about 920,000** Internet routes. `redistribute bgp ... subnets` poured **all 920,000** of them into OSPF as Type 5 LSAs:

<div class="zh" markdown="1">

**根因**：BGP 表里有 **约 92 万条** Internet 路由。`redistribute bgp ... subnets` 把这 92 万条**全部**作为 Type 5 LSA 灌进 OSPF：

</div>

```
920,000 Type 5 LSAs → flooded across the entire OSPF area
  → the LSDB on every router grows to hundreds of MB
  → every SPF run must process 920,000 external prefixes
  → CPU 100%, memory exhausted, neighbors time out → neighbors rebuild → full flooding again → avalanche
```

<div class="zh" markdown="1">

```
92 万条 Type 5 LSA → 泛洪到整个 OSPF 区域
  → 每台路由器的 LSDB 膨胀到数百 MB
  → 每次 SPF 重算要处理 92 万个外部前缀
  → CPU 100%、内存耗尽、邻居超时 → 邻居重建 → 再次全量泛洪 → 雪崩
```

</div>

**Recovery**: the team first `shutdown` the ASBR's OSPF interface to stop the bleeding, then removed the redistribution command, then ran `clear ip ospf process` device by device. 25 minutes in total.

<div class="zh" markdown="1">

**恢复过程**：现场先 `shutdown` 该 ASBR 的 OSPF 接口止血，然后删除重分发命令，再逐台 `clear ip ospf process`。总计 25 分钟。

</div>

**The correct approach**:

<div class="zh" markdown="1">

**正确做法**：

</div>

```cfg
! Inject only the default route (the only correct approach in the vast majority of scenarios)
router ospf 1
 default-information originate route-map RM-HAS-DEFAULT
 
! Or inject only your own public prefixes (when internal hosts must reach specific public services)
route-map RM-BGP-TO-OSPF permit 10
 match ip address prefix-list PL-MY-PUBLIC
 set metric 100
 set tag 500
!
router ospf 1
 redistribute bgp 65000 subnets route-map RM-BGP-TO-OSPF
```

<div class="zh" markdown="1">

```cfg
! 只引入默认路由（绝大多数场景唯一正确的做法）
router ospf 1
 default-information originate route-map RM-HAS-DEFAULT
 
! 或只引入自己的公网前缀（需要内网访问特定公网服务时）
route-map RM-BGP-TO-OSPF permit 10
 match ip address prefix-list PL-MY-PUBLIC
 set metric 100
 set tag 500
!
router ospf 1
 redistribute bgp 65000 subnets route-map RM-BGP-TO-OSPF
```

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **The IGP carries "reachability"; BGP carries "policy and scale"**. Pouring a BGP table into an IGP violates the division of labor between protocols and the consequences are catastrophic.
2. **`redistribute` is a command with no boundaries**. By default it redistributes **every** route of that protocol. Every `redistribute` must be paired with a `route-map` or `prefix-list`.
3. **This class of command must go through change review**. It looks like one line but is a nuclear-grade operation that "changes the size of the routing table across the network". **The change ticket must state "how many routes are affected".**

<div class="zh" markdown="1">

1. **IGP 承载"可达性"，BGP 承载"策略与规模"**。把 BGP 表灌进 IGP 违反了协议分工，后果是灾难性的。
2. **`redistribute` 是一条"无边界"的命令**。它默认重分发该协议里的**全部**路由。任何 `redistribute` 都必须配 `route-map` 或 `prefix-list`。
3. **这类命令必须走变更评审**。它看起来只有一行，实际是"改变全网路由表规模"的核弹级操作。**变更单上应明确写"影响多少条路由"**。

</div>

### Case 6: AS_PATH Prepend Applied Five Times and the Traffic Did Not Change At All · 案例六：AS_PATH prepend 加了 5 次，流量一点没变

**Background**: an enterprise had dual egress and wanted "all outbound traffic through ISP-A, with ISP-B as backup only". Operations applied **5 AS_PATH prepends** to the local prefixes in the outbound direction toward ISP-B (`set as-path prepend 65000 65000 65000 65000 65000`), and yet **the inbound traffic through ISP-A did not decrease at all**.

<div class="zh" markdown="1">

**背景**：某企业双出口，希望"去程全部走 ISP-A，ISP-B 只做备份"。运维在 ISP-B 的出方向对本地前缀做了 **5 次 AS_PATH preppend**（`set as-path prepend 65000 65000 65000 65000 65000`），结果 **ISP-A 的入向流量一点没减少**。

</div>

**Troubleshooting**:

<div class="zh" markdown="1">

**排查**：

</div>

| Check | Result |
|------|------|
| `show ip bgp <prefix>` | The selected best path was **not** the ISP-A one |
| Attribute comparison | ISP-A path: **MED 100**; ISP-B path (5 prepends): **MED 1000** |
| So why was ISP-B still chosen? | Because the two paths came from **different neighbor ASes** (ISP-A AS 65100, ISP-B AS 65200) |

<div class="zh" markdown="1">

| 检查 | 结果 |
|------|------|
| `show ip bgp <prefix>` | 选中的最佳路径 **不是** ISP-A 那条 |
| 比较属性 | ISP-A 路径：**MED 100**；ISP-B 路径（prepend 5 次）：**MED 1000** |
| 但为什么还选 ISP-B？ | 因为这两条路径来自**不同的邻居 AS**（ISP-A AS 65100，ISP-B AS 65200） |

</div>

**Root cause (two things stacked)**:

<div class="zh" markdown="1">

**根因（两个叠加）**：

</div>

1. **MED is only compared within the same neighbor AS** — MEDs from AS 65100 and AS 65200 were never compared at all. So the MED step was a tie.
2. **The AS_PATH prepend was applied in the wrong direction**. Operations prepended in the **outbound direction toward ISP-B**, which affects the path length for "**others coming to you through ISP-B**" — in theory that should work. It did not, because:
   - The enterprise had also configured **`bgp bestpath as-path ignore`** (left over from some "optimization"), so **AS_PATH length comparison was skipped entirely**
   - The decision therefore jumped past MED → eBGP/iBGP → IGP metric → Router ID
   - In the end **Router ID/neighbor address** decided the path

<div class="zh" markdown="1">

1. **MED 只在同一邻居 AS 内比较** —— 来自 AS 65100 和 AS 65200 的 MED 根本没被比较。所以 MED 那一步是"平局"。
2. **AS_PATH prepend 打在了错误的方向**。运维在 **ISP-B 的出方向**做了 prepend，这影响的是"**别人经 ISP-B 来访问你**"的路径长度 —— 理论上应该有效。但实际无效，因为：
   - 该企业还配置了 **`bgp bestpath as-path ignore`**（某次"优化"留下的），**AS_PATH 长度比较被整体跳过**
   - 于是判据直接跳到 MED 之后 → eBGP/iBGP → IGP metric → Router ID
   - 最终由 **Router ID/邻居地址**决定了路径

</div>

**Why "changing attributes has no effect" is the hardest thing to troubleshoot**: `show ip bgp` shows attributes but not "why a criterion was skipped". You must walk the selection order item by item and check the `bgp bestpath` family of settings.

<div class="zh" markdown="1">

**为什么"改了属性没效果"最难查**：`show ip bgp` 只显示属性，不显示"为什么跳过某条判据"。必须逐条对照选路顺序，并检查 `bgp bestpath` 系列配置。

</div>

**The final fix**:

<div class="zh" markdown="1">

**最终修复**：

</div>

```cfg
! 1) Remove the dangerous bestpath switches
no bgp bestpath as-path ignore
no bgp bestpath compare-routerid

! 2) Control egress with Local Preference (the one thing you fully control)
route-map RM-FROM-ISP-A permit 10
 set local-preference 200
route-map RM-FROM-ISP-B permit 10
 set local-preference 100

! 3) Control ingress with prepend, but only on the link you do not want used, and with a sensible count (2-3)
route-map RM-TO-ISP-B permit 10
 match ip address prefix-list PL-LOCAL
 set as-path prepend 65000 65000

! 4) Verify: you must confirm that both the best path and the FIB changed
!    show ip bgp <prefix> | show ip cef <prefix>
```

<div class="zh" markdown="1">

```cfg
! 1) 撤销危险的 bestpath 开关
no bgp bestpath as-path ignore
no bgp bestpath compare-routerid

! 2) 用 Local Preference 控制出向（这是"自己能完全决定"的那一条）
route-map RM-FROM-ISP-A permit 10
 set local-preference 200
route-map RM-FROM-ISP-B permit 10
 set local-preference 100

! 3) 入向用 prepend，但只在"不希望被使用"的链路上做，且次数要合理（2-3 次）
route-map RM-TO-ISP-B permit 10
 match ip address prefix-list PL-LOCAL
 set as-path prepend 65000 65000

! 4) 验证：必须确认 best 路径和 FIB 都变了
!    show ip bgp <prefix> | show ip cef <prefix>
```

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **Confirm the traffic direction before choosing the tool**: egress uses LP/Weight (fully controllable), ingress uses MED/prepend (partially controllable). **Use the wrong tool and no amount of tuning helps.**
2. **"Optimization switches" such as `no bgp bestpath ...` are time bombs**. They make path selection deviate from the standard **without generating any alarm**. Such configuration must be part of baseline review and may not be enabled without review.
3. **The verification loop closes on "the FIB changed", not on "the configuration took effect"**. `show ip bgp` for attributes, `show ip bgp <prefix>` for the best path, `show ip cef` for actual forwarding — all three must agree before the change counts as successful.

<div class="zh" markdown="1">

1. **先确认"流量方向"再选工具**：出向用 LP/Weight（完全可控），入向用 MED/prepend（部分可控）。**用错工具，怎么调都没用。**
2. **`no bgp bestpath ...` 这类"优化开关"是定时炸弹**。它们让选路行为偏离标准，且**不产生任何告警**。这类配置必须纳入基线审查，禁止无评审开启。
3. **验证闭环是"FIB 变了"而不是"配置生效了"**。`show ip bgp` 看属性、`show ip bgp <prefix>` 看 best、`show ip cef` 看实际转发 —— 三者必须一致才算改成功。

</div>

### Case 7: Duplicate RR cluster-id and a Quarter of the Routes Disappeared · 案例七：RR 的 cluster-id 重复，四分之一路由消失

**Background**: two RRs (RR1, RR2) were deployed for redundancy in a data center, each serving 40 border routers as clients. A configuration template was used for the deployment, and the template's `bgp cluster-id 1.1.1.1` was copied verbatim onto both RRs.

<div class="zh" markdown="1">

**背景**：某数据中心两台 RR（RR1、RR2）冗余部署，各带 40 台边界路由器作为 client。部署时用了配置模板，模板里 `bgp cluster-id 1.1.1.1` 被原样复制到两台 RR 上。

</div>

**Symptom**: after go-live **about 25% of prefixes were incomplete**. Some destinations were unreachable from some border routers but reachable from others; `show ip bgp` on some devices was completely missing certain prefixes.

<div class="zh" markdown="1">

**现象**：上线后**约 25% 的前缀不完整**。某些目的地址从部分边界路由器上不可达，但从另一些可达；`show ip bgp` 在部分设备上完全没有某些前缀。

</div>

**Troubleshooting**:

<div class="zh" markdown="1">

**排查**：

</div>

| Check | Result |
|------|------|
| `bgp cluster-id` on RR1 and RR2 | **Both 1.1.1.1** (identical cluster-id) |
| `show ip bgp <a missing prefix>` | Visible on the RRs, but never received by the clients |
| BGP update logging | When an RR received a route whose own Cluster List already contained `1.1.1.1`, it considered it a loop → **discarded** |

<div class="zh" markdown="1">

| 检查 | 结果 |
|------|------|
| RR1、RR2 的 `bgp cluster-id` | **都是 1.1.1.1**（相同的 cluster-id） |
| `show ip bgp <某缺失前缀>` | 在 RR 上可见，但 client 上收不到 |
| BGP 更新日志 | RR 收到自带 Cluster List 中包含 `1.1.1.1` 的路由时，判定为环路 → **丢弃** |

</div>

**Root cause**: BGP's **loop-prevention mechanism (Cluster List)** was working, but it was doing "friendly fire":

<div class="zh" markdown="1">

**根因**：BGP 的**防环机制（Cluster List）** 起作用了，但起的是"误伤"：

</div>

```
① Client-A sends a route to RR1
② RR1 reflects it to RR2 (the RRs are also iBGP peers) → "1.1.1.1" is added to the route's Cluster List
③ RR2 reflects it to its clients → the route carries Cluster List "1.1.1.1"
④ When RR2 itself sends to RR1, RR1 sees "1.1.1.1" (its own ID) in the Cluster List
   → concludes "this route looped back to me" → discards it
⑤ The result: RR1's clients only learn routes that came directly from RR1,
   and the prefixes RR2 learned (from RR2's clients) cannot be passed down through RR1
```

<div class="zh" markdown="1">

```
① Client-A 把路由发给 RR1
② RR1 反射给 RR2（RR 之间也是 iBGP 关系）→ 路由的 Cluster List 里加上 "1.1.1.1"
③ RR2 反射给它的 client → 路由带 Cluster List "1.1.1.1"
④ 而 RR2 自己发给 RR1 时，RR1 看到 Cluster List 里有 "1.1.1.1"（自己的 ID）
   → 判定"这条路由绕回我自己了"→ 丢弃
⑤ 结果是：RR1 的 client 只能学到"直接从 RR1 来的"路由，
   RR2 学到的那些前缀（来自 RR2 的 client）无法通过 RR1 传下去
```

</div>

**Why "about 25%"**: it depends on how the clients are distributed and where the routes originate. Half the clients hang off RR1 and half off RR2, plus the paths the RRs reflect to each other, giving roughly 25% missing.

<div class="zh" markdown="1">

**为什么是"约 25%"**：取决于 client 的归属分布与路由来源分布。有一半 client 挂在 RR1、一半挂 RR2，加上 RR 之间互相反射的路径，呈现约 25% 的缺失。

</div>

**Fix**:

<div class="zh" markdown="1">

**修复**：

</div>

```cfg
! Each RR uses a unique cluster-id
! RR1
router bgp 65000
 bgp cluster-id 1.1.1.1
! RR2
router bgp 65000
 bgp cluster-id 2.2.2.2
```

<div class="zh" markdown="1">

```cfg
! 每台 RR 使用唯一 cluster-id
! RR1
router bgp 65000
 bgp cluster-id 1.1.1.1
! RR2
router bgp 65000
 bgp cluster-id 2.2.2.2
```

</div>

After the change all prefixes were complete again.

<div class="zh" markdown="1">

改完后所有前缀恢复完整。

</div>

**Lessons**:

<div class="zh" markdown="1">

**教训**：

</div>

1. **`cluster-id` must be unique** (normally you can use the RR's Router ID, but **it must be set explicitly to each RR's own value**). Hard-coding a number in a template is a recipe for an outage.
2. **Know the four loop-prevention mechanisms of BGP**: AS_PATH (across ASes), Cluster List (inside an RR cluster), Originator ID (RR scenarios), and next-hop reachability. When they "take effect" the visible symptom is "routes disappearing" — **that is designed behavior, not a bug** — and you must be able to recognize it while troubleshooting.
3. **Templated configuration must include "variable checks"**: any parameter that should differ per device (Router ID, cluster-id, NET, interface addresses) must be a variable in the template, and uniqueness must be validated automatically after deployment.

<div class="zh" markdown="1">

1. **`cluster-id` 必须唯一**（通常用 RR 的 Router ID 即可，但**必须显式指定为各自的值**）。模板里写死一个数字是事故根源。
2. **BGP 的四种防环机制要分清**：AS_PATH（跨 AS）、Cluster List（RR 集群内）、Originator ID（RR 场景）、下一跳可达性。它们"生效"时表现为"路由消失"，**这是设计行为而不是 Bug** —— 排障时要能识别。
3. **模板化配置必须有"变量检查"**：凡是"每台设备应不同"的参数（Router ID、cluster-id、NET、接口地址），模板化时必须做成变量，且部署后自动校验唯一性。

</div>

---

## Common Layer 3 Design Trade-offs · 三层设计的常见取舍

| Trade-off | Option A | Option B | How to decide |
|------|--------|--------|---------|
| **IGP vs BGP as the core** | IGP (simple, fast convergence) | BGP (strong policy, high scale) | Do you need policy? Will scale exceed 500 devices? Does the team know BGP? |
| **Single area vs multi-area** | Single area (simple) | Multi-area (summarizable, smaller failure domain) | Does the flooding domain exceed 100–200 devices? Do you need summarization? |
| **Stub vs NSSA** | Stub (smallest routing table) | NSSA (allows local redistribution) | Does the site have a local egress? |
| **Summary granularity** | Coarse (small table, poor visibility) | Fine (good visibility, large table) | Do you need visibility of detailed failures? |
| **Equal cost vs primary/backup** | ECMP (high utilization) | Primary/backup (deterministic) | Are the link speeds equal? Does the business require determinism? |
| **Fast convergence vs stability** | BFD + fast timers | Defaults + throttling | Does the business really notice one second? What is the cost of a flap-driven false failover? |
| **Redistribution vs migration** | Dual-point, dual-direction redistribution (keeps heterogeneity) | Unify on one protocol (migration cost) | **In the long run unifying is almost always cheaper** (case 4) |
| **RR vs confederation** | RR (simple, mature) | Confederation (hierarchical but complex) | Almost always choose RR |
| **Static vs dynamic** | Static default route (simple, controllable) | Dynamic (self-adapting) | Can the branch accept "default route + summary"? |

<div class="zh" markdown="1">

| 取舍 | 选项 A | 选项 B | 判断依据 |
|------|--------|--------|---------|
| **IGP vs BGP 承载核心** | IGP（简单，收敛快） | BGP（策略强，规模大） | 需要策略吗？规模会超过 500 台吗？团队懂 BGP 吗？ |
| **单区域 vs 多区域** | 单区域（简单） | 多区域（可汇总、故障域小） | 泛洪域是否超过 100–200 台？需要汇总吗？ |
| **Stub vs NSSA** | Stub（路由表最小） | NSSA（允许本地重分发） | 站点有本地出口吗？ |
| **汇总粒度** | 粗（表小，可见性差） | 细（可见性好，表大） | 需要明细故障的可见性吗？ |
| **等开销 vs 主备** | ECMP（利用率高） | 主备（确定性好） | 链路速率是否相等？业务是否要求确定性？ |
| **快收敛 vs 稳定性** | BFD + 快计时器 | 默认 + 节流 | 业务真的感知 1 秒吗？抖动误切换的代价多大？ |
| **重分发 vs 迁移** | 双点双向重分发（保留异构） | 统一到一个协议（迁移成本高） | **长期看几乎总是统一更省**（案例四） |
| **RR vs 联盟** | RR（简单、成熟） | 联盟（分层但复杂） | 几乎总选 RR |
| **静态 vs 动态** | 静态默认路由（简单可控） | 动态（自适应） | 分支能否接受"默认路由 + 汇总" |

</div>

---

## Design Flaws · 设计缺陷

| Flaw | Symptom | Consequence | Avoidance |
|------|------|------|------|
| **Default `auto-cost reference-bandwidth`** | Every interface ≥100M has cost=1 | 1G and 10G look equal, ECMP splits 50/50 (case 1) | Change consistently network-wide to 10G/100G and put it in the baseline |
| **Reference bandwidth changed on only half the devices** | Different costs on the two ends of the same link | Asymmetric paths, potential loops | Network-wide change with consistency validation |
| **No `next-hop-self` in iBGP** | `show ip bgp` has a best path, the RIB has no entry (case 2) | Complete outage, "control plane fine, data plane broken" | Configure next-hop-self on border routers, or guarantee next-hop reachability |
| **Solving a discontiguous Area 0 with virtual links** | Works, but detoured paths, MTU traversal, no summarization (case 3) | Long-term hidden degradation, very hard to troubleshoot | Fix the architecture (dedicated circuit/VPN/direct Area 0); virtual links are emergency-only |
| **Dual-point, dual-direction redistribution without tags** | Fine normally, loops on failure (case 4) | Network-wide loops, CPU saturated, hard to recover | Tags + prefix-list whitelist + AD planning, all three |
| **Redistributing a BGP table into an IGP** | CPU 100%, memory exhausted, all neighbors down (case 5) | Whole network down | Inject only the default route or your own public prefixes |
| **`redistribute` without a route-map** | The scope has no boundary | Routes that should not be propagated are propagated | Every redistribute needs a route-map/prefix-list |
| **Using the control tool in the wrong direction** | MED for egress / LP for ingress | No tuning has any effect (case 6) | Egress LP/Weight, ingress MED/prepend |
| **Enabling switches such as `no bgp bestpath as-path ignore`** | Path selection deviates from the standard with no alarm | "Changing attributes has no effect", nobody can explain it | Prohibit enabling without review; include in baseline review |
| **Multiple RRs sharing the same cluster-id** | Some prefixes are silently missing (case 7) | Incomplete routing, random failures | Unique cluster-id plus automatic post-deployment validation |
| **Single RR / clients connected to only one RR** | An RR failure breaks routing | Large-scale route loss in that cluster | RRs in pairs, clients connect to both |
| **Summaries without null0** | The summary route stays when the details disappear | Black hole during failures ("the summary address pings, the business does not work") | Explicitly confirm the Null0 entry |
| **Non-contiguous summarized addresses** | The summary covers unused addresses | The summary itself creates a black hole | Verify address contiguity before summarizing |
| **Redistribution inside a stub area** | `redistribute` is silently ignored | The backup egress fails (earlier case) | Use NSSA; check the actual routing table during acceptance |
| **Shrinking Hello without SPF throttling** | Flap → recompute → flap | CPU saturated by SPF | BFD + throttling (throttle + arrival) |
| **EIGRP without stub or summarization** | Queries spread across the whole network | SIA, slow convergence, high CPU | `eigrp stub` + summarization |
| **Changing EIGRP K values** | Neighbors fail to come up | All neighbors drop network-wide | Do not change K values; control paths with policy |
| **`soft-reconfig inbound` everywhere in BGP** | Memory doubles | Memory exhaustion on large tables | Use route refresh instead |
| **No `update-delay`** | Forwarding with an incomplete table at startup | Brief large-scale black hole after restart | Configure 300–600 s in large networks |

<div class="zh" markdown="1">

| 缺陷 | 表现 | 后果 | 规避 |
|------|------|------|------|
| **`auto-cost reference-bandwidth` 用默认值** | 所有 ≥100M 接口 cost=1 | 1G 与 10G 等价，ECMP 各分一半（案例一） | 全网统一改为 10G/100G，写进基线 |
| **参考带宽只改一半设备** | 同一链路两端 cost 不同 | 不对称路径、潜在环路 | 全网变更，纳入一致性校验 |
| **iBGP 未配 `next-hop-self`** | `show ip bgp` 有 best，RIB 无条目（案例二） | 完全不通，"控制面正常数据面不通" | 边界路由器配 next-hop-self，或保证下一跳可达 |
| **靠 virtual-link 解决 Area 0 不连续** | 能通但路径绕、MTU 穿透、无法汇总（案例三） | 长期隐性劣化，排障极难 | 改架构（专线/VPN/直连 Area 0），virtual-link 只作应急 |
| **双点双向重分发无 tag** | 平时正常，故障时环路（案例四） | 全网环路，CPU 打满，恢复困难 | tag + prefix-list 白名单 + AD 规划，三者齐备 |
| **把 BGP 表重分发进 IGP** | CPU 100%、内存耗尽、邻居全断（案例五） | 全网瘫痪 | 只引入默认路由或自有公网前缀 |
| **`redistribute` 不配 route-map** | 范围无边界 | 把不该传的路由传出去 | 所有 redistribute 必须配 route-map/prefix-list |
| **用错方向的控制工具** | 出向用 MED / 入向用 LP | 怎么调都没效果（案例六） | 出向 LP/Weight，入向 MED/prepend |
| **开启 `no bgp bestpath as-path ignore` 等开关** | 选路行为偏离标准且无告警 | "改属性没效果"，无人能解释 | 禁止无评审开启，纳入基线审查 |
| **多台 RR 用相同 cluster-id** | 部分前缀静默缺失（案例七） | 路由不完整，故障随机出现 | cluster-id 唯一 + 部署后自动校验 |
| **RR 单点 / 客户端只连一个 RR** | RR 故障即路由中断 | 该集群路由大面积丢失 | 成对 RR，客户端连两个 |
| **汇总不配 null0** | 明细消失时汇总路由仍在 | 故障期间黑洞（"汇总地址通，业务不通"） | 显式确认 Null0 条目 |
| **汇总地址不连续** | 汇总包含了未使用的地址 | 汇总本身产生黑洞 | 汇总前验证地址连续性 |
| **Stub 区域配了重分发** | `redistribute` 被静默忽略 | 备份出口失效（前方案例） | 用 NSSA；验收查实际路由表 |
| **Hello 调小但不配 SPF 节流** | 抖动 → 重算 → 抖动 | CPU 被 SPF 吃满 | BFD + 节流（throttle + arrival） |
| **EIGRP 不开 Stub / 不汇总** | Query 扩散全网 | SIA、收敛慢、CPU 高 | `eigrp stub` + 汇总 |
| **EIGRP 改 K 值** | 邻居起不来 | 全网邻居中断 | 不改 K 值；用策略控制路径 |
| **BGP `soft-reconfig inbound` 全网开** | 内存翻倍 | 大表场景内存耗尽 | 用 Route Refresh 替代 |
| **`update-delay` 不配** | 启动时用不完整的表转发 | 启动后短暂大规模黑洞 | 大网配 300–600 秒 |

</div>

---

## Lessons from Practice · 实战经验总结

| Lesson | Description |
|------|------|
| **Reference bandwidth is a network-wide consistency parameter** | `auto-cost reference-bandwidth` must be **identical network-wide**; changing only half is worse than not changing it (asymmetric paths) |
| **Ask the business about tolerance before targeting convergence** | If the business cannot perceive one second, do not add BFD plus aggressive timers for 200 ms; the cost of flap-driven false failover is usually higher |
| **A summary must be paired with Null0** | The lifetime of the summary and of the details must be decoupled, otherwise the summary becomes a black hole when the details disappear |
| **RRs in pairs, unique cluster-ids, clients dual-homed** | These three are the minimum configuration for iBGP scalability; miss any one and the symptom is "routes are occasionally incomplete" |
| **The redistribution triad: tag + route-map + AD planning** | Miss any one and failures inevitably produce loops or suboptimal routing, **and it is invisible in normal operation** |
| **Control tools must point in the right direction** | Egress uses LP/Weight (decided locally), ingress uses MED/prepend (decided by the peer). Get the direction wrong and no tuning helps |
| **In the long run, unifying protocols is cheaper than maintaining two** | Dual-point, dual-direction redistribution is a "temporary bridge" that should be removed once migration is done; organizations that treat it as a long-term solution all pay a larger troubleshooting bill within three years |
| **Templated configuration must include variable validation** | Router ID, cluster-id, NET, and interface addresses "differ per device"; templating must validate uniqueness automatically, otherwise duplicate IDs silently drop routes |
| **When troubleshooting, first check whether the control and data planes agree** | "`show ip bgp` has a best path but the RIB has no entry" almost always points at next-hop reachability (`next-hop-self`) |

<div class="zh" markdown="1">

| 经验 | 说明 |
|------|------|
| **参考带宽是全网一致性参数** | `auto-cost reference-bandwidth` 必须**全网同值**，只改一半比不改更糟（不对称路径） |
| **收敛目标先问业务容忍度** | 业务感知不到 1 秒，就别为 200ms 上 BFD + 激进计时器；抖动导致的误切换代价往往更大 |
| **汇总必配 Null0** | 汇总路由与明细的存亡必须解耦，否则明细消失时汇总变成黑洞 |
| **RR 成对、cluster-id 唯一、客户端双连** | 这三条是 iBGP 可扩展性的最低配置，任何一条缺失都会表现为"路由偶尔不全" |
| **重分发三件套：tag + route-map + AD 规划** | 缺任何一个，故障时必然出现环路或次优，且**平时看不出来** |
| **控制工具方向不能错** | 出向用 LP/Weight（本地决定），入向用 MED/prepend（对端决定）。方向错了怎么调都没效果 |
| **长期看，统一协议比维护双协议便宜** | 双点双向重分发是"临时桥"，迁移完成就该拆；把它当长期方案的组织，都在三年内付出更大的排障成本 |
| **模板化配置必须带变量校验** | Router ID、cluster-id、NET、接口地址"每台不同"，模板化时要自动校验唯一性，否则重复 ID 会静默丢路由 |
| **排障先看控制面与数据面是否一致** | `show ip bgp` 有 best 而 RIB 无条目，问题几乎总在下一跳可达性（next-hop-self） |

</div>

---

## Key Terms · 本章关键术语

| Term | Meaning | One-line memory hook |
|------|---------|-----------|
| **RIB** | Routing information base | The candidate pool of all protocols |
| **FIB** | Forwarding information base | The table actually used for forwarding |
| **AD (administrative distance)** | Priority between different sources | Compare across protocols with AD; eBGP(20) beats OSPF(110), iBGP(200) is worst |
| **Metric** | Path quality within one protocol | **Not comparable across protocols** — the fundamental difficulty of redistribution |
| **Longest match** | The longest mask wins | A specific route always beats a summary |
| **Recursive lookup** | Resolve the next hop layer by layer | An unreachable BGP next hop means the route is not installed |
| **LSDB** | Link-state database | Must be identical inside an area |
| **SPF / Dijkstra** | Shortest path first algorithm | Build the tree rooted at yourself |
| **Area 0 / backbone** | The backbone area | Must be contiguous; if not, use a virtual link (emergency only) |
| **ABR** | Area border router | The producer of summaries and Type 3 LSAs |
| **ASBR** | AS boundary router | The producer of redistribution and Type 5 LSAs |
| **LSA Type 1–7** | OSPF link-state advertisements | 1/2 topology, 3/4 inter-area, 5/7 external |
| **Stub / Totally Stub** | Stub area | No ASBR allowed; smallest routing table |
| **NSSA** | Not-so-stubby area | Allows local redistribution (used when the site has a local egress) |
| **Virtual link** | Virtual link | An emergency measure, not a design option |
| **P2P / P2MP / Broadcast** | OSPF network types | The network type is a design variable, not an auto-detected result |
| **SPF throttle** | SPF throttling | Fast detection must be paired with suppression |
| **`auto-cost reference-bandwidth`** | Reference bandwidth | Default 100M → every interface above 1G gets cost=1 |
| **Area range / summary-address** | OSPF summarization | ABRs summarize intra-area routes; ASBRs summarize external routes |
| **Null0** | Discard route | **A summary must be paired with null0** |
| **IS-IS** | Intermediate system to intermediate system | Runs on Layer 2, best TLV extensibility |
| **Level 1 / Level 2** | IS-IS hierarchy | L2 = backbone, contiguous by design |
| **NET / System ID** | The IS-IS router identity | Must be unique network-wide |
| **DIS** | Designated intermediate system | No backup, preemptive (unlike DR which has a BDR) |
| **`metric-style wide`** | IS-IS wide metric | Mandatory, otherwise high-speed links cannot be distinguished |
| **Overload bit** | IS-IS overload bit | Used in maintenance windows to avoid attracting traffic early |
| **Multi-topology (MT)** | IS-IS multi-topology | IPv4/IPv6 can take different paths |
| **EIGRP / DUAL** | Diffusing update algorithm | The "hybrid" of distance vector |
| **FD / RD (AD)** | Feasible distance / reported distance | RD < FD is required to become a feasible successor |
| **Successor / feasible successor** | Successor / feasible successor | With an FS, repair is local and convergence is fastest |
| **Query / SIA** | Query / stuck in active | Query diffusion is the main scale risk of EIGRP |
| **EIGRP stub** | Stub routing | Cuts off the query scope |
| **BGP** | Border Gateway Protocol | Path vector, runs over TCP 179 |
| **eBGP / iBGP** | External / internal BGP | eBGP is directly connected; iBGP needs a full mesh or RRs |
| **iBGP full-mesh rule** | iBGP routes are not passed to other iBGP neighbors | N(N−1)/2 sessions |
| **Next-hop-self** | Self-referencing next hop | Mandatory in iBGP (or guarantee next-hop reachability) |
| **Weight** | Weight | Cisco proprietary, local only, higher wins |
| **Local Preference** | Local preference | AS-wide, **controls egress** |
| **AS_PATH** | AS path | Shorter wins; prepending lengthens it |
| **Origin** | Origin type | IGP < EGP < Incomplete |
| **MED** | Multi-exit discriminator | Lower wins; **compared only within the same neighbor AS** |
| **Route reflector (RR)** | Route reflector | Breaks the full-mesh requirement |
| **Cluster ID / cluster list** | Cluster ID / cluster list | Loop prevention; **must be unique across multiple RRs** |
| **Originator ID** | Originator ID | The second loop-prevention mechanism in RR scenarios |
| **Confederation** | Confederation | Splits a large AS into sub-ASes; complex, usually not chosen |
| **Peer group / template** | Peer group / template | Configuration shrinks from N entries to one |
| **`update-delay`** | Update delay | Waits for neighbor convergence at startup, avoiding forwarding with an incomplete table |
| **Route dampening** | Route dampening | **Use with care**, easily causes long black holes |
| **Redistribution** | Redistribution | Cross-protocol translation; incomparable metrics are the fundamental difficulty |
| **Seed metric** | Seed metric | The metric you "invent" when redistributing |
| **Route tag** | Route tag | **The only standard solution for dual-point redistribution loop prevention** |
| **Route feedback** | Route feedback | The source of loops in dual-point, dual-direction redistribution |
| **Egress / ingress traffic** | Egress / ingress traffic | Egress is fully controllable; ingress can only be requested |
| **PBR** | Policy-based routing | A last resort; breaks routing table consistency |
| **ECMP** | Equal-cost multipath | Per-flow hashing; use with care on unequal-speed links |

<div class="zh" markdown="1">

| 术语 | 中文含义 | 一句话记忆 |
|------|---------|-----------|
| **RIB** | 路由信息库 | 所有协议的候选池 |
| **FIB** | 转发信息库 | 真正用来转发的表 |
| **AD（管理距离）** | 不同来源的优先级 | 跨协议比较用 AD；eBGP(20) 优于 OSPF(110)，iBGP(200) 最劣 |
| **Metric（度量）** | 同协议内的路径优劣 | **跨协议不可比**——重分发的根本难题 |
| **最长匹配** | 掩码最长者胜 | 明细永远压过汇总 |
| **递归查找** | 下一跳逐层解析 | BGP 下一跳不可达则不装表 |
| **LSDB** | 链路状态数据库 | 区域内必须完全一致 |
| **SPF / Dijkstra** | 最短路径优先算法 | 以自己为根建树 |
| **Area 0 / Backbone** | 骨干区域 | 必须连续；不连续要靠 virtual-link（应急） |
| **ABR** | 区域边界路由器 | 汇总与 Type 3 的产生者 |
| **ASBR** | AS 边界路由器 | 重分发与 Type 5 的产生者 |
| **Type 1–7 LSA** | OSPF 的链路状态通告 | 1/2 拓扑，3/4 区域间，5/7 外部 |
| **Stub / Totally Stub** | 末节区域 | 不允许 ASBR；路由表最小 |
| **NSSA** | 非完全末节 | 允许本地重分发（有本地出口时用） |
| **Virtual Link** | 虚链路 | 应急手段，不是设计选项 |
| **P2P / P2MP / Broadcast** | OSPF 网络类型 | 网络类型是设计变量，不是自动检测 |
| **SPF Throttle** | SPF 节流 | 快检测必须配抑制 |
| **`auto-cost reference-bandwidth`** | 参考带宽 | 默认 100M → 所有 G 以上接口 cost=1 |
| **Area Range / Summary-address** | OSPF 汇总 | ABR 汇总区域内；ASBR 汇总外部 |
| **Null0** | 丢弃路由 | **汇总必须配 null0** |
| **IS-IS** | 中间系统到中间系统 | 跑在二层，TLV 扩展性最好 |
| **Level 1 / Level 2** | IS-IS 层级 | L2 = 骨干，天然连续 |
| **NET / System ID** | IS-IS 路由器标识 | 全网唯一 |
| **DIS** | 指定中间系统 | 无备份，抢占式（对比 DR 有 BDR） |
| **`metric-style wide`** | IS-IS 宽度量 | 必须开，否则无法区分高速链路 |
| **Overload Bit** | IS-IS 过载位 | 维护窗口用，避免提前吸引流量 |
| **Multi-Topology (MT)** | IS-IS 多拓扑 | IPv4/IPv6 可走不同路径 |
| **EIGRP / DUAL** | 扩散更新算法 | 距离矢量中的"混合型" |
| **FD / RD (AD)** | 可行距离 / 报告距离 | RD < FD 才能成为可行后继 |
| **Successor / Feasible Successor** | 后继 / 可行后继 | 有 FS 时本地修复，最快收敛 |
| **Query / SIA** | 查询 / 卡在活跃状态 | Query 扩散是 EIGRP 的主要规模风险 |
| **EIGRP Stub** | 末端路由 | 截断 Query 范围 |
| **BGP** | 边界网关协议 | 路径矢量，跑在 TCP 179 |
| **eBGP / iBGP** | 外部 / 内部 BGP | eBGP 直连；iBGP 需全互连或 RR |
| **iBGP 全互连规则** | iBGP 路由不再传给 iBGP | N(N−1)/2 条会话 |
| **Next-hop-self** | 下一跳自指 | iBGP 必配（或保证下一跳可达） |
| **Weight** | 权重 | Cisco 专有，本机有效，大者优 |
| **Local Preference** | 本地优先 | 整个 AS 有效，**控制出向** |
| **AS_PATH** | AS 路径 | 短者优；prepend 可加长 |
| **Origin** | 起源类型 | IGP < EGP < Incomplete |
| **MED** | 多出口判别器 | 小者优；**只在同一邻居 AS 内比较** |
| **Route Reflector (RR)** | 路由反射器 | 打破全互连需求 |
| **Cluster ID / Cluster List** | 集群 ID / 列表 | 防环；**多 RR 必须唯一** |
| **Originator ID** | 起源者 ID | RR 场景的第二道防环 |
| **Confederation** | 联盟 | 把大 AS 拆子 AS；复杂度高，一般不选 |
| **Peer Group / Template** | 邻居组 / 模板 | 配置量从 N 条降到 1 条 |
| **`update-delay`** | 更新延迟 | 启动时等邻居收敛，避免不完整表转发 |
| **Route Dampening** | 路由抑制 | **慎用**，容易造成长时间黑洞 |
| **Redistribution** | 重分发 | 跨协议翻译；度量不可比是根本难题 |
| **Seed Metric** | 种子度量 | 重分发时"拍"的度量 |
| **Route Tag** | 路由标记 | **双点双向重分发防环的唯一标准解法** |
| **Route Feedback** | 路由回馈 | 双点双向重分发的环路来源 |
| **Egress / Ingress Traffic** | 出向 / 入向流量 | 出向完全可控，入向只能请求 |
| **PBR** | 策略路由 | 最后手段，破坏路由表一致性 |
| **ECMP** | 等开销多路径 | 按流哈希，不等速链路慎用 |

</div>

---

## Chapter Summary · 本章小结

The main thread of Chapter 8 is **the layers of "control"**:

<div class="zh" markdown="1">

第 8 章的主线是**"控制"的层次**：

</div>

```
① Topology layer: areas/hierarchy/flooding domain   → sets the scale limit
② Metric layer: cost / metric / auto-cost           → sets the default path (easiest to lose control of)
③ Summarization layer: range / summary-address      → trades scale for visibility
④ Attribute layer: LP / MED / AS_PATH / Weight      → sets the policy path
⑤ Translation layer: redistribution / tag / seed metric → sets the boundary between heterogeneous domains
```

<div class="zh" markdown="1">

```
① 拓扑层：区域/层级/泛洪域          → 决定规模上限
② 度量层：cost / metric / auto-cost → 决定默认路径（最容易失控）
③ 汇总层：range / summary-address   → 决定规模与可见性的交换
④ 属性层：LP / MED / AS_PATH / Weight → 决定策略路径
⑤ 翻译层：重分发 / tag / seed metric → 决定异构域的边界
```

</div>

**Five conclusions worth taking away**:

<div class="zh" markdown="1">

**五条可以带走的结论**：

</div>

1. **The defaults are the design.** `auto-cost reference-bandwidth 100`, `default local-preference 100`, and MED being compared only within the same AS — these defaults determine the network's real behavior. Not designing explicitly means accepting "a network nobody ever designed".
2. **Egress is controllable; ingress can only be requested.** Any promise of "bidirectional load sharing" is empty unless you control the far end.
3. **The number of protocols must match operational capability.** The complexity of dual-point, dual-direction redistribution almost always exceeds the problem it solves; unify wherever you can.
4. **Summarization = trading visibility for scale.** Once you summarize, you must accept that "the summary address still works during a failure" and write the troubleshooting method (look inside the area) into the operations manual.
5. **Verify with the FIB and with traffic data, not with configuration and the BGP table.** `*>` in `show ip bgp` does not mean packets can be forwarded; a successful `traceroute` does not mean the path matches the design. **NetFlow plus `show ip cef` is the evidence.**

<div class="zh" markdown="1">

1. **默认值就是设计**。`auto-cost reference-bandwidth 100`、`default local-preference 100`、MED 只在同 AS 内比较——这些默认值决定了网络的真实行为。不显式设计，就等于接受了一个"没人设计过的网络"。
2. **出向可控，入向只能请求**。任何"双向负载分担"的承诺，在不控制对端的前提下都是空的。
3. **协议数量要与运维能力匹配**。双点双向重分发的复杂度，几乎永远超过它解决的问题；能统一就统一。
4. **汇总 = 用可见性换规模**。用了汇总，就必须接受"故障期间汇总地址仍然通"这件事，并把排障方法（进区域内看）写进运维手册。
5. **验证要看 FIB 和流量，不看配置和 BGP 表**。`show ip bgp` 有 `*>` 不代表能转发；`traceroute` 通不代表路径符合设计。**NetFlow + `show ip cef` 才是证据。**

</div>

The next chapter (Chapter 9, Network Virtualization) puts these Layer 3 capabilities into a virtualization context: when "one physical device" becomes "multiple logical devices" and "one network" becomes "multiple isolated VRFs", how do the roles of BGP and the IGP change?

<div class="zh" markdown="1">

下一章（第 9 章 网络虚拟化）会把这些三层能力放进虚拟化语境：当"一台物理设备"变成"多台逻辑设备"、"一个网络"变成"多个隔离的 VRF"时，BGP 与 IGP 的角色会如何变化。

</div>
