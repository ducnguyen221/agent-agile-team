# Kiểm thử Python bằng pytest — lõi

> **Kết luận:** test viết **trước** code theo skill `tdd` (đỏ → xanh → refactor); mỗi test kiểm **một
> hành vi**, tên nói rõ hành vi đó, chạy độc lập và nhanh. Dùng `assert` thuần và `pytest.raises`;
> fixture để khử lặp, mock chỉ cho phụ thuộc bên ngoài. Ngưỡng coverage theo `method/conventions.md`
> mục 1, không đặt con số riêng ở đây.

## 1. Triết lý

### 1.1. Test trước (theo skill `tdd`)

1. **Đỏ**: viết test cho hành vi mong muốn, chạy và **thấy nó hỏng đúng lý do**.
2. **Xanh**: viết code tối thiểu cho test qua.
3. **Refactor**: làm sạch code, test vẫn xanh.

```python
# Bước 1 — đỏ: test trước, hàm chưa có
def test_add_returns_sum_of_two_numbers():
    assert add(2, 3) == 5

# Bước 2 — xanh: code tối thiểu
def add(a, b):
    return a + b

# Bước 3 — refactor nếu cần, chạy lại test
```

### 1.2. Coverage

- Ngưỡng: `method/conventions.md` mục 1 — mặc định 80 % dòng cho **code mới và code được sửa**; dự án
  chỉnh qua `.agile.json` (`coverage.line_min_percent` kèm `coverage.reason`).
- Coverage là điều kiện cần, không đủ: test phải bắt được lỗi thật, không assert lên chính mock.
- Đo và ghi kèm lệnh vào `VR`:

```bash
uv run pytest --cov=mypackage --cov-report=term-missing
```

## 2. Cơ bản về pytest

### 2.1. Cấu trúc test

```python
def test_addition():
    assert 2 + 2 == 4

def test_upper_converts_all_letters():
    assert "hello".upper() == "HELLO"
```

Hàm tên `test_*` trong file `test_*.py`; pytest tự tìm, không cần lớp hay `unittest.TestCase`.

### 2.2. Assert

```python
import pytest

assert result == expected
assert result != unexpected
assert result               # truthy
assert not result           # falsy
assert result is None       # đúng None
assert item in collection
assert 0 <= result <= 100
assert isinstance(result, str)

# Ngoại lệ: dùng pytest.raises, không try/except trong test
with pytest.raises(ValueError, match="invalid input"):
    validate("bad")          # match là regex tìm trong thông báo lỗi

with pytest.raises(ValueError) as exc_info:
    validate("bad")
assert str(exc_info.value) == "invalid input: bad"
```

So số thực: `assert value == pytest.approx(0.3)`.

## 3. Nên và không nên

**Nên**
- Viết test trước code (skill `tdd`).
- Mỗi test một hành vi; tên mô tả: `test_login_with_invalid_credentials_fails`.
- Dùng fixture để khử lặp (`testing-fixtures.md`).
- Mock phụ thuộc bên ngoài (mạng, API bên thứ ba, đồng hồ) — không mock chính code đang test.
- Thử biên: rỗng, `None`, giá trị biên, dữ liệu sai kiểu.
- Giữ test nhanh; tách test chậm bằng marker `slow`.

**Không nên**
- Test chi tiết cài đặt thay vì hành vi.
- Đặt điều kiện rẽ nhánh phức tạp trong test.
- Bỏ qua test hỏng, đánh `skip` để qua kiểm.
- Test code của thư viện bên thứ ba.
- Chia sẻ trạng thái giữa các test.
- Bắt ngoại lệ bằng `try/except` trong test (dùng `pytest.raises`).
- Dùng `print` để kiểm (dùng `assert`).
- Mock quá cụ thể làm test gãy khi refactor.

## 4. Chạy test

```bash
uv run pytest                                   # chạy hết
uv run pytest tests/test_utils.py               # một file
uv run pytest tests/test_utils.py::test_func    # một test
uv run pytest -v                                # chi tiết
uv run pytest --cov=mypackage --cov-report=term-missing   # kèm coverage
uv run pytest -m "not slow"                     # bỏ test chậm
uv run pytest -x                                # dừng ở lỗi đầu tiên
uv run pytest --maxfail=3                       # dừng sau 3 lỗi
uv run pytest --lf                              # chạy lại test vừa hỏng
uv run pytest -k "test_user"                    # lọc theo tên
uv run pytest --pdb                             # mở debugger khi hỏng
```

## 5. Đọc gì khi nào

| Cần | Đọc |
|---|---|
| Fixture (scope, params, autouse, `conftest.py`), `@pytest.mark.parametrize`, marker và chọn test | `testing-fixtures.md` |
| Mock/patch (`@patch`, `autospec`, `side_effect`, `PropertyMock`), test async với pytest-asyncio | `testing-mocking-async.md` |
| Test ngoại lệ chi tiết, file tạm (`tmp_path`), bố cục thư mục test, lớp test, mẫu test API/DB, cấu hình pytest | `testing-organization.md` |
| Test endpoint FastAPI (ghi đè dependency, client async) | skill `fastapi`, `references/routes-errors-openapi-testing.md` |

## 6. Tra nhanh

| Mẫu | Dùng |
|---|---|
| `pytest.raises()` | kiểm ngoại lệ mong đợi |
| `@pytest.fixture()` | fixture dùng lại |
| `@pytest.mark.parametrize()` | một test, nhiều bộ đầu vào |
| `@pytest.mark.slow` | đánh dấu test chậm |
| `pytest -m "not slow"` | bỏ test chậm |
| `@patch()` | mock hàm, lớp |
| `tmp_path` | thư mục tạm tự dọn |
| `pytest --cov` | báo cáo coverage |
| `assert` | kiểm tra đơn giản, dễ đọc |
