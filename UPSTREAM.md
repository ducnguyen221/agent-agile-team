# UPSTREAM — nguồn, mốc và đợt distill

Mỗi đợt distill một khối. Mỗi nguồn ghi: nhánh, SHA HEAD lúc chốt, ngày commit, giấy phép, cách dùng.
Đợt nào cũng lấy bản **mới nhất tại thời điểm distill** của nguồn. Skill distill từ nguồn nào thì
frontmatter của skill đó ghi `source` (repo, đường file, SHA) khớp bảng dưới.

Cách dùng: **chép** = chép nguyên văn được, giữ thông báo bản quyền · **ý** = chỉ viết lại ý, không chép
văn bản · **NOTICE** = chép được nhưng mang theo NOTICE Apache-2.0 · **private** = chỉ dùng khi repo còn
private, phải viết lại trước khi công khai.

**File này là nguồn sự thật duy nhất để theo dõi bản mới của mọi nguồn gốc.** Repo thay thế các bộ skill
gốc, nên môi trường dùng repo có thể không còn cài bộ nào trong số đó — không plugin, cache hay kho nào khác
báo khi nguồn gốc ra bản mới. Muốn cập nhật hay mở rộng: quay lại các nguồn trong mục "Sổ theo dõi" dưới,
so bản mới, distill và bổ sung theo [docs/updating-from-upstream.md](docs/updating-from-upstream.md).

## Sổ theo dõi nguồn gốc

Mục này giữ **trạng thái hiện tại** của từng nguồn; các khối đợt bên dưới là lịch sử chốt SHA. Cột
**Đã distill tới** = SHA mà nội dung trong repo đang bám (chỉ đổi khi distill xong một đợt) · cột **Kiểm gần
nhất** = ngày và HEAD đã xem ở lượt kiểm gần nhất (đổi cả khi lượt kiểm không lấy gì) · cột **Kiểm** = khi
nào phải xem lại nguồn này. SHA rút gọn 8 ký tự; bản đầy đủ ở khối đợt.

### Repo đã dùng hoặc đã xét

Bảng dưới có 21 nguồn dạng repo, chia theo **vai trò**: **distill** (nội dung đã vào skill/agent) · **ý**
(chỉ lấy khái niệm) · **chỉ gọi** (công cụ chạy qua `npx`) · **đã loại** (đánh giá rồi không lấy, ghi để
khỏi đánh giá lại).

| Nguồn | Vai trò | Nhận nội dung | Đã distill tới | Kiểm gần nhất | Kiểm |
|---|---|---|---|---|---|
| `obra/superpowers` | distill · chép | `shaping-spec`, `writing-plan`, `running-sprint`, `closing-sprint`, `tdd`, `debugging`, `worktrees`, `verify-before-done`, `code-review`, `writing-skills` | Đợt 1 · `8ca22dba` (`v6.4.2`) | 2026-10-03 · `8ca22dba` | mọi lượt |
| `affaan-m/ECC` (tên cũ `affaan-m/everything-claude-code`) | distill · chép | `intake`, `python`, `fastapi`, `postgres`, `database-migrations`, `api-design`, `error-handling`, `deployment`, `github-ops`, `security-review`, `token-economy`, phần bài học của `closing-sprint`; 7 agent | Đợt 1 · `c70874fa` (`v2.2.2`) | 2026-10-03 · `ef648e01` | mọi lượt — nguồn chính của Đợt 2 |
| `garrytan/gstack` | distill · chép | `plan-review`, `security-audit`, `web-qa`, phần điều tra của `debugging`, docs-sync và retro của `closing-sprint` | Đợt 1 · `96764e80` (VERSION 1.91.9.0) | 2026-10-03 · `f30b7b78` (VERSION 1.91.13.0) | mọi lượt — Đợt 2 lấy thêm `review`, `qa`, `ship` |
| `obra/superpowers-lab` | đã ghi mốc, chưa distill | — (Đợt 2: tìm hàm trùng lặp cho `code-review`) | chưa distill — mốc Đợt 1 `51111f74` | 2026-10-03 · `51111f74` | mọi lượt |
| `obra/superpowers-skills` | distill · chép | phần bổ sung của `tdd`, `debugging` | Đợt 1 · `cdcd624a` | 2026-10-03 · `cdcd624a` (còn lưu trữ) | không — repo lưu trữ từ 2025-10-14; chỉ xem còn lưu trữ không |
| `supabase/agent-skills` | distill gián tiếp (đến qua ECC) | mẫu Postgres trong `postgres`, agent `database-reviewer` | qua ECC `c70874fa`; mốc xác minh giấy phép `544bfc56` | 2026-10-03 · `c9be0e93` | khi ECC đổi phần Postgres |
| `github/spec-kit` | ý | `id-convention`, mẫu SPEC/PLAN, `shaping-spec` | ý từ `d2ddd910` (`v1.0.13`) | 2026-10-03 · `e1fa857a` (`v1.1.0`) | mọi lượt — đọc release notes |
| `Fission-AI/OpenSpec` | ý | spec sống và delta Thêm / Sửa / Bỏ (`templates/registry/feature-spec.md`, mẫu SPEC) | ý từ `3a34ea30` (`v1.14.0`) | 2026-10-03 · `2500d6da` (`v1.14.0`) | mọi lượt — đọc release notes |
| `bmad-code-org/BMAD-METHOD` | ý | thẻ vai trong `roles/` | ý từ `1cbcfa27` | 2026-10-03 · `4f61d4e7` (`v6.12.0`) | mọi lượt |
| `google/eng-practices` | ý | `roles/verifier/tech-reviewer.md` | ý từ `3bb3ec25` | 2026-10-03 · `3bb3ec25` (còn lưu trữ) | không — repo lưu trữ |
| `OWASP/ASVS` | ý | thẻ chuyên đề security, `security-review` | ý từ `2b300716` | 2026-10-03 · `2b300716` | khi ASVS ra bản mới |
| `JuliusBrussee/caveman` | ý, không cài | lối viết gọn giữa agent trong `token-economy` | ý từ `f5d72948` | 2026-10-03 · `8af1f1b9` (`v3.0.0`) | mọi lượt |
| `ccusage/ccusage` (tên cũ `ryoppippi/ccusage`) | chỉ gọi | lệnh đo token trong `token-economy` | không chép — gọi bản mới nhất | 2026-10-03 · `9bca3e84` (`v20.0.26`) | khi cú pháp lệnh đổi |
| `yamadashy/repomix` | chỉ gọi | lệnh nén repo trong `token-economy` | không chép — gọi bản mới nhất | 2026-10-03 · `0b3f82b4` | khi cú pháp lệnh đổi |
| `alibaba/open-code-review` | đã loại | — (thành phần ủy quyền cho công cụ review ngoài, Tech Reviewer có đường riêng) | — | 2026-10-03 · `a758d9cb` | không |
| `rtk-ai/rtk` | đã loại, **xét lại có điều kiện** | — (ứng viên nén output lệnh shell) | — | 2026-10-03 · `4f9015f6` nhánh `develop`, bản phát hành `v0.51.0` | khi đạt `v1.0` hoặc các issue chặn đã đóng: không bắt tool PowerShell (#1319, #1248), gỡ cài đặt xoá cả hook khác cùng matcher (#3036), cắt output im lặng (#4073, #4098) — 5 issue này còn mở ngày 2026-10-03; hook tự cho phép lệnh (#3791) đã đóng; còn ghi đè file hook của harness Codex |
| `oraios/serena` | đã loại | — | — | 2026-10-03 · `d0f7f926` (`v1.7.0`) | không, trừ khi nhu cầu đổi — nghiên cứu Đợt 1 ghi GPL, GitHub báo `NOASSERTION`: đọc LICENSE trước khi xét lại; quá nặng cho repo phương pháp |
| `mksglu/context-mode` | đã loại | — | — | 2026-10-03 · `9f3ecc8b` (`v1.0.169`) | không — nghiên cứu Đợt 1 ghi ELv2 (không phải giấy phép mở), GitHub báo `NOASSERTION` |
| `microsoft/LLMLingua` | đã loại | — | — | 2026-10-03 · `5a4c78ae` | không — MIT nhưng cần mô hình nén prompt, quá nặng cho repo phương pháp |
| `affaan-m/agentshield` | đã loại | — | — | 2026-10-03 · `b0891303` | không — ngoài phạm vi phương pháp |
| squeez | đã loại | — | — | chưa xác định repo — nghiên cứu Đợt 1 chỉ ghi tên | không; xác định repo trước nếu xét lại |

### Tài liệu web (không có commit)

Bảng dưới có 7 nguồn **tài liệu web** — không có SHA, nên cột kiểm ghi ngày đọc gần nhất.

| Nguồn | Vai trò | Nhận nội dung | Đọc gần nhất | Kiểm |
|---|---|---|---|---|
| Kiro / EARS (`kiro.dev/docs/specs/concepts/`) | ý | dạng kịch bản KHI…THÌ… trong mẫu SPEC, `shaping-spec` | 2026-10-01 | khi sửa mẫu SPEC |
| Shape Up (`basecamp.com/shapeup`) | ý, không trích | sprint một mục tiêu, giới hạn công sức trong `method/` | 2026-10-01 | khi sửa `method/sizing.md` |
| Scrum Guide 2020 (`scrumguides.org`) | ý, không chép | mục tiêu sprint, review/retro trong `method/`, mẫu REPORT | 2026-10-01 | khi có Scrum Guide bản mới |
| ISO/IEC/IEEE 29148 | ý | mã yêu cầu ổn định trong `id-convention` | 2026-10-01 | khi tiêu chuẩn ra bản mới |
| MoSCoW | ý | mức ưu tiên viết bằng chữ trong mẫu SPEC, `id-convention` | 2026-10-01 | không |
| Nguồn văn phong (BLUF, Minto/SCQ, plain language, Google dev style, Diátaxis, Microsoft style, NN/g) | ý | `response-style` | 2026-10-01 | khi sửa `response-style` |
| Tài liệu Anthropic (hướng dẫn prompting, context engineering, Claude Code output styles) | ý, chỉ trỏ link | `response-style`, `token-economy` | 2026-10-01 | mỗi lượt — hành vi harness đổi theo bản |

Nguồn **private** (không giấy phép) không theo dõi ở đây: lớp riêng của môi trường giữ bản đồ và đường theo
dõi của chúng; trong repo chúng chỉ có nhãn trung tính ở khối Đợt 1 và `THIRD_PARTY.md` mục 3.

## Nhật ký kiểm bản mới

Mỗi lượt kiểm một dòng, mới nhất trên cùng: ngày · nguồn đã kiểm · HEAD đã xem · quyết định (`lấy` / `bỏ
qua` / `hoãn` — gì, vì sao, sai thì tốn gì). Lượt kiểm không lấy gì vẫn ghi, để lần sau không đọc lại cùng
đoạn thay đổi. Cách làm: [docs/updating-from-upstream.md](docs/updating-from-upstream.md) mục 3.

- 2026-10-03 · 20 nguồn repo (đo 06:20 +07, đo lại 07:41 +07 lúc chốt Đợt 2) · ECC `ef648e01` (sau tag `v2.2.3` một
  commit tài liệu), gstack `f30b7b78` (1.91.13.0), spec-kit `e1fa857a` (`v1.1.0`), OpenSpec `2500d6da`, BMAD
  `4f61d4e7` (`v6.12.0`), supabase `c9be0e93`, caveman `8af1f1b9`, ccusage `9bca3e84` (`v20.0.26`), rtk `4f9015f6`,
  context-mode `9f3ecc8b`; superpowers, superpowers-lab, superpowers-skills, eng-practices, ASVS, repomix,
  open-code-review, Serena, LLMLingua, agentshield không đổi · **lấy:** HEAD ECC và gstack làm mốc Đợt 2 — mọi thành
  phần Đợt 2 còn ở HEAD — sai thì distill từ bản cũ hơn, tốn một lượt đối chiếu lại; ý CI gate của gstack
  `land-and-deploy` và "sửa + test hồi quy là một lựa chọn" của gstack `review`; ý "một yêu cầu một hành vi" của
  OpenSpec · **bỏ qua:** đổi tên ECC, đường state và eval của gstack, CLI/MCP spec-kit, tài liệu review của BMAD,
  release-please của supabase, caveman 3.1 (gộp 108 commit: ba skill thay sáu mức, hook, proxy — repo chỉ lấy ý lối
  viết gọn, không nhắc mức nào), 14 commit sửa `discover`/`init` của rtk, context-mode (không đọc vì giấy phép) — chỉ
  chạm runtime của nguồn, sai thì tốn đọc lại 1–108 commit · **ghi sổ:** `ryoppippi/ccusage` đổi thành
  `ccusage/ccusage`, cú pháp `npx ccusage@latest` không đổi; BMAD và ccusage LICENSE vẫn MIT (GitHub báo
  `NOASSERTION`); rtk giữ đã loại (5/6 issue chặn còn mở, #3791 đã đóng) · **không kiểm lượt này:** 7 tài liệu web —
  chỉ đọc khi sửa file nhận nội dung, Đợt 2 không sửa `response-style` hay phần Shape Up của `method/sizing.md`;
  squeez — chưa xác định repo.

## Đợt 2 — dự kiến (chưa chốt SHA)

Mục này ghi thành phần đã chọn nhưng **chưa distill**, để đợt sau khỏi phải lập lại bảng ánh xạ. Khi bắt
đầu Đợt 2: chốt HEAD mới nhất của từng nguồn thành khối "Đợt 2 — chốt SHA", rồi đối chiếu bảng dưới với bản
mới (thành phần có thể đã đổi tên, gộp hay bị xoá ở upstream). Bảng dưới chia theo **mức**: **lấy** (đã chọn)
· **xét** (chỉ lấy khi có ca dùng thật, ghi lý do lấy/bỏ).

| Nguồn | Thành phần nguồn | Đích dự kiến | Mức |
|---|---|---|---|
| `affaan-m/ECC` agent | planner, architect (+ code-architect) | `roles/executor/architect.md`, `skills/writing-plan` | lấy |
| `affaan-m/ECC` agent | code-explorer · code-reviewer (lọc theo độ tin cậy, được trả 0 phát hiện) · pr-test-analyzer · build-error-resolver (+ lệnh build-fix) | `agents/code-explorer`, `agents/code-reviewer`, `agents/test-analyzer`, `agents/build-fixer` | lấy |
| `affaan-m/ECC` agent | spec-miner · tdd-guide | `skills/shaping-spec/references/spec-mining.md` · `skills/tdd` | lấy |
| `affaan-m/ECC` agent | typescript-reviewer, react-reviewer | `agents/typescript-reviewer`, `agents/react-reviewer` | lấy |
| `affaan-m/ECC` agent | agent-evaluator, gan-*, type-design-analyzer, code-simplifier, refactor-cleaner, a11y-architect | thẻ vai / agent tương ứng | xét |
| `affaan-m/ECC` skill quy trình | orch-pipeline + 5 orch-* (+ lệnh orch-*) | `method/sizing.md` | lấy |
| `affaan-m/ECC` skill quy trình | santa-method · verification-loop · delivery-gate · loop-design-check | `roles/verifier/` · `skills/verify-before-done/references/loop.md` · `method/evidence.md` (nội dung thành luật, không dùng Stop hook) · `method/process.md` | lấy |
| `affaan-m/ECC` skill quy trình | intent-driven-development · product-capability, lệnh plan-prd, prp-* · search-first · iterative-retrieval · eval-harness | `skills/intake` · `skills/shaping-spec` · thẻ Architect và Implementer · `skills/token-economy` · `skills/eval-harness` | lấy |
| `affaan-m/ECC` workflow | `orch-review.workflow.js` | `method/review-gate.md` — chỉ lấy thiết kế, không chạy JS | lấy |
| `affaan-m/ECC` skill quy trình | blueprint, contract-first, council, inherit-legacy-style, living-docs-governance (xét trước tiên), codebase-onboarding | tuỳ ca dùng | xét |
| `affaan-m/ECC` skill kỹ thuật | react-patterns, react-testing · vite-patterns, frontend-patterns · e2e-testing, ai-regression-testing · browser-qa, click-path-audit | `skills/react` · `skills/frontend` · `skills/e2e-testing` · `skills/web-qa` | lấy |
| `affaan-m/ECC` rules | `rules/common` (coding-style, testing, security, git-workflow, code-review, development-workflow, agents) · `rules/python`, `rules/typescript`, `rules/react` | `method/standards/common/` · `method/standards/<ngôn ngữ>.md` — ngưỡng coverage giữ 80 % | lấy |
| `affaan-m/ECC` rules | `rules/web` | `method/standards/web.md` | xét |
| `affaan-m/ECC` lệnh | code-review, review-pr · test-coverage · update-docs | `skills/code-review` · thẻ QA · `skills/closing-sprint/references/docs-sync.md` | lấy |
| `garrytan/gstack` | `review` · `qa` · `ship` | `skills/code-review` · `skills/web-qa` · `skills/closing-sprint` | lấy |
| `obra/superpowers-lab` | finding-duplicate-functions | `skills/code-review/references/duplicates.md` | lấy |
| `affaan-m/ECC`, `obra/superpowers` | viết lại sâu 9 mục "gọn" của Đợt 1 có nguồn công khai: `deployment` (+ docker), `fastapi`, `postgres`, agent `fastapi-reviewer`, `database-reviewer`, `comment-analyzer`, `rag-pipeline-reviewer`; `writing-skills/references/diagnosing.md` | tại chỗ, đối chiếu HEAD mới | lấy |
| nguồn private (nhãn trung tính) | viết lại sâu 6 mục "gọn" còn lại: `bug-triage`, `adr`, `database-migrations/references/rehearsal.md`, `closing-sprint/references/release-notes.md`, bảng phủ `FR` → `VR` của thẻ QA, luật truy vết của `check` | viết lại từ ý, không mở bản gốc (`THIRD_PARTY.md` mục 3) | lấy |

## Đợt 2 — chốt SHA 2026-10-03 (07:41 UTC+7)

Trạng thái: **đã chốt, chưa distill** — nội dung Đợt 2 chỉ đọc từ đúng các SHA dưới; thành phần và đích ở mục
"Đợt 2 — dự kiến" (chuyển vào khối này khi distill xong). HEAD đo bằng lệnh của
[docs/updating-from-upstream.md](docs/updating-from-upstream.md) mục 3 bước 2; ngày commit theo giờ UTC.

### Repo mã nguồn

| Nguồn | Nhánh | SHA HEAD (ngày commit) | Tag mới nhất | Giấy phép | Cách dùng |
|---|---|---|---|---|---|
| `affaan-m/ECC` | `main` | `ef648e01899ba3e8dc6371642deaaf64b4477775` (2026-10-02) | `v2.2.3` = `c05b2d6614f62f6db0047669aa4eefb223d478f9` (HEAD sau tag một commit tài liệu) | MIT © 2026 Affaan Mustafa | chép |
| `garrytan/gstack` | `main` | `f30b7b788a210d217ea3125bf3001b29cbc2a463` (2026-10-02), `VERSION` 1.91.13.0 | không có tag | MIT © 2026 Garry Tan | chép |
| `obra/superpowers` | `main` | `8ca22dba9a94f28898bbce59f2537ff4d87c747d` (2026-09-25) — không đổi từ Đợt 1 | `v6.4.2` = cùng SHA | MIT © 2025 Jesse Vincent | chép |
| `obra/superpowers-lab` | `main` | `51111f74f24058117752d9aa917cb19859f8ec86` (2026-06-01) — không đổi từ Đợt 1 | `v0.5.0` = cùng SHA | MIT © 2025 Jesse Vincent | chép |
| `supabase/agent-skills` | `main` | `c9be0e931b7930f7d02126d04774d904c381e7d7` (2026-10-02) | `v0.1.9` = `544bfc56c89afe2b87b20017a59b2c6e9502a1fb` | MIT © 2026 Supabase | chép (đến **qua ECC**, không distill trực tiếp) |
| `github/spec-kit` | `main` | `e1fa857a7f536b22760d48c1aa9ace41df0fd1dc` (2026-10-02) | `v1.1.0` = `f1d3a4f8337ebbd3ae22760a9c12e3352b93a175` | MIT © GitHub, Inc. | ý |
| `Fission-AI/OpenSpec` | `main` | `2500d6da971336167548b53731a35b2127df35ac` (2026-10-02) | `v1.14.0` = `94ca9c1eb15d1b49c06c988419b75c3d95f8b2b5` | MIT © 2024 OpenSpec Contributors | ý |
| `bmad-code-org/BMAD-METHOD` | `main` | `4f61d4e769e50bc11d0d5d724f48942aac699679` (2026-10-02) | `v6.12.0` = `05bfbd46d00766ec88eb9b42e76be2c575d64d7b` | MIT © 2025 BMad Code, LLC (GitHub báo `NOASSERTION` vì LICENSE có đoạn mở đầu) | ý |

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
| `closing-sprint` | `obra/superpowers` — `skills/finishing-a-development-branch/`; `garrytan/gstack` — `document-release/`, `retro/`; `affaan-m/ECC` — `commands/learn-eval.md`; bộ quy trình private — `preflight-gate`; ý từ bộ quy trình private — `release-notes-writer` (`references/release-notes.md` viết lại phòng sạch từ danh sách ý, `TK10.5`, không mở bản gốc) | `8ca22dba` · `96764e80` · `c70874fa` · `4c0fdc57` · — | — | MIT; không giấy phép (`references/preflight.md`); không giấy phép, chỉ lấy ý (`references/release-notes.md`) | viết lại; private (1 file); ý (1 file) |
| `bug-triage` | ý từ bộ quy trình private — `bug-triager` (gốc private, không giấy phép); viết lại phòng sạch từ danh sách ý (`TK10.2`), không mở bản gốc | — | — | không giấy phép (chỉ lấy ý) | ý |
| `tdd` | `obra/superpowers` — `skills/test-driven-development/` (+ `writing-good-tests.md`); `obra/superpowers-skills` — `skills/testing/testing-anti-patterns/` | `8ca22dba` · `cdcd624a` | — | MIT | chép |
| `debugging` | `obra/superpowers` — `skills/systematic-debugging/`; `garrytan/gstack` — `investigate/SKILL.md.tmpl`; `obra/superpowers-skills` — `defense-in-depth`, `condition-based-waiting`; script `find-polluter.sh` viết lại thành Python | `8ca22dba` · `96764e80` · `cdcd624a` | — | MIT | chép |
| `worktrees` | `obra/superpowers` — `skills/using-git-worktrees/` | `8ca22dba` | — | MIT | chép |
| `python` | `affaan-m/ECC` — `skills/python-patterns/`, `skills/python-testing/` | `c70874fa` | `3599962a` | MIT | chép |
| `fastapi` | `affaan-m/ECC` — `skills/fastapi-patterns/` | `c70874fa` | `3599962a` | MIT | chép |
| `postgres` | `affaan-m/ECC` — `skills/postgres-patterns/` (phần mẫu từ `supabase/agent-skills`) | `c70874fa` | `3599962a` | MIT | chép |
| `database-migrations` | `affaan-m/ECC` — `skills/database-migrations/`; ý từ bộ quy trình private — `migration-rehearsal` (gốc private, không giấy phép): `references/rehearsal.md` viết lại phòng sạch từ danh sách ý (`TK10.4`), không mở bản gốc | `c70874fa` · — | `3599962a` | MIT; không giấy phép (chỉ lấy ý, `references/rehearsal.md`) | chép; ý (1 file) |
| `api-design` | `affaan-m/ECC` — `skills/api-design/` | `c70874fa` | `3599962a` | MIT | chép |
| `error-handling` | `affaan-m/ECC` — `skills/error-handling/` | `c70874fa` | `3599962a` | MIT | chép |
| `deployment` | `affaan-m/ECC` — `skills/deployment-patterns/`, `skills/docker-patterns/` | `c70874fa` | `3599962a` | MIT | chép |
| `github-ops` | `affaan-m/ECC` — `skills/github-ops/` | `c70874fa` | `3599962a` | MIT | chép |
| `adr` | ý từ bộ quy trình private — `adr-writer` (gốc private, không giấy phép); viết lại phòng sạch từ danh sách ý (`TK10.3`), không mở bản gốc | — | — | không giấy phép (chỉ lấy ý) | ý |
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
