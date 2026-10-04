# Test component React: RTL, Vitest, MSW

> **Kết luận:** test điều người dùng thấy và làm, không test chi tiết hiện thực. Dựng component với đúng
> provider của sản phẩm, thao tác bằng truy vấn tiếp cận được (vai, nhãn) và `userEvent`, khẳng định đầu ra
> nhìn thấy hoặc tác dụng phụ quan sát được (hàm gọi lại chạy, yêu cầu mạng gửi đi). Mock ở tầng mạng bằng
> MSW. Đây là phần mở rộng của skill `react`; chu trình test trước nằm ở skill `tdd`.

## 1. Test nên và không nên làm gì

Nên: render với provider như bản chạy thật; tương tác bằng truy vấn tiếp cận được và `userEvent`; khẳng
định văn bản, trạng thái hiển thị, lời gọi hàm, yêu cầu mạng.
Không nên: soi state nội bộ, props truyền xuống con, hook nào được gọi; mock chính React hay hook của khung;
đếm số lần render hoặc khẳng định cấu trúc DOM vượt quá phần ảnh hưởng người dùng.

## 2. Chọn bộ chạy

| Bộ chạy | Khi nào | Ghi chú |
|---|---|---|
| Vitest | dự án Vite, Remix, cấu hình mới | nhanh, ESM gốc, API gần Jest |
| Jest | Next.js, dự án có sẵn | mặc định của nhiều dự án React |
| Playwright Component Testing | cần công cụ bố cục thật | khi JSDOM thiếu tính năng cần thiết |

Chọn **một** bộ cho một lớp test; chạy RTL + Vitest cùng Playwright component trong một repo chỉ khi chia
làn rõ ràng. Stack mặc định ở đây: Vitest + Testing Library.

## 3. Thứ tự truy vấn

Ba bậc, dùng từ trên xuống:

1. **Cho mọi người:** `getByRole` (kèm `name`), `getByLabelText`, `getByPlaceholderText`, `getByText`, `getByDisplayValue`.
2. **Ngữ nghĩa:** `getByAltText`, `getByTitle`.
3. **`getByTestId`:** đường lùi cuối cùng.

Ba họ truy vấn: `getBy*` ném lỗi nếu không thấy; `queryBy*` trả `null` (để khẳng định **vắng mặt**);
`findBy*` bất đồng bộ (phần tử xuất hiện sau việc chờ).

```tsx
screen.getByRole("button", { name: /lưu/i });   // tốt nhất
screen.getByLabelText("Email");                  // tốt cho ô nhập
screen.getByTestId("save-btn");                  // chỉ khi hai cách trên không dùng được
```

## 4. Tương tác và bất đồng bộ

```tsx
test("gửi form", async () => {
  const user = userEvent.setup();               // một lần mỗi test, dùng lại
  const onSubmit = vi.fn();
  render(<ContactForm onSubmit={onSubmit} />);
  await user.type(screen.getByLabelText("Email"), "a@example.test");
  await user.click(screen.getByRole("button", { name: /gửi/i }));
  expect(onSubmit).toHaveBeenCalledWith({ email: "a@example.test" });
});
```

- Luôn `await` lời gọi `userEvent`. `userEvent` mô phỏng chuỗi thao tác của trình duyệt thật; `fireEvent` chỉ
  bắn một sự kiện đơn lẻ: ưu tiên `userEvent`.
- Phần tử hiện sau việc chờ: `await screen.findByText(...)`. Tác dụng phụ: `await waitFor(() => expect(...))`.
  Phần tử phải biến mất: `waitForElementToBeRemoved`.
- Không `setTimeout` + khẳng định: dễ chập chờn. Dùng các hàm chờ ở trên.

## 5. Mock mạng bằng MSW

MSW chặn ở tầng mạng nên component, hook và thư viện gọi mạng chạy đúng như bản thật.

```ts
// test/setup.ts
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

export const server = setupServer(
  http.get("/api/items/:id", ({ params }) => HttpResponse.json({ id: params.id, label: "mẫu" })),
);
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

- `onUnhandledRequest: "error"` để yêu cầu quên mock làm test **đỏ ồn ào**: pass im lặng tệ hơn đỏ.
- Ghi đè theo từng test bằng `server.use(...)`; `resetHandlers` sau mỗi test trả về mặc định.
- Ca lỗi: trả `new HttpResponse(null, { status: 500 })` và khẳng định thông báo lỗi nhìn thấy.
- Dữ liệu mock là **giá trị giả**; không dán token hay dữ liệu thật vào handler.

## 6. Bọc provider một lần

Gói provider (state-server, theme, router) vào `test-utils.tsx` và xuất lại mọi thứ của Testing Library;
mọi test import từ đó. `QueryClient` của test đặt `retry: false`, tạo **mới cho mỗi test** để cache không rò
giữa các test.

## 7. Test hook tuỳ biến

```tsx
const { result } = renderHook(() => useCounter(0));
act(() => result.current.increment());
expect(result.current.count).toBe(1);
```

- Chỉ qua API công khai của hook. Lời gọi đổi state bọc trong `act`.
- Hook cần Context: truyền `wrapper`. Với hook dùng `QueryClient`, tạo `QueryClient` **ngoài** hàm wrapper
  (một lần mỗi test); tạo trong wrapper làm cache reset ở mỗi lần render và test chập chờn.

## 8. Tiếp cận trong test (axe)

Chạy `axe` (`jest-axe` hoặc `vitest-axe`) cho mọi component tương tác: bắt thiếu nhãn ở ô nhập, ARIA sai,
thiếu `alt`, sai thứ tự heading. Giới hạn: JSDOM không có bộ máy CSS thật nên **tương phản màu chỉ kiểm được
với style nội tuyến**; tương phản và bố cục thật kiểm bằng trình duyệt (`e2e-testing`, `web-qa`). Công cụ
tự động chỉ bắt một phần vấn đề tiếp cận; phần còn lại kiểm tay theo thẻ `roles/verifier/specialists/frontend.md`.

## 9. Snapshot

Snapshot DOM vỡ ở mọi đổi style, hay bị duyệt qua loa và test cấu trúc hơn hành vi. Chỉ chấp nhận cho hàm
tuần tự hoá dữ liệu thuần (chuỗi ổn định) hoặc tệp cấu hình sinh ra. So sánh hình ảnh thật dùng ảnh chụp
trình duyệt (Playwright, Chromatic), không dùng chuỗi DOM.

## 10. Khi nào ra khỏi JSDOM

JSDOM không có: bố cục thật (flex, grid, truy vấn viewport), hoạt ảnh và chuyển tiếp CSS, cuộn, kéo thả, dán
clipboard, iframe, cửa sổ bật lên, tải xuống, luồng chéo nguồn gốc. Ranh giới:

- hook, component trình bày, form có logic → RTL;
- component mà bố cục quan trọng hoặc dùng API trình duyệt thiếu trong JSDOM → Playwright component;
- luồng người dùng qua nhiều trang → E2E (skill `e2e-testing`).

## 11. Độ phủ

Ngưỡng là của **chuẩn dự án** (mặc định 80 % với mã mới hoặc sửa, theo luật lõi); **không hạ ngưỡng, không sửa
cấu hình để qua kiểm**. Độ phủ là sàn, không phải mục tiêu: một component phủ 100 % dòng vẫn có thể không test
trạng thái lỗi. Mỗi component nên có test cho trạng thái rỗng, đang tải, lỗi và nhánh thành công. Trang đầy đủ
được phủ riêng bằng E2E; tối thiểu một smoke test. Vitest: `coverage.provider: "v8"` kèm `thresholds` ở
`vitest.config.ts`.

## 12. Mẫu hỏng cần tránh

- `container.querySelector(...)`: bỏ qua truy vấn tiếp cận được, test qua trong khi người dùng thật thất bại.
- Khẳng định số lần render.
- Mock React (`vi.mock("react")`): sửa component thay vì mock.
- Mock component con theo mặc định: test thành test tích hợp giả. Chỉ mock khi con có tác dụng phụ nặng.
- Bỏ qua cảnh báo `act()`: thường là lỗi thật (cập nhật state sau khi gỡ, thiếu chờ).
- Chia sẻ state thay đổi được giữa các test: vỡ khi đổi thứ tự chạy.
- Test vẫn qua khi bỏ `it.skip`: test không khẳng định điều bạn nghĩ.
- Spy `console.error` để che lỗi mong đợi mà không `mockRestore`: spy rò sang test khác và che lỗi thật.

## 13. Lệnh

Vitest: `vitest` (theo dõi), `vitest run` (một lượt), `vitest run --coverage`, `vitest run đường/tới/file.test.tsx`.
Jest: `jest --watch`, `jest --coverage`. CI: biến `CI=true` rồi `vitest run --coverage`.

## 14. Hai mẫu thường gặp

Error boundary: ném lỗi trong con, khẳng định fallback; `vi.spyOn(console, "error")` bọc trong `try/finally`
để `mockRestore`.

Suspense: render trong `<Suspense fallback={<p>Đang tải</p>}>`; khẳng định fallback hiện, rồi `await findBy*` cho nội dung.

## 15. Test hộp thoại: focus, Esc, trả focus

```tsx
test("hộp thoại: focus vào Hủy, Esc đóng, trả focus về nút mở", async () => {
  const user = userEvent.setup();
  render(<PaymentFlow />);
  const opener = screen.getByRole("button", { name: /thanh toán/i });
  await user.click(opener);
  const dialog = screen.getByRole("dialog", { name: /xác nhận/i });
  expect(within(dialog).getByRole("button", { name: /hủy/i })).toHaveFocus();
  await user.keyboard("{Escape}");
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  expect(opener).toHaveFocus();
});
```

- Khẳng định bằng `toHaveFocus()` và truy vấn theo `role="dialog"`; không soi ref hay `document.activeElement` trực tiếp.
- Nhốt focus: `await user.tab()` nhiều lần rồi khẳng định focus vẫn nằm trong `within(dialog)`.
- JSDOM có thể thiếu `HTMLDialogElement.showModal` hoặc không mô phỏng việc vô hiệu hoá phần nền: kiểm bản JSDOM
  đang dùng; thiếu thì test phần này bằng Playwright component hoặc E2E (mục 10), phần logic còn lại vẫn kiểm bằng RTL.

## 16. MSW: phản hồi chậm, DELETE, lỗi theo từng test

```ts
import { delay } from "msw";
server.use(
  http.get("/api/invoices", async () => { await delay(150); return HttpResponse.json([]); }),  // chậm có chủ đích
  http.delete("/api/invoices/:id", () => new HttpResponse(null, { status: 204 })),
);
// treo mãi để test trạng thái đang tải / thời gian chờ:
server.use(http.get("/api/invoices", async () => { await delay("infinite"); }));
```

- Trong Node (môi trường test), `delay()` không đối số **không** làm chậm (tránh kéo dài test); muốn trạng thái chậm
  phải truyền số mili giây rõ hoặc `"infinite"`. Với `"infinite"` khẳng định khung xương đang hiện ngay, rồi để test kết thúc.
- `DELETE` ghi đè bằng `http.delete`; khẳng định hiệu ứng nhìn thấy (dòng biến mất, thông báo) chứ không chỉ "đã gọi".
  Ca lỗi 500 của `DELETE` khẳng định giao diện trở về trạng thái cũ và có thông báo (mẫu hoàn tác ở `e2e-testing`
  `references/ai-regression.md`).
- Mỗi test ghi đè bằng `server.use`; `afterEach(server.resetHandlers)` (mục 5) trả về mặc định. Bỏ `vi.mock("axios")`: mock ở tầng mạng
  mới bắt được hình dạng phản hồi đổi.
- Đợi trạng thái tải/lỗi bằng `findBy*`/`waitFor` (mục 4), không tắt cảnh báo `act`.

## 17. Test error boundary có nút "Thử lại"

```tsx
test("thử lại dựng lại khối biểu đồ", async () => {
  const user = userEvent.setup();
  let fail = true;
  server.use(http.get("/api/activity", () =>
    fail ? new HttpResponse(null, { status: 500 }) : HttpResponse.json({ points: [1, 2] })));
  render(<ProfilePage />);
  expect(await screen.findByRole("alert")).toHaveTextContent(/không tải được/i);
  expect(screen.getByRole("heading", { name: /hồ sơ/i })).toBeInTheDocument(); // phần ngoài boundary vẫn dùng được
  fail = false;
  await user.click(screen.getByRole("button", { name: /thử lại/i }));
  expect(await screen.findByRole("img", { name: /biểu đồ hoạt động/i })).toBeInTheDocument();
});
```

Khẳng định ba điều: fallback hiện, vùng ngoài boundary còn sống, bấm thử lại làm nội dung trở lại.
