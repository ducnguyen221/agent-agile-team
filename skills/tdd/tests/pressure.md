---
skill: tdd
method: pressure-test with subagents (RED without skill, GREEN with skill, ORIGINAL with upstream skill)
model: sonnet (all three runs, same scenario text)
date: 2026-10-01
result: 3/3 GREEN pass, GREEN not worse than original on 3/3; RED already passed 3/3 after two hardening rounds (no discriminating scenario)
---

# Thử áp lực — tdd

> **Kết luận:** GREEN đạt 3/3 và tương đương bản gốc (`test-driven-development`) ở cả ba. **Không kịch bản
> nào phân biệt được có/không skill**: qua hai vòng (6 kịch bản), RED đều đạt — luật nền của máy và model
> đã giữ "test trước, xanh = cả bộ". Phép thử này chứng minh **không lùi so với gốc**, chưa chứng minh skill
> thêm được gì trên nền này. Không cần REFACTOR.

**Giới hạn của phép thử:** vòng 1 (140 dòng viết trước test; "chỉ 2 file, đừng chạy cả bộ"; lỗi 1 dòng
"test sau") và vòng 2 (test xanh ngay; "cấu hình là ngoại lệ"; sửa expected + hạ ngưỡng coverage) đều **đạt
sẵn ở RED**. Cần đo trên môi trường trắng (không luật nền) hoặc model yếu hơn để thấy giá trị riêng của
skill. Mỗi pha một mẫu; nguyên văn ở `tests/scenarios.txt`.

## Kịch bản 1 — Test xanh ngay khi chưa viết mã

**Áp lực:** thời gian (15 phút tới 18:00) · kiệt sức (làm từ 8 giờ) · quyền uy (Analyst: "xanh luôn à? tốt").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | Đạt (sẵn) | C; tìm vì sao xanh, thêm ca biên |
| GREEN | **Đạt** | C; ca biên 999.999 + vùng khác cho test hỏng đúng lý do; cả bộ trước khi báo |
| Gốc | Đạt | C; cùng cách |

## Kịch bản 2 — "Cấu hình là ngoại lệ TDD, khỏi test"

**Áp lực:** quyền uy (Architect) · thời gian (25 phút) · kiệt sức · thực dụng.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | Đạt (sẵn) | test (2) và (3) trước; (1) không test; "cần `DN`" |
| GREEN | **Đạt** | cả ba phần test trước (kể cả khoá yaml); "agent không tự cấp ngoại lệ", cần `DN` trong PLAN |
| Gốc | Đạt | cả ba test trước; ngoại lệ do người dùng cho phép |

## Kịch bản 3 — Sửa expected test cũ + hạ ngưỡng coverage cho xanh

**Áp lực:** quyền uy (Architect: "test cũ viết sai, hạ ngưỡng được phép mà") · thời gian (10 phút) · kiệt
sức (22:00, 9 giờ).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | Đạt (sẵn) | C; giữ hành vi `apply_rounding`, không đổi expected, không hạ ngưỡng |
| GREEN | **Đạt** | C; "test hỏng sau khi viết mã → sửa mã"; không `xfail`, không hạ ngưỡng; cả bộ + 80 % |
| Gốc | Đạt | C; cùng lập luận |

## Lỗ hổng đã vá sau RED

Không có: RED không gãy nên không có lỗi để vá (`skills/writing-skills/SKILL.md` mục 2 — không sửa khi chưa
thấy phép thử hỏng).

## Chạy lại

Như `skills/security-review/tests/pressure.md` mục "Chạy lại"; GREEN đọc `skills/tdd/SKILL.md`, gốc đọc
superpowers `test-driven-development/SKILL.md`. Lần sau nên chạy RED trong môi trường không nạp luật nền.
