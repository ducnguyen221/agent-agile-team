---
id: SPR-01-plan
doc: plan
title: Tra trạng thái đơn hàng bằng mã đơn
sprint: SPR-01
request: RQ-001
feature: FS-001
status: approved
size: medium
risk: normal
risk_tags: []
gate_1: approved
gate_1_at: 2026-01-15 08:50 +07
gate_1_quote: "duyệt, làm đi"
roles:
  architect: [T1, agent-b]
  tech-reviewer: [T1, agent-d]
created: 2026-01-15
updated: 2026-01-15
links:
  spec: SPEC.md
  progress: PROGRESS.md
  report: REPORT.md
---

# Tra trạng thái đơn hàng bằng mã đơn — Kế hoạch (PLAN)

<!-- PLAN trả lời: làm thế nào, ai làm, kiểm ra sao. Mọi TK trỏ ít nhất một FR hoặc SC của SPEC.
     Nhắc chéo trong cùng sprint: `TK2 → FR1.1`; sang tài liệu khác: `FS-001/FR1.1`. -->

> **Kết luận:** <!-- MỘT câu: cách làm chính + số việc + điều cần người quyết (nếu có). -->
> Thêm một điểm tra cứu đơn hàng chỉ-đọc qua 2 việc; không có quyết định nào cần người ngoài Cổng 1.

## Mục tiêu

<!-- Nhắc lại mục tiêu sprint bằng một câu và trỏ SPEC. -->

Đạt SC1 (tra nhanh) của SPEC bằng một điểm tra cứu chỉ-đọc.

## Kiến trúc

<!-- Thành phần nào đổi, luồng dữ liệu, hợp đồng giữa các phần. Quyết định kiến trúc lâu dài → ADR riêng
     theo đường dẫn ADR của cấu hình dự án, ở đây chỉ trỏ tới. -->

- Thêm hàm tra cứu ở lớp dịch vụ; giao diện gọi hàm đó; không đổi lược đồ dữ liệu.

## Ràng buộc chung

<!-- Luật áp cho MỌI việc trong plan: quyết định đã chốt, giới hạn kỹ thuật, điều cấm. Chép nguyên, không
     diễn giải lại. Implementer đọc mục này trước mọi TK. -->

- Chỉ đọc dữ liệu đơn; không thêm thao tác ghi.
- Coverage dòng ≥80% cho code mới và code được sửa (hoặc ngưỡng của cấu hình dự án).

## Trọng tâm review

<!-- TỐI ĐA 5 điểm dễ hỏng mà chưa việc nào kiểm trực tiếp — reviewer soi kỹ nhất ở đây. -->

1. **Lộ dữ liệu khi mã sai:** thông báo lỗi không được tiết lộ đơn nào tồn tại.

## Việc

<!-- Mỗi TK đủ 7 dòng: Vai (+ tier) · Đầu vào/ra · Giao diện · Cách kiểm · Cổng · Hoàn tác, và tiêu đề trỏ FR/SC.
     Việc con viết `TK1.1`, kế thừa phần trỏ của việc cha. Không đánh số lại; việc bỏ giữ mã, ghi trạng thái `bỏ`. -->

### TK1 — Hàm tra cứu đơn (→ FR1.1, FR1.2)

- **Vai:** Implementer · T2 thực thi; QA · T3 vặt & kiểm thử chạy test.
- **Đầu vào:** SPEC mục 3. **Đầu ra:** hàm tra cứu + test.
- **Giao diện (interfaces):** `find_order(code: str) -> OrderStatus | None`; trả `None` khi không tìm thấy.
- **Cách kiểm:** `pytest tests/test_orders.py` xanh; coverage dòng ≥80%.
- **Cổng:** nội bộ.
- **Hoàn tác:** `git revert` commit của việc.

### TK2 — Màn hình tra cứu (→ FR1.1, SC1)

- **Vai:** Implementer · T2 thực thi.
- **Đầu vào:** TK1 (hàm tra cứu đơn). **Đầu ra:** màn hình + test giao diện.
- **Giao diện (interfaces):** ô nhập mã đơn → gọi `find_order` → hiện trạng thái hoặc "không tìm thấy".
- **Cách kiểm:** kịch bản FR1.1, FR1.2 chạy trên trình duyệt; ảnh chụp làm bằng chứng.
- **Cổng:** nội bộ.
- **Hoàn tác:** `git revert`.

## Rủi ro

<!-- Mức theo thang chung: Chặn / Phải sửa / Nên sửa / Ghi chú. Rủi ro mức Chặn hoặc Phải sửa phải nêu ở Cổng 1. -->

| Mã | Rủi ro | Mức | Giảm thiểu |
|---|---|---|---|
| RK1 (tra hụt do hoa thường) | Dữ liệu cũ lẫn mã đơn chữ hoa và chữ thường nên tra hụt | Nên sửa | Chuẩn hoá mã về chữ hoa trước khi tra |

## Quyết định cần người

<!-- Chỉ những điểm làm đổi đáng kể kết quả. Mỗi DN có lựa chọn, khuyến nghị kèm lý do. Không có thì ghi "Không có." -->

| Mã | Câu hỏi | Lựa chọn | Khuyến nghị | Trạng thái |
|---|---|---|---|---|
| DN1 (chỉ mục mã đơn) | Thêm chỉ mục cho cột mã đơn ngay sprint này? | (a) có · (b) để sprint sau | (b) — bảng còn nhỏ, chưa cần | đã chốt (b) |

## Ước lượng

<!-- Đơn vị: phiên agent (một lượt làm liên tục tới khi compact hoặc bàn giao) và số lần cần hỏi người. -->

| Việc | Phiên agent | Lần hỏi người |
|---|---|---|
| TK1 (hàm tra cứu đơn) | 1 | 0 |
| TK2 (màn hình tra cứu) | 1 | 0 |
