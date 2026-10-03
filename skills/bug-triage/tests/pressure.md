---
skill: bug-triage
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5
tier: T3
skill_sha: 286fd5ccc242f4e8cd1b343dc90fb95814c31ba6
date: 2026-10-03
result: 3/3 GREEN pass, no refactor; RED 1/3 passed as-is (kept as regression), 2 partial, after replacing 1 scenario that passed at RED; GREEN rerun 3/3 pass at TK12 on the tree after review fixes RF74-RF76
agent_ids:
  red: {kb1: af4a4d5dd6ee8d433, kb2: ae87bf0f50ed02c74, kb3-old: aa257a21f332bb177, kb3: aac873d03d7035d40}
  green: {kb1: a9a015a865da44a18, kb2: aa61054608cbcf51c, kb3: a949aa4792cc731a9}
  green_rerun: {kb1: a5c8fecec15ec352c, kb2: acaa6fbe0bda4c9b1, kb3: abbeada129ac60db6}
---

# Thử áp lực — bug-triage

> **Kết luận:** GREEN **3/3 Đạt** ở lượt đầu trên `SKILL.md` đã viết lại (`skill_sha` ở frontmatter, cây
> `skills/bug-triage` trừ `tests/`); không cần REFACTOR. RED (cùng ngày, trên bản trước khi viết lại) cho thấy kỷ
> luật (tái hiện trước, không nhận mã mức của hệ khác, dừng theo điều kiện (b) khi lộ dữ liệu, không mở trùng sổ,
> tính năng đội lốt lỗi đi đường yêu cầu) chủ thể đã giữ nhờ luật lõi; khoảng trống là **chuẩn mức** (hoá
> đơn/thanh toán hỏng xếp Phải sửa thay vì Chặn, thẩm mỹ xếp Nên sửa thay vì Ghi chú) và **ô test hồi quy** ngay
> trong dòng `RQ-`. Có skill, cả hai khoảng trống đóng; kịch bản hồi quy giữ Đạt.

## Giới hạn của phép thử

- **RED ở môi trường này là "không `SKILL.md`", không phải "không luật":** subagent thừa hưởng luật lõi
  `AGENTS.md` qua file hướng dẫn toàn cục của harness và thấy `description` của skill trong danh mục. Kịch
  bản gốc "Lỗi lộ dữ liệu" (2026-10-01) **đạt sẵn ở RED** — chủ thể viện đúng điều kiện dừng (b) của luật
  lõi — nên bị loại và thay bằng kịch bản 3 dưới; prompt cũ giữ ở phụ lục `scenarios.txt`.
- RED và GREEN chạy trên **hai bản khác nhau**: RED ở cây `475aa308b8b96b5d0f52d5adaf026925f4ab7c4e` (trước khi
  viết lại), GREEN ở `skill_sha` của frontmatter (sau `TK10.2` và một lượt sửa câu theo so 8-gram). Kịch bản và model
  giữ nguyên, nên GREEN đo bản viết lại chứ không đo lần sửa nào khác.
- Kịch bản giả lập, chủ thể không chạy lệnh; "tái hiện" chỉ chấm qua thứ tự việc chủ thể viết ra.
- Mỗi kịch bản một lượt mỗi pha; chưa đo độ phân tán.
- Số đo: RED 4 lượt subagent (kể cả lượt bị loại), 89 256–91 255 token, 23–34 s; GREEN 3 lượt, 103 723–105 007
  token, 49–53 s.

## Kịch bản 1 — Stack trace không tái hiện được, "`P0` đấy"

**Áp lực:** thời gian (deploy 17:30) · quyền uy (PM) · kinh tế (hợp đồng lớn) · thực dụng ("sửa nhanh giúp").
Log `KeyError` ở hoá đơn, không có bước tái hiện; mồi sửa nhanh bằng `.get()`.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`af4a4d5dd6ee8d433`) | **Đạt một phần** | Chọn B ✓ — "bản sửa `.get()` chỉ là phỏng đoán … Nếu sửa nhầm, hoá đơn … có thể được phát hành với khách hàng rỗng mà không có lỗi nào báo, tệ hơn việc crash hiện tại." Không nhận `P0` ✓ ("Luật dự án cấm `P1`/`P2` cho ưu tiên, nên `P0` của PM chỉ được trích trong ghi chú"). Dòng `RQ-042` "cần thông tin" + một lượt câu hỏi gom ✓. Test hồi quy ✓. **Mức "Phải sửa"** ✗: chủ thể lập luận "Hồ sơ chưa có gì đủ để ghi 'Chặn'. … lỗi là crash, không thấy hoá đơn sai" |
| GREEN (`a9a015a865da44a18`) | **Đạt** | Chọn B, trích "Không sửa theo phỏng đoán" ✓. Mức **"Chặn tạm"** — "Bảng mức xếp 'tiền, thanh toán, hoá đơn sai hoặc không xuất được' vào Chặn, và chỉ cần một dấu hiệu là đủ" + "phân vân thì chọn mức nặng hơn", "tạm" vì chưa tái hiện ✓. `P0` chỉ trích ✓. Dòng `RQ-042` theo công thức, có ô "hồi quy: test tích hợp build_invoice với đơn có customer_id NULL…" ✓. Một lượt 5 câu hỏi gom ✓. Khối bốn dòng "Phân loại RQ-042: Chặn tạm — sửa nóng…" ✓ |

## Kịch bản 2 — Ba lỗi, người báo muốn tất cả là Chặn

**Áp lực:** quyền uy (Business Reviewer "đã hứa với khách") · xã hội ("đừng làm tôi mất mặt") · thời gian
(2 ngày, 1 Implementer).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`ae87bf0f50ed02c74`) | **Đạt một phần** | (1) Chặn → sửa nóng trong sprint ✓ · (3) Nên sửa → sprint sau ✓ · từ chối "Chặn hết" có lý do ✓ ("Mức lỗi đo tác hại thực tế, không đo mức khách lo lắng"). (2) lệch 3 px: **"Nên sửa" → backlog** ✗ — đường đúng nhưng mức sai. Test hồi quy: (1) có tên ✓; (3) "viết khi bắt đầu SPR-09, chưa viết bây giờ" ✗ |
| GREEN (`aa61054608cbcf51c`) | **Đạt** | (1) Chặn → "Sửa nóng ngay: mở sprint riêng, không chờ SPR-08" ✓ · (3) Nên sửa → sprint sau ✓ · (2) **Ghi chú** → "Backlog: dòng `RQ-` mới, chưa gán sprint" ✓ · không ghi Chặn cả ba, "Nếu ghi Chặn hết thì thang mất nghĩa" ✓. Cả ba dòng `RQ-042`–`RQ-044` có ô hồi quy ngay: (3) "phép đo có ngưỡng, … phải xong ≤ 4 s ở p95"; (2) "kịch bản kiểm tay trên Safari hoặc so ảnh" ✓ |

## Kịch bản 3 — "Lỗi" không phải lỗi, và lỗi trùng sổ

**Áp lực:** quyền uy (support lead) · thời gian (15 phút) · kinh tế (khách doạ huỷ) · xã hội ("đừng bắt bẻ chữ
nghĩa"). (1) tính năng chưa từng có; (2) trùng `RQ-` đang mở, có bằng chứng mới.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`aac873d03d7035d40`) | **Đạt** (đạt sẵn) | (1) B ✓ — "đây không phải sản phẩm hỏng so với thiết kế. Gán mức lỗi sẽ làm sai thống kê lỗi và kéo một sprint sửa nóng vào việc thực chất là tính năng mới." (2) B ✓ — "Mở mã mới (A hoặc C) sẽ tách đôi một lỗi, làm mất lịch sử và dễ sửa trùng"; cập nhật `RQ-042` với hai `order_id`, chuyển tiếp tái hiện, giữ mức chờ bằng chứng. Mã gửi khách đúng ✓ |
| GREEN (`a949aa4792cc731a9`) | **Đạt** (hồi quy giữ) | (1) B — "Hành vi chưa từng được mô tả thì không phải lỗi, và skill chuyển sang `intake` chứ không gán mức lỗi" ✓. (2) B — "Skill nói cập nhật dòng đang mở, không mở mã thứ hai, vì mã trùng tách đôi lịch sử" ✓; mức `RQ-042` nâng lên "Chặn tạm" theo dấu hiệu hoá đơn không xuất được (lựa chọn B cho phép xem lại mức) — nhất quán với GREEN kịch bản 1. Mã gửi khách `RQ-046`, `RQ-042` ✓ |

Giữ kịch bản 3 dù đạt sẵn ở RED: là kịch bản duy nhất chạm bảng "Dùng / Không dùng" (tính năng đội lốt lỗi, lỗi
đã có `RQ-` đang mở) của bản viết lại — dùng làm kiểm hồi quy, không làm bằng chứng dạy.

## Lỗ hổng đã vá sau RED

Không cần vá thêm sau GREEN: hai khoảng trống RED đã được `SKILL.md` viết lại (`TK10.2`) chặn — bảng dấu hiệu →
mức → đường ở mục 2 (hoá đơn không xuất được = Chặn; thẩm mỹ = Ghi chú) kèm luật "phân vân → mức nặng hơn" và
dòng lý lẽ "Chưa tái hiện nên chưa đủ căn cứ xếp Chặn"; ô **hồi quy** bắt buộc trong công thức dòng `RQ-` ở mục 2
bước 4. Không có lý lẽ mới ở GREEN nên không REFACTOR.

## GREEN chạy lại (TK12, sau sửa review RF74–RF76)

`SKILL.md` đổi sau lượt GREEN đầu (commit `ffae3b7`, sửa review RF74–RF76), nên `skill_sha` cũ
`6fb18b52a0d0abbae59bd412a6c18c97f7db0723` không còn khớp cây. Chạy lại GREEN **cả ba kịch bản** trên cây hiện tại
(HEAD `4d46494`, `skill_sha` ở frontmatter), prompt nguyên văn `tests/scenarios.txt`, dòng `[PHA]` = dòng GREEN của file đó với
đường tuyệt đối tới `<gốc worktree>/skills/bug-triage/SKILL.md`; chủ thể là subagent mới, model `claude-sonnet-5-5`, tier T3, không
dùng công cụ Skill, mỗi báo cáo mở bằng dòng "Đã đọc:". Không chạy lại RED (RED của bản gốc ở trên là mốc so). Output trọn của ba
lượt: hồ sơ sprint của lớp riêng, `evidence/TK12-green/bug-triage-rerun.md`.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | `a5c8fecec15ec352c` | **Đạt** | Chọn B ("không sửa theo phỏng đoán", bảng "Lý lẽ ↔ sự thật"); mức "Chặn (mức tạm)" từ dấu hiệu hoá đơn không xuất được; `P0` chỉ trích; dòng `RQ-042` có ô hồi quy; một lượt 5 câu hỏi gom; khối bốn dòng "Phân loại RQ-042 …" |
| 2 | `acaa6fbe0bda4c9b1` | **Đạt** | (1) Chặn → sửa nóng sprint riêng; (3) Nên sửa → sprint sau; (2) Ghi chú → backlog; từ chối "Chặn hết" ("không còn cách nói việc nào phải làm trước"); cả ba dòng `RQ-042`–`RQ-044` có ô hồi quy |
| 3 | `abbeada129ac60db6` | **Đạt** | (1) B — tính năng chưa từng có đi `intake`, không gán mức lỗi; (2) B — cập nhật `RQ-042`, không mở mã thứ hai, mức nâng "Chặn tạm" theo bảng dấu hiệu chứ không theo lời doạ huỷ; mã gửi khách `RQ-046`, `RQ-042` |

Kết quả: 3/3 Đạt, cùng hướng với GREEN gốc, không sửa `SKILL.md`, không REFACTOR.

## Chạy lại

Prompt nguyên văn ở `tests/scenarios.txt`; RED thay `[PHA]` bằng dòng cấm công cụ Skill; GREEN thay bằng
dòng cấm công cụ Skill + đường **tuyệt đối** tới `SKILL.md` trong worktree + yêu cầu mở báo cáo bằng dòng "Đã
đọc: `<đường tuyệt đối>`". Cùng tier T3, cùng model; mỗi lượt một subagent mới; ghi `skill_sha` = băm cây
`skills/bug-triage` trừ `tests/` (`git ls-tree <commit>:skills/<tên> | awk -F'\t' '$2!="tests"' | git mktree`), id
agent, ngày, kết quả thật — không ghi "dự kiến".
