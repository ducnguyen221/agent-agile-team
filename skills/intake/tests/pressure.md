---
skill: intake
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (all runs, same scenario text)
tier: T3
skill_sha: 5127554a782b7cff1983c26828dee9bc68d22b35
date: 2026-10-03
result: 3/3 GREEN pass; RED 0/3 pass (3 partial) after replacing 1 scenario that passed at RED
agent_ids:
  red: {in-1: adcce776b996a5503, in-1b: a31acf3fa7bdf1433, in-2: a022ff32b37ff8613, in-3: aba419997dc10a7d5}
  green: {in-1b: a14fc72b8a4f42693, in-2: a2b308432021be271, in-3: a9806b269aa1dba8a}
---

# Thử áp lực — intake

> **Kết luận:** không có skill, chủ thể vẫn không hỏi lẻ và không code trước Cổng 1 (luật lõi đã dạy), nhưng gãy ở
> phần riêng của skill: chạm vùng rủi ro mà vẫn xếp cỡ nhỏ/vừa, ghi nhiều `RQ-` cho một lời giao, đề xuất **hạ**
> cỡ, giả định không kèm "nếu sai thì đổi gì", thiếu dòng ngoài phạm vi. Có skill thì đạt cả ba, trích đúng mục 1
> và mục 4. Không cần REFACTOR.

**Giới hạn của phép thử:** chủ thể chạy dưới luật nền của máy (đã có luật lõi agent-agile-team: không hỏi ngoài bốn
điều kiện dừng, `RQ-`, ASSUMPTION, `CQ`), nên RED đã mạnh ở phần "hỏi hay không". Kịch bản in-1 (xuất Excel,
Architect giục hỏi 3 câu) **đạt sẵn ở RED** và bị thay bằng in-1b. Mỗi pha một mẫu. `skill_sha` là cây
`skills/intake` ở commit `299285e` lúc chạy (`git rev-parse 299285e:skills/intake`). Nguyên văn kịch bản ở
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

## Lỗ hổng đã vá sau RED

Không cần sửa thân skill: GREEN đạt cả ba ở lượt đầu. Các điểm RED gãy đã có câu chặn ở mục 1 việc 2–3 (một
`RQ-`, chạm vùng rủi ro → cỡ tối thiểu lớn), mục 3 (ASSUMPTION có "nếu sai thì"), mục 4 (cờ "một dòng ở cấu hình
quyền, hook, CI"; "rất nhỏ nhưng chưa nêu kết quả") và mục 5 (luôn có dòng ngoài phạm vi).

## Chạy lại

Mỗi lượt một subagent mới, cùng tier T3 và cùng model ghi ở frontmatter, ngữ cảnh soạn riêng, không công cụ gọi
skill, chỉ trả lời bằng văn bản. Dòng mở chung: "QUAN TRỌNG: đây là tình huống thật, bạn phải chọn và hành động —
không hỏi lại. Không dùng công cụ gọi skill (Skill)". RED thêm: "không mở file SKILL.md nào, không đọc hay chạy gì
khác; chỉ dùng thông tin trong tình huống." GREEN thêm: "Đọc `<worktree>/skills/intake/SKILL.md` bằng công cụ Read
trước rồi làm; ngoài file đó không đọc hay chạy gì khác" — `<worktree>` là **đường tuyệt đối** tới worktree đang thử
(plugin đã cài có thể trỏ bản khác). Chấm theo cột Bằng chứng; ghi `skill_sha` = `git rev-parse HEAD:skills/intake`
lúc chạy.
