# Mạng, volume và bảo mật container

> **Kết luận:** dịch vụ gọi nhau bằng tên trong mạng Compose; tách mạng để DB chỉ với tới từ API; chỉ mở
> cổng cần thiết và bind `127.0.0.1` khi chỉ máy chủ dùng. Volume có tên cho dữ liệu bền, bind mount cho
> mã nguồn dev. Container chạy không root, hệ tệp chỉ đọc, bỏ mọi capability; secret vào lúc chạy, không
> bao giờ vào image.

## 1. Mạng

Tìm dịch vụ theo tên:

```
# From the "app" container:
postgres://postgres:***@db:5432/app_dev    # "db" resolves to the db container
redis://redis:6379/0                       # "redis" resolves to the redis container
```

Mạng riêng:

```yaml
services:
  frontend:
    networks:
      - frontend-net

  api:
    networks:
      - frontend-net
      - backend-net

  db:
    networks:
      - backend-net              # reachable from api only, not from frontend

networks:
  frontend-net:
  backend-net:
```

Chỉ mở thứ cần:

```yaml
services:
  db:
    ports:
      - "127.0.0.1:5432:5432"   # host only, not the network
    # Omit ports entirely in production — reachable only inside the Docker network
```

## 2. Volume

```yaml
volumes:
  # Named volume: persists across restarts, managed by Docker
  pgdata:

  # Bind mount: host directory into the container (development)
  # - ./src:/app/src

  # Anonymous volume: keeps container-generated content under a bind mount
  # - /app/node_modules
```

```yaml
services:
  app:
    volumes:
      - .:/app                   # source code (bind mount for hot reload)
      - /app/node_modules        # protect the container's node_modules from the host
      - /app/.next               # protect build cache

  db:
    volumes:
      - pgdata:/var/lib/postgresql/data                          # persistent data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql  # init scripts
```

## 3. Bảo mật container

Cứng hoá Dockerfile:

```dockerfile
# 1. Specific tags (never :latest)
FROM node:22.12-alpine3.20

# 2. Run as non-root
RUN addgroup -g 1001 -S app && adduser -S app -u 1001
USER app

# 3. Drop capabilities (in compose)
# 4. Read-only root filesystem where possible
# 5. No secrets in image layers
```

Cứng hoá Compose:

```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE          # only if binding to ports < 1024
```

Quản lý secret:

```yaml
# GOOD: environment variables injected at runtime
services:
  app:
    env_file:
      - .env                     # never commit .env
    environment:
      - API_KEY                  # inherited from the host environment

# GOOD: Docker secrets (Swarm mode)
secrets:
  db_password:
    file: ./secrets/db_password.txt   # gitignored

services:
  db:
    secrets:
      - db_password

# BAD: hardcoded in the image
# ENV API_KEY=...                # NEVER DO THIS
```

Chỉ commit `.env.example` (tên biến, không giá trị). Secret lọt vào image hay repo: báo để xoay vòng
(skill `security-review`).

## 4. `.dockerignore`

```
node_modules
.git
.env
.env.*
dist
coverage
*.log
.next
.cache
docker-compose*.yml
Dockerfile*
README.md
tests/
```
