---
skill: github-ops
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: df6ceb55a83c77b921ebe3f92465a4d9fc3b92f8
date: 2026-10-03
result: pass 6/6
---

Đã đọc: `<gốc worktree>\skills\github-ops\SKILL.md`

# Thử truy xuất — github-ops

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥5/6). Skill chỉ có `SKILL.md`, mỗi mục khớp một việc trong `description`, nên chủ thể
> trỏ đúng ở cả năm câu tình huống và nhận ra câu ranh giới thuộc `closing-sprint`. Chỗ còn thiếu là lệnh phụ: so với lần
> chạy xanh gần nhất, liệt kê người review còn thiếu.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Câu 6 là câu ranh giới: đáp án của
người soạn (`closing-sprint`) đã được người chấm đối chiếu với mục 1 của chính skill ("Không dùng cho: quyết định
gộp/phát hành → `closing-sprint`") và `description` của `closing-sprint`, và nhận là đúng.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần
chi tiết phụ còn thiếu ghi ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được cho quyết định đó.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Có 60 issue mở, nhiều cái trùng, cần phân loại và gắn nhãn nhanh bằng `gh`. Dùng lệnh nào và lọc theo tiêu chí gì? | `SKILL.md` › 3. Phân loại issue | `SKILL.md` › 3. Phân loại issue | Đạt (một phần: không có vòng gắn nhãn hàng loạt) |
| 2 | Run Actions #4821 của workflow `ci.yml` đỏ ở bước test. Làm sao lấy log của job lỗi và so với lần xanh gần nhất? | `SKILL.md` › 5. CI thất bại | `SKILL.md` › 5. CI thất bại | Đạt (một phần: không có lệnh so với lần xanh) |
| 3 | Cần xem PR #137 đã đủ điều kiện gộp chưa: check nào xong, review nào còn thiếu. Lệnh `gh` nào cho thấy trạng thái đó? | `SKILL.md` › 4. PR | `SKILL.md` › 4. PR | Đạt |
| 4 | Dependabot báo 9 cảnh báo và secret scanning báo một token lộ trong commit cũ. Xem và xử lý theo thứ tự nào bằng `gh`? | `SKILL.md` › 7. Cảnh báo bảo mật | `SKILL.md` › 7. Cảnh báo bảo mật | Đạt |
| 5 | Có hơn 40 issue và 12 PR không hoạt động từ nửa năm, muốn dọn mà không làm mất việc cần giữ. Cách lọc và đóng an toàn là gì? | `SKILL.md` › 4. PR (đoạn PR/issue tồn đọng) | `SKILL.md` › 4. PR (đoạn PR/issue tồn đọng) | Đạt |
| 6 | Sprint đã xong, cần soạn release notes từ các hạng mục đã làm, cập nhật spec sống rồi chọn merge hay mở PR. Dùng quy trình nào? | mục khác: skill `closing-sprint` | mục khác: `closing-sprint` (từ `SKILL.md` › 1. Phạm vi) | Đạt |

## Thiếu nội dung / mâu thuẫn

- `skills/github-ops/SKILL.md:87-93` (mục 5): có lệnh lấy log job lỗi nhưng không có cách so với lần chạy xanh gần nhất cùng workflow (câu 2). Đề xuất: thêm một
  dòng `gh run list --workflow <tên> --status success --limit 1` rồi so bước hoặc commit giữa hai lần chạy.
- `skills/github-ops/SKILL.md:72-76` (mục 4) và `:66-70` (mục 3): không có lệnh xem người review còn thiếu (`reviewRequests` trong `--json`) (câu 3) và không có
  mẫu lọc hàng loạt trước khi gắn nhãn (câu 1). Đề xuất: thêm `reviewRequests` vào dòng `gh pr view --json`, và một dòng `gh issue list --json … --jq`
  làm mẫu lọc.
- `skills/github-ops/SKILL.md:106-118` (mục 7): mức độ và hành động có đủ nhưng không nêu thứ tự xử lý khi cả hai loại cảnh báo cùng có (câu 4). Đề xuất: một câu
  "secret lộ trước, rồi Dependabot mức cao, rồi phần còn lại".
- Chủ đề `description` đều có mục trả lời; không có mâu thuẫn trong tệp.
