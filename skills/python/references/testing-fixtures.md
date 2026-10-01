# Fixture, parametrize và marker

> **Kết luận:** fixture cung cấp dữ liệu/tài nguyên và dọn dẹp sau `yield`; chọn scope hẹp nhất đủ dùng
> (mặc định `function`), fixture dùng chung đặt ở `conftest.py`. `parametrize` thay cho chép test; marker
> đăng ký trong cấu hình và chạy với `--strict-markers` để gõ sai tên là báo lỗi.

## 1. Fixture

### 1.1. Cơ bản

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "Alice", "age": 30}

def test_sample_data(sample_data):
    assert sample_data["name"] == "Alice"
    assert sample_data["age"] == 30
```

### 1.2. Dựng và dọn bằng `yield`

```python
@pytest.fixture
def database():
    db = Database(":memory:")
    db.create_tables()
    db.insert_test_data()
    yield db          # đưa cho test
    db.close()        # dọn, chạy cả khi test hỏng

def test_database_query(database):
    assert len(database.query("SELECT * FROM users")) > 0
```

### 1.3. Scope

```python
@pytest.fixture                      # function (mặc định): mỗi test một lần
def temp_file(tmp_path):
    path = tmp_path / "temp.txt"
    path.write_text("")
    return path

@pytest.fixture(scope="module")      # mỗi module một lần
def module_db():
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()

@pytest.fixture(scope="session")     # cả phiên test một lần
def shared_resource():
    resource = ExpensiveResource()
    yield resource
    resource.cleanup()
```

Scope rộng thì nhanh hơn nhưng dễ rò trạng thái giữa test; dữ liệu bị test sửa → giữ scope `function`.

### 1.4. Fixture có tham số

```python
@pytest.fixture(params=[1, 2, 3])
def number(request):
    return request.param

def test_numbers(number):   # chạy 3 lần
    assert number > 0
```

### 1.5. Nhiều fixture, fixture tự chạy

```python
@pytest.fixture
def user():
    return User(id=1, name="Alice")

@pytest.fixture
def admin():
    return User(id=2, name="Admin", role="admin")

def test_admin_can_manage_user(user, admin):
    assert admin.can_manage(user)

@pytest.fixture(autouse=True)
def reset_config():
    """Runs around every test in scope without being requested."""
    Config.reset()
    yield
    Config.cleanup()
```

### 1.6. `conftest.py` cho fixture dùng chung

```python
# tests/conftest.py
import pytest

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers(client):
    response = client.post("/api/login", json={"username": "test", "password": "test"})
    return {"Authorization": f"Bearer {response.json['token']}"}
```

Mật khẩu/token trong fixture chỉ là giá trị test giả; không dùng secret thật.

## 2. Parametrize

### 2.1. Cơ bản và nhiều tham số

```python
@pytest.mark.parametrize("text,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("PyThOn", "PYTHON"),
])
def test_uppercase(text, expected):
    assert text.upper() == expected

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### 2.2. Đặt tên từng trường hợp bằng `ids`

```python
@pytest.mark.parametrize("email,expected", [
    ("valid@email.com", True),
    ("invalid", False),
    ("@no-domain.com", False),
], ids=["valid-email", "missing-at", "missing-domain"])
def test_email_validation(email, expected):
    assert is_valid_email(email) is expected
```

### 2.3. Fixture tham số hoá theo backend

```python
@pytest.fixture(params=["sqlite", "postgresql"])
def db(request):
    if request.param == "sqlite":
        return Database(":memory:")
    return Database("postgresql://localhost/test")

def test_database_operations(db):   # chạy một lần cho mỗi backend
    assert db.query("SELECT 1") is not None
```

## 3. Marker và chọn test

```python
@pytest.mark.slow
def test_slow_operation():
    ...

@pytest.mark.integration
def test_api_integration():
    ...

@pytest.mark.unit
def test_unit_logic():
    assert calculate(2, 3) == 5
```

```bash
uv run pytest -m "not slow"              # chỉ test nhanh
uv run pytest -m integration             # chỉ integration
uv run pytest -m "integration or slow"
uv run pytest -m "unit and not slow"
```

Đăng ký marker (thiếu đăng ký + `--strict-markers` → lỗi ngay):

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```
