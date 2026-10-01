# Mẫu xử lý lỗi Python và Go

> **Kết luận:** Python dùng phân cấp ngoại lệ trên `AppError` và hai handler toàn cục ở FastAPI (lỗi đã
> biết → phong bì; lỗi lạ → log loại lỗi rồi 500). Go dùng lỗi sentinel, bọc bằng `%w` để không mất lỗi
> gốc, và `errors.Is` ở handler để chọn mã HTTP.

## 1. Python

### Phân cấp ngoại lệ

```python
class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, code: str, status_code: int = 500):
        super().__init__(message)
        self.code = code
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} not found: {id}", "NOT_FOUND", 404)

class ValidationError(AppError):
    def __init__(self, message: str, details: list[dict] | None = None):
        super().__init__(message, "VALIDATION_ERROR", 422)
        self.details = details or []
```

### Handler toàn cục FastAPI

```python
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
app = FastAPI()

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    # AppError messages are written by us for clients — safe to return.
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": str(exc)}},
    )

@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Unknown error: log type + route, never the raw message (may hold URLs with tokens).
    logger.error(
        "unexpected_error",
        extra={"type": type(exc).__name__, "path": request.url.path},
    )
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )
```

Chỉ `AppError` (thông điệp do mình viết) được trả nguyên cho client. Cần traceback để debug thì ghi ở
mức debug sau khi đã che (hàm `redact` trong SKILL mục 3), hoặc bật có chủ đích ở môi trường không phải
production. Chi tiết cài FastAPI: skill `fastapi`.

## 2. Go

### Lỗi sentinel và bọc lỗi

```go
package domain

import "errors"

// Sentinel errors for type-checking
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
    ErrConflict     = errors.New("conflict")
)

// Wrap errors with context — never lose the original
func (r *UserRepository) FindByID(ctx context.Context, id string) (*User, error) {
    user, err := r.db.QueryRow(ctx, "SELECT * FROM users WHERE id = $1", id)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, fmt.Errorf("user %s: %w", id, ErrNotFound)
    }
    if err != nil {
        return nil, fmt.Errorf("querying user %s: %w", id, err)
    }
    return user, nil
}
```

### Chọn mã HTTP ở handler

```go
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.GetUser(r.Context(), chi.URLParam(r, "id"))
    if err != nil {
        switch {
        case errors.Is(err, domain.ErrNotFound):
            writeError(w, http.StatusNotFound, "not_found", "User not found")
        case errors.Is(err, domain.ErrUnauthorized):
            writeError(w, http.StatusForbidden, "forbidden", "Access denied")
        default:
            // redact masks tokens / passwords in the wrapped chain (same rule as SKILL section 3)
            slog.Error("unexpected error", "op", "GetUser", "err", redact(err.Error()))
            writeError(w, http.StatusInternalServerError, "internal_error", "An unexpected error occurred")
        }
        return
    }
    writeJSON(w, http.StatusOK, user)
}
```

Thông điệp trả client là câu cố định, không phải `err.Error()`: chuỗi lỗi bọc nhiều tầng có thể mang chi
tiết nội bộ hoặc chuỗi kết nối.
