"""SPR-20 TK27b: vòng sửa gộp sau soát Tech + Security — rào máy cho thao tác phá cơ chế hoàn tác.

A1 (Sec RF2/RF6): ghép `mv` vào `.tmp/` rồi xoá; xoá đích thuộc `.git`; xoá đệ quy kiểu đường ống/`find -exec`/.NET/`robocopy /MIR`/`busybox`.
A2 (Sec RF3): `reflog expire`, `gc --prune=now`, `update-ref -d`, đẩy xoá/ép, `branch -D`.
A3 (Tech RF2): `stash -u` và `clean -f` chỉ chặn khi file dấu KHÔNG bị gitignore; `-c clean.requireForce=false clean -x`.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

import autopilot_guard
from test_autopilot_guard import MARKER_REASON, assert_allowed, assert_blocked, assert_marker_blocked, good_marker, make_repo, run

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="cần git")


def active_repo(tmp_path):
    return make_repo(tmp_path, branch="spr-20", marker=good_marker())


def real_repo(tmp_path, ignored):
    """Repo git THẬT có file dấu; `ignored` = `.tmp/` nằm trong .gitignore hay không."""
    repo = tmp_path / "repo"
    (repo / ".tmp").mkdir(parents=True)
    done = subprocess.run(["git", "init", "-q", str(repo)], capture_output=True)
    assert done.returncode == 0, done.stderr
    (repo / ".tmp" / "autopilot.json").write_text('{"sprints": ["SPR-20"]}', encoding="utf-8")
    if ignored:
        (repo / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
    return repo


# --- A1 (i): chuyển vào .tmp/ rồi xoá ------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    "mv src .tmp/x && rm -rf .tmp/x",
    "mv .git .tmp/g; rm -rf .tmp/g",
    "Move-Item src .tmp/x; Remove-Item .tmp/x -Recurse",
    "Rename-Item src .tmp/x; rm -rf .tmp/x",
    "move src .tmp\\x & rmdir /s /q .tmp\\x",
    "mv -t .tmp/x src && rm -rf .tmp/x",
    "robocopy src .tmp/x /E && rm -rf .tmp/x",
    "cp -r .git .tmp/g && rm -rf .tmp/g",
    "bash -c 'mv .git .tmp/g && rm -rf .tmp/g'",
    "mv src .tmp/x\nrm -rf .tmp/x",
    "mv src .tmp/x; bash -c 'rm -rf .tmp/x'",
])
def test_guard_move_into_tmp_then_delete_blocked(tmp_path, cmd):
    assert_blocked(active_repo(tmp_path), cmd, "irreversible_delete")


def test_guard_move_into_tmp_alone_or_delete_alone_still_allowed(tmp_path):
    repo = active_repo(tmp_path)
    for cmd in ("rm -rf .tmp/x", "mv src .tmp/x", "cp -r a .tmp/x", "mv a b && rm -rf .tmp/x", "cp a .tmp/x && rm -rf .tmp/y",
                "mv a b; mv c d"):
        assert_allowed(repo, cmd)


# --- TK27c: nguồn chuyển/chép thuộc .git (lỗ hai bước: `mv .git .tmp/x/g` rồi lệnh riêng `rm -rf .tmp/x`) ----------

@pytest.mark.parametrize("cmd", [
    "mv .git .tmp/x/g",
    "mv .git/ .tmp/x",
    "mv -t .tmp/x .git",
    "mv a .git .tmp/x",
    "Move-Item .git .tmp/x",
    "move .git .tmp\\x",
    "ren .git g",
    "Rename-Item .git g",
    "mv .g* .tmp/x",
    "robocopy .git .tmp/x /E",
    "bash -c 'mv .git .tmp/x'",
])
def test_guard_move_or_copy_git_source_blocked(tmp_path, cmd):
    assert_blocked(active_repo(tmp_path), cmd, "irreversible_delete")


def test_guard_move_non_git_source_still_allowed(tmp_path):
    repo = active_repo(tmp_path)
    for cmd in ("mv src .tmp/x", "mv .gitignore .tmp/x", "mv a .git-notes", "cp -r src .tmp/x", "robocopy src .tmp/x /E",
                "mv .tmp/x .git", "cp .git/HEAD .tmp/x",
                # TK27d: sao chép không phá gì (nguồn còn nguyên); chỉ chép vào `.tmp/` rồi xoá ở đó mới bị chặn (`_moves_into_tmp`)
                "cp -r .git backup", "cp -r .git .tmp/x", "Copy-Item .git D:/b -Recurse"):
        assert_allowed(repo, cmd)


# --- A1 (ii): đích xoá thuộc .git ---------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    "rm .git/index", "rm -rf .git", "rm -f .git/HEAD", "Remove-Item .git -Force", "Remove-Item -Recurse -Force .git",
    "rm -rf ./.git", "rm -rf .tmp/x/.git", "del .git\\index", "rmdir .git", "rm sub/.git/config", "ri .git/index", "rm .git",
])
def test_guard_delete_inside_git_always_blocked(tmp_path, cmd):
    assert_blocked(active_repo(tmp_path), cmd, "irreversible_delete")


def test_guard_delete_of_look_alike_git_names_allowed(tmp_path):
    repo = active_repo(tmp_path)
    for cmd in ("rm .gitignore", "rm .github/x", "rm file.git", "rm -f legit.gitkeep", "rm .tmp/a.git"):
        assert_allowed(repo, cmd)


# --- A1 (iii): xoá đệ quy dạng đường ống, find -exec, .NET, robocopy, busybox ----------------------------------------

@pytest.mark.parametrize("cmd", [
    "Get-ChildItem . -Recurse | Remove-Item",
    "gci -Recurse src | Remove-Item -Force",
    "Get-ChildItem -Path src -Recurse | ri",
    "gci src -r | rm -Force",
    "ls -Recurse | Remove-Item",
    "find src -name '*.o' -exec rm {} +",
    "find src -exec rm -f {} \\;",
    "find src -type f -exec rm {} ';'",
    "[IO.Directory]::Delete('src', $true)",
    "[System.IO.Directory]::Delete($p,$true)",
    "(Get-Item src).Delete($true)",
    "robocopy empty src /MIR",
    "robocopy empty .git /PURGE",
    "robocopy empty src /mir",
    "busybox rm -rf src",
    "busybox sh -c 'rm -rf src'",
])
def test_guard_other_recursive_delete_forms_blocked(tmp_path, cmd):
    assert_blocked(active_repo(tmp_path), cmd, "irreversible_delete")


def test_guard_other_recursive_delete_forms_inside_tmp_allowed(tmp_path):
    repo = active_repo(tmp_path)
    for cmd in ("Get-ChildItem .tmp/x -Recurse | Remove-Item", "find .tmp/x -exec rm {} +", "robocopy a .tmp/x /MIR",
                "busybox rm -rf .tmp/x", "find . -exec grep x {} +", "Get-ChildItem . | Select-Object Name", "gci src -Recurse | Select-String x",
                "[IO.File]::ReadAllText('a')", "robocopy a b /E", "busybox ls", "(Get-Item a).Length"):
        assert_allowed(repo, cmd)


def test_guard_pipeline_delete_after_cd_is_blocked_even_inside_tmp(tmp_path):
    assert_blocked(active_repo(tmp_path), "cd src && Get-ChildItem .tmp/x -Recurse | Remove-Item", "irreversible_delete")


# --- A2: lệnh phá cơ chế hoàn tác -----------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd", [
    "git reflog expire --expire=now --all", "git reflog expire --all", "git reflog delete HEAD@{1}",
    "git gc --prune=now", "git gc --prune now", "git gc --aggressive --prune=now", "git prune --expire now",
    "git update-ref -d refs/heads/x", "git update-ref --delete refs/heads/x",
    "git push origin --delete foo", "git push -d origin foo", "git push origin :foo", "git push origin +main", "git push origin +HEAD:main",
    "git push --force", "git push -f origin main", "git push --force-with-lease", "git push --force-if-includes origin x", "git push origin x --mirror",
    "git branch -D x", "git -C . branch -D x", "git branch -dD x", "git branch --delete --force x",
    "git -c core.x=1 push --force",
])
def test_guard_undo_breaking_git_commands_blocked(tmp_path, cmd):
    assert_blocked(active_repo(tmp_path), cmd, "irreversible_delete")


def test_guard_ordinary_git_commands_pass(tmp_path):
    repo = active_repo(tmp_path)
    for cmd in ("git push", "git push origin main", "git push -u origin spr-20/x", "git push origin HEAD:refs/heads/x", "git push origin main:main",
                "git push --dry-run", "git tag v1", "git merge x", "git commit -m 'x'", "git reset --hard HEAD~1", "git branch -d merged",
                "git gc", "git gc --prune=2.weeks.ago", "git reflog", "git reflog show", "git update-ref refs/heads/x HEAD", "git branch -m a b",
                "git push --tags", "git prune"):
        assert_allowed(repo, cmd)


# --- A3: stash -u / clean -f theo trạng thái gitignore của file dấu ---------------------------------------------------

UNIGNORED_ONLY = ["git stash -u", "git stash --include-untracked", "git stash push -u", "git stash push --include-untracked -m x", "git -C . stash -u",
                  "git clean -f", "git clean -fd", "git clean -d -f", "git clean --force",
                  "git -c clean.requireForce=false clean -d"]
ALWAYS_MARKER = ["git stash -a", "git stash --all", "git clean -fx", "git clean -fdX", "git -c clean.requireForce=false clean -x",
                 "git -c clean.requireForce=false clean -dX", "git -c clean.requireForce=0 clean -x", "git -C . -c clean.requireForce=false clean -fdx"]


@pytest.mark.parametrize("cmd", UNIGNORED_ONLY)
def test_guard_stash_clean_blocked_when_marker_not_ignored(tmp_path, cmd):
    assert_marker_blocked(real_repo(tmp_path, ignored=False), cmd)


@pytest.mark.parametrize("cmd", UNIGNORED_ONLY)
def test_guard_stash_clean_allowed_when_marker_ignored(tmp_path, cmd):
    assert_allowed(real_repo(tmp_path, ignored=True), cmd)


@pytest.mark.parametrize("ignored", [True, False])
@pytest.mark.parametrize("cmd", ALWAYS_MARKER)
def test_guard_stash_all_and_clean_x_blocked_in_both_ignore_states(tmp_path, cmd, ignored):
    assert_marker_blocked(real_repo(tmp_path, ignored=ignored), cmd)


def test_guard_ignore_check_error_counts_as_not_ignored(tmp_path):
    """Repo giả (`.git` chỉ có HEAD): `git check-ignore` lỗi → coi là không ignore → chặn."""
    assert_marker_blocked(active_repo(tmp_path), "git stash -u")
    assert_marker_blocked(active_repo(tmp_path / "b"), "git clean -fd")


def test_guard_clean_dry_run_and_plain_clean_still_allowed(tmp_path):
    for ignored in (True, False):
        repo = real_repo(tmp_path / str(ignored), ignored=ignored)
        for cmd in ("git clean -n", "git clean -nx", "git clean -x", "git stash", "git stash list", "git stash pop", "git stash push -m x"):
            assert_allowed(repo, cmd)


def test_guard_marker_ignored_helper_reports_both_states(tmp_path):
    ignored = real_repo(tmp_path / "i", ignored=True)
    plain = real_repo(tmp_path / "p", ignored=False)
    assert autopilot_guard._marker_ignored(str(ignored), str(ignored / ".tmp" / "autopilot.json")) is True
    assert autopilot_guard._marker_ignored(str(plain), str(plain / ".tmp" / "autopilot.json")) is False
    assert MARKER_REASON  # nhập dùng chung: lý do chặn file dấu giữ nguyên


# --- TK27d: dạng dính `-Destination:x`/`-Path:x`, cwd trong `.git`, glob `?git`, `git -c gc.*=now` ------------------------------

@pytest.mark.parametrize("cmd", [
    "Move-Item -Path .git -Destination:.tmp/g; Remove-Item .tmp/g -Recurse -Force",
    "Move-Item src -Destination:.tmp/x; Remove-Item .tmp/x -Recurse",
    "Move-Item -LiteralPath:.git -Destination:.tmp/g",
    "Move-Item -Path:.git -Destination .tmp/g",
    "move-item -PATH:'.git' -DESTINATION:.tmp/g",
    "Move-Item -Path .git -Destination:D:/y",
    "Remove-Item -Path:.git -Recurse",
    "Remove-Item -LiteralPath:.git/index",
    "Move-Item -Path ?git -Destination:D:/y",
    "rm -rf [.]git",
    "rm .git/../?git/index",
])
def test_guard_colon_attached_powershell_flags_blocked(tmp_path, cmd):
    assert_blocked(active_repo(tmp_path), cmd, "irreversible_delete")


def test_guard_colon_attached_flags_ordinary_use_allowed(tmp_path):
    repo = active_repo(tmp_path)
    for cmd in ("Move-Item -Path a -Destination:b", "Move-Item -LiteralPath:a -Destination:.tmp/x", "Copy-Item -Path:.git -Destination:D:/b -Recurse",
                "Remove-Item -Path:.tmp/x -Recurse", "rm *", "rm -f *.txt"):
        assert_allowed(repo, cmd)


def _in_dir(cmd, cwd):
    return {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": str(cwd)}


@pytest.mark.parametrize("cmd", ["cd .git && rm objects/pack/*", "cd .git; mv objects D:/y", "cd .git/objects && rm -f pack/x", "pushd ?git; rm HEAD",
                                 "cd [.]git && Remove-Item index"])
def test_guard_delete_or_move_after_cd_into_git_blocked(tmp_path, cmd):
    assert_blocked(active_repo(tmp_path), cmd, "irreversible_delete")


@pytest.mark.parametrize("cmd", ["rm objects/pack/x", "mv objects D:/y", "Remove-Item index"])
def test_guard_delete_or_move_with_cwd_inside_git_blocked(tmp_path, cmd):
    repo = active_repo(tmp_path)
    rc, _, err = run("claude", _in_dir(cmd, repo / ".git"))
    assert rc == 2 and "'irreversible_delete'" in err, (cmd, rc, err)


def test_guard_cwd_inside_git_still_allows_reading(tmp_path):
    repo = active_repo(tmp_path)
    for cmd in ("ls objects", "cat HEAD", "git log"):
        assert run("claude", _in_dir(cmd, repo / ".git"))[0] == 0, cmd


@pytest.mark.parametrize("cmd", [
    "git -c gc.pruneExpire=now gc",
    "git -c gc.reflogExpire=now -c gc.reflogExpireUnreachable=now -c gc.pruneExpire=now gc",
    "git -c gc.reflogExpire=now reflog expire --all",
    "git -c gc.pruneExpire=now prune",
    "git -C . -c gc.pruneExpire=all gc --aggressive",
    "git -c GC.PruneExpire=NOW gc",
])
def test_guard_git_config_zero_expiry_blocked(tmp_path, cmd):
    assert_blocked(active_repo(tmp_path), cmd, "irreversible_delete")


def test_guard_git_config_other_values_pass(tmp_path):
    repo = active_repo(tmp_path)
    for cmd in ("git -c gc.pruneExpire=2.weeks.ago gc", "git -c core.x=now status", "git -c gc.auto=0 gc", "git commit -m x",
                "git push origin main", "mv a b", "rm -rf .tmp/x", "cp -r .git backup"):
        assert_allowed(repo, cmd)
