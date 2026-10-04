# Dùng agent-agile-team với Claude Code

> **Kết luận:** cài plugin để có 32 skill và 13 agent (chỉ đọc, riêng `build-fixer` được sửa — T2); thêm một dòng `@import` tới `AGENTS.md` vào
> file luật cấp người dùng để luật lõi có mặt ở **mọi** phiên. Áp cho Claude Code ở terminal, IDE và tab
> **Code** của ứng dụng Claude.

## 1. Luật lõi

- Phiên mở **trong thư mục repo**: `CLAUDE.md` của repo là đúng một dòng `@AGENTS.md` — Claude Code không tự
  đọc `AGENTS.md`, dòng import nạp nó thật. Không cần làm gì thêm.
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
