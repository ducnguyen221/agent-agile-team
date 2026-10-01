---
name: fastapi
description: Use when building, extending, or reviewing a FastAPI service — routers, Pydantic request and response schemas, dependency injection, async endpoints calling a database or external service, authentication and authorization, error envelopes, OpenAPI docs, tests with dependency overrides, or production settings.
metadata:
  group: technique
  roles: [implementer, tech-reviewer]
source: affaan-m/ECC skills/fastapi-patterns/SKILL.md
source_sha: c70874fae9eb0e5ad0365beb7e2955899fd1d30f
license: MIT
rewrite_before_public: false
---

# FastAPI — mẫu cho dịch vụ chạy production

> **Kết luận:** coi app FastAPI là **lớp HTTP mỏng** trên dependency tường minh và tầng service: route
> chỉ nhận/trả và gọi service; tài nguyên theo request đi qua `Depends`; schema vào/ra tách riêng và
> **luôn** có `response_model`. Handler async chỉ dùng thư viện async. Test ghi đè đúng dependency mà
> route dùng. Code mẫu đầy đủ nằm trong `references/`.

## 1. Khi nào dùng

- Dựng hoặc review app FastAPI; tách router, schema, dependency, truy cập DB.
- Viết endpoint async gọi DB hay dịch vụ ngoài.
- Thêm xác thực, phân quyền, tài liệu OpenAPI, test, cấu hình triển khai.
- Soát PR FastAPI tìm rủi ro production.

## 2. Chia trách nhiệm

| Thành phần | Sở hữu |
|---|---|
| `main.py` | dựng app (`create_app()`), middleware, exception handler, đăng ký router |
| `config.py` | cấu hình đọc từ biến môi trường (pydantic-settings) |
| `schemas/` | model Pydantic cho request và response |
| `dependencies.py` | DB session, người dùng hiện tại, phân trang, dependency theo request |
| `services/` hoặc `crud/` | nghiệp vụ và transaction; bắt lỗi ràng buộc DB |
| `tests/` | ghi đè dependency thay vì mở tài nguyên production |

Router nhỏ, `response_model` khai báo tường minh. Không trả thẳng đối tượng ORM thô, secret hay biến
toàn cục của framework ra response.

## 3. Bố cục dự án

```text
app/
|-- main.py
|-- config.py
|-- dependencies.py
|-- exceptions.py
|-- api/
|   `-- routes/
|       |-- users.py
|       `-- health.py
|-- core/
|   |-- security.py
|   `-- middleware.py
|-- db/
|   |-- session.py
|   `-- crud.py
|-- models/
|-- schemas/
|-- services/
`-- tests/
```

## 4. Luật then chốt

- Dựng app trong `create_app()` với `lifespan` cho khởi động/tắt. **Không bao giờ** `allow_origins=["*"]`
  cùng `allow_credentials=True`.
- Cấu hình từ biến môi trường qua `pydantic-settings`; secret không có giá trị mặc định trong code, file
  `.env` không commit.
- Tách `UserCreate` / `UserUpdate` / `UserResponse`; response không bao giờ lộ hash mật khẩu hay token.
- Tài nguyên theo request (`get_db`, `get_current_user`) tiêm qua `Depends`; không tạo session hay client
  ngay trong handler. Gom bằng bí danh kiểu: `DbDep = Annotated[AsyncSession, Depends(get_db)]`.
- Route mỏng, nghiệp vụ và transaction ở tầng service. Trùng lặp dữ liệu: dựa vào **ràng buộc unique
  của DB** rồi bắt `IntegrityError`, không kiểm trước bằng truy vấn (dễ đua).
- Handler async chỉ dùng thư viện async (`httpx.AsyncClient`, SQLAlchemy async) — không `requests`, không
  `Session` đồng bộ trong route async.
- Một `ApiError` + exception handler đăng ký tập trung giữ ổn định vỏ lỗi `{ error: { code, message } }`.
- Endpoint phân trang offset/limit luôn có `ORDER BY` xác định (ví dụ theo id) để không sót/lặp dòng.
- Tách kiểm tra phân quyền khỏi dependency xác thực để trả đúng `401` (chưa xác thực) và `403` (không
  có quyền).
- OpenAPI tuỳ biến: **gán** hàm vào `app.openapi`, không gọi một lần.
- Test ghi đè **đúng** dependency mà `Depends` tham chiếu (ví dụ `get_db`) và xoá ghi đè sau test.

## 5. Đọc gì khi nào

| Cần | Đọc |
|---|---|
| `create_app` + lifespan + CORS, cấu hình pydantic-settings, tách schema Pydantic, dependency `get_db` / `get_current_user` | `references/app-schemas-dependencies.md` |
| Endpoint async có phân trang, tầng service + transaction, `ApiError` + exception handler, tuỳ biến `app.openapi`, fixture test ghi đè dependency, phản mẫu | `references/routes-errors-openapi-testing.md` |

## 6. Checklist bảo mật

- Băm mật khẩu bằng `argon2-cffi`, `bcrypt` hoặc bộ băm hiện hành tương thích passlib.
- Kiểm JWT đủ issuer, audience, hạn dùng và thuật toán ký (cố định danh sách thuật toán).
- Nguồn CORS theo từng môi trường.
- Giới hạn tần suất cho endpoint xác thực và endpoint ghi nhiều.
- Mọi body request đi qua model Pydantic.
- Truy vấn bằng tham số ràng buộc của ORM hoặc biểu thức SQLAlchemy Core; **không bao giờ** dựng SQL
  bằng f-string.
- Che token, header `Authorization`, cookie, mật khẩu khỏi log.
- Chạy audit phụ thuộc trong CI.
- Chạm xác thực, input ngoài, API công khai → kéo skill `security-review`.

## 7. Checklist hiệu năng

- Cấu hình connection pool của DB tường minh.
- Endpoint danh sách luôn phân trang.
- Canh truy vấn N+1; eager loading có chủ đích.
- Đường async dùng client HTTP/DB async.
- Chỉ bật nén sau khi xem cỡ payload và chi phí CPU.
- Cache đọc ổn định và đắt, có cơ chế vô hiệu hoá tường minh.

## 8. Xem thêm

- Agent reviewer: `fastapi-reviewer`; thêm `security-reviewer` khi chạm xác thực/secret, `database-reviewer`
  khi đổi schema/truy vấn.
- Skill: `python` (gồm kiểm thử pytest), `tdd`, `api-design`, `error-handling`, `postgres`,
  `database-migrations`, `security-review`, `deployment`.
