---
name: bug-triage
description: Use when a bug report, stack trace, error log or "this is broken" message arrives and someone must decide how serious it is and where it goes (hotfix, current sprint, next sprint, backlog), or when a reporter pushes a priority label from another tracker, demands a quick fix before anyone has reproduced the problem, or wants every bug marked blocking.
metadata:
  group: process
  roles: [analyst]
source: "concept: bug triage - reproduce first, grade by consequence, route by grade (rewritten from an idea list that kept some source wording; must be genuinely rewritten before public, see CO2 and RQ-021 in the owner private record)"
source_sha: null
license: none
rewrite_before_public: false
---

# Phân loại lỗi

> **Kết luận:** **tái hiện trước, xếp mức sau**. Mức đo **hậu quả nếu bỏ qua**, không đo công sửa; phân
> vân giữa hai mức thì chọn mức nặng hơn và ghi một câu vì sao. Mức quyết đường đi: Chặn → sửa nóng ngay ·
> Phải sửa → sprint này hoặc sprint kế · Nên sửa → sprint sau · Ghi chú → backlog. Mỗi lỗi là **đúng một**
> dòng `RQ-`, luôn có ô test hồi quy dự kiến. Nhãn ưu tiên của hệ khác chỉ được trích, không thay mức.

## 1. Khi nào

| Tình huống | Làm gì |
|---|---|
| Có báo cáo lỗi, stack trace, log lỗi, hay hành vi lệch so với spec sống / tài liệu dùng | skill này |
| Câu hỏi "lỗi này nặng không, ai xử lý, khi nào" | skill này |
| Hàng chờ nhiều lỗi cần xếp thứ tự | skill này, mỗi lỗi một dòng |
| Câu hỏi "vì sao nó hỏng" — cần nguyên nhân gốc | skill `debugging` trước; quay lại đây khi cần mức và đường |
| "Lỗi" là hành vi chưa từng được hứa (tính năng mới đội lốt lỗi) | skill `intake` — yêu cầu mới, không gán mức lỗi |
| Lỗi đã có dòng `RQ-` đang mở | cập nhật dòng đó (bằng chứng mới, mức nếu đổi); không mở mã thứ hai |

Phép thử "lỗi hay tính năng": so với spec sống `FS-`, `SC` đã nghiệm thu và tài liệu dùng. Hành vi chưa từng
được mô tả ở đâu thì không phải lỗi, dù người báo gọi là lỗi. Mở mã trùng cho cùng một lỗi tách đôi lịch sử
và dễ sinh hai bản sửa đá nhau.

## 2. Các bước

1. **Tái hiện.** Ghi các bước, môi trường, mong đợi ↔ thực tế; log dài lưu file và trỏ đường dẫn. Thiếu dữ
   liệu → gom mọi thứ thiếu (bước làm, thời điểm, mã đối tượng, môi trường, ảnh/log) vào **một** lượt hỏi
   người báo. Không liên lạc được → vẫn ghi `RQ-` trạng thái `mới` kèm "chưa tái hiện — thiếu <gì>".
   **Không sửa theo phỏng đoán:** bản vá chưa tái hiện có thể đổi một lỗi ồn ào thành dữ liệu sai lặng lẽ.
2. **Xếp mức và đường** theo bảng dưới, dựa trên dấu hiệu đã thấy (lúc tái hiện, hoặc trong log/báo cáo
   khi chưa tái hiện được — khi đó ghi "mức tạm" và xét lại sau tái hiện).

   | Dấu hiệu (một là đủ) | Mức | Đường xử lý |
   |---|---|---|
   | Dịch vụ ngừng; luồng chính không ai dùng được; dữ liệu mất, hỏng hoặc lộ; tiền, thanh toán, hoá đơn sai hoặc không xuất được | Chặn | **Sửa nóng ngay** — mở sprint riêng, không chờ sprint đang chạy |
   | Phần lớn người dùng không đi hết được một luồng quan trọng, và cũng không có cách làm khác | Phải sửa | Sprint hiện tại nếu lỗi nằm trong phạm vi đã duyệt ở Cổng 1; ngoài phạm vi → mở sprint kế |
   | Chức năng phụ hỏng, hoặc chức năng chính hỏng nhưng có đường vòng dùng được | Nên sửa | Sprint sau |
   | Thẩm mỹ thuần (lệch bố cục, màu, chữ — trừ khi che mất hay chặn thao tác thì xếp theo hàng chức năng ở trên), ca biên hiếm không làm sai dữ liệu | Ghi chú | Backlog: dòng `RQ-` mới, chưa gán sprint |

   Sửa nóng nghĩa là **làm ngay**, không phải bỏ cổng: cỡ vẫn định theo `method/sizing.md` (chạm dữ liệu,
   xác thực, thanh toán thì nâng cỡ và rủi ro), Cổng 1 vẫn có (rất nhỏ: "đạt theo lời giao").
3. **Giữ thang có nghĩa.** Gán Chặn cho mọi lỗi làm thang vô dụng: không còn cách nói cái gì phải làm trước.
   Hạ mức khi bằng chứng cho phép (có đường vòng, ít người dính, không chạm dữ liệu hay tiền) và ghi bằng
   chứng đó vào dòng `RQ-`. Lời người báo ("đã hứa với khách", "sếp bảo gấp") là áp lực, không phải bằng
   chứng. Nhãn của hệ khác (`P0`, `S1`, `critical`) chỉ để hiểu ý người báo — tra `method/severity.md` mục 4,
   trích trong dấu code; mức chính thức vẫn xếp theo bảng trên.
4. **Ghi sổ.** Một dòng `RQ-` trong REQUESTS (mã lấy từ `next_id`, ngày ISO, trạng thái `mới`); cột Tóm tắt
   theo công thức:

   ```text
   Lỗi: <hiện tượng một câu> — mức <mức>[ tạm] — tái hiện: <có, cách | chưa, thiếu gì> (log: <đường>)
   — vùng nghi: <module/file> — đường: <sửa nóng | SPR-xx | sprint sau | backlog> — hồi quy: <phép kiểm dự kiến, tầng>
   ```

   Ô **hồi quy** bắt buộc ở mọi mức, ghi ngay lúc phân loại, không "viết khi bắt đầu sprint": lỗi hiệu năng
   ghi phép đo có ngưỡng; lỗi thẩm mỹ ghi kịch bản kiểm tay hoặc so ảnh. Lỗi lộ ra **một lớp** rủi ro (cùng
   kiểu sai ở nhiều chỗ) → sprint sửa ghi thêm `RK` trong PLAN.
5. **Bàn giao cho sprint sửa.** Sprint sửa đi `debugging` (nguyên nhân gốc) rồi `tdd` (test hồi quy viết
   trước, phải hỏng đúng lý do). `VR` của test hồi quy ghi đủ vòng **gỡ bản sửa → hỏng → đặt lại → đạt**
   (`method/evidence.md` mục 4); test chưa từng hỏng không chứng minh lỗi đã hết.

**Lý lẽ ↔ sự thật**

| Lý lẽ | Sự thật |
|---|---|
| "Người báo nói `P0` rồi, cứ ghi theo" | nhãn ngoài chỉ được trích; mức xếp theo dấu hiệu và hậu quả |
| "Sửa nhanh cho kịp giờ deploy, tái hiện sau" | bản vá đoán mò có thể che lỗi thành sai lặng; ghi `RQ-` + một lượt hỏi |
| "Chưa tái hiện nên chưa đủ căn cứ xếp Chặn" | dấu hiệu chạm tiền/dữ liệu là đủ cho mức tạm; phân vân → mức nặng hơn |
| "Lỗi thẩm mỹ nhưng ghi Nên sửa cho chắc" | thẩm mỹ thuần là Ghi chú; nâng mức không lý do cũng làm hỏng thang |
| "Test hồi quy tính sau" | ô hồi quy trống thì sprint sửa không biết "xong" trông ra sao |

## 3. Điểm dừng

| Gặp | Làm |
|---|---|
| Nghi lộ dữ liệu cá nhân, lỗ hổng bảo mật, secret trong log | điều kiện dừng (b): ghi `BR`, báo người dùng ngay, kéo skill `security-review`; không xếp hàng chờ sprint, không ghi cách khai thác vào chỗ người ngoài đọc được |
| Sửa nóng phải đẩy thẳng lên nhánh chung hay môi trường thật | điều kiện (c): chỉ làm khi người dùng gật |
| Sửa cần xoá hoặc ghi đè dữ liệu thật | điều kiện (a) |
| Lỗi cho thấy giả định nền của sprint đang chạy sai, làm đổi `SC` | điều kiện (d): `BR`, báo Analyst điều phối |

Thiếu thông tin tái hiện **không** phải điều kiện dừng: ghi `RQ-` + một lượt câu hỏi rồi đi tiếp.

## 4. Đầu ra

Báo kết quả phân loại bằng khối bốn dòng dưới đây; log để ở file, trong khối chỉ ghi đường dẫn tới nó:

```text
Phân loại RQ-NNN: <mức>[ tạm] — <đường xử lý>
Tái hiện: <đã — cách | chưa — thiếu gì, đã hỏi ai>
Hồi quy: <phép kiểm dự kiến, tầng>
Cần quyết: <điều người dùng phải quyết | không>
```

Nhiều lỗi cùng lượt: một khối mỗi lỗi, xếp theo mức từ nặng tới nhẹ.
