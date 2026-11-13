"""SPR-20 TK22: autopilot chỉ còn MỘT chế độ. Không còn `mode`, `exclusions`, `-secure`, cờ `+chặn-…`/`+nhánh`/`+đẩy-nhánh` ở
`scripts/_autopilot_rules.py`; khối `delegation` kiểu cũ không phụ thuộc chúng.

Giữ tên file cũ (TK2/TK3 của bản 1) để lịch sử test đọc được một mạch; nội dung đã viết lại theo ngữ nghĩa một chế độ.
"""

from __future__ import annotations

import re

import pytest

import _autopilot_rules as rules

GRANT = "Bật autopilot cổng 1+2 cho SPR-9 tới hết sprint, trần 30 phiên."


def block(**fields) -> dict:
    base = {"grant": GRANT, "grant_at": "2026-11-13 08:30 +07", "scope": ["gate_1", "gate_2"], "expires": "sprint_end",
            "by": "agent-d", "tier": "T1", "files": [], "revoked_at": None, "level": "gate_1_2",
            "channel": "chat", "orchestrator": "agent-orch", "sessions_cap": None}
    base.update(fields)
    return base


@pytest.mark.parametrize("name", ["AUTOPILOT_MODES", "AUTOPILOT_SECURE_SUFFIX", "AUTOPILOT_BLOCK_FLAGS", "compute_mode", "_grant_parts"])
def test_two_mode_machinery_is_gone(name):
    assert not hasattr(rules, name), f"{name} thuộc chế độ chặt/mở, đã gỡ ở TK22"


def test_mode_and_exclusions_are_not_delegation_keys():
    assert "mode" not in rules.DELEGATION_OPTIONAL_KEYS and "exclusions" not in rules.DELEGATION_OPTIONAL_KEYS
    assert "ruleset_checked" not in rules.DELEGATION_OPTIONAL_KEYS


def test_effective_date_is_still_a_date():
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", rules.MODE_OPEN_EFFECTIVE_DATE)  # check.py dùng làm ngày hiệu lực của luật sprint mới


def test_block_without_mode_or_exclusions_is_valid():
    assert rules.autopilot_problem(block()) is None


@pytest.mark.parametrize("grant,level,scope", [
    ("Bật autopilot cổng 1 cho SPR-9.", "gate_1", ["gate_1"]),
    ("Bật autopilot cổng 1+2 cho SPR-9.", "gate_1_2", ["gate_1", "gate_2"]),
    ("BẬT AUTOPILOT cổng 1+2 cho SPR-9 +nhánh.", "gate_1_2", ["gate_1", "gate_2"]),  # hậu tố cũ chỉ là chữ trong lời, không có nghĩa
])
def test_grant_text_matches_level(grant, level, scope):
    assert rules.autopilot_problem(block(grant=grant, level=level, scope=scope)) is None


def test_grant_level_word_must_match_level():
    problem = rules.autopilot_problem(block(grant="Bật autopilot cổng 1 cho SPR-9."))  # lời nói cổng 1, level gate_1_2
    assert problem and problem[0] == "delegation.level"


def test_level_gate_1_2_needs_both_gates_in_scope():
    problem = rules.autopilot_problem(block(scope=["gate_2"]))
    assert problem and problem[0] == "delegation.scope"


@pytest.mark.parametrize("missing", ["level", "expires"])
def test_required_keys(missing):
    problem = rules.autopilot_problem(block(**{missing: None}))
    assert problem and missing in problem[0]


def test_old_grant_at_is_not_an_autopilot_error_anymore():
    """Chỉ còn một chế độ nên không có ngày bắt đầu riêng cho 'chế độ mở': `grant_at` cũ do kiểm cổng chung xử lý."""
    assert rules.autopilot_problem(block(grant_at="2020-01-01 08:30 +07")) is None


def test_orchestrator_cannot_sign():
    problem = rules.autopilot_problem(block(orchestrator="agent-d"))
    assert problem and problem[0] == "delegation.orchestrator"


# --- ca `check` trên cây hồ sơ ------------------------------------------------------------------------------------

import check  # noqa: E402
from test_check import _rewrite, autopilot_plan, make_sprint  # noqa: E402

SENTENCE = '"Mở SPR-03, gồm sửa file luật {file}, trần 30 phiên."'


def _plan(tmp_path, **fields):
    root = make_sprint(tmp_path)
    base = dict(level="gate_1_2", scope="[gate_1, gate_2]", grant_at='"2026-11-13 08:30 +07"')
    base.update(fields)
    autopilot_plan(root, **base)
    _rewrite(root / "PLAN.md", "gate_1_at: 2026-02-01 09:00 +07", "gate_1_at: 2026-11-13 09:00 +07")
    return root


def _rules_hit(root):
    return sorted({f.rule for f in check.check_paths([root]).findings if f.rule.startswith(("delegation-", "gate-delegation"))})


def test_sentence_naming_a_non_floor_file_is_clean(tmp_path):
    root = _plan(tmp_path, files="[method/task-routing.md]", grant=SENTENCE.format(file="method/task-routing.md"))
    assert _rules_hit(root) == []


def test_sentence_naming_a_floor_file_is_flagged(tmp_path):
    root = _plan(tmp_path, files="[scripts/autopilot_guard.py]", grant=SENTENCE.format(file="scripts/autopilot_guard.py"))
    assert _rules_hit(root) == ["delegation-floor-file"]


def test_sentence_files_must_be_in_the_sentence(tmp_path):
    root = _plan(tmp_path, files="[method/task-routing.md]", grant=SENTENCE.format(file="method/other.md"))
    assert _rules_hit(root) == ["gate-delegation-invalid"]


def test_zone_only_file_is_not_a_floor_file_for_the_delegation_rule(tmp_path):
    """File chỉ có VÙNG sàn (`method/sizing.md`) do `floor_check` và `gate-route-floor` giữ, không phải `delegation-floor-file`."""
    root = _plan(tmp_path, files="[method/sizing.md]", grant=SENTENCE.format(file="method/sizing.md"))
    assert "delegation-floor-file" not in _rules_hit(root)


@pytest.mark.parametrize("key,value", [("mode", "open"), ("mode", "secure")])
def test_leftover_mode_key_is_reported_as_unknown(tmp_path, key, value):
    """Khoá `mode` đã gỡ khỏi bảng khoá: khối mới có nó là khoá lạ (Phải sửa)."""
    root = _plan(tmp_path, **{key: value})
    assert _rules_hit(root) == ["gate-delegation-invalid"]
