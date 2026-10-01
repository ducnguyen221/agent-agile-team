"""`check.py` trên tài liệu sprint: bộ sạch thoát 0, mỗi ca hỏng cố ý bị bắt đúng mã luật (SC4)."""

import json
import shutil
from pathlib import Path

import pytest

from conftest import FIXTURES, REPO, run_script
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
        target.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    for rel, content in case.get("write", {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")


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
    report = check.check_paths([root])
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
    path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8", newline="\n")


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
    spec.write_text(text, encoding="utf-8", newline="\n")


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
    path.write_text(text, encoding="utf-8", newline="\n")
    hits = [f for f in check.check_paths([root]).findings if f.rule == "task-without-trace"]
    assert len(hits) == 1 and "TK5.1" in hits[0].message


def test_range_counts_for_trace_and_vr(tmp_path):
    root = make_sprint(tmp_path)
    spec = root / "SPEC.md"
    spec.write_text(
        spec.read_text(encoding="utf-8").replace(
            "| SC1 (xuất đủ cột) | File CSV có đủ ba cột | Test tự động của FR1 xanh |",
            "| SC1 (xuất đủ cột) | File CSV có đủ ba cột | Test tự động của FR1 xanh |\n"
            "| SC2 (có tiêu đề) | Có dòng tên cột | Test |\n| SC3 (UTF-8) | Mở được tiếng Việt | Test |",
            1,
        ),
        encoding="utf-8",
        newline="\n",
    )
    _set_report(root, "| SC1, FR1.1 |", "| SC1–SC3, FR1.1 |")
    assert check.check_paths([root]).findings == []


def test_risk_and_size_consistency(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "SPEC.md"
    path.write_text(path.read_text(encoding="utf-8").replace("risk_tags: []", "risk_tags: [secret]", 1), encoding="utf-8", newline="\n")
    messages = [f.message for f in check.check_paths([root]).findings if f.rule == "frontmatter-value"]
    assert any("risk_tags" in m for m in messages), messages


def test_bare_letter_inside_link_url_is_ignored(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "SPEC.md"
    text = path.read_text(encoding="utf-8").replace("- Xuất Excel.", "- Xuất Excel, xem [tài liệu](https://example.com/A1/B2).", 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    assert check.check_paths([root]).findings == []


def test_external_reference_with_slash_is_not_resolved(tmp_path):
    root = make_sprint(tmp_path)
    path = root / "PLAN.md"
    text = path.read_text(encoding="utf-8").replace("Đạt SC1 (xuất đủ cột).", "Đạt SC1 (xuất đủ cột); giữ FS-001/FR7.3.", 1)
    path.write_text(text, encoding="utf-8", newline="\n")
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
