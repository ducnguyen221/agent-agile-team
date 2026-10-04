---
name: adr
description: Use when a technical decision will be hard to undo or will touch several parts of a system - platform, framework, datastore, auth model, a changed contract or data model, a new cross-service dependency - when a large-size task needs its design choices written down, or when an accepted decision is being replaced.
metadata:
  group: technique
  kind: reference
  roles: [architect]
source: "concept: architecture decision records - short, numbered, at least two real options, superseded not edited (clean-room rewrite: old text removed first, new writer saw only a noun-phrase idea list; task `TK10` (clean-room rewrite), sprint `SPR-04` (method wave 3))"
source_sha: null
license: none
rewrite_before_public: false
---

# Ghi quyết định kiến trúc (ADR)

> **Kết luận:** một ADR dài một trang và chỉ nói về **một** quyết định bền: đang giải vấn đề gì, đã cân những
> phương án thật nào, vì sao chọn, và sẽ phải trả giá gì về sau. Mỗi ADR có số riêng, đứng trong thư mục ADR của dự án, được review cùng PLAN
> trước Cổng 1. Quyết định đổi thì viết ADR mới thay thế; ADR cũ giữ nguyên chữ, chỉ đổi trạng thái.

## 1. Khi nào viết

Viết ADR khi **một** trong các điều sau đúng:

- Một lựa chọn đắt để rút lại: nền tảng chạy, framework, nơi lưu dữ liệu, cách đăng nhập.
- Đổi hợp đồng giữa các phần, hoặc đổi mô hình dữ liệu.
- Tạo phụ thuộc mới giữa hai phần vốn độc lập, hoặc bỏ một công nghệ đang dùng.
- Việc cỡ lớn (`method/sizing.md`): PLAN phải có ít nhất một ADR; nếu thật sự không có quyết định nào cần
  ghi thì PLAN nói thẳng điều đó và nêu lý do.
- Một ADR đã chấp nhận nay bị thay.

**Không cần ADR:** đổi cục bộ sửa lại trong một sprint là xong; chọn thư viện nhỏ thay được trong một buổi;
quy ước đặt tên hay định dạng; lỗi sửa mà không đổi cấu trúc. Phép thử: quay lại sau ba tháng mà tốn công
đáng kể thì cần ADR, không tốn thì không.

## 2. Nội dung một ADR

| Phần | Phải có |
|---|---|
| Tiêu đề | một **mệnh đề quyết định** ("Dùng Postgres làm kho chính"), không phải chủ đề ("Về cơ sở dữ liệu") |
| Bối cảnh | vấn đề đang giải, ràng buộc thật (kỹ thuật, nhân lực, thời hạn, chi phí), ai chịu ảnh hưởng |
| Lựa chọn | **tối thiểu hai**; mỗi lựa chọn một dòng: cách làm · đánh đổi · khi nào hợp. "Giữ nguyên hiện trạng" là một lựa chọn hợp lệ và thường phải có mặt |
| Quyết định | một câu nói đã chọn gì, rồi lý do **bám vào ràng buộc** đã liệt kê ở Bối cảnh, không bám sở thích |
| Hệ quả | việc nào thành dễ · việc nào thành khó · thứ gì bị đóng khuôn từ nay; kèm **đường lùi** nếu chọn sai và giá của đường lùi đó |
| Trạng thái | `proposed` · `accepted` · `superseded by NNNN` |
| Liên kết | sprint (`SPR-`) sinh ra nó, PLAN, ADR liên quan |

Lựa chọn chỉ có một, hoặc các lựa chọn khác là hình nộm ("làm dở", "không làm gì cả" mà không phân tích) thì
chưa phải quyết định mà là lời biện hộ: quay lại tìm phương án thật.

Khuôn một trang:

```markdown
# NNNN. <mệnh đề quyết định>

Trạng thái: proposed · Sprint: SPR-NN · Liên quan: ADR NNNN, PLAN mục <tên>

## Bối cảnh
<vấn đề, ràng buộc, bên chịu ảnh hưởng>

## Lựa chọn
| Cách làm | Đánh đổi | Khi nào hợp |
|---|---|---|

## Quyết định
<một câu> — vì <ràng buộc nào>.

## Hệ quả
- Dễ hơn: …
- Khó hơn: …
- Bị cố định: …
- Quay lại: <các bước + chi phí>
```

## 3. Đánh số và nơi đặt

- Thư mục lấy từ `paths.adr_dir` trong `.agile.json` (mặc định `docs/architecture/adr`); tên file
  `NNNN-<slug>.md`, slug tiếng Anh ngắn. Đừng viết cứng đường dẫn khi đã có cấu hình.
- Số bốn chữ số: lấy số lớn nhất đang có trong thư mục rồi cộng một. **Không tái dùng** số, kể cả khi ADR
  bị bỏ dở; số trống chỉ là số trống.

## 4. Vòng đời

1. Architect viết bản `proposed` trong lúc lập PLAN.
2. ADR đi cùng PLAN vào review (Tech Reviewer từ cỡ vừa) **trước Cổng 1**; PLAN trỏ tới ADR bằng số, đường
   file và mệnh đề quyết định, không chép lại thân ADR.
3. Người dùng duyệt ở Cổng 1 → đổi sang `accepted`. Chưa duyệt thì không code theo ADR đó.
4. Khi phải đổi hướng: viết một ADR mới, ghi rõ nó thế chỗ ADR nào; ở ADR cũ chỉ sửa dòng trạng thái thành
   `superseded by NNNN`. **Không xoá, không sửa chữ** của bản cũ — lịch sử lý do là giá trị của ADR.

## 5. Điểm dừng

- Quyết định chạm secret, xác thực hay dữ liệu thật → điều kiện dừng (b) hoặc (a) của `method/process.md`;
  ADR chỉ ghi hướng, không thay cho việc hỏi người dùng.
- Hai lựa chọn ngang nhau mà cần người dùng chọn → ghi thành `DN` trong PLAN, không tự chốt trong ADR.
- Quyết định đã `accepted` nhưng mã đang làm khác đi → không sửa ADR cho khớp mã; mở ADR thay thế hoặc sửa
  mã.

## 6. Lỗi hay gặp

| Lỗi | Sửa |
|---|---|
| ADR viết **sau** khi code xong, chỉ để hợp thức hoá | viết khi còn chọn được; ghi lựa chọn đã bỏ là gì |
| Tiêu đề là chủ đề, không phải quyết định | đổi thành mệnh đề: ai làm gì |
| Chỉ một lựa chọn | thêm "giữ nguyên" và ít nhất một phương án khác |
| Hệ quả chỉ nêu ưu điểm | bắt buộc ghi mặt khó hơn và cách quay lại |
| Sửa ADR cũ cho khớp thực tế mới | ADR mới thay thế, cũ đổi trạng thái |
| Mỗi lần đổi nhỏ đều thành ADR | quay lại mục 1, áp phép thử ba tháng |
