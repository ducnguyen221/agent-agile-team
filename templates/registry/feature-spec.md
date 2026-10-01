---
id: FS-001
doc: feature
title: Feature name
status: live
requests: [RQ-001]
sprints: [SPR-01]
created: 2026-01-15
updated: 2026-01-16
---

# Tên tính năng — Spec sống

<!-- Spec sống mô tả HÀNH VI HIỆN HÀNH của một tính năng, không mô tả kế hoạch. Chỉ cập nhật sau khi Cổng 2 của
     một sprint chạm tính năng này đạt — ngay trong sprint đó. Mã FR/SC ở đây thuộc tính năng; nhắc từ tài liệu
     khác viết `FS-001/FR1.1`. Không đánh số lại; hành vi bỏ đi giữ mã, ghi trạng thái `bỏ`.
     Gộp ở Bước 5 (sau Cổng 2) theo delta của SPEC sprint — Thêm / Sửa / Bỏ:
     - Thêm: FR của SPEC không ghi "(sửa …)"/"(bỏ …)" → thêm FR mới vào mục 1 với mã kế tiếp, ghi "(từ SPR-NN)";
       SC cần giữ về sau → thêm vào mục 2.
     - Sửa: FR ghi "(sửa FS-001/FR1.2)" → thay câu KHI … THÌ … của FR1.2, giữ nguyên mã, ghi "(sửa ở SPR-NN)".
     - Bỏ: FR ghi "(bỏ FS-001/FR1.2)" → giữ mã, cuối dòng ghi "— bỏ" (sprint ghi ở mục 5);
       SC chỉ đo hành vi đó cũng ghi bỏ.
     Rồi thêm một dòng mục 5 ghi đủ ba vế delta và cập nhật `sprints`, `requests`, `updated`, `status`. -->

> **Kết luận:** <!-- MỘT câu: tính năng làm gì, cho ai, đang ở trạng thái nào. -->
> Nhân viên tra trạng thái đơn hàng bằng mã đơn; đang chạy từ SPR-01.

## 1. Hành vi hiện hành

<!-- Mỗi FR + kịch bản KHI … THÌ … đang đúng ở bản hiện tại. Ghi sprint đã đưa hành vi vào. -->

### FR1 — Tra đơn theo mã (từ SPR-01)

- **FR1.1 (mã đúng):** KHI người dùng nhập mã đơn tồn tại THÌ hệ thống hiện trạng thái và thời điểm cập nhật.
- **FR1.2 (mã sai):** KHI mã đơn không tồn tại THÌ hệ thống báo "không tìm thấy" và không lộ đơn khác.

## 2. Tiêu chí đang giữ

<!-- SC mà mọi sprint sau phải giữ nguyên (hồi quy). -->

| Mã | Tiêu chí | Cách đo |
|---|---|---|
| SC1 (tra nhanh) | 100% kịch bản FR1 chạy đúng | Bộ test tự động của FR1 xanh |

## 3. Giới hạn đã biết

<!-- Điều tính năng CHƯA làm hoặc làm có điều kiện; trỏ việc để lại CO hoặc yêu cầu RQ nếu có. -->

- Tra theo mã quét cả bảng, chậm dần khi số đơn lớn (SPR-01/CO1, chỉ mục mã đơn).

## 4. Quyết định liên quan

<!-- Trỏ ADR theo đường dẫn ADR của cấu hình dự án. Không có thì ghi "Không có." -->

Không có.

## 5. Lịch sử sprint

<!-- MỚI NHẤT Ở TRÊN. Một dòng mỗi sprint đã chạm tính năng; khớp danh sách `sprints` của frontmatter.
     Cột "Đổi gì" ghi delta theo khuôn "Thêm … · Sửa … · Bỏ …"; vế không có ghi "—". -->

| Sprint | Đóng | Đổi gì | Cổng 2 |
|---|---|---|---|
| SPR-01 | 2026-01-16 | Tạo tính năng — Thêm FR1.1, FR1.2, SC1 · Sửa — · Bỏ — | Đạt |
