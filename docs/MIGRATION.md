# MIGRATION — tên cũ → tên mới

> **Kết luận:** gặp tên skill hay agent cũ (`superpowers:*`, `ecc-pack:*`, `dev-process:*`) trong hồ sơ
> lịch sử — plan, PROGRESS, commit, memory — thì tra bảng dưới để biết thứ tương ứng trong repo này. Tên
> mới **không có tiền tố**; nhiều skill cũ gộp vào một skill mới; vài skill cũ không còn là skill (thành mẫu,
> công cụ, thẻ vai) hoặc bị bỏ. Nguồn và SHA của từng skill mới: [UPSTREAM.md](../UPSTREAM.md).

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
