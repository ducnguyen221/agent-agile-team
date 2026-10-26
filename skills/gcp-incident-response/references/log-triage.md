# Triage log mà không tràn ngữ cảnh

Đưa log GCP thô vào model là cách nhanh nhất để đầy ngữ cảnh và mất mạch điều tra.

## Contents

1. Thu gọn trước khi đọc · 2. Đọc có hạn giờ (bash và PowerShell) · 3. Định dạng gọn

## 1. Thu gọn trước khi đọc

- **Đừng** đọc nguyên file xuất lớn (ví dụ một file JSON log truy cập vài trăm MB). Thu gọn bằng `jq` trước:
  `jq -r '.[] | .httpRequest.status'` cho biểu đồ phân bố mã trạng thái; lọc `severity >= "ERROR"` (log lỗi ngắn và đậm tín
  hiệu hơn); giới hạn cửa sổ thời gian ở khoảng sự cố ± vài giờ.
- Nhắm đích bằng bộ lọc `gcloud logging read` (dịch vụ, mức nghiêm trọng, khoảng thời gian) thay vì kéo hết rồi lọc.

## 2. Đọc có hạn giờ

`gcloud logging read` có thể treo — đặt hạn giờ thật:

- **Cloud Shell / Linux (bash):** thêm `timeout 60` đầu lệnh: `timeout 60 gcloud logging read '<filter>' --limit=500`.
- **Windows PowerShell:** không có lệnh `timeout` dùng được (`timeout.exe` có sẵn chỉ là lệnh ngủ tương tác, không bọc lệnh khác) —
  chạy việc đọc thành job có hạn cứng:

  ```powershell
  $j = Start-Job { gcloud logging read '<filter>' --limit=500 }
  if (Wait-Job $j -Timeout 60) { Receive-Job $j } else { Stop-Job $j; Remove-Job $j -Force; 'timed out' }
  ```

- Cả hai shell: ưu tiên job **nền** đổ ra file rồi thăm dò file, thay vì chặn phiên làm việc.

## 3. Định dạng gọn

Đổi JSON dài dòng sang dạng một dòng gọn (kiểu rút gọn như access log Apache-combined tiết kiệm token hơn nhiều) — nhưng làm
bước đổi bằng script/`jq`, đừng dán file thô vào ngữ cảnh.
