# Fixture autopilot (SPR-12 TK3)

- `legacy-delegation/`: bản chép nguyên văn năm file `.md` của hồ sơ duyệt thay thật
  `agent-skill-studio/plans/2026-10-27-one-source-1b` (workshop-records; không chép `evidence/`). Chỉ có tám khoá
  `delegation` cũ -> luật autopilot không kích, kết quả `check` phải y hệt trước (FR1.13, ca tương thích).
- Để ngoài `tests/fixtures/valid/` vì test mẫu hợp lệ quét cả thư mục đó.
- Đã thay một từ trong danh sách cấm rò rỉ của repo bằng "đối tác" ở 8 dòng (cổng `leak-denylist` quét cả fixture); không đổi khối `delegation`.
