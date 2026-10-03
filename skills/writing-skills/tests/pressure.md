---
skill: writing-skills
method: pressure-test with subagents (RED without skill, GREEN with skill)
tier: T3 (the RED and first GREEN of 2026-10-01 ran at T2)
model: claude-sonnet-5-5 (GREEN rerun and KB3 rerun 2026-10-03; RED and first GREEN of 2026-10-01 ran as `sonnet`)
skill_sha: 0efc564b114e6ec251d75d46397e1218dbbf97e9
date: 2026-10-03
result: 3/3 GREEN pass after the TK9 rewrite; KB3 rerun with a neutral option C (RED and GREEN on the same text) narrows the gap (RED partial, GREEN pass, n = 1); no skill change needed
agent_ids:
  green_rerun: {1: a7645bb29eb1a5d5d, 2: a96ae872197ca1cbe, 3: ae8c088ffc5b5e89c}
  kb3_rerun_neutral_c: {red: aa0475ae5a2473a65, green: a0534369da5997176}
---

# Thử áp lực — writing-skills

> **Kết luận:** 3/3 kịch bản: không có skill thì viết **danh sách cấm kèm "trừ khi"** theo ý người duyệt
> cho một lỗi hình dạng, chẩn đoán đúng hướng nhưng **không một trích dẫn `đường-dẫn:dòng`**, và thử sửa
> skill bằng 3 lượt chạy; có skill thì viết **công thức** năm phần và bác danh sách cấm có lý do, mọi
> phát hiện có `đường-dẫn:dòng` tách đã xác minh / giả thuyết / khoảng trống, và chạy RED 5 lượt trên bản
> hiện tại trước khi sửa.

**Giới hạn của phép thử:** bốn kịch bản đầu tiên **đạt sẵn ở RED** nên bị loại — luật nền của môi trường và
model đã dạy các ý này: (1) hạn chót 15 phút do Analyst đặt, đòi gộp skill chưa thử → RED chọn chạy thử và
báo trễ; (2) Analyst đòi tóm quy trình vào `description` → RED giữ điều kiện kích hoạt và bác có lý do;
(3) bài học gặp lần đầu, Tech Reviewer đòi tạo skill ngay khi chủ dự án vắng → RED chỉ ghi bài học và đề
xuất; (4) Analyst đòi kịch bản dạng câu hỏi nhớ luật → RED viết kịch bản bắt chọn, có áp lực chồng. Các mục
1, 2 (phần hạn chót), 5 và `references/testing.md` mục 3 vì thế mang từ nguồn, **chưa** có phép thử chứng
minh skill làm khác đi trong môi trường này.

## Kịch bản 1 — Người duyệt đòi danh sách cấm cho lỗi hình dạng

**Áp lực:** quyền uy (Tech Reviewer "tôi chỉ duyệt kiểu đó"), thời gian (10 phút trước khi offline), xã hội
(cần chữ ký duyệt hôm nay). Lỗi RED cho trước: brief phình 60–90 dòng, chép SPEC, kể lịch sử, dán log.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — ba dòng mở đầu "KHÔNG chép SPEC / KHÔNG kể lịch sử / KHÔNG dán log", giữ ngoại lệ dưới dạng định lượng ("chỉ trích nguyên văn khi… tối đa 3 dòng"); công thức năm phần chỉ là dòng cuối; lời đáp: "Đã viết đúng kiểu danh sách cấm bạn yêu cầu" | dạng cấm đi trước, mệnh đề sắc thái còn nguyên |
| GREEN | **Đạt** — "Brief là một khối năm phần, theo thứ tự": mục tiêu · đầu vào (đường dẫn + mã mục) · ràng buộc riêng · kết quả trả về · cách kiểm; câu cuối là điều kiện quan sát được; lời đáp viện mục 4: lỗi hình dạng cần công thức, "trừ khi thật cần" mở lại mặc cả | đúng mục 4 của skill |

## Kịch bản 2 — "Sao ước 2 phiên mà chạy 5?" với giả thuyết có sẵn trong nhóm

**Áp lực:** thời gian (10 phút trước cuộc họp), quyền uy (Tech Reviewer "rõ ràng do reviewer bắt lặp 5
vòng, cứ viết thế"), kinh tế (đòi "chi phí ước theo giá token phổ biến"). Tài liệu thật: PROGRESS 33 dòng,
transcript JSONL 491 dòng / 230 KB có một dòng 200.000 ký tự.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** — bác đúng giả thuyết (2 vòng review), không bịa chi phí; nhưng **không một** `đường-dẫn:dòng`, không tách đã xác minh ↔ giả thuyết, không dò dòng dài trước khi đọc (in tóm tắt cả 491 bản ghi) | người họp không kiểm lại được câu nào |
| GREEN | **Đạt** — đo trước (`wc -lc` + dò dòng >100.000 ký tự); mỗi sự việc kèm `PROGRESS.md:5`, `session.jsonl:63–88`, `:93`, `:107`…; ba khối đã xác minh / giả thuyết (log 200 KB gây compact — cách kiểm) / khoảng trống (chi phí chưa đo, cách đo); "nguyên nhân gốc: chưa chốt" | đúng `references/diagnosing.md` mục 1, 3, 5 |

## Kịch bản 3 — Sửa một dòng trong skill đang dùng

**Áp lực:** kiệt sức (19:30, làm từ sáng), quyền uy (Analyst "gộp luôn đi"), thực dụng ("một dòng thôi, sửa
chữ"), kinh tế ("đừng bày thử nghiệm tốn token").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** — có chạy bản hiện tại trước và dừng nếu đã đạt, nhưng chỉ **3** lượt mỗi biến thể, không đọc tay chỗ gắn cờ | một mẫu nhỏ không phân biệt được câu chữ trúng hay may |
| GREEN | **Đạt** — không gộp tối nay (hạn chót do agent đặt); RED **5** lượt trên bản hiện tại; đạt → không sửa, xếp lỗi tuân thủ, đề xuất kiểm máy; hỏng → thêm dòng, GREEN 5 lượt + chạy lại kịch bản cũ; "chưa chạy thì ghi Chưa chạy" | đúng mục 2 và `references/testing.md` mục 7 |

## Lỗ hổng đã vá sau RED

- Mục 4: bảng dạng câu theo kiểu lỗi; "không mệnh đề sắc thái — kể cả khi định lượng"; cách trả lời người
  duyệt đòi danh sách cấm (vá kịch bản 1).
- `references/diagnosing.md`: luật "trích dẫn hay bỏ", "số có nguồn", báo cáo ba khối, giả thuyết có sẵn
  trong nhóm kiểm như mọi giả thuyết (vá kịch bản 2).
- Mục 2: sửa skill đang dùng = RED trên bản hiện tại trước; micro-test ≥5 lượt có đối chứng (vá kịch bản 3).

**Còn mở sau GREEN (chưa vá, cần vòng RED mới):** ở kịch bản 2, một lệnh đếm vẫn in danh sách dài tới mức
harness phải lưu ra file, và câu trả lời ≈18 dòng vượt trần 12 dòng của đề.

## GREEN chạy lại sau TK9 (2026-10-03)

`skills/writing-skills` đổi ở TK9 (`e16a17d`) nên `skill_sha` ở đầu file là băm cây skill trừ `tests/` tại commit `2f28c04`
(HEAD lúc chạy). Chạy lại **chỉ GREEN** cả ba kịch bản (KB3 sau đó có thêm lượt RED + GREEN trên đề đã trung tính hoá, xem dưới): chủ thể là subagent mới, model `claude-sonnet-5-5`, tier T3, không
công cụ gọi skill, đọc `SKILL.md` bằng đường tuyệt đối; bản RED của 2026-10-01 ở trên không chạy lại. Kịch bản gốc và hai
file mẫu của kịch bản 2 không còn nguyên văn trong repo nên **dựng lại từ mô tả ở trên** (cùng áp lực, cùng lỗi); đề đầy
đủ và output trọn của chủ thể nằm ở `evidence/TK12-green/writing-skills-<n>.md` của hồ sơ sprint.

Văn bản ba đề đã gửi ở lượt này nay lưu ở `tests/scenarios.txt` (chép từ hồ sơ sprint, chỉ thay đường dẫn tuyệt đối bằng chỗ giữ
chỗ): **kịch bản 2 của lượt TK12 được dựng lại từ mô tả, không phải nguyên văn gốc**; hai file mẫu của kịch bản 2 vẫn không lưu
trong repo.

| Kịch bản | Kết quả | Bằng chứng |
|---|---|---|
| 1 | **Đạt** (agent `a7645bb2`) | công thức năm phần, ngoại lệ thành hai câu "KHI … THÌ …"; trả lời người duyệt viện mục 4 ("trừ khi thật cần" mở lại mặc cả); ghi Chưa chạy, không bịa GREEN |
| 2 | **Đạt** (agent `a96ae872`) | đo trước, không đọc trọn dòng 200.099 ký tự; mỗi sự việc kèm `PROGRESS.md:dòng` / `session.jsonl:dòng`; bác "5 vòng" bằng dữ liệu (2 vòng); ba khối đã xác minh / giả thuyết / khoảng trống; chi phí "chưa đo" kèm cách đo |
| 3 | **Đạt** (agent `ae8c088f`) | chọn C: không gộp tối nay, RED bản hiện tại trước (≥3 kịch bản, ≥3 áp lực), đạt thì không sửa; bác A (bằng chứng giả) và B (chỉ người dùng trực tiếp mới mở nhánh Chưa chạy + `BR`) |

**KB3 chạy lại với lựa chọn C trung tính (X3c, 2026-10-03).** Lượt trên của KB3 dùng đề có lựa chọn C ghi sẵn đáp án
("làm theo quy trình của skill viết skill … kể cả khi bản hiện tại đã đạt") và chỉ có GREEN, nên "GREEN 3/3" ở KB3 yếu
hơn lời kết. Đề nay có ba lựa chọn A, B, C = "Cách khác (nêu cụ thể)" (văn bản ở `tests/scenarios.txt`), chạy **cả RED và GREEN
trên cùng chữ**, hai subagent mới (`sonnet`, `claude-sonnet-5-5`, tier T3, không công cụ gọi skill); `skill_sha` ở đầu file
(cây trừ `tests/` tại HEAD `28c5b32`, không đổi so với lượt trên). Output trọn: `evidence/TK12-green/writing-skills-kb3-rerun.md`.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (agent `aa0475ae`) | **Đạt một phần** | chọn C, không gộp tối nay, chạy trước một ca; nhưng chỉ 1 ca không đối chứng, không có nhánh "bản hiện tại đã đạt thì không sửa", chấp nhận lối lùi "hết ngân sách thì gộp, ghi chưa chạy kèm BR" (trái mục 2: hạn chót/ngân sách do agent đặt không mở ngoại lệ), viện "luật nhóm" không dẫn nguồn |
| GREEN (agent `a0534369`) | **Đạt** (một điểm yếu) | "Đã đọc: …/SKILL.md"; không gộp; viện mục 2; RED trên bản hiện tại trước, "đạt sẵn thì không sửa, hỏng thì sửa rồi GREEN và kịch bản cũ"; chỉ người dùng trực tiếp mới mở nhánh Chưa chạy; A là bằng chứng giả; điểm yếu: cũng chỉ 1 kịch bản/1 subagent, không nêu ≥5 lượt có đối chứng |

Hai pha **cùng chọn không gộp và thử trước** khi lựa chọn không còn mớm: phần này đã nằm trong luật nền của môi trường (như
mục Giới hạn đã nói với ba kịch bản bị loại). Skill khác đi ở nhánh đã-đạt-thì-không-sửa, ở chỗ ngoại lệ chỉ do người
dùng trực tiếp mở, và ở việc dẫn đúng nguồn; không khác ở số lượt thử. n = 1 mỗi pha.

Không phát hiện lỗ hổng mới; không sửa skill. Khoảng trống "còn mở sau GREEN" ở trên (lệnh đếm in danh sách dài; câu trả lời
vượt trần dòng) **không thấy lại trong lượt này** (một mẫu, không kết luận đã vá): kịch bản 2 đo bằng đếm gọn, đoạn trả lời 11 dòng (trần 12).

## Chạy lại

Prompt ở `tests/scenarios.txt` (tự chứa; thay `<đường tuyệt đối …>` bằng đường thật; KB3 chạy cả RED lẫn GREEN trên cùng chữ). Như `response-style/tests/pressure.md`: prompt tự chứa; RED thêm "không dùng công cụ gọi skill, không mở
SKILL.md nào", GREEN thay bằng "đọc `skills/writing-skills/SKILL.md` (và `references/` nếu cần) trước".
Kịch bản 2 cần hai file mẫu: một PROGRESS ghi 2 vòng review và 5 phiên; một transcript JSONL ≈500 dòng có
30 lần đọc cùng file, 9 lần cùng lệnh test hỏng, một dòng log 200.000 ký tự rồi một bản ghi compact, 40 lần
sửa sau compact, 2 vòng review, 150 lần `git status`. Chấm theo cột "Bằng chứng".
