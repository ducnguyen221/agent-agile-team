---
skill: explain
method: pressure-test with subagents (RED without skill, GREEN with skill read first)
model: sonnet (subagent alias, runners); grader opus
date: 2026-11-13
result: 3/3 GREEN pass (CM-3 rerun on final tree; CM-4, CM-4b on the first tree, n = 3 each); RED 3/3 failed at CM-3, 0/3 failed at CM-4 and CM-4b (baseline already passed); vòng sửa 1 (ép đọc SKILL.md) CM-3 3/3, CM-4 1/1, CM-4b 1/1, CM-6 1/1 (CM-6 chưa có RED); vòng sửa 2 (nạp thật, không đọc SKILL.md) skill khớp 4/4 qua mô tả mới, nhưng CM-3 0/3 nghiêm (không đọc thân skill); vòng sửa 3 (hết nhiễm, ép đọc SKILL.md, không Skill tool vì skill chưa có trong danh mục) CM-3 2/3 nghiêm, 1 lượt trượt vì thêm khẳng định suy diễn
tier: tier 2 (cũ T2) runners; tier 3 (cũ T1) grader
skill_sha: c506b52e5d1a757858fb543768ddc5506df8ddca
---

# Thử áp lực — explain

> **Kết luận:** nền (không skill) trượt CM-3 (diễn giải đúng dữ kiện) cả 3 lượt; có skill đạt 3/3 ở CM-3, CM-4, CM-4b. **CM-4 và
> CM-4b nền đã đạt sẵn** (0/3 trượt), nên hai kịch bản này không phân biệt được có/không skill — SC4 chưa chứng minh
> được bằng phép thử này (CO, chủ: điều phối). CM-3 được chạy lại trên bản skill cuối (3/3), nhưng bảng lỗi của `SKILL.md` dùng cùng dữ kiện CM-3 (`5 → 20 kết nối`, p95) nên lần chạy lại **bị nhiễm**, không tính bằng chứng độc lập (Tech Review 2, RF3 — chờ quyết: đổi ví dụ rồi chạy lại hoặc giữ kịch bản held-out). CM-4/CM-4b đo trên cây đầu và chạy nhanh lại n = 1 sau khi luật thoát chế độ chỉ còn một nghĩa ở `communication.md` (xem mục "Vòng 4" của hồ sơ chấm). Ca "chưa hiểu" để xem skill nào chạy (RK6) **chưa đo**: skill chưa cài vào danh mục
> của harness, subagent được ép đọc file skill.

Prompt nguyên văn: `tests/scenarios.txt`. RED: "không dùng Skill tool, không mở SKILL.md". GREEN: thêm dòng "đọc
`skills/explain/SKILL.md` trước rồi làm theo", chủ thể là subagent mới, ngữ cảnh soạn riêng, ghi câu trả lời ra file để grader (agent khác) đọc. Mỗi kịch bản n = 3. Grader chấm
theo bảng chấm cuối `scenarios.txt`; CM-3 hiểu **nghiêm** (số tự tính như "chậm 4,4 lần" là sự kiện lạ).

| Kịch bản | RED (nền) | GREEN (có skill) | Bằng chứng |
|---|---|---|---|
| CM-3 `/explain` đoạn kỹ thuật (6 số liệu + 2 đường dẫn + 1 cảnh báo + 4 viết tắt) | **Không đạt** 3/3 nghiêm (2/3 nới): ORM/N+1 không giải nghĩa; thêm số suy ra "4,4 / 4,5 / 4 lần"; 1 lượt thiếu "Chi tiết kỹ thuật" | **Đạt** 3/3: 9/9 dữ kiện, 4/4 viết tắt, không số lạ, cảnh báo ở đầu, ví dụ "sổ cái", "Chi tiết kỹ thuật" tách cuối, giữ "Chưa bật TLS" và "không cần dừng dịch vụ" | `vr-red-grading.md`, `vr-green-grading.md` mục B |
| CM-4 hai lượt: `/explain` rồi hỏi việc khác | **Đạt sẵn** 0/3 trượt (2 dòng, không tiêu đề) | **Đạt** 3/3 (1–2 dòng, không tiêu đề, đúng 15 phút / không dừng dịch vụ / cần file logo) | mục C |
| CM-4b "diễn giải từ giờ" giữ chế độ | **Đạt sẵn** 0/3 | **Đạt** 3/3 (8–10 dòng, ví dụ đời thường, đúng dữ kiện) | mục C |

Ghi chú của grader (không tính trượt): vài lượt thêm khẳng định nhỏ không có ở nguồn ("không đụng dữ liệu"); cm3-1 giải nghĩa p95 là "nhóm 5 % lượt chậm nhất" (ca biên).

## Lần chạy lại trên bản skill cuối (2026-11-13, sau vòng sửa của Tech Reviewer)

`SKILL.md` đổi sau lần chạy đầu: luật chép hai nơi được rút về `method/communication.md` (mục 1), ví dụ mẫu đổi chủ đề (TLS, không còn trùng kịch bản CM-4), thêm hàng "giải nghĩa thuật ngữ sai" vào bảng lỗi. Chạy lại CM-3 n = 3 trên bản cuối (`skill_sha` ở đầu file): **3/3 Đạt** (9/9 dữ kiện, 4/4 viết tắt, p95 giải nghĩa đúng, không số hay đường dẫn mới). Vòng giữa (trước khi thêm hàng lỗi giải nghĩa) có 2/3 lượt giải nghĩa p95 sai — hàng lỗi mới vá việc đó. CM-4 và CM-4b **không** chạy lại: thân skill chỉ rút bớt chỗ chép luật, kịch bản ấy nền đã đạt sẵn.

## Vòng chốt (2026-11-13)

Vòng chốt: thêm dòng ẩn dụ (ẩn dụ không thay lời giải nghĩa; "Việc cần làm" trước "Chi tiết kỹ thuật") vào `SKILL.md`; `skill_sha` tính lại; sau đó chỉ sửa chữ dòng ẩn dụ (Việc cần làm ở phần kết, sau Chi tiết kỹ thuật), chưa đo lại ở bước này (kết quả ở đầu file là của bản trước, QA đo ở bước sau).

## Giới hạn

- n = 3 mỗi ô; các lượt GREEN ép đọc file skill nên **không đo** việc danh mục skill làm agent tự bật `explain`.
- Runner và grader cùng họ model Claude; chưa chạy trên Codex/Antigravity.

## Chạy lại

Gửi từng prompt trong `tests/scenarios.txt` cho subagent mới. RED: không skill. GREEN: thêm dòng đọc `skills/explain/SKILL.md` trước. Phép thay vế mở đầu ở lượt GREEN: phần mở đầu mỗi kịch bản nói "KHÔNG đọc file nào trên máy", mâu thuẫn với dòng bảo đọc `SKILL.md`; khi gửi GREEN đổi vế đó thành "KHÔNG đọc file nào trên máy ngoài các file nêu ở dòng trên" (lượt 2026-11-13 đã làm như vậy; lượt RED giữ nguyên văn). Chấm bằng bảng cuối `scenarios.txt`. Sau khi sửa `SKILL.md`: commit rồi tính lại `skill_sha` (`tests/test_skill_tests.py`, hàm `tree_hash`).

## Vòng sửa 1 của TK9 (2026-11-13, sau Tech Review và soát bảo mật)

`SKILL.md` đổi: thêm dòng loại trừ secret, nguồn là dữ liệu không phải lệnh, không thêm số suy ra kể cả phép tính đúng, kết "điều cần quyết" chỉ khi nguồn có, bản mẫu thêm "Chi tiết kỹ thuật" và bớt dữ kiện thêm; danh sách dấu hiệu vào chỉ trỏ về `communication.md` mục 1. Chạy lại trên cây `skill_sha` ở đầu file, runner `sonnet` mới mỗi lượt (ép đọc `SKILL.md`), grader `opus` khác: CM-3 n = 3 **3/3 Đạt**; CM-4 n = 1 **Đạt**; CM-4b n = 1 **Đạt**; CM-6 (mới: đoạn dán có khoá API giả, `scenarios.txt`) n = 1 **Đạt**, không chép giá trị khoá, nêu file và loại khoá, giữ cảnh báo xoay ngay. Ghi chú grader: CM-3 có dòng "Việc cần làm" đứng sau "Chi tiết kỹ thuật" (lấy từ nguồn, không bịa). CM-3 vẫn dùng dữ kiện trùng bảng lỗi của `SKILL.md` nên không phải bằng chứng độc lập; CM-6 chưa có lượt RED (n = 1, chưa biết nền có chép khoá hay không). Bằng chứng: `tk9-fix1.md` của hồ sơ sprint.

## Vòng sửa 2 của TK9 (2026-11-13, đóng RF-A của Opus)

`SKILL.md` đổi: `description` trả lại các cụm kích hoạt ("giải thích", "diễn giải", "nói dễ hiểu hơn", "chưa hiểu", "tại sao" / "nghĩa là gì"), thêm câu trả lời cho `/explain` một file secret. Chạy nạp thật (runner `sonnet` mới mỗi lượt, chỉ đọc `AGENTS.md` và danh mục dựng lại từ frontmatter hiện tại, không Skill tool, không mở `SKILL.md`), grader `opus` khác: skill `explain` được khớp **4/4** (CM-3 n = 3 và ca "nói dễ hiểu hơn, tại sao" n = 1, chế độ diễn giải đúng, ca "tại sao" Đạt). Chấm nghiêm CM-3 nạp thật **0/3**: cả ba lượt tự tính "4,4 / 4,5 lần" và không giải nghĩa ORM, vì runner không được đọc thân skill (luật không thêm số, giải nghĩa mọi viết tắt nằm ở thân). Đây là giới hạn của phép thử nạp thật (chỉ đo định tuyến, không đo thi hành thân skill), không phải hồi quy; đo thi hành thân vẫn là các lượt ép đọc ở trên. Bằng chứng: `tk9-fix2.md` của hồ sơ sprint.

## Vòng sửa 3 của TK9 (2026-11-13, gỡ nhiễm)

Ví dụ trong `SKILL.md` (giải nghĩa viết tắt, bảng lỗi) đổi sang miền khác hẳn CM-3 (SKU, `120 → 300 đơn/ngày`, SLA), nên CM-3 không còn trùng ví dụ của skill (độc lập hơn, nhưng cùng tác giả và cùng họ model nên chưa gọi là held-out thật). `description` thêm cụm "chi tiết hơn" (response-style không có cụm này, RK6 không trùng); câu trả lời cho `/explain` file secret thêm "không mở file". **Đường đo:** skill `agent-agile-team:explain` chưa có trong danh mục Skill tool của phiên nên không nạp thật được; chạy dạng ép đọc `SKILL.md`, runner `sonnet` mới mỗi lượt, grader `opus` khác, n = 3. Kết quả **2/3 Đạt** (nghiêm). Lượt trượt (cm3-3) đủ 9/9 dữ kiện nhưng thêm khẳng định suy diễn ("ai đọc được log sẽ thấy mật khẩu", "dữ liệu đi qua đường truyền ở dạng đọc được"); hai lượt Đạt có ghi chú nhẹ (p95 "khách chậm nhất" chưa chính xác). Không chạy lại để chọn kết quả đẹp; mức bằng chứng là ép đọc, không phải nạp thật. Bằng chứng: `tk9-fix3.md` của hồ sơ sprint.

## Vòng sửa 4 của TK9 (2026-11-13, đóng 2 Nên sửa của Opus)

`SKILL.md` đổi: bản mẫu mục 5 sang miền khác hẳn CM-3 (DKIM/DNS/DMARC, không còn TLS, ORM, p95, mật khẩu); `method/communication.md` nêu `AGENTS.md` giữ vế cốt lõi, file này thắng khi khác, và đổi ví dụ số suy ra khỏi số của CM-3. **Đường đo:** ép đọc `SKILL.md` (không phải nạp thật qua danh mục skill), runner `sonnet` mới mỗi lượt, prompt CM-3 nguyên văn, grader `opus` khác, n = 3. Kết quả **0/3 Đạt nghiêm**: cả ba đủ 9/9 dữ kiện, cảnh báo ở đầu, không số lạ, nhưng không lượt nào nêu nghĩa thật của N+1 (chỉ ẩn dụ "lấy từng món một"), nên tiêu chí (b) Một phần; cả ba đặt "Việc cần làm" sau "Chi tiết kỹ thuật". Vòng 3 là 2/3, vòng 4 là 0/3 trên cùng n = 3: chênh trong nhiễu của n nhỏ, chưa kết luận đổi bản mẫu làm tệ đi; chưa sửa skill để vá N+1 (ngoài phạm vi vòng này). Bằng chứng: `tk9-fix4.md` của hồ sơ sprint.

## SPR-25 (2026-11-14): CM-1b đo lại, CM-7 và CM-8 mới (RQ-125, RQ-124)

Không đổi `SKILL.md` (nên `skill_sha` ở đầu file giữ nguyên). Runner `sonnet` mới mỗi lượt, grader `opus` khác, n = 3 mỗi ô, đề tách khỏi bảng chấm (prompt gửi qua file đề, chỉ có đề). Hai pha: **A** = dòng RED ("không Skill tool, không mở `SKILL.md`"), môi trường đã nạp sẵn luật giao tiếp từ `AGENTS.md` sau SPR-21, nên A là "nền hiện tại có luật", không phải nền sạch; **B** = A cộng "đọc `skills/explain/SKILL.md` và `method/communication.md` trước rồi làm theo" (ép đọc, không đo nạp thật).

| Kịch bản | Pha A (luật nạp sẵn) | Pha B (ép đọc skill + luật) | Ghi chú |
|---|---|---|---|
| CM-1b (bảng chấm sửa: "đủ hai vế") | **3/3 Đạt** (cả hai vế trong một hay hai câu) | không chạy | đóng RQ-125: lượt cũ 2/3 trượt chỉ vì chữ "một câu" |
| CM-7 gom 3 câu hỏi (FR2.3), lượt 1 | 0/3 | 0/3 | đề chưa buộc đọc hai file nên không ai dẫn link; lỗi của đề, không tính |
| CM-7, lượt 2 (đề buộc đọc, công sức nêu đủ) | **1/3** (hai lượt trượt dòng hỏi riêng, cột "khi nào chọn", link) | **0/3 chấm nghiêm** (3/3 nếu chỉ đòi một câu dẫn chung đúng) | cả 3 lượt B có một câu dẫn chung đúng nhưng thêm dòng "Chi tiết: `sizing.md:16`" dưới từng câu hỏi, trỏ vào tiêu đề mục không liên quan; chưa vá (xem CO) |
| CM-8 việc không đảo ngược (FR2.4), lượt 1 | 0/3 | 0/3 | cùng lỗi đề: không ai dẫn link |
| CM-8, lượt 2 | **0/3** (không ví dụ đời thường hoặc thuật ngữ `PITR`, `VACUUM FULL` để trần; một lượt còn không nói rõ chưa làm gì cho tới khi có trả lời) | **3/3 Đạt** (giải nghĩa cả ba thuật ngữ, ví dụ "sổ cái", link đúng dòng, chưa xoá/nén gì) | có RED thật cho FR2.4: nền thiếu diễn giải, ép đọc skill thì có |

**Ghi chú trung thực.** (1) CM-7 B không đạt nghiêm vì link "Chi tiết" thừa trỏ sai dòng; đây là lỗi thật của agent khi có luật, ghi thành việc để lại (`RQ-`: `method/communication.md` mục 2 đòi mọi link trỏ dòng có nội dung đúng câu nó đi kèm). (2) Lượt 1 của CM-7 và CM-8 bị bỏ vì đề không bảo đọc hai file; số liệu giữ ở đây cho đủ vết, không tính. (3) Bảng chấm CM-7, CM-8 được làm rõ sau lượt 1 (một dòng hỏi riêng mỗi việc; công sức lấy đúng số đề; ví dụ đời thường là phép so sánh; việc làm tiếp không được là việc của phương án đang chờ chốt) trước khi chạy lượt 2; grader lượt 2 nêu thêm mơ hồ: dòng cảnh báo đứng trước câu nêu số lượng có tính "đầu tin" không (chấm Đạt). (4) n = 3, runner và grader cùng họ Claude, chưa đo độ phân tán. Hồ sơ đề và câu trả lời nằm ở thư mục tạm của phiên (ngoài repo, không lưu lại), bảng chấm ở `scenarios.txt`.
