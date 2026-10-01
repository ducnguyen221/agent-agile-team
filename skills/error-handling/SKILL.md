---
name: error-handling
description: Use when designing error types or exception hierarchies, mapping errors to API responses, adding retry or backoff around an unreliable dependency, writing user-facing error messages, logging an exception, or reviewing code for swallowed errors, bad fallbacks or cascading failures.
metadata:
  group: technique
  kind: reference
  roles: [implementer, tech-reviewer]
source: affaan-m/ECC skills/error-handling/SKILL.md
source_sha: c70874fae9eb0e5ad0365beb7e2955899fd1d30f
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: MIT
rewrite_before_public: false
---

# Xử lý lỗi

> **Kết luận:** lỗi là giá trị có cấu trúc (`code` + mã HTTP), không phải chuỗi; hỏng thì báo to tại chỗ
> hỏng, không nuốt. Một chỗ duy nhất ở biên HTTP ánh xạ lỗi sang phong bì `{ error: { code, message } }`.
> Người dùng thấy câu thân thiện; log giữ ngữ cảnh — nhưng **không** đưa nguyên chuỗi lỗi của HTTP client
> hay DB ra log hay người dùng, vì nó có thể chứa URL kèm token hoặc mật khẩu.

## 1. Năm nguyên tắc

1. **Hỏng sớm, hỏng to** — báo lỗi ở biên nơi nó xảy ra; không chôn.
2. **Lỗi có kiểu hơn chuỗi** — lỗi là giá trị hạng nhất, có `code`, mã HTTP, `details` tuỳ chọn.
3. **Thông điệp người dùng khác thông điệp kỹ thuật** — người dùng đọc câu thân thiện; chi tiết ở log
   phía server.
4. **Không bao giờ nuốt lỗi im lặng** — mỗi khối `except`/`catch` phải xử lý, ném lại, hoặc log.
5. **Lỗi là một phần hợp đồng API** — mọi mã lỗi client có thể nhận đều được ghi tài liệu (skill
   `api-design`).

## 2. Mẫu lõi

- Phân cấp lỗi miền trên một lớp gốc `AppError` mang `code` + `status_code` (+ `details`).
- Thao tác hỏng thường xuyên (phân tích cú pháp, gọi ngoài) có thể trả kiểu `Result` thay vì ném.
- **Một** handler ở biên HTTP: lỗi đã biết → phong bì chuẩn; lỗi lạ → log rồi trả 500 chung chung.
- Bọc tầng hiển thị: handler toàn cục (FastAPI) hoặc error boundary (React).
- Chỉ retry lỗi **thoáng qua** (5xx, mạng chập chờn), backoff mũ + jitter, có trần lần thử; **không bao
  giờ** retry 4xx.
- Dịch mã lỗi sang câu cho người dùng qua **một** bảng tra.

```python
class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 500):
        super().__init__(message)
        self.code = code
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} not found: {id}", "NOT_FOUND", 404)
```

## 3. Lỗi không được làm lộ secret

Thông điệp của lỗi HTTP client (httpx, requests, aiohttp) và driver DB thường chứa **URL đầy đủ** — kể cả
query string có `?key=`/`?token=` — hoặc **chuỗi kết nối** có mật khẩu. `str(exc)` của chúng vì thế là
dữ liệu nhạy cảm.

- Không trả `str(exc)` của lỗi hạ tầng cho người dùng; không ghi nguyên `str(exc)` vào log.
- Log **loại lỗi + mã** (mã HTTP, mã lỗi DB, tên host không kèm thông tin đăng nhập); nếu buộc phải ghi
  thông điệp thì cho qua hàm che trước.
- Đặt khoá ở header thay vì query string để URL trong lỗi không mang secret ngay từ đầu.
- Che ở **mọi** biên: log, phong bì lỗi, thông điệp ném lại, báo cáo gửi về dịch vụ theo dõi lỗi.

```python
import re

_SENSITIVE = re.compile(
    r"(?i)((?:key|token|secret|password|passwd|sig|signature)=)[^&\s]+"  # query params
    r"|(//[^/\s:@]+:)[^/\s@]+(@)"                                          # user:pass@host
)

def redact(text: str) -> str:
    return _SENSITIVE.sub(lambda m: (m.group(1) or m.group(2)) + "***" + (m.group(3) or ""), text)

try:
    resp = client.get(url, headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
except httpx.HTTPStatusError as exc:
    logger.error("upstream_error", extra={"type": type(exc).__name__,
                                          "status": exc.response.status_code})
    raise AppError("Upstream service failed", "UPSTREAM_ERROR", 502) from None
except httpx.HTTPError as exc:
    logger.error("upstream_unreachable", extra={"type": type(exc).__name__,
                                                "detail": redact(str(exc))})
    raise AppError("Upstream service unavailable", "UPSTREAM_UNAVAILABLE", 503) from None
```

Secret lọt vào log hay response là phát hiện mức **Chặn**; báo để xoay vòng khoá (skill `security-review`).

## 4. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Python: phân cấp ngoại lệ + handler toàn cục FastAPI; Go: lỗi sentinel, bọc `%w`, `errors.Is` ở handler | `references/python-go-patterns.md` |
| Retry có backoff + jitter + điều kiện retry (Python và TypeScript); bảng tra câu báo lỗi cho người dùng | `references/retry-and-user-messages.md` |
| TypeScript: lớp `AppError` (bẫy prototype chain), kiểu `Result`, handler lỗi Next.js/Express có `ZodError`, React `ErrorBoundary` | `references/typescript-patterns.md` |

Liên quan: skill `python`, `fastapi`, `api-design`, `debugging` (truy lỗi lan tầng). Rà lỗi nuốt im lặng,
fallback sai, lỗi không lan lên bên gọi: giao agent `silent-failure-hunter`.

## 5. Danh mục kiểm trước khi gộp

- [ ] Mọi `except`/`catch` xử lý, ném lại, hoặc log — không nuốt im lặng; không `except:` trần
- [ ] Lỗi API theo phong bì chuẩn `{ error: { code, message } }`
- [ ] Thông điệp cho người dùng không có stack trace hay chi tiết nội bộ
- [ ] Log phía server có đủ ngữ cảnh (loại lỗi, mã, định danh yêu cầu) — **không** có `str(exc)` thô
      của HTTP client/DB, không có token, mật khẩu, chuỗi kết nối
- [ ] Lớp lỗi riêng kế thừa một `AppError` có trường `code`
- [ ] Hàm bất đồng bộ đưa lỗi lên bên gọi — không "bắn rồi quên" khi không có fallback
- [ ] Retry chỉ cho lỗi thoáng qua, có trần lần thử; không retry 4xx
- [ ] Ném lại giữ nguyên nhân (`raise ... from exc`) trừ khi nguyên nhân chứa secret (`from None` + log đã che)
- [ ] Giao diện React được bọc `ErrorBoundary` cho lỗi hiển thị
