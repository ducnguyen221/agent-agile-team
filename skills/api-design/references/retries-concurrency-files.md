# API: thử lại an toàn, khoá lạc quan, yêu cầu có điều kiện, tệp

> **Kết luận:** bốn chỗ hợp đồng API hay thiếu: (1) client thử lại `POST` khi mất mạng thì tạo trùng, nên endpoint tạo cần
> **`Idempotency-Key`**; (2) hai người sửa cùng bản ghi thì người sau ghi đè người trước, nên endpoint sửa cần **`ETag` +
> `If-Match`** (không khớp → `412`, thiếu điều kiện khi bắt buộc → `428`); (3) client thăm dò liên tục dùng **`If-None-Match`** để
> nhận `304` rỗng thay vì cả thân; (4) upload và tải tệp có luật riêng về kích thước (`413`), loại (`415`), cách truyền
> (multipart, URL ký sẵn) và **kiểm quyền lại ở lúc tải**.

Nguồn: RFC 9110 (ngữ nghĩa HTTP: `ETag`, `If-Match`, `If-None-Match`, `304`, `412`, `413`, `415`), RFC 6585 (`428`, `429`), RFC 7578
(`multipart/form-data`), bản nháp IETF `draft-ietf-httpapi-idempotency-key-header` (đã hết hạn, **chưa là tiêu chuẩn**; cách làm quen thuộc
của các cổng thanh toán), tài liệu OWASP "File Upload Cheat Sheet", tài liệu URL ký sẵn của dịch vụ lưu trữ đối tượng.

## 1. Thử lại an toàn cho `POST`: `Idempotency-Key`

`POST` không idempotent (mục 2 của `SKILL.md`): client hết thời gian chờ không biết đơn đã tạo chưa, thử lại thì có thể tạo đơn thứ hai.
Chữa bằng khoá chống trùng do **client sinh** cho mỗi *ý định* (không mỗi lần thử):

```
POST /api/v1/orders
Idempotency-Key: 0b8c6a3e-5a1f-4b6e-9d2a-7c1f3e8a9b10     (UUID ngẫu nhiên, một khoá cho một đơn)
```

Phía server:

1. Lần đầu thấy khoá: lưu `(khoá, người gọi, băm của thân yêu cầu, trạng thái "đang xử lý")` rồi xử lý.
2. Xong: lưu **mã trạng thái và thân phản hồi** của lần đầu với khoá đó (kể cả lỗi nghiệp vụ `4xx` đã chốt).
3. Lần gọi lặp cùng khoá và **cùng thân**: trả lại đúng phản hồi đã lưu (thường kèm header cho biết là bản phát lại), không chạy lại.
4. Cùng khoá, **thân khác**: lỗi (thường `422`), vì đó là lạm dụng khoá.
5. Cùng khoá khi lần đầu **còn đang xử lý**: `409` kèm `Retry-After`, không chạy song song.
6. Khoá hết hạn sau một khoảng (ví dụ 24 giờ) rồi dọn; khoá gắn với **người gọi** để người này không phát lại phản hồi của người khác.

- Khoá phải được kiểm và lưu **cùng giao dịch** với việc tạo (hoặc dùng ràng buộc unique trên khoá) để hai yêu cầu đua nhau không cùng qua
  (`postgres`: ràng buộc là chốt cuối).
- Thiếu khoá ở endpoint **bắt buộc** có khoá: `400` kèm chỉ dẫn. Endpoint tạo tiền, đơn hàng, gửi tin nhắn nên bắt buộc; endpoint
  ít hậu quả có thể tuỳ chọn. `PUT` và `DELETE` đã idempotent theo ngữ nghĩa nên không cần khoá.
- Tài liệu API ghi: header, thời hạn khoá, hành vi theo từng tình huống ở trên. Bản nháp IETF chưa là tiêu chuẩn: ghi rõ đây là quy ước
  của API mình, đối chiếu bản nháp hiện hành khi cần.

## 2. Khoá lạc quan: `ETag` + `If-Match`

Vấn đề "cập nhật bị mất": A và B cùng đọc bản ghi, A lưu, B lưu đè mà không biết. Cách chữa không khoá dòng lâu: mỗi bản có **phiên bản**.

```
GET /api/v1/customers/42        → 200, ETag: "v7"           (hoặc trường version trong thân)
PUT /api/v1/customers/42
If-Match: "v7"                   → khớp  : 200/204, ETag mới "v8"
                                  → lệch : 412 Precondition Failed (bản đã đổi, client đọc lại rồi gộp)
PUT /api/v1/customers/42        (không If-Match, endpoint bắt buộc điều kiện)
                                 → 428 Precondition Required
```

- `ETag` là chuỗi đặc trưng cho **phiên bản** của tài nguyên: số phiên bản tăng dần (`"v7"`), băm của nội dung, hoặc `updated_at` đủ
  độ phân giải. `If-Match` dùng so sánh **mạnh** (khớp từng byte của thẻ).
- Phía CSDL, kiểm và ghi trong **một câu** để không đua: `UPDATE customers SET ..., version = version + 1 WHERE id = $1 AND version = $2`;
  0 dòng bị đổi → `412` (hoặc `409` nếu hợp đồng của API dùng cột `version` trong thân thay cho header). Chọn **một** cách và ghi vào tài liệu.
- Mã lỗi: `412` khi điều kiện sai (không khớp); `428` khi server **yêu cầu** có điều kiện mà client bỏ qua (RFC 6585); `409` dành cho xung đột trạng thái
  nghiệp vụ khác (trùng khoá, trạng thái không cho phép), không lẫn với phiên bản lệch.
- Phản hồi `412`/`409` nên mang bản hiện tại (hoặc đường để lấy) để client gộp thay đổi; giao diện hiện "bản này đã được sửa bởi người khác".
- Dùng cho tài nguyên **nhiều người sửa**; tài nguyên một người sửa thì không cần. `PATCH` cũng nên nhận `If-Match`.
- Khi tạo chỉ-nếu-chưa-có: `If-None-Match: *` trên `PUT` (tạo, không ghi đè bản đã tồn tại).

## 3. Yêu cầu có điều kiện cho client thăm dò (`If-None-Match`, `304`)

Client hỏi lại danh sách mỗi vài giây mà dữ liệu hiếm đổi:

```
GET /api/v1/orders?status=open
If-None-Match: "abc123"
→ 304 Not Modified   (không thân, server tiết kiệm băng thông và serialize; vẫn tính vào rate limit)
→ 200 + ETag: "def456" + thân mới (khi đã đổi)
```

- Server tính `ETag` từ trạng thái dữ liệu (băm kết quả, hoặc mốc `max(updated_at)` + số dòng). Tính `ETag` rẻ hơn dựng cả thân mới có lợi.
- `304` thường **vẫn trừ vào hạn mức rate limit** nếu bạn đếm theo yêu cầu: nói rõ trong tài liệu, hoặc đặt hạn mức riêng cho yêu cầu có điều kiện.
  Hạn mức vẫn trả `429` + `Retry-After` như `references/auth-ratelimit-versioning.md` mục 3.
- Thăm dò tốt hơn: `Cache-Control: max-age`/`stale-while-revalidate` cho dữ liệu cache được, hoặc đẩy sự kiện (SSE, webhook) thay vì thăm dò.
  Đừng cache phản hồi có dữ liệu riêng của người dùng ở bộ nhớ đệm chung (`Cache-Control: private`).

## 4. Upload và tải tệp

**Cách truyền:**

| Cách | Khi nào | Đánh đổi |
|---|---|---|
| `multipart/form-data` (một yêu cầu: tệp + trường) | tệp vừa và nhỏ, qua API của mình | chuẩn, dễ; tệp đi qua server của mình (tốn băng thông, bộ nhớ nếu không stream) |
| thân nhị phân thô (`PUT /files/:id` kèm `Content-Type`) | một tệp mỗi yêu cầu | gọn; metadata đi đường khác |
| **URL ký sẵn** (presigned URL) tới kho đối tượng | tệp lớn | client tải thẳng lên kho, API chỉ cấp URL ngắn hạn + ghi metadata; không qua server của mình |
| base64 trong JSON | chỉ tệp rất nhỏ (ảnh đại diện nhỏ) | phình thân khoảng một phần ba, tốn bộ nhớ khi giải mã; tránh cho tệp lớn |

Luồng URL ký sẵn: (1) client gọi `POST /api/v1/uploads` khai tên, loại, kích thước → server kiểm quyền, **giới hạn kích thước và loại ở phía
cấp URL**, trả `{ upload_url, file_id, expires_in }`; (2) client `PUT` tệp lên `upload_url`; (3) client (hoặc sự kiện của kho) báo xong, server kiểm
tệp thật rồi đánh dấu `ready`. Tệp chưa `ready` không được dùng.

**Giới hạn và mã lỗi:**
- `413 Content Too Large` khi vượt kích thước cho phép: đặt giới hạn ở **cả** cổng/proxy lẫn ứng dụng, và đếm byte khi **stream** (đừng tin `Content-Length`).
  Ghi kích thước tối đa vào tài liệu và trả `code` riêng (`file_too_large`) kèm giới hạn.
- `415 Unsupported Media Type` khi loại không được phép: dùng **danh sách cho phép**; kiểm loại thật từ nội dung (chữ ký đầu tệp), không tin
  `Content-Type` hay đuôi tệp client gửi. `400` cho multipart hỏng, `422` cho trường metadata sai.
- Tệp tạo `201` kèm `Location` của tài nguyên tệp.

**Bảo mật (OWASP File Upload):** đổi tên tệp thành định danh ngẫu nhiên phía server (tên gốc chỉ lưu làm metadata); lưu **ngoài** thư mục phục vụ web
hoặc ở kho đối tượng riêng tư; quét mã độc nếu nhận tệp từ người lạ; không thực thi/biên dịch nội dung tải lên; chặn đường dẫn (`..`) và tệp nén bom.
Ảnh/SVG phục vụ lại cần header an toàn (`X-Content-Type-Options: nosniff`, SVG không chạy script).

**Tải xuống:**
- **Kiểm quyền lại ở lúc tải**, mỗi lần: có quyền lúc upload không có nghĩa có quyền xem sau này. Tải qua API của mình thì kiểm tại đó; qua URL ký
  sẵn thì URL sinh **sau** khi kiểm quyền, hết hạn ngắn (vài phút), một tệp, một lần dùng nếu có thể, và không ghi vào log/nhật ký có URL đầy đủ.
- Phục vụ tệp có thể bị trình duyệt thực thi: `Content-Disposition: attachment; filename="..."` và `Content-Type` đúng; không lấy tên tệp từ đầu vào không lọc.
- Hỗ trợ tải một phần (`Range`) cho tệp lớn nếu cần tiếp tục tải dở.
- Dọn tệp mồ côi (đã upload nhưng không bao giờ `ready`, hoặc bản ghi đã xoá) bằng việc nền định kỳ.
