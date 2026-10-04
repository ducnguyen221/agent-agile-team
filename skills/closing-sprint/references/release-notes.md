# Ghi chú phát hành

<!-- Ý khái niệm: ghi chú phát hành tổng hợp từ hồ sơ sprint, hai bản nội bộ / bên ngoài. Viết lại phòng sạch ở
     SPR-04 (TK10) từ danh sách ý cụm danh từ. -->

> **Kết luận:** ghi chú phát hành được **tổng hợp** từ hồ sơ đã có sau Cổng 2 — REPORT, CHANGELOG, PROGRESS, spec
> sống — chứ không viết từ trí nhớ. Có hai bản: bản **nội bộ** đủ các nhóm mục, bản **bên ngoài** bỏ mọi chi tiết
> nội bộ. Hai điều không làm: tự tăng version, và sửa mục CHANGELOG đã có.

## 1. Khi nào

Sau khi người dùng kết luận Cổng 2 (Đạt hoặc Đạt có điều kiện), trước khi phát hành. Chưa qua Cổng 2 thì chưa
có gì để ghi: nghiệm thu và phát hành là hai việc khác nhau ([method/evidence.md](../../../method/evidence.md)
mục 6). Bản ghi chú là đầu vào của bước phát hành, không thay bước đó.

## 2. Lấy chữ từ đâu

| Nguồn | Dùng cho |
|---|---|
| REPORT | kết quả kiểm, cách dùng, đã đổi gì, cách hoàn tác, rủi ro còn lại, việc để lại |
| Mục đang mở của CHANGELOG | câu chữ hướng người dùng; đọc để đối chiếu, **không sửa** |
| PROGRESS | phán quyết và mốc commit có ảnh hưởng tới người dùng hoặc vận hành |
| Spec sống của tính năng | hành vi hiện hành sau Cổng 2 |

Hai nguồn lệch nhau thì REPORT thắng ở phần kết quả kiểm; chỗ lệch ghi thành một dòng ở cuối ghi chú, không
tự dung hoà bằng cách đoán. Ý nào không có nguồn thì không viết — ghi "chưa kiểm" hoặc bỏ.

## 3. Bản nội bộ — khung theo nhóm mục

Mỗi nhóm một tiêu đề; nhóm không có gì thì giữ tiêu đề và ghi "Không có." để người đọc biết nhóm đã được xét.

| Nhóm | Trả lời câu hỏi | Lấy chủ yếu từ |
|---|---|---|
| Người dùng thấy gì | điều người dùng làm được hoặc thấy khác đi | spec sống, REPORT |
| API và hợp đồng | giao diện, sự kiện, định dạng nào đổi; ai đang dùng | mục "Đổi hợp đồng / giao diện" của SPEC |
| Dữ liệu và migration | schema, backfill, thứ tự chạy, có đảo ngược được không | PLAN, báo cáo diễn tập nếu có |
| Vận hành | cấu hình, biến môi trường, quyền, việc phải làm khi triển khai | REPORT, PROGRESS |
| Bảo mật | bề mặt tấn công đổi gì; phát hiện bảo mật đã đóng hay còn mở | `RF` của thẻ chuyên đề |
| Cờ tính năng | cờ nào, mặc định, ai bật, khi nào gỡ | PLAN, REPORT |
| Cách kiểm | sau triển khai, lệnh hoặc thao tác nào xác nhận chạy đúng | `VR` |
| Quan sát | log, số đo, cảnh báo nào cho biết đang hỏng | PLAN, REPORT |
| Hoàn tác | các bước quay lại, và giới hạn (dữ liệu đã ghi thì sao) | REPORT mục cách hoàn tác |
| Việc còn mở | `CO` và điều kiện của Đạt có điều kiện, mỗi mục kèm dòng `RQ-` | REPORT, REQUESTS |

Mọi mã (`FR`, `RF`, `CO`…) ở bản nội bộ kèm tên ngắn, theo skill `id-convention`.

## 4. Bản bên ngoài

Viết **sau** bản nội bộ, từ chính bản nội bộ, và chỉ giữ thứ người ngoài cần để dùng hoặc tích hợp:

- Giữ: điều làm được nay, thay đổi hợp đồng ảnh hưởng người tích hợp (kèm cách chuyển), việc người dùng phải
  tự làm khi nâng cấp, giới hạn đã biết nói bằng lời thường.
- Bỏ: mã định danh nội bộ, nhãn agent và tier, đường file và tên nhánh, số vòng kiểm định, nợ chưa công bố,
  chi tiết cách khai thác của lỗ hổng chưa có bản vá.
- Giọng: dẫn bằng điều người dùng **làm được**, không bằng việc đội đã làm. Một câu đổi nghĩa so với CHANGELOG
  thì dừng lại hỏi, không tự chọn.
- Người duyệt bản ngoài là một agent hoặc người khác người viết; việc gửi đi đâu là tác động ra ngoài và chờ
  người dùng gật.

## 5. Không làm

- **Tự tăng version.** Chỉ đề xuất số mới kèm lý do; người dùng quyết. Version đã tăng sẵn mà ghi chú không
  nhắc hết thay đổi thì nói ra chỗ thiếu.
- **Sửa, đảo thứ tự hay thay thế mục CHANGELOG có sẵn.** Chỉ thêm mục mới dưới tiêu đề đang mở của sprint;
  sửa chữ trong mục cũ phải dùng thao tác thay đúng chuỗi cũ, và mục trông sai thì hỏi.
- Phát hành, đẩy nhánh, gắn thẻ phiên bản: tác động ra ngoài, làm khi người dùng gật ở menu nhánh.
- Viết kết quả chưa có `VR`. Việc có `VR` Chưa chạy hoặc Không áp dụng không được tả như đã kiểm.
