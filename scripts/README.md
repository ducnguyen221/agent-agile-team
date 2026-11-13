# scripts/

Ba công cụ cho dự án áp dụng, chỉ dùng thư viện chuẩn Python (3.9+), chạy được trên Windows và macOS. Hợp
đồng đầy đủ (tập con YAML, khoá, tiêu đề, sổ gốc, cấu hình) ở [`templates/README.md`](../templates/README.md).

| Script | Việc |
|---|---|
| `init.py` | Dựng `.agile.json`, ba sổ gốc và khung sprint từ `templates/`; mặc định chạy thử, không ghi đè |
| `check.py` | Kiểm chuẩn tài liệu; `--self` kiểm lõi sạch và ngân sách `AGENTS.md` của chính repo |
| `index.py` | Sinh lại khối "Đang mở" ở đầu ba sổ gốc |
| `autopilot_guard.py` | Hook `PreToolUse` của autopilot: từ chối lệnh shell thuộc danh sách loại khi có file dấu `.tmp/autopilot.json`; đã đăng ký cho Claude qua `hooks/hooks.json` (launcher `autopilot-hook.sh`), Codex và Antigravity chưa (mục "Rào máy autopilot") |
| `_autopilot_rules.py` | Rào autopilot gom một chỗ (SPR-16): hằng `AUTOPILOT_*`/`DELEGATION_*`, `FENCE_FILES`, `FLOOR_ZONES`/`FLOOR_FILES`, `zone_spans`, hàm `autopilot_problem(block)` mà `check.py` gọi; guard và `check` nhập từ đây, guard không nhập `check`; không chạy trực tiếp |
| `floor_check.py` | `python -X utf8 scripts/floor_check.py --base <ref> [--head <ref>] [--mode strict\|report] [--json] [--root <repo>]`: so vùng giữa mốc `san-cung`, vị trí mốc và nội dung `FLOOR_FILES` của head với base; thoát 0 đạt / `bootstrap` / `report`, 1 vi phạm ở `strict`, 2 lỗi dùng. Bước CI `Floor vs base` giải `git archive <base> scripts` ra thư mục tạm rồi chạy **bản của base** (khe hở workflow-từ-head: xem `.github/workflows/verify.yml`; tới SPR-17 đây là rào hành vi có kiểm) |
| `_common.py` | Thư viện chung: đọc frontmatter tập con YAML, che mã trong Markdown, đọc `.agile.json`; không chạy trực tiếp |

## Cách chạy

```text
python scripts/init.py <gốc-dự-án>                     # chạy thử: in "+ tạo / ~ sửa / = giữ", không ghi
python scripts/init.py <gốc-dự-án> --apply             # ghi .agile.json + REQUESTS, SPRINTS, SPECS
python scripts/init.py <gốc-dự-án> --apply --sprint <slug> (--title "<mục tiêu>" | --title-file <file>) [--tiny]
       [--size tiny|small|medium|large] [--risk normal|high] [--risk-tags a,b] [--request RQ-NNN] [--feature FS-NNN]
       [--date YYYY-MM-DD]
python scripts/check.py <file.md|.agile.json|thư-mục> [...] [--include-evidence]   # thư mục: quét đệ quy *.md và mọi .agile.json
python scripts/check.py <thư-mục-pilot> --routing-manifest <manifest.json>
python scripts/check.py --self [--root <repo>]
python scripts/index.py <gốc-dự-án> [--check]          # --check: không ghi, thoát 1 nếu sổ chưa cập nhật
```

**Tiêu đề có dấu tiếng Việt.** Các script đọc và ghi file bằng UTF-8, in ra console bằng UTF-8, và nhận tham số
dạng Unicode của Windows — dấu không mất trong script. Nếu shell gọi (một số cầu Git Bash / `cmd` với code page
cũ) đã làm mất dấu trước khi tới Python thì script không khôi phục được: dùng `--title-file <file UTF-8>`, hoặc
chạy `python -X utf8 scripts/init.py …` từ PowerShell. `init` cảnh báo ra stderr khi tiêu đề có ký tự thay thế
U+FFFD hoặc `?` kẹp giữa hai chữ (`c?ch`); câu hỏi hợp lệ như "Có nên cache?" không bị cảnh báo.

Dòng sprint đầu tiên `init` ghi vào SPRINTS thay luôn comment dòng ví dụ của mẫu (mẫu dặn xoá khi ghi dòng thật).

**Quét thư mục không tính `evidence/`.** Khi `check.py` quét một **thư mục**, nó bỏ qua thư mục con tên `evidence`
**nằm cạnh tài liệu sprint** — tức thư mục cha trực tiếp của `evidence/` có file `SPEC.md`, `PLAN.md`, `PROGRESS.md`,
`REPORT.md` hoặc `SPRINT.md` (so đúng hoa/thường trên mọi hệ điều hành). Hồ sơ kèm (log, dossier, ghi chú) ở đó không phải tài liệu sprint, nên số phát hiện
của một thư mục sprint bằng tổng số phát hiện của các file `.md` ngoài `evidence/`. Quy tắc áp cho cả `*.md` và `.agile.json` dưới `evidence/`.
Thư mục `evidence` ở chỗ khác (cha không có tài liệu sprint) là tài liệu thật của dự án và vẫn được quét. Cờ
`--include-evidence` quét lại cả `evidence/` cạnh tài liệu sprint (hành vi cũ). Đường file truyền đích danh, hoặc
chính thư mục `evidence/` truyền làm gốc quét, luôn được kiểm, có cờ hay không. `--self` không đổi và không nhận cờ này.

## Rào máy autopilot

`python scripts/autopilot_guard.py --format {claude,codex,antigravity}` đọc sự kiện `PreToolUse` ở stdin. Thiết kế: [`method/autopilot.md`](../method/autopilot.md) mục 5; test: `tests/test_autopilot_guard.py`. **Đã đăng ký cho Claude** qua `hooks/hooks.json` (plugin nạp hook `PreToolUse` gọi launcher `sh "${CLAUDE_PLUGIN_ROOT}/scripts/autopilot-hook.sh" --format claude`, `timeout: 10`, `onFailure: block`; một khối matcher `Bash|PowerShell`, một khối `Write|Edit|MultiEdit|NotebookEdit`). **Codex và Antigravity chưa đăng ký**: đăng ký là sửa cấu hình harness (hỏi người dùng đủ 5 ý trước); Codex còn cần **người dùng** trust hook qua `/hooks`.

- **Không có file dấu** `.tmp/autopilot.json` (tìm từ thư mục làm việc của sự kiện đi lên, dừng sau cấp đầu tiên có `.git`) → cho qua: Claude/Codex thoát 0 không in, Antigravity in `{}`.
- **Có file dấu** và lệnh shell khớp mẫu của mục đang bật → chặn trước khi chạy: Claude/Codex thoát 2, stderr `autopilot: '<mục loại>' cần người dùng nói trong chat — lệnh không chạy`; Antigravity thoát 0, stdout JSON `{"decision": "deny", "reason": …}`.
- **Mẫu có sẵn:** chỉ `irreversible_delete` (cả `find -delete`/`-exec`, `git worktree remove --force`); lệnh git khác (đẩy, tag, gộp, `reset --hard`, `branch -D`, `clean -f`) không còn bị hook chặn từ SPR-20 TK21; sáu mục luôn chặn còn lại (`secret`, `auth`, `rules_unlisted`, `user_soul`, `license`, `network_fetch`) là rào hành vi (không có mẫu). Tên mục lấy từ `_autopilot_rules.AUTOPILOT_EXCLUSIONS` (một nguồn; `tests/test_autopilot_guard.py` ghim đúng 13 mục bằng danh sách viết tay: bớt mục ở `check.py` làm test đỏ, nhưng ai sửa được `check.py` cũng sửa được test — điều phối soát diff hai file khi nhận báo). Công cụ shell: Claude `Bash`/`PowerShell`, Codex `shell`/`Bash`/`exec_command`, Antigravity `run_command`; khoá lệnh `tool_input.command`/`cmd`, `toolCall.args.CommandLine`.
- **Đóng an toàn:** file dấu hỏng → chặn mọi lệnh khớp mẫu (lý do nêu "file dấu hỏng"); `exclusions` thiếu mục bắt buộc → hook bổ sung đủ; ngoại lệ sau khi đã đọc được sự kiện → chặn khi có file dấu từ thư mục sự kiện; JSON hỏng (chưa có thư mục sự kiện) → dò từ thư mục của tiến trình; không có file dấu thì cho qua. Không gọi tiến trình con (nhánh hiện tại đọc từ `.git/HEAD`, hỗ trợ worktree).
- **Giới hạn đã biết:** mẫu là danh sách đóng, tách lệnh thô theo `&&`, `||`, `;`, `|`, `&`, xuống dòng (chặn nhầm `git commit -m "a && git push"`). Thư mục lệnh = `tool_input.workdir`/`cwd`, `toolCall.args.Cwd`, rồi `cwd` phiên (thư mục phiên cũng được dò file dấu); nhánh đọc từ `.git/HEAD` của thư mục lệnh; quy tắc đóng an toàn cho `main_merge`: `git merge`/`git pull` không kèm `-C` mà trước đó trong cùng lệnh (kể cả lệnh ghép, subshell, `bash -c` lồng) có BẤT KỲ thao tác đổi thư mục (`cd`, `chdir`, `pushd`, `popd`, `Set-Location`, `sl`, `Push-Location`, `Pop-Location`, `env -C`/`--chdir` và `sudo -D`/`--chdir` mọi dạng kể cả viết dính) thì coi là ở `main` và chặn với lý do `main_merge`; hook không tính đường đi. `git -C <dir>` đọc nhánh của chính `<dir>` (không xác định được, hoặc tương đối sau khi đã đổi thư mục, thì coi là `main`). Cái giá: gộp hợp lệ có `cd` phía trước bị chặn nhầm — chạy `git merge` ở lệnh riêng sau khi đã đứng đúng thư mục (hoặc dùng `git -C <dir>`). `git pull` là gộp: thiếu `+nhánh` thì chặn ở mọi nhánh (`branch_merge_local`). Tiền tố `timeout`, `env`, `sudo`, `nice`, `xargs`… được bỏ cùng đối số. Hook chỉ mở lớp `bash -c`/`pwsh -Command`/`cmd /c` trực tiếp, tối đa 3 lớp (sâu hơn thì chặn); Codex `write_stdin` không được xét; đối thủ cố ý lách được (biến môi trường như `export GIT_DIR=…; git merge`, script, alias git, `python -c`, `env -S'…'` viết dính, tiền tố chưa liệt kê như `doas`, `ionice`, `flock`, `watch`, lệnh ghép tạo liên kết rồi xoá). Ngoại lệ dọn `.tmp/` và phần không chặn được: `method/autopilot.md` mục 5.1. Lưới an toàn, không phải ranh giới bảo mật.
- **Bảo vệ chính file dấu:** khi có file dấu, lệnh shell không chỉ-đọc có đối số trỏ tới nó, tới `.tmp/` bao nó hay glob khớp nó (`rm`, `mv`, `cp`, `Remove-Item`, `Move-Item`, `Rename-Item`, `Set-Content`, `truncate`, `sed -i`, chuyển hướng `>`/`>>`, `tee`…) bị chặn với lý do `autopilot: file dấu là rào — chỉ người dùng hoặc lệnh dừng mới xoá`; lệnh chỉ-đọc (`cat`, `type`, `Get-Content`, `ls`, `test -f`, `grep`, `git status|diff`…) qua. So tên không phân biệt hoa thường; sau thao tác đổi thư mục thì so theo tên. Chỉ file dấu **đang bật** được bảo vệ: chép file dấu sang worktree khác bằng đường tuyệt đối thì qua. Công cụ ghi file (`Write`, `Edit`, `MultiEdit`, `NotebookEdit` của Claude; `apply_patch` của Codex; `write_to_file`, `replace_file_content`, `multi_replace_file_content` của Antigravity) có đường đích là file dấu cũng bị chặn cùng lý do; với Claude, matcher `Write|Edit|MultiEdit|NotebookEdit` đã đăng ký ở `hooks/hooks.json`; với Codex và Antigravity thì chưa.
- **Cụm cờ, nối dòng, eval, ống vào shell:** cụm cờ ngắn kết thúc bằng cờ nhận giá trị (`sudo -Hu deploy`, `env -iu HOME`, `xargs -tI {}`) bỏ cả giá trị; `git \` (hay dấu huyền) + xuống dòng được nối trước khi tách lệnh; `eval …`, `iex`, `Invoke-Expression`, `bash <<< "…"` và `… | bash|sh|pwsh|iex` xét chuỗi như lệnh lồng (có git/gh kèm biến mà không phân tích được thì chặn). `git -C <dir>` và `cd <dir>` từ ngoài repo cũng dò file dấu ở `<dir>`.
- **Launcher `scripts/autopilot-hook.sh`** (POSIX sh, không cần Python): đọc sự kiện ở stdin một lần, rồi gọi thẳng `autopilot_guard.py "$@"` bằng `python3`, `python`, `py -3` theo thứ tự (bỏ qua stub của Microsoft Store; không dò phiên bản bằng tiến trình riêng — guard tự xử khi Python < 3.9). Guard trả 0 hoặc 2 thì trả nguyên mã. Guard vắng, Python không có, hoặc mọi ứng viên trả mã khác (lỗi cú pháp, import hỏng, traceback) thì launcher KHÔNG trả mã đó mà tự dò file dấu (không phân biệt hoa thường) từ `$CLAUDE_PROJECT_DIR` và `$PWD` tới thư mục có `.git`: có thì thoát 2 (lý do `guard lỗi` hay `không chạy được Python`), không thì thoát 0. Nhờ vậy guard bị sửa dở hay máy thiếu Python không chặn mọi lệnh khi autopilot tắt. Đo trên máy này (Windows, Git Bash): trước ~0,57 s mỗi lệnh, sau ~0,28 s (trung vị 12 lần). Guard luôn là `autopilot_guard.py` cạnh chính launcher; không có biến môi trường nào đổi đường tới guard (test dựng thư mục tạm chứa bản chép launcher cùng guard giả).
- **Đường tuyệt đối từ ngoài cây:** sự kiện có `cwd` ngoài cây có file dấu vẫn bị chặn nếu lệnh không chỉ-đọc (hay công cụ ghi file) trỏ bằng đường tuyệt đối hoặc tương đối vào cây đó: hook đi lên từ chính đường đích tới thư mục có `.git` để tìm file dấu. `rm <abs>/.tmp/autopilot.json`, `mv <abs>/.tmp …`, `Write` vào file dấu → chặn như bảo vệ file dấu; `rm -rf <thư mục chứa file dấu>` → chặn theo mục `irreversible_delete` của cây đó; dọn thư mục con của `.tmp/` bằng đường tuyệt đối thì qua, TRỪ khi đích (hay thư mục con của đích, dò `os.walk` sâu tối đa 6 cấp, bỏ `.git`) chứa `.tmp/autopilot.json` lồng bên trong (tên không phân biệt hoa thường; quá giới hạn hay lỗi đọc thì coi như có): lúc đó chạy `--clear` từng thư mục trước rồi mới `rm -rf`. Phép dò file dấu lồng chỉ chạy khi đối số được nhận là đường vào cây có file dấu đang bật hoặc ngoại lệ `.tmp/`: `rm -rf <tên trần>` từ `cwd` bên trong `.tmp/`, `cd .tmp/x && rm -rf y`, glob `.tmp/x*` và thư mục tổ tiên của thư mục có file dấu không được dò — điều phối luôn `--clear` từng thư mục trước khi dọn. `find … -exec`/`-execdir` mà lệnh sau không chỉ-đọc và điểm tìm là `.tmp/` hay thư mục chứa nó → chặn như bảo vệ file dấu. `git stash -u|--include-untracked|-a|--all` → chặn (file dấu bị cất đi). `cp`/`Copy-Item` mà file dấu chỉ là NGUỒN thì qua (điều phối chép vào worktree phiên con); đích là file dấu đang bật hay `mv` thì chặn. Thân heredoc đưa vào trình không phải shell (`python -`, `node -`, `cat >`) là dữ liệu, không phân tích; đưa vào `bash`/`sh`/`pwsh`/`eval` thì vẫn xét như lệnh lồng. Chỉ nhận `<<`/`<<-` nằm ngoài nháy (đơn, kép, kể cả chuỗi nhiều dòng) và ngoài comment `#`; dòng kết thúc phải khớp đúng nhãn, heredoc không có dòng kết thúc thì giữ nguyên thân để phân tích. Nhãn không nháy (`<<X`, `<<-X`) thì shell vẫn mở rộng `$(…)` và dấu huyền trong thân, nên các lệnh đó được trích ra phân tích như lệnh lồng; chỉ nhãn có nháy (`<<'X'`, `<<"X"`, `<<\X`) mới bỏ hẳn thân. Không phân tích chuỗi chương trình tuỳ ý (`awk 'BEGIN{system(…)}'`, `perl -e`, `ruby -e`, `node -e`, `python -c`): giới hạn đã biết. Không bắt được thư mục tổ tiên của cây (xoá cả thư mục cha của repo).
- **Lối dừng tường minh `--clear`:** `python scripts/autopilot_guard.py --clear <thư mục làm việc>` xoá đúng `<thư mục>/.tmp/autopilot.json` (chỉ file đó; in đường đã xoá; không có thì báo và thoát 0, không cần `--format`). Hook nhận ra đúng lệnh này (script của plugin, đúng dạng `--clear <đường>`, không đối số hay chuyển hướng nào khác) và cho qua kể cả khi có file dấu; mọi đường xoá khác (`rm`, `Remove-Item`, `mv`…) vẫn bị chặn. Đây là rào hành vi: phiên con gọi được về mặt máy nhưng luật cấm — chỉ điều phối (sau `Dừng autopilot.` hay thu hồi) hoặc người dùng gọi, và lần gọi hiện trong transcript để soát.
- Gỡ lỗi: `AUTOPILOT_GUARD_DEBUG=1` in traceback ra stderr.

## Mã thoát

| Script | 0 | 1 | 2 |
|---|---|---|---|
| `init.py` | xong (hoặc chạy thử xong) | — | lỗi đầu vào: tham số sai (gồm ký tự điều khiển trong `--title`, `--title` cùng `--title-file`, `--title-file` không đọc được dạng UTF-8), `.agile.json` hỏng hoặc sai hình, đích ghi nằm ngoài gốc dự án và `artifact_root`, sổ thiếu `next_id` |
| `check.py` | Đạt: không có Chặn / Phải sửa (Nên sửa, Ghi chú vẫn in) | Không đạt: có Chặn hoặc Phải sửa | lỗi đầu vào: đường dẫn không có, file không đọc được, frontmatter ngoài tập con, `.agile.json` không phải JSON |
| `index.py` | đã cập nhật hoặc không đổi | `--check` thấy sổ chưa cập nhật | lỗi đầu vào: thiếu hoặc sai hình `.agile.json`, sổ ngoài gốc dự án, thiếu sổ, dấu mốc sai, frontmatter spec sống hỏng, sổ hoặc spec sống không phải UTF-8 |

Mỗi phát hiện của `check` in một dòng `đường-dẫn:dòng: <mức> [<mã luật>] <mô tả>`; dòng cuối là tóm tắt số
file, số phát hiện theo mức và kết luận. `init` và `index` khi ghi lại một file có sẵn giữ nguyên BOM và kiểu
xuống dòng (LF/CRLF) của file đó; file mới ghi UTF-8 không BOM, LF.

## Biến môi trường

| Biến | Dùng bởi | Ý nghĩa |
|---|---|---|
| `AGENT_AGILE_TIERS` | `init.py` | Đường tới bảng tier → model ngoài repo ([`tiers/README.md`](../tiers/README.md) mục 2). Chưa đặt hoặc trỏ file không có → `init --sprint` in cảnh báo ra stderr (mã thoát không đổi), để Analyst xin chỉ định tier trong chat trước khi cần review PLAN |
| `AGENT_AGILE_DENYLIST` | `check.py --self` | Đường tới danh sách từ cấm **ngoài repo** (hợp đồng ở [`tests/README.md`](../tests/README.md)). Thiếu, không đọc được hoặc rỗng → in `WARNING NOT_CONFIGURED` ra stderr, luật `leak-denylist` **Chưa chạy** (không tính là Đạt); mã thoát không vì thế mà đổi |
| `AGENT_AGILE_LEDGER` | `check.py` | Mẫu đường file sổ tập trung của máy, chứa `{project}` (ví dụ `<kho-sổ>/{project}.md`; `~` đầu đường được mở rộng). **Chỉ dự án khai `ledger.project` trong `.agile.json` mới dùng**; không khai thì biến bị bỏ qua. Khai mà chưa đặt → Ghi chú `ledger-unconfigured`; thiếu `{project}` → `config-invalid` |

## Luật của `check`

Mức theo thang chung `method/severity.md`. Luật tài liệu chỉ áp cho file có khoá `doc` hợp lệ; ba luật chung
về mã (`id-bare-single-letter`, `id-unknown-prefix`, `old-scale-label`) áp cho mọi file `.md` được quét. Mã
trong code span, khối code, comment HTML và đích của liên kết không bị xét. Truyền thẳng `.agile.json` thì chỉ
chạy các luật `config-*` cho file đó.

**Routing pilot:** hồ sơ có marker HTML `routing-evidence:v1` phải đặt ngay trước một khối JSON fenced. Mỗi
khối là một record schema 1 theo `evals/task-routing/run.schema.json`; checker kiểm shape, unknown có lý do,
nguồn actual, override độc lập, notice trước dispatch và ba vòng sửa. `--routing-manifest` đối chiếu các
record đã quét với danh sách task/document/classification/assignment/attempt do QA khóa riêng; cùng assignment
phải khớp work item, cấu hình, notice và pin đã duyệt còn hiệu lực. Tổng vòng sửa phải giữ qua handoff khi
root cause, lịch sử assignment và thứ tự thời gian đủ bằng chứng; thiếu những nguồn đó là chưa kiểm được.
Trong cùng assignment, chênh lệch local cycle và tổng phải bằng nhau; `repair_rounds` khi hai đầu đã biết
cũng phải có cùng chênh lệch. Vòng ba thất bại, còn regression hoặc đã handoff giữ trạng thái dừng qua
các observation sau: muốn sửa tiếp phải có assignment receiver mới với lịch sử và tổng được giữ.
Observation/review/lỗi quyền không tiêu thêm vòng có thể giữ nguyên bộ đếm khác 0; không reset lịch sử.
Checker đối chiếu số tự khai, không chứng minh hypothesis, thay đổi và cùng oracle đã thực sự chạy.
Manifest thiếu hoặc source coverage chưa reconcile làm pilot Không đạt. Không có manifest và marker thì hồ sơ cũ giữ cách kiểm
trước đây. Checker chỉ đọc file Markdown được chỉ định và manifest, không mở ref nằm trong record hay ledger.
`effort_source` mô tả quyết định chọn effort, không chứng minh `effort_actual` đã được runtime quan sát. Khi
chưa có telemetry nguồn độc lập, record phải giữ `effort_actual: null` cùng `unknown_reasons` tương ứng;
QA/oracle đối chiếu nguồn này trước khi báo actual effort. Checker hiện chỉ kiểm hình dạng của field đó.

**Code span:** được ngắt qua nhiều dòng trong cùng một đoạn văn, nhưng `check` chỉ nối khi dòng mở và dòng đóng
đều lẻ số dấu huyền (dòng tự cân thì coi dấu huyền lẻ ở dòng trên là chữ thường). Code span **không lồng**: một
lệnh chứa dấu huyền (`git commit -m "…"` nhắc mã, JSON inline, dấu thoát PowerShell) phải bọc ngoài bằng **hai**
dấu huyền. Mã bị bắt có dấu huyền sát bên thì phát hiện kèm gợi ý "code span lồng nhau hoặc ngắt dòng?".

| Mã luật | Mức | Bắt gì |
|---|---|---|
| `frontmatter-syntax` | Chặn | Frontmatter ngoài tập con YAML, kèm dòng — lỗi đầu vào, thoát 2 |
| `frontmatter-missing` | Phải sửa | File tên chuẩn (`SPEC.md`, `PLAN.md`, `PROGRESS.md`, `REPORT.md`, `SPRINT.md`, ba sổ) không có frontmatter |
| `frontmatter-key-missing` | Phải sửa | Thiếu khoá bắt buộc theo loại tài liệu (`templates/README.md` mục 3); file tên chuẩn có frontmatter mà thiếu `doc` |
| `frontmatter-key-unknown` | Ghi chú | Khoá ngoài bảng khoá của hợp đồng |
| `frontmatter-value` | Phải sửa | Giá trị sai miền (`status`, `size`, `risk`, ngày, mã `RQ-`/`FS-`/`SPR-` kể cả độ rộng theo `id_width` của `.agile.json` gần nhất, `id`, `next_id`, `links`, `review_round`) hoặc mâu thuẫn (`risk: high` mà không `large`, `risk_tags` khác rỗng mà không `high`) |
| `doc-unknown` | Ghi chú | Có khoá `doc` nhưng không thuộc loại đã biết — chỉ áp luật chung |
| `heading-missing` | Phải sửa | Thiếu tiêu đề cấp 2 bắt buộc theo loại tài liệu (SPEC cỡ vừa trở lên thiếu "Truy vết" cũng báo); `SPRINT.md` cỡ rất nhỏ (hoặc chưa rõ cỡ) nhận hai phần "Kế hoạch" · "Kết quả" hoặc bốn phần cũ — bốn phần chỉ được suy ra khi có tiêu đề **bắt đầu** bằng SPEC, PLAN hay PROGRESS (sau số thứ tự); cỡ nhỏ trở lên luôn cần bốn phần |
| `sprint-size-mismatch` | Phải sửa | Tài liệu không khớp bậc việc: `SPRINT.md` ở cỡ vừa/lớn (dùng bốn file); hoặc cỡ rất nhỏ mà dựng bốn file SPEC · PLAN · PROGRESS · REPORT (báo một lần cho mỗi thư mục). Thiếu khoá `size` thì do `frontmatter-key-missing` báo, không báo đúp ([`method/sizing.md`](../method/sizing.md)) |
| `conclusion-missing` | Phải sửa | Tài liệu sprint hoặc spec sống thiếu dòng `> **Kết luận:**` trước tiêu đề cấp 2 đầu tiên |
| `id-bare-single-letter` | Phải sửa | Mã một chữ cái + số (`P1`, `D3`) ngoài dấu code; trừ tier `T1`/`T2`/`T3` |
| `id-unknown-prefix` | Phải sửa | Mục được định nghĩa bằng tiền tố hai chữ cái ngoài bảng mã (`YC2`); không áp cho `skills/*/tests/` |
| `id-wrong-doc` | Phải sửa | Mục định nghĩa bằng tiền tố của tài liệu khác (`BR1` trong PLAN) |
| `id-list-lead` | Ghi chú | Bảng có cột đầu "Mã" mà dòng không trống ngay trên (bỏ qua comment) không có chữ in đậm — thiếu câu dẫn "tài liệu + nghĩa của mã" (`templates/README.md` mục 5); khối "Đang mở" do `index` sinh được miễn |
| `xref-missing` | Phải sửa | Một mã được viết ra (ngoài code span, khối code, comment, đích liên kết) nhưng tài liệu **giữ** tiền tố của nó chưa định nghĩa mã ấy. Nơi giữ mã: `US` `FR` `SC` `CQ` ở SPEC; `TK` `RK` `DN` ở PLAN; `BR` ở PROGRESS; `VR` `RF` `LN` `CO` ở REPORT; `SPRINT.md` giữ mọi mã của mình, spec sống giữ mã SPEC, tài liệu khác tìm nơi giữ qua `links`. "Đã định nghĩa" = tiêu đề, mục danh sách in đậm, hoặc hàng bảng (cột đầu "Mã") mở đầu bằng chính mã đó; khoảng `SC1–SC3` được khai triển. Sổ gốc không chịu luật này |
| `xref-unresolved` | Ghi chú | Không tìm được tài liệu sở hữu qua `links` để đối chiếu |
| `task-without-trace` | Phải sửa | Mỗi việc `TK` (định nghĩa bằng tiêu đề hoặc mục danh sách in đậm, không phải hàng bảng) phải có chính dòng định nghĩa nhắc `FR` hoặc `SC`, không thì báo; áp cho PLAN và `SPRINT.md`. Việc con (`TK2.3`) không nhắc được kế thừa nếu có việc cha hoặc tổ tiên gần nhất đã định nghĩa; việc cha đó tự phải qua luật này, việc cấp đỉnh không nhắc thì báo |
| `task-order` | Phải sửa | `Đầu vào:` của `TK` trỏ `TK` số ≥ chính nó — số `TK` phải là thứ tự làm. Đọc mục `**Đầu vào:**` dưới tiêu đề `### TKn` (PLAN, `SPRINT.md`) tới `**Đầu ra:**` hoặc hết mục, bỏ phần từ cụm "chạy cùng được với"; dải `TKa–TKb` tính cả hai đầu; việc con (`TK3.1`) được trỏ việc cha (`TK3`) |
| `task-gap` | Ghi chú | Số `TK` cấp một của các tiêu đề `### TKn` không liền 1…N theo thứ tự xuất hiện (hụt số, đảo thứ tự, số đầu khác 1) |
| `plan-goal-block` | Ghi chú | Mục `## Mục tiêu` của PLAN thiếu một trong ba dòng nhãn của mẫu: `Mục tiêu sprint:` · `Kết quả mong muốn / xong khi:` · `Rủi ro cần chú ý:` |
| `report-sc-without-vr` | Phải sửa | `SC` cấp đỉnh (không có dấu chấm) của SPEC không nằm trên dòng định nghĩa của `VR` nào; `VR` là hàng bảng cột đầu "Mã" mở bằng `VR`, mã trong khoảng `SC1–SC3` tính đủ. SPEC của REPORT tìm qua `links.spec`, `SPRINT.md` tự là SPEC. Không có miễn trừ (`bỏ`, `NOT_APPLICABLE` đều không cứu) và luật chỉ thấy có hàng `VR`, không xét kết quả Đạt |
| `report-fr-without-vr` | Phải sửa | Chỉ chạy cho REPORT, không chạy cho `SPRINT.md`. Mỗi `FR` của SPEC, gộp theo cấp đỉnh (`FR3.2` tính vào `FR3`), phải xuất hiện — hoặc có kịch bản con `FRn.m` xuất hiện — trên dòng định nghĩa của ít nhất một `VR`; vắng ở mọi `VR` thì báo, một lần cho mỗi `FR`. Miễn khi dòng định nghĩa ở SPEC mang trạng thái `bỏ` (dạng "(bỏ)" hoặc "— bỏ" cuối dòng), hoặc có `NOT_APPLICABLE` kèm lý do ở dòng đó hay ở một dòng REPORT nhắc tới `FR` ấy. Máy không xét từng kịch bản con |
| `self-review` | Chặn | Một nhãn agent vừa giữ vai thực thi vừa giữ vai kiểm định trong `roles` (`gate-delegate` là vai kiểm định, so với mọi vai thực thi; `advisor` không phải vai kiểm định, chỉ so với `analyst`/`architect`/`gate-delegate`; trùng `business-reviewer`/`tech-reviewer` là hợp lệ); hoặc `delegation.by` (người duyệt thay) trùng nhãn một vai thực thi trong `roles` cùng file, hoặc nhãn `delegation.by` giữ `advisor` |
| `qa-not-independent` | Phải sửa | Có `VR` mà `qa` trùng nhãn `implementer`/`architect` không ghi "tự kiểm, chưa độc lập"; hoặc có ghi mà `verdict: pass` |
| `roles-invalid` | Phải sửa | `roles` sai hình: vai lạ (khoá vai thực thi gồm `researcher`; vai chuyên đề ngoài bốn chuyên đề `security-specialist`, `data-specialist`, `backend-specialist`, `frontend-specialist` = vai lạ), tier ngoài `T1`–`T3`, thiếu nhãn agent; `gate-delegate` và `advisor` tier khác `T1` |
| `gate-invalid` | Phải sửa | Cổng đã kết luận mà thiếu `*_at`/`*_quote`; `status: approved` khi `gate_1` chưa approved; REPORT `accepted` hoặc SPRINT `done` khi `gate_2` còn pending |
| `gate-delegation-invalid` | Phải sửa | Cổng `gate_N_mode: delegated` đã kết luận mà hồ sơ duyệt thay thiếu hoặc sai: khối `delegation` (tám khoá `grant`, `grant_at`, `scope`, `expires`, `by`, `tier`, `files`, `revoked_at` cùng năm khoá autopilot tuỳ chọn `level`, `program`, `channel`, `orchestrator`, `sessions_cap` — khoá ngoài mười ba khoá đó (kể cả `exclusions`, `mode` của bản cũ) cũng báo; luật autopilot **kích** khi `grant` bắt đầu `Bật autopilot` (không phân biệt hoa thường) hoặc khối có bất kỳ khoá autopilot (lời cấp thường trực mặc định mang `level: gate_1_2`), khi đã kích thì `level` (`gate_1`/`gate_1_2`/`program`) và `expires` bắt buộc và báo lời cấp thiếu mức/hạn, `program` thiếu tên hoặc `expires` không phải ngày, `scope` khác đúng tập cổng của `level` (`gate_1` → `[gate_1]`; `gate_1_2` → cả hai; `program` → cả hai khi `grant` có `cổng 1+2`, ngược lại `[gate_1]`), `channel` ngoài `chat`/`host_comment`, `sessions_cap` không phải số nguyên ≥1 hoặc `null`, `orchestrator` trùng `by`; hai lỗi cùng lúc chỉ báo lỗi đứng trước theo thứ tự đó, rồi mới tới các kiểm bên dưới; hồ sơ chỉ tám khoá cũ không đổi kết quả; khoá lạ cũng báo, kể cả khi cổng còn mở (`SPRINT.md` có khối chung cho hai cổng: một khoá lạ báo một lần, cổng thứ hai không báo lại khoá lạ đã báo); `grant`; `grant_at` không sau thời điểm cổng; `scope` chứa cổng; `expires` là `sprint_end` hoặc ngày chưa qua ngày cổng; `tier` = `T1`; `by` khác rỗng và khác `pending`; ở PLAN, REPORT, `SPRINT.md` (tài liệu có bản ghi duyệt thay) `by` phải giữ vai kiểm định (`business-reviewer`, `tech-reviewer`, `gate-delegate`, hoặc một chuyên đề trong danh sách đã liệt kê: `security-specialist`, `data-specialist`, `backend-specialist`, `frontend-specialist`) tier T1 trong `roles` của chính tài liệu — `roles` vắng, nhãn không có trong `roles`, hoặc vai kiểm định chỉ tier khác T1 đều báo; giữ nhiều vai kiểm định khác tier thì đủ một vai T1; SPEC không đòi (Cổng 1 duyệt thay ghi ở cả SPEC lẫn PLAN); `by` trùng nhãn vai thực thi thì chỉ báo `self-review`; `revoked_at` rỗng hoặc sau cổng (chỉ ghi ngày: trùng hoặc trước ngày cổng thì báo)); `gate_N_quote` không bắt đầu `duyệt thay:`; PLAN, REPORT, `SPRINT.md` thiếu mục `## Bản ghi duyệt thay` hoặc thiếu một trong ba nhãn; `risk_tags` vắng hoặc không phải danh sách chuỗi (dùng `[]` khi không có nhãn); `risk_tags` có `secret`/`auth`; `rules` mà `delegation.files` rỗng; thời điểm không đọc được. Báo lỗi đầu tiên của mỗi cổng. `gate_N_mode` ngoài `human`/`delegated` → `frontmatter-value`. Vắng `gate_N_mode` hoặc `human` → không kiểm hồ sơ, trừ khi `gate_N_quote` bắt đầu `duyệt thay:` hoặc có khối `delegation` mà cổng đã kết luận (lời trình/khối duyệt thay mà `gate_N_mode` không phải `delegated` cũng báo) |
| `old-scale-label` | Phải sửa | Bốn chỗ. (1) Giá trị trong bảng có cột tiêu đề là "Mức…", "Severity" hoặc "Level" mà lại là nhãn của thang cũ (`Critical`, `High`, `BLOCK`, `Minor`…). Nhãn tiếng Việt của thang cũ (`Nhẹ`, `Thấp`, `Cao`, `Trung bình`, `Quan trọng`, `Nghiêm trọng`) chỉ bị xét khi tiêu đề cột đúng là "Độ nghiêm trọng", "Mức", "Mức độ" hoặc "Mức nghiêm trọng"; cột "Mức chắc chắn" hay "Mức rủi ro" đo thứ khác nên được bỏ qua. (2) Chữ sau "Mức:"/"Severity:" trong dòng, gồm nhãn tiếng Việt kiểu cũ. (3) Nhãn kiểu nguồn trong câu: chữ HOA nguyên từ `CRITICAL`/`HIGH`/`MEDIUM`/`LOW`, nhãn trong ngoặc vuông ở đầu dòng (`[HIGH]`, `[WARN]`…; kể cả sau gạch đầu dòng hay dấu `>`). (4) Ngưỡng điểm của nguồn dạng `confidence ≥ 80` (cũng `>=`, `>` kèm số; "confidence: 8/10" hay "= 0.9" là báo cáo điểm, không phải ngưỡng nên không bị báo). Chữ thường ngoài hai chỗ đầu (`high-level`, `low-code`, "mức cao hơn") không bị báo; nhãn trong code span hay khối code cũng không. Miễn: `method/severity.md`; riêng ba chỗ (3)–(4) còn miễn ở file thử của skill (`skills/*/tests/`), nơi chép nguyên văn đầu ra của chủ thể thử |
| `config-syntax` | Chặn | `.agile.json` không phải JSON — lỗi đầu vào, thoát 2 |
| `config-invalid` | Phải sửa | `.agile.json` sai hình (gồm `paths.*` tuyệt đối hoặc chứa `..`, `sprint_dir` dùng placeholder ngoài `{date}`/`{slug}`, `id_width` không phải số nguyên ≥ 1), hoặc ngưỡng coverage khác 80 mà `coverage.reason` rỗng; `init`/`index` dùng chung bộ kiểm này (`_common.config_problems`). Khi `check` báo mã này, các luật `ledger-*` không chạy (cấu hình sai hình nên không đối chiếu sổ tập trung) |
| `config-public-root` | Chặn | `visibility: public` mà `artifact_root` (đường tuyệt đối) nằm trong gốc dự án |
| `ledger-missing-row` | Phải sửa | Chỉ khi dự án khai `ledger.project`: sprint (thư mục khớp `paths.sprint_dir`, hồ sơ `PROGRESS.md` hoặc `SPRINT.md`) có `status` khác `done`/`dropped` mà file sổ tập trung không có dòng mang mã sprint đó. Báo ở dòng `status` của hồ sơ sprint |
| `ledger-stale` | Phải sửa | Dòng sổ lệch hồ sơ: trạng thái khác `status`, ngày không phải `YYYY-MM-DD` hoặc cũ hơn `updated`. So ngày theo ngày — hai lần đổi trong cùng một ngày chỉ bắt được qua trạng thái ([`method/process.md`](../method/process.md) mục 11) |
| `ledger-unreadable` | Phải sửa | Chỉ khi dự án khai: file sổ (theo `AGENT_AGILE_LEDGER` với `{project}` đã thay) không tồn tại, không phải UTF-8, hoặc không có bảng cột đầu "Sprint"; chỉ đọc bảng ấy, nội dung khác của file sổ bị bỏ qua |
| `ledger-unconfigured` | Ghi chú | Dự án khai `ledger.project` mà máy chưa đặt `AGENT_AGILE_LEDGER` — chưa đối chiếu được; không làm đỏ. Dự án không khai khoá thì không có phát hiện nào về sổ, kể cả khi máy đặt biến. Mẫu đường thiếu `{project}` báo `config-invalid` |
| `leak-denylist` | Chặn | `--self`: file của repo (kể cả tên file) chứa từ cấm — mục chữ khớp nguyên từ, mục có ký tự đường dẫn khớp chuỗi con ([`tests/README.md`](../tests/README.md)); báo số thứ tự từ, không in lại từ |
| `root-junk` | Phải sửa | `--self`: file hoặc thư mục ở gốc repo không được theo dõi và không bị ignore (đo bằng `git status --porcelain --ignored=no`; cache đã ignore không tính; không phải repo Git thì bỏ qua) |
| `agents-md-budget` | Phải sửa | `--self`: `AGENTS.md` quá 120 dòng hoặc quá 10 240 byte |
| `delegation-floor-file` | Phải sửa | Khối `delegation` mà `delegation.files` nêu một file thuộc sàn cứng (`FLOOR_FILES`: `FENCE_FILES`, `floor_check.py`, các test ghim, `verify.yml`…): không duyệt thay được. File chỉ chứa **vùng** sàn (`AGENTS.md`, `method/{process,sizing,autopilot}.md`) không bị luật này báo — `floor_check` so vùng đó với base |
| `gate-signer-independence` | Phải sửa | Khối `delegation` mới (`grant_at` từ 2026-11-13) mà `delegation.by` trùng nhãn vai thực thi ở tài liệu khác cùng sprint (trùng trong cùng file do `self-review` báo), hoặc `delegation.tier` thấp hơn tier của một vai thực thi trong sprint. Hồ sơ cũ không bị áp. |
| `gate-route-floor` | Phải sửa | Cổng `gate_N_mode: delegated` (kể cả còn `pending`, không đợi kết luận) mà bảng `## File luật và file sàn cứng sẽ chạm` của PLAN khai file thuộc `FLOOR_FILES` hoặc có vùng sàn (`FLOOR_ZONES`), hoặc `risk_tags` có `rules` mà `delegation.files` rỗng: cổng đi người, trình lời khuyến nghị. Báo một lần mỗi lý do cho mỗi tài liệu |
| `decision-log-missing` | Phải sửa | REPORT có Cổng 2 `delegated` đã kết luận, khối `delegation` có `grant_at` từ 2026-11-13, mà không có mục `## Nhật ký quyết định` chứa ít nhất một dòng bảng đủ cột `Ai ký` (bốn phần nhãn · vai · tier · model cách nhau bằng `·`), `Bằng chứng` và `Lệnh hoàn tác` khác rỗng và khác `—` (`method/autopilot.md` mục 8). Hồ sơ cũ không bị áp; `SPRINT.md` chưa bị kiểm |
| `session-cap-missing` | Phải sửa | PLAN có Cổng 1 `delegated` đã kết luận, khối `delegation` có `grant_at` từ 2026-11-13, mà mục `## Ước lượng` không có dòng `Trần phiên: <số nguyên >= 1>` (`method/autopilot.md` mục 2.1). Hồ sơ cũ không bị áp; không đối chiếu số với `sessions_cap` |
| `frontmatter-duplicate-key` | Phải sửa | Khoá `delegation` lặp ở frontmatter: chỉ phiên điều phối ghi một khối. Thay `frontmatter-syntax` cho đúng trường hợp này; khoá lặp khác vẫn là `frontmatter-syntax` |
| `decision-owner-missing` | Nên sửa | Bảng `CQ`/`DN` (cột đầu `Mã`) của SPEC/PLAN/SPRINT có `created` từ `MODE_OPEN_EFFECTIVE_DATE` mà thiếu cột hoặc ô `Người quyết` (người · cổng · Analyst). Hồ sơ cũ hơn ngày đó không bị báo |
| `report-missing-ask-count` | Nên sửa | REPORT có `created` từ `MODE_OPEN_EFFECTIVE_DATE` mà không có dòng `Số lượt Đức phải trả lời: <số>` (chữ trong chú thích HTML không tính; dòng phải có chữ số). Đếm lượt người phải trả lời, không tính hộp xác nhận của rào máy ([`method/autopilot.md`](../method/autopilot.md) mục 8). Hồ sơ cũ hơn ngày đó và `SPRINT.md` không bị báo |
| `conditional-pass-merged-main` | Phải sửa | `gate_2: conditional_pass` mà REPORT/SPRINT có dòng khai đã gộp `main` (`đã gộp … main` hoặc `nhánh chính`, hay dòng `Commit gộp` kèm mã băm): Đạt có điều kiện thì nhánh vào hàng chờ người, không gộp. Không xét ngày hồ sơ; bắt lỗi sau khi chạy |
| `hard-floor-marker` | Chặn | `--self` (chỉ khi repo có `scripts/floor_check.py`): cặp mốc `<!-- san-cung:start -->`/`end` ở `AGENTS.md`, `method/{process,sizing,autopilot}.md` lệch (mở không đóng, lồng, nằm trong khối mã), mất hoặc thừa so với `FLOOR_ZONES` |
| `routing-invalid` | Phải sửa | Marker routing thiếu khối JSON kế tiếp, JSON sai, record sai schema 1 hoặc thiếu chứng cứ/nguồn độc lập |
| `routing-unknown` | Ghi chú | Record có field ngoài schema routing 1; checker không diễn giải field lạ |
| `routing-manifest-invalid` | Phải sửa | `--routing-manifest` thiếu file, JSON sai, hoặc manifest không có task/ref hợp lệ |
| `routing-missing` | Phải sửa | Manifest pilot có document/classification/assignment/attempt chưa xuất hiện hoặc source coverage chưa đối chiếu |
| `routing-duplicate` | Phải sửa | Record, assignment hoặc attempt trùng trong pilot |

**Phạm vi `--self`:** mọi file Git đang theo dõi **và** file chưa add, trừ file bị `.gitignore` (`git ls-files -c -o
--exclude-standard`); không phải repo Git thì quét cây thư mục. `--self` không nhận đường dẫn (thoát 2); chọn repo
bằng `--root`. Luật tài liệu bỏ
qua `tests/fixtures/` (ca hỏng cố ý). Chống rò quét cả `tests/fixtures/`. Miễn trừ chống rò là **danh sách
tường minh** `LEAK_EXEMPTIONS` trong `check.py` — mỗi mục một đường, một kiểu, một lý do; thêm mục mới phải thêm
dòng vào bảng dưới (`tests/test_check_self.py` kiểm), và miễn trừ chỉ che đúng phần được nêu, phần còn lại của
dòng vẫn bị quét:

| Đường | Kiểu | Che gì | Lý do |
|---|---|---|---|
| `NOTICE` | `file` | cả file | giấy phép buộc giữ nguyên thông báo bản quyền |
| `docs/MIGRATION.md` | `old-skill-id` | code span là mã skill cũ `bộ:tên` / `bộ:*` | hồ sơ lịch sử cố ý nêu tên cũ để tra |
| `skills/*/tests/pressure.md` | `model-line` | dòng có chữ `model` | hồ sơ thử ghi model đã chạy |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json` | `author-field` | dòng của trường `author` / `owner` (cả khối `{…}`) và `repository` / `homepage`; trường khác (`description`, `keywords`…) vẫn bị quét | `author-attribution` |
| `README.md`, `README.vi.md` | `author-section` | mục `## Author` (README.md) / `## Tác giả` (README.vi.md), từ tiêu đề tới tiêu đề kế tiếp | `author-attribution` |
| `LICENSE` | `credit-line` | dòng có `Copyright` hoặc `©` | `author-attribution` |
| `**` (mọi file) | `author-url` | đúng hai URL của tác giả — `AUTHOR_REPO_URL` (repo GitHub) và `AUTHOR_SITE` (trang cá nhân) trong `check.py`; `owner/repo` viết tắt, repo khác cùng tài khoản, tên miền khác cùng tiền tố, email vẫn bị quét | `author-attribution` |

`author-attribution` là ngoại lệ có chủ đích do chủ sản phẩm quyết (02/10/2026): repo ghi công tác giả — tên, trang,
địa chỉ repo — ở đúng các chỗ trên. Tên tác giả ở văn xuôi skill, luật, mẫu, tài liệu khác vẫn là **Chặn**
(`tests/test_check_self.py`: `test_author_attribution_is_narrow`, `test_author_url_mask_is_narrow`). Một file khớp
nhiều dòng của bảng thì áp mọi kiểu khớp.
