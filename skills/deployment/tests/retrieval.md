---
skill: deployment
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 07b95c2020afe72d8978dbedd6ee2174eb8ca624
date: 2026-10-04
result: "strict 5/7 (+2 partial, 0 fail) — below threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: "a4379b103fc9b94d3"
  answers: a2061dd90e8050429
---

Đã đọc: `<gốc worktree>/skills/deployment/SKILL.md` `references/cicd-health-config.md`, `references/deployment-strategies.md`, `references/docker.md`, `references/docker-compose-dev.md`, `references/dockerfiles.md`, `references/docker-network-volume-security.md`

# Thử truy xuất - deployment

> **Kết luận:** strict 5/7 (+2 partial, 0 fail), dưới ngưỡng. Bộ câu MỚI (lượt độc lập `TK13`, người soạn không đọc skill) phủ các góc khác của `description`; 4 trong 6 câu tình huống Đạt hẳn, các câu còn lại trỏ đúng nơi nhưng thiếu nội dung (mục "Thiếu nội dung" bên dưới). Câu ranh giới Đạt. Bộ câu cũ giữ ở mục lịch sử.

Câu hỏi do người soạn mới (id ở `agent_ids`) viết từ `description` và danh sách câu cũ, không đọc skill. Cột "Mục kỳ vọng" và điều kiện Đạt ghi vào file nháp
`.tmp/deployment-expected.md` lúc 2026-10-04 10:45:54 +07:00, **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm); file nháp chép giữ mtime vào
`expected/deployment-expected.md`. Bài trả lời trọn của chủ thể (id ở `agent_ids`, 10 lượt công cụ) và bảng chấm ở `evidence/TK13/deployment-retrieval.md`
trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>`
vì repo chặn tên người dùng. Chủ thể được dặn nói thẳng khi skill không có phần câu hỏi cần, không dùng kiến thức ngoài.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Team mình có 3 môi trường (dev, staging, prod) và mỗi môi trường cần biến cấu hình riêng như DATABASE_URL, JWT_SECRET, REDIS_URL, FEATURE_FLAGS. Hôm qua prod lên được nhưng app chạy với DATABASE_URL trỏ nhầm sang staging vì thiếu biến mà không ai biết. Làm thế nào để validate cấu hình môi trường ngay lúc khởi động (fail fast nếu thiếu biến hoặc sai định dạng) và quản lý secret cho từng môi trường mà không commit vào repo? | `SKILL.md` › 2. Quy trình lõi (mục 4: kiểm cấu hình lúc khởi động) + `references/cicd-health-config.md` › 5. Cấu hình môi trường (schema kiểm, thiếu thì dừng, chỉ nêu tên biến) + `references/docker-network-volume-security.md` › 3 | `SKILL.md` › 2 (mục 4), › 6; `references/cicd-health-config.md` › 5; `references/docker-network-volume-security.md` › 3; `references/docker.md` › 1 | Đạt (phần phụ thiếu: quản lý secret riêng từng môi trường, kiểm host/tên DB khớp môi trường) |
| 2 | Mình deploy bản mới lên Kubernetes bằng rolling update, 12 pod, API xử lý khoảng 800 req/s. Mình muốn thử canary trước: chỉ 5% traffic sang bản mới, theo dõi error rate và p95 latency 30 phút rồi mới tăng dần. Chọn ngưỡng nào để tự động dừng/hủy canary, và tiến lên 25%, 50%, 100% theo tiêu chí nào? | `SKILL.md` › 1. Chọn chiến lược (Canary) + › 3. Trước, trong và sau khi bật lưu lượng (điều kiện huỷ đo được so với số đo nền, thời gian quan sát mỗi nấc, chỉ tăng nấc khi trong ngưỡng) + `references/deployment-strategies.md` › 3. Canary | `SKILL.md` › 1, › 3, › 4; `references/deployment-strategies.md` › 3 | Đạt (phần phụ thiếu: con số ngưỡng, nấc 25 %, cách chia 5 % lưu lượng trên Kubernetes) |
| 3 | Bản release 2.4 vừa lên prod cách đây 20 phút, error rate nhảy từ 0,2% lên 6%, và bản này có kèm một migration thêm cột NOT NULL vào bảng orders. Mình cần quay lại bản 2.3 gấp nhưng sợ rollback code thì app cũ không chạy được với schema mới. Quyết định rollback hay roll-forward thế nào, và chuẩn bị gì từ trước để việc quay lại không phá dữ liệu? | `SKILL.md` › 3 (chạm điều kiện huỷ → hoàn tác theo lệnh đã ghi) + › 5. Danh mục hoàn tác (migration tương thích ngược) + › 1 (hai bản cùng đọc ghi một CSDL: mở rộng → chuyển → thu hẹp) + `references/cicd-health-config.md` › 6 | `SKILL.md` › 1, › 3, › 4, › 5, › 6; `references/cicd-health-config.md` › 6 | Một phần (đủ tương thích ngược, danh mục hoàn tác, người dùng gật; thiếu tiêu chí rollback hay roll-forward) |
| 4 | Pipeline GitHub Actions của mình chạy 14 phút, trong đó cài dependency và build Docker image chiếm gần 10 phút mỗi lần dù chỉ sửa một dòng code. Repo là monorepo có 3 service. Làm sao cache layer và dependency, chỉ build service bị thay đổi, và đặt thứ tự job (lint, test, build, deploy) cho nhanh mà vẫn an toàn? | `references/cicd-health-config.md` › 1. GitHub Actions (cache npm, `cache-from type=gha`, `needs:`) + › 2. Các chặng pipeline + `references/docker.md` › 1 (thứ tự lớp quyết định cache); build chỉ service đổi trong monorepo không có | `references/cicd-health-config.md` › 1, › 2; `references/docker.md` › 1; `references/dockerfiles.md` › 1, › 4 | Một phần (có cache npm, cache layer `gha`, thứ tự job; thiếu monorepo) |
| 5 | Container Node của mình khi chạy `docker compose up` thì tự thoát với exit code 137 sau khoảng 2 phút, còn log thì không có lỗi gì. Máy host có 2 GB RAM, service dùng khoảng 1,5 GB lúc build cache. Làm sao khoanh vùng nguyên nhân (OOM kill, healthcheck fail, restart policy...) và đặt giới hạn tài nguyên hợp lý trong compose? | `references/docker.md` › 2. Debug (bảng mã thoát: 137 = hết bộ nhớ hoặc không thoát kịp sau SIGTERM, `docker inspect` xem cờ OOM, giới hạn bộ nhớ) + › 3. Lỗi hay gặp | `references/docker.md` › 2, › 1, › 3; `references/docker-compose-dev.md` › 3; `SKILL.md` › 6 | Đạt (phần phụ thiếu: cách chọn con số giới hạn, chính sách restart, kiểm log host) |
| 6 | Mình sắp có đợt release lớn vào tối thứ Sáu cho hệ thống thanh toán nội bộ, chạy 4 service và 1 job cron. Mình cần checklist đi tới release: kiểm tra gì trước giờ G, tiêu chí go/no-go, ai trực, dashboard nào theo dõi, và khi nào thì ra lệnh quay lại bản trước? | `SKILL.md` › 8. Sẵn sàng production (ứng dụng, hạ tầng, giám sát, bảo mật, vận hành: có người trực) + › 3 (điều kiện huỷ, quan sát sau deploy) + › 4 (production chờ người dùng gật, sau Cổng 2) | `SKILL.md` › 8, › 3, › 4, › 5 | Đạt (phần phụ thiếu: ngưỡng go/no-go bằng số, lịch trực, tên dashboard, job cron) |
| 7 | Bảng `events` có 120 triệu dòng trên Postgres, mình cần thêm cột `source_id` NOT NULL có giá trị mặc định và backfill dữ liệu cũ, trong khi hệ thống vẫn phải chạy 24/7 không được khóa bảng lâu. Chia migration thành những bước nào, backfill theo lô ra sao, và khi nào mới được thêm ràng buộc NOT NULL? | mục khác: skill `database-migrations` (từ `SKILL.md` › 1 và › 7 Liên quan: thứ tự schema ↔ code → `database-migrations`) | mục khác: `database-migrations` (từ `SKILL.md` › 1, › 7) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Câu 3: Khi nào vá tiến nhanh hơn quay lui (skill chỉ nghiêng về "cái hoàn tác nhanh hơn"), xử lý cột NOT NULL đã thêm (giữ, bỏ, cho phép rỗng), ngưỡng cụ thể.
- Câu 4: Chỉ build service bị thay đổi (lọc theo đường dẫn, ma trận theo service), cache theo service, song song hoá job.
- Điều kiện Đạt ghi trước ở file nháp có vài chỗ đánh dấu "phần phụ"; lượt này **không** nương theo dấu đó: việc câu hỏi nêu đích danh mà skill không có thì câu tính Một phần. Các phần phụ thiếu ở câu Đạt ghi ngay trong cột "Kết quả".
- Skill chưa sửa ở lượt này (việc của điều phối); `skill_sha` là băm cây skill hiện tại.

## Lịch sử

Lượt trước (`TK11`/`TK12`, bộ câu cũ, ngày 2026-10-04, `skill_sha` 07b95c2020afe72d8978dbedd6ee2174eb8ca624, id chủ thể a8af49a08b7eb6686): `result` là `strict 6/6 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 6/6`. Bảng cũ giữ nguyên chữ, nhãn `Cũ-n`:

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| Cũ-1 | Chuyển từ docker-compose trên một VM sang production thật; CI pipeline có bước scan image bằng Trivy, tag image theo git SHA thay vì `latest`, push lên registry. Thiết kế stage và quy ước tag/promote từ staging lên prod thế nào cho gọn và truy vết được? | `references/cicd-health-config.md` › 1, › 2 (các chặng + chặng quét image Trivy: `--severity`, `--exit-code 1`, `--ignore-unfixed`, ngưỡng ghi PLAN) + `SKILL.md` › 2 (production nhận đúng image, tag `github.sha`) | `SKILL.md` › 2; `references/cicd-health-config.md` › 1; › 2 | Đạt |
| Cũ-2 | Container chạy được trên dev nhưng lên server crash lúc khởi động vì ghi file vào `/app/uploads`, permission denied sau khi đổi sang `USER node`. Sửa ownership, dùng volume, hay đổi cách lưu file? | `references/dockerfiles.md` › 5 (quyền ghi khi `USER` không root: `mkdir` + `chown` trước `USER`, volume có tên, bind mount UID/GID, dữ liệu thật ngoài container) + `docker-network-volume-security.md` › 2, › 3 | `references/dockerfiles.md` › 5; `SKILL.md` › 4 | Đạt |
| Cũ-3 | Blue-green cho API có session lưu trong memory từng instance, lo user văng đăng nhập lúc cutover. Cần chuẩn bị gì trước khi switch traffic, giữ đường quay lại bản blue vài giờ đầu thế nào? | `references/deployment-strategies.md` › 2 (phiên đăng nhập khi blue-green: kho dùng chung / token ký; giữ bản blue trong cửa sổ quan sát) + `SKILL.md` › 3, › 4, › 5 | `references/deployment-strategies.md` › 2. Blue-green; `SKILL.md` › 3; › 5 | Đạt |
| Cũ-4 | Dockerfile một stage, cài cả compiler lẫn devDependencies rồi build, image nặng nhiều CVE từ build tools. Tách multi-stage thế nào, chọn base image runtime nào (slim, alpine, distroless)? | `references/dockerfiles.md` › 1–3 (multi-stage), › 5 (bảng slim / alpine / distroless) + `references/docker.md` › 1 | `references/dockerfiles.md` › 1; › 5; `references/cicd-health-config.md` › 2 | Đạt |
| Cũ-5 | Service khởi động ~90 giây (warm cache, load model) nên Kubernetes kill pod trước khi sẵn sàng. Cấu hình `startupProbe`, `readinessProbe`, `livenessProbe` ra sao, đặt `terminationGracePeriodSeconds` thế nào để tắt pod không rớt request? | `references/cicd-health-config.md` › 4 (`startupProbe` bao 90 giây, readiness, liveness, `terminationGracePeriodSeconds` gồm cả `preStop`, SIGTERM, `maxUnavailable` / `maxSurge`) + `docker.md` › 3 (init, SIGTERM) | `references/cicd-health-config.md` › 4. Probe Kubernetes; `SKILL.md` › 2 | Đạt |
| Cũ-6 | `GET /orders` trả cả nghìn bản ghi một response, mobile chậm; thêm pagination cursor, giữ tương thích app cũ không truyền tham số. Thiết kế query params, response envelope, versioning thế nào? | mục khác: skill `api-design` | mục khác: `api-design`; nói rõ skill này không phủ | Đạt |
