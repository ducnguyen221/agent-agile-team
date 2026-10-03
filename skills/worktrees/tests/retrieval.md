---
skill: worktrees
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: a7d8807c40b16c2d83af5b34151fb7188c3b9926
date: 2026-10-03
result: pass 6/6
---

Đã đọc: `<gốc worktree>\skills\worktrees\SKILL.md`

# Thử truy xuất — worktrees

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥5/6). Skill ngắn, chỉ có `SKILL.md`; chủ thể trỏ đúng ở cả năm câu tình huống
> và nhận ra câu ranh giới thuộc `running-sprint`. Chỗ thiếu: không có dòng nói thẳng "mỗi Implementer một worktree và nhánh
> riêng" cho trường hợp làm song song, chủ thể phải suy.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Câu 6 là câu ranh giới: đáp án của
người soạn (`running-sprint`) đã được người chấm đối chiếu với `description` và mục 2 của `running-sprint` (giao việc
theo `TK`, ghi vai · tier · model vào PROGRESS) và nhận là đúng. Câu 5 người chấm chấp nhận hai đường: mục 5 và 6 của
skill này (chỉ tới menu kết thúc), hoặc `closing-sprint` là nơi có menu merge, PR, giữ.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần
chi tiết phụ còn thiếu ghi ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được cho quyết định đó.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Đang code dở nhánh `feature/billing` trên checkout chính thì có việc sửa gấp phải làm riêng. Tách một chỗ làm việc cô lập bằng lệnh nào? | `SKILL.md` › 2. Bước 1 — tạo không gian tách biệt (1b; + 1. Bước 0) | `SKILL.md` › 2. Bước 1 (1a rồi 1b) | Đạt |
| 2 | Sắp thực thi một brief TK có nhiều file, muốn chắc chắn không đụng vào thay đổi chưa commit của checkout hiện tại. Cần chuẩn bị gì trước? | `SKILL.md` › 1. Bước 0 + 2. Bước 1 + 4. Bước 3 — baseline sạch | `SKILL.md` › 1. Bước 0, 2. Bước 1, 4. Bước 3 | Đạt |
| 3 | Ba implementer cùng làm trên một repo song song, thường ghi đè lên nhau. Nên cấp mỗi người chỗ làm việc ra sao? | `SKILL.md` › 1 (tạo khi nhiều Implementer song song) + 2 (1b) | `SKILL.md` › 1. Bước 0, 2. Bước 1 | Đạt (một phần: skill chỉ nêu điều kiện kích hoạt, "mỗi người một worktree" là suy ra) |
| 4 | Việc xong và đã gộp, còn thư mục worktree `../repo-wt-fix12` cùng nhánh tạm. Dọn thế nào mà không mất công việc chưa gộp? | `SKILL.md` › 6. Dọn khi xong | `SKILL.md` › 6. Dọn khi xong (+ 5) | Đạt (một phần: không có lệnh xoá nhánh tạm) |
| 5 | Worktree xong nhưng nhánh còn chưa gộp, chưa chắc nên giữ, gộp hay mở PR. Lựa chọn nào an toàn và khi nào chọn? | `SKILL.md` › 5 và 6 (chỉ tới `closing-sprint`); chấp nhận mục khác: skill `closing-sprint` | mục khác: `closing-sprint` (từ `SKILL.md` › 5) | Đạt |
| 6 | PLAN đã qua Cổng 1, điều phối cần chia TK cho các agent, ghi vai và tier, theo dõi PROGRESS. Quy trình điều phối đó là gì? | mục khác: skill `running-sprint` | mục khác: `running-sprint` | Đạt |

## Thiếu nội dung / mâu thuẫn

- `skills/worktrees/SKILL.md:35-38` (mục 1): chỉ nói "tạo worktree … khi nhiều Implementer làm song song". Không có quy tắc "mỗi Implementer một worktree và một nhánh
  riêng, đặt tên theo `TK`" hay cách chia để các nhánh không chạm cùng tệp (câu 3). Đề xuất: một dòng ở mục 2 hoặc mục 7 (tra nhanh): song song thì mỗi Implementer một worktree
  riêng, nhánh theo `TK`; việc chung tệp thì xếp tuần tự.
- `skills/worktrees/SKILL.md:102-104` (mục 6): có `git worktree remove` và `prune`, không có lệnh xoá nhánh tạm đã gộp (câu 4). Đề xuất: thêm `git branch -d <nhánh>` (từ chối khi chưa
  gộp, nên an toàn), nhắc không dùng `-D`.
- Không có mâu thuẫn trong tệp.
