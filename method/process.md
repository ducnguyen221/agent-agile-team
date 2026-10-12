---
title: Process — six steps, two human gates
type: method
status: active
updated: 2026-10-05
---

# Quy trình: sáu bước, hai cổng người

> **Kết luận:** mọi sprint đi đúng sáu bước; người dùng xác nhận **một lượt trao đổi tiếp nhận** (mục tiêu,
> bậc việc, có mở sprint không — mục 2), rồi chỉ phải quyết ở **hai cổng** (Cổng 1 duyệt SPEC + PLAN, Cổng 2
> nghiệm thu) và ở **bốn điều kiện dừng**. Mọi điểm còn lại agent tự quyết, ghi phán quyết vào PROGRESS và đi
> tiếp. Sprint = một mục tiêu, không đo theo thời gian. Việc **làm thẳng** ([sizing.md](sizing.md) mục 1)
> không mở sprint và không đi sáu bước.

Thuật ngữ: **sprint** — một lượt làm việc phục vụ đúng một mục tiêu · **cổng** — điểm dừng chờ người
dùng quyết · **vòng** — một lần quay từ kiểm định về thực thi · **điều phối** — vai Analyst khi nó
dẫn sprint · **frontmatter** — khối khoá–giá trị ở đầu file tài liệu, máy đọc được · **subagent** —
agent con được agent chính giao một việc kèm brief riêng · **worktree** — bản chép riêng của repo để
làm một việc mà không đụng bản chính. Mã mục (`TK`, `RF`, `BR`…) theo
[skills/id-convention](../skills/id-convention/SKILL.md); thang mức theo [severity.md](severity.md);
cỡ việc theo [sizing.md](sizing.md). Gặp tên skill cũ trong hồ sơ lịch sử: `docs/MIGRATION.md`.

## 1. Sơ đồ

| Bước | Tên | Ai làm | Tài liệu ra | Cổng |
|---|---|---|---|---|
| 1 | Tiếp nhận | Analyst (T1) | **một** tin trao đổi gom với người dùng; sau xác nhận: dòng `RQ-` trong REQUESTS (hoặc làm thẳng, không hồ sơ) | Không phải cổng — lượt trao đổi tiếp nhận xác nhận mục tiêu, bậc từng việc, có mở sprint không; bỏ khi đã rõ (mục 2) |
| 2 | SPEC rồi PLAN | Analyst (SPEC), Architect (PLAN), Tech Reviewer (review PLAN từ cỡ vừa) | SPEC, PLAN | **Cổng 1** — duyệt / điều chỉnh |
| 3 | Thực thi | Implementer, QA, (Architect) theo từng `TK` | PROGRESS | cổng điều chỉnh nội bộ (không hỏi người) |
| 4 | Kiểm định | Business Reviewer, Tech Reviewer — **agent khác** người làm (thêm reviewer thứ hai khi `risk_tags` có `rules`/`secret`/`auth`) | `VR`, `RF` | vòng lặp 3 ↔ 4 |
| 5 | REPORT | Analyst | REPORT | **Cổng 2** — nghiệm thu |
| 6 | Bài học | Analyst (kiêm Distiller) | `LN` + nơi lưu bài học | không |

Bước 3 và 4 lặp cho tới khi không còn phát hiện mức Chặn hay Phải sửa (mục 6).

**Nạp thẻ vai trước khi làm.** Khi bắt đầu tiếp nhận, viết SPEC/PLAN, bàn giao thực thi hoặc QA/kiểm định,
Analyst đưa đường tới đúng thẻ trong [bảng vai](../roles/README.md) vào brief hiện có, cùng con trỏ tới bước
quy trình và mục đầu vào liên quan. Agent nhận việc tự mở thẻ và các mục được trỏ trước hành động của vai;
log đọc file của chính agent là bằng chứng, điều phối đọc thay không đủ. Analyst tự giữ vai cũng phải tự đọc
thẻ trước khi làm. Chỉ nạp vai đang dùng, không dán lịch sử hay cả thư viện vai vào brief; hợp đồng brief,
quyền, tier và các cổng giữ theo quy trình hiện hành.
Khi dùng nguồn ngoài, brief giữ rõ nguồn do ai cung cấp và phần nào đã/chưa kiểm chứng; người nhận giữ
đúng dữ kiện đó khi bàn giao, không hỏi lại dữ kiện nguồn đã có hay biến ví dụ thành yêu cầu; chỉ hỏi thêm
nội dung nguồn còn thiếu khi cần cho phần việc được giao.

**Người dùng cần làm gì:** giao yêu cầu bằng lời thường ở Bước 1 và trả lời **một** tin trao đổi của Analyst
(mục tiêu đúng chưa, câu hỏi phản biện, bậc việc, có mở sprint không); trả lời **"duyệt"** hoặc **"điều
chỉnh: <gì>"** ở Cổng 1; kết luận **Đạt / Đạt có điều kiện / Không đạt** ở Cổng 2. Ngoài ra chỉ phải
lên tiếng khi agent dừng ở bốn điều kiện (mục 5), sau vòng 3 (mục 6) hoặc khi cạn hạn mức tier.

## 2. Bước 1 — Tiếp nhận (một lượt trao đổi gom)

Mục đích của bước này là **phối hợp đúng từ đầu và mở yêu cầu chi tiết nhất có thể**: người dùng và agent cùng
hiểu một mục tiêu, một định nghĩa xong, một phạm vi, một bậc việc — trước khi có bất kỳ hồ sơ nào. Vai làm: Analyst,
tier **T1** (cần phân tích và phản biện, không hạ tier).

KHI người dùng giao một yêu cầu THÌ Analyst:

1. **Đọc và phân tích đầu bài** trước khi hỏi: tra repo, sổ gốc, spec sống; rà 11 điểm thiếu ngữ cảnh theo skill
   `intake` — điểm nào tra được thì tra, không hỏi. Kết quả phân tích là nguyên liệu cho tin ở bước 2.
2. **Gửi người dùng một tin trao đổi gom** (không hỏi lẻ nhiều lượt), đủ bốn phần:
   - *Mục tiêu theo cách hiểu của agent* — nhắc lại bằng lời thường, một đến ba câu.
   - *Câu hỏi phản biện* — để hiểu đúng **mục tiêu** (vì sao cần, kết quả trông ra sao), **định nghĩa xong**
     (đo bằng gì), **phạm vi** (cái gì không làm); mỗi câu kèm đề xuất của agent. Chỉ hỏi điều thuộc ý muốn
     người dùng; điều tra được từ repo không hỏi.
   - *Khuyến nghị bậc cho từng việc* — làm thẳng / rất nhỏ / nhỏ / vừa / lớn theo [sizing.md](sizing.md), kèm
     dấu hiệu đo được và rủi ro nhìn thấy của mỗi việc (rủi ro chỉ nâng); ghi ngay trong tin gửi người dùng.
   - *Có cần mở sprint không* — hỏi thẳng, kèm khuyến nghị suy từ bậc (làm thẳng → không; từ rất nhỏ → có).
3. **Chờ người dùng xác nhận** (có thể đổi mục tiêu, bậc, hay quyết làm thẳng). Chưa có xác nhận thì chưa ghi
   `RQ-`, chưa mở sprint, chưa chạm mã.
4. Người dùng chọn **làm thẳng** (hoặc nói "không cần sprint") → làm ngay theo [sizing.md](sizing.md) mục 1, không
   hồ sơ; kiểm bằng lệnh + kết quả mới chạy, báo trong lời trả lời. Hết bước này.
5. Người dùng chọn **mở sprint** → ghi một dòng `RQ-` mới vào sổ REQUESTS: ngày, tóm tắt một câu, trạng thái `mới`,
   **chi tiết nhất có thể**: chép câu trả lời của người dùng (mục tiêu đã chốt, định nghĩa xong, phạm vi ngoài, bậc
   đã xác nhận) vào `RQ-` và sau đó vào SPEC. Tách theo mục tiêu: một mục tiêu = một sprint (`SPR-`); nhiều mục
   tiêu → nhiều sprint cùng trỏ về một `RQ-`.
6. Định cỡ và rủi ro theo [sizing.md](sizing.md) (bậc người dùng đã xác nhận; rủi ro chỉ nâng cỡ, không hạ). Liệt kê
   giả định còn lại dưới nhãn **ASSUMPTION** (mỗi giả định một dòng, nói rõ nếu sai thì đổi gì). Điểm chưa rõ mà
   **không tự giả định được và chưa hỏi ở tin trao đổi** thì gom thành `CQ` để hỏi **một lần** ở Cổng 1 (cỡ
   vừa/lớn; cỡ nhỏ trình ngắn ở Cổng 1; cỡ rất nhỏ không có `CQ` chặn — lời giao đã nêu rõ kết quả).
7. Đi sang bước 2. Không hỏi thêm lượt nào nữa cho tới Cổng 1.

**Khi nào bỏ lượt trao đổi:** người dùng nói rõ "không cần sprint" cho đúng việc, hoặc việc là làm thẳng
**không mơ hồ** (1–2 thao tác, kết quả rõ, không chạm vùng loại trừ của [sizing.md](sizing.md) mục 1). "Làm luôn"
chỉ thúc tiến độ, không tự miễn sprint hay mở ngoại lệ cho vùng loại trừ. Đủ điều kiện bỏ lượt trao đổi thì làm
ngay và báo. Lời giao đủ mục tiêu, định nghĩa xong, phạm vi và bậc thì tin chỉ còn một câu xác nhận — không hỏi lại.

**Lượt trao đổi là một tin, không phải một chuỗi.** Hỏi lẻ từng câu, chờ, hỏi câu nữa ở bước này là lỗi quy
trình như mọi chỗ khác; ngoại lệ duy nhất là người dùng mở chế độ làm rõ (skill `shaping-spec` mục 3).

## 3. Bước 2 — SPEC rồi PLAN, Cổng 1

- Mở sprint: ghi dòng `SPR-` vào sổ SPRINTS (cột Mở, Mục tiêu; cột Đóng để trống) và dựng thư mục
  sprint từ mẫu — công cụ `init` làm. Nếu SPEC mở một **tính năng mới** thì cấp `FS-` và tạo spec sống
  ngay ở bước này (trạng thái `đề xuất`); tính năng có sẵn thì chỉ trỏ `FS-` cũ. Sổ SPECS và spec sống
  chỉ cập nhật **hành vi hiện hành** sau Cổng 2.
- Analyst viết **SPEC** (làm cái gì, cho ai, thế nào là xong): bối cảnh · `US` · `FR` với kịch bản
  KHI… THÌ… · `SC` · ngoài phạm vi · `CQ` (có thể rỗng, ghi rõ "không có"). Mục "Đổi hợp đồng / giao diện" (API, sự
  kiện, schema sẽ đổi và mọi bên dùng chúng — skill `shaping-spec`) bắt buộc khi cỡ lớn hoặc `risk_tags` có
  `public_api`; cỡ khác xoá mục.
- Architect viết **PLAN** (làm thế nào, ai làm, kiểm ra sao): mục tiêu · kiến trúc · ràng buộc chung ·
  trọng tâm review (≤5) · `TK` (vai + tier, đầu vào/ra, cách kiểm, cổng, hoàn tác, trỏ `FR`/`SC`) ·
  `RK` · `DN` · ước lượng (skill `writing-plan`). PLAN ghi **quyết định** (chữ ký, giá trị, assertion),
  không chép code.
- Từ cỡ **vừa**, Tech Reviewer review PLAN một lượt trước khi trình (skill `plan-review`): thách thức phạm
  vi, kiến trúc, phủ test. Phát hiện mức Chặn/Phải sửa thì sửa PLAN trước khi trình. Phát hiện ghi ở REPORT
  mục "Phát hiện của reviewer", tiểu mục "Review PLAN trước Cổng 1".
- Giao review PLAN cần model cho tier T1. Chưa có bảng tier (`AGENT_AGILE_TIERS`) thì dùng chỉ định tier →
  model người dùng đã nêu trong chat, ghi nguyên văn vào PROGRESS dòng `Phán quyết:`. Chưa có cả hai → không
  đoán: ghi `DN` "chỉ định tier → model" kèm khuyến nghị, trình ở Cổng 1; review PLAN chạy **ngay sau** khi có
  chỉ định, trước khi thực thi (`tiers/README.md` mục 2).
- **Cấm viết code trước Cổng 1.** Thử nghiệm kỹ thuật để trả lời `CQ` thì được, nhưng kết quả chỉ vào
  SPEC/PLAN, không vào nhánh sản phẩm.

**Trình Cổng 1.** Analyst gửi người dùng **một** bản tóm tắt, theo thứ tự: kết luận một câu → `CQ`
còn mở → `DN` cần người → rủi ro mức Chặn / Phải sửa → ước lượng công sức → đường tới SPEC và PLAN.
Mỗi mã kèm tên ngắn. Không dán cả tài liệu vào chat. Lời trình chuẩn:

```
Cổng 1 — sprint <SPR-> (<mục tiêu một câu>), cỡ <cỡ>, rủi ro <mức>.
Kết luận: <SPEC + PLAN sẵn sàng; điểm cần anh quyết là …>
CQ còn mở: <CQk (tên) — đề xuất: …> (hoặc "không")
DN cần anh: <DNk (tên) — phương án, khuyến nghị> (hoặc "không")
Rủi ro Chặn/Phải sửa: <RKk (tên) — cách giảm> (hoặc "không")
Ước lượng: <số việc, số vòng dự kiến>
Tài liệu: <đường tới SPEC>, <đường tới PLAN>
Anh trả lời: "duyệt" / "điều chỉnh: <gì>"
```

**Kết quả Cổng 1.**
- *Duyệt* → ghi `gate_1: approved` vào frontmatter SPEC và PLAN, kèm thời điểm `gate_1_at` và **câu
  duyệt nguyên văn** `gate_1_quote` (ví dụ `gate_1_quote: "duyệt, DN2 chọn phương án b"`). Chỉ từ lúc đó
  mới được thực thi.
- *Điều chỉnh* → sửa SPEC/PLAN đúng điểm người dùng nêu, trình lại. Mỗi lần trình lại chỉ trình đúng
  phần đã đổi.
- Người dùng trả lời `CQ`/`DN` nào thì ghi câu trả lời vào đúng mục đó; không hỏi lại điều đã có câu trả lời.

**Chỉ duyệt đúng giai đoạn đang trình.** Người dùng duyệt SPEC không có nghĩa duyệt PLAN; duyệt PLAN
không có nghĩa duyệt kết quả. Agent không được suy một lời "ok" ở bước này thành phép làm ở bước sau.

## 4. Bước 3 — Thực thi và cổng điều chỉnh nội bộ

- Mỗi `TK` do đúng vai và tier ghi trong PLAN làm (skill `running-sprint`). Khi giao cho subagent:
  brief soạn riêng (mục tiêu, phạm vi, đầu vào, điều cấm, cách báo cáo), **không dán lịch sử phiên**,
  và **ghi vai + tier + model thực tế** vào cột "Vai · tier · model" của PROGRESS; nhãn agent
  (`agent-a`, `agent-b`…) vào `roles` của frontmatter.
- Sau mỗi `TK`: cập nhật bảng trạng thái PROGRESS (Đạt / Không đạt / Chưa chạy / Không áp dụng / Đang
  làm) kèm **bằng chứng** theo [evidence.md](evidence.md). Hai dòng tối thiểu cho mỗi `TK`: lúc bắt đầu
  (brief + mốc commit gốc) và lúc xong (lệnh kiểm + kết quả thật).
- Nhật ký PROGRESS **chỉ thêm, không sửa** dòng cũ.

**Cổng điều chỉnh nội bộ.** Mâu thuẫn giữa SPEC và PLAN, chỗ PLAN mơ hồ, chi tiết PLAN chưa lường,
giới hạn nhỏ cần vượt — **Analyst tự quyết, không hỏi người dùng**, miễn còn trong phạm vi đã duyệt ở
Cổng 1. SPEC là thẩm quyền cao nhất, PLAN là lập luận của nó, phán quyết của Analyst lấp chỗ cả hai
chưa nói. Mỗi phán quyết ghi **một dòng** vào nhật ký PROGRESS:

```
Phán quyết: <quyết gì> — <vì sao> — <sai thì tốn gì>
```

Một phán quyết sai tốn công làm lại mà người dùng thấy và hoàn tác được; một phiên đứng chờ câu hỏi
tốn cả buổi của người dùng và không mua được gì. Phán quyết đổi tiêu chí thành công hay vượt phạm vi đã
duyệt **không** phải phán quyết — đó là điều kiện dừng (d) ở mục 5.

## 5. Bốn điều kiện dừng giữa chừng

Ngoài lượt trao đổi tiếp nhận (mục 2), hai cổng, bốn điều kiện này, mốc sau vòng 3 và cạn hạn mức tier, **không
hỏi**. KHI gặp một trong
bốn trường hợp sau THÌ dừng, ghi `BR` vào bảng Vướng mắc của PROGRESS (vướng gì, loại (a)–(d), đã làm
gì, cần ai, trạng thái) và hỏi người dùng:

| | Điều kiện | Ví dụ |
|---|---|---|
| (a) | Hành động **không đảo ngược** được hoặc phá hủy | xoá dữ liệu, viết lại lịch sử git, xoá nhánh chưa gộp |
| (b) | Chạm **bảo mật hoặc secret** | đọc/ghi file chứa khoá, đổi quyền, tắt kiểm tra xác thực |
| (c) | Tác động **ra ngoài phạm vi / worktree** đã giao | push nhánh chung, gộp vào nhánh chính, deploy, gửi tin, sửa file ngoài dự án |
| (d) | **PLAN hỏng** — giả định sai làm đổi tiêu chí thành công, hoặc mọi đường đi tiếp đều là đoán | thư viện nền không hỗ trợ tính năng cốt lõi |

Ngoài bốn điều này (và lượt trao đổi tiếp nhận đã qua ở Bước 1), dừng hỏi là **lỗi quy trình** (đếm được: số
lần hỏi ngoài cổng phải bằng 0).
Tương tự, cạn hạn mức model của một tier → dừng phần việc của tier đó, ghi `BR`, báo; **không tự hạ
tier** ([tiers/README.md](../tiers/README.md)).

## 6. Bước 4 — Kiểm định bởi agent khác, vòng lặp

- Kiểm định do **agent khác** người làm: phiên hoặc subagent mới, nhận ngữ cảnh soạn riêng. Một agent
  không bao giờ giữ cùng lúc vai thực thi và vai kiểm định cho cùng một sản phẩm
  ([roles/README.md](../roles/README.md)).
- Business Reviewer kiểm **đáp ứng yêu cầu** (`US`/`FR`/`SC`); Tech Reviewer kiểm **kỹ thuật** (code,
  test, bảo mật, dữ liệu, backend, frontend) và kéo thẻ chuyên đề khi rủi ro cao. Cỡ nhỏ: **một** reviewer
  khác người làm giữ cả hai lăng kính; cỡ rất nhỏ: tự kiểm có ghi "chưa độc lập" hoặc agent khác chạy nhanh
  (mục 9).
- `risk_tags` có `rules`, `secret` hoặc `auth` (ba nhãn này luôn kéo cỡ lớn, [sizing.md](sizing.md) mục 2) → kiểm định kỹ thuật theo
  [roles/verifier/dual-review.md](../roles/verifier/dual-review.md): **hai** reviewer độc lập, cùng rubric,
  cả hai Đạt mới Đạt. Một reviewer là chưa đủ cho các vùng này.
- Mỗi phát hiện là một `RF` mang một mức: Chặn / Phải sửa / Nên sửa / Ghi chú, có bằng chứng
  (`file:dòng` hoặc lệnh + kết quả). Reviewer được trả **0 phát hiện** và **phải** ghi phần mình không
  đánh giá.
- Người làm tiếp nhận review bằng cách **kiểm chứng trước khi sửa**; được phản bác có bằng chứng; cấm
  đồng ý cho có; sửa xong phải chạy lại test (skill `code-review`).

**Vòng.** Còn Chặn hoặc Phải sửa → quay lại bước 3; mỗi lần quay lại là **một vòng**, ghi
`review_round` trong PROGRESS. Nên sửa được **hoãn** và ghi thành `CO`; Ghi chú không chặn.

**Ba vòng sửa có kiểm chứng.** Baseline lỗi đầu tiên không tiêu vòng sửa. Mỗi vòng có hypothesis,
thay đổi thực tế, cùng oracle và outcome; tối đa ba vòng cho assignment. Ghi repair_cycle_index riêng
với review_round, root cause/test/regression refs và total counters. Hết vòng 3 còn cùng lỗi, không
tiến triển hoặc bất kỳ regression chưa xử lý: stop writer, cảnh báo, handoff một tier cao hơn trong
scope/hãng/role đã cấp. Không vòng 4 cho assignment bị kẹt. Chi tiết và pin/capability/quyền/T1 ceiling:
[task-routing.md](task-routing.md) mục 4. Analyst báo:

```
Sau 3 vòng sửa có kiểm chứng, sprint <SPR-> còn <n> phát hiện mức Chặn/Phải sửa:
- RF<k> (<tên>) — <một dòng vì sao chưa xong>
...
Đã dừng assignment <cũ>; kết quả/oracle/counters: <refs>.
Bàn giao: <agent/vai/tier/model/effort mới trong scope>; lý do: <cùng lỗi/no progress/regression>.
Nếu pin, T1 ceiling hoặc thiếu quyền/capability: <đúng phần cần người quyết, kèm khuyến nghị>.
```

Handoff đã có quyền thì thông báo rồi làm, không xin lại. Receiver có chu kỳ riêng tối đa ba vòng,
giữ lịch sử tổng. Pin/ceiling/quyền thiếu thì chờ đúng quyết định phụ thuộc; việc độc lập vẫn tiếp tục.
Phần không đạt giữ nguyên mức và evidence; không đổi Chặn/Phải sửa thành CO để vượt Cổng 2.

### 6.1 Thiết kế vòng lặp — khi giao agent chạy lặp

Vòng 3 ↔ 4 ở trên là một vòng lặp có người canh. Mục này áp khi sprint giao cho agent một vòng **tự chạy lặp**: "sửa tới
khi test xanh", canh CI cho tới khi xanh, một việc định kỳ. Nền: máy đo được "còn cách đích bao xa" và mài về
không; **đích có đúng không, có nên đổi hay dừng** là phán đoán của người, vì máy không đứng ra ngoài vòng để nghi ngờ
đích của nó. Giao phán đoán, nghiệm thu hay công tắc cuối cho vòng là bỏ phản hồi bậc cao — nó chạy nhanh và mạnh tới
một đích chưa ai hỏi.

1. **Có đáng dựng vòng không — thiếu một điều kiện là không dựng.** Việc lặp lại đủ thường để bù công dựng · kiểm
   được bằng máy · ngân sách token chịu nổi · agent có công cụ thật sự chạy và thấy kết quả. Việc làm một lần thì
   làm tay.
2. **Đích máy quyết được có/không.** "Làm cho tốt" không phải đích. Viết đích kèm **điều cấm** ("không xoá hay làm yếu
   test, không hạ coverage") — chỉ có tiêu chí xong mà không có điều cấm là giấy phép gian lận (đích bị lách khi nó
   thành thước đo). Ưu tiên đối chiếu với **sự thật bên ngoài** (mẫu vàng, tổng nguồn, số của hệ khác) hơn là khẳng
   định của chính mã. Phép thử: đọc đích cho người ngoài lĩnh vực — họ chạy một lệnh và biết xong chưa không?
3. **Ba vai: lập kế hoạch · làm · chấm.** Người chấm **độc lập** với người làm (khớp luật "người làm không tự
   chấm"), chấm bằng quy tắc xác định (test, lệnh đối chiếu, kiểm kiểu), không bằng "trông ổn". Người làm **không được
   sửa tiêu chí nghiệm thu** để qua: tiêu chí đổi là đổi `SC` và là điều kiện dừng (d) ở mục 5.
4. **Giảm chấn.** Trần số vòng và điểm dừng cứng; hết trần thì báo người (mục 6: khuyến nghị 3 vòng). Phản hồi âm không
   giảm chấn thì dao động, đốt token tại chỗ.
5. **Làm hết các câu hỏi trước khi chạy.** Agent chạy lặp sẽ không dừng giữa đêm để hỏi; nó chạy tới cùng với đáp án
   đoán. Mọi điều chưa rõ gom thành `CQ` và hỏi một lần ở Cổng 1 (mục 3).
6. **Đưa lên từng nấc.** Chạy tay một lần (buộc phải nói rõ người chấm quyết thế nào) → đóng gói thành quy trình hoặc
   subagent → mới tới chạy tự động theo lịch.

**Rà một vòng trước khi cho chạy — trúng một dòng là gửi trả:**

| Cách hỏng | Câu hỏi rà | Thuốc |
|---|---|---|
| Đích là câu đúng nhưng chung chung → quay vô tận | đích có máy quyết được không? | thay bằng điều kiện kết quả quyết được |
| "Kiểm" viết thành "xem có ổn không" → agent tự nói ổn rồi dừng | người chấm có là bị cáo? chấm bằng "trông đúng" hay quy tắc xác định? | đối chiếu + mã thoát + người chấm độc lập |
| Chỉ chặn bằng "mọi test xanh" → agent xoá test | có điều cấm đi cùng tiêu chí xong không? | tiêu chí xong **cộng** điều cấm |
| Trông chờ agent hỏi giữa chừng | có chỗ nào "đợi chạy tới đó mới hỏi"? | hỏi hết trước khi chạy |
| Tài liệu nền phình và cũ → vòng càng nhanh càng sai | tài liệu agent dựa vào còn mới không? ai giữ? | giữ tài liệu ngắn, rà định kỳ |

**Ba vạch đỏ — vi phạm một là không được tự chạy:** (1) **phán đoán ở lại với người** — ô "xong" và nghiệm thu do người
bật, vòng là thợ, không phải người nghiệm thu; (2) **trách nhiệm không chuyển** — thứ mà sai là không gánh nổi
(gộp nhầm nhánh chính, phát hành nhầm, chuyển nhầm tiền) thì không giao quyền tự động, khớp điều kiện dừng ở mục 5;
(3) vòng càng "tự cải tiến, tự viết lại luật của mình" thì người duyệt phải càng **chặt**, không lỏng — máy nhanh quá
để chặn sau, nên phán đoán của người nằm **trước** hành động như một cổng cứng, không phải miếng vá sau.

## 7. Bước 5 — REPORT và Cổng 2

KHI kiểm định không còn Chặn/Phải sửa, hoặc người dùng chọn dừng, THÌ Analyst viết **REPORT** theo
mẫu: câu đầu là kết luận · tóm tắt cho người không chuyên · kết quả kiểm định (`VR`: Đạt / Không đạt /
Chưa chạy / Không áp dụng + lý do) · phát hiện của reviewer (`RF` + mức + trạng thái xử lý) · rủi ro còn
lại · cách dùng, đã đổi gì, cách hoàn tác · bài học (`LN`) · việc để lại (`CO`) · review & retro (sản
phẩm đã đạt gì ↔ cách làm nên đổi gì) · Cổng 2 · tổng token phiên (mốc đo). REPORT thay cho bàn giao:
không có tài liệu bàn giao riêng.

**Nợ để lại vào sổ.** Mỗi `CO` ghi vào REPORT thì cùng lúc thành **một dòng `RQ-`** trạng thái `mới` trong
REQUESTS, tóm tắt ghi nguồn `từ SPR-xx/COn`; cột Đề xuất của REPORT ghi mã `RQ-` đó. Điều kiện của *Đạt có
điều kiện* sinh sau Cổng 2 cũng vậy. Nợ chỉ sống ở REQUESTS — không ai phải mở REPORT cũ để tìm nợ.

**Trình Cổng 2** giống Cổng 1: một bản tóm tắt, kết luận trước, mã kèm tên. Lời trình chuẩn:

```
Cổng 2 — sprint <SPR-> (<mục tiêu một câu>), sau <n> vòng kiểm định.
Kết luận: <đạt gì so với SC; reviewer kết luận …>
Kiểm định: <k/m SC có VR Đạt; VR Chưa chạy/Không áp dụng: … (lý do)>
Phát hiện còn mở: <RFk (tên) — mức — xử lý> (hoặc "không")
Việc để lại: <COk (tên) — chủ — mốc> (hoặc "không")
Cách dùng / đã đổi gì / hoàn tác: <một dòng mỗi ý>; REPORT: <đường dẫn>
Phiên bản đề xuất: <MAJOR | MINOR | PATCH> → <số>, vì <thay đổi nặng nhất> (hoặc "không áp dụng") — bảng ở conventions.md mục 4.1
Anh kết luận: Đạt / Đạt có điều kiện (kèm điều kiện) / Không đạt (kèm lý do)
```

Người dùng kết luận **Đạt / Đạt có điều kiện / Không đạt**:
- *Đạt* → ghi `gate_2: pass` + `gate_2_at` + `gate_2_quote` nguyên văn; cập nhật **spec sống** của tính
  năng trong thư mục spec sống theo cấu hình (`paths.feature_specs_dir`) ngay trong sprint; đóng sprint
  trong SPRINTS; lúc này mới trình menu nhánh (gộp local / push + PR / giữ nguyên — skill
  `closing-sprint`; push và PR là tác động ra ngoài, cần người dùng gật).
- *Đạt có điều kiện* (`conditional_pass`) → như Đạt, điều kiện ghi thành `CO` có chủ và mốc theo dõi, kèm
  dòng `RQ-` như trên.
- *Không đạt* (`fail`) → ghi lý do nguyên văn; mở vòng mới hoặc sprint mới theo người dùng chọn.

## 8. Bước 6 — Bài học

KHI sprint đóng THÌ Analyst (kiêm Distiller) rút bài học `LN`, tự chấm trước khi lưu (skill
`closing-sprint`, phần bài học): bài học có **tái dùng** được không? có tra lại được từ code/git/docs
không (nếu có thì không lưu)? có mâu thuẫn với bài học cũ không (nếu có thì gộp, không đẻ bản trùng)?
Retro thấy nợ để lại bằng cách đọc **khối "Đang mở" của REQUESTS** (dòng có nguồn `từ SPR-xx/COn`), không
mở REPORT cũ.

- Nơi lưu bài học do **lớp riêng** của môi trường quy định (điểm cắm trong `hosts/`); lõi chỉ quy định
  bài học ghi theo timeline, mỗi bài học một nguồn (sprint nào, bằng chứng nào).
- Bài học đánh dấu **quan trọng** THÌ **chỉ đề xuất** nâng thành luật, skill hoặc bước quy trình, kèm lý
  do và chi phí; người dùng quyết. Agent không tự sửa luật hay tự tạo skill từ bài học.

## 9. Việc nhẹ — làm thẳng, cỡ rất nhỏ và cỡ nhỏ

**Làm thẳng** (không sprint) — việc 1–2 thao tác có kết quả rõ, hoặc người dùng nói rõ không cần sprint
([sizing.md](sizing.md) mục 1, kèm điều kiện loại trừ): không `RQ-`, không `SPRINT.md`, không dòng sổ; làm ngay,
kiểm bằng lệnh + kết quả mới chạy, báo kết quả và bằng chứng trong lời trả lời. Giữ nguyên Git và điều cấm, giữ
mọi cổng xin phép khác (file luật, hành động không đảo ngược, secret). Lộ ra phức tạp hơn → dừng, mở lượt trao
đổi tiếp nhận (mục 2).

Hai cỡ nhẹ có sprint dùng **một** file `SPRINT.md` (bảng cỡ và dấu hiệu đo được: [sizing.md](sizing.md) mục 1); phân
vân giữa hai bậc thì chọn bậc nặng hơn.

**Cỡ rất nhỏ** (đổi chữ hoặc một chỗ, không đổi hành vi hay quyền, lời giao đã nêu rõ kết quả) — "có kế hoạch
rồi làm cho hoàn thiện":
- `SPRINT.md` có **hai** phần: "Kế hoạch" (lời giao, mục tiêu, tiêu chí xong `SC`, việc `TK` trỏ `SC`) và "Kết
  quả" (nhật ký ngắn, `VR` cho mỗi `SC`, cách hoàn tác). Không SPEC / PLAN riêng. `SPRINT.md` bốn phần của
  sprint cũ vẫn hợp lệ.
- **Cổng 1** không mở lượt hỏi mới: khi lời giao của người dùng đã nêu rõ kết quả, ghi
  `gate_1: approved`, `gate_1_at` là thời điểm giao, `gate_1_quote` là **trích nguyên văn** lời giao với
  tiền tố "đạt theo lời giao: …". Lời giao chưa nêu rõ kết quả thì không phải việc rất nhỏ — nâng cỡ.
- **Cổng 2** gộp vào lời báo cuối lượt: câu đầu là kết quả + bằng chứng; người dùng không phản đối trong
  lượt đó là nghiệm thu **ngầm** — ghi trung thực `gate_2: pass`, `gate_2_at`, và
  `gate_2_quote: "nghiệm thu ngầm — không phản đối tới <thời điểm>"`; người dùng lên tiếng thì ghi câu
  nguyên văn thay vào.
- Luật "người làm không tự chấm" vẫn áp: `VR` do agent khác chạy, hoặc ghi rõ "tự kiểm, chưa độc lập"
  và kết luận chỉ được là **Đạt có điều kiện**.

**Cỡ nhỏ** (sửa cục bộ một luồng có sẵn, một `FR`, không đổi hợp đồng / giao diện / schema, không có quyết định
kiến trúc):
- `SPRINT.md` đủ **bốn** phần SPEC · PLAN · PROGRESS · REPORT, mỗi phần ngắn (một `FR`, một hai `SC`, vài `TK`).
- **Cổng 1 là lượt duyệt thật**: trình tóm tắt ngắn, chờ người dùng duyệt rồi mới làm (mục 3). **Cổng 2 cũng thật**
  (mục 7).
- **Một** reviewer (agent khác người làm) kiểm cả nghiệp vụ lẫn kỹ thuật, một vòng ngắn; vòng sửa và điều kiện
  dừng như mục 5–6.

Giữ đủ hai cổng về mặt hồ sơ ở cả hai bậc; riêng cỡ rất nhỏ không thêm lượt hỏi về mặt con người.
Việc nâng cỡ giữa chừng (lộ rủi ro mới) thì chuyển sang bốn file ở cỡ vừa/lớn, ghi `Phán quyết:`.

## 10. Khi nào được hỏi người dùng — bảng tra nhanh

| Được hỏi | Không được hỏi (tự quyết + `Phán quyết:`) |
|---|---|
| Lượt trao đổi tiếp nhận — **một** tin gom (mục 2) | Hỏi lẻ nhiều lượt ở tiếp nhận; hỏi điều repo trả lời được |
| Cổng 1, Cổng 2 | Chi tiết triển khai PLAN chưa nói |
| Bốn điều kiện dừng (mục 5) | Mâu thuẫn nhỏ SPEC ↔ PLAN còn trong phạm vi |
| Sau vòng 3 còn Chặn/Phải sửa (mục 6) | Chọn thư viện/cách làm tương đương trong ràng buộc đã duyệt |
| Cạn hạn mức tier (không tự hạ tier) | Thứ tự làm `TK`, tách `TK` con |
| `CQ` gom ở Cổng 1 (một lần) | Hỏi lẻ từng câu giữa chừng |
| Tư vấn gọi chéo hãng (chỉ tư vấn, người dùng quyết) | Tự chạy gọi chéo |

## 11. Ghi sổ tại cổng

Dự án muốn một **sổ tập trung** (một file Markdown mỗi dự án, nằm ngoài repo, nơi nhiều dự án cùng được xem trạng
thái) thì bật bằng khoá `ledger.project` (tên dự án trong sổ) ở `.agile.json`; máy chỉ cấp **mẫu đường** kho sổ qua
biến môi trường `AGENT_AGILE_LEDGER` (chứa `{project}`). Dự án không khai khoá thì mục này không áp và `check`
không đọc sổ, kể cả khi máy đặt biến. Đường dẫn của máy không bao giờ vào file commit của repo. Khuôn file sổ:
[templates/registry/LEDGER.md](../templates/registry/LEDGER.md).

KHI một trong năm thời điểm dưới đây xảy ra THÌ cập nhật **hồ sơ sprint trước, sổ tập trung ngay sau, trong cùng
lượt** — mỗi lần ghi trạng thái cụ thể kèm bằng chứng, không ghi "đang làm" chung chung:

| Thời điểm | Ghi gì | Ở đâu | Bằng chứng |
|---|---|---|---|
| Mở sprint | `status: drafting`, ngày mở; thêm **dòng mới** trong sổ, link trỏ nhánh sprint | PROGRESS (hoặc `SPRINT.md`) + SPRINTS + dòng sổ | dòng sổ vừa thêm; `check` không báo `ledger-missing-row` |
| Qua Cổng 1 | `in_progress`, `gate_1: approved` và câu duyệt nguyên văn | PROGRESS (hoặc `SPRINT.md`) + dòng sổ | `gate_1_quote` |
| Quay lại bước 3 sau kiểm định **mà trạng thái đổi** | `in_progress` hoặc `blocked`, `review_round` mới; việc `RF` phải sửa còn mở | PROGRESS + dòng sổ | `RF` và `VR` của vòng vừa xong |
| Cổng 2 | `awaiting_gate_2`, rồi `done` hoặc `dropped` theo lời người dùng; `verdict` | REPORT + PROGRESS + dòng sổ | `gate_2_quote`; kết quả trong REPORT |
| Đóng sprint | trạng thái cuối; cột Hồ sơ đổi sang `REPORT.md`; link đổi sang `main` hoặc SHA khi hồ sơ nằm trong repo | dòng sổ (cập nhật, không thêm dòng) | lệnh gộp hoặc commit vừa chạy |

Dòng sổ có năm cột: `Sprint` · `Trạng thái` (đúng giá trị `status` của PROGRESS hoặc `SPRINT.md`) · `Cập nhật`
(ngày `YYYY-MM-DD`, không cũ hơn `updated` của hồ sơ) · `Hồ sơ` (`<repo>:docs/plans/<slug>/<tài-liệu>.md`; `<tài-liệu>` là `PROGRESS.md` khi sprint đang mở, `REPORT.md` khi đã
`done`/`dropped`, và luôn `SPRINT.md` với sprint một file) ·
`Link` bấm được. Hồ sơ **trong repo** → URL GitHub blob với `<ref>` là nhánh sprint khi đang mở, `main` hoặc SHA khi
đã đóng. Hồ sơ **ngoài repo** → đường tương đối trong kho sổ tới thư mục plan. Visibility của repo chỉ khuyến nghị
nơi đặt hồ sơ, không quyết hình link.

**Chạy `check` trên gốc dự án** (thư mục có `.agile.json`); `check` đọc sprint theo `paths.sprint_dir`. Chạy riêng trên thư mục
sprint thì không thấy `.agile.json` nên **không đọc sổ** — kết quả không có phát hiện về sổ chưa phải là sổ khớp.

`check` bắt lệch khi dự án đã khai: sprint đang mở (khác `done`, `dropped`) không có dòng → Phải sửa
(`ledger-missing-row`); dòng lệch `status` hoặc ngày cũ hơn `updated` → Phải sửa (`ledger-stale`); file sổ không có,
không đọc được UTF-8 hay không có bảng cột đầu "Sprint" → Phải sửa (`ledger-unreadable`); dự án khai mà máy chưa đặt
mẫu đường → Ghi chú (`ledger-unconfigured`); mẫu đường thiếu `{project}` → Phải sửa (`config-invalid`).

**Giới hạn đã biết:** `check` so ngày theo ngày — hai lần đổi trạng thái trong cùng một ngày chỉ bắt được qua
trạng thái, không qua ngày; `check` không mở link để thử bấm và không đọc nội dung "kết quả" của dòng, nên người ghi
chịu trách nhiệm link đúng và kết quả có bằng chứng. `init` và `index` chưa tự ghi dòng sổ (việc để lại).
