#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把根目录的 CCDE 中文笔记 Markdown 合成一本可打印的 HTML 与 PDF。

用法：
    python build_pdf.py            # 生成 build/book.html 与 build/CCDE_400-007_中文精讲.pdf
    python build_pdf.py --html     # 只生成 HTML，不打印 PDF
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

import markdown
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"

BOOK_TITLE = "CCDE 400-007 学习笔记"
BOOK_SUB = "Cisco Certified Design Expert · Official Cert Guide 中文精讲"
BOOK_DESC = "18 章 + 3 个附录 · 概念梳理 / 设计取舍 / 真实案例 / 经验总结"
PDF_NAME = "CCDE_400-007_中文精讲.pdf"

MD = markdown.Markdown(extensions=["extra", "sane_lists", "md_in_html"])

SEC_COUNTER = {"n": 0}


def pick(pattern: str) -> Path:
    hits = sorted(ROOT.glob(pattern))
    if not hits:
        raise SystemExit(f"[ERR] 找不到文件：{pattern}")
    return hits[0]


def fix_tables(text: str) -> str:
    """表格紧跟段落的标题行（缺空行）时补一个空行，否则不会被解析成表格。"""
    out: list[str] = []
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence:
            stripped = line.lstrip()
            prefix = ">" if stripped.startswith(">") else ""
            body = stripped[1:].lstrip() if prefix else stripped
            if body.startswith("|"):
                prev = out[-1] if out else ""
                pstripped = prev.lstrip()
                pprefix = ">" if pstripped.startswith(">") else ""
                pbody = pstripped[1:].lstrip() if pprefix else pstripped
                if pbody and not pbody.startswith("|") and pprefix == prefix:
                    out.append(prefix if prefix else "")
        out.append(line)
    return "\n".join(out)


def clean_md(text: str) -> str:
    text = fix_tables(text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = text.replace('<details markdown="1">', '<div class="foldbox" markdown="1">')
    text = text.replace("<details>", '<div class="foldbox" markdown="1">')
    text = re.sub(
        r"<summary>(.*?)</summary>",
        lambda m: f'<p class="foldhead">{m.group(1)}</p>',
        text,
        flags=re.S,
    )
    return text.replace("</details>", "</div>")


def render(md_text: str) -> str:
    MD.reset()
    return MD.convert(clean_md(md_text))


def add_ids(html: str, toc: list[tuple[int, str, str]], with_h2: bool) -> str:
    """给 h1/h2 加稳定 id，并收集目录条目。"""
    pattern = re.compile(r"<h([12])>(.*?)</h\1>", re.S)

    def repl(m: re.Match) -> str:
        level = int(m.group(1))
        text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        SEC_COUNTER["n"] += 1
        sid = f"sec-{SEC_COUNTER['n']}"
        if level == 1 or with_h2:
            toc.append((level, text, sid))
        return f'<h{level} id="{sid}">{m.group(2)}</h{level}>'

    return pattern.sub(repl, html)


def build_html() -> tuple[str, int, int]:
    chapters: list[tuple[str, Path]] = [(f"第 {n} 章", pick(f"第{n:02d}章_*.md")) for n in range(1, 19)]
    chapters += [(f"附录 {L}", pick(f"附录{L}_*.md")) for L in "ABC"]

    bodies: list[str] = []
    toc: list[tuple[int, str, str]] = []
    h2_total = 0
    for _, path in chapters:
        raw = path.read_text(encoding="utf-8")
        h2_total += len(re.findall(r"^## ", raw, flags=re.M))
        bodies.append(render(raw))

    with_h2 = True
    SEC_COUNTER["n"] = 0
    parts = [add_ids(b, toc, with_h2) for b in bodies]

    toc_items = []
    for level, text, sid in toc:
        cls = "toc-h1" if level == 1 else "toc-h2"
        toc_items.append(f'<div class="{cls}"><a href="#{sid}">{text}</a></div>')

    pyg_css = HtmlFormatter(style="friendly").get_style_defs(".codehilite")
    today = dt.date.today().isoformat()

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{BOOK_TITLE}</title>
<style>
{pyg_css}
{CSS}
</style>
</head>
<body>
<section class="cover">
  <div class="cover-rule"></div>
  <h1 class="cover-title">{BOOK_TITLE}</h1>
  <p class="cover-sub">{BOOK_SUB}</p>
  <p class="cover-desc">{BOOK_DESC}</p>
  <div class="cover-meta">
    <p>全书合订本 · 生成日期 {today}</p>
    <p>内容仅供个人学习使用，原书版权归 Cisco Press 及作者所有</p>
  </div>
</section>

<section class="toc">
  <h1 class="toc-title">目录</h1>
  <div class="toc-cols">
    {''.join(toc_items)}
  </div>
</section>

{''.join(f'<section class="chapter">{p}</section>' for p in parts)}
</body>
</html>
"""
    return html, len(chapters), len(toc)


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    script = ROOT / "print_pdf.mjs"
    cmd = ["node", str(script), str(html_path), str(pdf_path)]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise SystemExit("[ERR] PDF 打印失败")


CSS = r"""
@page { size: A4; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
  font-size: 10.5pt; line-height: 1.68; color: #1b1f24; text-align: justify;
}
p { margin: 0 0 6pt; }
a { color: #1f6feb; text-decoration: none; }
strong { font-weight: 700; color: #0d1117; }

/* ---------- 封面 ---------- */
.cover { break-after: page; height: 245mm; padding: 60mm 18mm 0; text-align: left; }
.cover-rule { width: 46mm; height: 3.2pt; background: #2f7a52; margin-bottom: 10mm; }
.cover-title { font-size: 34pt; line-height: 1.2; margin: 0 0 6mm; font-weight: 700; letter-spacing: 1pt; border: 0; padding: 0; }
.cover-sub { font-size: 13pt; color: #3d4650; margin: 0 0 4mm; }
.cover-desc { font-size: 10.5pt; color: #5a6673; margin: 0 0 60mm; }
.cover-meta { font-size: 9pt; color: #77828f; line-height: 1.8; }

/* ---------- 目录 ---------- */
.toc { break-after: page; }
.toc-title { font-size: 22pt; border: 0; padding: 0 0 4mm; margin: 0 0 6mm; border-bottom: 1.6pt solid #2f7a52; }
.toc-cols { column-count: 2; column-gap: 10mm; font-size: 8.4pt; line-height: 1.4; }
.toc-h1 { font-weight: 700; font-size: 9.6pt; margin: 6pt 0 1.5pt; break-after: avoid; }
.toc-h2 { font-size: 8.2pt; color: #46505c; margin: 0 0 0.6pt; padding-left: 3.5mm; }
.toc-h1 a, .toc-h2 a { color: inherit; }

/* ---------- 章节 ---------- */
.chapter { break-before: page; }
h1 { font-size: 19pt; line-height: 1.3; font-weight: 700; margin: 0 0 10pt; padding: 0 0 5pt; border-bottom: 1.6pt solid #2f7a52; }
h2 { font-size: 13.5pt; font-weight: 700; margin: 16pt 0 6pt; padding-left: 6pt; border-left: 4pt solid #2f7a52; break-after: avoid; }
h3 { font-size: 11.5pt; font-weight: 700; margin: 12pt 0 5pt; color: #14324a; break-after: avoid; }
h4 { font-size: 10.5pt; font-weight: 700; margin: 10pt 0 4pt; break-after: avoid; }
h1, h2, h3, h4 { page-break-after: avoid; }
ul, ol { margin: 0 0 6pt; padding-left: 18pt; }
li { margin: 0 0 3pt; }

/* ---------- 表格 ---------- */
table { width: 100%; border-collapse: collapse; font-size: 8.8pt; line-height: 1.5; margin: 8pt 0 10pt; }
thead { display: table-header-group; }
th, td { border: 0.6pt solid #c6ccd4; padding: 3.2pt 5pt; vertical-align: top; text-align: left; }
th { background: #eef2f6; font-weight: 700; }
tr, td, th { break-inside: avoid; }

/* ---------- 代码 ---------- */
pre {
  background: #f6f8fa; border: 0.6pt solid #dde3ea; border-radius: 2pt;
  padding: 6pt 8pt; font-size: 8.2pt; line-height: 1.45; margin: 6pt 0 9pt;
  white-space: pre-wrap; word-break: break-word; break-inside: avoid; text-align: left;
}
code { font-family: Consolas, "Cascadia Mono", "Courier New", monospace; font-size: 8.6pt; }
p code, li code, td code { background: #f2f4f7; padding: 0 2pt; border-radius: 2pt; }
.codehilite pre { margin: 0; }

/* ---------- 引用 / 提示 ---------- */
blockquote {
  margin: 8pt 0 10pt; padding: 6pt 10pt; background: #f4f8f5;
  border-left: 3.5pt solid #2f7a52; color: #25403a; break-inside: avoid;
}
blockquote p:last-child { margin-bottom: 0; }

/* ---------- 折叠块（打印时展开） ---------- */
.foldbox {
  margin: 8pt 0 10pt; padding: 6pt 9pt 4pt; background: #fbfcfd;
  border: 0.6pt solid #d3dae1; border-radius: 2pt;
}
.foldhead {
  font-weight: 700; color: #14324a; margin: 0 0 6pt;
  padding-bottom: 3pt; border-bottom: 0.6pt dashed #c6ccd4;
}

/* ---------- 杂项 ---------- */
hr { border: 0; border-top: 0.6pt solid #d6dbe1; margin: 10pt 0; }
img { max-width: 100%; }
"""


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", action="store_true", help="只生成 HTML")
    args = ap.parse_args()

    BUILD.mkdir(exist_ok=True)
    html, n_sec, n_toc = build_html()
    html_path = BUILD / "book.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"[OK] {html_path.name}: {n_sec} 个章节/附录，目录 {n_toc} 条，{len(html)/1024/1024:.2f} MB")

    if args.html:
        return 0

    pdf_path = BUILD / PDF_NAME
    print_pdf(html_path, pdf_path)
    size_mb = pdf_path.stat().st_size / 1024 / 1024
    print(f"[OK] {pdf_path} ({size_mb:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
