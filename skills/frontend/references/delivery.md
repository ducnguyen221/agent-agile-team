# Frontend: giao bản build, widget nhúng, proxy cookie, nạp trước route, cấu hình lúc chạy

> **Kết luận:** năm tình huống giao bản build mà `SKILL.md` chưa chi tiết: (1) chunk cũ sau triển khai cần
> **hai** việc, header cache đúng theo loại tệp và bắt `vite:preloadError`; (2) widget nhúng bằng một thẻ
> `<script>` là bản build **IIFE tự chứa** dựng vào phần tử do trang chủ chỉ định; (3) proxy dev với cookie phiên
> phải sửa miền/đường của `Set-Cookie`, và cách sạch nhất là cho client gọi cùng nguồn gốc; (4) nạp trước route kế
> tiếp bằng cùng hàm `import()` khi rê chuột hoặc focus, kèm `startTransition` để khỏi nháy khung xương; (5) một
> bản build cho nhiều môi trường thì cấu hình đọc **lúc chạy** từ tệp không băm, không từ `VITE_*`.

Nguồn: tài liệu Vite (`vite.dev`: "Building for Production" mục Load Error Handling và Library Mode, "Server Options" mục
`server.proxy`, "Env Variables and Modes", "Deploying a Static Site"), tài liệu MDN (`Cache-Control`, `<link rel>`
`modulepreload`/`prefetch`, `Element.attachShadow`), tài liệu React (`useTransition`). Mẫu cấu hình lúc chạy (mục 5)
là thực hành chung, Vite không có tính năng riêng cho việc này.

## 1. Chunk cũ sau triển khai: header cache và `vite:preloadError`

Nguyên nhân: bản mới đổi băm tên tệp; tab đang mở xin `Reports-3fa9c1.js` đã bị xoá khỏi máy chủ nên nhận 404 (hoặc nhận
`index.html` thay vì JS khi máy chủ chuyển mọi đường về trang chủ), lỗi "Failed to fetch dynamically imported module".

Hai nửa của cách chữa, cần **cả hai**:

| Tệp | Header | Vì sao |
|---|---|---|
| `index.html` (và mọi tệp **không** có băm) | `Cache-Control: no-cache` | Vite khuyến nghị; buộc trình duyệt hỏi lại, nên tải lại trang luôn thấy tham chiếu tới chunk mới |
| `assets/*` có băm trong tên | `Cache-Control: public, max-age=31536000, immutable` | tên đổi khi nội dung đổi nên giữ cache một năm là an toàn; nhanh cho lần truy cập sau |

Đặt `no-cache` cho tệp có băm thì mất lợi cache; đặt cache dài cho `index.html` thì người dùng bị kẹt ở bản cũ và vẫn xin chunk
đã xoá. Header đặt ở máy chủ tĩnh hoặc CDN (cấu hình theo máy chủ: skill `deployment`), **không** đặt được trong mã Vite.

Nửa thứ hai: khi tab cũ vẫn lỡ xin chunk đã mất, Vite phát sự kiện `vite:preloadError` trên `window`. Bắt nó, tải lại **một lần**
(có chốt chống lặp vô hạn nếu máy chủ hỏng thật):

```ts
window.addEventListener("vite:preloadError", (event) => {
  event.preventDefault();                                   // không ném lỗi ra ngoài
  if (sessionStorage.getItem("reloaded-for-stale-chunk")) return;   // đã thử một lần
  sessionStorage.setItem("reloaded-for-stale-chunk", "1");
  window.location.reload();
});
```

Xoá chốt khi tải xong lành lặn (ví dụ trong `load` sau vài giây). Bổ trợ: giữ `dist/assets/` của một hai bản trước thêm một
khoảng thời gian (không xoá ngay khi triển khai) để tab cũ vẫn xin được; với route lazy, error boundary riêng cho từng route
(`SKILL.md` mục 8) để một route hỏng không sập khung. Service worker cache chunk là cách thứ ba, đắt hơn (phải tự quản cache và
vòng đời bản mới): chỉ khi cần offline (`vite-plugin-pwa`).

## 2. Widget nhúng bằng một thẻ `<script>`

Yêu cầu: trang chủ chỉ chèn `<script src=".../widget.js">` và một phần tử; widget tự dựng. Đây **không** phải thư viện npm
(`references/vite.md` mục 5 nói `external` phụ thuộc đồng hành, ngược với đây): widget phải **tự chứa**, gói luôn React.

```ts
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  define: { "process.env.NODE_ENV": JSON.stringify("production") },   // chế độ thư viện không tự thay process.env
  build: {
    lib: { entry: "src/widget.tsx", name: "MyWidget", formats: ["iife"], fileName: () => "widget.js" },
    // KHÔNG external react: gói vào bundle
  },
});
```

```tsx
// src/widget.tsx
import css from "./widget.css?inline";            // ?inline: nhận CSS dạng chuỗi, không tự chèn vào trang
export function mount(el: HTMLElement, options: Options) {
  const root = el.attachShadow({ mode: "open" });  // Shadow DOM cách ly CSS hai chiều
  const style = document.createElement("style"); style.textContent = css; root.append(style);
  const host = document.createElement("div"); root.append(host);
  createRoot(host).render(<App {...options} />);
}
```

Trang chủ: `<div id="shop-widget"></div><script src="widget.js"></script><script>MyWidget.mount(document.getElementById("shop-widget"), {...})</script>`
(`name` của IIFE thành biến toàn cục; mount vào **phần tử do bên ngoài chỉ định**, không cứng `#root`).

- `formats: ["iife"]` cần `name`. Một tệp đầu ra: bỏ import động (hoặc `rollupOptions.output.inlineDynamicImports: true`).
- CSS ở chế độ thư viện mặc định ra tệp `.css` riêng (người dùng phải thêm thẻ `<link>`); `?inline` + Shadow DOM biến nó thành
  một tệp JS và không rò kiểu ra trang chủ. Không dùng Shadow DOM thì tiền tố class riêng hoặc CSS Modules.
  Lưu ý: phông, `rem` và biến CSS của trang chủ vẫn **kế thừa** vào Shadow DOM (thuộc tính kế thừa đi xuyên);
  Portal/popup dựng vào `document.body` thoát khỏi Shadow DOM nên mất kiểu: mount chúng vào host của widget.
- `import.meta.env.*` được thay tĩnh lúc build, nhưng `process.env.*` thì không (thư viện để người dùng đổi): vì thế phải `define`
  `process.env.NODE_ENV` như trên, không thì mã React tham chiếu `process` ở trình duyệt và lỗi.
- Phát hành: tệp có băm hay không? Trang chủ của bên thứ ba trỏ cứng tới URL, nên tên **cố định** (`widget.js`) và header cache
  ngắn hoặc `no-cache` + ETag, khác với `assets/*` có băm ở mục 1; hoặc phát hành theo phiên bản (`/v1/widget.js`).
- API gọi từ widget là khác nguồn gốc so với trang chủ: máy chủ API phải bật CORS cho các miền được phép (không `*` nếu có cookie).

## 3. Proxy dev với cookie phiên và CORS

`server.proxy` dùng tuỳ chọn của `http-proxy`; ngoài `target`, `changeOrigin`, `rewrite`, `ws`, hai khoá hay cần:

```ts
server: {
  proxy: {
    "/api": {
      target: "https://api.dev.example.test",
      changeOrigin: true,
      secure: true,
      cookieDomainRewrite: "localhost",         // Set-Cookie: Domain=api.dev... → localhost
      cookiePathRewrite: "/",                   // nếu máy chủ đặt Path khác
    },
  },
},
```

- Cookie đứng được ở dev khi trình duyệt tin nguồn gốc là **localhost** (cùng nguồn gốc với trang): để client gọi `/api/...` tương đối
  và proxy lo, không gọi thẳng `https://api...` từ `localhost:5173` (đó là yêu cầu khác nguồn gốc cần CORS + `credentials: "include"`
  + `SameSite=None; Secure`).
- Thuộc tính `Secure` trên HTTP dev: `localhost` được trình duyệt đối xử như nơi an toàn nên thường vẫn nhận; tên máy khác thì không.
  `SameSite=Lax/Strict` hợp với cách proxy cùng nguồn gốc. Cookie bị từ chối: mở tab mạng, xem `Set-Cookie` và cảnh báo từng thuộc tính.
- CORS: `server.cors` điều khiển CORS của **chính dev server** (mặc định chỉ cho localhost); nó **không** sửa CORS của backend.
  Có proxy thì thường không cần CORS ở dev; còn production phải cấu hình ở máy chủ (proxy chỉ sống ở dev, `SKILL.md` mục 6).
- Muốn can thiệp sâu: `configure: (proxy) => proxy.on("proxyRes", ...)`. Đừng bật `rewriteWsOrigin` bừa bãi (rủi ro CSRF qua WebSocket).

## 4. Nạp trước route kế tiếp và nhịp trắng khi chuyển route lazy

- Khai báo hàm nạp một lần và dùng cho cả `lazy` lẫn nạp trước, để trình duyệt cache cùng module:

```tsx
const loadCheckout = () => import("./routes/Checkout");
const Checkout = lazy(loadCheckout);
<Link to="/checkout" onMouseEnter={loadCheckout} onFocus={loadCheckout}>Thanh toán</Link>
```

  Khi bấm thật, `import()` trả kết quả đã nằm trong cache nên route hiện gần như tức thì. Nạp trước khi **rảnh** (sau khi
  trang chính hiện) chứ không trước LCP, và chỉ cho trang có xác suất cao được mở (checkout từ giỏ hàng).
- Vite tự chèn `<link rel="modulepreload">` cho **phụ thuộc** của chunk vào (cấu hình `build.modulePreload`), nhưng không tự
  nạp trước một route chưa bấm. Muốn trình duyệt tải ưu tiên thấp theo gợi ý: `<link rel="prefetch" href="...">` (MDN) với tên
  tệp thật sau khi băm, nên thường dễ hơn khi gọi `import()` ở mã.
- Nhịp trắng/khung xương nháy khi chuyển: bọc việc đổi route trong `startTransition` (hoặc router có hỗ trợ) để React **giữ
  giao diện cũ** cho tới khi route mới sẵn sàng thay vì rơi vào fallback của `Suspense`; fallback chỉ nên hiện ở lần nạp đầu.
  Hiển thị chỉ báo tiến trình mảnh (`isPending`) thay vì khung xương toàn trang.
- Đo lại sau khi thêm: số yêu cầu, kích thước chunk và LCP trước ↔ sau (`SKILL.md` mục 7).

## 5. Một bản build cho nhiều môi trường (cấu hình lúc chạy)

`VITE_*` bị **nhúng tĩnh lúc build** (`SKILL.md` mục 2, 4): muốn dev, staging, production dùng **cùng một tệp build** thì không đặt URL
môi trường vào `VITE_*`. Mẫu thường dùng:

1. Một tệp cấu hình **không băm**, ví dụ `public/config.json` hoặc `config.js`, chứa chỉ giá trị **công khai** (URL API, cờ tính năng).
2. Ứng dụng nạp nó **trước khi dựng** (`await fetch("/config.json")` rồi mới `createRoot(...).render`) hoặc `config.js` nạp bằng
   thẻ `<script>` đặt trước bundle và gán `window.__APP_CONFIG__`.
3. Tệp này được **sinh hoặc thay lúc khởi động container** (một entrypoint điền từ biến môi trường của máy chủ, ví dụ bằng
   `envsubst`) hoặc phục vụ từ máy chủ API; header `Cache-Control: no-cache` giống `index.html`.
4. Giữ kiểu: một hàm `getConfig()` kiểm cấu hình bằng schema (Zod) và hỏng ngay nếu thiếu khoá.

- Secret **vẫn không** ở đây: tệp cấu hình đi tới trình duyệt như bundle. Token, URL cơ sở dữ liệu ở server (`SKILL.md` mục 4).
- Khác biệt thật sự theo môi trường (khoá phân tích riêng) chỉ cần là **giá trị**; khác về mã (thêm tính năng) thì dùng cờ tính năng
  trong cấu hình, không rẽ nhánh bằng bản build khác.
- Nếu chấp nhận một bản build mỗi môi trường (đơn giản hơn): giữ `VITE_*` và `--mode` + `.env.[mode]`, nhưng đó là **nhiều** bản build
  và không "build một lần, chạy mọi nơi".
