# -*- coding: utf-8 -*-
import re
from pathlib import Path

h = Path("build/book.html").read_text(encoding="utf-8")
print("size MB", round(len(h) / 1024 / 1024, 2))
print("toc", len(re.findall(r'class="toc-h', h)), "h1", h.count("<h1"), "h2", h.count("<h2"), "h3", h.count("<h3"))
print("tables", h.count("<table"), "pre", h.count("<pre"), "foldbox", len(re.findall(r'class="foldbox"', h)))
print("raw md table rows", len(re.findall(r"\n\|[-: ]+\|", h)))
