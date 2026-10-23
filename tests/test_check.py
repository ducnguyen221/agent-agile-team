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
SPECIAL_CASES = {
    "leak-denylist", "agents-md-budget",
    "routing-invalid", "routing-unknown", "routing-manifest-invalid", "routing-missing", "routing-duplicate",
}


def make_sprint(tmp_path: Path) -> Path:
    root = tmp_path / "sprint"
    shutil.copytree(VALID, root)
    return root


def apply_case(root: Path, case: dict) -> None:
    if case.get("base") == "delegated":
        delegate_plan(root)
    elif case.get("base") == "delegated-report":
        delegate_report(root)
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


DELEGATION_RECORD = """
## Bản ghi duyệt thay

- **Phương án chọn:** phương án a — giữ nguyên hình hiện có.
- **Phương án bị loại:** phương án b — đổi hình, tốn thêm một việc.
- **Nếu sai thì tốn gì:** sửa lại tài liệu và duyệt lại, chưa có mã nào được viết.
- Lời cấp: khối `delegation` ở frontmatter.
"""


def _rewrite(path: Path, old: str, new: str, tail: str = "") -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"không thấy chuỗi cần thay trong {path.name}"
    write_lf(path, text.replace(old, new, 1) + tail)


def delegate_plan(root: Path) -> None:
    """PLAN hợp lệ ở Cổng 1 duyệt thay: khối `delegation` đủ, quote `duyệt thay:` và mục bản ghi."""
    _rewrite(root / "PLAN.md", 'gate_1_quote: "duyệt"\n', (
        'gate_1_quote: "duyệt thay: chọn phương án a — xem mục Bản ghi duyệt thay"\n'
        "gate_1_mode: delegated\n"
        "delegation:\n"
        '  grant: "Cho phép T1 duyệt thay Cổng 1 của SPR-03 tới hết sprint."\n'
        "  grant_at: 2026-02-01 08:30 +07\n"
        "  scope: [gate_1]\n"
        "  expires: sprint_end\n"
        "  by: agent-d\n"
        "  tier: T1\n"
        "  files: []\n"
        "  revoked_at: null\n"), DELEGATION_RECORD)


def delegate_report(root: Path) -> None:
    """REPORT hợp lệ ở Cổng 2 duyệt thay."""
    _rewrite(root / "REPORT.md", "gate_2: pending\ngate_2_at: null\ngate_2_quote: null\n", (
        "gate_2: pass\n"
        "gate_2_at: 2026-02-02 17:00 +07\n"
        'gate_2_quote: "duyệt thay: Đạt — xem mục Bản ghi duyệt thay"\n'
        "gate_2_mode: delegated\n"
        "delegation:\n"
        '  grant: "Cho phép T1 duyệt thay Cổng 2 của SPR-03 tới hết sprint."\n'
        "  grant_at: 2026-02-02 08:00 +07\n"
        "  scope: [gate_2]\n"
        "  expires: sprint_end\n"
        "  by: agent-d\n"
        "  tier: T1\n"
        "  files: []\n"
        "  revoked_at: null\n"), DELEGATION_RECORD)


def codes(findings) -> list:
    return sorted(f.rule for f in findings)


def test_valid_fixture_is_clean():
    report = check.check_paths([VALID])
    assert [f.render() for f in report.findings] == []
    assert report.exit_code == 0


@pytest.mark.parametrize("case", CASES, ids=[c.get("name", c["rule"]) for c in CASES])
def test_broken_case_is_caught_with_its_rule(tmp_path, case):
    root = make_sprint(tmp_path)
    apply_case(root, case)
    # Ca về sổ tập trung: `ledger` = nội dung file sổ trong kho riêng ngoài thư mục dự án; `env` = biến máy,
    # `{store}` là đường kho. Mọi ca khác chạy với môi trường rỗng (máy có đặt biến sổ cũng không ảnh hưởng).
    store = tmp_path / "store"
    if "ledger" in case or "env" in case:  # sổ tập trung đọc sprint theo mẫu `paths.sprint_dir`: đặt hồ sơ đúng chỗ
        folder = root / "docs" / "plans" / "2026-02-01-export-orders"
        folder.mkdir(parents=True)
        for item in [p for p in root.iterdir() if p.name not in (".agile.json", "docs")]:
            shutil.move(str(item), str(folder / item.name))
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
    assert set(check.RULES) - SPECIAL_CASES <= covered, set(check.RULES) - SPECIAL_CASES - covered


def test_every_rule_has_a_row_in_scripts_readme():
    """`check.py` tự khai mô tả từng luật ở `scripts/README.md`: mọi mã trong `RULES` phải có hàng ở bảng luật, đúng mức."""
    text = (REPO / "scripts" / "README.md").read_text(encoding="utf-8")
    rows = set(re.findall(r"^\| `([a-z0-9-]+)` \|", text, re.M))
    assert set(check.RULES) <= rows, sorted(set(check.RULES) - rows)
    for code, (level, _) in check.RULES.items():
        assert re.search(rf"^\| `{code}` \| {level} \|", text, re.M), f"{code}: mức ở README khác RULES ({level})"


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


@pytest.mark.parametrize("text", [
    "Lỗi này là CRITICAL nên phải sửa ngay.",
    "Mức độ HIGH được chấp nhận tạm thời.",
    "[HIGH] SQL ghép chuỗi ở dòng 12",
    "- [CRITICAL] khoá nằm trong mã nguồn",
    "> [MEDIUM] thiếu kiểm tra đầu vào",
    "Chỉ báo khi confidence ≥ 80 trên thang nguồn.",
    "Lọc theo confidence >= 80 rồi gộp.",
    "**Mức:** Cao — phải sửa trước khi giao.",
    "Severity: Thấp, bỏ qua được.",
    "- Mức: Trung bình",
    "Mức: Nghiêm trọng",
])
def test_old_scale_label_inside_a_sentence(tmp_path, text):
    (tmp_path / "a.md").write_text(text + "\n", encoding="utf-8")
    assert rules_of(check.check_paths([tmp_path])) == {"old-scale-label"}, text


@pytest.mark.parametrize("text", [
    "Dựng workflow high-level cho việc low-code, cỡ medium-sized.",
    "Critical thinking và low-level API không phải nhãn mức.",
    "Đặt mức cao hơn cho việc này là hợp lý; ưu tiên thấp nhất vẫn làm.",
    "Độ tin cậy cao, confidence interval hẹp, confidence là gì?",
    "Báo cáo ghi confidence: 8/10 và confidence = 0.9 (không phải ngưỡng so sánh).",
    "Mức rủi ro của việc này do người dùng quyết.",
    "Bảng quy đổi ghi `CRITICAL` → Chặn và `[HIGH]` → Phải sửa.",
    "Hàm `highlight()` trả về giá trị thấp nhất.",
    "Thư mục HIGHLIGHTS và LOWER_CASE_NAME không phải nhãn.",
    "Đầu ra: mức Chặn / Phải sửa / Nên sửa / Ghi chú.",
])
def test_lowercase_words_and_core_scale_are_not_old_labels(tmp_path, text):
    (tmp_path / "a.md").write_text(text + "\n", encoding="utf-8")
    assert check.check_paths([tmp_path]).findings == [], text


def test_source_style_labels_in_skill_test_records_are_quotes_of_subject_output(tmp_path):
    """File thử của skill chép nguyên văn đầu ra của chủ thể thử (pha Gốc, RED): nhãn kiểu nguồn trong câu ở đó
    là trích dẫn, không báo; cùng câu trong thân skill thì báo. Ô cột mức vẫn báo ở mọi nơi."""
    tests_dir = tmp_path / "skills" / "demo" / "tests"
    tests_dir.mkdir(parents=True)
    quote = "Gốc: hồi quy CRITICAL, [HIGH] ở dòng 3, confidence ≥ 80.\n"
    (tests_dir / "pressure.md").write_text(quote, encoding="utf-8")
    assert check.check_paths([tests_dir]).findings == []
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text(quote, encoding="utf-8")
    assert rules_of(check.check_paths([tmp_path / "skills" / "demo" / "SKILL.md"])) == {"old-scale-label"}
    (tests_dir / "pressure.md").write_text("| Mã | Mức |\n|---|---|\n| RF1 | CRITICAL |\n", encoding="utf-8")
    assert rules_of(check.check_paths([tests_dir])) == {"old-scale-label"}


def test_old_vietnamese_label_in_level_column(tmp_path):
    (tmp_path / "a.md").write_text(
        "| Mã | Phát hiện | Mức |\n|---|---|---|\n| RF1 (x) | y | Trung bình |\n", encoding="utf-8")
    assert rules_of(check.check_paths([tmp_path])) == {"old-scale-label"}
    (tmp_path / "a.md").write_text(
        "| Mã | Phát hiện | Mức |\n|---|---|---|\n| RF1 (x) | y | Phải sửa |\n", encoding="utf-8")
    assert check.check_paths([tmp_path]).findings == []
    (tmp_path / "a.md").write_text(  # thang khác (chắc chắn, rủi ro): "Cao" là giá trị hợp lệ
        "| Mã | Mức chắc chắn | Mức rủi ro |\n|---|---|---|\n| RF1 | Cao | Thấp |\n", encoding="utf-8")
    assert check.check_paths([tmp_path]).findings == []
    (tmp_path / "a.md").write_text(
        "| Mã | Mức độ |\n|---|---|\n| RF1 | Nghiêm trọng |\n", encoding="utf-8")
    assert rules_of(check.check_paths([tmp_path])) == {"old-scale-label"}
    (tmp_path / "a.md").write_text(  # cột không phải cột mức: "Cao" là giá trị thường
        "| Việc | Độ cao |\n|---|---|\n| Tra đơn | Cao |\n", encoding="utf-8")
    assert check.check_paths([tmp_path]).findings == []


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
        "SC1 (xuất đủ cột) của SPEC đạt.", "SC1 (xuất đủ cột) của SPEC đạt; `git commit -m \"`RF9`\"`.", 1)
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
        "SC1 (xuất đủ cột) của SPEC đạt.", 'SC1 (xuất đủ cột) của SPEC đạt; RF9 thường, P4 thường; `git commit -m "`RF9 P4`"`.', 1)
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


def test_tiny_two_part_sprint_with_plan_word_in_heading_is_not_taken_for_four_parts(tmp_path):
    """Tiêu đề chỉ *chứa* chữ plan ("Kế hoạch (plan)") không làm `SPRINT.md` hai phần bị đòi đủ bốn phần."""
    put(tmp_path, "SPRINT.md", two_part_sprint().replace("## 1. Kế hoạch", "## 1. Kế hoạch (plan)", 1))
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
    root = tmp_path / "sprint"
    folder = root / "docs" / "plans" / "2026-02-01-export-orders"  # đúng mẫu `paths.sprint_dir` mặc định
    shutil.copytree(VALID, folder)
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


def test_ledger_reads_only_sprint_folders_matching_sprint_dir(tmp_path):
    """Như `index.py`: sprint nằm theo mẫu `paths.sprint_dir`. Bản chép mẫu nằm chỗ khác trong repo (vendor, ví dụ) không
    bị đòi dòng sổ."""
    root, env = ledger_project(tmp_path)
    source = (root / "docs" / "plans" / "2026-02-01-export-orders" / "PROGRESS.md").read_text(encoding="utf-8")
    copy = root / "vendor" / "agile-example" / "PROGRESS.md"
    copy.parent.mkdir(parents=True)
    write_lf(copy, source.replace("SPR-03", "SPR-77"))
    report = check.check_paths([root], env=env)
    assert "ledger-missing-row" not in ledger_rules(report), [f.render() for f in report.findings]


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


@pytest.mark.parametrize("extra", [
    {"paths": "docs"},
    {"artifact_root": 5},
    {"paths": {"sprint_dir": "C:/abs/{date}-{slug}"}},
], ids=["paths-not-object", "artifact-root-not-string", "sprint-dir-absolute"])
def test_malformed_config_with_declared_ledger_reports_config_invalid_without_traceback(tmp_path, extra):
    """`.agile.json` sai hình mà dự án có khai sổ và máy đặt biến: chỉ `config-invalid`, thoát 1, không đối chiếu sổ, không traceback."""
    root, env = ledger_project(tmp_path)
    write_lf(root / ".agile.json", json.dumps({"schema": 1, "ledger": {"project": "order-desk"}, **extra}))
    report = check.check_paths([root], env=env)
    assert {f.rule for f in report.findings} == {"config-invalid"}, [f.render() for f in report.findings]
    assert report.exit_code == 1
    result = run_script("check.py", str(root), env=env)
    assert result.returncode == 1 and "Traceback" not in result.stderr and "config-invalid" in result.stdout


def test_ledger_closed_sprint_without_row_is_not_reported(tmp_path):
    root, env = ledger_project(tmp_path, row="| SPR-09 | done | 2026-02-02 | order-desk:x | y |")
    progress = root / "docs" / "plans" / "2026-02-01-export-orders" / "PROGRESS.md"
    write_lf(progress, progress.read_text(encoding="utf-8").replace("status: verifying", "status: dropped", 1))
    assert "ledger-missing-row" not in ledger_rules(check.check_paths([root], env=env))


def test_ledger_closed_sprint_with_row_is_still_compared(tmp_path):
    root, env = ledger_project(tmp_path, row="| SPR-03 | verifying | 2026-02-02 | order-desk:x | y |")
    progress = root / "docs" / "plans" / "2026-02-01-export-orders" / "PROGRESS.md"
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


# --- Routing evidence (pilot opt-in; legacy documents remain valid) -------------------------------------


def test_routing_marker_requires_json(tmp_path):
    path = tmp_path / "evidence.md"
    write_lf(path, "# Evidence\n\n<!-- routing-evidence:v1 -->\n\nMissing JSON.\n")
    report = check.check_paths([path])
    assert any(f.rule == "routing-invalid" and f.line == 3 for f in report.findings)
    assert report.exit_code == 1


def test_routing_malformed_json_is_a_finding(tmp_path):
    path = tmp_path / "evidence.md"
    write_lf(path, "# Evidence\n\n<!-- routing-evidence:v1 -->\n```json\n{bad}\n```\n")
    report = check.check_paths([path])
    assert any(f.rule == "routing-invalid" and f.line == 3 for f in report.findings)
    assert report.exit_code == 1


def test_routing_legacy_doc_unchanged():
    assert check.check_paths([VALID]).findings == []


ROUTING = FIXTURES / "routing"


def routing_record(kind: str) -> dict:
    return json.loads((ROUTING / f"valid_{kind}.json").read_text(encoding="utf-8"))


def routing_codes(record: dict) -> set:
    return {code for code, _ in check.routing_record_problems(record, set())}


def test_routing_complete_records_have_no_problems():
    assert check.routing_record_problems(routing_record("classification"), set()) == []
    assert check.routing_record_problems(routing_record("attempt"), set()) == []


def test_routing_unknown_usage_not_zero():
    record = routing_record("attempt")
    assert "routing-invalid" not in routing_codes(record)
    record["unknown_reasons"].pop("usage.tokens_in")
    assert "routing-invalid" in routing_codes(record)
    record["usage"]["tokens_in"] = 0
    record["unknown_reasons"].pop("usage.usage_source")
    assert "routing-invalid" in routing_codes(record)


def test_routing_default_request_null_is_not_actual():
    record = routing_record("attempt")
    record["dispatch"]["requested_model"] = None
    record["unknown_reasons"]["dispatch.requested_model"] = "not_applicable: native default"
    record["dispatch"]["actual_model_source"] = None
    record["unknown_reasons"]["dispatch.actual_model_source"] = "not observed at runtime"
    assert "routing-invalid" in routing_codes(record)


def test_routing_override_requires_scope_and_quote():
    record = routing_record("classification")
    record["assignment"]["override"] = {
        "decision_ref": "owner-1", "owner_quote": "", "approved_at": "2026-10-12T09:00:00Z",
        "scope_kind": "turn", "scope_ref": "", "status": "approved",
        "model_override": "model-pinned", "effort_override": None, "constraints": [], "expiry": None
    }
    record["decision"]["override_ref"] = "owner-1"
    assert "routing-invalid" in routing_codes(record)


def test_routing_human_pins_are_independent():
    record = routing_record("classification")
    record["assignment"]["override"] = {
        "decision_ref": "owner-1", "owner_quote": "Use model-pinned",
        "approved_at": "2026-10-12T09:00:00Z", "scope_kind": "work_item",
        "scope_ref": "TK1", "status": "approved", "model_override": "model-pinned",
        "effort_override": None, "constraints": [], "expiry": None
    }
    record["decision"]["override_ref"] = "owner-1"
    record["decision"]["decision_basis"] = "human_override"
    record["notification"]["model"] = "model-pinned"
    record["notification"]["approval_ref"] = "owner-1"
    record["unknown_reasons"].pop("assignment.override")
    record["unknown_reasons"].pop("decision.override_ref")
    record["unknown_reasons"].pop("notification.approval_ref")
    record["unknown_reasons"]["assignment.override.effort_override"] = "not_applicable: only model pinned"
    record["unknown_reasons"]["assignment.override.expiry"] = "not_applicable: work item scope"
    assert check.routing_record_problems(record, set()) == []
    record["effort"]["effort_requested"] = "high"
    record["effort"]["effort_source"] = "human_override"
    assert "routing-invalid" in routing_codes(record)


def test_routing_notice_must_precede_dispatch():
    record = routing_record("attempt")
    record["notification"]["notified_at"] = "2026-10-12T10:03:00Z"
    assert "routing-invalid" in routing_codes(record)


def test_routing_criteria_change_rechecks_both_branches():
    record = routing_record("classification")
    record["criteria_change"] = {
        "criteria_version": "v2", "previous_version": "v1", "change_ref": "owner-2",
        "baseline_invalidated": True, "re_evaluation_scope": "both_branches"
    }
    record["criteria_version"] = "v2"
    record["notification"]["event_kind"] = "criteria_change"
    record["unknown_reasons"].pop("criteria_change")
    assert check.routing_record_problems(record, set()) == []
    record["criteria_change"]["re_evaluation_scope"] = "candidate_only"
    assert "routing-invalid" in routing_codes(record)


def test_routing_third_failed_repair_requires_handoff():
    record = routing_record("attempt")
    record["repair_history"]["repair_cycle_index"] = 3
    record["repair_history"]["total_repair_cycles"] = 3
    record["outcome"]["repair_rounds"] = 3
    record["quality"]["acceptance_pass"] = False
    record["outcome"]["regressions"] = ["oracle:new-regression"]
    assert "routing-invalid" in routing_codes(record)
    record["outcome"]["escalations"] = ["handoff:assignment-2"]
    record["notification"]["event_kind"] = "handoff"
    assert check.routing_record_problems(record, set()) == []


def test_routing_fourth_repair_same_assignment_is_invalid():
    record = routing_record("attempt")
    record["repair_history"]["repair_cycle_index"] = 4
    assert "routing-invalid" in routing_codes(record)


def test_routing_nested_evidence_ref_cannot_escape_repository():
    record = routing_record("classification")
    record["axes"]["scope_dependencies"]["evidence_refs"] = ["../private.txt"]
    assert "routing-invalid" in routing_codes(record)


def test_routing_ordinal_and_difficulty_follow_evidenced_axes():
    record = routing_record("classification")
    record["axes"]["scope_dependencies"]["value"] = "coupled"
    record["axes"]["scope_dependencies"]["ordinal"] = 1
    record["decision"]["difficulty_level"] = 2
    assert check.routing_record_problems(record, set()) == []
    record["decision"]["difficulty_level"] = 1
    assert "routing-invalid" in routing_codes(record)
    record["axes"]["scope_dependencies"]["evidence_refs"] = []
    assert "routing-invalid" in routing_codes(record)


def test_routing_missing_axis_evidence_cannot_default_difficulty():
    record = routing_record("classification")
    record["axes"]["scope_dependencies"]["value"] = None
    record["axes"]["scope_dependencies"]["ordinal"] = None
    record["axes"]["scope_dependencies"]["unknowns"] = ["not_read:caller"]
    record["unknown_reasons"]["axes.scope_dependencies.value"] = "caller not inspected"
    record["unknown_reasons"]["axes.scope_dependencies.ordinal"] = "caller not inspected"
    assert "routing-invalid" in routing_codes(record)
    record["decision"]["difficulty_level"] = None
    record["unknown_reasons"]["decision.difficulty_level"] = "technical axis unknown"
    assert check.routing_record_problems(record, set()) == []


def test_routing_policy_default_effort_is_medium_or_higher():
    record = routing_record("classification")
    record["effort"]["effort_level"] = 1
    record["effort"]["effort_requested"] = "low"
    assert "routing-invalid" in routing_codes(record)


def test_routing_repair_total_cannot_reset_across_assignment():
    record = routing_record("attempt")
    record["repair_history"]["repair_cycle_index"] = 2
    record["repair_history"]["total_repair_cycles"] = 1
    record["outcome"]["repair_rounds"] = 2
    assert "routing-invalid" in routing_codes(record)


def test_routing_unknown_reason_is_text_not_a_path():
    record = routing_record("classification")
    record["unknown_reasons"]["decision.override_ref"] = "not_applicable: no ../other route selected"
    assert check.routing_record_problems(record, set()) == []


def test_routing_bad_reference_type_reports_finding_without_crashing():
    record = routing_record("classification")
    record["evidence_refs"] = [[]]
    assert "routing-invalid" in routing_codes(record)


def test_routing_attempt_requires_observed_prenotice():
    record = routing_record("attempt")
    record["notification"]["notified_at"] = None
    record["unknown_reasons"]["notification.notified_at"] = "missing timestamp"
    assert "routing-invalid" in routing_codes(record)


def test_routing_actual_status_cannot_be_claimed_in_prenotice():
    record = routing_record("attempt")
    record["notification"]["model_status"] = "actual"
    assert "routing-invalid" in routing_codes(record)


def test_routing_zero_actual_cost_requires_billing_source():
    record = routing_record("attempt")
    record["cost"]["actual_incremental_usd"] = 0
    assert "routing-invalid" in routing_codes(record)


def test_routing_complete_source_coverage_requires_ledger_refs():
    manifest = pilot_manifest()
    manifest["source_coverage"]["ledger_refs"] = []
    assert "routing-missing" in {code for code, _ in check.routing_bundle_problems(pilot_records(), manifest)}


def test_routing_malformed_record_in_bundle_does_not_crash():
    records = pilot_records()
    records[0]["record"]["record_ref"] = []
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


def test_routing_bundle_rejects_policy_hash_outside_manifest():
    records = pilot_records()
    records[0]["record"]["policy_hash"] = "f" * 64
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


def test_routing_notice_assignment_must_match_record():
    record = routing_record("classification")
    record["notification"]["assignment_ref"] = "assignment-other"
    assert "routing-invalid" in routing_codes(record)


def test_routing_marker_checks_record_fields(tmp_path):
    path = tmp_path / "evidence.md"
    record = routing_record("attempt")
    record["usage"]["tokens_in"] = 0
    fence = chr(96) * 3
    write_lf(path, "# Evidence\n\n<!-- routing-evidence:v1 -->\n" + fence + "json\n" + json.dumps(record) + "\n" + fence + "\n")
    report = check.check_paths([path])
    assert "routing-invalid" in rules_of(report)


def test_routing_unknown_field_is_only_a_note():
    record = routing_record("classification")
    record["invented_field"] = "ignored"
    problems = check.routing_record_problems(record, set())
    assert problems == [("routing-unknown", "record.invented_field: unknown field")]


def pilot_manifest() -> dict:
    return {
        "schema": 1,
        "policy_hash": "a" * 64,
        "source_coverage": {
            "status": "complete", "ledger_refs": ["ledger:call-1"],
            "reconciliation_ref": "review:join-1", "reason": None
        },
        "tasks": [{
            "task_ref": "SPR-01",
            "document_refs": ["PROGRESS.md"],
            "required_classification_refs": ["classification-1"],
            "assignment_refs": ["assignment-1"],
            "expected_attempt_refs": ["attempt-record-1"]
        }]
    }


def pilot_records() -> list:
    return [
        {"record": routing_record("classification"), "document_ref": "PROGRESS.md"},
        {"record": routing_record("attempt"), "document_ref": "PROGRESS.md"}
    ]


def routing_approved_override(classification: dict, *, model=None, effort=None, expiry=None) -> None:
    classification["assignment"]["override"] = {
        "decision_ref": "owner:1", "owner_quote": "Use this pin for TK1",
        "approved_at": "2026-10-12T09:00:00Z", "scope_kind": "work_item",
        "scope_ref": "TK1", "status": "approved", "model_override": model,
        "effort_override": effort, "constraints": [], "expiry": expiry,
    }
    for key, value in (("model_override", model), ("effort_override", effort), ("expiry", expiry)):
        if value is None:
            classification["unknown_reasons"][f"assignment.override.{key}"] = "not_applicable: field not pinned"
    classification["decision"]["override_ref"] = "owner:1"
    classification["notification"]["approval_ref"] = "owner:1"
    if model is not None:
        classification["notification"]["model"] = model
    if effort is not None:
        classification["effort"]["effort_requested"] = effort
        classification["effort"]["effort_source"] = "human_override"
        classification["effort"]["override_ref"] = "owner:1"
        classification["notification"]["native_effort"] = effort


def routing_handoff_bundle(receiver_total=0, receiver_cycle=0) -> tuple[list, dict]:
    records = pilot_records()
    first = records[1]["record"]
    first["repair_history"].update(repair_cycle_index=3, total_repair_cycles=3)
    first["outcome"].update(first_error_ref="error:one", root_cause_ref="cause:one",
                            repair_rounds=3, escalations=["handoff:one"])
    first["quality"]["acceptance_pass"] = False
    first["notification"]["event_kind"] = "handoff"
    second_classification = routing_record("classification")
    second_classification["record_ref"] = "classification-2"
    second_classification["assignment"]["assignment_ref"] = "assignment-2"
    second_classification["notification"].update(notification_ref="notice-2", assignment_ref="assignment-2",
                                                notified_at="2026-10-12T10:02:30Z", event_kind="handoff")
    second = routing_record("attempt")
    second["record_ref"] = "attempt-record-2"
    second["identity"].update(attempt_id="attempt-2", assignment_ref="assignment-2")
    second["notification"].update(notification_ref="notice-2", assignment_ref="assignment-2",
                                  notified_at="2026-10-12T10:02:30Z", event_kind="handoff")
    second["time"].update(started_at="2026-10-12T10:03:00Z", finished_at="2026-10-12T10:04:00Z")
    second["repair_history"].update(repair_cycle_index=receiver_cycle, total_repair_cycles=receiver_total,
                                    assignment_history=["assignment-1", "assignment-2"])
    second["outcome"].update(first_error_ref="error:one", root_cause_ref="cause:one",
                             repair_rounds=receiver_cycle)
    records.extend([{"record": second_classification, "document_ref": "PROGRESS.md"},
                    {"record": second, "document_ref": "PROGRESS.md"}])
    manifest = pilot_manifest()
    manifest["tasks"][0].update(required_classification_refs=["classification-1", "classification-2"],
                                assignment_refs=["assignment-1", "assignment-2"],
                                expected_attempt_refs=["attempt-record-1", "attempt-record-2"])
    return records, manifest


def routing_cli_bundle(tmp_path, records: list, manifest: dict):
    root = tmp_path / "pilot"
    root.mkdir()
    fence = chr(96) * 3
    blocks = ["<!-- routing-evidence:v1 -->\n" + fence + "json\n" + json.dumps(entry["record"])
              + "\n" + fence for entry in records]
    write_lf(root / "evidence.md", "# Evidence\n\n" + "\n\n".join(blocks) + "\n")
    manifest["tasks"][0]["document_refs"] = ["evidence.md"]
    manifest_path = root / "pilot.manifest.json"
    write_lf(manifest_path, json.dumps(manifest))
    return run_script("check.py", str(root), "--routing-manifest", str(manifest_path))


def test_routing_pilot_complete_bundle_is_valid():
    assert check.routing_bundle_problems(pilot_records(), pilot_manifest()) == []


def test_routing_pilot_missing_marker_fails(tmp_path):
    root = tmp_path / "pilot"
    root.mkdir()
    write_lf(root / "PROGRESS.md", "# Progress\n\nNo routing block.\n")
    manifest = root / "pilot.manifest.json"
    write_lf(manifest, json.dumps(pilot_manifest()))
    result = run_script("check.py", str(root), "--routing-manifest", str(manifest))
    assert result.returncode == 1 and "[routing-missing]" in result.stdout


def test_routing_pilot_missing_assignment_or_attempt_fails():
    records = pilot_records()
    assert "routing-missing" in {code for code, _ in check.routing_bundle_problems(records[:1], pilot_manifest())}
    records[0]["record"]["assignment"]["assignment_ref"] = "wrong-assignment"
    assert "routing-missing" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


def test_routing_pilot_duplicate_record_fails():
    records = pilot_records()
    records.append(records[1].copy())
    assert "routing-duplicate" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


def test_routing_pilot_manifest_invalid_fails(tmp_path):
    root = tmp_path / "pilot"
    root.mkdir()
    write_lf(root / "PROGRESS.md", "# Progress\n")
    manifest = root / "pilot.manifest.json"
    write_lf(manifest, "{bad")
    result = run_script("check.py", str(root), "--routing-manifest", str(manifest))
    assert result.returncode != 0 and "[routing-manifest-invalid]" in result.stdout


def test_routing_pilot_attempt_membership_uses_record_ref():
    records = pilot_records()
    records[1]["record"]["record_ref"] = "attempt-unlisted"
    assert "routing-missing" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}
    records = pilot_records()
    records[1]["record"]["identity"]["attempt_id"] = "runtime-identity-distinct"
    assert check.routing_bundle_problems(records, pilot_manifest()) == []


def test_routing_pilot_rejects_unlisted_classification_and_attempt():
    records = pilot_records()
    records[0]["record"]["record_ref"] = "classification-unlisted"
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}
    records = pilot_records()
    records.append({"record": routing_record("attempt"), "document_ref": "PROGRESS.md"})
    records[-1]["record"]["record_ref"] = "attempt-unlisted"
    records[-1]["record"]["identity"]["attempt_id"] = "runtime-identity-distinct"
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


@pytest.mark.parametrize("field,bad", [("notified_at", 42), ("notified_at", "2026-13-99T29:61:61Z")])
def test_routing_bad_notice_timestamp_is_finding(field, bad):
    record = routing_record("attempt")
    record["notification"][field] = bad
    assert "routing-invalid" in routing_codes(record)


def test_routing_bad_policy_hash_is_finding_without_crash():
    records = pilot_records()
    records[1]["record"]["policy_hash"] = []
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


@pytest.mark.parametrize("path,bad", [
    (("schema",), True),
    (("axes", "ambiguity", "ordinal"), False),
    (("decision", "difficulty_level"), True),
    (("decision", "topology_evidence", "context_transfer"), False),
    (("effort", "effort_level"), True),
])
def test_routing_json_schema_rejects_bool_as_integer(path, bad):
    record = routing_record("classification")
    target = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = bad
    assert any(code == "routing-invalid" and f"record.{'.'.join(path)}" in message
               for code, message in check.routing_record_problems(record, set()))


def test_routing_manifest_rejects_boolean_schema():
    manifest = pilot_manifest()
    manifest["schema"] = True
    assert "routing-manifest-invalid" in {code for code, _ in check.routing_bundle_problems(pilot_records(), manifest)}


@pytest.mark.parametrize("key,bad", [
    ("ledger_refs", "not-array"), ("ledger_refs", ["../private"]),
    ("ledger_refs", ["ledger:one", "ledger:one"]),
    ("reconciliation_ref", 123), ("reconciliation_ref", "../private"),
])
def test_routing_manifest_rejects_invalid_source_coverage(key, bad):
    manifest = pilot_manifest()
    manifest["source_coverage"][key] = bad
    assert "routing-manifest-invalid" in {code for code, _ in check.routing_bundle_problems(pilot_records(), manifest)}


def test_routing_manifest_rejects_invalid_candidate_hash():
    manifest = pilot_manifest()
    manifest["candidate_policy_hash"] = []
    assert "routing-manifest-invalid" in {code for code, _ in check.routing_bundle_problems(pilot_records(), manifest)}


def test_routing_cli_manifest_reports_bad_record_without_traceback(tmp_path):
    root = tmp_path / "pilot"
    root.mkdir()
    record = routing_record("attempt")
    record["notification"]["notified_at"] = 42
    record["policy_hash"] = []
    fence = chr(96) * 3
    write_lf(root / "evidence.md", "# Evidence\n\n<!-- routing-evidence:v1 -->\n"
             + fence + "json\n" + json.dumps(record) + "\n" + fence + "\n")
    manifest = root / "pilot.manifest.json"
    write_lf(manifest, json.dumps(pilot_manifest()))
    result = run_script("check.py", str(root), "--routing-manifest", str(manifest))
    assert result.returncode == 1 and "[routing-invalid]" in result.stdout
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("bad", [[], {}])
def test_routing_bundle_bad_identity_assignment_is_finding(bad):
    records = pilot_records()
    records[1]["record"]["identity"]["assignment_ref"] = bad
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


@pytest.mark.parametrize("bad", [[], {}])
def test_routing_cli_bad_identity_assignment_has_no_traceback(tmp_path, bad):
    root = tmp_path / "pilot"
    root.mkdir()
    record = routing_record("attempt")
    record["identity"]["assignment_ref"] = bad
    fence = chr(96) * 3
    write_lf(root / "evidence.md", "# Evidence\n\n<!-- routing-evidence:v1 -->\n"
             + fence + "json\n" + json.dumps(record) + "\n" + fence + "\n")
    manifest = pilot_manifest()
    manifest["tasks"][0]["document_refs"] = ["evidence.md"]
    manifest_path = root / "pilot.manifest.json"
    write_lf(manifest_path, json.dumps(manifest))
    result = run_script("check.py", str(root), "--routing-manifest", str(manifest_path))
    assert result.returncode == 1 and "[routing-invalid]" in result.stdout
    assert "Traceback" not in result.stderr


def test_routing_unknown_axis_cannot_supply_zero_ordinal_or_difficulty():
    record = routing_record("classification")
    record["axes"]["scope_dependencies"]["value"] = None
    record["unknown_reasons"]["axes.scope_dependencies.value"] = "unknown"
    assert "routing-invalid" in routing_codes(record)


def test_routing_unknown_axis_keeps_difficulty_unknown():
    record = routing_record("classification")
    record["axes"]["scope_dependencies"]["value"] = None
    record["axes"]["scope_dependencies"]["ordinal"] = None
    record["decision"]["difficulty_level"] = None
    record["unknown_reasons"].update({
        "axes.scope_dependencies.value": "unknown",
        "axes.scope_dependencies.ordinal": "unknown",
        "decision.difficulty_level": "unknown technical axis",
    })
    assert check.routing_record_problems(record, set()) == []


@pytest.mark.parametrize("path", [
    ("time", "active_ms"), ("usage", "quota_used"), ("cost", "api_equivalent_usd"),
])
@pytest.mark.parametrize("bad", [float("nan"), float("inf")], ids=["nan", "positive-infinity"])
def test_routing_pure_validator_rejects_nonfinite_telemetry(path, bad):
    record = routing_record("attempt")
    record[path[0]][path[1]] = bad
    if path[0] == "usage":
        record["usage"]["usage_source"] = "runtime:usage"
    assert "routing-invalid" in routing_codes(record)


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "1e999"])
def test_routing_cli_rejects_nonfinite_telemetry(tmp_path, literal):
    path = tmp_path / "evidence.md"
    record = routing_record("attempt")
    record["time"]["active_ms"] = 0
    encoded = json.dumps(record).replace('"active_ms": 0', '"active_ms": ' + literal, 1)
    fence = chr(96) * 3
    write_lf(path, "# Evidence\n\n<!-- routing-evidence:v1 -->\n" + fence + "json\n"
             + encoded + "\n" + fence + "\n")
    result = run_script("check.py", str(path))
    assert result.returncode == 1 and "[routing-invalid]" in result.stdout
    assert "Traceback" not in result.stderr


def test_routing_approved_model_pin_must_reach_attempt_and_cli(tmp_path):
    records = pilot_records()
    routing_approved_override(records[0]["record"], model="model-example")
    records[1]["record"]["dispatch"].update(requested_model="another-model", actual_model="another-model")
    assert all(check.routing_record_problems(entry["record"], set()) == [] for entry in records)
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}
    result = routing_cli_bundle(tmp_path, records, pilot_manifest())
    assert result.returncode == 1 and "[routing-invalid]" in result.stdout and "Traceback" not in result.stderr


def test_routing_approved_effort_pin_is_independent_of_model():
    records = pilot_records()
    routing_approved_override(records[0]["record"], effort="high")
    assert all(check.routing_record_problems(entry["record"], set()) == [] for entry in records)
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


def test_routing_approved_effort_pin_accepts_matching_effort_without_model_pin():
    records = pilot_records()
    routing_approved_override(records[0]["record"], effort="high")
    attempt = records[1]["record"]
    attempt["effort"].update(effort_requested="high", effort_source="human_override", override_ref="owner:1")
    attempt["notification"].update(native_effort="high", approval_ref="owner:1")
    assert check.routing_bundle_problems(records, pilot_manifest()) == []


def test_routing_assignment_cannot_change_work_item_or_notice_scope():
    records = pilot_records()
    records[1]["record"]["work_item_ref"] = "TK999"
    records[1]["record"]["notification"]["scope_ref"] = "TK999"
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


def test_routing_assignment_config_and_unannounced_model_change_fail():
    records = pilot_records()
    records[1]["record"]["plan_hash"] = "d" * 64
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}
    records = pilot_records()
    records[1]["record"]["notification"]["model"] = "another-model"
    records[1]["record"]["dispatch"]["requested_model"] = "another-model"
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


def test_routing_model_change_with_later_notice_is_valid_without_pin():
    records = pilot_records()
    attempt = records[1]["record"]
    attempt["notification"].update(model="another-model", event_kind="model_change",
                                   notified_at="2026-10-12T10:00:30Z")
    attempt["dispatch"]["requested_model"] = "another-model"
    assert check.routing_bundle_problems(records, pilot_manifest()) == []


def test_routing_malformed_attempt_decision_cannot_crash_pin_join():
    records = pilot_records()
    routing_approved_override(records[0]["record"], model="model-example")
    records[1]["record"]["notification"]["approval_ref"] = "owner:1"
    records[1]["record"]["decision"] = []
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


def test_routing_expired_model_pin_allows_new_requested_model():
    records = pilot_records()
    routing_approved_override(records[0]["record"], model="model-example", expiry="2026-10-12T10:00:30Z")
    attempt = records[1]["record"]
    attempt["notification"].update(notified_at="2026-10-12T10:00:45Z", event_kind="model_change",
                                   model="another-model")
    attempt["dispatch"]["requested_model"] = "another-model"
    assert check.routing_bundle_problems(records, pilot_manifest()) == []


def test_routing_new_assignment_pin_can_change_model_and_keep_actual_mismatch():
    records = pilot_records()
    classification, attempt = records[0]["record"], records[1]["record"]
    classification["record_ref"] = "classification-2"
    classification["assignment"]["assignment_ref"] = "assignment-2"
    classification["notification"]["assignment_ref"] = "assignment-2"
    routing_approved_override(classification, model="another-model")
    attempt["identity"]["assignment_ref"] = "assignment-2"
    attempt["repair_history"]["assignment_history"] = ["assignment-2"]
    attempt["notification"].update(assignment_ref="assignment-2", model="another-model",
                                   approval_ref="owner:1")
    attempt["decision"]["override_ref"] = "owner:1"
    attempt["dispatch"].update(requested_model="another-model", actual_model="runtime-different",
                               actual_model_source="native:call-1")
    manifest = pilot_manifest()
    manifest["tasks"][0].update(required_classification_refs=["classification-2"],
                                assignment_refs=["assignment-2"])
    assert check.routing_bundle_problems(records, manifest) == []


def test_routing_handoff_total_cannot_reset_in_bundle_or_cli(tmp_path):
    records, manifest = routing_handoff_bundle(receiver_total=0, receiver_cycle=0)
    assert all(check.routing_record_problems(entry["record"], set()) == [] for entry in records)
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, manifest)}
    result = routing_cli_bundle(tmp_path, records, manifest)
    assert result.returncode == 1 and "[routing-invalid]" in result.stdout and "Traceback" not in result.stderr


def test_routing_handoff_first_receiver_repair_cannot_restart_total():
    records, manifest = routing_handoff_bundle(receiver_total=1, receiver_cycle=1)
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, manifest)}


def test_routing_receiver_can_reset_local_cycle_and_keep_total():
    records, manifest = routing_handoff_bundle(receiver_total=3, receiver_cycle=0)
    assert check.routing_bundle_problems(records, manifest) == []


def test_routing_receiver_repair_increments_global_total():
    records, manifest = routing_handoff_bundle(receiver_total=4, receiver_cycle=1)
    assert check.routing_bundle_problems(records, manifest) == []


def test_routing_handoff_missing_order_or_cause_is_not_verified():
    records, manifest = routing_handoff_bundle(receiver_total=3)
    records[-1]["record"]["time"]["started_at"] = None
    records[-1]["record"]["unknown_reasons"]["time.started_at"] = "unknown ordering"
    assert "routing-missing" in {code for code, _ in check.routing_bundle_problems(records, manifest)}
    records, manifest = routing_handoff_bundle(receiver_total=3)
    records[-1]["record"]["outcome"]["root_cause_ref"] = None
    assert "routing-missing" in {code for code, _ in check.routing_bundle_problems(records, manifest)}


def test_routing_permission_first_error_is_not_a_repair_cycle():
    records = pilot_records()
    attempt = records[1]["record"]
    attempt["outcome"].update(first_error_ref="error:permission", failure_class="permission")
    assert check.routing_bundle_problems(records, pilot_manifest()) == []


def test_routing_bundle_malformed_document_wrapper_is_finding():
    records = pilot_records()
    records[0]["document_ref"] = []
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, pilot_manifest())}


def routing_same_assignment_sequence(*, event="dispatch", acceptance=False, regression=False):
    """Two distinct, ordered attempts; the second claims a hidden fourth repair."""
    records = pilot_records()
    first = records[1]["record"]
    first["repair_history"].update(repair_cycle_index=3, total_repair_cycles=3)
    first["outcome"].update(first_error_ref="error:one", root_cause_ref="cause:one",
                            failure_class="capability", repair_rounds=3, escalations=["handoff:one"],
                            regressions=["regression:one"] if regression else [])
    first["quality"]["acceptance_pass"] = acceptance
    first["notification"]["event_kind"] = "handoff"
    second = json.loads(json.dumps(first))
    second["record_ref"] = "attempt-record-2"
    second["identity"]["attempt_id"] = "attempt-2"
    second["notification"].update(notification_ref="notice-2", event_kind=event,
                                  notified_at="2026-10-12T10:02:30Z")
    second["time"].update(started_at="2026-10-12T10:03:00Z", finished_at="2026-10-12T10:04:00Z")
    second["repair_history"]["total_repair_cycles"] = 4
    second["outcome"].update(repair_rounds=4, regressions=[],
                             escalations=["handoff:one"] if event == "handoff" else [])
    second["quality"]["acceptance_pass"] = True
    records.append({"record": second, "document_ref": "PROGRESS.md"})
    manifest = pilot_manifest()
    manifest["tasks"][0]["expected_attempt_refs"].append("attempt-record-2")
    return records, manifest


@pytest.mark.parametrize("event", ["handoff", "dispatch"])
def test_routing_failed_ceiling_cannot_hide_fourth_repair_in_bundle_and_cli(tmp_path, event):
    records, manifest = routing_same_assignment_sequence(event=event)
    assert all(check.routing_record_problems(entry["record"], set()) == [] for entry in records)
    problems = check.routing_bundle_problems(records, manifest)
    result = routing_cli_bundle(tmp_path, records, manifest)
    assert "routing-invalid" in {code for code, _ in problems}, (problems, result.stdout)
    assert result.returncode == 1 and "[routing-invalid]" in result.stdout and "Traceback" not in result.stderr


def test_routing_ceiling_regression_stops_even_when_acceptance_passed():
    records, manifest = routing_same_assignment_sequence(acceptance=True, regression=True)
    problems = check.routing_bundle_problems(records, manifest)
    assert any(code == "routing-invalid" and "đã dừng" in message for code, message in problems)


def test_routing_success_at_third_repair_needs_no_handoff(tmp_path):
    records, manifest = routing_same_assignment_sequence()
    first, second = records[1]["record"], records[2]["record"]
    first["repair_history"].update(repair_cycle_index=2, total_repair_cycles=2)
    first["outcome"].update(repair_rounds=2, escalations=[])
    first["notification"]["event_kind"] = "dispatch"
    second["repair_history"]["total_repair_cycles"] = 3
    second["outcome"]["repair_rounds"] = 3
    assert all(check.routing_record_problems(entry["record"], set()) == [] for entry in records)
    assert check.routing_bundle_problems(records, manifest) == []
    result = routing_cli_bundle(tmp_path, records, manifest)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("receiver_cycle,receiver_total", [(0, 3), (1, 4)])
def test_routing_ceiling_handoff_receiver_retains_history_in_cli(tmp_path, receiver_cycle, receiver_total):
    records, manifest = routing_handoff_bundle(receiver_total=receiver_total, receiver_cycle=receiver_cycle)
    assert check.routing_bundle_problems(records, manifest) == []
    result = routing_cli_bundle(tmp_path, records, manifest)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("cycle", [1, 3])
def test_routing_permission_observation_preserves_nonzero_past_repairs(tmp_path, cycle):
    records, manifest = routing_same_assignment_sequence(event="handoff")
    for entry in records[1:]:
        entry["record"]["repair_history"].update(repair_cycle_index=cycle, total_repair_cycles=cycle)
        entry["record"]["outcome"]["repair_rounds"] = cycle
    second = records[2]["record"]
    second["outcome"]["failure_class"] = "permission"
    second["quality"]["acceptance_pass"] = False
    assert all(check.routing_record_problems(entry["record"], set()) == [] for entry in records)
    assert check.routing_bundle_problems(records, manifest) == []
    result = routing_cli_bundle(tmp_path, records, manifest)
    assert result.returncode == 0, result.stdout


def test_routing_observation_does_not_clear_stopped_assignment():
    records, manifest = routing_same_assignment_sequence()
    observation = records[2]["record"]
    observation["repair_history"]["total_repair_cycles"] = 3
    observation["outcome"].update(repair_rounds=3, failure_class=None)
    observation["quality"]["review_findings"] = ["review:clarification"]
    assert check.routing_bundle_problems(records, manifest) == []
    third = json.loads(json.dumps(observation))
    third["record_ref"] = "attempt-record-3"
    third["identity"]["attempt_id"] = "attempt-3"
    third["notification"].update(notification_ref="notice-3", notified_at="2026-10-12T10:04:30Z")
    third["time"].update(started_at="2026-10-12T10:05:00Z", finished_at="2026-10-12T10:06:00Z")
    third["repair_history"]["total_repair_cycles"] = 4
    third["outcome"]["repair_rounds"] = 4
    records.append({"record": third, "document_ref": "PROGRESS.md"})
    manifest["tasks"][0]["expected_attempt_refs"].append("attempt-record-3")
    problems = check.routing_bundle_problems(records, manifest)
    assert any(code == "routing-invalid" and "đã dừng" in message for code, message in problems)
    # Scanned Markdown order is not execution order.
    assert check.routing_bundle_problems(list(reversed(records)), manifest) == problems


@pytest.mark.parametrize("counter", ["total", "rounds", "cycle", "history"])
def test_routing_same_assignment_counter_deltas_must_agree(counter):
    records, manifest = routing_same_assignment_sequence(acceptance=True)
    first, second = records[1]["record"], records[2]["record"]
    for record in (first, second):
        record["repair_history"].update(repair_cycle_index=1, total_repair_cycles=1)
        record["outcome"].update(repair_rounds=1, escalations=[])
        record["notification"]["event_kind"] = "dispatch"
    if counter == "total":
        second["repair_history"]["total_repair_cycles"] = 2
    elif counter == "rounds":
        second["outcome"]["repair_rounds"] = 2
    elif counter == "cycle":
        second["repair_history"]["repair_cycle_index"] = 0
    else:
        second["repair_history"]["assignment_history"] = ["fabricated-prior", "assignment-1"]
    assert "routing-invalid" in {code for code, _ in check.routing_bundle_problems(records, manifest)}


def test_routing_duplicate_attempt_is_not_an_additional_observation():
    records, manifest = routing_same_assignment_sequence()
    records[2]["record"]["identity"]["attempt_id"] = "attempt-1"
    records[2]["record"]["repair_history"]["total_repair_cycles"] = 3
    records[2]["record"]["outcome"]["repair_rounds"] = 3
    assert "routing-duplicate" in {code for code, _ in check.routing_bundle_problems(records, manifest)}


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


def test_researcher_role_is_executor(tmp_path):
    """Khoá `researcher` là vai thực thi: `check` không báo `roles-invalid` cho nó."""
    root = make_sprint(tmp_path)
    path = root / "SPEC.md"
    text = path.read_text(encoding="utf-8")
    old = "  business-reviewer: [T1, agent-c]\n"
    assert old in text
    write_lf(path, text.replace(old, old + "  researcher: [T3, agent-g]\n", 1))
    report = check.check_paths([root])
    assert not [f for f in report.findings if f.rule == "roles-invalid"], [f.render() for f in report.findings]


# --- Duyệt thay tại cổng (SPEC 7.3) -----------------------------------------------------------------------


def test_delegated_gate_valid_has_no_findings(tmp_path):
    root = make_sprint(tmp_path)
    delegate_plan(root)
    report = check.check_paths([root])
    assert codes(report.findings) == [], [f.render() for f in report.findings]
    assert report.exit_code == 0


def test_delegated_gate_report_scope(tmp_path):
    root = make_sprint(tmp_path)
    delegate_report(root)
    report = check.check_paths([root])
    assert codes(report.findings) == [], [f.render() for f in report.findings]
    assert report.exit_code == 0


@pytest.mark.parametrize("old,new", [
    ("expires: sprint_end", "expires: 2026-02-01"),  # hạn đúng ngày cổng vẫn còn hiệu lực
    ("grant_at: 2026-02-01 08:30 +07", "grant_at: 2026-02-01"),  # ngày không giờ: so theo ngày
    ("grant_at: 2026-02-01 08:30 +07", "grant_at: 2026-02-01 01:30 +0000"),  # cùng một lúc 08:30 +07, múi giờ khác
    ("grant_at: 2026-02-01 08:30 +07", "grant_at: 2026-01-31 20:00 -05:00"),  # múi giờ âm, dạng +HH:MM
    ("revoked_at: null", "revoked_at: 2026-02-01 09:30 +07"),  # thu hồi sau cổng: cổng vẫn hợp lệ
    ("files: []", "files: [AGENTS.md]"),
])
def test_delegation_boundary_values_stay_valid(tmp_path, old, new):
    root = make_sprint(tmp_path)
    delegate_plan(root)
    _rewrite(root / "PLAN.md", old, new)
    assert codes(check.check_paths([root]).findings) == []


def test_delegation_rules_stay_quiet_while_gate_is_pending(tmp_path):
    root = make_sprint(tmp_path)
    delegate_plan(root)
    _rewrite(root / "PLAN.md", "gate_1: approved", "gate_1: pending")
    _rewrite(root / "PLAN.md", "scope: [gate_1]", "scope: []")
    assert "gate-delegation-invalid" not in codes(check.check_paths([root]).findings)


def test_delegation_stops_at_first_problem_per_gate(tmp_path):
    root = make_sprint(tmp_path)
    delegate_plan(root)
    _rewrite(root / "PLAN.md", "tier: T1", "tier: T3")
    _rewrite(root / "PLAN.md", "scope: [gate_1]", "scope: []")
    hits = [f for f in check.check_paths([root]).findings if f.rule == "gate-delegation-invalid"]
    assert len(hits) == 1, [f.render() for f in hits]


def test_delegated_spec_does_not_need_the_record_section(tmp_path):
    """SPEC không có mục bản ghi: bản ghi nằm ở PLAN; khối đủ ở SPEC không bị đòi mục bản ghi."""
    root = make_sprint(tmp_path)
    _rewrite(root / "SPEC.md", 'gate_1_quote: "duyệt"\n', (
        'gate_1_quote: "duyệt thay: chọn phương án a — xem mục Bản ghi duyệt thay ở PLAN"\n'
        "gate_1_mode: delegated\n"
        "delegation:\n"
        '  grant: "Cho phép T1 duyệt thay Cổng 1 của SPR-03 tới hết sprint."\n'
        "  grant_at: 2026-02-01 08:30 +07\n"
        "  scope: [gate_1]\n"
        "  expires: sprint_end\n"
        "  by: agent-c\n"
        "  tier: T1\n"
        "  files: []\n"
        "  revoked_at: null\n"))
    assert codes(check.check_paths([root]).findings) == []


def test_delegation_record_labels_must_sit_in_the_record_section(tmp_path):
    """Nhãn nằm ở mục khác phía sau không thay cho nhãn trong mục `Bản ghi duyệt thay`."""
    root = make_sprint(tmp_path)
    delegate_plan(root)
    _rewrite(root / "PLAN.md", "**Nếu sai thì tốn gì:**", "**Hậu quả:**", "\n## Phần khác\n\n- **Nếu sai thì tốn gì:** đặt nhầm chỗ.\n")
    hits = [f for f in check.check_paths([root]).findings if f.rule == "gate-delegation-invalid"]
    assert len(hits) == 1 and "Nếu sai thì tốn gì:" in hits[0].message, [f.render() for f in hits]


def test_delegation_record_may_precede_another_section(tmp_path):
    root = make_sprint(tmp_path)
    delegate_plan(root)
    _rewrite(root / "PLAN.md", "- Lời cấp:", "- Lời cấp:", "\n## Phần khác\n\nKhông có.\n")
    assert codes(check.check_paths([root]).findings) == []


def _add_tasks(root: Path, body: str) -> None:
    """Chèn các việc `TK` ngay trước mục `## Rủi ro` của PLAN."""
    path = root / "PLAN.md"
    write_lf(path, path.read_text(encoding="utf-8").replace("## Rủi ro", body + "\n## Rủi ro", 1))


def _task(code: str, input_line: str) -> str:
    return f"### {code} — Việc mẫu (→ FR1.1)\n\n- **Đầu vào:** {input_line}\n\n"


def test_task_order_flags_forward_input(tmp_path):
    root = make_sprint(tmp_path / "a")
    _add_tasks(root, _task("TK2", "TK3.") + _task("TK3", "TK1."))
    findings = check.check_paths([root]).findings
    hits = [f for f in findings if f.rule == "task-order"]
    assert "task-order" in codes(findings) and hits[0].level == "Phải sửa", [f.render() for f in findings]
    assert "TK2 trỏ TK3 ở Đầu vào" in hits[0].message
    assert check.check_paths([root]).exit_code == 1
    other = make_sprint(tmp_path / "b")
    _add_tasks(other, _task("TK2", "TK1.") + _task("TK3", "TK2–TK4."))
    assert "task-order" in codes(check.check_paths([other]).findings)  # đầu trên của dải là 4 ≥ 3


def test_task_order_ignores_parallel_mark(tmp_path):
    root = make_sprint(tmp_path)
    _add_tasks(root, _task("TK2", "TK1.") + _task("TK3", "TK2; chạy cùng được với TK4.") + _task("TK4", "TK2."))
    findings = check.check_paths([root]).findings
    assert "task-order" not in codes(findings), [f.render() for f in findings]


def test_task_order_parallel_mark_ignores_case(tmp_path):
    root = make_sprint(tmp_path)
    _add_tasks(root, _task("TK2", "TK1.") + _task("TK3", "TK2. Chạy cùng được với TK4.") + _task("TK4", "TK2."))
    findings = check.check_paths([root]).findings
    assert "task-order" not in codes(findings), [f.render() for f in findings]


def test_task_order_allows_parent_for_subtask(tmp_path):
    root = make_sprint(tmp_path)
    _add_tasks(root, _task("TK2", "TK1.") + _task("TK2.1", "TK2.") + _task("TK3", "TK2.1."))
    findings = check.check_paths([root]).findings
    assert "task-order" not in codes(findings), [f.render() for f in findings]


def test_task_gap_flags_missing_number(tmp_path):
    root = make_sprint(tmp_path)
    _add_tasks(root, _task("TK3", "TK1."))
    report = check.check_paths([root])
    assert "task-gap" in codes(report.findings) and report.exit_code == 0, [f.render() for f in report.findings]


def test_plan_goal_block_flags_missing_label(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "PLAN.md"
    text = path.read_text(encoding="utf-8")
    assert "**Rủi ro cần chú ý:**" in text
    write_lf(path, text.replace("**Rủi ro cần chú ý:**", "**Rủi ro:**", 1))
    report = check.check_paths([root])
    hits = [f for f in report.findings if f.rule == "plan-goal-block"]
    assert hits and hits[0].level == "Ghi chú" and "Rủi ro cần chú ý:" in hits[0].message, [f.render() for f in report.findings]
    assert report.exit_code == 0


def test_plan_goal_block_accepts_three_labels(tmp_path):
    root = make_sprint(tmp_path)
    assert "plan-goal-block" not in codes(check.check_paths([root]).findings)


def test_plain_quote_without_delegation_stays_clean(tmp_path):
    """Hồ sơ cũ: quote thường, không khoá mới → 0 phát hiện (không né, không báo oan)."""
    root = make_sprint(tmp_path)
    _rewrite(root / "PLAN.md", 'gate_1_quote: "duyệt"', 'gate_1_quote: "duyệt, chọn phương án a"')
    assert codes(check.check_paths([root]).findings) == []
