# skills/

Skill để **phẳng**: `skills/<tên>/SKILL.md` (+ `references/`, `tests/`), vì harness chỉ dò một cấp. Nhóm
(Quy trình, Kỹ thuật, Kiểm định, Giao tiếp, Meta) ghi trong frontmatter `metadata.group` và trong mục lục
README gốc. Frontmatter tiếng Anh (`description` chỉ ghi **điều kiện kích hoạt**, bắt đầu bằng "Use
when…"), thân tiếng Việt. Mỗi skill có `tests/pressure.md`: 3 kịch bản thử áp lực, chạy bằng subagent
không có skill (ghi lỗi) rồi có skill (phải đạt).

## Skill hiện có

| Skill | Nhóm | Dùng khi |
|---|---|---|
| [response-style](response-style/SKILL.md) | Giao tiếp | chọn độ dài, cấu trúc, giọng khi trả lời người hay agent; lối ra giải thích |
| [id-convention](id-convention/SKILL.md) | Giao tiếp | đặt, đọc, nhắc chéo, kiểm mã mục trong tài liệu sprint và chat |
| [token-economy](token-economy/SKILL.md) | Meta | phiên dài, output lớn, subagent báo cáo, nén ngữ cảnh, tuyên bố tiết kiệm token |

Skill distill từ nguồn cũ (quy trình, kỹ thuật, kiểm định) được thêm ở các đợt sau theo bảng ánh xạ trong
`docs/MIGRATION.md`.
