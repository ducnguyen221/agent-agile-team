---
name: bug-triage
description: Use when a bug report, stack trace, failing production flow or "how serious is this" question arrives and the bug must be reproduced, graded, registered and routed (hotfix now / this sprint / next sprint / backlog) — before or instead of debugging it.
metadata:
  group: process
  roles: [analyst]
source: private-process-skills skills/bug-triager/SKILL.md (private copy)
source_sha: 4c0fdc5736a49b6223a7dfc7626d5495cf55185c
license: none
rewrite_before_public: true
---

# Phân loại lỗi

> **Kết luận:** **tái hiện trước, xếp mức sau**; mức theo thang chung (Chặn / Phải sửa / Nên sửa /
> Ghi chú) quyết **đường xử lý** (sửa nóng ngay / sprint này / sprint sau / backlog); lỗi vào sổ
> REQUESTS dưới dạng `RQ-`; mọi bản sửa phải có test hồi quy; nghi sự cố bảo mật thì dừng theo điều
> kiện (b) chứ không "ghi ticket rồi thôi". Thành thật về mức — mọi thứ đều Chặn thì thang mất nghĩa.

## 1. Khi nào — và khi nào không

| Dùng | Không dùng |
|---|---|
| có báo cáo lỗi, stack trace, lỗi môi trường thật; người dùng hỏi "nặng không / ai xem" | "tại sao nó sập" → skill `debugging` trước, phân loại sau |
| theo dõi sau sự cố đã ổn định | yêu cầu tính năng đội lốt lỗi → `intake` như yêu cầu thường |
| hàng chờ lỗi cần xếp | lỗi đã có `RQ-` → trỏ, không mở trùng |

## 2. Bốn bước

1. **Tái hiện.** Bước, dữ liệu, môi trường, phiên bản; quan sát ↔ kỳ vọng. Không tái hiện được → hỏi
   lại người báo (một lượt, các câu gom); người báo không liên lạc được → ghi `RQ-` trạng thái `mới`
   với ghi chú "cần thông tin", **không sửa theo phỏng đoán**.
2. **Xếp mức → đường xử lý.**

   | Mức | Dấu hiệu | Đường |
   |---|---|---|
   | **Chặn** | ngừng dịch vụ, mất dữ liệu, lộ bảo mật, thanh toán hỏng | **sửa nóng ngay** — sprint rất nhỏ/nhỏ riêng, cổng "đạt theo lời giao" nếu lời giao rõ |
   | **Phải sửa** | tính năng chính hỏng với nhiều người, không có đường vòng | **sprint này** — thêm vào sprint đang mở nếu còn trong phạm vi, hoặc mở sprint kế ngay |
   | **Nên sửa** | tính năng phụ hỏng hoặc có đường vòng | **sprint sau** |
   | **Ghi chú** | thẩm mỹ, biên hiếm | **backlog** — `RQ-` trạng thái `mới`, không sprint |

   Mức nói về **hậu quả nếu bỏ qua**, không về công sửa; phân vân → mức nặng hơn và nói vì sao
   (`method/severity.md`). "Mệt vì cái gì cũng Chặn" là thật: gán mức thấp hơn khi bằng chứng chỉ ra
   thế, và ghi bằng chứng.
3. **Ghi sổ.** Một dòng `RQ-` trong REQUESTS: ngày, tóm tắt, mức, cách tái hiện (trỏ log/ảnh), vùng
   nghi ngờ, đường xử lý. Lỗi lộ một **lớp** rủi ro (không chỉ một chỗ) → ghi thêm vào `RK` của sprint
   sửa nó. Mã ngoài (`BUG-123` của hệ theo dõi lỗi) để trong dấu code kèm tên.
4. **Kế hoạch test hồi quy.** Ghi ngay trong `RQ-`: test nào sẽ chứng minh lỗi hết; sprint sửa phải có
   `VR` đi vòng *gỡ sửa → test hỏng → đặt lại → đạt* (`method/evidence.md` mục 4). Không ngoại lệ.

## 3. Dừng và hỏi

- Nghi **sự cố bảo mật hoặc lộ dữ liệu cá nhân** → điều kiện dừng (b): mở `BR`, báo ngay, kéo
  `security-review`; không chỉ ghi `RQ-` rồi xếp hàng.
- Sửa nóng cần đẩy thẳng lên nhánh chung / môi trường thật → điều kiện (c): người dùng gật.

## 4. Đầu ra

Một khối ngắn cho người dùng: *mức (tên) — đường xử lý — đã tái hiện: có/chưa — `RQ-` — test hồi quy
dự kiến — cần quyết: <có/không>*. Không dán log; trỏ đường dẫn.
