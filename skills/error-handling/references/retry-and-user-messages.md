# Retry có backoff và câu báo lỗi cho người dùng

> **Kết luận:** retry chỉ lỗi thoáng qua (5xx, timeout, mất kết nối), backoff mũ cộng jitter, có trần lần
> thử và trần độ trễ; hết lượt thì ném lỗi cuối cùng, không nuốt. Câu cho người dùng lấy từ **một** bảng
> tra theo mã lỗi, mã lạ rơi về câu lỗi chung.

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
