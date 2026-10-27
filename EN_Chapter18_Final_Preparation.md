# Chapter 18: The Whole Book in One Pass: A Complete Design Decision Workflow · 第 18 章：全书串讲：一次完整的设计决策流程

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapter 18 (pp. 850–1077; the original "Final Preparation" rewritten as a practical end-to-end walkthrough)

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译 | 原书第 850-1077 页（原章节为"最终准备"，已改写为面向实践的全书串讲）

</div>

---

## Topics Covered · 本章涵盖主题

- **The knowledge map of the whole book**: how the 18 chapters relate
- **Three threads**: the business thread, the architecture thread, the technology thread
- **The overall design decision workflow**: seven steps from kickoff to Day 2
- **Deliverables checklist**: what a complete design should produce
- **Cross-chapter trade-off lookup and the high-frequency mistake list**
- **Further reading**: RFCs and design documents

<div class="zh" markdown="1">

- **全书知识地图**：18 章之间的关系
- **三条主线**：业务线、架构线、技术线
- **设计决策总流程**：从立项到 Day 2 的七个步骤
- **设计交付物清单**：一次完整设计应该产出什么
- **跨章取舍速查与易错点清单**
- **延伸阅读**：RFC 与设计文档

</div>

---

## The Knowledge Map of the Whole Book · 全书知识地图

The 18 chapters form one continuous chain of reasoning: **from "why do this" to "how to do it", and then to "how to do it in this particular scenario"**.

<div class="zh" markdown="1">

本书 18 章其实是一条完整的推理链：**从"为什么做"到"怎么做"，再到"在什么场景下怎么做"**。

</div>

```
Part I  The premises of design (Chapters 1–5)
  1 Design thinking   → how you think decides what you design
  2 Business success  → why, is it worth it, how it is accepted
  3 Network purpose   → what the network must carry (apps/services/cloud/data)
  4 Security          → a constraint across every layer, not one box
  5 Architecture frameworks → wrap all of the above into a governable process
        ↓
Part II The technical toolbox (Chapters 6–14)
  6 Transport      → what I buy from the carrier
  7 Layer 2        → how the Layer 2 network I build is designed
  8 Layer 3        → which routing protocol, how it converges
  9 Virtualization → overlay and segmentation
 10 Security design→ putting Chapter 4's principles into practice
 11 Wireless       → mobility and capacity at the access side
 12 Automation     → repeatable and verifiable
 13 Multicast      → the efficiency of one-to-many
 14 Services and management → DNS/DHCP/NTP/QoS, invisible but fatal
        ↓
Part III Scenario architectures (Chapters 15–17)
 15 Campus   16 Internet edge   17 Enterprise WAN
        ↑ everything from the first three parts is assembled here into a concrete solution
```

<div class="zh" markdown="1">

```
Part I  设计的前提（第 1–5 章）
  1 设计思维  → 你怎么想，决定你设计出什么
  2 商业成功  → 为什么做、值不值、怎么验收
  3 网络目的  → 网络要承载什么（应用/服务/云/数据）
  4 安全      → 贯穿所有层的约束，不是一层设备
  5 架构框架  → 把上面全部纳入可治理的流程
        ↓
Part II 技术工具箱（第 6–14 章）
  6 传输      → 我从运营商买什么
  7 二层      → 我自己建的二层怎么设计
  8 三层      → 路由协议怎么选、怎么收敛
  9 虚拟化    → Overlay 与分段
 10 安全设计  → 落地第 4 章的原则
 11 无线      → 接入侧的移动性与容量
 12 自动化    → 可重复、可验证
 13 组播      → 一对多的效率问题
 14 服务管理  → DNS/DHCP/NTP/QoS 这些"看不见但会致命"的部分
        ↓
Part III 场景化架构（第 15–17 章）
 15 园区  16 互联网边缘  17 企业 WAN
        ↑ 前三部分的全部知识在这里被组装成具体方案
```

</div>

> 💡 **How to read the map**: Part II is the "parts bin", Part III is the "whole machine". Someone who knows only parts cannot produce a good design, because they do not know how the parts constrain one another inside the machine.

<div class="zh" markdown="1">

> 💡 **理解这张图的方式**：Part II 是"零件"，Part III 是"整机"。只会零件的人做不出好设计，因为他不知道零件在整机里如何互相牵制。

</div>

---

## Three Study Threads · 三条学习主线

The same book can be worked through along three different threads, and each pass yields something different.

<div class="zh" markdown="1">

同一本书，可以按三种线索反复过，每次都有不同收获。

</div>

### Thread 1: The Business Thread (answering "why") · 主线一：业务线（回答"为什么"）

```
Business drivers → business outcomes (SMART) → business capabilities → network requirements (functional/non-functional) → design → acceptance metrics (KPIs)
```

<div class="zh" markdown="1">

```
业务驱动力 → 业务成果(SMART) → 业务能力 → 网络需求(功能/非功能) → 设计 → 验收指标(KPI)
```

</div>

The chapters that string together: drivers and KPIs in Chapter 2, alignment levels in Chapter 5, application characteristics in Chapter 3, scenario requirements in Chapters 15–17.

<div class="zh" markdown="1">

串起来的章节：第 2 章的驱动力与 KPI、第 5 章的对齐级别、第 3 章的应用特征、第 15–17 章的场景需求。

</div>

> Self-check: **can you say in one business sentence what problem this design solves?** If not, the chapter is not yet understood.

<div class="zh" markdown="1">

> 自检问题：**你能用一句业务语言说清"这个设计解决什么问题"吗？** 说不清，说明这章还没读懂。

</div>

### Thread 2: The Architecture Thread (answering "at which layer") · 主线二：架构线（回答"在哪一层解决"）

| Requirement | Possible layers | Typical choices |
|-------------|-----------------|-----------------|
| Two sites must interconnect | L1/L2/L3/overlay | Dark fiber / L2VPN / MPLS L3VPN / SD-WAN |
| Isolation | VLAN / VRF / VXLAN segment / micro-segmentation | Chosen by business and compliance needs |
| High availability | Physical redundancy / protocol convergence / active-active applications | Chosen by RTO/RPO |
| Scalability | Hierarchy / modularity / overlay | Chosen by growth expectations |

<div class="zh" markdown="1">

| 需求 | 可能的解决层次 | 典型选择 |
|------|--------------|---------|
| 两个站点要互通 | L1/L2/L3/Overlay | 暗光纤 / L2VPN / MPLS L3VPN / SD-WAN |
| 隔离 | VLAN / VRF / VXLAN 分段 / 微分段 | 按业务与合规要求选 |
| 高可用 | 物理冗余 / 协议收敛 / 应用多活 | 按 RTO/RPO 选 |
| 可扩展 | 分层 / 模块化 / Overlay | 按增长预期选 |

</div>

The core question of the architecture thread never changes: **at which layer can this requirement be solved with the least effort and the fewest opportunities for error?**

<div class="zh" markdown="1">

架构线的核心问题永远是：**这个需求应该在哪一层解决最省事、最不容易出错？**

</div>

### Thread 3: The Technology Thread (answering "how exactly to configure it") · 主线三：技术线（回答"具体怎么配"）

Protocol details, packet behaviour, convergence mechanisms, parameter values. This part needs hands-on verification (lab, packet capture) — reading alone will fool you.

<div class="zh" markdown="1">

协议细节、报文行为、收敛机制、参数取值。这部分需要动手验证（实验环境、抓包），光看会骗自己。

</div>

---

## The Overall Design Workflow (Seven Steps) · 设计决策总流程（七步）

The first 17 chapters supply the "knowledge parts"; this section supplies the **assembly order**. Real projects rarely fail because "someone did not understand a technology"; they fail because **steps were skipped or reordered** — pick the technology before finding the requirement, draw the topology before defining the boundary, go live before thinking about acceptance.

<div class="zh" markdown="1">

前面 17 章给的是"知识零件"，这一节给的是**装配顺序**。真实项目的失败很少是因为"不懂某个技术"，而是因为**步骤被跳过或顺序颠倒**——先选技术再找需求、先搭拓扑再定边界、先上线再想验收。

</div>

Each step is given as: **input → action → output → most common mistake**.

<div class="zh" markdown="1">

每一步都给出：**输入 → 动作 → 产出 → 最常见错误**。

</div>

### Step 0: Kickoff and Scope Definition · Step 0 立项与范围界定

| Item | Content |
|---|---|
| **Input** | A request ("the network needs upgrading", "we are building a new plant", "we must integrate an acquisition") |
| **Action** | Classify the design case (the seven in Chapter 1: new build / redesign / add technology / replace / merge or divest / expand / fix a failure); write **in-scope and out-of-scope** lists; name the decision maker and the signatory |
| **Output** | One-page project charter: goal, scope, stakeholders, milestones, what we will not do |
| **Common mistake** | Scope states only "what we will do", never "what we will not do"; treating "the technical solution" as the project goal (the goal is a business outcome, the solution is a means) |

<div class="zh" markdown="1">

| 项 | 内容 |
|---|---|
| **输入** | 一个诉求（"网络要升级""新厂要建""并购要整合"） |
| **动作** | 判断设计用例（第 1 章七种：全新/改造/加技术/替换/合并剥离/扩展/失败修复）；画出**范围内/范围外**两个清单；明确决策人与签字人 |
| **产出** | 一页纸的项目章程：目标、范围、干系人、里程碑、不做什么 |
| **常见错误** | 范围只写"做什么"不写"不做什么"；把"技术方案"当项目目标（目标是业务结果，方案是手段） |

</div>

### Step 1: Clarify Business Goals and Outcomes · Step 1 澄清业务目标与成果

| Item | Content |
|---|---|
| **Input** | Business requests, pain points, budget, time windows |
| **Action** | Use "five whys" until the statement is verifiable; rewrite goals as SMART outcomes plus KPIs (Chapter 2); identify business drivers and compliance constraints (Chapter 4) |
| **Output** | Business outcome list + KPI baseline values + compliance requirements list |
| **Common mistake** | Accepting unmeasurable goals such as "improve experience" or "match peers"; deferring compliance to "we will handle it during implementation" |

<div class="zh" markdown="1">

| 项 | 内容 |
|---|---|
| **输入** | 业务方的诉求、痛点、预算、时间窗 |
| **动作** | 用"五个为什么"追问到可验证的层面；把目标改写成 SMART 成果 + KPI（第 2 章）；识别业务驱动力与合规约束（第 4 章） |
| **产出** | 业务成果清单 + KPI 基线值 + 合规要求清单 |
| **常见错误** | 接受"提升体验""对标同行"这类不可测目标；把合规要求当成"实施时再处理" |

</div>

### Step 2: Establish the Current-State Baseline · Step 2 建立现状基线

| Item | Content |
|---|---|
| **Input** | Existing documentation, monitoring data, interviews |
| **Action** | Collect three baseline categories: **capacity** (bandwidth/ports/CPU/sessions), **behaviour** (traffic matrix, route counts, convergence times), **organisation** (team skills, processes, contract terms) |
| **Output** | Current-state baseline report + a "problem–evidence" mapping table |
| **Common mistake** | Looking only at average utilisation (which hides bursts); trusting documents instead of measuring; ignoring remaining contract terms (which set the migration window) |

<div class="zh" markdown="1">

| 项 | 内容 |
|---|---|
| **输入** | 现网文档、监控数据、访谈 |
| **动作** | 采集三类基线：**容量**（带宽/端口/CPU/会话）、**行为**（流量矩阵、路由条目、收敛时间）、**组织**（团队技能、流程、合同期限） |
| **产出** | 现状基线报告 + "问题—证据"对应表 |
| **常见错误** | 只看平均利用率（掩盖突发）；只信文档不测现网；忽略合同剩余期限（决定迁移窗口） |

</div>

### Step 3: Define Requirements and Constraints · Step 3 定义需求与约束

| Item | Content |
|---|---|
| **Input** | Business outcomes + current-state baseline |
| **Action** | Write requirements in three categories: functional (what it does), technical/non-functional (availability, security, manageability), application (latency/loss/connection model); write constraints in four categories: business, application, technical, time and budget (Chapter 1) |
| **Output** | Requirements specification (each entry with source and verification method) + constraint list + **list of unresolved requirements** |
| **Common mistake** | Requirements without a source (untraceable); mistaking a solution for a requirement ("we need SD-WAN" actually means "a new site must be online within 7 days") |

<div class="zh" markdown="1">

| 项 | 内容 |
|---|---|
| **输入** | 业务成果 + 现状基线 |
| **动作** | 分三类写需求：功能（做什么）、技术/非功能（可用性、安全、可管理性）、应用（时延/丢包/连接模型）；约束分四类：业务、应用、技术、时间与预算（第 1 章） |
| **产出** | 需求规格表（每条带来源与验证方式）+ 约束清单 + **未明确需求清单** |
| **常见错误** | 需求没有来源（无法追溯）；把方案当需求（"需要 SD-WAN"其实是"需要新站点 7 天上线"） |

</div>

### Step 4: Draw the Architecture Boundaries · Step 4 划分架构边界

| Item | Content |
|---|---|
| **Input** | Requirements + constraints |
| **Action** | Divide modules and domains by business / trust level / failure domain: campus, WAN, DC, Internet edge, cloud access (the models in Chapters 15–17); define the **single convergence point** between domains; choose the isolation layer (VLAN / VRF / segment / micro-segment) |
| **Output** | Logical architecture diagram + inter-domain interface table (who connects to whom, over what, with which policy) |
| **Common mistake** | Domains drawn too large (an enlarged failure domain); multiple interconnection points between domains (policy cannot stay consistent); choosing equipment before defining boundaries |

<div class="zh" markdown="1">

| 项 | 内容 |
|---|---|
| **输入** | 需求 + 约束 |
| **动作** | 按业务/信任等级/故障域划模块与域：园区、WAN、DC、互联网边缘、云接入（第 15–17 章模型）；确定域间互通的**唯一收敛点**；确定隔离技术层次（VLAN / VRF / 分段 / 微分段） |
| **产出** | 逻辑架构图 + 域间接口表（谁连谁、走什么、什么策略） |
| **常见错误** | 域划得太大（故障域放大）；域间有多个互通点（策略无法一致）；先选设备后定边界 |

</div>

### Step 5: Layered Technical Decisions · Step 5 分层技术决策

Decide layer by layer in a fixed order, and at every layer answer "why not the other option". The order itself is the design method:

<div class="zh" markdown="1">

按固定顺序逐层决策，每一层都必须回答"为什么不是另一个"。这个顺序本身就是设计方法：

</div>

| Layer | Decision question | Main chapters |
|---|---|---|
| **Transport/bearer** | What do we buy between sites? Carrier L2/L3, Internet, leased line, SD-WAN? | 6, 17 |
| **Layer 2** | Is Layer 2 extension needed? Where is the STP domain boundary? | 7 |
| **Layer 3** | IGP/BGP boundaries, area planning, summarisation and convergence, dual stack | 8 |
| **Overlay/segmentation** | Do we need VXLAN/VRF/micro-segmentation? Control-plane or data-plane isolation? | 9, 10 |
| **Security** | Trust boundaries, encryption, access control, where visibility is implemented | 4, 10 |
| **Access** | Wired/wireless/remote, capacity and density, authentication methods | 11 |
| **Services** | Distribution and redundancy of DNS/DHCP/NTP/QoS/multicast | 13, 14 |
| **Automation and observability** | How configuration is generated, how changes are validated, how faults are located | 12, 14 |

<div class="zh" markdown="1">

| 层 | 决策问题 | 主要章节 |
|---|---|---|
| **传输/承载** | 站点之间买什么？运营商 L2/L3、Internet、专线、SD-WAN？ | 6、17 |
| **二层** | 需要二层延伸吗？STP 域边界在哪？ | 7 |
| **三层** | IGP/BGP 边界、区域规划、汇总与收敛、双栈 | 8 |
| **Overlay/分段** | 是否需要 VXLAN/VRF/微分段？控制面还是数据面隔离？ | 9、10 |
| **安全** | 信任边界、加密、访问控制、可见性在哪落地 | 4、10 |
| **接入** | 有线/无线/远程，容量与密度，认证方式 | 11 |
| **服务** | DNS/DHCP/NTP/QoS/组播等基础服务的分布与冗余 | 13、14 |
| **自动化与可观测** | 配置如何生成、变更如何验证、故障如何定位 | 12、14 |

</div>

**Output**: one decision table per layer (options / trade-offs / conclusion / reasons rejected).

<div class="zh" markdown="1">

**产出**：每层一张决策表（选项 / 取舍 / 结论 / 被否决理由）。

</div>

**Common mistake**: skipping the transport layer and drawing the topology directly; solving at Layer 2 what belongs at Layer 3; treating "it can work" as "it should be used".

<div class="zh" markdown="1">

**常见错误**：跳过传输层直接画拓扑；在二层解决本该在三层解决的问题；把"能用"当成"该用"。

</div>

### Step 6: Validation and Quantitative Acceptance · Step 6 验证与量化验收

| Item | Content |
|---|---|
| **Input** | Layered decisions + business KPIs |
| **Action** | Three levels of validation: **design validation** (model walkthrough, failure-domain analysis, capacity calculation), **lab validation** (minimal experiments for key mechanisms), **acceptance validation** (measurable metrics and pass thresholds after go-live) |
| **Output** | Acceptance test table (metric, collection method, pass threshold, owner) + risk register |
| **Common mistake** | Acceptance defined as "it pings"; no rollback criteria; treating "the load test passed" as "the business is available" |

<div class="zh" markdown="1">

| 项 | 内容 |
|---|---|
| **输入** | 分层决策 + 业务 KPI |
| **动作** | 三层验证：**设计验证**（模型推演、故障域分析、容量测算）、**实验验证**（关键机制的最小实验）、**验收验证**（上线后的可测指标与判定阈值） |
| **产出** | 验收用例表（指标、采集方式、通过阈值、责任人）+ 风险登记册 |
| **常见错误** | 验收标准是"能通"；没有回退判据；把"压测通过"当成"业务可用" |

</div>

### Step 7: Migration and Day 2 · Step 7 迁移与 Day 2

| Item | Content |
|---|---|
| **Input** | Target architecture + current-state baseline |
| **Action** | Design a **phased migration** (non-critical sites or services first, each batch with its own acceptance); define **rollback triggers and rollback duration** for every batch; deliver the operational essentials: monitoring items, alert thresholds, change process, on-call handover, documentation and topology-maintenance ownership |
| **Output** | Migration roadmap (batches, windows, validation, rollback) + operations manual + training plan |
| **Common mistake** | A single big-bang cutover; handing over equipment without documentation; nobody owning the Day 2 complexity |

<div class="zh" markdown="1">

| 项 | 内容 |
|---|---|
| **输入** | 目标架构 + 现状基线 |
| **动作** | 设计**分批迁移**（先非关键站点/业务，每批都有独立验收）；为每批定义**回退触发条件与回退耗时**；交付运维要件：监控项、告警阈值、变更流程、值班交接、文档与拓扑维护责任 |
| **产出** | 迁移路线图（批次、窗口、验证、回退）+ 运维手册 + 培训计划 |
| **常见错误** | 一次性全量切换；只交设备不交文档；没有人为 Day 2 的复杂度负责 |

</div>

> 💡 **The order of the seven steps cannot be swapped.** The most common failure is moving Step 5 in front of Step 1: solution first, then requirements used to justify it. **In a review, one question exposes such a proposal: "which metric of which requirement does this technology solve?"**

<div class="zh" markdown="1">

> 💡 **七步的次序不可交换**。最常见的失败是把 Step 5 提到 Step 1 前面：方案先行，然后用需求去解释方案。**评审时只要问一句"这个技术解决了哪条需求的哪个指标"，就能识别出这类方案。**

</div>

---

## Design Deliverables Checklist · 设计交付物清单

A complete design is not just "a topology diagram". The following checklist can be used directly as a project template:

<div class="zh" markdown="1">

一次完整的设计，不只是"一张拓扑图"。以下清单可直接当作业模板使用：

</div>

| Deliverable | Minimum content | Who signs off |
|---|---|---|
| **Business requirements and outcomes** | Goals, KPIs, constraints, out-of-scope list | Business owner |
| **Current-state baseline** | Capacity/behaviour/organisation, problem–evidence mapping | Operations and engineering |
| **Logical design** | Domain boundaries, inter-domain interfaces, addressing and naming | Architecture owner |
| **Physical/topology design** | Equipment placement, links, redundancy model, failure-domain analysis | Architecture owner |
| **Technical decisions** | One decision table per layer (options / trade-offs / conclusion / reasons rejected) | Technical authority |
| **Security design** | Trust boundaries, policy, encryption, access control, audit | Security and compliance |
| **Capacity and performance model** | Traffic matrix, growth ratio, bottleneck analysis, scaling triggers | Technical authority |
| **Acceptance test plan** | Metrics, methods, thresholds, owners, rollback criteria | Business plus operations |
| **Migration roadmap** | Batches, windows, rollback plan, communication plan | Project manager |
| **Operations and Day 2** | Monitoring items, alert thresholds, change process, documentation ownership | Operations owner |

<div class="zh" markdown="1">

| 交付物 | 最小内容要求 | 谁签字 |
|---|---|---|
| **需求规格书** | 功能/技术/应用三类需求，每条带来源、验证方式、优先级 | 业务方 + 设计负责人 |
| **现状基线报告** | 容量、行为、组织三类数据，附采集方法与时间 | 运维负责人 |
| **逻辑架构图** | 域划分、域间接口、信任边界、故障域标注 | 设计负责人 |
| **分层决策表** | 传输/二层/三层/Overlay/安全/接入/服务/自动化各一张，含被否决理由 | 架构评审会 |
| **地址与命名规划** | IPv4/IPv6 分配、VLAN/VRF 编号、设备命名、DNS 命名空间 | 网络负责人 |
| **容量与规模测算** | 带宽、端口、表项、会话、AP/信道，含三年增长 | 设计负责人 |
| **高可用与故障域分析** | 单点清单、故障场景矩阵（故障 → 影响 → 收敛时间） | 运维负责人 |
| **安全设计说明** | 信任边界、加密点、访问控制模型、审计留存 | 安全负责人 |
| **验收用例表** | 指标、采集方式、阈值、责任人 | 业务方 + 运维 |
| **迁移与回退方案** | 批次、窗口、验证、回退触发与耗时 | 项目经理 |
| **运维要件** | 监控项、告警阈值、备份、变更流程、培训 | 运维负责人 |
| **风险登记册与决策记录** | 每条决策的背景、选项、结论、被否决理由 | 设计负责人 |

</div>

> **Why "reasons rejected" must be written down**: a year later nobody remembers why an option was not used, so the same discussion starts over from scratch — and sometimes it lands on the rejected option. **Recording the rejected options and why is what makes decisions repeatable.**

<div class="zh" markdown="1">

> **为什么"被否决理由"必须写**：一年后没人记得为什么不用某个方案，于是同样的讨论会重来一遍。**决策记录是设计团队最重要的长期资产。**

</div>

---

## Design Judgement Checklist (Usable for Any Proposal) · 设计判断清单（任何方案都能用）

1. **Is the requirement real?** Is it backed by measurement, or is it just someone's opinion?
2. **Are all the constraints on the table?** Including the uncomfortable ones: budget, contract terms, team capability, organisational boundaries.
3. **Have the rejected options been documented?** For each: one sentence on why it was rejected.
4. **Where is the single point of failure?** Including power, cooling, physical paths, carriers and vendors.
5. **Has the convergence time been verified?** Measured, not assumed.
6. **What happens if the new technology fails?** Can we fail over? How long is the rollback?
7. **What would the strongest objection to this design be?** Who would make it, and how would you answer?

<div class="zh" markdown="1">

1. **需求是真的吗？** 有测量数据支持，还是只是某人的说法？
2. **约束都列全了吗？** 预算、时间、合规、遗留系统、人力。
3. **这个方案解决了当前问题，还是解决了想象的问题？**（过度设计检查）
4. **故障域有多大？** 一处故障会影响多少业务？
5. **谁在 Day 2 维护它？** 现有团队接得住吗？
6. **怎么验证它有效？** 有可测指标吗？
7. **否决它的理由是什么？** 能不能自己说出三个反对意见？

</div>

> 💡 **Item 7 is the most effective self-check**: if your proposal cannot survive the objections you raise yourself, it will not survive a design review.

<div class="zh" markdown="1">

> 💡 **第 7 条是最有效的自检**：如果你的方案经不起自己提的反对意见，它经不起评审。

</div>

---

## Integrated Case: A Real Transformation That Strings the Whole Book Together · 综合案例：把全书串起来的一次真实改造

**Background**: a manufacturer with 8,000 employees — headquarters, 6 plants, 40 sales offices. Problems: MPLS leased lines cost 42M per year and grow 15% a year; a new plant takes 10 weeks from decision to connectivity; one broadcast storm at a plant has taken down the whole company twice; a security audit raised 37 findings; the operations team is 4 people and cannot keep up with configuration changes.

<div class="zh" markdown="1">

**背景**：一家 8000 人的制造企业，总部 + 6 个工厂 + 40 个销售办事处。现状：总部双核心、工厂用 SDH 专线、办事处用 ADSL，全网一个 OSPF 域、一个 VLAN 大二层延伸到部分工厂。

</div>

**Reasoning in the book's order**:

<div class="zh" markdown="1">

**按全书顺序推演**：

</div>

| Step | Chapters used | What was done |
|------|---------------|---------------|
| 1. Business outcomes | 2, 5 | Rewritten as: cost −30%, new site live in ≤4 weeks, plant isolation, zero audit findings |
| 2. Baseline | 2 | Measured: 82% of traffic is IP; only 3 legacy systems need Layer 2 |
| 3. Requirements and constraints | 1, 3 | Constraint discovered: three MPLS contracts still have 18 months left, so a big-bang cutover is impossible |
| 4. Architecture boundaries | 5, 15–17 | Split into campus / WAN / Internet edge / cloud access, with one convergence point per domain |
| 5. Layered decisions | 6–14 | WAN: MPLS plus Internet SD-WAN hybrid; campus: Layer 3 to the access layer; security: segmentation plus cloud security service; automation: template-driven configuration |
| 6. Validation | 12, 14 | Before/after comparison on one plant pilot: convergence, cost, configuration time |
| 7. Migration and Day 2 | 12 | Three batches over 18 months, one batch per MPLS contract expiry; monitoring and change process handed over |

<div class="zh" markdown="1">

| 步骤 | 用到哪章 | 做法 |
|------|---------|------|
| 1. 澄清需求 | 1、2 | 访谈发现真实痛点是"新产线上线要 10 周"，其中 4 周等网络 |
| 2. 定义成果 | 2、5 | 目标改为"新产线上线 ≤ 5 周"，而不是"网络升级" |
| 3. 摸清应用 | 3 | 产线 MES 对丢包敏感（<0.1%），办公以 HTTP/文件为主 |
| 4. 安全定性 | 4 | 产线网与办公网必须隔离，且产线不允许跨厂二层互通 |
| 5. 传输选型 | 6、17 | 工厂改 MPLS L3VPN（不再需要二层）；办事处改 Internet + SD-WAN |
| 6. 二层收敛 | 7 | 拆掉跨厂大二层，工厂内部按产线划分 VLAN，STP 只在厂内 |
| 7. 三层设计 | 8 | 总部/工厂走 BGP（便于策略与多运营商），厂内 OSPF |
| 8. 分段 | 9 | 产线单独 VRF，办公与产线之间只在指定点互通 |
| 9. 接入 | 11 | 车间 Wi-Fi 与 AGV 用独立 SSID 与频段规划 |
| 10. 自动化 | 12 | 新产线网络用模板 + 自动化开通，把 4 周压到 2 天 |
| 11. 管理与验证 | 14 | QoS 分级、NTP 统一、DNS 分区、SLA 度量 |

</div>

**Result**: time to bring a site online fell from 10 weeks to 4; Layer 2 failures at plants no longer spread; leased-line cost down 35%.

<div class="zh" markdown="1">

**结果**：上线周期 10 周 → 4 周；跨厂二层故障不再扩散；专线成本降 35%。

</div>

**What this case shows**: **no single chapter can solve this project.** Real design capability shows up as "knowing which chapter's method to use at which moment" — and that is exactly what this chapter is for.

<div class="zh" markdown="1">

**这个案例说明了什么**：**没有任何一个单章能解决这个项目。** 真正的设计能力体现在"知道该按什么顺序问问题"。

</div>

---

## Core Thinking Modes · 核心思维模式

> 💡 **The most important thing is not memorising technical details but forming an order of judgement**

<div class="zh" markdown="1">

> 💡 **最重要的不是记住技术细节，而是形成判断顺序**

</div>

| Thinking mode | Explanation |
|---------------|-------------|
| **Business driver first** | Any technical decision must answer which business outcome it serves |
| **Constraint-driven** | Design is not "choosing the best", it is "finding the feasible best under constraints" |
| **Failure domain thinking** | Every design is evaluated by "what happens when it fails" |
| **Reversibility** | Prefer decisions that are easy to roll back |
| **Quantified verification** | Anything unmeasured is a guess |
| **Manageability** | The design that a 4-person team can operate beats the elegant one it cannot |
| **Cost of ownership** | TCO, not CAPEX |
| **Explicit assumptions** | Write assumptions down; they are the first thing to break |

<div class="zh" markdown="1">

| 思维模式 | 说明 |
|---------|------|
| **业务驱动** | 每个设计决策都能追溯到业务需求 |
| **没有标准答案** | 每个场景有其独特需求、约束和优先级 |
| **避免过度设计** | 解决当前问题，不多不少 |
| **权衡取舍** | 在功能、成本、复杂度之间取得平衡 |
| **全局视角** | 考虑整个网络而非单一模块 |
| **简单性优先** | 在满足需求前提下选最简单方案 |
| **可运维性** | 能维护的方案才是好方案 |

</div>

---

## Cross-Chapter Trade-Off Lookup: One Question, Many Answers · 跨章取舍速查：同一个问题，各章给了什么答案

The same requirement has answers at different layers in different chapters. **The most common error in design is answering at the wrong layer** — for example, solving an isolation requirement with a firewall rule (Layer 4–7) when a VRF (Layer 3) would have been cheaper and cleaner.

<div class="zh" markdown="1">

同一个需求在不同章里有不同层次的解法。**设计时最容易出错的地方，是在错误的层次回答**。下面这张表用来快速定位"该在哪一层解决"：

</div>

| Question | Answers by chapter | Boundary |
|----------|--------------------|----------|
| Should the two sites be connected over Layer 2 or Layer 3? | Ch7: Layer 2 extension enlarges the failure domain; Ch6: L2VPN offers transparency; Ch8: routing gives convergence | Only extend Layer 2 when a non-IP protocol or fixed addressing genuinely requires it |
| How is isolation achieved? | Ch7 VLAN; Ch8 VRF; Ch9 VXLAN segment; Ch10 micro-segmentation/policy | By business and compliance granularity |
| Where does high availability come from? | Ch7 STP/clustering; Ch8 BGP/IGP convergence; Ch2 RTO/RPO | Depends on the acceptable outage time |
| How is cost reduced? | Ch6 service choice; Ch12 automation; Ch17 SD-WAN | Automation reduces opex, transport choice reduces circuit cost |
| How is security implemented? | Ch4 principles; Ch9 segmentation; Ch10 controls; Ch15–17 placement | Security is a constraint on every layer, not one device |
| How is mobility supported? | Ch11 wireless; Ch9 overlay; Ch14 services | Roaming requirements decide the design |

<div class="zh" markdown="1">

| 问题 | 各章的答案 | 分界点 |
|------|-----------|--------|
| **两个站点互通** | 第 6 章：传输服务（EPL/EVPL/EVPN）<br>第 9 章：L3VPN / Overlay<br>第 17 章：WAN 架构（MPLS / Internet + SD-WAN） | 是否真的需要二层？需要 → 传输层/二层服务；不需要 → 三层 VPN 或 Overlay |
| **隔离** | 第 7 章：VLAN + Private VLAN<br>第 9 章：VRF、VXLAN 分段<br>第 10 章：SGT、微分段、802.1X<br>第 15 章：园区分段（业务/管理/访客） | 范围与精度：同一交换机内 → VLAN；跨站点 → VRF；东西向精细 → 微分段 |
| **高可用** | 第 7 章：STP/vPC/堆叠<br>第 8 章：路由收敛、BFD、ECMP<br>第 15 章：园区冗余模型<br>第 16 章：多宿主、状态同步<br>第 17 章：WAN 冗余形态 | 先定 RTO/RPO（第 2 章），再选层：秒级 → 协议收敛；分钟级 → 设备冗余；小时级 → 备件与流程 |
| **加密** | 第 4 章：策略要求<br>第 9 章：MPLS VPN **本身不加密**<br>第 10 章：IPsec / MACsec / GET VPN<br>第 16 章：边缘加密边界 | 运营商 MPLS 是"隔离"不是"加密"；需要保密性就自己加 IPsec/MACsec |
| **MTU** | 第 6 章：伪线封装开销<br>第 9 章：VXLAN/IPsec 开销<br>第 10 章：`ip mtu` + `adjust-mss` | 任何封装都要算，表现为"ping 通但业务不通" |
| **规模增长** | 第 7 章：二层域范围<br>第 8 章：区域划分、RR、汇总<br>第 13 章：组播 RP 与状态规模<br>第 15 章：园区层次与模块化 | 先问"增长的是流量、路由还是终端"，三者对策完全不同 |
| **多运营商** | 第 16 章：入向不可控、AS 规划<br>第 17 章：SD-WAN 多链路策略<br>第 8 章：BGP 选路方向（出向 LP / 入向 MED） | 出向自己可控，入向只能通过宣告与对端协商 |
| **运维能力不足** | 第 1 章：可管理性原则<br>第 12 章：自动化与模板<br>第 5 章：运营模型与标准化 | 团队接不住的方案不是好方案，复杂度必须与运维能力匹配 |

</div>

> 💡 **How to use it**: when a design requirement arrives, first decide **which layer it is asking about**, then go to that chapter. **A cross-layer answer is usually the most expensive one.**

<div class="zh" markdown="1">

> 💡 **用法**：拿到一个设计需求，先判断"它在问哪一层"，再看该层的章。**跨层回答是最常见的错误**——例如用"扩带宽"回答"应用 chatty 导致的高时延"。

</div>

---

## High-Frequency Mistake List (Whole-Book Quick Reference) · 高频易错点清单（全书速查）

| # | Mistaken belief | Correct understanding | Source |
|---|-----------------|-----------------------|--------|
| 1 | Requirements can be gathered completely at the start | Requirements emerge and conflict; design must handle change | Ch1, Ch5 |
| 2 | Redundancy equals reliability | Only independent failure domains count | Ch7, Ch12 |
| 3 | Convergence time is a protocol parameter | It is the sum of detection, notification, repair and application recovery | Ch7, Ch8 |
| 4 | "It pings" means the network is fine | Path quality, MTU, asymmetry and flooding all hide | Ch7, Ch14 |
| 5 | Security is a device or a zone | It is a constraint across every layer | Ch4, Ch10 |
| 6 | Automation is writing scripts | It is templates, validation, pipelines and rollback | Ch12 |
| 7 | Multicast is just "enable PIM" | It is RP design, tree selection and policy | Ch13 |
| 8 | Cloud connectivity is one link | It is a model choice (DCI/VPN/gateway) plus routing and security | Ch3, Ch6 |
| 9 | Migration can be done in one cut | It is batching, rollback and acceptance | Ch5, Ch18 |
| 10 | A design is finished at go-live | Day 2 operations decide whether the design succeeds | Ch12, Ch14 |

<div class="zh" markdown="1">

| # | 易错认知 | 正确理解 | 出处 |
|---|---------|---------|------|
| 1 | 需求 = 用户说要什么 | 需求 = 测量后确认的现象。平均利用率看不见 3 秒突发 | 第 1 章 |
| 2 | 最佳实践可以直接套用 | 最佳实践有前提条件，不问前提就是缺陷 | 第 1、5 章 |
| 3 | RTO/RPO 写进方案就成立 | 没演练过的 RTO 是假设，实测通常是它的 2–3 倍 | 第 2、15 章 |
| 4 | 预算是 CAPEX | TCO 含迁移过渡期、5 年运维、培训、退役 | 第 2 章 |
| 5 | 视频会议"要带宽" | 要的是低丢包、低抖动、对称上行 | 第 3、14 章 |
| 6 | 上云是搬机器 | 上云是搬"距离"，chatty 应用会被 RTT 放大 | 第 3 章 |
| 7 | 加密 = 访问控制 | 加密只解决"看不见"，进不进得来靠认证授权 | 第 4、10 章 |
| 8 | 有框架就有架构 | 框架要裁剪到决策点，否则只是文档工程 | 第 5 章 |
| 9 | 二层服务"就像一个大局域网" | 它会把 LAN 的问题（广播、STP、MTU）原封搬到 WAN | 第 6 章 |
| 10 | 上了 EVPN 就自动更好 | 复杂度从数据面搬到控制面参数，参数不调反而更难预测 | 第 6、9 章 |
| 11 | STP 收敛是"秒级" | 取决于拓扑与调优；二层域范围 = 故障域范围 | 第 7、15 章 |
| 12 | 接口 ≥100M 的 cost 都合理 | 默认参考带宽下 cost 全是 1，1G 与 10G 被判等价 | 第 8 章 |
| 13 | 重分发可以长期用 | 必须 tag + route-map + AD 规划，长期应统一协议 | 第 8 章 |
| 14 | RT 配了就能通 | RT 决定导入/导出方向，还需 next-hop、SoO、汇总配合 | 第 9 章 |
| 15 | VXLAN ping 通就正常 | 文件传输卡死几乎总是 MTU/MSS | 第 9、10 章 |
| 16 | CoPP 套模板最省事 | 速率过低会掐死路由协议，表现为"部分不通" | 第 10 章 |
| 17 | 802.1X 可以直接上 Closed | 必须 Monitor → Low-Impact → Closed 三阶段 | 第 10 章 |
| 18 | 无线容量看 AP 数量 | 看信道规划、空间流、客户端能力、上行带宽与密度设计 | 第 11 章 |
| 19 | 自动化 = 选工具 | 先定约束与爆炸半径，工具是实现细节 | 第 12 章 |
| 20 | 组播三层配通就行 | 二层 IGMP Snooping/Querier 是"最后一公里" | 第 13 章 |
| 21 | QoS 配了就有效 | 需要标记信任边界 + 端到端一致 + 队列与限速匹配 | 第 14 章 |
| 22 | 双核心 = vPC/堆叠 | 本质是故障域与运维模型问题，不是技术选型问题 | 第 15 章 |
| 23 | 多宿主 = 高可用 | 入向不可控、状态不可复制，两条硬约束先讲清 | 第 16 章 |
| 24 | 选传输 = 设计 WAN | 流量矩阵、站点分级、运维能力、合同约束才是输入 | 第 17 章 |

</div>

---

## Design Flaws (Closing Edition: Bad Habits in Design Behaviour) · 设计缺陷（收尾版：设计行为上的坏习惯）

The flaws in the previous 17 chapters are **technical**. Here we add the **behavioural** ones — they appear in no configuration file, yet they destroy more projects than any protocol flaw.

<div class="zh" markdown="1">

前面 17 章的缺陷都是**技术层面**的。这里补上**行为层面**的——它们不写在配置里，但决定了方案质量：

</div>

| Flaw | Symptom | Consequence | Avoidance |
|------|---------|-------------|-----------|
| **Solution first** | A technology is chosen before requirements are clear | The requirement gets bent to fit the solution | Always answer "which requirement does it serve" first |
| **Documenting only the chosen option** | No record of rejected alternatives | The same debate repeats, decisions are not auditable | Record options, trade-offs and reasons for rejection |
| **Unstated assumptions** | "Everyone knows the carrier provides dual routes" | The assumption breaks and the design collapses | Write an explicit assumptions list |
| **Over-design for the future** | Rarely used capability at many times the complexity | Operational burden, more failure modes | Choose by growth evidence, not by imagination |
| **Optimism about convergence** | Never measured, only estimated | Fails the SLA at the first real failure | Long-ping acceptance tests |
| **Ignoring operations capability** | A design too complex for a 4-person team | It degrades after go-live | Manageability as a hard requirement |
| **Big-bang migration** | One change window, all sites at once | One failure takes down everything | Batch, with rollback per batch |
| **Accepting requirements at face value** | "We need Layer 2 between sites" taken literally | Expensive, fragile design | Ask what the real need behind the request is |
| **No rollback plan** | "It will work" | Longer outages when it does not | Define triggers and duration for every change |
| **Documentation as an afterthought** | Topology and configuration out of sync | Troubleshooting by guesswork | Tie documentation ownership to the change process |

<div class="zh" markdown="1">

| 缺陷 | 表现 | 后果 | 规避 |
|------|------|------|------|
| **只准备一个方案** | 评审时只有一套设计，"取舍"无从谈起 | 无法证明这是最优解，也无法应对需求变化 | 至少两个备选方案 + 明确的分界条件 |
| **从技术偏好倒推需求** | 先想用 SD-WAN，再找理由 | 方案华丽但解决的不是真问题 | 先写需求与约束，再选技术 |
| **把设计评审做成方案宣讲** | 只讲"我要做什么"，不讲"为什么不做别的" | 评审失去价值，风险留到实施阶段 | 评审必须包含：备选方案、被否决理由、风险与降级路径 |
| **忽视 Day 2** | 方案里没有监控、备份、变更流程 | 上线即失控，故障时长由"摸索时间"决定 | 每个设计交付物配一份运维要点（谁、多久、怎么验证） |
| **不做量化验收** | 验收标准是"能通" | 无法证明业务成果，也无法定位劣化 | 验收指标在 Day 0 定义，与业务方共同签字 |
| **过度设计 / 欠设计** | 200 人分部上双核心，或核心只做单机 | 前者浪费，后者一次故障就下线 | 用 RTO/RPO 与流量数据定规模，而不是"和总部一样" |
| **把"标准"当"正确"** | "集团标准就是这样" | 标准适用于总部，不一定适用于分部 | 标准是默认值，例外要有依据 |

</div>

> 💡 **The single most useful self-check**: **can you state three objections to your own design and answer each one?** If not, you have not finished designing.

<div class="zh" markdown="1">

> 💡 **最有效的一条自检**：**能不能自己说出三个反对这个方案的理由，并逐个回答？** 说不出，说明方案还没想透。

</div>

---

## Lessons Learned (Design and Review) · 实战经验总结（设计与评审）

| Lesson | Explanation |
|--------|-------------|
| **Be able to "tell the story" before you can "draw the diagram"** | If you cannot explain it in business language, the design is not yet clear |
| **Every decision needs a "why not"** | The reason for rejection is more valuable than the reason for selection |
| **Quantify before arguing** | Numbers end debates faster than seniority |
| **Put manageability in the requirements** | Otherwise it will be negotiated away at the end |
| **Keep the rollback path** | It is part of the design, not an emergency measure |
| **Review with an adversary** | Invite someone to break the design while it is still cheap |
| **Write down assumptions** | They are the most likely thing to change after go-live |
| **Day 2 is the design** | What matters is not go-live, but the three years after |

<div class="zh" markdown="1">

| 经验 | 说明 |
|------|------|
| **先能"讲"再能"背"** | 能用 3 句话把一个技术讲给非本专业同事听，比背完整特性表有效得多 |
| **按"层次"记，不按"章"记** | 章是书的组织方式，层是问题的组织方式。记忆负担差一个数量级 |
| **把案例当"条件反射"训练** | 看到现象先列 3 个可能根因（配置/设计/容量），再逐个排除，比"想当年见过"稳定 |
| **复盘要追到"哪一层的取舍没想清"** | 只记结论是无效的；找出背后的取舍逻辑才能真正迁移到新场景 |
| **评审先给约束，再给方案** | 先说清"在什么条件下"，方案才有说服力 |
| **写方案时把"放弃的方案"写进来** | 被否决理由是最有说服力的部分，也是后续变更的依据 |
| **交付物随方案一起交付** | 拓扑、决策表、验收用例、运维要点缺一项，方案就只完成了一半 |

</div>

---

## Extended Reading · 延伸阅读

### Foundations and Architecture · 基础与架构

| Resource | Description |
|----------|-------------|
| **This book** | CCDE 400-007 Official Cert Guide — the source for the whole set of notes |
| **RFC 1925** | The Twelve Networking Truths — worth rereading every year |
| **Cisco CVD / SRND** | Campus, WAN and security design guides — the source of many "best practices" |
| **TM Forum / ITIL** | The language of operations and service management |
| **NIST SP 800 series** | Security control frameworks (relevant to Chapter 4) |
| **MEF specifications** | The formal definitions behind Chapter 6's Carrier Ethernet attributes |

<div class="zh" markdown="1">

| 资源 | 说明 |
|------|------|
| **本书** | CCDE 400-007 Official Cert Guide |
| **CCDE 学习指南** | Marwan Al-Shawi 著，案例视角更贴近实战 |
| **Cisco CVD / 设计指南** | 经过验证的设计与规模边界 |
| **RFC** | 关键机制的权威定义 |

</div>

### Recommended RFCs · 推荐阅读的 RFC

| RFC | Title | Topic |
|-----|-------|-------|
| RFC 1918 | Address Allocation for Private Internets | Addressing |
| RFC 4271 | A Border Gateway Protocol 4 (BGP-4) | Inter-domain routing |
| RFC 2328 | OSPF Version 2 | Intra-domain routing |
| RFC 5301–5304 | IS-IS extensions | IS-IS |
| RFC 4760 | Multiprotocol Extensions for BGP-4 | MP-BGP |
| RFC 7432 | BGP MPLS-Based Ethernet VPN | EVPN |
| RFC 7348 | Virtual eXtensible Local Area Network (VXLAN) | Overlay |
| RFC 4601/7761 | PIM-SM / PIM-SSM | Multicast |
| RFC 5880/5881 | BFD | Fast failure detection |
| RFC 5798 | VRRP v3 | First-hop redundancy |

<div class="zh" markdown="1">

| RFC | 标题 | 主题 |
|-----|------|------|
| RFC 4364 | BGP/MPLS IP VPNs | L3VPN |
| RFC 4761/4762 | VPLS | L2VPN |
| RFC 7432 | BGP EVPN | EVPN |
| RFC 3916 | PWE3 Requirements | 伪线需求 |
| RFC 4577 | OSPF as PE-CE | OSPF VPN |
| RFC 2328 | OSPF v2 | OSPF |
| RFC 5340 | OSPF v3 | IPv6 OSPF |
| RFC 4271 | BGP-4 | BGP |
| RFC 1195 | IS-IS | IS-IS |
| RFC 7761 | PIM-SM | 组播 |
| RFC 8200 | IPv6 | IPv6 |
| RFC 4594 | QoS 服务类 | QoS 设计 |
| RFC 7348 | VXLAN | Overlay |

</div>

> 💡 **The right way to read an RFC**: do not read it end to end, but be able to answer "what problem does this mechanism solve, at what cost, and under what conditions does it fail". That is the level of understanding design work requires.

<div class="zh" markdown="1">

> 💡 **读 RFC 的正确姿势**：不必通读，但要能回答"这个机制解决什么问题、代价是什么"。先读 Introduction 与 Design Considerations 两节，通常就够了。

</div>

---

## Key Terms · 本章关键术语

| Term | Chinese meaning |
|------|-----------------|
| Business Driver | 业务驱动力 |
| Business Outcome / KPI | 业务成果 / 关键绩效指标 |
| Current-State Baseline | 现状基线 |
| Functional / Non-functional Requirement | 功能 / 非功能需求 |
| Constraint | 约束 |
| Failure Domain | 故障域 |
| Convergence Time | 收敛时间 |
| Rollback | 回滚 |
| Migration Roadmap | 迁移路线图 |
| Acceptance Criteria | 验收标准 |
| Manageability | 可管理性 |
| Total Cost of Ownership (TCO) | 总拥有成本 |
| Design Decision Table | 设计决策表 |
| Assumption | 假设 |
| Day 2 Operations | 运维阶段（上线之后） |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| Business-driven Design | 业务驱动设计 |
| Design Trade-off | 设计权衡 |
| Requirement Traceability | 需求可追溯性 |
| Design Review | 设计评审 |
| Day 2 Operations | 运维阶段（上线之后） |
| Failure Domain | 故障域 |
| Technical Debt | 技术债 |
| Baseline | 基线（现状与性能基准） |
| Migration Runbook | 迁移操作手册（含回退步骤） |

</div>

---

## Chapter Summary · 本章小结

Chapter 18 introduces no new knowledge; it supplies **a way to retrieve and an order to assemble**. The whole book compresses into three questions:

<div class="zh" markdown="1">

第 18 章不提供新知识，它提供**检索方式与装配顺序**。把全书压缩成三个问题：

</div>

| Question | Which part answers it | Test |
|----------|----------------------|------|
| Why do it? | Part I (Chapters 1–5) | Can you state the business outcome and its KPI |
| How? | Part II (Chapters 6–14) | Can you produce a decision table with reasons for rejection |
| In this scenario? | Part III (Chapters 15–17) | Can you map requirements onto a reference architecture |

<div class="zh" markdown="1">

| 问题 | 用哪一部分回答 | 判据 |
|------|--------------|------|
| **为什么做这件事？** | Part I（第 1–5 章） | 有没有可测的业务成果与约束清单 |
| **用什么技术做？** | Part II（第 6–14 章） | 能不能说清每个选择的代价与适用边界 |
| **在具体场景怎么组合？** | Part III（第 15–17 章） | 能不能按"边界 → 层次 → 路由 → 隔离 → 容量 → 验证"的顺序推进 |

</div>

Three closing recommendations:

<div class="zh" markdown="1">

三条收尾建议：

</div>

1. **Use the knowledge map for navigation, not memorisation.** In a project or a review, ask only "which layer is this", then go to that chapter.
2. **Use the seven steps as a checklist.** Any time you are stuck, look at which step you skipped.
3. **Use the mistake list to review yourself.** Especially the behavioural flaws — they are harder to see than technical ones.

<div class="zh" markdown="1">

1. **知识地图用来定位，不用来记忆**。做项目或评审时，只问"这属于哪一层"，然后去那一层找答案，比自己硬想快得多。
2. **缺陷清单用来防错，不用来背**。200+ 条缺陷的价值不在于记住，而在于评审时逐条对照。
3. **案例用来建立直觉**。真正把水平拉开的是"看到现象就能列出 3 个可能根因"，这只能靠案例积累。

</div>

> **One-line memory hook**: **design capability = making trade-offs under constraints, and being able to explain why.** All 18 chapters of this book circle around that one sentence.

<div class="zh" markdown="1">

> **一句话记忆**：**设计能力 = 在约束下做取舍，并能说清为什么。** 全书 18 章都在训练这一件事。

</div>

This completes all 18 chapters of notes. Go back to the home page to search by keyword, or browse the sidebar in Part order.

<div class="zh" markdown="1">

到这里，18 章笔记全部完成。回到首页用搜索框按关键词检索，或从侧边栏按 Part 顺序重读。

</div>
