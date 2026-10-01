---
id: SPR-03-spec
doc: spec
title: Fixture sprint
sprint: SPR-03
request: RQ-007
feature: FS-002
status: approved
size: medium
risk: normal
risk_tags: []
gate_1: approved
gate_1_at: 2026-02-01 09:00 +07
gate_1_quote: "duyệt"
roles:
  analyst: [T1, agent-a]
  business-reviewer: [T1, agent-c]
created: 2026-02-01
updated: 2026-02-01
links:
  plan: PLAN.md
  progress: PROGRESS.md
  report: REPORT.md
---

# Xuất danh sách đơn — Đặc tả (SPEC)

> **Kết luận:** sprint SPR-03 cho phép xuất danh sách đơn ra CSV; xong khi SC1 (xuất đủ cột) đạt.

## 1. Bối cảnh

- Yêu cầu gốc: RQ-007 (xuất danh sách đơn). Tính năng: FS-002 (xuất dữ liệu).

## 2. Câu chuyện người dùng

| Mã | Câu chuyện | Ưu tiên |
|---|---|---|
| US1 (xuất nhanh) | Là kế toán, tôi xuất danh sách đơn ra CSV, để đối soát | Bắt buộc |

## 3. Yêu cầu chức năng

### FR1 — Xuất CSV (→ US1)

- **FR1.1 (đủ cột):** KHI người dùng bấm xuất THÌ file có đủ cột mã, ngày, trạng thái.

## 4. Tiêu chí thành công

| Mã | Tiêu chí | Cách đo |
|---|---|---|
| SC1 (xuất đủ cột) | File CSV có đủ ba cột | Test tự động của FR1 xanh |

## 5. Ngoài phạm vi

- Xuất Excel. Ví dụ mã bị cấm trong dấu code: `P1`, `S2` — không bị bắt.

## 6. Câu hỏi cần làm rõ

Không có.

## 7. Truy vết

| Câu chuyện | Yêu cầu | Tiêu chí |
|---|---|---|
| US1 (xuất nhanh) | FR1 | SC1 |
