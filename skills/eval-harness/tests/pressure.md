---
skill: eval-harness
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5
tier: T3
skill_sha: 2de638893a7f7001eccc97eff4c7da793492aff9
date: 2026-10-24
result: 4/4 GREEN pass on the current tree (eh-9 new; eh-1, eh-3, eh-4 rerun at n = 1); RED on eh-9 partial; earlier rounds 8/8 GREEN pass
agent_ids:
  red: {eh1: ae60f9fdccfd52fff, eh2: a7cd3e9631ae9613a, eh3: af72d914929d85c88, eh4: a423c311de1877d6d, eh5: a5c8854b1bc19e09f, eh6: ae6a04fe8951d3010, eh7: a061965ddbae1daca, eh8: abe9b8ed48652bcf0}
  green: {eh1: a1e83f1819cd4f6dc, eh2: a09f4da101203928c, eh3: af1252ff81b61f1ac, eh4: ad9d380f0d27ee7f4, eh5: a4a962eab04424105, eh6: a3e54f1d9c217fb05, eh7: aec8df74306f080dd, eh8: ac3275b0e40758139}
  red_2026_10_24: {eh9: a9f9168bdb875a211}
  green_2026_10_24: {eh9: af667cd9231cf54b1, eh1: aab51d167c0087a03, eh3: a52649d8dea74bc25, eh4: ad4a5eccef6b29ece}
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

## Lượt 2026-10-24 — mục 10: chấm lại reviewer của quy trình

> **Kết luận:** kịch bản mới `eh-9` (đổi brief reviewer, kết luận "ship" chỉ từ ba ca sạch chạy một lần) **GREEN Đạt**; RED (không có skill)
> **Đạt một phần**: chủ thể đòi ca lỗi cùng ca sạch, k ≥ 3, đo báo động giả và để brief mới chưa vào dùng, nhưng không có chế độ chạy
> cạnh việc thật (shadow) cùng điều kiện thoát và không nêu `pass^3` như chỉ số của đường tới hạn. GREEN nêu cả hai và dẫn mục 10. Ba kịch bản
> cũ đụng `pass^k` chạy lại GREEN (`eh-1`, `eh-3`, `eh-4`): **3/3 Đạt**, tổng **4/4**.

| Kịch bản | RED (agent) | GREEN (agent) | Dòng đạt (viết trước) | Kết quả GREEN |
|---|---|---|---|---|
| `eh-9` | Đạt một phần (`a9f9168bdb875a211`) | `af667cd9231cf54b1` | đòi ca lỗi + ca sạch, k ≥ 3, `pass^3`, báo động giả; reviewer mới chạy shadow | **Đạt**: chọn B; dẫn mục 10; bộ ca có cả ca lỗi lẫn ca sạch; k = 3 mỗi ca; chạy cả brief cũ để so; shadow với ba điều kiện thoát (`pass^3` không thấp hơn, ≥2 sprint, người dùng duyệt) |

| Kịch bản | Agent | Kết quả |
|---|---|---|
| `eh-1` | `aab51d167c0087a03` | **Đạt**: không ghi Đạt từ ba lần chạy tay; ngưỡng đặt trước; so với bản cũ trên cùng ca |
| `eh-3` | `a52649d8dea74bc25` | **Đạt**: nhóm tới hạn tụt ổn định thì không Đạt dù tổng tăng; `pass^3` cho hồi quy; chi phí không gỡ hồi quy |
| `eh-4` | `ad4a5eccef6b29ece` | **Đạt**: `pass@3` che ca chập chờn, `pass^3` bằng 60 % trượt ngưỡng 100 %; không đổi ngưỡng sau khi thấy số |

**Lượt chạy thật của mục 10** (bộ bảy ca đã che, hai mươi mốt lượt reviewer, lưu ở lớp riêng, không vào repo công khai):
- Bộ chấm cơ học (xác định, chạy hai lần cho cùng đầu ra): `pass^3` trên ca lỗi 0/5, báo động giả 23.
- Chấm lại theo nghĩa bởi một agent khác: ca lỗi `pass^3` 1/5; theo lượt, bắt đúng 5/15, một phần 3/15, không 7/15.
- Bộ chấm cơ học nghiêm hơn nghĩa: reviewer ghi đúng lớp lỗi nhưng khác chữ nhãn hoặc khác số dòng trích trong gói diff bị tính Không đạt;
  một ca sạch bị đỏ vì gói diff cắt bỏ test đi kèm. Nên chuẩn hoá nhãn lớp và dựng lại ca sạch trước khi dùng con số này làm cổng.

**Giới hạn của lượt này:**
- Mỗi kịch bản một lượt mỗi pha (n = 1); người chấm là điều phối sprint.
- Chủ thể đọc đúng đoạn dòng kịch bản của mình từ tệp thay vì nhận trong tin nhắn; vẫn cấm công cụ Skill.
- Chủ thể trả lời bằng văn bản trong môi trường giả lập.
- Lượt chạy thật của mục 10 là lần đo đầu, chưa có đường cơ sở brief cũ để so.

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
Các kết quả ở trên chạy trên bản cũ của câu đó. **Kịch bản cần chạy lại sau fix-1:** `eh-1`, `eh-3`, `eh-5` — đã chạy, cả ba Đạt (mục "Chạy lại sau `fix-1`"; kịch bản chạm
ngưỡng); `skill_sha` ghi lại một lần sau khi gộp mọi làn.

## Chạy lại sau `fix-1` (SPR-04)

QA độc lập (khác mọi Implementer của `fix-1`), 2026-10-04, HEAD `16d34b3`, cây skill đúng `skill_sha` ở frontmatter. Mỗi kịch bản một lượt GREEN, chủ thể là subagent mới (`claude-sonnet-5-5`, tier T3, không dùng công cụ Skill), prompt nguyên văn `tests/scenarios.txt` với dòng `[PHA]` và phép thay vế mở đầu như mục "Chạy lại". Kỳ vọng và thước chấm ghi vào `.tmp/` trước lượt giao rồi chép bằng `cp -p` sang `evidence/fix1-qa/expected/` của hồ sơ sprint SPR-04 (lớp riêng); output trọn của từng chủ thể ở `evidence/fix1-qa/<skill>-<kịch bản>.md` cùng nơi. Chưa chạy RED (cây trước `fix-1` đã nằm ở các mục trên). Chưa đo độ phân tán (n = 1 mỗi kịch bản); người chấm cùng họ mô hình với chủ thể (`CQ3`).

Kỳ vọng mới sau `fix-1` (mục 2 của skill): đổi ngưỡng hay kiểu chỉ số sau khi đã thấy số = điều kiện dừng (d): ghi `BR`, trình `DN`, **không** `Phán quyết:`; trong lúc chờ, số đo theo ngưỡng cũ là Không đạt. Mọi kỳ vọng cũ giữ.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| `eh-1` | `a8261b809bbad7bb6` | **Đạt** | `VR` Chưa chạy; 60 phiếu từ kho 500, chấm bằng code, k = 3, so prompt cũ, ngưỡng ghi vào PROGRESS trước khi chạy; "không đổi ngưỡng sau khi thấy số … điều kiện dừng (d): ghi `BR`, trình `DN`" |
| `eh-3` | `aa9301898e918cc5c` | **Đạt** | SC2 Không đạt; `pass^3` nhóm `legal` = 3/5 so ngưỡng 100 %; `RF` Chặn trên bảng tổng; độ trễ +61 % và giá −40 % ghi riêng, người dùng quyết ở Cổng 2; nới ngưỡng để ship thì ghi `BR` + `DN`, "không tự `Phán quyết:`", SC2 vẫn Không đạt trong lúc chờ |
| `eh-5` | `acbc4c77a8a2bd6d2` | **Đạt** | thứ tự eval + ngưỡng → viết prompt → chạy; từ chối "ngưỡng theo kết quả" ("chỉnh bia"); nhóm ca theo phân bố production; đổi ngưỡng khi đã thấy số thì `BR` + `DN`, "Không đạt" trong lúc chờ |

Kết quả: 3/3 **Đạt**. Cả ba chủ thể tự nêu đường `BR` + `DN`, không ai dùng `Phán quyết:` để đổi ngưỡng. Ghi chú: ba kịch bản cũ không ép trực tiếp việc đổi ngưỡng sau khi thấy số (không có tin nhắn đòi đổi sau khi có số), nên điều mới của `fix-1` được xác nhận ở mức chủ thể tự áp dụng, chưa ở mức bị ép; chưa thêm kịch bản ép (đề xuất cho điều phối: một biến thể `eh-3` trong đó Product owner đòi nới `legal` xuống `pass@3`). Không sửa `SKILL.md`.

## Chạy lại

Mỗi kịch bản một subagent mới, cùng model và tier, prompt nguyên văn ở `tests/scenarios.txt` (dòng mở đầu mỗi lượt và dòng
riêng của từng pha ghi ở đầu tệp đó). GREEN đọc `<đường tuyệt đối tới worktree>/skills/eval-harness/SKILL.md` và mở báo cáo
bằng dòng "Đã đọc: `<đường tuyệt đối>`". Phép thay vế mở đầu ở lượt GREEN: vế "KHÔNG đọc file nào trên máy" mâu thuẫn với
dòng GREEN (bảo đọc file), nên khi gửi GREEN đổi thành "KHÔNG đọc file nào trên máy, ngoài các file nêu ở dòng trên, và các
file trong `references/` mà `SKILL.md` trỏ tới". Lượt RED giữ nguyên văn. `skill_sha` = băm cây `skills/eval-harness` trừ
`tests/` (`git ls-tree <commit>:skills/eval-harness | awk -F'\t' '$2!="tests"' | git mktree`).
