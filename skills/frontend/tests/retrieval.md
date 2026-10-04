---
skill: frontend
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 8b98b3f727496ad6198d9da78dc485331f5b6714
date: 2026-10-04
result: "strict 4/7 (+3 partial, 0 fail) — below threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: a1178ca4572e96851
  answers: a2125a6e8d70506f4
---

Đã đọc: `<gốc worktree>/skills/frontend/SKILL.md` (kèm `references/vite.md`)

# Thử truy xuất — frontend (bộ câu mới, lượt độc lập)

> **Kết luận:** strict 4/7 (+3 partial, 0 fail), points-right 7/7: DƯỚI ngưỡng (3/6 câu tình huống Đạt hẳn = 50 %, ngưỡng ≥80 %; câu ranh giới Đạt). Lượt độc lập sau lượt cũ: bộ câu MỚI, người soạn mới, chủ thể mới, chấm lại từ đầu, không nương theo lượt cũ. Không sửa skill.

Bảy câu hỏi do một agent MỚI (`sonnet`, `a1178ca4572e96851`) **chưa đọc** skill soạn từ `description`, lĩnh vực và danh sách câu của mọi bộ cũ (để không lặp). Người soạn chỉ đọc một tệp đầu vào gồm đúng ba thứ đó. Cột "Mục kỳ vọng" do QA đọc `SKILL.md` và `references/` rồi ghi vào tệp nháp (mtime `2026-10-04 10:41:37 +0700`) **trước khi** giao chủ thể (lệnh giao sau `2026-10-04 10:42:34 +0700`). Chủ thể là agent mới (`sonnet`, `a2125a6e8d70506f4`), cấm công cụ Skill, được đưa đường tuyệt đối tới `SKILL.md`, không được mở thư mục `tests/`; 3 lượt đọc file (SKILL.md và câu hỏi cùng lượt, rồi `references/vite.md`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng. Bài trả lời trọn của chủ thể, câu hỏi của người soạn, id agent và tệp kỳ vọng (có mtime) ở `evidence/TK13/frontend-retrieval.md` và `evidence/TK13/expected/frontend-expected.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Câu 7 là câu ranh giới (đáp án của người soạn ghi ở cột kỳ vọng). Skill KHÔNG đổi giữa lượt cũ và lượt này (`skill_sha` giữ nguyên).

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Công ty có trang landing marketing 12 trang đang dùng Vite + React, đã bật code splitting nhưng PageSpeed báo LCP 4,8 giây trên điện thoại. Mỗi lần deploy mới, vài khách đang mở tab cũ bấm sang trang khác thì thấy màn hình trắng, console báo "Failed to fetch dynamically imported module" cho một file hash cũ trả về 404. Nên xử lý thế nào để người dùng đang mở tab không bị vỡ khi ra bản mới, và có cần đổi cách đặt cache cho file nào? | `SKILL.md` › 8 (chunk cũ sau triển khai) + › 7 (đo → tách → trì hoãn) | `SKILL.md` › 8, › 7 | Đạt (phần phụ: cách đặt cache theo loại file không có) |
| 2 | Team có một ứng dụng nội bộ cần nhúng như widget vào ba trang web của đối tác bằng một thẻ script duy nhất, không dựa vào framework của trang chủ. Hiện build ra nhiều chunk kèm file HTML, đối tác phàn nàn phải khai báo nhiều file và CSS đè lẫn kiểu dáng của trang họ. Muốn một bundle gọn có thể mount vào một div do đối tác chỉ định, kiểu dáng không rò ra ngoài. Nên cấu hình build đầu ra thế nào và xử lý CSS ra sao? | `SKILL.md` › 3 (`build.lib`, `external`) + `references/vite.md` › 5 | `SKILL.md` › 3; `references/vite.md` › 5 | Một phần (đúng nơi; thiếu một bundle tự chứa gắn bằng một thẻ script, mount vào div, cách ly CSS) |
| 3 | Ứng dụng đặt hàng đang dùng một React context lớn chứa giỏ hàng, người dùng đăng nhập, bộ lọc sản phẩm và trạng thái modal; mỗi lần đổi bộ lọc là cả trang chi tiết đơn hàng render lại. Dữ liệu từ API (danh sách sản phẩm 5.000 dòng, đơn hàng) cũng đang được fetch tay rồi nhét vào context. Nên chia state thế nào giữa state cục bộ, state toàn cục, state từ server và state nằm trên URL, và chọn công cụ nào cho từng loại? | `SKILL.md` › 9 (state ở tầng ứng dụng) | `SKILL.md` › 9, › 1, › 7 | Đạt |
| 4 | Ứng dụng Vite chạy ở dev gọi API bằng đường dẫn `/api/orders` nhưng backend FastAPI chạy riêng ở cổng 8000 và dùng cookie phiên; fetch trực tiếp thì dính CORS, còn khi dùng proxy thì cookie `Set-Cookie` không lưu được và có đường dẫn bị cắt mất tiền tố `/api` nên backend trả 404. Có thêm một endpoint WebSocket `/ws/notify` cũng cần đi qua. Cấu hình dev proxy cần những gì để cả REST, cookie và WebSocket chạy được như môi trường thật? | `SKILL.md` › 6 (`server.proxy`: `rewrite`, `ws`) | `SKILL.md` › 6; `references/vite.md` › 9 | Một phần (đúng nơi; thiếu cookie `Set-Cookie` qua proxy và CORS, WebSocket chỉ có cờ `ws: true`) |
| 5 | Ứng dụng có 40 trang, người dùng chủ yếu vào 3 trang đầu nhưng bundle khởi tạo vẫn 900 KB gzip vì mọi route được import tĩnh. Khi chuyển sang lazy route thì mỗi lần chuyển trang có một nhịp trắng ngắn, và trang quản trị còn kéo cả thư viện soạn thảo văn bản rất nặng chỉ dùng ở một màn hình con. Nên chia route và chunk thế nào, có nên tải trước (preload/prefetch) trang kế tiếp, và quyết định tách thư viện nặng ra sao? | `SKILL.md` › 7 (tách theo route, lazy thành phần nặng) + › 8 (Suspense mỗi route) | `SKILL.md` › 7, › 8 | Đạt (phần phụ: preload/prefetch trang kế không có) |
| 6 | Một trang bảng điều khiển có biểu đồ đang đọc một số thông tin cấu hình khi chạy (địa chỉ API, khóa tính năng, mã theo dõi) từ file `.env` lúc build; nhưng quy trình triển khai chỉ build một lần ra một image Docker duy nhất rồi chạy y hệt ở dev, staging, production. Sửa biến môi trường lúc chạy container thì giá trị trong bundle không đổi. Làm sao để một bản build dùng được cho cả ba môi trường mà không lộ bí mật ra trình duyệt? | `SKILL.md` › 2 + › 4 (biến nhúng tĩnh lúc build, secret ở server) | `SKILL.md` › 4, › 2 | Một phần (đúng nơi, xác nhận nguyên nhân; thiếu cách một bản build đọc cấu hình lúc chạy cho nhiều môi trường) |
| 7 | Nhóm có luồng thanh toán trên ứng dụng React gồm đăng nhập, thêm sản phẩm vào giỏ, nhập thẻ thử và xác nhận đơn; thỉnh thoảng sau khi deploy lên staging bước xác nhận bị kẹt, dù test đơn vị của từng component đều xanh. Họ muốn có một kịch bản tự động chạy trong trình duyệt thật theo cả luồng này, ổn định không bị flaky, tích hợp vào CI và chạy trên nhiều trình duyệt. Nên viết kịch bản này thế nào, chọn công cụ và cách chờ phần tử ra sao? | mục khác: skill `e2e-testing` (`SKILL.md` › 1: luồng nhiều trang trên trình duyệt thật) | mục khác: `e2e-testing` (› 1, `description`, › 10) | Đạt |

## Thiếu nội dung / mâu thuẫn

- Header cache theo loại file (tệp có băm so với `index.html`) cho bài toán chunk cũ sau triển khai: không có; mục 8 chỉ có "giữ file cũ" và "tải lại trang" (câu 1, phụ).
- Đóng gói widget nhúng bằng một thẻ script (một bundle tự chứa, định dạng đầu ra, mount vào phần tử do bên ngoài chỉ định, cách ly CSS): không có; `build.lib` ở mục 3 và `references/vite.md` mục 5 viết cho thư viện npm (câu 2).
- Proxy dev với cookie phiên (`Set-Cookie` qua proxy) và CORS: không có; mục 6 chỉ có `target`, `changeOrigin`, `rewrite`, `ws` (câu 4).
- Preload/prefetch trang kế tiếp và nhịp trắng khi chuyển lazy route ngoài "fallback là khung xương": không có (câu 5, phụ).
- Một bản build cho nhiều môi trường (cấu hình đọc lúc chạy): không có; mục 2 và mục 4 chỉ nói biến nhúng tĩnh lúc build và "secret ở server" (câu 6).

## Lịch sử

Lượt trước (bộ câu cũ, 2026-10-04, `skill_sha` `8b98b3f727496ad6198d9da78dc485331f5b6714`, `result`: strict 6/7 (+1 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7). Bộ câu cũ giữ nguyên bên dưới, id hàng đổi thành `c1`… để không lẫn vào bảng chấm của lượt mới; người soạn lần sau phải đọc cả hai bộ để không lặp. Dòng "Đã đọc" và đoạn thước chấm của lượt cũ không chép lại (thước chung ở trên).

> **Kết luận:** strict 6/7 (+1 partial, 0 fail), points-right 7/7: đạt ngưỡng (5/6 câu tình huống Đạt hẳn = 83 %; câu ranh giới Đạt). Đây là **lượt 2**: lượt 1 (bộ câu khác) chỉ đạt 4/6 câu
> tình huống Đạt hẳn nên **dưới ngưỡng**; sau đó skill được bổ sung nội dung có nguồn (proxy chỉ có ở dev server và cách ra production, thứ tự nạp tệp `.env`, `import.meta.env`, tóm tắt chế độ thư viện) rồi chạy bộ câu mới
> do người soạn khác viết. `skill_sha` ở trên là của bản sau bổ sung.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description`, lĩnh vực, tên các skill khác và danh sách chủ đề của bộ câu lượt 1 để không lặp); bài trả lời trọn của chủ thể,
file nháp "Mục kỳ vọng" (có mtime) và id agent ở `evidence/TK8/frontend-retrieval-2.md` (lượt 1: `frontend-retrieval-1.md`) trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `react`.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| c1 | Trang quản trị (Vite 5 + React 18) load chậm trên 4G, một file `index-xxxx.js` khoảng 2,3 MB chưa nén; nghi `moment`, `lodash` và thư viện biểu đồ bị kéo vào hết nhưng chưa biết đo cái nào chiếm bao nhiêu. Cần quy trình nhìn cấu trúc bundle, xác định thủ phạm, giảm mà không đập lại code nghiệp vụ. | `SKILL.md` › 7. Hiệu năng tải: đo → tách → trì hoãn (visualizer, lazy theo route, `manualChunks` hạng cuối, số trước ↔ sau) | `SKILL.md` › 7; `references/vite.md` › 2, › 6; `SKILL.md` › 11 | Đạt |
| c2 | Dự án khoảng 1.800 module, `npm run dev` lần đầu gần 40 giây, HMR mất 3-4 giây; đang dùng `@vitejs/plugin-react` (Babel) cùng vài plugin khác, và một thư viện icon import cả barrel file hàng nghìn export. Nên chuyển sang plugin SWC hay xử lý chỗ khác, và kiểm bằng cách nào để khỏi đoán mò? | `SKILL.md` › 7 mục 6 (`vite --profile`, Speedscope, `server.warmup`) + › 3 (barrel file; `plugin-react-swc` mặc định) + `references/vite.md` › 2 | `SKILL.md` › 3, › 7 (mục 6); `references/vite.md` › 8, › 2 | Đạt |
| c3 | Ba môi trường (local, staging, production), mỗi nơi một URL API; có `.env.staging` và `.env.production` nhưng `vite build --mode staging` vẫn gọi API production, `import.meta.env.MODE` in ra `production`; `process.env.API_URL` báo `undefined` trên trình duyệt. Vite chọn tệp env theo cơ chế nào và cấu hình sao cho staging build ra đúng? | `SKILL.md` › 4 (thứ tự nạp tệp; `import.meta.env`; chỉ `VITE_` lộ ra client) + › 3 (`loadEnv`, `mode`); cờ `--mode` và quan hệ với `NODE_ENV` không có | `SKILL.md` › 4, › 2, › 3; `references/vite.md` › 8 (nói rõ không phủ cờ `--mode` và quan hệ `NODE_ENV`) | Đạt |
| c4 | Xuất bộ component UI nội bộ lên npm bằng library mode; bản build nhét cả `react` và `react-dom`, ứng dụng dùng thư viện gặp "Invalid hook call" do hai bản React; chưa rõ nên xuất ESM hay cả CJS, khai `exports` và `types` trong `package.json` thế nào, CSS đi kèm có phải import riêng không. | `SKILL.md` › 3 (bullet `build.lib`) + `references/vite.md` › 5 (ngoại trừ phụ thuộc đồng hành, `formats`, dts); `exports`/`types` và CSS không có | `SKILL.md` › 3; `references/vite.md` › 5, › 8, › 2 | Đạt |
| c5 | Thư viện cũ chỉ có bản CommonJS: dev chạy được, sau `vite build` báo `xxx is not a function` / `default is not a function`; lần chạy dev đầu in cảnh báo "optimized dependencies changed, reloading". Vì sao dev và build khác nhau, xử lý ra sao, kể cả khi thư viện nằm trong monorepo nội bộ? | `SKILL.md` › 5 (dev khác build, CJS) + `references/vite.md` › 4 (`optimizeDeps.include`) + `SKILL.md` › 6 (xoá cache `.vite`, `server.fs.allow`); cơ chế bọc `default` và cảnh báo "optimized dependencies changed" không giải thích | `SKILL.md` › 2, › 5, › 6; `references/vite.md` › 4, › 8 (nói rõ không phủ cơ chế bọc `default`) | Đạt |
| c6 | Ứng dụng chạy sau reverse proxy công ty tại đường dẫn con `/app1/` qua nginx; dev dùng chung HMR không chạy (WebSocket `ws://localhost:5173/` lỗi), bản build asset 404 vì đường dẫn bắt đầu `/assets/`. Chỉnh `base`, `server.hmr` (host, port, clientPort, protocol) và phía proxy thế nào? | `SKILL.md` › 6 (`server.hmr.clientPort` sau reverse proxy; `base` khi chạy dưới thư mục con); thiếu `hmr.protocol/host/path` và cấu hình nginx cho WebSocket | `SKILL.md` › 6, `references/vite.md` › 1 (`base`); trỏ `deployment` | Một phần (trỏ đúng nơi, thiếu cấu hình phía proxy và các khoá `hmr` còn lại) |
| c7 | Form tạo đơn 30 trường chậm: mỗi lần gõ cả form render lại; dùng React Hook Form, có `useEffect` đồng bộ sang state cha, vài con bọc `React.memo` vẫn render lại vì nhận object/callback mới. Sửa cho mượt và viết test bằng React Testing Library. | mục khác: skill `react` (form, memo, test component; `SKILL.md` frontend › 1 bảng ranh giới) | mục khác: `react` (từ `SKILL.md` › 1 và `description`) | Đạt |

### Thiếu nội dung / mâu thuẫn

- Cấu hình phía proxy (header nâng cấp WebSocket, bỏ tiền tố `/app1/`) và các khoá `server.hmr.host`, `port`, `protocol`: không có (câu 6). Nguồn distill chỉ nhắc `clientPort`; skill trỏ sang `deployment` cho máy chủ.
- Cờ `--mode` và quan hệ với `NODE_ENV` (câu 3): không giải thích vì sao `MODE` không theo `--mode`; câu chấm Đạt vì quyết định chính (cơ chế chọn tệp env, `process.env` không có ở client) có nội dung.
- Cơ chế bọc `default` của thư viện CJS khi build và cách xử lý phía build (`build.commonjsOptions`); cảnh báo "optimized dependencies changed"; thư viện CJS trong monorepo nội bộ (câu 5): không có, chỉ phủ `optimizeDeps.include` và kiểm bằng `vite build` + `vite preview`. Câu chấm Đạt vì quyết định chính là chọn `optimizeDeps.include` và kiểm bản build; phần cơ chế còn thiếu.
- `exports`/`types` trong `package.json`, ESM hay cả CJS, CSS đi kèm ở chế độ thư viện (câu 4): không có.
- Không có chỗ nào `description` hứa mà thân skill không có; hai khoảng trống lượt 1 (nginx fallback cho đường con, tên lỗi `resolve` trong monorepo) vẫn còn: phần đầu đã được thêm một dòng trỏ, phần sau (`resolve.dedupe`, `exports` của gói nội bộ) không có trong nguồn nên không thêm.
