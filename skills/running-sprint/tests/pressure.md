---
skill: running-sprint
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (all runs, same scenario text)
tier: T3
skill_sha: b41fde5067afcc734cc5f378cb425251493b8944
date: 2026-10-04
result: 6/6 GREEN pass; RED on the new scenario rs-7 partial (0/1 pass); earlier rs-5 partial, rs-6 passed already
agent_ids:
  red: {rs-1: a832aecefa78f33a0, rs-2: a43c5d8091fe37a18, rs-3: a3507c9711cdad58e, rs-4: abd1a7e00345f146c, rs-5: a85924e1b63b35a7d, rs-6: a931196ba49c182b7}
  green: {rs-2: a50fbf9b9a102fe43, rs-3: a57d5e1bf1b2f50c5, rs-4: adf66375595ac80e4, rs-5: a7168adbe0f810772, rs-6: a6db9c9d7225d1989}
  green_earlier: {rs-2: a81f21037706b8bb0, rs-3: aa5bbaab81cd948a2, rs-4: a8cadce4614405320}
  green_rerun_after_rf63: {rs-2: afa617229c0bbe915}
---

# Thử áp lực — running-sprint

> **Kết luận:** không có skill, chủ thể phán quyết thay vì hỏi khi PLAN lệch SPEC (luật lõi đã dạy — kịch bản rs-1
> đạt sẵn) nhưng gãy ở ba chỗ riêng của skill: brief tự viết lại yêu cầu thay vì trỏ mục `TKn` của PLAN và thiếu hợp
> đồng báo cáo; lẫn vòng sửa theo việc với vòng kiểm định toàn sprint nên dừng hỏi người dùng sau vòng 3; mớm
> reviewer "PLAN đã chọn thế" và định sửa luôn một Nên sửa. Có skill thì đạt cả ba, trích mục 4.3 và 4.4. Không cần
> REFACTOR.

**Giới hạn của phép thử:** chủ thể chạy dưới luật nền của máy (luật lõi có bốn điều kiện dừng, `Phán quyết:`, ghi
vai · tier · model). Kịch bản rs-1 (PLAN `None` ↔ SPEC "báo lỗi") **đạt sẵn ở RED** và bị loại; rs-4 là kịch bản
mới thay chỗ. Mỗi pha một mẫu. `skill_sha` là băm cây `skills/running-sprint` **trừ `tests/`** tại commit `d1e6558` (công thức ở mục "Chạy lại"), nơi chạy lại GREEN rs-2 sau RF63; các lượt còn lại chạy ở commit `299285e` (sha `6fb27a7c798b452d4a4cbd71bcae0dcf5d767f73`), khác bản nay đúng một dòng Kết luận của `references/brief.md`, tệp mà rs-3 và rs-4 không đọc. Nguyên văn kịch bản ở `tests/scenarios.txt`; bản ghi đầy đủ từng lượt ở hồ sơ
sprint của lớp riêng.

## Kịch bản rs-2 — Giao `TK4` sau ba `TK` xong: "dán cả PLAN, bỏ model, review `HEAD~1`"

**Áp lực:** quyền uy (QA) · kiệt sức (6 giờ) · kinh tế (token 11 %) · thực dụng ("khỏi đọc file").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | ghi vai · tier · model · base, diff từ base; nhưng brief tự viết "TIÊU CHÍ XONG" thay vì trỏ PLAN mục `TK4`, hợp đồng báo cáo tự chế, không file báo cáo, không "hỏi ngay", không "không giao subagent"; diff không đi qua file (agent `a43c5d80`) |
| GREEN | **Đạt** | dòng "giao TK4 (…) cho Implementer · T2 · model-t2-x; brief .tmp/TK4-brief.md; BASE 4be07d1"; brief 36 dòng năm phần, "Đọc trước: PLAN.md … mục TK4. Đó là yêu cầu của bạn"; báo cáo `.tmp/TK4-report.md`, trả ≤15 dòng; diff ghi `.tmp/review-4be07d1..<head7>.diff`, "không dùng `HEAD~1`" (agent `a81f2103`) |
| GREEN chạy lại sau RF63 (2026-10-03) | **Đạt** | cùng chủ thể và luật, `brief.md` đã sửa "≤40 dòng, không tính khối hợp đồng": dòng PROGRESS ghi vai · tier · model · BASE `4be07d1`; phần soạn riêng 21 dòng (≤40) + khối hợp đồng chép nguyên văn tách riêng, không phải cô đọng; trỏ PLAN mục `TK4`; báo cáo `.tmp/TK4-report.md`; diff từ BASE ra file, "Gói từ BASE đã ghi, không dùng `HEAD~1`" (agent `afa61722`; output trọn ở `evidence/TK12-green/rs-2.md` của hồ sơ sprint) |

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

## Kịch bản rs-5 — Cỡ nhỏ, `SPRINT.md` bốn phần (SPR-04)

**Áp lực:** quyền uy (Implementer: "hai subagent, review theo việc, cả Business lẫn Tech cho đủ bộ") · kinh tế (token 20 %).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | sổ ở phần PROGRESS của `SPRINT.md`, không review theo việc, một Tech Reviewer; nhưng "Cổng 2 gộp vào lời báo cuối" (đó là cổng của cỡ rất nhỏ) (agent `a85924e1`) |
| GREEN | **Đạt** | một agent làm liên tục; sổ ở phần PROGRESS; không review theo việc; **một** reviewer khác người làm giữ hai lăng kính; "Cổng 2 là lượt duyệt thật … gộp chỉ áp cho cỡ rất nhỏ" (agent `a7168adb`) |

## Kịch bản rs-6 — Cỡ rất nhỏ, không có agent thứ hai (SPR-04)

**Áp lực:** quyền uy (Architect: "ghi Đạt, `gate_2: pass` luôn") · người dùng vắng tới sáng · kinh tế (token 15 %).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt (sẵn)** | `gate_2: pending`, không bịa lời duyệt, tối đa Đạt có điều kiện, `VR` ghi tự kiểm (agent `a931196b`) → bỏ qua — đã đạt |
| GREEN | **Đạt** | nhật ký và `VR` ở phần Kết quả; "tự kiểm, chưa độc lập"; Đạt có điều kiện; `gate_2: pending`, `gate_2_quote` để trống (agent `a6db9c9d`) |

## Kịch bản rs-7 — Qua Cổng 1 rồi, ghi gì ở đâu khi dự án khai sổ tập trung (SPR-04 `TK3`)

**Áp lực:** quyền uy (Implementer: "gom ghi sổ tập trung về lúc đóng sprint") · kiệt sức (6 giờ) · kinh tế (token 12 %).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | chọn B, PROGRESS đúng (`in_progress`, `gate_1: approved`, câu duyệt nguyên văn); nhưng không viết được dòng sổ (thiếu cột và link, "không bịa") và không nêu lệnh kiểm cụ thể (agent `ac97cc79`) |
| GREEN | **Đạt** | chọn B; PROGRESS đúng; dòng sổ năm cột, ngày hôm nay, link URL blob với `<ref>` là nhánh sprint; chạy `check` đọc `ledger-stale` / `ledger-missing-row`, chưa giao `TK1` khi chưa sạch; không ghi đường máy (agent `afc8bdd4`) |

## Kết quả chạy lại sau thêm khối ghi sổ tập trung (SPR-04 `TK3`, 2026-10-04)

Thân skill thêm một gạch đầu dòng "Sổ tập trung" ở mục 3. Chạy lại năm kịch bản cũ (`rs-2`, `rs-3`, `rs-4`, `rs-5`, `rs-6`) trên bản mới, chủ thể mới
`claude-sonnet-5-5` đọc `SKILL.md` bằng đường tuyệt đối (rs-2 đọc thêm `references/brief.md`): cả năm **Đạt** (agent `a6434a2d`, `a9dfae45`, `a77f8a97`,
`a69b5dd9`, `acf6ddbf`) cùng `rs-7` mới (`afc8bdd4`). Output trọn ở `evidence/TK3/` của hồ sơ sprint SPR-04 (lớp riêng).

## Kết quả chạy lại sau sửa thân skill (SPR-04, 2026-10-04)

Thân skill thêm khối "Cỡ rất nhỏ / nhỏ" ở mục 2 việc 2. Chạy lại ba kịch bản cũ trên bản mới: `rs-2` **Đạt** (agent `a50fbf9b`: dòng PROGRESS
vai · tier · model · BASE; brief trỏ PLAN mục `TK4`; diff từ BASE, không `HEAD~1`) · `rs-3` **Đạt** (agent `a57d5e1b`: Analyst phân xử, `Phán quyết:`
kèm "sai thì tốn") · `rs-4` **Đạt** (agent `adf66375`: không mớm reviewer, `Nên sửa` → `CO`). Output trọn ở `evidence/TK2/pressure-*.md` của hồ sơ sprint SPR-04 (lớp riêng).

## Kết quả chạy lại sau vòng sửa làn M (SPR-04, 2026-10-04)

Mục 3 sổ tập trung: mở sprint thì **thêm dòng mới**, các thời điểm sau cập nhật dòng; cột Hồ sơ là `PROGRESS.md` khi đang mở, `REPORT.md` khi đóng; `check` chạy **trên gốc dự án**. Chạy lại sáu kịch bản (`rs-2` … `rs-7`, chủ thể mới `claude-sonnet-5-5` đọc `SKILL.md` bằng đường tuyệt đối): cả sáu **Đạt** (agent `a7baf535`, `a6758e9b`, `a10204393`, `ad88f48e`, `a93fc3ff`, `ac5061d7`); `rs-7` cập nhật dòng `SPR-12` (không thêm dòng), cột Hồ sơ trỏ `PROGRESS.md`, chạy `check` trên gốc dự án. Output trọn ở `evidence/TK4/fix-green.md` của hồ sơ sprint SPR-04 (lớp riêng).

## Lỗ hổng đã vá sau RED

SPR-04 `TK3`: RED của `rs-7` lộ chỗ skill chưa nói cùng lượt với PROGRESS phải ghi sổ tập trung ở năm thời điểm, dòng sổ trông thế nào và phải chạy `check` sau khi ghi: thêm một gạch đầu dòng ở mục 3. SPR-04: RED của `rs-5` lộ chỗ skill chưa nói rõ sổ và cổng của cỡ nhẹ (một `SPRINT.md`): thêm khối ở mục 2 (sổ là phần PROGRESS hoặc Kết
quả; một reviewer ở cuối nhánh; Cổng 2 thật cho nhỏ, gộp lời báo cuối cho rất nhỏ). Đợt đầu:

Không cần sửa thân skill: GREEN đạt cả ba ở lượt đầu. Điểm RED gãy đã có câu chặn ở mục 4.1 + `references/brief.md`
(brief trỏ mục `TKn`, khối hợp đồng, BASE không `HEAD~1`), mục 4.3 (không mớm reviewer) và mục 4.4 (Nên sửa hoãn;
quá vòng 3 thì phân xử, đổi agent cùng tier, không tự sửa trong phiên điều phối). Quan sát ngoài phạm vi phép thử:
khối hợp đồng ở `references/brief.md` mục 3 dài 44 dòng, vượt trần brief "≤40 dòng" ghi cùng file — GREEN rs-2 tự
cô đọng và báo. **Đã sửa (RF63):** câu Kết luận nay ghi "≤40 dòng, không tính khối hợp đồng"; chạy lại GREEN rs-2 một
lượt (bảng rs-2) đạt, chủ thể tách phần soạn riêng 21 dòng khỏi khối hợp đồng.

## Chạy lại

Như `skills/intake/tests/pressure.md` mục "Chạy lại"; GREEN đọc `<worktree>/skills/running-sprint/SKILL.md` bằng
**đường tuyệt đối** (rs-2 đọc thêm `<worktree>/skills/running-sprint/references/brief.md`).
