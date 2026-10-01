"""Đưa `scripts/` lên `sys.path` và cung cấp tiện ích chạy script như dòng lệnh."""

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SAMPLES = REPO / "samples"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def run_script(name: str, *args: str, env: dict | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Chạy `scripts/<name>` bằng tiến trình con, trả kết quả có stdout/stderr dạng UTF-8."""
    full_env = dict(os.environ)
    full_env["PYTHONIOENCODING"] = "utf-8"
    if env is not None:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=full_env,
        cwd=str(cwd or REPO),
        stdin=subprocess.DEVNULL,
        timeout=120,
    )
