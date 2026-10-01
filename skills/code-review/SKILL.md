---
name: code-review
description: Use when code must be reviewed — a diff, a branch, a PR, "check my changes", a pre-merge or pre-deploy pass, a task review inside a sprint, or a bug hunt without a diff — to decide which reviewer runs, in what order, when to stop, how to brief the reviewer, and how the author receives the findings.
metadata:
  group: verification
  roles: [analyst, tech-reviewer, implementer]
source: ["obra/superpowers skills/requesting-code-review/ (SKILL.md, code-reviewer.md)", "obra/superpowers skills/receiving-code-review/SKILL.md", "dev-process skills/code-review-routing/SKILL.md (locally written, routing table and verify gate)"]
source_sha: [8ca22dba9a94f28898bbce59f2537ff4d87c747d, 4c0fdc5736a49b6223a7dfc7626d5495cf55185c]
license: MIT
rewrite_before_public: false
---

# Review mã

> **Kết luận:** chạy **ít reviewer nhất đủ việc**, mỗi reviewer thêm vào chỉ khi thấy được thứ
> reviewer trước **không thể** thấy; đòn bẩy của review là **loại bỏ phát hiện giả** (cổng xác minh)
> hơn là thêm máy dò; reviewer là **agent khác** người làm, nhận ngữ cảnh soạn riêng và một gói diff
> cắt từ **mốc gốc** (không `HEAD~1`); phát hiện theo thang chung có `file:dòng`; bắt buộc có mục
> "đã xem xét và gác lại" và "không đánh giá". Người làm **kiểm chứng trước khi sửa**, cấm đồng ý cho có.

## 1. Bước 0 — phân loại yêu cầu

| Tín hiệu | Tình huống | Đi |
|---|---|---|
| có diff / PR / "xem thay đổi của tôi" / trước commit | **A. Review diff** | mục 2 |
| không có diff — "tìm lỗi ở X", "sao hỏng" | **B. Săn lỗi** | mục 3 |
| chạm xác thực · secret · thanh toán · dữ liệu cá nhân · phân quyền · phạm vi nhiều khách · API công khai · migration · hạ tầng | **C. Nâng cấp bảo mật** | mục 4 — bắt buộc, **chồng lên** A hoặc B |
| "nhìn xấu", khoảng cách, bố cục | thiết kế, không phải review mã | công cụ thiết kế nếu môi trường có; không bịa reviewer |
| tài liệu, onboarding, trải nghiệm CLI | DX | tự đọc như người mới và báo; không có reviewer riêng |
| còn ở giai đoạn PLAN, chưa có code | review PLAN | skill `plan-review` |

Tình huống cộng dồn: diff migration = A **+** C. Thay đổi một dòng hay thuần thẩm mỹ: **đọc**, không
mở quy trình review đầy đủ.

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
- Đã phản bác mà sai → "Đã kiểm X, nó làm Y — anh đúng. Sửa." Không xin lỗi dài, không bào chữa.
- Phản hồi từ người dùng: tin, nhưng vẫn hỏi khi phạm vi chưa rõ; vẫn không nói "anh nói đúng".
- Trả lời thread PR trên GitHub: trả lời **trong thread** (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), không comment cấp PR.

## 7. Luật dừng

- Không xếp chồng reviewer đọc cùng một thứ theo cùng một cách — tranh luận trên cùng văn bản không
  thêm thông tin, chỉ nhân chi phí ("sân khấu nhiều agent").
- Không chạy review đầy đủ cho sửa một dòng hay thẩm mỹ: đọc.
- Không bật hook review tự động khi người dùng không yêu cầu — vòng lặp đốt hạn mức.
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
| "Mục rõ thì làm ngay cho kịp giờ, mục mơ hồ hỏi sau" | còn mục chưa rõ thì chưa sửa mục nào; mục mơ hồ có thể đổi cách làm mục rõ |
