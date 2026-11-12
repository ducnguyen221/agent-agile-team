"""SPR-20 TK6: định tuyến cổng, người quyết, `check` cổng `pending`, một người ghi (FR6.1-FR6.3, FR7.3, FR7.5, FR4.3, SC6, SC10).

Đặt ở file riêng (không nối vào `tests/test_check.py`); mượn helper dựng hồ sơ từ đó như `tests/test_autopilot_modes.py`.
"""

from __future__ import annotations

import pytest

import check
from conftest import write_lf
from test_check import AUTOPILOT_FIXTURES, _rewrite, delegate_plan, make_sprint

FLOOR_TABLE = """
## File luật và file sàn cứng sẽ chạm

PLAN khai các file luật dưới đây:

| File (★ = sàn cứng) | Vùng / dòng | Việc |
|---|---|---|
| {cell} | toàn file | TK1 |
"""


def _pending_delegated(tmp_path, *, tags: str = "[]", files: str = "[]", table_file: str | None = None):
    """PLAN Cổng 1 `delegated` nhưng còn `pending` (chưa kết luận), tuỳ chọn có bảng file luật."""
    root = make_sprint(tmp_path)
    delegate_plan(root)
    path = root / "PLAN.md"
    _rewrite(path, "gate_1: approved\ngate_1_at: 2026-02-01 09:00 +07\n", "gate_1: pending\ngate_1_at: null\n")
    _rewrite(path, 'gate_1_quote: "duyệt thay: chọn phương án a — xem mục Bản ghi duyệt thay"', "gate_1_quote: null")
    _rewrite(path, "status: approved", "status: draft")
    _rewrite(path, "risk_tags: []", f"risk_tags: {tags}")
    if files != "[]":
        _rewrite(path, "  files: []\n", f"  files: {files}\n")
    if tags != "[]":
        _rewrite(path, "risk: normal", "risk: high")
        _rewrite(path, "size: medium", "size: large")
    if table_file is not None:
        write_lf(path, path.read_text(encoding="utf-8") + FLOOR_TABLE.format(cell=f"★ `{table_file}`"))
    return root


def _hits(root, rule: str):
    return [f for f in check.check_paths([root], env={}).findings if f.rule == rule]


def test_baseline_pending_delegated_plan_is_clean(tmp_path):
    root = _pending_delegated(tmp_path)
    assert [f.render() for f in check.check_paths([root], env={}).findings] == []


def test_pending_delegated_floor_flags_must_fix(tmp_path):
    root = _pending_delegated(tmp_path, table_file="hooks/hooks.json")
    findings = check.check_paths([root], env={}).findings
    assert sorted(f.rule for f in findings) == ["gate-route-floor"], [f.render() for f in findings]
    assert findings[0].level == "Phải sửa" and "chuyển cổng người" in findings[0].message


def test_zone_file_in_table_flags_too(tmp_path):
    assert len(_hits(_pending_delegated(tmp_path, table_file="AGENTS.md"), "gate-route-floor")) == 1


def test_floor_table_without_delegation_stays_clean(tmp_path):
    root = _pending_delegated(tmp_path, table_file="hooks/hooks.json")
    _rewrite(root / "PLAN.md", "gate_1_mode: delegated", "gate_1_mode: human")
    assert _hits(root, "gate-route-floor") == []


def test_non_floor_file_in_table_is_clean(tmp_path):
    assert _hits(_pending_delegated(tmp_path, table_file="method/task-routing.md"), "gate-route-floor") == []


def test_rules_empty_files_flags_while_pending(tmp_path):
    root = _pending_delegated(tmp_path, tags="[rules]")
    hits = _hits(root, "gate-route-floor")
    assert len(hits) == 1 and "delegation.files" in hits[0].message, [f.render() for f in check.check_paths([root], env={}).findings]


def test_rules_with_named_files_is_clean_while_pending(tmp_path):
    root = _pending_delegated(tmp_path, tags="[rules]", files="[method/task-routing.md]")
    assert _hits(root, "gate-route-floor") == []


def test_duplicate_delegation_key_flags(tmp_path):
    root = _pending_delegated(tmp_path)
    path = root / "PLAN.md"
    _rewrite(path, "roles:\n", 'delegation:\n  grant: "bản thứ hai"\nroles:\n')
    findings = check.check_paths([root], env={}).findings
    assert [f.rule for f in findings] == ["frontmatter-duplicate-key"], [f.render() for f in findings]
    assert findings[0].level == "Phải sửa" and "delegation" in findings[0].message


def test_old_sprint_no_new_findings():
    findings = check.check_paths([AUTOPILOT_FIXTURES / "legacy-delegation"], env={}).findings
    new = {"gate-route-floor", "decision-owner-missing", "frontmatter-duplicate-key", "protected-repos-unconfigured"}
    assert not [f.render() for f in findings if f.rule in new]


# --- người quyết của CQ/DN (FR7.3) ------------------------------------------------------------------------------

DN_NO_OWNER = """
## Quyết định cần người

PLAN có 1 **decision** (DN) cần người dùng quyết:

| Mã | Câu hỏi | Lựa chọn | Khuyến nghị | Trạng thái |
|---|---|---|---|---|
| DN1 (chỉ mục) | Thêm chỉ mục? | (a) có · (b) không | (b) | mở |
"""
DN_WITH_OWNER = DN_NO_OWNER.replace("| Trạng thái |", "| Người quyết · trạng thái |").replace("| mở |", "| Analyst · mở |")


def _with_decisions(tmp_path, table: str, created: str):
    root = make_sprint(tmp_path)
    path = root / "PLAN.md"
    _rewrite(path, "created: 2026-02-01", f"created: {created}")
    write_lf(path, path.read_text(encoding="utf-8") + table)
    return root


def test_decision_owner_missing_flags_new_sprint(tmp_path):
    hits = _hits(_with_decisions(tmp_path, DN_NO_OWNER, "2026-11-13"), "decision-owner-missing")
    assert len(hits) == 1 and hits[0].level == "Nên sửa" and "DN1" in hits[0].message


def test_decision_owner_present_is_clean(tmp_path):
    assert _hits(_with_decisions(tmp_path, DN_WITH_OWNER, "2026-11-13"), "decision-owner-missing") == []


def test_decision_owner_not_required_for_old_sprint(tmp_path):
    assert _hits(_with_decisions(tmp_path, DN_NO_OWNER, "2026-11-12"), "decision-owner-missing") == []


# --- biến AGENT_AGILE_PROTECTED_REPOS vắng (FR4.3) -------------------------------------------------------------

def _open_sprint(tmp_path):
    root = _pending_delegated(tmp_path)
    _rewrite(root / "PLAN.md", "  revoked_at: null\n", "  revoked_at: null\n  mode: open\n  level: gate_1\n  exclusions: [network_fetch, rules_unlisted, irreversible_delete, secret, auth, user_soul, license]\n  channel: chat\n  orchestrator: agent-orch\n  sessions_cap: null\n")
    return root


def test_protected_repos_note_when_open_and_variable_missing(tmp_path):
    root = _open_sprint(tmp_path)
    hits = [f for f in check.check_paths([root], env={}).findings if f.rule == "protected-repos-unconfigured"]
    assert len(hits) == 1 and hits[0].level == "Ghi chú"
    set_env = check.check_paths([root], env={"AGENT_AGILE_PROTECTED_REPOS": "x=full"}).findings
    assert not [f for f in set_env if f.rule == "protected-repos-unconfigured"]


def test_protected_repos_note_silent_for_secure_sprint(tmp_path):
    root = _pending_delegated(tmp_path)
    assert not [f for f in check.check_paths([root], env={}).findings if f.rule == "protected-repos-unconfigured"]
