# CCDE 400-007 学习笔记

Cisco Certified Design Expert (CCDE 400-007) Official Cert Guide 中文精读笔记，共 18 章。

> 内容仅供个人学习使用，原书版权归 Cisco Press 及作者所有。
> 笔记以**理解与实战**为导向：每章包含概念梳理、设计取舍、真实案例与经验总结，不含应试技巧类内容。

## 在线阅读

https://huyushao521.github.io/ccde2023-notes/

## 章节结构与进度

| 部分 | 章节 | 主题 |
|------|------|------|
| Part I · 什么是网络设计 | 第 1-5 章 | 设计思维 · 需求 · 业务 · 安全 · 架构框架 |
| Part II · 核心技术设计 | 第 6-14 章 | 传输 · 二层 · 三层 · 虚拟化 · 安全 · 无线 · 自动化 · 组播 · 服务管理 |
| Part III · 企业网络架构 | 第 15-17 章 | 园区 · 互联网边缘 · WAN 架构设计 |
| 收尾 | 第 18 章 | 全书回顾与学习路径 |

每章 Markdown 顶部有一行成熟度标记，站点首页会据此显示徽章与进度：

```markdown
<!-- status: 精讲 -->
```

| 标记 | 含义 |
|------|------|
| 精讲 | 概念 + 取舍 + 实战案例，可独立阅读 |
| 精读 | 主干知识完整，案例较少 |
| 提纲 | 关键概念清单，待展开 |
| 骨架 | 仅章节结构 |

## 本地预览

```bash
pip install markdown
python build_site.py
python -m http.server 8000 --directory docs
```

然后打开 http://localhost:8000

## 更新笔记（一键）

```powershell
.\update.ps1 "第7章：二层技术 精讲"
```

脚本会依次执行：构建站点 → 检查改动 → 提交 → 推送；构建失败会中止，不会推旧内容。

手动等价步骤：

1. 编辑根目录的 `第NN章_xxx.md`
2. 运行 `python build_site.py` 重新生成 `docs/`
3. `git add -A && git commit -m "..." && git push`

## 辅助脚本

| 脚本 | 用途 |
|------|------|
| `build_site.py` | 生成站点、分片搜索索引、状态徽章与进度 |
| `set_status.py` | 批量写入/刷新各章成熟度标记 |
| `update.ps1` | 一键构建 + 提交 + 推送 |

## 站点结构

```
docs/                       # GitHub Pages 站点（构建产物）
  index.html                # 首页（进度条 + 章节卡片 + 状态徽章）
  ch-01.html ... ch-18.html
  assets/style.css          # 样式
  assets/app.js             # 搜索 / 主题切换 / 目录高亮
  assets/search-index.json  # 按小节分片的搜索索引
build_site.py               # 站点生成脚本
set_status.py               # 章节状态维护脚本
update.ps1                  # 一键更新脚本
```

> Pages 源为 `main` 分支的 `/docs` 目录，无需 GitHub Actions；每次 push 后约 1 分钟自动生效。
