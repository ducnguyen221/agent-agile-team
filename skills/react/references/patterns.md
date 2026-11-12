# React: hook tuỳ biến, effect, tải nặng, Context, key, focus, error boundary

> **Kết luận:** phần chi tiết của skill `react` cho bảy chỗ hay sai: (1) custom hook trả gì và đăng ký nguồn
> ngoài React bằng `useSyncExternalStore`; (2) effect có hàm dọn, chịu được chạy hai lần ở dev; (3) ô nhập
> phải đáp tức thì, kết quả nặng được phép trễ (`useDeferredValue`, `useTransition`); (4) giá trị truyền vào
> Context phải ổn định; (5) `key` là danh tính của dòng, không phải vị trí; (6) focus và ref chỉ dùng cho việc
> không-khai-báo-được (focus, cuộn, đo); (7) error boundary biết tự reset. Mặc định của skill vẫn là: tính lúc
> render, không memo khi chưa có số đo.

Nguồn: tài liệu React (`react.dev`: `useSyncExternalStore`, `useDeferredValue`, `useTransition`, `useContext`,
"Rendering Lists", "Manipulating the DOM with Refs", "Synchronizing with Effects"), README của
`react-error-boundary`, và mẫu focus hộp thoại, `useTransition`, `useSyncExternalStore`.

## 1. Custom hook: chữ ký trả về và quy tắc

- Tên bắt đầu bằng `use`; chỉ gọi hook khác ở cấp cao nhất (cùng luật hook ở `SKILL.md` mục 2). Hook không trả JSX.
- **Trả gì:** một giá trị (`useWindowSize()` → `{ width, height }`), hoặc cặp `[value, setValue]` khi mô phỏng
  `useState` (`useLocalStorage(key, initial)`), hoặc đối tượng có tên khi trả từ ba thứ trở lên (đọc theo tên,
  không theo thứ tự). Giữ **cùng một hình dạng** ở mọi nhánh trả về.
- **Tham số:** đối tượng hay hàm truyền vào mà đổi danh tính mỗi lần render sẽ chạy lại effect bên trong; nhận
  giá trị nguyên thuỷ, hoặc để người gọi bọc ổn định, hoặc giữ qua ref.
- Hook chia sẻ **logic**, không chia sẻ **state**: mỗi chỗ gọi có state riêng. Muốn nhiều component chung một
  giá trị thì đưa lên Context hoặc store (`SKILL.md` mục 3).
- Tách hook khi cùng dãy hook lặp ở từ hai nơi; hook đặt tên theo việc (`useOnlineStatus`) chứ không theo cơ
  chế (`useEventListener` cho một việc duy nhất).

### 1.1. Dữ liệu nằm ngoài React (`localStorage`, `matchMedia`, kích thước cửa sổ, trạng thái mạng)

Đăng ký bằng `useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?)`, không tự `useEffect` + `useState`:
React dùng nó để tránh **tearing** (hai component cùng một lần render thấy hai giá trị khác nhau của nguồn ngoài)
và nó tự gỡ đăng ký khi gỡ component.

```tsx
function subscribe(callback: () => void) {
  window.addEventListener("online", callback);
  window.addEventListener("offline", callback);
  return () => {
    window.removeEventListener("online", callback);
    window.removeEventListener("offline", callback);
  };
}
export function useOnlineStatus() {
  return useSyncExternalStore(subscribe, () => navigator.onLine, () => true);
}
```

- `subscribe` khai báo **ngoài component** (hoặc `useCallback`): đổi danh tính thì React đăng ký lại.
- `getSnapshot` phải trả **cùng giá trị** khi nguồn chưa đổi (so bằng `Object.is`). Trả đối tượng mới mỗi lần gọi
  gây lặp render vô hạn: với `localStorage` thì đọc ra chuỗi (nguyên thuỷ) và parse ở ngoài, hoặc cache bản
  parse theo chuỗi; với kích thước cửa sổ thì trả hai hook riêng hoặc cache đối tượng cho tới khi sự kiện đổi nó.
- `getServerSnapshot` (đối số thứ ba) bắt buộc khi hiển thị phía máy chủ; trả giá trị mặc định an toàn.
- Cảnh báo "state update on an unmounted component" thường báo thiếu hàm dọn: dùng `useSyncExternalStore` hoặc
  trả hàm gỡ listener trong `useEffect` (mục 2).

## 2. Effect: hàm dọn, chạy hai lần, đua yêu cầu

- Ở dev, `StrictMode` chạy mỗi effect **thêm một lần** (đăng ký → dọn → đăng ký lại) để lộ hàm dọn thiếu. Effect
  đúng thì chạy hai lần vẫn không đổi kết quả; **không** bỏ `StrictMode` để che.
- Hàm dọn gỡ đúng thứ effect đã đăng ký (listener, bộ đếm giờ, kết nối); với yêu cầu mạng thì huỷ hoặc bỏ qua kết quả:

```tsx
useEffect(() => {
  const controller = new AbortController();
  fetch(`/api/search?q=${query}`, { signal: controller.signal })
    .then((r) => r.json())
    .then(setResults)
    .catch((e) => { if (e.name !== "AbortError") setError(e); });
  return () => controller.abort();
}, [query]);
```

  Không có `AbortController`: dùng cờ `let ignore = false` đặt `true` trong hàm dọn và kiểm trước khi `setState`.
  Cách này giải quyết "yêu cầu cũ về sau yêu cầu mới". Hai request ở dev do StrictMode là bình thường; ở bản chạy
  thật chỉ có một.
- Dữ liệu ứng dụng vẫn nên đi qua thư viện state-server (`SKILL.md` mục 4); ví dụ trên chỉ cho chỗ buộc phải tự gọi.
- Debounce ô tìm kiếm: giữ giá trị trễ bằng `setTimeout` trong effect có hàm `clearTimeout`, hoặc `useDeferredValue` (mục 3) khi
  chi phí nằm ở render chứ không ở mạng (`useDeferredValue` không giảm số yêu cầu mạng).

## 3. Ô nhập đáp tức thì, kết quả nặng được trễ

Khi gõ vào ô lọc làm danh sách lớn render chậm, phân biệt hai loại cập nhật: **khẩn cấp** (nội dung ô nhập, phải
đổi ngay) và **có thể trì hoãn** (kết quả lọc). React 18 cho hai công cụ:

```tsx
const [text, setText] = useState("");
const deferredText = useDeferredValue(text);          // giá trị "đi sau"
return (
  <>
    <input value={text} onChange={(e) => setText(e.target.value)} />
    <SlowList text={deferredText} />                  {/* component nặng, bọc memo */}
  </>
);
const SlowList = memo(function SlowList({ text }: { text: string }) { /* ... */ });
```

- `useDeferredValue(value)`: render đầu dùng giá trị cũ, rồi render nền với giá trị mới; render nền bị bỏ nếu có
  cập nhật mới tới. **Component nặng phải bọc `memo`**, không thì không bỏ được lần render với giá trị cũ. Giá trị là
  nguyên thuỷ hoặc đối tượng tạo **ngoài** render. Không có độ trễ cố định như debounce, thích nghi theo máy.
- `useTransition` → `[isPending, startTransition]`: bọc **lời gọi đổi state** vào `startTransition(() => setTab(next))` khi
  mình nắm hàm đổi state (chuyển tab, đổi trang). Dùng `isPending` để báo "đang tải". Giới hạn: **không** bọc state
  điều khiển ô nhập vào transition (ô sẽ không đáp); cập nhật phải xảy ra **đồng bộ** trong hàm truyền vào, state đặt sau `await`
  phải bọc thêm một `startTransition`.
- `React.memo`: chỉ có lợi khi component con render nặng và props hay giữ nguyên (`SKILL.md` mục 2). Với danh sách
  hàng nghìn dòng, đo trước: ảo hoá (mục 7 của `SKILL.md`) thường thắng `memo` vì giảm số nút DOM, còn
  `memo`/deferred chỉ giảm số lần render.
- Thứ tự thử: (1) đo bằng profiler; (2) hạ state xuống để khỏi render lại cả cây; (3) `useDeferredValue` + `memo`;
  (4) ảo hoá; (5) `useMemo`/`useCallback` chỉ khi chuỗi phụ thuộc chứng minh cần.

## 4. Context: giá trị ổn định, tách theo mối quan tâm

- Khi giá trị của Provider đổi (so bằng `Object.is`), **mọi** component dùng context đó render lại, kể cả bọc `memo`.
  Giá trị là đối tượng literal `{ theme, user, setTheme }` tạo mới mỗi lần Provider render nên coi như luôn đổi.
- Hai chỗ chữa: (a) **tách** thành nhiều context nhỏ theo mối quan tâm (`ThemeContext`, `UserContext`,
  `NotificationsContext`): đổi thông báo không đánh thức người chỉ đọc theme; (b) bọc giá trị Provider bằng `useMemo`
  và hàm bằng `useCallback` để giữ danh tính khi Provider chỉ render lại vì cha.
- Cặp **state / dispatch**: đặt state và hàm cập nhật ở hai context riêng; hàm cập nhật gần như không đổi nên nơi chỉ
  bấm nút không render lại khi state đổi.
- Context là lựa chọn sai khi: dữ liệu đổi dồn dập (dùng store ngoài, `SKILL.md` mục 3); chỉ truyền qua một hai tầng
  (đưa bằng props); cần truyền **phần giao diện** xuống sâu (dùng **composition**: nhận `children` hoặc prop-khe để cha dựng sẵn
  phần tử, tránh đưa dữ liệu qua nhiều tầng).

## 5. `key` là danh tính, không phải vị trí

React ghép phần tử cũ và mới theo `key` để biết state nào thuộc dòng nào. Dùng `key={index}`: khi xoá, chèn, đổi
chỗ, vị trí dồn lên nhưng state (nội dung đang gõ, "đã thích", focus) của component **ở lại theo vị trí**, nên
nó dính sang dòng khác. Quy tắc:

- `key` duy nhất **giữa anh em**, ổn định qua các lần render, lấy từ dữ liệu (id từ máy chủ; với dữ liệu tạo tại máy
  khách thì cấp id lúc tạo, ví dụ bộ đếm hoặc `crypto.randomUUID()`).
- **Không** sinh `key` trong lúc render (`Math.random()`): mỗi lần render thành dòng mới, state mất, DOM dựng lại.
- Chỉ số mảng chấp nhận được khi danh sách **tĩnh**, không đổi thứ tự, không thêm xoá.
- `key` không truyền xuống làm prop; cần id thì truyền riêng (`<Row key={id} id={id} />`). Đổi `key` của một
  component cũng là cách **ép dựng lại từ đầu** (reset state) khi đổi đối tượng đang xem.

## 6. Focus, ref và hộp thoại

- Ref cho việc không khai báo được: focus, cuộn, đo kích thước, gọi API trình duyệt. **Không** sửa DOM mà React quản
  lý (xoá phần tử, đổi nội dung của nút do JSX dựng); thấy mình `document.getElementById`/`querySelector` để thao tác
  là dấu hiệu nên dùng ref.
- `ref.current` chỉ đáng tin trong trình xử lý sự kiện và effect (sau commit), không trong render. Danh sách phần tử
  cần ref: dùng **ref callback** (lưu vào `Map`, trả hàm dọn), không `useRef` trong vòng lặp.
- Ref qua component con: React 19 nhận `ref` như prop thường; React 18 phải bọc `forwardRef`. Muốn chỉ lộ vài
  thao tác (`focus`, `reset`) thay vì cả nút DOM: `useImperativeHandle(ref, () => ({ focus() { inputRef.current?.focus(); } }))`.
  Dùng ít; ưu tiên truyền prop và trạng thái.
- Cần đọc DOM ngay sau khi đổi state (cuộn tới dòng vừa thêm): `flushSync(() => setTodos(...))` rồi mới đọc ref.

Hộp thoại cần bốn việc: **focus vào phần tử đầu hợp lý khi mở** (thường nút an toàn như "Hủy"), **Esc đóng**, **nhốt
focus** trong hộp thoại (Tab và Shift+Tab xoay vòng, phần nền không focus được), **trả focus về phần tử đã mở nó** khi đóng.

```tsx
function Dialog({ open, onClose, children }: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dlg = ref.current;
    if (!dlg) return;
    if (open && !dlg.open) dlg.showModal();     // nền bị vô hiệu, Esc phát sự kiện cancel
    if (!open && dlg.open) dlg.close();         // trình duyệt trả focus về nút đã mở
  }, [open]);
  return <dialog ref={ref} onClose={onClose}>{children}</dialog>;
}
```

- Ưu tiên phần tử `<dialog>` + `showModal()`: trình duyệt lo Esc, vô hiệu phần nền và trả focus. Tự dựng bằng `div`
  thì phải tự làm cả bốn việc: lưu `document.activeElement` vào ref lúc mở, `focus()` phần tử đích, bắt `keydown`
  cho Esc và Tab, gọi `focus()` về phần tử đã lưu trong hàm dọn; hoặc dùng thư viện đã làm sẵn
  (Radix, React Aria) thay vì tự viết bẫy focus.
- Đặt `aria-labelledby` cho tiêu đề; nút mở là phần tử `button`.
- Cách test: `references/testing.md` mục 15.

## 7. Error boundary: reset được

Boundary giữ lỗi cho tới khi bị reset; fallback cần lối ra, nếu không vùng đó hỏng tới khi tải lại trang. Với
`react-error-boundary`:

```tsx
<ErrorBoundary
  resetKeys={[chartRange]}                        // đổi giá trị này thì tự thử dựng lại
  onReset={() => queryClient.resetQueries({ queryKey: ["activity"] })}
  fallbackRender={({ error, resetErrorBoundary }) => (
    <div role="alert">
      <p>Không tải được biểu đồ.</p>
      <button onClick={resetErrorBoundary}>Thử lại</button>
    </div>
  )}
>
  <Suspense fallback={<Skeleton />}><ActivityChart /></Suspense>
</ErrorBoundary>
```

- `resetErrorBoundary()` (nút "Thử lại") và `resetKeys` đổi giá trị đều dựng lại con; `onReset` chạy khi reset để dọn
  nguyên nhân (làm mới cache, đưa state về mặc định). Reset mà không dọn nguyên nhân thì con ném lại đúng lỗi cũ.
- Với dữ liệu từ thư viện state-server, nút thử lại phải làm mới truy vấn (TanStack Query: `QueryErrorResetBoundary`
  hoặc `resetQueries`), không chỉ dựng lại component.
- Lỗi trong trình xử lý sự kiện hoặc mã bất đồng bộ không tới boundary: `useErrorBoundary().showBoundary(error)` đẩy
  lỗi lên boundary gần nhất (hoặc tự `catch` và hiện thông báo tại chỗ).
- Đặt boundary theo **vùng độc lập** (một khối biểu đồ, một route), không một cái ở gốc; phần khác của trang vẫn dùng được.

## 8. Effect đọc giá trị mới nhất mà không chạy lại: `useEffectEvent` hoặc ref

Tình huống: effect đăng ký **một lần** (kết nối, bộ đếm giờ, listener) nhưng trình xử lý bên trong phải thấy `props` hay `state` **mới nhất**. Đưa giá trị vào mảng phụ thuộc thì đăng ký lại mỗi lần giá trị đổi; bỏ khỏi mảng thì trình xử lý đọc giá trị **cũ** (closure cũ). Cả hai đều sai.

- **React 19.2 trở lên: `useEffectEvent`.** Bọc phần "chỉ đọc giá trị mới nhất"; gọi nó **từ bên trong effect**; không đưa nó vào mảng phụ thuộc, không truyền xuống component con, không lưu để gọi ở chỗ khác.

```tsx
function Chat({ roomId, theme }: Props) {
  const onMessage = useEffectEvent((m: Message) => show(m, theme)); // luôn thấy theme mới nhất
  useEffect(() => {
    const conn = connect(roomId);
    conn.on('message', onMessage);
    return () => conn.close();
  }, [roomId]); // đổi theme không nối lại
}
```

- **Bản cũ hơn: ref "mới nhất"**, cập nhật sau mỗi lần commit:

```tsx
const themeRef = useRef(theme);
useEffect(() => { themeRef.current = theme; });      // sau mỗi render
useEffect(() => {
  const conn = connect(roomId);
  conn.on('message', (m) => show(m, themeRef.current));
  return () => conn.close();
}, [roomId]);
```

  Không ghi `ref.current` ngay trong thân render: render phải thuần (mục 1 của `SKILL.md`).
- Chỉ dành cho giá trị **không quyết định khi nào effect phải chạy**; giá trị quyết định (`roomId`) vẫn nằm trong mảng phụ thuộc. Dự án ở bản nào thì theo tài liệu bản đó.

## 9. Form với action (React 19): trạng thái chờ và giữ giá trị khi lỗi

- **Trạng thái chờ:** `useFormStatus()` đọc trạng thái của `<form>` **cha gần nhất**, nên phải gọi trong component **con** nằm trong form (ví dụ `SubmitButton`); gọi ngay trong component vẽ `<form>` thì không thấy form đó. Cách khác: `isPending` (phần tử thứ ba của `useActionState`) có sẵn ở chính component chứa form.

```tsx
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>Gửi</button>;
}
```

- **Giữ giá trị đã nhập khi lỗi:** sau khi action chạy xong, React **đặt lại** các ô không kiểm soát (uncontrolled) của form, kể cả khi action trả về lỗi. Muốn giữ: action trả lại giá trị đã gửi trong state, ô đọc từ đó bằng `defaultValue`.

```tsx
const [state, formAction, isPending] = useActionState(
  async (_prev: State, fd: FormData) => {
    const email = String(fd.get('email'));
    const error = await save(email);
    return error ? { error, email } : { error: null, email: '' };
  },
  { error: null, email: '' },
);
return (
  <form action={formAction}>
    <input name="email" defaultValue={state.email} />
    {state.error && <p role="alert">{state.error}</p>}
    <SubmitButton />
  </form>
);
```

  Đầu vào **kiểm soát** (mục 5 của `SKILL.md`) là cách khác: giá trị nằm trong state của bạn nên không bị đặt lại.
- **Bản 18** không có các API này: dùng state và `onSubmit` (mục 8 của `SKILL.md`). Kiểm tra phía server vẫn bắt buộc; `useOptimistic` chỉ hiển thị tạm trong lúc chờ rồi quay về giá trị thật khi action xong.

## 10. `use()` với promise: ổn định giữa các lần render, tránh thác tải

- **Promise phải ổn định.** `use(promise)` treo (suspend) tới khi promise xong rồi render lại. Promise tạo **trong** component (`use(fetch(...))`) là promise mới mỗi lần render, nên treo mãi. Tạo promise ở chỗ không chạy lại theo render: Server Component hay loader của khung, một cache theo khoá (thư viện state-server, `cache()` của khung), hoặc nâng lên component cha rồi truyền xuống bằng props.
- **Thác tải (waterfall):** yêu cầu đặt trong con chỉ bắt đầu khi con được render; cha chờ xong mới render con thì các yêu cầu nối đuôi nhau. Yêu cầu **độc lập** thì khởi động cùng lúc ở nơi tạo promise, truyền xuống, mỗi con `use` promise của mình trong `Suspense` riêng; cần cả hai cùng lúc thì `Promise.all`.

```tsx
// Server Component hoặc loader: chạy một lần, không lặp theo render ở client
async function Page({ id }: { id: string }) {
  const user = fetchUser(id);     // chưa await: bắt đầu ngay
  const posts = fetchPosts(id);   // bắt đầu cùng lúc
  return (
    <>
      <Suspense fallback={<Spin />}><User p={user} /></Suspense>
      <Suspense fallback={<Spin />}><Posts p={posts} /></Suspense>
    </>
  );
}
function User({ p }: { p: Promise<UserData> }) { const u = use(p); return <h1>{u.name}</h1>; }
```

- `use` đọc được cả Context và gọi được trong điều kiện (khác hook thường). Promise bị từ chối → lỗi nổi lên Error boundary gần nhất (mục 6 của `SKILL.md`), không bọc `try/catch` quanh `use`.

## 11. `React.memo` vô hiệu khi prop mới ở mỗi lần render

`React.memo` so từng prop bằng `Object.is`. Hàm, object hay mảng viết thẳng trong thân component cha (`onSelect={() => select(row.id)}`, `style={{ width: 120 }}`) là **giá trị mới mỗi lần cha render**, nên phép so luôn khác và con vẫn render lại dù đã bọc `memo`. Profiler ghi "props changed" đúng ở các prop đó.

Cách sửa — chỉ làm khi Profiler chứng minh cần (mục 2 của `SKILL.md`):

- **Object hay mảng không phụ thuộc props/state:** hạ ra ngoài component làm hằng (`const CELL_STYLE = { width: 120 }`) hoặc dùng class CSS.
- **Hàm callback:** một hàm **ổn định** nhận định danh, con gọi `onSelect(row.id)`, thay vì tạo `() => select(row.id)` riêng cho mỗi hàng. Hàm ổn định là `useCallback` có mảng phụ thuộc đúng, hoặc hàm vốn ổn định (`setState`, hàm của store).
- **Giá trị suy ra từ props/state:** `useMemo` có mảng phụ thuộc đúng.
- **Dữ liệu từng hàng** giữ nguyên tham chiếu khi không đổi: đừng `map` tạo object mới cho mọi hàng mỗi lần render.

```tsx
const CELL_STYLE = { width: 120 };
const Row = memo(function Row({ row, onSelect }: { row: RowData; onSelect: (id: string) => void }) {
  return <tr style={CELL_STYLE} onClick={() => onSelect(row.id)}>…</tr>;
});
function Grid({ rows }: { rows: RowData[] }) {
  const onSelect = useCallback((id: string) => select(id), [select]); // ổn định
  return <table><tbody>{rows.map((r) => <Row key={r.id} row={r} onSelect={onSelect} />)}</tbody></table>;
}
```

- Hàng nghìn dòng vẫn nặng sau khi sửa: ảo hoá (mục 7 của `SKILL.md`). Dự án đã bật React Compiler thì trình biên dịch tự memo hoá phần lớn trường hợp trên; vẫn đo bằng Profiler trước khi sửa tay.
