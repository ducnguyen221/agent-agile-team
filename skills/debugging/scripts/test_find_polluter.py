"""Test cho find_polluter.py — chạy: python -m pytest skills/debugging/scripts -q"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("find_polluter.py")


def run(args, cwd):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8", timeout=120)


def make_tests(root: Path, polluter: str | None) -> None:
    sub = root / "tests" / "deep"
    sub.mkdir(parents=True)
    for name in ("test_a.py", "test_b.py"):
        (root / "tests" / name).write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (sub / "test_c.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    if polluter:
        (root / polluter).write_text(
            "from pathlib import Path\n\ndef test_dirty():\n    Path('junk.txt').write_text('x')\n",
            encoding="utf-8")


def test_finds_the_test_that_creates_the_file(tmp_path):
    make_tests(tmp_path, "tests/deep/test_dirty.py")
    result = run(["--check", "junk.txt", "--glob", "tests/**/test_*.py"], tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "test_dirty.py" in result.stdout
    assert "test_a.py" not in result.stdout.split("FOUND")[-1]


def test_clean_suite_exits_zero(tmp_path):
    make_tests(tmp_path, None)
    result = run(["--check", "junk.txt", "--glob", "tests/**/test_*.py"], tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    # chạy đủ 3 file, kể cả file ở thư mục con (** khớp cả 0 tầng lẫn nhiều tầng)
    assert "/3] tests/deep/test_c.py" in result.stdout
    assert "/3] tests/test_a.py" in result.stdout


def test_existing_pollution_is_a_usage_error(tmp_path):
    make_tests(tmp_path, None)
    (tmp_path / "junk.txt").write_text("already here", encoding="utf-8")
    result = run(["--check", "junk.txt", "--glob", "tests/**/test_*.py"], tmp_path)
    assert result.returncode == 2


def test_custom_command_template_receives_each_file(tmp_path):
    make_tests(tmp_path, None)
    cmd = f'"{sys.executable}" -c "import sys, pathlib; pathlib.Path(\'seen.log\').open(\'a\').write(sys.argv[1] + chr(10))" {{file}}'
    result = run(["--check", "junk.txt", "--glob", "tests/*.py", "--cmd", cmd], tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    seen = (tmp_path / "seen.log").read_text(encoding="utf-8").split()
    assert sorted(Path(s).name for s in seen) == ["test_a.py", "test_b.py"]


def test_no_matching_files_is_a_usage_error(tmp_path):
    result = run(["--check", "junk.txt", "--glob", "nothing/**/*.py"], tmp_path)
    assert result.returncode == 2
