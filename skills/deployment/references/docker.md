# Docker và Compose

> **Kết luận:** Dockerfile nhiều tầng có tầng `dev` và `production` riêng; Compose cho dev dùng bind mount
> + healthcheck thật cho DB; mạng tách để DB không với tới từ frontend; container cứng hoá (tag ghim,
> không root, `no-new-privileges`, `read_only`, `cap_drop: ALL`); secret không bao giờ nằm trong lớp
> image. Lệnh xoá volume hay dọn image là không đảo ngược: chỉ chạy khi người dùng gật.

## 1. Luật chính

- Dockerfile nhiều tầng có tầng `dev` và `production` riêng; Compose build `target: dev`, bind mount mã
  nguồn để nạp lại nóng và một volume ẩn danh cho `node_modules` để không bị thư mục máy chủ đè.
- `depends_on` dùng `condition: service_healthy`, kèm healthcheck **thật** trên DB.
- `docker-compose.override.yml` tự nạp thiết lập chỉ dành cho dev; production gọi tường minh
  `-f docker-compose.prod.yml` và có giới hạn tài nguyên.
- Trong mạng Compose, dịch vụ gọi nhau bằng tên dịch vụ; tách mạng để DB không với tới từ frontend; cổng
  chỉ cho máy chủ thì bind `127.0.0.1:5432:5432`.
- Cứng hoá: tag ghim, người dùng không phải root, `no-new-privileges`, `read_only` + tmpfs,
  `cap_drop: ALL`; secret qua biến môi trường lúc chạy hoặc Docker secrets, không bao giờ trong lớp
  image; luôn có `.dockerignore`.

## 2. Debug

```bash
# Logs
docker compose logs -f app           # follow app logs
docker compose logs --tail=50 db     # last 50 lines from db

# Run commands in a running container
docker compose exec app sh
docker compose exec db psql -U postgres

# Inspect
docker compose ps                    # running services
docker compose top                   # processes per container
docker stats                         # resource usage

# Rebuild
docker compose up --build
docker compose build --no-cache app

# Network
docker compose exec app nslookup db                       # DNS inside the network
docker compose exec app wget -qO- http://api:3000/health  # connectivity
docker network ls
docker network inspect <project>_default
```

Dọn dẹp — **xoá dữ liệu, không đảo ngược**: chỉ chạy khi người dùng gật, nói rõ volume / image nào mất.

```bash
docker compose down                  # stop and remove containers (volumes kept)
docker compose down -v               # ALSO removes volumes — data loss
docker system prune                  # removes unused images / containers
```

Lỗi khó (container chết ngay, healthcheck chập chờn): skill `debugging` — tìm lỗi **đầu tiên** trong log
trước khi đổi cấu hình.

## 3. Phản mẫu

| Phản mẫu | Làm thay |
|---|---|
| Dùng `docker compose` cho production nhiều container mà không có điều phối | Kubernetes, ECS, Docker Swarm hoặc nền tảng quản lý |
| Lưu dữ liệu trong container không có volume | volume có tên — container là tạm, khởi động lại là mất |
| Chạy bằng root | tạo và dùng người dùng không phải root |
| Tag `:latest` | ghim phiên bản để build tái tạo được |
| Một container to chạy mọi dịch vụ | mỗi container một tiến trình |
| Secret trong `docker-compose.yml` | `.env` (trong `.gitignore`) hoặc Docker secrets |

## 4. Harness kiểm trình cài đặt trong container cô lập

Dùng khi cần kiểm một CLI hay trình cài đặt trên bản sao dự án dùng xong bỏ, mà không để phép thử sửa vào
checkout gốc.

- **Ranh giới nền tảng:** container Linux chỉ chứng minh hành vi trên Linux. macOS không chạy được trong
  Docker; container Windows cần engine Windows. Giữ ma trận CI chạy thẳng trên Ubuntu, macOS, Windows cho
  đường dẫn, shim lệnh, quoting và hệ tệp — không tuyên bố container Linux đã kiểm macOS hay Windows.
- **Ghim** image nền theo digest bất biến và ghim phiên bản CLI được cài.
- Chạy bằng UID/GID số, không phải root; mount repo và dự án nguồn **chỉ đọc**, chép vào vùng làm việc
  tmpfs riêng (chỉ người dùng container đọc được, `noexec`) trước mọi thay đổi.
- `read_only: true`, `no-new-privileges:true`, `cap_drop: [ALL]`, `pids_limit` hữu hạn; chỉ tạo đúng các
  đường tạm công cụ cần ghi.
- Mặc định **không mạng** (`network_mode: none`) và **không** chuyển thông tin đăng nhập của máy chủ vào;
  cần mạng thì mở bằng một dịch vụ riêng đặt tên rõ, bật có chủ đích — không bao giờ để biến môi trường
  vô tình bật.
- Mặc định chạy **dry-run**; chỉ nhận một danh sách chế độ cho phép.
- Gọi tiến trình con bằng mảng tham số, không qua shell; không nội suy đường dẫn dự án vào chuỗi lệnh.
- Dọn đúng container và project Compose có tên đã tạo, không xoá volume hay image không liên quan.

## 5. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Stack Compose đầy đủ (app + postgres + redis + mailpit), Dockerfile dev/production, file override | `docker-compose-dev.md` |
| Tìm dịch vụ, mạng riêng, mở cổng, chiến lược volume, cứng hoá Dockerfile/Compose, quản lý secret, `.dockerignore` | `docker-network-volume-security.md` |
| Dockerfile production theo ngôn ngữ | `dockerfiles.md` |
