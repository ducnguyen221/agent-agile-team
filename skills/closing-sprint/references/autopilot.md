# Autopilot — phần của closing-sprint

> Phần luật autopilot của skill này, dời **nguyên văn** từ `SKILL.md` (SPR-16 TK1); chỉ đường dẫn tương đối tới `method/` đổi theo vị trí file. Đọc khi nhận hoặc ghi lệnh autopilot.

## Cờ đỏ về autopilot (từ mục 7)

| Ý nghĩ | Thực tế |
|---|---|
| "Autopilot bật, nhánh sạch, gộp luôn" | lệnh không có `+nhánh` thì gộp cục bộ nhánh sprint thuộc danh sách loại; nhánh vào hàng chờ người của bản tin (mục 8) |
| "Cổng 2 Đạt có điều kiện, `+nhánh` vẫn gộp" | `+nhánh` chỉ cho gộp khi Cổng 2 là Đạt; Đạt có điều kiện thì nhánh vào hàng chờ người |

## Mục 8 — Khi autopilot đang bật

Chi tiết: [method/autopilot.md](../../../method/autopilot.md) mục 2, 5, 8. Cổng 2 do Gate Delegate phiên mới ký **chỉ khi** lệnh là `cổng 1+2`; lệnh `cổng 1` thì Cổng 2 về người. Phiên điều phối và Analyst không ký.

- **Bản tin autopilot** — REPORT mục "Bản tin autopilot" (`SPRINT.md` dùng cùng tiêu đề), người dùng đọc sau, không chặn việc: một dòng mỗi cổng duyệt thay (cổng · kết luận · người ký · đường tới `evidence/gate-N-verdict.md`) · hàng chờ người (`BR` `chờ người`) · nhánh chờ gộp · số phiên đã dùng / trần · mọi lần dừng và lý do. Sprint không bật autopilot ghi "Không áp dụng".
- **Nhánh sprint, menu:** lệnh **không có `+nhánh`** → gộp cục bộ thuộc danh sách loại, kể cả khi Cổng 2 Đạt: bản tin ghi rõ "lệnh không có `+nhánh` nên không gộp", nhánh vào hàng chờ người, menu mục 3 để người dùng trả lời sau. Lệnh **có `+nhánh`** (chỉ với `cổng 1+2`, đứng cuối câu): gộp cục bộ vào nhánh tích hợp **không phải nhánh chính**, **chỉ khi Cổng 2 là Đạt** và CI của đúng commit theo mục 3; Đạt có điều kiện thì nhánh vào hàng chờ người.
- **Luôn hỏi người, từng lần, dù lệnh nào:** push, PR gộp, tag, tăng phiên bản, gộp vào nhánh chính. Autopilot không có `+push`.
- Hết hạn hay hết sprint: bỏ sprint khỏi `sprints` của mọi file dấu (gốc repo và worktree phiên con), file nào rỗng thì xoá, sau cùng.
