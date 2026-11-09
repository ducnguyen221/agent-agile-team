#!/usr/bin/env python3
"""So sàn cứng của đầu nhánh (head) với bản base (SPR-16 FR2): vùng văn bản giữa mốc `san-cung`, vị trí mốc, và các
file thuộc `FLOOR_FILES`.

Cách chạy (từ gốc repo cần kiểm):
    python -X utf8 scripts/floor_check.py --base <ref> [--head <ref>] [--mode strict|report] [--json] [--root <repo>]

Bước CI chạy **bản của base** (giải `git archive <base> scripts` ra thư mục tạm) với cây của head làm dữ liệu, nên
danh sách sàn và hàm đọc mốc ở đây là của base, không phải của head.

Mã thoát: 0 = không chạm sàn, hoặc `bootstrap`, hoặc `--mode report`; 1 = có vi phạm ở `--mode strict`;
2 = lỗi dùng/git (ref không có, không phải repo git). Mỗi vi phạm một dòng `<mã> <đường>[:dòng] — <lý do>` với mã
`floor-zone-changed`, `floor-marker-moved`, `floor-file-added|removed|renamed|changed`.
`--mode report` (chỉ cho PR cổng người có nhãn `floor-approved` do Đức gắn) liệt kê mọi thay đổi sàn là
`floor-changed — cần Đức xác nhận ở Cổng 2` và thoát 0: phát hiện chạm sàn và việc người duyệt cho phép là hai việc tách bạch.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _autopilot_rules import FLOOR_FILES, FLOOR_MARKER_END, FLOOR_MARKER_START, FLOOR_ZONES, zone_spans  # noqa: E402

BOOTSTRAP = "bootstrap — chưa kiểm so base"


@dataclass
class Violation:
    code: str
    path: str
    reason: str
    line: int = 0

    def render(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"{self.code} {where} — {self.reason}"


class GitError(Exception):
    pass


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        raise GitError(f"không chạy được git: {error}")


def verify_ref(root: Path, ref: str) -> str:
    done = git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    if done.returncode != 0:
        raise GitError(f"ref không có hoặc không phải commit: {ref}")
    return done.stdout.decode("utf-8", "replace").strip()


def show(root: Path, ref: str, path: str) -> bytes | None:
    done = git(root, "show", f"{ref}:{path}")
    return done.stdout if done.returncode == 0 else None


def decode(data: bytes | None) -> str | None:
    return None if data is None else data.decode("utf-8", "replace").replace("\r\n", "\n")


def zone_parts(text: str, spans: list[tuple[int, int]]) -> tuple[list[list[str]], list[str]]:
    """(thân từng vùng, toàn bộ chữ bỏ dòng mốc)."""
    lines = text.split("\n")
    inner = [lines[a:b - 1] for a, b in spans]  # a, b là số dòng 1-based của mốc mở/đóng
    plain = [line for line in lines if line.strip() not in (FLOOR_MARKER_START, FLOOR_MARKER_END)]
    return inner, plain


def check_zones(root: Path, base: str, head: str) -> tuple[list[Violation], bool]:
    """(vi phạm vùng, base có ít nhất một vùng)."""
    found: list[Violation] = []
    base_has_zone = False
    for path in FLOOR_ZONES:
        base_text = decode(show(root, base, path))
        base_spans = zone_spans(base_text) if base_text is not None else []
        if isinstance(base_spans, str) or not base_spans:
            continue  # base không có vùng ở file này: không có gì để so
        base_has_zone = True
        head_text = decode(show(root, head, path))
        if head_text is None:
            found.append(Violation("floor-zone-changed", path, "file có vùng sàn ở base nhưng không còn ở head"))
            continue
        head_spans = zone_spans(head_text)
        if isinstance(head_spans, str):
            found.append(Violation("floor-marker-moved", path, f"cặp mốc san-cung ở head lỗi ({head_spans})"))
            continue
        if len(head_spans) != len(base_spans):
            found.append(Violation("floor-marker-moved", path,
                                   f"số cặp mốc san-cung đổi: base {len(base_spans)}, head {len(head_spans)}"))
            continue
        base_inner, base_plain = zone_parts(base_text, base_spans)
        head_inner, head_plain = zone_parts(head_text, head_spans)
        for index, (before, after) in enumerate(zip(base_inner, head_inner)):
            if before == after:
                continue
            start = head_spans[index][0]
            if base_plain == head_plain:
                found.append(Violation("floor-marker-moved", path,
                                       f"mốc của vùng {index + 1} bị dời so với chữ quanh nó", start))
            else:
                found.append(Violation("floor-zone-changed", path, f"chữ giữa mốc của vùng {index + 1} khác base", start))
    return found, base_has_zone


def check_files(root: Path, base: str, head: str) -> list[Violation]:
    done = git(root, "diff", "--name-status", "-M", "--no-color", base, head)
    if done.returncode != 0:
        raise GitError("git diff lỗi: " + done.stderr.decode("utf-8", "replace").strip())
    floor = set(FLOOR_FILES)
    found: list[Violation] = []
    for raw in done.stdout.decode("utf-8", "replace").splitlines():
        parts = raw.split("\t")
        status, paths = parts[0], parts[1:]
        if status.startswith("R"):
            old, new = paths[0], paths[1]
            if old in floor:
                found.append(Violation("floor-file-renamed", old, f"đổi tên thành {new}"))
            elif new in floor:
                found.append(Violation("floor-file-added", new, "file sàn được thêm (đổi tên từ " + old + ")"))
        elif status.startswith("A") and paths[0] in floor:
            found.append(Violation("floor-file-added", paths[0], "file thuộc sàn cứng được thêm"))
        elif status.startswith("D") and paths[0] in floor:
            found.append(Violation("floor-file-removed", paths[0], "file thuộc sàn cứng bị xoá"))
        elif status[0] in "MT" and paths[0] in floor:
            found.append(Violation("floor-file-changed", paths[0], "nội dung file thuộc sàn cứng khác base"))
    return found


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="floor_check.py", description="So sàn cứng của head với bản base.")
    parser.add_argument("--base", required=True, help="ref của base")
    parser.add_argument("--head", default="HEAD", help="ref của head (mặc định HEAD)")
    parser.add_argument("--mode", choices=("strict", "report"), default="strict")
    parser.add_argument("--json", dest="as_json", action="store_true")
    parser.add_argument("--root", default=".", help="gốc repo git cần kiểm (mặc định: thư mục hiện tại)")
    args = parser.parse_args(argv)
    root = Path(args.root)
    try:
        verify_ref(root, args.base)
        verify_ref(root, args.head)
        if git(root, "cat-file", "-e", f"{args.base}:scripts/floor_check.py").returncode != 0:
            return emit(args, "bootstrap", [], BOOTSTRAP)
        violations, base_has_zone = check_zones(root, args.base, args.head)
        if not base_has_zone:
            return emit(args, "bootstrap", [], BOOTSTRAP)
        violations += check_files(root, args.base, args.head)
    except GitError as error:
        print(f"floor_check: {error}", file=sys.stderr)
        return 2
    return emit(args, "violations" if violations else "ok", violations, "")


def emit(args, status: str, violations: list[Violation], note: str) -> int:
    if args.as_json:
        print(json.dumps({"status": status, "mode": args.mode, "note": note,
                          "violations": [{"code": v.code, "path": v.path, "line": v.line, "reason": v.reason}
                                         for v in violations]}, ensure_ascii=False, indent=2))
    elif status == "bootstrap":
        print(note)
    elif violations:
        if args.mode == "report":
            print(f"floor-changed — cần Đức xác nhận ở Cổng 2 ({len(violations)} thay đổi sàn)")
        for violation in violations:
            print(violation.render())
    else:
        print("floor_check: không chạm sàn cứng")
    if status == "violations" and args.mode == "strict":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
