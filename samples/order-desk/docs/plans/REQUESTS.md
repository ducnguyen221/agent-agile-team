---
id: REQUESTS
doc: requests
title: Request ledger
next_id: RQ-006
updated: 2026-01-23
---

# Sổ yêu cầu (REQUESTS)

<!-- Một dòng mỗi yêu cầu chủ sản phẩm giao, theo timeline, MỚI NHẤT Ở TRÊN. Analyst ghi ngay khi tiếp nhận.
     Mã RQ-NNN tăng dần, có gạch nối, KHÔNG tái dùng; lấy mã từ `next_id` rồi tăng `next_id` lên một.
     Trạng thái: mới · đang làm · xong · bỏ. Yêu cầu nhiều mục tiêu → nhiều sprint, ghi đủ ở cột Sprint. -->

> Agent phiên mới: đọc khối "Đang mở" rồi đi thẳng tới thư mục sprint; không quét cả thư mục.

## Đang mở

<!-- agile:open:start -->
<!-- Khối này do công cụ `index` ghi lại — đừng sửa tay. -->
| Mã | Ngày | Tóm tắt | Trạng thái | Sprint |
|---|---|---|---|---|
| RQ-004 | 2026-01-22 | Tra đơn bỏ khoảng trắng thừa quanh mã đơn | đang làm | SPR-03 |
| RQ-003 | 2026-01-20 | Câu báo không tìm thấy sai chính tả | đang làm | SPR-02 |
| RQ-002 | 2026-01-16 | Thêm chỉ mục cho cột mã đơn (từ SPR-01/CO1) | mới | — |
<!-- agile:open:end -->

## Timeline

Sổ REQUESTS ghi mỗi dòng một **request** (RQ), mới nhất ở trên:

| Mã | Ngày | Tóm tắt | Trạng thái | Tính năng | Sprint |
|---|---|---|---|---|---|
| RQ-005 | 2026-01-23 | Đổi chữ nút Gửi thành Gửi đơn | xong | FS-001 | SPR-04 |
| RQ-004 | 2026-01-22 | Tra đơn bỏ khoảng trắng thừa quanh mã đơn | đang làm | FS-001 | SPR-03 |
| RQ-003 | 2026-01-20 | Câu báo không tìm thấy sai chính tả | đang làm | FS-001 | SPR-02 |
| RQ-002 | 2026-01-16 | Thêm chỉ mục cho cột mã đơn (từ SPR-01/CO1) | mới | FS-001 | — |
| RQ-001 | 2026-01-15 | Tra trạng thái đơn hàng bằng mã đơn | xong | FS-001 | SPR-01 |
<!-- Ví dụ một dòng (xoá comment khi ghi dòng thật đầu tiên):
| RQ-001 | 2026-01-15 | Tra trạng thái đơn hàng bằng mã đơn | đang làm | FS-001 | SPR-01 |
-->
