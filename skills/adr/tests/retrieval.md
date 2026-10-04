---
skill: adr
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: e51ac5cfa6684f45de70dddd469b1975496a4a62
date: 2026-10-04
result: "strict 6/6 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 6/6"
agent_ids:
  questions: a25859e6268e55dde
  answers: a27b454d81f8d3543
---

Đã đọc: `<gốc worktree>\skills\adr\SKILL.md`

# Thử truy xuất — adr

> **Kết luận:** strict 6/6 (+0 partial, 0 fail), points-right 6/6: đạt ngưỡng (5/5 câu tình huống Đạt; câu ranh giới Đạt). Chạy lại ở SPR-04 TK10 trên bản `SKILL.md` **viết lại phòng sạch**
> (`skill_sha` ở frontmatter đổi so lượt trước; `description` không đổi). Giữ **nguyên bộ câu hỏi cũ** (người soạn `a25859e6268e55dde` của lượt trước); cột Mục kỳ vọng viết lại theo bản mới (các số mục
> của `SKILL.md` đổi: 6 mục, không còn bảng Đầu vào/khuôn riêng). Chủ thể là agent mới, do QA chạy.

Sáu câu hỏi do một agent **chưa đọc** skill soạn ở lượt trước (bộ câu giữ nguyên chữ, không soạn lại); file nháp "Mục kỳ vọng" viết lại theo bản mới (mtime `2026-10-04 08:09:28 +0700`) **trước khi** giao chủ thể
(lệnh giao lúc ~08:10 +0700); bài trả lời trọn của chủ thể và id agent ở `evidence/TK10/qa-adr.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.
Số lượt công cụ của chủ thể chưa đo (harness không báo). Skill chỉ có `SKILL.md`, không có `references/`. Câu 6 là câu ranh giới: đáp án của người soạn (`database-migrations`) đã được đối chiếu với `description` của skill đích
(thêm hoặc đổi cột, bảng lớn, backfill, đổi lược đồ không khoá) và nhận là đúng.

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Mình đang review PR của đồng nghiệp: bạn ấy gộp luôn module thanh toán vào dịch vụ đơn hàng và cho đơn hàng gọi thẳng vào bảng của thanh toán. PR không có dòng nào giải thích vì sao lại làm vậy thay vì giữ hai dịch vụ tách nhau. Mình nên đòi bạn ấy bổ sung gì để sau này người khác hiểu lý do, và đòi ở đâu? | `SKILL.md` › 1. Khi nào viết (tạo phụ thuộc mới giữa hai phần vốn độc lập) + › 2. Nội dung một ADR + › 3. Đánh số và nơi đặt + › 6. Lỗi hay gặp (ADR viết sau khi code) | `SKILL.md` › 1. Khi nào viết; › 2. Nội dung một ADR; › 3. Đánh số và nơi đặt; › 6. Lỗi hay gặp | Đạt |
| 2 | Sprint này mình là người điều phối, có một task cỡ lớn là tách dữ liệu khách hàng ra khỏi database dùng chung để mỗi dịch vụ có kho riêng. Kế hoạch đã gần xong nhưng mới chỉ có danh sách việc, chưa thấy chỗ nào ghi các lựa chọn thiết kế đã cân nhắc. Trước khi cho qua cổng duyệt kế hoạch, mình cần đảm bảo điều gì về phần quyết định thiết kế? | `SKILL.md` › 1. Khi nào viết (việc cỡ lớn: PLAN phải có ≥1 ADR hoặc nói thẳng không có) + › 4. Vòng đời bước 2 (review cùng PLAN trước Cổng 1) + › 2 (≥2 lựa chọn thật) | `SKILL.md` › 1. Khi nào viết (việc cỡ lớn); › 4. Vòng đời; › 5. Điểm dừng | Đạt |
| 3 | Sắp tới hạn bàn giao mà team vẫn đang cãi nhau: giữ nguyên REST cho đối tác bên ngoài hay đổi sang GraphQL. Đối tác đã tích hợp 6 tháng rồi, đổi thì họ phải viết lại. Anh sếp bảo chốt trong hôm nay, mình trễ hạn nên muốn chốt nhanh gọn mà vẫn không bị ai hỏi lại "sao hồi đó lại chọn vậy" sau này. Nên chốt và lưu lại kiểu gì? | `SKILL.md` › 1 (đổi hợp đồng) + › 2 (≥2 lựa chọn gồm giữ nguyên, Hệ quả có đường lùi) + › 5. Điểm dừng (hai lựa chọn ngang nhau → `DN` trong PLAN, không tự chốt) + › 4 (Cổng 1 → accepted) | `SKILL.md` › 1. Khi nào viết; › 2. Nội dung một ADR; › 5. Điểm dừng (hai lựa chọn ngang nhau thành `DN`); › 6. Lỗi hay gặp | Đạt |
| 4 | Công ty mình đang trả tiền thuê một dịch vụ tìm kiếm bên thứ ba khá đắt, và có người đề xuất bỏ hẳn, tự dựng bằng tính năng full-text của cơ sở dữ liệu hiện có. Phải sửa lại ba chỗ gọi API tìm kiếm và dữ liệu đồng bộ đi kèm. Chưa ai làm gì cả, mới đang bàn. Trước khi bắt tay vào, mình cần làm gì với quyết định gỡ bỏ công nghệ này? | `SKILL.md` › 1 (bỏ một công nghệ đang dùng) + › 2 (Hệ quả: khó hơn, đường lùi và giá) + › 4 (proposed, review trước Cổng 1, chưa duyệt chưa code) | `SKILL.md` › 1. Khi nào viết; › 2. Nội dung một ADR; › 4. Vòng đời | Đạt |
| 5 | Cuối năm ngoái mình ghi lại là "mọi dữ liệu người dùng lưu ở một vùng duy nhất cho đơn giản", đã được duyệt. Giờ khách hàng châu Âu yêu cầu dữ liệu phải nằm trong khu vực của họ, nên chắc chắn phải lưu theo từng vùng. Với bản ghi cũ đang nằm đó, mình nên đụng vào nó thế nào, và cái mới thì viết ra sao cho người sau đọc được cả hai? | `SKILL.md` › 4. Vòng đời bước 4 (ADR mới thế chỗ; cũ chỉ đổi trạng thái `superseded by NNNN`) + › 2 (Trạng thái, Liên kết) + › 3 (số kế tiếp, không tái dùng) + › 5, › 6 (không sửa ADR cũ) | `SKILL.md` › 4. Vòng đời (bước 4); › 5. Điểm dừng; › 6. Lỗi hay gặp | Đạt |
| 6 | Mình đã chốt sẽ chạy trên Postgres rồi, bây giờ chỉ cần thêm một cột `deleted_at` vào bảng đơn hàng 40 triệu dòng và điền giá trị mặc định cho dữ liệu cũ mà không được khóa bảng làm sập hệ thống. Nên làm theo trình tự nào? | mục khác: skill `database-migrations` (nền tảng đã chốt, chỉ thêm cột + backfill bảng lớn không khoá; `SKILL.md` › 1 "Không cần ADR") | mục khác: skill `database-migrations` (kèm `postgres`, reviewer `database-reviewer`), từ `SKILL.md` › 1 phần "Không cần ADR" | Đạt |

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hứa mà thân skill không có.
- Chỗ thiếu còn lại sau khi viết lại (chủ thể nêu hoặc tôi đối chiếu): khuôn mục "Hệ quả" trong `skills/adr/SKILL.md` mục 2 có ô "Quay lại" nhưng không có chỗ riêng cho kế hoạch chuyển đổi và quay lui khi quyết định là bỏ công nghệ hay gỡ dịch vụ (câu 4).
- Chủ thể nêu thêm các chỗ phụ: skill không nói lời của người ngoài quy trình (sếp) có tính là người duyệt ở cổng không và không có đường chốt nhanh dưới áp lực hạn chót (câu 3); không nói trường "Liên kết" của ADR thay thế phải ghi ra sao ngoài việc ghi rõ nó thế chỗ ADR nào, và không nói về di chuyển dữ liệu thật của bản ghi cũ (câu 5); `method/sizing.md` được nhắc nhưng không giải thích cỡ lớn trong file này (câu 2, phụ).
- Đã sửa so lượt trước: bản viết lại có đoạn "ADR viết sau khi code" ở mục 6 (câu 1 nay được trả lời trực tiếp); không còn dòng "đòi ADR trong PR đang review" riêng.

## Lịch sử

Lượt trước (2026-10-04, `skill_sha` `8daf1ea5596506d312da96d148a45f632368e77d`, bản trước khi viết lại phòng sạch, người soạn `a25859e6268e55dde`, chủ thể `a876fed94c9014359`): strict 6/6 (+0 partial, 0 fail), points-right 6/6, cùng bộ câu hỏi.

## Chạy lại sau `TK12.1` (mục 5)

- chạy lại 2026-10-04 sau khi `source:` của `SKILL.md` đổi (mã hồ sơ riêng vào dấu code kèm tên ngắn, `TK12.1` mục 5); bộ sáu câu giữ nguyên chữ; chủ thể mới `a27b454d81f8d3543`; 6/6 Đạt như lượt trước. Cột "Mục agent trỏ" ở bảng trên ghi theo lượt này; `result` không đổi (đếm lại từ bảng). Bài trả lời trọn ở `evidence/TK12/adr-retrieval-rerun.md` trong hồ sơ sprint `SPR-04` của lớp riêng.
