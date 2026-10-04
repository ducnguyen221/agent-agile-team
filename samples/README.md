# samples/

Một dự án mẫu sạch, dựng bằng `init.py` rồi điền tay, để xem các tài liệu trông thế nào khi đã dùng thật và
để test kiểm `check`/`index`.

`order-desk/` — dự án tra cứu đơn hàng:

| File | Trạng thái trong mẫu |
|---|---|
| `.agile.json` | cấu hình mặc định |
| `docs/plans/REQUESTS.md` | `RQ-001` xong, `RQ-002` mới (nợ `SPR-01/CO1` chuyển thành yêu cầu), `RQ-003` đang làm, `RQ-004` đang làm, `RQ-005` xong |
| `docs/plans/SPRINTS.md` | `SPR-01` và `SPR-04` đã đóng, `SPR-02` và `SPR-03` đang mở |
| `docs/plans/2026-01-15-order-lookup/` | `SPR-01` đủ bốn tài liệu SPEC → PLAN → PROGRESS → REPORT, đã qua Cổng 1 và Cổng 2 |
| `docs/plans/2026-01-20-fix-not-found-text/SPRINT.md` | `SPR-02` việc rất nhỏ theo dạng cũ (một file bốn phần, vẫn hợp lệ), đang kiểm định |
| `docs/plans/2026-01-22-trim-order-code/SPRINT.md` | `SPR-03` việc **nhỏ**: một `SPRINT.md` đủ bốn phần, `size: small`, Cổng 1 đã duyệt, đang kiểm định (dựng bằng `init --size small`) |
| `docs/plans/2026-01-23-rename-submit-button/SPRINT.md` | `SPR-04` việc **rất nhỏ**: một `SPRINT.md` hai phần Kế hoạch / Kết quả, Cổng 1 "đạt theo lời giao", Cổng 2 nghiệm thu ngầm, đã đóng (dựng bằng `init --tiny`) |
| `docs/specs/SPECS.md` + `order-lookup.md` | `FS-001` spec sống đang chạy |

Kết quả kỳ vọng (cũng là test trong `tests/test_samples.py`):

```text
python scripts/check.py samples            → 0 phát hiện, thoát 0
python scripts/index.py samples/order-desk --check   → thoát 0 (khối "Đang mở" đã cập nhật)
```

Sửa mẫu tài liệu ở `templates/` không tự cập nhật thư mục này; dựng lại bằng `init.py` nếu hình dạng đổi.
