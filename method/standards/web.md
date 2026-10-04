---
title: Web frontend standard — short rules
type: method
status: active
updated: 2026-10-04
---

<!-- Nguồn: affaan-m/ECC rules/web/{coding-style,design-quality,patterns,performance,security,testing}.md @
     ef648e01 (MIT). Viết lại, giữ ý; bỏ `hooks.md` của nguồn (cấu hình runtime của nguồn) và lời trỏ tới skill thiết
     kế riêng của nguồn. -->

# Chuẩn web (giao diện trình duyệt)

> **Kết luận:** giao diện web: HTML ngữ nghĩa trước, token thiết kế bằng biến CSS, chỉ animate thuộc tính do
> compositor xử lý, trạng thái tách theo loại, CSP và header bảo mật cho bản chạy thật, test theo thứ tự hình ảnh →
> trợ năng → hiệu năng → trình duyệt → responsive. Dành cho tầng HTML/CSS/trình duyệt; component React: `react.md`,
> ngôn ngữ: `typescript.md`. Coverage **80 % code mới/sửa**.

## Tổ chức và phong cách

- Tổ chức theo **tính năng hay bề mặt giao diện**, không theo loại tệp: thư mục cho từng khối (hero, phần cuộn,
  nút…), cạnh đó component, style, hook của khối đó; tách riêng `ui/` dùng chung, `hooks/`, `lib/`, `styles/`.
- Giá trị thiết kế (màu, chữ, khoảng cách, thời lượng, easing) khai báo **một lần** bằng biến CSS (token); không
  viết cứng lặp lại; cỡ chữ và khoảng cách co giãn bằng `clamp()`.
- HTML ngữ nghĩa trước: `header`, `nav` có `aria-label`, `main`, `section` có tiêu đề, `footer`; không chồng `div` khi đã
  có thẻ đúng nghĩa.
- Tên: component `PascalCase`, hook tiền tố `use`, lớp CSS `kebab-case` hay lớp tiện ích.
- Animate thuộc tính do compositor xử lý (`transform`, `opacity`, `clip-path`, `filter` có chừng mực); **không** animate
  thuộc tính kéo theo layout (`width`, `height`, `top`, `left`, `margin`, `padding`, `border`, `font-size`).

## Chất lượng thiết kế

- Giao diện chạy thật trông có chủ đích, đặc thù cho sản phẩm; không dừng ở mặc định của thư viện hay khuôn
  mẫu chung (lưới thẻ đều nhau không thứ bậc, hero gồm tiêu đề giữa trang cùng vệt màu chung, bố cục
  bảng điều khiển sáo rỗng, cỡ bo góc và bóng đổ giống nhau mọi chỗ, chữ mặc định không có lý do).
- Mỗi bề mặt đáng kể thể hiện ít nhất **bốn** trong: thứ bậc bằng tương phản cỡ chữ; nhịp khoảng cách có chủ ý;
  chiều sâu (chồng lớp, bóng, chuyển động); chữ có tính cách và cách ghép phông rõ; màu dùng theo nghĩa; trạng thái
  hover, focus, active có thiết kế; bố cục phá lưới khi hợp; chất liệu; chuyển động làm rõ luồng; trực quan hoá dữ
  liệu là một phần hệ thiết kế.
- Trước khi viết code giao diện: chọn **hướng phong cách cụ thể** (không "tối giản gọn gàng" chung chung), định
  bảng màu và cỡ chữ có chủ ý, gom vài tham chiếu thật. Không mặc định chế độ tối; chọn hướng sản phẩm cần.
- Hỗ trợ hai chủ đề thì cả hai đều có chủ ý.

## Mẫu

- Cụm điều khiển liên quan dùng compound component: cha giữ state, con dùng Context; render prop hay slot khi
  chia sẻ hành vi mà HTML thay đổi, giữ bàn phím, ARIA, focus ở lớp không giao diện.
- Container sở hữu dữ liệu và tác dụng phụ; component trình bày thuần, nhận props.
- **Tách các loại state:** máy chủ (TanStack Query, SWR, tRPC) · máy khách (Zustand, Jotai, signals) · URL (tham số
  tìm kiếm, đoạn route) · form (React Hook Form hay tương đương). Không sao chép state máy chủ vào kho máy khách;
  tính giá trị dẫn xuất thay vì lưu.
- **URL là state** cho thứ chia sẻ được: bộ lọc, thứ tự, phân trang, tab đang chọn, từ khoá tìm.
- Lấy dữ liệu: stale-while-revalidate bằng thư viện có sẵn; cập nhật lạc quan = chụp state, áp dụng, hoàn lại khi
  lỗi **kèm thông báo lỗi nhìn thấy**; tải song song dữ liệu độc lập, tránh thác request cha-con.

## Hiệu năng

- Mục tiêu Core Web Vitals theo ngưỡng "tốt" công bố của Google: **LCP dưới 2,5 s, INP dưới 200 ms, CLS dưới 0,1**;
  FCP dưới 1,5 s và TBT dưới 200 ms là mục tiêu tham khảo. Số đo ghi kèm lệnh, trang và điều kiện đo
  (Lighthouse hay công cụ tương đương), không ghi số không kèm cách đo.
- Ngân sách gói JS (nén gzip) khởi điểm: landing dưới 150 kB, trang ứng dụng dưới 300 kB, microsite dưới 80 kB; CSS
  dưới 30 kB, 50 kB, 15 kB tương ứng. Dự án chỉnh qua PLAN kèm lý do.
- Tải: CSS tới hạn trên màn đầu có thể nội tuyến; preload chỉ ảnh hero và phông chính; hoãn CSS/JS không tới hạn;
  `import()` động cho thư viện nặng.
- Ảnh: `width`/`height` tường minh; `loading="eager"` cùng `fetchpriority="high"` chỉ cho media hero, `lazy` cho phần
  dưới màn đầu; ưu tiên AVIF hay WebP kèm đường lùi; không phát ảnh nguồn lớn hơn nhiều kích thước hiển thị.
- Phông: tối đa hai họ trừ ngoại lệ rõ; `font-display: swap`; tách tập ký tự; preload chỉ kiểu cần nhất.
- Chuyển động: chỉ thuộc tính compositor; `will-change` hẹp rồi gỡ; CSS cho chuyển tiếp đơn giản;
  `requestAnimationFrame` hay thư viện có tiếng cho chuyển động JS; tránh xử lý scroll dồn dập — dùng
  `IntersectionObserver`.
- Trước khi báo xong: ảnh có kích thước, không tài nguyên chặn render vô ý, không nhảy layout vì nội dung động,
  script bên thứ ba `async`/`defer` và chỉ tải khi cần.

## Bảo mật

- Bản chạy thật luôn có **CSP**; dùng nonce theo yêu cầu cho script thay `'unsafe-inline'`; `object-src 'none'`,
  `base-uri 'self'`; nguồn cho phép chỉnh theo dự án, không chép nguyên một khối.
- XSS: không chèn HTML chưa làm sạch; tránh `innerHTML`/`dangerouslySetInnerHTML` trừ khi đã làm sạch bằng bộ làm
  sạch đã kiểm; escape giá trị mẫu động.
- Script bên thứ ba: tải bất đồng bộ, dùng SRI khi lấy từ CDN, rà soát định kỳ, tự lưu bản cho phụ thuộc trọng yếu
  khi tiện.
- Header: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy:
  strict-origin-when-cross-origin`, `Permissions-Policy` tắt máy ảnh, micro, định vị nếu không dùng.
- Form đổi trạng thái có chống CSRF, giới hạn tần suất; kiểm hợp lệ cả hai phía; chống lạm dụng nhẹ (honeypot)
  hơn là CAPTCHA nặng mặc định.
- Danh mục chung: `common/security.md`; React: `react.md`.

## Kiểm thử

Thứ tự ưu tiên:

1. **Hình ảnh:** chụp các điểm ngắt 320, 768, 1024, 1440; các trạng thái có nghĩa; cả hai chủ đề nếu có.
2. **Trợ năng:** kiểm tự động, điều hướng bàn phím, hành vi giảm chuyển động, độ tương phản.
3. **Hiệu năng:** Lighthouse hay tương đương trên các trang có nghĩa, giữ mục tiêu ở mục Hiệu năng.
4. **Đa trình duyệt:** tối thiểu Chrome, Firefox, Safari; kiểm cuộn, chuyển động, đường lùi.
5. **Responsive:** 320, 375, 768, 1024, 1440, 1920; không tràn ngang; thao tác chạm.

- E2E bằng Playwright, chờ xác định, không khẳng định bằng thời gian chờ cố định; thu bằng chứng theo skill
  `web-qa`.
- Test đơn vị cho tiện ích, biến đổi dữ liệu, hook tuỳ biến; với thành phần thiên về hình ảnh, hồi quy hình ảnh
  mang nhiều tín hiệu hơn khẳng định trên markup giòn. Hồi quy hình ảnh **bổ sung** cho coverage, không thay
  thế: ngưỡng **80 % code mới/sửa** vẫn giữ (`common/testing.md`).

## Xem thêm

`react.md`, `typescript.md`, `common/`; skill `web-qa`.
