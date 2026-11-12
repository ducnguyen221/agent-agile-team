# PostgreSQL: phân vùng, tìm chuỗi con, RLS nhiều tenant, đua dữ liệu, hàng đợi bền, đổi `timestamp`

> **Kết luận:** sáu việc mà `SKILL.md` chỉ chạm nguyên tắc: (1) bảng chuỗi thời gian lớn → **phân vùng theo khoảng** và dọn dữ liệu cũ
> bằng bỏ/tách phân vùng, không `DELETE` hàng loạt; (2) tìm chuỗi con `LIKE '%…%'` → `pg_trgm` + GIN; (3) RLS nhiều tenant với một role chung →
> truyền tenant vào **giao dịch** bằng `set_config(…, true)`, role ứng dụng **không** là chủ bảng, không superuser, không `BYPASSRLS`;
> (4) "đọc-kiểm-ghi" là đua dữ liệu → câu `UPDATE … WHERE` nguyên tử, khoá dòng, hoặc ràng buộc; (5) hàng đợi bằng `SKIP LOCKED`
> cần **thuê hết hạn** để cứu việc kẹt khi worker chết; (6) đổi `timestamp` sang `timestamptz` phải biết múi giờ đã dùng khi ghi. Mọi lệnh đổi
> schema trên bảng thật đi theo `database-migrations`.

Nguồn: tài liệu PostgreSQL (`postgresql.org/docs/current`: Table Partitioning, `pg_trgm`, Row Security Policies, Transaction Isolation,
Explicit Locking / `SELECT … FOR UPDATE … SKIP LOCKED`, `ALTER TABLE`).

## 1. Chia bảng theo thời gian và dọn dữ liệu cũ

Bảng nhật ký/sự kiện/đo lường tăng không ngừng, truy vấn gần như luôn có điều kiện thời gian, và dữ liệu cũ phải xoá theo lịch: dùng
**phân vùng khai báo theo khoảng**.

```sql
CREATE TABLE events (
  id bigint GENERATED ALWAYS AS IDENTITY,
  occurred_at timestamptz NOT NULL,
  payload jsonb,
  PRIMARY KEY (id, occurred_at)                  -- khoá chính / unique PHẢI chứa cột phân vùng
) PARTITION BY RANGE (occurred_at);

CREATE TABLE events_2026_10 PARTITION OF events
  FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');   -- cận dưới gồm, cận trên không gồm
CREATE INDEX ON events (occurred_at);                  -- tạo trên bảng cha, áp cho mọi phân vùng
```

- **Dọn dữ liệu cũ:** `DROP TABLE events_2026_01;` hoặc `ALTER TABLE events DETACH PARTITION events_2026_01 CONCURRENTLY;` (rồi lưu/xoá bảng
  vừa tách) gần như tức thì, không sinh dòng chết, không cần `VACUUM`. `DELETE FROM events WHERE occurred_at < …` xoá từng dòng, tạo bão dòng chết,
  ghi WAL lớn và phình bảng.
- Truy vấn có điều kiện trên cột phân vùng được **cắt tỉa** (chỉ quét phân vùng liên quan): kiểm bằng `EXPLAIN`. Điều kiện không dính cột phân vùng thì quét hết.
- Tạo phân vùng của các tháng tới **trước** bằng việc định kỳ (hoặc `pg_partman`); không để dòng rơi vào khoảng chưa có phân vùng (lỗi chèn). Phân vùng
  `DEFAULT` hứng dòng lạc nhưng làm `ATTACH` phải quét nó: thêm `CHECK` khớp trước khi gắn.
- Giới hạn: khoá chính và ràng buộc unique phải **chứa** cột phân vùng (không có unique toàn cục chỉ trên `id`); khoá ngoại tới hoặc từ bảng phân vùng: đối chiếu tài liệu của bản đang dùng;
  đừng chia quá nhiều (hàng nghìn phân vùng làm tốn thời gian lập kế hoạch và bộ nhớ): theo tháng hoặc tuần là đủ cho đa số.
- Khi nào **không**: bảng vài triệu dòng chạy ổn với index đúng (`SKILL.md` mục 2, BRIN cho dữ liệu chèn theo thứ tự); thêm phân vùng là thêm việc vận hành.
  Chuyển bảng đang chạy sang phân vùng là migration lớn: bảng mới + chuyển dữ liệu theo lô (`database-migrations`), có diễn tập.

## 2. Tìm chuỗi con: `LIKE '%…%'`, `ILIKE`, bỏ dấu

B-tree **không** giúp `LIKE '%abc%'` (không neo đầu), nên truy vấn quét cả bảng. Dùng `pg_trgm`:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_products_name_trgm ON products USING gin (name gin_trgm_ops);
-- phục vụ: WHERE name ILIKE '%tai nghe%'  /  WHERE name LIKE '%x%'  /  name % 'tai ngh' (gần giống)
```

- GIN trigram tăng tốc `LIKE`, `ILIKE`, `~`, `~*` và toán tử tương tự (`%`, `<%`); GiST (`gist_trgm_ops`) nhỏ hơn nhưng chậm hơn khi tìm, hợp với sắp xếp theo khoảng cách.
  Chuỗi tìm **dưới 3 ký tự** gần như không có trigram để lọc nên index kém hiệu quả: chặn hoặc yêu cầu tối thiểu 3 ký tự ở giao diện.
- Index GIN lớn và làm chậm ghi (`SKILL.md` mục 2: mỗi index có giá); chỉ lập cho cột thật sự tìm theo chuỗi con.
- **Không phân biệt hoa thường:** `ILIKE` đã dùng được index trigram; so bằng trọn chuỗi thì index biểu thức `CREATE INDEX ON users (lower(email))` và truy vấn `WHERE lower(email) = lower($1)` (phải
  **đúng biểu thức** của index); hoặc kiểu `citext`.
- **Bỏ dấu tiếng Việt:** extension `unaccent`. Hàm `unaccent()` không được đánh dấu bất biến (`IMMUTABLE`) nên không đặt thẳng vào index biểu thức; cách thường dùng là bọc trong hàm SQL
  `IMMUTABLE` riêng (`CREATE FUNCTION f_unaccent(text) RETURNS text AS $$ SELECT public.unaccent('public.unaccent', $1) $$ LANGUAGE sql IMMUTABLE`) rồi index
  `gin (f_unaccent(name) gin_trgm_ops)` và truy vấn dùng đúng `f_unaccent(name) ILIKE f_unaccent($1)`. Đây là **lời hứa** hàm không đổi kết quả: nếu đổi từ điển `unaccent` phải
  `REINDEX`. Cách khác: lưu thêm cột đã chuẩn hoá bỏ dấu (sinh sẵn) rồi index cột đó.
- Tiền tố (`LIKE 'abc%'`): nếu cơ sở dữ liệu không dùng bộ so sánh `C`, index B-tree cần lớp toán tử `text_pattern_ops` thì mới giúp được.
- Tìm toàn văn theo từ (tách từ, xếp hạng) là việc của `tsvector` + GIN (`SKILL.md` mục 2); trigram dành cho **chuỗi con và gần đúng**. Dữ liệu lớn cần tìm kiếm phức tạp: cân nhắc công cụ chuyên (ADR).

## 3. RLS nhiều tenant với một role ứng dụng chung

Mô hình: một role `app` kết nối, nhiều tenant, mọi bảng có `tenant_id`. Tenant của yêu cầu hiện tại truyền vào **giao dịch**, policy đọc nó.

```sql
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices FORCE ROW LEVEL SECURITY;     -- ép cả chủ bảng cũng bị policy chi phối
CREATE POLICY tenant_isolation ON invoices
  USING      (tenant_id = (SELECT current_setting('app.tenant_id', true)::uuid))
  WITH CHECK (tenant_id = (SELECT current_setting('app.tenant_id', true)::uuid));
CREATE INDEX ON invoices (tenant_id);              -- cột trong policy phải có index
```

```sql
BEGIN;
SELECT set_config('app.tenant_id', $1, true);      -- true = chỉ trong giao dịch này (như SET LOCAL, nhưng tham số hoá được)
-- ... các truy vấn của yêu cầu ...
COMMIT;
```

- **Truyền tenant vào phiên bằng cấu hình cục bộ giao dịch** (`SET LOCAL` hoặc `set_config(..., true)`), **không** `SET` mức phiên: kết nối nằm trong pool, `SET` mức phiên rò tenant
  của yêu cầu trước sang yêu cầu sau; PgBouncer chế độ `transaction` còn trộn kết nối giữa các client (`references/diagnostics.md` mục 3.2).
- `current_setting('app.tenant_id', true)`: đối số `true` trả `NULL` khi chưa đặt thay vì lỗi; so sánh với `NULL` cho 0 dòng, nên quên đặt tenant là **thấy trống**, không lộ dữ liệu.
  Bọc trong `(SELECT ...)` để tính một lần mỗi câu lệnh (`SKILL.md` mục 5). Giá trị lấy từ phiên xác thực của server, **không** từ đầu vào client.
- **Ai bỏ qua RLS:** **superuser** và role có thuộc tính `BYPASSRLS` luôn bỏ qua; **chủ bảng** bỏ qua trừ khi bảng `FORCE ROW LEVEL SECURITY`. Do đó role `app` **không** là
  superuser, không `BYPASSRLS`, và tốt nhất không là chủ bảng (migration chạy bằng role chủ bảng khác). Kiểm bằng `SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = 'app';`.
- Chưa có policy mà đã bật RLS: mặc định **từ chối hết** (an toàn). `USING` lọc dòng đọc/sửa/xoá; `WITH CHECK` chặn **ghi** dòng sai tenant (thiếu thì mặc định bằng `USING`).
- Không bị RLS lọc: ràng buộc khoá chính/unique/khoá ngoại (chạy bỏ qua RLS, có thể lộ "tồn tại" qua lỗi trùng khoá), và **view** chạy với quyền chủ view
  (PostgreSQL 15+: `CREATE VIEW ... WITH (security_invoker = true)` để view theo quyền người gọi). Hàm `SECURITY DEFINER` cũng chạy với quyền chủ.
- Kiểm bằng test hai tenant: tenant A không đọc/sửa/xoá dòng của B; không đặt tenant → 0 dòng; chèn dòng với `tenant_id` của B bị `WITH CHECK` từ chối; chạy test bằng **chính role `app`**,
  không bằng superuser (superuser luôn "đạt" và che lỗi). Chạm RLS là kéo `security-reviewer`.
- Chi phí: policy thêm điều kiện vào mọi câu lệnh; index theo `tenant_id` đứng đầu cột trong index ghép thường dùng; đo bằng `EXPLAIN`.

## 4. Đua dữ liệu kiểu đọc-kiểm-ghi

Mẫu hỏng: `SELECT` kiểm điều kiện (còn tồn kho, chưa có bản ghi trùng, số dư đủ) rồi `UPDATE`/`INSERT` ở câu sau. Hai giao dịch đồng thời cùng qua phép kiểm. Ở mức cô lập mặc định
**Read Committed**, hai câu tách rời **không** chống được "cập nhật bị mất". Bốn cách, từ nên dùng trước:

| Cách | Làm gì | Khi nào |
|---|---|---|
| **Câu lệnh nguyên tử** | gộp kiểm và ghi: `UPDATE stock SET qty = qty - 1 WHERE id = $1 AND qty > 0` rồi kiểm số dòng bị đổi (0 = hết hàng) | trừ tồn, tăng bộ đếm, đổi trạng thái có điều kiện |
| **Ràng buộc** trong CSDL | `UNIQUE`, `CHECK (qty >= 0)`, `EXCLUDE`; bắt lỗi vi phạm; `INSERT ... ON CONFLICT` | "chỉ một", "không âm", "không chồng lấn" |
| **Khoá dòng** | `SELECT ... FOR UPDATE` trong giao dịch, rồi kiểm và ghi (người sau chờ người trước) | quy tắc nhiều bước không gói được vào một câu |
| **Mức cô lập cao hơn** | `REPEATABLE READ`/`SERIALIZABLE`; xung đột báo lỗi `40001` | quy tắc phức tạp liên quan nhiều dòng; **phải** thử lại cả giao dịch từ đầu |

- Ở Read Committed, `UPDATE`/`FOR UPDATE` đang chờ dòng bị giao dịch khác đổi sẽ **kiểm lại điều kiện `WHERE`** trên bản mới sau khi nhận khoá; đó là lý do câu nguyên tử ở hàng đầu đúng, còn
  `SELECT` thường rồi ghi thì sai.
- Khoá dòng giữ **trong giao dịch ngắn** (không qua lời gọi API ngoài) và theo thứ tự nhất quán (`SKILL.md` mục 4). `FOR UPDATE` chỉ khoá dòng **đã tồn tại**; kiểm "chưa có bản ghi" nên dùng ràng buộc unique
  (không có dòng để khoá).
- Mức cô lập cao: bắt lỗi `40001` (và `40P01` deadlock) và thử lại **toàn bộ** giao dịch, có trần số lần và độ trễ ngẫu nhiên tăng dần; giao dịch có tác dụng ngoài (gửi mail) không được thử lại mù (`error-handling`).
- Khoá lạc quan ở tầng ứng dụng/API (cột `version`, `If-Match`): xem `api-design` `references/retries-concurrency-files.md` mục 2.
- Kiểm bằng test song song thật (hai kết nối, hai giao dịch xen kẽ), không bằng test tuần tự: test tuần tự không bao giờ bắt được đua.

## 5. Hàng đợi bền: worker chết giữa chừng, lấy theo lô

`FOR UPDATE SKIP LOCKED` (`SKILL.md` mục 4) lấy việc không tranh nhau, nhưng câu lệnh mẫu **đổi trạng thái sang `processing` rồi commit**: nếu worker chết sau đó, việc kẹt ở `processing` mãi.
Thêm **thuê hết hạn** và đếm lần thử:

```sql
-- cột: status, locked_by, lease_expires_at, attempts, run_after
WITH picked AS (
  SELECT id FROM jobs
  WHERE status = 'pending' AND run_after <= now()
  ORDER BY run_after, id
  LIMIT 10                                           -- lấy theo lô
  FOR UPDATE SKIP LOCKED
)
UPDATE jobs j SET status = 'processing', locked_by = $1,
       lease_expires_at = now() + interval '5 minutes', attempts = attempts + 1
FROM picked WHERE j.id = picked.id
RETURNING j.*;

-- người dọn (chạy định kỳ): trả việc hết thuê về hàng đợi, hoặc sang trạng thái chết sau quá nhiều lần
UPDATE jobs SET status = CASE WHEN attempts >= 5 THEN 'dead' ELSE 'pending' END, locked_by = NULL
WHERE status = 'processing' AND lease_expires_at < now();

-- worker xong: chỉ ghi nếu còn là chủ thuê
UPDATE jobs SET status = 'done' WHERE id = $1 AND locked_by = $2 AND status = 'processing';
```

- Thuê dài hơn thời gian xử lý bình thường; việc dài phải **gia hạn** (cập nhật `lease_expires_at` định kỳ). Worker xong sau khi thuê hết hạn (đã có người khác nhặt) sẽ thấy 0 dòng ở câu cuối
  (`locked_by` không còn khớp): bỏ kết quả, không ghi đè.
- **Xử lý phải idempotent**: việc có thể chạy hai lần (worker chết sau khi làm xong, trước khi ghi `done`). Dùng khoá chống trùng cho tác dụng ngoài (`api-design`, `references/retries-concurrency-files.md` mục 1: `Idempotency-Key`), hoặc
  ghi kết quả và đổi trạng thái trong **một giao dịch**.
- Cách khác: giữ **một giao dịch mở** suốt lúc xử lý (`SKIP LOCKED` giữ khoá dòng; worker chết thì giao dịch tự huỷ và khoá nhả). Đơn giản hơn, nhưng giữ kết nối và khoá cả lúc xử lý, vướng
  `idle_in_transaction_session_timeout`, không hợp việc dài; chỉ cho việc ngắn.
- Index một phần cho hàng đợi: `CREATE INDEX ON jobs (run_after, id) WHERE status = 'pending'` (`SKILL.md` mục 2). Dọn bảng `done` cũ theo lịch (hoặc phân vùng, mục 1).
- `SKIP LOCKED` cho "cái nhìn không nhất quán" của bảng: hợp hàng đợi, **không** dùng cho truy vấn thường.
- Hàng đợi nặng (hàng nghìn việc mỗi giây, định tuyến, lịch trễ phức tạp) nên dùng công cụ chuyên (ADR) thay vì tự dựng thêm.

## 6. Đổi `timestamp` sang `timestamptz` (dữ liệu từ nhiều múi giờ)

`timestamp` (không múi giờ) lưu giờ **trần**, không biết nó là giờ nào; `timestamptz` lưu thời điểm tuyệt đối (UTC) và hiển thị theo múi giờ phiên. Đổi kiểu **phải khai** múi giờ mà các giá trị cũ đã được ghi:

```sql
ALTER TABLE orders
  ALTER COLUMN created_at TYPE timestamptz USING created_at AT TIME ZONE 'UTC';
```

- `USING col AT TIME ZONE 'X'` diễn giải giờ trần là giờ vùng `X` (ở đây UTC). **Sai múi giờ = dữ liệu lệch im lặng** (lệch 7 giờ không báo lỗi). Trước khi đổi, xác định **mỗi nguồn ghi**
  (dịch vụ, tác vụ nhập, script) đã ghi theo múi giờ nào: nếu `now()` trên máy chủ cơ sở dữ liệu thì theo `TimeZone` của phiên lúc đó; nếu ứng dụng gửi giờ địa phương thì theo múi của ứng dụng.
  Nhiều nguồn khác múi: không đổi bằng một câu cho cả bảng; phân theo nguồn hoặc khoảng thời gian (cột nguồn, mốc ngày chuyển), hoặc lấy mẫu đối chiếu với giờ thật đã biết.
- Giờ địa phương có chuyển mùa (giờ mùa hè) làm một giờ bị trùng hoặc không tồn tại: giờ trần trong khoảng đó mơ hồ. Múi cố định như `Asia/Ho_Chi_Minh` (UTC+7, không chuyển mùa) đơn giản hơn.
- Bảng thật: `ALTER ... TYPE` giữ khoá `ACCESS EXCLUSIVE` và có thể viết lại cả bảng (PostgreSQL 12 trở lên có thể bỏ qua việc viết lại khi múi giờ phiên là UTC: kiểm bản đang dùng). Làm theo
  `database-migrations`: cột mới `timestamptz`, ghi cả hai, backfill theo lô, kiểm số dòng lệch, chuyển đọc, bỏ cột cũ; chạy diễn tập trên bản sao.
- Sau khi đổi: đặt `TimeZone` của phiên/ứng dụng rõ ràng; truy vấn "theo ngày" dùng `AT TIME ZONE` đúng múi người dùng; ứng dụng gửi và nhận **ISO 8601 có phần bù**, không giờ trần.

## 7. Tìm toàn văn: cột `tsvector` — cột sinh hay trigger

Tìm theo **từ** (có xếp hạng) dùng `tsvector` + GIN; khác `pg_trgm` ở mục 2 (chuỗi con, gõ sai gần đúng).

- **Mặc định: cột sinh (PostgreSQL 12 trở lên)** — cột lưu, tự cập nhật theo cột nguồn, không cần mã thêm:

```sql
ALTER TABLE docs ADD COLUMN tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('simple', f_unaccent(coalesce(title, '') || ' ' || coalesce(body, '')))) STORED;
CREATE INDEX docs_tsv_idx ON docs USING gin (tsv);

SELECT id FROM docs
WHERE tsv @@ websearch_to_tsquery('simple', f_unaccent($1))
ORDER BY ts_rank(tsv, websearch_to_tsquery('simple', f_unaccent($1))) DESC LIMIT 20;
```

  Biểu thức của cột sinh bắt buộc **immutable**: dùng hàm bọc `f_unaccent` ở mục 2 (`unaccent` gốc chỉ STABLE nên bị từ chối), và luôn truyền tên cấu hình văn bản (`'simple'`, `'english'`) vì `to_tsvector(text)` không cấu hình phụ thuộc cài đặt phiên.
- **Dùng trigger khi:** bản dưới 12; giá trị cần dữ liệu từ bảng khác hoặc hàm không immutable.

```sql
CREATE FUNCTION docs_tsv_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.tsv := to_tsvector('simple', f_unaccent(coalesce(NEW.title, '') || ' ' || coalesce(NEW.body, '')));
  RETURN NEW;
END $$;
CREATE TRIGGER docs_tsv BEFORE INSERT OR UPDATE OF title, body ON docs
  FOR EACH ROW EXECUTE FUNCTION docs_tsv_update();
```

  Trigger không tự điền dòng có sẵn: backfill theo lô (`database-migrations`).
- Thêm cột sinh `STORED` vào bảng đang có dữ liệu **viết lại cả bảng** dưới khoá nặng: trên bảng thật làm theo `database-migrations` (cột thường + trigger + backfill, rồi đổi sau).
- `websearch_to_tsquery` nhận cú pháp người dùng gõ (cụm trong nháy, `-từ`, `or`) mà không ném lỗi cú pháp; `to_tsquery` thì ném lỗi với đầu vào thô.

## 8. View vật chất hoá: kết quả tính nặng, chấp nhận cũ một lúc

- Dùng khi truy vấn tổng hợp nặng được **đọc nhiều hơn số lần dữ liệu đổi** và đọc cũ vài phút hay vài giờ chấp nhận được (báo cáo, bảng xếp hạng). Cần số liệu tức thời thì không dùng: index đúng, bảng tóm tắt do ứng dụng cập nhật, hoặc truy vấn trực tiếp.
- View vật chất hoá **không tự cập nhật**: nó lưu kết quả lúc tạo hoặc lúc làm mới gần nhất.

```sql
CREATE MATERIALIZED VIEW sales_daily AS
  SELECT date_trunc('day', created_at) AS day, sum(total) AS revenue
  FROM orders GROUP BY 1
  WITH NO DATA;
CREATE UNIQUE INDEX sales_daily_day ON sales_daily (day);
REFRESH MATERIALIZED VIEW sales_daily;                -- lần đầu: bắt buộc dạng thường
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_daily;   -- các lần sau: không chặn đọc
```

- `REFRESH` thường khoá `ACCESS EXCLUSIVE`: **chặn mọi đọc** trong lúc làm mới. `CONCURRENTLY` không chặn đọc nhưng cần ít nhất một index **unique** (chỉ trên tên cột, không có `WHERE`) trên view, chỉ dùng khi view đã có dữ liệu, và chậm hơn (tính lại rồi so với bản cũ).
- Lịch làm mới bằng `pg_cron` hoặc job ngoài; ghi thời điểm làm mới gần nhất để hiển thị độ cũ; theo dõi thời gian làm mới vì mỗi lần nó chạy lại **toàn bộ** truy vấn. Dữ liệu lớn tăng nhanh mà làm mới quá chậm: xét bảng tóm tắt cập nhật tăng dần.
- Index trên view vật chất hoá tạo như bảng thường (mục 2 của `SKILL.md`).

## 9. Số thứ tự liên tục (không lỗ hổng) và vì sao sequence có lỗ hổng

- `sequence`, `identity`, `serial` **không bảo đảm liên tục**: `nextval` không nằm trong giao dịch, nên giao dịch rollback, lỗi vi phạm ràng buộc khi chèn, `INSERT … ON CONFLICT` không chèn, hay máy chủ sập đều "đốt" số đã cấp. Tốt cho khoá chính; sai cho số mà luật đòi liên tục (số hoá đơn theo năm).
- **Bộ đếm liên tục theo năm** (hoặc theo chuỗi): một dòng bộ đếm cho mỗi khoá, tăng **trong cùng giao dịch** với hàng cần số:

```sql
CREATE TABLE invoice_counters (year int PRIMARY KEY, last_no int NOT NULL);
-- trong giao dịch tạo hoá đơn:
INSERT INTO invoice_counters (year, last_no) VALUES ($1, 1)
  ON CONFLICT (year) DO UPDATE SET last_no = invoice_counters.last_no + 1
  RETURNING last_no;
INSERT INTO invoices (year, no, ...) VALUES ($1, <last_no>, ...);   -- UNIQUE (year, no)
```

  Giao dịch rollback thì cả hai thay đổi cùng huỷ — không để lại lỗ hổng.
- **Cái giá đồng thời:** cập nhật cùng một dòng bộ đếm khoá dòng đó tới hết giao dịch, nên các giao dịch tạo hoá đơn **cùng năm xếp hàng**; thông lượng bị giới hạn bởi độ dài giao dịch. Giữ giao dịch ngắn (không gọi API ngoài, không chờ người dùng), cấp số ở **bước cuối** của giao dịch hoặc ở bước "phát hành" riêng thay vì lúc tạo nháp; cần thông lượng cao hơn thì tách bộ đếm theo khoá (chi nhánh, ngày) nếu luật cho phép.
- Không suy số tiếp theo bằng `max(no) + 1` hay `count(*) + 1`: hai giao dịch cùng đọc ra một số — đua đọc-kiểm-ghi ở mục 4.
