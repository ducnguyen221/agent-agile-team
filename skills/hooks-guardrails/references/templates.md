# Mẫu cấu hình hook — để trình người dùng, không tự cài

Mọi khối dưới đây là **đề xuất**. Chưa được giao việc cài thì chỉ trình khối, nơi đặt và cách gỡ; không ghi vào cấu hình harness
hay `.git/hooks`. Thay `<đường>` bằng đường tới `skills/hooks-guardrails/scripts/` (hoặc nơi người dùng chép script tới).
Mọi hook ở đây là kiểu `command`; không có hook kiểu model.

## Contents

1. Chặn path — Claude Code · 2. Chặn path — Codex · 3. Chặn path — Antigravity · 4. Stop-hook chạy test (Claude Code, tuỳ chọn) ·
5. Git hook quét khoá · 6. Thử trước khi bật

## 1. Chặn path — Claude Code

Nơi đặt: `.claude/settings.json` (chung cho repo) hoặc `.claude/settings.local.json` (riêng máy); gộp vào khoá `hooks` nếu đã có.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit|NotebookEdit",
        "hooks": [
          { "type": "command", "command": "python <đường>/protect_paths.py --format claude", "timeout": 10, "onFailure": "block" }
        ]
      }
    ]
  }
}
```

Cách gỡ: xoá phần tử `PreToolUse` này khỏi tệp (hoặc xoá tệp `.claude/settings.local.json` nếu chỉ chứa khối này). Matcher liệt kê
tên đúng; đừng viết `Edit.*` vì nó khớp cả `NotebookEdit` và tên khác có chứa `Edit`.

`"onFailure": "block"` (khoá của tài liệu Claude Code, từ bản 2.1.295) làm hook lỗi hoặc hết giờ cũng chặn; thiếu khoá này, hook hết giờ không chặn và tool vẫn chạy. Đừng `--allow-name` đúng một tên trong danh sách cấm (vd `.env`): allow bỏ luật tên nên mở toang tên đó; chỉ allow tên phụ như `.env.local`. Allow chỉ khớp tên nguyên văn (không phân biệt hoa thường): `.env.example ` (dấu cách cuối) hay `.env.example:x` vẫn bị chặn. Hook chặn kèm `bad hook input (TypeError)` mà payload không hỏng là bug của script: đặt biến môi trường `PROTECT_PATHS_DEBUG=1` để in traceback ra stderr (vẫn chặn như cũ).

## 2. Chặn path — Codex

Nơi đặt: `~/.codex/hooks.json` (toàn máy) hoặc `<repo>/.codex/hooks.json` (chỉ có hiệu lực khi repo được trust). Người dùng phải
xem và trust hook qua `/hooks`; hook đổi nội dung thì trust lại. Đừng dùng cờ bỏ qua trust.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "apply_patch|Edit|Write",
        "hooks": [
          { "type": "command", "command": "python <đường>/protect_paths.py --format codex", "timeout": 10 }
        ]
      }
    ]
  }
}
```

Tài liệu Codex: sửa file đi qua tool `apply_patch`, và `matcher` viết `apply_patch`, `Edit` hoặc `Write` đều trúng; dòng vá
(`*** Add File:`, `*** Update File:`, `*** Delete File:`, `*** Move to:`) nằm ở `tool_input.command`, script đọc từ đó. Để `matcher`
trống vẫn an toàn (hook chạy cho mọi tool, script tự lọc), chỉ tốn một lần gọi Python mỗi tool.

Cách gỡ: xoá phần tử `PreToolUse` này, rồi mở `/hooks` kiểm không còn mục tương ứng.

Mọi lệnh mẫu dùng `python`; trên máy chỉ có `python3` thì đổi thành `python3` hoặc đường tuyệt đối tới interpreter (Claude Code
với `onFailure: block` sẽ chặn mọi lần ghi nếu không tìm thấy lệnh; Codex và Antigravity thì hook lỗi coi như mở).

## 3. Chặn path — Antigravity

Nơi đặt: `.agents/hooks.json` (workspace) hoặc `~/.gemini/config/hooks.json` (toàn máy).

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "write_to_file|replace_file_content|multi_replace_file_content",
        "hooks": [
          { "type": "command", "command": "python <đường>/protect_paths.py --format antigravity" }
        ]
      }
    ]
  }
}
```

Script đọc đường đích ở khoá `TargetFile` của `toolCall.args` (cả ba tool ghi file dùng khoá này).

Lưu ý: tên sự kiện, `matcher` (regex trên tên tool) và `type: command` khớp tài liệu chính chủ; dạng lồng `hooks`
giả định giống hai harness kia — đối chiếu lại trước khi áp; khối trên cố ý không đặt `timeout` vì chưa xác minh. Khi không chặn, script in `{}`; hành vi `{}` ở
`PreToolUse` chưa xác minh, nên thử trên máy: tool vẫn đi qua hỏi duyệt bình thường mới đạt. Muốn chắc hơn thì để `matcher`
trống để script tự lọc.

Cách gỡ: xoá phần tử `PreToolUse` này khỏi tệp.

## 4. Stop-hook chạy test (Claude Code, tuỳ chọn theo repo, mặc định tắt)

Chỉ bật khi repo muốn và có bộ test chạy nhanh. Hai phần: script `stop_tests.py` và khai báo.

Nơi đặt script: `.claude/hooks/stop_tests.py`.

```python
"""Stop-hook tuỳ chọn: chạy test, hỏng thì giữ agent làm tiếp. Không gọi model."""
import json
import subprocess
import sys

payload = json.load(sys.stdin)
if payload.get("stop_hook_active"):  # chống lặp: lượt này đã tiếp tục vì chính hook này
    sys.exit(0)
try:
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x"], capture_output=True, text=True, timeout=240)
except subprocess.TimeoutExpired:  # trần thời gian: hết giờ thì thôi, không giữ agent
    sys.stderr.write("stop-hook: test chạy quá 240 giây, bỏ qua lượt này\n")
    sys.exit(0)
if done.returncode not in (0, 5):  # 5 = không có test nào
    sys.stderr.write("stop-hook: test hỏng\n" + done.stdout[-2000:] + "\n")
    sys.exit(2)
sys.exit(0)
```

Nơi đặt khai báo: `.claude/settings.local.json` (riêng máy, để mặc định tắt cho người khác).

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "python .claude/hooks/stop_tests.py", "timeout": 300 }
        ]
      }
    ]
  }
}
```

Cách gỡ: xoá phần tử `Stop` và tệp `.claude/hooks/stop_tests.py`. Dùng lệnh test của repo thay cho `pytest` khi repo khác. Claude
Code còn tự ngắt sau một số lần chặn liên tiếp; đừng dựa vào trần đó thay cho chống lặp ở trên.

## 5. Git hook quét khoá

Không phụ thuộc harness: chạy khi `git commit`. Quét **tên biến** kiểu khoá trong dòng thêm vào và tên file `.env`; không chứa
và không in giá trị khoá.

Nơi đặt: `.git/hooks/pre-commit` (cần quyền chạy) hoặc thư mục hook của repo qua `core.hooksPath`.

```sh
#!/bin/sh
# pre-commit: chặn commit nếu dòng thêm vào gán chuỗi dài cho biến tên kiểu khoá, hoặc nếu có file .env
q="'"
named="(API_KEY|SECRET|TOKEN|PASSWORD|PRIVATE_KEY)[A-Za-z_]*[[:space:]]*[:=][[:space:]]*[\"${q}][^\"${q}[:space:]]{12,}[\"${q}]"
bare="^[A-Z_]*(KEY|SECRET|TOKEN|PASSWORD)[A-Z_]*=[^[:space:]\$]{12,}"
added=$(git diff --cached -U0 --no-color | grep -E '^\+[^+]' | sed 's/^+//')
if printf '%s\n' "$added" | grep -Eq "$named" || printf '%s\n' "$added" | grep -Eq "$bare"; then
  echo "pre-commit: dòng thêm vào gán giá trị cho biến tên kiểu khoá; đưa vào biến môi trường hay kho bí mật" >&2
  exit 1
fi
if git diff --cached --name-only | grep -E '(^|/)\.env(\.|$)' | grep -vq '\.env\.example$'; then
  echo "pre-commit: file .env trong commit; chỉ commit .env.example" >&2
  exit 1
fi
exit 0
```

Cách gỡ: xoá `.git/hooks/pre-commit` (hoặc bỏ cấu hình `core.hooksPath`). Đây là heuristic: có thể báo nhầm hoặc sót; chỉnh danh
sách tên biến theo repo. `git commit --no-verify` bỏ qua hook — agent không dùng cờ đó.

## 6. Thử trước khi bật

Mỗi hook thử bằng một thao tác cấm và một thao tác hợp lệ trước khi nói "hook chạy". Với `protect_paths.py` (bash; PowerShell
thì dùng chuỗi JSON đơn rồi `| python …` và đọc `$LASTEXITCODE`):

```sh
printf '%s' '{"tool_name":"Write","tool_input":{"file_path":"C:/repo/.env"}}' | python <đường>/protect_paths.py --format claude; echo "thoát $?"
printf '%s' '{"tool_name":"Write","tool_input":{"file_path":"C:/repo/.env.example"}}' | python <đường>/protect_paths.py --format claude; echo "thoát $?"
printf '%s' '{"toolCall":{"name":"write_to_file","args":{"TargetFile":"C:/repo/.env"}}}' | python <đường>/protect_paths.py --format antigravity; echo "thoát $?"
```

Dòng thứ ba là payload Antigravity thật: in JSON `"decision": "deny"` và thoát 0.

Kỳ vọng: dòng đầu in `blocked: C:/repo/.env (name:.env)` và `thoát 2`; dòng sau không in gì và `thoát 0`. Đổi `--format
antigravity` thì dòng đầu in JSON có `"decision": "deny"` và thoát 0, dòng sau in `{}`. Phép thử này chứng minh script, chưa chứng
minh harness gọi hook: phần đó thử bằng một thao tác cấm thật trên harness, hoặc ghi **Chưa chạy**.
