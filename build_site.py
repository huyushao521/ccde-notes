#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把根目录的 CCDE 中文笔记 Markdown 生成为 GitHub Pages 静态站点（输出到 docs/）"""

import json
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"
ASSETS = OUT / "assets"

SITE_TITLE = "CCDE 400-007 学习笔记"
SITE_SUB = "Cisco Certified Design Expert · Official Cert Guide 中文精读"

# (分组标识, 中文名, 副标题, 起始章, 结束章)
PART_DEFS = [
    ("part1", "Part I · 什么是网络设计", "设计思维 · 需求 · 业务 · 安全 · 架构框架", 1, 5),
    ("part2", "Part II · 核心技术设计", "传输 · 二层 · 三层 · 虚拟化 · 安全 · 无线 · 自动化 · 组播 · 服务管理", 6, 14),
    ("part3", "Part III · 企业网络架构", "园区 · 互联网边缘 · WAN 架构设计", 15, 17),
    ("part4", "备考准备", "最终准备与备考清单", 18, 18),
]

FILENAME_RE = re.compile(r"^第(\d{2})章[_-](.+)\.md$")


def slug(num: int) -> str:
    return f"ch-{num:02d}"


def collect_chapters():
    chapters = []
    for path in sorted(ROOT.glob("第*章_*.md")):
        m = FILENAME_RE.match(path.name)
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).strip()
        raw = path.read_text(encoding="utf-8")
        h1 = ""
        for line in raw.splitlines():
            if line.startswith("# "):
                h1 = line[2:].strip()
                break
        chapters.append(
            {
                "num": num,
                "title": title,
                "h1": h1,
                "path": path,
                "raw": raw,
                "slug": slug(num),
            }
        )
    chapters.sort(key=lambda c: c["num"])
    return chapters


def part_of(num: int):
    for key, name, sub, start, end in PART_DEFS:
        if start <= num <= end:
            return key, name, sub
    return "part9", "其他", ""


def make_md():
    return markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
        extension_configs={
            "toc": {"permalink": "", "permalink_class": "anchor", "toc_depth": "2-3"},
        },
    )


def render(raw: str):
    md = make_md()
    return md.convert(raw), md.toc


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sidebar_html(chapters, current_slug=None):
    blocks = []
    for key, name, sub, start, end in PART_DEFS:
        items = [c for c in chapters if start <= c["num"] <= end]
        if not items:
            continue
        links = []
        for c in items:
            cls = "nav-link active" if c["slug"] == current_slug else "nav-link"
            links.append(
                f'<a class="{cls}" href="{c["slug"]}.html">'
                f'<span class="nav-num">{c["num"]:02d}</span>'
                f'<span class="nav-title">{c["title"]}</span></a>'
            )
        blocks.append(
            f'<div class="nav-group">'
            f'<div class="nav-head"><span class="nav-part">{name}</span>'
            f'<span class="nav-sub">{sub}</span></div>'
            f'<div class="nav-items">{"".join(links)}</div></div>'
        )
    return "".join(blocks)


def page_shell(title: str, content: str, sidebar: str, *, toc: str = "",
               prev_link: str = "", next_link: str = "", is_home: bool = False,
               root: str = ""):
    body_class = "layout-home" if is_home else "layout-doc"
    toc_panel = (
        f'<aside class="toc-rail"><div class="toc-inner">'
        f'<div class="toc-title">本页目录</div>{toc}</div></aside>'
        if toc
        else '<aside class="toc-rail"></aside>'
    )
    pager = ""
    if prev_link or next_link:
        pager = f'<nav class="pager">{prev_link}{next_link}</nav>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{SITE_SUB}">
<link rel="stylesheet" href="{root}assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%231e5fd0'/><text y='72' x='50' font-size='58' text-anchor='middle' fill='white' font-family='sans-serif' font-weight='bold'>C</text></svg>">
</head>
<body class="{body_class}">
<div class="progress-bar" id="progressBar"></div>

<header class="topbar">
  <button class="menu-btn" id="menuBtn" aria-label="菜单"><span></span><span></span><span></span></button>
  <a class="brand" href="{root}index.html">
    <span class="brand-mark">C</span>
    <span class="brand-text"><strong>{SITE_TITLE}</strong><small>{SITE_SUB}</small></span>
  </a>
  <div class="search-wrap">
    <input id="searchInput" type="search" placeholder="搜索章节 / 关键词…" autocomplete="off" aria-label="搜索">
    <div class="search-results" id="searchResults"></div>
  </div>
  <button class="theme-btn" id="themeBtn" aria-label="切换主题">◐</button>
</header>

<div class="shell">
  <nav class="sidebar" id="sidebar">
    <div class="sidebar-inner">{sidebar}</div>
    <div class="sidebar-foot">CCDE 400-007 · 学习笔记</div>
  </nav>
  <div class="scrim" id="scrim"></div>

  <main class="main">
    <article class="article markdown-body">{content}</article>
    {pager}
    <footer class="foot">
      <span>CCDE 400-007 学习笔记 · 基于 Cisco Press 官方认证指南整理</span>
      <span class="foot-note">内容仅供个人学习使用</span>
    </footer>
  </main>
  {toc_panel}
</div>

<button class="to-top" id="toTop" aria-label="回到顶部">↑</button>
<script src="{root}assets/app.js"></script>
</body>
</html>
"""


def pager_link(ch, direction):
    if not ch:
        return ""
    label = "上一章" if direction == "prev" else "下一章"
    return (
        f'<a class="pager-link {direction}" href="{ch["slug"]}.html">'
        f'<span class="pager-label">{label}</span>'
        f'<span class="pager-title">{ch["num"]:02d} · {ch["title"]}</span></a>'
    )


def main():
    OUT.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    chapters = collect_chapters()
    if not chapters:
        print("[ERROR] no chapter markdown found")
        return 1

    search_index = []

    for i, ch in enumerate(chapters):
        body, toc = render(ch["raw"])
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = chapters[i + 1] if i < len(chapters) - 1 else None
        html = page_shell(
            f'{ch["title"]} · 第 {ch["num"]} 章 · {SITE_TITLE}',
            body,
            sidebar_html(chapters, ch["slug"]),
            toc=toc,
            prev_link=pager_link(prev_ch, "prev"),
            next_link=pager_link(next_ch, "next"),
            root="",
        )
        (OUT / f'{ch["slug"]}.html').write_text(html, encoding="utf-8")
        search_index.append(
            {
                "u": f'{ch["slug"]}.html',
                "n": ch["num"],
                "t": ch["title"],
                "x": strip_html(body)[:6000],
            }
        )
        print(f"[OK] {ch['slug']}.html  <- {ch['path'].name}")

    # 首页
    guide = ROOT / "CCDE_Study_Guide.md"
    home_parts = []
    if guide.exists():
        home_body, _ = render(guide.read_text(encoding="utf-8"))
        home_parts.append(home_body)

    cards = []
    for key, name, sub, start, end in PART_DEFS:
        items = [c for c in chapters if start <= c["num"] <= end]
        if not items:
            continue
        links = "".join(
            f'<a class="card" href="{c["slug"]}.html">'
            f'<span class="card-num">{c["num"]:02d}</span>'
            f'<span class="card-body"><strong>{c["title"]}</strong>'
            f'<em>{c["h1"]}</em></span></a>'
            for c in items
        )
        cards.append(
            f'<section class="card-group"><h2 class="group-title">{name}</h2>'
            f'<p class="group-sub">{sub}</p><div class="card-grid">{links}</div></section>'
        )

    hero = (
        '<div class="hero">'
        f'<h1>{SITE_TITLE}</h1>'
        f'<p>{SITE_SUB}</p>'
        f'<div class="hero-stats"><span><b>{len(chapters)}</b> 章笔记</span>'
        f'<span><b>3</b> 大部分</span><span><b>400-007</b> 考试代码</span></div>'
        "</div>"
    )
    home_content = hero + '<div class="cards-wrap">' + "".join(cards) + "</div>"
    if home_parts:
        home_content += '<hr class="home-sep">' + "".join(home_parts)

    (OUT / "index.html").write_text(
        page_shell(SITE_TITLE, home_content, sidebar_html(chapters), is_home=True, root=""),
        encoding="utf-8",
    )
    print("[OK] index.html")

    (ASSETS / "search-index.json").write_text(
        json.dumps(search_index, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[OK] search-index.json ({len(search_index)} entries)")
    print(f"\nDone -> {OUT}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
