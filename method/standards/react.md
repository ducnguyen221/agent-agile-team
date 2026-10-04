---
title: React standard — short rules
type: method
status: active
updated: 2026-10-04
---

<!-- Nguồn: affaan-m/ECC rules/react/{coding-style,patterns,security,testing,hooks}.md @ ef648e01 (MIT). Viết lại,
     giữ ý. `hooks.md` của thư mục react nói về hook React (`useState`, `useEffect`…), không phải hook runtime của
     nguồn, nên phần đó được giữ ở mục "Hook". Ngưỡng coverage theo tầng của nguồn bỏ, dùng một ngưỡng chung. -->

# Chuẩn React

> **Kết luận:** component hàm, props có kiểu, state đặt thấp nhất có thể, dữ liệu dẫn xuất tính khi render chứ
> không đồng bộ bằng effect, mọi dữ liệu ra HTML đi qua escape của React, test theo hành vi người dùng thấy.
> Bổ sung cho `typescript.md` và `common/`; coverage **80 % code mới/sửa**.

## Tệp và tên

- `.tsx` cho tệp có JSX; `.ts` cho logic thuần, hook không JSX, kiểu, tiện ích; `.test.tsx` / `.test.ts` đặt cạnh
  tệp nguồn. `.jsx` chỉ khi dự án cố ý không dùng TypeScript — mỗi tệp React mới không kiểu bị gắn ghi chú khi review.
- Component: `PascalCase` cho cả tên và tệp; hook: `useCamelCase` (tệp theo quy ước của dự án); context:
  `<Miền>Context`, `<Miền>Provider`, `use<Miền>`.
- Hàm xử lý sự kiện trong component là `handleClick`, prop nhận nó là `onClick`; prop boolean là `isLoading`,
  `hasError`, `canSubmit`, không `loading` hay `error` trơn.

## Component

- Hàm, không dùng lớp trong code mới; lớp cũ chuyển sang hàm khi sửa lớn. Ngoại lệ duy nhất: Error Boundary (lớp,
  hoặc bọc bằng thư viện như `react-error-boundary`).
- Props khai bằng `type Props = {…}`; `interface` chỉ khi cần mở rộng qua khai báo hợp nhất hay là điểm mở rộng
  công khai. Phá props ngay trong danh sách tham số.
- JSX: thẻ không con thì tự đóng; dùng fragment thay `div` bọc thừa; logic nhiều dòng tính ra biến phía trên
  `return`, không nhét vào JSX; điều kiện: `&&` cho boolean, toán tử ba ngôi cho hai nhánh, trả về sớm cho điều
  kiện bảo vệ.
- Import: React trước, rồi thư viện ngoài, rồi đường tuyệt đối của dự án, rồi tương đối; kiểu thì `import type`.
- Mỗi component một thư mục khi có style và test đi kèm (`index.ts` chỉ re-export); component trình bày nhỏ thì
  để một tệp.

## State và dữ liệu

- Thứ tự đặt state: một component → `useState` trong nó; cha và vài con → nâng lên tổ tiên chung; nhánh xa nhau
  mà **ít đổi** (giao diện, đăng nhập, ngôn ngữ) → Context; **đổi liên tục** và dùng chung → kho ngoài (Zustand,
  Jotai, Redux Toolkit); dữ liệu từ máy chủ → thư viện state máy chủ (TanStack Query, SWR, fetch của RSC), không
  coi là state ứng dụng.
- **Không nhân đôi state tính được**: tính khi render. Context cho giá trị đổi liên tục làm mọi consumer render lại.
- Lấy dữ liệu: không `fetch` trong `useEffect` khi đã có thư viện cache (đua, không cache, không thử lại); `fetch`
  trong effect chỉ cho việc bắn-rồi-quên một lần.
- Container sở hữu dữ liệu, state và tác dụng phụ; component trình bày chỉ nhận props và vẽ, không gọi dịch vụ.
- Form: input không kiểm soát với form action khi chỉ có bước gửi rõ ràng; input có kiểm soát khi giá trị điều
  khiển phần giao diện khác hay cần kiểm tra thời gian thực; form phức tạp dùng thư viện.
- Danh sách: `key` ổn định và duy nhất trong anh em; **không dùng chỉ số mảng** làm `key` cho danh sách có thể
  đổi thứ tự, chèn, xoá.
- Gộp bằng composition: `children`, render prop, truyền kiểu component; không kế thừa lớp để đặc biệt hoá. Cụm
  điều khiển liên quan (Tabs, Menu) dùng compound component chia sẻ qua Context.
- Cổng (`createPortal`) cho modal, tooltip, toast cần thoát khỏi `overflow` hay `z-index` của cha.
- React 19: `ref` là prop thường, không cần `forwardRef`; mã React 18 vẫn cần `forwardRef`.

## Hook

- **Luật hook:** chỉ ở cấp cao nhất của component hàm hay hook khác; không trong vòng lặp, điều kiện, hàm lồng,
  sau `return` sớm; thứ tự gọi giống nhau ở mọi lần render. Bật `react-hooks/rules-of-hooks` mức lỗi.
- **`useEffect` chỉ để đồng bộ với hệ thống bên ngoài** (đăng ký, API trình duyệt, thư viện thứ ba). Không dùng
  cho state dẫn xuất, biến đổi dữ liệu để vẽ, đặt lại state khi prop đổi (dùng `key` ở cha), báo cha khi state đổi
  (gọi callback ở handler).
- Mảng phụ thuộc liệt kê đủ mọi giá trị phản ứng dùng trong effect; bật `react-hooks/exhaustive-deps`, tắt thì
  phải có chú thích lý do; mảng quá dài là dấu hiệu effect làm quá nhiều.
- Mọi đăng ký, timer, listener, request đang bay đều **dọn** khi unmount hay đổi phụ thuộc (`AbortController`,
  `clearInterval`).
- Mặc định **không memo hoá**; `useMemo`/`useCallback` khi giá trị truyền cho con bọc `React.memo` mà danh tính
  quan trọng, khi là phụ thuộc của hook khác, hoặc khi phép tính đã đo là đắt.
- Hook tuỳ biến khi cùng một chuỗi hook xuất hiện ở từ hai component, có mục đích gọi tên được, hay cần test
  riêng; không tách khi chỉ một nơi gọi hay chỉ là `useState` đổi tên.
- `useState` với hàm khởi tạo khi tính đắt; dùng hàm cập nhật khi state mới phụ thuộc state cũ; `useReducer` khi
  chuyển trạng thái có điều kiện hay từ ba giá trị liên quan. `useRef` cho DOM và giá trị khả biến không gây vẽ lại;
  không đọc hay ghi `ref.current` lúc render. `useSyncExternalStore` để đăng ký kho ngoài.

## Ranh giới máy chủ và máy khách (RSC, Next.js App Router)

- Tệp mới mặc định là Server Component; chỉ thêm `"use client"` khi dùng state, effect, ref, API trình duyệt hay
  handler sự kiện; chỉ thị đặt dòng 1, trước import.
- Component máy khách không import component máy chủ (nhận qua `children` hay vị trí có tên); không import tệp
  máy khách vào tệp `"use server"`; không re-export mã chỉ-máy-chủ qua module máy khách.
- Module nhạy cảm đánh dấu `import "server-only"` để bundler báo lỗi nếu máy khách import.
- Mỗi ranh giới Suspense có một Error Boundary phía trên; đặt Suspense gần chỗ cần dữ liệu, không ở gốc route.
- Server Actions, Route Handlers, Middleware: theo tài liệu chính thức của Next.js; React Native ngoài phạm vi.

## Bảo mật

- `dangerouslySetInnerHTML` với dữ liệu người dùng chưa làm sạch là lỗ hổng mức **Chặn**. Cách thay: hiển thị như
  văn bản, markdown qua thư viện làm sạch, hay HTML thô đã qua `DOMPurify` **tại chính chỗ dùng**; kiểm từng chỗ:
  nguồn nào, đã làm sạch chưa, bộ làm sạch cho phép thẻ theo danh sách trắng.
- URL: kiểm lược đồ (chỉ `http:`, `https:`, `mailto:`) trước khi gán vào `href`, `src`; `javascript:` và `data:` chạy
  được mã. `target="_blank"` luôn kèm `rel="noopener noreferrer"`, không dựa vào mặc định trình duyệt.
- Server Action có mức tin cậy như endpoint công khai: kiểm đầu vào bằng schema, xác thực và phân quyền **trong
  action** trên đúng bản ghi, giới hạn tần suất.
- Biến môi trường có tiền tố công khai (`NEXT_PUBLIC_*`, `VITE_*`, `REACT_APP_*`) bị gói vào bundle: coi là công
  khai, không để khoá bí mật ở đó; mỗi PR chạm biến môi trường tự hỏi "chuỗi này lộ ra có sao không".
- Không lưu phiên trong `localStorage` (XSS đọc được) — dùng cookie `httpOnly`, `secure`. Che giao diện không phải
  kiểm quyền; API phải kiểm. Cookie phiên cần CSRF token hay `SameSite`.
- CSP đặt phía máy chủ, tránh `unsafe-inline` và `unsafe-eval` ở `script-src`, dùng nonce theo yêu cầu cho script
  nội tuyến; `style-src 'unsafe-inline'` cho CSS-in-JS thì ghi rõ đánh đổi.
- Không rải JSON không tin cậy vào state bằng spread (ô nhiễm prototype); parse bằng schema hay lọc khoá.
- SSR: giá trị trong JSX đã được escape, còn HTML tự ghép quanh đầu ra phải escape hay làm sạch.
- Thư viện UI thứ ba: chạy audit gói trước khi thêm, kiểm chúng không dùng `dangerouslySetInnerHTML` lên đầu vào
  của mình, ghim phiên bản; bản build chạy thật không công khai source map (hoặc tải lên công cụ lỗi rồi gỡ).
- Danh mục chung: `common/security.md`; lượt đầy đủ: skill `security-review`.

## Kiểm thử

- **React Testing Library** cho component, **Vitest** cho dự án Vite mới, Jest cho Next.js hay CRA; một bộ chạy
  test component cho mỗi dự án, không trộn.
- Kiểm thứ người dùng thấy và làm, không kiểm chi tiết cài đặt: truy vấn theo vai trò trước, rồi nhãn, rồi chữ;
  `data-testid` là đường lùi cuối. Không khẳng định state nội bộ, props truyền cho con, số lần render.
- Dùng `userEvent` thay `fireEvent`, luôn `await`, gọi `userEvent.setup()` một lần mỗi test.
- Nội dung bất đồng bộ: `findBy*` hay `waitFor`; không `setTimeout` rồi khẳng định.
- Mạng: **MSW** ở tầng mạng; ghi đè từng test bằng `server.use(...)`, đặt lại sau mỗi test.
- Không snapshot cho component (giòn, bị duyệt qua loa); hồi quy hình ảnh dùng ảnh chụp thật của Playwright hay công
  cụ tương đương.
- Bọc provider một lần trong tiện ích test dùng chung; test hook bằng `renderHook` và `act`, qua API công khai của hook.
- Có khẳng định trợ năng bằng axe trong test component; layout thật, cuộn, kéo thả, hoạt ảnh thì cần trình duyệt
  thật (Playwright hay E2E), không mong JSDOM làm.
- Không mock hook của React hay component con theo mặc định; không bỏ qua cảnh báo `act()` — đó là lỗi thật.
- Coverage: ngưỡng chung **80 % code mới/sửa** (`common/testing.md`); không đặt ngưỡng riêng theo tầng.

## Xem thêm

`typescript.md`, `web.md`, `common/`; skill `react` (component, hook, test), `frontend` (build, tải trang),
`e2e-testing`, `web-qa`, `security-review`.
