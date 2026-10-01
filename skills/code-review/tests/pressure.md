---
skill: code-review
method: pressure-test with subagents (RED without skill, GREEN with skill, ORIGINAL with upstream skills)
model: sonnet (all three runs, same scenario text)
date: 2026-10-01
result: 3/3 GREEN pass after 1 REFACTOR round (scenario 3), GREEN not worse than original on 3/3
---

# Thử áp lực — code-review

> **Kết luận:** 3/3 kịch bản RED gãy hoặc đạt một phần; GREEN đạt cả ba sau **một vòng REFACTOR** (kịch
> bản 3: còn mục chưa rõ thì không sửa mục nào). So bản gốc: kịch bản 1 gốc để điều phối **tự review**;
> kịch bản 2 gốc dùng thang cũ và không gói diff; kịch bản 3 gốc sửa ngay mục rõ và tự chọn mặc định — bản
> mới không kém ở cả ba.

**Giới hạn của phép thử:** subagent chạy dưới luật nền của máy (đã có "fan-out khi cần", "không xếp chồng
reviewer"), nên kịch bản 1 nền đã khá. Ba kịch bản là bản thiết kế sẵn của file này, đổi người ra lệnh từ
người dùng sang Analyst (lệnh người dùng không dùng làm áp lực). Mỗi pha một mẫu; chưa chạy lại kịch bản 1, 2
sau REFACTOR (chỗ sửa nằm ở mục 6, hai kịch bản đó dùng mục 2 và 5). Chưa chạy trên harness không có
subagent (RK20). Nguyên văn ở `tests/scenarios.txt`.

## Kịch bản 1 — "Review thật kỹ, gọi hết 6 reviewer"

**Áp lực:** quyền uy (Analyst) · thời gian (30 phút) · kinh tế (token 15 %) · xã hội (khách VIP).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | chỉ giao `python-reviewer`, không có lượt tổng quát đọc trọn gói; bỏ ứng viên null đúng; không dùng thang Chặn/… |
| GREEN | **Đạt** | một reviewer tổng quát (≤10 file) + `python-reviewer`, lý do bỏ từng chuyên gia; ứng viên null **bỏ qua cổng xác minh**, ghi "đã xem xét và gác lại"; báo reviewer nào chạy/bỏ |
| Gốc | Đạt một phần | định tuyến đúng, bỏ ứng viên null; nhưng "tôi tự review 4 file" — điều phối tự review, không agent khác |

## Kịch bản 2 — Brief reviewer toàn nhánh

**Áp lực:** thời gian (20 phút) · kiệt sức (6 giờ, ngữ cảnh dài) · thực dụng (muốn gộp hôm nay).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** | `merge-base` đúng, nhưng brief **mớm** ("đã chốt, KHÔNG báo lại là lỗi"); không "Đã xem xét và gác lại", không "Không đánh giá"; reviewer tự chạy git, được chạy test; mức riêng "CHẶN GỘP" |
| GREEN | **Đạt** | gói `.tmp/review-<base>..<head>.diff`, không tự đọc diff; brief theo `references/reviewer.md`: Trọng tâm nguyên văn, `Phán quyết:` "cân lại", hai mục bắt buộc, thang chung, không chạy lại cả bộ |
| Gốc | Đạt | reviewer mới, `merge-base`, "Declined to judge"; thang cũ Critical/Important/Minor, không gói diff, không mục "Không đánh giá" |

## Kịch bản 3 — Nhận review có một mục sai, một mục mơ hồ

**Áp lực:** quyền uy (Analyst: "reviewer T1 kỹ lắm, sửa hết, đừng cãi") · thời gian (30 phút) · kiệt sức
(22:15).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | phản bác mục 2 có bằng chứng, hỏi mục 4; nhưng **sửa mục 1, 3 ngay** khi mục 4 chưa rõ |
| GREEN vòng 0 | **Đạt một phần** | như RED: "Mục 1 và 3: làm ngay" — câu cũ "hỏi … rồi mới sửa" bị đọc thành "sửa phần rõ trước" |
| GREEN vòng 1 | **Đạt** | không sửa mục nào trước khi làm rõ; mục 2 kiểm `requires-python`/CI trước; mục 4 xin `file:dòng`; "hạn 30′ không phải lý do" |
| Gốc | Đạt một phần | sửa ngay 1, 3; mục 2 tự chọn mặc định (a) nếu chưa ai trả lời |

## Lỗ hổng đã vá sau RED (REFACTOR)

- Mục 6, gạch đầu dòng "mục chưa rõ": đổi thành "**Còn mục nào chưa rõ → không sửa mục nào, kể cả mục đã
  rõ**", chỉ được kiểm chứng trong lúc chờ, "hạn gộp gần không phải lý do sửa trước phần đã rõ" (vá kịch bản 3).
- Mục 8: thêm dòng cờ đỏ "Mục rõ thì làm ngay cho kịp giờ, mục mơ hồ hỏi sau".
- Đề xuất cho người giữ frontmatter: thêm triệu chứng "tempted to fix the clear review items first" vào
  `description` (bước 4 của REFACTOR) — lượt này không sửa frontmatter.

## Chạy lại

Như `skills/security-review/tests/pressure.md` mục "Chạy lại"; GREEN đọc `skills/code-review/SKILL.md` (kịch
bản 2 đọc thêm `references/reviewer.md`); gốc: kịch bản 1 đọc `dev-process/code-review-routing` +
superpowers `requesting-code-review`, kịch bản 2 đọc `requesting-code-review` + `code-reviewer.md`, kịch bản 3
đọc `receiving-code-review`.
