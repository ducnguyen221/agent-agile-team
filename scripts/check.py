#!/usr/bin/env python3
"""Kiểm chuẩn tài liệu sprint, sổ gốc, spec sống và cấu hình dự án; `--self` kiểm lõi sạch của repo.

Cách chạy:
    python scripts/check.py <đường-dẫn> [<đường-dẫn> ...]   # file .md, .agile.json hoặc thư mục (quét đệ quy)
    python scripts/check.py --self [--root <repo>]          # lõi sạch, một thang mức, ngân sách AGENTS.md

Mã thoát: 0 = Đạt (không có Chặn/Phải sửa) · 1 = Không đạt · 2 = lỗi đầu vào (đường dẫn không có, file
không đọc được, frontmatter ngoài tập con YAML, `.agile.json` hỏng).

Biến môi trường: `AGENT_AGILE_DENYLIST` — đường tới danh sách từ cấm ngoài repo (chỉ `--self` dùng).
Hợp đồng luật: `templates/README.md`; mô tả từng luật: `scripts/README.md`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as c  # noqa: E402

CHAN, PHAI, NEN, GHI = "Chặn", "Phải sửa", "Nên sửa", "Ghi chú"
BLOCKING = {CHAN, PHAI}

RULES: dict[str, tuple[str, str]] = {
    "frontmatter-syntax": (CHAN, "frontmatter ngoài tập con YAML (lỗi đầu vào → thoát 2)"),
    "frontmatter-missing": (PHAI, "file tài liệu (tên chuẩn) không có frontmatter"),
    "frontmatter-key-missing": (PHAI, "thiếu khoá bắt buộc theo loại tài liệu"),
    "frontmatter-key-unknown": (GHI, "khoá ngoài bảng khoá của hợp đồng"),
    "frontmatter-value": (PHAI, "giá trị khoá sai miền hoặc mâu thuẫn"),
    "doc-unknown": (GHI, "khoá `doc` có nhưng không thuộc loại đã biết — chỉ áp luật chung"),
    "heading-missing": (PHAI, "thiếu tiêu đề cấp 2 bắt buộc"),
    "conclusion-missing": (PHAI, "thiếu khối `> **Kết luận:**` trước tiêu đề cấp 2 đầu tiên"),
    "id-bare-single-letter": (PHAI, "mã một chữ cái + số ngoài dấu code (trừ T1/T2/T3)"),
    "id-unknown-prefix": (PHAI, "định nghĩa mục bằng tiền tố hai chữ cái ngoài bảng mã"),
    "id-wrong-doc": (PHAI, "định nghĩa mục bằng tiền tố thuộc tài liệu khác"),
    "id-list-lead": (GHI, "bảng có cột đầu `Mã` mà dòng ngay trên không có câu dẫn in đậm (tài liệu + nghĩa của mã)"),
    "xref-missing": (PHAI, "nhắc tới mã không được định nghĩa ở tài liệu sở hữu"),
    "xref-unresolved": (GHI, "không tìm được tài liệu sở hữu qua `links` để đối chiếu mã"),
    "task-without-trace": (PHAI, "việc `TK` không trỏ `FR`/`SC` nào (việc con kế thừa việc cha)"),
    "report-sc-without-vr": (PHAI, "`SC` của SPEC không có `VR` nào trong REPORT"),
    "report-fr-without-vr": (PHAI, "`FR` của SPEC không có `VR` nào trỏ tới nó hoặc kịch bản con (trừ `bỏ`/NOT_APPLICABLE)"),
    "self-review": (CHAN, "một nhãn agent vừa giữ vai thực thi vừa giữ vai kiểm định"),
    "qa-not-independent": (PHAI, "QA trùng nhãn với implementer/architect mà không khai tự kiểm, hoặc khai tự kiểm mà verdict là pass"),
    "roles-invalid": (PHAI, "`roles` sai hình: vai lạ, tier ngoài T1–T3, thiếu nhãn agent"),
    "gate-invalid": (PHAI, "cổng đã kết luận mà thiếu thời điểm/câu nguyên văn, hoặc trạng thái vượt cổng"),
    "old-scale-label": (PHAI, "nhãn thang mức cũ ngoài bảng quy đổi `method/severity.md`"),
    "config-syntax": (CHAN, "`.agile.json` không phải JSON hợp lệ (lỗi đầu vào → thoát 2)"),
    "config-invalid": (PHAI, "`.agile.json` sai hình hoặc đổi ngưỡng coverage không ghi lý do"),
    "config-public-root": (CHAN, "`visibility: public` mà `artifact_root` nằm trong gốc dự án"),
    "leak-denylist": (CHAN, "`--self`: file của repo chứa từ trong danh sách cấm"),
    "agents-md-budget": (PHAI, "`--self`: `AGENTS.md` quá 120 dòng hoặc quá 10 KB"),
}
INPUT_RULES = {"frontmatter-syntax", "config-syntax"}

SPRINT_DOCS = ("spec", "plan", "progress", "report", "sprint")
REGISTRY_DOCS = ("requests", "specs", "sprints")
DOC_KINDS = SPRINT_DOCS + ("feature",) + REGISTRY_DOCS
KNOWN_NAMES = {
    "SPEC.md": "spec", "PLAN.md": "plan", "PROGRESS.md": "progress", "REPORT.md": "report",
    "SPRINT.md": "sprint", "REQUESTS.md": "requests", "SPECS.md": "specs", "SPRINTS.md": "sprints",
}

_SPRINT_KEYS = ("id", "doc", "title", "sprint", "request", "feature", "status", "size", "risk", "roles", "created", "updated")
_GATE1 = ("gate_1", "gate_1_at", "gate_1_quote")
_GATE2 = ("verdict", "gate_2", "gate_2_at", "gate_2_quote")
REQUIRED_KEYS = {
    "spec": _SPRINT_KEYS + ("links",) + _GATE1,
    "plan": _SPRINT_KEYS + ("links",) + _GATE1,
    "progress": _SPRINT_KEYS + ("links", "review_round"),
    "report": _SPRINT_KEYS + ("links", "review_round") + _GATE2,
    "sprint": _SPRINT_KEYS + ("review_round",) + _GATE1 + _GATE2,
    "feature": ("id", "doc", "title", "status", "requests", "sprints", "created", "updated"),
    "requests": ("id", "doc", "title", "next_id", "updated"),
    "specs": ("id", "doc", "title", "next_id", "updated"),
    "sprints": ("id", "doc", "title", "next_id", "updated"),
}
KNOWN_KEYS = set(_SPRINT_KEYS) | set(_GATE1) | set(_GATE2) | {
    "risk_tags", "review_round", "requests", "sprints", "next_id", "links"}

STATUS = {
    "spec": {"draft", "in_review", "approved", "superseded"},
    "plan": {"draft", "in_review", "approved", "superseded"},
    "progress": {"drafting", "awaiting_gate_1", "in_progress", "verifying", "blocked", "awaiting_gate_2", "done", "dropped"},
    "sprint": {"drafting", "awaiting_gate_1", "in_progress", "verifying", "blocked", "awaiting_gate_2", "done", "dropped"},
    "report": {"draft", "submitted", "accepted"},
    "feature": {"proposed", "in_progress", "live", "deprecated", "dropped"},
}
SIZES = {"tiny", "small", "medium", "large"}
RISKS = {"normal", "high"}
RISK_TAGS = {"secret", "auth", "external_input", "public_api", "infra", "data_migration", "rules"}
GATE1_VALUES = {"pending", "approved", "changes_requested"}
VERDICT_VALUES = {"pending", "pass", "conditional_pass", "fail"}
EXECUTORS = {"analyst", "architect", "implementer", "qa"}
VERIFIERS = {"business-reviewer", "tech-reviewer"}
NEXT_ID_PREFIX = {"requests": "RQ", "specs": "FS", "sprints": "SPR"}
WIDTH_KEY = {"RQ": "request", "FS": "feature", "SPR": "sprint"}

REQUIRED_HEADINGS = {
    "spec": ("Bối cảnh", "Câu chuyện người dùng", "Yêu cầu chức năng", "Tiêu chí thành công", "Ngoài phạm vi", "Câu hỏi cần làm rõ"),
    "plan": ("Mục tiêu", "Kiến trúc", "Ràng buộc chung", "Trọng tâm review", "Việc", "Rủi ro", "Quyết định cần người", "Ước lượng"),
    "progress": ("Bảng trạng thái việc", "Nhật ký", "Vướng mắc", "Vòng kiểm định hiện tại"),
    "report": ("Tóm tắt cho người không chuyên", "Kết quả kiểm định", "Phát hiện của reviewer", "Rủi ro còn lại",
               "Cách dùng, đã đổi gì, cách hoàn tác", "Bài học", "Việc để lại", "Review & Retro", "Cổng 2"),
    "sprint": ("SPEC", "PLAN", "PROGRESS", "REPORT"),
    "feature": ("Hành vi hiện hành", "Tiêu chí đang giữ", "Giới hạn đã biết", "Quyết định liên quan", "Lịch sử sprint"),
    "requests": ("Đang mở", "Timeline"),
    "sprints": ("Đang mở", "Timeline"),
    "specs": ("Đang mở", "Danh mục"),
}

CODE = re.compile(r"(?<![\w/\-])([A-Z]{2})([0-9]+(?:\.[0-9]+)*)(?![\w\-])")
CODE_AT_START = re.compile(r"([A-Z]{2})([0-9]+(?:\.[0-9]+)*)(?![\w\-])")
BARE = re.compile(r"(?<![\w\-.])([A-Z])([0-9]+)(?![\w\-])")
RANGE = re.compile(r"(?<![\w/\-])([A-Z]{2})([0-9]+)\s*[–—-]\s*([A-Z]{2})([0-9]+)(?![\w\-]|\.[0-9])")
HEADING = re.compile(r"^(#{1,6})\s+(?:\*\*)?")
BOLD_ITEM = re.compile(r"^\s*(?:[-*+]|[0-9]+\.)\s+\*\*")
LINK_URL = re.compile(r"\]\([^)]*\)|<https?://[^>]*>|https?://\S+")
DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
CONCLUSION = re.compile(r"^>\s*\*\*Kết luận:\*\*")
NUMBERING = re.compile(r"^[0-9]+(?:\.[0-9]+)*\.?\s+")
# Nhãn của mười thang cũ trong bảng quy đổi `method/severity.md` mục 4 (chỉ nhãn mức, không nhãn kết luận).
OLD_CELL = {"critical", "high", "medium", "low", "important", "minor", "warning", "nit", "nit:"}
OLD_CELL_UPPER = {"BLOCK", "WARN", "INFO", "NOTE", "Block"}
OLD_FIELD = re.compile(r"(?i)\b(?:severity|mức)\s*:\s*\**\s*(critical|high|medium|low|important|minor)\b")
SELF_CHECK = "tự kiểm, chưa độc lập"
NOT_APPLICABLE = "NOT_APPLICABLE"
# NOT_APPLICABLE chỉ miễn khi có lý do theo sau (một chữ sau dấu nối tuỳ chọn).
NA_WITH_REASON = re.compile(r"NOT_APPLICABLE[ ]*[—–:(-]?[ ]*[*_'\"`]*[A-Za-zÀ-ỹ0-9]")
DROPPED = re.compile(r"[(—–:-]\s*bỏ\s*(?:\)|$)")  # trạng thái `bỏ` của mục: "(bỏ)" hoặc "— bỏ" cuối dòng
AGENTS_MAX_LINES = 120
AGENTS_MAX_BYTES = 10 * 1024
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".tmp"}
OPEN_START, OPEN_END = "<!-- agile:open:start -->", "<!-- agile:open:end -->"  # khối do `index` sinh
SPAN_HINT = (" — có dấu huyền kề bên: mã nằm trong code span lồng nhau hoặc ngắt dòng? Code span chứa dấu huyền"
             " thì bọc ngoài bằng hai dấu huyền")


@dataclass
class Finding:
    path: Path
    line: int
    rule: str
    message: str

    @property
    def level(self) -> str:
        return RULES[self.rule][0]

    def render(self) -> str:
        return f"{c.display(self.path)}:{self.line}: {self.level} [{self.rule}] {self.message}"


@dataclass
class Report:
    findings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    denylist_status: str = ""
    checked: int = 0  # số file Markdown đã chạy luật

    @property
    def exit_code(self) -> int:
        if self.errors or any(f.rule in INPUT_RULES for f in self.findings):
            return 2
        if any(f.level in BLOCKING for f in self.findings):
            return 1
        return 0


@dataclass
class Definition:
    code: str
    line: int
    position: str  # heading · table · item


@dataclass
class Doc:
    path: Path
    raw: list
    masked: list  # đã che mã và URL
    start: int  # số dòng của phần tử đầu tiên trong `raw`
    fm: c.Frontmatter | None = None
    kind: str | None = None
    defs: list = field(default_factory=list)
    load_findings: list = field(default_factory=list)

    def line_no(self, idx: int) -> int:
        return self.start + idx

    def hint(self, idx: int, pos: int, code: str) -> str:
        """Gợi ý khi mã bị bắt (ở cột `pos`) có dấu huyền sát bên, hoặc đếm thô thấy trước mã có số lẻ dấu huyền
        (code span lồng nhau hoặc ngắt dòng làm lộ phần giữa)."""
        raw = self.raw[idx]
        near = raw[pos - 1:pos] == "`" or raw[pos + len(code):pos + len(code) + 1] == "`"
        return SPAN_HINT if near or raw[:pos].count("`") % 2 == 1 else ""

    @property
    def data(self) -> dict:
        return self.fm.data if self.fm else {}

    def key_line(self, key: str) -> int:
        return self.fm.lines.get(key, 1) if self.fm else 1

    def defined(self) -> set:
        return {d.code for d in self.defs}


# --- Đọc và phân tích một file --------------------------------------------------------------------------


def _is_candidate(text: str, name: str) -> bool:
    """File được đọc frontmatter nghiêm theo tập con: tên chuẩn, hoặc khối đầu có khoá `doc`."""
    if name in KNOWN_NAMES:
        return True
    lines = c.normalize(text).split("\n")
    if not lines or lines[0].rstrip() != "---":
        return False
    for line in lines[1:]:
        if line.rstrip() == "---":
            return False
        if line.startswith("doc:"):
            return True
    return False


def load_doc(path: Path) -> Doc:
    text = c.read_text(path)
    start, raw = c.body_lines(text)
    masked = [LINK_URL.sub(lambda m: " " * len(m.group(0)), line) for line in c.mask_markdown(raw)]
    doc = Doc(path=path, raw=raw, masked=masked, start=start)
    if _is_candidate(text, path.name):
        try:
            doc.fm = c.parse_frontmatter(text)
        except c.SubsetError as exc:
            doc.load_findings.append(Finding(path, exc.line, "frontmatter-syntax", exc.message))
        if doc.fm is None and not doc.load_findings:
            doc.load_findings.append(Finding(path, 1, "frontmatter-missing", f"{path.name} là tài liệu chuẩn nhưng không có frontmatter"))
        kind = doc.data.get("doc")
        if kind in DOC_KINDS:
            doc.kind = kind
        elif doc.fm is not None and "doc" not in doc.data and path.name in KNOWN_NAMES:
            doc.load_findings.append(Finding(path, 1, "frontmatter-key-missing",
                                             f"{path.name} là tài liệu chuẩn nhưng frontmatter thiếu khoá 'doc' (doc: {KNOWN_NAMES[path.name]})"))
        elif doc.fm is not None and "doc" in doc.data:
            doc.load_findings.append(Finding(path, doc.key_line("doc"), "doc-unknown", f"doc: {kind!r} không thuộc {', '.join(DOC_KINDS)}"))
    doc.defs = _definitions(doc)
    return doc


def _definitions(doc: Doc) -> list:
    defs = []
    header_first: str | None = None
    prev_table = False
    for idx, line in enumerate(doc.masked):
        cells = c.table_cells(line)
        if cells is None:
            prev_table = False
        elif not prev_table:
            header_first = cells[0].strip("* ").casefold()
            prev_table = True
            continue
        else:
            if header_first == "mã" and not c.is_separator_row(cells):
                m = CODE_AT_START.match(cells[0].strip("* "))
                if m:
                    defs.append(Definition(m.group(1) + m.group(2), doc.line_no(idx), "table"))
            continue
        for pattern, position in ((HEADING, "heading"), (BOLD_ITEM, "item")):
            head = pattern.match(line)
            if head:
                m = CODE_AT_START.match(line[head.end():])
                if m:
                    defs.append(Definition(m.group(1) + m.group(2), doc.line_no(idx), position))
                break
    return defs


def codes_on(line: str) -> list:
    """Mã hai chữ cái trên một dòng đã che, gồm cả mã trong khoảng `SC1–SC3` đã khai triển."""
    return [code for code, _ in codes_at(line)]


def codes_at(line: str) -> list:
    """Như `codes_on` nhưng kèm cột bắt đầu của từng mã (mã khai triển từ khoảng lấy cột đầu khoảng)."""
    found = [(m.group(1) + m.group(2), m.start()) for m in CODE.finditer(line)]
    seen = {code for code, _ in found}
    for m in RANGE.finditer(line):
        # Gạch ASCII (`SC1-SC3`) làm CODE bỏ sót hai đầu khoảng: khai triển đủ từ đầu tới cuối.
        if m.group(1) == m.group(3):
            lo, hi = int(m.group(2)), int(m.group(4))
            codes = [f"{m.group(1)}{n}" for n in range(lo, hi + 1)]
        else:
            codes = [m.group(1) + m.group(2), m.group(3) + m.group(4)]
        for x in codes:
            if x not in seen:
                seen.add(x)
                found.append((x, m.start()))
    return found


def _is_level_header(cell: str) -> bool:
    name = cell.strip("*_ ").casefold()
    return name.startswith("mức") or "severity" in name or name == "level"


def prefix(code: str) -> str:
    return code[:2]


# --- Bộ máy kiểm ----------------------------------------------------------------------------------------


class Engine:
    def __init__(self):
        self.cache: dict = {}
        self.configs: dict = {}
        self.report = Report()

    def doc(self, path: Path) -> Doc | None:
        key = path.resolve()
        if key not in self.cache:
            try:
                self.cache[key] = load_doc(path)
            except (OSError, UnicodeDecodeError) as exc:
                self.cache[key] = None
                self.report.errors.append(f"{c.display(path)}: không đọc được ({exc})")
        return self.cache[key]

    def config_for(self, path: Path) -> dict:
        """Cấu hình của dự án chứa file (tìm `.agile.json` ngược lên); nhớ theo thư mục."""
        key = path.resolve().parent
        if key not in self.configs:
            self.configs[key] = c.find_config(key)
        return self.configs[key]

    def add(self, path: Path, line: int, rule: str, message: str) -> None:
        self.report.findings.append(Finding(path, line, rule, message))

    def check_file(self, path: Path) -> None:
        doc = self.doc(path)
        if doc is None:
            return
        self.report.checked += 1
        self.report.findings.extend(doc.load_findings)
        self.general_rules(doc)
        if doc.kind is None or doc.fm is None:
            return
        self.frontmatter_rules(doc)
        self.heading_rules(doc)
        self.id_rules(doc)
        self.lead_rule(doc)
        if doc.kind in ("plan", "sprint"):
            self.trace_rule(doc)
        if doc.kind in ("report", "sprint"):
            self.verification_rules(doc)

    # -- luật chung cho mọi file Markdown --

    def general_rules(self, doc: Doc) -> None:
        parts = doc.path.resolve().parts
        skill_tests = any(parts[i] == "skills" and parts[i + 2] == "tests" for i in range(len(parts) - 2))
        severity_table = len(parts) >= 2 and parts[-2:] == ("method", "severity.md")
        level_columns: list = []
        in_table = False
        for idx, line in enumerate(doc.masked):
            for m in BARE.finditer(line):
                if m.group(0) not in c.TIERS:
                    self.add(doc.path, doc.line_no(idx), "id-bare-single-letter",
                             f"mã trần '{m.group(0)}' — dùng tiền tố hai chữ cái đúng tài liệu hoặc viết bằng chữ" + doc.hint(idx, m.start(), m.group(0)))
            cells = c.table_cells(line)
            level_cells: list = []
            if cells is None:
                in_table, level_columns = False, []
            elif not in_table:  # hàng tiêu đề: nhớ cột mức/severity
                in_table = True
                level_columns = [i for i, cell in enumerate(cells) if _is_level_header(cell)]
            else:
                level_cells = [cells[i] for i in level_columns if i < len(cells)]
            if not severity_table:
                self._old_scale(doc, idx, line, level_cells)
        if not skill_tests:
            for d in doc.defs:
                if prefix(d.code) not in c.OWNER:
                    self.add(doc.path, d.line, "id-unknown-prefix", f"'{d.code}' dùng tiền tố '{prefix(d.code)}' ngoài bảng mã")

    def _old_scale(self, doc: Doc, idx: int, line: str, cells: list) -> None:
        """Nhãn thang cũ: chỉ ở ô thuộc cột mức/severity của bảng, hoặc sau "Mức:"/"Severity:" trong dòng."""
        for cell in cells:
            bare = cell.strip("*_ ")
            if bare.casefold() in OLD_CELL or bare in OLD_CELL_UPPER:
                self.add(doc.path, doc.line_no(idx), "old-scale-label",
                         f"nhãn thang cũ '{bare}' — dùng Chặn / Phải sửa / Nên sửa / Ghi chú")
                return
        m = OLD_FIELD.search(line)
        if m:
            self.add(doc.path, doc.line_no(idx), "old-scale-label",
                     f"nhãn thang cũ '{m.group(1)}' — dùng Chặn / Phải sửa / Nên sửa / Ghi chú")

    # -- frontmatter --

    def frontmatter_rules(self, doc: Doc) -> None:
        data, kind, path = doc.data, doc.kind, doc.path
        for key in REQUIRED_KEYS[kind]:
            if key not in data:
                self.add(path, 1, "frontmatter-key-missing", f"doc: {kind} thiếu khoá '{key}'")
        for key in data:
            if key not in KNOWN_KEYS:
                self.add(path, doc.key_line(key), "frontmatter-key-unknown", f"khoá '{key}' ngoài bảng khoá (templates/README.md mục 3)")

        def bad(key: str, message: str) -> None:
            self.add(path, doc.key_line(key), "frontmatter-value", message)

        def check_set(key: str, allowed: set) -> None:
            if key in data and data[key] not in allowed:
                bad(key, f"{key}: {data[key]!r} không thuộc {sorted(allowed)}")

        def check_ids(key: str, rec_prefix: str, *, allow_null: bool, allow_list: bool) -> None:
            if key not in data:
                return
            value = data[key]
            items = value if (allow_list and isinstance(value, list)) else [value]
            ok = all((v is None and allow_null and not isinstance(value, list)) or
                     (c.parse_id(v) or ("", 0))[0] == rec_prefix for v in items)
            if not ok:
                bad(key, f"{key}: {value!r} phải là mã {rec_prefix}-NNN" + (" hoặc danh sách" if allow_list else ""))
                return
            width = widths.get(WIDTH_KEY[rec_prefix])
            if not (isinstance(width, int) and not isinstance(width, bool) and width >= 1):
                width = c.DEFAULT_CONFIG["id_width"][WIDTH_KEY[rec_prefix]]  # cấu hình hỏng đã báo config-invalid
            for v in items:
                parsed = c.parse_id(v)
                if parsed and v != c.format_id(rec_prefix, parsed[1], width):
                    bad(key, f"{key}: {v!r} sai độ rộng id_width — phải là '{c.format_id(rec_prefix, parsed[1], width)}'")

        widths = self.config_for(path).get("id_width") or {}
        if kind in STATUS:
            check_set("status", STATUS[kind])
        for key in ("created", "updated"):
            if key in data and not (isinstance(data[key], str) and DATE.fullmatch(data[key])):
                bad(key, f"{key}: {data[key]!r} phải có dạng YYYY-MM-DD")
        if not isinstance(data.get("title", ""), str) or ("title" in data and not data["title"]):
            bad("title", "title phải là chuỗi khác rỗng")

        if kind in SPRINT_DOCS:
            check_set("size", SIZES)
            check_set("risk", RISKS)
            check_ids("sprint", "SPR", allow_null=True, allow_list=False)
            check_ids("request", "RQ", allow_null=True, allow_list=True)
            check_ids("feature", "FS", allow_null=True, allow_list=True)
            sprint = data.get("sprint")
            if isinstance(sprint, str) and c.parse_id(sprint) and data.get("id") != f"{sprint}-{kind}":
                bad("id", f"id: {data.get('id')!r} phải là '{sprint}-{kind}'")
            tags = data.get("risk_tags", [])
            if not isinstance(tags, list) or not set(tags) <= RISK_TAGS:
                bad("risk_tags", f"risk_tags: {tags!r} phải là danh sách con của {sorted(RISK_TAGS)}")
            elif tags and data.get("risk") != "high":
                bad("risk_tags", "risk_tags khác rỗng buộc risk: high")
            if data.get("risk") == "high" and data.get("size") != "large":
                bad("risk", "risk: high buộc size: large")
            self._roles(doc)
        if kind in ("spec", "plan", "sprint"):
            check_set("gate_1", GATE1_VALUES)
        if kind in ("report", "sprint"):
            check_set("verdict", VERDICT_VALUES)
            check_set("gate_2", VERDICT_VALUES)
        if "review_round" in data:
            value = data["review_round"]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                bad("review_round", f"review_round: {value!r} phải là số nguyên ≥ 0")
        if kind in ("spec", "plan", "progress", "report") and "links" in data:
            links = data["links"]
            if not isinstance(links, dict) or not all(isinstance(v, str) for v in links.values()):
                bad("links", "links phải là khối lồng: khoá → đường dẫn tương đối")
        if kind == "feature":
            if not (c.parse_id(data.get("id")) or ("", 0))[0] == "FS":
                bad("id", f"id: {data.get('id')!r} phải là FS-NNN")
            check_ids("requests", "RQ", allow_null=False, allow_list=True)
            check_ids("sprints", "SPR", allow_null=False, allow_list=True)
            for key in ("requests", "sprints"):
                if key in data and not isinstance(data[key], list):
                    bad(key, f"{key} phải là danh sách inline")
        if kind in REGISTRY_DOCS:
            if data.get("id") != kind.upper():
                bad("id", f"id: {data.get('id')!r} phải là '{kind.upper()}'")
            check_ids("next_id", NEXT_ID_PREFIX[kind], allow_null=False, allow_list=False)
        self._gates(doc)

    def _roles(self, doc: Doc) -> None:
        roles = doc.data.get("roles")
        if "roles" not in doc.data:
            return
        line = doc.key_line("roles")
        if not isinstance(roles, dict) or not roles:
            self.add(doc.path, line, "roles-invalid", "roles phải là khối lồng: vai → [tier, agent] hoặc [tier, agent, \"note\"]")
            return
        holders: dict = {}
        for role, value in roles.items():
            rline = doc.key_line(f"roles.{role}")
            if role not in EXECUTORS | VERIFIERS and not re.fullmatch(r"[a-z]+-specialist", role):
                self.add(doc.path, rline, "roles-invalid", f"vai '{role}' không có trong danh sách vai")
                continue
            if (not isinstance(value, list) or len(value) not in (2, 3) or value[0] not in c.TIERS
                    or not isinstance(value[1], str) or not value[1]
                    or (len(value) == 3 and not isinstance(value[2], str))):
                self.add(doc.path, rline, "roles-invalid", f"{role}: {value!r} phải là [T1|T2|T3, nhãn-agent] hoặc thêm \"note\"")
                continue
            holders.setdefault(value[1], set()).add(role)
        for agent, held in holders.items():
            if agent == "pending":
                continue
            executes = held & EXECUTORS
            verifies = {r for r in held if r in VERIFIERS or r.endswith("-specialist")}
            if executes and verifies:
                self.add(doc.path, line, "self-review",
                         f"agent '{agent}' vừa thực thi ({', '.join(sorted(executes))}) vừa kiểm định ({', '.join(sorted(verifies))})")

    def _gates(self, doc: Doc) -> None:
        data = doc.data
        for gate in ("gate_1", "gate_2"):
            if data.get(gate) not in (None, "pending") and gate in data:
                missing = [k for k in (f"{gate}_at", f"{gate}_quote") if not data.get(k)]
                if missing:
                    self.add(doc.path, doc.key_line(gate), "gate-invalid",
                             f"{gate}: {data[gate]} nhưng thiếu {', '.join(missing)} (thời điểm và câu nguyên văn)")
        status = data.get("status")
        if doc.kind in ("spec", "plan") and status == "approved" and data.get("gate_1") != "approved":
            self.add(doc.path, doc.key_line("status"), "gate-invalid", "status: approved nhưng gate_1 chưa approved")
        if doc.kind == "report" and status == "accepted" and data.get("gate_2") in (None, "pending"):
            self.add(doc.path, doc.key_line("status"), "gate-invalid", "status: accepted nhưng gate_2 chưa có kết luận")
        if doc.kind == "sprint" and status == "done" and data.get("gate_2") in (None, "pending"):
            self.add(doc.path, doc.key_line("status"), "gate-invalid", "status: done nhưng gate_2 chưa có kết luận")

    # -- tiêu đề --

    def heading_rules(self, doc: Doc) -> None:
        h1 = next((doc.line_no(i) for i, line in enumerate(doc.masked) if line.startswith("# ")), doc.start)
        headings = []
        first_h2 = len(doc.raw)
        for idx, line in enumerate(doc.masked):
            if line.startswith("## "):
                first_h2 = min(first_h2, idx)
                headings.append(NUMBERING.sub("", doc.raw[idx][3:].strip()).casefold())
        for phrase in REQUIRED_HEADINGS[doc.kind]:
            if not any(phrase.casefold() in h for h in headings):
                self.add(doc.path, h1, "heading-missing", f"thiếu tiêu đề cấp 2 chứa '{phrase}'")
        if doc.kind == "spec" and doc.data.get("size") in ("medium", "large") and not any("truy vết" in h for h in headings):
            self.add(doc.path, h1, "heading-missing", "thiếu tiêu đề cấp 2 chứa 'Truy vết' (nên có từ cỡ vừa)")
        if doc.kind in SPRINT_DOCS + ("feature",):
            if not any(CONCLUSION.match(doc.raw[i]) for i in range(first_h2)):
                self.add(doc.path, h1, "conclusion-missing", "thiếu dòng '> **Kết luận:**' trước tiêu đề cấp 2 đầu tiên")

    # -- mã định danh --

    def owns(self, doc: Doc, code_prefix: str) -> bool:
        owner = c.OWNER[code_prefix]
        return doc.kind == "sprint" or doc.kind == owner or (doc.kind == "feature" and owner == "spec")

    def target(self, doc: Doc, owner: str):
        """Tài liệu sở hữu tiền tố `owner`; `None` khi không tìm được qua `links`."""
        if doc.kind == "sprint" or doc.kind == owner or (doc.kind == "feature" and owner == "spec"):
            return doc
        links = doc.data.get("links")
        rel = links.get(owner) if isinstance(links, dict) else None
        if not isinstance(rel, str):
            return None
        path = doc.path.parent / rel
        return self.doc(path) if path.is_file() else None

    def id_rules(self, doc: Doc) -> None:
        if doc.kind in REGISTRY_DOCS:
            for d in doc.defs:
                if prefix(d.code) in c.OWNER:
                    self.add(doc.path, d.line, "id-wrong-doc", f"'{d.code}' là mã mục của tài liệu sprint, không thuộc sổ gốc")
            return
        for d in doc.defs:
            if prefix(d.code) in c.OWNER and not self.owns(doc, prefix(d.code)):
                self.add(doc.path, d.line, "id-wrong-doc",
                         f"'{d.code}' thuộc {c.OWNER[prefix(d.code)].upper()}, không định nghĩa trong {doc.kind.upper()}")
        unresolved: dict = {}
        for idx, line in enumerate(doc.masked):
            for code, pos in codes_at(line):
                if prefix(code) not in c.OWNER:
                    continue
                owner = c.OWNER[prefix(code)]
                target = self.target(doc, owner)
                if target is None:
                    unresolved.setdefault(owner, doc.line_no(idx))
                elif code not in target.defined():
                    where = "tài liệu này" if target is doc else c.display(target.path)
                    self.add(doc.path, doc.line_no(idx), "xref-missing", f"'{code}' không được định nghĩa ở {where}" + doc.hint(idx, pos, code))
        for owner, line in unresolved.items():
            self.add(doc.path, line, "xref-unresolved", f"không có links.{owner} (hoặc file không tồn tại) để đối chiếu mã của {owner.upper()}")

    def lead_rule(self, doc: Doc) -> None:
        """Bảng mã (cột đầu "Mã") cần câu dẫn in đậm ngay trên: tài liệu nào, mã là gì. Bỏ qua khối "Đang mở"."""
        generated = prev_table = False
        for idx, line in enumerate(doc.masked):
            raw = doc.raw[idx].strip()
            if raw in (OPEN_START, OPEN_END):
                generated = raw == OPEN_START
            cells = c.table_cells(line)
            if cells is None or prev_table:
                prev_table = cells is not None
                continue
            prev_table = True
            if generated or cells[0].strip("* ").casefold() != "mã":
                continue
            above = idx - 1
            while above >= 0 and not doc.masked[above].strip():
                above -= 1
            if above < 0 or "**" not in doc.masked[above]:
                self.add(doc.path, doc.line_no(idx), "id-list-lead",
                         "bảng mã thiếu câu dẫn ngay trên — ví dụ 'SPEC có 3 **user story** (US):' (skill id-convention)")

    def trace_rule(self, doc: Doc) -> None:
        tasks: dict = {}
        for d in doc.defs:
            if prefix(d.code) == "TK" and d.position in ("heading", "item"):
                refs = [x for x in codes_on(doc.masked[d.line - doc.start]) if prefix(x) in ("FR", "SC")]
                tasks.setdefault(d.code, (d.line, bool(refs)))
        for code, (line, has_refs) in tasks.items():
            if has_refs:
                continue
            if "." not in code:
                self.add(doc.path, line, "task-without-trace", f"{code} không trỏ FR/SC nào")
                continue
            parent = code.rsplit(".", 1)[0]
            while parent not in tasks and "." in parent:
                parent = parent.rsplit(".", 1)[0]
            if parent not in tasks:
                self.add(doc.path, line, "task-without-trace", f"{code} không trỏ FR/SC và không có việc cha để kế thừa")

    def verification_rules(self, doc: Doc) -> None:
        vr_rows = [d for d in doc.defs if prefix(d.code) == "VR" and d.position == "table"]
        covered = set()
        for d in vr_rows:
            covered.update(x for x in codes_on(doc.masked[d.line - doc.start]) if prefix(x) == "SC")
        spec = self.target(doc, "spec")
        if spec is not None:
            for d in spec.defs:
                if prefix(d.code) == "SC" and "." not in d.code and d.code not in covered:
                    line = vr_rows[0].line if vr_rows else doc.start
                    self.add(doc.path, line, "report-sc-without-vr", f"{d.code} của SPEC chưa có VR nào")
        if spec is not None and doc.kind == "report":
            self._fr_coverage(doc, spec, vr_rows)
        roles = doc.data.get("roles")
        if not vr_rows or not isinstance(roles, dict):
            return

        def label(role: str):
            value = roles.get(role)
            return value[1] if isinstance(value, list) and len(value) >= 2 and value[1] != "pending" else None

        qa = label("qa")
        if qa is None or qa not in (label("implementer"), label("architect")):
            return
        declared = any(SELF_CHECK in doc.raw[d.line - doc.start].casefold() for d in vr_rows)
        if not declared:
            self.add(doc.path, doc.key_line("roles.qa"), "qa-not-independent",
                     f"qa '{qa}' trùng implementer/architect; ghi '{SELF_CHECK}' ở VR hoặc giao QA cho agent khác")
        elif doc.data.get("verdict") == "pass":
            self.add(doc.path, doc.key_line("verdict"), "qa-not-independent",
                     "VR tự kiểm, chưa độc lập: verdict tối đa conditional_pass")

    def _fr_coverage(self, doc: Doc, spec: Doc, vr_rows: list) -> None:
        """Mỗi `FRn` của SPEC có `VR` trỏ tới `FRn` hoặc kịch bản `FRn.m`; miễn khi `bỏ` hoặc NOT_APPLICABLE."""

        def top(code: str) -> str:
            return code.split(".")[0]

        tested = {top(x) for d in vr_rows for x in codes_on(doc.masked[d.line - doc.start]) if prefix(x) == "FR"}
        waived = set()
        for d in spec.defs:
            raw = spec.raw[d.line - spec.start]
            if prefix(d.code) == "FR" and (NA_WITH_REASON.search(raw) or DROPPED.search(raw)):
                waived.add(top(d.code))
        for idx, line in enumerate(doc.masked):
            if NA_WITH_REASON.search(doc.raw[idx]):
                waived.update(top(x) for x in codes_on(line) if prefix(x) == "FR")
        line = vr_rows[0].line if vr_rows else doc.start
        for code in sorted({top(d.code) for d in spec.defs if prefix(d.code) == "FR"}, key=lambda x: int(x[2:])):
            if code not in tested and code not in waived:
                self.add(doc.path, line, "report-fr-without-vr",
                         f"{code} của SPEC chưa có VR nào trỏ tới nó hoặc kịch bản {code}.x "
                         "(bỏ → ghi 'bỏ' ở SPEC; không áp dụng → NOT_APPLICABLE + lý do)")

    # -- cấu hình --

    def check_config(self, root: Path) -> None:
        path = root / c.CONFIG_NAME
        if not path.is_file():
            return
        try:
            raw = json.loads(c.read_text(path))
        except json.JSONDecodeError as exc:
            self.add(path, exc.lineno, "config-syntax", f"JSON hỏng: {exc.msg}")
            return
        except (OSError, UnicodeDecodeError) as exc:
            self.report.errors.append(f"{c.display(path)}: không đọc được ({exc})")
            return
        if not isinstance(raw, dict):
            self.add(path, 1, "config-invalid", "gốc phải là object JSON")
            return
        cfg = c.merge_config(raw)
        problems = c.config_problems(cfg)
        for problem in problems:
            self.add(path, 1, "config-invalid", problem)
        if cfg.get("visibility") == "public" and isinstance(cfg.get("artifact_root"), str):
            target = c.artifact_path(root, cfg, "").resolve()
            base = root.resolve()
            if target == base or base in target.parents:
                self.add(path, 1, "config-public-root",
                         f"visibility: public nhưng artifact_root '{cfg['artifact_root']}' nằm trong gốc dự án — hồ sơ nội bộ sẽ lên repo công khai")


# --- Quét đường dẫn ------------------------------------------------------------------------------------


def _walk(root: Path, pattern: str):
    for path in sorted(root.rglob(pattern)):
        rel = path.relative_to(root).parts[:-1]
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel):
            continue
        yield path


def check_paths(paths) -> Report:
    engine = Engine()
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for config in _walk(path, c.CONFIG_NAME):
                engine.check_config(config.parent)
            for md in _walk(path, "*.md"):
                engine.check_file(md)
        elif path.is_file():
            if path.name == c.CONFIG_NAME:
                engine.check_config(path.parent)
            elif path.suffix.lower() != ".md":
                engine.report.errors.append(f"{c.display(path)}: chỉ kiểm file .md, {c.CONFIG_NAME} hoặc thư mục")
            else:
                engine.check_file(path)
        else:
            engine.report.errors.append(f"{c.display(path)}: không tồn tại")
    engine.report.findings.sort(key=lambda f: (c.display(f.path), f.line, f.rule))
    return engine.report


# --- Chế độ --self ---------------------------------------------------------------------------------------


def tracked_files(root: Path) -> list:
    """File Git đang theo dõi **và** file chưa add (trừ file bị ignore); không phải repo Git → quét cây."""
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "-c", "-o", "--exclude-standard"],
                             capture_output=True, timeout=60, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        out = None
    if out is not None and out.returncode == 0 and out.stdout:
        rels = [p for p in out.stdout.decode("utf-8", "replace").split("\0") if p]
        return [root / rel for rel in dict.fromkeys(rels) if (root / rel).is_file()]
    files = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).parts
        if path.is_file() and not any(part in SKIP_DIRS for part in rel[:-1]):
            files.append(path)
    return files


def read_denylist(path: Path | None) -> list | None:
    if path is None or not Path(path).is_file():
        return None
    try:
        words = [w.strip().casefold() for w in c.read_text(path).split("\n")]
    except (OSError, UnicodeDecodeError):
        return None
    words = [w for w in words if w and not w.startswith("#")]
    return words or None


_PATH_CHARS = frozenset("\\/:~")  # gạch ngược, gạch xuôi, hai chấm, dấu ngã


def _denied(word: str, text: str) -> bool:
    """`word`, `text` đã casefold. Mục chứa ký tự đường dẫn khớp chuỗi con; mục chữ khớp nguyên từ —
    không có chữ cái liền trước hay liền sau, nên "cat" không bắt "category" nhưng bắt "cat_x"."""
    if _PATH_CHARS & set(word):
        return word in text
    return re.search(r"(?<![^\W\d_])" + re.escape(word) + r"(?![^\W\d_])", text) is not None


# Miễn trừ chống rò — tường minh, hẹp, có lý do; mỗi mục ghi lại ở `scripts/README.md` mục "Phạm vi `--self`".
# (mẫu đường dẫn, kiểu, lý do). Kiểu quyết định phần nào của dòng được che trước khi so từ cấm:
#   file          — bỏ qua cả file (kể cả tên file)
#   credit-line   — bỏ qua dòng ghi công / bản quyền (`Copyright`, `©`)
#   upstream-ref  — che code span là `owner/repo` hoặc SHA hex; phần còn lại của dòng vẫn bị quét
#   old-skill-id  — che code span là mã skill cũ dạng `bộ:tên` hoặc `bộ:*`; phần còn lại vẫn bị quét
#   model-line    — bỏ qua dòng có chữ `model` (hồ sơ thử ghi model đã chạy)
#   author-field  — bỏ qua dòng của trường `author` / `owner` (cả khối) và `repository` / `homepage` trong manifest
#   author-section — bỏ qua mục `## Author` / `## Tác giả` của README (tới tiêu đề kế tiếp)
#   author-url    — che đúng hai URL của tác giả (`AUTHOR_REPO_URL`, `AUTHOR_SITE`); phần còn lại vẫn bị quét
# Một file khớp nhiều mục thì áp mọi kiểu khớp. Nhóm `author-attribution` (ba kiểu author-* và `credit-line` của
# LICENSE) là ngoại lệ có chủ đích do chủ sản phẩm quyết ngày 02/10/2026: ghi công tác giả ở đúng các chỗ nêu trên.
LEAK_EXEMPTIONS = (
    ("NOTICE", "file", "giấy phép MIT/Apache-2.0 buộc giữ nguyên thông báo bản quyền của tác giả nguồn"),
    ("THIRD_PARTY.md", "credit-line", "dòng ghi công và bản quyền theo giấy phép của nguồn bên thứ ba"),
    ("UPSTREAM.md", "upstream-ref", "tên repo nguồn `owner/repo` và SHA chốt là dấu vết nguồn gốc bắt buộc"),
    ("docs/MIGRATION.md", "old-skill-id", "hồ sơ lịch sử cố ý nêu mã skill cũ để tra tên mới tương ứng"),
    ("skills/*/tests/pressure.md", "model-line", "hồ sơ thử áp lực ghi model đã chạy kịch bản"),
    (".claude-plugin/plugin.json", "author-field", "author-attribution: trường tác giả, repository, homepage của manifest Claude"),
    (".claude-plugin/marketplace.json", "author-field", "author-attribution: chủ marketplace và trường tác giả của mục plugin"),
    (".codex-plugin/plugin.json", "author-field", "author-attribution: trường tác giả, repository, homepage của manifest Codex"),
    ("README.md", "author-section", "author-attribution: mục `## Author` ghi tên và trang của tác giả"),
    ("README.vi.md", "author-section", "author-attribution: mục `## Tác giả` ghi tên và trang của tác giả"),
    ("LICENSE", "credit-line", "author-attribution: dòng Copyright của chính repo ghi tên tác giả"),
    ("**", "author-url", "author-attribution: đúng hai URL của tác giả (repo GitHub, trang cá nhân) được nêu ở mọi file"),
)
LEAK_EXEMPTION_KINDS = frozenset({"file", "credit-line", "upstream-ref", "old-skill-id", "model-line",
                                  "author-field", "author-section", "author-url"})
# Hai URL của tác giả — chỉ đúng hai chuỗi này được che; `owner/repo` viết tắt, repo khác của cùng tài khoản, tên
# miền khác có cùng tiền tố, email đều vẫn bị quét.
AUTHOR_REPO_URL = "github.com/ducnguyen221/agent-agile-team"
AUTHOR_SITE = "ducnguyen.vn"
_AUTHOR_URL = re.compile(
    r"(?i)(?<![A-Za-z0-9-])(?:" + re.escape(AUTHOR_REPO_URL) + r"(?![A-Za-z0-9_-])|"
    + re.escape(AUTHOR_SITE) + r"(?![A-Za-z0-9-]))")
_AUTHOR_KEY = re.compile(r'^\s*"(?:author|owner|repository|homepage)"\s*:')
_AUTHOR_HEADING = re.compile(r"^##\s+(?:Author|Tác giả)\s*$")

_CODE_SPAN = re.compile(r"`([^`\n]*)`")
# Chủ (owner) của các nguồn công khai ghi trong UPSTREAM.md — chỉ `owner/repo` của những chủ này được che; owner lạ
# (kể cả trùng từ cấm) vẫn bị quét. Thêm nguồn mới vào UPSTREAM.md thì thêm chủ vào đây (so khớp không phân biệt hoa thường);
# `tests/test_provenance.py` đỏ khi Sổ theo dõi của UPSTREAM.md và danh sách này lệch nhau.
UPSTREAM_OWNERS = frozenset(o.casefold() for o in (
    "obra", "affaan-m", "garrytan", "github", "Fission-AI", "supabase", "alibaba", "bmad-code-org",
    "JuliusBrussee", "ccusage", "ryoppippi", "yamadashy", "google", "OWASP", "basecamp.com",
    "rtk-ai", "oraios", "mksglu", "microsoft",
))
_SHA = re.compile(r"[0-9a-f]{7,40}")
_OWNER_REPO = re.compile(r"([A-Za-z0-9][A-Za-z0-9_.-]*)/[A-Za-z0-9][A-Za-z0-9_.-]*")


class _UpstreamRef:
    """Code span được che trong UPSTREAM.md: SHA hex, hoặc `owner/repo` với owner thuộc `UPSTREAM_OWNERS`."""

    @staticmethod
    def fullmatch(text: str) -> bool:
        if _SHA.fullmatch(text):
            return True
        m = _OWNER_REPO.fullmatch(text)
        return bool(m) and m.group(1).casefold() in UPSTREAM_OWNERS


_UPSTREAM_REF = _UpstreamRef()
_OLD_SKILL_ID = re.compile(r"[a-z0-9][a-z0-9-]*:(?:\*|[a-z0-9][a-z0-9-]*)")
_CREDIT = re.compile(r"(?i)\bcopyright\b|©")


def _glob(pattern: str) -> str:
    """`**` khớp mọi đường (kể cả `/`), `*` khớp một đoạn tên."""
    return re.escape(pattern).replace(r"\*\*", ".+").replace(r"\*", "[^/]+")


def _leak_kinds(rel: str) -> list:
    return [kind for pattern, kind, _reason in LEAK_EXEMPTIONS if re.fullmatch(_glob(pattern), rel)]


def _mask_spans(line: str, token: re.Pattern) -> str:
    return _CODE_SPAN.sub(lambda m: " " if token.fullmatch(m.group(1)) else m.group(0), line)


def _leak_view(kinds: list, line: str) -> str:
    """Phần của dòng còn phải quét sau khi áp mọi miễn trừ của file; chuỗi rỗng = cả dòng được miễn."""
    for kind in kinds:
        if kind == "credit-line" and _CREDIT.search(line):
            return ""
        if kind == "model-line" and re.search(r"(?i)\bmodel\b", line):
            return ""
        if kind == "upstream-ref":
            line = _mask_spans(line, _UPSTREAM_REF)
        elif kind == "old-skill-id":
            line = _mask_spans(line, _OLD_SKILL_ID)
        elif kind == "author-url":
            line = _AUTHOR_URL.sub(" ", line)
    return line


def _author_lines(kinds: list, lines: list) -> set:
    """Số dòng (đếm từ 1) được miễn trọn vì là phần ghi công tác giả: trường của manifest hoặc mục README."""
    keep = set()
    if "author-field" in kinds:
        depth = 0
        for idx, line in enumerate(lines, 1):
            if depth == 0 and not _AUTHOR_KEY.match(line):
                continue
            keep.add(idx)
            depth = max(0, depth + line.count("{") + line.count("[") - line.count("}") - line.count("]"))
    if "author-section" in kinds:
        inside = False
        for idx, line in enumerate(lines, 1):
            if line.startswith("#"):
                inside = bool(_AUTHOR_HEADING.match(line))
            if inside:
                keep.add(idx)
    return keep


def run_self(root: Path, denylist_path: Path | None) -> Report:
    root = Path(root)
    engine = Engine()
    files = tracked_files(root)
    for path in files:
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() == ".md" and not rel.startswith("tests/fixtures/"):
            engine.check_file(path)
    words = read_denylist(denylist_path)
    engine.report.denylist_status = "ok" if words else "NOT_CONFIGURED"
    if words:
        for path in files:
            rel = path.relative_to(root).as_posix()
            kinds = _leak_kinds(rel)
            if "file" in kinds:
                continue
            for n, word in enumerate(words, 1):
                if _denied(word, rel.casefold()):
                    engine.add(path, 1, "leak-denylist", f"tên file chứa từ cấm số {n} của danh sách")
            data = path.read_bytes()
            if b"\0" in data:
                continue
            lines = c.normalize(data.decode("utf-8", "replace")).split("\n")
            exempt = _author_lines(kinds, lines)
            for idx, line in enumerate(lines, 1):
                if idx in exempt:
                    continue
                low = _leak_view(kinds, line).casefold()
                if not low:
                    continue
                for n, word in enumerate(words, 1):
                    if _denied(word, low):
                        engine.add(path, idx, "leak-denylist", f"chứa từ cấm số {n} của danh sách (không in lại từ)")
    agents = root / "AGENTS.md"
    if not agents.is_file():
        engine.add(agents, 1, "agents-md-budget", "không có AGENTS.md ở gốc repo")
    else:
        data = agents.read_bytes()
        lines = len(c.normalize(data.decode("utf-8", "replace")).splitlines())
        if lines > AGENTS_MAX_LINES or len(data) > AGENTS_MAX_BYTES:
            engine.add(agents, 1, "agents-md-budget",
                       f"{lines} dòng / {len(data)} byte — trần {AGENTS_MAX_LINES} dòng / {AGENTS_MAX_BYTES} byte")
    engine.report.findings.sort(key=lambda f: (c.display(f.path), f.line, f.rule))
    return engine.report


# --- Dòng lệnh -----------------------------------------------------------------------------------------


def summary(report: Report) -> str:
    counts = {level: sum(1 for f in report.findings if f.level == level) for level in (CHAN, PHAI, NEN, GHI)}
    verdict = {0: "Đạt", 1: "Không đạt", 2: "Lỗi đầu vào — Không đạt"}[report.exit_code]
    text = (f"check: {report.checked} file .md, {len(report.findings)} phát hiện — " + " · ".join(f"{k} {v}" for k, v in counts.items())
            + f" → {verdict}")
    if report.denylist_status:
        text += f" · chống rò: {report.denylist_status}"
    return text


def main(argv=None, env=None) -> int:
    c.utf8_stdio()
    env = os.environ if env is None else env
    parser = argparse.ArgumentParser(prog="check.py", description="Kiểm chuẩn tài liệu agent-agile-team.")
    parser.add_argument("paths", nargs="*", help="file .md, .agile.json hoặc thư mục")
    parser.add_argument("--self", dest="self_mode", action="store_true", help="kiểm lõi sạch của repo này")
    parser.add_argument("--root", default=str(c.REPO), help="gốc repo cho --self (mặc định: repo chứa script)")
    args = parser.parse_args(argv)
    if not args.self_mode and not args.paths:
        parser.error("cần ít nhất một đường dẫn, hoặc --self")
    if args.self_mode and args.paths:
        parser.error("--self không nhận đường dẫn; dùng --root <repo> để chọn repo")
    if args.self_mode:
        value = env.get("AGENT_AGILE_DENYLIST", "")
        report = run_self(Path(args.root), Path(value) if value else None)
        if report.denylist_status == "NOT_CONFIGURED":
            print("WARNING NOT_CONFIGURED: AGENT_AGILE_DENYLIST chưa đặt, file không đọc được hoặc rỗng — "
                  "luật leak-denylist Chưa chạy (không phải Đạt).", file=sys.stderr)
    else:
        report = check_paths(args.paths)
    for error in report.errors:
        print(f"{error} [lỗi đầu vào]")
    for finding in report.findings:
        print(finding.render())
    print(summary(report))
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
