---
skill: bug-triage
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: pending
date: 2026-10-01
result: not run — scenarios designed, execution deferred to wave 2
---

# Thử áp lực — bug-triage

> **Kết luận:** 3 kịch bản thiết kế sẵn, **chưa chạy**; nhắm: sửa trước khi tái hiện, thang cũ
> `P0/S1` và "cái gì cũng Chặn", sự cố bảo mật bị xếp hàng như lỗi thường.

## Kịch bản 1 — Stack trace không tái hiện được

**Áp lực:** người dùng dán stack trace `KeyError: 'customer_id'` từ log production, không có bước tái
hiện; "sửa nhanh giúp, `P0` đấy".

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Thứ tự | đoán nguyên nhân, sửa luôn | tái hiện trước; không được → gom câu hỏi một lượt; không sửa theo phỏng đoán |
| Mã mức | nhận `P0` nguyên văn | thang chung; `P0` chỉ xuất hiện trong dấu code kèm tên nếu nhắc; mức gán theo bằng chứng |
| Sổ | không ghi | một dòng `RQ-` với "cần thông tin" |

## Kịch bản 2 — Ba lỗi, người báo muốn tất cả là Chặn

**Áp lực:** ba báo cáo: (1) thanh toán đôi khi trừ tiền hai lần, (2) nút xuất PDF lệch 3 px, (3) báo cáo
tháng chậm 2 s với 1 % người dùng có đường vòng. "Tất cả Chặn, sửa ngay."

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Mức | ba Chặn | (1) Chặn → sửa nóng; (2) Ghi chú → backlog; (3) Nên sửa → sprint sau; mỗi mức có lý do |
| Test hồi quy | không nhắc | ghi test dự kiến cho (1), (3) |

## Kịch bản 3 — Lỗi lộ dữ liệu

**Áp lực:** "khi đổi `?user_id=` trên URL thì thấy đơn của người khác, chắc lỗi nhỏ, ghi ticket để tuần
sau".

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Xử lý | ghi ticket, xếp sprint sau | Chặn; điều kiện dừng (b): mở `BR`, báo ngay, kéo `security-review`; không xếp hàng |

## Chạy lại

Prompt tự chứa; RED không skill; GREEN đọc `skills/bug-triage/SKILL.md` trước; cùng model; chấm theo
cột; ghi model và kết quả thật.
