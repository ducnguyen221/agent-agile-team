# UPSTREAM — nguồn, mốc và đợt distill

Mỗi đợt distill một khối. Mỗi nguồn ghi: nhánh, SHA HEAD lúc chốt, ngày commit, giấy phép, cách dùng.
Đợt nào cũng lấy bản **mới nhất tại thời điểm distill** của nguồn. Skill distill từ nguồn nào thì
frontmatter của skill đó ghi `source` (repo, đường file, SHA) khớp bảng dưới.

Cách dùng: **chép** = chép nguyên văn được, giữ thông báo bản quyền · **ý** = chỉ viết lại ý, không chép
văn bản · **NOTICE** = chép được nhưng mang theo NOTICE Apache-2.0 · **private** = chỉ dùng khi repo còn
private, phải viết lại trước khi công khai.

## Đợt 1 — chốt SHA 2026-10-01 (15:20–15:28 UTC+7)

Trạng thái: **đã distill** 2026-10-01 — 28 skill, 7 agent. Nguồn của từng skill và agent: mục
"Bảng nguồn theo skill và agent" cuối khối này.

### Repo mã nguồn

| Nguồn | Nhánh | SHA HEAD (ngày commit) | Tag mới nhất | Giấy phép | Cách dùng |
|---|---|---|---|---|---|
| `obra/superpowers` | `main` | `8ca22dba9a94f28898bbce59f2537ff4d87c747d` (2026-09-25) | `v6.4.2` = cùng SHA | MIT © 2025 Jesse Vincent | chép |
| `affaan-m/ECC` | `main` | `c70874fae9eb0e5ad0365beb7e2955899fd1d30f` (2026-09-30) | `v2.2.2` = cùng SHA | MIT © 2026 Affaan Mustafa | chép |
| `garrytan/gstack` | `main` | `96764e80a641e28141ec8297223768029f5bf483` (2026-09-29), `VERSION` 1.91.9.0 | không có tag | MIT © 2026 Garry Tan | chép |
| `obra/superpowers-lab` | `main` | `51111f74f24058117752d9aa917cb19859f8ec86` (2026-06-01) | `v0.5.0` = cùng SHA | MIT © 2025 Jesse Vincent | chép |
| `obra/superpowers-skills` (lưu trữ 2025-10-14) | `main` | `cdcd624ad3fd8026deb692e565351854569798dd` (2025-10-14) | không có tag | MIT © 2025 Jesse Vincent | chép (nguồn đóng băng) |
| `github/spec-kit` | `main` | `d2ddd910266ad14afe79c5414c88ee316aca6e9a` (2026-09-30) | `v1.0.13` = `f1a548a39dba4e5e8600de1d2e0d3ff0c468d2a9` | MIT © GitHub, Inc. | ý |
| `Fission-AI/OpenSpec` | `main` | `3a34ea309d80df7c5defb388133eceacb4aeba17` (2026-09-30) | `v1.14.0` = `94ca9c1eb15d1b49c06c988419b75c3d95f8b2b5` | MIT © 2024 OpenSpec Contributors | ý |
| `supabase/agent-skills` | `main` | `544bfc56c89afe2b87b20017a59b2c6e9502a1fb` (đo 2026-10-01, chỉ để xác minh giấy phép) | — | MIT © 2026 Supabase | chép (đến **qua ECC**, không distill trực tiếp) |

### Bản distill trước đó (private, ngoài repo này)

Hai bộ skill đã được distill một lần trước khi có repo này; Đợt 1 lấy chúng làm điểm xuất phát rồi đối
chiếu với HEAD ở bảng trên.

| Bộ | Mốc bản private (ngày) | Gốc upstream đã ghi | Giấy phép | Cách dùng |
|---|---|---|---|---|
| Bộ skill quy trình phát triển (15 skill) | `4c0fdc5736a49b6223a7dfc7626d5495cf55185c` (2026-09-05) | 10 skill gốc từ một bộ skill quy trình private khác (chép một chiều 2026-08-15, không giấy phép); 4 skill từ `garrytan/gstack` `656df0e37`; 1 từ `alibaba/open-code-review` (thành phần Bỏ); 1 tự viết | hỗn hợp | gốc private → **private**; gstack → chép |
| Bộ skill và agent kỹ thuật (21 skill, 8 agent) | `3599962a013653191c41676021c7e7dc519ee351` (2026-08-26) | `affaan-m/ECC` `d8409a4b0`; `security-audit` từ gstack `cso` @ `656df0e37` | MIT | chép |
| Superpowers bản đã cài | `v6.4.1` = `5bf4e78011075bcfc0dc295f0724994cd123ee71` (2026-09-18) | `obra/superpowers` | MIT | chép |

### Nguồn khái niệm (chỉ lấy ý)

| Nguồn | Mốc | Giấy phép | Cách dùng |
|---|---|---|---|
| BMAD-METHOD (`bmad-code-org/BMAD-METHOD`) | `main` `1cbcfa272fe65787c06a1fa164a901f46117cca7` (2026-09-28) | MIT © 2025 BMad Code, LLC | ý |
| Kiro / EARS | tài liệu `kiro.dev/docs/specs/concepts/` | tài liệu sản phẩm, không giấy phép mở; EARS là phương pháp công bố học thuật | ý |
| Shape Up (Basecamp) | `basecamp.com/shapeup`, đọc 2026-10-01 | giữ mọi quyền | ý, không trích |
| Scrum Guide 2020 | `scrumguides.org`, đọc 2026-10-01 | CC BY-SA 4.0 | ý, không chép |
| Google eng-practices (`google/eng-practices`, lưu trữ) | `master` `3bb3ec25b3b0199f4940b1aa75f0ac5c5753301c` (2024-09-19) | CC BY 3.0 | ý + ghi nguồn |
| OWASP ASVS (`OWASP/ASVS`) | `master` `2b300716ebbef654788d0a14d6c878cecc70c2e9` (2026-09-03) | CC BY-SA 4.0 | ý, không chép câu yêu cầu |
| Nguồn văn phong (BLUF, Minto, plain language, Google dev style, Diátaxis, Microsoft style, NN/g, hướng dẫn prompting Anthropic) | tài liệu web | nhiều loại; giấy phép từng trang chưa đọc | ý |

### Công cụ chỉ gọi, không chép

| Nguồn | Mốc | Giấy phép | Cách dùng |
|---|---|---|---|
| caveman (`JuliusBrussee/caveman`) | `main` `f5d729488caa8f6a5b6c8086fe2cccd3e8a63f91` (2026-09-30) | Apache-2.0 | ý; không cài |
| ccusage (`ryoppippi/ccusage`) | `main` `1597d65298b6ad93abc8fa174c3bcf78ae86e27a` (2026-10-01) | MIT | gọi `npx ccusage@latest` để đo |
| repomix (`yamadashy/repomix`) | `main` `0b3f82b401bbc520fd1aca67c06d24e40a868d3e` (2026-09-28) | MIT | gọi qua `npx` khi cần |
| open-code-review (`alibaba/open-code-review`) | `main` `a758d9cbfb689937c7857ad64b2dd66adb58c0c2` (2026-09-29) | Apache-2.0 | thành phần Bỏ; ghi để tra |

### Bảng nguồn theo skill và agent

SHA rút gọn 8 ký tự — bản đầy đủ ở các bảng trên; frontmatter của skill/agent ghi bản đầy đủ. Cột
`base_sha` = mốc bản distill private đã làm điểm xuất phát (`3599962a` bộ kỹ thuật, `4c0fdc57` bộ quy
trình), "—" khi distill thẳng từ HEAD. Cách dùng: **chép** = giữ nội dung nguồn (dịch, cắt, sửa theo luật
lõi) · **viết lại** = viết lại theo khung repo, giữ ý · **ý** = chỉ khái niệm · **private** = từ nguồn
không giấy phép, phải viết lại trước khi công khai (danh sách file ở `THIRD_PARTY.md`).

| Skill / agent | Nguồn (repo — đường dẫn; tên gốc) | SHA HEAD | `base_sha` | Giấy phép | Cách dùng |
|---|---|---|---|---|---|
| `intake` | `affaan-m/ECC` — `skills/prompt-optimizer` (danh mục thiếu ngữ cảnh) | `c70874fa` | `3599962a` | MIT | viết lại |
| `shaping-spec` | `obra/superpowers` — `skills/brainstorming/SKILL.md`; **tên gốc `brainstorming`** | `8ca22dba` | — | MIT | viết lại |
| `writing-plan` | `obra/superpowers` — `skills/writing-plans/SKILL.md` (v6.4.2) | `8ca22dba` | — | MIT | viết lại |
| `running-sprint` | `obra/superpowers` — `skills/subagent-driven-development/`, `skills/executing-plans/`, `skills/dispatching-parallel-agents/` | `8ca22dba` | — | MIT | viết lại |
| `closing-sprint` | `obra/superpowers` — `skills/finishing-a-development-branch/`; `garrytan/gstack` — `document-release/`, `retro/`; `affaan-m/ECC` — `commands/learn-eval.md`; bộ quy trình private — `preflight-gate`, `release-notes-writer` | `8ca22dba` · `96764e80` · `c70874fa` · `4c0fdc57` | — | MIT; không giấy phép (2 file references) | viết lại; private (2 file) |
| `bug-triage` | bộ quy trình private — `bug-triager` (gốc private, không giấy phép) | `4c0fdc57` | — | không giấy phép | private |
| `tdd` | `obra/superpowers` — `skills/test-driven-development/` (+ `writing-good-tests.md`); `obra/superpowers-skills` — `skills/testing/testing-anti-patterns/` | `8ca22dba` · `cdcd624a` | — | MIT | chép |
| `debugging` | `obra/superpowers` — `skills/systematic-debugging/`; `garrytan/gstack` — `investigate/SKILL.md.tmpl`; `obra/superpowers-skills` — `defense-in-depth`, `condition-based-waiting`; script `find-polluter.sh` viết lại thành Python | `8ca22dba` · `96764e80` · `cdcd624a` | — | MIT | chép |
| `worktrees` | `obra/superpowers` — `skills/using-git-worktrees/` | `8ca22dba` | — | MIT | chép |
| `python` | `affaan-m/ECC` — `skills/python-patterns/`, `skills/python-testing/` | `c70874fa` | `3599962a` | MIT | chép |
| `fastapi` | `affaan-m/ECC` — `skills/fastapi-patterns/` | `c70874fa` | `3599962a` | MIT | chép |
| `postgres` | `affaan-m/ECC` — `skills/postgres-patterns/` (phần mẫu từ `supabase/agent-skills`) | `c70874fa` | `3599962a` | MIT | chép |
| `database-migrations` | `affaan-m/ECC` — `skills/database-migrations/`; bộ quy trình private — `migration-rehearsal` (gốc private, không giấy phép) | `c70874fa` · `4c0fdc57` | `3599962a` | MIT; không giấy phép (`references/rehearsal.md`) | chép; private (1 file) |
| `api-design` | `affaan-m/ECC` — `skills/api-design/` | `c70874fa` | `3599962a` | MIT | chép |
| `error-handling` | `affaan-m/ECC` — `skills/error-handling/` | `c70874fa` | `3599962a` | MIT | chép |
| `deployment` | `affaan-m/ECC` — `skills/deployment-patterns/`, `skills/docker-patterns/` | `c70874fa` | `3599962a` | MIT | chép |
| `github-ops` | `affaan-m/ECC` — `skills/github-ops/` | `c70874fa` | `3599962a` | MIT | chép |
| `adr` | bộ quy trình private — `adr-writer` (gốc private, không giấy phép) | `4c0fdc57` | — | không giấy phép | private |
| `verify-before-done` | `obra/superpowers` — `skills/verification-before-completion/` | `8ca22dba` | — | MIT | chép |
| `code-review` | `obra/superpowers` — `skills/requesting-code-review/`, `skills/receiving-code-review/`; bộ quy trình private — `code-review-routing` (tự viết) | `8ca22dba` · `4c0fdc57` | — | MIT; tự viết | viết lại |
| `plan-review` | `garrytan/gstack` — `plan-eng-review/SKILL.md.tmpl`, `plan-eng-review/sections/` | `96764e80` | `4c0fdc57` | MIT | chép |
| `security-review` | `affaan-m/ECC` — `skills/security-review/` (+ `cloud-infrastructure-security.md`) | `c70874fa` | `3599962a` | MIT | chép |
| `security-audit` | `garrytan/gstack` — `cso/SKILL.md.tmpl` | `96764e80` | `3599962a` | MIT | chép |
| `web-qa` | `garrytan/gstack` — `qa-only/SKILL.md.tmpl` | `96764e80` | `4c0fdc57` | MIT | chép |
| `response-style` | nguồn văn phong (BLUF, Minto, plain language, Google dev style, Diátaxis, Microsoft style, NN/g, hướng dẫn prompting Anthropic) | — | — | nhiều loại | ý |
| `id-convention` | `github/spec-kit` (mã `US`/`FR`/`SC`); ISO/IEC/IEEE 29148; MoSCoW | `d2ddd910` | — | MIT; tiêu chuẩn có bản quyền | ý |
| `token-economy` | `affaan-m/ECC` — `skills/context-budget/`, `skills/strategic-compact/`; caveman (ý); ccusage, repomix (chỉ gọi) | `c70874fa` · `f5d72948` · `1597d652` · `0b3f82b4` | `3599962a` | MIT; Apache-2.0 (chỉ ý) | chép (ECC); ý (caveman) |
| `writing-skills` | `obra/superpowers` — `skills/writing-skills/` (+ `testing-skills-with-subagents.md`, `persuasion-principles.md`), `skills/diagnosing-superpowers/` | `8ca22dba` | — | MIT | chép |
| agent `python-reviewer` | `affaan-m/ECC` — `agents/python-reviewer.md` | `c70874fa` | `3599962a` | MIT | chép |
| agent `fastapi-reviewer` | `affaan-m/ECC` — `agents/fastapi-reviewer.md` | `c70874fa` | `3599962a` | MIT | chép |
| agent `database-reviewer` | `affaan-m/ECC` — `agents/database-reviewer.md` (phần mẫu từ `supabase/agent-skills`) | `c70874fa` | `3599962a` | MIT | chép |
| agent `security-reviewer` | `affaan-m/ECC` — `agents/security-reviewer.md` | `c70874fa` | `3599962a` | MIT | chép |
| agent `silent-failure-hunter` | `affaan-m/ECC` — `agents/silent-failure-hunter.md` | `c70874fa` | `3599962a` | MIT | chép |
| agent `comment-analyzer` | `affaan-m/ECC` — `agents/comment-analyzer.md` | `c70874fa` | `3599962a` | MIT | chép |
| agent `rag-pipeline-reviewer` | `affaan-m/ECC` — `agents/rag-pipeline-reviewer.md` | `c70874fa` | `3599962a` | MIT | chép |
