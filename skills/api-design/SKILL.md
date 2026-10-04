---
name: api-design
description: Use when designing, changing or reviewing a REST endpoint or its contract — resource URLs, HTTP methods, status codes, response or error envelopes, pagination, filtering, auth, rate limits, versioning, safe retries, optimistic locking, file upload — or when a SPEC must list an API change and its consumers.
metadata:
  group: technique
  kind: reference
  roles: [architect, implementer, tech-reviewer]
source: affaan-m/ECC skills/api-design/SKILL.md
source_sha: c70874fae9eb0e5ad0365beb7e2955899fd1d30f
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: MIT
rewrite_before_public: false
---

# Thiết kế API REST

> **Kết luận:** URL là **danh từ số nhiều, kebab-case**; phương thức đúng ngữ nghĩa; mã trạng thái nói
> thật (không 200 cho mọi thứ); lỗi theo một phong bì `{ error: { code, message, details? } }`. API là
> **hợp đồng**: trước khi đổi, liệt kê bên dùng và delta thêm / sửa / bỏ; thay đổi phá vỡ cần phiên bản
> mới và ADR.

## 1. Thiết kế tài nguyên

```
# Resources are nouns, plural, lowercase, kebab-case
GET    /api/v1/customers
GET    /api/v1/customers/:id
POST   /api/v1/customers
PUT    /api/v1/customers/:id
PATCH  /api/v1/customers/:id
DELETE /api/v1/customers/:id

# Sub-resources for relationships
GET    /api/v1/customers/:id/orders
POST   /api/v1/customers/:id/orders

# Actions that don't map to CRUD (use verbs sparingly)
POST   /api/v1/orders/:id/cancel
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
```

```
# GOOD
/api/v1/team-members          # kebab-case for multi-word resources
/api/v1/orders?status=active  # query params for filtering
/api/v1/customers/123/orders      # nested resources for ownership

# BAD
/api/v1/getCustomers              # verb in URL
/api/v1/customer                  # singular
/api/v1/team_members          # snake_case in URL
/api/v1/customers/123/getOrders   # verb in nested resource
```

## 2. Phương thức và mã trạng thái

| Phương thức | Idempotent | An toàn | Dùng cho |
|---|---|---|---|
| `GET` | có | có | đọc tài nguyên |
| `POST` | không | không | tạo tài nguyên, kích hoạt hành động |
| `PUT` | có | không | thay toàn bộ tài nguyên |
| `PATCH` | không (làm được idempotent nếu cài đúng) | không | sửa một phần |
| `DELETE` | có | không | xoá tài nguyên |

```
# Success
200 OK                    — GET, PUT, PATCH (with body)
201 Created               — POST (include Location header)
204 No Content            — DELETE, PUT (no body)

# Client errors
400 Bad Request           — validation failure, malformed JSON
401 Unauthorized          — missing or invalid authentication
403 Forbidden             — authenticated but not authorized
404 Not Found             — resource does not exist
409 Conflict              — duplicate entry, state conflict
412 Precondition Failed   — If-Match / ETag no longer matches (lost-update guard)
413 Content Too Large     — upload over the size limit
415 Unsupported Media Type — file or body type not allowed
422 Unprocessable Entity  — valid JSON, semantically invalid data
428 Precondition Required — endpoint requires If-Match and the client sent none
429 Too Many Requests     — rate limit exceeded

# Server errors
500 Internal Server Error — unexpected failure (never expose details)
502 Bad Gateway           — upstream service failed
503 Service Unavailable   — temporary overload, include Retry-After
```

`POST` không idempotent nên client thử lại sau khi hết thời gian chờ có thể tạo trùng: endpoint tạo tiền/đơn/tin nhắn nhận `Idempotency-Key`
(`references/retries-concurrency-files.md` mục 1). Hai người sửa cùng bản ghi: `ETag` + `If-Match`, lệch → `412` (mục 2 của tệp đó).

Lỗi hay gặp:

```
# BAD: 200 for everything
{ "status": 200, "success": false, "error": "Not found" }

# GOOD: semantic status code
HTTP/1.1 404 Not Found
{ "error": { "code": "not_found", "message": "Customer not found" } }

# BAD: 500 for validation errors   → GOOD: 400 or 422 with field-level details
# BAD: 200 for created resources   → GOOD: 201 with Location header
HTTP/1.1 201 Created
Location: /api/v1/customers/abc-123
```

## 3. Đổi hợp đồng: liệt kê bên dùng trước khi đổi

Đổi API (thêm, sửa, bỏ endpoint, trường, mã lỗi, cách xác thực) là đổi hợp đồng. Mục **"Đổi hợp đồng /
giao diện"** của SPEC bắt buộc khi cỡ lớn hoặc `risk_tags` có `public_api`; cỡ khác xoá mục và ghi thay đổi
ít nhất một dòng trong SPEC hoặc PLAN.

1. **Liệt kê bên dùng** có bằng chứng: grep bên gọi trong repo, client sinh từ OpenAPI, log truy cập.
   "Không ai dùng" mà không có bằng chứng thì coi như có người dùng.
2. **Ghi delta** theo bảng: thay đổi · thêm / sửa / bỏ · bên dùng bị ảnh hưởng · tương thích ngược? ·
   phiên bản / giai đoạn chuyển.
3. **Phân loại**: thêm trường vào response, thêm tham số tuỳ chọn, thêm endpoint → không phá vỡ, không cần
   phiên bản mới. Bỏ hoặc đổi tên trường, đổi kiểu, đổi cấu trúc URL, đổi cách xác thực → **phá vỡ**: cần
   phiên bản mới hoặc giai đoạn chuyển có `Sunset`, và một ADR (skill `adr`).
4. Cập nhật tài liệu API (OpenAPI hoặc tương đương) **trong cùng thay đổi**.

Thay đổi làm gãy bên dùng mà không có phiên bản hoặc giai đoạn chuyển là phát hiện mức **Chặn**.

## 4. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Phong bì thành công / danh sách / lỗi; phân trang offset và cursor (SQL, đánh đổi, bảng chọn); lọc, sắp xếp, tìm kiếm, chọn trường | `references/responses-pagination-filtering.md` |
| Xác thực bằng bearer / API key, kiểm quyền sở hữu và vai; header và bậc rate limit; phiên bản qua URL hay header, lộ trình ngừng hỗ trợ | `references/auth-ratelimit-versioning.md` |
| Thử lại an toàn cho `POST` (`Idempotency-Key`); khoá lạc quan `ETag` + `If-Match` (`412`, `428`); `If-None-Match`/`304` cho client thăm dò; upload và tải tệp (multipart, URL ký sẵn, `413`, `415`, kiểm quyền lúc tải) | `references/retries-concurrency-files.md` |
| Endpoint hoàn chỉnh: TypeScript (Next.js + Zod), Python (DRF), Go (net/http) | `references/implementation-examples.md` |

Liên quan: skill `fastapi` (cài endpoint bằng FastAPI), `error-handling` (phân cấp lỗi, ánh xạ lỗi sang
phong bì), `security-review` (bề mặt tấn công mới), `database-migrations` (đổi schema đi kèm đổi API).

## 5. Danh mục kiểm trước khi ra endpoint

- [ ] URL theo quy ước (số nhiều, kebab-case, không động từ)
- [ ] Phương thức đúng ngữ nghĩa
- [ ] Mã trạng thái đúng (không 200 cho mọi thứ)
- [ ] Đầu vào kiểm bằng schema (Pydantic, Zod, Bean Validation)
- [ ] Lỗi theo phong bì chuẩn, có `code` và `message`
- [ ] Endpoint danh sách có phân trang (cursor hoặc offset)
- [ ] Bắt buộc xác thực, hoặc ghi rõ là công khai
- [ ] Kiểm quyền: người dùng chỉ chạm tài nguyên của mình
- [ ] Có rate limit
- [ ] Endpoint tạo có hậu quả (tiền, đơn, tin nhắn) nhận khoá chống trùng; endpoint nhiều người sửa có `ETag`/`If-Match`
- [ ] Endpoint nhận tệp: giới hạn kích thước và loại (`413`, `415`), tên tệp do server đặt, kiểm quyền lúc tải
- [ ] Response không lộ nội bộ (stack trace, lỗi SQL, chuỗi kết nối)
- [ ] Đặt tên trường nhất quán với endpoint có sẵn (camelCase hay snake_case)
- [ ] Đổi hợp đồng đã liệt kê bên dùng và delta (mục 3)
- [ ] Tài liệu API (OpenAPI) đã cập nhật
