# Ghi chú phát hành

<!-- Nguồn ý: bộ skill quy trình private, `release-notes-writer` (không giấy phép). Viết lại phòng sạch từ danh
     sách ý (`TK10.5`), không mở văn bản gốc. -->

> **Kết luận:** ghi chú phát hành lấy nội dung từ **REPORT** (`VR`, `RF`, `CO`), không từ trí nhớ; nhóm theo
> **tác động**, không theo commit; luôn có cách kiểm, cách quan sát và cách hoàn tác. Hai bản: **nội bộ** đủ
> chi tiết vận hành, **bên ngoài** chỉ nói điều người dùng thấy và cần làm — không mã nội bộ, không hạ tầng,
> dẫn bằng lợi ích. Viết ghi chú không bao giờ kéo theo tăng version.

## 1. Khi nào

Sau Cổng 2 (bước 6 của `SKILL.md`), khi sprint làm **một** trong các điều: đổi hành vi người dùng thấy · thêm,
sửa, bỏ API hay hợp đồng giữa các phần · đổi dữ liệu hoặc schema · cắt một bản phát hành. Sprint chỉ đổi nội
bộ (refactor, test, tài liệu) thì không viết; ghi "không có ghi chú phát hành — không đổi gì bên ngoài" vào
nhật ký PROGRESS.

Không dùng cho: trạng thái giữa sprint (PROGRESS lo) · bài quảng bá · thay cho mục CHANGELOG (đồng bộ tài
liệu lo, `docs-sync.md` mục 5).

## 2. Nguồn

| Phần của ghi chú | Lấy từ |
|---|---|
| Đã phát hành | REPORT mục "Cách dùng, đã đổi gì, cách hoàn tác" + các `SC` có `VR` Đạt |
| Chưa phát hành hoặc có điều kiện | `CO`, `RF` còn mở, `VR` Chưa chạy / Không áp dụng |
| Cách kiểm | lệnh hoặc thao tác của `VR` tương ứng |
| Hoàn tác | REPORT mục 4; runbook nếu có migration (`database-migrations`, `references/rehearsal.md`) |
| Cờ tính năng | PLAN hoặc cấu hình: tên cờ, giá trị mặc định, **chủ** |

Hai luật đi kèm bảng:
- Một thay đổi không có `VR` Đạt thì ghi "đã phát hành, **chưa có bằng chứng kiểm**" — không bao giờ ghi "đã
  kiểm". Người đọc ghi chú sẽ tin chữ đó khi quyết định có bật cho khách hay không.
- Cờ tính năng không có chủ thì không đưa vào bản phát hành: chuyển xuống mục "Còn mở" và báo người điều
  phối. Cờ không ai chịu trách nhiệm tắt là cờ sống mãi.

## 3. Khung — bản nội bộ

Mỗi mục là một gạch đầu dòng ngắn; mục không có gì thì ghi "Không đổi" thay vì xoá, để người đọc biết đã
xét. Mã luôn kèm tên ngắn; ngày theo ISO.

```markdown
# Ghi chú phát hành — <tên bản hoặc SPR-xx> — YYYY-MM-DD (nội bộ)

## Người dùng thấy gì
- <đổi gì> — <ai bị ảnh hưởng> — <họ cần làm gì | không cần làm gì>

## API và hợp đồng
- Thêm | Sửa | Bỏ: <endpoint, sự kiện, schema> — <bên dùng phải đổi gì, trước khi nào>

## Dữ liệu và migration
- <bảng>: <đổi gì> · backfill <có/không, thời gian> · khoá <đo được bao lâu> · diễn tập: <VRk (tên) | chưa>

## Vận hành
- <cấu hình, biến môi trường, job định kỳ, quyền mới hay đổi>

## Bảo mật
- <loại vấn đề đã xử lý, ai bị ảnh hưởng> — không ghi cách khai thác

## Cờ tính năng
- <tên cờ> — mặc định <bật/tắt> — chủ <vai/người> — bật khi <điều kiện>

## Cách kiểm
- <bước kiểm sau khi lên> — bằng chứng: <VRk (tên)>

## Quan sát
- <log, metric, dashboard> — báo động khi <ngưỡng>

## Hoàn tác
- Lệnh: <…> · Huỷ khi: <ngưỡng cụ thể> · Dữ liệu hoàn tác được: <có | không — vì sao>

## Còn mở
- <COk (tên) — chủ — mốc> · <RFk (tên) — mức — xử lý> · <VRk Chưa chạy — vì sao>
```

Lưu ở nơi dự án quy định; chưa quy định thì đặt trong thư mục sprint, cạnh REPORT.

## 4. Bản bên ngoài

Chỉ ba phần: **Có gì mới** (từ "Người dùng thấy gì"), **Thay đổi cho bên tích hợp** (từ "API và hợp đồng",
chỉ khi có bên dùng ngoài) và **Bạn cần làm gì**. Mỗi dòng mở đầu bằng điều người dùng làm được:

```text
Có gì mới
- Giờ bạn có thể lọc đơn theo trạng thái ngay trên trang danh sách.
Bạn cần làm gì
- Không cần làm gì; bộ lọc cũ vẫn chạy tới hết tháng sau.
```

Cấm trong bản bên ngoài: mã sprint và mã mục (`SPR-`, `TK`, `RF`…), tên bảng, tên máy chủ hay dịch vụ hạ tầng,
chi tiết lỗ hổng. Lưu cạnh bản nội bộ, tiêu đề ghi rõ "(bên ngoài)". Đăng hay gửi bản bên ngoài là tác động
ra ngoài — điều kiện dừng (c): chỉ khi người dùng gật.

## 5. Không làm

- Không tăng version, không tạo tiêu đề phiên bản mới trong CHANGELOG — người dùng quyết lúc phát hành
  (`docs-sync.md` mục 5 và 7).
- Không ghi "đã kiểm" khi thiếu `VR` Đạt (mục 2).
- Không chép thông điệp commit: commit nói code đã đổi thế nào, ghi chú nói ai bị ảnh hưởng và phải làm gì.
- Không viết ghi chú cho thứ chưa qua Cổng 2.
