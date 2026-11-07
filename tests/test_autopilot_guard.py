"""Test cho scripts/autopilot_guard.py — rào máy autopilot (hook PreToolUse). Chạy: python -m pytest -q tests/test_autopilot_guard.py"""

from __future__ import annotations

import io
import shutil
import json
import os
import sys

import pytest

import autopilot_guard
import check
from pathlib import Path

from conftest import REPO, SCRIPTS

ALL = list(check.AUTOPILOT_EXCLUSIONS)
WITHOUT_BRANCH = [e for e in ALL if e != "branch_merge_local"]


def make_repo(tmp_path, branch="main", marker=None, worktree=False):
    """Dựng repo giả: `.git/HEAD` ở nhánh `branch`; `marker` là dict (ghi JSON), chuỗi (ghi nguyên văn) hay None (không file dấu)."""
    repo = tmp_path / "repo"
    git = repo / ".git"
    git.mkdir(parents=True)
    (git / "HEAD").write_text("ref: refs/heads/{}\n".format(branch), encoding="utf-8")
    (repo / ".tmp").mkdir()
    if marker is not None:
        text = marker if isinstance(marker, str) else json.dumps(marker)
        (repo / ".tmp" / "autopilot.json").write_text(text, encoding="utf-8")
    return repo


def good_marker(exclusions=None):
    return {"level": "gate_1_2", "scope": ["gate_1", "gate_2"], "expires": "sprint_end",
            "exclusions": ALL if exclusions is None else exclusions, "grant_at": "2026-11-20 09:00 +07", "sprints": ["SPR-20"]}


def link_dir(target, link):
    """Symlink thư mục; Windows không đặc quyền thì dùng junction (`mklink /J`). Không được thì bỏ qua test."""
    try:
        os.symlink(target, link, target_is_directory=True)
        return
    except (OSError, NotImplementedError):
        pass
    if os.name == "nt":
        import subprocess
        done = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        if done.returncode == 0:
            return
    pytest.skip("không tạo được liên kết thư mục trên máy này")


def claude(cmd, cwd, tool="Bash"):
    return {"tool_name": tool, "tool_input": {"command": cmd}, "cwd": str(cwd)}


def run(fmt, payload, *extra):
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    out, err = io.StringIO(), io.StringIO()
    rc = autopilot_guard.main(["--format", fmt, *extra], stdin=io.StringIO(raw), stdout=out, stderr=err)
    return rc, out.getvalue(), err.getvalue()


def assert_blocked(repo, cmd, item):
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)
    assert "'{}'".format(item) in err and "cần người dùng nói trong chat — lệnh không chạy" in err


def assert_allowed(repo, cmd):
    rc, out, err = run("claude", claude(cmd, repo))
    assert (rc, out, err) == (0, "", ""), (cmd, rc, err)


# --- đối chiếu hằng với check.py -------------------------------------------------------------------------------

PINNED_EXCLUSIONS = {"push", "tag", "version", "main_merge", "publish", "license", "irreversible_delete", "rules_unlisted",
                     "user_soul", "secret", "auth", "network_fetch", "branch_merge_local"}


def test_guard_uses_check_exclusions():
    assert autopilot_guard.known_exclusions() == check.AUTOPILOT_EXCLUSIONS


def test_guard_exclusions_pinned_to_thirteen():
    """Bớt một mục ở `check.AUTOPILOT_EXCLUSIONS` sẽ tắt chặn im lặng: ghim danh sách viết tay để test đỏ."""
    assert len(PINNED_EXCLUSIONS) == 13
    assert set(autopilot_guard.known_exclusions()) == PINNED_EXCLUSIONS
    assert set(check.AUTOPILOT_EXCLUSIONS) == PINNED_EXCLUSIONS and len(check.AUTOPILOT_EXCLUSIONS) == 13


# --- các test PLAN -----------------------------------------------------------------------------------------------

def test_guard_no_marker_allows(tmp_path):
    repo = make_repo(tmp_path)
    assert_allowed(repo, "git push origin main")
    assert_allowed(repo, "rm -rf build")


def test_guard_blocks_push(tmp_path):
    repo = make_repo(tmp_path, marker=good_marker())
    assert_blocked(repo, "git push", "push")
    assert_blocked(repo, "git push origin spr-12", "push")
    assert_blocked(repo, "git -C ../other push", "push")
    assert_blocked(repo, "git.exe push", "push")
    assert_blocked(repo, "/usr/bin/git -c user.name=x push --force", "push")
    assert_blocked(repo, "GIT_TRACE=1 git push", "push")
    assert_blocked(repo, '"C:\\Program Files\\Git\\bin\\git.exe" push', "push")


def test_guard_blocks_tag(tmp_path):
    repo = make_repo(tmp_path, marker=good_marker())
    assert_blocked(repo, "git tag v1.2.0", "tag")
    assert_blocked(repo, "git tag -a v1.2.0 -m release", "tag")
    assert_blocked(repo, "git tag -f v1", "tag")
    assert_blocked(repo, "git tag -d v1", "irreversible_delete")
    assert_blocked(repo, "git tag --delete v1", "irreversible_delete")
    for readonly in ("git tag", "git tag -l", "git tag --list 'v1*'", "git tag -v v1", "git tag --contains HEAD",
                     "git tag --points-at HEAD", "git tag --merged", "git tag --no-merged", "git tag -n5"):
        assert_allowed(repo, readonly)


def test_guard_blocks_merge_on_main(tmp_path):
    repo = make_repo(tmp_path, branch="main", marker=good_marker(WITHOUT_BRANCH))
    assert_blocked(repo, "git merge spr-12", "main_merge")
    assert_blocked(repo, "git pull", "main_merge")
    assert_blocked(repo, "git pull origin main", "main_merge")
    master = make_repo(tmp_path / "m", branch="master", marker=good_marker(WITHOUT_BRANCH))
    assert_blocked(master, "git merge x", "main_merge")
    # merge --abort không gộp gì
    assert_allowed(repo, "git merge --abort")
    # compound: checkout/switch tới main rồi merge/pull, kể cả khi đang ở nhánh khác
    feature = make_repo(tmp_path / "f", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    assert_blocked(feature, "git checkout main && git merge spr-12", "main_merge")
    assert_blocked(feature, "git switch master; git pull", "main_merge")
    assert_allowed(feature, "git pull")  # nhánh sprint, không phải nhánh chính
    assert_allowed(feature, "git checkout other && git merge x")  # chỉ branch_merge_local lo, mà marker này cho gộp cục bộ


def test_guard_blocks_gh_pr_merge(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, "gh pr merge 12 --squash", "main_merge")
    assert_blocked(repo, "gh pr merge", "main_merge")
    assert_allowed(repo, "gh pr view 12")
    assert_allowed(repo, "gh pr list")


@pytest.mark.parametrize("cmd", [
    "rm -rf build", "rm -fr build", "rm -Rf build", "rm -r -f build", "rm --recursive build", "rm -r build",
    "rm -rfv build", "rm -fR build", "rm -r",  # không đích: vẫn chặn
    "git reset --hard", "git reset --hard HEAD~1", "git branch -D old", "git branch -fD old", "git branch --delete --force old",
    "git clean -fd", "git clean -f", "git clean --force -d", "git clean -xdf",
    "git worktree remove -f ../w", "git worktree remove --force ../w",
    "Remove-Item -Recurse -Force build", "Remove-Item build -Recurse", "remove-item -recurse build", "ri -r build",
    "rmdir /s /q build", "rd /S build", "rm -Recurse build", "del /s build",
])
def test_guard_blocks_rm_rf(tmp_path, cmd):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, cmd, "irreversible_delete")


def test_guard_safe_deletes_allowed(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("rm file.txt", "rm -f file.txt", "git branch -d merged", "git clean -n", "git reset --soft HEAD~1",
                "git worktree remove ../w", "Remove-Item file.txt -Force", "rmdir empty", "git status", "git log --oneline",
                "git commit -m 'fix git push docs'", "echo git push", "ls -la"):
        assert_allowed(repo, cmd)


def test_guard_blocks_compound_command(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, "git add -A && git commit -m x && git push", "push")
    assert_blocked(repo, "git status; git push", "push")
    assert_blocked(repo, "git log | cat\ngit push", "push")
    assert_blocked(repo, "false || git push", "push")
    assert_blocked(repo, "(git push)", "push")
    assert_blocked(repo, "echo $(git push)", "push")
    assert_blocked(repo, "sleep 1 & git push", "push")
    assert_blocked(repo, "sudo git push", "push")
    assert_blocked(repo, "bash -c 'git add . && git push'", "push")
    assert_blocked(repo, 'pwsh -NoProfile -Command "git push"', "push")
    assert_blocked(repo, "cmd /c git push", "push")
    # chặn nhầm có chủ ý (mục 5.1): tách thô không hiểu dấu nháy
    assert_blocked(repo, 'git commit -m "a && git push"', "push")


def test_guard_branch_merge_allowed_with_plus_branch(tmp_path):
    feature = make_repo(tmp_path, branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    assert_allowed(feature, "git merge spr-12-tk3")
    default = make_repo(tmp_path / "d", branch="spr-12", marker=good_marker())
    assert_blocked(default, "git merge spr-12-tk3", "branch_merge_local")
    # khoá exclusions vắng hẳn → mặc định đủ danh sách (gồm branch_merge_local)
    marker = good_marker()
    del marker["exclusions"]
    nokey = make_repo(tmp_path / "n", branch="spr-12", marker=marker)
    assert_blocked(nokey, "git merge x", "branch_merge_local")
    # exclusions không phải danh sách → coi như mặc định
    wrong = make_repo(tmp_path / "w", branch="spr-12", marker=dict(good_marker(), exclusions="push"))
    assert_blocked(wrong, "git merge x", "branch_merge_local")


def test_guard_exclusions_missing_required_filled_in(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker(["version"]))  # thiếu push, tag, ...
    assert_blocked(repo, "git push", "push")
    assert_blocked(repo, "git tag v1", "tag")
    assert_blocked(repo, "rm -rf x", "irreversible_delete")
    # mục lạ bị bỏ qua, không làm hỏng
    odd = make_repo(tmp_path / "o", branch="spr-12", marker=good_marker(WITHOUT_BRANCH + ["bogus", 3]))
    assert_blocked(odd, "git push", "push")
    assert_allowed(odd, "git merge x")


@pytest.mark.parametrize("text", ["{not json", "", "[]", "null", '"x"', "\xef\xbf\xbd"])
def test_guard_bad_marker_fails_closed(tmp_path, text):
    repo = make_repo(tmp_path, branch="spr-12", marker=text)
    rc, _, err = run("claude", claude("git push", repo))
    assert rc == 2 and "file dấu hỏng" in err and "'push'" in err
    rc, _, err = run("claude", claude("git merge x", repo))  # đóng an toàn: cả branch_merge_local
    assert rc == 2 and "'branch_merge_local'" in err
    assert_allowed(repo, "git status")  # lệnh không khớp mẫu vẫn qua


def test_guard_bad_marker_binary_bytes(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    (repo / ".tmp" / "autopilot.json").write_bytes(b"\xff\xfe\x00bad")
    rc, _, err = run("claude", claude("git push", repo))
    assert rc == 2 and "file dấu hỏng" in err


def test_guard_codex_and_antigravity_event_shapes(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    # Codex: tool shell, command dạng chuỗi hoặc danh sách ["bash","-lc","<script>"], cwd ở payload hoặc workdir
    for tool in ("shell", "Bash", "exec_command"):
        rc, out, err = run("codex", {"tool_name": tool, "tool_input": {"command": "git push"}, "cwd": str(repo)})
        assert rc == 2 and out == "" and "'push'" in err
    rc, _, err = run("codex", {"tool_name": "shell", "tool_input": {"command": ["bash", "-lc", "git add . && git push"], "workdir": str(repo)}})
    assert rc == 2 and "'push'" in err
    rc, _, err = run("codex", {"tool_name": "shell", "tool_input": {"command": ["git", "push"]}, "cwd": str(repo)})
    assert rc == 2 and "'push'" in err
    rc, _, err = run("codex", {"tool_name": "shell", "tool_input": {"cmd": "git push"}, "cwd": str(repo)})
    assert rc == 2
    assert run("codex", {"tool_name": "shell", "tool_input": {"command": ["git", "status"]}, "cwd": str(repo)}) == (0, "", "")
    # Codex apply_patch có khoá command nhưng là patch, không phải shell
    patch = "*** Begin Patch\n*** Update File: a.md\n+git push\n*** End Patch"
    assert run("codex", {"tool_name": "apply_patch", "tool_input": {"command": patch}, "cwd": str(repo)}) == (0, "", "")
    # Antigravity: toolCall.args.CommandLine, in JSON quyết định chặn ở stdout, thoát 0; cho qua in {}
    payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": "git push", "Cwd": str(repo)}}, "stepIdx": 1}
    rc, out, err = run("antigravity", payload)
    assert rc == 0 and err == ""
    decision = json.loads(out)
    assert decision["decision"] == "deny" and "'push'" in decision["reason"]
    ok = {"toolCall": {"name": "run_command", "args": {"CommandLine": "git status", "Cwd": str(repo)}}, "stepIdx": 1}
    assert run("antigravity", ok) == (0, "{}\n", "")
    write = {"toolCall": {"name": "write_to_file", "args": {"TargetFile": str(repo / "a.md")}}}
    assert run("antigravity", write) == (0, "{}\n", "")
    # PowerShell của Claude trên Windows
    rc, _, err = run("claude", claude("git push", repo, tool="PowerShell"))
    assert rc == 2
    # công cụ không phải shell: cho qua dù chứa chữ git push
    assert run("claude", {"tool_name": "Write", "tool_input": {"file_path": "x", "content": "git push", "command": "git push"}, "cwd": str(repo)}) == (0, "", "")
    assert run("claude", {"tool_name": "mcp__x__y", "tool_input": {"command": "git push"}, "cwd": str(repo)}) == (0, "", "")
    # không có tên công cụ nhưng có lệnh: coi là shell (đóng)
    assert run("claude", {"tool_input": {"command": "git push"}, "cwd": str(repo)})[0] == 2
    # shell mà không có lệnh
    assert run("claude", {"tool_name": "Bash", "tool_input": {}, "cwd": str(repo)}) == (0, "", "")


# --- tìm file dấu và nhánh ----------------------------------------------------------------------------------------

def test_guard_finds_marker_walking_up(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    sub = repo / "src" / "deep"
    sub.mkdir(parents=True)
    assert_blocked(sub, "git push", "push")


def test_guard_stops_at_first_git(tmp_path):
    outer = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    inner = outer / "vendor"
    (inner / ".git").mkdir(parents=True)  # repo lồng: file dấu ở ngoài không áp
    assert_allowed(inner, "git push")


def test_guard_worktree_gitdir_file(tmp_path):
    repo = make_repo(tmp_path, branch="main", marker=good_marker(WITHOUT_BRANCH))
    gitdir = repo / ".git" / "worktrees" / "wt"
    gitdir.mkdir(parents=True)
    (gitdir / "HEAD").write_text("ref: refs/heads/spr-12\n", encoding="utf-8")
    wt = tmp_path / "wt"
    (wt / ".tmp").mkdir(parents=True)
    (wt / ".git").write_text("gitdir: {}\n".format(gitdir), encoding="utf-8")
    (wt / ".tmp" / "autopilot.json").write_text(json.dumps(good_marker(WITHOUT_BRANCH)), encoding="utf-8")
    assert_allowed(wt, "git merge x")  # nhánh sprint trong worktree, không phải main
    assert_allowed(wt, "git pull")
    (gitdir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    assert_blocked(wt, "git merge x", "main_merge")
    # worktree không thấy file dấu của repo chính
    other = tmp_path / "wt2"
    other.mkdir()
    (other / ".git").write_text("gitdir: {}\n".format(gitdir), encoding="utf-8")
    assert_allowed(other, "git push")
    # gitdir tương đối
    rel = tmp_path / "wt3"
    (rel / ".tmp").mkdir(parents=True)
    (rel / ".git").write_text("gitdir: ../repo/.git/worktrees/wt\n", encoding="utf-8")
    (rel / ".tmp" / "autopilot.json").write_text(json.dumps(good_marker(WITHOUT_BRANCH)), encoding="utf-8")
    assert_blocked(rel, "git merge x", "main_merge")


@pytest.mark.parametrize("head", ["abc123def\n", "", "ref: refs/heads/\n"])
def test_guard_unknown_branch_treated_as_main(tmp_path, head):
    repo = make_repo(tmp_path, marker=good_marker(WITHOUT_BRANCH))
    (repo / ".git" / "HEAD").write_text(head, encoding="utf-8")
    assert_blocked(repo, "git merge x", "main_merge")


def test_guard_missing_head_treated_as_main(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    (repo / ".git" / "HEAD").unlink()
    assert_blocked(repo, "git merge x", "main_merge")


def test_guard_no_cwd_uses_process_cwd(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    monkeypatch.chdir(repo)
    rc, _, err = run("claude", {"tool_name": "Bash", "tool_input": {"command": "git push"}})
    assert rc == 2 and "'push'" in err
    monkeypatch.chdir(tmp_path)
    assert run("claude", {"tool_name": "Bash", "tool_input": {"command": "git push"}}) == (0, "", "")


def test_guard_marker_without_git_repo(tmp_path):
    (tmp_path / "plain" / ".tmp").mkdir(parents=True)
    (tmp_path / "plain" / ".tmp" / "autopilot.json").write_text(json.dumps(good_marker(WITHOUT_BRANCH)), encoding="utf-8")
    assert_blocked(tmp_path / "plain", "git push", "push")
    assert_blocked(tmp_path / "plain", "git merge x", "main_merge")  # không rõ nhánh: coi như main
    assert_blocked(tmp_path / "plain", "rm -rf .tmp/x", "irreversible_delete")  # không có gốc repo: không có ngoại lệ .tmp


# --- ngoại lệ dọn .tmp/ (N1) --------------------------------------------------------------------------------------

def test_guard_tmp_cleanup_exception(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    (repo / ".tmp" / "scratch").mkdir()
    for cmd in ("rm -rf .tmp/scratch", "rm -fr .tmp/scratch", "rm -r -f .tmp/scratch", "rm --recursive .tmp/scratch",
                "rm -rf ./.tmp/scratch", "rm -rf .tmp/scratch/", "rm -rf .tmp\\scratch", "Remove-Item -Recurse -Force .tmp\\scratch",
                "rm -rf .tmp/a .tmp/b", "rm -rf '.tmp/with space'", "rm -rf .tmp/out*", "rm -rf .tmp/scratch/*", "rm -rf .tmp/ab[c]",
                "rm -rf " + str(repo / ".tmp" / "scratch"), "rmdir /s /q .tmp\\scratch"):
        assert_allowed(repo, cmd)


@pytest.mark.parametrize("cmd", [
    "rm -rf .tmp", "rm -rf .tmp/", "rm -rf .tmp/.", "rm -rf .tmp/*", "rm -rf .tmp/a*", "rm -rf .tmp/autopilot.json",
    "rm -rf .tmp/AUTOPILOT.JSON", "rm -rf .tmp/../src", "rm -rf .tmp/x/../../src", "rm -rf .tmp/scratch ..", "rm -rf .tmp/scratch build",
    "rm -rf src/.tmp/x", "rm -rf /tmp/x", "rm -rf .tmp/$X", "rm -rf .tmp/x,../y", "rm -rf ~/.tmp/x", "rm -rf .tmp/{a,b}",
    "rm -rf .tmp/*/x/../..", "rm -rf .tm*/x", "cd src && rm -rf .tmp/scratch",
    "rm -rf .tmpx/a", "rm -rf", "Remove-Item -Recurse .tmp",
])
def test_guard_tmp_exception_not_applied(tmp_path, cmd):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    (repo / "src").mkdir()
    assert_blocked(repo, cmd, "irreversible_delete")


def test_guard_tmp_exception_from_subdir_uses_repo_root(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    sub = repo / "src"
    sub.mkdir()
    # từ thư mục con, `.tmp/x` là .tmp của thư mục con, không phải của gốc repo → chặn; đường tuyệt đối vào .tmp gốc → qua
    assert_blocked(sub, "rm -rf .tmp/x", "irreversible_delete")
    assert_blocked(sub, "rm -rf ../.tmp/x", "irreversible_delete")  # có ".."
    assert_allowed(sub, "rm -rf " + str(repo / ".tmp" / "x"))


def test_guard_tmp_exception_symlink_escapes(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    outside = tmp_path / "outside"
    outside.mkdir()
    link_dir(outside, repo / ".tmp" / "link")
    assert_blocked(repo, "rm -rf .tmp/link", "irreversible_delete")
    assert_blocked(repo, "rm -rf .tmp/link/inside", "irreversible_delete")
    assert_allowed(repo, "rm -rf .tmp/real")  # tên thường không tồn tại: vẫn nằm trong .tmp


def test_guard_tmp_dir_itself_a_link(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=None)
    outside = tmp_path / "outside"
    outside.mkdir()
    marker_text = json.dumps(good_marker())
    (outside / "autopilot.json").write_text(marker_text, encoding="utf-8")
    (repo / ".tmp").rmdir()
    link_dir(outside, repo / ".tmp")
    assert_blocked(repo, "rm -rf .tmp/x", "irreversible_delete")  # .tmp là link ra ngoài: không có ngoại lệ


def test_guard_tmp_marker_symlinked_target(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    try:
        os.symlink(repo / ".tmp" / "autopilot.json", repo / ".tmp" / "alias")
    except (OSError, NotImplementedError):
        pytest.skip("không tạo được symlink trên máy này")
    assert_blocked(repo, "rm -rf .tmp/alias", "irreversible_delete")  # trỏ tới file dấu


# --- lỗi đầu vào ------------------------------------------------------------------------------------------------

def test_guard_bad_stdin_without_marker_passes_and_with_marker_blocks(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert run("claude", "{broken") == (0, "", "")
    assert run("antigravity", "[]") == (0, "{}\n", "")
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    monkeypatch.chdir(repo)
    rc, _, err = run("claude", "{broken")
    assert rc == 2 and "autopilot" in err
    rc, out, _ = run("antigravity", "null")
    assert rc == 0 and json.loads(out)["decision"] == "deny"


def test_guard_unexpected_exception_closed_with_marker(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    monkeypatch.chdir(repo)  # ngoại lệ lạ → dò file dấu từ thư mục của tiến trình hook
    monkeypatch.setattr(autopilot_guard, "_analyze", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    rc, _, err = run("claude", claude("git status", repo))
    assert rc == 2 and "RuntimeError" in err
    monkeypatch.setenv("AUTOPILOT_GUARD_DEBUG", "1")
    rc, _, err = run("claude", claude("git status", repo))
    assert rc == 2 and "Traceback" in err
    # không có file dấu: lỗi lạ không chặn việc của người dùng
    plain = tmp_path / "plain"
    plain.mkdir()
    monkeypatch.chdir(plain)
    assert run("claude", claude("git status", plain))[0] == 0


def _nest(cmd, layers):
    for _ in range(layers):
        cmd = 'bash -c "{}"'.format(cmd.replace('"', "'"))
    return cmd


def test_guard_deep_command_nesting_fails_closed(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    rc, _, err = run("claude", claude(_nest("git push", 3), repo))  # trong giới hạn: mở hết lớp, thấy push
    assert rc == 2 and "'push'" in err
    rc, _, err = run("claude", claude(_nest("git push", 4), repo))  # quá giới hạn: không phân tích được → chặn
    assert rc == 2 and "lồng" in err and "hook gặp lỗi" not in err
    rc, _, err = run("claude", claude(_nest("git status", 6), repo))
    assert rc == 2 and "lồng" in err
    plain = tmp_path / "plain"
    plain.mkdir()
    assert run("claude", claude(_nest("git push", 6), plain)) == (0, "", "")  # không có file dấu → qua


def test_guard_cli_subprocess(tmp_path):
    import subprocess
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    payload = json.dumps(claude("git push", repo))
    proc = subprocess.run([sys.executable, str(SCRIPTS / "autopilot_guard.py"), "--format", "claude"], input=payload,
                          capture_output=True, text=True, encoding="utf-8", cwd=str(repo))
    assert proc.returncode == 2 and "'push'" in proc.stderr and proc.stdout == ""
    ok = subprocess.run([sys.executable, str(SCRIPTS / "autopilot_guard.py"), "--format", "antigravity"], input="{broken",
                        capture_output=True, text=True, encoding="utf-8", cwd=str(tmp_path))
    assert ok.returncode == 0 and ok.stdout.strip() == "{}"


# ===================== vòng sửa 1 (S-RF1…S-RF9, T-RF1…T-RF4) =====================

def codex(cmd, cwd=None, workdir=None):
    payload = {"tool_name": "shell", "tool_input": {"command": cmd}}
    if cwd is not None:
        payload["cwd"] = str(cwd)
    if workdir is not None:
        payload["tool_input"]["workdir"] = str(workdir)
    return payload


def fwd(path):
    return str(path).replace("\\", "/")


def test_guard_workdir_beats_session_cwd(tmp_path):
    """S-RF1 / T-RF3: thư mục của lệnh (workdir) quyết định, không phải cwd của phiên."""
    repo = make_repo(tmp_path / "a", branch="spr-12", marker=good_marker())
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    rc, _, err = run("codex", codex(["bash", "-lc", "git push"], cwd=elsewhere, workdir=repo))
    assert rc == 2 and "'push'" in err
    # cwd phiên trong repo có file dấu, workdir nơi không có: file dấu của phiên vẫn áp (thấy ở đâu cũng bật)
    rc, _, err = run("codex", codex(["bash", "-lc", "git push"], cwd=repo, workdir=elsewhere))
    assert rc == 2
    # nhánh đọc ở workdir: phiên ở worktree sprint, lệnh chạy ở bản checkout main
    mainrepo = make_repo(tmp_path / "m", branch="main", marker=good_marker(WITHOUT_BRANCH))
    sprint = make_repo(tmp_path / "s", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    rc, _, err = run("codex", codex("git merge spr-12", cwd=sprint, workdir=mainrepo))
    assert rc == 2 and "'main_merge'" in err
    assert run("codex", codex("git merge x", cwd=mainrepo, workdir=sprint)) == (0, "", "")
    # workdir tương đối ghép với cwd phiên; Antigravity: Cwd trong args thắng cwd phiên
    (repo / "sub").mkdir()
    rc, _, err = run("codex", {"tool_name": "shell", "cwd": str(repo), "tool_input": {"command": "git push", "workdir": "sub"}})
    assert rc == 2
    ag = {"toolCall": {"name": "run_command", "args": {"CommandLine": "git push", "Cwd": str(repo)}}, "cwd": str(elsewhere)}
    assert json.loads(run("antigravity", ag)[1])["decision"] == "deny"


def test_guard_error_after_event_dir_probes_event_dir(tmp_path, monkeypatch):
    """T-RF1 / S-RF4: lỗi sau khi có thư mục sự kiện → dò file dấu ở thư mục sự kiện, không phải thư mục tiến trình."""
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    away = tmp_path / "away"
    away.mkdir()
    monkeypatch.chdir(away)

    def boom():
        raise ImportError("check không nhập được")

    monkeypatch.setattr(autopilot_guard, "known_exclusions", boom)
    rc, _, err = run("claude", claude("git push", repo))
    assert rc == 2 and "ImportError" in err
    rc, out, _ = run("antigravity", {"toolCall": {"name": "run_command", "args": {"CommandLine": "git push", "Cwd": str(repo)}}})
    assert rc == 0 and json.loads(out)["decision"] == "deny"
    assert run("claude", claude("git push", away)) == (0, "", "")  # thư mục sự kiện không file dấu: lỗi không chặn
    monkeypatch.undo()
    monkeypatch.chdir(away)
    monkeypatch.setattr(autopilot_guard, "_analyze", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    rc, _, err = run("claude", claude("git status", repo))
    assert rc == 2 and "RuntimeError" in err


@pytest.mark.parametrize("cmd", [
    "timeout 60 git push", "timeout -s KILL 30 git push", "timeout --signal=KILL 5 git push", "timeout -k 5 60 git push",
    "env -i git push", "env -u HOME git push", "env FOO=bar BAZ=1 git push", "env -i FOO=1 git push", "env -S 'git push'",
    "sudo -u deploy git push", "sudo -E git push", "sudo -u x -g y git push", "sudo --user=x git push",
    "nice -n 10 git push", "nice -10 git push", "command -p git push", "nohup git push", "time git push", "time -p git push",
    "ls | xargs -0 git push", "xargs -n 1 -I {} git push", "echo x | xargs -r git push",
    "stdbuf -oL git push", "exec git push", "/usr/bin/env git push", "sudo env FOO=1 timeout 5 git push",
])
def test_guard_prefix_wrappers_with_their_arguments(tmp_path, cmd):
    """S-RF2 / T-RF6: tiền tố kèm cờ và đối số vẫn lộ lệnh thật."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, cmd, "push")


def test_guard_prefix_wrappers_other_items(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, "timeout 60 rm -rf build", "irreversible_delete")
    assert_blocked(repo, "ls | xargs -0 rm -rf", "irreversible_delete")
    assert_blocked(repo, "sudo -u x gh pr merge 3", "main_merge")
    assert_allowed(repo, "timeout 60 git status")
    assert_allowed(repo, "env -i FOO=1 ls")
    assert_allowed(repo, "sudo -u x ls")


@pytest.mark.parametrize("cmd", [
    "cd {main} && git merge spr-12", "cd {main}; git pull", "pushd {main} && git merge x", "Set-Location {main}; git merge x",
    "git -C {main} merge spr-12", "git -C {main} pull", "git -C {main} -c user.name=x merge y",
    "cd {rel} && git merge x", "cd $UNKNOWN && git merge x", "git -C $UNKNOWN merge x", "cd && git merge x", "cd - && git merge x",
    "GIT_DIR={main}/.git git merge x", "git --git-dir={main}/.git merge x", "git --work-tree {main} merge x",
])
def test_guard_merge_reads_branch_of_target_dir(tmp_path, cmd):
    """T-RF2: lệnh chạy ở worktree sprint nhưng cd/-C sang bản checkout main, hay không xác định được thư mục → coi là main."""
    sprint = make_repo(tmp_path / "s", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    mainrepo = make_repo(tmp_path / "m", branch="main")
    rel = fwd(os.path.relpath(mainrepo, sprint))
    assert_blocked(sprint, cmd.format(main=fwd(mainrepo), rel=rel), "main_merge")


def test_guard_merge_in_non_main_dir_allowed(tmp_path):
    sprint = make_repo(tmp_path / "s", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    other = make_repo(tmp_path / "o", branch="spr-13")
    rel = fwd(os.path.relpath(other, sprint))
    for cmd in ("git -C {o} merge x", "git -C {o} pull"):
        assert_allowed(sprint, cmd.format(o=fwd(other), r=rel))
    for cmd in ("cd {o} && git merge x", "cd {r} && git pull"):  # đổi thư mục rồi gộp: chặn nhầm có chủ đích
        assert_blocked(sprint, cmd.format(o=fwd(other), r=rel), "main_merge")
    mainrepo = make_repo(tmp_path / "m", branch="main", marker=good_marker(WITHOUT_BRANCH))
    assert_allowed(mainrepo, "git -C {} merge x".format(fwd(other)))  # từ thư mục main, -C sang nhánh sprint → đọc nhánh sprint


@pytest.mark.parametrize("cmd", ["gh -R o/r pr merge 12", "gh --repo o/r pr merge 12", "gh pr -R o/r merge 12",
                                 "gh pr --repo=o/r merge 12", "gh pr merge 12 -R o/r", "gh -Ro/r pr merge 1", "gh pr merge"])
def test_guard_gh_repo_flag_any_position(tmp_path, cmd):
    """S-RF5 / T-RF5."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, cmd, "main_merge")


def test_guard_gh_repo_flag_not_merge(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("gh -R o/r pr view 12", "gh pr -R o/r list", "gh -R merge pr view"):
        assert_allowed(repo, cmd)


def test_guard_more_patterns(tmp_path):
    """S-RF6: git subtree push, gh release create, find -exec/-delete."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, "git subtree push --prefix=x origin main", "push")
    assert_blocked(repo, "gh release create v1.0 --notes x", "tag")
    assert_blocked(repo, "gh -R o/r release create v1", "tag")
    assert_blocked(repo, "find . -name '*.o' -delete", "irreversible_delete")
    assert_blocked(repo, "find build -exec rm -rf {} +", "irreversible_delete")
    assert_blocked(repo, "find build -type d -execdir rm -r {} +", "irreversible_delete")
    assert_allowed(repo, "git subtree split --prefix=x")
    assert_allowed(repo, "gh release list")
    assert_allowed(repo, "gh release view v1")
    assert_allowed(repo, "find . -name '*.py'")
    assert_allowed(repo, "find . -name x -exec grep foo {} +")


def test_guard_marker_name_case_insensitive(tmp_path):
    """S-RF7: tên file dấu so không phân biệt hoa thường trên mọi hệ."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, "rm -rf .tmp/Autopilot.JSON", "irreversible_delete")
    assert_blocked(repo, "rm -rf .tmp/AUTOPILOT*", "irreversible_delete")
    assert_blocked(repo, "rm -rf .tmp/autopilot.js?n", "irreversible_delete")


def test_guard_tmp_glob_expands_and_checks_each_match(tmp_path):
    """S-RF3 / T-RF7: đích glob mở rộng theo thư mục lệnh; mỗi mục khớp phải nằm thật trong .tmp/."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    outside = tmp_path / "outside"
    outside.mkdir()
    (repo / ".tmp" / "keep1").mkdir()
    (repo / ".tmp" / "keep2").mkdir()
    assert_allowed(repo, "rm -rf .tmp/keep*")
    assert_allowed(repo, "rm -rf .tmp/nomatch*")  # không khớp gì: không xoá gì
    link_dir(outside, repo / ".tmp" / "lnk")
    assert_blocked(repo, "rm -rf .tmp/ln*", "irreversible_delete")
    assert_blocked(repo, "rm -rf .tmp/l*", "irreversible_delete")
    assert_blocked(repo, "rm -rf .tmp/ln*/", "irreversible_delete")
    assert_blocked(repo, "rm -rf .tmp/lnk/", "irreversible_delete")
    assert_blocked(repo, "Remove-Item -Recurse -Force .tmp\\ln*", "irreversible_delete")
    assert_blocked(repo, "rm -rf .tmp/[kl]*", "irreversible_delete")  # khớp keep* lẫn lnk
    assert_allowed(repo, "rm -rf .tmp/keep[12]")


def test_guard_tmp_glob_unreadable_parent_blocks(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    real = os.listdir

    def failing(path="."):
        if str(path).endswith(".tmp"):
            raise OSError("denied")
        return real(path)

    monkeypatch.setattr(os, "listdir", failing)
    assert_blocked(repo, "rm -rf .tmp/keep*", "irreversible_delete")


# ===================== vòng sửa 2 (S-N-RF1, S-N-RF2, T-N-RF1, S-RF6 phần còn) =====================

@pytest.mark.parametrize("cmd", [
    "(cd {feat} && true); git merge x", "bash -c 'cd {feat}'; git merge x", "cd {feat} | true; git merge x",
    "(cd {feat}); git pull", "cd {feat} & git merge x", "(cd {main}); cd {feat}; git merge x",
])
def test_guard_cd_in_subshell_does_not_hide_main(tmp_path, cmd):
    """S-N-RF1: cd trong subshell/pipeline/bash -c không đổi thư mục của lệnh sau; thư mục ban đầu là main thì vẫn chặn."""
    mainrepo = make_repo(tmp_path / "m", branch="main", marker=good_marker(WITHOUT_BRANCH))
    feat = make_repo(tmp_path / "f", branch="spr-13")
    assert_blocked(mainrepo, cmd.format(feat=fwd(feat), main=fwd(mainrepo)), "main_merge")


def test_guard_cd_visited_dirs_all_count(tmp_path):
    sprint = make_repo(tmp_path / "s", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    mainrepo = make_repo(tmp_path / "m", branch="main")
    feat = make_repo(tmp_path / "f", branch="spr-13")
    # đã từng vào thư mục main (kể cả trong subshell) rồi mới sang nhánh khác: đóng an toàn
    assert_blocked(sprint, "cd {m}; (cd {f}); git merge x".format(m=fwd(mainrepo), f=fwd(feat)), "main_merge")
    # quy tắc vòng 3: có đổi thư mục thì coi là main, kể cả khi chỉ đi qua thư mục không phải main
    assert_blocked(sprint, "cd {f} && git merge x".format(f=fwd(feat)), "main_merge")
    # git -C vẫn đọc nhánh của chính thư mục đó, bất kể cd trước
    main_marked = make_repo(tmp_path / "mm", branch="main", marker=good_marker(WITHOUT_BRANCH))
    assert_allowed(main_marked, "git -C {f} merge x".format(f=fwd(feat)))
    assert_blocked(sprint, "git -C {m} merge x".format(m=fwd(mainrepo)), "main_merge")


@pytest.mark.parametrize("cmd", [
    "Push-Location {main}; git merge x", "push-location {main} && git pull", "Pop-Location; git merge x", "popd; git merge x",
    "env -C {main} git merge spr-12", "env --chdir={main} git merge spr-12", "env --chdir {main} git pull",
    "sudo -D {main} git merge x", "sudo --chdir={main} git merge x", "env -i -C {main} git merge x",
])
def test_guard_other_directory_changers(tmp_path, cmd):
    """S-N-RF2 / T-N-RF1: Push/Pop-Location, env -C/--chdir, sudo -D/--chdir đổi thư mục như cd."""
    sprint = make_repo(tmp_path / "s", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    mainrepo = make_repo(tmp_path / "m", branch="main")
    assert_blocked(sprint, cmd.format(main=fwd(mainrepo)), "main_merge")


def test_guard_directory_changers_to_non_main_still_blocked(tmp_path):
    sprint = make_repo(tmp_path / "s", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    feat = make_repo(tmp_path / "f", branch="spr-13")
    for cmd in ("Push-Location {f}; git merge x", "env -C {f} git merge x", "sudo -D {f} git merge x", "env --chdir={f} git pull"):
        assert_blocked(sprint, cmd.format(f=fwd(feat)), "main_merge")


def test_guard_pull_is_a_merge_when_branch_merge_local_listed(tmp_path):
    """S-RF6 phần còn: `git pull` gộp cục bộ → khi thiếu `+nhánh` chặn ở mọi nhánh."""
    default = make_repo(tmp_path / "d", branch="spr-12", marker=good_marker())
    assert_blocked(default, "git pull", "branch_merge_local")
    assert_blocked(default, "git pull --ff-only", "branch_merge_local")
    assert_blocked(default, "git pull origin spr-12", "branch_merge_local")
    assert_blocked(default, "git -C . pull", "branch_merge_local")
    onmain = make_repo(tmp_path / "m", branch="main", marker=good_marker())
    assert_blocked(onmain, "git pull", "main_merge")
    plus = make_repo(tmp_path / "p", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    assert_allowed(plus, "git pull")  # +nhánh: gộp cục bộ ngoài nhánh chính được phép
    assert_allowed(default, "git fetch")


# ===================== vòng sửa 3: mọi thao tác đổi thư mục trước merge/pull (không -C) = main =====================

@pytest.mark.parametrize("cmd", [
    "(cd sub); cd {rel}; git merge x",  # N2-RF1: cd tương đối tính từ cd trong subshell
    "cd sub && cd {rel} && git merge x",
    "env -C{rel} git merge x",  # N2-RF2: viết dính
    "sudo -D{rel} git merge x",
    "env --chdir{rel} git merge x", "env --ch={rel} git merge x", "sudo --chdir={rel} git pull",
    "cd sub; git merge x", "Set-Location sub; git merge x", "sl sub; git pull", "chdir sub && git merge x", "pushd sub; git merge x",
    "bash -c 'cd sub'; git merge x", "popd; git pull",
])
def test_guard_any_dir_change_before_merge_counts_as_main(tmp_path, cmd):
    sprint = make_repo(tmp_path / "s", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    (sprint / "sub").mkdir()
    mainrepo = make_repo(tmp_path / "m", branch="main")
    assert_blocked(sprint, cmd.format(rel=fwd(os.path.relpath(mainrepo, sprint))), "main_merge")


def test_guard_merge_without_dir_change_and_git_c_unchanged(tmp_path):
    sprint = make_repo(tmp_path / "s", branch="spr-12", marker=good_marker(WITHOUT_BRANCH))
    feat = make_repo(tmp_path / "f", branch="spr-13")
    for cmd in ("git merge spr-12-tk3", "git pull", "git add -A && git commit -m x && git merge spr-12-tk3",
                "git -C {f} merge x", "cd {f} && git -C {f} merge x", "git merge x && cd sub"):
        assert_allowed(sprint, cmd.format(f=fwd(feat)))
    assert_blocked(sprint, "git -C $UNKNOWN merge x", "main_merge")
    assert_blocked(sprint, "cd sub && git -C rel merge x", "main_merge")  # -C tương đối sau cd: gốc không biết


# ===================== TK8 vòng 1: bảo vệ file dấu, công cụ ghi file, cụm cờ, nối dòng, eval/ống, -C, launcher, hooks.json =====================

MARKER_REASON = "file dấu là rào — chỉ người dùng hoặc lệnh dừng mới xoá"


def assert_marker_blocked(repo, cmd):
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2 and MARKER_REASON in err, (cmd, rc, err)


@pytest.mark.parametrize("cmd", [
    "rm .tmp/autopilot.json", "rm -f .tmp/autopilot.json", "rm -f .tmp/*", "rm .tmp/auto*", "rm .tmp/AUTOPILOT.JSON",
    "rm -f ./.tmp/autopilot.json", "rm -f .tmp\\autopilot.json", "mv .tmp/autopilot.json .tmp/x", "mv x .tmp/autopilot.json",
    "mv .tmp x", "cp x .tmp/autopilot.json", "cp /dev/null .tmp/autopilot.json", "Remove-Item .tmp\\autopilot.json",
    "Remove-Item .tmp/*", "Move-Item .tmp/autopilot.json x", "Rename-Item .tmp/autopilot.json y", "Set-Content .tmp/autopilot.json '{}'",
    "Out-File -FilePath .tmp/autopilot.json", "echo '{}' > .tmp/autopilot.json", "echo x >> .tmp/autopilot.json",
    "echo x >.tmp/autopilot.json", "echo x 2>.tmp/autopilot.json", "> .tmp/autopilot.json", ": > .tmp/autopilot.json",
    "echo x | tee .tmp/autopilot.json", "truncate -s 0 .tmp/autopilot.json", "sed -i s/a/b/ .tmp/autopilot.json",
    "sed -i.bak s/a/b/ .tmp/autopilot.json", "python -c pass .tmp/autopilot.json", "git rm .tmp/autopilot.json", "git checkout -- .tmp",
    "unlink .tmp/autopilot.json", "cd .tmp && rm autopilot.json", "cd .tmp; rm *", "Set-Location .tmp; Remove-Item autopilot.json",
])
def test_guard_marker_is_protected_from_shell_writes(tmp_path, cmd):
    """RF2 (TK8 tr-a) / RF3 (tr-b): file dấu không bị xoá, đổi tên, ghi đè bằng lệnh shell không chỉ-đọc."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_marker_blocked(repo, cmd)


def test_guard_marker_protection_read_only_and_other_files_allowed(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("cat .tmp/autopilot.json", "type .tmp\\autopilot.json", "Get-Content .tmp/autopilot.json", "ls .tmp", "ls .tmp/*",
                "ls -la .tmp/autopilot.json", "test -f .tmp/autopilot.json", "[ -f .tmp/autopilot.json ]", "grep level .tmp/autopilot.json",
                "git status .tmp", "git diff .tmp/autopilot.json", "sed -n 1p .tmp/autopilot.json", "head -n 1 .tmp/autopilot.json",
                "echo hi", "rm -f .tmp/other.txt", "rm .tmp/scratch.txt", "cp a b", "mv a b", "echo x > .tmp/out.txt", "echo x > out.txt",
                "echo x > src/autopilot.json.bak", "python -c pass .tmp/notes.json"):
        assert_allowed(repo, cmd)


def test_guard_marker_protection_resolves_from_command_dir_and_other_markers_allowed(tmp_path):
    repo = make_repo(tmp_path / "a", branch="spr-12", marker=good_marker())
    (repo / "src").mkdir()
    assert_marker_blocked(repo / "src", "rm -f ../.tmp/autopilot.json")
    assert_marker_blocked(repo / "src", "rm -f " + fwd(repo / ".tmp" / "autopilot.json"))
    assert_allowed(repo / "src", "rm -f .tmp/autopilot.json")  # `.tmp` của thư mục con, không phải file dấu đang bật
    # điều phối chép file dấu sang worktree khác bằng đường tuyệt đối, không cd: không đụng file dấu đang bật... (nguồn là file dấu đang bật nên vẫn là đọc-ghi)
    other = tmp_path / "wt"
    (other / ".tmp").mkdir(parents=True)
    assert_allowed(repo, "echo '{}' > " + fwd(other / ".tmp" / "autopilot.json"))
    assert_allowed(repo, "cp x " + fwd(other / ".tmp" / "autopilot.json"))


def test_guard_marker_protection_symlink_alias(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    try:
        os.symlink(repo / ".tmp" / "autopilot.json", repo / ".tmp" / "alias")
    except (OSError, NotImplementedError):
        pytest.skip("không tạo được symlink file trên máy này (cần đặc quyền)")
    assert_marker_blocked(repo, "rm .tmp/alias")


@pytest.mark.parametrize("payload_of", ["claude_write", "claude_edit", "claude_multiedit", "claude_notebook", "codex_patch",
                                        "codex_patch_move", "antigravity_write", "antigravity_replace", "antigravity_multi"])
def test_guard_marker_blocks_write_tools(tmp_path, payload_of):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    target = str(repo / ".tmp" / "autopilot.json")
    payloads = {
        "claude_write": ("claude", {"tool_name": "Write", "tool_input": {"file_path": target, "content": "{}"}, "cwd": str(repo)}),
        "claude_edit": ("claude", {"tool_name": "Edit", "tool_input": {"file_path": ".tmp/AUTOPILOT.json", "old_string": "a", "new_string": "b"},
                                   "cwd": str(repo)}),
        "claude_multiedit": ("claude", {"tool_name": "MultiEdit", "tool_input": {"file_path": target, "edits": []}, "cwd": str(repo)}),
        "claude_notebook": ("claude", {"tool_name": "NotebookEdit", "tool_input": {"notebook_path": target}, "cwd": str(repo)}),
        "codex_patch": ("codex", {"tool_name": "apply_patch", "cwd": str(repo),
                                  "tool_input": {"command": "*** Begin Patch\n*** Update File: .tmp/autopilot.json\n@@\n-a\n+b\n*** End Patch"}}),
        "codex_patch_move": ("codex", {"tool_name": "apply_patch", "cwd": str(repo),
                                       "tool_input": {"command": "*** Begin Patch\n*** Update File: x.md\n*** Move to: .tmp/autopilot.json\n*** End Patch"}}),
        "antigravity_write": ("antigravity", {"toolCall": {"name": "write_to_file", "args": {"TargetFile": target}}, "cwd": str(repo)}),
        "antigravity_replace": ("antigravity", {"toolCall": {"name": "replace_file_content", "args": {"TargetFile": target}}, "cwd": str(repo)}),
        "antigravity_multi": ("antigravity", {"toolCall": {"name": "multi_replace_file_content", "args": {"TargetFile": target, "Cwd": str(repo)}}}),
    }
    fmt, payload = payloads[payload_of]
    rc, out, err = run(fmt, payload)
    if fmt == "antigravity":
        decision = json.loads(out)
        assert rc == 0 and decision["decision"] == "deny" and MARKER_REASON in decision["reason"]
    else:
        assert rc == 2 and MARKER_REASON in err


def test_guard_write_tools_other_files_and_no_marker_allowed(tmp_path):
    repo = make_repo(tmp_path / "a", branch="spr-12", marker=good_marker())
    assert run("claude", {"tool_name": "Write", "tool_input": {"file_path": str(repo / "src.md")}, "cwd": str(repo)}) == (0, "", "")
    assert run("claude", {"tool_name": "Write", "tool_input": {"file_path": str(repo / ".tmp" / "notes.md")}, "cwd": str(repo)}) == (0, "", "")
    other = make_repo(tmp_path / "b", branch="spr-12")  # không file dấu: intake ghi file dấu lần đầu phải qua
    assert run("claude", {"tool_name": "Write", "tool_input": {"file_path": str(other / ".tmp" / "autopilot.json")}, "cwd": str(other)}) == (0, "", "")
    # worktree khác (không phải file dấu đang bật): điều phối chép file dấu bằng công cụ ghi được qua
    wt = tmp_path / "wt"
    (wt / ".tmp").mkdir(parents=True)
    assert run("claude", {"tool_name": "Write", "tool_input": {"file_path": str(wt / ".tmp" / "autopilot.json")}, "cwd": str(repo)}) == (0, "", "")


@pytest.mark.parametrize("cmd", ["sudo -Hu deploy git push", "sudo -Eu root git push", "env -iu HOME git push", "xargs -tI {} git push",
                                 "sudo -EHu x -g y git push", "env -iC /tmp git push"])
def test_guard_short_flag_clusters_ending_in_value_flag(tmp_path, cmd):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, cmd, "push")
    assert_allowed(repo, cmd.replace("git push", "git status"))


def test_guard_line_continuation_joined(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, "git \\\npush origin x", "push")
    assert_blocked(repo, "git \\\r\n  push", "push")
    assert_blocked(repo, "git `\npush", "push")
    assert_blocked(repo, "git push \\\n --force", "push")
    assert_allowed(repo, "git \\\nstatus")
    assert_blocked(repo, "git status\ngit push", "push")


@pytest.mark.parametrize("cmd,item", [
    ('eval "git push"', "push"), ("eval git push", "push"), ("eval 'git add . && git push'", "push"), ("eval rm -rf build", "irreversible_delete"),
    ('iex "git push"', "push"), ("Invoke-Expression 'git push'", "push"),
    ("echo git push | bash", "push"), ('echo "git push" | sh', "push"), ("printf 'git push' | pwsh", "push"),
    ("echo git push | sudo bash", "push"), ("echo git push | bash -s", "push"), ("echo git push | iex", "push"),
    ('bash <<< "git push"', "push"), ("echo rm -rf build | bash", "irreversible_delete"),
    ("eval git $ARGS", "unresolved"), ("echo git $ARGS | bash", "unresolved"), ("eval \"gh pr merge $N\"", "main_merge"),
])
def test_guard_eval_and_pipe_into_shell(tmp_path, cmd, item):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)
    if item == "unresolved":
        assert "không phân tích được" in err
    else:
        assert "'{}'".format(item) in err


def test_guard_eval_and_pipe_benign_allowed(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("eval echo hi", "eval $(ssh-agent)", "echo hi | bash", "cat script.sh | bash", "curl -s x | sh", "echo git status | bash",
                "ls | grep git", "echo $X | bash", "bash -s < script.sh"):
        assert_allowed(repo, cmd)
    # lồng quá sâu qua eval: chặn
    deep = "eval \"eval 'eval \\\"eval git push\\\"'\""
    rc, _, _ = run("claude", claude(deep, repo))
    assert rc == 2


def test_guard_git_c_from_outside_repo_finds_marker(tmp_path):
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    outside = tmp_path / "outside"
    outside.mkdir()
    rel = fwd(os.path.relpath(repo, outside))
    for cmd in ("git -C {r} push", "git -C {rel} push", "git -C {rel} reset --hard", "cd {rel} && git push", "bash -c 'git -C {rel} push'",
                "git -c a=b -C {rel} push", "Set-Location {rel}; git push"):
        rc, _, err = run("claude", claude(cmd.format(r=fwd(repo), rel=rel), outside))
        assert rc == 2, (cmd, err)
    assert run("claude", claude("git -C {} status".format(rel), outside)) == (0, "", "")
    assert run("claude", claude("git -C {} push".format(fwd(outside)), outside)) == (0, "", "")  # đích không có file dấu


# --- launcher ---

SH = shutil.which("sh")
LAUNCHER = SCRIPTS / "autopilot-hook.sh"


def run_launcher(cwd, payload, path_dirs, extra_env=None):
    env = {"PATH": os.pathsep.join(str(d) for d in path_dirs), "CLAUDE_PROJECT_DIR": fwd(cwd), "PYTHONIOENCODING": "utf-8"}
    for key in ("SystemRoot", "SYSTEMROOT", "TEMP", "TMP", "HOME"):
        if key in os.environ:
            env[key] = os.environ[key]
    env.update(extra_env or {})
    import subprocess
    return subprocess.run([SH, fwd(LAUNCHER), "--format", "claude"], input=json.dumps(payload), capture_output=True, text=True,
                          encoding="utf-8", cwd=str(cwd), env=env)


@pytest.fixture
def bare_sh_ok(tmp_path):
    if SH is None:
        pytest.skip("không có `sh` trên máy này")
    empty = tmp_path / "emptybin"
    empty.mkdir()
    probe = run_launcher(tmp_path, {}, [empty])
    if probe.returncode != 0:
        pytest.skip("sh không chạy được với PATH rỗng trên máy này: " + probe.stderr[:80])
    return empty


def test_launcher_without_python_blocks_when_marker(tmp_path, bare_sh_ok):
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    sub = repo / "src"
    sub.mkdir()
    for cwd in (repo, sub):
        done = run_launcher(cwd, claude("git push", cwd), [bare_sh_ok])
        assert done.returncode == 2 and "không chạy được Python" in done.stderr, done.stderr
    # tên file dấu viết hoa
    (repo / ".tmp" / "autopilot.json").rename(repo / ".tmp" / "AutoPilot.JSON")
    assert run_launcher(repo, claude("ls", repo), [bare_sh_ok]).returncode == 2


def test_launcher_without_python_passes_when_no_marker(tmp_path, bare_sh_ok):
    repo = make_repo(tmp_path / "r", branch="spr-12")
    assert run_launcher(repo, claude("git push", repo), [bare_sh_ok]).returncode == 0
    nested = repo / "vendor"
    (nested / ".git").mkdir(parents=True)  # marker của repo ngoài không áp cho repo lồng
    (repo / ".tmp" / "autopilot.json").write_text("{}", encoding="utf-8")
    assert run_launcher(nested, claude("git push", nested), [bare_sh_ok], {"CLAUDE_PROJECT_DIR": fwd(nested)}).returncode == 0


def test_launcher_with_python_delegates_to_guard(tmp_path, bare_sh_ok):
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    path = [bare_sh_ok, Path(sys.executable).parent]
    blocked_run = run_launcher(repo, claude("git push", repo), path)
    if blocked_run.returncode == 2 and "không chạy được Python" in blocked_run.stderr:
        pytest.skip("launcher không thấy Python dùng được trong PATH thử")
    assert blocked_run.returncode == 2 and "'push'" in blocked_run.stderr
    assert run_launcher(repo, claude("git status", repo), path).returncode == 0
    plain = make_repo(tmp_path / "p", branch="spr-12")
    assert run_launcher(plain, claude("git push", plain), path).returncode == 0


def test_launcher_is_posix_sh_text():
    text = LAUNCHER.read_bytes().decode("utf-8")
    assert text.startswith("#!/bin/sh\n") and "\r" not in text
    assert "python3" in text and "sys.version_info >= (3, 9)" in text and "exit 2" in text


# --- hooks/hooks.json ---

def test_hooks_json_registers_guard():
    config = json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    entries = config["hooks"]["PreToolUse"]
    assert len(entries) == 1
    matcher = entries[0]["matcher"].split("|")
    assert "Bash" in matcher and "PowerShell" in matcher
    hook = entries[0]["hooks"][0]
    assert hook["type"] == "command" and hook["onFailure"] == "block" and "--format claude" in hook["command"]
    assert "scripts/autopilot_guard.py" in hook["command"] or "scripts/autopilot-hook.sh" in hook["command"]
    for name in ("autopilot_guard.py", "autopilot-hook.sh"):
        if "scripts/" + name in hook["command"]:
            assert (REPO / "scripts" / name).is_file()
