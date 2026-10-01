---
name: python
description: Use when writing, reviewing, or refactoring Python code, designing a Python package or module, setting up Python tooling (uv, ruff, mypy, pytest), or writing and reviewing pytest tests — fixtures, mocks, parametrization, async tests, coverage.
metadata:
  group: technique
  kind: reference
  roles: [implementer, qa, tech-reviewer]
source: [affaan-m/ECC skills/python-patterns/SKILL.md, affaan-m/ECC skills/python-testing/SKILL.md]
source_sha: [c70874fae9eb0e5ad0365beb7e2955899fd1d30f, c70874fae9eb0e5ad0365beb7e2955899fd1d30f]
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: MIT
rewrite_before_public: false
---

# Python — viết code đúng kiểu và kiểm thử bằng pytest

> **Kết luận:** code Python phải **dễ đọc, tường minh, ít bất ngờ**: rõ hơn khéo, bắt lỗi cụ thể, tài
> nguyên đi qua `with`, chữ ký hàm có type hint. Bộ công cụ chuẩn: **uv** (môi trường + phụ thuộc),
> **ruff** (định dạng + lint), **mypy** (kiểu), **pytest** (test, viết trước code theo skill `tdd`).
> Chi tiết theo chủ đề nằm trong `references/` — mở đúng file khi cần (mục 5).

## 1. Khi nào dùng

- Viết code Python mới, review hoặc refactor code Python.
- Thiết kế package/module, bố cục dự án, cấu hình `pyproject.toml`.
- Viết, tổ chức, chạy test pytest; đo coverage (đọc `references/testing.md`).

## 2. Ba nguyên tắc lõi

### 2.1. Dễ đọc là trên hết

```python
# Nên: rõ ràng, có kiểu, có docstring
def get_active_users(users: list[User]) -> list[User]:
    """Return only active users from the provided list."""
    return [user for user in users if user.is_active]


# Tránh: khéo nhưng khó hiểu
def get_active_users(u):
    return [x for x in u if x.a]
```

### 2.2. Tường minh hơn ngầm định

Không "ma thuật": đọc code là biết nó làm gì, không giấu tác dụng phụ trong một lệnh import hay `setup()`.

```python
# Nên: cấu hình tường minh
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Tránh: tác dụng phụ ẩn
import some_module
some_module.setup()  # làm gì?
```

### 2.3. EAFP — thử rồi xử lý ngoại lệ, thay vì kiểm trước

```python
# Nên: EAFP
def get_value(dictionary: dict, key: str, default: Any = None) -> Any:
    try:
        return dictionary[key]
    except KeyError:
        return default

# Tránh: LBYL (kiểm trước rồi mới làm)
def get_value(dictionary: dict, key: str, default: Any = None) -> Any:
    if key in dictionary:
        return dictionary[key]
    return default
```

## 3. Công cụ: uv, ruff, mypy, pytest

```bash
uv sync                                  # tạo/cập nhật .venv theo pyproject.toml + uv.lock
uv add httpx                             # thêm phụ thuộc chạy
uv add --dev pytest pytest-cov ruff mypy # thêm phụ thuộc phát triển
uv run ruff format .                     # định dạng (thay black + isort)
uv run ruff check . --fix                # lint, gồm sắp xếp import
uv run mypy src                          # kiểm kiểu
uv run pytest --cov=mypackage --cov-report=term-missing   # test + coverage
uv run ruff check . --select S           # luật bảo mật (bộ luật kiểu bandit của ruff)
uv run --with pip-audit pip-audit        # audit lỗ hổng phụ thuộc
```

- Commit `uv.lock`; CI chạy `uv sync --locked` để phụ thuộc không trôi.
- Không sửa cấu hình ruff/mypy/pytest hay hạ ngưỡng coverage chỉ để qua kiểm.
- Cấu hình đầy đủ `pyproject.toml`: `references/packaging-and-tooling.md`.

## 4. Kiểm thử

- Test viết **trước** code (đỏ → xanh → refactor) theo skill `tdd`; Python cụ thể: pytest, fixture,
  parametrize, mock, async — đọc **`references/testing.md`** (lõi) rồi các file `testing-*.md` khi cần.
- Coverage: ngưỡng chung ở `method/conventions.md` mục 1 (mặc định 80 % dòng cho code mới và code được
  sửa; dự án chỉnh qua `.agile.json` kèm lý do). Skill này không đặt ngưỡng riêng.
- Test hỏng hay hành vi lạ: skill `debugging` trước khi sửa.

## 5. Đọc gì khi nào

| Cần | Đọc |
|---|---|
| Type hint (cơ bản, kiểu dựng sẵn từ 3.9, `TypeVar`, `Protocol`), dataclass (+ kiểm hợp lệ), `NamedTuple` | `references/type-hints-and-dataclasses.md` |
| Bắt và nối ngoại lệ, cây ngoại lệ riêng, context manager (`@contextmanager`, `__enter__`/`__exit__`), decorator (hàm, có tham số, dạng lớp) | `references/errors-context-decorators.md` |
| Comprehension vs generator; thread vs process vs asyncio; `__slots__`; ghép chuỗi hiệu quả | `references/generators-concurrency-performance.md` |
| Bố cục `src/`, thứ tự import, export trong `__init__.py`, `pyproject.toml` đầy đủ (uv, ruff, mypy, pytest) | `references/packaging-and-tooling.md` |
| Triết lý test, cấu trúc test pytest, assert, nên/không nên, lệnh chạy test | `references/testing.md` |
| Fixture (scope, params, autouse, `conftest.py`), `parametrize`, marker | `references/testing-fixtures.md` |
| Mock/patch (`autospec`, `side_effect`, `PropertyMock`), test async | `references/testing-mocking-async.md` |
| Test ngoại lệ, file tạm, bố cục thư mục test, lớp test, mẫu test API/DB, cấu hình pytest | `references/testing-organization.md` |

## 6. Thành ngữ tra nhanh

| Thành ngữ | Dùng khi |
|---|---|
| EAFP | thử rồi bắt ngoại lệ cụ thể thay vì kiểm trước |
| Context manager | quản lý tài nguyên bằng `with` |
| List comprehension | biến đổi đơn giản |
| Generator | xử lý lười, dữ liệu lớn |
| Type hint | chú thích mọi chữ ký hàm |
| Dataclass | lớp chứa dữ liệu, tự sinh `__init__`/`__repr__`/`__eq__` |
| `__slots__` | tiết kiệm bộ nhớ khi có rất nhiều đối tượng |
| f-string | định dạng chuỗi |
| `pathlib.Path` | thao tác đường dẫn |
| `enumerate` | cần cả chỉ số lẫn phần tử khi lặp |

## 7. Phản mẫu cần tránh

```python
# Tránh: giá trị mặc định khả biến (list dùng chung giữa các lần gọi)
def append_to(item, items=[]):
    items.append(item)
    return items

# Nên: mặc định None, tạo mới trong hàm
def append_to(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

# Tránh: so kiểu bằng type()          # Nên: isinstance
if type(obj) == list: ...              # if isinstance(obj, list): ...

# Tránh: so None bằng ==               # Nên: is
if value == None: ...                  # if value is None: ...

# Tránh: import *                      # Nên: import tường minh
from os.path import *                  # from os.path import join, exists

# Tránh: except trần nuốt mọi lỗi
try:
    risky_operation()
except:
    pass

# Nên: bắt lỗi cụ thể, ghi log có ngữ cảnh
try:
    risky_operation()
except SpecificError:
    logger.exception("risky_operation failed")
    raise
```

## 8. Liên quan

- Skill: `tdd` (test trước), `debugging`, `error-handling`, `fastapi`, `postgres`, `security-review`,
  `code-review`, `verify-before-done`.
- Agent reviewer: `python-reviewer` (code Python), `silent-failure-hunter` (lỗi bị nuốt, fallback sai).
