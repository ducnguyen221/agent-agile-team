# Dùng agent-agile-team với Codex

> **Kết luận:** Codex tự đọc `AGENTS.md` khi mở thư mục repo; muốn luật lõi có ở mọi dự án thì **ghép** nội
> dung `AGENTS.md` vào file luật cấp người dùng của Codex bằng một bước sinh lại được (Codex không có cú pháp
> import). Skill cài qua plugin hoặc đọc thẳng từ repo.

## 1. Luật lõi

- Phiên mở **trong thư mục repo**: Codex đọc `AGENTS.md` ở gốc theo chuỗi thư mục. Không cần làm gì thêm.
- Phiên ở **dự án khác**: file luật cấp người dùng của Codex là `~/.codex/AGENTS.md`. Ghép nội dung
  `AGENTS.md` của repo vào đó bằng **một script sinh** của môi trường (đọc repo → ghi bản sinh), không chép
  tay — chép tay thì lần cập nhật repo sau bản sinh lệch mà không ai biết. Đây là file luật của người dùng:
  agent nói rõ sẽ ghép gì, ở đâu, rồi **chờ người dùng đồng ý**.
- Kích thước: luật lõi ≤120 dòng, ≤10 KB; bản sinh cộng thêm phần đó vào mọi phiên Codex.

## 2. Skill

Chọn **một** đường:

- **A. Plugin.** Repo có manifest [`.codex-plugin/plugin.json`](../../.codex-plugin/plugin.json)
  (`skills: ./skills/`). Lệnh plugin của Codex khác nhau theo phiên bản — xem `codex plugin --help` trên máy,
  thêm marketplace từ bản clone (hoặc `https://github.com/ducnguyen221/agent-agile-team`) rồi cài `agent-agile-team`.
- **B. Mở thẳng repo.** Không cài gì; agent đọc `skills/<tên>/SKILL.md` khi luật lõi bảo rà skill. Hợp khi
  chỉ thử hoặc đang sửa repo.

Agent reviewer trong `agents/` là thẻ vai dạng Markdown: Codex không nạp chúng như agent riêng. Khi Tech
Reviewer cần một chuyên đề, brief của subagent ghi "đọc `agents/<tên>.md` rồi làm theo".

## 3. Kiểm, cập nhật, gỡ

- **Kiểm:** phiên **mới**, hỏi "luật lõi agent-agile-team nói gì về hai cổng?" và "skill nào dùng khi tiếp
  nhận yêu cầu?" — phải trả lời `intake`. Trong thư mục repo: `python scripts/check.py --self` ra `Đạt`.
- **Cập nhật:** `git pull --ff-only` trong bản clone, chạy lại script sinh ở mục 1, cài lại plugin nếu dùng
  đường A.
- **Gỡ:** gỡ plugin bằng lệnh plugin của Codex; bỏ phần ghép khỏi `~/.codex/AGENTS.md` bằng chính script sinh
  (hỏi người dùng trước).

## 4. Lưu ý

- Sandbox của Codex có thể chặn ghi ra ngoài thư mục đang mở; `init.py` ghi vào **dự án đang áp dụng**, nên
  mở Codex ở gốc dự án đó.
- Điểm cắm (bảng tier, từ cấm, nơi lưu bài học, cầu gọi chéo): [`hosts/README.md`](../README.md) mục 2.
