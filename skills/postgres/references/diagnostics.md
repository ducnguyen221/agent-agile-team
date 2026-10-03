# Chẩn đoán và cấu hình PostgreSQL

> **Kết luận:** đo trước khi sửa — đọc `EXPLAIN (ANALYZE, BUFFERS)` của đúng truy vấn chậm, rồi mới thêm index
> hay đổi cấu hình. `EXPLAIN ANALYZE` **chạy thật** câu lệnh: câu ghi chỉ thử trên CSDL dev hay bản sao, bọc
> trong giao dịch rồi huỷ. Đổi cấu hình máy chủ dùng chung là thao tác ngoài phạm vi thường: hỏi trước.

## 1. Đọc kế hoạch thực thi

`EXPLAIN (ANALYZE, BUFFERS) <truy vấn>` — với câu ghi: `BEGIN; EXPLAIN (ANALYZE, BUFFERS) …; ROLLBACK;`, và chỉ
trên CSDL không phải production (sequence vẫn tăng, trigger vẫn chạy dù đã huỷ).

| Thấy trong kế hoạch | Thường nghĩa là | Làm tiếp |
|---|---|---|
| `Seq Scan` trên bảng lớn kèm `Rows Removed by Filter` rất lớn | thiếu index cho điều kiện lọc | index theo dạng điều kiện (`SKILL.md` mục 2) |
| số dòng ước lượng lệch số dòng thật nhiều bậc | thống kê cũ, hoặc cột tương quan | `ANALYZE <bảng>`; cân nhắc thống kê mở rộng |
| `Nested Loop` với vế ngoài hàng nghìn dòng trở lên | kế hoạch chọn sai vì ước lượng sai | sửa ước lượng trước, rồi xem lại index phía trong |
| `Sort` hay `Hash` ghi ra đĩa (`external merge`, nhiều batch) | `work_mem` nhỏ so với phép đó | thu hẹp dữ liệu trước; tăng `work_mem` cho phiên, không toàn máy |
| `Buffers: shared read` cao, `hit` thấp | dữ liệu không nằm trong bộ nhớ đệm | lần chạy thứ hai để so; index bao phủ để đọc ít trang hơn |
| `Index Scan` nhưng vẫn chậm, đọc nhiều trang bảng | index không chọn lọc, hoặc phải tra bảng từng dòng | index ghép, index bao phủ |

## 2. Truy vấn chẩn đoán (chỉ đọc)

```sql
-- Foreign keys without an index led by that column on the referencing side
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND i.indkey[0] = a.attnum
  );

-- Slowest statements on average (needs the pg_stat_statements extension)
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Bloat signal: many dead tuples, old vacuum
SELECT relname, n_dead_tup, last_vacuum, last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Largest tables, indexes included
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Indexes rarely used since the last statistics reset
SELECT indexrelname, idx_scan, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

- Số liệu `pg_stat_*` tính từ lần đặt lại thống kê gần nhất: index "không dùng" trên CSDL mới khởi động hay bản
  sao ít tải chưa chứng minh gì.
- Ngưỡng trong câu lệnh (100 ms, 1000 dòng chết) là điểm bắt đầu; so với số đo nền của chính dự án.
- Chuỗi kết nối lấy từ biến môi trường; không in ra báo cáo.

## 3. Cấu hình mẫu

```sql
-- Connection limits (size to RAM and pool)
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET work_mem = '8MB';

-- Timeouts
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '30s';

-- Monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Safe default
REVOKE ALL ON SCHEMA public FROM public;

SELECT pg_reload_conf();
```

- `max_connections` chỉ có hiệu lực sau khi khởi động lại máy chủ; `pg_stat_statements` còn phải có trong
  `shared_preload_libraries`.
- `work_mem` tính **cho mỗi phép sắp xếp hay băm**, không cho mỗi kết nối: một truy vấn dùng được nhiều lần
  giá trị đó. Tăng cho một phiên hay một vai trò trước khi tăng toàn máy.
- Nhiều tiến trình ứng dụng thì đặt pool phía trước (pooler hoặc pool trong ứng dụng) thay vì nâng
  `max_connections`; mỗi kết nối tốn bộ nhớ riêng.
- `statement_timeout` toàn máy có thể giết migration dài: đặt riêng cho vai trò ứng dụng, migration dùng vai
  trò khác (skill `database-migrations`).
- Chạy những lệnh trên lên máy chủ dùng chung hay production: dừng, trình lệnh + ảnh hưởng + cách hoàn tác,
  chờ người dùng gật.
