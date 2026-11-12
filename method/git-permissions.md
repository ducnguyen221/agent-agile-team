# Quyền git và `gh` ở repo được bảo vệ — rào thường trực

> **Kết luận:** ở repo được bảo vệ, lệnh git và `gh` đưa việc ra ngoài hoặc vào nhánh chính **luôn** bị hỏi hay chặn, **dù
> không bật autopilot**: agent không đẩy, không gộp PR, không tag, không đổi remote, không ghi thẳng lên nhánh chính khi
> Đức chưa nói trong chat. Máy canh bằng `scripts/git_fence.py` (do `scripts/autopilot_guard.py` gọi, đăng ký ở
> `hooks/hooks.json`), không phải bằng lời dặn. File này là **luật**; hợp đồng với mã nằm ở mục 9, phần chưa canh được ở mục 8.

Khác autopilot: [autopilot.md](autopilot.md) chỉ bật khi Đức ra lệnh và chỉ canh khi có file dấu `.tmp/autopilot.json`.
Rào ở đây **thường trực**, tắt bằng cách tắt plugin chứ không bằng lệnh trong chat. File này thuộc tập
`FENCE_FILES` (`scripts/_autopilot_rules.py`): sprint duyệt thay không sửa được nó.

## 1. Repo nào được bảo vệ

Một repo là **được bảo vệ** khi **bất kỳ** dấu hiệu nào đúng:

| # | Dấu hiệu | Ghi chú |
|---|---|---|
| 1 | danh tính repo (thư mục git chung hoặc URL remote chuẩn hoá) có trong danh sách bảo vệ ngoài repo | biến `AGENT_AGILE_PROTECTED_REPOS` trỏ file JSON, mục 2 |
| 2 | có `.agile.json` ở gốc repo, kể cả file hỏng | |
| 3 | `git ls-files --error-unmatch -- :/.agile.json` cho thấy chỉ mục **của worktree hiện tại** còn đường đó | pathspec gốc repo nên đúng cả khi lệnh chạy ở thư mục con; chỉ-đọc |
| 4 | có file dấu autopilot | `.tmp/autopilot.json` |

Không dấu hiệu nào → guard không đụng. Lỗi hay quá giờ khi kiểm dấu hiệu 3 là "không xác định", không mở rộng quyền.
Tổng thời gian mọi lời gọi `git` của một lần guard ≤4 giây (hook Claude có `timeout: 10`); chỉ gọi `git` khi lệnh thuộc nhóm
ở mục 3 và chưa có dấu hiệu 1 hay 2.

## 2. Danh sách bảo vệ và mức `full` / `push-only`

Danh sách là file JSON do **Đức** đặt ngoài repo, đường trong biến môi trường `AGENT_AGILE_PROTECTED_REPOS` (mẫu:
`templates/protected-repos.example.json`; điểm cắm: `hosts/README.md`). Agent không đặt được danh sách, không đặt được mức.

```json
{"repos": [{"git_common_dir": "<realpath thư mục .git chung>", "remote_urls": ["<URL chuẩn hoá>"],
            "protected_branches": ["release"], "level": "full"}]}
```

- Khớp **một trong hai** của `git_common_dir` hoặc `remote_urls`. `protected_branches` chỉ **thêm** vào `main`, `master` và nhánh
  mặc định của remote. `level` tuỳ chọn, mặc định `full`.
- **`full`:** bảng đầy đủ ở mục 4. **`push-only`:** chỉ áp nhóm đẩy, gộp PR, tag, remote, release; **không** chặn `commit` và
  đúng dạng trần `git pull --ff-only` (không remote, nhánh, cờ khác; tuỳ chọn toàn cục chỉ `-C <thư mục>`; và cả chuỗi lệnh **không có phép gán biến môi trường nào** — `A=1 git …`, `export`/`set`/`setx`/`env`, PowerShell `$env:`, ở đoạn lệnh nào cũng tính, hỏi thừa với lệnh gán vô hại là chấp nhận) cục bộ trên nhánh chính, và hạ `cherry-pick`, `reset`, `rebase` từ cấm xuống hỏi — nghĩa là mất rào
  chặn cứng với lệnh viết lại lịch sử cục bộ, còn hỏi từng lần. Mức này dành cho repo mà chủ làm việc thẳng trên `main` (ví dụ kho gốc của một workspace), nơi chặn cứng `commit` sẽ chặn cả việc ghi hồ sơ hằng ngày.
- Biến phải tới được **tiến trình hook**: đặt ở mức Người dùng của hệ điều hành rồi khởi động lại ứng dụng Claude; đặt trong
  profile PowerShell hay một cửa sổ terminal là không đủ. Biến vắng hay file hỏng → dấu hiệu 1 "không xác định", mức mặc
  định `full`, các dấu hiệu khác vẫn áp.

## 3. Nhóm lệnh được nhận dạng

Đẩy (mọi dạng, kể cả `git subtree push`) · `gh pr merge` · `gh release` · `git tag` có tạo/xoá · `git remote set-url|add|remove|rename`
· `git config` ghi khoá `remote.*`, `url.*`, `core.hooksPath` · cờ `--no-verify` · và, khi **nhánh hiện tại** là nhánh được
bảo vệ (`main`, `master`, nhánh mặc định của remote, cộng `protected_branches`): `merge`, `commit`, `pull`, `cherry-pick`,
`reset`, `rebase`. Nhánh hiện tại đọc từ `.git/HEAD` của thư mục mà lệnh git thật sự chạy. Sau một `cd`/`pushd` trong cùng lệnh, hay khi có `GIT_DIR=`,
guard không tính được thư mục thật nên **coi là nhánh được bảo vệ** (đóng an toàn, có thể chặn nhầm một `git commit` ở nhánh phụ): viết `git -C <thư mục> …` thay cho `cd`.

## 4. Bảng quyền

| Lệnh (repo được bảo vệ) | `full` | `push-only` |
|---|---|---|
| `git push` không file dấu | **hỏi** (Claude) · **chặn** (Codex, Antigravity) | như `full` |
| `git push` có file dấu `+đẩy-nhánh` | tự làm **chỉ khi** đúng hợp đồng đích (mục 6); ngoài ra chặn | như `full` |
| `git push` có file dấu, không `+đẩy-nhánh` | chặn | như `full` |
| `git push` ép/xoá/rộng: `-f`, `--force*`, `+refspec`, `--delete`, `--mirror`, `--all`, `--tags` | **cấm** (chặn) | như `full` |
| `git tag` tạo | hỏi (có file dấu: chặn) | như `full` |
| `git tag -d`, `git remote set-url\|add\|remove\|rename`, `git config` ghi `remote.*`/`url.*`/`core.hooksPath`, `--no-verify` | **cấm** | như `full` |
| `git merge` cục bộ vào nhánh được bảo vệ | hỏi | hỏi |
| `git commit`, `git pull` khi đang ở nhánh được bảo vệ | **cấm** | tự làm (`pull` chỉ dạng trần `git pull --ff-only`; dạng khác: hỏi) |
| `git cherry-pick`, `git reset`, `git rebase` khi đang ở nhánh được bảo vệ | **cấm** | hỏi |
| `gh pr merge` | hỏi (có file dấu: cấm) | như `full` |
| `gh release …` | **cấm** | như `full` |
| `git status`, `log`, `diff`, `fetch`, `branch`, `checkout` sang nhánh khác, `commit` trên nhánh không được bảo vệ | tự làm | tự làm |

"Hỏi": Claude trả quyết định hỏi (Đức bấm cho phép trong phiên = lời gật của phiên đó); Codex và Antigravity chưa có tầng
hỏi nên "hỏi" là **chặn**, kèm lý do "Đức tự chạy". Với file dấu autopilot, mọi "hỏi" chặn trừ đẩy đúng hợp đồng đích —
**ngoại lệ (SPR-20):** file dấu `mode: open`, sự kiện đến từ **phiên chính** của Claude (không `agent_id`, không `agent_type`) ở
`permission_mode` `bypassPermissions` (đã đo ở `claude -p`, `baseline-measure.md` mục 5; `auto` chưa đo phiên tương tác nên giữ chặn)
thì "hỏi" **giữ là hỏi**: Đức bấm trong hộp; subagent, Codex, Antigravity, mode chưa đo, file dấu hỏng hay `secure` vẫn chặn.
Trong phiên không có người bấm (`claude -p`, subagent không giao tiếp, tác vụ nền), "hỏi" thành chặn — xem mục 7.

## 5. `gh`: ba nhóm

- **Cho qua (đọc):** `pr view|list|status|checks|diff`, `repo view`, `run list|view|watch`, `issue view|list`, `label list`,
  `auth status`, `gh api` bằng GET.
- **Hỏi, nhóm A:** `pr create|comment|review|checkout|ready`, `issue comment`, `run rerun` (tự làm khi file dấu có hợp đồng
  đích khớp: `+đẩy-nhánh` ở `secure`, chế độ mở).
- **Hỏi, nhóm B (không bao giờ tự làm):** `label create`, `pr edit`, `issue create`.
- **Cấm:** `gh api` có phương thức ghi (`-X`/`--method` khác GET, `-f`, `-F`, `--input`), `release`, mọi lệnh con ngoài danh
  sách — kể cả alias như `gh ship`. `gh pr merge` xem bảng ở mục 4.
- `gh` có `-R`/`--repo` hay đường `repos/<chủ>/<repo>`: áp quyền nếu thư mục làm việc là repo được bảo vệ **hoặc** repo đích
  khớp URL trong danh sách. Đích khác repo của thư mục làm việc mà không khớp danh sách là **giới hạn đã biết** (mục 8).

## 6. Hợp đồng đích khi tự đẩy (`+đẩy-nhánh`)

Cờ `+đẩy-nhánh` đứng cuối lệnh, chỉ đi với `cổng 1+2` ([autopilot.md](autopilot.md) mục 2). Khi file dấu mang cờ, `intake` ghi thêm
bốn khoá (`push_remote`, `push_urls`, `push_targets`, `git_common_dir`) và bỏ `push` khỏi `exclusions`. Guard chỉ cho qua một lệnh
đẩy khi **cả bảy điều** đúng, còn lại chặn (đóng an toàn, kể cả khi lệnh `git` đọc lỗi hay quá giờ):

1. **một** refspec, dạng `<nguồn>:<ref đích>` hay tên nhánh, không `+`;
2. remote **có tên** bằng `push_remote` (không URL trực tiếp, không `git push` trần);
3. **tập URL đẩy hiệu lực** (`git remote get-url --push --all <remote>`) bằng đúng `push_urls`;
4. ref đích bằng đúng một ref trong `push_targets` và không phải nhánh được bảo vệ;
5. `git_common_dir` bằng realpath thư mục git chung hiện tại (worktree của repo khác không đẩy được);
6. nhánh mặc định của remote đọc được (`refs/remotes/<remote>/HEAD`) và khác đích;
7. không có cờ hay biến cấm: `--force*`, `+`, `--mirror`, `--all`, `--tags`, `--delete`, `--no-verify`, `GIT_DIR=`, `-c`,
   `git -C <thư mục khác>`.

Thiếu danh sách hay chỉ có dấu hiệu 2–4, không khớp dấu hiệu 1 → chặn `push-repo-unverified`; đích không có trong
`push_targets` → chặn `push-target-unknown`. Mười tám ca của bảng hợp đồng nằm ở `tests/test_git_fence.py`.

## 7. Host: ai hỏi được, ai chỉ chặn

Kết quả ma trận host đo bằng hook thăm dò (SPR-16 TK6, `evidence/host-matrix.md` trong hồ sơ sprint): hook `PreToolUse` chạy cho
`Bash` và `PowerShell`; quyết định "hỏi" chỉ thành hộp xác nhận ở phiên có người bấm. Ở `claude -p`, ở subagent và ở Codex /
Antigravity "hỏi" là **chặn**. Ô nào chưa chạy được (Codex cần Đức trust hook, phiên tương tác, chế độ bỏ qua quyền) ghi "Chưa
chạy" trong ma trận và, ở host đó, cờ `+đẩy-nhánh` giữ tắt cho tới khi có ô xanh.

## 8. Phần vẫn là rào hành vi — nói thẳng

Rào máy chỉ nhìn thấy **lệnh shell và tool ghi file qua hook đã đăng ký**. Không canh được:

- script hay chương trình gọi git bên trong (`python -c "subprocess…"`, `make`, `npm run`): lớp độc lập thứ hai ở mục 10 canh việc này;
- công cụ MCP và terminal của ứng dụng (ví dụ `mcp__ccd_pr__merge`, `mcp__terminal__run_in_terminal`) chừng nào ma trận chưa
  cho thấy hook áp được cho chúng;
- `gh` nhắm repo khác repo của thư mục làm việc mà không khớp danh sách bảo vệ;
- sửa chính `.github/workflows/verify.yml` trước khi SPR-17 nghiệm thu workflow-từ-base (bước `Floor vs base` là rào hành vi có kiểm);
- alias git: alias trong file config **của repo** được khai triển (tối đa 3 lớp; alias `!lệnh-shell` bị chặn là không phân tích được) và ghi khoá `alias.*` bị cấm;
  alias ở cấu hình toàn cục của người dùng thì guard không đọc (file đó nằm trong vùng không đọc), nên một lệnh con lạ có thể là alias đẩy mà guard không thấy;
- biến môi trường `GIT_*` trong lệnh (`GIT_CONFIG_COUNT`/`GIT_CONFIG_PARAMETERS`, `GIT_SSH_COMMAND`, `GIT_CONFIG_GLOBAL`…) làm hợp đồng đích không áp (`push-repo-unverified`) vì chúng đổi hành vi của `git` mà guard không thấy; `-c` trên dòng lệnh đặt khoá `remote.*`/`url.*`/`alias.*`/`include*`/`core.hooksPath` bị cấm;
- file `.agile.json` và file danh sách: tên viết đúng, glob khớp tên (`.agil*`, `*.json` ở gốc repo), biến chứa tên biến danh sách, hay đích chuyển hướng bị chặn; chuỗi có `$`/dấu huyền chỉ bị chặn khi cả lệnh nhắc tới `.agile` hay biến danh sách (không giải được biến);
- repo có `[include]` trong config: lệnh con lạ (không phải lệnh có sẵn của git) coi là alias trong file được nạp thêm, không đọc được nên bị chặn;
- nhánh dự phòng của launcher (Python hay guard lỗi) chỉ dò file dấu, `.agile.json` ở gốc và chỉ mục còn `.agile.json`; **không** đọc danh sách bảo vệ (dấu hiệu 1) nên mất mức bảo vệ đó khi Python lỗi;
- **che giấu cú pháp:** guard là bộ đọc chuỗi lệnh, không phải trình thông dịch shell. Nó nhận lệnh viết thẳng và các dạng che giấu phổ biến đã có test (nháy, `\`, `$'…'`, brace, glob, biến, `env`/`export`, `bash -c`, `eval`, alias của repo, chuyển hướng không tên lệnh, pathspec `:(…)`), nhưng một agent cố ý che giấu bằng cách ghép chuỗi (PowerShell `'GI'+'T_…'`, mã hoá, `printf` rồi `eval`…) thì chỉ còn lớp (b) ở mục 10 chặn được; mỗi vòng kiểm định bảo mật vẫn tìm thêm được dạng mới thuộc lớp này nên nó **không bao giờ được gọi là rào máy kín**;
- script, `xargs rm`, `python -c "open('.agile.json','w')"`, `mv . ../x` và mọi cách ghi file không qua lệnh được nhận dạng: không canh được (chỉ lớp (b) ở mục 10 và việc đối chiếu ở Cổng 2);
- `git` báo `dubious ownership` ở nhánh dự phòng của launcher thì dấu hiệu 3 bị bỏ qua (fail-open ở đúng nhánh dự phòng);
- nhãn `floor-approved` của PR không gắn với SHA của head: commit đẩy thêm sau khi gắn nhãn vẫn chạy `--mode report`;
- miễn `git pull --ff-only` ở `push-only` còn một lối: khoá cấu hình `branch.*`/`pull.*` đã nằm sẵn trong config của repo hay config toàn cục (không đặt qua lệnh) có thể đổi nhánh theo dõi mà rào không đọc; `protected_config_key` chưa chặn các khoá này. Việc hoãn (CO), không phải Đạt;
- repo **không có dấu hiệu nào**: guard không đụng — giới hạn đã biết, không phải Đạt;
- mất dấu hiệu: `.agile.json` bị xoá nhưng danh sách (dấu hiệu 1) hay chỉ mục (dấu hiệu 3) còn thì vẫn được bảo vệ; lệnh hay tool ghi
  nhắm `.agile.json`, chỉ mục cho đường đó (`git rm`, `git mv`, `git update-index`) hay file danh sách bị chặn dù không có file dấu.

## 9. Ánh xạ về mã

| Mục luật | Hàm / file |
|---|---|
| mục 1 (bốn dấu hiệu) | `git_fence.protection()` → `Signals` |
| mục 3–5 (nhận dạng, bảng quyền, `gh`) | `git_fence.classify()` → `Verdict(none\|auto\|ask\|forbid)` |
| mục 6 (hợp đồng đích) | `git_fence.push_contract()` ; bốn khoá đọc bằng `autopilot_guard.load_push_contract()` |
| mục 2 (danh sách) | `git_fence` đọc `AGENT_AGILE_PROTECTED_REPOS` |
| điểm vào | `autopilot_guard._decide()` chạy rào autopilot (`_evaluate`) rồi gọi `_fence_decision()` → `git_fence` cho **mọi** sự kiện (tool ghi file, không file dấu, đầu vào hỏng, lỗi nội bộ trong repo có dấu hiệu 1/2/4 đều đóng); `_ask` in định dạng hỏi cho Claude |

## 10. Lớp độc lập thứ hai

Guard là lớp (a). Lớp (b) không đi qua agent và không phụ thuộc hook: **ruleset GitHub** trên nhánh chính (nơi gói GitHub cho
phép) hoặc **`pre-push` cục bộ** (`templates/git-hooks/pre-push`). Đức tự đặt ruleset và tự cài `pre-push` vào từng repo thật;
agent chỉ soạn mẫu và hướng dẫn. Hướng dẫn từng bước ở mục 11; mẫu `pre-push` và bài thử bằng remote trần ở `tests/test_git_server_layer.py`.

## 11. Đặt ruleset GitHub — việc của người dùng, từng repo

Agent **không** đặt ruleset, không dùng token quản trị. Các bước (giao diện GitHub, quyền quản trị repo):

1. **Settings → Rules → Rulesets → New ruleset → New branch ruleset.** Tên dễ nhận (ví dụ `protect-main`); **Enforcement status: Active**.
2. **Target branches:** thêm nhánh mặc định và mọi nhánh trong `protected_branches` của danh sách bảo vệ (mục 2), ví dụ `main`, `release/*`.
3. Bật các quy tắc: **Restrict deletions** · **Block force pushes** · **Require a pull request before merging** (số người duyệt theo repo) ·
   **Require status checks to pass** và thêm check của workflow `verify` (tên job dạng `<hệ điều hành> · Python <phiên bản>`, chọn từ danh sách sau lần chạy đầu) ·
   khuyến nghị **Require branches to be up to date before merging**.
4. **Bypass list: để trống.** Không thêm tài khoản người đang làm việc hằng ngày, không thêm GitHub App hay token của agent — đúng chỗ đó là lỗ hổng.
5. **Kiểm:** từ một bản sao, `git push origin HEAD:main` phải bị từ chối với thông báo ruleset; đẩy một nhánh sprint rồi mở PR phải được. Ghi kết quả vào REPORT của sprint chạm repo đó.

Nếu gói GitHub của repo **không có** ruleset (repo riêng tư trên gói miễn phí): dùng `templates/git-hooks/pre-push` làm lớp cục bộ, chấp nhận rằng `git push --no-verify` bỏ qua nó (bài thử
`test_server_layer_still_blocks_when_pre_push_is_bypassed` chỉ chứng minh được khi có hook `pre-receive` ở máy chủ), và ghi vào REPORT rằng lớp (b) chỉ là rào hành vi cho repo đó. Phần GitHub thật
(ruleset, `pre-receive` thật) chưa được chạy trong SPR-16: bàn giao cho người dùng.
