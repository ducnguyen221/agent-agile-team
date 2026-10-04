---
title: TypeScript and JavaScript standard — short rules
type: method
status: active
updated: 2026-10-04
---

<!-- Nguồn: affaan-m/ECC rules/typescript/{coding-style,patterns,security,testing}.md @ ef648e01 (MIT). Viết lại,
     giữ ý; bỏ `hooks.md` của nguồn (cấu hình runtime của nguồn); phần mẫu hook React chuyển sang `react.md`. -->

# Chuẩn TypeScript và JavaScript

> **Kết luận:** kiểu tường minh ở ranh giới công khai, `unknown` thay `any` cho dữ liệu ngoài, dữ liệu bất biến,
> lỗi bắt có kiểu và giữ nguyên nhân, đầu vào kiểm bằng schema, secret từ môi trường, không `console.log` trong
> code chạy thật, coverage **80 % code mới/sửa**. Bổ sung cho `common/`; React xem `react.md`.

## Kiểu

- Hàm export, tiện ích dùng chung và phương thức công khai của lớp có **kiểu tham số và kiểu trả về**; biến cục
  bộ để TypeScript tự suy khi hiển nhiên.
- Hình dạng đối tượng nội tuyến lặp lại thì tách thành kiểu có tên.
- `interface` cho hình dạng đối tượng có thể mở rộng hay cài đặt; `type` cho union, giao, tuple, mapped type và
  kiểu tiện ích.
- Ưu tiên union chuỗi hằng hơn `enum`, trừ khi cần `enum` để tương tác với bên ngoài.
- Tránh `any` trong code ứng dụng: dữ liệu ngoài hay không tin cậy là `unknown` rồi thu hẹp an toàn; kiểu phụ
  thuộc người gọi thì dùng generic.
- Props của component đặt bằng `interface` hay `type` có tên; kiểu hoá tường minh các callback; không dùng
  `React.FC` trừ khi có lý do cụ thể.
- Tệp `.js`/`.jsx` chưa chuyển được sang TypeScript thì dùng JSDoc khi kiểu làm rõ hơn, và giữ JSDoc khớp với
  hành vi chạy thật.

## Dữ liệu

- Cập nhật bằng cách trả đối tượng mới (toán tử spread), không sửa đối số; nhận `Readonly<T>` khi hàm không được
  đổi đầu vào.

## Lỗi và đầu vào

- `async`/`await` với `try`/`catch`; biến bắt lỗi là `unknown`, thu hẹp trước khi đọc (`instanceof Error`).
- Ném lại lỗi **giữ nguyên nhân** (`cause`) hay lỗi có kiểu của ứng dụng; không đổi lỗi gốc thành chuỗi mất ngữ
  cảnh; log chi tiết phía server (skill `error-handling`, `references/typescript-patterns.md`).
- Kiểm đầu vào bằng **schema** (Zod hay công cụ tương đương) ở biên và suy kiểu từ schema, không khai kiểu rồi
  tin mù.
- Không `console.log` trong code chạy thật; dùng thư viện log của dự án.

## Mẫu

- Hình dạng phản hồi API thống nhất cho cả dự án; phong bì lỗi theo skill `error-handling` và `api-design`.
- Truy cập dữ liệu qua giao diện kiểu repository để thay thế được khi test.
- Hook tuỳ biến của React: `react.md`.

## Bảo mật

- Secret từ biến môi trường, thiếu thì lỗi rõ lúc khởi động; không chuỗi khoá viết cứng.
- Danh mục chung: `common/security.md`; lượt bảo mật đầy đủ: skill `security-review`.

## Kiểm thử

- Test đơn vị và tích hợp theo `common/testing.md`.
- E2E cho các luồng người dùng trọng yếu bằng **Playwright**; cách chạy và thu bằng chứng: skill `web-qa`.
- Coverage **80 % code mới/sửa**.

## Xem thêm

Skill `error-handling`, `api-design`, `tdd`, `security-review`; chuẩn `common/`.
