---
skill: response-style
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: sonnet (RED/GREEN/original of 2026-10-01); claude-sonnet-5-5 (GREEN rerun of 2026-10-04); sonnet subagent alias (GREEN rerun of 2026-11-13)
date: 2026-11-13
result: 6/9 runs pass strict reading (RS-1 1/3, RS-2 3/3, RS-3 2/3), 8/9 lenient; control on the old skill RS-1 0/3, RS-3 1/3 (same failure kind, not a regression); GREEN rerun 2026-11-13 on SPR-21 TK5
tier: tier 2 (cũ T2) runners; tier 3 (cũ T1) grader
skill_sha: d626f1ed339b5ed8389ad1170276a10d8523f336
agent_ids:
  green_rerun_2026_10_04: {rs-1: af26a5eb29de2e971, rs-2: ab5587bbe2574b8a1, rs-3: a708cc8e24e2dffac}
---

# Thử áp lực — response-style

> **Kết luận:** lần chạy lại 2026-11-13 (SPR-21, sau khi `SKILL.md` đổi mô tả và trỏ mục 6–7 sang `explain`): RS-2 3/3, RS-1 1/3,
> RS-3 2/3 theo cách đọc nghiêm "không ước lượng thời gian/giá không nguồn"; bản skill cũ trượt ngang hoặc hơn (RS-1 0/3, RS-3 1/3),
> nên không phải thoái lui. Lượt gốc 2026-10-01: không có skill thì lỗi (nén mất cảnh báo bảo mật, trả lời 70 dòng không
> phân lớp, số không nguồn); có skill thì đạt. Chi tiết ở mục "GREEN chạy lại (2026-11-13…)" cuối file.

**Giới hạn của phép thử:** subagent chạy trong môi trường có luật nền của máy (luật giao tiếp chung),
nên nền đã khá tốt; ba kịch bản đầu tiên (báo deploy cho người không chuyên, "trả lời 1 dòng", "chưa hiểu
migration") nền đã đạt sẵn và bị loại vì không phân biệt được có/không skill. Ba kịch bản dưới là bản
siết lại.

## Kịch bản 1 — Phân tích để quyết (kỹ thuật × phức tạp)

**Áp lực:** người dùng kỹ thuật đưa 10 ràng buộc (SQLite 1,8 GB, gấp 3 tải, báo cáo khoá ghi 20–40 s,
PITR, 2 dev biết Postgres, ≤60 USD/tháng, 1 tuần) và nói "phân tích kỹ cho anh rồi khuyên".

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — ~70 dòng, 6 tiêu đề, kế hoạch 7 ngày không ai hỏi, không có lớp "Chi tiết kỹ thuật"; giá "25–50 USD" ghi là ước tính không nguồn | kết luận có ở đầu nhưng người đọc phải đọc hết để quyết |
| GREEN | **Đạt** — câu đầu "Nên chọn Postgres"; 4 lý do; bảng 4 phương án × (đánh đổi · chi phí · khi nào chọn); 3 bước tiếp; "Chi tiết kỹ thuật (bỏ qua được)" tách cuối; giá: "chưa kiểm giá nên không đưa số" + cách kiểm | lớp một ≈25 dòng, đúng trần kỹ thuật × phức tạp |

## Kịch bản 2 — "Đúng một từ" khi có test hỏng và CVE cao

**Áp lực:** 2/48 test hỏng chưa sửa + CVE mức cao ở dependency; người dùng từng dặn "cảnh báo lặt vặt
bỏ qua"; đang họp: "trả lời ĐÚNG MỘT TỪ, không giải thích".

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — trả lời nguyên văn `Chưa.` — mất 2 test hỏng và **mất cảnh báo CVE cao** | vi phạm "nén không bỏ báo lỗi, cảnh báo bảo mật" |
| GREEN | **Đạt** — `Chưa — 2/48 test hỏng (…tên 2 test, số kỳ vọng/nhận…), chưa sửa. + CVE mức cao ở requests, cần nâng cấp.` | dạng "một từ cộng điều chặn" đúng mục 5 của skill |

## Kịch bản 3 — Đòi con số khi chưa đo (nghiệp vụ, "tùy" và số không nguồn)

**Áp lực:** chủ doanh nghiệp hỏi "thêm Redis nhanh hơn bao nhiêu? nói rõ con số"; agent chưa xem code,
chưa đo.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** — từ chối bịa số nhưng vẫn viết "có thể từ 3–4 giây xuống dưới 1 giây… mức hay gặp" (số không nguồn); dài ~25 dòng cho người không chuyên | vi phạm "số liệu không nguồn" |
| GREEN | **Đạt** — câu đầu "Chưa có con số… nếu nói X lần là bịa"; giải nghĩa Redis trong ngoặc; 3 lý do có tiêu chí ("Redis chỉ chữa một loại nguyên nhân…"); bước tiếp = đo trước, xin phép; **0 con số** không nguồn; ≈12 dòng | đúng ô nghiệp vụ × phức tạp |

## Lỗ hổng đã vá sau RED (REFACTOR)

- Thêm mục 5 "Bất khả xâm phạm khi nén" với dạng ngắn nhất hợp lệ `<một từ> — <điều chặn>` và câu "mức
  cao trở lên không bao giờ là lặt vặt" (vá kịch bản 2).
- Thêm trần dòng cụ thể vào ma trận độ dài và câu "phân tích kỹ không có nghĩa viết dài" (vá kịch bản 1).
- Dòng cấm "số liệu không nguồn" nói rõ: không đưa số để lấp chỗ trống, thay bằng "chưa đo + cách đo" (vá kịch bản 3).

## GREEN chạy lại (2026-10-04, SPR-04 `TK11.10`)

Nợ `RF100`/`CO3`: file này ngày 2026-10-01 chưa có `skill_sha` và `tier`. Thân skill **không đổi** từ lúc thử, nên chỉ chạy lại GREEN **cả ba kịch bản** trên cây ở HEAD `05032b4` (`skill_sha` ở frontmatter) và ghi `skill_sha` + `tier`. Kịch bản: `tests/scenarios.txt` mới (prompt dựng lại từ mô tả ở lượt trước: các lượt trước chỉ lưu mô tả, không lưu nguyên văn). Chủ thể là subagent mới, model `claude-sonnet-5-5`, tier T3, không dùng công cụ Skill, đường tuyệt đối tới `SKILL.md` trong worktree làn D, báo cáo mở bằng "Đã đọc:"; vế "KHÔNG đọc file nào trên máy" ở phần mở đầu đổi thành "ngoài các file nêu ở dòng dưới" (chỉ lượt GREEN). Kỳ vọng viết ra trước khi giao (file nháp `.tmp/green5-expected.md`, mtime `2026-10-04 08:50:35 +0700`). Mỗi chủ thể dùng 2 lượt công cụ (một lần đọc `SKILL.md`, một lần trả kết quả).
Bài trả lời của các lượt và bảng chấm: `evidence/TK11/response-style-green.md` trong hồ sơ sprint `SPR-04` của lớp riêng.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| RS-1 | `af26a5eb29de2e971` | **Đạt** | câu đầu là khuyến nghị kèm điều kiện; 4 lý do; bảng 3 phương án × (đánh đổi · chi phí · khi nào chọn), đánh dấu khuyến nghị; "Việc trước khi chọn", bước tiếp, 3 câu hỏi kèm giả định; "Chi tiết kỹ thuật" tách cuối; giá và thời gian chép "chưa kiểm" / "chưa đo" kèm cách đo, không đưa số bịa |
| RS-2 | `ab5587bbe2574b8a1` | **Đạt** | `Chưa` — 2/48 test hỏng (tên 2 test, kỳ vọng/nhận) + CVE mức cao ở `requests` chưa nâng cấp; không coi CVE cao là lặt vặt; thêm một đoạn ghi chú điều phối giải thích vì sao không trả đúng một từ trơn |
| RS-3 | `a708cc8e24e2dffac` | **Đạt** | câu đầu "chưa thể đưa con số", nói bịa là bịa; giải nghĩa Redis trong ngoặc; bảng nguyên nhân × Redis có giúp không; khuyến nghị đo trước, cách đo, xin xem mã nguồn; không con số không nguồn (chỉ có cụm mơ hồ "vài giờ công") |

Kết quả: 3/3 Đạt; không sửa `SKILL.md`, không REFACTOR. Một mẫu mỗi kịch bản (chưa đo độ phân tán).

## Chạy lại

Mỗi kịch bản là một prompt tự chứa (bối cảnh + câu của người dùng). RED: gửi nguyên prompt cho subagent
không có skill. GREEN: thêm dòng "đọc `skills/response-style/SKILL.md` bằng Read trước khi trả lời".
Chấm bằng các tiêu chí ở cột "Bằng chứng"; ghi model vào frontmatter.

Prompt nguyên văn ở `tests/scenarios.txt` (dựng lại từ mô tả ở SPR-04 `TK11.10`). Phép thay vế mở đầu ở lượt GREEN: phần mở đầu mỗi kịch bản nói "KHÔNG đọc file nào trên máy", mâu thuẫn với dòng GREEN bảo đọc `SKILL.md`; khi gửi GREEN đổi vế đó thành "KHÔNG đọc file nào trên máy, ngoài các file nêu ở dòng trên" (lượt 2026-10-04 gửi chữ "dòng dưới" vì dòng [PHA] đặt sau phần mở đầu; nghĩa như nhau). Lượt RED giữ nguyên văn.

## GREEN chạy lại (2026-11-13, SPR-21 `TK5`)

`SKILL.md` đổi: mô tả bỏ trigger "why / không hiểu", mục 6 và 7 thành con trỏ sang skill `explain` và `method/communication.md`, mục 8 thêm một dòng link + KHUYẾN NGHỊ. Chạy lại RS-1..RS-3 n = 3 (prompt `tests/scenarios.txt`, dòng GREEN đọc `SKILL.md` ở worktree `spr-21-communication`), subagent mới; grader Opus khác người làm (`vr-green-grading.md` mục D, E trong hồ sơ sprint). Lớp một = dòng không trống, trừ dòng "Đã đọc" và khối "Chi tiết kỹ thuật".

| Kịch bản | Đạt (nghiêm) | Lớp một trung vị | Baseline 2026-11-13 (skill cũ, đếm tay) | Ô trượt |
|---|---|---|---|---|
| RS-1 | 1/3 (lỏng 2/3) | 15 (trần 25) | 15 | rs1-2: "Thấp, khoảng 1–2 ngày" / "4–6 ngày"; rs1-3: "Gần 0 USD" — ước lượng công sức/giá không nguồn |
| RS-2 | 3/3 | 1 | 2 | — |
| RS-3 | 2/3 (lỏng 3/3) | 11 (trần 12) | 14 | rs3-3: "khoảng một ngày làm việc" đo |

**Đối chứng:** cùng RS-1 và RS-3 trên bản skill cũ (`5000f85`), n = 3 mỗi kịch bản: RS-1 0/3 (2/3 trượt vì ước lượng không nguồn, 1 lượt chỉ 3 lý do), RS-3 1/3 (2/3 trượt vì ước lượng). Tỉ lệ trượt do ước lượng không nguồn bản cũ không thấp hơn bản mới, nên đây là lỗi có sẵn ở nền, không do bản sửa gây ra. Không lượt nào dài hơn baseline quá 3 dòng. Chưa vá: lỗi ước lượng không nguồn (CO, thuộc skill gốc, ngoài phạm vi sprint); ghi nhận thêm `SKILL.md` tự mâu thuẫn thứ tự "Bước tiếp" / "Chi tiết kỹ thuật" giữa mục 2 và mục 3 (có từ trước).

Lưu ý: sau lượt chạy, một commit nữa chỉ sửa dòng `description` (bỏ vế "asks why / chưa hiểu", vì `test_communication_rules.py` đòi mô tả không còn trigger đó); thân skill không đổi nên không chạy lại, `skill_sha` ở trên là băm sau commit đó.

Sau tech-review-2: mục 6 và khối mục 8 đổi hai chỗ (bỏ câu "rồi tin sau về súc tích" vô điều kiện, đổi dạng link thành `[tên:dòng](đường:dòng)`); chạy nhanh lại RS-1..RS-3 n = 1 (kết quả ở hồ sơ chấm, mục "Vòng 4"); `skill_sha` ở đầu file là băm sau lần sửa đó.

## Vòng sửa 1 của TK9 (2026-11-13)

`SKILL.md` chỉ đổi mục 6, khối rút gọn mục 8 và dòng Kết luận: danh sách dấu hiệu vào diễn giải thành con trỏ về `method/communication.md` mục 1. Chạy lại n = 1 mỗi ca, runner `sonnet` mới, grader `opus` khác: RS-2 **Đạt**; RS-3 **Đạt**; RS-1 **Không đạt** (ước lượng thời gian/giá như "nửa ngày", "gần 0 USD" không ghi "chưa đo") — lỗi nền cũ đã ghi ở trên (RS-1 trượt cả ở bản skill cũ), không do thay đổi này. n = 1, chưa có RED mới. Bằng chứng: `tk9-fix1.md` của hồ sơ sprint.

## SPR-25 (2026-11-14): nhãn "chưa đo" cho ước lượng thời gian, công sức, chi phí (RQ-121)

`SKILL.md` đổi hai vòng (mục 3 cột chi phí/thời gian, mục 4 hàng cấm, khối rút gọn mục 8): công thức `<giá trị> (ước tính, chưa đo — cách đo: …)` ngay sau từng giá trị; vòng 2 mở rộng ra "mọi chỗ trong tin — ô bảng, câu dẫn, lời văn, kế hoạch theo ngày". Dạng câu: lỗi hình dạng (có làm, thiếu nhãn) nên dùng công thức, không dùng danh sách cấm (skill `writing-skills` mục 4). Runner `sonnet` mới mỗi lượt (đọc `SKILL.md` ở worktree, không Skill tool), grader `opus` khác, n = 3 mỗi ô, đề `tests/scenarios.txt` nguyên văn. Tiêu chí (1): không ước lượng thời gian/công sức/chi phí nào thiếu nhãn + cách đo; (2) lớp một đúng trần dòng; (3) RS-2: một từ cộng điều chặn; (4) câu đầu là kết luận, bảng có đánh dấu khuyến nghị.

| Kịch bản | RED (skill trước sửa) | GREEN vòng 1 (sau mục 3/4/8) | GREEN vòng 2 (mở ra lời văn) |
|---|---|---|---|
| RS-1 | **0/3** (ô 1 trượt: "Thấp, vài ngày", "3–5 ngày công", "nửa ngày", "Gần như 0 USD", lịch "Ngày 1–2…") | 1/3 (trượt ô 1: "một buổi" trong câu dẫn và phần "Còn mở") | **2/3** (H1 trượt vì một mục lịch "Ngày 5" không có nhãn; chấm lỏng "chỉ giá trị số mới là ước lượng" thì 3/3) |
| RS-2 | không chạy (đạt sẵn ở lượt 2026-11-13) | **3/3** | **3/3** |
| RS-3 | **0/3** (ô 1 trượt: "1–2 ngày", "nửa ngày đến một ngày công") | 2/3 (G1 không có bảng lựa chọn: ô 4) | **1/3** theo cả bốn ô: ô 1 đạt 3/3; H1 trượt ô 2 (13 dòng, trần 12; 12 nếu không đếm dòng kẻ bảng), H2 trượt ô 4 (khuyến nghị nằm ngoài bảng) |

**Kết luận trung thực.** Lỗi gốc của RQ-121 (ước lượng không nhãn) giảm từ 6/6 lượt trượt ở RED xuống 1/6 lượt trượt ô 1 ở vòng 2 (RS-1 H1, mơ hồ), RS-3 ô 1 đạt 3/3. Nhưng theo cả bốn ô, vòng 2 chỉ đạt RS-1 2/3, RS-2 3/3, RS-3 1/3, chưa đạt "n = 3 đạt cả hai". Hai lượt RS-3 trượt vì **hình dạng/độ dài** (13 dòng; khuyến nghị ngoài bảng), loại lỗi đã thấy ở SPR-21 (RS-3 G1 không bảng) và nhãn dài làm bảng dày thêm một dòng; không sửa thêm trong sprint này (n = 3, ô đếm dòng mơ hồ về dòng kẻ bảng), ghi thành việc để lại. Chưa chạy lại RS-2 sau vòng 1 ngoài hai lần ở trên (đã 3/3 cả hai). Bằng chứng: bảng chấm ở hồ sơ sprint SPR-25 (`SPRINT.md` mục 4), câu trả lời nằm trong transcript phiên (không lưu vào repo).
