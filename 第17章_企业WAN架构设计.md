<!-- status: 骨架 -->
# 第 17 章：企业 WAN 架构设计 (Enterprise WAN Architecture Design)

> 《CCDE 400-007 Official Cert Guide》中文翻译 | 原书第 774-849 页

---

## 本章涵盖主题

- **WAN 传输模型**：L2 MPLS、L3 MPLS、Internet
- **WAN 边缘连接设计**：连接选项和冗余
- **网络覆盖技术**：IPsec、GRE、DMVPN
- **WAN 虚拟化**：Multi-VRF CE、CSC
- **WAN 设计选项**：按规模选择

---

## 基础内容 (Foundation Topics)

### 三种 WAN 传输模型

| 模型 | 成本 | 可扩展性 | 安全性 | QoS |
|------|------|---------|--------|-----|
| L2 MPLS | 高 | 中 | 高 | 是 |
| L3 MPLS | 中 | 高 | 高 | 是 |
| Internet | 低 | 高 | 低(需VPN) | 否 |

### WAN 边缘连接选项

| 连接模型 | 冗余 | 成本 | 适用场景 |
|---------|------|------|---------|
| 单宿主 WAN | 无 | 中 | 小型分支 |
| 双宿主 WAN(单路由器) | 链路 | 高 | 中大型站点 |
| 双宿主 WAN(双路由器) | 链路+设备 | 很高 | 总部/DC |

### 覆盖技术对比

| 技术 | 拓扑 | 可扩展性 | Spoke-to-Spoke |
|------|------|---------|----------------|
| IPsec | 点对点 | 低 | 否 |
| GRE | 点对点 | 低 | 否 |
| DMVPN | Hub-Spoke→Mesh | 高 | 是 |

### DMVPN 优势

- 自动建立 Full Mesh
- Spoke-to-Spoke 直接通信
- 支持动态地址 Spoke
- NAT 穿透
- 自动 IPsec 触发

### WAN 设计选项（按规模）

| 规模 | 特点 |
|------|------|
| 小到中型 | 单 WAN + 单 Internet |
| 中到大型 | 双 WAN + 双 Internet + 双路由器 |
| 大到超大型 | 区域 WAN + WAN 核心 + 数据中心 |

---

## 本章关键术语

| 术语 | 中文含义 |
|------|---------|
| L2 MPLS VPN | 二层 MPLS VPN |
| L3 MPLS VPN | 三层 MPLS VPN |
| DMVPN | 动态多点 VPN |
| Multi-VRF CE | 多 VRF 客户边缘 |
| CSC | 运营商的运营商 |
| Overlay | 覆盖网络 |
| DIA | 直接互联网接入 |
