# Tìm hàm trùng ý — bước thủ công

<!-- Nguồn: obra/superpowers-lab skills/finding-duplicate-functions/SKILL.md @ 51111f7 (MIT). Chỉ lấy ý
     (hàm cùng mục đích mà khác tên, khác cách viết; vùng hay trùng; chọn hàm sống sót; không gộp khi chưa có
     test). Viết lại thành năm bước đọc-và-grep thủ công; không mang script, không mang bộ prompt nhiều mô
     hình; thêm thang mức chung. -->

> **Kết luận:** hàm trùng ý là hàm **cùng hợp đồng** (đầu vào → đầu ra, lỗi, tác dụng phụ) mà khác tên hoặc
> cách viết, nên grep tên không bắt hết; tìm bằng năm bước đọc được bằng tay — liệt kê, gom, so thân, chọn hàm
> sống sót, báo. Trùng là **lời khuyên** (Nên sửa hoặc Ghi chú), không chặn gộp; chỉ lên Phải sửa khi hai bản
> trùng **đang cho kết quả khác nhau** cho cùng đầu vào — khi đó nó là lỗi, xử lý như lỗi.

## 1. Khi nào chạy

- Diff **thêm hàm mới** ở vùng hay mọc bản sao: tiện ích (`utils/`, `helpers/`, `lib/`), kiểm hợp lệ, định
  dạng (tiền, ngày, chuỗi), đường dẫn, đổi lỗi thành chuỗi, biến đổi phản hồi API. Mã do agent sinh hay trùng vì
  hàm mới được viết thay vì đi tìm hàm có sẵn.
- Hoặc Analyst/người dùng nhờ tìm trùng. Quét **cả repo** chỉ khi được giao như một việc riêng (audit); review
  diff thì hàm mới của diff là **mỏ neo**, chỉ tìm bản trùng của nó.
- Không chạy cho sửa một dòng hay diff không thêm hàm.

## 2. Năm bước

1. **Khoanh phạm vi.** Chỉ hàm xuất hoặc công khai và hàm trong vùng nêu ở mục 1; bỏ `tests/`, mã sinh tự
   động và thư viện bên thứ ba (bản sao ở đó không tính là nơi gọi hay bằng chứng).
2. **Liệt kê.** Dùng grep của harness tìm **định nghĩa** hàm (`def `, `function `, `=>` gán vào tên…) kết hợp
   từ khoá miền của hàm neo (động từ + danh từ: `format`, `parse`, `money`, `date`…). Ghi **lệnh đã chạy** và
   `file:dòng:chữ ký` từng kết quả. Grep tên bỏ sót hàm đặt tên khác (`to_dong`, `price_str`): thêm một lượt grep
   theo **thân** (chuỗi đặc trưng như ký hiệu tiền, regex, tên hàm chuẩn thư viện) rồi ghi cả hai lệnh.
3. **Gom.** Xếp các hàm cùng ý vào một nhóm (tên gần nhau, chữ ký tương đương, cho cùng đầu ra với một giá trị
   mẫu); nhóm chỉ có một hàm thì bỏ.
4. **So thân.** Đọc thân từng hàm trong nhóm. Cho cùng vài giá trị mẫu, gồm biên (0, âm, rỗng, số lẻ, giá trị
   lạ), so đầu ra, lỗi ném ra, tác dụng phụ, và đếm nơi gọi. Mỗi ứng viên mang đúng một kết luận:

   | Kết luận | Nghĩa | Làm gì |
   |---|---|---|
   | trùng ý | cùng hợp đồng, khác cách viết hoặc tên | đề nghị dùng một bản |
   | trùng một phần | một bản bao hàm bản kia (thêm nhánh, thêm tham số) | đề nghị dùng bản rộng hơn nếu hợp đồng nơi gọi khớp |
   | chỉ trùng tên | hợp đồng khác (định dạng khác, nơi dùng khác) | không gộp; ghi để khỏi nhầm lần sau |

5. **Chọn hàm sống sót, đặt mức.** Xem mục 3 và 4.

## 3. Chọn hàm sống sót

- **Dùng lại cái có sẵn** thay vì thêm hàm mới; hàm mới của diff là bản bị đề nghị bỏ khi có bản tương đương.
- Hàm sống sót là hàm **nhiều nơi gọi và nhiều test phủ nhất**, hợp đồng rộng nhất; không chọn theo "bản của
  mình". Hàm có hành vi im lặng đáng ngờ (cắt phần lẻ tiền, nuốt lỗi) thì **nêu ra** như phát hiện riêng chứ
  không bê nguyên sang.
- **Giữ khác biệt mà nơi gọi cần** (làm tròn, cắt phần lẻ, lỗi ném): so từng nơi gọi trước khi nói "thay được".
- Chưa có test phủ mọi cách dùng của bản sắp bỏ → bước đầu là **thêm test cho hàm sống sót**, rồi mới gộp.
- Đề nghị tạo hàm dùng chung **mới** chỉ khi có ít nhất hai nơi gọi **có thật** (không phải nơi gọi dự kiến) và
  hợp đồng tương thích; không bắc cầu hai hợp đồng khác nhau bằng một hàm nhiều cờ.

## 4. Mức và cách báo

| Tình huống | Mức |
|---|---|
| trùng ý, chưa lệch hành vi, gộp được rõ ràng | Nên sửa |
| trùng một phần, hoặc chưa quét hết, hoặc gộp đòi đổi nhiều nơi gọi | Ghi chú (hoãn thành `CO` nếu hoãn) |
| hai bản trùng cho **kết quả khác nhau** với cùng đầu vào, người dùng thấy | Phải sửa — là lỗi, kèm ví dụ đầu vào |
| trùng nói chung | không bao giờ Chặn |

Báo cáo gồm: lệnh đã chạy · bảng ứng viên (`file:dòng` · kết luận · lý do một dòng) · phát hiện theo mức · phần
**chưa quét** (đưa vào "Không đánh giá": hàm đặt tên lạ, mã ngoài vùng, ngôn ngữ khác). "Chưa thấy thêm bản sao"
không có nghĩa là không còn.

## 5. Không làm

- Không viết script, không dựng bộ phân loại nhiều mô hình hay giao agent chỉ để tìm trùng — grep và đọc là đủ,
  agent thêm đốt hạn mức.
- Reviewer chỉ đọc: không xoá, không gộp hộ trong lượt review; việc gộp là việc của người làm (một `TK` hay `CO`).
- Không coi giống tên là trùng, không coi khác tên là không trùng — so thân.
