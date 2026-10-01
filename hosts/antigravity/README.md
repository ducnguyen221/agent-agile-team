# Dùng agent-agile-team với Google Antigravity

> **Kết luận:** Antigravity tự nạp `AGENTS.md` và `GEMINI.md` của workspace; ngoài repo thì ghép luật lõi vào
> file luật cấp người dùng bằng bản sinh như Codex. Skill theo chuẩn Agent Skills mở, liên kết **từng thư mục**
> skill vào thư mục skill của Antigravity.

## 1. Luật lõi

- Phiên mở **trong thư mục repo**: Antigravity nạp `AGENTS.md` và `GEMINI.md` theo chuỗi thư mục. `GEMINI.md`
  của repo cố ý chỉ là **con trỏ văn xuôi** tới `AGENTS.md`: cú pháp nhúng `@[nhãn](đường-dẫn)` sẽ nạp đúp vào
  ngân sách luật đầu phiên, còn `@tên-file` trần chỉ đổi thành đường dẫn, không nhúng.
- Phiên ở **dự án khác**: file luật cấp người dùng là `~/.gemini/GEMINI.md`. Ghép nội dung `AGENTS.md` vào đó
  bằng script sinh của môi trường (không chép tay), sau khi người dùng đồng ý.

## 2. Skill

Thư mục skill toàn cục của Antigravity là `~/.gemini/antigravity/skills/`; mỗi skill là một thư mục con có
`SKILL.md`. Tạo **một liên kết thư mục cho mỗi skill** trỏ về `skills/<tên>/` của bản clone (Windows:
junction — không cần Developer Mode; macOS: symlink). Không chép thư mục: chép là có bản thứ hai và hai bản
sẽ trôi khỏi nhau.

- Tên thư mục đã có sẵn ở đích (skill cùng tên của bộ khác): **không ghi đè**, báo người dùng chọn.
- Thử nhanh không liên kết gì: mở thẳng repo làm workspace; agent đọc `skills/<tên>/SKILL.md` khi luật lõi
  bảo rà skill.

Agent reviewer trong `agents/` là thẻ vai Markdown, đọc theo brief như với Codex
([codex/README.md](../codex/README.md) mục 2).

## 3. Kiểm, cập nhật, gỡ

- **Kiểm:** phiên **mới**, hỏi "luật lõi agent-agile-team nói gì về hai cổng?" và nhờ agent dùng skill
  `intake` cho một yêu cầu thử. Trong thư mục repo: `python scripts/check.py --self` ra `Đạt`.
- **Cập nhật:** `git pull --ff-only` trong bản clone — liên kết tự thấy bản mới; skill mới thêm thì tạo
  thêm liên kết; chạy lại script sinh luật.
- **Gỡ:** xoá đúng các **liên kết** do mình tạo (không xoá thư mục đích của liên kết), bỏ phần ghép khỏi
  `~/.gemini/GEMINI.md` bằng script sinh.

Điểm cắm (bảng tier, từ cấm, nơi lưu bài học, cầu gọi chéo): [`hosts/README.md`](../README.md) mục 2.
