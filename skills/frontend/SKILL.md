---
name: frontend
description: Use when building or debugging the client-side delivery of a web app - Vite config, plugins, env variables, dev proxy, bundle size and chunking, lazy-loaded routes, stale chunks after a deploy, library mode - or choosing app-level routing and state, or when a page loads slowly. Not for component, hook or component-test details (that is `react`) nor browser flows (`e2e-testing`).
metadata:
  group: technique
  kind: reference
  roles: [implementer, qa]
source: [affaan-m/ECC skills/frontend-patterns/SKILL.md, affaan-m/ECC skills/vite-patterns/SKILL.md]
source_sha: [ef648e01899ba3e8dc6371642deaaf64b4477775, ef648e01899ba3e8dc6371642deaaf64b4477775]
license: [MIT, MIT]
rewrite_before_public: false
---

# Frontend: build, routing, state ứng dụng, tải trang

> **Kết luận:** `vite build` chỉ **chuyển mã, không kiểm kiểu** (thêm `tsc --noEmit` vào CI); tiền tố `VITE_`
> **không phải ranh giới bảo mật** (mọi thứ mang tiền tố bị nhúng vào bundle, secret thì ở server); dev khác
> build nên **luôn thử bản build** trước khi giao; tối ưu tải thì **đo trước** (bundle, chunk), rồi tách
> route bằng `lazy`, rồi mới tới chia chunk tay. State ở tầng ứng dụng tách **state-server** khỏi state giao diện.

ASSUMPTION stack: Vite 5 + React 18 + TypeScript. Nguồn viết cho Vite bản mới (từ **Vite 8** mặc định dùng Rolldown, khoá cấu
hình đổi tên: `build.rollupOptions` ↔ `build.rolldownOptions`, bộ nén mặc định đổi từ esbuild sang Oxc; Vite 7 vẫn dùng
Rollup, và trước Vite 8 Rolldown chỉ có ở gói `rolldown-vite` riêng): luôn
đối chiếu tài liệu **đúng phiên bản của dự án** trước khi chép cấu hình.

## 1. Ranh giới với `react`

| Việc | Skill |
|---|---|
| component, hook, vị trí state trong cây, form, Suspense, test component | `react` |
| cấu hình build, plugin, biến môi trường, proxy, chia chunk, routing, store ứng dụng, tải trang | `frontend` (đây) |
| luồng nhiều trang trên trình duyệt thật | `e2e-testing` |

## 2. Vite hoạt động ra sao (để đoán đúng lỗi)

- **Dev:** phục vụ mã nguồn dạng ESM gốc, **không gói**; biến đổi theo từng module khi được hỏi nên khởi động
  nhanh và HMR chính xác.
- **Build:** gói cho production (tree-shaking, tách chunk, nén).
- **Pre-bundle:** thư viện CJS/UMD đổi sang ESM một lần, cache ở `node_modules/.vite`.
- **Biến môi trường:** nhúng **tĩnh** lúc build; chỉ biến có tiền tố `VITE_` hiện ra cho mã client.
- Plugin chung một giao diện cho dev và build.

## 3. Cấu hình

- Luôn bọc `defineConfig` (có gợi ý kiểu). Cần biến môi trường trong cấu hình: `defineConfig(({ mode }) => ...)`
  rồi `loadEnv(mode, process.cwd(), ["VITE_"])`, **luôn truyền danh sách tiền tố rõ**.
- React: `@vitejs/plugin-react-swc` là mặc định; `@vitejs/plugin-react` (Babel) chỉ khi cần plugin Babel.
- Bí danh đường dẫn đã có trong `tsconfig` thì dùng `vite-tsconfig-paths`, đừng chép tay hàng chục
  `resolve.alias` trùng lặp.
- Import chỉ một hàm qua file `index` gom mọi thứ (barrel file) buộc Vite nạp **cả thư mục** ở dev: import trực tiếp file đích.
- Xuất thư viện (`build.lib`): **ngoại trừ phụ thuộc đồng hành** (`external`) và tự sinh kiểu
  (`vite-plugin-dts`), vì Vite không phát `.d.ts`. Chi tiết: `references/vite.md` mục 5.
- Plugin riêng: hiếm khi cần; nếu cần, viết thẳng trong `vite.config.ts`, tách file khi có chỗ thứ hai dùng.
  Chi tiết plugin, HMR, pre-bundle, SSR, thư viện: `references/vite.md`.

## 4. Biến môi trường và bảo mật

- **`VITE_` không che được gì.** Nén, mã hoá base64 hay tắt source map không giấu được: ai cũng trích được
  từ JavaScript đã giao. Chỉ **giá trị công khai** (URL API, cờ tính năng, khoá công khai) mang `VITE_`;
  token, URL cơ sở dữ liệu, khoá riêng phải ở **server** sau một API.
- Bẫy `loadEnv(mode, root, "")`: tiền tố rỗng nạp **mọi** biến, kể cả secret của máy build, và `define` có thể nhúng
  chúng vào client. Tương tự `envPrefix: ""` là lỗi mức **Chặn**.
- Cần **một bản build chạy ở nhiều môi trường** (staging, production khác URL API): đừng nhúng URL bằng `VITE_*`; đọc cấu hình lúc chạy
  từ tệp không băm (`references/delivery.md` mục 5).
- Thứ tự nạp tệp: `.env`, `.env.local`, `.env.[mode]`, `.env.[mode].local`; tệp sau đè tệp trước, tệp `*.local`
  dành cho giá trị riêng của máy và không commit. Trong mã client đọc `import.meta.env.VITE_*` cùng các giá trị
  dựng sẵn `MODE`, `BASE_URL`, `DEV`, `PROD`, `SSR`.
- Source map production làm lộ mã gốc: mặc định tắt; chỉ bật khi đẩy sang công cụ theo dõi lỗi, rồi xoá bản local.
- `.gitignore`: `.env.local`, `.env.*.local`, `dist/`, `node_modules/.vite`. Chỉ commit `.env.example` (không giá trị thật).

## 5. Ba điều "xanh giả"

- **`vite build` không kiểm kiểu:** lỗi kiểu lọt production. Thêm `vite-plugin-checker` hoặc `tsc --noEmit` ở CI.
- **Dev khác build:** thư viện CJS có thể chạy khác nhau giữa hai chế độ. Xác nhận bằng `vite build` rồi
  `vite preview` trước khi giao.
- **`vite preview` không phải server production:** chỉ là thử nhanh gói đã build. Giao `dist/` lên máy
  chủ tĩnh thật, hoặc Dockerfile nhiều tầng (skill `deployment`).

## 6. Dev server: proxy, container, monorepo

- Gọi API khác nguồn gốc khi dev: `server.proxy` (`target`, `changeOrigin: true` cho backend ảo hoá theo tên
  máy, `rewrite` để bỏ tiền tố; thêm `ws: true` cho WebSocket).
- **Proxy chỉ sống ở dev server.** Bản build giao lên máy chủ tĩnh không có proxy: ở production, `/api` phải do
  reverse proxy phía máy chủ chuyển đi, hoặc client gọi URL API đầy đủ lấy từ `VITE_API_URL` (giá trị công
  khai). `base` chỉ đổi khi ứng dụng chạy dưới thư mục con. Bộ định tuyến phía client cần máy chủ trả
  `index.html` cho đường con khi tải lại (cấu hình theo máy chủ, xem `deployment`).
- **Trong Docker/container:** Vite nghe ở `localhost` nên bên ngoài không tới được; đặt `server.host: true`
  (nghe `0.0.0.0`) và, sau reverse proxy, `server.hmr.clientPort` đúng cổng ngoài.
- **Monorepo:** gói ngoài gốc dự án bị chặn phục vụ; mở bằng `server.fs.allow`.
- Cache pre-bundle cũ gây lỗi "ma" sau khi đổi nhánh hay vá phụ thuộc: xoá `node_modules/.vite`.
- **Cookie phiên qua proxy** (`Set-Cookie`, `cookieDomainRewrite`, vì sao nên gọi `/api` cùng nguồn gốc) và việc `server.cors` không sửa CORS của
  backend: `references/delivery.md` mục 3.

## 7. Hiệu năng tải: đo → tách → trì hoãn

1. **Đo:** báo cáo bundle (`rollup-plugin-visualizer`, đặt `enforce: "post"`) và kích thước từng chunk; nói số
   trước ↔ sau, không tuyên bố "nhanh hơn" khi chưa đo.
2. **Tách theo route:** `lazy(() => import("./Route"))` bọc `Suspense`; thành phần nặng và ít dùng (biểu đồ,
   trình soạn thảo, 3D) cũng lazy. Fallback là khung xương, không làm nhảy bố cục.
3. **Chia chunk tay (`manualChunks`):** hạng cuối. Gom phụ thuộc lớn ổn định vào vài chunk "vendor"; **không**
   một chunk mỗi gói (tạo hàng trăm file nhỏ).
4. Dòng danh sách dài: ảo hoá (`react`, mục 7); ảnh và phông: nén, định kích thước, tải lười.
   Nạp trước route kế tiếp (rê chuột/focus gọi cùng `import()`), tránh nhịp trắng khi chuyển route lazy: `references/delivery.md` mục 4.
5. Không đưa `@vitejs/plugin-legacy` mặc định (phình bundle khoảng 40 % theo nguồn, phục vụ ít người): chỉ khi
   số liệu truy cập chứng minh cần.
6. Dev chậm: `vite --profile`, thao tác, rồi nạp `.cpuprofile` vào Speedscope để tìm plugin ngốn thời gian;
   `server.warmup.clientFiles` biến đổi sẵn các đường nóng.

## 8. Routing

- Router nào cũng áp được mẫu `react`; chọn theo nhu cầu (React Router, TanStack Router). Router có loader
  và action thì theo tài liệu của nó.
- Mỗi route lazy có `Suspense` và error boundary **riêng**: một route hỏng không kéo sập khung.
- **Chunk cũ sau khi triển khai:** bản build mới đổi tên (băm) file, người đang mở tab xin file cũ đã mất → lỗi
  khi tải route lazy. Vite không giải quyết sẵn. Hai cách giảm nhẹ: giữ file cũ của `dist/assets/` thêm một
  khoảng thời gian; bắt lỗi import động (`vite:preloadError`) và **tải lại trang** một lần. Cả hai chỉ hiệu quả nếu header cache đúng:
  `index.html` `no-cache`, `assets/*` băm `immutable` (chi tiết, mã mẫu: `references/delivery.md` mục 1).
- Đổi route: đưa focus về vùng nội dung và cập nhật tiêu đề trang (tiếp cận: `roles/verifier/specialists/frontend.md` mục 9).

## 9. State ở tầng ứng dụng

| Loại | Công cụ | Ghi chú |
|---|---|---|
| bản sao dữ liệu server (cache, làm mới, đột biến) | TanStack Query hoặc SWR | không chép vào store khác |
| state giao diện nhiều nơi, đổi dồn dập | Zustand, Jotai, Redux Toolkit | store nhỏ theo miền, không một store khổng lồ |
| state hiếm đổi (theme, phiên, ngôn ngữ) | Context | một Context mỗi mối quan tâm |
| state mô tả vị trí (bộ lọc, trang, tab) | URL / tham số truy vấn | để liên kết chia sẻ được |
| state tạm của một component | `useState` | xem `react` mục 3 |

Một nguồn sự thật cho mỗi mẩu dữ liệu; Context + `useReducer` đủ cho miền nhỏ, hành động có kiểu (union).

## 10. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Danh sách plugin cần biết, viết plugin riêng, HMR API, pre-bundle, chế độ thư viện (`build.lib`), SSR externals, bảng tham chiếu nhanh, mẫu hỏng | `references/vite.md` |
| Chunk cũ sau triển khai (header cache theo loại tệp, `vite:preloadError`); widget nhúng bằng một thẻ `<script>` (IIFE tự chứa, Shadow DOM, mount vào phần tử ngoài chỉ định); proxy dev với cookie và CORS; nạp trước route; cấu hình lúc chạy cho nhiều môi trường | `references/delivery.md` |

Liên quan: `react`, `e2e-testing`, `deployment` (Dockerfile nhiều tầng, máy chủ tĩnh), `security-review`
(secret trong bundle), `error-handling`.

Chuẩn mã bắt buộc của dự án (hiệu năng tải, bảo mật phía trình duyệt, kiểm thử): `method/standards/web.md`, `react.md`,
`typescript.md` — chuẩn giữ luật ngắn, skill giữ mẫu; hai bên trái nhau là lỗi tài liệu (`method/standards/README.md`).

## 11. Danh mục kiểm trước khi giao bản build

- [ ] CI có kiểm kiểu độc lập với `vite build`
- [ ] không secret trong biến `VITE_`; `loadEnv` có tiền tố; không `envPrefix: ""`
- [ ] source map production tắt (hoặc có đường đẩy sang công cụ theo dõi lỗi)
- [ ] đã chạy `vite build` + `vite preview`, không chỉ chạy dev
- [ ] route nặng đã `lazy`; có số đo bundle trước ↔ sau
- [ ] có xử lý chunk cũ sau triển khai (giữ file cũ hoặc tải lại trang) và header cache đúng (`index.html` `no-cache`, tệp băm `immutable`)
