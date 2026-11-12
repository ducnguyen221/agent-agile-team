"""Kiểm "rác ở gốc" của `check --self` (SPR-19, SPR-17/FR16.2): file hoặc thư mục ở gốc repo **không được theo dõi và không bị
ignore** là rác (nhật ký phiên, bản nháp, nơi ghi nhầm); cache đã ignore (`.coverage`, `.venv`, `.tmp`, `.pytest_cache`,
`__pycache__`, `.worktrees`) không tính. Repo tạm dựng ở `tmp_path` bằng `git init`, không ghi vào gốc repo thật.
"""

from __future__ import annotations

import subprocess

import check

IGNORE = "/.venv/\n/.tmp/\n/.worktrees/\n.coverage\n.pytest_cache/\n__pycache__/\n"


def git(repo, *args):
    ident = ["-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", "-c", "core.hooksPath="]
    res = subprocess.run(["git", *ident, *args], cwd=repo, capture_output=True)
    assert res.returncode == 0, res.stderr.decode(errors="replace")


def git_repo(path):
    (path / "AGENTS.md").write_text("# luật\n", encoding="utf-8")
    (path / ".gitignore").write_text(IGNORE, encoding="utf-8")
    git(path, "init", "-q")
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", "init")
    return path


def test_clean_repo_has_no_root_junk(tmp_path):
    assert check.root_junk(git_repo(tmp_path)) == []


def test_untracked_file_at_root_is_junk(tmp_path):
    repo = git_repo(tmp_path)
    (repo / "junk-probe.txt").write_text("x", encoding="utf-8")
    assert check.root_junk(repo) == ["junk-probe.txt"]


def test_untracked_directory_at_root_is_junk(tmp_path):
    repo = git_repo(tmp_path)
    (repo / "scratch").mkdir()
    (repo / "scratch" / "a.txt").write_text("x", encoding="utf-8")
    assert check.root_junk(repo) == ["scratch/"]


def test_ignored_caches_are_not_junk(tmp_path):
    repo = git_repo(tmp_path)
    (repo / ".coverage").write_text("x", encoding="utf-8")
    for name in (".venv", ".tmp", ".worktrees", ".pytest_cache", "__pycache__"):
        (repo / name).mkdir()
        (repo / name / "f").write_text("x", encoding="utf-8")
    assert check.root_junk(repo) == []


def test_untracked_file_in_a_subfolder_is_not_root_junk(tmp_path):
    repo = git_repo(tmp_path)
    (repo / "docs").mkdir()
    (repo / "docs" / "keep.md").write_text("x", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs")
    (repo / "docs" / "new.md").write_text("x", encoding="utf-8")
    assert check.root_junk(repo) == []


def test_not_a_git_repo_reports_nothing(tmp_path):
    (tmp_path / "AGENTS.md").write_text("# luật\n", encoding="utf-8")
    (tmp_path / "junk-probe.txt").write_text("x", encoding="utf-8")
    assert check.root_junk(tmp_path) == []


def test_run_self_flags_root_junk_with_its_own_rule(tmp_path):
    repo = git_repo(tmp_path)
    (repo / "junk-probe.txt").write_text("x", encoding="utf-8")
    report = check.run_self(repo, None)
    hits = [f for f in report.findings if f.rule == "root-junk"]
    assert len(hits) == 1 and hits[0].level == "Phải sửa", [f.render() for f in report.findings]
    assert "junk-probe.txt" in hits[0].render()


def test_this_repo_has_no_root_junk():
    from conftest import REPO

    assert check.root_junk(REPO) == [], "gốc repo có rác chưa theo dõi và chưa ignore"
