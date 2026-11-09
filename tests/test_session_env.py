"""Test cho scripts/session-env.sh — hook SessionStart ghi shims/ + AGENT_AGILE_SHIM vào $CLAUDE_ENV_FILE (SPR-16c). Chạy: python -m pytest -q tests/test_session_env.py"""

from __future__ import annotations

import json
import os
import shutil
import subprocess

import pytest

from conftest import REPO
from test_argv_shim import BASH_OK

SCRIPT = REPO / "scripts" / "session-env.sh"
needs_sh = pytest.mark.skipif(not BASH_OK, reason="không có sh/bash chạy được (WSL stub của Windows không tính)")


def run_script(env_file, extra=None, script=SCRIPT):
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_ENV_FILE", "AGENT_AGILE_SHIM")}
    if env_file is not None:
        env["CLAUDE_ENV_FILE"] = str(env_file)
    env.update(extra or {})
    return subprocess.run(["sh", str(script)], env=env, capture_output=True, text=True, timeout=30)


def test_hooks_json_registers_session_start_next_to_the_pre_tool_use_hooks():
    hooks = json.loads((REPO / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    commands = [h["command"] for entry in hooks["SessionStart"] for h in entry["hooks"]]
    assert commands == ['sh "${CLAUDE_PLUGIN_ROOT}/scripts/session-env.sh"']
    assert "PreToolUse" in hooks  # hook rào cũ còn nguyên


@needs_sh
def test_writes_path_and_flag_lines_and_sourcing_twice_keeps_one_shims_entry(tmp_path):
    env_file = tmp_path / "env.sh"
    done = run_script(env_file)
    assert done.returncode == 0 and done.stderr == ""
    text = env_file.read_text(encoding="utf-8")
    assert "export AGENT_AGILE_SHIM=1" in text and "shims" in text and text.count("\n") == 2
    probe = subprocess.run(["sh", "-c", '. "$1"; . "$1"; . "$1"; echo "$PATH" | tr ":" "\\n" | grep -c shims; echo "$AGENT_AGILE_SHIM"', "x", str(env_file)],
                           capture_output=True, text=True, env={**os.environ, "PATH": os.environ["PATH"]}, timeout=30)
    count, flag = probe.stdout.split()
    assert int(count) <= 2 and flag == "1"  # chạy nạp lại nhiều lần không làm PATH phình thêm (tối đa một mục thêm so với mục sẵn có)
    first = subprocess.run(["sh", "-c", '. "$1"; echo "$PATH" | cut -d: -f1', "x", str(env_file)], capture_output=True, text=True, timeout=30).stdout.strip()
    assert first.endswith("/shims")


@needs_sh
def test_does_nothing_without_the_env_file_or_when_switched_off_or_without_shims(tmp_path):
    assert run_script(None).returncode == 0
    off = tmp_path / "off.sh"
    assert run_script(off, {"AGENT_AGILE_SHIM": "0"}).returncode == 0 and not off.exists()
    lonely = tmp_path / "scripts"
    lonely.mkdir()
    copy = lonely / "session-env.sh"
    shutil.copy(SCRIPT, copy)
    none = tmp_path / "none.sh"
    assert run_script(none, script=copy).returncode == 0 and not none.exists()  # không có shims/ cạnh script
