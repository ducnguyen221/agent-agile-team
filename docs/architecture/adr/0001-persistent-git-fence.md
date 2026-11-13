# 0001. Đặt rào git thường trực cho repo được bảo vệ, kèm hai lớp độc lập

Trạng thái: superseded (SPR-20, 13/11/2026: git-fence và shim gỡ hẳn; an toàn dựa vào git để quay lại và ruleset GitHub; xem plan SPR-20 bản 2) · Sprint: SPR-16 (chương trình SPR-15) · Liên quan: `method/git-permissions.md`, `method/autopilot.md` mục 5, PLAN mục Kiến trúc của SPR-16

## Bối cảnh

Rào của autopilot chỉ bật khi có lệnh `Bật autopilot …` và file dấu `.tmp/autopilot.json`; không file dấu thì `git push origin HEAD:main`
đi qua. Chương trình SPR-15 muốn agent không đưa gì vào nhánh chính hay ra ngoài khi người dùng chưa nói, **kể cả khi autopilot tắt**.
Ràng buộc thật: hook chỉ thấy lệnh shell và tool ghi file qua matcher đã đăng ký; Codex và Antigravity chưa có tầng "hỏi"; hook Codex phải do
người dùng trust; repo có người làm việc thẳng trên `main` (kho gốc của một workspace) bị chặn cả việc ghi hồ sơ nếu áp bảng đầy đủ; guard chạy
trong `timeout: 10` giây của hook trên Windows. Bên chịu ảnh hưởng: người dùng (hỏi nhiều hơn), mọi phiên có plugin bật trong repo có `.agile.json`.

## Lựa chọn

| Cách làm | Đánh đổi | Khi nào hợp |
|---|---|---|
| Chỉ mở rộng rào autopilot (giữ nguyên: cần file dấu) | không đổi hành vi hằng ngày; nhưng ngoài autopilot không có rào nào, đúng lỗ hổng đang có | khi chấp nhận tin vào lời dặn |
| **Rào thường trực trong guard (`git_fence.py`) + lớp độc lập thứ hai (ruleset GitHub hoặc `pre-push`)** | hỏi/chặn ở repo có dấu hiệu bảo vệ, có thể chặn nhầm lệnh hợp lệ và thêm trễ hook; lớp (b) không qua agent nên chặn cả script | khi cần chặn máy ở lớp hook **và** có đường cho việc hook không thấy |
| Chỉ ruleset/`pre-push` (bỏ hook) | độc lập hoàn toàn với agent nhưng không "hỏi" được, chỉ từ chối sau khi lệnh đã chạy tới tận remote; gói GitHub không phải nơi nào cũng có ruleset | khi không tin hook ở host nào |

## Quyết định

Chọn **rào thường trực trong guard cộng lớp độc lập thứ hai** — vì ràng buộc "không đưa gì ra ngoài khi người dùng chưa nói, kể cả khi autopilot tắt"
cần một lớp chặn trước khi lệnh chạy (hook) lẫn một lớp không phụ thuộc agent (ruleset/`pre-push`). Rào đặt ở mô-đun `scripts/git_fence.py` do
`autopilot_guard.py` gọi để giữ **một** tiến trình mỗi lần hook chạy. Repo làm việc thẳng trên `main` dùng mức `push-only` do người dùng đặt ở danh sách ngoài repo.

## Hệ quả

- Dễ hơn: đưa việc ra ngoài là luôn qua người; cờ `+đẩy-nhánh` cho đẩy nhánh sprint đúng hợp đồng đích mà không mở cửa nhánh chính.
- Khó hơn: hỏi nhiều hơn ở repo được bảo vệ; mỗi lần đổi hợp đồng đổi cùng lúc luật, công cụ kiểm, mẫu và test; guard thêm vài lời gọi `git` chỉ-đọc (tổng ≤4 giây).
- Bị cố định: `method/git-permissions.md` và các file trong `FENCE_FILES` là sàn cứng, sprint duyệt thay không sửa được; danh sách bảo vệ nằm ngoài repo.
- Quay lại: tắt plugin hoặc `git revert` các commit TK7–TK9 của SPR-16; hook thật ghi vào cấu hình người dùng khôi phục từ bản ghi. Phần còn là rào hành vi
  (script, công cụ MCP/terminal, `gh` nhắm repo khác) nói thẳng ở `method/git-permissions.md` mục 8 — ADR này không hứa chặn chúng.
