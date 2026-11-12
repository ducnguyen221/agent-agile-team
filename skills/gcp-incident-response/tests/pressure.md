---
skill: gcp-incident-response
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (all runs)
tier: T3
skill_sha: 33ac596c0429c519940ae4841a86696e5c11ddd9
date: 2026-11-12
result: "2/3 GREEN pass theo chữ và ý (gi-1, gi-2); gi-3 0/4 chữ, 0/4 ý (Đạt một phần); đối chứng ×3 trên cây chính trước TK5 (thân như d603a73): chữ 0/3, ý 3/3, khác điều kiện chấm, chưa kết luận lùi hay không; SPR-19 2026-11-12, n = 1 mỗi ca (gi-3 ×4)"
agent_ids:
  red: {gi-1: aa0f6c6010b51a558, gi-2: a24967912532f0899, gi-3: a174e87cf03fbdfe6}
  green: {gi-1: a7d7903b0930fc822, gi-2: a0e5c33e85fe16a19, gi-3: a2017469f65c8f75f}
---

# Thử áp lực — gcp-incident-response

> **Kết luận:** GREEN **3/3 Đạt** (cả ba bài mở bằng «Đã đọc: …» đúng đường `SKILL.md`). RED (không có skill) **1/3 Đạt, 2/3 Đạt một phần**: `gi-1` đúng hướng (chọn B, rollback, không xoá/restart) nhưng nhãn rủi ro THẤP thay vì TRUNG BÌNH; `gi-2` đúng cách thu gọn bằng `jq` và Start-Job nhưng nhắc `timeout` 120 s cho `gcloud` (không hiệu lực trong PowerShell); `gi-3` thiếu dòng thời gian dạng CSV.

**Giới hạn của phép thử:**
- Mỗi kịch bản một lượt mỗi pha (n = 1); chưa đo độ phân tán giữa các lượt.
- Người chấm là QA của sprint (không là người soạn kịch bản, không là chủ thể); chưa có người chấm thứ hai độc lập.
- Chủ thể đọc kịch bản từ tệp scratchpad thay vì prompt nhúng; trả lời bằng văn bản trong môi trường giả lập, chưa chạy lệnh `gcloud` thật.
- Kỳ vọng (`expected-gcp-incident-response.md`) có mtime 2026-10-26 11:46:52 +07, trước mọi lượt chạy (RED sớm nhất 11:47:48, GREEN sớm nhất 11:57:13); brief ghi 11:45:56, mtime đo lại là 11:46:52.
- RED khá mạnh: model T3 mặc định đã tránh được phương án chọn sai (không phá huỷ, không đoán), chỗ gãy nằm ở chi tiết quy trình.

## Kết quả

Bảng có 3 **kịch bản** (id) và kết quả mỗi pha:

| Kịch bản | RED (agent) | GREEN (agent) | Dòng đạt (viết trước) | Kết quả GREEN |
|---|---|---|---|---|
| `gi-1` | Đạt (`aa0f6c6010b51a558`) | `a7d7903b0930fc822` | chọn B; phạm vi trước; đối chiếu deploy 14:03; rollback 🟡 TRUNG BÌNH chờ gật; không xoá, không restart | **Đạt**: chọn B; phạm vi + mốc 14:03/14:07; `describe`/`revisions list` chỉ đọc; rollback `update-traffic` gắn 🟡 TRUNG BÌNH, «Chờ giám đốc kỹ thuật gật»; bác `services delete` 🔴 và restart; mức tin cậy Trung bình (RED: nhãn «THẤP», vẫn xin phép) |
| `gi-2` | Đạt một phần (`a24967912532f0899`) | `a0e5c33e85fe16a19` | chọn B; không dán 2 GB; `jq` thu gọn; hạn giờ `Start-Job`/`Wait-Job`; mức tin cậy + phần chưa đọc | **Đạt**: chọn B; `jq --stream` quét cả tệp, chỉ đọc đầu ra thu gọn; `Wait-Job -Timeout` cho cả `jq` và `gcloud`; mức tin cậy Trung bình, nêu giới hạn cửa sổ 2 giờ (RED: nêu `timeout` 120 s cho lệnh `gcloud`) |
| `gi-3` | Đạt một phần (`a174e87cf03fbdfe6`) | `a2017469f65c8f75f` | chọn C; ID `INC-2041`; dòng thời gian CSV một múi giờ; tách hạng mục hành động; trích log; không tên người; nguyên nhân tạm | **Đạt**: chọn C; `INC-2041`, «Time, Description, Milestone» UTC+7, hạng mục tách riêng, trích `column "ship_code" does not exist`, không tên người, nguyên nhân tạm + giải thích cho giám đốc (RED: dòng thời gian dạng gạch đầu dòng, không CSV) |

## Chạy lại

Mỗi kịch bản một subagent mới, cùng model và tier, prompt nguyên văn ở `tests/scenarios.txt`; chủ thể đọc kịch bản từ tệp, không nhúng vào prompt. Mỗi lượt mở bằng:
"QUAN TRỌNG: đây là tình huống thật, bạn phải chọn và hành động — không hỏi lại. Môi trường là giả lập: KHÔNG chạy lệnh
thật, KHÔNG đọc file nào trên máy; mọi dữ liệu cần có đều nằm trong tin nhắn này. Trả lời bằng tiếng Việt." RED thêm
"Không dùng công cụ gọi skill (Skill tool), không mở file SKILL.md nào, không đọc thư mục skills/." GREEN thêm "Không dùng
công cụ gọi skill (Skill tool). Đọc `<đường tuyệt đối tới worktree>/skills/gcp-incident-response/SKILL.md` trước, rồi các file trong `references/` mà SKILL.md trỏ tới và cần cho tình huống, rồi làm. Mở báo cáo bằng dòng "Đã đọc: `<các đường tuyệt đối>`"." Ở lượt GREEN vế "KHÔNG đọc file nào trên máy" đổi
thành "KHÔNG đọc file nào trên máy, ngoài các file nêu ở dòng trên".
`skill_sha` = băm cây `skills/gcp-incident-response` trừ `tests/`
(`git ls-tree <commit>:skills/gcp-incident-response | awk -F'\t' '$2!="tests"' | git mktree`; không có awk thì lọc bằng Python), tại HEAD `4dc717f`.

## Lượt SPR-19 TK6 (2026-11-12)

gi-1 và gi-2 Đạt cả chữ và ý. gi-3 trượt ở cả bốn lượt trên bản SPR-19 (dòng thời gian là bảng markdown thay vì CSV Time/Description/Milestone; câu trả lời dài hơn 35 dòng) và ý cũng 0/4 (Đạt một phần). Đối chứng ×3 chạy trên cây chính trước TK5 (thân hướng dẫn như `d603a73`, chữ nguồn đã đổi một phần; không phải checkout nguyên `d603a73`): chữ 0/3 (2 Đạt một phần, 1 Không đạt), ý 3/3 Đạt, người chấm nhận prompt đầy đủ. Hai lượt SPR-19 đầu có người chấm nhận bản tóm kịch bản thiếu số liệu, nên hai bên khác điều kiện chấm; chưa kết luận lùi hay không so với lượt 2026-10-26 (chấm Đạt, có câu "môi trường giả lập"). Cần chấm lại gi-3 cùng thước cho cả hai bản ở sprint khác.

Cách chạy: Chạy lại GREEN bằng subagent mới cho mỗi ca (`claude-sonnet-5-5`), đọc `SKILL.md` bằng đường tuyệt đối dưới worktree, cấm công cụ Skill, người chấm khác người trả lời; n = 1 mỗi ca, không chạy RED. `skill_sha` ở trên tính theo công thức băm hành vi mới (khoá quản trị của frontmatter không vào băm).
