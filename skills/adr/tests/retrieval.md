---
skill: adr
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: b08afe82222042ab4d85e0151a95820df85c7b7f
date: 2026-10-03
result: pass 6/6
---

Đã đọc: `<gốc worktree>\skills\adr\SKILL.md`

# Thử truy xuất — adr

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥5/6). Chủ thể trỏ đúng mục ở cả năm câu tình huống và nhận ra câu ranh giới
> thuộc `plan-review`. Một chỗ skill chưa nói: khuôn "Hệ quả" không có chỗ ghi cách quay lại khi bỏ một công nghệ.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Skill chỉ có `SKILL.md`, không có
`references/`. Câu 6 là câu ranh giới: đáp án của người soạn (`plan-review`) đã được người chấm đối chiếu với
`description` của skill đích (review PLAN nháp trước Cổng 1) và nhận là đúng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Team đang chọn giữa PostgreSQL và MongoDB cho dịch vụ đơn hàng mới, và đổi ý sau 6 tháng sẽ rất tốn kém. Quyết định này cần được ghi lại những gì để người sau hiểu vì sao chọn? | `SKILL.md` › 4. Khuôn (+ 2. Đầu vào) | `SKILL.md` › 2. Đầu vào, 4. Khuôn; lý do cần ADR ở 1. Khi nào | Đạt |
| 2 | Sprint cỡ lớn có thiết kế cho billing-service gọi trực tiếp inventory-service thay vì qua queue, và reviewer đòi hồ sơ quyết định. Cần ghi những phương án và hệ quả nào? | `SKILL.md` › 4. Khuôn › Lựa chọn đã cân nhắc, Hệ quả (+ 2. Đầu vào) | `SKILL.md` › 4. Khuôn › Lựa chọn đã cân nhắc, Hệ quả; 1. Khi nào | Đạt |
| 3 | Quyết định dùng RabbitMQ đã được chấp nhận từ năm ngoái, giờ nhóm muốn chuyển sang Kafka. Quyết định cũ xử lý thế nào, trạng thái nào đổi? | `SKILL.md` › 3. Các bước › bước 6 Thay thế | `SKILL.md` › 3. Các bước, bước 6; 5. Điểm dừng | Đạt |
| 4 | Dự án định đổi mô hình đăng nhập từ session cookie sang OIDC qua Keycloak, ảnh hưởng cả web lẫn mobile. Tình huống này có đáng lập hồ sơ quyết định không, và cần so sánh những phương án nào? | `SKILL.md` › 1. Khi nào (+ 2. Đầu vào: ít nhất hai lựa chọn) | `SKILL.md` › 1. Khi nào; 5. Điểm dừng (đọc qua bảo mật) | Đạt |
| 5 | Có đề xuất bỏ hẳn Redis khỏi stack vì chỉ còn cache vài màn hình. Bỏ một công nghệ thì cần ghi lại điều gì về hệ quả và cách quay lại? | `SKILL.md` › 1. Khi nào + 4. Khuôn › Hệ quả | `SKILL.md` › 1. Khi nào, 4. Khuôn › Hệ quả, 5. Điểm dừng | Đạt (một phần: không có chỗ ghi cách quay lại) |
| 6 | PLAN của sprint vừa viết xong, Tech Reviewer cần soát trước khi trình Cổng 1. Soát theo những tiêu chí nào? | mục khác: skill `plan-review` | mục khác: `plan-review` (từ `SKILL.md` › 3. Các bước, bước 4) | Đạt |

## Thiếu nội dung / mâu thuẫn

- `skills/adr/SKILL.md:82-87` (khuôn mục "Hệ quả"): có "Dễ hơn / Khó hơn / Từ nay cố định / Việc kéo theo" nhưng không có chỗ cho cách quay
  lại hay lối thoát khi quyết định là bỏ công nghệ hoặc gỡ dịch vụ (câu 5). Đề xuất: thêm dòng "Cách quay lại: <viết ADR thay thế
  nào, mất gì khi quay lại>" vào khuôn, hoặc nêu thẳng "quay lại = ADR mới thay thế" ở bước 6 mục 3.
- Không có chỗ nào `description` hứa mà thân skill không có.
