# Test với session CSDL giả và cấu hình chạy sau proxy

> **Kết luận:** test dùng client ASGI trong cùng event loop với fixture; CSDL test dựng lại **mỗi test** (SQLite
> in-memory) để dữ liệu không dính nhau; người dùng giả là một ghi đè dependency. Ở production sau Nginx: IP thật
> đến từ `--proxy-headers` + `--forwarded-allow-ips` (chỉ tin IP của proxy), nén bằng `GZipMiddleware`, tắt `/docs` bằng
> tham số khởi tạo app.

## 1. Fixture `test_session` và cô lập dữ liệu

Mẫu `client` ở `references/routes-errors-openapi-testing.md` mục 5 cần một `test_session`. SQLite in-memory dùng
`StaticPool` để mọi kết nối của test thấy cùng một CSDL; dựng bảng từ metadata, mỗi test một engine mới nên dữ liệu
không dính sang test khác.

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base            # DeclarativeBase của dự án; import cả models để bảng có trong metadata
from app.dependencies import get_current_user, get_db
from app.main import create_app
from app.models.user import User


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def test_session(engine):
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    app = create_app()
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with maker() as session:      # mỗi request một phiên, như production; route commit thật
            yield session

    async def fake_user():
        return User(id=1, email="tester@example.com", role="admin")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = fake_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- **Cô lập:** dựng engine + bảng mới cho mỗi test (như trên) là cách đơn giản và đúng với SQLite. Muốn rẻ hơn thì đổi
  `scope` của fixture `engine` sang `session` **và** `loop_scope="session"` cho các test dùng nó (event loop phải sống
  bằng fixture), rồi xoá dữ liệu từng bảng bằng `DELETE FROM` sau mỗi test — tốn công hơn, dễ rò rỉ giữa các test.
- **Đừng dựa vào "bọc test trong một transaction ngoài + savepoint" với SQLite:** kiểu này
  (`AsyncSession(bind=conn, join_transaction_mode="create_savepoint")`, rollback ở cuối) là mẫu của SQLAlchemy cho
  CSDL có savepoint chuẩn như PostgreSQL; chạy thử với `aiosqlite` thì dữ liệu route đã `commit` vẫn còn sang test sau
  (driver SQLite tự quản transaction). Cần hành vi giống production → chạy test với PostgreSQL thật (container) và dùng
  mẫu savepoint ở đó.
- SQLite khác PostgreSQL ở kiểu dữ liệu, ràng buộc, `JSONB`, `ON CONFLICT`: test chạm tính năng riêng của PostgreSQL
  (khoá, upsert, kiểu mảng) không có giá trị trên SQLite — dùng PostgreSQL thật cho nhóm test đó.
- **Người dùng giả:** ghi đè **đúng hàm** mà route tham chiếu (`get_current_user` của `Depends`/`Security`). Ghi đè
  thay cả dependency, nên kiểm tra scope/vai của dependency gốc **không chạy** — test phân quyền thật thì ghi đè ở mức
  thấp hơn (ví dụ trả token giả đã ký bằng khoá test) hoặc tạo token thật bằng hàm cấp token.
- **Event loop:** dùng `AsyncClient(transport=ASGITransport(app=app))` thay `TestClient` trong test async: mọi thứ chạy trong
  loop của pytest-asyncio, tránh lỗi "attached to a different loop". `ASGITransport` **không chạy `lifespan`** —
  tài nguyên khởi tạo ở `lifespan` (pool, client HTTP) không có trong test; hoặc ghi đè dependency lấy chúng (như
  trên), hoặc bọc app bằng trình quản lý lifespan, hoặc dùng `with TestClient(app)` cho test đồng bộ (có chạy lifespan).

## 2. Chạy sau Nginx: IP thật, nén, `/docs`

**IP client thật.** Sau proxy, `request.client.host` là IP của proxy. Uvicorn đọc `X-Forwarded-For` và
`X-Forwarded-Proto` khi `--proxy-headers` bật (mặc định bật) **và** IP của proxy nằm trong `--forwarded-allow-ips`
(mặc định biến môi trường `FORWARDED_ALLOW_IPS` hoặc `127.0.0.1`). Nginx phải gửi các header đó
(`proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` và `X-Forwarded-Proto $scheme`).

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips 10.0.0.5
# hoặc đặt biến môi trường FORWARDED_ALLOW_IPS=10.0.0.5 (dải mạng: 10.0.0.0/24)
```

- Chỉ liệt kê IP/dải của **proxy của mình**. `--forwarded-allow-ips '*'` tin mọi nguồn: ai kết nối thẳng tới app cũng
  tự khai được IP và scheme (giả mạo log, rate limit, kiểm IP). Proxy cùng host thì giữ mặc định `127.0.0.1`; proxy ở
  container khác thì đặt IP/dải của mạng container đó.
- Đã chạy thử: proxy trong danh sách → `request.client.host` ra IP trong `X-Forwarded-For` và `url.scheme` ra `https`;
  proxy **ngoài** danh sách → vẫn là IP kết nối thật, header bị bỏ qua.
- Dịch vụ phục vụ dưới tiền tố đường dẫn (`/api` do proxy cắt đi): đặt `--root-path /api` hoặc `FastAPI(root_path=...)`
  để URL trong OpenAPI và `url_for` đúng; không thay cho proxy headers.

**Nén.** `GZipMiddleware` của Starlette nén response khi client gửi `Accept-Encoding: gzip`:

```python
from starlette.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)   # byte; mặc định 500. Response nhỏ hơn thì không nén
```

Đặt `minimum_size` ≥ 1000 (response nhỏ nén không lợi, tốn CPU); `compresslevel` mặc định 9 (nén kỹ, tốn CPU) — có thể
hạ xuống 5-6 nếu CPU là điểm nghẽn. Nếu Nginx đã nén ở lớp trước thì không nén hai lần: chọn **một** nơi nén. Chỉ bật
sau khi đo (`SKILL.md` mục 7).

**Tắt `/docs` ở production.** Tham số khởi tạo, không phải middleware; điều kiện theo cấu hình:

```python
app = FastAPI(
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
)
```

`docs_url=None` chỉ tắt giao diện Swagger; **`openapi_url=None` mới tắt luôn file `openapi.json`** (và kéo theo cả
`/docs`, `/redoc` không dùng được). Đã chạy thử: `docs_url=None` → `/docs` trả `404`. Cần giữ docs cho nội bộ thì để
proxy chặn theo mạng/xác thực thay vì chỉ ẩn đường dẫn. CORS có cookie: xem `SKILL.md` mục 3 và
`references/app-schemas-dependencies.md` mục 1.

## Nguồn

Tài liệu chính thức: FastAPI (Testing, Async Tests, Behind a Proxy, Metadata and Docs URLs, Middleware), Starlette
(`GZipMiddleware`), Uvicorn (Settings: `--proxy-headers`, `--forwarded-allow-ips`, `--root-path`), SQLAlchemy
(asyncio, "Joining a Session into an External Transaction"), pytest-asyncio (`loop_scope`). Mẫu fixture và hành vi
proxy/gzip/docs đã chạy lại trên FastAPI 0.135, Starlette 0.52, Uvicorn 0.41, SQLAlchemy 2.0, aiosqlite 0.22.
