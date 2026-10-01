---
title: Process — six steps, two human gates
type: method
status: active
updated: 2026-10-01
---

# Quy trình: sáu bước, hai cổng người

> **Kết luận:** mọi sprint đi đúng sáu bước; người dùng chỉ phải quyết ở **hai cổng** (Cổng 1 duyệt
> SPEC + PLAN, Cổng 2 nghiệm thu) và ở **bốn điều kiện dừng**. Mọi điểm còn lại agent tự quyết, ghi
> phán quyết vào PROGRESS và đi tiếp. Sprint = một mục tiêu, không đo theo thời gian.

Thuật ngữ: **sprint** — một lượt làm việc phục vụ đúng một mục tiêu · **cổng** — điểm dừng chờ người
dùng quyết · **vòng** — một lần quay từ kiểm định về thực thi · **điều phối** — vai Analyst khi nó
dẫn sprint · **frontmatter** — khối khoá–giá trị ở đầu file tài liệu, máy đọc được · **subagent** —
agent con được agent chính giao một việc kèm brief riêng · **worktree** — bản chép riêng của repo để
làm một việc mà không đụng bản chính. Mã mục (`TK`, `RF`, `BR`…) theo
[skills/id-convention](../skills/id-convention/SKILL.md); thang mức theo [severity.md](severity.md);
cỡ việc theo [sizing.md](sizing.md). Các skill nhắc tên trong file này (`intake`, `shaping-spec`,
`writing-plan`, `plan-review`, `running-sprint`, `code-review`, `closing-sprint`) đến từ đợt distill
sau — xem `docs/MIGRATION.md`.

## 1. Sơ đồ

| Bước | Tên | Ai làm | Tài liệu ra | Cổng |
|---|---|---|---|---|
| 1 | Tiếp nhận | Analyst | dòng `RQ-` trong REQUESTS | không |
| 2 | SPEC rồi PLAN | Analyst (SPEC), Architect (PLAN), Tech Reviewer (review PLAN từ cỡ vừa) | SPEC, PLAN | **Cổng 1** — duyệt / điều chỉnh |
| 3 | Thực thi | Implementer, QA, (Architect) theo từng `TK` | PROGRESS | cổng điều chỉnh nội bộ (không hỏi người) |
| 4 | Kiểm định | Business Reviewer, Tech Reviewer — **agent khác** người làm | `VR`, `RF` | vòng lặp 3 ↔ 4 |
| 5 | REPORT | Analyst | REPORT | **Cổng 2** — nghiệm thu |
| 6 | Bài học | Analyst (kiêm Distiller) | `LN` + nơi lưu bài học | không |

Bước 3 và 4 lặp cho tới khi không còn phát hiện mức Chặn hay Phải sửa (mục 6).

**Người dùng cần làm gì:** giao yêu cầu bằng lời thường ở Bước 1; trả lời **"duyệt"** hoặc **"điều
chỉnh: <gì>"** ở Cổng 1; kết luận **Đạt / Đạt có điều kiện / Không đạt** ở Cổng 2. Ngoài ra chỉ phải
lên tiếng khi agent dừng ở bốn điều kiện (mục 5), sau vòng 3 (mục 6) hoặc khi cạn hạn mức tier.

## 2. Bước 1 — Tiếp nhận (không cổng)

KHI người dùng giao một yêu cầu THÌ Analyst:

1. Ghi một dòng `RQ-` mới vào sổ REQUESTS: ngày, tóm tắt một câu, trạng thái `mới`.
2. Tách theo mục tiêu: một mục tiêu = một sprint (`SPR-`); yêu cầu chứa nhiều mục tiêu thì tách thành
   nhiều sprint, mỗi sprint vẫn trỏ về cùng `RQ-`.
3. Định cỡ và rủi ro theo [sizing.md](sizing.md). Rủi ro chỉ nâng cỡ, không hạ.
4. Liệt kê giả định dưới nhãn **ASSUMPTION** (mỗi giả định một dòng, nói rõ nếu sai thì đổi gì).
5. Rà **danh mục thiếu ngữ cảnh** (skill `intake`): mục tiêu, người dùng cuối, ràng buộc, định nghĩa
   xong, dữ liệu mẫu, môi trường, phụ thuộc, điều cấm, tiêu chí đo, phạm vi ngoài, tiền lệ. Điểm chưa rõ
   mà **không tự giả định được** thì gom thành `CQ` để hỏi **một lần** ở Cổng 1.
6. Đi thẳng sang bước 2. **Không dừng chờ** người dùng ở bước này.

## 3. Bước 2 — SPEC rồi PLAN, Cổng 1

- Mở sprint: ghi dòng `SPR-` vào sổ SPRINTS (cột Mở, Mục tiêu; cột Đóng để trống) và dựng thư mục
  sprint từ mẫu — công cụ `init` làm. Nếu SPEC mở một **tính năng mới** thì cấp `FS-` và tạo spec sống
  ngay ở bước này (trạng thái `đề xuất`); tính năng có sẵn thì chỉ trỏ `FS-` cũ. Sổ SPECS và spec sống
  chỉ cập nhật **hành vi hiện hành** sau Cổng 2.
- Analyst viết **SPEC** (làm cái gì, cho ai, thế nào là xong): bối cảnh · `US` · `FR` với kịch bản
  KHI… THÌ… · `SC` · ngoài phạm vi · `CQ` (có thể rỗng, ghi rõ "không có"). Cỡ **lớn** có thêm mục
  "Đổi hợp đồng / giao diện": liệt kê API, sự kiện, schema sẽ đổi và mọi bên dùng chúng (skill `shaping-spec`).
- Architect viết **PLAN** (làm thế nào, ai làm, kiểm ra sao): mục tiêu · kiến trúc · ràng buộc chung ·
  trọng tâm review (≤5) · `TK` (vai + tier, đầu vào/ra, cách kiểm, cổng, hoàn tác, trỏ `FR`/`SC`) ·
  `RK` · `DN` · ước lượng (skill `writing-plan`). PLAN ghi **quyết định** (chữ ký, giá trị, assertion),
  không chép code.
- Từ cỡ **vừa**, Tech Reviewer review PLAN một lượt trước khi trình (skill `plan-review`): thách thức phạm
  vi, kiến trúc, phủ test. Phát hiện mức Chặn/Phải sửa thì sửa PLAN trước khi trình.
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

Ngoài hai cổng, bốn điều kiện này, mốc sau vòng 3 và cạn hạn mức tier, **không hỏi**. KHI gặp một trong
bốn trường hợp sau THÌ dừng, ghi `BR` vào bảng Vướng mắc của PROGRESS (vướng gì, loại (a)–(d), đã làm
gì, cần ai, trạng thái) và hỏi người dùng:

| | Điều kiện | Ví dụ |
|---|---|---|
| (a) | Hành động **không đảo ngược** được hoặc phá hủy | xoá dữ liệu, viết lại lịch sử git, xoá nhánh chưa gộp |
| (b) | Chạm **bảo mật hoặc secret** | đọc/ghi file chứa khoá, đổi quyền, tắt kiểm tra xác thực |
| (c) | Tác động **ra ngoài phạm vi / worktree** đã giao | push nhánh chung, gộp vào nhánh chính, deploy, gửi tin, sửa file ngoài dự án |
| (d) | **PLAN hỏng** — giả định sai làm đổi tiêu chí thành công, hoặc mọi đường đi tiếp đều là đoán | thư viện nền không hỗ trợ tính năng cốt lõi |

Ngoài bốn điều này, dừng hỏi là **lỗi quy trình** (đếm được: số lần hỏi ngoài cổng phải bằng 0).
Tương tự, cạn hạn mức model của một tier → dừng phần việc của tier đó, ghi `BR`, báo; **không tự hạ
tier** ([tiers/README.md](../tiers/README.md)).

## 6. Bước 4 — Kiểm định bởi agent khác, vòng lặp

- Kiểm định do **agent khác** người làm: phiên hoặc subagent mới, nhận ngữ cảnh soạn riêng. Một agent
  không bao giờ giữ cùng lúc vai thực thi và vai kiểm định cho cùng một sản phẩm
  ([roles/README.md](../roles/README.md)).
- Business Reviewer kiểm **đáp ứng yêu cầu** (`US`/`FR`/`SC`); Tech Reviewer kiểm **kỹ thuật** (code,
  test, bảo mật, dữ liệu, backend, frontend) và kéo thẻ chuyên đề khi rủi ro cao.
- Mỗi phát hiện là một `RF` mang một mức: Chặn / Phải sửa / Nên sửa / Ghi chú, có bằng chứng
  (`file:dòng` hoặc lệnh + kết quả). Reviewer được trả **0 phát hiện** và **phải** ghi phần mình không
  đánh giá.
- Người làm tiếp nhận review bằng cách **kiểm chứng trước khi sửa**; được phản bác có bằng chứng; cấm
  đồng ý cho có; sửa xong phải chạy lại test (skill `code-review`).

**Vòng.** Còn Chặn hoặc Phải sửa → quay lại bước 3; mỗi lần quay lại là **một vòng**, ghi
`review_round` trong PROGRESS. Nên sửa được **hoãn** và ghi thành `CO`; Ghi chú không chặn.

**Khuyến nghị 3 vòng, không trần cứng.** Vòng 1–3 do cùng người làm sửa. Hết vòng thứ ba mà còn Chặn
hoặc Phải sửa THÌ Analyst **báo người dùng** theo lời báo chuẩn:

```
Sau 3 vòng kiểm định, sprint <SPR-> còn <n> phát hiện mức Chặn/Phải sửa:
- RF<k> (<tên>) — <một dòng vì sao chưa xong>
...
Đề xuất: <làm tiếp với cách khác / đổi tier / thu hẹp phạm vi / dừng và bàn giao phần đã đạt>.
Chọn: (1) làm tiếp — bao nhiêu vòng nữa? (2) dừng & bàn giao — phần còn mở ghi CO.
```

Người dùng chọn **làm tiếp** (ghi số vòng thêm) hoặc **dừng & bàn giao** (sang bước 5, phần còn mở
thành `CO`). Đây là mốc hỏi hợp lệ thứ ba ngoài hai cổng và bốn điều kiện dừng.

## 7. Bước 5 — REPORT và Cổng 2

KHI kiểm định không còn Chặn/Phải sửa, hoặc người dùng chọn dừng, THÌ Analyst viết **REPORT** theo
mẫu: câu đầu là kết luận · tóm tắt cho người không chuyên · kết quả kiểm định (`VR`: Đạt / Không đạt /
Chưa chạy / Không áp dụng + lý do) · phát hiện của reviewer (`RF` + mức + trạng thái xử lý) · rủi ro còn
lại · cách dùng, đã đổi gì, cách hoàn tác · bài học (`LN`) · việc để lại (`CO`) · review & retro (sản
phẩm đã đạt gì ↔ cách làm nên đổi gì) · Cổng 2 · tổng token phiên (mốc đo). REPORT thay cho bàn giao:
không có tài liệu bàn giao riêng.

**Trình Cổng 2** giống Cổng 1: một bản tóm tắt, kết luận trước, mã kèm tên. Lời trình chuẩn:

```
Cổng 2 — sprint <SPR-> (<mục tiêu một câu>), sau <n> vòng kiểm định.
Kết luận: <đạt gì so với SC; reviewer kết luận …>
Kiểm định: <k/m SC có VR Đạt; VR Chưa chạy/Không áp dụng: … (lý do)>
Phát hiện còn mở: <RFk (tên) — mức — xử lý> (hoặc "không")
Việc để lại: <COk (tên) — chủ — mốc> (hoặc "không")
Cách dùng / đã đổi gì / hoàn tác: <một dòng mỗi ý>; REPORT: <đường dẫn>
Anh kết luận: Đạt / Đạt có điều kiện (kèm điều kiện) / Không đạt (kèm lý do)
```

Người dùng kết luận **Đạt / Đạt có điều kiện / Không đạt**:
- *Đạt* → ghi `gate_2: pass` + `gate_2_at` + `gate_2_quote` nguyên văn; cập nhật **spec sống** của tính
  năng trong thư mục spec sống theo cấu hình (`paths.feature_specs_dir`) ngay trong sprint; đóng sprint
  trong SPRINTS; lúc này mới trình menu nhánh (gộp local / push + PR / giữ nguyên — skill
  `closing-sprint`; push và PR là tác động ra ngoài, cần người dùng gật).
- *Đạt có điều kiện* (`conditional_pass`) → như Đạt, điều kiện ghi thành `CO` có chủ và mốc theo dõi.
- *Không đạt* (`fail`) → ghi lý do nguyên văn; mở vòng mới hoặc sprint mới theo người dùng chọn.

## 8. Bước 6 — Bài học

KHI sprint đóng THÌ Analyst (kiêm Distiller) rút bài học `LN`, tự chấm trước khi lưu (skill
`closing-sprint`, phần bài học): bài học có **tái dùng** được không? có tra lại được từ code/git/docs
không (nếu có thì không lưu)? có mâu thuẫn với bài học cũ không (nếu có thì gộp, không đẻ bản trùng)?

- Nơi lưu bài học do **lớp riêng** của môi trường quy định (điểm cắm trong `hosts/`); lõi chỉ quy định
  bài học ghi theo timeline, mỗi bài học một nguồn (sprint nào, bằng chứng nào).
- Bài học đánh dấu **quan trọng** THÌ **chỉ đề xuất** nâng thành luật, skill hoặc bước quy trình, kèm lý
  do và chi phí; người dùng quyết. Agent không tự sửa luật hay tự tạo skill từ bài học.

## 9. Việc rất nhỏ — cổng "đạt theo lời giao"

KHI cỡ **rất nhỏ** (đổi chữ, một dòng, không đổi hành vi) THÌ:
- Bốn tài liệu gộp thành một file `SPRINT.md` có đủ bốn phần.
- **Cổng 1** không mở lượt hỏi mới: khi lời giao của người dùng đã nêu rõ kết quả, ghi
  `gate_1: approved`, `gate_1_at` là thời điểm giao, `gate_1_quote` là **trích nguyên văn** lời giao với
  tiền tố "đạt theo lời giao: …". Lời giao chưa nêu rõ kết quả thì không phải việc rất nhỏ — nâng cỡ.
- **Cổng 2** gộp vào lời báo cuối lượt: câu đầu là kết quả + bằng chứng; người dùng không phản đối trong
  lượt đó là nghiệm thu **ngầm** — ghi trung thực `gate_2: pass`, `gate_2_at`, và
  `gate_2_quote: "nghiệm thu ngầm — không phản đối tới <thời điểm>"`; người dùng lên tiếng thì ghi câu
  nguyên văn thay vào.
- Luật "người làm không tự chấm" vẫn áp: `VR` do agent khác chạy, hoặc ghi rõ "tự kiểm, chưa độc lập"
  và kết luận chỉ được là **Đạt có điều kiện**.

Giữ đủ hai cổng về mặt hồ sơ, không thêm lượt hỏi về mặt con người.

## 10. Khi nào được hỏi người dùng — bảng tra nhanh

| Được hỏi | Không được hỏi (tự quyết + `Phán quyết:`) |
|---|---|
| Cổng 1, Cổng 2 | Chi tiết triển khai PLAN chưa nói |
| Bốn điều kiện dừng (mục 5) | Mâu thuẫn nhỏ SPEC ↔ PLAN còn trong phạm vi |
| Sau vòng 3 còn Chặn/Phải sửa (mục 6) | Chọn thư viện/cách làm tương đương trong ràng buộc đã duyệt |
| Cạn hạn mức tier (không tự hạ tier) | Thứ tự làm `TK`, tách `TK` con |
| `CQ` gom ở Cổng 1 (một lần) | Hỏi lẻ từng câu giữa chừng |
| Tư vấn gọi chéo hãng (chỉ tư vấn, người dùng quyết) | Tự chạy gọi chéo |
