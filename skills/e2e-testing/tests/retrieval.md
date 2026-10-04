---
skill: e2e-testing
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 51e76464b28d22c68ebbaa1a5828e708eb4a1734
date: 2026-10-04
result: "strict 2/7 (+5 partial, 0 fail) — below threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: a5bfd2ee4d689e95d
  answers: a6faffdbabaa76ee1
---

Đã đọc: `<gốc worktree>/skills/e2e-testing/SKILL.md`

# Thử truy xuất — e2e-testing (bộ câu mới, lượt độc lập)

> **Kết luận:** strict 2/7 (+5 partial, 0 fail), points-right 7/7: DƯỚI ngưỡng (1/6 câu tình huống Đạt hẳn = 17 %, ngưỡng ≥80 %; câu ranh giới Đạt). Lượt độc lập sau lượt cũ: bộ câu MỚI, người soạn mới, chủ thể mới, chấm lại từ đầu, không nương theo lượt cũ. Không sửa skill.

Bảy câu hỏi do một agent MỚI (`sonnet`, `a5bfd2ee4d689e95d`) **chưa đọc** skill soạn từ `description`, lĩnh vực và danh sách câu của mọi bộ cũ (để không lặp). Người soạn chỉ đọc một tệp đầu vào gồm đúng ba thứ đó. Cột "Mục kỳ vọng" do QA đọc `SKILL.md` và `references/` rồi ghi vào tệp nháp (mtime `2026-10-04 10:41:37 +0700`) **trước khi** giao chủ thể (lệnh giao sau `2026-10-04 10:42:34 +0700`). Chủ thể là agent mới (`sonnet`, `a6faffdbabaa76ee1`), cấm công cụ Skill, được đưa đường tuyệt đối tới `SKILL.md`, không được mở thư mục `tests/`; 2 lượt đọc file (SKILL.md và câu hỏi); `references/ai-regression.md` không mở vì không câu nào cần. Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng. Bài trả lời trọn của chủ thể, câu hỏi của người soạn, id agent và tệp kỳ vọng (có mtime) ở `evidence/TK13/e2e-testing-retrieval.md` và `evidence/TK13/expected/e2e-testing-expected.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Câu 7 là câu ranh giới (đáp án của người soạn ghi ở cột kỳ vọng). Skill KHÔNG đổi giữa lượt cũ và lượt này (`skill_sha` giữ nguyên).

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Trang quản trị `/admin/products` có bảng 50 dòng, mỗi dòng có nút "Xoá" mở hộp thoại xác nhận rồi gọi `DELETE /api/products/:id`. Dev viết test đếm số dòng sau khi xoá nhưng thỉnh thoảng thấy số dòng vẫn còn 50 dù API đã trả 204, và đôi khi lại đếm trúng 49 rồi 48 vì bảng render lại hai lần. Viết test thế nào để chờ đúng trạng thái cuối của bảng mà không dùng sleep cố định? | `SKILL.md` › 5 (chờ đúng) + › 3 (locator) | `SKILL.md` › 5, › 3 | Đạt (phần phụ: không có ví dụ khẳng định số dòng cuối của bảng) |
| 2 | Ứng dụng đặt phòng họp có trang chọn ngày dùng thư viện lịch tuỳ biến, và nút "Đặt phòng" chỉ cho bấm khi giờ bắt đầu nằm trong tương lai. Test đang hard-code "ngày 15/10/2026", nên sang tuần sau thì đỏ vì ngày đã qua; thêm nữa test "nhắc lịch trước 15 phút" phải chờ thật 15 phút. Làm sao kiểm soát thời gian trong trình duyệt để test chạy nhanh, không phụ thuộc ngày chạy? | không có mục phủ (giả lập đồng hồ trong trình duyệt) | không trỏ mục nào; nói thẳng skill không có | Một phần (không có mục nào chứa; chủ thể nêu rõ thiếu và không bịa) |
| 3 | Trang "Báo cáo doanh thu" có nút "Xuất Excel" tải về `revenue-2026-Q3.xlsx`, và nút "In PDF" mở tab mới với bản xem trước. Team muốn kiểm tra rằng file tải về có đúng tên, không rỗng, và tab mới mở đúng URL, nhưng test hiện tại treo vì không bắt được sự kiện tải xuống lẫn cửa sổ mới. Xử lý hai luồng này thế nào để test ổn định, kể cả khi chạy headless trên CI? | không có mục phủ (sự kiện tải xuống, tab mới) | không trỏ mục nào; nói thẳng skill không có | Một phần (không có mục nào chứa; chủ thể nêu rõ thiếu và không bịa) |
| 4 | Ứng dụng đã có chức năng đa ngôn ngữ (vi/en) và bật chế độ tối. Hai tuần liền có người đổi CSS khiến nút "Gửi" bị che mất ở bản tiếng Anh trên màn hình 375px, mà test chức năng vẫn xanh. Team muốn một lớp kiểm tra bắt các lỗi bố cục như vậy qua nhiều kích thước màn hình, ngôn ngữ và theme. Thiết lập config và cách so sánh ảnh thế nào để không bị báo đỏ giả vì font hoặc animation? | `SKILL.md` › 4 (`projects`) + › 7 (ảnh chụp) | `SKILL.md` › 4, › 7 (chỉ là nền) | Một phần (đúng nơi gần nhất; thiếu so sánh ảnh, ma trận ngôn ngữ/theme/kích thước, chống đỏ giả) |
| 5 | Dự án có 340 test e2e chạy tuần tự mất 48 phút trên một máy CI, và PR nào cũng phải đợi. Dev đề xuất chia nhỏ hoặc chạy trên nhiều máy. Cho biết cách chia (shard) trên GitHub Actions, gộp báo cáo từ nhiều máy về một chỗ, và cách xử lý khi một shard đỏ mà các shard khác xanh, để thời gian xuống dưới 10 phút mà không mất độ tin cậy? | `SKILL.md` › 4 (`fullyParallel`, `workers`) + › 8 (CI) | `SKILL.md` › 8, › 4; mục khác: `deployment` cho pipeline | Một phần (đúng nơi; thiếu chia shard, gộp báo cáo, xử lý shard đỏ) |
| 6 | Trang đăng nhập có đăng nhập qua Google OAuth và xác thực hai bước bằng mã OTP gửi email. Mỗi test E2E đều phải đi qua cả hai bước nên chậm, và CI thỉnh thoảng bị Google chặn vì nghi bot. Test không được dùng tài khoản Google thật của nhân viên. Cho biết cách giả lập hoặc bỏ qua luồng này an toàn, đồng thời vẫn có ít nhất một test kiểm đúng luồng thật ở nơi thích hợp? | `SKILL.md` › 9 (mock dịch vụ ngoài, tài khoản giả) + › 2 (fixtures đăng nhập) | `SKILL.md` › 9, › 2 | Một phần (đúng nơi; thiếu OAuth/OTP, dùng lại trạng thái đăng nhập, vị trí của test luồng thật) |
| 7 | Chị PM nhờ bạn "chạy thử toàn bộ trang bán hàng bản staging trước khi ra mắt tối nay" và gửi lại danh sách những gì bất thường: lỗi hiển thị, nút không bấm được, trang trắng khi đổi sang tiếng Anh. Chị chưa cần bạn sửa gì hay viết thành test tự động, chỉ cần báo cáo có ảnh chụp và mức độ nghiêm trọng của từng lỗi. Nên dùng skill nào để tiến hành lượt kiểm này? | mục khác: skill `web-qa` (`SKILL.md` › 1: QA dùng thử chỉ báo cáo, không viết test) | mục khác: `web-qa` (`description`, › 1, › 10) | Đạt |

## Thiếu nội dung / mâu thuẫn

- Không có mục nào chứa: giả lập thời gian trong trình duyệt (ngày cố định, chờ 15 phút), sự kiện tải xuống và tab/cửa sổ mới. Đây là hai mảng Playwright thường gặp mà skill bỏ trống (câu 2, câu 3).
- So sánh ảnh nhiều viewport/ngôn ngữ/theme và chống đỏ giả do font hay hoạt ảnh: không có; ảnh chụp chỉ được nói như bằng chứng ở mục 7 (câu 4).
- Chia shard trên CI, gộp báo cáo nhiều máy, xử lý một shard đỏ: không có; mục 8 chỉ có các bước CI cơ bản và tải báo cáo cả khi hỏng (câu 5).
- Đăng nhập bên thứ ba (OAuth, OTP): dùng lại trạng thái đăng nhập và vị trí duy nhất của test luồng thật: không có; mục 9 chỉ có nguyên tắc mock và tài khoản giả (câu 6).
- Số dòng cuối của bảng sau khi xoá (khẳng định số lượng với thử lại): chỉ có nguyên tắc chung ở mục 5 (câu 1, phụ).
- `description` hứa "locators, config, retries, traces, CI runs, flaky tests, quarantine" và thân skill có đủ các mảng đó; các câu mới rơi vào mảng description không nêu tên nên không phải lỗi hứa quá.

## Lịch sử

Lượt trước (bộ câu cũ, 2026-10-04, `skill_sha` `51e76464b28d22c68ebbaa1a5828e708eb4a1734`, `result`: strict 6/7 (+1 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7). Bộ câu cũ giữ nguyên bên dưới, id hàng đổi thành `c1`… để không lẫn vào bảng chấm của lượt mới; người soạn lần sau phải đọc cả hai bộ để không lặp. Dòng "Đã đọc" và đoạn thước chấm của lượt cũ không chép lại (thước chung ở trên).

> **Kết luận:** strict 6/7 (+1 partial, 0 fail), points-right 7/7: đạt ngưỡng (5/6 câu tình huống Đạt hẳn = 83 %; câu ranh giới Đạt). Lượt đầu của skill mới, một lượt, không bổ sung nội dung.
> Chủ thể trỏ đúng mục ở cả 6 câu tình huống và nhận ra câu ranh giới thuộc `react`.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description`, lĩnh vực và tên các skill khác); bài trả lời trọn của chủ thể,
file nháp "Mục kỳ vọng" (có mtime) và id agent ở `evidence/TK8/e2e-testing-retrieval.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `react`.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| c1 | Test `checkout.spec.ts` "áp mã giảm giá rồi thanh toán" xanh ở máy local nhưng trên CI (GitHub Actions, 2 worker) cứ khoảng 1 trong 5 lần đỏ với "locator.click: Timeout 30000ms exceeded" ở nút "Đặt hàng"; dev đã chèn `waitForTimeout(2000)` mà vẫn chập chờn. Điều tra theo thứ tự nào và sửa thế nào để hết thật, không chỉ tăng timeout hay bật thêm retry? | `SKILL.md` › 5. Chờ đúng, không ngủ + › 6. Test chập chờn: xử lý có kỷ luật (tái hiện `--repeat-each`, sửa nguyên nhân, không tăng chờ hay retry để che) | `SKILL.md` › 6, › 5, › 4 | Đạt |
| c2 | CI chỉ hiện "1 failed" kèm stack trace, không rõ vì sao test đăng nhập hỏng. Muốn có trace, ảnh chụp, video khi hỏng nhưng không lưu cho mọi test vì artifact phình. Đặt `retries`, `trace`, `screenshot`, `video` thế nào và upload đúng phần cần thiết ra sao? | `SKILL.md` › 4. Cấu hình nên có + › 7. Bằng chứng + › 8. CI (upload báo cáo cả khi hỏng) | `SKILL.md` › 4, › 7, › 8; mục khác: `deployment` cho pipeline đầy đủ | Đạt |
| c3 | Class `LoginPage` toàn selector kiểu `div.form > div:nth-child(2) > input` và `//button[3]`, designer đổi layout là cả chục test gãy; các câu `expect` còn nằm trong page object. Cấu trúc lại page object, chọn locator và đặt assertion thế nào? | `SKILL.md` › 3. Locator và page object (vai/nhãn trước, `data-testid` đường lùi; khẳng định nằm trong test) | `SKILL.md` › 3, › 2, › 11 | Đạt |
| c4 | `orders.spec.ts` dùng chung một tài khoản và một giỏ hàng có sẵn trong DB staging; bật `fullyParallel: true` với 4 worker thì test "xoá đơn hàng" làm hỏng "xem lịch sử đơn". Cô lập dữ liệu và trạng thái đăng nhập (storageState, dữ liệu riêng mỗi test hay worker, dọn dẹp) thế nào mà không tắt chạy song song? | `SKILL.md` › 5 (hàng "dữ liệu dùng chung giữa test": mỗi test dựng và dọn dữ liệu riêng) + › 2 (fixtures) + › 11; `storageState` và tài khoản riêng theo worker không có | `SKILL.md` › 5, › 2, › 11, › 4 (nói rõ không có `storageState`, tài khoản theo worker) | Đạt |
| c5 | E2E cho luồng thanh toán: nạp ví 500.000đ, trả đơn 320.000đ, số dư cuối phải đúng 180.000đ, kể cả khi bấm "Thanh toán" hai lần liên tiếp hoặc mạng cổng thanh toán chập chờn. Khẳng định gì ở giao diện, kiểm thêm gì ở API hay DB, cổng thật hay giả, chặn bấm đúp thế nào mà test vẫn ổn định? | `SKILL.md` › 9. Luồng quan trọng và tiền (không chạy production, tài khoản và ví giả, mock dịch vụ ngoài, chờ phản hồi cụ thể); bấm đúp, kiểm số dư ở API hay DB, chặn trùng giao dịch không có | `SKILL.md` › 9, › 5 (nói rõ thiếu API/DB, bấm đúp, mạng chập chờn) | Một phần (trỏ đúng nơi, thiếu cách kiểm bấm đúp và số dư ở API hay DB) |
| c6 | Một agent AI sửa hàm tính phí vận chuyển rồi chính nó (cùng model) review và duyệt PR; lên production đơn trên 2 triệu bị tính phí ship gấp đôi. Viết test hồi quy bám hành vi người dùng thấy ở trang giỏ hàng, bảo đảm nó thật sự đỏ khi lỗi còn tồn tại; quy trình thế nào và vì sao cùng model sửa và review dễ bỏ sót? | `references/ai-regression.md` › 1 (vì sao review của cùng model không đủ), › 3 (test cho lỗi đã gặp), › 4 (chạy test trước review); chứng minh đỏ trước khi sửa chỉ nói gián tiếp | `references/ai-regression.md` › 1, › 3, › 4, › 6; `SKILL.md` › 10; mục khác: `tdd` cho phần kiểm đỏ rồi xanh | Đạt |
| c7 | Form đăng ký nhiều bước `StepperForm` kiểm hợp lệ bằng React Hook Form: để trống email thì hiện lỗi và nút "Tiếp tục" vô hiệu, gõ lại email đúng thì lỗi mất; logic nằm trong một component, API giả lập bằng MSW, không cần backend thật. Dùng Playwright dựng trình duyệt hay có cách nhẹ hơn, viết test thế nào? | mục khác: skill `react` (`SKILL.md` e2e › 1 bảng chọn lớp test: logic trong một component → RTL + Vitest) | mục khác: `react` (từ `SKILL.md` › 1, › 10) | Đạt |

### Thiếu nội dung / mâu thuẫn

- Luồng tiền: kiểm số dư ở tầng API hoặc cơ sở dữ liệu, chặn và kiểm bấm đúp (trùng giao dịch), giả lập mạng cổng chập chờn như một ca test: không có (câu 5). Nguồn distill chỉ có mẫu giao dịch gọi `waitForResponse` và bỏ qua trên production.
- Cô lập trạng thái đăng nhập (`storageState`, tài khoản riêng theo worker) và cách dọn dữ liệu cụ thể: không có, chỉ có nguyên tắc "dựng và dọn riêng mỗi test" (câu 4); câu chấm Đạt vì quyết định chính (dữ liệu riêng mỗi test, không tắt chạy song song) có nội dung.
- Bước tường minh "chứng minh test đỏ ở bản lỗi rồi xanh ở bản sửa": chỉ nói gián tiếp ("viết test trước khi sửa, nếu được"); skill trỏ sang `tdd` (câu 6).
- YAML GitHub Actions cụ thể và cách lọc chỉ tải `test-results` của test hỏng: không có; skill chỉ liệt kê các bước và trỏ `deployment` (câu 2).
- Không có chỗ nào `description` hứa mà thân skill không có.
