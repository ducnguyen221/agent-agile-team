# Django và golang-migrate

> **Kết luận:** tham khảo cho dự án không dùng Alembic. Nguyên tắc ở `SKILL.md` giữ nguyên: schema và dữ
> liệu tách migration, backfill chia lô, bỏ cột qua hai lần deploy.

## 1. Django

```bash
python manage.py makemigrations                       # sinh migration từ thay đổi model
python manage.py migrate                              # áp
python manage.py showmigrations                       # trạng thái
python manage.py sqlmigrate accounts 0016             # xem SQL sẽ chạy
python manage.py makemigrations --empty accounts -n backfill_display_name   # migration rỗng để viết tay
```

**Migration dữ liệu** — chia lô theo khoá chính để vòng lặp luôn kết thúc:

```python
from django.db import migrations

BATCH = 5000

def backfill_display_names(apps, schema_editor):
    User = apps.get_model("accounts", "User")   # model lịch sử, không import model hiện hành
    last_pk = 0
    while True:
        batch = list(User.objects.filter(pk__gt=last_pk, display_name="").order_by("pk")[:BATCH])
        if not batch:
            break
        for user in batch:
            user.display_name = user.username
        User.objects.bulk_update(batch, ["display_name"], batch_size=BATCH)
        last_pk = batch[-1].pk

class Migration(migrations.Migration):
    atomic = False   # mỗi lô commit riêng, không một transaction khổng lồ
    dependencies = [("accounts", "0015_add_display_name")]
    operations = [migrations.RunPython(backfill_display_names, migrations.RunPython.noop)]
```

**`SeparateDatabaseAndState`** — gỡ cột khỏi model mà chưa bỏ khỏi DB (bỏ thật ở migration sau):

```python
class Migration(migrations.Migration):
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[migrations.RemoveField(model_name="user", name="legacy_field")],
            database_operations=[],   # chưa đụng DB
        ),
    ]
```

Index đồng thời trên Postgres: `django.contrib.postgres.operations.AddIndexConcurrently` trong migration
`atomic = False`.

## 2. golang-migrate

```bash
migrate create -ext sql -dir migrations -seq add_user_avatar      # tạo cặp up/down
migrate -path migrations -database "$DATABASE_URL" up             # áp mọi bản đang chờ
migrate -path migrations -database "$DATABASE_URL" down 1         # lùi một bản (dev/diễn tập)
migrate -path migrations -database "$DATABASE_URL" force VERSION  # gỡ trạng thái "dirty" — chỉ sau khi đã sửa tay DB khớp VERSION
```

```sql
-- migrations/000003_add_user_avatar.up.sql
ALTER TABLE users ADD COLUMN avatar_url TEXT;
CREATE INDEX CONCURRENTLY idx_users_avatar ON users (avatar_url) WHERE avatar_url IS NOT NULL;

-- migrations/000003_add_user_avatar.down.sql
DROP INDEX IF EXISTS idx_users_avatar;
ALTER TABLE users DROP COLUMN IF EXISTS avatar_url;
```

`CONCURRENTLY` không chạy trong transaction: nếu driver bọc file trong transaction, tách câu `CREATE INDEX
CONCURRENTLY` ra file migration riêng chỉ có một câu lệnh.
