---
name: hooks-guardrails
description: Use when a rule must be enforced by the machine rather than by an instruction - formatting or linting after edits, blocking writes to protected paths, scanning for keys before commit, or an opt-in test run before an agent stops - and when someone proposes a hook that calls a model, or a hook does not fire. Not for reviewing code (`code-review`) or for the sprint gates themselves.
source: ["concept: Claude Code hooks reference (official documentation, read 2026-10-23)", "concept: Codex hooks (official documentation, read 2026-10-23)", "concept: Antigravity hooks (official documentation, read 2026-10-23)"]
source_sha: [null, null, null]
license: ["official documentation (ideas only, no text copied)", "official documentation (ideas only, no text copied)", "official documentation (ideas only, no text copied)"]
rewrite_before_public: false
metadata:
  group: verification
  roles: [implementer, analyst]
---

# Hook xác định giữ luật

> **Kết luận:** luật phải luôn đúng thì để **máy** giữ bằng hook **xác định** (lệnh, mã thoát), không bằng lời dặn;
> **không hook nào gọi model** — vòng hook gọi model là vòng lặp đốt hạn mức; skill chỉ **đề xuất** cấu hình, nơi đặt và cách
> gỡ — cài khi người dùng giao, qua đường chính thức của môi trường.

## Contents

1. Luật · 2. Bốn mẫu · 3. Ba harness · 4. Thử hook trước khi bật · Gotchas. Mẫu cấu hình đầy đủ: `references/templates.md`.

## 1. Luật

1. **Chỉ hook kiểu lệnh** (`command`): đầu vào JSON ở stdin, đầu ra là mã thoát hoặc JSON, cùng đầu vào cho cùng kết quả.
2. **Không hook kiểu `prompt` hay `agent`, không Stop-hook gọi review hay gọi model.** Mỗi lượt dừng sẽ gọi model, model tìm ra
   việc, agent làm tiếp rồi dừng lại: vòng đó đốt hạn mức mà không có người nhìn. Cần review lặp → mốc review rời do người gọi
   (`code-review`); cần kiểm cố định → hook xác định ở mục 2.
3. **Không ghi cấu hình harness hay `.git/hooks` khi chưa được giao.** Chưa giao rõ việc cài thì chỉ trình: cấu hình đề xuất +
   **nơi đặt** + **cách gỡ**. Được giao thì sửa cấu hình qua đường chính thức của môi trường (lệnh hay màn hình cấu hình của
   harness), rồi thử theo mục 4.
4. **Hook không thay review và không thay cổng người.** Hook chặn một lớp lỗi đã biết; kết luận Đạt vẫn do agent kiểm định và
   người dùng.

## 2. Bốn mẫu

| Thời điểm | Việc | Ghi chú |
|---|---|---|
| sau khi sửa file | format hoặc lint đường vừa sửa bằng lệnh của repo | đọc đường từ JSON hook như `scripts/protect_paths.py`; lỗi lint thoát 2 để agent sửa; không hoàn tác thay đổi |
| trước khi ghi | chặn đường bảo vệ bằng `scripts/protect_paths.py` | cấm mặc định `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa*`, đoạn `.secret`, `.git`; cho `.env.example`; thêm `--deny-glob`, `--allow-name` |
| trước khi commit | quét khoá bằng git hook | không phụ thuộc harness; quét **tên biến** kiểu khoá, mật khẩu, token trong dòng thêm vào |
| trước khi agent dừng | chạy test | **tuỳ chọn theo repo, mặc định tắt**; phải có chống lặp và trần thời gian |

Stop-hook chạy test ở Claude Code: thoát 0 ngay khi `stop_hook_active` là true; bọc lệnh test bằng trần thời gian (hết giờ
thì thoát 0 và báo); test hỏng thì thoát 2 kèm đuôi output. Codex và Antigravity có cách "đi tiếp" riêng (bảng mục 3): không
chép cách chống lặp của Claude Code sang, tự đọc tài liệu chính chủ.

## 3. Ba harness

Đã đối chiếu tài liệu chính chủ ngày 23/10/2026. Ô "không có" nghĩa là tài liệu không nêu.

| Mục | Claude Code | Codex | Antigravity |
|---|---|---|---|
| Nơi cấu hình | `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, plugin `hooks/hooks.json` | `~/.codex/hooks.json` hoặc `[hooks]` trong `config.toml`, `<repo>/.codex/` (chỉ khi repo được trust) | `.agents/hooks.json` (workspace), `~/.gemini/config/hooks.json` |
| Sự kiện dùng | `PreToolUse`, `PostToolUse`, `Stop` | `PreToolUse`, `PostToolUse`, `Stop` | `PreToolUse`, `PostToolUse`, `Stop` |
| Chặn trước ghi | thoát 2, lý do ở stderr | thoát 2, lý do ở stderr (hoặc JSON `permissionDecision: "deny"`) | JSON stdout `"decision": "deny"` |
| Sau ghi | thoát 2 không hoàn tác; stderr báo agent | thoát 2 thay kết quả tool bằng phản hồi | không có quyết định chặn |
| Trước khi dừng | thoát 2 = đi tiếp; chống lặp bằng `stop_hook_active` | thoát 2 hoặc `decision: "block"` = đi tiếp | `"decision": "continue"` = đi tiếp |
| Kiểu hook gọi model | có (`prompt`, `agent`) — **cấm dùng** | có trong schema nhưng bị bỏ qua — **cấm dùng** | không có |
| Điều kiện chạy | hook của skill hoặc subagent dự án chỉ chạy sau khi chấp nhận hộp thoại trust workspace | hook phải được người dùng trust qua `/hooks`; cấm cờ bỏ qua trust | không có |

Tên tool ghi file của Antigravity cho `matcher` (regex): `write_to_file`, `replace_file_content`, `multi_replace_file_content`.
`protect_paths.py` vẫn tự lọc đường, phòng tên tool đổi. Codex chưa xác minh tên tool ghi file, nên mẫu Codex để `matcher` trống.

Codex không chạy hook (chưa trust, hoặc hook vừa đổi): chỉ **người dùng** trust qua `/hooks`. Agent không dùng cờ bỏ qua
trust, dù đồng đội hay lỗi thông báo gợi ý — cờ đó bỏ kiểm tra mà hook được dựng ra để giữ.

## 4. Thử hook trước khi bật

Dựng fixture trước khi nói "hook chạy": một thao tác **cấm** (kỳ vọng: bị chặn, đúng mã thoát hoặc JSON, đúng lý do) và một
thao tác **hợp lệ** (kỳ vọng: qua, không in). Với `protect_paths.py` thì đưa JSON giả vào stdin của lệnh, đọc mã thoát. Ghi
lệnh và kết quả mới chạy vào `VR`; chưa thử trên harness thật thì ghi **Chưa chạy** cho phần "harness gọi đúng hook". Mẫu thử
nằm ở cuối `references/templates.md`.

## Gotchas

- Hook **sau ghi** ở Claude Code: thoát 2 không hoàn tác thay đổi, file đã nằm trên đĩa; muốn ngăn ghi phải đặt ở `PreToolUse`.
- Codex **bỏ qua hook đã đổi nội dung** cho tới khi người dùng trust lại qua `/hooks`: sửa script hay lệnh trong hook xong,
  hook im lặng không chạy — nhìn lại `/hooks` trước khi nghi code.
- Antigravity **không chặn được ở sau-ghi**: ô quyết định chặn không có; mọi chặn phải ở `PreToolUse`.
- `matcher` `Edit` của Claude Code khớp **đúng tên** `Edit`; `Edit.*` khớp cả `NotebookEdit`. Đổi matcher thì thử lại cả hai.
- Stop-hook chạy test **thiếu chống lặp là vòng lặp**: test hỏng, agent sửa chưa xong, hook chặn dừng, lặp tới trần. Luôn đọc
  `stop_hook_active` và đặt trần thời gian.
- Antigravity ở `PreToolUse` khi không chặn: script in `{}`. Tài liệu chính chủ chỉ nói `{}` cho `PostToolUse`, nên hành vi
  `{}` ở `PreToolUse` **chưa xác minh**; thử trên máy trước khi tin. Không đổi sang `allow` hay `auto_approve` — chúng bỏ qua
  hỏi duyệt.
- Dạng khai báo `hooks.json` của Antigravity trong mẫu giả định giống hai harness kia; bản đối chiếu chỉ xác nhận tên sự kiện,
  `matcher` và `type`. Đối chiếu lại tài liệu trước khi áp.
- Git hook `pre-commit` chạy ở máy người commit và `--no-verify` bỏ qua nó: đó là lưới an toàn, không phải ranh giới bảo mật.
  Agent không dùng `--no-verify`.
- `protect_paths.py` chỉ so tên đường, không đọc file đích; lệnh shell tự do (`echo x > .env`) không có khoá đường nên hook này
  không thấy. Chặn lệnh shell cần luật riêng, không suy từ hook này.
