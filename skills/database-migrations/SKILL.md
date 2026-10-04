---
name: database-migrations
description: Use when creating or altering tables, columns, indexes or constraints, writing a data backfill or data-fix script, planning a zero-downtime schema change, setting up migration tooling, reviewing a migration, or before a migration runs against production-sized or production data.
metadata:
  group: technique
  kind: reference
  roles: [implementer, tech-reviewer]
source: [affaan-m/ECC skills/database-migrations/SKILL.md, "concept: migration rehearsal on a production-sized copy (references/rehearsal.md, clean-room rewrite in SPR-04 TK10: old text removed first, new writer saw only a noun-phrase idea list)"]
source_sha: [c70874fae9eb0e5ad0365beb7e2955899fd1d30f, null]
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: [MIT, none]
rewrite_before_public: false
---

# Migration cơ sở dữ liệu

> **Kết luận:** mọi thay đổi schema là một file migration, chạy tới (forward-only) ở production, không bao
> giờ sửa tay DB thật. Tách migration **schema** khỏi migration **dữ liệu**; đổi phá vỡ đi theo
> **mở rộng → chuyển → thu hẹp**; migration chạm bảng lớn hoặc rủi ro cao phải **diễn tập** trên bản sao cỡ
> production và có kế hoạch hoàn tác trước khi chạy thật. Chạy trên dữ liệu thật là hành động không đảo
> ngược — chỉ khi người dùng gật.

## 1. Nguyên tắc

1. **Mọi thay đổi là một migration** — không sửa tay DB production; không có dấu vết, không lặp lại được.
   Ngoại lệ duy nhất: gỡ trạng thái hỏng của công cụ (cờ dirty của golang-migrate) hoặc khôi phục dữ liệu sau
   lệnh sai — theo runbook đã ghi và được người dùng gật (`references/django-golang-migrate.md`,
   `references/postgres-safe-ddl.md` mục 8).
2. **Production chỉ đi tới** — "hoàn tác" ở production là một migration tới mới; bản `downgrade` dùng cho
   môi trường phát triển và diễn tập.
3. **Schema và dữ liệu tách riêng** — không trộn DDL với cập nhật dữ liệu trong một migration.
4. **Thử với dữ liệu cỡ production** — migration chạy êm trên 100 dòng có thể khoá bảng 10 triệu dòng.
5. **Migration đã chạy ở production là bất biến** — không sửa; tạo migration mới.
6. **Mã và schema tương thích hai chiều trong lúc chuyển** — mã cũ đọc được schema mới, mã mới đọc được
   schema cũ cho tới khi rollout xong.

## 2. Kiểm trước khi áp migration

- [ ] Có cả `upgrade` và `downgrade`, hoặc ghi rõ "không đảo ngược được" kèm lý do.
- [ ] Không khoá toàn bảng trên bảng lớn (dùng thao tác đồng thời).
- [ ] Cột mới cho phép rỗng hoặc có mặc định (không thêm `NOT NULL` không mặc định vào bảng đã có dữ liệu).
- [ ] Khoá ngoại trên bảng đã có dữ liệu: `NOT VALID` → dọn dòng mồ côi → `VALIDATE`; đổi kiểu cột: đã đếm dòng
      không ép được kiểu (`references/postgres-safe-ddl.md` mục 6, 7).
- [ ] Index trên bảng đã có tạo bằng `CONCURRENTLY`.
- [ ] Backfill là migration riêng: chia lô, idempotent, chạy tiếp được khi đứt, có log tiến độ.
- [ ] Đã thử trên bản sao dữ liệu cỡ production (rủi ro cao: diễn tập đủ — mục 5).
- [ ] Kế hoạch hoàn tác đã ghi (PLAN hoặc runbook).

## 3. Đổi không gián đoạn: mở rộng → chuyển → thu hẹp

```
Mở rộng: thêm cột/bảng mới (cho phép rỗng hoặc có mặc định)
         deploy: ứng dụng ghi vào CẢ cũ và mới; backfill dữ liệu cũ
Chuyển:  deploy: ứng dụng đọc MỚI, vẫn ghi cả hai; kiểm dữ liệu khớp
Thu hẹp: deploy: ứng dụng chỉ dùng MỚI
         migration riêng: bỏ cột/bảng cũ
```

Ví dụ nhịp: ngày 1 thêm `new_status` (cho phép rỗng) + deploy bản ghi cả hai · ngày 2 backfill · ngày 3
deploy bản chỉ đọc `new_status` · ngày 7 bỏ cột `status`. Bỏ cột: **gỡ mã tham chiếu trước**, deploy, rồi
mới `DROP COLUMN` ở lần sau.

## 4. Alembic — công cụ mặc định cho dự án Python

```bash
alembic revision --autogenerate -m "add user avatar"   # sinh nháp từ model — LUÔN đọc lại trước khi dùng
alembic upgrade head --sql > .tmp/upgrade.sql         # xem SQL sẽ chạy, không đụng DB
alembic upgrade head                                  # áp (môi trường dev/staging)
alembic downgrade -1                                  # lùi một bước (dev/diễn tập)
alembic current; alembic history --verbose
```

```python
"""add user avatar and email index"""
from alembic import op
import sqlalchemy as sa

revision = "0007_add_user_avatar"
down_revision = "0006_create_orders"

def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.Text(), nullable=True))
    # CONCURRENTLY không chạy được trong transaction → mở khối autocommit
    with op.get_context().autocommit_block():
        op.create_index("idx_users_email", "users", ["email"],
                        postgresql_concurrently=True, if_not_exists=True)

def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("idx_users_email", table_name="users",
                      postgresql_concurrently=True, if_exists=True)
    op.drop_column("users", "avatar_url")
```

Migration dữ liệu là revision riêng, chạy SQL theo lô (mẫu lô ở `references/postgres-safe-ddl.md`); không
import model ORM hiện hành vào migration — model đổi theo thời gian, migration thì đóng băng. Autogenerate
**không** thấy: đổi tên cột (nó sinh bỏ + thêm = mất dữ liệu), một số đổi kiểu, server default, index
`CONCURRENTLY` — luôn sửa tay bản nháp.

## 5. Tra cứu

| Cần | Đọc |
|---|---|
| DDL an toàn trên Postgres: thêm/bỏ/đổi tên cột, index đồng thời, backfill bảng lớn theo lô, khoá ngoại + dòng mồ côi, đổi kiểu với dữ liệu hỏng, khôi phục sau `UPDATE` sai | [references/postgres-safe-ddl.md](references/postgres-safe-ddl.md) |
| Diễn tập trên bản sao, đo khoá/độ trễ, runbook production, tiêu chí huỷ | [references/rehearsal.md](references/rehearsal.md) |
| Django, golang-migrate (trạng thái dirty và `force`, trùng số phiên bản, quy ước đánh số) | [references/django-golang-migrate.md](references/django-golang-migrate.md) |
| Prisma, Drizzle, Kysely (Node) | [references/orm-tooling-node.md](references/orm-tooling-node.md) |

Thiết kế schema, index, truy vấn Postgres: skill `postgres`. Review migration chuyên đề dữ liệu: agent
`database-reviewer`. Mức rủi ro: migration tối thiểu là rủi ro vừa; backfill trên bảng nóng, đổi kiểu, bỏ
cột là rủi ro cao → bắt buộc diễn tập (`method/sizing.md`).

## 6. Phản mẫu

| Phản mẫu | Vì sao hỏng | Làm thay |
|---|---|---|
| SQL tay trên production | không dấu vết, không lặp lại | luôn qua file migration |
| Sửa migration đã deploy | lệch giữa các môi trường | tạo migration mới |
| `NOT NULL` không mặc định | khoá bảng, ghi lại mọi dòng | thêm cho phép rỗng → backfill → thêm ràng buộc |
| Index thường trên bảng lớn | chặn ghi suốt lúc dựng | `CREATE INDEX CONCURRENTLY` |
| Schema + dữ liệu chung một migration | khó lùi, transaction dài | tách hai migration |
| Bỏ cột trước khi gỡ mã | ứng dụng lỗi vì thiếu cột | gỡ mã trước, bỏ cột lần deploy sau |
| Tin bản autogenerate không đọc lại | đổi tên thành bỏ + thêm, mất dữ liệu | đọc và sửa tay từng bản nháp |
