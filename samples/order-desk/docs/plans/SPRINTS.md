---
id: SPRINTS
doc: sprints
title: Sprint ledger
next_id: SPR-05
updated: 2026-01-23
---

# Sổ sprint (SPRINTS)

<!-- Một dòng mỗi sprint, theo timeline, MỚI NHẤT Ở TRÊN. Sprint = một mục tiêu, dài ngắn tùy mục tiêu.
     Mã SPR-NN tăng dần, có gạch nối, KHÔNG tái dùng; lấy mã từ `next_id`.
     Cột Đóng để trống khi sprint còn mở. Kết luận = kết luận Cổng 2: Đạt / Đạt có điều kiện / Không đạt / bỏ. -->

> Agent phiên mới: đọc khối "Đang mở" rồi mở thẳng PROGRESS của sprint; không quét cả thư mục.

## Đang mở

<!-- agile:open:start -->
<!-- Khối này do công cụ `index` ghi lại — đừng sửa tay. -->
| Mã | Mở | Mục tiêu | Trạng thái | Vòng | Thư mục |
|---|---|---|---|---|---|
| SPR-03 | 2026-01-22 | Tra đơn bỏ khoảng trắng thừa quanh mã đơn | đang kiểm định | 1 | [2026-01-22-trim-order-code](2026-01-22-trim-order-code/) |
| SPR-02 | 2026-01-20 | Sửa chính tả câu báo không tìm thấy | đang kiểm định | 1 | [2026-01-20-fix-not-found-text](2026-01-20-fix-not-found-text/) |
<!-- agile:open:end -->

## Timeline

Sổ SPRINTS ghi mỗi dòng một **sprint** (SPR), mới nhất ở trên:

| Mã | Mở | Đóng | Mục tiêu | Kết luận | Thư mục |
|---|---|---|---|---|---|
| SPR-04 | 2026-01-23 | 2026-01-23 | Đổi chữ nút Gửi thành Gửi đơn ở form tạo đơn | Đạt | [2026-01-23-rename-submit-button](2026-01-23-rename-submit-button/) |
| SPR-03 | 2026-01-22 |  | Tra đơn bỏ khoảng trắng thừa quanh mã đơn |  | [2026-01-22-trim-order-code](2026-01-22-trim-order-code/) |
| SPR-02 | 2026-01-20 |  | Sửa chính tả câu báo không tìm thấy |  | [2026-01-20-fix-not-found-text](2026-01-20-fix-not-found-text/) |
| SPR-01 | 2026-01-15 | 2026-01-16 | Tra trạng thái đơn hàng bằng mã đơn | Đạt có điều kiện | [2026-01-15-order-lookup](2026-01-15-order-lookup/) |
