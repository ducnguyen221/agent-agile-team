# Tổ chức package và cấu hình công cụ

> **Kết luận:** bố cục `src/` + `tests/`, một `pyproject.toml` duy nhất chứa metadata, phụ thuộc và cấu
> hình công cụ; **uv** quản lý môi trường và khoá phụ thuộc (`uv.lock` được commit), **ruff** vừa định
> dạng vừa lint (gồm sắp import), **mypy** kiểm kiểu nghiêm, **pytest** chạy test + coverage.

## 1. Bố cục dự án chuẩn

```
myproject/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_models.py
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

Bố cục thư mục test chi tiết (unit / integration / e2e): `testing-organization.md`.

## 2. Quy ước import

```python
# Thứ tự: thư viện chuẩn → bên thứ ba → nội bộ, mỗi nhóm cách một dòng trống
import os
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI

from mypackage.models import User
from mypackage.utils import format_name
```

Không sắp tay: `uv run ruff check . --fix` với nhóm luật `I` sắp lại theo thứ tự trên.

## 3. Export ở `__init__.py`

```python
# src/mypackage/__init__.py
"""mypackage - a sample Python package."""

__version__ = "1.0.0"

from mypackage.models import Post, User
from mypackage.utils import format_name

__all__ = ["User", "Post", "format_name"]
```

## 4. `pyproject.toml`

```toml
[project]
name = "mypackage"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.0",
]

[dependency-groups]          # uv add --dev ... ghi vào đây
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.6",
    "mypy>=1.10",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "UP"]   # thêm "S" nếu muốn luật bảo mật mặc định

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=mypackage --cov-report=term-missing"
```

- Ngưỡng coverage không đặt ở đây theo ý thích: theo `method/conventions.md` mục 1.
- Đổi cấu hình lint/kiểu/test để code "qua" kiểm là điều cấm; sửa code, hoặc ghi lý do và xin duyệt.
