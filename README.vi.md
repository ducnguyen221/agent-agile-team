# agent-agile-team

> **Trạng thái: đang dựng — private.** Chưa phát hành, chưa có hướng dẫn cài. Bản tiếng Anh:
> [README.md](README.md).

Phương pháp agile cho đội agent AI: một quy trình (tiếp nhận → SPEC → PLAN → thực thi ↔ kiểm định →
REPORT → bài học, có hai cổng người duyệt), thẻ vai chỉ định theo tier thay vì tên model, mẫu tài liệu
sprint và sổ gốc dự án, một bộ skill gọn, và ba công cụ Python chỉ dùng thư viện chuẩn (`init`, `check`,
`index`) giữ tài liệu nhất quán.

Lõi trong repo này trung tính: không biết gì về máy, người hay dự án cụ thể nào. Môi trường dùng repo
cắm vào qua hai biến môi trường (`AGENT_AGILE_TIERS`, `AGENT_AGILE_DENYLIST`) và cách nạp luật đầu phiên
của riêng nó.

## Cấu trúc

| Đường dẫn | Mục đích |
|---|---|
| `AGENTS.md` | Luật lõi nạp đầu phiên (ngân sách ≤120 dòng, ≤10 KB) |
| `method/` | Quy trình, cỡ việc, thang mức, bằng chứng, quy ước |
| `roles/` | Thẻ vai: thực thi và kiểm định (kèm thẻ chuyên đề) |
| `tiers/` | Định nghĩa tier và hợp đồng bảng tier |
| `skills/` | Skill, để phẳng (`skills/<tên>/SKILL.md`) |
| `agents/` | Agent reviewer và trợ thủ |
| `templates/` | Mẫu tài liệu sprint, sổ gốc, cấu hình dự án |
| `scripts/` | `init`, `check`, `index` |
| `tests/` · `samples/` | Test và dự án mẫu kèm kết quả kỳ vọng |
| `hosts/` | Ghi chú từng harness (Claude, Codex, Claude Desktop, Antigravity) |

## Giấy phép

Chưa chọn; giữ mọi quyền trong thời gian private. Nguồn bên thứ ba ghi ở [UPSTREAM.md](UPSTREAM.md),
[NOTICE](NOTICE) và [THIRD_PARTY.md](THIRD_PARTY.md).
