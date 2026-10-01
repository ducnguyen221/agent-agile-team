# Pipeline CI/CD, health check, cấu hình môi trường, lệnh hoàn tác

> **Kết luận:** PR chạy lint → kiểm kiểu → test; gộp vào nhánh chính thì build image gắn tag theo commit,
> lên staging, smoke test, rồi production qua môi trường có người duyệt. Health check tách đơn giản và
> chi tiết; cấu hình kiểm bằng schema lúc khởi động. Lệnh hoàn tác production chỉ chạy khi người dùng gật.

## 1. GitHub Actions (pipeline chuẩn)

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage
          path: coverage/

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production        # require reviewer approval on this environment
    steps:
      - name: Deploy to production
        run: |
          # Platform-specific command, e.g.:
          # kubectl set image deployment/app app=ghcr.io/${{ github.repository }}:${{ github.sha }}
          echo "Deploying ${{ github.sha }}"
```

Workflow CI chi tiết hơn: skill `github-ops`.

## 2. Các chặng pipeline

```
PR opened:
  lint → typecheck → unit tests → integration tests → preview deploy

Merged to main:
  lint → typecheck → unit tests → integration tests → build image → deploy staging → smoke tests → deploy production
```

## 3. Endpoint health

```typescript
// Simple health check
app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});

// Detailed health check (internal monitoring only)
app.get("/health/detailed", async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    redis: await checkRedis(),
    externalApi: await checkExternalApi(),
  };
  const allHealthy = Object.values(checks).every(c => c.status === "ok");

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? "ok" : "degraded",
    timestamp: new Date().toISOString(),
    version: process.env.APP_VERSION || "unknown",
    uptime: process.uptime(),
    checks,
  });
});

async function checkDatabase(): Promise<HealthCheck> {
  try {
    await db.query("SELECT 1");
    return { status: "ok", latency_ms: 2 };
  } catch {
    // Fixed message: driver errors may contain the connection string.
    return { status: "error", message: "Database unreachable" };
  }
}
```

`/health/detailed` không mở công khai; nó lộ phụ thuộc và phiên bản.

## 4. Probe Kubernetes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 30
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 2

startupProbe:
  httpGet:
    path: /health
    port: 3000
  initialDelaySeconds: 0
  periodSeconds: 5
  failureThreshold: 30    # 30 * 5s = 150s max startup time
```

## 5. Cấu hình môi trường

Mọi cấu hình qua biến môi trường, không trong code:

```bash
DATABASE_URL=postgres://user:***@host:5432/db
REDIS_URL=redis://host:6379/0
API_KEY=${API_KEY}           # injected by the secrets manager
LOG_LEVEL=info
PORT=3000
NODE_ENV=production          # or staging, development
APP_ENV=production           # explicit app environment
```

Kiểm lúc khởi động — sai thì dừng ngay:

```typescript
import { z } from "zod";

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "staging", "production"]),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
});

export const env = envSchema.parse(process.env);
```

Thông báo lỗi kiểm cấu hình chỉ nêu **tên** biến sai, không in giá trị.

## 6. Lệnh hoàn tác tức thì

Chỉ chạy trên production khi người dùng gật (SKILL mục 3). Dự án có công cụ deploy riêng thì dùng lệnh
hoàn tác của công cụ đó.

```bash
# Kubernetes: back to the previous ReplicaSet / image
kubectl rollout undo deployment/app

# Platform CLIs usually offer "promote previous deployment" or "redeploy commit <sha>"

# Database: roll back a migration only if it is reversible
npx prisma migrate resolve --rolled-back <migration-name>
```

Hoàn tác migration: skill `database-migrations`.
