# method/ — luật chơi

> **Kết luận:** các file dưới đây và thư mục `standards/` là nguồn chuẩn cho mọi skill, thẻ vai và mẫu trong repo; `AGENTS.md`
> là bản rút gọn nạp đầu phiên, khi khác nhau thì file ở đây thắng và `AGENTS.md` phải sửa theo.

| File | Trả lời | Đọc khi |
|---|---|---|
| [task-routing.md](task-routing.md) | Sáu trục, độ khó/effort, field override, topology, ba repair cycles, notice và pilot chưa promoted | Phân công có routing, đổi criteria/model/effort hoặc bàn giao sau sửa |
| [effort-scale.md](effort-scale.md) | Thang effort 1–5, nhãn từng vendor, độ khó 1–5, công thức max(sàn vai, độ khó), hạ theo `fallback` | giao việc, ghi effort vào PROGRESS, đọc bảng tier schema 2 |
| [process.md](process.md) | 6 bước, 2 cổng người, lượt trao đổi tiếp nhận, phán quyết nội bộ, điều kiện dừng, ba repair cycles có oracle và handoff, thiết kế vòng lặp (mục 6.1), việc nhẹ một file, ghi sổ và bài học | mở sprint, phân vân quyền/handoff, giao agent chạy lặp, ghi sổ tập trung |
| [sizing.md](sizing.md) | bậc làm thẳng (không sprint) + 4 cỡ việc (bảng dấu hiệu đo được → số file → kiểm định → cổng; việc đơn giản đi đường nhẹ), bảng rủi ro → `risk_tags` → chuyên đề, sprint = một mục tiêu, đối chiếu luồng orch ↔ bậc việc ↔ cổng (mục 5) | tiếp nhận yêu cầu, thấy rủi ro mới, gặp quy trình ngoài dùng tên luồng khác |
| [severity.md](severity.md) | thang Chặn / Phải sửa / Nên sửa / Ghi chú, kết luận Đạt / Đạt có điều kiện / Không đạt, **bảng quy đổi duy nhất** từ 10 thang cũ | gán mức cho `RF`, distill nguồn có thang khác |
| [evidence.md](evidence.md) | một `VR` gồm gì, 4 kết quả, độ tươi, test hồi quy, câu "đỏ", xong ≠ phát hành ≠ nghiệm thu, bằng chứng của reviewer, cổng giao hàng — kiểm cơ học trước Cổng 2 (mục 8) | ghi `VR`, kiểm PROGRESS/REPORT, sắp trình Cổng 2 |
| [review-gate.md](review-gate.md) | cổng review giữa thực thi và Cổng 2: bốn pha (song song theo khía cạnh · gộp theo bằng chứng · kiểm đối kháng · lỗi thì đóng), báo cáo của cổng; nhân đôi theo người cho việc rủi ro cao: [dual-review](../roles/verifier/dual-review.md) | review một diff cỡ vừa trở lên, việc có `risk_tags` `rules` / `secret` / `auth` |
| [conventions.md](conventions.md) | coverage 80 %, đường dẫn mặc định và khoá `.agile.json`, ADR, luật git, quy tắc số phiên bản (mục 4.1), frontmatter | cấu hình dự án, commit, viết ADR, đặt số phiên bản |

[standards/](standards/README.md) là chuẩn code chung (`common/`) và theo ngôn ngữ (`python`, `typescript`, `react`, `web`) — luật ngắn, mẫu code và lý do ở skill; Implementer đọc chuẩn của ngôn ngữ đang viết, Tech Reviewer đọc khi review ngôn ngữ đó; **không nạp vào `AGENTS.md`**.
