# Type hint, dataclass và NamedTuple

> **Kết luận:** chú thích kiểu mọi chữ ký hàm, dùng kiểu dựng sẵn (`list[str]`, `X | None`) thay
> `typing.List`/`Optional` từ Python 3.9/3.10; `Protocol` cho duck typing có kiểm; `dataclass` cho lớp
> dữ liệu (kiểm hợp lệ trong `__post_init__`), `NamedTuple` cho bản ghi bất biến nhỏ.

## 1. Type hint

### 1.1. Chú thích cơ bản

```python
from typing import Any

def process_user(
    user_id: str,
    data: dict[str, Any],
    active: bool = True,
) -> User | None:
    """Process a user and return the updated User or None."""
    if not active:
        return None
    return User(user_id, data)
```

### 1.2. Kiểu dựng sẵn (Python 3.9+) và cú pháp cũ

```python
# Python 3.9+: dùng kiểu dựng sẵn
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Python 3.8 trở về trước: mới cần typing.List / typing.Dict
from typing import Dict, List

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
```

`X | None` cần Python 3.10 (hoặc `from __future__ import annotations`); dưới đó dùng `Optional[X]`.

### 1.3. Bí danh kiểu và `TypeVar`

```python
from typing import Any, TypeVar, Union

# Bí danh cho kiểu phức tạp
JSON = Union[dict[str, Any], list[Any], str, int, float, bool, None]

def parse_json(data: str) -> JSON:
    return json.loads(data)

# Kiểu tổng quát
T = TypeVar("T")

def first(items: list[T]) -> T | None:
    """Return the first item or None if the list is empty."""
    return items[0] if items else None
```

### 1.4. `Protocol` — duck typing có kiểm kiểu

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str:
        """Render the object to a string."""

def render_all(items: list[Renderable]) -> str:
    """Render every item that implements Renderable."""
    return "\n".join(item.render() for item in items)
```

## 2. Dataclass và NamedTuple

### 2.1. Dataclass

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    """User entity with generated __init__, __repr__ and __eq__."""
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

user = User(id="123", name="Alice", email="alice@example.com")
```

Giá trị mặc định khả biến (list, dict, thời điểm hiện tại) luôn qua `field(default_factory=...)`.

### 2.2. Dataclass có kiểm hợp lệ

```python
@dataclass
class User:
    email: str
    age: int

    def __post_init__(self):
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        if self.age < 0 or self.age > 150:
            raise ValueError(f"Invalid age: {self.age}")
```

### 2.3. NamedTuple

```python
from typing import NamedTuple

class Point(NamedTuple):
    """Immutable 2D point."""
    x: float
    y: float

    def distance(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

Point(0, 0).distance(Point(3, 4))  # 5.0
```
