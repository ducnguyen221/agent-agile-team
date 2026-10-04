# Vite: plugin, HMR, pre-bundle, thư viện, SSR, mẫu hỏng

> **Kết luận:** phần chi tiết của skill `frontend`. Trước khi chép cấu hình, kiểm phiên bản Vite của dự án
> (stack mặc định: Vite 5): từ bản mới (nguồn nói v7 trở đi) bộ gói là Rolldown, khoá `rollupOptions` đổi
> thành `rolldownOptions`, bộ nén mặc định đổi từ esbuild sang Oxc. Ở Vite 5, giữ `build.rollupOptions` và
> `build.minify` mặc định.

## 1. Khoá cấu hình hay dùng

| Khoá | Mặc định | Ý nghĩa |
|---|---|---|
| `root` | `.` | gốc dự án (nơi có `index.html`) |
| `base` | `/` | đường dẫn công khai khi triển khai dưới thư mục con |
| `envPrefix` | `VITE_` | tiền tố biến lộ ra client — **không bao giờ để rỗng** |
| `build.outDir` | `dist` | thư mục đầu ra |
| `build.minify` | tuỳ phiên bản | bộ nén; `false` để gỡ lỗi |
| `build.sourcemap` | `false` | `true`, `"inline"` hoặc `"hidden"`; mặc định giữ tắt |

## 2. Plugin nên biết trước khi tự viết

| Plugin | Việc | Khi nào |
|---|---|---|
| `@vitejs/plugin-react-swc` | HMR + Fast Refresh bằng SWC | mặc định cho React |
| `@vitejs/plugin-react` | cùng việc, bằng Babel | chỉ khi cần plugin Babel |
| `vite-plugin-checker` | chạy `tsc` + ESLint trong luồng riêng, hiện lỗi trên màn hình dev | mọi dự án TypeScript, vì Vite không kiểm kiểu |
| `vite-tsconfig-paths` | dùng bí danh đường dẫn của `tsconfig` | khi đã có `paths` |
| `vite-plugin-dts` | sinh `.d.ts` ở chế độ thư viện | xuất thư viện TypeScript |
| `vite-plugin-svgr` | nhập SVG thành component React | SVG dùng như component |
| `rollup-plugin-visualizer` | bản đồ kích thước bundle | kiểm định kỳ, `enforce: "post"` |
| `vite-plugin-pwa` | PWA + Workbox | ứng dụng cần offline |

Cần plugin riêng hiếm: viết thẳng trong `vite.config.ts` (`name` duy nhất; tuỳ chọn `enforce`: `pre`/`post`
và `apply`: `build`/`serve`), tách file khi có chỗ thứ hai dùng. Hook thường dùng: `transform` (sửa mã), `resolveId`
+ `load` (module ảo, tiền tố `\0` để plugin khác bỏ qua), `transformIndexHtml`, `configureServer` (thêm
middleware dev), `handleHotUpdate` / `hotUpdate` (HMR riêng; tên đổi theo phiên bản). Gỡ lỗi chuỗi biến đổi: `vite-plugin-inspect`.

## 3. HMR

Plugin khung (React, Vue) lo HMR sẵn. Chỉ dùng `import.meta.hot` trực tiếp cho store tự dựng hoặc công cụ dev
cần giữ state qua lần cập nhật: **sửa thuộc tính** của `import.meta.hot.data` (`data.count = ...`), **không gán lại**
`data`; dọn hiệu ứng phụ trong `dispose`; `accept()` để module tự nhận cập nhật. Mã `import.meta.hot` bị loại khỏi bản build.

## 4. Pre-bundle (`optimizeDeps`)

Vite đổi CJS/UMD sang ESM và gộp để giảm số yêu cầu. Khi thư viện CJS lỗi tương tác: `optimizeDeps.include` (kể cả glob
cho import sâu). `exclude` chỉ cho gói **đã là ESM hợp lệ**. `force: true` bỏ cache, chỉ tạm khi gỡ lỗi; sau đó xoá cờ.

## 5. Chế độ thư viện (`build.lib`)

Hai bẫy quan trọng hơn chi tiết cấu hình: (1) **kiểu không tự được sinh**: thêm `vite-plugin-dts` hoặc
`tsc --emitDeclarationOnly`; (2) **phụ thuộc đồng hành (peer) phải ngoại trừ** (`external`: `react`, `react-dom`,
`react/jsx-runtime`...), nếu không bị gói vào thư viện và người dùng dính lỗi trùng runtime. Khai `formats`
(`es`, `cjs`) và `fileName` rõ ràng.

## 6. Chia chunk (`manualChunks`)

Dạng đối tượng gom gói theo nhóm (`react-vendor: ["react", "react-dom"]`). Dạng hàm chia theo `id` (`node_modules/react`
→ `react-vendor`, còn lại → `vendor`). Không trả tên gói làm tên chunk cho mọi gói.

## 7. SSR

Dựng `createServer({ middlewareMode: true })` trần là việc của người làm khung; ứng dụng thường nên dùng khung đã có
(Nuxt, Remix, SvelteKit, Astro, TanStack Start). Chỉ chỉnh thứ người dùng khung chạm tới: `ssr.external` (giữ
`require()` cho gói gốc native), `ssr.noExternal` (ép gói ESM-only vào bundle SSR, sửa phần lớn lỗi SSR), `ssr.target` (`node` hoặc `webworker`).

## 8. Mẫu hỏng

- `envPrefix: ""` hoặc `loadEnv(mode, root, "")`: đưa mọi biến, kể cả secret, về phía client. Mức Chặn.
- Giả định `require()` chạy trong mã ứng dụng: Vite thiên ESM; dùng `import`.
- Một chunk mỗi gói trong `manualChunks`: sinh hàng trăm file nhỏ.
- Không ngoại trừ phụ thuộc đồng hành ở chế độ thư viện.
- Dùng bộ nén đã bị thay (esbuild ở bản mới): theo mặc định của phiên bản đang dùng.
- Gán lại `import.meta.hot.data`.
- Bí danh `resolve.alias` chép tay trùng `tsconfig.paths`: dùng `vite-tsconfig-paths`.
- Import ngầm đuôi file ở dự án lớn: mỗi lần đoán đuôi tốn nhiều lần tra file hệ thống; viết đuôi rõ (`./Foo.tsx`) và thu hẹp `resolve.extensions`.
- Nhầm `vite preview` với server production; mong `vite build` kiểm kiểu; để `node_modules/.vite` cũ sau khi đổi phụ thuộc.

## 9. Tra nhanh

| Mẫu | Dùng khi |
|---|---|
| `defineConfig` | luôn luôn (có gợi ý kiểu) |
| `loadEnv(mode, root, ["VITE_"])` | đọc biến trong cấu hình, tiền tố rõ |
| `vite-plugin-checker` | dự án TypeScript |
| `vite-tsconfig-paths` | thay `resolve.alias` chép tay |
| `optimizeDeps.include` | thư viện CJS lỗi tương tác |
| `server.proxy` | chuyển yêu cầu API tới backend khi dev |
| `server.host: true` | Docker, container, truy cập từ xa |
| `server.warmup.clientFiles` | biến đổi sẵn các route nóng |
| `build.lib` + `external` | xuất gói npm |
| `manualChunks` dạng đối tượng | tách vendor |
| `vite --profile` | dev chậm |
| `vite build` rồi `vite preview` | thử bản build tại máy (không phải server production) |
