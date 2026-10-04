# Endpoint async, tầng service, xử lý lỗi, OpenAPI, test

> **Kết luận:** handler async làm I/O bằng thư viện async và chỉ điều phối; transaction và lỗi ràng buộc
> DB nằm ở tầng service; lỗi miền đổi sang vỏ JSON ổn định qua handler tập trung; OpenAPI tuỳ biến bằng
> cách gán `app.openapi`; test dựng app mới và ghi đè đúng dependency.

Nguồn (phần bổ sung ở SPR-04, đọc 2026-10-04): tài liệu chính thức FastAPI.

## 1. Endpoint async có phân trang

```python
from fastapi import APIRouter, Query
from sqlalchemy import select

from app.dependencies import CurrentUser, DbDep
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: DbDep,
    current_user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = await db.execute(
        select(User).order_by(User.created_at.desc(), User.id).limit(limit).offset(offset)
    )
    return result.scalars().all()
```

Gọi HTTP ra ngoài trong handler async dùng `httpx.AsyncClient`, không dùng `requests`.

## 2. Tầng service và transaction

```python
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


class DuplicateUserError(Exception):
    """A unique user field conflicts with an existing row."""


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, payload: UserCreate) -> User:
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        self.db.add(user)
        try:
            await self.db.flush()      # để ràng buộc unique của DB quyết định, không kiểm trước
        except IntegrityError as exc:
            await self.db.rollback()
            raise DuplicateUserError from exc
        await self.db.refresh(user)
        return user
```

Bắt `IntegrityError` chỉ an toàn khi cột có **unique index trong DB** (migration: skill
`database-migrations`). Thiếu ràng buộc đó thì hai request đồng thời vẫn tạo trùng.

## 3. Xử lý lỗi tập trung

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
```

Thông báo lỗi trả ra ngoài không chứa stack trace, câu SQL hay dữ liệu nhạy cảm (skill `error-handling`).

## 4. Tuỳ biến OpenAPI

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def install_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        app.openapi_schema = get_openapi(
            title="Service API",
            version="1.0.0",
            routes=app.routes,
        )
        return app.openapi_schema

    app.openapi = custom_openapi   # gán hàm, không gọi một lần
```

## 5. Test

Ghi đè dependency mà `Depends` tham chiếu, không ghi đè hàm phụ trợ mà route không gọi tới.

```python
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.main import create_app


@pytest.fixture
async def client(test_session: AsyncSession):
    app = create_app()

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

Fixture async cần pytest-asyncio (`asyncio_mode = "auto"`) hoặc anyio; nền pytest: skill `python`,
`references/testing.md`.

## 6. Phản mẫu

```python
# Tránh: nghiệp vụ nằm trong route
@router.post("/")
async def create_user(payload: UserCreate, db: DbDep):
    user = User(email=payload.email, hashed_password=bcrypt.hash(payload.password))
    db.add(user)
    await db.commit()
    return user            # trả ORM thô, không response_model

# Nên: route mỏng, service lo transaction
@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(payload: UserCreate, db: DbDep):
    try:
        return await UserService(db).create(payload)
    except DuplicateUserError:
        raise HTTPException(status_code=409, detail="Email already registered")


# Tránh: gọi DB đồng bộ trong route async — khoá vòng sự kiện
@router.get("/items/")
async def list_items(db: Session = Depends(get_sync_db)):
    return db.query(Item).all()

# Nên: SQLAlchemy async
@router.get("/items/")
async def list_items(db: DbDep):
    result = await db.execute(select(Item).order_by(Item.id))
    return result.scalars().all()
```

## 7. Bổ sung: khuôn lỗi có request id, OpenAPI gọn, dependency theo header

**Một khuôn cho mọi lỗi (kể cả lỗi validate và lỗi của framework).** Mục 3 chỉ phủ `ApiError` của mình; để lỗi
`404`/`405` của Starlette và lỗi validate của Pydantic cũng ra cùng khuôn, đăng ký thêm handler cho
`StarletteHTTPException` và `RequestValidationError` (ghi đè handler mặc định), và gắn **request id** từ
một middleware:

```python
import uuid
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request.state.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


def error_body(request: Request, code: str, message: str, details=None) -> dict:
    return {"error": {"code": code, "message": message, "request_id": request.state.request_id, "details": details}}


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content=error_body(request, f"HTTP_{exc.status_code}", str(exc.detail)))


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    fields = [{"loc": ".".join(map(str, e["loc"])), "msg": e["msg"]} for e in exc.errors()]   # không trả `input`
    return JSONResponse(status_code=422, content=error_body(request, "VALIDATION_ERROR", "Invalid request", fields))
```

Đăng ký handler ở **một** chỗ (`register_exception_handlers`, mục 3). Log lỗi kèm cùng `request_id` để người
dùng đọc mã trong phong bì là tra được dòng log. Không trả `exc.errors()` thô nếu có thể chứa giá trị người dùng
đã gửi (trường `input`) — có thể là dữ liệu nhạy cảm.

**OpenAPI gọn, tên operation sạch.** Tên kiểu `read_items_items__get` do FastAPI sinh từ tên hàm và đường dẫn;
đặt hàm sinh id duy nhất theo `tag` + tên hàm, và nhóm route bằng tag:

```python
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute


def unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}" if route.tags else route.name


app = FastAPI(
    generate_unique_id_function=unique_id,
    openapi_tags=[{"name": "orders", "description": "Đơn hàng"}, {"name": "users", "description": "Người dùng"}],
)
router = APIRouter(prefix="/v1/orders", tags=["orders"])   # mỗi router một tag → Swagger gom nhóm


class OrderCreate(BaseModel):
    sku: str = Field(examples=["SKU-001"])
    quantity: int = Field(ge=1, examples=[2])
    model_config = {"json_schema_extra": {"examples": [{"sku": "SKU-001", "quantity": 2}]}}


@router.post("", status_code=201, summary="Tạo đơn", operation_id="create_order",
             responses={409: {"description": "Trùng mã đơn"}})
async def create_order(body: OrderCreate) -> OrderResponse: ...
```

`operation_id` đặt tay cho từng route hoặc dùng `generate_unique_id_function` cho cả app — chọn một, và **ổn
định** (đổi tên operation làm client đã sinh code bị vỡ; coi nó là một phần hợp đồng, skill `api-design`). Ví dụ
đặt ở `Field(examples=…)` hoặc `json_schema_extra`, không viết tay vào JSON OpenAPI.

**Dependency đọc header, dùng chung cho nhiều route.** Một dependency cho người dùng hiện tại, một dependency
con kiểm tenant; route chỉ khai kiểu:

```python
from typing import Annotated
from fastapi import Depends, Header, HTTPException


async def current_user(token: TokenDep, db: DbDep) -> User: ...      # xác thực một lần, ở đây


async def tenant_user(
    user: Annotated[User, Depends(current_user)],
    x_tenant_id: Annotated[str, Header()],                             # đọc header `X-Tenant-ID`
) -> User:
    if x_tenant_id not in user.tenant_ids:
        raise HTTPException(status_code=403, detail="Wrong tenant")
    return user


CurrentUser = Annotated[User, Depends(current_user)]
TenantUser = Annotated[User, Depends(tenant_user)]                    # 6 route cần tenant dùng TenantUser
```

FastAPI lưu đệm kết quả dependency trong một request, nên `current_user` chỉ chạy một lần dù có nhiều dependency
con dùng nó. Cả router cùng cần: `APIRouter(dependencies=[Depends(tenant_user)])`.
