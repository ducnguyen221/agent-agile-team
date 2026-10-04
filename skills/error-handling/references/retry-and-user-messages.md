# Retry có backoff và câu báo lỗi cho người dùng

> **Kết luận:** retry chỉ lỗi thoáng qua (5xx, timeout, mất kết nối), backoff mũ cộng jitter, có trần lần
> thử và trần độ trễ; hết lượt thì ném lỗi cuối cùng, không nuốt. Retry ở **một** tầng, kèm ngắt mạch khi
> dependency hỏng kéo dài; việc chạy qua hàng đợi thì lỗi vĩnh viễn đi vào hàng chờ lỗi. Câu cho người dùng lấy
> từ **một** bảng tra theo mã lỗi, mã lạ rơi về câu lỗi chung.

Nguồn (phần bổ sung ở SPR-04, đọc 2026-10-04): AWS Builders' Library (timeout, retry, backoff), Amazon SQS (hàng chờ lỗi), Azure Architecture Center (retry, ngắt mạch).

## 1. Retry — Python

```python
import random
import time
from typing import Callable, TypeVar

import httpx

T = TypeVar("T")

def is_retriable(exc: Exception) -> bool:
    if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500 or exc.response.status_code == 429
    return False

def with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    retry_if: Callable[[Exception], bool] = is_retriable,
) -> T:
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as exc:
            if attempt == max_attempts or not retry_if(exc):
                raise
            jitter = random.uniform(0, base_delay)
            time.sleep(min(base_delay * 2 ** (attempt - 1) + jitter, max_delay))
    raise AssertionError("unreachable")

# Usage: retries 5xx / 429 / network errors, never 4xx
data = with_retry(lambda: client.get("/api/data").raise_for_status().json())
```

Mã bất đồng bộ dùng `asyncio.sleep` thay `time.sleep`. Thư viện có sẵn (ví dụ `tenacity`) dùng được nếu
dự án đã có; luật giống nhau: điều kiện retry tường minh, có trần. Với 429, ưu tiên chờ theo
`Retry-After` nếu server gửi.

## 2. Retry — TypeScript

```typescript
interface RetryOptions {
  maxAttempts?: number
  baseDelayMs?: number
  maxDelayMs?: number
  retryIf?: (error: unknown) => boolean
}

async function withRetry<T>(fn: () => Promise<T>, options: RetryOptions = {}): Promise<T> {
  const { maxAttempts = 3, baseDelayMs = 500, maxDelayMs = 10_000, retryIf = () => true } = options
  let lastError: unknown

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      if (attempt === maxAttempts || !retryIf(error)) throw error
      const jitter = Math.random() * baseDelayMs
      const delay = Math.min(baseDelayMs * 2 ** (attempt - 1) + jitter, maxDelayMs)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  throw lastError
}

// Usage: retry transient network errors, not 4xx
const data = await withRetry(() => fetch('/api/data').then(r => r.json()), {
  maxAttempts: 3,
  retryIf: (error) => !(error instanceof AppError && error.statusCode < 500),
})
```

## 3. Câu báo lỗi cho người dùng

Ánh xạ mã lỗi sang câu dễ hiểu; chi tiết kỹ thuật không bao giờ vào câu người dùng thấy.

```python
USER_ERROR_MESSAGES: dict[str, str] = {
    "NOT_FOUND": "The requested item could not be found.",
    "UNAUTHORIZED": "Please sign in to continue.",
    "FORBIDDEN": "You don't have permission to do that.",
    "VALIDATION_ERROR": "Please check your input and try again.",
    "RATE_LIMITED": "Too many requests. Please wait a moment and try again.",
    "INTERNAL_ERROR": "Something went wrong on our end. Please try again later.",
}

def get_user_message(code: str) -> str:
    return USER_ERROR_MESSAGES.get(code, USER_ERROR_MESSAGES["INTERNAL_ERROR"])
```

Bảng tra là nơi duy nhất chứa câu cho người dùng; dịch sang ngôn ngữ giao diện ở đây, không rải chuỗi
trong code.

## 4. Phân loại mã lỗi và cờ "thử lại được"

Với API có nhiều mã lỗi (hai chục mã trở lên), gán **mỗi `code` đúng một lớp** ngay trong lớp `AppError` hoặc
một bảng duy nhất — đừng để mỗi bên gọi tự đoán:

| Lớp | Ví dụ | Mã HTTP | Thử lại được? | Phía client làm gì |
|---|---|---|---|---|
| Lỗi do yêu cầu | `VALIDATION_ERROR`, `NOT_FOUND`, `FORBIDDEN` | 4xx | không | sửa yêu cầu, báo người dùng |
| Quá tải / giới hạn tốc độ | `RATE_LIMITED` | 429 | có, sau khi chờ | chờ theo `Retry-After` nếu có, nếu không backoff |
| Dependency tạm lỗi | `UPSTREAM_UNAVAILABLE`, `TIMEOUT` | 502/503/504 | có, có trần | backoff + jitter; 503 có thể kèm `Retry-After` |
| Lỗi nội bộ | `INTERNAL_ERROR` | 500 | thường không | báo người dùng, log, cảnh báo — chưa chắc thử lại sẽ khác |
| Xung đột trạng thái | `CONFLICT` | 409 | chỉ sau khi đọc lại trạng thái | đọc lại rồi quyết, không gửi y nguyên |

Đưa cờ vào phong bì (`{ error: { code, message, retryable } }`) hoặc suy ra từ bảng này một chỗ; `is_retriable`
ở mục 1 dùng chính bảng đó, không phải một danh sách khác. Thêm mã mới = thêm một dòng vào bảng, cùng với câu
trong bảng tra người dùng (mục 3). Phương thức ghi (tạo, trừ tiền) chỉ thử lại an toàn khi API có khoá bất
biến (idempotency key); không có thì không tự retry phương thức ghi.

## 5. Retry một tầng, giới hạn phía client, ngắt mạch

- **Retry ở đúng một tầng.** Mỗi tầng trong chuỗi gọi tự retry thì tải nhân lên: năm tầng, mỗi tầng ba lần
  thử, đẩy tới tầng cuối gấp 243 lần (AWS Builders' Library, "Timeouts, retries, and backoff with jitter").
  Chọn tầng gần người dùng hoặc gần dependency nhất; các tầng còn lại **không** retry mà báo lỗi lên.
- **Giới hạn tổng lượng retry** (retry budget): ngoài trần lần thử mỗi yêu cầu, giữ trần chung của tiến trình
  (ví dụ chỉ cho phép retry khi tỷ lệ retry so với yêu cầu dưới một ngưỡng, hoặc token bucket). Khi dependency
  chết, cả đội worker cùng retry sẽ đè nó thêm; trần chung chặn chuyện đó. Nhiều worker dùng chung một dependency
  thì chia sẻ trần qua nơi chung (Redis, hoặc giới hạn ở proxy/cổng) chứ không chỉ trong từng tiến trình.
- **Ngắt mạch (circuit breaker)** — khác retry: retry là "thử lại, hy vọng được"; ngắt mạch là "ngừng gọi thứ
  nhiều khả năng sẽ hỏng" (Azure Architecture Center, Circuit Breaker pattern). Ba trạng thái: **Closed**
  (gọi bình thường, đếm lỗi gần đây trong một cửa sổ thời gian) → vượt ngưỡng thì **Open** (mọi lệnh gọi hỏng
  ngay, không chạm dependency, kèm đồng hồ chờ) → hết giờ thì **Half-Open** (cho một ít lệnh gọi thử; thành công
  liên tiếp đủ số thì về Closed, một lần hỏng là về Open). Quyết định cần ghi: ngưỡng và cửa sổ đếm; lỗi nào
  được tính (timeout, 5xx — không tính 4xx); đồng hồ chờ; Open thì trả gì (lỗi rõ ràng, giá trị cache có gắn
  nhãn, hoặc đường thay thế — fallback phải nói thật là fallback, không giả như kết quả thật); phát sự kiện mỗi
  lần đổi trạng thái để theo dõi. Mỗi dependency độc lập một ngắt mạch, đừng gộp nhiều nguồn vào một.
  Retry gọi qua ngắt mạch phải dừng ngay khi ngắt mạch báo Open. Không dùng ngắt mạch thay cho xử lý lỗi nghiệp vụ,
  hay cho tài nguyên cục bộ trong tiến trình.

## 6. Hàng đợi, thông điệp độc, hàng chờ lỗi (dead-letter)

Việc chạy qua hàng đợi hay job nền không có người chờ phản hồi, nên cùng nguyên tắc nhưng khác chỗ đặt lỗi:

- **Phân lỗi thoáng qua và lỗi vĩnh viễn ở consumer.** Thoáng qua (dependency tạm lỗi, khoá bị giữ) → trả
  thông điệp về hàng đợi để thử lại sau, có backoff. Vĩnh viễn (thông điệp sai định dạng, tham chiếu một thứ không
  tồn tại, vi phạm luật nghiệp vụ) → **không** thử lại: nó sẽ hỏng y như cũ.
- **Thông điệp độc** (poison message): thông điệp nào cũng làm consumer hỏng sẽ bị giao lại mãi, chặn hàng đợi
  hoặc ăn hết tài nguyên. Chặn bằng **trần số lần nhận**: quá trần thì chuyển sang **hàng chờ lỗi**
  (dead-letter queue) thay vì giao tiếp (Amazon SQS: `maxReceiveCount` trong redrive policy).
- **Hàng chờ lỗi không phải thùng rác:** có cảnh báo khi có thông điệp rơi vào; lưu kèm lý do lỗi, số lần thử và
  ngữ cảnh (không kèm secret — mục 3 của `SKILL.md`); thời hạn lưu dài hơn hàng gốc; có đường đưa thông điệp
  về hàng gốc (redrive) sau khi sửa lỗi hoặc sửa dữ liệu.
- **Xử lý trùng lặp:** hàng đợi thường giao *ít nhất một lần* nên consumer phải idempotent (khoá khử trùng,
  hoặc thao tác ghi dùng khoá duy nhất) trước khi bật retry.
- Hàng đợi có thứ tự (FIFO) mà chuyển thông điệp sang hàng chờ lỗi sẽ làm vỡ thứ tự — cân nhắc trước khi dùng.
