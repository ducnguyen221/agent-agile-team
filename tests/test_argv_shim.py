"""Test cho scripts/git_shim.py và shims/ — rào kiểm argv thật (thử nghiệm SPR-16b). Chạy: python -m pytest -q tests/test_argv_shim.py"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import git_shim
from conftest import REPO

import oracle_harness as oracle
from test_autopilot_guard import protected_repo

SHIMS = REPO / "shims"
ON = {"AGENT_AGILE_SHIM": "1"}  # shim chỉ chặn trong phiên agent (biến này); không có thì chạy lệnh thật ngay


def _bash_works() -> bool:
    exe = shutil.which("bash")
    if exe is None:
        return False
    try:
        done = subprocess.run([exe, "-c", "echo ok"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0 and done.stdout.strip() == "ok"


BASH_OK = _bash_works()
needs_bash = pytest.mark.skipif(not BASH_OK, reason="không có bash chạy được (WSL stub của Windows không tính)")


def test_clean_path_drops_only_the_shim_directory(tmp_path):
    shim, other = tmp_path / "shims", tmp_path / "bin"
    shim.mkdir()
    other.mkdir()
    path = os.pathsep.join([str(shim), str(other), str(shim)])
    assert git_shim.clean_path(str(shim), path) == str(other)
    assert git_shim.clean_path(None, path) == path


def test_canonical_command_quotes_every_argument_and_lists_git_environment_first():
    assert git_shim.canonical_command("git", ["push", "--force", "origin", "a;b c"], {}) == "git push --force origin 'a;b c'"
    text = git_shim.canonical_command("git", ["status"], {"GIT_SSH_COMMAND": "ssh -x", "HOME": "/h", "GIT_TERMINAL_PROMPT": "0"})
    assert text == "GIT_SSH_COMMAND='ssh -x' git status"
    assert git_shim.canonical_command("gh", ["pr", "list"], {"GH_REPO": "o/r"}) == "GH_REPO=o/r gh pr list"


def test_decide_refuses_dangerous_argv_and_allows_reads(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    assert git_shim.decide("git", ["push", "--force", "origin", "main"], {}, str(repo))[0] is False
    ok, reason = git_shim.decide("git", ["push", "origin", "x"], {}, str(repo))
    assert ok is False and "git-fence" in reason  # shim không có tầng hỏi: lệnh "hỏi" cũng không chạy
    assert git_shim.decide("git", ["status", "-sb"], {}, str(repo)) == (True, "")
    assert git_shim.decide("git", ["-c", "x.y=a;b", "push", "--force", "origin", "main"], {}, str(repo))[0] is False


def test_decide_outside_a_protected_repo_changes_nothing(tmp_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    assert git_shim.decide("git", ["push", "--force", "origin", "main"], {}, str(plain)) == (True, "")


def test_main_refuses_unknown_tool_name():
    assert git_shim.main(["rm", "-rf", "x"]) == 2


@needs_bash
@pytest.mark.parametrize("cmd", [
    "xargs -I{} sh -c 'command git push origin x main' <<< x", "sh -c 'time '\\''git'\\'' push --force origin main'",
    "eval 'nice '\\''git'\\'' push origin main'", "for i in 1; do time git -c x.y=\"a;b\" push origin main; done",
    "git -c x.y=\"a;b\" push --force origin main", "bash -c 'echo a;git push --force origin main'",
    "echo \"x\n\";for i in 1; do GIT_TRACE=0 git -c x.y=\"a;b\" push --delete origin main; done", "g\"i\"t push --force origin main",
    "env FOO=1 'git' push origin x main",
])
def test_shim_blocks_the_shapes_that_reading_the_string_misses(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    stub = tmp_path / "stub"
    oracle.make_stub(stub)
    log = tmp_path / "log.txt"
    assert not oracle.danger_in(oracle.run_bash(cmd, repo, log, [SHIMS, stub], extra_env=ON)), cmd


@needs_bash
def test_shim_lets_ordinary_commands_reach_the_real_tool(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    stub = tmp_path / "stub"
    oracle.make_stub(stub)
    log = tmp_path / "log.txt"
    for cmd in ("git status", "git log --oneline -3", "git -c core.pager=cat log -1", "git commit -m 'msg (a); b'"):
        assert oracle.run_bash(cmd, repo, log, [SHIMS, stub], extra_env=ON).startswith("RUN "), cmd


@needs_bash
def test_differential_shim_has_no_miss_and_no_false_positive(tmp_path):
    """Đối chứng với bash thật trên lệnh sinh ngẫu nhiên (hạt cố định): argv nguy hiểm không bao giờ tới git thật, lệnh lành luôn tới."""
    n_danger, n_safe = int(os.environ.get("ORACLE_DANGER", "24")), int(os.environ.get("ORACLE_SAFE", "12"))
    danger, safe = oracle.build_cases(11, n_danger, n_safe)
    repo = protected_repo(tmp_path, branch="x")
    stub = tmp_path / "stub"
    oracle.make_stub(stub)
    log = tmp_path / "log.txt"
    missed = [c for c in danger if oracle.danger_in(oracle.run_bash(c, repo, log, [SHIMS, stub], extra_env=ON))]
    assert missed == []
    blocked = [c for c in safe if "RUN" in oracle.run_bash(c, repo, log, [stub]) and "RUN" not in oracle.run_bash(c, repo, log, [SHIMS, stub], extra_env=ON)]
    assert blocked == []


@needs_bash
def test_shim_is_transparent_without_the_agent_variable(tmp_path):
    """Người dùng ở terminal (không có AGENT_AGILE_SHIM) không bị ảnh hưởng: ngay cả lệnh nguy hiểm tới `git` thật nguyên vẹn."""
    repo = protected_repo(tmp_path, branch="x")
    stub = tmp_path / "stub"
    oracle.make_stub(stub)
    log = tmp_path / "log.txt"
    assert oracle.danger_in(oracle.run_bash("git push --force origin main", repo, log, [SHIMS, stub]))
    assert oracle.danger_in(oracle.run_bash("git push --force origin main", repo, log, [SHIMS, stub], extra_env={"AGENT_AGILE_SHIM": "0"}))
    assert not oracle.danger_in(oracle.run_bash("git push --force origin main", repo, log, [SHIMS, stub], extra_env=ON))


@needs_bash
def test_shim_skips_python_in_repos_without_any_protection_sign(tmp_path):
    """Đường tắt của wrapper: không có .agile.json/.tmp/autopilot.json từ thư mục hiện tại lên tới gốc repo thì chạy git thật ngay (không guard)."""
    from test_autopilot_guard import make_repo

    plain = make_repo(tmp_path, branch="x")
    stub = tmp_path / "stub"
    oracle.make_stub(stub)
    log = tmp_path / "log.txt"
    assert oracle.danger_in(oracle.run_bash("git push --force origin main", plain, log, [SHIMS, stub], extra_env=ON))


def test_clean_path_drops_every_shims_directory_not_only_its_own(tmp_path):
    """Hai bản plugin (hai thư mục shims/) cùng trên PATH không được gọi vòng nhau."""
    plug_a, plug_b = tmp_path / "a", tmp_path / "b"
    for plug in (plug_a, plug_b):
        (plug / "shims").mkdir(parents=True)
        (plug / "scripts").mkdir()
        (plug / "scripts" / "git_shim.py").write_text("", encoding="utf-8")
    real = tmp_path / "real"
    real.mkdir()
    path = os.pathsep.join([str(plug_a / "shims"), str(plug_b / "shims"), str(real)])
    assert git_shim.clean_path(str(plug_a / "shims"), path) == str(real)


@needs_bash
def test_two_shim_copies_on_path_do_not_call_each_other_forever(tmp_path):
    other = tmp_path / "other"
    shutil.copytree(SHIMS, other / "shims")
    (other / "scripts").mkdir()
    shutil.copy(REPO / "scripts" / "git_shim.py", other / "scripts" / "git_shim.py")
    repo = protected_repo(tmp_path, branch="x")
    stub = tmp_path / "stub"
    oracle.make_stub(stub)
    log = tmp_path / "log.txt"
    for extra in ({}, ON):  # biến tắt (chạy thẳng tới git thật) và bật (đi qua guard)
        out = oracle.run_bash("git status", repo, log, [SHIMS, other / "shims", stub], timeout=40, extra_env=extra)
        assert out.startswith("RUN "), extra


# SPR-18/TK3b: CI đỏ từ trước (main 07d2785, 16c) ở ubuntu/macOS/Windows — hai lỗi của chính bộ test, không phải của shim.
# (1) stub `git` giả không có bit chạy → `[ -x ]` của shim bỏ qua nó trên Linux/macOS, lệnh lành không tới "git" giả (log rỗng).
# (2) `subprocess.run(["bash", ...])` trên Windows tìm bash.exe ở System32 (stub WSL) trước PATH; dùng đường dẫn mà shutil.which đã thử chạy được.
@pytest.mark.skipif(os.name == "nt", reason="Windows không có bit chạy kiểu POSIX")
def test_make_stub_git_is_executable(tmp_path):
    stub = oracle.make_stub(tmp_path / "stub")
    assert os.access(stub, os.X_OK)


def test_run_bash_calls_the_bash_that_which_resolved_not_a_bare_name(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(oracle.shutil, "which", lambda name, *a, **k: "/probe/bin/bash" if name == "bash" else None)
    monkeypatch.setattr(oracle.subprocess, "run", lambda argv, **k: seen.append(argv))
    log = tmp_path / "log.txt"
    oracle.run_bash("true", tmp_path, log, [tmp_path])
    assert seen and seen[0][0] == "/probe/bin/bash"
