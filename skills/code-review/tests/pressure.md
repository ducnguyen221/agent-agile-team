---
skill: code-review
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5
tier: T3
skill_sha: 43ee2ca2480c8f4b403230a753c133dd5acac079
date: 2026-10-23
result: 11/11 GREEN pass on the current tree (3 new cr-9 to cr-11, plus cr-1 to cr-8 rerun); RED on the three new scenarios 0/3 pass (3 partial); earlier rounds 2026-10-04 8/8 GREEN pass
agent_ids:
  red: {cr4: a271d593244c9237e, cr5: aaecd867d1856eebe, cr6: a07176d4fa0bdc33a}
  green: {cr4: aad5d938c1bad1e0e, cr5: a07ac7d0967aa0527, cr6: a401b01bb0a78d377}
  green_rerun: {cr1: aaed3b375c841301f, cr2: aae7a4f1a80410b6f, cr3: ab43029ce6c071070}
  red_2026_10_23: {cr9: a0c1c8abd434b6145, cr10: a26dffdb35867a976, cr11: a3a6377c2ba3459e1}
  green_2026_10_23: {cr9: a72bd8f0c166f8747, cr10: a4bdaddbbd5de4ea8, cr11: a58168d6fcfc6ce45, cr1: a9cca050160f4dcb2, cr2: acbcb9f78dc1bf46b, cr3: a66451a61a33945c5, cr4: a17575bbc4dfd182d, cr5: ab85b4ba11f450009, cr6: adec480097940b5e9, cr7: af66496e06dba6fe5, cr8: a4e61234155bca6b4}
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

## Lượt 2026-10-23 — `REVIEW.md`, hội tụ, nhãn `có từ trước`, bậc rủi ro

> **Kết luận:** ba kịch bản mới (cr-9 đến cr-11) **GREEN 3/3 Đạt**; RED (không có skill) **Đạt một phần 3/3**: chủ thể
> từ chối đúng hướng nhưng thiếu phần skill thêm (đọc `REVIEW.md` ở `BASE` kèm phân vai lệnh harness ↔ brief; vòng sau chỉ đọc
> diff từ mốc trước; nhãn `có từ trước` kèm kết cục và mở việc theo dõi). Tám kịch bản cũ (cr-1 đến cr-8) chạy lại GREEN trên
> cây mới: **8/8 Đạt**, tổng **11/11**.

Bảng có 3 **kịch bản** (id) mới và kết quả hai pha:

| Kịch bản | RED (agent) | GREEN (agent) | Dòng đạt (viết trước) | Kết quả GREEN |
|---|---|---|---|---|
| `cr-9` | Đạt một phần (`a0c1c8abd434b6145`) | `a72bd8f0c166f8747` | brief đọc `git show <BASE>:REVIEW.md`; thay đổi `REVIEW.md` thành Ghi chú + bậc cao; nói phân vai lệnh harness ↔ quy trình | **Đạt**: chọn B; brief chép lệnh đọc `REVIEW.md` ở `BASE`; việc sửa `REVIEW.md` ghi thành `RF` Ghi chú, bậc cao; lệnh review của harness chỉ nhắc, không làm cổng |
| `cr-10` | Đạt một phần (`a26dffdb35867a976`) | `a4bdaddbbd5de4ea8` | không mở vòng 4, không hook gọi model; ghi lớp lỗi, báo người dùng hai lựa chọn; vòng sau chỉ đọc diff từ mốc trước | **Đạt**: chọn B; dẫn mục 5.1; nêu lớp lỗi lặp; ba lựa chọn cho người dùng gồm một vòng đọc hẹp chỉ phần diff sửa; bác hook Stop gọi review |
| `cr-11` | Đạt một phần (`a3a6377c2ba3459e1`) | `a58168d6fcfc6ce45` | lỗi 1 nhãn `có từ trước` → việc theo dõi; lỗi 2 vẫn Chặn và dừng hỏi; không `RF` nào thiếu kết cục | **Đạt**: nhãn `có từ trước`, kết cục `có từ trước → CO` kèm dòng theo dõi; lỗi lộ dữ liệu giữ Chặn, dừng hỏi, gọi `security-reviewer`; không gộp khi còn Chặn mở |

Tám kịch bản cũ chạy lại GREEN n = 1 (agent mới, cùng model và tier):

| Kịch bản | Agent | Kết quả |
|---|---|---|
| `cr-1` | `a9cca050160f4dcb2` | **Đạt**: ba reviewer có lý do, năm loại không giao vì diff không có tín hiệu; ứng viên null bị loại ở cổng xác minh |
| `cr-2` | `acbcb9f78dc1bf46b` | **Đạt**: reviewer riêng cho cả nhánh, `BASE` bằng `git merge-base`, brief theo khuôn mới |
| `cr-3` | `a66451a61a33945c5` | **Đạt**: phản bác mục sai bằng bằng chứng, hỏi lại mục mơ hồ, không sửa nửa chừng |
| `cr-4` | `a17575bbc4dfd182d` | **Đạt**: sửa và test hồi quy là một lựa chọn, không `xfail`; mục không kịp giờ giữ mở |
| `cr-5` | `ab85b4ba11f450009` | **Đạt**: năm bước tìm hàm trùng, phân biệt trùng ý và trùng tên, trùng lặp mức Nên sửa |
| `cr-6` | `adec480097940b5e9` | **Đạt**: mô tả PR là lời khai; đọc ngoài diff cho giá trị mới; không ghi Đạt khi chưa đủ chứng cứ |
| `cr-7` | `af66496e06dba6fe5` | **Đạt**: ba chuyên gia song song (TypeScript, React, test), không dùng reviewer chung |
| `cr-8` | `a4e61234155bca6b4` | **Đạt**: `risk_tags` có `rules` → hai reviewer độc lập cộng lượt bảo mật |

**Giới hạn của lượt này:**
- Mỗi kịch bản một lượt mỗi pha (n = 1); người chấm là điều phối sprint, chưa có người chấm độc lập riêng cho các lượt GREEN.
- Chủ thể đọc đúng đoạn dòng kịch bản của mình từ tệp thay vì nhận trong tin nhắn; vẫn cấm công cụ Skill.
- `cr-8` không mở `references/reviewer.md` và thẻ kiểm định kép; Đạt dựa trên phần `SKILL.md` nêu về hai tệp đó. `cr-1` không mở `references/`.
- Chủ thể trả lời bằng văn bản trong môi trường giả lập; chưa thử trong một sprint thật.

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

## Chạy lại sau `fix-2` (SPR-04, QA2)

QA độc lập (khác mọi Implementer của `fix-1`/`fix-2`), 2026-10-04, `a35b618`, cây skill đúng `skill_sha` ở frontmatter. Mỗi kịch bản một lượt GREEN (n = 1), chủ thể là subagent mới (`claude-sonnet-5-5`, tier T3, không dùng công cụ Skill), đọc `SKILL.md` bằng đường tuyệt đối cùng `references/` và tài liệu được trỏ. Kỳ vọng và thước chấm ghi trước lượt giao rồi chép bằng `cp -p` sang `evidence/QA2/expected/` của hồ sơ sprint `SPR-04` của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`); output trọn của từng chủ thể ở `evidence/QA2/<skill>-<kịch bản>.md` cùng nơi. Chưa chạy RED cho kịch bản mới (cây trước `fix-1` đã nằm ở các mục trên). Chưa đo độ phân tán; người chấm cùng họ mô hình với chủ thể (`CQ3`). Không sửa `SKILL.md`. Thân `SKILL.md` đổi ở `fix-1`: bảng chuyên gia thêm `typescript-reviewer`, `react-reviewer` (chạy cạnh), `test-analyzer`, `code-reviewer` và đoạn nói `code-reviewer` với brief `references/reviewer.md` là hai cách giao cùng một lượt tổng quát; hàng bảng mục 1 thêm `rules` vào vùng nâng cấp bảo mật; mục 4 bước 2 thêm `dual-review`. Hai kịch bản mới `cr-7`, `cr-8` thêm vào `tests/scenarios.txt`; GREEN đọc thêm `roles/verifier/dual-review.md` (tài liệu được trỏ).

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| `cr-7` (mới) | `aaddfa0723229f122` | **Đạt** | chọn B; `typescript-reviewer` + `react-reviewer` ("chạy cạnh nhau") + `test-analyzer`, mỗi agent một brief, song song, cùng gói diff từ `BASE`, ghi vai · tier · model; cổng xác minh (ứng viên không `file:dòng` → tối đa Ghi chú); không kéo agent Python; không thay chuyên gia bằng `code-reviewer` |
| `cr-8` (mới) | `a2bf84b93f0d1d143` | **Đạt** | chọn B; hai Tech Reviewer T1 độc lập, nhãn khác nhau và khác người làm, brief không gồm lịch sử phiên hay kết luận bên kia; cả hai Đạt mới Đạt, bên nào khác Đạt = chưa Đạt, gộp `RF`, chạy lại cả hai bằng agent mới; lượt bảo mật giữ (cộng thêm); tin Architect không giảm về một bên |

Kết quả: 2/2 **Đạt** (kịch bản mới, chưa có RED). Không sửa `SKILL.md`.

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
