---
id: SPR-01-progress
doc: progress
title: Sprint goal title
sprint: SPR-01
request: RQ-001
feature: FS-001
status: in_progress
size: medium
risk: normal
risk_tags: []
review_round: 0
roles:
  analyst: [T1, agent-a]
  architect: [T1, agent-b]
  implementer: [T2, agent-e]
  qa: [T3, agent-f]
  business-reviewer: [T1, agent-c]
  tech-reviewer: [T1, agent-d]
created: 2026-01-15
updated: 2026-01-15
links:
  spec: SPEC.md
  plan: PLAN.md
  report: REPORT.md
---

# Tên mục tiêu sprint — Tiến độ (PROGRESS)

<!-- PROGRESS trả lời: đang ở đâu, vướng gì. Trạng thái sống trong file này, không sống trong ngữ cảnh phiên.
     Cập nhật sau MỖI việc. `status` trong frontmatter là trạng thái sống của cả sprint (công cụ index đọc nó). -->

> **Kết luận:** <!-- MỘT câu, viết lại mỗi lần cập nhật: xong bao nhiêu việc, vướng gì, vòng kiểm định thứ mấy. -->
> 1/2 việc Đạt; chưa có vướng mắc; chưa vào vòng kiểm định.

## 1. Bảng trạng thái việc

<!-- Trạng thái: Chưa chạy · Đang làm · Đạt · Không đạt · Không áp dụng (kèm lý do) · bỏ.
     "Chưa chạy" và "Không áp dụng" KHÔNG BAO GIỜ tính là Đạt.
     Bằng chứng = file:dòng, hoặc lệnh + kết quả vừa chạy. Cột model ghi model thực tế đã giao. -->

| Việc | Vai · tier · model | Trạng thái | Bằng chứng |
|---|---|---|---|
| TK1 (hàm tra cứu đơn) | Implementer · T2 · model-x | Đạt | `pytest tests/test_orders.py` → 6 passed; coverage 92% |
| TK2 (màn hình tra cứu) | Implementer · T2 · model-x | Chưa chạy | — |

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

| Mã | Vướng mắc | Loại | Xử lý | Cần ai | Trạng thái |
|---|---|---|---|---|---|
| BR1 (cần quyền hệ thống ngoài) | Kiểm `SC2` cần tài khoản đọc trên hệ thống thanh toán của bên thứ ba, ngoài phạm vi dự án; agent không được tự xin | (c) ngoài phạm vi | Chờ chủ sản phẩm cấp tài khoản chỉ-đọc; `VR` của `SC2` ghi Chưa chạy | Chủ sản phẩm | mở |

## 4. Vòng kiểm định hiện tại

<!-- Vòng = một lần reviewer kiểm và trả kết quả. Khuyến nghị 3 vòng, không phải trần cứng; hết vòng 3 mà còn
     Chặn hoặc Phải sửa thì báo người: số vòng, phát hiện còn mở, đề xuất làm tiếp hay dừng & bàn giao.
     Reviewer là agent KHÁC người làm. Chi tiết RF ghi ở REPORT; ở đây chỉ đếm và trỏ. -->

Vòng 0 — chưa kiểm. Mẫu khi đã kiểm: *Vòng 1 — Business Reviewer (agent-c, T1) và Tech Reviewer (agent-d,
T1): Đạt có điều kiện; 0 Chặn, 0 Phải sửa, 2 Nên sửa, 0 Ghi chú; RF1 (thông báo khó hiểu) đã sửa ở TK2,
RF2 (truy vấn chưa có chỉ mục) để lại → CO1.*
