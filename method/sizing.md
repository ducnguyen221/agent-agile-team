---
title: Sizing — four sizes, risk only raises
type: method
status: active
updated: 2026-10-01
---

# Cỡ việc: bốn mức, rủi ro chỉ nâng

> **Kết luận:** cỡ việc quyết **độ dày tài liệu và độ sâu kiểm định**, không quyết thời gian. Chọn cỡ
> theo thứ tự *phạm vi được giao → rủi ro → cỡ → tài liệu/cổng áp dụng*. Rủi ro chỉ được **nâng** cỡ;
> diff nhỏ không bao giờ là lý do hạ cỡ.

## 1. Bốn cỡ

| Cỡ | Dấu hiệu | Tài liệu | Kiểm định | Cổng |
|---|---|---|---|---|
| **Rất nhỏ** | đổi chữ, một dòng, không đổi hành vi hay quyền | một file `SPRINT.md` đủ 4 phần | tự kiểm + ghi "chưa độc lập", hoặc agent khác chạy nhanh | Cổng 1 "đạt theo lời giao", Cổng 2 gộp vào lời báo cuối ([process.md](process.md) mục 9) |
| **Nhỏ** | sửa cục bộ một luồng có sẵn, hành vi không đổi với người dùng khác | 4 tài liệu, mỗi phần ngắn | Business Reviewer **hoặc** Tech Reviewer, một lượt | đủ 2 cổng |
| **Vừa** | tính năng, hành vi hay luồng mới | 4 tài liệu đầy đủ; Tech Reviewer review PLAN trước Cổng 1 | cả hai reviewer | đủ 2 cổng |
| **Lớn** | nhiều phần, đổi hợp đồng / giao diện / schema, hoặc **rủi ro cao** (mục 2) | 4 tài liệu + mục "Đổi hợp đồng / giao diện" trong SPEC + ADR cho quyết định kiến trúc + kế hoạch hoàn tác | cả hai reviewer + thẻ chuyên đề theo rủi ro; diễn tập migration nếu có dữ liệu | đủ 2 cổng; Cổng 2 có kiểm kế hoạch hoàn tác |

## 2. Rủi ro nâng cỡ

KHI việc chạm **một** trong các vùng sau THÌ ghi nhãn vào `risk_tags`, `risk: high`, cỡ tối thiểu là
**lớn** và Tech Reviewer kéo thẻ chuyên đề tương ứng ([roles/verifier/specialists/](../roles/verifier/specialists/)):

| Vùng | `risk_tags` | Chuyên đề kéo |
|---|---|---|
| secret, khoá, token, cấu hình xác thực | `secret` | security |
| xác thực, phân quyền, phiên | `auth` | security |
| đầu vào từ ngoài (form, API công khai, file tải lên, webhook) | `external_input` | security (+ backend) |
| API công khai, hợp đồng giữa dịch vụ | `public_api` | backend |
| hạ tầng, deploy, hook, workflow CI, quyền chạy | `infra` | security (+ backend) |
| migration dữ liệu, đổi schema, backfill, xoá dữ liệu | `data_migration` | data |
| file luật của dự án hay của môi trường (quy tắc agent, cấu hình harness) | `rules` | security |

Cấu hình đổi quyền, hook hay workflow thực thi **không được** xếp rất nhỏ dù diff một dòng.

## 3. Sprint = một mục tiêu

- Một sprint phục vụ đúng một mục tiêu đã "định hình": biết làm gì, biết thế nào là xong, biết giới hạn
  công sức. Dài ngắn tuỳ mục tiêu — một phiên, một tính năng, một đợt chỉnh đều là sprint.
- Yêu cầu chứa nhiều mục tiêu → tách thành nhiều sprint, cùng trỏ về một `RQ-`.
- Giới hạn là **công sức**, không phải lịch: ước lượng trong PLAN ghi bằng số việc và số vòng dự kiến;
  vượt ước lượng đáng kể (gấp đôi) là tín hiệu PLAN hỏng (điều kiện dừng (d)) hoặc cần tách sprint.
- Không dùng tuần, story point, burndown.

## 4. Ghi vào tài liệu

Frontmatter mọi tài liệu sprint có `size: tiny | small | medium | large`, `risk: normal | high` và
`risk_tags` (rỗng khi `normal`). `risk: high` buộc `size: large`.
Cỡ ghi ở Bước 1 (Tiếp nhận), có thể **nâng** ở bất kỳ bước nào khi lộ rủi ro mới (ghi `Phán quyết:` kèm lý
do); **hạ** cỡ chỉ được ở Cổng 1 do người dùng quyết.
