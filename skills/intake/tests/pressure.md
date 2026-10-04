---
skill: intake
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (all runs, same scenario text)
tier: T3
skill_sha: f200a6b19d3677e20924742be209a7e34531a3dd
date: 2026-10-04
result: 6/6 GREEN pass; RED on the 3 new scenarios (in-4, in-5, in-6) 0/3 pass (1 fail, 2 partial); QA2 after fix-2 in-5 rerun GREEN pass (n = 1)
agent_ids:
  red: {in-1: adcce776b996a5503, in-1b: a31acf3fa7bdf1433, in-2: a022ff32b37ff8613, in-3: aba419997dc10a7d5, in-4: a81ee044a2949cb9c, in-5: ab57d0120cba4a923}
  green: {in-1b: aab7991e3533e7484, in-2: a6acdfcc653e402ac, in-3: a12dc50c810907a91, in-4: ab4a8e38f3c55f196, in-5: a46c939c2caada298}
  green_first_pass_superseded_by_skill_edit: {in-1b: a8fe28dee1ef7b418, in-2: aab856b26c612a782, in-3: a23c17613f034b4a3, in-4: a3f64f47e6f21cccc, in-5: ae539bca672377843}
---

# Thử áp lực — intake

> **Kết luận:** không có skill, chủ thể vẫn không hỏi lẻ và không code trước Cổng 1 (luật lõi đã dạy), nhưng gãy ở
> phần riêng của skill: chạm vùng rủi ro mà vẫn xếp cỡ nhỏ/vừa, ghi nhiều `RQ-` cho một lời giao, đề xuất **hạ**
> cỡ, giả định không kèm "nếu sai thì đổi gì", thiếu dòng ngoài phạm vi. Có skill thì đạt cả ba, trích đúng mục 1
> và mục 4. Không cần REFACTOR.

**Giới hạn của phép thử:** chủ thể chạy dưới luật nền của máy (đã có luật lõi agent-agile-team: không hỏi ngoài bốn
điều kiện dừng, `RQ-`, ASSUMPTION, `CQ`), nên RED đã mạnh ở phần "hỏi hay không". Kịch bản in-1 (xuất Excel,
Architect giục hỏi 3 câu) **đạt sẵn ở RED** và bị thay bằng in-1b. Mỗi pha một mẫu. `skill_sha` là băm cây `skills/intake` **trừ `tests/`** lúc chạy (commit `299285e`; công thức ở mục "Chạy lại"). Nguyên văn kịch bản ở
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

## Kịch bản in-5 — "Việc rất nhỏ: đổi chữ, người dùng vắng" (SPR-04, cỡ rất nhỏ)

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

## Chạy lại

Mỗi lượt một subagent mới, cùng tier T3 và cùng model ghi ở frontmatter, ngữ cảnh soạn riêng, không công cụ gọi
skill, chỉ trả lời bằng văn bản. Dòng mở chung: "QUAN TRỌNG: đây là tình huống thật, bạn phải chọn và hành động —
không hỏi lại. Không dùng công cụ gọi skill (Skill)". RED thêm: "không mở file SKILL.md nào, không đọc hay chạy gì
khác; chỉ dùng thông tin trong tình huống." GREEN thêm: "Đọc `<worktree>/skills/intake/SKILL.md` bằng công cụ Read
trước rồi làm; ngoài file đó không đọc hay chạy gì khác" — `<worktree>` là **đường tuyệt đối** tới worktree đang thử
(plugin đã cài có thể trỏ bản khác). Chấm theo cột Bằng chứng; ghi `skill_sha` = băm cây thư mục skill **trừ `tests/`**:
`git ls-tree HEAD:skills/<tên> | awk -F'\t' '$2!="tests"' | git mktree` (tái lập được, không đổi khi chỉ `tests/` đổi).
