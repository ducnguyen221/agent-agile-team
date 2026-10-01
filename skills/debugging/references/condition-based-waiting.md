# Chờ theo điều kiện

> **Kết luận:** test chập chờn thường đoán thời gian bằng một khoảng chờ tuỳ ý — đạt trên máy nhanh, hỏng
> khi máy tải nặng hay chạy CI. **Chờ đúng điều kiện bạn cần**, không chờ một con số đoán xem việc mất bao
> lâu; luôn có timeout kèm thông báo rõ.

Dùng khi: test có `sleep`/`setTimeout` tuỳ ý; test chập chờn (lúc đạt lúc hỏng khi tải nặng); test timeout
khi chạy song song; chờ thao tác bất đồng bộ xong. **Không** dùng khi chính hành vi cần test là thời gian
(debounce, throttle, chu kỳ) — khi đó ghi rõ **vì sao** cần khoảng chờ đó.

## 1. Mẫu chính

```python
# Sai — đoán thời gian
time.sleep(0.05)
assert get_result() is not None

# Đúng — chờ điều kiện
wait_for(lambda: get_result() is not None, "result available")
assert get_result() is not None
```

| Tình huống | Mẫu |
|---|---|
| Chờ sự kiện | `wait_for(lambda: next((e for e in events if e.type == "DONE"), None), "DONE event")` |
| Chờ trạng thái | `wait_for(lambda: machine.state == "ready", "machine ready")` |
| Chờ số lượng | `wait_for(lambda: len(items) >= 5, "5 items")` |
| Chờ file | `wait_for(lambda: path.exists(), f"{path} created")` |
| Điều kiện ghép | `wait_for(lambda: obj.ready and obj.value > 10, "obj ready > 10")` |

## 2. Hàm chờ dùng chung

```python
import time
from typing import Callable, TypeVar

T = TypeVar("T")

def wait_for(condition: Callable[[], T], description: str,
             timeout_s: float = 5.0, interval_s: float = 0.01) -> T:
    deadline = time.monotonic() + timeout_s
    while True:
        result = condition()          # gọi lại mỗi vòng: luôn đọc dữ liệu mới
        if result:
            return result
        if time.monotonic() > deadline:
            raise TimeoutError(f"timeout waiting for {description} after {timeout_s}s")
        time.sleep(interval_s)
```

Bản `async`: thay `time.sleep` bằng `await asyncio.sleep`. Thư viện test thường có sẵn (ví dụ
`waitFor` của Testing Library, `expect.poll` của Playwright) — dùng bản có sẵn nếu dự án đã có.

## 3. Lỗi hay gặp

| Sai | Sửa |
|---|---|
| Thăm dò quá dày (1 ms) — đốt CPU | ~10 ms mỗi vòng |
| Không có timeout — treo mãi khi điều kiện không bao giờ đúng | luôn có timeout và thông báo nói đang chờ gì |
| Đọc trạng thái một lần trước vòng lặp — dữ liệu cũ | gọi hàm đọc **bên trong** vòng lặp |

## 4. Khi khoảng chờ tuỳ ý là đúng

```python
wait_for_event(manager, "TOOL_STARTED")   # trước hết: chờ điều kiện kích hoạt
time.sleep(0.2)   # công cụ tick mỗi 100 ms — cần 2 tick để thấy output dở dang
```

Điều kiện: (1) chờ điều kiện kích hoạt trước; (2) con số dựa trên nhịp đã biết, không đoán; (3) có chú
thích giải thích **vì sao**.
