# Stack Compose cho dev và Dockerfile dev/production

> **Kết luận:** một `docker-compose.yml` dựng app + DB + cache + hộp thư thử cho dev, app chờ DB khoẻ
> mới chạy; Dockerfile có tầng `dev` (nạp lại nóng) và `production` (tối giản, không root); file override
> tự nạp cho dev, file production gọi tường minh. Mật khẩu trong file này chỉ là giá trị dev mặc định.

## 1. Stack web app chuẩn

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      target: dev                     # dev stage of the multi-stage Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - .:/app                        # bind mount for hot reload
      - /app/node_modules             # anonymous volume keeps container deps
    environment:
      - DATABASE_URL=postgres://postgres:***@db:5432/app_dev   # *** = POSTGRES_PASSWORD (dev default)
      - REDIS_URL=redis://redis:6379/0
      - NODE_ENV=development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: npm run dev

  db:
    image: postgres:16-alpine
    ports:
      - "127.0.0.1:5432:5432"         # host-only
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres     # dev only
      POSTGRES_DB: app_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redisdata:/data

  mailpit:                            # local email testing
    image: axllent/mailpit
    ports:
      - "8025:8025"                   # web UI
      - "1025:1025"                   # SMTP

volumes:
  pgdata:
  redisdata:
```

## 2. Dockerfile dev và production

```dockerfile
# Stage: dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage: dev (hot reload, debug tools)
FROM node:22-alpine AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Stage: build
FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --production

# Stage: production (minimal image)
FROM node:22-alpine AS production
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser
COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY --from=build --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/package.json ./
ENV NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

## 3. File override

```yaml
# docker-compose.override.yml (auto-loaded, dev-only settings)
services:
  app:
    environment:
      - DEBUG=app:*
      - LOG_LEVEL=debug
    ports:
      - "9229:9229"                   # Node.js debugger

# docker-compose.prod.yml (explicit for production)
services:
  app:
    build:
      target: production
    restart: always
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
```

```bash
# Development (auto-loads the override)
docker compose up

# Production — outward-facing: only after the user approves
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
