"""Bảng tier mẫu schema 2 và ma trận vai × vendor mẫu: hình dạng, thang 1–5, khớp thẻ vai."""

from __future__ import annotations

import json
import re
from pathlib import Path

from conftest import REPO
import check

ROOT = REPO
EXAMPLE = ROOT / "tiers" / "tiers.example.json"
MATRIX = ROOT / "tiers" / "ROLE-MATRIX.example.md"
HARNESSES = ("claude", "codex", "antigravity")
MATRIX_COLUMNS = ("Vai", "Tier", "Vendor", "Model", "Effort", "Effort native", "Ghi chú")
ROLE_NAMES = {
    "analyst": "Analyst",
    "architect": "Architect",
    "implementer": "Implementer",
    "qa": "QA",
    "researcher": "Researcher",
    "business-reviewer": "Business Reviewer",
    "tech-reviewer": "Tech Reviewer",
}


def _load() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def _card_tier(role: str) -> str:
    """Tier ghi ở dòng `tier: Tn` trong frontmatter của thẻ `roles/**/<role>.md`."""
    card = next((ROOT / "roles").rglob(f"{role}.md"))
    for line in card.read_text(encoding="utf-8").splitlines()[1:12]:
        match = re.fullmatch(r"tier:\s*(T[123])\s*", line)
        if match:
            return match.group(1)
    raise AssertionError(f"thẻ {card} không có dòng tier")


def _effort_values(data: dict) -> list:
    """Mọi ô effort trong bảng (tier và vai), mở khối `{harness: số}` thành từng số."""
    values: list = []
    cells = [t.get("effort") for t in data["tiers"].values()]
    cells += [r.get("effort") for r in data.get("roles", {}).values()]
    for cell in cells:
        if cell is None:
            continue
        values.extend(cell.values() if isinstance(cell, dict) else [cell])
    return values


def _model_cells(data: dict) -> list:
    """Mọi ô model trong bảng (tier và vai)."""
    cells: list = []
    for entry in list(data["tiers"].values()) + list(data.get("roles", {}).values()):
        cells.extend(entry.get("models", {}).values())
    return cells


def _split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _matrix_header(path: Path) -> tuple[str, ...]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return tuple(_split_row(next(line for line in lines if line.startswith("|"))))


def _matrix_rows(path: Path) -> list[dict]:
    """Hàng của bảng đầu tiên trong file ma trận, mỗi hàng là dict theo tên cột."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("|"))
    header = _split_row(lines[start])
    rows: list[dict] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        rows.append(dict(zip(header, _split_row(line))))
    return rows


def test_example_declares_schema_2():
    data = _load()
    assert data["schema"] == 2


def test_example_models_are_placeholders():
    data = _load()
    assert all(v == "<model-id>" for v in _model_cells(data))


def test_example_effort_levels_in_1_to_5():
    data = _load()
    assert all(isinstance(x, int) and 1 <= x <= 5 for x in _effort_values(data))
    assert all(set(data["effort_scale"][h]) == {"1", "2", "3", "4", "5"} for h in HARNESSES)


def test_example_effort_scale_fallback():
    data = _load()
    assert data["fallback"] == {"antigravity": "clamp_to_max"}
    assert data["effort_scale"]["antigravity"]["4"] is None


def test_example_roles_are_known_role_keys():
    data = _load()
    assert data["roles"], "roles rỗng"
    assert set(data["roles"]) <= check.EXECUTORS | check.VERIFIERS


def test_example_role_tiers_match_cards():
    data = _load()
    assert all(v["tier"] == _card_tier(k) for k, v in data["roles"].items())


def test_role_matrix_example_shape():
    assert _matrix_header(MATRIX) == MATRIX_COLUMNS
    rows = _matrix_rows(MATRIX)
    roles = check.EXECUTORS | check.VERIFIERS
    assert len(rows) == len(roles) * 3
    pairs = {(r["Vai"], r["Vendor"]) for r in rows}
    assert len(pairs) == len(rows)
    assert pairs == {(ROLE_NAMES[r], h) for r in roles for h in HARNESSES}
    assert all(r["Model"] == "`<model-id>`" for r in rows)


def test_role_matrix_example_tiers_match_cards():
    names = {v: k for k, v in ROLE_NAMES.items()}
    assert all(r["Tier"] == _card_tier(names[r["Vai"]]) for r in _matrix_rows(MATRIX))
