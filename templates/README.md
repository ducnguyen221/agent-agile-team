# templates/

Mẫu tài liệu cho dự án áp dụng: bốn tài liệu sprint, bản gộp cho việc rất nhỏ, ba sổ gốc, spec sống của
tính năng và cấu hình dự án. File này là **hợp đồng** giữa mẫu và ba công cụ `init` · `check` · `index`:
khoá frontmatter, giá trị cho phép, tiêu đề bắt buộc, khuôn sổ gốc và tập con YAML mà `scripts/_common.py`
đọc được. Đổi mẫu thì đổi file này cùng lượt.

## 1. Danh sách mẫu

| Mẫu | Ra file nào trong dự án | Dùng khi |
|---|---|---|
| `sprint/SPEC.md` | `<thư mục sprint>/SPEC.md` | Mọi sprint từ cỡ nhỏ trở lên — làm cái gì |
| `sprint/PLAN.md` | `<thư mục sprint>/PLAN.md` | Như trên — làm thế nào |
| `sprint/PROGRESS.md` | `<thư mục sprint>/PROGRESS.md` | Như trên — đang ở đâu, vướng gì |
| `sprint/REPORT.md` | `<thư mục sprint>/REPORT.md` | Như trên — kết quả, bàn giao |
| `sprint/SPRINT.md` | `<thư mục sprint>/SPRINT.md` | Chỉ cỡ rất nhỏ: bốn phần gộp một file |
| `registry/REQUESTS.md` | `paths.requests` | Sổ yêu cầu theo timeline |
| `registry/SPECS.md` | `paths.specs` | Mục lục tính năng |
| `registry/feature-spec.md` | `<paths.feature_specs_dir>/<slug>.md` | Spec sống của một tính năng |
| `registry/SPRINTS.md` | `paths.sprints` | Sổ sprint theo timeline |
| `project/agile.json` | `.agile.json` ở gốc dự án | Cấu hình đường dẫn, coverage, chế độ hiển thị |

**Giá trị trong mẫu là ví dụ hợp lệ**, không phải chỗ trống kiểu `<...>`: nhờ vậy `check` chạy được trên
chính thư mục `templates/`. Phần thân ví dụ là để người viết thay. Dòng ví dụ của sổ gốc nằm trong comment
HTML nên `init` chép sang là sổ rỗng.

Khi tạo file thật, `init` ghi lại frontmatter như sau (khoá không có trong mẫu thì không thêm):

| Tạo gì | Khoá được ghi |
|---|---|
| Sổ gốc | `next_id` = mã đầu tiên theo `id_width`, `updated` = ngày chạy |
| Sprint mới (4 file, hoặc `SPRINT.md` khi `--tiny`) | `id` = `<sprint>-<doc>`, `sprint` = `next_id` của SPRINTS, `request`/`feature` theo tham số (không có thì `null`), `title`, `created`, `updated`; **đặt lại trạng thái**: `status` = `drafting` (PROGRESS, SPRINT) hoặc `draft` (SPEC, PLAN, REPORT), `review_round: 0`, `gate_1`/`verdict`/`gate_2` = `pending`, `*_at`/`*_quote` = `null`, mọi vai trong `roles` = `[tier, pending]`; `size`/`risk`/`risk_tags` theo tham số (mặc định `medium`/`normal`/`[]`, `--tiny` → `tiny`) |
| SPRINTS khi tạo sprint | thêm một dòng Timeline ở đầu bảng (Mã, Mở = ngày chạy, Mục tiêu = `title`; Đóng và Kết luận để trống) và tăng `next_id` |

Tiêu đề cấp 1 thay cụm "Tên mục tiêu sprint" bằng `title`. Chạy lại cùng `slug` không đổi gì.

Chỉ dẫn viết nằm trong comment HTML `<!-- ... -->` ngay dưới mỗi tiêu đề; người viết được xoá sau khi viết.

## 2. Tập con YAML của frontmatter

Frontmatter là khối giữa dòng `---` **đầu tiên của file** và dòng `---` kế tiếp. Chỉ dùng tập con sau;
ngoài tập con là lỗi đầu vào, `check` báo `đường-dẫn:dòng` và không đoán.

| Thành phần | Dạng | Ví dụ |
|---|---|---|
| Dòng trống | bỏ qua | |
| Comment cả dòng | `#` sau khoảng trắng tuỳ ý | `# ghi chú` |
| Comment cuối dòng | ` #` (có khoảng trắng trước) ngoài dấu nháy kép; bị bỏ | `sprint: null  # chưa có sổ` |
| Cặp khoá–giá trị | `khoá: giá trị`, bắt đầu ở cột 0 | `size: medium` |
| Khoá | `[a-z][a-z0-9_-]*` — khoá gốc dùng `snake_case`, khoá vai dùng `kebab-case`; không trùng trong cùng cấp | `gate_1`, `business-reviewer` |
| Khối lồng một cấp | khoá có giá trị rỗng; các dòng con thụt **đúng 2 dấu cách**, mỗi dòng là một cặp khoá–giá trị | `roles:` rồi `  analyst: [T1, agent-a]` |
| `null` | chữ `null`; khoá rỗng **không có dòng con** cũng là `null` | `gate_1_at: null`, `feature:` |
| Bool | `true` / `false` | |
| Số nguyên | `-?[0-9]+` | `review_round: 0` |
| Chuỗi trần | phần sau `: `, cắt khoảng trắng hai đầu; không bắt đầu bằng `[` `"` `'` `{` `>` `&` `*` `!` `%` `@`, dấu sổ đứng hay dấu huyền, không bắt đầu bằng `- ` | `status: in_progress` |
| Chuỗi nháy kép | `"..."`, chỉ có hai escape `\"` và `\\`; dùng khi chuỗi chứa ` #`, `: `, `,` hoặc bắt đầu bằng ký tự bị cấm | `gate_1_quote: "duyệt, làm tiếp"` |
| Danh sách inline | `[a, b]`; phần tử là chuỗi trần (không chứa `,` `[` `]`), chuỗi nháy kép, số, bool hoặc `null`; `[]` là rỗng | `risk_tags: [secret, auth]` |
| Ngày, giờ | đọc là **chuỗi**, không đổi kiểu | `created: 2026-01-15` |

**Không hỗ trợ** (báo lỗi đầu vào): danh sách dạng khối `- mục`, chuỗi nhiều dòng `|` `>`, nháy đơn, map
inline `{}`, anchor/alias/tag, lồng sâu hơn một cấp, ký tự tab, nhiều tài liệu trong một khối.

> `FR3.1` (frontmatter chung) mô tả `roles` có bốn trường `role`, `tier`, `agent`, `note`. Tập con này viết
> chúng thành map một cấp: khoá = vai, giá trị = `[tier, agent]` hoặc `[tier, agent, "note"]`. Tài liệu viết
> `roles` dạng danh sách khối là ngoài tập con.

## 3. Khoá frontmatter

Giá trị là token tiếng Anh cho máy đọc; thân tài liệu dùng nhãn tiếng Việt tương ứng.

`check` áp luật tài liệu theo khoá `doc` **có mặt và thuộc bảng dưới**. File `.md` có frontmatter mà không có
`doc` (thẻ vai, skill, phương pháp) chỉ chịu luật chung về mã; `doc` có mà lạ → Ghi chú. Khoá ngoài bảng này
→ mức **Ghi chú**, không phải lỗi. Thiếu khoá bắt buộc của loại tài liệu → Phải sửa.

| Khoá | Có ở | Giá trị |
|---|---|---|
| `id` | mọi file | sprint: `<sprint>-<doc>` (`SPR-01-spec`); spec sống: `FS-NNN`; sổ gốc: `REQUESTS` · `SPECS` · `SPRINTS` |
| `doc` | mọi file | `spec` · `plan` · `progress` · `report` · `sprint` (gộp) · `feature` · `requests` · `specs` · `sprints` |
| `title` | mọi file | chuỗi tự do |
| `sprint` | tài liệu sprint | `SPR-NN` |
| `request` | tài liệu sprint | `RQ-NNN`, hoặc danh sách inline khi sprint phục vụ nhiều yêu cầu |
| `feature` | tài liệu sprint | `FS-NNN`, danh sách inline, hoặc `null` |
| `status` | mọi file trừ sổ gốc | xem bảng trạng thái dưới |
| `size` | tài liệu sprint | `tiny` (rất nhỏ) · `small` (nhỏ) · `medium` (vừa) · `large` (lớn) |
| `risk` | tài liệu sprint | `normal` · `high` — `high` buộc `size: large` |
| `risk_tags` | tài liệu sprint | danh sách con của `secret`, `auth`, `external_input`, `public_api`, `infra`, `data_migration`, `rules`; khác rỗng buộc `risk: high` |
| `roles` | tài liệu sprint | khối lồng; khoá vai → `[tier, agent]` hoặc `[tier, agent, "note"]` (mục 3.1) |
| `gate_1` · `gate_1_at` · `gate_1_quote` | SPEC, PLAN, SPRINT | `pending` · `approved` · `changes_requested`; thời điểm và câu duyệt nguyên văn, chưa có thì `null` |
| `verdict` | REPORT, SPRINT | kết luận vòng kiểm định cuối: `pending` · `pass` (Đạt) · `conditional_pass` (Đạt có điều kiện) · `fail` (Không đạt) |
| `gate_2` · `gate_2_at` · `gate_2_quote` | REPORT, SPRINT | kết luận của chủ sản phẩm, cùng bộ giá trị với `verdict`; thời điểm, câu nguyên văn |
| `review_round` | PROGRESS, REPORT, SPRINT | số nguyên ≥ 0 — vòng kiểm định hiện tại |
| `requests` · `sprints` | spec sống | danh sách inline `RQ-NNN` / `SPR-NN` đã chạm tính năng |
| `next_id` | sổ gốc | mã kế tiếp sẽ cấp: `RQ-NNN` · `FS-NNN` · `SPR-NN` |
| `created` · `updated` | mọi file (sổ gốc: chỉ `updated`) | `YYYY-MM-DD` |
| `links` | SPEC, PLAN, PROGRESS, REPORT | khối lồng; khoá `spec` · `plan` · `progress` · `report` → đường dẫn tương đối |

**Trạng thái (`status`):**

| Tài liệu | Giá trị |
|---|---|
| SPEC, PLAN | `draft` (nháp) · `in_review` (đang review) · `approved` (đã qua Cổng 1) · `superseded` (bị thay) |
| PROGRESS, SPRINT — trạng thái sống của cả sprint | `drafting` (viết SPEC/PLAN) · `awaiting_gate_1` · `in_progress` (thực thi) · `verifying` (kiểm định) · `blocked` (có `BR` đang mở) · `awaiting_gate_2` · `done` · `dropped` |
| REPORT | `draft` · `submitted` (đã trình Cổng 2) · `accepted` (Cổng 2 đã kết luận) |
| spec sống | `proposed` (đề xuất) · `in_progress` (đang làm) · `live` (đang chạy) · `deprecated` (ngừng) · `dropped` (bỏ) |

### 3.1. Khoá vai và luật "người làm không tự chấm"

- Vai thực thi: `analyst`, `architect`, `implementer`, `qa`. Vai kiểm định: `business-reviewer`,
  `tech-reviewer` và chuyên đề `<tên>-specialist` (`security-specialist`, `data-specialist`,
  `backend-specialist`, `frontend-specialist`).
- `tier` là `T1` · `T2` · `T3`. `agent` là **nhãn phiên hoặc subagent** (`agent-a`), không phải tên model —
  hai phiên của cùng một model là hai agent khác nhau. Chưa giao thì `pending`. Model thực tế ghi ở cột
  "Vai · tier · model" của PROGRESS.
- Luật `check` dựa vào: trong một file, không nhãn `agent` nào (trừ `pending`) vừa giữ vai thực thi vừa giữ
  vai kiểm định (mức Chặn). Một agent được giữ nhiều vai thực thi.
- **Độc lập kiểm định:** file có `VR` (REPORT, SPRINT) thì nhãn `qa` phải khác nhãn `implementer` và
  `architect`. Trùng nhãn → Phải sửa, trừ khi dòng `VR` ghi rõ "tự kiểm, chưa độc lập"; khi đó `verdict`
  tối đa `conditional_pass`.
- Phần tử thứ ba `"note"` ghi lý do khi chủ sản phẩm chỉ định model khác tier mặc định cho lượt đó.

## 4. Tiêu đề bắt buộc

`check` so tiêu đề cấp 2 (`## `) theo kiểu **chứa cụm**, không phân biệt hoa thường, bỏ qua số thứ tự đầu
dòng (`## 3. Rủi ro` khớp "Rủi ro"). Thứ tự không bị kiểm. Tài liệu sprint và spec sống còn phải có khối
trích bắt đầu bằng `> **Kết luận:**` trước tiêu đề cấp 2 đầu tiên.

| Tài liệu | Cụm tiêu đề cấp 2 bắt buộc |
|---|---|
| SPEC | Bối cảnh · Câu chuyện người dùng · Yêu cầu chức năng · Tiêu chí thành công · Ngoài phạm vi · Câu hỏi cần làm rõ (Truy vết: Nên có từ cỡ vừa; Đổi hợp đồng / giao diện: bắt buộc khi cỡ lớn hoặc `risk_tags` có `public_api`, cỡ khác xoá mục — `check` chưa kiểm) |
| PLAN | Mục tiêu · Kiến trúc · Ràng buộc chung · Trọng tâm review · Việc · Rủi ro · Quyết định cần người · Ước lượng |
| PROGRESS | Bảng trạng thái việc · Nhật ký · Vướng mắc · Vòng kiểm định hiện tại |
| REPORT | Tóm tắt cho người không chuyên · Kết quả kiểm định · Phát hiện của reviewer · Rủi ro còn lại · Cách dùng, đã đổi gì, cách hoàn tác · Bài học · Việc để lại · Review & Retro · Cổng 2 (tiểu mục `### Review PLAN trước Cổng 1` dưới "Phát hiện của reviewer": nơi chuẩn của `RF` review PLAN, nên có từ cỡ vừa — `check` không bắt buộc) |
| SPRINT (gộp) | SPEC · PLAN · PROGRESS · REPORT |
| spec sống | Hành vi hiện hành · Tiêu chí đang giữ · Giới hạn đã biết · Quyết định liên quan · Lịch sử sprint |
| REQUESTS, SPRINTS | Đang mở · Timeline |
| SPECS | Đang mở · Danh mục |

Mục không có nội dung vẫn giữ tiêu đề và ghi "Không có." — không xoá tiêu đề.

## 5. Mã và nhãn trong thân

- Mã mục theo tài liệu sở hữu: SPEC `US` `FR` (`FR1.2` là kịch bản) `SC` `CQ` · PLAN `TK` (`TK1.1` là việc
  con) `RK` `DN` · PROGRESS `BR` · REPORT `VR` `RF` `LN` `CO`. Hồ sơ sổ gốc có gạch nối: `RQ-` ≥ 3 chữ số,
  `FS-` ≥ 3 chữ số, `SPR-` ≥ 2 chữ số (độ rộng theo `id_width` của cấu hình).
- Trước mỗi bảng / danh sách mã có **câu dẫn**: tài liệu nào + nghĩa của mã in đậm + mã trong ngoặc —
  `SPEC có 1 **user story** (US):`, `Sổ REQUESTS ghi mỗi dòng một **request** (RQ), mới nhất ở trên:` (sổ
  gốc không ghi số đếm vì `init` thêm dòng). `check` báo `id-list-lead` (Ghi chú) khi bảng có cột đầu "Mã" mà
  dòng không trống ngay trên không có chữ in đậm; khối "Đang mở" do `index` sinh được miễn.
- Ô mã của bảng viết `Mã (tên ngắn)`, ví dụ `TK1 (hàm tra cứu đơn)`. Tiêu đề việc trỏ spec:
  `### TK1 — Tên (→ FR1.1, SC1)`. Nhắc sang tài liệu khác: `FS-001/FR1.1`.
- `check` coi một mã là **được định nghĩa** khi nó đứng đầu tiêu đề, đứng đầu ô thứ nhất của bảng có cột đầu
  "Mã", hoặc đứng đầu gạch đầu dòng in đậm (`- **FR1.1 (…):**`). Việc `TK` được nhận ở tiêu đề lẫn gạch đầu
  dòng in đậm (`- **TK1 (…) → FR1.1, SC1:**`) và phải trỏ ít nhất một `FR`/`SC` trên chính dòng đó; `TK1.1`
  không tự khai thì kế thừa phần trỏ của `TK1`. Khoảng `SC1–SC3` tính đủ ba mã. Mã trong code span, khối
  code, comment HTML, hoặc sau dấu `/` (`FS-001/FR1.1`) không được đối chiếu.
- Kết quả phép kiểm (`VR`, cột trạng thái việc): Đạt · Không đạt · Chưa chạy · Không áp dụng (kèm lý do);
  bảng việc thêm Đang làm · bỏ.
- Phủ kiểm của REPORT: mỗi `SC` của SPEC xuất hiện trong ít nhất một dòng `VR`; mỗi `FR` cũng vậy — dòng `VR`
  trỏ `FRn` hoặc một kịch bản `FRn.m` đều tính. `FR` có trạng thái `bỏ` ở dòng định nghĩa ("(bỏ)" hoặc "— bỏ"
  cuối dòng), hoặc được ghi `NOT_APPLICABLE` kèm lý do, thì được miễn.
- Mức phát hiện và rủi ro: Chặn · Phải sửa · Nên sửa · Ghi chú. Kết luận: Đạt · Đạt có điều kiện · Không đạt.
- Điều chỉnh nội bộ trong nhật ký PROGRESS theo khuôn
  `Phán quyết: <quyết gì> — <vì sao> — <sai thì tốn gì>`. Mục Review & Retro của REPORT đọc lại các dòng này
  và rà nợ để lại ở khối "Đang mở" của REQUESTS (mỗi `CO` đã thành một dòng `RQ-` ghi nguồn `từ SPR-xx/COn`).
- Delta so với spec sống: dòng `FR` của SPEC ghi `(sửa FS-001/FR1.2)` hoặc `(bỏ FS-001/FR1.2)` ở cuối; không
  ghi gì là Thêm. Dấu delta khác trạng thái `bỏ` của chính mục (`(bỏ)` trần): `FR` mang delta Bỏ vẫn cần `VR`
  chứng minh hành vi đã gỡ. Bước 5 gộp theo delta (cách gộp: comment đầu `registry/feature-spec.md`); cột "Đổi
  gì" của lịch sử sprint ghi `Thêm … · Sửa … · Bỏ …`.
- Trạng thái trong cột bảng sổ gốc viết chữ Việt: REQUESTS `mới` · `đang làm` · `xong` · `bỏ`; SPECS
  `đề xuất` · `đang làm` · `đang chạy` · `ngừng` · `bỏ` (khớp `status` của spec sống theo thứ tự ở mục 3).

## 6. Sổ gốc và khối "Đang mở"

- Mỗi sổ có đúng một khối giữa hai dòng `<!-- agile:open:start -->` và `<!-- agile:open:end -->`. `index` ghi
  lại **toàn bộ** nội dung giữa hai dấu mốc, không đụng phần khác; cùng đầu vào cho cùng đầu ra (sắp theo mã
  giảm dần). Không có mục thì ghi đúng câu "Không có … nào đang mở." như mẫu.
- Bảng chính của sổ: cột đầu là mã, **mới nhất ở trên**, thứ tự cột cố định như mẫu.

| Sổ | Nguồn của khối "Đang mở" | Cột của khối |
|---|---|---|
| REQUESTS | dòng bảng Timeline có trạng thái `mới` hoặc `đang làm` | Mã · Ngày · Tóm tắt · Trạng thái · Sprint |
| SPECS | frontmatter các spec sống trong `paths.feature_specs_dir` có `status` là `proposed` hoặc `in_progress` | Mã · Tính năng · Trạng thái · Spec sống |
| SPRINTS | frontmatter `PROGRESS.md` (hoặc `SPRINT.md`) của từng thư mục sprint có `status` khác `done` và `dropped`; mục tiêu lấy từ dòng Timeline cùng mã | Mã · Mở · Mục tiêu · Trạng thái · Vòng · Thư mục |

Cột Trạng thái của khối viết chữ Việt: SPECS `proposed` → đề xuất, `in_progress` → đang làm; SPRINTS
`drafting` → đang viết SPEC/PLAN, `awaiting_gate_1` → chờ Cổng 1, `in_progress` → đang làm, `verifying` → đang
kiểm định, `blocked` → vướng, `awaiting_gate_2` → chờ Cổng 2.

## 7. Cấu hình dự án (`project/agile.json` → `.agile.json`)

| Khoá | Mặc định | Ý nghĩa |
|---|---|---|
| `schema` | `1` | Phiên bản hình dạng file |
| `visibility` | `private` | `private`: hồ sơ nằm trong repo dự án. `public`: `artifact_root` **phải** trỏ ra ngoài repo (không đưa kế hoạch nội bộ lên repo công khai); `check` so đường dẫn tuyệt đối và báo mức **Chặn** nếu `artifact_root` nằm trong gốc dự án |
| `artifact_root` | `.` | Gốc của mọi đường dẫn trong `paths` trừ `adr_dir`; tương đối theo gốc dự án hoặc tuyệt đối |
| `paths.*` (chung) | — | Đường **tương đối**, không chứa `..`; `init`/`index` từ chối ghi ra ngoài gốc dự án và `artifact_root` (thoát 2), `check` báo `config-invalid` |
| `paths.requests` · `paths.sprints` | `docs/plans/REQUESTS.md` · `docs/plans/SPRINTS.md` | Hai sổ timeline |
| `paths.sprint_dir` | `docs/plans/{date}-{slug}` | Thư mục mỗi sprint; `{date}` = `YYYY-MM-DD` ngày mở, `{slug}` = kebab-case |
| `paths.specs` · `paths.feature_specs_dir` | `docs/specs/SPECS.md` · `docs/specs` | Mục lục tính năng và thư mục spec sống |
| `paths.adr_dir` | `docs/architecture/adr` | ADR `NNNN-<slug>.md`; luôn tương đối theo gốc dự án |
| `id_width.request` · `.feature` · `.sprint` | `3` · `3` · `2` | Số chữ số tối thiểu của `RQ-` · `FS-` · `SPR-` |
| `coverage.line_min_percent` | `80` | Ngưỡng coverage dòng cho code mới và code được sửa |
| `coverage.reason` | `""` | Bắt buộc khác rỗng khi ngưỡng khác 80 |
