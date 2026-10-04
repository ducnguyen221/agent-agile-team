---
skill: react
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: f906c1e9de32a9ed19830f51fd8b6739a7f82236
date: 2026-10-04
result: "strict 4/7 (+3 partial, 0 fail) — below threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: a673ba177ac2e78ae
  answers: a54b786f9023c404b
---

Đã đọc: `<gốc worktree>/skills/react/SKILL.md` (kèm `references/testing.md`)

# Thử truy xuất — react (bộ câu mới, lượt độc lập)

> **Kết luận:** strict 4/7 (+3 partial, 0 fail), points-right 7/7: DƯỚI ngưỡng (3/6 câu tình huống Đạt hẳn = 50 %, ngưỡng ≥80 %; câu ranh giới Đạt). Lượt độc lập sau lượt cũ: bộ câu MỚI, người soạn mới, chủ thể mới, chấm lại từ đầu, không nương theo lượt cũ. Không sửa skill.

Bảy câu hỏi do một agent MỚI (`sonnet`, `a673ba177ac2e78ae`) **chưa đọc** skill soạn từ `description`, lĩnh vực và danh sách câu của mọi bộ cũ (để không lặp). Người soạn chỉ đọc một tệp đầu vào gồm đúng ba thứ đó. Cột "Mục kỳ vọng" do QA đọc `SKILL.md` và `references/` rồi ghi vào tệp nháp (mtime `2026-10-04 10:41:37 +0700`) **trước khi** giao chủ thể (lệnh giao sau `2026-10-04 10:42:34 +0700`). Chủ thể là agent mới (`sonnet`, `a54b786f9023c404b`), cấm công cụ Skill, được đưa đường tuyệt đối tới `SKILL.md`, không được mở thư mục `tests/`; 3 lượt đọc file (SKILL.md và câu hỏi, rồi `references/testing.md`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng. Bài trả lời trọn của chủ thể, câu hỏi của người soạn, id agent và tệp kỳ vọng (có mtime) ở `evidence/TK13/react-retrieval.md` và `evidence/TK13/expected/react-expected.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Câu 7 là câu ranh giới (đáp án của người soạn ghi ở cột kỳ vọng). Skill KHÔNG đổi giữa lượt cũ và lượt này (`skill_sha` giữ nguyên).

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Mình đang viết hook `useCartSync` cho một giỏ hàng React: nó có 3 thứ cần theo dõi là `items`, `coupon` và `shippingMethod`. Hiện mình lưu thêm một state `total` rồi cập nhật bằng `useEffect` mỗi khi 3 thứ kia đổi, nên thỉnh thoảng giao diện nháy một lần với tổng tiền cũ rồi mới nhảy sang số mới. Ngoài ra có chỗ gọi `useMemo` bọc mọi phép tính nhỏ mà mình cũng không chắc có cần không. Mình nên tính tổng tiền thế nào cho đúng, và khi nào thì `useMemo`/`useCallback` thực sự đáng dùng? | `SKILL.md` › 1 (suy ra, đừng lưu) + › 2 (mặc định không memo) | `SKILL.md` › 1, › 2, › 10 | Đạt (phần phụ: không có ngưỡng cụ thể cho `useMemo`/`useCallback`) |
| 2 | Component `CommentList` hiển thị 200 bình luận, mỗi bình luận có nút "Thích" và ô trả lời nhỏ. Mình render bằng `comments.map((c, i) => <CommentItem key={i} .../>)`. Từ khi cho phép xóa bình luận ở giữa danh sách, mình thấy nội dung đang gõ dở trong ô trả lời của bình luận này bị nhảy sang bình luận khác, và trạng thái "đã thích" cũng lệch hàng. Nguyên nhân là gì, và nên chọn key thế nào khi dữ liệu có thể thêm, xóa, sắp xếp lại? | `SKILL.md` › 7 (danh sách: `key` ổn định, không dùng chỉ số mảng) | `SKILL.md` › 7, › 10 | Đạt (phần phụ: không giải thích vì sao `key` theo chỉ số làm lệch state) |
| 3 | Mình có `useWindowSize` và `useLocalStorage` viết lặp lại ở 5 component, mỗi nơi tự gắn `addEventListener('resize', ...)` rồi đôi khi quên gỡ, và console báo "Can't perform a React state update on an unmounted component" dưới dạng cảnh báo rò rỉ. Mình muốn gom lại thành custom hook dùng chung. Hook nên có chữ ký trả về thế nào, quy tắc nào cần tuân thủ để không vi phạm luật hook, và với dữ liệu nằm ngoài React như `localStorage` hay `matchMedia` thì nên đăng ký lắng nghe theo cách nào để không bị "tearing"? | `SKILL.md` › 2 (custom hook khi ≥2 nơi, hàm dọn) + › 3 (`useSyncExternalStore`) | `SKILL.md` › 2, › 3, › 1; `references/testing.md` › 7 | Một phần (đúng nơi; thiếu chữ ký trả về của hook và cách đăng ký nguồn ngoài để khỏi tearing) |
| 4 | Mình có `ThemeContext` giữ `{ theme, user, notifications, setTheme, markRead }`. Cứ mỗi lần có thông báo mới, 40 component dùng `useContext(ThemeContext)` chỉ để đọc `theme` cũng render lại, và profiler cho thấy mất khoảng 90 ms mỗi lần. Giá trị truyền vào `Provider` là một object literal tạo mới ở mỗi lần render. Mình nên tách context ra sao, và khi nào thì context là lựa chọn sai so với việc đưa state xuống bằng prop hoặc dùng composition (`children`)? | `SKILL.md` › 3 (một Context mỗi mối quan tâm) + › 7 (tránh thác render, `children`) | `SKILL.md` › 3, › 7; store tầng ứng dụng: `frontend` | Đạt (phần phụ: giá trị `Provider` tạo mới mỗi lần render không được nói tới) |
| 5 | Mình có modal xác nhận thanh toán `PaymentDialog` cần: tự focus vào nút "Hủy" khi mở, đóng bằng phím Esc, nhốt focus bên trong, và khi đóng thì trả focus về nút đã mở nó. Lúc này mình dùng `document.getElementById` và `document.querySelector` để focus, rồi đặt `ref` rải rác trong nhiều component con nên rất rối. Nên quản lý focus và DOM ref trong React theo cách nào, khi nào cần `forwardRef` hay `useImperativeHandle`, và phần nào của việc này mình nên test bằng Testing Library? | `SKILL.md` › 7 (tiếp cận: quản lý focus hộp thoại) + `references/testing.md` › 8 | `SKILL.md` › 7; `references/testing.md` › 1, › 3, › 4, › 8, › 10 | Một phần (đúng nơi; thiếu cách quản lý focus và ref, nhốt focus, `forwardRef`, `useImperativeHandle`) |
| 6 | Trang tìm kiếm sản phẩm của mình nhập vào ô lọc thì danh sách 5.000 dòng bị khựng, mỗi phím gõ mất khoảng 300 ms. Mình đã thử `useDeferredValue` và `startTransition` nhưng không chắc đặt ở đâu, và một đồng nghiệp lại khuyên `React.memo` cho tất cả hàng. Trong React 18, mình nên phân biệt thế nào giữa cập nhật khẩn cấp (nội dung ô nhập) và cập nhật có thể trì hoãn (kết quả lọc), và khi nào `React.memo` mới thật sự phát huy? | `SKILL.md` › 2 (khi nào `React.memo`) + › 7 (ảo hoá) | `SKILL.md` › 2, › 7, › 8 | Một phần (đúng nơi; thiếu `useDeferredValue`, `startTransition`, cập nhật khẩn cấp so với trì hoãn) |
| 7 | Dự án React của mình bị lỗi "Failed to fetch dynamically imported module" sau mỗi lần deploy: người dùng đang mở tab cũ bấm sang trang `/reports` thì tải chunk `Reports-3fa9c1.js` bị 404 vì hash đã đổi. Mình cần cấu hình `build.rollupOptions.output` trong Vite để đặt tên chunk, cân nhắc service worker cache, và thêm xử lý chuyển hướng ở router khi chunk tải lỗi. Cách xử lý đúng cho vấn đề tải chunk và route này là gì? | mục khác: skill `frontend` (đầu `SKILL.md`: build, routing, tải bundle sang `frontend`; › 8 của `frontend` về chunk cũ) | mục khác: `frontend` (từ phần Kết luận, › 8, › 9 của `SKILL.md`) | Đạt |

## Thiếu nội dung / mâu thuẫn

- Chữ ký trả về của custom hook và cách đăng ký nguồn ngoài React (`localStorage`, `matchMedia`) để khỏi tearing: chỉ có tên `useSyncExternalStore` ở mục 3, không có cách dùng (câu 3).
- Quản lý focus và ref trong hộp thoại (focus lúc mở, Esc, nhốt focus, trả focus), `forwardRef`, `useImperativeHandle`, và cách test các phần đó: không có; mục 7 chỉ nhắc "quản lý focus khi mở/đóng hộp thoại" (câu 5).
- Cập nhật khẩn cấp so với trì hoãn (`useDeferredValue`, `startTransition`) cho danh sách lọc nặng: không có; skill chỉ có `React.memo` và ảo hoá (câu 6).
- Giá trị `Provider` là object tạo mới mỗi lần render, tách state và dispatch: không có (câu 4, phụ). Cơ chế vì sao `key` theo chỉ số làm lệch state: không giải thích (câu 2, phụ).
- `description` không hứa chỗ nào thân skill thiếu về mảng đã nêu (component, hook, state, form, Suspense, test); hai mảng không có trong thân là những mảng hẹp kể trên.

## Lịch sử

Lượt trước (bộ câu cũ, 2026-10-04, `skill_sha` `f906c1e9de32a9ed19830f51fd8b6739a7f82236`, `result`: strict 6/7 (+1 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7). Bộ câu cũ giữ nguyên bên dưới, id hàng đổi thành `c1`… để không lẫn vào bảng chấm của lượt mới; người soạn lần sau phải đọc cả hai bộ để không lặp. Dòng "Đã đọc" và đoạn thước chấm của lượt cũ không chép lại (thước chung ở trên).

> **Kết luận:** strict 6/7 (+1 partial, 0 fail), points-right 7/7: đạt ngưỡng (5/6 câu tình huống Đạt hẳn = 83 %; câu ranh giới Đạt). Lượt đầu của skill mới, một lượt, không bổ sung nội dung.
> Chủ thể trỏ đúng mục ở cả 6 câu tình huống và nhận ra câu ranh giới thuộc `frontend`.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description`, lĩnh vực và tên các skill khác); bài trả lời trọn của chủ thể, file nháp
"Mục kỳ vọng" (có mtime) và id agent ở `evidence/TK8/react-retrieval.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `frontend`. Câu 4 chấm Một phần vì nửa sau của câu (cách reset nút "Thử lại") không có nội dung,
dù chủ thể nói rõ phần thiếu.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| c1 | Nhóm mình đang viết `OrderFilterBar` trong một dashboard React 18 + TypeScript. Component này giữ 4 state: từ khóa tìm kiếm, trạng thái đơn, khoảng ngày và trang hiện tại. Mỗi lần gõ vào ô tìm kiếm thì cả bảng `OrderTable` render lại, trong khi `OrderTable` chỉ cần danh sách đã lọc. Một đồng nghiệp muốn đưa hết state lên một context toàn cục. Mình nên đặt từng state ở đâu, và khi nào thì dùng derived state thay cho `useState` + `useEffect` để đồng bộ? | `SKILL.md` › 3. Vị trí state + › 1 (suy ra, đừng lưu) + › 7 (tránh thác render) | `SKILL.md` › 3, › 1, › 7, › 2 | Đạt |
| c2 | Mình có hook `useDebouncedSearch(query)` gọi API trong `useEffect`. Khi người dùng gõ nhanh, kết quả của request cũ đôi khi về sau request mới, nên danh sách hiển thị sai. Thêm nữa, ở dev mode với StrictMode thì effect chạy hai lần và bắn hai request. Cleanup của effect cần viết thế nào, và có nên thay bằng cách lấy dữ liệu khác không? | `SKILL.md` › 4. Lấy dữ liệu + › 2. Hook (hàm dọn); không phủ cleanup cụ thể và StrictMode | `SKILL.md` › 4, › 2, › 10 (nói rõ không phủ cleanup cụ thể và StrictMode) | Đạt |
| c3 | Mình làm form đăng ký 3 bước (thông tin, địa chỉ, xác nhận) bằng React. Mỗi bước có validate riêng và phải giữ dữ liệu khi người dùng bấm quay lại. Hiện mình dùng một `useState` lớn kèm 12 handler `onChange`, nên dễ lỗi và khó test. Mình nên tổ chức form theo controlled hay uncontrolled, và đặt state của các bước ở đâu? Lỗi validate nên hiển thị và đọc ra sao cho người dùng màn hình đọc? | `SKILL.md` › 5. Form + › 7 (tiếp cận); chỗ đặt state các bước không có mục riêng | `SKILL.md` › 5, › 3, › 7 | Đạt |
| c4 | Trang `ProfilePage` dùng `React.lazy` cho `ActivityChart` và bọc bằng `Suspense`. Khi API trả lỗi 500 thì cả trang trắng xóa, không có thông báo gì. Mình cần một error boundary, nhưng chỉ muốn lỗi của khối biểu đồ hiển thị fallback có nút "Thử lại", còn phần thông tin cá nhân phía trên vẫn dùng bình thường. Mình nên đặt boundary và Suspense ở mức nào, và nút "Thử lại" reset trạng thái ra sao? | `SKILL.md` › 6. Suspense và error boundary; cách reset nút Thử lại không có chi tiết | `SKILL.md` › 6, › 10, `references/testing.md` › 14 (nói rõ thiếu cách reset) | Một phần (trỏ đúng nơi, thiếu cách reset boundary) |
| c5 | Mình viết test cho `CartSummary` bằng Vitest và React Testing Library. Test hiện lấy phần tử bằng `container.querySelector('.cart-total span')` và kiểm tra `useState` nội bộ qua một prop `testId`. Mỗi lần đổi class CSS là test vỡ. Mình nên truy vấn phần tử theo thứ tự ưu tiên nào, và nên assert hành vi nào cho một nút "Xóa sản phẩm" khi bấm vào? | `references/testing.md` › 3. Thứ tự truy vấn, › 1, › 12 (mẫu hỏng); `SKILL.md` › 10 | `references/testing.md` › 3, › 4, › 1, › 12; `SKILL.md` › 10 | Đạt |
| c6 | Component `InvoiceList` gọi `GET /api/invoices` và `DELETE /api/invoices/:id`. Mình đang mock bằng `vi.mock('axios')` nên test không bắt được lỗi khi hình dạng response đổi. Mình muốn dùng MSW để mô phỏng cả trường hợp 200, 500 và response chậm trong Vitest. Cấu hình server MSW dùng chung cho các test thế nào, reset handler giữa các test ra sao, và test trạng thái loading/lỗi nên viết thế nào cho khỏi bị `act` warning? | `references/testing.md` › 5. Mock mạng bằng MSW + › 4 (findBy, waitFor, act); phản hồi chậm và DELETE không có ví dụ | `references/testing.md` › 5, › 4, › 6, › 12, › 11 | Đạt |
| c7 | Dự án Vite + React Router của mình có bundle `index.js` nặng 1,8 MB. Mình muốn tách theo route bằng dynamic import, cấu hình `manualChunks` trong `vite.config.ts` và thêm prefetch cho trang checkout. Đồng nghiệp bảo mình chỉnh luôn các component trang cho "đúng kiểu React". Mình nên làm theo thứ tự nào để giảm thời gian tải trang đầu? | mục khác: skill `frontend` (react trỏ build, routing, tải bundle sang `frontend`) | mục khác: `frontend` (từ đầu `SKILL.md` và › 8, › 9) | Đạt |

### Thiếu nội dung / mâu thuẫn

- Cách reset error boundary cho nút "Thử lại" (`resetErrorBoundary`, khoá reset, làm mới dữ liệu): không có (câu 4). Nguồn distill không nói tới, nên không thêm nội dung ở lượt này.
- Cleanup cụ thể cho effect (cờ bỏ qua hoặc huỷ yêu cầu) và hành vi chạy hai lần của StrictMode: không có (câu 2); skill chỉ trỏ sang thư viện state-server.
- Chỗ đặt state của form nhiều bước (nâng lên tổ tiên chung, giữ khi quay lại): chỉ suy ra từ bảng vị trí state (câu 3).
- MSW: không có ví dụ phản hồi chậm (`delay`) và handler cho `DELETE` (câu 6).
- Không có chỗ nào `description` hứa mà thân skill không có.
