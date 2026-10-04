# Dockerfile cho production

> **Kết luận:** build nhiều tầng để image cuối chỉ có thứ cần chạy; chép file phụ thuộc trước để tận dụng
> cache; chạy bằng người dùng không phải root; ghim tag; có `HEALTHCHECK`; không bao giờ đặt secret trong
> image.

## 1. Node.js

```dockerfile
# Stage 1: install dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --production=false

# Stage 2: build
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build
RUN npm prune --production

# Stage 3: production image
FROM node:22-alpine AS runner
WORKDIR /app

RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser

COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

ENV NODE_ENV=production
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/server.js"]
```

## 2. Go

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /server ./cmd/server

FROM alpine:3.19 AS runner
RUN apk --no-cache add ca-certificates
RUN adduser -D -u 1001 appuser
USER appuser

COPY --from=builder /server /server

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:8080/health || exit 1
CMD ["/server"]
```

## 3. Python / Django

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

FROM python:3.12-slim AS runner
WORKDIR /app

RUN useradd -r -u 1001 appuser
USER appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

## 4. Nên và không nên

| Nên | Không nên |
|---|---|
| tag cụ thể (`node:22-alpine`) | tag `:latest` |
| build nhiều tầng để image nhỏ | chép cả repo trong một lớp `COPY` |
| chạy bằng người dùng không phải root | chạy bằng root |
| chép file phụ thuộc trước (cache lớp) | cài phụ thuộc dev vào image production |
| có `.dockerignore` loại `node_modules`, `.git`, test | để `.env` lọt vào build context |
| có `HEALTHCHECK` | đặt secret trong image — dùng biến môi trường lúc chạy hoặc kho secret |
| đặt giới hạn tài nguyên ở compose hoặc Kubernetes | |

## 5. Chọn image nền cho tầng chạy; quyền ghi khi chạy bằng người dùng không phải root

**Image nền của tầng chạy** (build nhiều tầng đã loại compiler và devDependencies khỏi image cuối; còn lại là chọn nền):

| Nền | Đặc điểm | Chọn khi | Cái giá |
|---|---|---|---|
| `slim` (Debian rút gọn) | glibc, có shell và trình quản lý gói, nhỏ hơn bản đầy đủ | mặc định cho Python/Node/…, cần thư viện native | còn vài gói thừa, vẫn có thể có CVE của OS |
| `alpine` | rất nhỏ, musl libc, có shell | image nhỏ, ứng dụng thuần (Go tĩnh, Node không native) | musl khác glibc: wheel/binary dựng sẵn có thể không chạy hoặc chậm; lỗi lạ khó gỡ |
| distroless | chỉ ứng dụng + runtime, không shell, không trình quản lý gói | production cần bề mặt tấn công nhỏ nhất, binary tĩnh (Go) hay runtime đã đóng gói | khó debug (không `sh`/`exec` được; dùng ephemeral debug container), không chạy `RUN` ở tầng này |

Luật chung: ghim phiên bản (production ghim digest), quét bằng Trivy (`cicd-health-config.md` mục 2), tầng chạy không cài
công cụ build. Đổi nền là việc cần đo (kích thước, số CVE trước/sau, chạy test trên nền mới), không đổi theo thói quen.
Nguồn: tài liệu Docker (multi-stage, best practices) và README của dự án distroless.

**Quyền ghi khi `USER` không phải root.** Lỗi "permission denied" ở `/app/uploads` sau khi thêm `USER` nghĩa là thư mục
thuộc root. **Không lùi về root.** Chọn theo nơi dữ liệu nằm:

1. **Thư mục ghi nằm trong image** (cache, tạm): tạo và đặt quyền **trước** dòng `USER`:
   ```dockerfile
   RUN mkdir -p /app/uploads && chown appuser:appgroup /app/uploads
   COPY --chown=appuser:appgroup --from=builder /app/dist ./dist
   USER appuser
   ```
2. **Dữ liệu cần giữ qua lần chạy lại** → volume có tên gắn vào đúng thư mục đó. Volume có tên **mới và rỗng** nhận nội
   dung và quyền từ thư mục có sẵn trong image ở lần gắn đầu, nên bước `chown` ở mục 1 truyền sang volume; volume đã
   tạo từ trước với chủ cũ không tự đổi — chỉnh một lần bằng container tạm chạy `chown`, hoặc xoá volume nếu chưa có dữ
   liệu thật (xoá volume là hành động không đảo ngược: theo `SKILL.md` mục 4).
3. **Bind mount** thư mục máy chủ: quyền do máy chủ quyết; chạy container với đúng UID/GID sở hữu thư mục
   (`user: "1001:1001"` hoặc cấp quyền cho nhóm), không `chmod 777`.
4. **Tệp người dùng tải lên là dữ liệu thật** → không để trong container: lưu ra kho đối tượng của nền tảng hoặc volume
   dùng chung — container là tạm, nhiều bản sao không chia sẻ được đĩa cục bộ.
Không `chmod 777`; không đổi `USER` về root để "cho chạy được". Nguồn: tài liệu Docker (volumes, `COPY --chown`).
