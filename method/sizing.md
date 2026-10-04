---
title: Sizing — four sizes, risk only raises
type: method
status: active
updated: 2026-10-04
---

# Cỡ việc: bốn mức, rủi ro chỉ nâng

> **Kết luận:** cỡ việc quyết **độ dày tài liệu và độ sâu kiểm định**, không quyết thời gian. Chọn cỡ
> theo thứ tự *phạm vi được giao → rủi ro → cỡ → tài liệu/cổng áp dụng*. Rủi ro chỉ được **nâng** cỡ;
> diff nhỏ không bao giờ là lý do hạ cỡ.

## 1. Bốn cỡ

| Cỡ | Dấu hiệu đo được | Tài liệu | Kiểm định | Cổng |
|---|---|---|---|---|
| **Rất nhỏ** | đổi chữ hoặc một chỗ; không đổi hành vi hay quyền; lời giao đã nêu rõ kết quả; không cần người quyết gì | **một** `SPRINT.md` hai phần: "Kế hoạch" (mục tiêu, tiêu chí xong `SC`, việc `TK` trỏ `SC`) rồi "Kết quả" (nhật ký ngắn, `VR` cho mỗi `SC`) — "có kế hoạch rồi làm cho hoàn thiện", không SPEC / PLAN riêng | tự kiểm ghi "chưa độc lập" (kết luận tối đa Đạt có điều kiện), hoặc agent khác chạy kiểm nhanh | Cổng 1 "đạt theo lời giao" + trích lời giao; Cổng 2 gộp vào lời báo cuối ([process.md](process.md) mục 9) |
| **Nhỏ** | sửa cục bộ một luồng có sẵn; một `FR`; không đổi hợp đồng / giao diện / schema; không có quyết định kiến trúc | **một** `SPRINT.md` đủ bốn phần SPEC · PLAN · PROGRESS · REPORT, mỗi phần ngắn | **một** reviewer (agent khác người làm) kiểm cả nghiệp vụ lẫn kỹ thuật | Cổng 1 thật (trình ngắn), Cổng 2 thật |
| **Vừa** | tính năng, hành vi hay luồng mới; hoặc nhiều hơn một `FR` | 4 file đầy đủ; Tech Reviewer review PLAN trước Cổng 1 | cả Business Reviewer **và** Tech Reviewer | đủ 2 cổng |
| **Lớn** | nhiều phần, đổi hợp đồng / giao diện / schema, hoặc **rủi ro cao** (mục 2) | 4 file + mục "Đổi hợp đồng / giao diện" trong SPEC + ADR cho quyết định kiến trúc + kế hoạch hoàn tác | cả hai reviewer + thẻ chuyên đề theo rủi ro; diễn tập migration nếu có dữ liệu | đủ 2 cổng; Cổng 2 có kiểm kế hoạch hoàn tác |

**Luật đi kèm bảng:**

- **Phân vân giữa hai bậc → chọn bậc nặng hơn.** Nghi có đổi hành vi hay hợp đồng thì không phải rất nhỏ; nghi
  hơn một luồng thì không phải nhỏ.
- **Rủi ro chỉ nâng cỡ** (mục 2): `risk: high` luôn là lớn. Diff nhỏ không bao giờ là lý do hạ cỡ.
- **Hạ cỡ chỉ ở Cổng 1, do người dùng quyết** (mục 4).
- **Cấu hình quyền, hook hay workflow CI không bao giờ là rất nhỏ**, dù diff một dòng (mục 2).
- **Hình tài liệu khớp cỡ:** `init --tiny` dựng `SPRINT.md` hai phần, `init --size small` dựng `SPRINT.md` bốn phần;
  `check` báo `sprint-size-mismatch` khi `SPRINT.md` ở cỡ vừa/lớn hoặc khi cỡ rất nhỏ lại dựng bốn file. Sprint cũ
  vẫn hợp lệ: `SPRINT.md` cỡ rất nhỏ bốn phần, và bốn file cỡ nhỏ ([templates/README.md](../templates/README.md) mục 4).
- **Người làm không tự chấm ở mọi bậc.** Việc rất nhỏ không có agent thứ hai thì ghi "tự kiểm, chưa độc lập".

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

Cấu hình đổi quyền, hook hay workflow thực thi **không được** xếp rất nhỏ dù diff một dòng (và `risk: high` buộc cỡ lớn).

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
