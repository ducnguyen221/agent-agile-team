# MIGRATION — tên cũ → tên mới, và nâng cấp giữa các bản

> **Kết luận:** hai việc. (1) Gặp tên skill hay agent cũ (`superpowers:*`, `ecc-pack:*`, `dev-process:*`) trong hồ sơ
> lịch sử — plan, PROGRESS, commit, memory — thì tra bảng ở mục 1–3 để biết thứ tương ứng trong repo này. Tên
> mới **không có tiền tố**; nhiều skill cũ gộp vào một skill mới; vài skill cũ không còn là skill (thành mẫu,
> công cụ, thẻ vai) hoặc bị bỏ. Nguồn và SHA của từng skill mới: [UPSTREAM.md](../UPSTREAM.md). (2) Dự án đang dùng
> bản `0.1`/`0.2` lên `0.3.0`: hồ sơ cũ **vẫn hợp lệ**, không phải sửa gì để `check` xanh; mục 4 liệt kê thứ
> mới có thể bật và chỗ `check` bắt chặt hơn.

Ký hiệu cột "Kiểu": **đổi tên** = một-một · **gộp** = nhiều cũ vào một mới · **thành phần khác** = không còn
là skill · **bỏ** = không mang vào · **ra ngoài** = chuyển sang bộ khác, không thuộc repo này.

## 1. Bộ Superpowers (`superpowers:*`)

| Tên cũ | Tên mới | Kiểu |
|---|---|---|
| `superpowers:brainstorming` | `shaping-spec` | đổi tên |
| `superpowers:writing-plans` | `writing-plan` | đổi tên |
| `superpowers:subagent-driven-development` | `running-sprint` | gộp |
| `superpowers:executing-plans` | `running-sprint` | gộp |
| `superpowers:dispatching-parallel-agents` | `running-sprint` (`references/parallel.md`) | gộp |
| `superpowers:finishing-a-development-branch` | `closing-sprint` | gộp |
| `superpowers:test-driven-development` | `tdd` | đổi tên |
| `superpowers:systematic-debugging` | `debugging` | đổi tên |
| `superpowers:using-git-worktrees` | `worktrees` | đổi tên |
| `superpowers:verification-before-completion` | `verify-before-done` | đổi tên |
| `superpowers:requesting-code-review` | `code-review` | gộp |
| `superpowers:receiving-code-review` | `code-review` | gộp |
| `superpowers:writing-skills` | `writing-skills` | đổi tên |
| `superpowers:diagnosing-superpowers` | `writing-skills` (`references/diagnosing.md`) | gộp |
| `superpowers:using-superpowers` | khối "dùng skill" trong `AGENTS.md` | thành phần khác |

## 2. Bộ kỹ thuật (`ecc-pack:*`) và ECC upstream

| Tên cũ | Tên mới | Kiểu |
|---|---|---|
| `ecc-pack:ecc-python-patterns` | `python` | gộp |
| `ecc-pack:ecc-python-testing` | `python` (`references/testing.md`) | gộp |
| `ecc-pack:ecc-fastapi-patterns` | `fastapi` | đổi tên |
| `ecc-pack:ecc-postgres-patterns` | `postgres` | đổi tên |
| `ecc-pack:ecc-database-migrations` | `database-migrations` | gộp |
| `ecc-pack:ecc-api-design` | `api-design` | đổi tên |
| `ecc-pack:ecc-error-handling` | `error-handling` | đổi tên |
| `ecc-pack:ecc-deployment-patterns` | `deployment` | gộp |
| `ecc-pack:ecc-docker-patterns` | `deployment` (`references/docker.md`) | gộp |
| `ecc-pack:ecc-github-ops` | `github-ops` | đổi tên |
| `ecc-pack:ecc-security-review` | `security-review` | đổi tên |
| `ecc-pack:security-audit` | `security-audit` | đổi tên |
| `ecc-pack:ecc-prompt-optimizer` | `intake` (danh mục 11 điểm thiếu ngữ cảnh) + `running-sprint/references/brief.md` | gộp |
| `ecc-pack:ecc-context-budget` | `token-economy` | gộp |
| ECC `strategic-compact` | `token-economy` | gộp |
| ECC `learn-eval` | `closing-sprint` (`references/lessons.md`) | gộp |
| `ecc-pack:ecc-knowledge-ops` | — đã rời pack trước Đợt 1; ý tương đương → `closing-sprint/references/lessons.md` + luật memory của môi trường | ra ngoài |
| agent `ecc-pack:ecc-python-reviewer` | agent `python-reviewer` | đổi tên |
| agent `ecc-pack:ecc-fastapi-reviewer` | agent `fastapi-reviewer` | đổi tên |
| agent `ecc-pack:ecc-database-reviewer` | agent `database-reviewer` (bỏ quyền Write/Edit) | đổi tên |
| agent `ecc-pack:ecc-security-reviewer` | agent `security-reviewer` | đổi tên |
| agent `ecc-pack:ecc-silent-failure-hunter` | agent `silent-failure-hunter` | đổi tên |
| agent `ecc-pack:ecc-comment-analyzer` | agent `comment-analyzer` | đổi tên |
| agent `ecc-pack:ecc-rag-pipeline-reviewer` | agent `rag-pipeline-reviewer` | đổi tên |
| `ecc-pack:ecc-brand-voice`, `ecc-pack:ecc-seo`, `ecc-pack:ecc-market-research`, agent `ecc-pack:ecc-seo-specialist` | — (bộ marketing của môi trường nguồn) | ra ngoài |
| `ecc-pack:ecc-frontend-slides`, `ecc-pack:ecc-google-workspace-ops`, `ecc-pack:literature-review`, `ecc-pack:scholar-evaluation` | — (bộ skill chung của môi trường nguồn) | ra ngoài |

## 3. Bộ quy trình phát triển (`dev-process:*`)

| Tên cũ | Tên mới | Kiểu |
|---|---|---|
| `dev-process:plan-eng-review` | `plan-review` | đổi tên |
| `dev-process:web-qa` | `web-qa` | đổi tên |
| `dev-process:bug-triager` | `bug-triage` | đổi tên |
| `dev-process:adr-writer` | `adr` | đổi tên |
| `dev-process:migration-rehearsal` | `database-migrations` (`references/rehearsal.md`) | gộp |
| `dev-process:code-review-routing` | `code-review` (định tuyến, cổng xác minh); phần săn bug không có diff → `debugging` | gộp |
| `dev-process:document-release` | `closing-sprint` (`references/docs-sync.md`) | gộp |
| `dev-process:preflight-gate` | `closing-sprint` (`references/preflight.md`) | gộp |
| `dev-process:release-notes-writer` | `closing-sprint` (`references/release-notes.md`) | gộp |
| `dev-process:sprint-orchestrator` | `method/process.md` + `scripts/init.py` + `templates/sprint/` | thành phần khác |
| `dev-process:registry-syncer` | `scripts/index.py` + `templates/registry/` | thành phần khác |
| `dev-process:openspec-proposer` | mục "Đổi hợp đồng / giao diện" của `templates/sprint/SPEC.md`; delta Thêm / Sửa / Bỏ của `templates/registry/feature-spec.md` | thành phần khác |
| `dev-process:test-mapper`, `dev-process:rtm-auditor` | thẻ `roles/executor/qa.md` (bảng phủ `FR` → `VR`) + bốn luật truy vết của `scripts/check.py`: `task-without-trace`, `report-sc-without-vr`, `report-fr-without-vr`, `xref-missing` | thành phần khác |
| `dev-process:open-code-review-delegate` | — (bản gốc nằm trong lịch sử git của môi trường nguồn) | bỏ |

## 4. Nâng cấp dự án đang dùng từ `0.1` / `0.2` lên `0.3.0`

`0.3.0` tăng MINOR theo [method/conventions.md](../method/conventions.md) mục 4.1: chỉ thêm năng lực tương thích ngược, không
đổi tên hay bỏ skill, agent, lệnh, khoá nào. Bảng tên ở mục 1–3 không có dòng mới. Cập nhật bản cài theo
[hosts/](../hosts/README.md) (Claude Code: `claude plugin marketplace update agent-agile-team` rồi
`claude plugin update agent-agile-team@agent-agile-team`; Antigravity: tạo liên kết cho skill mới thêm; Codex: chạy lại
script sinh luật). Rồi đối chiếu bảng dưới.

| Trong dự án của bạn | `0.1` / `0.2` | `0.3.0` | Phải làm gì |
|---|---|---|---|
| `.agile.json` | không có khoá `ledger` | thêm khoá `ledger.project` (rỗng = tắt); hình file sai → `check` báo `config-invalid`, `init`/`index` thoát 2 cùng thông điệp, không in traceback | **Không bắt buộc.** Khoá vắng lấy mặc định (sổ tắt). Muốn bật sổ tập trung: thêm tay `"ledger": {"project": "<tên>"}` (`init` không ghi đè file có sẵn), máy đặt `AGENT_AGILE_LEDGER`, tạo file sổ từ [templates/registry/LEDGER.md](../templates/registry/LEDGER.md) — `init` không dựng file này. Bốn luật `ledger-*` chỉ chạy khi khoá khác rỗng ([scripts/README.md](../scripts/README.md)) |
| Hồ sơ việc rất nhỏ | một `SPRINT.md` bốn phần SPEC · PLAN · PROGRESS · REPORT (`--tiny`) | một `SPRINT.md` **hai phần** Kế hoạch · Kết quả (`init --tiny`, mẫu `SPRINT-tiny.md`) | Sprint cũ **giữ nguyên** — dạng bốn phần ở cỡ rất nhỏ vẫn hợp lệ. Sprint mới dựng bằng `init --tiny` |
| Hồ sơ việc nhỏ | bốn file như cỡ vừa | một `SPRINT.md` bốn phần (`init --size small`); một reviewer khác người làm | Sprint cũ **giữ nguyên** — bốn file ở cỡ nhỏ vẫn hợp lệ. Sprint mới dựng bằng `init --size small` |
| Làm thẳng | việc rất nhỏ vẫn có hồ sơ sprint | việc 1–2 thao tác có kết quả rõ, hoặc người dùng nói rõ không cần sprint: không `RQ-` / `SPRINT.md` / dòng sổ; vẫn kiểm và báo bằng chứng | Sàn cỡ hành vi mới, sửa luồng và các vùng rủi ro vẫn áp; không chia một mục tiêu để né sprint. Test đi kèm không làm việc đổi chữ thành ba thao tác ([method/sizing.md](../method/sizing.md)) |
| Tiếp nhận | ghi yêu cầu rồi gom câu hỏi tới Cổng 1 | một tin gom: nhắc mục tiêu, phản biện có đề xuất, bậc/rủi ro từng việc, hỏi có mở sprint; chờ xác nhận rồi mới ghi một `RQ-` kèm câu trả lời | Lượt này không phải Cổng 1 và không thay hai cổng nghiệm thu. Bỏ lượt cho làm thẳng không mơ hồ hoặc người dùng nói rõ không cần sprint ([skills/intake](../skills/intake/SKILL.md)) |
| `check`: luật mới | — | `sprint-size-mismatch` (Phải sửa): `SPRINT.md` ở cỡ vừa/lớn, hoặc cỡ rất nhỏ mà dựng bốn file; `ledger-missing-row` · `ledger-stale` · `ledger-unreadable` (Phải sửa) · `ledger-unconfigured` (Ghi chú) khi có khai `ledger.project` | Hồ sơ theo đúng luật `0.2` không chạm luật mới: `SPRINT.md` khi đó chỉ dành cho cỡ rất nhỏ. Chạy `check` một lần sau nâng cấp để chắc |
| `check`: `old-scale-label` rộng hơn | chỉ xét ô bảng cột "Mức…" và chữ sau "Mức:" | thêm nhãn kiểu nguồn trong câu — `CRITICAL`/`HIGH`/`MEDIUM`/`LOW` viết hoa nguyên từ, `[HIGH]`/`[WARN]` đầu dòng, ngưỡng điểm dạng `confidence ≥ 80`; nhãn tiếng Việt thang cũ dưới cột "Mức"/"Độ nghiêm trọng" | Hồ sơ cũ có thể **mới bị báo** ở chỗ chép nguyên văn đầu ra của công cụ. Đổi sang thang chung Chặn / Phải sửa / Nên sửa / Ghi chú ([method/severity.md](../method/severity.md)); nhãn trong code span hay khối code không bị xét |
| Tự kiểm (`qa` trùng nhãn người làm) | một agent kiêm ở "việc nhỏ" ghi "tự kiểm, chưa độc lập", kết luận tối đa Đạt có điều kiện | chỉ hợp lệ ở cỡ **rất nhỏ**; cỡ nhỏ trở lên `qa` trùng nhãn người làm là Phải sửa dù có khai — `check` chỉ bắt khi không khai hoặc khai mà `verdict: pass`, phần còn lại do người đọc hồ sơ bắt ([roles/README.md](../roles/README.md)) | Sprint đang mở ở cỡ nhỏ trở lên: giao một reviewer khác người làm trước Cổng 2 |
| Việc chạm luật, secret, xác thực | một Tech Reviewer | `dual-review`: hai reviewer độc lập cùng rubric, cả hai Đạt mới Đạt; reviewer thứ hai ghi ở phần tử `note` của `roles` (`reviewer 2: <nhãn>`) | Áp từ sprint mới có `risk_tags` `rules` / `secret` / `auth` ([roles/verifier/dual-review.md](../roles/verifier/dual-review.md)). Hồ sơ cũ không phải sửa |
| Review từ cỡ vừa | theo skill `code-review` | cổng review bốn pha ([method/review-gate.md](../method/review-gate.md)): song song theo khía cạnh · gộp theo bằng chứng · kiểm đối kháng Chặn / Phải sửa · lỗi thì đóng | Không có khoá hay file mới; reviewer đọc thêm `review-gate.md` khi được brief |
| Chuẩn code | không có | `method/standards/`: 7 chuẩn chung + `python`, `typescript`, `react`, `web`; Implementer và Tech Reviewer đọc, **không** nạp vào `AGENTS.md` | Không bắt buộc; ngưỡng coverage 80 % cho code mới/sửa không đổi |
| Skill và agent mới | 28 skill · 7 agent | 32 skill · 13 agent: thêm `react`, `frontend`, `e2e-testing`, `eval-harness`; agent `code-explorer`, `code-reviewer`, `test-analyzer`, `typescript-reviewer`, `react-reviewer` (chỉ đọc) và `build-fixer` (agent duy nhất được sửa file, T2) | Cập nhật bản cài (đầu mục). Trên Codex và Antigravity, `agents/` vẫn đọc như thẻ vai trong brief |
| Số phiên bản | chưa có quy tắc | `method/conventions.md` mục 4.1: `MAJOR.MINOR.PATCH`, mỗi đợt tăng đúng một phần, `-dev` khi chưa phát hành; agent **đề xuất** mức ở Cổng 2, người dùng quyết | Áp cho dự án của bạn nếu muốn cùng quy tắc; repo này không ép |

**Nếu bạn giữ bản fork hoặc thêm skill của riêng mình** vào repo: `tests/test_skill_tests.py` của `0.3.0` bỏ miễn theo ngày —
**mọi** file thử (`tests/pressure.md`, `tests/retrieval.md`) phải có `skill_sha` (băm cây skill trừ `tests/` ở HEAD) và `tier`;
`result` và `model` theo danh sách trạng thái hợp lệ ([tests/README.md](../tests/README.md)). File thử từ `0.2` thiếu hai
khoá đó làm `pytest` đỏ cho tới khi chạy lại tệp thử và ghi đủ (cách chạy: [skills/writing-skills](../skills/writing-skills/SKILL.md),
`references/testing.md`).
