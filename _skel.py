#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打印中文章节的「节 + 块」骨架，用于编写结构对齐的英文稿（临时工具）。"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from make_bilingual import parse, merge_blocks, block_kind  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent


def main():
    num = sys.argv[1]
    lo, hi = 0, 10**6
    for a in sys.argv[2:]:
        if a.startswith("--from="):
            lo = int(a.split("=")[1])
        elif a.startswith("--to="):
            hi = int(a.split("=")[1])
    paths = sorted(ROOT.glob(f"第{num}章_*.md"))
    if not paths:
        print("[ERR] not found")
        return 1
    raw = paths[0].read_text(encoding="utf-8")
    for idx, sec in enumerate(parse(raw)):
        if not (lo <= idx <= hi):
            continue
        blocks = merge_blocks(sec["blocks"])
        print(f"[{idx}] H{sec['level']} {sec['title'][:36]} n={len(blocks)}")
        for bi, b in enumerate(blocks):
            head = b.replace("\n", " | ")[:44]
            print(f"   {bi} {block_kind(b)}: {head}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
