"""Test cho scripts/autopilot_guard.py — rào máy autopilot (hook PreToolUse). Chạy: python -m pytest -q tests/test_autopilot_guard.py"""

from __future__ import annotations

import io
import json
import os
import sys

import pytest

import autopilot_guard
import check
from conftest import SCRIPTS

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


def blocked(payload, fmt="claude"):
    rc, out, err = run(fmt, payload)
    return rc, out, err


def assert_blocked(repo, cmd, item):
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)
    assert "'{}'".format(item) in err and "cần người dùng nói trong chat — lệnh không chạy" in err


def assert_allowed(repo, cmd):
    rc, out, err = run("claude", claude(cmd, repo))
    assert (rc, out, err) == (0, "", ""), (cmd, rc, err)


# --- đối chiếu hằng với check.py -------------------------------------------------------------------------------

def test_guard_uses_check_exclusions():
    assert autopilot_guard.known_exclusions() == check.AUTOPILOT_EXCLUSIONS


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
                "rm -rf .tmp/a .tmp/b", "rm -rf '.tmp/with space'", "rm -rf .tmp/out*", "rm -rf .tmp/scratch/*",
                "rm -rf " + str(repo / ".tmp" / "scratch"), "rmdir /s /q .tmp\\scratch"):
        assert_allowed(repo, cmd)


@pytest.mark.parametrize("cmd", [
    "rm -rf .tmp", "rm -rf .tmp/", "rm -rf .tmp/.", "rm -rf .tmp/*", "rm -rf .tmp/a*", "rm -rf .tmp/autopilot.json",
    "rm -rf .tmp/AUTOPILOT.JSON", "rm -rf .tmp/../src", "rm -rf .tmp/x/../../src", "rm -rf .tmp/scratch ..", "rm -rf .tmp/scratch build",
    "rm -rf src/.tmp/x", "rm -rf /tmp/x", "rm -rf .tmp/$X", "rm -rf .tmp/x,../y", "rm -rf ~/.tmp/x", "rm -rf .tmp/{a,b}",
    "rm -rf .tmp/*/x/../..", "rm -rf .tm*/x", "rm -rf .tmp/ab[c]", "cd src && rm -rf .tmp/scratch",
    "rm -rf .tmpx/a", "rm -rf", "Remove-Item -Recurse .tmp",
])
def test_guard_tmp_exception_not_applied(tmp_path, cmd):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    (repo / "src").mkdir()
    # `.tmp/ab[c]` khớp ký tự lớp glob trong thành phần cuối: không chứa autopilot.json nên được qua; giữ ngoài danh sách chặn.
    if cmd == "rm -rf .tmp/ab[c]":
        assert_allowed(repo, cmd)
        return
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


def test_guard_deep_command_nesting_stops(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    cmd = "git push"
    for _ in range(6):
        cmd = 'bash -c "{}"'.format(cmd.replace('"', "'"))
    rc, _, _ = run("claude", claude(cmd, repo))
    assert rc in (0, 2)  # lồng quá sâu: dừng mở lớp, không văng ngoại lệ, không treo


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
