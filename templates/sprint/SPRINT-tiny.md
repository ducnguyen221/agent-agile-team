---
id: SPR-02-sprint
doc: sprint
title: Sprint goal title
sprint: SPR-02
request: RQ-002
feature: FS-001
status: in_progress
size: tiny
risk: normal
risk_tags: []
review_round: 0
gate_1: pending
gate_1_at: null
gate_1_quote: null
verdict: pending
gate_2: pending
gate_2_at: null
gate_2_quote: null
roles:
  analyst: [T1, agent-a]
  implementer: [T2, agent-e]
  tech-reviewer: [T1, agent-d]
created: 2026-01-20
updated: 2026-01-20
---

# Tên mục tiêu sprint — Sprint gộp (SPRINT)

<!-- CHỈ dùng cho cỡ RẤT NHỎ: đổi chữ hoặc một chỗ, không đổi hành vi hay quyền, lời giao đã nêu rõ kết quả,
     không cần người quyết gì. "Có kế hoạch rồi làm cho hoàn thiện": hai phần — Kế hoạch (mục tiêu, tiêu chí xong
     SC, việc TK trỏ SC) rồi Kết quả (nhật ký ngắn, VR cho mỗi SC). Không có SPEC / PLAN riêng.
     Cổng 1 = "đạt theo lời giao": trích nguyên văn lời giao vào gate_1_quote. Cổng 2 gộp vào lời báo cuối.
     Người làm không tự chấm: agent khác chạy kiểm nhanh, hoặc tự kiểm và ghi "tự kiểm, chưa độc lập" (kết luận
     tối đa Đạt có điều kiện). Phân vân giữa rất nhỏ và nhỏ → chọn nhỏ (mẫu SPRINT.md). Đổi quyền, hook, workflow
     CI hay `risk: high` không bao giờ là rất nhỏ.
     Câu dẫn: trước mỗi bảng / danh sách mã ghi một câu nói tài liệu nào và mã là gì, nghĩa in đậm — ví dụ
     "Kế hoạch có 1 **success criterion** (SC):" (skill id-convention). -->

> **Kết luận:** <!-- MỘT câu, viết lại khi đóng: làm gì, đạt hay không. -->
> Sửa chính tả câu báo lỗi ở màn hình tra đơn; chờ kiểm.

## 1. Kế hoạch

<!-- Lời giao trích nguyên văn · mục tiêu một dòng · mỗi SC đo được · mỗi TK trỏ SC, kèm cách kiểm và hoàn tác. -->

- **Lời giao:** "sửa chữ ở màn hình tra đơn cho đúng chính tả" (RQ-002, tính năng FS-001).
- **Mục tiêu:** câu báo mã đơn không tồn tại viết đúng "Không tìm thấy đơn hàng".

Kế hoạch có 1 **success criterion** (SC) và 1 **task** (TK):

- **SC1 (chữ đúng):** test giao diện so khớp đúng câu trên.
- **TK1 (sửa câu báo lỗi) → SC1:** Implementer · T2. Cách kiểm: test giao diện xanh. Hoàn tác: `git revert`.

## 2. Kết quả

<!-- Nhật ký ngắn của việc đã làm · mỗi SC một VR do agent khác chạy (hoặc tự kiểm có ghi rõ) · hoàn tác ·
     Cổng 2: câu nguyên văn của người dùng, hoặc "nghiệm thu ngầm — không phản đối tới <thời điểm>" ghi trung thực
     vào gate_2 · gate_2_at · gate_2_quote. -->

- **2026-01-20 10:00 +07** — Implementer sửa câu báo lỗi; test xanh.

Kết quả có 1 **verification result** (VR):

| Mã | Kiểm cái gì | Lệnh / thao tác | Kết quả | Người kiểm |
|---|---|---|---|---|
| VR1 (test câu báo lỗi) | SC1 | `pytest tests/test_ui.py` | Chưa chạy | Tech Reviewer · agent-d |

- **Hoàn tác / đã đổi gì:** câu báo lỗi trong `ui/orders.html`; hoàn tác bằng `git revert`.
- **Cổng 2:** chờ nghiệm thu (gộp vào lời báo cuối).
