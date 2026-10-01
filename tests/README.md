# Test

Chạy: `python -m pytest` từ gốc repo (chỉ cần Python 3 và pytest).

Hiện có: `test_version_sync.py` — mọi manifest cùng một version, và mục đầu `CHANGELOG.md` là version đó.
Test cho ba script, chống rò, nguồn gốc và ngân sách `AGENTS.md` viết ở `TK4`. Fixture đúng và hỏng cố ý
nằm ở `fixtures/`.

## Hợp đồng điểm cắm `AGENT_AGILE_DENYLIST`

Test chống rò (lõi không chứa dấu riêng của bất kỳ máy, người hay dự án nào) đọc danh sách từ cấm từ
**ngoài** repo — để chính danh sách không làm lộ thứ nó che.

- **Giá trị:** đường dẫn tuyệt đối tới một file văn bản UTF-8 nằm ngoài repo.
- **Định dạng:** mỗi dòng một từ cấm, so khớp không phân biệt hoa thường; dòng trống và dòng bắt đầu
  bằng `#` bị bỏ qua.
- **Phạm vi quét:** mọi file Git đang theo dõi trong repo.
- **Khi thiếu biến hoặc file không đọc được:** test chống rò báo **Chưa chạy** (skip có lý do), không báo
  Đạt.
