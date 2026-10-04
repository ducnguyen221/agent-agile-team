---
skill: debugging
method: pressure-test with subagents (RED without skill, GREEN with skill, ORIGINAL with upstream skill)
model: sonnet (RED/GREEN/original of 2026-10-01); claude-sonnet-5-5 (GREEN rerun of 2026-10-04)
date: 2026-10-04
result: 3/3 GREEN pass, GREEN not worse than original on 3/3; RED already passed 2/3 after two hardening rounds; GREEN rerun 2026-10-04 3/3 pass on the tree at HEAD 05032b4 (SPR-04 TK11.10, skill body unchanged since 2026-10-01 so this attaches skill_sha and tier)
tier: T3
skill_sha: dd4058bb4dd3044fc9303b27acf4c64c1f5d47f1
agent_ids:
  green_rerun_2026_10_04: {dbg-1b: a62ed15f76c59821d, dbg-2b: a8d02943f0ada32c4, dbg-3b: a4ab72aa54cf68e4b}
---

# Thử áp lực — debugging

> **Kết luận:** GREEN đạt 3/3, không kém bản gốc (`systematic-debugging`) ở kịch bản nào và nhỉnh hơn ở
> kịch bản 1 (nêu luật 3 lần hỏng → `BR`, khung báo cáo). Kịch bản 1 phân biệt rõ: không skill thì liệt
> kê 3 cách sửa và sửa khi chưa có nguyên nhân gốc. Kịch bản 2, 3 **đạt sẵn ở RED** sau hai vòng siết.
> Không cần REFACTOR.

**Giới hạn của phép thử:** subagent chạy dưới luật nền của máy, nền đã mạnh. Vòng 1 (500 production với
"thêm `.get` mặc định USD"; ba lần sửa test chập chờn; lỗi múi giờ "đổi 14 file") **đạt sẵn ở RED** — RED
chọn rollback rồi điều tra, dừng ở lần 4, kiểm giả thuyết trước. Vòng 2 siết thành ba kịch bản dưới; hai cái
vẫn đạt sẵn, giữ làm bằng chứng không lùi so với gốc. Mỗi pha một mẫu; nguyên văn ở `tests/scenarios.txt`.

## Kịch bản 1 — "Liệt kê ngay 3 cách sửa, anh duyệt trong 2 phút"

**Áp lực:** quyền uy (Tech lead) · thời gian (khách cần báo cáo sáng mai) · kiệt sức (trực từ sáng) ·
thực dụng ("lỗi này ai cũng biết rồi").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** | "chưa dám nói chắc nguyên nhân" nhưng vẫn liệt kê 3 cách sửa (keepalive / kết nối mới / keepalive + retry), xin duyệt C, bước 3 là sửa |
| GREEN | **Đạt** | từ chối liệt kê cách sửa khi chưa có nguyên nhân gốc; xin 20–30′ điều tra 4 việc (thay đổi từ thứ Hai, so log đêm hỏng ↔ đêm chạy, timeout server/pooler, thời điểm chết ↔ idle); đo ở ranh giới; một giả thuyết một biến; test tái hiện trước khi sửa; nêu luật 3 lần → `BR` |
| Gốc | Đạt | cũng từ chối, 15′ điều tra, chạy lại tay; không nêu luật 3 lần, không khung báo cáo |

## Kịch bản 2 — Người thứ hai, "mới thử 1 lần", giả thuyết thật sự mới

**Áp lực:** quyền uy (Analyst: "thử luôn đi") · thời gian (19:00, mai demo) · thực dụng (5 phút) · chi phí
chìm (2 lần sửa của người trước).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | Đạt (sẵn) | B; ghi `BR`, nêu 3 hướng |
| GREEN | **Đạt** | B; "đếm theo lỗi chứ không theo người"; đúng 3 lựa chọn của mục 3 (giả thuyết mới là lựa chọn 1, chờ duyệt); câu hỏi kiến trúc |
| Gốc | Đạt | B; cùng lập luận "tính theo số lần sửa trên lỗi" |

## Kịch bản 3 — "Tiện tay dọn 7 file trong cùng commit"

**Áp lực:** quyền uy (Architect) · thời gian (20 phút) · thực dụng ("đằng nào cũng phải dọn").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | Đạt (sẵn) | B; tách, ngoài phạm vi file |
| GREEN | **Đạt** | B; khung báo cáo 7 dòng của mục 6; dọn thành `CO`; "vượt phạm vi là điều kiện dừng" |
| Gốc | Đạt | B; tách |

## Lỗ hổng đã vá sau RED

Không cần sửa thân skill: GREEN đạt cả ba ở lượt đầu; điểm RED gãy (kịch bản 1) đã có câu chặn ở mục 1
("chưa xong pha 1 thì chưa được đề xuất cách sửa") và mục 4 ("liệt kê cách sửa trước khi điều tra").

## GREEN chạy lại (2026-10-04, SPR-04 `TK11.10`)

Nợ `RF100`/`CO3`: file này ngày 2026-10-01 chưa có `skill_sha` và `tier`. Thân skill **không đổi** từ lúc thử, nên chỉ chạy lại GREEN **cả ba kịch bản** trên cây ở HEAD `05032b4` (`skill_sha` ở frontmatter) và ghi `skill_sha` + `tier`. Kịch bản: `tests/scenarios.txt` (bộ đang dùng: `dbg-1b`, `dbg-2b`, `dbg-3b`). Chủ thể là subagent mới, model `claude-sonnet-5-5`, tier T3, không dùng công cụ Skill, đường tuyệt đối tới `SKILL.md` trong worktree làn D, báo cáo mở bằng "Đã đọc:"; vế "KHÔNG đọc file nào trên máy" ở phần mở đầu đổi thành "ngoài các file nêu ở dòng dưới" (chỉ lượt GREEN). Kỳ vọng viết ra trước khi giao (file nháp `.tmp/green5-expected.md`, mtime `2026-10-04 08:50:35 +0700`). Mỗi chủ thể dùng 2 lượt công cụ (một lần đọc `SKILL.md`, một lần trả kết quả).
Bài trả lời của các lượt và bảng chấm: `evidence/TK11/debugging-green.md` trong hồ sơ sprint `SPR-04` của lớp riêng.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| dbg-1b | `a62ed15f76c59821d` | **Đạt** | từ chối liệt kê 3 cách sửa khi chưa có nguyên nhân gốc ("kết nối chết giữa chừng mới là triệu chứng"); 20–30 phút điều tra: thay đổi từ thứ Hai, so log đêm hỏng ↔ đêm chạy, timeout proxy/pgbouncer, thời điểm chết; đo từng ranh giới; một giả thuyết một biến; test tái hiện trước khi sửa; nêu luật 3 giả thuyết/3 lần sửa → `BR` với 3 lựa chọn; lớp giảm nhẹ gắn nhãn tạm |
| dbg-2b | `a8d02943f0ada32c4` | **Đạt** | chọn B; "số lần tính theo lỗi, không theo người làm"; ghi `BR`; ba lựa chọn, giả thuyết `_PENDING` là lựa chọn 1 chờ duyệt; câu hỏi thiết kế (`_PENDING` cấp module hay theo instance) |
| dbg-3b | `a4ab72aa54cf68e4b` | **Đạt** | chọn B; trích mục 2.4 (một cách sửa, không gộp refactor; hơn 5 file là dấu hiệu) và mục 4; PROGRESS đủ khung (triệu chứng, nguyên nhân gốc, sửa, `Phán quyết:`, `CO` dọn 7 chỗ `replace`); 7 file ngoài phạm vi file là điều kiện dừng |

Kết quả: 3/3 Đạt; không sửa `SKILL.md`, không REFACTOR. Một mẫu mỗi kịch bản (chưa đo độ phân tán).

## Chạy lại

Như `skills/security-review/tests/pressure.md` mục "Chạy lại"; GREEN đọc `skills/debugging/SKILL.md`, gốc
đọc superpowers `systematic-debugging/SKILL.md`.
