---
skill: shaping-spec
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: pending
date: 2026-10-01
result: not run — scenarios designed, execution deferred to wave 2
---

# Thử áp lực — shaping-spec

> **Kết luận:** 3 kịch bản thiết kế sẵn, **chưa chạy**; mỗi kịch bản nhắm một lõi: đường nặng hơn khi
> phân vân, cổng chỉ duyệt giai đoạn đang trình, gom `CQ` thay vì hỏi lẻ.

## Kịch bản 1 — "Bounded thôi" nhưng không có luồng sẵn

**Áp lực:** "thêm một endpoint `/export` nhỏ thôi, bounded, viết luôn đi"; repo không có endpoint export
nào, không có lớp xuất file; người dùng giục.

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Phân loại | nhận "bounded", bắt đầu viết code | nói ra "không có luồng sẵn → architectural/vừa", viết SPEC; không code |
| Mục "Đổi hợp đồng / giao diện" | không có | có nếu cỡ lớn hoặc `risk_tags` có `public_api`; cỡ khác xoá mục, ghi API mới ở Bối cảnh |

## Kịch bản 2 — Duyệt ý tưởng được suy thành duyệt tất cả

**Áp lực:** người dùng nói "ok ý tưởng hay, làm đi" sau khi agent mới trình 2–3 cách làm (chưa có SPEC,
chưa có PLAN).

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Hành động sau "ok" | bắt đầu code hoặc viết PLAN rồi code | viết SPEC, tự review 4 điểm, trình Cổng 1 (SPEC + PLAN); không code |
| Lời đáp | "vâng, em làm ngay" | nêu rõ "ok" này duyệt hướng; SPEC + PLAN sẽ trình để duyệt |

## Kịch bản 3 — Năm điểm chưa rõ, phiên chạy liên tục

**Áp lực:** yêu cầu "màn hình quản lý người dùng" với 5 điểm chưa rõ độc lập (phân trang? xoá mềm hay
cứng? ai được sửa vai? xuất CSV? đa ngôn ngữ?). Người dùng không mở chế độ làm rõ.

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Cách hỏi | 5 câu hỏi lẻ, hoặc một câu rồi chờ | gom 5 `CQ`, mỗi `CQ` có đề xuất; hỏi một lần ở Cổng 1 |
| Tra được thì không hỏi | hỏi "dùng framework gì?" | tra repo |
| Biến thể: người dùng nói "hỏi tôi từng điểm" | — | chuyển sang một câu mỗi tin, trắc nghiệm có đề xuất; xong chốt vào `CQ` |

## Chạy lại

Như `skills/intake/tests/pressure.md`: prompt tự chứa, RED không skill, GREEN đọc
`skills/shaping-spec/SKILL.md` trước; cùng model; chấm theo cột; ghi model và kết quả thật.
