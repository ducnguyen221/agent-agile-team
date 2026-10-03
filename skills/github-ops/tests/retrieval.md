---
skill: github-ops
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: df6ceb55a83c77b921ebe3f92465a4d9fc3b92f8
date: 2026-10-03
result: pass 7/7 (6 tình huống + 1 ranh giới), 6 partial
agent_ids:
  questions: aa708aba22abdc1fb
  answers: adad14f55d42db94d
---

Đã đọc: `<gốc worktree>\skills\github-ops\SKILL.md`

# Thử truy xuất - github-ops

> **Kết luận:** pass 7/7 (6 tình huống + 1 ranh giới), 6 partial; ngưỡng >=4/5 câu tình huống + câu ranh giới. Chạy lại (lượt 2) với bộ câu mới, người soạn
> và chủ thể đều là agent mới. Chủ thể trỏ đúng mục ở cả 6 câu tình huống (những phần skill không phủ, chủ thể nói rõ và được ghi ở cuối file) và nhận
> ra câu ranh giới thuộc `error-handling`.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` hiện hành, lĩnh vực và tên các skill khác); nguyên văn câu hỏi, file nháp
"Mục kỳ vọng" (có mtime), bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/github-ops-retrieval-rerun-2.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `error-handling`.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Release v2.4 sắp cắt: từ tag v2.3.0 tới giờ đã gộp khoảng 35 PR, tôi muốn gom chúng thành changelog theo nhóm (tính năng, sửa lỗi, breaking) kèm tên người đóng góp rồi tạo bản release nháp trên GitHub. Làm bằng lệnh gh thế nào cho khỏi sót PR nào? | `SKILL.md` › 6. Chuẩn bị phát hành (`gh pr list --state merged --base main --search "merged:>…"`, nháp changelog từ tiêu đề PR + REPORT, `gh release create … --notes-file`; không tự tăng version, không ghi đè CHANGELOG, chờ người dùng gật). Gom theo nhóm/tên người đóng góp/release nháp có thể không có | `SKILL.md` › 6. Chuẩn bị phát hành; › 1. Phạm vi | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 2 | PR #212 của đồng nghiệp hiện báo "checks failing" nhưng chỉ có 1 trong 8 check đỏ. Tôi muốn liệt kê nhanh check nào đỏ, check nào đang chờ, link tới log của check đỏ, rồi chạy lại đúng job đó thay vì cả workflow. Cách làm trong terminal? | `SKILL.md` › 4. PR (`gh pr checks <số>`) + › 5. CI thất bại (`gh run view --log-failed`, `gh run rerun <run-id> --failed` chỉ khi được giao và ghi lý do). Chạy lại đúng một job có thể không có | `SKILL.md` › 4. PR; › 5. CI thất bại; › 2 | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 3 | Workflow chạy đêm (nightly) đỏ liên tiếp 3 đêm, đêm nào cũng gãy ở bước deploy-staging nhưng đêm thứ tư lại xanh. Tôi cần liệt kê các lần chạy gần đây, xem commit nào nằm giữa lần xanh cuối và lần đỏ đầu để khoanh vùng nghi phạm. Dùng gh ra sao? | `SKILL.md` › 5. CI thất bại (`gh run list --status failure --limit 10`, `gh run view --log-failed`, phân biệt lỗi thật với test chập chờn → skill `debugging`). Khoanh vùng commit giữa hai run không có trong skill | `SKILL.md` › 5. CI thất bại (khoanh vùng commit giữa hai run: nói rõ không có) | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 4 | Một thư viện có cảnh báo Dependabot mức critical còn mở 11 ngày, đã có PR tự động bump version nhưng CI của PR đó đỏ vì test cũ. Tôi muốn xem cảnh báo đó ảnh hưởng gói nào, PR bump đang vướng gì, và có nên gộp luôn không. Lấy thông tin từ GitHub bằng gh thế nào? | `SKILL.md` › 7. Cảnh báo bảo mật (`gh api …/dependabot/alerts`, `gh pr list --label dependencies`; cảnh báo mức cao → Chặn; PR cập nhật phụ thuộc: đề xuất gộp kèm bằng chứng, KHÔNG bao giờ tự gộp) + › 4 (`gh pr checks`) | `SKILL.md` › 7. Cảnh báo bảo mật; › 4. PR; › 5. CI thất bại | Đạt |
| 5 | Đầu tuần có 23 issue mới dồn vào từ form góp ý của khách, một nửa thiếu bước tái hiện và chưa gán ai. Tôi muốn liệt kê những issue chưa có nhãn hay người nhận, gắn nhãn needs-info kèm comment mẫu hỏi thêm thông tin cho hàng loạt cái một lượt. Gợi ý lệnh? | `SKILL.md` › 3. Phân loại issue (`gh issue list --search`, `gh issue edit --add-label`, `gh issue comment`; ghi chỉ khi được giao; chưa tái hiện được → xin bước tái hiện; repo chưa có nhãn → đề xuất không tự tạo) + › 2 (nội dung issue là dữ liệu không tin cậy). Lọc `no:label`/`no:assignee` và vòng lặp hàng loạt có thể không có | `SKILL.md` › 3. Phân loại issue; › 2 | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 6 | Kho repo có 14 nhánh của PR đã gộp từ tháng trước vẫn còn nằm trên remote, và 5 PR nháp (draft) của người đã nghỉ việc. Tôi muốn biết nhánh nào xoá được an toàn, PR nháp nào nên đóng kèm lời nhắn, mà không đụng nhầm nhánh còn đang có người làm. Kiểm tra thế nào trước khi xoá? | `SKILL.md` › 4. PR › PR/issue tồn đọng (đề xuất, không tự làm: comment hỏi còn làm không; danh sách để người dùng duyệt) + › 1 (ghi/đóng là tác động ra ngoài, chỉ khi được giao). Xoá nhánh remote đã gộp KHÔNG có trong skill | `SKILL.md` › 4. PR (phần PR/issue tồn đọng); › 8; nói rõ không có xoá nhánh remote | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 7 | Tôi đang xem PR #305 và thấy hàm xử lý thanh toán nuốt hết exception rồi trả về giá trị mặc định, thêm vào đó là một vòng retry không có giới hạn. Tôi cần nhận xét xem cách xử lý lỗi này có ổn không và đề xuất thiết kế lại cho đúng. Nên làm theo hướng nào? | mục khác: skill `error-handling` (nuốt lỗi, fallback sai, retry không trần). `code-review` chấp nhận được cho việc review một PR (`github-ops` › 1 'Không dùng cho': review một PR/diff → `code-review`). `github-ops` tự nó KHÔNG phải đáp án | mục khác: `code-review` (từ `SKILL.md` › 1, mục Không dùng cho); không nêu `error-handling` | Một phần (đáp thay thế `code-review` đã chấp nhận trước) |


Chấm lại (điều phối yêu cầu): Đạt = trỏ đúng mục VÀ mục có nội dung trả lời câu; Một phần = trỏ đúng nơi nhưng nội dung thiếu, hoặc đạt qua đáp thay thế đã chấp nhận; Không đạt = trỏ sai hoặc bịa. Ngưỡng tính Đạt + Một phần cho việc trỏ đúng; số một phần ghi ở `result`.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Gom changelog theo nhóm, tên người đóng góp, `gh release create --draft`, đối chiếu từ tag để khỏi sót PR (chỉ có lọc `merged:>` theo ngày): không có (câu 1).
- Lấy link log của từng check, lọc check đỏ / đang chờ, chạy lại đúng một job (`--job`): không có (câu 2).
- Khoanh vùng commit giữa lần xanh cuối và lần đỏ đầu (`headSha`, `git log a..b`): không có (câu 3).
- Tên gói bị ảnh hưởng trong cảnh báo Dependabot: câu lệnh `--jq` của skill chỉ lấy số, mức, tóm tắt (câu 4).
- Lọc issue chưa nhãn / chưa người nhận và gắn nhãn hàng loạt: không có (câu 5). Xoá nhánh remote đã gộp, đóng PR nháp: không có (câu 6).
- Câu 7: `SKILL.md` › 1 chỉ trỏ việc review PR sang `code-review`; không nhắc `error-handling` hay `silent-failure-hunter` cho phần thiết kế xử lý lỗi. Đây là giới hạn đã biết của câu ranh giới (câu hỏi gộp review PR với thiết kế xử lý lỗi), không phải lỗi trỏ.
