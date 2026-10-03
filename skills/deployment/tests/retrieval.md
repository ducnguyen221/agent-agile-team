---
skill: deployment
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 0c0f87c992a2bcf7e684e6a6fc910e81a63aaf30
date: 2026-10-03
result: pass 6/6
---

Đã đọc: `<gốc worktree>\skills\deployment\SKILL.md`

# Thử truy xuất — deployment

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥5/6). Truy xuất đúng ở cả năm câu tình huống và câu ranh giới (`web-qa`).
> Việc đọc lại cho thấy hai chỗ trong `references/cicd-health-config.md` trái với `SKILL.md`: mẫu probe dùng một
> endpoint `/health` cho cả liveness lẫn readiness, và mẫu GitHub Actions không có chặng staging.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Câu 6 là câu ranh giới: đáp án của
người soạn (`web-qa`) đã được người chấm đối chiếu với `description` của skill đích (kiểm một web app trong trình
duyệt thật, có ảnh chụp) và nhận là đúng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Dockerfile của service Node hiện build ra image 1,8 GB và chạy bằng root. Nên sửa theo hướng nào để nhỏ và an toàn hơn? | `references/dockerfiles.md` (+ `SKILL.md` › 2 bước 1, `references/docker.md` › 1) | `references/dockerfiles.md` › 1. Node.js, 4. Nên và không nên; `SKILL.md` › 2 bước 1 | Đạt |
| 2 | Pod `api` bị Kubernetes restart liên tục vì liveness probe gọi `/health` quá sớm khi app còn đang kết nối DB. Probe nên cấu hình ra sao? | `SKILL.md` › 2 bước 3 + `references/cicd-health-config.md` › 4. Probe Kubernetes | `SKILL.md` › 2 bước 3; `references/cicd-health-config.md` › 4. Probe Kubernetes; `SKILL.md` › 6 | Đạt |
| 3 | Sắp phát hành bản mới cho dịch vụ thanh toán, muốn giảm rủi ro. Chọn rolling, blue-green hay canary, và chuẩn bị đường rollback thế nào? | `SKILL.md` › 1. Chọn chiến lược (+ 5. Danh mục hoàn tác, `references/deployment-strategies.md`) | `SKILL.md` › 1, 3, 5, 4; `references/deployment-strategies.md` | Đạt |
| 4 | Pipeline CI/CD trên GitHub Actions cần build, test, rồi deploy staging tự động. Pipeline nên chia giai đoạn và gác cổng thế nào? | `references/cicd-health-config.md` › 1, 2 (+ `SKILL.md` › 2 bước 2) | `references/cicd-health-config.md` › 2. Các chặng pipeline, 1. GitHub Actions; `SKILL.md` › 2 bước 2 | Đạt |
| 5 | Container `worker` thoát với exit code 137 trên staging và biến môi trường `DATABASE_URL` có thể đang thiếu. Kiểm tra cấu hình môi trường và gỡ lỗi container theo thứ tự nào? | `references/docker.md` › 2. Debug (+ `references/cicd-health-config.md` › 5, `SKILL.md` › 2 bước 4) | `references/docker.md` › 2. Debug; `references/cicd-health-config.md` › 5. Cấu hình môi trường; `SKILL.md` › 2 bước 4 | Đạt |
| 6 | Bản deploy staging xong, cần chạy thử luồng đăng nhập rồi checkout trên trình duyệt thật và chụp bằng chứng. Dùng quy trình nào? | mục khác: skill `web-qa` | mục khác: `web-qa` | Đạt |

## Thiếu nội dung / mâu thuẫn

- **Mâu thuẫn, mức Phải sửa.** `skills/deployment/references/cicd-health-config.md:123-143` (mục 4): liveness (dòng 125), readiness (133) và startup (141)
  đều trỏ `path: /health`. Mục 3 của cùng tệp (dòng 84-87) định nghĩa `/health` là bản đơn giản trả 200 cố định, không kiểm phụ thuộc. Hậu
  quả: readiness không kiểm phụ thuộc, trái `SKILL.md:48` ("readiness … được kiểm phụ thuộc thiết yếu") và rơi đúng dòng `SKILL.md:95`
  (`/health` luôn 200); liveness và readiness chung một endpoint, trái `SKILL.md:45` ("đừng dồn vào một endpoint"). Đề xuất: liveness `/health`,
  readiness một endpoint kiểm phụ thuộc thiết yếu (ví dụ `/ready`), có chú thích vì sao khác nhau.
- **Mâu thuẫn, mức Nên sửa.** `skills/deployment/references/cicd-health-config.md:18-67` (mẫu YAML) chỉ có job `test`, `build`, `deploy` (môi trường
  `production`); không có job staging và smoke test, trong khi dòng 3-5 của cùng tệp, mục 2 (dòng 71-79) và `SKILL.md:43-44` đều nói "deploy staging →
  smoke test → production, production nhận đúng image đã qua staging". Đề xuất: thêm job `deploy-staging` + `smoke` trước `deploy`, hoặc ghi
  chú YAML là rút gọn.
- Chủ đề `description` đều có mục trả lời; không có chỗ nào thiếu nội dung.
- Kết quả đo ở `skill_sha` cũ `0c0f87c992a2bcf7e684e6a6fc910e81a63aaf30`; sửa RF91–RF92 (`references/cicd-health-config.md`: probe tách `/livez` ↔ `/readyz`, YAML thêm `deploy-staging` + `smoke`) sau đó, chạy lại ở `TK12`.
