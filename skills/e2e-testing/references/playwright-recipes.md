# Playwright: thời gian giả, tải xuống và tab mới, ảnh chụp so sánh, shard CI, đăng nhập bên thứ ba

> **Kết luận:** sáu tình huống Playwright hay gặp mà `SKILL.md` chưa chi tiết: (1) **thời gian**: dùng
> `page.clock`, `install` trước `goto`, không chờ thật; (2) **tải xuống và tab mới**: bắt sự kiện **trước** khi bấm;
> (3) **ảnh chụp so sánh**: một môi trường dựng nền, tắt thứ chập chờn, mỗi viewport/theme một project; (4) **shard CI**:
> `--shard`, báo cáo `blob`, một job gộp chạy cả khi shard đỏ; (5) **đăng nhập bên thứ ba**: không tự động hoá giao diện của
> bên ngoài, dùng trạng thái đã lưu của tài khoản test và giữ đúng **một** test luồng thật; (6) **đếm dòng sau xoá**: khẳng
> định tương đối với dữ liệu mình dựng, dùng `toHaveCount`. Quy tắc nền không đổi: chờ điều kiện, không ngủ cố định.

Nguồn: tài liệu Playwright (`playwright.dev/docs`: Clock, Downloads, Pages, Visual comparisons, Sharding, Authentication,
Assertions). Phần đăng nhập bên thứ ba (mục 5) ngoài `storageState` là thực hành chung, không phải tính năng của công cụ.

## 1. Giả lập thời gian trong trình duyệt

Test phụ thuộc ngày giờ (đồng hồ hiển thị, hạn dùng, tự đăng xuất sau 15 phút không hoạt động) **không** dùng
`waitForTimeout`. Playwright có `page.clock`:

```ts
// ngày cố định, đồng hồ vẫn chạy bình thường
await page.clock.setFixedTime(new Date("2024-02-02T10:00:00"));
await page.goto("/");
await expect(page.getByTestId("current-time")).toHaveText(/2\/2\/2024, 10:00/);

// "chờ 15 phút" trong một cái chớp mắt
await page.clock.install();                                 // PHẢI gọi trước mọi goto/tải trang
await page.clock.pauseAt(new Date("2024-02-02T10:00:00"));
await page.goto("/dashboard");
await page.clock.fastForward("15:00");                      // nhảy 15 phút, bộ đếm giờ hết hạn được kích
await expect(page.getByRole("dialog", { name: /phiên đã hết hạn/i })).toBeVisible();
```

- `setFixedTime`: chỉ cố định `Date.now()`/`new Date()`, bộ đếm giờ vẫn chạy thật; hợp để kiểm hiển thị ngày.
- `install` + `pauseAt` + `fastForward` / `runFor`: dùng khi cần **bộ đếm giờ** chạy (đăng xuất do im lặng, nhắc nhở,
  debounce dài). `fastForward` nhảy một lần (như máy ngủ rồi mở lại); `runFor` đi từng tick, kích mọi bộ đếm giữa chừng; `resume`
  cho thời gian chạy lại.
- Gọi sai thứ tự (sau khi trang đã tải) cho hành vi không xác định: đặt ở đầu test hoặc trong fixture, trước `goto`.
- Đồng hồ chỉ giả **trong trình duyệt**; máy chủ vẫn dùng giờ thật: hạn của token do máy chủ cấp không đổi theo. Test phía
  máy chủ dùng cách khác (đồng hồ giả của máy chủ, hoặc dữ liệu dựng sẵn đã hết hạn).

## 2. Tải xuống và tab / cửa sổ mới

Cả hai theo một nguyên tắc: **bắt đầu chờ sự kiện trước khi hành động gây ra nó**, rồi mới `await` kết quả.

```ts
// tải xuống
const downloadPromise = page.waitForEvent("download");
await page.getByRole("button", { name: /xuất csv/i }).click();
const download = await downloadPromise;
expect(download.suggestedFilename()).toBe("bao-cao.csv");
await download.saveAs(testInfo.outputPath("bao-cao.csv"));   // giữ lại nếu cần đọc nội dung

// liên kết target=_blank mở tab mới
const pagePromise = context.waitForEvent("page");
await page.getByRole("link", { name: /điều khoản/i }).click();
const newPage = await pagePromise;
await newPage.waitForLoadState();
await expect(newPage).toHaveURL(/terms/);
```

- Tệp tải xuống bị xoá khi **context** đóng: `saveAs` ngay nếu cần so nội dung. Khẳng định tên tệp (`suggestedFilename`)
  và nội dung (đọc tệp đã lưu), không chỉ "sự kiện đã tới".
- Tab mở từ trang hiện tại: `page.waitForEvent("popup")`; tab/cửa sổ bất kỳ trong cùng context: `context.waitForEvent("page")`.
  Các trang trong một context dùng chung cookie và cấu hình; thao tác tiếp trên `newPage`, đừng quay lại `page` cũ.
- Việc xảy ra không đoán được: `context.on("page", ...)` thay vì chờ một lần.

## 3. So sánh ảnh chụp (visual) nhiều viewport, ngôn ngữ, giao diện

```ts
await expect(page).toHaveScreenshot("trang-chu.png", {
  fullPage: true,
  maxDiffPixels: 100,                                  // ngưỡng nhỏ, có chủ đích
  mask: [page.getByTestId("clock"), page.locator("img[data-dynamic]")],   // che vùng đổi theo thời gian
});
```

- Ảnh nền được đặt tên theo test + trình duyệt + hệ điều hành; chạy khác môi trường thì lệch (phông, khử răng cưa). Tạo ảnh nền và
  chạy so sánh **trong cùng một môi trường cố định** (hình ảnh Docker của Playwright trên CI), không sinh nền ở máy cá nhân rồi so ở CI.
- Một viewport / ngôn ngữ / giao diện = **một project** trong `playwright.config.ts` (`use: { ...devices["iPhone 13"] }`,
  `locale: "vi-VN"`, `colorScheme: "dark"`); mỗi project có bộ ảnh nền riêng, nên đỏ chỉ rõ tổ hợp nào hỏng. Đừng nhân ba chiều
  cho mọi trang: chọn trang chính và trạng thái chính.
- Chống đỏ giả: `animations: "disabled"` (mặc định của `toHaveScreenshot`, tua hoạt ảnh hữu hạn về trạng thái cuối); ẩn con trỏ nhấp
  nháy (`caret: "hide"`, mặc định); che dữ liệu động bằng `mask`; chờ phông sẵn sàng; cố định dữ liệu và thời gian (mục 1);
  `stylePath` nạp CSS để ẩn quảng cáo, iframe, bộ đếm. Chờ trang ổn định bằng khẳng định hiện hữu trước khi chụp.
- Cập nhật nền chủ ý: `npx playwright test --update-snapshots`, rồi **xem ảnh diff trong review**; ảnh nền đổi là phát hiện cần người
  duyệt, không tự chấp nhận vì "test xanh lại". Ngưỡng `maxDiffPixels` lớn để làm xanh là hạ ngưỡng (luật lõi cấm).
- Ảnh nền nằm trong git (không `artifacts/` bị bỏ qua); kích thước lớn thì dùng ít ảnh, ưu tiên phần tử (`expect(locator).toHaveScreenshot`).

## 4. Shard trên CI và gộp báo cáo

Test chạy lâu thì chia **shard** ra nhiều máy:

```yaml
strategy:
  fail-fast: false                      # một shard đỏ không huỷ các shard khác
  matrix: { shardIndex: [1, 2, 3, 4], shardTotal: [4] }
steps:
  - run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}
  - uses: actions/upload-artifact@v4
    if: ${{ !cancelled() }}
    with: { name: blob-report-${{ matrix.shardIndex }}, path: blob-report, retention-days: 1 }

merge-reports:
  if: ${{ !cancelled() }}               # chạy cả khi có shard đỏ
  needs: [playwright-tests]
  steps:
    - uses: actions/download-artifact@v4
      with: { path: all-blob-reports, pattern: blob-report-*, merge-multiple: true }
    - run: npx playwright merge-reports --reporter html ./all-blob-reports
```

- Cấu hình: `reporter: process.env.CI ? "blob" : "html"` để mỗi shard xuất báo cáo `blob` (gồm tệp đính kèm, trace); job gộp
  `merge-reports` ra một báo cáo HTML (hoặc JUnit cho máy) rồi tải lên làm tài liệu đính kèm.
- Cân bằng: `fullyParallel: true` chia theo **từng test**; không bật thì chia theo **tệp** và tệp dài làm shard lệch.
- **Một shard đỏ:** pipeline đỏ (đúng), nhưng các shard khác vẫn chạy hết (`fail-fast: false`) để báo cáo gộp cho thấy
  toàn cảnh; báo cáo gộp chỉ ra tệp:dòng hỏng thuộc shard nào. Đừng chạy lại cả bộ vì một shard: chạy lại đúng shard đó
  (`--shard=3/4`) hoặc dùng `--last-failed` ở cùng máy; shard đỏ lặp lại ở cùng test thì xử lý như chập chờn (`SKILL.md` mục 6).
- Mỗi shard cần cơ sở dữ liệu và dịch vụ **riêng** hoặc test không đụng dữ liệu nhau; shard dùng chung môi trường làm lộ test phụ
  thuộc thứ tự (mục 5 `SKILL.md`).
- Số liệu REPORT (`SKILL.md` mục 7) lấy từ báo cáo gộp, không từ từng shard.

## 5. Đăng nhập bên thứ ba (OAuth, mã OTP)

- **Không tự động hoá giao diện của bên thứ ba** (trang đăng nhập Google, ngân hàng): nó đổi bất kỳ lúc nào, chặn bot, có thể vi phạm
  điều khoản, và biến test của mình phụ thuộc hệ ngoài.
- Đường chuẩn: một **project "setup"** đăng nhập một lần bằng **tài khoản test chuyên dụng** (không phải tài khoản người
  thật), lưu `storageState` ở `playwright/.auth/` (**gitignore**: nó chứa cookie), các project test khác khai `storageState` và
  `dependencies: ["setup"]`. Nhiều vai trò: mỗi vai một tệp, chọn bằng `test.use({ storageState })`. Test sửa dữ liệu phía máy chủ chạy song song:
  mỗi worker một tài khoản (fixture phạm vi worker). Đăng nhập qua API (`request`) thường nhanh hơn qua giao diện.
- Cách tránh bên thứ ba thật: nhà cung cấp danh tính **giả lập** trong môi trường test (máy chủ OIDC thử, hoặc chế độ đăng nhập
  test của chính ứng dụng, chỉ bật ngoài production); hoặc chặn yêu cầu mạng tới nhà cung cấp và trả mã phản hồi giả (`page.route`).
- **OTP/2FA:** dùng nhà cung cấp ở chế độ thử với mã cố định, hoặc tài khoản test có khoá TOTP đặt trong kho bí mật của CI
  (thư viện sinh mã TOTP trong fixture); không đọc SMS thật, không dán khoá vào mã (luật lõi: không đọc, in, chép giá trị secret).
- Giữ đúng **một** test luồng thật (smoke) đi qua nhà cung cấp thật, tách thành project hoặc lịch riêng, đánh dấu rõ có thể chập chờn
  vì hệ ngoài; mọi test còn lại dùng `storageState` hoặc mô phỏng. `storageState` hết hạn: setup chạy lại ở mỗi lượt CI, không commit.
- `sessionStorage` không nằm trong `storageState` (gắn theo tab): cần thì khôi phục bằng `context.addInitScript`.

## 6. Đếm dòng sau khi xoá, có thử lại

Khẳng định số lượng dùng `toHaveCount` (tự thử lại tới khi đúng hoặc hết hạn), và so với **dữ liệu mình dựng**, không so với con số đọc ra
từ giao diện lúc đầu:

```ts
test("xoá một dòng giảm số dòng còn 2", async ({ page, seed }) => {
  await seed.items(3);                                   // dựng đúng 3 dòng cho test này
  await page.goto("/items");
  const rows = page.getByRole("row", { name: /mục/i });
  await expect(rows).toHaveCount(3);
  await page.getByRole("row", { name: /mục 1/i }).getByRole("button", { name: /xoá/i }).click();
  await expect(rows).toHaveCount(2);                     // thử lại tự động, không `count()` rồi so ngay
});
```

- Không `const n = await rows.count()` rồi `expect(n)`: đọc một lần, không thử lại, chập chờn khi danh sách chưa cập nhật.
- Thử lại cấp **test** (`retries`) chạy **cả test** từ đầu: mỗi lần dựng lại dữ liệu từ không (fixture dựng và dọn); test xoá dữ liệu dùng chung sẽ
  sai ở lần thử lại. Test chỉ qua ở lần thử lại vẫn báo **chập chờn** (`SKILL.md` mục 6).
- Dòng đổi sau thao tác bất đồng bộ (xoá lạc quan rồi hoàn tác khi API lỗi): khẳng định cả hai trạng thái bằng `toHaveCount`
  (mẫu hoàn tác ở `references/ai-regression.md` mục 5). Cần đợi API: `waitForResponse` theo URL và trạng thái, không ngủ cố định.
- Điều kiện không phải một phần tử: `expect.poll(() => lấyTổngTừApi()).toBe(2)` thử lại một giá trị; `expect(async () => {...}).toPass()`
  thử lại cả khối nhiều khẳng định.
