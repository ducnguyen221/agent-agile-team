# Công cụ migration cho Node (Prisma, Drizzle, Kysely)

> **Kết luận:** tham khảo cho dự án Node. Mọi công cụ đều có lệnh "đẩy thẳng schema" chỉ dành cho dev —
> production luôn đi qua file migration đã review. Thao tác công cụ không sinh được (index đồng thời,
> backfill) thì viết SQL tay trong migration rỗng.

## 1. Prisma

```bash
npx prisma migrate dev --name add_user_avatar      # sinh migration từ schema (dev)
npx prisma migrate deploy                          # áp migration đang chờ (production, CI)
npx prisma migrate reset                           # xoá sạch và dựng lại — CHỈ dev
npx prisma generate                                # sinh lại client sau khi đổi schema
npx prisma migrate dev --create-only --name add_email_index   # migration rỗng để viết SQL tay
```

```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  avatarUrl String?  @map("avatar_url")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  orders    Order[]

  @@map("users")
  @@index([email])
}
```

```sql
-- migrations/20240115_add_email_index/migration.sql — Prisma không sinh được CONCURRENTLY
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);
```

## 2. Drizzle

```bash
npx drizzle-kit generate     # sinh migration từ schema
npx drizzle-kit migrate      # áp migration
npx drizzle-kit push         # đẩy thẳng schema, không file migration — CHỈ dev
```

```typescript
import { pgTable, text, timestamp, uuid, boolean } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name"),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});
```

## 3. Kysely (kysely-ctl)

```bash
kysely init                          # tạo kysely.config.ts
kysely migrate make add_user_avatar  # tạo file migration
kysely migrate latest                # áp mọi bản đang chờ
kysely migrate down                  # lùi bản cuối
kysely migrate list                  # trạng thái
```

Migration dùng `Kysely<any>`, **không** dùng kiểu DB hiện hành: migration đóng băng theo thời gian, không
được phụ thuộc kiểu schema hôm nay.

```typescript
import { type Kysely, sql } from 'kysely'

export async function up(db: Kysely<any>): Promise<void> {
  await db.schema
    .createTable('user_profile')
    .addColumn('id', 'serial', (col) => col.primaryKey())
    .addColumn('email', 'varchar(255)', (col) => col.notNull().unique())
    .addColumn('avatar_url', 'text')
    .addColumn('created_at', 'timestamp', (col) => col.defaultTo(sql`now()`).notNull())
    .execute()
  await db.schema.createIndex('idx_user_profile_avatar').on('user_profile').column('avatar_url').execute()
}

export async function down(db: Kysely<any>): Promise<void> {
  await db.schema.dropTable('user_profile').execute()
}
```

Chạy migration bằng mã (`Migrator` + `FileMigrationProvider`): kiểm `error` trả về của
`migrateToLatest()` và thoát mã khác 0 khi lỗi; **không** bật `allowUnorderedMigrations` ngoài dev — nó tắt
kiểm thứ tự theo thời gian và gây lệch schema giữa các môi trường.
