"""Test đột biến của rào (SPR-16 FR3): gỡ rào bằng tám cách trên **bản sao** trong thư mục tạm, bộ test ghim phải đỏ
đúng test được chỉ định; bản sao chưa đột biến phải xanh; đột biến nào sống thì suite này đỏ và nêu mã đột biến.

File này thuộc sàn cứng (`FLOOR_FILES`). Một cơ chế chỉ được gọi là "rào máy" khi đột biến tương ứng ở đây đã đỏ (FR3.3).
Không chạm cây làm việc: mỗi đột biến sửa bản sao, chạy pytest trong tiến trình con ở thư mục bản sao.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import pytest

REPO = Path(__file__).resolve().parent.parent
PINNED_SUITES = ("tests/test_fence_wiring.py", "tests/test_floor_check.py",
                 "tests/test_autopilot_guard.py", "tests/test_autopilot_guard_undo.py", "tests/test_check.py")
KEYWORDS = "fence or floor or marker or autopilot or delegation or push"
IGNORE = shutil.ignore_patterns(".git", ".tmp", ".claude", "__pycache__", ".pytest_cache", "*.pyc", ".env", ".env.*")
WIRING = "tests/test_fence_wiring.py"
UNDO = "tests/test_autopilot_guard_undo.py"


@dataclass
class Mutation:
    apply: Callable[[Path], None]
    must_fail: str  # id (hoặc tiền tố id) của test ghim phải ở trạng thái FAILED
    suites: Optional[tuple] = None  # file test mutant chạy; None = bộ ghim đầy đủ (chỉ các file đang tồn tại)
    needs: Optional[str] = None  # file phải tồn tại ở bản gốc, không thì đột biến skip có lý do


def edit(root: Path, rel: str, old: str, new: str, count: int = 1) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"đột biến không áp được: không thấy {old!r} trong {rel}"
    path.write_bytes(text.replace(old, new, count).encode("utf-8"))


CALL_LINE = "problem = rules.autopilot_problem(block)"


def line_indent(root: Path, rel: str, needle: str) -> str:
    for line in (root / rel).read_text(encoding="utf-8").split("\n"):
        if needle in line:
            return line[:len(line) - len(line.lstrip())]
    raise AssertionError(f"không thấy {needle!r} trong {rel}")


def drop_call(root: Path) -> None:
    edit(root, "scripts/check.py", CALL_LINE, "problem = None")


def drop_result(root: Path) -> None:
    edit(root, "scripts/check.py", CALL_LINE, "rules.autopilot_problem(block)")


def early_return(root: Path) -> None:
    indent = line_indent(root, "scripts/check.py", CALL_LINE)
    edit(root, "scripts/check.py", indent + CALL_LINE, f"{indent}return\n{indent}{CALL_LINE}")


def shadow_def(root: Path) -> None:
    path = root / "scripts" / "_autopilot_rules.py"
    path.write_bytes((path.read_text(encoding="utf-8") + "\n\ndef autopilot_problem(block):\n    return None\n").encode("utf-8"))


def move_marker(root: Path) -> None:
    path = root / "method" / "process.md"
    lines = path.read_text(encoding="utf-8").split("\n")
    end = next(i for i, line in enumerate(lines) if line.strip() == "<!-- san-cung:end -->")
    lines[end], lines[end + 1] = lines[end + 1], lines[end]
    path.write_bytes("\n".join(lines).encode("utf-8"))


def remove_fence_file(root: Path) -> None:
    (root / "scripts" / "autopilot_guard.py").unlink()


def guard_imports_check(root: Path) -> None:
    edit(root, "scripts/autopilot_guard.py", "from _autopilot_rules import AUTOPILOT_EXCLUSIONS",
         "from check import AUTOPILOT_EXCLUSIONS")


def drop_always_blocked(root: Path) -> None:
    """Bỏ `irreversible_delete` khỏi tập bảy mục luôn chặn: guard không còn chặn xoá khi file dấu hợp lệ (thay đột biến cũ trỏ danh sách 13 mục, nay chỉ dùng khi file dấu hỏng)."""
    edit(root, "scripts/_autopilot_rules.py", '"network_fetch", "rules_unlisted", "irreversible_delete", "secret"', '"network_fetch", "rules_unlisted", "secret"')


GUARD = "scripts/autopilot_guard.py"


def stash_all_open(root: Path) -> None:
    edit(root, GUARD, 'if "--all" in rest or any(_cluster(a, "a") for a in rest):', "if False:")


def clean_x_open(root: Path) -> None:
    edit(root, GUARD, 'if forced and any(_cluster(a, "xX") for a in opts):', "if False:")


def ignore_check_inverted(root: Path) -> None:
    edit(root, GUARD, "return None if ctx.marker_ignored() else MARKER", "return MARKER")


def git_dir_delete_open(root: Path) -> None:
    edit(root, GUARD, "if any(_is_git_path(t) for t in targets + [v for _, v in _ps_split(tokens).other]):", "if False:")


def tmp_move_ignored(root: Path) -> None:
    edit(root, GUARD, "        ctx.tmp_moved = True", "        pass")


def pipeline_delete_open(root: Path) -> None:
    edit(root, GUARD, 'item = "irreversible_delete"  # `Get-ChildItem', 'item = None  # `Get-ChildItem')


def reflog_expire_open(root: Path) -> None:
    edit(root, GUARD, 'return "irreversible_delete" if rest[:1] in (["expire"], ["delete"]) else None', "return None")


def push_force_open(root: Path) -> None:
    edit(root, GUARD, 'or a.startswith("--force") or _cluster(a, "fd")', 'or _cluster(a, "fd")')


def branch_big_d_open(root: Path) -> None:
    edit(root, GUARD, 'any(_cluster(a, "D") for a in rest) or (deleting and forced)', "(deleting and forced)")


def session_cap_formula_off(root: Path) -> None:
    edit(root, "scripts/check.py", "cap > formula and not", "cap > 10 ** 9 and not")


def colon_dest_open(root: Path) -> None:
    edit(root, GUARD, 'bucket = parts.dst if canon == "destination" else parts.new', 'bucket = parts.other if canon == "destination" else parts.new')


def named_param_colon_open(root: Path) -> None:
    edit(root, GUARD, 'found = None if token.startswith("--") else _COLON_FLAG.fullmatch(token)', "found = None")


def rename_newname_open(root: Path) -> None:
    edit(root, GUARD, '(parts.new if parts.kind == "rename" else [])', "[]")


def gc_any_expiry_open(root: Path) -> None:
    edit(root, GUARD, 'any(re.fullmatch(r"gc\..*expire\w*", key) for key in config)', 'any(re.fullmatch(r"gc\..*expire\w*", key) and value in ("now", "all", "0") for key, value in config.items())')


def cwd_in_git_open(root: Path) -> None:
    edit(root, GUARD, "self.in_git = _is_git_path(self.cwd)", "self.in_git = False")


def gc_config_open(root: Path) -> None:
    edit(root, GUARD, 'if sub in ("gc", "prune", "reflog", "maintenance") and any(', "if False and any(")


# SPR-20 TK21: sáu đột biến tinh (hợp đồng đích, nhánh được bảo vệ, alias, nhánh đẩy) nhắm mô-đun rào git thường trực và suite của nó;
# hai file đó đã gỡ nên sáu đột biến bỏ theo, còn tám đột biến của dòng nối/vùng sàn/danh sách mục. Đây là gỡ cơ chế, không phải sửa test cho qua kiểm.
MUTATIONS = {
    "drop-call": Mutation(drop_call, f"{WIRING}::test_check_calls_rules_validator", (WIRING,)),
    "drop-result": Mutation(drop_result, f"{WIRING}::test_check_uses_validator_result", (WIRING,)),
    "early-return": Mutation(early_return, f"{WIRING}::test_validator_call_reachable", (WIRING,)),
    "shadow-def": Mutation(shadow_def, f"{WIRING}::test_no_shadowed_definitions", (WIRING,)),
    "move-marker": Mutation(move_marker, f"{WIRING}::test_floor_zone_hashes", (WIRING,)),
    "remove-fence-file": Mutation(remove_fence_file, f"{WIRING}::test_fence_files_exist", (WIRING,)),
    "guard-imports-check": Mutation(guard_imports_check, f"{WIRING}::test_guard_does_not_import_check", (WIRING,)),
    "drop-always-blocked": Mutation(drop_always_blocked, f"{WIRING}::test_fence_wiring_pins_7_plus_6", (WIRING,)),
    # SPR-20 TK27b: mười đột biến phủ rào mới của guard và trần phiên (mỗi cái trúng đúng một test ghim; hằng chết `drop-exclusion` cũ được thay bằng `drop-always-blocked`).
    "stash-all-open": Mutation(stash_all_open, "tests/test_autopilot_guard.py::test_guard_marker_pattern_blocked", ("tests/test_autopilot_guard.py",)),
    "clean-x-open": Mutation(clean_x_open, f"{UNDO}::test_guard_stash_all_and_clean_x_blocked_in_both_ignore_states", (UNDO,)),
    "ignore-check-inverted": Mutation(ignore_check_inverted, f"{UNDO}::test_guard_stash_clean_allowed_when_marker_ignored", (UNDO,)),
    "git-dir-delete-open": Mutation(git_dir_delete_open, f"{UNDO}::test_guard_delete_inside_git_always_blocked", (UNDO,)),
    "tmp-move-ignored": Mutation(tmp_move_ignored, f"{UNDO}::test_guard_move_into_tmp_then_delete_blocked", (UNDO,)),
    "pipeline-delete-open": Mutation(pipeline_delete_open, f"{UNDO}::test_guard_other_recursive_delete_forms_blocked", (UNDO,)),
    "reflog-expire-open": Mutation(reflog_expire_open, f"{UNDO}::test_guard_undo_breaking_git_commands_blocked", (UNDO,)),
    "push-force-open": Mutation(push_force_open, f"{UNDO}::test_guard_undo_breaking_git_commands_blocked", (UNDO,)),
    "branch-big-d-open": Mutation(branch_big_d_open, f"{UNDO}::test_guard_undo_breaking_git_commands_blocked", (UNDO,)),
    # SPR-20 TK27d: ba đột biến phủ dạng dính `-Destination:x`, thư mục làm việc trong `.git`, `git -c gc.*=now`.
    "colon-dest-open": Mutation(colon_dest_open, f"{UNDO}::test_guard_colon_attached_powershell_flags_blocked", (UNDO,)),
    # TK27e: ba đột biến phủ bộ phân tích tham số chung (dạng dính `-Tên:giá-trị`, tên mới là `.git`) và hạn hết hạn bất kỳ của `gc`.
    "named-param-colon-open": Mutation(named_param_colon_open, f"{UNDO}::test_guard_ps_parameter_forms_git_blocked", (UNDO,)),
    "rename-newname-open": Mutation(rename_newname_open, f"{UNDO}::test_guard_ps_parameter_forms_git_blocked", (UNDO,)),
    "gc-any-expiry-open": Mutation(gc_any_expiry_open, f"{UNDO}::test_guard_git_config_zero_expiry_blocked", (UNDO,)),
    "cwd-in-git-open": Mutation(cwd_in_git_open, f"{UNDO}::test_guard_delete_or_move_with_cwd_inside_git_blocked", (UNDO,)),
    "gc-config-open": Mutation(gc_config_open, f"{UNDO}::test_guard_git_config_zero_expiry_blocked", (UNDO,)),
    "session-cap-formula-off": Mutation(session_cap_formula_off, "tests/test_check.py::test_delegation_session_cap_must_not_exceed_the_formula", ("tests/test_check.py",)),
}


def run_pinned_detail(copy_root: Path, suites=None) -> tuple:
    """(id FAILED, id ERROR) khi chạy các file test ghim đang tồn tại trong `copy_root`. Lỗi import/collection là ERROR,
    không bao giờ tính là đã giết đột biến."""
    files = [s for s in (suites or PINNED_SUITES) if (copy_root / s).is_file()]
    assert files, "không có file test ghim nào trong bản sao"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    done = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", *files, "-k", KEYWORDS, "-q", "-rfE", "--tb=no",
                           "-p", "no:cacheprovider"], cwd=copy_root, capture_output=True, text=True, encoding="utf-8", env=env)
    failed, errors = [], []
    for line in done.stdout.splitlines():
        match = re.match(r"^(FAILED|ERROR) (.+?)(?: - .*)?$", line)
        if match:
            (failed if match.group(1) == "FAILED" else errors).append(match.group(2))
    return failed, errors


def run_pinned(copy_root: Path, suites=None) -> list:
    """Danh sách id test ở trạng thái FAILED (lỗi nạp/collection được báo riêng ở `run_pinned_detail`)."""
    return run_pinned_detail(copy_root, suites)[0]


def killed(mutation: Mutation, failed: list) -> bool:
    return any(item == mutation.must_fail or item.startswith(mutation.must_fail + "[") for item in failed)


def require_killed(slug: str, mutation: Mutation, failed: list, errors: list) -> None:
    if not killed(mutation, failed):
        raise AssertionError(f"đột biến sống: {slug} — {mutation.must_fail} không FAILED "
                             f"(FAILED: {failed[:6]}; ERROR: {errors[:6]})")


@pytest.fixture(scope="module")
def pristine(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("pristine") / "repo"
    shutil.copytree(REPO, root, ignore=IGNORE, symlinks=True)
    return root


def fresh_copy(pristine: Path, tmp_path: Path) -> Path:
    root = tmp_path / "mutant"
    shutil.copytree(pristine, root)
    return root


def test_pristine_copy_is_green(pristine):
    failed, errors = run_pinned_detail(pristine)
    assert failed == [] and errors == [], f"bản sao chưa đột biến phải xanh: FAILED {failed[:6]} ERROR {errors[:6]}"


@pytest.mark.parametrize("slug", sorted(MUTATIONS))
def test_mutant_is_killed(slug, pristine, tmp_path):
    mutation = MUTATIONS[slug]
    if mutation.needs and not (REPO / mutation.needs).is_file():
        pytest.skip(f"{mutation.needs} không tồn tại")
    root = fresh_copy(pristine, tmp_path)
    mutation.apply(root)
    failed, errors = run_pinned_detail(root, mutation.suites)
    require_killed(slug, mutation, failed, errors)


def test_surviving_mutant_fails_suite(pristine, tmp_path):
    """FR3.2: vô hiệu đúng một detector (thân test ghim thành `pass`) rồi áp đột biến tương ứng → suite nhận ra đột biến
    sống và nêu slug. Chứng minh cơ chế chứ không chứng minh đột biến khác."""
    root = fresh_copy(pristine, tmp_path)
    edit(root, WIRING, "def test_check_calls_rules_validator():\n    delegation_call()\n",
         "def test_check_calls_rules_validator():\n    pass\n")
    mutation = MUTATIONS["drop-call"]
    mutation.apply(root)
    failed, errors = run_pinned_detail(root, mutation.suites)
    assert not killed(mutation, failed), "detector đã vô hiệu mà vẫn thấy FAILED: cơ chế thử không đáng tin"
    with pytest.raises(AssertionError, match="đột biến sống: drop-call"):
        require_killed("drop-call", mutation, failed, errors)


def test_load_error_is_not_a_kill(pristine, tmp_path):
    """Lỗi nạp/collection không được tính là giết: phá cú pháp file test mục tiêu thì kết quả là ERROR, không FAILED đúng test."""
    root = fresh_copy(pristine, tmp_path)
    edit(root, WIRING, '"""Test ghim dòng nối', "def broken(:\n\"\"\"Test ghim dòng nối")
    mutation = MUTATIONS["drop-call"]
    mutation.apply(root)
    failed, errors = run_pinned_detail(root, mutation.suites)
    assert not killed(mutation, failed) and errors, (failed, errors)
    with pytest.raises(AssertionError, match="đột biến sống"):
        require_killed("drop-call", mutation, failed, errors)


def test_pinned_suites_complete():
    missing = [s for s in PINNED_SUITES if not (REPO / s).is_file()]
    assert not missing, f"bộ ghim thiếu suite: {missing}"
