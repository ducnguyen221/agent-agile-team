---
name: e2e-testing
description: Use when writing, structuring or fixing Playwright end-to-end tests - page objects, locators, config, retries, traces, CI runs, flaky or intermittently failing tests, quarantine - or when a bug found in AI-assisted code needs a regression test. Not for component tests (that is `react`) and not for a QA pass that only reports findings (that is `web-qa`).
metadata:
  group: technique
  kind: reference
  roles: [implementer, qa]
source: [affaan-m/ECC skills/e2e-testing/SKILL.md, affaan-m/ECC skills/ai-regression-testing/SKILL.md]
source_sha: [ef648e01899ba3e8dc6371642deaaf64b4477775, ef648e01899ba3e8dc6371642deaaf64b4477775]
license: [MIT, MIT]
rewrite_before_public: false
---

# E2E với Playwright

> **Kết luận:** E2E chỉ dành cho **luồng người dùng qua nhiều trang hoặc cần trình duyệt thật**; hành vi của một
> component thì test component (skill `react`). Test ổn định nhờ **chờ đúng điều kiện** (không ngủ cố định),
> locator theo vai/nhãn, trạng thái test dựng sạch mỗi lần. Test qua nhờ **thử lại** là test chập chờn, không
> phải Đạt sạch. Test bị cách ly thì **Chưa chạy** kèm lý do và người giữ, không bao giờ là Đạt. Test hồi quy
> cho lỗi đã gặp: `references/ai-regression.md`.

ASSUMPTION stack: Playwright Test (TypeScript) cho ứng dụng Vite + React.

## 1. Chọn đúng lớp test

| Điều cần kiểm | Lớp | Skill |
|---|---|---|
| hook, component trình bày, form có logic | RTL + Vitest | `react` |
| bố cục thật, API trình duyệt thiếu trong JSDOM | Playwright component | `react`, `e2e-testing` |
| luồng nhiều trang, đăng nhập, thanh toán, đa trình duyệt | **E2E (đây)** | `e2e-testing` |
| QA dùng thử ứng dụng, chấm điểm sức khoẻ, chỉ báo cáo | không viết test | `web-qa` |

## 2. Tổ chức tệp

`tests/e2e/` chia theo tính năng (`auth/`, `features/`, `api/`); `tests/fixtures/` cho đăng nhập và dữ liệu;
`pages/` cho page object; `playwright.config.ts` ở gốc. Một tệp `*.spec.ts` một chủ đề; tên test mô tả hành vi người dùng.

## 3. Locator và page object

- Locator theo **vai và nhãn** trước (`getByRole`, `getByLabel`, `getByText`); `data-testid` là đường lùi khi
  hai cách trên không ổn định. Cùng thứ tự ưu tiên với test component.
- **Page object** gói trang thành lớp: giữ locator và thao tác (`goto`, `search`, `getItemCount`), còn
  **khẳng định nằm trong test**, không nằm trong page object.
- Locator của Playwright tự chờ phần tử sẵn sàng: dùng `page.locator(...).click()`, không đọc phần tử rồi thao tác.

## 4. Cấu hình nên có

- `fullyParallel: true`; `forbidOnly` bật ở CI (chặn `test.only` lọt vào); `workers: 1` ở CI nếu môi trường yếu.
- `retries`: 2 ở CI, 0 ở máy dev. Thử lại chỉ để **phát hiện** chập chờn; test qua ở lần thử lại phải được
  báo là chập chờn (mục 6).
- `trace: "on-first-retry"`, `screenshot: "only-on-failure"`, `video: "retain-on-failure"`.
- `actionTimeout` và `navigationTimeout` đặt rõ; `baseURL` từ biến môi trường `BASE_URL`.
- `webServer` khởi động ứng dụng (`reuseExistingServer` tắt ở CI); `projects` theo phạm vi trình duyệt của dự án
  (Chromium, Firefox, WebKit, một thiết bị di động).
- Báo cáo: HTML cho người đọc, JUnit hoặc JSON cho máy.

## 5. Chờ đúng, không ngủ

| Nguyên nhân chập chờn | Cách sai | Cách đúng |
|---|---|---|
| tranh chấp thời gian (phần tử chưa sẵn sàng) | đọc rồi thao tác ngay | locator tự chờ, `expect(locator)` có thử lại |
| trễ mạng | `waitForTimeout(5000)` | `waitForResponse` theo URL và trạng thái, hoặc chờ phần tử kết quả hiện |
| hoạt ảnh | bấm khi menu đang trượt | chờ `visible` và ổn định rồi mới bấm |
| dữ liệu dùng chung giữa test | test A làm bẩn test B | mỗi test dựng và dọn dữ liệu riêng |

Tránh coi `networkidle` là cách chờ chuẩn: chờ sự kiện cụ thể mà người dùng thấy.

Ngày giờ cố định, "chờ 15 phút" không chờ thật (`page.clock`), tải xuống, tab mới: `references/playwright-recipes.md` mục 1–2.
Đếm dòng sau xoá có thử lại: `toHaveCount` và dữ liệu tự dựng, mục 6 của tệp đó.

## 6. Test chập chờn: xử lý có kỷ luật

1. **Tái hiện trước khi sửa:** chạy lặp (`--repeat-each=10`) trên đúng tệp; không "thử xem có hết không".
2. Tìm nguyên nhân theo bảng mục 5; sửa nguyên nhân, không tăng thời gian chờ để che.
3. **Cách ly** (`test.fixme` hoặc `test.skip` có điều kiện) chỉ khi chưa sửa kịp và phải ghi **mã vấn đề, người giữ, mốc**;
   test bị cách ly báo là **Chưa chạy**, không Đạt; không để cách ly vô thời hạn (thành `CO` nếu hoãn). Cách ly **không**
   dùng để đóng một `RF` hay làm `VR` Đạt (`method/standards/common/testing.md`).
4. Test qua nhờ thử lại: ghi **chập chờn** thành phát hiện mức Nên sửa; chập chờn ở luồng chính là Phải sửa.
5. Không hạ ngưỡng, không sửa cấu hình test để qua kiểm.

## 7. Bằng chứng

Ảnh chụp (`page.screenshot`, cả trang hoặc một phần tử), trace (xem lại từng bước), video giữ khi hỏng; đặt
trong thư mục bằng chứng của sprint có git (không `artifacts/` bị bỏ qua). So sánh ảnh chụp nhiều viewport/ngôn ngữ/giao diện và chống đỏ giả: `references/playwright-recipes.md` mục 3. Một lượt chạy ghi vào REPORT: số tổng,
qua, hỏng, chập chờn, bỏ qua; mỗi hỏng kèm `tệp:dòng`, thông báo lỗi, ảnh, gợi ý sửa. Tệp báo cáo HTML đưa lên
CI làm tài liệu đính kèm (`upload-artifact`, `if: always()`).

## 8. CI

Các bước: lấy mã → cài phụ thuộc theo khoá (`npm ci`) → `npx playwright install --with-deps` → chạy
`npx playwright test` với `BASE_URL` trỏ môi trường dựng sẵn → tải báo cáo lên, **cả khi hỏng**. Chạy trên đẩy mã
và pull request. Cấu hình pipeline đầy đủ: skill `deployment`. Chia shard, gộp báo cáo `blob`, xử lý một shard đỏ: `references/playwright-recipes.md` mục 4.

## 9. Luồng quan trọng và tiền

- Luồng có tiền hoặc dữ liệu thật **không chạy trên production**: chặn bằng điều kiện môi trường, dùng môi trường test
  và tài khoản, thẻ, ví giả. Không dán khoá, mật khẩu hay token thật vào test.
- Đăng nhập bên thứ ba (OAuth, OTP): `storageState` của tài khoản test, đúng một test luồng thật: `references/playwright-recipes.md` mục 5.
- Dịch vụ ngoài khó điều khiển (ví, cổng thanh toán) mock ở tầng ngữ cảnh trình duyệt (`context.addInitScript` hoặc
  chặn yêu cầu mạng) và khẳng định kết quả nhìn thấy; chờ phản hồi cụ thể với thời gian chờ dài đủ cho bước chậm.

## 10. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Giả lập thời gian, tải xuống và tab mới, so sánh ảnh nhiều viewport/ngôn ngữ/giao diện, shard CI và gộp báo cáo, đăng nhập bên thứ ba, đếm dòng sau xoá | `references/playwright-recipes.md` |
| Vì sao cùng một model viết và review thì để lọt lỗi; test hồi quy cho lỗi đã gặp; chạy test trước review; mẫu lỗi hay gặp (lệch đường sandbox/thật, thiếu cột, rò trạng thái lỗi, thiếu hoàn tác) | `references/ai-regression.md` |

Liên quan: `react` (test component, MSW), `web-qa` (QA chỉ báo cáo), `tdd`, `debugging` (tìm nguyên nhân test
hỏng), `bug-triage` (đường xử lý lỗi), `verify-before-done`, `deployment` (CI/CD).

Chuẩn mã bắt buộc của dự án (mục Kiểm thử): `method/standards/web.md`, `typescript.md`, `common/testing.md` — chuẩn giữ
luật ngắn, skill giữ mẫu; hai bên trái nhau là lỗi tài liệu (`method/standards/README.md`).

## 11. Danh mục kiểm

- [ ] mỗi test độc lập: dựng và dọn dữ liệu riêng, chạy được một mình
- [ ] không `waitForTimeout`; chờ theo điều kiện
- [ ] locator theo vai/nhãn, khẳng định nằm trong test
- [ ] có trace và ảnh khi hỏng; báo cáo được tải lên cả khi hỏng
- [ ] test chập chờn và test bị cách ly đều có mã vấn đề, người giữ, mốc
- [ ] không chạy luồng tiền/dữ liệu thật trên production
