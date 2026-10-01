# DDL an toàn và migration dữ liệu trên PostgreSQL

> **Kết luận:** thêm cột cho phép rỗng hoặc có mặc định; index trên bảng đã có luôn `CONCURRENTLY`; không
> đổi tên hay bỏ cột trực tiếp — đi qua mở rộng → thu hẹp; cập nhật dữ liệu lớn chia lô, không một
> transaction khổng lồ.

## 1. Thêm cột

```sql
-- Tốt: cho phép rỗng, không khoá lâu
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- Tốt: có mặc định hằng (Postgres 11+ tức thì, không ghi lại bảng)
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- Xấu: NOT NULL không mặc định trên bảng đã có dữ liệu — hỏng ngay, hoặc phải ghi lại mọi dòng
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;
```

Cần `NOT NULL` không mặc định: thêm cột cho phép rỗng → backfill → `ADD CONSTRAINT … CHECK (role IS NOT
NULL) NOT VALID` → `VALIDATE CONSTRAINT` (không khoá ghi) → `SET NOT NULL`.

## 2. Thêm index không gián đoạn

```sql
-- Xấu: chặn ghi suốt thời gian dựng trên bảng lớn
CREATE INDEX idx_users_email ON users (email);

-- Tốt: cho phép ghi đồng thời
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
```

`CONCURRENTLY` **không chạy được trong transaction** — công cụ migration phải mở khối autocommit (Alembic:
`op.get_context().autocommit_block()`). Dựng hỏng giữa chừng để lại index `INVALID`: `DROP INDEX
CONCURRENTLY` rồi dựng lại.

## 3. Đổi tên cột (không gián đoạn)

Không đổi tên trực tiếp ở production. Đi theo mở rộng → thu hẹp:

```sql
-- Bước 1 (migration 001): thêm cột mới
ALTER TABLE users ADD COLUMN display_name TEXT;
-- Bước 2 (migration 002, dữ liệu): backfill theo lô (mục 5)
UPDATE users SET display_name = username WHERE display_name IS NULL;  -- bảng nhỏ; bảng lớn dùng mục 5
-- Bước 3: deploy mã đọc/ghi cả hai cột
-- Bước 4 (migration 003): ngừng ghi cột cũ, rồi bỏ nó
ALTER TABLE users DROP COLUMN username;
```

## 4. Bỏ cột an toàn

1. Gỡ mọi tham chiếu tới cột trong mã.
2. Deploy bản không còn tham chiếu.
3. Migration lần sau mới bỏ cột: `ALTER TABLE orders DROP COLUMN legacy_status;`

ORM giữ model tách khỏi DB được thì gỡ khỏi model trước, bỏ cột ở migration sau (Django:
`SeparateDatabaseAndState` — `django-golang-migrate.md`).

## 5. Cập nhật dữ liệu lớn

```sql
-- Xấu: cập nhật mọi dòng trong một transaction — khoá dòng lâu, phình WAL, lag replica
UPDATE users SET normalized_email = LOWER(email);
```

```sql
-- Tốt: chia lô, có tiến độ, chạy tiếp được. Chạy NGOÀI transaction (COMMIT trong DO cần Postgres 11+).
DO $$
DECLARE
  batch_size INT := 10000;
  rows_updated INT;
BEGIN
  LOOP
    UPDATE users
    SET normalized_email = LOWER(email)
    WHERE id IN (
      SELECT id FROM users
      WHERE normalized_email IS NULL
      LIMIT batch_size
      FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    RAISE NOTICE 'Updated % rows', rows_updated;
    EXIT WHEN rows_updated = 0;
    COMMIT;
  END LOOP;
END $$;
```

Điều kiện `WHERE normalized_email IS NULL` làm vòng lặp **idempotent**: dừng giữa chừng rồi chạy lại vẫn
đúng. Bảng nóng: thêm khoảng nghỉ giữa các lô, theo dõi lag replica và khoá (`rehearsal.md`).
