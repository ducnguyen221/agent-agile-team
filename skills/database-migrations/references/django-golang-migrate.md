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
migrate -path migrations -database "$DATABASE_URL" version        # phiên bản hiện tại (có thể kèm "dirty")
migrate -path migrations -database "$DATABASE_URL" force VERSION  # đặt phiên bản, KHÔNG chạy migration — xem "Trạng thái dirty"
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

**Trạng thái dirty.** Mỗi migration chạy, công cụ đặt cờ dirty; migration hỏng giữa chừng thì cờ giữ nguyên và
mọi lệnh tiếp theo dừng. `force` chỉ ghi lại con số phiên bản, không sửa dữ liệu hay schema. Đây là **ngoại lệ
có kiểm soát** của nguyên tắc "không sửa tay DB" (`SKILL.md` mục 1), nên làm theo runbook và xin người dùng gật:

1. Điều tra: migration hỏng áp một phần hay chưa áp gì? (đọc lỗi, so schema với file `up`).
2. Đưa DB về đúng một trạng thái đã biết — hoàn tác phần đã áp dở, hoặc làm nốt phần còn lại — bằng SQL ghi lại
   trong runbook (không gõ tay không dấu vết).
3. `force VERSION` với VERSION khớp trạng thái thật (phiên bản trước nếu đã hoàn tác; phiên bản hỏng nếu đã làm
   nốt), rồi `version` để kiểm cờ dirty đã hết, rồi sửa file migration hỏng **bằng migration mới** nếu nó đã
   chạy ở môi trường chung (nguyên tắc 5: migration đã chạy là bất biến).

**Trùng số phiên bản.** Phiên bản phải khác nhau và tăng dần; hai nhánh cùng tạo `000061` thì khi gộp có hai cặp
file cùng số. Cách gỡ: nhánh vào sau đổi **cả cặp** `up`/`down` sang số kế tiếp (`000062`) **trước khi gộp** —
chỉ đổi được khi file đó chưa chạy ở môi trường chung nào; đã chạy rồi thì giữ nguyên nó và đổi file còn lại.
DB cá nhân đã áp bản cũ số: dựng lại DB dev (hoặc `down` rồi `up`), đừng `force` để lách.

**Quy ước phòng ngừa.** `migrate create` mặc định đặt số theo thời gian; chỉ cờ `-seq` mới đánh số tuần tự.
Nhiều người làm song song → dùng số theo thời gian (không cờ `-seq`), hoặc giữ `-seq` và thêm kiểm trong CI
rằng không phiên bản nào trùng:

```bash
ls migrations/*.up.sql | sed 's#.*/##; s/_.*//' | sort | uniq -d   # có dòng in ra = trùng phiên bản → CI đỏ
```
