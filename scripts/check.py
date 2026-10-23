#!/usr/bin/env python3
"""Kiểm chuẩn tài liệu sprint, sổ gốc, spec sống và cấu hình dự án; `--self` kiểm lõi sạch của repo.

Cách chạy:
    python scripts/check.py <đường-dẫn> [<đường-dẫn> ...]   # file .md, .agile.json hoặc thư mục (quét đệ quy)
    python scripts/check.py --self [--root <repo>]          # lõi sạch, một thang mức, ngân sách AGENTS.md

Mã thoát: 0 = Đạt (không có Chặn/Phải sửa) · 1 = Không đạt · 2 = lỗi đầu vào (đường dẫn không có, file
không đọc được, frontmatter ngoài tập con YAML, `.agile.json` hỏng).

Biến môi trường: `AGENT_AGILE_DENYLIST` — đường tới danh sách từ cấm ngoài repo (chỉ `--self` dùng);
`AGENT_AGILE_LEDGER` — mẫu đường file sổ tập trung, chứa `{project}` (chỉ dự án khai `ledger.project` mới dùng).
Hợp đồng luật: `templates/README.md`; mô tả từng luật: `scripts/README.md`.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
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
    "sprint-size-mismatch": (PHAI, "hình tài liệu không khớp `size`: `SPRINT.md` ở cỡ vừa/lớn, hoặc bốn file ở cỡ rất nhỏ"),
    "conclusion-missing": (PHAI, "thiếu khối `> **Kết luận:**` trước tiêu đề cấp 2 đầu tiên"),
    "id-bare-single-letter": (PHAI, "mã một chữ cái + số ngoài dấu code (trừ T1/T2/T3)"),
    "id-unknown-prefix": (PHAI, "định nghĩa mục bằng tiền tố hai chữ cái ngoài bảng mã"),
    "id-wrong-doc": (PHAI, "định nghĩa mục bằng tiền tố thuộc tài liệu khác"),
    "id-list-lead": (GHI, "bảng có cột đầu `Mã` mà dòng ngay trên không có câu dẫn in đậm (tài liệu + nghĩa của mã)"),
    "xref-missing": (PHAI, "nhắc tới mã không được định nghĩa ở tài liệu sở hữu"),
    "xref-unresolved": (GHI, "không tìm được tài liệu sở hữu qua `links` để đối chiếu mã"),
    "task-without-trace": (PHAI, "việc `TK` không trỏ `FR`/`SC` nào (việc con kế thừa việc cha)"),
    "task-order": (PHAI, "`Đầu vào:` của `TK` trỏ `TK` số ≥ chính nó — số `TK` phải là thứ tự làm"),
    "task-gap": (GHI, "số `TK` cấp một không liền 1…N theo thứ tự xuất hiện"),
    "plan-goal-block": (GHI, "mục Mục tiêu của PLAN thiếu một trong ba dòng nhãn (mẫu PLAN)"),
    "report-sc-without-vr": (PHAI, "`SC` của SPEC không có `VR` nào trong REPORT"),
    "report-fr-without-vr": (PHAI, "`FR` của SPEC không có `VR` nào trỏ tới nó hoặc kịch bản con (trừ `bỏ`/NOT_APPLICABLE)"),
    "self-review": (CHAN, "một nhãn agent vừa giữ vai thực thi vừa giữ vai kiểm định"),
    "qa-not-independent": (PHAI, "QA trùng nhãn với implementer/architect mà không khai tự kiểm, hoặc khai tự kiểm mà verdict là pass"),
    "roles-invalid": (PHAI, "`roles` sai hình: vai lạ, tier ngoài T1–T3, thiếu nhãn agent"),
    "gate-invalid": (PHAI, "cổng đã kết luận mà thiếu thời điểm/câu nguyên văn, hoặc trạng thái vượt cổng"),
    "gate-delegation-invalid": (PHAI, "duyệt thay thiếu lời cấp/phạm vi/hạn/bản ghi, quá hạn, đã thu hồi, người duyệt không phải T1, hoặc vào vùng cấm"),
    "old-scale-label": (PHAI, "nhãn thang mức cũ (kiểu nguồn trong câu, hoặc tiếng Việt kiểu cũ) ngoài bảng quy đổi `method/severity.md`"),
    "config-syntax": (CHAN, "`.agile.json` không phải JSON hợp lệ (lỗi đầu vào → thoát 2)"),
    "config-invalid": (PHAI, "`.agile.json` sai hình hoặc đổi ngưỡng coverage không ghi lý do"),
    "config-public-root": (CHAN, "`visibility: public` mà `artifact_root` nằm trong gốc dự án"),
    "ledger-missing-row": (PHAI, "dự án khai sổ tập trung mà sổ không có dòng cho sprint đang mở"),
    "ledger-stale": (PHAI, "dòng sổ lệch `status` hoặc ngày cũ hơn `updated` của PROGRESS/SPRINT"),
    "ledger-unreadable": (PHAI, "file sổ không có, không đọc được UTF-8 hoặc không có bảng cột đầu 'Sprint'"),
    "ledger-unconfigured": (GHI, "dự án khai sổ tập trung mà máy chưa đặt mẫu đường `AGENT_AGILE_LEDGER`"),
    "leak-denylist": (CHAN, "`--self`: file của repo chứa từ trong danh sách cấm"),
    "agents-md-budget": (PHAI, "`--self`: `AGENTS.md` quá 120 dòng hoặc quá 10 KB"),
    "routing-invalid": (PHAI, "routing evidence marker/JSON/record không hợp lệ"),
    "routing-unknown": (GHI, "routing record có field ngoài schema 1"),
    "routing-manifest-invalid": (PHAI, "routing applicability manifest thiếu hoặc sai hình"),
    "routing-missing": (PHAI, "routing pilot thiếu record/document/assignment/attempt/source coverage"),
    "routing-duplicate": (PHAI, "routing pilot có record/assignment/attempt trùng"),
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
    "risk_tags", "review_round", "requests", "sprints", "next_id", "links",
    "gate_1_mode", "gate_2_mode", "delegation"}

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
GATE_MODES = {"human", "delegated"}  # vắng `gate_N_mode` = human; chỉ `delegated` kích các luật duyệt thay
DELEGATION_FORBIDDEN_TAGS = {"secret", "auth"}  # vùng cấm duyệt thay (SPEC 7.3)
DELEGATION_RECORD = "Bản ghi duyệt thay"  # tiêu đề cấp 2 ở plan, report, sprint
DELEGATION_LABELS = ("Phương án chọn:", "Phương án bị loại:", "Nếu sai thì tốn gì:")
DELEGATION_QUOTE = "duyệt thay:"  # tiền tố bắt buộc của `gate_N_quote`
DELEGATION_KEYS = ("grant", "grant_at", "scope", "expires", "by", "tier", "files", "revoked_at")
MOMENT = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2})(?: ([0-9]{2}):([0-9]{2}) ([+-])([0-9]{2})(?::?([0-9]{2}))?)?")
EXECUTORS = {"analyst", "architect", "implementer", "qa", "researcher"}
VERIFIERS = {"business-reviewer", "tech-reviewer"}
NEXT_ID_PREFIX = {"requests": "RQ", "specs": "FS", "sprints": "SPR"}
WIDTH_KEY = {"RQ": "request", "FS": "feature", "SPR": "sprint"}

REQUIRED_HEADINGS = {
    "spec": ("Bối cảnh", "Câu chuyện người dùng", "Yêu cầu chức năng", "Tiêu chí thành công", "Ngoài phạm vi", "Câu hỏi cần làm rõ"),
    "plan": ("Mục tiêu", "Kiến trúc", "Ràng buộc chung", "Trọng tâm review", "Việc", "Rủi ro", "Quyết định cần người", "Ước lượng"),
    "progress": ("Bảng trạng thái việc", "Nhật ký", "Vướng mắc", "Vòng kiểm định hiện tại"),
    "report": ("Tóm tắt cho người không chuyên", "Kết quả kiểm định", "Phát hiện của reviewer", "Rủi ro còn lại",
               "Cách dùng, đã đổi gì, cách hoàn tác", "Bài học", "Việc để lại", "Review & Retro", "Cổng 2"),
    "sprint": ("SPEC", "PLAN", "PROGRESS", "REPORT"),  # bốn phần; cỡ rất nhỏ còn nhận hai phần (SPRINT_TINY_HEADINGS)
    "feature": ("Hành vi hiện hành", "Tiêu chí đang giữ", "Giới hạn đã biết", "Quyết định liên quan", "Lịch sử sprint"),
    "requests": ("Đang mở", "Timeline"),
    "sprints": ("Đang mở", "Timeline"),
    "specs": ("Đang mở", "Danh mục"),
}

PLAN_GOAL_LABELS = ("Mục tiêu sprint:", "Kết quả mong muốn / xong khi:", "Rủi ro cần chú ý:")  # SPEC 7.8
INPUT_FIELD = "**Đầu vào:**"
OUTPUT_FIELD = "**Đầu ra:**"
PARALLEL_MARK = "chạy cùng được với"

SPRINT_TINY_HEADINGS = ("Kế hoạch", "Kết quả")  # `SPRINT.md` cỡ rất nhỏ: hai phần; bốn phần cũ vẫn hợp lệ
SPRINT_FOUR = REQUIRED_HEADINGS["sprint"]

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
# Nhãn tiếng Việt kiểu cũ (ngoài bốn mức Chặn / Phải sửa / Nên sửa / Ghi chú) — chỉ xét ở chỗ đứng của một nhãn mức.
OLD_VI = ("cao", "trung bình", "thấp", "nghiêm trọng", "quan trọng", "nhẹ")
OLD_CELL_VI = set(OLD_VI)
# Nhãn tiếng Việt kiểu cũ chỉ bị bắt ở cột mà tiêu đề NÓI LÀ mức của phát hiện; "Mức chắc chắn", "Mức rủi ro" là
# thang khác, "Cao" ở đó là giá trị hợp lệ.
SEVERITY_HEADERS_VI = {"mức", "mức độ", "mức nghiêm trọng", "độ nghiêm trọng"}
OLD_FIELD = re.compile(
    r"(?i)\b(?:severity|mức)\**\s*:\s*\**\s*(critical|high|medium|low|important|minor|" + "|".join(OLD_VI) + r")\b")
# Nhãn kiểu nguồn nằm trong câu: chữ HOA nguyên từ (chữ thường như "high-level", "low-code" không trúng), nhãn trong
# ngoặc vuông đầu dòng (kể cả sau gạch đầu dòng hay dấu trích dẫn) và ngưỡng "confidence ≥ 80".
OLD_SRC_WORD = re.compile(r"(?<![\w/\-.])(CRITICAL|HIGH|MEDIUM|LOW)(?![\w/\-])")
OLD_SRC_BRACKET = re.compile(
    r"^\s*(?:[-*+>]\s+)*\[(CRITICAL|HIGH|MEDIUM|LOW|BLOCK|WARN|INFO|NOTE|Critical|Important|Minor|Warning)\]")
OLD_SRC_CONFIDENCE = re.compile(r"(?i)\bconfidence\s*(?:≥|>=|>)\s*[0-9]+")
SELF_CHECK = "tự kiểm, chưa độc lập"
NOT_APPLICABLE = "NOT_APPLICABLE"
# NOT_APPLICABLE chỉ miễn khi có lý do theo sau (một chữ sau dấu nối tuỳ chọn).
NA_WITH_REASON = re.compile(r"NOT_APPLICABLE[ ]*[—–:(-]?[ ]*[*_'\"`]*[A-Za-zÀ-ỹ0-9]")
DROPPED = re.compile(r"[(—–:-]\s*bỏ\s*(?:\)|$)")  # trạng thái `bỏ` của mục: "(bỏ)" hoặc "— bỏ" cuối dòng
AGENTS_MAX_LINES = 120
AGENTS_MAX_BYTES = 10 * 1024
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".tmp"}
# Thư mục `evidence` cạnh tài liệu sprint là hồ sơ kèm, không phải tài liệu sprint: quét thư mục thì bỏ qua (FR4.1).
EVIDENCE_DIR = "evidence"
SPRINT_DOC_NAMES = ("SPEC.md", "PLAN.md", "PROGRESS.md", "REPORT.md", "SPRINT.md")
OPEN_START, OPEN_END = "<!-- agile:open:start -->", "<!-- agile:open:end -->"  # khối do `index` sinh
SPAN_HINT = (" — có dấu huyền kề bên: mã nằm trong code span lồng nhau hoặc ngắt dòng? Code span chứa dấu huyền"
             " thì bọc ngoài bằng hai dấu huyền")
ROUTING_MARKER = "<!-- routing-evidence:v1 -->"
ROUTING_SCHEMA = json.loads((c.REPO / "evals" / "task-routing" / "run.schema.json").read_text(encoding="utf-8"))


def _routing_json_equal(left: object, right: object) -> bool:
    """JSON Schema does not equate Python booleans with JSON numbers."""
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    return left == right


def _routing_reject_constant(value: str) -> None:
    raise ValueError(f"nonstandard JSON constant: {value}")


def _routing_timestamps(record: dict) -> tuple[dict[str, datetime], list[str]]:
    paths = ("notification.notified_at", "time.started_at", "time.finished_at",
             "provenance.catalog_at", "cost.price_source_at", "assignment.override.approved_at")
    parsed: dict[str, datetime] = {}
    problems: list[str] = []
    for path in paths:
        value: object = record
        for key in path.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        if value is None:
            continue
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", value):
            problems.append(f"{path}: invalid timestamp")
            continue
        try:
            parsed[path] = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            problems.append(f"{path}: impossible timestamp")
    return parsed, problems


def _routing_shape(value: object, spec: dict, where: str = "") -> list[str]:
    """Check the small JSON Schema vocabulary used by the frozen routing schema (stdlib only)."""
    if "$ref" in spec:
        name = spec["$ref"].split("/")[-1]
        return _routing_shape(value, ROUTING_SCHEMA["$defs"][name], where)
    problems: list[str] = []
    if "oneOf" in spec:
        if sum(not _routing_shape(value, option, where) for option in spec["oneOf"]) != 1:
            problems.append(f"{where}: no unique schema variant")
    for part in spec.get("allOf", []):
        problems.extend(_routing_shape(value, part, where))
    allowed = spec.get("type")
    if allowed is not None:
        types = allowed if isinstance(allowed, list) else [allowed]
        matches = {
            "object": isinstance(value, dict),
            "array": isinstance(value, list),
            "string": isinstance(value, str),
            "integer": isinstance(value, int) and not isinstance(value, bool),
            "number": isinstance(value, (int, float)) and not isinstance(value, bool),
            "boolean": isinstance(value, bool),
            "null": value is None,
        }
        if not any(matches[t] for t in types):
            return problems + [f"{where}: expected {'|'.join(types)}"]
    if isinstance(value, float) and not math.isfinite(value):
        return problems + [f"{where}: nonfinite number"]
    if "const" in spec and not _routing_json_equal(value, spec["const"]):
        problems.append(f"{where}: expected {spec['const']!r}")
    if "enum" in spec and not any(_routing_json_equal(value, option) for option in spec["enum"]):
        problems.append(f"{where}: value outside enum")
    if isinstance(value, str):
        if len(value) < spec.get("minLength", 0):
            problems.append(f"{where}: empty value")
        if "pattern" in spec and not re.search(spec["pattern"], value):
            problems.append(f"{where}: invalid pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        for bound in ("minimum", "maximum"):
            if bound in spec and ((bound == "minimum" and value < spec[bound])
                                  or (bound == "maximum" and value > spec[bound])):
                problems.append(f"{where}: outside {bound}")
    if isinstance(value, list):
        if spec.get("uniqueItems") and len(set(map(str, value))) != len(value):
            problems.append(f"{where}: duplicate items")
        for index, item in enumerate(value):
            if "items" in spec:
                problems.extend(_routing_shape(item, spec["items"], f"{where}[{index}]"))
    if isinstance(value, dict):
        for key in spec.get("required", []):
            if key not in value:
                problems.append(f"{where}.{key}: required")
        props = spec.get("properties", {})
        for key, item in value.items():
            nested = props.get(key, spec.get("additionalProperties"))
            if isinstance(nested, dict):
                problems.extend(_routing_shape(item, nested, f"{where}.{key}".strip(".")))
    return problems


def _routing_null_paths(value: object, prefix: str = "") -> list[str]:
    if value is None:
        return [prefix]
    if isinstance(value, dict):
        return [path for key, item in value.items() if key != "unknown_reasons"
                for path in _routing_null_paths(item, f"{prefix}.{key}".strip("."))]
    return []


def _routing_safe_ref(ref: str) -> bool:
    """Check a reference's syntax without opening its target."""
    return bool(ref and not ref.startswith(("/", "\\")) and not re.match(r"^[A-Za-z]:", ref)
                and ".." not in ref.replace("\\", "/").split("/"))


def _routing_reference_problems(value: object, where: str = "record") -> list[str]:
    problems = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{where}.{key}"
            if key != "unknown_reasons" and (key.endswith("_ref") or key.endswith("_refs") or key == "evidence_refs"):
                candidates = item if isinstance(item, list) else [item]
                for candidate in candidates:
                    if isinstance(candidate, str) and not _routing_safe_ref(candidate):
                        problems.append(f"{path}: unsafe reference")
            problems.extend(_routing_reference_problems(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            problems.extend(_routing_reference_problems(item, f"{where}[{index}]"))
    return problems


def _routing_unknown_keys(value: object, spec: dict, where: str = "record") -> list[str]:
    if "$ref" in spec:
        return _routing_unknown_keys(value, ROUTING_SCHEMA["$defs"][spec["$ref"].split("/")[-1]], where)
    if not isinstance(value, dict):
        return []
    properties = dict(spec.get("properties", {}))
    for part in spec.get("allOf", []) + spec.get("oneOf", []):
        if "$ref" in part:
            part = ROUTING_SCHEMA["$defs"][part["$ref"].split("/")[-1]]
        properties.update(part.get("properties", {}))
    unknown = []
    for key, item in value.items():
        path = f"{where}.{key}"
        if key in properties:
            unknown.extend(_routing_unknown_keys(item, properties[key], path))
        elif "additionalProperties" not in spec:
            unknown.append(path)
    return unknown


def routing_record_problems(record: dict, expected_refs: set) -> list[tuple[str, str]]:
    """Pure validation of one routing record; no model selection or filesystem access."""
    if not isinstance(record, dict):
        return [("routing-invalid", "routing record phải là object")]
    problems = [("routing-invalid", message) for message in _routing_shape(record, ROUTING_SCHEMA, "record")]
    timestamps, timestamp_problems = _routing_timestamps(record)
    problems.extend(("routing-invalid", message) for message in timestamp_problems)
    problems.extend(("routing-unknown", f"{path}: unknown field") for path in _routing_unknown_keys(record, ROUTING_SCHEMA))
    problems.extend(("routing-invalid", message) for message in _routing_reference_problems(record))
    kind = record.get("record_kind")
    if kind == "classification" and not isinstance(record.get("axes"), dict):
        problems.append(("routing-invalid", "classification phải có axes"))
    if kind == "classification" and not isinstance(record.get("assignment"), dict):
        problems.append(("routing-invalid", "classification phải có assignment"))
    if kind == "attempt":
        for key in ("identity", "dispatch", "provenance", "outcome", "repair_history", "quality", "time", "usage", "cost", "join"):
            if not isinstance(record.get(key), dict):
                problems.append(("routing-invalid", f"attempt phải có {key}"))
    reasons = record.get("unknown_reasons")
    if not isinstance(reasons, dict):
        return problems
    for path in _routing_null_paths(record):
        if not isinstance(reasons.get(path), str) or not reasons[path].strip():
            problems.append(("routing-invalid", f"{path}: null cần unknown_reasons"))
    refs = record.get("evidence_refs", [])
    if isinstance(refs, list):
        for ref in refs:
            if isinstance(ref, str) and not _routing_safe_ref(ref):
                problems.append(("routing-invalid", f"unsafe evidence ref: {ref!r}"))
        if expected_refs and not expected_refs.issubset({ref for ref in refs if isinstance(ref, str)}):
            problems.append(("routing-invalid", "evidence_refs thiếu expected refs"))
    if kind == "classification":
        axes = record.get("axes", {})
        if isinstance(axes, dict):
            ordinal_map = {
                "ambiguity": ("resolved", "technical_unknown", "owner_decision_open"),
                "scope_dependencies": ("local", "coupled", "cross_boundary"),
                "error_consequence": ("reversible_local", "shared_behavior", "sensitive_or_irreversible"),
                "verifiability": ("deterministic", "mixed", "weak_or_unavailable"),
                "plan_readiness": ("complete_feasible", "direction_only", "invalid_or_unavailable"),
                "execution_complexity": ("bounded_known", "nontrivial", "complex"),
            }
            for name, axis in axes.items():
                if not isinstance(axis, dict):
                    continue
                if (axis.get("value") is None) != (axis.get("ordinal") is None):
                    problems.append(("routing-invalid", f"axes.{name}: value/ordinal phải cùng known hoặc cùng null"))
                if name in ordinal_map and axis.get("value") in ordinal_map[name]:
                    if axis.get("ordinal") != ordinal_map[name].index(axis["value"]):
                        problems.append(("routing-invalid", f"axes.{name}: ordinal khác value"))
                if axis.get("ordinal") is not None and not axis.get("evidence_refs"):
                    problems.append(("routing-invalid", f"axes.{name}: ordinal thiếu evidence"))
            technical = []
            for name in ("scope_dependencies", "plan_readiness", "execution_complexity"):
                axis = axes.get(name)
                if not isinstance(axis, dict):
                    technical.append(None)
                    continue
                value, ordinal, refs = axis.get("value"), axis.get("ordinal"), axis.get("evidence_refs")
                if (value in ordinal_map[name] and type(ordinal) is int
                        and ordinal == ordinal_map[name].index(value)
                        and isinstance(refs, list) and bool(refs)
                        and all(isinstance(ref, str) and _routing_safe_ref(ref) for ref in refs)):
                    technical.append(ordinal)
                else:
                    technical.append(None)
            difficulty = None
            if all(isinstance(value, int) and not isinstance(value, bool) for value in technical):
                maximum = max(technical)
                difficulty = 1 if maximum == 0 else 2 if maximum == 1 else 3 if technical.count(2) == 1 else 4
            decision = record.get("decision", {})
            if isinstance(decision, dict) and decision.get("difficulty_level") != difficulty:
                problems.append(("routing-invalid", "difficulty_level không khớp ba trục kỹ thuật có bằng chứng"))
            effort = record.get("effort", {})
            if isinstance(effort, dict) and effort.get("effort_source") == "policy" and difficulty is not None:
                if isinstance(effort.get("effort_level"), int) and effort["effort_level"] < max(2, difficulty):
                    problems.append(("routing-invalid", "policy effort thấp hơn default medium/difficulty"))
        assignment = record.get("assignment", {})
        if isinstance(assignment, dict):
            notice = record.get("notification", {})
            if isinstance(notice, dict) and notice.get("assignment_ref") != assignment.get("assignment_ref"):
                problems.append(("routing-invalid", "notification.assignment_ref khác classification assignment"))
            override = assignment.get("override")
            if isinstance(override, dict) and override.get("status") == "approved":
                decision = record.get("decision", {})
                if isinstance(decision, dict) and decision.get("override_ref") != override.get("decision_ref"):
                    problems.append(("routing-invalid", "approved override thiếu decision.override_ref"))
                notice = record.get("notification", {})
                if isinstance(notice, dict) and notice.get("approval_ref") != override.get("decision_ref"):
                    problems.append(("routing-invalid", "approved override thiếu notification.approval_ref"))
                if override.get("model_override") and isinstance(notice, dict) and notice.get("model") != override["model_override"]:
                    problems.append(("routing-invalid", "human model pin khác notification.model"))
                effort = record.get("effort", {})
                if isinstance(effort, dict) and not override.get("effort_override") and effort.get("effort_source") == "human_override":
                    problems.append(("routing-invalid", "human model pin không thay effort"))
                if isinstance(effort, dict) and override.get("effort_override") and effort.get("effort_requested") != override["effort_override"]:
                    problems.append(("routing-invalid", "human effort pin khác effort_requested"))
    if kind == "attempt":
        dispatch = record.get("dispatch", {})
        usage = record.get("usage", {})
        identity = record.get("identity", {})
        notice = record.get("notification", {})
        if isinstance(identity, dict) and isinstance(notice, dict) and notice.get("assignment_ref") != identity.get("assignment_ref"):
            problems.append(("routing-invalid", "notification.assignment_ref khác attempt assignment"))
        if isinstance(dispatch, dict) and dispatch.get("actual_model") is not None:
            source = dispatch.get("actual_model_source")
            if not isinstance(source, str) or not source.strip() or source == "requested":
                problems.append(("routing-invalid", "actual_model cần runtime source độc lập"))
        if isinstance(usage, dict):
            if any(usage.get(key) is not None for key in ("tokens_in", "tokens_out", "cache_tokens", "quota_used")) and not usage.get("usage_source"):
                problems.append(("routing-invalid", "usage đo được cần usage_source"))
            if usage.get("coverage_status") == "complete" and not usage.get("usage_source"):
                problems.append(("routing-invalid", "usage complete cần source"))
        clock = record.get("time", {})
        if isinstance(notice, dict) and isinstance(clock, dict):
            notice_at, started_at = notice.get("notified_at"), clock.get("started_at")
            if started_at and not notice_at:
                problems.append(("routing-invalid", "attempt bắt đầu nhưng thiếu notified_at trước dispatch"))
            if notice.get("model_status") == "actual" or notice.get("effort_status") == "actual":
                problems.append(("routing-invalid", "prenotice không thể xác nhận actual trước dispatch"))
            if ("notification.notified_at" in timestamps and "time.started_at" in timestamps
                    and timestamps["notification.notified_at"] > timestamps["time.started_at"]):
                problems.append(("routing-invalid", "notification sau dispatch started_at"))
        repair = record.get("repair_history", {})
        outcome = record.get("outcome", {})
        quality = record.get("quality", {})
        if isinstance(repair, dict) and isinstance(outcome, dict) and isinstance(quality, dict):
            cycle, total = repair.get("repair_cycle_index"), repair.get("total_repair_cycles")
            if isinstance(cycle, int) and isinstance(total, int) and total < cycle:
                problems.append(("routing-invalid", "total_repair_cycles không được reset dưới repair_cycle_index"))
            at_ceiling = repair.get("repair_cycle_index") == 3
            unresolved = quality.get("acceptance_pass") is False or bool(outcome.get("regressions"))
            if at_ceiling and unresolved and not outcome.get("escalations"):
                problems.append(("routing-invalid", "vòng sửa thứ ba còn lỗi/regression cần cảnh báo và handoff"))
            if at_ceiling and unresolved and isinstance(notice, dict) and notice.get("event_kind") != "handoff":
                problems.append(("routing-invalid", "vòng sửa thứ ba còn lỗi/regression cần notice handoff"))
        cost = record.get("cost", {})
        join = record.get("join", {})
        if isinstance(cost, dict) and cost.get("actual_incremental_usd") is not None:
            refs = join.get("evidence_refs", []) if isinstance(join, dict) else []
            if not isinstance(refs, list) or not any(isinstance(ref, str) and ref.startswith("billing:") for ref in refs):
                problems.append(("routing-invalid", "actual_incremental_usd kể cả 0 cần billing source"))
    criteria = record.get("criteria_change")
    if isinstance(criteria, dict):
        if criteria.get("criteria_version") != record.get("criteria_version") or criteria.get("previous_version") == record.get("criteria_version"):
            problems.append(("routing-invalid", "criteria version không nhất quán"))
        notice = record.get("notification", {})
        if isinstance(notice, dict) and notice.get("event_kind") != "criteria_change":
            problems.append(("routing-invalid", "criteria change thiếu notice tương ứng"))
    return problems


def _routing_assignment_join_problems(classification: dict, attempt: dict) -> list[tuple[str, str]]:
    """Check facts shared by an assignment and an attempt, without inferring runtime actuals."""
    problems: list[tuple[str, str]] = []
    assignment = classification.get("assignment", {})
    notice = attempt.get("notification", {})
    original_notice = classification.get("notification", {})
    dispatch = attempt.get("dispatch", {})
    effort = attempt.get("effort", {})
    if not all(isinstance(part, dict) for part in (assignment, notice, original_notice, dispatch, effort)):
        return [("routing-invalid", "assignment/attempt thiếu cấu hình để đối chiếu")]
    for key in ("task_ref", "work_item_ref", "policy_hash", "plan_hash", "criteria_version"):
        if attempt.get(key) != classification.get(key):
            problems.append(("routing-invalid", f"attempt.{key} khác classification assignment"))
    if original_notice.get("scope_ref") not in (classification.get("work_item_ref"), classification.get("task_ref")):
        problems.append(("routing-invalid", "classification notice scope khác assignment"))
    if notice.get("scope_ref") != original_notice.get("scope_ref"):
        problems.append(("routing-invalid", "attempt notice scope khác classification assignment"))
    if notice.get("role") != assignment.get("role") or original_notice.get("role") != assignment.get("role"):
        problems.append(("routing-invalid", "attempt/classification role khác assignment"))
    tier = assignment.get("requested_tier")
    if tier is not None and (notice.get("tier") != tier or original_notice.get("tier") != tier):
        problems.append(("routing-invalid", "attempt/classification tier khác assignment"))
    if notice.get("harness") != dispatch.get("harness"):
        problems.append(("routing-invalid", "attempt notice harness khác dispatch"))
    if original_notice.get("harness") != dispatch.get("harness"):
        problems.append(("routing-invalid", "attempt dispatch harness khác classification assignment"))
    if notice.get("model") != dispatch.get("requested_model"):
        problems.append(("routing-invalid", "attempt notice model khác dispatch requested_model"))
    if notice.get("native_effort") != effort.get("effort_requested"):
        problems.append(("routing-invalid", "attempt notice effort khác effort_requested"))
    for key, event in (("model", "model_change"), ("native_effort", "effort_change")):
        if notice.get(key) == original_notice.get(key):
            continue
        original_times, _ = _routing_timestamps(classification)
        attempt_times, _ = _routing_timestamps(attempt)
        before = original_times.get("notification.notified_at")
        after = attempt_times.get("notification.notified_at")
        if notice.get("event_kind") != event:
            problems.append(("routing-invalid", f"attempt {key} đổi mà thiếu notice {event}"))
        elif before is None or after is None or after <= before:
            problems.append(("routing-missing", f"attempt {key} đổi nhưng thiếu notice mới có thứ tự"))

    override = assignment.get("override")
    if not isinstance(override, dict) or override.get("status") != "approved":
        return problems
    identity = attempt.get("identity", {})
    scope_kind, scope_ref = override.get("scope_kind"), override.get("scope_ref")
    if scope_kind == "task":
        if scope_ref != classification.get("task_ref"):
            problems.append(("routing-invalid", "approved override scope khác classification task"))
        in_scope = scope_ref == attempt.get("task_ref")
    elif scope_kind == "work_item":
        if scope_ref != classification.get("work_item_ref"):
            problems.append(("routing-invalid", "approved override scope khác classification work item"))
        in_scope = scope_ref == attempt.get("work_item_ref")
    elif scope_kind == "turn" and isinstance(identity, dict):
        in_scope = scope_ref == identity.get("attempt_id")
    else:
        return problems + [("routing-missing", "approved override không xác định được scope")]
    if not in_scope:
        return problems
    class_times, _ = _routing_timestamps(classification)
    attempt_times, _ = _routing_timestamps(attempt)
    approved_at = class_times.get("assignment.override.approved_at")
    started_at = attempt_times.get("time.started_at")
    if approved_at is None or started_at is None:
        return problems + [("routing-missing", "approved override thiếu thời điểm để đối chiếu hiệu lực")]
    if approved_at > started_at:
        return problems + [("routing-invalid", "approved override sau attempt dispatch")]
    expiry = override.get("expiry")
    if expiry is not None:
        if not isinstance(expiry, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", expiry):
            return problems + [("routing-missing", "approved override expiry chưa kiểm được")]
        try:
            if datetime.fromisoformat(expiry.replace("Z", "+00:00")) <= started_at:
                return problems
        except ValueError:
            return problems + [("routing-missing", "approved override expiry chưa kiểm được")]
    decision_ref = override.get("decision_ref")
    decision = attempt.get("decision")
    if not isinstance(decision, dict):
        problems.append(("routing-invalid", "attempt decision không hợp lệ để đối chiếu override"))
        decision = {}
    if override.get("model_override") is not None:
        if dispatch.get("requested_model") != override["model_override"] or notice.get("model") != override["model_override"]:
            problems.append(("routing-invalid", "attempt trái human model pin còn hiệu lực"))
        if notice.get("approval_ref") != decision_ref or decision.get("override_ref") != decision_ref:
            problems.append(("routing-invalid", "attempt model pin thiếu approval/decision ref"))
    if override.get("effort_override") is not None:
        if effort.get("effort_requested") != override["effort_override"] or notice.get("native_effort") != override["effort_override"]:
            problems.append(("routing-invalid", "attempt trái human effort pin còn hiệu lực"))
        if notice.get("approval_ref") != decision_ref or effort.get("override_ref") != decision_ref:
            problems.append(("routing-invalid", "attempt effort pin thiếu approval/decision ref"))
    return problems


def _routing_counter_join_problems(attempts: list[dict]) -> list[tuple[str, str]]:
    """Keep verified repair totals across ordered attempts for one work item."""
    problems: list[tuple[str, str]] = []
    if not attempts:
        return problems
    rows = []
    for record in attempts:
        repair = record.get("repair_history", {})
        outcome = record.get("outcome", {})
        identity = record.get("identity", {})
        if not all(isinstance(part, dict) for part in (repair, outcome, identity)):
            problems.append(("routing-missing", "repair counter thiếu record để đối chiếu"))
            continue
        cycle, total = repair.get("repair_cycle_index"), repair.get("total_repair_cycles")
        if type(cycle) is not int or type(total) is not int:
            problems.append(("routing-missing", "repair counter chưa biết nên không thể xác nhận tổng"))
            continue
        if cycle or total:
            if not isinstance(outcome.get("root_cause_ref"), str) or not _routing_safe_ref(outcome["root_cause_ref"]):
                problems.append(("routing-missing", "repair counter thiếu root_cause_ref"))
            if not isinstance(outcome.get("first_error_ref"), str) or not _routing_safe_ref(outcome["first_error_ref"]):
                problems.append(("routing-missing", "repair counter thiếu first_error_ref baseline"))
        history = repair.get("assignment_history")
        assignment_ref = identity.get("assignment_ref")
        if (not isinstance(history, list) or not all(isinstance(ref, str) for ref in history)
                or not isinstance(assignment_ref, str) or not history or history[-1] != assignment_ref):
            problems.append(("routing-missing", "repair assignment_history thiếu assignment hiện tại"))
            continue
        times, _ = _routing_timestamps(record)
        quality, notice = record.get("quality"), record.get("notification")
        unresolved = (isinstance(quality, dict) and quality.get("acceptance_pass") is False
                      or bool(outcome.get("regressions")))
        stopped = cycle == 3 and (unresolved or isinstance(notice, dict) and notice.get("event_kind") == "handoff")
        rows.append((times.get("time.started_at"), times.get("time.finished_at"), cycle, total,
                     history, assignment_ref, outcome.get("repair_rounds"), stopped))
    if len(attempts) < 2 or not any(row[2] or row[3] for row in rows):
        return problems
    if len(rows) != len(attempts) or any(start is None or end is None or end < start
                                         for start, end, *_ in rows):
        return problems + [("routing-missing", "repair attempts thiếu thứ tự thời gian kiểm được")]
    rows.sort(key=lambda row: row[0])
    stopped_assignments: set[str] = set()
    for previous, current in zip(rows, rows[1:]):
        prev_start, prev_end, prev_cycle, prev_total, prev_history, prev_assignment, prev_rounds, prev_stopped = previous
        start, _end, cycle, total, history, assignment, rounds, _stopped = current
        if prev_stopped:
            stopped_assignments.add(prev_assignment)
        if start < prev_end or start == prev_start:
            problems.append(("routing-missing", "repair attempts chồng thời gian hoặc thứ tự không rõ"))
            continue
        if assignment == prev_assignment:
            # Repeated observations preserve counters; a new repair must advance both.
            cycle_delta = cycle - prev_cycle
            rounds_delta = rounds - prev_rounds if type(rounds) is int and type(prev_rounds) is int else None
            repair_increased = cycle_delta > 0 or total > prev_total or rounds_delta is not None and rounds_delta > 0
            if assignment in stopped_assignments and repair_increased:
                problems.append(("routing-invalid", "assignment đã dừng sau vòng ba không được thực hiện thêm repair"))
            if total - prev_total != cycle_delta or rounds_delta is not None and rounds_delta != cycle_delta:
                problems.append(("routing-invalid", "repair counters tăng/giảm không khớp trong cùng assignment"))
            if history != prev_history:
                problems.append(("routing-invalid", "assignment_history thay đổi nhưng vẫn cùng assignment"))
            if cycle < prev_cycle:
                problems.append(("routing-invalid", "repair_cycle_index reset trong cùng assignment"))
            required_total = prev_total + max(0, cycle - prev_cycle)
        else:
            if history[:len(prev_history)] != prev_history or assignment in prev_history:
                problems.append(("routing-missing", "repair handoff thiếu assignment_history nối tiếp"))
            required_total = prev_total + cycle
        if total < required_total:
            problems.append(("routing-invalid", "total_repair_cycles giảm hoặc thiếu vòng sau handoff"))
    return problems


def routing_bundle_problems(records: list, applicability: dict) -> list[tuple[str, str]]:
    """Compare scanned records with a separately frozen applicability manifest."""
    if not isinstance(applicability, dict) or not _routing_json_equal(applicability.get("schema"), 1):
        return [("routing-manifest-invalid", "manifest phải là object schema=1")]
    tasks = applicability.get("tasks")
    policy_hash = applicability.get("policy_hash")
    if not isinstance(policy_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", policy_hash):
        return [("routing-manifest-invalid", "manifest thiếu policy_hash SHA-256")]
    candidate_hash = applicability.get("candidate_policy_hash")
    if candidate_hash is not None and (not isinstance(candidate_hash, str)
                                       or not re.fullmatch(r"[a-f0-9]{64}", candidate_hash)):
        return [("routing-manifest-invalid", "candidate_policy_hash phải là SHA-256 hoặc null")]
    if not isinstance(tasks, list) or not tasks:
        return [("routing-manifest-invalid", "manifest thiếu tasks")]
    required = ("task_ref", "document_refs", "required_classification_refs", "assignment_refs", "expected_attempt_refs")
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("task_ref"), str) or not _routing_safe_ref(task["task_ref"]):
            return [("routing-manifest-invalid", "task_ref của manifest không hợp lệ")]
        for key in required[1:]:
            values = task.get(key)
            if not isinstance(values, list) or not values or not all(isinstance(item, str) and _routing_safe_ref(item) for item in values):
                return [("routing-manifest-invalid", f"{task['task_ref']}: {key} thiếu/không hợp lệ")]
            if len(set(values)) != len(values):
                return [("routing-manifest-invalid", f"{task['task_ref']}: {key} trùng")]
    if len({task["task_ref"] for task in tasks}) != len(tasks):
        return [("routing-manifest-invalid", "task_ref trùng trong manifest")]
    coverage = applicability.get("source_coverage")
    if not isinstance(coverage, dict) or coverage.get("status") not in ("unknown", "partial", "complete"):
        return [("routing-manifest-invalid", "source_coverage sai hình/trạng thái")]
    ledger_refs, reconciliation_ref = coverage.get("ledger_refs"), coverage.get("reconciliation_ref")
    if (not isinstance(ledger_refs, list)
            or not all(isinstance(ref, str) and _routing_safe_ref(ref) for ref in ledger_refs)
            or len(set(ledger_refs)) != len(ledger_refs)
            or (reconciliation_ref is not None and
                (not isinstance(reconciliation_ref, str) or not _routing_safe_ref(reconciliation_ref)))):
        return [("routing-manifest-invalid", "source_coverage có reference sai kiểu/trùng/ngoài repo")]
    problems: list[tuple[str, str]] = []
    if coverage["status"] != "complete" or not ledger_refs or not reconciliation_ref:
        problems.append(("routing-missing", "source coverage/join chưa được reconcile; không thể tuyên bố đầy đủ"))
    tasks_by_ref = {task["task_ref"]: task for task in tasks}
    seen_records, seen_attempts, seen_assignments = set(), set(), set()
    valid_entries: list[dict] = []
    for entry in records:
        if (not isinstance(entry, dict) or not isinstance(entry.get("record"), dict)
                or not isinstance(entry.get("document_ref"), str) or not _routing_safe_ref(entry["document_ref"])):
            problems.append(("routing-invalid", "scanned record thiếu document_ref"))
            continue
        valid_entries.append(entry)
        record = entry["record"]
        record_policy_hash = record.get("policy_hash")
        if not isinstance(record_policy_hash, str) or record_policy_hash not in (policy_hash, candidate_hash):
            problems.append(("routing-invalid", f"{record.get('record_ref')}: policy_hash ngoài manifest"))
        if applicability.get("criteria_version") and record.get("criteria_version") != applicability["criteria_version"]:
            problems.append(("routing-invalid", f"{record.get('record_ref')}: criteria_version ngoài manifest"))
        record_ref = record.get("record_ref")
        if not isinstance(record_ref, str):
            problems.append(("routing-invalid", "record_ref không hợp lệ"))
            continue
        if record_ref in seen_records:
            problems.append(("routing-duplicate", f"record_ref trùng: {record_ref}"))
        seen_records.add(record_ref)
        task = tasks_by_ref.get(record.get("task_ref")) if isinstance(record.get("task_ref"), str) else None
        if task is None:
            problems.append(("routing-invalid", f"{record_ref}: task_ref ngoài manifest"))
        elif entry["document_ref"] not in task["document_refs"]:
            problems.append(("routing-invalid", f"{record_ref}: document_ref ngoài manifest task"))
        if record.get("record_kind") == "classification":
            if task is not None and record_ref not in task["required_classification_refs"]:
                problems.append(("routing-invalid", f"{record_ref}: classification ngoài manifest task"))
            assignment = record.get("assignment", {})
            assignment_ref = assignment.get("assignment_ref") if isinstance(assignment, dict) else None
            if not isinstance(assignment_ref, str):
                problems.append(("routing-invalid", "assignment_ref không hợp lệ"))
                continue
            if assignment_ref in seen_assignments:
                problems.append(("routing-duplicate", f"assignment_ref trùng: {assignment_ref}"))
            seen_assignments.add(assignment_ref)
            if task is not None and assignment_ref not in task["assignment_refs"]:
                problems.append(("routing-invalid", f"{assignment_ref}: assignment ngoài manifest task"))
        if record.get("record_kind") == "attempt":
            if task is not None and record_ref not in task["expected_attempt_refs"]:
                problems.append(("routing-invalid", f"{record_ref}: attempt ngoài manifest task"))
            identity = record.get("identity", {})
            attempt_ref = identity.get("attempt_id") if isinstance(identity, dict) else None
            if not isinstance(attempt_ref, str):
                problems.append(("routing-invalid", "attempt_id không hợp lệ"))
                continue
            if attempt_ref in seen_attempts:
                problems.append(("routing-duplicate", f"attempt_id trùng: {attempt_ref}"))
            seen_attempts.add(attempt_ref)
    for task in tasks:
        scoped = [entry for entry in valid_entries if isinstance(entry, dict) and isinstance(entry.get("record"), dict)
                  and entry["record"].get("task_ref") == task["task_ref"]]
        docs = {entry.get("document_ref") for entry in scoped}
        classifications = [entry["record"] for entry in scoped if entry["record"].get("record_kind") == "classification"]
        attempts = [entry["record"] for entry in scoped if entry["record"].get("record_kind") == "attempt"]
        observed = {
            "document_refs": docs,
            "required_classification_refs": {record.get("record_ref") for record in classifications
                                             if isinstance(record.get("record_ref"), str)},
            "assignment_refs": {record.get("assignment", {}).get("assignment_ref") for record in classifications
                                if isinstance(record.get("assignment"), dict)
                                and isinstance(record["assignment"].get("assignment_ref"), str)},
            "expected_attempt_refs": {record.get("record_ref") for record in attempts
                                      if isinstance(record.get("record_ref"), str)}
        }
        for key, actual in observed.items():
            missing = set(task[key]) - actual
            if missing:
                problems.append(("routing-missing", f"{task['task_ref']}: thiếu {key}: {', '.join(sorted(missing))}"))
        for record in attempts:
            identity = record.get("identity", {})
            assignment_ref = identity.get("assignment_ref") if isinstance(identity, dict) else None
            if not isinstance(assignment_ref, str) or not _routing_safe_ref(assignment_ref):
                problems.append(("routing-invalid", f"{task['task_ref']}: attempt assignment_ref không hợp lệ"))
            elif assignment_ref not in observed["assignment_refs"]:
                problems.append(("routing-missing", f"{task['task_ref']}: attempt thiếu assignment {assignment_ref}"))
            else:
                classification = next((item for item in classifications
                                       if isinstance(item.get("assignment"), dict)
                                       and item["assignment"].get("assignment_ref") == assignment_ref), None)
                if classification is not None:
                    problems.extend(_routing_assignment_join_problems(classification, record))
        work_items = {record.get("work_item_ref") for record in attempts
                      if isinstance(record.get("work_item_ref"), str)}
        for work_item in work_items:
            work_attempts = [record for record in attempts if record.get("work_item_ref") == work_item]
            problems.extend(_routing_counter_join_problems(work_attempts))
    return problems


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


def parse_moment(value) -> tuple | None:
    """`YYYY-MM-DD` hoặc `YYYY-MM-DD HH:MM +TZ` → (ngày như đã viết, thời điểm có múi giờ hoặc `None`); không đọc được → `None`."""
    m = MOMENT.fullmatch(value.strip()) if isinstance(value, str) else None
    if not m:
        return None
    try:
        day = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        if m.group(2) is None:
            return day, None
        offset = int(m.group(5)) * 60 + int(m.group(6) or 0)
        if m.group(4) == "-":
            offset = -offset
        return day, datetime(day.year, day.month, day.day, int(m.group(2)), int(m.group(3)),
                             tzinfo=timezone(timedelta(minutes=offset)))
    except ValueError:  # ngày không có thật, giờ ngoài 00:00–23:59, múi giờ ngoài ±24h
        return None


def moment_not_after(a: tuple, b: tuple) -> bool:
    """`a` không sau `b`: so thời điểm khi cả hai có giờ, không thì so ngày."""
    return a[1] <= b[1] if a[1] is not None and b[1] is not None else a[0] <= b[0]


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


def _tk_key(code: str) -> tuple:
    """`TK3.1` → `(3, 1)`: so theo bộ số nên việc con lớn hơn việc cha."""
    return tuple(int(x) for x in code[2:].split("."))


# --- Bộ máy kiểm ----------------------------------------------------------------------------------------


class Engine:
    def __init__(self, env=None):
        self.env = os.environ if env is None else env
        self.cache: dict = {}
        self.configs: dict = {}
        self.size_flagged: set = set()  # thư mục sprint bốn file đã báo `sprint-size-mismatch` (một lần mỗi thư mục)
        self.delegation_flagged: set = set()  # (tài liệu, khoá lạ) đã báo trong khối `delegation` (khối chung của hai cổng)
        self.report = Report()
        self.routing_records: list[tuple[dict, Path, int]] = []

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
        self.routing_rules(doc)
        if doc.kind is None or doc.fm is None:
            return
        self.frontmatter_rules(doc)
        self.size_rules(doc)
        self.heading_rules(doc)
        self.id_rules(doc)
        self.lead_rule(doc)
        if doc.kind in ("plan", "sprint"):
            self.trace_rule(doc)
            self.order_rules(doc)
        if doc.kind == "plan":
            self.plan_goal_rule(doc)
        if doc.kind in ("report", "sprint"):
            self.verification_rules(doc)

    def routing_rules(self, doc: Doc) -> None:
        """Read an explicit marker and its immediately following fenced JSON object."""
        lines = doc.raw
        in_fence = False
        for index, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("```") and stripped != "```json":
                in_fence = not in_fence
            elif stripped == "```json":
                in_fence = True
            if in_fence or stripped != ROUTING_MARKER:
                continue
            cursor = index + 1
            while cursor < len(lines) and not lines[cursor].strip():
                cursor += 1
            if cursor >= len(lines) or lines[cursor].strip() != "```json":
                self.add(doc.path, doc.line_no(index), "routing-invalid", "marker phải theo ngay bởi khối ```json")
                continue
            end = cursor + 1
            while end < len(lines) and lines[end].strip() != "```":
                end += 1
            if end >= len(lines):
                self.add(doc.path, doc.line_no(index), "routing-invalid", "khối routing JSON chưa đóng")
                continue
            try:
                record = json.loads("\n".join(lines[cursor + 1:end]), parse_constant=_routing_reject_constant)
            except ValueError as exc:
                message = exc.msg if isinstance(exc, json.JSONDecodeError) else str(exc)
                self.add(doc.path, doc.line_no(index), "routing-invalid", f"routing JSON sai cú pháp: {message}")
                continue
            if not isinstance(record, dict):
                self.add(doc.path, doc.line_no(index), "routing-invalid", "routing record phải là object")
                continue
            for rule, message in routing_record_problems(record, set()):
                self.add(doc.path, doc.line_no(index), rule, message)
            self.routing_records.append((record, doc.path, doc.line_no(index)))

    # -- luật chung cho mọi file Markdown --

    def general_rules(self, doc: Doc) -> None:
        parts = doc.path.resolve().parts
        skill_tests = any(parts[i] == "skills" and parts[i + 2] == "tests" for i in range(len(parts) - 2))
        severity_table = len(parts) >= 2 and parts[-2:] == ("method", "severity.md")
        level_columns: list = []
        vi_columns: list = []
        in_table = False
        for idx, line in enumerate(doc.masked):
            for m in BARE.finditer(line):
                if m.group(0) not in c.TIERS:
                    self.add(doc.path, doc.line_no(idx), "id-bare-single-letter",
                             f"mã trần '{m.group(0)}' — dùng tiền tố hai chữ cái đúng tài liệu hoặc viết bằng chữ" + doc.hint(idx, m.start(), m.group(0)))
            cells = c.table_cells(line)
            level_cells: list = []
            vi_cells: list = []
            if cells is None:
                in_table, level_columns, vi_columns = False, [], []
            elif not in_table:  # hàng tiêu đề: nhớ cột mức/severity
                in_table = True
                level_columns = [i for i, cell in enumerate(cells) if _is_level_header(cell)]
                vi_columns = [i for i, cell in enumerate(cells) if cell.strip("*_ ").casefold() in SEVERITY_HEADERS_VI]
            else:
                level_cells = [cells[i] for i in level_columns if i < len(cells)]
                vi_cells = [cells[i] for i in vi_columns if i < len(cells)]
            if not severity_table:
                self._old_scale(doc, idx, line, level_cells, vi_cells, quoting=skill_tests)
        if not skill_tests:
            for d in doc.defs:
                if prefix(d.code) not in c.OWNER:
                    self.add(doc.path, d.line, "id-unknown-prefix", f"'{d.code}' dùng tiền tố '{prefix(d.code)}' ngoài bảng mã")

    def _old_scale(self, doc: Doc, idx: int, line: str, cells: list, vi_cells: list = (), *, quoting: bool = False) -> None:
        """Nhãn thang cũ ở bốn chỗ: ô thuộc cột mức/severity của bảng; sau "Mức:"/"Severity:" trong dòng; nhãn kiểu
        nguồn trong câu (`CRITICAL`, `[HIGH]` đầu dòng, `confidence ≥ 80`). Chữ thường ngoài hai chỗ đầu không xét.
        `quoting` (file thử của skill chép nguyên văn đầu ra chủ thể thử): bỏ nhãn kiểu nguồn trong câu, giữ ô cột mức."""
        for cell in cells:
            bare = cell.strip("*_ ")
            if bare.casefold() in OLD_CELL or bare in OLD_CELL_UPPER:
                self._old_scale_hit(doc, idx, bare)
                return
        for cell in vi_cells:
            bare = cell.strip("*_ ")
            if bare.casefold() in OLD_CELL_VI:
                self._old_scale_hit(doc, idx, bare)
                return
        m = OLD_FIELD.search(line) or (None if quoting else OLD_SRC_BRACKET.search(line) or OLD_SRC_WORD.search(line))
        if m:
            self._old_scale_hit(doc, idx, m.group(1))
            return
        m = None if quoting else OLD_SRC_CONFIDENCE.search(line)
        if m:
            self._old_scale_hit(doc, idx, m.group(0), "ngưỡng điểm của nguồn")

    def _old_scale_hit(self, doc: Doc, idx: int, label: str, what: str = "nhãn thang cũ") -> None:
        self.add(doc.path, doc.line_no(idx), "old-scale-label",
                 f"{what} '{label}' — dùng Chặn / Phải sửa / Nên sửa / Ghi chú")

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
        for gate, kinds in (("gate_1", ("spec", "plan", "sprint")), ("gate_2", ("report", "sprint"))):
            mode = data.get(f"{gate}_mode")
            if kind in kinds and f"{gate}_mode" in data and not (isinstance(mode, str) and mode in GATE_MODES):
                bad(f"{gate}_mode", f"{gate}_mode: {mode!r} không thuộc {sorted(GATE_MODES)}")
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
        if doc.kind in ("spec", "plan", "sprint"):
            self._delegation(doc, "gate_1")
        if doc.kind in ("report", "sprint"):
            self._delegation(doc, "gate_2")

    def _delegation(self, doc: Doc, gate: str) -> None:
        """Cổng `delegated` đã kết luận phải có hồ sơ duyệt thay đủ (SPEC 7.3); báo lỗi đầu tiên của cổng rồi dừng.
        Cổng `delegated` còn mở (chưa kết luận) chỉ bị kiểm khoá lạ trong khối `delegation`.
        Vắng `gate_N_mode` hoặc `human` → không kiểm gì (hồ sơ cũ giữ nguyên kết quả)."""
        data, path = doc.data, doc.path
        mode_key, quote_key = f"{gate}_mode", f"{gate}_quote"
        done = data.get(gate) not in (None, "pending")
        if data.get(mode_key, "human") == "human":  # vắng mode = human: lời/khối duyệt thay mà không khai mode là cách né kiểm
            quote = data.get(f"{gate}_quote")
            if isinstance(quote, str) and quote.lstrip().casefold().startswith(DELEGATION_QUOTE):
                self.add(path, doc.key_line(f"{gate}_quote"), "gate-delegation-invalid",
                         f"{gate}_quote bắt đầu '{DELEGATION_QUOTE}' mà {mode_key} không phải delegated")
            elif done and "delegation" in data and "delegated" not in (data.get("gate_1_mode"), data.get("gate_2_mode")):
                self.add(path, doc.key_line("delegation"), "gate-delegation-invalid",
                         f"có khối delegation và {gate} đã kết luận mà {mode_key} không phải delegated")
            return
        if data.get(mode_key) != "delegated":
            return
        if not done:  # cổng còn mở: chỉ khoá lạ trong khối (khối vắng/không phải dict/rỗng giữ nguyên, không báo)
            if isinstance(data.get("delegation"), dict):
                self._unknown_delegation_key(doc, mode_key)
            return

        def bad(key: str, message: str) -> None:
            self.add(path, doc.key_line(key), "gate-delegation-invalid", f"{mode_key}: delegated — {message}")

        block = data.get("delegation")
        if not isinstance(block, dict) or not block:
            return bad("delegation" if "delegation" in data else mode_key,
                       "thiếu khối delegation (lời cấp, phạm vi, hạn, người duyệt)")
        if self._unknown_delegation_key(doc, mode_key):
            return
        grant = block.get("grant")
        if not (isinstance(grant, str) and grant.strip()):
            return bad("delegation.grant" if "grant" in block else "delegation", "thiếu lời cấp nguyên văn (delegation.grant)")
        gate_at = None
        if data.get(f"{gate}_at") not in (None, ""):
            gate_at = parse_moment(data[f"{gate}_at"])
            if gate_at is None:
                return bad(f"{gate}_at", f"{gate}_at: {data[f'{gate}_at']!r} không đọc được (YYYY-MM-DD hoặc YYYY-MM-DD HH:MM +TZ)")
        grant_at = parse_moment(block.get("grant_at"))
        if grant_at is None:
            return bad("delegation.grant_at" if "grant_at" in block else "delegation",
                       f"delegation.grant_at: {block.get('grant_at')!r} thiếu hoặc không đọc được")
        if gate_at is not None and not moment_not_after(grant_at, gate_at):
            return bad("delegation.grant_at", f"lời cấp ({block['grant_at']}) sau thời điểm cổng ({data[f'{gate}_at']})")
        scope = block.get("scope")
        if not isinstance(scope, list) or gate not in scope:
            return bad("delegation.scope" if "scope" in block else "delegation", f"phạm vi {scope!r} không chứa {gate}")
        expires = block.get("expires")
        if expires != "sprint_end":
            until = parse_moment(expires) if isinstance(expires, str) and DATE.fullmatch(expires) else None
            if until is None:
                return bad("delegation.expires" if "expires" in block else "delegation",
                           f"delegation.expires: {expires!r} phải là sprint_end hoặc ngày YYYY-MM-DD")
            if gate_at is not None and until[0] < gate_at[0]:
                return bad("delegation.expires", f"quá hạn: hạn {expires} trước ngày cổng")
        if block.get("tier") != "T1":
            return bad("delegation.tier" if "tier" in block else "delegation", f"người duyệt thay phải là T1, đang là {block.get('tier')!r}")
        by = block.get("by")
        if not isinstance(by, str) or not by.strip() or by == "pending":
            return bad("delegation.by" if "by" in block else "delegation", "delegation.by phải là nhãn agent đã giao (khác rỗng, khác pending)")
        roles = data.get("roles")
        held = sorted(r for r, v in roles.items()
                      if r in EXECUTORS and isinstance(v, list) and len(v) >= 2 and v[1] == by) if isinstance(roles, dict) else []
        if held:
            self.add(path, doc.key_line("delegation.by"), "self-review",
                     f"người duyệt thay '{by}' cũng giữ vai thực thi ({', '.join(held)}) của cùng tài liệu")
        elif doc.kind in ("plan", "report", "sprint"):  # SPEC không đòi: Cổng 1 duyệt thay ghi ở cả SPEC lẫn PLAN (DN5)
            if not isinstance(roles, dict):
                return bad("roles" if "roles" in data else mode_key, "tài liệu duyệt thay phải có khối roles để đối chiếu delegation.by")
            mine = {r: v for r, v in roles.items() if isinstance(v, list) and len(v) >= 2 and v[1] == by}
            if not mine:
                return bad("delegation.by", f"người duyệt thay '{by}' không giữ vai nào trong roles của tài liệu")
            tiers = [v[0] for r, v in mine.items() if r in VERIFIERS or re.fullmatch(r"[a-z]+-specialist", r)]
            if "T1" not in tiers:
                if not tiers:
                    return bad("delegation.by", f"người duyệt thay '{by}' không giữ vai kiểm định nào trong roles của tài liệu")
                return bad("delegation.by", f"người duyệt thay '{by}' giữ vai kiểm định nhưng tier là {', '.join(map(str, tiers))}, phải là T1")
        files = block.get("files", [])
        if not isinstance(files, list):
            return bad("delegation.files", f"delegation.files: {files!r} phải là danh sách")
        revoked = block.get("revoked_at")
        if revoked not in (None, ""):
            revoked_at = parse_moment(revoked)
            if revoked_at is None:
                return bad("delegation.revoked_at", f"delegation.revoked_at: {revoked!r} không đọc được")
            if gate_at is not None:  # ngày không giờ: trùng ngày cổng thì coi là đã thu hồi (an toàn khi không chắc)
                timed = revoked_at[1] is not None and gate_at[1] is not None
                if revoked_at[1] <= gate_at[1] if timed else revoked_at[0] <= gate_at[0]:
                    return bad("delegation.revoked_at", f"đã thu hồi ({revoked}) không sau thời điểm cổng ({data[f'{gate}_at']})")
        quote = data.get(quote_key)
        if not (isinstance(quote, str) and quote.startswith(DELEGATION_QUOTE)):
            return bad(quote_key, f"{quote_key} phải bắt đầu bằng '{DELEGATION_QUOTE}'")
        if doc.kind in ("plan", "report", "sprint"):
            missing = self._record_gaps(doc)
            if missing is not None:
                return bad(mode_key, missing)
        tags = data.get("risk_tags")
        if not (isinstance(tags, list) and all(isinstance(t, str) for t in tags)):
            return bad("risk_tags" if "risk_tags" in data else mode_key,
                       "risk_tags thiếu hoặc không phải danh sách chuỗi — duyệt thay cần khai nhãn rủi ro (dùng [] khi không có)")
        tags = set(tags)
        if tags & DELEGATION_FORBIDDEN_TAGS:
            return bad("risk_tags", f"risk_tags có {', '.join(sorted(tags & DELEGATION_FORBIDDEN_TAGS))} — vùng cấm duyệt thay")
        if "rules" in tags and not files:
            return bad("delegation.files", "risk_tags có rules mà delegation.files rỗng — file luật phải nêu đích danh trong lời cấp")

    def _unknown_delegation_key(self, doc: Doc, mode_key: str) -> bool:
        """Khối `delegation` có khoá ngoài bảng không; có thì báo một lần cho mỗi (tài liệu, khoá lạ) — khối là CHUNG của
        hai cổng nên lần gọi của cổng kia không báo lặp. Trả `True` khi có khoá lạ (người gọi dừng, kể cả khi đã báo)."""
        unknown = [k for k in doc.data["delegation"] if k not in DELEGATION_KEYS]
        if not unknown:
            return False
        flag = (doc.path.resolve(), unknown[0])
        if flag not in self.delegation_flagged:
            self.delegation_flagged.add(flag)
            self.add(doc.path, doc.key_line(f"delegation.{unknown[0]}"), "gate-delegation-invalid",
                     f"{mode_key}: delegated — delegation.{unknown[0]} ngoài bảng khoá {list(DELEGATION_KEYS)}")
        return True

    def _record_gaps(self, doc: Doc) -> str | None:
        """Mục `## Bản ghi duyệt thay` có đủ ba nhãn không; `None` = đủ, ngược lại = lời mô tả chỗ thiếu."""
        start = end = None
        for idx, line in enumerate(doc.masked):
            if not line.startswith("## "):
                continue
            if start is not None:
                end = idx
                break
            if DELEGATION_RECORD.casefold() in NUMBERING.sub("", doc.raw[idx][3:].strip()).casefold():
                start = idx
        if start is None:
            return f"thiếu mục '## {DELEGATION_RECORD}'"
        body = [re.sub(r"^[-*\s]+", "", line).replace("**", "") for line in doc.masked[start + 1:end]]
        missing = [label for label in DELEGATION_LABELS if not any(line.startswith(label) for line in body)]
        return f"mục '{DELEGATION_RECORD}' thiếu nhãn {', '.join(missing)}" if missing else None

    # -- hình tài liệu theo cỡ --

    def size_rules(self, doc: Doc) -> None:
        """`size × doc`: `SPRINT.md` chỉ ở cỡ rất nhỏ/nhỏ; bốn file chỉ từ cỡ nhỏ trở lên. Thiếu/sai `size` đã có luật khác."""
        size = doc.data.get("size")
        if not isinstance(size, str):
            return
        if doc.kind == "sprint" and size in ("medium", "large"):
            self.add(doc.path, doc.key_line("size"), "sprint-size-mismatch",
                     f"SPRINT.md ở cỡ {size} — cỡ vừa/lớn dùng bốn file SPEC · PLAN · PROGRESS · REPORT (method/sizing.md)")
        elif doc.kind in ("spec", "plan", "progress", "report") and size == "tiny":
            folder = doc.path.resolve().parent
            if folder not in self.size_flagged:
                self.size_flagged.add(folder)
                self.add(doc.path, doc.key_line("size"), "sprint-size-mismatch",
                         "cỡ rất nhỏ dùng một file SPRINT.md, không dựng bốn file (method/sizing.md); nâng cỡ lên nhỏ nếu giữ bốn file")

    def required_headings(self, doc: Doc, headings: list) -> tuple:
        """Tiêu đề bắt buộc; `SPRINT.md` cỡ rất nhỏ (hoặc cỡ chưa rõ) nhận hai phần "Kế hoạch" · "Kết quả" hoặc bốn phần cũ
        (nhận ra bốn phần khi có tiêu đề **bắt đầu** bằng SPEC/PLAN/PROGRESS, không phải chỉ chứa chữ đó)."""
        if doc.kind != "sprint":
            return REQUIRED_HEADINGS[doc.kind]
        size = doc.data.get("size")
        if size in ("small", "medium", "large"):
            return SPRINT_FOUR
        four_part = any(h.startswith(w.casefold()) for w in SPRINT_FOUR[:3] for h in headings)  # bắt đầu bằng SPEC/PLAN/PROGRESS (đã bỏ số thứ tự)
        return SPRINT_FOUR if four_part else SPRINT_TINY_HEADINGS

    # -- tiêu đề --

    def heading_rules(self, doc: Doc) -> None:
        h1 = next((doc.line_no(i) for i, line in enumerate(doc.masked) if line.startswith("# ")), doc.start)
        headings = []
        first_h2 = len(doc.raw)
        for idx, line in enumerate(doc.masked):
            if line.startswith("## "):
                first_h2 = min(first_h2, idx)
                headings.append(NUMBERING.sub("", doc.raw[idx][3:].strip()).casefold())
        for phrase in self.required_headings(doc, headings):
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

    def order_rules(self, doc: Doc) -> None:
        """Số `TK` là thứ tự làm: `Đầu vào:` chỉ trỏ số nhỏ hơn (`task-order`); số cấp một liền 1…N (`task-gap`)."""
        heads = [d for d in doc.defs if prefix(d.code) == "TK" and d.position == "heading"]
        previous = 0
        for d in heads:
            if "." in d.code:
                continue
            number = _tk_key(d.code)[0]
            if number != previous + 1:
                self.add(doc.path, d.line, "task-gap", f"{d.code} đứng sau TK{previous} — số TK cấp một phải liền 1…N" if previous else f"{d.code} là việc cấp một đầu tiên — số đầu phải là TK1")
            previous = number
        for i, d in enumerate(heads):
            end = heads[i + 1].line - doc.start if i + 1 < len(heads) else len(doc.masked)
            field = self._input_field(doc, d.line - doc.start + 1, end)
            if field is None:
                continue
            line, text = field
            own = _tk_key(d.code)
            seen = set()
            for code in codes_on(re.split(re.escape(PARALLEL_MARK), text, maxsplit=1, flags=re.I)[0]):
                if prefix(code) == "TK" and code not in seen and _tk_key(code) >= own:
                    seen.add(code)
                    self.add(doc.path, line, "task-order", f"{d.code} trỏ {code} ở Đầu vào — số TK phải là thứ tự làm")

    def _input_field(self, doc: Doc, begin: int, end: int):
        """Mục danh sách `**Đầu vào:**` trong phần [begin, end) của một việc: (dòng, chữ) tới `**Đầu ra:**` hoặc hết mục."""
        for idx in range(begin, end):
            line = doc.masked[idx]
            if HEADING.match(line):
                break
            m = re.match(r"^(\s*)(?:[-*+]|[0-9]+\.)\s+" + re.escape(INPUT_FIELD), line)
            if not m:
                continue
            parts = [line[m.end():]]
            for nxt in doc.masked[idx + 1:end]:
                if not nxt.strip():
                    continue
                if len(nxt) - len(nxt.lstrip()) <= len(m.group(1)) or HEADING.match(nxt):
                    break
                parts.append(nxt)
            return doc.line_no(idx), " ".join(parts).split(OUTPUT_FIELD)[0]
        return None

    def plan_goal_rule(self, doc: Doc) -> None:
        """Mục `## Mục tiêu` của PLAN có đủ ba dòng nhãn của mẫu (SPEC 7.8)."""
        start = next((i for i, line in enumerate(doc.masked) if re.match(r"^##\s+Mục tiêu\s*$", line)), None)
        if start is None:
            return  # thiếu tiêu đề đã có `heading-missing`
        lines = []
        for line in doc.masked[start + 1:]:
            if re.match(r"^#{1,2}\s", line):
                break
            lines.append(re.sub(r"^\s*(?:[-*+]\s+)?(?:\*\*)?", "", line))
        for label in PLAN_GOAL_LABELS:
            if not any(x.startswith(label) for x in lines):
                self.add(doc.path, doc.line_no(start), "plan-goal-block", f"mục Mục tiêu thiếu dòng nhãn '{label}' (mẫu PLAN)")

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
        if not problems:  # cấu hình sai hình thì không đối chiếu sổ (như `index`/`init` dừng ở `config_problems`)
            self.check_ledger(root, cfg, path)

    # -- sổ tập trung (FR8) --

    def check_ledger(self, root: Path, cfg: dict, config_path: Path) -> None:
        """Chỉ chạy khi dự án khai `ledger.project`; không khai thì 0 phát hiện dù máy có đặt mẫu đường."""
        project = c.ledger_project(cfg)
        if project is None:
            return
        pattern = self.env.get(c.LEDGER_ENV, "")
        if not pattern:
            self.add(config_path, 1, "ledger-unconfigured",
                     f"dự án khai ledger.project '{project}' nhưng máy chưa đặt {c.LEDGER_ENV} — chưa đối chiếu được sổ tập trung")
            return
        ledger = c.ledger_path(pattern, project)
        if ledger is None:
            self.add(config_path, 1, "config-invalid", f"{c.LEDGER_ENV} phải chứa {{project}} (nơi thay tên dự án)")
            return
        rows = self._ledger_rows(ledger, config_path)
        if rows is None:
            return
        for sprint_id, doc in self._ledger_sprints(root, cfg):
            status, updated = doc.data.get("status"), doc.data.get("updated")
            row = rows.get(sprint_id)
            if row is None:
                if status not in ("done", "dropped"):
                    self.add(doc.path, doc.key_line("status"), "ledger-missing-row",
                             f"{sprint_id} đang '{status}' mà sổ tập trung chưa có dòng (method/process.md mục 11)")
                continue
            row_status, row_date = row
            if row_status != status:
                self.add(doc.path, doc.key_line("status"), "ledger-stale",
                         f"{sprint_id}: sổ ghi trạng thái '{row_status}', hồ sơ ghi '{status}'")
            if not DATE.fullmatch(row_date):
                self.add(doc.path, doc.key_line("updated"), "ledger-stale",
                         f"{sprint_id}: ngày trong sổ '{row_date}' không phải YYYY-MM-DD")
            elif isinstance(updated, str) and DATE.fullmatch(updated) and row_date < updated:
                self.add(doc.path, doc.key_line("updated"), "ledger-stale",
                         f"{sprint_id}: sổ ghi ngày {row_date}, hồ sơ cập nhật {updated}")

    def _ledger_rows(self, ledger: Path, config_path: Path):
        """`{mã sprint: (trạng thái, ngày)}` từ bảng có cột đầu "Sprint" (dòng đầu thắng); lỗi → báo và trả `None`."""
        try:
            text = c.read_text(ledger)
        except (OSError, UnicodeDecodeError) as exc:
            kind = "không tồn tại" if not ledger.exists() else f"không đọc được dạng UTF-8 ({type(exc).__name__})"
            self.add(config_path, 1, "ledger-unreadable", f"file sổ {kind}: {ledger.name}")
            return None
        rows: dict = {}
        found = in_table = False
        for line in c.mask_markdown(text.split("\n")):
            cells = c.table_cells(line)
            if cells is None:
                in_table = False
            elif not in_table:
                in_table = cells[0].strip("*_ ").casefold() == "sprint"
                found = found or in_table
            elif not c.is_separator_row(cells) and len(cells) >= 3:
                key = cells[0].strip("*_` ")
                if c.parse_id(key) is not None:
                    rows.setdefault(key, (cells[1].strip("*_` "), cells[2].strip("*_` ")))
        if not found:
            self.add(config_path, 1, "ledger-unreadable",
                     f"file sổ {ledger.name} không có bảng cột đầu 'Sprint' (mẫu: templates/registry/LEDGER.md)")
            return None
        return rows

    def _ledger_sprints(self, root: Path, cfg: dict) -> list:
        """Sprint của dự án: thư mục khớp `paths.sprint_dir` (như `index.py`), PROGRESS.md hoặc SPRINT.md có mã `SPR-`.
        Bản chép mẫu nằm chỗ khác trong repo không bị đòi dòng sổ."""
        base = c.artifact_path(root, cfg, "")
        found = []
        if not base.is_dir():
            return found
        pattern = cfg["paths"]["sprint_dir"].replace("{date}", "*").replace("{slug}", "*")
        for folder in sorted(p for p in base.glob(pattern) if p.is_dir()):
            for name in ("PROGRESS.md", "SPRINT.md"):
                path = folder / name
                if not path.is_file():
                    continue
                doc = self.doc(path)
                sprint = doc.data.get("sprint") if doc is not None and doc.kind in ("progress", "sprint") else None
                if isinstance(sprint, str) and (c.parse_id(sprint) or ("", 0))[0] == "SPR":
                    found.append((sprint, doc))
                break  # như index.py: PROGRESS.md trước, không có thì SPRINT.md
        return found


# --- Quét đường dẫn ------------------------------------------------------------------------------------


def _has_sprint_document(folder: Path) -> bool:
    """`folder` có FILE mang đúng tên tài liệu sprint, so đúng hoa/thường như trên Linux (`spec.md` thì không)?"""
    try:
        names = os.listdir(folder)
    except OSError:
        return False
    return any(name in SPRINT_DOC_NAMES and (folder / name).is_file() for name in names)


def _under_sprint_evidence(root: Path, rel: tuple, beside: dict) -> bool:
    """`rel` đi qua một thư mục `evidence` nằm cạnh tài liệu sprint (FR4.1)? `root` không bao giờ tính (FR4.2)."""
    for index, part in enumerate(rel):
        if part != EVIDENCE_DIR:
            continue
        parent = root.joinpath(*rel[:index])
        if parent not in beside:
            beside[parent] = _has_sprint_document(parent)
        if beside[parent]:
            return True
    return False


def _walk(root: Path, pattern: str, include_evidence: bool = False):
    beside: dict = {}
    for path in sorted(root.rglob(pattern)):
        rel = path.relative_to(root).parts[:-1]
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel):
            continue
        if not include_evidence and _under_sprint_evidence(root, rel, beside):
            continue
        yield path


def check_paths(paths, env=None, routing_manifest=None, include_evidence: bool = False) -> Report:
    engine = Engine(env)
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for config in _walk(path, c.CONFIG_NAME, include_evidence):
                engine.check_config(config.parent)
            for md in _walk(path, "*.md", include_evidence):
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
    if routing_manifest is not None:
        manifest_path = Path(routing_manifest)
        try:
            manifest = json.loads(c.read_text(manifest_path), parse_constant=_routing_reject_constant)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            engine.add(manifest_path, 1, "routing-manifest-invalid", f"không đọc/parse được manifest ({exc})")
        else:
            scanned = [Path(raw) for raw in paths]
            base = scanned[0] if len(scanned) == 1 and scanned[0].is_dir() else Path(os.path.commonpath(
                [str(path if path.is_dir() else path.parent) for path in scanned]))
            records = [{"record": record, "document_ref": path.resolve().relative_to(base.resolve()).as_posix()}
                       for record, path, _ in engine.routing_records if path.resolve().is_relative_to(base.resolve())]
            for rule, message in routing_bundle_problems(records, manifest):
                engine.add(manifest_path, 1, rule, message)
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
    "rtk-ai", "oraios", "mksglu", "microsoft", "firelex",
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
    parser.add_argument("--routing-manifest", help="manifest applicability độc lập của pilot routing")
    parser.add_argument("--include-evidence", action="store_true",
                        help="khi quét thư mục: quét cả thư mục evidence/ nằm cạnh tài liệu sprint (mặc định bỏ qua)")
    args = parser.parse_args(argv)
    if not args.self_mode and not args.paths:
        parser.error("cần ít nhất một đường dẫn, hoặc --self")
    if args.self_mode and args.paths:
        parser.error("--self không nhận đường dẫn; dùng --root <repo> để chọn repo")
    if args.self_mode and args.include_evidence:
        parser.error("--include-evidence chỉ dùng khi quét đường dẫn; --self không đổi")
    if args.self_mode and args.routing_manifest:
        parser.error("--routing-manifest chỉ dùng khi kiểm đường dẫn pilot")
    if args.self_mode:
        value = env.get("AGENT_AGILE_DENYLIST", "")
        report = run_self(Path(args.root), Path(value) if value else None)
        if report.denylist_status == "NOT_CONFIGURED":
            print("WARNING NOT_CONFIGURED: AGENT_AGILE_DENYLIST chưa đặt, file không đọc được hoặc rỗng — "
                  "luật leak-denylist Chưa chạy (không phải Đạt).", file=sys.stderr)
    else:
        report = check_paths(args.paths, env, routing_manifest=args.routing_manifest,
                             include_evidence=args.include_evidence)
    for error in report.errors:
        print(f"{error} [lỗi đầu vào]")
    for finding in report.findings:
        print(finding.render())
    print(summary(report))
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
