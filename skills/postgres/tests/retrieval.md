---
skill: postgres
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 963d141988d565844c46768b15bb0382b39cdf06
date: 2026-10-04
result: "strict 3/7 (+4 partial, 0 fail) — below threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: a054e00d335abdcb0
  answers: a4592ce7b1250d1a0
---

Đã đọc: `<gốc worktree>/skills/postgres/SKILL.md` (kèm `references/diagnostics.md`)

# Thử truy xuất — postgres (bộ câu mới, lượt độc lập)

> **Kết luận:** strict 3/7 (+4 partial, 0 fail), points-right 7/7: DƯỚI ngưỡng (2/6 câu tình huống Đạt hẳn = 33 %, ngưỡng ≥80 %; câu ranh giới Đạt). Lượt độc lập sau lượt cũ: bộ câu MỚI, người soạn mới, chủ thể mới, chấm lại từ đầu, không nương theo lượt cũ. Không sửa skill.

Bảy câu hỏi do một agent MỚI (`sonnet`, `a054e00d335abdcb0`) **chưa đọc** skill soạn từ `description`, lĩnh vực và danh sách câu của mọi bộ cũ (để không lặp). Người soạn chỉ đọc một tệp đầu vào gồm đúng ba thứ đó. Cột "Mục kỳ vọng" do QA đọc `SKILL.md` và `references/` rồi ghi vào tệp nháp (mtime `2026-10-04 10:41:37 +0700`) **trước khi** giao chủ thể (lệnh giao sau `2026-10-04 10:42:34 +0700`). Chủ thể là agent mới (`sonnet`, `a4592ce7b1250d1a0`), cấm công cụ Skill, được đưa đường tuyệt đối tới `SKILL.md`, không được mở thư mục `tests/`; 3 lượt đọc file (SKILL.md và câu hỏi cùng lượt, rồi `references/diagnostics.md`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng. Bài trả lời trọn của chủ thể, câu hỏi của người soạn, id agent và tệp kỳ vọng (có mtime) ở `evidence/TK13/postgres-retrieval.md` và `evidence/TK13/expected/postgres-expected.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Câu 7 là câu ranh giới (đáp án của người soạn ghi ở cột kỳ vọng). Skill KHÔNG đổi giữa lượt cũ và lượt này (`skill_sha` giữ nguyên). Riêng câu 5 trong tệp này đổi chuỗi ví dụ địa chỉ thư (`'%an@example%'` thay cho chuỗi gốc của người soạn) vì máy kiểm chống rò chặn chuỗi gốc; chủ thể đã nhận và trả lời bản gốc, nguyên văn ở tệp evidence.

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Bảng `outbox_events` (PostgreSQL) đang dùng làm hàng đợi: 6 worker chạy song song, mỗi worker `SELECT ... WHERE status='pending' ORDER BY id LIMIT 100` rồi xử lý. Hiện thấy hai worker nhặt trùng cùng một event và gửi email hai lần, ngược lại có lúc worker khác bị chờ nhau rất lâu. Tôi nên viết câu truy vấn lấy việc thế nào để các worker không giẫm chân nhau mà không cần Redis hay RabbitMQ, và nếu worker chết giữa chừng thì event có bị kẹt không? | `SKILL.md` › 4 (hàng đợi việc: `FOR UPDATE SKIP LOCKED`) | `SKILL.md` › 4; `references/diagnostics.md` › 3.1 | Đạt (phần phụ: worker chết giữa chừng thì việc kẹt ở `processing`, và lấy lô 100 dòng, không có) |
| 2 | Ứng dụng đa tenant: bảng `invoices` có cột `tenant_id`, hiện mọi endpoint đều phải nhớ gắn `WHERE tenant_id = :t`; tuần trước một endpoint báo cáo quên điều kiện này và lộ hoá đơn của công ty khác. Tôi muốn để chính cơ sở dữ liệu ép cách ly dữ liệu giữa các tenant, role kết nối của app dùng chung một user cho mọi request. Cấu hình thế nào để an toàn, và có những cạm bẫy nào (superuser, owner của bảng, hiệu năng) tôi cần tránh? | `SKILL.md` › 5 (RLS, quyền tối thiểu) + › 2 (index cột policy) + › 6 | `SKILL.md` › 5, › 2, › 6 | Một phần (đúng nơi; thiếu truyền tenant vào phiên khi dùng chung một role, `FORCE ROW LEVEL SECURITY`, `BYPASSRLS`) |
| 3 | Bảng `ledger_entries` có cột `amount` đang là `float8`, tổng cuối tháng lệch vài xu so với báo cáo kế toán (ví dụ cộng 1,3 triệu dòng ra 4.999.999,98 thay vì 5.000.000,00). Ngoài ra cột `created_at` là `timestamp without time zone` và dữ liệu nhập từ nhiều múi giờ (Hà Nội, Singapore, UTC). Nên đổi sang kiểu dữ liệu nào, và đổi trên bảng đang có dữ liệu thì cần lưu ý gì? | `SKILL.md` › 3 (`numeric`, `timestamptz`) + › 6 + › 1 (đổi kiểu → `database-migrations`) | `SKILL.md` › 3, › 6; mục khác: `database-migrations` cho cách đổi | Đạt (phần phụ: chuyển `timestamp` sang `timestamptz` khi nhiều múi giờ, chọn độ chính xác `numeric`) |
| 4 | Bảng `sensor_readings` tăng khoảng 40 triệu dòng mỗi tháng, truy vấn gần như luôn lọc theo khoảng thời gian (7 ngày gần nhất) và hàng tháng phải xoá dữ liệu cũ hơn 18 tháng bằng `DELETE ... WHERE ts < ...`, mỗi lần chạy hàng giờ và làm bảng phình to dù đã autovacuum. Có nên chia bảng không, chia theo kiểu nào, và việc dọn dữ liệu cũ nên làm ra sao cho nhanh, không để lại bloat? | `SKILL.md` › 2 (BRIN cho chuỗi thời gian) | `SKILL.md` › 2 (BRIN); `references/diagnostics.md` › 2 (bloat) | Một phần (đúng nơi gần nhất; thiếu chia bảng theo thời gian và bỏ phân vùng cũ thay cho `DELETE`) |
| 5 | Màn hình tìm kiếm khách hàng: người dùng gõ `WHERE lower(email) LIKE '%an@example%'` và `WHERE name ILIKE '%tran van%'` trên bảng `customers` 5 triệu dòng, mỗi lần mất 3-4 giây dù cột `email` và `name` đã có index B-tree thông thường. EXPLAIN cho thấy Seq Scan. Tại sao index hiện tại không được dùng và làm sao để tìm kiếm theo chuỗi con (kể cả có dấu tiếng Việt) chạy nhanh? | `SKILL.md` › 2 (GIN cho full-text/`jsonb`) | `SKILL.md` › 2; `references/diagnostics.md` › 1 (Seq Scan) | Một phần (đúng nơi gần nhất; thiếu `pg_trgm`, `LIKE '%…%'`, chuẩn hoá dấu tiếng Việt) |
| 6 | Hai nhân viên cùng bấm "đặt chỗ" cho ghế cuối cùng của một chuyến bay. Code hiện tại: `SELECT seats_left FROM flights WHERE id=7`, kiểm tra trong Python rằng `seats_left > 0`, rồi `UPDATE flights SET seats_left = seats_left - 1`. Thỉnh thoảng `seats_left` xuống âm (-1, -2). Giao dịch đang chạy ở mức mặc định. Cách sửa nào đúng ở tầng cơ sở dữ liệu: khoá dòng, mức cô lập, hay ràng buộc, và đánh đổi của từng cách là gì? | `SKILL.md` › 3 (ràng buộc `CHECK`, "kiểm trước rồi chèn là đua") + › 4 (khoá, giao dịch ngắn) | `SKILL.md` › 3, › 4 | Một phần (đúng nơi; thiếu so sánh khoá dòng/mức cô lập/ràng buộc và `UPDATE` có điều kiện) |
| 7 | Chúng tôi cần đổi tên cột `orders.cust_ref` thành `customer_code` và tách bảng `addresses` ra từ `customers` trên PostgreSQL production đang có ~30 triệu dòng, có 4 service khác nhau đọc/ghi các cột này và không được phép downtime. Cần lên kế hoạch các bước phát hành (thêm cột mới, ghi đôi, backfill, chuyển đọc, bỏ cột cũ), thứ tự deploy giữa các service và cách rollback nếu bước giữa chừng hỏng. Làm thế nào? | mục khác: skill `database-migrations` (`SKILL.md` › 1 "Đổi schema trên dữ liệu thật") | mục khác: `database-migrations` (`SKILL.md` › 1, › 2, › 3) | Đạt |

## Thiếu nội dung / mâu thuẫn

- Chia bảng theo thời gian (partition) và dọn dữ liệu cũ bằng bỏ phân vùng thay cho `DELETE` hàng loạt: không có; mục 2 chỉ có BRIN (câu 4).
- Tìm chuỗi con (`LIKE '%…%'`, `ILIKE`) với `pg_trgm`/GIN trigram, `unaccent`, index trên `lower(…)`: không có; mục 2 chỉ có GIN cho `jsonb` và full-text (câu 5).
- RLS nhiều tenant với một role chung: cách truyền tenant vào phiên (`SET LOCAL`/`current_setting`), `FORCE ROW LEVEL SECURITY`, superuser/`BYPASSRLS` bỏ qua RLS: không có; mục 5 chỉ có nguyên tắc (câu 2).
- Đua dữ liệu kiểu đọc-kiểm-ghi: so sánh khoá dòng, mức cô lập, ràng buộc, `UPDATE … WHERE` nguyên tử: không có; chỉ có câu "kiểm trước rồi chèn là đua" và `CHECK` (câu 6).
- Worker chết giữa chừng (việc kẹt ở `processing`, hết hạn thuê, xử lý idempotent) và lấy việc theo lô: không có (câu 1, phụ). Chuyển `timestamp` sang `timestamptz` từ nhiều múi giờ: không có (câu 3, phụ).
- `description` hứa "implementing Row Level Security"; thân skill chỉ có mấy dòng nguyên tắc (mục 5) nên mức hứa hơi cao so với nội dung (câu 2).

## Lịch sử

Lượt trước (bộ câu cũ, 2026-10-04, `skill_sha` `963d141988d565844c46768b15bb0382b39cdf06`, `result`: strict 6/6 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 6/6). Bộ câu cũ giữ nguyên bên dưới, id hàng đổi thành `c1`… để không lẫn vào bảng chấm của lượt mới; người soạn lần sau phải đọc cả hai bộ để không lặp. Dòng "Đã đọc" và đoạn thước chấm của lượt cũ không chép lại (thước chung ở trên).

> **Kết luận:** strict 6/6: đạt ngưỡng. Sau `TK11.8` năm câu tình huống đều Đạt (lượt trước 5/6 Đạt hẳn, 1 Một phần; các ý một phần: `lock_timeout`, PgBouncer, index ghép + một phần, con trỏ cho khoá không duy nhất, `jsonb` hay bảng riêng); câu ranh giới trả `database-migrations`.

Bộ câu hỏi giữ nguyên chữ của lượt trước (bộ câu cũ giữ nguyên, không soạn mới); bộ câu mới là việc của `TK13`. Cột "Mục kỳ vọng" ghi vào file nháp
`.tmp/postgres-expected.md` **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm). Bài trả lời của chủ thể (id ở
`agent_ids`) và bảng chấm ở `evidence/TK11/postgres-retrieval.md` trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời,
đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| c1 | Bảng `audit_logs` ~200 triệu dòng, phân trang `LIMIT 50 OFFSET n` càng sâu càng chậm. Chuyển sang kiểu phân trang nào để trang thứ 100.000 vẫn nhanh, cần index gì? | `SKILL.md` › 4 (phân trang con trỏ, khoá không duy nhất `(created_at, id)`, so sánh hàng, không nhảy trang số N) + › 2 (index `(created_at DESC, id DESC)`) | `SKILL.md` › 4. Truy vấn và đồng thời; › 2. Chọn index | Đạt |
| c2 | 12 instance FastAPI × pool 20 kết nối, `too many connections`, vài kết nối `idle in transaction`. Đặt `max_connections`, PgBouncer, `statement_timeout`, `idle_in_transaction_session_timeout`, `lock_timeout` thế nào? | `references/diagnostics.md` › 3 (`lock_timeout`, `statement_timeout`, `idle_in_transaction_session_timeout` theo vai trò), › 3.1, › 3.2 (12 × 20 = 240 vượt `max_connections`; giảm pool hoặc PgBouncer `pool_mode = transaction`, giới hạn của chế độ này) + `SKILL.md` › 4 | `references/diagnostics.md` › 3.2; › 3.1; › 3 | Đạt |
| c3 | Thêm cột `deleted_at` vào `orders`, muốn danh sách đơn đang hoạt động nhanh. Định tạo partial index `WHERE deleted_at IS NULL` trên `(customer_id, created_at DESC)`: cú pháp đúng không, khi nào partial index có lợi hơn index thường? | `SKILL.md` › 2 (hàng "ghép + một phần" `(customer_id, created_at DESC) WHERE deleted_at IS NULL`, khi nào index một phần có lợi, truy vấn phải chứa điều kiện) | `SKILL.md` › 2. Chọn index | Đạt |
| c4 | `EXPLAIN ANALYZE` truy vấn join 3 bảng: ước lượng `rows=10`, thực tế `rows=480000`, Nested Loop 40 giây. Đọc plan thế nào, xử lý ra sao (`ANALYZE`, statistics, viết lại)? | `references/diagnostics.md` › 1 (ước lượng lệch nhiều bậc → `ANALYZE`; Nested Loop vế ngoài lớn → sửa ước lượng trước) | `references/diagnostics.md` › 1. Đọc kế hoạch thực thi | Đạt |
| c5 | Cột `tags` kiểu `text` chứa chuỗi JSON, cần lọc bản ghi có tag `"vip"` và đôi khi lấy khoá lồng. Đổi sang `jsonb` hay tách bảng riêng, dùng index GIN thế nào? | `SKILL.md` › 3 (đoạn "`jsonb` hay bảng riêng") + › 2 (GIN) + trỏ `database-migrations` cho việc đổi `text` → `jsonb` | `SKILL.md` › 3. Kiểu dữ liệu và ràng buộc; › 2. Chọn index | Đạt |
| c6 | Thêm cột `NOT NULL` kèm mặc định vào `users` 80 triệu dòng đang chạy production, backfill theo lô không khoá bảng. Quy trình migration zero-downtime từng bước? | mục khác: skill `database-migrations` (từ `SKILL.md` › 1) | mục khác: `database-migrations` (từ `SKILL.md` › 1), kèm agent `database-reviewer` | Đạt |

### Thiếu nội dung / mâu thuẫn

- `description` đã hứa "connection and timeout settings"; thân skill nay có `lock_timeout` và PgBouncer ở `references/diagnostics.md` mục 3.1–3.2.
- Chủ thể nêu: không có phần viết lại truy vấn hay tăng statistics target (câu 4); không nêu `jsonb_ops` / `jsonb_path_ops` hay cú pháp index biểu thức (câu 5).
- Nguồn của phần thêm ở `TK11.8`: tài liệu PostgreSQL (Client Connection Defaults), tài liệu PgBouncer (cấu hình, bảng tính năng theo chế độ gộp).
