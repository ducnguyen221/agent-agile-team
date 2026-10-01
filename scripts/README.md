# scripts/

KHUNG — viết ở `TK4` theo TDD, chỉ dùng thư viện chuẩn Python:

- `init.py` — dựng sổ gốc và khung sprint từ mẫu; mặc định chạy thử, không ghi đè.
- `check.py` — kiểm chuẩn tài liệu; `--self` kiểm lõi sạch và ngân sách `AGENTS.md`. Mã thoát 0 / 1 / 2.
- `index.py` — sinh khối "đang mở" ở đầu ba sổ gốc.
- `_common.py` — thư viện đọc frontmatter và `.agile.json`; không chạy trực tiếp.
