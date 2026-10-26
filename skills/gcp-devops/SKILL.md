---
name: gcp-devops
description: Use when deploying or operating a service on Google Cloud (Cloud Run, Cloud SQL, Secret Manager, HTTPS load balancer) - checking gcloud auth and config, building and pushing an image, running a migration job, shifting traffic or rolling back, mounting or rotating a secret, adding a managed certificate, or debugging a revision that will not start or a 403. Not for platform-neutral Docker/CI/rollout patterns (use `deployment`) nor incident investigation (use `gcp-incident-response`).
metadata:
  group: technique
  roles: [implementer]
source: ["concept: gcloud-auth-verification (Google datacloud, section 1 only)"]
source_sha: ["c125eaea039b9440b306b428ee2068d79123ddb7"]
license: [Apache-2.0]
rewrite_before_public: false
---

# Vận hành dịch vụ trên Google Cloud (gcloud · Cloud Run · Cloud SQL · Secret Manager)

> **Kết luận:** mọi lệnh `gcloud` đổi trạng thái chỉ chạy khi project, region và tên tài nguyên **đến từ người dùng
> hoặc từ cấu hình thật**, sau khi đã `describe` hiện trạng; danh tính do người dùng dựng, agent không sửa hộ; secret
> không bao giờ xuất hiện trong lời nhắn, tham số lệnh hay kết quả công cụ. Khi tài liệu hãng và hiện trạng khác nhau,
> `describe` tài nguyên thật rồi tin trạng thái thật. Giá trị riêng của dự án (mã project, tên dịch vụ, secret, IP, domain)
> lấy từ hồ sơ dự án của bạn; mọi khối lệnh trong skill này dùng placeholder `<PROJECT_ID>`, `<REGION>`, `<SERVICE>`…

## 0. Nguyên tắc vận hành (trước mọi lệnh)

1. **Không đoán định danh.** `--project`, `--region` và tên tài nguyên chỉ lấy từ lời người dùng hoặc `gcloud config list`;
   thiếu thì hỏi. Deploy nhầm project không có nút hoàn tác.
2. **Không vá danh tính hộ người dùng.** Đăng nhập là việc của người; agent thấy lỗi xác thực thì dừng và nhờ họ xử lý (mục 1).
3. **Lệnh chuyên dụng thắng lệnh thô.** `gcloud run services update` hơn sửa tay YAML; lệnh Cloud Run hơn gọi REST thẳng.
4. **Đọc rồi mới ghi.** `describe` tài nguyên trước khi đổi — trạng thái hiện tại là đầu vào an toàn duy nhất cho một thay đổi.
5. **Secret ngoài transcript.** Không trong chat, tham số lệnh, commit message hay kết quả công cụ; mẫu bàn giao qua file ở
   `references/secrets.md`.
6. **Quét secret trước khi build hoặc push.** Image đọc được trong cả project; khoá nướng vào image còn sống sau khi đã
   xoay file nguồn.

## 1. Xác thực và cấu hình

```bash
gcloud auth list          # LUÔN chạy trước khi kết luận "chưa đăng nhập"
gcloud config list        # project / region / account đang dùng
```

Với `No credentialed accounts.`, `No account is currently active.` hay `DefaultCredentialsError`:

- `auth list` **không có tài khoản** → nhờ người dùng chạy `gcloud auth login` (và `gcloud auth application-default login`
  nếu thư viện hay notebook cần ADC). Chạy lại `auth list` sau khi họ báo xong.
- `auth list` **có tài khoản** mà vẫn `403` → đây là **IAM, không phải xác thực**: xem role binding, đừng bắt đăng nhập lại.
- **Danh tính CLI và ADC có thể khác nhau**: lệnh `gcloud` chạy được mà lời gọi thư viện/REST vẫn 403 là dấu hiệu đó.
- Không sửa credential bằng mã hay công cụ khác; dừng và hỏi.
- `--project` và region đọc từ cấu hình thật (hoặc từ người dùng), không suy từ tên thư mục hay lần chạy trước.

## 2. Việc nào đọc reference nào

| Việc | Đọc |
|---|---|
| build image (nhiều Dockerfile), deploy, chia traffic, rollback, đọc log revision không khởi động, script deploy nối nhiều bước | `references/cloud-run-deploy.md` |
| kết nối Cloud SQL (Auth Proxy), backup, audit job migrate | `references/cloud-sql-migration.md` |
| gắn secret, xoay secret, ký tự trong mật khẩu DSN, không echo secret | `references/secrets.md` |
| HTTPS load balancer, chứng chỉ managed (wildcard), chính sách org chặn service agent | `references/lb-tls.md` |

## 3. Checklist trước khi deploy production

- [ ] `gcloud config list`: đúng project và region?
- [ ] Đã quét secret trên diff; không khoá hay mật khẩu nào nằm trong image hoặc commit
- [ ] Image build bằng `--config` hoặc `--file`, không `--tag` khi repo có nhiều Dockerfile (`cloud-run-deploy.md`)
- [ ] Audit job migrate xong; backup đã tạo (`cloud-sql-migration.md`)
- [ ] Script deploy mở đầu bằng `set -euo pipefail` (`cloud-run-deploy.md`)
- [ ] Đã ghi tên revision tốt gần nhất để hoàn tác (`cloud-run-deploy.md`)
- [ ] Secret mới gắn bằng `secretKeyRef`, không literal (`secrets.md`)
- [ ] Sau deploy: revision đang phục vụ, endpoint đại diện qua smoke test, log sạch

Deploy production, rollback production và restore dữ liệu là hành động ra ngoài: làm khi người dùng đã gật.

## 4. Liên quan

- `deployment` — mẫu Docker, CI/CD, rollout không gắn nhà cung cấp; skill này là lớp riêng Google Cloud.
- `gcp-incident-response` — sự cố đang xảy ra: phân loại, giảm thiểu, SLO, postmortem.
