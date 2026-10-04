---
title: Code standards — index and standard-to-skill map
type: method
status: active
updated: 2026-10-04
---

# standards/ — chuẩn code

> **Kết luận:** chuẩn ở đây là **luật ngắn** (gạch đầu dòng, không ví dụ dài); **skill giữ mẫu code và lý do**.
> Hai bên cùng nói một điều thì chuẩn giữ câu luật, skill trỏ về chuẩn, không chép lại. Chuẩn **không** nạp vào
> `AGENTS.md`: Implementer đọc chuẩn của ngôn ngữ đang viết, Tech Reviewer đọc khi review ngôn ngữ đó. Chuẩn lệch
> luật lõi (`AGENTS.md`, `method/`) thì luật lõi thắng.

## 1. Mục lục

| File | Nói về | Bổ sung cho |
|---|---|---|
| [common/coding-style.md](common/coding-style.md) | đơn giản, dữ liệu bất biến, kích thước file và hàm, đặt tên, mùi code | — |
| [common/testing.md](common/testing.md) | ngưỡng coverage, các lớp test, test trước, test hỏng | — |
| [common/security.md](common/security.md) | danh mục trước commit, secret, xử trí khi thấy lỗ hổng | — |
| [common/git-workflow.md](common/git-workflow.md) | định dạng commit và PR | luật git ở `method/conventions.md` mục 4 |
| [common/code-review.md](common/code-review.md) | xét cái gì, quy đổi mức, kết luận | cách chạy review ở skill `code-review` |
| [common/development-workflow.md](common/development-workflow.md) | thói quen kỹ thuật trong sáu bước | `method/process.md` |
| [common/agents.md](common/agents.md) | giao việc song song, hợp đồng hoàn tất | vai và tier ở `AGENTS.md` |
| [python.md](python.md) | PEP 8, type hint, ruff, pytest, FastAPI | `common/` |
| [typescript.md](typescript.md) | kiểu, `unknown`, lỗi có kiểu, schema, Playwright | `common/` |
| [react.md](react.md) | component, state, hook, RSC, bảo mật, test | `typescript.md` |
| [web.md](web.md) | HTML/CSS, thiết kế, hiệu năng, CSP, test trình duyệt | `react.md`, `typescript.md` |

Nguồn của từng file ở comment đầu file (repo, đường dẫn, SHA, giấy phép); sổ nguồn: `UPSTREAM.md`.

## 2. Bảng đối chiếu chuẩn ↔ skill

Cột "Luật ngắn" là câu của chuẩn; "Mẫu và lý do" là nơi skill giữ. Khi sửa một câu ở một bên, rà bên kia.

| Chuẩn | Skill giữ mẫu và lý do | Điểm đã đối chiếu |
|---|---|---|
| `python.md` | `skills/python` (type hint, ngoại lệ, decorator, generator, đóng gói, pytest) | bộ công cụ uv + ruff + mypy + pytest; không công cụ định dạng thứ hai; coverage trỏ `method/conventions.md` |
| `python.md` mục FastAPI | `skills/fastapi` | `create_app()`, router mỏng, schema tách ba, `Depends`, async, CORS, JWT, ghi đè dependency khi test |
| `python.md` mục Bảo mật | `skills/security-review` | secret từ môi trường; quét bằng bộ luật bảo mật của `ruff` |
| `typescript.md` | `skills/error-handling` (`references/typescript-patterns.md`) | lỗi có kiểu, giữ nguyên nhân, schema ở biên |
| `typescript.md`, `web.md` mục Kiểm thử | `skills/web-qa` | Playwright cho luồng trọng yếu; thu bằng chứng ở skill |
| `react.md`, `web.md` | chưa có skill React hay frontend trong repo; dòng trỏ thêm khi skill vào repo | — |
| `common/coding-style.md` | `skills/error-handling`, `skills/code-review` | không nuốt lỗi; kiểm đầu vào ở biên |
| `common/testing.md` | `skills/tdd`, `skills/debugging`, `skills/verify-before-done` | một vòng đỏ → xanh → dọn; không sửa cấu hình kiểm; 80 % code mới/sửa |
| `common/security.md` | `skills/security-review`, `skills/security-audit` | cùng danh mục chín mục; lỗ hổng là mức Chặn |
| `common/git-workflow.md` | `skills/github-ops`, `skills/closing-sprint`, `skills/worktrees` | push và PR chỉ sau Cổng 2 và khi người dùng gật |
| `common/code-review.md` | `skills/code-review`, `method/severity.md` | bốn mức và ba kết luận; reviewer khác người làm |
| `common/development-workflow.md` | `skills/running-sprint`, `skills/writing-plan`, `method/process.md` | sáu bước và hai cổng không bị bỏ |
| `common/agents.md` | `skills/running-sprint`, `skills/token-economy`, `AGENTS.md` | vai · tier · model ghi vào PROGRESS; gọi chéo hãng khác chỉ khi người dùng yêu cầu |

## 3. Chỗ lệch đã xử lý

Chỗ chuẩn nguồn khác một skill hay luật lõi đã có trong repo, và cách chọn:

| Chỗ lệch | Chọn | Vì sao |
|---|---|---|
| Nguồn Python dùng black + isort + ruff; skill `python` dùng ruff cho cả định dạng và lint | ruff một công cụ (skill) | một bộ công cụ, hai định dạng chạy cùng lúc sinh thay đổi qua lại |
| Nguồn React đặt ngưỡng coverage riêng theo tầng (tiện ích, hook, component, container) | một ngưỡng **80 % code mới/sửa** (luật lõi) | luật lõi và `method/conventions.md` chỉ có một ngưỡng; dự án chỉnh qua cấu hình kèm lý do |
| Nguồn bảo gọi agent riêng mà không cần hỏi, và đưa commit rồi push vào dòng chảy làm việc | luật lõi: giao việc theo vai và tier, push sau Cổng 2 | điều khoản của `AGENTS.md` về hai cổng người và điều cấm git |
| Nguồn mô tả bốn nhãn mức và ba nhãn kết luận riêng | thang chung của repo | `method/severity.md` là nơi duy nhất quy đổi |

## 4. Giữ cho chuẩn ngắn

- Thêm luật: một câu, một gạch đầu dòng, đủ để Implementer làm đúng và reviewer chỉ ra chỗ sai; ví dụ dài đưa vào
  skill.
- Chuẩn và skill nói trái nhau là lỗi tài liệu: sửa cùng lượt, luật lõi thắng.
- File chuẩn mới theo dạng: frontmatter, comment nguồn, dòng `Kết luận`, luật gạch đầu dòng.
