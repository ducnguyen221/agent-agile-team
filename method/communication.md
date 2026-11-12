# Trao đổi agent–người

> **Kết luận:** agent nói với người theo hai chế độ — **súc tích** (mặc định) và **diễn giải** (khi người đọc cần) —
> và mỗi tin dựa trên file thì kèm **link tới file đó**, mỗi câu hỏi cần người chốt thì kèm **phương án và khuyến
> nghị**. Tài liệu sprint có hai lớp: lớp một cho người, lớp hai cho agent. Đây là nơi chuẩn của các luật đó;
> `AGENTS.md`, skill `response-style`, skill `explain` và mẫu chỉ **trỏ tới**, không chép lại.

Luật không đổi (nằm ở `AGENTS.md` mục Văn phong phản hồi và skill `response-style` mục 5): dù nén hay diễn giải,
**không bao giờ mất** báo lỗi, cảnh báo bảo mật, xác nhận thao tác phá hủy, số liệu + đơn vị, đường dẫn, mã lỗi,
chữ phủ định.

## 1. Hai chế độ trả lời

| | Súc tích (mặc định) | Diễn giải |
|---|---|---|
| Dấu hiệu vào | không có yêu cầu khác | người dùng gõ `/explain` (kèm đường dẫn thì diễn giải file đó), hoặc nói "giải thích", "diễn giải", "nói dễ hiểu hơn", "chưa hiểu", "tại sao"; hỏi lại cùng một điểm; hậu quả khó hoàn tác |
| Cách trả lời | theo `skills/response-style`: câu đầu là kết luận, không dẫn nhập, không tóm tắt lặp | viết lại **tin gần nhất** (hoặc đoạn/file người dùng chỉ) bằng lời dễ hiểu — xem skill `explain` |
| Dấu hiệu thoát | — | người dùng hiểu hoặc chuyển việc: tin sau về súc tích; "diễn giải từ giờ" giữ chế độ cả phiên; "ngắn gọn lại" về mặc định |

- Mặc định phải súc tích để tiết kiệm token; chế độ diễn giải **chỉ bật theo yêu cầu**, trừ việc có hậu quả khó hoàn
  tác (mục 3 dưới đây).
- Host không có lệnh gạch chéo thì câu của người dùng có tác dụng như lệnh. Lời yêu cầu trực tiếp của người dùng
  luôn thắng.
- **Cách diễn giải:** mở bằng kết luận một câu; giải nghĩa mọi viết tắt và thuật ngữ ở lần đầu; bỏ mã trần; ví dụ
  đời thường cho khái niệm khó; nêu chuyện gì xảy ra, ảnh hưởng gì tới người đọc, tốn gì, rủi ro gì, có đường lui
  không; "Chi tiết kỹ thuật" tách xuống cuối; kết bằng điều người đọc cần quyết kèm khuyến nghị.
- **Giữ nguyên dữ kiện:** diễn giải làm rõ, không bỏ, không thêm sự kiện. Số liệu + đơn vị, đường dẫn, mã lỗi,
  chữ phủ định, cảnh báo bảo mật của nguồn còn nguyên; cảnh báo và hậu quả khó hoàn tác đưa lên **đầu** tin. Chỗ
  nguồn mơ hồ thì ghi "nguồn không nói rõ" thay vì đoán.

## 2. Link tới file chi tiết

- **Dạng link:** `[tên ngắn](đường/dẫn.md:dòng)` — đường dẫn **tương đối** theo thư mục làm việc của phiên (dạng
  `[tên:dòng](đường:dòng)` đúng chỉ dẫn của ứng dụng Claude Desktop); `:dòng` khi trỏ một mục cụ thể (một `TK`,
  `DN`, `RF`…). Không dùng đường tuyệt đối trong link bấm; không bọc link trong khối code.
- **Khi nào bắt buộc:** tin có (a) danh sách hay bảng mã lấy từ một tài liệu, (b) tóm tắt nội dung một file, (c) câu
  hỏi cần người quyết dựa trên chi tiết trong file, hoặc (d) tin dừng, tin mở sprint, tin cuối. **Trước** danh
  sách, bảng hay câu hỏi đó có một câu dẫn kèm link tới tài liệu nguồn. Câu dẫn của skill `id-convention` ("SPEC
  có 3 **user story** (US):") giữ nguyên, tên tài liệu trong đó thành link.
- **Khi nào không cần:** câu trả lời không dựa trên file nào, hoặc là xác nhận 1–3 câu. Không thêm link cho đẹp.
- **File ngoài thư mục phiên** (ví dụ hồ sơ ở nơi khác khi phiên mở ở repo mã): trước hết dùng cơ chế của host để
  mở thư mục hoặc gửi file, nếu có. Không có thì nêu đường dẫn tuyệt đối trong dấu code **và** một câu nói rõ
  "file ngoài thư mục phiên, cần mở thư mục để bấm được"; không giả làm link bấm được.
- **Không để link gãy:** file có thật và dòng nằm trong file tại lúc gửi; file vừa đổi thì dùng mã (`TK4`) thay số
  dòng.

Đúng: `PLAN có 4 **task** (TK) — chi tiết ở [PLAN.md](docs/plans/x/PLAN.md:97):` · Sai: `Xem file PLAN` (không link) ·
Sai: `` `[PLAN](PLAN.md:97)` `` (link bọc trong khối code).

## 3. Câu hỏi cần người quyết

Khi agent cần người chốt một việc, tin có đúng bốn phần theo thứ tự:

1. **Một dòng câu hỏi** kết thúc bằng dấu hỏi, mở bằng `**Cần anh quyết:**` (đổi "anh" theo cách người dùng xưng hô).
2. **Câu dẫn kèm link** tới file chi tiết (mục 2): `Chi tiết: [<tài liệu> mục N](<đường>:<dòng>)`.
3. **Phương án** — bảng khi ≥ 3 phương án × ≥ 2 thuộc tính, ngược lại danh sách; mỗi phương án nêu đánh đổi và
   rủi ro, công sức, khi nào nên chọn.
4. **`KHUYẾN NGHỊ:`** phương án nghiêng về + lý do một câu + việc chờ hoặc việc làm tiếp được nếu người chưa trả
   lời. **Im lặng không bao giờ là duyệt** cổng, lượt 5 ý hay việc không đảo ngược.

Mẫu điền sẵn:

```
**Cần anh quyết:** chia khúc tệp xuất > 50 MB ngay trong sprint này hay để sprint sau?
Chi tiết: [PLAN mục TK3](docs/plans/x/PLAN.md:97).
| Phương án | Đánh đổi · rủi ro | Công sức | Chọn khi |
|---|---|---|---|
| A. Làm ngay | tránh sửa gấp; rủi ro bộ nhớ trên máy 2 GB | +1 phiên | đã có đơn lớn |
| B. Để sprint sau | xuất lỗi nếu gặp tệp lớn sớm | 0 | chưa có đơn lớn |
**KHUYẾN NGHỊ:** B — chưa có đơn nào > 50 MB. Nếu anh chưa trả lời, em làm tiếp TK1–TK2 và giữ TK3 chờ.
```

- Luôn có khuyến nghị khi người sẽ phải chọn; chưa có thì ghi "chưa có khuyến nghị vì …" và nêu tiêu chí để chọn.
  Cấm "tùy" không kèm tiêu chí.
- Nhiều câu hỏi cùng lúc thì gom thành **một** tin, nêu số lượng đầu tin ("có 3 **quyết định** (DN) chờ anh:"), mỗi
  câu theo bốn phần trên.
- Quyết định **không đảo ngược được** thì riêng câu hỏi đó chuyển sang chế độ diễn giải (mục 1) trước khi hỏi.

## 4. Tài liệu sprint hai lớp

- **Lớp một (người):** khối `> **Kết luận:**` một câu và mục `## Tóm tắt cho người không chuyên` (3–5 câu: việc gì ·
  vì sao · ảnh hưởng tới người · rủi ro · người cần làm/quyết gì). Không mã trần, viết tắt có nghĩa ở lần đầu.
- **Lớp hai (agent):** bảng, mã, `file:dòng`, lệnh, bằng chứng.
- Không lặp cùng một dữ kiện ở hai lớp; lớp một trỏ xuống mã. Mục tóm tắt còn nguyên chú thích của mẫu tính là rỗng.
- SPEC, PLAN và REPORT có mục tóm tắt ngay sau khối Kết luận. Câu Kết luận của PROGRESS viết bằng lời thường, không
  mã trần, số đếm đúng.

## 5. Điều này không đổi

Skill `response-style` mục 5 (bất khả xâm phạm khi nén) và `AGENTS.md` mục Văn phong phản hồi vẫn là luật của mặc
định súc tích; file này chỉ thêm link, mẫu câu hỏi, chế độ diễn giải và hai lớp tài liệu. Hai chỗ nói khác nhau
thì file ở `method/` thắng và chỗ kia sửa theo.
