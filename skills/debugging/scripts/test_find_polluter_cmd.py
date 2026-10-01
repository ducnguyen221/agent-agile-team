"""build_command phải tìm đường đầy đủ của chương trình (npm.cmd trên Windows không chạy được khi không qua shell)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location("find_polluter", Path(__file__).with_name("find_polluter.py"))
fp = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("find_polluter", fp)
_SPEC.loader.exec_module(fp)


def test_program_resolved_through_path(monkeypatch):
    monkeypatch.setattr(fp.shutil, "which", lambda name: r"C:\tools\npm.CMD" if name == "npm" else None)
    assert fp.build_command("npm test -- {file}", "a.test.ts") == [r"C:\tools\npm.CMD", "test", "--", "a.test.ts"]


def test_unknown_program_kept_as_typed(monkeypatch):
    monkeypatch.setattr(fp.shutil, "which", lambda name: None)
    assert fp.build_command("nosuchtool {file}", "t.py") == ["nosuchtool", "t.py"]


def test_real_executable_on_path_is_found(tmp_path, monkeypatch):
    name = "faketool"
    if sys.platform == "win32":
        exe = tmp_path / f"{name}.cmd"
        exe.write_text("@echo off\r\n", encoding="ascii")
    else:
        exe = tmp_path / name
        exe.write_text("#!/bin/sh\n", encoding="ascii")
        exe.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))
    cmd = fp.build_command(f"{name} {{file}}", "t.py")
    assert Path(cmd[0]).resolve() == exe.resolve() and cmd[1:] == ["t.py"]
