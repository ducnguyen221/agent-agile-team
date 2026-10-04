---
skill: github-ops
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: e7a76210e2fd399c5d0c637864bac169b0117ec4
date: 2026-10-04
result: "strict 7/7 (+0 partial, 0 fail) — at threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 7/7"
agent_ids:
  questions: "bộ câu cũ giữ nguyên, không soạn mới"
  answers: aedf633815b3a90ed
---

Đã đọc: `<gốc worktree>/skills/github-ops/SKILL.md` (không có `references/`)

# Thử truy xuất - github-ops

> **Kết luận:** strict 7/7: đạt ngưỡng. Sau `TK11.1` cả sáu câu tình huống trỏ đúng mục và mục có nội dung (lượt trước 1/7 Đạt hẳn, 6 Một phần); câu ranh giới trả `error-handling` (đáp án chính) kèm `code-review`.

Bộ câu hỏi giữ nguyên chữ của lượt trước (bộ câu cũ giữ nguyên, không soạn mới); bộ câu mới là việc của `TK13`. Cột "Mục kỳ vọng" ghi vào file nháp
`.tmp/github-ops-expected.md` **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm). Bài trả lời của chủ thể (id ở
`agent_ids`) và bảng chấm ở `evidence/TK11/github-ops-retrieval.md` trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời,
đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Release v2.4 sắp cắt: từ tag v2.3.0 tới giờ đã gộp khoảng 35 PR, tôi muốn gom chúng thành changelog theo nhóm (tính năng, sửa lỗi, breaking) kèm tên người đóng góp rồi tạo bản release nháp trên GitHub. Làm bằng lệnh gh thế nào cho khỏi sót PR nào? | `SKILL.md` › 6. Chuẩn bị phát hành: mốc theo tag, `--limit` (mặc định 30), `--json … author,labels`, đối chiếu `compare … total_commits`, gom theo nhãn/tiền tố, `--draft`, `--generate-notes --notes-start-tag`, chờ người dùng gật | `SKILL.md` › 6. Chuẩn bị phát hành | Đạt |
| 2 | PR #212 của đồng nghiệp hiện báo "checks failing" nhưng chỉ có 1 trong 8 check đỏ. Tôi muốn liệt kê nhanh check nào đỏ, check nào đang chờ, link tới log của check đỏ, rồi chạy lại đúng job đó thay vì cả workflow. Cách làm trong terminal? | `SKILL.md` › 4. PR (`gh pr checks --json name,bucket,link`, lọc fail/pending) + › 5 (`gh run view --json jobs` lấy `databaseId`, `gh run rerun --job`, chỉ khi được giao) | `SKILL.md` › 4. PR; › 5. CI thất bại (chạy lại một job) | Đạt |
| 3 | Workflow chạy đêm (nightly) đỏ liên tiếp 3 đêm, đêm nào cũng gãy ở bước deploy-staging nhưng đêm thứ tư lại xanh. Tôi cần liệt kê các lần chạy gần đây, xem commit nào nằm giữa lần xanh cuối và lần đỏ đầu để khoanh vùng nghi phạm. Dùng gh ra sao? | `SKILL.md` › 5. CI thất bại, đoạn "Khoanh vùng commit" (`gh run list --workflow --json headSha,conclusion`, `git log a..b`, `compare`); chập chờn → `debugging` | `SKILL.md` › 5. CI thất bại (đoạn Khoanh vùng commit) | Đạt |
| 4 | Một thư viện có cảnh báo Dependabot mức critical còn mở 11 ngày, đã có PR tự động bump version nhưng CI của PR đó đỏ vì test cũ. Tôi muốn xem cảnh báo đó ảnh hưởng gói nào, PR bump đang vướng gì, và có nên gộp luôn không. Lấy thông tin từ GitHub bằng gh thế nào? | `SKILL.md` › 7. Cảnh báo bảo mật (jq có tên gói / manifest / bản vá, không gộp khi CI đỏ, không bao giờ tự gộp) + › 4, › 5 (xem check của PR, `--log-failed`) | `SKILL.md` › 7. Cảnh báo bảo mật; › 4. PR; › 5. CI thất bại | Đạt |
| 5 | Đầu tuần có 23 issue mới dồn vào từ form góp ý của khách, một nửa thiếu bước tái hiện và chưa gán ai. Tôi muốn liệt kê những issue chưa có nhãn hay người nhận, gắn nhãn needs-info kèm comment mẫu hỏi thêm thông tin cho hàng loạt cái một lượt. Gợi ý lệnh? | `SKILL.md` › 3. Phân loại issue, đoạn "Nhiều issue một lượt" (`no:label no:assignee`, `--limit`, `gh issue edit` nhiều số, vòng lặp comment, duyệt trước, nhãn có sẵn) + › 2 (nội dung là dữ liệu không tin cậy) | `SKILL.md` › 3. Phân loại issue (đoạn Nhiều issue một lượt); › 2 | Đạt |
| 6 | Kho repo có 14 nhánh của PR đã gộp từ tháng trước vẫn còn nằm trên remote, và 5 PR nháp (draft) của người đã nghỉ việc. Tôi muốn biết nhánh nào xoá được an toàn, PR nháp nào nên đóng kèm lời nhắn, mà không đụng nhầm nhánh còn đang có người làm. Kiểm tra thế nào trước khi xoá? | `SKILL.md` › 4. PR, đoạn "Dọn nhánh remote và PR nháp" (4 điều kiện, squash, `--draft`, `gh pr close --comment`, `git push origin --delete` sau khi duyệt) | `SKILL.md` › 4. PR (đoạn Dọn nhánh remote và PR nháp) | Đạt |
| 7 | Tôi đang xem PR #305 và thấy hàm xử lý thanh toán nuốt hết exception rồi trả về giá trị mặc định, thêm vào đó là một vòng retry không có giới hạn. Tôi cần nhận xét xem cách xử lý lỗi này có ổn không và đề xuất thiết kế lại cho đúng. Nên làm theo hướng nào? | mục khác: skill `error-handling` (từ `SKILL.md` › 1 "Không dùng cho"); `code-review` chấp nhận được cho việc review PR, đáp án chính là `error-handling` | mục khác: `error-handling` (thiết kế lại xử lý lỗi) và `code-review` (review PR), từ `SKILL.md` › 1. Phạm vi | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Lượt này chủ thể không nêu khoảng trống nào trong sáu câu tình huống; phần phụ chưa có: vòng lặp comment hàng loạt chỉ là mẫu `for`, không có tạo nhãn `needs-info` (skill chủ ý chỉ đề xuất, không tự tạo nhãn).
- Nguồn của phần thêm ở `TK11.1`: `gh <lệnh> --help` của gh 2.97.0 (cli.github.com/manual) và REST API Dependabot alerts (docs.github.com).
