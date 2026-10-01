# Tổ chức test, cấu hình pytest và mẫu thường gặp

> **Kết luận:** tách thư mục theo loại test (unit / integration / e2e), fixture chung ở `conftest.py`.
> File tạm dùng `tmp_path`, không tự tạo/xoá bằng `tempfile`. Test DB chạy trong transaction rồi
> rollback. Cấu hình pytest đặt trong `pyproject.toml`, bật `--strict-markers`.

## 1. Test ngoại lệ

```python
def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_invalid_input_message():
    with pytest.raises(ValueError, match="invalid input"):
        validate_input("invalid")

def test_exception_carries_code():
    with pytest.raises(CustomError) as exc_info:
        handle_request(bad_payload)
    assert exc_info.value.code == 400
    assert "error" in str(exc_info.value)
```

## 2. Test tác dụng phụ lên file

```python
# Nên: tmp_path — thư mục tạm riêng mỗi test, pytest tự dọn
def test_process_file(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    assert process_file(str(test_file)) == "hello world"
```

Tránh `tempfile.NamedTemporaryFile(delete=False)` + `os.unlink` thủ công (dễ để rác khi test hỏng) và
fixture cũ `tmpdir` (kiểu `py.path`); dùng `tmp_path` (kiểu `pathlib.Path`).

## 3. Bố cục thư mục test

```
tests/
├── conftest.py          # fixture dùng chung
├── unit/
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_services.py
├── integration/
│   ├── test_api.py
│   └── test_database.py
└── e2e/
    └── test_user_flow.py
```

## 4. Lớp test — nhóm test cùng đối tượng

```python
class TestUserService:
    @pytest.fixture
    def service(self):
        return UserService()

    def test_create_user(self, service):
        assert service.create_user("Alice").name == "Alice"

    def test_delete_user(self, service):
        user = service.create_user("Bob")
        service.delete_user(user)
        assert not service.user_exists(user.id)
```

Lớp test không kế thừa `unittest.TestCase` và không có `__init__`; trạng thái đi qua fixture.

## 5. Mẫu thường gặp

### 5.1. Test endpoint API (đồng bộ)

```python
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(create_app())

def test_get_order(client):
    response = client.get("/api/orders/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_create_order(client):
    response = client.post("/api/orders", json={"sku": "BOOK-1", "quantity": 2})
    assert response.status_code == 201
    assert response.json()["quantity"] == 2
```

Client async và ghi đè dependency DB: skill `fastapi`, `references/routes-errors-openapi-testing.md`.

### 5.2. Test thao tác DB trong transaction lồng

```python
@pytest.fixture
def db_session():
    session = Session(bind=engine)
    session.begin_nested()
    yield session
    session.rollback()     # không để dữ liệu test lại
    session.close()

def test_create_user(db_session):
    db_session.add(User(name="Alice", email="alice@example.com"))
    db_session.flush()

    retrieved = db_session.query(User).filter_by(name="Alice").first()
    assert retrieved.email == "alice@example.com"
```

Test chạm DB thật (Postgres) chạy với DB riêng cho test, không bao giờ trỏ vào DB production.

## 6. Cấu hình pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=mypackage",
    "--cov-report=term-missing",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

Dự án dùng `pytest.ini` thì cùng khoá, đặt dưới mục `[pytest]`. Không thêm `--disable-warnings` để giấu
cảnh báo; xử lý hoặc lọc đích danh bằng `filterwarnings`.
