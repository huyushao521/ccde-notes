#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给每章 Markdown 顶部写入成熟度标记： <!-- status: 精讲 --> （一次性维护脚本）"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STATUS = {}
for n in range(1, 7):
    STATUS[n] = "精讲"
for n in (7, 8):
    STATUS[n] = "精读"
for n in range(9, 15):
    STATUS[n] = "提纲"
for n in range(15, 18):
    STATUS[n] = "骨架"
STATUS[18] = "精讲"


def main():
    for path in sorted(ROOT.glob("第*章_*.md")):
        m = re.match(r"^第(\d{2})章", path.name)
        if not m:
            continue
        num = int(m.group(1))
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\A\s*<!--\s*status:.*?-->\s*\n", "", text, flags=re.S)
        text = f"<!-- status: {STATUS[num]} -->\n" + text
        path.write_text(text, encoding="utf-8")
        print(f"[SET] {path.name} -> {STATUS[num]}")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
