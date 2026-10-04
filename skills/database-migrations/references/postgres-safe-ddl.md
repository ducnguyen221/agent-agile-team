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
-- Bước 3: deploy mã đọc/ghi cả hai cột, rồi deploy bản chỉ đọc/ghi cột mới (mã không còn tham chiếu `username`)
-- Bước 4 (migration 003, ở lần deploy SAU bước 3 — mục 4): bỏ cột cũ
ALTER TABLE users DROP COLUMN username;
```

Bước 4 không chạy cùng lúc với việc ngừng ghi cột cũ: bỏ cột chỉ sau khi bản deploy không còn tham chiếu nó đã
chạy ổn (mục 4).

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

## 6. Thêm khoá ngoại lên bảng đã có dữ liệu (có thể có dòng mồ côi)

```sql
SET lock_timeout = '5s';   -- ADD FOREIGN KEY giữ khoá ghi ngắn trên CẢ HAI bảng; không chờ khoá vô hạn
ALTER TABLE orders ADD CONSTRAINT fk_orders_warehouse
  FOREIGN KEY (warehouse_id) REFERENCES warehouses (id) NOT VALID;   -- bỏ qua quét dòng cũ

-- Dòng mồ côi: có warehouse_id nhưng bảng cha không có dòng tương ứng
SELECT o.id, o.warehouse_id
FROM orders o LEFT JOIN warehouses w ON w.id = o.warehouse_id
WHERE o.warehouse_id IS NOT NULL AND w.id IS NULL;

-- Sau khi dọn xong (migration dữ liệu riêng, mục 5):
ALTER TABLE orders VALIDATE CONSTRAINT fk_orders_warehouse;
CREATE INDEX CONCURRENTLY idx_orders_warehouse_id ON orders (warehouse_id);
```

- `NOT VALID` bỏ quét dòng cũ nhưng **vẫn kiểm mọi lần ghi sau đó**: dòng mới trỏ vào cha không tồn tại bị từ
  chối, nên báo đội ứng dụng trước khi thêm.
- `VALIDATE CONSTRAINT` quét cả bảng nhưng chỉ giữ khoá `SHARE UPDATE EXCLUSIVE` trên bảng con và `ROW SHARE`
  trên bảng cha (không chặn đọc/ghi thường) — khác với `ADD FOREIGN KEY` trực tiếp, vốn giữ `SHARE ROW
  EXCLUSIVE` suốt lúc quét.
- Dòng mồ côi là **quyết định nghiệp vụ**, không phải của migration: đặt `NULL` (nếu cột cho phép), trỏ về một
  bản ghi cha "không rõ", tạo lại bản ghi cha thiếu, hoặc xoá. Chốt với người dùng, rồi sửa bằng migration dữ
  liệu chia lô; ghi số dòng mồ côi trước và sau vào báo cáo.
- Postgres **không** tự tạo index trên cột khoá ngoại phía bảng con; thiếu nó thì mỗi lần xoá hay đổi dòng ở
  bảng cha quét cả bảng con. Dựng bằng `CONCURRENTLY` (mục 2).

## 7. Đổi kiểu cột khi dữ liệu có thể không hợp lệ (ví dụ `TEXT` → `JSONB`)

`ALTER COLUMN … TYPE` thường ghi lại cả bảng và giữ `ACCESS EXCLUSIVE`; một dòng không ép được kiểu làm cả
lệnh hỏng giữa chừng. Bảng lớn, ghi liên tục: không đổi tại chỗ, đi qua mở rộng → chuyển → thu hẹp
(`SKILL.md` mục 3) với cột mới `payload_jsonb`, và **đo số dòng hỏng trước khi viết backfill**:

```sql
-- PostgreSQL 16+: kiểm tra chuỗi có hợp lệ cho kiểu đích mà không ném lỗi
SELECT count(*) FROM events WHERE NOT pg_input_is_valid(payload, 'jsonb');
-- Bản cũ hơn: hàm bọc bắt lỗi ép kiểu
CREATE FUNCTION try_jsonb(t text) RETURNS jsonb LANGUAGE plpgsql IMMUTABLE AS $$
BEGIN RETURN t::jsonb; EXCEPTION WHEN others THEN RETURN NULL; END $$;
SELECT count(*) FROM events WHERE payload IS NOT NULL AND try_jsonb(payload) IS NULL;
```

- Xử lý dòng hỏng là **quyết định chốt với người dùng**: chép sang bảng cách ly kèm `id` (để sửa hoặc huỷ
  sau), để cột mới `NULL`, hoặc bọc nguyên chuỗi thành một giá trị JSON (`to_jsonb(payload)`). Không bỏ dòng
  hỏng đi mà không ghi lại.
- Backfill duyệt theo **khoá chính tăng dần** (`WHERE id > :last_id ORDER BY id LIMIT :batch`) rồi chỉ ép các
  dòng hợp lệ; đừng dùng `WHERE cột_mới IS NULL` làm điều kiện lặp — dòng hỏng không bao giờ được điền nên vòng
  lặp không kết thúc. Mẫu theo khoá chính: `django-golang-migrate.md` mục 1.
- Diễn tập (xem `rehearsal.md`) phải chạy trên bản sao có đúng dòng hỏng của production; tập dữ liệu sạch
  không chứng minh gì cho phần này.

## 8. Khôi phục sau một lệnh `UPDATE` sai

Nguyên tắc: **không sửa chồng lên dữ liệu sai bằng một `UPDATE` đoán mò**; dừng, xác định phạm vi, lấy lại giá
trị cũ từ nguồn đáng tin, rồi đưa về bằng migration dữ liệu.

1. Còn trong giao dịch chưa `COMMIT` → `ROLLBACK`, xong. Phòng từ đầu: chạy `UPDATE` hàng loạt trong `BEGIN`,
   so số dòng bị đổi với con số dự tính, chỉ `COMMIT` khi khớp.
2. Đã `COMMIT`: dừng ghi thêm vào bảng nếu có thể, ghi lại thời điểm và câu lệnh đã chạy, báo người dùng.
3. Có bản chụp trước khi sửa (`CREATE TABLE users_bak AS SELECT id, <cột sẽ đổi> FROM users WHERE <cùng điều
   kiện>` — việc nên làm trước mọi cập nhật hàng loạt) → lấy giá trị cũ từ đó.
4. Không có bản chụp → khôi phục theo thời điểm (point-in-time recovery: bản sao lưu gốc + WAL đã lưu, dừng ở
   `recovery_target_time` ngay trước lệnh sai) vào **một máy riêng**, không bao giờ khôi phục đè lên production;
   đọc giá trị cũ của các dòng bị đổi từ máy đó.
5. Đưa giá trị cũ về production bằng migration dữ liệu chia lô, idempotent (mục 5), chỉ sửa dòng mà giá trị hiện
   tại **vẫn bằng giá trị sai** do lệnh đó sinh ra — dòng người dùng đã sửa hợp lệ sau đó thì giữ nguyên.
6. Chạy trên dữ liệu thật là hành động không đảo ngược: runbook (phạm vi, câu lệnh, cách kiểm) trình người dùng
   gật trước. Kiểm sau cùng: số dòng và tổng kiểm trên cột liên quan khớp với bản cũ.

## 9. Thêm unique index khi dữ liệu có thể đã trùng

Dựng unique index trên bảng đã có dữ liệu mà có dòng trùng thì **thất bại** — và nếu dùng `CONCURRENTLY` thì để lại index
`INVALID` (mục 2). Thứ tự: tìm trùng → quyết giữ/bỏ → dọn → chặn trùng mới → dựng index → kiểm hợp lệ.

1. **Tìm và đo.** Chuẩn hoá đúng cách unique sẽ so (ví dụ không phân biệt hoa thường thì so `lower(email)`; khoảng trắng
   thừa; `NULL` — mặc định Postgres coi các `NULL` là khác nhau nên không đụng unique, muốn coi `NULL` là trùng thì
   `NULLS NOT DISTINCT` ở bản có hỗ trợ):

```sql
SELECT lower(email) AS email_chuan, count(*) AS so_dong, min(id) AS id_nho_nhat, max(id) AS id_lon_nhat
FROM users GROUP BY lower(email) HAVING count(*) > 1 ORDER BY so_dong DESC;
```

2. **Chọn dòng giữ — quyết định nghiệp vụ**, không phải của migration (như dòng mồ côi ở mục 6): thường giữ dòng mới cập nhật nhất
   (hoặc đầy đủ nhất), nhưng hai dòng có thể mang dữ liệu khác nhau (đơn hàng gắn vào cả hai, hồ sơ khác nhau). Chốt quy tắc với
   chủ dữ liệu trước; dòng cần **gộp** (không chỉ xoá) thì chuyển bảng con trỏ vào dòng bị bỏ sang dòng giữ trước khi xoá.
3. **Lưu bản sao rồi mới xoá:**

```sql
CREATE TABLE users_dedup_removed AS            -- bản lưu dòng bị bỏ, để khôi phục nếu quy tắc sai
SELECT u.* FROM users u
WHERE u.id IN (SELECT id FROM (SELECT id, row_number() OVER (PARTITION BY lower(email) ORDER BY updated_at DESC, id) AS rn
                                FROM users) r WHERE r.rn > 1);
-- xoá theo lô (mục 5), từng lô kiểm số dòng bị xoá bằng số dòng đã dự tính
DELETE FROM users WHERE id IN (SELECT id FROM users_dedup_removed WHERE id > :last_id ORDER BY id LIMIT 5000);
```

   (mẫu `row_number()` đã chạy thử trên SQLite — logic chọn dòng giữ: cùng nhóm, `updated_at` mới nhất, hoà thì `id` nhỏ nhất.)
4. **Chặn trùng mới trước hoặc song song:** nếu ứng dụng vẫn ghi trùng được thì dọn xong trùng lại xuất hiện. Đưa ứng dụng
   sang cách ghi chuẩn hoá (`INSERT … ON CONFLICT`, `lower()` khi lưu) **trước** khi dựng index; tài liệu Postgres cảnh báo khi dựng
   unique index đồng thời, ràng buộc đã có hiệu lực với giao dịch khác từ lượt quét thứ hai — vi phạm có thể báo ở truy vấn
   khác ngay cả khi dựng cuối cùng thất bại.
5. **Dựng index đồng thời:**

```sql
SET lock_timeout = '5s';
CREATE UNIQUE INDEX CONCURRENTLY uq_users_email_lower ON users (lower(email));
-- kiểm hợp lệ: không được còn index INVALID
SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
-- INVALID → DROP INDEX CONCURRENTLY uq_users_email_lower; dọn nốt dòng trùng còn sót; dựng lại (hoặc REINDEX INDEX CONCURRENTLY)
```

6. **Muốn thành ràng buộc `UNIQUE`** (ví dụ để làm đích cho khoá ngoại): dựng index trước rồi gắn —
   `ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE USING INDEX uq_users_email_lower;` — thao tác nhanh, không chặn
   ghi lâu (tài liệu Postgres dùng đúng cách này). Điều kiện: index unique, b-tree thường, **không** một phần (`WHERE`) và
   **không** biểu thức (`lower(...)`) — index theo biểu thức giữ nguyên là index unique, không gắn được thành ràng buộc; muốn
   ràng buộc thì lưu cột đã chuẩn hoá (cột sinh sẵn hay lưu sẵn chữ thường) rồi đánh index trên cột đó.
7. Trong Alembic: tách thành các revision (dọn dữ liệu, rồi dựng index trong khối autocommit như mục 4 của `SKILL.md` với
   `unique=True, postgresql_concurrently=True`); `downgrade` chỉ `DROP INDEX`, **không** khôi phục dòng đã xoá (dùng
   bảng lưu ở bước 3). Bảng lưu giữ đến khi hết cửa sổ khôi phục đã thoả thuận rồi mới bỏ (migration riêng).

Nguồn: tài liệu PostgreSQL (`CREATE INDEX` — mục CONCURRENTLY: hai lượt quét, index `INVALID` khi thất bại, lưu ý unique;
`ALTER TABLE` — `ADD table_constraint_using_index`). Câu chọn dòng giữ đã chạy thử logic trên SQLite; các lệnh `CONCURRENTLY`
chưa chạy trên Postgres thật trong lượt này.
