---
skill: adr
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 8daf1ea5596506d312da96d148a45f632368e77d
date: 2026-10-04
result: "strict 6/6 (+0 partial, 0 fail) — at threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 6/6"
agent_ids:
  questions: a25859e6268e55dde
  answers: a876fed94c9014359
---

Đã đọc: `<gốc worktree>\skills\adr\SKILL.md`

# Thử truy xuất — adr

> **Kết luận:** strict 6/6 (+0 partial, 0 fail), points-right 6/6: đạt ngưỡng (5/5 câu tình huống Đạt; câu ranh giới Đạt). Chủ thể trỏ đúng mục ở cả năm câu tình huống
> và nhận ra câu ranh giới thuộc `database-migrations`. Chạy lại (lượt 3) vì dòng `source:` của `SKILL.md` đổi (bỏ số đo 8-gram khỏi metadata đi vào băm, re-review lần 2) làm lệch `skill_sha`; `description` không đổi.
> Bộ câu mới, người soạn và chủ thể đều là agent mới.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description`, lĩnh vực, tên các skill khác và cột câu hỏi của bộ cũ để không lặp); nguyên văn câu hỏi, file nháp "Mục mong đợi" (mtime `2026-10-04 00:58:24 +0700`),
bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/adr-rerun-after-rereview2.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường
dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp
**trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng -> giao chủ thể -> chấm). Skill chỉ có `SKILL.md`, không có
`references/`. Câu 6 là câu ranh giới: đáp án của người soạn (`database-migrations`) đã được đối chiếu với `description` của
skill đích (thêm hoặc đổi cột, bảng lớn, backfill, đổi lược đồ không khoá) và nhận là đúng.

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Mình đang review PR của đồng nghiệp: bạn ấy gộp luôn module thanh toán vào dịch vụ đơn hàng và cho đơn hàng gọi thẳng vào bảng của thanh toán. PR không có dòng nào giải thích vì sao lại làm vậy thay vì giữ hai dịch vụ tách nhau. Mình nên đòi bạn ấy bổ sung gì để sau này người khác hiểu lý do, và đòi ở đâu? | `SKILL.md` › 1. Khi nào (hàng reviewer đòi ADR, phụ thuộc giữa các service, hợp đồng giữa các phần) + › 3 bước 2 và 5 + › 4. Khuôn | `SKILL.md` › 1. Khi nào, › 2. Đầu vào, › 3. Các bước (bước 1, 2, 5), › 4. Khuôn | Đạt |
| 2 | Sprint này mình là người điều phối, có một task cỡ lớn là tách dữ liệu khách hàng ra khỏi database dùng chung để mỗi dịch vụ có kho riêng. Kế hoạch đã gần xong nhưng mới chỉ có danh sách việc, chưa thấy chỗ nào ghi các lựa chọn thiết kế đã cân nhắc. Trước khi cho qua cổng duyệt kế hoạch, mình cần đảm bảo điều gì về phần quyết định thiết kế? | `SKILL.md` › 1. Khi nào (sprint cỡ lớn mặc định có ADR) + › 3 bước 4 và 5 + › 5. Điểm dừng (chỉ một lựa chọn thật) | `SKILL.md` › 1. Khi nào (dòng sprint cỡ lớn), › 3. Các bước (bước 4, 5), › 5. Điểm dừng | Đạt |
| 3 | Sắp tới hạn bàn giao mà team vẫn đang cãi nhau: giữ nguyên REST cho đối tác bên ngoài hay đổi sang GraphQL. Đối tác đã tích hợp 6 tháng rồi, đổi thì họ phải viết lại. Anh sếp bảo chốt trong hôm nay, mình trễ hạn nên muốn chốt nhanh gọn mà vẫn không bị ai hỏi lại "sao hồi đó lại chọn vậy" sau này. Nên chốt và lưu lại kiểu gì? | `SKILL.md` › 1. Khi nào (đổi hợp đồng; phép thử nhanh) + › 2. Đầu vào + › 3 bước 3-4 + › 4. Khuôn | `SKILL.md` › 1. Khi nào (phép thử nhanh; dòng đổi endpoint trỏ `api-design`), › 2. Đầu vào, › 3. Các bước (bước 4), › 4. Khuôn | Đạt |
| 4 | Công ty mình đang trả tiền thuê một dịch vụ tìm kiếm bên thứ ba khá đắt, và có người đề xuất bỏ hẳn, tự dựng bằng tính năng full-text của cơ sở dữ liệu hiện có. Phải sửa lại ba chỗ gọi API tìm kiếm và dữ liệu đồng bộ đi kèm. Chưa ai làm gì cả, mới đang bàn. Trước khi bắt tay vào, mình cần làm gì với quyết định gỡ bỏ công nghệ này? | `SKILL.md` › 1. Khi nào (hàng bỏ một công nghệ đang dùng) + › 4. Khuôn (Hệ quả) + › 5. Điểm dừng (không đảo ngược → dừng (a)) | `SKILL.md` › 1. Khi nào (dòng bỏ một công nghệ), › 4. Khuôn (Hệ quả), › 5. Điểm dừng (dòng không đảo ngược, dòng đổi `SC`) | Đạt |
| 5 | Cuối năm ngoái mình ghi lại là "mọi dữ liệu người dùng lưu ở một vùng duy nhất cho đơn giản", đã được duyệt. Giờ khách hàng châu Âu yêu cầu dữ liệu phải nằm trong khu vực của họ, nên chắc chắn phải lưu theo từng vùng. Với bản ghi cũ đang nằm đó, mình nên đụng vào nó thế nào, và cái mới thì viết ra sao cho người sau đọc được cả hai? | `SKILL.md` › 3. Các bước bước 6 Thay thế + › 4. Khuôn (Trạng thái, Thay thế) + › 5. Điểm dừng (sửa ADR đã accepted) | `SKILL.md` › 3. Các bước (bước 6, 5), › 4. Khuôn (dòng Thay thế, Trạng thái), › 5. Điểm dừng | Đạt |
| 6 | Mình đã chốt sẽ chạy trên Postgres rồi, bây giờ chỉ cần thêm một cột `deleted_at` vào bảng đơn hàng 40 triệu dòng và điền giá trị mặc định cho dữ liệu cũ mà không được khóa bảng làm sập hệ thống. Nên làm theo trình tự nào? | mục khác: skill `database-migrations` (nền tảng đã chốt, chỉ đổi lược đồ và backfill an toàn; không có ADR mới) | mục khác: `database-migrations` (chủ thể nhận câu không thuộc `adr`; `SKILL.md` › 1. Khi nào, cột Không viết ADR: nền đã chốt nên không cần ADR cho từng cột) | Đạt |

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hứa mà thân skill không có.
- Chỗ thiếu đã biết từ các lượt trước vẫn còn: `skills/adr/SKILL.md:82-87` (khuôn mục "Hệ quả") không có chỗ ghi cách quay lại khi quyết định là bỏ công nghệ hay gỡ dịch vụ (câu 4: chủ thể nêu thêm là skill không có kế hoạch chuyển đổi và quay lui). Lượt này chủ thể nêu thêm các chỗ phụ: không nói cách đòi ADR ngay trong một PR đang review hay viết ADR bổ sung sau khi code đã làm (câu 1); không nói lời của người ngoài quy trình (sếp) có tính là người duyệt ở cổng không và không có đường chốt nhanh dưới áp lực hạn chót (câu 3); không nói xử lý một ghi chú cũ không theo khuôn ADR khi viết bản thay thế (câu 5).
