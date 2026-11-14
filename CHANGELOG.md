# Changelog

Mục mới nhất đứng đầu. Tiêu đề mỗi mục là đúng chuỗi version trong các manifest (test đồng bộ
version kiểm điều này).

## 0.11.0 (2026-11-14)

- **Sửa — `shaping-spec` ô `SC` và `running-sprint/references/brief.md` (hai thẻ learn-skills; chưa phát hành, chưa tăng version):** ô `SC` đòi số đếm lấy từ máy ghi đo ở đâu (checkout hay worktree), lệnh, mốc commit và điều kiện làm lệch (EOL, cache), ưu tiên quan hệ bất biến hơn hằng số (thẻ `2026-11-09-shaping-spec-sc-environment`, SPR-64); báo cáo, ảnh, log của `TK` ghi vào thư mục hồ sơ sprint (`paths.sprint_dir`), không vào `.tmp/`, rà secret trước khi ghi (thẻ `2026-11-09-brief-report-in-sprint-dir`). Thử áp lực n = 1, ca cũ chưa chạy lại. Đề xuất tăng PATCH (sửa lời hai skill); số do người dùng quyết.
- **Thêm — lệnh `/agent-agile-team:stop-autopilot` và khuôn tin autopilot theo `method/communication.md` (SPR-24):** `commands/stop-autopilot.md` chỉ in câu chuẩn `Dừng autopilot.` hoặc `Thu hồi duyệt thay SPR-NN.` (không ghi hồ sơ, không chạm file dấu, không `--clear`, đối số coi là dữ liệu); `tests/test_commands.py`. `method/autopilot.md` mục 2, 7, 8: tin mở thêm dòng `Chi tiết:` (link), tin dừng và báo cuối mở bằng kết luận, câu hỏi theo bốn phần; dòng "chưa có `commands/`" đổi theo lệnh mới; không đổi nghĩa luật. `skills/intake/references/autopilot.md` điều 6 và `hosts/claude/README.md` đồng bộ; kịch bản áp lực `in-26`/`in-27`. Đóng RQ-106, RQ-122.
- **Đổi — lời dặn cuối của lệnh `/agent-agile-team:autopilot-goal`:** câu "Gửi nguyên khối trên trong chat mới là đặt goal" dễ đọc nhầm là lệnh đã đặt goal; viết lại thành "Dán khối trên vào chat và gửi đi thì mới đặt được goal. Chưa gửi thì chưa có goal nào". Sửa thêm `method/communication.md`: con trỏ tới khuôn tin của `method/autopilot.md` ghi "mục 2, 7 và 8" (tin mở, dừng, báo cuối) thay cho "mục 6 và 7" sai. Không đổi khối `/goal` hay luật.
- **Thêm — lệnh `/agent-agile-team:autopilot-goal` (SPR-27, RQ-131):** `commands/autopilot-goal.md` đọc sprint đang mở rồi **chỉ in** một khối `/goal` (hai điều kiện xong, bốn điều kiện dừng, dòng "Phán quyết", câu cấm push/gộp/tag/sửa file luật trừ khi PLAN có lời cấp, trần lượt từ `Trần phiên:` hoặc bảng `method/autopilot.md` mục 2.1, mặc định 30) để người dùng tự gửi; lệnh không chạy `/goal`, chỉ có công cụ đọc, đối số là dữ liệu. Test mới `tests/test_autopilot_goal_command.py`. Có thể xung đột khi gộp với PR #13 (SPR-24) vì cùng thêm mục ở đầu mục 0.10.0 và cùng tạo `commands/`.

- **Đổi — nợ SPR-21 và SPR-20 (SPR-25):** mẫu `templates/sprint/SPRINT-tiny.md` có mục `Nhật ký quyết định` như mẫu cỡ nhỏ (RQ-109; `check` đã kiểm mục này cho mọi cỡ `SPRINT.md`, test mới `test_tiny_scaffold_has_decision_log_bullet_in_result_part`); `skills/explain/tests/scenarios.txt`: thêm CM-7 (gom nhiều câu hỏi) và CM-8 (việc khó hoàn tác cần diễn giải), bảng chấm CM-1b đòi "đủ hai vế" thay "một câu" (RQ-124, RQ-125); `skills/response-style/tests/scenarios.txt`: bảng chấm bốn ô v1, v2 cho RS-1…RS-3 (phục vụ RQ-121, chưa đổi `SKILL.md`: RQ-121 tách sang sprint riêng, bản ghi vòng thử ở hồ sơ SPR-25). Không đổi mã `check`.
- **Thêm — skill `explain`, mục Tóm tắt cho người không chuyên và luật `plain-summary` (SPR-21).** Luật `plain-summary` (mức Nên sửa) báo SPEC/PLAN tạo từ ngày hiệu lực mà thiếu mục tóm tắt hoặc để rỗng; ngày hiệu lực chốt khi gộp. File chạm chính: `method/communication.md`, `skills/explain/`, `scripts/check.py`, `AGENTS.md` (một dòng trỏ).
- **Thêm — ước lượng tự đưa trong skill `response-style` phải có nhãn (SPR-28, RQ-121):** ước lượng do agent tự đưa (thời gian, chi phí, số lượng) ghi nhãn theo phạm vi; chưa đo thì viết "chưa đo" kèm cách đo, không dùng số suy ra. Có bảng chấm hợp nhất và 4 đề UAT trong `skills/response-style/tests/pressure.md`.
- **Đổi — `intake` và `sizing` (SPR-23, RQ-107, RQ-108):** `intake` bắt trường hợp `.tmp/` chưa nằm trong `.gitignore` trước khi ghi file dấu; ngưỡng nhỏ/vừa dời về `method/sizing.md` mục 3.1, chữ quanh mốc sàn cứng giữ nguyên.
- **Thêm — `check` kiểm model nhật ký quyết định theo bảng tier và cờ `--by-dir` (SPR-22, RQ-111, RQ-115):** `decision-log-missing` kiểm model ghi trong nhật ký quyết định khớp bảng tier; `check --by-dir` tách nguồn phát hiện theo thư mục.

## 0.10.0 (2026-11-13)

- **Sửa — chữ luật quét secret theo quyết định của Đức 13/11 (SPR-20 TK28b):** trước khi đẩy, agent quét secret toàn bộ diff đẩy bằng công cụ sẵn có hoặc tự quét bằng `security-review`/`security-reviewer` kèm dò mẫu khoá và tên file nhạy cảm, ghi kết quả vào báo cáo cuối; nghi ngờ hoặc không quét được thì không đẩy. Không còn đòi công cụ chuyên dụng cài ngoài. `method/autopilot.md` (vùng sàn, ghim băm đổi), `method/conventions.md`.
- **Gỡ, phá tương thích — rào git thường trực và shim (SPR-20 TK21, chưa phát hành; chưa tăng version):** xoá `scripts/git_fence.py`, `scripts/git_shim.py`, `shims/`, `scripts/session-env.sh`, `templates/git-hooks/pre-push`, `templates/protected-repos.example.json`, `method/git-permissions.md` và các test của chúng; `hooks/hooks.json` bỏ khối `SessionStart`; `scripts/autopilot_guard.py` không còn mẫu lệnh git (`push`, `tag`, gộp, `reset --hard`, `branch -D`, `clean -f`, `gh`), không còn lệnh viết lại và quyết định `ask`, chỉ giữ xoá đệ quy ngoài `.tmp/`, `git worktree remove --force`, `git stash -u` và bảo vệ file dấu; `FENCE_FILES` bớt hai file; test đột biến còn tám; ADR 0001 chuyển `superseded`. Vùng sàn (`FLOOR_FILES`, băm vùng), `check.py` và chữ luật dời TK22/TK23.
  - TK21b: mẫu bảo vệ file dấu thu hẹp: `git stash` chỉ bị chặn khi có `-a`/`--all` (`-u` qua); thêm `git clean` có `-f` kèm `-x`/`-X`; xoá `tests/oracle_harness.py` (bộ đối chiếu của rào đã gỡ, không còn ai dùng).
- **Đổi — chữ luật một chế độ autopilot (SPR-20 TK23, chưa phát hành; chưa tăng version):** `method/autopilot.md` viết lại cho một chế độ mặc định bật (tin mở autopilot bắt buộc đầu mỗi sprint và phiên tiếp tục, trần phiên theo công thức cỡ × rủi ro, Gate Delegate ký Cổng 1 và 2, bảy việc luôn chặn, mục "Nhật ký quyết định", `Dừng autopilot.` là lệnh duy nhất); thêm `method/git-conventions.md` (nhánh sprint, tag và commit sao lưu, ba lệnh cấm dạng chữ, bảng hoàn tác 5 ca); `AGENTS.md` và `method/process.md` đổi "cổng của người" thành Gate Delegate (Đạt có điều kiện không mở gộp `main`); skill `intake`, `running-sprint`, `closing-sprint` (và `references/autopilot.md`), `roles/verifier/gate-delegate.md`, mẫu REPORT/SPRINT (mục "Nhật ký quyết định"), `templates/README.md`, `scripts/README.md` đồng bộ chữ; gỡ `AGENT_AGILE_PROTECTED_REPOS` khỏi tài liệu. Vùng sàn đổi chữ: ghim băm và `FLOOR_FILES` đổi ở commit sau của TK23.
- **Đổi — skill `intake`, `running-sprint`, `closing-sprint` theo một chế độ autopilot (SPR-20 TK24, chưa phát hành; chưa tăng version):** `intake/SKILL.md` viết lại phần còn sót của luật cũ (tin gom không chờ trả lời, không hỏi "bật autopilot không", làm thẳng không tin mở, `CQ` do Gate Delegate quyết, phần cần người dồn vào báo cuối); `tests/scenarios.txt` của ba skill thay ca cờ/chế độ/`exclusions`/ruleset/`+nhánh`/`+đẩy-nhánh`/lối tắt (đã bỏ vì hành vi đã bỏ) bằng ca cho luật mới; thử áp lực chạy lại RED (cây `553c1aa`) và GREEN, mỗi ca một chủ thể mới (`claude-sonnet-5-5`): GREEN intake 9/9, running-sprint 4/4, closing-sprint 5/5; `skill_sha` của ba `pressure.md` và bảng `skills/README.md` cập nhật. `n = 1` mỗi ca, cùng họ model.
- **Thêm — luật `check` cho nhật ký quyết định và trần phiên (SPR-20 TK25, chưa phát hành; chưa tăng version):** `decision-log-missing` (REPORT có Cổng 2 duyệt thay mới mà thiếu mục `## Nhật ký quyết định` có dòng đủ ai ký · model · bằng chứng · lệnh hoàn tác) và `session-cap-missing` (PLAN có Cổng 1 duyệt thay mới mà mục `## Ước lượng` thiếu dòng `Trần phiên: <số>`), cả hai Phải sửa, chỉ áp khi `delegation.grant_at` từ 2026-11-13 nên hồ sơ cũ không sinh phát hiện mới.
- **Sửa — vòng sửa gộp sau soát Tech + Security (SPR-20 TK27b, chưa phát hành; chưa tăng version):** `scripts/autopilot_guard.py` chặn thêm `mv`/`robocopy`/`cp -r` vào `.tmp/` rồi xoá, mọi lệnh xoá có đích thuộc `.git`, `Get-ChildItem -Recurse | Remove-Item`, `find -exec rm`, `[IO.Directory]::Delete(…,$true)`, `robocopy /MIR`, `busybox rm` và các lệnh git phá hoàn tác (`reflog expire`, `gc --prune=now`, `update-ref -d`, `push` xoá/ép, `branch -D`); `git stash -u`/`git clean -f` chỉ chặn khi file dấu không bị gitignore (`git check-ignore -q`). `check`: `session-cap-missing` đối chiếu `Trần phiên` với `sessions_cap` và công thức cỡ × rủi ro (`_autopilot_rules.session_cap_formula`; `null` không hợp lệ ở hồ sơ mới), `gate-signer-independence` kiểm `evidence/gate-<N>-verdict.md`, hai luật nhật ký/trần áp cả `SPRINT.md`, khử trùng phát hiện. Chữ luật: Gate Delegate không quyết thay ở (a), (b), bảy mục luôn chặn; đẩy/gộp `main`/tag/phát hành chỉ khi PLAN có lời cấp + Cổng 2 Đạt, kèm kiểm ruleset và quét secret; lời cấp mẫu chỉ là ví dụ. Vùng sàn đổi: `AGENTS.md`, `method/process.md`, `method/autopilot.md`, `tests/test_fence_wiring.py` (băm), `tests/test_mutation_floor.py` (mười đột biến mới) — cần Đức gật 5 ý và nhãn `floor-approved`. Nợ ghi nhận: `core.md` và `~/.claude/CLAUDE.md` còn ghi hai cổng người / push chỉ khi giao rõ — xin 5 ý riêng sau, không sửa trong sprint này.
- **Sửa — vòng sửa sau Cổng 2 Đạt có điều kiện (SPR-20 TK27c, chưa phát hành):** `scripts/autopilot_guard.py` chặn `mv`/`move`/`Move-Item`/`ren`/`Rename-Item`/`robocopy`/`cp -r` có nguồn thuộc `.git` (lỗ hai bước `mv .git .tmp/x/g` rồi `rm -rf .tmp/x` ở lệnh riêng), thêm test ở `tests/test_autopilot_guard_undo.py`; `method/conventions.md` mục 4 thống nhất với luật mới (version do Gate Delegate quyết theo bảng, hiệu lực khi Cổng 2 Đạt; đẩy/PR/gộp chỉ sau Cổng 2 Đạt khi PLAN có lời cấp; `reset --hard` chỉ sau commit sao lưu `backup/<ngày-giờ>`). Version 0.10.0 theo Gate Delegate (tiêu đề này và ba manifest).
- **Sửa — vòng sửa nhỏ sau soát hẹp (SPR-20 TK27d, chưa phát hành):** `scripts/autopilot_guard.py` nhận dạng dính `-Destination:x`/`-Path:x`/`-LiteralPath:x` (lỗ `Move-Item -Path .git -Destination:.tmp/g`), chặn xoá/chuyển sau `cd .git` hay khi thư mục làm việc nằm trong `.git`, glob khớp `.git` (`?git`, `[.]git`), `git -c gc.pruneExpire|reflogExpire*=now` kèm `gc`/`prune`/`reflog`; bỏ `cp` khỏi nhóm nguồn thuộc `.git` (sao chép không phá gì). `method/autopilot.md`: không có công cụ quét secret thì không đẩy (ghi `BR`), thêm phần không chặn được; `method/conventions.md` thêm `branch -D` và nhắc quét secret. Ghim băm vùng `method/autopilot.md` và ba đột biến mới.
- **Sửa — vòng sửa gốc cuối sau soát hẹp lần 2 (SPR-20 TK27e, chưa phát hành):** `scripts/autopilot_guard.py` thay suy đoán theo vị trí token bằng MỘT bộ phân tích tham số PowerShell (`_ps_split`: nhận `-Tên:giá-trị` và `-Tên giá-trị`, tiền tố duy nhất, hoa thường tuỳ ý; tách nguồn/đích/tên mới) dùng chung cho xoá/chuyển/đổi tên/chép (lỗ `Rename-Item .git -NewName:g`); tên mới là `.git` bị chặn; `git -c gc.*expire*=<hạn bất kỳ>` với gc/prune/reflog/maintenance và mọi `--prune=`/`--expire=` bị chặn (không còn liệt kê hạn; `git gc` trần vẫn qua). Thêm test và ba đột biến.

## 0.9.0 (2026-11-12)

- **Đổi, phá tương thích — nguồn distill chỉ ở Workshop (SPR-19):** gỡ `UPSTREAM.md`, `THIRD_PARTY.md`, `docs/updating-from-upstream.md`, mã quét nguồn trong `scripts/check.py` và `tests/test_provenance.py`; gỡ khoá `source`, `source_sha`, `base_sha`, `rewrite_before_public` và `license` dạng danh sách khỏi frontmatter 49 file skill/agent; `NOTICE` còn tên nguồn, dòng bản quyền và văn bản giấy phép. `metadata.roles` là chuỗi ("a, b"). Dự án đọc các file/khoá này phải sửa theo.
- **Đổi — `skill_sha` băm hành vi:** `tree_hash` ở `tests/test_skill_tests.py` bỏ khoá quản trị của frontmatter (`metadata`, khoá nguồn) khỏi băm; vẫn băm `description`, thân và file kèm. Skill chỉ đổi khoá quản trị không phải thử lại.
- **Thêm — test ngược:** `tests/test_no_source_leak.py` (không khoá nguồn ở frontmatter, `roles` là chuỗi, không tên nguồn ngoài `NOTICE`; danh sách tên đọc ngoài repo qua `AGENT_AGILE_SOURCE_NAMES`), `tests/test_root_junk.py`, `tests/test_measure_claims.py` (dời từ `test_provenance.py`).
- **Thêm — cấu trúc repo:** `docs/STRUCTURE.md`, khung `templates/repo-skeleton/` cho repo xưởng; `INSTALL.md` và `GUIDE.md` dời vào `docs/` (con trỏ ngắn ở gốc).
- **Đổi — `closing-sprint` và `running-sprint`:** thư mục tạm của sprint là `.tmp/<SPR-NN>/` và được dọn ở mọi nhánh của menu đóng sprint; nhánh giữ nguyên/bỏ việc ghi `CO` dọn khi PR gộp.
- **Sửa — nội dung skill:** `code-review` mục 5.1 (báo hai lựa chọn sau vòng 3, vòng sau chỉ đọc diff từ mốc trước); `postgres` mục 7–9 (toàn văn `tsvector`, view vật chất hoá, số thứ tự liên tục); `react` mục 8–11 (`useEffectEvent`, form action, `use()`, `React.memo`); `gcp-devops`, `gcp-incident-response` ghi "xem `NOTICE`" thay tên nguồn.

## 0.8.0 (2026-11-12)

- **Đổi — shim git/gh tắt mặc định (SPR-18/TK3, SPR-17/DN2):** `AGENT_AGILE_SHIM` vắng = hook PreToolUse KHÔNG viết lại lệnh Bash/PowerShell ở mọi chế độ quyền; `rewrite` viết lại; `0`/`1` như cũ. Hook `SessionStart` (`scripts/session-env.sh`) chỉ ghi PATH khi `AGENT_AGILE_SHIM=1`; `=0` là công tắc tắt. Test cũ ghim viết lại mặc định ở auto/bypass được đảo.
- **Thêm — rào SPR-16 (chưa nghiệm thu):** gộp nhánh 16c (`claude/spr-16c-session-env`, tức SPR-16/TK12): hook `SessionStart`, shim không gọi vòng khi có hai bản `shims/` trên PATH. Rào autopilot SPR-16 chưa qua Cổng 2; bản này đưa mã vào, chưa khẳng định rào đạt.
- **Sửa — tài liệu:** `README.md`/`README.vi.md` ghi đúng bản 0.8.0 và tình trạng kho; `templates/sprint/PROGRESS.md` mục 6 có hàng tiêu đề sáu cột "Sổ phiên con" (RQ-075).

## 0.7.0 (2026-11-08)

- **Đổi — bỏ `CLAUDE.md` ở gốc:** `claude plugin validate --strict` đỏ khi plugin có `CLAUDE.md` gốc («not loaded as project
  context»). Luật lõi vào Claude Code qua dòng import cấp người dùng như `INSTALL.md` hướng dẫn, hoặc bản ≥ 2.1.277 tự đọc
  `AGENTS.md`; `hosts/claude/README.md` nêu điều kiện và cách `.claude/CLAUDE.md` cục bộ. Test khoá `CLAUDE.md` gốc vắng.
- **Đổi — `agents/README.md` dời sang `docs/agents.md`:** mọi file trong `agents/` thành một agent, nên README cũ hiện
  thành agent rác `agent-agile-team:README` và làm `validate --strict` đỏ. Test khoá: mọi `agents/*.md` phải có
  frontmatter; `.gitignore` bỏ qua `.claude/CLAUDE.md` cục bộ.

Phát hành một lần cho cả ba sprint của RQ-057 (SPR-14, SPR-13, SPR-12) — thêm vai và khoá vai mới, không bỏ gì, nên tăng MINOR
(`method/conventions.md` mục 4.1).

- **Thêm — hai vai T1:** `gate-delegate` (kiểm định: duyệt thay cổng khi được cấp, phiên mới, chỉ đọc hồ sơ) và `advisor`
  (tư vấn: phản biện SPEC/PLAN trước Cổng 1, không viết, không duyệt), có thẻ `roles/verifier/gate-delegate.md`,
  `roles/advisor/advisor.md`, hàng trong `AGENTS.md` và `roles/README.md`, ma trận mẫu chín vai.
- **Thêm — `scripts/check.py`:** khoá vai `gate-delegate` (thuộc `VERIFIERS`, làm `delegation.by` được) và `advisor` (nhóm mới
  `ADVISORS`); cả hai buộc tier T1 (khác → `roles-invalid`). `self-review` khi nhãn `advisor` trùng `analyst`, `architect` hoặc
  `gate-delegate`, hoặc khi nhãn `delegation.by` giữ `advisor`; nhãn `gate-delegate` trùng vai thực thi cũng là `self-review`.
  Hồ sơ không dùng hai khoá này cho kết quả như trước.
- **Thêm — bậc model:** `tiers/README.md` mục 8 tách **bậc model** (1 thấp → 3 cao, chỉ chọn model và effort) khỏi tier
  thẩm quyền T1/T2/T3; vai → bậc; cách tra model id qua bảng tier ngoài repo.
- **Thay đổi — review PLAN:** từ cỡ vừa, Advisor **thay** Tech Reviewer ở lượt review PLAN khi Analyst/Architect chạy ở bậc
  model 2 trên Codex/Antigravity hoặc tác giả PLAN cùng model với Tech Reviewer (`method/process.md` mục 3); `sizing.md`,
  thẻ Tech Reviewer, Architect, skill `plan-review`, `writing-plan` trỏ cùng quy tắc (thử áp lực GREEN chạy lại, `skill_sha` mới).
- **Thay đổi — Researcher:** hợp đồng chỉ tìm kiếm, xem, đọc, tra cứu, trích xuất; mỗi mục kèm trích ngắn và nguồn, không có thì
  "không tìm thấy", không suy diễn; người tổng hợp kiểm lại số dùng để quyết. Mẫu `templates/sprint/BRIEF.md` mục 5.
- **Sửa — test:** `MODEL_NAME` nhận id `gemini-*` có hậu tố effort.
- **Thêm — mở rộng tính năng cho dự án có mã sản phẩm (SPR-13):** `method/feature-expansion.md` — hai không gian mã (sản
  phẩm / dự án), bảng ánh xạ, đối chiếu 13 điểm của một tài liệu BA thật với kết luận giữ / đổi / hỏi, bảng nhân vật → vai
  repo (T3 của dự án ≠ T3 của repo), thứ tự lớp gợi ý cho tính năng full-stack, tên phiên `SPR-NN <tên gọi nhớ>`, chuỗi tìm
  hiểu đọc → tổng hợp → soát → khuyến nghị; mục lục `method/README.md`; nguồn ghi ở `UPSTREAM.md`.
- **Thêm — quy ước mã sản phẩm luôn gạch nối:** `FE-01`, `SCR-033`, `FR-47`; `check` không đọc dạng này, dạng không gạch nối
  (`FE01`) bị báo như mã repo. Không đổi `check.py`, `_common.py`, `.agile.json`; hành vi khoá bằng test
  `test_product_codes_hyphen_ignored`, `test_product_code_without_hyphen_flagged`, ca `id-unknown-prefix-product-code` và fixture
  `tests/fixtures/product-codes/`. Skill `id-convention` mục 2 thêm đoạn trỏ (description giữ nguyên).
- **Thêm — chế độ autopilot duyệt cổng (SPR-12):** `method/autopilot.md` — lệnh chuẩn `Bật autopilot cổng 1|cổng 1+2|chương trình
  … cho SPR-NN …` (hậu tố `+nhánh` cho gộp cục bộ sau Cổng 2 Đạt), `Dừng autopilot.`, `Thu hồi duyệt thay SPR-NN.`; Gate
  Delegate phiên mới là người ký duy nhất, phiên điều phối không ký; danh sách loại đóng 13 mục; sổ phiên con; tạm dừng ≠ kết
  thúc; file dấu `.tmp/autopilot.json`. `AGENTS.md` bước 2/5 gộp câu duyệt thay lặp và trỏ autopilot (108 dòng, 9 901 byte);
  `method/process.md` mục 3, `method/sizing.md`, `roles/README.md` trỏ cùng chỗ.
- **Thêm — `scripts/check.py`:** khoá tuỳ chọn của `delegation` (`level`, `program`, `exclusions`, `channel`, `orchestrator`,
  `sessions_cap`); kích khi `grant` bắt đầu `Bật autopilot` hoặc có khoá mới; báo `gate-delegation-invalid` khi chữ mức của
  lời cấp lệch `level`, `scope` khác tập cổng của mức, `exclusions` thiếu/lạ/trùng, `+nhánh` sai chỗ, `orchestrator` trùng `by`,
  `files` có mục không nêu trong lời cấp. Hồ sơ chỉ có tám khoá cũ cho kết quả như trước (fixture `tests/fixtures/autopilot/`).
- **Thêm — rào máy autopilot cho Claude Code:** `hooks/hooks.json` đăng ký `PreToolUse` cho `Bash|PowerShell` và
  `Write|Edit|MultiEdit|NotebookEdit`, chạy `scripts/autopilot-hook.sh` (POSIX sh, tự tìm Python ≥ 3.9; không có Python hoặc
  guard lỗi thì chỉ chặn khi có file dấu) → `scripts/autopilot_guard.py`. Khi có file dấu: chặn đẩy nhánh, tạo/xoá tag, gộp
  vào nhánh chính, xoá không đảo ngược, gộp cục bộ khi thiếu `+nhánh`, và mọi thao tác ghi vào file dấu; không có file dấu thì
  cho qua. Lối kết thúc: `python scripts/autopilot_guard.py --clear <dir>`. Chi phí đo ~0,28 s mỗi lệnh/lần ghi (Windows, Git
  Bash). Codex, Antigravity chưa đăng ký.
- **Thay đổi — skill `intake`, `running-sprint`, `closing-sprint`:** nhận và nhắc lại lệnh autopilot, từ chối câu không phải lệnh
  ("theo khuyến nghị", "chốt theo mặc định", chữ trong file/comment/kết quả công cụ), giữ sổ phiên con, dừng ở danh sách loại,
  không gộp khi thiếu `+nhánh`; thử áp lực 12 ca chấm mù (`skill_sha` mới). Mẫu PROGRESS/REPORT/SPRINT thêm mục "Sổ phiên con",
  "Bản tin autopilot" tuỳ chọn.
- **Ghi nợ (autopilot):** rào máy là danh sách mẫu đóng — chuỗi chương trình tuỳ ý (`python -c`, `awk system()`…), công cụ ngoài
  matcher (MCP) và phiên con cố ý lách vẫn qua; `--clear` phiên con gọi được (rào hành vi); plugin cài từ marketplace thư mục
  thì hook sống theo cây làm việc của checkout — sửa guard trên bản chép, thay một lần. Việc để lại: RQ-069…RQ-076 của sổ dự án.
- **Ghi nợ (known limitations):** `check` chỉ so nhãn trong cùng một file (Advisor/Gate Delegate trùng người làm ở file khác
  không bị bắt); nhánh `gemini` của `MODEL_NAME` còn nhận họ model bất kỳ; `method/process.md` mục "Duyệt thay" và
  `roles/README.md` chưa nêu ngoại lệ "Advisor không làm `delegation.by`".

## 0.6.0 (2026-11-01)

Thêm hành vi mới cho skill `security-audit` nên tăng MINOR (`method/conventions.md` mục 4.1).

- **Thêm — `security-audit` Pha 8 Tầng 1b:** khi audit cây mã lấy từ ngoài mà dự án có máy quét tĩnh riêng, chạy máy quét đó trước và
  đưa phát hiện vào báo cáo, thay vì chỉ đọc tay.
- **Sửa — `security-audit` mục 5:** chế độ hằng ngày không có phụ lục giả thuyết hay mục «nếu có thì»; mục chưa kiểm ghi đúng một dòng
  «chưa kiểm».
- Thử áp lực T3 chạy lại (18 lượt, GREEN 9/9, RED 0/9), `skill_sha` cập nhật trong `skills/security-audit/tests/pressure.md`.

## 0.5.0 (2026-10-28)

Gộp các đoạn "Chưa phát hành" sau 0.4.0; thêm skill `gcp-devops`, `gcp-incident-response`, `rag-pageindex` nên tăng MINOR (`method/conventions.md` mục 4.1).

- **Sửa — kiểm duyệt thay (`scripts/check.py`):** khi `gate_N_mode: delegated` và cổng đã kết luận, `check.py` đòi `risk_tags` khai
  hợp lệ (danh sách chuỗi; áp cho mọi tài liệu có cổng duyệt thay, kể cả SPEC) và đòi `delegation.by` giữ ít nhất một vai kiểm
  định (`business-reviewer`, `tech-reviewer` hoặc `*-specialist`, vai chuyên đề phải thuộc danh sách chuyên đề đã liệt kê) có tier T1 trong
  `roles` của PLAN, REPORT hoặc SPRINT (SPEC không bị đòi). Cũng khi `gate_N_mode: delegated`, khoá lạ trong khối `delegation` được báo cả khi cổng còn mở (`pending`): chỉ khoá lạ đầu
  tiên, một lần cho mỗi tài liệu. Khối `roles` và luật `self-review` cũng chỉ nhận bốn chuyên đề đã liệt kê (tên khác bị báo vai lạ). Cổng `human` không đổi.
- **Sửa — quét thư mục sprint:** `check.py` không còn tính `evidence/` cạnh tài liệu sprint; thêm cờ `--include-evidence` để
  quét lại như cũ (không dùng cùng `--self`); tên tài liệu sprint được so đúng hoa thường.
- **Thay đổi — mẫu PROGRESS và SPRINT:** cột "Vai · tier · model · effort" thay cho "Vai · tier · model"; effort là số 1–5
  (`method/effort-scale.md`), chưa giao thì ghi `—`.
- **Ghi nợ (known limitations):**
  - các `tests/pressure.md` giữ lệ ghi `model:` hiện có (id model cụ thể trong 33 file), chưa chuẩn hoá thành nhãn trung tính;
  - chưa chạy lại ca đo `in-3` của skill `intake` (lần chấm gần nhất: Đạt một phần, n = 1) và chưa dựng lại rubric riêng của ba
    phép thử routing A/B/C; chỉ còn đề bài và bảng kỳ vọng ở `skills/intake/tests/`;
  - tên cột cũ "Vai · tier · model" còn trong vài tài liệu phụ (`skills/closing-sprint/references/preflight.md`,
    `method/process.md`, `roles/verifier/dual-review.md`, `tiers/README.md`), sẽ đồng bộ ở đợt sửa tài liệu luật.
- **Review nhiều lớp:** skill mới `hooks-guardrails` (hook xác định cho ba harness, không hook gọi model, script
  `protect_paths.py`); `code-review` đọc `REVIEW.md` của repo từ mốc gốc, hội tụ cho review toàn nhánh, nhãn `có từ trước` và năm
  kết cục của phát hiện, bảng bậc rủi ro → người duyệt đọc gì; `verify-before-done` bốn bậc cổng và ảnh cạnh thiết kế; `web-qa` chế
  độ So thiết kế; `security-review` luật đóng phát hiện; `eval-harness` mục chấm lại reviewer (incident → eval, shadow);
  `deployment` và `closing-sprint` hậu kiểm "tầng nào lẽ ra bắt", thân PR có rủi ro còn lại. 33 skill, 13 agent. Không đổi sáu bước,
  hai cổng, tier hay `check`. Mức phiên bản **đề xuất MINOR**, chủ quyết khi nghiệm thu.

## 0.4.0 (2026-10-23)

Gộp các đoạn "Chưa phát hành" sau 0.3.1: hồ sơ vai và thang effort (schema 2), phân loại tác vụ và effort (ứng viên),
giấy phép MIT, bài học lập PLAN lớn, bổ sung quy trình. Mức MINOR do chủ sản phẩm chốt (22/10); sửa nhãn phiên bản lệch (RQ-011) cùng lượt.

**Hồ sơ vai và thang effort 1–5:** bảng tier schema 2 cộng thêm (schema 1 vẫn
hợp lệ) có `effort_scale`, `fallback`, effort số theo tier và theo vai; thang ở `method/effort-scale.md`; ma trận mẫu
`tiers/ROLE-MATRIX.example.md`; vai Researcher (T3); khuyến nghị T1 và duyệt thay có máy kiểm (mặc định tắt); Brief 4 ô ở `intake`,
Kết luận SPEC có rủi ro; luật `task-order`, `task-gap`, `plan-goal-block`; mẫu PLAN ba nhãn; `writing-plan` có checklist 11 ô.

**Giấy phép MIT, repo công khai:** `LICENSE` chuyển sang giấy phép MIT (Copyright (c) 2026 Nguyễn Quang Đức); trường `license` ở `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` và `.claude-plugin/marketplace.json` đổi từ `UNLICENSED` sang `MIT`; `NOTICE`, `README.md`, `README.vi.md`, `INSTALL.md`, `THIRD_PARTY.md`, `UPSTREAM.md`, `docs/standardization.md` bỏ câu "private"/"giữ mọi quyền". `.agile.json` giữ `visibility: private` vì khai báo đó nói về nơi đặt hồ sơ dự án (`artifact_root` là `.`), không phải trạng thái GitHub.

**Phân loại tác vụ và effort:** method candidate có sáu trục, difficulty/effort riêng,
default medium và human override từng field; notice trước thay đổi, ba repair cycles có oracle và
handoff giữ counters. Checker/template opt-in schema 1 + manifest độc lập; 36 synthetic cases chuẩn
bị, chưa pilot. Giữ baseline tier, ngưỡng coverage/denylist, native capabilities của môi trường và hai
cổng. Hồ sơ: `docs/plans/2026-10-12-task-routing/`; migration: `docs/MIGRATION.md` mục 5.
Luật lõi/skill pressure/reviews/pilot/release có trạng thái riêng; chưa promotion.

- **2026-10-12:** thẻ `roles/verifier/dual-review.md` phân biệt lượt review với vòng thực hiện sửa có kiểm chứng; sau vòng sửa ba còn kẹt hoặc regression thì dừng assignment và bàn giao, giữ counter và chỉ định người dùng. Hồ sơ và review: `docs/plans/2026-10-12-task-routing/`.
- **2026-10-12:** nối `intake`, `writing-plan`, `running-sprint` và `token-economy` với hợp đồng phân loại/effort/notice hiện có; `running-sprint` giữ trần ba lần sửa có kiểm chứng và lịch sử bàn giao. Intake có bằng chứng một phần; ba candidate còn lại chưa kiểm chứng hành vi sau giới hạn ngân sách của người dùng. Không kế thừa kết quả thử của bản cũ cho bản mới, không phát hành hoặc đổi file luật đang chạy.

**Bài học lập PLAN lớn:** `writing-plan` mục 6b (hợp đồng bàn giao trước fan-out, tự kiểm chứng mã trước review, đồng bộ chéo sau mỗi lần sửa, trần 2–3 vòng review, PLAN ngắn) và `plan-review` mục 10 (re-review hẹp theo diff, trần vòng, phân loại phát hiện theo nguồn, bắt buộc `file:dòng`). Nguồn: chuỗi năm sprint nội bộ (10 vòng, 82 phát hiện, khoảng 15 triệu token). Không đổi sáu bước, hai cổng hay tier.

**Bổ sung quy trình:** nối thẻ Analyst đến quy trình; đưa thẻ vai vào brief và giữ
người cung cấp nguồn cùng tình trạng kiểm chứng qua bàn giao. Không thêm script, không đổi sáu bước,
hai cổng hay tier. Đã kiểm hành vi bằng tình huống mô phỏng và review độc lập; kết quả một lượt không
chứng minh độ tin cậy tổng quát.

## 0.3.1 (2026-10-14)

Gắn `.mcp.json` cho `pageindex-mcp` (SPR-13, repo dời về thư mục plugins của hệ chủ); không đổi luật lõi hay skill.
Bản phát hành để cache plugin theo kịp nguồn; phần "Chưa phát hành" phía trên vẫn chưa vào bản nào.

**MCP đi kèm plugin:** thêm `.mcp.json` khai `pageindex-mcp` theo thư mục lấy từ biến `PAGEINDEX_MCP_DIR` (tên biến trung tính do plugin định nghĩa); INSTALL mục 5 có ghi chú.

## 0.3.0 (2026-10-05)

SPR-04 — nội dung Đợt 2 (phần mới), luật bậc việc đơn giản / phức tạp, sổ tập trung, quy tắc số phiên
bản, viết lại phòng sạch 7 đích private, trả nợ máy kiểm của SPR-02. Mức MINOR theo `method/conventions.md` mục 4.1: thêm
skill, agent và luật tương thích ngược, dự án cũ không phải sửa gì (phân vân → chọn mức cao hơn: chưa có thay đổi gãy nào).

- **Tiếp nhận và làm thẳng:** một tin gom nhắc mục tiêu, phản biện có đề xuất, bậc/rủi ro từng việc và hỏi mở sprint;
  chờ xác nhận rồi mới ghi yêu cầu. Bậc làm thẳng không có hồ sơ; định nghĩa thao tác không đếm tự kiểm/test đi kèm,
  giữ sàn cỡ cho sửa luồng/tính năng/rủi ro, cấm chia một mục tiêu để né sprint. Đồng bộ role, REQUESTS mẫu/sample,
  sizing/process và hướng dẫn nâng cấp. Intake QA cùng model: baseline 2/6 → GREEN 6/6 (`n = 1`); thước `in-4` sửa sau
  quan sát để tránh hỏi lại lời giao, giới hạn ghi trong file thử.
- **Tài liệu và giới thiệu:** bổ sung lỗi cài/cập nhật, nâng cấp `0.1`/`0.2` → `0.3.0`, tổng quan và chuẩn hoá;
  trang giới thiệu được quản lý ở repo riêng, ảnh quy trình PNG và nội dung theo hai luật mới. Gói này không chứa site.
- **Model thử skill:** máy kiểm chấp nhận tên GPT có phiên bản, giữ chặn placeholder; test hồi quy GPT thấy đỏ trước
  sửa và xanh sau sửa. Ba manifest đồng bộ `0.3.0`; không thay ngưỡng coverage hay config kiểm thử.
- **Sửa sau review phát hành:** "làm luôn" chỉ thúc tiến độ, không miễn sprint/vùng rủi ro; cần người dùng nói rõ
  "không cần sprint" cho đúng việc hoặc việc đủ điều kiện làm thẳng. Thu hẹp cam kết nâng cấp thành tương thích hình
  hồ sơ, nêu nội dung có thể cần sửa. Siết hình ID GPT: một major 1–99, minor 0–99 tuỳ chọn, đúng một family;
  đây là kiểm định dạng metadata, không thay bằng chứng model thật sự chạy hay khoá danh sách phiên bản hiện tại.
- **Ranh giới đầu vào và tin tiếp nhận:** nhãn `external_input` áp khi thêm/đổi ranh giới nhận và xử lý dữ liệu
  không tin cậy; trường UI có sẵn không tự tạo nhãn, chưa loại trừ tác động bảo mật vẫn nâng lớn. Tin tiếp nhận phải
  được viết nguyên văn trong lượt hiện tại; câu hứa "sẽ gửi tin gom" chưa phải sản phẩm tiếp nhận.

- **Bậc việc** (`TK2`): việc **rất nhỏ** một `SPRINT.md` hai phần (Kế hoạch, Kết quả), việc **nhỏ** một `SPRINT.md`
  bốn phần, từ cỡ vừa bốn tài liệu; `init --tiny` và `init --size small`, mẫu `templates/sprint/SPRINT-tiny.md`, luật
  `check` `sprint-size-mismatch`, `method/sizing.md` mục 5 đối chiếu luồng orch ↔ bậc việc ↔ cổng; hai sprint mẫu mới ở
  `samples/order-desk/`. `AGENTS.md` đổi đúng một câu (bậc nhỏ và rất nhỏ); sprint cũ dạng một file bốn phần cỡ rất nhỏ vẫn
  hợp lệ.
- **Sổ tập trung** (`TK3`): khoá `ledger.project` ở `.agile.json`, biến môi trường `AGENT_AGILE_LEDGER` (mẫu đường, máy cấp),
  khuôn `templates/registry/LEDGER.md`, bốn luật `check` (`ledger-missing-row`, `ledger-stale`, `ledger-unreadable`,
  `ledger-unconfigured`), `method/process.md` mục 11 "Ghi sổ tại cổng". Dự án không khai khoá thì không áp.
- **Phương pháp** (`TK4`): `method/review-gate.md` (cổng review bốn pha), `roles/verifier/dual-review.md` (hai reviewer
  độc lập cho việc có `risk_tags` `rules` / `secret` / `auth`), `method/process.md` mục 6.1 (thiết kế vòng lặp),
  `method/evidence.md` mục 8 (cổng giao hàng, luật văn bản không hook), `skills/verify-before-done/references/loop.md`,
  luật giữ spec sống ở `templates/registry/feature-spec.md`.
- **Thẻ vai và skill quy trình** (`TK5`): thẻ Architect và Implementer (tìm cái có sẵn, theo phong cách file đang sửa, lát
  giao được độc lập); `intake` (luật nghiệp vụ không đọc được từ mã, tiêu chí nghiệm thu quan sát được), `shaping-spec`
  (+ `references/spec-mining.md`, một `FR` một hành vi), `tdd` (ca biên bắt buộc có test), `verify-before-done`,
  `running-sprint` (nhắc ghi sổ ở cổng); mỗi skill sửa có RED/GREEN và `skill_sha` mới.
- **Chuẩn code** (`TK6`): `method/standards/` — 7 chuẩn chung `common/`, `python.md`, `typescript.md`, `react.md`, `web.md`,
  bảng đối chiếu chuẩn ↔ skill; thẻ Implementer và Tech Reviewer trỏ tới, **không** nạp vào `AGENTS.md`.
- **Sáu agent mới** (`TK7`): `code-explorer`, `code-reviewer`, `test-analyzer`, `typescript-reviewer`, `react-reviewer` (chỉ
  đọc) và `build-fixer` (agent **duy nhất được sửa file**, T2); mỗi agent chạy thử trên fixture, `tests/fixtures/agents/`.
- **Bốn skill mới và phần bổ sung** (`TK8`, `TK9`): `react` (+ `references/testing.md`), `frontend` (+ `references/vite.md`),
  `e2e-testing` (+ `references/ai-regression.md`), `eval-harness`; `web-qa` (chỉ báo cáo, ranh giới và nhiệm vụ khám phá,
  cách đếm điểm, kiểm lại sau sửa), `code-review` (+ `references/duplicates.md`, sửa kèm test hồi quy là một lựa chọn),
  `closing-sprint` (phần ship, cổng CI của đúng commit, đề xuất mức phiên bản), `token-economy` mục 7 (truy xuất lặp);
  thẻ QA mục 9 (đo và ghi coverage); thẻ chuyên đề frontend mục 9 (a11y WCAG 2.2 AA).
- **Viết lại phòng sạch** (`TK10`): `bug-triage`, `adr`, `database-migrations/references/rehearsal.md`,
  `closing-sprint/references/release-notes.md` và `preflight.md`, bảng phủ `FR` → `VR` của thẻ QA, bốn ô "Bắt gì" của
  `scripts/README.md`: bản cũ gỡ khỏi cây trước, người viết mới chỉ nhận danh sách ý dạng cụm danh từ, để lại nhật ký đường
  đã đọc; 8-gram so với cả gốc private lẫn bản trước đó bằng 0 trên phần viết lại, sau khi loại stoplist cụm chung. Nguồn
  ghi dạng `concept:`; `THIRD_PARTY.md` mục 3 trống.
- **Đính chính (2026-10-04):** mục `0.2.0-dev` bên dưới ghi 7 đích đó "chưa đạt quy trình phòng sạch, phải viết lại thật
  sự trước khi công khai" — đúng tại thời điểm đó; từ `0.3.0-dev` câu này không còn đúng, 7 đích đã viết lại phòng sạch ở
  `TK10` và không còn file nào chờ viết lại. Mục `0.2.0-dev` giữ nguyên vì changelog chỉ thêm.
- **Nội dung thêm cho skill tham chiếu** (`TK11`): `github-ops`, `database-migrations`, `error-handling`, `fastapi`, `python`,
  `worktrees`, `deployment`, `postgres` thêm phần còn thiếu, mỗi skill chạy lại truy xuất bộ câu cũ.
- **Máy kiểm** (`TK12`): `tests/test_skill_tests.py` bỏ miễn theo ngày — **mọi** file thử phải có `skill_sha` và `tier`
  (ca đột biến với file ngày 2026-10-01 và 2025-01-01); `result` và `model` theo danh sách trắng; phép kiểm 8-gram nhận mọi
  cách viết, buộc điều kiện "loại stoplist"; luật `check` về nhãn mức kiểu nguồn; fixture `security-audit` đổi sang giá trị giả không khớp mẫu khoá thật; `writing-skills` thống nhất
  một quy ước "sửa lưới" và mục nạp bản worktree.
- **Thử truy xuất và định tuyến** (`TK13`): 13 skill tham chiếu (`react`, `frontend`, `e2e-testing`, `adr`, `api-design`,
  `postgres`, `github-ops`, `database-migrations`, `error-handling`, `fastapi`, `python`, `worktrees`, `deployment`) thử truy
  xuất bằng bộ câu mới do QA độc lập soạn, kỳ vọng ghi trước khi đọc skill, hai lượt: lượt 1 thấy 12/13 skill dưới ngưỡng (chỉ
  `adr` đạt; không câu nào Không đạt — skill thiếu nội dung, agent không bịa), `references/` được bổ sung có nguồn rồi chạy lại
  bộ câu mới ở lượt 2, kết quả vẫn 12/13 skill dưới ngưỡng (chỉ `adr` đạt) — để lại sang sprint sau, đổi cách đo trước khi vá
  tiếp; định tuyến 21 câu (12 câu ranh giới, đủ 5 cặp dễ nhầm) đối chiếu danh mục 49 mục; `n = 3` cho 5 skill
  (`writing-skills`, `closing-sprint`, `bug-triage`, `security-audit`, `web-qa`).
- **Quy tắc số phiên bản** (`TK15`): `method/conventions.md` mục 4.1 (MAJOR · MINOR · PATCH, bốn điều đi kèm); agent đề xuất
  mức tăng kèm lý do ở Cổng 2, người dùng quyết.
- **Dấu vết và tài liệu** (`TK14`): `UPSTREAM.md` — khối Đợt 2 thành khối chốt có bảng thành phần đã distill, bảng nguồn theo
  skill/agent và thành phần ngoài skill, mục "Đợt 3 — dự kiến"; `NOTICE` (superpowers-lab thành nguồn đã dùng),
  `THIRD_PARTY.md` mục 1; số đếm **32 skill, 13 agent** (agent chỉ đọc, riêng `build-fixer` được sửa) ở `README.md`,
  `README.vi.md`, `GUIDE.md`, `agents/README.md`, `skills/README.md`, `hosts/claude/README.md` và mô tả 3 manifest; dòng trỏ
  ở `method/README.md`, `roles/README.md`.
- **Hai vòng sửa sau review tổng thể** (`fix-1`, `fix-2`): `dual-review` nối vào luồng chính (`process.md`);
  ngoại lệ bảo mật (phát hiện tin cậy 5–6) vào danh sách chính "cần kiểm" ở cổng
  review và ở agent; `closing-sprint` so mốc với HEAD sau Cổng 2 là `sha7` của menu, tách nhãn CI không có / chưa chạy; tự
  kiểm chỉ hợp lệ ở cỡ rất nhỏ — cỡ nhỏ trở lên `qa` trùng nhãn người làm vẫn là Phải sửa dù có khai (`severity.md`,
  `roles/README.md`, `evidence.md`, `templates/README.md`), và chữ về `check` nói đúng khả năng thật (bắt khi không khai, hoặc
  khai mà `verdict: pass`); `check` không in traceback khi `.agile.json` sai hình; `description` của `closing-sprint` và
  `database-migrations` viết lại phòng sạch (đo 8-gram 0 hai mốc, sau khi loại stoplist cụm chung); `adr` điểm 3 chỉ cho ADR
  lúc PLAN, `preflight.md` ô lớn × `high` thêm reviewer kỹ thuật thứ hai; `docs-sync` chỉ sửa thân PR sau khi người dùng
  chọn push + PR.
- Phiên bản các manifest (`.claude-plugin`, `.codex-plugin`, `marketplace.json`) lên `0.3.0-dev`.

## 0.2.0-dev

Chưa phát hành. SPR-02 — làm cứng Đợt 1 (phần nội dung mới của Đợt 2 chưa làm, xem `UPSTREAM.md` mục "Đợt 2 —
dự kiến").

- Mốc Đợt 2: khối "Đợt 2 — chốt SHA 2026-10-03" và một dòng nhật ký kiểm cho 20 nguồn repo ở `UPSTREAM.md`;
  `ccusage` đổi tên chủ thành `ccusage/ccusage` (`UPSTREAM_OWNERS` giữ cả `ryoppippi`). Bảng nguồn theo
  skill/agent ghi đúng `ef648e01` cho 7 mục đã viết lại sâu, `postgres` thêm nguồn thứ hai
  `agents/database-reviewer.md`; `docs/updating-from-upstream.md` mục 4 nói rõ `base_sha` giữ nguyên khi đổi
  `source_sha`.
- Viết lại sâu 9 mục "gọn" của Đợt 1 có nguồn công khai, đối chiếu ECC `ef648e01` (và Superpowers `8ca22dba`
  cho `diagnosing.md`): `deployment` (+ `references/docker.md`), `fastapi`, `postgres` (+
  `references/diagnostics.md`), bốn agent `fastapi-reviewer`, `database-reviewer`, `comment-analyzer`,
  `rag-pipeline-reviewer`, và `writing-skills/references/diagnosing.md`.
- Viết lại 7 đích từ danh sách ý lấy từ nguồn private, có mang một số câu chữ nguồn; 8-gram bằng 0 sau khi loại stoplist 45 cụm chung (trước khi loại: còn cụm trùng ở 5/7 đích); chưa đạt quy trình phòng sạch, phải viết lại thật sự trước khi công khai (`CO2`, `RQ-021` ở hồ sơ riêng của chủ repo):
  `bug-triage`, `adr`,
  `database-migrations/references/rehearsal.md`, `closing-sprint/references/release-notes.md` và
  `preflight.md`, bảng phủ `FR` → `VR` của thẻ QA, bốn luật truy vết trong `scripts/README.md`. Cờ
  `rewrite_before_public: true` không còn ở skill hay agent nào.
- Thử áp lực nền (RED rồi GREEN) cho `intake`, `shaping-spec`, `writing-plan`, `running-sprint`,
  `closing-sprint`, `bug-triage`, và cho `security-audit`, `web-qa`; thử truy xuất cho 10 skill tham chiếu
  (`adr`, `api-design`, `database-migrations`, `deployment`, `error-handling`, `fastapi`, `github-ops`,
  `postgres`, `python`, `worktrees`); thử định tuyến 14/14. Cả 28 skill giờ có tệp thử đã chạy
  (`skills/README.md` mục 4).
- `tests/test_skill_tests.py`: máy kiểm tệp thử — skill kỷ luật có `pressure.md`, skill tham chiếu có
  `retrieval.md`, `result`/`model`/`date` hợp lệ, `skill_sha` khớp băm cây skill trừ `tests/` (skill đổi sau
  khi thử thì đỏ; `git` có mà lỗi thì đỏ, chỉ thiếu lệnh `git` mới skip); có ca đột biến cho trạng thái chưa chạy
  (kể cả giá trị mở đầu bằng dấu câu như `(pending)`), `date`, thiếu `skill_sha`/`tier`, và ca repo git tạm cho
  phép băm cùng cho kiểm thiếu tệp thử theo `metadata.kind`.
- Phiên bản các manifest (`.claude-plugin`, `.codex-plugin`, `marketplace.json`) lên `0.2.0-dev`. Số đếm không
  đổi: 28 skill, 7 agent.

## 0.1.0-dev

Chưa phát hành.

- Khung repo: cây thư mục, luật lõi dạng khung, manifest khung cho Claude và Codex, con trỏ cho
  Antigravity, hợp đồng hai điểm cắm `AGENT_AGILE_TIERS` và `AGENT_AGILE_DENYLIST`, test đồng bộ version.
- Distill Đợt 1 (SHA chốt 2026-10-01): 28 skill phẳng trong `skills/` chia 5 nhóm — Quy trình (6),
  Kỹ thuật (12, trong đó 10 skill tham chiếu `metadata.kind: reference`), Kiểm định (6), Giao tiếp & tối
  ưu (3), Meta (1) — và 7 agent reviewer chỉ-đọc trong `agents/`. Nguồn: Superpowers, ECC, gstack (MIT),
  bộ skill quy trình private (gốc không giấy phép, gắn `rewrite_before_public: true` ở 4 skill), nguồn khái
  niệm chỉ lấy ý. Mỗi skill/agent ghi `source`, `source_sha`, `license` (và `base_sha` khi có) trong
  frontmatter.
- Dấu vết: `UPSTREAM.md` (bảng nguồn theo từng skill/agent), `NOTICE` (bản quyền MIT của Superpowers, ECC,
  gstack, Supabase Agent Skills), `THIRD_PARTY.md` (nguồn chỉ lấy ý, danh sách file phải viết lại trước khi
  công khai), `docs/MIGRATION.md` (tên cũ → tên mới).
- Mẫu: SPEC thêm mục "Đổi hợp đồng / giao diện" và dấu delta `(sửa …)`/`(bỏ …)`; spec sống ghi cách gộp
  delta Thêm / Sửa / Bỏ ở Bước 5; REPORT mục Review & Retro đọc lại `Phán quyết:` và rà nợ `CO`. Thẻ QA thêm
  bảng phủ `FR` → `VR` theo tầng test thấp nhất. `pytest` gom thêm test trong `skills/`.
- Thử áp lực bắt buộc cho skill kỷ luật/quy trình (`tests/pressure.md`); skill tham chiếu miễn ở Đợt 1,
  Đợt 2 thêm `tests/retrieval.md`.
- Vòng sửa 1 sau kiểm định Đợt 1: nợ `CO` chuyển thành dòng `RQ-` trong REQUESTS ngay khi ghi REPORT (retro
  chỉ đọc khối "Đang mở"); luật `leak-denylist` khớp nguyên từ cho mục chữ, chuỗi con cho mục đường dẫn;
  `tests/test_provenance.py` kiểm nguồn gốc mọi skill/agent với `UPSTREAM.md`, `THIRD_PARTY.md`.
- TK6.5 — vướng mắc của sprint thử đầu tiên: `init --title-file` và cảnh báo tiêu đề mất dấu, cảnh báo sớm khi
  thiếu `AGENT_AGILE_TIERS`, dòng sprint thật đầu tiên xoá comment ví dụ của SPRINTS; `index` gặp sổ không UTF-8
  thoát 2 có thông báo; `check` che code span ngắt dòng (thận trọng), gợi ý khi mã bị bắt kề dấu huyền, nhận
  `.agile.json` truyền thẳng, luật Ghi chú `id-list-lead`; thiếu bảng tier thì dùng chỉ định tier → model trong
  chat, chưa có thì hỏi ở Cổng 1; mẫu REPORT có tiểu mục "Review PLAN trước Cổng 1", mẫu SPEC nhắc số đo trước
  sprint; `writing-plan` có luật cho `TK` tác động ngoài worktree; câu dẫn "tài liệu + nghĩa in đậm" trước mọi
  danh sách / bảng mã (`id-convention`, `response-style`, `AGENTS.md`, mẫu, dự án mẫu).
- TK8.1–TK8.2 — đóng gói ba harness: manifest thật (tác giả trung tính, mô tả đủ 28 skill / 7 agent; Claude
  để mặc định dò `skills/` và `agents/`), `hosts/README.md` (bảng harness + năm điểm cắm của lớp riêng + hợp
  đồng nơi lưu bài học), bốn `hosts/*/README.md` viết thật, `INSTALL.md` cho agent đọc kèm prompt dán Việt/Anh,
  `GUIDE.md` (sprint đầu tiên cho người mới), `README.md` + `README.vi.md` có mục cài và ghi nhận nguồn,
  `docs/standardization.md` (áp khuôn 13 mục: 10 áp dụng, 3 điều chỉnh).
- Ba mục khuôn còn lại: `tests/test_install_docs.py` (prompt VI/EN ≤12 dòng, đủ bước và bốn `hosts/`, link nội
  bộ không gãy — `A5`), `docs/troubleshooting.md` sáu triệu chứng, được README/GUIDE/INSTALL trỏ tới (`A10`),
  `.github/workflows/verify.yml` — 3 hệ điều hành × Python 3.9/3.13, mọi nhánh, `contents: read`, action ghim
  SHA (`A11`).
- Vòng sửa 1 sau kiểm định TK8: lệnh Windows dùng `"$HOME\agent-agile-team"` (PowerShell 5.1 không mở `~` cho
  chương trình ngoài) ở INSTALL, README, GUIDE, `hosts/claude`, kèm triệu chứng thứ bảy ở `docs/troubleshooting.md`
  và test bắt `~` trong khối PowerShell; miễn trừ chống rò thành danh sách tường minh `LEAK_EXEMPTIONS` trong
  `check.py` (mỗi mục một kiểu, một lý do): `THIRD_PARTY.md` chỉ miễn dòng ghi công, `UPSTREAM.md` chỉ che
  `owner/repo` và SHA, `docs/MIGRATION.md` chỉ che mã skill cũ `bộ:tên`; nguồn private gọi trung tính
  ("bộ skill quy trình private", `private-process-skills` trong frontmatter); `pytest==8.4.2` ghim trong CI.
- Tác giả và địa chỉ repo: ba manifest ghi `author` (tên, email, trang), `homepage`, `repository`; README
  EN/VI có mục Author/Tác giả; dòng Copyright của `NOTICE`, `LICENSE` ghi tên tác giả (giấy phép vẫn "All
  rights reserved — private"); URL repo thật thay `OWNER/agent-agile-team` ở INSTALL, README, `hosts/`. Chống rò
  thêm nhóm miễn trừ có chủ đích `author-attribution` (kiểu `author-field`, `author-section`, `author-url`) —
  tên tác giả ở chỗ khác vẫn bị chặn.
- Theo dõi nguồn gốc: `UPSTREAM.md` thêm "Sổ theo dõi nguồn gốc" (21 repo + 7 tài liệu web: vai trò, nơi nhận
  nội dung, mốc đã distill, lần kiểm gần nhất, khi nào kiểm — gồm cả nguồn đã loại và điều kiện xét lại),
  "Nhật ký kiểm bản mới" và "Đợt 2 — dự kiến" (thành phần đã chọn, đích, mức lấy/xét); quy trình
  `docs/updating-from-upstream.md` (khi nào kiểm, so HEAD với mốc, quyết định lấy/bỏ qua/hoãn, distill như một
  sprint, mở rộng phải ghi sổ trước), con trỏ từ `AGENTS.md`, README, `docs/README.md`. `UPSTREAM_OWNERS` thêm
  `rtk-ai`, `oraios`, `mksglu`, `microsoft`; `tests/test_provenance.py` đỏ khi Sổ theo dõi thiếu nguồn nhắc ở
  `UPSTREAM.md` hay frontmatter, hoặc lệch với `UPSTREAM_OWNERS`.
- CI lượt đầu đỏ ở cả ba job Python 3.9: test ghi file bằng `Path.write_text(newline=...)` — tham số chỉ có từ
  Python 3.10. Test đổi sang tiện ích `write_lf` trong `tests/conftest.py` (ghi byte UTF-8, giữ LF);
  `tests/test_common.py` đỏ khi mã trong `scripts/`, `tests/`, `skills/` vượt mức sàn Python của
  `verify.yml` (cú pháp, hoặc `write_text`/`read_text` có `newline=`).
- `A11` chạy thật: run `37077757196` (commit `2a09e34`) xanh 6/6 job (Ubuntu, Windows, macOS × Python 3.9/3.13);
  `docs/standardization.md` ghi `A11` xong. Việc để lại "chạy lần đầu `verify.yml`" bên dưới đã xong.
- `hosts/claude/README.md`: trên Claude, skill dựng sẵn tên trần `code-review` / `security-review` thắng tên trần,
  nên khi skill của repo nói "skill `code-review`" thì gọi `agent-agile-team:code-review` (tương tự
  `security-review`); skill và luật lõi giữ tên trần để không phụ thuộc harness.

**Việc để lại (Đợt 2):**

- Chạy thử áp lực 6 skill quy trình đã có kịch bản: `intake`, `shaping-spec`, `writing-plan`,
  `running-sprint`, `closing-sprint`, `bug-triage`.
- Viết và chạy thử áp lực `security-audit`, `web-qa` (ngoại lệ chỉ báo cáo ở Đợt 1 — `skills/README.md`
  mục 2).
- `tests/retrieval.md` cho 10 skill tham chiếu.
- Chạy lần đầu `.github/workflows/verify.yml` khi đẩy lên GitHub private (`A11` — đã viết, chưa chạy).
