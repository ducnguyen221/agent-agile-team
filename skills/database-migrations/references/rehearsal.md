
# Diễn tập migration

> **Kết luận:** lần chạy đầu tiên của một migration nặng hoặc rủi ro cao không được rơi vào dữ liệu thật. Cần
> sẵn ba thứ: **số đo** các bảng bị chạm, **một buổi diễn tập** trên bản sao dựng lại từ bản lưu và có cỡ ngang
> production, cùng **runbook** ghi giá trị cụ thể, ngưỡng dừng và lệnh hoàn tác. Kết quả diễn tập được
> ghi thành `VR` để reviewer và người dùng đối chiếu.

## 1. Khi nào phải diễn tập

Cỡ lớn hoặc `risk_tags` có `data_migration` (`method/sizing.md`): đổi kiểu cột, bỏ cột, backfill trên bảng
hay bị ghi, thêm ràng buộc lên bảng đã có dữ liệu, dựng index trên bảng lớn. Migration nhỏ, bảng nhỏ, thêm
cột cho phép rỗng thì kiểm cú pháp và chạy trên môi trường phát triển là đủ; ghi lý do bỏ diễn tập vào PLAN.

## 2. Số liệu đầu vào

Với **mỗi bảng bị chạm**, ghi:

- số dòng ước lượng;
- dung lượng **gồm cả index** (không chỉ dữ liệu bảng);
- tốc độ ghi hiện tại nếu bảng đang nhận ghi liên tục.

Đo bằng truy vấn **chỉ-đọc** trên bản sao đọc hoặc trên chính bản sao diễn tập, không chạy lên node chính
đang phục vụ người dùng. Ví dụ trên Postgres:

```sql
SELECT relname,
       n_live_tup AS rows_estimate,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_stat_user_tables
WHERE relname IN ('orders', 'order_items');
```

Số ước lượng đủ để chọn đường; cần chính xác (ví dụ để chia lô) thì đếm thật trên bản sao.

## 3. Phân loại và đường lùi

1. Phân loại thay đổi theo `method/sizing.md` mục 2; thay đổi nào cũng chạm `data_migration` thì cỡ tối thiểu
   là lớn.
2. **Viết và cho review đường lùi trước khi viết migration tới.** Đường lùi là lệnh cụ thể (migration lùi,
   hoặc migration tới bù), không phải câu "khôi phục từ bản sao lưu". Có bước **không đảo ngược** thì nói
   thẳng, và bước đó chỉ chạy khi người dùng gật.
3. Ước lượng tác động bằng **chạy khô** (in SQL sẽ chạy, kế hoạch thực thi, số dòng bị chạm) trước khi chạy
   thật trên bản sao.

## 4. Diễn tập

Điều kiện: dựng bản sao bằng cách **khôi phục** bản lưu mới nhất; phiên bản và cấu hình quan trọng của máy
cơ sở dữ liệu giống production; khối lượng dữ liệu cũng ngang. Bản thu nhỏ cho số đo đẹp nhưng sai.

Chạy đúng trình tự sẽ chạy ở production, và ghi lại:

| Đo | Ghi |
|---|---|
| Thời gian | tổng và từng bước, tính bằng giây |
| Khoá | loại khoá, bảng nào, giữ bao lâu; truy vấn khác có bị chờ không |
| Dung lượng | tăng thêm của bảng, index và nhật ký ghi trước (WAL) |
| Tải | CPU, I/O, độ trễ của một truy vấn mẫu chạy song song |
| Đường lùi | chạy thử cả đường lùi, đo như trên |

**Backfill:** chia theo lô cỡ cố định, mỗi lô là một giao dịch ngắn; **idempotent** (chạy lại không làm hỏng
dữ liệu đã chuyển); có điểm tiếp (lưu khoá lô cuối đã xong) để đứt giữa chừng thì chạy tiếp; có log tiến độ.
Diễn tập phải cắt ngang một lần giữa chừng để chứng minh chạy tiếp được.

Kiểm sau cùng: số dòng và tổng kiểm trên cột liên quan khớp với trước khi chạy; ứng dụng bản cũ và bản mới
đều đọc được schema ở mỗi bước (nguyên tắc 6 của skill `database-migrations`).

## 5. Runbook production

Sinh từ kết quả diễn tập, với **giá trị cụ thể**, không để chỗ trống:

- thứ tự lệnh, và người chạy từng bước;
- thời gian dự kiến mỗi bước (lấy từ số đo, cộng biên an toàn đã ghi rõ);
- **ngưỡng dừng** dạng số: ví dụ khoá giữ quá N giây, độ trễ truy vấn vượt M mili giây, lỗi vượt K lần;
- **lệnh hoàn tác** cho từng bước, đã chạy thử ở mục 4;
- cách theo dõi trong lúc chạy và điều gì chứng tỏ bước xong.

Runbook đi cùng PLAN vào review. Reviewer chuyên đề dữ liệu (`database-reviewer`) đọc runbook, không chỉ đọc
mã migration.

## 6. Đầu ra

**Báo cáo diễn tập** ghi vào REPORT thành một `VR`: lệnh, môi trường (phiên bản, cỡ bản sao, commit), các số
đo ở mục 4, kết quả Đạt hoặc Không đạt kèm lý do, và giới hạn (bản sao khác production ở điểm nào). `VR` do
agent khác người viết migration chạy hoặc kiểm lại.

## 7. Dừng

- Việc diễn tập đòi chạm **dữ liệu thật** (khôi phục bản sao chứa dữ liệu người dùng, hay chạy lên môi trường
  đang phục vụ): dừng, ghi `BR`, hỏi người dùng; che hoặc ẩn danh dữ liệu cá nhân nếu được cho phép.
- **Không có bản sao** cỡ production để diễn tập: dừng, không chạy thay bằng bản thu nhỏ rồi coi như đạt. Ghi
  `VR` là Chưa chạy; người dùng quyết tạo bản sao hoặc chấp nhận rủi ro bằng văn bản.
- Đo thấy khoá hay thời gian vượt ngưỡng dừng đã định: quay lại thiết kế (chia lô nhỏ hơn, đổi cách làm),
  không nới ngưỡng cho vừa số đo.
