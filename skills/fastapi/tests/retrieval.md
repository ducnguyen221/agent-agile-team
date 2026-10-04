---
skill: fastapi
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: e1152e8f4b4e34626b96a26e17510512b95a9dc6
date: 2026-10-04
result: "strict 7/7 (+0 partial, 0 fail) — at threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 7/7"
agent_ids:
  questions: "bộ câu cũ giữ nguyên, không soạn mới"
  answers: a41c8365a9a6d1dd6
---

Đã đọc: `<gốc worktree>/skills/fastapi/SKILL.md` cùng `references/app-schemas-dependencies.md`, `references/background-and-streaming.md`, `references/routes-errors-openapi-testing.md` (cùng thư mục skill)

# Thử truy xuất - fastapi

> **Kết luận:** strict 7/7: đạt ngưỡng. Sau `TK11.4` (tác vụ nền và luồng) cộng bổ sung request id, `operation_id`/tag/ví dụ và dependency theo header ở `routes-errors-openapi-testing.md` mục 7, sáu câu tình huống đều Đạt (lượt trước 4/7 Đạt hẳn, 3 Một phần); câu ranh giới trả `api-design`.

Bộ câu hỏi giữ nguyên chữ của lượt trước (bộ câu cũ giữ nguyên, không soạn mới); bộ câu mới là việc của `TK13`. Cột "Mục kỳ vọng" ghi vào file nháp
`.tmp/fastapi-expected.md` **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm). Bài trả lời của chủ thể (id ở
`agent_ids`) và bảng chấm ở `evidence/TK11/fastapi-retrieval.md` trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời,
đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Mình có endpoint POST /v1/invoices nhận body JSON lồng 3 cấp (khách hàng, danh sách dòng hàng, địa chỉ giao). Hiện client gửi thiếu trường hoặc sai kiểu thì app văng 500 và trả stack trace thô; còn response thì đang trả luôn cả cột `password_hash` của bảng user vì trả thẳng object ORM. Nên khai báo model vào/ra thế nào để input bị từ chối gọn và output chỉ lộ đúng trường cần? | `SKILL.md` › 3 (Schema Create/Update/Response, `response_model`) + › 4 (trả ORM thô = Chặn); `references/app-schemas-dependencies.md` › 3 | `SKILL.md` › 3. Luật then chốt (Schema); `references/app-schemas-dependencies.md` › 3. Schema Pydantic; `SKILL.md` › 4 | Đạt |
| 2 | Service có 14 route cùng cần "người dùng hiện tại", và 6 trong số đó còn cần kiểm tra user thuộc đúng tenant trong header `X-Tenant-ID`. Hiện mỗi route tự parse header rồi tự query lại user, copy-paste khắp nơi. Gom việc này lại một chỗ và cho các route dùng chung bằng cách nào cho gọn? | `references/routes-errors-openapi-testing.md` › 7 (dependency đọc header `X-Tenant-ID`, `CurrentUser`/`TenantUser`) + `SKILL.md` › 3 (Dependency, bí danh kiểu); `app-schemas-dependencies.md` › 4 | `references/routes-errors-openapi-testing.md` › 7 (Dependency đọc header); `references/app-schemas-dependencies.md` › 4 | Đạt |
| 3 | Endpoint GET /reports/export chạy ~40 giây vì phải dựng file CSV từ 2 triệu dòng, client bên ngoài hay timeout ở giây thứ 30. Mình định cho trả về ngay rồi xử lý phần nặng sau, và trả file qua dạng stream. Trong FastAPI làm được những cách nào, chọn cái nào để không chặn các request khác? | `references/background-and-streaming.md` › 1 (chọn đường), › 2 (`BackgroundTasks`), › 3 (`202` + mã việc), › 4 (`StreamingResponse` generator async); `SKILL.md` › 3 (Tác vụ nền và luồng, Async) | `references/background-and-streaming.md` › 1, › 3, › 4 | Đạt |
| 4 | Frontend và mobile đang nhận lỗi mỗi route một kiểu: chỗ thì `{"detail": "not found"}`, chỗ thì `{"error": "..."}`, lỗi validate thì ra mảng dài của Pydantic. Muốn mọi lỗi 4xx/5xx của service đều ra một khuôn thống nhất có mã lỗi và request id. Cài đặt khuôn đó vào app FastAPI ở chỗ nào? | `references/routes-errors-openapi-testing.md` › 3 + › 7 (một khuôn cho mọi lỗi: handler `StarletteHTTPException`, `RequestValidationError`, middleware request id); `SKILL.md` › 3 (Lỗi) | `references/routes-errors-openapi-testing.md` › 7 (Một khuôn cho mọi lỗi); › 3; `references/app-schemas-dependencies.md` › 1 | Đạt |
| 5 | Tài liệu Swagger của mình hiện có cả 60 route chung một danh sách dài, response mẫu trống trơn, và client sinh code tự động từ openapi.json đặt tên hàm rất xấu (kiểu `read_items_items__get`). Chỉnh gì ở router và từng route để docs gọn, có ví dụ và tên operation sạch? | `references/routes-errors-openapi-testing.md` › 7 (`generate_unique_id_function` / `operation_id`, `openapi_tags`, ví dụ trong schema) + › 4 | `references/routes-errors-openapi-testing.md` › 7 (OpenAPI gọn, tên operation sạch); › 4 | Đạt |
| 6 | Khi app khởi động cần mở pool kết nối Postgres và Redis, tắt app thì đóng lại cho sạch; ngoài ra cấu hình (URL DB, secret ký token, bật/tắt debug) hiện đang đọc rải rác bằng `os.getenv` trong nhiều file, deploy lên 3 môi trường hay sai. Quản lý vòng đời tài nguyên và cấu hình theo kiểu chuẩn của FastAPI ra sao? | `SKILL.md` › 3 (Khởi tạo: `create_app()` + `lifespan`; Cấu hình pydantic-settings); `references/app-schemas-dependencies.md` › 1, › 2 | `references/app-schemas-dependencies.md` › 1. Factory dựng app; › 2. Cấu hình bằng pydantic-settings; `SKILL.md` › 3 | Đạt |
| 7 | Team đang bàn trước khi code: endpoint danh sách đơn hàng nên phân trang kiểu offset hay cursor, thêm lọc theo trạng thái thế nào, đường dẫn đặt `/v1/orders` hay `/v1/[users]/{id}/orders`, và mã trạng thái nào cho trường hợp đơn đã bị huỷ. Chưa ai viết dòng code nào, chỉ muốn chốt hợp đồng API cho các bên dùng. | mục khác: skill `api-design` (từ `SKILL.md` › 1) | mục khác: `api-design` (từ `SKILL.md` › 1. Khi nào dùng — và khi nào sang skill khác) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- `description` đã thêm "background tasks, streaming responses" ở `TK11.4`; thân skill có (mục 3 và `background-and-streaming.md`).
- Chủ thể nêu: ví dụ schema chỉ phẳng, không có model lồng 3 cấp và không nói thiếu trường thì FastAPI trả `422` chứ không phải `500` (câu 1); Redis chưa có ví dụ riêng cho `lifespan` (câu 6); skill không nói đổi GET export thành POST (hợp đồng cặp endpoint giao `api-design`, câu 3).
- Nguồn của phần thêm ở `TK11.4`: fastapi.tiangolo.com (Background Tasks, Custom Response, Stream Data, Server-Sent Events); mục 7 của `routes-errors-openapi-testing.md` (request id, `generate_unique_id_function`, `openapi_tags`, `Header()`) viết theo tài liệu FastAPI về xử lý lỗi, cấu hình OpenAPI và dependency — chưa trích dòng nào của trang nguồn riêng cho mục đó.
