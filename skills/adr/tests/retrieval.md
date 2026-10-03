---
skill: adr
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 25741ba60d2baa3c35fd65200288b574c839df4b
date: 2026-10-04
result: "strict 6/6 (+0 partial, 0 fail) — at threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 6/6"
agent_ids:
  questions: a46877d5dc8954614
  answers: afe455f6f76053bc6
---

Đã đọc: `<gốc worktree>\skills\adr\SKILL.md`

# Thử truy xuất — adr

> **Kết luận:** strict 6/6 (+0 partial, 0 fail), points-right 6/6: đạt ngưỡng (5/5 câu tình huống Đạt; câu ranh giới Đạt). Chủ thể trỏ đúng mục ở cả năm câu tình huống
> và nhận ra câu ranh giới thuộc `deployment`. Chạy lại vì `source:` của `SKILL.md` đổi (gỡ lời khẳng định phòng sạch, quyết định `DN6`) làm lệch `skill_sha`; `description` không đổi.
> Bộ câu mới, người soạn và chủ thể đều là agent mới.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description`, lĩnh vực, tên các skill khác và cột câu hỏi của bộ cũ để không lặp); nguyên văn câu hỏi, file nháp "Mục mong đợi" (mtime `2026-10-04 00:27:43 +0700`),
bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/adr-retrieval-rerun-after-dn6.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường
dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp
**trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng -> giao chủ thể -> chấm). Skill chỉ có `SKILL.md`, không có
`references/`. Câu 6 là câu ranh giới: đáp án của người soạn (`deployment`) đã được đối chiếu với `description` của
skill đích (Dockerfile, health check, chiến lược triển khai) và nhận là đúng.

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Đội phân tích dữ liệu đang chọn giữa lưu toàn bộ sự kiện hành vi người dùng trong kho dạng cột (ClickHouse) hay tiếp tục dồn vào PostgreSQL hiện có. Việc di dời sau này sẽ rất đắt vì mọi pipeline báo cáo đều đọc từ đó. Quyết định này có đáng được ghi lại thành hồ sơ riêng không, và nếu có thì gồm những gì? | `SKILL.md` › 1. Khi nào (hàng nơi lưu dữ liệu + phép thử nhanh) rồi › 4. Khuôn | `SKILL.md` › 1. Khi nào, › 2. Đầu vào, › 4. Khuôn | Đạt |
| 2 | Tuần trước nhóm đã duyệt và ghi lại quyết định để các dịch vụ gọi nhau qua hàng đợi tin nhắn (message broker). Giờ đo thực tế cho thấy độ trễ không chấp nhận được, nên cả nhóm muốn quay lại gọi đồng bộ trực tiếp giữa các dịch vụ. Hồ sơ của quyết định cũ nên xử lý thế nào, và hồ sơ mới cần liên kết với nó ra sao? | `SKILL.md` › 3. Các bước › bước 6 Thay thế (+ › 5. Điểm dừng dòng sửa ADR đã accepted, › 4. Khuôn dòng Thay thế) | `SKILL.md` › 3. Các bước (bước 1, 6), › 4. Khuôn, › 5. Điểm dừng | Đạt |
| 3 | Mình vừa nhận một repo mà người tiền nhiệm bảo "đã có tài liệu ghi lại các quyết định lớn". Mình cần soát xem mấy tài liệu đó đã đủ chuẩn chưa: có nêu rõ lý do chọn, các phương án đã loại và hệ quả chưa. Khuôn mẫu chuẩn của một hồ sơ như vậy có những mục nào, và nên đối chiếu theo tiêu chí gì? | `SKILL.md` › 4. Khuôn + › 2. Đầu vào (+ › 5. Điểm dừng dòng chỉ một lựa chọn thật) | `SKILL.md` › 4. Khuôn, › 2. Đầu vào, › 3. Các bước (bước 3, 6), › 5. Điểm dừng | Đạt |
| 4 | Anh trưởng nhóm bảo sắp chuyển cách đăng nhập từ phiên làm việc lưu ở máy chủ sang token tự chứa (JWT) cho cả ứng dụng web lẫn di động. Việc này đụng tới nhiều dịch vụ và khó rút lại nếu client đã phát hành rộng. Trước khi viết dòng code đầu tiên, mình nên làm gì với quyết định này? | `SKILL.md` › 1. Khi nào (hàng cách xác thực) + › 3. Các bước (proposed → accepted ở Cổng 1) + › 5. Điểm dừng (an ninh → `security-review`) | `SKILL.md` › 1. Khi nào, › 3. Các bước (bước 4, 5), › 5. Điểm dừng | Đạt |
| 5 | Mình định đổi tên biến `usr_cnt` thành `user_count` trong một hàm tiện ích nội bộ, và đổi màu nút "Lưu" từ xanh lá sang xanh dương trên một trang. Hai thay đổi này có cần lập hồ sơ quyết định kiến trúc không, hay bỏ qua cho nhẹ việc? | `SKILL.md` › 1. Khi nào, cột Không viết ADR (refactor → `TK`; lựa chọn dễ đổi lại → dòng `Phán quyết:`) | `SKILL.md` › 1. Khi nào (cột phải của bảng + phép thử nhanh) | Đạt |
| 6 | Ứng dụng đang chạy trên Cloud Run, mình cần viết Dockerfile nhiều giai đoạn, thêm kiểm tra sức khỏe (health check) và chọn chiến lược triển khai dần (canary) cho bản phát hành tuần này. Nền tảng đã chốt từ trước, giờ chỉ là việc đóng gói và phát hành an toàn. Nên bắt đầu từ đâu và cần chú ý gì? | mục khác: skill `deployment` (đóng gói và phát hành; nền tảng đã chốt nên không có ADR mới) | mục khác: `deployment` (chủ thể nhận câu không thuộc `adr`; `SKILL.md` › 1. Khi nào: nền tảng đã chốt nên không cần ADR mới) | Đạt |

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hứa mà thân skill không có.
- Chỗ thiếu đã biết từ các lượt trước vẫn còn: `skills/adr/SKILL.md:82-87` (khuôn mục "Hệ quả") không có chỗ ghi cách quay lại khi quyết định là bỏ công nghệ hay gỡ dịch vụ. Lượt này chủ thể nêu thêm hai chỗ phụ: không nói cách xử lý code hay hạ tầng đã triển khai theo quyết định cũ khi ADR bị thay thế (câu 2), và không có danh mục soát tài liệu ADR có sẵn riêng (câu 3, tiêu chí do chủ thể suy ra từ khuôn và điểm dừng).
