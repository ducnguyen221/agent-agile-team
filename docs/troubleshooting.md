# Lỗi hay gặp

> **Kết luận:** bảy triệu chứng hay gặp khi cài và dùng lần đầu, mỗi cái một cách xử lý. Phần lớn là
> **cấu hình chưa đặt** (điểm cắm của lớp riêng) hoặc **cách shell xử lý** dấu `~` và mã hoá ký tự — không phải lỗi của script.

Cài đặt: [`INSTALL.md`](../INSTALL.md). Điểm cắm: [`hosts/README.md`](../hosts/README.md) mục 2.

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `check.py --self` in `WARNING NOT_CONFIGURED`, dòng cuối `chống rò: NOT_CONFIGURED`; `pytest` có 1 ca skip | Biến `AGENT_AGILE_DENYLIST` chưa đặt, trỏ file không có hoặc file rỗng | Không phải lỗi: luật chống rò **Chưa chạy** (không tính Đạt). Muốn chạy thì đặt biến trỏ file từ cấm **ngoài repo** ([`tests/README.md`](../tests/README.md)) rồi mở terminal / phiên **mới** — biến chỉ thấy ở tiến trình mới |
| `init.py` in `cảnh báo: AGENT_AGILE_TIERS chưa đặt…` khi dựng sprint | Chưa có bảng tier → model | Agent dùng chỉ định tier → model người dùng nêu trong chat; chưa có thì hỏi ở Cổng 1. Muốn cố định: đặt biến trỏ file JSON theo [`tiers/tiers.example.json`](../tiers/tiers.example.json) |
| Claude Code không biết luật lõi (hỏi "hai cổng là gì" thì trả lời sai) | Dòng `@…/AGENTS.md` chưa có, sai đường, nằm trong khối code hay dấu huyền (import trong code không được nạp), hoặc phiên mở trước khi thêm dòng | Gõ `/memory` để xem file luật nào đã nạp; sửa dòng import ở `~/.claude/CLAUDE.md` (đường dạng `@~/agent-agile-team/AGENTS.md`, đứng riêng một dòng); mở **phiên mới**. Codex / Antigravity: chạy lại script sinh luật của môi trường |
| Tiêu đề sprint mất dấu tiếng Việt (`Tra c?u ??n`), `init` cảnh báo dấu `?` hoặc ký tự thay thế | Shell gọi Python (một số cầu Git Bash, `cmd` code page cũ) làm mất dấu **trước khi** tới script | Ghi tiêu đề vào file UTF-8 rồi dùng `--title-file <file>`, hoặc chạy `python -X utf8 scripts/init.py …` từ PowerShell. Tiêu đề đã ghi sai thì sửa tay trong frontmatter + dòng SPRINTS |
| `index.py` / `init.py` thoát 2: `không đọc được dạng UTF-8 … — lưu lại sổ bằng UTF-8` | Sổ gốc hoặc spec sống bị lưu bằng bảng mã khác (Windows PowerShell 5.1 `Set-Content` mặc định ANSI; một số editor mặc định UTF-16) | Mở file, lưu lại dạng **UTF-8** (có hay không BOM đều được); PowerShell thì ghi bằng `-Encoding utf8`. Chạy lại lệnh |
| Sau khi chạy `init`/`index`, `git diff` báo đổi **cả file** dù chỉ một dòng | Kiểu xuống dòng bị đổi (LF ↔ CRLF) — thường do editor hoặc `core.autocrlf`, không do script: script giữ nguyên BOM và kiểu xuống dòng của file có sẵn | `git diff --ignore-cr-at-eol` để xác nhận; dự án muốn cố định thì thêm `.gitattributes` (`* text=auto eol=lf`) rồi `git add --renormalize .`. Repo phương pháp này đã ép LF |
| Windows PowerShell: `python ~/agent-agile-team/…` báo `can't open file '…\~\agent-agile-team…'`, `git -C ~/agent-agile-team …` báo `cannot change to '~/agent-agile-team'` | Windows PowerShell 5.1 chỉ mở `~` cho lệnh của chính PowerShell (`cd`, `Get-ChildItem`), **không** mở cho chương trình ngoài (`python`, `git`, `claude`) — chúng nhận nguyên chữ `~` | Dùng `"$HOME\agent-agile-team"` (hoặc `$env:USERPROFILE`) thay `~/agent-agile-team`, như các khối lệnh PowerShell trong `INSTALL.md` và `GUIDE.md`. Riêng dòng `@~/agent-agile-team/AGENTS.md` trong file luật của Claude Code giữ nguyên — Claude Code tự mở `~` |

Không thấy triệu chứng của mình ở đây: chạy `python scripts/check.py --self` và chép nguyên dòng cuối; mã thoát
của ba script ở [`scripts/README.md`](../scripts/README.md) mục "Mã thoát". Trên macOS dùng `python3` thay
`python`; Windows mở Microsoft Store khi gõ `python` nghĩa là máy chưa có Python thật.
