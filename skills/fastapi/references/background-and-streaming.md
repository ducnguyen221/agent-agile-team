# Tác vụ nền và phản hồi dạng luồng (stream)

> **Kết luận:** `BackgroundTasks` chỉ cho việc **nhẹ, mất cũng chấp nhận được** chạy sau khi đã trả response, cùng
> tiến trình; việc nặng, dài hay không được mất đi qua hàng đợi riêng và endpoint trả `202` kèm mã việc.
> Phản hồi dài (file, dòng dữ liệu, sự kiện) trả theo luồng bằng generator, không dựng cả body trong bộ nhớ.

## 1. Chọn đường: tác vụ nền, hàng đợi hay chờ ngay

| Việc | Đường | Lý do |
|---|---|---|
| Gửi mail thông báo, ghi log kiểm toán, dọn file tạm — nhanh, mất một lần cũng chịu được | `BackgroundTasks` | chạy sau response, không thêm hạ tầng |
| Xử lý nặng (CPU, hàng nghìn dòng), mất là không chấp nhận, cần chạy lại khi lỗi, cần chạy trên nhiều tiến trình/máy | hàng đợi việc riêng (Celery, hoặc worker đọc hàng đợi/CSDL của dự án) | `BackgroundTasks` chạy **cùng tiến trình** với app, không nhân lên theo máy |
| Kết quả cần ngay để trả client | làm trong request (`await`) | không có gì để "nền" |
| Việc dài mà client cần biết kết quả | `202 Accepted` + mã việc + endpoint hỏi trạng thái | không giữ kết nối HTTP hàng phút |

Nguồn: tài liệu chính thức FastAPI, mục Background Tasks (việc nặng cần nhiều tiến trình thì dùng công cụ như
Celery) và Custom Response / Stream Data.

## 2. `BackgroundTasks`

```python
from fastapi import BackgroundTasks, FastAPI

def send_welcome_mail(email: str) -> None:   # def hay async def đều được
    ...   # tự mở kết nối/phiên riêng, bắt lỗi và log tại đây

@app.post("/users", status_code=201)
async def create_user(body: UserCreate, background: BackgroundTasks, svc: UserSvcDep):
    user = await svc.create(body)            # commit XONG rồi mới đăng ký việc nền
    background.add_task(send_welcome_mail, user.email)
    return user
```

- Việc nền chạy **sau khi response đã gửi**; client không thấy lỗi của nó. Vì vậy: bắt lỗi và log bên trong hàm
  (loại lỗi + mã, không `str(exc)` thô — skill `error-handling`), nếu không lỗi chỉ hiện ở log máy chủ và việc
  mất im lặng.
- `BackgroundTasks` dùng được cả trong dependency; mọi việc đăng ký ở mọi tầng được gộp và chạy sau response.
- **Đừng đưa đối tượng gắn với request vào việc nền**: phiên CSDL của `Depends(get_db)`, đối tượng `Request`, file
  upload đang mở. Truyền **giá trị thuần** (id, email) và để hàm nền tự mở phiên/client của nó.
- Đăng ký việc **sau khi** transaction đã commit; đăng ký trước thì có thể gửi mail cho bản ghi chưa tồn tại.
- Việc nền chạy lại khi tiến trình chết? Không — `BackgroundTasks` không bền. Cần bền → mục 1, dòng hàng đợi;
  khi đó hàm nền phải idempotent vì có thể chạy hai lần.
- Không dùng `BackgroundTasks` để chạy vòng lặp vô hạn hay việc theo lịch: dùng bộ lập lịch/worker riêng.

## 3. Endpoint `202` cho việc dài

```python
@app.post("/reports", status_code=202)
async def start_report(body: ReportRequest, svc: ReportSvcDep) -> ReportAccepted:
    job_id = await svc.enqueue(body)                       # ghi việc vào hàng đợi/bảng việc
    return ReportAccepted(job_id=job_id, status_url=f"/reports/{job_id}")

@app.get("/reports/{job_id}")
async def report_status(job_id: str, svc: ReportSvcDep) -> ReportStatus:
    return await svc.status(job_id)                        # queued | running | done | failed (+ link kết quả)
```

Khuôn trạng thái, mã lỗi và hợp đồng của cặp endpoint: skill `api-design`. Việc thất bại phải để lại trạng thái
`failed` kèm mã lỗi (không kèm secret), không biến mất.

## 4. Stream: file, dòng dữ liệu, sự kiện

```python
from collections.abc import AsyncIterable
from fastapi.responses import StreamingResponse

@app.get("/exports/{export_id}.csv", response_class=StreamingResponse)
async def export_csv(export_id: str, svc: ExportSvcDep) -> AsyncIterable[bytes]:
    async for chunk in svc.iter_csv(export_id):     # từng khối nhỏ, không dựng cả file trong bộ nhớ
        yield chunk
```

- `StreamingResponse` nhận generator (đồng bộ hay bất đồng bộ); cách khuyến nghị hiện nay là khai
  `response_class=StreamingResponse` rồi `yield` ngay trong hàm route, chú thích kiểu `AsyncIterable[bytes]`
  (hoặc `Iterable[...]`). Đặt `media_type` bằng cách kế thừa lớp hoặc tham số khi dựng.
- Dùng **generator bất đồng bộ** có `await` thật (hoặc `await anyio.sleep(0)` giữa các khối): huỷ tác vụ chỉ xảy
  ra tại điểm `await`, generator không có `await` vẫn chạy tiếp sau khi client đã bỏ đi.
- File mở trong generator thì bọc bằng `with` — file đóng khi luồng kết thúc hoặc bị huỷ.
- Generator đồng bộ chạy trong threadpool; gọi thư viện chặn trong generator `async` là lỗi cũ "chặn vòng sự kiện"
  (`SKILL.md` mục 3, Async).
- **Lỗi giữa luồng:** response đã bắt đầu thì không đổi được mã trạng thái nữa. Kiểm mọi điều kiện (quyền, tồn tại,
  tham số) **trước** `yield` đầu tiên; lỗi sau đó chỉ có thể log và cắt luồng, hoặc gửi một bản ghi lỗi ngay trong
  luồng nếu định dạng cho phép (JSON Lines).
- **Sự kiện máy chủ đẩy (SSE):** FastAPI từ `0.135.0` có `EventSourceResponse` trong `fastapi.sse`: khai
  `response_class=EventSourceResponse`, `yield` từng mục, mỗi mục được mã hoá JSON thành trường `data:`; bản này tự
  gửi ping giữ kết nối và hỗ trợ `Last-Event-ID`. Bản FastAPI cũ hơn chưa có: kiểm bản đang dùng trước khi viết,
  hoặc dùng `StreamingResponse` với `media_type="text/event-stream"` và tự định dạng.
- Qua proxy/cổng: kiểm bộ đệm của proxy (tắt đệm cho đường luồng) và thời gian chờ nhàn rỗi, kẻo luồng bị cắt
  hoặc gom lại tới khi kết thúc.

## 5. Kiểm tra

- Test việc nền: gọi hàm nền trực tiếp; test route chỉ kiểm việc **đã được đăng ký** (hoặc mock `add_task`), không
  đợi thời gian.
- Test luồng: dùng client ASGI đọc từng khối (`aiter_bytes`), kiểm khối đầu tới trước khi luồng kết thúc, và
  kiểm đường lỗi trước `yield` trả đúng mã trạng thái.
