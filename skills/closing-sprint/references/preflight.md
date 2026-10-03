# Tiền kiểm bằng chứng

<!-- Nguồn ý: bộ skill quy trình private, `preflight-gate` (không giấy phép). Viết lại phòng sạch từ danh sách ý
     (`TK10.6`), không mở văn bản gốc. -->

> **Kết luận:** tiền kiểm là lần soát cuối trước Cổng 2 và trước khi gộp. Đặt bằng chứng hiện có cạnh **bảng
> yêu cầu của cỡ việc** (mục 2; rủi ro cao dùng hàng nặng hơn), soát **danh mục đánh số** (mục 3), rồi chốt bằng
> **khối ba dòng** (mục 4) với một trong ba kết luận: Đạt / Đạt có điều kiện / Không đạt. Điều kiện nào cũng phải
> là một `CO` ghi **người chịu và hạn**; thiếu thì kết luận rơi xuống Không đạt. Ba trường hợp đi thẳng tới
> Không đạt, không cân nhắc:
>
> - diff để lọt khoá, token hay mật khẩu;
> - có test bị vô hiệu hoá (skip, xfail, xoá) để né lỗi thay vì chữa lỗi;
> - việc rủi ro cao mà đường quay lui chưa từng được thử.

## 1. Khi nào

| Chạy | Không chạy |
|---|---|
| Trước khi trình Cổng 2, mọi cỡ (rất nhỏ: hàng đầu ma trận, ghi trong `SPRINT.md`) | Giữa lúc thực thi — đó là việc của `tdd` và `verify-before-done` |
| Trước khi gộp hay push; **chạy lại** nếu nhánh có commit mới sau Cổng 2 | Để "xem trước" khi kiểm định còn Chặn/Phải sửa mở — xong vòng kiểm định trước |
| Khi reviewer hay người dùng hỏi "xong chưa" | — |

Sprint chỉ sửa tài liệu dùng hàng rất nhỏ / nhỏ của ma trận.

**Thứ tự với REPORT.** Trong `SKILL.md`, tiền kiểm là bước 1, REPORT là bước 2. Vì thế lần chạy ở bước 1 soát mọi
dòng của danh mục **trừ** dòng 4, 9 và 12 — ba dòng này đọc nội dung REPORT. Chúng được soát ở bước 2, ngay khi
REPORT nháp viết xong và **trước** lời trình Cổng 2; khối kết luận ở mục 4 chỉ chốt sau khi cả ba dòng đã soát.

## 2. Ma trận cổng

Cỡ theo `method/sizing.md`. Hàng dưới **cộng thêm** vào hàng trên; rủi ro chỉ đẩy xuống hàng nặng hơn, không
bao giờ kéo lên. Mọi `VR` phải do agent khác người làm chạy và **tươi** theo mốc commit đang trình
(`method/evidence.md` mục 3).

| Cỡ | Bằng chứng bắt buộc |
|---|---|
| Rất nhỏ | cả bộ test xanh trên đúng mốc · lint sạch · mỗi `SC` có `VR` Đạt · kiểm bởi agent khác chạy nhanh, hoặc tự kiểm ghi "chưa độc lập" (khi đó kết luận tối đa Đạt có điều kiện) |
| Nhỏ | như rất nhỏ, nhưng không được tự kiểm: **cả hai** reviewer — Business Reviewer **và** Tech Reviewer, mỗi bên một lượt ngắn trên toàn nhánh (`method/sizing.md` mục 1) |
| Vừa | + mỗi cờ tính năng có người chịu và giá trị mặc định · hành vi mới để lại dấu vết đọc được (log hoặc metric) · luồng mới có ít nhất một test chạy qua ranh giới thật · phần code mới và code sửa đạt ngưỡng coverage của dự án (mặc định 80 %) |
| Lớn, hoặc `risk: high` | + mỗi nhãn trong `risk_tags` có reviewer chuyên đề của nó · đổi dữ liệu thì migration đã chạy thử trên bản sao (`database-migrations`, `references/rehearsal.md`) · đưa lên từng nấc, và đường quay lui **đã thử thật** — có lệnh cụ thể và ngưỡng để quyết định quay lui · quyết định kiến trúc nằm trong ADR (sprint không có quyết định nào thì PLAN nói vậy) |

## 3. Danh mục kiểm

Cột "Ai kiểm": **máy** = công cụ `check` chạy trên thư mục sprint báo ra (mã luật trong ngoặc); **tay** =
Analyst tự đối chiếu, ghi bằng chứng `file:dòng` hoặc lệnh. Dòng có cả hai thì làm cả hai.

| # | Kiểm | Không đạt khi | Ai kiểm |
|---|---|---|---|
| 1 | Mỗi `SC` có `VR` Đạt; mỗi `FR` (hoặc kịch bản của nó) có ít nhất một `VR` | `SC` bắt buộc thiếu `VR`, hoặc `VR` là Chưa chạy / Không áp dụng chưa có reviewer xác nhận | máy (`report-sc-without-vr`, `report-fr-without-vr`) + tay (kết quả từng `VR`) |
| 2 | `VR` độc lập, có lệnh + kết quả + mốc commit, không cũ hơn thay đổi code cuối | người chạy trùng người làm mà không ghi; mốc trong `VR` trước commit sửa code cuối | máy (`qa-not-independent`, `self-review`) + tay (mốc so với `git log`) |
| 3 | Không còn phát hiện mức Chặn nào chưa xử lý; phát hiện Phải sửa nào để treo đều có câu đồng ý của người dùng, chép nguyên văn | có Chặn chưa xử lý; Phải sửa bị treo mà không có câu đồng ý | tay |
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
