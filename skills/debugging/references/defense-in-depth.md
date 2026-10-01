# Chặn nhiều tầng

> **Kết luận:** sửa xong một lỗi do dữ liệu sai, thêm một chỗ kiểm thấy là đủ — nhưng một chỗ kiểm có thể
> bị vượt qua bởi đường mã khác, refactor, hay mock. Kiểm ở **mọi tầng** dữ liệu đi qua để lỗi trở nên
> **không thể xảy ra về cấu trúc**: một chỗ kiểm = "đã sửa lỗi"; nhiều tầng = "lỗi không thể có".

Dùng sau khi đã tìm ra nguyên nhân gốc (`root-cause-tracing.md`), không thay cho việc tìm nó.

## 1. Bốn tầng

| Tầng | Mục đích | Bắt được |
|---|---|---|
| 1. Điểm vào | từ chối đầu vào hiển nhiên sai ở biên API | phần lớn lỗi |
| 2. Logic nghiệp vụ | dữ liệu có hợp lý cho **thao tác này** không | ca biên, đường mã vòng qua điểm vào |
| 3. Chặn theo môi trường | cấm thao tác nguy hiểm trong ngữ cảnh cụ thể (đang test, production) | nguy cơ riêng ngữ cảnh, khác biệt nền tảng |
| 4. Đo đạc gỡ lỗi | ghi ngữ cảnh để điều tra khi các tầng kia hỏng | dùng sai cấu trúc, lỗi chưa thấy |

```python
from pathlib import Path
import os, tempfile, logging, traceback

log = logging.getLogger(__name__)

# Tầng 1 — điểm vào
def create_project(name: str, working_dir: str) -> "Project":
    if not working_dir or not working_dir.strip():
        raise ValueError("working_dir must not be empty")
    path = Path(working_dir)
    if not path.is_dir():
        raise ValueError(f"working_dir is not an existing directory: {working_dir}")
    ...

# Tầng 2 — logic nghiệp vụ
def initialize_workspace(project_dir: str, session_id: str) -> None:
    if not project_dir:
        raise ValueError("project_dir required for workspace initialization")
    ...

# Tầng 3 — chặn theo môi trường
def git_init(directory: str) -> None:
    if os.environ.get("APP_ENV") == "test":
        target = Path(directory).resolve()
        tmp = Path(tempfile.gettempdir()).resolve()
        if not target.is_relative_to(tmp):
            raise RuntimeError(f"refusing git init outside temp dir during tests: {directory}")
    # Tầng 4 — đo đạc
    log.debug("about to git init", extra={"directory": directory, "cwd": os.getcwd(),
              "stack": "".join(traceback.format_stack())})
    ...
```

## 2. Cách áp

1. **Lần luồng dữ liệu** — giá trị xấu sinh ra ở đâu, được dùng ở đâu.
2. **Vẽ mọi điểm dữ liệu đi qua** — liệt kê từng hàm/tầng.
3. **Thêm kiểm ở mỗi tầng** — điểm vào, nghiệp vụ, môi trường, đo đạc.
4. **Test từng tầng** — cố vượt qua tầng 1 (gọi thẳng tầng 2), xác nhận tầng 2 bắt được; mỗi tầng có test
   riêng (skill `tdd`).

Trong thực tế cả bốn tầng đều cần: đường mã khác vượt qua kiểm ở điểm vào; mock vượt qua kiểm nghiệp vụ; ca
biên trên nền tảng khác cần chặn theo môi trường; log gỡ lỗi chỉ ra chỗ dùng sai cấu trúc. **Đừng dừng ở
một điểm kiểm.**
