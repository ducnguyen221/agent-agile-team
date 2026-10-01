---
name: deployment
description: Use when containerizing an app, writing or reviewing a Dockerfile or compose file, setting up a CI/CD pipeline, adding health checks or probes, choosing a rollout strategy (rolling, blue-green, canary), planning a rollback, validating environment config, debugging a container, or preparing a production release.
metadata:
  group: technique
  roles: [implementer]
source: [affaan-m/ECC skills/deployment-patterns/SKILL.md, affaan-m/ECC skills/docker-patterns/SKILL.md]
source_sha: [c70874fae9eb0e5ad0365beb7e2955899fd1d30f, c70874fae9eb0e5ad0365beb7e2955899fd1d30f]
license: MIT
rewrite_before_public: false
---

# Triển khai

> **Kết luận:** đóng gói bằng Dockerfile nhiều tầng (người dùng không phải root, tag ghim, `HEALTHCHECK`),
> pipeline đi lint → test → build image → staging → smoke test → production, cấu hình chỉ qua biến môi
> trường được kiểm lúc khởi động, và **luôn có đường hoàn tác đã thử**. Deploy production và rollback là
> hành động ra ngoài: chỉ làm khi người dùng gật.

## 1. Chọn chiến lược triển khai

| Chiến lược | Đặc tính chính | Chi phí | Chọn khi |
|---|---|---|---|
| **Rolling** | thay dần từng instance; hai bản chạy song song | thấp | thay đổi tương thích ngược, việc thường ngày |
| **Blue-green** | chuyển toàn bộ lưu lượng một lần giữa hai môi trường đầy đủ; hoàn tác tức thì | gấp đôi hạ tầng lúc deploy | dịch vụ quan trọng, không chấp nhận sự cố |
| **Canary** | một phần nhỏ lưu lượng sang bản mới trước, rồi tăng dần | cần chia lưu lượng + giám sát | lưu lượng cao, thay đổi rủi ro |

Sơ đồ lưu lượng và đánh đổi từng chiến lược: `references/deployment-strategies.md`.

## 2. Quy trình lõi

1. **Đóng gói** bằng Dockerfile nhiều tầng: người dùng không phải root, tag ghim, `HEALTHCHECK` — mẫu ở
   `references/dockerfiles.md`; luật Docker và Compose ở `references/docker.md`.
2. **Nối pipeline**: lint → kiểm kiểu → test → build image → deploy staging → smoke test → deploy
   production — YAML ở `references/cicd-health-config.md`.
3. **Health check**: `/health` (đơn giản) và `/health/detailed` (kiểm phụ thuộc); gắn vào probe liveness,
   readiness, startup.
4. **Kiểm cấu hình lúc khởi động** (twelve-factor, biến môi trường kiểm bằng schema) — sai thì dừng ngay.
5. **Giữ đường hoàn tác tức thì** và thử nó ở staging trước khi cần tới.

Dự án hoặc máy có công cụ deploy riêng (script, runbook, lệnh nền tảng) thì dùng công cụ đó; các mẫu ở
đây là mặc định khi chưa có.

## 3. Điều kiện dừng

- **Deploy production, rollback production, chạy migration trên dữ liệu thật, xoá volume / image** là
  hành động ra ngoài hoặc không đảo ngược: dừng, trình lệnh sẽ chạy + ảnh hưởng + cách hoàn tác, **chờ
  người dùng gật**. Gật cho một lần deploy không phải gật cho lần sau.
- Deploy staging, build image cục bộ, chạy compose dev được làm trong phạm vi việc đã giao.
- Không sửa cấu hình CI hay cấu hình deploy để "cho qua"; đổi cấu hình kiểm là một việc riêng có lý do.

## 4. Danh mục hoàn tác

- [ ] Image / artifact bản trước còn và có tag
- [ ] Migration DB tương thích ngược (không thay đổi phá huỷ cùng đợt) — skill `database-migrations`
- [ ] Feature flag tắt được tính năng mới mà không cần deploy
- [ ] Cảnh báo giám sát đặt cho tỉ lệ lỗi tăng vọt
- [ ] Đã thử hoàn tác ở staging trước khi lên production

## 5. Docker và Compose

Luật chính, lệnh debug, phản mẫu, và cách dựng harness kiểm trình cài đặt trong container cô lập:
**`references/docker.md`**. Từ đó trỏ tiếp tới stack Compose cho dev (`references/docker-compose-dev.md`)
và mạng, volume, bảo mật container (`references/docker-network-volume-security.md`).

## 6. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Sơ đồ lưu lượng rolling / blue-green / canary, được mất, khi nào dùng | `references/deployment-strategies.md` |
| Dockerfile nhiều tầng (Node.js, Go, Python/Django), nên và không nên | `references/dockerfiles.md` |
| Pipeline GitHub Actions, các chặng pipeline, endpoint health, probe Kubernetes, cấu hình twelve-factor + kiểm, lệnh hoàn tác | `references/cicd-health-config.md` |
| Luật Docker/Compose, debug, phản mẫu, harness cô lập | `references/docker.md` |

Liên quan: skill `github-ops` (workflow CI), `security-review` (secret, CVE, header bảo mật),
`error-handling` (log không lộ secret), `closing-sprint` (deploy nằm sau Cổng 2).

## 7. Sẵn sàng production

Trước mọi lần deploy production:

**Ứng dụng**
- [ ] Mọi test đạt (unit, tích hợp, end-to-end)
- [ ] Không secret cứng trong code hay file cấu hình
- [ ] Xử lý lỗi phủ các nhánh biên
- [ ] Log có cấu trúc (JSON), không chứa dữ liệu cá nhân
- [ ] Endpoint health trả trạng thái có ý nghĩa

**Hạ tầng**
- [ ] Image build tái tạo được (phiên bản ghim)
- [ ] Biến môi trường có tài liệu và được kiểm lúc khởi động
- [ ] Đặt giới hạn tài nguyên (CPU, bộ nhớ)
- [ ] Cấu hình co giãn ngang (số instance tối thiểu / tối đa)
- [ ] TLS bật trên mọi endpoint

**Giám sát**
- [ ] Xuất metric ứng dụng (lượng yêu cầu, độ trễ, lỗi)
- [ ] Cảnh báo khi tỉ lệ lỗi vượt ngưỡng
- [ ] Gom log (có cấu trúc, tìm được)
- [ ] Giám sát uptime trên endpoint health

**Bảo mật**
- [ ] Phụ thuộc đã quét CVE
- [ ] CORS chỉ cho origin được phép
- [ ] Rate limit trên endpoint công khai
- [ ] Đã kiểm xác thực và phân quyền
- [ ] Đặt header bảo mật (CSP, HSTS, X-Frame-Options)

**Vận hành**
- [ ] Kế hoạch hoàn tác có tài liệu và đã thử
- [ ] Migration DB đã thử trên dữ liệu cỡ production
- [ ] Runbook cho các tình huống hỏng thường gặp
- [ ] Có người trực và đường báo cấp trên
