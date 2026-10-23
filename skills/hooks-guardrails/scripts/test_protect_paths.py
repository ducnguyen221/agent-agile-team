"""Test cho protect_paths.py — chạy: python -m pytest skills/hooks-guardrails/scripts -q"""

from __future__ import annotations

import builtins
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import protect_paths  # noqa: E402


def run(fmt, payload, *extra):
    """Chạy `main` với payload (dict → JSON, chuỗi → nguyên văn); trả (mã thoát, stdout, stderr)."""
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    out, err = io.StringIO(), io.StringIO()
    rc = protect_paths.main(["--format", fmt, *extra], stdin=io.StringIO(raw), stdout=out, stderr=err)
    return rc, out.getvalue(), err.getvalue()


def write(path):
    return {"tool_name": "Write", "tool_input": {"file_path": path}}


def test_claude_write_env_blocked():
    rc, out, err = run("claude", write("C:\\repo\\.env"))
    assert rc == 2
    assert "blocked: C:/repo/.env (name:.env)" in err
    assert out == ""


def test_env_example_allowed():
    rc, out, err = run("claude", write("C:\\repo\\.env.example"))
    assert rc == 0
    assert err == ""
    assert out == ""


def test_codex_patch_secret_blocked():
    patch = "*** Begin Patch\n*** Update File: .secret/x.txt\n@@\n-a\n+b\n*** End Patch\n"
    rc, out, err = run("codex", {"tool_name": "apply_patch", "tool_input": {"command": patch}})
    assert rc == 2
    assert "segment:.secret" in err


def test_antigravity_deny_json():
    rc, out, err = run("antigravity", {"tool_input": {"file_path": "a/b/key.pem"}})
    assert json.loads(out) == {"decision": "deny", "reason": "blocked: a/b/key.pem (name:*.pem)"}
    assert rc == 0


def test_antigravity_no_match_empty_object():
    rc, out, err = run("antigravity", write("src/app.py"))
    assert json.loads(out) == {}
    assert rc == 0


def test_no_paths_passes():
    assert run("claude", {"tool_name": "Bash", "tool_input": {"command": "ls"}})[0] == 0
    assert run("codex", {})[0] == 0
    rc, out, _ = run("antigravity", {})
    assert rc == 0 and json.loads(out) == {}


def test_bad_json_fails_closed():
    rc, out, err = run("claude", "not json {")
    assert rc == 2
    assert "bad hook input" in err


def test_bad_json_antigravity_deny_json():
    rc, out, err = run("antigravity", "not json {")
    assert json.loads(out) == {"decision": "deny", "reason": "blocked: bad hook input"}
    assert rc == 0


def test_custom_deny_glob():
    rc, out, err = run("claude", write("docs/locked/a.md"), "--deny-glob", "docs/locked/*")
    assert rc == 2
    assert "glob:docs/locked/*" in err
    # đường tuyệt đối vẫn khớp mẫu tương đối
    rc, out, err = run("claude", write("C:\\repo\\docs\\locked\\a.md"), "--deny-glob", "docs/locked/*")
    assert rc == 2
    assert "glob:docs/locked/*" in err
    assert run("claude", write("docs/open/a.md"), "--deny-glob", "docs/locked/*")[0] == 0


def test_custom_allow_name_passes():
    assert run("claude", write("C:/repo/.env.local"))[0] == 2
    rc, out, err = run("claude", write("C:/repo/.env.local"), "--allow-name", ".env.local")
    assert rc == 0
    assert err == ""


def test_git_segment_blocked():
    rc, out, err = run("claude", write("C:/repo/.git/hooks/pre-commit"))
    assert rc == 2
    assert "segment:.git" in err


def test_nested_notebook_path_blocked():
    payload = {"tool_name": "Edit", "tool_input": {"edits": [{"target": {"notebook_path": "nb/.env"}}]}}
    rc, out, err = run("claude", payload)
    assert rc == 2
    assert "blocked: nb/.env (name:.env)" in err


def test_target_file_never_opened(monkeypatch):
    target = "C:/does/not/exist/.env"
    real_open = builtins.open

    def guarded(file, *args, **kwargs):
        if str(file).replace("\\", "/") == target:
            raise AssertionError("script mở file đích")
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded)
    rc, out, err = run("claude", write(target))
    assert rc == 2
    assert "name:.env" in err
