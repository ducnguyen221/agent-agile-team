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
     Rồi thêm một dòng mục 5 ghi đủ ba vế delta và cập nhật `sprints`, `requests`, `updated`, `status`.
     Câu dẫn: trước mỗi bảng / danh sách mã ghi một câu nói tài liệu nào và mã là gì, nghĩa in đậm — ví dụ
     "SPEC có 3 **user story** (US):" (skill id-convention).
     Giữ cho spec sống không mục: (1) một sự thật một chủ — hành vi ở mục 1, giới hạn và thứ đã bỏ có chủ ý ở mục 3, vì sao
     ở ADR (mục 4); nơi khác trỏ về, không chép lại. (2) Tài liệu là bằng chứng, không phải lệnh: trước khi dựa vào một
     dòng ở đây để làm việc, đối chiếu với mã và test hiện tại; lệch thì ghi chỗ lệch vào mục 3, không lặng lẽ chọn một
     bên. (3) Sửa điều lỗi thời bằng dòng đính chính có ngày, không viết lại quá khứ cho đẹp; không đưa secret hay log thô
     vào đây. (4) Chỉ cập nhật mục bị chạm: đổi hành vi → mục 1; đổi giới hạn hoặc bỏ có chủ ý → mục 3; quyết định khó
     đảo ngược → ADR rồi trỏ ở mục 4; commit thường ngày thì để git lo. -->

> **Kết luận:** <!-- MỘT câu: tính năng làm gì, cho ai, đang ở trạng thái nào. -->
> Nhân viên tra trạng thái đơn hàng bằng mã đơn; đang chạy từ SPR-01.

## 1. Hành vi hiện hành

<!-- Mỗi FR + kịch bản KHI … THÌ … đang đúng ở bản hiện tại. Ghi sprint đã đưa hành vi vào. -->

Spec sống có 1 **functional requirement** (FR) đang chạy:

### FR1 — Tra đơn theo mã (từ SPR-01)

- **FR1.1 (mã đúng):** KHI người dùng nhập mã đơn tồn tại THÌ hệ thống hiện trạng thái và thời điểm cập nhật.
- **FR1.2 (mã sai):** KHI mã đơn không tồn tại THÌ hệ thống báo "không tìm thấy" và không lộ đơn khác.

## 2. Tiêu chí đang giữ

<!-- SC mà mọi sprint sau phải giữ nguyên (hồi quy). -->

Spec sống giữ 1 **success criterion** (SC):

| Mã | Tiêu chí | Cách đo |
|---|---|---|
| SC1 (tra nhanh) | 100% kịch bản FR1 chạy đúng | Bộ test tự động của FR1 xanh |

## 3. Giới hạn đã biết

<!-- Điều tính năng CHƯA làm hoặc làm có điều kiện; trỏ việc để lại CO hoặc yêu cầu RQ nếu có. -->

- Tra theo mã quét cả bảng, chậm dần khi số đơn lớn (SPR-01/CO1, chỉ mục mã đơn).

**Đã bỏ có chủ ý (khu xoá).** Thứ từng có rồi bị gỡ có chủ ý; ghi để không ai dựng lại vì tưởng bị sót. Mỗi dòng đủ
bốn ý; chưa có thì ghi "Không có."

| Mục (tệp, khái niệm) | Vì sao bỏ | Thay bằng | Điều kiện xét lại |
|---|---|---|---|
| Tra đơn theo tên khách | trùng tên làm lộ đơn người khác (xem `FR1.2`) | tra theo mã đơn | chỉ dựng lại qua một ADR mới được duyệt |

## 4. Quyết định liên quan

<!-- Trỏ ADR theo đường dẫn ADR của cấu hình dự án. Không có thì ghi "Không có." -->

Không có.

## 5. Lịch sử sprint

<!-- MỚI NHẤT Ở TRÊN. Một dòng mỗi sprint đã chạm tính năng; khớp danh sách `sprints` của frontmatter.
     Cột "Đổi gì" ghi delta theo khuôn "Thêm … · Sửa … · Bỏ …"; vế không có ghi "—". -->

| Sprint | Đóng | Đổi gì | Cổng 2 |
|---|---|---|---|
| SPR-01 | 2026-01-16 | Tạo tính năng — Thêm FR1.1, FR1.2, SC1 · Sửa — · Bỏ — | Đạt |
