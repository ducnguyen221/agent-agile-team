---
skill: react
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: f906c1e9de32a9ed19830f51fd8b6739a7f82236
date: 2026-10-04
result: "strict 6/7 (+1 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: a6d062c7d2ac47870
  answers: a35641bc293940465
---

Đã đọc: `<gốc worktree>\skills\react\SKILL.md` (kèm `references/testing.md`)

# Thử truy xuất - react

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
| 1 | Nhóm mình đang viết `OrderFilterBar` trong một dashboard React 18 + TypeScript. Component này giữ 4 state: từ khóa tìm kiếm, trạng thái đơn, khoảng ngày và trang hiện tại. Mỗi lần gõ vào ô tìm kiếm thì cả bảng `OrderTable` render lại, trong khi `OrderTable` chỉ cần danh sách đã lọc. Một đồng nghiệp muốn đưa hết state lên một context toàn cục. Mình nên đặt từng state ở đâu, và khi nào thì dùng derived state thay cho `useState` + `useEffect` để đồng bộ? | `SKILL.md` › 3. Vị trí state + › 1 (suy ra, đừng lưu) + › 7 (tránh thác render) | `SKILL.md` › 3, › 1, › 7, › 2 | Đạt |
| 2 | Mình có hook `useDebouncedSearch(query)` gọi API trong `useEffect`. Khi người dùng gõ nhanh, kết quả của request cũ đôi khi về sau request mới, nên danh sách hiển thị sai. Thêm nữa, ở dev mode với StrictMode thì effect chạy hai lần và bắn hai request. Cleanup của effect cần viết thế nào, và có nên thay bằng cách lấy dữ liệu khác không? | `SKILL.md` › 4. Lấy dữ liệu + › 2. Hook (hàm dọn); không phủ cleanup cụ thể và StrictMode | `SKILL.md` › 4, › 2, › 10 (nói rõ không phủ cleanup cụ thể và StrictMode) | Đạt |
| 3 | Mình làm form đăng ký 3 bước (thông tin, địa chỉ, xác nhận) bằng React. Mỗi bước có validate riêng và phải giữ dữ liệu khi người dùng bấm quay lại. Hiện mình dùng một `useState` lớn kèm 12 handler `onChange`, nên dễ lỗi và khó test. Mình nên tổ chức form theo controlled hay uncontrolled, và đặt state của các bước ở đâu? Lỗi validate nên hiển thị và đọc ra sao cho người dùng màn hình đọc? | `SKILL.md` › 5. Form + › 7 (tiếp cận); chỗ đặt state các bước không có mục riêng | `SKILL.md` › 5, › 3, › 7 | Đạt |
| 4 | Trang `ProfilePage` dùng `React.lazy` cho `ActivityChart` và bọc bằng `Suspense`. Khi API trả lỗi 500 thì cả trang trắng xóa, không có thông báo gì. Mình cần một error boundary, nhưng chỉ muốn lỗi của khối biểu đồ hiển thị fallback có nút "Thử lại", còn phần thông tin cá nhân phía trên vẫn dùng bình thường. Mình nên đặt boundary và Suspense ở mức nào, và nút "Thử lại" reset trạng thái ra sao? | `SKILL.md` › 6. Suspense và error boundary; cách reset nút Thử lại không có chi tiết | `SKILL.md` › 6, › 10, `references/testing.md` › 14 (nói rõ thiếu cách reset) | Một phần (trỏ đúng nơi, thiếu cách reset boundary) |
| 5 | Mình viết test cho `CartSummary` bằng Vitest và React Testing Library. Test hiện lấy phần tử bằng `container.querySelector('.cart-total span')` và kiểm tra `useState` nội bộ qua một prop `testId`. Mỗi lần đổi class CSS là test vỡ. Mình nên truy vấn phần tử theo thứ tự ưu tiên nào, và nên assert hành vi nào cho một nút "Xóa sản phẩm" khi bấm vào? | `references/testing.md` › 3. Thứ tự truy vấn, › 1, › 12 (mẫu hỏng); `SKILL.md` › 10 | `references/testing.md` › 3, › 4, › 1, › 12; `SKILL.md` › 10 | Đạt |
| 6 | Component `InvoiceList` gọi `GET /api/invoices` và `DELETE /api/invoices/:id`. Mình đang mock bằng `vi.mock('axios')` nên test không bắt được lỗi khi hình dạng response đổi. Mình muốn dùng MSW để mô phỏng cả trường hợp 200, 500 và response chậm trong Vitest. Cấu hình server MSW dùng chung cho các test thế nào, reset handler giữa các test ra sao, và test trạng thái loading/lỗi nên viết thế nào cho khỏi bị `act` warning? | `references/testing.md` › 5. Mock mạng bằng MSW + › 4 (findBy, waitFor, act); phản hồi chậm và DELETE không có ví dụ | `references/testing.md` › 5, › 4, › 6, › 12, › 11 | Đạt |
| 7 | Dự án Vite + React Router của mình có bundle `index.js` nặng 1,8 MB. Mình muốn tách theo route bằng dynamic import, cấu hình `manualChunks` trong `vite.config.ts` và thêm prefetch cho trang checkout. Đồng nghiệp bảo mình chỉnh luôn các component trang cho "đúng kiểu React". Mình nên làm theo thứ tự nào để giảm thời gian tải trang đầu? | mục khác: skill `frontend` (react trỏ build, routing, tải bundle sang `frontend`) | mục khác: `frontend` (từ đầu `SKILL.md` và › 8, › 9) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Cách reset error boundary cho nút "Thử lại" (`resetErrorBoundary`, khoá reset, làm mới dữ liệu): không có (câu 4). Nguồn distill không nói tới, nên không thêm nội dung ở lượt này.
- Cleanup cụ thể cho effect (cờ bỏ qua hoặc huỷ yêu cầu) và hành vi chạy hai lần của StrictMode: không có (câu 2); skill chỉ trỏ sang thư viện state-server.
- Chỗ đặt state của form nhiều bước (nâng lên tổ tiên chung, giữ khi quay lại): chỉ suy ra từ bảng vị trí state (câu 3).
- MSW: không có ví dụ phản hồi chậm (`delay`) và handler cho `DELETE` (câu 6).
- Không có chỗ nào `description` hứa mà thân skill không có.
