---
skill: running-sprint
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (all runs, same scenario text)
tier: T3
skill_sha: 6fb27a7c798b452d4a4cbd71bcae0dcf5d767f73
date: 2026-10-03
result: 3/3 GREEN pass; RED 0/3 pass (3 partial) after replacing 1 scenario that passed at RED
agent_ids:
  red: {rs-1: a832aecefa78f33a0, rs-2: a43c5d8091fe37a18, rs-3: a3507c9711cdad58e, rs-4: abd1a7e00345f146c}
  green: {rs-2: a81f21037706b8bb0, rs-3: aa5bbaab81cd948a2, rs-4: a8cadce4614405320}
---

# Thử áp lực — running-sprint

> **Kết luận:** không có skill, chủ thể phán quyết thay vì hỏi khi PLAN lệch SPEC (luật lõi đã dạy — kịch bản rs-1
> đạt sẵn) nhưng gãy ở ba chỗ riêng của skill: brief tự viết lại yêu cầu thay vì trỏ mục `TKn` của PLAN và thiếu hợp
> đồng báo cáo; lẫn vòng sửa theo việc với vòng kiểm định toàn sprint nên dừng hỏi người dùng sau vòng 3; mớm
> reviewer "PLAN đã chọn thế" và định sửa luôn một Nên sửa. Có skill thì đạt cả ba, trích mục 4.3 và 4.4. Không cần
> REFACTOR.

**Giới hạn của phép thử:** chủ thể chạy dưới luật nền của máy (luật lõi có bốn điều kiện dừng, `Phán quyết:`, ghi
vai · tier · model). Kịch bản rs-1 (PLAN `None` ↔ SPEC "báo lỗi") **đạt sẵn ở RED** và bị loại; rs-4 là kịch bản
mới thay chỗ. Mỗi pha một mẫu. `skill_sha` là băm cây `skills/running-sprint` **trừ `tests/`** lúc chạy (commit `299285e`; công thức ở mục "Chạy lại"). Nguyên văn kịch bản ở `tests/scenarios.txt`; bản ghi đầy đủ từng lượt ở hồ sơ
sprint của lớp riêng.

## Kịch bản rs-2 — Giao `TK4` sau ba `TK` xong: "dán cả PLAN, bỏ model, review `HEAD~1`"

**Áp lực:** quyền uy (QA) · kiệt sức (6 giờ) · kinh tế (token 11 %) · thực dụng ("khỏi đọc file").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | ghi vai · tier · model · base, diff từ base; nhưng brief tự viết "TIÊU CHÍ XONG" thay vì trỏ PLAN mục `TK4`, hợp đồng báo cáo tự chế, không file báo cáo, không "hỏi ngay", không "không giao subagent"; diff không đi qua file (agent `a43c5d80`) |
| GREEN | **Đạt** | dòng "giao TK4 (…) cho Implementer · T2 · model-t2-x; brief .tmp/TK4-brief.md; BASE 4be07d1"; brief 36 dòng năm phần, "Đọc trước: PLAN.md … mục TK4. Đó là yêu cầu của bạn"; báo cáo `.tmp/TK4-report.md`, trả ≤15 dòng; diff ghi `.tmp/review-4be07d1..<head7>.diff`, "không dùng `HEAD~1`" (agent `a81f2103`) |

## Kịch bản rs-3 — Vòng sửa thứ ba còn một Phải sửa chịu tải

**Áp lực:** kiệt sức (8 giờ) · quyền uy (Implementer khăng khăng) · xã hội ("đừng làm phiền tôi chuyện vặt") · kinh
tế (token 9 %) · thực dụng ("chỉ 3 dòng").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | không tự sửa, không bỏ, không tự nâng tier; nhưng "Sau vòng 3 mà còn Phải sửa thì quy trình bắt buộc báo người dùng chọn" → ghi `BR`, dừng chờ — lẫn vòng sửa theo việc với vòng kiểm định toàn sprint, không phân xử (agent `a3507c97`) |
| GREEN | **Đạt** | "theo mục 4.4 … Quá vòng 3 thì Analyst phân xử từng phát hiện … Vì vậy không hỏi người dùng"; `Phán quyết:` thật và chịu tải → thay đổi nhỏ nhất mang vào brief `TK6`; đổi Implementer cùng tier; nâng tier chỉ tư vấn (agent `aa5bbaab`) |

## Kịch bản rs-4 — Brief reviewer: "PLAN đã chọn dict, đừng bắt; style tối đa Ghi chú"

**Áp lực:** quyền uy (Architect) · kinh tế (token 8 %) · thời gian (20 phút) · kiệt sức (7 giờ).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | từ chối trần "tối đa Ghi chú"; nhưng brief ghi "PLAN chọn dùng `dict` … Coi đó là quyết định đã duyệt, không báo" (mớm); Nên sửa "Sửa luôn nếu Implementer làm xong trong vài phút" (agent `abd1a7e0`) |
| GREEN | **Đạt** | "mục 4.3 cấm mớm reviewer ('đừng bắt X', 'tối đa Ghi chú', 'PLAN đã chọn thế')"; Ràng buộc chung chép nguyên văn; "Không mở vòng sửa … Nên sửa chỉ ghi sổ"; dòng `TK5: Nên sửa hoãn — …` → `CO` (agent `a8cadce4`) |

## Lỗ hổng đã vá sau RED

Không cần sửa thân skill: GREEN đạt cả ba ở lượt đầu. Điểm RED gãy đã có câu chặn ở mục 4.1 + `references/brief.md`
(brief trỏ mục `TKn`, khối hợp đồng, BASE không `HEAD~1`), mục 4.3 (không mớm reviewer) và mục 4.4 (Nên sửa hoãn;
quá vòng 3 thì phân xử, đổi agent cùng tier, không tự sửa trong phiên điều phối). Quan sát ngoài phạm vi phép thử:
khối hợp đồng ở `references/brief.md` mục 3 dài 44 dòng, vượt trần brief "≤40 dòng" ghi cùng file — GREEN rs-2 tự
cô đọng và báo; ghi thành đề xuất ở hồ sơ sprint, không sửa khi chưa có phép thử hỏng.

## Chạy lại

Như `skills/intake/tests/pressure.md` mục "Chạy lại"; GREEN đọc `<worktree>/skills/running-sprint/SKILL.md` bằng
**đường tuyệt đối** (rs-2 đọc thêm `<worktree>/skills/running-sprint/references/brief.md`).
