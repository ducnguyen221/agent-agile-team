---
skill: adr
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 6ec980f797a9be9573d5c53b58b1df879b2b494c
date: 2026-10-03
result: pass 6/6 (rerun with a new question set after the description was shortened from 490 to 396 characters)
agent_ids:
  questions: a9241d4672a5a250a
  answers: a6bbb3b62fb8db542
---

Đã đọc: `<gốc worktree>\skills\adr\SKILL.md`

# Thử truy xuất — adr

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥4/5 câu tình huống + câu ranh giới). Chủ thể trỏ đúng mục ở cả năm câu tình huống
> và nhận ra câu ranh giới thuộc `api-design`. Chạy lại vì `description` đổi (490 -> 396 ký tự) làm lệch `skill_sha`;
> bộ câu mới, người soạn và chủ thể đều là agent mới.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` mới và lĩnh vực); nguyên văn, bài trả lời
trọn của chủ thể và file nháp "Mục kỳ vọng" ở `evidence/TK12-green/adr-retrieval-rerun.md` trong hồ sơ sprint của lớp
riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường
dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp
**trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng -> giao chủ thể -> chấm). Skill chỉ có `SKILL.md`, không có
`references/`. Câu 6 là câu ranh giới: đáp án của người soạn (`api-design`) đã được đối chiếu với `description` của
skill đích (thiết kế hoặc đổi một endpoint REST, phân trang, mã lỗi) và nhận là đúng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Nhóm đang cân nhắc đổi nền tảng chạy ứng dụng từ vài máy ảo tự quản sang Google Cloud Run; việc này ràng buộc cách build, mạng và chi phí về sau. Cần ghi lại những gì (bối cảnh, phương án đã loại, hệ quả)? | `SKILL.md` › 4. Khuôn (+ 1. Khi nào) | `SKILL.md` › 4. Khuôn, kèm 1. Khi nào và 2. Đầu vào | Đạt |
| 2 | Tách cột địa chỉ của bảng `customers` thành thực thể `addresses` riêng; mô hình dữ liệu được ba dịch vụ khác dùng chung nên rất khó quay lại. Trước khi chốt thiết kế, ghi quyết định này ra sao? | `SKILL.md` › 1. Khi nào + 4. Khuôn | `SKILL.md` › 1. Khi nào, rồi 4. Khuôn | Đạt |
| 3 | Dự án cổng thông tin cỡ lớn sắp bắt đầu, chọn React hay Vue; người duyệt kế hoạch đòi tài liệu ghi lý do chọn framework. Nên ghi những mục nào? | `SKILL.md` › 1. Khi nào + 4. Khuôn | `SKILL.md` › 2. Đầu vào và 4. Khuôn (dẫn dữ kiện mục 1) | Đạt |
| 4 | Ba tháng trước đã chốt dùng một ORM nặng cho toàn bộ backend; nay muốn bỏ để viết SQL thuần. Quyết định cũ đã duyệt thì xử lý hồ sơ thế nào khi lật lại? | `SKILL.md` › 3. Các bước › bước 6 Thay thế | `SKILL.md` › 3. Các bước (bước 6) và 5. Điểm dừng | Đạt |
| 5 | Thay cổng thanh toán tích hợp trực tiếp bằng nhà cung cấp mới, kéo theo đổi hợp đồng webhook bốn đội đang nghe; reviewer hỏi đã cân nhắc những lựa chọn nào. Chuẩn bị phần ghi lại thế nào? | `SKILL.md` › 4. Khuôn › Lựa chọn đã cân nhắc (+ 2. Đầu vào) | `SKILL.md` › 4. Khuôn › Lựa chọn đã cân nhắc và 5. Điểm dừng | Đạt |
| 6 | Đổi `GET /orders` sang phân trang con trỏ kèm lọc theo trạng thái, khoảng ngày và định dạng lỗi thống nhất; đặt tên tham số, mã HTTP, cấu trúc phản hồi ra sao để client không vỡ? | mục khác: skill `api-design` | mục khác: `api-design` (từ `SKILL.md` › 1. Khi nào) | Đạt |

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hứa mà thân skill không có.
- Chỗ thiếu đã biết từ lượt trước vẫn còn, bộ câu mới không chạm tới: `skills/adr/SKILL.md:82-87` (khuôn mục "Hệ quả") không có chỗ
  ghi cách quay lại khi quyết định là bỏ công nghệ hay gỡ dịch vụ.
