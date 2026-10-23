---
name: code-review
description: Use when code must be reviewed — a diff, a branch, a PR, "check my changes", a pre-merge or pre-deploy pass, a task review inside a sprint, or a bug hunt without a diff — to decide which reviewer runs, in what order, when to stop, how to brief the reviewer, and how the author receives the findings — including when tempted to fix the clear review items first while others are still unclear, or when a repository REVIEW.md, a follow-up review round or a pre-existing finding is involved.
metadata:
  group: verification
  roles: [analyst, tech-reviewer, implementer]
source: ["obra/superpowers skills/requesting-code-review/ (SKILL.md, code-reviewer.md)", "obra/superpowers skills/receiving-code-review/SKILL.md", "private-process-skills skills/code-review-routing/SKILL.md (private copy, locally written: routing table and verify gate)", "obra/superpowers-lab skills/finding-duplicate-functions/SKILL.md", "garrytan/gstack review/SKILL.md (step on approved fixes with regression tests), review/sections/shared-code-reuse.md (caller evidence idea)"]
source_sha: [8ca22dba9a94f28898bbce59f2537ff4d87c747d, 8ca22dba9a94f28898bbce59f2537ff4d87c747d, 4c0fdc5736a49b6223a7dfc7626d5495cf55185c, 51111f74f24058117752d9aa917cb19859f8ec86, f30b7b788a210d217ea3125bf3001b29cbc2a463]
license: [MIT, MIT, none, MIT, MIT]
rewrite_before_public: false
---

# Review mã

> **Kết luận:** chạy **ít reviewer nhất đủ việc**, mỗi reviewer thêm vào chỉ khi thấy được thứ
> reviewer trước **không thể** thấy; đòn bẩy của review là **loại bỏ phát hiện giả** (cổng xác minh)
> hơn là thêm máy dò; reviewer là **agent khác** người làm, nhận ngữ cảnh soạn riêng và một gói diff
> cắt từ **mốc gốc** (không `HEAD~1`); phát hiện theo thang chung có `file:dòng`; bắt buộc có mục
> "đã xem xét và gác lại" và "không đánh giá". Người làm **kiểm chứng trước khi sửa**, cấm đồng ý cho có; mục được chọn sửa = sửa **và**
> test hồi quy, mục bỏ qua = bỏ **cả hai** và lỗi giữ trạng thái chưa giải.

## Contents

- 1. Bước 0 — phân loại yêu cầu — mọi yêu cầu review; có cả phân vai skill và lệnh review của harness
- 2. A — Review diff — có diff hay PR: phạm vi, gói diff, `REVIEW.md` của repo, chuyên gia, cổng xác minh
- 3. B — Săn lỗi (không có diff) — "tìm lỗi ở X" khi chưa có diff
- 4. C — Nâng cấp bảo mật (bắt buộc, đè right-sizing) — diff chạm vùng nhạy cảm
- 5. Yêu cầu review — brief cho reviewer — soạn brief; 5.1 vòng sau, 5.2 nhãn và kết cục
- 6. Tiếp nhận review — người làm — nhận phát hiện, sửa, phản bác
- 7. Luật dừng — trước khi thêm reviewer, hook hay vòng lặp
- 8. Cờ đỏ — khi thấy mình viện cớ bỏ bước
- Gotchas — ba chỗ hay vấp

## 1. Bước 0 — phân loại yêu cầu

| Tín hiệu | Tình huống | Đi |
|---|---|---|
| có diff / PR / "xem thay đổi của tôi" / trước commit | **A. Review diff** | mục 2 |
| không có diff — "tìm lỗi ở X", "sao hỏng" | **B. Săn lỗi** | mục 3 |
| chạm xác thực · secret · thanh toán · dữ liệu cá nhân · phân quyền · phạm vi nhiều khách · API công khai · migration · hạ tầng · file luật (`rules`) | **C. Nâng cấp bảo mật** | mục 4 — bắt buộc, **chồng lên** A hoặc B |
| "nhìn xấu", khoảng cách, bố cục | thiết kế, không phải review mã | công cụ thiết kế nếu môi trường có; không bịa reviewer |
| tài liệu, onboarding, trải nghiệm CLI | DX | tự đọc như người mới và báo; không có reviewer riêng |
| còn ở giai đoạn PLAN, chưa có code | review PLAN | skill `plan-review` |

Tình huống cộng dồn: diff migration = A **+** C. Thay đổi một dòng hay thuần thẩm mỹ: **đọc**, không
mở quy trình review đầy đủ.

**Phân vai:** skill này là quy trình — ai review, thứ tự, khi nào dừng, brief, cách tiếp nhận; lệnh review sẵn có của
harness (nếu có) là một lượt chạy ngay do người dùng gõ, kết quả của nó là một khía cạnh nữa của cổng review. Review có
hai việc: bắt lỗi trước khi gộp và giúp người duyệt hiểu thay đổi; bỏ việc sau thì Cổng 2 thành ký cho có.

## 2. A — Review diff

**Phạm vi — xác định bằng git, không bằng trí nhớ.**

```
BASE=$(git merge-base <nhánh gốc> HEAD)      # cả nhánh; review theo việc dùng BASE ghi trước khi giao
git log --oneline $BASE..HEAD
git diff --stat $BASE..HEAD
git diff --name-only $BASE..HEAD
```

`HEAD~1` bỏ sót mọi commit trừ commit cuối của việc nhiều commit — **không dùng**. Review theo
phạm vi commit (`BASE..HEAD`), không review working tree: working tree kéo file chưa track (`.env`,
dump) vào ngữ cảnh. Diff chứa secret → dừng, Chặn, điều kiện dừng (b).

**Lượt tổng quát — chia theo cỡ.**

| File trong diff | Làm |
|---|---|
| ≤10 | **một** reviewer đọc trọn gói diff theo brief ở [references/reviewer.md](references/reviewer.md); đó *là* review |
| >10 | chia gói theo **module/thư mục** (mỗi gói ≤10 file, cùng một reviewer lần lượt hoặc nhiều reviewer song song, mỗi gói một brief); một lượt cuối đọc danh sách phát hiện gộp để bắt mâu thuẫn **giữa** các gói |

Gói diff: `git log --oneline`, `git diff --stat`, `git diff -U10 $BASE..HEAD` ghi ra một file
`.tmp/review-<base7>..<head7>.diff` (hoặc theo đường dẫn module với `-- <đường>`); reviewer đọc **một**
lần, diff không đi qua ngữ cảnh điều phối. Reviewer là **agent khác** người làm (T1); với sprint, Tech
Reviewer ở Bước 4 và review theo việc ở Bước 3 (skill `running-sprint`, `references/review.md`).

**`REVIEW.md` của repo.** Có `REVIEW.md` ở `BASE` thì brief chép lệnh `git show <BASE>:REVIEW.md` và reviewer áp nó trước
khi đọc diff — từ mốc gốc, để nhánh không tự nới luật review của mình; diff sửa chính file này vẫn áp bản `BASE`, ghi
`RF` Ghi chú và xếp bậc cao; vắng file → mặc định. Khuôn: [references/review-md.md](references/review-md.md).

**Chuyên gia — thêm chỉ khi có tín hiệu**, không bao giờ mặc định; mỗi chuyên gia phải thấy được
thứ lượt tổng quát không thấy:

| Diff có | Thêm agent |
|---|---|
| Python ngoài mức tầm thường | `python-reviewer` |
| route / dependency / schema FastAPI | `fastapi-reviewer` |
| SQL, schema, migration | `database-reviewer` |
| `try/except`, fallback, đường lỗi, `.get()` mặc định | `silent-failure-hunter` |
| comment có thể đã lệch code | `comment-analyzer` |
| pipeline RAG, vector store, chunking | `rag-pipeline-reviewer` |
| TypeScript / JavaScript ngoài mức tầm thường | `typescript-reviewer` |
| `.tsx` / `.jsx`, hook, ranh giới server/client của React hay Next.js | `react-reviewer` (chạy cạnh `typescript-reviewer`) |
| thêm hay sửa hành vi có test đi kèm; nghi test rỗng, nhánh lỗi chưa phủ, test chập chờn | `test-analyzer` |
| cần một lượt tổng quát mà không có chuyên gia hợp, hoặc làm lượt đầu trước khi kéo chuyên gia | `code-reviewer` |

`code-reviewer` và brief `references/reviewer.md` (mục 5) là **hai cách giao cùng một lượt tổng quát**, chọn một cho mỗi
diff: brief `reviewer.md` khi review toàn nhánh đối chiếu PLAN/SPEC và Trọng tâm review; agent `code-reviewer` khi cần lượt
tổng quát nhanh trên một diff mà không soạn brief riêng. Chuyên gia khi diff nằm trọn trong một vùng chúng phủ.

Diff **thêm hàm mới** ở vùng hay mọc bản sao (tiện ích, định dạng, kiểm hợp lệ, đường dẫn, đổi lỗi thành chuỗi):
thêm bước tìm hàm trùng ý theo [references/duplicates.md](references/duplicates.md) — grep và đọc thân, không giao
agent; trùng là Nên sửa hoặc Ghi chú, không bao giờ Chặn.

Chuyên gia độc lập chạy **song song** (một lượt, nhiều lệnh giao agent), mỗi agent một brief, cùng
gói diff. Ghi vai · tier · model từng agent vào PROGRESS.

**Cổng xác minh — không bỏ.** Trước khi báo bất kỳ phát hiện nào: đối chiếu từng ứng viên với mã
nguồn thật (schema gốc, nơi gọi, kiểu cột) — phần lớn phát hiện "có vẻ đúng" chết ở đây (đo một lần:
cổng này loại 4/6 ứng viên, cả 4 đều giả). Ứng viên không có `file:dòng` hay lệnh + kết quả → tối đa
Ghi chú, hoặc bỏ. Một báo động giả tốn lòng tin hơn một nit bỏ sót. Phát hiện sống sót mang **đúng
một mức**: Chặn / Phải sửa / Nên sửa / Ghi chú.

**Ý kiến đối kháng thứ hai — có điều kiện.** Chỉ khi thay đổi rủi ro cao (mục 4) hoặc một phát
hiện bị tranh cãi: reviewer thứ hai **khác agent** (và tốt nhất khác hãng) đọc cùng gói với brief
"phản biện phát hiện X". Khác hãng = **tư vấn gọi chéo**, người dùng quyết (`tiers/README.md` mục 6).

## 3. B — Săn lỗi (không có diff)

1. Lỗi đang sống / tái hiện được → skill `debugging` **trước**; reviewer dưới chỉ hỗ trợ nó.
2. `silent-failure-hunter` đi đầu — lỗi im lặng (500 thay vì 422, giá ×10, file test bị bỏ mà vẫn
   xanh) là dạng hay gặp nhất và tổng quát không thấy.
3. Rồi chuyên gia theo hệ con (bảng chuyên gia ở mục 2).
4. Cổng xác minh như thường.

## 4. C — Nâng cấp bảo mật (bắt buộc, đè right-sizing)

Chạm vùng ở Bước 0 → `risk: high`, cỡ **lớn** (`method/sizing.md` mục 2):

1. Chạy A bình thường.
2. **Rồi** lượt bảo mật — không tuỳ chọn, không thay bằng tổng quát: skill `security-review` +
   agent `security-reviewer`; cần soát cả repo (OWASP, STRIDE, khảo cổ secret) thêm `security-audit`.
   `risk_tags` có `rules`, `secret` hoặc `auth` → lượt kiểm kỹ thuật chạy theo `roles/verifier/dual-review.md`:
   hai reviewer độc lập cùng rubric, cả hai Đạt mới Đạt (cộng thêm, không thay lượt bảo mật).
3. Báo đã nâng cấp gì và vì sao, để người dùng gác ở **Cổng 2** trước khi phát hành.

## 5. Yêu cầu review — brief cho reviewer

Khi nào **bắt buộc**: sau mỗi `TK` từ cỡ vừa (review theo việc), sau tính năng lớn, trước gộp nhánh
chính (review toàn nhánh — luôn, kể cả chế độ một agent). **Nên**: khi kẹt (mắt mới), trước refactor
(mốc), sau lỗi phức tạp.

Brief theo [references/reviewer.md](references/reviewer.md): mô tả ngắn đã làm gì · yêu cầu
(đường dẫn PLAN/SPEC + mục, hoặc brief `TK`) · `BASE`/`HEAD` + đường gói diff · mục **Trọng tâm
review** của PLAN nguyên văn · con trỏ tới các dòng `Phán quyết:` và `Nên sửa hoãn` · khối văn phong
rút gọn. **Không** dán lịch sử phiên; **không mớm** ("đừng bắt X", "tối đa Ghi chú"). Reviewer trả:
*Đã xem xét và gác lại* (bắt buộc, có thể rỗng) · Điểm tốt · `RF` theo mức có `file:dòng` · Không đánh
giá (bắt buộc) · kết luận **Đạt / Đạt có điều kiện / Không đạt**.

Điều phối xử lý: mỗi dòng "gác lại" là một **phán quyết** của Analyst (giữ hay thành `RF`), chấm theo
**tác động lên người dùng** chứ không theo việc SPEC có nhắc đầu vào đó không; Chặn/Phải sửa → vòng
sửa; Nên sửa → `CO`; reviewer sai → phản bác có bằng chứng (mục 6), không bỏ im lặng. Không tự review
diff trong phiên điều phối thay cho reviewer — đốt ngữ cảnh điều phối và không độc lập.

### 5.1 Vòng sau — hội tụ

- **Vòng ≥2 đọc hẹp:** reviewer nhận diff từ mốc vòng trước tới `HEAD` cùng bảng `RF` cũ, phán từng `RF` *đã xử lý / chưa*,
  chỉ bắt lỗi mới trong diff sửa. Review theo việc giữ nguyên `running-sprint` mục 4.4.
- **Lớp lỗi:** `RF` thuộc lớp có thể lặp ghi `lớp: <tên>`; người làm sửa mọi chỗ cùng lớp trong diff và nêu số chỗ;
  vòng sau reviewer kiểm cả lớp, không chỉ dòng đã báo.
- **Không đăng lại** `RF` đã có kết cục (5.2) cùng khoá gộp (đoạn mã + file), trừ khi diff sửa đem bằng chứng mới — nêu bằng chứng đó.
- Khuyến nghị 3 vòng, không trần cứng (`AGENTS.md`). Hết vòng 3 còn Chặn hay Phải sửa: không tự mở vòng 4 — dừng vòng
  tự động, ghi một câu xem lại cách làm kèm lớp lỗi lặp, báo người dùng chọn làm tiếp hay dừng và bàn giao.

### 5.2 Nhãn và kết cục

- **`có từ trước`** (nhãn ở cột `Nhãn`, không phải mức; `RF` vẫn đúng một mức): lỗi đã có ở `BASE` (`git show <BASE>:<file>`
  hay `git blame`) và diff không làm nặng thêm → không chặn sprint, kết cục `có từ trước → CO` kèm dòng `RQ-`. Là Chặn về
  bảo mật hay mất dữ liệu thì báo ngay mức Chặn, điều phối mở `BR` theo điều kiện dừng (b); không hoãn thành `CO` im lặng.
- **Năm kết cục**, mỗi `RF` đúng một khi trình Cổng 2: *đã sửa* (sha + test hồi quy đỏ rồi xanh) · *bác kèm lý do*
  (bằng chứng `file:dòng`) · *để lại → `CO`* · *có từ trước → `CO`* · *mở*. Còn *mở* ở Chặn hay Phải sửa → tiền kiểm Không đạt.
- **Đo nhiễu:** Retro đếm theo từng reviewer số `RF` bị *bác* trên tổng `RF` của reviewer đó, từ cột "Xử lý" của REPORT.
- Bậc duyệt, path luôn-cần-người và dòng `Bậc duyệt:` của lời trình: [references/risk-tiers.md](references/risk-tiers.md).

## 6. Tiếp nhận review — người làm

```
1. ĐỌC hết, chưa phản ứng.
2. HIỂU: nói lại yêu cầu bằng lời mình (hoặc hỏi).
3. KIỂM CHỨNG: đối chiếu codebase thật — đúng với stack này? vỡ gì đang chạy? vì sao code hiện tại
   như vậy? mọi nền tảng/phiên bản? reviewer có đủ ngữ cảnh?
4. ĐÁNH GIÁ: đúng về kỹ thuật cho repo này?
5. TRẢ LỜI: xác nhận kỹ thuật hoặc phản bác có lý do.
6. SỬA: từng mục một, test từng mục, chạy lại cả bộ.
```

- **Cấm:** "Anh nói đúng quá!", "Góp ý tuyệt vời!", "Để em làm ngay" (trước khi kiểm), mọi lời cảm ơn.
  Thay bằng: nói lại yêu cầu kỹ thuật, hỏi làm rõ, phản bác có lý do, hoặc **làm luôn** — code cho thấy
  đã nghe.
- **Còn mục nào chưa rõ → không sửa mục nào, kể cả mục đã rõ:** hỏi tất cả mục chưa rõ trong một lượt,
  chờ trả lời rồi mới bắt đầu sửa; các mục có thể liên quan nhau, hiểu một nửa = sửa sai. Trong lúc chờ
  chỉ được kiểm chứng (đọc code, chạy test hiện có), không đổi code. "Hiểu 1, 2, 3, 6; cần làm rõ 4, 5
  trước khi làm bất kỳ mục nào." Hạn gộp gần không phải lý do sửa trước phần đã rõ.
- **Phản bác khi:** sửa theo sẽ vỡ chức năng; reviewer thiếu ngữ cảnh; vi phạm YAGNI (reviewer bảo
  "làm cho tử tế" → `grep` xem có ai gọi; không ai gọi → đề xuất bỏ); sai với stack này; có lý do tương
  thích; trái quyết định kiến trúc đã duyệt (→ Analyst, không tự quyết). Phản bác bằng lý do kỹ thuật,
  câu hỏi cụ thể, test/code đang chạy; không phòng thủ. Không kiểm chứng được → nói rõ "không kiểm được
  nếu thiếu X; điều tra / hỏi / đi tiếp?".
- **Thứ tự sửa:** Chặn (vỡ, bảo mật) → sửa đơn giản (typo, import) → sửa phức tạp (refactor, logic);
  test từng mục; cuối cùng cả bộ. Phát hiện Chặn/Phải sửa từ reviewer = **vòng mới** trong PROGRESS.
- **Sửa và test hồi quy là MỘT lựa chọn.** Mục được chọn sửa = viết test hồi quy cho đúng lỗi, thấy nó **đỏ** với
  mã gốc, rồi sửa, rồi chạy test đó cùng phép thăm dò ban đầu và cả bộ; chưa có test thì chưa gọi là đã sửa, `RF`
  chưa đóng. Mục bị bỏ qua = bỏ **cả hai**: không sửa, và không thêm test `xfail`/`skip` làm vật thay thế cho
  việc sửa. Lỗi giữ trạng thái **chưa giải** (Phải sửa mở, hoặc `CO` có chủ và hạn), không ghi "đã xử lý", và
  hiện ở Cổng 2. Không đủ giờ cho cả hai → không sửa và báo Analyst; không sửa-không-test để kịp.
- Đã phản bác mà sai → "Đã kiểm X, nó làm Y — anh đúng. Sửa." Không xin lỗi dài, không bào chữa.
- Phản hồi từ người dùng: tin, nhưng vẫn hỏi khi phạm vi chưa rõ; vẫn không nói "anh nói đúng".
- Trả lời thread PR trên GitHub: trả lời **trong thread** (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), không comment cấp PR.

## 7. Luật dừng

- Không xếp chồng reviewer đọc cùng một thứ theo cùng một cách — tranh luận trên cùng văn bản không
  thêm thông tin, chỉ nhân chi phí ("sân khấu nhiều agent").
- Không chạy review đầy đủ cho sửa một dòng hay thẩm mỹ: đọc.
- Không bật hook review tự động khi người dùng không yêu cầu — vòng lặp đốt hạn mức; hook xác định (format, chặn path, quét khoá) thì được — skill `hooks-guardrails`.
- Lệnh review có tính phí của harness (nếu có) do **người dùng** kích; chỉ nhắc nó tồn tại.
- Báo trung thực: reviewer nào đã chạy, bỏ reviewer nào vì sao, đã xác minh gì ↔ còn là giả thuyết.

## 8. Cờ đỏ

| Ý nghĩ | Thực tế |
|---|---|
| "Tự đọc diff cho nhanh thay vì giao reviewer" | điều phối đốt ngữ cảnh và không độc lập; diff và đánh giá sống trong ngữ cảnh reviewer, chỉ phát hiện quay về |
| "Reviewer cần cả lịch sử phiên mới hiểu" | ngữ cảnh soạn riêng giữ reviewer trên sản phẩm, không trên dòng suy nghĩ của bạn |
| "Đơn giản, khỏi review" | trước gộp luôn review; "đơn giản" là cờ đỏ |
| "Chạy hết 6 reviewer cho chắc" | mỗi reviewer thêm phải thấy được thứ reviewer trước không thấy |
| "Phát hiện này nghe hợp lý, báo luôn" | qua cổng xác minh; không `file:dòng` thì tối đa Ghi chú |
| "Reviewer nói vậy thì làm vậy" | kiểm chứng trước; sai thì phản bác có bằng chứng |
| "Anh nói đúng quá, em sửa ngay" | nói lại yêu cầu rồi kiểm; hoặc sửa và để code trả lời |
| "Sửa trước, test sau cho kịp giờ" | sửa và test hồi quy là một lựa chọn; chưa có test thì chưa sửa xong, `RF` chưa đóng |
| "Không kịp thì thêm test `xfail` rồi đóng `RF` cho REPORT sạch" | bỏ qua = bỏ cả sửa lẫn test; lỗi giữ chưa giải, nói thẳng ở Cổng 2 |
| "Mục rõ thì làm ngay cho kịp giờ, mục mơ hồ hỏi sau" | còn mục chưa rõ thì chưa sửa mục nào; mục mơ hồ có thể đổi cách làm mục rõ |

## Gotchas

- `REVIEW.md` đọc từ `BASE` bằng `git show`, không từ cây làm việc: nhánh sửa file này không tự nới luật review của mình.
- Khuyến nghị 3 vòng, không trần cứng: hết vòng 3 còn Chặn hay Phải sửa thì báo người, không mở vòng 4, không đóng im lặng.
- `có từ trước` và `lớp:` là nhãn, không phải mức; lỗi có từ trước mà là bảo mật hay mất dữ liệu vẫn là Chặn.
