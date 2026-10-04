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

## 5. Đối chiếu luồng orch

Nhiều bộ công cụ chia việc thành năm **luồng** theo loại thay đổi (thêm tính năng, đổi hành vi có sẵn, sửa lỗi, tái
cấu trúc, dựng bản đầu từ tài liệu thiết kế). Repo này **không** thêm trục thứ hai: cỡ việc (mục 1) vẫn là trục duy
nhất quyết độ dày tài liệu và cổng. Bảng dưới chỉ trả lời "một luồng quen tay rơi vào cỡ nào, bước đầu tiên là gì,
kéo skill nào". Bốn bậc của nguồn (nhỏ nhất → lớn nhất) khớp bốn cỡ **Rất nhỏ · Nhỏ · Vừa · Lớn** ở trên, nhưng nguồn
chỉ đếm số file; ở đây cỡ còn do hành vi, hợp đồng và rủi ro quyết.

Bảng có 5 hàng — mỗi hàng một **luồng** ở cột đầu:

| Luồng (loại việc) | Cỡ tối thiểu | Bước đầu tiên khi làm | Cổng người | Skill kéo vào |
|---|---|---|---|---|
| Thêm tính năng (hành vi chưa có) | **Vừa** — luôn có hành vi hay luồng mới | viết test mới cho hành vi mới, thấy nó hỏng **đúng lý do**, rồi mới viết mã | Cổng 1 và Cổng 2 đủ | `intake` → `shaping-spec` → `writing-plan` → `running-sprint` + `tdd` → `code-review` |
| Đổi hành vi có sẵn (chạy đúng nhưng muốn khác) | **Nhỏ** — một luồng, một `FR`, không đổi hợp đồng; **Vừa** khi đổi nhiều hơn một `FR` | sửa **test hiện có** cho khớp hành vi mới rồi đổi mã tới khi đạt; sửa test trước là điểm phân biệt đổi hành vi với sửa lỗi | Cổng 1 và Cổng 2 thật (trình ngắn) | `intake`, `shaping-spec` (delta **Sửa** cho spec sống), `tdd`, `code-review` |
| Sửa lỗi (hành vi sai, hồi quy) | **Nhỏ** — sửa lỗi là đổi hành vi nên không xuống Rất nhỏ; lỗi chạm vùng rủi ro (mục 2) thì **Lớn** | tái hiện lỗi thành **test hỏng** (test hồi quy) rồi sửa; chứng minh bằng vòng gỡ sửa → hỏng → đặt lại ([evidence.md](evidence.md) mục 4) | Cổng 1 và Cổng 2 thật | `bug-triage` (chấm mức, định tuyến) → `debugging` → `tdd` → `verify-before-done` |
| Tái cấu trúc (giữ hành vi, đổi cấu trúc) | theo **phạm vi đụng tới**: **Nhỏ** khi một mô-đun cục bộ; **Vừa** khi nhiều mô-đun hoặc đổi giao diện nội bộ; **Lớn** khi chạm hợp đồng bên ngoài | xác nhận test liên quan **đang xanh trước khi chạm mã**; thiếu thì viết test mô tả hành vi hiện tại; đổi từng bước nhỏ, chạy lại sau mỗi bước; diff phải trung tính về hành vi | như cỡ đã chọn | `tdd`, `code-review` (kể cả tìm hàm trùng lặp), `verify-before-done` |
| Dựng bản đầu từ tài liệu thiết kế | **Lớn** | đọc tài liệu, trích phạm vi, quyết định đã khoá và danh sách tính năng; cắt thành **lát dọc mỏng** (một đường chạy hết đầu–cuối trước, không làm hết lớp này rồi mới tới lớp kia) | Cổng 1 và Cổng 2 đủ; mỗi lát một mục tiêu nên **một sprint một lát**, cùng trỏ về một `RQ-` | `intake`, `shaping-spec`, `writing-plan`, `adr` |

Luật đi kèm:

- **Luồng không hạ cỡ.** Cột "cỡ tối thiểu" là sàn; mục 1 (phân vân chọn bậc nặng hơn) và mục 2 (rủi ro chỉ nâng)
  vẫn quyết cỡ cuối cùng. Việc chạm vùng rủi ro nào ở mục 2 cũng thành cỡ lớn, bất kể luồng.
- **Cổng 2 là nghiệm thu sau REPORT**, không đặt trước từng lần commit. Commit nằm trong bước thực thi theo từng
  `TK`; push, mở PR và gộp nhánh chính chỉ sau Cổng 2 và khi người dùng gật ([process.md](process.md) mục 7).
- **Kiểm định luôn do agent khác** người làm ở mọi luồng và mọi cỡ; thêm Tech Reviewer kéo thẻ chuyên đề security khi
  việc chạm secret, xác thực hay đầu vào từ ngoài (mục 2).
