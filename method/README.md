# method/ — luật chơi

> **Kết luận:** năm file dưới đây là nguồn chuẩn cho mọi skill, thẻ vai và mẫu trong repo; `AGENTS.md`
> là bản rút gọn nạp đầu phiên, khi khác nhau thì file ở đây thắng và `AGENTS.md` phải sửa theo.

| File | Trả lời | Đọc khi |
|---|---|---|
| [process.md](process.md) | 6 bước, 2 cổng người, cổng điều chỉnh nội bộ (`Phán quyết:`), 4 điều kiện dừng, vòng Thực thi ↔ Kiểm định (3 vòng khuyến nghị + lời báo chuẩn), việc rất nhỏ, bài học | mở sprint, phân vân có được hỏi người dùng không |
| [sizing.md](sizing.md) | 4 cỡ việc, bảng rủi ro → `risk_tags` → chuyên đề, sprint = một mục tiêu | tiếp nhận yêu cầu, thấy rủi ro mới |
| [severity.md](severity.md) | thang Chặn / Phải sửa / Nên sửa / Ghi chú, kết luận Đạt / Đạt có điều kiện / Không đạt, **bảng quy đổi duy nhất** từ 10 thang cũ | gán mức cho `RF`, distill nguồn có thang khác |
| [evidence.md](evidence.md) | một `VR` gồm gì, 4 kết quả, độ tươi, test hồi quy, câu "đỏ", xong ≠ phát hành ≠ nghiệm thu | ghi `VR`, kiểm PROGRESS/REPORT |
| [conventions.md](conventions.md) | coverage 80 %, đường dẫn mặc định và khoá `.agile.json`, ADR, luật git, frontmatter | cấu hình dự án, commit, viết ADR |

`standards/` dành cho chuẩn code chung và theo ngôn ngữ (đợt distill sau).
