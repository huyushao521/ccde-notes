"""把「纯英文笔记 + 中文章节」合成为一段英文一段中文的双语 Markdown。

用法：
    python make_bilingual.py 01 --check     # 只打印对齐报告
    python make_bilingual.py 01             # 生成（覆盖 EN_Chapter01_*.md）

约定：
    - 英文源：EN_ChapterNN_*.md（纯英文，标题层级与中文章节一一对应）
    - 中文源：第NN章_*.md
    - 输出：直接写回英文源文件，正文改为「英文段落 + 中文对照块」
      <div class="zh" markdown="1"> ... </div>
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent

# 某些节的段落切分在两种语言里粗细不同，这里手工指定「英文块序号组 -> 中文块序号组」
# 例如情景演练：英文把「小标题」和「列表」拆成两块，中文是同一块
PAIR_OVERRIDES = {
    47: [([0], [0]), ([1], [1]), ([2, 3], [2]), ([4, 5], [3])],
    48: [([0], [0]), ([1], [1]), ([2, 3], [2]), ([4, 5], [3])],
    49: [([0], [0]), ([1], [1]), ([2, 3], [2]), ([4, 5], [3])],
}

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
PAREN_EN_RE = re.compile(r"\s*[（(][A-Za-z0-9 ,\-/'’&.、]*[A-Za-z][A-Za-z0-9 ,\-/'’&.、]*[)）]\s*$")
NUM_PREFIX_RE = re.compile(r"^\d+\.\s*")


def parse(raw: str):
    """按标题切节，再按空行切段；丢弃 --- 分隔线与 HTML 注释"""
    sections = []
    title, level, blocks = "", 0, []
    buf, in_fence = [], False

    def flush():
        nonlocal buf
        if buf:
            text = "\n".join(buf).strip()
            if text and text.strip("-").strip() == "":
                buf = []
                return
            if not text.startswith("<!--"):
                blocks.append(text)
            buf = []

    for line in raw.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and re.match(r"^#{1,4} ", line):
            flush()
            if title:
                sections.append({"title": title, "level": level, "blocks": blocks})
            m = re.match(r"^(#+) (.+)$", line)
            title, level, blocks = m.group(2).strip(), len(m.group(1)), []
            continue
        if not in_fence and not line.strip():
            flush()
            continue
        buf.append(line)
    flush()
    if title:
        sections.append({"title": title, "level": level, "blocks": blocks})
    return sections


def block_kind(block: str) -> str:
    head = block.lstrip()
    if re.match(r"^[-*+]\s", head):
        return "ul"
    if re.match(r"^\d+\.\s", head):
        return "ol"
    if head.startswith(">"):
        return "quote"
    return "p"


def merge_blocks(blocks):
    """把相邻且同类的列表/引用块合成一块，让两种语言的切分粒度一致"""
    out = []
    for b in blocks:
        if out and block_kind(out[-1]) == block_kind(b) and block_kind(b) in ("ul", "ol", "quote"):
            out[-1] = out[-1] + "\n" + b
        else:
            out.append(b)
    return out


def zh_core(title: str) -> str:
    """从中文标题里去掉末尾的英文括注和编号前缀"""
    core = PAREN_EN_RE.sub("", title).strip()
    core = NUM_PREFIX_RE.sub("", core).strip()
    return core


def combine_title(en_title: str, zh_title: str) -> str:
    core = zh_core(zh_title)
    if not core or not CJK_RE.search(core):
        return en_title
    if core in en_title:
        return en_title
    return f"{en_title} · {core}"


def zh_div(text: str) -> str:
    return f'<div class="zh" markdown="1">\n\n{text}\n\n</div>'


def build(en_raw: str, zh_raw: str, check: bool = False, chapter: str = "01") -> str:
    overrides = PAIR_OVERRIDES if chapter == "01" else {}
    en, zh = parse(en_raw), parse(zh_raw)
    if len(en) != len(zh):
        print(f"[WARN] 节数不一致：英文 {len(en)} / 中文 {len(zh)}")

    out = []
    problems = []
    for idx in range(min(len(en), len(zh))):
        e, z = en[idx], zh[idx]
        eb, zb = merge_blocks(e["blocks"]), merge_blocks(z["blocks"])
        heading = "#" * e["level"] + " " + combine_title(e["title"], z["title"])

        if idx in overrides:
            pairs = overrides[idx]
        elif len(eb) == len(zb):
            pairs = [([i], [i]) for i in range(len(eb))]
        else:
            problems.append(f"节 {idx:02d} {e['title']} 英文 {len(eb)} 块 / 中文 {len(zb)} 块")
            pairs = [([i], [i]) for i in range(min(len(eb), len(zb)))]

        chunk = [heading]
        for ei, zi in pairs:
            en_text = "\n\n".join(eb[i] for i in ei)
            zh_text = "\n\n".join(zb[i] for i in zi)
            pieces = []
            if en_text:
                pieces.append(en_text)
            if zh_text:
                pieces.append(zh_div(zh_text))
            chunk.append("\n\n".join(pieces))
        # 补齐未被配对的尾巴
        used_en = {i for p in pairs for i in p[0]}
        used_zh = {i for p in pairs for i in p[1]}
        for i, b in enumerate(eb):
            if i not in used_en:
                chunk.append(b)
        for i, b in enumerate(zb):
            if i not in used_zh:
                chunk.append(zh_div(b))

        if e["level"] == 2 and out:
            chunk[0] = "---\n\n" + chunk[0]
        out.append("\n\n".join(chunk))

    for p in problems:
        print("[PAIR?]", p)
    if check:
        return "\n\n".join(out)
    return "\n\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("num", help="章号，例如 01")
    ap.add_argument("--check", action="store_true", help="只打印对齐报告，不写文件")
    args = ap.parse_args(argv)

    en_paths = sorted(ROOT.glob(f"EN_Chapter{args.num}_*.md"))
    zh_paths = sorted(ROOT.glob(f"第{args.num}章_*.md"))
    if not en_paths or not zh_paths:
        print("[ERR] 找不到英文或中文源文件")
        return 1
    en_path, zh_path = en_paths[0], zh_paths[0]

    en_raw = en_path.read_text(encoding="utf-8")
    if '<div class="zh"' in en_raw and not args.check:
        print(f"[ERR] {en_path.name} 已经是双语格式，拒绝重复处理（可从 git 取回纯英文版本）")
        return 1

    result = build(en_raw, zh_raw=zh_path.read_text(encoding="utf-8"), check=args.check, chapter=args.num)
    if args.check:
        print(result[:1500])
        print("...")
        return 0

    en_path.write_text(result, encoding="utf-8")
    print(f"[OK] {en_path.name} <- {zh_path.name}（双语对照）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
