# Upload multipart và phân quyền theo vai / scope

> **Kết luận:** file nhận bằng `UploadFile` + trường text bằng `Form`, đọc **theo khối có trần**, không `read()` hết.
> Giới hạn cỡ body thật sự phải đặt **trước** khi app đọc body (proxy, hoặc middleware ASGI kiểm `Content-Length`):
> FastAPI phân tích cả body multipart rồi mới chạy dependency và handler. Phân quyền theo vai là dependency có tham
> số; theo scope là `Security` + `SecurityScopes`; nút Authorize của Swagger đến từ scheme bảo mật khai trong OpenAPI.

## 1. Nhận file và trường form

Cần gói `python-multipart` cho `UploadFile` và `Form`. Body phải là `multipart/form-data` (không trộn với JSON).

```python
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, UploadFile, status

router = APIRouter()

MAX_BYTES = 5 * 1024 * 1024
CHUNK = 64 * 1024
MAGIC = {"image/png": b"\x89PNG\r\n\x1a\n", "image/jpeg": b"\xff\xd8\xff"}


@router.post("/avatar", status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile,
    caption: Annotated[str, Form(max_length=200)],
    visibility: Annotated[str, Form(pattern="^(public|private)$")] = "private",
):
    magic = MAGIC.get(file.content_type or "")
    if magic is None:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Loại file không được hỗ trợ")
    head = await file.read(len(magic))
    if head != magic:  # content_type do client tự khai: kiểm byte đầu thật
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Nội dung không khớp loại file")
    total = len(head)
    while chunk := await file.read(CHUNK):  # đọc theo khối, dừng ngay khi vượt trần
        total += len(chunk)
        if total > MAX_BYTES:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File quá lớn")
        # ghi chunk ra kho lưu trữ ở đây, không gom vào list
    return {"size": total, "caption": caption, "visibility": visibility}
```

Cách `UploadFile` hoạt động (Starlette): phần file được ghi vào file tạm kiểu spooled — **trong RAM đến 1 MB rồi chuyển
ra đĩa** — nên request lớn tốn đĩa tạm chứ không tự làm phình RAM; thứ làm phình RAM là `await file.read()` không đối số
trên cả file. Các phần **không phải file** bị giới hạn mỗi phần 1 MB (`max_part_size`), tối đa 1000 file và 1000 trường
mỗi request (`max_files`, `max_fields`); vượt thì request bị từ chối.

- Một file → `file: UploadFile`; nhiều file → `files: list[UploadFile]`. Trường form kiểm bằng `Form(...)` như
  `Query`: sai khuôn → `422`.
- `file.content_type` và `file.filename` là dữ liệu client tự khai: không tin để quyết định loại file hay đường lưu.
  Kiểm byte đầu như trên (hoặc thư viện nhận dạng loại file), sinh tên lưu riêng (UUID), không dùng `filename` làm
  đường dẫn.
- **Trần cỡ body — đặt ở đâu:** (1) tầng proxy (ví dụ `client_max_body_size` của Nginx) là chặn đầu tiên và rẻ nhất;
  (2) trong app, **dependency và handler đều chạy SAU khi body đã được đọc xong**, nên `Depends` kiểm `Content-Length`
  không ngăn được việc nhận file; kiểm ở middleware ASGI thuần:

```python
from starlette.responses import JSONResponse


class MaxContentLengthMiddleware:
    """Từ chối theo Content-Length trước khi app đọc body (không bắt được body chunked không khai độ dài)."""

    def __init__(self, app, max_bytes: int):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            raw = dict(scope["headers"]).get(b"content-length")
            if raw is not None and (not raw.isdigit() or int(raw) > self.max_bytes):
                response = JSONResponse({"error": {"code": "payload_too_large"}}, status_code=413)
                return await response(scope, receive, send)
        await self.app(scope, receive, send)


# app.add_middleware(MaxContentLengthMiddleware, max_bytes=MAX_BYTES + 64 * 1024)  # chừa chỗ cho trường form và biên
```

  Body chunked không có `Content-Length` lọt qua middleware này: trần thật cho trường hợp đó vẫn là proxy, cộng vòng đọc
  theo khối có trần ở handler (đĩa tạm vẫn bị ghi đến lúc handler dừng). Ném ngoại lệ từ hàm `receive` bọc ngoài **không**
  cho ra `413` sạch — FastAPI bắt lỗi khi phân tích body và trả `400`.
- Nhiều upload đồng thời: mỗi file lớn chiếm đĩa tạm của máy hay container đến khi request xong — tính dung lượng thư
  mục tạm theo số upload đồng thời, không chỉ theo một request.

## 2. Phân quyền theo vai và scope

**Theo vai:** một hàm dựng dependency nhận danh sách vai cho phép; route khai một dòng, không còn `if` rải rác.

```python
from typing import Annotated

from fastapi import Depends, HTTPException, status


def require_roles(*roles: str):
    async def checker(user: CurrentUser) -> User:        # CurrentUser: dependency xác thực ở app-schemas-dependencies.md mục 4
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Không đủ quyền")
        return user
    return checker


@router.get("/admin/stats")
async def stats(user: Annotated[User, Depends(require_roles("admin"))]): ...

@router.delete("/projects/{pid}")
async def delete_project(pid: int, user: Annotated[User, Depends(require_roles("admin", "manager"))]): ...
```

Chưa đăng nhập hay token hỏng → `401` (dependency xác thực), đã xác thực nhưng sai vai → `403` (dependency vai).
Vai nên lấy từ nguồn tin cậy (token đã kiểm chữ ký, hoặc đọc lại từ CSDL nếu vai đổi thường xuyên: token cũ giữ vai cũ
đến khi hết hạn).

**Theo scope:** khai các scope ở scheme, route yêu cầu scope bằng `Security(..., scopes=[...])`, dependency đọc
`SecurityScopes` để so với scope trong token.

```python
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scopes={"reports:read": "Đọc báo cáo", "reports:write": "Ghi báo cáo"},
)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    claims = decode_token(token)                        # lỗi giải mã / đổi kiểu → 401 + WWW-Authenticate
    granted = set(claims.get("scopes", []))
    for scope in security_scopes.scopes:                # gồm scope của mọi dependency trong chuỗi gọi
        if scope not in granted:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Thiếu scope {scope}")
    ...


@router.get("/reports")
async def reports(user: Annotated[User, Security(get_current_user, scopes=["reports:read"])]): ...
```

Khi cấp token (`/login`), đặt `scopes` (hoặc claim `scope` theo chuẩn OAuth2: chuỗi cách nhau bởi dấu cách) theo vai của
người dùng; scope là **quyền cụ thể**, vai là **nhóm quyền** — dùng vai cho phân quyền thô, scope khi cần quyền hẹp.

**Vì sao Swagger hiện nút Authorize:** `OAuth2PasswordBearer` (hay `HTTPBearer`, `APIKeyHeader`…) khi nằm trong chuỗi
`Depends` của một route thì FastAPI khai scheme đó vào `components.securitySchemes` của OpenAPI, và route ghi mục
`security` tương ứng (kèm danh sách scope của `Security`). Swagger UI đọc chỗ đó để hiện nút Authorize, ô nhập
thông tin đăng nhập (với `OAuth2PasswordBearer`, form gọi `tokenUrl`) và biểu tượng khoá ở từng route. Dependency vai
chỉ gọi lại `CurrentUser` cũng đủ để route hiện khoá. Cần `tokenUrl` trỏ đúng route đăng nhập nhận form
`username`/`password` (`OAuth2PasswordRequestForm`), nếu không nút Authorize hiện nhưng đăng nhập từ Swagger lỗi.

## Nguồn

Tài liệu chính thức của FastAPI (Request Files, Form Data, Security — OAuth2 scopes, Bigger Applications) và Starlette
(`UploadFile`, `request.form`, middleware ASGI); đã chạy lại các mẫu trên FastAPI 0.135 / Starlette 0.52 bằng client
ASGI để xác nhận mã trạng thái và thứ tự dependency–body.
