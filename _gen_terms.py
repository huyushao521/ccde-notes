# -*- coding: utf-8 -*-
"""从各章「本章关键术语」表格抽取术语，生成附录A（术语总表）。用完即删。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent

PART_OF = {}
for n in range(1, 6):
    PART_OF[n] = "Part I · 什么是网络设计"
for n in range(6, 15):
    PART_OF[n] = "Part II · 核心技术设计"
for n in range(15, 18):
    PART_OF[n] = "Part III · 企业网络架构"
PART_OF[18] = "收尾与回顾"

SEC = re.compile(r"^## 本章(?:关键术语|术语).*?$(.*?)(?=^## |\Z)", re.M | re.S)
FN = re.compile(r"^第(\d{2})章[_-](.+)\.md$")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def main():
    out = ["<!-- status: 精讲 -->", "# 附录 A：全书术语总表", "",
           "> 由 18 章「本章关键术语」汇总而成，按章分组，用于考前速刷与写作时统一用词。",
           "> 想按关键词检索，直接用顶部搜索框（本页已纳入搜索索引）。", "", "---", ""]
    total = 0
    seen = {}
    for path in sorted(ROOT.glob("第*章_*.md")):
        m = FN.match(path.name)
        if not m:
            continue
        num = int(m.group(1))
        title = m.group(2).replace(".md", "").strip()
        raw = path.read_text(encoding="utf-8")
        sec = SEC.search(raw)
        if not sec:
            print(f"[WARN] no terms: {path.name}")
            continue
        lines = [l for l in sec.group(1).splitlines() if l.strip().startswith("|")]
        if len(lines) < 2:
            continue
        head = cells(lines[0])
        rows = []
        for idx, l in enumerate(lines):
            c = cells(l)
            if len(c) < 2:
                continue
            if all(set(x) <= {"-", ":", " "} for x in c):
                continue
            nxt = cells(lines[idx + 1]) if idx + 1 < len(lines) else []
            if nxt and all(set(x) <= {"-", ":", " "} for x in nxt):
                continue  # 表头行
            term, cn = c[0], c[1]
            term = term.replace("**", "").strip()
            note = c[2].replace("**", "").strip() if len(c) > 2 else ""
            if not term:
                continue
            rows.append((term, cn, note))
            seen.setdefault(term, []).append(num)
        total += len(rows)
        part = PART_OF[num]
        out.append(f'## 第 {num:02d} 章 · {title}')
        out.append("")
        out.append(f'<span class="ch-words">{part} · {len(rows)} 条</span>')
        out.append("")
        if sum(1 for r in rows if r[2]) > len(rows) / 2:
            out.append("| 术语 | 中文含义 | 一句话记忆 |")
            out.append("|------|---------|-----------|")
            for term, cn, note in rows:
                out.append(f"| {term} | {cn} | {note} |")
        else:
            out.append("| 术语 | 中文含义 |")
            out.append("|------|---------|")
            for term, cn, note in rows:
                out.append(f"| {term} | {cn} |")
        out.append("")
    dup = sorted([(k, v) for k, v in seen.items() if len(v) > 1], key=lambda x: -len(x[1]))
    out.append("---")
    out.append("")
    out.append("## 跨章重复出现的术语")
    out.append("")
    out.append("> 在多章出现的术语，说明它是**贯穿性概念**——这类词最容易被问到「在哪一章讲过」，也最容易在各章之间说法不一致。")
    out.append("")
    out.append("| 术语 | 出现章 |")
    out.append("|------|--------|")
    for term, chs in dup[:60]:
        uniq = sorted(set(chs))
        out.append(f"| {term} | {'、'.join(str(c) for c in uniq)} |")
    out.append("")
    (ROOT / "附录A_术语总表.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[OK] 附录A_术语总表.md  terms={total}  dup={len(dup)}")


if __name__ == "__main__":
    main()
