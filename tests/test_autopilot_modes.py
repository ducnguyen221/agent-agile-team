"""SPR-20 TK2: chế độ mở/secure của autopilot (FR1, SC1, SC8). RED trước TK3: `compute_mode`, `OPEN_*`,
`AUTOPILOT_MODES`, `MODE_OPEN_EFFECTIVE_DATE` chưa có ở `scripts/_autopilot_rules.py`.

Đặt ở file riêng (không nối vào `tests/test_check.py` 2 600+ dòng) để nhóm test chế độ đọc được một mạch.
"""

from __future__ import annotations

import re

import pytest

import _autopilot_rules as rules

OPEN_GRANT = "Bật autopilot cổng 1+2 cho SPR-9 tới hết sprint, trần 30 phiên."
SECURE_GRANT = "Bật autopilot-secure cổng 1+2 cho SPR-9 tới hết sprint, trần 30 phiên."
OPEN_ALWAYS = {"network_fetch", "rules_unlisted", "irreversible_delete", "secret", "auth", "user_soul", "license"}
OPEN_DEFAULT = {"push", "branch_merge_local", "version", "main_merge", "tag", "publish"}


def open_block(**fields) -> dict:
    block = {"grant": OPEN_GRANT, "grant_at": "2099-01-01 08:30 +07", "scope": ["gate_1", "gate_2"], "expires": "sprint_end",
             "by": "agent-d", "tier": "T1", "files": [], "revoked_at": None, "level": "gate_1_2", "mode": "open",
             "exclusions": sorted(OPEN_ALWAYS), "channel": "chat", "orchestrator": "agent-orch", "sessions_cap": None}
    block.update(fields)
    return block


def test_open_sets_are_seven_and_six():
    assert set(rules.OPEN_ALWAYS_BLOCKED) == OPEN_ALWAYS and len(rules.OPEN_ALWAYS_BLOCKED) == 7
    assert set(rules.OPEN_DEFAULT_OPEN) == OPEN_DEFAULT and len(rules.OPEN_DEFAULT_OPEN) == 6
    assert set(rules.OPEN_ALWAYS_BLOCKED) | set(rules.OPEN_DEFAULT_OPEN) == set(rules.AUTOPILOT_EXCLUSIONS)
    assert rules.AUTOPILOT_MODES == ("open", "secure")
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", rules.MODE_OPEN_EFFECTIVE_DATE)


def test_open_mode_blocks_seven():
    assert rules.compute_mode(OPEN_GRANT) == ("open", frozenset(rules.OPEN_ALWAYS_BLOCKED))


def test_block_flags_add():
    mode, excl = rules.compute_mode(OPEN_GRANT[:-1] + " +chặn-tag +chặn-phát-hành.")
    assert mode == "open" and len(excl) == 9 and {"tag", "publish"} <= excl and set(rules.OPEN_ALWAYS_BLOCKED) <= excl


@pytest.mark.parametrize("flag,item", [("+chặn-push", "push"), ("+chặn-nhánh", "branch_merge_local"), ("+chặn-version", "version"),
                                       ("+chặn-gộp-chính", "main_merge"), ("+chặn-tag", "tag"), ("+chặn-phát-hành", "publish")])
def test_each_block_flag_maps_to_one_item(flag, item):
    assert rules.compute_mode(OPEN_GRANT[:-1] + f" {flag}.")[1] == frozenset(rules.OPEN_ALWAYS_BLOCKED) | {item}


def test_secure_keeps_13():
    mode, excl = rules.compute_mode(SECURE_GRANT)
    assert mode == "secure" and excl == frozenset(rules.AUTOPILOT_EXCLUSIONS) and len(excl) == 13


def test_secure_suffix_level_and_push_flag():
    mode, excl = rules.compute_mode("Bật autopilot-secure cổng 1+2 cho SPR-9 +đẩy-nhánh.")
    assert mode == "secure" and "push" not in excl and len(excl) == 12
    secure = open_block(grant=SECURE_GRANT, mode="secure", exclusions=sorted(rules.AUTOPILOT_EXCLUSIONS))
    assert rules.autopilot_problem(secure) is None  # `-secure` được bóc trước khi so chữ mức với `level`


def test_gate1_is_secure():
    assert rules.compute_mode("Bật autopilot cổng 1 cho SPR-9.") == ("secure", frozenset(rules.AUTOPILOT_EXCLUSIONS))


@pytest.mark.parametrize("grant", [OPEN_GRANT[:-1] + " +nhánh.", OPEN_GRANT[:-1] + " +chặn-lạ.", OPEN_GRANT[:-1] + " +đẩy-nhánh."])
def test_bad_open_grants_are_refused(grant):
    with pytest.raises(ValueError):
        rules.compute_mode(grant)


def test_legacy_no_mode_is_secure():
    legacy = open_block()
    legacy.pop("mode")
    problem = rules.autopilot_problem(legacy)  # vắng `mode` = secure: bảy mục là thiếu sáu mục bắt buộc
    assert problem and problem[0] == "delegation.exclusions" and "thiếu mục bắt buộc" in problem[1]


def test_open_block_valid_and_old_grant_at_invalid():
    assert rules.autopilot_problem(open_block()) is None
    problem = rules.autopilot_problem(open_block(grant_at="2020-01-01 08:30 +07"))
    assert problem and problem[0] == "delegation.grant_at"


def test_open_mode_needs_gate_two_even_when_the_grant_has_no_command_prefix():
    """Soát RF1: lời cấp không bắt đầu bằng 'Bật autopilot' không được lách điều kiện Cổng 2 của chế độ mở."""
    block = open_block(grant="duyệt thay Cổng 1 cho SPR-9", level="gate_1", scope=["gate_1"])
    problem = rules.autopilot_problem(block)
    assert problem and problem[0] == "delegation.level" and "gate_1_2" in problem[1]
    assert rules.autopilot_problem(open_block(grant="Mở SPR-9, trần 30 phiên.")) is None


def test_exclusions_superset_ok():
    assert rules.autopilot_problem(open_block(exclusions=sorted(OPEN_ALWAYS | {"tag"}))) is None


@pytest.mark.parametrize("removed", sorted(OPEN_ALWAYS))
def test_exclusions_missing_always_blocked_red(removed):
    problem = rules.autopilot_problem(open_block(exclusions=sorted(OPEN_ALWAYS - {removed})))
    assert problem and problem[0] == "delegation.exclusions" and removed in problem[1]


# --- ca `check` trên cây hồ sơ (TK3): câu mở sprint, file luật, hồ sơ cũ ---------------------------------------------

import check  # noqa: E402
from test_check import _rewrite, autopilot_plan, make_sprint  # noqa: E402

OPEN_EXCL = "[" + ", ".join(sorted(OPEN_ALWAYS)) + "]"
OPEN_SENTENCE = '"Mở SPR-03, gồm sửa file luật {file}, trần 30 phiên."'


def _open_plan(tmp_path, **fields):
    root = make_sprint(tmp_path)
    base = dict(mode="open", level="gate_1_2", scope="[gate_1, gate_2]", exclusions=OPEN_EXCL, grant_at='"2026-11-13 08:30 +07"')
    base.update(fields)
    autopilot_plan(root, **base)
    _rewrite(root / "PLAN.md", "gate_1_at: 2026-02-01 09:00 +07", "gate_1_at: 2026-11-13 09:00 +07")  # sau ngày hiệu lực của chế độ mở
    return root


def _rules_hit(root):
    return sorted({f.rule for f in check.check_paths([root]).findings if f.rule.startswith(("delegation-", "gate-delegation"))})


def test_open_sentence_naming_a_non_floor_file_is_clean(tmp_path):
    root = _open_plan(tmp_path, files="[method/task-routing.md]", grant=OPEN_SENTENCE.format(file="method/task-routing.md"))
    assert _rules_hit(root) == []


@pytest.mark.parametrize("floor_file", ["AGENTS.md", "method/process.md", "scripts/git_fence.py"])
def test_open_sentence_naming_a_floor_or_zone_file_is_flagged(tmp_path, floor_file):
    root = _open_plan(tmp_path, files=f"[{floor_file}]", grant=OPEN_SENTENCE.format(file=floor_file))
    assert _rules_hit(root) == ["delegation-fence-file"]


def test_open_sentence_files_must_be_in_the_sentence(tmp_path):
    root = _open_plan(tmp_path, files="[method/task-routing.md]", grant=OPEN_SENTENCE.format(file="method/other.md"))
    assert _rules_hit(root) == ["gate-delegation-invalid"]


def test_open_block_before_effective_date_is_invalid(tmp_path):
    root = _open_plan(tmp_path, grant_at='"2026-02-01 08:30 +07"')
    assert _rules_hit(root) == ["gate-delegation-invalid"]


def test_secure_zone_file_stays_as_before(tmp_path):
    """SC8: khối không `mode: open` giữ kết quả cũ — file chỉ có vùng sàn không bị `delegation-fence-file`."""
    root = make_sprint(tmp_path)
    autopilot_plan(root, files="[method/sizing.md]", grant='"Bật autopilot cổng 1 cho SPR-03, gồm method/sizing.md."')
    assert "delegation-fence-file" not in _rules_hit(root)
