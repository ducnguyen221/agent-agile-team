---
skill: worktrees
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: fbcbc7509618b5c69a8f372a7125c106fb3719db
date: 2026-10-04
result: "strict 6/6 (+0 partial, 0 fail) — at threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 6/6"
agent_ids:
  questions: "bộ câu cũ giữ nguyên, không soạn mới"
  answers: a71a62ffa2ff7a5d7
---

Đã đọc: `<gốc worktree>/skills/worktrees/SKILL.md` (không có `references/`)

# Thử truy xuất - worktrees

> **Kết luận:** strict 6/6: đạt ngưỡng. Sau `TK11.6` năm câu tình huống đều Đạt (lượt trước 3/6 Đạt hẳn, 3 Một phần: tên nhánh và `.env.local`, mỗi agent một worktree, dọn worktree mồ côi); câu ranh giới trả `github-ops`.

Bộ câu hỏi giữ nguyên chữ của lượt trước (bộ câu cũ giữ nguyên, không soạn mới); bộ câu mới là việc của `TK13`. Cột "Mục kỳ vọng" ghi vào file nháp
`.tmp/worktrees-expected.md` **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm). Bài trả lời của chủ thể (id ở
`agent_ids`) và bảng chấm ở `evidence/TK11/worktrees-retrieval.md` trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời,
đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Nhận task brief cho TK7, muốn chạy trong chỗ làm việc tách biệt để hỏng thì vứt đi mà không ảnh hưởng checkout đang mở. Tạo bằng cách nào, đặt tên nhánh ra sao, làm gì ngay sau khi tạo trước khi code? | `SKILL.md` › 1 (dò), › 2 (1a/1b, `git worktree add`, đoạn "Tên nhánh"), › 4 (baseline, ghi PROGRESS) | `SKILL.md` › 2. Bước 1 — tạo không gian tách biệt; › 1; › 4 | Đạt |
| 2 | Repo Node, worktree mới trống trơn: không `node_modules`, không `.env.local`, build báo thiếu dependency. Dựng môi trường theo thứ tự nào để agent làm việc được ngay? | `SKILL.md` › 3 (dựng dự án `npm ci`; đoạn "File không theo dõi không đi theo sang worktree": `.env.local` chép từ `.env.example`, không chép secret thật) + › 4 | `SKILL.md` › 3. Bước 2 — dựng dự án | Đạt |
| 3 | Hai agent cùng repo, một sửa module auth, một sửa module báo cáo, cả hai định `git checkout -b` ngay trong thư mục hiện tại. Chia chỗ làm việc để không dẫm lên index và working tree của nhau thế nào, mỗi agent cấp đường dẫn nào? | `SKILL.md` › 2 (đoạn "Nhiều agent song song": mỗi agent một worktree + nhánh riêng, đường dẫn tuyệt đối, phạm vi file không giao nhau) + › 5 | `SKILL.md` › 2. Bước 1 (đoạn Nhiều agent song song) | Đạt |
| 4 | Đã gộp nhánh vào main, test xanh, muốn xoá worktree cùng nhánh. Trước khi xoá cần xác nhận gì để không mất công việc chưa lưu, thứ tự lệnh dọn đúng là gì? | `SKILL.md` › 6 ("Trước khi xoá một worktree của mình": `status` sạch, `log nhánh-đích..nhánh` rỗng, `git worktree remove` không `--force`, `git branch -d`, `prune`) | `SKILL.md` › 6. Dọn khi xong | Đạt |
| 5 | Worktree cho task dài, hôm sau không nhớ nhánh nào gắn thư mục nào, còn thư mục mồ côi từ task cũ. Liệt kê, kiểm tra, dọn worktree còn sót (kể cả entry trỏ thư mục đã bị xoá tay) thế nào? | `SKILL.md` › 6 ("Worktree còn sót và thư mục mồ côi": `git worktree list`, `prune --dry-run -v`, `prune`, thư mục không có trong list, `repair`, lock) | `SKILL.md` › 6. Dọn khi xong (đoạn Worktree còn sót và thư mục mồ côi) | Đạt |
| 6 | Vừa mở PR từ nhánh sprint, cần xem trạng thái check CI đang đỏ, đọc log run Actions bị fail và gắn label cho PR. Dùng gì? | mục khác: skill `github-ops` (từ `SKILL.md` › 7 Tra nhanh) | mục khác: `github-ops` (từ `SKILL.md` › 7. Tra nhanh) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có. Luật `.worktrees/` vào `.gitignore` (hoặc `.git/info/exclude`) trước khi tạo có ở mục 2.
- Chủ thể nêu: skill không cấp sẵn tên thư mục cụ thể cho từng agent, chỉ nêu dạng phẳng (câu 3).
- Nguồn của phần thêm ở `TK11.6`: tài liệu `git worktree` (list, remove, prune, lock, repair) và `git check-ref-format`.
