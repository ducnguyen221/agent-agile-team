"""Hook chặn ghi vào đường bảo vệ — đọc JSON hook ở stdin, chỉ thư viện chuẩn, không mở file đích.

Gọi: python protect_paths.py --format {claude,codex,antigravity} [--deny-glob G ...] [--allow-name N ...]
Khớp: claude/codex in `blocked: <đường> (<luật>)` ở stderr rồi thoát 2; antigravity in JSON `deny` ở stdout, thoát 0.
Không khớp: claude/codex thoát 0, không in; antigravity in `{}`. JSON hỏng: chặn (đóng khi lỗi).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from typing import TextIO

DEFAULT_DENY_NAMES = (".env", ".env.*", "*.pem", "*.key", "id_rsa", "id_rsa.*")
DEFAULT_DENY_SEGMENTS = (".secret", ".git")
DEFAULT_ALLOW_NAMES = (".env.example",)
PATH_KEYS = ("file_path", "path", "notebook_path")
PATCH_PREFIXES = ("*** Add File: ", "*** Update File: ", "*** Delete File: ")
FORMATS = ("claude", "codex", "antigravity")
BAD_INPUT = "bad hook input"


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _walk(node: object, found: list) -> None:
    """Duyệt mọi độ sâu: gom chuỗi ở khoá đường, và dòng vá trong mọi chuỗi."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in PATH_KEYS and isinstance(value, str):
                found.append(value)
            _walk(value, found)
    elif isinstance(node, list):
        for item in node:
            _walk(item, found)
    elif isinstance(node, str):
        for line in node.splitlines():
            line = line.lstrip()
            for prefix in PATCH_PREFIXES:
                if line.startswith(prefix):
                    found.append(line[len(prefix):].strip())


def extract_paths(payload: object) -> list[str]:
    """Mọi đường ứng viên trong payload: giá trị chuỗi của PATH_KEYS ở bất kỳ độ sâu, cộng đường sau PATCH_PREFIXES.

    `\\` đổi thành `/`; giữ thứ tự gặp, bỏ trùng và chuỗi rỗng."""
    raw: list[str] = []
    _walk(payload, raw)
    paths: list[str] = []
    for item in raw:
        path = _norm(item)
        if path and path not in paths:
            paths.append(path)
    return paths


def _fits(text: str, pattern: str) -> bool:
    # So không phân biệt hoa thường: Windows và macOS mặc định coi `.ENV` là `.env`.
    return fnmatch.fnmatchcase(text.casefold(), pattern.casefold())


def match_rule(path: str, deny_globs: tuple[str, ...] = (),
               allow_names: tuple[str, ...] = DEFAULT_ALLOW_NAMES) -> str | None:
    """Tên luật chặn đường này (`name:<mẫu>`, `segment:<tên>`, `glob:<mẫu>`) hoặc None.

    Chỉ so chuỗi, không chạm hệ thống file. Tên trong `allow_names` bỏ qua luật tên, không bỏ qua luật đoạn đường và glob."""
    path = _norm(path)
    parts = [p for p in path.split("/") if p and p != "."]
    name = parts[-1] if parts else ""
    if name and not any(_fits(name, a) for a in allow_names):
        for pattern in DEFAULT_DENY_NAMES:
            if _fits(name, pattern):
                return "name:" + pattern
    for segment in DEFAULT_DENY_SEGMENTS:
        if any(part.casefold() == segment.casefold() for part in parts):
            return "segment:" + segment
    # glob so với cả đường và từng đoạn đuôi, để mẫu tương đối khớp đường tuyệt đối
    tails = [path] + ["/".join(parts[i:]) for i in range(len(parts))]
    for pattern in deny_globs:
        if any(_fits(tail, _norm(pattern)) for tail in tails):
            return "glob:" + pattern
    return None


def _deny(fmt: str, reason: str, stdout: TextIO, stderr: TextIO) -> int:
    if fmt == "antigravity":
        stdout.write(json.dumps({"decision": "deny", "reason": reason}) + "\n")
        return 0
    stderr.write(reason + "\n")
    return 2


def main(argv: list[str] | None = None, stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout,
         stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description="Chặn hook ghi vào đường bảo vệ.")
    parser.add_argument("--format", required=True, choices=FORMATS)
    parser.add_argument("--deny-glob", action="append", default=[])
    parser.add_argument("--allow-name", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        payload = json.loads(stdin.read())
    except ValueError:  # JSON hỏng hoặc byte không giải mã được
        return _deny(args.format, "blocked: " + BAD_INPUT, stdout, stderr)
    allow = DEFAULT_ALLOW_NAMES + tuple(args.allow_name)
    for path in extract_paths(payload):
        rule = match_rule(path, tuple(args.deny_glob), allow)
        if rule:
            return _deny(args.format, "blocked: {} ({})".format(path, rule), stdout, stderr)
    if args.format == "antigravity":
        stdout.write("{}\n")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
