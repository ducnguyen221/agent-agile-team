---
name: react
description: Use when writing, changing or reviewing React function components, hooks, state placement, forms, Suspense or error boundaries, or component tests (React Testing Library, Vitest, MSW). Not for build tooling, routing or bundle loading (that is `frontend`) and not for browser-driven user flows (that is `e2e-testing`).
metadata:
  group: technique
  kind: reference
  roles: [implementer, qa]
source: [affaan-m/ECC skills/react-patterns/SKILL.md, affaan-m/ECC skills/react-testing/SKILL.md]
source_sha: [ef648e01899ba3e8dc6371642deaaf64b4477775, ef648e01899ba3e8dc6371642deaaf64b4477775]
license: [MIT, MIT]
rewrite_before_public: false
---

# React: component, hook, test component

> **Kết luận:** render là hàm thuần của props và state; tác dụng phụ nằm ngoài render; giá trị suy ra được thì
> **tính lúc render**, không lưu thành state; đặt state ở nơi thấp nhất đủ dùng; dữ liệu từ server dùng thư
> viện state-server, không `useEffect` + `fetch`. Test component **như người dùng**: truy vấn theo vai/nhãn,
> mock mạng ở tầng mạng (MSW), không soi chi tiết hiện thực. Build, routing, tải bundle: skill `frontend`.

ASSUMPTION stack: React 18 + TypeScript. Phần React 19 hay Server Component ghi rõ ở mục 8; dự án dùng bản
nào thì theo tài liệu bản đó.

## 1. Nguyên tắc nền

- **Render thuần.** Cùng props và state thì cùng JSX. Không gọi mạng, không ghi biến ngoài, không đọc đồng
  hồ hay số ngẫu nhiên trong thân component.
- **Suy ra, đừng lưu.** Tổng tiền từ danh sách mặt hàng là biểu thức lúc render. Lưu nó vào state rồi đồng
  bộ bằng `useEffect` thêm một vòng render, dễ lệch và che mất luồng dữ liệu.
- **Tác dụng phụ** (mạng, đăng ký sự kiện, bộ đếm giờ, ghi DOM) nằm trong trình xử lý sự kiện hoặc
  `useEffect`, không bao giờ trong thân render.
- **Ghép, không kế thừa.** Dùng `children`, prop nhận component hoặc hook để tái dùng.

## 2. Hook: kỷ luật

- Gọi ở cấp cao nhất, không trong điều kiện hay vòng lặp.
- Mọi đăng ký, bộ đếm giờ, listener phải có hàm dọn trong `useEffect`.
- State mới phụ thuộc state cũ thì dùng dạng hàm: `setCount(c => c + 1)`.
- Mảng phụ thuộc đủ và đúng; muốn "bỏ bớt cho khỏi chạy lại" là dấu hiệu thiết kế sai, không phải chỗ để tắt cảnh báo.
- **Mặc định không memo.** `useMemo`, `useCallback`, `React.memo` chỉ thêm khi profiler hoặc chuỗi phụ thuộc
  chứng minh cần; `React.memo` chỉ có lợi khi component render nặng, render thường xuyên và props hay giữ nguyên.
- Tách custom hook khi cùng một dãy hook xuất hiện ở từ hai component trở lên.

## 3. Vị trí state

| Trường hợp | Đặt ở |
|---|---|
| một component dùng | `useState` trong nó |
| cha và vài con cháu dùng | nâng lên tổ tiên chung gần nhất |
| nhánh xa nhau, đọc ít đổi (theme, người dùng, ngôn ngữ) | Context |
| cập nhật dồn dập, chia sẻ rộng | store ngoài (Zustand, Jotai, Redux Toolkit), dùng `useSyncExternalStore` hoặc thư viện đã làm sẵn |
| bản sao dữ liệu server | thư viện state-server (TanStack Query, SWR) |

Phần lớn trang không cần Context hay store toàn cục: chờ đến khi việc nâng state lặp lại gây đau mới trừu
tượng hoá. Một Context mỗi mối quan tâm, để đổi theme không render lại phần dùng người dùng.
Cách chọn và dựng store ở tầng ứng dụng: skill `frontend`.

## 4. Lấy dữ liệu

Tránh `useEffect` + `fetch` cho dữ liệu ứng dụng: thiếu cache, thử lại, huỷ khi đua yêu cầu, và không nối
được Suspense. Cần cache + đột biến + vô hiệu hoá → TanStack Query; cache nhẹ + tự làm mới → SWR; thời gian
thực → SSE hoặc WebSocket; bắn-và-quên một lần → `fetch` trong trình xử lý sự kiện.

## 5. Form

- Đầu vào **kiểm soát** (controlled) khi giá trị chi phối UI khác, định dạng theo từng phím hoặc kiểm tra tức thời.
- Form nhiều bước, mảng trường động, kiểm tra chéo trường: dùng thư viện (React Hook Form, TanStack Form);
  tự dựng state form quá mức đơn giản là bẫy bảo trì.
- Kiểm tra **hai phía**: giản đồ (Zod) ở client để báo lỗi sớm, server vẫn kiểm lại. Lỗi hiện bằng
  `role="alert"` hoặc liên kết `aria-describedby`, nút gửi khoá trong lúc chờ.

## 6. Suspense và error boundary

- Đặt Suspense **sát chỗ lấy dữ liệu**, không ở gốc route, để nội dung hiện dần.
- Error boundary vẫn là API dạng class (dùng `react-error-boundary` cho gọn). Nó bắt lỗi ném lúc render,
  vòng đời, constructor của con; **không** bắt lỗi trong trình xử lý sự kiện hay mã bất đồng bộ: những chỗ đó tự `catch`.
- Cặp chuẩn: `ErrorBoundary` bọc ngoài, `Suspense` bọc trong, mỗi cặp một vùng giao diện độc lập.

## 7. Ghép thành phần, danh sách, tiếp cận

- Mẫu ghép: khe `children`; khe có tên (`header`, `sidebar` truyền như prop); **compound component** chia
  state qua Context (`Tabs` + `Tabs.Trigger`); render prop khi cha phải đưa tham số cho phần con. Hook trả
  cùng hình dạng dữ liệu thường gọn hơn render prop.
- Danh sách: `key` ổn định (id từ dữ liệu, không phải chỉ số mảng); ảo hoá (`@tanstack/react-virtual`,
  `react-window`) khi số dòng thấy được vượt chừng 50 và dòng không nhẹ.
- Tránh thác render: hạ state xuống thấp thay vì nâng lên; tách Context theo mối quan tâm.
- **Tiếp cận trước:** dùng thẻ ngữ nghĩa (`button`, `a`, `nav`, `main`) trước khi thêm `role`; mọi thứ bấm được
  phải tới được bằng bàn phím; ô nhập có nhãn (`label htmlFor` hoặc `aria-label`); quản lý focus khi đổi route
  và khi mở/đóng hộp thoại. Danh mục đầy đủ: `roles/verifier/specialists/frontend.md` mục 9.

## 8. Phiên bản và phạm vi

- **React 19:** `useActionState`, `form action`, `useOptimistic` thay một phần mẫu form và cập nhật lạc quan.
  Dự án đang ở 18 thì không dùng; đổi bản là quyết định kiến trúc (skill `adr`).
- **Server Component** (Next.js App Router): server → client chỉ truyền props tuần tự hoá được hoặc `children`;
  không `import` Server Component vào file Client Component. Chi tiết Next.js, Remix, React Native: theo tài
  liệu khung, ngoài skill này.
- Mẫu ở đây không phụ thuộc bộ định tuyến nào (routing: skill `frontend`).

## 9. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Viết hoặc sửa test component, hook, trang; MSW; axe; thứ tự truy vấn; snapshot nên hay không; chọn RTL / trình duyệt thật; bộ lệnh test | `references/testing.md` |

Liên quan: `frontend` (build Vite, routing, state ứng dụng, hiệu năng tải), `e2e-testing` (luồng nhiều trang
bằng Playwright), `tdd` (chu trình test trước), `web-qa` (QA kiểm bằng trình duyệt), `typescript-reviewer` và
`react-reviewer` khi có.

## 10. Danh mục kiểm khi viết hoặc review component

- [ ] giá trị suy ra được không bị lưu thành state
- [ ] mỗi `useEffect` có hàm dọn nếu đăng ký gì đó; mảng phụ thuộc đủ
- [ ] không `useEffect` + `fetch` cho dữ liệu ứng dụng
- [ ] state ở nơi thấp nhất đủ dùng; không Context hay store khi chưa cần
- [ ] có trạng thái rỗng, đang tải, lỗi (không chỉ nhánh thành công)
- [ ] `key` ổn định; không memo khi chưa có số đo
- [ ] thẻ ngữ nghĩa, nhãn, bàn phím, focus
- [ ] test theo hành vi người dùng, mock ở tầng mạng, không soi chi tiết hiện thực
