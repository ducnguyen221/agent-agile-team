# scripts/

Ba công cụ cho dự án áp dụng, chỉ dùng thư viện chuẩn Python (3.9+), chạy được trên Windows và macOS. Hợp
đồng đầy đủ (tập con YAML, khoá, tiêu đề, sổ gốc, cấu hình) ở [`templates/README.md`](../templates/README.md).

| Script | Việc |
|---|---|
| `init.py` | Dựng `.agile.json`, ba sổ gốc và khung sprint từ `templates/`; mặc định chạy thử, không ghi đè |
| `check.py` | Kiểm chuẩn tài liệu; `--self` kiểm lõi sạch và ngân sách `AGENTS.md` của chính repo |
| `index.py` | Sinh lại khối "Đang mở" ở đầu ba sổ gốc |
| `_common.py` | Thư viện chung: đọc frontmatter tập con YAML, che mã trong Markdown, đọc `.agile.json`; không chạy trực tiếp |

## Cách chạy

```text
python scripts/init.py <gốc-dự-án>                     # chạy thử: in "+ tạo / ~ sửa / = giữ", không ghi
python scripts/init.py <gốc-dự-án> --apply             # ghi .agile.json + REQUESTS, SPRINTS, SPECS
python scripts/init.py <gốc-dự-án> --apply --sprint <slug> (--title "<mục tiêu>" | --title-file <file>) [--tiny]
       [--size tiny|small|medium|large] [--risk normal|high] [--risk-tags a,b] [--request RQ-NNN] [--feature FS-NNN]
       [--date YYYY-MM-DD]
python scripts/check.py <file.md|.agile.json|thư-mục> [...]   # thư mục: quét đệ quy *.md và mọi .agile.json
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
| `report-sc-without-vr` | Phải sửa | `SC` cấp đỉnh (không có dấu chấm) của SPEC không nằm trên dòng định nghĩa của `VR` nào; `VR` là hàng bảng cột đầu "Mã" mở bằng `VR`, mã trong khoảng `SC1–SC3` tính đủ. SPEC của REPORT tìm qua `links.spec`, `SPRINT.md` tự là SPEC. Không có miễn trừ (`bỏ`, `NOT_APPLICABLE` đều không cứu) và luật chỉ thấy có hàng `VR`, không xét kết quả Đạt |
| `report-fr-without-vr` | Phải sửa | Chỉ chạy cho REPORT, không chạy cho `SPRINT.md`. Mỗi `FR` của SPEC, gộp theo cấp đỉnh (`FR3.2` tính vào `FR3`), phải xuất hiện — hoặc có kịch bản con `FRn.m` xuất hiện — trên dòng định nghĩa của ít nhất một `VR`; vắng ở mọi `VR` thì báo, một lần cho mỗi `FR`. Miễn khi dòng định nghĩa ở SPEC mang trạng thái `bỏ` (dạng "(bỏ)" hoặc "— bỏ" cuối dòng), hoặc có `NOT_APPLICABLE` kèm lý do ở dòng đó hay ở một dòng REPORT nhắc tới `FR` ấy. Máy không xét từng kịch bản con |
| `self-review` | Chặn | Một nhãn agent vừa giữ vai thực thi vừa giữ vai kiểm định trong `roles` |
| `qa-not-independent` | Phải sửa | Có `VR` mà `qa` trùng nhãn `implementer`/`architect` không ghi "tự kiểm, chưa độc lập"; hoặc có ghi mà `verdict: pass` |
| `roles-invalid` | Phải sửa | `roles` sai hình: vai lạ, tier ngoài `T1`–`T3`, thiếu nhãn agent |
| `gate-invalid` | Phải sửa | Cổng đã kết luận mà thiếu `*_at`/`*_quote`; `status: approved` khi `gate_1` chưa approved; REPORT `accepted` hoặc SPRINT `done` khi `gate_2` còn pending |
| `old-scale-label` | Phải sửa | Bốn chỗ. (1) Giá trị trong bảng có cột tiêu đề là "Mức…", "Severity" hoặc "Level" mà lại là nhãn của thang cũ (`Critical`, `High`, `BLOCK`, `Minor`…). Nhãn tiếng Việt của thang cũ (`Nhẹ`, `Thấp`, `Cao`, `Trung bình`, `Quan trọng`, `Nghiêm trọng`) chỉ bị xét khi tiêu đề cột đúng là "Độ nghiêm trọng", "Mức", "Mức độ" hoặc "Mức nghiêm trọng"; cột "Mức chắc chắn" hay "Mức rủi ro" đo thứ khác nên được bỏ qua. (2) Chữ sau "Mức:"/"Severity:" trong dòng, gồm nhãn tiếng Việt kiểu cũ. (3) Nhãn kiểu nguồn trong câu: chữ HOA nguyên từ `CRITICAL`/`HIGH`/`MEDIUM`/`LOW`, nhãn trong ngoặc vuông ở đầu dòng (`[HIGH]`, `[WARN]`…; kể cả sau gạch đầu dòng hay dấu `>`). (4) Ngưỡng điểm của nguồn dạng `confidence ≥ 80` (cũng `>=`, `>` kèm số; "confidence: 8/10" hay "= 0.9" là báo cáo điểm, không phải ngưỡng nên không bị báo). Chữ thường ngoài hai chỗ đầu (`high-level`, `low-code`, "mức cao hơn") không bị báo; nhãn trong code span hay khối code cũng không. Miễn: `method/severity.md`; riêng ba chỗ (3)–(4) còn miễn ở file thử của skill (`skills/*/tests/`), nơi chép nguyên văn đầu ra của chủ thể thử |
| `config-syntax` | Chặn | `.agile.json` không phải JSON — lỗi đầu vào, thoát 2 |
| `config-invalid` | Phải sửa | `.agile.json` sai hình (gồm `paths.*` tuyệt đối hoặc chứa `..`, `sprint_dir` dùng placeholder ngoài `{date}`/`{slug}`, `id_width` không phải số nguyên ≥ 1), hoặc ngưỡng coverage khác 80 mà `coverage.reason` rỗng; `init`/`index` dùng chung bộ kiểm này (`_common.config_problems`). Khi `check` báo mã này, các luật `ledger-*` không chạy (cấu hình sai hình nên không đối chiếu sổ tập trung) |
| `config-public-root` | Chặn | `visibility: public` mà `artifact_root` (đường tuyệt đối) nằm trong gốc dự án |
| `ledger-missing-row` | Phải sửa | Chỉ khi dự án khai `ledger.project`: sprint (thư mục khớp `paths.sprint_dir`, hồ sơ `PROGRESS.md` hoặc `SPRINT.md`) có `status` khác `done`/`dropped` mà file sổ tập trung không có dòng mang mã sprint đó. Báo ở dòng `status` của hồ sơ sprint |
| `ledger-stale` | Phải sửa | Dòng sổ lệch hồ sơ: trạng thái khác `status`, ngày không phải `YYYY-MM-DD` hoặc cũ hơn `updated`. So ngày theo ngày — hai lần đổi trong cùng một ngày chỉ bắt được qua trạng thái ([`method/process.md`](../method/process.md) mục 11) |
| `ledger-unreadable` | Phải sửa | Chỉ khi dự án khai: file sổ (theo `AGENT_AGILE_LEDGER` với `{project}` đã thay) không tồn tại, không phải UTF-8, hoặc không có bảng cột đầu "Sprint"; chỉ đọc bảng ấy, nội dung khác của file sổ bị bỏ qua |
| `ledger-unconfigured` | Ghi chú | Dự án khai `ledger.project` mà máy chưa đặt `AGENT_AGILE_LEDGER` — chưa đối chiếu được; không làm đỏ. Dự án không khai khoá thì không có phát hiện nào về sổ, kể cả khi máy đặt biến. Mẫu đường thiếu `{project}` báo `config-invalid` |
| `leak-denylist` | Chặn | `--self`: file của repo (kể cả tên file) chứa từ cấm — mục chữ khớp nguyên từ, mục có ký tự đường dẫn khớp chuỗi con ([`tests/README.md`](../tests/README.md)); báo số thứ tự từ, không in lại từ |
| `agents-md-budget` | Phải sửa | `--self`: `AGENTS.md` quá 120 dòng hoặc quá 10 240 byte |
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
| `THIRD_PARTY.md` | `credit-line` | dòng có `Copyright` hoặc `©` | dòng ghi công theo giấy phép nguồn |
| `UPSTREAM.md` | `upstream-ref` | code span là SHA hex, hoặc `owner/repo` với owner thuộc danh sách nguồn công khai `UPSTREAM_OWNERS` trong `check.py` (owner lạ vẫn bị quét; thêm nguồn mới thì thêm owner) | dấu vết nguồn gốc bắt buộc |
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
