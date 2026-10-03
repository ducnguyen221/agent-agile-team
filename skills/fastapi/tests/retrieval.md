---
skill: fastapi
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 79140a71a0b2f0a450333698d8adda6765774fe6
date: 2026-10-03
result: "strict 4/7 (+3 partial, 0 fail) — below threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 7/7"
agent_ids:
  questions: aca1d2476945acb8e
  answers: ab5106b7165090ed2
---

Đã đọc: `<gốc worktree>\skills\fastapi\SKILL.md`

# Thử truy xuất - fastapi

> **Kết luận:** strict 4/7 (+3 partial, 0 fail), points-right 7/7: dưới ngưỡng (3/6 câu tình huống Đạt; câu ranh giới Đạt). Chạy lại (lượt 2) với bộ câu mới, người soạn
> và chủ thể đều là agent mới. Chủ thể trỏ đúng mục ở cả 6 câu tình huống (những phần skill không phủ, chủ thể nói rõ và được ghi ở cuối file) và nhận
> ra câu ranh giới thuộc `api-design`.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` hiện hành, lĩnh vực và tên các skill khác); nguyên văn câu hỏi, file nháp
"Mục kỳ vọng" (có mtime), bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/fastapi-retrieval-rerun-2.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `api-design`. Trong câu 7 đoạn đường dẫn mẫu `/v1/[users]/{id}/orders` đặt `users` trong ngoặc vuông (nguyên văn không có ngoặc) vì cổng chống rò của repo chặn chuỗi đó; bản nguyên văn ở file hồ sơ.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Mình có endpoint POST /v1/invoices nhận body JSON lồng 3 cấp (khách hàng, danh sách dòng hàng, địa chỉ giao). Hiện client gửi thiếu trường hoặc sai kiểu thì app văng 500 và trả stack trace thô; còn response thì đang trả luôn cả cột `password_hash` của bảng user vì trả thẳng object ORM. Nên khai báo model vào/ra thế nào để input bị từ chối gọn và output chỉ lộ đúng trường cần? | `SKILL.md` › 3. Luật then chốt (Schema: tách Create/Update/Response, response không có hash mật khẩu; luôn `response_model`) + › 4 bảng (trả ORM thô = Chặn); `references/app-schemas-dependencies.md` › 3. Schema Pydantic | `SKILL.md` › 3 (Schema), › 4, › 6; `references/app-schemas-dependencies.md` › 3 | Đạt |
| 2 | Service có 14 route cùng cần "người dùng hiện tại", và 6 trong số đó còn cần kiểm tra user thuộc đúng tenant trong header `X-Tenant-ID`. Hiện mỗi route tự parse header rồi tự query lại user, copy-paste khắp nơi. Gom việc này lại một chỗ và cho các route dùng chung bằng cách nào cho gọn? | `SKILL.md` › 3 (Dependency: bí danh kiểu `DbDep`) + › 2 (`dependencies.py` giữ người dùng hiện tại/phân quyền); `references/app-schemas-dependencies.md` › 4. Dependency (`get_current_user`). Header tenant cụ thể không có; chỉ suy từ mẫu dependency | `SKILL.md` › 3 (Dependency, Xác thực); `references/app-schemas-dependencies.md` › 4 | Đạt |
| 3 | Endpoint GET /reports/export chạy ~40 giây vì phải dựng file CSV từ 2 triệu dòng, client bên ngoài hay timeout ở giây thứ 30. Mình định cho trả về ngay rồi xử lý phần nặng sau, và trả file qua dạng stream. Trong FastAPI làm được những cách nào, chọn cái nào để không chặn các request khác? | `SKILL.md` › 3. Luật then chốt › Async (`async def` chỉ gọi thư viện async; chặn thì khai `def` hoặc bọc) + › 7 hiệu năng. KHÔNG có `BackgroundTasks`, `StreamingResponse`, hàng đợi tác vụ nền. Đạt nếu agent nêu đúng phần Async và nói rõ phần nền/stream không có | `SKILL.md` › 3 (Async), › 4, › 7; nói rõ skill không phủ BackgroundTasks / stream / hàng đợi | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 4 | Frontend và mobile đang nhận lỗi mỗi route một kiểu: chỗ thì `{"detail": "not found"}`, chỗ thì `{"error": "..."}`, lỗi validate thì ra mảng dài của Pydantic. Muốn mọi lỗi 4xx/5xx của service đều ra một khuôn thống nhất có mã lỗi và request id. Cài đặt khuôn đó vào app FastAPI ở chỗ nào? | `SKILL.md` › 3 (Lỗi: một lớp lỗi miền + exception handler đăng ký tập trung, phong bì `{error:{code,message}}`) + › 2 (`main.py` sở hữu exception handler); `references/routes-errors-openapi-testing.md` › 3. Xử lý lỗi tập trung. Request id có thể không có | `SKILL.md` › 2, › 3 (Lỗi); `references/routes-errors-openapi-testing.md` › 3; `references/app-schemas-dependencies.md` › 1; nói rõ không có request id | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 5 | Tài liệu Swagger của mình hiện có cả 60 route chung một danh sách dài, response mẫu trống trơn, và client sinh code tự động từ openapi.json đặt tên hàm rất xấu (kiểu `read_items_items__get`). Chỉnh gì ở router và từng route để docs gọn, có ví dụ và tên operation sạch? | `SKILL.md` › 3 (OpenAPI: tuỳ biến bằng gán vào `app.openapi`, khai response lỗi từng route) + › 4 (OpenAPI thiếu response model/response lỗi); `references/routes-errors-openapi-testing.md` › 4. Tuỳ biến OpenAPI. `tags`/`operation_id`/ví dụ có thể không có | `SKILL.md` › 3 (OpenAPI), › 4; `references/routes-errors-openapi-testing.md` › 4; nói rõ không có `operation_id` / ví dụ | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 6 | Khi app khởi động cần mở pool kết nối Postgres và Redis, tắt app thì đóng lại cho sạch; ngoài ra cấu hình (URL DB, secret ký token, bật/tắt debug) hiện đang đọc rải rác bằng `os.getenv` trong nhiều file, deploy lên 3 môi trường hay sai. Quản lý vòng đời tài nguyên và cấu hình theo kiểu chuẩn của FastAPI ra sao? | `SKILL.md` › 3 (Khởi tạo: `create_app()` + `lifespan`; Cấu hình: pydantic-settings, secret bắt buộc không mặc định); `references/app-schemas-dependencies.md` › 1. Factory dựng app và › 2. Cấu hình bằng pydantic-settings | `SKILL.md` › 3 (Khởi tạo, Cấu hình), › 7; `references/app-schemas-dependencies.md` › 1, › 2 | Đạt |
| 7 | Team đang bàn trước khi code: endpoint danh sách đơn hàng nên phân trang kiểu offset hay cursor, thêm lọc theo trạng thái thế nào, đường dẫn đặt `/v1/orders` hay `/v1/[users]/{id}/orders`, và mã trạng thái nào cho trường hợp đơn đã bị huỷ. Chưa ai viết dòng code nào, chỉ muốn chốt hợp đồng API cho các bên dùng. | mục khác: skill `api-design` (`SKILL.md` › 1: 'Hình URL, mã trạng thái, phong bì lỗi, phân trang, đổi hợp đồng → skill `api-design`') | mục khác: `api-design` (từ `SKILL.md` › 1) | Đạt |


Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Tác vụ nền / `BackgroundTasks` / `StreamingResponse` / hàng đợi cho endpoint chạy lâu: không có (câu 3).
- Request id trong khuôn lỗi; ghi đè handler cho `RequestValidationError` / `HTTPException`: không có (câu 4).
- `operation_id` / `generate_unique_id_function`, `openapi_tags`, ví dụ trong schema: không có; chỉ có `tags` khi `include_router` và tuỳ biến `app.openapi` (câu 5).
- Đọc header `X-Tenant-ID` trong dependency: không có ví dụ; chỉ suy ra từ khuôn dependency phân quyền (câu 2). Ví dụ Redis cho `lifespan`: không có riêng (câu 6).
