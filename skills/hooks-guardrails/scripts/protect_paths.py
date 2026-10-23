"""Hook chặn ghi vào đường bảo vệ — đọc JSON hook ở stdin, chỉ thư viện chuẩn, không mở file đích.

Gọi: python protect_paths.py --format {claude,codex,antigravity} [--deny-glob G ...] [--allow-name N ...]
Khớp: claude/codex in `blocked: <đường> (<luật>)` ở stderr rồi thoát 2; antigravity in JSON `deny` ở stdout, thoát 0.
Không khớp: claude/codex thoát 0, không in; antigravity in `{}`. Đóng khi lỗi: JSON hỏng hay MỌI ngoại lệ khác
(JSON lồng quá sâu, hết bộ nhớ…) đều chặn đúng định dạng của harness, không bao giờ thoát 1 kèm traceback.
Khoá đường đọc từ payload: file_path, path, notebook_path (Claude Code), TargetFile (Antigravity); dòng vá của Codex.
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
PATH_KEYS = ("file_path", "path", "notebook_path", "TargetFile")
PATCH_PREFIXES = ("*** Add File: ", "*** Update File: ", "*** Delete File: ", "*** Move to: ")
FORMATS = ("claude", "codex", "antigravity")
BAD_INPUT = "bad hook input"
MAX_GLOB_SEGMENTS = 1024  # đường sâu hơn không có thật; với --deny-glob thì chặn thay vì so từng đoạn đuôi (bậc hai)


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
    seen: set[str] = set()
    for item in raw:
        path = _norm(item)
        if path and path not in seen:
            seen.add(path)
            paths.append(path)
    return paths


def _fits(text: str, pattern: str) -> bool:
    # So không phân biệt hoa thường: Windows và macOS mặc định coi `.ENV` là `.env`.
    return fnmatch.fnmatchcase(text.casefold(), pattern.casefold())


def _win_name(part: str) -> str:
    """Tên như Win32 ghi ra đĩa: bỏ hậu tố luồng `:…` (`.env::$DATA`) rồi dấu cách và dấu chấm cuối."""
    return part.split(":", 1)[0].rstrip(" .")


def _variants(part: str) -> tuple[str, ...]:
    """Tên nguyên văn và tên đã chuẩn hoá theo Win32 (cả hai, vì trên POSIX dấu `:` là ký tự thường)."""
    win = _win_name(part)
    return (part,) if win == part else (part, win)


def match_rule(path: str, deny_globs: tuple[str, ...] = (),
               allow_names: tuple[str, ...] = DEFAULT_ALLOW_NAMES) -> str | None:
    """Tên luật chặn đường này (`name:<mẫu>`, `segment:<tên>`, `glob:<mẫu>`) hoặc None.

    Chỉ so chuỗi, không chạm hệ thống file. Tên trong `allow_names` bỏ qua luật tên, không bỏ qua luật đoạn đường và glob.
    Có `deny_globs` mà đường quá 1024 đoạn thì chặn (`limit:`), để việc so đuôi không thành bậc hai.
    Tên và đoạn đường được so cả ở dạng nguyên văn lẫn dạng Win32 (bỏ dấu cách/dấu chấm cuối, bỏ luồng `::$DATA`)."""
    path = _norm(path)
    parts = [p for p in path.split("/") if p and p != "."]
    name = parts[-1] if parts else ""
    names = _variants(name) if name else ()
    if names and not any(_fits(n, a) for n in names for a in allow_names):
        for pattern in DEFAULT_DENY_NAMES:
            if any(_fits(n, pattern) for n in names):
                return "name:" + pattern
    for segment in DEFAULT_DENY_SEGMENTS:
        if any(_fits(v, segment) for part in parts for v in _variants(part)):
            return "segment:" + segment
    if deny_globs:
        if len(parts) > MAX_GLOB_SEGMENTS:
            return "limit:segments>{}".format(MAX_GLOB_SEGMENTS)
        # glob so với cả đường và từng đoạn đuôi (dựng lười), để mẫu tương đối khớp đường tuyệt đối
        for pattern in deny_globs:
            glob = _norm(pattern)
            if _fits(path, glob) or any(_fits("/".join(parts[i:]), glob) for i in range(len(parts))):
                return "glob:" + pattern
    return None


def _deny(fmt: str, reason: str, stdout: TextIO, stderr: TextIO) -> int:
    if fmt == "antigravity":
        stdout.write(json.dumps({"decision": "deny", "reason": reason}) + "\n")
        return 0
    stderr.write(reason + "\n")
    return 2


def _check(args: argparse.Namespace, stdin: TextIO, stdout: TextIO, stderr: TextIO) -> int:
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


def main(argv: list[str] | None = None, stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout,
         stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description="Chặn hook ghi vào đường bảo vệ.")
    parser.add_argument("--format", required=True, choices=FORMATS)
    parser.add_argument("--deny-glob", action="append", default=[])
    parser.add_argument("--allow-name", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        return _check(args, stdin, stdout, stderr)
    except Exception as exc:  # RecursionError, MemoryError, lỗi ghi stdout…: đóng khi lỗi, không thoát 1
        return _deny(args.format, "blocked: {} ({})".format(BAD_INPUT, type(exc).__name__), stdout, stderr)


def _last_resort(argv: list[str]) -> int:
    """Lưới cuối khi chính `main` văng (kể cả lúc từ chối): vẫn ra định dạng chặn của harness."""
    fmt = "antigravity" if "antigravity" in argv else "claude"
    try:
        return _deny(fmt, "blocked: " + BAD_INPUT, sys.stdout, sys.stderr)
    except BaseException:  # noqa: BLE001 — stream hỏng: chỉ còn mã thoát
        return 0 if fmt == "antigravity" else 2


if __name__ == "__main__":
    try:
        for stream in (sys.stdin, sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
        code = main()
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        code = _last_resort(sys.argv)
    sys.exit(code)
