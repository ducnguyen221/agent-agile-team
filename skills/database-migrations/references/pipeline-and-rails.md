# Migration trong pipeline CI/CD, quyền chạy ở production, và Rails

> **Kết luận:** migration chạy ở production là **một bước riêng của pipeline**, có người duyệt, chạy bằng tài khoản CSDL riêng
> (quyền DDL), mỗi lần đúng một tiến trình, **trước** khi triển khai mã cần schema mới. PR kiểm migration trên CSDL tạm trước.
> Không ai (kể cả agent) chạy migration production bằng tay từ máy cá nhân. Rails dùng `bin/rails db:migrate`, thêm
> `strong_migrations` để chặn thao tác nguy hiểm.

## 1. Gắn migration vào pipeline

| Giai đoạn | Làm | Hỏng thì |
|---|---|---|
| Pull request | dựng CSDL tạm (container dịch vụ), chạy **toàn bộ chuỗi** migration từ đầu; kiểm model khớp migration; lint migration | chặn gộp |
| Sau gộp vào nhánh chính → staging | tự động chạy migration trên staging (bản sao cỡ gần production nếu rủi ro cao), rồi triển khai mã | dừng pipeline, không sang production |
| Production | job riêng, **chờ duyệt**, chạy migration; xong mới triển khai mã | dừng, báo, theo kế hoạch hoàn tác |

- **Kiểm model khớp migration (không sinh file mới):** Alembic `alembic check` (thoát khác 0 nếu model đòi thêm revision; dùng cùng
  logic autogenerate nên có cùng giới hạn — không thấy đổi tên cột); Django `python manage.py makemigrations --check --dry-run`
  (thoát khác 0 nếu còn thay đổi chưa có migration). Lint migration: Rails dùng `strong_migrations` (mục 3); Postgres nói chung có
  công cụ lint file SQL migration (ví dụ Squawk) — chọn một và để chạy ở bước PR.
- **Chuỗi lên/xuống trên CSDL tạm:** `upgrade head` từ rỗng; chạy `downgrade` rồi `upgrade` lại cho migration mới (diễn tập, không
  phải production). Migration rủi ro cao thì diễn tập trên bản sao cỡ production (`references/rehearsal.md`).
- **Thứ tự với mã:** migration **mở rộng** trước, deploy mã, **thu hẹp** ở lần sau (`SKILL.md` mục 3); không đặt migration phá vỡ
  trong cùng lần phát hành với mã cần nó mà không có bước tương thích hai chiều.
- **Không để mỗi instance ứng dụng tự migrate lúc khởi động** ở production: N instance khởi động cùng lúc chạy cùng migration, lỗi
  migration biến thành vòng lặp khởi động hỏng, và ứng dụng cần quyền DDL. Chạy migration một lần từ pipeline.
- **Một lần chạy tại một thời điểm:** không giả định công cụ tự khoá hộ. Trong GitHub Actions đặt `concurrency` cho job migration
  để hai lần chạy không đè nhau; Rails/Flyway/golang-migrate có cơ chế khoá riêng (kiểm trong tài liệu bản đang dùng), vẫn giữ `concurrency` ở pipeline.

```yaml
# .github/workflows/deploy.yml (rút gọn)
jobs:
  migrate-production:
    needs: migrate-staging              # staging đã chạy xanh
    runs-on: ubuntu-latest
    environment: production             # bật "Required reviewers" ở environment này: job dừng chờ duyệt
    concurrency: { group: migrate-production, cancel-in-progress: false }
    steps:
      - uses: actions/checkout@v4
      - run: alembic upgrade head       # hoặc: bin/rails db:migrate (RAILS_ENV=production)
        env:
          DATABASE_URL: ${{ secrets.MIGRATION_DATABASE_URL }}   # secret của environment production, tài khoản có quyền DDL
  deploy-app:
    needs: migrate-production           # mã mới chỉ lên sau khi migration xong
    # ...
```

Environment trong GitHub Actions: **Required reviewers** (tối đa 6 người hoặc nhóm, chỉ cần một người duyệt), **Wait timer**, giới hạn
nhánh được triển khai, và secret/biến **chỉ job dùng environment đó đọc được** (tài liệu GitHub, "Managing environments for deployment").

## 2. Ai được chạy migration ở production

- **Người dùng gật trước** (chạy trên dữ liệu thật là hành động không đảo ngược — `SKILL.md`): trong pipeline, người duyệt ở
  environment chính là cái gật; agent không tự bấm duyệt, không tự chạy migration production.
- **Tài khoản riêng cho migration**: có quyền `CREATE/ALTER/DROP`; tài khoản của ứng dụng chỉ có quyền đọc/ghi dữ liệu (ít quyền nhất).
  Mật khẩu của tài khoản migration nằm ở secret của environment production, không ở file trong repo, không ở máy cá nhân.
- **Ai duyệt:** người hiểu rủi ro (chủ dịch vụ/DBA), **khác người viết migration** khi migration rủi ro cao (backfill bảng nóng, đổi kiểu,
  bỏ cột). Ghi lại: commit nào, ai duyệt, giờ chạy, kết quả (log của job là bằng chứng).
- **Trước khi duyệt:** SQL sẽ chạy đã xem (Alembic: `upgrade head --sql`), kế hoạch hoàn tác đã ghi, có bản sao lưu/bản chụp gần nhất, cửa sổ thời
  gian thấp tải nếu có khoá; phiên chạy đặt `lock_timeout` (`references/postgres-safe-ddl.md` mục 6, 9).
- Ngoại lệ chạy tay (gỡ trạng thái hỏng của công cụ, khôi phục sau lệnh sai) theo runbook đã ghi và có người dùng gật (`SKILL.md` mục 1).

## 3. Rails

```bash
bin/rails generate migration AddTaxCodeToInvoices tax_code:string   # sinh file db/migrate/<mốc-thời-gian>_*.rb
bin/rails db:migrate                       # áp mọi migration chưa chạy (dev/staging)
RAILS_ENV=production bin/rails db:migrate  # production: chỉ từ job pipeline đã duyệt
bin/rails db:migrate:status                # up/down từng migration; "NO FILE" = migration đã chạy nhưng file đã bị xoá
bin/rails db:rollback STEP=1               # lùi (dev/diễn tập); production đi tới bằng migration mới
```

- `change` tự đảo ngược phần lớn thao tác; thao tác không đảo ngược được thì dùng `up`/`down`, hoặc `down` ném
  `ActiveRecord::IrreversibleMigration` kèm lý do (khớp với "không đảo ngược được" ở `SKILL.md` mục 2).
- Migration chạy trong transaction nếu CSDL hỗ trợ DDL trong transaction (Postgres có); `CREATE INDEX CONCURRENTLY` thì **không**: khai
  `disable_ddl_transaction!` và `algorithm: :concurrently`.
- **Gem `strong_migrations`** bắt thao tác nguy hiểm lúc phát triển (thêm index không đồng thời, thêm `NOT NULL` không an toàn, bỏ cột còn dùng…), in cách làm
  an toàn, và chỉ cho qua khi bọc `safety_assured { … }` — mỗi lần dùng phải có lý do trong PR. Đây là bước lint ở giai đoạn Pull request.

```ruby
class AddUniqueEmailToUsers < ActiveRecord::Migration[8.1]
  disable_ddl_transaction!

  def change
    # dọn dòng trùng trước (references/postgres-safe-ddl.md mục 9); gắn thành ràng buộc UNIQUE là bước tuỳ chọn ở mục đó
    add_index :users, :email, unique: true, algorithm: :concurrently
  end
end
```

- **Backfill là migration/tác vụ riêng**, không trong cùng `change` với DDL (`SKILL.md` mục 1): chia lô bằng `in_batches(of: 5000)`,
  idempotent, không import model ứng dụng vào migration — khai lớp tối giản ngay trong file (`class User < ActiveRecord::Base; end`)
  để migration không đổi nghĩa khi model đổi.
- `db/schema.rb` (mặc định) chỉ mô tả được phần Ruby DSL biết; dùng tính năng Postgres riêng (ràng buộc kiểm tra phức tạp, kiểu enum, trigger)
  thì đặt `config.active_record.schema_format = :sql` để giữ `db/structure.sql`. Cả hai là ảnh chụp trạng thái hiện tại — CSDL mới
  nên nạp bằng `db:schema:load`/`db:prepare`, đừng chạy lại cả chuỗi migration cũ trên CSDL trống (migration cũ có thể đã hỏng theo thời gian).
- Migration đã chạy ở production là bất biến (`SKILL.md` mục 1): không sửa file, tạo migration mới.

## Nguồn

Tài liệu GitHub Actions (environments: required reviewers, secret theo environment; `concurrency`), tài liệu Alembic (`alembic check`
trong CI), tài liệu Django (`makemigrations --check`), hướng dẫn Rails (Active Record Migrations: `db:migrate`, `db:migrate:status`,
`db:rollback`, `disable_ddl_transaction!`, schema format), README `strong_migrations`. Cú pháp `makemigrations --check` và các lệnh Rails chưa
chạy trực tiếp trên máy đo (không có Rails/Django cài sẵn); mẫu YAML đã kiểm cú pháp.
