# Factory dựng app, cấu hình, schema và dependency

> **Kết luận:** dựng app bằng factory để test và worker tạo app với cấu hình kiểm soát được; cấu hình đọc
> từ môi trường qua pydantic-settings; schema vào/ra/cập nhật tách riêng; tài nguyên theo request đi
> qua dependency, không tạo trong handler.

## 1. Factory dựng app

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, users
from app.config import settings
from app.db.session import close_db, init_db
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=bool(settings.cors_origins),
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    register_exception_handlers(app)
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    return app


app = create_app()
```

Không dùng `allow_origins=["*"]` cùng `allow_credentials=True`: Starlette không từ chối mà trả lại đúng
`Origin` của request (preflight, và response khi request mang cookie) kèm credentials, nên trang web nào
cũng đọc được response đã đăng nhập. Liệt kê nguồn cụ thể.

## 2. Cấu hình bằng pydantic-settings

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_title: str = "Service API"
    api_version: str = "0.1.0"
    debug: bool = False

    database_url: str          # bắt buộc, không mặc định
    secret_key: str            # bắt buộc, không mặc định
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: list[str] = []   # mỗi môi trường khai riêng


settings = Settings()
```

`.env` nằm trong `.gitignore`; repo chỉ có `.env.example` với tên biến, không giá trị thật.

## 3. Schema Pydantic

Tách model tạo, cập nhật, phản hồi.

```python
from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Annotated[str, Field(min_length=1, max_length=100)]


class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=12, max_length=128)]


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: Annotated[str | None, Field(min_length=1, max_length=100)] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
```

Model phản hồi không bao giờ chứa hash mật khẩu, access token, refresh token hay trạng thái phân quyền
nội bộ. Cập nhật từng phần dùng `payload.model_dump(exclude_unset=True)`.

## 4. Dependency

```python
from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenError, decode_token
from app.db.session import session_factory
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DbDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbDep,
) -> User:
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)   # kiểm chữ ký, hạn, issuer, audience
        user_id = UUID(str(payload["sub"]))
    except (TokenError, KeyError, TypeError, ValueError):
        raise invalid from None         # token rác là 401, không bao giờ 500
    user = await db.get(User, user_id)
    if user is None:
        raise invalid
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
```

`TokenError` là lớp lỗi của chính `app/core/security.py`: `decode_token` bắt lỗi của thư viện JWT
(`jwt.PyJWTError` với PyJWT, `JWTError` với python-jose) cùng lỗi `iss`, `aud`, hạn dùng, rồi ném lại thành
`TokenError` để dependency chỉ cần bắt một loại.

Không tạo session, client hay credential ngay trong route handler. Kiểm tra quyền (`403`) để ở dependency
riêng nhận `CurrentUser`, không trộn vào `get_current_user` (`401`).
