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
nào phải xem lại nguồn này. SHA rút gọn 8 ký tự; bản đầy đủ ở khối đợt, trừ bảy mốc chưa ghi bản đầy đủ ở đâu: caveman `aeb45e2f`, ccusage `f28658eb` (chỉ lấy ý / chỉ gọi; đo 2026-10-04) và rtk `c356374f` (đo 2026-10-04), context-mode `dbfa57d5` (đo 2026-10-04), Serena `d0f7f926`, LLMLingua `5a4c78ae`, agentshield `b0891303` (đo 2026-10-03) — năm mốc sau cùng đã loại — cần bản đầy đủ thì đo lại từ GitHub.

### Repo đã dùng hoặc đã xét

Bảng dưới có 21 nguồn dạng repo, chia theo **vai trò**: **distill** (nội dung đã vào skill/agent) · **ý**
(chỉ lấy khái niệm) · **chỉ gọi** (công cụ chạy qua `npx`) · **đã loại** (đánh giá rồi không lấy, ghi để
khỏi đánh giá lại).

| Nguồn | Vai trò | Nhận nội dung | Đã distill tới | Kiểm gần nhất | Kiểm |
|---|---|---|---|---|---|
| `obra/superpowers` | distill · chép | `shaping-spec`, `writing-plan`, `running-sprint`, `closing-sprint`, `tdd`, `debugging`, `worktrees`, `verify-before-done`, `code-review`, `writing-skills` | Đợt 1 · `8ca22dba` (`v6.4.2`); SPR-02 viết lại sâu `references/diagnosing.md` của `writing-skills`, cùng SHA | 2026-10-04 · `8ca22dba` | mọi lượt |
| `affaan-m/ECC` (tên cũ `affaan-m/everything-claude-code`) | distill · chép | `intake`, `python`, `fastapi`, `postgres`, `database-migrations`, `api-design`, `error-handling`, `deployment`, `github-ops`, `security-review`, `token-economy`, phần bài học của `closing-sprint`; 7 agent | Đợt 1 · `c70874fa` (`v2.2.2`); SPR-02 viết lại sâu 7 mục trên `ef648e01`: `deployment` (+ `references/docker.md`), `fastapi`, `postgres`, agent `fastapi-reviewer`, `database-reviewer`, `comment-analyzer`, `rag-pipeline-reviewer`; Đợt 2 · `ef648e01` (SPR-04): 6 agent mới, `method/standards/**` (`rules/*`), 4 skill mới (`react`, `frontend`, `e2e-testing`, `eval-harness`), luồng orch, `santa-method`, `verification-loop`, `delivery-gate`, `loop-design-check`, `living-docs-governance`, `spec-miner`, `tdd-guide`, `iterative-retrieval`, `browser-qa`, `click-path-audit`, các lệnh `code-review`, `review-pr`, `test-coverage`, `update-docs`, `build-fix` — chi tiết ở khối Đợt 2 | 2026-10-04 · `ef648e01` | mọi lượt — nguồn chính của Đợt 2 và Đợt 3 |
| `garrytan/gstack` | distill · chép | `plan-review`, `security-audit`, `web-qa`, phần điều tra của `debugging`, docs-sync và retro của `closing-sprint`; Đợt 2: `review` (`code-review`), `qa` (`web-qa`), `ship` và `land-and-deploy` (`closing-sprint`) | Đợt 1 · `96764e80` (VERSION 1.91.9.0); Đợt 2 · `f30b7b78` (VERSION 1.91.13.0, SPR-04) | 2026-10-04 · `fe6d1ae6` (VERSION 1.91.17.0) | mọi lượt — còn ý luật dừng mới của `qa` (HEAD sau mốc) và checklist Pass 1/2 của `review` ở Đợt 3 |
| `obra/superpowers-lab` | distill · chép | `finding-duplicate-functions` → `skills/code-review/references/duplicates.md` | Đợt 2 · `51111f74` (`v0.5.0`, SPR-04) | 2026-10-04 · `51111f74` | mọi lượt |
| `obra/superpowers-skills` | distill · chép | phần bổ sung của `tdd`, `debugging` | Đợt 1 · `cdcd624a` | 2026-10-04 · `cdcd624a` (còn lưu trữ) | không — repo lưu trữ từ 2025-10-14; chỉ xem còn lưu trữ không |
| `supabase/agent-skills` | distill gián tiếp (đến qua ECC) | mẫu Postgres trong `postgres`, agent `database-reviewer` | qua ECC `c70874fa`; riêng `postgres` và `database-reviewer` qua ECC `ef648e01` (SPR-02); mốc xác minh giấy phép `544bfc56` | 2026-10-04 · `c9be0e93` | khi ECC đổi phần Postgres |
| `github/spec-kit` | ý | `id-convention`, mẫu SPEC/PLAN, `shaping-spec` | ý từ `d2ddd910` (`v1.0.13`) | 2026-10-04 · `ae5ade72` (`v1.1.0`) | mọi lượt — đọc release notes |
| `Fission-AI/OpenSpec` | ý | spec sống và delta Thêm / Sửa / Bỏ (`templates/registry/feature-spec.md`, mẫu SPEC) | ý từ `3a34ea30` (`v1.14.0`) | 2026-10-04 · `2500d6da` (`v1.14.0`) | mọi lượt — đọc release notes |
| `bmad-code-org/BMAD-METHOD` | ý | thẻ vai trong `roles/` | ý từ `1cbcfa27` | 2026-10-04 · `3cae711e` (`v6.12.0`) | mọi lượt |
| `google/eng-practices` | ý | `roles/verifier/tech-reviewer.md` | ý từ `3bb3ec25` | 2026-10-04 · `3bb3ec25` (còn lưu trữ) | không — repo lưu trữ |
| `OWASP/ASVS` | ý | thẻ chuyên đề security, `security-review` | ý từ `2b300716` | 2026-10-04 · `2b300716` | khi ASVS ra bản mới |
| `JuliusBrussee/caveman` | ý, không cài | lối viết gọn giữa agent trong `token-economy` | ý từ `f5d72948` | 2026-10-04 · `aeb45e2f` (sau tag `v3.1.0`) | mọi lượt |
| `ccusage/ccusage` (tên cũ `ryoppippi/ccusage`) | chỉ gọi | lệnh đo token trong `token-economy` | không chép — gọi bản mới nhất | 2026-10-04 · `f28658eb` (`v20.0.26`) | khi cú pháp lệnh đổi |
| `yamadashy/repomix` | chỉ gọi | lệnh nén repo trong `token-economy` | không chép — gọi bản mới nhất | 2026-10-04 · `8d642912` | khi cú pháp lệnh đổi |
| `alibaba/open-code-review` | đã loại | — (thành phần ủy quyền cho công cụ review ngoài, Tech Reviewer có đường riêng) | — | 2026-10-04 · `a758d9cb` | không |
| `rtk-ai/rtk` | đã loại, **xét lại có điều kiện** | — (ứng viên nén output lệnh shell) | — | 2026-10-04 · `c356374f` nhánh `develop`, bản phát hành `v0.51.0` | khi đạt `v1.0` hoặc các issue chặn đã đóng: không bắt tool PowerShell (#1319, #1248), gỡ cài đặt xoá cả hook khác cùng matcher (#3036), cắt output im lặng (#4073, #4098) — 5 issue này còn mở ngày 2026-10-04; hook tự cho phép lệnh (#3791) đã đóng; còn ghi đè file hook của harness Codex |
| `oraios/serena` | đã loại | — | — | 2026-10-04 · `d0f7f926` (`v1.7.0`) | không, trừ khi nhu cầu đổi — nghiên cứu Đợt 1 ghi GPL, GitHub báo `NOASSERTION`: đọc LICENSE trước khi xét lại; quá nặng cho repo phương pháp |
| `mksglu/context-mode` | đã loại | — | — | 2026-10-04 · `dbfa57d5` (`v1.0.169`) | không — nghiên cứu Đợt 1 ghi ELv2 (không phải giấy phép mở), GitHub báo `NOASSERTION` |
| `microsoft/LLMLingua` | đã loại | — | — | 2026-10-04 · `5a4c78ae` | không — MIT nhưng cần mô hình nén prompt, quá nặng cho repo phương pháp |
| `affaan-m/agentshield` | đã loại | — | — | 2026-10-04 · `b0891303` | không — ngoài phạm vi phương pháp |
| squeez | đã loại | — | — | chưa xác định repo — nghiên cứu Đợt 1 chỉ ghi tên | không; xác định repo trước nếu xét lại |

### Tài liệu web (không có commit)

Bảng dưới có 9 nhóm nguồn **tài liệu web** — không có SHA, nên cột kiểm ghi ngày đọc gần nhất.

| Nguồn | Vai trò | Nhận nội dung | Đọc gần nhất | Kiểm |
|---|---|---|---|---|
| Kiro / EARS (`kiro.dev/docs/specs/concepts/`) | ý | dạng kịch bản KHI…THÌ… trong mẫu SPEC, `shaping-spec` | 2026-10-01 | khi sửa mẫu SPEC |
| Shape Up (`basecamp.com/shapeup`) | ý, không trích | sprint một mục tiêu, giới hạn công sức trong `method/` | 2026-10-01 | khi sửa `method/sizing.md` |
| Scrum Guide 2020 (`scrumguides.org`) | ý, không chép | mục tiêu sprint, review/retro trong `method/`, mẫu REPORT | 2026-10-01 | khi có Scrum Guide bản mới |
| ISO/IEC/IEEE 29148 | ý | mã yêu cầu ổn định trong `id-convention` | 2026-10-01 | khi tiêu chuẩn ra bản mới |
| MoSCoW | ý | mức ưu tiên viết bằng chữ trong mẫu SPEC, `id-convention` | 2026-10-01 | không |
| Nguồn văn phong (BLUF, Minto/SCQ, plain language, Google dev style, Diátaxis, Microsoft style, NN/g) | ý | `response-style` | 2026-10-01 | khi sửa `response-style` |
| Tài liệu Anthropic (hướng dẫn prompting, context engineering, Claude Code output styles) | ý, chỉ trỏ link | `response-style`, `token-economy` | 2026-10-01 | mỗi lượt — hành vi harness đổi theo bản |
| Tài liệu chính thức của công cụ (`gh`, PostgreSQL, PgBouncer, golang-migrate, Kubernetes, Docker, Trivy, FastAPI, pytest, PyPA, uv, docs.python.org) | ý, không chép | phần bổ sung của skill kỹ thuật ở `TK11`/`TK13` (`github-ops`, `database-migrations`, `deployment`, `fastapi`, `postgres`, `python`, `worktrees`, `react`, `frontend`, `e2e-testing`) | 2026-10-04 | khi sửa reference tương ứng; nguồn ghi ở mục Nguồn từng file |
| Bài kỹ thuật của nhà cung cấp (Azure Architecture Center, AWS Builders' Library, Amazon SQS) | ý, không chép | `error-handling`, `deployment` | 2026-10-04 | khi sửa reference tương ứng |

Nguồn **private** (không giấy phép) không theo dõi ở đây: lớp riêng của môi trường giữ bản đồ và đường theo
dõi của chúng; trong repo chúng chỉ có nhãn trung tính ở khối Đợt 1 và `THIRD_PARTY.md` mục 3. SPR-02 đã viết lại 7 đích từ danh sách ý lấy từ nguồn private nhưng còn mang một số câu chữ nguồn; `SPR-04` (`TK10`) **viết lại phòng sạch** đúng 7 đích đó: bản cũ gỡ khỏi cây trước, người viết mới chỉ nhận danh sách ý dạng cụm danh từ (máy kiểm từng dòng), không mở bản cũ, để lại nhật ký đường đã đọc; 8-gram so với cả gốc private lẫn bản trước đó bằng 0 trên phần viết lại, sau khi loại stoplist cụm chung. Đích: `bug-triage`, `adr`, `database-migrations/references/rehearsal.md`, `closing-sprint/references/release-notes.md` và `preflight.md`, bảng phủ `FR` → `VR` của thẻ QA, bốn luật truy vết trong `scripts/README.md`. Các skill đó ghi nguồn ý dạng `concept:` (`source_sha` rỗng, `license: none`); cờ `rewrite_before_public` là `false` và không còn file nào chờ viết lại (`THIRD_PARTY.md` mục 3).

## Nhật ký kiểm bản mới

Mỗi lượt kiểm một dòng, mới nhất trên cùng: ngày · nguồn đã kiểm · HEAD đã xem · quyết định (`lấy` / `bỏ
qua` / `hoãn` — gì, vì sao, sai thì tốn gì). Lượt kiểm không lấy gì vẫn ghi, để lần sau không đọc lại cùng
đoạn thay đổi. Cách làm: [docs/updating-from-upstream.md](docs/updating-from-upstream.md) mục 3.

- 2026-10-04 · 20 nguồn repo (đo đầu SPR-04, trước mọi sửa) · gstack `fe6d1ae6` (1.91.17.0, 3 commit sau mốc), spec-kit
  `ae5ade72` (hai commit tự huỷ nhau, 0 file đổi), BMAD `3cae711e` (10 commit, 49 file — chỉ `bmad-ticket`, `bmad-build`),
  caveman `aeb45e2f` (12 commit sau tag `v3.1.0`), ccusage `f28658eb` (26 commit chỉ cập nhật bảng giá), repomix `8d642912`
  (12 commit chỉ nâng phụ thuộc), rtk `c356374f` (22 commit, 12 file), context-mode `dbfa57d5` (1 commit số liệu cài);
  ECC `ef648e01` (`v2.2.3`), superpowers, superpowers-lab, superpowers-skills, supabase, OpenSpec, eng-practices, ASVS,
  open-code-review, Serena, LLMLingua, agentshield không đổi · **giữ mốc Đợt 2:** gstack `f30b7b78` và ECC `ef648e01`
  — 3 commit gstack chạm `review`, `qa`, `ship`, `land-and-deploy` nhưng chỉ ở phần mở đầu chạy trên môi trường của nguồn,
  đường lưu state và vài chữ; còn hai đổi nhỏ ở nội dung `qa` (quy tắc dừng khi tự sửa bớt thang phần trăm, `--quick` chọn cả
  mức sửa lẫn mức khám phá) và nhịp chờ CI của `land-and-deploy` (4 phút mỗi vòng ở bước 3), không đủ để đổi mốc — sai thì
  tốn viết lại một đoạn khi distill, ghi trong báo cáo `TK1` để người distill `web-qa` và `closing-sprint` cân nhắc ·
  **bỏ qua:** BMAD `bmad-ticket`/`bmad-build` (repo chỉ lấy ý thẻ vai), caveman (pi/MCP của nguồn), ccusage (bảng giá),
  repomix (phụ thuộc), rtk (sửa lệnh `curl`/`go`/`diff`/`jest`, tài liệu Windows), context-mode (không đọc vì giấy phép),
  spec-kit (không đổi ròng) — chỉ chạm runtime hoặc ngoài phạm vi, sai thì tốn đọc lại 1–26 commit · **ghi sổ:** rtk
  giữ đã loại (#1319, #1248, #3036, #4073, #4098 còn mở, #3791 đã đóng); không có nguồn đổi tên, đổi giấy phép hay lưu
  trữ mới · **không kiểm lượt này:** 7 tài liệu web và squeez như lượt trước. Chi tiết: `evidence/TK1/upstream-check.md`
  của sprint SPR-04 (hồ sơ riêng của chủ repo).

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

## Đợt 3 — dự kiến (chưa chốt SHA)

Mục này ghi thành phần đã xét ở Đợt 2 nhưng **chưa distill**, để đợt sau khỏi lập lại bảng ánh xạ. Khi bắt đầu Đợt 3: chốt
HEAD mới nhất của từng nguồn thành khối "Đợt 3 — chốt SHA", rồi đối chiếu bảng dưới với bản mới (thành phần có thể đã đổi
tên, gộp hay bị xoá ở upstream). Cột **Vì sao hoãn** ghi lý do và điều kiện lấy; hoãn là **Không làm đợt này**, không phải bỏ.

| Nguồn | Thành phần nguồn | Đích dự kiến | Vì sao hoãn |
|---|---|---|---|
| `affaan-m/ECC` agent | agent-evaluator | thẻ vai hoặc agent chấm agent | `writing-skills` đã có RED/GREEN bằng subagent; chưa có ca chấm agent ngoài đó |
| `affaan-m/ECC` agent | type-design-analyzer | `agents/` (phân tích thiết kế kiểu) | chưa có sprint cần phân tích thiết kế kiểu; `typescript-reviewer` phủ phần thường gặp |
| `affaan-m/ECC` agent | refactor-cleaner | đi qua `code-review` + `references/duplicates.md` | chưa có ca dọn mã chết |
| `affaan-m/ECC` skill | council | bước cân nhắc quyết định mơ hồ | bốn giọng cùng hãng (giọng chính + 3 subagent); repo đã có bảng lựa chọn có khuyến nghị và Bước 0 của `plan-review`; chưa có ca cần thêm 3 subagent mỗi quyết định |
| `affaan-m/ECC` skill | `product-capability` — bản kê capability; `intent-driven-development` — Full Acceptance Brief | `skills/intake`, `skills/shaping-spec` | Đợt 2 chỉ lấy hai ý vào `intake` (luật nghiệp vụ không đọc được từ mã; tiêu chí nghiệm thu quan sát được); hai bản mẫu sinh thêm tài liệu thứ hai nên chưa lấy |
| `affaan-m/ECC` lệnh | `plan-prd`, `prp-*` (`prp-prd`, `prp-plan`, `prp-implement`, `prp-commit`, `prp-pr`) | `skills/shaping-spec`, `skills/writing-plan` | trùng SPEC/PLAN/`running-sprint` của repo; `prp-commit`, `prp-pr` là hành động ra ngoài, thuộc cổng người |
| `affaan-m/ECC` agent | phần eval-driven của `tdd-guide` | `skills/eval-harness` | thuộc `eval-harness`; chưa lấy vào `tdd` |
| `garrytan/gstack` | ý luật dừng mới của `qa` (nằm sau mốc `f30b7b78`, thấy ở lượt kiểm 2026-10-04 `fe6d1ae6`: quy tắc dừng khi tự sửa bớt thang phần trăm; `--quick` chọn cả mức sửa lẫn mức khám phá) | `skills/web-qa` | `web-qa` giữ "chỉ báo cáo" nên phần tự sửa không dùng; phần còn lại chưa đủ để đổi mốc; đo lại ở HEAD lúc chốt Đợt 3 |
| `garrytan/gstack` | checklist Pass 1/2 và Suppressions của `review` | `skills/code-review` | danh mục lỗi không trái luật lõi nhưng chưa có RED chứng minh `code-review` thiếu; lấy khi một sprint cho thấy chỗ hổng |

## Đợt 2 — chốt SHA 2026-10-03 (07:41 UTC+7)

Trạng thái: **đã distill** — `SPR-02` làm cứng Đợt 1 (viết lại sâu 9 mục trên ECC `ef648e01` và superpowers `8ca22dba`), `SPR-04` distill phần nội dung mới của Đợt 2 và viết lại phòng sạch 7 đích private (`TK10`). Nội dung Đợt 2 chỉ đọc từ đúng các SHA dưới; thành phần và nơi chúng đã đi ở bảng "Thành phần Đợt 2" cuối khối này, phần chưa lấy ở mục "Đợt 3 — dự kiến". HEAD đo bằng lệnh của [docs/updating-from-upstream.md](docs/updating-from-upstream.md) mục 3 bước 2; ngày commit theo giờ UTC.

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

### Thành phần Đợt 2 và nơi chúng đã đi

Bảng chuyển từ mục "Đợt 2 — dự kiến" cũ: mỗi dòng ghi đích đã làm (hoặc phán quyết) và việc của `SPR-04` (`TK`) đã làm.
**Đã làm** = nội dung đã vào repo; **đã thay** = repo có sẵn thứ thay thế, không chép; **bỏ qua** = đã xét, không lấy, lý do ở
cột đích; **hoãn** = sang "Đợt 3 — dự kiến". Câu nguồn trái luật lõi đã bị bỏ, ghi ở báo cáo từng `TK` của hồ sơ sprint
(hồ sơ riêng của chủ repo). Bảng nguồn từng skill/agent (frontmatter) ở mục "Bảng nguồn theo skill và agent" dưới.

| Nguồn | Thành phần nguồn | Đích | Trạng thái |
|---|---|---|---|
| `affaan-m/ECC` agent | planner, architect, code-architect, search-first | `roles/executor/architect.md` (tìm cái có sẵn, lát giao được, ưu/nhược), `roles/executor/implementer.md`; `skills/writing-plan` đạt sẵn ở RED wp-4 nên không sửa | đã làm (`TK5.1`, `TK5.5`) |
| `affaan-m/ECC` agent | inherit-legacy-style | `roles/executor/implementer.md` (theo phong cách file đang có, theo đa số, ghi `Phán quyết:`) | đã làm (`TK5.1`) |
| `affaan-m/ECC` agent | code-explorer, code-reviewer (+ lệnh `code-review`), pr-test-analyzer, build-error-resolver (+ lệnh `build-fix`), typescript-reviewer, react-reviewer | `agents/code-explorer`, `code-reviewer`, `test-analyzer`, `build-fixer`, `typescript-reviewer`, `react-reviewer` — agent chỉ đọc, riêng `build-fixer` được sửa (T2) | đã làm (`TK6`, `TK7`) |
| `affaan-m/ECC` agent | spec-miner | `skills/shaping-spec/references/spec-mining.md` | đã làm (`TK5.2`) |
| `affaan-m/ECC` agent | tdd-guide | `skills/tdd` (phần eval-driven chưa lấy: Đợt 3) | đã làm (`TK5.4`) |
| `affaan-m/ECC` agent | a11y-architect | `roles/verifier/specialists/frontend.md` mục 9 (WCAG 2.2 AA) | đã làm, lấy gọn (`TK8.5`) |
| `affaan-m/ECC` agent | agent-evaluator, type-design-analyzer, refactor-cleaner | — | hoãn (Đợt 3) |
| `affaan-m/ECC` agent | gan-* (planner, generator, evaluator), code-simplifier | — (ý vòng sinh ↔ chấm đã ở `method/process.md`; code-simplifier trùng `code-review` và luật sửa tối thiểu) | bỏ qua |
| `affaan-m/ECC` skill quy trình | orch-pipeline + 5 orch-* (+ lệnh orch-*) | `method/sizing.md` mục 5 (luồng ↔ bậc việc ↔ cổng), `method/process.md` mục 6.1 | đã làm (`TK4.1`, `TK4.2`) |
| `affaan-m/ECC` skill quy trình | santa-method | `roles/verifier/dual-review.md` | đã làm (`TK4.5`) |
| `affaan-m/ECC` skill quy trình | verification-loop | `skills/verify-before-done/references/loop.md` | đã làm (`TK4.6`) |
| `affaan-m/ECC` skill quy trình | delivery-gate | `method/evidence.md` mục 8 — nội dung thành luật văn bản, không dùng Stop hook | đã làm (`TK4.3`) |
| `affaan-m/ECC` skill quy trình | loop-design-check | `method/process.md` mục 6.1 | đã làm (`TK4.2`) |
| `affaan-m/ECC` skill quy trình | intent-driven-development, product-capability | `skills/intake` (hai ý: luật nghiệp vụ không đọc được từ mã, tiêu chí nghiệm thu quan sát được) | đã làm, lấy ý (`TK5.3`); Full Acceptance Brief và bản kê capability: hoãn |
| `affaan-m/ECC` skill quy trình | iterative-retrieval | `skills/token-economy` mục 7 | đã làm (`TK9.5`) |
| `affaan-m/ECC` skill quy trình | eval-harness | `skills/eval-harness` (skill mới, kỷ luật) | đã làm (`TK9.4`) |
| `affaan-m/ECC` workflow | `orch-review.workflow.js` | `method/review-gate.md` — chỉ lấy thiết kế, không chạy JS | đã làm (`TK4.4`) |
| `affaan-m/ECC` skill quy trình | living-docs-governance | `templates/registry/feature-spec.md`, `skills/closing-sprint/references/docs-sync.md` mục 11 | đã làm (`TK4.7`, `TK9.2`) |
| `affaan-m/ECC` skill quy trình | blueprint, contract-first, codebase-onboarding | — (trùng `writing-plan`; trùng mục "Đổi hợp đồng / giao diện" của mẫu SPEC và `api-design`; `code-explorer` và bước tra repo của `intake` phủ) | bỏ qua |
| `affaan-m/ECC` skill quy trình | council | — | hoãn (Đợt 3) |
| `affaan-m/ECC` skill kỹ thuật | react-patterns, react-testing | `skills/react` (+ `references/testing.md`) | đã làm (`TK8.1`) |
| `affaan-m/ECC` skill kỹ thuật | frontend-patterns, vite-patterns | `skills/frontend` (+ `references/vite.md`) | đã làm (`TK8.2`) |
| `affaan-m/ECC` skill kỹ thuật | e2e-testing, ai-regression-testing | `skills/e2e-testing` (+ `references/ai-regression.md`) | đã làm (`TK8.3`) |
| `affaan-m/ECC` skill kỹ thuật | browser-qa, click-path-audit | `skills/web-qa` (giữ "chỉ báo cáo") | đã làm (`TK8.4`) |
| `affaan-m/ECC` rules | `rules/common` (coding-style, testing, security, git-workflow, code-review, development-workflow, agents), `rules/python`, `rules/typescript`, `rules/react` | `method/standards/common/` (7 file), `method/standards/python.md`, `typescript.md`, `react.md` — ngưỡng coverage giữ 80 %; không nạp vào `AGENTS.md` | đã làm (`TK6`) |
| `affaan-m/ECC` rules | `rules/web` | `method/standards/web.md` | đã làm (`TK6.5`) |
| `affaan-m/ECC` lệnh | code-review, review-pr | `skills/code-review` (chỉ đối chiếu; chưa có câu nào được chép vào skill — khớp dòng `code-review` ở bảng nguồn) | đã đối chiếu, chưa chép (`TK9.1`) |
| `affaan-m/ECC` lệnh | test-coverage | `roles/executor/qa.md` mục 9 (cách đo và ghi coverage) | đã làm (`TK9.3`) |
| `affaan-m/ECC` lệnh | update-docs | `skills/closing-sprint/references/docs-sync.md` mục 10 | đã làm (`TK9.2`) |
| `affaan-m/ECC` lệnh | plan, checkpoint, quality-gate | đã thay bằng `method/process.md` mục 3 và 7 và `method/evidence.md` mục 8 | đã thay |
| `affaan-m/ECC` lệnh | plan-prd, prp-* | `skills/shaping-spec`, `skills/writing-plan` (lý do ở dòng `plan-prd`, `prp-*` mục lấy/bỏ: trùng SPEC/PLAN/`running-sprint`; `prp-commit`, `prp-pr` là hành động ra ngoài, thuộc cổng người) | đã thay |
| `affaan-m/ECC` khác | 24 hook, continuous-learning, loop / multi / tmux / devfleet | — (runtime của nguồn; quyết định Bỏ ở `SPR-02`) | bỏ qua |
| `garrytan/gstack` | `review` | `skills/code-review` (bước "sửa + test hồi quy là một lựa chọn", ý bằng chứng nơi gọi); checklist Pass 1/2 chưa lấy | đã làm một phần (`TK9.1`); phần còn lại hoãn |
| `garrytan/gstack` | `qa` | `skills/web-qa` (ranh giới và nhiệm vụ khám phá, cách đếm điểm, phát lại đúng bước, kiểm lại sau sửa; bỏ vòng tự sửa) | đã làm (`TK8.4`) |
| `garrytan/gstack` | `ship`, `land-and-deploy` (ý cổng CI của đúng commit) | `skills/closing-sprint` (bắt kịp gốc, ca hỏng thuộc ai, PLAN đối chiếu diff, PR; cổng CI trước khi gộp) | đã làm (`TK9.2`) |
| `obra/superpowers-lab` | finding-duplicate-functions | `skills/code-review/references/duplicates.md` (bước thủ công, không chép script) | đã làm (`TK9.1`) |
| `Fission-AI/OpenSpec` | "một yêu cầu một hành vi" | `skills/shaping-spec`, mẫu SPEC (một `FR` một hành vi) | đã làm, lấy ý (`TK5.2`) |
| `affaan-m/ECC`, `obra/superpowers` | viết lại sâu 9 mục "gọn" của Đợt 1: `deployment` (+ docker), `fastapi`, `postgres`, agent `fastapi-reviewer`, `database-reviewer`, `comment-analyzer`, `rag-pipeline-reviewer`, `writing-skills/references/diagnosing.md` | tại chỗ, đối chiếu HEAD mới | đã làm (`SPR-02`) |
| nguồn private (nhãn trung tính) | 6 mục "gọn" còn lại + luật truy vết của `check`: `bug-triage`, `adr`, `database-migrations/references/rehearsal.md`, `closing-sprint/references/release-notes.md` và `preflight.md`, bảng phủ `FR` → `VR` của thẻ QA, `scripts/README.md` | viết lại phòng sạch từ danh sách ý (`THIRD_PARTY.md` mục 3) | đã làm (`SPR-02`, viết lại phòng sạch ở `SPR-04` `TK10`) |

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

SHA rút gọn 8 ký tự — bản đầy đủ ở các bảng trên; frontmatter của skill/agent ghi bản đầy đủ. Bảng gồm cả thành phần
Đợt 2 (`SPR-04`). Cột SHA HEAD theo frontmatter hiện tại: mục viết lại sâu hay lấy thêm ở Đợt 2 ghi `ef648e01`, `f30b7b78` hoặc
`51111f74` (khối Đợt 2), mục còn lại giữ mốc Đợt 1. Cột
`base_sha` = mốc bản distill private đã làm điểm xuất phát (`3599962a` bộ kỹ thuật, `4c0fdc57` bộ quy
trình), "—" khi distill thẳng từ HEAD. Cách dùng: **chép** = giữ nội dung nguồn (dịch, cắt, sửa theo luật
lõi) · **viết lại** = viết lại theo khung repo, giữ ý · **ý** = chỉ khái niệm · **private** = từ nguồn
không giấy phép, phải viết lại trước khi công khai (danh sách file ở `THIRD_PARTY.md`).

| Skill / agent | Nguồn (repo — đường dẫn; tên gốc) | SHA HEAD | `base_sha` | Giấy phép | Cách dùng |
|---|---|---|---|---|---|
| `intake` | `affaan-m/ECC` — `skills/prompt-optimizer` (danh mục thiếu ngữ cảnh); `skills/intent-driven-development`, `skills/product-capability` (hai ý: luật nghiệp vụ không đọc được từ mã, tiêu chí nghiệm thu quan sát được) | `c70874fa` · `ef648e01` | `3599962a` | MIT | viết lại |
| `shaping-spec` | `obra/superpowers` — `skills/brainstorming/SKILL.md`; **tên gốc `brainstorming`**; `affaan-m/ECC` — `agents/spec-miner.md` (`references/spec-mining.md`); ý "một yêu cầu một hành vi" từ `Fission-AI/OpenSpec` | `8ca22dba` · `ef648e01` | — | MIT | viết lại |
| `writing-plan` | `obra/superpowers` — `skills/writing-plans/SKILL.md` (v6.4.2) | `8ca22dba` | — | MIT | viết lại |
| `running-sprint` | `obra/superpowers` — `skills/subagent-driven-development/`, `skills/executing-plans/`, `skills/dispatching-parallel-agents/` | `8ca22dba` | — | MIT | viết lại |
| `closing-sprint` | `obra/superpowers` — `skills/finishing-a-development-branch/`; `garrytan/gstack` — `document-release/`, `retro/`; ý từ bộ quy trình private — `preflight-gate` (`references/preflight.md`) và `release-notes-writer` (`references/release-notes.md`), cả hai **viết lại phòng sạch** ở `TK10` (`SPR-04`) từ danh sách ý, nguồn ghi dạng `concept:`; `affaan-m/ECC` — `commands/learn-eval.md`, `commands/update-docs.md` và `skills/living-docs-governance` (`references/docs-sync.md`); `garrytan/gstack` — `ship/` (ý: bắt kịp gốc, ca hỏng thuộc ai, PLAN đối chiếu diff, PR) và `land-and-deploy/` (ý: cổng CI của đúng commit) | `8ca22dba` · `96764e80` · — · `c70874fa` · `ef648e01` · `f30b7b78` | — | MIT; không giấy phép, chỉ lấy ý (2 file references) | viết lại; ý (2 file) |
| `bug-triage` | ý khái niệm "phân loại lỗi" (tái hiện trước, chấm theo hậu quả, định tuyến theo mức) — viết lại phòng sạch ở `TK10` (`SPR-04`) từ danh sách ý; nguồn ghi dạng `concept:`; gốc private (không giấy phép) không còn trong bản viết | — | — | không giấy phép (chỉ lấy ý) | ý |
| `tdd` | `obra/superpowers` — `skills/test-driven-development/` (+ `writing-good-tests.md`); `obra/superpowers-skills` — `skills/testing/testing-anti-patterns/`; `affaan-m/ECC` — `agents/tdd-guide.md` | `8ca22dba` · `cdcd624a` · `ef648e01` | — | MIT | chép |
| `debugging` | `obra/superpowers` — `skills/systematic-debugging/`; `garrytan/gstack` — `investigate/SKILL.md.tmpl`; `obra/superpowers-skills` — `defense-in-depth`, `condition-based-waiting`; script `find-polluter.sh` viết lại thành Python | `8ca22dba` · `96764e80` · `cdcd624a` | — | MIT | chép |
| `worktrees` | `obra/superpowers` — `skills/using-git-worktrees/` | `8ca22dba` | — | MIT | chép |
| `python` | `affaan-m/ECC` — `skills/python-patterns/`, `skills/python-testing/` | `c70874fa` | `3599962a` | MIT | chép |
| `fastapi` | `affaan-m/ECC` — `skills/fastapi-patterns/` | `ef648e01` | `3599962a` | MIT | chép |
| `postgres` | `affaan-m/ECC` — `skills/postgres-patterns/` (phần mẫu từ `supabase/agent-skills`), `agents/database-reviewer.md` | `ef648e01` · `ef648e01` | `3599962a` | MIT | chép |
| `database-migrations` | `affaan-m/ECC` — `skills/database-migrations/`; ý khái niệm "diễn tập migration trên bản sao cỡ production" (`references/rehearsal.md`) — viết lại phòng sạch ở `TK10` (`SPR-04`), nguồn ghi dạng `concept:` | `c70874fa` · — | `3599962a` | MIT; không giấy phép (chỉ lấy ý, `references/rehearsal.md`) | chép; ý (1 file) |
| `api-design` | `affaan-m/ECC` — `skills/api-design/` | `c70874fa` | `3599962a` | MIT | chép |
| `error-handling` | `affaan-m/ECC` — `skills/error-handling/` | `c70874fa` | `3599962a` | MIT | chép |
| `deployment` | `affaan-m/ECC` — `skills/deployment-patterns/`, `skills/docker-patterns/` | `ef648e01` | `3599962a` | MIT | chép |
| `github-ops` | `affaan-m/ECC` — `skills/github-ops/` | `c70874fa` | `3599962a` | MIT | chép |
| `adr` | ý khái niệm "bản ghi quyết định kiến trúc" (ngắn, đánh số, ít nhất hai lựa chọn thật, thay thế chứ không sửa) — viết lại phòng sạch ở `TK10` (`SPR-04`) từ danh sách ý; nguồn ghi dạng `concept:` | — | — | không giấy phép (chỉ lấy ý) | ý |
| `verify-before-done` | `obra/superpowers` — `skills/verification-before-completion/`; `affaan-m/ECC` — `skills/verification-loop/` (`references/loop.md`) | `8ca22dba` · `ef648e01` | — | MIT | chép |
| `code-review` | `obra/superpowers` — `skills/requesting-code-review/`, `skills/receiving-code-review/`; bộ quy trình private — `code-review-routing` (tự viết); `obra/superpowers-lab` — `skills/finding-duplicate-functions/` (`references/duplicates.md`); `garrytan/gstack` — `review/` (ý: sửa kèm test hồi quy; bằng chứng nơi gọi); `affaan-m/ECC` — `commands/code-review.md`, `commands/review-pr.md` (đối chiếu, chưa có câu nào được chép vào skill) | `8ca22dba` · `4c0fdc57` · `51111f74` · `f30b7b78` | — | MIT; tự viết | viết lại |
| `plan-review` | `garrytan/gstack` — `plan-eng-review/SKILL.md.tmpl`, `plan-eng-review/sections/` | `96764e80` | `4c0fdc57` | MIT | chép |
| `security-review` | `affaan-m/ECC` — `skills/security-review/` (+ `cloud-infrastructure-security.md`) | `c70874fa` | `3599962a` | MIT | chép |
| `security-audit` | `garrytan/gstack` — `cso/SKILL.md.tmpl` | `96764e80` | `3599962a` | MIT | chép |
| `web-qa` | `garrytan/gstack` — `qa-only/SKILL.md.tmpl`, `qa/` (ý chỉ-báo-cáo: ranh giới và nhiệm vụ khám phá, cách đếm điểm, phát lại đúng bước, kiểm lại sau sửa); `affaan-m/ECC` — `skills/browser-qa/`, `skills/click-path-audit/` (ý) | `96764e80` · `f30b7b78` · `ef648e01` | `4c0fdc57` | MIT | chép |
| `response-style` | nguồn văn phong (BLUF, Minto, plain language, Google dev style, Diátaxis, Microsoft style, NN/g, hướng dẫn prompting Anthropic) | — | — | nhiều loại | ý |
| `id-convention` | `github/spec-kit` (mã `US`/`FR`/`SC`); ISO/IEC/IEEE 29148; MoSCoW | `d2ddd910` | — | MIT; tiêu chuẩn có bản quyền | ý |
| `token-economy` | `affaan-m/ECC` — `skills/context-budget/`, `skills/strategic-compact/`, `skills/iterative-retrieval/` (mục 7); caveman (ý); ccusage, repomix (chỉ gọi) | `c70874fa` · `f5d72948` · `1597d652` · `0b3f82b4` · `ef648e01` | `3599962a` | MIT; Apache-2.0 (chỉ ý) | chép (ECC); ý (caveman) |
| `writing-skills` | `obra/superpowers` — `skills/writing-skills/` (+ `testing-skills-with-subagents.md`, `persuasion-principles.md`), `skills/diagnosing-superpowers/` | `8ca22dba` | — | MIT | chép |
| `react` | `affaan-m/ECC` — `skills/react-patterns/`, `skills/react-testing/` (`references/testing.md`) | `ef648e01` | — | MIT | chép |
| `frontend` | `affaan-m/ECC` — `skills/frontend-patterns/`, `skills/vite-patterns/` (`references/vite.md`) | `ef648e01` | — | MIT | chép |
| `e2e-testing` | `affaan-m/ECC` — `skills/e2e-testing/`, `skills/ai-regression-testing/` (`references/ai-regression.md`) | `ef648e01` | — | MIT | chép |
| `eval-harness` | `affaan-m/ECC` — `skills/eval-harness/` | `ef648e01` | — | MIT | chép |
| agent `python-reviewer` | `affaan-m/ECC` — `agents/python-reviewer.md` | `c70874fa` | `3599962a` | MIT | chép |
| agent `fastapi-reviewer` | `affaan-m/ECC` — `agents/fastapi-reviewer.md` | `ef648e01` | `3599962a` | MIT | chép |
| agent `database-reviewer` | `affaan-m/ECC` — `agents/database-reviewer.md` (phần mẫu từ `supabase/agent-skills`) | `ef648e01` | `3599962a` | MIT | chép |
| agent `security-reviewer` | `affaan-m/ECC` — `agents/security-reviewer.md` | `c70874fa` | `3599962a` | MIT | chép |
| agent `silent-failure-hunter` | `affaan-m/ECC` — `agents/silent-failure-hunter.md` | `c70874fa` | `3599962a` | MIT | chép |
| agent `comment-analyzer` | `affaan-m/ECC` — `agents/comment-analyzer.md` | `ef648e01` | `3599962a` | MIT | chép |
| agent `rag-pipeline-reviewer` | `affaan-m/ECC` — `agents/rag-pipeline-reviewer.md` | `ef648e01` | `3599962a` | MIT | chép |
| agent `code-explorer` | `affaan-m/ECC` — `agents/code-explorer.md` | `ef648e01` | — | MIT | chép |
| agent `code-reviewer` | `affaan-m/ECC` — `agents/code-reviewer.md`, `commands/code-review.md` | `ef648e01` | — | MIT | chép |
| agent `test-analyzer` | `affaan-m/ECC` — `agents/pr-test-analyzer.md`; **tên gốc `pr-test-analyzer`** | `ef648e01` | — | MIT | chép |
| agent `build-fixer` | `affaan-m/ECC` — `agents/build-error-resolver.md`, `commands/build-fix.md`; **tên gốc `build-error-resolver`**; agent duy nhất được sửa file (T2) | `ef648e01` | — | MIT | chép |
| agent `typescript-reviewer` | `affaan-m/ECC` — `agents/typescript-reviewer.md` | `ef648e01` | — | MIT | chép |
| agent `react-reviewer` | `affaan-m/ECC` — `agents/react-reviewer.md` | `ef648e01` | — | MIT | chép |

### Thành phần ngoài skill và agent (không có frontmatter)

Các file này không mang khoá `source` nên nguồn ghi ở đây (và trong chú thích đầu file khi có). Mọi dòng dùng ECC ở
`ef648e01` (MIT), gstack ở `f30b7b78`, superpowers-lab ở `51111f74`; cách dùng là viết lại, không chép câu.

| Thành phần | Nguồn (repo — đường dẫn) | SHA | Việc |
|---|---|---|---|
| `method/standards/common/*.md` (7 file), `python.md`, `typescript.md`, `react.md`, `web.md` | `affaan-m/ECC` — `rules/common/*`, `rules/python/*`, `rules/typescript/*`, `rules/react/*`, `rules/web/*` | `ef648e01` | `TK6`, `TK6.5` |
| `method/sizing.md` mục 5, `method/process.md` mục 6.1 | `affaan-m/ECC` — `skills/orch-pipeline/`, `skills/orch-*` (5), `skills/loop-design-check/` | `ef648e01` | `TK4.1`, `TK4.2` |
| `method/evidence.md` mục 8 | `affaan-m/ECC` — `skills/delivery-gate/` (nội dung thành luật, không Stop hook) | `ef648e01` | `TK4.3` |
| `method/review-gate.md` | `affaan-m/ECC` — `workflows/orch-review.workflow.js` (chỉ thiết kế) | `ef648e01` | `TK4.4` |
| `roles/verifier/dual-review.md` | `affaan-m/ECC` — `skills/santa-method/` | `ef648e01` | `TK4.5` |
| `roles/executor/architect.md`, `roles/executor/implementer.md` | `affaan-m/ECC` — `agents/planner.md`, `agents/architect.md`, `agents/code-architect.md`, `skills/search-first/`, `skills/inherit-legacy-style/` | `ef648e01` | `TK5.1` |
| `roles/executor/qa.md` mục 9 | `affaan-m/ECC` — `commands/test-coverage.md` (ý) | `ef648e01` | `TK9.3` |
| `roles/verifier/specialists/frontend.md` mục 9 | `affaan-m/ECC` — `agents/a11y-architect.md` (lấy gọn) | `ef648e01` | `TK8.5` |
| `templates/registry/feature-spec.md`, `skills/closing-sprint/references/docs-sync.md` mục 10–11 | `affaan-m/ECC` — `skills/living-docs-governance/`, `commands/update-docs.md` | `ef648e01` | `TK4.7`, `TK9.2` |
| `skills/code-review/references/duplicates.md` | `obra/superpowers-lab` — `skills/finding-duplicate-functions/` (bước thủ công; không chép script) | `51111f74` | `TK9.1` |
| `method/conventions.md` mục 4.1 (quy tắc số phiên bản), `method/sizing.md` (bậc việc), `templates/sprint/SPRINT-tiny.md`, `templates/registry/LEDGER.md` | không có nguồn bên ngoài — tự viết theo yêu cầu của chủ repo (`SPR-04`) | — | `TK2`, `TK3`, `TK15` |
