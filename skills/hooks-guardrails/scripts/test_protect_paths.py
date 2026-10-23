"""Test cho protect_paths.py — chạy: python -m pytest skills/hooks-guardrails/scripts -q"""

from __future__ import annotations

import argparse
import builtins
import io
import json
import runpy
import subprocess
import sys
import time
from pathlib import Path

import pytest

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


# --- vòng sửa theo review độc lập ---------------------------------------------------------------


@pytest.mark.parametrize("tool", ["write_to_file", "replace_file_content", "multi_replace_file_content"])
def test_antigravity_real_payload_blocked(tool):
    payload = {"toolCall": {"name": tool, "args": {"TargetFile": "C:/repo/.env"}}, "stepIdx": 1}
    rc, out, err = run("antigravity", payload)
    assert rc == 0
    assert json.loads(out) == {"decision": "deny", "reason": "blocked: C:/repo/.env (name:.env)"}


def test_antigravity_real_payload_allowed():
    payload = {"toolCall": {"name": "write_to_file", "args": {"TargetFile": "C:/repo/src/app.py"}}, "stepIdx": 1}
    rc, out, err = run("antigravity", payload)
    assert rc == 0
    assert json.loads(out) == {}


@pytest.mark.parametrize("target, rule", [(".env", "name:.env"), (".secret/a.txt", "segment:.secret")])
def test_codex_patch_move_to_blocked(target, rule):
    patch = "*** Begin Patch\n*** Update File: notes.txt\n*** Move to: " + target + "\n@@\n-a\n+b\n*** End Patch\n"
    rc, out, err = run("codex", {"tool_name": "apply_patch", "tool_input": {"command": patch}})
    assert rc == 2
    assert rule in err


DEEP_LIST = "[" * 2000 + "]" * 2000
DEEP_DICT = '{"a":' * 2000 + "1" + "}" * 2000


@pytest.mark.parametrize("raw", [DEEP_LIST, DEEP_DICT], ids=["list", "dict"])
@pytest.mark.parametrize("fmt", ["claude", "codex"])
def test_deep_json_fails_closed(fmt, raw):
    rc, out, err = run(fmt, raw)
    assert rc == 2
    assert "blocked: bad hook input" in err
    assert out == ""


@pytest.mark.parametrize("raw", [DEEP_LIST, DEEP_DICT], ids=["list", "dict"])
def test_deep_json_antigravity_deny_json(raw):
    rc, out, err = run("antigravity", raw)
    assert rc == 0
    decision = json.loads(out)
    assert decision["decision"] == "deny"
    assert "bad hook input" in decision["reason"]


@pytest.mark.parametrize("error", [MemoryError, RecursionError, RuntimeError])
def test_any_exception_fails_closed(monkeypatch, error):
    def boom(payload):
        raise error("x")

    monkeypatch.setattr(protect_paths, "extract_paths", boom)
    rc, out, err = run("claude", write("src/app.py"))
    assert rc == 2
    assert "blocked: bad hook input" in err
    rc, out, err = run("antigravity", write("src/app.py"))
    assert rc == 0
    assert json.loads(out)["decision"] == "deny"


@pytest.mark.parametrize("fmt", ["claude", "antigravity"])
def test_script_deep_json_never_traceback(fmt):
    """Chạy script thật như harness gọi: JSON lồng sâu không bao giờ thoát 1 hay in traceback."""
    script = str(Path(protect_paths.__file__))
    done = subprocess.run([sys.executable, "-I", script, "--format", fmt], input=DEEP_LIST.encode(),
                          capture_output=True, timeout=30)
    assert "Traceback" not in done.stderr.decode()
    if fmt == "claude":
        assert done.returncode == 2
        assert b"blocked: bad hook input" in done.stderr
    else:
        assert done.returncode == 0
        assert json.loads(done.stdout)["decision"] == "deny"


@pytest.mark.parametrize("name", ["id_rsa", "id_rsa.pub", "server.key"])
def test_default_secret_names_blocked(name):
    rc, out, err = run("claude", write("C:/repo/ssh/" + name))
    assert rc == 2
    assert "blocked: C:/repo/ssh/" + name in err


def test_match_is_case_insensitive():
    rc, out, err = run("claude", write("C:/repo/.ENV"))
    assert rc == 2
    assert "name:.env" in err
    rc, out, err = run("claude", write("C:/repo/.SECRET/x"))
    assert rc == 2
    assert "segment:.secret" in err
    assert run("claude", write("C:/repo/ID_RSA"))[0] == 2
    assert run("claude", write("C:/repo/.GIT/config"))[0] == 2


@pytest.mark.parametrize("path, rule", [
    ("C:/repo/.env ", "name:.env"),
    ("C:/repo/k.pem.", "name:*.pem"),
    ("C:/repo/.env::$DATA", "name:.env"),
    ("C:/repo/.env. .", "name:.env"),
    ("C:/repo/.git./config", "segment:.git"),
    ("C:/repo/.secret /a.txt", "segment:.secret"),
])
def test_windows_name_normalisation_blocked(path, rule):
    rc, out, err = run("claude", write(path))
    assert rc == 2
    assert rule in err


def test_windows_normalisation_keeps_allow_and_posix_colon():
    assert run("claude", write("C:/repo/.env.example "))[0] == 0  # sau chuẩn hoá là .env.example: được phép
    assert run("claude", write("C:/repo/a:b.pem"))[0] == 2  # POSIX: dấu ':' là ký tự thường, tên nguyên văn vẫn khớp *.pem
    assert run("claude", write("C:/repo/a:b.txt"))[0] == 0
    assert run("claude", write("C:/repo/src/app.py"))[0] == 0


def test_many_segments_is_fast():
    """50 000 đoạn đường (~100 KB) phải xong dưới 1 giây, kể cả khi đoạn cuối là .env."""
    filler = "a/" * 50000
    for last, expected in (("x.txt", 0), (".env", 2)):
        started = time.perf_counter()
        rc, out, err = run("claude", write(filler + last))
        elapsed = time.perf_counter() - started
        assert rc == expected
        assert elapsed < 1.0, "mất {:.2f}s".format(elapsed)


def test_glob_with_many_segments_is_capped_and_fast():
    """Có --deny-glob: đường sâu quá giới hạn bị chặn nhanh (không so bậc hai); đường 1000 đoạn vẫn so bình thường."""
    started = time.perf_counter()
    rc, out, err = run("claude", write("a/" * 50000 + "x.txt"), "--deny-glob", "docs/locked/*")
    assert rc == 2
    assert "limit:segments" in err
    rc, out, err = run("claude", write("a/" * 1000 + "x.txt"), "--deny-glob", "docs/locked/*")
    assert rc == 0
    rc, out, err = run("claude", write("docs/locked/" + "a/" * 1000 + "x.txt"), "--deny-glob", "docs/locked/*")
    assert rc == 2
    assert time.perf_counter() - started < 1.0


def test_last_resort_formats(capsys):
    assert protect_paths._last_resort(["--format", "claude"]) == 2
    captured = capsys.readouterr()
    assert "blocked: bad hook input" in captured.err
    assert protect_paths._last_resort(["--format", "antigravity"]) == 0
    assert json.loads(capsys.readouterr().out)["decision"] == "deny"


def test_last_resort_survives_broken_streams(monkeypatch):
    class Broken:
        def write(self, text):
            raise OSError("closed")

    monkeypatch.setattr(sys, "stdout", Broken())
    monkeypatch.setattr(sys, "stderr", Broken())
    assert protect_paths._last_resort(["--format", "claude"]) == 2
    assert protect_paths._last_resort(["--format", "antigravity"]) == 0


def test_main_block_wires_last_resort(monkeypatch):
    """Chạy khối `__main__` thật: lỗi không phải `Exception` (KeyboardInterrupt) thoát main vẫn ra mã chặn."""
    script = str(Path(protect_paths.__file__))

    def interrupted(self, *args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(sys, "argv", [script, "--format", "claude"])
    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", interrupted)
    monkeypatch.setattr(sys, "stderr", io.StringIO())
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(script, run_name="__main__")
    assert exit_info.value.code == 2


def test_main_block_normal_run(monkeypatch):
    script = str(Path(protect_paths.__file__))
    out = io.StringIO()
    monkeypatch.setattr(sys, "argv", [script, "--format", "antigravity"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(write("C:/repo/src/app.py"))))
    monkeypatch.setattr(sys, "stdout", out)
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(script, run_name="__main__")
    assert exit_info.value.code == 0
    assert json.loads(out.getvalue()) == {}
