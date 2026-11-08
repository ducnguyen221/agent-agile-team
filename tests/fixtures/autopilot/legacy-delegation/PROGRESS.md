---
id: SPR-02-progress
doc: progress
title: "Chặng 1b: một nguồn cho agent-skill-studio"
sprint: SPR-02
request: RQ-003
feature: null
status: done
size: large
risk: high
risk_tags: [public_api, infra]
review_round: 2
roles:
  analyst: [T1, coordinator]
  architect: [T1, coordinator]
  implementer: [T2, claude-sonnet-5-5, "Sonnet High theo phân vai Đức 23/10 (memory feedback_model_roles_sonnet_fable_opus); bảng tier AGENT_AGILE_TIERS trỏ file không có, đo 27/10"]
  qa: [T3, sonnet-qa-subagent, "claude-sonnet-5-5, subagent riêng (TK12, TK14), không viết mã sprint"]
  business-reviewer: [T1, claude-fable-5-1]
  tech-reviewer: [T1, claude-opus-5-5]
created: 2026-10-27
updated: 2026-10-27
links:
  spec: SPEC.md
  plan: PLAN.md
  report: REPORT.md
---

# Chặng 1b: một nguồn cho agent-skill-studio — Tiến độ (PROGRESS)

> **Kết luận:** 18/18 việc xong (TK14 Đạt có điều kiện); 2 vòng kiểm định, Tech/Security/Business ký; Cổng 2 Đạt có điều kiện (Fable duyệt hộ); Studio `main` = `3cc1bd3`, CI `40552921951` 4/4.

## 1. Bảng trạng thái việc

PLAN có 18 **task** (TK); bảng ghi trạng thái từng việc:

| Việc | Vai · tier · model · effort | Trạng thái | Bằng chứng |
|---|---|---|---|
| TK0 (nhánh, mốc) | Analyst · T1 · claude-opus-5-5 · 2 | Đạt | `evidence/tk0-baseline.txt`; nhánh `sprint/spr-02-one-source-1b` @ `1211bfa`; pytest 434 passed 4 skipped; coverage hợp hai bản 89,2 %; 12 `PR1`; 9 blob trùng ngoài vùng loại trừ |
| TK1 (bộ ca hợp đồng) | Implementer · T2 · claude-sonnet-5-5 · 4 | Đạt | Studio `6407a06`; 96 ca (R 22 · C 22 · E 23 · S 13 · Z 13 · sống 3); đáp án từ archive `1211bfa`; so 2 lần OK; pytest 437 passed 4 skipped; unittest 441 OK; Py 3.9 OK; blob trùng 9 = TK0 — `evidence/tk1.txt` |
| TK1b (CI đáp án) | Analyst · T1 · claude-opus-5-5 · 1 | Đạt | run `40505017074` (`6407a06`) ubuntu 2/2 đỏ do lệch môi trường; vòng sửa `8b155ca`; run `40506026587` 4/4 xanh |
| TK2 (shim) | Implementer · T2 · claude-sonnet-5-5 · 3 | Đạt | Studio `e5efede`; shim 14 dòng (runpy); 3 test `bắt-lỗi` đỏ trên `8b155ca`; `tests/_engine.py`; bộ ca hợp đồng OK — `evidence/tk2.txt` |
| TK3 (khuôn, sync) | Implementer · T2 · claude-sonnet-5-5 · 3 | Đạt | Studio `332070d`; 4 test `bắt-lỗi` đỏ trên `e5efede`; blob trùng ngoài vùng loại trừ = 0; pytest 442 passed 4 skipped; unittest 3.12 + 3.9.25 446 OK — `evidence/tk3.txt` |
| TK4a (const + fs) | Implementer · T2 · claude-sonnet-5-5 · 4 | Đạt | Studio `1c3beb8`; `studio_const.py` 104 + `studio_fs.py` 604 dòng, engine 2.103; 115 tham chiếu test đổi; test kiểm danh tính (plan-review `RF25`) đỏ trên `332070d` (`0 != 2`); pytest 448 passed 4 skipped; unittest 3.12 + 3.9 452 OK — `evidence/tk4a.txt` |
| TK4b (lint, validate, evals) | Implementer · T2 · claude-sonnet-5-5 · 4 | Đạt | Studio `156225a`; `studio_lint` 346 · `studio_validate` 202 · `studio_evals` 266 dòng, engine 1.338; 91 tham chiếu test đổi; không vòng import; pytest 448 passed 4 skipped; unittest 3.12 + 3.9 452 OK — `evidence/tk4b.txt` |
| TK4c (scaffold, dist, doctor, fmt, CLI) | Implementer · T2 · claude-sonnet-5-5 · 4 | Đạt | Studio `395e621`; engine `studio.py` 197 dòng + 9 mô-đun; 100 tham chiếu test đổi; `validate skills/skill-creator-studio` 0/0; ZIP 10 file `studio*.py`; pytest 448 passed 4 skipped; unittest 3.12 + 3.9 452 OK — `evidence/tk4c.txt` |
| TK5 (`check`) | Implementer · T2 · claude-sonnet-5-5 · 3 | Đạt | Studio `37fb2f9`; test `bắt-lỗi` đỏ trên `395e621` (argparse thoát 2); bí danh giữ (bộ ca OK) — `evidence/tk5.txt` |
| TK6 (cổng catalog) | Implementer · T2 · claude-sonnet-5-5 · 3 | Đạt | Studio `66a798b`; `catalog_problems` trong `studio_evals`; 5 ca CLI đỏ trên cha (`1 != 0`); `grep AB_THRESHOLDS *= tests/` = 0; pytest 476 passed 6 skipped; unittest 3.12 + 3.9 482 OK — `evidence/tk6.txt` |
| TK7 (`RQ-009`) | Implementer · T2 · claude-sonnet-5-5 · 4 | Đạt | Studio `6592429`; `tests/test_link_holes.py` 21 test, 16 đỏ trên `66a798b`; junction thật chạy được trên máy — `evidence/tk7.txt` |
| TK8 (đột biến) | Implementer · T2 · claude-sonnet-5-5 · 4 | Đạt | Studio `9a100d4`, `d0792cb`, `df4043b`; đột biến trước 10 chết/9 sống ở `913306a` → 19/19 chết; coverage (i) 88,0 % · (ii) 90,7 % · (iii) 91,4 %; pytest 540 passed 7 skipped; unittest 3.12 + 3.9 547 OK — `evidence/tk8.txt`, `mutants.json`, `run_mutants.py` |
| TK9 (`PR1`, vi) | Implementer · T2 · claude-sonnet-5-5 · 3 | Đạt | Studio `88deee2`; `tests/test_new_full_vi.py` 9 test đỏ trước; `fmt --check` skill 0 `PR1`; `validate` skill 0/0; 3 ca `after` — `evidence/tk9.txt` |
| TK10 (tài liệu) | Implementer · T2 · claude-sonnet-5-5 · 2 | Đạt | Studio `913306a`; `AGENTS.md:36` diff 1−/1+ đúng câu duyệt + mốc CHANGELOG cùng commit; pytest 505 passed 7 skipped; unittest 3.12 + 3.9 512 OK — `evidence/tk10.txt` |
| TK11 (CI) | Analyst · T1 · claude-opus-5-5 · 2 | Đạt | 0 file ngoài phạm vi (134 file `1211bfa..df4043b`); CI `40528630643` 4/4 xanh trên `df4043b` |
| TK12 (QA) | QA · T3 · claude-sonnet-5-5 · 3 | Đạt (vòng 1, trên `df4043b`) | SC1, SC2 (lệch DN9), SC5, SC6, SC8, SC9 (`run.ps1 -Tier fast` ĐẠT 1.078 s), SC10 Đạt; ĐK2: cache 0.1.0 thiếu `evals/tools/` → giải bằng `RF-S1` — `evidence/qa.md` |
| TK13 (kiểm định) | Tech Reviewer · T1 · claude-opus-5-5 · 4; Security Reviewer · T1 · claude-opus-5-5 · 5; Business Reviewer · T1 · claude-fable-5-1 · 3 | Đạt (vòng 2) | Tech Đạt; Security Đạt có điều kiện (0 Chặn/Phải sửa; `RF-S7` có từ 1a → `CO`); Business Đạt có điều kiện (ĐK đóng sprint) — `evidence/review-{tech,security,business}.md` |
| TK14 (lô 16 lượt) | QA · T3 · claude-sonnet-5-5 · 3 | Đạt có điều kiện | Studio `e59ef52`; 16/16 ran; `skill-creator-studio` 2/5 · 0/3; `data-quality-audit` 2/5 · 0/3 (dưới ngưỡng); đối chứng `1211bfa` 4/5 = `f1e3f71` 4/5 (Claude Code 2.1.310) — `evidence/batch.md`, `control-TK14/` |

## 2. Nhật ký

- **2026-10-27 18:30 +07** — Analyst (claude-opus-5-5) nhận lời giao của phiên điều phối chương trình «dời skill» («mở Studio 1b»):
  chạy chặng 1b = SPR-02, đủ quy trình; Fable duyệt hộ Cổng 1/Cổng 2/gộp/push theo uỷ quyền Đức 27/10.
- **2026-10-27 18:45 +07** — Researcher T3 (claude-sonnet-5-5, subagent Explore, chỉ đọc) lập `evidence/dossier-1b.md`.
- **2026-10-27 18:55 +07** — Mở sprint bằng `init.py` (SPR-02, `RQ-003`); viết SPEC, PLAN, ADR-0001 (`adr/0001-engine-in-skill-flat-modules.md`).
- **2026-10-27 19:05 +07** — TK0 Đạt (inline, trước Cổng 1, không chạm mã). Gửi plan-review cho Tech Reviewer T1 (claude-opus, subagent
  mới). Hỏi điều phối CQ1 (sửa `AGENTS.md:36`, trình 5 ý).
- **2026-10-27 19:10 +07** — Điều phối trả lời CQ1: Fable (subagent của phiên này) xét 5 ý sửa `AGENTS.md:36` theo uỷ quyền Đức;
  gật → sửa đúng một dòng ở TK10 + mốc CHANGELOG Studio cùng commit; từ chối → giữ dòng, `CO` chặng 2 (`RQ-186`). Đưa vào Cổng 1.

- **2026-10-27 19:15 +07** — Plan-review vòng 1 (Tech Reviewer T1 claude-opus, subagent mới): Không đạt — 1 Chặn (`RF1` nguồn
  `activation`), 9 Phải sửa, 7 Nên sửa, 5 Ghi chú (`evidence/plan-review-opus.md`). Analyst nạp cả 22: TK1b CI sau TK1, tách mô-đun chia ba lát TK4a/TK4b/TK4c (bản đầu một việc), chia ba
  lát, đầu vào hợp đồng đóng băng + cách gọi E, SC5 «đỏ trên commit cha», SC6 coverage nhánh, DN8, DN9. Checkout lại working tree LF.
- **2026-10-27 19:20 +07** — Plan-review vòng 2: Đạt có điều kiện — 22/22 đóng; mới `RF23` (Phải sửa, `summarize` tự đọc log →
  duyệt `walk_files` trước), `RF24` (Phải sửa, quy tắc ghép đầu vào hợp đồng), `RF25`, `RF26` (Nên sửa), `RF27`, `RF28` (Ghi chú) —
  Analyst nạp hết vào SPEC FR6.4, PLAN Kiến trúc/TK4a/TK6. Đã tới trần 2 vòng plan-review.
- **2026-10-27 19:23 +07** — Cổng 1: Business Reviewer T1 `claude-fable-5-1` (subagent riêng) duyệt hộ theo uỷ quyền Đức 27/10 —
  Duyệt có điều kiện; DN1 D, DN2–DN5 (a), DN7 (a), DN8 (a), DN9 (a); ĐK1–ĐK3 (`evidence/gate1-fable.md`; ĐK3 đã làm). CQ1:
  «Gật CQ1: sửa đúng một dòng `AGENTS.md:36` của repo Studio thành "Templates live only in `skills/skill-creator-studio/assets/`;
  edit them there and rerun tests.", làm ở TK10 sau TK3, cùng commit với mốc CHANGELOG, không chạm dòng nào khác — Fable duyệt hộ
  theo uỷ quyền Đức (sửa file luật)». Giao TK1.

- **2026-10-27 19:40 +07** — TK1 Đạt (`6407a06`). Phán quyết Implementer: `validate` đường không có thoát 1 (`FM1`), không 2 như PLAN — giữ đáp án thật, thêm ca không đối số (thoát 2); băm `SHA256:` của `package` chuẩn hoá thành `<SHA>` vì mtime ZIP khác máy — sai thì tốn một ca không khoá băm gói (tên file trong ZIP vẫn khoá). Analyst chạy lại `unittest tests.test_contract_regression` → OK. TK1b: đẩy nhánh, CI `40505017074`.

- **2026-10-27 19:45 +07** — TK1b: CI `40505017074` trên `6407a06` windows xanh, ubuntu đỏ 21 ca: `new` ghi CRLF trên Windows (`write_text` không `newline`) và thứ tự `files` của `fmt` theo OS. Phán quyết: chuẩn hoá runner (băm sau CRLF→LF; sắp riêng `files` của `fmt`) — vì đó là khác biệt môi trường có sẵn ở `1211bfa`, không phải hợp đồng — sai thì tốn một ca không bắt được đổi EOL của `new` (giữ ghi chú cho TK sau). Sửa `8b155ca`; CI `40506026587` 4/4 xanh. Giao TK2+TK3 (hai commit).

- **2026-10-27 20:05 +07** — TK2, TK3 Đạt. Phán quyết Implementer: test «shim và engine cùng đầu ra» gắn `tương-đương` (không thể đỏ khi hai bản byte-giống), phần «shim thật sự chạy engine» do test khác đỏ ở cha — sai thì tốn một nhãn. Bỏ có chủ ý 2 test của hàm đã gỡ (`test_template_mirror_matches`, `test_mirror_diff_detects_extra_file`). Analyst kiểm: shim, bộ ca OK. Đẩy nhánh, kích CI. Giao TK4a.

- **2026-10-27 20:16 +07** — CI `40509026320` trên `332070d` 4/4 xanh. TK4a Đạt; Analyst xem diff (luật nạp, kiểm danh tính, không re-export). Phán quyết Implementer: thêm câu nêu mô-đun vào `SKILL.md` ngay TK4a thay vì TK4c — để `SC3` không WARN giữa chừng — sai thì tốn một dòng sửa. Giao TK4b (cùng Implementer).

- **2026-10-27 20:22 +07** — CI `40510540431` trên `1c3beb8` xanh. TK4b Đạt; Analyst kiểm 0 `from studio_*`, bộ ca + test mô-đun OK. Phán quyết Implementer: `find_skills`/`cmd_check` ở lại CLI (TK5 thêm `check`) — sai thì tốn một lần dời. Giao TK4c.

- **2026-10-27 20:31 +07** — TK4c Đạt. Phán quyết Implementer: `cmd_evals*` ở lại CLI vì dời vào `studio_evals` tạo vòng với `studio_validate`; 17 `patch.object(studio.os|shutil|tempfile)` đổi sang patch thẳng mô-đun thư viện chuẩn (cùng đối tượng, cùng tác dụng) — sai thì tốn sửa đích patch. Đẩy nhánh, kích CI. Giao TK5+TK6.

- **2026-10-27 21:03 +07** — CI `40512668446` trên `395e621` xanh. TK5, TK6 Đạt. Phán quyết Implementer: cổng duyệt cả `runs/` của skill (mọi sprint, vì `summarize` đọc hết) — link ở sprint cũ cũng chặn (`EV20`) — sai thì tốn một ca chặn thừa; `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` báo loại `rules`; ca hàm/mock TK6 đỏ trên cha bằng `AttributeError` (hàm mới), ca CLI đỏ bằng mã thoát — đủ SC5. Đẩy nhánh, kích CI. Giao TK7→TK9→TK10.

- **2026-10-27 21:47 +07** — CI `40517496766` trên `66a798b` xanh. TK7, TK9, TK10 Đạt. Phán quyết Implementer: `iter_md` báo `link` cho mọi symlink (không stat đích nên không biết đuôi đích); `parse_roots` vẫn nhận gốc `--roots` là link (hành vi cũ có test); cây cũ > 5.000 mục khác ổ bị từ chối `install --force` có lời báo — sai thì tốn một ca từ chối thừa. Đổi có chủ ý 2 test thoát 2 của `new --full --lang vi`. Analyst kiểm `git diff -U0 AGENTS.md` 1 dòng. Đẩy nhánh, CI `40524497312`. Giao TK8.

- **2026-10-27 21:52 +07** — CI `40524497312` trên `913306a` ubuntu đỏ: hồi quy TK7 — `_is_dir_quiet` rồi `parse_roots` gọi `is_link` ngoài `try`, POSIX ENAMETOOLONG crash (1a `RF-T6` đã bắt). Trả TK7 hai vòng: `138cbfa` (`_is_dir_quiet`), `851e2c5` (`is_link` bọc `is_symlink()`+`lstat`, `OSError` → False; `parse_roots` về «root not found»), 5 test `bắt-lỗi` mới. Phán quyết Analyst: `is_link` trả False khi `OSError` đưa vào Trọng tâm review bảo mật (TK13) — sai thì tốn một vòng sửa. Báo TK8 Implementer song song chỉ add file của mình.

- **2026-10-27 22:11 +07** — CI `40525828381` trên `851e2c5` 4/4 xanh. TK8 Đạt (không sửa engine). Ghi chú: ba đột biến nhóm `RQ-009` chết nhờ test TK7; (i) đo theo HEAD `d0792cb` nên gồm cả TK5–TK7, TK9. TK11: `git diff --name-only 1211bfa..HEAD` 0 file ngoài phạm vi Kiến trúc/TK (134 file); đẩy nhánh, kích CI.

- **2026-10-27 22:12 +07** — TK11 Đạt. Giao song song TK12 QA (claude-sonnet, T3) và TK13: Tech Reviewer (claude-opus, T1, agent `code-reviewer`), Security Reviewer (claude-opus, T1, agent `security-reviewer`), Business Reviewer (claude-fable, T1) — subagent mới, ngữ cảnh soạn riêng.

- **2026-10-27 22:30 +07** — Vòng kiểm định 1: Business Đạt có điều kiện (4 Nên sửa; `RF-B1`, `RF-B2` Analyst sửa ngay ở PROGRESS/SPEC mục 7); Tech **Không đạt** — Chặn `RF-T1` (`doctor --roots` gốc cloud thoát 2 «root not found» thay vì `skipped: cloud`, hồi quy TK7); Security **Không đạt** — Chặn `RF-S1` (cổng `EV20` nạp và chạy `evals/tools/activation.py` của repo lạ khi engine được `install` vào đó; PoC chạy được), Phải sửa `RF-S3` (`check <file.md>` đọc file trong vùng `.secret`), Nên sửa `RF-S2` (`sprint`/`evals` từ catalog thoát cây đã duyệt). Phán quyết Analyst: DN8 đổi từ (a) sang (b) — đưa `summarize` vào `studio_evals` (cổng chỉ đọc JSON, không còn `importlib`), `evals/tools/activation.py` gọi ngược engine qua đường cố định theo `__file__` của nó để giữ một nguồn — vì (a) để lại thực thi mã từ cây không tin cậy, không vá được bằng siết `repo_root` — sai thì tốn sửa lại công cụ lô; SPEC FR6.4 sửa chữ theo; Fable xác nhận ở Cổng 2. Chờ QA rồi giao vòng sửa 1.

- **2026-10-27 22:40 +07** — TK12 QA vòng 1 Đạt mọi SC đo được. Lệch QA nêu: `new --output` vẫn ghi `evals/<tên>/` vào repo của cwd (hành vi có từ trước) → đề xuất `CO`. Giao vòng sửa 1 (Implementer T2 claude-sonnet, subagent mới): `RF-S1`, `RF-S2`, `RF-S3`, `RF-T1`, `RF-T2`, `RF-B4`. Để lại → `CO`: `RF-S5`, `RF-S6`, `RF-T3`, `RF-B7`. Analyst sửa SPEC FR6.4, PLAN DN8.

- **2026-10-27 23:02 +07** — Vòng sửa 1 (Implementer T2 claude-sonnet, subagent mới): `241b837` RF-S3, `0d331f5` RF-T1, `009c4f8` RF-S1+RF-S2, `193d485` RF-T2, `5341ba6` RF-B4, `698f552` CHANGELOG, `f1e3f71` `evaluated.date` (Phán quyết Analyst: cùng loại RF-S2, sửa luôn — sai thì tốn một luật chặt thừa). Mỗi mục có test `bắt-lỗi` đỏ trên `df4043b`; pytest 552 passed 7 skipped; 3.12 + 3.9 OK; đột biến 19/19. Đổi có chủ ý 2 test `test_catalog_gate.py` (thiếu `activation.py` không còn `EV20`). CI `40538897327` 4/4 xanh. Gọi Tech, Security vòng 2 (cùng reviewer).

- **2026-10-27 23:10 +07** — Vòng 2: Tech Đạt (`RF-T4` PLAN tả cổng cũ — Analyst sửa PLAN), Security Đạt có điều kiện (`RF-S1`, `RF-S2`, `RF-S3` đóng; mới `RF-S7` Nên sửa: `check <thư mục>` đọc `SKILL.md` trong vùng cloud/secret và in `name` — có từ 1a ở `validate`, không hồi quy → `CO`). `SHA lô` = `f1e3f71`. Giao TK14 (QA T3 claude-sonnet).

- **2026-10-27 23:32 +07** — TK14 lô 16 lượt trên `f1e3f71` (QA T3 claude-sonnet, commit Studio `e59ef52`, 4,87 USD): 16/16 `ran`; `skill-creator-studio` 2/5 · 0/3 (đạt); `data-quality-audit` positive **2/5** (ngưỡng 4/5) · 0/3 — SC4 lệch. Cây `data-quality-audit` không đổi băm so SPR-33; Claude Code 2.1.308 → 2.1.310. Phán quyết Analyst: chạy đối chứng 5 ca positive `data-quality-audit` trên archive `1211bfa` và lặp lại trên `f1e3f71` (cùng phiên bản) trước khi kết luận — vì RUNBOOK đã ghi thước dao động giữa lô và skill không đổi — sai thì tốn ~1,5 USD.

- **2026-10-28 00:35 +07** — Đối chứng xong 23:38 (agent chưa báo; Analyst đọc `control-TK14/results.json`): `data-quality-audit` positive `1211bfa` 4/5, `f1e3f71` 4/5 → lô chính 2/5 là dao động thước. Phán quyết Analyst: VR4 «Đạt có điều kiện», trình Fable ở Cổng 2 — sai thì tốn một lô đo lại ở chặng 4. Điều phối hỏi tình trạng, đã trả lời. REPORT viết; `RQ-021`…`RQ-024` ghi REQUESTS; ĐK1 vào `RQ-004`. CI `40551125882` trên `e59ef52`.

- **2026-10-28 00:35 +07** — Cổng 2: người duyệt hộ T1 `claude-fable-5-1` (subagent mới) — Đạt có điều kiện; xác nhận DN8 (a) → (b);
  VR4 lệch có duyệt; ĐK-A…ĐK-C. Phán quyết Analyst: dòng CHANGELOG của ĐK-C commit trên nhánh trước khi gộp (`76510a4`, chỉ
  `CHANGELOG.md`, CI `40552419420` xanh) thay vì sửa trong commit gộp — sai thì tốn một commit. Gộp `--no-ff` → `main` `3cc1bd3`, push;
  CI `40552921951` 4/4. SC2 ở `3cc1bd3` = 0. Xoá nhánh bị harness chặn (để lại). Ghi chú: giờ nhật ký từ 19:10 đã chỉnh theo giờ commit thật
  (bản trước ghi giờ ước, lệch tới 4 giờ — Fable ĐK-A).

## 3. Vướng mắc

Không có.

## 4. Vòng kiểm định hiện tại

Vòng 2 — Tech Reviewer (claude-opus-5-5) Đạt; Security Reviewer (claude-opus-5-5) Đạt có điều kiện; Business Reviewer (claude-fable-5-1) Đạt có điều kiện. 0 Chặn, 0 Phải sửa mở; chi tiết RF ở REPORT mục 2.
