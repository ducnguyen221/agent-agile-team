# agent-agile-team

> **Trạng thái: bản tiền phát hành private (`0.3.0-dev`).** Cài được trên Claude Code, Codex và
> Antigravity; chưa công khai. Bản tiếng Anh: [README.md](README.md).

Phương pháp agile cho đội agent AI. Một người giao việc bằng lời thường, xác nhận một tin trao đổi lúc tiếp
nhận (mục tiêu, bậc việc, có mở sprint không) và chỉ trả lời ở đúng hai cổng; đội agent làm phần còn lại và ghi sổ.

- **Một quy trình, sáu bước, hai cổng người:** tiếp nhận (một tin trao đổi gom: nhắc lại mục tiêu, câu hỏi phản
  biện, khuyến nghị bậc, mở sprint hay làm thẳng) → SPEC + PLAN (**Cổng 1:** duyệt / điều chỉnh) →
  thực thi ↔ kiểm định (vòng lặp, khuyến nghị 3 vòng) → REPORT (**Cổng 2:** Đạt / Đạt có điều kiện / Không
  đạt) → bài học. Việc 1–2 thao tác có kết quả rõ, hay người dùng nói "không cần sprint", thì làm thẳng, không hồ
  sơ. Agent chỉ dừng hỏi ở bốn trường hợp đã nêu tên; hỏi ngoài đó là lỗi quy trình.
- **Vai theo tier, không theo tên model:** Analyst, Architect, Implementer, QA, Business Reviewer, Tech
  Reviewer; tier `T1` tư duy · `T2` thực thi · `T3` việc vặt và chạy test. **Người làm không tự chấm.**
- **Tài liệu agent tra rẻ:** bốn tài liệu sprint (SPEC, PLAN, PROGRESS, REPORT; việc rất nhỏ dùng một
  `SPRINT.md` hai phần, việc nhỏ một `SPRINT.md` bốn phần) và ba sổ gốc dự án (yêu cầu, sprint, spec sống) có khối "Đang mở" ở đầu. Mọi mục có mã hai chữ cái
  (`FR3.2`, `TK4`, `RF2`).
- **32 skill và 13 agent** cho quy trình, kỹ thuật, kiểm định, giao tiếp và tối ưu token; agent chỉ đọc, riêng
  `build-fixer` được sửa file (T2).
- **Ba công cụ Python chỉ dùng thư viện chuẩn:** `init` dựng khung không ghi đè gì, `check` giữ chuẩn tài
  liệu, `index` sinh lại khối "Đang mở".

Lõi trung tính: không biết gì về máy, người hay dự án cụ thể nào. Môi trường dùng repo cắm vào qua năm điểm
cắm khai báo — nạp luật đầu phiên, `AGENT_AGILE_TIERS`, `AGENT_AGILE_DENYLIST`, nơi lưu bài học, cầu gọi chéo
hãng ([`hosts/README.md`](hosts/README.md)).

## Cài

Dán prompt ở cuối [INSTALL.md](INSTALL.md) cho agent; agent làm theo file đó và hỏi trước khi chạm vào máy.
Tự làm theo từng harness: [`hosts/`](hosts/README.md). Claude Code tóm tắt:

```bash
git clone https://github.com/ducnguyen221/agent-agile-team ~/agent-agile-team            # macOS, bash
claude plugin marketplace add ~/agent-agile-team
claude plugin install agent-agile-team@agent-agile-team
```

```powershell
git clone https://github.com/ducnguyen221/agent-agile-team "$HOME\agent-agile-team"      # Windows PowerShell
claude plugin marketplace add "$HOME\agent-agile-team"
claude plugin install agent-agile-team@agent-agile-team
```

rồi thêm dòng `@~/agent-agile-team/AGENTS.md` vào `~/.claude/CLAUDE.md` để luật lõi nạp ở mọi phiên. Kiểm:
`python scripts/check.py --self` kết thúc bằng `Đạt`. Lỗi hay gặp: [docs/troubleshooting.md](docs/troubleshooting.md).

## Sprint đầu tiên

[GUIDE.md](GUIDE.md) dẫn người mới đi một sprint; [`samples/order-desk/`](samples/README.md) là một dự án
sau bốn sprint. Tổng quan cả repo cho người mới (tính năng, cách hoạt động, cấu trúc, cài đặt):
[docs/OVERVIEW.md](docs/OVERVIEW.md) — cũng là trang web <https://ducnguyen.vn/agent-agile-team/>.

## Cấu trúc

| Đường dẫn | Mục đích |
|---|---|
| `AGENTS.md` | Luật lõi nạp đầu phiên (ngân sách ≤120 dòng, ≤10 KB) |
| `method/` | Quy trình, cỡ việc, thang mức, bằng chứng, quy ước, cổng review; `standards/` là các chuẩn code |
| `roles/` · `tiers/` | Thẻ vai (thực thi, kiểm định, chuyên đề); định nghĩa tier và hợp đồng bảng tier |
| `skills/` · `agents/` | Skill để phẳng (`skills/<tên>/SKILL.md`); agent (chỉ đọc, riêng `build-fixer` được sửa — T2) |
| `templates/` | Mẫu tài liệu sprint, sổ gốc, cấu hình dự án |
| `scripts/` · `tests/` · `samples/` | `init`, `check`, `index`; test; dự án mẫu kèm kết quả kỳ vọng |
| `hosts/` | Cài và nạp theo từng harness, điểm cắm của lớp riêng |
| `docs/` | Tổng quan repo; bảng tên cũ → tên mới; hồ sơ áp khuôn chuẩn hóa; xử lý sự cố; cập nhật từ nguồn gốc |

## Ghi nhận

Distill từ Superpowers (obra), Everything Claude Code (affaan-m), gstack (garrytan), lấy ý từ GitHub Spec
Kit, OpenSpec, BMAD-METHOD và Kiro/EARS. Commit chính xác, giấy phép và nguồn từng skill:
[UPSTREAM.md](UPSTREAM.md), [NOTICE](NOTICE), [THIRD_PARTY.md](THIRD_PARTY.md). Cập nhật hay mở rộng từ
các nguồn đó: [docs/updating-from-upstream.md](docs/updating-from-upstream.md).

## Giấy phép

Chưa chọn; giữ mọi quyền trong thời gian private ([LICENSE](LICENSE)). Nội dung bên thứ ba giữ giấy phép gốc.

## Tác giả

Nguyễn Quang Đức — <https://ducnguyen.vn>. Repo: <https://github.com/ducnguyen221/agent-agile-team> (private).
