# Loại trừ mặc định và tiền lệ

> **Kết luận:** danh sách dưới đây là **loại trừ mặc định**, không tuyệt đối. Ứng viên rơi vào một mục
> vẫn là phát hiện nếu có bằng chứng kẻ tấn công kiểm soát đầu vào và vượt ranh giới bảo mật. Mỗi lần
> loại một ứng viên, ghi mục loại trừ vào thống kê lọc.

## 1. Loại trừ mặc định

1. Từ chối dịch vụ, cạn tài nguyên, thiếu rate limit đơn thuần. **Ngoại lệ:** khuếch đại chi phí gọi
   mô hình AI (pha 7) là rủi ro **tài chính** — không loại.
2. Secret trên đĩa đã được bảo vệ (mã hoá, phân quyền).
3. Cạn bộ nhớ, CPU, file descriptor.
4. Validate đầu vào ở trường không nhạy cảm, không có tác động chứng minh được.
5. Lỗi workflow CI không kích hoạt được bằng đầu vào không tin cậy. **Ngoại lệ:** không bao giờ tự loại
   phát hiện pha 4 (action không ghim, `pull_request_target`, script injection, lộ secret).
6. "Thiếu hardening" chung chung — chỉ gắn lỗ hổng cụ thể. **Ngoại lệ:** action bên thứ ba không ghim và
   thiếu CODEOWNERS cho workflow là rủi ro cụ thể.
7. Tấn công race/timing không có đường khai thác cụ thể.
8. Lỗ hổng bên trong thư viện cũ (pha 3 xử lý gộp).
9. Lỗi an toàn bộ nhớ ở ngôn ngữ an toàn bộ nhớ.
10. File chỉ là test/fixture và không được code thật import.
11. Ghi log đầu vào chưa làm sạch (log spoofing) — tự nó không phải lỗ hổng.
12. SSRF mà kẻ tấn công chỉ kiểm soát **đường dẫn**, không kiểm soát host hay giao thức — trừ khi đường
    dẫn đó vượt được ranh giới nhạy cảm.
13. Nội dung người dùng ở vị trí tin nhắn người dùng của hội thoại với mô hình.
14. Độ phức tạp regex ở code không bao giờ nhận đầu vào không tin cậy.
15. Vấn đề bảo mật trong file `*.md` thông thường. **Ngoại lệ:** `SKILL.md`, `AGENTS.md`, `CLAUDE.md`,
    `GEMINI.md` là **mã prompt thực thi được** — phát hiện pha 8 trong chúng không bao giờ bị loại.
16. Thiếu log kiểm toán đơn thuần.
17. Ngẫu nhiên không an toàn ngoài ngữ cảnh bảo mật (id phần tử giao diện).
18. Secret được commit rồi gỡ ngay trong cùng commit khởi tạo ban đầu.
19. CVE của dependency có điểm thấp (dưới 4.0) và không có khai thác đã biết.
20. Vấn đề Docker trong `Dockerfile.dev`/`Dockerfile.local` không được cấu hình deploy thật trỏ tới.
21. Phát hiện ở workflow đã lưu trữ hoặc đã tắt.

## 2. Tiền lệ

- Ghi secret dạng rõ vào log **là** phát hiện; ghi URL thì không (trừ khi URL chứa token).
- **UUID khó đoán không thay được phân quyền** — tài nguyên lấy theo UUID vẫn phải kiểm quyền theo đối
  tượng.
- Biến môi trường và cờ dòng lệnh là đầu vào tin cậy **trừ khi** chúng đến từ workflow nhận dữ liệu không
  tin cậy (tiêu đề PR, thân issue).
- Framework escape mặc định (React, Angular, template engine hiện đại) — chỉ gắn các lối thoát.
- JavaScript phía client không cần xác thực — đó là việc của server.
- Command injection cần một đường dữ liệu không tin cậy cụ thể tới lệnh.
- Notebook chỉ tính khi đầu vào không tin cậy với tới được.
- Lock file không track là phát hiện với ứng dụng, không với thư viện.
- `pull_request_target` **không** checkout code của PR là an toàn.
- Container chạy root trong compose cho máy dev là bình thường; trong Dockerfile/K8s của môi trường thật
  là phát hiện.
- Dependency dev, secret trong lịch sử, prompt injection ở vai người dùng: không loại hàng loạt — phân
  tích ai kiểm soát đầu vào và tác động là gì.
