# Mock, patch và test code async

> **Kết luận:** patch **nơi tên được dùng** (`mypackage.module.name`), không phải nơi nó được định nghĩa;
> bật `autospec=True` để mock gọi sai chữ ký là hỏng ngay. Mock chỉ phụ thuộc bên ngoài và kiểm hành vi
> quan sát được, không assert lên chính mock. Test async dùng pytest-asyncio, mock async bằng `AsyncMock`.

## 1. Mock và patch

### 1.1. Mock hàm

```python
from unittest.mock import Mock, patch

@patch("mypackage.service.external_api_call")
def test_with_mock(api_call_mock):
    api_call_mock.return_value = {"status": "success"}

    result = my_function()

    api_call_mock.assert_called_once()
    assert result["status"] == "success"
```

### 1.2. Mock giá trị trả về và đối số gọi

```python
@patch("mypackage.db.Database.connect")
def test_database_connection(connect_mock):
    connect_mock.return_value = FakeConnection()

    Database().connect()

    connect_mock.assert_called_once_with("localhost")
```

### 1.3. Mock ngoại lệ bằng `side_effect`

```python
@patch("mypackage.client.api_call")
def test_api_error_is_reported(api_call_mock):
    api_call_mock.side_effect = ConnectionError("Network error")

    with pytest.raises(ServiceUnavailable):
        fetch_report()          # code đang test, không phải mock

    api_call_mock.assert_called_once()
```

### 1.4. Mock `open`

```python
from unittest.mock import mock_open

@patch("builtins.open", new_callable=mock_open, read_data="file content")
def test_file_reading(mock_file):
    assert read_file("test.txt") == "file content"
    mock_file.assert_called_once_with("test.txt", "r")
```

Đọc/ghi file thật thường đơn giản hơn với `tmp_path` (`testing-organization.md`).

### 1.5. `autospec` — bắt dùng sai API

```python
@patch("mypackage.db.DBConnection", autospec=True)
def test_autospec(db_mock):
    db = db_mock.return_value
    db.query("SELECT * FROM users")   # hỏng nếu DBConnection không có query()
    db_mock.assert_called_once()
```

### 1.6. Mock instance của lớp

```python
class TestUserService:
    @patch("mypackage.service.UserRepository")
    def test_create_user(self, repo_mock):
        repo_mock.return_value.save.return_value = User(id=1, name="Alice")

        service = UserService(repo_mock.return_value)
        user = service.create_user(name="Alice")

        assert user.name == "Alice"
        repo_mock.return_value.save.assert_called_once()
```

Khi có thể, truyền phụ thuộc qua tham số (dependency injection) và đưa vào một bản giả đơn giản thay vì
`patch`.

### 1.7. Mock property

```python
from unittest.mock import PropertyMock

@pytest.fixture
def mock_config():
    config = Mock()
    type(config).debug = PropertyMock(return_value=True)
    type(config).api_key = PropertyMock(return_value="test-key")
    return config

def test_with_mock_config(mock_config):
    assert mock_config.debug is True
    assert mock_config.api_key == "test-key"
```

## 2. Test code async

### 2.1. pytest-asyncio

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    assert await async_add(2, 3) == 5
```

Đặt `asyncio_mode = "auto"` trong `[tool.pytest.ini_options]` để bỏ được marker trên từng test.

### 2.2. Fixture async

```python
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client():
    app = create_app()
    async with app.test_client() as client:
        yield client

@pytest.mark.asyncio
async def test_api_endpoint(async_client):
    response = await async_client.get("/api/data")
    assert response.status_code == 200
```

Client async cho FastAPI (httpx + `ASGITransport`, ghi đè dependency): skill `fastapi`.

### 2.3. Mock hàm async

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
@patch("mypackage.client.async_api_call", new_callable=AsyncMock)
async def test_async_mock(api_call_mock):
    api_call_mock.return_value = {"status": "ok"}

    result = await my_async_function()

    api_call_mock.assert_awaited_once()
    assert result["status"] == "ok"
```
