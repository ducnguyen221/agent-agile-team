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
| `source_sha` | có | SHA HEAD đã chốt ở [UPSTREAM.md](../UPSTREAM.md), cùng thứ tự với `source`; `null` cho tài liệu web không có commit, hoặc cho nguồn chỉ lấy ý (`concept:`) |
| `base_sha` | không | mốc của **bản distill private** đã làm điểm xuất phát — khuyến khích khi có, để lần distill sau đối chiếu được |
| `license` | có | giấy phép của nguồn; `none` cho nguồn không giấy phép; `source` là danh sách thì `license` là danh sách cùng độ dài, cùng thứ tự |
| `rewrite_before_public` | có | `true` khi có file lấy từ nguồn không giấy phép — phải viết lại trước khi repo công khai (file nào: [THIRD_PARTY.md](../THIRD_PARTY.md)) |

## 2. Thử áp lực

- Skill **kỷ luật/quy trình** (có luật sắt hoặc cổng — không có `metadata.kind: reference`) **bắt buộc**
  có `tests/pressure.md`: 3 kịch bản thử áp lực, chạy bằng subagent không có skill (ghi lỗi) rồi có skill
  (phải đạt). Cách viết: skill `writing-skills`, `references/testing.md`.
- Skill **tham chiếu kỹ thuật** (`metadata.kind: reference`) không kiểm áp lực mà kiểm **truy xuất** (agent
  tìm đúng mục khi cần): bắt buộc có `tests/retrieval.md` với ≥4/5 câu Đạt.
- `security-audit`, `web-qa` là skill **chỉ báo cáo** (không sửa gì); kịch bản thật cần cả một repo hoặc
  trình duyệt dựng sẵn, nên thử áp lực bằng prompt tự chứa (đã chạy ở SPR-02, xem mục 4).
- Frontmatter của `pressure.md`/`retrieval.md`: `result` và `model` là kết quả đã chạy (không phải `not run`/
  `pending`/`chưa chạy`/`dự kiến`), `date`; file từ 2026-10-03 thêm `tier` và `skill_sha` (băm cây skill trừ
  `tests/`). `tests/test_skill_tests.py` kiểm các điều này.
- `tests/scenarios.txt` (tuỳ chọn): **nguyên văn** prompt các kịch bản đã chạy, để chạy lại được. Đuôi `.txt`
  để `check` không quét như tài liệu; file chứa khoá, mật khẩu hay token làm mồi thì dòng thứ hai ghi rõ
  chúng là **GIÁ TRỊ GIẢ**.

**Hiện trạng thử:** cả 28 skill đã có tệp thử đã chạy — bảng ở mục 4.

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

## 4. Hiện trạng thử — 28 skill

Đọc từ frontmatter của tệp thử, không từ trí nhớ (`tests/test_skill_tests.py` đối chiếu bảng này với frontmatter). Tệp kỷ luật:
cột `result` là đoạn đầu (số kịch bản Đạt), chi tiết RED và GREEN ở chính tệp. Tệp truy xuất: một thước chung — `strict` là
số câu Đạt hẳn trên tổng số câu (kèm số Một phần và Không đạt), `points-right` là Đạt + Một phần (số câu trỏ đúng nơi),
`at/below threshold` là so với ngưỡng PLAN (≥4/5 câu tình huống Đạt + câu ranh giới Đạt); định nghĩa đầy đủ ở mỗi `retrieval.md`.
`below threshold` nghĩa là skill còn thiếu nội dung, không phải agent trỏ sai. `date` 2026-10-01 là lần chạy Đợt 1 (model `sonnet`, chưa ghi `tier` và
`skill_sha`); 2026-10-03 là lần chạy hoặc chạy lại ở SPR-02 trên bản skill hiện tại (`claude-sonnet-5-5`, tier T3).

| Skill | Loại | Tệp thử | `result` | `date` |
|---|---|---|---|---|
| [bug-triage](bug-triage/tests/pressure.md) | kỷ luật | `pressure.md` | 3/3 GREEN pass | 2026-10-04 |
| [closing-sprint](closing-sprint/tests/pressure.md) | kỷ luật | `pressure.md` | 11/11 GREEN pass | 2026-10-04 |
| [intake](intake/tests/pressure.md) | kỷ luật | `pressure.md` | 6/6 GREEN pass | 2026-10-04 |
| [running-sprint](running-sprint/tests/pressure.md) | kỷ luật | `pressure.md` | 6/6 GREEN pass | 2026-10-04 |
| [shaping-spec](shaping-spec/tests/pressure.md) | kỷ luật | `pressure.md` | 6/6 GREEN pass | 2026-10-04 |
| [writing-plan](writing-plan/tests/pressure.md) | kỷ luật | `pressure.md` | 3/3 GREEN pass | 2026-10-03 |
| [adr](adr/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 6/7 (+1 partial, 0 fail), at threshold; points-right 7/7 | 2026-10-04 |
| [api-design](api-design/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 3/7 (+4 partial, 0 fail), below threshold; points-right 7/7 | 2026-10-04 |
| [database-migrations](database-migrations/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 7/7 (+0 partial, 0 fail), at threshold; points-right 7/7 | 2026-10-04 |
| [debugging](debugging/tests/pressure.md) | kỷ luật | `pressure.md` | 3/3 GREEN pass | 2026-10-04 |
| [deployment](deployment/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 6/6 (+0 partial, 0 fail), at threshold; points-right 6/6 | 2026-10-04 |
| [e2e-testing](e2e-testing/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 2/7 (+5 partial, 0 fail), below threshold; points-right 7/7 | 2026-10-04 |
| [error-handling](error-handling/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 7/7 (+0 partial, 0 fail), at threshold; points-right 7/7 | 2026-10-04 |
| [fastapi](fastapi/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 7/7 (+0 partial, 0 fail), at threshold; points-right 7/7 | 2026-10-04 |
| [frontend](frontend/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 2/7 (+5 partial, 0 fail), below threshold; points-right 7/7 | 2026-10-04 |
| [github-ops](github-ops/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 7/7 (+0 partial, 0 fail), at threshold; points-right 7/7 | 2026-10-04 |
| [postgres](postgres/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 4/7 (+2 partial, 1 fail), below threshold; points-right 6/7 | 2026-10-04 |
| [python](python/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 6/6 (+0 partial, 0 fail), at threshold; points-right 6/6 | 2026-10-04 |
| [react](react/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 3/7 (+4 partial, 0 fail), below threshold; points-right 7/7 | 2026-10-04 |
| [tdd](tdd/tests/pressure.md) | kỷ luật | `pressure.md` | 4/4 GREEN pass | 2026-10-04 |
| [worktrees](worktrees/tests/retrieval.md) | tham chiếu | `retrieval.md` | strict 6/6 (+0 partial, 0 fail), at threshold; points-right 6/6 | 2026-10-04 |
| [code-review](code-review/tests/pressure.md) | kỷ luật | `pressure.md` | 6/6 GREEN pass | 2026-10-04 |
| [plan-review](plan-review/tests/pressure.md) | kỷ luật | `pressure.md` | 3/3 GREEN pass | 2026-10-04 |
| [security-audit](security-audit/tests/pressure.md) | kỷ luật | `pressure.md` | 3/3 GREEN pass | 2026-10-03 |
| [security-review](security-review/tests/pressure.md) | kỷ luật | `pressure.md` | 3/3 GREEN pass | 2026-10-04 |
| [verify-before-done](verify-before-done/tests/pressure.md) | kỷ luật | `pressure.md` | 5/5 GREEN pass | 2026-10-04 |
| [web-qa](web-qa/tests/pressure.md) | kỷ luật | `pressure.md` | 6/6 GREEN pass on the final tree (wq-1 to wq-3 rerun plus new wq-4 to wq-6) | 2026-10-04 |
| [id-convention](id-convention/tests/pressure.md) | kỷ luật | `pressure.md` | 3/3 GREEN pass | 2026-10-04 |
| [response-style](response-style/tests/pressure.md) | kỷ luật | `pressure.md` | 3/3 GREEN pass | 2026-10-04 |
| [token-economy](token-economy/tests/pressure.md) | kỷ luật | `pressure.md` | 4/4 GREEN pass | 2026-10-04 |
| [eval-harness](eval-harness/tests/pressure.md) | kỷ luật | `pressure.md` | 8/8 GREEN pass | 2026-10-04 |
| [writing-skills](writing-skills/tests/pressure.md) | kỷ luật | `pressure.md` | 3/3 GREEN pass after the TK9 rewrite; TK12 rerun: GREEN 3/3 on the old scenarios and on 4 new ones (KB5 partial against the expectation) | 2026-10-04 |

Agent reviewer chuyên đề: [agents/README.md](../agents/README.md). Gặp tên cũ trong hồ sơ lịch sử:
[docs/MIGRATION.md](../docs/MIGRATION.md).
