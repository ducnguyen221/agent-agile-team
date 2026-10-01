---
id: SPR-01-progress
doc: progress
title: Tra trạng thái đơn hàng bằng mã đơn
sprint: SPR-01
request: RQ-001
feature: FS-001
status: done
size: medium
risk: normal
risk_tags: []
review_round: 1
roles:
  analyst: [T1, agent-a]
  architect: [T1, agent-b]
  implementer: [T2, agent-e]
  qa: [T3, agent-f]
  business-reviewer: [T1, agent-c]
  tech-reviewer: [T1, agent-d]
created: 2026-01-15
updated: 2026-01-16
links:
  spec: SPEC.md
  plan: PLAN.md
  report: REPORT.md
---

# Tra trạng thái đơn hàng bằng mã đơn — Tiến độ (PROGRESS)

<!-- PROGRESS trả lời: đang ở đâu, vướng gì. Trạng thái sống trong file này, không sống trong ngữ cảnh phiên.
     Cập nhật sau MỖI việc. `status` trong frontmatter là trạng thái sống của cả sprint (công cụ index đọc nó). -->

> **Kết luận:** <!-- MỘT câu, viết lại mỗi lần cập nhật: xong bao nhiêu việc, vướng gì, vòng kiểm định thứ mấy. -->
> 2/2 việc Đạt; BR1 (thiếu quyền đọc) đã xử lý; vòng kiểm định 1 kết luận Đạt có điều kiện; sprint đã đóng.

## 1. Bảng trạng thái việc

<!-- Trạng thái: Chưa chạy · Đang làm · Đạt · Không đạt · Không áp dụng (kèm lý do) · bỏ.
     "Chưa chạy" và "Không áp dụng" KHÔNG BAO GIỜ tính là Đạt.
     Bằng chứng = file:dòng, hoặc lệnh + kết quả vừa chạy. Cột model ghi model thực tế đã giao. -->

| Việc | Vai · tier · model | Trạng thái | Bằng chứng |
|---|---|---|---|
| TK1 (hàm tra cứu đơn) | Implementer · T2 · model-x | Đạt | `pytest tests/test_orders.py` → 6 passed; coverage 92% |
| TK2 (màn hình tra cứu) | Implementer · T2 · model-x | Đạt | ảnh chụp kịch bản FR1.1, FR1.2 |

## 2. Nhật ký

<!-- CHỈ THÊM, KHÔNG SỬA dòng cũ. Mỗi dòng: **YYYY-MM-DD HH:MM +múi giờ** — ai làm gì, kết quả.
     Điều chỉnh nội bộ trong phạm vi đã duyệt ghi đúng khuôn:
     "Phán quyết: <quyết gì> — <vì sao> — <sai thì tốn gì>". Không hỏi người cho loại điều chỉnh này. -->

- **2026-01-15 09:00 +07** — Analyst nhận SPR-01 sau Cổng 1; giao TK1 (hàm tra cứu đơn) cho Implementer T2.
- **2026-01-15 09:40 +07** — TK1 Đạt. Phán quyết: cắt khoảng trắng đầu/cuối mã đơn trước khi tra — vì người
  dùng hay dán mã kèm khoảng trắng — sai thì tốn một lần sửa hàm và test.

## 3. Vướng mắc

<!-- BR chỉ mở cho 4 trường hợp phải dừng và hỏi người: (a) hành động không đảo ngược được, (b) chạm bảo mật
     hoặc secret, (c) tác động ra ngoài phạm vi đã giao, (d) PLAN hỏng — giả định sai làm đổi tiêu chí thành
     công. Hết hạn mức model của một tier cũng mở BR (không tự hạ tier). Không có thì ghi "Không có." -->

PROGRESS có 1 **blocker** (BR):

| Mã | Vướng mắc | Loại | Xử lý | Cần ai | Trạng thái |
|---|---|---|---|---|---|
| BR1 (thiếu quyền đọc) | Tài khoản kiểm thử không đọc được bảng đơn | (c) ngoài phạm vi | Chủ sản phẩm cấp quyền chỉ-đọc lúc 2026-01-15 11:00 | Chủ sản phẩm | đã xử lý |

## 4. Vòng kiểm định hiện tại

<!-- Vòng = một lần reviewer kiểm và trả kết quả. Khuyến nghị 3 vòng, không phải trần cứng; hết vòng 3 mà còn
     Chặn hoặc Phải sửa thì báo người: số vòng, phát hiện còn mở, đề xuất làm tiếp hay dừng & bàn giao.
     Reviewer là agent KHÁC người làm. Chi tiết RF ghi ở REPORT; ở đây chỉ đếm và trỏ. -->

*Vòng 1 — Business Reviewer (agent-c, T1) và Tech Reviewer (agent-d,
T1): Đạt có điều kiện; 0 Chặn, 0 Phải sửa, 2 Nên sửa, 0 Ghi chú; RF2 (thông báo khó hiểu) đã sửa ở TK2,
RF3 (truy vấn chưa có chỉ mục) để lại → CO1.*
