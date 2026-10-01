#!/usr/bin/env python3
"""Sinh lại khối "Đang mở" ở đầu ba sổ gốc (REQUESTS · SPECS · SPRINTS).

Cách chạy:
    python scripts/index.py <gốc-dự-án>            # ghi lại khối giữa hai dấu mốc khi nội dung đổi
    python scripts/index.py <gốc-dự-án> --check    # không ghi; thoát 1 nếu có sổ chưa cập nhật

Nguồn (hợp đồng `templates/README.md` mục 6):
- REQUESTS: dòng Timeline có trạng thái `mới` hoặc `đang làm`.
- SPECS: frontmatter spec sống trong `paths.feature_specs_dir` có `status` `proposed` hoặc `in_progress`.
- SPRINTS: frontmatter `PROGRESS.md` (hoặc `SPRINT.md`) của từng thư mục sprint, `status` khác `done`/`dropped`.
Sắp theo mã giảm dần (mới nhất ở trên). Cùng đầu vào cho cùng đầu ra, từng byte.

Mã thoát: 0 = xong / đã cập nhật · 1 = `--check` thấy sổ cũ · 2 = lỗi đầu vào.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c  # noqa: E402

START = "<!-- agile:open:start -->"
END = "<!-- agile:open:end -->"
NOTICE = "<!-- Khối này do công cụ `index` ghi lại — đừng sửa tay. -->"
EMPTY = {"requests": "Không có yêu cầu nào đang mở.", "specs": "Không có tính năng nào đang mở.",
         "sprints": "Không có sprint nào đang mở."}
OPEN_REQUEST = {"mới", "đang làm"}
FEATURE_LABEL = {"proposed": "đề xuất", "in_progress": "đang làm"}
SPRINT_LABEL = {"drafting": "đang viết SPEC/PLAN", "awaiting_gate_1": "chờ Cổng 1", "in_progress": "đang làm",
                "verifying": "đang kiểm định", "blocked": "vướng", "awaiting_gate_2": "chờ Cổng 2"}


class InputError(Exception):
    pass


def table_under(text: str, heading: str) -> list[dict]:
    """Các dòng dữ liệu của bảng đầu tiên dưới tiêu đề cấp 2 chứa `heading`, dạng {cột: ô}."""
    lines = c.mask_markdown(text.split("\n"))
    raw = text.split("\n")
    start = next((i for i, line in enumerate(lines) if line.startswith("## ") and heading in line), None)
    if start is None:
        return []
    header = None
    rows = []
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            break
        cells = c.table_cells(raw[i]) if lines[i].strip() else None
        if cells is None:
            if header is not None and rows:
                break
            continue
        if header is None:
            header = cells
        elif not c.is_separator_row(cells):
            rows.append(dict(zip(header, cells)))
    return rows


def _id_key(record: str) -> int:
    parsed = c.parse_id(record)
    return parsed[1] if parsed else -1


def _frontmatter(path: Path) -> dict:
    try:
        fm = c.parse_frontmatter(c.read_text(path))
    except c.SubsetError as exc:
        raise InputError(f"{c.display(path)}:{exc.line}: {exc.message}") from exc
    return fm.data if fm else {}


def _table(header: list, rows: list) -> list:
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(r) + " |" for r in rows]


def _link(target: Path, ledger: Path, folder: bool = False) -> str:
    rel = Path(os.path.relpath(target.resolve(), ledger.parent.resolve())).as_posix()
    return f"[{target.name}]({rel}{'/' if folder else ''})"


def requests_block(ledger: Path) -> list:
    rows = [r for r in table_under(c.read_text(ledger), "Timeline") if r.get("Trạng thái") in OPEN_REQUEST and c.parse_id(r.get("Mã"))]
    rows.sort(key=lambda r: _id_key(r["Mã"]), reverse=True)
    cols = ("Mã", "Ngày", "Tóm tắt", "Trạng thái", "Sprint")
    return _table(list(cols), [[r.get(col, "") for col in cols] for r in rows]) if rows else [EMPTY["requests"]]


def specs_block(ledger: Path, feature_dir: Path) -> list:
    names = {r.get("Mã"): r.get("Tính năng", "") for r in table_under(c.read_text(ledger), "Danh mục")}
    rows = []
    for path in sorted(feature_dir.glob("*.md")) if feature_dir.is_dir() else []:
        if path.resolve() == ledger.resolve():
            continue
        data = _frontmatter(path)
        if data.get("doc") != "feature" or data.get("status") not in FEATURE_LABEL:
            continue
        fid = str(data.get("id"))
        rows.append([fid, names.get(fid) or str(data.get("title", "")), FEATURE_LABEL[data["status"]], _link(path, ledger)])
    rows.sort(key=lambda r: _id_key(r[0]), reverse=True)
    return _table(["Mã", "Tính năng", "Trạng thái", "Spec sống"], rows) if rows else [EMPTY["specs"]]


def sprints_block(ledger: Path, base: Path, pattern: str) -> list:
    timeline = {r.get("Mã"): r for r in table_under(c.read_text(ledger), "Timeline")}
    rows = []
    for folder in sorted(p for p in base.glob(pattern.replace("{date}", "*").replace("{slug}", "*")) if p.is_dir()):
        state = next((folder / n for n in ("PROGRESS.md", "SPRINT.md") if (folder / n).is_file()), None)
        if state is None:
            continue
        data = _frontmatter(state)
        sid = data.get("sprint")
        if data.get("status") not in SPRINT_LABEL or not c.parse_id(sid):
            continue
        row = timeline.get(sid, {})
        rows.append([sid, row.get("Mở") or str(data.get("created", "")), row.get("Mục tiêu") or str(data.get("title", "")),
                     SPRINT_LABEL[data["status"]], str(data.get("review_round", 0)), _link(folder, ledger, folder=True)])
    rows.sort(key=lambda r: _id_key(r[0]), reverse=True)
    return _table(["Mã", "Mở", "Mục tiêu", "Trạng thái", "Vòng", "Thư mục"], rows) if rows else [EMPTY["sprints"]]


def rewrite(text: str, block: list, path: Path) -> str:
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if line.strip() == START]
    ends = [i for i, line in enumerate(lines) if line.strip() == END]
    if len(starts) != 1 or len(ends) != 1 or starts[0] > ends[0]:
        raise InputError(f"{c.display(path)}: cần đúng một cặp dấu mốc {START} … {END}")
    return "\n".join(lines[:starts[0] + 1] + [NOTICE] + block + lines[ends[0]:])


def build(root: Path) -> list:
    """Trả [(đường dẫn sổ, nội dung cũ, nội dung mới, kiểu file gốc)]."""
    try:
        cfg = c.load_config(root)
        problems = c.config_problems(cfg)
        if problems:
            raise c.ConfigError(f"{c.display(root / c.CONFIG_NAME)}: " + "; ".join(problems))
        paths = cfg["paths"]
        ledgers = {key: c.safe_path(root, cfg, paths[key]) for key in ("requests", "specs", "sprints")}
    except c.ConfigError as exc:
        raise InputError(str(exc)) from exc
    for key, path in ledgers.items():
        if not path.is_file():
            raise InputError(f"{c.display(path)}: không có sổ {key.upper()} (chạy init.py --apply)")
    blocks = {
        "requests": requests_block(ledgers["requests"]),
        "specs": specs_block(ledgers["specs"], c.artifact_path(root, cfg, paths["feature_specs_dir"])),
        "sprints": sprints_block(ledgers["sprints"], c.artifact_path(root, cfg, ""), paths["sprint_dir"]),
    }
    out = []
    for key, path in ledgers.items():
        old, style = c.read_text_style(path)
        out.append((path, old, rewrite(old, blocks[key], path), style))
    return out


def main(argv=None) -> int:
    c.utf8_stdio()
    parser = argparse.ArgumentParser(prog="index.py", description="Sinh lại khối 'Đang mở' của ba sổ gốc.")
    parser.add_argument("root", help="gốc dự án (chứa .agile.json)")
    parser.add_argument("--check", action="store_true", help="không ghi; thoát 1 nếu có sổ chưa cập nhật")
    args = parser.parse_args(argv)
    try:
        results = build(Path(args.root))
    except InputError as exc:
        print(f"lỗi đầu vào: {exc}")
        return 2
    stale = False
    for path, old, new, style in results:
        if old == new:
            print(f"= không đổi {c.display(path)}")
            continue
        stale = True
        if args.check:
            print(f"! chưa cập nhật {c.display(path)}")
        else:
            c.write_text_style(path, new, style)  # giữ BOM và kiểu xuống dòng của file gốc
            print(f"~ đã ghi {c.display(path)}")
    return 1 if (args.check and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
