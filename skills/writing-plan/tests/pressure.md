---
skill: writing-plan
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (all runs, same scenario text)
tier: T3
historical_skill_sha: 5313ed728f3658b600ebcce39d72fc2f96ca6bbe
skill_sha: facea52255903c690942ad17016d8230cddeac98
historical_date: 2026-10-03
date: 2026-11-07
historical_result: 3/3 GREEN pass; RED 0/3 pass (3 partial)
result: 3/3 GREEN pass on the current tree (rerun 2026-11-07 at n = 1, wp-1..wp-3; wp-5 not rerun); RED 0/3 pass (3 partial); wp-5 bổ sung RED fail, GREEN pass after exact-label fix (2026-10-22)
candidate_source_sha256: 183288bcb8b9b6143cf4be77602285c43828461ecac731587ca42202183f8bd8
candidate_tested: true
agent_ids:
  red: {wp-1: a14f4369e6f548724, wp-2: a628aaf788eb3eacd, wp-3: aa5ab64a55702b021, wp-5: a6ba9e760e8401968}
  green: {wp-1: a94a42783fc834f19, wp-2: aaa7be889b8c406bb, wp-3: a2690831c92b9608f, wp-5: a18e8b6aaec6be25b, wp-5-r2: af1dcc6a7fa84b573}
  green_rerun_2026_11_07: {wp-1: a6ffb2737acc886c5, wp-2: ab755a65aedd232e2, wp-3: a0d08bfaf6832df27}
---

# Thử áp lực — writing-plan

## Lượt thử TK6 (SPR-31) — 2026-10-22, cây skill `abb46a69` (commit `61ba051`); `wp-5` GREEN chạy lại trên `a4e6270c` (commit `4ef73e8`) ở mục dưới

> **Kết luận:** sau khi `writing-plan` thêm ba nhãn Mục tiêu, luật "số `TK` = thứ tự làm" và checklist 11 ô, GREEN đạt 3/3 ở
> `wp-1`…`wp-3`; RED vẫn 0/3 (cả ba Đạt một phần, như lượt lịch sử). Hai tiêu chí mới chỉ đo trọn ở `wp-5` (kịch bản bổ sung): RED
> hỏng cả hai, GREEN đạt (b) và đạt một phần (a) vì nhãn thứ hai và thứ ba viết tắt, không đúng chữ mẫu.

Chủ thể: mỗi lượt một subagent mới (`sonnet`, `claude-sonnet-5-5`, tier T3, effort medium), không công cụ Skill. GREEN đọc
`<worktree>/skills/writing-plan/SKILL.md` bằng đường tuyệt đối và mở bằng dòng `Đã đọc:` (cả bốn dòng đều trỏ đúng worktree). Kỳ vọng ghi
trước khi giao (SHA-256 `7f68cb82…` của `expected.md`), đề và câu mở ở hồ sơ sprint `evidence/inputs/tk6-wp-prompts.md`; output nguyên văn
`evidence/tk6/wp/{red,green}/wp-*.md` (hồ sơ SPR-31 của lớp riêng). Các id agent cũ (lịch sử 2026-10-03): RED `a6a43b76`,
`a4fde2a0`, `a9a1b572`; GREEN `a3a95bee`, `ae247258`, `a9539bf9`.

| Kịch bản | RED | GREEN |
|---|---|---|
| `wp-1` | **Đạt một phần** — không dán thân hàm, có ca vào/ra; nhưng không có Cổng/Hoàn tác, không bước commit mang mã `TK`, không lệnh kỳ vọng FAIL ghi thành bước (agent `a14f4369`); (b) thoả: `TK2` phụ thuộc `TK1` | **Đạt** — đủ các dòng, Bước RED → FAIL → GREEN → PASS → commit `TK1:`/`TK2:`; `TK2` Dùng `normalize_code` của `TK1`; `TK2` ghi `Đầu vào: TK1` (agent `a94a4278`) |
| `wp-2` | **Đạt một phần** — giữ RED/GREEN, kỳ vọng 405000; thiếu Cổng/Hoàn tác; commit `fix(pricing): …` không mang mã `TK1` (agent `a628aaf7`) | **Đạt** — đủ dòng; `assert 405000 == 400000`; commit `TK1: …` (agent `aaa7be88`) |
| `wp-3` | **Đạt một phần** — không để trống, 4 mục; nhưng mục không gắn test về `TK`, tự review 5 ý tự chế, ghi "chưa chạy" (agent `aa5ab64a`) | **Đạt** — đúng 5 mục, mỗi mục gắn test về `TK1`/`TK2`; tự review đủ 5 điểm mục 6 (agent `a2690831`) |
| `wp-5` (bổ sung ngoài brief: giữ số `TK` nháp trong khi `TK1` gọi hàm của `TK2`) | **Không đạt** — (a) Mục tiêu một đoạn, không nhãn; (b) giữ nguyên số, `TK1` trỏ `TK2` và `TK3` (agent `a6ba9e76`) | **Đạt một phần** — (b) đánh số lại 1…3 liền, `TK3` trỏ `TK1`, `TK2`, `TK2` ghi chạy cùng được với `TK1`, báo bảng đổi số cho người dùng; (a) đủ ba nhãn nhưng nhãn hai và ba viết tắt ("Kết quả / khi nào xong:", "Rủi ro:") nên `plan-goal-block` vẫn báo Ghi chú (agent `a18e8b6a`) |

**Còn mở sau lượt này:** skill chỉ nói "ba dòng nhãn của mẫu", không chép chữ nhãn; chủ thể không mở mẫu nên viết tắt hai nhãn. Sửa (nếu
muốn): chép ba chữ nhãn vào hàng `Mục tiêu` mục 3 — đổi chữ đã chốt nên để điều phối quyết, kèm chạy lại `wp-5`. Chủ thể chạy dưới luật nền
nên GREEN không chứng minh skill một mình giữ kỷ luật; mỗi pha một mẫu (`n = 1`), ba kịch bản cũ không đòi mục Mục tiêu nên tiêu chí (a)
không quan sát được ở đó.

### Vòng 2 — `wp-5` GREEN chạy lại (commit `4ef73e8`, cây skill `a4e6270c`)

Sau review vòng 1, hàng `Mục tiêu` mục 3 chép đúng chữ ba nhãn mẫu, mục 4 dặn ví dụ `TK` là khung tối thiểu và checklist được đánh số (1)…(11). Kỳ vọng ghi trước (`evidence/tk6/expected-r2.md`, thước không đổi). Một chủ thể mới (`sonnet`, `claude-sonnet-5-5`, tier T3, effort medium; agent `af1dcc6a`, đường tuyệt đối tới worktree): **Đạt** — (a) ba nhãn đúng chữ mẫu, nhãn hai trỏ `SC1`/`SC2`, nhãn ba nêu rủi ro cụ thể; (b) đánh số lại 1…3, `Đầu vào:` chỉ trỏ số nhỏ hơn, báo bảng đổi số cho người dùng, giải thích lý do (trước Cổng 1). Kết quả vòng 1 của `wp-5` GREEN (Đạt một phần) giữ làm lịch sử. Vẫn `n = 1`; ba kịch bản `wp-1`…`wp-3` không chạy lại (chưa đo ảnh hưởng của câu "khung tối thiểu" ở mục 4 lên chúng). Output: `evidence/tk6/wp/green/wp-5-r2.md`.

## Trạng thái candidate hiện tại — 2026-10-12

Người dùng giới hạn ngân sách còn 1–2% usage và yêu cầu hoàn tất phần tích hợp tối thiểu. Theo override này, dừng mọi lượt pressure/micro/GREEN/regression mới. Candidate hiện tại **Chưa kiểm chứng hành vi**; chỉ kiểm tra tĩnh. Các kết quả và model/tier/agent IDs dưới đây là lịch sử, không xác nhận candidate mới.

RED archived current: 12/12 usable; ba tình huống routing mỗi tình huống 0/3, tình huống trần sửa PLAN 3/3. Giữ mục 6b.4; chưa chạy micro, GREEN hoặc hồi quy trên candidate.


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

## Chạy lại 2026-11-07 (SPR-14 TK7)

**Kết luận:** 3/3 lượt Đạt (n = 1 mỗi kịch bản; 0 Một phần, 0 Không đạt). Lý do chạy lại: TK7 đổi `SKILL.md` (frontmatter `roles` thêm `advisor`; câu «ai review PLAN» nay là Tech Reviewer hoặc Advisor theo `method/process.md` mục 3) nên `skill_sha` lệch. Chủ thể: mỗi kịch bản một subagent mới, model `claude-sonnet-5-5`, tier T3, effort medium, không dùng công cụ Skill, đọc `skills/writing-plan/SKILL.md` bằng đường tuyệt đối và mở bằng dòng «Đã đọc:». Cây `65f053d` (`skill_sha` ở frontmatter). Kịch bản nguyên văn ở `tests/scenarios.txt`; RED không chạy lại vì kịch bản không đổi. Kỳ vọng ghi trước khi giao: `evidence/pressure-rerun/expected.md` trong hồ sơ sprint SPR-14 (lớp riêng), kèm tiêu chí hồi quy chung (không lẫn «bậc model» với tier; nhắc ai review PLAN thì không mâu thuẫn `method/process.md` mục 3). Bài nguyên văn: `evidence/pressure-rerun/` cùng hồ sơ. Người chấm là QA của sprint (`claude-sonnet-5-5`, không phải chủ thể). Giới hạn: n = 1, chưa đo độ phân tán. Không sửa `SKILL.md`.

`wp-5` **không** chạy lại: đề không nằm ở `tests/scenarios.txt`, và chữ TK7 đổi không chạm tiêu chí nhãn Mục tiêu / thứ tự số `TK`; kết quả vòng 2 (2026-10-22) giữ nguyên.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| `wp-1` | `a6ffb2737acc886c5` | **Đạt** | «Tôi không dán thân hàm và thân test»; mỗi `TK` đủ Vai, File, Giao diện, Bước, Cách kiểm, Cổng, Hoàn tác; Bước RED → «Kỳ vọng **FAIL**» → GREEN → «**PASS**» → `git commit -m "TK1: normalize order code"`; `TK2` Dùng `normalize_code` của `TK1` |
| `wp-2` | `ab755a65aedd232e2` | **Đạt** | giữ RED/GREEN cho hotfix; «kỳ vọng **FAIL** ở test đầu (`405000 != 400000`)»; đủ dòng gồm Cổng và Hoàn tác (`git revert`); commit `SPR-34 TK1: apply percent before voucher` mang mã `TK1` (thêm tiền tố sprint, không lệch ý tiêu chí) |
| `wp-3` | `a0d08bfaf6832df27` | **Đạt** | «Mục Trọng tâm review không để trống và phần tự review không bỏ»; đúng 5 mục, mỗi mục gắn test về `TK1`/`TK2` (`test_parse_missing_column_raises`, `test_import_atomic_on_bad_row`…); tự review đủ 5 điểm; `DN1` đưa lên Cổng 1, không tự chọn |

Kết quả: 3/3 Đạt; tiêu chí hồi quy chung không bị vi phạm (không bài nào nhắc «bậc model» hay ai review PLAN). Không REFACTOR.

## Chạy lại

Như `skills/intake/tests/pressure.md` mục "Chạy lại"; GREEN đọc `<worktree>/skills/writing-plan/SKILL.md` bằng
**đường tuyệt đối**.
