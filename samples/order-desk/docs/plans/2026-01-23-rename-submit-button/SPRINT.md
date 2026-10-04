---
id: SPR-04-sprint
doc: sprint
title: Đổi chữ nút Gửi thành Gửi đơn ở form tạo đơn
sprint: SPR-04
request: RQ-005
feature: FS-001
status: done
size: tiny
risk: normal
risk_tags: []
review_round: 0
gate_1: approved
gate_1_at: 2026-01-23 09:00 +07
gate_1_quote: "đạt theo lời giao: đổi chữ nút Gửi thành Gửi đơn ở form tạo đơn, chỉ đổi chữ"
verdict: pass
gate_2: pass
gate_2_at: 2026-01-23 15:00 +07
gate_2_quote: "nghiệm thu ngầm — không phản đối tới 2026-01-23 15:00 +07"
roles:
  analyst: [T1, agent-a]
  implementer: [T2, agent-e]
  tech-reviewer: [T1, agent-d]
created: 2026-01-23
updated: 2026-01-23
---

# Đổi chữ nút Gửi thành Gửi đơn ở form tạo đơn — Sprint gộp (SPRINT)

<!-- Cỡ RẤT NHỎ: hai phần Kế hoạch / Kết quả. Cổng 1 = "đạt theo lời giao"; Cổng 2 gộp vào lời báo cuối, nghiệm thu ngầm
     ghi trung thực. Mẫu: templates/sprint/SPRINT-tiny.md. -->

> **Kết luận:** nút gửi ở form tạo đơn đã hiện "Gửi đơn"; test giao diện xanh, agent khác kiểm xong; Đạt.

## 1. Kế hoạch

<!-- Lời giao trích nguyên văn · mục tiêu một dòng · mỗi SC đo được · mỗi TK trỏ SC, kèm cách kiểm và hoàn tác. -->

- **Lời giao:** "đổi chữ nút Gửi thành Gửi đơn ở form tạo đơn, chỉ đổi chữ" (RQ-005, tính năng FS-001).
- **Mục tiêu:** nút gửi của form tạo đơn hiện đúng chữ "Gửi đơn".

Kế hoạch có 1 **success criterion** (SC) và 1 **task** (TK):

- **SC1 (chữ đúng):** test giao diện so khớp chữ nút gửi bằng "Gửi đơn".
- **TK1 (đổi chữ nút) → SC1:** Implementer · T2. Cách kiểm: test giao diện xanh. Hoàn tác: `git revert`.

## 2. Kết quả

<!-- Nhật ký ngắn của việc đã làm · mỗi SC một VR do agent khác chạy · hoàn tác · Cổng 2. -->

- **2026-01-23 10:00 +07** — Implementer đổi chữ nút trong `ui/create_order.html` và chữ kỳ vọng trong test; test xanh.
- **2026-01-23 10:20 +07** — Tech Reviewer (agent khác) chạy lại test và đọc diff: chỉ đổi chữ nhãn nút.

Kết quả có 1 **verification result** (VR):

| Mã | Kiểm cái gì | Lệnh / thao tác | Kết quả | Người kiểm |
|---|---|---|---|---|
| VR1 (test chữ nút gửi) | SC1 | `pytest tests/test_ui.py` → 1 passed | Đạt | Tech Reviewer · agent-d |

- **Hoàn tác / đã đổi gì:** chữ nút trong `ui/create_order.html`; hoàn tác bằng `git revert`.
- **Cổng 2:** gộp vào lời báo cuối; nghiệm thu ngầm — không phản đối tới 2026-01-23 15:00 +07.
