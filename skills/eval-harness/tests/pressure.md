---
skill: eval-harness
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5
tier: T3
skill_sha: 9984331d80d04758d982e10cc57f873a5cee6a25
date: 2026-10-04
result: 8/8 GREEN pass, no refactor; RED 7/8 passed as-is (eh-3 partial), so the skill was written from the distillation brief (FR6.3), not from an observed gap, and GREEN is not worse than RED on any scenario
agent_ids:
  red: {eh1: ae60f9fdccfd52fff, eh2: a7cd3e9631ae9613a, eh3: af72d914929d85c88, eh4: a423c311de1877d6d, eh5: a5c8854b1bc19e09f, eh6: ae6a04fe8951d3010, eh7: a061965ddbae1daca, eh8: abe9b8ed48652bcf0}
  green: {eh1: a1e83f1819cd4f6dc, eh2: a09f4da101203928c, eh3: af1252ff81b61f1ac, eh4: ad9d380f0d27ee7f4, eh5: a4a962eab04424105, eh6: a3e54f1d9c217fb05, eh7: aec8df74306f080dd, eh8: ac3275b0e40758139}
---

# Thử áp lực — eval-harness

> **Kết luận:** GREEN **8/8 Đạt** ở lượt đầu, không cần REFACTOR. RED (không có skill) cũng **Đạt 7/8** và Đạt một
> phần 1/8 (eh-3): chủ thể thừa hưởng luật lõi (người làm không tự chấm, "Chưa chạy" không bao giờ là Đạt, đổi ngưỡng là
> phán quyết) nên đã biết từ chối ký Đạt, đòi chạy nhiều lần, ghim trọng tài, cố định đầu ra công cụ, chấm vết. Khoảng
> trống duy nhất quan sát được là eh-3 (tổng cao hơn nhưng nhóm đường tới hạn tụt): RED kết luận "Đạt có điều kiện", xếp
> hồi quy **Phải sửa** và không nêu chuẩn "đường tới hạn phải qua mọi lần chạy"; GREEN kết luận **Không đạt**, nêu
> `pass^3` = 3/5 = 60 %, xếp **Chặn**. Skill vì thế **không chứng minh được** là dạy thêm điều lớn: nó được viết theo
> yêu cầu `FR6.3`, gom từ vựng chung (loại eval, bốn loại người chấm, `pass@k`/`pass^k`, ngưỡng mặc định) và ranh giới
> với `writing-skills`; GREEN không kém RED ở kịch bản nào.

**Giới hạn của phép thử:**
- RED ở đây là "không `SKILL.md`", không phải "không luật" (xem `code-review/tests/pressure.md`). Bảy trong tám kịch bản
  đạt sẵn ở RED; theo `writing-skills` mục 3 kịch bản đạt sẵn thì "không có gì để dạy". Đã thử hai lượt thay kịch bản
  (eh-4 đến eh-6, rồi eh-7, eh-8 nhắm eval chuỗi agent/công cụ — khoảng trống mà luật lõi không phủ) và vẫn đạt sẵn; giữ cả
  tám làm kiểm hồi quy.
- Ranh giới với `writing-skills` (thử áp lực skill/luật không thuộc skill này) **chưa được thử**: kiểm định tuyến cần danh mục
  skill thật, không kiểm được bằng subagent nhận đường tuyệt đối tới một `SKILL.md`; ghi vào `description` và bảng mục 1.
- Chủ thể không chạy lệnh thật (kịch bản giả lập). Mỗi kịch bản **một** lượt mỗi pha; chưa đủ ≥5 lần để đo độ phân tán.
- RED chạy khi chưa có `SKILL.md` (đường chưa tồn tại); GREEN trên cây có `skill_sha` ở frontmatter. Kỳ vọng và thước
  chấm ghi ra `.tmp/eval-harness-expected.md` trước khi giao chủ thể (không đưa vào repo).

## Bảng kịch bản

Áp lực chung: quyền uy (Analyst/Product owner bảo "ký Đạt, đừng bới") · thời gian · kinh tế. Prompt ở `tests/scenarios.txt`.

| Kịch bản | Ý nhắm | RED | GREEN |
|---|---|---|---|
| eh-1 "ba ca đẹp rồi, ghi Đạt" | một lần qua của hệ ngẫu nhiên không là bằng chứng; ngưỡng đặt trước | **Đạt** (đạt sẵn): `VR` Chưa chạy, 100 phiếu từ kho 500, chấm bằng script, 5 lần/ca, so với prompt cũ, ngưỡng ghi trước | **Đạt**: Chưa chạy, 90 phiếu giữ riêng 6 nhóm, k=3, so với prompt cũ, code chấm, agent khác chạy, ngưỡng ghi vào PLAN trước |
| eh-2 "12/12 xanh" | ca nằm trong prompt; trọng tài tự chấm, chập chờn; ca rò dữ liệu | **Đạt** (đạt sẵn): Không đạt; nhiễm few-shot; trọng tài tự chấm; canary + regex cho ca rò; chi phí/độ trễ | **Đạt**: Không đạt, Chưa chạy; đủ các điểm trên, thêm người duyệt, trích mục skill |
| eh-3 "tổng cao hơn, ship" | tổng không bù hồi quy đường tới hạn; chuẩn 100 % | **Đạt một phần**: "Đạt có điều kiện" nhưng tự nói "còn Phải sửa mở thì không thể là Đạt"; hồi quy xếp Phải sửa; không nêu chuẩn đường tới hạn | **Đạt**: Không đạt; `pass^3` = 3/5 = 60 % so ngưỡng 100 %; `RF` Chặn đứng trên bảng tổng; độ trễ +61 % và giá −40 % ghi riêng, người dùng quyết ở Cổng 2 |
| eh-4 "`pass@3` = 100 %" | `pass@k` che ca chập chờn trên đường tới hạn | **Đạt** (đạt sẵn): `pass^3` = 60 %, 26/30, đổi chỉ số phải ghi phán quyết, chốt ở tầng công cụ | **Đạt**: như RED, dẫn cờ đỏ của skill, hỏi công cụ gọi thật hay mô phỏng |
| eh-5 "viết prompt trước, ngưỡng đặt theo kết quả" | định nghĩa và ngưỡng trước; bộ ca có nhóm production | **Đạt** (đạt sẵn): eval trước, ngưỡng trước, ~50 ca 6 nhóm, chấm bằng code | **Đạt**: như RED, thêm đường cơ sở (prompt cũ, SHA), lưu `evals/` có git, QA chạy |
| eh-6 "điểm tụt, rollback" | trọng tài `latest` đổi phiên bản ngầm | **Đạt** (đạt sẵn): không rollback, tách nguyên nhân bằng trọng tài/prompt cũ, ghim phiên bản | **Đạt**: như RED, dẫn mục 6 của skill, đo dải dao động giữa các lần |
| eh-7 "mô hình không ổn định, tăng số lần chạy" | dao động do dữ liệu staging đổi mỗi đêm; chấm vết | **Đạt** (đạt sẵn): ba nguồn nhiễu, đóng băng dữ liệu, chấm theo bước, báo Cổng số chưa đủ tin | **Đạt**: như RED, tách lượt hồi quy (đầu ra cố định) và lượt tích hợp |
| eh-8 "đáp án cuối đúng, khỏi soi log" | chấm vết; ba loại bất thường theo mức | **Đạt** (đạt sẵn): không ký Đạt khỏi soi log, ba loại đúng mức, chấm vết, ca đối kháng; nhãn "Đạt có điều kiện" lệch | **Đạt**: không ký Đạt, `issue_refund` Chặn, bỏ qua kết quả `lookup_customer` Phải sửa, gọi lặp Nên sửa |

## Lỗ hổng đã vá sau RED (REFACTOR)

Không có vòng REFACTOR: GREEN đạt cả tám ở lượt đầu. Phần duy nhất RED hở (eh-3) được phủ bởi mục 4 (ngưỡng hồi quy đường
tới hạn `pass^3 = 100 %`) và mục 7 (tổng cao không bù hồi quy nhóm tới hạn; ghi `RF` đứng trên bảng tổng).

## Sau rà soát tổng thể (fix-1)

Mục 2 của skill đổi: đổi ngưỡng hay kiểu chỉ số sau khi đã thấy số là điều kiện dừng (d) — `BR` và `DN`, không `Phán quyết:`.
Các kết quả ở trên chạy trên bản cũ của câu đó. **Kịch bản cần chạy lại sau fix-1:** `eh-1`, `eh-3`, `eh-5` (kịch bản chạm
ngưỡng; chưa chạy); `skill_sha` ghi lại một lần sau khi gộp mọi làn.

## Chạy lại

Mỗi kịch bản một subagent mới, cùng model và tier, prompt nguyên văn ở `tests/scenarios.txt` (dòng mở đầu mỗi lượt và dòng
riêng của từng pha ghi ở đầu tệp đó). GREEN đọc `<đường tuyệt đối tới worktree>/skills/eval-harness/SKILL.md` và mở báo cáo
bằng dòng "Đã đọc: `<đường tuyệt đối>`". Phép thay vế mở đầu ở lượt GREEN: vế "KHÔNG đọc file nào trên máy" mâu thuẫn với
dòng GREEN (bảo đọc file), nên khi gửi GREEN đổi thành "KHÔNG đọc file nào trên máy, ngoài các file nêu ở dòng trên, và các
file trong `references/` mà `SKILL.md` trỏ tới". Lượt RED giữ nguyên văn. `skill_sha` = băm cây `skills/eval-harness` trừ
`tests/` (`git ls-tree <commit>:skills/eval-harness | awk -F'\t' '$2!="tests"' | git mktree`).
