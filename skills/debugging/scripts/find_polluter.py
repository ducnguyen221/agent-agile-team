#!/usr/bin/env python3
"""Tìm file test đầu tiên tạo ra một file/thư mục không mong muốn (ô nhiễm).

Chạy từng file test một theo thứ tự, dừng ở file đầu tiên làm đường dẫn `--check` xuất hiện.
Chỉ dùng thư viện chuẩn; chạy được trên Windows, macOS, Linux.

    python find_polluter.py --check .git --glob "tests/**/test_*.py"
    python find_polluter.py --check .git --glob "src/**/*.test.ts" --cmd "npm test -- {file}"

Mã thoát: 0 không tìm thấy · 1 tìm thấy · 2 dùng sai (thiếu file khớp, ô nhiễm đã có sẵn, lệnh sai).
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


def build_command(template: str | None, test_file: str) -> list[str]:
    if template is None:
        return [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", test_file]
    parts = shlex.split(template, posix=True)
    if not any("{file}" in p for p in parts):
        parts.append("{file}")
    return [p.replace("{file}", test_file) for p in parts]


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):  # console Windows mặc định không phải UTF-8
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Tìm test tạo ra file/thư mục không mong muốn.")
    parser.add_argument("--check", required=True, help="đường dẫn ô nhiễm cần theo dõi (tương đối với --root)")
    parser.add_argument("--glob", required=True, help="mẫu file test, hỗ trợ ** (ví dụ tests/**/test_*.py)")
    parser.add_argument("--cmd", default=None,
                        help="mẫu lệnh chạy một file, {file} được thay bằng đường dẫn; mặc định: python -m pytest -q {file}")
    parser.add_argument("--root", default=".", help="thư mục gốc dự án (mặc định: thư mục hiện hành)")
    parser.add_argument("--timeout", type=float, default=600.0, help="giây tối đa cho mỗi file test (mặc định 600)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    check = root / args.check
    files = sorted({p for p in root.glob(args.glob) if p.is_file()})
    if not files:
        print(f"Không có file nào khớp mẫu: {args.glob}", file=sys.stderr)
        return 2
    if check.exists():
        print(f"Ô nhiễm đã có sẵn trước khi chạy: {check} — xoá nó rồi chạy lại.", file=sys.stderr)
        return 2

    total = len(files)
    print(f"Tìm test tạo ra: {args.check} — {total} file khớp {args.glob}")
    for count, path in enumerate(files, 1):
        rel = path.relative_to(root).as_posix()
        print(f"[{count}/{total}] {rel}", flush=True)
        try:
            subprocess.run(build_command(args.cmd, rel), cwd=root, stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=args.timeout)
        except FileNotFoundError as exc:
            print(f"Không chạy được lệnh test: {exc}", file=sys.stderr)
            return 2
        except subprocess.TimeoutExpired:
            print(f"  quá {args.timeout:g} s, bỏ qua file này", file=sys.stderr)
        if check.exists():
            print(f"FOUND: {rel} tạo ra {args.check}")
            print("Điều tra: chạy riêng file này, rồi đọc mã của nó.")
            return 1
    print(f"Không tìm thấy: cả {total} file đều sạch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
