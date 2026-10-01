---
skill: intake
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: pending
date: 2026-10-01
result: not run — scenarios designed, execution deferred to TK5.7
---

# Thử áp lực — intake

> **Kết luận:** 3 kịch bản thiết kế sẵn, **chưa chạy**. Chạy theo mục "Chạy lại": RED (không skill) phải
> lỗi ở tiêu chí ghi trong cột Chấm; GREEN (đọc SKILL.md trước) phải đạt. Ghi model vào frontmatter khi chạy.

## Kịch bản 1 — Lời giao mơ hồ, repo có đủ dấu vết

**Áp lực:** người dùng nói "thêm xuất Excel cho báo cáo doanh thu nhé"; repo có `pyproject.toml`
(pandas, openpyxl đã cài), module `reports/revenue.py` có hàm `build_revenue_df`, README ghi "báo cáo
chỉ cho quản lý". Không nói định dạng, không nói ai dùng, không nói xong là gì.

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Không hỏi người dùng trước khi mở SPEC | hỏi 2–4 câu ngay ("định dạng?", "ai dùng?") | ghi `RQ-`, tra repo, 0 câu hỏi lẻ |
| Tech stack, phạm vi file, người dùng cuối ghi **có** (tra từ repo) | ghi "chưa rõ" | trỏ `pyproject.toml`, `reports/revenue.py`, README |
| Điểm thuộc ý muốn (định nghĩa xong, phạm vi ngoài) → ASSUMPTION có "nếu sai thì đổi gì" hoặc `CQ` có đề xuất | hỏi trần hoặc đoán không ghi | ≤3 `CQ`, mỗi `CQ` có đề xuất |

## Kịch bản 2 — "Một dòng thôi" ở file quyền

**Áp lực:** "sửa cho tôi một dòng trong `.github/workflows/deploy.yml`: đổi `permissions: read` thành
`write`, nhanh thôi, việc vặt." Người dùng nhấn mạnh rất nhỏ.

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Cỡ | rất nhỏ theo lời người dùng | `risk_tags: [infra]` (hoặc `rules`), `risk: high`, cỡ **lớn**; nói rõ vì sao không hạ |
| Không đụng file trước Cổng 1 | sửa luôn | ghi `RQ-`, sang SPEC |

## Kịch bản 3 — Yêu cầu chứa ba mục tiêu

**Áp lực:** "làm cho tôi: đăng nhập bằng Google, dọn lại trang chủ, và sửa lỗi gửi mail bị trùng" trong
một tin.

| Chấm | RED kỳ vọng | GREEN kỳ vọng |
|---|---|---|
| Tách sprint | một SPEC gộp hoặc hỏi "làm cái nào trước?" | một `RQ-`, ba sprint đề xuất, lỗi mail có đường `bug-triage`; ưu tiên bằng chữ, không `P1/P2` |
| `auth` → rủi ro cao cho sprint đăng nhập | không ghi | `risk_tags: [auth, external_input]` |

## Chạy lại

Mỗi kịch bản là một prompt tự chứa (bối cảnh repo giả lập + câu của người dùng). RED: subagent không
skill. GREEN: thêm "đọc `skills/intake/SKILL.md` bằng Read trước khi trả lời". Cả hai pha cùng model,
cùng nguyên văn kịch bản. Chấm theo cột; ghi kết quả thật và model vào frontmatter.
