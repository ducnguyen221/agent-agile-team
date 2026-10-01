# Tier

KHUNG — định nghĩa đầy đủ, luật không tự hạ tier, chỉ định đè của người dùng và tư vấn gọi chéo viết ở
`TK3.4`. Mục này chỉ chốt **hợp đồng điểm cắm**.

Vai được chỉ định theo **tier**, không theo tên model. Lõi chỉ biết ba tên tier:

| Tier | Mục đích |
|---|---|
| `T1` | Tư duy — phân tích, kiến trúc, kiểm định |
| `T2` | Thực thi — viết mã, viết tài liệu theo plan |
| `T3` | Việc vặt và QA / chạy test |

## Hợp đồng điểm cắm `AGENT_AGILE_TIERS`

- **Giá trị:** đường dẫn tuyệt đối tới một file JSON bảng tier → model. File nằm **ngoài** repo, do môi
  trường dùng repo quản lý. Repo không bao giờ chứa tên model thật.
- **Hình dạng:** như [`tiers.example.json`](tiers.example.json) — khóa `schema` (số nguyên, hiện là `1`)
  và `tiers`; mỗi tier có `purpose` và `models` ánh xạ tên harness → mã model của harness đó.
- **Khi thiếu biến, file không tồn tại hoặc đọc lỗi:** công cụ báo **Chưa chạy** cho phần cần bảng tier,
  không đoán model, không lấy giá trị mặc định.
- **Khi thiếu một harness hay một tier trong bảng:** báo Chưa chạy cho đúng ô đó; không tự hạ sang tier
  khác.
