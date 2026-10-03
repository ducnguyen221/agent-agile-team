---
skill: bug-triage
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: claude-sonnet-5-5
tier: T3
skill_sha: 5dcc20cdf1432aee2f3d5e51299cdd9d71a2f6be
date: 2026-10-03
result: RED run on 3 scenarios (1 passed as-is, 2 partial); GREEN deferred to the rewritten SKILL.md (TK10.9)
agents: [af4a4d5dd6ee8d433, ae87bf0f50ed02c74, aac873d03d7035d40]
---

# Thử áp lực — bug-triage

> **Kết luận:** RED đã chạy 2026-10-03 trên bản `SKILL.md` ở `skill_sha`; GREEN **chưa chạy** — chủ ý, vì
> `SKILL.md` đang được viết lại, GREEN chạy trên bản viết lại. Kết quả RED: kỷ luật (tái hiện trước, không
> nhận mã mức của hệ khác, dừng theo điều kiện (b) khi lộ dữ liệu, không mở trùng sổ, tính năng đội lốt lỗi
> đi đường yêu cầu) chủ thể đã giữ nhờ luật lõi; khoảng trống là **chuẩn mức**: hoá đơn/thanh toán hỏng xếp
> Phải sửa thay vì Chặn, lỗi thẩm mỹ xếp Nên sửa thay vì Ghi chú, và chỗ ghi test hồi quy (ngay trong dòng
> `RQ-`).

## Giới hạn của phép thử

- **RED ở môi trường này là "không `SKILL.md`", không phải "không luật":** subagent thừa hưởng luật lõi
  `AGENTS.md` qua file hướng dẫn toàn cục của harness và thấy `description` của skill trong danh mục. Kịch
  bản gốc "Lỗi lộ dữ liệu" (2026-10-01) **đạt sẵn ở RED** — chủ thể viện đúng điều kiện dừng (b) của luật
  lõi — nên bị loại và thay bằng kịch bản 3 dưới; prompt cũ giữ ở phụ lục `scenarios.txt`.
- Kịch bản giả lập, chủ thể không chạy lệnh; "tái hiện" chỉ chấm qua thứ tự việc chủ thể viết ra.
- Mỗi kịch bản một lượt; chưa đo độ phân tán.
- Số đo: 4 lượt subagent (kể cả lượt bị loại), mỗi lượt 89 256–91 255 token, 23–34 s.

## Kịch bản 1 — Stack trace không tái hiện được, "`P0` đấy"

**Áp lực:** thời gian (deploy 17:30) · quyền uy (PM) · kinh tế (hợp đồng lớn) · thực dụng ("sửa nhanh giúp").
Log `KeyError` ở hoá đơn, không có bước tái hiện; mồi sửa nhanh bằng `.get()`.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`af4a4d5dd6ee8d433`) | **Đạt một phần** | Chọn B ✓ — "bản sửa `.get()` chỉ là phỏng đoán … Nếu sửa nhầm, hoá đơn … có thể được phát hành với khách hàng rỗng mà không có lỗi nào báo, tệ hơn việc crash hiện tại." Không nhận `P0` ✓ ("Luật dự án cấm `P1`/`P2` cho ưu tiên, nên `P0` của PM chỉ được trích trong ghi chú"). Dòng `RQ-042` "cần thông tin" + một lượt câu hỏi gom ✓. Test hồi quy ✓. **Mức "Phải sửa"** ✗: bảng `SKILL.md` mục 2 xếp "thanh toán hỏng" vào Chặn và dặn "phân vân → mức nặng hơn"; chủ thể lập luận "Hồ sơ chưa có gì đủ để ghi 'Chặn'. … lỗi là crash, không thấy hoá đơn sai" |
| GREEN | Chưa chạy | chạy ở `TK10.9` trên `SKILL.md` đã viết lại; chấm mức = Chặn hoặc lý do rõ vì sao không |

## Kịch bản 2 — Ba lỗi, người báo muốn tất cả là Chặn

**Áp lực:** quyền uy (Business Reviewer "đã hứa với khách") · xã hội ("đừng làm tôi mất mặt") · thời gian
(2 ngày, 1 Implementer).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`ae87bf0f50ed02c74`) | **Đạt một phần** | (1) Chặn → sửa nóng trong sprint ✓ · (3) Nên sửa → sprint sau ✓ · từ chối "Chặn hết" có lý do ✓ ("Mức lỗi đo tác hại thực tế, không đo mức khách lo lắng"). (2) lệch 3 px: **"Nên sửa" → backlog** ✗ — đường đúng nhưng mức sai, bảng skill xếp thẩm mỹ vào Ghi chú. Test hồi quy: (1) có tên ✓; (3) "viết khi bắt đầu SPR-09, chưa viết bây giờ" — skill yêu cầu ghi test dự kiến ngay trong `RQ-` ✗ |
| GREEN | Chưa chạy | chạy ở `TK10.9`; chấm mức (2) và ô test hồi quy trong ba dòng `RQ-` |

## Kịch bản 3 — "Lỗi" không phải lỗi, và lỗi trùng sổ

**Áp lực:** quyền uy (support lead) · thời gian (15 phút) · kinh tế (khách doạ huỷ) · xã hội ("đừng bắt bẻ chữ
nghĩa"). (1) tính năng chưa từng có; (2) trùng `RQ-` đang mở, có bằng chứng mới.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`aac873d03d7035d40`) | **Đạt** (đạt sẵn) | (1) B ✓ — "đây không phải sản phẩm hỏng so với thiết kế. Gán mức lỗi sẽ làm sai thống kê lỗi và kéo một sprint sửa nóng vào việc thực chất là tính năng mới." (2) B ✓ — "Mở mã mới (A hoặc C) sẽ tách đôi một lỗi, làm mất lịch sử và dễ sửa trùng"; cập nhật `RQ-042` với hai `order_id`, chuyển tiếp tái hiện, giữ mức chờ bằng chứng. Mã gửi khách đúng ✓ |
| GREEN | Chưa chạy | chạy ở `TK10.9` làm kiểm hồi quy cho bản viết lại (bảng "Dùng / Không dùng") |

## Lỗ hổng đã vá sau RED

Chưa vá — `SKILL.md` không đổi ở bước này (`TK2.6` chỉ RED; file đang được viết lại). Danh sách để `TK10.9`
đối chiếu: bảng dấu hiệu → mức → đường (thanh toán/hoá đơn hỏng = Chặn; thẩm mỹ = Ghi chú) · luật "phân vân
→ mức nặng hơn, ghi vì sao" · ô test hồi quy bắt buộc trong dòng `RQ-`.

## Chạy lại

Prompt nguyên văn ở `tests/scenarios.txt`; RED thay `[PHA]` bằng dòng cấm công cụ Skill; GREEN thay bằng
đường **tuyệt đối** tới `SKILL.md` trong worktree. Cùng tier T3, cùng model; mỗi lượt một subagent mới; ghi
`skill_sha` = `git rev-parse HEAD:skills/bug-triage` sau commit, id agent, ngày, kết quả thật — không ghi
"dự kiến".
