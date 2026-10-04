---
title: Conventions — coverage, default paths, ADR, git rules
type: method
status: active
updated: 2026-10-01
---

# Quy ước chung: coverage, đường dẫn mặc định, ADR, luật git

> **Kết luận:** một ngưỡng coverage (**80 %** cho code mới và code được sửa), một bộ đường dẫn mặc định
> (chỉnh qua cấu hình dự án), một đường ADR, và một bộ luật git không có ngoại lệ "cho nhanh".

## 1. Coverage

- Mặc định **80 % dòng** cho code **mới** và code **được sửa** trong sprint; không yêu cầu nâng toàn repo
  lên 80 % trong một sprint.
- Dự án chỉnh ngưỡng trong cấu hình dự án (`coverage.line_min_percent`) **kèm lý do** ở
  `coverage.reason`. Ngưỡng khác 80 mà lý do rỗng → `check` báo Không đạt.
- Coverage là điều kiện cần, không phải đủ: test phải gọi tên lỗi nó bắt, không assert lên mock, không
  là "change detector" (skill `tdd`, phần test tốt).
- Số coverage ghi vào `VR` kèm lệnh đo.

## 2. Đường dẫn mặc định

Chỉnh được qua cấu hình dự án (file `.agile.json` ở gốc dự án; mẫu ở `templates/project/agile.json`).
Lõi và công cụ đọc cấu hình trước, dùng mặc định sau.

| Thứ | Khoá cấu hình | Mặc định |
|---|---|---|
| Thư mục sprint | `paths.sprint_dir` | `docs/plans/{date}-{slug}/` (SPEC, PLAN, PROGRESS, REPORT — hoặc một `SPRINT.md` khi cỡ rất nhỏ hoặc nhỏ) |
| Sổ REQUESTS | `paths.requests` | `docs/plans/REQUESTS.md` |
| Sổ SPRINTS | `paths.sprints` | `docs/plans/SPRINTS.md` |
| Sổ SPECS + spec sống | `paths.specs` · `paths.feature_specs_dir` | `docs/specs/SPECS.md`, `docs/specs/<slug>.md` |
| ADR | `paths.adr_dir` | `docs/architecture/adr/NNNN-<slug>.md` |
| Sổ tập trung (tuỳ chọn) | `ledger.project` | rỗng = tắt; điền tên dự án trong sổ để bật ([process.md](process.md) mục 11); máy cấp mẫu đường kho sổ qua biến `AGENT_AGILE_LEDGER`, không ghi đường máy vào repo |
| Thư mục tạm của sprint | — | `.tmp/` (trong `.gitignore`; xoá khi đóng sprint) |

Mã hồ sơ sổ gốc: `RQ-` và `FS-` tối thiểu 3 chữ số, `SPR-` tối thiểu 2 (`id_width`). Repo **public** mà
hồ sơ sprint là nội bộ: `visibility: public` và `artifact_root` **phải** trỏ ra ngoài repo; lõi không bắt
hồ sơ phải nằm trong repo. Hợp đồng đầy đủ của cấu hình ở `templates/README.md` mục 7.

## 3. ADR — quyết định kiến trúc

- Viết ADR khi một quyết định **khó đảo ngược** hoặc ảnh hưởng nhiều phần: chọn nền tảng, đổi hợp đồng,
  đổi mô hình dữ liệu, bỏ một công nghệ. Cỡ **lớn** luôn có ít nhất một ADR hoặc ghi rõ "không có
  quyết định kiến trúc mới".
- Đánh số `NNNN` bốn chữ số tăng dần, không tái dùng, slug tiếng Anh ngắn.
- Khuôn: **Bối cảnh** (vấn đề, ràng buộc) · **Quyết định** (một câu khẳng định) · **Lựa chọn đã cân
  nhắc** (bảng cách làm · đánh đổi · khi nào chọn) · **Hệ quả** (được gì, mất gì, việc phải làm theo) ·
  **Trạng thái** (`proposed | accepted | superseded by NNNN`) · **Sprint** (`SPR-` sinh ra nó).
- ADR bị thay thì đổi trạng thái, không xoá, không sửa nội dung cũ (skill `adr`).

## 4. Luật git

Không có ngoại lệ "cho nhanh"; vi phạm là phát hiện mức **Chặn**.

| Luật | Cụ thể |
|---|---|
| **Không bỏ hook** | không `--no-verify`, không `HUSKY=0`, không tắt pre-commit. Hook hỏng → sửa nguyên nhân |
| **Không force-push** | không `push --force`, không `--force-with-lease` lên nhánh chung; viết lại lịch sử chỉ trên nhánh riêng chưa đẩy, và là điều kiện dừng (a) nếu được yêu cầu trên nhánh đã đẩy |
| **Không sửa cấu hình kiểm để qua** | không nới linter, không bỏ rule, không hạ ngưỡng coverage, không đánh dấu `skip`/`xfail` để test xanh. Đổi cấu hình kiểm là một `TK` riêng có lý do trong PLAN |
| **Không `git stash` trần** | dùng commit tạm trên nhánh làm việc, hoặc `stash push -m <tên duy nhất>` rồi `apply` theo mã (stash dùng chung giữa nhiều phiên) |
| **Không `reset --hard`, không xoá nhánh chưa gộp** | trừ khi được giao đích danh — điều kiện dừng (a) |
| **Không commit secret** | `.env*`, khoá, token; chỉ `.env.example`. Secret lọt vào diff → Chặn và báo để xoay vòng |
| **Không tự tăng version, không ghi đè CHANGELOG** | version và CHANGELOG do người dùng quyết lúc phát hành; agent chỉ **thêm** mục vào CHANGELOG dưới tiêu đề đang mở, không viết lại mục cũ |
| **Commit** | thông điệp một dòng tóm tắt + thân ngắn nêu *vì sao*; mỗi `TK` ít nhất một commit; commit ghi mã `TK` khi có |
| **Worktree** | ưu tiên công cụ worktree của harness; thư mục worktree nằm trong `.gitignore`; không `cd` sang worktree khác (skill `worktrees`) |
| **Push, PR, gộp vào nhánh chính** | tác động ra ngoài: chỉ sau Cổng 2 và khi người dùng gật; menu 3 lựa chọn ở skill `closing-sprint` |
| **Cấu hình harness và file luật** | không sửa để nới quyền cho mình; sửa qua đường chính thức của môi trường và luôn qua người dùng |

## 5. Ngôn ngữ và frontmatter

- Thân tài liệu bằng ngôn ngữ làm việc của dự án; **frontmatter tiếng Anh** (khoá và giá trị liệt kê),
  vì công cụ và harness đọc frontmatter để định tuyến.
- Frontmatter chỉ dùng tập con YAML: khoá–giá trị phẳng, danh sách inline, khối lồng một cấp (`roles`,
  `links`) — hợp đồng đầy đủ ở `templates/README.md` mục 2. Không neo, không nhiều dòng, không kiểu phức tạp.
