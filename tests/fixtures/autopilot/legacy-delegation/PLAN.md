---
id: SPR-02-plan
doc: plan
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
  architect: [T1, coordinator]
  tech-reviewer: [T1, claude-opus-5-5]
  business-reviewer: [T1, claude-fable-5-1]
created: 2026-10-27
updated: 2026-10-27
links:
  spec: SPEC.md
  progress: PROGRESS.md
  report: REPORT.md
  adr: ../../adr/0001-engine-in-skill-flat-modules.md
---

# Chặng 1b: một nguồn cho agent-skill-studio — Kế hoạch (PLAN)

> **Kết luận:** khoá hợp đồng CLI bằng bộ ca đóng băng sinh từ `1211bfa` và chứng xanh trên CI 4 ô trước, rồi đổi gốc thành
> shim, dời khuôn về `assets/`, tách engine thành mô-đun phẳng theo ADR-0001 (ba lát), sau đó trả `RQ-018`, `RQ-009`, `RQ-011`,
> `PR1`, `new --full --lang vi`; 18 việc tuần tự trên một nhánh; 9 quyết định cho người duyệt hộ ở Cổng 1 (DN6 đã chốt theo lời
> giao) và SPEC/CQ1 (file luật) cho Fable xét 5 ý. Plan-review vòng 1 (Opus): 22 phát hiện, đã nạp hết (`evidence/plan-review-opus.md`).

## Mục tiêu

Đạt SC1–SC10 của SPEC: một nguồn (SC2), hợp đồng giữ (SC1, SC9), CI 4/4 (SC3), lô không hồi quy (SC4), nợ 1a xếp cho 1b đóng
có test đỏ→xanh (SC5, SC6, SC10), ký bảo mật (SC7), `check`/`new vi`/`PR1` (SC8).

## Kiến trúc

- **Engine (ADR-0001, phương án D):** `skills/skill-creator-studio/scripts/` gồm `studio.py` (CLI, argparse, chọn lệnh; ≤ 300 dòng)
  và mô-đun phẳng theo dossier mục 1:
  `studio_const.py` (hằng, `VERSION`, regex) · `studio_fs.py` (emit, frontmatter, `repo_root`, `skill_dirs`, link/cloud/zone,
  `walk_files`, `open_nofollow_read`, `create_exclusive`, `_remove_quietly`, `_is_dir_quiet`, `_secret_dirs`) · `studio_lint.py` ·
  `studio_validate.py` · `studio_evals.py` (`check_evals`, export, cổng catalog `RQ-018`) · `studio_scaffold.py` (`new`,
  `get_template`) · `studio_dist.py` (`package`, `install`, `move_aside`) · `studio_doctor.py` · `studio_fmt.py`.
- **Luật nạp (SPEC FR4.5, tuyệt đối — ADR-0001 sửa theo `RF13`):** mô-đun gọi nhau qua đối tượng mô-đun (`import studio_fs as fs`);
  cấm `from studio_* import …` và cấm `import studio` trong mọi `studio_*.py`; engine `studio.py` không re-export tên của mô-đun
  (để `patch.object(<facade>, tên)` ném `AttributeError` thay vì xanh giả, `RF3`); engine `studio.py` chèn thư mục của chính nó vào
  đầu `sys.path` rồi import, sau đó kiểm `Path(m.__file__).resolve().parent == Path(__file__).resolve().parent` cho mọi `studio_*`
  — lệch → stderr lời báo, thoát 2; mỗi mô-đun mở đầu `from __future__ import annotations` (Python 3.9, `RF22`). Test chạy engine
  khác chỗ (archive, ZIP) chỉ bằng subprocess.
- `datetime`: doctor/fmt tra qua mô-đun sở hữu (`studio_doctor.datetime`, `studio_fmt.datetime`); `cmd_install` giữ import cục bộ.
- **Shim gốc** `studio.py` (≤ 20 dòng, không `def`): `runpy.run_path(<thư mục shim>/skills/skill-creator-studio/scripts/studio.py,
  run_name="__main__")`, giữ `sys.argv`.
- **Khuôn:** chỉ `assets/skill-template/`, `assets/skill-template-full/` (+ `SKILL.vi.md` mới cho FR10, không chép ra khi tạo).
  `get_template` = `Path(studio_scaffold.__file__).resolve().parent.parent / "assets"`. `repo_root(start)` nhận gốc khi có
  `.claude-plugin/plugin.json` **và** `standards/SKILL_AUTHORING_STANDARD.md`.
- **Bộ ca hợp đồng (`RF5`, `RF6`, `RF7`, `RF11`):** mọi thứ dưới `tests/fixtures/contract/`: `inputs/` (ảnh chụp đóng băng từ
  `git archive 1211bfa`: `skills/skill-creator-studio`, `skills/data-quality-audit`, `evals/skill-creator-studio` gồm fixture
  `broken-skill`, `tests/fixtures/doctor`, một bản sao tối thiểu repo cho ca `--all`/`evals --all`), `cases.json`, `golden.json`
  (một file, khoá theo id ca: mã thoát, stdout JSON/chữ chuẩn hoá, tiền tố stderr, cây file + băm cho `new`/`package`/`install`).
  Runner `tests/contract_runner.py` chép đầu vào ra `tempfile`, dựng 5 cách gọi, chuẩn hoá đường tạm → `<TMP>`, gốc → `<REPO>`,
  giờ ISO → `<TS>`, `\` → `/` (không bỏ trường, không sắp xếp lại); `tests/test_contract_regression.py` so. Đáp án sinh một lần
  bằng `contract_runner.py --write-golden --engine <archive 1211bfa>`. Ca đổi có chủ ý mang `"changed_by": "<FR>"` và đáp án
  `"after"` riêng trong cùng `golden.json`. Thêm 3–5 ca «repo sống» chỉ so mã thoát.
  **Quy tắc ghép (`RF24`):** bản sao repo tạm = mã đang thử (shim gốc + `skills/skill-creator-studio` **sống** — skill mang engine)
  + `inputs/`. Ca so JSON nội dung (`validate`/`audit`/`fmt`/`doctor`) chỉ nhắm skill đóng băng **không mang engine**:
  `inputs/skills/data-quality-audit` và `inputs/skills/creator-frozen/` (bản chép `skill-creator-studio@1211bfa` đổi tên, bỏ
  `scripts/`). Skill mang engine chỉ là **đường gọi**; với nó (`validate --all`, `audit skills/skill-creator-studio`, `fmt --check
  skills/skill-creator-studio`, S/Z `validate <chính nó>`) chỉ so mã thoát. `inputs/` cho ca `evals --all` gồm
  `registry/catalog.json`, `evals/tools/activation.py`, `evals/<skill>/` (cases, fixtures, `runs/<sprint>/` mà catalog trỏ tới)
  (`RF26`).
- **Cổng catalog (`RQ-018`, DN8):** `studio_evals.catalog_problems(root)` + `AB_THRESHOLDS`, `RESULT_VALUES`, `_ran_logs` dời từ
  `tests/test_studio.py:26-165`. **Sửa sau kiểm định (`RF-S1`, DN8 → (b), `RF-T4`):** engine không nạp `activation.py`;
  `summarize` nằm trong `studio_evals` (đọc JSON qua helper an toàn), `evals/tools/activation.py` gọi ngược engine; cổng chỉ chạy khi
  repo có `evals/`; «thiếu `activation.py` → `EV20`» bỏ; `evals`/`sprint`/`date` từ catalog được kiểm (`RF-S2`). Đoạn dưới là thiết
  kế lúc Cổng 1, giữ để lần ngược. ~~`activation` nạp bằng `importlib.util.spec_from_file_location` **chỉ** từ
  `<repo_root(engine)>/evals/tools/activation.py` (không cwd, không biến môi trường).~~ Trước `summarize(runs_dir)`: duyệt `runs_dir`
  bằng `fs.walk_files`; link/cloud/vượt trần → `EV20` «runs dir not safe to count», không gọi `summarize` (`RF23`); `_ran_logs` đọc
  qua `fs.read_capped`/`open_nofollow_read`. `cmd_evals --all`: engine trong repo → chạy cổng, mỗi vấn đề một finding ERROR `EV20`;
  thiếu catalog hoặc thiếu `activation.py` trong repo → `EV20` (`RF26`); ngoài repo → bỏ qua. Test `tests/test_studio.py` gọi engine.
  Ghi chú `RF28`: bản cài plugin (cache) có `.claude-plugin/plugin.json` + `standards/` → được nhận là repo như hiện nay (cache cũng có
  `templates/`); không đổi hành vi, Tech Reviewer kiểm ở TK13.
- Không phụ thuộc ngoài thư viện chuẩn; Python 3.9 (`py -V:Astral/CPython3.9.25`, `RF22`).

## Ràng buộc chung

- Nguyên văn SPEC mục 1.1 (quy trình đủ, không secret, không `--no-verify`/force-push, người làm không tự chấm, hồ sơ trong
  `evidence/`, đẩy nhánh + CI Windows trước reviewer ký, dừng hỏi điều phối chỉ ở 4 trường hợp).
- **Nhãn test (`LN2` 1a):** mỗi test mới có đúng một nhãn `bắt-lỗi` / `tương-đương` / `đơn-vị-hàm-mới` trong docstring.
  **«Đỏ trước» (`RF4`):** test `bắt-lỗi` đỏ trên **commit cha của commit sửa** bằng assertion/mã thoát (không phải `ImportError`);
  viết test trước, commit sửa sau, ghi lệnh + dòng đỏ vào `evidence/tk<n>.txt`. Test FR8 (TK8): đỏ trên ≥ 1 đột biến.
- **Đổi mã thoát/mức báo ngoài SPEC mục 7 → Implementer dừng, báo Analyst trước khi làm** (`RF-T3` 1a).
- Test đổi có chủ ý (đích tham chiếu `studio.<tên>` → mô-đun, đường nạp, bỏ test byte-giống/`sync-template`) liệt kê trong
  `evidence/tk<n>.txt` kèm lý do. Không xoá test hành vi; không hạ ngưỡng.
- Working tree đã checkout lại LF ở TK0 (`evidence/tk0-baseline.txt`); file mới viết LF.
- Test cần link: `skipUnless` theo phép thử tạo link thật. Không tạo file trên cây cloud; cloud chỉ mock.
- Commit nhỏ theo TK, thông điệp `SPR-02 TK<n>: …` + `Co-Authored-By` của model làm. Nhánh đã đẩy (DN6) thì `git push` thường
  sau mỗi TK; không PR, không gộp.
- Chạy test: `python -X utf8 -m pytest -q -p no:cacheprovider` và `python -m unittest discover -s tests` (CI).
- Hook harness có thể chặn Edit/Write trong repo Studio: sửa bằng Python/Bash khi bị chặn; lệnh Bash > 6.000 ký tự bị hook chặn —
  ghi script ra file tạm rồi chạy.

## Trọng tâm review

1. **Test xanh giả sau tách:** reviewer chọn ≥ 5 test có `patch.object`, bỏ patch thử → test phải đỏ; engine không re-export.
2. **Hợp đồng:** bộ ca phủ 5 cách gọi; đầu vào đóng băng; chuẩn hoá không che khác biệt thật.
3. **Shim/sys.path/nạp `activation`:** không mở đường nạp mã lạ (cwd, biến môi trường); kiểm danh tính mô-đun.
4. **Ba lỗ `RQ-009`:** không stat/đọc đích link (mẫu `walk_files`); `PACK` chặn trước mọi đọc; `install --force` không chép xuyên.
5. **Cổng catalog không nới:** mọi ca tự kiểm cũ cho cùng kết luận trên engine; thiếu catalog không im lặng.

## Việc

PLAN có 18 **task** (TK), làm **tuần tự** trên nhánh `sprint/spr-02-one-source-1b` (một checkout, không worktree song song).

### TK0 — Nhánh và mốc (→ SC1, SC6)

- **Vai:** Analyst · T1 · claude-opus-5-5 · effort 2 (inline). **File:** chỉ `evidence/tk0-baseline.txt`.
- **Trạng thái:** đã làm 27/10 trước Cổng 1, không chạm mã: nhánh từ `1211bfa`, archive `%TEMP%\spr02-base\1211bfa`, pytest,
  unittest, coverage, `PR1`, blob trùng, checkout lại LF, danh sách 39 hàm đổi ở 1a.

### TK1 — Bộ ca hợp đồng đóng băng (→ FR11, SC1)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 4. **Đầu vào:** TK0, Kiến trúc «Bộ ca hợp đồng».
- **File:** `tests/fixtures/contract/**`, `tests/contract_runner.py`, `tests/test_contract_regression.py`.
- **Cách gọi:** R (cwd = bản sao repo tạm, `python studio.py`), C (cwd = thư mục tạm khác, đường tuyệt đối tới `studio.py` gốc của
  bản sao), E (cwd = `skills/skill-creator-studio` của bản sao, `python scripts/studio.py`, `RF7`), S (skill chép rời,
  `python <bản chép>/scripts/studio.py`), Z (`package` → giải nén → `scripts/studio.py`).
  Ghi chú: bản sao repo tạm dựng từ **mã đang thử** + `inputs/`; khi sinh đáp án, mã đang thử = archive `1211bfa`.
- **Ca tối thiểu (Implementer được thêm, không bớt):**
  - R, C, E: `--version`; `validate --all --require-evals --json`; `audit skills/skill-creator-studio --json`; `audit` chế độ chữ;
    `validate` skill hỏng `--json` (thoát 1); `validate` đường không có (thoát 2); `evals --all --json`; `doctor --roots
    tests/fixtures/doctor --json`; `fmt --check skills/skill-creator-studio --json`; `new` ×4 (`en`, `--lang vi`, `--full`,
    `--full --lang vi` [đổi FR10]) ra thư mục tạm; E thêm `new` **không** `--output` (ghi vào `<repo>/skills`); `package
    skills/data-quality-audit`; `install skills/data-quality-audit --agent claude --workspace <tạm>`; `sync-template --check`
    [đổi FR3, chỉ so mã thoát].
  - S, Z: `--version`; `validate <chính nó> --json`; `new` ×3; `doctor --roots <cha bản chép> --json`; `fmt --check <chính nó> --json`.
  - Repo sống (chỉ mã thoát): `validate --all --require-evals`, `evals --all`, `package skills/skill-creator-studio`.
- **Bước:** viết runner + ca; sinh đáp án từ archive `1211bfa`; chạy so trên nhánh (chưa sửa engine) → 100 % khớp, hai lần
  liên tiếp; đo thời gian thêm vào bộ test (> 60 s → gộp ca theo cách gọi).
- **Hoàn tác:** `git revert`. **Bằng chứng:** `evidence/tk1.txt` (số ca, thời gian).

### TK1b — Đẩy nhánh, CI đáp án (→ FR11.4, SC3)

- **Vai:** Analyst · T1 · inline · effort 1. **Bước:** `git push -u origin sprint/spr-02-one-source-1b`; `gh workflow run ci.yml
  --ref <nhánh>`; CI 4/4 xanh trên commit TK1 trước khi sang TK2. Đỏ vì lệch môi trường → Implementer sửa chuẩn hoá, không sửa đáp án tay.

### TK2 — Shim gốc, test nạp engine, `VERSION` một chỗ (→ FR1, SC1)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 3. **Đầu vào:** TK1b.
- **File:** `studio.py` (gốc → shim), engine `scripts/studio.py` (chèn `sys.path`), `tests/_engine.py` (mới: nạp engine một lần,
  xoá `lru_cache` dùng chung trong helper `setUp`), `tests/*.py` (5 file nạp gốc → engine; subprocess vẫn gọi shim),
  `tests/test_plugin_manifests.py` (đọc `VERSION` từ engine), test văn bản/AST (`test_cloud_package.py:222`, `test_doctor.py:881`,
  `test_fmt.py:566`, `test_standards.py:290`) quét engine.
- **Bước:** test `bắt-lỗi` (viết trước, đỏ trên commit cha): shim ≤ 20 dòng không chứa `def `; test subprocess shim từ cwd khác
  cho cùng stdout + mã thoát như engine; thay test byte-giống bằng test «gốc là shim»; sửa đường nạp.
- **Cách kiểm:** bộ ca hợp đồng 100 %; cả bộ xanh. **Bằng chứng:** `evidence/tk2.txt` (liệt kê test đổi).

### TK3 — Khuôn chỉ ở `assets/`, bỏ `sync-template` (→ FR2, FR3, SC2)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 3. **Đầu vào:** TK2.
- **File:** `git rm -r templates/skill-template templates/skill-template-full`; engine (`repo_root`, `get_template`, bỏ `cmd_sync`,
  `TEMPLATE_PAIRS`, `mirror_diff` nếu không còn người dùng, parser); `.github/workflows/ci.yml` (bỏ bước); tests (`:353`, `:992`,
  `:1017-1022` bỏ/đổi có chủ ý); `skills/skill-creator-studio/SKILL.md:27,37,43` («bundled mirrors»); `templates/README.md`;
  `README.md:52,112` (bỏ hứa `templates/skill-template/SKILL.md` là đường cứng), `:265` (lệnh QA `fmt --check … templates/…`), `:268`
  (`RF16`). **Không** sửa `AGENTS.md` (SPEC/CQ1 → TK10).
- **Bước:** test `bắt-lỗi`: `new` trong repo lấy `assets/` (khuôn `templates/` khác `assets/` → đỏ trên commit cha); `repo_root`
  nhận gốc không có `templates/`; `sync-template` thoát 2.
- **Cách kiểm:** bộ ca hợp đồng (ca `sync-template` sang `after`); SC2 đếm 0 ngoài vùng loại trừ; `fmt --check` lệnh QA README
  chạy được. **Bằng chứng:** `evidence/tk3.txt`.

### TK4a / TK4b / TK4c — Tách mô-đun phẳng theo ba lát (→ FR4, ADR-0001, SC1)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 4 mỗi lát. **Đầu vào:** TK3. Mỗi lát một commit; Analyst xem diff lát
  trước khi giao lát sau.
- **Lát:** TK4a `studio_const` + `studio_fs` (lá) + luật nạp + kiểm danh tính; TK4b `studio_lint`, `studio_validate`, `studio_evals`;
  TK4c `studio_scaffold`, `studio_dist`, `studio_doctor`, `studio_fmt` + CLI `studio.py` ≤ 300 dòng + `SKILL.md` một dòng nêu các
  mô-đun nội bộ (`RF2`, chung commit với lát tạo mô-đun cuối).
- **Quy mô test (`RF3`):** ~392 tham chiếu `studio.<tên>` tới ~60 tên + ~40 `patch.object` + tiến trình con `CHILD`/`CHILD3`
  (`tests/test_doctor.py:486-489,821-824`) → đổi sang mô-đun sở hữu qua `tests/_engine.py` (`E.fs`, `E.lint`, …). Patch đặt ở
  mô-đun **gọi** tên (vd `path_is_cloud` patch ở `studio_fs` nếu mọi nơi gọi `fs.path_is_cloud`).
- **Bước mỗi lát:** chuyển khối nguyên văn (không sửa logic); đổi gọi chéo sang `mod.tên`; dời `_remove_quietly` xuống
  `studio_fs` (TK4a); sửa tham chiếu test, liệt kê (tên · file:dòng · mô-đun đích); test `tương-đương` mới ở TK4a: AST — không
  `from studio_* import`, không `import studio` trong `studio_*`, mọi `studio_*.py` có `from __future__ import annotations`; engine
  `studio.py` không có thuộc tính trùng tên công khai của `studio_*`; kiểm tĩnh cũ (regex tuyến tính, cấm `subprocess`, quét `SZ2`)
  quét mọi `studio*.py` của engine. TK4a thêm test `bắt-lỗi` hành vi cho kiểm danh tính (`RF25`): tiến trình con nạp engine ở thư
  mục A rồi nạp bản chép engine ở thư mục B (trong cùng tiến trình) → thoát 2 kèm lời báo.
- **Cách kiểm mỗi lát:** bộ ca hợp đồng 100 %; cả bộ xanh; Python 3.9 (`py -V:Astral/CPython3.9.25 -X utf8 -m unittest discover -s
  tests`); TK4c: `validate skills/skill-creator-studio` 0 WARN mới, ca Z xanh. **Bằng chứng:** `evidence/tk4a.txt`, `tk4b.txt`, `tk4c.txt`.

### TK5 — Lệnh `check` (→ FR5, SC8)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 3. **Đầu vào:** TK4c. **File:** engine `studio.py` (parser), `studio_validate.py`; tests.
- **Bước:** test `bắt-lỗi` (đỏ trên commit cha vì không có lệnh — argparse thoát 2 ≠ đáp án): `check <skill> --json` khớp sơ đồ SPEC
  FR5.2 (`type` ở mỗi phần tử `reports`, cả `--all`); `check SKILL.md`; `check` file `type: workflow` / `AGENTS.md` thoát 2 lời báo
  FR5.3; file không nhận loại thoát 2; cờ FR5.2. Bí danh giữ nguyên (bộ ca hợp đồng). **Bằng chứng:** `evidence/tk5.txt`.

### TK6 — Cổng `model_evaluated` vào engine (→ FR6, SC10)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 3. **Đầu vào:** TK4c. **File:** `studio_evals.py`, engine CLI, `tests/test_studio.py`, `README.md` (mã `EV20`).
- **Bước:** test `bắt-lỗi` (đỏ trên commit cha: thoát 0): `evals --all` trên bản sao repo tạm có catalog hỏng → thoát 1 + `EV20`;
  bản sao repo thiếu catalog → `EV20`; ~~có catalog mà thiếu `activation.py` → `EV20`~~ (bỏ ở vòng sửa 1, `RF-S1`); `runs/` chứa `*.json` là
  symlink (`skipUnless`) hoặc mock `entry_is_cloud` → `EV20` và spy xác nhận `summarize` không được gọi (`RF23`); ZIP/skill rời → bỏ
  qua, thoát như đáp án; `activation.py` giả đặt ở **cwd** (không phải repo
  của engine) không được nạp (đánh dấu file ghi khi nạp). Dời logic nguyên văn; mọi ca tự kiểm `:378-579` chạy trên engine;
  `grep -n AB_THRESHOLDS tests/` = 0 định nghĩa. **Bằng chứng:** `evidence/tk6.txt`.

### TK7 — Ba lỗ link/cloud `RQ-009` (→ FR7, SC5, SC7)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 4. **Đầu vào:** TK4c. **File:** `studio_fs.py`, `studio_fmt.py`, `studio_doctor.py`, `studio_dist.py`; tests.
- **Hành vi:** (a) `iter_md`/`skill_dirs`/`_is_dir_quiet` theo mẫu `walk_files` (`is_symlink()` → cloud → `is_dir(follow_symlinks=False)`
  → `is_link(path)`) hoặc gọi `walk_files`; link → bỏ qua có báo như walk khác (`RF10`). (b) `ensure_distributable` kiểm `SKILL.md`,
  manifest bằng `is_link`/cloud/`input_file_problem` **trước** `validate_skill` và `read_text`; vi phạm → `PACK`, không đọc.
  (c) `move_aside` nhánh khác ổ (`os.rename` ném `OSError` `EXDEV`, `RF18`): duyệt cây cũ không theo link; gặp junction/symlink/cloud
  → không chép, thoát 1 lời báo, bản cũ nguyên (DN5).
- **Bước:** test `bắt-lỗi` bằng mock (đếm lời gọi stat theo đích; `path_is_cloud` cho `SKILL.md` + phát hiện đọc; `os.rename` ném
  `EXDEV` theo mẫu `tests/test_install_safe.py:182`) + test link/junction thật `skipUnless` (chạy ở CI Windows) cho cả ba hàm (a).
- **Bằng chứng:** `evidence/tk7.txt`.

### TK8 — Đột biến và coverage `RQ-011` (→ FR8, SC6)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 4. **Đầu vào:** TK5–TK7 + `evidence/mutants.md` (Analyst, 19 đột biến,
  chốt trước).
- **File:** tests; `evidence/mutants.json` + `evidence/run_mutants.py` ở sổ (không vào repo Studio, `RF9`).
- **Bước:** viết `mutants.json` đúng bảng `mutants.md` (không thêm/bớt); script áp từng đột biến lên bản chép `git archive HEAD` ở
  `%TEMP%`, chạy bộ test, ghi chết/sống; chạy trước khi thêm test → ghi số sống; thêm test tới khi 100 % chết; đo coverage
  `--branch` FR8.2 (i)–(iii) bằng `coverage json` + `git diff -U0 <commit TK4c>..HEAD` (script tạm, xoá sau, lệnh ghi evidence).
- **Bằng chứng:** `evidence/tk8.txt`.

### TK9 — `PR1` và `new --full --lang vi` (→ FR9, FR10, SC8)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 3. **Đầu vào:** TK4c.
- **File:** `references/NEW_WORKFLOW.md` (gồm `:21` «`--full --lang vi` exits 2», `RF16`), `REFINE_WORKFLOW.md`;
  `assets/skill-template-full/SKILL.vi.md` (mới); `studio_scaffold.py`; `SKILL.md:43` («English-only…»); tests.
- **Bước:** bảng đối chiếu bước cũ → mới cho hai file (evidence); viết lại đúng hình `PR1`; test `bắt-lỗi` `new --full --lang vi`
  thoát 0, `SKILL.md` là bản vi, không có `SKILL.vi.md` thừa trong đích, skill sinh `validate` 0 ERROR; `new --full` (en) cây không đổi.
- **Bằng chứng:** `evidence/tk9.txt`.

### TK10 — Tài liệu, CHANGELOG, `AGENTS.md` (→ FR3.1, SPEC mục 7, SPEC/CQ1)

- **Vai:** Implementer · T2 · claude-sonnet-5-5 · effort 2. **File:** `README.md` (lệnh `check`, mã `EV20`, bố cục engine),
  `CHANGELOG.md` (`Unreleased`: mọi dòng SPEC mục 7); `AGENTS.md:36` đúng **một dòng** và một mốc CHANGELOG trong cùng commit, chỉ
  khi Fable gật CQ1 (câu duyệt ở PROGRESS); từ chối → giữ dòng, `CO` chặng 2 (`RQ-186`).
- **Cách kiểm:** `tests/test_docs_links.py` xanh; `grep -rn "sync-template\|templates/skill-template"` chỉ còn ở CHANGELOG, `QA_REPORT.md`
  (nhật ký, để nguyên). **Bằng chứng:** `evidence/tk10.txt`.

### TK11 — CI trước kiểm định (→ SC3)

- **Vai:** Analyst · T1 · inline · effort 2. **Bước:** kiểm diff nhánh chỉ chạm file trong Kiến trúc/TK; `git push`;
  `gh workflow run ci.yml --ref <nhánh>`; 4/4 xanh trước TK13. Đỏ → TK sửa tương ứng.

### TK12 — QA (→ SC1, SC2, SC5, SC6, SC8, SC9, SC10)

- **Vai:** QA · T3 · claude-sonnet-5-5 · effort 3 (subagent riêng, không viết mã sprint).
- **Bước:** chạy từng test `bắt-lỗi` trên commit cha của commit sửa và ở HEAD; bộ ca hợp đồng; đếm blob; `run_mutants.py` ở HEAD;
  coverage FR8.2; `fmt --check` `PR1`; `system/evals/run.ps1 -Tier fast`. **Bằng chứng:** `evidence/qa.md`, `qa-*.txt`.

### TK13 — Kiểm định độc lập (→ SC7, mọi FR)

- **Vai:** Tech Reviewer · T1 · claude-opus-5-5 · 4; Security Reviewer · T1 · claude-opus-5-5 · 5 (FR1 shim/`sys.path`, FR4.5 danh
  tính mô-đun, FR6.4 nạp `activation` + đọc log, FR7); Business Reviewer · T1 · claude-fable-5-1 · 3. Chạy sau TK11 xanh. Vòng sửa
  giao Implementer; khuyến nghị tối đa 3 vòng.
- **Bằng chứng:** `evidence/review-{tech,security,business}.md`.

### TK14 — Lô «không hồi quy» 16 lượt (→ FR13, SC4)

- **Vai:** QA · T3 · claude-sonnet-5-5 · 3. **Đầu vào:** HEAD sau review cuối = `SHA lô`, CI xanh.
- **Bước:** theo RUNBOOK «Luật lô»; thư mục log `evals/<skill>/runs/studio-SPR-02/` (DN7); `redact.py` trước `git add`;
  `manifest.json` `batch_sha` 40 hex + `batch_sha_kind: commit`; `activation.py summarize`. Sau lô chỉ commit `evals/**/runs/`
  (không chạm `skills/`, engine). `registry/catalog.json` **không đổi**: giữ `model_evaluated: false`, không thêm/sửa khối
  `evaluated` (A/B là chặng 4) — cổng `EV20` phải vẫn xanh ở commit gộp (`RF20`).
- **Bằng chứng:** `evidence/batch.md`.

## Rủi ro

PLAN có 8 **risk** (RK):

| Mã | Rủi ro | Mức | Giảm thiểu |
|---|---|---|---|
| RK1 (test xanh giả sau tách) | tham chiếu/patch trỏ facade, mô-đun gọi không bị patch | Phải sửa | luật nạp tuyệt đối + cấm re-export (`AttributeError` thay vì xanh giả); test AST; Trọng tâm review 1 |
| RK2 (gãy người gọi) | shim/ZIP/skill rời/engine trong repo cho kết quả khác | Phải sửa | TK1 đầu vào đóng băng, 5 cách gọi, CI 4 ô trước sửa (TK1b); mọi TK sau chạy bộ ca |
| RK3 (nạp mã lạ) | `sys.path` chèn, mô-đun cùng tên đã cache, `activation` dò theo cwd | Phải sửa | chỉ chèn thư mục engine; kiểm danh tính; `activation` chỉ từ `repo_root(engine)`; Security review |
| RK4 (băm skill đổi nhiều lần) | review tìm sửa trong `skills/` sau lô | Nên sửa | lô chỉ sau review cuối (TK14), luật lô 3 |
| RK5 (Windows-only không thử được cục bộ) | junction/symlink không tạo được trên máy | Nên sửa | mock + `skipUnless`; CI Windows trước TK13 |
| RK6 (phình phạm vi) | 9 nhóm việc, ~430 chỗ test đổi | Nên sửa | TK4a/TK4b/TK4c ba lát; US4 «Nên có»: TK9 cắt thành `CO` nếu hết effort; FR1–FR8, FR11 không cắt |
| RK7 (lệch môi trường đáp án) | đáp án Windows 3.12, CI 4 ô | Nên sửa | stderr chỉ tiền tố; JSON không phụ thuộc thứ tự `scandir` khi engine đã sắp; TK1b chứng 4/4 |
| RK8 (cổng im lặng ở chặng 2) | dời catalog làm cổng ngừng chạy | Ghi chú | thiếu catalog trong repo → `EV20` (FR6.2) |

## Quyết định cần người

PLAN có 9 **decision** (DN) cần người duyệt (Fable duyệt hộ theo uỷ quyền Đức 27/10):

| Mã | Câu hỏi | Lựa chọn | Khuyến nghị | Trạng thái |
|---|---|---|---|---|
| DN1 (cách tách, ADR-0001) | Chọn phương án nào của ADR-0001? | A giữ · B engine ở gốc · C một file trong skill · D mô-đun phẳng gọi qua mô-đun · E namespace gộp | D — thoả shim + chạy rời + tái dùng chặng 3; E cho test xanh giả | chốt |
| DN2 (`check` loại khác skill) | Loại workflow/rules ở 1b? | (a) thoát 2 «chưa có» · (b) lint tối thiểu frontmatter | (a) — `DOC_TYPES.md` là chặng 2; tránh hợp đồng nửa vời | chốt |
| DN3 (chỗ chạy cổng catalog) | Cổng `RQ-018` chạy ở đâu? | (a) trong `evals --all` khi engine trong repo · (b) cờ mới `evals --catalog` | (a) — CI đã gọi `evals --all`; không thêm bề mặt | chốt |
| DN4 (khuôn full tiếng Việt) | Cách làm `new --full --lang vi`? | (a) `assets/skill-template-full/SKILL.vi.md`, không chép ra · (b) thư mục `skill-template-full-vi/` | (a) — (b) sinh blob trùng, trái SC2 | chốt |
| DN5 (`install --force` khác ổ gặp link) | Cây cũ có junction/symlink khi phải chép? | (a) từ chối, thoát 1, bản cũ giữ · (b) chép link như link | (a) — tái tạo junction trên Windows không chắc; người dùng gỡ tay | chốt |
| DN6 (đẩy nhánh sprint) | Đẩy nhánh lên origin để CI ma trận chạy? | — | đã chốt theo lời giao (SPEC 1.1, `LN1` 1a); áp từ TK1b (`RF19`) | chốt |
| DN7 (thư mục log lô) | Tên thư mục log lô? | (a) `runs/studio-SPR-02/` · (b) `runs/SPR-02/` | (a) — `SPR-18`/`SPR-33` cùng chỗ là mã sổ đối tác; tránh đọc nhầm | chốt |
| DN8 (nguồn `activation` cho cổng, `RF1`) | Engine lấy `activation.summarize` từ đâu? | (a) nạp chỉ từ `repo_root(engine)/evals/tools/`; duyệt `runs/` bằng `walk_files` trước, link/cloud/vượt trần → `EV20` không gọi `summarize` (`RF23`) · (b) dời `summarize` vào `studio_evals`, `activation.py` import ngược · (c) cổng thành `evals/tools/catalog_gate.py` ngoài engine | (a) — diff đúng cỡ, không đổi công cụ lô, một bản `activation`; (c) không đạt `RQ-018` | chốt (a) ở Cổng 1 → đổi sang (b) sau kiểm định `RF-S1` (Phán quyết Analyst PROGRESS 22:30; Fable xác nhận ở Cổng 2) |
| DN9 (SC2 lệch ROADMAP, `RF15`) | ROADMAP «không còn blob trùng»; 11 blob `runs/SPR-18` + 1 fixture còn | (a) loại trừ có duyệt, `runs/` theo `RQ-004` chặng 2 · (b) xử lý ngay ở 1b (dời bằng chứng thô) | (a) — dời bằng chứng thô là việc chặng 2 (ROADMAP mục 3), làm ở 1b đổi phạm vi | chốt |

## Ước lượng

| Việc | Phiên agent | Lần hỏi người |
|---|---|---|
| TK0 | 0,2 | 0 |
| TK1 (bộ ca) + TK1b (CI) | 1,5 | 0 |
| TK2 (shim) | 0,7 | 0 |
| TK3 (khuôn, sync) | 0,6 | 0 |
| TK4a/b/c (tách) | 3 | 0 |
| TK5 (`check`) | 0,5 | 0 |
| TK6 (cổng) | 0,6 | 0 |
| TK7 (`RQ-009`) | 1 | 0 |
| TK8 (đột biến) | 1 | 0 |
| TK9 (`PR1`, vi) | 0,7 | 0 |
| TK10 (tài liệu) | 0,3 | 0 (SPEC/CQ1: Fable) |
| TK11 (CI) | 0,2 | 0 |
| TK12 (QA) | 1 | 0 |
| TK13 (review ×3, một vòng sửa) | 2,5 | 0 |
| TK14 (lô) | 0,5 | 0 |
| Cộng | 14,3 | 0 (Cổng 1, Cổng 2, SPEC/CQ1: Fable duyệt hộ) |

## Bản ghi duyệt thay

Cổng 1 do Business Reviewer T1 `claude-fable-5-1` (subagent riêng, không viết SPEC/PLAN) duyệt hộ theo lời cấp ở
`delegation.grant`; kết luận **Duyệt có điều kiện**; hồ sơ đầy đủ `evidence/gate1-fable.md`.

- **Phương án chọn:** DN1 D, DN2 (a), DN3 (a), DN4 (a), DN5 (a), DN7 (a), DN8 (a) kèm `RF23`, DN9 (a) chỉ hai vùng loại trừ; DN6 đã chốt.
- **Phương án bị loại:** DN1 A/B/C/E (ADR-0001), DN2 (b), DN3 (b), DN4 (b), DN5 (b), DN7 (b), DN8 (b)/(c) lúc Cổng 1 (DN8 sau đổi sang (b) — PROGRESS 22:30), DN9 (b).
- **Nếu sai thì tốn gì:** theo `evidence/gate1-fable.md` từng DN; lớn nhất DN1 — gộp lại mô-đun, ~nửa phiên agent.
- **Điều kiện:** ĐK1 REPORT ghi «lệch có duyệt» + danh sách blob trùng còn lại ở commit gộp, `RQ-004` nhận dòng đích danh 11 blob
  `runs/SPR-18`; ĐK2 TK12 chạy `evals --all` trên archive HEAD đóng vai bản cài và đối chiếu cache plugin thật (`registry/`,
  `evals/tools/`), thiếu → Analyst phán quyết trước Cổng 2; ĐK3 sửa số TK (18), PROGRESS đủ dòng, dossier :97-99 (đã làm).
- **SPEC/CQ1 (file luật):** gật — sửa đúng `AGENTS.md:36` ở TK10 (sau TK3), cùng commit mốc CHANGELOG; `CO` nếu có trỏ `RQ-004`.
