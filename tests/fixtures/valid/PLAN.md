---
id: SPR-03-plan
doc: plan
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
  architect: [T1, agent-b]
  tech-reviewer: [T1, agent-d]
created: 2026-02-01
updated: 2026-02-01
links:
  spec: SPEC.md
  progress: PROGRESS.md
  report: REPORT.md
---

# Xuất danh sách đơn — Kế hoạch (PLAN)

> **Kết luận:** một việc, không có quyết định nào cần người ngoài Cổng 1.

## Mục tiêu

- **Mục tiêu sprint:** Xuất danh sách đơn ra CSV đủ cột.
- **Kết quả mong muốn / xong khi:** SC1 (xuất đủ cột) của SPEC đạt.
- **Rủi ro cần chú ý:** tên khách có dấu phẩy làm lệch cột — RK1 (dấu phẩy trong tên).

## Kiến trúc

- Thêm hàm xuất ở lớp dịch vụ.

## Ràng buộc chung

- Coverage dòng ≥80%.

## Trọng tâm review

1. Ký tự đặc biệt trong tên khách.

## Việc

### TK1 — Hàm xuất CSV (→ FR1.1, SC1)

- **Vai:** Implementer · T2.
- **TK1.1 (viết test trước):** kế thừa phần trỏ của TK1 (hàm xuất CSV).

## Rủi ro
PLAN có 1 **risk** (RK):
| Mã | Rủi ro | Mức | Giảm thiểu |
|---|---|---|---|
| RK1 (dấu phẩy trong tên) | Tên khách có dấu phẩy làm lệch cột | Nên sửa | Dùng thư viện CSV chuẩn |

## Quyết định cần người

Không có.

## Ước lượng

| Việc | Phiên agent | Lần hỏi người |
|---|---|---|
| TK1 (hàm xuất CSV) | 1 | 0 |
