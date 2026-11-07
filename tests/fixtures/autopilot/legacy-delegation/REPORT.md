---
id: SPR-02-report
doc: report
title: "Chặng 1b: một nguồn cho agent-skill-studio"
sprint: SPR-02
request: RQ-003
feature: null
status: accepted
size: large
risk: high
risk_tags: [public_api, infra]
review_round: 2
verdict: conditional_pass
gate_2: conditional_pass
gate_2_at: 2026-10-28 00:35 +07
gate_2_quote: "duyệt thay: Đạt có điều kiện SPR-02 chặng 1b — VR1–VR11 Đạt, VR4 Đạt có điều kiện theo đối chứng cặp `1211bfa` 4/5 = `f1e3f71` 4/5 (SC4 lệch có duyệt, ghi `RQ-007`); xác nhận DN8 (a) → (b); 4 CO = `RQ-021`…`RQ-024`, ĐK1–ĐK3 Cổng 1 thoả; duyệt gộp `--no-ff` `sprint/spr-02-one-source-1b` vào `main` tại `e59ef52` (CI `40551125882` xanh) + push, CI commit gộp phải 4/4; điều kiện ĐK-A…ĐK-C ở `evidence/gate2-fable.md` — Fable duyệt hộ theo uỷ quyền Đức 27/10"
gate_2_mode: delegated
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
  implementer: [T2, claude-sonnet-5-5, "Sonnet High, subagent mới mỗi cụm TK; vòng sửa 1 subagent riêng"]
  qa: [T3, sonnet-qa-subagent, "claude-sonnet-5-5, subagent riêng, không viết mã sprint"]
  business-reviewer: [T1, claude-fable-5-1]
  tech-reviewer: [T1, claude-opus-5-5, "hai subagent riêng: code-reviewer (Tech) và security-reviewer (Security)"]
created: 2026-10-27
updated: 2026-10-28
links:
  spec: SPEC.md
  plan: PLAN.md
  progress: PROGRESS.md
---

# Chặng 1b: một nguồn cho agent-skill-studio — Báo cáo (REPORT)

> **Kết luận:** **Đạt có điều kiện** ở Cổng 2 (Fable duyệt hộ; VR4 dựa trên lô đối chứng) — Studio `main` = `3cc1bd3`, CI `40552921951` 4/4 — mã và khuôn của Studio mỗi thứ còn một bản (gốc là shim 14 dòng, engine trong skill tách 9 mô-đun
> phẳng), lời gọi cũ giữ nguyên trên 96 ca hợp đồng đóng băng từ `1211bfa`, ba nợ 1a (`RQ-009`, `RQ-011`, `RQ-018`) đóng có test
> đỏ→xanh, hai vòng kiểm định độc lập tìm và đóng 2 Chặn (`RF-S1` thực thi mã từ cây lạ, `RF-T1` hồi quy `doctor` gốc cloud);
> CI 4/4 xanh; lô 16 lượt xem VR4. Còn 4 `CO` (→ `RQ-021`…`RQ-024`).

## Tóm tắt cho người không chuyên

Trước sprint, bộ công cụ kiểm skill có hai bản mã giống hệt nhau và hai bản khuôn skill, phải chép qua lại bằng tay; nay chỉ còn
một bản, nên sửa một chỗ là xong. Mọi cách gọi cũ vẫn cho đúng kết quả cũ (đã khoá bằng 96 ca kiểm tự động trước khi sửa). Có thêm
lệnh `check`, khuôn skill đầy đủ bằng tiếng Việt, và ba chỗ còn đọc xuyên đường tắt (link) đã được bịt. Trong lúc kiểm, reviewer
bảo mật tìm ra một lỗ mới do chính sprint tạo (chạy được mã của thư mục lạ) — đã sửa và kiểm lại. Không cần quyết gì thêm ngoài
Cổng 2.

## 1. Kết quả kiểm định

REPORT có 11 **verification result** (VR):

| Mã | Tiêu chí | Lệnh / cách đo | Kết quả | Ai đo | Bằng chứng |
|---|---|---|---|---|---|
| VR1 (hợp đồng giữ) | SC1 · FR1, FR4, FR5.1, FR11 | `unittest tests.test_contract_regression` | Đạt — 96 ca (R 22 · C 22 · E 23 · S 13 · Z 13 · sống 3), 6 ca `changed_by` (FR3 ×3, FR10 ×3) có `after`; khớp ở `df4043b` và `f1e3f71` (CI); chạy trên archive `1211bfa` 96/96 khớp | QA · claude-sonnet-5-5; Tech · claude-opus-5-5 | `evidence/qa.md`, `review-tech.md` |
| VR2 (một nguồn) | SC2 · FR1, FR2 | `git ls-files -s` blob trùng ngoài `evals/*/runs/`, `tests/fixtures/` | Đạt (lệch có duyệt DN9) — 0 ở `df4043b` và ở commit gộp `3cc1bd3` (ĐK-C; trước sprint 9); còn lại trong vùng loại trừ: 11 `runs/SPR-18` (`blind` ↔ `out`), 5 fixture, 80 cặp tệp ↔ ảnh đóng băng hợp đồng | QA | `evidence/qa-sc2.txt` |
| VR3 (CI) | SC3 · FR11.4 | `gh run view` | Đạt — nhánh: `40528630643` (`df4043b`), `40538897327` (`f1e3f71`), `40551125882` (`e59ef52`), `40552419420` (`76510a4`) 4/4; commit gộp `3cc1bd3`: `40552921951` 4/4 | Analyst | — |
| VR4 (lô không hồi quy) | SC4 · FR13 | 16 lượt `claude -p … --plugin-dir <archive f1e3f71>` (Claude Code 2.1.310); `activation.py summarize`; đối chứng 5 ca positive `data-quality-audit` trên archive `1211bfa` và `f1e3f71` | Đạt có điều kiện — **SC4 nguyên văn không đạt về số** (lệch có duyệt Cổng 2): 16/16 `ran`; `skill-creator-studio` 2/5 · 0/3 (đạt); `data-quality-audit` 2/5 · 0/3 ở lô chính (dưới ngưỡng 4/5) nhưng cây skill **không đổi băm** so SPR-33 và đối chứng cùng phiên bản cho `1211bfa` 4/5 = `f1e3f71` 4/5 → dao động thước, không hồi quy (RUNBOOK «Dao động giữa lô»); chi phí 4,87 + 1,66 USD | QA · claude-sonnet-5-5 | `evidence/batch.md`, `evidence/control-TK14/`; Studio `e59ef52` |
| VR5 (đỏ trước xanh sau) | SC5 · FR5, FR6, FR7, FR10 | test `bắt-lỗi` trên commit cha của commit sửa và HEAD; đột biến | Đạt — TK2, TK3, TK5, TK6, TK7 (+2 vòng CI), TK9 đỏ bằng assertion/mã thoát → xanh; vòng sửa 1: mỗi RF có test đỏ trên `df4043b` | QA; Implementer (vòng sửa, Tech/Security xác nhận) | `evidence/qa-sc5.txt`, `fix-round1.txt` |
| VR6 (đột biến, coverage) | SC6 · FR8 | `evidence/run_mutants.py`; `coverage --branch` | Đạt — 19/19 chết (trước TK8: 10/19), giữ 19/19 sau vòng sửa; (i) 88,0 % · (ii) 90,7 % · (iii) 91,4 % | QA | `evidence/qa.md`, `tk8.txt` |
| VR7 (ký bảo mật) | SC7 · FR1, FR4.5, FR6.4, FR7 | Security Reviewer T1 hai vòng | Đạt có điều kiện — vòng 1 Không đạt (`RF-S1` Chặn, `RF-S3` Phải sửa), vòng 2 0 Chặn/Phải sửa; `RF-S7` → `CO1` | Security · claude-opus-5-5 | `evidence/review-security.md` |
| VR8 (`check`, `new vi`, `PR1`) | SC8 · FR5, FR9, FR10 | `fmt --check`, `new --full --lang vi`, `check` | Đạt — 0 `PR1` (trước 12); `new --full --lang vi` thoát 0, 0 ERROR; `check` skill/`AGENTS.md`/`.md` lạ đúng FR5 | QA; Business | `evidence/qa-sc8-10.txt` |
| VR9 (người gọi đối tác) | SC9 · FR1, FR3 | `system/evals/run.ps1 -Tier fast` | Đạt — «EVAL ĐẠT — tier fast», exit 0, 1.078 s (trên `df4043b`; vòng sửa chỉ chạm cổng `evals` + `check` + `doctor` cloud, không đổi bề mặt đối tác gọi) | QA | `evidence/qa-sc9-*.txt` |
| VR10 (cổng trong engine) | SC10 · FR6 | `evals --all`; `grep AB_THRESHOLDS *= tests/` | Đạt — exit 0; 0 định nghĩa trong `tests/`; catalog hỏng → `EV20` thoát 1 (test) | QA | `evidence/qa-sc8-10.txt` |
| VR11 (bộ test, Python 3.9) | Ràng buộc chung · FR4.2, FR12 | pytest; `unittest discover` 3.12 + 3.9.25 | Đạt — `f1e3f71`: pytest 552 passed 7 skipped; unittest 3.12 + 3.9 OK | Implementer; Security (559 ca) | `evidence/fix-round1.txt` |

## 2. Phát hiện của reviewer

### Review PLAN trước Cổng 1

Tech Reviewer T1 `claude-opus` hai vòng: vòng 1 Không đạt — 1 Chặn (`RF1` nguồn `activation`), 9 Phải sửa, 7 Nên sửa, 5 Ghi chú;
vòng 2 Đạt có điều kiện — 22/22 đóng, mới `RF23`–`RF28` (2 Phải sửa) nạp trước Cổng 1. Chi tiết `evidence/plan-review-opus.md`.

### Business Reviewer

`claude-fable-5-1`: Đạt có điều kiện — 0 Chặn · 0 Phải sửa · 4 Nên sửa · 3 Ghi chú (`evidence/review-business.md`).

| Mã | Phát hiện | Mức | Xử lý |
|---|---|---|---|
| RF-B1 (PROGRESS cũ) | kết luận/TK11 chưa cập nhật | Nên sửa | đã sửa |
| RF-B2 (SPEC mục 7 thiếu dòng) | đổi hợp đồng `fmt`/`validate --all` với symlink | Nên sửa | đã thêm dòng SPEC mục 7 |
| RF-B3 (REQUESTS) | `RQ-003/009/011/018` chưa đóng; ĐK1 `RQ-004` | Nên sửa | làm khi đóng sprint (mục 6) |
| RF-B4 (câu mơ hồ `SKILL.vi.md:45`) | «Nhiệm vụ không đạt chỉ vì…» | Nên sửa | `5341ba6` |
| RF-B5…RF-B7 | Ghi chú (gốc `--roots` là link, ĐK2, EOL `new`) | Ghi chú | RF-B5 Security xác nhận; RF-B6 xem VR9/ĐK2; RF-B7 → `CO4` |

### Tech Reviewer

`claude-opus`, hai vòng: vòng 1 Không đạt, vòng 2 Đạt (`evidence/review-tech.md`). Bỏ `patch.object` thử ở 9 chỗ → cả 9 đỏ; so AST
từng hàm với `1211bfa`: chỉ hàm thuộc TK3, TK5–TK7, TK9 đổi.

| Mã | Phát hiện | Mức | Xử lý |
|---|---|---|---|
| RF-T1 (`doctor --roots` gốc cloud) | thoát 2 «root not found» thay vì `skipped: cloud` (hồi quy TK7) | Chặn | `0d331f5`, test đỏ trên `df4043b` |
| RF-T2 (lệnh mẫu thiếu `--eval-root`) | Step 7/Step 5 hai workflow | Nên sửa | `193d485` |
| RF-T3 (stderr chỉ so tiền tố) | đổi lời báo giữ mã thoát lọt | Ghi chú | đúng FR11.1 → `CO4` |
| RF-T4 (PLAN tả cổng cũ) | sau DN8 (b) | Ghi chú | Analyst sửa PLAN |

### Security Reviewer

`claude-opus` (agent `security-reviewer`), hai vòng (`evidence/review-security.md`).

| Mã | Phát hiện | Mức | Xử lý |
|---|---|---|---|
| RF-S1 (cổng `EV20` thực thi `activation.py` của cây lạ) | engine cài vào repo X chạy mã X (PoC in dòng) | Chặn | `009c4f8`: bỏ `importlib`, `summarize` vào engine, `activation.py` gọi ngược; DN8 → (b); PoC vòng 2 không chạy |
| RF-S2 (`sprint`/`evals` thoát cây) | đọc log ngoài cây đã duyệt | Nên sửa | `009c4f8` + `f1e3f71` (`date`) |
| RF-S3 (`check` đọc vùng secret) | thiếu `input_file_problem` | Phải sửa | `241b837` |
| RF-S4 (`is_link` False khi `OSError`) | soát 23 nơi gọi, không đường xuyên | Ghi chú | giữ |
| RF-S5 (`skill_dirs` stat xuyên `SKILL.md` symlink) | chưa xác minh (máy không tạo symlink) | Ghi chú | `CO2` |
| RF-S6 (`new` ghi đè `cases.json`) | có từ 1a | Ghi chú | `CO3` |
| RF-S7 (`check`/`validate <thư mục>` đọc `SKILL.md` vùng cloud/secret, in `name`) | có từ 1a, không hồi quy | Nên sửa | `CO1` |
| RF-S8, RF-S9 | `activation.py` tìm engine theo `__file__`; bản cài chạy cổng trên repo giả chỉ đọc dữ liệu | Ghi chú | giữ |

## 3. Rủi ro còn lại

- `RF-S7` (`CO1`): `validate`/`check` trên thư mục skill nằm trong vùng cloud/secret vẫn đọc `SKILL.md` và in `name` — có từ 1a.
- Junction/symlink thật chỉ chạy ở CI Windows/Ubuntu; placeholder OneDrive thật chưa thử (mock).
- Cache plugin Claude `0.1.0` trên máy là bản cũ (trước 1a); cài lại thuộc chặng 2 (`RQ-004`).
- Thước kích hoạt dao động mạnh (cùng cây skill: 2/5 rồi 4/5 cách nhau 2 giờ) — «không hồi quy» chỉ khẳng định ở mức ngưỡng sau đối chứng; đo thật ở chặng 4 (`RQ-007`).

## 4. Cách dùng, đã đổi gì, cách hoàn tác

- **Dùng:** như cũ (`python studio.py validate|audit|evals|doctor|fmt|new|package|install …`); mới `python studio.py check <skill|SKILL.md>`;
  `new <tên> --description … --full --lang vi`. Engine: `skills/skill-creator-studio/scripts/studio.py` (gọi trực tiếp được).
- **Đã đổi:** CHANGELOG `Unreleased` + SPEC mục 7 (bỏ `sync-template`, `templates/skill-template*`; thêm `check`, cổng `EV20` trong
  `evals --all`; `new --full --lang vi`; nhận diện gốc repo; `package`/`install` chặn `PACK` trước khi đọc; `install --force` khác ổ
  gặp link thoát 1; `fmt`/`validate --all` không đi theo symlink; kiểm danh tính mô-đun). `AGENTS.md:36` đổi một dòng (Fable duyệt hộ).
- **Hoàn tác:** `git revert -m 1 <commit gộp>` trên `main` Studio; không có dữ liệu/trạng thái ngoài repo bị đổi.

## 5. Bài học

REPORT có 4 **lesson** (LN):

| Mã | Bài học | Tái dùng | Đề xuất nâng thành | Nơi |
|---|---|---|---|---|
| LN1 (khoá hợp đồng trước khi tách) | Bộ ca đóng băng sinh từ archive mốc + CI 4 ô ngay sau đó bắt được lệch môi trường (EOL `new`, thứ tự `fmt`) trước mọi sửa, nên mọi đỏ sau là hồi quy thật | Có | bước quy trình | `agent-agile-team` skill `writing-plan` (việc tái cấu trúc) |
| LN2 (CI POSIX bắt hồi quy Windows không thấy) | Thêm `is_link` lên trước phép bắt `OSError` crash ENAMETOOLONG trên Linux; máy Windows xanh. Đẩy nhánh + CI mỗi TK, không chỉ trước review | Có | bước quy trình | memory feedback (gộp với bài học CI symlink 1a) |
| LN3 (cơ chế nạp «chỉ từ repo của chính engine» không an toàn khi engine được cài vào cây lạ) | Engine chép rời không biết repo nào là «của nó»; mọi cổng phải chỉ đọc dữ liệu, không nạp mã theo vị trí | Có | luật thiết kế | `SECURITY_AND_PERMISSIONS.md` chặng 2 |
| LN4 (hai Implementer song song trên một cây) | Được nếu mỗi bên chỉ `git add` đúng file của mình; báo trước cho bên kia | Có | không | — |

## 6. Việc để lại

REPORT có 4 **carry-over** (CO); mỗi CO một `RQ-` trạng thái `mới` ở REQUESTS:

| Mã | Việc | Lý do để lại | Xử lý |
|---|---|---|---|
| CO1 (`RF-S7` đọc vùng cloud/secret khi đầu vào là thư mục) | `validate`/`check <thư mục>` kiểm `input_file_problem` cho `SKILL.md` trước khi đọc | có từ 1a, không hồi quy | `RQ-021` — chặng 2 |
| CO2 (`RF-S5`) | `skill_dirs` không stat xuyên `SKILL.md` là symlink | chưa xác minh (máy không tạo symlink) | `RQ-022` — chặng 2 |
| CO3 (`new` và evals) | `new` ghi đè `cases.json` có sẵn (`RF-S6`); `new --output` vẫn ghi `evals/<tên>/` vào repo của cwd (QA) | có từ trước | `RQ-023` — chặng 2 |
| CO4 (độ nhạy bộ ca hợp đồng) | stderr chỉ so tiền tố (`RF-T3`); băm `new` sau CRLF→LF không bắt đổi EOL (`RF-B7`) | đúng thiết kế FR11.1 | `RQ-024` — Có thì tốt |

ĐK1 Cổng 1: `RQ-004` (chặng 2) nhận dòng đích danh 11 blob `evals/data-quality-audit/runs/SPR-18/{blind,out}/` (VR2).

## 7. Review & Retro

- **Review:** 8/8 việc ROADMAP 1b xong; «Xong khi»: blob trùng 0 ngoài vùng loại trừ đã duyệt (DN9), lời gọi cũ 96/96 ca, lô 16 lượt
  (VR4).
- **Retro:** làm tốt — khoá hợp đồng + CI trước khi tách; tách ba lát; đột biến chốt trước và lưu chạy lại được. Chưa tốt — TK7 hai
  lần đỏ CI Ubuntu vì thiếu bắt `OSError`; thiết kế DN8 (a) được duyệt ở Cổng 1 nhưng có lỗ bảo mật mà plan-review chỉ chạm một phần
  (`RF23`) — review bảo mật nên đọc PLAN khi có nạp mã động.
- Số vòng kiểm định: 2 (sửa 1 vòng + vá `date`). Plan-review 2 vòng.

## 8. Cổng 2 — nghiệm thu

- **Kết luận:** Đạt có điều kiện — người duyệt hộ T1 `claude-fable-5-1` (subagent riêng), 2026-10-28 00:35 +07, theo `delegation.grant`;
  hồ sơ `evidence/gate2-fable.md`. Câu duyệt nguyên văn ở frontmatter `gate_2_quote`.
- **Điều kiện:** ĐK-A sổ khớp hiện trạng (REQUESTS, PROGRESS, ghi chú `RF-S4/S8/S9` → `RQ-025`) — đã làm; ĐK-B VR4 ghi «lệch có duyệt»
  + `RQ-007` thêm luật đo theo cặp — đã làm; ĐK-C đếm SC2 ở commit gộp (0) + dòng CHANGELOG `doctor --roots` gốc placeholder cloud
  (`76510a4`) — đã làm.
- **Gộp:** `git merge --no-ff sprint/spr-02-one-source-1b` → Studio `main` `3cc1bd3` (cha `1211bfa` + `76510a4`; `76510a4` = `e59ef52`
  + một dòng CHANGELOG theo ĐK-C, CI `40552419420` xanh), push; CI commit gộp `40552921951` 4/4 xanh.
- Nhánh `sprint/spr-02-one-source-1b`: lần đầu lệnh xoá bị bộ phân loại quyền của harness chặn; 28/10 Đức xác nhận «xác nhận cho
  xóa» → đã kiểm `76510a4` là tổ tiên của `main` và `origin/main`, rồi `git branch -d` + `git push origin --delete` — chỉ còn `main`.

## Bản ghi duyệt thay

Cổng 2 do người duyệt hộ T1 `claude-fable-5-1` (subagent riêng, không làm, không viết REPORT) theo `delegation.grant`; kết luận
**Đạt có điều kiện**; hồ sơ `evidence/gate2-fable.md`.

- **Phương án chọn:** Đạt có điều kiện; VR4 chấp nhận theo đối chứng cặp, không đo lại; xác nhận DN8 (a) → (b); duyệt gộp `--no-ff` + push.
- **Phương án bị loại:** Không đạt / đo lại lô — đối chứng cùng phiên bản đã cho `1211bfa` 4/5 = `f1e3f71` 4/5, cây skill không đổi băm;
  giữ DN8 (a) — để lại thực thi mã từ cây lạ (`RF-S1`).
- **Nếu sai thì tốn gì:** nếu kích hoạt `data-quality-audit` thật sự kém đi, chặng 4 (`RQ-007`) đo theo cặp sẽ thấy — tốn một lô ~5 USD và
  một sprint sửa mô tả; DN8 (b) sai thì tốn sửa lại đường gọi ngược của `activation.py`.
- **Điều kiện:** ĐK-A…ĐK-C — đã làm (mục 8).
