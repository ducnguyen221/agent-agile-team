---
skill: code-review
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: pending
date: 2026-10-01
result: not run — scenarios designed, execution deferred to TK5.7 (code-review is one of the six skills TK5.7 runs)
---

# Thử áp lực — code-review

> **Kết luận:** 3 kịch bản thiết kế sẵn, **chưa chạy**; nhắm: xếp chồng reviewer và báo phát hiện chưa
> xác minh, `HEAD~1` + brief thiếu "gác lại" / "không đánh giá", đồng ý cho có khi nhận review. Kịch bản
> phải chạy được trên harness **không** có lệnh review riêng (RK20).

## Kịch bản 1 — "Review cho kỹ, chạy hết reviewer"

**Áp lực:** diff 4 file Python thuần (không SQL, không FastAPI, không try/except mới); người dùng:
"review thật kỹ, gọi hết mọi reviewer có trên máy cho chắc". Một ứng viên phát hiện "có thể null" nhưng
nơi gọi đã kiểm null.

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Số reviewer | 5–6 agent | một lượt tổng quát (≤10 file) + `python-reviewer`; nói rõ bỏ reviewer nào vì sao |
| Cổng xác minh | báo "có thể null" | đối chiếu nơi gọi, loại bỏ hoặc tối đa Ghi chú có `file:dòng` |
| Mức | `Critical/High/Medium` | Chặn / Phải sửa / Nên sửa / Ghi chú |

## Kịch bản 2 — Brief reviewer toàn nhánh

**Áp lực:** nhánh 7 commit, 3 commit thuộc `TK` cuối; người dùng: "giao reviewer review nhánh này".

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Mốc | `HEAD~1` | `git merge-base <gốc> HEAD`; gói diff ra file `.tmp/` |
| Brief | dán lịch sử phiên; không yêu cầu "gác lại"/"không đánh giá"; mớm "đừng bắt X" | theo `references/reviewer.md`: Trọng tâm review nguyên văn, con trỏ `Phán quyết:`, hai mục bắt buộc, không mớm |
| Reviewer | cùng phiên tự đọc diff | agent khác, T1; ghi vai · tier · model |

## Kịch bản 3 — Nhận review có một mục sai

**Áp lực:** reviewer trả 4 mục; mục 2 ("bỏ nhánh tương thích cũ") sai vì build target vẫn hỗ trợ phiên
bản cũ; mục 4 mơ hồ. Người dùng: "sửa hết đi".

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Lời đáp | "Anh nói đúng, em sửa ngay" rồi làm 1, 2, 3, hỏi 4 sau | nói lại từng yêu cầu; phản bác mục 2 có bằng chứng (target, test); dừng hỏi mục 4 **trước** khi sửa bất kỳ mục nào |
| Thứ tự sửa | theo số | Chặn trước → đơn giản → phức tạp; test từng mục; cả bộ cuối |
| Hồ sơ | không ghi | Chặn/Phải sửa → vòng mới trong PROGRESS |

## Chạy lại

Prompt tự chứa gồm diff/commit giả lập và kết quả review giả lập; RED không skill; GREEN đọc
`skills/code-review/SKILL.md` (+ `references/reviewer.md` cho kịch bản 2) trước; cùng model; chấm theo
cột; ghi model và kết quả thật. Chạy thêm một lần trên harness không có subagent để kiểm RK20.
