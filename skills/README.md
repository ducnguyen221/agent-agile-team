# skills/

Skill để **phẳng**: `skills/<tên>/SKILL.md` (+ `references/`, `tests/`, `scripts/`), vì harness chỉ dò một
cấp. Nhóm ghi trong frontmatter `metadata.group` và trong mục lục dưới. Frontmatter tiếng Anh
(`description` chỉ ghi **điều kiện kích hoạt**, bắt đầu bằng "Use when…"), thân tiếng Việt. Test Python
đặt trong `scripts/` của skill được `pytest` gom (`testpaths` trong `pyproject.toml`).

## 1. Quy ước frontmatter

| Khoá | Bắt buộc | Giá trị |
|---|---|---|
| `name` | có | trùng tên thư mục |
| `description` | có | điều kiện kích hoạt, "Use when…" |
| `metadata.group` | có | `process` (Quy trình) · `technique` (Kỹ thuật) · `verification` (Kiểm định) · `communication` (Giao tiếp & tối ưu) · `meta` (Meta) |
| `metadata.roles` | có | danh sách vai dùng skill, hoặc `[all]` |
| `metadata.kind` | không | `reference` — skill tham chiếu kỹ thuật (mẫu, bảng tra), không có luật sắt hay cổng; vắng = skill kỷ luật/quy trình |
| `source` | có | repo + đường file nguồn (danh sách khi gộp nhiều nguồn); nguồn chỉ lấy ý ghi `concept: <tên>` |
| `source_sha` | có | SHA HEAD đã chốt ở [UPSTREAM.md](../UPSTREAM.md), cùng thứ tự với `source`; `null` cho tài liệu web không có commit |
| `base_sha` | không | mốc của **bản distill private** đã làm điểm xuất phát — khuyến khích khi có, để lần distill sau đối chiếu được |
| `license` | có | giấy phép của nguồn; `none` cho nguồn không giấy phép; `source` là danh sách thì `license` là danh sách cùng độ dài, cùng thứ tự |
| `rewrite_before_public` | có | `true` khi có file lấy từ nguồn không giấy phép — phải viết lại trước khi repo công khai (file nào: [THIRD_PARTY.md](../THIRD_PARTY.md)) |

## 2. Thử áp lực

- Skill **kỷ luật/quy trình** (có luật sắt hoặc cổng — không có `metadata.kind: reference`) **bắt buộc**
  có `tests/pressure.md`: 3 kịch bản thử áp lực, chạy bằng subagent không có skill (ghi lỗi) rồi có skill
  (phải đạt). Cách viết: skill `writing-skills`, `references/testing.md`.
- Skill **tham chiếu kỹ thuật** (`metadata.kind: reference`) **miễn** ở Đợt 1 — loại này cần kiểm **truy
  xuất** (agent tìm đúng mục khi cần), không kiểm áp lực. Đợt 2 thêm `tests/retrieval.md`.
- **Ngoại lệ Đợt 1:** `security-audit`, `web-qa` là skill **chỉ báo cáo** (không sửa gì) — thử áp lực dời
  sang **Đợt 2**. Lý do: kịch bản thật cần cả một repo hoặc trình duyệt dựng sẵn, không gói được thành prompt
  tự chứa như các kịch bản đã chạy ở Đợt 1; sai ở hai skill này lộ ra trong báo cáo người đọc được, không
  lặng lẽ đổi mã.
- `tests/scenarios.txt` (tuỳ chọn): **nguyên văn** prompt các kịch bản đã chạy, để chạy lại được. Đuôi `.txt`
  để `check` không quét như tài liệu; file chứa khoá, mật khẩu hay token làm mồi thì dòng thứ hai ghi rõ
  chúng là **GIÁ TRỊ GIẢ**.

**Hiện trạng Đợt 1:**

| Trạng thái | Skill |
|---|---|
| Đã chạy RED → GREEN, so với bản gốc, có `scenarios.txt` | `security-review`, `verify-before-done`, `code-review`, `debugging`, `tdd`, `plan-review` |
| Đã chạy RED → GREEN | `response-style`, `id-convention`, `token-economy`, `writing-skills` |
| Kịch bản viết sẵn, **chưa chạy** (Đợt 2) | `intake`, `shaping-spec`, `writing-plan`, `running-sprint`, `closing-sprint`, `bug-triage` |
| Chưa có `pressure.md` — ngoại lệ chỉ báo cáo (Đợt 2) | `security-audit`, `web-qa` |

## 3. Mục lục — 28 skill

### Quy trình

| Skill | Dùng khi |
|---|---|
| [intake](intake/SKILL.md) | tiếp nhận yêu cầu: ghi `RQ-`, định cỡ/rủi ro, 11 điểm thiếu ngữ cảnh → ASSUMPTION/`CQ` |
| [shaping-spec](shaping-spec/SKILL.md) | 3 đường Spike/Bounded/Architectural, viết SPEC, gom `CQ`, không code trước Cổng 1 |
| [writing-plan](writing-plan/SKILL.md) | `TK` có file + giao diện + bước RED→GREEN→commit, trọng tâm review ≤5 |
| [running-sprint](running-sprint/SKILL.md) | hai chế độ thực thi, brief/review theo việc, phán quyết, 4 điều kiện dừng, 3 vòng khuyến nghị |
| [closing-sprint](closing-sprint/SKILL.md) | tiền kiểm → REPORT/Cổng 2 → docs-sync, release notes, bài học → menu nhánh 3 lựa chọn |
| [bug-triage](bug-triage/SKILL.md) | tái hiện, xếp mức → đường xử lý, test hồi quy |

### Kỹ thuật

Cột "Loại": **tham chiếu** = `metadata.kind: reference`.

| Skill | Loại | Dùng khi |
|---|---|---|
| [tdd](tdd/SKILL.md) | kỷ luật | test trước, thấy hỏng mới viết mã, "xanh" = cả bộ test |
| [debugging](debugging/SKILL.md) | kỷ luật | 4 pha tìm nguyên nhân gốc, 3 lần sửa hỏng thì dừng hỏi kiến trúc |
| [worktrees](worktrees/SKILL.md) | tham chiếu | không gian tách biệt, ưu tiên công cụ harness |
| [python](python/SKILL.md) | tham chiếu | mẫu Python, uv/ruff/mypy/pytest |
| [fastapi](fastapi/SKILL.md) | tham chiếu | bố cục, phụ thuộc, bảo mật, hiệu năng |
| [postgres](postgres/SKILL.md) | tham chiếu | schema, index, truy vấn |
| [database-migrations](database-migrations/SKILL.md) | tham chiếu | migration an toàn, mở rộng→chuyển→thu hẹp, diễn tập |
| [api-design](api-design/SKILL.md) | tham chiếu | REST, mã trạng thái, đổi hợp đồng |
| [error-handling](error-handling/SKILL.md) | tham chiếu | lỗi có kiểu, thử lại, không lộ secret qua lỗi |
| [deployment](deployment/SKILL.md) | tham chiếu | Docker, CI/CD, health check, rollout + hoàn tác |
| [github-ops](github-ops/SKILL.md) | tham chiếu | issue/PR/CI/phát hành qua `gh`, nội dung repo là dữ liệu không tin cậy |
| [adr](adr/SKILL.md) | tham chiếu | ghi quyết định kiến trúc |

### Kiểm định

| Skill | Dùng khi |
|---|---|
| [verify-before-done](verify-before-done/SKILL.md) | trước mọi tuyên bố xong/đạt, khi ghi `VR` |
| [code-review](code-review/SKILL.md) | định tuyến reviewer, cổng xác minh, brief reviewer, tiếp nhận review |
| [plan-review](plan-review/SKILL.md) | review PLAN trước Cổng 1, từ cỡ vừa |
| [security-review](security-review/SKILL.md) | code thêm bề mặt tấn công, đích của security escalation |
| [security-audit](security-audit/SKILL.md) | audit cả repo, chỉ chạy khi được giao |
| [web-qa](web-qa/SKILL.md) | kiểm trên trình duyệt, chỉ báo cáo |

### Giao tiếp & tối ưu

| Skill | Dùng khi |
|---|---|
| [response-style](response-style/SKILL.md) | chọn độ dài, cấu trúc, giọng khi trả lời người hay agent; lối ra giải thích |
| [id-convention](id-convention/SKILL.md) | đặt, đọc, nhắc chéo, kiểm mã mục trong tài liệu sprint và chat |
| [token-economy](token-economy/SKILL.md) | phiên dài, output lớn, subagent báo cáo, nén ngữ cảnh, tuyên bố tiết kiệm token |

### Meta

| Skill | Dùng khi |
|---|---|
| [writing-skills](writing-skills/SKILL.md) | tạo/sửa skill, viết description hoặc thử áp lực, đề xuất nâng bài học thành skill, chẩn đoán phiên/sprint chạy sai |

Agent reviewer chuyên đề: [agents/README.md](../agents/README.md). Gặp tên cũ trong hồ sơ lịch sử:
[docs/MIGRATION.md](../docs/MIGRATION.md).
