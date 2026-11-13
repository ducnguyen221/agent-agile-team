# Autopilot — phần của closing-sprint

> Phần luật autopilot của skill này, dời từ `SKILL.md` (SPR-16 TK1); một chế độ mặc định bật từ SPR-20 TK23; chỉ đường dẫn tương đối tới `method/` đổi theo vị trí file. Đọc khi đóng sprint.

## Cờ đỏ về autopilot (từ mục 7)

| Ý nghĩ | Thực tế |
|---|---|
| "Autopilot bật, nhánh sạch, gộp `main` luôn" | vào `main` chỉ qua PR sau Cổng 2 **Đạt**, kèm tag `backup/main-<ngày-giờ>` trước khi gộp (`method/git-conventions.md`); không commit thẳng `main` |
| "Cổng 2 Đạt có điều kiện, vẫn gộp" | Đạt có điều kiện không mở gộp `main`: một vòng sửa nữa, Gate Delegate phiên mới ký lại; còn Chặn/Phải sửa sau vòng đó → dừng và bàn giao |
| "Bản phát hành có guard tốt hơn, cập nhật bản cài luôn cho đồng bộ" | cài bản dựng và cập nhật bản cài là đổi cấu hình máy: làm ở bước riêng, báo rõ lệnh trước khi chạy, ghi lệnh hoàn tác (cài lại bản trước); không sửa tay bản chép |
| "Đạt có điều kiện nhưng CI xanh, bản tin ghi đã gộp `main` cũng được" | Đạt có điều kiện không gộp `main`; bản tin ghi đã gộp là lỗi, `check` báo Phải sửa |

## Mục 8 — Khi autopilot đang bật (mặc định mọi sprint)

Chi tiết: [method/autopilot.md](../../../method/autopilot.md) mục 2, 5, 8. Cổng 2 do Gate Delegate phiên mới ký (phiên điều phối và Analyst không ký); riêng sprint `risk_tags` `secret`/`auth` cổng về người.

- **Bản tin autopilot** — REPORT mục "Bản tin autopilot" (`SPRINT.md` dùng cùng tiêu đề), người dùng đọc sau, không chặn việc: dòng đầu cảnh báo nếu `main` chưa có ruleset · một dòng mỗi cổng (cổng · kết luận · người ký · đường tới `evidence/gate-N-verdict.md`) · hàng chờ người (`BR` `chờ người`) · nhánh chờ gộp · số phiên đã dùng / trần · mọi lần dừng và lý do.
- **Nhật ký quyết định** — REPORT (và `SPRINT.md`) có mục này: mỗi quyết định của Gate Delegate hay điều phối một dòng — quyết gì · ai ký (nhãn · vai · tier · model) · bằng chứng · lệnh hoàn tác.
- **Nhánh sprint, menu:** Gate Delegate ghi lựa chọn (gộp local / push + PR / giữ nguyên) và số version ở `gate-2-verdict.md`; điều phối thi hành. Cổng 2 **Đạt**: sau khi CI của đúng commit xanh, push nhánh sprint, mở PR bằng `gh pr create`, tạo tag `backup/main-<ngày-giờ>`, rồi gộp PR; không đẩy ép, không commit thẳng `main`. Cổng 2 **Đạt có điều kiện**: không gộp `main`, nhánh vào hàng chờ người của bản tin.
- Hết hạn hay hết sprint: bỏ sprint khỏi `sprints` của mọi file dấu (gốc repo và worktree phiên con), file nào rỗng thì xoá, sau cùng.

### Tin cuối sprint (báo cuối)

Một tin gom, gửi khi đóng sprint: Cổng 2 + bản tin + nhật ký quyết định + đề xuất sprint kế. Không tách thành nhiều tin lẻ. Mẫu:

```
Cổng 2 — sprint <SPR-> (<mục tiêu>): <Đạt / Đạt có điều kiện / Không đạt>.
Cảnh báo: <`main` chưa có ruleset — khuyến nghị mạnh, chủ repo đặt một lần> hoặc "không"
Khuyến nghị (T1, vai <vai>): <một câu: chọn gì, loại gì, sai thì tốn gì>
Bản tin autopilot:
- Số lượt Đức phải trả lời: <số> (không tính hộp xác nhận của rào máy)
- Cổng duyệt thay: <cổng · kết luận · người ký · evidence/gate-N-verdict.md>, mỗi cổng một dòng
- Đã đẩy: <nhánh · remote · sha> hoặc "không" · PR: <số, trạng thái> hoặc "không"
- Commit gộp: <sha, nhánh đích> hoặc "không" · Tag · bản phát hành: <tên, đường> hoặc "không"
- Hoàn tác từng bước: <mỗi việc đã đẩy, gộp, tag, phát hành một lệnh hoàn tác>
- Hàng chờ người · nhánh chờ gộp · phiên đã dùng / trần · mọi lần dừng và lý do
Nhật ký quyết định: <mỗi dòng: quyết gì · ai ký (nhãn · vai · tier · model) · bằng chứng · lệnh hoàn tác>
Đề xuất sprint kế: <một câu>
```

- **Dòng đếm lượt** có mặt ở mọi REPORT; `check` báo Nên sửa khi REPORT sprint mới thiếu. Đạt có điều kiện thì bản tin không ghi đã gộp `main`; `check` báo Phải sửa nếu có.
- **Bản cài:** bản phát hành chạm hook hay guard (`hooks/hooks.json`, `scripts/autopilot-hook.sh`, `scripts/autopilot_guard.py`, `scripts/_autopilot_rules.py`) thì cập nhật bản cài là đổi cấu hình máy: làm ở **bước riêng**, nêu rõ lệnh cài, lệnh kiểm (xem phiên bản đang cài) và lệnh hoàn tác (cài lại bản trước) **trước khi chạy**, rồi mới chạy; không sửa tay bản chép, không trỏ lại thư mục cài. Lý do: hook hỏng thì mọi phiên trên máy hỏng theo. Bản phát hành không chạm hook hay guard thì cập nhật bản cài chỉ qua công cụ cập nhật chính thức của máy đó; ghi vào bản tin.
