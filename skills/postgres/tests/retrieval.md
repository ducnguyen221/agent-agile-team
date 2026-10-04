---
skill: postgres
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 963d141988d565844c46768b15bb0382b39cdf06
date: 2026-10-04
result: "strict 6/6 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 6/6"
agent_ids:
  questions: "bộ câu cũ giữ nguyên, không soạn mới"
  answers: a99082a28f9f7b923
---

Đã đọc: `<gốc worktree>/skills/postgres/SKILL.md` và `<gốc worktree>/skills/postgres/references/diagnostics.md`

# Thử truy xuất - postgres

> **Kết luận:** strict 6/6: đạt ngưỡng. Sau `TK11.8` năm câu tình huống đều Đạt (lượt trước 5/6 Đạt hẳn, 1 Một phần; các ý một phần: `lock_timeout`, PgBouncer, index ghép + một phần, con trỏ cho khoá không duy nhất, `jsonb` hay bảng riêng); câu ranh giới trả `database-migrations`.

Bộ câu hỏi giữ nguyên chữ của lượt trước (bộ câu cũ giữ nguyên, không soạn mới); bộ câu mới là việc của `TK13`. Cột "Mục kỳ vọng" ghi vào file nháp
`.tmp/postgres-expected.md` **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm). Bài trả lời của chủ thể (id ở
`agent_ids`) và bảng chấm ở `evidence/TK11/postgres-retrieval.md` trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời,
đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Bảng `audit_logs` ~200 triệu dòng, phân trang `LIMIT 50 OFFSET n` càng sâu càng chậm. Chuyển sang kiểu phân trang nào để trang thứ 100.000 vẫn nhanh, cần index gì? | `SKILL.md` › 4 (phân trang con trỏ, khoá không duy nhất `(created_at, id)`, so sánh hàng, không nhảy trang số N) + › 2 (index `(created_at DESC, id DESC)`) | `SKILL.md` › 4. Truy vấn và đồng thời; › 2. Chọn index | Đạt |
| 2 | 12 instance FastAPI × pool 20 kết nối, `too many connections`, vài kết nối `idle in transaction`. Đặt `max_connections`, PgBouncer, `statement_timeout`, `idle_in_transaction_session_timeout`, `lock_timeout` thế nào? | `references/diagnostics.md` › 3 (`lock_timeout`, `statement_timeout`, `idle_in_transaction_session_timeout` theo vai trò), › 3.1, › 3.2 (12 × 20 = 240 vượt `max_connections`; giảm pool hoặc PgBouncer `pool_mode = transaction`, giới hạn của chế độ này) + `SKILL.md` › 4 | `references/diagnostics.md` › 3.2; › 3.1; › 3 | Đạt |
| 3 | Thêm cột `deleted_at` vào `orders`, muốn danh sách đơn đang hoạt động nhanh. Định tạo partial index `WHERE deleted_at IS NULL` trên `(customer_id, created_at DESC)`: cú pháp đúng không, khi nào partial index có lợi hơn index thường? | `SKILL.md` › 2 (hàng "ghép + một phần" `(customer_id, created_at DESC) WHERE deleted_at IS NULL`, khi nào index một phần có lợi, truy vấn phải chứa điều kiện) | `SKILL.md` › 2. Chọn index | Đạt |
| 4 | `EXPLAIN ANALYZE` truy vấn join 3 bảng: ước lượng `rows=10`, thực tế `rows=480000`, Nested Loop 40 giây. Đọc plan thế nào, xử lý ra sao (`ANALYZE`, statistics, viết lại)? | `references/diagnostics.md` › 1 (ước lượng lệch nhiều bậc → `ANALYZE`; Nested Loop vế ngoài lớn → sửa ước lượng trước) | `references/diagnostics.md` › 1. Đọc kế hoạch thực thi | Đạt |
| 5 | Cột `tags` kiểu `text` chứa chuỗi JSON, cần lọc bản ghi có tag `"vip"` và đôi khi lấy khoá lồng. Đổi sang `jsonb` hay tách bảng riêng, dùng index GIN thế nào? | `SKILL.md` › 3 (đoạn "`jsonb` hay bảng riêng") + › 2 (GIN) + trỏ `database-migrations` cho việc đổi `text` → `jsonb` | `SKILL.md` › 3. Kiểu dữ liệu và ràng buộc; › 2. Chọn index | Đạt |
| 6 | Thêm cột `NOT NULL` kèm mặc định vào `users` 80 triệu dòng đang chạy production, backfill theo lô không khoá bảng. Quy trình migration zero-downtime từng bước? | mục khác: skill `database-migrations` (từ `SKILL.md` › 1) | mục khác: `database-migrations` (từ `SKILL.md` › 1), kèm agent `database-reviewer` | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- `description` đã hứa "connection and timeout settings"; thân skill nay có `lock_timeout` và PgBouncer ở `references/diagnostics.md` mục 3.1–3.2.
- Chủ thể nêu: không có phần viết lại truy vấn hay tăng statistics target (câu 4); không nêu `jsonb_ops` / `jsonb_path_ops` hay cú pháp index biểu thức (câu 5).
- Nguồn của phần thêm ở `TK11.8`: tài liệu PostgreSQL (Client Connection Defaults), tài liệu PgBouncer (cấu hình, bảng tính năng theo chế độ gộp).
