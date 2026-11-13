"""SPR-20 TK8: hai tin dừng, bản tin autopilot (FR7.2, FR7.4, SC10).

Hai luật mới của `check`: `report-missing-ask-count` (Nên sửa) và `conditional-pass-merged-main` (Phải sửa).
Đặt ở file riêng; mượn helper dựng hồ sơ từ `tests/test_check.py`.
"""

from __future__ import annotations

import check
from conftest import write_lf
from test_check import _rewrite, make_sprint

ASK_LINE = "- **Số lượt Đức phải trả lời:** 1 (Cổng 1); không tính hộp xác nhận của rào máy."

BULLETIN = """
## Bản tin autopilot

- Cổng 1 · Đạt · Gate Delegate agent-g · `evidence/gate-1-verdict.md`
{ask}
- **Đã đẩy / PR:** không đẩy.
- **Commit gộp:** {merged}
"""


def _report(tmp_path, *, created: str, bulletin: str | None = None, conditional: bool = False):
    root = make_sprint(tmp_path)
    path = root / "REPORT.md"
    _rewrite(path, "created: 2026-02-02", f"created: {created}")
    if conditional:
        _rewrite(path, "gate_2: pending\ngate_2_at: null\ngate_2_quote: null\n",
                 'gate_2: conditional_pass\ngate_2_at: 2026-11-13 17:00 +07\ngate_2_quote: "Đạt có điều kiện, ghi CO1"\n')
        _rewrite(path, "verdict: pass", "verdict: conditional_pass")
    if bulletin is not None:
        write_lf(path, path.read_text(encoding="utf-8") + bulletin)
    return root


def _hits(root, rule: str):
    return [f for f in check.check_paths([root], env={}).findings if f.rule == rule]


def test_report_missing_ask_count_flags(tmp_path):
    root = _report(tmp_path, created="2026-11-13")
    hits = _hits(root, "report-missing-ask-count")
    assert len(hits) == 1 and hits[0].level == "Nên sửa" and "số lượt Đức phải trả lời" in hits[0].message


def test_report_ask_count_present_is_clean(tmp_path):
    root = _report(tmp_path, created="2026-11-13", bulletin=BULLETIN.format(ask=ASK_LINE, merged="không có."))
    assert _hits(root, "report-missing-ask-count") == []


def test_report_ask_count_in_comment_does_not_count(tmp_path):
    root = _report(tmp_path, created="2026-11-13", bulletin="\n<!-- Số lượt Đức phải trả lời: 2 -->\n")
    assert len(_hits(root, "report-missing-ask-count")) == 1


def test_report_ask_count_needs_a_number(tmp_path):
    root = _report(tmp_path, created="2026-11-13", bulletin="\n- Số lượt Đức phải trả lời: <điền số>\n")
    assert len(_hits(root, "report-missing-ask-count")) == 1


def test_report_ask_count_not_required_for_old_sprint(tmp_path):
    assert _hits(_report(tmp_path, created="2026-11-12"), "report-missing-ask-count") == []


def test_conditional_pass_merged_main_flags(tmp_path):
    bulletin = BULLETIN.format(ask=ASK_LINE, merged="đã gộp nhánh sprint vào `main` (abc1234).")
    root = _report(tmp_path, created="2026-11-13", bulletin=bulletin, conditional=True)
    hits = _hits(root, "conditional-pass-merged-main")
    assert len(hits) == 1 and hits[0].level == "Phải sửa"


def test_conditional_pass_merged_by_sha_line_flags(tmp_path):
    bulletin = BULLETIN.format(ask=ASK_LINE, merged="`3f2a9c1d` vào `main`")
    root = _report(tmp_path, created="2026-11-13", bulletin=bulletin, conditional=True)
    assert len(_hits(root, "conditional-pass-merged-main")) == 1


def test_conditional_pass_not_merged_is_clean(tmp_path):
    bulletin = BULLETIN.format(ask=ASK_LINE, merged="không có — Đạt có điều kiện nên nhánh chờ người gộp.")
    root = _report(tmp_path, created="2026-11-13", bulletin=bulletin, conditional=True)
    assert _hits(root, "conditional-pass-merged-main") == []
    bulletin = BULLETIN.format(ask=ASK_LINE, merged="chưa gộp vào `main`.")
    assert _hits(_report(tmp_path / "b", created="2026-11-13", bulletin=bulletin, conditional=True), "conditional-pass-merged-main") == []


def test_pass_merged_main_is_clean(tmp_path):
    bulletin = BULLETIN.format(ask=ASK_LINE, merged="đã gộp nhánh sprint vào `main` (abc1234).")
    root = _report(tmp_path, created="2026-11-13", bulletin=bulletin)
    assert _hits(root, "conditional-pass-merged-main") == []


def test_conditional_pass_merged_outside_bulletin_is_clean(tmp_path):
    """Hồ sơ cũ do người duyệt gộp (không có bản tin autopilot) ghi "đã gộp vào main" ở chỗ khác: không đỏ."""
    root = _report(tmp_path, created="2026-10-24", bulletin="\n## 9. Ghi chú\n\nNhánh mã đã gộp vào `main` theo chỉ thị của người dùng.\n", conditional=True)
    assert _hits(root, "conditional-pass-merged-main") == []


def test_conditional_pass_merged_in_sprint_inline_bulletin_flags(tmp_path):
    """SPRINT.md ghi bản tin thành một dòng mục nhỏ: dòng đó cũng được soi."""
    root = _report(tmp_path, created="2026-11-13", bulletin="\n- **Bản tin autopilot:** đã gộp nhánh vào `main`.\n", conditional=True)
    assert len(_hits(root, "conditional-pass-merged-main")) == 1


def test_conditional_pass_merged_main_applies_to_old_sprint(tmp_path):
    """Lưới bắt RK5 không phụ thuộc ngày: hồ sơ cũ mà tự khai đã gộp `main` khi Đạt có điều kiện vẫn đỏ."""
    bulletin = BULLETIN.format(ask=ASK_LINE, merged="đã gộp vào `main`.")
    root = _report(tmp_path, created="2026-11-12", bulletin=bulletin, conditional=True)
    assert len(_hits(root, "conditional-pass-merged-main")) == 1
