---
skill: database-migrations
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: ee60372d2429a3e3db75358226396fbcf0c3537b
date: 2026-10-03
result: pass 7/7 (6 tình huống + 1 ranh giới), 4 partial
agent_ids:
  questions: a98471e3e606092bb
  answers: aacd41bfb8c8d0753
---

Đã đọc: `<gốc worktree>\skills\database-migrations\SKILL.md`

# Thử truy xuất - database-migrations

> **Kết luận:** pass 7/7 (6 tình huống + 1 ranh giới), 4 partial; ngưỡng >=4/5 câu tình huống + câu ranh giới. Chạy lại (lượt 2) với bộ câu mới, người soạn
> và chủ thể đều là agent mới. Chủ thể trỏ đúng mục ở cả 6 câu tình huống (những phần skill không phủ, chủ thể nói rõ và được ghi ở cuối file) và nhận
> ra câu ranh giới thuộc `postgres`.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` hiện hành, lĩnh vực và tên các skill khác); nguyên văn câu hỏi, file nháp
"Mục kỳ vọng" (có mtime), bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/database-migrations-retrieval-rerun-2.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `postgres`.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Bảng `invoices` có 45 triệu dòng, cột `status` đang là VARCHAR(20) tự do, giờ muốn đổi sang enum 5 giá trị và thêm CHECK. Trong dữ liệu cũ chắc còn vài giá trị lạ như "Paid ", "paid", "PAID". Làm sao đổi mà không chặn ghi của app đang chạy và không làm hỏng dòng cũ? | `SKILL.md` › 3. Đổi không gián đoạn: mở rộng → chuyển → thu hẹp + `references/postgres-safe-ddl.md` › 1. Thêm cột (mẫu CHECK … NOT VALID → VALIDATE CONSTRAINT) và › 5. Cập nhật dữ liệu lớn (backfill theo lô). Không có mục riêng về ép kiểu enum / chuẩn hoá giá trị lạ | `SKILL.md` › 1, › 3, › 5; `references/postgres-safe-ddl.md` › 1, › 5; `references/rehearsal.md` › 2 | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 2 | Team muốn tách cột `users.full_name` thành `first_name` và `last_name`, nhưng 3 service khác nhau vẫn đang đọc `full_name`, mỗi service deploy lệch nhau vài ngày. Nên chia thành những lần phát hành nào để không service nào bị lỗi giữa chừng? | `SKILL.md` › 3. Mở rộng → chuyển → thu hẹp (nhịp ngày 1/2/3/7, gỡ mã trước rồi mới DROP COLUMN) + › 1 nguyên tắc 6 (tương thích hai chiều); `references/postgres-safe-ddl.md` › 4. Bỏ cột an toàn | `SKILL.md` › 1 (nguyên tắc 6), › 3; `references/postgres-safe-ddl.md` › 3, › 4 | Đạt |
| 3 | Mình thêm foreign key `payments.order_id → orders.id` trên bảng `payments` khoảng 30 triệu dòng, và có vài chục dòng mồ côi từ hồi import cũ. Thêm thẳng thì sợ treo, mà không thêm thì dữ liệu cứ bẩn dần. Xử lý theo thứ tự nào? | `references/postgres-safe-ddl.md` › 1. Thêm cột (mẫu NOT VALID → VALIDATE áp dụng cho CHECK, suy ra cho ràng buộc) + `SKILL.md` › 2. Kiểm trước khi áp migration. KHÔNG có mục riêng cho FOREIGN KEY / dọn dòng mồ côi | `SKILL.md` › 1, › 6; `references/postgres-safe-ddl.md` › 1 (NOT VALID → VALIDATE), › 5; `references/rehearsal.md` › 2; nói rõ skill không có FOREIGN KEY / dòng mồ côi | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 4 | Sáng nay tôi chạy một script UPDATE sửa nhầm 18.000 dòng trong `subscriptions` trên production (lẽ ra chỉ sửa gói "trial"), đã commit rồi. Tôi chưa có migration tool, cũng chưa có bảng sao lưu riêng cho bảng này. Nên làm gì ngay, và rút gì để lần sau script sửa dữ liệu không sai như vậy? | `SKILL.md` › 1. Nguyên tắc (1: mọi thay đổi là migration, không SQL tay) + › 6. Phản mẫu ('SQL tay trên production'); `references/postgres-safe-ddl.md` › 5 (backfill idempotent, chia lô, log). Phần 'làm gì ngay để khôi phục' KHÔNG có trong skill (rehearsal chỉ nói sao lưu đã khôi phục thử). Đạt nếu agent nói rõ khoảng trống đó | `SKILL.md` › 1, › 6; `references/rehearsal.md` › 2, › 3, › 4; nói rõ skill không phủ khôi phục sau sự cố | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 5 | Dev mới trong nhóm hay sửa trực tiếp file migration đã merge (đổi tên cột, thêm dòng) thay vì viết file mới, và hai nhánh song song sinh ra hai file cùng số thứ tự 0057. CI đang đỏ vì checksum không khớp. Quy ước nào để chuyện này không lặp lại? | `SKILL.md` › 1. Nguyên tắc 5 (migration đã chạy là bất biến, tạo mới) + › 6. Phản mẫu ('Sửa migration đã deploy'). KHÔNG có mục xử lý xung đột số thứ tự / checksum (› 4 Alembic chỉ nói revision/down_revision) | `SKILL.md` › 1 (nguyên tắc 1, 5), › 6, › 4; nói rõ skill không phủ xung đột số thứ tự / checksum | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 6 | Sau khi thêm cột `logs.trace_id` bằng migration, bảng 200 triệu dòng, tôi cần lấp giá trị từ một bảng khác trong lúc app vẫn ghi liên tục. Ngoài việc đúng dữ liệu, tôi cũng muốn biết nên đóng gói đoạn lấp này trong chính file migration hay tách riêng, vì lần deploy trước đã bị timeout giữa chừng. | `SKILL.md` › 1 nguyên tắc 3 (schema và dữ liệu tách riêng) + › 2 (backfill là migration riêng: chia lô, idempotent, chạy tiếp được, log tiến độ) + › 4 (migration dữ liệu = revision riêng); `references/postgres-safe-ddl.md` › 5. Cập nhật dữ liệu lớn | `SKILL.md` › 1, › 2, › 4, › 6; `references/postgres-safe-ddl.md` › 5; `references/rehearsal.md` › 2 | Đạt |
| 7 | Query lấy danh sách đơn của một khách trong `orders` (60 triệu dòng) đang chậm 8 giây, EXPLAIN cho thấy seq scan, và cột lọc `customer_id` + `created_at` đã có index nhưng planner không dùng. Nên đọc EXPLAIN thế nào, kiểm statistics, chọn kiểu index và cấu hình Postgres ra sao để nó chạy dưới 100 ms? | mục khác: skill `postgres` (`SKILL.md` › 5. Tra cứu: 'Thiết kế schema, index, truy vấn Postgres: skill `postgres`') | mục khác: `postgres` (từ `SKILL.md` › 5. Tra cứu) | Đạt |


Chấm lại (điều phối yêu cầu): Đạt = trỏ đúng mục VÀ mục có nội dung trả lời câu; Một phần = trỏ đúng nơi nhưng nội dung thiếu, hoặc đạt qua đáp thay thế đã chấp nhận; Không đạt = trỏ sai hoặc bịa. Ngưỡng tính Đạt + Một phần cho việc trỏ đúng; số một phần ghi ở `result`.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Ép kiểu sang enum và chuẩn hoá giá trị lạ (`Paid `, `paid`, `PAID`) trước khi thêm `CHECK`: mẫu `NOT VALID` → `VALIDATE` chỉ minh hoạ bằng `CHECK (role IS NOT NULL)` (câu 1).
- `FOREIGN KEY` trên bảng lớn và dọn dòng mồ côi: không có (câu 3).
- Việc cần làm NGAY sau khi một `UPDATE` sai đã commit trên production (khôi phục từ sao lưu / PITR): không có; skill chỉ có phần phòng ngừa (câu 4).
- Xung đột số thứ tự migration giữa hai nhánh và checksum đỏ trên CI: không có; `SKILL.md` › 4 chỉ nói `revision` / `down_revision` (câu 5).
- Backfill lấp giá trị từ một bảng khác (JOIN / lookup trong phần chọn lô): mẫu lô chỉ có biểu thức trên chính bảng (câu 6).
