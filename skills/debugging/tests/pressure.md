---
skill: debugging
method: pressure-test with subagents (RED without skill, GREEN with skill, ORIGINAL with upstream skill)
model: sonnet (all three runs, same scenario text)
date: 2026-10-01
result: 3/3 GREEN pass, GREEN not worse than original on 3/3; RED already passed 2/3 after two hardening rounds
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

## Chạy lại

Như `skills/security-review/tests/pressure.md` mục "Chạy lại"; GREEN đọc `skills/debugging/SKILL.md`, gốc
đọc superpowers `systematic-debugging/SKILL.md`.
