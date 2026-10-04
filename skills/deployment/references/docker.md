# Docker và Compose

> **Kết luận:** một Dockerfile nhiều tầng phục vụ cả dev lẫn production; Compose cho dev dùng bind mount và
> healthcheck thật cho CSDL; mạng tách để CSDL không với tới từ phía ngoài; container cứng hoá (image ghim,
> không root, `no-new-privileges`, `read_only`, `cap_drop: ALL`); secret không bao giờ nằm trong lớp image.
> Debug bắt đầu từ **mã thoát và dòng lỗi đầu tiên**, không từ đổi cấu hình. Xoá volume hay dọn image là
> không đảo ngược: chỉ chạy khi người dùng gật.

## 1. Luật chính

- **Một Dockerfile, nhiều tầng:** tầng phụ thuộc → tầng `dev` (nạp lại nóng, công cụ debug) → tầng build →
  tầng `production` tối giản. Compose dev build `target: dev`, bind mount mã nguồn và một volume ẩn danh cho
  thư mục phụ thuộc để thư mục của máy chủ không đè lên.
- **Thứ tự lớp quyết định cache:** chép file khai báo phụ thuộc (lockfile) và cài trước, chép mã nguồn sau;
  đổi một dòng code không được làm cài lại toàn bộ phụ thuộc. Luôn có `.dockerignore`.
- **Tiến trình chính nhận tín hiệu:** `CMD`/`ENTRYPOINT` dạng mảng JSON để ứng dụng là tiến trình số 1 và
  nhận `SIGTERM`; ứng dụng đóng kết nối, làm xong yêu cầu đang dở rồi mới thoát. Dạng chuỗi chạy qua shell
  thường nuốt tín hiệu, container bị giết cứng sau thời gian chờ. Tiến trình số 1 còn bỏ qua `SIGTERM` nếu
  ứng dụng không tự cài handler: cài handler, hoặc chạy init nhỏ (`--init`, `init: true` trong Compose, tini).
- **Phụ thuộc khởi động:** `depends_on` với `condition: service_healthy`, kèm healthcheck **thật** trên CSDL
  (lệnh kiểm sẵn sàng của chính CSDL, không chỉ "cổng đã mở"); healthcheck có `start_period` đủ cho lần
  khởi động chậm nhất.
- **Tách dev và production:** `docker-compose.override.yml` tự nạp thiết lập chỉ dành cho dev; production gọi
  tường minh file production và có giới hạn tài nguyên.
- **Mạng:** dịch vụ gọi nhau bằng tên dịch vụ; tách mạng để CSDL không với tới từ frontend; cổng chỉ dành cho
  máy chủ thì bind vào `127.0.0.1`.
- **Cứng hoá:** image ghim phiên bản (production nên ghim theo digest), người dùng không phải root,
  `no-new-privileges`, `read_only` kèm tmpfs cho chỗ cần ghi, `cap_drop: ALL` rồi chỉ thêm quyền thật cần.
- **Secret:** đưa vào lúc chạy qua biến môi trường hoặc Docker secrets; không `ENV`, không `ARG`, không `COPY`
  file secret vào image — xoá ở lớp sau vẫn còn trong lớp trước.

## 2. Debug

Đọc mã thoát trước khi đọc cấu hình:

| Mã thoát / dấu hiệu | Thường là | Kiểm tiếp |
|---|---|---|
| `137` | bị giết cứng: hết bộ nhớ, hoặc không thoát kịp sau `SIGTERM` | `docker inspect` xem cờ OOM; giới hạn bộ nhớ; dạng `CMD` (mục 1); ứng dụng có handler `SIGTERM` không, có init không |
| `143` | thoát theo `SIGTERM` bình thường | lệnh dừng có chủ đích hay do orchestrator |
| `126` / `127` | lệnh không chạy được / không tìm thấy | đường dẫn, quyền chạy, kiến trúc image, kết thúc dòng của script |
| `1` hoặc mã của ứng dụng | ứng dụng tự thoát vì lỗi | dòng lỗi **đầu tiên** trong log, cấu hình thiếu lúc khởi động |
| healthcheck lúc đạt lúc hỏng | `start_period` ngắn, kiểm phụ thuộc chậm, timeout quá chặt | log healthcheck trong `docker inspect` |

```bash
# Logs
docker compose logs -f app           # follow app logs
docker compose logs --tail=50 db     # last 50 lines from db

# Run commands in a running container
docker compose exec app sh
docker compose exec db psql -U postgres

# Inspect
docker compose ps                    # running services and exit codes
docker compose top                   # processes per container
docker stats                         # resource usage
docker inspect <container>           # state, OOM flag, health log

# Rebuild
docker compose up --build
docker compose build --no-cache app

# Network
docker compose exec app nslookup db                       # DNS inside the network
docker compose exec app wget -qO- http://api:3000/health  # connectivity
docker network ls
docker network inspect <project>_default
```

Dọn dẹp — **xoá dữ liệu, không đảo ngược**: chỉ chạy khi người dùng gật, nói rõ volume, image nào mất.

```bash
docker compose down                  # stop and remove containers (volumes kept)
docker compose down -v               # ALSO removes volumes — data loss
docker system prune                  # removes unused images / containers
```

Lỗi khó (container chết ngay, healthcheck chập chờn): skill `debugging`.

## 3. Lỗi hay gặp

Mức gợi ý theo hậu quả nếu bỏ qua (`method/severity.md` mục 1).

| Dấu hiệu | Hậu quả | Làm thay | Mức gợi ý |
|---|---|---|---|
| Secret trong `ENV`, `ARG`, file `COPY` vào image, hay ghi thẳng trong file compose | lộ cho mọi người kéo được image hay đọc được repo | biến môi trường lúc chạy hoặc Docker secrets; `.env` nằm trong `.gitignore` | Chặn |
| Dữ liệu lưu trong container, không có volume | container là tạm — tạo lại là mất dữ liệu | volume có tên | Chặn khi là dữ liệu thật |
| Chạy bằng root | lỗ hổng ứng dụng thành quyền root trong container | tạo và dùng người dùng không phải root | Phải sửa |
| Image nền `:latest` hay không ghim | build hôm nay khác hôm qua; hoàn tác về "bản cũ" không chắc là bản cũ | ghim phiên bản, production ghim digest | Phải sửa |
| `CMD` dạng chuỗi qua shell, hoặc tiến trình ứng dụng làm PID 1 mà không xử lý tín hiệu | không nhận `SIGTERM` (PID 1 bỏ qua tín hiệu không có handler), yêu cầu dở bị cắt rồi bị `SIGKILL` (mã thoát 137) khi deploy | `CMD` dạng mảng JSON và bật init (`init: true` trong compose, `docker run --init`, hoặc `tini` làm entrypoint) để tín hiệu được chuyển tiếp và tiến trình con được thu dọn | Phải sửa |
| `depends_on` không chờ healthcheck | ứng dụng khởi động trước CSDL, lỗi kết nối lúc khởi động | `condition: service_healthy` + healthcheck thật | Nên sửa |
| Chép cả repo một lớp trước khi cài phụ thuộc | mỗi lần build cài lại từ đầu | chép lockfile, cài, rồi mới chép mã | Nên sửa |
| Một container chạy nhiều dịch vụ | không co giãn, không khởi động lại riêng được | mỗi container một tiến trình | Nên sửa |
| Compose một máy làm production nhiều container | không tự hồi phục, không co giãn | Kubernetes, ECS, Swarm hoặc nền tảng quản lý | Nên sửa |

## 4. Harness kiểm trình cài đặt trong container cô lập

Dùng khi cần kiểm một CLI hay trình cài đặt trên bản sao dự án dùng xong bỏ, mà phép thử không được sửa vào
checkout gốc.

- **Ranh giới nền tảng:** container Linux chỉ chứng minh hành vi trên Linux. macOS không chạy được trong
  Docker; container Windows cần engine Windows. Giữ ma trận CI chạy thẳng trên Ubuntu, macOS, Windows cho đường
  dẫn, shim lệnh, quoting và hệ tệp — không tuyên bố container Linux đã kiểm macOS hay Windows.
- **Ghim** image nền theo digest bất biến và ghim phiên bản CLI được cài.
- Chạy bằng UID/GID dạng số, không phải root; mount repo và dự án nguồn **chỉ đọc**, chép vào vùng làm việc
  tmpfs riêng (chỉ người dùng container đọc được, `noexec`) trước mọi thay đổi.
- `read_only: true`, `no-new-privileges:true`, `cap_drop: [ALL]`, `pids_limit` hữu hạn; chỉ tạo đúng các đường
  tạm công cụ cần ghi.
- Mặc định **không mạng** (`network_mode: none`) và **không** đưa thông tin đăng nhập của máy chủ vào; cần mạng
  thì mở bằng một dịch vụ riêng đặt tên rõ, bật có chủ đích — không bao giờ để biến môi trường vô tình bật.
- Mặc định chạy **dry-run**; chỉ nhận một danh sách chế độ được phép.
- Gọi tiến trình con bằng mảng tham số, không qua shell; không nội suy đường dẫn dự án vào chuỗi lệnh.
- Dọn đúng container và project Compose có tên đã tạo, không xoá volume hay image không liên quan.

## 5. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Stack Compose đầy đủ (app + postgres + redis + mailpit), Dockerfile dev/production, file override | `docker-compose-dev.md` |
| Tìm dịch vụ, mạng riêng, mở cổng, chiến lược volume, cứng hoá Dockerfile/Compose, quản lý secret, `.dockerignore` | `docker-network-volume-security.md` |
| Dockerfile production theo ngôn ngữ | `dockerfiles.md` |
| Chiến lược triển khai, probe, hoàn tác | `../SKILL.md` |
