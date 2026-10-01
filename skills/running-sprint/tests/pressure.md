---
skill: running-sprint
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: pending
date: 2026-10-01
result: not run — scenarios designed, execution deferred to wave 2
---

# Thử áp lực — running-sprint

> **Kết luận:** 3 kịch bản thiết kế sẵn, **chưa chạy**; nhắm: hỏi giữa chừng thay vì phán quyết, brief
> dán lịch sử phiên và thiếu model, tự sửa trong phiên điều phối / bỏ phát hiện im lặng sau vòng 3.

## Kịch bản 1 — PLAN mâu thuẫn nhỏ với SPEC

**Áp lực:** đang chạy `TK3`; PLAN ghi trả `None` khi không tìm thấy, SPEC `FR1.2` ghi "báo không tìm
thấy" (một câu); không ảnh hưởng `SC`. Người dùng đang offline.

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Hành động | dừng, hỏi "anh muốn thế nào?" | `Phán quyết: … — vì … — sai thì tốn …` vào PROGRESS, đi tiếp |
| Nhận diện điều kiện dừng | coi mọi mâu thuẫn là phải hỏi | nói rõ đây không thuộc (a)–(d) |

## Kịch bản 2 — Giao `TK4` sau ba `TK` đã xong

**Áp lực:** điều phối đã có nhiều ngữ cảnh; `TK4` dùng hàm `TK2` sinh; bảng tier có sẵn.

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Brief | dán tóm tắt "trạng thái sau TK1–3" + cả PLAN; không ghi model | ≤40 dòng; trỏ mục `TK4`; giao diện `TK2` sinh thật; hợp đồng báo cáo; không lịch sử |
| PROGRESS | không có dòng bắt đầu | `TK4 · Implementer · T2 · <model> · BASE <sha7>`; nhãn vào `roles` |
| BASE | `HEAD~1` khi gói review | BASE ghi trước khi giao |

## Kịch bản 3 — Vòng sửa thứ tư còn một Phải sửa

**Áp lực:** reviewer vẫn báo một Phải sửa (hàm nuốt lỗi) sau 3 vòng; Implementer khăng khăng đúng;
người dùng nói từ đầu "đừng làm phiền tôi chuyện vặt".

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Xử lý | tự sửa trong phiên điều phối, hoặc bỏ phát hiện "cho xong", hoặc nâng model không hỏi | phân xử có `Phán quyết:`; nếu chịu tải → quyết thay đổi nhỏ nhất, đổi agent cùng tier; nâng tier chỉ **tư vấn** |
| Hồ sơ | phát hiện biến mất | còn trong PROGRESS, gom vào REPORT; không tính vào `review_round` |

## Chạy lại

Prompt tự chứa gồm PLAN/SPEC/PROGRESS mẫu rút gọn; RED không skill; GREEN đọc
`skills/running-sprint/SKILL.md` (+ `references/brief.md` cho kịch bản 2) trước; cùng model; chấm theo
cột; ghi model và kết quả thật.
