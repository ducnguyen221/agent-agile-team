# Timeout từng tầng, lỗi nhập liệu theo trường, tác vụ dài

> **Kết luận:** đặt **một hạn chót** ở tầng ngoài cùng rồi chia xuống: mỗi tầng trong có timeout nhỏ hơn phần thời gian
> còn lại của tầng ngoài. Cô lập mỗi dependency bằng bulkhead (trần đồng thời riêng) và ngắt mạch có ngưỡng ghi rõ.
> Lỗi nhập liệu trả danh sách theo trường (`field` + `code` + `message`), câu tiếng Việt nói **điều gì sai và sửa thế nào**,
> không tiết lộ tài khoản có tồn tại hay không. Tác vụ dài có trạng thái `failed` tường minh, nhịp tim (`heartbeat`) để
> phát hiện chết im lặng, và quy tắc thử lại ghi trước.

## 1. Timeout từng tầng, bulkhead, ngưỡng ngắt mạch

**Nguyên tắc timeout theo tầng.** Không có timeout thì một dependency chậm giữ luồng/kết nối đến khi hết tài nguyên; timeout
đặt sai tầng thì tầng ngoài bỏ cuộc trong khi tầng trong vẫn làm việc vô ích. Quy tắc:

1. Chốt **hạn chót của người dùng** trước (ví dụ yêu cầu phải trả lời trong 3 giây) — đó là tầng ngoài cùng.
2. Mỗi tầng trong nhận **thời gian còn lại**, không nhận con số cố định: timeout của một lời gọi = `min(trần của lời gọi đó,
   thời gian còn lại)`; còn lại ≤ 0 thì không gọi nữa, báo lỗi ngay. Tổng các lời gọi tuần tự **cộng cả các lần retry**
   phải nằm trong hạn chót; retry tốn thời gian của chính mình.
3. Tầng trong **nhỏ hơn** tầng ngoài (ví dụ minh hoạ: người dùng 3 s → handler 2,5 s → lời gọi dịch vụ ngoài 1 s, tối đa
   một lần thử lại → truy vấn CSDL 0,8 s). Tầng ngoài nhỏ hơn tầng trong là lỗi cấu hình: client đã bỏ đi mà server còn
   chạy.
4. **Truyền hạn chót qua biên dịch vụ.** gRPC có sẵn deadline: server tự huỷ RPC khi hạn chót của client qua, và khi server
   lại làm client thì hạn chót được chuyển tiếp (đổi thành timeout, trừ thời gian đã trôi); tiến trình con do ứng dụng sinh
   ra thì ứng dụng phải tự dừng. Với HTTP thì tự quy ước một header (ví dụ thời gian còn lại tính bằng mili-giây) và tầng nhận
   dùng nó thay cho timeout cố định.
5. **Chọn con số từ số đo**, không đoán: lấy phân vị độ trễ cao của dependency (ví dụ p99 hoặc p99.9) ứng với tỉ lệ
   "timeout nhầm" chấp nhận được, rồi kiểm bằng test tải (gRPC docs: xác nhận deadline bằng load test; AWS Builders'
   Library, "Timeouts, retries, and backoff with jitter"). Tách **timeout kết nối** (ngắn) khỏi **timeout chờ phản hồi**.

```python
import asyncio, time

class DeadlineExceeded(Exception): ...

class Deadline:
    def __init__(self, seconds: float):
        self.at = time.monotonic() + seconds

    def remaining(self) -> float:
        left = self.at - time.monotonic()
        if left <= 0:
            raise DeadlineExceeded
        return left

    def timeout_for(self, cap: float) -> float:       # timeout của một lời gọi con
        return min(cap, self.remaining())

async def call_dep(deadline: Deadline, cap: float, work):
    try:
        async with asyncio.timeout(deadline.timeout_for(cap)):     # asyncio.timeout: Python 3.11+
            return await work()
    except TimeoutError as exc:
        raise DeadlineExceeded from exc
```

Đã chạy lại mẫu trên: gọi 0,2 s trong hạn chót 1 s thành công và còn 0,8 s; gọi 0,9 s sau đó vượt hạn chót nên ném
`DeadlineExceeded` thay vì chờ hết 2 s trần riêng. Thư viện đồng bộ (HTTP client, driver CSDL) **không** bị `asyncio.timeout` ngắt
giữa chừng: đặt timeout ngay trong client (`httpx.Timeout(5.0, connect=1.0)`, tham số timeout của driver).

**Bulkhead (vách ngăn) — mỗi dependency một trần đồng thời riêng.** Một dependency chậm không được ăn hết luồng/kết nối của cả
dịch vụ. Hai kiểu: **semaphore** (đếm số lời gọi đang chạy, lời gọi vượt trần bị từ chối ngay hoặc chờ có hạn) và **pool
luồng riêng** (hàng đợi giới hạn + số luồng cố định cho dependency đó). Mặc định tham khảo của Resilience4j: semaphore
`maxConcurrentCalls` = 25, `maxWaitDuration` = 0 (không chờ, từ chối ngay); pool luồng có `queueCapacity` = 100. Với Python:
`asyncio.Semaphore(N)` mỗi dependency cho code async; `ThreadPoolExecutor(max_workers=N)` **riêng** từng dependency cho code
chặn (đừng dùng chung một pool cho mọi thứ). Vượt trần → lỗi rõ (`503` kèm `Retry-After`/lỗi nội bộ có mã), không xếp hàng
vô hạn; trần chọn từ tải đồng thời bình thường × hệ số dự phòng, kiểm bằng test tải. Đã chạy lại: bulkhead hai chỗ nhận hai
lời gọi và từ chối lời gọi thứ ba ngay (`bulkhead payments full`).

**Ngưỡng ngắt mạch.** Mục 5 của `references/retry-and-user-messages.md` nói cơ chế; đây là cách chọn số. Điểm khởi đầu (mặc định
của Resilience4j, không phải chân lý): ngưỡng tỉ lệ lỗi 50 % trong cửa sổ 100 lệnh gọi gần nhất, **tối thiểu 100 lệnh gọi** mới
tính, mở 60 giây rồi nửa mở cho 10 lệnh gọi thử, lệnh gọi chậm hơn 60 giây tính là chậm. Chỉnh theo dịch vụ:

- Lưu lượng thấp (vài yêu cầu mỗi giây) thì cửa sổ 100 lệnh gọi mất rất lâu mới đầy → dùng cửa sổ **theo thời gian** (ví dụ 30-60
  giây) và hạ số lệnh gọi tối thiểu, không thì ngắt mạch không bao giờ mở.
- Cửa sổ ngắn hơn phản ứng nhanh nhưng dễ mở nhầm vì một đợt lỗi nhỏ; đồng hồ mở ngắn thử lại sớm nhưng đè lên dependency
  đang hồi phục. Ghi ngưỡng vào cấu hình, **kèm lý do chọn**, và theo dõi số lần chuyển trạng thái để chỉnh.
- Chỉ tính lỗi do dependency (timeout, 5xx, từ chối kết nối); không tính 4xx nghiệp vụ.

## 2. Lỗi nhập liệu theo trường, câu tiếng Việt, không lộ tài khoản

**Hình dạng `details` theo trường.** Một yêu cầu sai nhiều chỗ thì trả **tất cả** một lượt (không báo lỗi đầu tiên rồi bắt người dùng
thử lại từng cái). Mỗi phần tử gồm đường dẫn trường, mã lỗi **ổn định** theo trường (client dịch/nhấn mạnh theo mã) và câu cho người
dùng. RFC 9457 (Problem Details) ví dụ cùng ý: mảng `errors` mỗi phần tử có `detail` và `pointer` tới chỗ sai.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Thông tin chưa hợp lệ. Vui lòng kiểm tra các trường được đánh dấu.",
    "request_id": "req_8f2c1a",
    "details": [
      {"field": "email", "code": "INVALID_FORMAT", "message": "Email chưa đúng định dạng, ví dụ ten@congty.vn."},
      {"field": "items[2].quantity", "code": "OUT_OF_RANGE", "message": "Số lượng phải từ 1 đến 99."}
    ]
  }
}
```

- `field` là đường dẫn trong thân yêu cầu (`items[2].quantity`) hoặc tên tham số truy vấn; mã theo trường lấy từ **bảng một chỗ**
  (`REQUIRED`, `INVALID_FORMAT`, `TOO_SHORT`, `OUT_OF_RANGE`, `ALREADY_USED`…), không chép nguyên mã của thư viện kiểm.
- **Không dội lại giá trị người dùng đã gửi** (trường `input` của Pydantic/`exc.errors()`): có thể là mật khẩu hay số thẻ.
- Quy tắc dùng chung với phong bì lỗi ở `SKILL.md` mục 2; mã HTTP `422` (hoặc `400` theo quy ước API — skill `api-design`).

**Viết câu tiếng Việt cho người dùng.** Mỗi câu trả lời hai ý: **điều gì chưa đúng** và **cần làm gì**; ngắn, không thuật ngữ, không
mã nội bộ, không đổ lỗi.

| Tránh | Nên |
|---|---|
| "Lỗi! Dữ liệu không hợp lệ." | "Số điện thoại cần 10 chữ số, bắt đầu bằng số 0." |
| "Bạn nhập sai mật khẩu." | "Email hoặc mật khẩu chưa đúng. Vui lòng kiểm tra và thử lại." |
| "Exception: connection timeout" | "Hệ thống đang bận. Vui lòng thử lại sau ít phút." |
| "Request failed with status 500" | "Có sự cố ở phía chúng tôi. Vui lòng thử lại sau; nếu vẫn lỗi, gửi mã tham chiếu `req_8f2c1a` cho bộ phận hỗ trợ." |

Thống nhất cách xưng hô cho cả giao diện (một cách: không xưng, hoặc "bạn"), dùng cùng một thuật ngữ cho cùng một khái niệm, đặt câu
ở bảng tra duy nhất (`references/retry-and-user-messages.md` mục 3) kèm bản dịch; lỗi hệ thống kèm **mã tham chiếu** (request id) để
hỗ trợ tra log, không kèm chi tiết kỹ thuật (nguyên tắc chung: thông điệp lỗi nói rõ, lịch sự, hướng dẫn cách sửa — Nielsen Norman Group,
error-message guidelines).

**Không lộ tài khoản nào tồn tại.** Báo "email này đã được đăng ký", "không có tài khoản với email này" hay trả lời nhanh/chậm khác
nhau giúp kẻ xấu **liệt kê tài khoản** (account enumeration). OWASP (Forgot Password Cheat Sheet) yêu cầu trả **một thông điệp giống
nhau** cho tài khoản có và không có, và thời gian phản hồi **giống nhau**.

- Quên mật khẩu: luôn "Nếu email này có tài khoản, chúng tôi đã gửi hướng dẫn đặt lại mật khẩu"; việc gửi thư thực tế làm nền
  để thời gian trả lời không phụ thuộc tài khoản có tồn tại.
- Đăng nhập sai: một câu cho cả "sai email" và "sai mật khẩu" (bảng trên).
- Đăng ký trùng email: trả cùng một màn "Kiểm tra email để hoàn tất đăng ký" và **gửi thư tới địa chỉ đó** nói hoặc "xác nhận đăng ký"
  hoặc "đã có tài khoản, hãy đăng nhập/đặt lại mật khẩu". Chấp nhận báo thẳng "đã đăng ký" là quyết định đánh đổi (tiện cho người dùng,
  lộ thông tin) — phải được người sở hữu sản phẩm duyệt, kèm giới hạn tốc độ theo IP/địa chỉ.
- Log phía server vẫn ghi đúng lý do (có mã, không kèm email/mật khẩu thô).

## 3. Tác vụ dài: trạng thái `failed`, phát hiện chết im lặng, thông báo, thử lại

Tác vụ chạy nền (xuất báo cáo, nhập file lớn, gọi hệ thống ngoài) không có người chờ ở đầu dây — lỗi dễ biến mất. Hợp đồng gồm:

**Mô hình trạng thái** (một bảng/bản ghi cho mỗi tác vụ):

| Trạng thái | Nghĩa | Chuyển đến |
|---|---|---|
| `queued` | đã nhận, chưa ai chạy | `running`, `cancelled` |
| `running` | worker đang chạy, có `heartbeat_at` | `succeeded`, `failed`, `queued` (thử lại), `cancelled` |
| `succeeded` | xong, có kết quả/đường tải | (cuối) |
| `failed` | hỏng, có `error_code` + câu cho người dùng + `attempt` | `queued` (người dùng bấm thử lại), (cuối) |
| `cancelled` | người dùng/hệ thống huỷ | (cuối) |

Chỉ chuyển theo bảng (cập nhật có điều kiện: `UPDATE … WHERE id = ? AND status = ?`), ghi `started_at`, `finished_at`, `attempt`,
`error_code`. **Thất bại phải để lại `failed` có mã lỗi**, không để tác vụ biến mất hay kẹt ở `running` mãi; hết thời gian tối đa của
cả tác vụ (hạn chót tổng) cũng là `failed` với mã `TIMEOUT`. Endpoint hỏi trạng thái và khuôn `202`: skill `fastapi`, `references/background-and-streaming.md`.

**Phát hiện tác vụ chết im lặng.** Worker bị kill hay treo không kịp ghi `failed`; chỉ trạng thái `running` còn đó. Phát hiện bằng
**nhịp tim**:

- Worker ghi `heartbeat_at = now()` định kỳ (khoảng H giây, có thể kèm tiến độ) khi đang chạy.
- Một **bộ quét** (job định kỳ) tìm `running` mà `heartbeat_at` cũ hơn ngưỡng (ví dụ 3 × H): còn lượt thử và việc idempotent → đưa
  về `queued` (tăng `attempt`); hết lượt → `failed` với mã `WORKER_LOST`. Mẫu PostgreSQL (chưa chạy trên CSDL thật):

```sql
UPDATE jobs SET status = 'queued', attempt = attempt + 1
 WHERE status = 'running' AND heartbeat_at < now() - interval '90 seconds' AND attempt < max_attempts;
UPDATE jobs SET status = 'failed', error_code = 'WORKER_LOST', finished_at = now()
 WHERE status = 'running' AND heartbeat_at < now() - interval '90 seconds' AND attempt >= max_attempts;
```

- Hàng đợi có sẵn cơ chế tương tự: Amazon SQS dùng **visibility timeout** (mặc định 30 giây): worker chết không xoá thông điệp thì
  nó hiện lại cho worker khác; việc dài thì gia hạn định kỳ bằng `ChangeMessageVisibility` (tối đa 12 giờ kể từ lần nhận đầu), tức "nhịp
  tim" của hàng đợi. Temporal có `Heartbeat Timeout`: thiếu nhịp tim thì hoạt động bị coi là hỏng (worker chết hay treo) và thử lại
  nếu cấu hình; nên dùng nhịp tim ngắn và thường xuyên cho việc dài.
- Cảnh báo thêm: `queued` quá lâu (không có worker), số `failed`/`WORKER_LOST` tăng.

**Thông báo cho người dùng.** Người dùng thấy trạng thái bất cứ lúc nào (`queued`, `running` kèm tiến độ nếu có, `failed` kèm câu
tiếng Việt và hướng đi tiếp). Việc dài hơn dự kiến → hiện "đang xử lý lâu hơn bình thường" thay vì quay vô hạn. Khi `failed` hay `succeeded`
báo bằng kênh người dùng đã chọn (trong ứng dụng, email) — một lần cho mỗi trạng thái cuối. Câu thất bại theo bảng tra (mục 2), kèm mã tham chiếu.

**Cho thử lại hay không** (ghi trước theo `code`, cùng bảng cờ "thử lại được" ở `references/retry-and-user-messages.md` mục 4):

- Tự thử lại chỉ khi: lỗi thoáng qua **và** việc idempotent (có khoá khử trùng) **và** `attempt < max_attempts`; backoff + jitter giữa các lần.
- Lỗi vĩnh viễn (dữ liệu sai, thiếu quyền) → `failed` ngay, **không** thử lại tự động; câu cho người dùng nói cần sửa gì.
- Hết lượt tự động → `failed` + cảnh báo cho người vận hành; người dùng có nút "Thử lại" tạo lượt mới (cùng khoá khử trùng, giữ
  liên kết với tác vụ cũ), chỉ hiện khi mã lỗi cho phép.
- Việc không idempotent (gửi tiền, gửi thư) không tự thử lại sau `WORKER_LOST`: không biết nó đã chạy tới đâu — chuyển người xử lý.

## Nguồn

gRPC (Deadlines: hạn chót, truyền hạn chót, huỷ phía server); AWS Builders' Library (Timeouts, retries, and backoff with jitter);
Resilience4j (mặc định CircuitBreaker và Bulkhead); RFC 9457 (Problem Details, ví dụ `errors` có `detail` và `pointer`);
OWASP Forgot Password Cheat Sheet (thông điệp và thời gian phản hồi giống nhau); Nielsen Norman Group (hướng dẫn thông điệp lỗi);
Amazon SQS (visibility timeout, gia hạn, dead-letter); Temporal (Heartbeat Timeout). Mẫu Python đã chạy trên Python 3.12; mẫu SQL
chưa chạy trên CSDL thật.
