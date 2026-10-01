---
name: adr
description: Use when a decision is hard to reverse or affects several parts of the system (choosing a platform, framework, datastore or auth model, changing a contract or data model, adding a cross-service dependency, dropping a technology), when a large-size task needs its architecture decisions recorded, when a reviewer asks for an ADR, or when an accepted ADR must be superseded.
metadata:
  group: technique
  kind: reference
  roles: [architect]
source: academy skills/adr-writer/SKILL.md (private copy)
source_sha: 4c0fdc5736a49b6223a7dfc7626d5495cf55185c
license: none
rewrite_before_public: true
---

# Ghi quyết định kiến trúc (ADR)

> **Kết luận:** quyết định **khó đảo ngược** hoặc chạm nhiều phần thì ghi thành một ADR ngắn (dưới một
> trang) ở `docs/architecture/adr/NNNN-<slug>.md` (chỉnh qua `paths.adr_dir`), có **ít nhất hai lựa chọn
> thật** đã cân nhắc. ADR đã chấp nhận thì **không sửa nội dung**; đổi ý = ADR mới thay thế, ADR cũ chỉ đổi
> trạng thái.

## 1. Khi nào viết

- Chọn nền tảng, framework, kho dữ liệu, mô hình xác thực; thêm phụ thuộc xuyên service; đổi hợp đồng
  hoặc mô hình dữ liệu; bỏ một công nghệ.
- Việc cỡ **lớn**: luôn có ít nhất một ADR, hoặc PLAN ghi rõ "không có quyết định kiến trúc mới"
  (`method/sizing.md`, `method/conventions.md` mục 3).
- Reviewer nói "cái này cần ADR trước khi gộp"; một tranh luận thiết kế kéo dài cần chốt.

**Không viết khi:** refactor thẩm mỹ không ảnh hưởng kiến trúc (sửa mã là đủ) · đổi luật hay quy trình
làm việc (thuộc file luật của dự án, không phải ADR) · đổi API/sự kiện/schema đơn thuần → mục **Đổi hợp đồng
/ giao diện** trong SPEC (liệt kê consumer, delta thêm/sửa/bỏ — skill `api-design`); chỉ thêm ADR khi đằng
sau nó là một quyết định kiến trúc.

## 2. Đầu vào

Tiêu đề (mệnh đề ngắn, ví dụ "Dùng Postgres làm kho OLTP chính") · bối cảnh: vấn đề, ràng buộc, ai bị ảnh
hưởng · **≥2 lựa chọn** mỗi cái có đánh đổi, chi phí, rủi ro · lựa chọn được chọn và vì sao · hệ quả: cái
gì dễ hơn, khó hơn, cái gì từ nay không thương lượng.

## 3. Các bước

1. Lấy số tiếp theo: số lớn nhất trong thư mục ADR + 1; bốn chữ số, không tái dùng số của ADR đã bỏ.
2. Tạo `NNNN-<slug>.md` (slug tiếng Anh ngắn, chữ thường, gạch nối) theo khuôn mục 4.
3. Điền đủ các mục; trạng thái ban đầu `proposed`.
4. Dự án có mục lục ADR → thêm một dòng. PLAN trỏ tới ADR (mục Kiến trúc), không chép nội dung.
5. ADR đi qua kiểm định cùng PLAN/sprint (Tech Reviewer); được duyệt ở Cổng 1 hoặc Cổng 2 → `accepted`.
6. Thay ADR cũ: ADR mới ghi `supersedes: NNNN`; ADR cũ **chỉ** đổi trạng thái thành
   `superseded by NNNN` — không sửa, không xoá phần còn lại.

## 4. Khuôn

```markdown
# NNNN — <Tiêu đề quyết định>

- **Trạng thái:** proposed | accepted | superseded by NNNN
- **Ngày:** YYYY-MM-DD · **Người viết:** <vai> · **Sprint:** SPR-NN

## Bối cảnh
Vấn đề cần giải, ràng buộc (kỹ thuật, thời gian, đội), ai/cái gì bị ảnh hưởng.

## Quyết định
Một câu khẳng định: "Chúng ta dùng X cho Y."

## Lựa chọn đã cân nhắc
| Cách làm | Đánh đổi & rủi ro | Chi phí | Khi nào nên chọn |
|---|---|---|---|
| X (đã chọn) | … | … | … |
| Z | … | … | … |

## Hệ quả
Được gì · mất gì · việc phải làm theo (migration, tài liệu, giám sát) · điều từ nay không thương lượng.

## Liên kết
SPEC/PLAN của sprint, ADR liên quan, tài liệu thiết kế chi tiết.
```

Dài hơn một trang → tách phần phụ lục sang tài liệu thiết kế và trỏ tới.

## 5. Điểm dừng

- **Chỉ có một lựa chọn thật** → ADR một lựa chọn là diễn kịch: đưa thêm lựa chọn khả dĩ (kể cả "giữ
  nguyên hiện trạng") hoặc nói rõ vì sao không có lựa chọn khác.
- **Quyết định chạm bảo mật, dữ liệu cá nhân, quyền** → bắt buộc Tech Reviewer chuyên đề bảo mật/dữ liệu
  review ADR trước khi `accepted` (skill `security-review`).
- Quyết định đổi tiêu chí thành công của sprint → PLAN hỏng: ghi `BR`, đưa lên người dùng.
