# Autopilot — phần của closing-sprint

> Phần luật autopilot của skill này, dời **nguyên văn** từ `SKILL.md` (SPR-16 TK1); chỉ đường dẫn tương đối tới `method/` đổi theo vị trí file. Đọc khi nhận hoặc ghi lệnh autopilot.

## Cờ đỏ về autopilot (từ mục 7)

| Ý nghĩ | Thực tế |
|---|---|
| "Autopilot bật, nhánh sạch, gộp luôn" | lệnh không có `+nhánh` thì gộp cục bộ nhánh sprint thuộc danh sách loại; nhánh vào hàng chờ người của bản tin (mục 8) |
| "Cổng 2 Đạt có điều kiện, `+nhánh` vẫn gộp" | `+nhánh` chỉ cho gộp khi Cổng 2 là Đạt; Đạt có điều kiện thì nhánh vào hàng chờ người |
| "Bản phát hành có guard tốt hơn, cập nhật bản cài luôn cho đồng bộ" | bản phát hành chạm hook hay guard thì agent không tự cập nhật bản cài: ghi vào gói lệnh chỉ Đức và chờ (mục 8, "Rào bản cài") |
| "Đạt có điều kiện nhưng CI xanh, bản tin ghi đã gộp `main` cũng được" | Đạt có điều kiện không gộp `main`; bản tin ghi đã gộp là lỗi, `check` báo Phải sửa |

## Mục 8 — Khi autopilot đang bật

Chi tiết: [method/autopilot.md](../../../method/autopilot.md) mục 2, 5, 8. Cổng 2 do Gate Delegate phiên mới ký **chỉ khi** lệnh là `cổng 1+2`; lệnh `cổng 1` thì Cổng 2 về người. Phiên điều phối và Analyst không ký.

- **Bản tin autopilot** — REPORT mục "Bản tin autopilot" (`SPRINT.md` dùng cùng tiêu đề), người dùng đọc sau, không chặn việc: một dòng mỗi cổng duyệt thay (cổng · kết luận · người ký · đường tới `evidence/gate-N-verdict.md`) · hàng chờ người (`BR` `chờ người`) · nhánh chờ gộp · số phiên đã dùng / trần · mọi lần dừng và lý do. Sprint không bật autopilot ghi "Không áp dụng".
- **Nhánh sprint, menu:** lệnh **không có `+nhánh`** → gộp cục bộ thuộc danh sách loại, kể cả khi Cổng 2 Đạt: bản tin ghi rõ "lệnh không có `+nhánh` nên không gộp", nhánh vào hàng chờ người, menu mục 3 để người dùng trả lời sau. Lệnh **có `+nhánh`** (chỉ với `cổng 1+2`, đứng cuối câu): gộp cục bộ vào nhánh tích hợp **không phải nhánh chính**, **chỉ khi Cổng 2 là Đạt** và CI của đúng commit theo mục 3; Đạt có điều kiện thì nhánh vào hàng chờ người.
- **Lệnh có `+đẩy-nhánh`** (chỉ với `cổng 1+2`, đứng cuối câu; file dấu có bốn khoá đích, `exclusions` không có `push`): **sau Cổng 2 Đạt** và CI của đúng commit xanh, đẩy nhánh sprint bằng `git push <push_remote> <nhánh sprint>` — đúng remote và đúng một ref trong `push_targets`, không `+`, không `--force*`, không `HEAD:<nhánh chính>` — rồi mở PR bằng `gh pr create`. Chỉ vậy: **không** gộp PR, **không** tag, **không** đẩy nhánh chính. Bản tin ghi đã đẩy gì, tới đâu, PR nào đang chờ người gộp. Đạt có điều kiện thì không đẩy: nhánh vào hàng chờ người.
- **Luôn hỏi người, từng lần, dù lệnh nào:** PR gộp, tag, tăng phiên bản, gộp vào nhánh chính; và push khi lệnh không có `+đẩy-nhánh` hay lệnh đẩy lệch hợp đồng đích. Autopilot không có `+push`.
- Hết hạn hay hết sprint: bỏ sprint khỏi `sprints` của mọi file dấu (gốc repo và worktree phiên con), file nào rỗng thì xoá, sau cùng.

### Tin cuối sprint (hai tin dừng, tin thứ hai)

Một tin gom, gửi khi đóng sprint: Cổng 2 + bản tin + gói lệnh chỉ Đức + đề xuất sprint kế. Không tách thành nhiều tin lẻ. Dòng `Khuyến nghị` có sẵn vì autopilot bật (`method/process.md` mục 3). Mẫu:

```
Cổng 2 — sprint <SPR-> (<mục tiêu>): <Đạt / Đạt có điều kiện / Không đạt>.
Khuyến nghị (T1, vai <vai>): <một câu: chọn gì, loại gì, sai thì tốn gì>
Bản tin autopilot:
- Số lượt Đức phải trả lời: <số> (không tính hộp xác nhận của rào máy; mục tiêu ≤ 1 sprint ký thay, ≤ 2 sprint cổng người)
- Cổng duyệt thay: <cổng · kết luận · người ký · evidence/gate-N-verdict.md>, mỗi cổng một dòng
- Đã đẩy: <nhánh · remote · sha> hoặc "không" · PR: <số, trạng thái> hoặc "không"
- Commit gộp: <sha, nhánh đích> hoặc "không" · Tag · bản phát hành: <tên, đường> hoặc "không"
- Hoàn tác từng bước: <mỗi việc đã đẩy, gộp, tag, phát hành một lệnh hoàn tác>
- Hàng chờ người · nhánh chờ gộp · phiên đã dùng / trần · mọi lần dừng và lý do
Gói lệnh chỉ Đức (mỗi lệnh: mục đích · lệnh kiểm · hoàn tác): <danh sách> hoặc "không có"
Đề xuất sprint kế: <một câu>
```

- **Dòng đếm lượt** có mặt dù sprint không bật autopilot; `check` báo Nên sửa khi REPORT sprint mới thiếu. Đạt có điều kiện thì bản tin không ghi đã gộp `main`: nhánh vào hàng chờ người; `check` báo Phải sửa nếu có.
- **Rào bản cài:** bản phát hành chạm hook hay guard (`hooks/hooks.json`, `scripts/autopilot-hook.sh`, `scripts/autopilot_guard.py`, `scripts/git_fence.py`, `scripts/_autopilot_rules.py`) thì **agent không tự cập nhật bản cài**: không chạy lệnh cài hay cập nhật plugin, không sửa tay bản chép, không trỏ lại thư mục cài. Ghi vào gói lệnh chỉ Đức: mục đích (đưa bản cài lên bản mới), lệnh kiểm (xem phiên bản đang cài), lệnh hoàn tác (cài lại bản trước), rồi chờ Đức. Lý do: hook hỏng thì mọi phiên trên máy hỏng theo. Bản phát hành không chạm hook hay guard thì cập nhật bản cài chỉ qua công cụ cập nhật chính thức của máy đó, trong phạm vi lệnh; ghi vào bản tin.
