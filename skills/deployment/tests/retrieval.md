---
skill: deployment
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 7821ed2b8db9eb24d7eb359c91c44f60fe95b268
date: 2026-10-03
result: pass 6/6 (rerun with a new question set after RF91-RF92; first run of the same day passed 6/6 on the earlier tree)
agent_ids:
  questions: a72b31dd351091fcf
  answers: a246a05b167de1156
---

Đã đọc: `<gốc worktree>\skills\deployment\SKILL.md` (kèm bốn file `references/`: `cicd-health-config.md`, `docker.md`, `docker-compose-dev.md`, `deployment-strategies.md`)

# Thử truy xuất — deployment

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥4/5 câu tình huống: 5/5; câu ranh giới Đạt) trên **bộ câu mới** và cây sau sửa RF91–RF92. Lượt
> đầu cùng ngày (6/6, `skill_sha` `0c0f87c992a2bcf7e684e6a6fc910e81a63aaf30`) chạy trước khi `references/cicd-health-config.md` được
> sửa (probe tách `/livez` ↔ `/readyz`, mẫu YAML thêm `deploy-staging` + `smoke`); file này ghi lượt chạy lại trên cây hiện tại.
> Chủ thể nêu đúng `/readyz`/`/livez` và việc tách readiness với liveness, tức đã đọc bản sau sửa.

Sáu câu hỏi do một agent mới **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực, được cho 6 chủ đề của bộ cũ để không lặp);
nguyên văn ở bảng dưới và ở `evidence/TK12-green/deployment-retrieval-rerun.md` trong hồ sơ sprint của lớp riêng, cùng output trọn của
chủ thể (dòng "Đã đọc" ở đó có đường tuyệt đối; ở đây lược thành `<gốc worktree>` vì repo chặn tên người dùng). Câu 6 là câu ranh giới:
đáp án của người soạn (`database-migrations`) đã được đối chiếu với `description` của skill đích ("altering tables, columns … writing a
data backfill … zero-downtime schema change") và nhận là đúng.

**Cách chấm, ghi thật:** cột "Mục kỳ vọng" **không** được ghi trước khi mở bài trả lời như khuôn quy định — báo cáo của chủ thể được
harness chuyển vào ngữ cảnh người chấm ngay khi xong. Mục kỳ vọng suy từ mục lục `SKILL.md` (bảng "Đọc thêm khi cần") và từ cột kỳ vọng
của bộ cũ cho cùng chủ đề, rồi đối chiếu tiêu đề thật trong các file `references/`; nên chấm lại độc lập khi kiểm định.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Dịch vụ `orders-api` có 3 replica, mỗi lần deploy vài giây người dùng nhận 502 vì pod cũ tắt trước khi pod mới sẵn sàng. Cấu hình readiness probe, `maxUnavailable` và thời gian chờ tắt thế nào để cập nhật không rớt request? | `SKILL.md` › 2 bước 3 + `references/cicd-health-config.md` › 4. Probe Kubernetes (+ `references/docker.md` › 1, tiến trình nhận `SIGTERM`) | `SKILL.md` › 2 bước 3; `cicd-health-config.md` › 4. Probe Kubernetes; `docker.md` › 1. Luật chính | Đạt |
| 2 | Release 2.14 lên production 10 phút thì 5xx nhảy từ 0,2% lên 6%. Quay về 2.13 hay sửa tiến? Trước release cần chuẩn bị gì để quay lui nhanh và an toàn, nhất là khi bản mới đã chạy migration đổi cột? | `SKILL.md` › 3, 4, 5 + `cicd-health-config.md` › 6. Lệnh hoàn tác tức thì (+ `database-migrations` cho phần migration) | `SKILL.md` › 3, 5, 4; `cicd-health-config.md` › 6; migration → `database-migrations` | Đạt |
| 3 | docker compose với `api`, `postgres`, `redis`; `docker compose up` thì `api` crash `connection refused` tới `postgres:5432` vì khởi động nhanh hơn database. Sửa khai báo thứ tự khởi động, healthcheck và `depends_on` thế nào? | `references/docker-compose-dev.md` › 1 + `docker.md` › 1 (phụ thuộc khởi động) và › 3 (`depends_on` không chờ healthcheck) | `docker-compose-dev.md` › 1. Stack web app chuẩn; `docker.md` › 1, 3 | Đạt |
| 4 | Pod `report-worker` ở `CrashLoopBackOff`, `kubectl logs` trống, container thoát gần như ngay. Chui vào xem gì và kiểm theo thứ tự nào để biết chết vì lệnh khởi động sai, thiếu file hay quyền? | `references/docker.md` › 2. Debug (+ `SKILL.md` › 7 → `debugging`) | `docker.md` › 2. Debug; `SKILL.md` › 7 → `debugging` | Đạt |
| 5 | Mai phát hành v3.0 cho ~40.000 người dùng, staging khác production ở vài biến môi trường. Trước giờ phát hành rà những gì (cấu hình, secret, theo dõi sau phát hành, người trực)? | `SKILL.md` › 8. Sẵn sàng production + `cicd-health-config.md` › 5. Cấu hình môi trường (+ › 3) | `SKILL.md` › 8, 3; `cicd-health-config.md` › 5. Cấu hình môi trường | Đạt |
| 6 | Migration chạy `ALTER TABLE orders ADD COLUMN ...` trên bảng 80 triệu dòng khi production đang chạy. Tách bước nào (cột nullable, backfill theo lô, rồi ràng buộc) để không khoá bảng? | mục khác: skill `database-migrations` | mục khác: `database-migrations` | Đạt |

## Thiếu nội dung / mâu thuẫn

- Không có mâu thuẫn trong các mục chủ thể đã đọc; hai mâu thuẫn của lượt trước (probe chung `/health`, mẫu YAML thiếu staging) không còn
  xuất hiện: chủ thể mô tả readiness `/readyz` riêng, liveness `/livez` riêng, startup probe.
- **Ghi chú.** Câu 1: skill không đưa giá trị hay cách chọn cho `maxUnavailable` và `terminationGracePeriodSeconds` (chủ thể nói hai
  số đó người dùng phải tự chọn); `SKILL.md` chỉ nêu rolling là mặc định và hai bản chạy song song.
- **Nên sửa (ngoài phạm vi lượt này).** Câu 4: `references/docker.md` › 2 viết cho Docker/Compose; không có đường `kubectl` cho
  `CrashLoopBackOff` (xem log lần chạy trước, mô tả pod, container tạm để chui vào container thoát ngay) nên chủ thể chuyển sang
  `debugging`. Đề xuất cho điều phối quyết có thêm mục ngắn hay không; không đổi mục lục/tiêu đề vì truy xuất đã Đạt.
- Chủ đề `description` còn lại đều có mục trả lời.
