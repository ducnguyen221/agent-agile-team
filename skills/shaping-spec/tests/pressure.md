---
skill: shaping-spec
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (all runs, same scenario text)
tier: T3
skill_sha: 92f0bb93c3ddc1f99f28f63e912bd408cefca610
date: 2026-10-03
result: 3/3 GREEN pass; RED 0/3 pass (3 partial) after replacing 8 scenarios that passed at RED
agent_ids:
  red: {sp-1: a09d98979e0255a9f, sp-2: a97388f4a69a13249, sp-3: a03b0a87d1da0c3c6, sp-1b: adeaac5f4bc2187dd, sp-2b: ae26aff6cb038c2f4, sp-3b: a3022148e0388e605, sp-4: a1e563e2a0f2e2156, sp-5: ab01690e55e146d34, sp-6: a0d62338ea98cebd8, sp-7: a8d6c8da98d7d394d, sp-8: ae658785fb34a9f5c}
  green: {sp-4: a7baeface173f105e, sp-7: ac4888e2ade3fc352, sp-8: a220d26372e2c4df7}
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
RED** và bị loại; nguyên văn vẫn ở `tests/scenarios.txt`. Mỗi pha một mẫu. `skill_sha` là cây `skills/shaping-spec`
lúc chạy (`git rev-parse 299285e:skills/shaping-spec`). Bản ghi đầy đủ từng lượt ở hồ sơ sprint của lớp riêng.

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

## Lỗ hổng đã vá sau RED

Không cần sửa thân skill: GREEN đạt cả ba ở lượt đầu. Điểm RED gãy đã có câu chặn ở mục 5 (`FR` dạng KHI…THÌ, gồm
đường lỗi; `SC` đo được; mục hợp đồng theo cỡ) và mục 6 (`status: in_review`, Business Reviewer đọc trước khi
Architect viết PLAN).

## Chạy lại

Như `skills/intake/tests/pressure.md` mục "Chạy lại"; GREEN đọc `<worktree>/skills/shaping-spec/SKILL.md` bằng
**đường tuyệt đối**. Chạy lại cả kịch bản đã loại khi skill đổi phần kỷ luật — đạt sẵn ở RED hôm nay không bảo đảm
đạt khi luật nền đổi.
