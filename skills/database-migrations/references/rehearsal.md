# Diễn tập migration

> **Kết luận:** migration rủi ro vừa trở lên phải chạy thử trên **bản sao cỡ production** trước, đo thời
> gian, khoá, lỗi ứng dụng, lag replica; viết `downgrade` **trước khi** duyệt `upgrade`; có runbook
> production gồm tiêu chí huỷ và cách hoàn tác. Dữ liệu là đường một chiều: chạy ở production rồi thì lối
> ra duy nhất là đi tới.

**Dùng khi:** thêm/sửa file migration (Alembic, Flyway, Knex, Prisma, SQL thuần); mọi `ALTER TABLE`,
`DROP COLUMN`, `CREATE INDEX`, đổi khoá ngoại, đổi kiểu; chuẩn bị script backfill hay sửa dữ liệu.
**Không dùng khi:** chỉ đọc schema, truy vấn phân tích; thay đổi ứng dụng không chạm schema lưu trữ.

## 1. Đầu vào

- File migration.
- **Cỡ bảng đích** (số dòng, dung lượng) — lấy bằng truy vấn trên staging hoặc bản sao, không chép từ sổ:
  ```sql
  SELECT relname, n_live_tup, pg_size_pretty(pg_total_relation_size(relid))
  FROM pg_stat_user_tables WHERE relname IN ('users', 'orders');
  ```
- Hành vi khoá của engine (Postgres, MySQL, SQL Server…) với từng câu lệnh.
- Dạng tải: chạy 24/7 hay có cửa sổ bảo trì; có replica đọc không.

## 2. Sáu bước

1. **Phân loại**: thêm (rủi ro thấp) · sửa tại chỗ (vừa/cao) · phá huỷ (cao). Migration tối thiểu là rủi ro
   vừa; backfill trên bảng nóng là rủi ro cao (`method/sizing.md`).
2. **Lên kế hoạch đảo ngược**: viết `downgrade` trước khi duyệt `upgrade`. Không đảo ngược được → ghi lý do,
   cần người dùng chấp nhận rõ (ghi `DN`).
3. **Ước lượng tác động**: thời gian giữ khoá, lag replica, phạm vi ảnh hưởng — `EXPLAIN`, chạy khô
   (`alembic upgrade head --sql`) trên bản sao mới dạng production.
4. **Diễn tập**: khôi phục bản sao lưu gần đây hoặc bản sao có cỡ tương đương; chạy migration; đo thời gian,
   khoá đang giữ, lỗi ứng dụng, lag replica. Ghi số đo vào `VR` (kèm lệnh).
5. **Kế hoạch backfill**: chia lô, idempotent, có tiết lưu, log tiến độ, chạy tiếp được khi đứt.
6. **Runbook production**: kiểm trước khi chạy · lệnh chính xác · bảng theo dõi · **tiêu chí huỷ** · các bước
   hoàn tác · ai cần được báo. Rủi ro vừa: Tech Reviewer (chuyên đề dữ liệu) duyệt; rủi ro cao: thêm người
   vận hành do người dùng chỉ định.

## 3. Đầu ra

- Báo cáo diễn tập (thời gian, khoá, quan sát) → `VR` trong REPORT.
- Cặp `upgrade`/`downgrade` đã review.
- Runbook production (hoặc đường dẫn) có phần hoàn tác → mục "Cách dùng, đã đổi gì, cách hoàn tác" của
  REPORT.
- Chạy ở production: hành động không đảo ngược, **chỉ khi người dùng gật**.

## 4. Điểm dừng

| Tình huống | Mức | Làm |
|---|---|---|
| Không đảo ngược được và chưa có chấp nhận rõ của người dùng | Chặn | ghi `BR`, hỏi |
| Thời gian khoá trên bảng nóng vượt cửa sổ chấp nhận được | Chặn | chuyển sang chiến lược DDL trực tuyến (bảng bóng, công cụ như `gh-ost`, `pt-online-schema-change`) |
| Backfill không idempotent / không chạy tiếp được | Phải sửa | viết lại trước khi duyệt |
| Chưa diễn tập với migration rủi ro cao | Chặn | diễn tập rồi mới trình Cổng 2 |
