---
skill: worktrees
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: a7d8807c40b16c2d83af5b34151fb7188c3b9926
date: 2026-10-03
result: pass 5/6, 3 partial, 1 fail
agent_ids:
  questions: aaa480af25c9fbdd6
  answers: aa30d8d2d0e51b138
---

Đã đọc: `<gốc worktree>\skills\worktrees\SKILL.md` (và các file trong `references/` mà `SKILL.md` trỏ tới, nếu có)

# Thử truy xuất — worktrees

> **Kết luận:** 5/6 câu Đạt (ngưỡng ≥4/5 câu tình huống và câu ranh giới): câu 1, 3, 5 chỉ Đạt một phần, câu 2 Đạt, **câu 4 Không đạt vì thiếu nội dung** ("already checked out").
> Câu ranh giới (câu 6) trỏ đúng `closing-sprint`. Skill chỉ có `SKILL.md` (không `references/`); chủ thể đọc một lần, không bịa, và đánh dấu rõ chỗ nào là suy luận
> (câu 3: không dùng `--force` là suy từ luật commit tạm, không phải câu chữ của skill). Chủ thể ghi sai số mục baseline là "mục 3" (đúng là mục 4, tiêu đề đúng); chấm theo tiêu đề.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực, kèm danh sách chủ đề của bộ cũ để không lặp); lượt này là **bộ câu mới** chạy lại sau khi `X2` đổi nội dung skill
(chạy lại theo giao thức rerun-2). Cột "Mục kỳ vọng" do người chấm ghi vào file nháp **trước khi** giao chủ thể (mtime file nháp 2026-10-03 21:40:39 +0700 (21:40:39,62), sớm hơn lệnh giao chủ thể đầu tiên); mục kỳ vọng ghi theo cây MỚI.
Câu 6 là câu ranh giới, đáp án do người soạn nêu và người chấm đối chiếu với `description` của skill đáp.
Nguyên văn câu hỏi của người soạn, file nháp kỳ vọng, output TRỌN của chủ thể (đường dẫn thư mục người dùng giữ nguyên ở đó, còn ở đây lược thành `<gốc worktree>` vì repo chặn tên người dùng)
và số lượt công cụ: hồ sơ sprint của lớp riêng, `evidence/TK12-green/worktrees-retrieval-rerun-2.md`.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần chi tiết phụ còn thiếu ghi trong ngoặc và ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được.
Ngưỡng: ≥4/5 câu tình huống Đạt và câu ranh giới Đạt. `result` ghi cả số "một phần".

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Vừa tạo worktree cho TK5 để chạy brief, chạy bộ test trước khi sửa thì đã đỏ 3 test; không biết có sẵn từ nhánh gốc hay do worktree tạo sai. Xử lý thế nào trước khi giao implementer? | `SKILL.md` › 4. Bước 3 — baseline sạch (hỏng → ghi tên test vào PROGRESS; có sẵn không chặn TK thì làm tiếp, chặn thì `BR`); cách phân biệt nguồn lỗi không có | `SKILL.md` › "3. Bước 3 — baseline sạch" (số mục ghi nhầm, tiêu đề đúng = mục 4); › 1. Bước 0 | Đạt (một phần: có luật ghi PROGRESS và phân nhánh chặn/không chặn; chủ thể nói thẳng skill không có cách so với nhánh gốc để biết lỗi có sẵn hay do tạo sai) |
| 2 | Định đặt worktree ở `.worktrees/` trong repo. Git có coi thư mục này là chưa theo dõi và `git add .` có kéo vào commit không? Cần ignore gì trước? | `SKILL.md` › 2. Bước 1, mục 1b (`git check-ignore -q`, chưa bỏ qua thì thêm `.gitignore` + commit trước) + › 7. Tra nhanh | `SKILL.md` › 2. Bước 1 (1b); › 7. Tra nhanh + bảng bào chữa | Đạt (chủ thể ghi skill không giải thích cơ chế untracked / `git add .`) |
| 3 | `git worktree remove ../repo-wt-tk7` báo "contains modified or untracked files, use --force"; có vài file implementer chưa commit. Có nên thêm `--force` cho nhanh? | `SKILL.md` › 6. Dọn khi xong (+ › 5: cất việc dở bằng commit tạm, không `reset --hard`); skill không nhắc `--force` | `SKILL.md` › 6. Dọn khi xong; › 5. Luật git trong worktree | Đạt (một phần: kết luận "đừng `--force`, commit tạm trước" là suy luận của chủ thể từ mục 5 và 6, chủ thể ghi rõ không phải câu chữ của skill) |
| 4 | `git worktree add ../repo-wt-tk9 sprint/spr-03` báo nhánh "is already checked out at" đường dẫn khác, hình như phiên agent cũ còn giữ. Nên làm gì? | `SKILL.md` › 5 và › 6 (chỉ nguyên tắc: không xoá worktree không phải của mình, không xoá nhánh chưa gộp); lỗi "already checked out" không có tên trong skill | `SKILL.md` › 1. Bước 0; › 6. Dọn khi xong; › 5. Luật git trong worktree (chủ thể: "skill không có đáp án") | **Không đạt (thiếu nội dung)**: chỉ rút được "đừng xoá worktree/nhánh không phải của mình"; cách xác định ai giữ, nối lại hay dọn không có |
| 5 | Đã tạo worktree nhưng agent con vẫn thấy ở thư mục chính và sửa nhầm file ở đó. Kiểm tra isolation đúng chưa, và brief cho agent cần ghi gì để không lạc ra ngoài? | `SKILL.md` › 1. Bước 0 (lệnh dò `--git-dir` so `--git-common-dir`) + › 2 (đường dẫn tuyệt đối, không `cd` sang worktree khác); nội dung brief không có | `SKILL.md` › 1. Bước 0; › 2. Bước 1 | Đạt (một phần: có lệnh dò và "làm việc trong worktree bằng đường dẫn tuyệt đối"; không có mẫu brief cho agent con, chủ thể trỏ `running-sprint` mà không khẳng định nội dung) |
| 6 | Sprint đã qua Cổng 2, nói "Đạt"; muốn chọn gộp main cục bộ / PR / giữ nhánh, rồi cập nhật spec sống, release notes và đóng sprint. Bước nào của quy trình làm tiếp? | mục khác: skill `closing-sprint` (`SKILL.md` › 5 chỉ tới nó) | mục khác: `closing-sprint` (từ `SKILL.md` › 5. Luật git trong worktree) | Đạt (ranh giới) |

## Thiếu nội dung / mâu thuẫn

- **Thiếu nội dung (câu 4).** `skills/worktrees/SKILL.md` không có đường xử lý khi `git worktree add` báo nhánh "is already checked out at …": không nhắc `git worktree list` để tìm
  ai giữ nhánh, không nói khi nào dùng lại worktree đó, khi nào dọn, khi nào tạo nhánh mới. Đề xuất (điều phối quyết, đổi `skill_sha`): thêm một dòng ở mục 7 (Tra nhanh): "nhánh đã checkout ở nơi khác →
  `git worktree list` để tìm chủ; của mình thì dùng lại hoặc dọn theo mục 6; không phải của mình thì không xoá, tạo nhánh mới từ nó".
- **Thiếu nội dung, nhẹ.** Mục 6 có `git worktree remove` nhưng không nói gì khi git từ chối vì còn file chưa commit (câu 3; chủ thể phải suy "đừng `--force`"); mục 4 không có cách phân biệt baseline đỏ có sẵn
  hay do dựng sai (câu 1); không có mẫu brief cho agent con (câu 5). Các điểm từ lượt trước còn nguyên: không có lệnh xoá nhánh tạm sau gộp (`git branch -d`), không có dòng "mỗi Implementer một worktree và nhánh theo `TK`".
- Không có mâu thuẫn trong tệp.
