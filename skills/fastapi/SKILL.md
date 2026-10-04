---
name: fastapi
description: Use when building, extending, or reviewing a FastAPI service — routers, Pydantic request and response schemas, dependency injection, async endpoints calling a database or external service, background tasks, streaming responses, authentication and authorization, error envelopes, OpenAPI docs, tests with dependency overrides, or production settings.
metadata:
  group: technique
  kind: reference
  roles: [implementer, tech-reviewer]
source: affaan-m/ECC skills/fastapi-patterns/SKILL.md
source_sha: ef648e01899ba3e8dc6371642deaaf64b4477775
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: MIT
rewrite_before_public: false
---

# FastAPI — mẫu cho dịch vụ chạy production

> **Kết luận:** coi app FastAPI là **lớp HTTP mỏng**: route nhận, kiểm, gọi service, trả; tài nguyên theo
> request đi qua `Depends`; schema tạo / cập nhật / phản hồi tách riêng và **luôn** có `response_model`;
> handler `async def` chỉ gọi thư viện async; token hỏng hay thiếu trường là `401`, không bao giờ là `500`;
> ràng buộc duy nhất nằm ở CSDL, không ở câu kiểm trước. Test ghi đè **đúng** dependency mà route dùng.

## 1. Khi nào dùng — và khi nào sang skill khác

- Dựng hoặc review app FastAPI; tách router, schema, dependency, truy cập CSDL; endpoint async gọi CSDL hay
  dịch vụ ngoài; xác thực, phân quyền, OpenAPI, test, cấu hình triển khai.
- Hình URL, mã trạng thái, phong bì lỗi, phân trang, đổi hợp đồng → skill `api-design` (skill này chỉ cài).
- Python chung (kiểu, idiom, pytest) → skill `python`. Schema bảng, index, migration → `postgres`,
  `database-migrations`. Đóng gói, probe, deploy → `deployment`.

## 2. Chia trách nhiệm

| Thành phần | Sở hữu | Không chứa |
|---|---|---|
| `main.py` | `create_app()`, `lifespan`, middleware, exception handler, đăng ký router | nghiệp vụ, tạo bảng |
| `config.py` | cấu hình từ biến môi trường (pydantic-settings) | giá trị secret mặc định |
| `schemas/` | model Pydantic vào và ra | đối tượng ORM |
| `dependencies.py` | phiên CSDL, người dùng hiện tại, phân quyền, phân trang | logic nghiệp vụ |
| `services/` | nghiệp vụ, ranh giới transaction, dịch lỗi ràng buộc CSDL sang lỗi miền | `HTTPException` |
| `tests/` | ghi đè dependency, client ASGI | kết nối tới tài nguyên production |

```text
app/
|-- main.py  config.py  dependencies.py  exceptions.py
|-- api/routes/        users.py, health.py
|-- core/              security.py, middleware.py
|-- db/                session.py
|-- models/  schemas/  services/
`-- tests/
```

## 3. Luật then chốt

- **Khởi tạo:** `create_app()` với `lifespan` mở và đóng tài nguyên dùng chung (pool CSDL, client HTTP).
  `lifespan` **không** tạo bảng — schema đi qua migration (skill `database-migrations`); tạo bảng lúc khởi động
  chỉ chấp nhận ở bản demo.
- **CORS:** nguồn theo từng môi trường; **không bao giờ** `allow_origins=["*"]` cùng `allow_credentials=True`.
- **Cấu hình:** pydantic-settings đọc biến môi trường; secret là trường bắt buộc không có mặc định; `.env`
  không commit, repo chỉ có `.env.example`.
- **Schema:** tách `…Create` / `…Update` / `…Response`; kiểm chéo trường bằng validator sau khi dựng model;
  cập nhật từng phần bằng `model_dump(exclude_unset=True)`; response không bao giờ có hash mật khẩu, token hay
  cờ phân quyền nội bộ.
- **Dependency:** gom bằng bí danh kiểu (`DbDep = Annotated[AsyncSession, Depends(get_db)]`); không tạo phiên,
  client hay credential trong handler.
- **Xác thực:** giải mã token với danh sách thuật toán cố định, kiểm hạn, issuer, audience; trường `sub` có thể
  thiếu hay sai kiểu (chuỗi ↔ số, UUID hỏng) — bắt mọi lỗi giải mã **và** lỗi đổi kiểu, trả `401` kèm
  `WWW-Authenticate`. Phân quyền là dependency riêng nhận người dùng đã xác thực, trả `403`.
- **Async:** `async def` chỉ dùng thư viện async (`httpx.AsyncClient`, SQLAlchemy async). Buộc phải dùng thư
  viện đồng bộ → khai route bằng `def` thường (FastAPI chạy nó trong threadpool) hoặc bọc lời gọi chặn; không
  bao giờ gọi chặn trực tiếp trong `async def`.
- **Tác vụ nền và luồng:** `BackgroundTasks` chỉ cho việc nhẹ chạy sau response, cùng tiến trình, mất được —
  đăng ký **sau** commit, truyền giá trị thuần, không dùng lại phiên CSDL của request; việc nặng hay không được
  mất → hàng đợi riêng + `202` kèm mã việc. Response dài trả bằng generator `async` qua `StreamingResponse`, kiểm
  quyền và tham số **trước** `yield` đầu (`references/background-and-streaming.md`).
- **Service và transaction:** route mỏng; service giữ transaction, bắt `IntegrityError` rồi ném lỗi miền.
  Trùng dữ liệu dựa vào **ràng buộc unique của CSDL** — truy vấn kiểm trước rồi chèn là đua; route dịch lỗi
  trùng thành `409` (skill `api-design`).
- **Lỗi:** một lớp lỗi miền + exception handler đăng ký tập trung giữ ổn định phong bì
  `{ error: { code, message } }`; không để stack trace hay câu SQL lọt ra response.
- **Phân trang:** offset/limit có giới hạn trên (`Query(le=…)`) và `ORDER BY` xác định (ví dụ theo khoá
  chính) để không sót hay lặp dòng giữa các trang.
- **OpenAPI:** tuỳ biến bằng cách **gán** hàm vào `app.openapi`; khai response lỗi cho từng route.
- **Test:** ghi đè đúng hàm mà `Depends` tham chiếu (ví dụ `get_db`), xoá ghi đè sau mỗi test; test qua client
  ASGI, không mở cổng thật.

## 4. Lỗi hay gặp khi viết và review

Mức gợi ý theo hậu quả nếu bỏ qua (`method/severity.md` mục 1); review sâu: agent `fastapi-reviewer`.

| Dấu hiệu | Hậu quả | Mức gợi ý |
|---|---|---|
| Secret, token viết cứng; SQL dựng bằng f-string hay nối chuỗi | lộ secret, SQL injection | Chặn |
| Response trả đối tượng ORM thô hay model có hash mật khẩu, token | lộ dữ liệu xác thực | Chặn |
| Dependency xác thực bỏ qua được, không kiểm chữ ký hay hạn | ai cũng vào được | Chặn |
| `allow_origins=["*"]` cùng `allow_credentials=True` | Starlette trả lại đúng `Origin` của request kèm credentials (cả preflight) → trang web nào cũng đọc được response đã đăng nhập | Chặn |
| Đổi kiểu `sub` không bọc lỗi → `500` thay vì `401` | token rác làm lỗi máy chủ, nhiễu giám sát | Phải sửa |
| Việc nặng hay không được mất chạy bằng `BackgroundTasks`; truyền phiên CSDL của request vào việc nền | việc mất khi tiến trình chết, phiên đã đóng, lỗi chỉ hiện ở log | Phải sửa |
| Gọi CSDL hay HTTP đồng bộ trong `async def` | một request chậm chặn cả vòng sự kiện | Phải sửa |
| Kiểm trùng bằng truy vấn trước, không có ràng buộc unique | hai request cùng lúc tạo bản trùng | Phải sửa |
| Ghi đè test nhắm sai dependency | test xanh mà không kiểm gì | Phải sửa |
| Phân trang offset không `ORDER BY` hay không trần `limit` | trang sót, lặp dòng; một request kéo cả bảng | Phải sửa |
| Client HTTP ngoài không timeout | request treo tới khi hết worker | Nên sửa (Phải sửa nếu là đường găng) |
| Route chứa nghiệp vụ, lặp giữa các route | khó test, sửa một chỗ quên chỗ kia | Nên sửa |
| OpenAPI thiếu response model hay response lỗi | bên dùng sinh client sai | Nên sửa |

## 5. Đọc gì khi nào

| Cần | Đọc |
|---|---|
| `create_app` + lifespan + CORS, cấu hình pydantic-settings, tách schema Pydantic, dependency `get_db` / `get_current_user` | `references/app-schemas-dependencies.md` |
| Tác vụ nền (`BackgroundTasks` hay hàng đợi), endpoint `202` cho việc dài, `StreamingResponse`, SSE | `references/background-and-streaming.md` |
| Endpoint async có phân trang, tầng service + transaction, lớp lỗi + exception handler (kể cả lỗi validate/framework, request id), tuỳ biến `app.openapi`, `operation_id`/tag/ví dụ, dependency đọc header (tenant), fixture test ghi đè dependency, phản mẫu | `references/routes-errors-openapi-testing.md` |

## 6. Checklist bảo mật

- [ ] Băm mật khẩu bằng `argon2-cffi`, `bcrypt` hoặc bộ băm hiện hành tương thích passlib
- [ ] Token: thuật toán cố định, kiểm hạn, issuer, audience; lỗi đổi kiểu trường trả `401`
- [ ] CORS theo từng môi trường; rate limit cho endpoint xác thực và endpoint ghi nhiều
- [ ] Mọi body request đi qua model Pydantic; mọi response có `response_model`
- [ ] Truy vấn bằng tham số ràng buộc của ORM hay SQLAlchemy Core; **không bao giờ** f-string
- [ ] Che token, header `Authorization`, cookie, mật khẩu khỏi log
- [ ] Audit phụ thuộc trong CI
- [ ] Chạm xác thực, đầu vào ngoài, API công khai → kéo skill `security-review` và agent `security-reviewer`

## 7. Checklist hiệu năng

- [ ] Pool kết nối CSDL cấu hình tường minh, đóng trong `lifespan`
- [ ] Endpoint danh sách luôn phân trang, có trần
- [ ] Canh truy vấn N+1; eager loading có chủ đích
- [ ] Đường async dùng client HTTP, CSDL async; client dùng chung, không tạo mới mỗi request
- [ ] Chỉ bật nén sau khi đo cỡ payload và chi phí CPU
- [ ] Cache đọc ổn định và đắt, có cách vô hiệu hoá tường minh

## 8. Xem thêm

- Agent reviewer: `fastapi-reviewer`; thêm `security-reviewer` khi chạm xác thực, secret; `database-reviewer`
  khi đổi schema hay truy vấn; `python-reviewer` cho Python chung.
- Skill: `python` (gồm pytest), `tdd`, `api-design`, `error-handling`, `postgres`, `database-migrations`,
  `security-review`, `deployment`.
