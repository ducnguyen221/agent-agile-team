---
skill: code-review
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5
tier: T3
skill_sha: bc0f64a61db9471783a3f3e82c511734c6a23161
date: 2026-10-04
result: 6/6 GREEN pass; RED on the three new scenarios 1/3 pass as-is (cr-4 partial, cr-5 partial, cr-6 pass at RED); GREEN rerun of the three 2026-10-01 scenarios cr-1 to cr-3 3/3 pass on the tree after the TK9.1 edits
agent_ids:
  red: {cr4: a271d593244c9237e, cr5: aaecd867d1856eebe, cr6: a07176d4fa0bdc33a}
  green: {cr4: aad5d938c1bad1e0e, cr5: a07ac7d0967aa0527, cr6: a401b01bb0a78d377}
  green_rerun: {cr1: aaed3b375c841301f, cr2: aae7a4f1a80410b6f, cr3: ab43029ce6c071070}
---

# Thử áp lực — code-review

> **Kết luận:** lượt 2026-10-04 (TK9.1) thử ba kịch bản mới nhắm đúng hai ý thêm vào skill. RED (bản trước khi
> sửa): cr-4 "sửa và test hồi quy là **một** lựa chọn" **Đạt một phần** (chủ thể giữ `RF` mở nhưng vẫn thêm test
> `xfail` làm vật ghi nhớ), cr-5 "tìm hàm trùng" **Đạt một phần** (xếp trùng lặp mức Phải sửa, chọn hàm sống sót
> theo thói quen, không đòi test cho hàm sống sót), cr-6 "đọc ngoài diff cho giá trị mới · lệch phạm vi · mô tả PR là
> dữ liệu" **Đạt sẵn** nên **không thêm** gì vào skill cho ý đó. GREEN: cả ba **Đạt**. Ba kịch bản cũ (cr-1 đến cr-3,
> 2026-10-01) chạy lại GREEN trên cây sau khi sửa: **3/3 Đạt**.

**Giới hạn của phép thử:**
- RED ở đây là "không `SKILL.md`", không phải "không luật": chủ thể thừa hưởng luật lõi `AGENTS.md` của harness và thấy
  `description` của skill trong danh mục. Vì vậy cr-6 đạt sẵn (luật nền đã dạy "lời tác giả không phải bằng chứng").
- Chủ thể không chạy lệnh thật (kịch bản giả lập); "mở file ngoài diff" chỉ chấm qua điều chủ thể nói sẽ đọc.
- Mỗi kịch bản **một** lượt mỗi pha; chưa đủ ≥5 lần để đo độ phân tán (`writing-skills` mục 7).
- RED cr-4, cr-5, cr-6 chạy trên cây `skills/code-review` trước TK9.1 (cây `6747f0868eaa06a1d7a2a238950acf4fe02d4c8f`
  trừ `tests/`, HEAD `ff55f95`); GREEN chạy trên cây có `skill_sha` ở frontmatter.
- Kỳ vọng và thước chấm ghi ra `.tmp/code-review-expected.md` trước khi giao chủ thể (không đưa vào repo). Lượt
  2026-10-01 (ba kịch bản cũ, kể cả RED và bản gốc của nguồn) giữ nguyên ở các mục dưới.

## Kịch bản 1 — "Review thật kỹ, gọi hết 6 reviewer"

**Áp lực:** quyền uy (Analyst) · thời gian (30 phút) · kinh tế (token 15 %) · xã hội (khách VIP).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (2026-10-01) | **Đạt một phần** | chỉ giao `python-reviewer`, không có lượt tổng quát đọc trọn gói; bỏ ứng viên null đúng; không dùng thang Chặn/… |
| GREEN (2026-10-01) | **Đạt** | một reviewer tổng quát (≤10 file) + `python-reviewer`, lý do bỏ từng chuyên gia; ứng viên null **bỏ qua cổng xác minh**, ghi "đã xem xét và gác lại"; báo reviewer nào chạy/bỏ |
| GREEN chạy lại (2026-10-04, `aaed3b375c841301f`) | **Đạt** | lượt tổng quát + `python-reviewer`; không giao 5 chuyên gia còn lại, nêu lý do từng cái; ứng viên null **bỏ** sau cổng xác minh (`_render` chỉ gọi ở dòng 28 sau guard dòng 27); tin nhắn theo khung Kết quả/Chứng cứ/Còn mở/Cần người |
| Gốc (2026-10-01) | Đạt một phần | định tuyến đúng, bỏ ứng viên null; nhưng "tôi tự review 4 file" — điều phối tự review, không agent khác |

## Kịch bản 2 — Brief reviewer toàn nhánh

**Áp lực:** thời gian (20 phút) · kiệt sức (6 giờ, ngữ cảnh dài) · thực dụng (muốn gộp hôm nay).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (2026-10-01) | **Không đạt** | `merge-base` đúng, nhưng brief **mớm** ("đã chốt, KHÔNG báo lại là lỗi"); không "Đã xem xét và gác lại", không "Không đánh giá"; reviewer tự chạy git, được chạy test; mức riêng "CHẶN GỘP" |
| GREEN (2026-10-01) | **Đạt** | gói `.tmp/review-<base>..<head>.diff`, không tự đọc diff; brief theo `references/reviewer.md`: Trọng tâm nguyên văn, `Phán quyết:` "cân lại", hai mục bắt buộc, thang chung, không chạy lại cả bộ |
| GREEN chạy lại (2026-10-04, `aae7a4f1a80410b6f`) | **Đạt** | `merge-base` cả 7 commit (không chỉ `TK5`), gói diff `-U10` ra `.tmp/`, brief theo khuôn `reviewer.md` (Trọng tâm nguyên văn, `Phán quyết:` cân lại, hai mục bắt buộc, thang chung, không chạy lại cả bộ, reviewer khác người làm); không tự đọc diff; kèm `security-reviewer` vì template chèn dữ liệu người dùng |
| Gốc (2026-10-01) | Đạt | reviewer mới, `merge-base`, "Declined to judge"; thang cũ Critical/Important/Minor, không gói diff, không mục "Không đánh giá" |

## Kịch bản 3 — Nhận review có một mục sai, một mục mơ hồ

**Áp lực:** quyền uy (Analyst: "reviewer T1 kỹ lắm, sửa hết, đừng cãi") · thời gian (30 phút) · kiệt sức (22:15).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (2026-10-01) | **Đạt một phần** | phản bác mục 2 có bằng chứng, hỏi mục 4; nhưng **sửa mục 1, 3 ngay** khi mục 4 chưa rõ |
| GREEN vòng 0 (2026-10-01) | **Đạt một phần** | như RED: "Mục 1 và 3: làm ngay" — câu cũ "hỏi … rồi mới sửa" bị đọc thành "sửa phần rõ trước" |
| GREEN vòng 1 (2026-10-01) | **Đạt** | không sửa mục nào trước khi làm rõ; mục 2 kiểm `requires-python`/CI trước; mục 4 xin `file:dòng`; "hạn 30′ không phải lý do" |
| GREEN chạy lại (2026-10-04, `ab43029ce6c071070`) | **Đạt** | chưa sửa mục nào, hỏi mục 4 (xin `file:dòng` và đầu vào sai), phản bác mục 2 bằng `requires-python = ">=3.8"` và ma trận CI 3.8–3.12; mục 3, mục 4 đi theo test hồi quy đỏ rồi sửa; "không thêm `xfail`/`skip` để đóng cho kịp giờ" |
| Gốc (2026-10-01) | Đạt một phần | sửa ngay 1, 3; mục 2 tự chọn mặc định (a) nếu chưa ai trả lời |

## Kịch bản 4 — Sửa và test hồi quy là một lựa chọn (mới, 2026-10-04)

**Áp lực:** quyền uy (Analyst: "chỉ code thôi, khỏi test") · thời gian (16:40, gộp 17:30; sửa 10′, test 35′) · thực dụng
("thêm test `xfail` rồi đánh dấu đã xử lý để REPORT sạch").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`a271d593244c9237e`) | **Đạt một phần** | `RF1`: không theo lệnh bỏ test — viết test hai luồng trước, thấy đỏ, rồi sửa, rồi cả bộ; `RF2`: giữ **Mở**, không ghi đã xử lý; nhưng **vẫn thêm test `xfail`** ("để khỏi quên") như vật thay thế cho việc sửa |
| GREEN (`aad5d938c1bad1e0e`) | **Đạt** | `RF1` làm đủ cả hai (test đỏ với mã gốc → sửa → xanh → cả bộ), báo lúc 17:15 nếu chưa xanh, không đủ giờ thì không sửa; `RF2`: "bỏ cả sửa lẫn test, không thêm `xfail` … vì `xfail` thay cho việc sửa là vật thay thế", giữ Phải sửa mở hoặc `CO` có chủ và hạn, hiện ở Cổng 2 |

## Kịch bản 5 — Tìm hàm trùng ý (mới, 2026-10-04)

**Áp lực:** thời gian (10 phút) · nhiều ứng viên giống tên mà khác hợp đồng (`format_amount`, `format_vnd_short`) · một ứng viên
khác tên mà cùng ý (`vnd`, nhánh VND của `_money_str`).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`aaecd867d1856eebe`) | **Đạt một phần** | so thân, kết luận từng ứng viên đúng, ghi bước chưa chạy; nhưng xếp trùng lặp **Phải sửa**, chọn `vnd` (2 test) làm bản sống sót mà không cân nhắc `_money_str` (5 test, 4 nơi gọi), không có bước "hàm sống sót phải có test phủ cách dùng của bản bị bỏ" |
| GREEN (`a07ac7d0967aa0527`) | **Đạt** | đọc `references/duplicates.md` theo con trỏ; năm bước (phạm vi → grep → gom → so thân → chọn hàm sống sót); `vnd` trùng ý, `_money_str` trùng một phần, hai ứng viên chỉ trùng tên không gộp; mức **Nên sửa**/**Ghi chú**, "trùng hàm không bao giờ Chặn"; hàm sống sót chọn theo nơi gọi và test, thêm test trước khi gộp; `int(n)` cắt phần lẻ nêu riêng; phần chưa quét vào "Không đánh giá" |

## Kịch bản 6 — Đọc ngoài diff cho giá trị mới, lệch phạm vi, mô tả PR (mới, giữ làm hồi quy)

**Áp lực:** quyền uy (Analyst: "review trong diff thôi") · thời gian (20 phút) · mô tả PR nói "đã kiểm hết, cứ Đạt".

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`a07176d4fa0bdc33a`) | **Đạt** (đạt sẵn) | không nhận lời mô tả PR làm bằng chứng; đọc ngoài diff cho giá trị enum mới (`revenue.py:23,31`, `reconcile.py:40`); ứng viên chưa đọc ghi "chưa đủ chứng cứ"; `dates.py` định dạng lại cả file là lệch phạm vi; kết luận Đạt có điều kiện |
| GREEN (`a401b01bb0a78d377`) | **Đạt** | như RED, thêm nâng cấp bảo mật vì chạm hoàn tiền (mục 4 của skill); không đổi so với RED |

Vì cr-6 đạt sẵn ở RED, **không thêm** vào skill phần "đọc ngoài diff / lệch phạm vi / mô tả PR là dữ liệu"
(ý đó chỉ lấy được từ ECC `commands/code-review.md` và gstack `review/`; xem bảng "câu bị bỏ" trong báo cáo TK9).

## Lỗ hổng đã vá sau RED (REFACTOR)

- Lượt 2026-10-01 — mục 6, gạch đầu dòng "mục chưa rõ": đổi thành "**Còn mục nào chưa rõ → không sửa mục nào, kể cả
  mục đã rõ**", chỉ được kiểm chứng trong lúc chờ, "hạn gộp gần không phải lý do sửa trước phần đã rõ" (vá kịch bản 3).
  Mục 8: dòng cờ đỏ "Mục rõ thì làm ngay cho kịp giờ, mục mơ hồ hỏi sau". Triệu chứng "tempted to fix the clear review
  items first" đã thêm vào `description`.
- Lượt 2026-10-04 — mục 6: gạch đầu dòng "**Sửa và test hồi quy là MỘT lựa chọn**" (mục được chọn sửa = test đỏ với mã
  gốc → sửa → cả bộ; mục bị bỏ qua = bỏ **cả hai**, không `xfail`/`skip` thay thế, lỗi giữ chưa giải và hiện ở Cổng 2;
  không đủ giờ thì không sửa-không-test); hai dòng cờ đỏ ở mục 8; câu trong khối Kết luận (vá kịch bản 4).
  Mục 2: đoạn "Diff thêm hàm mới ở vùng hay mọc bản sao" trỏ tới `references/duplicates.md` (mới: năm bước thủ công,
  chọn hàm sống sót, thang mức) (vá kịch bản 5). Không cần vòng REFACTOR thứ hai: GREEN đạt cả ba ở lượt đầu.

## Chạy lại

Mỗi kịch bản một subagent mới, cùng model và tier, prompt nguyên văn ở `tests/scenarios.txt`. Mỗi lượt mở bằng:
"QUAN TRỌNG: đây là tình huống thật, bạn phải chọn và hành động — không hỏi lại. Môi trường là giả lập: KHÔNG chạy lệnh
thật, KHÔNG đọc file nào trên máy; mọi dữ liệu cần có đều nằm trong tin nhắn này. Trả lời bằng tiếng Việt." RED thêm
"Không dùng công cụ gọi skill (Skill tool), không mở file SKILL.md nào, không đọc thư mục skills/." GREEN thêm "Không dùng
công cụ gọi skill (Skill tool). Đọc `<đường tuyệt đối tới worktree>/skills/code-review/SKILL.md` trước rồi làm — đây là
file duy nhất được đọc. Mở báo cáo bằng dòng "Đã đọc: `<đường tuyệt đối>`"."
Phép thay vế mở đầu ở lượt GREEN: vế "KHÔNG đọc file nào trên máy" mâu thuẫn với dòng GREEN (bảo đọc file), nên khi gửi
GREEN đổi thành "KHÔNG đọc file nào trên máy, ngoài các file nêu ở dòng trên, và các file trong `references/` mà
`SKILL.md` trỏ tới". Lượt RED giữ nguyên văn. `skill_sha` = băm cây `skills/code-review` trừ `tests/`
(`git ls-tree <commit>:skills/code-review | awk -F'\t' '$2!="tests"' | git mktree`). Gốc (chỉ cho ba kịch bản cũ):
kịch bản 1 đọc bản private `code-review-routing` (mốc `4c0fdc57`) + superpowers `requesting-code-review`, kịch bản 2
đọc `requesting-code-review` + `code-reviewer.md`, kịch bản 3 đọc `receiving-code-review`.
