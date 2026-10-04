# Test hồi quy khi mã do AI viết

> **Kết luận:** khi cùng một model viết mã rồi tự review, hai bước mang **cùng giả định**, nên điểm mù lọt qua
> cả hai. Chỉ test tự động bắt được chúng. Quy tắc: **test cho lỗi đã gặp**, viết ngay khi tìm ra lỗi (nếu được,
> trước khi sửa); **chạy test trước, review sau**; kiểm cả hai đường mã (sandbox và thật, cờ tính năng bật và
> tắt). Điều này bổ sung cho nguyên tắc lõi "người làm không tự chấm" (skill `code-review`,
> `verify-before-done`), không thay thế nó.

## 1. Vì sao review của cùng model không đủ

Chuỗi hay gặp: model sửa lỗi → model review bản sửa → nói "trông đúng" → lỗi còn nguyên. Ví dụ một lỗi
được sửa lần lượt: (1) thêm trường vào phản hồi nhưng quên thêm vào câu truy vấn; (2) thêm vào truy vấn thì
kiểu sinh tự động chưa có cột, build lỗi; (3) đổi sang chọn mọi cột, đường production chạy nhưng đường sandbox
vẫn thiếu trường. Mỗi vòng review đều bỏ sót, vì người review mang đúng giả định của người viết. Test chạy ở
lần đầu đã bắt được ngay.

## 2. Test không cần cơ sở dữ liệu (đường sandbox)

Dự án có đường giả lập (sandbox, mock) thì dùng nó để test API nhanh, không phụ thuộc cơ sở dữ liệu:

- Bộ chạy ở môi trường `node`, ép chế độ sandbox trong tệp thiết lập test (đặt biến môi trường giả và rỗng cho
  khoá kết nối), để không test nào chạm hệ thống thật.
- Viết một hàm trợ giúp tạo yêu cầu thử (URL, phương thức, thân, header) và một hàm đọc phản hồi (trạng thái +
  JSON), gọi thẳng hàm xử lý của route, không dựng server.
- Khai báo **hợp đồng phản hồi** thành danh sách trường bắt buộc, rồi khẳng định mỗi trường có mặt (kể cả khi
  giá trị `null`): trường thiếu và trường `null` là hai lỗi khác nhau.
- Giữ cả bộ test dưới khoảng một giây để chạy ở đầu mọi vòng kiểm.

## 3. Quy tắc viết test hồi quy

- **Test cho lỗi đã tìm thấy**, đặt tên theo lỗi nó chặn (mô tả hành vi, không mã nội bộ trần): ví dụ "phản hồi
  hồ sơ luôn có trường cài đặt thông báo, dù giá trị rỗng".
- Khẳng định **hình dạng phản hồi**, không khẳng định cách hiện thực.
- Mỗi lỗi sửa xong đề xuất một test; `bug-triage` ghi đường xử lý, test hồi quy là một phần của bản sửa.
- Độ phủ theo chuẩn dự án (mặc định 80 % với mã mới hoặc sửa) là **sàn**, không hạ. Test hồi quy là phần **thêm vào**
  ở nơi lỗi đã xuất hiện, không thay cho độ phủ.

## 4. Quy trình kiểm lỗi có test đi trước

1. Chạy bộ test và bước build/kiểm kiểu **trước** mọi việc review. Hỏng → đó là phát hiện cao nhất, tìm ra
   bằng máy, không cần phán đoán.
2. Chỉ khi cả hai qua mới review mã, với danh sách điểm mù đã biết: nhất quán giữa đường sandbox và đường thật;
   hình dạng phản hồi khớp điều giao diện mong đợi; câu truy vấn có đủ cột; lỗi có hoàn tác; cập nhật lạc quan
   có đua dữ liệu không.
3. Với mỗi lỗi sửa, thêm một test hồi quy; lần kiểm sau nó bắt được nếu bản sửa bị phá.

## 5. Bốn mẫu lỗi hay gặp và test bắt chúng

| Mẫu | Triệu chứng | Test bắt |
|---|---|---|
| **Lệch đường sandbox và đường thật** (gặp nhiều nhất) | thêm trường ở một nhánh, nhánh kia trả thiếu | khẳng định cùng một danh sách trường bắt buộc ở chế độ sandbox |
| **Thiếu cột trong truy vấn chọn** | trường mới có trong phản hồi nhưng luôn `undefined` vì truy vấn không chọn cột đó | khẳng định mọi trường bắt buộc có trong phản hồi |
| **Rò trạng thái lỗi** | bắt lỗi rồi báo lỗi nhưng dữ liệu cũ của tab trước vẫn hiện | khẳng định state liên quan được xoá khi lỗi |
| **Cập nhật lạc quan thiếu hoàn tác** | xoá khỏi giao diện trước, API hỏng thì mục mất khỏi UI mà vẫn còn trong cơ sở dữ liệu | khẳng định giao diện trở về trạng thái cũ khi API lỗi |

Một mẫu phụ: ép kiểu (`as`) che mất `null`: test khẳng định trường không `undefined`.

Ví dụ lệch đường: nhánh sandbox trả `{ id, email, name }` còn nhánh thật trả thêm cài đặt thông báo → sửa cả hai
nhánh trả cùng hình dạng (giá trị mặc định `null` ở sandbox) và test kiểm danh sách trường ở sandbox. Ví dụ hoàn
tác: lưu bản sao danh sách trước khi xoá lạc quan; nếu phản hồi không ổn thì trả lại bản sao và hiện thông báo lỗi.

## 6. Chiến lược: test ở nơi lỗi đã xuất hiện

```
Lỗi ở /api/profile      → viết test cho API hồ sơ
Lỗi ở /api/messages     → viết test cho API tin nhắn
/api/notifications chưa từng lỗi → ưu tiên thấp hơn, nhưng vẫn theo sàn độ phủ
```

Vì sao hợp với phát triển có AI: (1) AI hay lặp **cùng một loại lỗi**; (2) lỗi dồn ở vùng phức tạp (xác thực, nhiều đường
mã, quản lý state); (3) đã có test thì đúng lỗi đó **không tái diễn**; (4) số test tăng theo số lỗi, không phí công.

## 7. Nên và không nên

Nên: viết test ngay khi tìm ra lỗi; test hình dạng phản hồi chứ không hiện thực; chạy test đầu mỗi vòng kiểm; giữ test
nhanh; đặt tên theo lỗi nó chặn.
Không nên: tin review của AI thay cho test tự động; bỏ qua đường sandbox vì "chỉ là dữ liệu giả"; viết test tích hợp
nặng khi test đơn vị đủ; đuổi theo phần trăm độ phủ thay vì ngăn lỗi tái diễn (nhưng không hạ sàn độ phủ của dự án).
