---
skill: worktrees
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: c4f7534eb458e5167d34eec0e660f03c4c1e3718
date: 2026-10-03
result: below threshold (2/5 situations pass, 3 partial, 0 fail; boundary pass)
agent_ids:
  questions: ab40a8772df23badb
  answers: a9acf3ec649d4ddc0
---

Đã đọc: `<gốc worktree>\skills\worktrees\SKILL.md` (và các file trong `references/` mà `SKILL.md` trỏ tới, nếu có)

# Thử truy xuất — worktrees

> **Kết luận:** dưới ngưỡng ≥4/5 câu tình huống Đạt: 2/5 Đạt (câu 1, 2), 3/5 Một phần (câu 3, 4, 5), 0 Không đạt; câu ranh giới (câu 6) chủ thể trỏ đúng `github-ops`. Skill chỉ có `SKILL.md` (không `references/`); chủ thể đọc một lần,
> trỏ đúng mục ở mọi câu, không bịa, và đánh dấu rõ chỗ nào là suy luận (câu 3: "mỗi agent một worktree riêng" là suy từ mô hình worktree) và chỗ skill không có (đặt tên nhánh, `.env.local`, danh sách kiểm trước khi xoá,
> dọn entry trỏ thư mục đã xoá tay). Dòng mới ở mục 7 về lỗi "đã được checkout ở worktree khác" được chủ thể dùng đúng ở câu 5 (`git worktree list`).

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực, kèm danh sách chủ đề của các bộ cũ để không lặp); lượt này là **bộ câu mới** chạy lại sau commit `7e296f1` (thêm dòng lỗi "branch đã được checkout ở worktree khác" vào mục 7).
Cột "Mục kỳ vọng" do người chấm ghi vào file nháp **trước khi** giao chủ thể (mtime file nháp 2026-10-03 21:54:53 +0700 (21:54:53,42), sớm hơn lệnh giao chủ thể); mục kỳ vọng ghi theo cây hiện tại.
Câu 6 là câu ranh giới, đáp án do người soạn nêu và người chấm đối chiếu với `description` của skill đáp.
Nguyên văn câu hỏi của người soạn, file nháp kỳ vọng, output TRỌN của chủ thể (đường dẫn thư mục người dùng giữ nguyên ở đó, còn ở đây lược thành `<gốc worktree>` vì repo chặn tên người dùng)
và số lượt công cụ: hồ sơ sprint của lớp riêng, `evidence/TK12-green/worktrees-retrieval-rerun-3.md`.

Cách chấm: **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính;
**Không đạt** = trỏ sai hoặc bịa. Ngưỡng: ≥4/5 câu tình huống Đạt và câu ranh giới Đạt. `result` ghi cả số "một phần".

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Nhận task brief cho TK7, muốn chạy trong chỗ làm việc tách biệt để hỏng thì vứt đi mà không ảnh hưởng checkout đang mở. Tạo bằng cách nào, đặt tên nhánh ra sao, làm gì ngay sau khi tạo trước khi code? | `SKILL.md` › 2. Bước 1 (1a công cụ harness / 1b `git worktree add .worktrees/<nhánh> -b <nhánh>`), › 4. Bước 3 baseline sạch (+ › 3); quy ước đặt tên nhánh không có | `SKILL.md` › 1. Bước 0, › 2 (1a, 1b), › 3, › 4 | Đạt (cách tạo và việc ngay sau khi tạo đủ: dựng, baseline, ghi PROGRESS; không có quy ước đặt tên nhánh, chủ thể ghi rõ) |
| 2 | Repo Node, worktree mới trống trơn: không `node_modules`, không `.env.local`, build báo thiếu dependency. Dựng môi trường theo thứ tự nào để agent làm việc được ngay? | `SKILL.md` › 3. Bước 2 dựng dự án (`npm ci`/`npm install`), › 4; file `.env.local` không có | `SKILL.md` › 3, › 4 | Đạt (`npm ci`/`npm install` rồi baseline; không có cách xử lý file không được theo dõi như `.env.local`, chủ thể ghi rõ) |
| 3 | Hai agent cùng repo, một sửa module auth, một sửa module báo cáo, cả hai định `git checkout -b` ngay trong thư mục hiện tại. Chia chỗ làm việc để không dẫm lên index và working tree của nhau thế nào, mỗi agent cấp đường dẫn nào? | `SKILL.md` › 1 (nhiều Implementer song song thì tạo worktree), › 2 (đường dẫn tuyệt đối, không `cd` sang worktree khác); "mỗi agent một worktree riêng" và cơ chế index không tường minh | `SKILL.md` › 1, › 2 (1b), › 5 | Một phần (có điều kiện "nhiều Implementer song song" và đường dẫn tuyệt đối; "mỗi agent một worktree và một nhánh riêng", `.worktrees/<nhánh-của-agent>` là suy luận của chủ thể, skill không nói tường minh; không chia phạm vi file) |
| 4 | Đã gộp nhánh vào main, test xanh, muốn xoá worktree cùng nhánh. Trước khi xoá cần xác nhận gì để không mất công việc chưa lưu, thứ tự lệnh dọn đúng là gì? | `SKILL.md` › 6. Dọn khi xong (`git worktree remove` rồi `prune`, sau khi nhánh đã gộp), › 5, › 7; danh sách kiểm "mất việc chưa lưu" và xoá nhánh sau gộp không tường minh | `SKILL.md` › 6, › 7, › 5 | Một phần (có thứ tự `remove` rồi `prune` và điều kiện "nhánh đã gộp"; không có danh sách kiểm trước khi xoá, không có lệnh xoá nhánh) |
| 5 | Worktree cho task dài, hôm sau không nhớ nhánh nào gắn thư mục nào, còn thư mục mồ côi từ task cũ. Liệt kê, kiểm tra, dọn worktree còn sót (kể cả entry trỏ thư mục đã bị xoá tay) thế nào? | `SKILL.md` › 7 (`git worktree list`), › 6 (`prune`); quy trình liệt kê và dọn entry xoá tay không có | `SKILL.md` › 7, › 6 | Một phần (có `git worktree list` và `prune`; không có quy trình liệt kê, kiểm tra, xử lý thư mục mồ côi; skill không nói `prune` dọn entry trỏ thư mục đã xoá tay) |
| 6 | Vừa mở PR từ nhánh sprint, cần xem trạng thái check CI đang đỏ, đọc log run Actions bị fail và gắn label cho PR. Dùng gì? | mục khác: skill `github-ops` | mục khác: `github-ops` (từ danh mục skill; chủ thể ghi chưa mở skill đó) | Đạt (ranh giới) |

## Thiếu nội dung / mâu thuẫn

- **Thiếu nội dung (câu 1).** Quy ước đặt tên nhánh (có hay không mã `TK`).
- **Thiếu nội dung (câu 2).** Xử lý file ignore cần cho build (`.env.local`) khi tạo worktree mới.
- **Thiếu nội dung (câu 3).** Không nói tường minh "mỗi Implementer một worktree riêng" và cách chia phạm vi file giữa hai agent (đã nêu ở lượt trước, vẫn còn).
- **Thiếu nội dung (câu 4).** Danh sách kiểm trước khi xoá (`git status` sạch, commit chưa gộp/chưa đẩy) và lệnh xoá nhánh sau gộp (đã nêu ở lượt trước, vẫn còn).
- **Thiếu nội dung (câu 5).** Liệt kê worktree còn sót và dọn entry trỏ thư mục đã xoá tay (`git worktree prune` chỉ được nhắc sau `remove`).
- Theo brief `X4` không sửa tiếp: mở rộng nội dung các mục trên thuộc sprint nội dung mới, điều phối ghi `CO`.
- Không có mâu thuẫn trong `SKILL.md`.
