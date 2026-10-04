---
skill: database-migrations
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: fa84cc5a791ab575a98f7510f946d6504a629c42
date: 2026-10-04
result: "strict 7/7 (+0 partial, 0 fail) — at threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 7/7"
agent_ids:
  questions: "bộ câu cũ giữ nguyên, không soạn mới"
  answers: af2d85d8e6de32480
---

Đã đọc: `<gốc worktree>/skills/database-migrations/SKILL.md` cùng bốn file `references/` (`postgres-safe-ddl.md`, `rehearsal.md`, `django-golang-migrate.md`, `orm-tooling-node.md`)

# Thử truy xuất - database-migrations

> **Kết luận:** strict 7/7: đạt ngưỡng. Sau `TK11.2` ba câu từng Một phần (khoá ngoại + dòng mồ côi, trùng số golang-migrate, dòng JSON hỏng) đều có mục chứa đủ quyết định chính; câu ranh giới trả `api-design`. `references/rehearsal.md` (phòng sạch) không đổi.

Bộ câu hỏi giữ nguyên chữ của lượt trước (bộ câu cũ giữ nguyên, không soạn mới); bộ câu mới là việc của `TK13`. Cột "Mục kỳ vọng" ghi vào file nháp
`.tmp/database-migrations-expected.md` **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm). Bài trả lời của chủ thể (id ở
`agent_ids`) và bảng chấm ở `evidence/TK11/database-migrations-retrieval.md` trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời,
đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Bên mình có bảng `orders` khoảng 40 triệu dòng, giờ muốn thêm khoá ngoại `orders.warehouse_id` trỏ sang bảng `warehouses`. Dữ liệu cũ chắc chắn có vài dòng mồ côi vì trước đây không ràng buộc gì. Làm sao thêm khoá ngoại mà không khoá bảng ghi đơn hàng trong giờ cao điểm? | `references/postgres-safe-ddl.md` › 6 (`NOT VALID`, truy vấn mồ côi, xử lý mồ côi = quyết định nghiệp vụ + migration dữ liệu riêng, `VALIDATE CONSTRAINT`, index `CONCURRENTLY`, `lock_timeout`) + `SKILL.md` › 2 | `references/postgres-safe-ddl.md` › 6. Thêm khoá ngoại lên bảng đã có dữ liệu; `SKILL.md` › 2; `references/rehearsal.md` › 1 | Đạt |
| 2 | Bảng `users` của tôi đang nhét luôn cả địa chỉ giao hàng (street, city, zip, country) thành 6 cột, giờ cần tách sang bảng `addresses` riêng, một user nhiều địa chỉ. Bảng 8 triệu dòng, app vẫn đang chạy và ghi liên tục. Nên chia các bước deploy theo thứ tự nào để không có lúc nào app đọc thiếu dữ liệu? | `SKILL.md` › 3 (mở rộng → chuyển → thu hẹp) + › 1 (nguyên tắc 3, 6) + `references/postgres-safe-ddl.md` › 4 (gỡ mã trước, bỏ cột sau) | `SKILL.md` › 3; › 1; `references/postgres-safe-ddl.md` › 5 | Đạt |
| 3 | Mình có script Python chạy một lần để sửa dữ liệu: chuẩn hoá 30 triệu số điện thoại trong bảng `contacts` (bỏ khoảng trắng, thêm đầu +84). Viết kiểu `UPDATE contacts SET ...` một câu duy nhất thì sợ treo DB. Script nên chia lô, chạy lại được nếu giữa chừng bị ngắt, và kiểm tra kết quả ra sao? | `references/postgres-safe-ddl.md` › 5 (chia lô, idempotent) + `references/rehearsal.md` › 4 + `references/django-golang-migrate.md` › 1 (mẫu theo khoá chính) | `references/postgres-safe-ddl.md` › 5. Cập nhật dữ liệu lớn; › 8; `references/rehearsal.md` › 4; `references/django-golang-migrate.md` › 1 | Đạt |
| 4 | Team mình dùng Node với Prisma, dev vừa merge một migration thêm enum mới và đổi kiểu cột `status` trong cùng một file. Lên staging thì chạy ngon, nhưng staging chỉ có vài nghìn dòng còn production hàng chục triệu. Tôi cần đọc kỹ file migration này để chốt có cho lên production không, nên soi những điểm nào và dựa vào đâu để tin kết quả staging? | `references/orm-tooling-node.md` › 1 + `SKILL.md` › 1, › 2 + `references/rehearsal.md` (diễn tập trên bản sao cỡ production) | `references/rehearsal.md` › 4. Diễn tập; `SKILL.md` › 2; `references/rehearsal.md` › 7; `references/orm-tooling-node.md` › 1; `references/postgres-safe-ddl.md` › 7 | Đạt |
| 5 | Dự án Go của tôi dùng golang-migrate, đang có thư mục migrations với 60 file up/down. Hai dev cùng tạo file số 000061 trên hai nhánh khác nhau, merge xong thì lệch phiên bản và có cột bị `dirty`. Xử lý đống này thế nào, và nên đặt quy ước gì để khỏi tái diễn? | `references/django-golang-migrate.md` › 2: "Trạng thái dirty" (điều tra → sửa DB có runbook → `force`), "Trùng số phiên bản" (đổi số cả cặp trước khi gộp), "Quy ước phòng ngừa" (số theo thời gian mặc định / kiểm `uniq -d`); mâu thuẫn với nguyên tắc 1 giải ở `SKILL.md` › 1 | `references/django-golang-migrate.md` › 2. golang-migrate (Trạng thái dirty, Trùng số phiên bản, Quy ước phòng ngừa) | Đạt |
| 6 | Cần chuyển cột `events.payload` từ kiểu TEXT chứa JSON sang JSONB, bảng 300 triệu dòng, lưu lịch sử sự kiện, ghi liên tục cả ngày. Có vài dòng JSON hỏng chắc chắn không parse được. Cách làm nào không phải dừng hệ thống, và xử lý các dòng hỏng đó ra sao? | `SKILL.md` › 3 + `references/postgres-safe-ddl.md` › 7 (đếm dòng hỏng bằng `pg_input_is_valid` / `try_jsonb`, cách xử lý dòng hỏng chốt với người dùng, backfill theo khoá chính) + › 5 + `references/rehearsal.md` | `references/postgres-safe-ddl.md` › 7. Đổi kiểu cột khi dữ liệu có thể không hợp lệ; `SKILL.md` › 3; `references/rehearsal.md` › 4 | Đạt |
| 7 | Tôi đang viết endpoint `POST /v1/invoices` trong FastAPI, cần chọn mã trạng thái trả về khi hoá đơn trùng số, khi thiếu quyền, khi dữ liệu sai định dạng, và định dạng JSON báo lỗi chung cho toàn bộ API. Nên thiết kế thế nào cho nhất quán, kèm cả phân trang cho `GET /v1/invoices`? | mục khác: skill `api-design` (+ `fastapi`, `error-handling`) | mục khác: `api-design`, kèm `fastapi` và `error-handling`; nói rõ skill này không phủ | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có. Mâu thuẫn "không sửa tay DB" ↔ `force` đã giải ở `SKILL.md` mục 1; chỗ lệch ở `postgres-safe-ddl.md` mục 3 bước 4 đã sửa.
- Chủ thể nêu: chưa có mẫu script Python thuần cho backfill (câu 3, có mẫu SQL và Django); cơ chế enum Postgres không có riêng (câu 4); thiết kế quan hệ 1-nhiều của `addresses` thuộc skill `postgres` (câu 2).
- Nguồn của phần thêm ở `TK11.2`: tài liệu PostgreSQL (ALTER TABLE, ddl-constraints, continuous-archiving, hàm kiểm hợp lệ bản 16), golang-migrate (MIGRATIONS.md, GETTING_STARTED.md, cmd/migrate/README.md); `rehearsal.md` không dùng.
