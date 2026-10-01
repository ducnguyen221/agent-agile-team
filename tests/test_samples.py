"""Dự án mẫu `samples/`: sạch theo `check`, khối "Đang mở" đã cập nhật, và đột biến bị bắt."""

import shutil

from conftest import SAMPLES
import check
import index

PROJECT = SAMPLES / "order-desk"


def rules_of(report) -> set:
    return {f.rule for f in report.findings}


def test_samples_pass_check():
    report = check.check_paths([SAMPLES])
    assert [f.render() for f in report.findings] == []
    assert report.exit_code == 0
    assert report.checked >= 9


def test_sample_has_one_full_sprint_one_tiny_sprint_and_ledgers():
    plans = PROJECT / "docs" / "plans"
    full = [d for d in plans.iterdir() if d.is_dir() and (d / "REPORT.md").is_file()]
    assert len(full) == 1 and {p.name for p in full[0].iterdir()} == {"SPEC.md", "PLAN.md", "PROGRESS.md", "REPORT.md"}
    assert any((d / "SPRINT.md").is_file() for d in plans.iterdir() if d.is_dir())
    for rel in ("docs/plans/REQUESTS.md", "docs/plans/SPRINTS.md", "docs/specs/SPECS.md", ".agile.json"):
        assert (PROJECT / rel).is_file(), rel


def test_sample_open_blocks_are_fresh():
    assert index.main([str(PROJECT), "--check"]) == 0


def test_bare_code_inserted_into_sample_fails(tmp_path):
    root = tmp_path / "samples"
    shutil.copytree(SAMPLES, root)
    spec = next(root.rglob("SPEC.md"))
    spec.write_text(spec.read_text(encoding="utf-8") + "\nGhi chú thêm: D3.\n", encoding="utf-8", newline="\n")
    report = check.check_paths([root])
    assert report.exit_code == 1
    assert "id-bare-single-letter" in rules_of(report)


def test_nested_project_config_is_checked(tmp_path):
    root = tmp_path / "samples"
    shutil.copytree(SAMPLES, root)
    (root / "order-desk" / ".agile.json").write_text("{hỏng", encoding="utf-8")
    report = check.check_paths([root])
    assert report.exit_code == 2 and "config-syntax" in rules_of(report)
