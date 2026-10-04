# Pipeline CI/CD, health check, cấu hình môi trường, lệnh hoàn tác

> **Kết luận:** PR chạy lint → kiểm kiểu → test; gộp vào nhánh chính thì build image gắn tag theo commit,
> lên staging, smoke test, rồi production qua môi trường có người duyệt. Health check tách
> liveness, readiness và chi tiết nội bộ; cấu hình kiểm bằng schema lúc khởi động. Lệnh hoàn tác production chỉ chạy khi người dùng gật.

Nguồn (phần bổ sung ở SPR-04, đọc 2026-10-04): tài liệu Trivy (quét image trong pipeline), tài liệu Kubernetes (probe, `terminationGracePeriodSeconds`, `preStop`), twelve-factor (cấu hình theo môi trường).

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

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging
    steps:
      - name: Deploy the image built above to staging
        run: |
          # Platform-specific command, e.g.:
          # kubectl set image deployment/app app=ghcr.io/${{ github.repository }}:${{ github.sha }}
          echo "Deploying ${{ github.sha }} to staging"

  smoke:
    needs: deploy-staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Smoke test staging
        run: ./scripts/smoke.sh "${{ vars.STAGING_URL }}"   # fails the run on any broken critical path

  deploy:
    needs: smoke
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production        # require reviewer approval on this environment
    steps:
      - name: Promote the same image to production (no rebuild)
        run: |
          # Platform-specific command, e.g.:
          # kubectl set image deployment/app app=ghcr.io/${{ github.repository }}:${{ github.sha }}
          echo "Deploying ${{ github.sha }} to production"
```

Production nhận **đúng image** `:${{ github.sha }}` đã qua staging và smoke test, không build lại. Môi trường
`production` đặt người duyệt; agent không tự kích hoạt job này (SKILL mục 4).

Workflow CI chi tiết hơn: skill `github-ops`.

## 2. Các chặng pipeline

```
PR opened:
  lint → typecheck → unit tests → integration tests → preview deploy

Merged to main:
  lint → typecheck → unit tests → integration tests → build image → scan image → deploy staging → smoke tests → deploy production
```

**Chặng quét image (Trivy)** đứng ngay sau build, **trước** khi đẩy image lên registry dùng cho staging/production,
và quét đúng image sẽ được promote (tag `github.sha`), không quét lại bản build khác:

```yaml
      - name: Scan image
        run: |
          trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 \
            registry.example.com/app:${{ github.sha }}
```

- `--severity HIGH,CRITICAL` giới hạn mức lỗ hổng tính; `--exit-code 1` làm bước này thoát khác 0 (pipeline đỏ)
  khi tìm thấy; `--ignore-unfixed` bỏ lỗ hổng chưa có bản vá (chưa làm được gì) để cảnh báo còn hành động được.
- Ngưỡng làm hỏng pipeline do dự án chọn và ghi vào PLAN (ví dụ chặn `CRITICAL` ngay, `HIGH` có hạn xử lý); không hạ
  ngưỡng để "cho qua" — ngoại lệ cho một CVE cụ thể thì ghi lý do và hạn trong tệp bỏ qua của công cụ, có người duyệt.
- Image nặng CVE từ công cụ build là dấu hiệu thiếu multi-stage hoặc base quá to (`dockerfiles.md` mục 5).
- Nguồn: tài liệu Trivy, quét container image.

## 3. Endpoint health

Mỗi probe một endpoint, vì mỗi probe hỏi một câu khác nhau (SKILL mục 2 bước 3):

```typescript
// Liveness: is the process alive? Never checks dependencies,
// otherwise a flaky database restarts every instance at once.
app.get("/livez", (req, res) => {
  res.status(200).json({ status: "ok" });
});

// Readiness: can this instance serve traffic now? Checks only the
// dependencies a request cannot succeed without; 503 takes the instance
// out of the load balancer without restarting it.
app.get("/readyz", async (req, res) => {
  const db = await checkDatabase();
  res.status(db.status === "ok" ? 200 : 503).json({ status: db.status });
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

`/health/detailed` chỉ cho giám sát nội bộ, không gắn vào probe và không mở công khai; nó lộ phụ thuộc và phiên bản.

## 4. Probe Kubernetes

```yaml
livenessProbe:            # process alive only
  httpGet:
    path: /livez
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 30
  failureThreshold: 3

readinessProbe:           # essential dependencies reachable
  httpGet:
    path: /readyz
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 2

startupProbe:             # holds liveness off during a slow start
  httpGet:
    path: /livez
    port: 3000
  initialDelaySeconds: 0
  periodSeconds: 5
  failureThreshold: 30    # 30 * 5s = 150s max startup time
```

Dịch vụ khởi động chậm (ví dụ ~90 giây): `startupProbe` phải **bao được** thời gian đó (`periodSeconds × failureThreshold`
> thời gian khởi động tệ nhất, ở mẫu trên 150 giây); liveness và readiness chỉ bắt đầu sau khi startup thành công.

**Tắt pod êm, không rớt yêu cầu.** Khi pod bị xoá: hook `preStop` chạy → `SIGTERM` gửi tới tiến trình → chờ tối đa
`terminationGracePeriodSeconds` (mặc định 30 giây, **tính cả** thời gian `preStop`) → `SIGKILL`. Pod bị gỡ khỏi
danh sách endpoint **song song** với chuỗi này, nên một lúc nữa nó vẫn có thể nhận yêu cầu mới.

```yaml
spec:
  terminationGracePeriodSeconds: 60          # > preStop + thời gian xử lý nốt yêu cầu dài nhất
  containers:
    - name: app
      lifecycle:
        preStop:
          exec:
            command: ["sleep", "10"]         # chờ endpoint/cân bằng tải ngừng chuyển yêu cầu mới tới pod
```

- Ứng dụng nhận `SIGTERM` thì **ngừng nhận yêu cầu mới, xử lý nốt yêu cầu đang dở, rồi thoát**; tiến trình không xử lý
  `SIGTERM` (shell form, PID 1 không init — `docker.md` mục 3) bị `SIGKILL` (mã thoát 137) sau hết hạn.
- `preStop` kiểu `sleep` cần image có lệnh đó (image distroless không có shell: dùng cơ chế `sleep` của hook nếu
  nền tảng hỗ trợ, hoặc để chính ứng dụng chờ sau khi nhận `SIGTERM`).
- **Rolling update**: `maxUnavailable` (số pod được phép không sẵn sàng, mặc định 25 %) và `maxSurge` (số pod vượt
  quá mong muốn, mặc định 25 %) quyết định tốc độ đợt; dịch vụ không chịu mất công suất đặt `maxUnavailable: 0` với
  `maxSurge: 1` để luôn đủ pod sẵn sàng, đổi lại đợt chạy chậm hơn và cần dư tài nguyên cho pod thêm.
  `minReadySeconds` bắt pod mới sẵn sàng đủ lâu mới tính là "available".
- Nguồn: tài liệu Kubernetes (Pod Lifecycle, Deployments, probes).

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

## 7. Pod không lên: `CrashLoopBackOff`

`CrashLoopBackOff` = container thoát liên tục và kubelet chờ lâu dần giữa các lần khởi động lại; nó là triệu chứng,
nguyên nhân nằm ở lý do thoát. Điều tra **chỉ-đọc** theo thứ tự (đúng với skill `debugging`: tìm nguyên nhân trước khi sửa):

```bash
kubectl get pod <pod>                    # trạng thái, số lần khởi động lại
kubectl describe pod <pod>               # Last State: lý do + mã thoát, Events (pull image lỗi, probe hỏng, OOM)
kubectl logs <pod> --previous            # log của lần chạy trước đó vừa chết (log hiện tại có thể rỗng)
kubectl get events --sort-by=.lastTimestamp
kubectl rollout status deployment/<tên>  # đợt triển khai kẹt ở đâu
```

| Dấu hiệu | Nghĩa thường gặp | Hướng |
|---|---|---|
| `OOMKilled`, mã thoát 137 | vượt giới hạn bộ nhớ (137 cũng là `SIGKILL` do hết `terminationGracePeriodSeconds`) | tăng request/limit có đo, hoặc sửa rò bộ nhớ |
| Thoát ngay với mã khác 0, log có lỗi cấu hình | thiếu biến môi trường / bí mật, kiểm cấu hình lúc khởi động đã dừng (`SKILL.md` mục 2) | sửa cấu hình, không thêm giá trị mặc định đoán |
| Liveness probe fail lặp lại | probe quá chặt hoặc dịch vụ khởi động chậm hơn `startupProbe` | nới/thêm `startupProbe` (mục 4); liveness không kiểm phụ thuộc |
| `ImagePullBackOff` hay `ErrImagePull` | sai tag, registry không cho kéo | kiểm tag bất biến và quyền kéo |

`kubectl exec`/`kubectl debug` chạy lệnh trong pod đang sống; đọc xong mới quyết. Hoàn tác (`kubectl rollout undo`) là
hành động trên production: theo điều kiện dừng ở `SKILL.md` mục 4.
- Nguồn: tài liệu Kubernetes, "Debug Pods".
