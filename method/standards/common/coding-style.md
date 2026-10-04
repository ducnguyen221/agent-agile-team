---
title: Coding style — common rules for every language
type: method
status: active
updated: 2026-10-04
---

<!-- Nguồn: affaan-m/ECC rules/common/coding-style.md @ ef648e01 (MIT). Viết lại, giữ ý; bỏ nhãn mức kiểu nguồn
     và danh sách tự kiểm riêng (đã có trong skill `code-review` và `verify-before-done`). -->

# Phong cách code chung

> **Kết luận:** code đơn giản, nhỏ, tường minh: làm điều đơn giản nhất chạy đúng, tách khi lặp thật, không
> xây thứ chưa cần. Dữ liệu mặc định bất biến, lỗi không bị nuốt, đầu vào kiểm ở biên. Luật riêng của ngôn
> ngữ (`python.md`, `typescript.md`, `react.md`) đè luật chung khi ngôn ngữ có thành ngữ khác.

## Nguyên tắc

- **Đơn giản trước:** chọn cách đơn giản nhất mà thật sự chạy đúng; rõ ràng hơn khéo léo; chưa đo thì chưa tối ưu.
- **Không lặp có thật:** gom logic lặp vào một hàm hay tiện ích; chỉ trừu tượng hoá khi lặp đã xảy ra, không khi
  mới đoán sẽ lặp; tránh bản sao dán rồi lệch nhau.
- **Chưa cần thì chưa làm:** không dựng tính năng hay lớp trừu tượng cho nhu cầu chưa tồn tại; làm đơn giản, đợi
  áp lực thật rồi mới tách.

## Dữ liệu

- Mặc định **tạo bản mới thay vì sửa tại chỗ**: hàm trả giá trị mới, không đổi đối số của người gọi. Dữ liệu
  bất biến tránh tác dụng phụ ẩn, dễ gỡ lỗi, an toàn khi chạy đồng thời.
- Sửa tại chỗ chỉ khi ngôn ngữ hay hiệu năng đã đo đòi hỏi, và ghi lý do cạnh dòng đó.

## Tổ chức file

- Nhiều file nhỏ gắn kết hơn ít file lớn: một file một trách nhiệm, phụ thuộc lỏng.
- Điển hình 200–400 dòng; **800 dòng là trần mềm** cho file nguồn. Vượt thì tách module hoặc ghi lý do.
  File test, file sinh tự động và mã vendored được vượt khi vai trò của chúng biện minh.
- Tổ chức theo tính năng hay miền, không theo loại kỹ thuật.

## Lỗi và đầu vào

- Xử lý lỗi tường minh ở mọi tầng; người dùng thấy câu thân thiện, log phía server giữ ngữ cảnh chi tiết;
  **không bao giờ nuốt lỗi im lặng** (mẫu và phong bì lỗi: skill `error-handling`).
- Kiểm đầu vào **ở biên hệ thống**: mọi dữ liệu từ người dùng, API ngoài, file; dùng schema khi có công cụ;
  hỏng sớm với thông điệp rõ. Không tin dữ liệu đến từ ngoài.

## Đặt tên

- Tên nói được vật chứa gì hay hàm làm gì, không cần chú thích kèm.
- Tên boolean đọc như một khẳng định theo quy ước của ngôn ngữ.
- Hằng và kiểu nhìn khác giá trị thường, theo cách luật ngôn ngữ quy định; kiểu chữ hoa thường thuộc luật
  của ngôn ngữ hay gói đó, không đặt ở đây.

## Mùi code

- **Lồng sâu** (quá 4 tầng): trả về sớm thay vì chồng điều kiện.
- **Số ma thuật:** ngưỡng, độ trễ, giới hạn có nghĩa thì đặt hằng có tên.
- **Hàm dài** (quá 50 dòng): tách thành các phần một trách nhiệm.
- **Giá trị cứng:** cấu hình và bí mật đi qua cấu hình hay biến môi trường, không nằm trong code.
