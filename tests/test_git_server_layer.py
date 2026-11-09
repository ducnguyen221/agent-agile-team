"""Lớp độc lập thứ hai cho việc đẩy (SPR-16 TK10, FR6): `pre-push` mẫu và remote trần có `pre-receive` mô phỏng ruleset.

Mỗi ca dùng git thật trong `tmp_path` (remote trần cục bộ, không mạng). Lệnh đẩy chạy bằng script — không qua guard (lớp a) —
nên chứng minh lớp (b) chặn cả khi lớp (a) không nhìn thấy. Cài `pre-push` vào repo thật và đặt ruleset GitHub không nằm trong test.
"""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import autopilot_guard

REPO = Path(__file__).resolve().parent.parent
PRE_PUSH = REPO / "templates" / "git-hooks" / "pre-push"
PRE_RECEIVE = """#!/bin/sh
# mô phỏng ruleset: từ chối mọi cập nhật refs/heads/main
while read -r old new ref; do
  if [ "$ref" = "refs/heads/main" ]; then
    echo "pre-receive: ruleset mô phỏng từ chối $ref" >&2
    exit 1
  fi
done
exit 0
"""

pytestmark = pytest.mark.skipif(shutil.which("git") is None or shutil.which("sh") is None, reason="cần git và sh")


def git(cwd, *args, check=True):
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull, GIT_TERMINAL_PROMPT="0",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com")
    done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, encoding="utf-8", env=env)
    if check:
        assert done.returncode == 0, (args, done.stderr)
    return done


@pytest.fixture
def world(tmp_path):
    remote = tmp_path / "remote.git"
    remote.mkdir()
    git(remote, "init", "-q", "--bare", "-b", "main")
    hook = remote / "hooks" / "pre-receive"
    hook.write_bytes(PRE_RECEIVE.encode("utf-8"))
    os.chmod(hook, 0o755)
    work = tmp_path / "work"
    work.mkdir()
    git(work, "init", "-q", "-b", "main")
    (work / "a.txt").write_text("a\n", encoding="utf-8")
    (work / ".agile.json").write_text("{}", encoding="utf-8")
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", "init")
    git(work, "remote", "add", "origin", str(remote))
    git(work, "checkout", "-q", "-b", "spr-x")
    return work, remote


def install_pre_push(work):
    target = work / ".git" / "hooks" / "pre-push"
    target.write_bytes(PRE_PUSH.read_bytes())
    os.chmod(target, 0o755)


def test_pre_receive_alone_rejects_main_and_accepts_sprint_branch(world):
    work, _ = world
    assert git(work, "push", "origin", "HEAD:main", check=False).returncode != 0
    assert git(work, "push", "origin", "HEAD:spr-x", check=False).returncode == 0


def test_pre_push_rejects_main_locally(world):
    work, remote = world
    install_pre_push(work)
    done = git(work, "push", "origin", "HEAD:main", check=False)
    assert done.returncode != 0 and "pre-push: từ chối" in done.stderr
    assert "pre-receive" not in done.stderr  # bị chặn trước khi tới máy chủ
    assert git(work, "push", "origin", "HEAD:spr-x", check=False).returncode == 0


def test_pre_push_honours_configured_protected_branches(world):
    work, _ = world
    install_pre_push(work)
    git(work, "config", "agile.protectedBranches", "release, develop")
    for name in ("release", "develop", "master"):
        done = git(work, "push", "origin", "HEAD:" + name, check=False)
        assert done.returncode != 0 and "pre-push: từ chối" in done.stderr, name
    assert git(work, "push", "origin", "HEAD:spr-y", check=False).returncode == 0


def test_server_layer_still_blocks_when_pre_push_is_bypassed(world):
    work, _ = world
    install_pre_push(work)
    done = git(work, "push", "--no-verify", "origin", "HEAD:main", check=False)
    assert done.returncode != 0 and "pre-receive" in done.stderr


def test_script_push_slips_past_guard_but_not_past_layer_b(world):
    """Đẩy bằng script `python -c "subprocess…"`: guard (lớp a) không nhận dạng → không chặn; lớp (b) chặn."""
    work, _ = world
    script = "import subprocess; subprocess.run(['git','push','origin','HEAD:main'])"
    command = 'python -c "{}"'.format(script)
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(work)}
    out, err = io.StringIO(), io.StringIO()
    assert autopilot_guard.main(["--format", "claude"], stdin=io.StringIO(json.dumps(payload)), stdout=out, stderr=err) == 0
    assert out.getvalue() == "" and err.getvalue() == ""  # (a) không chặn: giới hạn đã biết ở method/git-permissions.md mục 8
    install_pre_push(work)
    git(work, "config", "core.hooksPath", str(work / ".git" / "hooks"))
    ran = subprocess.run([sys.executable, "-c", script], cwd=str(work), capture_output=True, text=True, encoding="utf-8",
                         env=dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull))
    assert "pre-push: từ chối" in ran.stderr or "pre-receive" in ran.stderr  # (b) chặn


def test_template_is_posix_sh_and_has_no_bashisms():
    text = PRE_PUSH.read_text(encoding="utf-8")
    assert text.startswith("#!/bin/sh\n") and "[[" not in text and "<<<" not in text
