---
skill: frontend
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 8b98b3f727496ad6198d9da78dc485331f5b6714
date: 2026-10-04
result: "strict 6/7 (+1 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: a93899b68c859b98f
  answers: a63cc863201c976e5
---

Đã đọc: `<gốc worktree>\skills\frontend\SKILL.md` (kèm `references/vite.md`)

# Thử truy xuất - frontend

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
| 1 | Trang quản trị (Vite 5 + React 18) load chậm trên 4G, một file `index-xxxx.js` khoảng 2,3 MB chưa nén; nghi `moment`, `lodash` và thư viện biểu đồ bị kéo vào hết nhưng chưa biết đo cái nào chiếm bao nhiêu. Cần quy trình nhìn cấu trúc bundle, xác định thủ phạm, giảm mà không đập lại code nghiệp vụ. | `SKILL.md` › 7. Hiệu năng tải: đo → tách → trì hoãn (visualizer, lazy theo route, `manualChunks` hạng cuối, số trước ↔ sau) | `SKILL.md` › 7; `references/vite.md` › 2, › 6; `SKILL.md` › 11 | Đạt |
| 2 | Dự án khoảng 1.800 module, `npm run dev` lần đầu gần 40 giây, HMR mất 3-4 giây; đang dùng `@vitejs/plugin-react` (Babel) cùng vài plugin khác, và một thư viện icon import cả barrel file hàng nghìn export. Nên chuyển sang plugin SWC hay xử lý chỗ khác, và kiểm bằng cách nào để khỏi đoán mò? | `SKILL.md` › 7 mục 6 (`vite --profile`, Speedscope, `server.warmup`) + › 3 (barrel file; `plugin-react-swc` mặc định) + `references/vite.md` › 2 | `SKILL.md` › 3, › 7 (mục 6); `references/vite.md` › 8, › 2 | Đạt |
| 3 | Ba môi trường (local, staging, production), mỗi nơi một URL API; có `.env.staging` và `.env.production` nhưng `vite build --mode staging` vẫn gọi API production, `import.meta.env.MODE` in ra `production`; `process.env.API_URL` báo `undefined` trên trình duyệt. Vite chọn tệp env theo cơ chế nào và cấu hình sao cho staging build ra đúng? | `SKILL.md` › 4 (thứ tự nạp tệp; `import.meta.env`; chỉ `VITE_` lộ ra client) + › 3 (`loadEnv`, `mode`); cờ `--mode` và quan hệ với `NODE_ENV` không có | `SKILL.md` › 4, › 2, › 3; `references/vite.md` › 8 (nói rõ không phủ cờ `--mode` và quan hệ `NODE_ENV`) | Đạt |
| 4 | Xuất bộ component UI nội bộ lên npm bằng library mode; bản build nhét cả `react` và `react-dom`, ứng dụng dùng thư viện gặp "Invalid hook call" do hai bản React; chưa rõ nên xuất ESM hay cả CJS, khai `exports` và `types` trong `package.json` thế nào, CSS đi kèm có phải import riêng không. | `SKILL.md` › 3 (bullet `build.lib`) + `references/vite.md` › 5 (ngoại trừ phụ thuộc đồng hành, `formats`, dts); `exports`/`types` và CSS không có | `SKILL.md` › 3; `references/vite.md` › 5, › 8, › 2 | Đạt |
| 5 | Thư viện cũ chỉ có bản CommonJS: dev chạy được, sau `vite build` báo `xxx is not a function` / `default is not a function`; lần chạy dev đầu in cảnh báo "optimized dependencies changed, reloading". Vì sao dev và build khác nhau, xử lý ra sao, kể cả khi thư viện nằm trong monorepo nội bộ? | `SKILL.md` › 5 (dev khác build, CJS) + `references/vite.md` › 4 (`optimizeDeps.include`) + `SKILL.md` › 6 (xoá cache `.vite`, `server.fs.allow`); cơ chế bọc `default` và cảnh báo "optimized dependencies changed" không giải thích | `SKILL.md` › 2, › 5, › 6; `references/vite.md` › 4, › 8 (nói rõ không phủ cơ chế bọc `default`) | Đạt |
| 6 | Ứng dụng chạy sau reverse proxy công ty tại đường dẫn con `/app1/` qua nginx; dev dùng chung HMR không chạy (WebSocket `ws://localhost:5173/` lỗi), bản build asset 404 vì đường dẫn bắt đầu `/assets/`. Chỉnh `base`, `server.hmr` (host, port, clientPort, protocol) và phía proxy thế nào? | `SKILL.md` › 6 (`server.hmr.clientPort` sau reverse proxy; `base` khi chạy dưới thư mục con); thiếu `hmr.protocol/host/path` và cấu hình nginx cho WebSocket | `SKILL.md` › 6, `references/vite.md` › 1 (`base`); trỏ `deployment` | Một phần (trỏ đúng nơi, thiếu cấu hình phía proxy và các khoá `hmr` còn lại) |
| 7 | Form tạo đơn 30 trường chậm: mỗi lần gõ cả form render lại; dùng React Hook Form, có `useEffect` đồng bộ sang state cha, vài con bọc `React.memo` vẫn render lại vì nhận object/callback mới. Sửa cho mượt và viết test bằng React Testing Library. | mục khác: skill `react` (form, memo, test component; `SKILL.md` frontend › 1 bảng ranh giới) | mục khác: `react` (từ `SKILL.md` › 1 và `description`) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Cấu hình phía proxy (header nâng cấp WebSocket, bỏ tiền tố `/app1/`) và các khoá `server.hmr.host`, `port`, `protocol`: không có (câu 6). Nguồn distill chỉ nhắc `clientPort`; skill trỏ sang `deployment` cho máy chủ.
- Cờ `--mode` và quan hệ với `NODE_ENV` (câu 3): không giải thích vì sao `MODE` không theo `--mode`; câu chấm Đạt vì quyết định chính (cơ chế chọn tệp env, `process.env` không có ở client) có nội dung.
- Cơ chế bọc `default` của thư viện CJS khi build và cách xử lý phía build (`build.commonjsOptions`); cảnh báo "optimized dependencies changed"; thư viện CJS trong monorepo nội bộ (câu 5): không có, chỉ phủ `optimizeDeps.include` và kiểm bằng `vite build` + `vite preview`. Câu chấm Đạt vì quyết định chính là chọn `optimizeDeps.include` và kiểm bản build; phần cơ chế còn thiếu.
- `exports`/`types` trong `package.json`, ESM hay cả CJS, CSS đi kèm ở chế độ thư viện (câu 4): không có.
- Không có chỗ nào `description` hứa mà thân skill không có; hai khoảng trống lượt 1 (nginx fallback cho đường con, tên lỗi `resolve` trong monorepo) vẫn còn: phần đầu đã được thêm một dòng trỏ, phần sau (`resolve.dedupe`, `exports` của gói nội bộ) không có trong nguồn nên không thêm.
