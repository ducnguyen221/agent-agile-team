---
name: deployment
description: Use when containerizing an app, writing or reviewing a Dockerfile or compose file, setting up a CI/CD pipeline, adding health checks or probes, choosing a rollout strategy (rolling, blue-green, canary), planning a rollback, validating environment config, debugging a container, or preparing a production release.
metadata:
  group: technique
  kind: reference
  roles: [implementer]
source: [affaan-m/ECC skills/deployment-patterns/SKILL.md, affaan-m/ECC skills/docker-patterns/SKILL.md]
source_sha: [ef648e01899ba3e8dc6371642deaaf64b4477775, ef648e01899ba3e8dc6371642deaaf64b4477775]
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: [MIT, MIT]
rewrite_before_public: false
---

# Triển khai

> **Kết luận:** chọn chiến lược theo câu hỏi **"bản cũ và bản mới có chạy cạnh nhau được không"**; đóng gói
> thành image tái tạo được, gắn tag bất biến; pipeline đi qua staging và smoke test rồi mới tới production;
> **trước khi bật lưu lượng** đã viết điều kiện huỷ đo được và đã thử đường hoàn tác. Deploy production,
> rollback production và xoá dữ liệu là hành động ra ngoài: chỉ làm khi người dùng gật, mỗi lần một lần gật.
> "Đã deploy" chưa phải "chạy đúng" — kết quả ghi thành bằng chứng mới chạy.

## 1. Chọn chiến lược triển khai

| Chiến lược | Cách chạy | Hoàn tác | Chi phí | Chọn khi |
|---|---|---|---|---|
| **Rolling** (mặc định) | thay từng instance; hai bản phục vụ cùng lúc trong đợt | chạy lại đợt với bản cũ — chậm như lúc lên | thấp | thay đổi tương thích ngược, việc thường ngày |
| **Blue-green** | dựng đủ môi trường thứ hai, kiểm xong mới chuyển **toàn bộ** lưu lượng một lần | chuyển lưu lượng về — gần như tức thì | gấp đôi hạ tầng trong lúc deploy | dịch vụ quan trọng, không chấp nhận sự cố kéo dài |
| **Canary** | đưa một phần nhỏ lưu lượng thật sang bản mới, tăng theo nấc khi số đo ổn | rút phần lưu lượng canary về | cần chia lưu lượng + giám sát theo bản | lưu lượng lớn, thay đổi rủi ro, cần thấy lỗi trên tải thật |

- Rolling và canary để **hai bản cùng đọc ghi một CSDL**: schema phải hợp với cả hai — mở rộng trước, chuyển
  dữ liệu, thu hẹp ở đợt sau (skill `database-migrations`). Không đạt điều đó → blue-green có khoảng bảo trì,
  hoặc tách thay đổi schema ra một lần deploy riêng.
- Phân vân giữa hai chiến lược → chọn cái hoàn tác nhanh hơn.

Sơ đồ lưu lượng từng chiến lược: `references/deployment-strategies.md`.

## 2. Quy trình lõi

1. **Đóng gói** bằng Dockerfile nhiều tầng: người dùng không phải root, image nền ghim phiên bản,
   `HEALTHCHECK`; tag image bằng mã commit, không dùng tag trôi — mẫu ở `references/dockerfiles.md`, luật
   Docker và Compose ở `references/docker.md`.
2. **Nối pipeline**: lint → kiểm kiểu → test → build image → deploy staging → smoke test → deploy production.
   Production nhận **đúng image** đã qua staging, không build lại — YAML ở `references/cicd-health-config.md`.
3. **Health check và probe** — ba câu hỏi khác nhau, đừng dồn vào một endpoint:
   - liveness: tiến trình còn sống không — **không** kiểm phụ thuộc, nếu không thì CSDL chập chờn làm mọi
     instance bị khởi động lại cùng lúc;
   - readiness: instance phục vụ được chưa — được kiểm phụ thuộc thiết yếu; hỏng thì chỉ rút khỏi lưu lượng;
   - startup: cho khởi động chậm thời gian riêng, để liveness không giết instance đang khởi động.
   Endpoint chi tiết (phiên bản, trạng thái từng phụ thuộc) chỉ mở cho giám sát nội bộ.
4. **Kiểm cấu hình lúc khởi động**: mọi cấu hình qua biến môi trường, kiểm bằng schema; thiếu hay sai thì
   dừng ngay, không chạy với giá trị mặc định đoán.
5. **Giữ đường hoàn tác tức thì** và thử nó ở staging trước khi cần tới (mục 5).

Dự án hoặc máy có công cụ deploy riêng (script, runbook, lệnh nền tảng) thì dùng công cụ đó; các mẫu ở đây là
mặc định khi chưa có.

## 3. Trước, trong và sau khi bật lưu lượng

- **Trước:** ghi điều kiện huỷ đo được — tỉ lệ lỗi, độ trễ p95 so với số đo ngay trước deploy, health
  check hỏng — cùng thời gian quan sát mỗi nấc và lệnh hoàn tác cụ thể. Không có số đo nền → đo trước rồi
  mới deploy.
- **Trong** (rolling, canary): chỉ tăng nấc khi số đo nằm trong ngưỡng suốt thời gian quan sát. Chạm điều kiện
  huỷ → dừng tăng nấc, hoàn tác theo lệnh đã ghi (nếu người dùng đã duyệt sẵn kế hoạch hoàn tác kèm điều kiện huỷ đó; chưa thì trình lệnh và chờ gật, mục 4), rồi điều tra (skill `debugging`); không "chờ thêm chút xem có tự hết".
- **Sau:** smoke test trên production, so số đo với nền; ghi thành `VR` gồm lệnh + kết quả mới chạy
  (`method/evidence.md`). Lỗi lọt qua deploy → ghi vào REQUESTS theo skill `bug-triage`.

## 4. Điều kiện dừng

- **Deploy production, rollback production, chạy migration trên dữ liệu thật, xoá volume hay image** là hành
  động ra ngoài hoặc không đảo ngược: dừng, trình lệnh sẽ chạy + ảnh hưởng + cách hoàn tác, **chờ người dùng
  gật**. Gật cho một lần deploy không phải gật cho lần sau; pipeline tự deploy không thay được lời gật đó khi
  chính agent là người kích hoạt. Ngoại lệ duy nhất: người dùng đã duyệt sẵn kế hoạch hoàn tác kèm điều
  kiện huỷ (mục 3) — chạm đúng điều kiện đó thì hoàn tác đúng kế hoạch đã duyệt, không hơn.
- Deploy staging, build image cục bộ, chạy compose dev được làm trong phạm vi việc đã giao.
- Không sửa cấu hình CI hay cấu hình deploy để "cho qua"; đổi cấu hình kiểm là một việc riêng có lý do.
- Deploy production nằm **sau Cổng 2** (skill `closing-sprint`), không phải bước cuối của thực thi.

## 5. Danh mục hoàn tác

- [ ] Image hay artifact bản trước còn trong registry, tag bất biến (không bị ghi đè)
- [ ] Migration CSDL tương thích ngược, không có thay đổi phá huỷ cùng đợt (skill `database-migrations`)
- [ ] Feature flag tắt được tính năng mới mà không cần deploy
- [ ] Cảnh báo giám sát đặt cho tỉ lệ lỗi tăng vọt
- [ ] Đã thử hoàn tác ở staging, đo thời gian hoàn tác

## 6. Lỗi hay gặp khi viết và review

Mức là gợi ý theo **hậu quả nếu bỏ qua**; quyết cuối theo `method/severity.md` mục 1.

| Dấu hiệu | Hậu quả | Mức gợi ý |
|---|---|---|
| Secret trong Dockerfile, lớp image, file compose đã commit, hay log build | ai kéo được image là đọc được secret | Chặn |
| Thay đổi phá huỷ schema cùng đợt rolling với code mới | bản cũ còn chạy ghi hỏng dữ liệu, không hoàn tác được | Chặn |
| Liveness kiểm CSDL hay dịch vụ ngoài | phụ thuộc chập chờn → khởi động lại dây chuyền, sập toàn bộ | Phải sửa |
| `/health` luôn trả 200 dù không phục vụ được | lưu lượng đổ vào instance hỏng, cảnh báo im lặng | Phải sửa |
| Không có đường hoàn tác đã thử, hoặc tag bản trước bị ghi đè | sự cố kéo dài trong lúc dựng lại bản cũ | Phải sửa |
| Tag trôi, phụ thuộc không ghim, build lại image cho production | bản lên production khác bản đã kiểm ở staging | Phải sửa |
| Container chạy bằng root | lỗ hổng ứng dụng thành quyền root trong container | Phải sửa (Chặn khi `privileged` hay mount socket Docker) |
| Thiếu giới hạn CPU, bộ nhớ | một instance ngốn hết máy, kéo instance khác chết theo | Nên sửa |
| Cấu hình đọc lười, lỗi lúc chạy thay vì lúc khởi động | lỗi lộ ra giữa giờ cao điểm thay vì lúc deploy | Nên sửa |

## 7. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Sơ đồ lưu lượng rolling / blue-green / canary, được mất, khi nào dùng | `references/deployment-strategies.md` |
| Dockerfile nhiều tầng (Node.js, Go, Python/Django), nên và không nên | `references/dockerfiles.md` |
| Pipeline GitHub Actions, các chặng pipeline, endpoint health, probe Kubernetes, cấu hình twelve-factor + kiểm, lệnh hoàn tác | `references/cicd-health-config.md` |
| Luật Docker/Compose, debug theo mã thoát, lỗi hay gặp, harness kiểm trình cài đặt cô lập | `references/docker.md` |
| Stack Compose cho dev; mạng, volume, bảo mật container | `references/docker-compose-dev.md`, `references/docker-network-volume-security.md` |

Liên quan: skill `github-ops` (workflow CI), `security-review` và agent `security-reviewer` (secret, CVE,
header bảo mật), `error-handling` (log không lộ secret), `database-migrations` (thứ tự schema ↔ code),
`closing-sprint` (deploy sau Cổng 2), `debugging` (container chết, health chập chờn).

## 8. Sẵn sàng production

Trước mọi lần deploy production:

- **Ứng dụng:** [ ] mọi test đạt (unit, tích hợp, end-to-end) · [ ] không secret cứng trong code hay cấu
  hình · [ ] xử lý lỗi phủ nhánh biên · [ ] log có cấu trúc, không dữ liệu cá nhân · [ ] endpoint health trả
  trạng thái có nghĩa
- **Hạ tầng:** [ ] image build tái tạo được (phiên bản ghim) · [ ] biến môi trường có tài liệu và được kiểm
  lúc khởi động · [ ] giới hạn CPU, bộ nhớ · [ ] co giãn ngang (số instance tối thiểu, tối đa) · [ ] TLS trên
  mọi endpoint
- **Giám sát:** [ ] metric lượng yêu cầu, độ trễ, lỗi · [ ] cảnh báo khi tỉ lệ lỗi vượt ngưỡng · [ ] log gom
  về một chỗ, tìm được · [ ] giám sát uptime trên endpoint health
- **Bảo mật:** [ ] phụ thuộc đã quét CVE · [ ] CORS chỉ cho origin được phép · [ ] rate limit trên endpoint
  công khai · [ ] đã kiểm xác thực và phân quyền · [ ] header bảo mật (CSP, HSTS, chống nhúng khung)
- **Vận hành:** [ ] kế hoạch hoàn tác có tài liệu và đã thử · [ ] migration đã thử trên dữ liệu cỡ
  production · [ ] runbook cho tình huống hỏng thường gặp · [ ] có người trực và đường báo cấp trên
