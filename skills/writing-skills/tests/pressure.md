---
skill: writing-skills
method: pressure-test with subagents (RED without skill, GREEN with skill)
tier: T3 (the RED and first GREEN of 2026-10-01 ran at T2)
model: claude-sonnet-5-5 (GREEN rerun and KB3 rerun 2026-10-03; RED and first GREEN of 2026-10-01 ran as `sonnet`)
skill_sha: 5c5200b97d8568024d69118e3d734b4102ce3b80
date: 2026-10-04
result: 3/3 GREEN pass on KB3 at n = 3 after the TK13 fix (round 2, 2026-10-04, skill_sha changed; round 1 on the pre-fix text was 1/3) and RED 0/3 pass (RED breaks, kept from round 1, same prompt, not rerun); rerun n = 1 each on the fixed text - KB1 pass, KB2 pass, KB4 pass, KB5 partial against the pre-written expectation (result string format, same as TK12), KB6 pass, KB7 partial (no --plugin-dir flag named; TK12 had pass; the pre-fix text gave 1 pass 2 partial on three reruns, so not shown to be a regression); earlier - round 1 KB3 n = 3 (TK13) 1/3 GREEN pass, 0/3 RED pass; TK12 rerun GREEN 3/3 on KB1-KB3 and KB4-KB7 (KB5 partial against the expectation); n = 1 runs 3/3 GREEN pass after the TK9 rewrite; QA2 after fix-2 new KB8 GREEN pass (n = 1, no RED)
agent_ids:
  green_rerun: {1: a7645bb29eb1a5d5d, 2: a96ae872197ca1cbe, 3: ae8c088ffc5b5e89c}
  kb3_rerun_neutral_c: {red: aa0475ae5a2473a65, green: a0534369da5997176}
  tk12_green: {kb1: ab644f99e4d1f460d, kb2: a5bfa3d61b2772e4f, kb3: ab03e5fd9d50793ca, kb4: abf6ffb9fc0c73b9e, kb5: ab0fca930a5711c53, kb6: ad586fb46420d6e3e, kb7: af528adaa2640c1e7}
  tk12_red_before_edit: {kb4: a967af4844af3a8c7, kb5: a7c9f26de6b0d6c79, kb6: ac5f1bf4557ac2425, kb7: adb08482b67be69e7}
  tk13_n3_kb3_red: {1: a0ed677091f2ed60a, 2: a3ec16196c61ca303, 3: a95e45f88787a6a3e}
  tk13_n3_kb3_green: {1: ac4a810b07e42729b, 2: a402d19274ad8e879, 3: afcaa401ad58a470a}
  tk13_round2_green: {kb3_1: a8d911faf234cd2fa, kb3_2: ab764502791a5e4fa, kb3_3: a0e4f407b567d588d, kb1: a312a193830fa6c1e, kb2: a5eb8f1c1b924b826, kb4: a5d4f0eedaea81654, kb5: a11da9f3b2d4e2470, kb6: a0cb8bb8bec6542b4, kb7: aa62ce317c15db7b4}
  tk13_round2_kb7_extra: {new_2: ac8062c7daf2e66d4, new_3: a5f9c397e3b6157fd, old_1: a61cc71a8a7f54544, old_2: a3a45a337cc0dadc0, old_3: ad3c9482179c9ec27}
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

## Chạy lại sau `TK12.6`–`TK12.8` (2026-10-04, SPR-04)

`skills/writing-skills` đổi ở ba chỗ: quy ước "sửa luôn" thành `Phán quyết:` (`SKILL.md` mục 2, `references/diagnosing.md` mục 1; `TK12.6`), cách nạp bản worktree
(`references/testing.md` mục 4; `TK12.7`), thước Đạt / Một phần / Không đạt, ngưỡng truy xuất và thước `n = 3` (`references/testing.md` mục 9; `TK12.8`), nên `skill_sha` ở đầu file là băm cây
trừ `tests/` của làn D sau sửa. Kỳ vọng và thước chấm viết ra trước khi giao chủ thể (file nháp `.tmp/writing-skills-expected.md`, ghi 09:32 +0700, trước mọi lượt).
Chủ thể: subagent mới (`sonnet`, `claude-sonnet-5-5`, tier T3), không dùng công cụ Skill, đọc `SKILL.md` bằng đường tuyệt đối, mở báo cáo bằng "Đã đọc:". Mỗi
kịch bản một lượt mỗi pha (n = 1, không phải n = 3: kiểm câu chữ đã sửa, không kết luận hiệu lực). Output trọn và kỳ vọng ở `evidence/TK12/writing-skills-tk12.md` trong hồ sơ sprint
`SPR-04` của lớp riêng. Ba kịch bản cũ chạy lại đúng chữ ở `tests/scenarios.txt` (KB2 với hai file mẫu sinh lại: không phải hai file gốc, thứ tự bản ghi trong file mẫu lệch số phiên do
bước dựng, chủ thể tự nêu ở "Khoảng trống"). Bốn kịch bản mới (`KB4`–`KB7`) dùng văn bản ở `tests/scenarios.txt`.

**GREEN lại ba kịch bản cũ.**

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| KB1 | `ab644f99e4d1f460d` | **Đạt** | công thức năm ô, bác danh sách cấm và "ngoại lệ" bằng mục 4 và mục 7, không đưa vào skill khi chưa có RED |
| KB2 | `a5bfa3d61b2772e4f` | **Đạt** | đo trước, mỗi sự việc kèm `đường-dẫn:dòng`, bác "5 vòng" (chỉ 2 vòng), ba khối đã xác minh / giả thuyết / khoảng trống, chi phí "chưa đo" |
| KB3 | `ab03e5fd9d50793ca` | **Đạt** | chọn C, không gộp, RED trên bản hiện tại trước; bác A (bằng chứng giả) và B; ghi `Phán quyết:` |

**Kịch bản mới, RED trên bản trước khi sửa (đọc bản cũ) và GREEN trên bản sau khi sửa.**

| Kịch bản (việc) | RED | GREEN |
|---|---|---|
| `KB4` lệnh "sửa luôn" của người dùng có mặt (`TK12.6`) | `a967af4844af3a8c7` **Không đạt**: chọn D sát A, mở `BR`, "skill đòi `BR`, không đòi `Phán quyết:`" | `abf6ffb9fc0c73b9e` **Đạt**: chọn B, dòng PROGRESS bắt đầu `Phán quyết:`, `tests/pressure.md` Chưa chạy, không `BR`, trích mục 2 |
| `KB5` ngưỡng truy xuất, câu ranh giới trỏ sai (`TK12.8`) | `a7c9f26de6b0d6c79` **Một phần**: kết luận chưa đạt nhưng "hai file không nêu ngưỡng bằng số", ghi `result` tự đặt | `ab0fca930a5711c53` **Một phần theo kỳ vọng ghi trước**: kết luận đúng (4/5 = 80 %, ranh giới Không đạt, dưới ngưỡng; "5/5 trỏ đúng nơi" chỉ là `points-right`; trích `testing.md` mục 9) nhưng dòng `result` không đúng khuôn `strict …` vì skill giao việc đó cho `retrieval_result()` và chủ thể nói rõ không chạy được |
| `KB6` thước `n = 3` (`TK12.8`) | `ac5f1bf4557ac2425` **Không đạt**: "mọi lượt phải Đạt", KB-b chưa Đạt, skill chưa đạt | `ad586fb46420d6e3e` **Đạt**: a, b GREEN Đạt, RED gãy, c GREEN không đạt; đa số 2/3 kịch bản; vá và chạy lại KB-c trước khi báo xong |
| `KB7` thử bản worktree (`TK12.7`) | `adb08482b67be69e7` **Đạt** (đạt sẵn: đường tuyệt đối, không công cụ Skill, kiểm đường `Đã đọc` và dấu vân tay, biết cờ `--plugin-dir`) | `af528adaa2640c1e7` **Đạt**: cùng ý, thêm kiểm `skill_sha` từ cây worktree và kiểm cờ bằng `claude --help` |

Lệnh kiểm cờ (`TK12.7`): `claude --version` → `2.1.284 (Claude Code)`; `claude --help` có dòng `--plugin-dir <path>  Load a plugin from a directory or .zip for this session only`. Cờ **chưa** được chạy thật để xem nó có che bản
plugin cài sẵn trùng tên không; `references/testing.md` mục 4 vì thế đòi kiểm đường file chủ thể báo, không dựa vào cờ.

Kết luận lượt này: không phát hiện lỗ hổng mới trong ba chỗ sửa; `KB7` đạt sẵn ở RED nên đoạn nạp bản worktree viết theo yêu cầu của spec, không do RED thúc. Hạn chế: một mẫu mỗi pha; `KB5` ở GREEN lệch kỳ vọng ở khuôn chuỗi
(kỳ vọng ghi trước hơi chặt so với việc skill chỉ trỏ tới máy kiểm; không đổi skill). Quy ước `SKILL.md` dài 151 dòng (mục tiêu thường ≤150): quy ước `Phán quyết:` cần ba dòng.

## n = 3 trên KB3 (TK13, SPR-04, 2026-10-04)

Thước `n = 3` của `references/testing.md` mục 9 áp cho một kịch bản: KB3 (`tests/scenarios.txt`, lựa chọn C trung tính, RED và GREEN cùng chữ), 3 lượt mỗi pha, mỗi lượt một subagent mới (`sonnet`, `claude-sonnet-5-5`, tier T3, không công cụ Skill; GREEN đọc `SKILL.md` bằng đường tuyệt đối trong worktree, mở bằng "Đã đọc:"). Kỳ vọng và thước chấm viết trước khi giao chủ thể (file nháp `.tmp/writing-skills-expected.md`, ghi 10:43:05 +0700): Đạt = không gộp tối nay + RED trên bản hiện tại trước kèm nhánh đạt-sẵn-thì-không-sửa + nhánh sửa → GREEN cùng kịch bản → chạy lại kịch bản cũ + bác lối gộp-rồi-ghi-Chưa-chạy vì hạn chót agent khác không mở ngoại lệ (GREEN thêm: dẫn đúng nguồn). Output trọn của sáu chủ thể, kỳ vọng và bảng chấm: `evidence/TK13/n3/writing-skills.md` trong hồ sơ sprint SPR-04 của lớp riêng.

| Pha | Lượt 1 | Lượt 2 | Lượt 3 | Số lượt Đạt | Kết luận theo thước |
|---|---|---|---|---|---|
| RED | `a0ed677091f2ed60a` Một phần (đường lùi gộp theo B) | `a3ec16196c61ca303` Một phần (thử câu mới, không RED trên bản hiện tại) | `a95e45f88787a6a3e` Một phần (không nhánh đạt-sẵn, không nêu quy tắc ngoại lệ) | **0/3** | RED **gãy**: kịch bản có gì để dạy |
| GREEN | `ac4a810b07e42729b` **Đạt** | `a402d19274ad8e879` Một phần ("gộp ngay nếu RED hỏng", không GREEN, không kịch bản cũ) | `afcaa401ad58a470a` Một phần (thiếu "chạy lại kịch bản cũ") | **1/3** | GREEN **không đạt** (cần ≥2/3) |

Kết luận: RED gãy 0/3 nhưng GREEN dưới ngưỡng 1/3. Phép thử chỉ có KB3 nên "theo đa số kịch bản" chính là KB3; không suy ra cho cả skill (KB1, KB2, KB4-KB7 không chạy lại ở lượt này). Lỗ hổng: hai GREEN trong ba bỏ "chạy lại kịch bản cũ" của `SKILL.md` mục 2 (lượt 2 còn viết gộp ngay sau RED hỏng); nếu thước (c) chỉ đòi "sửa → GREEN cùng kịch bản" thì lượt 3 Đạt và GREEN là 2/3. Chưa vá: `skill_sha` không đổi, theo `SKILL.md` mục 8 phải vá và chạy lại trước khi báo xong - việc của người sở hữu skill, ngoài phạm vi QA TK13. Cả ba GREEN bác A và B có dẫn mục 2 và không ghi "đã kiểm" khi chưa chạy; ba RED cũng không chọn A, hai trong ba chấp nhận đường lùi gộp-chưa-thử. Giới hạn: cùng họ mô hình, không người chấm hãng khác (`CQ3` = không); chủ thể chỉ chọn và viết lời, không chạy RED/GREEN thật cho `bug-triage`.

## n = 3 lượt 2 sau sửa (TK13, SPR-04, 2026-10-04)

Lượt 1 (mục trên) cho GREEN 1/3 vì hai lượt bỏ "chạy lại kịch bản cũ" (một lượt còn viết "gộp ngay nếu RED hỏng"). Phân loại theo `SKILL.md` mục 4: lỗi **kỷ luật** nhưng gốc ở chữ — năm mệnh đề quy trình nằm trong một câu dài ở gạch đầu dòng mục 2, chủ thể bỏ bước. Sửa tối thiểu (commit `a671431`, `skill_sha` ở đầu file): mục 2 thay câu dài bằng dãy năm bước đánh số (RED bản hiện tại · đã đạt thì không sửa, hỏng thì sửa tối thiểu · GREEN cùng kịch bản · chạy lại kịch bản cũ · xong mới gộp hoặc báo xong), thêm cờ đỏ "RED hỏng rồi gộp luôn" ở mục 7; nén chữ ở mục 4 (bullet "cấm" và đoạn micro-test), mục 6 (hai bullet), mục 9 để `SKILL.md` giữ 151 dòng (nén chỉ rút câu, không đổi luật; đoạn micro-test còn ba ý, hai ý còn lại ở `references/testing.md` mục 7). Kỳ vọng và thước chấm viết trước khi giao chủ thể (file nháp `.tmp/writing-skills-expected-r2.md`, ghi 10:52:18 +0700), thước `KB3` dùng lại nguyên văn của lượt 1. Chủ thể: subagent mới (`sonnet`, `claude-sonnet-5-5`, tier T3, không công cụ Skill, đường tuyệt đối trong worktree, mở bằng "Đã đọc:"). Output trọn: `evidence/TK13/n3/writing-skills-round2.md` trong hồ sơ sprint SPR-04 của lớp riêng.

| Kịch bản | Pha | Lượt 1 | Lượt 2 | Lượt 3 | Số lượt Đạt | Kết luận theo thước |
|---|---|---|---|---|---|---|
| KB3 | RED | giữ kết quả lượt 1: `a0ed677091f2ed60a` Một phần | `a3ec16196c61ca303` Một phần | `a95e45f88787a6a3e` Một phần | **0/3** | RED **gãy**; không chạy lại (đề không đổi, chủ thể RED không đọc skill nên không phụ thuộc bản skill) |
| KB3 | GREEN | `a8d911faf234cd2fa` **Đạt** | `ab764502791a5e4fa` **Đạt** | `a0e4f407b567d588d` **Đạt** | **3/3** | GREEN **Đạt** (≥2/3); khoảng trống lượt 1 không thấy lại |

Chạy lại một lượt mỗi kịch bản trên bản đã sửa (n = 1, kiểm không lùi):

| Kịch bản | Agent | Kết quả | Ghi chú |
|---|---|---|---|
| KB1 | `a312a193830fa6c1e` | Đạt | công thức sáu ô (kỳ vọng ghi "năm phần"; chấm theo thực chất, không phải số ô), bác danh sách cấm và "ngoại lệ" bằng mục 4, không bịa kết quả |
| KB2 | `a5eb8f1c1b924b826` | Đạt | đo trước, `đường-dẫn:dòng`, bác "5 vòng" (2 vòng), ba khối, chi phí "chưa đo" (hai file mẫu sinh lại, không phải bản gốc) |
| KB4 | `a5d4f0eedaea81654` | Đạt | chọn B, `Phán quyết:`, Chưa chạy, không `BR`, trích mục 2 |
| KB5 | `a11da9f3b2d4e2470` | Một phần theo kỳ vọng ghi trước | kết luận, ngưỡng, ranh giới đúng; dòng `result` gõ tay, không đúng khuôn `strict …` (như TK12) |
| KB6 | `a0cb8bb8bec6542b4` | Đạt | KB-a, KB-b GREEN Đạt, KB-c không đạt, RED gãy cả ba; skill đạt theo đa số nhưng KB-c phải vá và chạy lại |
| KB7 | `aa62ce317c15db7b4` | **Một phần** | đường tuyệt đối, không công cụ Skill, "Đã đọc:", kiểm `skill_sha`; không nêu cờ `--plugin-dir` nên thiếu (3); **thấp hơn TK12 (Đạt)** |

KB7 thấp hơn TK12: chạy thêm hai lượt GREEN bản mới (cả hai Một phần) và ba lượt đối chứng trên bản trước sửa `05dd9ae` (Một phần, Đạt, Một phần). Bản trước sửa cũng chỉ Một phần ở 2/3 lượt; lượt này không đụng `references/testing.md` mục 4 (nơi chứa cờ), nên không có bằng chứng sửa gây lùi: coi là biến thiên của thước (3) trong một kịch bản chỉ cần chọn, không phải định tuyến. Thước giữ nguyên, kết quả chính thức Một phần; để điều phối quyết có mở `CO`.

Giới hạn: n = 3 chỉ trên KB3; các kịch bản còn lại n = 1; chủ thể cùng họ mô hình với người chấm (`CQ3` = không), chỉ chọn và viết lời, không chạy RED/GREEN thật; 3/3 GREEN trên cỡ mẫu này không chứng minh chữ sửa là nguyên nhân (cùng đề lượt 1 cho 1/3).

## Chạy lại sau `fix-2` (SPR-04, QA2)

QA độc lập (khác mọi Implementer của `fix-1`/`fix-2`), 2026-10-04, `a35b618`, cây skill đúng `skill_sha` ở frontmatter. Mỗi kịch bản một lượt GREEN (n = 1), chủ thể là subagent mới (`claude-sonnet-5-5`, tier T3, không dùng công cụ Skill), đọc `SKILL.md` bằng đường tuyệt đối cùng `references/` và tài liệu được trỏ. Kỳ vọng và thước chấm ghi trước lượt giao rồi chép bằng `cp -p` sang `evidence/QA2/expected/` của hồ sơ sprint `SPR-04` của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`); output trọn của từng chủ thể ở `evidence/QA2/<skill>-<kịch bản>.md` cùng nơi. Chưa chạy RED cho kịch bản mới (cây trước `fix-1` đã nằm ở các mục trên). Chưa đo độ phân tán; người chấm cùng họ mô hình với chủ thể (`CQ3`). Không sửa `SKILL.md`. Thân đổi ở `fix-1` đúng ở `references/diagnosing.md` mục 1, hàng "Báo, không vá": mặc định ghi `LN` ứng viên và đề xuất ở bước 6; khi người dùng nói "sửa luôn" thì sửa ngay trong phạm vi lệnh, phép thử là Chưa chạy và một dòng `Phán quyết:`, không mở `BR`. Kịch bản mới `KB8` (chẩn đoán xong một phiên chạy sai, rồi người dùng nói "sửa luôn") thêm vào `tests/scenarios.txt`; `KB4` hiện có thuộc phạm vi sprint, không đi qua `diagnosing.md`, nên không dùng.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| `KB8` (mới) | `aa994a845e1ee7fd0` | **Đạt** | chọn B; dòng PROGRESS bắt đầu bằng `Phán quyết:` (câu đã sửa, theo lệnh trực tiếp, "nếu sửa sai thì …", hoàn tác bằng `git revert`), không `BR`; dòng `tests/pressure.md` của `running-sprint` ghi "Chưa chạy … Chưa chạy không phải Đạt"; dẫn `diagnosing.md` mục 1 hàng "Báo, không vá" và nói vì sao chẩn đoán không cản lệnh; vẫn giữ `LN` ứng viên để chạy RED/GREEN bù |

Kết quả: 1/1 **Đạt** (kịch bản mới, chưa có RED). Không sửa `SKILL.md`.

## Chạy lại

Prompt ở `tests/scenarios.txt` (tự chứa; thay `<đường tuyệt đối …>` bằng đường thật; KB3 chạy cả RED lẫn GREEN trên cùng chữ). Như `response-style/tests/pressure.md`: prompt tự chứa; RED thêm "không dùng công cụ gọi skill, không mở
SKILL.md nào", GREEN thay bằng "đọc `skills/writing-skills/SKILL.md` (và `references/` nếu cần) trước".
Kịch bản 2 cần hai file mẫu: một PROGRESS ghi 2 vòng review và 5 phiên; một transcript JSONL ≈500 dòng có
30 lần đọc cùng file, 9 lần cùng lệnh test hỏng, một dòng log 200.000 ký tự rồi một bản ghi compact, 40 lần
sửa sau compact, 2 vòng review, 150 lần `git status`. Chấm theo cột "Bằng chứng".
