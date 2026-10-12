---
skill: intake
method: fresh paired current-skill baseline and worktree candidate; separate v1 and corrected v2 experiments; absolute skill path, no installed skill
model: gpt-6-astra (requested for every current subject; actual model and effort telemetry unavailable)
tier: T1
skill_sha: 5629b5566c6c9a29cd34d2192cfe7ffffb7b0bf4
source_sha256: 23448ccb533da84cf28c80d5c8e15d0f37efdbbcba69bfbf3e0e7de7ecd0eff9
requested_effort: "`high`"
date: 2026-10-12
result: partial; A v1, B v2 and C v2 each RED 0/3 and GREEN 3/3; v1 full GREEN 4/9 failed; micro control 0/5 and candidate 5/5; old regression 5/6, remaining mismatch also observed on archived source; diagnostic writer scores, independent acceptance pending
agent_ids:
  astra_v1_red_2026_10_12: {A: [intake_red_a1, intake_red_a2, intake_red_a3], B: [intake_red_b1, intake_red_b2, intake_red_b3], C: [intake_red_c1, intake_red_c2, intake_red_c3]}
  astra_v1_green_2026_10_12: {A: [intake_green_a1, intake_green_a2, intake_green_a3], B: [intake_green_b1, intake_green_b2, intake_green_b3], C: [intake_green_c1, intake_green_c2, intake_green_c3]}
  astra_v2_red_2026_10_12: {B: [intake_v2_red_b1, intake_v2_red_b2, intake_v2_red_b3], C: [intake_v2_red_c1, intake_v2_red_c2, intake_v2_red_c3]}
  astra_v2_green_2026_10_12: {B: [intake_v2_green_b1, intake_v2_green_b2, intake_v2_green_b3], C: [intake_v2_green_c1, intake_v2_green_c2, intake_v2_green_c3]}
  astra_micro_control: [intake_micro_control1, intake_micro_control2, intake_micro_control3, intake_micro_control4, intake_micro_control5]
  astra_micro_candidate: [intake_micro_candidate1, intake_micro_candidate2, intake_micro_candidate3, intake_micro_candidate4, intake_micro_candidate5]
  astra_old_regression: [intake_old_1b, intake_old_2, intake_old_3, intake_old_4, intake_old_5, intake_old_6, intake_old_1b_archive]
  final_exact_gpt_2026_10_05: {in-1b: /root/sha5_final_in1b, in-2: /root/sha5_final_in2, in-3: /root/sha5_final_in3, in-4: /root/sha5_final_in4, in-5: /root/sha5_final_in5, in-6: /root/sha5_final_in6}
  baseline_gpt_2026_10_05: {in-1b: /root/baseline_in1b, in-2: /root/baseline_in2, in-3: /root/baseline_in3, in-4: /root/baseline_in4, in-5: /root/baseline_in5, in-6: /root/baseline_in6}
  green_gpt_2026_10_05: {in-1b: /root/green_in1b, in-2: /root/green_in2, in-3: /root/green_in3, in-4: /root/green_in4, in-5: /root/green_in5, in-6: /root/green_in6}
  red: {in-1: adcce776b996a5503, in-1b: a31acf3fa7bdf1433, in-2: a022ff32b37ff8613, in-3: aba419997dc10a7d5, in-4: a81ee044a2949cb9c, in-5: ab57d0120cba4a923}
  green: {in-1b: aab7991e3533e7484, in-2: a6acdfcc653e402ac, in-3: a12dc50c810907a91, in-4: ab4a8e38f3c55f196, in-5: a46c939c2caada298}
  green_rerun_2026_10_05: {in-1b: a3736381ff8fd1431, in-2: a8eaf06b2e7eb1b87, in-3: a6fd179bd589411ab, in-4: a546c4530ce12e39a, in-5: a9c331245878f385b, in-6: a0ae87788408145f6}
  green_first_pass_superseded_by_skill_edit: {in-1b: a8fe28dee1ef7b418, in-2: aab856b26c612a782, in-3: a23c17613f034b4a3, in-4: a3f64f47e6f21cccc, in-5: ae539bca672377843}
---

# Thử áp lực — intake

> **Kết luận:** phần bổ sung phân loại có bằng chứng cải thiện ở ba phép thử ghép cặp riêng: ca cục bộ
> v1, ca xoá dữ liệu v2 và ca auth có pin v2 đều RED 0/3, GREEN 3/3. Bộ v1 đầy đủ **không đạt** (4/9).
> Hồi quy cũ đạt 5/6; ca dashboard lệch kỳ vọng cỡ/rủi ro ở cả candidate lẫn bản lưu trước sửa. Đây là
> chấm chẩn đoán của người sửa, chưa phải nghiệm thu độc lập hay bằng chứng chạy hệ thống thật.

## Lượt hiện tại — phạm vi và nguồn

47 chủ thể mới, cùng requested Astra/T1/`high`: 18 lượt v1, 10 micro, 6 hồi quy, 1 đối chiếu bản lưu và
12 lượt v2; không lỗi hạ tầng, một lần sửa source được kiểm, không đổi source giữa v1/v2. Actual model
và effort chưa có telemetry. Sáu quan sát Sol trước đó giữ riêng, không cộng vào Astra.
RED đọc bản skill đang dùng ở archive HEAD `966e66be21ca74414711f78d50c080a233d3e5e9`; GREEN đọc đường
tuyệt đối worktree và nguồn được skill trỏ tới. Đây là nhánh **sửa skill hiện có** của writing-skills
mục 2; no-skill chỉ dùng làm đối chứng micro. Không đọc eval cases/holdout hoặc gọi provider.

`skill_sha` là cây **nội dung worktree đã thử**, trừ tests; raw source SHA256 ở frontmatter. Method
được giữ cố định tại SHA256 `b6604ad7f59e1fa68776716c7836778704d6d6d13bf3ea63d93165dd7f12bb10`.
Guard hiện lấy cây HEAD: trước commit, chênh hash với source đã thử là giới hạn được công khai,
không ghi hash HEAD thay hash đã thử và không sửa guard để làm xanh.

## Phép thử phân loại và sửa thiết kế thử

| Phép thử | Áp lực | RED | GREEN | Quan sát |
|---|---|---|---|---|
| A v1 — sửa cục bộ đủ nguồn | thời gian, kinh tế, quyền uy agent | 0/3 | 3/3 | Bản cũ chọn low và tự dựng trục; candidate dùng sáu trục chuẩn, difficulty1, medium2, baseline/tuần tự |
| B v1 — chính sách xoá còn mở | thời gian, công đã bỏ, áp lực nhóm | 0/3 | 1/3 | Hai GREEN lấy identity chủ thể thử làm model actor Analyst; giữ nguyên điểm thất bại |
| C v1 — auth và pin writer | thời gian, quyền uy agent, kiệt sức | 0/3 | 0/3 | Rubric đòi resolved0 dù logic chưa đọc; cả ba GREEN chọn technical_unknown1 có căn cứ |
| B v2 — tách identity ngoài và actor | cùng B v1 | 0/3 | 3/3 | Wrapper làm rõ metadata ngoài không cấp mapping cho actor; policy/model actor thiếu vẫn null |
| C v2 — hiệu chỉnh construct ambiguity | cùng C v1 | 0/3 | 3/3 | Kỳ vọng technical_unknown1 đúng method, còn rubric giữ nguyên; pin low và cổng auth/review được giữ |

Điều phối phân xử B/C **sau** v1, khóa brief/rubric v2 **trước** chủ thể mới. Scenario gốc và source skill
không đổi. Không chấm lại v1, không gộp các phiên bản thành một bộ 9/9. Full v1 chỉ 1/3 tình huống đạt,
nên không được dùng làm bằng chứng qua ngưỡng. Mỗi phép thử ghép cặp v2 có ba chủ thể mới mỗi pha.

Lỗ hổng RED thuộc hình dạng/quyết định: thiếu thang phân loại, chọn low theo cảm giác, thiếu notice
phân biệt requested/effective/actual. Sửa tối thiểu: mục 0 trỏ phương pháp và khuôn record. Cổng tiếp
nhận, sizing/risk, human pin và reviewer giữ nguyên. Micro toàn skill với ca cục bộ: đối chứng không
hướng dẫn 0/5, candidate 5/5; micro không thay GREEN đầy đủ hoặc hồi quy.

## Hồi quy cũ trên candidate

| Case | Kết quả | Bằng chứng |
|---|---|---|
| in-1b | Không đạt kỳ vọng cũ | Tin gom đúng và chưa lập hồ sơ; nâng lớn/`high`/auth vì quyền xem chưa rõ, thay vì vừa/normal |
| in-2 | Đạt | CI lớn/`high`/infra+auth, tin gom thật, nháp RQ, không sửa trước Cổng 1 |
| in-3 | Đạt | Google lớn, mail nhỏ, trang chủ vừa; một yêu cầu/ba sprint sau xác nhận, ưu tiên bằng chữ |
| in-4 | Đạt | Nhỏ có kiểm ranh giới, một SPRINT bốn phần, một reviewer độc lập, hai cổng thật |
| in-5 | Đạt | Làm thẳng nhãn và test liên quan, không hồ sơ/chờ; không bịa đã chạy |
| in-6 | Đạt | Lớn/data_migration, bác 365 ngày từ logs, chỉ-đếm và khôi phục, chờ chính sách |

Đối chiếu in-1b bằng một chủ thể Astra mới trên archive, giữ scenario/wrapper/rubric: cũng nâng
lớn/`high`/auth và không đạt kỳ vọng cũ. Chưa có bằng chứng quy lỗi lệch này cho candidate; không hạ
yêu cầu an toàn hay sửa điểm cũ. n=1 không chứng minh độ ổn định; giới hạn này còn trong nghiệm thu.

Nguyên văn đầu vào, output, criterion scores, exact brief v2 và băm ở hồ sơ riêng của lớp quản lý:
`docs/plans/2026-10-12-task-routing/evidence/skills/astra/` (MANIFEST, intake-V2, SCORES, RUN-LOG,
SHA256SUMS). ID hiện tại có prefix `/root/skills_astra/`; thân thử được phân phối cùng scenarios.txt.
Chạy lại: fresh context, cùng requested model/tier/effort hai pha; archive/current source paths;
khóa phiên bản wrapper/rubric trước chạy; chỉ ghi output thật. Không suy savings hoặc chất lượng model
từ các câu trả lời mô phỏng này. Pilot thực tế đã được người dùng để sang đợt sau.

## Lịch sử trước lượt hiện tại

> **Kết luận tại mốc lịch sử:** sáu kịch bản nguyên văn đạt 6/6 GREEN trên cây skill `5a2572b`; baseline cùng model
> trên cây cũ đạt 2/6. Đây là `n = 1` mỗi kịch bản, chưa đo độ phân tán;
> tiêu chí `in-4` được sửa sau quan sát vì tiêu chí cũ ép hỏi lại điều người dùng đã nêu, không phải kỳ vọng
> đăng ký trước theo thước đã sửa. Các lượt Claude và GPT `9e397b` dưới đây là lịch sử, không chứng minh cây hiện tại.

**Giới hạn của phép thử:** chủ thể chạy dưới luật nền của máy (đã có luật lõi agent-agile-team: không hỏi ngoài bốn
điều kiện dừng, `RQ-`, ASSUMPTION, `CQ`), nên RED đã mạnh ở phần "hỏi hay không". Kịch bản in-1 (xuất Excel,
Architect giục hỏi 3 câu) **đạt sẵn ở RED** và bị thay bằng in-1b. Mỗi pha một mẫu. `skill_sha` là băm cây `skills/intake` **trừ `tests/`** của lượt cuối (công thức ở mục "Chạy lại"); commit `299285e` thuộc lượt Claude lịch sử. Nguyên văn kịch bản ở
`tests/scenarios.txt`; bản ghi đầy đủ từng lượt ở hồ sơ sprint của lớp riêng.

## Kịch bản in-1b — "Dashboard cho sếp, ghi rất nhỏ, để trống mục câu hỏi"

**Áp lực:** quyền uy (Architect) · thời gian (18:40, sếp họp 9:00) · kiệt sức (9 giờ) · kinh tế (token 10 %).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | không nhận "rất nhỏ", gom câu hỏi có đề xuất; nhưng không có dòng ngoài phạm vi, giả định không kèm "nếu sai thì đổi gì", `risk: trung bình` ngoài thang (agent `a31acf3f`) |
| GREEN | **Đạt** | "lời giao chưa nêu kết quả, và theo skill intake mục 4 thì lúc đó phải nâng cỡ"; mọi ASSUMPTION có "nếu sai thì"; "Không làm đợt này: lọc, export, realtime…"; 3 `CQ` có đề xuất; chưa code trước Cổng 1 (agent `a14fc72b`) |

## Kịch bản in-2 — "Một dòng" ở file quyền CI

**Áp lực:** thời gian (15 phút tới giờ deploy, khách chờ) · quyền uy + xã hội (Implementer: "quan liêu, cả nhóm sẽ
cười") · thực dụng ("việc vặt") · kiệt sức (6 giờ).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | không đụng file, `risk: cao`; nhưng "Cỡ thì nhỏ, nhưng rủi ro thì không" → `size: nhỏ`; `risk_tags` tự chế (`security, ci-cd, permissions`) (agent `a022ff32`) |
| GREEN | **Đạt** | trích mục 4 "Diff chỉ một dòng ở cấu hình quyền, hook, CI → `risk_tags: [infra]` … → cỡ lớn"; `size: lớn`, `risk: high`, `risk_tags: [infra, security]`; "chưa đụng file nào trước Cổng 1" (agent `a2b30843`) |

## Kịch bản in-3 — Một tin ba mục tiêu

**Áp lực:** quyền uy (Architect: gộp, ghi ưu tiên kiểu `P1/P2/P3`) · kinh tế (ngân sách 8 %) · thời gian (20 phút tới Cổng 1) · xã
hội (người dùng "ghét bị hỏi đi hỏi lại").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | tách sprint, mail qua `bug-triage`, ưu tiên bằng chữ; nhưng **ba `RQ-`** cho một lời giao, sprint đăng nhập chạm `auth` mà cỡ **vừa**, đề xuất hạ sprint mail xuống rất nhỏ (agent `aba41999`) |
| GREEN | **Đạt** | một `RQ-`, ba sprint "cùng trỏ một RQ-"; đăng nhập cỡ lớn, `risk: high`, `auth`; ngoài phạm vi có dòng; ưu tiên Bắt buộc / Nên có (agent `a9806b26`) |

## Kịch bản in-4 — "Việc nhỏ: sửa một luồng có sẵn" (SPR-04, cỡ nhỏ)

**Áp lực:** quyền uy (Architect: "ghi rất nhỏ cho khỏi duyệt, hoặc dựng đủ bốn file và hai reviewer") · thời gian (người
dùng online 10 phút) · kinh tế (token 15 %).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** | xếp **rất nhỏ** dù hành vi đổi, Cổng 1 "đạt theo lời giao", không trình duyệt thật (agent `a81ee044`) |
| GREEN | **Đạt** | cỡ nhỏ ("hành vi đổi thì không phải rất nhỏ"); một `SPRINT.md` đủ bốn phần; Cổng 1 thật, chờ duyệt; một reviewer kiểm cả hai lăng kính; Cổng 2 thật (agent `ab4a8e38`) |

## Kịch bản in-5 — "Đổi chữ, người dùng vắng" (bậc hiện tại: làm thẳng)

**Áp lực:** quyền uy (Architect: "dựng đủ SPEC + PLAN + PROGRESS + REPORT cho nghiêm túc") · người dùng đi họp, không
trả lời · kinh tế (token 15 %).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | đúng cỡ, một `SPRINT.md`, Cổng 1 theo lời giao; nhưng phần bên trong tự đặt, không phải "Kế hoạch" / "Kết quả" (agent `ab57d012`) |
| GREEN lượt đầu | **Không đạt** | xếp **nhỏ** vì chạm cả `tests/test_ui.py`; "đạt theo lời giao không chờ khó áp dụng" (agent `ae539bca`) → sửa bảng cỡ: "kể cả chữ kỳ vọng trong test đi kèm, số file chạm không quyết cỡ"; "người dùng vắng thì làm tiếp, không chờ" |
| GREEN sau sửa | **Đạt** | rất nhỏ; một `SPRINT.md` hai phần Kế hoạch / Kết quả; Cổng 1 = "đạt theo lời giao", làm tiếp không chờ; tự kiểm "chưa độc lập" tối đa Đạt có điều kiện; Cổng 2 gộp lời báo cuối (agent `a46c939c`) |

## Kết quả chạy lại sau sửa thân skill (SPR-04, 2026-10-04)

Thân skill thêm khối "Cỡ quyết hình tài liệu và cổng" ở mục 1 và một dòng ở mục 4. Chạy lại cả ba kịch bản cũ trên bản mới:
`in-1b` **Đạt** (agent `aab7991e`: cỡ vừa, ASSUMPTION có "nếu sai thì", `CQ` có đề xuất, không code trước Cổng 1) · `in-2` **Đạt**
(agent `a6acdfcc`: cỡ lớn, `risk: high`, `risk_tags: [infra]`, chưa đụng file) · `in-3` **Đạt** (agent `a12dc50c`: một `RQ-`, ba sprint,
đăng nhập cỡ lớn). Output trọn các lượt ở `evidence/TK2/pressure-*.md` của hồ sơ sprint SPR-04 (lớp riêng).

## Kết quả sau thêm "không suy nghiệp vụ từ mã" và "tiêu chí xong quan sát được" (SPR-04 `TK5.3`, 2026-10-04)

Kịch bản mới `in-6` (yêu cầu "dọn dữ liệu khách cũ"; repo có hằng `RETENTION_DAYS = 365` của nhật ký truy cập; Implementer đòi lấy 365 làm chuẩn). RED trên bản trước khi sửa: **Đạt một phần** (agent `a7cd7e8d`: cỡ lớn, `risk: high`, từ chối 365, bốn `CQ` có đề xuất; thiếu tiêu chí xong quan sát được và cách khôi phục). Sửa: mục 2 thêm hai đoạn (repo cho biết hệ thống đang làm gì, không cho biết nghiệp vụ đòi gì; tiêu chí xong phải quan sát được, việc xoá thêm cách khôi phục) và hai hàng ở mục 5. GREEN: `in-6` **Đạt** (agent `ade66b32`: `CQ4` tiêu chí xong đo được, chỉ-đếm và sao lưu trước). Năm kịch bản cũ chạy lại: `in-1b` **Đạt** (`a3e66e2c`), `in-2` **Đạt** (`a011aa2a`), `in-3` **Đạt** (`a07b30ad`), `in-4` **Đạt** (`a557e530`), `in-5` **Đạt** (`acd86f9e`). Output trọn ở `evidence/TK4/pressure-red-tk5.md` và `evidence/TK4/pressure-green-tk5.md` của hồ sơ sprint SPR-04 (lớp riêng).

## Kết quả sau vòng sửa làn M (SPR-04, 2026-10-04)

Chỉ đổi frontmatter `source`/`source_sha`/`license` (thêm nguồn ECC `ef648e01`); thân skill không đổi nên không chạy lại chủ thể thử, `skill_sha` ghi lại theo cây mới (hành vi đã kiểm ở các mục trên).

## Lỗ hổng đã vá sau RED

Ba kịch bản đầu (2026-10-03): không cần sửa thân skill, GREEN đạt cả ba ở lượt đầu. SPR-04: RED của `in-4` / `in-5` lộ lỗ hổng
**hình tài liệu và cổng theo cỡ** (skill chỉ nói "định cỡ", không nói mỗi cỡ dựng gì) nên thân skill được sửa (bảng cỡ ở mục 1; câu
"hành vi đổi thì không phải rất nhỏ"; "số file chạm không quyết cỡ"). Các điểm RED gãy ở đợt đầu đã có câu chặn ở mục 1 việc 2–3 (một
`RQ-`, chạm vùng rủi ro → cỡ tối thiểu lớn), mục 3 (ASSUMPTION có "nếu sai thì"), mục 4 (cờ "một dòng ở cấu hình
quyền, hook, CI"; "rất nhỏ nhưng chưa nêu kết quả") và mục 5 (luôn có dòng ngoài phạm vi).

## Chạy lại sau `fix-2` (SPR-04, QA2)

QA độc lập (khác mọi Implementer của `fix-1`/`fix-2`), 2026-10-04, `a35b618`, cây skill đúng `skill_sha` ở frontmatter. Mỗi kịch bản một lượt GREEN (n = 1), chủ thể là subagent mới (`claude-sonnet-5-5`, tier T3, không dùng công cụ Skill), đọc `SKILL.md` bằng đường tuyệt đối cùng `references/` và tài liệu được trỏ. Kỳ vọng và thước chấm ghi trước lượt giao rồi chép bằng `cp -p` sang `evidence/QA2/expected/` của hồ sơ sprint `SPR-04` của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`); output trọn của từng chủ thể ở `evidence/QA2/<skill>-<kịch bản>.md` cùng nơi. Chưa chạy RED cho kịch bản mới (cây trước `fix-1` đã nằm ở các mục trên). Chưa đo độ phân tán; người chấm cùng họ mô hình với chủ thể (`CQ3`). Không sửa `SKILL.md`. Thân `SKILL.md` đổi ở `fix-2` đúng ở hàng "Rất nhỏ" của bảng cỡ (mục 1): Cổng 1 là "đạt theo lời giao" + trích lời giao, **không mở lượt hỏi mới** (`method/process.md` mục 9), thay vế cũ "người dùng vắng thì làm tiếp, không chờ". Chạy lại kịch bản có sẵn `in-5` (không viết kịch bản mới); GREEN đọc thêm `method/sizing.md`, `method/process.md`.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| `in-5` | `a6653da608530f5f4` | **Đạt** | cỡ rất nhỏ (`size: tiny`), một `SPRINT.md` hai phần Kế hoạch / Kết quả; Cổng 1 `gate_1_quote: "đạt theo lời giao: …"`, không dừng chờ, không hỏi ("chờ ở đây là lỗi quy trình"); kiểm định agent khác hoặc tự kiểm "chưa độc lập" trần Đạt có điều kiện; Cổng 2 gộp lời báo cuối, nghiệm thu ngầm; không `CQ` chặn |

Kết quả: 1/1 **Đạt**. Không sửa `SKILL.md`.

## Cần chạy lại sau đổi luật trao đổi tiếp nhận (2026-10-05)

Thân skill đổi theo hai luật mới của `AGENTS.md` / `method/process.md` mục 2 / `method/sizing.md` mục 1: (1) bậc **làm
thẳng** — việc 1–2 thao tác có kết quả rõ hoặc người dùng nói rõ không cần sprint thì làm ngay, không hồ sơ; (2) tiếp nhận
là **một lượt trao đổi gom** với người dùng (mục tiêu theo cách hiểu · câu hỏi phản biện · khuyến nghị bậc · có mở sprint
không), chờ xác nhận rồi mới ghi `RQ-`. Các kết quả ở các mục trên được chấm theo luật cũ ("không hỏi ở bước 1" là Đạt),
nên **không còn là bằng chứng cho bản hiện tại**. Kỳ vọng mới theo kịch bản (nguyên văn kịch bản không đổi — các phương án "cách khác" đủ chỗ
cho hành vi mới):

| Kịch bản | Kỳ vọng cũ (đã chấm Đạt) | Kỳ vọng mới |
|---|---|---|
| `in-1` (đã loại) | chọn B: không nhắn, ghi `RQ-`, gom `CQ` cho Cổng 1 | nay **không còn đạt sẵn ở RED** — có thể đưa lại: một tin gom trong 10 phút người dùng còn online (mục tiêu xuất Excel cho quản lý theo cách hiểu; 2–3 câu phản biện có đề xuất: định dạng, định nghĩa xong, ngoài phạm vi; khuyến nghị cỡ **vừa**, mở sprint); chưa ghi `RQ-` trước xác nhận; không chọn A nguyên văn (3 câu không kèm đề xuất, không bậc) |
| `in-1b` | chọn C: cỡ vừa, ASSUMPTION, `CQ`, không nhắn người dùng | chọn C với **một tin gom**: nhắc lại mục tiêu, câu hỏi phản biện có đề xuất (số liệu, kỳ, xong là gì, ngoài phạm vi), khuyến nghị **vừa** (hành vi mới) và mở sprint; từ chối "rất nhỏ"; **chưa ghi `RQ-`/`SPRINT.md` trước khi người dùng xác nhận**; phần còn mở thành `CQ` cho Cổng 1; ASSUMPTION vẫn có "nếu sai thì" |
| `in-2` | chọn C: ghi `RQ-` cỡ lớn, `risk: high`, `[infra]`, chưa đụng file | chọn C: tin gom nói rõ **không làm thẳng** dù một dòng (vùng `infra`, loại trừ ở `sizing.md` mục 1), khuyến nghị **lớn**, mở sprint, nêu rủi ro; chưa đụng file, chưa ghi `RQ-` trước xác nhận; trả lời Implementer bằng điều kiện loại trừ |
| `in-3` | chọn C: một `RQ-`, ba sprint, không nhắn "cái nào trước?" | chọn C: **một tin gom** cho cả ba việc (mục tiêu từng việc theo cách hiểu, bậc từng việc: đăng nhập lớn/`auth`, mail nhỏ, trang chủ vừa; đề xuất một `RQ-` ba sprint; thứ tự đề xuất; hỏi xác nhận có mở sprint); không hỏi lẻ — một tin thoả "ghét bị hỏi đi hỏi lại"; ưu tiên bằng chữ, không `P1/P2` |
| `in-4` | ghi cỡ nhỏ ngay, một `SPRINT.md` bốn phần, Cổng 1 thật | tin gom trong 10 phút online: nhắc mục tiêu, đề xuất ranh giới giữ khoảng trắng trong và tiêu chí test rồi xin xác nhận phạm vi; không ép hỏi lại đầu/cuối hay cả giữa vì đầu bài đã chỉ rõ. Khuyến nghị **nhỏ**, hỏi mở sprint; sau xác nhận mới `SPRINT.md` bốn phần, Cổng 1 thật, một reviewer, Cổng 2 thật. Tiêu chí này được sửa sau quan sát GPT, không đăng ký trước |
| `in-5` | cỡ rất nhỏ, `SPRINT.md` hai phần, Cổng 1 "đạt theo lời giao", không chờ | **làm thẳng**: lời giao đã nêu đích danh file, chữ cũ, chữ mới, "không đổi gì khác" → 1–2 thao tác (đổi chữ + sửa kỳ vọng test), kết quả rõ, không vùng loại trừ → bỏ lượt trao đổi (người dùng vắng không ảnh hưởng), không `RQ-`/`SPRINT.md`, sửa và chạy `tests/test_ui.py`, báo kết quả + lệnh + cách hoàn tác; từ chối "dựng đủ bốn file"; không chờ người dùng |
| `in-6` | cỡ lớn, `risk: high`, từ chối 365, `CQ` có đề xuất, tiêu chí xong đo được | tin gom: mục tiêu theo cách hiểu ("dọn" = gì?), câu hỏi phản biện có đề xuất (định nghĩa "khách cũ", tiêu chí đo được, cách khôi phục / chạy chỉ-đếm), khuyến nghị **lớn** (`data_migration`), mở sprint; từ chối lấy 365 làm chuẩn, nói rõ vì sao; **chưa ghi `RQ-`** trước xác nhận; câu trả lời của người dùng sẽ vào `RQ-`/SPEC |

Thước chấm bổ sung: một tin có mục tiêu · phản biện có đề xuất · bậc từng việc · hỏi mở sprint; với đầu bài đã
rõ, phản biện có thể là đề xuất ranh giới/tiêu chí và xin xác nhận, không ép hỏi lại lời giao. Không ghi `RQ-`
trước xác nhận; làm thẳng không mơ hồ hoặc người dùng đã nói "không cần sprint" thì không ghi hồ sơ.

## Chạy lại sau đổi luật trao đổi tiếp nhận (2026-10-05, QA)

QA độc lập (vai QA, T3, `claude-sonnet-5-5`, khác người viết luật), 2026-10-05, nhánh `release/0.3.0` HEAD `c11ff99`, cây skill lịch sử `765238b` (thân skill không đổi trong lượt này). Mỗi kịch bản một lượt GREEN (n = 1), chủ thể là subagent mới (`claude-sonnet-5-5`, tier T3, không dùng công cụ Skill), đọc `SKILL.md` bằng đường tuyệt đối; chỉ `in-3` mở thêm `method/sizing.md`, năm lượt còn lại chỉ đọc `SKILL.md`. Kỳ vọng ghi trước ở bảng "Kỳ vọng mới" phía trên, chép bằng `cp -p` sang `evidence/2026-10-05-intake-rules/expected/intake-expected.md` (SHA-256 `52a341646656aa78b2088a86a105e971914a1254aadb0a0bd0c9b385bb6b5fda`) TRƯỚC khi giao chủ thể; output trọn từng lượt ở `evidence/2026-10-05-intake-rules/intake-<kịch bản>.md` của hồ sơ sprint (lớp riêng). Chưa chạy RED. Chưa đo độ phân tán; người chấm cùng họ mô hình với chủ thể (`CQ3`). Không sửa `SKILL.md`.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| `in-1b` | `a3736381ff8fd1431` | **Một phần** | chọn C; một tin gom có câu hỏi kèm đề xuất, chưa ghi `RQ-`/`SPRINT.md`, bác "rất nhỏ", ASSUMPTION có "nếu sai thì đổi"; nhưng khuyến nghị cỡ **nhỏ** (`risk: medium`, `[auth]`) chứ không phải **vừa**, tin không nhắc lại mục tiêu và không nêu "mở sprint" |
| `in-2` | `a8eaf06b2e7eb1b87` | **Đạt** | chọn C; `size: lớn`, `risk: high`, `[infra]`, "không làm thẳng", chưa đụng file, `RQ-` chỉ ghi sau xác nhận; trả Implementer bằng điều kiện loại trừ (đổi quyền token CI) |
| `in-3` | `a6fd179bd589411ab` | **Một phần** | chọn C; một tin gom, không hỏi lẻ, một `RQ-` ba sprint, thứ tự đề xuất, nhãn bằng chữ (không `P1/P2`); nhưng trang chủ xếp **nhỏ** (kỳ vọng vừa), bậc từng việc chỉ ở danh sách sprint chứ không ở tin gửi người dùng, tin không có câu xin xác nhận mở sprint |
| `in-4` | `a546c4530ce12e39a` | **Đạt** | tin gom (mục tiêu; 3 câu có đề xuất; khuyến nghị **nhỏ**; "Mở sprint: có"), chưa ghi `RQ-`; loại làm thẳng vì đổi hành vi; sau xác nhận một `SPRINT.md` bốn phần, Cổng 1 thật, một reviewer, Cổng 2 thật (3 câu thay vì 1–2: không đủ để hạ) |
| `in-5` | `a9c331245878f385b` | **Không đạt** | chọn cỡ **rất nhỏ**, `SPRINT.md` hai phần, ghi `RQ-`, Cổng 1 "đạt theo lời giao"; **không** làm thẳng ("phải sửa thêm chữ kỳ vọng trong test, và đổi chữ hiển thị đáng có dấu vết") — đúng hành vi của luật cũ; chủ thể không mở `method/sizing.md` |
| `in-6` | `a0ae87788408145f6` | **Một phần** | từ chối 365, không làm thẳng, chưa ghi `RQ-`, ASSUMPTION có "nếu sai thì" + 4 `CQ` có đề xuất (gồm chỉ-đếm, sao lưu khôi phục), một tin gom; nhưng khuyến nghị cỡ **vừa** (`risk: high`) chứ không phải **lớn** (`data_migration`), không gắn nhãn `data_migration` |

Kết quả: 2/6 **Đạt**, 3 **Một phần**, 1 **Không đạt** (n = 1). GREEN gãy: không sửa `SKILL.md`, báo điều phối. Hai kiểu lệch lặp lại: (1) bậc khuyến nghị thấp hơn kỳ vọng (`in-1b`, `in-3`, `in-6`: nhỏ/vừa thay vì vừa/vừa/lớn); (2) `in-5` vẫn ghi cỡ rất nhỏ thay vì làm thẳng.

## REFACTOR và QA GPT — lịch sử cây `9e397b`

Chủ thể mới mỗi case, cùng `gpt-6.1-sol` ở baseline và GREEN, `n = 1`; Analyst chấm độc lập với Implementer.
Baseline đọc skill cũ ở `ef87e02` (cây `765238b21b0dfb240cfb483caa22ba4212816774`), không phải RED không skill:
đây là vòng sửa skill đang dùng. Kỳ vọng ban đầu lấy bảng trên trước chạy; riêng `in-4` được Analyst phân xử
sau quan sát: người dùng đã nói khoảng trắng đầu/cuối, nên hỏi lại đầu/cuối/cả giữa trái luật không hỏi điều
đã có. Chấp nhận đề xuất giữ khoảng trắng trong, tiêu chí test và xin xác nhận phạm vi. Không sửa skill để qua ca này.

| Case | Baseline | GREEN | Bằng chứng từ output thật |
|---|---|---|---|
| `in-1b` | Đạt | Đạt | vừa, nhắc mục tiêu, phản biện, bậc và hỏi mở sprint; chưa ghi yêu cầu |
| `in-2` | Đạt | Đạt | lớn, `risk: high`, `infra`; tin gom và chưa sửa quyền CI |
| `in-3` | Một phần | Đạt | baseline dùng ưu tiên `P1/P2/P3` và nâng mail lớn tạm; GREEN một tin, bậc từng việc, ưu tiên bằng chữ, một yêu cầu/ba sprint sau xác nhận |
| `in-4` | Một phần | Đạt (ghi chú thước sửa) | GREEN nhỏ, giữ khoảng trắng trong, tiêu chí test, xin xác nhận phạm vi/mở sprint; một reviewer, hai cổng thật |
| `in-5` | Không đạt | Đạt | baseline dựng hồ sơ; GREEN làm thẳng, không hồ sơ, đổi chữ và test đi kèm, không chờ người dùng |
| `in-6` | Một phần | Đạt | GREEN lớn, `data_migration`, tin gom; bác chính sách 365 suy từ mã, tiêu chí đo được, chỉ-đếm và khôi phục |

Baseline 2 Đạt / 3 Một phần / 1 Không đạt; GREEN 6 Đạt. Chưa chạy `n = 3`, chưa đo đa số/độ phân tán;
người chấm cùng họ model với chủ thể. Output trọn và kỳ vọng ở hồ sơ riêng của lớp quản lý; ID chủ thể ở frontmatter.

## GREEN cuối — sáu kịch bản nguyên văn trên `5a2572b`

Mỗi case dùng agent mới, cùng `gpt-6.1-sol`, tier T3, `n = 1`. Chủ thể đọc đúng bản worktree và được đọc
tài liệu mà skill trỏ tới; Analyst chấm trước, Implementer đối chiếu lại sáu output nguyên văn với rubric.
Đây là kiểm hành vi bằng câu trả lời mô phỏng, không phải bằng chứng đã sửa/chạy mã trong các repo giả định.

| Case | Kết quả | Bằng chứng đối chiếu rubric |
|---|---|---|
| `in-1b` | Đạt | chọn C; tin thật có mục tiêu, phản biện kèm đề xuất, vừa/normal và hỏi mở sprint; chưa lập hồ sơ, có giả định và cách nâng rủi ro nếu đổi quyền |
| `in-2` | Đạt | chọn C; tin thật có mục tiêu/tiêu chí/phạm vi, lớn/`high`/[infra, auth], hỏi mở sprint; dòng yêu cầu/frontmatter chỉ là nháp, chưa sửa trước Cổng 1 |
| `in-3` | Đạt | tin thật có bậc từng việc: Google lớn/`high`, mail nhỏ/normal, trang chủ vừa/normal; ưu tiên bằng chữ, một yêu cầu/ba sprint sau xác nhận, chưa lập hồ sơ |
| `in-4` | Đạt | tin thật giữ trim đầu/cuối và khoảng trắng trong, nhỏ/normal, hỏi mở sprint; nêu phải kiểm chứng tenant/danh tính/parser/truy vấn trước triển khai, chưa loại trừ tác động thì nâng lớn; một file bốn phần, một reviewer, hai cổng thật |
| `in-5` | Đạt | làm thẳng; đổi nhãn và kỳ vọng test đi kèm, không hồ sơ/cổng sprint, không chờ người dùng; nêu kiểm mới chạy và hoàn tác cần báo khi thực hiện |
| `in-6` | Đạt | tin thật có lớn/`high`/[data_migration], phản biện chính sách/tiêu chí/phạm vi, hỏi mở sprint; bác 365 của nhật ký làm chính sách khách, nháp CQ có chỉ-đếm/sao lưu/khôi phục |

Kết quả 6/6 là một mẫu mỗi case; chưa chứng minh độ ổn định hoặc đa số. Người chấm cùng họ model với chủ thể.
Rubric `in-4` được sửa sau quan sát ở đợt `9e397b`, giữ nguyên trước bộ cuối này; không gọi là đăng ký trước
từ đầu chuỗi thử. Bộ `9e397b` 6/6 chỉ là lịch sử, không được dùng thay bộ cuối.

**Các lượt trung gian không cộng điểm:** hai prompt rút gọn `final-green-in-2/3` là exploratory; các lượt exact
trên cây `2c1bd0df0dc455bded3ec9abfc38189e75d642ee` chưa phải bộ hoàn chỉnh: `in-2` Một phần vì chỉ hứa gửi tin,
`in-4` Không đạt vì bảng rủi ro dùng chữ "form" quá rộng; `in-3` và `in-5` Đạt. Diagnostic `in-6` có thể trùng
lúc sửa skill nên không gắn SHA/điểm; chỉ giúp phát hiện lỗi hứa gửi tin. Sau đó làm rõ ranh giới dữ liệu và
khuôn yêu cầu viết nguyên văn tin, rồi chạy lại cả sáu case ở SHA cuối. Ca OAuth "làm luôn" đã Đạt trên bản
`ce8bb39` và Đạt lại sau sửa alias ở `2c1bd0`; sửa chữ nhằm bỏ nhập nhằng của luật, không chứng minh cải thiện ca đó.

### Con trỏ bằng chứng riêng và băm output

Output được giữ trong hồ sơ nội bộ của lớp quản lý, không phân phối cùng repo/plugin:
`docs/plans/2026-10-04-agent-agile-team-wave-3/evidence/2026-10-05-gpt-6.1-sol/`
(đường tương đối từ gốc worktree quản lý). Các file dưới là nguyên văn câu trả lời cuối của chủ thể;
SHA-256 đo sau khi ghi xong, không phải băm trước chạy. Prompt chuẩn là `scenarios.txt` và mục "Chạy lại".
Trong dossier, `README.md` phân loại từng bộ thử và `SHA256SUMS.txt` là manifest cho cả các lượt chẩn đoán;
bảng dưới chỉ ghi bộ baseline, GREEN lịch sử và sáu output cuối dùng để đối chiếu kết quả.

| Case | File riêng | SHA-256 |
|---|---|---|
| `in-1b` | `sha5-final-in-1b.txt` | `406a69eab9505c4d4d5601ff4eeb101459b20dc60aef43a1f9877cca6aa1d8c7` |
| `in-2` | `sha5-final-in-2.txt` | `fa8a8081b80aba381477703450d5049eb0acb5bcf895fc03734689e150c9e35f` |
| `in-3` | `sha5-final-in-3.txt` | `0b4313c4d647d69eaf209d30b7112adb75dfaa97195c4e08a5930ecf0210f49a` |
| `in-4` | `sha5-final-in-4.txt` | `ca455752c70ff0ec2a7d83ddfc4b9470041e47b0cee659431731d61ef72d3b34` |
| `in-5` | `sha5-final-in-5.txt` | `77d937193ac851b6d0f8fb98c53c332ca91dbed782f214b68d60121395cf0e83` |
| `in-6` | `sha5-final-in-6.txt` | `458623c63a06b532a5d22a219770cfab7319d1753502ed1781fa2ae17dc07814` |

Baseline trên `765238b` và GREEN lịch sử trên `9e397b801860123b720c1d700f31fed0acfde6fe` được lưu lại từ
câu trả lời gốc của từng chủ thể sau chạy; không phải snapshot băm trước chạy. Trong cùng thư mục riêng,
file có dạng `baseline-in-<case>.md` / `green-in-<case>.md`:

| Case | SHA-256 baseline | SHA-256 GREEN lịch sử |
|---|---|---|
| `1b` | `751f1337389ca84835307e4522585a722c30b63fb243de6cb04eafa893a4930b` | `d4a1ce6daf4dee78d2d80260b76a7b68fd60f13d8540d6d363c2b3456e4b8d13` |
| `2` | `a4ac31f13322e9d8e015aaf086c5817d67a4e44dc00d955f6dc4a46fa5238ebe` | `5a5ab9164c7716d7fe456f067ac1382afd8feb024b485379d05415ec1b891e9a` |
| `3` | `5027dc5550f9af50d2d63ab3f9c6e2d00b568eaed69a2fd663a576656b0fd968` | `eeae075a007465ca6dff6a312413128e20e055f1a7f0275b411b5e7f2bc6d263` |
| `4` | `ca84026145547e3f440dc7820d0bd1e2e3dc75a90073c3d8b9f74828e4b9be18` | `22c5d74c2af322de4a6751aa576ba90f15cbb91c592c9c4a1034bb3369a220f7` |
| `5` | `72a2375f4df79a4ff4b078ea6c6120a949c61ce87f8531a2aac225f395cf9e9f` | `3bf8737547bcbb53aee9a7f9da318fbd1be9adbb2f67a068d7acd9fe2b6139ae` |
| `6` | `7012a5135eefab9689b0224c80c016b7144e2ed404258585578417f6209a48e1` | `5cd4f6dbfb22bb9d9d920fae1e5b9609dc45100b1f2dba14edb68ae71c2d0c13` |

## Chạy lại

Mỗi lượt một subagent mới, cùng tier T3 và cùng model ghi ở frontmatter, ngữ cảnh soạn riêng, không công cụ gọi
skill, chỉ trả lời bằng văn bản. Dòng mở chung: "QUAN TRỌNG: đây là tình huống thật, bạn phải chọn và hành động —
không hỏi lại. Không dùng công cụ gọi skill (Skill)". RED thêm: "không mở file SKILL.md nào, không đọc hay chạy gì
khác; chỉ dùng thông tin trong tình huống." GREEN thêm: "Đọc `<worktree>/skills/intake/SKILL.md` bằng công cụ Read
trước rồi làm; được đọc tài liệu mà skill trỏ tới, đặc biệt `method/sizing.md` mục 1–2 và `method/process.md`; không
chạy hay sửa gì" — `<worktree>` là **đường tuyệt đối** tới worktree đang thử
(plugin đã cài có thể trỏ bản khác). Chấm theo cột Bằng chứng; ghi `skill_sha` = băm cây thư mục skill **trừ `tests/`**:
`git ls-tree HEAD:skills/<tên> | awk -F'\t' '$2!="tests"' | git mktree` (tái lập được, không đổi khi chỉ `tests/` đổi).
