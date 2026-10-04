---
skill: python
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 93927b63539f410932e88592bb6c6d1dac0ca10b
date: 2026-10-04
result: "strict 3/7 (+4 partial, 0 fail) — below threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: "afbbece2a6f1f6a07"
  answers: a205edc92d607789a
---

Đã đọc: `<gốc worktree>/skills/python/SKILL.md` `references/testing-mocking-async.md`, `references/packaging-and-tooling.md`, `references/type-hints-and-dataclasses.md`, `references/testing-fixtures.md`, `references/generators-concurrency-performance.md`, `references/testing-organization.md`, `references/testing.md`

# Thử truy xuất - python

> **Kết luận:** strict 3/7 (+4 partial, 0 fail), dưới ngưỡng. Bộ câu MỚI (lượt độc lập `TK13`, người soạn không đọc skill) phủ các góc khác của `description`; 2 trong 6 câu tình huống Đạt hẳn, các câu còn lại trỏ đúng nơi nhưng thiếu nội dung (mục "Thiếu nội dung" bên dưới). Câu ranh giới Đạt. Bộ câu cũ giữ ở mục lịch sử.

Câu hỏi do người soạn mới (id ở `agent_ids`) viết từ `description` và danh sách câu cũ, không đọc skill. Cột "Mục kỳ vọng" và điều kiện Đạt ghi vào file nháp
`.tmp/python-expected.md` lúc 2026-10-04 10:45:54 +07:00, **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm); file nháp chép giữ mtime vào
`expected/python-expected.md`. Bài trả lời trọn của chủ thể (id ở `agent_ids`, 11 lượt công cụ) và bảng chấm ở `evidence/TK13/python-retrieval.md`
trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>`
vì repo chặn tên người dùng. Chủ thể được dặn nói thẳng khi skill không có phần câu hỏi cần, không dùng kiến thức ngoài.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Mình có một service FastAPI-less, chỉ là thư viện xử lý dữ liệu, hàm `fetch_prices(symbols)` gọi API ngoài bằng `httpx.AsyncClient` và chạy bằng `asyncio`. Mình cần viết test bằng pytest cho nó mà không gọi mạng thật, và phải test được case timeout lẫn case trả về 500. Dùng `pytest-asyncio` hay `anyio`, mock `AsyncClient` bằng `respx`, `AsyncMock` hay `monkeypatch`, và đặt `asyncio_mode` thế nào cho gọn? | `references/testing-mocking-async.md` › 1.3. Mock ngoại lệ bằng `side_effect` + › 2. Test code async (pytest-asyncio, `asyncio_mode = "auto"`, `AsyncMock`) | `references/testing-mocking-async.md` › 1.3, › 2 | Đạt (phần phụ thiếu: so sánh với anyio, `respx`, dựng response `httpx` cho timeout và lỗi 500) |
| 2 | Repo Python của team mình (khoảng 120 file) đang dùng song song `black`, `isort`, `flake8` và `pip-tools`, mỗi PR CI mất gần 6 phút chỉ để lint với cài dependency. Mình muốn gom hết sang `ruff` + `uv`. Cấu hình `[tool.ruff]` chọn rule set nào (`E`, `F`, `I`, `UP`, `B`?), và chuyển `requirements.txt` sang `uv.lock` rồi cache trong GitHub Actions ra sao để CI xuống dưới 2 phút? | `SKILL.md` › 3. Công cụ: uv, ruff, mypy, pytest (`ruff format` thay black + isort, `uv sync --locked`) + `references/packaging-and-tooling.md` › 4. `pyproject.toml` (`select = ["E","F","I","N","W","B","UP"]`) | `SKILL.md` › 3; `references/packaging-and-tooling.md` › 4 | Một phần (có rule set và `uv sync --locked`; thiếu chuyển requirements và cache CI) |
| 3 | Mình có hàm `parse_record(raw: dict)` nhận JSON từ nhiều nguồn, có 3 loại record (`"order"`, `"refund"`, `"adjustment"`) với các field khác nhau, hiện toàn trả `dict` và dùng `if raw["type"] == ...` khắp nơi. Mình muốn mô hình hoá thành kiểu rõ ràng và validate lúc đọc. Chọn `dataclass`, `TypedDict`, `pydantic` hay `attrs`, và dùng `Literal` + discriminated union ra sao để `match` bắt đủ các nhánh? | `references/type-hints-and-dataclasses.md` › 2. Dataclass và NamedTuple (2.2 dataclass có kiểm hợp lệ) + › 1.4 `Protocol`; phần `Literal`, union phân biệt, `TypedDict`, `match` không có | `references/type-hints-and-dataclasses.md` › 2, › 1 | Một phần (chỉ dataclass có kiểm hợp lệ trong `__post_init__`) |
| 4 | Mình viết thư viện nội bộ, cần chạy được trên Python 3.9 đến 3.13 và test trên cả 5 phiên bản đó trên CI. Mình đang phân vân giữa `tox`, `nox` và ma trận trong GitHub Actions với `uv python install`. Ngoài ra một số cú pháp như `X \| None` và `match` không có ở 3.9. Chọn công cụ nào và xử lý tương thích cú pháp thế nào cho đỡ gãy? | `references/packaging-and-tooling.md` › 4. `pyproject.toml` (`requires-python`, `target-version`) + `references/type-hints-and-dataclasses.md` › 1.2 (kiểu dựng sẵn 3.9+ và cú pháp cũ); ma trận nhiều phiên bản/tox/nox không có | `references/type-hints-and-dataclasses.md` › 1.2; `references/packaging-and-tooling.md` › 4, › 6 | Một phần (có ghi chú cú pháp 3.9/3.10 và `requires-python`; thiếu công cụ ma trận phiên bản) |
| 5 | Bộ test của mình có 900 test, riêng một nhóm test tích hợp cần Postgres thật chạy mất 4 phút, còn lại chạy 20 giây. Mình muốn tách ra để chạy nhanh khi dev nhưng vẫn chạy đủ ở CI, và có vài test cần chạy với 12 tổ hợp tham số. Dùng `pytest.mark`, `-m`, `parametrize` với `ids`, hay `pytest-xdist` để chia, và đăng ký marker trong `pyproject.toml` thế nào để khỏi bị cảnh báo? | `references/testing-fixtures.md` › 2. Parametrize (2.2 `ids`) + › 3. Marker và chọn test (`-m`, đăng ký marker, `--strict-markers`) + `references/testing-organization.md` › 6. Cấu hình pytest | `references/testing-fixtures.md` › 2, › 3; `references/testing-organization.md` › 6; `references/testing.md` › 4 | Đạt (phần phụ thiếu: `pytest-xdist`, dựng Postgres thật ở CI) |
| 6 | Script xử lý của mình dùng `requests` trong vòng lặp gọi 5.000 URL, chạy tuần tự mất khoảng 40 phút và còn đụng giới hạn 20 request/giây của server. Mình cân nhắc `ThreadPoolExecutor`, `asyncio` với `aiohttp` hay `multiprocessing`. Chọn cái nào, giới hạn đồng thời bằng `Semaphore` thế nào, và xử lý khi một URL treo mãi không trả về? | `references/generators-concurrency-performance.md` › 2. Đồng thời (bảng chọn thread/asyncio/process; 2.1 `ThreadPoolExecutor` với `max_workers`) | `references/generators-concurrency-performance.md` › 2 | Một phần (có bảng chọn thread/asyncio/process và `max_workers`; thiếu giới hạn tốc độ và timeout) |
| 7 | Query của mình chạy từ Python qua `psycopg` trên bảng `orders` 40 triệu dòng, `EXPLAIN ANALYZE` cho thấy Seq Scan dù đã có index trên `(customer_id, created_at)` và điều kiện lọc `WHERE created_at >= now() - interval '7 days' ORDER BY created_at DESC LIMIT 50`. Mình nên tạo index kiểu gì, thứ tự cột ra sao để planner chịu dùng index? | mục khác: skill `postgres` (từ `SKILL.md` › 8. Liên quan: `postgres`) | mục khác: `postgres` (từ `SKILL.md` › 8. Liên quan) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Câu 2: Chuyển `requirements.txt` hay `pip-tools` sang `pyproject.toml` và `uv.lock`, cấu hình cache uv trong GitHub Actions, mục tiêu thời gian CI.
- Câu 3: So sánh `dataclass`, `TypedDict`, `pydantic`, `attrs`; `Literal` và union phân biệt; `match` kiểm đủ nhánh; parse `dict` thô theo trường `type`.
- Câu 4: So sánh `tox`, `nox`, ma trận GitHub Actions với `uv python install`; cách thay `match` ở 3.9; giới hạn của `from __future__ import annotations`.
- Câu 6: `asyncio.Semaphore`, giới hạn 20 request/giây, timeout cho URL treo; skill chỉ dùng `httpx`, không nhắc `aiohttp`.
- Điều kiện Đạt ghi trước ở file nháp có vài chỗ đánh dấu "phần phụ"; lượt này **không** nương theo dấu đó: việc câu hỏi nêu đích danh mà skill không có thì câu tính Một phần. Các phần phụ thiếu ở câu Đạt ghi ngay trong cột "Kết quả".
- Skill chưa sửa ở lượt này (việc của điều phối); `skill_sha` là băm cây skill hiện tại.

## Lịch sử

Lượt trước (`TK11`/`TK12`, bộ câu cũ, ngày 2026-10-04, `skill_sha` 93927b63539f410932e88592bb6c6d1dac0ca10b, id chủ thể a26cd825a62c1e64e): `result` là `strict 6/6 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 6/6`. Bảng cũ giữ nguyên chữ, nhãn `Cũ-n`:

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| Cũ-1 | Class `Config` đọc từ biến môi trường, gói thành CLI có `pyproject.toml` với entry point `mytool = mytool.cli:main`, src layout. Bố trí `src/mytool/`, `__main__.py`, `[project.scripts]` thế nào, và `uv build` ra wheel cài được ở máy khác? | `references/packaging-and-tooling.md` › 1 (src layout), › 4 (`pyproject.toml`), › 5 (`[project.scripts]`, `__main__.py`, `main()` trả mã thoát, `uv build`, kiểm wheel ở môi trường sạch) | `references/packaging-and-tooling.md` › 5. Công cụ dòng lệnh; › 1; › 4 | Đạt |
| Cũ-2 | `mypy --strict` báo `Missing type parameters for generic type "dict"` và `Incompatible return type` ở hàm trả `list \| None`. Dùng `Protocol`, `TypeVar` hay `overload` để type hàm `get_first(items)` trả phần tử đầu hoặc `None`? | `references/type-hints-and-dataclasses.md` › 1.3 `TypeVar`, › 1.4 `Protocol`, › 1.2; `overload` và `mypy --strict` không có | `references/type-hints-and-dataclasses.md` › 1.3, › 1.4, › 1.2 | Đạt |
| Cũ-3 | `monkeypatch` patch `datetime.now()` và `os.environ` ở nhiều file, test A rò trạng thái sang test B (chạy riêng pass, chạy cả bộ fail). Fixture trong `conftest.py` scope nào, dùng `tmp_path`, `monkeypatch` thế nào để cô lập? | `references/testing-fixtures.md` › 1.7 `monkeypatch` (`setenv`, vá `datetime`, tự hoàn lại), › 1.8 (test phụ thuộc thứ tự), › 1.3 scope, › 1.5 autouse; `testing-organization.md` › 2 `tmp_path` | `references/testing-fixtures.md` › 1.7; › 1.8; › 1.3; › 1.6 | Đạt |
| Cũ-4 | Hàm xử lý file log lớn, mỗi dòng tạo nhiều object nhỏ, chậm và memory tăng dần. Đổi sang `__slots__`, `functools.lru_cache` hay `dataclass(slots=True)`? Đo trước bằng `cProfile`/`tracemalloc` thế nào? | `references/generators-concurrency-performance.md` › 3.1 `__slots__`, › 3.3 `lru_cache`, › 3.4 `cProfile`/`tracemalloc`; `references/type-hints-and-dataclasses.md` › 2.1 `dataclass(slots=True)` | `references/generators-concurrency-performance.md` › 3.4; › 3.1; › 3.3; › 1.3 | Đạt |
| Cũ-5 | Module có class kế thừa nhiều tầng, `isinstance` khắp nơi, import vòng giữa `models.py` và `services.py`. Refactor theo composition hay `Protocol`, gỡ circular import thế nào mà không phá API? | `references/type-hints-and-dataclasses.md` › 3 (composition thay vì kế thừa, `Protocol`, giữ API) + `references/packaging-and-tooling.md` › 6 (vòng import: tách module, `TYPE_CHECKING`, đảo phụ thuộc, import cục bộ) | `references/type-hints-and-dataclasses.md` › 3. Ghép (composition) thay vì kế thừa nhiều tầng; `references/packaging-and-tooling.md` › 6. Vòng import | Đạt |
| Cũ-6 | Server Python sinh stack trace dài ở production; thiết kế hệ exception riêng (`DomainError`, `NotFoundError`, `ValidationError`), khi nào wrap/re-raise, log ở tầng nào để không trùng, retry backoff cho lỗi tạm thời từ database | mục khác: skill `error-handling` | mục khác: `error-handling` (từ `SKILL.md` › 8 và `errors-context-decorators.md` › 1.3), kèm `silent-failure-hunter` | Đạt |
