# Comprehension, generator, đồng thời và hiệu năng

> **Kết luận:** comprehension cho biến đổi đơn giản, tách thành hàm khi điều kiện rối; generator cho dữ
> liệu lớn. Chọn mô hình đồng thời theo loại việc: **I/O → thread hoặc asyncio**, **CPU → process**.
> Tối ưu bộ nhớ/chuỗi chỉ khi có lý do; đo trước khi tuyên bố nhanh hơn.

## 1. Comprehension và generator

### 1.1. List comprehension

```python
# Nên: comprehension cho biến đổi đơn giản
names = [user.name for user in users if user.is_active]

# Tránh: vòng lặp thủ công cho việc tương tự
names = []
for user in users:
    if user.is_active:
        names.append(user.name)

# Tránh: comprehension quá rối
result = [x * 2 for x in items if x > 0 if x % 2 == 0]

# Nên: tách thành hàm đặt tên rõ
def double_positive_evens(items: Iterable[int]) -> list[int]:
    return [x * 2 for x in items if x > 0 and x % 2 == 0]
```

### 1.2. Biểu thức generator

```python
# Nên: lười, không tạo list trung gian
total = sum(x * x for x in range(1_000_000))

# Tránh: tạo list lớn chỉ để cộng
total = sum([x * x for x in range(1_000_000)])
```

### 1.3. Hàm generator cho dữ liệu lớn

```python
def read_lines(path: str) -> Iterator[str]:
    """Yield stripped lines one at a time."""
    with open(path) as f:
        for line in f:
            yield line.strip()

for line in read_lines("huge.txt"):
    process(line)
```

## 2. Đồng thời

| Loại việc | Chọn | Lý do |
|---|---|---|
| I/O, code đồng bộ (thư viện chặn) | `ThreadPoolExecutor` | GIL nhả khi chờ I/O |
| I/O, đã có hệ sinh thái async | `asyncio` + thư viện async | nhiều kết nối, ít luồng |
| CPU nặng | `ProcessPoolExecutor` | vượt GIL bằng nhiều tiến trình |

### 2.1. Thread cho việc I/O

```python
import concurrent.futures
import urllib.request

def fetch_url(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode()

def fetch_all_urls(urls: list[str]) -> dict[str, str | Exception]:
    results: dict[str, str | Exception] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:  # giữ lỗi theo từng URL, không nuốt
                results[url] = e
    return results
```

### 2.2. Process cho việc CPU

```python
def process_data(data: list[int]) -> int:
    return sum(x ** 2 for x in data)

def process_all(datasets: list[list[int]]) -> list[int]:
    with concurrent.futures.ProcessPoolExecutor() as executor:
        return list(executor.map(process_data, datasets))
```

### 2.3. async/await cho I/O đồng thời

```python
import asyncio
import httpx

async def fetch_all(urls: list[str]) -> dict[str, str | BaseException]:
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(
            *(client.get(url) for url in urls), return_exceptions=True
        )
    return {
        url: r if isinstance(r, BaseException) else r.text
        for url, r in zip(urls, responses)
    }
```

Trong code async không gọi thư viện chặn (`requests`, driver DB đồng bộ, `time.sleep`): chúng khoá cả
vòng sự kiện.

## 3. Bộ nhớ và hiệu năng

### 3.1. `__slots__` khi có rất nhiều đối tượng

```python
class Point:
    __slots__ = ("x", "y")  # không có __dict__, tốn ít bộ nhớ hơn

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
```

Dataclass: `@dataclass(slots=True)` (Python 3.10+).

### 3.2. Không cộng chuỗi trong vòng lặp

```python
# Tránh: O(n²) vì chuỗi bất biến
result = ""
for item in items:
    result += str(item)

# Nên: O(n)
result = "".join(str(item) for item in items)

# Hoặc dựng dần bằng StringIO
from io import StringIO

buffer = StringIO()
for item in items:
    buffer.write(str(item))
result = buffer.getvalue()
```

### 3.3. `functools.lru_cache` — nhớ kết quả hàm thuần, tốn kém

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def parse_rule(rule_text: str) -> Rule:
    return expensive_parse(rule_text)

parse_rule.cache_info()    # CacheInfo(hits=…, misses=…, maxsize=1024, currsize=…)
parse_rule.cache_clear()   # dùng trong test, hoặc khi dữ liệu nguồn đổi
```

- Chỉ cho **hàm thuần** (cùng đối số → cùng kết quả, không tác dụng phụ). Không cho hàm đọc giờ, số ngẫu nhiên,
  CSDL đang đổi, hay hàm async/generator.
- Đối số phải **băm được** (`str`, `int`, `tuple`…); `list`/`dict` thì không. Đối tượng trả về dùng chung giữa các
  lần gọi: đừng cho nơi nhận sửa nó.
- `maxsize` mặc định `128`; `maxsize=None` cho phép nở vô hạn — chỉ khi tập đối số hữu hạn và nhỏ. `functools.cache`
  là dạng không giới hạn.
- **Phương thức:** `@lru_cache` trên method giữ tham chiếu tới `self`, nên đối tượng không bao giờ được giải
  phóng (rò bộ nhớ). Cache một hàm cấp module nhận giá trị thuần, hoặc dùng `cached_property` cho giá trị tính một
  lần theo đối tượng.
- Trong test, xoá cache giữa các test (`cache_clear()` ở fixture) kẻo kết quả rò sang test sau (`testing-fixtures.md` mục 1.8).

### 3.4. Đo trước khi tối ưu: `cProfile`, `tracemalloc`

Đoán chỗ chậm hay chỗ ngốn bộ nhớ thường sai; đo rồi mới sửa, và đo lại sau khi sửa.

```bash
python -m cProfile -o .tmp/out.prof -s cumulative script.py      # CPU: hàm nào tốn thời gian tích luỹ
python -c "import pstats; pstats.Stats('.tmp/out.prof').sort_stats('cumulative').print_stats(15)"
```

```python
import tracemalloc

tracemalloc.start()                         # bật sớm; chỉ theo dõi cấp phát từ lúc này
before = tracemalloc.take_snapshot()
run_workload()
after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:10]:    # dòng nào cấp phát thêm nhiều nhất
    print(stat)
```

- `cProfile` đo theo hàm; chỉ ra "hàm nào" chứ không ra "dòng nào" — khoanh vùng xong mới vào trong hàm.
  Bản ghi `.prof` ghi vào `.tmp/` rồi xoá khi xong.
- `tracemalloc` cho biết **dòng** nào cấp phát bộ nhớ và so được hai ảnh chụp để bắt rò; theo dõi nhiều khung ngăn
  xếp (`tracemalloc.start(25)`) tốn thêm CPU và bộ nhớ, bật khi cần.
- Tối ưu có đo (trước/sau, cùng dữ liệu) mới ghi vào báo cáo; "có vẻ nhanh hơn" không phải bằng chứng.
- Nguồn: tài liệu Python (`functools`, `profile`/`cProfile`, `tracemalloc`).
