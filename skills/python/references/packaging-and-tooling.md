# Tổ chức package và cấu hình công cụ

> **Kết luận:** bố cục `src/` + `tests/`, một `pyproject.toml` duy nhất chứa metadata, phụ thuộc và cấu
> hình công cụ; **uv** quản lý môi trường và khoá phụ thuộc (`uv.lock` được commit), **ruff** vừa định
> dạng vừa lint (gồm sắp import), **mypy** kiểm kiểu nghiêm, **pytest** chạy test + coverage.

Nguồn (phần bổ sung ở SPR-04, đọc 2026-10-04): PyPA (đóng gói, `[project.scripts]`) và tài liệu uv.

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

## 5. Công cụ dòng lệnh: `[project.scripts]`, `__main__.py`, build

```toml
[project.scripts]
mycli = "mypackage.cli:main"        # cài xong có lệnh `mycli`
```

```python
# src/mypackage/cli.py
import argparse
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("name")
    args = parser.parse_args(argv)          # argv=None → đọc sys.argv; test truyền danh sách vào
    print(f"hello {args.name}")
    return 0                                 # mã thoát
```

```python
# src/mypackage/__main__.py — để `python -m mypackage` chạy cùng đường vào
from mypackage.cli import main

raise SystemExit(main())
```

- Lệnh sinh từ `[project.scripts]` làm tương đương `import sys; from mypackage.cli import main; sys.exit(main())`,
  nên `main()` **trả mã thoát** (`0`, hoặc số khác khi lỗi), không tự `sys.exit` bên trong (khó test). Bảng
  `[project.gui-scripts]` dành cho ứng dụng đồ hoạ — chỉ khác ở Windows (không bật cửa sổ terminal).
- Giá trị dạng `"gói.module:hàm"` phải trỏ tới tên import được sau khi cài; sai tên thì lệnh cài xong mới báo
  lỗi khi chạy. Kiểm bằng cách chạy lệnh, không chỉ đọc cấu hình.
- Build: `uv build` sinh bản nguồn (sdist) và wheel vào `dist/`. Kiểm wheel ở môi trường sạch, không dùng thư
  mục dự án: `uv run --with dist/<tên>.whl --no-project -- mycli --help`; xem nội dung wheel bằng `unzip -l`
  (đủ file dữ liệu, có `entry_points.txt`).
- Nguồn: Python Packaging User Guide, "Writing your `pyproject.toml`" (mục tạo script chạy được); tài liệu `uv`,
  hướng dẫn build và kiểm package.

## 6. Vòng import (circular import)

`ImportError: cannot import name … (most likely due to a circular import)` hay `AttributeError` lúc nạp module
nghĩa là hai module import lẫn nhau. Gỡ theo thứ tự ưu tiên:

1. **Tách phần dùng chung ra module thứ ba** mà cả hai cùng import (kiểu, hằng, hàm tiện ích). Vòng import hầu hết
   là dấu hiệu hai module đang giữ một khái niệm chung chưa có chỗ riêng.
2. **Chỉ cần kiểu để chú thích** → import dưới `TYPE_CHECKING`, chú thích bằng chuỗi hoặc dùng
   `from __future__ import annotations`; import này không chạy lúc nạp nên không tạo vòng:
   ```python
   from __future__ import annotations
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from mypackage.orders import Order   # chỉ cho trình kiểm kiểu

   def refund(order: Order) -> None: ...
   ```
3. **Đảo chiều phụ thuộc**: module cấp thấp nhận thứ nó cần qua tham số hoặc `Protocol`
   (`references/type-hints-and-dataclasses.md` mục 1.4) thay vì import module cấp cao.
4. **Import cục bộ trong hàm** là cách cuối: nó giấu vòng chứ không gỡ, và chỉ chấp nhận khi hai khái niệm thật
   sự gắn nhau; để lại một dòng chú thích vì sao.

Không "chữa" bằng cách đổi thứ tự dòng `import` cho tới khi chạy được — vòng vẫn còn, chỉ hỏng lúc khác. Thứ tự
import (mục 2) do `ruff` sắp, nên đổi tay cũng bị sắp lại.
