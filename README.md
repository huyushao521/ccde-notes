# CCDE 400-007 学习笔记

Cisco Certified Design Expert (CCDE 400-007) Official Cert Guide 中文精读笔记，共 18 章。

> 内容仅供个人学习使用，原书版权归 Cisco Press 及作者所有。

## 在线阅读

部署后访问：`https://<你的用户名>.github.io/<仓库名>/`

## 章节结构

| 部分 | 章节 | 主题 |
|------|------|------|
| Part I · 什么是网络设计 | 第 1-5 章 | 设计思维 · 需求 · 业务 · 安全 · 架构框架 |
| Part II · 核心技术设计 | 第 6-14 章 | 传输 · 二层 · 三层 · 虚拟化 · 安全 · 无线 · 自动化 · 组播 · 服务管理 |
| Part III · 企业网络架构 | 第 15-17 章 | 园区 · 互联网边缘 · WAN 架构设计 |
| 备考准备 | 第 18 章 | 最终准备 |

## 本地预览

```bash
pip install markdown
python build_site.py
python -m http.server 8000 --directory docs
```

然后打开 http://localhost:8000

## 更新笔记

1. 编辑根目录的 `第NN章_xxx.md`
2. 运行 `python build_site.py` 重新生成 `docs/`
3. 提交并推送，GitHub Actions 会自动部署

## 站点结构

```
docs/                  # GitHub Pages 站点（自动生成）
  index.html           # 首页（含章节卡片）
  ch-01.html ... ch-18.html
  assets/style.css     # 样式
  assets/app.js        # 搜索 / 主题切换 / 目录高亮
  assets/search-index.json
build_site.py          # 站点生成脚本
.github/workflows/pages.yml  # 自动部署
```
