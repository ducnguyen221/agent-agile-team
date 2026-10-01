---
skill: writing-plan
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: pending
date: 2026-10-01
result: not run — scenarios designed, execution deferred to TK5.7
---

# Thử áp lực — writing-plan

> **Kết luận:** 3 kịch bản thiết kế sẵn, **chưa chạy**; nhắm: chép code thay vì quyết định, thiếu bước
> RED→GREEN→commit, Trọng tâm review rỗng vì "SPEC không nói".

## Kịch bản 1 — SPEC 40 dòng, agent được giục "chi tiết vào"

**Áp lực:** SPEC ngắn cho hàm chuẩn hoá + endpoint tra cứu; người dùng nói "viết plan thật chi tiết,
Implementer là model rẻ, đừng để nó đoán".

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Tỷ lệ | PLAN dài gấp 4–6 lần SPEC, thân hàm đầy đủ trong mọi `TK` | code step = chữ ký + file + giá trị; thân chỉ cho thuật toán không xác định; PLAN ≤ ~2× SPEC |
| Giao diện | tên hàm lệch giữa `TK` | khối Giao diện dùng/sinh khớp nhau |

## Kịch bản 2 — `TK` không có bước test trước

**Áp lực:** yêu cầu viết PLAN cho việc sửa lỗi tính giá sai khi giảm giá chồng nhau.

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Khối Bước | "sửa hàm tính giá, chạy test, commit" | 1 RED (tên test + assertion với giá trị từ SPEC) → 2 chạy, kỳ vọng FAIL vì lý do X → 3 GREEN (chữ ký) → 4 chạy PASS + cả bộ → 5 commit có mã `TK` |
| Hồi quy | không nhắc | test phải hỏng khi gỡ bản sửa (trỏ `method/evidence.md` mục 4) |

## Kịch bản 3 — SPEC im lặng về đầu vào xấu

**Áp lực:** SPEC chỉ tả đường vui của upload CSV; người dùng nói "SPEC không nói gì về file lỗi, khỏi
lo".

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Trọng tâm review | rỗng hoặc "theo SPEC" | ≤5 dòng (file rỗng, encoding sai, cột thiếu, 100 MB, header trùng), mỗi dòng gắn test về `TK` sở hữu |
| Tự review 5 điểm | không có | có, nêu điểm 4 và 5 |

## Chạy lại

Prompt tự chứa gồm SPEC mẫu; RED không skill; GREEN đọc `skills/writing-plan/SKILL.md` trước; cùng
model; chấm theo cột; ghi model và kết quả thật vào frontmatter.
