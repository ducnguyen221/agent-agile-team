---
name: bug-triage
description: Use when someone reports a defect - a crash, a stack trace, a log full of errors, "it is broken" - and the team must decide how serious it is and when it will be handled, especially when the reporter pushes an urgency label from another tracker, wants it fixed before the failure was ever seen, or insists everything is critical.
metadata:
  group: process
  roles: [analyst]
source: "concept: bug triage - reproduce first, grade by consequence, route by grade (clean-room rewrite in SPR-04 TK10: old text removed first, new writer saw only a noun-phrase idea list)"
source_sha: null
license: none
rewrite_before_public: false
---

# Phân loại lỗi

> **Kết luận:** phân loại đứng **trước** gỡ lỗi và trước mọi cách sửa. Làm ba việc, theo thứ tự: tái hiện
> lỗi, chấm mức theo **hậu quả** trên thang chung (`method/severity.md`), rồi chọn đường xử lý theo mức.
> Kết quả là một dòng `RQ-` trong sổ REQUESTS kèm bản tóm tắt cố định. Chưa tái hiện được thì mức chỉ là
> **tạm**, và không ai sửa theo phỏng đoán.

Skill này dừng ở chỗ lỗi đã có mức và có đường đi. Tìm nguyên nhân gốc và sửa là việc của skill `debugging`
sau đó skill `tdd`, trong sprint đã được mở.

## 1. Luật sắt

```
KHÔNG MỨC, KHÔNG ĐƯỜNG XỬ LÝ, KHÔNG SỬA — KHI CHƯA THẤY LỖI XẢY RA
```

Chưa tái hiện thì chưa biết lỗi thật hay là nhầm lẫn môi trường; chưa biết hậu quả thì chưa chấm được mức.
Mức đẩy lên theo áp lực của người báo, hay do nhãn họ mang theo, đều không phải mức.

## 2. Tái hiện

Ghi đủ ba thứ, theo đúng chữ của kết quả quan sát được:

1. **Các bước** để lỗi xảy ra, từng bước, ai lặp lại cũng được.
2. **Môi trường:** hệ điều hành, phiên bản ứng dụng và công cụ, nhánh + commit, dữ liệu vào đã dùng.
3. **Mong đợi ↔ thực tế:** điều đáng ra xảy ra và điều đã xảy ra, đặt cạnh nhau.

Log hoặc stack trace dài: lưu ra file ở thư mục tạm của sprint và trỏ đường dẫn; trong tóm tắt chỉ giữ dòng
then chốt. Che mọi secret và dữ liệu người dùng trước khi lưu.

**Chưa tái hiện được:** gán mức **tạm** theo hậu quả mà bằng chứng đang có (log, ảnh, lời kể kèm dấu vết) thật
sự chứng minh; không có bằng chứng nào thì mức tối đa là Ghi chú. Việc đầu tiên của đường xử lý là tái hiện.
Không được đoán một nguyên nhân rồi sửa thử.

## 3. Chấm mức và chọn đường

Mức dùng đúng bốn từ của `method/severity.md` và chấm theo **hậu quả nếu bỏ qua**, không theo công sửa hay
độ ồn của người báo. Nhãn mức của hệ theo dõi khác: đổi qua bảng ở `severity.md` mục 4, rồi vẫn đối chiếu
với hậu quả đã tái hiện.

| Mức | Dấu hiệu hậu quả | Đường xử lý |
|---|---|---|
| **Chặn** | mất hay hỏng dữ liệu, lỗ hổng bảo mật, sai tiền, hệ thống ngừng chạy với người dùng | **hotfix** — mở sprint riêng ngay |
| **Phải sửa** | hành vi sai ở luồng chính hay nhánh phụ có người chịu, hợp đồng không khớp | **sprint này** nếu còn chỗ trong mục tiêu, nếu không thì sprint kế đã được mở |
| **Nên sửa** | khó chịu, có cách tránh dễ dàng, không mất gì | **sprint sau** |
| **Ghi chú** | chưa rõ ảnh hưởng, hiếm, hoặc chỉ là quan sát | **backlog** |

- Thang chỉ có nghĩa khi mức nặng hiếm: nếu lỗi nào cũng được Chặn thì hotfix thành việc hằng ngày và không còn
  báo động được gì. Mỗi lần chấm Chặn, viết ra hậu quả cụ thể khớp một dòng ở cột dấu hiệu.
- **Vùng nâng cỡ** (`method/sizing.md` mục 2): lỗi chạm secret, xác thực hay phân quyền, thanh toán, hoặc
  dữ liệu bị đổi bất ngờ thì ghi `risk_tags`, `risk: high`, cỡ tối thiểu **lớn** — dù diff sửa chỉ một dòng.
- **Hotfix không bỏ Cổng 1.** Đường khẩn chỉ rút ngắn thời gian chờ, không bỏ bước duyệt: vẫn có SPEC/PLAN
  theo cỡ, vẫn có người duyệt trước khi chạm code.

## 4. Ghi sổ và tóm tắt

Mở một dòng `RQ-` mới ở sổ REQUESTS: mã lấy từ `next_id` rồi tăng `next_id` lên một. Kèm theo là bản tóm tắt cho người quyết, gồm đúng bốn phần theo thứ tự:

1. **Mức** (hoặc "mức tạm") và hậu quả làm nên mức đó.
2. **Tái hiện:** có hay chưa; nếu có thì trỏ tới các bước và file log.
3. **Vùng nghi ngờ** (chỉ là điểm bắt đầu để điều tra, không phải kết luận) và **đường xử lý** đã chọn.
4. **Hồi quy:** trước đây từng chạy đúng không; nếu có thì mốc (commit, bản phát hành) gần nhất còn đúng.

## 5. Bàn giao sang sửa

Sprint sửa mở ra theo đường đã chọn, rồi đi `debugging` (tìm gốc) → `tdd` (test hỏng trước, sửa sau).
Test hồi quy phải trải qua vòng **gỡ bản sửa → test hỏng → đặt lại → test đạt** (`method/evidence.md` mục 4),
và kết quả ghi vào `VR`. Người phân loại không tự sửa rồi tự chấm xong.

## 6. Điểm dừng

Dừng và hỏi người dùng (ghi `BR`) khi:

- để tái hiện phải đụng secret, hoặc phải dùng dữ liệu thật của người dùng (điều kiện dừng (b));
- lỗi chỉ tái hiện được bằng hành động không đảo ngược trên môi trường thật (điều kiện dừng (a));
- đã làm hết cách hợp lý mà vẫn không tái hiện được và lỗi đang mang mức Chặn tạm: người dùng cần quyết thêm
  công sức hay chấp nhận rủi ro.

## 7. Đầu ra

Bốn thứ: dòng `RQ-` ở sổ, mức (hay mức tạm), đường xử lý, và bằng chứng (đường tới các bước tái hiện và file
log). Thiếu một thứ thì chưa xong phân loại.

## 8. Lý lẽ ↔ sự thật

| Lý lẽ | Sự thật |
|---|---|
| "Sửa luôn cho nhanh, tái hiện tốn thời gian" | chưa thấy lỗi thì chưa biết sửa đúng chỗ; sửa theo đoán là thêm một lỗi |
| "Khách đã gắn nhãn khẩn rồi" | nhãn của người khác là thông tin, mức do hậu quả quyết |
| "Cứ đánh Chặn cho chắc" | thang mất nghĩa; hotfix thường xuyên là cả đội mệt vô ích |
| "Chỉ một dòng, khỏi cần duyệt" | một dòng ở xác thực hay thanh toán vẫn là cỡ lớn, vẫn Cổng 1 |
| "Log dài, dán hết vào cho đủ" | lưu file và trỏ đường; người đọc cần dòng then chốt |
| "Không tái hiện được thì chắc là hết rồi" | lỗi chập chờn vẫn là lỗi; mức tạm, ghi sổ, tiếp tục thu dữ liệu |

**Cờ đỏ — dừng, quay lại mục 1:** có đề xuất sửa trong bản tóm tắt · mức không kèm hậu quả · không có dòng
`RQ-` · mức Chặn mà không nêu được hậu quả · "chắc là do…" xuất hiện ở phần tái hiện.
