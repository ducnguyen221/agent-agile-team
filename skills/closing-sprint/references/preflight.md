# Tiền kiểm bằng chứng

<!-- Nguồn ý: bộ skill quy trình private, `preflight-gate` (không giấy phép). Viết lại phòng sạch từ danh sách ý
     (`TK10.6`), không mở văn bản gốc. -->

> **Kết luận:** tiền kiểm là lưới cuối trước Cổng 2 và trước khi gộp: so bằng chứng đang có với **ma trận theo
> cỡ và rủi ro** (mục 2), đi hết **danh mục đánh số** (mục 3), rồi ghi **khối kết luận ba dòng** (mục 4). Kết
> luận là Đạt / Đạt có điều kiện / Không đạt. Đạt có điều kiện chỉ hợp lệ khi mỗi điều kiện là một `CO` **có
> chủ và mốc** — thiếu một trong hai là Không đạt. Secret trong diff, test bị tắt thay vì sửa, rủi ro cao
> không có kế hoạch hoàn tác: Không đạt, không thương lượng.

## 1. Khi nào

| Chạy | Không chạy |
|---|---|
| Trước khi trình Cổng 2, mọi cỡ (rất nhỏ: hàng đầu ma trận, ghi trong `SPRINT.md`) | Giữa lúc thực thi — đó là việc của `tdd` và `verify-before-done` |
| Trước khi gộp hay push; **chạy lại** nếu nhánh có commit mới sau Cổng 2 | Để "xem trước" khi kiểm định còn Chặn/Phải sửa mở — xong vòng kiểm định trước |
| Khi reviewer hay người dùng hỏi "xong chưa" | — |

Sprint chỉ sửa tài liệu dùng hàng rất nhỏ / nhỏ của ma trận.

## 2. Ma trận cổng

Cỡ theo `method/sizing.md`. Hàng dưới **cộng thêm** vào hàng trên; rủi ro chỉ đẩy xuống hàng nặng hơn, không
bao giờ kéo lên. Mọi `VR` phải do agent khác người làm chạy và **tươi** theo mốc commit đang trình
(`method/evidence.md` mục 3).

| Cỡ | Bằng chứng bắt buộc |
|---|---|
| Rất nhỏ, nhỏ | cả bộ test xanh trên đúng mốc · lint sạch · review toàn nhánh bởi agent khác (rất nhỏ được tự kiểm, ghi "chưa độc lập" — kết luận tối đa Đạt có điều kiện) · mỗi `SC` có `VR` Đạt |
| Vừa | + test tích hợp cho luồng mới · coverage ≥ ngưỡng dự án (mặc định 80 %) cho code mới và code sửa · mỗi cờ tính năng có chủ và giá trị mặc định · log hoặc metric quan sát được hành vi mới |
| Lớn, hoặc `risk: high` | + review chuyên đề theo từng nhãn `risk_tags` · diễn tập migration nếu đổi dữ liệu (`database-migrations`, `references/rehearsal.md`) · triển khai theo bậc kèm kế hoạch hoàn tác **đã kiểm** (lệnh + điều kiện huỷ) · ADR, hoặc PLAN ghi "không có quyết định kiến trúc mới" |

## 3. Danh mục kiểm

Cột "Ai kiểm": **máy** = công cụ `check` chạy trên thư mục sprint báo ra (mã luật trong ngoặc); **tay** =
Analyst tự đối chiếu, ghi bằng chứng `file:dòng` hoặc lệnh. Dòng có cả hai thì làm cả hai.

| # | Kiểm | Không đạt khi | Ai kiểm |
|---|---|---|---|
| 1 | Mỗi `SC` có `VR` Đạt; mỗi `FR` (hoặc kịch bản của nó) có ít nhất một `VR` | `SC` bắt buộc thiếu `VR`, hoặc `VR` là Chưa chạy / Không áp dụng chưa có reviewer xác nhận | máy (`report-sc-without-vr`, `report-fr-without-vr`) + tay (kết quả từng `VR`) |
| 2 | `VR` độc lập, có lệnh + kết quả + mốc commit, không cũ hơn thay đổi code cuối | người chạy trùng người làm mà không ghi; mốc trong `VR` trước commit sửa code cuối | máy (`qa-not-independent`, `self-review`) + tay (mốc so với `git log`) |
| 3 | 0 `RF` Chặn còn mở; `RF` Phải sửa còn mở chỉ khi người dùng chấp nhận, câu chấp nhận ghi rõ | còn Chặn; Phải sửa mở không có lời chấp nhận | tay |
| 4 | Nên sửa hoãn đã thành `CO` có chủ + mốc, kèm dòng `RQ-` trong REQUESTS | `CO` thiếu chủ hoặc mốc, hoặc không có dòng sổ | tay |
| 5 | Sprint sửa lỗi: test hồi quy có vòng gỡ sửa → hỏng → đặt lại → đạt | chỉ có lần đạt | tay |
| 6 | Không thêm skip/xfail, không tắt test, không nới linter, không hạ coverage (`method/conventions.md` mục 4) | diff chạm cấu hình kiểm mà không có `TK` riêng có lý do | tay (đọc diff file cấu hình test/lint) |
| 7 | Diff không chứa secret | có secret → **Không đạt** và điều kiện dừng (b): báo ngay để xoay vòng khoá | tay + công cụ quét secret của dự án nếu có |
| 8 | CHANGELOG chỉ thêm mục; VERSION không đổi | mục cũ bị sửa hay xoá; version tự tăng | tay (diff hai file) |
| 9 | REPORT đủ mục; mục "Cách dùng, đã đổi gì, cách hoàn tác" có đủ ba phần | thiếu mục; một trong ba phần trống | máy (`heading-missing`, chỉ tiêu đề) + tay (nội dung) |
| 10 | Mọi mã nhắc chéo có định nghĩa; mọi `TK` trỏ `FR`/`SC`; trường cổng hợp lệ | mã treo; `TK` không truy vết; cổng thiếu câu nguyên văn | máy (`xref-missing`, `task-without-trace`, `gate-invalid`) |
| 11 | Cỡ lớn: reviewer chuyên đề ghi phần "không đánh giá"; hoàn tác có lệnh thật | thiếu phần không đánh giá; hoàn tác chỉ ghi "revert" trong khi migration đã backfill dữ liệu | tay |
| 12 | Mọi dòng `Phán quyết:` trong PROGRESS đã được đọc lại và gom vào Retro của REPORT | Retro không nhắc phán quyết nào dù PROGRESS có | tay |

Kết quả máy chỉ chứng minh hồ sơ **nhất quán**; nó không chứng minh test thật sự đã chạy hay chạy đúng mốc.

## 4. Kết luận và ghi

| Kết luận | Khi |
|---|---|
| Đạt | mọi ô của hàng ma trận và mọi dòng danh mục đạt |
| Đạt có điều kiện | còn lại chỉ Nên sửa đã hoãn, Phải sửa người dùng đã chấp nhận ghi rõ, hoặc tự kiểm ở việc rất nhỏ — mỗi điều kiện là `CO` có chủ và mốc |
| Không đạt | còn bất kỳ ô nào khác; hoặc điều kiện thiếu chủ / mốc; hoặc dòng 7, test bị tắt, rủi ro cao thiếu hoàn tác |

Ghi đúng ba dòng vào nhật ký PROGRESS:

```text
Tiền kiểm SPR-xx — cỡ <rất nhỏ|nhỏ|vừa|lớn>, rủi ro <normal|high>: <Đạt | Đạt có điều kiện | Không đạt>
Chưa đạt: <#n — vì sao; #m — vì sao> | không
Điều kiện: <COk (tên) — chủ — mốc; …> | không
```

Chỉ Đạt và Đạt có điều kiện mới được trình Cổng 2 (dán ba dòng này vào dòng "Kiểm định" của lời trình).
Không đạt → quay lại Bước 3 hoặc Bước 4 sửa đúng dòng hỏng rồi chạy lại tiền kiểm; không trình Cổng 2 "kèm
ghi chú để người dùng tự quyết".
