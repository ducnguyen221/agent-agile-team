---
skill: tdd
method: pressure-test with subagents (RED without skill, GREEN with skill, ORIGINAL with upstream skill)
model: claude-sonnet-5-5 (SPR-04 reruns and td-4); sonnet (runs of 2026-10-01), same scenario text
tier: T3
skill_sha: 994537299f230a89077baa002e24a5bcccdd2766
date: 2026-10-04
result: 4/4 GREEN pass; RED on the new scenario td-4 partial (0/1 pass); the three earlier scenarios passed already at RED (2026-10-01), GREEN not worse than original on 3/3
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

## Kết quả sau thêm danh sách ca biên bắt buộc có test (SPR-04 `TK5.4`, 2026-10-04)

Kịch bản mới `td-4` ("ba test là đủ, ca biên để sau" cho `slugify`; PLAN im lặng về ca biên). RED trên bản trước khi sửa: **Đạt một phần** (agent `abaceb8b`: bốn test vui, đẩy mọi ca biên sang `CQ`, không test nào cho rỗng, dấu cách liền, Unicode, ký tự đặc biệt). Sửa: mục 3 thêm đoạn "Ca biên bắt buộc có test" (tám nhóm; PLAN im lặng thì vẫn test hành vi an toàn tối thiểu và ghi ASSUMPTION; "ca biên để sau" không phải phép bỏ). GREEN: `td-4` **Đạt** (agent `a4cbcd2d`: chín test gồm rỗng, `None`, dấu cách liền và đầu/cuối, Unicode có dấu, emoji, ký tự SQL/shell). Ba kịch bản cũ chạy lại (chủ thể mới `claude-sonnet-5-5`): `tdd-1b` **Đạt** (`ad3bab9a`), `tdd-2b` **Đạt** (`a7c0a8ad`), `tdd-3b` **Đạt** (`a7169a28`). Lần chạy này cũng ghi `skill_sha` cho kịch bản của 2026-10-01 (thay nợ chạy GREEN lại). Output trọn ở `evidence/TK4/pressure-red-tk5.md` và `evidence/TK4/pressure-green-tk5.md` của hồ sơ sprint SPR-04 (lớp riêng).

## Kết quả sau vòng sửa làn M (SPR-04, 2026-10-04)

Chỉ đổi frontmatter `source`/`source_sha`/`license` (thêm nguồn ECC `ef648e01`); thân skill không đổi nên không chạy lại chủ thể thử, `skill_sha` ghi lại theo cây mới (hành vi đã kiểm ở các mục trên).

## Lỗ hổng đã vá sau RED

Không có: RED không gãy nên không có lỗi để vá (`skills/writing-skills/SKILL.md` mục 2 — không sửa khi chưa
thấy phép thử hỏng).

## Chạy lại

Như `skills/security-review/tests/pressure.md` mục "Chạy lại"; GREEN đọc `skills/tdd/SKILL.md`, gốc đọc
superpowers `test-driven-development/SKILL.md`. Lần sau nên chạy RED trong môi trường không nạp luật nền.
