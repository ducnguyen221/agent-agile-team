---
skill: response-style
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: sonnet (RED/GREEN/original of 2026-10-01); claude-sonnet-5-5 (GREEN rerun of 2026-10-04)
date: 2026-10-04
result: 3/3 GREEN pass; GREEN rerun 2026-10-04 3/3 pass on the tree at HEAD 05032b4 (SPR-04 TK11.10, skill body unchanged since 2026-10-01 so this attaches skill_sha and tier)
tier: T3
skill_sha: a00b4c8c4a90ec32d6f13f5e43e1f6d8635938f0
agent_ids:
  green_rerun_2026_10_04: {rs-1: af26a5eb29de2e971, rs-2: ab5587bbe2574b8a1, rs-3: a708cc8e24e2dffac}
---

# Thử áp lực — response-style

> **Kết luận:** 3/3 kịch bản: không có skill thì lỗi (nén mất cảnh báo bảo mật, trả lời 70 dòng không
> phân lớp, số không nguồn); có skill thì đạt. Cả hai pha chạy cùng model `sonnet`, cùng nguyên văn kịch
> bản; pha GREEN chỉ thêm một dòng "đọc SKILL.md trước".

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
