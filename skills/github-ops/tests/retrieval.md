---
skill: github-ops
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: e7a76210e2fd399c5d0c637864bac169b0117ec4
date: 2026-10-04
result: "strict 1/7 (+6 partial, 0 fail) — below threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: "a97b91121edf9bad2 (câu ranh giới soạn lại: a68a3f6478d90e2ff, vì bản đầu trùng câu cũ)"
  answers: abbe8fff11c6a2c9d
---

Đã đọc: `<gốc worktree>/skills/github-ops/SKILL.md` (không có `references/`)

# Thử truy xuất - github-ops

> **Kết luận:** strict 1/7 (+6 partial, 0 fail), dưới ngưỡng. Bộ câu MỚI (lượt độc lập `TK13`, người soạn không đọc skill) phủ các góc khác của `description`; 0 trong 6 câu tình huống Đạt hẳn, các câu còn lại trỏ đúng nơi nhưng thiếu nội dung (mục "Thiếu nội dung" bên dưới). Câu ranh giới Đạt. Bộ câu cũ giữ ở mục lịch sử.

Câu hỏi do người soạn mới (id ở `agent_ids`) viết từ `description` và danh sách câu cũ, không đọc skill. Cột "Mục kỳ vọng" và điều kiện Đạt ghi vào file nháp
`.tmp/github-ops-expected.md` lúc 2026-10-04 10:45:54 +07:00, **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm); file nháp chép giữ mtime vào
`expected/github-ops-expected.md`. Bài trả lời trọn của chủ thể (id ở `agent_ids`, 4 lượt công cụ) và bảng chấm ở `evidence/TK13/github-ops-retrieval.md`
trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>`
vì repo chặn tên người dùng. Chủ thể được dặn nói thẳng khi skill không có phần câu hỏi cần, không dùng kiến thức ngoài.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Tôi đang xem các alert bảo mật của repo: có 6 cảnh báo secret-scanning còn mở, trong đó một cái là AWS access key bị commit vào file cấu hình từ 3 tuần trước, và một cái là token test bị đánh dấu nhầm. Tôi muốn liệt kê các alert đang mở qua gh, xem alert nào là false positive để đóng lại với lý do, còn cái key thật thì ghi nhận gì trước khi xoay khóa? Dùng lệnh gh nào để làm việc này? | `SKILL.md` › 7. Cảnh báo bảo mật (lệnh `gh api … secret-scanning/alerts`, secret lộ → báo để xoay vòng khoá, không in lại giá trị, ghi số ngày mở) | `SKILL.md` › 7. Cảnh báo bảo mật (+ › 1, › 3, › 8) | Một phần (có lệnh liệt kê alert và luật xoay khoá; thiếu lệnh đóng alert false positive kèm lý do) |
| 2 | Một PR của tôi (#418) cứ báo "merge conflict" với main dù tôi vừa rebase hôm qua, và tôi cũng không chắc nó đang chờ review của ai: có 2 reviewer được yêu cầu nhưng chưa ai phản hồi, và có 1 comment chưa resolve. Tôi muốn xem một lượt trạng thái mergeable, người đang bị chờ review, các thread chưa giải quyết và trạng thái auto-merge. Có cách nào lấy gọn từ terminal bằng gh không? | `SKILL.md` › 4. PR (`gh pr view <số> --json mergeable,reviewDecision,updatedAt`, tuổi và lần hoạt động cuối, PR >5 ngày chưa ai review) | `SKILL.md` › 4. PR | Một phần (chỉ ba trường `mergeable,reviewDecision,updatedAt`) |
| 3 | Sếp vừa nhờ tôi đếm xem trong quý này team đóng được bao nhiêu issue, trung bình mất bao lâu từ lúc mở tới lúc đóng, và những issue nào đang nằm im hơn 90 ngày không có hoạt động. Repo có khoảng 600 issue cả mở lẫn đóng. Tôi nên truy vấn thế nào bằng gh để lấy số liệu dạng JSON rồi lọc ra, thay vì ngồi đếm tay trên giao diện web? | `SKILL.md` › 3. Phân loại issue (đoạn Nhiều issue một lượt: `--limit`, `--json`) và › 4. PR (đoạn PR/issue tồn đọng: `gh issue list --json … --jq` theo `updatedAt`) | `SKILL.md` › 3 (Nhiều issue một lượt) và › 4 (PR/issue tồn đọng) | Một phần (có `--limit`, `--json`, `--jq` theo `updatedAt`; thiếu đếm issue đã đóng và thời gian đóng trung bình) |
| 4 | Tôi cần sửa lại một release đã publish hôm qua: tên tag bị gõ sai thành v3.1.0-rc1 thay vì v3.1.0, phần mô tả còn dính ghi chú nội bộ, và thiếu 2 file đính kèm (một file .zip và một file checksum .sha256). Tôi muốn chỉnh release hiện có thay vì xoá làm lại, và đính kèm thêm file. Lệnh gh nào xử lý được từng phần, và phần nào sửa không được? | `SKILL.md` › 6. Chuẩn bị phát hành (chỉ có `gh release create`; chỉnh release đã publish nằm ngoài nội dung hiện có) | `SKILL.md` › 6. Chuẩn bị phát hành (+ › 1) | Một phần (đúng mục phát hành; chỉ có `gh release create`) |
| 5 | Trong org có 9 repo cùng dùng một workflow build, hôm nay cả 9 cùng đỏ ở bước cache restore sau khi GitHub đổi runner image. Tôi muốn quét qua tất cả các repo trong org, lấy lần chạy thất bại mới nhất của workflow đó ở mỗi repo, rồi in ra dòng log lỗi liên quan để xác nhận chung một nguyên nhân. Làm hàng loạt bằng gh thế nào mà không phải mở từng repo? | `SKILL.md` › 5. CI thất bại (`gh run list --workflow … --json`, `gh run view <run-id> --log-failed`); phần quét nhiều repo trong org không có | `SKILL.md` › 5. CI thất bại (+ › 2) | Một phần (đúng mục CI; chỉ cho một repo) |
| 6 | Mình làm việc trên fork của một dự án mã nguồn mở, upstream đã có 52 commit mới còn nhánh feature của mình đang mở một PR lên upstream. Mình muốn đồng bộ fork với upstream, kiểm tra PR của mình còn trỏ đúng nhánh đích không, rồi đổi base branch của PR sang nhánh release/2.x vì maintainer vừa yêu cầu. Cách làm bằng gh là gì? | `SKILL.md` › 4. PR (gần nhất: `gh pr view`); lệnh đồng bộ fork và đổi base của PR không có trong skill | `SKILL.md` › 1. Phạm vi và › 4. PR (nói thẳng không có nội dung) | Một phần (trỏ mục gần nhất và nói thẳng skill thiếu) |
| 7 | Đồng nghiệp vừa mở một pull request trên GitHub, gồm 27 file đổi và khoảng 1.400 dòng thêm vào, đang chờ mình duyệt trước khi gộp vào nhánh chính. Mình cần đọc từng đoạn diff xem logic có đúng không, test đã đủ chưa, và quyết định có nên bắt tác giả sửa lại hay cho qua. Nên dùng quy trình nào để review PR này một cách bài bản? | mục khác: skill `code-review` (từ `SKILL.md` › 1. Phạm vi, "Không dùng cho": review một PR hay diff) | mục khác: `code-review` (từ `SKILL.md` › 1. Phạm vi) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Câu 1: Đóng alert secret-scanning là false positive kèm lý do (không có lệnh hay trường `resolution`); danh sách thông tin cần ghi trước khi xoay khoá ngoài "báo, số ngày mở, không in lại giá trị".
- Câu 2: Người được yêu cầu review, thread chưa giải quyết, trạng thái auto-merge, chẩn đoán conflict sau khi rebase.
- Câu 3: Đếm issue đóng trong quý, tính trung bình từ mở tới đóng (`closedAt`), lọc im lặng quá 90 ngày (skill chỉ có ngưỡng 14 và 30 ngày).
- Câu 4: Sửa release đã publish: đổi ghi chú, đổi tag, đính kèm thêm file; phần nào sửa không được.
- Câu 5: Quét nhiều repo trong org (liệt kê repo, chọn repo bằng cờ, vòng lặp), trích dòng log lỗi hàng loạt.
- Câu 6: Đồng bộ fork với upstream, kiểm nhánh đích (base) của PR, đổi base sang nhánh khác (`gh pr view --json` của skill không có trường nhánh đích).
- Điều kiện Đạt ghi trước ở file nháp có vài chỗ đánh dấu "phần phụ"; lượt này **không** nương theo dấu đó: việc câu hỏi nêu đích danh mà skill không có thì câu tính Một phần. Các phần phụ thiếu ở câu Đạt ghi ngay trong cột "Kết quả".
- Skill chưa sửa ở lượt này (việc của điều phối); `skill_sha` là băm cây skill hiện tại.

## Lịch sử

Lượt trước (`TK11`/`TK12`, bộ câu cũ, ngày 2026-10-04, `skill_sha` e7a76210e2fd399c5d0c637864bac169b0117ec4, id chủ thể aedf633815b3a90ed): `result` là `strict 7/7 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7`. Bảng cũ giữ nguyên chữ, nhãn `Cũ-n`:

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| Cũ-1 | Release v2.4 sắp cắt: từ tag v2.3.0 tới giờ đã gộp khoảng 35 PR, tôi muốn gom chúng thành changelog theo nhóm (tính năng, sửa lỗi, breaking) kèm tên người đóng góp rồi tạo bản release nháp trên GitHub. Làm bằng lệnh gh thế nào cho khỏi sót PR nào? | `SKILL.md` › 6. Chuẩn bị phát hành: mốc theo tag, `--limit` (mặc định 30), `--json … author,labels`, đối chiếu `compare … total_commits`, gom theo nhãn/tiền tố, `--draft`, `--generate-notes --notes-start-tag`, chờ người dùng gật | `SKILL.md` › 6. Chuẩn bị phát hành | Đạt |
| Cũ-2 | PR #212 của đồng nghiệp hiện báo "checks failing" nhưng chỉ có 1 trong 8 check đỏ. Tôi muốn liệt kê nhanh check nào đỏ, check nào đang chờ, link tới log của check đỏ, rồi chạy lại đúng job đó thay vì cả workflow. Cách làm trong terminal? | `SKILL.md` › 4. PR (`gh pr checks --json name,bucket,link`, lọc fail/pending) + › 5 (`gh run view --json jobs` lấy `databaseId`, `gh run rerun --job`, chỉ khi được giao) | `SKILL.md` › 4. PR; › 5. CI thất bại (chạy lại một job) | Đạt |
| Cũ-3 | Workflow chạy đêm (nightly) đỏ liên tiếp 3 đêm, đêm nào cũng gãy ở bước deploy-staging nhưng đêm thứ tư lại xanh. Tôi cần liệt kê các lần chạy gần đây, xem commit nào nằm giữa lần xanh cuối và lần đỏ đầu để khoanh vùng nghi phạm. Dùng gh ra sao? | `SKILL.md` › 5. CI thất bại, đoạn "Khoanh vùng commit" (`gh run list --workflow --json headSha,conclusion`, `git log a..b`, `compare`); chập chờn → `debugging` | `SKILL.md` › 5. CI thất bại (đoạn Khoanh vùng commit) | Đạt |
| Cũ-4 | Một thư viện có cảnh báo Dependabot mức `critical` còn mở 11 ngày, đã có PR tự động bump version nhưng CI của PR đó đỏ vì test cũ. Tôi muốn xem cảnh báo đó ảnh hưởng gói nào, PR bump đang vướng gì, và có nên gộp luôn không. Lấy thông tin từ GitHub bằng gh thế nào? | `SKILL.md` › 7. Cảnh báo bảo mật (jq có tên gói / manifest / bản vá, không gộp khi CI đỏ, không bao giờ tự gộp) + › 4, › 5 (xem check của PR, `--log-failed`) | `SKILL.md` › 7. Cảnh báo bảo mật; › 4. PR; › 5. CI thất bại | Đạt |
| Cũ-5 | Đầu tuần có 23 issue mới dồn vào từ form góp ý của khách, một nửa thiếu bước tái hiện và chưa gán ai. Tôi muốn liệt kê những issue chưa có nhãn hay người nhận, gắn nhãn needs-info kèm comment mẫu hỏi thêm thông tin cho hàng loạt cái một lượt. Gợi ý lệnh? | `SKILL.md` › 3. Phân loại issue, đoạn "Nhiều issue một lượt" (`no:label no:assignee`, `--limit`, `gh issue edit` nhiều số, vòng lặp comment, duyệt trước, nhãn có sẵn) + › 2 (nội dung là dữ liệu không tin cậy) | `SKILL.md` › 3. Phân loại issue (đoạn Nhiều issue một lượt); › 2 | Đạt |
| Cũ-6 | Kho repo có 14 nhánh của PR đã gộp từ tháng trước vẫn còn nằm trên remote, và 5 PR nháp (draft) của người đã nghỉ việc. Tôi muốn biết nhánh nào xoá được an toàn, PR nháp nào nên đóng kèm lời nhắn, mà không đụng nhầm nhánh còn đang có người làm. Kiểm tra thế nào trước khi xoá? | `SKILL.md` › 4. PR, đoạn "Dọn nhánh remote và PR nháp" (4 điều kiện, squash, `--draft`, `gh pr close --comment`, `git push origin --delete` sau khi duyệt) | `SKILL.md` › 4. PR (đoạn Dọn nhánh remote và PR nháp) | Đạt |
| Cũ-7 | Tôi đang xem PR #305 và thấy hàm xử lý thanh toán nuốt hết exception rồi trả về giá trị mặc định, thêm vào đó là một vòng retry không có giới hạn. Tôi cần nhận xét xem cách xử lý lỗi này có ổn không và đề xuất thiết kế lại cho đúng. Nên làm theo hướng nào? | mục khác: skill `error-handling` (từ `SKILL.md` › 1 "Không dùng cho"); `code-review` chấp nhận được cho việc review PR, đáp án chính là `error-handling` | mục khác: `error-handling` (thiết kế lại xử lý lỗi) và `code-review` (review PR), từ `SKILL.md` › 1. Phạm vi | Đạt |
