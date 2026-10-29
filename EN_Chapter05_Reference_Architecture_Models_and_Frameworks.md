# Chapter 5: Reference Architecture Models and Frameworks · 第 5 章：参考架构模型与框架

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapter 5 (pp. 234–259)
>
> Terminology follows the English edition. Every English passage is followed by its Chinese counterpart in the grey block below it, so the two can be checked sentence by sentence.

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译 | 原书第 234-259 页

</div>

---

## Topics Covered · 本章涵盖主题

- **Reference architecture models and frameworks**: business architecture, enterprise architecture and the architecture frameworks in common use today

<div class="zh" markdown="1">

- **参考架构模型与框架**：业务架构、企业架构和当前常见的架构框架

</div>

---

## Chapter Overview: Why a Designer Needs "Borrowed Wisdom" · 本章导读：为什么设计师需要"借来的智慧"

The previous four chapters were about how to think — design mindset, business language, the purpose of the network, security. They answer questions of **direction**.

<div class="zh" markdown="1">

前四章讲的是"怎么想"——设计思维、业务语言、网络目的、安全。它们回答的是**方向**问题。

</div>

In a real project, however, you immediately hit an awkward question: **what makes you believe your design is right?**

<div class="zh" markdown="1">

但到了真实项目里，你会立刻遇到一个尴尬：**你凭什么认为自己的设计是对的？**

</div>

- A client says "we do enterprise architecture following TOGAF", and you must be able to hold up your end of the conversation
- Your boss asks "how do we justify this investment", and you need a shared language
- Your own "best practice" — what makes it "best"?

<div class="zh" markdown="1">

- 客户说"我们按 TOGAF 做的企业架构"，你要能接得上话
- 老板问"这个投资怎么证明合理"，你需要一套共同语言
- 你自己加的"最佳实践"，凭什么就是"最佳"？

</div>

Reference architectures, reference models and frameworks are the tools that solve this: **they turn pitfalls other people already fell into into reusable patterns**. You do not have to invent an architecture language from scratch; you only have to pick the right framework and then do the actual design inside its skeleton.

<div class="zh" markdown="1">

参考架构、参考模型、框架，就是解决这个问题的工具：**它们把别人踩过的坑整理成了可复用的句式**。你不用从零发明架构语言，只需选择合适的框架，然后在它的骨架里做具体设计。

</div>

> ⚠️ **The core attitude of this chapter (and it runs throughout)**: a framework is **scaffolding, not the building**. A framework tells you which dimensions to consider; it will never tell you whether to choose OSPF or EIGRP. What really counts is **whether you can make the right trade-offs inside those dimensions, given your business constraints**.

<div class="zh" markdown="1">

> ⚠️ **本章的核心态度（贯穿全章）**：框架是**脚手架**，不是**建筑**。框架告诉你需要考虑哪些维度，但不会告诉你选 OSPF 还是 EIGRP。真正见真章的是——你能不能在框架给的维度里，结合业务约束做出正确取舍。

</div>

---

## Three Concepts That Are Easy to Confuse · 三个容易混淆的概念

In practice and in documentation these three words are often used interchangeably, even though they sit at different levels:

<div class="zh" markdown="1">

实际工作和文档里，这三个词经常被混用，但它们层次不同：

</div>

| Concept | What it is | What it does | Examples |
|---------|------------|--------------|----------|
| **Reference model** | An abstract, layered **general framework** | Provides thinking dimensions and vocabulary | The OSI seven-layer model, the TCP/IP model |
| **Reference architecture** | A **structured template** for a class of scenarios | Provides a reusable design blueprint | Cisco SAFE, the layered campus architecture |
| **Framework** | Manages **process and methodology** | Provides the steps and governance for doing the work | TOGAF, ITIL, FEAF |

<div class="zh" markdown="1">

| 概念 | 英文 | 是什么 | 作用 | 举例 |
|------|------|--------|------|------|
| **参考模型** | Reference Model | 抽象的、分层的**通用框架** | 提供思考维度和术语 | OSI 七层模型、TCP/IP 模型 |
| **参考架构** | Reference Architecture | 针对某类场景的**结构化模板** | 提供可复用的设计蓝本 | Cisco SAFE 安全架构、园区网分层架构 |
| **框架** | Framework | 管理**流程与方法论** | 提供做事的步骤与治理 | TOGAF、ITIL、FEAF |

</div>

The relationship can be understood like this:

<div class="zh" markdown="1">

三者的关系可以这样理解：

</div>

```
Framework              → which process should I follow to do architecture? (HOW to do architecture)
    ↓ produces
Reference architecture → what does this class of scenario usually look like? (WHAT it looks like)
    ↓ referenced by
Reference model        → describe it with a common language and layering (HOW to describe it)
```

<div class="zh" markdown="1">

```
框架（Framework）      → 我该按什么流程做架构？（HOW to do architecture）
    ↓ 产出
参考架构（Ref. Arch.）  → 这类场景通常长什么样？（WHAT it looks like）
    ↓ 参考
参考模型（Ref. Model）  → 用统一的语言和分层来描述它（HOW to describe it）
```

</div>

> 💡 **The key distinction**: **TOGAF is a framework, not a reference architecture**. TOGAF will not tell you whether the data center should use spine-leaf or a three-tier design; it only tells you "align stakeholders with an architecture vision first, then do the technology architecture". This is one of the most common confusions.

<div class="zh" markdown="1">

> 💡 **关键区分**：**TOGAF 是框架，不是参考架构**。TOGAF 不会告诉你数据中心该用 spine-leaf 还是三层架构，它只告诉你"要先用架构愿景对齐利益相关者，再做技术架构"。这是最常见的混淆点之一。

</div>

---

<figure class="fig">
<img src="assets/fig/en05-01-three-concepts.svg" alt="Framework, reference architecture and reference model stacked by the question each one answers" loading="lazy">
<figcaption><b>Figure 5-1　Three concepts, three levels: a framework gives the process, a reference architecture gives the shape, a reference model gives the words</b><br><span>图 5-1　三个概念三个层级：框架给流程，参考架构给形态，参考模型给语言</span></figcaption>
</figure>

## Foundation Topics · 基础内容

> How do you know the option you chose from a network design perspective is viable? Are you making the right network design decisions? How do you define the word "architecture"? Who defines your architecture?

<div class="zh" markdown="1">

> 你如何知道从网络设计角度选择的是可行的？你在做正确的网络设计决策吗？你如何定义"架构"这个词？谁定义你的架构？

</div>

This is where reference architectures, models and frameworks come in. They help guide your decisions by drawing on different aspects of the organization, so you can determine the right direction for the business.

<div class="zh" markdown="1">

这就是参考架构、模型和框架发挥作用的地方。它们通过利用组织的不同方面来帮助指导你的决策，以确定业务的正确前进方向。

</div>

---

## Business Architecture (BA) · 业务架构

Business architecture puts everyone from the strategic planning team to the implementation team "on the same page", so they can meet challenges and achieve business goals.

<div class="zh" markdown="1">

业务架构使从战略规划团队到实施团队的每个人都能"在同一页上"，使他们能够应对挑战并实现业务目标。

</div>

### Core Concepts · 核心概念

| Concept | Definition |
|---------|------------|
| **Business solution** | A set of interacting business capabilities that delivers one or more business outcomes |
| **Business outcome** | A measurable result of an activity, process or event in the business, following the SMART principle |

<div class="zh" markdown="1">

| 概念 | 定义 |
|------|------|
| **业务解决方案 (Business Solution)** | 一组交互的业务能力，交付一个或多个业务成果 |
| **业务成果 (Business Outcome)** | 业务中活动、流程或事件的可衡量结果，遵循 SMART 原则 |

</div>

**The SMART principle** (the test for whether a business outcome is acceptable):

<div class="zh" markdown="1">

**SMART 原则**（衡量业务成果是否合格的标准）：

</div>

| Letter | Meaning | Counter-example (an unacceptable outcome) |
|--------|---------|------------------------------------------|
| **S**pecific | Concrete | "Improve the network experience" |
| **M**easurable | Quantifiable | "Make the network faster" |
| **A**chievable | Attainable | "Achieve zero failures" |
| **R**elevant | Tied to business goals | A purely technical metric unrelated to any business goal |
| **T**ime-bound | Has a deadline | "Done some day in the future" |

<div class="zh" markdown="1">

| 字母 | 含义 | 反例（不合格的成果） |
|------|------|-------------------|
| **S**pecific | 具体 | "提升网络体验" |
| **M**easurable | 可衡量 | "让网络更快" |
| **A**chievable | 可实现 | "做到零故障" |
| **R**elevant | 相关 | 与业务目标无关的纯技术指标 |
| **T**ime-bound | 有时限 | "未来某天完成" |

</div>

**Examples of business outcomes** (from real production environments — note that each one satisfies SMART):

<div class="zh" markdown="1">

**业务成果示例**（真实生产环境，注意每条都符合 SMART）：

</div>

- Increase same-day order shipments by 20% before Q1
- Raise customer lifetime value by 10% within 24 months
- Shorten new product time to market by 25% before Q3
- Grow sales by 10% this fiscal year
- Improve delivery efficiency by 25% this fiscal year

<div class="zh" markdown="1">

- Q1 前将当日订单发货量增加 20%
- 24 个月内将客户终身价值提高 10%
- Q3 前将新产品上市时间缩短 25%
- 本财年销售额增长 10%
- 本财年交付效率提高 25%

</div>

> ⚠️ **A common trap**: if a "requirement" in a scenario does not satisfy SMART, you must **go back and clarify it with the business**, rather than inventing a measurable version yourself. A design requirement that cannot be verified means a project that cannot be accepted.

<div class="zh" markdown="1">

> ⚠️ **常见陷阱**：场景里给你的"需求"如果不满足 SMART，你必须**回头向业务方澄清**，而不是自己脑补一个可测量的版本。设计需求无法验证 = 项目无法验收。

</div>

<figure class="fig">
<img src="assets/fig/en05-02-smart-gate.svg" alt="Interacting capabilities forming a business solution and delivering a business outcome, with SMART as the acceptance test" loading="lazy">
<figcaption><b>Figure 5-2　A business solution is judged by the outcome it moves, and SMART is the test that makes the claim checkable</b><br><span>图 5-2　业务解决方案由成果评判，SMART 是让成果可被验证的闸门</span></figcaption>
</figure>

### The Four Alignment Levels of Business Architecture · 业务架构的四个对齐级别

This is the first key model in the chapter — **the demands business places on architecture rise level by level with maturity**:

<div class="zh" markdown="1">

这是本章第一个重点模型——**业务对架构的诉求会随成熟度逐级上升**：

</div>

| Level | Type | Description | The designer's deliverable |
|-------|------|-------------|----------------------------|
| **Technology specific** | Domain-specific architecture | The business needs the right product inside one architecture domain (data center, security or enterprise network), without crossing domains | Product recommendations, comparisons |
| **Technology architecture** | Multi-domain architecture (MDA) | The business needs to understand the value of a multi-domain technology architecture. Two or more domains are involved | Cross-domain integration design |
| **Business solutions** | Partial business architecture | The business needs help solving a business problem and measuring the impact of the technology investment (CAPEX, OPEX, ROI, TCO) | Business case, decision matrix |
| **Business transformation** | Business-led architecture | The business needs help transforming business capabilities to drive innovation and accelerate digitalization | Roadmap, evolution plan |

<div class="zh" markdown="1">

| 级别 | 类型 | 说明 | 设计师的产出 |
|------|------|------|------------|
| **技术特定 (Technology Specific)** | 领域特定架构 | 业务需要在某个架构领域（数据中心、安全或企业网络）内找到合适的产品，不跨领域 | 选型建议、产品对比 |
| **技术架构 (Technology Architecture)** | 多领域架构 (MDA) | 业务需要理解多领域技术架构的价值。两个或更多架构领域被纳入 | 跨域整合方案 |
| **业务解决方案 (Business Solutions)** | 部分业务架构 | 业务需要帮助解决业务问题并衡量技术投资的影响 (CAPEX, OPEX, ROI, TCO) | 商业论证、决策矩阵 |
| **业务转型 (Business Transformation)** | 业务主导的架构 | 业务需要帮助转变业务能力以促进创新，加速公司数字化 | 路线图、演进规划 |

</div>

**The progression logic across the four levels**:

<div class="zh" markdown="1">

**四个级别的递进逻辑**：

</div>

```
Technology specific → only "what do we buy in this domain"
     ↓ add more domains
Technology architecture → "how do multiple domains work together"
     ↓ add money and return
Business solutions → "is this money well spent"
     ↓ add business change
Business transformation → "how does IT change the way the company does business"
```

<div class="zh" markdown="1">

```
技术特定 → 只看"这个域里买什么"
     ↓ 加入更多域
技术架构 → 看"多个域怎么协同"
     ↓ 加入钱和收益
业务解决方案 → 看"这钱花得值不值"
     ↓ 加入业务变革
业务转型 → 看"IT 如何改变公司做生意的方式"
```

</div>

> 💡 **A useful test**: if a scenario mentions **ROI / TCO / CAPEX discussions**, it has risen to the "business solutions" level; if it mentions "entering a new market" or "digital strategy", it is "business transformation". The design freedom of the two is completely different — a transformation project may legitimately overturn the existing architecture.

<div class="zh" markdown="1">

> 💡 **判断技巧**：看到场景里出现 **ROI / TCO / CAPEX 讨论**，说明已经上升到"业务解决方案"级别；如果出现"进入新市场""数字化战略"，就是"业务转型"。这两类的设计自由度完全不同——转型类项目允许你推翻现有架构。

</div>

<figure class="fig">
<img src="assets/fig/en05-03-alignment-levels.svg" alt="The four alignment levels as rising steps, each with its trigger and its deliverable" loading="lazy">
<figcaption><b>Figure 5-3　Four alignment levels: the business asks for more with each step, and the trigger tells you which step a scenario sits on</b><br><span>图 5-3　四个对齐级别：每上一层业务要求更高，触发词决定落在哪一层</span></figcaption>
</figure>

### Business Architecture Guiding Principles · 业务架构指导原则

Combining the guiding principles of TOGAF and ITIL, business architecture needs to cover **nine architecture perspectives**:

<div class="zh" markdown="1">

结合 TOGAF 和 ITIL 的指导原则，业务架构需要覆盖**九个架构视角**：

</div>

| Principle | Description |
|-----------|-------------|
| **Strategy and vision** | Align architecture capability with business goals and outcomes |
| **Business architecture** | Stay consistent with the business model and market/industry perspective |
| **Application architecture** | Coexist with hybrid cloud models and support three-tier/N-tier standards |
| **Technology architecture** | Support automation, configuration, orchestration, analytics and telemetry |
| **Infrastructure architecture** | Support data center, cloud, collaboration, security, SASE, enterprise network and IoT |
| **Physical architecture** | Support compute, storage and virtualization |
| **Data architecture** | Support business intelligence, data integration, data security, data management and operations |
| **Operations architecture** | Support ITIL service capability and align Day 0, Day 1 and Day 2 management services |
| **Architecture governance** | Support the architecture management office and align the plan, design, implement and operate lifecycle |

<div class="zh" markdown="1">

| 原则 | 说明 |
|------|------|
| **战略和愿景** | 将架构能力与业务目标和成果对齐 |
| **业务架构** | 与业务模型和市场/行业视角一致 |
| **应用架构** | 与混合云模型共存，支持三层/N 层架构标准 |
| **技术架构** | 支持自动化、配置、编排、分析和遥测能力 |
| **基础设施架构** | 支持数据中心、云、协作、安全、SASE、企业网络和 IoT |
| **物理架构** | 支持计算、存储和虚拟化 |
| **数据架构** | 支持商业智能、数据集成、数据安全、数据管理和运营 |
| **运营架构** | 支持 ITIL 服务能力，对齐 Day 0、Day 1、Day 2 管理服务 |
| **架构治理** | 支持架构管理办公室服务，对齐规划、设计、实施、运营生命周期 |

</div>

> ⚠️ **Note the Day 0/1/2 split**, which is extremely common in operations discussions:
> - **Day 0**: planning and design (not live yet)
> - **Day 1**: deployment and provisioning (the moment it goes live)
> - **Day 2**: day-to-day operations and change (the long running period)
>
> Many designs fail not because Day 0 was designed wrong, but because **Day 2 operational cost was never considered** (for example configuration so complex that human changes cause outages).

<div class="zh" markdown="1">

> ⚠️ **注意"Day 0/1/2"这个划分**——它是运维讨论中非常常见的划分：
> - **Day 0**：规划与设计（还没上线）
> - **Day 1**：部署与开通（上线那一刻）
> - **Day 2**：日常运维与变更（长期运行）
>
> 很多设计失败不是 Day 0 设计错了，而是**没有考虑 Day 2 的运维成本**（比如配置太复杂导致人为变更故障）。

</div>

<figure class="fig">
<img src="assets/fig/en05-04-nine-perspectives.svg" alt="The nine architecture perspectives in a grid above the Day 0, Day 1 and Day 2 split" loading="lazy">
<figcaption><b>Figure 5-4　Nine perspectives, one architecture: skip the first or the last and the design has a blind side</b><br><span>图 5-4　九个架构视角与 Day 0/1/2 切分：忽略两端就会留下盲区</span></figcaption>
</figure>

### Key Performance Indicators (KPIs) · 关键绩效指标

How do you know whether a framework or reference architecture succeeded? You measure it with KPIs:

<div class="zh" markdown="1">

如何知道某个框架或参考架构是否成功？需要通过 KPI 来衡量：

</div>

- IT CAPEX and OPEX reduced by x%
- Time to market and business agility improved by x%
- Time to launch new IT services reduced by x%
- Security operations MTTD reduced from x days to x hours
- Security operations MTTR reduced from x days to x hours
- Business ROI contributed to IT solutions

<div class="zh" markdown="1">

- IT CAPEX 和 OPEX 降低 x%
- 上市速度和业务敏捷性提高 x%
- 新 IT 服务上市时间减少 x%
- 安全运维 MTTD 从 x 天降到 x 小时
- 安全运维 MTTR 从 x 天降到 x 小时
- 业务 ROI 贡献于 IT 解决方案

</div>

> 💡 **MTTD and MTTR** (these come up constantly in security and availability scenarios):
> - **MTTD** (mean time to detect) measures **visibility** capability, and depends on traffic analysis, logs and NetFlow
> - **MTTR** (mean time to repair/recover) measures **resilience** capability, and depends on redundancy, fast convergence and automation
>
> To improve MTTD in a design you add monitoring points; to improve MTTR you add redundancy and improve convergence. These are two completely different design paths.

<div class="zh" markdown="1">

> 💡 **MTTD 与 MTTR**（安全与可用性场景必考）：
> - **MTTD**（Mean Time To Detect，平均检测时间）→ 衡量**可见性**能力，靠流量分析、日志、NetFlow
> - **MTTR**（Mean Time To Repair/Recover，平均修复时间）→ 衡量**弹性**能力，靠冗余、快速收敛、自动化
>
> 设计里想改善 MTTD，就得加监测点；想改善 MTTR，就得加冗余和收敛优化。这是两条完全不同的设计路径。

</div>

---

<figure class="fig">
<img src="assets/fig/en05-05-kpi-mttd-mttr.svg" alt="From business goal to IT capability to one board-readable number, then the different design paths behind MTTD and MTTR" loading="lazy">
<figcaption><b>Figure 5-5　From business goal to a number the board can read, and why MTTD and MTTR buy completely different things</b><br><span>图 5-5　从业务目标到能上报的数字：MTTD 买可见性，MTTR 买弹性</span></figcaption>
</figure>

## Enterprise Architecture (EA) · 企业架构

Enterprise architecture is the process of organizing business processes and IT infrastructure logic, reflecting the integration and standardization requirements of the company's operating model.

<div class="zh" markdown="1">

企业架构是组织业务流程和 IT 基础设施逻辑的过程，反映公司运营模型的集成和标准化要求。

</div>

**In one sentence**: business architecture focuses on "what the business must achieve", while enterprise architecture focuses on "how the whole enterprise's IT is organized to support that".

<div class="zh" markdown="1">

**一句话理解**：业务架构关注"业务要做成什么"，企业架构关注"整个企业的 IT 怎么组织起来支撑它"。

</div>

**Business benefits of enterprise architecture**:

<div class="zh" markdown="1">

**企业架构的业务收益**：

</div>

- Respond to new market opportunities
- Justify investment
- Reduce cost (CAPEX and OPEX)
- Improve quality

<div class="zh" markdown="1">

- 响应新市场机会
- 证明投资的合理性
- 降低成本 (CAPEX 和 OPEX)
- 提高质量

</div>

### Enterprise Architecture Methodology Steps · 企业架构方法论步骤

1. **Identify business requirements** — by aligning stakeholders and determining the operating model
2. **Align stakeholders** — four groups of stakeholders:
   - IT steering committee (architecture management office, vendor-neutral team, senior management)
   - Architects (business architects, technology architects, enterprise architects)
   - Finance and procurement (CFO, procurement team, supplier relationships)
   - Enterprise-level process owners (functional owners, user groups, business unit leaders)
3. **Identify the operating model**

<div class="zh" markdown="1">

1. **识别业务需求** — 通过对齐利益相关者和确定运营模型
2. **对齐利益相关者** — 四组利益相关者：
   - IT 指导委员会（架构管理办公室、厂商无关团队、高级管理层）
   - 架构师（业务架构师、技术架构师、企业架构师）
   - 财务和采购（CFO、采购团队、供应商关系）
   - 企业级流程负责人（各部门负责人、用户组、业务单元领导）
3. **识别运营模型**

</div>

> ⚠️ **The order cannot be rearranged**: business requirements come first, then stakeholder alignment, then the operating model. Doing it the other way round (fixing the operating model first and hunting for requirements afterwards) is the classic **bottom-up** error that Chapter 1 already criticised.
> 💡 **The "vendor-neutral team" role is worth noting**: it exists precisely to prevent the vendor lock-in constraint from Chapter 1. When a scenario says "must support multiple vendors" or "cannot be bound to a single supplier", the organization probably has such a governance role.

<div class="zh" markdown="1">

> ⚠️ **顺序不能乱**：先有业务需求，才能对齐人，才能定运营模型。反过来（先定运营模型再找需求）就是典型的**自底向上**错误——第 1 章已经明确批判过。
> 💡 **"厂商无关团队"这个角色值得注意**：它的存在就是为了防止第 1 章讲的"厂商锁定"约束。当场景里出现"必须支持多厂商"或"不能绑定单一供应商"时，说明组织里可能存在这样一个治理角色。

</div>

<figure class="fig">
<img src="assets/fig/en05-06-ea-method-steps.svg" alt="The three enterprise architecture method steps in fixed order with the four stakeholder groups beneath" loading="lazy">
<figcaption><b>Figure 5-6　Three steps in one order: requirements, then the people who must agree, then the operating model</b><br><span>图 5-6　EA 方法论三步与四类干相人：顺序不能颠倒</span></figcaption>
</figure>

### Operating Model Types (a core model) · 运营模型类型（核心模型）

The operating model determines **the degree of standardization and integration inside the enterprise** — this is the classic MIT four-quadrant model, positioned on two dimensions:

<div class="zh" markdown="1">

运营模型决定了**企业内部的标准化程度和集成程度**，这是 MIT 经典的四象限模型。用两个维度来定位：

</div>

- **Standardization**: are business processes and systems unified
- **Integration**: do business units share data with each other

<div class="zh" markdown="1">

- **标准化 (Standardization)**：业务流程和系统是否统一
- **集成 (Integration)**：业务单元之间是否共享数据

</div>

```
                          Integration high
                                 ↑
   Coordination        |        Unification
   (low std / high int)|     (high std / high int)
  ─────────────────────┼──────────────────────→ Standardization high
   Diversification     |        Replication
   (low std / low int) |     (high std / low int)
                                 ↓
                          Integration low
```

<div class="zh" markdown="1">

```
        集成度 高
             ↑
   协调型     |     统一型
 Coordination|   Unification
 (低标/高集) |   (高标/高集)
  ───────────┼───────────→ 标准化 高
   多样化型   |     复制型
 Diversification| Replication
 (低标/低集) |   (高标/低集)
             ↓
        集成度 低
```

</div>

| Type | Characteristics | Standardization | Integration | Network design implication |
|------|-----------------|-----------------|-------------|----------------------------|
| **Coordination** | High integration, low standardization. Data is shared across units. Business units innovate | Low | High | Needs flexible east-west connectivity and cross-domain data sharing (DCI, flexible SD-WAN policy) |
| **Unification** | Centralized management and process design. Centralized databases and IT organization | High | High | Centralized architecture, unified policy, strong governance; standardized templates land most easily |
| **Diversification** | Independence plus shared services. Few shared customers or business practices. Shared IT services for economies of scale | Low | Low | Each unit builds its own network plus a few shared services (for example a shared Internet egress) |
| **Replication** | Business units autonomous. Operations run in a standardized way. Learning is shared but operations are independent | High | Low | Standardized templates replicated per branch, each site operating independently (typical of chains) |

<div class="zh" markdown="1">

| 类型 | 特点 | 标准化 | 集成 | 网络设计含义 |
|------|------|--------|------|------------|
| **协调型 (Coordination)** | 高集成、低标准化。数据跨组合共享。业务单元发布创新 | 低 | 高 | 需要灵活的东西向连通、跨域数据共享（数据中心互联、SD-WAN 灵活策略） |
| **统一型 (Unification)** | 集中管理和流程设计。集中化数据库和 IT 组织 | 高 | 高 | 集中式架构、统一策略、强治理；标准化模板最容易落地 |
| **多样化型 (Diversification)** | 独立性 + 共享服务。少量共同客户或业务实践。共享 IT 服务以实现规模经济 | 低 | 低 | 各业务单元独立建网 + 少量共享服务（如共享互联网出口） |
| **复制型 (Replication)** | 业务单元自治。运营以标准化方式运行。共享学习但独立运营 | 高 | 低 | 分支/多站点标准化模板复制，每个站点独立运营（典型连锁企业） |

</div>

> ⚠️ **This is the model most likely to be tested in this chapter**. To place a scenario, answer two questions:
> 1. "Do the business units do things the same way?" → yes = high standardization
> 2. "Do the business units need to share data or interact frequently?" → yes = high integration
>
> Once the quadrant is known, the network design direction is essentially fixed: high standardization → templates, automation and unified policy; high integration → high-bandwidth east-west, cross-domain security policy and low-latency interconnect.

<div class="zh" markdown="1">

> ⚠️ **这是本章最容易被考到的模型**。判断技巧：抓住两个问题的答案——
> 1. "各业务单元做事情的方式一样吗？" → 一样 = 高标准化
> 2. "业务单元之间要共享数据/频繁交互吗？" → 要 = 高集成
>
> 得到象限后，网络设计方向基本就定了：高标准化 → 模板化、自动化、统一策略；高集成 → 高带宽东西向、跨域安全策略、低延迟互联。

</div>

---

<figure class="fig">
<img src="assets/fig/en05-07-operating-model.svg" alt="The four operating model quadrants on standardisation and integration with the design direction each one implies" loading="lazy">
<figcaption><b>Figure 5-7　Four operating models, and the network each one actually needs</b><br><span>图 5-7　四种运营模型与它们各自需要的网络</span></figcaption>
</figure>

## Common Enterprise Architecture Frameworks · 常见企业架构框架

### TOGAF (The Open Group Architecture Framework)

TOGAF is an enterprise architecture methodology containing a high-level, enterprise-oriented framework focused on designing, planning, implementing and governing enterprise IT architecture.

<div class="zh" markdown="1">

TOGAF 是一种企业架构方法论，包含面向企业的高层框架，专注于企业 IT 架构的设计、规划、实施和治理。

</div>

**The eight phases of the TOGAF Architecture Development Method (ADM)** (note that it is an **iterative cycle**, not a waterfall):

<div class="zh" markdown="1">

**TOGAF 架构开发方法 (ADM) 的 8 个步骤**（注意是**迭代循环**，不是瀑布）：

</div>

| Phase | Name | Description | Key output |
|-------|------|-------------|------------|
| **A** | Architecture vision | Define project scope, stakeholders and business goals | Architecture vision document |
| **B** | Business architecture | Develop the baseline and target business architecture | Baseline/target business architecture |
| **C** | Information systems architecture | Develop the baseline and target data and application architectures | Data and application architectures |
| **D** | Technology architecture | Develop the baseline and target technology architecture | **The network design lands here** |
| **E** | Opportunities and solutions | Perform gap analysis and define solutions | Gap analysis, work packages |
| **F** | Migration planning | Build the implementation and migration plan | Migration roadmap |
| **G** | Implementation governance | Provide implementation oversight | Compliance checks |
| **H** | Architecture change management | Manage architecture change | Change requests |

<div class="zh" markdown="1">

| 步骤 | 名称 | 说明 | 关键产出 |
|------|------|------|---------|
| **A** | 架构愿景 | 定义项目范围、利益相关者、业务目标 | 架构愿景文档 |
| **B** | 业务架构 | 开发基线和目标业务架构 | 基线/目标业务架构 |
| **C** | 信息系统架构 | 开发基线和目标数据和应用架构 | 数据+应用架构 |
| **D** | 技术架构 | 开发基线和目标技术架构 | **网络设计在这里落地** |
| **E** | 机会和解决方案 | 进行差距分析，制定解决方案 | 差距分析、工作包 |
| **F** | 迁移规划 | 制定实施和迁移计划 | 迁移路线图 |
| **G** | 实施治理 | 提供实施监督 | 合规检查 |
| **H** | 架构变更管理 | 管理架构变更 | 变更请求 |

</div>

**Understanding the ADM structure**:

<div class="zh" markdown="1">

**ADM 的结构理解**：

</div>

```
        ┌──────── requirements management (throughout) ────────┐
        │                                                       │
   A vision → B business → C information systems → D technology → E solutions → F migration → G governance → H change
                                            ↑                                          │
                                            └──────────────────────────────────────────┘
                                                     back to A, iterate
```

<div class="zh" markdown="1">

```
        ┌──────── 需求管理（贯穿始终）────────┐
        │                                      │
   A 愿景 → B 业务 → C 信息系统 → D 技术 → E 解决方案 → F 迁移 → G 治理 → H 变更
                                          ↑                              │
                                          └──────────────────────────────┘
                                                  回到 A，迭代
```

</div>

> 💡 **Two points you must remember**:
> 1. **The ADM is cyclical** (A→H→back to A), which is why architecture can evolve with the business
> 2. **"Requirements management" spans every phase** — which confirms the core point from Chapter 1: requirements are not gathered once and finished, they are maintained continuously
>
> For a network designer, **phase D (technology architecture) is your home ground**, but you must be able to trace back to the business and information architecture of phases B and C, otherwise the design has no basis — that is what "top-down" means.

<div class="zh" markdown="1">

> 💡 **两个必记要点**：
> 1. **ADM 是循环的**（A→H→回到 A），因此架构能随业务变化演进
> 2. **"需求管理"横跨所有阶段**——这正好印证第 1 章的核心观点：需求不是一次性收集完的，而是持续维护的
>
> 对网络设计师来说，**D 阶段（技术架构）是你的主场**，但你必须能追溯到 B/C 阶段的业务与信息架构，否则设计就没有依据——这就是"自顶向下"。

</div>

<figure class="fig">
<img src="assets/fig/en05-08-togaf-adm.svg" alt="The eight TOGAF ADM phases on a ring around requirements management, with phase D marked as the designer's home ground" loading="lazy">
<figcaption><b>Figure 5-8　TOGAF ADM as a ring: phase D is where network design lands, and A to C are what keep it from landing on nothing</b><br><span>图 5-8　TOGAF ADM 循环：D 阶段是网络设计的落点，A–C 是它的依据</span></figcaption>
</figure>

### ITIL (Information Technology Infrastructure Library)

ITIL is a set of best-practice processes for IT service management.

<div class="zh" markdown="1">

ITIL 是一组 IT 服务管理的最佳实践流程。

</div>

**The ITIL service lifecycle**:

<div class="zh" markdown="1">

**ITIL 服务生命周期**：

</div>

| Stage | Description |
|-------|-------------|
| **Service strategy** | Defines the business value and policy of IT services |
| **Service design** | Designs new or changed IT services |
| **Service transition** | Moves services from design into production |
| **Service operation** | Manages the day-to-day operation of IT services |
| **Continual service improvement** | Continuously improves IT service quality and performance |

<div class="zh" markdown="1">

| 阶段 | 说明 |
|------|------|
| **服务策略** | 定义 IT 服务的业务价值和策略 |
| **服务设计** | 设计新的或变更的 IT 服务 |
| **服务转换** | 将服务从设计过渡到生产 |
| **服务运营** | 管理 IT 服务的日常运营 |
| **持续服务改进** | 持续改进 IT 服务质量和性能 |

</div>

> 💡 **TOGAF vs. ITIL** (learn them as a pair):
>
> | Dimension | TOGAF | ITIL |
> |-----------|-------|------|
> | Focus | How to build **architecture** (planning) | How to deliver **services** (operations) |
> | Timeline | Day 0 (design and planning) | Day 1 and Day 2 (delivery and operations) |
> | Key outputs | Architecture blueprint, roadmap | SLAs, change processes, incident management |
>
> In real projects the two complement each other: TOGAF decides "what to build", ITIL ensures "it is delivered stably once built".

<div class="zh" markdown="1">

> 💡 **TOGAF vs ITIL**（对比记忆）：
>
> | 维度 | TOGAF | ITIL |
> |------|-------|------|
> | 关注点 | **架构**怎么建（规划层面） | **服务**怎么交付（运营层面） |
> | 时间轴 | Day 0（设计与规划） | Day 1、Day 2（交付与运维） |
> | 关键输出 | 架构蓝图、路线图 | SLA、变更流程、事件管理 |
>
> 实际项目里两者互补：TOGAF 决定"建什么"，ITIL 保证"建好后能稳定交付"。

</div>

<figure class="fig">
<img src="assets/fig/en05-09-itil-and-togaf-split.svg" alt="The five ITIL service lifecycle stages looping back through continual improvement, and how ITIL divides work with TOGAF" loading="lazy">
<figcaption><b>Figure 5-9　ITIL covers the half of the lifecycle TOGAF stops short of: one decides the shape, the other whether it can be run</b><br><span>图 5-9　ITIL 与 TOGAF 的分工：一个定形态，一个定能不能跑得下去</span></figcaption>
</figure>

### Other Frameworks · 其他框架

| Framework | Description | Where it applies |
|-----------|-------------|------------------|
| **FEAF (Federal Enterprise Architecture Framework)** | The US federal enterprise architecture framework | Government and public sector |
| **DODAF (Department of Defense Architecture Framework)** | The US Department of Defense architecture framework | Defence and high-security environments |
| **RMF (Risk Management Framework)** | Risk management framework | Compliance and risk-driven design |

<div class="zh" markdown="1">

| 框架 | 说明 | 适用场景 |
|------|------|---------|
| **FEAF (Federal Enterprise Architecture Framework)** | 美国联邦企业架构框架 | 政府/公共部门 |
| **DODAF (Department of Defense Architecture Framework)** | 美国国防部架构框架 | 国防、强安全要求场景 |
| **RMF (Risk Management Framework)** | 风险管理框架 | 合规、风险驱动的设计 |

</div>

> These three usually appear only as background knowledge; understanding **the domain each one applies to** is enough, and there is no need to memorize their sub-steps.

<div class="zh" markdown="1">

> 这三个框架通常只作为"背景知识"出现，理解它们的**适用领域**即可，不需要记住细分步骤。

</div>

---

## From Frameworks to Network Reference Architectures · 从框架到网络参考架构

Frameworks are generic, but network design needs concrete blueprints. The network reference architectures commonly used in the industry include:

<div class="zh" markdown="1">

框架是通用的，但网络设计需要具体的蓝本。业界常见的网络参考架构包括：

</div>

| Reference architecture | Scope | Problem it solves |
|------------------------|-------|-------------------|
| **Cisco SAFE** | Security architecture | Security domain design and chokepoint placement (the subject of Chapter 4) |
| **Cisco Validated Design (CVD)** | Validated designs per domain | Tested configuration baselines and scale boundaries |
| **Layered campus architecture** | Campus network | Modularity and fault isolation across core/distribution/access |
| **Enterprise WAN / SD-WAN architecture** | Wide area network | Transport selection, topology, centralized policy |
| **Data center spine-leaf** | Data center | East-west scalability and low latency |

<div class="zh" markdown="1">

| 参考架构 | 覆盖范围 | 解决的问题 |
|---------|---------|-----------|
| **Cisco SAFE** | 安全架构 | 安全域划分、检查点部署位置（对应第 4 章） |
| **Cisco Validated Design (CVD)** | 各领域验证设计 | 提供经过测试的配置基线与规模边界 |
| **园区分层架构** | 园区网 | 核心/分布/接入的模块化与故障隔离 |
| **企业 WAN / SD-WAN 架构** | 广域网 | 传输选型、拓扑、策略中心化 |
| **数据中心 Spine-Leaf** | 数据中心 | 东西向流量的可扩展性与低延迟 |

</div>

> ⚠️ **A critical judgement**: a reference architecture tells you "how it is usually done", but **it does not carry your constraints**. If a scenario contains special constraints (an extremely tight budget, a legacy system that cannot be touched, compliance requiring data to stay in country), you must **deviate from the reference architecture deliberately and be able to explain why**. Citing "that is how the reference architecture does it" as your design rationale is the classic "best practice trap" from Chapter 1.

<div class="zh" markdown="1">

> ⚠️ **关键判断**：参考架构给你"通常怎么做"，但**它不承担你的约束**。如果场景里出现特殊约束（预算极紧、遗留系统不能动、合规要求数据不出境），你必须**有意识地偏离参考架构，并说得出理由**。拿"参考架构就是这么做的"当作设计依据，是最典型的第 1 章"最佳实践陷阱"。

</div>

---

<figure class="fig">
<img src="assets/fig/en05-10-frameworks-to-reference-arch.svg" alt="Frameworks feeding reference architectures, and the column of constraints that no reference architecture carries" loading="lazy">
<figcaption><b>Figure 5-10　Frameworks give the process, reference architectures give the shape, and only you can supply the constraints</b><br><span>图 5-10　框架给流程、参考架构给形态，约束只能自己补</span></figcaption>
</figure>

## Case Studies · 实战案例

### Case 1: A Bank "Moves to the Cloud" — Phase A Cannot Be Skipped · 案例一：银行"上云"——A 阶段不能跳

**Background**: the business side of a city commercial bank proposed "move the core business to the cloud within two years". The architecture team went straight to technology selection: private or public cloud, which SDN vendor, VXLAN or EVPN.

<div class="zh" markdown="1">

**背景**：某城商行业务部门提出"两年内核心业务上云"，架构团队直接开始做技术选型：私有云还是公有云、SDN 用哪家、VXLAN 还是 EVPN。

</div>

**The problem**: after four months of work, the CFO asked three questions in the review meeting —
1. "Once we are in the cloud, how much does each transaction cost us less?"
2. "How many weeks does go-live get shorter?"
3. "If we do not move to the cloud, what do we lose?"

<div class="zh" markdown="1">

**问题**：方案做了四个月，评审会上 CFO 问了三个问题——
1. "上云之后，我们的每笔交易成本降多少？"
2. "上线时间缩短几周？"
3. "如果不上云，会损失什么？"

</div>

The architecture team could not answer. **Because phase A (architecture vision) and phase B (business architecture) had never been done**, they jumped straight to D (technology architecture).

<div class="zh" markdown="1">

架构团队答不出来。因为**从来没有做过 A 阶段（架构愿景）和 B 阶段（业务架构）**，直接跳到了 D（技术架构）。

</div>

**After redoing it in TOGAF, the real pain point emerged**: it was not "we have not moved to the cloud", it was "a new business launch averages eleven weeks, while competitors take three" — and six of those weeks were spent **requesting network resources**.

<div class="zh" markdown="1">

**回到 TOGAF 重做后才发现**：真实的业务痛点不是"没上云"，而是"新业务上线平均要 11 周，竞品只要 3 周"，其中 6 周花在**申请网络资源**上。

</div>

**The genuinely effective solution**: not a wholesale move to the cloud, but **self-service network resource requests plus automated provisioning** (Chapter 12), compressing the six weeks to two days. Results in three months, at one tenth of the original cost.

<div class="zh" markdown="1">

**真正有效的方案**：不是全面上云，而是先做**网络资源自助申请 + 自动化开通**（第 12 章自动化），把 6 周压到 2 天。项目 3 个月见效，成本只有原方案的 1/10。

</div>

> 💡 **Lesson**: **before the requirement is clarified, any technical proposal is guesswork.** Phases A and B of TOGAF look "soft", but they are the only gate against technology for its own sake.

<div class="zh" markdown="1">

> 💡 **教训**：**需求没澄清之前，任何技术方案都是在猜。** TOGAF 的 A、B 阶段看起来"虚"，但它们是防止"技术自嗨"的唯一闸门。

</div>

<figure class="fig">
<img src="assets/fig/en05-11-case1-skip-phase-a.svg" alt="Case 1 in two lanes: jumping straight to phase D against starting at phase A in the same bank" loading="lazy">
<figcaption><b>Figure 5-11　Case 1: the same bank twice &#8212; four months in phase D answered none of the CFO's three questions</b><br><span>图 5-11　案例一：直奔 D 阶段四个月，CFO 的三个问题一个都答不上</span></figcaption>
</figure>

### Case 2: A Manufacturing Group With the Wrong Operating Model · 案例二：制造集团运营模型错配

**Background**: a manufacturing group has five business units (auto parts, home appliance parts, tooling, trading, new energy). Headquarters required "one unified network architecture and unified management across the group".

<div class="zh" markdown="1">

**背景**：某制造集团有 5 个事业部（汽车件、家电件、模具、贸易、新能源），总部要求"全集团统一网络架构、统一管理"。

</div>

**The misjudgement**: headquarters IT assumed the group was a **Unification** operating model and pushed unified IP planning, unified security policy and a unified egress.

<div class="zh" markdown="1">

**误判**：总部 IT 认为集团属于**统一型**运营模型，于是强推统一 IP 规划、统一安全策略、统一出口。

</div>

**The actual conflicts**:

<div class="zh" markdown="1">

**实际冲突**：

</div>

| Business unit | Real characteristics | Problem created by unification |
|---------------|----------------------|-------------------------------|
| Auto parts | EDI integration with OEMs; the dedicated circuit must use the carrier the customer specifies | The unified egress design cannot be implemented |
| Home appliance parts | Runs its own e-commerce and needs fast CDN and cloud changes | The change approval chain is far too long |
| Tooling | Only 200 people; IT is a part-time role | Nobody can take on the complexity of a unified management platform |
| New energy | A brand-new plant that shares almost no data with the group | Forcing the unified architecture into the plant build slows it down |

<div class="zh" markdown="1">

| 事业部 | 实际特征 | 统一带来的问题 |
|--------|---------|--------------|
| 汽车件 | 与主机厂做 EDI 对接，专线必须走客户指定的运营商 | 统一出口方案无法落地 |
| 家电件 | 有自建电商，需要快速变更 CDN/云资源 | 变更审批链路过长 |
| 模具 | 只有 200 人，IT 是兼职的 | 统一管理平台的复杂度无人能接手 |
| 新能源 | 新建工厂，与集团几乎不共享数据 | 强绑统一架构拖慢建厂 |

</div>

**Repositioning with standardization × integration**: the facts point to **Diversification** (low standardization, low integration: independent units plus a few shared services), at most transitioning toward **Coordination**.

<div class="zh" markdown="1">

**用标准化 × 集成重新定位**：事实是**多样化型**（低标准化、低集成，各单元独立 + 少量共享服务），最多向**协调型**过渡。

</div>

**The corrected architecture**:
- Headquarters unifies only three things: **the shared Internet egress service, the group-level security baseline, and the WAN transport framework**
- Each business unit keeps its own addressing plan and change authority
- **Layered policy templates** (a mandatory security baseline plus optional network templates) replace the one-size-fits-all approach

<div class="zh" markdown="1">

**修正后的架构**：
- 总部只统一三件事：**互联网出口共享服务、集团级安全基线、WAN 传输框架**
- 每个事业部保留自己的地址规划与变更权
- 用**分层的策略模板**（强制的安全基线 + 可选的网络模板）代替"一刀切"

</div>

> 💡 **Lesson**: **get the operating model wrong and every downstream design is wrong.** Two questions settle it: do the units do things the same way? do the units need to share data frequently?

<div class="zh" markdown="1">

> 💡 **教训**：**运营模型判断错误，会导致所有下游设计都错。** 判断只需两问：各单元做事方式一样吗？单元之间需要频繁共享数据吗？

</div>

<figure class="fig">
<img src="assets/fig/en05-12-case2-operating-model-mismatch.svg" alt="Case 2: headquarters assuming Unification, the four units' real constraints, and the corrected three-things-unified design" loading="lazy">
<figcaption><b>Figure 5-12　Case 2: &#8220;the group is therefore Unification&#8221; was the design error, and three unified services were the fix</b><br><span>图 5-12　案例二：误判为统一型是设计错误，只统一三件事才是解法</span></figcaption>
</figure>

### Case 3: A Security Project That Could Not Prove Its Value and Lost Its Budget · 案例三：安全项目无法证明价值，预算被砍

**Background**: a retailer invested 8M in a network-wide security overhaul (firewalls, microsegmentation, NAC). A year later its request for phase-two funding was rejected.

<div class="zh" markdown="1">

**背景**：某零售企业投入 800 万做全网安全改造（防火墙、微隔离、NAC），一年后申请二期预算被拒。

</div>

**The reason**: the business case said only "improve the overall security level" — not SMART, therefore not verifiable. What the CIO saw was "8M spent and no visible change".

<div class="zh" markdown="1">

**原因**：立项时只写了"提升整体安全水平"——不满足 SMART，无法验证。CIO 看到的是"花了 800 万，没看到任何变化"。

</div>

**The measurement framework rebuilt afterwards**:

<div class="zh" markdown="1">

**重做后的度量体系**：

</div>

| Metric | Before | After |
|--------|--------|-------|
| **MTTD** (mean time to find a compromised host) | 21 days | 4 hours (NetFlow plus centralized logging) |
| **MTTR** (mean time to repair) | 5 days | 6 hours (automated isolation playbooks) |
| Non-compliant endpoint connection events | 30+ per month | 2 per month |

<div class="zh" markdown="1">

| 指标 | 改造前 | 改造后 |
|------|-------|-------|
| **MTTD**（发现失陷主机平均时间） | 21 天 | 4 小时（靠 NetFlow + 日志集中） |
| **MTTR**（修复平均时间） | 5 天 | 6 小时（靠自动化隔离剧本） |
| 违规终端接入事件 | 每月 30+ 起 | 每月 2 起 |

</div>

**Phase-two funding was approved** — because the CIO could take that table to the board.

<div class="zh" markdown="1">

**二期预算顺利通过**——因为 CIO 能拿这张表向董事会汇报。

</div>

> 💡 **Lesson**: **MTTD depends on visibility, MTTR on resilience and automation.** Fixing those two metrics at design time effectively locks in the technical direction: to improve MTTD add monitoring points, to improve MTTR add redundancy and automation.

<div class="zh" markdown="1">

> 💡 **教训**：**MTTD 靠可见性，MTTR 靠弹性与自动化。** 设计之初就确定这两条指标，等于提前锁定了技术方向：想改善 MTTD 就加监测点，想改善 MTTR 就加冗余和自动化。

</div>

---

<figure class="fig">
<img src="assets/fig/en05-13-case3-metrics.svg" alt="Case 3: the unverifiable business case that lost phase two, and the three measurable rows that won it back" loading="lazy">
<figcaption><b>Figure 5-13　Case 3: three rows of measurable metrics won back the budget an unverifiable business case had lost</b><br><span>图 5-13　案例三：三行可测指标赢回了不可验证方案丢掉的预算</span></figcaption>
</figure>

## Design Pitfalls · 设计缺陷

| Pitfall | Symptom | Correct practice |
|---------|---------|------------------|
| **Framework worship** | "We do it because TOGAF says so" | A framework is scaffolding; tailor it to this project's constraints |
| **Level mismatch** | A selection exercise is treated as depth for a business transformation need | Judge the alignment level first, then decide how deep the design goes |
| **Missing KPIs** | The design is finished but the value cannot be proven | Define measurable metrics (MTTD/MTTR/time to market) at the start |
| **Skipping phases A/B** | Selection starts as soon as a vague goal like "move to cloud" or "overhaul" appears | Write the business outcomes in SMART form first, then enter the technology domain |
| **Assumed operating model** | Assuming "the group is therefore Unification" | Reposition it with the two questions of standardization × integration |

<div class="zh" markdown="1">

| 缺陷 | 表现 | 正确做法 |
|------|------|---------|
| **框架崇拜** | "因为 TOGAF 说要做，所以就做" | 框架是脚手架，要对照本项目的约束裁剪 |
| **级别错配** | 用只做选型的深度去应对业务转型需求 | 先判断处在哪个对齐级别，再决定设计深度 |
| **KPI 缺失** | 设计完成却无法证明价值 | 设计之初就定义 MTTD/MTTR/上市时间等可测指标 |
| **跳过 A/B 阶段** | 拿到"上云""改造"这类模糊目标就开始选型 | 先把业务成果写成 SMART 形式，再进技术域 |
| **运营模型想当然** | 默认"集团就是统一型" | 用标准化 × 集成两问重新定位 |

</div>

---

## Lessons Learned · 实战经验总结

| Lesson | Explanation |
|--------|-------------|
| **Set the alignment level before the design depth** | A pure selection project should not carry the heavy process of business transformation; conversely a transformation need cannot be closed out with a selection report |
| **Trim the framework until it produces deliverables** | Cut any phase that produces neither a decision nor a constraint after review. The value of a framework is at the decision points, not in the volume of documents |
| **Position the operating model with two questions** | "Do we want unified standardization?" and "do we want unified integration?" — the answers land directly on one of four models, and that step fixes the scope of all later standardization |
| **Use reference architectures as a starting checklist, not the answer** | SAFE and CVD give you dimensions and validated scale boundaries, not configurations to copy |
| **Metrics must be set on Day 0** | MTTD (detection) and MTTR (recovery) decide whether you buy monitoring or redundancy; metrics added afterwards are not metrics |
| **Separate architecture from projects** | EA sets direction and standards; projects only deliver inside those standards. Without EA, every project grows its own locally optimal island |
| **Tie architecture to money** | Architecture output must enter budgeting and project review, or it stays a beautiful document. Phase two was approved because the CIO had a table the board could read |

<div class="zh" markdown="1">

| 经验 | 说明 |
|------|------|
| **先定对齐级别，再定设计深度** | 只做选型的项目不要套用"业务转型"级别的重型流程；反之业务转型需求也不能用一份选型报告交差 |
| **框架要裁剪到"能产出交付物"** | 凡是评审后既不产出决策、也不产出约束的阶段，一律砍掉。框架的价值在决策点，不在文档数量 |
| **运营模型用两问定位** | "要不要统一标准化？""要不要统一集成？"两个问题的答案直接落到四种模型（统一/协调/复制/多样化），这一步决定后面所有标准化范围 |
| **参考架构当起点清单，不当标准答案** | SAFE、CVD 给你的是维度和验证过的规模边界，不是可以直接抄的配置 |
| **指标在 Day 0 就要定** | MTTD（检测）与 MTTR（恢复）决定了要买监测还是买冗余，事后补指标等于没有指标 |
| **架构与项目分层** | EA 决定方向与标准，项目只负责在标准内交付。缺了 EA，项目会各自长出"本地最优"的孤岛 |
| **把架构和钱绑在一起** | 架构产出必须能进入预算与立项评审，否则永远是"漂亮的文档"。案例里二期预算能过，是因为 CIO 有一张能对上董事会语言的表 |

</div>

---

## Design Scenarios (2) · 设计情景演练（2 个）

### Scenario 1: After an Acquisition, Two Architecture Languages Coexist · 情景一：并购之后，两套架构语言并存

**Situation**: Group A (financial services, using TOGAF with centralized IT and a network planned by headquarters) acquires Company B (an internet business running Scrum with autonomous product teams, each building its own network). The group requires "a unified enterprise architecture within three years". At the first architecture review, B's team said "your architecture phases are too long, we run two-week iterations", and A's architect said "you have no architecture governance, you will never be auditable".

<div class="zh" markdown="1">

**场景**：A 集团（金融，用 TOGAF + 集中式 IT，网络由总部统一规划）收购 B 公司（互联网业务，用 Scrum + 产品团队自治，网络由各产品线自建）。集团要求"三年内统一企业架构"。第一次架构评审会上，B 的团队说"你们的架构阶段太长，我们两周一个迭代"，A 的架构师说"你们没有架构治理，以后无法审计"。

</div>

**Questions to answer**:
1. Is the conflict really about frameworks, or about operating models?
2. Which side's cadence should the network architecture follow?
3. What is the first deliverable that becomes the "common language"?

<div class="zh" markdown="1">

**要回答的问题**：
1. 冲突的本质是框架之争，还是运营模型之争？
2. 网络架构应该按哪一边的节奏走？
3. 第一个可交付的"共同语言"是什么？

</div>

**Reference approach**:
- **The essence is an operating model mismatch, not one framework being better.** A is centralized (pursuing standardization and compliance), B is federated/autonomous (pursuing speed). **Forcing one framework on both only makes the fast side slow and does not make the slow side better.**
- **Govern in layers by risk level**: network domains involving compliance, funds and customer data (core trading, payments, customer data) follow A's centralized governance (TOGAF phases with audit evidence); growth-oriented domains (marketing, experimental products) keep B's autonomy but must satisfy a **minimum architecture baseline** (addressing plan, security baseline, observability onboarding, cost attribution).
- **Run two tracks in terms of cadence**: architecture decisions reviewed quarterly, technical work delivered in iterations. **The framework governs decisions and their evidence, agile governs the delivery method; the two do not conflict — what conflicts is mistaking the framework for a project plan.**
- **The first common language**: a **capability map plus interface contracts** (which capabilities the center provides, which stay autonomous, and how SLAs and security responsibility are defined at the boundary). It produces real value faster than any framework document.
- **Acceptance**: not "the architecture documents are complete", but "a new business launch does not need an exception from headquarters" and "no unaudited change has occurred in the compliance domains".

<div class="zh" markdown="1">

**参考思路**：
- **本质是运营模型错配，不是框架优劣。** A 是集中式（追求标准化与合规），B 是联邦/自治式（追求速度）。**强行统一框架，只会让快的一方变慢、慢的一方也没变好。**
- **按"风险等级"分层治理**：涉及合规、资金、客户数据的网络域（如核心交易、支付、客户数据）走 A 的集中治理（TOGAF 阶段 + 审计留痕）；面向增长的业务域（如营销、试验性产品）保留 B 的自治，但必须满足"最小架构基线"（地址规划、安全基线、可观测性接入、成本归属）。
- **节奏上做双轨**：架构决策按季度评审，技术实施按迭代交付。**框架规定"决策与留痕"，敏捷规定"交付方式"，两者不冲突，冲突的是把框架当成项目计划。**
- **第一个共同语言**：一份**能力地图 + 接口契约**（哪些能力由中心提供、哪些自治，边界处的 SLA 与安全责任如何界定）。它比任何框架文档都更快产生实际价值。
- **验收**：不是"架构文档齐全"，而是"新业务上线不需要向总部申请例外"且"合规域没有出现未审计的变更"。

</div>

### Scenario 2: In a Budget Review, the Network Investment Cannot Explain Its Value · 情景二：预算评审会上，网络投资说不清价值

**Situation**: at the group's annual budget review, the network team requests 26M for a campus and WAN overhaul, with the justification "equipment is out of support, the architecture is dated, and we need to move to SD-WAN + Wi-Fi 6E". The CFO's response: "we just did a security project last year, why do you need money again? What does this spending bring?" The request was cut to 9M.

<div class="zh" markdown="1">

**场景**：集团年度预算评审，网络团队申请 2600 万做园区与 WAN 改造，理由写的是"设备已过保、架构陈旧、需要升级到 SD-WAN + Wi-Fi 6E"。CFO 的反馈是："去年刚做过安全项目，今年为什么又要钱？这些投入带来什么？" 结果被砍到 900 万。

</div>

**Questions to answer**:
1. Which pieces of business language are missing from the request?
2. How can KPIs translate a technology upgrade into business outcomes?
3. If only part of the budget can be saved, what should be protected first?

<div class="zh" markdown="1">

**要回答的问题**：
1. 这份申请缺了哪几块业务语言？
2. 如何用 KPI 把技术升级翻译成业务成果？
3. 如果只能保住一部分预算，优先保什么？

</div>

**Reference approach**:
- **Three things are missing: alignment to business goals, quantified current pain, and the consequence of not investing.** "Out of support" is technical language; what the CFO hears is "the vendor is raising prices".
- **Translate into KPIs**: map each technical item to business metrics — wireless overhaul → failed meeting/desk handovers and mean troubleshooting time; WAN overhaul → new store onboarding cycle and P95 latency for key applications across regions; SD-WAN → circuit cost and change-ticket duration. **Every KPI needs "current value → target value → money or risk".**
- **Write the consequence of not investing as risk exposure**: recovery time for out-of-support equipment failures (no spares means weeks), compliance risk from unpatched known vulnerabilities, and how much the old architecture drags on new business launch cycles (for example new store in 45 days versus 7 days for competitors).
- **Prioritize**: protect "compliance and security red lines" (non-negotiable), protect items that directly generate revenue or shorten time to market, cut "experience optimization" items. **Splitting 26M into three phases passes far more easily than insisting on a single request.**
- **One sentence**: **the CFO is not unwilling to spend money, but unwilling to spend it on things that cannot be measured.** Referring to the four alignment levels and the KPI section of this chapter, attach the plan to group-level goals.

<div class="zh" markdown="1">

**参考思路**：
- **缺三样东西：业务目标的对齐、可量化的现状痛点、不投资的后果。** "设备过保"是技术语言，CFO 听到的是"厂商要涨价"。
- **翻译成 KPI**：把技术项一一对应到业务指标——无线改造 → 会议/工位切换失败次数、平均排障时长；WAN 改造 → 新门店上线周期、跨区访问关键应用 P95 时延；SD-WAN → 线路成本与变更工单时长。**每个 KPI 要有"现状值 → 目标值 → 对应金额或风险"。**
- **不投资的后果要写成风险敞口**：过保设备的故障恢复时长（无备件 → 按周计）、已知漏洞无法修补带来的合规风险、老架构对新业务上线周期的拖累（例如新开店 45 天 vs 同行 7 天）。
- **优先级排序**：保"合规与安全红线"（不可谈）、保"直接产生收入或缩短上市时间"的项、砍"体验优化类"项。**把 2600 万拆成三期，比坚持一次性申请更容易通过。**
- **一句话**：**CFO 不是不愿意花钱，而是不愿意为无法度量的东西花钱。** 参照本章"业务架构四个对齐级别"与 KPI 小节，把方案挂到集团级目标上。

</div>

---

## Key Terms · 本章关键术语

| Term | Meaning |
|------|---------|
| Business Architecture (BA) | The architecture of business capabilities, outcomes and alignment |
| Enterprise Architecture (EA) | Organizing business process and IT infrastructure logic across the enterprise |
| Business Solution | Interacting capabilities delivering one or more outcomes |
| Business Outcome | Measurable result following SMART |
| SMART Principle | Specific, Measurable, Achievable, Relevant, Time-bound |
| Technology Specific | Domain-specific architecture level |
| Technology Architecture | Multi-domain architecture level |
| Business Transformation | Business-led architecture level |
| KPI | Key performance indicator |
| TOGAF | The Open Group Architecture Framework |
| ADM | Architecture Development Method (phases A–H) |
| ITIL | Information Technology Infrastructure Library |
| FEAF | Federal Enterprise Architecture Framework |
| DODAF | Department of Defense Architecture Framework |
| RMF | Risk Management Framework |
| Operating Model | Standardization and integration positioning of the enterprise |
| Coordination | Low standardization, high integration |
| Unification | High standardization, high integration |
| Diversification | Low standardization, low integration |
| Replication | High standardization, low integration |
| Reference Model | Abstract layered framework providing vocabulary |
| Reference Architecture | Structured reusable blueprint for a scenario class |
| MTTD | Mean time to detect |
| MTTR | Mean time to repair/recover |
| Day 0 / Day 1 / Day 2 | Plan and design / deploy and provision / operate and change |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| Business Architecture (BA) | 业务架构 |
| Enterprise Architecture (EA) | 企业架构 |
| Business Solution | 业务解决方案 |
| Business Outcome | 业务成果 |
| SMART Principle | SMART 原则 |
| Technology Specific | 技术特定（领域特定架构） |
| Technology Architecture | 技术架构（多领域架构） |
| Business Transformation | 业务转型 |
| KPI | 关键绩效指标 |
| TOGAF | The Open Group 架构框架 |
| ADM | 架构开发方法 |
| ITIL | 信息技术基础设施库 |
| FEAF | 联邦企业架构框架 |
| DODAF | 国防部架构框架 |
| RMF | 风险管理框架 |
| Operating Model | 运营模型 |
| Coordination | 协调型 |
| Unification | 统一型 |
| Diversification | 多样化型 |
| Replication | 复制型 |
| Reference Model | 参考模型 |
| Reference Architecture | 参考架构 |
| MTTD | 平均检测时间 |
| MTTR | 平均修复时间 |
| Day 0 / Day 1 / Day 2 | 规划设计 / 部署上线 / 日常运维 |

</div>

---

## Chapter Summary · 本章小结

Chapter 5 is the "engineering landing" of the first four chapters:

<div class="zh" markdown="1">

第 5 章是前四章的"工程化落地"：

</div>

```
Chapter 1 (design mindset)  → frameworks provide a legitimate source of best practice, but they remain a breeding ground for traps
Chapter 2 (business language)→ business architecture lifts priority → driver → outcome → capability to architecture level
Chapter 3 (purpose)         → information and application architecture in EA define what the network serves
Chapter 4 (pervasive security)→ the SAFE reference architecture is the standard blueprint for domains and chokepoints
Chapter 5 (frameworks)      → brings all of the above into one governable, measurable, iterative process
```

<div class="zh" markdown="1">

```
第 1 章（设计思维）    → 框架提供了"合法的最佳实践"来源，但仍是陷阱温床
第 2 章（业务语言）    → 业务架构把"优先级→驱动力→成果→能力"变成架构级别
第 3 章（网络目的）    → 企业架构中的信息/应用架构定义了网络服务对象
第 4 章（普适安全）    → SAFE 参考架构是安全域与检查点的标准蓝本
第 5 章（架构框架）    → 把以上全部纳入一个可治理、可衡量、可迭代的流程
```

</div>

> **One-line memory hook**: **business architecture sets direction, enterprise architecture sets organization, TOGAF sets process, ITIL sets operations, reference architectures set the blueprint.**
>
> And what is genuinely hard about design is this: **can you make trade-offs inside the dimensions a framework gives you, under this project's constraints, and explain clearly why.**

<div class="zh" markdown="1">

> **一句话记忆**：**业务架构定方向，企业架构定组织，TOGAF 定流程，ITIL 定运维，参考架构定蓝本。**
>
> 而设计真正难的是：**你能否在框架给出的维度里，结合本项目约束做出取舍，并说清为什么。**

</div>
