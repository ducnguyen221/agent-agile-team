---
skill: api-design
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: dde5b6a0ecb7f5eac7daa12e8c96ab8fd32a50b4
date: 2026-10-03
result: pass 6/6
---

Đã đọc: `<gốc worktree>\skills\api-design\SKILL.md`

# Thử truy xuất — api-design

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥5/6). Chủ thể mở đúng tệp `references/` mà bảng "Đọc thêm khi cần" trỏ tới
> cho phân trang, rate limit, phiên bản, và nhận ra câu ranh giới thuộc `shaping-spec`. Không có chỗ thiếu nội dung.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Câu 6 là câu ranh giới: đáp án của
người soạn (`shaping-spec`) đã được người chấm đối chiếu với `description` của skill đích (biến lời giao thành SPEC
trước khi viết mã) và nhận là đúng; `intake` cũng chấp nhận được.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Endpoint `GET /orders` đang trả 50.000 dòng một lần, client mobile bị timeout. Nên phân trang kiểu offset hay cursor, và response gói phân trang thế nào? | `references/responses-pagination-filtering.md` › 2. Phân trang | `references/responses-pagination-filtering.md` › 2. Phân trang, 1. Phong bì response | Đạt |
| 2 | `POST /users` với email đã tồn tại, nhóm đang tranh cãi trả 400, 409 hay 422. Chọn mã nào và body lỗi nên có những trường gì? | `SKILL.md` › 2. Phương thức và mã trạng thái (+ phong bì lỗi ở `references/responses-pagination-filtering.md` › 1) | `SKILL.md` › 2. Phương thức và mã trạng thái; `references/responses-pagination-filtering.md` › 1. Phong bì response | Đạt |
| 3 | Cần đổi `price` từ số nguyên sang object `{amount, currency}` trong khi ba bản app mobile cũ vẫn gọi. Nên đặt versioning ra sao để không làm hỏng client cũ? | `references/auth-ratelimit-versioning.md` › 4. Phiên bản (+ `SKILL.md` › 3) | `references/auth-ratelimit-versioning.md` › 4. Phiên bản; `SKILL.md` › 3. Đổi hợp đồng | Đạt |
| 4 | `/search` cần giới hạn 100 request/phút theo API key. Header nào báo quota, và khi vượt thì trả mã gì cùng thông tin chờ bao lâu? | `references/auth-ratelimit-versioning.md` › 3. Rate limit | `references/auth-ratelimit-versioning.md` › 3. Rate limit | Đạt |
| 5 | SPEC có một thay đổi `PATCH /subscriptions/{id}` dùng bởi web admin và hai dịch vụ nội bộ. Phần mô tả thay đổi API cần liệt kê gì về các bên dùng? | `SKILL.md` › 3. Đổi hợp đồng | `SKILL.md` › 3. Đổi hợp đồng: liệt kê bên dùng trước khi đổi | Đạt |
| 6 | Khách nói "cho app hiển thị lịch sử giao dịch" nhưng chưa rõ ai xem, xem gì, bao lâu. Làm sao biến thành yêu cầu rõ ràng trước khi nghĩ tới endpoint? | mục khác: skill `shaping-spec` | mục khác: `shaping-spec` (kèm `intake`) | Đạt |

## Thiếu nội dung / mâu thuẫn

Không phát hiện chỗ thiếu hay mâu thuẫn ở sáu câu này. Mọi chủ đề trong `description` (URL, phương thức, mã trạng thái,
phong bì lỗi, phân trang, lọc, xác thực, rate limit, phiên bản, đổi hợp đồng) đều có mục trả lời.
