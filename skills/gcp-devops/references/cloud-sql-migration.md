# Cloud SQL — Auth Proxy, backup, job migrate

Placeholder: `<PROJECT_ID>`, `<REGION>`, `<INSTANCE>`, `<JOB>`, `<SERVICE>`, `<SECRET_NAME>`, `<DB_USER>`, `<VERSION>`, `<BINARY>`, `<TAG>`.

## Contents

1. Cloud SQL Auth Proxy · 2. Backup và thao tác instance · 3. Job migrate (Cloud Run job)

## 1. Cloud SQL Auth Proxy (truy cập từ máy cục bộ)

Binary **không** phát hành dạng asset của GitHub release; nó nằm trên `storage.googleapis.com`. Lấy số phiên bản mới nhất ở
trang release của kho `cloud-sql-proxy` (GoogleCloudPlatform) rồi tải đúng bản cho hệ điều hành:

```bash
# <VERSION>: phiên bản mới nhất; <BINARY>: tên file theo hệ điều hành
BIN="$(mktemp -d)/cloud-sql-proxy"      # thư mục tạm quyền 0700
curl -sL -o "$BIN" \
  "https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/<VERSION>/<BINARY>"
chmod +x "$BIN"                          # bỏ bước này trên Windows (file .exe)
"$BIN" <PROJECT_ID>:<REGION>:<INSTANCE> --gcloud-auth --port 5433
```

`--gcloud-auth` dùng lại người dùng đã `gcloud auth login`, tránh một vòng trình duyệt `gcloud auth application-default login`.

⚠️ **BẪY:** đừng tin binary nằm sẵn trong repo. Một file proxy bị commit từng chỉ là **phản hồi XML 404 vài trăm byte**, không
phải chương trình — kiểm kích thước rồi **tải bản mới**. Instance có IP công khai mà không có authorized network thì proxy là
đường vào duy nhất.

## 2. Backup và thao tác instance

```bash
gcloud sql backups list   --instance=<INSTANCE> --project=<PROJECT_ID>
gcloud sql backups create --instance=<INSTANCE> --description="pre-migration <TAG>"
gcloud sql instances describe <INSTANCE> --format='value(settings.tier,state)'
```

**Backup trước mọi migration có tính huỷ.** Restore ghi đè instance — xác nhận với người dùng trước khi chạy, không tự làm.

## 3. Job migrate (Cloud Run job)

**Audit cấu hình job trước mỗi lần deploy migration** — nó đã từng lệch âm thầm:

```bash
gcloud run jobs describe <JOB> --region <REGION> --project <PROJECT_ID>
# BẮT BUỘC có:
#   annotations.run.googleapis.com/cloudsql-instances = <PROJECT_ID>:<REGION>:<INSTANCE>
#   env DATABASE_URL = secretKeyRef <SECRET_NAME>:latest      (KHÔNG phải giá trị literal)
gcloud run jobs execute <JOB> --region=<REGION> --wait
```

⚠️ **BẪY:** job từng được tạo **không gắn Cloud SQL instance** (socket `/cloudsql/...` không tồn tại) **và** để `DATABASE_URL`
là giá trị literal chứa mật khẩu trước lần xoay → `password authentication failed for "<DB_USER>"`. DSN literal cũ đi sau mỗi lần
xoay; `secretKeyRef` thì không. Tạo lại job thì chép cấu hình của **service** `<SERVICE>` đang chạy đúng.

Chuỗi migrate của repo có thể có lệch đã biết: đọc docstring migration trước khi tin `upgrade head` sạch. Kiểm mã thoát của job
trước khi lật revision (`cloud-run-deploy.md` mục 5).
