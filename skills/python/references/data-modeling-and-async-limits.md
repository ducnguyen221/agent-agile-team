# Chọn kiểu dữ liệu và giới hạn đồng thời cho async

> **Kết luận:** **dữ liệu từ ngoài vào (JSON, API, file) → dùng pydantic** (kiểm lúc chạy); dữ liệu nội bộ đã tin cậy
> → `dataclass` (hoặc `attrs` khi cần validator/converter nhẹ); `TypedDict` chỉ **mô tả hình dạng `dict`** cho
> type checker, không kiểm gì lúc chạy. Biến thể theo trường `type` → union phân biệt + `match` + `assert_never`.
> Gọi nhiều URL bằng async: `Semaphore` giới hạn số yêu cầu đồng thời, bộ điều tốc giới hạn số yêu cầu mỗi giây, mỗi lời
> gọi có timeout.

## 1. Chọn giữa `dataclass`, `TypedDict`, pydantic, `attrs`

| Cần | Chọn | Vì sao |
|---|---|---|
| Parse + kiểm dữ liệu không tin cậy (JSON, body API, file cấu hình) | pydantic `BaseModel` / `TypeAdapter` | kiểm kiểu và ràng buộc lúc chạy, ép kiểu, báo lỗi theo trường |
| Đối tượng nội bộ đã kiểm ở biên, cần gọn, ít phụ thuộc | `@dataclass(frozen=True, slots=True)` | thư viện chuẩn; **không kiểm kiểu lúc chạy** (gán `retries="x"` vẫn qua) |
| Cần validator/converter ngay ở lớp, vẫn nhẹ hơn pydantic | `attrs` (`@define`, `field(validator=…, converter=…)`) | kiểm lúc dựng đối tượng; thêm phụ thuộc |
| Dữ liệu vẫn là `dict` (đọc từ JSON/DB, đưa cho thư viện khác) mà muốn kiểu cho mypy | `TypedDict` | lúc chạy chỉ là `dict` thường, **không kiểm gì**; sai kiểu chỉ bị mypy bắt |
| Bản ghi bất biến đơn giản, giải nén như tuple | `NamedTuple` | xem `references/type-hints-and-dataclasses.md` |

Quy tắc: **kiểm một lần ở biên** (pydantic), bên trong dùng dataclass/kiểu đã kiểm; đừng truyền `dict` thô đi khắp nơi.
`attrs` đã chạy được: `@define class Cfg: retries: int = field(default=3, converter=int, validator=validators.ge(0))`
→ `Cfg("a", "5")` ra `retries=5`; `retries=-1` ném `ValueError`.

## 2. `Literal`, union phân biệt, `match` kiểm đủ nhánh

`Literal` giới hạn giá trị (`Literal["click", "key"]`); mỗi biến thể mang một trường `type: Literal[...]` riêng để phân
biệt. Parse `dict` thô theo trường `type`:

```python
from typing import Annotated, Literal, assert_never   # Python < 3.11: from typing_extensions import assert_never

from pydantic import BaseModel, Field, TypeAdapter


class Click(BaseModel):
    type: Literal["click"]
    x: int
    y: int


class KeyPress(BaseModel):
    type: Literal["key"]
    key: str


Event = Annotated[Click | KeyPress, Field(discriminator="type")]    # union phân biệt theo trường `type`
event_adapter: TypeAdapter[Event] = TypeAdapter(Event)


def describe(event: Event) -> str:
    match event:                    # match: Python 3.10+
        case Click(x=x, y=y):
            return f"click {x},{y}"
        case KeyPress(key=k):
            return f"key {k}"
        case _:
            assert_never(event)     # thêm biến thể mới mà quên nhánh → mypy báo lỗi ở dòng này


event = event_adapter.validate_python({"type": "click", "x": 1, "y": 2})   # dict thô → Click
```

- Union phân biệt nhanh hơn và báo lỗi rõ hơn union thường: `type` không khớp biến thể nào → lỗi `union_tag_invalid`, không đoán.
- `assert_never` kiểm **lúc chạy** chỉ ném lỗi nếu nhánh bị bỏ sót thật sự xảy ra; giá trị chính là **mypy** báo thiếu
  nhánh khi thêm biến thể mới (chạy `mypy` trong CI). Không dùng `case _:` trả giá trị mặc định — nó nuốt biến thể mới.
- Thay `match` ở Python 3.9: `if isinstance(event, Click): … elif isinstance(event, KeyPress): … else: assert_never(event)`
  (mypy vẫn kiểm đủ nhánh). Giới hạn bản Python: `references/uv-migration-and-multiversion-ci.md` mục 3.
- Không có pydantic mà dữ liệu là `dict` có trường `type`: `TypedDict` cho từng biến thể + `Literal` ở trường `type`
  để mypy thu hẹp kiểu; kiểm lúc chạy phải tự viết (`type` không nằm trong tập cho phép → ném lỗi).

## 3. Gọi nhiều URL với async: đồng thời, tốc độ, timeout

Ba giới hạn khác nhau, đừng nhầm:

| Giới hạn | Công cụ | Ý |
|---|---|---|
| Tối đa N yêu cầu **đang chạy cùng lúc** | `asyncio.Semaphore(N)` | bảo vệ socket, bộ nhớ, đối tác |
| Tối đa R yêu cầu **mỗi giây** | bộ điều tốc (khoảng cách tối thiểu `1/R` giữa các lần bắt đầu) hoặc thư viện giới hạn tốc độ | hạn mức của API |
| Tối đa T giây cho **mỗi** yêu cầu | `httpx.Timeout(T)` hoặc `asyncio.timeout(T)` (3.11+) / `asyncio.wait_for` (cũ hơn) | URL treo không giữ chỗ mãi |

```python
import asyncio
import time

import httpx


async def fetch_all(urls: list[str], *, concurrency: int = 10, rate_per_sec: float = 20.0, timeout: float = 5.0):
    sem = asyncio.Semaphore(concurrency)
    interval = 1.0 / rate_per_sec
    lock = asyncio.Lock()
    next_slot = 0.0

    async def wait_slot() -> None:               # xếp mỗi yêu cầu vào một khe cách nhau `interval`
        nonlocal next_slot
        async with lock:
            now = time.monotonic()
            start = max(now, next_slot)
            next_slot = start + interval
        await asyncio.sleep(max(0.0, start - now))

    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
        async def one(url: str):
            async with sem:                      # tối đa `concurrency` yêu cầu cùng lúc
                await wait_slot()
                try:
                    r = await client.get(url)
                    return url, r.status_code
                except httpx.HTTPError as exc:   # gồm timeout, lỗi kết nối: ghi nhận từng URL, không làm hỏng cả lô
                    return url, repr(exc)

        return await asyncio.gather(*(one(u) for u in urls))
```

- Đã chạy với máy chủ ASGI giả: 40 yêu cầu, `rate_per_sec=20`, `Semaphore(5)` mất ~1,95 giây (≈ 40/20) — tốc độ bị bộ điều tốc
  khống chế, số đồng thời bị semaphore khống chế. Với URL thật, thời gian tối thiểu vẫn là `số URL / R` giây.
- `Semaphore` **không** giới hạn tốc độ: 100 yêu cầu nhanh có thể vẫn vượt 20/giây. Nếu API cho phép theo cửa sổ (20 yêu
  cầu mỗi giây tính theo cửa sổ trượt), đặt `rate_per_sec` thấp hơn một chút so với hạn mức.
- `gather` mặc định ném lỗi đầu tiên và để các việc khác chạy tiếp không ai nhận; bắt lỗi từng URL trong `one` (như trên) hoặc
  dùng `return_exceptions=True`. Lô lớn (hàng chục nghìn URL) không tạo hết task một lúc: chia lô hoặc dùng hàng đợi `asyncio.Queue`
  với N worker.
- `httpx` và `aiohttp` đều dùng được cho async; **chọn một** theo thư viện dự án đã dùng. Với `aiohttp`: `aiohttp.ClientTimeout(total=T)`
  và `aiohttp.TCPConnector(limit=N)` đặt trần kết nối đồng thời ở tầng client; vẫn cần semaphore/bộ điều tốc nếu
  phải giới hạn theo giây hay theo từng host. Với `httpx`: `httpx.Limits(max_connections=N)` làm tương tự.
- Tái dùng **một** client cho cả lô (không tạo client mỗi URL). Timeout đặt riêng cho kết nối/đọc khi cần
  (`httpx.Timeout(10.0, connect=3.0)`).

## Nguồn

Tài liệu Python (`typing`: `Literal`, `TypedDict`, `assert_never`; `asyncio`: `Semaphore`, `timeout`, `wait_for`, `gather`),
tài liệu pydantic (union phân biệt, `TypeAdapter`), tài liệu attrs (validators, converters), tài liệu `httpx`
(`Timeout`, `Limits`) và `aiohttp` (`ClientTimeout`, `TCPConnector`). Các mẫu pydantic/dataclass/attrs/asyncio ở trên
đã chạy trên Python 3.12, pydantic 2.12, attrs 25.4.
