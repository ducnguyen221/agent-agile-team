---
name: response-style
description: Use when replying to a person or to another agent, writing a brief for a subagent, or drafting a sprint document, and the length, structure, register or level of detail of the response has to be chosen — including when the reader asks for a one-line answer.
metadata:
  group: "communication"
  roles: "all"
---

# Văn phong phản hồi

> **Kết luận:** câu đầu là kết luận hoặc điều người đọc cần làm; độ dài theo **người đọc × việc**; người đọc
> cần diễn giải thì chuyển sang skill `explain` (dấu hiệu: `method/communication.md` mục 1); và dù nén đến đâu cũng **không mất** báo
> lỗi, cảnh báo bảo mật, số liệu, chữ phủ định. Luật giao tiếp của môi trường (nếu có) thắng skill này;
> skill không chép lại luật đó.

## 1. Hai giọng

| Giọng | Cho ai | Tối ưu cho |
|---|---|---|
| **Người** | người dùng, tài liệu bàn giao, REPORT | hiểu nhanh, quyết được: kết luận trước, câu đầy đủ, thuật ngữ giải nghĩa |
| **Agent** | subagent, điều phối, PROGRESS | ít token: khung Kết quả / Chứng cứ / Còn mở / Cần người, câu gọn, con trỏ thay nội dung (skill `token-economy`) |

Subagent **không kế thừa** giọng của phiên chính: brief cho subagent chép khối rút gọn ở mục 8.

## 2. Ma trận độ dài

| Người đọc \ Việc | Đơn giản (hỏi đáp, trạng thái, một quyết định rõ) | Phức tạp hoặc rủi ro (so sánh, thiết kế, hậu quả khó hoàn tác) |
|---|---|---|
| **Nghiệp vụ** (không chuyên) | 1–3 câu, không tiêu đề, không bảng, không mã | ≤12 dòng lớp một: kết luận → 2–4 lý do → bảng lựa chọn nếu cần quyết → bước tiếp; "Chi tiết kỹ thuật" tách lớp hai, có thể bỏ qua |
| **Kỹ thuật** | 1–3 câu, mã kèm tên, số liệu | ≤25 dòng lớp một: kết luận → lý do → bảng lựa chọn → bước tiếp → "Chi tiết kỹ thuật" |
| **Giữa agent** | ≤5 dòng khung 4 phần | ≤2.000 token khung 4 phần, con trỏ file thay log |

Vượt trần → cắt tường thuật, cắt lặp, đẩy chi tiết xuống lớp hai hoặc ra file — **không** cắt mục 5.
Người dùng hỏi "phân tích kỹ" không có nghĩa viết dài: kỹ = đủ lý do và bảng lựa chọn, vẫn phân lớp.

## 3. Cấu trúc chuẩn (việc phức tạp)

1. **Câu đầu** = kết luận, hoặc điều người đọc phải làm/quyết. Không dẫn nhập, không "Em xin báo cáo".
2. **2–4 lý do** không chồng nhau, mỗi lý do một dòng.
3. **Bảng lựa chọn** khi có quyết định: cột *cách làm · đánh đổi & rủi ro · chi phí · khi nào chọn*;
   đánh dấu **khuyến nghị** và nói vì sao. Chỉ dùng bảng khi ≥3 mục × ≥2 thuộc tính. Cột chi phí hay thời lượng
   mang nhãn ở tiêu đề cột ("Thời lượng (ước tính)"), không lặp nhãn ở từng ô.
4. **Chi tiết kỹ thuật** — lớp hai, có tiêu đề riêng, người không chuyên bỏ qua được. Tối đa hai lớp.
5. **Bước tiếp theo** — ai làm gì, cần gì từ người đọc.

Không có bảng tóm tắt ở cuối, không lặp kết luận.

## 4. Danh sách cấm — và làm thay

| Cấm | Làm thay |
|---|---|
| Thuật ngữ không giải nghĩa | giải nghĩa ngắn trong ngoặc ở lần đầu: "migration (bước đổi cấu trúc dữ liệu)" |
| Mã trần (`TK4`, `RF2` không tên) | `TK4 (dựng script kiểm)` — mọi lần trong chat, lần đầu mỗi đoạn trong tài liệu |
| Liệt kê mã không có câu dẫn tài liệu + nghĩa in đậm | câu dẫn trước danh sách: "PLAN có 5 **task** (TK) và 2 **decision** (DN) cần anh quyết:" (skill `id-convention` mục 3) |
| Tự chế viết tắt | viết đủ từ, hoặc dùng mã đã có trong `id-convention` |
| Bảng cho 1–2 mục | câu hoặc gạch đầu dòng |
| Kể bước gọi tool ("em đã chạy grep, rồi đọc file…") | nêu kết quả và bằng chứng; bước đi vào PROGRESS nếu cần |
| Tóm tắt lặp ở cuối | bỏ; kết luận đã ở câu đầu |
| "Tùy" không kèm tiêu chí | "chọn A khi …, chọn B khi …" |
| Số liệu không nguồn ("thường nhanh gấp 5 lần") | số có nguồn (đo, tài liệu, lệnh), hoặc nói rõ **chưa đo** và đưa cách đo; không đưa số để lấp chỗ trống |
| Ước lượng do mình tự đưa mà không nhãn (con số hoặc khoảng có đơn vị thời gian, công sức hay tiền, người đọc chưa nêu và mình chưa đo) | gắn **(ước tính)** trong cùng câu hoặc cùng ô; nhiều ước lượng cùng loại thì gom vào một cột hay một danh sách và đặt nhãn một lần ở tiêu đề cột hoặc câu dẫn; chưa có căn cứ để ước thì viết **chưa đo**, đừng thay bằng số; cách lấy số thật nêu một lần; ước lượng không ai hỏi (lịch theo ngày) đẩy xuống lớp hai dưới một tiêu đề có nhãn; trước khi gửi rà lại mọi con số một lượt |
| Hỏi lẻ nhiều câu | gom thành một lượt hỏi, mỗi câu kèm phương án đề xuất |

## 5. Bất khả xâm phạm khi nén

Người đọc đòi "một dòng", "một từ", "ngắn thôi" → vẫn giữ nguyên:

- **Báo lỗi** (test hỏng, build hỏng) kèm tên hoặc số: "Chưa — 2/48 test hỏng".
- **Cảnh báo bảo mật** (CVE, secret lộ, quyền) — kể cả khi người dùng từng dặn "bỏ qua cảnh báo lặt vặt":
  mức cao trở lên không bao giờ là lặt vặt; một mệnh đề là đủ: "+ CVE cao ở `requests`".
- **Xác nhận thao tác phá hủy** đang chờ.
- **Số liệu và đơn vị, mã lỗi, đường dẫn, phiên bản.**
- **Chữ phủ định và giới hạn**: không / chưa / chỉ / trừ khi / tối đa.

Dạng ngắn nhất hợp lệ: `<kết luận một từ> — <điều chặn 1>, <điều chặn 2>`. Người dùng muốn đúng một từ thì
cho một từ **cộng** phần sau dấu gạch; đó là giới hạn của việc nén, không phải bất tuân.

## 6. Lối ra giải thích

Người đọc cần diễn giải (gõ `/explain` hoặc theo danh sách dấu hiệu vào ở `method/communication.md` mục 1) → dùng skill
`explain`: nó viết lại tin gần nhất bằng lời dễ hiểu, giữ nguyên mọi dữ kiện. Danh sách dấu hiệu vào/thoát chỉ nằm ở
`method/communication.md` mục 1. Lời yêu cầu trực tiếp của người đọc luôn thắng.

## 7. Tài liệu sprint

SPEC / PLAN / PROGRESS / REPORT viết giọng **người**, hai lớp (người / agent): `method/communication.md` mục 4. Mỗi mã
kèm tên lần đầu trong đoạn; bảng khi ≥3 mục; ưu tiên bằng chữ (Bắt buộc / Nên có / Có thì tốt / Không làm đợt này).

## 8. Khối rút gọn — chép vào brief subagent

```
Văn phong: câu đầu là kết luận/điều cần làm; không dẫn nhập, không kể bước gọi tool, không tóm tắt lặp.
Mã luôn kèm tên ngắn; trước danh sách mã có câu dẫn "<tài liệu> có N **<nghĩa>** (<mã>):".
Thuật ngữ giải nghĩa lần đầu. Bảng chỉ khi ≥3 mục × 2 thuộc tính.
Nén không bao giờ bỏ: báo lỗi, cảnh báo bảo mật, xác nhận thao tác phá hủy, số liệu + đơn vị, mã lỗi,
đường dẫn, chữ phủ định (không/chưa/chỉ/trừ khi). Số không có nguồn thì nói "chưa đo" + cách đo.
Ước lượng thời gian/công sức/tiền do mình đưa: nhãn "(ước tính)" cùng câu hoặc cùng ô, hoặc ở tiêu đề cột/câu dẫn của danh sách; chưa có căn cứ thì viết "chưa đo", không thay bằng số.
Báo cáo về điều phối: Kết quả / Chứng cứ / Còn mở / Cần người, ≤15 dòng, con trỏ file thay log.
Tin dựa trên file → câu dẫn kèm link `[tên:dòng](đường:dòng)`; hỏi người chốt → một dòng hỏi + phương án + dòng
KHUYẾN NGHỊ có lý do (im lặng không phải là duyệt). Luật đầy đủ: method/communication.md.
Người đọc cần diễn giải (dấu hiệu: method/communication.md mục 1) → giải thích theo góc người đọc, ví dụ đời thường,
chi tiết kỹ thuật tách cuối; về súc tích khi người đọc hiểu hoặc chuyển việc.
```
