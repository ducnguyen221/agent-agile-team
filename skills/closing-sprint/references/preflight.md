# Tiền kiểm bằng chứng — trước khi trình Cổng 2 và trước khi gộp

<!-- Nguồn: dev-process preflight-gate (gốc Academy, không giấy phép — viết lại hoàn toàn, ý: ma trận
     cổng theo rủi ro; bằng chứng đính kèm; secret trong diff = không đạt). rewrite_before_public. -->

> **Kết luận:** tiền kiểm là **lưới cuối**: so bằng chứng đã có với ma trận theo **cỡ và rủi ro**,
> không bao giờ vẫy tay cho qua. Kết luận Đạt / Đạt có điều kiện / Không đạt; **Đạt có điều kiện phải
> có `CO` có chủ và mốc**, không thì là Không đạt. Secret trong diff, test bị tắt thay vì sửa, rủi ro
> cao không có kế hoạch hoàn tác → **Không đạt**.

## 1. Khi nào

- Trước khi Analyst trình Cổng 2 (bắt buộc, mọi cỡ từ nhỏ).
- Trước khi gộp/push (lại một lần nếu nhánh đổi sau Cổng 2).
- Reviewer hỏi "xong chưa?" — trả lời bằng bảng này.

Không chạy giữa chừng thực thi (quá sớm — `tdd` và `verify-before-done` lo); sprint chỉ-tài-liệu
dùng hàng "rất nhỏ / nhỏ".

## 2. Ma trận cổng — bằng chứng bắt buộc theo cỡ

| Cỡ (theo `method/sizing.md`) | Bằng chứng bắt buộc (`VR` do agent khác, tươi theo mốc commit) |
|---|---|
| **Rất nhỏ / nhỏ** | cả bộ test xanh · lint sạch · review bởi agent khác (toàn nhánh) · mỗi `SC` có `VR` Đạt |
| **Vừa** | như trên **+** test tích hợp cho luồng mới · coverage ≥ ngưỡng cho code mới/sửa · cờ tính năng (nếu có) khai báo chủ và mặc định · log/metric cho hành vi mới (biết nó chạy ở môi trường thật bằng gì) |
| **Lớn / `risk: high`** | như trên **+** review chuyên đề theo `risk_tags` (security / data / backend / frontend) · diễn tập migration nếu đổi dữ liệu (skill `database-migrations`) · kế hoạch triển khai theo bậc và **kế hoạch hoàn tác** đã kiểm (lệnh + điều kiện huỷ) · ADR cho quyết định kiến trúc hoặc dòng "không có quyết định kiến trúc mới" |

Rủi ro chỉ nâng hàng, không hạ.

## 3. Danh mục kiểm — đánh từng dòng

| # | Kiểm | Không đạt khi |
|---|---|---|
| 1 | Mỗi `SC` của SPEC có ít nhất một `VR` Đạt; mỗi kịch bản `FR` có `VR` | `VR` Chưa chạy / Không áp dụng ở `SC` bắt buộc |
| 2 | `VR` do agent khác người làm, có lệnh + kết quả + mốc commit (`method/evidence.md`) | tự kiểm không ghi "chưa độc lập"; bằng chứng từ commit cũ hơn thay đổi cuối |
| 3 | 0 `RF` Chặn còn mở; Phải sửa còn mở chỉ khi người dùng chấp nhận **ghi rõ** | còn Chặn |
| 4 | Nên sửa hoãn → `CO` có chủ và mốc | `CO` không chủ |
| 5 | Test hồi quy cho lỗi đã sửa đi vòng gỡ-sửa → hỏng → đặt lại → đạt | chỉ có "test xanh" |
| 6 | Không test nào bị `skip`/`xfail`/tắt để qua; không nới linter, không hạ coverage | có — vi phạm luật git (`method/conventions.md` mục 4) → Chặn |
| 7 | Diff không chứa secret, khoá, token, `.env` | có → Không đạt **và** điều kiện dừng (b), báo để xoay vòng |
| 8 | CHANGELOG chỉ **thêm** mục dưới tiêu đề đang mở; VERSION không tự tăng | ghi đè, viết lại mục cũ, tự bump |
| 9 | REPORT đủ mục bắt buộc; mục "Cách dùng, đã đổi gì, cách hoàn tác" có cả ba phần | thiếu hoàn tác |
| 10 | Cỡ lớn: `risk_tags` ↔ reviewer chuyên đề đã ghi "không đánh giá" gì; kế hoạch hoàn tác có lệnh thật | hoàn tác chỉ là "revert" cho migration đã backfill |
| 11 | Mọi `Phán quyết:` đã gom vào REPORT | phán quyết chỉ nằm trong nhật ký |

Công cụ `check` của repo chạy được 1 (đối chiếu mã), 3, 4 và cấu trúc REPORT; còn lại là việc của Analyst.

## 4. Kết luận và ghi

```
Tiền kiểm <SPR-> — cỡ <cỡ>, rủi ro <mức>: Đạt | Đạt có điều kiện | Không đạt
Không đạt ở: <#dòng — vì sao> (hoặc "không")
Điều kiện (→ CO có chủ, mốc): <COk — chủ — mốc> (hoặc "không")
```

Ghi vào nhật ký PROGRESS; kết quả Đạt / Đạt có điều kiện mới trình Cổng 2. Không đạt → về Bước 3/4
với phát hiện tương ứng, không "trình kèm ghi chú".
