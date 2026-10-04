---
skill: database-migrations
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: b381f7d0c9842053c921c6448fcd6ddffcc7eb26
date: 2026-10-04
result: "strict 4/7 (+3 partial, 0 fail) — below threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 7/7"
agent_ids:
  questions: a4d7a065604b7ced6
  answers: a3cd5dd01f85cd720
---

Đã đọc: `<gốc worktree>\skills\database-migrations\SKILL.md`

# Thử truy xuất - database-migrations

> **Kết luận:** strict 4/7 (+3 partial, 0 fail), points-right 7/7: dưới ngưỡng (3/6 câu tình huống Đạt, 50 % so với ngưỡng 80 %; câu ranh giới Đạt). Chạy lại ở SPR-04 TK10 trên bản có `references/rehearsal.md` **viết lại phòng sạch**
> (`skill_sha` ở frontmatter đổi so lượt trước; `description` và `SKILL.md` không đổi nội dung). Giữ **nguyên bộ câu hỏi cũ** (người soạn `a4d7a065604b7ced6` của lượt trước); cột Mục kỳ vọng viết lại theo `rehearsal.md` mới
> (mục 1 Khi nào · 2 Số liệu đầu vào · 3 Phân loại và đường lùi · 4 Diễn tập (có khối Backfill) · 5 Runbook · 6 Đầu ra · 7 Dừng). So lượt trước: cùng 4/7; chủ thể trỏ đúng vào `rehearsal.md` mới ở các câu 3, 4, 6 và nội dung dùng được.
> Ba câu "một phần" (1, 5, 6) vẫn là ba khoảng trống nội dung đã biết (khoá ngoại và dòng mồ côi, trùng số phiên bản `golang-migrate`, dòng JSON hỏng khi đổi kiểu), nằm ở `references/` không đổi ở TK10; chủ thể tự nói rõ phần tự suy ngoài skill, không bịa.

Bảy câu hỏi do một agent **chưa đọc** skill soạn ở lượt trước (bộ câu giữ nguyên chữ, không soạn lại); file nháp "Mục kỳ vọng" viết lại theo bản mới (mtime `2026-10-04 08:09:29 +0700`) **trước khi** giao chủ thể
(lệnh giao lúc ~08:10 +0700); bài trả lời trọn của chủ thể, id agent và số lượt công cụ (6: năm lần đọc file, một lần trả kết quả) ở `evidence/TK10/qa-database-migrations.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.
Chủ thể đọc thêm bốn file `references/` mà `SKILL.md` trỏ tới (được phép). Câu 7 là câu ranh giới: đáp án của người soạn là `api-design`, đã được đối chiếu với `description` của skill đích (REST, mã trạng thái, phân trang) và nhận là đúng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Bên mình có bảng `orders` khoảng 40 triệu dòng, giờ muốn thêm khoá ngoại `orders.warehouse_id` trỏ sang bảng `warehouses`. Dữ liệu cũ chắc chắn có vài dòng mồ côi vì trước đây không ràng buộc gì. Làm sao thêm khoá ngoại mà không khoá bảng ghi đơn hàng trong giờ cao điểm? | `references/postgres-safe-ddl.md` › 1 (mẫu `NOT VALID` → `VALIDATE`, viết cho `NOT NULL`) + `SKILL.md` › 1 nguyên tắc 3-4, › 2, › 6 + `references/rehearsal.md` › 1 (thêm ràng buộc lên bảng đã có dữ liệu thuộc diện diễn tập); nội dung riêng cho khoá ngoại và dòng mồ côi không có trong skill | `SKILL.md` › 1 (nguyên tắc 3, 4), › 2; `references/postgres-safe-ddl.md` › 1, › 5; `references/rehearsal.md` › 1; nói rõ skill không có công thức khoá ngoại và không nói xử lý dòng mồ côi, `NOT VALID` → `VALIDATE` cho khoá ngoại là tự suy | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 2 | Bảng `users` của tôi đang nhét luôn cả địa chỉ giao hàng (street, city, zip, country) thành 6 cột, giờ cần tách sang bảng `addresses` riêng, một user nhiều địa chỉ. Bảng 8 triệu dòng, app vẫn đang chạy và ghi liên tục. Nên chia các bước deploy theo thứ tự nào để không có lúc nào app đọc thiếu dữ liệu? | `SKILL.md` › 3. Mở rộng → chuyển → thu hẹp + › 1 nguyên tắc 3 và 6 + `references/postgres-safe-ddl.md` › 4 | `SKILL.md` › 3, › 1 (nguyên tắc 6); `references/postgres-safe-ddl.md` › 4; nêu năm bước, gỡ mã trước rồi mới `DROP COLUMN`; nói rõ skill không có ví dụ tách bảng một-nhiều | Đạt |
| 3 | Mình có script Python chạy một lần để sửa dữ liệu: chuẩn hoá 30 triệu số điện thoại trong bảng `contacts` (bỏ khoảng trắng, thêm đầu +84). Viết kiểu `UPDATE contacts SET ...` một câu duy nhất thì sợ treo DB. Script nên chia lô, chạy lại được nếu giữa chừng bị ngắt, và kiểm tra kết quả ra sao? | `references/postgres-safe-ddl.md` › 5 + `SKILL.md` › 2 (backfill là migration riêng) + `references/rehearsal.md` › 4 (khối Backfill: lô cố định, idempotent, điểm tiếp, log; cắt ngang một lần; kiểm sau cùng) | `SKILL.md` › 2; `references/postgres-safe-ddl.md` › 5; `references/rehearsal.md` › 4 (Backfill, Kiểm sau cùng); `references/django-golang-migrate.md` › 1; nói rõ mẫu trong skill là SQL không phải Python và điều kiện idempotent cho chuẩn hoá tại chỗ là tự thiết kế | Đạt |
| 4 | Team mình dùng Node với Prisma, dev vừa merge một migration thêm enum mới và đổi kiểu cột `status` trong cùng một file. Lên staging thì chạy ngon, nhưng staging chỉ có vài nghìn dòng còn production hàng chục triệu. Tôi cần đọc kỹ file migration này để chốt có cho lên production không, nên soi những điểm nào và dựa vào đâu để tin kết quả staging? | `references/orm-tooling-node.md` › 1 (Prisma) + `SKILL.md` › 1 nguyên tắc 3-4, › 2, › 6 + `references/rehearsal.md` › 1, › 2, › 4 (bản sao cỡ production) | `SKILL.md` › 1, › 2, › 5, › 6; `references/orm-tooling-node.md` › 1; `references/rehearsal.md` › 4, › 7; kết luận staging nhỏ không chứng minh được, cần diễn tập cỡ production, không có bản sao thì `VR` là Chưa chạy | Đạt |
| 5 | Dự án Go của tôi dùng golang-migrate, đang có thư mục migrations với 60 file up/down. Hai dev cùng tạo file số 000061 trên hai nhánh khác nhau, merge xong thì lệch phiên bản và có cột bị `dirty`. Xử lý đống này thế nào, và nên đặt quy ước gì để khỏi tái diễn? | `references/django-golang-migrate.md` › 2. golang-migrate (`force VERSION` để gỡ `dirty`); xử lý trùng số phiên bản và quy ước phòng ngừa không có trong skill | `references/django-golang-migrate.md` › 2; `SKILL.md` › 1 (nguyên tắc 5); nói rõ chỉ có `force` và cách tạo cặp tệp, còn đổi số tệp, CI kiểm trùng số, `-seq` hay timestamp không có; nêu lệch với nguyên tắc 1 | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 6 | Cần chuyển cột `events.payload` từ kiểu TEXT chứa JSON sang JSONB, bảng 300 triệu dòng, lưu lịch sử sự kiện, ghi liên tục cả ngày. Có vài dòng JSON hỏng chắc chắn không parse được. Cách làm nào không phải dừng hệ thống, và xử lý các dòng hỏng đó ra sao? | `SKILL.md` › 3 (cột song song, backfill lô, chuyển đọc) + `references/postgres-safe-ddl.md` › 5 + `references/rehearsal.md` › 1, › 4; cách xử lý dòng JSON hỏng không có trong skill | `SKILL.md` › 3, › 5; `references/postgres-safe-ddl.md` › 3, › 5; `references/rehearsal.md` › 4, › 5, › 7; nói rõ skill không nói gì về dòng JSON hỏng | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 7 | Tôi đang viết endpoint `POST /v1/invoices` trong FastAPI, cần chọn mã trạng thái trả về khi hoá đơn trùng số, khi thiếu quyền, khi dữ liệu sai định dạng, và định dạng JSON báo lỗi chung cho toàn bộ API. Nên thiết kế thế nào cho nhất quán, kèm cả phân trang cho `GET /v1/invoices`? | mục khác: skill `api-design` (mã trạng thái, error envelope, phân trang; `fastapi` cho phần FastAPI) | mục khác: `api-design` (kèm `fastapi`, `error-handling`; chủ thể nhận câu không thuộc skill, không trả lời nội dung) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Thêm khoá ngoại trên bảng lớn có dòng mồ côi (khoá ngoại `NOT VALID`, tìm và dọn dòng mồ côi, `VALIDATE`, index trên cột khoá): không có; mẫu `NOT VALID` → `VALIDATE` trong skill viết cho `NOT NULL`, chủ thể nói rõ phần khoá ngoại là tự suy (câu 1).
- Xử lý xung đột số phiên bản `golang-migrate` (hai nhánh cùng số) và quy ước phòng ngừa (kiểm trùng số ở CI, thứ tự merge, `-seq` hay timestamp): không có; chỉ có `force VERSION` để gỡ `dirty` và cách tạo cặp tệp (câu 5).
- Đổi kiểu cột qua cột song song, cách bắt và cách ly dòng dữ liệu hỏng (ví dụ JSON không parse được), đối chiếu nội dung giữa kiểu cũ và mới: không có; chủ thể nói rõ và không bịa quy trình (câu 6).
- Mâu thuẫn mới do chủ thể nêu (câu 5): nguyên tắc 1 của `SKILL.md` ("không sửa tay DB") lệch với `references/django-golang-migrate.md` mục 2 (`force` "chỉ sau khi đã sửa tay DB khớp VERSION"); skill không giải thích.
- Chỗ thiếu đã biết từ các lượt trước vẫn còn: chuyển lịch sử migration giữa hai công cụ (Django ORM sang SQLAlchemy/Alembic) và đặt `UNIQUE` trên bảng lớn đang ghi, cả hai không có trong skill (bộ câu này không hỏi lại hai chỗ đó).
- Phần phụ nằm ngoài quyết định chính, ghi để biết: ánh xạ một-nhiều và thiết kế bảng `addresses` (câu 2); mẫu Python và điều kiện idempotent cho biến đổi tại chỗ như chuẩn hoá số điện thoại (câu 3); cơ chế enum Postgres, `ALTER COLUMN … TYPE … USING`, đổi kiểu có ghi lại cả bảng không (câu 4); mẫu `WHERE … IS NULL` có thể lặp mãi trên dòng không điền được, mẫu duyệt theo khoá chính hợp hơn (câu 6, suy luận của chủ thể ngoài skill).
- Mâu thuẫn nhỏ đã ghi ở các lượt trước vẫn còn, tôi đã đối chiếu lại file: `references/postgres-safe-ddl.md` mục 3 bước 4 gộp ngừng ghi cột cũ và `DROP COLUMN` trong một migration, còn `SKILL.md` mục 3 và `references/postgres-safe-ddl.md` mục 4 tách thành deploy rồi mới bỏ cột ở migration sau.

## Lịch sử

Lượt trước (2026-10-04, `skill_sha` `6a835f88c7cda24d3e9b46ebb0fb73a94519bb79`, bản trước khi viết lại `rehearsal.md` phòng sạch, người soạn `a4d7a065604b7ced6`, chủ thể `a47e3e101dea21a8b`): strict 4/7 (+3 partial, 0 fail), points-right 7/7, cùng bộ câu hỏi, cùng ba câu "một phần" (1, 5, 6).
