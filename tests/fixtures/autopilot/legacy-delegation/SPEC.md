---
id: SPR-02-spec
doc: spec
title: "Chặng 1b: một nguồn cho agent-skill-studio"
sprint: SPR-02
request: RQ-003
feature: null
status: approved
size: large
risk: high
risk_tags: [public_api, infra]
gate_1: approved
gate_1_at: 2026-10-27 19:23 +07
gate_1_quote: "duyệt thay: Duyệt có điều kiện SPEC/PLAN SPR-02 chặng 1b — DN1 D, DN2 (a), DN3 (a), DN4 (a), DN5 (a), DN7 (a), DN8 (a) kèm RF23, DN9 (a) loại trừ `evals/*/runs/` và `tests/fixtures/`; mốc hợp đồng `1211bfa`; điều kiện ĐK1–ĐK3 ở `evidence/gate1-fable.md` — Fable duyệt hộ theo uỷ quyền Đức 27/10"
gate_1_mode: delegated
delegation:
  grant: "Đức uỷ quyền Fable quyết thay mọi nội dung cần quyết kể cả Cổng 1, Cổng 2, gộp, push (chuyển qua lời giao của phiên điều phối chương trình dời skill, 27/10/2026, «mở Studio 1b»)"
  grant_at: 2026-10-27 18:30 +07
  scope: [gate_1, gate_2]
  expires: sprint_end
  by: claude-fable-5-1
  tier: T1
  files: []
  revoked_at: null
roles:
  analyst: [T1, coordinator]
  business-reviewer: [T1, claude-fable-5-1]
created: 2026-10-27
updated: 2026-10-27
links:
  plan: PLAN.md
  progress: PROGRESS.md
  report: REPORT.md
---

# Chặng 1b: một nguồn cho agent-skill-studio — Đặc tả (SPEC)

> **Kết luận:** sprint SPR-02 làm cho mã và khuôn skill của Studio mỗi thứ chỉ còn một bản (engine trong skill, gốc là shim,
> engine tách mô-đun phẳng, thêm lệnh `check`), trả ba nợ 1a xếp cho 1b (`RQ-009`, `RQ-011`, `RQ-018`) và hai việc ROADMAP
> (`PR1`, `new --full --lang vi`); xong khi bộ ca hợp đồng chốt trước cho cùng kết quả như `1211bfa` (SC1), không còn blob trùng
> ngoài vùng loại trừ (SC2), CI 4/4 xanh (SC3) và lô 16 lượt không kém SPR-33 (SC4).

## 1. Bối cảnh

- Yêu cầu gốc: RQ-003 (chặng 1b của [ROADMAP](../ROADMAP.md) mục 5; «lát 1 của sổ đối tác `RQ-190`» = một nguồn engine/khuôn, lát 2
  áp chuẩn → đối tác P13b), cộng `RQ-009`, `RQ-011`, `RQ-018` (để lại từ SPR-01, xếp
  cho 1b). Không có tính năng (FS) sống. Bàn giao: [HANDOFF-1b](../2026-10-27-security-debt-1a/HANDOFF-1b.md).
- Chương trình «dời skill» (ROADMAP chương trình mục 6): 1b là tiên quyết của chặng 2 → 3 → đối tác `P11a`, `P13b`.
  `studio.py`, `standards/`, khuôn **ở lại Studio**.
- Hiện trạng đo 27/10 trên `1211bfa` (bằng chứng gốc: [evidence/dossier-1b.md](evidence/dossier-1b.md)):
  - `studio.py` 2.813 dòng, hai bản byte-giống (gốc và `skills/skill-creator-studio/scripts/studio.py`); test ép bằng nhau.
  - Khuôn hai bản: `templates/skill-template{,-full}/` ↔ `skills/skill-creator-studio/assets/…` (10 blob trùng), giữ đồng bộ
    bằng lệnh `sync-template`; `repo_root` đòi `templates/skill-template/SKILL.md`.
  - `git ls-files -s`: 21 blob trùng — 9 do hai bản mã/khuôn, 1 fixture cố ý, 11 bằng chứng thô `evals/…/runs/SPR-18` (`evidence/tk0-baseline.txt`).
  - 10 file test nạp `studio.py` bằng `importlib`; 20 tên tự định nghĩa bị `patch.object` (rủi ro chính khi tách).
  - Cổng `model_evaluated_problems` sống trong `tests/test_studio.py:36-149`, engine không tự kiểm (`RQ-018`).
  - `fmt --check skills/skill-creator-studio`: 12 WARN `PR1` ở `references/NEW_WORKFLOW.md`, `REFINE_WORKFLOW.md`.
  - `new --full --lang vi` thoát 2 "full template is English-only".
  - Ba lỗ `RQ-009` (dossier mục 5): `entry.is_dir()` theo đích symlink; `SKILL.md`/manifest đọc trước khi chặn `PACK`;
    `move_aside` `copytree` đi xuyên junction trong bản cài cũ.
  - Bộ test: `pytest` 434 passed, 4 skipped, 39 s; 0 người gọi mã sống ngoài repo (dossier mục 7).

### 1.1 Ràng buộc và lưu ý do người giao

Chép nguyên ý lời giao của phiên điều phối 27/10:
- Đủ quy trình agent-agile-team; Opus review PLAN; kiểm định bởi agent khác (Opus), kéo security reviewer nếu chạm đầu vào
  ngoài/hệ tệp.
- Không đọc `~/.secret`, `.env*`; không `--no-verify`; không force-push.
- Người làm không tự chấm: Sonnet đọc, Sonnet High làm, Opus review, Fable duyệt hộ Cổng 1/Cổng 2/gộp/push (ghi
  `gate_*_quote` kèm "Fable duyệt hộ theo uỷ quyền Đức").
- Hồ sơ kiểm định trong `evidence/` của thư mục sprint (sổ đối tác, có git).
- Máy không tạo được symlink: đẩy nhánh + kích `workflow_dispatch` CI Windows **trước** khi gọi reviewer ký (`LN1` 1a).
- Dừng hỏi điều phối chỉ khi: chạm secret, sửa file luật (trình 5 ý), xoá ngoài vùng tạm, PLAN hỏng.
- Gộp `--no-ff` + push khi CI của đúng commit xanh. `RQ-008` không thuộc sprint.

### 1.2 Rủi ro cần chú ý và khẩu vị / mức tự trị

- Gãy người gọi cũ (`python studio.py …` từ gốc, cwd khác, skill chép rời, ZIP) — chặn bằng bộ ca hợp đồng chốt trước.
- Mỗi sửa `skills/` đổi băm cây skill → một lô đo duy nhất ở cuối, sau review cuối.
- Khẩu vị: hồi quy hợp đồng ngoài danh sách mục 7 = **Chặn**; tự trị trong repo Studio + sổ riêng.

## 2. Câu chuyện người dùng

SPEC có 4 **user story** (US):

| Mã | Câu chuyện | Ưu tiên |
|---|---|---|
| US1 (một nguồn) | Là người bảo trì Studio, tôi sửa mã hay khuôn ở đúng một chỗ, để không còn lệnh đồng bộ và test ép hai bản giống nhau | Bắt buộc |
| US2 (lời gọi cũ không gãy) | Là người/CI đang gọi `python studio.py validate|audit|doctor|fmt|evals|package|install|new`, tôi nhận cùng mã thoát và JSON như trước, ở mọi cách gọi | Bắt buộc |
| US3 (engine tự kiểm, an toàn hơn) | Là chủ repo, engine tự kiểm hồ sơ đánh giá, không đọc xuyên link/cloud ở ba chỗ còn sót, và test bắt được đột biến | Bắt buộc |
| US4 (viết skill tiếng Việt đủ khuôn) | Là người tạo skill, tôi dùng `check` cho một file và `new --full --lang vi` có khuôn đầy đủ tiếng Việt; tài liệu quy trình của skill đúng hình | Nên có |

## 3. Yêu cầu chức năng

SPEC có 13 **functional requirement** (FR); kịch bản KHI … THÌ … là mã con. «Engine» = `skills/skill-creator-studio/scripts/`.

### FR1 — Shim và một bản engine (→ US1, US2)

- **FR1.1:** KHI chạy `python <repo>/studio.py <lệnh> …` (cwd bất kỳ) THÌ shim gốc (≤ 20 dòng, chỉ thư viện chuẩn) chạy engine với
  cùng `argv`, cùng stdout/stderr, cùng mã thoát.
- **FR1.2:** `VERSION` chỉ khai một chỗ trong engine; `--version`, doctor `studio_version`, test manifest đọc từ đó.
- **FR1.3:** Mọi test nạp engine (không nạp shim như mô-đun); test ép byte-giống bỏ, thay bằng test subprocess cho shim.

### FR2 — Khuôn chỉ ở `assets/` (→ US1)

- **FR2.1:** `templates/skill-template/`, `templates/skill-template-full/` bị xoá; `get_template` **luôn** lấy `assets/` của chính
  engine (cạnh `scripts/`), kể cả khi chạy trong repo.
- **FR2.2:** Nhận diện gốc repo đổi sang `.claude-plugin/plugin.json` + `standards/SKILL_AUTHORING_STANDARD.md` (không còn cần
  `templates/`). `templates/project/` và `templates/README.md` giữ (dời ở chặng 2), README sửa chữ.

### FR3 — Bỏ `sync-template` (→ US1)

- **FR3.1:** KHI gọi `python studio.py sync-template [--check]` THÌ argparse báo lệnh không hợp lệ, thoát 2. CI, test, tài liệu
  (README, SKILL.md, `templates/README.md`) không còn nhắc lệnh như lệnh sống; CHANGELOG ghi bỏ.

### FR4 — Tách mô-đun phẳng, giữ hành vi (→ US1, US2)

- **FR4.1:** Engine thành ≥ 6 mô-đun phẳng trong `scripts/` (theo ADR-001), `studio.py` của engine ≤ 300 dòng (CLI + chọn lệnh).
- **FR4.2:** Chạy được trên Python 3.9–3.12, chỉ thư viện chuẩn; chạy từ repo, từ skill chép rời, từ ZIP `package` đã giải nén.
- **FR4.3:** Mọi kiểm tĩnh đang áp cho `studio.py` (AST cấm `subprocess`, regex tuyến tính, quét mã `SZ2`) áp cho **mọi** mô-đun engine.
- **FR4.4:** `package` của `skill-creator-studio` gói đủ mọi mô-đun; ZIP chạy `new`, `validate`, `doctor` độc lập.
- **FR4.5:** Luật nạp (ADR-0001, `RF3`, `RF13`): mô-đun engine không `from studio_* import`, không `import studio`; engine `studio.py`
  không có thuộc tính trùng tên công khai của `studio_*` (không re-export); sau import, mọi `studio_*` phải nằm cùng thư mục với
  engine — lệch (mô-đun cùng tên đã cache từ chỗ khác) → thoát 2 có lời báo; mỗi mô-đun có `from __future__ import annotations`.
- **FR4.6:** `validate` skill `skill-creator-studio` không sinh WARN mới vì mô-đun (`SC3`: mỗi `scripts/*.py` phải được nêu trong
  `SKILL.md` — `SKILL.md` thêm một dòng nêu các mô-đun nội bộ, `RF2`).

### FR5 — Lệnh `check`, bí danh `validate`/`audit` (→ US2, US4)

- **FR5.1:** `validate`, `audit` giữ nguyên cờ, mã thoát, JSON (gồm khoá `audit`) và dòng chữ cuối của `audit`.
- **FR5.2:** `check <đường>` nhận skill (thư mục có `SKILL.md` hoặc chính `SKILL.md`) → cùng kết quả như `validate` trên skill đó
  cùng mã thoát; nhận cờ `--all`, `--require-evals`, `--eval-root`, `--target`, `--json`. JSON đích (`RF17`):
  `{"audit": false, "reports": [{"skill": <str>, "type": "skill", "findings": [...]}]}` — giống hệt `validate` trừ khoá `type` ở
  **mỗi** phần tử `reports` (cả với `--all`); chế độ chữ giống `validate`.
- **FR5.3:** KHI file `.md` có frontmatter `type:` là `workflow`/`rules`, hoặc tên `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` THÌ thoát 2
  "check for type <t> is not available yet" (chặng 2/3 làm theo `DOC_TYPES.md`). KHI không nhận được loại THÌ thoát 2 kèm lời báo.

### FR6 — Cổng `model_evaluated` trong engine (`RQ-018`) (→ US3)

- **FR6.1:** Logic cổng (`model_evaluated_problems`, `AB_THRESHOLDS`) chuyển vào engine; test chỉ gọi engine, không giữ bản thứ hai.
- **FR6.2:** KHI `evals --all` chạy và engine nằm trong repo (`repo_root` của **chính engine**, không theo cwd) THÌ engine chạy cổng;
  có vấn đề → mỗi vấn đề một finding ERROR `EV20`, thoát 1. Trong repo mà thiếu `registry/catalog.json` → ERROR `EV20` (không bỏ
  qua im lặng, `RF14`). Ngoài repo (skill chép rời/ZIP) cổng bỏ qua, không lỗi.
- **FR6.4:** Cổng **không thực thi mã** ngoài engine: logic đếm log (`summarize`) nằm trong `studio_evals`, đọc JSON qua helper an toàn
  (không theo link/cloud, có trần); `evals/tools/activation.py` gọi ngược engine theo đường cố định từ chính nó (một nguồn).
  `skill["evals"]`, `sprint` từ catalog phải là đường tương đối thuần dưới gốc repo, `runs_dir` được duyệt `walk_files` trước khi
  đọc; vi phạm → `EV20`. Cổng chỉ chạy khi repo của engine có thư mục `evals/` (sửa sau kiểm định: `RF-S1`, `RF-S2`; DN8 → (b),
  PROGRESS 22:30).

### FR7 — Ba lỗ link/cloud (`RQ-009`) (→ US3)

- **FR7.1:** `iter_md`, `skill_dirs`, `_is_dir_quiet`: không stat theo đích link; **bắt buộc** mẫu của `walk_files` (`is_symlink()` →
  cloud → `is_dir(follow_symlinks=False)` → `is_link(path)` cho reparse point/junction) hoặc gọi thẳng `walk_files`; riêng
  `follow_symlinks=False` không đủ vì junction Windows vẫn là thư mục (`RF10`). Link thư mục không được đi vào, không stat đích.
- **FR7.2:** `package`/`install`: kiểm link/cloud/zone của `SKILL.md` và manifest **trước** khi đọc; vi phạm → ERROR `PACK`, không đọc.
- **FR7.3:** `install --force`: bản sao lưu khác ổ không đi xuyên junction/symlink bên trong cây cũ (chép link như link, hoặc từ chối
  `PACK`/thoát 1 có lời báo); không mất bản cũ khi lỗi.

### FR8 — Đột biến và đường lỗi (`RQ-011`) (→ US3)

- **FR8.1:** Một bộ đột biến chốt trước (≥ 13: nhóm `CT10` và nhóm doctor theo `co-list.md` SPR-33, cộng đột biến cho ba lỗ FR7) ghi
  vào evidence **trước** khi viết test; test mới giết 100 % bộ đó.
- **FR8.2:** Coverage (`coverage run --branch`, bộ test đầy đủ): (i) dòng + nhánh trên dòng mới/sửa **sau** commit tách cuối (TK4c)
  ≥ 80 %; (ii) dòng + nhánh của 39 hàm có dòng đổi ở 1a (danh sách `evidence/tk0-baseline.txt`) ≥ 80 % gộp — nợ «nhánh lỗi» của
  `RQ-011`; (iii) dòng toàn engine ≥ 89 % làm sàn (baseline hợp hai bản 89,2 %) (`RF8`).

### FR9 — Tài liệu quy trình đúng hình (`PR1`) (→ US4)

- **FR9.1:** `references/NEW_WORKFLOW.md`, `references/REFINE_WORKFLOW.md` có đủ hình quy trình; `fmt --check skills/skill-creator-studio`
  0 `PR1`, nội dung hướng dẫn không mất bước (đối chiếu từng bước cũ → mới).

### FR10 — `new --full --lang vi` (→ US4)

- **FR10.1:** KHI `new <tên> --description … --full --lang vi` THÌ tạo cây full với `SKILL.md` tiếng Việt, thoát 0; skill sinh ra
  `validate` 0 ERROR; `new --full` (en) và `new --lang vi` không đổi đầu ra.

### FR11 — Bộ ca hợp đồng chốt trước (→ US2)

- **FR11.1:** Bộ ca (lệnh × cách gọi: gốc repo, cwd khác, engine trực tiếp trong thư mục skill của repo, skill chép rời, ZIP giải
  nén) và đáp án (mã thoát + stdout JSON/chữ đã chuẩn hoá đường/giờ; stderr chỉ so tiền tố ổn định) sinh từ `git archive 1211bfa`,
  commit **trước** mọi sửa engine; chạy trong bộ test thường.
- **FR11.3:** Đầu vào ca là **ảnh chụp đóng băng** từ `1211bfa` (skill, evals, fixture cần) dưới `tests/fixtures/contract/`, không phải
  skill sống mà sprint sửa; thêm vài ca «repo sống» chỉ so mã thoát (`RF5`). Đáp án cũng dưới `tests/fixtures/contract/` (`RF11`).
- **FR11.4:** Đáp án xanh trên CI 4 ô **trước** khi sửa engine (đẩy nhánh ngay sau TK1, `RF6`).
- **FR11.2:** Đổi có chủ ý (mục 7) đánh dấu từng ca, không sửa đáp án âm thầm.

### FR12 — ADR chỗ đặt engine (→ US1)

- **FR12.1:** ADR-001 ở sổ riêng (`system/ledger/agent-skill-studio/adr/`) chốt Quyết định 2 ROADMAP + cách tách mô-đun + cách patch test.

### FR13 — Lô «không hồi quy» 16 lượt (→ US2)

- **FR13.1:** Sau review cuối, `SHA lô` = HEAD; 16 lượt (8 ca × 2 skill, claude-code, `--plugin-dir` = `git archive` của `SHA lô`
  ngoài cây cha) theo RUNBOOK «Luật lô»; log che bằng `redact.py` trước commit; `batch_sha_kind: commit`.

## 4. Tiêu chí thành công

SPEC có 10 **success criterion** (SC):

| Mã | Tiêu chí | Cách đo |
|---|---|---|
| SC1 (hợp đồng giữ) | 100 % ca của bộ FR11 cho cùng mã thoát và JSON chuẩn hoá như đáp án `1211bfa`, trừ ca đánh dấu đổi có chủ ý (mục 7) | test bộ ca, lệnh mới chạy ở HEAD |
| SC2 (một nguồn) | `git ls-files -s` 0 blob trùng ngoài `evals/*/runs/` và `tests/fixtures/` (lệch có duyệt so ROADMAP «không còn blob trùng» — PLAN DN9) | lệnh đếm |
| SC3 (CI) | CI 4/4 ô xanh trên commit nhánh trước review ký và trên commit gộp `main` | `gh run view` |
| SC4 (lô không hồi quy) | 16/16 lượt `ran`; `data-quality-audit` positive ≥ 4/5, negative 0/3; `skill-creator-studio` positive ≥ 2/5, negative 0/3 | `activation.py summarize` |
| SC5 (đỏ trước xanh sau) | Mỗi FR5–FR7, FR10 có ≥ 1 test `bắt-lỗi` đỏ trên **commit cha của commit sửa** (assertion/mã thoát, không phải lỗi import), xanh ở HEAD; FR8: mỗi test mới đỏ trên ≥ 1 đột biến; ca chỉ tái hiện được bằng junction/symlink thật chạy ở CI Windows (`RF4`) | `evidence/qa.md` |
| SC6 (đột biến, coverage) | Bộ đột biến FR8.1 chết 100 % (chạy lại bằng `evidence/run_mutants.py`); FR8.2 (i), (ii) ≥ 80 %, (iii) ≥ 89 % | script đột biến + `coverage --branch` |
| SC7 (ký bảo mật) | Security reviewer T1 độc lập: 0 Chặn/Phải sửa mở trên FR7, FR1, FR4 (shim/sys.path) | `evidence/review-security.md` |
| SC8 (check, new vi, PR1) | Test FR5.2/FR5.3 xanh; `new --full --lang vi` thoát 0 và skill sinh ra 0 ERROR; `fmt --check skills/skill-creator-studio` 0 `PR1` | lệnh mới chạy |
| SC9 (người gọi đối tác) | `system/evals/run.ps1 -Tier fast` ĐẠT trước khi gộp (ROADMAP Rủi ro 1) | lệnh mới chạy |
| SC10 (cổng trong engine) | `evals --all` thoát 1 trên catalog hỏng (ca đỏ), 0 trên catalog thật; 0 bản cổng thứ hai trong `tests/` | test + grep |

## 5. Ngoài phạm vi

- Dời cây 8 → 6 thư mục, `standards/` gộp, `DOC_TYPES.md`, README < 150 dòng, `check` cho loại workflow/rules: chặng 2/3.
- Bằng chứng thô `evals/*/runs/` ra ledger (blob trùng SPR-18): chặng 2.
- `RQ-010` (TOCTOU `_winapi`), `RQ-012`…`RQ-017`, `RQ-019`, `RQ-020`: chặng khác theo REQUESTS.
- `skill-curator`, `catalog`: chặng 3. Phát hành/tag: chặng 2. Đo A/B `model_evaluated: true`: chặng 4.

## 6. Câu hỏi cần làm rõ

SPEC có 1 **clarification question** (CQ) cần người duyệt trả lời ở Cổng 1:

| Mã | Câu hỏi | Đề xuất | Trạng thái |
|---|---|---|---|
| CQ1 (file luật `AGENTS.md` của Studio) | `AGENTS.md:36` bảo chạy `sync-template` — lệnh bị bỏ. Sửa dòng đó là sửa file luật: cần lời gật 5 ý của điều phối | Hỏi điều phối một lần; chưa gật thì giữ dòng, ghi `CO` cho chặng 2 (`RQ-186` gộp file luật) | đóng → Fable gật 19:23 (PLAN Bản ghi duyệt thay) |

- **ASSUMPTION — mốc so sánh:** đáp án hợp đồng lấy `1211bfa` (HANDOFF mục 2), không `df875ce` — 1a đã đổi hợp đồng có chủ ý.
- **ASSUMPTION — vùng loại trừ SC2:** blob trùng trong `evals/*/runs/` (11, bằng chứng thô; chặng 2 dời ra ledger theo `RQ-004`)
  và `tests/fixtures/` (1 fixture cố ý + ảnh chụp/đáp án hợp đồng) không tính — chốt bằng PLAN DN9.
- **ASSUMPTION — import shim:** nạp `studio.py` gốc như mô-đun Python không còn là hợp đồng (0 người gọi ngoài test).

## 7. Đổi hợp đồng / giao diện

| Thay đổi | Kiểu | Trước → sau | Bên dùng bị ảnh hưởng | Tương thích ngược | Lộ trình deprecate |
|---|---|---|---|---|---|
| `sync-template` | Bỏ | lệnh sống → thoát 2 (argparse) | CI Studio, `AGENTS.md:36` (CQ1); 0 mã sống ngoài | Không | CHANGELOG; khuôn không còn bản sao để đồng bộ |
| `check` | Thêm | — → lệnh mới, `validate`/`audit` thành bí danh giữ nguyên | — | Có | Không cần |
| `evals --all` | Sửa | không kiểm catalog → kiểm cổng `model_evaluated`, thoát 1 khi hỏng | CI Studio | Có khi catalog hợp lệ (hiện hợp lệ) | CHANGELOG |
| `new --full --lang vi` | Sửa | thoát 2 → thoát 0, cây full tiếng Việt | người gọi `new` | Có (chỉ mở thêm) | Không cần |
| `templates/skill-template*` | Bỏ | đường khuôn → chỉ `assets/` | 0 mã sống (Quyết định 8) | Không | CHANGELOG |
| Nhận diện gốc repo | Sửa | cần `templates/skill-template/SKILL.md` → cần `.claude-plugin/plugin.json` | cây chép một phần repo | Gần như có | CHANGELOG |
| `studio.py` gốc | Sửa | engine đầy đủ → shim; nạp như mô-đun không còn hỗ trợ | chỉ test | Có cho CLI | CHANGELOG |
| `package`/`install` đọc `SKILL.md`/manifest là link/cloud | Sửa | đọc rồi mới chặn → chặn `PACK`, không đọc | người đóng gói | Có (chặt hơn có chủ ý) | CHANGELOG |
| `install --force` cây cũ có junction | Sửa | chép xuyên → thoát 1 lời báo, bản cũ giữ nguyên (DN5) | người cài lại | Có | CHANGELOG |
| Hai engine khác chỗ trong một tiến trình | Sửa | dùng nhầm mô-đun đã cache im lặng → thoát 2 có lời báo (FR4.5) | `skill-curator` chặng 3, test | Có | Không cần |
| Trong repo thiếu `registry/catalog.json` | Sửa | — → `evals --all` ERROR `EV20` | chặng 2 khi dời catalog phải dời cùng | Có | Không cần |
| `fmt`/`validate --all` gặp symlink (bổ sung sau kiểm định, `RF-B2`) | Sửa | `fmt` stat đích rồi bỏ qua tên không `.md` → mọi symlink báo `skipped (link)`; `skill_dirs` (`--all`) không còn đi vào thư mục là link/junction | người chạy `fmt`, `validate --all` trên cây có link | Có (chặt hơn có chủ ý, FR7.1) | CHANGELOG |

## 8. Truy vết

| Câu chuyện | Yêu cầu | Tiêu chí |
|---|---|---|
| US1 (một nguồn) | FR1, FR2, FR3, FR4, FR12 | SC2, SC3 |
| US2 (lời gọi cũ không gãy) | FR1, FR4, FR5.1, FR11, FR13 | SC1, SC3, SC4, SC9 |
| US3 (engine tự kiểm, an toàn) | FR6, FR7, FR8 | SC5, SC6, SC7, SC10 |
| US4 (skill tiếng Việt, check) | FR5.2, FR5.3, FR9, FR10 | SC8 |
