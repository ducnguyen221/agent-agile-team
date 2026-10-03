---
skill: database-migrations
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 6a835f88c7cda24d3e9b46ebb0fb73a94519bb79
date: 2026-10-04
result: "strict 4/7 (+3 partial, 0 fail) — below threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 7/7"
agent_ids:
  questions: a4d7a065604b7ced6
  answers: a47e3e101dea21a8b
---

Đã đọc: `<gốc worktree>\skills\database-migrations\SKILL.md`

# Thử truy xuất - database-migrations

> **Kết luận:** strict 4/7 (+3 partial, 0 fail), points-right 7/7: dưới ngưỡng (3/6 câu tình huống Đạt, 50 % so với ngưỡng 80 %; câu ranh giới Đạt). Chạy lại (lượt 4) vì dòng `source:` của `SKILL.md` và chú thích đầu `references/rehearsal.md` đổi (bỏ số đo 8-gram khỏi metadata đi vào băm, re-review lần 2) làm lệch `skill_sha`; `description` không đổi và `SKILL.md` không đổi nội dung.
> Bộ câu mới, người soạn và chủ thể đều là agent mới. So lượt trước (strict 6/8, 5/7 tình huống) là thấp hơn về số, nhưng cả hai lượt đều dưới ngưỡng và khác nhau ở bộ câu: bộ này chạm thêm ba chỗ thiếu nội dung (khoá ngoại, trùng số phiên bản golang-migrate, dòng JSON hỏng khi đổi kiểu), xem cuối file. Cả ba câu "một phần" (1, 5, 6) trỏ đúng nơi; chủ thể tự nói rõ phần tự suy ngoài skill, không bịa.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description`, lĩnh vực, tên các skill khác và cột câu hỏi của bộ cũ để không lặp); nguyên văn câu hỏi, file nháp
"Mục mong đợi" (mtime `2026-10-04 00:58:24 +0700`), bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/database-migrations-rerun-after-rereview2.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `api-design`, đã được đối chiếu với `description` của skill đích (REST, mã trạng thái, phân trang) và nhận là đúng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Bên mình có bảng `orders` khoảng 40 triệu dòng, giờ muốn thêm khoá ngoại `orders.warehouse_id` trỏ sang bảng `warehouses`. Dữ liệu cũ chắc chắn có vài dòng mồ côi vì trước đây không ràng buộc gì. Làm sao thêm khoá ngoại mà không khoá bảng ghi đơn hàng trong giờ cao điểm? | `references/postgres-safe-ddl.md` › 1 (mẫu `NOT VALID` → `VALIDATE`, viết cho `NOT NULL`) + `SKILL.md` › 1 nguyên tắc 3, › 2, › 6 + `references/rehearsal.md` › 1 (đổi khoá ngoại thuộc phạm vi); nội dung riêng cho khoá ngoại và dòng mồ côi không có trong skill | `SKILL.md` › 2, › 5; `references/postgres-safe-ddl.md` › 1, › 5; `references/rehearsal.md` › 2; nói rõ skill không có công thức khoá ngoại, trình tự `NOT VALID` → dọn dòng mồ côi → `VALIDATE` là tự suy | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 2 | Bảng `users` của tôi đang nhét luôn cả địa chỉ giao hàng (street, city, zip, country) thành 6 cột, giờ cần tách sang bảng `addresses` riêng, một user nhiều địa chỉ. Bảng 8 triệu dòng, app vẫn đang chạy và ghi liên tục. Nên chia các bước deploy theo thứ tự nào để không có lúc nào app đọc thiếu dữ liệu? | `SKILL.md` › 3. Mở rộng → chuyển → thu hẹp + › 1 nguyên tắc 3 và 6 + `references/postgres-safe-ddl.md` › 4, › 5 | `SKILL.md` › 3, › 1 (điểm 3, 6), › 6; `references/postgres-safe-ddl.md` › 3, › 4; nói rõ skill không có ví dụ tách bảng một-nhiều và ghi kép | Đạt |
| 3 | Mình có script Python chạy một lần để sửa dữ liệu: chuẩn hoá 30 triệu số điện thoại trong bảng `contacts` (bỏ khoảng trắng, thêm đầu +84). Viết kiểu `UPDATE contacts SET ...` một câu duy nhất thì sợ treo DB. Script nên chia lô, chạy lại được nếu giữa chừng bị ngắt, và kiểm tra kết quả ra sao? | `references/postgres-safe-ddl.md` › 5. Cập nhật dữ liệu lớn + `SKILL.md` › 2 (backfill là migration riêng) + `references/rehearsal.md` › 2 bước 5 | `SKILL.md` › 2; `references/postgres-safe-ddl.md` › 5; `references/rehearsal.md` › 2 (bước 4, 5), › 3; nói rõ mẫu trong skill là SQL chứ không phải Python và điều kiện idempotent cho số điện thoại là tự thiết kế | Đạt |
| 4 | Team mình dùng Node với Prisma, dev vừa merge một migration thêm enum mới và đổi kiểu cột `status` trong cùng một file. Lên staging thì chạy ngon, nhưng staging chỉ có vài nghìn dòng còn production hàng chục triệu. Tôi cần đọc kỹ file migration này để chốt có cho lên production không, nên soi những điểm nào và dựa vào đâu để tin kết quả staging? | `references/orm-tooling-node.md` › 1. Prisma + `SKILL.md` › 1 nguyên tắc 3-4, › 2, › 6 + `references/rehearsal.md` › 2 (diễn tập trên bản sao cỡ production) | `SKILL.md` › 1 (điểm 4, 5), › 2, › 5, › 6; `references/orm-tooling-node.md` › 1; `references/rehearsal.md` › 2, › 3, › 4; kết luận staging nhỏ không chứng minh được, cần diễn tập cỡ production | Đạt |
| 5 | Dự án Go của tôi dùng golang-migrate, đang có thư mục migrations với 60 file up/down. Hai dev cùng tạo file số 000061 trên hai nhánh khác nhau, merge xong thì lệch phiên bản và có cột bị `dirty`. Xử lý đống này thế nào, và nên đặt quy ước gì để khỏi tái diễn? | `references/django-golang-migrate.md` › 2. golang-migrate (`force VERSION` để gỡ `dirty`); xử lý trùng số phiên bản và quy ước phòng ngừa không có trong skill | `references/django-golang-migrate.md` › 2; `SKILL.md` › 1 (điểm 5), › 6; nói rõ chỉ có `force` và cách tạo cặp tệp, còn đổi số tệp, CI kiểm trùng số, `-seq` hay timestamp là tự suy | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 6 | Cần chuyển cột `events.payload` từ kiểu TEXT chứa JSON sang JSONB, bảng 300 triệu dòng, lưu lịch sử sự kiện, ghi liên tục cả ngày. Có vài dòng JSON hỏng chắc chắn không parse được. Cách làm nào không phải dừng hệ thống, và xử lý các dòng hỏng đó ra sao? | `SKILL.md` › 3 (cột song song, backfill lô, chuyển đọc) + `references/postgres-safe-ddl.md` › 5 + `references/rehearsal.md` › 2; cách xử lý dòng JSON hỏng và ép kiểu không có trong skill | `SKILL.md` › 2, › 3, › 6; `references/postgres-safe-ddl.md` › 5; `references/rehearsal.md` › 2; nói rõ skill không nói gì về dòng JSON hỏng, bảng cách ly và `pg_input_is_valid` là kiến thức ngoài skill | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 7 | Tôi đang viết endpoint `POST /v1/invoices` trong FastAPI, cần chọn mã trạng thái trả về khi hoá đơn trùng số, khi thiếu quyền, khi dữ liệu sai định dạng, và định dạng JSON báo lỗi chung cho toàn bộ API. Nên thiết kế thế nào cho nhất quán, kèm cả phân trang cho `GET /v1/invoices`? | mục khác: skill `api-design` (mã trạng thái, error envelope, phân trang; `fastapi` cho phần FastAPI) | mục khác: `api-design` và `fastapi` (chủ thể nhận câu không thuộc skill, không trả lời nội dung; nêu thêm `error-handling`) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Thêm khoá ngoại trên bảng lớn có dòng mồ côi (khoá ngoại `NOT VALID`, tìm và dọn dòng mồ côi, `VALIDATE`, index trên cột khoá): không có; mẫu `NOT VALID` → `VALIDATE` trong skill viết cho `NOT NULL`, chủ thể nói rõ phần khoá ngoại là tự suy (câu 1).
- Xử lý xung đột số phiên bản `golang-migrate` (hai nhánh cùng số) và quy ước phòng ngừa (kiểm trùng số ở CI, thứ tự merge, `-seq` hay timestamp): không có; chỉ có `force VERSION` để gỡ `dirty` và cách tạo cặp tệp (câu 5).
- Đổi kiểu cột qua cột song song, cách bắt và cách ly dòng dữ liệu hỏng (ví dụ JSON không parse được), đối chiếu nội dung giữa kiểu cũ và mới: không có; chủ thể nói rõ và không bịa quy trình (câu 6).
- Chỗ thiếu đã biết từ lượt trước vẫn còn: chuyển lịch sử migration giữa hai công cụ (Django ORM sang SQLAlchemy/Alembic) và đặt `UNIQUE` trên bảng lớn đang ghi, cả hai không có trong skill (bộ câu lượt này không hỏi lại hai chỗ đó).
- Phần phụ nằm ngoài quyết định chính, ghi để biết: ví dụ tách bảng một-nhiều với ghi kép và chống đua khi backfill (câu 2); mẫu Python và cách kiểm chất lượng chuẩn hoá dữ liệu (câu 3); đặc thù Postgres khi đổi kiểu sang enum, `ALTER COLUMN … TYPE … USING`, `ALTER TYPE … ADD VALUE` trong giao dịch (câu 4).
- Mâu thuẫn nhỏ đã ghi ở lượt trước (`references/postgres-safe-ddl.md` mục 3 bước 4 gộp ngừng ghi cột cũ và `DROP COLUMN` trong một migration, còn `SKILL.md` mục 3 tách thành deploy rồi mới bỏ cột ở migration sau): lượt này không ai nêu lại và tôi chưa kiểm lại, nên vẫn tính là còn.
