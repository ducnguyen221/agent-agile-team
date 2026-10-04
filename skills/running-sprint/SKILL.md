---
name: running-sprint
description: Use when a PLAN has passed gate 1 and tasks must now be executed — by dispatching a fresh subagent per task with a task review after each, or by one agent working inline — keeping PROGRESS as the ledger, ruling on ambiguities without stalling, and stopping only for the four stop conditions.
metadata:
  group: process
  roles: [analyst, implementer]
source: ["obra/superpowers skills/subagent-driven-development/ (SKILL.md, implementer-prompt.md, task-reviewer-prompt.md, re-review-prompt.md)", "obra/superpowers skills/executing-plans/SKILL.md", "obra/superpowers skills/dispatching-parallel-agents/SKILL.md"]
source_sha: [8ca22dba9a94f28898bbce59f2537ff4d87c747d, 8ca22dba9a94f28898bbce59f2537ff4d87c747d, 8ca22dba9a94f28898bbce59f2537ff4d87c747d]
license: [MIT, MIT, MIT]
rewrite_before_public: false
---

# Chạy sprint (Bước 3)

> **Kết luận:** sau Cổng 1, sprint chạy **liên tục** tới việc cuối: mỗi `TK` được giao bằng brief soạn
> riêng (không dán lịch sử phiên), ghi **vai · tier · model** vào PROGRESS, được agent khác kiểm (`VR`)
> và — từ cỡ vừa — review theo việc; mâu thuẫn và chỗ PLAN mơ hồ thì Analyst **phán quyết rồi đi
> tiếp**, chỉ dừng ở bốn điều kiện. PROGRESS là sổ sống: ngữ cảnh phiên mất sau nén, sổ thì không.

## 1. Hai chế độ — chọn ở Cổng 1

| Chế độ | Cách chạy | Được gì | Tốn gì | Chọn khi |
|---|---|---|---|---|
| **Giao subagent từng việc** (mặc định khi harness có subagent) | mỗi `TK` một Implementer mới + review theo việc; review toàn nhánh cuối | ngữ cảnh sạch mỗi việc; lỗi bị bắt ngay sau `TK` gây ra | một ngữ cảnh mỗi việc và mỗi review | nhiều `TK` phụ thuộc giao diện nhau; lỗi lọt ra tốn kém; PLAN dài tới mức việc cuối sẽ chạy trên ngữ cảnh đã nén |
| **Một agent làm liên tục** (mục 6) | agent điều phối tự làm từng `TK`; chỉ review toàn nhánh cuối | rẻ, nhanh; PLAN đủ rõ thì chạy tốt ở T2 | không có mắt thứ hai cho tới cuối; việc cuối nhận ngữ cảnh mỏi nhất | ít `TK`, PLAN đầy đủ, harness không có subagent, hoặc người dùng chọn |

Người dùng đã chọn thì không hỏi lại. Harness không có công cụ subagent → không "giả vờ" giao việc;
chạy chế độ một agent và nói rõ.

## 2. Thiết lập — trước `TK` đầu tiên

1. **Worktree riêng** (skill `worktrees`). Không bắt đầu trên nhánh chính khi chưa được giao đích danh.
2. **PROGRESS là sổ:** `status: in_progress`, `roles` ghi nhãn agent từng vai. Sổ đã có dòng `TKn Đạt`
   thì `TK` đó **xong** — không làm lại; nối ở `TK` đầu tiên chưa có dòng xong. Sau nén ngữ cảnh,
   tin PROGRESS và `git log`, không tin trí nhớ.
   **Cỡ rất nhỏ / nhỏ** (một `SPRINT.md`): sổ là phần **PROGRESS** (nhỏ) hoặc **Kết quả** (rất nhỏ) của chính file đó,
   không dựng `PROGRESS.md` riêng; chế độ một agent (mục 6) là mặc định. Kiểm: nhỏ → **một** reviewer khác người
   làm giữ cả hai lăng kính (khớp SPEC + kỹ thuật) ở cuối nhánh, không review theo việc, Cổng 2 là lượt duyệt thật;
   rất nhỏ → agent khác chạy nhanh, hoặc ghi "tự kiểm, chưa độc lập" (tối đa Đạt có điều kiện) và Cổng 2 gộp lời
   báo cuối (`method/process.md` mục 9).
3. **Đọc PLAN một lần** (Ràng buộc chung, Trọng tâm review, bảng Giao diện) và SPEC (thẩm quyền khi
   PLAN mâu thuẫn). Tạo todo mỗi `TK` — todo là màn hình, PROGRESS là hồ sơ.
4. **Tiền kiểm giao diện:** với mỗi cặp `TK` chung file hay giao diện, một dòng: hai `TK`, cái này
   *sinh* gì ↔ cái kia *dùng* gì, có khớp không; với mỗi `TK`, chính nó có tự nhất quán không (test
   nó ghi ↔ code nó ghi; file nó tạo ↔ file nó sửa). Bảng ghi vào nhật ký PROGRESS; "tiền kiểm sạch"
   mà không có dòng nào là chưa kiểm. Mâu thuẫn → **phán quyết** theo SPEC trước khi giao `TK1`.
5. **Bảng tier → model** đọc từ nơi `AGENT_AGILE_TIERS` trỏ; thiếu thì hỏi người dùng (`tiers/README.md`).

## 3. Chạy liên tục, phán quyết không dừng

- Không hỏi "làm tiếp không?" giữa các `TK`; không tóm tắt tiến độ cho người dùng giữa chừng — PROGRESS
  là nơi họ xem.
- Mâu thuẫn SPEC ↔ PLAN, chỗ PLAN mơ hồ, chi tiết chưa lường, giới hạn nhỏ cần vượt: **Analyst quyết**
  và ghi `Phán quyết: <quyết gì> — <vì sao> — <sai thì tốn gì>` vào nhật ký. Sai thì tốn công làm lại
  mà người dùng thấy và hoàn tác được; phiên đứng chờ tốn cả buổi của họ.
- **Dừng và mở `BR` chỉ khi** (`method/process.md` mục 5): (a) hành động không đảo ngược, (b) chạm bảo
  mật/secret, (c) tác động ra ngoài worktree/phạm vi (push, gộp nhánh chung, deploy, gửi tin), (d) PLAN
  hỏng — mọi đường đi tiếp đều là đoán hoặc tiêu chí thành công đổi. Cạn hạn mức tier cũng mở `BR`,
  không tự hạ tier.
- Mỗi lần giao việc và mỗi kết quả là **một dòng PROGRESS**; ghi trong cùng lượt với commit, không
  để dồn.
- **Sổ tập trung** (chỉ khi `.agile.json` có `ledger.project`; không khai thì bỏ qua): cùng lượt với PROGRESS,
  **hồ sơ trước, sổ sau**, ở năm thời điểm — mở sprint · qua Cổng 1 · quay lại bước 3 mà trạng thái đổi · Cổng 2 ·
  đóng sprint; không để dồn tới lúc đóng. Cập nhật dòng của sprint (không thêm dòng):
  `| SPR-xx | <status của PROGRESS> | <ngày hôm nay> | <repo>:docs/plans/<slug>/PROGRESS.md | [PROGRESS](<link>) |`.
  Link: hồ sơ trong repo → URL GitHub blob `https://github.com/<owner>/<repo>/blob/<ref>/docs/plans/<slug>/PROGRESS.md`
  (`<ref>` = nhánh sprint khi đang mở, `main` hoặc SHA khi đã đóng); hồ sơ ngoài repo → đường tương đối trong kho sổ.
  Không ghi đường dẫn của máy vào file của repo. Qua Cổng 1: `gate_1_quote` là câu duyệt nguyên văn. Ghi xong chạy
  `check` của repo (máy đã đặt biến `AGENT_AGILE_LEDGER`) và đọc: không còn `ledger-stale`, `ledger-missing-row`.
  Chi tiết: `method/process.md` mục 11.

## 4. Vòng lặp theo việc (chế độ giao subagent)

### 4.1 Giao việc

- Ghi **BASE** = `git rev-parse HEAD` trước khi giao — gói review và vòng sửa cắt từ đây, **không bao
  giờ** `HEAD~1` (bỏ sót mọi commit trừ commit cuối của việc nhiều commit).
- Soạn brief theo [references/brief.md](references/brief.md): mục tiêu một câu · đường dẫn PLAN + mục
  `TKn` (brief là nguồn yêu cầu duy nhất; giá trị chính xác chỉ ở đó) · giao diện và phán quyết từ `TK`
  trước mà brief không biết · điều cấm · hợp đồng báo cáo. **Không dán lịch sử phiên, không dán cả
  PLAN.** Có phát hiện gác lại ở vùng `TK` này chạm → trỏ dòng PROGRESS đó.
- Ghi dòng bắt đầu: `**<giờ>** — giao TKn (<tên>) cho Implementer · T2 · <model>; brief <đường dẫn>;
  BASE <sha7>`; nhãn agent vào `roles`. Thiếu model là Phải sửa khi kiểm PROGRESS.
- **Không giao hai Implementer song song** lên cùng file; việc độc lập chạy song song theo
  [references/parallel.md](references/parallel.md). Việc nhỏ cùng hình (một sửa lặp ở nhiều file) gộp
  thành **một** brief có danh sách file, review như một diff.
- Ghi nhớ nhãn agent của Implementer: vòng sửa 1–3 nối lại chính agent đó.

### 4.2 Nhận báo cáo

Implementer trả **≤15 dòng** (chi tiết nằm trong file báo cáo): trạng thái · commit · một dòng test ·
lo ngại · đường dẫn báo cáo. Trạng thái quy về `method/severity.md`:

| Báo | Nghĩa | Làm gì |
|---|---|---|
| xong (`DONE`) | làm xong, có bằng chứng | sang 4.3 |
| xong có lo ngại | đúng/sai còn ngờ, hoặc quan sát ("file đang phình") | đọc lo ngại; về đúng/sai hay phạm vi → xử lý trước review; quan sát → ghi nhật ký, review tiếp |
| thiếu ngữ cảnh | cần thông tin brief không có | bổ sung, giao lại cùng agent |
| bị chặn | không làm được | thiếu ngữ cảnh → bổ sung; việc quá to → tách `TK` con; PLAN sai → phán quyết rồi giao lại kèm phán quyết; cần năng lực cao hơn → **tư vấn tier**, người dùng quyết (được đổi sang agent khác **cùng tier** để có mắt mới) |

Không bao giờ bỏ qua một lần báo chặn hay ép cùng agent thử lại **y nguyên**. Implementer hỏi trước khi
bắt đầu → trả lời đủ, không giục.

### 4.3 Kiểm theo việc

- **`VR` do agent khác chạy** (QA, nhãn khác Implementer): chạy lệnh kiểm của `TK`, ghi dòng
  PROGRESS xong: `TKn Đạt — <lệnh> → <kết quả thật>; commit <base7>..<head7>`. Implementer tự chạy chưa
  phải `VR`.
- **Review theo việc** — bắt buộc từ cỡ **vừa**, và với mọi `TK` chạm Trọng tâm review hay `risk_tags`;
  cỡ nhỏ được bỏ (review toàn nhánh ở Bước 4 lo). Reviewer là agent khác, nhận ba thứ: brief, báo cáo
  của Implementer, **gói diff** — `git log --oneline BASE..HEAD`, `git diff --stat BASE..HEAD`,
  `git diff -U10 BASE..HEAD` ghi ra một file trong `.tmp/` (`review-<base7>..<head7>.diff`), reviewer
  đọc một lần, diff không đi qua ngữ cảnh điều phối. Brief reviewer ở
  [references/review.md](references/review.md): hai phán quyết — **khớp SPEC** và **chất lượng** theo
  thang chung — mỗi phát hiện có `file:dòng`.
- Khối Ràng buộc chung trao cho reviewer chép **nguyên văn** từ PLAN/SPEC; **không mớm** ("đừng bắt
  X", "tối đa Ghi chú", "PLAN đã chọn thế") — thấy mình viết câu đó là đang tự tránh một vòng sửa.
  Không bắt reviewer chạy lại bộ test Implementer đã chạy trên cùng code.
- Mục "không kiểm được từ diff" của reviewer là của Analyst: kiểm bằng ngữ cảnh liên-`TK`; là lỗ hổng
  thật → vào vòng sửa như phát hiện khớp SPEC.

### 4.4 Vòng sửa theo việc

Mở khi review trả **không khớp SPEC**, hoặc phát hiện **Chặn / Phải sửa**. Nên sửa → ghi nhật ký
`TKn: Nên sửa hoãn — <một dòng>` (thành `CO` ở REPORT, review toàn nhánh soát lại); Ghi chú không vào
vòng. Phát hiện **xung đột với chữ của PLAN** → Analyst phán quyết theo SPEC trước khi sửa, không bác vì
"PLAN bảo thế", không sửa trái PLAN mà chưa ghi phán quyết.

- **Một vòng** = một lượt sửa + một lượt re-review **phạm vi hẹp** (diff từ mốc review trước tới HEAD;
  re-reviewer phán từng phát hiện *đã xử lý / chưa*, chỉ bắt lỗi mới trong diff sửa, quan sát ngoài
  phạm vi ghi nhật ký, không kéo dài vòng).
- Vòng 1–3: nối lại **chính Implementer** (ngữ cảnh còn nguyên) với phát hiện chép nguyên văn; harness
  không nối lại được thì agent mới cùng tier mang brief + file báo cáo + phát hiện. Implementer sửa,
  chạy lại test **phủ chỗ sửa** (nêu tên file test; sửa một dòng không cần cả bộ), nối báo cáo sửa vào
  cùng file báo cáo (lệnh + output); đủ ba thứ đó mới giao re-review.
- Sau mỗi vòng, nhật ký: `TKn: vòng sửa <r> (<x> đã xử lý, <y> còn mở — <tóm tắt>; commit <a7>..<b7>)`.
  Vòng sửa theo việc **không** đếm vào `review_round` (đó là vòng kiểm định toàn sprint, Bước 4).
- **Khuyến nghị 3 vòng, không trần cứng.** Quá vòng 3 còn mở → Analyst **phân xử từng phát hiện** và
  ghi `Phán quyết:`: reviewer sai hoặc tranh cãi được → gác lại có lý do; thật nhưng không gì phía sau
  dựa vào → gác lại, ghi "thật, hoãn"; thật và **chịu tải** (`TK` sau dựa vào, hay lộ PLAN hỏng) → quyết
  thay đổi nhỏ nhất gỡ tắc, mang vào brief `TK` sau. Vòng sửa kéo dài thường vì Implementer không thấy
  lỗi của mình: đổi agent cùng tier (Analyst tự quyết) hoặc tư vấn nâng tier (người dùng quyết). Mọi
  đường đi tiếp đều là đoán → điều kiện dừng (d), mở `BR`.
- Phân xử chỉ sau vòng 3; phân xử sớm để kết thúc vòng là mớm reviewer dưới tên khác. **Không tự sửa
  trong phiên điều phối** — vừa làm bẩn ngữ cảnh vừa bỏ qua review.

### 4.5 Xong việc

Review sạch (hoặc mọi phát hiện còn mở đã gác lại có phán quyết) → bảng trạng thái PROGRESS: `TKn`
Đạt, bằng chứng (lệnh + kết quả, commit range); đánh dấu todo; sang `TK` kế. Không sang `TK` kế khi còn
Chặn/Phải sửa chưa sửa hay chưa gác lại có phán quyết.

## 5. Sau việc cuối — kiểm định toàn sprint (Bước 4)

1. Gói diff **cả nhánh**: `MERGE_BASE=$(git merge-base <nhánh chính> HEAD)` → gói như 4.3. Giao
   Tech Reviewer (agent khác, T1) theo skill `code-review` phần yêu cầu review, kèm đường dẫn PLAN +
   SPEC, mục **Trọng tâm review** nguyên văn, và con trỏ tới các dòng `Phán quyết:` và `Nên sửa hoãn`
   để reviewer cân lại. Business Reviewer kiểm `US`/`FR`/`SC` song song.
2. Phát hiện → **một** lượt sửa với danh sách đầy đủ (không một agent mỗi phát hiện — mỗi agent dựng
   lại ngữ cảnh và chạy lại bộ test; một phiên thật tốn hơn toàn bộ các `TK` cộng lại), rồi **một**
   re-review phạm vi hẹp. Đây là một vòng, tăng `review_round`. Khuyến nghị 3 vòng; hết vòng 3 còn
   Chặn/Phải sửa → lời báo chuẩn `method/process.md` mục 6, người dùng chọn.
3. Gom **mọi** dòng `Phán quyết:` (tiền kiểm, gác lại, phân xử) vào REPORT mục Review & Retro, theo thứ
   tự, mỗi dòng kèm "sai thì tốn gì". Phán quyết không tới tay người dùng là quyết định trong bóng tối.
4. → REPORT → Cổng 2 → skill `closing-sprint`. Xoá `.tmp/` của sprint sau khi đóng.

## 6. Chế độ một agent

Giữ nguyên sổ, tiền kiểm, bốn điều kiện dừng, phán quyết. Khác ở:

- Agent **tự làm** từng `TK` theo khối **Bước** của PLAN dưới skill `tdd` (nạp trước `TK1`): viết test
  → chạy **thấy hỏng** (test đạt khi chưa có code là phát hiện về test) → code tối thiểu → chạy đạt →
  cả bộ xanh → commit. Mỗi `Kỳ vọng` trong Bước so với output **thật**: khớp → bước kế; code sai →
  skill `debugging` (không vá triệu chứng cho output khớp); PLAN sai → phán quyết, ghi nhật ký, đi
  tiếp — `TK` sau đọc phán quyết từ sổ, không từ trí nhớ.
- **Hợp đồng xong việc** (skill `verify-before-done`): mọi test brief nêu đã tồn tại, đã chạy trong
  việc này và đã đọc output; lần chạy cuối đạt; mọi `Kỳ vọng` đã so; mọi lệch so với brief có
  `Phán quyết:`. Thiếu một điều → chưa xong.
- Hai dòng PROGRESS tối thiểu mỗi `TK`: bắt đầu (`TKn`, BASE) và xong (lệnh test + kết quả thật, commit
  range). Ghi cùng lượt với commit.
- Output test dài ghi ra `.tmp/` và đọc đuôi; đọc mục `TK` trong PLAN, không đọc lại cả PLAN.
- **Review toàn nhánh vẫn bắt buộc** bởi agent khác (mục 5): đó là ngữ cảnh mới duy nhất chế độ này
  mua. Có subagent → giao T1. Không có → tự review theo brief ở `code-review`, ghi "tự review, chưa độc
  lập" vào PROGRESS và REPORT; kết luận sprint tối đa **Đạt có điều kiện** cho tới khi agent khác chạy
  lại. Chặn/Phải sửa từ review cuối: agent tự sửa **một lượt**, mỗi sửa đi RED → GREEN + cả bộ xanh, ghi
  `Final: sửa <phát hiện> — <test> RED→GREEN, bộ <n>/<n>`; không re-review (test phủ đã trả lời "đã
  xử lý", bộ xanh đã trả lời "không vỡ gì"). Nên sửa → `CO`, không sửa thêm.
- Mục "Đã xem xét và gác lại" của reviewer: mỗi dòng là một phán quyết của Analyst (giữ nguyên hay
  thành phát hiện), chấm theo **tác động lên người dùng**, không theo việc SPEC có nhắc đầu vào đó không.

## 7. Giữ ngữ cảnh điều phối sạch

- Mọi thứ dán vào brief và mọi thứ subagent in ra **ở lại** ngữ cảnh tới hết phiên. Đưa artifact qua
  **file** (brief, báo cáo, gói diff), truyền đường dẫn.
- Chờ subagent: không poll với timeout ngắn, không chờ mở vô hạn. Còn việc tại chỗ (ghi sổ, gói review
  kế) thì làm; rảnh thật thì chờ theo đợt có giới hạn, giữa đợt một dòng trạng thái và rà agent con
  nào xong mà chưa báo.
- Kể giữa các tool call tối đa một dòng; sổ và kết quả tool mang hồ sơ (skill `token-economy`).

## 8. Cờ đỏ

| Ý nghĩ | Thực tế |
|---|---|
| "Gần khớp SPEC rồi" | reviewer thấy lỗ hổng SPEC = chưa xong; sửa, hoặc quá vòng 3 thì phân xử có phán quyết |
| "Tự sửa cho nhanh, giao việc tốn công" | sửa trong phiên điều phối làm bẩn ngữ cảnh và không qua review |
| "Thêm một vòng nữa chắc hội tụ" | quá vòng 3 lỗi thường là cấu trúc: phân xử, đổi agent, hoặc `BR` |
| "Phát hiện này rõ ràng sai, bỏ" | phân xử chỉ sau vòng 3, và mọi phân xử là một dòng sổ; bỏ im lặng bị cấm |
| "Sửa nhỏ, khỏi re-review" | sửa không review là cách hồi quy lọt vào |
| "Ghi sổ sau vài việc" | nén ngữ cảnh không chờ lúc tiện; một dòng mỗi việc, cùng lượt với commit |
| "Implementer tự gọi reviewer — thêm bảo đảm miễn phí" | ghế review trùng, toàn chi phí; đó là lỗi cần ghi, không phải sự kỹ |
| "Hỏi anh ấy một câu cho chắc" | ngoài bốn điều kiện, hỏi là lỗi; phán quyết và ghi sổ |
| "Nhớ `TK4` nói gì rồi" | nhớ là bản tóm tắt; brief có giá trị chính xác — đọc lại |
