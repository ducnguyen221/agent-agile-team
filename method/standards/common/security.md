---
title: Security — common rules for every language
type: method
status: active
updated: 2026-10-04
---

<!-- Nguồn: affaan-m/ECC rules/common/security.md @ ef648e01 (MIT). Viết lại, giữ ý; bỏ lời gọi agent riêng của
     nguồn và nhãn mức kiểu nguồn; quy trình phản ứng nối với điều kiện dừng của luật lõi. -->

# Bảo mật chung

> **Kết luận:** trước mỗi commit phải qua danh mục kiểm bảo mật ngắn dưới đây; secret không nằm trong code;
> thấy lỗ hổng thì dừng, đánh giá mức, sửa, xoay vòng khoá lộ. Chạm bí mật hay bảo mật là điều kiện dừng
> của luật lõi — ghi một mục chặn (`BR`) rồi hỏi người dùng. Danh mục chi tiết từng mục: skill `security-review`.

## Danh mục trước mỗi commit

- Không secret viết cứng (khoá API, mật khẩu, token).
- Mọi đầu vào người dùng đã được kiểm.
- Chống SQL injection: truy vấn tham số hoá, không ghép chuỗi.
- Chống XSS: HTML đã làm sạch, không chèn dữ liệu thô vào trang.
- Chống CSRF khi dùng phiên bằng cookie.
- Xác thực và phân quyền đã kiểm trên từng điểm vào, không chỉ ở giao diện.
- Giới hạn tần suất trên mọi endpoint.
- Thông điệp lỗi không lộ dữ liệu nhạy cảm.

## Quản lý secret

- Không viết secret vào mã nguồn; dùng biến môi trường hay kho secret; repo chỉ có `.env.example`.
- Kiểm khi khởi động rằng secret bắt buộc đã có, thiếu thì dừng với lỗi rõ.
- Secret nghi đã lộ (vào diff, log, đầu ra) thì **xoay vòng** ngay và báo người dùng; không lặp lại giá trị
  trong báo cáo.

## Khi thấy vấn đề bảo mật

1. Dừng việc đang làm.
2. Đánh giá mức theo thang chung (`method/severity.md`); lỗ hổng hay rò rỉ dữ liệu là **Chặn**.
3. Chạm vùng bảo mật thì nâng việc lên cỡ lớn và chạy lượt bảo mật: skill `security-review` cùng agent
   `security-reviewer`; muốn soát cả repo thì skill `security-audit`.
4. Sửa mức Chặn trước khi làm tiếp; xoay vòng secret đã lộ.
5. Rà phần còn lại của code tìm lỗi cùng kiểu.
