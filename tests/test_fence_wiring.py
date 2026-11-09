"""Test ghim dòng nối của rào autopilot (SPR-16 TK2): hằng và validator nằm ở `scripts/_autopilot_rules.py`,
`check.py` gọi đúng một lần và dùng kết quả, guard không nhập gì từ `check`.

File này thuộc sàn cứng (`FLOOR_FILES`). Nó kiểm bằng đọc văn bản và cây AST, **không nhập** `check` hay
`autopilot_guard`, để test đột biến xoá hay phá một file không biến assertion thành lỗi nạp test.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
RULES = SCRIPTS / "_autopilot_rules.py"
CHECK = SCRIPTS / "check.py"
GUARD = SCRIPTS / "autopilot_guard.py"
GIT_FENCE = SCRIPTS / "git_fence.py"

# Bản ghim viết tay: mỗi lần danh sách đổi, đổi cả chỗ này trong cùng commit và nêu lý do ở thông điệp commit.
PINNED_FENCE_FILES = (
    "method/autopilot.md",
    "skills/intake/references/autopilot.md",
    "skills/running-sprint/references/autopilot.md",
    "skills/closing-sprint/references/autopilot.md",
    "scripts/_autopilot_rules.py",
    "scripts/autopilot_guard.py",
    "scripts/autopilot-hook.sh",
    "hooks/hooks.json",
)
PINNED_EXCLUSIONS = {"push", "tag", "version", "main_merge", "publish", "license", "irreversible_delete",
                     "rules_unlisted", "user_soul", "secret", "auth", "network_fetch", "branch_merge_local"}
PINNED_NAMES = ("DELEGATION_KEYS", "DELEGATION_OPTIONAL_KEYS", "AUTOPILOT_PREFIX", "AUTOPILOT_LEVELS",
                "AUTOPILOT_EXCLUSIONS", "AUTOPILOT_GATES_BOTH", "AUTOPILOT_BRANCH_SUFFIX", "DELEGATION_CHANNELS",
                "DATE", "MOMENT", "parse_moment", "autopilot_problem", "FENCE_FILES")


def parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def module_bindings(tree: ast.Module) -> dict[str, list[ast.AST]]:
    """Mọi chỗ gắn tên ở **phạm vi module** (kể cả trong if/try/with), không đi vào thân hàm hay lớp."""
    found: dict[str, list[ast.AST]] = {}

    def add(name: str, node: ast.AST) -> None:
        found.setdefault(name, []).append(node)

    def walk(nodes) -> None:
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                add(node.name, node)
                continue
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    for sub in ast.walk(target):
                        if isinstance(sub, ast.Name):
                            add(sub.id, node)
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign)) and isinstance(node.target, ast.Name):
                add(node.target.id, node)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    add((alias.asname or alias.name).split(".")[0], node)
            for field in ("body", "orelse", "finalbody"):
                inner = getattr(node, field, None)
                if isinstance(inner, list):
                    walk(inner)
            for handler in getattr(node, "handlers", []) or []:
                walk(handler.body)

    walk(tree.body)
    return found


def rules_constant(name: str):
    """Giá trị literal của hằng module `name` trong `_autopilot_rules.py`, đọc bằng AST (không nhập module)."""
    nodes = module_bindings(parse(RULES)).get(name, [])
    if not nodes:
        raise AssertionError(f"fence-def-shadowed: {name} không có trong _autopilot_rules.py")
    node = nodes[-1]
    value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
    return ast.literal_eval(value)


def validator_calls(tree: ast.Module) -> list[tuple[ast.Call, ast.AST | None]]:
    """Mọi `Call` tới `rules.autopilot_problem` kèm hàm chứa nó."""
    out = []
    for func in ast.walk(tree):
        if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(func):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "autopilot_problem"
                        and isinstance(node.func.value, ast.Name) and node.func.value.id == "rules"):
                    out.append((node, func))
    # `ast.walk` lặp một lời gọi lồng nhiều hàm: giữ hàm trong cùng nhất (xuất hiện cuối)
    unique: dict[int, tuple[ast.Call, ast.AST]] = {}
    for call, func in out:
        unique[id(call)] = (call, func)
    return list(unique.values())


def delegation_call():
    tree = parse(CHECK)
    calls = validator_calls(tree)
    assert len(calls) == 1, (f"fence-call-missing: cần đúng một lời gọi rules.autopilot_problem trong check.py, "
                             f"có {len(calls)}")
    call, func = calls[0]
    assert func.name == "_delegation", f"fence-call-missing: lời gọi nằm ở {func.name}, không phải _delegation"
    return tree, call, func


def statement_list_with(func: ast.AST, call: ast.Call) -> tuple[list[ast.stmt], int]:
    """Danh sách lệnh (cùng nhánh) chứa câu lệnh mang lời gọi, và chỉ số của nó."""
    for node in ast.walk(func):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if isinstance(stmts, list):
                for index, stmt in enumerate(stmts):
                    if any(sub is call for sub in ast.walk(stmt)) and not isinstance(
                            stmt, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                        return stmts, index
    raise AssertionError("fence-call-missing: không tìm thấy câu lệnh mang lời gọi")


# --- FR1.2/FR1.3: dòng nối ---------------------------------------------------------------------------------------

def test_check_calls_rules_validator():
    delegation_call()


def test_check_uses_validator_result():
    _, call, func = delegation_call()
    stmts, index = statement_list_with(func, call)
    stmt = stmts[index]
    assert (isinstance(stmt, ast.Assign) and stmt.value is call and len(stmt.targets) == 1
            and isinstance(stmt.targets[0], ast.Name)), "fence-result-unused: kết quả lời gọi không được gán vào một tên"
    name = stmt.targets[0].id
    used = False
    for later in stmts[index + 1:index + 3]:
        if isinstance(later, ast.If) and isinstance(later.test, ast.Compare):
            test = later.test
            if (isinstance(test.left, ast.Name) and test.left.id == name and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.IsNot) and isinstance(test.comparators[0], ast.Constant)
                    and test.comparators[0].value is None
                    and any(isinstance(n, ast.Name) and n.id == name for b in later.body for n in ast.walk(b))):
                used = True
    assert used, f"fence-result-unused: sau lời gọi phải có `if {name} is not None:` dùng {name}"


def test_validator_call_reachable():
    _, call, func = delegation_call()
    stmts, index = statement_list_with(func, call)
    for earlier in stmts[:index]:
        assert not isinstance(earlier, (ast.Return, ast.Raise, ast.Continue, ast.Break)), (
            f"fence-call-unreachable: có {type(earlier).__name__} ở dòng {earlier.lineno} trước lời gọi trong cùng nhánh")


# --- FR1.2/FR1.4: mô-đun rào ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", PINNED_NAMES)
def test_no_shadowed_definitions(name):
    nodes = module_bindings(parse(RULES)).get(name, [])
    assert len(nodes) == 1, (f"fence-def-shadowed: {name} có {len(nodes)} chỗ gắn tên trong _autopilot_rules.py "
                             f"(cần đúng 1, không định nghĩa lại sau)")


def test_validator_is_a_function_taking_block():
    node = module_bindings(parse(RULES))["autopilot_problem"][0]
    assert isinstance(node, ast.FunctionDef) and [a.arg for a in node.args.args] == ["block"]


@pytest.mark.parametrize("path", [GUARD, GIT_FENCE], ids=lambda p: p.name)
def test_guard_does_not_import_check(path):
    if not path.exists():
        pytest.skip(f"{path.name} chưa tồn tại ở thời điểm này")
    for node in ast.walk(parse(path)):
        if isinstance(node, ast.Import):
            assert all(a.name.split(".")[0] != "check" for a in node.names), (
                f"fence-import-from-check: {path.name}:{node.lineno} nhập check")
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] != "check", (
                f"fence-import-from-check: {path.name}:{node.lineno} nhập từ check")


def test_guard_imports_exclusions_from_rules():
    imported = [n for n in ast.walk(parse(GUARD)) if isinstance(n, ast.ImportFrom) and n.module == "_autopilot_rules"]
    names = {a.name for n in imported for a in n.names}
    assert "AUTOPILOT_EXCLUSIONS" in names, "fence-import-from-check: guard phải nhập AUTOPILOT_EXCLUSIONS từ _autopilot_rules"


def test_check_imports_rules():
    tree = parse(CHECK)
    assert any(isinstance(n, ast.Import) and any(a.name == "_autopilot_rules" and a.asname == "rules" for a in n.names)
               for n in ast.walk(tree)), "fence-call-missing: check.py phải có `import _autopilot_rules as rules`"


# --- FR1.1: danh sách file rào -----------------------------------------------------------------------------------

def test_fence_files_pinned():
    assert tuple(rules_constant("FENCE_FILES")) == PINNED_FENCE_FILES, (
        "fence-files-changed: FENCE_FILES khác bản ghim viết tay; đổi cả hai trong cùng commit, có lý do")


def test_fence_files_exist():
    missing = [f for f in rules_constant("FENCE_FILES") if not (REPO / f).is_file()]
    assert not missing, f"fence-file-missing: {', '.join(missing)}"


def test_exclusions_pinned():
    values = rules_constant("AUTOPILOT_EXCLUSIONS")
    assert len(values) == 13 and len(set(values)) == 13 and set(values) == PINNED_EXCLUSIONS, (
        f"fence-exclusions-changed: AUTOPILOT_EXCLUSIONS khác 13 mục ghim ({sorted(set(values) ^ PINNED_EXCLUSIONS)})")
