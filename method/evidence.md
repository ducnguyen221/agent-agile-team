---
title: Evidence — what counts, how fresh, done is not released
type: method
status: active
updated: 2026-10-01
---

# Bằng chứng: cái gì được tính, tươi tới đâu, xong ≠ phát hành ≠ nghiệm thu

> **Kết luận:** không có bằng chứng **mới chạy** thì không có kết luận Đạt. Bằng chứng là lệnh + kết
> quả thật hoặc `file:dòng`, do **agent khác** người làm ghi, gắn với đúng mốc code và spec đang kiểm.
> "Chưa chạy", "Không áp dụng", "chắc là chạy được" không bao giờ là Đạt.

## 1. Một `VR` gồm gì

Mỗi kết quả kiểm (`VR`) trong REPORT (và dòng bằng chứng trong PROGRESS) ghi đủ:

| Trường | Nội dung |
|---|---|
| Trỏ tới | `FR`/`SC` được kiểm (một `VR` có thể phục vụ nhiều mục; mỗi kịch bản `FR` cần ít nhất một `VR`) |
| Cách kiểm | lệnh nguyên văn, hoặc các bước tái hiện bằng tay (ai cũng lặp lại được) |
| Môi trường | hệ điều hành, phiên bản công cụ/runtime, nhánh + commit đang kiểm, working tree sạch hay bẩn |
| Thời điểm | ngày giờ chạy |
| Kỳ vọng ↔ thực tế | giá trị mong đợi và giá trị nhận được (số, mã thoát, dòng output then chốt) |
| Kết quả | **Đạt · Không đạt · Chưa chạy · Không áp dụng** (+ lý do cho hai mức sau) |
| Người chạy | vai + agent (tier, model) — phải khác người làm |
| Giới hạn | phần không kiểm được, giả định khi kiểm |

Output dài lưu ra file (thư mục tạm của sprint) và trỏ đường dẫn; trong tài liệu chỉ giữ dòng then chốt.

## 2. Bốn kết quả — và cái không phải Đạt

| Kết quả | Khi nào | Lưu ý |
|---|---|---|
| Đạt | kết quả thực tế khớp kỳ vọng, chạy trên đúng mốc code | — |
| Không đạt | không khớp, hoặc lệnh lỗi | ghi đủ output lỗi, không cắt |
| Chưa chạy | chưa có điều kiện (thiếu môi trường, thiếu bảng tier, chưa tới lượt) | **không** tính là Đạt; Cổng 2 không được Đạt nếu `SC` bắt buộc còn Chưa chạy |
| Không áp dụng | phép kiểm không có nghĩa với thay đổi này | phải có lý do và người xác nhận (reviewer); **không** tính là Đạt; không dùng để né phép kiểm khó |

Giới hạn năng lực công cụ ("không chạy được trình duyệt trong môi trường này") là **Chưa chạy** kèm
giới hạn, không phải Không áp dụng.

## 3. Độ tươi

- Bằng chứng gắn với **mốc**: commit, spec revision, phiên bản toolchain. Một trong ba đổi → bằng chứng
  cũ **hết hạn** cho mục bị ảnh hưởng; phải chạy lại trước khi tái dùng kết luận.
- Reviewer được phép **không chạy lại** phép kiểm không liên quan tới thay đổi mới, nếu ghi rõ căn cứ
  phạm vi ("đổi chỉ chạm module X; `VR3` của module Y giữ nguyên từ commit abc123").
- Working tree bẩn: ghi rõ và kèm tóm tắt diff chưa commit; không ghi mỗi `HEAD` để che phần chưa commit.
- Sửa chỉ tài liệu/bằng chứng không làm hết hạn bằng chứng của code. Sửa source, dependency, cấu hình
  ảnh hưởng runtime luôn làm hết hạn các phép kiểm liên quan.

## 4. Test hồi quy phải đi vòng "gỡ sửa → hỏng"

Một test được gọi là bắt lỗi hồi quy chỉ khi đã chứng minh: **gỡ bản sửa → test hỏng → đặt lại bản sửa
→ test đạt**. Test chưa từng hỏng không chứng minh gì. Ghi cả hai kết quả vào `VR`.

Cùng tinh thần cho test mới của tính năng mới: test viết trước phải hỏng vì đúng lý do (chưa có tính
năng), không hỏng vì lỗi cú pháp (skill `tdd`).

## 5. Câu "đỏ" — thấy là chưa có bằng chứng

- "Chắc chạy được", "should work", "về lý thuyết là đúng".
- "Đã sửa" / "đã test" **không kèm** lệnh và output.
- "Test xanh" nhưng chỉ chạy một file, không chạy **cả bộ**.
- "Build ok" từ lần chạy trước khi sửa thêm.
- Kết quả do chính người làm ghi, dán vào `VR` mà không có agent khác chạy lại.

Gặp câu đỏ trong tài liệu, reviewer gán ít nhất **Phải sửa**; trong `VR` thì kết quả đổi về Chưa chạy.

## 6. Xong ≠ phát hành ≠ nghiệm thu

Bốn trạng thái khác nhau, không suy từ nhau:

| Trạng thái | Nghĩa | Ai/cái gì xác nhận |
|---|---|---|
| **Xong** (`TK` Đạt) | việc làm xong, có bằng chứng | `VR` do agent khác |
| **Kiểm định xong** | 0 Chặn/Phải sửa còn mở | reviewer |
| **Nghiệm thu** (Cổng 2) | người dùng kết luận Đạt / Đạt có điều kiện | người dùng, câu nguyên văn trong `gate_2` |
| **Phát hành** | đã lên môi trường thật và được kiểm ở đó | `VR` chạy trên môi trường thật, sau Cổng 2 |

Sprint đóng ở nghiệm thu; phát hành là việc riêng (menu nhánh sau Cổng 2, tác động ra ngoài → người dùng
gật). Archive hồ sơ không có nghĩa đã kiểm trên production.

## 7. Bằng chứng của reviewer

- Mỗi `RF` có `file:dòng` hoặc lệnh + kết quả. Không có → mức tối đa Ghi chú.
- Reviewer ghi rõ **phần không đánh giá** ("không xem phần frontend", "không chạy test E2E vì thiếu
  trình duyệt") — bắt buộc, kể cả khi 0 phát hiện.
- Reviewer **không sửa code**; đề xuất cách sửa được, nhưng việc sửa và chạy lại test là của người làm.
- Trường `roles` trong frontmatter ghi ai làm, ai kiểm; công cụ kiểm so hai danh sách đó. Công cụ chỉ chứng
  minh hồ sơ **nhất quán**, không chứng minh danh tính — trách nhiệm điều phối là giao kiểm định cho agent
  khác thật.
- `VR` do QA chạy chỉ tính là độc lập khi nhãn `qa` khác nhãn `implementer`/`architect` của cùng sản
  phẩm. Trùng nhãn → mỗi `VR` ghi "tự kiểm, chưa độc lập"; kết luận của sprint tối đa **Đạt có điều
  kiện** cho tới khi agent khác chạy lại.

## 8. Cổng giao hàng — kiểm cơ học trước khi trình Cổng 2

Review (agent khác đọc, chấm) và **cổng giao hàng** là hai lớp khác nhau, chồng lên nhau. Review chấm chất lượng nội
dung — đúng, đủ, trung thực. Cổng giao hàng chỉ kiểm **sự thật máy kiểm được**: lệnh chạy ra mã thoát nào, hồ sơ có
nhất quán không, một câu "né" có xuất hiện không. Không suy luận, không đoán ý. Giống cổng của hệ CI: không tin lời
tự báo, chỉ tin thứ đo được. Cổng này là **luật văn bản**, không cần hook hay thành phần chạy nền nào.

KHI sắp trình Cổng 2 (và trước khi đánh dấu một `TK` là xong) THÌ người điều phối (hoặc QA) chạy đủ năm kiểm sau, ghi
kết quả vào PROGRESS. Năm kiểm này **chính là** bước "Chạy" của vòng kiểm sáu pha mỗi `TK`
([loop.md](../skills/verify-before-done/references/loop.md)), không phải vòng thứ hai:

| Kiểm | Cách kiểm cơ học | Trúng thì |
|---|---|---|
| Lệnh kiểm của dự án | build, test cả bộ, lint, kiểm kiểu vừa chạy **trên đúng mốc đang giao**; mã thoát 0 (vòng gỡ sửa → hỏng của mục 4 cho test hồi quy) | **Chặn** — chưa trình Cổng 2 |
| Hồ sơ nhất quán | `scripts/check.py` trên thư mục sprint (và `--self` nếu sửa chính repo phương pháp): Đạt | **Chặn** nếu có mức Chặn/Phải sửa; Nên sửa → ghi `CO` |
| Mốc còn tươi | commit, spec và toolchain hiện tại bằng mốc ghi trong `VR` (mục 3); working tree sạch hoặc diff chưa commit đã ghi | `VR` hết hạn → **Chưa chạy**, chạy lại |
| Tài nguyên đủ để kiểm | đĩa, bộ nhớ, hạn mức công cụ đủ chạy phép kiểm; không đủ thì phép kiểm không chạy được | `VR` là **Chưa chạy** kèm giới hạn (mục 2), không phải Đạt |
| Câu né (xem dưới) | tìm theo mẫu chữ trong báo cáo và PROGRESS | người đọc gán **một** mức (Ghi chú hoặc Phải sửa) theo ngữ cảnh; chỉ cảnh báo, không tự chặn |

**Ca hỏng có sẵn ở gốc.** Lệnh kiểm đỏ mà ca hỏng được **chứng minh** có từ gốc (chạy đúng ca đó ở gốc, như
`closing-sprint` mục 2 bước 4) thì không phải Chặn của sprint này: ghi `CO` kèm dòng `RQ-`, người dùng quyết ở Cổng 2
có đóng không. "Lỗi có từ trước" nói miệng, không có lần chạy ở gốc, vẫn là câu né (dưới).

**Câu né** là dấu hiệu việc kiểm bị cắt ngắn: "bỏ qua test lần này", "lỗi có từ trước", "để sau", "chắc chạy được", "chỉ
là cảnh báo", "test chậm nên tắt". Tìm bằng mẫu chữ nên **có thể báo nhầm** — nhầm thì reviewer đọc ngữ cảnh và bỏ
cảnh báo; cổng này **không bao giờ tự chặn chỉ vì câu né**. Còn câu né mà đúng là một phép kiểm bị bỏ thì xử như câu "đỏ"
ở mục 5.

**Giới hạn.** Cổng cơ học chứng minh hồ sơ **nhất quán** và lệnh **đã chạy**, không chứng minh nội dung **đúng**.
Mọi `VR` vẫn cần agent khác chạy (mục 7); cổng giao hàng không thay review, và review không thay cổng — cái này bắt thói
quen cắt ngắn, cái kia bắt lỗi nghĩa. Hai lớp chồng nhau mới thành phòng thủ nhiều tầng.
