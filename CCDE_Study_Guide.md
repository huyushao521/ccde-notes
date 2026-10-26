# CCDE 400-007 Official Cert Guide - 学习指南

## 📖 书籍基本信息

| 项目 | 内容 |
|------|------|
| **书名** | Cisco Certified Design Expert (CCDE 400-007) Official Cert Guide |
| **作者** | Zig Zsiga |
| **出版社** | Cisco Press |
| **版权年** | 2023 |
| **总页数** | 1077 页 |
| **对应认证** | CCDE 400-007 |

---

## 📚 全书结构总览

本书分为 **三大部分，18 章**，外加附录和词汇表：

### Part I: What is Network Design?（什么是网络设计？）
> 第 1-5 章，聚焦网络设计的基础概念、商业驱动和安全架构

### Part II: Core Technology Design（核心技术设计）
> 第 6-14 章，深入各种网络技术的设计考量

### Part III: Enterprise Network Architectures（企业网络架构）
> 第 15-17 章，综合架构设计实战

---

## 📋 各章详细目录与学习要点

### Part I: 什么是网络设计？

#### 第 1 章：网络设计 (Network Design)
- 网络设计基础与思维方式
- 功能需求、技术需求、应用需求
- 设计范围：Greenfield（全新）/ Brownfield（改造）
- 网络设计原则：安全普适性、可用性、复杂度控制、可扩展性、成本约束
- 网络设计技术：故障隔离、模块化、层次化设计
- 网络设计缺陷：假设、过度设计、最佳实践误区

**学习要点**：理解网络设计的核心思维框架，这是整本书的基础。

---

#### 第 2 章：为商业成功而设计 (Designing for Business Success)
- 商业优先级与驱动因素
- 商业成果与能力
- 业务连续性：RPO（恢复点目标）和 RTO（恢复时间目标）
- 项目管理方法论对比：
  - Waterfall（瀑布法）
  - Agile（敏捷法）
  - Scrum
  - Kanban

**学习要点**：网络设计必须服务于商业目标，理解不同项目管理方法的适用场景。

---

#### 第 3 章：网络的目的 (What's the Purpose of the Network?)
- 业务应用模型与约束
- 云服务模型与连接方式
- 云类型：Cloud-Agnostic 架构
- 容器化与微服务架构
- 传统部署 vs 虚拟化部署 vs 容器部署

**学习要点**：理解网络如何支撑现代应用和云架构。

---

#### 第 4 章：安全是普适的 (Security Is Pervasive)
- 零信任架构（Zero Trust Architecture）
- 安全 CIA 三要素：机密性、完整性、可用性
- 法规合规：HIPAA、PCI DSS、GDPR
- 数据主权

**学习要点**：安全不是附加项，而是设计的核心考量。

---

#### 第 5 章：参考架构模型与框架 (Reference Architecture Models and Frameworks)
- 参考架构模型与框架的概念

**学习要点**：掌握业界标准的网络架构参考模型。

---

### Part II: 核心技术设计

#### 第 6 章：传输技术 (Transport Technologies)
- 城域以太网
- MPLS 传输
- SONET/SDH
- OTN（光传输网络）
- PON（无源光网络）

**学习要点**：理解不同传输技术的选型与设计。

---

#### 第 7 章：二层技术 (Layer 2 Technologies)
- VLAN 设计与 Trunk
- STP（生成树协议）设计考量
- LAN 交换技术
- EtherChannel/链路聚合

**学习要点**：掌握二层网络的设计原则与最佳实践。

---

#### 第 8 章：三层技术 (Layer 3 Technologies)
- IGP（内部网关协议）设计：OSPF、IS-IS、EIGRP
- IGP 特性总结与路由重分发
- BGP 路由设计：属性与路径选择
- BGP 作为企业核心路由协议
- BGP 可扩展性：路由反射器、联盟

**学习要点**：这是设计重点，需要深入理解各种路由协议的设计选型。

---

#### 第 9 章：网络虚拟化 (Network Virtualization)
- MPLS 架构与控制平面
- VRF（虚拟路由转发）
- Route Distinguisher & Route Targets
- L3VPN 设计：Full Mesh、Hub-and-Spoke、Extranet
- PE-CE 路由设计
- SD-WAN 组件与策略
- SD-LAN

**学习要点**：MPLS/VPN 和 SD-WAN 是现代网络设计的核心知识。

---

#### 第 10 章：安全 (Security)
- 设备加固技术
- 二层安全考量
- 三层控制平面安全
- 远程访问与网络覆盖 (VPN)

**学习要点**：从基础设施到覆盖层的全方位安全设计。

---

#### 第 11 章：无线 (Wireless)
- IEEE 802.11 标准与协议
- 设备无线能力与安全
- 企业无线网络设计
- 高密度设计
- 语音和视频设计

**学习要点**：无线网络设计的特殊考量与高密度场景。

---

#### 第 12 章：自动化 (Automation)
- Zero-Touch Provisioning（零接触部署）
- Infrastructure as Code（基础设施即代码）
- CI/CD Pipelines

**学习要点**：网络自动化趋势，理解 IaC 和 CI/CD 在网络中的应用。

---

#### 第 13 章：组播设计 (Multicast Design)
- 组播交换与 IP 地址映射
- 组播路由：RPF、PIM
- RP 放置与域间组播
- Anycast-RP、Phantom RP、Live-Live 流
- FHRP-Aware PIM

**学习要点**：组播是设计中的难点，需要理解各种组播设计模式。

---

#### 第 14 章：网络服务与管理 (Network Services and Management)
- IPv6 设计考量与迁移策略
- QoS 设计：商业驱动与架构
- 网络管理与服务

**学习要点**：IPv6 迁移和 QoS 设计是实际工作中的高频需求。

---

### Part III: 企业网络架构

#### 第 15 章：可扩展企业园区架构设计 (Scalable Enterprise Campus Architecture Design)
- 园区网络架构设计方法论
- 层次化设计：接入层、汇聚层、核心层
- 可扩展性与弹性设计

**学习要点**：综合应用前面学到的技术进行园区网络设计。

---

#### 第 16 章：企业互联网边缘架构设计 (Enterprise Internet Edge Architecture Design)
- 互联网边缘架构
- 出口设计与多宿主
- 安全边界设计

**学习要点**：企业连接互联网的边缘架构设计。

---

#### 第 17 章：企业 WAN 架构设计 (Enterprise WAN Architecture Design)
- WAN 架构设计
- MPLS WAN vs Internet WAN
- SD-WAN 在 WAN 设计中的应用

**学习要点**：广域网架构的综合设计考量。

---

#### 第 18 章：最终准备 (Final Preparation)
- 收尾与回顾策略
- 复习建议

---

## 🎯 如何使用本指南阅读这本书

### 推荐学习路径

```
第 1-5 章（基础概念）→ 第 6-8 章（核心技术）→ 第 9 章（虚拟化）
→ 第 10-11 章（安全与无线）→ 第 12-14 章（自动化/组播/服务）
→ 第 15-17 章（综合架构）→ 第 18 章（全书回顾与学习路径）
```

### 每章学习方法

1. **先做 "Do I Know This Already?" 测验** - 评估现有知识水平
2. **阅读 Foundation Topics** - 核心内容学习
3. **完成 Exam Preparation Tasks** - 巩固关键知识点
4. **Define Key Terms** - 掌握术语定义
5. **Review All Key Topics** - 复习重点

### 🧰 附录：三个速查工具

| 附录 | 内容 | 什么时候用 |
|------|------|-----------|
| **[附录 A · 术语总表](apx-a.html)** | 全书 924 条术语，按章分组，附跨章重复词表 | 考前速刷；写方案时统一用词 |
| **[附录 B · 跨章对比速查](apx-b.html)** | 13 个横向对比矩阵（IGP / L2VPN / Overlay / WAN / 组播 / QoS…）+ 全书总表 | 拿不准"该选哪个"时查矩阵 |
| **[附录 C · 自测题库](apx-c.html)** | 18 章 × 5 题 = 90 题，答案默认折叠 | 读完一章立刻测；考前 3 天过一遍 |

> 顺序建议：**读章 → 做附录 C 的 5 题 → 错的回章里补 → 用附录 A 记词、附录 B 做取舍**。

### 你可以让我帮你做的事情

| 你可以这样说 | 我能帮你做什么 |
|-------------|--------------|
| "帮我解读第 X 章" | 我会提取该章内容并详细讲解 |
| "解释一下 SD-WAN" | 我会找到相关内容并深入解读 |
| "OSPF 和 IS-IS 有什么区别" | 基于书中的对比帮你分析 |
| "帮我总结第 X 章的要点" | 提炼核心知识点 |
| "解释零信任架构" | 用通俗语言讲解技术概念 |
| "第 X 章的 Key Terms 是什么" | 提取并解释关键术语 |
| "帮我出几道练习题" | 根据内容生成测试题 |
