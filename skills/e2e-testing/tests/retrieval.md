---
skill: e2e-testing
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 51e76464b28d22c68ebbaa1a5828e708eb4a1734
date: 2026-10-04
result: "strict 6/7 (+1 partial, 0 fail) — at threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 7/7"
agent_ids:
  questions: a7be0a3525e1b378f
  answers: a3a619cf63c5cb084
---

Đã đọc: `<gốc worktree>\skills\e2e-testing\SKILL.md` (kèm `references/ai-regression.md`)

# Thử truy xuất - e2e-testing

> **Kết luận:** strict 6/7 (+1 partial, 0 fail), points-right 7/7: đạt ngưỡng (5/6 câu tình huống Đạt hẳn = 83 %; câu ranh giới Đạt). Lượt đầu của skill mới, một lượt, không bổ sung nội dung.
> Chủ thể trỏ đúng mục ở cả 6 câu tình huống và nhận ra câu ranh giới thuộc `react`.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description`, lĩnh vực và tên các skill khác); bài trả lời trọn của chủ thể,
file nháp "Mục kỳ vọng" (có mtime) và id agent ở `evidence/TK8/e2e-testing-retrieval.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `react`.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Test `checkout.spec.ts` "áp mã giảm giá rồi thanh toán" xanh ở máy local nhưng trên CI (GitHub Actions, 2 worker) cứ khoảng 1 trong 5 lần đỏ với "locator.click: Timeout 30000ms exceeded" ở nút "Đặt hàng"; dev đã chèn `waitForTimeout(2000)` mà vẫn chập chờn. Điều tra theo thứ tự nào và sửa thế nào để hết thật, không chỉ tăng timeout hay bật thêm retry? | `SKILL.md` › 5. Chờ đúng, không ngủ + › 6. Test chập chờn: xử lý có kỷ luật (tái hiện `--repeat-each`, sửa nguyên nhân, không tăng chờ hay retry để che) | `SKILL.md` › 6, › 5, › 4 | Đạt |
| 2 | CI chỉ hiện "1 failed" kèm stack trace, không rõ vì sao test đăng nhập hỏng. Muốn có trace, ảnh chụp, video khi hỏng nhưng không lưu cho mọi test vì artifact phình. Đặt `retries`, `trace`, `screenshot`, `video` thế nào và upload đúng phần cần thiết ra sao? | `SKILL.md` › 4. Cấu hình nên có + › 7. Bằng chứng + › 8. CI (upload báo cáo cả khi hỏng) | `SKILL.md` › 4, › 7, › 8; mục khác: `deployment` cho pipeline đầy đủ | Đạt |
| 3 | Class `LoginPage` toàn selector kiểu `div.form > div:nth-child(2) > input` và `//button[3]`, designer đổi layout là cả chục test gãy; các câu `expect` còn nằm trong page object. Cấu trúc lại page object, chọn locator và đặt assertion thế nào? | `SKILL.md` › 3. Locator và page object (vai/nhãn trước, `data-testid` đường lùi; khẳng định nằm trong test) | `SKILL.md` › 3, › 2, › 11 | Đạt |
| 4 | `orders.spec.ts` dùng chung một tài khoản và một giỏ hàng có sẵn trong DB staging; bật `fullyParallel: true` với 4 worker thì test "xoá đơn hàng" làm hỏng "xem lịch sử đơn". Cô lập dữ liệu và trạng thái đăng nhập (storageState, dữ liệu riêng mỗi test hay worker, dọn dẹp) thế nào mà không tắt chạy song song? | `SKILL.md` › 5 (hàng "dữ liệu dùng chung giữa test": mỗi test dựng và dọn dữ liệu riêng) + › 2 (fixtures) + › 11; `storageState` và tài khoản riêng theo worker không có | `SKILL.md` › 5, › 2, › 11, › 4 (nói rõ không có `storageState`, tài khoản theo worker) | Đạt |
| 5 | E2E cho luồng thanh toán: nạp ví 500.000đ, trả đơn 320.000đ, số dư cuối phải đúng 180.000đ, kể cả khi bấm "Thanh toán" hai lần liên tiếp hoặc mạng cổng thanh toán chập chờn. Khẳng định gì ở giao diện, kiểm thêm gì ở API hay DB, cổng thật hay giả, chặn bấm đúp thế nào mà test vẫn ổn định? | `SKILL.md` › 9. Luồng quan trọng và tiền (không chạy production, tài khoản và ví giả, mock dịch vụ ngoài, chờ phản hồi cụ thể); bấm đúp, kiểm số dư ở API hay DB, chặn trùng giao dịch không có | `SKILL.md` › 9, › 5 (nói rõ thiếu API/DB, bấm đúp, mạng chập chờn) | Một phần (trỏ đúng nơi, thiếu cách kiểm bấm đúp và số dư ở API hay DB) |
| 6 | Một agent AI sửa hàm tính phí vận chuyển rồi chính nó (cùng model) review và duyệt PR; lên production đơn trên 2 triệu bị tính phí ship gấp đôi. Viết test hồi quy bám hành vi người dùng thấy ở trang giỏ hàng, bảo đảm nó thật sự đỏ khi lỗi còn tồn tại; quy trình thế nào và vì sao cùng model sửa và review dễ bỏ sót? | `references/ai-regression.md` › 1 (vì sao review của cùng model không đủ), › 3 (test cho lỗi đã gặp), › 4 (chạy test trước review); chứng minh đỏ trước khi sửa chỉ nói gián tiếp | `references/ai-regression.md` › 1, › 3, › 4, › 6; `SKILL.md` › 10; mục khác: `tdd` cho phần kiểm đỏ rồi xanh | Đạt |
| 7 | Form đăng ký nhiều bước `StepperForm` kiểm hợp lệ bằng React Hook Form: để trống email thì hiện lỗi và nút "Tiếp tục" vô hiệu, gõ lại email đúng thì lỗi mất; logic nằm trong một component, API giả lập bằng MSW, không cần backend thật. Dùng Playwright dựng trình duyệt hay có cách nhẹ hơn, viết test thế nào? | mục khác: skill `react` (`SKILL.md` e2e › 1 bảng chọn lớp test: logic trong một component → RTL + Vitest) | mục khác: `react` (từ `SKILL.md` › 1, › 10) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Luồng tiền: kiểm số dư ở tầng API hoặc cơ sở dữ liệu, chặn và kiểm bấm đúp (trùng giao dịch), giả lập mạng cổng chập chờn như một ca test: không có (câu 5). Nguồn distill chỉ có mẫu giao dịch gọi `waitForResponse` và bỏ qua trên production.
- Cô lập trạng thái đăng nhập (`storageState`, tài khoản riêng theo worker) và cách dọn dữ liệu cụ thể: không có, chỉ có nguyên tắc "dựng và dọn riêng mỗi test" (câu 4); câu chấm Đạt vì quyết định chính (dữ liệu riêng mỗi test, không tắt chạy song song) có nội dung.
- Bước tường minh "chứng minh test đỏ ở bản lỗi rồi xanh ở bản sửa": chỉ nói gián tiếp ("viết test trước khi sửa, nếu được"); skill trỏ sang `tdd` (câu 6).
- YAML GitHub Actions cụ thể và cách lọc chỉ tải `test-results` của test hỏng: không có; skill chỉ liệt kê các bước và trỏ `deployment` (câu 2).
- Không có chỗ nào `description` hứa mà thân skill không có.
