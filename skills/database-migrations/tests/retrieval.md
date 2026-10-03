---
skill: database-migrations
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: ee60372d2429a3e3db75358226396fbcf0c3537b
date: 2026-10-03
result: pass 6/6
---

Đã đọc: `<gốc worktree>\skills\database-migrations\SKILL.md`

# Thử truy xuất — database-migrations

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥5/6), trong đó câu 4 chỉ Đạt một phần vì skill không có phần dựng Alembic từ
> đầu. Chủ thể trỏ đúng tệp `references/` cho thêm cột, backfill theo lô và diễn tập; nhận ra câu ranh giới thuộc
> agent `database-reviewer`.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Câu 6 là câu ranh giới: đáp án của
người soạn (agent `database-reviewer`) đã được người chấm đối chiếu với `agents/database-reviewer.md` (reviewer
chỉ đọc cho SQL, schema, khoá) và nhận là đúng.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần
chi tiết phụ còn thiếu ghi ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được cho quyết định đó.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Cần thêm cột `orders.channel NOT NULL` vào bảng 80 triệu dòng mà không được khóa bảng. Các bước an toàn là gì? | `references/postgres-safe-ddl.md` › 1. Thêm cột (+ `SKILL.md` › 3, 6) | `references/postgres-safe-ddl.md` › 1. Thêm cột; `SKILL.md` › 6. Phản mẫu | Đạt |
| 2 | Viết script điền `customers.region` từ `address` cho bảng 12 triệu dòng, có thể bị ngắt giữa chừng. Chia batch thế nào để chạy lại được mà không ghi đè sai? | `references/postgres-safe-ddl.md` › 5. Cập nhật dữ liệu lớn (+ `SKILL.md` › 2) | `references/postgres-safe-ddl.md` › 5; `references/rehearsal.md` › 2, bước 5; `SKILL.md` › 2 | Đạt |
| 3 | PR có dòng `CREATE INDEX idx_events_user ON events(user_id)` sẽ chạy trên production đang tải cao. Reviewer cần soát những gì trong migration này? | `SKILL.md` › 2. Kiểm trước khi áp migration + `references/postgres-safe-ddl.md` › 2. Thêm index | `SKILL.md` › 2; `references/postgres-safe-ddl.md` › 2. Thêm index không gián đoạn | Đạt |
| 4 | Dự án đang chạy SQL thủ công, nay muốn dựng Alembic cho đúng. Cấu trúc thư mục, quy ước đặt tên và thứ tự áp dụng nên thế nào? | `SKILL.md` › 4. Alembic | `SKILL.md` › 4. Alembic (chủ thể ghi "chỉ trả lời một phần") | Đạt (một phần: có đặt tên và thứ tự, không có thư mục và cách đưa DB đang chạy vào Alembic) |
| 5 | Migration đã qua staging và sắp chạy trên dữ liệu production thật. Cần kiểm gì trước khi chạy và có đường lùi nào nếu hỏng giữa chừng? | `references/rehearsal.md` (+ `SKILL.md` › 2, 5) | `references/rehearsal.md` › 2, bước 2 và 6; `SKILL.md` › 1, 2 | Đạt |
| 6 | File migration `0042_add_index.sql` đã viết xong, cần một người soát độc lập, chỉ đọc, chấm riêng phần dữ liệu và ghi phát hiện có mức độ. Giao cho ai? | mục khác: agent `database-reviewer` | mục khác: agent `database-reviewer` (từ `SKILL.md` › 5. Tra cứu) | Đạt |

## Thiếu nội dung / mâu thuẫn

- `skills/database-migrations/SKILL.md:58-93` (mục 4, Alembic) mà `description` hứa "setting up migration tooling": chỉ có lệnh, mẫu
  một revision và quy tắc autogenerate. Thiếu cấu trúc thư mục (`alembic init`, `env.py`, `versions/`, mẫu tên file) và đường đưa một
  DB đang chạy bằng SQL thủ công vào Alembic (revision gốc, đánh dấu trạng thái hiện tại). Đề xuất: thêm một mục "Dựng mới / đưa DB
  có sẵn vào Alembic" khoảng 8 dòng, hoặc ghi rõ skill không phủ phần này.
- Không có mâu thuẫn giữa `SKILL.md` và các tệp `references/` trong sáu câu này.
