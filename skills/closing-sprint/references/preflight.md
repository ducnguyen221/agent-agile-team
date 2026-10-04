# Tiền kiểm bằng chứng

<!-- Ý khái niệm: một lượt rà hồ sơ sprint trước Cổng 2, độ nghiêm theo bậc việc và rủi ro, tách rõ phần máy
     bắt thật và phần phải đọc tay. Soạn mới lần hai trong SPR-04 (TK10), chỉ dựa trên một danh sách ý ngắn. -->

> **Kết luận:** trước khi trình Cổng 2, rà hồ sơ sprint một lượt để biết bằng chứng đã đủ chưa. Độ nghiêm đổi
> theo **bậc việc** và **rủi ro**. Mỗi dòng của danh mục nói rõ ai kiểm: **máy** chỉ khi `scripts/check.py` có
> luật thật (nêu tên luật), còn lại **tay**. Kết luận dùng thang Đạt / Đạt có điều kiện / Không đạt; còn Chặn
> mở thì Không đạt. Tiền kiểm chuẩn bị cho Cổng 2, không thay Cổng 2.

## 1. Khi nào

Đúng lúc vòng kiểm định hết phát hiện nặng (hoặc người dùng đã chọn dừng và bàn giao) và REPORT có bản nháp
đầu tiên, nhưng **trước** lời trình Cổng 2 ([process.md](../../../method/process.md) mục 7). Việc rất nhỏ: chạy ngay trước lời
báo cuối lượt.

Chạy lại phần bị ảnh hưởng khi một trong ba thứ đổi sau lần chạy trước: commit của mã, spec, hoặc công cụ
([evidence.md](../../../method/evidence.md) mục 3). Sửa chỉ tài liệu thì không phải chạy lại phép kiểm mã.

Tiền kiểm không thay việc của reviewer và không thay lời kết luận của người dùng: nó kiểm hồ sơ, không kiểm lại
sản phẩm.

## 2. Ma trận cổng: bậc việc × rủi ro

Bậc theo [sizing.md](../../../method/sizing.md); rủi ro là `risk: normal` hoặc `risk: high`.

| Bậc | `risk: normal` | `risk: high` |
|---|---|---|
| Rất nhỏ | `SPRINT.md` chia hai phần, Kế hoạch và Kết quả. Người làm được tự chạy phép kiểm nếu khai rõ "tự kiểm, chưa độc lập" — lúc đó trần kết luận là Đạt có điều kiện; phép kiểm do agent khác chạy mới mở đường tới Đạt. Chỉ xét các dòng "mọi bậc" | Không có ô này: rủi ro cao tự động thành cỡ lớn (`frontmatter-value` bắt lệch) |
| Nhỏ | `SPRINT.md` bốn phần. Một reviewer khác người làm, nhưng reviewer ấy xét **cả hai** lăng kính: khớp SPEC (nghiệp vụ) và kỹ thuật ([process.md](../../../method/process.md) mục 9); không chọn một lăng kính. Danh mục: "mọi bậc" và "từ nhỏ" | Không có ô này, như trên |
| Vừa | Bốn tài liệu. Hai reviewer; review PLAN trước Cổng 1 đã ghi. Danh mục thêm các dòng "từ vừa" | Không có ô này, như trên |
| Lớn | Bốn tài liệu cộng thêm theo cỡ: ADR cho quyết định kiến trúc, mục "Đổi hợp đồng / giao diện" trong SPEC, kế hoạch hoàn tác có lệnh. Hai reviewer, mỗi bên có phần không đánh giá. Danh mục đủ mọi dòng | Như ô bên cạnh, **cộng**: mỗi `risk_tags` có thẻ chuyên đề tương ứng đã kiểm; không `VR` nào Chưa chạy; phép kiểm chạy lại trên commit cuối; Phải sửa còn mở là Không đạt; khi `risk_tags` có `rules`, `secret` hoặc `auth` thì có thêm **một reviewer kỹ thuật thứ hai**, độc lập với reviewer kỹ thuật đầu, đã ký ([dual-review.md](../../../roles/verifier/dual-review.md)) |

Hai ô trống không phải kẽ hở để lách: ai gắn `risk: normal` cho việc chạm vùng rủi ro đang hạ cỡ trái luật
(sizing.md mục 2); tiền kiểm gặp thì nâng cỡ và ghi `Phán quyết:`.

## 3. Danh mục kiểm

Cột **Ai kiểm**: "máy" nghĩa là luật có tên trong bảng `RULES` của [check.py](../../../scripts/check.py);
cách chạy là `python scripts/check.py <thư mục sprint>` và đọc lần lượt từng phát hiện. Máy chỉ cho thấy hồ sơ **nhất quán**,
không chứng minh việc thật đã làm; vì vậy nhiều dòng có cả phần máy lẫn phần tay, ghi riêng. Cột **Từ bậc**:
dòng áp dụng từ bậc ấy trở lên.

### 3.1. Phủ và bằng chứng

| # | Kiểm gì | Ai kiểm | Từ bậc |
|---|---|---|---|
| 1 | Mỗi `SC` của SPEC có mặt trong ít nhất một dòng `VR` | máy: `report-sc-without-vr` | mọi bậc |
| 2 | Mỗi `SC` có `VR` kết quả **Đạt**; Chưa chạy và Không áp dụng không tính | tay: máy chỉ thấy có dòng, không đọc cột kết quả | mọi bậc |
| 3 | Với mỗi `FR`, có một `VR` nhắm vào chính nó hoặc vào một kịch bản con của nó (được miễn khi `FR` đã `bỏ`, hay có NOT_APPLICABLE kèm lý do) | máy: `report-fr-without-vr`, luật này chỉ quét REPORT riêng; hồ sơ gộp `SPRINT.md` thì tay | từ nhỏ |
| 4 | Mỗi `TK` trỏ ít nhất một `FR`/`SC`; việc con kế thừa việc cha | máy: `task-without-trace` | mọi bậc |
| 5 | Mã nhắc chéo đều có định nghĩa ở tài liệu sở hữu | máy: `xref-missing`; thiếu `links` thì chỉ ra Ghi chú `xref-unresolved`, đọc tay | mọi bậc |
| 6 | Từng `VR` ghi đủ: lệnh nguyên văn hoặc các bước lặp lại được, giá trị mong đợi so với nhận được, môi trường, mốc commit, người chạy; lệnh phải phủ cả bộ test chứ không chỉ một file | tay | mọi bậc |
| 7 | Bằng chứng còn tươi: từ lúc chạy tới nay không có commit mã, dependency, cấu hình hay spec đổi | tay: so mốc ghi trong `VR` với `git log` | mọi bậc |
| 8 | Nhãn agent trong `roles` không vừa thực thi vừa kiểm định; QA khác implementer và architect, hoặc `VR` ghi "tự kiểm, chưa độc lập" và `verdict` không phải `pass` | máy: `self-review`, `qa-not-independent`, `roles-invalid` | mọi bậc |
| 9 | Nhãn trong `roles` ứng với phiên hay subagent khác thật | tay: đối chiếu cột "Vai · tier · model" của PROGRESS; máy không biết danh tính | mọi bậc |
| 10 | Test hồi quy đã đi vòng gỡ sửa → hỏng → đặt lại → đạt, cả hai kết quả ghi trong `VR` | tay | mọi bậc có sửa lỗi |

### 3.2. Điều cấm

| # | Kiểm gì | Ai kiểm | Từ bậc |
|---|---|---|---|
| 11 | Không test bị skip hay xfail mới; không sửa cấu hình linter hoặc test để qua kiểm | tay: đọc diff của file cấu hình và file test | mọi bậc |
| 12 | Ngưỡng coverage trong `.agile.json` không đổi, hoặc đổi có ghi lý do | máy: `config-invalid` | mọi bậc, khi có `.agile.json` |
| 13 | Số đo coverage thật của code mới và code sửa đạt ngưỡng (mặc định 80 %) | tay: đọc báo cáo coverage | mọi bậc |
| 14 | Diff cả nhánh không chứa secret, khoá, token | tay: đọc diff; việc mang nhãn `secret` thì xem cả thẻ security | mọi bậc |
| 15 | CHANGELOG chỉ có dòng thêm; file version không đổi, **trừ khi** người dùng đã quyết đổi (một `DN` đã được duyệt, hoặc lời duyệt trích nguyên văn) — khớp [conventions.md](../../../method/conventions.md) mục 4.1 | tay: `git diff` của hai file, đối chiếu với `DN` hay lời duyệt | mọi bậc |
| 16 | Không còn nhãn thang mức cũ | máy: `old-scale-label` | mọi bậc |
| 17 | `.agile.json` hợp lệ; `visibility: public` thì `artifact_root` nằm ngoài repo | máy: `config-syntax`, `config-invalid`, `config-public-root` | mọi bậc, khi có `.agile.json` |

### 3.3. Hồ sơ

| # | Kiểm gì | Ai kiểm | Từ bậc |
|---|---|---|---|
| 18 | Frontmatter đủ khoá, giá trị đúng miền, `risk: high` đi cùng `size: large` và `risk_tags` khác rỗng | máy: `frontmatter-key-missing`, `frontmatter-value` | mọi bậc |
| 19 | Cổng đã kết luận thì có thời điểm và câu nguyên văn; `status` không vượt cổng chưa qua. Cổng 1 thật sự `approved` trước khi viết mã | máy: `gate-invalid` cho phần đầu; phần sau tay | mọi bậc |
| 20 | Hồ sơ đủ tiêu đề cấp 2 bắt buộc của loại tài liệu và có khối `> **Kết luận:**` | máy: `heading-missing`, `conclusion-missing` (bộ tiêu đề do `check` quyết, đừng tự đếm) | mọi bậc |
| 21 | Phần cách dùng, đã đổi gì, cách hoàn tác có nội dung thật: ít nhất một dòng nói hoàn tác bằng gì | tay: máy chỉ thấy tiêu đề | mọi bậc |
| 22 | Mỗi `RF` đúng một mức và có bằng chứng; **không còn Chặn mở** | tay | từ nhỏ |
| 23 | Nên sửa chưa sửa đã thành `CO` có chủ và mốc, và cùng lúc một dòng `RQ-` trạng thái `mới` trong REQUESTS, nguồn `từ SPR-xx/COn` | tay | mọi bậc |
| 24 | Bảng mã có câu dẫn; không mã trần một chữ cái | máy: `id-list-lead` (Ghi chú), `id-bare-single-letter` | mọi bậc |
| 25 | Retro đã đọc lại hết các dòng `Phán quyết:` của nhật ký PROGRESS và nêu phán quyết nào sai hoặc tốn hơn dự kiến | tay | từ nhỏ |
| 26 | Review PLAN trước Cổng 1 đã ghi ở REPORT, kèm phần không đánh giá | tay | từ vừa |
| 27 | Mỗi reviewer có mục "không đánh giá"; mỗi thẻ chuyên đề kéo theo `risk_tags` có `RF` hoặc mục "không đánh giá" riêng (bậc thấp hơn reviewer vẫn phải ghi, tiền kiểm chỉ chặn từ lớn) | tay | lớn |
| 28 | Kế hoạch hoàn tác viết bằng **lệnh thật**, thứ tự rõ, nêu giới hạn (dữ liệu đã ghi thì sao); có ADR cho quyết định kiến trúc; SPEC có mục "Đổi hợp đồng / giao diện" khi đổi hợp đồng (`check` chưa kiểm hai mục sau) | tay | lớn |
| 29 | Việc chạm dữ liệu (`data_migration`) có báo cáo diễn tập thành `VR` | tay | lớn, khi có migration |

## 4. Kết luận tiền kiểm

Chọn kết luận **nặng nhất** trong các điều kiện đang đúng.

| Kết luận | Khi nào |
|---|---|
| **Đạt** | Mọi dòng áp dụng cho bậc đã đạt; 0 Chặn và 0 Phải sửa còn mở; mọi `SC` có `VR` Đạt do agent khác chạy trên commit hiện tại |
| **Đạt có điều kiện** | 0 Chặn; còn Nên sửa nhưng đã hoãn thành `CO` có chủ, mốc và dòng `RQ-`; hoặc việc rất nhỏ chỉ tự kiểm; hoặc một Phải sửa mà người dùng đã chấp nhận ghi rõ trong chat (trích nguyên văn) |
| **Không đạt** | Còn Chặn mở (**luôn**, không ngoại lệ); hoặc `SC` không có `VR` Đạt (kể cả Chưa chạy); hoặc Phải sửa còn mở mà người dùng chưa chấp nhận; hoặc bằng chứng hết hạn chưa chạy lại; ở `risk: high`, thêm các điều trong ô lớn của mục 2 chưa đủ |

Máy báo Đạt (thoát 0) **không** có nghĩa tiền kiểm Đạt: các dòng tay vẫn phải đạt. Ngược lại, máy báo Phải sửa
hay Chặn là đã đủ để kết luận Không đạt, không cần xét tiếp dòng khác.

Không đạt thì không trình Cổng 2: quay về bước thực thi, ghi một vòng, hoặc nếu người dùng đã chọn dừng thì ghi
phần còn mở thành `CO` rồi tiền kiểm lại.

## 5. Ghi kết luận ở đâu

Ba chỗ, theo mẫu trong [templates/](../../../templates/README.md):

- Khoá `verdict` ở frontmatter của REPORT (với việc gộp: của `SPRINT.md`) — khoá này vốn là kết luận của vòng
  kiểm định cuối, đúng việc tiền kiểm. `pass` ↔ Đạt, `conditional_pass` ↔ Đạt có điều kiện, `fail` ↔ Không đạt.
  `check` kiểm giá trị và chặn `pass` khi `VR` khai tự kiểm. **Không** đụng các khoá `gate_2`: đó là lời của người
  dùng.
- Một dòng đầu mục "Kết quả kiểm định" của REPORT: `Tiền kiểm: <kết luận> · mốc <commit> · <ngày> · <vai và
  agent chạy> · <n> dòng máy, <m> dòng tay`, kèm dòng nào còn thiếu nếu không phải Đạt. Output đầy đủ của `check`
  lưu ra file tạm của sprint và trỏ đường dẫn, không dán cả.
- Khối `> **Kết luận:**` của REPORT nhắc lại kết quả bằng một câu cho người duyệt, và lời trình Cổng 2 lấy từ đó.

Lý do chọn REPORT thay vì một file riêng: người duyệt Cổng 2 đã mở REPORT; thêm file là thêm chỗ lệch. Một dòng
chỉ-thêm trong nhật ký PROGRESS lúc chạy tiền kiểm cũng được, để lại dấu vết thời điểm.

## 6. Không làm

- Tích dòng tay mà chưa mở bằng chứng ra xem. Dòng chưa xem thì ghi "chưa xem", không ghi đạt.
- Dùng Không áp dụng để né phép kiểm khó; giới hạn công cụ là Chưa chạy kèm giới hạn
  ([evidence.md](../../../method/evidence.md) mục 2).
- Sửa cấu hình linter, test hay ngưỡng coverage cho `check` hoặc test qua.
- Hạ bậc việc hay gỡ nhãn `risk_tags` để được danh mục nhẹ hơn; hạ cỡ chỉ ở Cổng 1 do người dùng quyết.
- Tự ghi `gate_2` hoặc tự tăng version; hai việc đó thuộc người dùng.
