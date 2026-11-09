"""Test đột biến của rào (SPR-16 FR3): gỡ rào bằng chín cách trên **bản sao** trong thư mục tạm, bộ test ghim phải đỏ
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
PINNED_SUITES = ("tests/test_fence_wiring.py", "tests/test_floor_check.py", "tests/test_git_fence.py",
                 "tests/test_autopilot_guard.py", "tests/test_check.py")
KEYWORDS = "fence or floor or marker or autopilot or delegation or push"
IGNORE = shutil.ignore_patterns(".git", ".tmp", ".claude", "__pycache__", ".pytest_cache", "*.pyc", ".env", ".env.*")
WIRING = "tests/test_fence_wiring.py"


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


def drop_exclusion(root: Path) -> None:
    edit(root, "scripts/_autopilot_rules.py", '("push", "tag",', '("tag",')


def push_allow_all(root: Path) -> None:
    """Nhánh đẩy của `git_fence` luôn trả 'không đụng': chèn `return Verdict()` ngay sau dòng def của `_push_verdict`."""
    path = root / "scripts" / "git_fence.py"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^def _push_verdict\(.*\) -> Verdict:\n", text, re.M)
    assert match, "không thấy _push_verdict trong git_fence.py"
    path.write_bytes((text[:match.end()] + "    return Verdict()\n" + text[match.end():]).encode("utf-8"))


def drop_listed_check(root: Path) -> None:
    """Hợp đồng đích không còn đòi danh tính repo được xác minh bằng danh sách (dấu hiệu 1)."""
    edit(root, "scripts/git_fence.py", "    return (ctx.signals_for(target) if target else sig).listed is True", "    return True")


def drop_targets_check(root: Path) -> None:
    edit(root, "scripts/git_fence.py", '    if dest not in contract["push_targets"]:\n        return "push-target-unknown"', "    pass")


def drop_url_check(root: Path) -> None:
    edit(root, "scripts/git_fence.py", '        return "push-url-mismatch"', "        pass")


def drop_protected_branch_check(root: Path) -> None:
    """`_on_protected_branch` luôn nói 'không phải nhánh được bảo vệ'."""
    path = root / "scripts" / "git_fence.py"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^def _on_protected_branch\(.*\) -> bool:\n", text, re.M)
    assert match, "không thấy _on_protected_branch"
    path.write_bytes((text[:match.end()] + "    return False\n" + text[match.end():]).encode("utf-8"))


def drop_alias_expansion(root: Path) -> None:
    edit(root, "scripts/git_fence.py", "        seg = expand_alias(seg, ctx.cwd)\n", "")


MUTATIONS = {
    "drop-call": Mutation(drop_call, f"{WIRING}::test_check_calls_rules_validator", (WIRING,)),
    "drop-result": Mutation(drop_result, f"{WIRING}::test_check_uses_validator_result", (WIRING,)),
    "early-return": Mutation(early_return, f"{WIRING}::test_validator_call_reachable", (WIRING,)),
    "shadow-def": Mutation(shadow_def, f"{WIRING}::test_no_shadowed_definitions", (WIRING,)),
    "move-marker": Mutation(move_marker, f"{WIRING}::test_floor_zone_hashes", (WIRING,)),
    "remove-fence-file": Mutation(remove_fence_file, f"{WIRING}::test_fence_files_exist", (WIRING,)),
    "guard-imports-check": Mutation(guard_imports_check, f"{WIRING}::test_guard_does_not_import_check", (WIRING,)),
    "drop-exclusion": Mutation(drop_exclusion, f"{WIRING}::test_exclusions_pinned", (WIRING,)),
    # Thêm sau vòng 2 kiểm định (Astra RV7): đột biến tinh trong git_fence.py, mỗi cái đỏ đúng test ghim của hợp đồng/nhánh/alias.
    "drop-listed-check": Mutation(drop_listed_check, "tests/test_git_fence.py::test_contract_needs_the_protected_list_to_name_the_repo",
                                  ("tests/test_git_fence.py",), needs="scripts/git_fence.py"),
    "drop-targets-check": Mutation(drop_targets_check, "tests/test_git_fence.py::test_contract_rejections",
                                   ("tests/test_git_fence.py",), needs="scripts/git_fence.py"),
    "drop-url-check": Mutation(drop_url_check, "tests/test_git_fence.py::test_contract_pushurl_changed_after_writing",
                               ("tests/test_git_fence.py",), needs="scripts/git_fence.py"),
    "drop-protected-branch-check": Mutation(drop_protected_branch_check,
                                            "tests/test_git_fence.py::test_local_history_commands_on_main_are_forbidden_at_full",
                                            ("tests/test_git_fence.py",), needs="scripts/git_fence.py"),
    "drop-alias-expansion": Mutation(drop_alias_expansion, "tests/test_git_fence.py::test_repo_alias_for_push_is_seen",
                                     ("tests/test_git_fence.py",), needs="scripts/git_fence.py"),
    "push-allow-all": Mutation(push_allow_all, "tests/test_git_fence.py::test_push_to_main_without_marker_in_protected_repo",
                               ("tests/test_git_fence.py",), needs="scripts/git_fence.py"),
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
        pytest.skip(f"{mutation.needs} chưa tồn tại; TK8 tạo mô-đun và bỏ skip này")
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


@pytest.mark.skipif(not (REPO / "tests" / "test_git_fence.py").is_file(),
                    reason="test_git_fence.py do TK8 tạo; bật lại khi suite tồn tại")
def test_pinned_suites_complete():
    missing = [s for s in PINNED_SUITES if not (REPO / s).is_file()]
    assert not missing, f"bộ ghim thiếu suite: {missing}"
