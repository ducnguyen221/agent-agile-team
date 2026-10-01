---
name: postgres
description: Use when writing PostgreSQL queries or migrations, designing tables, columns, or indexes, choosing data types, troubleshooting a slow query or table bloat, implementing Row Level Security, paginating large tables, building a job queue on Postgres, or setting connection and timeout settings.
metadata:
  group: technique
  kind: reference
  roles: [implementer, tech-reviewer]
source: affaan-m/ECC skills/postgres-patterns/SKILL.md
source_sha: c70874fae9eb0e5ad0365beb7e2955899fd1d30f
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: MIT
rewrite_before_public: false
---

# PostgreSQL — tra nhanh

> **Kết luận:** chọn index theo **dạng điều kiện** của truy vấn (bằng → B-tree, JSONB/full-text → GIN,
> chuỗi thời gian rất lớn → BRIN; index ghép: cột so bằng trước, cột khoảng sau); kiểu dữ liệu đúng ngay
> từ đầu (`bigint`, `text`, `timestamptz`, `numeric`). Phân trang bằng con trỏ, hàng đợi bằng
> `FOR UPDATE SKIP LOCKED`, đặt timeout cho mọi kết nối. Review đầy đủ: agent `database-reviewer`.

## 1. Khi nào dùng

- Viết truy vấn SQL hoặc migration (quy trình migration an toàn: skill `database-migrations`).
- Thiết kế bảng, cột, index.
- Truy vấn chậm, bảng phình.
- Cài Row Level Security.
- Cấu hình connection pool, timeout.

## 2. Chọn index

| Dạng truy vấn | Loại index | Ví dụ |
|---|---|---|
| `WHERE col = value` | B-tree (mặc định) | `CREATE INDEX idx ON t (col)` |
| `WHERE col > value` | B-tree | `CREATE INDEX idx ON t (col)` |
| `WHERE a = x AND b > y` | Ghép | `CREATE INDEX idx ON t (a, b)` |
| `WHERE jsonb @> '{}'` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| `WHERE tsv @@ query` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| Khoảng thời gian trên bảng chuỗi thời gian | BRIN | `CREATE INDEX idx ON t USING brin (col)` |

Mỗi khoá ngoại cần index ở phía tham chiếu (truy vấn ở mục 5 tìm khoá ngoại thiếu index). Tạo index
trên bảng đang chạy: `CREATE INDEX CONCURRENTLY`.

## 3. Chọn kiểu dữ liệu

| Dùng cho | Kiểu đúng | Tránh |
|---|---|---|
| ID | `bigint` (identity) | `int` (tràn), UUID ngẫu nhiên (index phân mảnh) |
| Chuỗi | `text` | `varchar(255)` tuỳ tiện |
| Thời điểm | `timestamptz` | `timestamp` không múi giờ |
| Tiền | `numeric(10,2)` | `float` |
| Cờ | `boolean` | `varchar`, `int` |

## 4. Mẫu thường dùng

**Thứ tự cột trong index ghép**

```sql
-- Cột so bằng trước, cột khoảng sau
CREATE INDEX idx ON orders (status, created_at);
-- Phục vụ: WHERE status = 'pending' AND created_at > '2024-01-01'
```

**Index bao phủ**

```sql
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);
-- SELECT email, name, created_at không phải đọc bảng
```

**Index một phần**

```sql
CREATE INDEX idx ON users (email) WHERE deleted_at IS NULL;
-- Nhỏ hơn, chỉ chứa người dùng còn hoạt động
```

**Chính sách RLS tối ưu** (ví dụ theo Supabase, hàm `auth.uid()`)

```sql
CREATE POLICY policy ON orders
  USING ((SELECT auth.uid()) = user_id);  -- bọc trong SELECT để chỉ tính một lần, không tính mỗi dòng
```

**UPSERT**

```sql
INSERT INTO settings (user_id, key, value)
VALUES (123, 'theme', 'dark')
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value;
```

**Phân trang con trỏ**

```sql
SELECT * FROM products WHERE id > $1 ORDER BY id LIMIT 20;
-- Nhảy thẳng qua index; OFFSET lớn phải đọc rồi bỏ mọi dòng phía trước
```

**Hàng đợi việc**

```sql
UPDATE jobs SET status = 'processing'
WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1
  FOR UPDATE SKIP LOCKED
) RETURNING *;
```

## 5. Phát hiện phản mẫu

```sql
-- Khoá ngoại chưa có index
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );

-- Truy vấn chậm (cần extension pg_stat_statements)
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;

-- Bảng phình (nhiều dòng chết)
SELECT relname, n_dead_tup, last_vacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

Xem kế hoạch thực thi trước khi kết luận chậm ở đâu: `EXPLAIN (ANALYZE, BUFFERS) <truy vấn>`.

## 6. Cấu hình mẫu

```sql
-- Giới hạn kết nối (chỉnh theo RAM)
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET work_mem = '8MB';

-- Timeout
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '30s';

-- Giám sát
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Mặc định an toàn
REVOKE ALL ON SCHEMA public FROM public;

SELECT pg_reload_conf();
```

`max_connections` cần khởi động lại máy chủ mới có hiệu lực; `pg_stat_statements` còn cần có trong
`shared_preload_libraries`. Đổi cấu hình máy chủ dùng chung là thao tác ngoài phạm vi thường: hỏi trước.

## 7. Liên quan

- Agent reviewer: `database-reviewer` (review đầy đủ truy vấn, schema, bảo mật, hiệu năng);
  `security-reviewer` khi chạm RLS, quyền, dữ liệu nhạy cảm.
- Skill: `database-migrations`, `fastapi`, `python`, `api-design`, `security-review`.

Dựa trên Supabase Agent Skills (ghi công: nhóm Supabase), giấy phép MIT.
