---
skill: deployment
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 238d01b8e615f03c7788533ce1343ec421d38f99
date: 2026-10-03
result: below threshold (3/5 situations pass, 2 partial, 0 fail; boundary pass)
agent_ids:
  questions: a50baf20beb2035c3
  answers: aa6e83831c0278ece
---

Đã đọc: `<gốc worktree>\skills\deployment\SKILL.md` (và các file trong `references/` mà `SKILL.md` trỏ tới, nếu có)

# Thử truy xuất — deployment

> **Kết luận:** dưới ngưỡng ≥4/5 câu tình huống Đạt: 3/5 Đạt (câu 1, 4, 5), 2/5 Một phần (câu 2, 3), 0 Không đạt; câu ranh giới (câu 6) chủ thể trỏ đúng `api-design`. Chủ thể đọc `SKILL.md` và năm file `references/`,
> trỏ đúng nơi ở mọi câu, gắn nhãn suy luận của mình và nói thẳng phần skill không có (scan Trivy, chỉnh ownership thư mục ghi cho `USER` không root, session trong memory khi cutover blue-green, so sánh slim/alpine/distroless,
> `terminationGracePeriodSeconds`) thay vì bịa. Con trỏ `deployment-strategies.md` › 3 → `SKILL.md` › 4 đã đúng sau sửa.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực, kèm danh sách chủ đề của các bộ cũ để không lặp); lượt này là **bộ câu mới** chạy lại sau commit `6e57dc5` (sửa con trỏ mục).
Cột "Mục kỳ vọng" do người chấm ghi vào file nháp **trước khi** giao chủ thể (mtime file nháp 2026-10-03 21:54:53 +0700 (21:54:53,45), sớm hơn lệnh giao chủ thể); mục kỳ vọng ghi theo cây hiện tại.
Câu 6 là câu ranh giới, đáp án do người soạn nêu và người chấm đối chiếu với `description` của skill đáp.
Nguyên văn câu hỏi của người soạn, file nháp kỳ vọng, output TRỌN của chủ thể (đường dẫn thư mục người dùng giữ nguyên ở đó, còn ở đây lược thành `<gốc worktree>` vì repo chặn tên người dùng)
và số lượt công cụ: hồ sơ sprint của lớp riêng, `evidence/TK12-green/deployment-retrieval-rerun-3.md`.

Cách chấm: **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính;
**Không đạt** = trỏ sai hoặc bịa. Ngưỡng: ≥4/5 câu tình huống Đạt và câu ranh giới Đạt. `result` ghi cả số "một phần".

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Chuyển từ docker-compose trên một VM sang production thật; CI pipeline có bước scan image bằng Trivy, tag image theo git SHA thay vì `latest`, push lên registry. Thiết kế stage và quy ước tag/promote từ staging lên prod thế nào cho gọn và truy vết được? | `references/cicd-health-config.md` › 1 GitHub Actions, › 2 Các chặng pipeline (tag `github.sha`, promote đúng image, không build lại); `SKILL.md` › 2.2; scan Trivy không có | `SKILL.md` › 2, › 4, › 5, › 8; `cicd-health-config.md` › 1, › 2; `dockerfiles.md` › 4; `docker.md` › 3 | Đạt (thứ tự chặng, tag `github.sha`, promote đúng image không build lại, truy vết bằng tag bất biến; không có bước scan Trivy, ngưỡng CVE) |
| 2 | Container chạy được trên dev nhưng lên server crash lúc khởi động vì ghi file vào `/app/uploads`, permission denied sau khi đổi sang `USER node`. Sửa ownership, dùng volume, hay đổi cách lưu file? | `references/dockerfiles.md` › 1 (`--chown`), `docker-network-volume-security.md` › 2 Volume, › 3 non-root; `SKILL.md` › 6; chọn chown/volume cho thư mục ghi chỉ gián tiếp | `docker.md` › 2, › 3; `dockerfiles.md` › 1; `docker-network-volume-security.md` › 3; `SKILL.md` › 6 | Một phần (không lùi về root, `--chown` cho file trong image, volume có tên, tmpfs cho `read_only`; không có quyết định chính: chỉnh ownership thư mục mount/volume cho `USER` không root, hay lưu file ngoài container) |
| 3 | Blue-green cho API có session lưu trong memory từng instance, lo user văng đăng nhập lúc cutover. Cần chuẩn bị gì trước khi switch traffic, giữ đường quay lại bản blue vài giờ đầu thế nào? | `SKILL.md` › 1, › 5; `references/deployment-strategies.md` › 2 Blue-green; session sticky/đưa ra ngoài không có | `SKILL.md` › 1, › 3, › 4, › 5; `deployment-strategies.md` › 2 | Một phần (blue idle làm đường quay về tức thì, điều kiện huỷ đo được, danh mục hoàn tác, schema hợp cả hai bản; không có nỗi lo chính: session trong memory khi cutover; không có thời gian giữ blue) |
| 4 | Dockerfile một stage, cài cả compiler lẫn devDependencies rồi build, image nặng nhiều CVE từ build tools. Tách multi-stage thế nào, chọn base image runtime nào (slim, alpine, distroless)? | `references/dockerfiles.md` › 1-3, › 4 Nên và không nên; `docker.md` › 1; so sánh slim/alpine/distroless không có | `dockerfiles.md` › 1, › 4; `docker.md` › 1; `docker-network-volume-security.md` › 4 | Đạt (tách `deps`/`builder`/`runner`, bỏ phụ thuộc dev, thứ tự lớp, ghim phiên bản; không có so sánh slim/alpine/distroless, không có distroless) |
| 5 | Service khởi động ~90 giây (warm cache, load model) nên Kubernetes kill pod trước khi sẵn sàng. Cấu hình `startupProbe`, `readinessProbe`, `livenessProbe` ra sao, đặt `terminationGracePeriodSeconds` thế nào để tắt pod không rớt request? | `references/cicd-health-config.md` › 4 Probe Kubernetes; `SKILL.md` › 2.3; `docker.md` › 1 (`SIGTERM`, tắt êm); `terminationGracePeriodSeconds` có thể không có | `SKILL.md` › 2; `cicd-health-config.md` › 3, › 4; `docker.md` › 1, › 2 | Đạt (bộ ba probe, mẫu `startupProbe` tối đa 150 s bao được 90 s, tắt êm bằng `SIGTERM`; không có `terminationGracePeriodSeconds`, `preStop`) |
| 6 | `GET /orders` trả cả nghìn bản ghi một response, mobile chậm; thêm pagination cursor, giữ tương thích app cũ không truyền tham số. Thiết kế query params, response envelope, versioning thế nào? | mục khác: skill `api-design` | mục khác: `api-design` (từ danh mục skill; chủ thể ghi chưa mở skill đó) | Đạt (ranh giới) |

## Thiếu nội dung / mâu thuẫn

- **Thiếu nội dung (câu 1).** Bước scan image (Trivy) và ngưỡng CVE làm fail pipeline.
- **Thiếu nội dung (câu 2).** Cấp quyền thư mục ghi (`/app/uploads`) cho `USER` không root; chọn giữa chỉnh ownership volume và lưu file ngoài container.
- **Thiếu nội dung (câu 3).** Xử lý session lưu trong memory khi cutover blue-green (sticky hoặc đưa session ra ngoài); thời gian giữ bản blue.
- **Thiếu nội dung (câu 4).** So sánh slim/alpine/distroless để chọn base image runtime.
- **Thiếu nội dung (câu 5).** `terminationGracePeriodSeconds`, `preStop`, thứ tự rút khỏi cân bằng tải so với `SIGTERM`.
- Theo brief `X4` không sửa tiếp: mở rộng nội dung các mục trên thuộc sprint nội dung mới, điều phối ghi `CO`.
- Không có mâu thuẫn giữa các file chủ thể đọc; con trỏ chéo lệch số mục của lượt trước đã sửa.
