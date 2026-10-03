# Brief cho Implementer — khuôn và hợp đồng

<!-- Nguồn: obra/superpowers skills/subagent-driven-development/implementer-prompt.md @ 8ca22db (MIT);
     affaan-m/ECC skills/prompt-optimizer (phần tối ưu brief) @ c70874f (MIT). Viết lại theo repo này. -->

> **Kết luận:** brief là **nguồn yêu cầu duy nhất** của một `TK`: mục `TKn` của PLAN (giá trị chính
> xác chỉ ở đó) + giao diện và phán quyết từ `TK` trước mà PLAN không biết + điều cấm + hợp đồng báo
> cáo. **≤40 dòng, không tính khối hợp đồng, không dán lịch sử phiên, không dán cả PLAN.** Một phiên thật từng gửi brief 42 000 ký
> tự mà 99 % là lịch sử dán vào.

## 1. Năm phần của brief

| # | Phần | Viết gì |
|---|---|---|
| 1 | Vị trí | một câu: `TK` này nằm đâu trong sprint, phụ thuộc `TK` nào |
| 2 | Yêu cầu | "Đọc trước: `PLAN.md` mục `TKn` — đó là yêu cầu của bạn, dùng đúng giá trị ghi ở đó" + Ràng buộc chung của PLAN (chép nguyên văn hoặc trỏ mục) |
| 3 | Ngữ cảnh brief không biết | giao diện `TK` trước đã **sinh thật** (tên, chữ ký đúng như trong code), phán quyết đã ghi ở PROGRESS liên quan vùng này, phát hiện gác lại ở vùng này (trỏ dòng sổ) |
| 4 | Giải mơ hồ | điểm mơ hồ Analyst đã thấy trong brief và cách Analyst quyết (một dòng mỗi điểm) |
| 5 | Hợp đồng | thư mục làm việc · file báo cáo (`.tmp/TKn-report.md`) · khối hợp đồng ở mục 3 · khối văn phong rút gọn (skill `response-style` mục 8) |

Giá trị chính xác (số, chuỗi, chữ ký, test) **chỉ** xuất hiện ở mục `TKn` của PLAN — brief trỏ, không
chép, để không có hai nguồn lệch nhau.

## 2. Kiểm brief trước khi gửi (từ danh mục tối ưu prompt)

- **Ý định rõ:** làm gì (tạo / sửa / xoá / kiểm), ở đâu, xong khi nào — Implementer không phải đoán.
- **Phạm vi file:** liệt kê file được chạm; ngoài danh sách là điều cấm, trừ khi báo "xong có lo ngại".
- **Thiếu ngữ cảnh:** rà nhanh 11 điểm của skill `intake` cho riêng `TK` này — điểm nào PLAN chưa trả
  lời mà Implementer sẽ vấp thì ghi vào phần 3 hoặc 4.
- **Định dạng ra:** hợp đồng báo cáo (mục 3) có mặt nguyên văn.
- **Tier/model:** ghi model chỉ khi harness cần tham số; luôn ghi vào PROGRESS.
- **Không mớm:** không ghi "reviewer sẽ không bắt X", không ghi lịch sử các `TK` trước ("trạng thái sau
  TK1–3"), không chép nội dung tài liệu Implementer tự đọc được.

## 3. Khối hợp đồng — chép nguyên vào brief

```
## Việc của bạn
1. Đọc mục TKn của PLAN trước. Có câu hỏi về yêu cầu, cách làm, giả định → hỏi NGAY, trước khi làm.
2. Làm đúng những gì TKn ghi: test trước (RED → thấy hỏng → GREEN → cả bộ xanh), commit theo bước.
3. Khi làm: chạy test tập trung cho chỗ đang sửa; chạy cả bộ một lần trước khi commit.
4. Tự review (dưới), rồi báo cáo.

## Bạn không giao subagent
Làm toàn bộ việc này tự tay. Không mở subagent làm một phần, và nhất là không mở reviewer kiểm
việc của mình — review do điều phối giao sau khi bạn báo cáo; reviewer bạn mở là ghế trùng, kết
quả không tính.

## Tổ chức code
Theo cấu trúc file PLAN ghi; mỗi file một trách nhiệm. File đang tạo phình quá ý PLAN → dừng, báo
"xong có lo ngại", không tự tách. File có sẵn đã rối → làm cẩn thận, ghi lo ngại. Theo khuôn repo;
cải thiện chỗ mình chạm như một kỹ sư tốt, không cấu trúc lại ngoài việc.

## Khi quá sức
Dừng và nói "việc này quá sức" luôn được phép; làm dở tệ hơn không làm. Dừng khi: cần quyết định
kiến trúc có nhiều hướng hợp lệ · phải hiểu code ngoài phần được giao mà không tìm ra · không chắc
hướng đúng · phải cấu trúc lại thứ PLAN không lường · đọc hết file này sang file khác mà không tiến.
Báo "bị chặn" hoặc "thiếu ngữ cảnh": kẹt ở đâu, đã thử gì, cần gì.

## Tự review trước khi báo
Đủ: làm hết yêu cầu? sót gì? biên nào chưa xử? · Chất lượng: tên đúng với việc nó làm? · Kỷ luật:
không làm thừa (YAGNI)? theo khuôn repo? · Test: test kiểm hành vi thật, không kiểm mock? output
test sạch, không cảnh báo lạ? Thấy lỗi → sửa ngay rồi mới báo.

## Sau khi review có phát hiện
Bạn sẽ được nối lại với danh sách phát hiện. Sửa, chạy lại test phủ chỗ sửa, nối vào CUỐI file
báo cáo: đổi gì, test nào, lệnh, output. Reviewer không chạy lại test cho bạn — báo cáo là bằng
chứng. Rồi trả lại đúng khối ngắn như lần đầu.

## Báo cáo
Ghi đầy đủ vào <file báo cáo>: đã làm gì (hoặc đã thử gì nếu chặn) · đã test gì, kết quả · bằng chứng
RED (lệnh, output hỏng, vì sao hỏng là đúng) và GREEN (lệnh, output đạt) · file đổi · phát hiện khi
tự review · lo ngại.
Rồi trả về CHỈ (≤15 dòng):
- Trạng thái: xong | xong có lo ngại | bị chặn | thiếu ngữ cảnh
- Commit (sha ngắn + tiêu đề)
- Một dòng test ("14/14 đạt, output sạch")
- Lo ngại (nếu có)
- Đường dẫn file báo cáo
Bị chặn / thiếu ngữ cảnh → ghi cụ thể ngay trong lời trả, điều phối xử lý trực tiếp.
"Xong có lo ngại" khi làm xong mà còn ngờ đúng/sai. Không bao giờ im lặng nộp thứ mình không chắc.
```

## 4. Brief cho vòng sửa

Nối lại cùng agent: "Review trả các phát hiện sau (nguyên văn): … Sửa, chạy lại test phủ (`<file test>`),
nối báo cáo sửa vào `<file báo cáo>`, trả khối ngắn." Agent mới (vòng sau 3, hoặc harness không nối
được): thêm "Một Implementer trước đã thử `TKn` <r> lần; giờ việc là của bạn. Đọc `<file báo cáo>` để
biết đã thử gì." + brief gốc + file báo cáo + phát hiện.
