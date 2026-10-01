# Xử lý lỗi, context manager và decorator

> **Kết luận:** bắt **ngoại lệ cụ thể**, nối nguyên nhân bằng `raise ... from e`, gom lỗi miền vào một
> cây ngoại lệ riêng; không bao giờ `except:` trần rồi trả `None`. Tài nguyên đi qua context manager.
> Decorator luôn bọc `functools.wraps` để giữ tên và docstring hàm gốc.

## 1. Xử lý lỗi

### 1.1. Bắt ngoại lệ cụ thể

```python
# Nên: bắt đúng loại lỗi, đổi sang lỗi miền và giữ nguyên nhân
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            return Config.from_json(f.read())
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {path}") from e

# Tránh: except trần, lỗi biến mất không dấu vết
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            return Config.from_json(f.read())
    except:
        return None
```

### 1.2. Nối ngoại lệ

```python
def process_data(data: str) -> Result:
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        # `from e` giữ traceback gốc
        raise ValueError(f"Failed to parse data: {data}") from e
```

### 1.3. Cây ngoại lệ riêng của ứng dụng

```python
class AppError(Exception):
    """Base exception for all application errors."""

class ValidationError(AppError):
    """Input validation failed."""

class NotFoundError(AppError):
    """Requested resource does not exist."""

def get_user(user_id: str) -> User:
    user = db.find_user(user_id)
    if not user:
        raise NotFoundError(f"User not found: {user_id}")
    return user
```

Lỗi bị nuốt, fallback im lặng, lỗi không lan ra ngoài: xem skill `error-handling`; review bằng agent
`silent-failure-hunter`.

## 2. Context manager

### 2.1. Quản lý tài nguyên

```python
# Nên
def process_file(path: str) -> str:
    with open(path) as f:
        return f.read()

# Tránh: tự mở/đóng bằng try/finally
def process_file(path: str) -> str:
    f = open(path)
    try:
        return f.read()
    finally:
        f.close()
```

### 2.2. Context manager bằng `@contextmanager`

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    """Time a block of code."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{name} took {elapsed:.4f} seconds")

with timer("data processing"):
    process_large_dataset()
```

### 2.3. Context manager dạng lớp

```python
class DatabaseTransaction:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.connection.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        return False  # không nuốt ngoại lệ

with DatabaseTransaction(conn):
    user = conn.create_user(user_data)
    conn.create_profile(user.id, profile_data)
```

## 3. Decorator

### 3.1. Decorator hàm

```python
import functools
import time
from collections.abc import Callable

def timer(func: Callable) -> Callable:
    """Time function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
```

### 3.2. Decorator có tham số

```python
def repeat(times: int):
    """Call the wrapped function `times` times and collect results."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator

@repeat(times=3)
def greet(name: str) -> str:
    return f"Hello, {name}!"

# greet("Alice") -> ["Hello, Alice!", "Hello, Alice!", "Hello, Alice!"]
```

### 3.3. Decorator dạng lớp (giữ trạng thái)

```python
class CountCalls:
    """Count how many times a function is called."""
    def __init__(self, func: Callable):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

@CountCalls
def process():
    pass
# process.count tăng sau mỗi lần gọi
```
