"""`scripts/floor_check.py` (SPR-16 FR2): so sàn cứng với bản base trên repo thử trong `tmp_path`.

File này thuộc sàn cứng (`FLOOR_FILES`). Mỗi ca dựng repo thử (`git init`, commit base rồi commit head) và chạy
`floor_check.py` của **repo này** với `--root <repo thử>`, đúng như bước CI chạy bản của base trên cây của head.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "floor_check.py"
WORKFLOW = REPO / ".github" / "workflows" / "verify.yml"
ZONE_FILES = ("AGENTS.md", "method/process.md", "method/sizing.md", "method/autopilot.md")

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="không có lệnh git")


def _bash_works() -> bool:
    """`bash` trong PATH chạy được một lệnh thật? (trên Windows, `bash.exe` của WindowsApps là stub WSL không dùng được.)"""
    exe = shutil.which("bash")
    if exe is None:
        return False
    try:
        done = subprocess.run([exe, "-c", "echo ok"], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0 and done.stdout.strip() == "ok"


BASH_EXE = shutil.which("bash")  # đường dẫn đã thử chạy ở trên; không gọi tên trần (Windows tìm bash.exe WSL của System32 trước PATH)
BASH_OK = _bash_works()


def git(root: Path, *args: str) -> str:
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_SYSTEM=os.devnull)
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8", env=env)
    assert done.returncode == 0, f"git {' '.join(args)}: {done.stderr}"
    return done.stdout.strip()


def commit(root: Path, message: str) -> str:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD")


def put(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


@pytest.fixture
def lab(tmp_path):
    """Repo thử: bốn file có mốc (chép nguyên từ repo này), vài file sàn, một tệp thường."""
    root = tmp_path / "lab"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    for rel in ZONE_FILES:
        put(root, rel, (REPO / rel).read_text(encoding="utf-8"))
    for rel in ("scripts/autopilot_guard.py", "scripts/floor_check.py", "hooks/hooks.json", ".github/workflows/verify.yml"):
        put(root, rel, f"# {rel}\n")
    put(root, "README.md", "# lab\n")
    base = commit(root, "base")
    return root, base


def run(root: Path, base: str, *extra: str, head: str = "HEAD"):
    done = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), "--root", str(root), "--base", base,
                           "--head", head, *extra], capture_output=True, text=True, encoding="utf-8")
    return done.returncode, done.stdout + done.stderr


def edit(root: Path, rel: str, old: str, new: str) -> None:
    text = (root / rel).read_text(encoding="utf-8")
    assert old in text
    put(root, rel, text.replace(old, new, 1))


def zone_line(root: Path, rel: str, which: int = 0) -> str:
    """Một dòng chữ nằm giữa cặp mốc thứ `which` của `rel`."""
    lines = (root / rel).read_text(encoding="utf-8").split("\n")
    starts = [i for i, l in enumerate(lines) if l.strip() == "<!-- san-cung:start -->"]
    return lines[starts[which] + 1]


def test_no_floor_change_passes(lab):
    root, base = lab
    put(root, "README.md", "# lab đổi\n")
    edit(root, "AGENTS.md", "# agent-agile-team — luật lõi", "# agent-agile-team — luật lõi (ngoài vùng sàn)")
    commit(root, "head")
    code, out = run(root, base)
    assert code == 0, out
    assert "floor-" not in out


def test_zone_text_changed_is_flagged(lab):
    root, base = lab
    line = zone_line(root, "method/autopilot.md")
    edit(root, "method/autopilot.md", line, line + " (đã sửa)")
    commit(root, "head")
    code, out = run(root, base)
    assert code == 1 and "floor-zone-changed method/autopilot.md" in out, out


def test_moved_end_marker_is_flagged(lab):
    root, base = lab
    text = (root / "method/process.md").read_text(encoding="utf-8").split("\n")
    end = next(i for i, l in enumerate(text) if l.strip() == "<!-- san-cung:end -->")
    text[end], text[end + 1] = text[end + 1], text[end]
    put(root, "method/process.md", "\n".join(text))
    commit(root, "head")
    code, out = run(root, base)
    assert code == 1 and "floor-marker-moved method/process.md" in out, out


def test_marker_removed_is_flagged(lab):
    root, base = lab
    edit(root, "method/sizing.md", "<!-- san-cung:start -->\n", "")
    commit(root, "head")
    code, out = run(root, base)
    assert code == 1 and "floor-marker-moved method/sizing.md" in out, out


def test_floor_file_removed_renamed_added_changed(lab):
    root, base = lab
    git(root, "mv", "scripts/autopilot_guard.py", "scripts/guard_renamed.py")
    put(root, "hooks/hooks.json", "# hooks đã sửa\n")
    put(root, "scripts/merge_ready.py", "# mới\n")
    (root / ".github/workflows/verify.yml").unlink()
    commit(root, "head")
    code, out = run(root, base)
    assert code == 1, out
    for expected in ("floor-file-renamed scripts/autopilot_guard.py", "floor-file-changed hooks/hooks.json",
                     "floor-file-added scripts/merge_ready.py", "floor-file-removed .github/workflows/verify.yml"):
        assert expected in out, out


def test_floor_file_without_marker_changed(lab):
    root, base = lab
    put(root, "scripts/floor_check.py", "# khác hẳn\n")
    commit(root, "head")
    code, out = run(root, base)
    assert code == 1 and "floor-file-changed scripts/floor_check.py" in out, out


def test_report_mode_lists_and_exits_zero(lab):
    root, base = lab
    line = zone_line(root, "AGENTS.md")
    edit(root, "AGENTS.md", line, line + " (sửa)")
    put(root, "hooks/hooks.json", "# hooks đã sửa\n")
    commit(root, "head")
    code, out = run(root, base, "--mode", "report")
    assert code == 0, out
    assert "floor-changed" in out and "cần Đức xác nhận ở Cổng 2" in out
    assert "floor-zone-changed AGENTS.md" in out and "floor-file-changed hooks/hooks.json" in out


def test_json_output(lab):
    root, base = lab
    put(root, "hooks/hooks.json", "# hooks đã sửa\n")
    commit(root, "head")
    code, out = run(root, base, "--json")
    assert code == 1
    import json
    data = json.loads(out)
    assert data["status"] == "violations" and data["violations"][0]["code"] == "floor-file-changed"


def test_base_without_script_is_bootstrap(lab):
    root, _ = lab
    git(root, "rm", "-q", "scripts/floor_check.py")
    base = commit(root, "base2 không có floor_check")
    put(root, "scripts/floor_check.py", "# mới\n")
    put(root, "hooks/hooks.json", "# hooks đã sửa\n")
    commit(root, "head")
    code, out = run(root, base)
    assert code == 0 and "bootstrap — chưa kiểm so base" in out, out


def test_base_without_markers_is_bootstrap(tmp_path):
    root = tmp_path / "bare"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    put(root, "scripts/floor_check.py", "# x\n")
    put(root, "AGENTS.md", "# không mốc\n")
    base = commit(root, "base")
    put(root, "AGENTS.md", "# không mốc, đổi\n")
    commit(root, "head")
    code, out = run(root, base)
    assert code == 0 and "bootstrap" in out, out


def test_bad_ref_is_usage_error(lab):
    root, _ = lab
    code, out = run(root, "khong-co-ref")
    assert code == 2, out


def test_script_runs_from_a_foreign_directory(lab, tmp_path):
    """Bản chạy không nằm trong cây của head: sao `scripts/` sang chỗ khác vẫn chạy được (điều kiện của bước CI)."""
    root, base = lab
    put(root, "hooks/hooks.json", "# hooks đã sửa\n")
    commit(root, "head")
    copy = tmp_path / "base-scripts"
    shutil.copytree(REPO / "scripts", copy)
    done = subprocess.run([sys.executable, "-X", "utf8", str(copy / "floor_check.py"), "--root", str(root),
                           "--base", base], capture_output=True, text=True, encoding="utf-8")
    assert done.returncode == 1 and "floor-file-changed hooks/hooks.json" in done.stdout


# --- bước CI trong verify.yml ------------------------------------------------------------------------------------

def ci_step_script() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(r"- name: Floor vs base[^\n]*\n(?P<body>(?:[ ]{6,}[^\n]*\n|\n)+)", text)
    assert match, "verify.yml thiếu bước 'Floor vs base'"
    body = match.group("body")
    run_at = body.index("run: |\n") + len("run: |\n")
    lines = body[run_at:].split("\n")
    indent = len(lines[0]) - len(lines[0].lstrip())
    return "\n".join(line[indent:] for line in lines)


@pytest.mark.skipif(not BASH_OK, reason="không có bash chạy được (WSL stub của Windows không tính)")
def test_ci_step_runs_base_script_not_head_script(lab, tmp_path):
    root, _ = lab
    # base có bản floor_check.py thật; head thay bằng script độc hại in PWNED
    put(root, "scripts/floor_check.py", SCRIPT.read_text(encoding="utf-8"))
    put(root, "scripts/_autopilot_rules.py", (REPO / "scripts" / "_autopilot_rules.py").read_text(encoding="utf-8"))
    commit(root, "base thật")
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(root), str(origin)], check=True)
    git(root, "remote", "add", "origin", str(origin))
    put(root, "scripts/floor_check.py", "print('PWNED')\n")
    put(root, "hooks/hooks.json", "# hooks đã sửa\n")
    commit(root, "head độc hại")
    env = dict(os.environ, BASE_REF="main", FLOOR_MODE="strict", PYTHONIOENCODING="utf-8", GH_TOKEN="x",
               PYTHON=sys.executable.replace("\\", "/"), RUNNER_TEMP=str(tmp_path / "tmp").replace("\\", "/"))
    (tmp_path / "tmp").mkdir()
    done = subprocess.run([BASH_EXE, "-c", ci_step_script()], cwd=root, capture_output=True, text=True,
                          encoding="utf-8", env=env)
    out = done.stdout + done.stderr
    assert "PWNED" not in out, out
    assert done.returncode == 1 and "floor-file-changed hooks/hooks.json" in out, out


@pytest.mark.skipif(not BASH_OK, reason="không có bash chạy được (WSL stub của Windows không tính)")
def test_ci_step_reports_bootstrap_when_base_lacks_script(lab, tmp_path):
    root, _ = lab
    git(root, "rm", "-q", "scripts/floor_check.py")
    commit(root, "base không script")
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(root), str(origin)], check=True)
    git(root, "remote", "add", "origin", str(origin))
    put(root, "scripts/floor_check.py", "print('PWNED')\n")
    commit(root, "head")
    env = dict(os.environ, BASE_REF="main", FLOOR_MODE="strict", PYTHONIOENCODING="utf-8", GH_TOKEN="x",
               PYTHON=sys.executable.replace("\\", "/"), RUNNER_TEMP=str(tmp_path / "tmp").replace("\\", "/"))
    (tmp_path / "tmp").mkdir()
    done = subprocess.run([BASH_EXE, "-c", ci_step_script()], cwd=root, capture_output=True, text=True,
                          encoding="utf-8", env=env)
    out = done.stdout + done.stderr
    assert done.returncode == 0 and "bootstrap — chưa kiểm so base" in out and "PWNED" not in out, out


def test_workflow_step_only_on_pull_request():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "if: github.event_name == 'pull_request'" in text
    assert "floor-approved" in text and "git archive" in text


# --- gọi trong tiến trình (để đo coverage của floor_check.main; hành vi đã kiểm bằng tiến trình con ở trên) --------------

def in_process(root, base, *extra, head="HEAD"):
    sys.path.insert(0, str(REPO / "scripts"))
    import floor_check
    import io
    import contextlib
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = floor_check.main(["--root", str(root), "--base", base, "--head", head, *extra])
    return code, out.getvalue()


def test_in_process_strict_report_json_and_errors(lab):
    root, base = lab
    line = zone_line(root, "method/sizing.md")
    edit(root, "method/sizing.md", line, line + " (đã sửa)")
    put(root, "hooks/hooks.json", "# hooks đã sửa\n")
    git(root, "mv", "scripts/autopilot_guard.py", "scripts/g2.py")
    put(root, "scripts/merge_ready.py", "# mới\n")
    (root / ".github/workflows/verify.yml").unlink()
    commit(root, "head")
    code, out = in_process(root, base)
    assert code == 1
    for expected in ("floor-zone-changed method/sizing.md", "floor-file-changed hooks/hooks.json", "floor-file-renamed",
                     "floor-file-added scripts/merge_ready.py", "floor-file-removed .github/workflows/verify.yml"):
        assert expected in out, out
    code, out = in_process(root, base, "--mode", "report")
    assert code == 0 and "floor-changed — cần Đức xác nhận ở Cổng 2" in out
    code, out = in_process(root, base, "--json")
    assert code == 1 and '"status": "violations"' in out
    assert in_process(root, "khong-co-ref")[0] == 2
    assert in_process(root, base, head=base)[0] == 0


def test_in_process_marker_problems_and_bootstrap(lab, tmp_path):
    root, base = lab
    text = (root / "AGENTS.md").read_text(encoding="utf-8")
    put(root, "AGENTS.md", text.replace("<!-- san-cung:start -->\n", "", 1))
    commit(root, "mất một mốc")
    code, out = in_process(root, base)
    assert code == 1 and "floor-marker-moved AGENTS.md" in out
    git(root, "rm", "-q", "method/process.md")
    commit(root, "xoá file có vùng")
    code, out = in_process(root, base)
    assert "floor-zone-changed method/process.md" in out
    bare = tmp_path / "bare"
    bare.mkdir()
    git(bare, "init", "-q", "-b", "main")
    put(bare, "x.txt", "x")
    first = commit(bare, "a")
    put(bare, "x.txt", "y")
    commit(bare, "b")
    code, out = in_process(bare, first)
    assert code == 0 and "bootstrap" in out


def test_workflow_floor_step_runs_before_any_head_code():
    """Bảo mật SC4: bước 'Floor vs base' đứng trước mọi bước chạy mã của head (Tests, check --self), để head không đầu độc môi trường trước đó."""
    text = WORKFLOW.read_text(encoding="utf-8")
    floor = text.index("name: Floor vs base")
    for later in ("name: Install test runner", "name: Tests", "name: Core is clean", "name: Samples and templates"):
        assert floor < text.index(later), later


def test_workflow_floor_step_does_not_call_a_bare_tar():
    """SPR-18/TK3c: trên runner Windows `tar` trần là tar của hệ điều hành, không đọc được luồng của `git archive` ('Error is not recoverable'); dùng GNU tar của Git."""
    text = WORKFLOW.read_text(encoding="utf-8")
    step = text[text.index("name: Floor vs base"):]
    step = step[:step.index("floor_check.py")]
    assert "/usr/bin/tar -x" in step and "| tar " not in step
    # GNU tar đọc `D:` trong `-C "D:\a\_temp/..."` là máy từ xa (Windows runner): không đưa đường Windows cho `-C`, vào thư mục bằng `cd` trong subshell.
    assert "tar -x -C" not in step and '(cd "$base_dir" && /usr/bin/tar -x)' in step


def test_ci_step_tests_call_the_bash_that_which_resolved():
    """SPR-18/TK3b: gọi `bash` trần trên Windows CI ra stub WSL của System32 dù `_bash_works` đã thử Git Bash — phải dùng đường dẫn which."""
    source = Path(__file__).read_text(encoding="utf-8")
    bare = 'subprocess.run(["bash", ' + '"-c", ci_step_script()]'  # ghép chuỗi để dòng này không tự khớp
    assert bare not in source
