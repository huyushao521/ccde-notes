"""临时辅助：导出章节段落骨架，便于对齐英文段落。用完删除。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_bilingual import parse, merge_blocks, block_kind  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_skel_out"


def main() -> int:
    num = sys.argv[1]
    start = end = 10**9
    for a in sys.argv[2:]:
        if a.startswith("--from="):
            start = int(a.split("=")[1])
        if a.startswith("--to="):
            end = int(a.split("=")[1])
    path = sorted(ROOT.glob(f"第{num}*"))[0]
    secs = parse(path.read_text(encoding="utf-8"))
    lines = [f"{path.name}: {len(secs)} sections"]
    for i, s in enumerate(secs):
        blocks = merge_blocks(s["blocks"])
        lines.append(f"[{i:02d}] H{s['level']} {s['title']}  n={len(blocks)}")
        if not (start <= i <= end):
            continue
        for bi, b in enumerate(blocks):
            head = b.replace("\n", " ")[:46]
            lines.append(f"    [{bi}] {block_kind(b)}: {head}")
    OUT.mkdir(exist_ok=True)
    dest = OUT / f"{num}.txt"
    dest.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {dest} ({len(lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
