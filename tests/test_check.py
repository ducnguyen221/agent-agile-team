"""`check.py` trên tài liệu sprint: bộ sạch thoát 0, mỗi ca hỏng cố ý bị bắt đúng mã luật (SC4)."""

import json
import os
import re
import shutil
from pathlib import Path

import pytest

from conftest import FIXTURES, LEDGER_ENV, REPO, run_script, write_lf
import check

VALID = FIXTURES / "valid"
CASES = json.loads((FIXTURES / "broken.json").read_text(encoding="utf-8"))["cases"]
SELF_ONLY = {"leak-denylist", "agents-md-budget"}


def make_sprint(tmp_path: Path) -> Path:
    root = tmp_path / "sprint"
    shutil.copytree(VALID, root)
    return root


def apply_case(root: Path, case: dict) -> None:
    if "replace" in case:
        target = root / case.get("target", case["file"])
        old, new = case["replace"]
        text = target.read_text(encoding="utf-8")
        assert old in text, f"ca {case['rule']}: không thấy chuỗi cần thay trong {target.name}"
        write_lf(target, text.replace(old, new, 1))
    for rel, content in case.get("write", {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        write_lf(path, content)


def rules_of(report) -> set:
    return {f.rule for f in report.findings}


def test_valid_fixture_is_clean():
    report = check.check_paths([VALID])
    assert [f.render() for f in report.findings] == []
    assert report.exit_code == 0


@pytest.mark.parametrize("case", CASES, ids=[c["rule"] for c in CASES])
def test_broken_case_is_caught_with_its_rule(tmp_path, case):
    root = make_sprint(tmp_path)
    apply_case(root, case)
    # Ca về sổ tập trung: `ledger` = nội dung file sổ trong kho riêng ngoài thư mục dự án; `env` = biến máy,
    # `{store}` là đường kho. Mọi ca khác chạy với môi trường rỗng (máy có đặt biến sổ cũng không ảnh hưởng).
    store = tmp_path / "store"
    if "ledger" in case:
        store.mkdir(parents=True, exist_ok=True)
        write_lf(store / "order-desk.md", case["ledger"])
    env = {k: v.replace("{store}", store.as_posix()) for k, v in case.get("env", {}).items()}
    report = check.check_paths([root], env=env)
    hits = [f for f in report.findings if f.rule == case["rule"]]
    rendered = [f.render() for f in report.findings]
    assert hits, f"không bắt được {case['rule']}: {rendered}"
    assert any(Path(f.path).as_posix().endswith(case["file"]) for f in hits), rendered
    if "line" in case:
        assert any(f.line == case["line"] for f in hits), rendered
    assert report.exit_code == case["exit"], rendered


def test_every_rule_has_a_broken_case():
    covered = {c["rule"] for c in CASES}
    assert set(check.RULES) - SELF_ONLY <= covered, set(check.RULES) - SELF_ONLY - covered


def test_rule_levels_use_the_single_scale():
    assert {level for level, _ in check.RULES.values()} <= {"Chặn", "Phải sửa", "Nên sửa", "Ghi chú"}


# --- Luật chi tiết ------------------------------------------------------------------------------------


def _set_report(root: Path, old: str, new: str) -> None:
    path = root / "REPORT.md"
    write_lf(path, path.read_text(encoding="utf-8").replace(old, new, 1))


def test_declared_self_check_allows_conditional_pass_only(tmp_path):
    root = make_sprint(tmp_path)
    _set_report(root, "qa: [T3, agent-f]", "qa: [T3, agent-e]")
    _set_report(root, "| 4 passed |", "| 4 passed; tự kiểm, chưa độc lập |")
    assert "qa-not-independent" in rules_of(check.check_paths([root]))  # verdict vẫn là pass
    _set_report(root, "verdict: pass", "verdict: conditional_pass")
    assert "qa-not-independent" not in rules_of(check.check_paths([root]))


def _add_fr2(root: Path, heading: str) -> None:
    spec = root / "SPEC.md"
    text = spec.read_text(encoding="utf-8").replace(
        "## 4. Tiêu chí thành công",
        f"{heading}\n\n- **FR2.1 (lọc):** KHI chọn ngày THÌ chỉ xuất đơn trong ngày.\n\n## 4. Tiêu chí thành công", 1)
    write_lf(spec, text)


def test_fr_without_vr_exemptions(tmp_path):
    root = make_sprint(tmp_path)
    _add_fr2(root, "### FR2 — Lọc theo ngày (→ US1) — bỏ")
    assert "report-fr-without-vr" not in rules_of(check.check_paths([root]))
    root = make_sprint(tmp_path / "b")
    _add_fr2(root, "### FR2 — Lọc theo ngày (→ US1)")
    assert "report-fr-without-vr" in rules_of(check.check_paths([root]))
    _set_report(root, "## 2. Phát hiện", "- FR2 (lọc theo ngày): NOT_APPLICABLE — chưa có dữ liệu ngày.\n\n## 2. Phát hiện")
    assert "report-fr-without-vr" not in rules_of(check.check_paths([root]))
    _set_report(root, "| SC1, FR1.1 |", "| SC1, FR1.1, FR2.1 |")
    assert "report-fr-without-vr" not in rules_of(check.check_paths([root]))


def test_subtask_without_parent_is_flagged(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "PLAN.md"
    text = path.read_text(encoding="utf-8").replace("## Rủi ro", "- **TK5.1 (mồ côi):** không có TK5.\n\n## Rủi ro", 1)
    write_lf(path, text)
    hits = [f for f in check.check_paths([root]).findings if f.rule == "task-without-trace"]
    assert len(hits) == 1 and "TK5.1" in hits[0].message


def test_range_counts_for_trace_and_vr(tmp_path):
    root = make_sprint(tmp_path)
    spec = root / "SPEC.md"
    write_lf(spec, spec.read_text(encoding="utf-8").replace(
        "| SC1 (xuất đủ cột) | File CSV có đủ ba cột | Test tự động của FR1 xanh |",
        "| SC1 (xuất đủ cột) | File CSV có đủ ba cột | Test tự động của FR1 xanh |\n"
        "| SC2 (có tiêu đề) | Có dòng tên cột | Test |\n| SC3 (UTF-8) | Mở được tiếng Việt | Test |",
        1,
    ))
    _set_report(root, "| SC1, FR1.1 |", "| SC1–SC3, FR1.1 |")
    assert check.check_paths([root]).findings == []


def test_ascii_hyphen_range_keeps_both_ends(tmp_path):
    for text in ("SC1-SC3", "SC1–SC3", "SC1 - SC3"):
        assert {"SC1", "SC2", "SC3"} <= set(check.codes_on(f"| VR1 | {text}, FR1.1 |")), text
    root = make_sprint(tmp_path)
    spec = root / "SPEC.md"
    write_lf(spec, spec.read_text(encoding="utf-8").replace(
        "| SC1 (xuất đủ cột) | File CSV có đủ ba cột | Test tự động của FR1 xanh |",
        "| SC1 (xuất đủ cột) | File CSV có đủ ba cột | Test tự động của FR1 xanh |\n"
        "| SC2 (có tiêu đề) | Có dòng tên cột | Test |\n| SC3 (UTF-8) | Mở được tiếng Việt | Test |", 1))
    _set_report(root, "| SC1, FR1.1 |", "| SC1-SC3, FR1.1 |")
    assert [f.render() for f in check.check_paths([root]).findings] == []
    _set_report(root, "| SC1-SC3, FR1.1 |", "| SC1-SC9, FR1.1 |")
    assert "xref-missing" in rules_of(check.check_paths([root]))


def test_old_scale_only_in_severity_columns(tmp_path):
    (tmp_path / "a.md").write_text("| Việc | Cỡ |\n|---|---|\n| Tra đơn | medium |\n", encoding="utf-8")
    assert check.check_paths([tmp_path]).findings == []
    (tmp_path / "a.md").write_text("| Mã | Phát hiện | Severity |\n|---|---|---|\n| RF1 (x) | y | Medium |\n", encoding="utf-8")
    assert rules_of(check.check_paths([tmp_path])) == {"old-scale-label"}


def test_not_applicable_needs_a_reason(tmp_path):
    root = make_sprint(tmp_path)
    _add_fr2(root, "### FR2 — Lọc theo ngày (→ US1)")
    _set_report(root, "## 2. Phát hiện", "- FR2 (lọc theo ngày): NOT_APPLICABLE\n\n## 2. Phát hiện")
    assert "report-fr-without-vr" in rules_of(check.check_paths([root]))


def test_record_id_width_follows_project_config(tmp_path):
    root = make_sprint(tmp_path)
    (root / ".agile.json").write_text('{"schema": 1, "id_width": {"sprint": 3}}', encoding="utf-8")
    messages = [f.message for f in check.check_paths([root]).findings if f.rule == "frontmatter-value"]
    assert any("SPR-003" in m for m in messages), messages


def test_risk_and_size_consistency(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "SPEC.md"
    write_lf(path, path.read_text(encoding="utf-8").replace("risk_tags: []", "risk_tags: [secret]", 1))
    messages = [f.message for f in check.check_paths([root]).findings if f.rule == "frontmatter-value"]
    assert any("risk_tags" in m for m in messages), messages


def test_bare_letter_inside_link_url_is_ignored(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "SPEC.md"
    text = path.read_text(encoding="utf-8").replace("- Xuất Excel.", "- Xuất Excel, xem [tài liệu](https://example.com/A1/B2).", 1)
    write_lf(path, text)
    assert check.check_paths([root]).findings == []


def test_external_reference_with_slash_is_not_resolved(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "PLAN.md"
    text = path.read_text(encoding="utf-8").replace("Đạt SC1 (xuất đủ cột).", "Đạt SC1 (xuất đủ cột); giữ FS-001/FR7.3.", 1)
    write_lf(path, text)
    assert check.check_paths([root]).findings == []


def test_files_without_doc_key_get_only_general_rules(tmp_path):
    (tmp_path / "SKILL.md").write_text("---\nname: x\ndescription: y\n---\n\n# Skill\n\nKhông có mục.\n", encoding="utf-8")
    assert check.check_paths([tmp_path]).findings == []
    (tmp_path / "SKILL.md").write_text("---\nname: x\n---\n\nƯu tiên P2.\n", encoding="utf-8")
    assert rules_of(check.check_paths([tmp_path])) == {"id-bare-single-letter"}


# --- Mẫu và dự án mẫu ----------------------------------------------------------------------------------


def test_templates_pass_check():
    report = check.check_paths([REPO / "templates"])
    assert [f.render() for f in report.findings if f.level in ("Chặn", "Phải sửa")] == []
    assert report.exit_code == 0


# --- Dòng lệnh -----------------------------------------------------------------------------------------


def test_cli_prints_location_level_rule_and_summary(tmp_path, capsys):
    root = make_sprint(tmp_path)
    apply_case(root, next(c for c in CASES if c["rule"] == "id-bare-single-letter"))
    code = check.main([str(root)])
    out = capsys.readouterr().out
    assert code == 1
    assert "SPEC.md:54: Phải sửa [id-bare-single-letter]" in out
    assert "Không đạt" in out.splitlines()[-1]


def test_cli_missing_path_is_input_error(tmp_path, capsys):
    assert check.main([str(tmp_path / "không-có")]) == 2
    assert "không-có" in capsys.readouterr().out


def test_cli_rejects_non_markdown_file(tmp_path):
    other = tmp_path / "a.txt"
    other.write_text("x", encoding="utf-8")
    assert check.main([str(other)]) == 2


def test_cli_without_paths_is_usage_error(capsys):
    with pytest.raises(SystemExit) as err:
        check.main([])
    assert err.value.code == 2


def test_script_runs_standalone():
    result = run_script("check.py", str(VALID))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 phát hiện" in result.stdout


# --- Vòng sửa 2 ----------------------------------------------------------------------------------------


def test_broken_id_width_reports_config_only(tmp_path):
    root = make_sprint(tmp_path)
    (root / ".agile.json").write_text('{"schema": 1, "id_width": {"sprint": "hai", "request": 0}}', encoding="utf-8")
    report = check.check_paths([root])
    assert "config-invalid" in rules_of(report)
    assert [f.render() for f in report.findings if f.rule == "frontmatter-value"] == []


@pytest.mark.parametrize("reason", ["**chưa có dữ liệu**", '"chưa có dữ liệu"', "`chưa có` dữ liệu"])
def test_not_applicable_reason_may_start_with_markup(tmp_path, reason):
    root = make_sprint(tmp_path)
    _add_fr2(root, "### FR2 — Lọc theo ngày (→ US1)")
    _set_report(root, "## 2. Phát hiện", f"- FR2 (lọc theo ngày): NOT_APPLICABLE — {reason}\n\n## 2. Phát hiện")
    assert "report-fr-without-vr" not in rules_of(check.check_paths([root]))


@pytest.mark.parametrize("text", ["SC1-SC3.", "SC1–SC3.", "SC1 - SC3;", "SC1–SC3)"])
def test_range_before_punctuation_keeps_all_codes(text):
    assert {"SC1", "SC2", "SC3"} <= set(check.codes_on(f"Phủ {text}")), text


# --- TK6.5 ---------------------------------------------------------------------------------------------


def test_code_span_split_over_two_lines_hides_external_codes(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "PLAN.md"
    text = path.read_text(encoding="utf-8").replace(
        "Đạt SC1 (xuất đủ cột).", "Đạt SC1 (xuất đủ cột); lệnh ngoài `tool --case\nRF9 --id P7`.", 1)
    write_lf(path, text)
    assert check.check_paths([root]).findings == []


def test_caught_code_next_to_backtick_gets_a_hint(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "PLAN.md"
    text = path.read_text(encoding="utf-8").replace(
        "Đạt SC1 (xuất đủ cột).", "Đạt SC1 (xuất đủ cột); `git commit -m \"`RF9`\"`.", 1)
    write_lf(path, text)
    hits = [f for f in check.check_paths([root]).findings if f.rule == "xref-missing"]
    assert hits and all("code span" in f.message for f in hits), [f.render() for f in hits]


def test_agile_json_path_is_checked_directly(tmp_path, capsys):
    cfg = tmp_path / ".agile.json"
    cfg.write_text('{"schema": 2}', encoding="utf-8")
    assert check.main([str(cfg)]) == 1
    assert "[config-invalid]" in capsys.readouterr().out
    cfg.write_text('{"schema": 1}', encoding="utf-8")
    assert check.main([str(cfg)]) == 0
    cfg.write_text("{hỏng", encoding="utf-8")
    assert check.main([str(cfg)]) == 2


def test_code_table_needs_bold_lead_sentence(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "SPEC.md"
    text = path.read_text(encoding="utf-8")
    assert "SPEC có 1 **user story** (US):" in text
    write_lf(path, text.replace("SPEC có 1 **user story** (US):", "Câu chuyện:", 1))
    report = check.check_paths([root])
    hits = [f for f in report.findings if f.rule == "id-list-lead"]
    assert [(f.path.name, f.line) for f in hits] == [("SPEC.md", 36)] and hits[0].level == "Ghi chú"
    assert report.exit_code == 0


def test_generated_open_block_is_exempt_from_lead_rule(tmp_path):
    import init
    init.main([str(tmp_path), "--apply", "--date", "2026-03-02", "--sprint", "ok", "--title", "X"], env={})
    ledger = tmp_path / "docs" / "plans" / "SPRINTS.md"
    text = ledger.read_text(encoding="utf-8").replace(
        "Không có sprint nào đang mở.", "| Mã | Mở |\n|---|---|\n| SPR-01 | 2026-03-02 |", 1)
    write_lf(ledger, text)
    assert "id-list-lead" not in rules_of(check.check_paths([tmp_path]))


def test_hint_uses_the_position_of_each_match(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "PLAN.md"
    text = path.read_text(encoding="utf-8").replace(
        "Đạt SC1 (xuất đủ cột).", 'Đạt SC1 (xuất đủ cột); RF9 thường, P4 thường; `git commit -m "`RF9 P4`"`.', 1)
    write_lf(path, text)
    report = check.check_paths([root])
    for rule in ("xref-missing", "id-bare-single-letter"):
        hits = [f for f in report.findings if f.rule == rule]
        assert sorted("code span" in f.message for f in hits) == [False, True], [f.render() for f in hits]


# --- Bậc việc nhẹ: hợp đồng size × doc (FR7.4) ---------------------------------------------------------

SAMPLE_TINY_FOUR_PARTS = REPO / "samples" / "order-desk" / "docs" / "plans" / "2026-01-20-fix-not-found-text" / "SPRINT.md"


def two_part_sprint(size: str = "tiny", *, with_result: bool = True) -> str:
    """Một `SPRINT.md` hai phần "Kế hoạch" / "Kết quả" (bậc rất nhỏ), dựng từ frontmatter của sprint mẫu."""
    head = SAMPLE_TINY_FOUR_PARTS.read_text(encoding="utf-8").split("\n# ", 1)[0].replace("size: tiny", f"size: {size}", 1)
    body = (
        "\n# Sửa chữ báo lỗi — Sprint gộp (SPRINT)\n\n"
        "> **Kết luận:** sửa chữ câu báo lỗi; chờ kiểm.\n\n"
        "## 1. Kế hoạch\n\n"
        "- **Mục tiêu:** câu báo lỗi ở màn hình tra đơn viết đúng chính tả.\n\n"
        "Kế hoạch có 1 **success criterion** (SC) và 1 **task** (TK):\n\n"
        "- **SC1 (chữ đúng):** test giao diện so khớp đúng câu \"Không tìm thấy đơn hàng\".\n"
        "- **TK1 (sửa câu báo lỗi) → SC1:** Implementer · T2. Hoàn tác: `git revert`.\n"
    )
    if with_result:
        body += (
            "\n## 2. Kết quả\n\n"
            "Kết quả có 1 **verification result** (VR):\n\n"
            "| Mã | Kiểm cái gì | Lệnh / thao tác | Kết quả | Người kiểm |\n|---|---|---|---|---|\n"
            "| VR1 (test câu báo lỗi) | SC1 | `pytest tests/test_ui.py` | Chưa chạy | Tech Reviewer · agent-d |\n\n"
            "- **Nhật ký:** Implementer sửa câu báo lỗi.\n"
        )
    return head + "\n" + body


def put(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    write_lf(path, text)
    return path


def test_old_tiny_sprint_with_four_parts_stays_valid():
    """Hồi quy: sprint rất nhỏ bốn phần của đợt trước vẫn qua."""
    assert check.check_paths([SAMPLE_TINY_FOUR_PARTS]).findings == []


def test_four_files_size_small_is_valid(tmp_path):
    """Hồi quy: sprint nhỏ dựng bằng bốn file (cách cũ) vẫn hợp lệ."""
    root = make_sprint(tmp_path)
    for name in ("SPEC", "PLAN", "PROGRESS", "REPORT"):
        path = root / f"{name}.md"
        write_lf(path, path.read_text(encoding="utf-8").replace("size: medium", "size: small", 1))
    assert [f.render() for f in check.check_paths([root]).findings] == []


def test_tiny_two_part_sprint_is_clean(tmp_path):
    put(tmp_path, "SPRINT.md", two_part_sprint())
    assert [f.render() for f in check.check_paths([tmp_path]).findings] == []


def test_tiny_two_part_sprint_missing_result_is_flagged(tmp_path):
    put(tmp_path, "SPRINT.md", two_part_sprint(with_result=False))
    hits = [f for f in check.check_paths([tmp_path]).findings if f.rule == "heading-missing"]
    assert any("Kết quả" in f.message for f in hits), [f.render() for f in hits]


def test_small_sprint_file_needs_four_parts(tmp_path):
    put(tmp_path, "SPRINT.md", two_part_sprint("small"))
    hits = [f for f in check.check_paths([tmp_path]).findings if f.rule == "heading-missing"]
    missing = {w for w in ("SPEC", "PLAN", "PROGRESS", "REPORT") if any(f"'{w}'" in f.message for f in hits)}
    assert missing == {"SPEC", "PLAN", "PROGRESS", "REPORT"}, [f.render() for f in hits]


def test_sprint_file_at_medium_is_flagged_exactly_once(tmp_path):
    text = SAMPLE_TINY_FOUR_PARTS.read_text(encoding="utf-8").replace("size: tiny", "size: medium", 1)
    put(tmp_path, "SPRINT.md", text)
    report = check.check_paths([tmp_path])
    hits = [f for f in report.findings if f.rule == "sprint-size-mismatch"]
    assert len(hits) == 1 and hits[0].level == "Phải sửa", [f.render() for f in report.findings]
    assert report.exit_code == 1


def test_sprint_file_at_large_is_flagged(tmp_path):
    text = SAMPLE_TINY_FOUR_PARTS.read_text(encoding="utf-8").replace("size: tiny", "size: large", 1)
    put(tmp_path, "SPRINT.md", text)
    assert "sprint-size-mismatch" in rules_of(check.check_paths([tmp_path]))


def test_four_files_size_tiny_is_flagged_once_per_folder(tmp_path):
    root = make_sprint(tmp_path)
    for name in ("SPEC", "PLAN", "PROGRESS", "REPORT"):
        path = root / f"{name}.md"
        write_lf(path, path.read_text(encoding="utf-8").replace("size: medium", "size: tiny", 1))
    hits = [f for f in check.check_paths([root]).findings if f.rule == "sprint-size-mismatch"]
    assert len(hits) == 1, [f.render() for f in hits]


def test_missing_size_key_is_not_reported_twice(tmp_path):
    text = SAMPLE_TINY_FOUR_PARTS.read_text(encoding="utf-8").replace("size: tiny\n", "", 1)
    put(tmp_path, "SPRINT.md", text)
    rules = [f.rule for f in check.check_paths([tmp_path]).findings]
    assert "frontmatter-key-missing" in rules and "sprint-size-mismatch" not in rules


# --- Sổ tập trung (FR8, SC10) ---------------------------------------------------------------------------

LEDGER_STORE = FIXTURES / "ledger"
LEDGER_TABLE_HEAD = "| Sprint | Trạng thái | Cập nhật | Hồ sơ | Link |\n|---|---|---|---|---|\n"
URL_PATTERN = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/blob/[\w./-]+/docs/plans/[\w.-]+/[\w.-]+\.md")
# Đường tuyệt đối của máy (ổ đĩa kiểu Windows, thư mục người dùng, thư mục home Unix); ghép từ mảnh để file test
# không tự chứa chuỗi bị `--self` coi là đường máy.
ABSOLUTE_PATH = re.compile("|".join([r"[A-Za-z]:\\", "/" + "Us" + "ers/", "/" + "ho" + "me/"]))


def ledger_project(tmp_path: Path, *, declared=True, row=None, ledger_text=None):
    """Dự án mẫu (sprint `SPR-03`, `verifying`, `updated: 2026-02-02`) + kho sổ riêng; trả (gốc dự án, env)."""
    root = make_sprint(tmp_path)
    cfg = {"schema": 1, "ledger": {"project": "order-desk"}} if declared else {"schema": 1}
    write_lf(root / ".agile.json", json.dumps(cfg))
    store = tmp_path / "store"
    shutil.copytree(LEDGER_STORE, store)
    if row is not None:
        write_lf(store / "order-desk.md", "# Sổ\n\n## Sprint\n\n" + LEDGER_TABLE_HEAD + row + "\n")
    if ledger_text is not None:
        write_lf(store / "order-desk.md", ledger_text)
    return root, {LEDGER_ENV: f"{store.as_posix()}/{{project}}.md"}


def ledger_rules(report) -> dict:
    return {f.rule: f for f in report.findings if f.rule.startswith("ledger-") or f.rule == "config-invalid"}


def test_ledger_off_when_project_not_declared_even_if_machine_sets_the_variable(tmp_path):
    root, env = ledger_project(tmp_path, declared=False)
    (tmp_path / "store" / "order-desk.md").unlink()  # kho sổ không có file cũng không sao: sổ tắt
    report = check.check_paths([root], env=env)
    assert [f.render() for f in report.findings] == [] and report.exit_code == 0
    write_lf(root / ".agile.json", json.dumps({"schema": 1, "ledger": {"project": ""}}))  # khoá rỗng cũng là tắt
    assert check.check_paths([root], env=env).findings == []
    write_lf(root / ".agile.json", json.dumps({"schema": 1}))
    assert check.check_paths([root], env={LEDGER_ENV: "không-có-placeholder.md"}).findings == []


def test_ledger_declared_with_full_row_is_clean(tmp_path):
    root, env = ledger_project(tmp_path)
    report = check.check_paths([root], env=env)
    assert [f.render() for f in report.findings] == [] and report.exit_code == 0


def test_ledger_missing_row_for_open_sprint(tmp_path):
    root, env = ledger_project(tmp_path, row="| SPR-09 | verifying | 2026-02-02 | order-desk:x | y |")
    report = check.check_paths([root], env=env)
    hit = ledger_rules(report)["ledger-missing-row"]
    assert hit.level == "Phải sửa" and hit.path.name == "PROGRESS.md" and "SPR-03" in hit.message
    assert report.exit_code == 1


def test_ledger_stale_status(tmp_path):
    root, env = ledger_project(tmp_path, row="| SPR-03 | in_progress | 2026-02-02 | order-desk:x | y |")
    report = check.check_paths([root], env=env)
    hit = ledger_rules(report)["ledger-stale"]
    assert hit.level == "Phải sửa" and "in_progress" in hit.message and "verifying" in hit.message
    assert report.exit_code == 1


def test_ledger_stale_date_older_than_updated(tmp_path):
    root, env = ledger_project(tmp_path, row="| SPR-03 | verifying | 2026-02-01 | order-desk:x | y |")
    report = check.check_paths([root], env=env)
    hit = ledger_rules(report)["ledger-stale"]
    assert "2026-02-01" in hit.message and "2026-02-02" in hit.message and report.exit_code == 1
    newer = ledger_project(tmp_path / "n", row="| SPR-03 | verifying | 2026-03-01 | order-desk:x | y |")
    assert check.check_paths([newer[0]], env=newer[1]).findings == []  # ngày mới hơn `updated` là bình thường


def test_ledger_date_must_be_iso(tmp_path):
    root, env = ledger_project(tmp_path, row="| SPR-03 | verifying | hôm qua | order-desk:x | y |")
    assert "ledger-stale" in ledger_rules(check.check_paths([root], env=env))


def test_ledger_unreadable_file_missing_not_utf8_or_without_table(tmp_path):
    root, env = ledger_project(tmp_path)
    (tmp_path / "store" / "order-desk.md").unlink()
    report = check.check_paths([root], env=env)
    assert ledger_rules(report)["ledger-unreadable"].level == "Phải sửa" and report.exit_code == 1
    (tmp_path / "store" / "order-desk.md").write_bytes(b"\xff\xfe\x00bad")
    assert "ledger-unreadable" in ledger_rules(check.check_paths([root], env=env))
    write_lf(tmp_path / "store" / "order-desk.md", "# Sổ\n\nKhông có bảng nào.\n\n| Mục | Giá trị |\n|---|---|\n| a | b |\n")
    assert "ledger-unreadable" in ledger_rules(check.check_paths([root], env=env))


def test_ledger_declared_but_machine_has_no_pattern_is_a_note(tmp_path):
    root, _ = ledger_project(tmp_path)
    report = check.check_paths([root], env={})
    hit = ledger_rules(report)["ledger-unconfigured"]
    assert hit.level == "Ghi chú" and "AGENT_AGILE_LEDGER" in hit.message
    assert report.exit_code == 0  # Ghi chú không làm đỏ
    assert "ledger-unconfigured" in ledger_rules(check.check_paths([root], env={LEDGER_ENV: ""}))


def test_ledger_pattern_without_project_placeholder_is_config_invalid(tmp_path):
    root, _ = ledger_project(tmp_path)
    report = check.check_paths([root], env={LEDGER_ENV: (tmp_path / "store" / "order-desk.md").as_posix()})
    hit = ledger_rules(report)["config-invalid"]
    assert hit.level == "Phải sửa" and "{project}" in hit.message and report.exit_code == 1


@pytest.mark.parametrize("ledger", ['"x"', "5", '{"project": 5}', '{"project": "a/b"}', '{"project": "..\\\\x"}', '{"project": "../x"}'])
def test_ledger_shape_errors_are_config_invalid(tmp_path, ledger):
    root = make_sprint(tmp_path)
    write_lf(root / ".agile.json", '{"schema": 1, "ledger": ' + ledger + "}")
    report = check.check_paths([root], env={})
    assert any(f.rule == "config-invalid" and "ledger" in f.message for f in report.findings), [f.render() for f in report.findings]


def test_ledger_closed_sprint_without_row_is_not_reported(tmp_path):
    root, env = ledger_project(tmp_path, row="| SPR-09 | done | 2026-02-02 | order-desk:x | y |")
    progress = root / "PROGRESS.md"
    write_lf(progress, progress.read_text(encoding="utf-8").replace("status: verifying", "status: dropped", 1))
    assert "ledger-missing-row" not in ledger_rules(check.check_paths([root], env=env))


def test_ledger_closed_sprint_with_row_is_still_compared(tmp_path):
    root, env = ledger_project(tmp_path, row="| SPR-03 | verifying | 2026-02-02 | order-desk:x | y |")
    progress = root / "PROGRESS.md"
    write_lf(progress, progress.read_text(encoding="utf-8").replace("status: verifying", "status: done", 1))
    assert "ledger-stale" in ledger_rules(check.check_paths([root], env=env))


def test_ledger_ignores_sprints_of_a_nested_project(tmp_path):
    root, env = ledger_project(tmp_path)
    nested = root / "sub" / "other"
    shutil.copytree(VALID, nested)
    write_lf(nested / ".agile.json", json.dumps({"schema": 1}))
    progress = nested / "PROGRESS.md"
    write_lf(progress, progress.read_text(encoding="utf-8").replace("sprint: SPR-03", "sprint: SPR-77", 1))
    assert "ledger-missing-row" not in ledger_rules(check.check_paths([root / ".agile.json"], env=env))


def test_ledger_cli_reads_the_variable_from_the_environment(tmp_path):
    root, env = ledger_project(tmp_path, row="| SPR-09 | verifying | 2026-02-02 | order-desk:x | y |")
    result = run_script("check.py", str(root), env=env)
    assert result.returncode == 1 and "[ledger-missing-row]" in result.stdout
    clean = run_script("check.py", str(root), env={LEDGER_ENV: ""})
    assert "[ledger-unconfigured]" in clean.stdout and clean.returncode == 0


def test_machine_ledger_variable_never_leaks_into_ordinary_tests():
    assert LEDGER_ENV not in os.environ


# --- Link của dòng sổ (FR8.3) ----------------------------------------------------------------------------


def _ledger_rows(text: str) -> list:
    rows, in_table = [], False
    for line in text.splitlines():
        cells = [x.strip() for x in line.strip().strip("|").split("|")] if line.startswith("|") else None
        if cells is None:
            in_table = False
        elif cells[0] == "Sprint":
            in_table = True
        elif in_table and cells[0].startswith("SPR-"):
            rows.append(cells)
    return rows


def test_ledger_fixture_links_are_clickable_and_machine_free():
    text = (LEDGER_STORE / "order-desk.md").read_text(encoding="utf-8")
    rows = _ledger_rows(text)
    assert len(rows) == 2 and not ABSOLUTE_PATH.search(text)
    relative = urls = 0
    for _sprint, _status, _day, doc, link in rows:
        assert re.fullmatch(r"[a-z0-9-]+:docs/plans/[\w.-]+/[A-Z]+\.md", doc)
        target = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", link).group(1)
        if target.startswith("https://"):
            assert URL_PATTERN.fullmatch(target), target
            assert doc.split(":", 1)[1] in target
            urls += 1
        else:
            assert (LEDGER_STORE / target).is_file(), target  # đường tương đối trỏ file có thật trong kho sổ
            assert not Path(target).is_absolute()
            relative += 1
    assert (relative, urls) == (1, 1)


def test_ledger_template_has_the_sprint_table_and_no_machine_paths():
    path = REPO / "templates" / "registry" / "LEDGER.md"
    text = path.read_text(encoding="utf-8")
    assert "| Sprint | Trạng thái | Cập nhật | Hồ sơ | Link |" in text
    assert not ABSOLUTE_PATH.search(text) and "~/" not in text
    example = [line for line in text.splitlines() if line.startswith("| SPR-")]  # dòng ví dụ nằm trong comment HTML
    assert len(example) == 2 and not any(ABSOLUTE_PATH.search(line) for line in example)
    assert any(URL_PATTERN.search(line) for line in example)  # một dòng URL, một dòng tương đối
    assert check.check_paths([path]).findings == []
