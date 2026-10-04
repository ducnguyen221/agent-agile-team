---
skill: deployment
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 07b95c2020afe72d8978dbedd6ee2174eb8ca624
date: 2026-10-04
result: "strict 6/6 (+0 partial, 0 fail) — at threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 6/6"
agent_ids:
  questions: "bộ câu cũ giữ nguyên, không soạn mới"
  answers: a8af49a08b7eb6686
---

Đã đọc: `<gốc worktree>/skills/deployment/SKILL.md` cùng `references/deployment-strategies.md`, `references/dockerfiles.md`, `references/cicd-health-config.md`

# Thử truy xuất - deployment

> **Kết luận:** strict 6/6: đạt ngưỡng. Sau `TK11.7` năm câu tình huống đều Đạt (lượt trước 4/6 Đạt hẳn, 2 Một phần; các ý còn thiếu: Trivy, `USER` không root và quyền thư mục ghi, session blue-green, slim/alpine/distroless, `terminationGracePeriodSeconds`); câu ranh giới trả `api-design`.

Bộ câu hỏi giữ nguyên chữ của lượt trước (bộ câu cũ giữ nguyên, không soạn mới); bộ câu mới là việc của `TK13`. Cột "Mục kỳ vọng" ghi vào file nháp
`.tmp/deployment-expected.md` **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm). Bài trả lời của chủ thể (id ở
`agent_ids`) và bảng chấm ở `evidence/TK11/deployment-retrieval.md` trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời,
đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Chuyển từ docker-compose trên một VM sang production thật; CI pipeline có bước scan image bằng Trivy, tag image theo git SHA thay vì `latest`, push lên registry. Thiết kế stage và quy ước tag/promote từ staging lên prod thế nào cho gọn và truy vết được? | `references/cicd-health-config.md` › 1, › 2 (các chặng + chặng quét image Trivy: `--severity`, `--exit-code 1`, `--ignore-unfixed`, ngưỡng ghi PLAN) + `SKILL.md` › 2 (production nhận đúng image, tag `github.sha`) | `SKILL.md` › 2; `references/cicd-health-config.md` › 1; › 2 | Đạt |
| 2 | Container chạy được trên dev nhưng lên server crash lúc khởi động vì ghi file vào `/app/uploads`, permission denied sau khi đổi sang `USER node`. Sửa ownership, dùng volume, hay đổi cách lưu file? | `references/dockerfiles.md` › 5 (quyền ghi khi `USER` không root: `mkdir` + `chown` trước `USER`, volume có tên, bind mount UID/GID, dữ liệu thật ngoài container) + `docker-network-volume-security.md` › 2, › 3 | `references/dockerfiles.md` › 5; `SKILL.md` › 4 | Đạt |
| 3 | Blue-green cho API có session lưu trong memory từng instance, lo user văng đăng nhập lúc cutover. Cần chuẩn bị gì trước khi switch traffic, giữ đường quay lại bản blue vài giờ đầu thế nào? | `references/deployment-strategies.md` › 2 (phiên đăng nhập khi blue-green: kho dùng chung / token ký; giữ bản blue trong cửa sổ quan sát) + `SKILL.md` › 3, › 4, › 5 | `references/deployment-strategies.md` › 2. Blue-green; `SKILL.md` › 3; › 5 | Đạt |
| 4 | Dockerfile một stage, cài cả compiler lẫn devDependencies rồi build, image nặng nhiều CVE từ build tools. Tách multi-stage thế nào, chọn base image runtime nào (slim, alpine, distroless)? | `references/dockerfiles.md` › 1–3 (multi-stage), › 5 (bảng slim / alpine / distroless) + `references/docker.md` › 1 | `references/dockerfiles.md` › 1; › 5; `references/cicd-health-config.md` › 2 | Đạt |
| 5 | Service khởi động ~90 giây (warm cache, load model) nên Kubernetes kill pod trước khi sẵn sàng. Cấu hình `startupProbe`, `readinessProbe`, `livenessProbe` ra sao, đặt `terminationGracePeriodSeconds` thế nào để tắt pod không rớt request? | `references/cicd-health-config.md` › 4 (`startupProbe` bao 90 giây, readiness, liveness, `terminationGracePeriodSeconds` gồm cả `preStop`, SIGTERM, `maxUnavailable` / `maxSurge`) + `docker.md` › 3 (init, SIGTERM) | `references/cicd-health-config.md` › 4. Probe Kubernetes; `SKILL.md` › 2 | Đạt |
| 6 | `GET /orders` trả cả nghìn bản ghi một response, mobile chậm; thêm pagination cursor, giữ tương thích app cũ không truyền tham số. Thiết kế query params, response envelope, versioning thế nào? | mục khác: skill `api-design` | mục khác: `api-design`; nói rõ skill này không phủ | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có. `docker.md` (init, `SIGTERM`, mã thoát 137) và Kết luận của `SKILL.md` (ngoại lệ kế hoạch hoàn tác đã duyệt) đã sửa theo `RF131` và `RF133`.
- Chủ thể nêu: skill không chốt một nền runtime cho Node, chỉ cho tiêu chí chọn (câu 4).
- Nguồn của phần thêm ở `TK11.7`: tài liệu Trivy (quét container image), tài liệu Kubernetes (Pod Lifecycle, Deployments, Debug Pods), tài liệu Docker (volumes, `COPY --chown`, multi-stage), README dự án distroless, twelve-factor (tiến trình không giữ trạng thái).
