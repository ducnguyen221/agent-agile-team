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


@pytest.mark.parametrize("cmd", [
    "rm -rf build", "rm -fr build", "rm -Rf build", "rm -r -f build", "rm --recursive build", "rm -r build",
    "rm -rfv build", "rm -fR build", "rm -r",  # không đích: vẫn chặn
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
    assert_blocked(repo, "git add -A && git commit -m x && rm -rf x", "irreversible_delete")
    assert_blocked(repo, "ls; rm -rf x", "irreversible_delete")
    assert_blocked(repo, "git log | cat\nrm -rf x", "irreversible_delete")
    assert_blocked(repo, "false || rm -rf x", "irreversible_delete")
    assert_blocked(repo, "(rm -rf x)", "irreversible_delete")
    assert_blocked(repo, "echo $(rm -rf x)", "irreversible_delete")
    assert_blocked(repo, "sleep 1 & rm -rf x", "irreversible_delete")
    assert_blocked(repo, "sudo rm -rf x", "irreversible_delete")
    assert_blocked(repo, "bash -c 'git add . && rm -rf x'", "irreversible_delete")
    assert_blocked(repo, 'pwsh -NoProfile -Command "rm -rf x"', "irreversible_delete")
    assert_blocked(repo, "cmd /c rm -rf x", "irreversible_delete")
    # chặn nhầm có chủ ý (mục 5.1): tách thô không hiểu dấu nháy
    assert_blocked(repo, 'git commit -m "a && rm -rf x"', "irreversible_delete")


def test_guard_exclusions_missing_required_filled_in(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker(["version"]))  # thiếu push, tag, ...
    assert_blocked(repo, "rm -rf x", "irreversible_delete")
    assert_blocked(repo, "rm -rf x", "irreversible_delete")
    # mục lạ bị bỏ qua, không làm hỏng
    odd = make_repo(tmp_path / "o", branch="spr-12", marker=good_marker(WITHOUT_BRANCH + ["bogus", 3]))
    assert_blocked(odd, "rm -rf x", "irreversible_delete")
    assert_allowed(odd, "git merge x")


@pytest.mark.parametrize("text", ["{not json", "", "[]", "null", '"x"', "\xef\xbf\xbd"])
def test_guard_bad_marker_fails_closed(tmp_path, text):
    repo = make_repo(tmp_path, branch="spr-12", marker=text)
    rc, _, err = run("claude", claude("rm -rf x", repo))
    assert rc == 2 and "file dấu hỏng" in err and "'irreversible_delete'" in err
    assert_allowed(repo, "ls")  # lệnh không khớp mẫu vẫn qua


def test_guard_bad_marker_binary_bytes(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    (repo / ".tmp" / "autopilot.json").write_bytes(b"\xff\xfe\x00bad")
    rc, _, err = run("claude", claude("rm -rf x", repo))
    assert rc == 2 and "file dấu hỏng" in err


def test_guard_codex_and_antigravity_event_shapes(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    # Codex: tool shell, command dạng chuỗi hoặc danh sách ["bash","-lc","<script>"], cwd ở payload hoặc workdir
    for tool in ("shell", "Bash", "exec_command"):
        rc, out, err = run("codex", {"tool_name": tool, "tool_input": {"command": "rm -rf x"}, "cwd": str(repo)})
        assert rc == 2 and out == "" and "'irreversible_delete'" in err
    rc, _, err = run("codex", {"tool_name": "shell", "tool_input": {"command": ["bash", "-lc", "git add . && rm -rf x"], "workdir": str(repo)}})
    assert rc == 2 and "'irreversible_delete'" in err
    rc, _, err = run("codex", {"tool_name": "shell", "tool_input": {"command": ["rm", "-rf", "x"]}, "cwd": str(repo)})
    assert rc == 2 and "'irreversible_delete'" in err
    rc, _, err = run("codex", {"tool_name": "shell", "tool_input": {"cmd": "rm -rf x"}, "cwd": str(repo)})
    assert rc == 2
    assert run("codex", {"tool_name": "shell", "tool_input": {"command": ["ls"]}, "cwd": str(repo)}) == (0, "", "")
    # Codex apply_patch có khoá command nhưng là patch, không phải shell
    patch = "*** Begin Patch\n*** Update File: a.md\n+rm -rf x\n*** End Patch"
    assert run("codex", {"tool_name": "apply_patch", "tool_input": {"command": patch}, "cwd": str(repo)}) == (0, "", "")
    # Antigravity: toolCall.args.CommandLine, in JSON quyết định chặn ở stdout, thoát 0; cho qua in {}
    payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf x", "Cwd": str(repo)}}, "stepIdx": 1}
    rc, out, err = run("antigravity", payload)
    assert rc == 0 and err == ""
    decision = json.loads(out)
    assert decision["decision"] == "deny" and "'irreversible_delete'" in decision["reason"]
    ok = {"toolCall": {"name": "run_command", "args": {"CommandLine": "ls", "Cwd": str(repo)}}, "stepIdx": 1}
    assert run("antigravity", ok) == (0, "{}\n", "")
    write = {"toolCall": {"name": "write_to_file", "args": {"TargetFile": str(repo / "a.md")}}}
    assert run("antigravity", write) == (0, "{}\n", "")
    # PowerShell của Claude trên Windows
    rc, _, err = run("claude", claude("rm -rf x", repo, tool="PowerShell"))
    assert rc == 2
    # công cụ không phải shell: cho qua dù chứa chữ rm -rf x
    assert run("claude", {"tool_name": "Write", "tool_input": {"file_path": "x", "content": "rm -rf x", "command": "rm -rf x"}, "cwd": str(repo)}) == (0, "", "")
    assert run("claude", {"tool_name": "mcp__x__y", "tool_input": {"command": "rm -rf x"}, "cwd": str(repo)}) == (0, "", "")
    # không có tên công cụ nhưng có lệnh: coi là shell (đóng)
    assert run("claude", {"tool_input": {"command": "rm -rf x"}, "cwd": str(repo)})[0] == 2
    # shell mà không có lệnh
    assert run("claude", {"tool_name": "Bash", "tool_input": {}, "cwd": str(repo)}) == (0, "", "")


# --- tìm file dấu và nhánh ----------------------------------------------------------------------------------------

def test_guard_finds_marker_walking_up(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    sub = repo / "src" / "deep"
    sub.mkdir(parents=True)
    assert_blocked(sub, "rm -rf x", "irreversible_delete")


def test_guard_stops_at_first_git(tmp_path):
    outer = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    inner = outer / "vendor"
    (inner / ".git").mkdir(parents=True)  # repo lồng: file dấu ở ngoài không áp
    assert_allowed(inner, "rm -rf x")


def test_guard_no_cwd_uses_process_cwd(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    monkeypatch.chdir(repo)
    rc, _, err = run("claude", {"tool_name": "Bash", "tool_input": {"command": "rm -rf x"}})
    assert rc == 2 and "'irreversible_delete'" in err
    monkeypatch.chdir(tmp_path)
    assert run("claude", {"tool_name": "Bash", "tool_input": {"command": "rm -rf x"}}) == (0, "", "")


def test_guard_marker_without_git_repo(tmp_path):
    (tmp_path / "plain" / ".tmp").mkdir(parents=True)
    (tmp_path / "plain" / ".tmp" / "autopilot.json").write_text(json.dumps(good_marker(WITHOUT_BRANCH)), encoding="utf-8")
    assert_blocked(tmp_path / "plain", "rm -rf x", "irreversible_delete")
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
    rc, _, err = run("claude", claude(_nest("rm -rf x", 3), repo))  # trong giới hạn: mở hết lớp, thấy push
    assert rc == 2 and "'irreversible_delete'" in err
    rc, _, err = run("claude", claude(_nest("rm -rf x", 4), repo))  # quá giới hạn: không phân tích được → chặn
    assert rc == 2 and "lồng" in err and "hook gặp lỗi" not in err
    rc, _, err = run("claude", claude(_nest("ls", 6), repo))
    assert rc == 2 and "lồng" in err
    plain = tmp_path / "plain"
    plain.mkdir()
    assert run("claude", claude(_nest("rm -rf x", 6), plain)) == (0, "", "")  # không có file dấu → qua


def test_guard_cli_subprocess(tmp_path):
    import subprocess
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    payload = json.dumps(claude("rm -rf x", repo))
    proc = subprocess.run([sys.executable, str(SCRIPTS / "autopilot_guard.py"), "--format", "claude"], input=payload,
                          capture_output=True, text=True, encoding="utf-8", cwd=str(repo))
    assert proc.returncode == 2 and "'irreversible_delete'" in proc.stderr and proc.stdout == ""
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
    rc, _, err = run("codex", codex(["bash", "-lc", "rm -rf x"], cwd=elsewhere, workdir=repo))
    assert rc == 2 and "'irreversible_delete'" in err
    # cwd phiên trong repo có file dấu, workdir nơi không có: file dấu của phiên vẫn áp (thấy ở đâu cũng bật)
    rc, _, err = run("codex", codex(["bash", "-lc", "rm -rf x"], cwd=repo, workdir=elsewhere))
    assert rc == 2
    # workdir tương đối ghép với cwd phiên; Antigravity: Cwd trong args thắng cwd phiên
    (repo / "sub").mkdir()
    rc, _, err = run("codex", {"tool_name": "shell", "cwd": str(repo), "tool_input": {"command": "rm -rf x", "workdir": "sub"}})
    assert rc == 2
    ag = {"toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf x", "Cwd": str(repo)}}, "cwd": str(elsewhere)}
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
    "timeout 60 rm -rf x", "timeout -s KILL 30 rm -rf x", "timeout --signal=KILL 5 rm -rf x", "timeout -k 5 60 rm -rf x",
    "env -i rm -rf x", "env -u HOME rm -rf x", "env FOO=bar BAZ=1 rm -rf x", "env -i FOO=1 rm -rf x", "env -S 'rm -rf x'",
    "sudo -u deploy rm -rf x", "sudo -E rm -rf x", "sudo -u x -g y rm -rf x", "sudo --user=x rm -rf x",
    "nice -n 10 rm -rf x", "nice -10 rm -rf x", "command -p rm -rf x", "nohup rm -rf x", "time rm -rf x", "time -p rm -rf x",
    "ls | xargs -0 rm -rf x", "xargs -n 1 -I {} rm -rf x", "echo x | xargs -r rm -rf x",
    "stdbuf -oL rm -rf x", "exec rm -rf x", "/usr/bin/env rm -rf x", "sudo env FOO=1 timeout 5 rm -rf x",
])
def test_guard_prefix_wrappers_with_their_arguments(tmp_path, cmd):
    """S-RF2 / T-RF6: tiền tố kèm cờ và đối số vẫn lộ lệnh thật."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, cmd, "irreversible_delete")


def test_guard_prefix_wrappers_other_items(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, "timeout 60 rm -rf build", "irreversible_delete")
    assert_blocked(repo, "ls | xargs -0 rm -rf", "irreversible_delete")
    assert_allowed(repo, "timeout 60 ls")
    assert_allowed(repo, "env -i FOO=1 ls")
    assert_allowed(repo, "sudo -u x ls")


def test_guard_more_patterns(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, "find . -name '*.o' -delete", "irreversible_delete")
    assert_blocked(repo, "find build -exec rm -rf {} +", "irreversible_delete")
    assert_blocked(repo, "find build -type d -execdir rm -r {} +", "irreversible_delete")
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



# ===================== vòng sửa 3: mọi thao tác đổi thư mục trước merge/pull (không -C) = main =====================



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


@pytest.mark.parametrize("cmd", ["sudo -Hu deploy rm -rf x", "sudo -Eu root rm -rf x", "env -iu HOME rm -rf x", "xargs -tI {} rm -rf x",
                                 "sudo -EHu x -g y rm -rf x", "env -iC /tmp rm -rf x"])
def test_guard_short_flag_clusters_ending_in_value_flag(tmp_path, cmd):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, cmd, "irreversible_delete")
    assert_allowed(repo, cmd.replace("rm -rf x", "ls"))


def test_guard_line_continuation_joined(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, "rm \\\n-rf x", "irreversible_delete")
    assert_blocked(repo, "rm \\\r\n  -rf x", "irreversible_delete")
    assert_blocked(repo, "rm `\n-rf x", "irreversible_delete")
    assert_blocked(repo, "rm -rf \\\n x", "irreversible_delete")
    assert_allowed(repo, "ls \\\n-l")
    assert_blocked(repo, "ls\nrm -rf x", "irreversible_delete")


@pytest.mark.parametrize("cmd,item", [
    ('eval "rm -rf x"', "irreversible_delete"), ("eval rm -rf x", "irreversible_delete"), ("eval 'git add . && rm -rf x'", "irreversible_delete"), ("eval rm -rf build", "irreversible_delete"),
    ('iex "rm -rf x"', "irreversible_delete"), ("Invoke-Expression 'rm -rf x'", "irreversible_delete"),
    ("echo rm -rf x | bash", "irreversible_delete"), ('echo "rm -rf x" | sh', "irreversible_delete"), ("printf 'rm -rf x' | pwsh", "irreversible_delete"),
    ("echo rm -rf x | sudo bash", "irreversible_delete"), ("echo rm -rf x | bash -s", "irreversible_delete"), ("echo rm -rf x | iex", "irreversible_delete"),
    ('bash <<< "rm -rf x"', "irreversible_delete"), ("echo rm -rf build | bash", "irreversible_delete"),
])
def test_guard_eval_and_pipe_into_shell(tmp_path, cmd, item):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)
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
    for cmd in ("git -C {r} worktree remove --force x", "git -C {rel} worktree remove --force x", "git -C {rel} stash -a", "cd {rel} && rm -rf x",
                "bash -c 'git -C {rel} worktree remove --force x'", "git -c a=b -C {rel} worktree remove --force x", "Set-Location {rel}; rm -rf x"):
        rc, _, err = run("claude", claude(cmd.format(r=fwd(repo), rel=rel), outside))
        assert rc == 2, (cmd, err)
    assert run("claude", claude("git -C {} status".format(rel), outside)) == (0, "", "")
    assert run("claude", claude("git -C {} worktree remove --force x".format(fwd(outside)), outside)) == (0, "", "")  # đích không có file dấu


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
    blocked_run = run_launcher(repo, claude("rm -rf x", repo), path)
    if blocked_run.returncode == 2 and "không chạy được Python" in blocked_run.stderr:
        pytest.skip("launcher không thấy Python dùng được trong PATH thử")
    assert blocked_run.returncode == 2 and "'irreversible_delete'" in blocked_run.stderr
    assert run_launcher(repo, claude("ls", repo), path).returncode == 0
    plain = make_repo(tmp_path / "p", branch="spr-12")
    assert run_launcher(plain, claude("rm -rf x", plain), path).returncode == 0


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
    assert set(config["hooks"]) == {"PreToolUse"}  # SPR-20 TK21: bỏ khối SessionStart (shim đã gỡ)
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
    done = run_launcher(marked, claude("rm -rf x", marked), path, {"AUTOPILOT_GUARD_PATH": fwd(evil)})
    if "không chạy được Python" in done.stderr:
        pytest.skip("launcher không thấy Python dùng được trong PATH thử")
    assert done.returncode == 2 and "'irreversible_delete'" in done.stderr  # guard thật vẫn chạy, giả không thay được
    assert run_launcher(plain, claude("ls", plain), path, {"AUTOPILOT_GUARD_PATH": fwd(evil)}).returncode == 0


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
    # TK27b A1(iii): `find … -exec rm` chỉ qua khi điểm bắt đầu nằm trong `.tmp/` (trước đây `find build -exec rm {} +` qua)
    for cmd in ("find .tmp/x -exec rm {} +", "find . -name '*.py'", "find .tmp -exec grep level {} +", "find . -exec cat {} +",
                "find .tmp -name x -print", "find build -type f -exec ls {} +"):
        assert_allowed(repo, cmd)
    assert_blocked(repo, "find build -exec rm {} +", "irreversible_delete")


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
    for cmd in ("rm -rf {r}", "rm -rf {rel}", "rm -rf {r}/build", "rm -rf {r}/.tmp"):
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
    "python - <<EOF\nrm -rf x\nEOF", "python - <<'EOF'\nrm -rf build\nrm -rf x\nEOF", "node - <<-EOF\n\trm -rf x\n\tEOF",
    "cat > notes.txt <<EOF\nrm -rf x\nEOF", "python3 - <<\"PY\"\nsubprocess.run(['git','push'])\nrm -rf x\nPY",
    "python - <<EOF\nrm -rf x\nEOF\ngit status", "cat <<EOF\nrm -rf x\nEOF", "tee out.txt <<EOF\nrm -rf x\nEOF",
])
def test_guard_heredoc_body_for_non_shell_is_data(tmp_path, cmd):
    """N3: thân heredoc cho python/node/cat… là dữ liệu, không bị coi là lệnh."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_allowed(repo, cmd)


@pytest.mark.parametrize("cmd,item", [
    ("bash <<EOF\nrm -rf x\nEOF", "irreversible_delete"), ("sh <<'EOF'\nrm -rf build\nEOF", "irreversible_delete"), ("bash -s <<-EOF\n\trm -rf x\n\tEOF", "irreversible_delete"),
    ("pwsh <<EOF\nrm -rf x\nEOF", "irreversible_delete"), ("cat <<EOF | bash\nrm -rf x\nEOF", "irreversible_delete"), ("python - <<EOF\nx\nEOF\nrm -rf x", "irreversible_delete"),
    ("cat > f <<EOF\nx\nEOF\nrm -rf x", "irreversible_delete"), ("eval <<EOF\nrm -rf x\nEOF", "irreversible_delete"),
    ("python - <<EOF\nx\nEOF\ncat <<EOF2 > .tmp/autopilot.json\ny\nEOF2", "marker"),
])
def test_guard_heredoc_body_for_shell_still_analyzed(tmp_path, cmd, item):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    rc, _, err = run("claude", claude(cmd, repo))
    assert rc == 2, (cmd, err)
    assert (MARKER_REASON if item == "marker" else "'{}'".format(item)) in err


@pytest.mark.parametrize("cmd", ["git stash -a", "git stash --all", "git stash push -a", "git stash push --all -m x", "git stash -ua", "git stash -au",
                                 "git stash push -ua", "git -C . stash -a",
                                 "git clean -fdx", "git clean -xdf", "git clean -fX", "git clean -f -x", "git clean --force -x", "git clean -f -X",
                                 "git clean -x --force", "git clean -fdX", "git -C . clean -fdx"])
def test_guard_marker_pattern_blocked(tmp_path, cmd):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_marker_blocked(repo, cmd)


def test_guard_stash_and_clean_plain_allowed(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    # TK27b A3: `stash -u` và `clean -f[d]` chỉ còn qua khi file dấu bị gitignore (repo thật) — các ca đó ở tests/test_autopilot_guard_undo.py
    for cmd in ("git stash", "git stash list", "git stash pop", "git stash push -m x", "git stash show -p",
                "git clean -n", "git clean -nx", "git clean -x"):
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
    "echo 'a <<END'\nrm -rf x",
    'git commit -m "x <<EOF"\nrm -rf x origin HEAD',
    "echo \"y <<'EOF'\"\nrm -rf x",
    "echo hi # <<EOF\nrm -rf x",
    "echo a <<<'x <<EOF'\nrm -rf x",
    "cat <<EOF\nrm -rf x",  # không có dòng kết thúc: giữ thân để phân tích
    "python - <<EOF\nprint(1)\nrm -rf x\nEOFX",  # nhãn kết thúc phải khớp đúng
    "python - <<EOF\nprint(1)\n EOF\nrm -rf x",  # thụt lề không phải dòng kết thúc của <<
    "echo 'multi\nline <<EOF'\nrm -rf x\nEOF",
])
def test_guard_heredoc_only_outside_quotes_and_comments(tmp_path, cmd):
    """RF16: `<<` trong nháy hay comment, hoặc heredoc không có dòng kết thúc, không được che lệnh thật."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    assert_blocked(repo, cmd, "irreversible_delete")


def test_guard_real_heredoc_still_data(tmp_path):
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("python - <<EOF\nrm -rf x\nEOF", "python - <<'EOF'\nrm -rf x\nEOF", "node - <<-EOF\n\trm -rf x\n\tEOF",
                "cat > f <<EOF\nrm -rf x\nEOF", "python - <<EOF\nx = '<<'\nrm -rf x\nEOF\ngit status"):
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
    for cmd in ("python - <<X\nx = $(rm -rf x)\nX", "cat > f <<X\nrun `rm -rf x origin main`\nX", "cat <<-X\n\t$(rm -rf build)\n\tX",
                "python - <<X\na $(echo $(rm -rf x)) b\nX", "tee f <<EOF\n$(rm -rf x)\nEOF"):
        rc, _, err = run("claude", claude(cmd, repo))
        assert rc == 2, (cmd, err)
    for cmd in ("python - <<'X'\nx = $(rm -rf x)\nX", 'python - <<"X"\nx = $(rm -rf x)\nX', "cat > f <<\\X\n`rm -rf x` x\nX",
                "python - <<X\nx = $(ls) $((1+2)) `ls`\nX", "python - <<X\nplain text rm -rf x\nX"):
        assert_allowed(repo, cmd)



def test_guard_continuation_before_heredoc_scan(tmp_path):
    """RF19 (hồi quy fix 4): `bash` + dấu gạch ngược + xuống dòng + `<<EOF` — nối dòng trước khi dò heredoc, nên thân vẫn được phân tích."""
    repo = make_repo(tmp_path, branch="spr-12", marker=good_marker())
    for cmd in ("bash \\\n<<EOF\nrm -rf x\nEOF", "sh \\\n-s <<EOF\nrm -rf x\nEOF", "bash \\\n<<'EOF'\nrm -rf x\nEOF",
                "bash -s \\\n  <<-EOF\n\trm -rf x\n\tEOF"):
        assert_blocked(repo, cmd, "irreversible_delete")
    assert_allowed(repo, "python - \\\n<<'EOF'\nrm -rf x\nEOF")  # trình không phải shell: thân vẫn là dữ liệu
    assert_allowed(repo, "python - \\\n<<EOF\nx\nEOF\nls")
