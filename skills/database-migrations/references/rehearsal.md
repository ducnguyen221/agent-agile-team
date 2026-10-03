# Diễn tập migration

<!-- Nguồn ý: bộ skill quy trình private, `migration-rehearsal` (không giấy phép). Viết lại từ danh sách ý có mang một số
     câu chữ nguồn (`TK10.4`); chưa đạt quy trình phòng sạch, phải viết lại
     thật sự trước khi công khai (`CO2`, `RQ-021` ở hồ sơ riêng của chủ repo). -->

> **Kết luận:** trước khi xin chạy thật bất kỳ migration nào từ rủi ro vừa trở lên, chạy thử nó trọn vẹn trên
> **một bản sao có lượng dữ liệu như production** và ghi lại các số đo ở mục 2 bước 4; đường lùi được viết và
> review **trước** đường tiến; runbook production nêu **tiêu chí huỷ** bằng con số và từng bước hoàn tác. Dữ liệu chỉ đi một chiều: chạy ở production rồi
> thì "hoàn tác" là một migration tiến mới — vì thế mọi bất ngờ phải lộ ra ở buổi diễn tập, không ở buổi thật.

**Dùng khi:** thêm hoặc sửa file migration, với bất kỳ công cụ nào (Alembic, Flyway, Knex, Prisma, SQL thuần);
lệnh `ALTER`/`DROP`/`CREATE INDEX`, đổi khoá ngoại, đổi kiểu cột; mọi script ghi lại dữ liệu hàng loạt (lấp
cột mới, chữa dữ liệu sai).
**Không dùng khi:** thay đổi không đụng tới nơi lưu dữ liệu, hoặc việc chỉ là đọc — xem cấu trúc bảng, chạy báo cáo.

## 1. Đầu vào

- File migration (cả hướng tiến và hướng lùi) và script backfill nếu có.
- **Số liệu thật của các bảng bị chạm** (số dòng, dung lượng kể cả index), lấy bằng một truy vấn chạy ngay lúc
  chuẩn bị, trên staging hay bản sao; con số nhớ được hay ghi trong tài liệu cũ không dùng. Ví dụ trên Postgres (số dòng là ước lượng từ thống kê, đủ để chọn chiến lược):

  ```sql
  SELECT relname,
         n_live_tup                                     AS approx_rows,
         pg_size_pretty(pg_total_relation_size(relid))  AS size_with_indexes
  FROM pg_stat_user_tables
  WHERE relname IN ('orders', 'order_items');
  ```

- Hành vi khoá của engine với **từng** lệnh trong migration (tra tài liệu engine đúng phiên bản đang chạy).
- Hệ thống được phép chậm hay ngừng lúc nào: có khung bảo trì hay phải phục vụ liên tục, giờ nào ít truy cập
  nhất, và có bản sao chỉ-đọc nào phải bám kịp máy chính hay không.

## 2. Các bước

1. **Phân loại** thay đổi và rủi ro (`method/sizing.md`):

   | Loại | Ví dụ | Rủi ro |
   |---|---|---|
   | Thêm | bảng mới, cột cho phép rỗng, index dựng đồng thời | thấp |
   | Sửa tại chỗ | đổi kiểu, thêm ràng buộc, backfill | vừa — **cao** khi backfill bảng nóng hoặc đổi kiểu bảng lớn |
   | Phá huỷ | bỏ cột/bảng, xoá dữ liệu, biến đổi làm mất thông tin | cao |

   Rủi ro cao → `risk: high`, `risk_tags` có `data_migration`, cỡ lớn, kéo thẻ chuyên đề dữ liệu.
2. **Đường lùi trước.** Viết `downgrade` (hoặc script đảo) và review nó **trước** khi duyệt đường tiến.
   Không đảo được → ghi `DN` cho người dùng chấp nhận rõ, kèm cách cứu thay thế (bản sao lưu đã khôi phục
   thử, bảng giữ bản dữ liệu cũ tới mốc hẹn).
3. **Ước lượng tác động** không đụng dữ liệu thật: in SQL sẽ chạy (chạy khô, ví dụ `alembic upgrade head
   --sql`), `EXPLAIN` cho truy vấn chọn dòng của backfill, đối chiếu loại khoá từng lệnh với cỡ bảng.
4. **Diễn tập** trên bản sao khôi phục từ bản sao lưu gần nhất, hoặc bản sao cỡ tương đương với dữ liệu cá
   nhân đã che. Chạy **tiến → kiểm dữ liệu → lùi → tiến lại**, tốt nhất khi có tải giả lập. Đo:

   - **Thời gian** từng bước, so với cửa sổ cho phép.
   - **Khoá và lag replica** — đặt `lock_timeout` ngắn để lệnh tự bỏ thay vì xếp hàng chặn mọi truy vấn sau
     nó; theo dõi trong lúc chạy:

     ```sql
     SET lock_timeout = '3s';
     -- phiên khác, lặp lại trong lúc migration chạy:
     SELECT a.pid, l.mode, l.relation::regclass AS rel, now() - a.query_start AS running_for
     FROM pg_locks l JOIN pg_stat_activity a USING (pid)
     WHERE NOT l.granted;
     SELECT application_name, replay_lag FROM pg_stat_replication;  -- trên primary
     ```

   - **Lỗi ứng dụng** trong lúc chạy (log, tỉ lệ lỗi của tải giả lập).
   - **Dữ liệu khớp**: số dòng và tổng then chốt trước ↔ sau, sau cả chiều lùi.

   Ghi số đo vào `VR` kèm lệnh nguyên văn, phiên bản engine, nguồn và cỡ bản sao.
5. **Kế hoạch backfill:** lô cố định; idempotent (điều kiện chọn dòng chưa xử lý, chạy lại không ghi đúp);
   nghỉ giữa các lô; log tiến độ "đã xử lý / tổng"; chạy tiếp được sau khi đứt; ngưỡng tự dừng (lag hay tỉ
   lệ lỗi vượt mức đã đo ở bước 4). Mẫu lô cho Postgres: `postgres-safe-ddl.md` mục 5.
6. **Runbook production**, mỗi mục có giá trị cụ thể, không "theo dõi cẩn thận":
   kiểm trước (sao lưu mới **đã khôi phục thử**, đủ đĩa, không job nặng trùng giờ) · lệnh chính xác theo thứ
   tự · bảng theo dõi (chỉ số, ngưỡng) · **tiêu chí huỷ** (ví dụ "khoá chờ > 5 s hoặc lag > 30 s thì dừng ở
   lô hiện tại") · bước hoàn tác · ai cần báo trước và sau.
   Ai ký runbook tuỳ mức rủi ro: mức vừa cần thẻ chuyên đề dữ liệu mà Tech Reviewer kéo vào; mức cao thì ngoài
   thẻ đó còn phải có một người trực vận hành, do chính người dùng chọn.

## 3. Đầu ra

- **Báo cáo diễn tập** thành `VR`:

  ```text
  Diễn tập <migration> trên <bản sao: nguồn, cỡ, ngày khôi phục> — <engine + phiên bản>
  Tiến: <thời gian> · lag replica tối đa <…> · khoá chờ lâu nhất <…> · lỗi ứng dụng <…>
  Lùi: <thời gian> · dữ liệu khớp trước ↔ sau: <số dòng, tổng then chốt>
  Kết quả: Đạt | Không đạt — <vì sao>
  ```

- Cặp tiến / lùi đã được review, trỏ commit.
- Runbook gắn vào PLAN; phần hoàn tác chép tóm tắt vào REPORT mục "Cách dùng, đã đổi gì, cách hoàn tác".
- Chạy trên production là hành động không đảo ngược — điều kiện dừng (a): chỉ làm khi người dùng gật,
  sau Cổng 2.

## 4. Điểm dừng

| Tình huống | Mức | Làm |
|---|---|---|
| Migration một chiều (không có đường lùi) mà chưa có `DN` người dùng đồng ý bằng chữ | Chặn | `BR`, trình `DN` kèm cách cứu thay thế |
| Khoá trên bảng nóng kéo dài quá cửa sổ cho phép | Chặn | đổi sang cách trực tuyến: bảng bóng, công cụ đổi schema trực tuyến, hoặc chia nhỏ lệnh |
| Backfill không idempotent hoặc không chạy tiếp được | Phải sửa | sửa điều kiện chọn dòng và log tiến độ, diễn tập lại |
| Rủi ro cao, chưa có buổi chạy thử nào | Chặn | chưa được trình Cổng 2: chạy thử trên bản sao, ghi `VR`, rồi mới trình |
| Không có bản sao để diễn tập | — | `VR` ghi Chưa chạy kèm giới hạn, báo Analyst; không thay bằng "chạy thử trên production" |
