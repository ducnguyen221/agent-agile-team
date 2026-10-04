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
- Truy vấn khoá ngoại xét từng cột riêng: khoá ngoại ghép `(a, b)` đã có index `(a, b)` vẫn bị báo ở cột `b`
  (dương tính giả); đọc index thật trước khi kết luận thiếu.
- `mean_exec_time` có từ PostgreSQL 13; bản cũ hơn dùng `mean_time`.
- Chuỗi kết nối lấy từ biến môi trường; không in ra báo cáo.

## 3. Cấu hình mẫu

```sql
-- Connection limits (size to RAM and pool)
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET work_mem = '8MB';

-- Timeouts
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER ROLE app_role SET statement_timeout = '30s';  -- vai trò ứng dụng, không đặt toàn máy
ALTER ROLE app_role SET lock_timeout = '5s';        -- chờ khoá quá 5 giây thì bỏ, không xếp hàng vô hạn

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
- `statement_timeout` đặt toàn máy có thể giết migration dài: mẫu trên đặt riêng cho vai trò ứng dụng
  (`app_role` là tên giả định, thay bằng vai trò thật), migration dùng vai trò khác (skill `database-migrations`).
- Chạy những lệnh trên lên máy chủ dùng chung hay production: dừng, trình lệnh + ảnh hưởng + cách hoàn tác,
  chờ người dùng gật.

### 3.1. `lock_timeout` — đừng xếp hàng chờ khoá vô hạn

Ba timeout làm ba việc khác nhau (mặc định đều `0` = tắt; tài liệu PostgreSQL khuyên đặt theo vai trò, cơ sở dữ liệu hay
phiên, không đặt toàn máy trong `postgresql.conf`):

| Timeout | Huỷ khi | Dùng để |
|---|---|---|
| `statement_timeout` | một câu lệnh chạy quá thời gian | chặn truy vấn chạy mãi |
| `lock_timeout` | một câu lệnh **chờ khoá** quá thời gian (mỗi lần xin khoá tính riêng) | chặn dây chuyền chờ khoá: lệnh DDL xếp hàng sau giao dịch dài sẽ chặn mọi truy vấn xếp sau nó |
| `idle_in_transaction_session_timeout` | phiên nằm im trong giao dịch mở quá thời gian | giao dịch bỏ dở không giữ khoá và không chặn dọn dòng chết |

- `lock_timeout` nên **nhỏ hơn** `statement_timeout`; đặt bằng hoặc lớn hơn thì `statement_timeout` luôn kích hoạt trước,
  `lock_timeout` vô nghĩa.
- Vai trò ứng dụng: `lock_timeout` vài giây (ví dụ `5s`), hết hạn thì báo lỗi gọn và thử lại ở tầng ứng dụng (skill
  `error-handling`). Lệnh đổi schema chạy tay hay trong migration: đặt riêng cho phiên migration
  (`SET lock_timeout = '5s'` trước câu `ALTER`), hỏng thì thử lại ngoài giờ cao điểm thay vì để câu `ALTER` giữ hàng đợi khoá
  (xem skill `database-migrations`).
- Nguồn: tài liệu PostgreSQL, "Client Connection Defaults" (`lock_timeout`, `statement_timeout`,
  `idle_in_transaction_session_timeout`).

### 3.2. Tính số kết nối và bộ gộp kết nối (PgBouncer)

**Số kết nối tối đa tới Postgres = số instance × cỡ pool mỗi instance** (cộng kết nối quản trị, job, giám sát), và con số đó
phải **nhỏ hơn `max_connections`** đã trừ phần dự trữ. Ví dụ 12 instance × pool 20 = 240 kết nối: vượt `max_connections = 100`,
sinh `too many connections`. Mỗi kết nối Postgres là một tiến trình tốn bộ nhớ, nên nâng `max_connections` cao không phải cách
chữa; cách chữa là **giảm số kết nối thật** bằng một trong hai cách (hoặc cả hai):

1. Giảm cỡ pool mỗi instance (đa số ứng dụng cần ít kết nối hơn nhiều so với pool mặc định) cho tới khi tổng thật nằm
   trong ngân sách; đo chờ lấy kết nối trước khi chốt.
2. Đặt bộ gộp kết nối (**PgBouncer**) giữa ứng dụng và Postgres: hàng trăm kết nối phía ứng dụng dồn vào vài chục kết nối
   thật.

```ini
; pgbouncer.ini (trích)
[pgbouncer]
pool_mode = transaction        ; trả kết nối thật về bể ngay khi giao dịch kết thúc
default_pool_size = 20         ; kết nối thật tối đa cho mỗi cặp người dùng/CSDL
max_client_conn = 1000         ; số kết nối phía ứng dụng chấp nhận
reserve_pool_size = 5          ; dự phòng khi tải cao
```

- Ba chế độ: `session` (mặc định; trả kết nối khi client ngắt), `transaction` (trả khi giao dịch xong — thường dùng với
  ứng dụng web), `statement` (trả sau mỗi câu, cấm giao dịch nhiều câu). Mặc định `default_pool_size` là 20,
  `max_client_conn` là 100 — đặt lại theo ngân sách ở trên.
- **Chế độ `transaction` không dùng được** với: `SET`/`RESET` ở mức phiên, `LISTEN`, khoá tư vấn mức phiên
  (advisory lock), con trỏ `WITH HOLD`, `PREPARE` ở mức phiên (câu lệnh chuẩn bị phía giao thức chỉ chạy khi cấu hình
  `max_prepared_statements`). Ứng dụng dùng các tính năng đó thì giữ chế độ `session` hoặc nối thẳng, hoặc sửa ứng dụng.
  Đặt timeout theo vai trò (`ALTER ROLE … SET`, mục 3.1) thay vì `SET` mỗi phiên, vì `SET` không sống qua các giao dịch.
- Khi có PgBouncer, pool trong ứng dụng đặt nhỏ lại (tổng instance × pool app có thể lớn hơn `default_pool_size`; bộ gộp
  hấp thụ chênh lệch). Cảnh báo khi số kết nối gần `max_connections` (`SELECT count(*) FROM pg_stat_activity`).
- Nguồn: tài liệu PgBouncer (cấu hình, bảng tính năng theo chế độ gộp).
