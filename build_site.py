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
    ("part4", "收尾与串讲", "全书串讲 · 设计决策流程", 18, 18),
]

FILENAME_RE = re.compile(r"^第(\d{2})章[_-](.+)\.md$")

# (文件名, slug, 编号字母, 标题, 副标题)
APPENDIX_DEFS = [
    ("附录A_术语总表.md", "apx-a", "A", "术语总表", "全书术语按章速刷"),
    ("附录B_跨章对比速查.md", "apx-b", "B", "跨章对比速查", "13 个横向对比矩阵"),
    ("附录C_自测题库.md", "apx-c", "C", "自测题库", "18 章 × 5 题 · 答案折叠"),
]

# 章节成熟度：按中文字数自动判定（也可在 md 顶部用 <!-- status: 精讲 --> 覆盖）
STATUS_RULES = [(4000, "精讲"), (1800, "精读"), (800, "提纲"), (0, "骨架")]
STATUS_RE = re.compile(r"<!--\s*status:\s*(.+?)\s*-->")
H2_RE = re.compile(r'<h2[^>]*id="([^"]*)"[^>]*>(.*?)</h2>', re.S)


def slug(num: int) -> str:
    return f"ch-{num:02d}"


def cn_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fa5]", text))


def detect_status(raw: str, words: int) -> str:
    m = STATUS_RE.search(raw)
    if m:
        return m.group(1)
    for threshold, name in STATUS_RULES:
        if words >= threshold:
            return name
    return "骨架"


def shard_sections(body: str):
    """把一章正文按 h2 切片，保证长章节每个小节都能被搜到"""
    chunks = []
    for part in re.split(r"(?=<h2[^>]*>)", body):
        m = H2_RE.search(part)
        anchor = m.group(1) if m else ""
        section = strip_html(m.group(2)) if m else ""
        text = strip_html(part)
        if not text:
            continue
        for i in range(0, len(text), 2000):
            chunks.append(
                {
                    "anchor": anchor if i == 0 else "",
                    "section": section,
                    "text": text[i : i + 2000],
                }
            )
    return chunks


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


def collect_appendices():
    items = []
    for idx, (fname, slug_str, letter, title, sub) in enumerate(APPENDIX_DEFS):
        path = ROOT / fname
        if not path.exists():
            print(f"[WARN] missing appendix: {fname}")
            continue
        raw = path.read_text(encoding="utf-8")
        h1 = ""
        for line in raw.splitlines():
            if line.startswith("# "):
                h1 = line[2:].strip()
                break
        items.append(
            {
                "slug": slug_str,
                "letter": letter,
                "title": title,
                "sub": sub,
                "h1": h1,
                "path": path,
                "raw": raw,
                "num": f"附录 {letter}",
                "order": 19 + idx,
            }
        )
    return items


def part_of(num: int):
    for key, name, sub, start, end in PART_DEFS:
        if start <= num <= end:
            return key, name, sub
    return "part9", "其他", ""


def make_md():
    return markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list", "md_in_html"],
        extension_configs={
            "toc": {"permalink": "", "permalink_class": "anchor", "toc_depth": "2-3"},
        },
    )


def render(raw: str):
    md = make_md()
    return md.convert(STATUS_RE.sub("", raw)), md.toc


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sidebar_html(chapters, current_slug=None, appendices=()):
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
    if appendices:
        links = []
        for a in appendices:
            cls = "nav-link active" if a["slug"] == current_slug else "nav-link"
            links.append(
                f'<a class="{cls}" href="{a["slug"]}.html">'
                f'<span class="nav-num">{a["letter"]}</span>'
                f'<span class="nav-title">{a["title"]}</span></a>'
            )
        blocks.append(
            f'<div class="nav-group">'
            f'<div class="nav-head"><span class="nav-part">附录 · 速查工具</span>'
            f'<span class="nav-sub">术语 · 对比 · 自测</span></div>'
            f'<div class="nav-items">{"".join(links)}</div></div>'
        )
    return "".join(blocks)


def board_html(page_label: str, page_key: str) -> str:
    """页面底部的留言板：主通道用 giscus（GitHub Discussions，多端自动同步），
    本机速记（localStorage）折叠保留，用于离线草稿与导出 .md 贴给 AI 改稿。"""
    return f"""
    <section class="board" id="board" data-page="{page_label}" data-key="{page_key}">
      <div class="board-head">
        <h2 class="board-title">留言板 · 想法与勘误</h2>
        <span class="board-count" id="boardCount"></span>
      </div>
      <p class="board-tip">留言直接写入本仓库的 <strong>GitHub Discussions</strong>：手机、平板、任何浏览器打开都自动同步，
        不再有「换浏览器就丢」的问题。首次发言需用 GitHub 账号登录一次，之后免登录。</p>
      <div class="giscus-shell" id="giscusThread"></div>
      <details class="board-local">
        <summary>本机速记（离线草稿，仅当前浏览器，不自动同步）</summary>
        <div class="board-local-body">
          <p class="board-tip">这里的内容只存在当前浏览器。适合离线随手记；想并入仓库就点「导出 .json」后运行
            <code>.\\update.ps1</code>，想让我改稿就点「复制全部」或「导出 .md」贴给我。</p>
          <form class="board-form" id="boardForm">
            <div class="board-where">
              <span class="board-chip" id="boardWhere">{page_label}</span>
              <span class="board-chip anchor" id="boardAnchor">未定位到小节</span>
            </div>
            <textarea id="boardInput" rows="3"
              placeholder="例如：这节说 RSTP 收敛是秒级，但没讲清楚 50 秒指的是什么场景…（Ctrl + Enter 提交）"></textarea>
            <div class="board-actions">
              <button type="submit" class="board-btn primary">提交留言</button>
              <span class="board-hint" id="boardHint"></span>
            </div>
          </form>
          <div class="board-tools">
            <div class="board-filter" id="boardFilter">
              <button type="button" class="board-tab active" data-scope="page">仅本页</button>
              <button type="button" class="board-tab" data-scope="all">全部章节</button>
            </div>
            <div class="board-tools-right">
              <button type="button" class="board-btn" id="boardCopy">复制全部</button>
              <button type="button" class="board-btn primary" id="boardSync">导出 .json</button>
              <button type="button" class="board-btn" id="boardExport">导出 .md</button>
              <button type="button" class="board-btn danger" id="boardClear">清空</button>
            </div>
          </div>
          <ul class="board-list" id="boardList"></ul>
          <p class="board-empty" id="boardEmpty">本页还没有留言，随手记一条吧。</p>
        </div>
      </details>
    </section>
"""


def page_shell(title: str, content: str, sidebar: str, *, toc: str = "",
               prev_link: str = "", next_link: str = "", is_home: bool = False,
               root: str = "", board: str = ""):
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
<link rel="stylesheet" href="{root}assets/board.css">
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
    {board}
    <footer class="foot">
      <span>CCDE 400-007 学习笔记 · 基于 Cisco Press 官方认证指南整理</span>
      <span class="foot-note">内容仅供个人学习使用</span>
    </footer>
  </main>
  {toc_panel}
</div>

<button class="to-top" id="toTop" aria-label="回到顶部">↑</button>
<script src="{root}assets/app.js"></script>
<script src="{root}assets/board.js"></script>
<script src="{root}assets/giscus.js"></script>
</body>
</html>
"""


def pager_link(ch, direction):
    if not ch:
        return ""
    label = "上一章" if direction == "prev" else "下一章"
    num = ch["num"]
    num_txt = f"{num:02d}" if isinstance(num, int) else str(num)
    return (
        f'<a class="pager-link {direction}" href="{ch["slug"]}.html">'
        f'<span class="pager-label">{label}</span>'
        f'<span class="pager-title">{num_txt} · {ch["title"]}</span></a>'
    )


def main():
    OUT.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    chapters = collect_chapters()
    if not chapters:
        print("[ERROR] no chapter markdown found")
        return 1

    appendices = collect_appendices()
    nav_chain = chapters + appendices

    search_index = []

    for i, ch in enumerate(chapters):
        body, toc = render(ch["raw"])
        ch["words"] = cn_count(ch["raw"])
        ch["status"] = detect_status(ch["raw"], ch["words"])
        meta = (
            f'<div class="ch-meta">'
            f'<span class="badge" data-s="{ch["status"]}">{ch["status"]}</span>'
            f'<span class="ch-words">约 {ch["words"]} 字</span></div>'
        )
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = nav_chain[i + 1] if i + 1 < len(nav_chain) else None
        html = page_shell(
            f'{ch["title"]} · 第 {ch["num"]} 章 · {SITE_TITLE}',
            meta + body,
            sidebar_html(chapters, ch["slug"], appendices),
            toc=toc,
            prev_link=pager_link(prev_ch, "prev"),
            next_link=pager_link(next_ch, "next"),
            root="",
            board=board_html(f'第 {ch["num"]:02d} 章 · {ch["title"]}', ch["slug"]),
        )
        (OUT / f'{ch["slug"]}.html').write_text(html, encoding="utf-8")
        for shard in shard_sections(body):
            target = f'{ch["slug"]}.html'
            if shard["anchor"]:
                target += f'#{shard["anchor"]}'
            search_index.append(
                {
                    "u": target,
                    "n": ch["num"],
                    "t": ch["title"],
                    "s": shard["section"],
                    "x": shard["text"],
                }
            )
        print(f"[OK] {ch['slug']}.html  <- {ch['path'].name}")

    # 附录页
    for i, ap in enumerate(appendices):
        body, toc = render(ap["raw"])
        prev_item = nav_chain[len(chapters) + i - 1] if (len(chapters) + i - 1) >= 0 else None
        next_item = appendices[i + 1] if i + 1 < len(appendices) else None
        meta = (
            f'<div class="ch-meta">'
            f'<span class="badge" data-s="附录">附录 {ap["letter"]}</span>'
            f'<span class="ch-words">{ap["sub"]}</span></div>'
        )
        html = page_shell(
            f'{ap["title"]} · {SITE_TITLE}',
            meta + body,
            sidebar_html(chapters, ap["slug"], appendices),
            toc=toc,
            prev_link=pager_link(prev_item, "prev"),
            next_link=pager_link(next_item, "next"),
            root="",
            board=board_html(f'附录 {ap["letter"]} · {ap["title"]}', ap["slug"]),
        )
        (OUT / f'{ap["slug"]}.html').write_text(html, encoding="utf-8")
        label = f'附录 {ap["letter"]} · {ap["title"]}'
        for shard in shard_sections(body):
            target = f'{ap["slug"]}.html'
            if shard["anchor"]:
                target += f'#{shard["anchor"]}'
            search_index.append(
                {
                    "u": target,
                    "n": ap["order"],
                    "lb": label,
                    "t": ap["title"],
                    "s": shard["section"],
                    "x": shard["text"],
                }
            )
        print(f'[OK] {ap["slug"]}.html  <- {ap["path"].name}')

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
            f'<em>{c["h1"]}</em>'
            f'<span class="badge" data-s="{c["status"]}">{c["status"]}</span>'
            f'</span></a>'
            for c in items
        )
        cards.append(
            f'<section class="card-group"><h2 class="group-title">{name}</h2>'
            f'<p class="group-sub">{sub}</p><div class="card-grid">{links}</div></section>'
        )

    if appendices:
        links = "".join(
            f'<a class="card" href="{a["slug"]}.html">'
            f'<span class="card-num">{a["letter"]}</span>'
            f'<span class="card-body"><strong>{a["title"]}</strong>'
            f'<em>{a["sub"]}</em>'
            f'<span class="badge" data-s="附录">附录</span>'
            f'</span></a>'
            for a in appendices
        )
        cards.append(
            f'<section class="card-group"><h2 class="group-title">附录 · 速查工具</h2>'
            f'<p class="group-sub">术语表 · 跨章对比 · 自测题</p>'
            f'<div class="card-grid">{links}</div></section>'
        )

    done = sum(1 for c in chapters if c["status"] == "精讲")
    pct = round(done / len(chapters) * 100)
    hero = (
        '<div class="hero">'
        f'<h1>{SITE_TITLE}</h1>'
        f'<p>{SITE_SUB}</p>'
        f'<div class="hero-stats"><span><b>{len(chapters)}</b> 章笔记</span>'
        f'<span><b>{len(PART_DEFS)}</b> 大部分</span>'
        f'<span><b>{len(appendices)}</b> 个附录</span>'
        f'<span><b>{done}/{len(chapters)}</b> 已精讲</span></div>'
        f'<div class="hero-progress" title="精讲进度 {pct}%">'
        f'<span style="width:{pct}%"></span></div>'
        "</div>"
    )
    home_content = hero + '<div class="cards-wrap">' + "".join(cards) + "</div>"
    if home_parts:
        home_content += '<hr class="home-sep">' + "".join(home_parts)

    (OUT / "index.html").write_text(
        page_shell(
            SITE_TITLE,
            home_content,
            sidebar_html(chapters, None, appendices),
            is_home=True,
            root="",
            board=board_html("首页 · 引言与目录", "index"),
        ),
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
