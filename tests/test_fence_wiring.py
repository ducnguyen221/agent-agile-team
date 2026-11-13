"""Test ghim dòng nối của rào autopilot (SPR-16 TK2): hằng và validator nằm ở `scripts/_autopilot_rules.py`,
`check.py` gọi đúng một lần và dùng kết quả, guard không nhập gì từ `check`.

File này thuộc sàn cứng (`FLOOR_FILES`). Nó kiểm bằng đọc văn bản và cây AST, **không nhập** `check` hay
`autopilot_guard`, để test đột biến xoá hay phá một file không biến assertion thành lỗi nạp test.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
RULES = SCRIPTS / "_autopilot_rules.py"
CHECK = SCRIPTS / "check.py"
GUARD = SCRIPTS / "autopilot_guard.py"

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
PINNED_NAMES = ("DELEGATION_KEYS", "DELEGATION_OPTIONAL_KEYS", "AUTOPILOT_PREFIX", "AUTOPILOT_LEVELS", "AUTOPILOT_PUSH_FLAG",
                "AUTOPILOT_EXCLUSIONS", "AUTOPILOT_GATES_BOTH", "AUTOPILOT_BRANCH_SUFFIX", "DELEGATION_CHANNELS",
                "DATE", "MOMENT", "parse_moment", "autopilot_problem", "FENCE_FILES",
                "FLOOR_ZONES", "FLOOR_FILES", "FLOOR_MARKER_START", "FLOOR_MARKER_END", "zone_spans")


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
    return _evaluate(value)


def _evaluate(node):
    """`ast.literal_eval` mở rộng cho tên hằng đã định nghĩa ở module và phép `+` giữa các tuple."""
    if isinstance(node, ast.Name):
        return rules_constant(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _evaluate(node.left) + _evaluate(node.right)
    return ast.literal_eval(node)


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


@pytest.mark.parametrize("path", [GUARD], ids=lambda p: p.name)
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


# --- FR2.1: vùng sàn cứng ------------------------------------------------------------------------------------------

PINNED_FLOOR_ZONES = {"AGENTS.md": 2, "method/process.md": 3, "method/sizing.md": 1, "method/autopilot.md": 1}
PINNED_FLOOR_FILES_EXTRA = (
    "scripts/floor_check.py", "scripts/merge_ready.py", "scripts/deploy_scan.py", "tests/test_fence_wiring.py",
    "tests/test_floor_check.py", "tests/test_mutation_floor.py",
    ".github/workflows/verify.yml",
)
# (đường file, số thứ tự cặp mốc) → (SHA-256 của chữ giữa mốc, SHA-256 của hai dòng chữ gần nhất quanh cặp mốc).
# Sửa chữ trong vùng sàn thì đổi cả băm ở đây trong cùng commit, có lý do và có 5 ý Đức gật cho file luật đó.
PINNED_ZONE_HASHES = {
    ("AGENTS.md", 0): (
        "4f3b98a6913e0d5ef2bd16832c3c86da0c41959cc3b8721758a15692b6527a15",  # TK27b: Gate Delegate không quyết thay ở (a), (b), bảy mục luôn chặn (Sec RF1)
        "1b674c5981eda2acbc3b340bec29f1730fce0513d8061f11383ce0d60d4a3f4c"),
    ("AGENTS.md", 1): (
        "f6c45f132903c33cf32a4e5434829f2afc35d127e807f1c5db6ef7bd87bcfb47",  # TK27b: lệnh phá hoàn tác + đẩy chỉ khi có lời cấp, kiểm ruleset, quét secret (Sec RF3, RF4)
        "5d18f5eaed17becce2a26b0381cb1a0576ec05b6d3d5948bcef94a80abe411bf"),
    ("method/process.md", 0): (
        "49b0eba555d5560aa81f72079e3f0bf012065b94185f8b38a4a7bb18c20f084b",  # SPR-20 TK8: Khuyến nghị có sẵn khi autopilot bật + câu mẫu `Mở SPR-NN` (vùng sàn đã duyệt ở PLAN); TK27b: lời cấp thật trích nguyên văn từ chat, câu mẫu chỉ là ví dụ (QA lệch 1)
        "ecb48ff6109d5b11438be3eef55f7e9c5d7af45c98a2cf48cf4dea2efc4f1029"),
    ("method/process.md", 1): (
        "46c568486b7986e0f7ec30197687361aaa199067688b25ead162163cd97051ec",  # TK27b: điều kiện dừng (a), (b) vào "Việc cần người" (Sec RF1)
        "2a61b772d7d11e70c57623ef3447b2dc001d4218b8c2aaa09c181ac31d436c5f"),
    ("method/process.md", 2): (
        "a4d227e219acf81466e07c74745e0dee15f9e82a48e34b41030c3abdeb028cd2",
        "b7c7fe0fbd1a77eb08490351e6fe3812eefdec315cb73a9df8fa00de8148ce6a"),
    ("method/sizing.md", 0): (
        "dc327e76921c81fcf4266a5285b617b74cb55af89e71eca950067b4d9018acba",
        "47c90f9685ed7aecfe4ca66bc4e10a217a68813484e3d1eb920f085e292b85d3"),
    ("method/autopilot.md", 0): (
        "e48cc18d121cdf721b76c108b367ff670c2ac26ba65cb21dfc904bce402773dc",  # TK7 (DN3 a): hàng `push` mục 5 thêm "trừ đúng hợp đồng đích"; TK27b (đã thay hàng `push` cũ ở TK21): bảy mục luôn chặn, mẫu hook mới, lệnh phá hoàn tác, đẩy chỉ khi có lời cấp (Sec RF1-RF4)
        "55283740743d60f43bb66242f9133c4ff732b4617fe81bdf07ad8ad37098fc56"),
}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _spans(text: str) -> list[tuple[int, int]]:
    """Cặp mốc bằng đọc văn bản (không nhập module rào): dòng mốc mở/đóng, đánh số từ 1."""
    out, opened = [], 0
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.strip()
        if line == "<!-- san-cung:start -->":
            assert not opened, f"fence-zone-nested: dòng {number}"
            opened = number
        elif line == "<!-- san-cung:end -->":
            assert opened, f"fence-zone-unbalanced: dòng {number}"
            out.append((opened, number))
            opened = 0
    assert not opened, "fence-zone-unbalanced: mốc mở không đóng"
    return out


def test_floor_zone_counts_pinned():
    assert rules_constant("FLOOR_ZONES") == PINNED_FLOOR_ZONES, "fence-floor-zones-changed"
    files = tuple(rules_constant("FENCE_FILES")) + PINNED_FLOOR_FILES_EXTRA
    assert tuple(rules_constant("FLOOR_FILES")) == files, "fence-floor-files-changed"


def test_floor_zone_hashes():
    """Chữ giữa mốc và chữ quanh mốc khớp bản ghim: sửa vùng, dời mốc, đổi chữ lân cận đều làm test đỏ."""
    seen = set()
    for rel, count in PINNED_FLOOR_ZONES.items():
        text = (REPO / rel).read_text(encoding="utf-8").replace("\r\n", "\n")
        spans = _spans(text)
        assert len(spans) == count, f"fence-zone-count: {rel} cần {count} cặp mốc, có {len(spans)}"
        lines = text.split("\n")
        for index, (start, end) in enumerate(spans):
            inner = "\n".join(lines[start:end - 1])
            before = start - 2
            while before >= 0 and not lines[before].strip():
                before -= 1
            after = end
            while after < len(lines) and not lines[after].strip():
                after += 1
            around = (lines[before] if before >= 0 else "") + "\n" + (lines[after] if after < len(lines) else "")
            expected = PINNED_ZONE_HASHES[(rel, index)]
            assert _sha(inner) == expected[0], f"floor-zone-hash: chữ giữa mốc {rel} #{index} khác bản ghim"
            assert _sha(around) == expected[1], f"floor-marker-position: chữ quanh mốc {rel} #{index} khác bản ghim"
            seen.add((rel, index))
    assert seen == set(PINNED_ZONE_HASHES), "floor-zone-hash: bản ghim có vùng không còn trong file"


# SPR-20 TK2: chế độ mở chia 13 mục thành 7 luôn chặn + 6 mở mặc định (bản ghim viết tay; đổi thì nêu lý do ở thông điệp commit).
PINNED_OPEN_ALWAYS_BLOCKED = {"network_fetch", "rules_unlisted", "irreversible_delete", "secret", "auth", "user_soul", "license"}
PINNED_OPEN_DEFAULT_OPEN = {"push", "branch_merge_local", "version", "main_merge", "tag", "publish"}


def test_fence_wiring_pins_7_plus_6():
    always = rules_constant("OPEN_ALWAYS_BLOCKED")
    default_open = rules_constant("OPEN_DEFAULT_OPEN")
    assert set(always) == PINNED_OPEN_ALWAYS_BLOCKED and len(always) == 7, "fence-open-always-changed"
    assert set(default_open) == PINNED_OPEN_DEFAULT_OPEN and len(default_open) == 6, "fence-open-default-changed"
    assert set(always) | set(default_open) == PINNED_EXCLUSIONS and not set(always) & set(default_open), "fence-open-partition"
