---
skill: postgres
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: a92444b475e862f4d2370506200cc449ab14d49e
date: 2026-10-03
result: pass 5/6
---

Đã đọc: `<gốc worktree>\skills\postgres\SKILL.md`

# Thử truy xuất — postgres

> **Kết luận:** 5/6 câu Đạt (ngưỡng ≥5/6). Câu 2 Không đạt vì thiếu nội dung: `description` hứa "table bloat" nhưng skill chỉ
> có câu truy vấn phát hiện, không có cách xử lý. Chủ thể trỏ đúng chỗ duy nhất có liên quan và nói thẳng phần xử lý không có,
> không bịa. Câu 4 (Row Level Security) chỉ Đạt một phần vì skill có một ví dụ policy theo `auth.uid()`, không có mẫu theo tenant.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Câu 6 là câu ranh giới: đáp án của
người soạn (agent `security-reviewer`) đã được người chấm đối chiếu với `SKILL.md` mục 5 ("chạm RLS, quyền, dữ liệu
nhạy cảm → kéo agent `security-reviewer`") và `agents/security-reviewer.md`, và nhận là đúng; `database-reviewer` cũng
hợp lý cho phần SQL nhưng RLS và quyền được skill chỉ đích danh cho `security-reviewer`.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần
chi tiết phụ còn thiếu ghi ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được cho quyết định đó.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Query `SELECT * FROM invoices WHERE status = 'pending' ORDER BY created_at LIMIT 50` chạy 4 giây, `EXPLAIN` hiện Seq Scan trên 30 triệu dòng. Nên tạo index thế nào? | `SKILL.md` › 2. Chọn index (+ `references/diagnostics.md` › 1) | `SKILL.md` › 2. Chọn index; `references/diagnostics.md` › 1. Đọc kế hoạch thực thi | Đạt |
| 2 | Bảng `events` bị bloat sau khi xóa hàng loạt, autovacuum chạy mãi không giảm dung lượng. Chẩn đoán và xử lý ra sao? | `references/diagnostics.md` › 2 chỉ có phát hiện; cách xử lý không có, `description` hứa "table bloat" | `references/diagnostics.md` › 2. Truy vấn chẩn đoán (câu "Bloat signal"); chủ thể ghi phần xử lý không có | **Không đạt (thiếu nội dung)** |
| 3 | Thiết kế bảng `payments`: nên chọn kiểu dữ liệu nào cho tiền, thời gian và khóa chính? | `SKILL.md` › 3. Kiểu dữ liệu và ràng buộc | `SKILL.md` › 3. Kiểu dữ liệu và ràng buộc | Đạt |
| 4 | Ứng dụng đa tenant, cần để mỗi tenant chỉ thấy hàng của mình trong bảng `documents` bằng Row Level Security. Viết policy thế nào? | `SKILL.md` › 5. Bảo mật (một ví dụ policy) | `SKILL.md` › 5. Bảo mật; `SKILL.md` › 2 (index cột trong policy) | Đạt (một phần: chỉ ví dụ `auth.uid()`, không có mẫu theo tenant) |
| 5 | Muốn dùng một bảng Postgres làm hàng đợi job, nhiều worker lấy job song song mà không đụng nhau. Câu lệnh và thiết lập nào phù hợp? | `SKILL.md` › 4. Truy vấn và đồng thời (Hàng đợi việc) | `SKILL.md` › 4. Truy vấn và đồng thời (Hàng đợi việc) | Đạt |
| 6 | Policy RLS trên bảng `invoices` đã viết xong, cần một agent bảo mật soát xem có rò rỉ dữ liệu giữa các tenant không. Giao cho ai? | mục khác: agent `security-reviewer` | mục khác: agent `security-reviewer` (từ `SKILL.md` › 5) | Đạt |

## Thiếu nội dung / mâu thuẫn

- **Thiếu nội dung, quan trọng.** `skills/postgres/SKILL.md:3` (`description`: "troubleshooting a slow query or table bloat") và
  `skills/postgres/references/diagnostics.md:41-45`: chỉ có câu truy vấn đo số dòng chết và lần vacuum gần nhất. Không có: vì sao autovacuum không trả
  dung lượng cho hệ điều hành, khi nào dùng `VACUUM FULL` hay `pg_repack` (và khoá mà chúng cần), giao dịch dài hay slot sao chép giữ vacuum lại, chỉnh
  `autovacuum_*` cho từng bảng. Đề xuất: thêm mục "Bảng phình" khoảng 10 dòng vào `diagnostics.md`, hoặc bỏ "table bloat" khỏi `description`.
- `skills/postgres/SKILL.md:85-86` (mục 5, RLS): chỉ có một dòng ví dụ theo `auth.uid()` của Supabase. Không có `ENABLE`/`FORCE ROW LEVEL SECURITY`, mẫu `CREATE POLICY`
  theo tenant (ví dụ khoá tenant lấy từ `current_setting`), hay cách kiểm policy. Đề xuất: một khối SQL 5-6 dòng cho mẫu đa tenant.
- Không có mâu thuẫn giữa `SKILL.md` và `references/diagnostics.md` trong sáu câu này.
