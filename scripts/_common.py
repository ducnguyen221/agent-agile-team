"""Thư viện chung cho `init`, `check`, `index` — chỉ dùng thư viện chuẩn.

- Đọc frontmatter theo **tập con YAML** của `templates/README.md` mục 2; ngoài tập con → `SubsetError`
  có số dòng của file, không đoán.
- Che code span, khối code và comment HTML trong Markdown (giữ nguyên số dòng và độ dài dòng) để các luật
  về mã không bắt nhầm ví dụ được trích.
- Đọc `.agile.json` (mục 7) và gộp với giá trị mặc định.

Không chạy trực tiếp.
"""

from __future__ import annotations

import copy
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "templates"
CONFIG_NAME = ".agile.json"

DEFAULT_CONFIG: dict = {
    "schema": 1,
    "visibility": "private",
    "artifact_root": ".",
    "paths": {
        "requests": "docs/plans/REQUESTS.md",
        "sprints": "docs/plans/SPRINTS.md",
        "sprint_dir": "docs/plans/{date}-{slug}",
        "specs": "docs/specs/SPECS.md",
        "feature_specs_dir": "docs/specs",
        "adr_dir": "docs/architecture/adr",
    },
    "id_width": {"request": 3, "feature": 3, "sprint": 2},
    "coverage": {"line_min_percent": 80, "reason": ""},
}

# Mã mục: tiền tố → loại tài liệu sở hữu (`templates/README.md` mục 5).
OWNER = {
    "US": "spec", "FR": "spec", "SC": "spec", "CQ": "spec",
    "TK": "plan", "RK": "plan", "DN": "plan",
    "BR": "progress",
    "VR": "report", "RF": "report", "LN": "report", "CO": "report",
}
TIERS = ("T1", "T2", "T3")


class SubsetError(Exception):
    """Frontmatter nằm ngoài tập con YAML. `line` là số dòng (đếm từ 1) trong file."""

    def __init__(self, line: int, message: str):
        super().__init__(f"line {line}: {message}")
        self.line = line
        self.message = message


class ConfigError(Exception):
    """`.agile.json` thiếu hoặc không đọc được."""


@dataclass
class Frontmatter:
    data: dict
    lines: dict = field(default_factory=dict)  # khoá ("a" hoặc "a.b") → số dòng trong file
    end_line: int = 0  # dòng `---` đóng khối
    body_start: int = 0  # dòng đầu tiên của thân


# --- Đọc file ------------------------------------------------------------------------------------------


def read_text(path: Path) -> str:
    """Đọc UTF-8, bỏ BOM, chuẩn hoá xuống dòng về LF."""
    text = Path(path).read_text(encoding="utf-8")
    return normalize(text)


def normalize(text: str) -> str:
    if text.startswith("﻿"):
        text = text[1:]
    return text.replace("\r\n", "\n").replace("\r", "\n")


def utf8_stdio() -> None:
    """Console Windows mặc định không phải UTF-8; nhãn mức tiếng Việt phải in được."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


# --- Tập con YAML ----------------------------------------------------------------------------------------

_KEY = re.compile(r"[a-z][a-z0-9_-]*")
_INT = re.compile(r"-?[0-9]+")
_FORBIDDEN_START = {
    "|": "multi-line string (| or >) is not supported",
    ">": "multi-line string (| or >) is not supported",
    "'": "single quote is not supported; use double quotes",
    "{": "inline map {} is not supported",
    "&": "anchor, alias or tag is not supported",
    "*": "anchor, alias or tag is not supported",
    "!": "anchor, alias or tag is not supported",
    "%": "reserved character at start of value; use double quotes",
    "@": "reserved character at start of value; use double quotes",
    "`": "reserved character at start of value; use double quotes",
}


def parse_frontmatter(text: str) -> Frontmatter | None:
    """Trả `None` nếu dòng đầu không phải `---`. Ngoài tập con → `SubsetError`."""
    lines = normalize(text).split("\n")
    if not lines or lines[0].rstrip() != "---":
        return None
    for idx in range(1, len(lines)):
        if lines[idx].rstrip() == "---":
            data, key_lines = parse_subset(lines[1:idx], first_line=2)
            return Frontmatter(data=data, lines=key_lines, end_line=idx + 1, body_start=idx + 2)
    raise SubsetError(1, "frontmatter opened with --- but never closed")


def parse_subset(lines: list[str], first_line: int = 1) -> tuple[dict, dict]:
    data: dict = {}
    key_lines: dict = {}
    parent: str | None = None  # khoá gốc đang mở khối lồng
    for offset, raw in enumerate(lines):
        no = first_line + offset
        if "\t" in raw:
            raise SubsetError(no, "tab character is not allowed")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        content = raw[indent:]
        if content.startswith("- ") or content == "-":
            raise SubsetError(no, "block list '- item' is not supported; use an inline list [a, b] or a one-level map")
        if indent == 0:
            key, value, is_block = _pair(content, no)
            if key in data:
                raise SubsetError(no, f"duplicate key '{key}'")
            key_lines[key] = no
            if is_block:
                data[key] = None  # khoá rỗng không có dòng con = null
                parent = key
            else:
                data[key] = value
                parent = None
        elif indent == 2:
            if parent is None:
                raise SubsetError(no, "indented line without a parent block (parent key must have an empty value)")
            key, value, is_block = _pair(content, no)
            if is_block:
                raise SubsetError(no, "nesting deeper than one level is not supported")
            if data[parent] is None:
                data[parent] = {}
            if key in data[parent]:
                raise SubsetError(no, f"duplicate key '{parent}.{key}'")
            key_lines[f"{parent}.{key}"] = no
            data[parent][key] = value
        else:
            raise SubsetError(no, f"indent must be 0 or exactly 2 spaces (found {indent}); one level only")
    return data, key_lines


def _pair(content: str, no: int):
    m = _KEY.match(content)
    if not m or content[m.end():m.end() + 1] != ":":
        raise SubsetError(no, "expected 'key: value' with key matching [a-z][a-z0-9_-]*")
    key = m.group(0)
    rest = content[m.end() + 1:]
    if rest and not rest.startswith(" "):
        raise SubsetError(no, "expected a space after ':' (bad key or 'key:value')")
    value_text = _strip_comment(rest).strip()
    if value_text == "":
        return key, None, True
    return key, _scalar_or_list(value_text, no), False


def _strip_comment(text: str) -> str:
    in_quote = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_quote and ch == "\\":
            i += 2
            continue
        if ch == '"':
            in_quote = not in_quote
        elif ch == "#" and not in_quote and (i == 0 or text[i - 1] == " "):
            return text[:i]
        i += 1
    return text


def _scalar_or_list(text: str, no: int):
    if text.startswith("["):
        return _inline_list(text, no)
    return _scalar(text, no, in_list=False)


def _scalar(text: str, no: int, in_list: bool):
    if text.startswith('"'):
        value, end = _quoted(text, 0, no)
        if text[end:].strip():
            raise SubsetError(no, "unexpected text after closing double quote")
        return value
    first = text[0]
    if first in _FORBIDDEN_START:
        raise SubsetError(no, _FORBIDDEN_START[first])
    if text.startswith("- "):
        raise SubsetError(no, "block list '- item' is not supported")
    if text == "null":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if _INT.fullmatch(text):
        return int(text)
    if ": " in text or text.endswith(":"):
        raise SubsetError(no, "plain value contains ': '; wrap it in double quotes")
    if in_list and any(ch in text for ch in ",[]"):
        raise SubsetError(no, "inline list item contains , [ or ]; wrap it in double quotes")
    return text


def _quoted(text: str, start: int, no: int) -> tuple[str, int]:
    """Đọc chuỗi nháy kép bắt đầu ở `start`; trả (giá trị, vị trí sau dấu nháy đóng)."""
    out = []
    i = start + 1
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            nxt = text[i + 1:i + 2]
            if nxt not in ('"', "\\"):
                raise SubsetError(no, "only the escapes \\\" and \\\\ are supported in double quotes")
            out.append(nxt)
            i += 2
            continue
        if ch == '"':
            return "".join(out), i + 1
        out.append(ch)
        i += 1
    raise SubsetError(no, "double quote is not closed on the same line")


def _inline_list(text: str, no: int) -> list:
    if not text.endswith("]"):
        raise SubsetError(no, "inline list must close with ] at the end of the line")
    inner = text[1:-1]
    if not inner.strip():
        return []
    items: list = []
    i = 0
    while True:
        while i < len(inner) and inner[i] == " ":
            i += 1
        if i < len(inner) and inner[i] == '"':
            value, i = _quoted(inner, i, no)
            items.append(value)
            while i < len(inner) and inner[i] == " ":
                i += 1
            if i < len(inner) and inner[i] != ",":
                raise SubsetError(no, "inline list item: unexpected text after closing quote")
        else:
            j = inner.find(",", i)
            raw = inner[i:] if j == -1 else inner[i:j]
            raw = raw.strip()
            if not raw:
                raise SubsetError(no, "inline list has an empty item")
            if raw.startswith("["):
                raise SubsetError(no, "nested inline list is not supported")
            items.append(_scalar(raw, no, in_list=True))
            i = len(inner) if j == -1 else j
        if i >= len(inner):
            return items
        i += 1  # bỏ dấu phẩy
        if not inner[i:].strip():
            raise SubsetError(no, "inline list has an empty item")


# --- Markdown ------------------------------------------------------------------------------------------


def body_lines(text: str) -> tuple[int, list[str]]:
    """Trả (số dòng đầu của thân, các dòng thân). Frontmatter hỏng thì coi cả file là thân."""
    lines = normalize(text).split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if lines and lines[0].rstrip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].rstrip() == "---":
                return idx + 2, lines[idx + 1:]
    return 1, lines


_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def mask_markdown(lines: list[str]) -> list[str]:
    """Thay nội dung khối code, code span và comment HTML bằng dấu cách; giữ số dòng và độ dài dòng."""
    out: list[str] = []
    fence: str | None = None
    in_comment = False
    for line in lines:
        if fence is not None:
            m = _FENCE.match(line)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not line[m.end():].strip():
                fence = None
            out.append(" " * len(line))
            continue
        if not in_comment:
            m = _FENCE.match(line)
            if m:
                fence = m.group(1)
                out.append(" " * len(line))
                continue
        masked, in_comment = _mask_inline(line, in_comment)
        out.append(masked)
    return out


def _mask_inline(line: str, in_comment: bool) -> tuple[str, bool]:
    chars = list(line)
    i = 0
    n = len(line)
    while i < n:
        if in_comment:
            end = line.find("-->", i)
            stop = n if end == -1 else end + 3
            for k in range(i, stop):
                chars[k] = " "
            if end == -1:
                return "".join(chars), True
            in_comment = False
            i = stop
            continue
        if line.startswith("<!--", i):
            in_comment = True
            continue
        if line[i] == "`":
            run = i
            while run < n and line[run] == "`":
                run += 1
            width = run - i
            close = _find_run(line, run, width)
            if close == -1:
                i = run  # dấu huyền lẻ là chữ thường
                continue
            for k in range(i, close + width):
                chars[k] = " "
            i = close + width
            continue
        i += 1
    return "".join(chars), in_comment


def _find_run(line: str, start: int, width: int) -> int:
    i = start
    n = len(line)
    while i < n:
        if line[i] == "`":
            run = i
            while run < n and line[run] == "`":
                run += 1
            if run - i == width:
                return i
            i = run
            continue
        i += 1
    return -1


def table_cells(line: str) -> list[str] | None:
    """Ô của một dòng bảng Markdown (đã che mã); không phải dòng bảng → `None`."""
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    inner = stripped[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    cells = re.split(r"(?<!\\)\|", inner)
    return [cell.strip() for cell in cells]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


# --- Mã hồ sơ sổ gốc -------------------------------------------------------------------------------------

_RECORD = re.compile(r"(RQ|FS|SPR)-([0-9]+)")


def format_id(prefix: str, number: int, width: int) -> str:
    return f"{prefix}-{number:0{width}d}"


def parse_id(text) -> tuple[str, int] | None:
    if not isinstance(text, str):
        return None
    m = _RECORD.fullmatch(text.strip())
    return (m.group(1), int(m.group(2))) if m else None


# --- Cấu hình dự án --------------------------------------------------------------------------------------


def load_config(root: Path) -> dict:
    path = Path(root) / CONFIG_NAME
    if not path.is_file():
        raise ConfigError(f"{path}: missing {CONFIG_NAME} (run init.py first)")
    try:
        raw = json.loads(read_text(path))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfigError(f"{path}: cannot read {CONFIG_NAME}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: top level must be a JSON object")
    return merge_config(raw)


def merge_config(raw: dict) -> dict:
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    for key, value in raw.items():
        if isinstance(value, dict) and isinstance(cfg.get(key), dict):
            cfg[key].update(value)
        else:
            cfg[key] = value
    return cfg


def artifact_path(root: Path, cfg: dict, rel: str) -> Path:
    """Đường dẫn trong `paths` (trừ `adr_dir`) tính theo `artifact_root`."""
    base = Path(cfg.get("artifact_root") or ".")
    if not base.is_absolute():
        base = Path(root) / base
    return base / rel


def display(path: Path) -> str:
    """Đường dẫn để in: tương đối theo thư mục hiện tại nếu được, dấu `/`."""
    path = Path(path)
    try:
        path = path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        pass
    return path.as_posix()
