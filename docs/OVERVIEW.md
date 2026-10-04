---
title: Overview — what agent-agile-team is, how it works, how to install
type: guide
status: active
updated: 2026-10-04
---

# agent-agile-team — tổng quan

> **Kết luận:** agent-agile-team là một **phương pháp làm phần mềm cho đội AI agent**: bạn giao việc bằng lời
> thường, xác nhận **một tin trao đổi** lúc tiếp nhận (mục tiêu, bậc việc, có mở sprint không), rồi trả lời đúng
> **hai lần** (duyệt kế hoạch, nghiệm thu kết quả), đội agent làm phần còn lại, ghi sổ,
> và nhờ **agent khác** kiểm. Repo gồm luật lõi, 32 skill, 13 agent, bộ mẫu tài liệu và ba công cụ kiểm; cài
> được trên Claude Code, Codex và Antigravity. Bản hiện tại `0.3.0-dev`, repo **private**.

File này là nguồn cho trang giới thiệu <https://ducnguyen.vn/agent-agile-team/>. Số liệu và tên file khớp repo
ở bản `0.3.0-dev`; đổi repo thì sửa file này cùng lượt. Người mới cài xong đọc tiếp [`GUIDE.md`](../GUIDE.md).

## 1. Định vị và lợi ích

**Một câu:** agent-agile-team biến "nhờ AI viết code" thành một quy trình có kế hoạch, có kiểm định độc lập
và có hồ sơ — bạn chỉ phải quyết ở hai điểm, phần còn lại agent tự chạy và tự ghi lại.

Lợi ích cho người không chuyên:

- **Nói lời thường, không cần biết thuật ngữ.** Bạn mô tả việc muốn làm; agent tự viết ra "làm gì" (SPEC) và
  "làm thế nào" (PLAN) rồi trình bản tóm tắt ngắn để bạn duyệt.
- **Một tin trao đổi lúc tiếp nhận, rồi chỉ bị hỏi đúng hai lần.** Khi nhận việc, agent gửi **một tin gom**: nhắc
  lại mục tiêu theo cách hiểu, câu hỏi phản biện, khuyến nghị bậc việc và có cần mở sprint không — bạn trả lời một
  lần. Sau đó: Cổng 1: duyệt hoặc điều chỉnh kế hoạch. Cổng 2: Đạt / Đạt có điều kiện / Không đạt.
  Agent hỏi lẻ giữa chừng là lỗi quy trình — bạn được quyền nhắc.
- **Người làm không tự chấm.** Agent viết code không được kết luận "xong" cho chính nó; một agent khác kiểm và
  ghi bằng chứng (lệnh đã chạy, kết quả thật).
- **Mọi việc đều có dấu vết.** Mỗi yêu cầu, mỗi sprint, mỗi quyết định có mã và nằm trong tài liệu tra được —
  tháng sau mở lại vẫn biết vì sao làm vậy.
- **Việc nhỏ đi đường nhẹ.** Sửa một dòng chữ không cần bốn tài liệu; bậc việc quyết độ dày hồ sơ, không phải
  nghi thức. Việc 1–2 thao tác có kết quả rõ, hay bạn nói "không cần sprint", agent **làm thẳng** — không hồ sơ,
  vẫn kiểm và báo kết quả.

Con số của bản `0.3.0-dev`: **6** bước · **2** cổng người · **6** vai · **3** tier · **32** skill · **13** agent ·
**3** công cụ Python · **3** harness được hỗ trợ.

## 2. Tính năng

### 2.1 Quy trình sáu bước, hai cổng người

Một sprint = một mục tiêu, đi đúng sáu bước; bạn xác nhận một tin trao đổi lúc tiếp nhận rồi chỉ quyết ở hai cổng.

- Tiếp nhận (một tin trao đổi gom: mục tiêu, câu hỏi phản biện, bậc việc, có mở sprint không) → SPEC + PLAN
  (**Cổng 1**) → Thực thi ↔ Kiểm định (vòng lặp, khuyến nghị 3 vòng) → REPORT (**Cổng 2**) → Bài học.
- Ngoài tin trao đổi tiếp nhận và hai cổng, agent chỉ dừng hỏi ở **bốn điều kiện**: hành động không hoàn tác được; chạm bảo mật hay
  secret; tác động ra ngoài phạm vi đã giao (push, deploy, gửi tin); kế hoạch hỏng vì giả định sai.
- Chỗ kế hoạch chưa nói tới, agent tự quyết và ghi một dòng `Phán quyết: <gì> — <vì sao> — <sai thì tốn gì>`
  vào nhật ký, không hỏi.
- Không viết code trước Cổng 1; không push, không gộp nhánh chính trước Cổng 2 và khi bạn chưa gật.

### 2.2 Bậc việc — việc đơn giản đi đường nhẹ

Bậc "làm thẳng" và bốn cỡ việc quyết độ dày tài liệu và độ sâu kiểm định; rủi ro chỉ được **nâng** cỡ, không hạ.
Agent khuyến nghị bậc trong tin trao đổi lúc tiếp nhận; bạn xác nhận.

| Cỡ | Dấu hiệu | Hồ sơ | Kiểm định |
|---|---|---|---|
| Làm thẳng | 1–2 thao tác, kết quả rõ; hoặc bạn nói "không cần sprint". Không áp khi chạm vùng rủi ro, file luật, secret, việc không hoàn tác — trừ khi bạn nói rõ không cần sprint | không hồ sơ, không sprint | agent tự kiểm (lệnh + kết quả mới chạy) và báo trong lời trả lời |
| Rất nhỏ | đổi chữ hoặc một chỗ, không đổi hành vi, lời giao đã nêu rõ kết quả | một `SPRINT.md` hai phần (Kế hoạch · Kết quả) | tự kiểm ghi "chưa độc lập", hoặc agent khác kiểm nhanh |
| Nhỏ | sửa cục bộ một luồng có sẵn, một yêu cầu chức năng, không đổi hợp đồng | một `SPRINT.md` bốn phần | một reviewer khác người làm |
| Vừa | tính năng hay luồng mới, hoặc nhiều yêu cầu chức năng | bốn file SPEC · PLAN · PROGRESS · REPORT | Business Reviewer và Tech Reviewer |
| Lớn | nhiều phần, đổi hợp đồng / schema, hoặc rủi ro cao | bốn file + mục đổi hợp đồng + ADR + kế hoạch hoàn tác | hai reviewer + thẻ chuyên đề |

- Chạm secret, xác thực, đầu vào từ ngoài, API công khai, hạ tầng, migration dữ liệu hay file luật → nhãn
  `risk_tags`, cỡ tối thiểu là **lớn**, dù diff chỉ một dòng.
- **Phân vân giữa hai cỡ → chọn cỡ nặng hơn**: nghi có đổi hành vi hay hợp đồng thì không phải rất nhỏ
  ([`method/sizing.md`](../method/sizing.md) mục 1).
- `init --tiny` và `init --size small` dựng đúng hình hồ sơ; `check` báo khi hồ sơ không khớp cỡ.

### 2.3 Vai và tier — giao việc theo năng lực, không theo tên model

Sáu vai agent chia hai nhóm; mỗi vai có tier; repo không chứa tên model thật.

- **Thực thi:** Analyst (điều phối, T1) · Architect (T1) · Implementer (T2) · QA (T3). **Kiểm định:** Business
  Reviewer (T1) · Tech Reviewer (T1), kéo thêm 4 thẻ chuyên đề security · data · backend · frontend khi rủi ro cao.
- Tier: `T1` tư duy · `T2` thực thi · `T3` việc vặt và chạy test. Bảng tier → model nằm **ngoài repo**, trỏ
  bằng biến môi trường `AGENT_AGILE_TIERS`; thiếu bảng thì agent dùng chỉ định của bạn trong chat, không đoán.
- Cạn hạn mức model: dừng tier đó, ghi vướng mắc, báo bạn — **không tự hạ tier**.
- Mỗi lần giao việc cho agent con, hồ sơ ghi đủ vai · tier · model thực tế.

### 2.4 Bộ 32 skill và 13 agent

Skill là năng lực thường trực: agent rà danh mục trước mỗi hành động và tự gọi skill khớp tình huống.

- **32 skill**, năm nhóm: Quy trình (6: `intake`, `shaping-spec`, `writing-plan`, `running-sprint`,
  `closing-sprint`, `bug-triage`) · Kỹ thuật (15: `tdd`, `debugging` và 13 skill tham chiếu như `python`,
  `fastapi`, `postgres`, `react`, `deployment`…) · Kiểm định (6: `verify-before-done`, `code-review`,
  `plan-review`, `security-review`, `security-audit`, `web-qa`) · Giao tiếp và tối ưu (3: `response-style`,
  `id-convention`, `token-economy`) · Meta (2: `writing-skills`, `eval-harness`).
- Skill **kỷ luật** (19) có luật sắt và được thử áp lực; skill **tham chiếu** (13) là bảng tra kỹ thuật và được
  thử truy xuất. Cả 32 đều có tệp thử đã chạy.
- **13 agent** chuyên đề: 12 agent **chỉ đọc** (reviewer theo ngôn ngữ, bảo mật, CSDL, săn lỗi bị nuốt, kiểm
  comment, kiểm test, lần bản đồ code…) và `build-fixer` — agent duy nhất được sửa file, chỉ sửa đúng chỗ lỗi
  build đòi.
- Thứ tự gọi: skill quy trình trước, skill kỹ thuật sau. "Làm X" → định hình spec trước; "sửa lỗi" → debug trước.

### 2.5 Kiểm định độc lập

Kết luận Đạt chỉ đến từ bằng chứng **mới chạy** do agent **khác** người làm ghi.

- Reviewer nhận ngữ cảnh soạn riêng, không dán lịch sử phiên; được trả 0 phát hiện nhưng phải ghi phần không
  đánh giá.
- Một thang mức chung cho mọi phát hiện: **Chặn / Phải sửa / Nên sửa / Ghi chú**; một thang kết luận: **Đạt /
  Đạt có điều kiện / Không đạt**. Thang cũ của mọi nguồn quy về một bảng duy nhất. Reviewer phân vân giữa hai
  mức → chọn mức **nặng hơn** và nói rõ vì sao ([`method/severity.md`](../method/severity.md)).
- Việc chạm file luật, secret hay xác thực → `dual-review`: hai reviewer độc lập cùng rubric, cả hai Đạt mới Đạt.
- Từ cỡ vừa: cổng review bốn pha — review song song theo khía cạnh, gộp theo bằng chứng, kiểm đối kháng từng
  phát hiện Chặn / Phải sửa, và **lỗi thì đóng** (khía cạnh nào không chạy thì không ghi Đạt).
- "Chưa chạy", "chắc chạy được", "đã test" không kèm lệnh — không bao giờ là Đạt.

### 2.6 Máy kiểm: `init` · `check` · `index`

Ba công cụ Python chỉ dùng thư viện chuẩn (3.9+), chạy trên Windows và macOS, không cần cài gói nào.

- `init` dựng `.agile.json`, ba sổ gốc và khung sprint từ mẫu; mặc định chạy thử, **không bao giờ ghi đè**.
- `check` kiểm chuẩn tài liệu bằng 32 luật: đủ mục, mã đúng chuẩn, mỗi tiêu chí có kết quả kiểm, không ai tự
  chấm, cổng đã kết luận thì có câu nguyên văn. Thoát 0 = Đạt, 1 = Không đạt, 2 = lỗi đầu vào.
- `check --self` kiểm chính repo phương pháp: lõi sạch, ngân sách `AGENTS.md` (≤120 dòng, ≤10 KB), và luật
  **chống rò** — không một đường máy, tên người hay dự án riêng nào lọt vào lõi.
- `index` sinh lại khối "Đang mở" ở đầu ba sổ gốc để agent tra nhanh việc đang chạy.

### 2.7 Sổ tập trung

Dự án có thể bật một sổ Markdown ngoài repo để nhìn trạng thái nhiều dự án ở một chỗ.

- Bật bằng khoá `ledger.project` trong `.agile.json`; máy cấp mẫu đường kho sổ qua biến `AGENT_AGILE_LEDGER`.
- Ghi tại năm thời điểm: mở sprint, qua Cổng 1, quay lại thực thi, Cổng 2, đóng sprint — luôn kèm bằng chứng.
- `check` bắt sổ lệch hồ sơ (thiếu dòng, trạng thái cũ, file sổ không đọc được). Dự án không khai khoá thì
  không áp.

### 2.8 Chuẩn code `method/standards/`

Chuẩn là luật ngắn; skill giữ mẫu code và lý do.

- 7 chuẩn chung (`common/`: phong cách, test, bảo mật, git, code review, quy trình phát triển, giao việc agent)
  và 4 chuẩn theo ngôn ngữ (`python`, `typescript`, `react`, `web`).
- Implementer đọc chuẩn của ngôn ngữ đang viết; Tech Reviewer đọc khi review. Chuẩn **không** nạp vào luật lõi.
- Ngưỡng coverage mặc định 80 % cho code mới và code được sửa; đổi ngưỡng phải ghi lý do.

### 2.9 Quy tắc phiên bản

Số phiên bản `MAJOR.MINOR.PATCH`, mỗi đợt tăng đúng một phần, do thay đổi nặng nhất quyết.

- Dưới `1.0.0`, thay đổi gãy chỉ tăng MINOR; bản chưa phát hành mang hậu tố `-dev`.
- Agent **đề xuất** mức tăng kèm lý do ở Cổng 2; bạn quyết. Agent không tự tăng version, không ghi đè CHANGELOG.
- Ba manifest plugin và mục đầu `CHANGELOG.md` phải cùng một số — có test giữ điều này.

### 2.10 Nguồn gốc và giấy phép

Repo chưng cất từ các bộ skill mã nguồn mở và ghi dấu vết từng dòng.

- Nguồn chính (MIT): Superpowers, Everything Claude Code, gstack, superpowers-lab, Supabase Agent Skills; lấy
  ý từ GitHub Spec Kit, OpenSpec, BMAD-METHOD, Kiro/EARS. Mọi skill và agent ghi `source`, `source_sha`,
  `license` trong frontmatter; `UPSTREAM.md` chốt SHA từng đợt và theo dõi bản mới.
- Phần từng lấy từ nguồn private đã được **viết lại phòng sạch**: bản cũ gỡ khỏi cây, người viết mới chỉ nhận
  danh sách ý; hiện không còn file nào chờ viết lại.
- Giấy phép của repo **chưa chọn**; giữ mọi quyền trong thời gian private. Nội dung bên thứ ba giữ giấy phép
  gốc (`NOTICE`, `THIRD_PARTY.md`).

## 3. Cách hoạt động — một ví dụ

Bạn nói với agent trong thư mục dự án: *"Dùng agent-agile-team: thêm chức năng tra cứu đơn theo mã cho dự án
này."* Sáu bước diễn ra như sau.

| Bước | Ai làm | Tạo ra gì | Bạn làm gì |
|---|---|---|---|
| 1. Tiếp nhận | Analyst | **một tin trao đổi**: nhắc lại mục tiêu, vài câu hỏi phản biện (tra theo mã nào, ai dùng, xong là gì), khuyến nghị cỡ **vừa** (hành vi mới) và mở sprint; sau khi bạn xác nhận: một dòng yêu cầu `RQ-001` trong sổ REQUESTS kèm câu trả lời của bạn; giả định ghi nhãn ASSUMPTION; điểm còn chưa rõ gom thành câu hỏi cho Cổng 1 | trả lời tin trao đổi một lần (xác nhận mục tiêu, cỡ, có mở sprint) |
| 2. SPEC rồi PLAN | Analyst viết SPEC; Architect viết PLAN; Tech Reviewer soát PLAN | thư mục sprint `docs/plans/<ngày>-order-lookup/` với SPEC (người dùng cần gì, kịch bản KHI… THÌ…, tiêu chí thành công) và PLAN (từng việc: ai làm, kiểm ra sao, hoàn tác thế nào) | **Cổng 1:** đọc bản tóm tắt vài dòng, trả lời "duyệt" hoặc "điều chỉnh: …" |
| 3. Thực thi | Implementer (code, test), QA (chạy test) | code trên nhánh riêng; PROGRESS ghi từng việc kèm bằng chứng và các dòng `Phán quyết:` | không gì |
| 4. Kiểm định | Business Reviewer, Tech Reviewer — agent **khác** người làm | phát hiện có mức và bằng chứng; còn Chặn / Phải sửa thì quay lại bước 3 (một vòng) | không gì; sau 3 vòng còn lỗi thì chọn làm tiếp hay dừng |
| 5. REPORT | Analyst | REPORT: kết luận một câu, tóm tắt cho người không chuyên, kết quả kiểm, cách dùng, cách hoàn tác, việc để lại; sau khi bạn kết luận: spec sống của tính năng cập nhật, sprint đóng trong sổ SPRINTS | **Cổng 2:** Đạt / Đạt có điều kiện / Không đạt; rồi chọn gộp nhánh, push + PR, hay giữ nguyên |
| 6. Bài học | Analyst | bài học tái dùng ghi trong REPORT và vào nơi môi trường quy định; nợ để lại thành dòng `RQ-` mới | quyết có nâng bài học thành luật hay skill không |

Hồ sơ của đúng ví dụ này — bốn sprint (một cỡ vừa đủ bốn tài liệu, một cỡ nhỏ, hai cỡ rất nhỏ), ba sổ gốc và
một spec sống — nằm ở [`samples/order-desk/`](../samples/README.md).

## 4. Cấu trúc thư mục

Luật lõi ở một chỗ, chi tiết tách theo thư mục; mỗi thư mục có `README.md` riêng.

```text
agent-agile-team/
├── AGENTS.md            luật lõi — agent đọc mỗi phiên (≤120 dòng, ≤10 KB)
├── CLAUDE.md            một dòng @AGENTS.md cho Claude Code
├── GEMINI.md            con trỏ tới AGENTS.md cho Antigravity
├── README.md · README.vi.md   giới thiệu ngắn (Anh · Việt)
├── GUIDE.md             sprint đầu tiên — bạn làm gì, agent làm gì
├── INSTALL.md           hướng dẫn cài dành cho AI agent (prompt dán ở cuối)
├── method/              luật chơi: process, sizing, severity, evidence, review-gate, conventions
│   └── standards/       chuẩn code chung và theo ngôn ngữ
├── roles/               thẻ vai: executor/ (4) · verifier/ (2 + dual-review + 4 chuyên đề)
├── tiers/               ba tier và hợp đồng bảng tier → model (tiers.example.json)
├── skills/              32 skill, mỗi skill một thư mục skills/<tên>/SKILL.md
├── agents/              13 agent chuyên đề, mỗi agent một file
├── templates/           khuôn hồ sơ: sprint/ (6) · registry/ (5) · project/agile.json
├── scripts/             init.py · check.py · index.py (+ _common.py)
├── tests/               bộ test pytest và fixture
├── samples/order-desk/  một dự án mẫu đã dùng thật, kết quả kỳ vọng cố định
├── hosts/               cài và nạp theo harness: claude · codex · antigravity · claude-desktop
├── docs/                OVERVIEW · MIGRATION · standardization · troubleshooting · updating-from-upstream
├── UPSTREAM.md · NOTICE · THIRD_PARTY.md · LICENSE   nguồn gốc, bản quyền, giấy phép
├── CHANGELOG.md         mục mới nhất đứng đầu, trùng version của manifest
└── .claude-plugin/ · .codex-plugin/   manifest plugin cho Claude Code và Codex
```

Ý nghĩa khi dùng:

| Thư mục / file | Khi nào bạn hoặc agent chạm tới |
|---|---|
| `AGENTS.md` | nạp đầu **mọi** phiên; là bản rút gọn của `method/` — khác nhau thì `method/` thắng |
| `method/process.md` · `sizing.md` · `severity.md` · `evidence.md` | khi phân vân có được hỏi người dùng không, chọn cỡ việc, gán mức phát hiện, ghi kết quả kiểm |
| `method/review-gate.md` · `roles/verifier/dual-review.md` | khi review diff cỡ vừa trở lên, hoặc việc chạm luật / secret / xác thực |
| `roles/executor/*.md` · `roles/verifier/*.md` | khi giao vai cho một agent: mục đích, đầu vào, đầu ra, được làm, không được làm, khi nào dừng |
| `skills/<tên>/SKILL.md` | agent tự gọi theo tình huống; `tests/pressure.md` hay `tests/retrieval.md` là bằng chứng skill đã thử |
| `agents/<tên>.md` | Tech Reviewer kéo theo trigger; trên Codex / Antigravity đọc như thẻ vai trong brief |
| `templates/sprint/` · `templates/registry/` | `init` chép ra dự án của bạn; `templates/README.md` là hợp đồng khoá, tiêu đề, trạng thái mà `check` dựa vào |
| `templates/project/agile.json` → `.agile.json` | đường dẫn hồ sơ, ngưỡng coverage, sổ tập trung của từng dự án |
| `scripts/` | agent chạy trước mỗi cổng; bạn chỉ đọc dòng cuối |
| `samples/order-desk/` | xem hồ sơ thật trông thế nào trước khi mở sprint đầu tiên |
| `hosts/<harness>/README.md` | cài, kiểm, cập nhật, gỡ trên harness của bạn |
| `docs/troubleshooting.md` | triệu chứng → nguyên nhân → cách xử lý khi cài và dùng lần đầu |

Tra nhanh:

| Tôi muốn … | Mở file … |
|---|---|
| hiểu bộ này trong 5 phút | `docs/OVERVIEW.md` (file này), rồi `README.vi.md` |
| cài lên máy | `INSTALL.md` (dán prompt cho agent) hoặc `hosts/<harness>/README.md` (tự gõ) |
| chạy sprint đầu tiên | `GUIDE.md` |
| biết agent được phép làm gì, dừng khi nào | `AGENTS.md`, rồi `method/process.md` |
| biết việc này cỡ nào, có cần ADR không | `method/sizing.md`, `method/conventions.md` |
| xem một hồ sơ sprint mẫu | `samples/order-desk/docs/plans/` |
| biết mỗi mã (`FR`, `TK`, `VR`…) nghĩa gì | `skills/id-convention/SKILL.md` |
| biết `check` báo lỗi gì, vì sao | `scripts/README.md` mục "Luật của `check`" |
| sửa hay thêm skill | `skills/writing-skills/SKILL.md`, `skills/README.md` |
| biết skill này lấy từ đâu, giấy phép gì | frontmatter của skill, `UPSTREAM.md`, `THIRD_PARTY.md` |
| gặp tên skill cũ trong hồ sơ lịch sử | `docs/MIGRATION.md` |
| cài rồi mà agent không biết luật | `docs/troubleshooting.md` |

## 5. Hồ sơ một sprint

Mỗi sprint là một thư mục; cỡ vừa và lớn có bốn tài liệu, cỡ nhỏ và rất nhỏ gộp vào một `SPRINT.md`.

| Tài liệu | Trả lời câu | Ai viết | Mã sống ở đây |
|---|---|---|---|
| SPEC | làm **cái gì**, cho ai, thế nào là xong | Analyst | `US` `FR` `SC` `CQ` |
| PLAN | làm **thế nào**, ai làm, kiểm ra sao | Architect | `TK` `RK` `DN` |
| PROGRESS | đang **ở đâu**, vướng gì, đã quyết gì | vai thực thi, cập nhật sau mỗi việc; nhật ký chỉ thêm, không sửa | `BR` |
| REPORT | **kết quả**: kiểm được gì, phát hiện gì, dùng thế nào, hoàn tác thế nào | Analyst | `VR` `RF` `LN` `CO` |
| `SPRINT.md` | cả bốn phần (cỡ nhỏ) hoặc hai phần Kế hoạch · Kết quả (cỡ rất nhỏ) | như trên | mọi mã của chính nó |

Ba **sổ gốc** sống lâu hơn sprint, mỗi sổ có khối "Đang mở" ở đầu do `index` sinh: REQUESTS (mọi yêu cầu,
`RQ-`), SPRINTS (mọi sprint, `SPR-`), SPECS + spec sống từng tính năng (`FS-`). Nợ để lại của một sprint thành
một dòng `RQ-` mới — không ai phải mở REPORT cũ để tìm nợ.

Mã định danh có tiền tố **hai chữ cái** lấy từ tên tiếng Anh, luôn đi kèm tên ngắn trong chat ("`FR3` (tra theo
mã đơn)"). Bảng dưới liệt kê các **mã** chính:

| Mã | Tên | Nghĩa | Ở tài liệu |
|---|---|---|---|
| `RQ-` | request | một yêu cầu của bạn, theo thời gian (`RQ-001`) | sổ REQUESTS |
| `SPR-` | sprint | một sprint = một mục tiêu (`SPR-01`) | sổ SPRINTS |
| `FS-` | feature spec | spec sống của một tính năng đang chạy (`FS-001`) | sổ SPECS |
| `US` | user story | ai cần gì, vì sao | SPEC |
| `FR` | functional requirement | hành vi phải có; `FR1.2` là một kịch bản KHI… THÌ… | SPEC |
| `SC` | success criterion | thế nào là xong, đo được | SPEC |
| `CQ` | clarifying question | điều chưa rõ, hỏi một lần ở Cổng 1 | SPEC |
| `TK` | task | một việc: vai, tier, cách kiểm, hoàn tác; `TK2.3` là việc con | PLAN |
| `RK` | risk | rủi ro và cách giảm | PLAN |
| `DN` | decision | quyết định cần bạn | PLAN |
| `BR` | blocker | vướng mắc khiến agent dừng hỏi | PROGRESS |
| `VR` | verification result | kết quả một phép kiểm: Đạt · Không đạt · Chưa chạy · Không áp dụng | REPORT |
| `RF` | review finding | phát hiện của reviewer, mang mức Chặn / Phải sửa / Nên sửa / Ghi chú | REPORT |
| `LN` | lesson | bài học tái dùng | REPORT |
| `CO` | carry-over | việc để lại, có chủ và mốc | REPORT |

Frontmatter của mỗi tài liệu (khối khoá–giá trị ở đầu file, tiếng Anh) ghi cỡ, rủi ro, vai và nhãn agent, trạng
thái cổng kèm **câu duyệt nguyên văn** của bạn — `check` đọc chúng để bắt hồ sơ lệch.

## 6. Cài đặt và dùng

Cần **Git** và **Python 3.9+**; ba script không cần cài gói nào (chỉ `pytest` khi muốn chạy bộ test của repo).

**Repo đang private.** Bạn cần quyền đọc `https://github.com/ducnguyen221/agent-agile-team` mới clone được;
chưa có quyền thì phần cài dưới đây chưa dùng được.

### 6.1 Cách nhanh nhất: để agent cài

Dán prompt ở cuối [`INSTALL.md`](../INSTALL.md) vào Claude Code, Codex hoặc Antigravity. Agent đọc file đó, làm
lần lượt, và **hỏi trước** mỗi lần cài phần mềm, sửa file luật của harness hay đặt biến môi trường. Cài xong agent
chép nguyên dòng cuối của `check.py --self` cho bạn.

### 6.2 Tự làm — bước chung

```bash
git clone https://github.com/ducnguyen221/agent-agile-team ~/agent-agile-team        # macOS, bash
```

```powershell
git clone https://github.com/ducnguyen221/agent-agile-team "$HOME\agent-agile-team"  # Windows PowerShell
```

Windows PowerShell 5.1 không mở `~` cho `git`, `python`, `claude` — dùng `"$HOME\agent-agile-team"`. Trên macOS
mọi lệnh `python` dưới đây là `python3`.

### 6.3 Theo harness

| Harness | Skill và agent | Luật lõi cho mọi dự án | Chi tiết |
|---|---|---|---|
| **Claude Code** (terminal, IDE, tab Code của ứng dụng Claude) | `claude plugin marketplace add ~/agent-agile-team` rồi `claude plugin install agent-agile-team@agent-agile-team`; skill hiện với tiền tố `agent-agile-team:` | thêm một dòng `@~/agent-agile-team/AGENTS.md` vào `~/.claude/CLAUDE.md` | [`hosts/claude/`](../hosts/claude/README.md) |
| **Codex** (CLI hoặc desktop) | cài plugin từ `.codex-plugin/plugin.json` theo `codex plugin --help`, hoặc mở thẳng thư mục repo | ghép `AGENTS.md` vào `~/.codex/AGENTS.md` bằng một script sinh của môi trường, không chép tay | [`hosts/codex/`](../hosts/codex/README.md) |
| **Antigravity** | mỗi skill một liên kết thư mục từ `~/.gemini/antigravity/skills/<tên>` về `skills/<tên>/` của bản clone | ghép vào `~/.gemini/GEMINI.md` như Codex | [`hosts/antigravity/`](../hosts/antigravity/README.md) |
| Claude Desktop, tab chat | **chưa hỗ trợ** — dùng tab Code | — | [`hosts/claude-desktop/`](../hosts/claude-desktop/README.md) |

Trên Codex và Antigravity, 13 agent trong `agents/` là thẻ vai Markdown: brief của agent con ghi "đọc
`agents/<tên>.md` rồi làm theo".

### 6.4 Điểm cắm (tuỳ chọn)

Không đặt gì repo vẫn chạy. Muốn cố định thì đặt biến ở mức tài khoản, trỏ file **ngoài repo**, rồi mở phiên mới:

| Biến | Trỏ tới | Thiếu thì |
|---|---|---|
| `AGENT_AGILE_TIERS` | file JSON bảng tier → model (hình dạng: `tiers/tiers.example.json`) | agent dùng chỉ định tier → model bạn nêu trong chat; chưa có thì hỏi ở Cổng 1 |
| `AGENT_AGILE_DENYLIST` | file văn bản từ cấm, một từ một dòng | `check --self` báo luật chống rò **Chưa chạy** (`NOT_CONFIGURED`) — không phải lỗi |
| `AGENT_AGILE_LEDGER` | mẫu đường file sổ tập trung, chứa `{project}` | chỉ dự án khai `ledger.project` mới dùng |

### 6.5 Kiểm sau khi cài

```bash
cd ~/agent-agile-team && python3 scripts/check.py --self                                   # macOS
```

```powershell
python "$HOME\agent-agile-team\scripts\check.py" --self --root "$HOME\agent-agile-team"    # Windows
```

Dòng cuối có `→ Đạt` là lõi nguyên vẹn. Rồi mở **phiên mới** và hỏi agent: *"luật lõi agent-agile-team nói gì về
hai cổng?"* — trả lời đúng là luật đã nạp.

### 6.6 Dùng lần đầu trong dự án của bạn

```bash
python3 ~/agent-agile-team/scripts/init.py .            # chạy thử: in sẽ tạo gì, không ghi
python3 ~/agent-agile-team/scripts/init.py . --apply    # tạo .agile.json + REQUESTS, SPRINTS, SPECS
python3 ~/agent-agile-team/scripts/check.py docs/plans  # kiểm hồ sơ sprint
python3 ~/agent-agile-team/scripts/index.py .           # sinh lại khối "Đang mở"
```

`init` không ghi đè file có sẵn; chạy lại không đổi gì. Sau đó giao việc bằng lời thường — ví dụ *"Dùng
agent-agile-team: thêm chức năng tra cứu đơn theo mã cho dự án này."* — và đọc tiếp [`GUIDE.md`](../GUIDE.md).

Cập nhật: `git pull --ff-only` trong bản clone (Claude Code thêm `claude plugin marketplace update agent-agile-team`
và `claude plugin update agent-agile-team@agent-agile-team`). Gỡ không xoá sổ gốc hay hồ sơ sprint của dự án.

## 7. Câu hỏi thường gặp

**Tôi không phải lập trình viên, dùng được không?** Được ở vai người giao việc và nghiệm thu: bạn nói lời
thường, đọc bản tóm tắt vài dòng ở hai cổng, và được quyền hỏi "`FR3` là gì?". Phần kỹ thuật agent làm và tự ghi.

**Agent có tự push code hay deploy không?** Không. Push, PR, gộp nhánh chính, deploy là tác động ra ngoài — chỉ
sau Cổng 2 và khi bạn gật. Agent cũng không bỏ hook, không force-push, không hạ ngưỡng test để qua kiểm.

**Việc nhỏ có phải viết đủ bốn tài liệu?** Không. Rất nhỏ: một `SPRINT.md` hai phần, Cổng 1 là "đạt theo lời
giao". Nhỏ: một `SPRINT.md` bốn phần. Từ cỡ vừa mới dùng bốn file.

**Repo có chứa tên model, giá tiền hay tài khoản nào không?** Không. Repo chỉ biết ba tier; bảng tier → model,
danh sách từ cấm và nơi lưu bài học nằm ngoài repo, cắm vào qua biến môi trường. `check --self` bảo đảm lõi
không lộ dấu riêng của máy nào.

**Có cần Node, Docker hay dịch vụ ngoài không?** Không. Chỉ Git và Python 3.9+. Hai công cụ đo token
(`ccusage`, `repomix`) trong skill `token-economy` gọi qua `npx` khi bạn muốn, không bắt buộc.

**Chạy trên Windows được không?** Được. Bộ test chạy trên Ubuntu, Windows, macOS × Python 3.9 và 3.13 ở CI.
Lưu ý duy nhất: Windows PowerShell 5.1 không mở `~` cho chương trình ngoài.

**Hồ sơ sprint có bắt buộc nằm trong repo dự án không?** Không. Repo công khai thì đặt `visibility: public`
và `artifact_root` trỏ ra ngoài trong `.agile.json`; `check` chặn nếu hồ sơ nội bộ lại nằm trong repo công khai.

**Dùng cho việc không phải viết code được không?** Phương pháp và luật lõi viết cho phát triển phần mềm (code,
test, review, nhánh git); bộ mẫu tài liệu và ba công cụ không đòi code, nhưng phần lớn skill kỹ thuật và agent
reviewer là cho phần mềm.

## 8. Giới hạn hiện tại

Trung thực về chỗ chưa tới:

- **Repo private, giấy phép chưa chọn.** Người ngoài chưa clone được; chưa có bản phát hành, version đứng ở
  `0.3.0-dev`.
- **12/13 skill tham chiếu chưa đạt ngưỡng truy xuất** (chỉ `adr` đạt): agent tìm đúng chỗ nhưng nội dung còn
  thiếu để trả lời hẳn; đang bổ sung và sẽ đổi cách đo trước khi vá tiếp. Trong 91 câu thử chỉ 1 câu Không đạt.
- **Tệp thử skill chạy trên một dòng model** (tier T3); kết quả có thể khác trên model khác.
- **Claude Desktop tab chat chưa hỗ trợ**; Codex và Antigravity không nạp `agents/` như agent riêng — đọc như thẻ vai.
- **`check` chứng minh hồ sơ nhất quán, không chứng minh nội dung đúng**: bằng chứng vẫn do agent khác chạy;
  `check` không mở link, không đọc kết quả thật trong ô bằng chứng.
- **Sổ tập trung:** `init` và `index` chưa tự ghi dòng sổ; so ngày theo ngày nên hai lần đổi trạng thái trong
  cùng ngày chỉ bắt được qua trạng thái.
- **Luật chống rò chỉ chạy khi có danh sách từ cấm** (biến `AGENT_AGILE_DENYLIST`); ở CI không có danh sách
  nên luật báo `NOT_CONFIGURED` và một test skip có lý do — không tính là Đạt.
- **Chưa có bản tiếng Anh** của skill, phương pháp và trang giới thiệu; frontmatter và `README.md` là tiếng Anh.
