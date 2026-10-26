# Cloud Run — build, deploy, traffic, rollback

Placeholder: `<PROJECT_ID>`, `<REGION>`, `<SERVICE>`, `<JOB>`, `<REGISTRY>`, `<IMAGE>`, `<REVISION>`. Thay bằng giá trị lấy từ hồ sơ
dự án hoặc `gcloud config list`; không đoán.

## Contents

1. Chọn hình dạng và dựng image · 2. Bẫy `builds submit --tag` · 3. Deploy, traffic, rollback · 4. Revision không khởi động ·
5. Bẫy script nối nhiều bước

## 1. Chọn hình dạng và dựng image

Quyết hình dạng trước: **site tĩnh** (script build ra `public/`, `dist/` hoặc `build/`) → Cloud Storage + CDN; **tiến trình
server chạy lâu** → Cloud Run. Rồi chọn **buildpacks** (Go, Node.js, Python, Java, .NET, Ruby, PHP — không cần Dockerfile) hoặc
**image tự dựng**. Image tự dựng thì build cục bộ một lần trước khi đẩy lên `<REGISTRY>`.

## 2. ⚠️ BẪY — không dùng `gcloud builds submit --tag` khi repo có nhiều Dockerfile

```bash
# ĐÚNG
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_PROJECT_ID=<PROJECT_ID>,_TAG=<TAG> \
  --project=<PROJECT_ID> .
```

Cờ `--tag` âm thầm chọn file tên `Dockerfile`. Nếu thư mục gốc có Dockerfile thứ hai (ví dụ một file tên khác mới là
image thật, còn `Dockerfile` là bản demo không phải web server) thì build **thành công**, container thoát mã 0 ngay khi
khởi động và Cloud Run báo `Default STARTUP TCP probe failed` trên cổng 8080 — ra một revision chết.

- **Tổng quát:** trước mọi `builds submit`, liệt kê Dockerfile ở thư mục gốc. Nhiều hơn một ⇒ dùng `--config` (kèm
  `cloudbuild.yaml` trỏ `--file`) hoặc `--file`, không bao giờ `--tag`.
- Giá trị mặc định trong `cloudbuild.yaml` (project cũ, tag) có thể lỗi thời: **luôn ghi đè** `_PROJECT_ID` bằng `<PROJECT_ID>`.
- Không truyền `--gcs-log-dir` khi YAML đã đặt `logging: CLOUD_LOGGING_ONLY` — hai cái xung đột.

## 3. Deploy, traffic, rollback

```bash
# deploy một image cụ thể, chưa nhận traffic
gcloud run deploy <SERVICE> --region=<REGION> \
  --image=<IMAGE> --no-traffic --tag=candidate

# kiểm tra
gcloud run revisions list --service=<SERVICE> --region=<REGION>
gcloud run services describe <SERVICE> --region=<REGION> --format='value(status.traffic)'

# chuyển traffic / canary
gcloud run services update-traffic <SERVICE> --region=<REGION> --to-latest
gcloud run services update-traffic <SERVICE> --region=<REGION> \
  --to-revisions=<REVISION_NEW>=10,<REVISION_OLD>=90

# ROLLBACK = ghim 100% vào revision tốt gần nhất
gcloud run services update-traffic <SERVICE> --region=<REGION> \
  --to-revisions=<REVISION_GOOD>=100
```

Rollback là thao tác **traffic**, không phải deploy lại: revision cũ vẫn gọi được nên ghim traffic là tức thì và không cần
build. **Ghi tên revision tốt gần nhất trước khi ship.** Schema dữ liệu vẫn phải tương thích với bản cũ — xem
`cloud-sql-migration.md`.

## 4. Revision không khởi động

Đọc log trước khi đổi bất cứ thứ gì:

```bash
gcloud run services logs read <SERVICE> --region=<REGION> --limit=100
```

`Default STARTUP TCP probe failed` trên cổng 8080 gần như luôn là: container không phải web server (xem mục 2) hoặc không
lắng nghe trên `$PORT`.

## 5. ⚠️ BẪY — script deploy nối nhiều bước cần `set -euo pipefail`

```bash
# SAI — tail mới là nguồn mã thoát và luôn trả 0, nên `set -e` không bao giờ nổ
# và bước kế tiếp chạy trên trạng thái đã hỏng
gcloud run jobs execute <JOB> --region=<REGION> 2>&1 | tail -20

# ĐÚNG
set -euo pipefail
```

Một sự cố thật: chuỗi migrate → deploy → đồng bộ tiếp tục chạy sau khi job migrate thất bại, đưa mã mới lên production mà
không có schema tương ứng; mọi truy vấn người dùng trả 500 cho tới khi rollback.

**Luật cho chuỗi deploy:** mở khối bằng `set -euo pipefail`, hoặc bỏ hẳn `| tail`. Khẳng định lệnh migrate trả 0 **trước khi**
lật revision. Gọi thử một endpoint đại diện sau migration và trước khi chuyển traffic, để lệch schema bị bắt khi rollback còn rẻ.
