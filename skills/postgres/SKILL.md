---
name: postgres
description: Use when writing PostgreSQL queries or migrations, designing tables, columns, or indexes, choosing data types, troubleshooting a slow query or table bloat, implementing Row Level Security, paginating large tables, building a job queue on Postgres, or setting connection and timeout settings.
metadata:
  group: technique
  kind: reference
  roles: [implementer, tech-reviewer]
source: [affaan-m/ECC skills/postgres-patterns/SKILL.md, affaan-m/ECC agents/database-reviewer.md]
source_sha: [ef648e01899ba3e8dc6371642deaaf64b4477775, ef648e01899ba3e8dc6371642deaaf64b4477775]
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: [MIT, MIT]
rewrite_before_public: false
---

# PostgreSQL — tra nhanh

> **Kết luận:** chọn index theo **dạng điều kiện** của truy vấn thật (bằng và khoảng → B-tree, cột so bằng
> đứng trước trong index ghép; JSONB, full-text → GIN; bảng chuỗi thời gian rất lớn → BRIN), và mọi khoá
> ngoại có index. Kiểu dữ liệu đúng ngay từ đầu (`bigint`, `text`, `timestamptz`, `numeric`), ràng buộc đặt
> trong CSDL. Giao dịch ngắn, khoá theo thứ tự nhất quán; phân trang bằng con trỏ; hàng đợi bằng
> `FOR UPDATE SKIP LOCKED`; mọi kết nối có timeout. Không kết luận "chậm ở đâu" khi chưa đọc `EXPLAIN`.

## 1. Khi nào dùng — và khi nào sang chỗ khác

- Viết truy vấn, thiết kế bảng, cột, index; truy vấn chậm, bảng phình; Row Level Security; pool và timeout.
- Đổi schema trên dữ liệu thật (thứ tự bước, khoá, backfill, diễn tập) → skill `database-migrations`.
- Review độc lập SQL, schema, quyền → agent `database-reviewer`; truy cập CSDL từ FastAPI → skill `fastapi`.

## 2. Chọn index

| Dạng truy vấn | Loại index | Ví dụ |
|---|---|---|
| `WHERE col = value`, `WHERE col > value`, `ORDER BY col` | B-tree (mặc định) | `CREATE INDEX idx ON t (col)` |
| `WHERE a = x AND b > y` | ghép, cột so bằng trước | `CREATE INDEX idx ON t (a, b)` |
| `WHERE jsonb @> '{}'`, `WHERE tsv @@ query` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| khoảng thời gian trên bảng chuỗi thời gian chèn theo thứ tự | BRIN | `CREATE INDEX idx ON t USING brin (col)` |
| chỉ đọc vài cột | bao phủ | `CREATE INDEX idx ON t (email) INCLUDE (name)` |
| chỉ một phần dòng được truy vấn (xoá mềm, trạng thái) | một phần | `CREATE INDEX idx ON t (email) WHERE deleted_at IS NULL` |

- Mỗi khoá ngoại có index ở phía tham chiếu — không có thì `JOIN` và xoá dòng cha phải quét cả bảng con.
- Cột dùng trong policy RLS có index.
- Index có giá: mỗi lần ghi phải cập nhật mọi index. Index không được dùng (`idx_scan` gần 0 sau một chu kỳ
  tải thật) là ứng viên bỏ — kiểm ở `references/diagnostics.md`.
- Tạo index trên bảng đang phục vụ: `CREATE INDEX CONCURRENTLY`, ngoài transaction, theo skill
  `database-migrations`.

## 3. Kiểu dữ liệu và ràng buộc

| Dùng cho | Kiểu đúng | Tránh |
|---|---|---|
| Khoá chính | `bigint` identity, hoặc UUIDv7 khi cần sinh ở phía ứng dụng | `int` (tràn), UUID ngẫu nhiên (index phân mảnh) |
| Chuỗi | `text`, giới hạn bằng `CHECK` khi có luật nghiệp vụ | `varchar(255)` tuỳ tiện |
| Thời điểm | `timestamptz` | `timestamp` không múi giờ |
| Tiền | `numeric(p, s)` | `float`, `real` |
| Cờ | `boolean` | `varchar`, `int` |

- Ràng buộc nằm trong CSDL, không chỉ trong code: khoá chính, khoá ngoại có `ON DELETE` chọn có chủ đích,
  `NOT NULL`, `UNIQUE`, `CHECK`. Ứng dụng kiểm trước rồi chèn là đua — ràng buộc mới là chốt cuối.
- Định danh `lowercase_snake_case`, không tên hoa thường lẫn lộn trong nháy kép.

## 4. Truy vấn và đồng thời

- Chọn đúng cột cần, không `SELECT *` trong code chạy thật. Truy vấn luôn tham số hoá.
- **Phân trang con trỏ:** `WHERE id > $1 ORDER BY id LIMIT 20` nhảy thẳng qua index; `OFFSET` lớn phải đọc
  rồi bỏ mọi dòng phía trước.
- **Chèn theo lô:** `INSERT` nhiều dòng hoặc `COPY`; không chèn từng dòng trong vòng lặp.
- **UPSERT:** `INSERT … ON CONFLICT (khoá) DO UPDATE SET col = EXCLUDED.col` — cần ràng buộc unique khớp khoá.
- **Giao dịch ngắn:** không giữ khoá trong lúc gọi API ngoài hay chờ người dùng; đặt
  `idle_in_transaction_session_timeout` để giao dịch bỏ dở không giữ khoá mãi.
- **Thứ tự khoá nhất quán:** cập nhật nhiều dòng thì khoá theo cùng thứ tự (`ORDER BY id FOR UPDATE`) để
  không deadlock.
- **Hàng đợi việc:** worker lấy việc bằng `FOR UPDATE SKIP LOCKED` để không tranh cùng dòng:

```sql
UPDATE jobs SET status = 'processing'
WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1
  FOR UPDATE SKIP LOCKED
) RETURNING *;
```

## 5. Bảo mật

- Bảng nhiều tenant bật Row Level Security; policy gọi hàm thì bọc trong `SELECT` để tính **một lần** mỗi câu
  lệnh, không mỗi dòng — ví dụ theo Supabase: `USING ((SELECT auth.uid()) = user_id)`.
- Quyền tối thiểu: tài khoản ứng dụng không phải chủ bảng, không `GRANT ALL`; thu hồi quyền mặc định trên
  schema `public`.
- Chuỗi kết nối đọc từ biến môi trường, không in ra log hay báo cáo. Chạm RLS, quyền, dữ liệu nhạy cảm → kéo
  agent `security-reviewer`.

## 6. Lỗi hay gặp khi viết và review

Mức gợi ý theo hậu quả nếu bỏ qua (`method/severity.md` mục 1).

| Dấu hiệu | Hậu quả | Mức gợi ý |
|---|---|---|
| SQL ghép chuỗi với đầu vào ngoài | SQL injection | Chặn |
| Bảng nhiều tenant không RLS hay không lọc theo tenant | dữ liệu tenant này lộ sang tenant khác | Chặn |
| Tiền lưu bằng số thực; thiếu ràng buộc làm dữ liệu sai lọt vào | sai tiền, dữ liệu hỏng âm thầm | Phải sửa |
| Seq scan bảng lớn ở đường găng; N+1 truy vấn | ổn lúc thử, sập khi tải tăng | Phải sửa |
| Khoá ngoại không index | `JOIN` chậm, xoá dòng cha khoá bảng con lâu | Phải sửa |
| Giao dịch giữ khoá qua lời gọi ngoài; khoá không cùng thứ tự | chờ khoá dây chuyền, deadlock | Phải sửa |
| Kết nối không `statement_timeout` hay giới hạn pool | một truy vấn hỏng ăn hết kết nối | Phải sửa |
| `OFFSET` lớn trên bảng lớn | trang càng sau càng chậm | Nên sửa |
| `int` cho khoá chính đang lớn, `timestamp` không múi giờ, `varchar(255)` vô cớ | tràn số về sau, lệch giờ, đổi kiểu tốn khoá bảng | Nên sửa (Phải sửa khi bảng đã gần trần `int`) |
| `SELECT *` trong code chạy thật | thêm cột là đổi hành vi, đọc thừa | Nên sửa |
| Policy RLS gọi hàm mỗi dòng | truy vấn chậm theo số dòng | Nên sửa |

## 7. Đọc thêm khi cần

| Cần | Đọc |
|---|---|
| Đọc `EXPLAIN (ANALYZE, BUFFERS)`; truy vấn tìm khoá ngoại thiếu index, truy vấn chậm, bảng phình, index không dùng; cấu hình mẫu kết nối, timeout, giám sát | `references/diagnostics.md` |

Liên quan: agent `database-reviewer` (review đầy đủ), `security-reviewer` (RLS, quyền); skill
`database-migrations`, `fastapi`, `python`, `api-design`, `security-review`.

Phần mẫu Postgres dựa trên bộ thực hành của đội Supabase (MIT), đến qua nguồn ghi ở frontmatter.
