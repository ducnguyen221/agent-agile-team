# Review theo việc và re-review phạm vi hẹp — khuôn brief

<!-- Nguồn: obra/superpowers skills/subagent-driven-development/task-reviewer-prompt.md,
     re-review-prompt.md @ 8ca22db (MIT). Viết lại: thang chung Chặn / Phải sửa / Nên sửa / Ghi chú;
     kết luận Đạt / Không đạt; "⚠️ cannot verify" → "Không kiểm được từ diff". -->

> **Kết luận:** review theo việc là **cổng của một `TK`**, không phải review gộp nhánh: reviewer (agent
> khác) đọc **một** gói diff, trả **hai phán quyết** — khớp SPEC (Đạt / Không đạt) và chất lượng
> (danh sách `RF` theo thang chung) — mỗi phát hiện có `file:dòng`. Re-review sau vòng sửa chỉ phán từng
> phát hiện *đã xử lý / chưa* và bắt lỗi mới trong diff sửa.

## 1. Đầu vào reviewer nhận

| Thứ | Từ đâu |
|---|---|
| Brief của `TK` (cùng file Implementer đã dùng) | Analyst |
| File báo cáo của Implementer | `.tmp/TKn-report.md` |
| Gói diff: commit list + stat + `git diff -U10 BASE..HEAD` | `.tmp/review-<base7>..<head7>.diff` — BASE là mốc ghi trước khi giao, không `HEAD~1` |
| Ràng buộc chung bó `TK` này | chép **nguyên văn** từ PLAN/SPEC: giá trị, định dạng, quan hệ ("cùng bố cục với X") — không phải luật quy trình (đã có trong khuôn) |

## 2. Khuôn brief review theo việc — chép, điền chỗ `< >`

```
Bạn review MỘT việc: trước là nó có khớp yêu cầu không, sau là nó có được làm tốt không. Đây là
cổng của riêng việc này; review toàn nhánh làm riêng sau khi mọi việc xong.

## Yêu cầu
Đọc brief: <đường dẫn brief>. Ràng buộc chung bó việc này: <chép nguyên văn>.

## Implementer nói đã làm gì
Đọc báo cáo: <file báo cáo>. Coi nó là LỜI KHAI chưa kiểm — có thể thiếu, sai, lạc quan. Đối chiếu
với diff. Lý do thiết kế trong báo cáo ("để vậy vì YAGNI") cũng là lời khai: không hạ mức một phát
hiện vì có lý do kèm theo.

## Diff
BASE <sha> · HEAD <sha> · gói: <file diff>. Đọc file này MỘT lần: nó có commit, stat và diff kèm ngữ
cảnh — đó là góc nhìn của bạn. Không chạy lại lệnh git; không mở file đã đổi riêng trừ khi một hunk
bị cắt giữa hàm (và nói rõ). Không đi dạo codebase: chỉ xem ngoài diff để kiểm một rủi ro cụ thể
bạn gọi tên được (đổi thứ tự khoá, đổi hợp đồng hàm, state chia sẻ → kiểm nơi gọi là đúng), một
lần kiểm mỗi rủi ro, ghi cả rủi ro lẫn thứ đã kiểm. Review chỉ-đọc: không đụng working tree, index,
HEAD, nhánh.

## Bạn không giao subagent
Tự review toàn bộ. Không mở subagent review một phần, không mở reviewer thứ hai. Diff quá to cho một
lượt → tự review nhiều lượt và nói rõ.

## Test
Implementer đã chạy test và ghi bằng chứng RED/GREEN cho đúng code này. Không chạy lại cả bộ để xác
nhận. Chỉ chạy một test TẬP TRUNG khi đọc code nảy ra nghi ngờ cụ thể mà không lần chạy nào đã trả
lời; không chạy cả gói, race detector, vòng lặp nhiều lần — thấy cần thì đề xuất trong báo cáo. Không
chạy được lệnh → ghi tên test bạn sẽ chạy. Cảnh báo hay nhiễu trong output test là phát hiện.
Bằng chứng không thấy ≠ không tồn tại: báo cáo có vẻ cụt → đọc lại đúng đường dẫn; thật sự thiếu →
ghi là lỗ hổng cho điều phối. Chạy lại bộ test để "tái tạo" thứ bạn chưa đọc không phải kiểm chứng.

## Phần 1 — Khớp SPEC
So diff với yêu cầu: THIẾU (bỏ qua, khai mà không làm) · THỪA (không ai yêu cầu, over-engineering)
· HIỂU SAI (đúng tính năng, sai cách; giải sai bài). Brief liệt kê nhiều file (việc gộp) → kiểm từng
file: file có trong danh sách mà diff không chạm là THIẾU, dù phần còn lại sạch. Yêu cầu không kiểm
được chỉ từ diff (nằm ở code không đổi, hay trải nhiều việc) → ghi vào "Không kiểm được từ diff",
không mở rộng tìm kiếm.

## Phần 2 — Chất lượng
Code: tách trách nhiệm? xử lý lỗi? DRY không trừu tượng sớm? biên? · Test: test mới/đổi kiểm hành
vi thật, không kiểm mock? biên của việc này có phủ? · Cấu trúc: mỗi file một trách nhiệm, giao diện
rõ? theo cấu trúc file của PLAN? việc này có tạo file đã to, hay làm file có sẵn phình đáng kể? (không
bắt cỡ file có từ trước).
Mọi phát hiện và mọi câu "có" trần đều kèm file:dòng.

## Mức — thang chung
Chặn: sai yêu cầu, mất dữ liệu, lỗ hổng bảo mật, test hỏng, không build, vi phạm điều cấm.
Phải sửa: việc này chưa tin được tới khi sửa — hành vi sai/mong manh, thiếu yêu cầu, hại bảo trì đáng
chặn merge (chép nguyên khối logic, nuốt lỗi, test không assert gì).
Nên sửa: "coverage có thể rộng hơn", đánh bóng. Ghi chú: quan sát.
Phân vân hai mức → mức nặng hơn, nói vì sao. Không bằng chứng → tối đa Ghi chú.
PLAN hay brief BẮT làm thứ thang này gọi là lỗi (test không assert, chép nguyên khối) → vẫn là phát
hiện, mức Phải sửa, gắn nhãn "PLAN bắt buộc" — tác giả PLAN không tự chấm việc của mình, điều phối
phân xử. Ghi điểm làm tốt trước khi liệt kê lỗi — khen đúng chỗ giúp Implementer tin phần còn lại.

## Trả về — câu đầu là phán quyết khớp SPEC, không mở đầu, không kể quá trình, không tóm tắt cuối
### Khớp SPEC: Đạt | Không đạt — <thiếu/thừa/hiểu sai, file:dòng>
### Không kiểm được từ diff: <yêu cầu + điều phối cần kiểm gì> (hoặc "không")
### Điểm tốt: <cụ thể>
### Phát hiện
| RF | Mức | file:dòng | Sai gì | Vì sao quan trọng | Cách sửa (nếu không hiển nhiên) |
### Không đánh giá: <phần không xem, vì sao> (bắt buộc, kể cả 0 phát hiện)
### Chất lượng: Đạt | Cần sửa — <1–2 câu kỹ thuật>
```

## 3. Khuôn brief re-review phạm vi hẹp

```
Bạn re-review MỘT vòng sửa. Review trước trả các phát hiện dưới; Implementer đã thử sửa. Việc của bạn:
phán từng phát hiện và soi diff sửa — không gì khác. Review đầy đủ đã làm rồi.

Brief việc: <đường dẫn>. Phát hiện đang kiểm (nguyên văn, mỗi dòng một):
<danh sách Chặn / Phải sửa / lỗ hổng SPEC của review trước>
Báo cáo Implementer (báo cáo sửa nối ở cuối): <file>. Mốc sửa <sha mà review trước thấy> · HEAD <sha>
· gói diff sửa: <file>. Đọc một lần; không chạy lại git; chỉ-đọc; không giao subagent.

Phạm vi: danh sách phát hiện + diff sửa. Phán mọi phát hiện. Soi diff sửa tìm lỗi mới do chính bản sửa
gây ra. KHÔNG review lại code bản sửa không chạm: thấy vấn đề hoàn toàn ngoài diff sửa → ghi "Quan sát
ngoài phạm vi", không chặn việc này, không kéo dài vòng.
Test: Implementer đã chạy lại test phủ chỗ sửa và nối kết quả vào báo cáo. Coi là lời khai: kiểm báo
cáo sửa có nêu test phủ và output; đối chiếu diff. Không chạy lại cả bộ.

Trả về — câu đầu là phán quyết của phát hiện đầu tiên:
### Từng phát hiện (theo thứ tự): <một dòng> — ĐÃ XỬ LÝ | CHƯA, file:dòng. "Đã cố" không phải đã xử
lý: lỗi cụ thể phải không còn.
### Lỗi mới trong diff sửa: <mức + file:dòng> hoặc "không"
### Quan sát ngoài phạm vi: <không chặn; điều phối ghi sổ cho review toàn nhánh> hoặc "không"
### Kết luận vòng: mọi phát hiện đã xử lý, không Chặn/Phải sửa mới | còn mở — <liệt kê>
```

## 4. Analyst xử lý kết quả

| Reviewer trả | Analyst làm |
|---|---|
| Khớp SPEC Đạt + chất lượng Đạt (có thể kèm Nên sửa/Ghi chú) | `TK` Đạt; Nên sửa → nhật ký `Nên sửa hoãn` → `CO` |
| Không đạt, hoặc Chặn/Phải sửa | vòng sửa (SKILL.md mục 4.4) |
| "Không kiểm được từ diff" | Analyst tự kiểm bằng ngữ cảnh liên-`TK`; thật → vào vòng sửa |
| Phát hiện gắn "PLAN bắt buộc" | phán quyết theo SPEC trước khi sửa hay gác |
| Re-review: lỗi mới Chặn/Phải sửa trong diff sửa | nhập vào danh sách còn mở của vòng kế |
| Re-review: quan sát ngoài phạm vi | nhật ký; review toàn nhánh soát |
