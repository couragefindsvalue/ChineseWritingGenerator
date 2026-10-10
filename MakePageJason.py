#!/usr/bin/env python3
"""
扫描字帖文件夹，生成 pages.json（网页用它来知道有哪些页码）。

目录结构（和网页一致）:
    FinalChars/
        index.html
        001/chars/001002.png ...
        024/chars/024001.png ...
        pages.json            <-- 本脚本生成

用法:
    python make_pages_json.py                  # 扫描脚本所在的文件夹
    python make_pages_json.py D:\\Handwriting\\FinalChars
    python make_pages_json.py 文件夹 --sub chars --min 1   # --min: 少于几张图的页码忽略
    python make_pages_json.py 文件夹 --counts  # 额外生成 pages_info.json（每页字数，仅供查看）

只用 Python 标准库，不需要安装任何东西。
"""
import argparse
import json
import re
import sys
from pathlib import Path

IMG_EXTS = {".png", ".webp", ".jpg", ".jpeg"}


def count_images(folder: Path) -> int:
    if not folder.is_dir():
        return 0
    return sum(1 for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXTS)


def main():
    ap = argparse.ArgumentParser(description="扫描页码文件夹并生成 pages.json")
    ap.add_argument("root", nargs="?", default=None, help="字帖根目录（默认：脚本所在文件夹）")
    ap.add_argument("--sub", default="chars", help="页码文件夹里放图片的子文件夹名，默认 chars；图片直接放在页码文件夹里就写 --sub ''")
    ap.add_argument("--min", type=int, default=1, help="至少有几张图片才算有效页码，默认 1")
    ap.add_argument("--counts", action="store_true", help="同时生成 pages_info.json（每页字数）")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve() if args.root else Path(__file__).resolve().parent
    if not root.is_dir():
        sys.exit(f"找不到文件夹：{root}")

    pages, info, skipped = [], {}, []
    for d in sorted(root.iterdir()):
        # 页码文件夹：名字是 1~3 位数字，如 001、024（也接受 1、24，自动补成 3 位）
        if not d.is_dir() or not re.fullmatch(r"\d{1,3}", d.name):
            continue
        code = f"{int(d.name):03d}"
        n = count_images(d / args.sub if args.sub else d)
        if n >= args.min:
            pages.append(code)
            info[code] = n
        else:
            skipped.append((d.name, n))

    pages = sorted(set(pages))
    out = root / "pages.json"
    out.write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")

    print(f"扫描目录：{root}")
    print(f"找到 {len(pages)} 个页码文件夹，已写入：{out}")
    if pages:
        print("页码：" + ", ".join(pages))
    for name, n in skipped:
        print(f"[忽略] {name}：{args.sub or '.'} 里只有 {n} 张图片")
    if not pages:
        print("提示：没有找到有效页码。请确认结构是  页码/%s/页码001.png" % (args.sub or ""))

    if args.counts:
        (root / "pages_info.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"每页字数已写入：{root / 'pages_info.json'}  （共 {sum(info.values())} 字）")


if __name__ == "__main__":
    main()