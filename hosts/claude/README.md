# Dùng agent-agile-team với Claude Code

> **Kết luận:** cài plugin để có 37 skill và 13 agent (chỉ đọc, riêng `build-fixer` được sửa — T2); thêm một dòng `@import` tới `AGENTS.md` vào
> file luật cấp người dùng để luật lõi có mặt ở **mọi** phiên. Áp cho Claude Code ở terminal, IDE và tab
> **Code** của ứng dụng Claude.

## 1. Luật lõi

- Phiên mở **trong thư mục repo**: repo cố ý không có `CLAUDE.md` (`claude plugin validate --strict` đỏ nếu có). Luật
  lõi vào qua dòng import cấp người dùng ở dưới — đã có dòng đó thì không cần làm gì thêm. Chưa có thì Claude Code
  ≥ 2.1.277 tự đọc `AGENTS.md`, nhưng chỉ khi thư mục làm việc và mọi thư mục cha không có `CLAUDE.md`,
  `.claude/CLAUDE.md` hay `CLAUDE.local.md` (`~/.claude/CLAUDE.md` không tính), và mục *Project instructions*
  trong `/config` chưa tắt. Không thoả hai điều đó thì tạo `.claude/CLAUDE.md` cục bộ chứa đúng một dòng
  `@../AGENTS.md` (đường `@` tính từ file chứa nó); `.gitignore` đã bỏ qua file này để nó không vào repo. Gõ
  `/memory` trong phiên để xem luật đã nạp từ đâu.
- Phiên ở **dự án khác** (cách dùng thường ngày): thêm một dòng vào file luật cấp người dùng
  `~/.claude/CLAUDE.md`, trỏ tới bản clone của repo, ví dụ:

  ```text
  @~/agent-agile-team/AGENTS.md
  ```

  Đây là file luật của người dùng — agent nói rõ sẽ thêm dòng nào, ở đâu, rồi **chờ người dùng đồng ý**.
  Luật lõi có ngân sách ≤120 dòng, ≤10 KB (`check.py --self` đo) vì nó là thuế token của mọi phiên.

## 2. Skill và agent — cài plugin

```bash
claude plugin marketplace add ~/agent-agile-team          # bản clone cục bộ — macOS, bash
claude plugin install agent-agile-team@agent-agile-team
```

```powershell
claude plugin marketplace add "$HOME\agent-agile-team"    # Windows PowerShell — 5.1 không mở `~`
claude plugin install agent-agile-team@agent-agile-team
```

Đã có quyền đọc repo trên GitHub thì thay dòng đầu bằng `claude plugin marketplace add https://github.com/ducnguyen221/agent-agile-team.git`.
Skill hiện với tên có tiền tố `agent-agile-team:` (ví dụ `agent-agile-team:intake`), nên không đè skill cùng tên của plugin khác.
Claude Code có skill dựng sẵn tên trần `code-review` và `security-review`; gọi tên trần sẽ ra bản dựng sẵn. Skill và
luật của repo trỏ nhau bằng tên trần (không phụ thuộc harness — `writing-skills` mục 6), nên trên Claude, khi một skill
nói "skill `code-review`" hay "skill `security-review`", gọi `agent-agile-team:code-review` /
`agent-agile-team:security-review`.

Thử khi đang sửa repo, không cài lại plugin:

```bash
claude --plugin-dir ~/agent-agile-team                    # macOS, bash
```

```powershell
claude --plugin-dir "$HOME\agent-agile-team"              # Windows PowerShell
```

**Hook autopilot.** Plugin kèm `hooks/hooks.json`: hook `PreToolUse` cho `Bash|PowerShell` chạy
`scripts/autopilot-hook.sh --format claude` (launcher, chạy bằng `sh`; Claude Code trên Windows dùng Git Bash, nên máy Windows cần Git for Windows).
Launcher gọi `scripts/autopilot_guard.py` bằng `python3`, `python` hoặc `py -3` (cần Python 3.9 trở lên nếu có). Hook chỉ chặn khi có
`.tmp/autopilot.json` (dấu autopilot đang bật); không có file đó thì thoát 0 và không làm gì. Máy không có Python dùng được, hoặc
guard vắng hay lỗi: launcher tự dò file dấu bằng `sh` và chỉ chặn khi có file dấu, nên không làm hỏng công cụ shell của dự án chưa bật
autopilot. Codex và Antigravity chưa có hook này: xem [method/autopilot.md](../../method/autopilot.md).

**Lệnh dừng.** Plugin kèm `commands/stop-autopilot.md`: gõ `/agent-agile-team:stop-autopilot` (kèm `SPR-NN` nếu chỉ thu hồi một sprint) để lấy câu chuẩn `Dừng autopilot.` hoặc `Thu hồi duyệt thay SPR-NN.`; lệnh chỉ in câu, người dùng phải gửi câu đó trong chat.

## 3. Kiểm, cập nhật, gỡ

- **Kiểm:** mở phiên **mới**, hỏi agent "luật lõi agent-agile-team nói gì về hai cổng?" — trả lời đúng là luật
  đã nạp; gõ `/agent-agile-team:` để thấy danh sách skill. Trong thư mục repo:
  `python scripts/check.py --self` (macOS: `python3`) phải ra `Đạt`.
- **Cập nhật:** `git pull --ff-only` trong bản clone, rồi
  `claude plugin marketplace update agent-agile-team` và
  `claude plugin update agent-agile-team@agent-agile-team`.
- **Gỡ:** `claude plugin uninstall agent-agile-team@agent-agile-team`, rồi bỏ dòng `@import` ở mục 1 (hỏi người
  dùng trước). Gỡ không xoá sổ gốc hay tài liệu sprint của dự án đã áp dụng.

## 4. Điểm cắm

Bảng tier, danh sách từ cấm, nơi lưu bài học, cầu gọi chéo: [`hosts/README.md`](../README.md) mục 2.
