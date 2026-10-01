# Ghi chú phát hành

<!-- Nguồn: bộ skill quy trình private, `release-notes-writer` (private copy, không giấy phép — viết lại hoàn toàn, ý:
     khung đã ship / tác động / cách kiểm / observability / hoàn tác; hai bản nội bộ ↔ bên ngoài).
     rewrite_before_public. -->

> **Kết luận:** ghi chú phát hành lấy nội dung từ **REPORT** (`VR`, `RF`, `CO`), không viết lại từ trí
> nhớ; nhóm theo tác động; luôn có **cách kiểm · quan sát · hoàn tác**; hai bản — **nội bộ** đầy đủ
> và **bên ngoài** không mã nội bộ, không chi tiết hạ tầng, dẫn bằng lợi ích. Không tự tăng version.

## 1. Khi nào

- Sprint đổi hành vi người dùng thấy, đổi API/hợp đồng, đổi dữ liệu, hoặc cắt bản phát hành.
- Người dùng hỏi "tuần này / bản này đổi gì".
- Không viết cho trạng thái giữa sprint (PROGRESS lo) hay bài marketing.

## 2. Nguồn

| Lấy | Từ |
|---|---|
| Đã ship gì | REPORT mục Cách dùng, đã đổi gì; `SC` có `VR` Đạt |
| Chưa ship / có điều kiện | `CO`, `RF` còn mở, `VR` Chưa chạy |
| Cách kiểm | lệnh / thao tác của `VR` |
| Hoàn tác | REPORT mục Cách hoàn tác |
| Cờ tính năng | PLAN / cấu hình: tên, mặc định, **chủ** |

Mục nào không có `VR` Đạt → ghi "**đã phát hành, bằng chứng còn thiếu**" chứ không ghi "đã kiểm".
Cờ tính năng không có chủ → không ship cờ đó; báo Analyst.

## 3. Khung — bản nội bộ

```
# <Tên bản / SPR-> — <ngày ISO>
## Người dùng thấy gì          (mỗi dòng: đổi gì · ai bị ảnh hưởng · họ cần làm gì)
## API và hợp đồng             (endpoint/sự kiện/schema: thêm / sửa / bỏ; bên dùng phải đổi gì)
## Dữ liệu và migration        (bảng, backfill, thời gian, lock; đã diễn tập chưa)
## Vận hành và hạ tầng         (cấu hình, biến môi trường, job, quyền)
## Bảo mật                      (sửa lỗ hổng, đổi quyền — không mô tả cách khai thác)
## Cờ tính năng                 (tên · mặc định · chủ · khi nào bật)
## Cách kiểm                    (bước + VR trỏ tới; ai cũng lặp lại được)
## Quan sát                     (log/metric/dashboard nào cho biết nó chạy; ngưỡng báo động)
## Hoàn tác                     (lệnh, điều kiện huỷ, dữ liệu có hoàn tác được không)
## Còn mở                       (CO, RF còn mở, bằng chứng thiếu)
```

Mã kèm tên ngắn (`FS-007 (tra cứu đơn)`), ngày ISO `YYYY-MM-DD`.

## 4. Bản bên ngoài (khách hàng / hỗ trợ)

- Chỉ hai mục đầu của khung + "cần làm gì" nếu có.
- **Không** mã nội bộ (`SPR-`, `TK`, `RF`), không tên bảng, không hạ tầng, không chi tiết lỗ hổng.
- Mỗi dòng dẫn bằng điều người dùng **làm được** ("Giờ bạn có thể…"), ngắn, không thuật ngữ nội bộ.
- Lưu cạnh bản nội bộ, ghi rõ "bản bên ngoài" ở tiêu đề.

## 5. Không làm

- Không tăng version, không tạo tiêu đề phiên bản trong CHANGELOG (xem `docs-sync.md` mục 5, 7).
- Không ghi "đã kiểm" cho mục không có `VR` Đạt.
- Không chép mô tả commit làm ghi chú — ghi chú nói về tác động, commit nói về code.
