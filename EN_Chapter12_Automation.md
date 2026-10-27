# Chapter 12: Automation · 第 12 章：自动化

> *CCDE 400-007 Official Cert Guide* · English study notes | Original edition, Chapter 12 (pp. 565–588)

<div class="zh" markdown="1">

> 《CCDE 400-007 Official Cert Guide》中文翻译与精讲 | 原书第 565–588 页

</div>

---

## Topics Covered in This Chapter · 本章涵盖主题

- **Purpose and maturity model of automation**: why a "script" is not "automation"
- **Zero-Touch Provisioning (ZTP)**: Day 0/1/2, discovery mechanisms, bootstrap configuration, device identity
- **Infrastructure as Code (IaC)**: declarative, idempotent, configuration/data separation, single source of truth
- **CI/CD and the network change pipeline**: test pyramid, digital twin, canary rollout, rollback design
- **APIs and data models**: NETCONF/RESTCONF/gNMI, YANG, OpenConfig
- **Telemetry and drift governance**: from polling to streaming, from manual cross-checks to continuous compliance

<div class="zh" markdown="1">

- **自动化的目的与成熟度模型**：为什么"脚本"不等于"自动化"
- **零接触部署（ZTP）**：Day 0/1/2、发现机制、引导配置、设备身份
- **基础设施即代码（IaC）**：声明式、幂等、配置与数据分离、单一数据源
- **CI/CD 与网络变更流水线**：测试金字塔、数字孪生、灰度发布、回滚设计
- **API 与数据模型**：NETCONF/RESTCONF/gNMI、YANG、OpenConfig
- **遥测与配置漂移治理**：从"轮询"到"流式"，从"人工核对"到"持续合规"

</div>

---

## Chapter Introduction: Twelve Counter-Intuitive Truths About Automation · 本章导读：自动化的十二个反直觉认知

### 1. The Goal of Automation Is Not Speed — It Is Repeatability + Verifiability · 自动化的目标不是"快"，是"可重复 + 可验证"

If a manual configuration takes 10 minutes and the automated one takes 10 seconds, but the automated version has a 3% chance of misconfiguring the whole network, it is **more dangerous** than doing it by hand. The real value of automation is:

<div class="zh" markdown="1">

如果手工配置 10 分钟、自动化配置 10 秒，但自动化版本有 3% 概率配错全网，那它比手工**更危险**。自动化的真实价值是：

</div>

- **Repeatable**: the same input always produces the same output (idempotency)
- **Verifiable**: you can predict the result before the change and confirm it automatically afterwards
- **Traceable**: every change records who, why, what changed, and how to roll back

<div class="zh" markdown="1">

- **可重复**：同样的输入永远得到同样的输出（幂等）
- **可验证**：变更前能预测结果，变更后能自动确认
- **可追溯**：每一次变更都有谁、为什么、改了什么、如何回滚

</div>

**Speed is a by-product.** A script that cannot be rolled back and cannot be verified is, in essence, a batch incident generator.

<div class="zh" markdown="1">

**速度只是副产品。** 一个不能回滚、不能验证的自动化脚本，本质上是"批量事故生成器"。

</div>

### 2. Network Automation and Server Automation Are Two Different Problems · 网络自动化和服务器自动化是两类问题

| Dimension | Servers (cloud native) | Network |
|------|----------------|------|
| **Change granularity** | A single instance can be destroyed and rebuilt at will | One device carries hundreds of services; it cannot be rebooted |
| **Rollback** | Delete and re-create | **There is no "redo"**: protocol convergence and session loss are irreversible |
| **State** | Stateless, or state lives outside | **The device itself holds a large amount of state** (routes, neighbors, sessions, MAC) |
| **API completeness** | Full-featured API | Some functions are CLI-only, and **the commands differ between versions** |
| **Blast radius** | One instance | Potentially the whole network (one bad routing policy) |

<div class="zh" markdown="1">

| 维度 | 服务器（云原生） | 网络 |
|------|----------------|------|
| **变更粒度** | 单实例可随时销毁重建 | 一台设备承载几百个业务，不能重启 |
| **回滚** | 删掉重来 | **没有"重来"**：协议收敛、会话中断不可逆 |
| **状态** | 无状态或状态在外部 | **设备本身持有大量状态**（路由、邻居、会话、MAC） |
| **API 完整度** | API 全功能 | 部分功能只有 CLI，且**不同版本命令不同** |
| **爆炸半径** | 单实例 | 可能全网（一条错误路由策略） |

</div>

**Conclusion: network IaC must be more conservative than server IaC** — stronger pre-change validation, smaller change batches, and explicit rollback points.

<div class="zh" markdown="1">

**结论：网络 IaC 必须比服务器 IaC 更保守** —— 需要更强的预检验证、更小的变更批次、更明确的回滚点。

</div>

### 3. Declarative Does Not Mean You Stop Caring About Details · 声明式不等于"不用管细节"

`state: present` looks far more elegant than a pile of CLI, but declarative automation assumes that **the data model can express your intent**. When your intent is "the OSPF cost on this link must be 10 higher than on that one", either the declarative model can express it, or you go back to imperative.

<div class="zh" markdown="1">

`state: present` 看起来比一堆 CLI 优雅，但声明式的前提是**数据模型能把意图表达清楚**。当你的意图是"这条链路上 OSPF cost 必须比那条高 10"时，声明式模型要么能表达它，要么你就得回到命令式。

</div>

**Real-world network automation is almost always hybrid**: templates plus variables (declarative) generate the configuration, CLI/API (imperative) pushes and verifies it, and a test framework (declarative assertions) confirms the outcome.

<div class="zh" markdown="1">

**现实中的网络自动化几乎都是混合的**：用模板 + 变量（声明式）生成配置，用 CLI/API（命令式）下发并验证，用测试框架（声明式断言）确认结果。

</div>

### 4. The Biggest Cost Is Not Code, It Is Data · 最大的成本不是写代码，是"数据"

In a real campus automation project, the effort distribution looks approximately like this:

<div class="zh" markdown="1">

一个真实的园区自动化项目里，工作量的分布大致是：

</div>

| Work | Share |
|------|------|
| Building the **single source of truth (SoT)**: sites, devices, interfaces, IPs, VLANs, routing policies | **50%–60%** |
| Writing templates and playbooks | 20% |
| Building CI/CD and tests | 15% |
| Process and training | 10% |

<div class="zh" markdown="1">

| 工作 | 占比 |
|------|------|
| 建立**单一数据源（SoT）**：站点、设备、接口、IP、VLAN、路由策略 | **50%–60%** |
| 写模板与 playbook | 20% |
| 搭建 CI/CD 与测试 | 15% |
| 组织流程与培训 | 10% |

</div>

**Automation without structured data is just CLI replaced by Python string concatenation** — the error rate will not fall, because the data itself is wrong (IP conflicts, undefined VLANs, misspelled device names).

<div class="zh" markdown="1">

**没有结构化数据的自动化，等于把 CLI 换成 Python 字符串拼接** —— 错误率不会下降，因为数据本身是错的（IP 冲突、VLAN 未定义、设备名拼错）。

</div>

### 5. Configuration Drift Is Automation's Number One Enemy — and Its Biggest Value · 配置漂移是自动化的头号敌人，也是它最大的价值

In a manual environment, three years later 500 devices hold 500 different configurations, and nobody knows which one is "the standard". **The killer capability of automation is continuous compliance**: periodically compare the running configuration with the intended state, and alert or auto-remediate on any drift.

<div class="zh" markdown="1">

手工环境里，三年后 500 台设备的配置有 500 个版本，没人知道哪台是"标准配置"。**自动化的真正杀手级能力是"持续合规"**：定期把设备实际配置与期望状态比对，一旦漂移就告警或自动纠正。

</div>

> 💡 How to tell whether a team is really doing automation: **ask them how they detect configuration drift**. "People check it" = still Level 1; "we compare automatically every day and generate a report" = Level 3.

<div class="zh" markdown="1">

> 💡 判断一个团队是否真的在做自动化：**问他们"配置漂移怎么发现"**。答"靠人查"= 还在 Level 1；答"每天自动比对并出报告"= 到了 Level 3。

</div>

### 6. Automation Amplifies Process, Not Capability · 自动化放大的是流程，不是能力

**Chaotic process + automation = automated chaos.** If approvals are verbal, rollback is from memory, and testing means "I think it's fine", automation only makes the mistakes happen faster and more consistently.

<div class="zh" markdown="1">

**流程混乱 + 自动化 = 混乱的自动化**。如果变更审批靠口头、回滚靠记忆、测试靠"我觉得没问题"，那么自动化只会让错误发生得更快、更一致。

</div>

**The correct order is always: standardize the process first, then automate the standardized process.** Define change tiers, test requirements and rollback plans before writing a single line of code.

<div class="zh" markdown="1">

**正确的顺序永远是：先把流程标准化，再把标准流程自动化。** 先有"变更分级 + 测试要求 + 回滚方案"的定义，再写代码。

</div>

### 7. ZTP Has a Low Ceiling of Benefit; Day 2 Is Where the Cost Lives · ZTP 的收益封顶很低，Day 2 才是成本大头

Many proposals sell ZTP as "the automation project", but the arithmetic is straightforward:

<div class="zh" markdown="1">

很多方案把 ZTP 当成"自动化项目"来卖，但算一下账就清楚了：

</div>

| Phase | Effort per device (manual) | After automation | One-off or recurring |
|------|------------------|---------|--------------|
| Day 0/1 (deployment) | 1–4 hours | 5–30 minutes (just power and cabling) | **One-off** (once per device lifetime) |
| Day 2 (change) | 30–120 minutes each time | 1–5 minutes plus approval | **Several times per device per month** |
| Day N (incident/compliance) | 1–8 hours each time | Minute-level alerting and isolation | Continuous |

<div class="zh" markdown="1">

| 阶段 | 单设备工作量（手工） | 自动化后 | 一次性 or 重复 |
|------|------------------|---------|--------------|
| Day 0/1（部署） | 1–4 小时 | 5–30 分钟（只剩上电插线） | **一次性**（设备生命周期内 1 次） |
| Day 2（变更） | 每次 30–120 分钟 | 每次 1–5 分钟 + 审批 | **每台每月数次** |
| Day N（故障/合规） | 每次 1–8 小时 | 分钟级告警 + 定位 | 持续 |

</div>

**Conclusion: deployment automation saves one-off hours; configuration and verification automation saves recurring monthly hours.** With 500 devices and two changes per device per month, Day 2 consumes 5–10 times the annual hours of Day 1. So **the right investment order is: ZTP (builds trust, quick win) → compliance/drift (low risk, high value) → change pipeline → closed loop**.

<div class="zh" markdown="1">

**结论：部署自动化省的是"一次性工时"，配置与验证自动化省的是"每月重复工时"。** 500 台设备、每台每月 2 次变更，Day 2 的年度工时是 Day 1 的 5–10 倍。所以**正确的投资顺序是：ZTP（拿信任、见效快）→ 合规/漂移（低风险、高价值）→ 变更流水线 → 闭环**。

</div>

### 8. The Real Bottleneck Is Usually Authority and Approval, Not Technology · 真正的瓶颈通常不是技术，是"权限与审批"

Once you can technically "push to 500 devices in 5 minutes", you discover that changes are stuck in process: approval takes three days, the change window is monthly, the automation account has no TACACS authorization, and the firewall policy does not let the orchestration platform reach port 830 on the devices.

<div class="zh" markdown="1">

技术上"5 分钟能推完 500 台"之后，你会发现变更卡在流程里：审批要走 3 天、变更窗口每月一次、自动化账号没有 TACACS 授权、防火墙策略不让编排平台访问设备的 830 端口。

</div>

**To judge the real maturity of enterprise automation, ask three questions**:

<div class="zh" markdown="1">

**判断一个企业自动化的真实成熟度，问三个问题**：

</div>

1. Does the automation platform's service account have **its own least-privilege** AAA authorization (can change configuration but cannot change local accounts or erase the device)?
2. How long does it take on average from "code merged" to "effective in production"? **If it is three days, your bottleneck is process, not tooling.**
3. Can the change approval process recognize the shape of "automated bulk change" (or is it still one ticket per device)?

<div class="zh" markdown="1">

1. 自动化平台的服务账号有**独立的、最小权限的** AAA 授权吗（能改配置但不能改本地账号/不能 erase）？
2. 从"代码合并"到"生产生效"平均需要多久？**如果是 3 天，那你的瓶颈是流程，不是工具。**
3. 变更审批能识别"自动化批量变更"这种形态吗（还是一条一条审批）？

</div>

> ⚠️ Optimizing technology without optimizing process gives you "5-minute deployment plus 3-day queueing" — end-to-end time improves almost not at all.

<div class="zh" markdown="1">

> ⚠️ 只优化技术、不优化流程，会得到"5 分钟完成的下发 + 3 天的排队"——端到端时间改善几乎为零。

</div>

### 9. Read-Only Automation Is the Highest Value-per-Risk Starting Point · 只读自动化（read-only）是性价比最高的起点

Do not write configuration first. **Get reading right first**: collect configurations and state periodically → build a baseline → generate reports (compliance, inventory, software versions, EOL, interface description conventions, unused ports, duplicate IPs).

<div class="zh" markdown="1">

先不要写配置。**先把"读"做好**：定期采集配置与状态 → 建立基线 → 生成报告（合规、库存、软件版本、EOL、接口描述规范、未使用端口、重复 IP）。

</div>

- **Zero risk** (read-only cannot break anything)
- **Immediate value** (a single configuration-difference census often uncovers dozens of latent problems)
- **It is the prerequisite for everything else**: no baseline means no drift detection, and no drift detection means no trustworthy SoT

<div class="zh" markdown="1">

- **风险为零**（只读，不可能改坏东西）
- **能立刻产出价值**（一次配置差异普查往往能查出几十条隐患）
- **它是后续一切的前提**：没有基线就没有漂移检测，没有漂移检测就没有可信的 SoT

</div>

> 💡 "Read before write" is the only workable path for brownfield automation. Skipping the read and going straight to writes is driving through a minefield without a map.

<div class="zh" markdown="1">

> 💡 "先读后写"是存量网络（brownfield）自动化的唯一可行路径。跳过"读"直接"写"，等于在没有地图的雷区里开车。

</div>

### 10. The Orchestration Platform Is Itself a Production System · 编排平台本身是生产系统，也需要设计可用性

What happens when the controller or orchestration platform dies? This is a mandatory CCDE question. There are three possibilities:

<div class="zh" markdown="1">

控制器/编排平台挂了会怎样？这是 CCDE 必问的问题。三种可能：

</div>

| Shape of the failure | Consequence | Design action |
|----------------|------|---------|
| **Only affects change, not forwarding** (configuration already on the devices) | Acceptable: operations degrade to manual CLI | CLI access must be preserved, plus a manual runbook |
| **Affects service turn-up** (e.g. an SD-WAN controller that cannot push policy) | Acceptable but uncomfortable | Controller HA, configuration cache, local policy fallback |
| **Affects forwarding** (e.g. centralized control plane or a cloud gateway in the data path) | **Unacceptable design** | Decouple data plane from control plane; forwarding must survive cloud loss |

<div class="zh" markdown="1">

| 平台故障时的形态 | 后果 | 设计动作 |
|----------------|------|---------|
| **只影响"改"，不影响"转发"**（配置已下发到设备） | 可接受：运维降级到 CLI 手工 | 必须保留 CLI 能力 + 手工 Runbook |
| **影响"业务上线"**（如 SD-WAN 控制器挂了下发不了策略） | 可接受但不舒服 | 控制器 HA、配置缓存、本地策略兜底 |
| **影响"转发"**（如集中式控制面、云管理网关在数据路径上） | **不可接受的设计** | 数据面与控制面解耦，断云可转发 |

</div>

**The test question**: **"If the orchestration platform is down for four hours, does the business still run?"** "Yes, but nobody can change anything" = acceptable. "Forwarding stopped too" = architectural defect.

<div class="zh" markdown="1">

**判断句**：**"编排平台宕机 4 小时，业务还转不转？"** 答"转，但没人能改配置"= 可接受；答"转发也停了"= 架构设计缺陷。

</div>

### 11. 80% Template Coverage ≈ No Automation at All · 模板覆盖率 80% ≈ 没做自动化（长尾会吃掉收益）

The classic trap: 80% of standard switches go through templates, and the remaining 20% are "special" (old models, stacks, dedicated WAN egress, security zones, legacy VLANs). The result:

<div class="zh" markdown="1">

最典型的困局：80% 的标准交换机走模板，剩下 20% 是"特殊的"（老型号、堆叠、专线出口、安全区、历史遗留 VLAN）。结果是：

</div>

- **Two processes to maintain**: template and manual, which increases cognitive load
- Drift detection covers only 80%, and the remaining 20% is exactly where incidents happen
- Newcomers do not know why a given device is not templated, so they keep configuring by hand

<div class="zh" markdown="1">

- 维护**两套流程**：模板流程 + 手工流程，反而增加认知负担
- 漂移检测只覆盖 80%，剩下的 20% 恰恰是出事最多的
- 新人不知道"为什么这台不用模板"，只能继续手工

</div>

**The value of automation is a step function, not a line**: below 95% coverage the team is still running dual tracks and the benefit is largely cancelled out. **So a design must state an explicit long-tail strategy**:

<div class="zh" markdown="1">

**自动化的价值是阶跃的，不是线性的**：覆盖率 < 95% 时，团队仍在双轨运行，收益基本被抵消。**所以设计时必须明确处理长尾的策略**：

</div>

| Long-tail type | How to handle it |
|---------|---------|
| **Functional difference** (different VLANs/routing) | Data-driven (variables), bring it into the template |
| **Model difference** (old hardware lacks a feature) | `{% if %}` branches inside the template plus an explicit version matrix |
| **Genuinely one-off devices** | An **exemption list** naming the reason, owner and review date |
| **Operations that cannot be automated** (console rescue, ROMMON) | Documented in the runbook, out of automation scope, but with a fallback |

<div class="zh" markdown="1">

| 长尾类型 | 处理方式 |
|---------|---------|
| **功能差异**（VLAN/路由不同） | 数据驱动（变量），进模板 |
| **型号差异**（老设备不支持某特性） | 模板内 `{% if %}` 分支 + 明确的版本矩阵 |
| **真的一次性设备** | **明确豁免清单**（Exemption List），列明原因、责任人和复审日期 |
| **无法自动化的操作**（Console 救援、ROMmon） | 写进 Runbook，不算自动化范围，但要有替代手段 |

</div>

### 12. AI Made Writing Code Cheap; It Did Not Make Changes Safe · AI 让"写代码"变便宜，但没有让"变更"变安全

Generating Jinja2 templates, Ansible playbooks and regex parsers with a large model does save time. But it redistributes risk:

<div class="zh" markdown="1">

用大模型生成 Jinja2 模板、Ansible playbook、正则解析器确实能省时间。但它改变了风险分布：

</div>

| Step | Change | Risk |
|------|------|------|
| Writing code | 5–10× faster | More code to review, heavier review load |
| Understanding code | **Slower** (you did not write it) | During an incident nobody can explain why it is configured that way |
| Data and intent | Unchanged | **Still the leading cause of incidents** |
| Verification | Unchanged | Still needs schema, intent analysis and canary rollout |

<div class="zh" markdown="1">

| 环节 | 变化 | 风险 |
|------|------|------|
| 写代码 | 变快 5–10 倍 | 代码量增加，评审负担增加 |
| 理解代码 | **变慢**（不是你写的） | 出故障时没人能解释"为什么这么配" |
| 数据与意图 | 不变 | **仍然是事故主因** |
| 验证 | 不变 | 仍需 schema + 意图分析 + 灰度 |

</div>

**Conclusion: AI is a generator, not a verifier.** Everything it produces must land behind the existing defenses (schema validation, diff review, Batfish, canary, assertions). **Using AI to skip review means manufacturing bigger incidents faster.**

<div class="zh" markdown="1">

**结论：AI 是"生成器"，不是"验证器"。** 它产出的一切都必须落在已有的防线后面（schema 校验、diff 评审、Batfish、灰度、断言）。**用 AI 跳过评审，等于用更快的速度制造更大的事故。**

</div>

---

## Automation Maturity Model (for Assessing Current State and Target) · 自动化成熟度模型（用来评估现状与目标）

| Level | Name | Characteristics | Typical problems | Key transition action |
|------|------|------|---------|------------|
| **L0** | Pure manual | CLI onto each device, records in Excel | Severe drift, no audit trail | Establish configuration templates and naming conventions |
| **L1** | Scripts | Scattered Python/Shell scripts maintained by individuals | Only the author can run them, no version control | Put scripts in Git, establish review |
| **L2** | Templated | Unified templates plus variables (Jinja2/Ansible) | Human-triggered, no automated verification | Wire into CI, add syntax and compliance checks |
| **L3** | Pipeline | Git commit → CI validation → automated push → automated verification | Manual rollback, insufficient test environment | Build a digital twin/lab, add canary rollout |
| **L4** | Closed-loop self-healing | Telemetry-driven, automatic remediation or reconfiguration | Hard to define policy boundaries, risk of wrong actions | Define a self-healing allowlist and circuit breakers |
| **L5** | Intent-driven | Business intent → controller generates and validates configuration | Vendor ecosystem dependency, poor explainability | Narrow the scope (start with one or two high-value scenarios) |

<div class="zh" markdown="1">

| 级别 | 名称 | 特征 | 典型问题 | 关键跃迁动作 |
|------|------|------|---------|------------|
| **L0** | 纯手工 | CLI 逐台配置、Excel 记录 | 配置漂移严重、无审计 | 建立配置模板与命名规范 |
| **L1** | 有脚本 | 零散 Python/Shell 脚本，个人维护 | 脚本只有作者会跑、无版本控制 | 脚本进 Git、建立评审 |
| **L2** | 模板化 | 统一配置模板 + 变量（Jinja2/Ansible） | 靠人触发、无自动验证 | 接入 CI，做语法与合规检查 |
| **L3** | 流水线 | Git 提交 → CI 验证 → 自动下发 → 自动验证 | 回滚靠人工、测试环境不足 | 建数字孪生/实验室、加灰度 |
| **L4** | 闭环自愈 | 遥测驱动，异常自动修复/重配置 | 策略边界难界定、误动作风险 | 明确"可自愈"的白名单与熔断 |
| **L5** | 意图驱动 | 业务意图 → 控制器自动生成并验证配置 | 依赖厂商生态、可解释性差 | 场景收敛（先做 1–2 个高价值场景） |

</div>

**The key CCDE judgement**: **do not jump straight to L4/L5**. Most enterprises are stuck between L0 and L2; making data standardization, templating and Git solid returns far more than buying an intent-based controller.

<div class="zh" markdown="1">

**CCDE 视角的关键判断**：**不要一步跳到 L4/L5**。绝大多数企业的问题在 L0–L2 之间，把"数据标准化 + 模板化 + Git"做扎实，收益远大于上一个意图驱动控制器。

</div>

---

## The Four Layers of Automation (Know What You Are Automating) · 自动化的四个层次（分清你在自动化什么）

| Layer | Object of automation | Techniques | Value |
|------|-----------|---------|------|
| **① Deployment automation (Day 0/1)** | Power-on → bring-up → baseline configuration | ZTP/PnP, bootstrap scripts | Deployment time drops from weeks to hours |
| **② Configuration automation (Day 2)** | Service changes (VLAN/route/ACL/policy) | IaC, templates, CI/CD | Consistency and auditability |
| **③ Verification automation** | Fact-checking before and after a change | pyATS, Batfish, telemetry, compliance scans | Turns "I think it is fine" into "I can prove it is fine" |
| **④ Operations automation (AIOps)** | Fault detection, isolation, remediation | Telemetry + event correlation + automated action | Shorter MTTR |

<div class="zh" markdown="1">

| 层次 | 自动化对象 | 技术手段 | 价值 |
|------|-----------|---------|------|
| **① 部署自动化（Day 0/1）** | 设备上电 → 上线 → 基础配置 | ZTP/PnP、引导脚本 | 部署时间从周到小时 |
| **② 配置自动化（Day 2）** | 业务变更（VLAN/路由/ACL/策略） | IaC、模板、CI/CD | 一致性与可审计 |
| **③ 验证自动化** | 变更前后的事实核查 | pyATS、Batfish、遥测、合规扫描 | 把"以为没问题"变成"证明没问题" |
| **④ 运维自动化（AIOps）** | 故障检测、定位、修复 | 遥测 + 事件关联 + 自动动作 | 缩短 MTTR |

</div>

> ⚠️ **The most common failure mode**: doing only ② (configuration automation) and skipping ③ (verification automation). The result is "changes are pushed fast and uniformly, but nobody knows whether they are correct" — and when it goes wrong, the blast radius is larger than manual configuration.

<div class="zh" markdown="1">

> ⚠️ **最常见的失败模式**：只做 ②（配置自动化），不做 ③（验证自动化）。结果是"变更下发得又快又整齐，但没人知道它是否正确" —— 一旦出错，爆炸半径比手工更大。

</div>

---

## Doing the Math: Cost, Benefit and Priority of Automation · 把账算清楚：自动化的成本、收益与优先级

The most persuasive page in a design review is not the architecture diagram — it is **the TCO breakdown of a single change**.

<div class="zh" markdown="1">

方案评审时最有说服力的一页不是架构图，而是**一次变更的 TCO 拆解**。

</div>

### The True Cost of One Manual Change · 一次"手工变更"的真实成本

| Step | Typical duration | Comment |
|------|---------|------|
| Requirement clarification and design | 30–120 min | Automation **cannot** remove this part |
| Writing and approving the change ticket | 15–60 min | Partly removable (templated risk tiers) |
| Preparing the configuration (copy-paste/edit) | 20–60 min | 90% removable |
| Pre-checks (backup, current state) | 10–20 min | 100% removable |
| Execution and push | 10–40 min (longer across devices) | 95% removable |
| **Verification** (neighbors, routes, services) | 15–60 min | **80% removable** (requires assertions first) |
| Recording (update docs/CMDB) | 10–30 min | 100% removable (the SoT is the documentation) |
| Rework after mistakes (spread over a 10% probability) | Expected 10–60 min | Removed mainly by eliminating human error |

<div class="zh" markdown="1">

| 环节 | 典型耗时 | 说明 |
|------|---------|------|
| 需求澄清 + 设计 | 30–120 min | 自动化**不能省**这一部分 |
| 变更单填写与审批 | 15–60 min | 自动化可省一部分（模板化风险分级） |
| 准备配置（复制粘贴/手改） | 20–60 min | 自动化可省 90% |
| 预检查（备份、看现状） | 10–20 min | 自动化可省 100% |
| 执行下发 | 10–40 min（多设备更久） | 自动化可省 95% |
| **验证**（看邻居、看路由、看业务） | 15–60 min | **自动化可省 80%**（需先有断言） |
| 记录（更新文档/CMDB） | 10–30 min | 自动化可省 100%（SoT 即文档） |
| 出错返工（按 10% 概率分摊） | 期望值 10–60 min | 自动化主要靠"消除人为错误"降低此项 |

</div>

**Conclusion**: in a manual change, **the time actually spent typing commands is only 20%–30%**. So automating just the commands (CLI into a script) has limited payoff; **automating pre-checks, verification and recording together is what delivers an order-of-magnitude improvement.**

<div class="zh" markdown="1">

**结论**：手工变更里，**真正"敲命令"的时间只占 20%–30%**。所以只做"命令自动化"（把 CLI 换成脚本）收益有限；**把预检、验证、记录一起自动化，才有数量级的改善。**

</div>

### A Reusable ROI Model · 一个可复用的 ROI 模型

```
Annual hours saved ≈ number of changes × (manual time − automated time − approval time) × success-rate factor
                   + one-off deployment hours saved by ZTP (new devices this year)
                   + loss avoided from fewer incidents (ΔMTTR × incidents × business loss per hour)
```

<div class="zh" markdown="1">

```
年度节省工时 ≈ 变更次数 × (手工耗时 − 自动化耗时 − 审批耗时) × 单次成功率提升系数
             + ZTP 节省的一次性部署工时（当年新增设备数）
             + 事故减少带来的损失下降（MTTR↓ × 事故次数 × 每小时业务损失）
```

</div>

**Worked example (a mid-size enterprise with 500 devices)**:

<div class="zh" markdown="1">

**算例（500 台设备的中型企业）**：

</div>

| Item | Value | Annual saving |
|----|------|-------|
| Number of changes | 200/month × 12 = 2,400 | — |
| Time per change | 90 min → 15 min (including approval) | 2,400 × 1.25 h ≈ **3,000 person-hours** |
| Deployment | 120 new devices × 3 h → 0.5 h | ≈ **300 person-hours** |
| Incidents | 12 per year × MTTR 4 h → 1 h × ¥50k/h | ≈ **¥1.8 million** |

<div class="zh" markdown="1">

| 项 | 数值 | 年节省 |
|----|------|-------|
| 变更次数 | 200 次/月 × 12 = 2400 次 | — |
| 单次人工耗时 | 90 min → 15 min（含审批） | 2400 × 1.25 h ≈ **3000 人时** |
| 部署 | 新增 120 台 × 3 h → 0.5 h | ≈ **300 人时** |
| 事故 | 每年 12 起 × MTTR 4 h → 1 h × 5 万元/h | ≈ **180 万元** |

</div>

Against the investment (two person-years of platform staff, tooling licenses, lab), payback is typically **12–18 months**. **If you cannot produce this arithmetic, the project lacks a quantified goal and will most likely become a technology demo.**

<div class="zh" markdown="1">

对照投入（平台人力 2 人年 + 工具许可 + 实验室），通常 **12–18 个月回本**。**如果算不出这个账，说明项目缺少量化目标，大概率会变成"技术演示"。**

</div>

### Which Scenarios You Should Not Automate (Draw the Boundary Explicitly) · 哪些场景"不该"自动化（明确划出边界）

| Scenario | Why not | Better approach |
|------|-----------|-----------|
| **One-off architecture migration** (e.g. protocol replacement) | Happens once; the investment never pays back | Script-assisted execution plus a strict runbook |
| **Low-frequency, high-complexity change** (WAN redesign once or twice a year) | The code rots; nobody maintains it | Templatize fragments, execute the main path manually |
| **Operations requiring on-site judgement** (optical power, cable order, console) | The precondition for automation does not hold | Mobile checklist with results fed back |
| **Actions on the provider/carrier side** | Not under your control | Constrain the interface with acceptance assertions instead of assuming |
| **Emergency recovery during an incident** | State is unpredictable | **Break-glass manual path**, and it must be rehearsed |

<div class="zh" markdown="1">

| 场景 | 为什么不该 | 更好的做法 |
|------|-----------|-----------|
| **一次性的架构迁移**（如协议替换） | 只做一次，投入产出不成立 | 脚本辅助 + 严格 Runbook |
| **低频高复杂变更**（每年 1–2 次的 WAN 重构） | 代码会腐烂，无人维护 | 模板化"片段"，人工执行主干 |
| **需要现场判断的操作**（光功率、线序、Console） | 自动化前提不成立 | 移动端 Checklist + 结果回填 |
| **供应商/运营商侧动作** | 不受你控制 | 用"验收断言"约束接口，而非假设 |
| **故障中的紧急恢复** | 状态不可预测 | **break-glass 手工路径**（必须演练） |

</div>

> 💡 **CCDE perspective**: the scope of automation should be the intersection of **high frequency × structured × verifiable**. Remove any one of the three and the benefit drops sharply.

<div class="zh" markdown="1">

> 💡 **CCDE 视角**：自动化范围的定义应当是"**高频 × 结构化 × 可验证**"的交集。三个条件缺一个，收益都会大打折扣。

</div>

### Priority Ranking (by Value/Risk Ratio) · 优先级排序（按"价值/风险"比）

| Priority | Scenario | Risk | Value | Comment |
|-------|------|------|------|------|
| **P0** | Read-only collection and compliance reporting | None | High | Finds latent problems immediately, builds the baseline |
| **P0** | Configuration backup and version archiving | None | High | The lifeline during an incident |
| **P1** | Standard configuration generation for new sites | Low (new devices) | High | Small blast radius, ideal pilot |
| **P1** | Software version / EOL inventory | None | Medium-high | Compliance and lifecycle management |
| **P2** | Routine changes (VLAN/ACL/port/routing) | Medium | High | Requires diff, canary and rollback |
| **P2** | Post-change verification (assertions) | None | Very high | Determines whether P3 is even possible |
| **P3** | Fully automatic CD (no human confirmation) | High | Medium | Only for mature scenarios with strong assertions |
| **P4** | Closed-loop self-healing | Very high | Scenario-dependent | Allowlist, circuit breakers, human interrupt |

<div class="zh" markdown="1">

| 优先级 | 场景 | 风险 | 价值 | 说明 |
|-------|------|------|------|------|
| **P0** | 只读采集 + 合规报告 | 无 | 高 | 立刻能查出隐患，建立基线 |
| **P0** | 配置备份与版本归档 | 无 | 高 | 事故时的救命绳 |
| **P1** | 新增站点的标准配置生成 | 低（新设备） | 高 | 爆炸半径小，天然适合试点 |
| **P1** | 软件版本/EOL 盘点 | 无 | 中高 | 合规与生命周期管理 |
| **P2** | 常规变更（VLAN/ACL/端口/路由） | 中 | 高 | 必须有 diff + 灰度 + 回滚 |
| **P2** | 变更后验证（断言） | 无 | 极高 | 决定 P3 能否成立 |
| **P3** | 全自动 CD（无人确认） | 高 | 中 | 仅限成熟场景 + 强断言 |
| **P4** | 闭环自愈 | 极高 | 视场景 | 白名单 + 熔断 + 人工可打断 |

</div>

---

## Foundation Topics · 基础内容

---

## Zero-Touch Provisioning (ZTP) · 零接触部署

ZTP lets a network device complete the whole "power on → come online → under management" sequence **without any hands-on configuration on site**.

<div class="zh" markdown="1">

ZTP 使网络设备能够在**无需人工现场配置**的情况下自动完成"上电 → 上线 → 纳入管理"的全过程。

</div>

### The Day 0 / Day 1 / Day 2 Split · Day 0 / Day 1 / Day 2 的划分

| Phase | Content | Automation | Owner |
|------|------|-----------|--------|
| **Day 0** | Device arrival, physical install, power, identity (serial/certificate) | Procurement flow + serial registration + **SZiP/802.1AR** certificate | Supply chain + field installation |
| **Day 1** | Bootstrap configuration, management reachability, controller join, baseline | **ZTP / PnP**, bootstrap scripts | Network team (automated) |
| **Day 2** | Service configuration, policy change, capacity expansion, optimization | **IaC + CI/CD** | Network team (automated) |
| **Day N** | Upgrades, compliance, drift correction, repair | Telemetry + compliance scans + orchestration | Operations (automated + human judgement) |

<div class="zh" markdown="1">

| 阶段 | 内容 | 自动化手段 | 谁负责 |
|------|------|-----------|--------|
| **Day 0** | 设备到货、物理安装、上电、取证（序列号/证书） | 采购流程 + 序列号登记 + **SZiP/802.1AR** 证书 | 供应链 + 现场施工 |
| **Day 1** | 引导配置、管理面可达、加入控制器、基线配置 | **ZTP / PnP**、引导脚本 | 网络团队（自动） |
| **Day 2** | 业务配置、策略变更、扩容、优化 | **IaC + CI/CD** | 网络团队（自动） |
| **Day N** | 升级、合规、漂移纠正、故障修复 | 遥测 + 合规扫描 + 编排 | 运维（自动 + 人工判断） |

</div>

> 💡 **Design point**: ZTP only solves Day 0/1; **Day 2 is where the long-term cost lives**. Many projects treat ZTP as "automation done", and end up with devices online in five minutes and then entirely manual afterwards — 90% of the benefit evaporates.

<div class="zh" markdown="1">

> 💡 **设计要点**：ZTP 只解决 Day 0/1，**Day 2 才是长期成本的来源**。很多项目把 ZTP 当成"自动化完成"，结果设备上线 5 分钟，后面全靠手工 —— 收益被稀释了 90%。

</div>

### The Complete ZTP Flow (where it is harder than the six-line diagram) · ZTP 的完整流程（比六行流程图复杂的地方）

```
[Precondition: serial number / certificate pre-registered in the orchestration system (PnP database / cloud)]

1. Device powers on with no configuration
2. Layer 2 discovery: broadcast/multicast to find the PnP server (or DHCP Option 43 pointing at it)
   └─ If crossing Layer 3: DHCP Option 43 / DNS (pnp-server.<domain>)
3. HTTPS session to the orchestration system (certificate/serial validation → device identity)
4. Orchestration matches the device profile by serial (role + site + template)
5. Bootstrap is pushed: management IP, certificate, controller address, domain, NTP
6. Device reloads → joins the controller / management platform
7. All further configuration comes from the controller/IaC (Day 2); ZTP is over
```

<div class="zh" markdown="1">

```
【前提：设备序列号/证书已提前登记在编排系统（PnP 数据库 / 云平台）】

① 设备上电，无配置启动
② 二层发现：广播/组播寻找 PnP 服务器（或 DHCP Option 43 指向）
   └─ 若跨三层：DHCP Option 43 / DNS（pnp-server.<domain>）
③ 与编排系统建立 HTTPS 连接（校验证书/序列号 → 设备身份认证）
④ 编排系统根据序列号匹配"设备画像"（角色 + 站点 + 模板）
⑤ 下发引导配置（bootstrap）：管理 IP、证书、控制器地址、域名、NTP
⑥ 设备重启 → 加入控制器/纳管平台
⑦ 后续配置由控制器/IaC 下发（Day 2），ZTP 结束
```

</div>

**The key difference**: real ZTP is not "DHCP hands out a configuration file URL and we are done" — it is the **device identity → role → configuration** mapping. That mapping table is the automation **single source of truth** (see below).

<div class="zh" markdown="1">

**关键差别**：真正的 ZTP 不是"DHCP 给一个配置文件 URL 就完了"，而是**"设备身份 → 角色 → 配置"的映射过程**。这个映射表就是自动化的**单一数据源**（见后文）。

</div>

### The Four ZTP Implementations · ZTP 的四种实现方式

| Method | Discovery | Configuration source | Pros | Cons |
|------|---------|---------|------|------|
| **DHCP + TFTP/HTTP** | Option 43/66/67 | Configuration file | Simple, controllable | Clear-text TFTP is insecure; no identity check |
| **PnP (Cisco Plug and Play)** | Broadcast/DHCP/DNS to find the PnP server | PnP Connect / on-prem PnP | Device identity validation, cloud support | Requires PnP infrastructure |
| **Cloud ZTP (SD-WAN / Meraki)** | Serial registered in the cloud | Cloud templates | Global zero-touch, no local server | Depends on internet and cloud vendor |
| **PXE / iPXE (server style)** | DHCP + TFTP + HTTP | Full image + scripts | Can do a full re-image | Limited support on network devices |

<div class="zh" markdown="1">

| 方式 | 发现机制 | 配置来源 | 优点 | 缺点 |
|------|---------|---------|------|------|
| **DHCP + TFTP/HTTP** | Option 43/66/67 | 配置文件 | 简单、可控 | 明文 TFTP 不安全；无身份校验 |
| **PnP（Cisco Plug and Play）** | 广播/DHCP/DNS 找 PnP 服务器 | PnP Connect / 本地 PnP | 有设备身份校验、支持云 | 需要 PnP 基础设施 |
| **Cloud ZTP（SD-WAN / Meraki）** | 云端登记序列号 | 云平台模板 | 全球零接触、无需本地服务器 | 依赖互联网与云厂商 |
| **PXE / iPXE（服务器式）** | DHCP + TFTP + HTTP | 完整镜像 + 脚本 | 可做"整机重装" | 对网络设备支持有限 |

</div>

### What the Bootstrap Configuration Should Contain · 引导配置（Bootstrap）应该包含什么

The **first configuration ZTP pushes must be tiny** — it only has to make the device manageable by the systems that follow:

<div class="zh" markdown="1">

ZTP 下发的**第一份配置必须极小**，只解决"让设备能被后续系统管理"：

</div>

| Required item | Why | Common omission |
|-------|------|---------|
| **Management interface IP / Loopback** | Foundation of every management path | Using a DHCP address that expires and loses the device |
| **Default gateway / route** | Reach the controller and NTP | IP configured without a route |
| **NTP** | Certificate validation, log timestamps, TACACS | Clock skew breaks DTLS/TLS |
| **DNS** | Resolve controller names | Everything hard-coded to IPs, so an IP change kills everything |
| **Management credentials / certificate** | API authentication later | Default passwords (a serious security problem) |
| **ACL on management protocols** | Only management subnets may connect | SSH open to the whole network |
| **Controller address / domain** | Joining management | Typed by hand; a typo strands the device at Day 1 |
| **Logging/telemetry destination** | Observability from day one | Finding out after go-live that nothing was logged |

<div class="zh" markdown="1">

| 必须项 | 原因 | 常见遗漏 |
|-------|------|---------|
| **管理接口 IP / Loopback** | 后续所有管理通道的基础 | 用 DHCP 地址，租期到了就失联 |
| **默认网关 / 路由** | 到达控制器与 NTP | 只配 IP 不配路由 |
| **NTP** | 证书校验、日志时间戳、TACACS | 时间不同步导致 DTLS/TLS 失败 |
| **DNS** | 控制器域名解析 | 全靠 IP 硬编码，换 IP 就全瘫 |
| **管理凭据 / 证书** | 后续 API 认证 | 用默认密码（严重安全问题） |
| **管理协议的 ACL** | 只允许管理网段访问 | 全网可 SSH |
| **控制器地址 / 域名** | 加入纳管 | 手工填写，写错就卡在 Day 1 |
| **日志/遥测目标** | 可观测性从第一天开始 | 上线后才发现没日志 |

</div>

> ⚠️ **The security floor of ZTP**: **device identity must be validated** (serial plus certificate/SZiP), otherwise anyone who plugs in a cable can "claim" a complete configuration (including management credentials and routing policy) — the most serious ZTP risk. TFTP plus clear-text passwords is equivalent to unauthenticated access in a modern audit.

<div class="zh" markdown="1">

> ⚠️ **ZTP 的安全底线**：**必须验证设备身份**（序列号 + 证书/SZiP），否则任何插上网线的人都能"领走"一份完整配置（含管理凭据、路由策略）—— 这是 ZTP 最严重的安全风险。TFTP + 明文密码的组合在现代审计里等同于"未授权访问"。

</div>

### ZTP Failure Modes (the ones you meet on cutover night) · ZTP 的失败模式（上线现场最常遇到的）

| Failure point | Symptom | Cause | How to check |
|-------|------|------|---------|
| **No DHCP** | Device waits forever | Access port VLAN unconfigured, no DHCP, port security | Switch port state, DHCP logs |
| **PnP server not found** | Repeated broadcast, timeout | Option 43/DNS not configured across Layer 3 | Packet capture of the DHCP options |
| **HTTPS certificate validation failure** | Connection refused | Device clock wrong (NTP not synced), missing CA chain | `show clock` on the device |
| **Serial not registered** | Authentication fails, no profile match | Procurement data never entered in the system | Query the PnP database |
| **Wrong profile mapping** | Device gets another site's configuration | Site/role fields wrong | Cross-check the SoT data |
| **Lost after bootstrap** | Wrong management IP/VLAN pushed | Template variable resolved wrongly | Console in and inspect |
| **Duplicate enrollment / device ID clash** | Two devices overwrite each other | Duplicate serial registration or cloned images | Audit the PnP database |

<div class="zh" markdown="1">

| 失败点 | 现象 | 原因 | 排查方法 |
|-------|------|------|---------|
| **拿不到 DHCP** | 设备一直等待 | 接入端口 VLAN 未配、无 DHCP、端口安全 | 交换机端口状态、DHCP 日志 |
| **找不到 PnP 服务器** | 反复广播、超时 | 跨三层未配 Option 43/DNS | 抓包看 DHCP Option 内容 |
| **HTTPS 证书校验失败** | 连接被拒 | 设备时间不对（NTP 未同步）、CA 链缺失 | 设备 `show clock` |
| **序列号未登记** | 认证失败或无画像匹配 | 采购信息未录入系统 | PnP 数据库查询 |
| **画像映射错误** | 配成了错误站点的配置 | 站点/角色字段填错 | 核对 SoT 数据 |
| **引导后失联** | 下发了错误的管理 IP/VLAN | 模板变量取值错误 | Console 接入检查 |
| **重复纳管 / 设备 ID 冲突** | 两台设备互相覆盖 | 序列号重复登记或克隆镜像 | PnP 数据库审计 |

</div>

### The Value of ZTP (quantified) · ZTP 的价值（量化收益）

| Benefit | Explanation | Measurable indicator |
|------|------|-----------|
| **Shorter deployment** | Hours down to minutes | Per-site deployment effort: 8 h → 0.5 h |
| **Fewer human errors** | Templated configuration removes typos | Rework rate after cutover: 30% → < 5% |
| **Remote deployment** | No engineer on site | Travel cost, arrival-to-live interval (weeks → days) |
| **Consistency** | Every device uses the same template | Number of configuration differences (trends to zero) |
| **Auditability** | Configuration changes are traceable | Every cutover has a Git record and a change ticket |
| **Scalability** | 100 sites cost about the same as 10 | Marginal deployment cost drops sharply |

<div class="zh" markdown="1">

| 好处 | 说明 | 可量化指标 |
|------|------|-----------|
| **减少部署时间** | 从小时级降到分钟级 | 单站点部署工时：8 h → 0.5 h |
| **降低人为错误** | 模板化配置消除手误 | 上线返工率：30% → < 5% |
| **远程部署** | 无需工程师现场操作 | 差旅成本、到货到上线周期（周 → 天） |
| **一致性** | 所有设备使用相同模板 | 配置差异项数量（趋于 0） |
| **可审计** | 配置变更可追踪 | 每次上线有 Git 记录 + 变更单 |
| **可扩展** | 100 个站点和 10 个站点工作量近似 | 边际部署成本显著下降 |

</div>

> 💡 **The only real test of ZTP success**: **can the on-site person do nothing but power up and plug in cables?** If an engineer still has to travel to type commands or edit configuration files, it is semi-automatic deployment.

<div class="zh" markdown="1">

> 💡 **判断 ZTP 是否成功的唯一标准**：**现场人员能不能"只做上电和插线"**。如果还需要工程师到现场敲命令、改配置文件，那只是"半自动部署"。

</div>

### On-Prem ZTP vs Cloud ZTP · 本地 ZTP vs 云 ZTP

| Type | Characteristics | Where it fits | Risk |
|------|---------|---------|------|
| **On-prem ZTP** | Local DHCP + PnP/TFTP/HTTP server | Internal networks, security-sensitive environments, no internet egress | You must build HA for the local servers |
| **Cloud ZTP** | Managed through a cloud platform (PnP Connect / Meraki / SD-WAN controller) | Multi-branch enterprises, SD-WAN, no on-site IT | Depends on internet and cloud availability |
| **Hybrid** | Bootstrap from the cloud, long-term configuration on-prem | Large enterprises in transition | Data consistency between the two systems |

<div class="zh" markdown="1">

| 类型 | 特点 | 适用场景 | 风险 |
|------|------|---------|------|
| **本地 ZTP（On-Prem）** | 本地 DHCP + PnP/TFTP/HTTP 服务器 | 内部网络、安全敏感环境、无外网出口 | 本地服务器需自建高可用 |
| **云 ZTP（Cloud）** | 通过云平台（PnP Connect / Meraki / SD-WAN 控制器）管理 | 多分支企业、SD-WAN、无 IT 现场 | 依赖互联网与云厂商可用性 |
| **混合** | 引导走云，长期配置走本地 | 大型企业过渡期 | 两套系统的数据一致性 |

</div>

### ZTP Concurrency and Capacity: What Happens When 500 Devices Power On at Once · ZTP 的并发与容量：500 台同时上电会发生什么

For a new factory or a new campus, devices usually **power up in batches**. What breaks first is normally not the network but the ZTP server:

<div class="zh" markdown="1">

新建工厂/新开园区时，设备往往是**整批上电**。这时最先崩的通常不是网络，而是 ZTP 服务器：

</div>

| Resource | Peak estimate | Easy to overlook |
|------|---------|-------------|
| **HTTPS sessions** | 500 × 2–3 retries | Image download and configuration push may use separate connections |
| **DHCP pool** | Must be ≥ 2× device count (old leases linger during retries) | Once the pool is exhausted, new devices never get an address |
| **TFTP/HTTP throughput** | 500 MB image × 50 concurrent = 25 GB | A single TFTP server yields "first 50 succeed, the rest time out" |
| **PnP database writes** | 500 concurrent registrations | Database locks cause "registration succeeded but no profile matched" |
| **AAA/RADIUS** | Devices authenticate at boot (MAB/802.1X) | Ordering conflict between authentication and ZTP |

<div class="zh" markdown="1">

| 资源 | 峰值估算 | 容易忽略的点 |
|------|---------|-------------|
| **HTTPS 会话数** | 500 台 × 2–3 次重试 | 引导镜像下载与配置下发可能占不同连接 |
| **DHCP 池** | 需 ≥ 设备数 × 2（重试时旧租约未释放） | 池子耗尽后新设备永远等不到地址 |
| **TFTP/HTTP 吞吐** | 镜像 500 MB × 50 台并发 = 25 GB | 用单台 TFTP 会出现"前 50 台成功，后面全超时" |
| **PnP 数据库写入** | 500 条并发登记 | 数据库锁导致"登记成功但画像未匹配" |
| **AAA/RADIUS** | 设备开机即认证（MAB/802.1X） | 认证与 ZTP 的顺序冲突（先认证还是先给配置） |

</div>

**Three throttling designs**:

<div class="zh" markdown="1">

**三种节流设计**：

</div>

1. **Staged power-up** (simplest and most effective): by rack or floor, 20–30 devices per batch, 10 minutes apart.
2. **Port scheduling**: `link-delay`/`storm-control` on access ports, or operations issuing `shutdown`/`no shutdown` in batches.
3. **Rate limiting at the ZTP server**: a reverse proxy caps concurrent connections, turning load into queueing instead of timeouts.

<div class="zh" markdown="1">

1. **分批上电**（最简单有效）：按机柜/楼层分批，每批 20–30 台，间隔 10 分钟。
2. **端口调度**：交换机端口配置 `link-delay`/`storm-control`，或由运维按批次 `shutdown/no shutdown`。
3. **ZTP 服务器限流**：反向代理限制并发连接数，把压力变成"排队"而不是"超时"。

</div>

> ⚠️ **A real trap**: with ZTP and 802.1X both enabled, the device is blocked by MAB at boot (no certificate, no account), never gets network access, and therefore never reaches ZTP. **Plan a two-phase policy — open during ZTP, tighten after enrollment** (for example a ZTP VLAN plus temporary port authorization, switched to the production VLAN by the controller once managed).

<div class="zh" markdown="1">

> ⚠️ **一个真实的坑**：ZTP 与 802.1X 同时启用时，设备开机先被 MAB 拦住（无证书/无账号），拿不到网络就永远走不到 ZTP。**必须规划"ZTP 阶段放行、纳管后收紧"的两阶段策略**（例如 ZTP VLAN + 端口授权临时放行 + 纳管后由控制器统一切换到生产 VLAN）。

</div>

### The Most Underrated Value of ZTP: RMA Replacement · ZTP 最被低估的价值：RMA 换机

Design reviews often miss this: **a device does not go live only once**. Over a three-year lifecycle, replacement of failed units (RMA) typically runs at 3%–10% per year.

<div class="zh" markdown="1">

方案评审时常忽略这一点：**设备不是只上线一次**。三年生命周期里，坏件更换（RMA）的比例通常 3%–10%/年。

</div>

| Process | Without ZTP | With ZTP |
|------|-------|-------|
| New unit arrives | Field engineer brings the old configuration template | Plug it in |
| Configuration restore | Copy the old configuration by hand (possibly stale) | Profile matches automatically → latest standard configuration |
| Consistency | Restored to "the configuration from three years ago" | Restored to "today's standard configuration" |
| Duration | Half a day to two days (including travel) | 30 minutes |
| Hidden risk | Old configuration carries deprecated VLANs/ACLs | Legacy issues corrected automatically |

<div class="zh" markdown="1">

| 流程 | 无 ZTP | 有 ZTP |
|------|-------|-------|
| 新机到货 | 现场工程师带着旧配置模板 | 直接插电 |
| 配置恢复 | 手工复制旧配置（可能已过期） | 自动匹配画像 → 下发最新标准配置 |
| 一致性 | 恢复成"三年前的配置" | 恢复成"今天的标准配置" |
| 耗时 | 半天到两天（含差旅） | 30 分钟 |
| 隐藏风险 | 旧配置含已废弃 VLAN/ACL | 自动纠正历史遗留 |

</div>

**The test question**: **"When this unit fails and is replaced, can a security guard be the only person involved — just plugging in the power?"** That is the touchstone of ZTP design maturity.

<div class="zh" markdown="1">

**判断句**：**"这台设备坏了换新的，能不能只让保安插上电源？"** 这是 ZTP 设计成熟度的试金石。

</div>

### ZTP Acceptance Checklist (a deliverable, not an afterthought) · ZTP 上线验收清单（写进方案交付物）

| # | Check item | Pass criteria |
|---|-------|---------|
| 1 | Device identity validation | Serial plus certificate both validated; unregistered devices rejected and alerted |
| 2 | Discovery coverage | Layer 2 (broadcast), Layer 3 (Option 43) and cross-domain (DNS) all tested live |
| 3 | Minimal bootstrap | Only management IP/route/NTP/DNS/controller/ACL, no service configuration |
| 4 | NTP reachability | Every site can reach a time source in its timezone (otherwise certificates fail) |
| 5 | Failure alerting | Alert if not joined within 30 minutes (instead of waiting for a site report) |
| 6 | Fallback path | USB/console bootstrap script works and **has been rehearsed** |
| 7 | Concurrency test | A batch of 50 all succeed with no timeouts |
| 8 | Admission integration | Open during ZTP, tightened automatically after enrollment (port VLAN + authentication policy) |
| 9 | RMA process | Replacement restored within 30 minutes, and it receives the latest standard configuration |
| 10 | Audit trail | Every bootstrap recorded (who, when, which device, which template version) |

<div class="zh" markdown="1">

| # | 检查项 | 通过标准 |
|---|-------|---------|
| 1 | 设备身份验证 | 序列号 + 证书双校验，未登记设备被拒绝并告警 |
| 2 | 发现机制覆盖 | 二层（广播）、三层（Option 43）、跨域（DNS）三种形态都实测 |
| 3 | 引导配置最小化 | 只含管理 IP/路由/NTP/DNS/控制器/ACL，不含业务配置 |
| 4 | NTP 可达性 | 所有站点时区与源可达（否则证书必挂） |
| 5 | 失败告警 | 30 分钟未 join 触发告警（而非等现场报修） |
| 6 | 兜底路径 | USB/Console 引导脚本可用，且**演练过** |
| 7 | 并发压测 | 单批 50 台可全部成功，无超时 |
| 8 | 与准入衔接 | ZTP 阶段放行、纳管后自动收紧（端口 VLAN + 认证策略） |
| 9 | RMA 流程 | 换机 30 分钟内恢复，且拿到的是最新标准配置 |
| 10 | 审计留痕 | 每次引导有记录（谁、何时、哪台、下发哪个模板版本） |

</div>

---

## Infrastructure as Code (IaC) · 基础设施即代码

IaC is the practice of managing and configuring infrastructure through code (machine-readable definition files) instead of manual configuration.

<div class="zh" markdown="1">

IaC 是通过代码（机器可读的定义文件）管理和配置基础设施的过程，替代手动配置。

</div>

**One-line definition**: **write what the network should look like into Git, let machines implement it, and continuously verify that reality matches.**

<div class="zh" markdown="1">

**一句话定义**：**把"网络应该是什么样"写进 Git，让机器去实现它，并持续验证它与现实一致。**

</div>

### Declarative vs Imperative: Where the Real Difference Lies · 声明式 vs 命令式：本质区别在哪里

| Dimension | Imperative | Declarative |
|------|---------------------|---------------------|
| **Expression** | "Do A, then B, then C" | "The end state must be X" |
| **Representatives** | Shell/Python scripts, Netmiko, CLI | Ansible, Terraform, NETCONF/YANG, controller APIs |
| **Idempotency** | **Not inherent** (a re-run may add duplicates) | Inherent (converges to the target state) |
| **Error recovery** | You write the checks and the fallback yourself | Re-run and it converges |
| **Transparency** | Logic is visible and easy to debug | State is abstracted; you must understand the tool's behaviour |
| **Fits** | One-off tasks, complex orchestration, migrations | Routine configuration, continuous compliance |

<div class="zh" markdown="1">

| 维度 | 命令式（Imperative） | 声明式（Declarative） |
|------|---------------------|---------------------|
| **表达** | "先做 A，再做 B，最后做 C" | "最终状态必须是 X" |
| **代表** | Shell/Python 脚本、Netmiko、CLI | Ansible、Terraform、NETCONF/YANG、控制器 API |
| **幂等性** | **不天然具备**（重跑可能重复添加） | 天然具备（收敛到目标状态） |
| **错误恢复** | 需自己写判断与回退 | 重新执行即可收敛 |
| **透明度** | 逻辑可见、易调试 | 状态抽象、需理解工具行为 |
| **适用** | 一次性任务、复杂编排、迁移 | 常规配置、持续合规 |

</div>

**Key insight**: **declarative tools are still imperative underneath**. Ansible modules ultimately emit CLI/API commands. So "declarative" is the **user's viewpoint, not the device's**. The consequence: **when the tool's behaviour diverges from your intent, you still need to understand the underlying commands.**

<div class="zh" markdown="1">

**关键认知**：**声明式工具在底层仍然是命令式的**。Ansible 的模块最终也是发 CLI/API 命令。所以"声明式"是**使用者的视角**，不是设备的视角。这意味着：**当工具的行为与你理解的意图不一致时，你仍然要懂底层命令。**

</div>

### Idempotency: The First Hurdle of Automation · 幂等性（Idempotency）：自动化的第一道门槛

| Scenario | Non-idempotent script | Idempotent implementation |
|------|-----------|---------|
| Adding a VLAN | `vlan 100` executed every time (may error or duplicate) | Check existence first, create only if absent |
| Adding ACL entries | Entries duplicate on re-run (10 become 20) | Delete the old ACL and push the whole thing |
| Adding a route | Static route duplicates on re-run | `no ip route` first, or replace wholesale |
| Applying tags | Tags accumulate | Declare the tag set and write it overwriting |

<div class="zh" markdown="1">

| 场景 | 非幂等脚本 | 幂等实现 |
|------|-----------|---------|
| 加 VLAN | `vlan 100` 每次都执行（可能报错或重复） | 先检查存在性，不存在才创建 |
| 加 ACL 条目 | 重跑后条目重复（10 条变 20 条） | 先删除旧 ACL 再整体下发 |
| 加路由 | 重跑后 static route 重复 | 用 `no ip route` 清理再配置，或整体替换 |
| 打标签 | 标签叠加 | 声明标签集合，覆盖式写入 |

</div>

**How to verify**: **run the same code twice; the second run must report zero changes (changed=0)**. If the second run still reports changes, it is not idempotent — the most commonly ignored quality defect in network automation.

<div class="zh" markdown="1">

**验证方法**：**同一份代码连续执行两次，第二次应该是"零变更"（changed=0）**。如果第二次仍然报告变更，说明不是幂等的 —— 这是网络自动化里最容易被忽略的质量缺陷。

</div>

### Configuration/Data Separation (Template + Variables) · 配置与数据分离（模板 + 变量）

This is the core paradigm of network IaC:

<div class="zh" markdown="1">

这是网络 IaC 的核心范式：

</div>

```
+-----------------+     +--------------+     +---------------+
| Template        |  +  | Data         |  -> | Configuration |
| Jinja2 / YANG   |     | YAML/JSON/SoT|     | device config |
+-----------------+     +--------------+     +---------------+
      "how"                 "what"                "result"
```

<div class="zh" markdown="1">

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  模板 (Template) │  +  │ 数据 (Data)  │  →  │ 配置 (Config) │
│  Jinja2 / YANG   │     │ YAML/JSON/SoT│     │  设备配置      │
└─────────────────┘     └──────────────┘     └──────────────┘
      "怎么做"                "是什么"              "结果"
```

</div>

**Example: switch baseline template (Jinja2)**

<div class="zh" markdown="1">

**示例：交换机基线模板（Jinja2）**

</div>

```jinja
hostname {{ device.name }}
!
{% for vlan in device.vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% endfor %}
!
{% for intf in device.uplinks %}
interface {{ intf.name }}
 description UPLINK-to-{{ intf.peer }}
 switchport mode trunk
 switchport trunk allowed vlan {{ intf.allowed_vlans | join(',') }}
{% endfor %}
!
ntp server {{ site.ntp }}
logging host {{ site.syslog }}
```

<div class="zh" markdown="1">

```jinja
hostname {{ device.name }}
!
{% for vlan in device.vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% endfor %}
!
{% for intf in device.uplinks %}
interface {{ intf.name }}
 description UPLINK-to-{{ intf.peer }}
 switchport mode trunk
 switchport trunk allowed vlan {{ intf.allowed_vlans | join(',') }}
{% endfor %}
!
ntp server {{ site.ntp }}
logging host {{ site.syslog }}
```

</div>

**The matching data (YAML)**

<div class="zh" markdown="1">

**配套数据（YAML）**

</div>

```yaml
device:
  name: SW-HQ-F1-01
  vlans:
    - { id: 110, name: DATA }
    - { id: 120, name: VOICE }
    - { id: 130, name: GUEST }
  uplinks:
    - { name: Te1/1/1, peer: CORE-01, allowed_vlans: "110,120,130" }
    - { name: Te1/1/2, peer: CORE-02, allowed_vlans: "110,120,130" }
site:
  ntp: 10.0.0.10
  syslog: 10.0.0.20
```

<div class="zh" markdown="1">

```yaml
device:
  name: SW-HQ-F1-01
  vlans:
    - { id: 110, name: DATA }
    - { id: 120, name: VOICE }
    - { id: 130, name: GUEST }
  uplinks:
    - { name: Te1/1/1, peer: CORE-01, allowed_vlans: "110,120,130" }
    - { name: Te1/1/2, peer: CORE-02, allowed_vlans: "110,120,130" }
site:
  ntp: 10.0.0.10
  syslog: 10.0.0.20
```

</div>

> ⚠️ **Never let service data leak into the template.** The test: **if you have to edit the template when you move to another site, the data is in the wrong place.** A template should be common to all sites; only the data changes.

<div class="zh" markdown="1">

> ⚠️ **不要让模板里出现"业务数据"**。判断标准：**如果换一个站点就要改模板，那说明数据放错了位置。** 模板应该对全部站点通用，只有数据变化。

</div>

### Single Source of Truth (SoT) · 单一数据源

**The SoT is the foundation of automation.** It must answer: which devices exist at this site, where every interface of every device connects, where the gateway of each VLAN lives, and what each subnet is for and who owns it.

<div class="zh" markdown="1">

**SoT 是自动化的地基**。它必须回答：这个站点有哪些设备、每台设备的每个接口连到哪里、每个 VLAN 的网关在哪、每个网段的用途与归属。

</div>

| Type | Representatives | Characteristics |
|------|------|------|
| **IPAM/DCIM** | NetBox, Nautobot, Infoblox | Structured database of network objects that can generate configuration |
| **CMDB** | ServiceNow | ITIL-oriented; network granularity is often insufficient |
| **Built into a platform** | SD-WAN controller, DNA Center | Vendor-bound but usable out of the box |
| **YAML in Git** | Home-grown SoT | Lightweight and flexible, but you must build validation and querying |

<div class="zh" markdown="1">

| 类型 | 代表 | 特点 |
|------|------|------|
| **IPAM/DCIM** | NetBox、Nautobot、Infoblox | 网络对象的结构化数据库，可生成配置 |
| **CMDB** | ServiceNow | 面向 ITIL，网络粒度往往不足 |
| **云平台内置** | SD-WAN 控制器、DNA Center | 与厂商绑定，但开箱可用 |
| **Git 中的 YAML** | 自建 SoT | 轻量、灵活；但需自建校验与查询 |

</div>

**The four quality requirements of an SoT**:

<div class="zh" markdown="1">

**SoT 的四条质量要求**：

</div>

1. **Uniqueness**: one fact has exactly one source (do not keep the same IP in Excel, NetBox and a template)
2. **Validatable**: a schema (JSON Schema/YANG) rejects illegal data at the door
3. **Traceable**: changes go through Git/PR with a review record
4. **Consumable**: an API or export mechanism so CI, monitoring and documentation share it

<div class="zh" markdown="1">

1. **唯一性**：一个事实只有一个来源（不要在 Excel、NetBox、模板里各存一份 IP）
2. **可校验**：有 schema（JSON Schema/YANG）校验，非法数据进不来
3. **可追溯**：变更走 Git/PR，有评审记录
4. **可消费**：有 API 或导出机制，供 CI、监控、文档共用

</div>

### Data Layering: Intent, Derived, Device · 数据分层：意图（Intent）、派生（Derived）、设备

**This is the structural problem network IaC gets wrong most often.** Many teams treat "the final device configuration" as the SoT, which is wrong: 80% of a device configuration is **derived from intent** (the VLAN gateway IP, the interface OSPF cost, the ACL match entries). Once derived values are hard-coded, changing one prefix means editing hundreds of records.

<div class="zh" markdown="1">

**这是网络 IaC 最容易被做错的结构问题。** 很多人把"最终设备配置"当成 SoT，这是错的：设备配置里 80% 是**由意图推导出来的**（VLAN 的网关 IP、接口的 OSPF cost、ACL 的匹配项）。一旦把派生值写死，改一个前缀就要改几百份数据。

</div>

| Layer | Content | Written by | Change frequency | Where it lives |
|----|------|------|---------|--------|
| **① Intent layer** | Sites, device roles, VLAN semantics, subnet plan, policy intent ("guests cannot reach the office"), SLAs | Architecture/design team | Low | SoT (NetBox/Git) |
| **② Derived layer** | Gateway IP (subnet +1), interface addresses, routing metrics, concrete ACL entries, template variables | **Computed by automation** (code) | Follows intent | Generated artifacts (never hand-edited) |
| **③ Device layer** | The actual running-config / YANG tree | The device | High (including drift) | The device |

<div class="zh" markdown="1">

| 层 | 内容 | 谁写 | 变更频率 | 存哪里 |
|----|------|------|---------|--------|
| **① 意图层** | 站点、设备角色、VLAN 语义、子网规划、策略意图（"访客不能访问办公"）、SLA | 架构/设计团队 | 低 | SoT（NetBox/Git） |
| **② 派生层** | 网关 IP（子网 +1）、接口地址、路由度量、ACL 具体条目、模板变量 | **自动化计算**（代码） | 跟随意图 | 生成产物（不手改） |
| **③ 设备层** | 实际 running-config / YANG 树 | 设备 | 高频（含漂移） | 设备 |

</div>

**The derivation chain, illustrated**:

<div class="zh" markdown="1">

**推导链条示意**：

</div>

```
intent : site=SH-HQ, vlan=120(name=VOICE, role=user-voice), subnet=10.20.120.0/24
   ↓ (derivation rule: gateway = subnet +1; DHCP = +2; reserve +3 .. +10)
derived: SVI120 = 10.20.120.1/24; dhcp_pool = 10.20.120.10-10.20.120.200
   ↓ (template rendering)
device : interface Vlan120 / ip address 10.20.120.1 255.255.255.0 / ip helper-address ...
```

<div class="zh" markdown="1">

```
意图：site=SH-HQ, vlan=120(name=VOICE, role=user-voice), subnet=10.20.120.0/24
   ↓ (派生规则：网关 = 子网 +1；DHCP = +2；保留 +3 ~ +10)
派生：SVI120 = 10.20.120.1/24；dhcp_pool = 10.20.120.10-10.20.120.200
   ↓ (模板渲染)
设备：interface Vlan120 / ip address 10.20.120.1 255.255.255.0 / ip helper-address ...
```

</div>

> ⚠️ **Anti-pattern**: typing the gateway IP into every SVI of every device in the SoT. With 500 devices that is 1,500 copies, and changing one subnet is guaranteed to break something. **Derived values must be computed by code, never filled in by hand.**

<div class="zh" markdown="1">

> ⚠️ **反模式**：把网关 IP 手工填进 SoT 的每一台设备的每一个 SVI。这样 500 台设备有 1500 个副本，改一个子网必然出错。**派生值必须由代码算，不能由人填。**

</div>

### The SoT Schema: Stopping Illegal Data at the Door · SoT 的 schema：把"非法数据"挡在门口

Data validation is not a nice-to-have; it is **the highest value-per-cost line of defence** (seconds to run, zero risk, stops errors by orders of magnitude).

<div class="zh" markdown="1">

数据校验不是"锦上添花"，它是**最高性价比的一道防线**（秒级、零风险、拦住数量级错误）。

</div>

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["site", "vlan_id", "name", "subnet", "role"],
  "additionalProperties": false,
  "properties": {
    "site":    { "type": "string", "pattern": "^[A-Z]{2}-[A-Z]{3}$" },
    "vlan_id": { "type": "integer", "minimum": 2, "maximum": 4094,
                 "not": { "enum": [1, 1002, 1003, 1004, 1005] } },
    "name":    { "type": "string", "maxLength": 32, "pattern": "^[A-Z0-9_-]+$" },
    "subnet":  { "type": "string",
                 "pattern": "^(\\d{1,3}\\.){3}\\d{1,3}/(1[6-9]|2[0-9]|30)$" },
    "role":    { "enum": ["user-data", "user-voice", "guest", "mgmt",
                          "iot", "wan-transit", "dc-inband"] },
    "dhcp":    { "type": "boolean" }
  }
}
```

<div class="zh" markdown="1">

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["site", "vlan_id", "name", "subnet", "role"],
  "additionalProperties": false,
  "properties": {
    "site":    { "type": "string", "pattern": "^[A-Z]{2}-[A-Z]{3}$" },
    "vlan_id": { "type": "integer", "minimum": 2, "maximum": 4094,
                 "not": { "enum": [1, 1002, 1003, 1004, 1005] } },
    "name":    { "type": "string", "maxLength": 32, "pattern": "^[A-Z0-9_-]+$" },
    "subnet":  { "type": "string",
                 "pattern": "^(\\d{1,3}\\.){3}\\d{1,3}/(1[6-9]|2[0-9]|30)$" },
    "role":    { "enum": ["user-data", "user-voice", "guest", "mgmt",
                          "iot", "wan-transit", "dc-inband"] },
    "dhcp":    { "type": "boolean" }
  }
}
```

</div>

**Beyond the schema, three classes of cross-object validation are mandatory** (a schema cannot express them):

<div class="zh" markdown="1">

**除了 schema，还必须有的三类"跨对象"校验**（schema 表达不了）：

</div>

| Validation type | Example | Tool / implementation |
|---------|------|-------------|
| **Uniqueness** | VLAN IDs unique per site; subnets do not overlap | Custom Python assertions / IPAM API |
| **Referential integrity** | A VLAN referenced by a device must exist; the peer device referenced by an interface must exist | Graph checks (`undef-refs`) |
| **Policy/range** | Management subnets must be inside `allowed_mgmt_prefixes`; VLAN IDs must fall inside the site's block | Policy as Code (OPA or in-house rules) |

<div class="zh" markdown="1">

| 校验类型 | 例子 | 工具/实现方式 |
|---------|------|-------------|
| **唯一性** | 同一站点 VLAN ID 不重复；同一子网不重叠 | 自定义 Python 断言 / IPAM API |
| **引用完整性** | 设备引用的 VLAN 必须存在；接口引用的 peer 设备必须存在 | graph 校验（`undef-refs`） |
| **策略/范围** | 管理网段必须在 `allowed_mgmt_prefixes` 内；VLAN ID 必须落在站点号段 | Policy as Code（OPA/自研规则） |

</div>

### Naming and Numbering Conventions: The Invisible Foundation · 命名与编号规则：自动化的"隐形地基"

In the manual era names can be anything (`SW1`, `sw-hq-1`, `switchA`); in the automated era **the name is the primary key**. A naming convention must satisfy three conditions: **parsable (a machine can split the fields), extensible (you will not run out), readable (a human understands it)**.

<div class="zh" markdown="1">

手工时代命名可以随意（`SW1`、`sw-hq-1`、`交换机A`），自动化时代**名字就是主键**。设计命名规范要满足三个条件：**可解析（机器能拆字段）、可扩展（不会用完）、可读（人能看懂）**。

</div>

| Object | Recommended format | Example | Comment |
|------|---------|----|------|
| Device | `<type>-<site>-<building>-<floor>-<index>` | `SW-SH-HQ-F1-03` | Fixed fields, easy to parse by regex |
| Interface description | `<peer type>-<peer device>-<peer port>` | `UPLINK-SW-SH-HQ-F2-01-Te1/1/1` | Topology can be reverse-engineered from descriptions |
| VLAN | Segmented by site/function | Site block plus function suffix (e.g. 1xx data, 2xx voice) | Avoids cross-site collisions |
| Subnet | Site block plus VLAN segment | Site gets a /16, each VLAN segment takes a /24 | Naturally summarization-friendly |
| Loopback | Planned explicitly in blocks | Segmented by role (core/border/access) | Role is visible at a glance during troubleshooting |

<div class="zh" markdown="1">

| 对象 | 推荐格式 | 例 | 说明 |
|------|---------|----|------|
| 设备 | `<类型>-<站点>-<楼>-<层>-<序号>` | `SW-SH-HQ-F1-03` | 字段固定，方便按正则解析 |
| 接口描述 | `<对端类型>-<对端设备>-<对端端口>` | `UPLINK-SW-SH-HQ-F2-01-Te1/1/1` | 拓扑可由描述反推 |
| VLAN | 按站点/功能分段 | 站点号段 + 功能尾号（如 1xx 数据、2xx 语音） | 避免跨站点冲突 |
| 子网 | 按站点块 + VLAN 段 | 站点拿到 /16，VLAN 段占 /24 | 汇总路由天然友好 |
| Loopback | 显式规划成块 | 按角色分段（核心/边界/接入） | 排障时一眼看角色 |

</div>

> 💡 **VLAN and subnet numbering must reserve gaps** (e.g. leave every tenth number free), otherwise the day the 501st VLAN appears you will find there is nowhere to put it — this kind of numbering collision is a high-frequency incident source when integrating brownfield networks.

<div class="zh" markdown="1">

> 💡 **VLAN/子网编号规则必须"预留空洞"**（如每 10 号留空），否则第 501 个 VLAN 出现时你会发现无处可放 —— 这种"编号冲突"在存量网络整合时是高频事故源。

</div>

### SoT-to-Device Reconciliation (the Reconciliation Loop) · SoT 与设备的对账

**An SoT is only the truth once it has been verified; otherwise it is merely an intention.** So there must be a continuously running reconciliation process:

<div class="zh" markdown="1">

**SoT 只有在"被验证过"的时候才是真相，否则只是意愿。** 所以必须有一条持续运行的对账流程：

</div>

```
1. Compute the "desired state" from the SoT   -> desired config / desired YANG tree
2. Collect the "actual state" from the device -> NETCONF get-config / CLI snapshot
3. Normalize                                 -> strip timestamps, serials, counters, default-value differences
4. Three-way comparison
     desired vs actual        -> drift
     actual vs last actual    -> who changed what (including out-of-band changes)
     actual vs hard rules     -> violations (compliance)
5. Output: drift report / violation list / change timeline
6. Action: alert -> human confirmation -> feed back into the SoT or re-converge
```

<div class="zh" markdown="1">

```
① 从 SoT 计算"期望状态"        → 期望配置 / 期望 YANG 树
② 从设备采集"实际状态"          → NETCONF get-config / CLI 快照
③ 归一化（normalize）           → 去掉时间戳、序列号、计数器、默认值差异
④ 三方比较
    期望 vs 实际   → 漂移（Drift）
    实际 vs 上一版实际 → 谁改了什么（含未纳管变更）
    实际 vs 硬性规则 → 违规（Compliance）
⑤ 输出：漂移报告 / 违规清单 / 变更时间线
⑥ 处置：告警 → 人工确认 → 反哺 SoT 或重新收敛
```

</div>

**Normalization is the hardest step** (and the most underestimated): the same configuration may have a dozen equivalent forms on the device (`switchport trunk allowed vlan 10,20` versus `10-20`, different indentation, hidden or explicit defaults, command order). **If normalization is poor, drift detection becomes thousands of noise entries a day, and after three months nobody reads it.** Practical approach: compare the **structured model** (NETCONF/YANG) first, fall back to text comparison only where the device does not support it, and maintain version-controlled ignore/normalize rules (`ignore-lines`/`normalize rules`).

<div class="zh" markdown="1">

**归一化是最难的一步**（也是最容易被低估）：同一份配置在设备上可能有十几种等价写法（`switchport trunk allowed vlan 10,20` vs `10-20`、缩进不同、默认值显隐、命令顺序）。**如果归一化做不好，漂移检测会变成"每天几千条噪音"，三个月后没人看。** 实用做法：优先比对**结构化模型**（NETCONF/YANG），只有在设备不支持时才退回文本比对，并且必须建立"忽略规则"（`ignore-lines`/`normalize rules`）并纳入版本管理。

</div>

### Read First: The Takeover Path for Brownfield Networks · 只读先行：存量网络（Brownfield）的接管路径

A greenfield network can design its data model from scratch; a brownfield one cannot — your SoT must be **reverse-engineered from the devices**, and what you reverse-engineer will certainly contain contradictions (the same VLAN named differently on different devices, the same subnet appearing at two sites).

<div class="zh" markdown="1">

新建网络可以从零设计数据模型；存量网络不行 —— 你的 SoT 必须**从设备里"反推"出来**，而且反推出来的东西一定有矛盾（同一 VLAN 在不同设备上叫不同名字、同一网段出现在两个站点）。

</div>

| Phase | What to do | Deliverable | Risk |
|------|-------|--------|------|
| **1. Collect** | Pull all configurations, interface tables, ARP/MAC, routing tables, neighbors, versions | A structured "current state" database | None |
| **2. Reverse-engineer** | Infer VLANs/subnets/roles/topology from configuration (interface descriptions + LLDP + CDP) | A candidate SoT, **with conflicts flagged** | None |
| **3. Disambiguate** | Humans confirm the conflicting items (the design team must decide which one is right) | Authoritative SoT v1 | None |
| **4. Compliance** | Rule-based scanning (NTP, SNMP, TACACS, passwords, logging, versions) | Violation list with fix priorities | None |
| **5. Pilot writes** | Start writing with **new devices/new sites, never touching the installed base** | Templates + pipeline | Low |
| **6. Progressive enrollment** | Enroll in batches from low risk to high risk, with assertions in place before each batch | Coverage ramp curve | Medium |
| **7. Freeze manual change** | After an enrolled device is changed, direct CLI edits are forbidden (AAA command authorization + audit) | Governance rules | Medium |

<div class="zh" markdown="1">

| 阶段 | 做什么 | 交付物 | 风险 |
|------|-------|--------|------|
| **1. 采集** | 全量拉取配置、接口表、ARP/MAC、路由表、邻居、版本 | 结构化的"当前状态库" | 无 |
| **2. 反推** | 从配置推断 VLAN/子网/角色/拓扑（接口描述 + LLDP + CDP） | 候选 SoT（**带冲突标记**） | 无 |
| **3. 消歧** | 人工确认冲突项（需要设计团队判断"哪个是对的"） | 权威 SoT v1 | 无 |
| **4. 合规** | 用规则扫描（NTP、SNMP、TACACS、密码、日志、版本） | 违规清单 + 修复优先级 | 无 |
| **5. 试点写** | 从"新设备/新站点"开始写（**不碰存量**） | 模板 + 流水线 | 低 |
| **6. 渐进纳管** | 按"低风险 → 高风险"逐批纳管，每批必须先有断言 | 覆盖率爬升曲线 | 中 |
| **7. 冻结手工** | 纳管设备完成变更后禁止 CLI 直改（AAA 命令授权 + 审计） | 治理规则 | 中 |

</div>

**Key judgement**: **step 3 (disambiguation) is the one most often skipped and the most fatal.** Ship an SoT carrying "two contradictory truths" and the first bulk push spreads the error everywhere. Better to spend two weeks having the design team confirm every row than to gamble.

<div class="zh" markdown="1">

**关键判断**：**第 3 步（消歧）是最容易被跳过、也最致命的一步。** 如果 SoT 里带着"两个互相矛盾的真相"上线，第一次批量下发就会把错误扩散出去。宁可花两周让设计团队逐条确认，也不要赌。

</div>

### The Core Principles of IaC · IaC 的核心原则

| Principle | Explanation |
|------|------|
| **Idempotency** | Running the same code repeatedly produces the same result |
| **Version control** | Infrastructure definitions are stored in a version control system |
| **Declarative vs imperative** | Declarative describes "what you want"; imperative describes "how to do it" |
| **Reusability** | Modular design so pieces can be reused |
| **Auditability** | The change history is traceable |

<div class="zh" markdown="1">

| 原则 | 说明 |
|------|------|
| **幂等性 (Idempotency)** | 多次执行相同代码产生相同结果 |
| **版本控制** | 基础设施定义存储在版本控制系统中 |
| **声明式 vs 命令式** | 声明式描述"想要什么"，命令式描述"怎么做" |
| **可重用** | 模块化设计，可复用 |
| **可审计** | 变更历史可追踪 |

</div>

### IaC Tools and Selection · IaC 工具与选型

| Tool | Type | Agent required | Strengths | Limits | Typical use |
|------|------|-----------|------|------|---------|
| **Ansible** | Declarative (task level) | **Agentless** (SSH/NETCONF/API) | Fast to learn, large ecosystem, many network modules | No state management, average performance at scale | Configuration push, compliance checks, bulk operations |
| **Terraform** | Declarative (resource level) | Agentless (API) | State management, dependency graph, execution plan | **Network device providers vary in maturity** | Cloud networking, SD-WAN, controller-side resources |
| **Nornir** | Imperative (Python framework) | Agentless | Pure Python, maximum control, easy parallelism | No DSL; you write the logic | Complex orchestration, migrations, data processing |
| **Netmiko** | Imperative (library) | Agentless | Works with all kinds of CLI | Screen scraping, fragile | Legacy devices, one-off tasks |
| **NAPALM** | Hybrid abstraction layer | Agentless | Multi-vendor unified interface (get/replace/commit) | Limited device and feature coverage | Vendor-neutral configuration comparison |
| **Cisco NSO** | Declarative (model driven) | Agentless | End-to-end service models, transactional commit | Commercial licence, steep curve | Large SP/enterprise service orchestration |
| **pyATS / Genie** | Verification framework | Agentless | Rich parsers, structured assertions | Test-oriented; does not configure | Post-change validation, regression testing |
| **Git** | Version control | — | Single source of truth, audit | Needs a review process around it | The substrate for all configuration and data |

<div class="zh" markdown="1">

| 工具 | 类型 | 是否有代理 | 优势 | 局限 | 典型用途 |
|------|------|-----------|------|------|---------|
| **Ansible** | 声明式（任务级） | **无代理**（SSH/NETCONF/API） | 上手快、生态大、网络模块多 | 无状态管理、大规模性能一般 | 配置下发、合规检查、批量操作 |
| **Terraform** | 声明式（资源级） | 无代理（API） | 状态管理（state）、依赖图、执行计划（plan） | **网络设备 provider 成熟度参差** | 云网络、SD-WAN、控制器侧资源 |
| **Nornir** | 命令式（Python 框架） | 无代理 | 纯 Python、可控性最强、易并行 | 无 DSL，需自己写逻辑 | 复杂编排、迁移、数据处理 |
| **Netmiko** | 命令式（库） | 无代理 | 兼容各种 CLI | 屏幕抓取（screen scraping），脆弱 | 遗留设备、一次性任务 |
| **NAPALM** | 混合抽象层 | 无代理 | 多厂商统一接口（get/replace/commit） | 支持的设备与特性有限 | 多厂商中立的配置比对 |
| **Cisco NSO** | 声明式（模型驱动） | 无代理 | 端到端服务模型、事务性提交 | 商业许可、学习曲线陡 | 大型 SP/企业服务编排 |
| **pyATS / Genie** | 验证框架 | 无代理 | 解析器丰富、可做结构化断言 | 主要用于测试，不做配置 | 变更后验证、回归测试 |
| **Git** | 版本控制 | — | 单一事实来源、审计 | 需要配套评审流程 | 所有配置与数据的底座 |

</div>

**Selection criteria (the three rules to write into a design)**:

<div class="zh" markdown="1">

**选型判断（写方案时的三条准则）**：

</div>

1. **Start from device capability**: NETCONF/YANG support → prefer model-driven; CLI only → Ansible/Netmiko, and accept the fragility of screen scraping.
2. **Then ask whether you need state**: "create/destroy resources, dependencies, execution plans" → Terraform; simply "push configuration" → Ansible.
3. **Finally, look at the team**: a Python-capable team is more flexible long term with Nornir; an operations-background team will pick up Ansible more easily.

<div class="zh" markdown="1">

1. **先看设备能力**：设备支持 NETCONF/YANG → 优先模型驱动；只有 CLI → Ansible/Netmiko，但必须接受"屏幕抓取"的脆弱性。
2. **再看是否需要状态**：需要"创建/销毁资源、依赖关系、执行计划" → Terraform；只是"把配置推上去" → Ansible。
3. **最后看团队**：会 Python 的团队用 Nornir 长期更灵活；运维背景的团队用 Ansible 更容易接手。

</div>

### Key Ansible Concepts · Ansible 的关键概念

| Concept | Explanation | Design point |
|------|------|---------|
| **Playbook** | YAML task orchestration | One playbook per business action; never write a catch-all script |
| **Inventory** | The list of target devices (can be generated dynamically from the SoT) | **Do not maintain by hand**; pull dynamically from NetBox or the cloud platform |
| **Module** | The code unit that performs a function | Network modules come in two flavours: generic (`cli_command`/`cli_config`) and vendor-specific |
| **Role** | A reusable task bundle (templates, variables, defaults) | Organize by device role (core/access/wan/firewall) |
| **Variables** | Parameterized configuration | Layered variables: group_vars (site) → host_vars (device) → defaults (role) |
| **Facts** | Current state collected from the device | Used to draft configuration and to compare for drift |
| **Check Mode (--check)** | Dry run without pushing | **Limited support on network devices**; cannot be relied on completely |

<div class="zh" markdown="1">

| 概念 | 说明 | 设计要点 |
|------|------|---------|
| **Playbook** | YAML 格式的任务编排 | 一个 playbook 对应一个"业务动作"，不要写"万能脚本" |
| **Inventory** | 目标设备清单（可动态从 SoT 生成） | **不要手工维护**，从 NetBox/云平台动态拉取 |
| **Module** | 执行特定功能的代码单元 | 网络模块分两类：`cli_command`/`cli_config`（通用）与厂商专用模块 |
| **Role** | 可复用的任务集合（含模板、变量、默认值） | 按"设备角色"组织（core/access/wan/防火墙） |
| **Variables** | 参数化配置 | 变量分层：group_vars（站点）→ host_vars（设备）→ defaults（角色） |
| **Facts** | 从设备采集的当前状态 | 用于生成配置草稿、漂移比对 |
| **Check Mode（--check）** | 演练模式，不实际下发 | **网络设备支持有限**，不能完全依赖 |

</div>

**Why Ansible dominates networking**: **it is agentless**. Network devices will practically never run an agent, and Ansible works with only SSH/NETCONF/API — that single fact explains its dominance in this domain.

<div class="zh" markdown="1">

**为什么 Ansible 在网络上流行**：**无代理**。网络设备几乎不可能装 agent，Ansible 只靠 SSH/NETCONF/API 就能工作，这一条决定了它在网络领域的统治地位。

</div>

**A minimal usable directory layout**:

<div class="zh" markdown="1">

**一个最小可用的目录结构**：

</div>

```
network-iac/
├── inventories/
│   └── production/
│       ├── hosts.yml            # generated from the SoT
│       └── group_vars/
│           ├── all.yml          # global: NTP/DNS/AAA
│           └── site_hq.yml      # site level: VLANs, subnets
├── roles/
│   ├── access-switch/
│   │   ├── templates/base.j2
│   │   ├── tasks/main.yml
│   │   └── defaults/main.yml
│   └── core-router/
├── playbooks/
│   ├── deploy-access.yml
│   ├── validate.yml
│   └── compliance.yml
└── tests/                       # integrated with CI
```

<div class="zh" markdown="1">

```
network-iac/
├── inventories/
│   └── production/
│       ├── hosts.yml            # 从 SoT 生成
│       └── group_vars/
│           ├── all.yml          # 全局：NTP/DNS/AAA
│           └── site_hq.yml      # 站点级：VLAN、子网
├── roles/
│   ├── access-switch/
│   │   ├── templates/base.j2
│   │   ├── tasks/main.yml
│   │   └── defaults/main.yml
│   └── core-router/
├── playbooks/
│   ├── deploy-access.yml
│   ├── validate.yml
│   └── compliance.yml
└── tests/                       # 与 CI 集成
```

</div>

### Terraform's State and Its Limits in Network Scenarios · Terraform 的 state 与网络场景的局限

Terraform centres on the **state file** (which resources I manage and what they look like now). That buys two capabilities: an **execution plan** (see what will change first) and **drift detection** (a refresh reveals reality diverging from state).

<div class="zh" markdown="1">

Terraform 的核心是 **state 文件**（记录"我管理了哪些资源、它们现在是什么样"）。它带来两个能力：**执行计划（plan，先看要改什么）** 与 **漂移检测（refresh 后发现现实与 state 不一致）**。

</div>

But two characteristics of network devices make Terraform awkward:

<div class="zh" markdown="1">

但网络设备有两个特点让 Terraform 用起来别扭：

</div>

| Problem | Explanation |
|------|------|
| **Incomplete provider coverage** | Old devices and proprietary features may have no provider, or only partial field coverage |
| **Mapping granularity between state and the real configuration** | A device holds "one whole configuration"; Terraform holds "resources"; some vendor providers model the entire configuration as a single resource |
| **Destructive change risk** | `terraform destroy` is unacceptable in networking |

<div class="zh" markdown="1">

| 问题 | 说明 |
|------|------|
| **Provider 覆盖不全** | 老设备、专有特性可能没有 provider 或只有部分字段 |
| **state 与设备实际配置的映射粒度** | 设备是"一整份配置"，Terraform 是"一个个资源"；部分厂商 provider 会把整份配置当成一个资源 |
| **破坏性变更风险** | `terraform destroy` 在网络里是不可接受的 |

</div>

**Conclusion**: Terraform's strength in networking is **cloud networking, SD-WAN controllers and virtualized network resources**; for configuring traditional devices, Ansible/NSO is more common.

<div class="zh" markdown="1">

**结论**：Terraform 在网络领域的强项是**云网络、SD-WAN 控制器、虚拟化网络资源**；对传统设备的配置管理，Ansible/NSO 更常见。

</div>

### The Git Workflow: Automation's Change Management Vehicle · Git 工作流：自动化的"变更管理"载体

| Practice | How | Why it matters |
|------|------|-----------|
| **Branching strategy** | `main` (production) is protected; changes go on feature branches | Prevents unreviewed configuration reaching production |
| **Pull request** | One PR per change, with the change ticket number and impact scope | Review + audit + discussion trail |
| **Code review** | At least one reviewer (two for critical changes) | Catches logic errors (100× cheaper than finding them in production) |
| **Commit message convention** | `[CHG0012345] add vlan 130 to HQ-F1` | Two-way traceability between ticket and code |
| **Tag / release** | Tag every production rollout | A definite target version for rollback |
| **CI must pass** | lint + syntax + compliance + unit tests | Blocks elementary errors before merge |

<div class="zh" markdown="1">

| 实践 | 做法 | 为什么重要 |
|------|------|-----------|
| **分支策略** | `main`（生产）= 受保护；改动走 feature 分支 | 防止未经评审的配置进生产 |
| **Pull Request** | 每次变更一个 PR，附变更单号与影响范围 | 评审 + 审计 + 讨论留痕 |
| **Code Review** | 至少一人评审（关键变更两人） | 捕获逻辑错误（比现场发现便宜 100 倍） |
| **提交信息规范** | `[CHG0012345] add vlan 130 to HQ-F1` | 变更单与代码双向可追溯 |
| **Tag / Release** | 每次上线打 tag | 回滚有明确目标版本 |
| **CI 必过** | lint + 语法 + 合规 + 单元测试 | 把"低级错误"挡在合并前 |

</div>

> 💡 **Git is the audit log, the rollback point and the collaboration platform of network automation, all in one**. Automation without Git is a fast car without brakes.

<div class="zh" markdown="1">

> 💡 **Git 是网络自动化的"审计日志 + 回滚点 + 协作平台"三合一**。没有 Git 的自动化，等于没有刹车的高速车。

</div>

### Configuration Drift Detection · 配置漂移（Configuration Drift）检测

**Definition of drift**: the actual configuration on the device ≠ the desired configuration (the definition in Git/SoT). Sources: manual hotfixes, failed scripts, vendor default changes, unmanaged changes.

<div class="zh" markdown="1">

**漂移的定义**：设备上的实际配置 ≠ 期望配置（Git/SoT 中的定义）。来源：手工热修、脚本失败、厂商默认值变化、未纳管的变更。

</div>

| Detection method | How | Frequency | Pros | Cons |
|---------|------|------|------|------|
| **Configuration snapshot diff** | Periodically grab `show running-config` and diff against a baseline | Daily/hourly | Simple and direct | Noisy (timestamps, counters, serial numbers) |
| **Model-based comparison** | Fetch structured state via NETCONF/YANG and compare field by field | On demand | Precise, pinpoints the field | Depends on model coverage |
| **Compliance scanning (Policy as Code)** | Scan with rules ("NTP must be configured", "telnet forbidden", password policy) | Daily | Judges "should it be like this", independent of a baseline | You must write the rules |
| **Automated re-push** | Periodically "converge" devices with IaC | Daily | Self-healing | **Dangerous**: may overwrite legitimate manual emergency changes |

<div class="zh" markdown="1">

| 检测方式 | 做法 | 频率 | 优点 | 缺点 |
|---------|------|------|------|------|
| **配置快照比对** | 定期抓 `show running-config`，与基线做 diff | 每天/每小时 | 简单直接 | 噪音大（时间戳、计数器、序列号） |
| **模型化比对** | 通过 NETCONF/YANG 取结构化状态，逐字段比对 | 按需 | 精准、可定位到字段 | 依赖模型覆盖度 |
| **合规扫描（Policy as Code）** | 用规则（如"必须有 NTP""禁止 telnet""密码策略"）扫描 | 每天 | 面向"该不该这样"，不依赖基线 | 需要编写规则 |
| **自动化重下发** | 定期用 IaC "收敛"设备 | 每天 | 自动修复 | **危险**：可能覆盖合法的手工应急变更 |

</div>

> ⚠️ **The biggest trap in drift detection**: **auto-pushing a correction as soon as drift is found**. If the drift is an emergency change an engineer made during an outage, the automatic correction triggers a second outage immediately. **The correct approach is alert + human confirmation + promote the emergency change into Git afterwards** (formalize it).

<div class="zh" markdown="1">

> ⚠️ **漂移检测的最大陷阱**：**发现漂移后自动重下发**。如果漂移是工程师在故障中做的应急修改，自动"纠正"会立刻引发第二次故障。**正确做法是告警 + 人工确认 + 事后反哺到 Git**（把应急变更正式化）。

</div>

---

## CI/CD and the Network Change Pipeline · CI/CD 与网络变更流水线

CI/CD is a way to build, test and deploy changes through automation. In networking it solves one very concrete problem: **how to make "changing configuration" have review, tests and rollback, just like committing code.**

<div class="zh" markdown="1">

CI/CD 是一种通过自动化来构建、测试和部署变更的方法。在网络里，它解决的是一个非常具体的问题：**如何让"改配置"这件事像"提交代码"一样有评审、有测试、有回滚。**

</div>

### Why Networks Need Pipelines More Than Software Does · 网络为什么比软件更需要流水线

| Comparison | Application software | Network configuration |
|-------|---------|---------|
| **Recovery after a mistake** | Redeploy (minutes) | Possibly hours (protocol convergence, session loss, loops) |
| **Test environment** | Easy to duplicate (containers) | Hard to duplicate (needs hardware or a virtualization platform) |
| **Blast radius** | One service | Possibly the whole network or an entire site |
| **Observability** | Complete logs/APM | Distributed and fragmented (needs telemetry to fill the gaps) |
| **Change frequency** | Many times a day | Weekly/monthly, but each change is enormous |

<div class="zh" markdown="1">

| 对比项 | 应用软件 | 网络配置 |
|-------|---------|---------|
| **出错后的恢复** | 重新部署（分钟级） | 可能几小时（协议收敛、会话中断、环路） |
| **测试环境** | 容易复制（容器） | 难复制（需要硬件或虚拟化平台） |
| **影响范围** | 单服务 | 可能是全网或整个站点 |
| **可观测性** | 日志/APM 完整 | 分布式、碎片化（需要遥测补齐） |
| **变更频率** | 每天多次 | 每周/每月，但每次影响巨大 |

</div>

**So the point of CI/CD in networking is not speed — it is eliminating uncertainty before the change.**

<div class="zh" markdown="1">

**因此网络的 CI/CD 重点不是"快"，而是"在变更前把不确定性消灭掉"。**

</div>

### The Seven Stages of the Pipeline · 流水线的七个阶段

```
1. Commit
   Engineer edits YAML/template -> push branch -> open a PR
        ↓
2. Static checks (lint & schema)
   yamllint / ansible-lint / JSON Schema / YANG validation
        ↓
3. Render and preview (diff)
   Template + data -> generated config -> diff against the running config -> "what will change"
        ↓
4. Static analysis (policy and reachability)
   Batfish: reachability, shadowed ACL entries, whether a routing policy breaks a path
        ↓
5. Digital twin / lab validation
   Bring up an equivalent topology in CML / containerlab, run the real config plus automated tests
        ↓
6. Canary rollout (rings)
   Ring 0 (1 device) -> Ring 1 (1 non-critical site) -> Ring 2 (batches) -> Ring 3 (everything)
        ↓
7. Post-change verification and monitoring
   pyATS assertions + telemetry baseline + business probes -> on failure, roll back or roll forward
```

<div class="zh" markdown="1">

```
① 提交（Commit）
   工程师改 YAML/模板 → push 分支 → 建 PR
        ↓
② 静态检查（Lint & Schema）
   yamllint / ansible-lint / JSON Schema / YANG 校验
        ↓
③ 渲染与预览（Render & Diff）
   用模板 + 数据生成配置 → 与设备当前配置做 diff → 输出"将要改什么"
        ↓
④ 静态分析（Policy & Reachability）
   Batfish：可达性、ACL 是否被遮蔽、路由策略是否会断开某条路径
        ↓
⑤ 数字孪生 / 实验室验证
   CML / containerlab 里起同构拓扑，跑真实配置 + 自动化测试
        ↓
⑥ 灰度下发（Canary Rings）
   Ring 0（1 台）→ Ring 1（1 个非关键站点）→ Ring 2（分批）→ Ring 3（全量）
        ↓
⑦ 变更后验证 + 监控
   pyATS 断言 + 遥测基线 + 业务探针 → 失败则回滚/前滚
```

</div>

### The Test Pyramid (Network Edition) · 测试金字塔（网络版）

| Layer | What is tested | Tools | Cost | Problems it catches |
|----|-------|------|------|------------|
| **L1 Syntax/format** | Valid YAML, renderable Jinja2, complete variables | yamllint, ansible-lint, jsonschema | Seconds | Typos, indentation, missing variables |
| **L2 Rendered diff** | Difference between generated and current configuration | Built-in diff, `--check --diff` | Seconds | Accidental deletion, reordering |
| **L3 Intent analysis** | Whether reachability/ACL/routing policy satisfies intent | **Batfish** (offline configuration analysis) | Minutes | "This ACL also blocks the management subnet" |
| **L4 Emulation** | Protocol behaviour in a full topology | CML, EVE-NG, containerlab | Tens of minutes | Neighbors that never come up, routing loops, convergence problems |
| **L5 Canary** | Real devices, small scope | Batched rollout plus assertions | Hours | Hardware/version differences, real traffic effects |
| **L6 Production observation** | Business metrics after full rollout | Telemetry + probes + NetFlow | Continuous | Hidden performance regression, asymmetric paths |

<div class="zh" markdown="1">

| 层 | 测什么 | 工具 | 成本 | 能发现的问题 |
|----|-------|------|------|------------|
| **L1 语法/格式** | YAML 合法、Jinja2 可渲染、变量齐全 | yamllint、ansible-lint、jsonschema | 秒级 | 拼写、缩进、缺变量 |
| **L2 渲染 Diff** | 生成的配置与现状差异 | 自带 diff、`--check --diff` | 秒级 | 意外删除、顺序变化 |
| **L3 意图分析** | 可达性/ACL/路由策略是否满足意图 | **Batfish**（离线配置分析） | 分钟级 | "这条 ACL 把管理网段也拦了" |
| **L4 仿真** | 完整拓扑中协议行为 | CML、EVE-NG、containerlab | 十分钟级 | 邻居起不来、路由环路、收敛问题 |
| **L5 灰度** | 真实设备、小范围 | 分批下发 + 断言 | 小时级 | 硬件/版本差异、真实流量影响 |
| **L6 生产观测** | 全量后的业务指标 | 遥测 + 探针 + NetFlow | 持续 | 隐性性能退化、非对称路径 |

</div>

> 💡 **The three layers with the best return are L1, L2 and L3.** L4 emulation is expensive but extremely valuable; L5 canary is the last airbag. **Doing only L1 and then going straight to production is the most common and most dangerous practice.**

<div class="zh" markdown="1">

> 💡 **投入产出比最高的三层是 L1、L2、L3**。L4 仿真成本高但价值巨大；L5 灰度是"最后的安全气囊"。**只做 L1 + 直接上生产，是最常见也最危险的做法。**

</div>

### Canary Rollout: Turning Blast Radius into a Design Parameter · 灰度发布：把"爆炸半径"变成设计参数

| Ring | Scope | Typical selection criteria | Observation | Rollback trigger |
|------|------|------------|---------|------------|
| **Ring 0** | 1 device | Lab/test unit | 30 min | Any assertion failure |
| **Ring 1** | 1 site | Non-critical, has local support, high tolerance for disruption | 24 h | Business metric drops > 5% |
| **Ring 2** | 10%–30% of sites | By region or batch | 48–72 h | Any P2 or above incident |
| **Ring 3** | Everything | Remaining sites | Continuous | The normal production process |

<div class="zh" markdown="1">

| Ring | 范围 | 典型选择标准 | 观察时长 | 回滚触发条件 |
|------|------|------------|---------|------------|
| **Ring 0** | 1 台设备 | 实验室/测试机 | 30 min | 任何断言失败 |
| **Ring 1** | 1 个站点 | 非关键、有本地支持、业务容忍度高 | 24 h | 业务指标下降 > 5% |
| **Ring 2** | 10%–30% 站点 | 按区域/批次 | 48–72 h | 任何 P2 以上事件 |
| **Ring 3** | 全量 | 剩余站点 | 持续 | 按线上流程 |

</div>

**Three criteria for choosing Ring 1**: ① low business impact (e.g. back-office or test offices); ② people on site (they can console in immediately); ③ representative topology (matches the mainstream site design).

<div class="zh" markdown="1">

**选择 Ring 1 的三条标准**：①业务影响小（如后勤/测试办公区）；②有现场人员（出问题能立刻 console）；③拓扑代表性好（和主流站点架构一致）。

</div>

### Turning Blast Radius into a Computable Quantity · 把"爆炸半径"变成可计算的量

Saying "we will batch it to reduce risk" in a CCDE design is empty; saying "each batch affects at most N users for M minutes" is design. A simple quantitative model:

<div class="zh" markdown="1">

CCDE 方案里说"分批降低风险"是空话，说清"每批最多影响多少用户、多久"才是设计。可以用一个简单的量化模型：

</div>

```
Blast radius (users affected) = batch size (devices)
                              x users per device
                              x failure probability of this change (only if it is actually wrong)
                              x dependency amplification factor (egress/auth/DNS involved -> xN)
```

<div class="zh" markdown="1">

```
爆炸半径（受影响用户数）= 批大小（设备数）
                         × 单设备承载用户数
                         × 该变更的失效概率（仅当它真的错时）
                         × 依赖放大系数（若涉及出口/认证/DNS → ×N）
```

</div>

**A worked comparison**:

<div class="zh" markdown="1">

**算例对比**：

</div>

| Change | Batch size | Users per device | Dependency amplification | Worst case |
|------|-------|-----------|---------|---------|
| Adding a new VLAN to access switches | 20 | 200 | ×1 | 4,000 people (but nobody uses the new VLAN → effectively 0) |
| Changing STP parameters on access switches | 20 | 200 | ×1 | 4,000 people with a brief blip |
| **Core ACL change** | 2 | 20,000 | **×3 (egress/auth/DNS)** | **60,000 people (the whole company)** |
| **DHCP/RADIUS-side change** | 2 | — | **×10 (all new connections)** | **Every new connection company-wide** |
| **Global SD-WAN policy** | 200 sites | 50 | ×1 | **10,000 people plus all voice** |

<div class="zh" markdown="1">

| 变更 | 批大小 | 单设备用户 | 依赖放大 | 最坏影响 |
|------|-------|-----------|---------|---------|
| 接入交换机加 VLAN（新增） | 20 台 | 200 | ×1 | 4000 人（但新 VLAN 无人使用 → 实际 0） |
| 接入交换机改 STP 参数 | 20 台 | 200 | ×1 | 4000 人短暂闪断 |
| **核心 ACL 变更** | 2 台 | 20000 | **×3（含出口/认证/DNS）** | **60000 人（全公司）** |
| **DHCP/RADIUS 侧变更** | 2 台 | — | **×10（所有新接入）** | **全公司新连接受影响** |
| **SD-WAN 全局策略** | 200 站点 | 50 | ×1 | **10000 人 + 全部语音** |

</div>

**Three design conclusions**:

<div class="zh" markdown="1">

**三条设计结论**：

</div>

1. **The dependency amplification factor determines the batch size**: for core, egress, authentication and DNS changes the batch must be one or two devices.
2. **"Adding" is always safer than "modifying"**: add-then-remove is equivalent to splitting one high-risk change into two low-risk ones.
3. **Reversibility beats size**: a 40-device change with `confirmed-commit` timeout rollback is safer than a 2-device change without rollback.

<div class="zh" markdown="1">

1. **"依赖放大系数"决定批大小**：核心/出口/认证/DNS 类变更，批大小必须按 1–2 台算。
2. **"新增"永远比"修改"安全**：先加后删（add-then-remove）等价于把一次高危变更拆成两次低危变更。
3. **可逆性优先于大小**：带 `confirmed-commit` 超时回滚的 40 台变更，比没有回滚的 2 台变更更安全。

</div>

### Pre-flight Checklist · 变更前置检查清单

Make this table into **blocking pipeline checks** (fail = no deployment); it eliminates a whole class of elementary incidents:

<div class="zh" markdown="1">

把这张表做成流水线的**阻断性检查**（fail = 不能下发），能消掉一大类低级事故：

</div>

| # | Check | Blocking condition | Implementation |
|---|------|---------|------|
| 1 | Schema validation passes | Any record illegal | jsonschema |
| 2 | Variable ranges/units sane | Threshold outside min/max, missing units | schema + custom assertions |
| 3 | Device reachable and version matched | Version outside the template support matrix | `show version` / NETCONF capabilities |
| 4 | Existing configuration backed up | Backup failed or absent | Automatic capture archived to object storage |
| 5 | Diff generated and attached to the ticket | No diff, or an empty diff (suspicious) | Render + diff tooling |
| 6 | Management-plane self-reference check | After the change, the automation source cannot reach the device | Batfish reachability / ACL simulation |
| 7 | Dependency check | Referenced VLAN/prefix/policy does not exist | Graph validation |
| 8 | Capacity check | New subnet conflicts with the plan, address pool exhausted | IPAM query |
| 9 | Rollback plan exists | No backup, no rollback commands | Required runbook field |
| 10 | Window and approval | Outside the window, no approval number | ITSM integration |
| 11 | Telemetry baseline exists | Key metrics have no baseline (cannot tell better from worse) | Block if absent from the baseline store |
| 12 | Canary batches defined | No ring assignment | Pipeline variable |

<div class="zh" markdown="1">

| # | 检查 | 阻断条件 | 实现 |
|---|------|---------|------|
| 1 | schema 校验通过 | 任一条不合法 | jsonschema |
| 2 | 变量范围/单位合理 | 阈值超 min/max、单位缺失 | schema + 自定义断言 |
| 3 | 设备可达且版本匹配 | 版本不在模板支持矩阵内 | `show version` / NETCONF capabilities |
| 4 | 已有配置备份 | 备份失败或无备份 | 自动抓取并归档到对象存储 |
| 5 | diff 已生成并附在变更单 | 无 diff 或 diff 为空（可疑） | 渲染 + diff 工具 |
| 6 | 管理面自指校验 | 变更后自动化源不可达设备 | Batfish 可达性 / ACL 模拟 |
| 7 | 依赖检查 | 引用的 VLAN/前缀/策略不存在 | 图校验 |
| 8 | 容量检查 | 新增子网与原规划冲突、地址池耗尽 | IPAM 查询 |
| 9 | 回滚方案存在 | 无备份/无回滚命令 | Runbook 字段必填 |
| 10 | 窗口与审批 | 不在窗口内、无审批号 | ITSM 集成 |
| 11 | 遥测基线存在 | 关键指标无基线（无法判断"变好还是变坏"） | 基线库里查不到即阻断 |
| 12 | 灰度批次已定义 | 无 Ring 划分 | 流水线变量 |

</div>

> 💡 **Items 6 (management-plane self-reference) and 11 (baseline exists) are the two most often omitted.** The first locks you out of your own network; the second leaves you unable to prove afterwards whether the change caused a regression.

<div class="zh" markdown="1">

> 💡 **第 6 项（管理面自指）和第 11 项（基线存在）是最常被遗漏的两项**。前者会让你把自己关在门外，后者会让你在事后无法证明变更是否造成了退化。

</div>

### Change Metrics: Managing Automation as an Engineering Capability · 变更度量：把自动化当成工程能力来管理

The four DORA metrics map directly onto network change and make excellent acceptance criteria for "did the automation project succeed":

<div class="zh" markdown="1">

DORA 的四项指标可以直接搬到网络变更上，而且非常适合作为"自动化项目是否成功"的验收：

</div>

| Metric | Network definition | Manual baseline | Target |
|--------|-----------|---------|------|
| **Lead time for change** | From PR opened to effective in production | 3–10 days | < 1 day |
| **Change frequency** | Production changes per week | 5–20 | Up 3–5× (a side effect, not the goal) |
| **Change failure rate** | Share requiring rollback or causing an incident | 10%–20% | < 5% |
| **Recovery time (MTTR for change)** | From detecting the anomaly to recovery | 2–8 h | < 30 min |

<div class="zh" markdown="1">

| 指标 | 网络版定义 | 手工基线 | 目标 |
|------|-----------|---------|------|
| **变更前置时间** | 从 PR 提出到生产生效 | 3–10 天 | < 1 天 |
| **变更频率** | 每周生产变更次数 | 5–20 次 | 上升 3–5 倍（不是目标本身，是副作用） |
| **变更失败率** | 需要回滚/引发事件的比例 | 10%–20% | < 5% |
| **恢复时间（MTTR for change）** | 从发现异常到恢复 | 2–8 h | < 30 min |

</div>

**All four must be read together**: chasing frequency alone destroys the failure rate; chasing the failure rate alone degenerates into changing nothing. **What automation really improves is the combination of the first two and the last**, with the middle one as the binding constraint.

<div class="zh" markdown="1">

**这四项必须一起看**：只追求"频率"会牺牲失败率；只追求"失败率"会退化成"什么都不改"。**自动化真正改善的是前两项与后一项的组合**，中间那项是关键约束。

</div>

### Roll-back vs Roll-forward · 回滚 vs 前滚

| Strategy | How | Fits | Risk |
|------|------|------|------|
| **Rollback** | Restore the previous configuration (`configure replace` / backup file) | Configuration changes whose failure is detectable | **Protocol state does not roll back** (neighbors rebuilt, sessions already dropped) |
| **Roll-forward** | Fix quickly and push again | Partially effective changes where rollback costs more | Requires fast isolation capability |
| **Hybrid** | Stop the bleeding first (roll back the critical items) then roll forward | Large changes | Requires clear decision criteria |

<div class="zh" markdown="1">

| 策略 | 做法 | 适用 | 风险 |
|------|------|------|------|
| **回滚（Rollback）** | 恢复上一版配置（`configure replace` / 备份文件） | 配置类变更、失败可判定 | **协议状态不可回滚**（邻居重建、会话中断已经发生） |
| **前滚（Roll-forward）** | 快速修复并重新下发 | 变更部分生效、回滚代价更大 | 需要快速定位能力 |
| **混合** | 先止损（回滚关键项）再前滚修复 | 大型变更 | 需要清晰的判据 |

</div>

**Three things that must be defined in advance**:

<div class="zh" markdown="1">

**必须提前定义的三件事**：

</div>

1. **Rollback criteria** (which symptom mandates rollback, and who decides)
2. **Rollback steps** (who executes, how long, whether on-site presence is needed)
3. **Rollback verification** (how you confirm recovery afterwards)

<div class="zh" markdown="1">

1. **回滚判据**（什么现象必须回滚，谁有权决定）
2. **回滚步骤**（谁执行、多长时间、是否需要现场）
3. **回滚验证**（回滚后如何确认恢复）

</div>

> ⚠️ **The most overlooked point about network rollback**: **configuration rollback ≠ state rollback**. Remove a BGP policy and add it back, and the neighbors must re-establish and routes must reconverge — the outage already happened. So **design changes to be incremental and undoable** (for example add a more specific policy first and then remove the old one, instead of replacing a whole block).

<div class="zh" markdown="1">

> ⚠️ **网络回滚最容易被忽略的一点**：**配置回滚 ≠ 状态回滚**。清空 BGP 策略配置后重新加回，BGP 邻居要重新建立、路由要重新收敛，期间的中断已经发生了。所以**变更设计应该尽量"可增量、可撤销"**（例如先加一条更具体的策略再去掉，而不是直接替换整段）。

</div>

### A Realistic Pipeline Example (GitLab CI) · 一个真实可用的流水线示例

```yaml
stages: [lint, render, analyze, deploy-canary, verify, deploy-full]

lint:
  stage: lint
  script:
    - yamllint data/
    - ansible-lint playbooks/
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

render:
  stage: render
  script:
    - python tools/render.py --site $SITE --out build/
    - python tools/diff_config.py --target $DEVICE --candidate build/  # post the diff to the MR
  artifacts:
    paths: [build/]
    expire_in: 7 days

analyze:
  stage: analyze
  script:
    - batfish-run --snapshot build/ --questions reachability,acl,undef-refs
  allow_failure: false

deploy-canary:
  stage: deploy-canary
  script:
    - ansible-playbook -i inv/canary.yml playbooks/deploy-access.yml --limit $CANARY_HOST
  when: manual          # the canary always needs human confirmation

verify:
  stage: verify
  script:
    - pyats run job verify_job.py --testbed canary.yml   # assertions: neighbors, routes, ping, business probes
    - python tools/telemetry_check.py --window 15m

deploy-full:
  stage: deploy-full
  script:
    - ansible-playbook -i inv/prod.yml playbooks/deploy-access.yml --limit $BATCH
  when: manual
  rules:
    - if: $VERIFY_PASSED == "true"
```

<div class="zh" markdown="1">

```yaml
stages: [lint, render, analyze, deploy-canary, verify, deploy-full]

lint:
  stage: lint
  script:
    - yamllint data/
    - ansible-lint playbooks/
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

render:
  stage: render
  script:
    - python tools/render.py --site $SITE --out build/
    - python tools/diff_config.py --target $DEVICE --candidate build/  # 输出 diff 到 MR
  artifacts:
    paths: [build/]
    expire_in: 7 days

analyze:
  stage: analyze
  script:
    - batfish-run --snapshot build/ --questions reachability,acl,undef-refs
  allow_failure: false

deploy-canary:
  stage: deploy-canary
  script:
    - ansible-playbook -i inv/canary.yml playbooks/deploy-access.yml --limit $CANARY_HOST
  when: manual          # 灰度必须人工确认

verify:
  stage: verify
  script:
    - pyats run job verify_job.py --testbed canary.yml   # 断言：邻居、路由、ping、业务探针
    - python tools/telemetry_check.py --window 15m

deploy-full:
  stage: deploy-full
  script:
    - ansible-playbook -i inv/prod.yml playbooks/deploy-access.yml --limit $BATCH
  when: manual
  rules:
    - if: $VERIFY_PASSED == "true"
```

</div>

**Three things this example demonstrates**: ① **rendering and diffing happen inside CI**, so reviewers can see what will happen; ② **both canary and full rollout are manual**, preserving the human veto; ③ **verify is its own stage**, and without passing it the full rollout is impossible.

<div class="zh" markdown="1">

**这个示例的三个要点**：①**渲染与 diff 在 CI 里完成**，评审看得见"将要发生什么"；②**灰度与全量都是 manual**，保留人的否决权；③**verify 是独立阶段**，不通过就不允许进入全量。

</div>

### Typical CI/CD Anti-patterns · CI/CD 的典型反模式

| Anti-pattern | Consequence | Correct approach |
|-------|------|---------|
| **Skipping the diff and pushing** | Accidental deletion of critical configuration | Every change emits a diff for human confirmation |
| **Fully automatic straight to production** | One mistake spreads network-wide | Keep a manual gate for critical changes |
| **Testing syntax but not intent** | Valid configuration, broken service | L3 reachability analysis plus canary |
| **Rollback plan living in someone's head** | Panic during the incident | Rollback steps in the runbook, rehearsed |
| **Treating a green CI as success** | Configuration pushed but not effective | Post-change assertions (verify) |
| **One repository for every environment** | Test configuration pushed to production | Environment isolation (branches or directories plus variables) |
| **Merging without approval** | No audit, unclear accountability | PR plus at least one reviewer |
| **No telemetry** | During an incident you can only guess | Baseline before, compare after |

<div class="zh" markdown="1">

| 反模式 | 后果 | 正确做法 |
|-------|------|---------|
| **跳过 diff 直接下发** | 意外删除关键配置 | 每次变更必须输出 diff 并人工确认 |
| **自动化"全自动"到生产** | 一次错误扩散全网 | 关键变更保留 manual gate |
| **只测语法不测意图** | 配置合法但业务断了 | L3 可达性分析 + 灰度 |
| **回滚方案写在脑子里** | 出事时手忙脚乱 | 回滚步骤进 Runbook 并演练 |
| **CI 通过就当成功** | 配置下去了但没生效 | 必须有变更后断言（verify） |
| **一个仓库管所有环境** | 测试配置误推生产 | 环境隔离（分支或目录 + 变量） |
| **无审批直接合并** | 无审计、责任不清 | PR + 至少一人评审 |
| **遥测缺失** | 出问题只能"猜" | 变更前建立基线，变更后对比 |

</div>

### Verification Deep Dive ①: What Batfish Can and Cannot Answer · 验证层深化①：Batfish 能回答什么、不能回答什么

Batfish's value is **offline configuration analysis** (no real devices, no traffic), but its limits must be documented, otherwise teams misread "CI passed" as "nothing will break".

<div class="zh" markdown="1">

Batfish 的价值在于**离线分析配置**（不需要真实设备、不需要流量），但它的能力边界必须写清楚，否则会误判"CI 通过了就没问题"。

</div>

| Question type | Batfish capability | Comment |
|---------|------------|------|
| **Reachability** | ✅ Precise | "Can A reach B on port 22", hop by hop through ACL/NAT/routing |
| **ACL shadowing/redundancy** | ✅ | Finds entries that can never match (including those blocked by earlier rules) |
| **Routing table (per-device FIB)** | ✅ | Static plus most dynamic protocols (BGP/OSPF/IS-IS/EIGRP) converged offline |
| **Loops/blackholes** | ✅ Partial | Forwarding loops, no-route blackholes, multi-hop dead ends |
| **Configuration differences/undefined references** | ✅ | `undef-refs`: references to ACLs, prefix lists or route-maps that do not exist |
| **Asymmetric paths/path consistency** | ✅ | Computes whether the forward and reverse paths agree |
| **Fault injection (simulate a link down)** | ✅ | "If this link fails, is there a backup path?" — excellent for validating redundancy |
| **Real forwarding behaviour/performance** | ❌ | Sees no hardware, no queues, no chip behaviour |
| **Protocol timing/convergence time** | ❌ | A steady-state snapshot; the convergence process is invisible |
| **Full NAT/tunnel/encryption semantics** | ⚠️ Limited | Complex NAT, IPsec and VXLAN support is limited |
| **Vendor proprietary features** | ⚠️ Limited | The more obscure the feature, the more likely it is "parsed but semantically wrong" |
| **Runtime state** | ❌ | Configuration only, not live neighbors/routes (unless snapshots are imported) |

<div class="zh" markdown="1">

| 问题类型 | Batfish 能做 | 说明 |
|---------|------------|------|
| **可达性** | ✅ 精确 | "A 能否到达 B 的 22 端口"，逐跳考虑 ACL/NAT/路由 |
| **ACL 遮蔽/冗余** | ✅ | 找出永远不会被命中的条目（含被前面规则挡住的） |
| **路由表（每台设备的 FIB）** | ✅ | 静态 + 多数动态协议（BGP/OSPF/IS-IS/EIGRP）的离线收敛 |
| **环路/黑洞** | ✅ 部分 | 转发环路、无路由（blackhole）、多跳死路 |
| **配置差异/未定义引用** | ✅ | `undef-refs`：引用了不存在的 ACL/前缀列表/route-map |
| **非对称路径 / 路径一致性** | ✅ | 能算出双向路径是否一致 |
| **故障注入（模拟某链路 down）** | ✅ | "这条链路断了，还有备用路径吗" —— 非常适合验证冗余设计 |
| **真实转发行为/性能** | ❌ | 不看硬件、不看队列、不看芯片行为 |
| **协议时序/收敛时间** | ❌ | 只看稳态快照，看不到收敛过程 |
| **NAT/隧道/加密的完整语义** | ⚠️ 有限 | 复杂 NAT、IPsec、VXLAN 支持有限 |
| **厂商专有特性** | ⚠️ 有限 | 越冷门的特性越容易"解析了但语义不对" |
| **运行时状态** | ❌ | 只看配置，不看实际邻居/路由（除非导入快照） |

</div>

> ⚠️ **The biggest misuse of Batfish**: treating it as universal verification and therefore skipping emulation and canary. **It can only prove that the configuration, as simulated, is correct — not that the device will execute it as you understand it.**

<div class="zh" markdown="1">

> ⚠️ **Batfish 最大的误用**：把它当成"万能验证"，于是跳过仿真与灰度。**它只能保证"按配置推演是通的"，不能保证"设备按你的理解执行"。**

</div>

### Verification Deep Dive ②: Writing Assertions That Mean Something · 验证层深化②：断言怎么写才有意义

**Three principles for assertion design**:

<div class="zh" markdown="1">

**断言设计的三个原则**：

</div>

1. **Assert business facts, not configuration text** — "the voice gateway is reachable with RTT < 5 ms" is far more meaningful than "an `ip route` line exists".
2. **Assert what must be true; do not chase full coverage** — 20 critical assertions beat 500 brittle ones (the latter cost too much to maintain and end up `skip`ped).
3. **Assertions must be able to fail when things are broken** — after writing one, deliberately inject a fault and confirm it goes red; otherwise you do not know whether it is really running or permanently green.

<div class="zh" markdown="1">

1. **断言"业务事实"，不断言"配置文本"** —— "语音网关可达且 RTT < 5 ms" 比 "有 ip route 命令" 有意义得多。
2. **断言"必须为真"，不追求"全量覆盖"** —— 20 条关键断言胜过 500 条脆弱断言（后者维护成本高，最后被 `skip`）。
3. **断言必须能"在坏的时候失败"** —— 写完断言要**故意注入故障验证它会红**，否则你不知道它是真在跑还是永远绿。

</div>

| Assertion class | Example | Meaning of failure |
|-------|------|---------|
| **Existence** | `all vPC member interfaces state=up` | Missing link or configuration |
| **Count** | `BGP neighbor count = expected (computed from the SoT)` | Missing or extra configuration |
| **State** | `all OSPF neighbors FULL and stable for 5 minutes` | Protocol not converged |
| **Path** | `the next hop for 10.20.0.0/16 must be CORE-01/02 ECMP` | Routing policy changed by mistake |
| **Performance** | `P95 latency < threshold; ECMP traffic imbalance < 20%` | Hidden degradation |
| **Business** | `gate POS transaction success rate > 99.5%` | Real business impact |

<div class="zh" markdown="1">

| 断言层 | 例子 | 失败含义 |
|-------|------|---------|
| **存在性** | `所有 vPC 成员接口 state=up` | 链路/配置缺失 |
| **计数** | `BGP 邻居数 = 期望值（从 SoT 计算）` | 漏配/多配 |
| **状态** | `所有 OSPF 邻居 FULL 且持续 5 分钟` | 协议未收敛 |
| **路径** | `10.20.0.0/16 的下一跳必须是 CORE-01/02 ECMP` | 路由策略被误改 |
| **性能** | `P95 时延 < 阈值；ECMP 流量偏差 < 20%` | 隐性劣化 |
| **业务** | `登机口 POS 交易成功率 > 99.5%` | 真实业务受损 |

</div>

**pyATS assertion skeleton (example)**:

<div class="zh" markdown="1">

**pyATS 断言骨架（示例）**：

</div>

```python
# verify_job.py (excerpt)
from genie.testbed import load

def test_underlay_health(testbed):
    for name, dev in testbed.devices.items():
        dev.connect(log_stdout=False)
        # 1) neighbor count must equal the SoT expectation
        isis = dev.parse("show isis neighbors")
        expected = EXPECTED_NEIGHBORS[name]          # generated from the SoT
        assert len(isis["isis"]) == expected, f"{name} neighbor count mismatch"

        # 2) every uplink must be in ECMP (a path assertion, not a config assertion)
        route = dev.parse("show ip route 10.20.0.0/16")
        nexthops = route["routes"]["10.20.0.0/16"]["next_hop"]["outgoing_interface"]
        assert len(nexthops) == 2, f"{name} ECMP broken"
```

<div class="zh" markdown="1">

```python
# verify_job.py（节选）
from genie.testbed import load

def test_underlay_health(testbed):
    for name, dev in testbed.devices.items():
        dev.connect(log_stdout=False)
        # ① 邻居数必须等于 SoT 期望值
        isis = dev.parse("show isis neighbors")
        expected = EXPECTED_NEIGHBORS[name]          # 从 SoT 生成
        assert len(isis["isis"]) == expected, f"{name} 邻居数不符"

        # ② 每条上行必须有 ECMP（路径断言，不是配置断言）
        route = dev.parse("show ip route 10.20.0.0/16")
        nexthops = route["routes"]["10.20.0.0/16"]["next_hop"]["outgoing_interface"]
        assert len(nexthops) == 2, f"{name} ECMP 失效"
```

</div>

### Verification Deep Dive ③: Digital Twin Fidelity and Cost · 验证层深化③：数字孪生的保真度与成本

A digital twin (CML / EVE-NG / containerlab) validates behaviour on a real protocol stack, but **fidelity comes at a price**:

<div class="zh" markdown="1">

数字孪生（CML / EVE-NG / containerlab）能验证配置在真实协议栈下的行为，但它的**保真度是有代价的**：

</div>

| Fidelity dimension | High fidelity (real gear/high-fidelity emulation) | Low fidelity (virtual/approximate) |
|-----------|---------------------|-------------------|
| Protocol behaviour | Real | Broadly equivalent |
| **Data-plane performance** | Real | **Essentially untrustworthy** (virtual forwarding never touches the ASIC) |
| Vendor proprietary features | Supported | Often missing or incomplete |
| Boot and concurrency | Real | 50 virtual devices is already the cost ceiling |
| Cost | High (hardware/licences) | Low |

<div class="zh" markdown="1">

| 保真度维度 | 高保真（真机/高仿真） | 低保真（虚拟/近似） |
|-----------|---------------------|-------------------|
| 协议行为 | 真实 | 大体一致 |
| **数据面性能** | 真实 | **基本不可信**（虚拟转发不经芯片） |
| 厂商专有特性 | 支持 | 常常缺失或不完整 |
| 启动与并发 | 真实 | 起 50 台虚拟设备已是成本极限 |
| 成本 | 高（硬件/许可） | 低 |

</div>

**Three hard problems in twin design**:

<div class="zh" markdown="1">

**孪生设计的三个硬问题**：

</div>

1. **Synchronization**: is the twin's topology and configuration mirrored from production? A hand-built twin validates a different network. (Practice: generate the twin topology automatically from the SoT plus production snapshots — "twin as code".)
2. **Coverage**: build only the critical subset (core + egress + one representative access block); do not try to mirror the whole network.
3. **Assertion reuse**: the assertions running in the twin must be **the same code** that runs in production, otherwise a green twin says nothing about production.

<div class="zh" markdown="1">

1. **同步性**：孪生里的拓扑和配置是从生产"镜像"过来的吗？如果孪生是手工搭的，它验证的是"另一个网络"。（做法：从 SoT + 生产配置快照自动生成孪生拓扑，做到"孪生即代码"。）
2. **覆盖范围**：只搭关键子集（核心 + 出口 + 一个代表性接入），不要追求全网镜像。
3. **断言复用**：孪生里跑的断言必须和生产里跑的是**同一套代码**，否则孪生通过不代表生产通过。

</div>

> 💡 **A pragmatic layered strategy**: routine changes use **L1+L2+L3 (seconds to minutes)**; **high blast-radius changes** (core, egress, authentication, DNS) additionally go through the twin (L4) and canary (L5); **disaster-recovery switchover changes** require both twin validation and a rehearsal. **Do not demand full-stack validation of every change** — that makes the pipeline so slow nobody uses it.

<div class="zh" markdown="1">

> 💡 **一个务实的分层策略**：日常变更用 **L1+L2+L3（秒到分钟级）**；**高爆炸半径变更**（核心、出口、认证、DNS）额外进孪生（L4）+ 灰度（L5）；**灾备切换类**变更必须孪生 + 演练双份。**不要对所有变更都要求全链路验证** —— 那会让流水线慢到没人用。

</div>

---

## APIs and Data Models · API 与数据模型

### Three Generations of Management Interfaces · 三代管理接口

| Generation | Interface | Data format | Characteristics | Fits |
|------|------|---------|------|------|
| **First** | CLI (SSH/Telnet), SNMP | Text / ASN.1 | Human-readable, machine-hostile; SNMP is monitoring only | Legacy devices, one-off tasks |
| **Second** | **NETCONF** (RFC 6241), **RESTCONF** (RFC 8040) | XML / JSON (+YANG models) | Structured, transactional, validated | Mainstream modern devices |
| **Third** | **gNMI / gRPC** | Protobuf (+YANG paths) | High performance, **streaming telemetry**, bidirectional | Large scale, telemetry-driven |

<div class="zh" markdown="1">

| 代际 | 接口 | 数据格式 | 特点 | 适用 |
|------|------|---------|------|------|
| **第一代** | CLI（SSH/Telnet）、SNMP | 文本 / ASN.1 | 人可读，机器难解析；SNMP 只适合监控 | 遗留设备、一次性任务 |
| **第二代** | **NETCONF**（RFC 6241）、**RESTCONF**（RFC 8040） | XML / JSON（+YANG 模型） | 结构化、事务性、有校验 | 主流现代设备 |
| **第三代** | **gNMI / gRPC** | Protobuf（+YANG 路径） | 高性能、支持**流式遥测**、双向 | 大规模、遥测驱动 |

</div>

### NETCONF: Why It Is the Standard Answer for Network Configuration · NETCONF：为什么它是"网络配置的标准答案"

| Feature | Explanation | Value |
|------|------|------|
| **Transport** | SSH (default port **830**), `netconf` subsystem | Encrypted, reuses the existing operations channel |
| **Datastores** | `running` / `candidate` / `startup` | **candidate** allows edit-then-commit |
| **Transactions** | `commit` is atomic; `:rollback-on-error` | Automatic rollback on failure, no half-applied configuration |
| **Pre-validation** | `:validate`, strict YANG model validation | Illegal configuration rejected before commit |
| **Confirmed commit** | `:confirmed-commit` (auto-rollback if not confirmed in time) | **A lifesaver**: ideal for high-risk remote changes |
| **Capability negotiation** | `<hello>` capability exchange | The client knows which features the device supports |
| **Standard operations** | `get` / `get-config` / `edit-config` / `copy-config` / `lock` / `commit` | Uniform semantics across vendors |

<div class="zh" markdown="1">

| 特性 | 说明 | 价值 |
|------|------|------|
| **传输** | SSH（默认端口 **830**），`netconf` 子系统 | 加密、复用现有运维通道 |
| **数据存储（Datastore）** | `running` / `candidate` / `startup` | **candidate** 允许"先改后提交" |
| **事务性** | `commit` 原子生效；`:rollback-on-error` | 失败自动回滚，不留半成品配置 |
| **预校验** | `:validate`、YANG 模型强校验 | 非法配置在提交前被拒 |
| **确认提交** | `:confirmed-commit`（超时未确认自动回滚） | **救命特性**：适合远程高风险变更 |
| **能力协商** | `<hello>` 交换 capabilities | 客户端可判断设备支持哪些特性 |
| **标准操作** | `get` / `get-config` / `edit-config` / `copy-config` / `lock` / `commit` | 统一语义，跨厂商一致 |

</div>

**The value of `confirmed-commit` (the safety rope of network change)**:

<div class="zh" markdown="1">

**`confirmed-commit` 的价值（网络变更的"安全绳"）**：

</div>

```
1. Push the change with commit confirmed (e.g. 5-minute timeout)
2. If no confirming commit arrives within 5 minutes -> the device rolls back automatically
3. The engineer confirms service health via out-of-band/console or monitoring -> manual confirm
```

<div class="zh" markdown="1">

```
1. 下发变更 + commit confirmed（例如 5 分钟）
2. 若 5 分钟内没有再次 commit 确认 → 设备自动回滚到变更前
3. 工程师通过带外/Console 或监控确认业务正常 → 手动确认
```

</div>

> 💡 This is the standard practice for **remotely configuring firewalls and core devices**: if the configuration cuts your management path, `confirmed-commit` pulls you back automatically. Junos `commit confirmed` and Cisco `configure replace ... timeout` provide the same capability.

<div class="zh" markdown="1">

> 💡 这是**远程配置防火墙/核心设备**时的标准做法：因为一旦配置切断了你的管理通道，`confirmed-commit` 会自动把你"救回来"。Junos 的 `commit confirmed`、Cisco 的 `configure replace ... timeout` 都提供同类能力。

</div>

### RESTCONF: Letting the Web Ecosystem Manage the Network · RESTCONF：让 Web 生态能管网络

| Item | Explanation |
|----|------|
| **Basis** | HTTP/HTTPS plus YANG models, JSON (`application/yang-data+json`) |
| **Method mapping** | GET (read), POST (create), PUT (replace), PATCH (partial update), DELETE (delete) |
| **Path** | `/restconf/data/<module>:<container>/<list>=<key>` |
| **Pros** | Anyone who can write HTTP can use it; easy to integrate with ITSM/automation platforms |
| **Cons** | No candidate/confirmed-commit semantics as in NETCONF (implementation-dependent) |

<div class="zh" markdown="1">

| 项 | 说明 |
|----|------|
| **基础** | HTTP/HTTPS + YANG 模型，JSON（`application/yang-data+json`） |
| **方法映射** | GET（读）、POST（建）、PUT（替换）、PATCH（部分改）、DELETE（删） |
| **路径** | `/restconf/data/<module>:<container>/<list>=<key>` |
| **优点** | 任何会写 HTTP 的人都能上手；易与 ITSM/自动化平台集成 |
| **缺点** | 不支持 NETCONF 的 candidate/confirmed-commit 语义（依赖实现） |

</div>

### gNMI: A Unified Interface for Configuration and Telemetry · gNMI：配置 + 遥测的统一接口

| Operation | Purpose |
|------|------|
| **Capabilities** | Query supported models and encodings |
| **Get** | Read state/configuration |
| **Set** | Update (Replace / Update / Delete) |
| **Subscribe** | **Subscribe to telemetry**: `ONCE` / `POLL` / `STREAM` (`ON_CHANGE` / `SAMPLE` / `TARGET_DEFINED`) |

<div class="zh" markdown="1">

| 操作 | 作用 |
|------|------|
| **Capabilities** | 查询支持的模型与编码 |
| **Get** | 读取状态/配置 |
| **Set** | 更新（Replace / Update / Delete） |
| **Subscribe** | **订阅遥测**：`ONCE` / `POLL` / `STREAM`（`ON_CHANGE` / `SAMPLE` / `TARGET_DEFINED`） |

</div>

**Why gNMI matters**: it unifies configuration and telemetry onto one gRPC channel and addresses data precisely with **YANG paths** (e.g. `/interfaces/interface[name=Gi0/1]/state/counters/in-octets`). That makes **high-frequency, fine-grained, on-demand subscription** possible — which SNMP polling cannot do.

<div class="zh" markdown="1">

**为什么 gNMI 重要**：它把"配置"和"遥测"统一到一条 gRPC 通道上，用 **YANG 路径**（如 `/interfaces/interface[name=Gi0/1]/state/counters/in-octets`）精确定位数据。这使**高频、细粒度、按需订阅**的监控成为可能，而 SNMP 轮询做不到。

</div>

### YANG Models: Three Sources, Three Trade-offs · YANG 模型：三种来源，三种取舍

| Type | Example | Pros | Cons | Fits |
|------|------|------|------|------|
| **Vendor-native models** | `Cisco-IOS-XE-native` | Broadest coverage (all proprietary features) | Vendor lock-in, heavy models | When device-specific features are needed |
| **IETF standard models** | `ietf-interfaces`, `ietf-routing` | Highly standardized | Limited coverage, implementation differences | Common baseline configuration |
| **OpenConfig** | `openconfig-interfaces`, `openconfig-bgp` | **Vendor-neutral**, operations-oriented semantics | Partial support on some devices | Multi-vendor unified automation |

<div class="zh" markdown="1">

| 类型 | 例子 | 优点 | 缺点 | 适用 |
|------|------|------|------|------|
| **厂商原生模型** | `Cisco-IOS-XE-native` | 覆盖最全（含所有专有特性） | 厂商绑定、模型笨重 | 需要设备特有功能 |
| **IETF 标准模型** | `ietf-interfaces`、`ietf-routing` | 标准化程度高 | 覆盖有限、实现差异 | 通用基础配置 |
| **OpenConfig** | `openconfig-interfaces`、`openconfig-bgp` | **厂商无关**、面向运维语义 | 部分设备支持不全 | 多厂商统一自动化 |

</div>

**Recommendation**: **use OpenConfig wherever possible** (cross-vendor, clear semantics); for proprietary features **mix both** (OpenConfig for the baseline, native models for the delta). Note that **vendors may implement the same OpenConfig path differently**, so it must be verified in the lab.

<div class="zh" markdown="1">

**选择建议**：**能用 OpenConfig 就用 OpenConfig**（跨厂商、语义清晰）；需要专有特性时**混合使用**（OpenConfig 做基线 + 原生模型做增量）。注意：**不同厂商对同一 OpenConfig 路径的实现可能不同**，必须实测验证。

</div>

### API Engineering Details: Use the Protocol Correctly, Not Merely "Get It Connected" · API 工程细节：把协议用对，而不是"能连上"

The tables above are concepts; what actually makes a pipeline reliable is these engineering details.

<div class="zh" markdown="1">

上面的表格是概念；真正让流水线稳定的是这些工程细节。

</div>

**① NETCONF locking, concurrency and transactions**

<div class="zh" markdown="1">

**① NETCONF 的锁、并发与事务**

</div>

| Mechanism | Behaviour | Design point |
|---------|------|---------|
| `lock` (candidate or running) | Exclusive; other sessions cannot edit | **Must be released explicitly** (including on error paths), otherwise all later automation is stuck on "lock denied" |
| **Partial lock (RFC 6241)** | Not supported on all devices | Do not assume cross-vendor consistency |
| `commit` atomicity | Changes inside one commit all succeed or all fail | But **there is no cross-device transaction** → multi-device change needs your own compensation/rollback orchestration |
| `confirmed-commit` | Auto-rollback if not confirmed within the timeout | The timeout must cover the worst-case verification time, otherwise it rolls back while you are still reading logs |
| Session timeout (`idle-timeout`) | Long operations get disconnected | Increase it before large pushes, or commit in fragments |
| Performance | One session is serial; round-trip count dominates | Use a **concurrent connection pool** for 500 devices, but cap concurrency (device CPUs and management planes are fragile) |

<div class="zh" markdown="1">

| 机制 | 行为 | 设计要点 |
|------|------|---------|
| `lock`（candidate 或 running） | 独占，其他会话无法编辑 | **必须显式释放**（含异常路径），否则后续所有自动化都卡在"锁被占用" |
| **隐式锁（RFC 6241 partial-lock）** | 部分设备不支持 | 不要假设跨厂商一致 |
| `commit` 原子性 | 一次提交内的变更要么全成功要么全失败 | 但**跨设备没有事务** → 多设备变更必须自己做"补偿/回滚编排" |
| `confirmed-commit` | 超时未确认自动回滚 | 超时值要覆盖"最坏验证时长"，否则你正在看日志时它自己回滚了 |
| 会话超时（`idle-timeout`） | 长耗时操作被踢 | 大配置下发前调大，或分片提交 |
| 性能 | 单会话串行，往返次数决定耗时 | 500 台设备用**并发连接池**，但要限并发（设备 CPU/管理面脆弱） |

</div>

> ⚠️ **The most common production incident**: a script exits abnormally without releasing the candidate lock. The symptom is "it worked yesterday, today every automation run reports lock-denied", and nobody knows who holds the lock (you need `show netconf-yang sessions` or device logs). **Code must release locks in `try/finally`, and you must monitor a "lock hold duration" metric.**

<div class="zh" markdown="1">

> ⚠️ **最常见的生产事故**：脚本异常退出没有释放 candidate 锁。表现是"昨天还好，今天所有自动化报 lock-denied"，且没人知道是谁锁的（要靠 `show netconf-yang sessions` 或设备日志）。**代码必须有 `try/finally` 释放锁，并且监控"锁占用时长"指标。**

</div>

**② Dividing the work between gNMI and NETCONF**

<div class="zh" markdown="1">

**② gNMI 与 NETCONF 的分工**

</div>

| Use | Choice | Reason |
|------|------|------|
| Configuration push (needs transactions/validation) | **NETCONF** | candidate + confirmed-commit + YANG validation |
| High-frequency telemetry | **gNMI** | STREAM subscription, low overhead, Protobuf compression |
| Lightweight queries (HTTP ecosystem) | RESTCONF | Easy integration with ITSM/portals |
| Unified configuration + telemetry channel | gNMI Set + Subscribe | One fewer dependency, but confirm the device implementation is complete |

<div class="zh" markdown="1">

| 用途 | 选谁 | 理由 |
|------|------|------|
| 配置下发（需要事务/校验） | **NETCONF** | candidate + confirmed-commit + YANG 校验 |
| 高频遥测 | **gNMI** | STREAM 订阅、低开销、Protobuf 压缩 |
| 轻量查询（HTTP 生态） | RESTCONF | 与 ITSM/门户集成方便 |
| 配置 + 遥测统一通道 | gNMI Set + Subscribe | 少一套依赖，但要确认设备实现完备 |

</div>

**③ Model version evolution (where upgrades break automation most often)**

<div class="zh" markdown="1">

**③ 模型版本演进（自动化最容易被"升级"打垮的地方）**

</div>

After a device upgrade, the YANG paths you depend on may have changed. Three things are mandatory:

<div class="zh" markdown="1">

设备升级后，你依赖的 YANG 路径可能变了。必须准备的三件事：

</div>

1. **Capability matrix and gate**: before pushing, the pipeline reads the `<hello>` capabilities and checks the required models and versions; devices outside the matrix are **rejected outright**, not "given a try".
2. **YANG deviations and unsupported nodes**: the same model may carry `deviation` on different devices (a node is unsupported). Maintain a list of what is actually supported — generated from testing, not copied from documentation.
3. **Compatibility window**: during an upgrade, support both model version N and N+1, and branch in the template on capability — **never on device model** (identical models can run different versions).

<div class="zh" markdown="1">

1. **能力矩阵与门禁**：流水线在下发前读 `<hello>` 的 capabilities，检查必需模型与版本；不在矩阵内的设备**直接拒绝下发**，而不是"试试看"。
2. **YANG deviation 与不支持项**：同一模型在不同设备上可能有 `deviation`（不支持某节点）。要维护一张"实际支持项"清单（实测生成，不是抄文档）。
3. **兼容窗口**：升级期间同时支持 N 和 N+1 两个模型版本，模板里用 capability 判断分支，**不要用设备型号判断**（型号相同但版本不同）。

</div>

**④ The OpenConfig "hands-on checklist" (mandatory for every new platform)**

<div class="zh" markdown="1">

**④ OpenConfig"实测清单"（每个新平台上线必做）**

</div>

| Test item | How | Pass criteria |
|-------|------|---------|
| Read: full configuration tree | `get` on the root path | No timeout, complete fields |
| Write: interface description | `Set/Update` a single leaf | Effective, and no other field changed |
| Write: list entry add/remove | Add and remove a VLAN/subinterface | Idempotent (replay changes nothing) |
| Delete semantics | Delete a container | Only the target is deleted; no cascading damage |
| Validation rejection | Deliberately write an illegal value (VLAN 5000) | Rejected with an error path |
| Concurrency | Two sessions writing different subtrees | No mutual blocking, or a clear error |
| Telemetry | Subscribe to a counter with 10 s sampling | Continuous data, no dropped samples, acceptable CPU |
| Consistency | Cross-check with CLI after writing | Both views agree (guard against "the model accepted it but it never reached the running config") |

<div class="zh" markdown="1">

| 测试项 | 做法 | 通过标准 |
|-------|------|---------|
| 读：全量配置树 | `get` 根路径 | 无超时、字段完整 |
| 写：接口描述 | `Set/Update` 单个叶子 | 变更生效且不误改其他字段 |
| 写：列表项增删 | 增删一个 VLAN/子接口 | 幂等（重放无变化） |
| 删除语义 | Delete 一个 container | 只删目标，不级联误删 |
| 校验拒绝 | 故意写非法值（VLAN 5000） | 被拒绝且给出错误路径 |
| 并发 | 两个会话同时写不同子树 | 不互相阻塞或明确报错 |
| 遥测 | 订阅计数器 10 s 采样 | 数据连续、无丢样、CPU 可接受 |
| 一致性 | 写入后用 CLI 核对 | 两处视图一致（防止"模型写了但没落到运行配置"） |

</div>

### Telemetry: From Polling to Streaming · 遥测：从"轮询"到"流式"

| Dimension | SNMP polling | Model-driven telemetry (MDT / gNMI) |
|------|----------|--------------------------|
| **Model** | Pull | Push, with subscription as well |
| **Granularity** | 5 minutes (limited by device and scale) | **Seconds or even sub-second** |
| **Overhead** | Full table walk per poll, high CPU | Pushes only changes or samples, low overhead |
| **Data types** | Counters (integers) | Counters + state + events + structured models |
| **Scalability** | Collector pressure grows with device count | Supports dial-out: devices push to the collector |
| **Typical problem** | Peaks are averaged away; transient congestion invisible | Requires collector capacity and data-pipeline planning |

<div class="zh" markdown="1">

| 维度 | SNMP 轮询 | 模型驱动遥测（MDT / gNMI） |
|------|----------|--------------------------|
| **模型** | 拉（Poll） | 推（Push），也支持订阅 |
| **粒度** | 5 分钟（受设备与规模限制） | **秒级甚至亚秒级** |
| **开销** | 每次轮询全表遍历，CPU 高 | 只推送变化量或采样，开销低 |
| **数据类型** | 计数器（整数） | 计数器 + 状态 + 事件 + 结构化模型 |
| **扩展性** | 设备多时采集器压力大 | 支持 dial-out，设备主动推给采集器 |
| **典型问题** | 峰值被平均掉、看不到瞬时拥塞 | 需要规划采集器容量与数据管道 |

</div>

**The three subscription modes of telemetry**:

<div class="zh" markdown="1">

**遥测的三种订阅模式**：

</div>

- **ON_CHANGE**: push when the value changes (good for interface up/down, BGP state)
- **SAMPLE (periodic)**: push at a fixed interval (good for traffic counters)
- **TARGET_DEFINED**: decided by the device (vendor-recommended values)

<div class="zh" markdown="1">

- **ON_CHANGE**：值变化就推（适合接口 up/down、BGP 状态）
- **SAMPLE（周期采样）**：固定间隔推（适合流量计数器）
- **TARGET_DEFINED**：由设备决定（厂商推荐值）

</div>

> 💡 **Telemetry is the eyes of automation.** Automation without telemetry can push but cannot verify — driving with a blindfold. The design order should be: **observability first → then configuration automation → then closed-loop self-healing.**

<div class="zh" markdown="1">

> 💡 **遥测是自动化的"眼睛"**。没有遥测的自动化只能"下发"不能"验证"，等于蒙着眼睛开车。设计顺序应该是：**先建可观测性 → 再做配置自动化 → 最后做闭环自愈**。

</div>

### The Capacity Arithmetic of Telemetry Engineering: Do Not Turn Streaming into Expensive Polling · 遥测工程的容量账：别把推流做成"更贵的轮询"

**This is the most common way telemetry projects fail**: after moving from SNMP to gNMI, the number of metrics grows 50× and the interval drops from 300 s to 10 s — and the **collector collapses first**, followed by the device management-plane CPU pinning.

<div class="zh" markdown="1">

**这是遥测项目最常见的翻车点**：从 SNMP 换成 gNMI 之后，采集的指标数量翻了 50 倍、采样间隔从 300 s 变成 10 s，结果**采集器先崩了**，接着设备管理面 CPU 打满。

</div>

**Step one: compute the sample rate**

<div class="zh" markdown="1">

**第一步：算样本速率**

</div>

```
Sample rate (samples/s) = devices x subscribed paths per device x (1 / sampling interval)
```

<div class="zh" markdown="1">

```
样本速率（samples/s） = 设备数 × 每设备订阅路径数 × (1 / 采样间隔)
```

</div>

| Scenario | Devices | Paths/device | Interval | Samples/s | Comment |
|------|------|----------|------|--------|------|
| Conservative | 200 | 50 | 60 s | 167 | A single collector can carry it |
| Moderate | 500 | 200 | 30 s | 3,333 | Needs a collector cluster (3–5 nodes) |
| Aggressive | 2,000 | 500 | 10 s | **100,000** | Needs tiered collection + aggregation + storage planning |
| Out of control | 2,000 | 2,000 | 1 s | **4,000,000** | **Guaranteed failure**: device CPU, network and storage all collapse |

<div class="zh" markdown="1">

| 场景 | 设备 | 路径/设备 | 间隔 | 样本/秒 | 说明 |
|------|------|----------|------|--------|------|
| 保守 | 200 | 50 | 60 s | 167 | 单机可承载 |
| 中等 | 500 | 200 | 30 s | 3,333 | 需要采集器集群（3–5 节点） |
| 激进 | 2000 | 500 | 10 s | **100,000** | 需要分层采集 + 聚合 + 存储规划 |
| 失控 | 2000 | 2000 | 1 s | **4,000,000** | **必然失败**：设备 CPU、网络、存储全线崩塌 |

</div>

**Step two: compute the bandwidth**

<div class="zh" markdown="1">

**第二步：算带宽**

</div>

```
Bandwidth ≈ samples/s x (path encoding + value + timestamp ≈ 200–400 B after Protobuf compression)
100,000 samples/s x 300 B ≈ 30 MB/s ≈ 240 Mbps (sustained!)
```

<div class="zh" markdown="1">

```
带宽 ≈ 样本数/秒 × (路径编码 + 值 + 时间戳 ≈ 200–400 B，Protobuf 压缩后)
100,000 samples/s × 300 B ≈ 30 MB/s ≈ 240 Mbps（持续！）
```

</div>

That magnitude means **telemetry traffic itself becomes a significant load on link bandwidth and device CPU** (especially on low-end access devices with weak management CPUs).

<div class="zh" markdown="1">

这个量级意味着：**遥测流量本身会成为链路带宽与设备 CPU 的可观开销**（尤其低端接入设备，管理面 CPU 很弱）。

</div>

**Step three: a four-layer throttling strategy**

<div class="zh" markdown="1">

**第三步：四层节流策略**

</div>

| Layer | Strategy | Effect |
|----|------|------|
| **Source** | Subscribe only to the metrics decisions need, not to everything available | 80%+ reduction |
| **Granularity** | Counters as SAMPLE (30–60 s), state as ON_CHANGE | Objects that rarely change cost almost nothing |
| **Aggregation** | Edge collectors aggregate first (P95/max) and forward only the results | An order of magnitude less storage and bandwidth |
| **Tiering** | Fine granularity on core/egress (10 s), coarse on access (60 s) | Precision where the critical path is |

<div class="zh" markdown="1">

| 层 | 策略 | 效果 |
|----|------|------|
| **源头** | 只订阅"决策需要的指标"，不订阅"能拿到的全部指标" | 减少 80% 以上 |
| **粒度** | 计数器用 SAMPLE（30–60 s），状态用 ON_CHANGE | 变化少的对象几乎零开销 |
| **聚合** | 边缘采集器先聚合（P95/最大值），只把聚合结果上送 | 存储与带宽降一个量级 |
| **分层** | 核心/出口细粒度（10 s），接入粗粒度（60 s） | 关键路径保精度 |

</div>

**Step four: four design judgements about telemetry**

<div class="zh" markdown="1">

**第四步：遥测的四条设计判断**

</div>

1. **Telemetry is not "more data is better"; it is "the shorter the decision chain the better".** If no alert, assertion or automated action consumes a metric, do not collect it.
2. **You must monitor the telemetry pipeline itself**: subscription state on the device, collection success rate, end-to-end latency, sample loss. Otherwise, when the pipeline breaks you will think the network is quiet.
3. **Keep a degraded path**: SNMP/CLI fallback collection when gNMI dies, otherwise automation goes blind exactly during an incident.
4. **Tiered retention**: raw samples 7–30 days, aggregates one year, change/event records forever (these are what post-incident reviews depend on).

<div class="zh" markdown="1">

1. **遥测不是"数据越多越好"，是"决策链越短越好"**。一个指标如果没有任何告警、断言或自动化动作消费它，就不要采。
2. **必须监控"遥测管道自身"**：设备侧订阅状态、采集成功率、端到端延迟、丢样率。否则管道断了你会以为"网络很安静"。
3. **保留降级通道**：gNMI 挂了还能用 SNMP/CLI 做兜底采集，否则自动化在故障时反而"全盲"。
4. **数据保留分级**：原始样本保留 7–30 天，聚合值保留 1 年，变更/事件记录永久（这是事后复盘的关键）。

</div>

### The Boundaries of Closed-Loop Self-Healing: What May Be Changed Automatically, and What Never · 闭环自愈的边界：什么能自动改，什么永远不能

Maturity level L4 (closed-loop self-healing) is the endpoint of many proposals, but **the scope it can cover is much smaller than people imagine**.

<div class="zh" markdown="1">

自动化成熟度 L4（闭环自愈）是很多方案的终点，但**它能覆盖的范围比想象的小得多**。

</div>

| Object | Self-healable | Conditions | Risk |
|------|---------|------|------|
| **NTP/DNS/logging/AAA server addresses** | ✅ Yes | Target values come from the SoT, the action is idempotent | Low |
| **Non-conforming interface descriptions** | ✅ Yes | Description changes only | Very low |
| **Recovery from port err-disable** | ⚠️ Cautiously | Needs a "root cause is gone" criterion plus a retry cap | Medium (may mask a real fault) |
| **BGP/OSPF neighbor reset** | ⚠️ Cautiously | `clear` only, rate-limited, needs a circuit breaker | Medium-high |
| **Routing metrics/routing policy** | ❌ Should not | Business intent cannot be judged automatically | High |
| **ACL/security policy** | ❌ Should not | Security policy change is a business decision | Very high |
| **QoS/bandwidth allocation** | ❌ Should not | Involves commercial priority | High |
| **Device reload/version rollback** | ❌ Should not | Destructive and irreversible | Very high |

<div class="zh" markdown="1">

| 对象 | 能否自愈 | 条件 | 风险 |
|------|---------|------|------|
| **NTP/DNS/日志/AAA 服务器地址** | ✅ 可以 | 目标值来自 SoT，动作幂等 | 低 |
| **接口描述不规范** | ✅ 可以 | 只改描述 | 极低 |
| **端口 err-disable 恢复** | ⚠️ 谨慎 | 必须有"根因已消失"判据 + 次数上限 | 中（可能掩盖真故障） |
| **BGP/OSPF 邻居重启** | ⚠️ 谨慎 | 只做 `clear` 且限次，需熔断 | 中高 |
| **路由度量/路由策略** | ❌ 不应 | 业务意图无法自动判断 | 高 |
| **ACL/安全策略** | ❌ 不应 | 安全策略变更是业务决策 | 极高 |
| **QoS/带宽分配** | ❌ 不应 | 涉及商业优先级 | 高 |
| **设备重启/版本回退** | ❌ 不应 | 破坏性、不可逆 | 极高 |

</div>

**Three prerequisites for enabling self-healing** (all are required):

<div class="zh" markdown="1">

**开启自愈的三个必要条件**（缺一不可）：

</div>

1. **An unambiguous failure mode**: the alert maps uniquely to a definite cause and a definite action (not "looks like").
2. **Idempotent and bounded actions**: repeating the action gives the same result; there is a retry cap (e.g. at most three per hour) and a circuit breaker (stop and call a human).
3. **Rollback and trail**: automatic backup before the action, automatic verification after it, and a full record (who triggered it, what changed).

<div class="zh" markdown="1">

1. **故障模式明确**：告警能唯一映射到"确定的原因 + 确定的动作"（不是"看起来像"）。
2. **动作幂等且有界**：同样的动作重复执行结果一致；有次数上限（如每小时最多 3 次）与熔断（超过就停下等人）。
3. **有回退与留痕**：动作前自动备份、动作后自动验证、全程记录（谁触发、改了什么）。

</div>

> ⚠️ **The most dangerous shape of self-healing is oscillation**: flapping → automatic neighbor reset → more flapping → reset again. **A circuit breaker and reverse indicators are mandatory** (e.g. "if the problem recurs within 10 minutes of a self-healing action, stop immediately and escalate to a human").

<div class="zh" markdown="1">

> ⚠️ **自愈最危险的形态是"振荡"**：网络抖动 → 自动重启邻居 → 更多抖动 → 再重启。**必须有熔断器与"反向指标"**（如"自愈动作后 10 分钟内问题复发 → 立即停止并升级到人"）。

</div>

---

## Automation Platform Security and Governance · 自动化平台的安全与治理

One hidden consequence of automation: **it converts human authority into platform authority**. A service account that can change configuration on 500 devices is the most dangerous account in the network. Security design must therefore proceed in step with configuration design.

<div class="zh" markdown="1">

自动化的一个隐性后果：**它把"人的权限"变成了"平台的权限"**。一个能改 500 台设备配置的服务账号，是全网最危险的账号。所以安全设计必须和配置设计同步。

</div>

### Credentials and Keys: Never in Git · 凭据与密钥：绝不能进 Git

| Anti-pattern | Consequence | Correct approach |
|-------|------|---------|
| Credentials in `group_vars`/`.env` committed to Git | **Permanently leaked in history** (deleting them does not help) | Secret manager (Vault/cloud KMS/CI variables), injected at runtime |
| Everyone sharing one admin credential | Cannot audit to a person; offboarding risk | One service account per task class, bound to its purpose |
| Clear-text `enable` password | Leaks via screen or logs | Encrypted secret storage, log redaction |
| Keys that never expire | A leak stays valid forever | Regular rotation plus rotation rehearsals (prove rotation does not break the pipeline) |
| Logging full request bodies | Credentials land in the log platform | Log redaction (mask passwords, community strings, SNMP, certificate fields) |

<div class="zh" markdown="1">

| 反模式 | 后果 | 正确做法 |
|-------|------|---------|
| 凭据写进 `group_vars`/`.env` 提交到 Git | **历史记录永久泄露**（删掉也没用） | secret 管理器（Vault/云 KMS/CI 变量），运行时注入 |
| 所有人共用一套 admin 凭据 | 无法审计到人，离职风险 | 每类任务一个服务账号，绑定用途 |
| 用 `enable` 明文密码 | 屏幕/日志泄露 | secret 走加密存储，日志脱敏 |
| 密钥不过期 | 泄露后长期有效 | 定期轮换 + 轮换演练（要验证轮换不中断流水线） |
| 日志打印完整请求体 | 凭据进日志平台 | 日志脱敏（密码/community/SNMP/证书字段屏蔽） |

</div>

> 💡 **How to judge an enterprise's automation security hygiene: search its Git history for `password`.** If you find it, their automation project fails a security review — and the leak is **permanent** (rewriting history requires coordinating every branch and every clone).

<div class="zh" markdown="1">

> 💡 **判断一家企业的自动化安全水位：搜一下 Git 历史里有没有 `password`。** 有的话，说明他们的自动化项目在安全评审里是不合格的 —— 而且这个泄露是**永久性的**（重写历史需要协调所有分支与所有克隆）。

</div>

### Least Privilege and Audit: Drawing the Boundary Around the Automation Account · 最小权限与审计：给自动化账号划边界

| Privilege layer | Design | Reason |
|-------|------|------|
| **Network reachability** | Permit 22/830/443/57400 only from the orchestration subnet | Reduce the exposure surface |
| **AAA authorization** | TACACS+ command sets/roles: may change service configuration, **may not change local accounts, may not erase, may not modify AAA itself** | Prevent automation from destroying your ability to recover |
| **Domain separation** | Separate accounts for production and test; scoped per site | Prevent test scripts from pushing to production |
| **Session audit** | Tag automation sessions separately; retain commands and responses in full | Attribute afterwards "which task changed this" |
| **Approval coupling** | High-risk command sets require a ticket number (passed as a variable and validated) | Makes "there is a change ticket" technically enforced, not a convention |

<div class="zh" markdown="1">

| 权限层 | 设计 | 理由 |
|-------|------|------|
| **网络可达性** | 只允许从编排网段访问 22/830/443/57400 | 缩小暴露面 |
| **AAA 授权** | TACACS+ 命令集/角色：可改业务配置，**不可改本地账号、不可 erase、不可改 AAA 本身** | 防止自动化改掉"恢复能力" |
| **分域权限** | 生产/测试不同账号；不同站点范围隔离 | 防止测试脚本误推生产 |
| **会话审计** | 自动化会话单独打标、完整留存命令与响应 | 事后定位"是哪个任务改的" |
| **审批联动** | 高危命令集需要工单号（作为变量传入并校验） | 让"有变更单"成为技术强制而非流程约定 |

</div>

**The critical design judgement**: **the automation account must not be able to break itself out of business** — it must not modify AAA, the management interface IP, or the VLAN/ACL that carries the management path. Otherwise a single script error leaves you **unable to fix anything** (as happened for real in Case 3).

<div class="zh" markdown="1">

**关键设计判断**：**automation 账号必须"改不坏自己"** —— 不能修改 AAA、不能改管理接口 IP、不能改承载管理通道的 VLAN/ACL。否则一次脚本错误会导致**丧失修复能力**（案例三里已经实战发生过一次）。

</div>

### Supply Chain and Code Integrity · 供应链与代码本身的完整性

The automation platform is itself part of the software supply chain:

<div class="zh" markdown="1">

自动化平台现在也是"软件供应链"的一部分：

</div>

| Risk | Explanation | Mitigation |
|-------|------|------|
| **Third-party collections/roles** | Ansible collections pulled from the community can be poisoned | Pin versions + internal proxy/mirror + code scanning |
| **Container images** | Orchestration tool images of unknown provenance | Fixed tags + image signing + scanning |
| **Template repository rights** | Being able to merge a PR means being able to change the whole network | Branch protection + at least one reviewer + CODEOWNERS on critical paths |
| **CI runner privileges** | The runner holds production credentials | Runner isolation, credentials injected only in the deploy stage, short-lived tokens |
| **AI-generated code** | Hallucinations, outdated APIs, insecure defaults | Mandatory review + lint + unit tests; never straight to production |

<div class="zh" markdown="1">

| 风险点 | 说明 | 缓解 |
|-------|------|------|
| **第三方 collection/role** | 从社区拉取的 Ansible collection 可能被投毒 | 锁定版本 + 内部源（proxy/mirror）+ 代码扫描 |
| **容器镜像** | 编排工具镜像来源不明 | 固定 tag + 镜像签名 + 扫描 |
| **模板仓库权限** | 能合并 PR 就等于能改全网 | 分支保护 + 至少一人评审 + 关键路径 CODEOWNERS |
| **CI runner 权限** | runner 持有生产凭据 | runner 隔离、凭据只在部署阶段注入、临时令牌 |
| **AI 生成的代码** | 幻觉/过时 API/不安全默认值 | 强制评审 + lint + 单元测试 + 绝不直接进生产 |

</div>

### Automation Platform Availability and Operating Model · 自动化平台的可用性与运营模型

| Concern | Requirement | How to verify |
|-------|------|---------|
| **Platform HA** | Multiple orchestration/controller instances, recoverable configuration and credentials | Kill the primary node and measure failover time |
| **Data backup** | Backups of SoT, Git, CI configuration and secret store, with rehearsed restore | A twice-yearly "rebuild the platform from backup" drill |
| **Break-glass path** | A manual runbook for a total platform outage (jump hosts, credential retrieval, verification steps) | **Must be rehearsed**, with date and outcome recorded |
| **Change freeze mechanism** | No automated changes during peak events or month-end close | The pipeline reads a freeze calendar and rejects non-allowlisted changes |
| **Responsibility model** | Platform team (capability) + network team (content) + security team (policy) | Explicit who approves template changes and who approves data changes |
| **On-call and alerting** | Alerts for pipeline failures, held locks, telemetry gaps | Monthly "top 5 pipeline failure causes" report |

<div class="zh" markdown="1">

| 关注项 | 要求 | 检验方法 |
|-------|------|---------|
| **平台 HA** | 编排/控制器多实例、配置与凭据可恢复 | 杀掉主节点，验证故障切换时间 |
| **数据备份** | SoT、Git、CI 配置、凭据库的备份与恢复演练 | 半年一次"从备份重建平台"演练 |
| **break-glass 路径** | 平台全挂时的手工操作手册（含跳板机、凭据获取、验证步骤） | **必须演练**，并记录演练时间与结果 |
| **变更冻结机制** | 大促/月末结账等窗口内禁止自动化变更 | 流水线读取"冻结日历"，非白名单变更直接拒绝 |
| **责任模型** | 平台团队（能力）+ 网络团队（内容）+ 安全团队（策略） | 明确谁批准模板变更、谁批准数据变更 |
| **值班与告警** | 流水线失败、锁占用、遥测断流都要告警 | 每月统计"流水线失败原因 Top 5" |

</div>

**Three common organisational models**:

<div class="zh" markdown="1">

**三种常见的组织模式**：

</div>

| Model | Structure | Pros | Cons |
|------|------|------|------|
| **Centralized (CoE)** | One automation team serving all network teams | Uniform standards, deep expertise | Becomes a bottleneck, far from the business |
| **Platform as a product** | A platform team builds the product (templates, CI, SoT); network teams self-serve | Scales well, clear ownership | The platform must genuinely be usable, or people bypass it |
| **Decentralized** | Every team does its own | Fast to start | Three years later: five toolchains and three data copies (straight back to trap number one) |

<div class="zh" markdown="1">

| 模式 | 结构 | 优点 | 缺点 |
|------|------|------|------|
| **集中式（CoE）** | 一个自动化团队服务所有网络团队 | 标准统一、能力强 | 成为瓶颈、离业务远 |
| **平台式（Platform as Product）** | 平台团队做"产品"（模板、CI、SoT），网络团队自助使用 | 扩展性好、责任清晰 | 平台必须真的好用，否则被绕过 |
| **分散式** | 各团队自己搞 | 起步快 | 三年后 5 套工具、3 份数据（回到陷阱表第一条） |

</div>

> 💡 **The CCDE judgement**: below roughly 500 devices a centralized model is usually sufficient; **at thousands of devices, multiple sites and multiple teams you must move to the platform model**, otherwise the automation team becomes the change bottleneck — and bottlenecks push teams to "quietly use the CLI", bypassing all the governance you built.

<div class="zh" markdown="1">

> 💡 **CCDE 视角的判断**：规模在 500 台设备以下时"集中式"通常够用；**上千台、多站点、多团队时必须走"平台式"**，否则自动化团队会成为变更瓶颈 —— 而瓶颈会促使各团队"私下用 CLI"，把你辛苦建立的治理全部绕开。

</div>

---

## Real-World Case Studies · 实战案例

### 🔥 Case 1: ZTP Was Perfect in the Lab and Failed Completely From Site 3 Onward · 🔥 案例一：ZTP 在实验室完美，在第 3 个站点开始全线失败

**Scenario**: a retail chain with 200 stores used PnP plus a cloud controller for ZTP. Lab testing passed, the first two sites succeeded, and from the third site on every AP and switch sat at "waiting for bootstrap".

<div class="zh" markdown="1">

**场景**：连锁企业 200 个门店，用 PnP + 云控制器做 ZTP。实验室测试通过，前 2 个站点成功，第 3 个站点起 AP 与交换机全部停在"等待引导"。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. The failing sites were all **routed (Layer 3) segments** (each store has its own router/firewall), while the two successful sites were flat Layer 2
2. DHCP capture: **Option 43 was not configured**, and the PnP broadcast could not cross Layer 3 → the PnP server was never found
3. After adding Option 43 some devices still failed: **their serial numbers were not registered in the PnP database** (the procurement batch was late and the data had not been synced)
4. Three more devices rebooted repeatedly: **the bootstrap pointed NTP at a headquarters-internal address** unreachable from the stores → clock skew → HTTPS certificate validation failure

<div class="zh" markdown="1">

1. 失败站点都是**跨三层网段**（门店有独立的路由器/防火墙），而成功的两个站点是扁平二层
2. 抓 DHCP 包：**Option 43 未配置**，PnP 广播跨不过三层 → 找不到 PnP 服务器
3. 补上 Option 43 后，部分设备仍失败：**序列号未在 PnP 数据库登记**（采购批次晚了，数据没同步）
4. 还有 3 台设备反复重启：**引导配置里 NTP 指向总部内网地址**，门店无法访问 → 时间不同步 → HTTPS 证书校验失败

</div>

**Root cause**: ZTP depends on **four preconditions holding simultaneously** — network reachability (Option 43/DNS), device registration, time synchronization, and certificate trust. If any one is missing, the symptom is simply "stuck".

<div class="zh" markdown="1">

**根因**：ZTP 依赖**四个前提同时成立** —— 网络可达（Option 43/DNS）、设备已登记、时间同步、证书信任。任何一个缺失都表现为"卡住"。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Action | Explanation |
|------|------|
| **Standardized discovery** | Configure Option 43 (hex IP list) plus DNS fallback in every site's DHCP |
| **Serials up front** | Integrate procurement with the PnP database; register before the goods arrive |
| **Minimal bootstrap** | Only management IP, route, **reachable NTP**, controller address |
| **Failure alerting** | The PnP platform alerts on "not joined within 30 minutes" instead of waiting for a site call |
| **Field emergency kit** | A USB/console bootstrap script as the ZTP fallback |

<div class="zh" markdown="1">

| 动作 | 说明 |
|------|------|
| **标准化发现方式** | 所有站点 DHCP 统一配 Option 43（十六进制 IP 列表）+ DNS 兜底 |
| **序列号前置** | 采购流程与 PnP 数据库打通，到货前完成登记 |
| **引导配置最小化** | 只含管理 IP、路由、**可达的 NTP**、控制器地址 |
| **失败告警** | PnP 平台对"30 分钟未 join"的设备告警，而不是等现场报修 |
| **现场应急包** | 提供 USB/Console 引导脚本，作为 ZTP 失败兜底 |

</div>

**Lesson**: **a ZTP success rate is set by the worst site, not the best one**. The design must make uniform assumptions about discovery, device identity, time and certificates across all sites — and carry a fallback path.

<div class="zh" markdown="1">

**教训**：**ZTP 的成功率取决于"最差的那个站点"，而不是"最好的那个"**。设计时必须把"发现机制、设备身份、时间、证书"四件事对所有站点做统一假设，并准备兜底路径。

</div>

### 🔥 Case 2: A Non-Idempotent Ansible Script Doubled the ACL on the Second Run · 🔥 案例二：非幂等的 Ansible 脚本，第二次执行把 ACL 翻倍

**Scenario**: operations used Ansible to add a management ACL to 80 access switches. The first run succeeded. A week later, to add two rules, they re-ran the same playbook — and lost SSH to the entire estate.

<div class="zh" markdown="1">

**场景**：运维用 Ansible 给 80 台接入交换机加管理 ACL。第一次执行成功。一周后为了新增两条规则重跑同一个 playbook，结果全网 SSH 断连。

</div>

**Root cause**:

<div class="zh" markdown="1">

**根因**：

</div>

1. The playbook appended rules using `ios_config` `lines:` and **never used `parents` to replace the whole ACL**
2. On the re-run the entries were **appended again** (80 became 160), including a wrong `deny` out of order relative to the real rules
3. Worse: **the ACL was applied to vty**, so once the order changed the management subnet was matched by a later deny → the whole site lost its management path

<div class="zh" markdown="1">

1. playbook 用 `ios_config` 的 `lines:` 追加规则，**没有用 `parents` 覆盖整段 ACL**
2. 重跑后 ACL 里的条目**重复追加**（80 条变 160 条），其中包含一条错误的 `deny`，与实际规则顺序错乱
3. 更致命：**ACL 应用在 vty 上**，一旦顺序变化，管理网段被后面的 deny 命中 → 全站失去管理通道

</div>

**Fix**:

<div class="zh" markdown="1">

**修复**：

</div>

```yaml
# Wrong: appending with lines duplicates on re-run
- cisco.ios.ios_config:
    lines:
      - 10 permit 10.10.0.0 0.0.255.255
      - 20 deny any log

# Right: replace the block (delete then push) and validate
- cisco.ios.ios_config:
    parents: ["ip access-list extended MGMT-IN"]
    lines:
      - "no 10"
      - "no 20"
      - "10 permit 10.10.0.0 0.0.255.255"
      - "20 deny ip any any log"
    match: none
```

<div class="zh" markdown="1">

```yaml
# 错误做法：lines 追加，重跑会重复
- cisco.ios.ios_config:
    lines:
      - 10 permit 10.10.0.0 0.0.255.255
      - 20 deny any log

# 正确做法：整段覆盖（先删除再下发），并校验
- cisco.ios.ios_config:
    parents: ["ip access-list extended MGMT-IN"]
    lines:
      - "no 10"
      - "no 20"
      - "10 permit 10.10.0.0 0.0.255.255"
      - "20 deny ip any any log"
    match: none
```

</div>

**Four hard rules (write them into the automation coding standard)**:

<div class="zh" markdown="1">

**四条硬性规则（写进自动化编码规范）**：

</div>

1. **Configuration operations always replace the whole block; never append**
2. **vty/management-plane changes must carry `confirmed-commit` or a timed rollback**
3. **CI must include a "second run produces zero changes" test** (idempotency verification)
4. **Management-plane changes must go out of band or in small batches** (five devices at a time)

<div class="zh" markdown="1">

1. **配置类操作一律"整段覆盖"，不做"追加"**
2. **vty/管理面相关变更必须带 `confirmed-commit` 或定时回滚**
3. **CI 中必须有"二次执行零变更"测试**（幂等性验证）
4. **管理面变更必须走带外通道或分批次**（一次只改 5 台）

</div>

**Lesson**: **idempotency is not elegance; it is a safety floor**. On a network the second run of a non-idempotent script is often more dangerous than the first, because the first run already moved the baseline.

<div class="zh" markdown="1">

**教训**：**幂等性不是"优雅"，是安全底线**。在网络上，非幂等脚本的第二次执行往往比第一次更危险，因为第一次已经改变了基线。

</div>

### 🔥 Case 3: A Syntactically Perfect ACL Cut the Entire Data Centre Management Plane · 🔥 案例三：一条"语法完全正确"的 ACL，把整个数据中心管理面切断

**Scenario**: the automation pipeline pushed a new ACL to 40 core/aggregation devices (a compliance requirement to "restrict management access sources"). yamllint, ansible-lint and Jinja2 rendering all passed in CI. Three minutes after the push, SSH, SNMP and NetFlow collection from every device stopped.

<div class="zh" markdown="1">

**场景**：自动化流水线给 40 台核心/汇聚设备统一下发新 ACL（合规要求"限制管理访问源"）。CI 阶段 yamllint、ansible-lint、Jinja2 渲染全部通过。下发后 3 分钟，所有设备的 SSH、SNMP、NetFlow 采集全部中断。

</div>

**Root cause**:

<div class="zh" markdown="1">

**根因**：

</div>

1. The variable file had the management subnet as `10.20.0.0/16`, while the real one is `10.2.0.0/16` (**one digit too many**)
2. CI only did **syntax/format checks**, never an **intent check** ("does this ACL still let the automation server reach the device?")
3. There was no canary; all 40 devices were pushed at once
4. Fortunately the push used `configure replace` with a 5-minute timeout rollback → the devices restored the previous configuration automatically, and the outage lasted 4 minutes

<div class="zh" markdown="1">

1. 变量文件里管理网段写成了 `10.20.0.0/16`，而实际管理网段是 `10.2.0.0/16`（**少写一位**）
2. CI 只做了**语法/格式检查**，没有做**意图检查**（"这条 ACL 是否仍然允许自动化服务器访问设备"）
3. 没有灰度，40 台一次推完
4. 万幸：下发用的是 `configure replace` 带 5 分钟超时回滚 → 设备自动恢复了旧配置，中断 4 分钟

</div>

**Fixes (a textbook retrofit for network CI/CD)**:

<div class="zh" markdown="1">

**修复（这是网络 CI/CD 的教科书式改造）**：

</div>

| Added defence | Concrete practice |
|------------|---------|
| **Data validation** | JSON Schema asserts the subnet belongs to the `allowed_mgmt_prefixes` list |
| **Intent analysis (Batfish)** | Before merge, assert reachability from the automation server to device port 22; fail CI if unreachable |
| **Self-reference check** | Any ACL change must verify "the source IP can still manage the device afterwards" |
| **Canary** | 1 device → 1 rack → everything, with manual confirmation at each step |
| **Safety rope** | Every management-plane change is forced through `configure replace ... timeout 300` |

<div class="zh" markdown="1">

| 加的一道防线 | 具体做法 |
|------------|---------|
| **数据校验** | 用 JSON Schema 校验网段必须属于 `allowed_mgmt_prefixes` 列表 |
| **意图分析（Batfish）** | 提交前跑"自动化服务器 → 设备 22 端口"可达性断言，不通则 CI 失败 |
| **自指检查** | 任何 ACL 变更必须验证"变更后源 IP 仍可管理设备" |
| **灰度** | 1 台 → 1 个机柜 → 全量，每步人工确认 |
| **安全绳** | 所有管理面变更强制 `configure replace ... timeout 300` |

</div>

**Lesson**: **syntactically correct ≠ intent correct**. The most frequent network incident is not "the command was wrong" but "the variable took the wrong value". CI must therefore include at least one layer of **semantic/intent verification** (Batfish reachability, pyATS assertions); otherwise a 100% pass rate means nothing.

<div class="zh" markdown="1">

**教训**：**语法正确 ≠ 意图正确**。网络中最高频的事故不是"命令写错"，而是"变量取错值"。所以 CI 必须至少有一层**语义/意图验证**（Batfish 可达性、pyATS 断言），否则通过率 100% 也毫无意义。

</div>

### 🔥 Case 4: Automatic Drift Correction Overwrote an Emergency Fix and Caused a Second Outage · 🔥 案例四：自动漂移纠正，把故障中的应急修改覆盖，引发二次故障

**Scenario**: an enterprise deployed "automatic compliance convergence": every night at 02:00 the running configuration was compared with the intended configuration in Git, and any difference was re-pushed automatically.

<div class="zh" markdown="1">

**场景**：某企业上线"配置合规自动收敛"：每天凌晨把设备的运行配置与 Git 中的期望配置比对，不一致就自动重下发。

</div>

**What happened**:

<div class="zh" markdown="1">

**事件经过**：

</div>

1. During the day, operations added `ip route 0.0.0.0 0.0.0.0 <backup egress> 10` on the core to work around a failed link (a temporary emergency change)
2. The nightly job ran → **drift detected → baseline re-pushed → the emergency route was deleted**
3. The backup egress stopped working and the morning peak lost service for 40 minutes

<div class="zh" markdown="1">

1. 白天运维为绕过一条故障链路，在核心上手工加了 `ip route 0.0.0.0 0.0.0.0 <备用出口> 10`（临时应急）
2. 凌晨自动任务运行 → **发现漂移 → 自动重下发基线配置 → 应急路由被删除**
3. 备用出口失效，早高峰业务中断 40 分钟

</div>

**Root cause**: treating drift as identical to error. **Drift has two classes**:

<div class="zh" markdown="1">

**根因**：把"漂移"等同于"错误"。**漂移分两类**：

</div>

| Drift class | Source | Correct handling |
|---------|------|---------|
| **Unauthorized drift** | Mistake, leftover script, temporary experiment | Alert plus process-driven correction |
| **Authorized drift** | Incident workaround, change not yet committed | **Alert and feed back into Git (formalize)**; never overwrite automatically |

<div class="zh" markdown="1">

| 漂移类型 | 来源 | 正确处置 |
|---------|------|---------|
| **非授权漂移** | 误操作、脚本残留、临时试验 | 告警 + 按流程纠正 |
| **授权漂移** | 故障应急、变更未及时入库 | **告警 + 反哺到 Git（正式化）**，不自动覆盖 |

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

- Drift detection changed to **alert only, never correct**; correction runs after human confirmation
- An **emergency change registration process** was established: out-of-band changes made during an incident must become a PR within 24 hours
- Automatic convergence applies only to **allowlisted objects** (NTP, logging, password policy) — **routes and ACLs are never auto-corrected**

<div class="zh" markdown="1">

- 漂移检测改为**只告警不纠正**，人工确认后执行
- 建立**应急变更登记流程**：故障中通过带外通道做的修改，需在 24 h 内补 PR
- 自动收敛只对**白名单对象**生效（如 NTP、日志、密码策略），**路由/ACL 永不自动纠正**

</div>

**Lesson**: **the boundary of automation must be "predictable, idempotent, lossless" objects**. Applying auto-repair to routes and ACLs means letting a machine decide without business context — and those incidents usually happen at night and are discovered in the morning.

<div class="zh" markdown="1">

**教训**：**自动化的边界必须是"可预测的、幂等的、无损的"对象**。把"自动修复"应用到路由与 ACL 上，等于让机器在不了解业务上下文的情况下做决策 —— 这类事故往往在凌晨发生，早上才被发现。

</div>

### 🔥 Case 5: Skipping the Canary, Pushing 200 Sites at Once, and a One-Digit Variable Error Degraded the Whole Network · 🔥 案例五：跳过灰度，一次推 200 个站点，变量错一位导致全网次优

**Scenario**: a bulk SD-WAN policy update (AAR thresholds for 200 sites). CI passed and the pipeline went straight to `deploy-full`, because "we pushed it the same way last time and nothing happened".

<div class="zh" markdown="1">

**场景**：SD-WAN 策略批量更新（200 个站点的 AAR 阈值），流水线跑通 CI 后直接 `deploy-full`（因为"上次也是这样推的，没问题"）。

</div>

**Result**: the AAR latency threshold was mistyped as 20 ms instead of 200 ms at every site (field misalignment), and the whole network began **flapping between links**; voice degraded broadly for six hours.

<div class="zh" markdown="1">

**结果**：所有站点的 AAR 时延阈值从 200 ms 被误写成 20 ms（字段错位），全网开始**频繁切换链路**，语音大面积劣化，持续 6 小时。

</div>

**Root cause**:

<div class="zh" markdown="1">

**根因**：

</div>

1. **No canary**: one full push, no control group, so nobody could tell whether the change or the carrier caused it
2. **No unit or range validation on the variable**: `latency_ms: 20` passed the schema (the type was right) but was semantically absurd
3. **The verify stage only checked "did the policy push"**, not "are the business metrics normal"
4. **No fast rollback path**: rolling back meant re-running the pipeline, 40 minutes

<div class="zh" markdown="1">

1. **没有灰度**：一次全量，无对比组，无法判断"是变更导致还是运营商问题"
2. **变量无单位/范围校验**：`latency_ms: 20` 通过了 schema（数字类型正确），但语义离谱
3. **verify 阶段只检查"策略是否下发成功"**，不检查"业务指标是否正常"
4. **没有快速回滚通道**：回滚需要重新跑一次流水线，耗时 40 分钟

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Measure | Explanation |
|------|------|
| **Range constraints in the schema** | `latency_ms: {min: 50, max: 1000}` |
| **Mandatory canary** | The pipeline requires a `canary_passed` flag before `deploy-full` |
| **Business assertions** | The verify stage checks voice MOS, loss rate and flap-count thresholds |
| **One-click rollback** | Keep the previous variable tag; rollback = re-run with the old tag (5 minutes) |
| **Change windows** | Large policy changes only during business troughs |

<div class="zh" markdown="1">

| 措施 | 说明 |
|------|------|
| **schema 加范围约束** | `latency_ms: {min: 50, max: 1000}` |
| **强制灰度** | 流水线里 `deploy-full` 前必须存在 `canary_passed` 标记 |
| **业务断言** | verify 阶段校验语音 MOS、丢包率、切换次数的阈值 |
| **一键回滚** | 保留上一版变量的 tag，回滚 = 用旧 tag 重跑（5 分钟） |
| **变更窗口** | 大规模策略变更只在业务低峰执行 |

</div>

**Lesson**: **"it worked last time" is the most dangerous kind of experience**. The point of a canary is not catching obvious errors but **catching hidden errors before they cost you 1%**. Order-of-magnitude variable errors (ms/s, Mb/Gb, decimal/hex) are the number one cause of automation incidents and must be stopped by schema constraints.

<div class="zh" markdown="1">

**教训**：**"上次这样推没问题"是最危险的经验**。灰度的意义不是发现"明显的错误"，而是**在损失 1% 前发现隐藏的错误**。变量的数量级错误（ms/s、Mb/Gb、十进制/十六进制）是自动化事故的头号原因，必须靠 schema 约束拦住。

</div>

### 🔥 Case 6: Automation Without Telemetry — Problems Found a Week Later · 🔥 案例六：没有遥测的自动化，变更后一周才发现问题

**Scenario**: a data centre finished automating its leaf-spine underlay (IS-IS configuration pushed from templates). Change verification only checked "did neighbors come up, were routes learned" — all passed. A week later the business team reported that "batch jobs across PODs are 40% slower".

<div class="zh" markdown="1">

**场景**：数据中心完成 leaf-spine 的 underlay 自动化改造（IS-IS 配置由模板统一下发）。变更验证只做了"邻居是否建立、路由是否学到"，全部通过。上线一周后，业务团队反馈"跨 POD 的批量任务变慢了 40%"。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. Routing tables were correct, neighbors were up, no packet loss → every traditional metric looked fine
2. NetFlow showed: **all cross-POD traffic was crossing a single spine** (ECMP broken or extremely unbalanced)
3. A configuration diff showed `isis metric` in the template had been unified to `10`, whereas the previous design used different metrics per link bandwidth
4. Because all links had equal cost, ECMP should have spread traffic evenly — but **some links were 40G and some 100G**, so equal-cost paths pushed the same share onto the 40G links, causing local congestion
5. Congestion only appeared at peak; the 5-minute average utilization in `show interface` hid it (SNMP polling missed the instantaneous peaks)

<div class="zh" markdown="1">

1. 路由表正确、邻居正常、无丢包 → 传统指标全部正常
2. 抓 NetFlow：**跨 POD 流量全部走同一条 spine**（ECMP 失效或负载极不均）
3. 查配置 diff：模板里 `isis metric` 被统一改成 `10`，而原来按链路带宽设置了不同度量
4. 因为所有链路 cost 相同，理论上应 ECMP 均分 —— 但实际**部分链路是 40G、部分是 100G**，等价路径把流量平均分到 40G 链路上，造成局部拥塞
5. 拥塞只在流量高峰出现，`show interface` 的 5 分钟平均利用率看不出来（SNMP 轮询漏掉了瞬时峰值）

</div>

**Root cause**: **"configuration correct" and "performance correct" are two different things**. Templating flattened the per-link metric differences — the most typical side effect of automation: **wiping out the differences that were intentional**.

<div class="zh" markdown="1">

**根因**：**"配置正确"与"性能正确"是两件事**。模板化把"每链路差异化的度量"抹平了 —— 这是自动化最典型的副作用：**把有意的差异也统一掉了**。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Measure | Explanation |
|------|------|
| **Derived values in templates** | The metric is computed from link bandwidth (e.g. `100000 / bandwidth_mbps`) instead of a fixed constant |
| **Performance baseline before change** | Record ECMP path distribution and the P95 utilization per link |
| **Telemetry instead of polling** | gNMI sampling at 10 s to see instantaneous utilization and queue drops |
| **Assertions include performance** | "Traffic distribution across all ECMP paths deviates < 20%" |
| **NetFlow in routine verification** | After the change, verify that path distribution matches the design |

<div class="zh" markdown="1">

| 措施 | 说明 |
|------|------|
| **模板支持"派生值"** | metric 由链路带宽计算（如 `100000 / bandwidth_mbps`），而不是固定常量 |
| **变更前建立性能基线** | 记录 ECMP 路径分布、各链路利用率 P95 |
| **遥测替代轮询** | 用 gNMI 采样（10 s 粒度）看瞬时利用率与队列丢弃 |
| **验证断言包含性能项** | "所有 ECMP 路径上的流量分布偏差 < 20%" |
| **NetFlow 纳入常规验证** | 变更后检查路径分布是否与设计一致 |

</div>

**Lesson**: **automated verification cannot look only at the control plane; it must look at data-plane behaviour**. Green neighbors and green routing tables do not prove that forwarding paths and load distribution match the design. **Automation without telemetry and flow analysis is surgery with your eyes closed.**

<div class="zh" markdown="1">

**教训**：**自动化的验证不能只看"控制面正确"，必须看"数据面表现"**。控制面（邻居、路由表）绿了，不代表转发路径与负载分布符合设计。**没有遥测与流分析的自动化，等于闭眼做手术。**

</div>

### 🔥 Case 7: One Unreleased candidate Lock Halted Network Automation for Two Days · 🔥 案例七：一个没释放的 candidate 锁，让全网自动化停摆两天

**Scenario**: configuration changes on 500 devices all went through NETCONF (Python + `ncclient`). Starting one Wednesday, operations reported "some devices will not take configuration", with plenty of `lock-denied` errors in the automation logs. The team assumed a device software bug, rebooted three devices and saw them recover — but **new devices started failing every day**.

<div class="zh" markdown="1">

**场景**：500 台设备的配置变更全部走 NETCONF（Python + `ncclient`）。某个周三开始，运维陆续报"部分设备改不了配置"，自动化日志里大量报错 `lock-denied`。团队以为是"设备软件 bug"，重启了 3 台设备后恢复正常，但**每天都有新的设备开始失败**。

</div>

**Investigation**:

<div class="zh" markdown="1">

**排查过程**：

</div>

1. Inspecting NETCONF sessions on a failing device revealed **a candidate lock five days old**, held by the orchestration platform's IP
2. The orchestration logs showed a bulk job five days earlier where 20 devices hit an SSH timeout between `lock` and `commit` (a brief network glitch)
3. The code had **no `try/finally` between `lock` and `commit`**: once the exception was raised, `unlock` never ran → the lock stayed on the device forever
4. Rebooting the device to clear the session was "effective but unacceptable" — and rebooting a core switch outside a change window is a policy violation

<div class="zh" markdown="1">

1. 在失败设备上查 NETCONF 会话：**存在一个 5 天前的 candidate 锁**，持有者是编排平台的 IP
2. 编排平台日志：5 天前有一次批量任务，其中 20 台设备在 `lock` 之后、`commit` 之前遇到 SSH 超时（网络闪断）
3. 代码里 `lock` 与 `commit` 之间**没有 `try/finally`**：异常抛出后 `unlock` 从未执行 → 锁永久留在设备上
4. 重启设备清空会话是"有效但不该有"的解法 —— 而且重启一台核心交换机在变更窗口之外是违规操作

</div>

**Root cause**: **in a distributed system, the exception path is the main path**. The script's author tested only the success path, never "the connection dies halfway".

<div class="zh" markdown="1">

**根因**：**"分布式系统里，异常路径才是主路径"**。脚本作者只测了成功路径，未测"连一半断了"的路径。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Measure | Practice |
|------|------|
| **Code level** | Every `lock` wrapped in `with`/`try-finally`; on exception, `unlock` first (ignoring errors) then reconnect |
| **Timeouts and retries** | `lock` requests carry a short timeout; failures do not retry forever but enter a "needs a human" queue |
| **Monitoring** | Collect "locked sessions and hold duration" per device, **alert above 30 minutes** |
| **Self-healing rule** | A lock held by the orchestration platform for more than an hour → automatic `kill session` (allowlisted and recorded), not a device reboot |
| **Single write path** | Forbid multiple people or scripts writing configuration directly (AAA command authorization plus session tagging); otherwise lock conflicts cannot be attributed |
| **Rehearsal** | Periodically **pull a cable mid-job** in the lab to prove the exception path releases resources correctly |

<div class="zh" markdown="1">

| 措施 | 做法 |
|------|------|
| **代码层** | 所有 `lock` 用 `with`/`try-finally` 保证释放；异常时先 `unlock`（忽略错误）再重连 |
| **超时与重试** | `lock` 请求带短超时；失败不无限重试，进"待人工"队列 |
| **监控** | 采集每台设备的"锁持有会话数与持有时长"，**超过 30 分钟告警** |
| **自愈规则** | 持锁会话来自编排平台且超过 1 小时 → 自动 `kill session`（有白名单与留痕），而不是重启设备 |
| **单一写入口** | 禁止多人/多脚本直连设备写配置（AAA 命令授权 + 会话标记），否则锁冲突无法定位 |
| **演练** | 定期在实验室**故意拔线中断**一次批量任务，验证异常路径能正确释放资源 |

</div>

**Lesson**: **the reliability of an automation platform is set by the quality of its failure-path handling**. The success path passes on the first try; failure paths need deliberate design and deliberate testing. These defects are delayed-action: a lock planted today goes off a week later.

<div class="zh" markdown="1">

**教训**：**自动化平台的可靠性取决于"失败路径的处理质量"**。成功路径只跑一次就通过，失败路径需要专门设计、专门测试。这类缺陷的特征是"有延迟"：今天埋下的锁，一周后才爆发。

</div>

### 🔥 Case 8: VLAN IDs Reused Everywhere — One Layer 2 Extension Merged Two Sites Into One Broadcast Domain · 🔥 案例八：VLAN 编号到处复用，一次二层延伸把两个站点连成一个大广播域

**Scenario**: after a merger, 200 sites were consolidated into one SoT. Historically every site used `VLAN 100`, with different meanings (site A: office; site B: voice). The SoT rule was "**VLAN IDs unique within a site**", so everything validated. Six months later the project needed to "stretch Layer 2" for one service between two sites (EVPN/VXLAN L2 stretch), and both sites' VLAN 100 were mapped to the same EVPN instance.

<div class="zh" markdown="1">

**场景**：企业并购后整合，200 个站点统一纳入 SoT。各站点历史上都用了 `VLAN 100`，但含义不同（A 站点是办公、B 站点是语音）。SoT 的校验规则是"**站点内 VLAN 唯一**"，因此全部通过。半年后项目要把两个站点的某业务"二层打通"（用 EVPN/VXLAN 做 L2 stretch），实施时把 A、B 两站点的 VLAN 100 都映射到同一个 EVPN 实例。

</div>

**What happened**:

<div class="zh" markdown="1">

**事件经过**：

</div>

1. After the stretch, the two sites' VLAN 100 **became a single broadcast domain** (site A's voice endpoints appeared in site B's office subnet)
2. The STP domain grew from "one site" to "across the WAN": **convergence went from seconds to tens of seconds**, and WAN link flaps triggered full-site STP recalculation
3. Two weeks later an access loop at site B (a mispatch) flooded broadcasts across the stretch into site A, and both sites went down together
4. DHCP pools became chaotic: endpoints at site A received addresses from site B, with gateways that did not match their subnet

<div class="zh" markdown="1">

1. 二层打通后，两个站点的 VLAN 100 **合并成同一个广播域**（A 的语音终端出现在 B 的办公网段）
2. STP 域从"单站点"扩大成"跨 WAN"，**收敛时间从秒级变成十几秒**，且 WAN 链路抖动会触发全站点 STP 重算
3. 两周后 B 站点一个接入环路（误接线）通过二层延伸把广播泛洪灌到 A 站点，两个站点同时瘫
4. DHCP 池混乱：A 站点的终端拿到了 B 站点的地址，网关与网段不匹配

</div>

**Root cause**: **a VLAN is a locally significant identifier** that automation and orchestration layers easily treat as a globally unique ID. The SoT validation was missing the "cross-site semantic consistency" layer.

<div class="zh" markdown="1">

**根因**：**VLAN 是"本地有效"的标识符**，但在自动化/编排层很容易被当成"全局唯一 ID"来用。SoT 的校验缺了"跨站点语义一致性"这一层。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Measure | Practice |
|------|------|
| **VLAN namespace rule** | Allocate VLAN IDs per site block (site 1: 100–199; site 2: 200–299…); **forbid the same ID meaning different things across sites** |
| **Mandatory semantic field** | Every VLAN in the SoT must carry `role` (user-voice/guest/iot…); cross-site mapping is by role, not by ID |
| **Layer 2 extension ban** | **No L2 stretch by default**; when it is unavoidable, use dedicated VLANs (a reserved stretch block) with an explicit STP boundary and storm control |
| **Cross-site validation** | Two new assertions: subnets of the same role must not overlap across sites; stretched VLANs must be registered explicitly |
| **Broadcast domain register** | Maintain a cross-site broadcast domain register (who, why, how big, approver); unregistered L2 stretches may not go live |

<div class="zh" markdown="1">

| 措施 | 做法 |
|------|------|
| **VLAN 命名空间规则** | VLAN ID 按站点号段分配（站点 1：100–199；站点 2：200–299…），**禁止跨站点同号不同义** |
| **语义字段必填** | SoT 中 VLAN 必须带 `role`（user-voice/guest/iot…），跨站点映射按 role 而不是按 ID |
| **二层延伸禁令** | 默认**不做 L2 stretch**；必须做时走独立 VLAN（专用延伸号段）+ 明确 STP 边界 + 风暴抑制 |
| **跨站点校验** | 增加"同一 role 在不同站点的网段不得重叠"与"延伸 VLAN 必须显式登记"两条断言 |
| **广播域清单** | 维护"跨站点广播域登记表"（谁、为什么、多大、审批人），无登记的二层延伸不允许上线 |

</div>

**Lesson**: **automation faithfully executes the facts you defined — including the wrong ones**. VLAN conflicts used to be avoided by "the senior engineer remembers"; in the automated era they must be avoided by **data rules plus validation**. **Prefer Layer 3 interconnection and be cautious with Layer 2 extension** — that old rule matters more, not less, with automation.

<div class="zh" markdown="1">

**教训**：**自动化会忠实地执行你定义的"事实"，包括错误的那个**。VLAN 冲突在手工时代靠"老师傅记得"避免，在自动化时代必须靠**数据规则 + 校验**避免。**优先三层互联、谨慎二层延伸**，这条老规则在自动化时代更重要。

</div>

### 🔥 Case 9: `terraform destroy` Ran in the Wrong Workspace and Deleted the Production VPN Topology · 🔥 案例九：`terraform destroy` 在错误的 workspace 里执行，删掉了生产 VPN 拓扑

**Scenario**: SD-WAN site topologies were managed by Terraform (one resource set per site). An engineer validated a refactor in the **test environment** and habitually ran `terraform apply`, but **the current workspace pointed at production** (it had not been switched back, and `TF_WORKSPACE` in the CI variables was overridden by a local `.env`). The plan showed "3 resources will be replaced", which the engineer read as the intended refactor, and typed `yes`.

<div class="zh" markdown="1">

**场景**：SD-WAN 的站点拓扑由 Terraform 管理（每个站点一套资源）。工程在**测试环境**验证一套重构，习惯性执行 `terraform apply`，但**当前 workspace 指向生产**（`terraform workspace` 上次切换后没切回，且 CI 变量里 `TF_WORKSPACE` 被本地 `.env` 覆盖）。plan 显示"3 个资源将被替换（replace）"，工程师认为"就是预期的重构"，输入 `yes`。

</div>

**Result**: the primary and backup tunnels of three sites were **destroyed and rebuilt** (Terraform's replace semantics are destroy + create). Creation then failed because of a template parameter error, leaving a 25-minute tunnel gap; voice and POS at two sites were fully down.

<div class="zh" markdown="1">

**结果**：3 个站点的主备隧道被**先删后建**（Terraform 的 replace 语义就是 destroy + create）。创建过程中因模板参数错误失败，隧道空窗 25 分钟，两个站点的语音与 POS 全部中断。

</div>

**Root cause (three overlapping failures)**:

<div class="zh" markdown="1">

**根因（三个叠加）**：

</div>

1. **Environment isolation depended on human memory** (one directory plus manual workspace switching) instead of directory/account hard isolation
2. **"Replace" was treated as harmless**: `-/+` on network resources means **break before build** (not a rolling update)
3. **Nobody read the destructive actions in the plan** — the review only looked at what was being added

<div class="zh" markdown="1">

1. **环境隔离靠人记**（同一目录 + 手工切 workspace），而不是靠目录/账号硬隔离
2. **"replace" 被当成无害操作**：`-/+` 在网络资源上等于**先断后建**（不是滚动更新）
3. **没有人看 plan 的"破坏性动作"** —— 评审时只看了"新增了什么"

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Measure | Practice |
|------|------|
| **Hard isolation** | Separate directories, credentials and CI projects for production and test; production workspaces require an explicit `-chk-prod` token |
| **Destructive plan check** | CI parses the plan JSON and **blocks on `delete`/`replace`**, requiring two-person approval; pure additions pass automatically |
| **Lifecycle protection** | Critical resources carry `lifecycle { prevent_destroy = true }` |
| **No destroy** | Production credentials **do not hold delete permission** (forbidden at the API role level); deletion requires a human process |
| **Two-phase change** | Network resource changes become "build new, shift traffic, delete old" (split into two resource groups in the template) to avoid replace |
| **State vs manual-change reconciliation** | Periodic read-only `terraform plan` to check state against real resources; manual changes must be fed back into code |

<div class="zh" markdown="1">

| 措施 | 做法 |
|------|------|
| **硬隔离** | 生产/测试**不同目录 + 不同凭据 + 不同 CI 项目**；生产 workspace 需要显式 `-chk-prod` 令牌才能操作 |
| **plan 破坏性检查** | CI 解析 plan JSON，出现 `delete`/`replace` 就**阻断并要求双人批准**；纯新增可自动通过 |
| **生命周期保护** | 关键资源加 `lifecycle { prevent_destroy = true }` |
| **禁 destroy** | 生产凭据**不具备删除权限**（API 角色层面禁止），删除必须走人工流程 |
| **两阶段变更** | 网络资源变更改为"先建新、再切流、最后删旧"（模板里拆成两组资源），避免 replace |
| **state 与手工变更对账** | 定期 `terraform plan`（只读）并检查"state 与真实资源的差异"，手工改动必须回填代码 |

</div>

**Lesson**: **"infrastructure as code" assumes code and state are strictly consistent**. Once someone has changed a real resource by hand, state becomes a lie; the next apply will "correct" reality to match the code — including deleting things you believed existed. **A plan must genuinely be read, especially the `-/+` and `-` symbols.**

<div class="zh" markdown="1">

**教训**：**"基础设施即代码"的前提是"代码与状态严格一致"**。当有人手工改过真实资源，state 就变成了谎言；此时一次 apply 会"纠正"成代码描述的样子 —— 包括删掉你以为存在的东西。**plan 必须被人真正读懂，尤其是 `-/+` 和 `-` 这两种符号。**

</div>

### 🔥 Case 10: Telemetry Sampling Went from 300 s to 1 s and Pinned Core Management-Plane CPU, Causing BGP Flapping · 🔥 案例十：遥测采样从 300 秒改到 1 秒，核心设备管理面 CPU 打满引发 BGP 抖动

**Scenario**: the team upgraded monitoring from SNMP (5-minute polling) to gNMI telemetry to "see transient congestion". For "data completeness" they subscribed to **every path** for CPU, memory, interface counters, queue drops and buffers at a **1-second** SAMPLE interval: 300 devices, roughly 800 paths per device.

<div class="zh" markdown="1">

**场景**：团队把监控从 SNMP（5 分钟轮询）升级为 gNMI 遥测，目标是"看到瞬时拥塞"。为了"数据完整"，把 CPU/内存/接口计数器/队列丢弃/缓冲区的**全部路径**以 **1 秒**间隔 SAMPLE 订阅。全网 300 台设备，单设备约 800 个路径。

</div>

**The arithmetic alone predicted the outcome**:

<div class="zh" markdown="1">

**计算一下就知道要出事**：

</div>

```
300 devices x 800 paths / 1 s = 240,000 samples/s
One sample (path encoding included, compressed) ≈ 250 B -> 60 MB/s ≈ 480 Mbps sustained telemetry traffic
```

<div class="zh" markdown="1">

```
300 台 × 800 路径 ÷ 1 s = 240,000 samples/s
单样本（含路径编码、压缩后）≈ 250 B → 60 MB/s ≈ 480 Mbps 持续遥测流量
```

</div>

**What happened**:

<div class="zh" markdown="1">

**事件经过**：

</div>

1. Within the first week: core management-plane CPU rose from 35% to 85%–95% (telemetry encoding and serialization are CPU-intensive)
2. BGP neighbors began periodic `hold timer expired` (management-plane CPU contention delayed keepalive processing)
3. The collector side collapsed too: 12 nodes, Kafka consumer lag growing to hours, heavy sample loss (but **nobody monitored the loss rate**; the dashboards said "data normal")

<div class="zh" markdown="1">

1. 上线当周：核心设备管理面 CPU 从 35% 升到 85%–95%（遥测编码 + 序列化是 CPU 密集的）
2. BGP 邻居开始周期性 `hold timer expired`（管理面 CPU 抢占导致 keepalive 处理延迟）
3. 采集器侧同样崩溃：12 个节点，Kafka 消费滞后增长到小时级，大量丢样（但**没人监控丢样率**，看板上"数据正常"）

</div>

**Root cause**: treating telemetry as "free, finer-grained monitoring" without capacity planning or source trimming — and **not monitoring the telemetry pipeline itself**.

<div class="zh" markdown="1">

**根因**：把遥测当成"免费的更细粒度监控"，没有做容量规划与源头裁剪；且**没有监控遥测管道自身**。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Measure | Practice |
|------|------|
| **Source trimming** | Subscribe only to metrics with a consumer (alert/assertion/SLO): paths 800 → 120 |
| **Tiered sampling** | Counters at 30 s (SAMPLE); state moved to ON_CHANGE; queue drops at 10 s (core only) |
| **Capacity first** | Produce a capacity table from `devices x paths / interval` before go-live, and load-test at 1/10 scale |
| **Device-side protection** | Configure telemetry CPU policing/priority so the protocol stack wins |
| **Pipeline self-monitoring** | Monitor subscription establishment rate, sample loss, end-to-end latency, collector CPU/backlog — all alerting |
| **Degradation plan** | Fall back to coarse SNMP collection when telemetry is unavailable (never fully blind) |

<div class="zh" markdown="1">

| 措施 | 做法 |
|------|------|
| **源头裁剪** | 只订阅有消费方的指标（告警/断言/SLO），路径数 800 → 120 |
| **分级采样** | 计数器 30 s（SAMPLE）；状态类改 ON_CHANGE；队列丢弃 10 s（仅核心） |
| **算容量再做** | 上线前按 `设备 × 路径 ÷ 间隔` 出容量表，并做 1/10 规模压测 |
| **设备侧保护** | 配置遥测 CPU 限流/优先级，确保协议栈优先 |
| **管道自监控** | 监控"订阅建立率、丢样率、端到端延迟、采集器 CPU/积压"，全部纳入告警 |
| **降级方案** | 遥测不可用时自动回落到 SNMP 粗粒度采集（保证"不完全失明"） |

</div>

**Lesson**: **the telemetry bottleneck is almost always device management-plane CPU and the collector, not network bandwidth**. The formula must be written down and computed during design. **Also: a telemetry system with no sample-loss monitoring is effectively random sampling — less trustworthy than polling** (polling at least tells you what is missing).

<div class="zh" markdown="1">

**教训**：**遥测的瓶颈几乎总在"设备管理面 CPU"和"采集器"，而不是网络带宽**。设计时必须写出公式并算一遍。**另外：一个没有"丢样率"监控的遥测系统，本质上是"随机抽样"，比轮询更不可信**（轮询至少你知道缺了什么）。

</div>

### 🔥 Case 11: One Debug Line in the CI Log Leaked Credentials for the Whole Network · 🔥 案例十一：CI 日志里的一行 debug 输出，泄露了全网设备凭据

**Scenario**: the pipeline added "retry on failure plus verbose logging" for troubleshooting. Some tasks in a playbook had `- debug: var=hostvars` and `no_log: false`, so CI logs printed `ansible_password`, `snmp_community` and `tacacs_key`. The log platform was readable by **all engineering staff** ("logs help people self-serve troubleshooting").

<div class="zh" markdown="1">

**场景**：自动化流水线加了"失败重试 + 详细日志"以便排障。某个 playbook 里有 `- debug: var=hostvars` 与 `no_log: false` 的部分任务，CI 日志把 `ansible_password`、`snmp_community`、`tacacs_key` 打了出来。日志平台对**全体研发只读**开放（因为"日志有助于自助排障"）。

</div>

**What happened**:

<div class="zh" markdown="1">

**事件经过**：

</div>

1. The exposure lasted four months before a security audit found it (an external penetration test report mentioned "an intranet wiki link pointing to a log platform where administrative credentials are visible")
2. Throughout, those credentials were a **shared administrator account** (the same set for every device), so nobody could determine whether they had been used
3. Remediation required changing passwords, SNMP communities and TACACS keys on 500 devices — roughly three person-weeks, plus change windows

<div class="zh" markdown="1">

1. 泄露持续了 4 个月才被安全审计发现（外部渗透测试报告中提到"某内网 Wiki 链接指向的日志平台可见管理凭据"）
2. 期间这些凭据是**共享的管理员账号**（所有设备同一套），无法判断是否被使用过
3. 事后必须对 500 台设备改密码 + 改 SNMP community + 改 TACACS key，工作量约 3 人周，且要排变更窗口

</div>

**Root cause**: **the credential lifecycle was entirely outside governance** (static, shared, never expiring, visible in clear text), while automation copied it into more places (CI logs, artifacts, caches).

<div class="zh" markdown="1">

**根因**：**凭据的生命周期完全脱离治理**（静态、共享、永不过期、明文可见），而自动化又把它复制到了更多地方（CI 日志、制品、缓存）。

</div>

**Fixes**:

<div class="zh" markdown="1">

**修复**：

</div>

| Layer | Measure |
|----|------|
| **Prevent leakage** | Pre-commit secret scanning (gitleaks/trufflehog) plus CI-stage scanning; `no_log: true` on every variable that holds a secret |
| **Reduce exposure** | **Runtime injection** of credentials (Vault/KMS): never in files, never printed from environment variables, never in artifacts |
| **De-sharing** | An independent service account per task class plus short-lived tokens (issued per task, valid one hour) |
| **Rotatable** | A "rotate credentials every 30 days" regime with **automated rotation** (rotation itself needs a pipeline, otherwise it never happens) |
| **Discoverable** | Log platforms redact by default (regex masking of password/community/key/secret fields); log access requires a request |
| **Attributable** | All administrative actions recorded through TACACS to a person or a task; shared admin accounts forbidden |

<div class="zh" markdown="1">

| 层 | 措施 |
|----|------|
| **防泄露** | pre-commit 密钥扫描（gitleaks/trufflehog）+ CI 阶段扫描；`no_log: true` 覆盖所有含密变量 |
| **少暴露** | 凭据**运行时注入**（Vault/KMS），不落在文件、不落在环境变量打印、不进制品 |
| **去共享** | 每类任务独立服务账号 + 短期令牌（按任务发放，1 小时有效） |
| **可轮换** | 建立"凭据轮换 30 天"机制并**自动化轮换**（轮换本身必须有流水线，否则永远不做） |
| **可发现** | 日志平台默认脱敏（正则屏蔽 password/community/key/secret 字段）；日志访问需要申请 |
| **可追溯** | 管理员操作全部经 TACACS 记录到人/到任务，禁止共享 admin 账号 |

</div>

**Lesson**: **automation multiplies the exposure surface of credentials** (scripts, CI, logs, caches, artifacts, AI context). **Credential management must land before automation does**, otherwise you are spreading risk faster. A shared account, a static password and clear-text logs together mean the network's control plane is hanging on the intranet.

<div class="zh" markdown="1">

**教训**：**自动化会成倍放大凭据的暴露面**（脚本、CI、日志、缓存、制品、AI 上下文）。**凭据管理必须先于自动化落地**，否则你是在用"更快的方式"扩散风险。共享账号 + 静态密码 + 明文日志，这三项同时存在时，等于把设备控制权挂在内部网上。

</div>

### 🔥 Case 12: An AI-Generated Template Missed One Variable and the ACL Silently Became "permit any" · 🔥 案例十二：AI 生成的模板少写一个变量，ACL 静默变成了"permit any"

**Scenario**: the team used a large model to help generate a Jinja2 ACL template for inbound filtering across 300 devices ("only business subnets may reach the server farm"). The template rendered correctly in the lab, `yamllint`/`ansible-lint` passed, and the diff looked like "just a few added entries". On day three after go-live, a security scan found that **the server farm was open to all sources**.

<div class="zh" markdown="1">

**场景**：团队用大模型辅助生成 Jinja2 ACL 模板，用来统一 300 台设备的入方向过滤（"只允许业务网段访问服务器区"）。模板在实验室渲染正常、`yamllint`/`ansible-lint` 全过、diff 看起来"只是新增了若干条目"。上线后第三天，安全团队做漏扫时发现**服务器区对所有源开放**。

</div>

**The root-cause chain**:

<div class="zh" markdown="1">

**根因链**：

</div>

1. The template read `permit ip {{ item.src }} {{ item.dst }}`, and the data for several sites **was missing the `src` field**
2. Jinja2 **renders undefined variables as empty strings by default** (`Undefined` raises nothing) → `permit ip  10.20.0.0 0.0.0.255` → the device interpreted the missing source as `any`
3. The configuration was **syntactically valid** (the device accepted it); to a human the diff looked like "a field is missing", but nobody checked line by line
4. CI had no **rendered-output assertion** (e.g. "every permit must have two address operands")
5. There was no Batfish reachability validation either (the intent "any source to the server farm must be denied" was never tested)

<div class="zh" markdown="1">

1. 模板里写的是 `permit ip {{ item.src }} {{ item.dst }}`，而数据里某几个站点**漏了 `src` 字段**
2. Jinja2 **默认把未定义变量渲染为空字符串**（`Undefined` 不报错）→ 生成 `permit ip  10.20.0.0 0.0.0.255` → 设备把缺失的源解释为 `any`
3. 配置**语法合法**（设备接受了），diff 人类看起来"少了个字段"，但没人逐条核
4. CI 没有"渲染结果断言"（例如"每条 permit 必须包含两个地址操作数"）
5. 也没有 Batfish 可达性验证（"从任意源到服务器区必须被拒绝"这条意图从未被测试）

</div>

**Fixes (the standard defence line for the "AI + automation" era)**:

<div class="zh" markdown="1">

**修复（这是"AI + 自动化"时代的标准防线）**：

</div>

| Defence | Concrete practice |
|------|---------|
| **Strict template mode** | Jinja2 `Environment(undefined=StrictUndefined)` — a missing variable fails the render |
| **Rendered-output assertions** | Regex/parser checks the **structural completeness** of the generated configuration (every rule must have source and destination) |
| **Required schema fields** | `src`/`dst` are `required` in the data schema; absence fails CI |
| **Intent validation** | Batfish: assert "any source → server farm ports 22/3389 denied" and "business subnets → permitted" |
| **Negative testing** | Deliberately inject sample data with the field missing and prove the pipeline goes red |
| **Semantic diff annotation** | Changes that **loosen** permissions (added permit, removed deny) are **highlighted separately** and require two-person review |
| **AI output passes the whole chain** | AI generation → review → lint → schema → render assertions → Batfish → canary; not one step may be skipped |

<div class="zh" markdown="1">

| 防线 | 具体做法 |
|------|---------|
| **模板严格模式** | Jinja2 `Environment(undefined=StrictUndefined)` —— 缺变量直接渲染失败 |
| **渲染结果断言** | 正则/解析器校验生成配置的**结构完整性**（每条规则必须有源和目的） |
| **schema 必填** | 数据结构中 `src`/`dst` 为 `required`，缺失即 CI 失败 |
| **意图验证** | Batfish：断言"任意源 → 服务器区 22/3389 被 deny"、"业务网段 → 允许" |
| **反向断言（负向测试）** | 故意注入"缺字段"的样本数据，验证流水线会红 |
| **diff 语义标注** | 对"放宽权限"的变更（新增 permit、删除 deny）**单独标红**并要求双人评审 |
| **AI 产出必过全链** | AI 生成 → 评审 → lint → schema → 渲染断言 → Batfish → 灰度，一步不能少 |

</div>

**Lesson**: **the most dangerous configuration is not the one that errors out; it is the legal but wrong one**. `permit ip any any` and `permit ip 10.20.0.0/24 any` are equally correct syntactically and worlds apart semantically. **A template engine's fault-tolerant defaults are the most insidious killer** and must all be changed to "fail when data is missing". AI only makes these errors faster to produce; it removes none of the defences.

<div class="zh" markdown="1">

**教训**：**最危险的不是"报错的配置"，是"合法的错误配置"**。`permit ip any any` 和 `permit ip 10.20.0.0/24 any` 在语法上同样正确，在安全语义上天差地别。**模板引擎的"容错默认值"是最隐蔽的杀手**，必须全部改成"缺数据就失败"。AI 只是让这类错误生成得更快，防线一条也没变。

</div>

---

## Design Trade-offs · 自动化设计的取舍

| Trade-off | Option A | Option B | How to decide |
|---------|------|------|---------|
| **Configuration method** | **CLI + screen scraping**: works with any device | **Model driven (NETCONF/YANG)**: precise and validated | Model-driven where supported; CLI only for legacy gear |
| **Tooling** | **Ansible**: quick to learn, agentless | **Nornir / in-house**: flexible and controllable | Strong Python team → Nornir; otherwise Ansible |
| **State management** | **Terraform**: state plus plan | **Stateless push**: simple | Resources to create/destroy → Terraform; pure configuration → Ansible |
| **Data source** | **IPAM/DCIM (NetBox)**: structured, queryable | **YAML in Git**: lightweight, PR friendly | Large scale → IPAM; small scale → Git is enough (with a schema) |
| **Verification depth** | **Static analysis (Batfish)**: fast and cheap | **Digital twin (CML)**: realistic and expensive | High-risk changes need both; routine changes need static analysis only |
| **Release model** | **Fully automatic (CD)**: fast | **Manual gate**: safe | Core network and management plane always keep a manual gate |
| **Drift governance** | **Automatic convergence**: saves effort | **Alert plus human confirmation**: safe | Auto-converge only stateless configuration |
| **Model choice** | **OpenConfig**: cross-vendor | **Native models**: full features | OpenConfig for the baseline, native models for proprietary features |
| **Monitoring** | **SNMP polling**: simple, existing tooling | **gNMI telemetry**: finer granularity, less overhead | Telemetry for all new devices; keep SNMP for legacy |
| **Automation scope** | **Day 0/1 first**: quick wins | **Day 2 first**: larger long-term benefit | Do ZTP first to earn trust, then Day 2 for the payoff |
| **Self-healing** | **Enabled**: shorter MTTR | **Disabled**: no wrong actions | Enable only with a clear failure mode, idempotent actions and a circuit breaker |
| **Derived values** | **Computed in code** (gateway = subnet + 1) | **Entered by hand**: flexible and intuitive | Code once the derivation rule is stable; hand-entered values must be validated |
| **Template granularity** | **One template per role**: clear | **One template per model**: close to the device | Express differences with data or conditionals, not by copying templates |
| **Idempotency approach** | **Whole-block replace**: clean and predictable | **Incremental append**: smaller impact | Replace by default; incremental only where a whole block cannot be replaced (e.g. huge ACLs) |
| **Automation account** | **Shared admin account**: convenient | **Service account plus short-lived token**: auditable | Any security requirement forces the latter; the cost is automated rotation |
| **Approval model** | **Case-by-case approval**: safe | **Templated batch approval** (by risk tier) | Bulk automation requires risk-tiered approval, or process becomes the bottleneck |
| **Platform choice** | **Vendor controller**: works out of the box | **In-house platform**: fits your process | One or two scenarios → vendor; multi-vendor/multi-domain long term → build the orchestration layer |
| **Onboarding scope** | **Onboard everything** (including legacy) | **Critical devices first** | Legacy devices go read-only plus compliance; write scope can be staged |
| **Verification rigour** | **Full-chain verification every time**: safe | **Risk-tiered verification** | Tiered: high risk (core/egress/auth) full chain; routine changes L1–L3 only |
| **Credential storage** | **CI variables plus encrypted files**: simple | **Vault/KMS dynamic credentials**: secure | More than 100 devices or multiple teams → go straight to Vault |

<div class="zh" markdown="1">

| 取舍维度 | 选 A | 选 B | 判断依据 |
|---------|------|------|---------|
| **配置方式** | **CLI + 屏幕抓取**：兼容一切设备 | **模型驱动（NETCONF/YANG）**：精准、可校验 | 设备支持就选模型；老设备只能 CLI |
| **工具** | **Ansible**：上手快、无代理 | **Nornir/自研**：灵活、可控 | 团队 Python 能力强选 Nornir；否则 Ansible |
| **状态管理** | **Terraform**：有 state、有 plan | **无状态推送**：简单 | 需要创建/销毁资源用 Terraform；纯配置用 Ansible |
| **数据源** | **IPAM/DCIM（NetBox）**：结构化、可查询 | **Git YAML**：轻量、PR 友好 | 规模大用 IPAM；小规模 Git 够用（但要 schema） |
| **验证深度** | **静态分析（Batfish）**：快、便宜 | **数字孪生（CML）**：真实、贵 | 高危变更两者都要；日常变更静态分析即可 |
| **发布方式** | **全自动（CD）**：快 | **人工 gate**：稳 | 核心网/管理面必须人工 gate |
| **漂移治理** | **自动收敛**：省人力 | **告警 + 人工确认**：安全 | 只对无状态配置自动收敛 |
| **模型选择** | **OpenConfig**：跨厂商 | **原生模型**：功能全 | 基线用 OpenConfig，专有特性用原生 |
| **监控** | **SNMP 轮询**：简单、存量工具支持 | **gNMI 遥测**：细粒度、低开销 | 新建设备一律遥测；老设备保留 SNMP |
| **自动化范围** | **Day 0/1 优先**：见效快 | **Day 2 优先**：长期收益大 | 先做 ZTP 拿信任，再做 Day 2 拿收益 |
| **自愈** | **开启**：MTTR 短 | **关闭**：避免误动作 | 仅在"故障模式明确 + 动作幂等 + 有熔断"时开启 |
| **派生值** | **代码计算**（网关=子网+1） | **人工填写**：灵活、直观 | 派生规则稳定就代码算；手工填的值必须能被校验 |
| **模板粒度** | **按角色一个模板**：清晰 | **按型号一个模板**：贴合设备 | 差异用数据/条件分支表达，不要用"复制模板"表达 |
| **幂等实现** | **整段覆盖**：干净、可预测 | **增量追加**：影响小 | 默认覆盖；增量仅用于"不能整段替换"的场景（如大型 ACL） |
| **自动化账号** | **共享管理员账号**：省事 | **服务账号 + 短期令牌**：可审计 | 有安全要求就必须后者，成本是"轮换要自动化" |
| **审批模型** | **逐条人工审批**：稳 | **模板化批量审批**（按风险等级） | 批量自动化必须配套"风险分级审批"，否则流程会成为瓶颈 |
| **平台建设** | **厂商控制器**：开箱可用 | **自研平台**：贴合流程 | 场景 1–2 个用厂商；多厂商/多域长期要自建编排层 |
| **纳管范围** | **全量纳管**（含老设备） | **关键设备优先** | 老设备走"只读 + 合规"，写入范围可以分批 |
| **验证严格度** | **每次全链路验证**：安全 | **按风险分级验证** | 分级：高危（核心/出口/认证）全链路，日常仅 L1–L3 |
| **凭据存储** | **CI 变量 + 加密文件**：简单 | **Vault/KMS 动态凭据**：安全 | 设备数 > 100 或有多团队时直接上 Vault |

</div>

---

## Design Pitfalls · 设计缺陷

| Pitfall | Typical symptom | Root cause | How to avoid it |
|------|---------|------|---------|
| **Treating scripts as automation** | Only the author can run it; no version control | No Git, no review, no docs | Scripts in Git + README + parameterization |
| **Automating configuration but not verification** | Push is fast but nobody knows whether it is right | Missing L3/L5 verification | Test pyramid reaches at least intent analysis plus canary |
| **Non-idempotent scripts** | Configuration doubles or scrambles on re-run | Append instead of replace | "Second run produces zero changes" as a CI gate |
| **Business data inside templates** | The template must change per site | Configuration and data not separated | Generic template, data externalized to the SoT |
| **No single source of truth** | An IP differs in three places; the wrong subnet is configured | Excel, NetBox and templates each keep a copy | One SoT plus schema validation |
| **Skipping the diff** | Critical configuration accidentally deleted | Rendered output pushed directly | Every change emits a diff for human confirmation |
| **One-shot full rollout** | A small error becomes a network-wide incident | No canary | Rings 0→3; Ring 1 picked for low risk |
| **No rollback plan** | Firefighting on site after the fact | Rollback steps undefined | Runbook plus `configure replace` timed rollback |
| **Management-plane change without a safety rope** | An ACL change cuts off your own access | No confirmed-commit | Timed rollback plus out-of-band path for management changes |
| **Automatically correcting drift** | Overwrites an emergency fix, second outage | Treating drift as identical to error | Alert only; auto-converge allowlisted objects only |
| **ZTP without identity validation** | Anyone who plugs in a cable can "claim" a configuration | DHCP plus clear-text TFTP only | Serial plus certificates (SZiP/802.1AR) |
| **ZTP covering only one network shape** | Every Layer 3 site fails | Option 43/DNS not standardized | Uniform discovery mechanism plus USB bootstrap fallback |
| **Templates flattening differences that should exist** | Performance drops while configuration is "all correct" | Fixed constants replacing derived values | Derive metrics from bandwidth/position |
| **No telemetry** | Problems found a week later | Polling and manual inspection only | gNMI telemetry + NetFlow + baselines |
| **CI tests syntax only** | 100% pass rate, business broken | No intent/reachability validation | Batfish and pyATS assertions |
| **Variables without range validation** | Threshold written as 20 ms instead of 200 ms | Schema validates types only | Add min/max/enum/units |
| **One repository for many environments** | Test configuration pushed to production | Environments not isolated | Branches/directories + environment variables + separate credentials |
| **Automation before process standardization** | Chaos amplified, unclear accountability | Code written before process defined | Define change tiers and approval first |
| **Ignoring the human veto** | Machines making wrong decisions autonomously | No manual gate | Keep human confirmation at critical points |
| **Fragmented toolchain** | Five tools, three copies of the data | No unified platform or standards | Converge on one or two tools plus one SoT |
| **Unreleased NETCONF locks** | Sudden network-wide lock-denied | No `finally` on the exception path | `try/finally` + lock-duration monitoring + automatic session cleanup |
| **Derived values entered by hand** | Changing one prefix means hundreds of edits | Treating the derived layer as the intent layer | Derive gateways/addresses/metrics in code; the SoT stores intent only |
| **VLAN/subnet reuse across sites** | Broadcast domains merge after L2 stretch, loops spread | Validation only checks uniqueness within a site | Numbering rules + cross-site semantic validation + L2 stretch registration |
| **Misused `terraform destroy`/replace** | Break before build; service gap | Environments not hard-isolated, nobody reads the plan | Directory and account isolation, `prevent_destroy`, no delete rights in production |
| **Telemetry sampled too densely** | Device management-plane CPU pinned, protocol flapping | Sample rate never computed | Capacity table before go-live + source trimming + tiered sampling |
| **No self-monitoring of the telemetry pipeline** | Sample loss while believing "everything is normal" | Monitoring the network but not the pipeline | Alert on subscription rate, loss rate, latency and backlog |
| **Credentials in Git or logs** | Permanent leak requiring a network-wide password change | Static shared credentials, logs not redacted | Runtime injection + secret scanning + regular rotation |
| **Shared admin accounts** | Cannot audit to a person | Convenience | Service accounts + short-lived tokens + TACACS to the individual |
| **Undefined template variables silently empty** | Generates "legal but loosened" configuration | Jinja2 `Undefined` raises nothing by default | `StrictUndefined` + rendered-structure assertions + negative testing |
| **Coverage stuck at 80%** | Dual-track operation, benefits cancelled | No long-tail strategy | One of: data-driven, conditional branches, exemption list |
| **Nobody owns the last mile** | The platform gets messier, templates rot | No platform product owner | Named platform owner + quarterly refactoring + failure post-mortems |
| **Switching environments by human memory** | Production used as test | Workspace/variables switched by hand | Three-way hard isolation: directories, accounts, CI projects |

<div class="zh" markdown="1">

| 缺陷 | 典型现象 | 根因 | 规避方法 |
|------|---------|------|---------|
| **把脚本当自动化** | 只有作者会跑、无版本控制 | 缺 Git、缺评审、缺文档 | 脚本进 Git + README + 参数化 |
| **只做配置自动化，不做验证** | 下发很快但没人知道对不对 | 缺少 L3/L5 验证层 | 测试金字塔至少做到意图分析 + 灰度 |
| **非幂等脚本** | 重跑后配置翻倍/错乱 | 用追加而非覆盖 | "二次执行零变更"作为 CI 门槛 |
| **模板里塞业务数据** | 换站点就要改模板 | 配置与数据未分离 | 模板通用，数据外置到 SoT |
| **SoT 不唯一** | IP 在三处不一样，配错网段 | Excel/NetBox/模板各存一份 | 单一事实来源 + schema 校验 |
| **跳过 diff** | 意外删除关键配置 | 直接下发渲染结果 | 每次变更输出 diff 并人工确认 |
| **一次性全量下发** | 小错误放大成全网事件 | 无灰度 | Ring 0→3 分批，Ring 1 选低风险站点 |
| **无回滚方案** | 出事后只能现场救火 | 回滚步骤未定义 | Runbook + `configure replace` 超时回滚 |
| **管理面变更无安全绳** | 改 ACL 切断自己 | 未用 confirmed-commit | 管理面变更强制定时回滚 + 带外通道 |
| **自动纠正漂移** | 覆盖应急配置引发二次故障 | 把漂移等同于错误 | 只告警；白名单对象才自动收敛 |
| **ZTP 未验证身份** | 任何人插线可"领走"配置 | 只靠 DHCP + TFTP 明文 | 序列号 + 证书（SZiP/802.1AR） |
| **ZTP 只覆盖一种网络形态** | 跨三层站点全失败 | Option 43/DNS 未统一 | 统一发现机制 + 兜底 USB 引导 |
| **模板抹平了应有的差异** | 性能下降但配置全"正确" | 固定常量替代了派生值 | 度量由带宽/位置派生 |
| **无遥测** | 变更后问题一周才发现 | 只靠轮询与人工巡检 | gNMI 遥测 + NetFlow + 基线 |
| **CI 只测语法** | 通过率 100% 但业务断了 | 无意图/可达性验证 | Batfish + pyATS 断言 |
| **变量无范围校验** | 阈值写成 20 ms 而非 200 ms | schema 只校验类型 | 加 min/max/枚举/单位 |
| **一个仓库管多环境** | 测试配置误推生产 | 环境未隔离 | 分支/目录 + 环境变量 + 独立凭据 |
| **自动化先于流程标准化** | 混乱被放大、责任不清 | 流程未定义就写代码 | 先定变更分级与审批，再自动化 |
| **忽略人类否决权** | 机器全自动做出错误决策 | 缺 manual gate | 关键节点保留人工确认 |
| **工具链碎片化** | 5 套工具、3 份数据 | 无统一平台与规范 | 收敛到 1–2 套工具 + 统一 SoT |
| **NETCONF 锁未释放** | 突然全网报 lock-denied | 异常路径没有 finally 释放 | `try/finally` + 锁持有时长监控 + 会话自动清理 |
| **派生值手工填写** | 改一个前缀要改几百处 | 把派生层当意图层 | 网关/地址/度量由代码派生，SoT 只存意图 |
| **VLAN/子网跨站点复用** | 二层延伸后广播域合并、环路扩散 | 校验只查"站点内唯一" | 号段规则 + 跨站点语义校验 + 二层延伸登记 |
| **`terraform destroy`/replace 误用** | 先删后建，业务空窗 | 环境未硬隔离、无人读 plan | 目录+账号隔离、`prevent_destroy`、生产禁删除权限 |
| **遥测采样过密** | 设备管理面 CPU 打满、协议抖动 | 没算样本速率 | 先算容量表再上线 + 源头裁剪 + 分级采样 |
| **遥测管道无自监控** | 丢样却以为"一切正常" | 只监控网络，不监控管道 | 订阅率/丢样率/延迟/积压纳入告警 |
| **凭据进 Git/日志** | 永久泄露，需全网改密码 | 静态共享凭据、日志不脱敏 | 运行时注入 + secret 扫描 + 定期轮换 |
| **共享 admin 账号** | 无法审计到人 | 图省事 | 服务账号 + 短期令牌 + TACACS 到人 |
| **模板未定义变量静默为空** | 生成"合法但放宽权限"的配置 | Jinja2 默认 Undefined 不报错 | `StrictUndefined` + 渲染结构断言 + 负向测试 |
| **覆盖率卡在 80%** | 双轨运行、收益被抵消 | 长尾无处理策略 | 数据驱动/条件分支/豁免清单三选一 |
| **自动化的"最后一公里"无人管** | 平台越用越乱、模板腐烂 | 没有平台产品负责人 | 明确平台 Owner + 季度重构 + 失败原因复盘 |
| **依赖人的记忆切换环境** | 生产当测试用 | workspace/变量靠人切 | 目录、账号、CI 项目三重硬隔离 |

</div>

---

## Design Scenario Practice (Three Automation Scenarios) · 设计情景演练（自动化类，三道）

> The trap in automation scenarios is **reaching for a tool immediately** (Ansible / Terraform / NSO). The right approach is to write the constraints first (team size, device capability, compliance, blast radius) and then treat the tool as an implementation detail.

<div class="zh" markdown="1">

> 自动化类情景题的陷阱是：**一到手就选工具**（Ansible / Terraform / NSO）。正确的做法是先写约束（团队规模、设备能力、合规要求、爆炸半径），再看工具是"实现细节"。

</div>

### Scenario 1: 1,200 devices, a 4-person team, 300 legacy devices, change volume doubling in two years · 情景一：1200 台设备、4 人团队、300 台老设备，两年内变更量翻倍

**Background**: a manufacturing company with 1,200 devices across 60 sites (including 300 legacy devices that only support SSH CLI). The network team has four people. Compliance requires "all changes auditable and reversible, and configuration compliance provable within six months". The number of sites will double in two years.

<div class="zh" markdown="1">

**背景**：制造企业，1200 台设备分布在 60 个站点（含 300 台只支持 SSH CLI 的老设备）。IT 网络团队 4 人。合规要求"所有变更可审计、可回滚、半年内可证明配置合规"。两年内站点数将翻倍。

</div>

**Question**: design the phased automation roadmap and target architecture, and explain why you would not go straight to "intent-driven" automation.

<div class="zh" markdown="1">

**问题**：设计自动化的分期路线与目标架构，并说明为什么不做"一步到位的意图驱动"。

</div>

<details markdown="1">
<summary>Reference analysis (write yours first)</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core idea: solve "auditable + verifiable" first, then "fast changes". The binding constraint on a four-person team is maintenance capacity, not technical ceiling.**

<div class="zh" markdown="1">

**核心思路：先解决"可审计 + 可验证"，再解决"变更快"。4 人团队的最大约束是"维护能力"，不是"技术上限"。**

</div>

| Phase | Timing | Deliverable | Key judgement |
|---|---|---|---|
| **1: Read-only** | Months 0–3 | Configuration collection/backup/compliance scans/version inventory; candidate SoT (with conflicts flagged) | Zero risk, immediate value (a latent-issue list) |
| **2: Data standardization** | Months 3–6 | Authoritative SoT (disambiguation complete) + schema validation + naming/numbering rules | **This is the make-or-break step**, not optional |
| **3: Limited writes** | Months 6–9 | New sites/devices through templates + pipeline (no touching the installed base) | New devices have the smallest blast radius: a natural pilot |
| **4: Onboarding the installed base** | Months 9–18 | Batch onboarding by site; legacy devices via CLI plus session templates (accepting fragility) plus strict diff | The legacy strategy is "write less, verify more", not "force them into a model" |
| **5: Governance hardening** | Months 18–24 | Freeze direct manual changes (AAA command authorization), DORA metrics live, platform owner named | Without governance, coverage regresses |

<div class="zh" markdown="1">

| 阶段 | 时间 | 交付物 | 关键判断 |
|---|---|---|---|
| **一：只读化** | 0–3 月 | 配置采集/备份/合规扫描/版本盘点；候选 SoT（带冲突标记） | 零风险、立刻产出价值（查出隐患清单） |
| **二：数据标准化** | 3–6 月 | 权威 SoT（消歧完成）+ schema 校验 + 命名/号段规则 | **这是全项目成败点**，不是可选步骤 |
| **三：少量写入** | 6–9 月 | 新站点/新设备走模板 + 流水线（不碰存量） | 新设备爆炸半径最小，天然试点 |
| **四：存量纳管** | 9–18 月 | 按站点分批纳管写入；老设备走 CLI + 会话模板（接受脆弱性）+ 强 diff | 老设备的策略是"少写多验"，不是"强行模型化" |
| **五：治理固化** | 18–24 月 | 冻结手工直改（AAA 命令授权）、DORA 四项指标上线、平台 Owner | 没有治理，覆盖率会回退 |

</div>

**Three judgements that must appear in the design**:

<div class="zh" markdown="1">

**三个必须写进方案的判断**：

</div>

1. **Do not do intent-driven (L5)**: 1,200 devices plus four people cannot sustain L5's explainability and maintenance cost. **Doing L2–L3 solidly is enough benefit.**
2. **Do not chase model-driven automation for legacy devices**: 300 devices going through CLI plus strict diff plus canary costs less than "adding a middleware layer for uniformity" (the middleware itself needs people to maintain it).
3. **Data work consumes 50%–60% of the effort**: the plan must explicitly schedule a "disambiguation" phase and staff for it, otherwise you stall in month six.

<div class="zh" markdown="1">

1. **不做意图驱动（L5）**：1200 台规模 + 4 人团队，L5 的可解释性与维护成本无法支撑。**把 L2–L3 做扎实，收益已足够。**
2. **老设备不追求模型驱动**：300 台设备走 CLI + 严格 diff + 灰度，比"为了统一而上中间层"更省成本（中间层本身也要人维护）。
3. **数据工作占 50%–60% 工时**：方案里必须显式安排"消歧"阶段与人力，否则会在第 6 个月卡死。

</div>

**The question you are most likely to be asked**: why not just buy a vendor's intent-driven controller? — Because **the data is not in the controller** (VLAN semantics, site numbering, business ownership live in people's heads and in Excel). **First you have an SoT, then the controller has an input.**

<div class="zh" markdown="1">

**最容易被追问的一点**：为什么不直接买厂商的意图驱动控制器？—— 因为**数据不在控制器里**（VLAN 语义、站点号段、业务归属都在人的脑子里和 Excel 里）。**先有 SoT，控制器才有输入。**

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 2: Automation raised change frequency 5×, but there are two automation-caused incidents every month · 情景二：自动化上线后变更频率 5 倍，但每月 2 起自动化引发的事件

**Background**: one year after automation went live, change frequency rose from 40 to 200 per month and lead time fell from 5 days to 4 hours. But there are on average two incidents per month caused directly or indirectly by automation (24 in the current assessment window). Management offers a choice: "either make it reliable, or roll back to semi-automatic".

<div class="zh" markdown="1">

**背景**：自动化上线一年，变更频率从每月 40 次升到 200 次，变更前置时间从 5 天降到 4 小时。但每月平均有 2 起由自动化直接或间接引发的事件（本次评估区间内已有 24 起）。管理层给出选择："要么把可靠性做上去，要么回退到半自动"。

</div>

**Question**: design a balance between reliability and throughput, and explain why rolling back is the wrong option.

<div class="zh" markdown="1">

**问题**：给出可靠性与吞吐的平衡设计，并说明"回退"为什么是错误选项。

</div>

<details markdown="1">
<summary>Reference analysis (write yours first)</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Do the arithmetic first**: 200 changes per month at a 1% failure rate (2/200) versus the manual era at 40 changes per month and a 15% failure rate (6 per month). **The absolute number of incidents actually fell after automation**; the "caused by automation" label just makes it feel worse. **The key metric is not "incident count" but "failure rate per change" and "MTTR".**

<div class="zh" markdown="1">

**先算账**：变更 200 次/月、失败率 1%（2/200），对比手工时代的 40 次/月、失败率 15%（6 次/月）。**自动化后的事件绝对数量其实下降了**，但"自动化导致"这个标签让人感知更强烈。**关键指标不是"事件数"，是"每次变更的失败率"与"MTTR"。**

</div>

| Improvement direction | Concrete action | Expected effect |
|---|---|---|
| **Stronger verification layer** | Add L3 (Batfish intent assertions) + L5 (canary); critical changes go through the twin | Blocks logic errors before merge |
| **Risk tiering** | Three tiers by blast radius: low (automatic) / medium (single approver) / high (two people + window + rollback plan) | The high-risk failure rate falls fastest |
| **Smaller batches** | Changes with dependency amplification ≥ 3 are fixed at 1–2 devices | Impact per change drops an order of magnitude |
| **Mandatory rollback points** | Every write-type change carries timed rollback; MTTR target < 15 min | Incidents "happen" but do not "affect the business" |
| **Failure post-mortems** | Monthly root-cause classification of automation failures (data/template/process/tool), eliminating one class per month | Systematic decline |
| **Assertion effectiveness audit** | Spot-check that assertions "go red when broken" (fault injection) | Removes the false safety of "always green" |

<div class="zh" markdown="1">

| 改善方向 | 具体动作 | 预期效果 |
|---|---|---|
| **提高验证层** | 补 L3（Batfish 意图断言）+ L5（灰度）；关键变更进孪生 | 把"逻辑错误"挡在合并前 |
| **风险分级** | 变更按爆炸半径分三档：低（自动）/中（单人批准）/高（双人+窗口+回滚预案） | 高风险的失败率下降最快 |
| **缩小批次** | 依赖放大系数 ≥3 的变更，批大小固定 1–2 台 | 单次影响面下降一个量级 |
| **强制回滚点** | 所有写入类变更带超时回滚；MTTR 目标 < 15 分钟 | 事件"发生"但不"影响业务" |
| **失败复盘机制** | 每月对自动化失败做根因分类（数据/模板/流程/工具），每月消一类 | 系统性下降 |
| **断言有效性审计** | 抽查断言是否"坏的时候会红"（注入故障验证） | 消除"永远绿"的假安全 |

</div>

**Why "roll back to semi-automatic" is the wrong option**:

<div class="zh" markdown="1">

**为什么"回退到半自动"是错误选项**：

</div>

- The manual era had a higher failure rate and longer MTTR; rolling back only converts **visible failures** into **hidden ones**
- Rolling back destroys the SoT and pipeline already built (the data rots; in six months you start over)
- The right target is "**drive the failure rate below 0.5% and MTTR within 15 minutes**", not "fewer changes"

<div class="zh" markdown="1">

- 手工时代的失败率更高、MTTR 更长，回退只是把**可见的失败**换成**隐蔽的失败**
- 回退会摧毁已建立的 SoT 与流水线（数据会腐烂，半年后要从头再来）
- 正确的目标是"**降低失败率到 < 0.5% 并把 MTTR 压到 15 分钟内**"，而不是"减少变更次数"

</div>

**One-sentence answer**: **localize the problem to "insufficient verification depth + batches too large + rollback too slow", not to "automation itself".** All three are design parameters that engineering can improve.

<div class="zh" markdown="1">

**一句话答案**：**把问题定位在"验证深度不足 + 批次过大 + 回滚不够快"，而不是"自动化本身"。** 这三个都是可以通过工程手段改善的设计参数。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

### Scenario 3: Three vendors + cloud networking + a quarterly acquisition, requiring one SoT and one change entry point · 情景三：3 家厂商 + 云网络 + 每季度并购，要求统一 SoT 与统一变更入口

**Background**: a multi-vendor environment (two switch vendors, one SD-WAN vendor, public cloud networking), where acquisitions add a new site cluster every quarter (each with its own historical naming and addressing habits). Goal: one SoT, one change entry point, one unified audit and compliance view.

<div class="zh" markdown="1">

**背景**：多厂商环境（2 家交换机、1 家 SD-WAN、公有云网络），并购导致每季度新增一个站点群（每个站点群有自己的历史命名与编址习惯）。目标：单一 SoT、单一变更入口、统一的审计与合规视图。

</div>

**Question**: design the data model and the tool boundaries, and explain how far "unification" should go and what must be allowed to stay heterogeneous.

<div class="zh" markdown="1">

**问题**：设计数据模型与工具边界，说明"统一"到什么程度、哪些必须允许异构。

</div>

<details markdown="1">
<summary>Reference analysis (write yours first)</summary>

<div class="zh" markdown="1">

<details markdown="1">
<summary>参考解析</summary>

</div>

**Core idea: unify "intent and process"; allow "implementation heterogeneity".**

<div class="zh" markdown="1">

**核心思路：统一"意图与流程"，允许"实现异构"。**

</div>

| Layer | Degree of unification | Explanation |
|---|---|---|
| **Intent data (SoT)** | **Fully unified** | Sites/devices/roles/VLAN semantics/subnets/policy intent under one schema |
| **Derivation rules** | **Fully unified** | Gateway = subnet + 1, metric derivation formulas, ACL generation rules |
| **Change process** | **Fully unified** | One entry point (Git + PR + CI), one audit record |
| **Verification assertions** | **Unified framework, layered implementation** | Assertion semantics unified ("voice gateway reachable"), implementation adapted per vendor |
| **Vendor implementation** | **Heterogeneity allowed** | Switches via NETCONF/OpenConfig, SD-WAN via controller API, cloud via Terraform |
| **Migration transition** | **Dual track allowed** | Acquired clusters first onboarded read-only plus compliance, then progressively given write access |

<div class="zh" markdown="1">

| 层 | 统一程度 | 说明 |
|---|---|---|
| **意图数据（SoT）** | **必须完全统一** | 站点/设备/角色/VLAN 语义/子网/策略意图，一套 schema |
| **派生规则** | **必须统一** | 网关=子网+1、度量派生公式、ACL 生成规则 |
| **变更流程** | **必须统一** | 一个入口（Git + PR + CI），一个审计记录 |
| **验证断言** | **统一框架、分层实现** | 断言语义统一（"语音网关可达"），实现按厂商适配 |
| **厂商实现** | **允许异构** | 交换机用 NETCONF/OpenConfig，SD-WAN 用控制器 API，云用 Terraform |
| **迁移过渡** | **允许双轨** | 并购站点群先在"只读 + 合规"模式下纳管，再逐步接入写入 |

</div>

**Four key design actions**:

<div class="zh" markdown="1">

**四个关键设计动作**：

</div>

1. **An adapter layer isolates vendor differences**: do not try to fit every vendor into one template; use an "intent → vendor template" adapter, with templates branching by role/model while **the intent layer stays untouched**.
2. **A data-cleansing pipeline for acquisitions**: every new cluster goes through collection → reverse engineering → disambiguation, and **its naming and addressing are mapped onto corporate rules** (rename/re-address plans must be designed explicitly, not "keep theirs").
3. **Multi-domain orchestration**: switches, SD-WAN and cloud networking each have a controller/provider; above them sits a "service orchestration" layer (one business change = cross-domain multi-step actions plus compensating rollback).
4. **Unified audit**: every change ends up in the same Git repository and the same ITSM record (including parent/child tickets for cross-domain orchestration).

<div class="zh" markdown="1">

1. **适配层（Adapter）隔离厂商差异**：不要试图用一个模板适配所有厂商；用"意图 → 厂商模板"的适配层，模板按角色/型号分支，**意图层不受影响**。
2. **并购的"数据清洗流水线"**：新站点群进来先做采集→反推→消歧，**命名与编址统一映射到企业规则**（重命名/重编址计划必须显式设计，而不是"沿用他们的"）。
3. **多域编排**：交换机、SD-WAN、云网络各自有控制器/Provider；在它们之上有一层"服务编排"（一次业务变更 = 跨域的多步动作 + 补偿回滚）。
4. **统一审计**：所有变更最终落到同一个 Git 仓库与同一个 ITSM 记录（含跨域编排的父子工单）。

</div>

**The question you are most likely to be asked**: why not standardize everything onto one vendor? — Because acquired equipment has depreciation cycles: **technical standardization takes 3–5 years, while acquisitions happen every quarter**. So the automation architecture must **assume heterogeneity is permanent** and absorb the differences in an adapter layer.

<div class="zh" markdown="1">

**最容易被追问的一点**：为什么不干脆"全部标准化成一套厂商"？—— 因为并购带来的存量设备有折旧周期，**技术标准化要 3–5 年，而并购每季度都在发生**。所以自动化架构必须**默认异构长期存在**，用适配层吸收差异。

</div>

</details>

<div class="zh" markdown="1">

</details>

</div>

---

## Scenario Framework: The Generic Recipe for Automation Questions · 情景分析框架：自动化类场景的通用套路

```
1. Write the constraints first:    device count, vendor/version capability, team size and skills,
                                   compliance, budget, change frequency
2. Write the invariants:           can it be rolled back, can it be audited, blast-radius ceiling,
                                   degraded mode when the platform fails
3. Answer in layers:               data -> template -> pipeline -> verification -> governance
                                   (the order cannot be reversed)
4. State the cost of every choice: this is the watershed between CCDE and CCIE
5. State the open issues:          legacy capability unconfirmed, SoT disambiguation pending,
                                   AAA authorization pending approval
6. Give acceptance and degradation: metrics (failure rate/lead time/coverage) plus break-glass
                                   behaviour when the platform fails
```

<div class="zh" markdown="1">

```
① 先写约束（Constraint）：      设备数、厂商/版本能力、团队人数与技能、合规、预算、变更频率
② 再写不变量（What must hold）： 能否回滚、能否审计、爆炸半径上限、平台故障时的降级形态
③ 分层作答：                    数据 → 模板 → 流水线 → 验证 → 治理（顺序不能颠倒）
④ 每个选择都写代价（Trade-off）： 这是 CCDE 与 CCIE 的分水岭
⑤ 写清未决项（Open issues）：     老设备能力未确认、SoT 消歧待完成、AAA 授权待批
⑥ 给出验收与降级：               指标（失败率/前置时间/覆盖率）+ 平台故障时的 break-glass
```

</div>

**One-sentence summary**: **an automation scenario question is not testing whether you can write a playbook; it is testing whether you can reduce the uncertainty of change step by step under the constraints of a limited team and limited device capability.**

<div class="zh" markdown="1">

**一句话总结**：**自动化情景题考的不是"你会不会写 playbook"，而是"你能不能在有限的团队与设备能力约束下，把变更的不确定性一步步降下来"。**

</div>

---

## Key Terms · 本章关键术语

| Term | Meaning |
|------|---------|
| ZTP | Zero-Touch Provisioning: deployment with no on-site configuration |
| IaC | Infrastructure as Code |
| CI/CD | Continuous Integration / Continuous Deployment |
| Ansible | Agentless automation tool |
| Terraform | Infrastructure orchestration tool with state |
| Playbook | Ansible's unit of task orchestration |
| Idempotency | Running repeatedly produces the same result |
| NETCONF | Network configuration protocol (RFC 6241, SSH 830) |
| RESTCONF | RESTful configuration protocol (RFC 8040) |
| gNMI | gRPC Network Management Interface |
| YANG | Data modeling language (RFC 7950) |
| OpenConfig | Vendor-neutral YANG model set |
| Version control | Git and the review workflow around it |
| Pipeline | The automated CI/CD execution chain |
| Day 0 / Day 1 / Day 2 | Arrival and install / bring-up and onboarding / routine change and operations |
| PnP | Plug and Play (Cisco ZTP) |
| SZiP / 802.1AR | Secure Zero-Touch provisioning identity / device identity certificate standard |
| Bootstrap | Minimal initial configuration pushed by ZTP |
| DHCP Option 43 | Vendor-specific option carrying controller addresses |
| Declarative / Imperative | Describing the end state versus describing the steps |
| Drift | Actual configuration diverging from intended configuration |
| SoT | Single Source of Truth |
| IPAM / DCIM | IP address management / data centre infrastructure management |
| Jinja2 | Configuration template engine |
| Playbook / Inventory / Role | Ansible orchestration / host list / reusable unit |
| Check Mode | Ansible dry-run mode |
| Screen scraping | Parsing human-readable CLI output |
| Nornir | Python network automation framework |
| Netmiko | Multi-vendor SSH CLI library |
| NAPALM | Multi-vendor unified network abstraction layer |
| pyATS / Genie | Cisco test and parsing framework |
| Batfish | Offline configuration analysis and reachability verification |
| Digital twin | A network replica in a simulation environment |
| CML / containerlab | Network emulation platforms |
| Canary / Ring | Staged rollout / rollout batch |
| Blast radius | Scope of impact of a failure |
| Rollback / Roll-forward | Reverting versus fixing forward |
| Manual gate | Human confirmation before an automated step |
| CI / CD | Continuous integration / continuous delivery (deployment) |
| GitOps | Operating with Git as the single source of truth |
| Pull request / code review | Merge request and peer review |
| Lint | Static checking of code and configuration |
| JSON Schema | Data validation schema |
| gRPC | High-performance RPC framework (HTTP/2 + Protobuf) |
| Datastore | Configuration store (running / candidate / startup) |
| candidate config | Candidate configuration, pre-validated and committed as a whole |
| confirmed-commit | Commit that auto-rolls back if not confirmed in time |
| rollback-on-error | Automatic revert when a commit fails |
| Capabilities | HELLO-based capability negotiation |
| MDT | Model-Driven Telemetry |
| Dial-out / Dial-in | Device pushes to collector / collector pulls from device |
| ON_CHANGE / SAMPLE | Change-triggered versus periodic subscription |
| Policy as Code | Compliance policy expressed as code |
| Runbook | Operating procedure including rollback steps |
| MTTR | Mean time to repair |
| Zero Trust (related) | Automation must be bound to identity and authorization |
| Intent / Derived / Device | The three-layer data structure of network data |
| Derived value | A value computed from rules (gateway IP = subnet + 1), never typed by hand |
| Reconciliation | Continuous comparison and handling of desired versus actual state |
| Normalization | Removing equivalent-form differences before comparing |
| Exemption list | Objects excluded from automation, with reason, owner and review date |
| Pre-flight check | Blocking validation before a change is pushed |
| DORA metrics | Lead time / change frequency / change failure rate / time to restore |
| Blast radius (dependency amplification) | Core/egress/authentication changes multiply by a dependency factor |
| candidate lock | NETCONF candidate datastore lock; an unreleased lock halts all writes |
| Capability matrix | Device capability matrix (model × version × supported models/features) |
| YANG deviation | Model deviation: some nodes unsupported on a given device |
| StrictUndefined | Jinja2 strict mode: undefined variables fail instead of rendering empty |
| Negative testing | Deliberately injecting bad data to prove the defence blocks it |
| Sample rate | Samples per second; the core parameter of telemetry capacity |
| Collector / pipeline | Telemetry collector and data pipeline; must self-monitor loss and backlog |
| Break-glass | Emergency manual path used when the platform fails; must be rehearsed |
| Secret manager / Vault | Runtime credential injection instead of files or logs |
| Secret scanning | Pre-commit/CI blocking of credentials entering the repository |
| Command authorization | TACACS+ restriction on the command set the automation account may run |
| Least privilege | The automation account must not be able to remove its own recovery path |
| `prevent_destroy` / plan | Terraform lifecycle protection / execution plan (read destructive actions) |
| Workspace | Terraform environment isolation unit (production/test must be hard-isolated) |
| Adapter layer | Absorbs vendor differences, isolating intent from implementation |
| CoE / platform as a product | The two organizational models for automation |
| Circuit breaker | Stops self-healing actions on recurrence or after a retry cap |
| Bounded action | Automated action that is idempotent, rate-limited and reversible |

<div class="zh" markdown="1">

| 术语 | 中文含义 |
|------|---------|
| ZTP | 零接触部署 |
| IaC | 基础设施即代码 |
| CI/CD | 持续集成/持续部署 |
| Ansible | 自动化工具 |
| Terraform | 基础设施编排工具 |
| Playbook | Ansible 自动化任务定义 |
| Idempotency | 幂等性 |
| NETCONF | 网络配置协议 |
| RESTCONF | RESTful 配置协议 |
| gNMI | gRPC 网络管理接口 |
| YANG | 数据建模语言 |
| OpenConfig | 开放配置模型 |
| Version Control | 版本控制 |
| Pipeline | 流水线 |
| Day 0 / Day 1 / Day 2 | 到货安装 / 上线纳管 / 日常变更与运维 |
| PnP | 即插即用（Cisco 零接触部署） |
| SZiP / 802.1AR | 安全唯一标识 / 设备身份证书标准 |
| Bootstrap | 引导配置（最小化初始配置） |
| DHCP Option 43 | 向设备下发控制器地址的私有选项 |
| Declarative / Imperative | 声明式 / 命令式 |
| Idempotency | 幂等性（重复执行结果一致） |
| Drift | 配置漂移 |
| SoT | 单一数据源 |
| IPAM / DCIM | IP 地址管理 / 数据中心基础设施管理 |
| Jinja2 | 配置模板引擎 |
| Playbook / Inventory / Role | Ansible 的编排 / 清单 / 复用单元 |
| Check Mode | Ansible 演练模式（不实际下发） |
| Screen Scraping | 屏幕抓取（解析 CLI 文本输出） |
| Nornir | Python 网络自动化框架 |
| Netmiko | 多厂商 SSH CLI 库 |
| NAPALM | 多厂商统一网络抽象层 |
| pyATS / Genie | Cisco 测试与解析框架 |
| Batfish | 离线配置静态分析与可达性验证 |
| Digital Twin | 数字孪生（仿真环境中的网络副本） |
| CML / containerlab | 网络仿真平台 |
| Canary / Ring | 灰度发布 / 灰度批次 |
| Blast Radius | 爆炸半径（故障影响范围） |
| Rollback / Roll-forward | 回滚 / 前滚 |
| Manual Gate | 人工确认门禁 |
| CI / CD | 持续集成 / 持续交付（部署） |
| GitOps | 以 Git 为唯一事实来源的运维范式 |
| Pull Request / Code Review | 合并请求 / 代码评审 |
| Lint | 静态代码/配置检查 |
| JSON Schema | 数据校验模式 |
| NETCONF | 网络配置协议（RFC 6241，SSH 830） |
| RESTCONF | RESTful 配置协议（RFC 8040） |
| gNMI | gRPC 网络管理接口 |
| gRPC | 高性能 RPC 框架（基于 HTTP/2 + Protobuf） |
| YANG | 数据建模语言（RFC 7950） |
| OpenConfig | 厂商无关的 YANG 模型集合 |
| Datastore | 数据存储（running / candidate / startup） |
| candidate config | 候选配置（可预校验、可整体提交） |
| confirmed-commit | 确认提交（超时未确认自动回滚） |
| rollback-on-error | 出错自动回滚能力 |
| Capabilities | 能力协商（HELLO 交换支持特性） |
| MDT | 模型驱动遥测 |
| Dial-out / Dial-in | 设备主动推送 / 采集器拉取 |
| ON_CHANGE / SAMPLE | 变化触发 / 周期采样订阅 |
| Policy as Code | 以代码表达的合规策略 |
| Runbook | 操作手册（含回滚步骤） |
| MTTR | 平均修复时间 |
| Zero Trust（关联） | 零信任（自动化需与身份/权限结合） |
| Intent / Derived / Device | 意图层 / 派生层 / 设备层（网络数据的三层结构） |
| Derived Value | 派生值（由规则计算而非人工填写的值，如网关 IP = 子网 +1） |
| Reconciliation | 对账（期望状态与实际状态的持续比较与处置） |
| Normalization | 归一化（消除等价写法差异后比对，否则漂移检测全是噪音） |
| Exemption List | 豁免清单（无法纳入自动化的对象，须写明原因/责任人/复审日期） |
| Pre-flight Check | 变更前置检查（下发前的阻断性校验） |
| DORA Metrics | 前置时间 / 变更频率 / 变更失败率 / 恢复时长 |
| Blast Radius（依赖放大） | 爆炸半径；核心/出口/认证类变更需乘依赖放大系数 |
| candidate Lock | NETCONF 候选配置锁（异常路径未释放会导致全网写入停摆） |
| Capability Matrix | 设备能力矩阵（型号 × 版本 × 支持的模型/特性） |
| YANG Deviation | 模型偏差（同一模型在特定设备上不支持某些节点） |
| StrictUndefined | Jinja2 严格模式（未定义变量直接失败，而非渲染为空） |
| Negative Testing | 负向测试（故意注入坏数据，证明防线会拦） |
| Sample Rate | 采样速率（遥测容量估算的核心参数） |
| Collector / Pipeline | 遥测采集器与数据管道（需自监控丢样率与积压） |
| Break-glass | 应急通道（平台失效时的手工操作路径，须演练） |
| Secret Manager / Vault | 密钥管理系统（运行时注入凭据，避免落盘/进日志） |
| Secret Scanning | 密钥扫描（pre-commit/CI 阻断凭据入库） |
| Command Authorization | 命令授权（TACACS+ 限制自动化账号可执行的命令集） |
| Least Privilege | 最小权限（自动化账号不能修改自身的恢复能力） |
| `prevent_destroy` / plan | Terraform 生命周期保护 / 执行计划（必须先读破坏性动作） |
| Workspace | Terraform 环境隔离单元（生产/测试必须硬隔离） |
| Adapter Layer | 适配层（吸收多厂商差异，隔离意图层与实现） |
| CoE / Platform as Product | 卓越中心 / 平台即产品（自动化的两种组织模式） |
| Circuit Breaker | 熔断器（自愈动作限次并在异常复发时停止） |
| Bounded Action | 有界动作（幂等 + 次数上限 + 可回退的自动化动作） |

</div>

---

## Practical Experience Summary · 实战经验总结

1. **The acceptance criterion for automation is "on site, only power and cabling".** As long as an engineer still has to travel and type commands, it is semi-automatic. The value of ZTP is compressing human action to the physical layer.
2. **Data matters an order of magnitude more than code.** Real projects are almost always blocked by "no trustworthy SoT": an IP inconsistent in three places, VLANs with no authoritative definition, device roles remembered by people. **Standardize the data first, then talk about automation.**
3. **Idempotency is a safety floor, not elegance.** A large share of network automation incidents are caused by "the second execution". Making "run twice, second run changes nothing" a hard CI gate eliminates a whole class of incidents.
4. **Syntax checks solve almost nothing; intent verification solves the problem.** Passing yamllint does not mean the network works. You need at least Batfish-level reachability/ACL analysis, and ideally the real-traffic validation of a canary.
5. **A canary is the only way to catch an error before it costs 1%.** A full rollout is not "efficient"; it is "skipping testing". Ring 1 must be a site with low business impact, on-site support and a representative topology.
6. **Rollback must be designed in advance, and it must account for "state that cannot be rolled back".** Configuration can be restored, but BGP sessions have already rebuilt, OSPF has reconverged and TCP connections have already dropped. So change incrementally where possible, and never push without a timed rollback.
7. **Automation amplifies process, not capability.** Chaotic process plus automation equals automated chaos. Standardize first (change tiers, approval, test requirements, rollback plan), then write code.
8. **Automation without telemetry is driving with your eyes closed.** Configuration automation only solves "can I change it"; telemetry plus assertions solve "did I change it correctly". The order is: observability → configuration automation → closed-loop self-healing.
9. **Read-only first is the only viable starting point for brownfield.** Collection → baseline → compliance report is zero risk, immediately valuable, and it is the shared prerequisite for drift detection, the SoT and the verification layer. **Skipping "read" and going straight to "write" is driving through a minefield without a map.**
10. **Derived values must be computed by code, never filled in by hand.** Gateway = subnet + 1, routing metric derived from bandwidth, ACL entries derived from policy. Once a derived value is written into the SoT, changing one prefix means hundreds of edits — and people always miss some.
11. **The enemy of coverage is the long tail, and there are only three ways to handle it: data-driven, conditional branches, exemption list.** When coverage is stuck at 80% the team runs two tracks and the benefit is essentially cancelled — and "those special devices" are exactly where incidents cluster.
12. **The orchestration platform is itself a production system.** The design must state "if the platform is down for four hours, does forwarding continue, how do we make changes", and the **break-glass manual path must be rehearsed**. "Controller HA" alone is not enough.
13. **Credential governance must land before automation.** Automation multiplies the exposure surface (scripts, CI logs, artifacts, caches, AI context). A shared account, a static password and clear-text logs together mean the network's control plane is hanging on the intranet.
14. **A template engine's fault-tolerant defaults are the most insidious killer.** Jinja2 renders undefined variables as empty, producing "syntactically legal but semantically loosened" configuration (the `permit ip any any` class of incident). **Strict mode + rendered-structure assertions + negative testing** must be standard equipment.
15. **In deterministic engineering there is no "it should be fine".** Assertions must be proven to "go red when broken" (fault injection), the telemetry pipeline must self-monitor (sample loss), and rollback must be rehearsed (not merely written in a runbook). **A capability you have never verified is a capability you do not have.**
16. **AI only made generation cheap; it did not make change safe.** Everything it produces still passes the same defence line: review → lint → schema → intent validation → canary → assertions. Using AI to skip review means manufacturing bigger incidents faster.

<div class="zh" markdown="1">

1. **自动化的验收标准是"现场只做上电和插线"。** 只要还需要工程师到现场敲命令，就还是"半自动"。ZTP 的价值在于把人的动作压缩到物理层面。
2. **数据比代码重要一个数量级。** 现实项目的瓶颈几乎总是"没有可信的 SoT"：IP 在三处不一致、VLAN 没有权威定义、设备角色靠人记。**先把数据标准化，再谈自动化。**
3. **幂等性是安全底线，不是优雅。** 网络自动化事故里，有相当比例是"第二次执行"造成的。把"连续执行两次，第二次零变更"作为 CI 硬门槛，能消掉一大类事故。
4. **语法检查几乎不解决问题，意图验证才解决问题。** yamllint 通过不代表网络能通。至少要有 Batfish 这一层的可达性/ACL 分析，最好再加灰度这一层真实流量验证。
5. **灰度是唯一能在"损失 1% 前"发现错误的手段。** 全量下发不是"效率高"，是"把测试省掉"。Ring 1 一定要选"业务影响小、有现场支持、拓扑有代表性"的站点。
6. **回滚要提前设计，而且要考虑"状态不可回滚"。** 配置可以恢复，但 BGP 会话重建、OSPF 重收敛、TCP 连接中断已经发生了。所以能增量就别整体替换，能给超时回滚就别裸奔。
7. **自动化放大的是流程，不是能力。** 流程混乱 + 自动化 = 混乱的自动化。先标准化（变更分级、审批、测试要求、回滚方案），再写代码。
8. **没有遥测的自动化是闭眼开车。** 配置自动化只解决"改得动"，遥测 + 断言才解决"改得对"。顺序是：可观测性 → 配置自动化 → 闭环自愈。
9. **只读先行，是存量网络唯一可行的起点。** 采集 → 基线 → 合规报告，风险为零、立刻产出价值，而且它是漂移检测、SoT、验证层的共同前提。**跳过"读"直接"写"，等于在没有地图的雷区里开车。**
10. **派生值必须由代码算，不能由人填。** 网关 = 子网 +1、路由度量 = 带宽派生、ACL 条目由策略派生。一旦把派生值写进 SoT，改一个前缀就要改几百处，而人一定会漏。
11. **覆盖率的敌人是长尾，处理长尾只有三条路：数据驱动、条件分支、豁免清单。** 覆盖率卡在 80% 时，团队是双轨运行，收益基本被抵消；而"特殊的那些设备"恰恰是出事最多的。
12. **编排平台本身是生产系统。** 方案里必须写明"平台宕机 4 小时，业务是否照常转发、变更怎么做"，并且**演练过 break-glass 手工路径**。只写"控制器 HA"是不够的。
13. **凭据治理必须先于自动化落地。** 自动化会成倍放大凭据暴露面（脚本、CI 日志、制品、缓存、AI 上下文）。共享账号 + 静态密码 + 明文日志三项共存，等于把设备控制权挂在内部网。
14. **模板引擎的"容错默认值"是最隐蔽的杀手。** Jinja2 未定义变量默认为空，会生成"语法合法但语义放宽"的配置（`permit ip any any` 级别的事故）。**严格模式 + 渲染结构断言 + 负向测试**三件套必须标配。
15. **确定性工程里没有"应该没事"。** 断言要能被证明"坏的时候会红"（注入故障验证），遥测管道要有自监控（丢样率），回滚要演练过（不只是写在 Runbook 里）。**没验证过的能力，等于不存在的能力。**
16. **AI 只让"生成"变便宜，没有让"变更"变安全。** 它产出的一切仍然要过同一条防线：评审 → lint → schema → 意图验证 → 灰度 → 断言。用 AI 跳过评审，就是用更快的速度制造更大的事故。

</div>

---

## Chapter Summary · 本章小结

In network design, automation is not a tool selection question but a set of **engineering constraints**: it replaces human-error-prone actions (copy-paste, hand-computed IPs, rollback from memory) with mechanisms that are **repeatable, verifiable and traceable**.

<div class="zh" markdown="1">

自动化在网络设计里不是"工具选型"，而是一套**工程约束**：把人类易错的动作（复制粘贴、手算 IP、凭记忆回滚）替换成**可重复、可验证、可追溯**的机制。

</div>

This chapter's four layers and four defence lines:

<div class="zh" markdown="1">

本章的四个层次与四道防线：

</div>

| Layer | Object automated | Key means | Test of success |
|------|-----------|---------|---------|
| **Deployment** | Day 0/1 | ZTP/PnP plus bootstrap configuration | On site, only power and cabling |
| **Configuration** | Day 2 | IaC (templates plus data), Git, CI | Second run produces zero changes |
| **Verification** | Before and after a change | Static analysis, emulation, canary, assertions | Intent is provable, not just syntactically valid |
| **Operations** | Day N | Telemetry, drift detection, closed loop | Drift is detectable before users notice problems |

<div class="zh" markdown="1">

| 层次 | 自动化对象 | 关键手段 | 成败判据 |
|------|-----------|---------|---------|
| **部署** | Day 0/1 | ZTP/PnP + 引导配置 | 现场只做上电插线 |
| **配置** | Day 2 | IaC（模板+数据）、Git、CI | 二次执行零变更 |
| **验证** | 变更前后 | 静态分析、仿真、灰度、断言 | 意图可证明，不只语法正确 |
| **运维** | Day N | 遥测、漂移检测、闭环 | 漂移可发现，问题早于用户发现 |

</div>

| Defence line | What it blocks | What happens without it |
|------|-------|-----------|
| **Data validation (schema)** | Wrong order of magnitude or unit in a variable | 200 ms typed as 20 ms → network-wide flapping |
| **Intent analysis (Batfish)** | Logic errors (ACL/reachability) | Management plane cut off; you lock yourself out |
| **Canary (rings)** | Hidden environmental differences | A small error amplified network-wide in one shot |
| **Telemetry and assertions (verify)** | Control plane healthy while data plane degrades | The business notices the performance drop a week later |

<div class="zh" markdown="1">

| 防线 | 拦什么 | 缺了会怎样 |
|------|-------|-----------|
| **数据校验（schema）** | 变量数量级/单位错误 | 200 ms 写成 20 ms，全网抖动 |
| **意图分析（Batfish）** | 逻辑错误（ACL/可达性） | 把管理面切断，自己被关在门外 |
| **灰度（Ring）** | 隐藏的环境差异 | 小错误一次性放大到全网 |
| **遥测与断言（verify）** | 控制面正常但数据面劣化 | 一周后业务才发现性能下降 |

</div>

From a CCDE perspective, automation design really has to answer four questions:

<div class="zh" markdown="1">

CCDE 视角下，自动化设计真正要回答的四个问题：

</div>

1. **Where is the single source of truth, who maintains it, and how is it validated?**
2. **How large is the blast radius of a change, and by what means is it reduced?**
3. **How is it rolled back on failure, how long does that take, and who decides?**
4. **How do you prove that "the network still matches the design intent after the change"?**

<div class="zh" markdown="1">

1. **单一数据源在哪里，谁维护，如何校验？**
2. **变更的爆炸半径多大，用什么手段把它切小？**
3. **失败时如何回滚，回滚需要多久，谁来决定？**
4. **如何证明"变更后网络仍然符合设计意图"？**

</div>

Plus two more that are often skipped but always asked:

<div class="zh" markdown="1">

再加两个常被跳过、但一定会被追问的问题：

</div>

5. **What happens when the platform itself fails?** (Does forwarding continue, how are changes made, has break-glass been rehearsed?)
6. **Where are the boundaries of authority and credentials?** (Can the service account remove its own recovery path, who can read logs, how often are credentials rotated?)

<div class="zh" markdown="1">

5. **平台自己挂了怎么办？**（转发是否照常、变更怎么做、break-glass 演练过没有）
6. **权限与凭据的边界在哪？**（服务账号能否改掉自己的恢复能力、谁能读日志、凭据多久轮换一次）

</div>

Answer those six questions and whether you use Ansible or Nornir, NETCONF or CLI, is only an implementation detail.

<div class="zh" markdown="1">

这六问答清楚，用 Ansible 还是 Nornir、用 NETCONF 还是 CLI，都只是实现细节。

</div>

**Finally, remember the whole chapter as a three-step progression**:

<div class="zh" markdown="1">

**最后用一个"三层递进"记住全章**：

</div>

| Progression | Question | Means | What failure looks like |
|------|------|------|-----------|
| **Can you see it** | What does the network actually look like now | Read-only collection + SoT + drift/compliance | Three years later: 500 devices, 500 versions, nobody knows the standard |
| **Can you change it** | Can changes be batched, repeated, rolled back | Templates + Git + CI/CD + canary | Changes 10× faster, incidents 10× faster |
| **Can you change it correctly** | How do you prove it matches intent afterwards | Assertions + telemetry + business metrics | Control plane all green while the business has been degraded for a week |

<div class="zh" markdown="1">

| 递进 | 问题 | 手段 | 失败的样子 |
|------|------|------|-----------|
| **看得见** | 网络现在到底是什么样 | 只读采集 + SoT + 漂移/合规 | 三年后 500 台设备 500 个版本，没人知道标准是什么 |
| **改得动** | 能否批量、可重复、可回滚地改 | 模板 + Git + CI/CD + 灰度 | 变更快 10 倍，事故也快 10 倍 |
| **改得对** | 改完如何证明符合意图 | 断言 + 遥测 + 业务指标 | 控制面全绿，业务已劣化一周 |

</div>

**The order cannot be reversed**: doing "can you change it" without "can you see it" is replicating errors at high speed on a wrong baseline; doing "can you change it correctly" without "can you change it" is impossible even to assert (there is no trustworthy desired state).

<div class="zh" markdown="1">

**顺序不能颠倒**：没有"看得见"就做"改得动"，是在错误的基线上高速复制错误；没有"改得动"就做"改得对"，则连断言都跑不起来（没有可信的期望状态）。

</div>

> 📌 **Next chapter (Chapter 13: Multicast Design)** returns to a field where "the configuration looks simple and the design is extremely complex": when the same traffic must reach hundreds or thousands of receivers, the shape of the tree, the placement of the RP and the choice of PIM mode force every earlier judgement about routing, convergence and scalability to be re-examined.

<div class="zh" markdown="1">

> 📌 **下一章（第 13 章 组播设计）**会回到一个"配置看起来简单、设计极其复杂"的领域：当同一份流量需要发给成百上千个接收者时，树的结构、RP 的位置、PIM 模式的选择，会把前面所有关于路由、收敛、扩展性的判断重新考一遍。

</div>
