---
skill: database-migrations
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 3afc7c5247e2c0b05cfac19de5268a1d48a2ec9f
date: 2026-10-04
result: "strict 6/8 (+2 partial, 0 fail) — below threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 8/8"
agent_ids:
  questions: a27aba66b6a05efa7
  answers: afca6bc43ff323c6c
---

Đã đọc: `<gốc worktree>\skills\database-migrations\SKILL.md`

# Thử truy xuất - database-migrations

> **Kết luận:** strict 6/8 (+2 partial, 0 fail), points-right 8/8: dưới ngưỡng (5/7 câu tình huống Đạt, 71 % so với ngưỡng 80 %; câu ranh giới Đạt). Chạy lại (lượt 3) vì `source:` của `SKILL.md` và chú thích đầu `references/rehearsal.md` đổi (gỡ lời khẳng định phòng sạch, quyết định `DN6`) làm lệch `skill_sha`; `description` không đổi.
> Bộ câu mới, người soạn và chủ thể đều là agent mới. So lượt trước (strict 3/7, 4 một phần) là tốt hơn, không đỏ hơn; hai câu còn "một phần" (4 và 6) đúng là hai chỗ thiếu nội dung ghi ở cuối file, không phải trỏ sai.

Tám câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description`, lĩnh vực, tên các skill khác và cột câu hỏi của bộ cũ để không lặp); nguyên văn câu hỏi, file nháp
"Mục mong đợi" (mtime `2026-10-04 00:27:43 +0700`), bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/database-migrations-retrieval-rerun-after-dn6.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 8 là câu ranh giới: đáp án của người soạn là `deployment`, đã được đối chiếu với `description` của skill đích và nhận là đúng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Đội muốn đổi tên cột `customers.phone` thành `phone_e164` trên bảng 12 triệu dòng, và ORM của hai service đang map cứng tên cột cũ. Có thể đổi tên một phát bằng một câu lệnh không, hay phải làm theo trình tự nào để không service nào bị lỗi giữa chừng? | `references/postgres-safe-ddl.md` › 3. Đổi tên cột (không gián đoạn) + `SKILL.md` › 3. Mở rộng → chuyển → thu hẹp + › 1 nguyên tắc 6 | `SKILL.md` › 1 (điểm 6), › 3, › 6; `references/postgres-safe-ddl.md` › 3, › 5; nói rõ skill không có chỉ dẫn riêng cho ORM map cứng tên cột | Đạt |
| 2 | Cuối tuần này sẽ chạy migration xoá hai cột cũ và đổi kiểu một cột tiền từ INTEGER sang NUMERIC(12,2) trên bản production 600 GB. Trước khi bấm chạy thật, nhóm nên diễn tập thế nào, trên dữ liệu nào, và cần đo/ghi lại những gì để quyết định có dám chạy hay không? | `references/rehearsal.md` › 2. Các bước (phân loại, đường lùi, diễn tập tiến-kiểm-lùi-tiến, đo thời gian/khoá/lag/lỗi/dữ liệu khớp) + › 3. Đầu ra + `SKILL.md` › 5 (rủi ro cao bắt buộc diễn tập) | `SKILL.md` › 2, › 5; `references/rehearsal.md` › 1, › 2, › 3, › 4; `references/postgres-safe-ddl.md` › 4; nói rõ skill không có công thức đổi kiểu INTEGER sang NUMERIC | Đạt |
| 3 | Đồng nghiệp gửi PR có một file migration vừa thêm cột `orders.region_id NOT NULL` không giá trị mặc định, vừa tạo index thường trên bảng 80 triệu dòng, vừa chạy UPDATE điền dữ liệu, tất cả trong cùng một giao dịch. Bạn là người rà soát: cần soi những điểm nào và đề nghị sửa ra sao? | `SKILL.md` › 2. Kiểm trước khi áp migration + › 6. Phản mẫu + `references/postgres-safe-ddl.md` › 1, › 2, › 5 (+ › 1 nguyên tắc 3 tách schema/dữ liệu) | `SKILL.md` › 1 (điểm 3, 4), › 2, › 6; `references/postgres-safe-ddl.md` › 1, › 2, › 5; `references/rehearsal.md` › 2 | Đạt |
| 4 | Công ty đang chuyển backend từ Django ORM sang SQLAlchemy và lịch sử schema hiện nằm trong 140 file migration của Django. Làm sao chuyển sang công cụ migration mới mà DB production đang chạy không bị tạo lại hay mất dấu phiên bản đã áp? | không có mục riêng (không có nội dung chuyển công cụ / đặt mốc phiên bản); `SKILL.md` › 4 Alembic và `references/django-golang-migrate.md` › 1 chỉ gần liên quan | `SKILL.md` › 1 (điểm 5), › 4; `references/django-golang-migrate.md` › 1; nói rõ skill không có hướng dẫn chuyển lịch sử migration giữa hai công cụ | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 5 | Migration đã chạy lên production lúc 2h sáng: thêm một bảng mới và xoá cột `legacy_code`; đến 9h phát hiện báo cáo cuối tháng vẫn cần cột đó. Lúc này hoàn tác bằng cách nào, và lẽ ra phải chuẩn bị gì từ trước để việc lùi lại an toàn? | `SKILL.md` › 1 nguyên tắc 2 (production chỉ đi tới) + › 3 (bỏ cột) + `references/postgres-safe-ddl.md` › 4 + `references/rehearsal.md` › 2 bước 2 (đường lùi, sao lưu đã khôi phục thử) | `SKILL.md` › 1 (điểm 2, 5), › 2, › 3; `references/rehearsal.md` › 2, › 4; `references/postgres-safe-ddl.md` › 4; nói rõ skill không có thủ tục khôi phục chi tiết lúc sự cố | Đạt |
| 6 | Một cột `products.sku` hiện cho phép NULL và có khoảng 2% dòng NULL, nay muốn đặt NOT NULL cùng ràng buộc UNIQUE trên bảng 25 triệu dòng đang có người ghi liên tục. Đi theo các bước nào để không khoá bảng quá lâu? | `references/postgres-safe-ddl.md` › 1 (NOT NULL qua backfill → CHECK NOT VALID → VALIDATE → SET NOT NULL) + › 2 (index CONCURRENTLY); cách đặt UNIQUE không có trong skill | `SKILL.md` › 2, › 6; `references/postgres-safe-ddl.md` › 1, › 2, › 5; `references/rehearsal.md` › 2; nói rõ skill không có cách đặt UNIQUE | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 7 | Nhóm định thêm một index để tăng tốc tìm kiếm theo `email` trên bảng `users` 5 triệu dòng, và hỏi nên tạo thế nào cho an toàn khi hệ thống đang chạy, có cần xoá index cũ trùng ý nghĩa không. (Lưu ý: lần này không có truy vấn chậm cụ thể nào cần chẩn đoán.) | `references/postgres-safe-ddl.md` › 2. Thêm index không gián đoạn + `SKILL.md` › 4 (autocommit_block) + › 6 phản mẫu index thường trên bảng lớn | `SKILL.md` › 2, › 4; `references/postgres-safe-ddl.md` › 2; `references/django-golang-migrate.md` › 1; nói rõ skill không có nội dung xoá index trùng ý nghĩa | Đạt |
| 8 | Nhóm chuẩn bị đưa một thay đổi schema lên production và đang bàn về việc viết Dockerfile mới cho service, thêm bước CI tự chạy migration trước khi khởi động container, và chiến lược rolling hay blue-green để các bản cũ/mới của service cùng chạy được trong lúc chuyển. Họ hỏi nên thiết kế pipeline và cách phát hành như thế nào. | mục khác: skill `deployment` (Dockerfile, CI chạy migration trước container, rolling/blue-green) | mục khác: `deployment` (chủ thể nhận việc đóng gói, pipeline, rollout nằm ngoài skill; chỉ nêu phần ranh giới `SKILL.md` › 1 điểm 6, › 3) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Chuyển lịch sử migration từ Django ORM sang SQLAlchemy/Alembic (đặt mốc phiên bản hiện tại để DB đang chạy không bị áp lại, xử lý bảng lịch sử của Django): không có; chủ thể nói rõ và không bịa quy trình (câu 4).
- Đặt `UNIQUE` trên bảng lớn đang ghi (dựng unique index đồng thời rồi gắn thành ràng buộc), xử lý dòng trùng sẵn có: không có; phần `NOT NULL` qua `CHECK … NOT VALID` thì có (câu 6).
- Phần phụ nằm ngoài quyết định chính, ghi để biết: ORM map cứng tên cột khi đổi tên song song (câu 1); công thức đổi kiểu INTEGER sang NUMERIC trên bảng lớn (câu 2); giá trị điền cho cột mới `NOT NULL` và khoá ngoại (câu 3); thủ tục khôi phục dữ liệu cột đã `DROP` và kiểm kê consumer ngoài ứng dụng trước khi bỏ cột (câu 5); xoá index cũ trùng ý nghĩa (câu 7).
- Mâu thuẫn nhỏ chủ thể phát hiện (câu 1): `references/postgres-safe-ddl.md` mục 3 bước 4 gộp ngừng ghi cột cũ và `DROP COLUMN` trong một migration, còn `SKILL.md` mục 3 tách thành deploy rồi mới bỏ cột ở migration sau.
