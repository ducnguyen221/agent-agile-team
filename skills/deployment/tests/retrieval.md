---
skill: deployment
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 6b0cf6003eb87163121978994d2917c3fec71559
date: 2026-10-03
result: pass 6/6, 3 partial
agent_ids:
  questions: a08b0b716bc5c8aad
  answers: ad5c49b16bee844f7
---

Đã đọc: `<gốc worktree>\skills\deployment\SKILL.md` (và các file trong `references/` mà `SKILL.md` trỏ tới, nếu có)

# Thử truy xuất — deployment

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥4/5 câu tình huống và câu ranh giới), trong đó 3 câu chỉ Đạt một phần (câu 1, 4, 5). Chủ thể đọc `SKILL.md` và sáu file `references/`, nói thẳng phần skill không có
> (`.venv` và hot reload Python, cách tổ chức cấu hình theo môi trường, công cụ tự động hoá canary, lệnh `gh run`) thay vì bịa; câu ranh giới trỏ đúng `github-ops`. Phát hiện thêm ngoài ngưỡng: một con trỏ chéo lệch số mục
> trong `references/deployment-strategies.md` (xem cuối).

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực, kèm danh sách chủ đề của bộ cũ để không lặp); lượt này là **bộ câu mới** chạy lại sau khi `X2` đổi nội dung skill
(chạy lại theo giao thức rerun-2). Cột "Mục kỳ vọng" do người chấm ghi vào file nháp **trước khi** giao chủ thể (mtime file nháp 2026-10-03 21:40:39 +0700 (21:40:39,75), sớm hơn lệnh giao chủ thể đầu tiên); mục kỳ vọng ghi theo cây MỚI.
Câu 6 là câu ranh giới, đáp án do người soạn nêu và người chấm đối chiếu với `description` của skill đáp.
Nguyên văn câu hỏi của người soạn, file nháp kỳ vọng, output TRỌN của chủ thể (đường dẫn thư mục người dùng giữ nguyên ở đó, còn ở đây lược thành `<gốc worktree>` vì repo chặn tên người dùng)
và số lượt công cụ: hồ sơ sprint của lớp riêng, `evidence/TK12-green/deployment-retrieval-rerun-2.md`.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần chi tiết phụ còn thiếu ghi trong ngoặc và ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được.
Ngưỡng: ≥4/5 câu tình huống Đạt và câu ranh giới Đạt. `result` ghi cả số "một phần".

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Compose dev cho API FastAPI hot reload: bind-mount `./src`, nhưng `node_modules` và `.venv` trên host đè lên bản trong image. Cấu hình volume và override giữa compose dev và prod thế nào? | `references/docker-compose-dev.md` › 1 (volume ẩn danh `/app/node_modules`) + › 3. File override; `.venv` không nói trực tiếp | `references/docker-compose-dev.md` › 1. Stack web app chuẩn, › 3. File override; `docker-network-volume-security.md` › 2; `docker.md` › 1 | Đạt (một phần: mẫu volume ẩn danh và override dev/prod đủ; chỉ ví dụ Node, không `.venv`, không `uvicorn --reload`, mẫu mount `.:/app` chứ không `./src` — chủ thể ghi là suy ra) |
| 2 | Mỗi lần sửa một dòng, `docker build` cài lại toàn bộ dependency ~6 phút trên CI; Dockerfile `COPY . .` rồi `pip install -r requirements.txt`. Sắp xếp lại thứ tự lệnh và dùng cache layer ra sao? | `references/dockerfiles.md` › 1 (Node: manifest trước, `COPY . .` sau), › 3. Python/Django, › 4. Nên và không nên; `SKILL.md` › 2.1 | `references/dockerfiles.md` › 3, › 4; `docker.md` › 1, › 3; `cicd-health-config.md` › 1 (cache buildx `type=gha`) | Đạt |
| 3 | Image lẫn `.git`, `.env`, `tests/`, context 900 MB, chưa có `.dockerignore`. Loại những gì, có rủi ro lộ secret nào cần xử lý? | `references/docker-network-volume-security.md` › 4. `.dockerignore` + › 3. Bảo mật container (secret trong lớp image) | `docker-network-volume-security.md` › 4, › 3; `dockerfiles.md` › 4; `docker.md` › 3; `SKILL.md` › 6 | Đạt (chủ thể ghi mẫu `.dockerignore` thiên về Node, không có `.venv`/`__pycache__`) |
| 4 | Ba môi trường dev/staging/prod với URL database, feature flag, khoá API khác nhau; hiện sửa tay `.env` từng server, từng deploy prod nhầm cấu hình staging. Tổ chức và kiểm tra cấu hình thế nào để không lặp lại? | `references/cicd-health-config.md` › 5. Cấu hình môi trường (biến môi trường, kiểm schema lúc khởi động, sai thì dừng) + `SKILL.md` › 2.4; cách tổ chức file cấu hình theo môi trường không có | `cicd-health-config.md` › 5, › 1; `SKILL.md` › 2, › 8 | Đạt (một phần: có kiểm schema lúc khởi động, `APP_ENV`, secret manager, cùng image qua staging; không có cách tổ chức cấu hình theo môi trường, bỏ sửa tay `.env`, kiểm chéo URL với `APP_ENV`) |
| 5 | Canary 10% cho dịch vụ đơn hàng, hiện ngồi nhìn dashboard tự tăng 50% hoặc rollback. Muốn tự tăng dần và tự dừng khi lỗi hoặc p95 vượt ngưỡng: đặt tiêu chí và quy trình thế nào? | `SKILL.md` › 3. Trước, trong và sau khi bật lưu lượng + › 1 (Canary) + `deployment-strategies.md` › 3; công cụ tự động hoá không có; › 4: mỗi bước tăng canary production cần người gật | `SKILL.md` › 3, › 4, › 1, › 5; `references/deployment-strategies.md` › 3. Canary | Đạt (một phần: có khung điều kiện huỷ đo được, quan sát mỗi nấc, hoàn tác, và giới hạn quyền; không có ngưỡng số, cỡ nấc, công cụ tự động hoá) |
| 6 | Workflow GitHub Actions chạy 2 giờ sáng đỏ ở bước "Run tests". Dùng `gh` xem lại run, tải log job lỗi, re-run chỉ job fail. Lệnh `gh run` nào? | mục khác: skill `github-ops` | mục khác: `github-ops` (từ `cicd-health-config.md` › 1 và `SKILL.md` › 7 "Liên quan") | Đạt (ranh giới) |

## Thiếu nội dung / mâu thuẫn

- **Lệch tham chiếu (không đổi kết quả).** `skills/deployment/references/deployment-strategies.md` mục 3 (Canary), dòng cuối: "theo điều kiện dừng ở SKILL mục 3". Tiêu đề "Điều kiện dừng" của `SKILL.md` là **mục 4**
  (mục 3 là "Trước, trong và sau khi bật lưu lượng"); nội dung liên quan có ở cả hai mục. Đề xuất: đổi thành "mục 3 và 4" hoặc "mục 4".
- **Thiếu nội dung, nhẹ.** Không có ví dụ Python cho volume ẩn danh (`.venv`) và hot reload (câu 1); cách tổ chức cấu hình theo môi trường và chống nhầm staging/prod ngoài kiểm schema lúc khởi động (câu 4);
  công cụ hoặc cấu hình tự động hoá canary (câu 5). Không phải lỗ hổng so với `description`: skill nói rõ đây là khung quyết định chứ không phải hướng dẫn công cụ.
- Không có mâu thuẫn nào khác giữa `SKILL.md` và sáu file `references/` chủ thể đọc.
