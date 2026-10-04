---
title: Severity — one finding scale, one verdict scale, one conversion table
type: method
status: active
updated: 2026-10-01
---

# Thang mức: một thang phát hiện, một thang kết luận, một bảng quy đổi

> **Kết luận:** mọi phát hiện mang đúng một trong bốn mức **Chặn / Phải sửa / Nên sửa / Ghi chú**; mọi
> kết luận là một trong ba **Đạt / Đạt có điều kiện / Không đạt**. Bảng quy đổi ở mục 4 là nơi **duy
> nhất** trong repo được chứa nhãn của thang cũ; ngoài bảng đó, nhãn cũ không xuất hiện.

## 1. Thang phát hiện (`RF`)

| Mức | Nghĩa | Hành động bắt buộc |
|---|---|---|
| **Chặn** | Sai yêu cầu, mất dữ liệu, lỗ hổng bảo mật, test hỏng, không build được, hoặc vi phạm điều cấm | Dừng kết luận Đạt. Sửa ngay trong vòng hiện tại; không được hoãn, không được gộp vào sprint sau |
| **Phải sửa** | Hành vi sai ở nhánh phụ, thiếu test cho hành vi mới, lỗi sẽ gây sự cố khi tải tăng, hợp đồng không khớp | Sửa trước Cổng 2. Mở vòng mới nếu đã qua kiểm định |
| **Nên sửa** | Chất lượng: trùng lặp, đặt tên, cấu trúc, hiệu năng chưa đo thấy, tài liệu thiếu | **Được hoãn.** Nếu không sửa trong sprint thì ghi thành `CO` (việc để lại) có chủ; không chặn Cổng 2 |
| **Ghi chú** | Quan sát, gợi ý, "nit", câu hỏi mở không ảnh hưởng kết quả | Không cần hành động; người làm đọc và tự quyết. Không bao giờ chặn |

Quy tắc kèm theo:
- Mỗi `RF` **đúng một mức**; reviewer phân vân giữa hai mức thì chọn mức **nặng hơn** và nói rõ vì sao.
- Mỗi `RF` có bằng chứng (`file:dòng`, hoặc lệnh + kết quả). Không bằng chứng → mức tối đa là Ghi chú.
- Mức nói về **hậu quả nếu bỏ qua**, không nói về công sửa. Lỗi một ký tự làm sai tiền vẫn là Chặn.
- Thành thật về mức: gán Chặn cho mọi thứ làm thang mất nghĩa; gán Ghi chú để tránh vòng mới là tự chấm.

## 2. Thang kết luận (Cổng 2, và kết luận của reviewer)

| Kết luận | Điều kiện |
|---|---|
| **Đạt** | 0 Chặn, 0 Phải sửa còn mở; mọi `SC` có `VR` Đạt |
| **Đạt có điều kiện** | 0 Chặn; Phải sửa còn mở đã được người dùng chấp nhận **ghi rõ**, hoặc Nên sửa hoãn thành `CO` có chủ và mốc; hoặc kiểm định chưa độc lập (tự kiểm) — **chỉ ở cỡ rất nhỏ**; cỡ nhỏ trở lên bắt buộc reviewer khác người làm, `qa` trùng nhãn người làm là Phải sửa dù có khai tự kiểm (`check` chỉ bắt được khi `VR` không khai — người đọc hồ sơ bắt phần còn lại) |
| **Không đạt** | Còn Chặn; hoặc `SC` bắt buộc không có `VR` Đạt; hoặc người dùng không nghiệm thu |

Kết luận của reviewer dùng cùng ba từ. Reviewer được kết luận Đạt với 0 phát hiện, nhưng phải ghi phần
**không** đánh giá.

## 3. Kết quả từng phép kiểm (`VR`) — không phải thang mức

`VR` dùng **Đạt · Không đạt · Chưa chạy · Không áp dụng (kèm lý do)**. "Chưa chạy" và "Không áp dụng"
không bao giờ được tính là Đạt. Chi tiết ở [evidence.md](evidence.md).

## 4. Bảng quy đổi duy nhất

Mười thang cũ gặp trong các nguồn đã chưng cất, quy về thang chung. Khi distill nguồn mới gặp thang
khác, thêm một dòng vào đây — không tạo bảng thứ hai.

| # | Thang cũ (nguồn) | → Chặn | → Phải sửa | → Nên sửa | → Ghi chú |
|---|---|---|---|---|---|
| 1 | `P0` `P1` `P2` `P3` (bug triage, plan review, web QA) | `P0` | `P1` | `P2` | `P3` |
| 2 | `S1` `S2` `S3` `S4` (bug triage) | `S1` | `S2` | `S3` | `S4` |
| 3 | `CRITICAL` `HIGH` `MEDIUM` `LOW` (security audit, security reviewer; cả dạng chữ thường `high/medium/low` của web QA) | `CRITICAL` | `HIGH` | `MEDIUM` | `LOW` |
| 4 | `Critical` `Important` `Minor` (review từng việc) | `Critical` | `Important` | `Minor` | — |
| 5 | `BLOCK` `WARN` `INFO` `NOTE` (luật code review) | `BLOCK` | `WARN` | `INFO` | `NOTE` |
| 6 | `Block` `Warning` `Approve` (web QA, cổng tự động) | `Block` | `Warning` | — | `Approve` = không có phát hiện |
| 7 | `FAIL` / `PASS` theo từng mục kiểm (checklist bảo mật) | `FAIL` ở mục bảo mật | `FAIL` ở mục khác | — | `PASS` = không có phát hiện |
| 8 | `Strengths` / `Issues` 3 mức / `Ready to merge: Yes · With fixes · No` (yêu cầu review) | `No` | `With fixes` | — | `Strengths` = Ghi chú tích cực |
| 9 | "Nit:" (chuẩn review kỹ thuật) | — | — | — | "Nit:" |
| 10 | `Spec ✅ / ⚠️ / ❌` (review khớp spec) | `❌` | `⚠️` | — | `✅` = không có phát hiện |

**Kết luận cũ → kết luận mới:**

| Thang cũ | Đạt | Đạt có điều kiện | Không đạt |
|---|---|---|---|
| `Go` / `Conditional` / `No-Go` (cổng trước phát hành) | `Go` | `Conditional` (phải có việc theo dõi + chủ) | `No-Go` |
| `PASS` / `REVISE` / `BLOCK` (cổng chất lượng) | `PASS` | `REVISE` | `BLOCK` |
| `Approve` / `Request changes` (review nhánh) | `Approve` | — | `Request changes` |

**Trạng thái báo cáo của người làm — không phải mức, quy về trạng thái việc:** `DONE` → Đạt ·
`DONE_WITH_CONCERNS` → Đạt có điều kiện, mối lo ghi thành `RF` hoặc `CO` · `BLOCKED` → `BR` ·
`NEEDS_CONTEXT` → `BR` (nếu cần người) hoặc `CQ` (nếu thuộc SPEC).
