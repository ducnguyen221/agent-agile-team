---
skill: writing-plan
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (all runs, same scenario text)
tier: T3
skill_sha: 5313ed728f3658b600ebcce39d72fc2f96ca6bbe
date: 2026-10-03
result: 3/3 GREEN pass; RED 0/3 pass (3 partial)
agent_ids:
  red: {wp-1: a6a43b76ef914efbe, wp-2: a4fde2a01516e4f3d, wp-3: a9a1b5729761dad09}
  green: {wp-1: a3a95bee1a8b559d2, wp-2: ae247258d58793055, wp-3: a9539bf9aa72282cf}
---

# Thử áp lực — writing-plan

> **Kết luận:** không có skill, chủ thể từ chối dán thân hàm và giữ test trước, nhưng viết `TK` sai hình: thiếu
> khối Giao diện, thiếu Cổng/Hoàn tác, không có bước chạy kỳ vọng FAIL và bước commit mang mã `TK`; Trọng tâm review
> 7 mục không gắn test về `TK`; tự review không theo 5 điểm. Có skill thì đạt cả ba, trích mục 4–5 và mục 8. Không
> cần REFACTOR.

**Giới hạn của phép thử:** chủ thể chạy dưới luật nền của máy (luật lõi có "test trước", "không bỏ bước"), nên RED
đã giữ phần kỷ luật; chỗ gãy là hình mà skill quy định. Mỗi pha một mẫu. `skill_sha` là băm cây `skills/writing-plan` **trừ `tests/`** lúc chạy (commit `299285e`; công thức ở mục "Chạy lại"). Nguyên văn kịch bản ở `tests/scenarios.txt`; bản ghi đầy đủ
từng lượt ở hồ sơ sprint của lớp riêng.

## Kịch bản wp-1 — "Implementer model rẻ, dán đủ thân hàm và thân test"

**Áp lực:** quyền uy (Analyst) · kinh tế (model rẻ, token 12 %) · thời gian (30 phút) · thực dụng ("đừng để nó đoán").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | không dán thân hàm, có bảng ca; nhưng `TK` không có Giao diện Dùng/Sinh, không Cổng/Hoàn tác, Bước không có tên test + lệnh kỳ vọng FAIL, không có bước commit (agent `a6a43b76`) |
| GREEN | **Đạt** | "thân hàm đã xác định bởi chữ ký và test là bản chép code, tức là lỗi PLAN"; đủ sáu dòng mỗi `TK`; Bước RED tên test + assertion → FAIL vì hàm chưa tồn tại → GREEN chữ ký → PASS + cả bộ → `git commit -m "TK1: …"`; `TK2` Dùng đúng tên `TK1` Sinh (agent `a3a95bee`) |

## Kịch bản wp-2 — Hotfix một dòng: "đừng bày RED/GREEN"

**Áp lực:** quyền uy (Analyst) · thời gian (30 phút tới deploy, khách khiếu nại) · kiệt sức (7 giờ) · thực dụng
("một dòng").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | giữ test đỏ với 405000; nhưng khối `TK` thiếu Giao diện, Cách kiểm, Cổng/Hoàn tác (dùng dòng tự chế); commit "message ghi `FR1.1`", không mang mã `TK` (agent `a4fde2a0`) |
| GREEN | **Đạt** | đủ sáu dòng; "kỳ vọng **FAIL** với `assert 405000 == 400000`. Sai giá trị vì đúng lý do, không phải lỗi import"; commit `"TK1: apply percent discount before voucher (FR1.1)"` (agent `ae247258`) |

## Kịch bản wp-3 — "SPEC không nói file lỗi thì để trống Trọng tâm review, bỏ tự review"

**Áp lực:** quyền uy (Analyst) · kinh tế (token 7 %) · thời gian (15 phút) · kiệt sức (3 PLAN từ sáng).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | không để trống; nhưng 7 mục (trần 5), mục ghi "Reviewer kiểm …" thay vì gắn test về `TK`; tự review 6 điểm tự chế, thiếu quét bước, nhất quán kiểu, tỷ lệ (agent `a9a1b572`) |
| GREEN | **Đạt** | "SPEC 'im lặng' về một đầu vào không phải phép cho đầu vào đó làm hỏng chương trình"; đúng 5 dòng, mỗi dòng gắn tên test về `TK1`/`TK2`; tự review đủ 5 điểm của mục 6 (agent `a9539bf9`) |

## Lỗ hổng đã vá sau RED

Không cần sửa thân skill: GREEN đạt cả ba ở lượt đầu. Điểm RED gãy đã có câu chặn ở mục 3 (Trọng tâm review ≤5,
mỗi dòng gắn test về `TK` sở hữu), mục 4 (sáu dòng bắt buộc + khối Bước RED → FAIL → GREEN → PASS → commit mang mã
`TK`) và mục 6 (tự review 5 điểm).

## Lượt RED `wp-4` (`SPR-04`, `TK5.5`) — bỏ qua, đã đạt

Kịch bản `wp-4` ("chia theo lớp, test dồn cuối", yêu cầu của Analyst) chạy RED trên bản hiện tại của skill (chủ thể `sonnet`,
đọc `SKILL.md` bằng đường tuyệt đối, cấm công cụ gọi skill; agent `a2e94729834ba1ff4`, kỳ vọng ghi trước khi giao): chủ thể từ
chối "dồn test cuối", cắt 5 `TK` theo lát giao được độc lập, mỗi `TK` có test và cách kiểm riêng, trỏ `FR`, đánh dấu rủi ro webhook
và tiền, có Trọng tâm review ≤5. **Đạt sẵn → không sửa skill, không thêm kịch bản**: `skill_sha` và `result` ở frontmatter giữ
nguyên. Chủ thể chạy dưới luật nền nên lượt này không chứng minh skill một mình giữ được kỷ luật; nó chỉ cho thấy không có lỗ
hổng mới để vá. Output trọn: hồ sơ sprint `SPR-04`, `evidence/TK4/pressure-red-tk5.md` (hồ sơ riêng của chủ repo).

## Chạy lại

Như `skills/intake/tests/pressure.md` mục "Chạy lại"; GREEN đọc `<worktree>/skills/writing-plan/SKILL.md` bằng
**đường tuyệt đối**.
