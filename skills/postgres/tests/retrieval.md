---
skill: postgres
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: b71dbb049e18e89e476a2c8d723fa60c6695e7fe
date: 2026-10-03
result: pass 6/6, 3 partial
agent_ids:
  questions: ad2bcf515a755bb2d
  answers: a25a6768d8f143aa2
---

Đã đọc: `<gốc worktree>\skills\postgres\SKILL.md` (và các file trong `references/` mà `SKILL.md` trỏ tới, nếu có)

# Thử truy xuất — postgres

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥4/5 câu tình huống và câu ranh giới), trong đó 3 câu chỉ Đạt một phần (câu 2, 3, 5). Lỗ hổng "table bloat" của lượt
> trước đã hết vì `description` không còn hứa nó. Chủ thể trỏ đúng mục ở cả sáu câu và nói thẳng phần skill không có (`lock_timeout`, PgBouncer, so sánh
> `jsonb` với bảng riêng) thay vì bịa. Câu 5 là câu sát ngưỡng nhất: skill chỉ có hàng GIN trong bảng chọn index, quyết định "đổi `jsonb` hay tách bảng"
> không có đáp án.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực, kèm danh sách chủ đề của bộ cũ để không lặp); lượt này là **bộ câu mới** chạy lại sau khi `X2` đổi nội dung skill
(chạy lại theo giao thức rerun-2). Cột "Mục kỳ vọng" do người chấm ghi vào file nháp **trước khi** giao chủ thể (mtime file nháp 2026-10-03 21:39:36 +0700 (21:39:36,96), sớm hơn lệnh giao chủ thể đầu tiên); mục kỳ vọng ghi theo cây MỚI.
Câu 6 là câu ranh giới, đáp án do người soạn nêu và người chấm đối chiếu với `description` của skill đáp.
Nguyên văn câu hỏi của người soạn, file nháp kỳ vọng, output TRỌN của chủ thể (đường dẫn thư mục người dùng giữ nguyên ở đó, còn ở đây lược thành `<gốc worktree>` vì repo chặn tên người dùng)
và số lượt công cụ: hồ sơ sprint của lớp riêng, `evidence/TK12-green/postgres-retrieval-rerun-2.md`.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần chi tiết phụ còn thiếu ghi trong ngoặc và ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được.
Ngưỡng: ≥4/5 câu tình huống Đạt và câu ranh giới Đạt. `result` ghi cả số "một phần".

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Bảng `audit_logs` ~200 triệu dòng, phân trang `LIMIT 50 OFFSET n` càng sâu càng chậm. Chuyển sang kiểu phân trang nào để trang thứ 100.000 vẫn nhanh, cần index gì? | `SKILL.md` › 4. Truy vấn và đồng thời (phân trang con trỏ) + › 2. Chọn index | `SKILL.md` › 4. Truy vấn và đồng thời; › 2. Chọn index; › 6. Lỗi hay gặp (dòng `OFFSET` lớn) | Đạt (một phần: không có mẫu con trỏ cho khoá sắp xếp không duy nhất như `created_at` kèm `id`, không có cách nhảy tới trang số N) |
| 2 | 12 instance FastAPI × pool 20 kết nối, `too many connections`, vài kết nối `idle in transaction`. Đặt `max_connections`, PgBouncer, `statement_timeout`, `idle_in_transaction_session_timeout`, `lock_timeout` thế nào? | `references/diagnostics.md` › 3. Cấu hình mẫu + `SKILL.md` › 4 (giao dịch ngắn); PgBouncer và `lock_timeout` không có tên trong skill | `references/diagnostics.md` › 3. Cấu hình mẫu; `SKILL.md` › 4. Truy vấn và đồng thời; › 6 | Đạt (một phần: có pool phía trước thay vì nâng `max_connections`, `idle_in_transaction_session_timeout`, `statement_timeout` theo vai trò; không có `lock_timeout`, không PgBouncer, không con số cho 12 instance) |
| 3 | Thêm cột `deleted_at` vào `orders`, muốn danh sách đơn đang hoạt động nhanh. Định tạo partial index `WHERE deleted_at IS NULL` trên `(customer_id, created_at DESC)`: cú pháp đúng không, khi nào partial index có lợi hơn index thường? | `SKILL.md` › 2. Chọn index (hàng index một phần: xoá mềm; hàng index ghép). Không có ví dụ ghép + một phần cùng lúc | `SKILL.md` › 2. Chọn index (hàng "chỉ một phần dòng được truy vấn") | Đạt (một phần: có khuôn `CREATE INDEX … WHERE deleted_at IS NULL`; chủ thể ghi phần `DESC` là suy từ khuôn; tiêu chí "khi nào có lợi" chỉ nói bằng ví dụ, không định lượng) |
| 4 | `EXPLAIN ANALYZE` truy vấn join 3 bảng: ước lượng `rows=10`, thực tế `rows=480000`, Nested Loop 40 giây. Đọc plan thế nào, xử lý ra sao (`ANALYZE`, statistics, viết lại)? | `references/diagnostics.md` › 1. Đọc kế hoạch thực thi (ước lượng lệch nhiều bậc → `ANALYZE`; Nested Loop vế ngoài lớn → sửa ước lượng trước) | `references/diagnostics.md` › 1. Đọc kế hoạch thực thi; `SKILL.md` › Kết luận | Đạt (chủ thể ghi rõ skill không có cách viết lại truy vấn hay tăng `default_statistics_target`) |
| 5 | Cột `tags` kiểu `text` chứa chuỗi JSON, cần lọc bản ghi có tag `"vip"` và đôi khi lấy khoá lồng. Đổi sang `jsonb` hay tách bảng riêng, dùng index GIN thế nào? | `SKILL.md` › 2. Chọn index (hàng GIN cho `jsonb @>`) — chỉ một phần: so sánh `jsonb` với bảng riêng và cách đổi `text` → `jsonb` không có | `SKILL.md` › 2. Chọn index (hàng GIN); › 6 (đổi kiểu tốn khoá bảng) | Một phần (có cú pháp GIN và nhắc đổi kiểu tốn khoá bảng; quyết định "jsonb hay tách bảng" không có đáp án; chủ thể nói thẳng) |
| 6 | Thêm cột `NOT NULL` kèm mặc định vào `users` 80 triệu dòng đang chạy production, backfill theo lô không khoá bảng. Quy trình migration zero-downtime từng bước? | mục khác: skill `database-migrations` (từ `SKILL.md` › 1) | mục khác: `database-migrations` (từ `SKILL.md` › 1. Khi nào dùng — và khi nào sang chỗ khác); kèm agent `database-reviewer` để review | Đạt (ranh giới) |

## Thiếu nội dung / mâu thuẫn

- **Thiếu nội dung.** `description` hứa "setting connection and timeout settings" (`skills/postgres/SKILL.md:3`) nhưng `lock_timeout` không xuất hiện ở cả `SKILL.md` lẫn
  `references/diagnostics.md`, và không có chỉ dẫn về bộ gộp kết nối ngoài một câu "đặt pool phía trước" (`diagnostics.md` mục 3). Đề xuất (điều phối quyết, vì đổi `skill_sha`): thêm
  vào mục 3 của `diagnostics.md` một dòng `lock_timeout` cho vai trò ứng dụng và một dòng cách tính số kết nối (số instance × cỡ pool so với `max_connections`).
- **Thiếu nội dung, nhẹ.** `SKILL.md` mục 2 không có mẫu index ghép kèm một phần (`(customer_id, created_at DESC) WHERE deleted_at IS NULL`), mục 4 không có phân trang con trỏ cho
  khoá không duy nhất, và không chỗ nào nói chọn `jsonb` hay tách bảng (câu 5). Câu 5 là chỗ kém nhất của lượt này; nếu muốn đóng, thêm 2 dòng vào mục 3 (kiểu dữ liệu) về `jsonb` so với bảng quan hệ.
- Không có mâu thuẫn giữa `SKILL.md` và `references/diagnostics.md` trong sáu câu này.
