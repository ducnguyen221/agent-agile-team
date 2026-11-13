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
> tiết kỹ thuật tách cuối — và **giữ nguyên mọi dữ kiện** của nguồn. Luật chế độ,
> dấu hiệu vào/thoát: [communication.md](../../method/communication.md) mục 1.

## 1. Nguồn

| Người dùng gõ | Nguồn để diễn giải |
|---|---|
| `/explain` | tin gần nhất của agent; chưa có tin trước thì hỏi một câu: "diễn giải gì?" |
| `/explain <đường dẫn>` (vd `/explain PLAN.md`) | file đó; nguồn quá dài thì hỏi người muốn phần nào (ngưỡng và cách hỏi: `method/communication.md` mục 1) |
| một đoạn dán kèm | đoạn đó |
| câu tương đương ("chưa hiểu", "tại sao", "nói dễ hiểu hơn") | tin gần nhất, như `/explain` |

Luật giữ nguyên dữ kiện, chỗ nguồn mơ hồ và việc không thêm số mới: `method/communication.md` mục 1.

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

Trước khi gửi, đối chiếu bản diễn giải với nguồn: mọi số liệu + đơn vị, đường dẫn, mã lỗi, chữ phủ định, cảnh báo bảo
mật của nguồn còn đủ, và không có số hay dữ kiện mới. Luật: `method/communication.md` mục 1. Dài hơn nguồn là bình thường.

## 4. Thoát

Khi nào về súc tích, "diễn giải từ giờ", "ngắn gọn lại": một nghĩa duy nhất ở `method/communication.md` mục 1 (bảng
hai chế độ, hàng "Dấu hiệu thoát"); skill này không nhắc lại.

## 5. Mẫu

Nguồn (mọi dữ kiện bản mẫu dùng): "Chứng chỉ TLS của trang web hết hạn sau 12 ngày. Gia hạn tự động chưa bật. Gia hạn
tay mất khoảng 10 phút, không cần dừng dịch vụ. Khuyến nghị: gia hạn tay ngay rồi bật gia hạn tự động."

```
Chứng chỉ TLS của trang web hết hạn sau 12 ngày; nên gia hạn tay ngay.
Chứng chỉ TLS (giấy xác nhận trang web là thật) giống giấy phép treo ở cửa tiệm: có hạn, hết hạn thì phải đổi.
Gia hạn tự động chưa bật nên phải làm tay. Làm tay mất khoảng 10 phút, không cần dừng dịch vụ.
**Cần anh quyết:** cho gia hạn tay ngay chứ?
**KHUYẾN NGHỊ:** có — gia hạn tay ngay rồi bật gia hạn tự động. Nếu anh chưa trả lời, em chưa làm gì; còn 12 ngày.
```

## 6. Lỗi hay gặp

| Lỗi | Sửa |
|---|---|
| Về súc tích quá sớm hoặc giữ diễn giải quá lâu | theo hàng "Dấu hiệu thoát" ở `method/communication.md` mục 1 |
| Bỏ cảnh báo vì "nghe đáng sợ" | cảnh báo lên đầu, một câu rõ |
| Đổi `5 → 20 kết nối` thành "tăng gấp bốn" | giữ số gốc; không thêm số tự tính |
| Ví dụ làm sai nghĩa kỹ thuật | ví dụ chỉ để hiểu khái niệm; con số và hậu quả vẫn lấy từ nguồn |
| Giải nghĩa thuật ngữ sai (vd p95 thành "người chậm nhất") | p95 = mức mà 95 % lượt nhanh hơn; không chắc nghĩa thì nói chung chung hoặc "nguồn không nói rõ", đừng đoán |
