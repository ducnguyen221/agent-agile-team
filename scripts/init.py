#!/usr/bin/env python3
"""Dựng `.agile.json`, ba sổ gốc và (tuỳ chọn) khung một sprint từ `templates/`.

Cách chạy:
    python scripts/init.py <gốc-dự-án>                    # chạy thử: in thao tác, không ghi gì
    python scripts/init.py <gốc-dự-án> --apply            # ghi thật; file có sẵn không bao giờ bị ghi đè
    python scripts/init.py <gốc-dự-án> --apply --sprint <slug> --title "<mục tiêu>"
        [--tiny] [--size S] [--risk normal|high] [--risk-tags a,b] [--request RQ-NNN] [--feature FS-NNN]
        [--date YYYY-MM-DD]

Sprint mới lấy mã từ `next_id` của SPRINTS, đặt lại trạng thái (`status: drafting` cho PROGRESS/SPRINT, cổng
và `verdict` về pending/null, `review_round: 0`, mọi vai về nhãn `pending`) rồi ghi một dòng Timeline vào
SPRINTS và tăng `next_id`. Chạy lại cùng `slug` không đổi gì.

Mã thoát: 0 = xong (hoặc chạy thử xong) · 2 = lỗi đầu vào.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c  # noqa: E402

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
LEDGERS = (("requests", "REQUESTS.md", "RQ", "request"), ("sprints", "SPRINTS.md", "SPR", "sprint"),
           ("specs", "SPECS.md", "FS", "feature"))
SPRINT_FILES = ("SPEC", "PLAN", "PROGRESS", "REPORT")
STATUS_NEW = {"spec": "draft", "plan": "draft", "progress": "drafting", "report": "draft", "sprint": "drafting"}
RESET = {"gate_1": "pending", "gate_1_at": "null", "gate_1_quote": "null", "verdict": "pending",
         "gate_2": "pending", "gate_2_at": "null", "gate_2_quote": "null", "review_round": "0"}


class InputError(Exception):
    pass


# --- Ghi YAML tập con ----------------------------------------------------------------------------------


def yaml_str(value: str) -> str:
    """Chuỗi trần nếu an toàn trong tập con, nếu không thì nháy kép."""
    plain = (value and value == value.strip() and value[0] not in "[\"'{>&*!%@|`#-" and ": " not in value
             and " #" not in value and not value.endswith(":") and value not in ("null", "true", "false")
             and not re.fullmatch(r"-?[0-9]+", value))
    if plain:
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def yaml_value(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, list):
        return "[" + ", ".join(yaml_value(v) for v in value) + "]"
    return yaml_str(str(value))


def set_keys(text: str, values: dict) -> str:
    """Thay giá trị các khoá gốc có sẵn trong frontmatter; giữ nguyên mọi dòng khác."""
    lines = text.split("\n")
    end = next(i for i in range(1, len(lines)) if lines[i].rstrip() == "---")
    for i in range(1, end):
        m = re.match(r"([a-z][a-z0-9_-]*):( |$)", lines[i])
        if m and m.group(1) in values:
            lines[i] = f"{m.group(1)}: {values[m.group(1)]}"
    return "\n".join(lines)


def reset_roles(text: str) -> str:
    """Mọi vai trong khối `roles` về `[tier, pending]` (bỏ ghi chú chỉ định của sprint mẫu)."""
    lines = text.split("\n")
    end = next(i for i in range(1, len(lines)) if lines[i].rstrip() == "---")
    in_roles = False
    for i in range(1, end):
        if not lines[i].startswith(" "):
            in_roles = lines[i].rstrip() == "roles:"
            continue
        m = re.match(r"  ([a-z][a-z0-9-]*): \[(T[123]),", lines[i])
        if in_roles and m:
            lines[i] = f"  {m.group(1)}: [{m.group(2)}, pending]"
    return "\n".join(lines)


# --- Kế hoạch thao tác -----------------------------------------------------------------------------------


class Plan:
    """Danh sách thao tác: (kiểu, đường dẫn, nội dung). Chạy thử chỉ in; `--apply` mới ghi."""

    def __init__(self):
        self.actions: list = []  # (kiểu, đường dẫn, nội dung, kiểu file)

    def create(self, path: Path, content: str) -> None:
        if path.exists():
            self.actions.append(("skip", path, None, None))
        else:
            self.actions.append(("create", path, content, None))

    def update(self, path: Path, content: str, style: c.TextStyle | None) -> None:
        self.actions.append(("update", path, content, style))

    def render(self, apply: bool) -> None:
        labels = {"create": "+ tạo", "update": "~ sửa", "skip": "= giữ (đã có)"}
        for kind, path, _, _ in self.actions:
            print(f"{labels[kind]} {c.display(path)}")
        if not apply:
            print("(chạy thử — không ghi gì; thêm --apply để ghi)")

    def apply(self) -> None:
        for kind, path, content, style in self.actions:
            if kind != "skip":
                c.write_text_style(path, content, style)


def template(rel: str) -> str:
    return c.read_text(c.TEMPLATES / rel)


def plan_project(root: Path, date: str, plan: Plan) -> dict:
    config_path = root / c.CONFIG_NAME
    if config_path.exists():
        try:
            cfg = c.load_config(root)
        except c.ConfigError as exc:
            raise InputError(str(exc)) from exc
        plan.create(config_path, "")  # đã có → in "= giữ", không ghi
    else:
        raw = template("project/agile.json")
        plan.create(config_path, raw)
        cfg = c.merge_config(json.loads(raw))
    problems = c.config_problems(cfg)
    if problems:
        raise InputError(f"{c.display(config_path)}: " + "; ".join(problems))
    for key, name, rec_prefix, width_key in LEDGERS:
        text = template(f"registry/{name}")
        first = c.format_id(rec_prefix, 1, cfg["id_width"][width_key])
        plan.create(target(root, cfg, cfg["paths"][key]), set_keys(text, {"next_id": first, "updated": date}))
    return cfg


def target(root: Path, cfg: dict, rel: str) -> Path:
    """Đích ghi đã resolve; ngoài gốc dự án và `artifact_root` → lỗi đầu vào."""
    try:
        return c.safe_path(root, cfg, rel)
    except c.ConfigError as exc:
        raise InputError(str(exc)) from exc


def _pending_content(plan: Plan, path: Path) -> tuple[str | None, c.TextStyle | None]:
    for kind, dest, content, style in reversed(plan.actions):
        if dest == path and kind != "skip":
            return content, style
    return c.read_text_style(path) if path.is_file() else (None, None)


def plan_sprint(root: Path, cfg: dict, args, plan: Plan) -> None:
    ledger_path = target(root, cfg, cfg["paths"]["sprints"])
    pattern = cfg["paths"]["sprint_dir"]
    base = c.artifact_path(root, cfg, "").resolve()
    exact = re.compile(re.escape(pattern).replace(re.escape("{date}"), "[0-9]{4}-[0-9]{2}-[0-9]{2}")
                       .replace(re.escape("{slug}"), re.escape(args.sprint)))
    existing = sorted(p for p in base.glob(pattern.replace("{date}", "*").replace("{slug}", "*"))
                      if p.is_dir() and exact.fullmatch(p.relative_to(base).as_posix()))
    if existing:
        for p in existing:
            plan.actions.append(("skip", p, None, None))
        return
    ledger, style = _pending_content(plan, ledger_path)
    try:
        fm = c.parse_frontmatter(ledger) if ledger is not None else None
    except c.SubsetError as exc:
        raise InputError(f"{c.display(ledger_path)}:{exc.line}: {exc.message}") from exc
    parsed = c.parse_id(fm.data.get("next_id")) if fm else None
    if not parsed or parsed[0] != "SPR":
        raise InputError(f"{c.display(ledger_path)}: thiếu next_id SPR-NN hợp lệ")
    width = cfg["id_width"]["sprint"]
    sprint_id = c.format_id("SPR", parsed[1], width)
    folder = target(root, cfg, pattern.format(date=args.date, slug=args.sprint))

    values = {
        "sprint": sprint_id, "request": yaml_value(args.request), "feature": yaml_value(args.feature),
        "title": yaml_str(args.title), "created": args.date, "updated": args.date,
        "size": args.size, "risk": args.risk, "risk_tags": yaml_value(args.risk_tags), **RESET,
    }
    for name in (("SPRINT",) if args.tiny else SPRINT_FILES):
        doc = name.lower()
        text = set_keys(template(f"sprint/{name}.md"), {**values, "id": f"{sprint_id}-{doc}", "status": STATUS_NEW[doc]})
        text = reset_roles(text).replace("# Tên mục tiêu sprint —", f"# {args.title} —", 1)
        plan.create(folder / f"{name}.md", text)

    rel = Path(os.path.relpath(folder, ledger_path.parent)).as_posix()
    title_cell = args.title.replace("|", "\\|")
    row = f"| {sprint_id} | {args.date} |  | {title_cell} |  | [{folder.name}]({rel}/) |"
    updated = set_keys(ledger, {"next_id": c.format_id("SPR", parsed[1] + 1, width), "updated": args.date})
    plan.update(ledger_path, insert_timeline_row(updated, row, ledger_path), style)


def insert_timeline_row(text: str, row: str, path: Path) -> str:
    """Chèn dòng ngay dưới hàng phân cách của bảng Timeline (mới nhất ở trên)."""
    lines = text.split("\n")
    try:
        head = next(i for i, line in enumerate(lines) if re.match(r"##\s+(?:[0-9.]+\s+)?Timeline", line))
        sep = next(i for i in range(head, len(lines)) if lines[i].startswith("|") and set(lines[i]) <= set("|-: "))
    except StopIteration as exc:
        raise InputError(f"{c.display(path)}: không thấy bảng dưới tiêu đề Timeline") from exc
    lines.insert(sep + 1, row)
    return "\n".join(lines)


# --- Dòng lệnh -----------------------------------------------------------------------------------------


def validate(args) -> None:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", args.date):
        raise InputError(f"--date {args.date!r} phải có dạng YYYY-MM-DD")
    if args.sprint is None:
        return
    if not SLUG.fullmatch(args.sprint):
        raise InputError(f"--sprint {args.sprint!r} phải là kebab-case chữ thường")
    if not args.title or not args.title.strip():
        raise InputError("--sprint cần --title (mục tiêu sprint)")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in args.title):
        raise InputError("--title không được chứa ký tự điều khiển (xuống dòng, tab…) — sẽ làm hỏng frontmatter và bảng")
    if args.tiny:
        if args.size not in (None, "tiny"):
            raise InputError("--tiny không đi cùng --size khác tiny")
        args.size = "tiny"
    args.size = args.size or "medium"
    args.risk_tags = [t.strip() for t in (args.risk_tags or "").split(",") if t.strip()]
    unknown = set(args.risk_tags) - {"secret", "auth", "external_input", "public_api", "infra", "data_migration", "rules"}
    if unknown:
        raise InputError(f"--risk-tags không biết: {', '.join(sorted(unknown))}")
    if args.risk_tags and args.risk != "high":
        raise InputError("--risk-tags khác rỗng buộc --risk high")
    if args.risk == "high" and args.size != "large":
        raise InputError("--risk high buộc --size large (rủi ro cao không bao giờ là việc nhỏ)")
    for value, rec_prefix, flag in ((args.request, "RQ", "--request"), (args.feature, "FS", "--feature")):
        if value is not None and (c.parse_id(value) or ("", 0))[0] != rec_prefix:
            raise InputError(f"{flag} {value!r} phải là {rec_prefix}-NNN")


def main(argv=None) -> int:
    c.utf8_stdio()
    parser = argparse.ArgumentParser(prog="init.py", description="Dựng sổ gốc và khung sprint từ mẫu.")
    parser.add_argument("root", help="gốc dự án")
    parser.add_argument("--apply", action="store_true", help="ghi thật (mặc định chỉ in thao tác)")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="ngày ghi vào file (YYYY-MM-DD)")
    parser.add_argument("--sprint", metavar="SLUG", help="tạo khung một sprint mới")
    parser.add_argument("--title", help="mục tiêu sprint")
    parser.add_argument("--tiny", action="store_true", help="việc rất nhỏ: một file SPRINT.md")
    parser.add_argument("--size", choices=["tiny", "small", "medium", "large"])
    parser.add_argument("--risk", choices=["normal", "high"], default="normal")
    parser.add_argument("--risk-tags", help="danh sách nhãn rủi ro, phân cách bằng dấu phẩy")
    parser.add_argument("--request", help="RQ-NNN của yêu cầu gốc")
    parser.add_argument("--feature", help="FS-NNN của tính năng")
    args = parser.parse_args(argv)
    root = Path(args.root)
    plan = Plan()
    try:
        validate(args)
        cfg = plan_project(root, args.date, plan)
        if args.sprint:
            plan_sprint(root, cfg, args, plan)
    except InputError as exc:
        print(f"lỗi đầu vào: {exc}")
        return 2
    plan.render(args.apply)
    if args.apply:
        plan.apply()
    return 0


if __name__ == "__main__":
    sys.exit(main())
