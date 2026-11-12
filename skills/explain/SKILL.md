---
name: explain
description: Use when the user types /explain (or /agent-agile-team:explain), or asks to explain, "diễn giải", "nói dễ hiểu hơn", "chưa hiểu", "tại sao" about a message, a pasted passage or a file, or a decision with consequences that are hard to undo.
metadata:
  group: "communication"
  roles: "all"
---

# Diễn giải bằng lời dễ hiểu

> **Kết luận:** viết lại **tin gần nhất** (hoặc đoạn/file người dùng chỉ) cho người không rành kỹ thuật: kết luận
> một câu trước, giải nghĩa mọi viết tắt, ví dụ đời thường, chuyện gì xảy ra · ảnh hưởng · tốn gì · rủi ro gì, chi
> tiết kỹ thuật tách cuối — và **giữ nguyên mọi dữ kiện** của nguồn. Xong thì tin sau về súc tích. Luật chế độ,
> dấu hiệu vào/thoát: [communication.md](../../method/communication.md) mục 1.

## 1. Nguồn

| Người dùng gõ | Nguồn để diễn giải |
|---|---|
| `/explain` | tin gần nhất của agent; chưa có tin trước thì hỏi một câu: "diễn giải gì?" |
| `/explain <đường dẫn>` (vd `/explain PLAN.md`) | file đó; **nguồn dài hơn 200 dòng** thì hỏi người muốn phần nào (một câu), không tự cắt |
| một đoạn dán kèm | đoạn đó |
| câu tương đương ("chưa hiểu", "tại sao", "nói dễ hiểu hơn") | tin gần nhất, như `/explain` |

Nguồn mơ hồ chỗ nào thì ghi "nguồn không nói rõ" chỗ đó; không đoán, không thêm sự kiện không có ở nguồn.

## 2. Cách viết

1. **Cảnh báo trước.** Nguồn có cảnh báo bảo mật hoặc hậu quả khó hoàn tác → đưa lên **đầu** tin diễn giải, một câu rõ.
2. **Kết luận một câu** (hoặc điều người đọc cần làm).
3. **Theo góc người đọc:** chuyện gì xảy ra · ảnh hưởng gì tới họ · tốn gì · rủi ro gì · có đường lui không.
4. **Giải nghĩa** mọi viết tắt và thuật ngữ ở lần đầu, trong ngoặc ngay sau từ đó ("ORM (lớp trung gian giữa code
   và cơ sở dữ liệu)"). Không bỏ từ nào trong danh sách viết tắt của nguồn.
5. **Ví dụ đời thường** cho khái niệm khó ("cơ sở dữ liệu giống một cuốn sổ cái dùng chung").
6. **Bỏ mã trần**: mã đi kèm tên ngắn hoặc thay bằng tên.
7. **"Chi tiết kỹ thuật"** tách xuống cuối, người không chuyên bỏ qua được: ở đây giữ nguyên số liệu, đường dẫn,
   tên lệnh của nguồn.
8. **Kết** bằng điều người đọc cần quyết, kèm khuyến nghị (mẫu câu hỏi: `method/communication.md` mục 3).

## 3. Giữ nguyên dữ kiện

Diễn giải **làm rõ, không bỏ, không thêm**:

- **Còn nguyên:** số liệu + đơn vị, đường dẫn (trong dấu code), mã lỗi, chữ phủ định ("chưa", "không cần"),
  cảnh báo bảo mật.
- **Không thêm** số mới, kể cả số tự tính từ số nguồn (ví dụ "chậm gấp 4,4 lần" khi nguồn chỉ nêu hai số gốc), mức
  độ hay thời gian mà nguồn không nêu.
- Dài hơn nguồn là bình thường; mất dữ kiện hay thêm dữ kiện là lỗi.

## 4. Thoát

- Người dùng hiểu hoặc chuyển sang việc khác → tin sau **về súc tích** (`skills/response-style`).
- "Diễn giải từ giờ" / "trả lời chi tiết từ giờ" → giữ chế độ này cả phiên; "ngắn gọn lại" → về mặc định.
- Lời yêu cầu trực tiếp của người dùng luôn thắng.

## 5. Mẫu

Nguồn: "Replica chỉ chữa nếu báo cáo là nguyên nhân khoá; cần đo 1 ngày."

```
Chưa nên làm replica — cần đo 1 ngày trước.
Cơ sở dữ liệu giống một cuốn sổ cái dùng chung: báo cáo cuối tháng lật hết sổ nên người khác không ghi được. Replica
(bản sao chỉ để đọc) giống photo cuốn sổ cho báo cáo dùng riêng. Nhưng nếu báo cáo không phải thủ phạm thì photo sổ
cũng không giúp gì. Đo mất 1 ngày, không đụng dữ liệu thật.
**Cần anh quyết:** cho đo 1 ngày chứ? KHUYẾN NGHỊ: có — đo trước khi tốn tiền làm replica.
```

## 6. Lỗi hay gặp

| Lỗi | Sửa |
|---|---|
| Diễn giải xong vẫn viết dài cho các tin sau | về súc tích ở tin kế (mục 4) |
| Bỏ cảnh báo vì "nghe đáng sợ" | cảnh báo lên đầu, một câu rõ |
| Đổi `5 → 20 kết nối` thành "tăng gấp bốn" | giữ số gốc; không thêm số tự tính |
| Ví dụ làm sai nghĩa kỹ thuật | ví dụ chỉ để hiểu khái niệm; con số và hậu quả vẫn lấy từ nguồn |
