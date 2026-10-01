"""`check.py --self`: lõi sạch theo danh sách từ cấm ngoài repo, một thang mức, ngân sách `AGENTS.md`.

Danh sách từ cấm thật nằm ngoài repo (hợp đồng `AGENT_AGILE_DENYLIST` ở `tests/README.md`). Các test đột
biến dưới đây tự tạo danh sách tạm với một từ giả, nên chạy được trên mọi máy.
"""

import os
from pathlib import Path

import pytest

from conftest import REPO, run_script
import check

WORD = "zq-private-marker"


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "skills" / "demo" / "tests").mkdir(parents=True)
    (root / "method").mkdir()
    (root / "tests" / "fixtures").mkdir(parents=True)
    (root / "AGENTS.md").write_text("# Luật lõi\n\nNgắn gọn.\n", encoding="utf-8")
    (root / "README.md").write_text("# Repo\n\nSạch.\n", encoding="utf-8")
    return root


def denylist(tmp_path: Path, *words: str) -> Path:
    path = tmp_path / "deny.txt"
    path.write_text("# từ cấm thử\n\n" + "\n".join(words) + "\n", encoding="utf-8")
    return path


def rules_of(report) -> set:
    return {f.rule for f in report.findings}


def test_clean_repo_passes(tmp_path):
    root = make_repo(tmp_path)
    report = check.run_self(root, denylist(tmp_path, WORD))
    assert report.findings == [] and report.exit_code == 0
    assert report.denylist_status == "ok"


def test_denylist_word_is_caught_case_insensitively(tmp_path):
    root = make_repo(tmp_path)
    (root / "README.md").write_text("# Repo\n\nCó dấu ZQ-Private-Marker ở đây.\n", encoding="utf-8")
    report = check.run_self(root, denylist(tmp_path, WORD))
    hits = [f for f in report.findings if f.rule == "leak-denylist"]
    assert len(hits) == 1 and hits[0].line == 3 and hits[0].level == "Chặn"
    assert report.exit_code == 1
    assert WORD not in hits[0].render().lower(), "báo cáo không được in lại chính từ cấm"


def test_denylist_exemptions(tmp_path):
    root = make_repo(tmp_path)
    (root / "NOTICE").write_text(f"Copyright (c) 2026 {WORD}\n", encoding="utf-8")
    (root / "THIRD_PARTY.md").write_text(f"| nguồn | {WORD} |\n", encoding="utf-8")
    (root / "UPSTREAM.md").write_text(f"# Nguồn\n\n| `{WORD}/repo` | main |\n", encoding="utf-8")
    (root / "skills" / "demo" / "tests" / "pressure.md").write_text(f"---\nmodel: {WORD}\n---\n\nChạy bằng model `{WORD}`.\n", encoding="utf-8")
    assert check.run_self(root, denylist(tmp_path, WORD)).findings == []
    (root / "UPSTREAM.md").write_text(f"# Nguồn\n\nVăn xuôi nhắc {WORD}.\n", encoding="utf-8")
    assert rules_of(check.run_self(root, denylist(tmp_path, WORD))) == {"leak-denylist"}


def test_denylist_scans_non_markdown_and_fixtures(tmp_path):
    root = make_repo(tmp_path)
    (root / "tests" / "fixtures" / "x.json").write_text(f'{{"a": "{WORD}"}}\n', encoding="utf-8")
    assert rules_of(check.run_self(root, denylist(tmp_path, WORD))) == {"leak-denylist"}


def test_missing_denylist_is_not_configured_not_silent(tmp_path, capsys):
    root = make_repo(tmp_path)
    report = check.run_self(root, None)
    assert report.exit_code == 0 and report.denylist_status == "NOT_CONFIGURED"
    report = check.run_self(root, tmp_path / "không-có.txt")
    assert report.denylist_status == "NOT_CONFIGURED"
    code = check.main(["--self", "--root", str(root)], env={})
    captured = capsys.readouterr()
    assert code == 0
    assert "NOT_CONFIGURED" in captured.err and "AGENT_AGILE_DENYLIST" in captured.err


def test_main_reads_denylist_from_env(tmp_path, capsys):
    root = make_repo(tmp_path)
    (root / "README.md").write_text(f"{WORD}\n", encoding="utf-8")
    code = check.main(["--self", "--root", str(root)], env={"AGENT_AGILE_DENYLIST": str(denylist(tmp_path, WORD))})
    assert code == 1
    assert "[leak-denylist]" in capsys.readouterr().out


def test_agents_md_budget(tmp_path):
    root = make_repo(tmp_path)
    (root / "AGENTS.md").write_text("dòng\n" * 121, encoding="utf-8")
    assert "agents-md-budget" in rules_of(check.run_self(root, None))
    (root / "AGENTS.md").write_text(("x" * 100 + "\n") * 102, encoding="utf-8")  # 102 dòng, 10 302 byte
    assert "agents-md-budget" in rules_of(check.run_self(root, None))
    (root / "AGENTS.md").write_text("dòng\n" * 120, encoding="utf-8")
    assert "agents-md-budget" not in rules_of(check.run_self(root, None))


def test_old_scale_only_inside_conversion_table(tmp_path):
    root = make_repo(tmp_path)
    table = "| Mức | Nghĩa |\n|---|---|\n| Critical | x |\n"
    (root / "method" / "severity.md").write_text(table, encoding="utf-8")
    assert check.run_self(root, None).findings == []
    (root / "method" / "other.md").write_text(table, encoding="utf-8")
    assert rules_of(check.run_self(root, None)) == {"old-scale-label"}


def test_self_skips_fixtures_and_skill_scenarios_for_document_rules(tmp_path):
    root = make_repo(tmp_path)
    (root / "tests" / "fixtures" / "SPEC.md").write_text("Mã hỏng cố ý P1.\n", encoding="utf-8")
    (root / "skills" / "demo" / "tests" / "pressure.md").write_text("## ID1 — kịch bản\n", encoding="utf-8")
    assert check.run_self(root, None).findings == []
    (root / "skills" / "demo" / "SKILL.md").write_text("## ID1 — tiền tố tự chế\n", encoding="utf-8")
    assert rules_of(check.run_self(root, None)) == {"id-unknown-prefix"}


def test_this_repo_is_clean():
    report = check.run_self(REPO, None)
    assert [f.render() for f in report.findings if f.level in ("Chặn", "Phải sửa")] == []
    assert report.exit_code == 0


def test_this_repo_against_real_denylist():
    configured = os.environ.get("AGENT_AGILE_DENYLIST")
    if not configured or not Path(configured).is_file():
        pytest.skip("Chưa chạy: AGENT_AGILE_DENYLIST chưa đặt hoặc file không đọc được (tests/README.md)")
    report = check.run_self(REPO, Path(configured))
    assert report.denylist_status == "ok"
    assert [f.render() for f in report.findings if f.rule == "leak-denylist"] == []


def test_self_cli_standalone():
    result = run_script("check.py", "--self", env={"AGENT_AGILE_DENYLIST": ""})
    assert result.returncode == 0, result.stdout + result.stderr
    assert "NOT_CONFIGURED" in result.stderr
