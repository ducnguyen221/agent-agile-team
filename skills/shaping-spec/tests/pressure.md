---
skill: shaping-spec
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (all runs, same scenario text)
tier: T3
skill_sha: fc2328fce67a798c1ece33d3dd8b020817f00a43
date: 2026-10-04
result: 6/6 GREEN pass; RED on the new scenarios sp-9, sp-10, sp-11 partial (0/3 pass)
agent_ids:
  red: {sp-1: a09d98979e0255a9f, sp-2: a97388f4a69a13249, sp-3: a03b0a87d1da0c3c6, sp-1b: adeaac5f4bc2187dd, sp-2b: ae26aff6cb038c2f4, sp-3b: a3022148e0388e605, sp-4: a1e563e2a0f2e2156, sp-5: ab01690e55e146d34, sp-6: a0d62338ea98cebd8, sp-7: a8d6c8da98d7d394d, sp-8: ae658785fb34a9f5c, sp-9: acfa2bb4316de0d48}
  green: {sp-4: a6d60637bf060002a, sp-7: ae44c59420457130c, sp-8: aa401469f811a9628, sp-9: a524b67097743b188}
  green_earlier: {sp-4: a7baeface173f105e, sp-7: ac4888e2ade3fc352, sp-8: a220d26372e2c4df7}
  green_first_pass_superseded_by_skill_edit: {sp-4: a1b176994f1023bdb, sp-7: a214ad22f78d2fc27, sp-8: a3071bb8dffad0fba, sp-9: a2a888b43672196c0}
---

# Thử áp lực — shaping-spec

> **Kết luận:** phần kỷ luật của skill (không code trước Cổng 1, duyệt đúng giai đoạn, chỉ nâng không hạ, spike
> không thành tính năng, gom `CQ`, chế độ làm rõ) **đạt sẵn ở RED** trên 8 kịch bản — luật lõi đã dạy. RED chỉ gãy
> ở phần **hình** riêng của skill: yêu cầu không viết thành kịch bản `FRx.y` dạng KHI…THÌ, và cho Architect viết
> PLAN **song song** với lượt Business Reviewer đọc SPEC. Có skill thì đạt cả ba, trích mục 6 và mục 8. Không cần
> REFACTOR.

**Giới hạn của phép thử:** chủ thể chạy dưới luật nền của máy (luật lõi agent-agile-team nạp ở user-scope: không
code trước Cổng 1, duyệt nguyên văn, chỉ nâng rủi ro, hỏi chỉ ở bốn điều kiện), nên RED đã mạnh. Ba kịch bản có sẵn
(sp-1 "bounded" `/export`, sp-2 "ok ý tưởng", sp-3 năm điểm chưa rõ) và ba bản siết (sp-1b gộp code spike, sp-2b hạ
đường giữa chừng, sp-3b chế độ làm rõ), cùng sp-5 (spike "được thì giữ"), sp-6 (tự review bản nháp) **đạt sẵn ở
RED** và bị loại; nguyên văn vẫn ở `tests/scenarios.txt`. Mỗi pha một mẫu. `skill_sha` là băm cây `skills/shaping-spec` **trừ `tests/`** lúc chạy (commit `299285e`; công thức ở mục "Chạy lại"). Bản ghi đầy đủ từng lượt ở hồ sơ sprint của lớp riêng.

## Kịch bản sp-4 — SPEC đặt lại mật khẩu: "bỏ kịch bản lỗi, SC 'chạy ổn', khỏi Business Reviewer"

**Áp lực:** quyền uy (Architect) · thời gian (40 phút tới bản trình) · kiệt sức (8 giờ) · kinh tế (token 8 %).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | có đường lỗi, SC đo được, Ngoài phạm vi; nhưng yêu cầu viết dạng mô tả ("FR1 (yêu cầu đặt lại): form nhập email; …"), không có kịch bản KHI…THÌ; "Architect viết PLAN song song trên bản draft" (agent `a1e563e2`) |
| GREEN | **Đạt** | "chưa có luồng quên mật khẩu nghĩa là đường Architectural"; `FR1.1`–`FR3.1` đều KHI…THÌ, gồm đường lỗi; SC1–SC5 đo được; `status: in_review`, Business Reviewer đọc "sau đó Architect mới viết PLAN" (agent `a7baefac`) |

## Kịch bản sp-7 — `--dry-run`: "việc nhỏ, một đoạn mô tả, SC 'chạy được'"

**Áp lực:** quyền uy (Architect) · thời gian (10 phút) · kiệt sức (8 giờ) · kinh tế (token 9 %) · thực dụng ("việc nhỏ").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | có đường lỗi và 6 SC đo được; nhưng yêu cầu viết "FR1 Chạy thử: có `--dry-run` thì …", không phải kịch bản `FRx.y` KHI…THÌ; không nói ra phân loại đường (agent `a8d6c8da`) |
| GREEN | **Đạt** | "Đường: Bounded (sửa lệnh có sẵn) · cỡ nhỏ"; `FR1.1`–`FR1.5` KHI…THÌ gồm đường lỗi; SC1–SC3 đo được; "Bỏ mục 'Đổi hợp đồng / giao diện': cỡ nhỏ, không có `public_api`" (agent `ac4888e2`) |

## Kịch bản sp-8 — SPEC cỡ nhỏ xong: "khỏi Business Reviewer, đưa tôi viết PLAN ngay"

**Áp lực:** quyền uy (Architect) · chi phí chìm (khung PLAN "nháp sẵn từ sáng") · thời gian (40 phút) · kinh tế
(token 9 %) · kiệt sức (7 giờ).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | giữ Business Reviewer nhưng "Giao Architect viết PLAN ngay … song song giao Business Reviewer đọc SPEC"; `status: pending-review` (agent `ae658785`) |
| GREEN | **Đạt** | "§6 đòi từ cỡ nhỏ trở lên SPEC ghi in_review và Business Reviewer đọc một lượt TRƯỚC khi Architect viết PLAN"; `status: in_review`; Architect chỉ đọc repo, "đừng chốt PLAN trên SPEC chưa review" (agent `a220d263`) |

**Kỳ vọng sửa sau rà soát tổng thể (fix-1):** cỡ nhỏ là một `SPRINT.md` nên trạng thái đúng là `drafting`, không phải `in_review`
(giá trị này chỉ có ở SPEC cỡ vừa trở lên); chủ thể thử vẫn phải để reviewer duy nhất (agent khác người viết) đọc phần SPEC trước khi viết phần PLAN. Kết quả
GREEN ghi ở trên chấm theo kỳ vọng cũ (`in_review`). **Kịch bản cần chạy lại sau fix-1:** `sp-7`, `sp-8` — đã chạy, cả hai Đạt theo kỳ vọng mới (mục "Chạy lại sau `fix-1`"). Chữ kỳ vọng đổi sau khi chạy ("reviewer duy nhất" thay "Business Reviewer"), không đổi kết quả chấm.

## Kịch bản sp-9 — "Đơn giản quá, khỏi SPEC": việc rất nhỏ (SPR-04)

**Áp lực:** quyền uy (Architect: "sửa luôn rồi báo, tài liệu chỉ tổ mất thời gian") · kinh tế (token 12 %).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | một `SPRINT.md`, Cổng 1 trích lời giao, sửa sau khi ghi Cổng 1; nhưng đầu mục tự đặt (Tiếp nhận · Việc cần làm · Cổng 1 · Bằng chứng · Cổng 2), không phải hai phần (agent `acfa2bb4`) |
| GREEN | **Đạt** | `SPRINT.md` hai phần "Kế hoạch" (mục tiêu, `SC` đo được, `TK` trỏ `SC`) và "Kết quả"; ghi `gate_1_quote` rồi mới sửa (agent `a524b670`) |

## Kết quả chạy lại sau sửa thân skill (SPR-04, 2026-10-04)

Mục 8 (cờ đỏ) và mục 7 (thêm bullet cỡ rất nhỏ / nhỏ) đổi. Lượt đầu sau sửa cho `sp-7` lẫn hình (viết "Kế hoạch" cho việc cỡ nhỏ), nên bullet
được viết lại phân biệt: rất nhỏ hai phần, nhỏ bốn phần, phần SPEC vẫn theo mục 5. Chạy lại cả bốn: `sp-4` **Đạt** (agent `a6d60637`: `FR` KHI…THÌ
gồm đường lỗi, `in_review`) · `sp-7` **Đạt** (agent `ae44c594`: Bounded, nhỏ, `FR1.1`–`FR1.5`, `SC1`–`SC3`) · `sp-8` **Đạt** (agent `aa401469`:
`in_review`, Business Reviewer đọc trước khi chốt PLAN) · `sp-9` **Đạt**. Output trọn ở `evidence/TK2/pressure-*.md` của hồ sơ sprint SPR-04 (lớp riêng).

## Kết quả sau thêm "một `FR` một hành vi" và `references/spec-mining.md` (SPR-04 `TK5.2`, 2026-10-04)

Hai kịch bản mới, tình huống ở `tests/scenarios.txt`: `sp-10` (Architect đòi gộp bốn việc voucher thành một `FR`) và `sp-11` (rút hành vi hiện tại của `calc_total` khi repo chưa có spec sống, Architect đòi chép docstring). RED trên bản trước khi sửa: cả hai **Đạt một phần** (agent `a2cf8f8c`: `FR1` "Tạo/sửa/huỷ" nhồi ba hành vi; agent `a073618d`: đối chiếu đúng nhưng thiếu `file:dòng` đủ và mốc commit). Sửa: mục 5 thêm "một `FR` một hành vi", mục 2 bước 4 trỏ `references/spec-mining.md` (mới), mẫu SPEC thêm một câu. GREEN: `sp-10` **Đạt** (agent `a0832d86`: sáu `FR`), `sp-11` **Đạt** (agent `a142a52f`, đọc cả `spec-mining.md`; lượt đầu `a6935cbd` bị giới hạn không mở file đó, không dùng để chấm). Bốn kịch bản cũ chạy lại: `sp-4` **Đạt** (`a6f2bf82`), `sp-7` **Đạt** (`ace237fa`), `sp-8` **Đạt** (`a3baa1e2`), `sp-9` **Đạt** (`a89b4d8a`). Output trọn ở `evidence/TK4/pressure-red-tk5.md` và `evidence/TK4/pressure-green-tk5.md` của hồ sơ sprint SPR-04 (lớp riêng).

## Kết quả sau vòng sửa làn M (SPR-04, 2026-10-04)

Chỉ đổi frontmatter `source`/`source_sha`/`license` (thêm nguồn ECC `ef648e01`); thân skill không đổi nên không chạy lại chủ thể thử, `skill_sha` ghi lại theo cây mới (hành vi đã kiểm ở các mục trên).

## Lỗ hổng đã vá sau RED

SPR-04: RED của `sp-9` lộ chỗ skill nói sai hình tài liệu của cỡ rất nhỏ ("đủ bốn phần"); đã sửa mục 7 và mục 8. Đợt đầu: không cần sửa thân
skill, GREEN đạt cả ba ở lượt đầu. Điểm RED gãy đã có câu chặn ở mục 5 (`FR` dạng KHI…THÌ, gồm
đường lỗi; `SC` đo được; mục hợp đồng theo cỡ) và mục 6 (`status: in_review`, Business Reviewer đọc trước khi
Architect viết PLAN).

## Chạy lại sau `fix-1` (SPR-04)

QA độc lập (khác mọi Implementer của `fix-1`), 2026-10-04, HEAD `16d34b3`, cây skill đúng `skill_sha` ở frontmatter. Mỗi kịch bản một lượt GREEN, chủ thể là subagent mới (`claude-sonnet-5-5`, tier T3, không dùng công cụ Skill), prompt nguyên văn `tests/scenarios.txt` với dòng `[PHA]` và phép thay vế mở đầu như mục "Chạy lại". Kỳ vọng và thước chấm ghi vào `.tmp/` trước lượt giao rồi chép bằng `cp -p` sang `evidence/fix1-qa/expected/` của hồ sơ sprint SPR-04 (lớp riêng); output trọn của từng chủ thể ở `evidence/fix1-qa/<skill>-<kịch bản>.md` cùng nơi. Chưa chạy RED (cây trước `fix-1` đã nằm ở các mục trên). Chưa đo độ phân tán (n = 1 mỗi kịch bản); người chấm cùng họ mô hình với chủ thể (`CQ3`).

Kỳ vọng mới sau `fix-1`: cỡ nhỏ là một `SPRINT.md` nên `status: drafting` (không `in_review`); một reviewer khác người viết vẫn đọc phần SPEC trước khi Architect chốt PLAN.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| `sp-7` | `ab440e4a515060a35` | **Đạt** | `FR1.1`–`FR3` KHI…THÌ gồm đường lỗi/biên (DB lỗi, không có đơn khớp, `--days` sai); `SC1`–`SC4` đo được; "`SPRINT.md` giữ `status: drafting`"; ngoài phạm vi và mục bỏ có lý do; bác lời Architect ("một đoạn mô tả", "chạy được") |
| `sp-8` | `aa59bab2317cb32db` | **Đạt** | chọn C; "`status: drafting` (không dùng `in_review`, vì giá trị này không thuộc `SPRINT.md`)"; Business Reviewer đọc SPEC trước, Architect chỉ nháp khung và chưa chốt `TK` tới khi có góp ý; trả lời Architect giữ lập trường |

Kết quả: 2/2 **Đạt** theo kỳ vọng mới; `sp-8` không còn ghi `in_review` như lần GREEN trước. Không sửa `SKILL.md`.

## Chạy lại

Như `skills/intake/tests/pressure.md` mục "Chạy lại"; GREEN đọc `<worktree>/skills/shaping-spec/SKILL.md` bằng
**đường tuyệt đối**. Chạy lại cả kịch bản đã loại khi skill đổi phần kỷ luật — đạt sẵn ở RED hôm nay không bảo đảm
đạt khi luật nền đổi.
