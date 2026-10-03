---
name: adr
description: Use when a technical decision is expensive to undo or reaches across several parts of a system - picking a platform, framework, datastore or authentication model, changing a data model or a contract between services, adding a cross-service dependency, retiring a technology - when a large-size task needs its design choices written down, when a reviewer insists on a written decision record, or when a decision accepted earlier is being overturned.
metadata:
  group: technique
  kind: reference
  roles: [architect]
source: "concept: architecture decision records - short, numbered, at least two real options, superseded not edited (clean-room rewrite from an idea list)"
source_sha: null
license: none
rewrite_before_public: false
---

# Ghi quyết định kiến trúc (ADR)

> **Kết luận:** ADR là **một trang** ghi một quyết định khó đảo ngược: bối cảnh, một câu quyết định, **ít
> nhất hai lựa chọn thật** trong bảng bốn cột, hệ quả. Số bốn chữ số tăng dần, không cấp lại; trạng thái
> `proposed` → `accepted` khi người dùng duyệt ở cổng; PLAN **trỏ** tới ADR chứ không chép. Muốn lật một quyết
> định đã chốt: viết bản mới; bản cũ giữ nguyên chữ và file, chỉ nhận nhãn `superseded by` trỏ sang bản mới.

## 1. Khi nào

| Viết ADR | Không viết ADR — làm gì thay |
|---|---|
| Cách xác thực người dùng; nơi lưu dữ liệu; framework hay nền tảng để chạy | Refactor không đổi kiến trúc → mô tả trong `TK` của PLAN |
| Thêm phụ thuộc giữa các service; bỏ một công nghệ đang dùng | Đổi luật, quy trình làm việc → file luật của dự án |
| Đổi mô hình dữ liệu hay hợp đồng giữa các phần | Đổi một endpoint / một schema đơn thuần → mục "Đổi hợp đồng / giao diện" của SPEC (skill `api-design`); chỉ thêm ADR khi đằng sau có một lựa chọn kiến trúc |
| Sprint cỡ **lớn** — mặc định phải có ADR; sprint lớn mà thật sự không chọn gì về kiến trúc thì PLAN nói thẳng điều đó trong một câu (luật ở `method/sizing.md`, `method/conventions.md` mục 3) | Lựa chọn tương đương, dễ đổi lại (tên thư viện tiện ích, kiểu đặt tên) → dòng `Phán quyết:` trong PROGRESS |
| Reviewer đòi ADR; cuộc tranh luận thiết kế cần được chốt lại thành chữ | — |

Phép thử nhanh: nếu sáu tháng sau có người hỏi "sao hồi đó lại chọn thế này?" mà câu trả lời tốn hơn một
buổi để dựng lại, thì đó là ADR.

## 2. Đầu vào

- **Mệnh đề quyết định** — sẽ thành tiêu đề ("Dùng hàng đợi bền cho thông báo", không phải "Về hàng đợi").
- **Bối cảnh:** vấn đề cần quyết, ràng buộc (kỹ thuật, chi phí, pháp lý, thời hạn), ai và cái gì chịu ảnh hưởng.
- **Ít nhất hai lựa chọn**, mỗi lựa chọn có đánh đổi, chi phí, rủi ro; "giữ nguyên hiện trạng" là lựa chọn hợp lệ.
- **Lựa chọn được chọn và lý do** — lý do trỏ về ràng buộc ở bối cảnh, không phải sở thích.
- **Hệ quả:** cái gì dễ hơn, cái gì khó hơn, điều gì từ nay cố định (muốn đổi phải có ADR mới).

## 3. Các bước

1. **Lấy số:** xem thư mục ADR, lấy số lớn nhất + 1, viết đủ bốn chữ số (`0007`). Số đã cấp không bao giờ cấp
   lại, kể cả khi bản nháp bị bỏ.
2. **Đặt file:** `docs/architecture/adr/NNNN-<slug>.md` — dự án đổi thư mục qua `paths.adr_dir` của
   `.agile.json`. Slug tiếng Anh, chữ thường, nối bằng gạch (`0007-durable-notification-queue`).
3. **Viết theo khuôn** (mục 4), trạng thái `proposed`. Dài quá một trang → đẩy chi tiết sang phụ lục hay tài
   liệu thiết kế riêng, ADR chỉ trỏ tới.
4. **Review cùng PLAN:** Tech Reviewer đọc ADR trong lượt review PLAN (skill `plan-review`). ADR chuyển
   `accepted` khi người dùng duyệt PLAN ở Cổng 1; quyết định nảy ra giữa sprint thì trình kèm Cổng 2.
5. **Nối dây:** PLAN trỏ ADR bằng số + đường + câu quyết định — không chép bối cảnh hay bảng. Dự án có mục lục
   ADR (ví dụ `README.md` trong thư mục ADR) thì thêm một dòng: số · tiêu đề · trạng thái · ngày.
6. **Thay thế:** ADR mới ghi "Thay thế: NNNN" ở phần đầu. ADR cũ chỉ đổi dòng trạng thái thành
   `superseded by MMMM`; thân giữ nguyên, file không xoá — lịch sử lý do là thứ ADR sinh ra để giữ.

## 4. Khuôn

```markdown
# NNNN — <mệnh đề quyết định>

- **Trạng thái:** proposed | accepted | superseded by MMMM
- **Ngày:** YYYY-MM-DD · **Người viết:** <vai · tier> · **Sprint:** SPR-xx
- **Thay thế:** <NNNN | không>

## Bối cảnh

<vấn đề cần quyết; ràng buộc; ai và cái gì chịu ảnh hưởng>

## Quyết định

<một câu khẳng định, ví dụ: "Thông báo đi qua hàng đợi bền; dịch vụ gửi đọc từ hàng đợi.">

## Lựa chọn đã cân nhắc

| Cách làm | Đánh đổi & rủi ro | Chi phí / công sức | Khi nào nên chọn |
|---|---|---|---|
| <A> (chọn) | … | … | … |
| <B> | … | … | … |
| Giữ nguyên hiện trạng | … | … | … |

## Hệ quả

- Dễ hơn: …
- Khó hơn / mất đi: …
- Từ nay cố định: <điều không mở lại nếu không có ADR mới>
- Việc kéo theo: <việc trong PLAN hay dòng sổ yêu cầu>

## Liên kết

SPEC và PLAN của SPR-xx · ADR liên quan · tài liệu ngoài (nếu có)
```

Bảng lựa chọn dùng đúng bốn cột của bảng lựa chọn trong luật lõi, để người đọc ADR và người đọc lời trình
cổng thấy cùng một hình.

## 5. Điểm dừng

| Gặp | Làm |
|---|---|
| Chỉ có một lựa chọn thật — bảng lựa chọn thành màn diễn | bổ sung phương án thật (giữ hiện trạng cũng tính), hoặc nêu tên ràng buộc đã loại hết các phương án kia |
| Quyết định chạm bảo mật, dữ liệu cá nhân, phân quyền | reviewer chuyên đề bảo mật (skill `security-review`) đọc trước khi `accepted`; `risk_tags` của sprint ghi tương ứng |
| Quyết định làm đổi `SC` của sprint đang chạy | PLAN hỏng — điều kiện dừng (d): `BR`, báo Analyst |
| Thực hiện quyết định không đảo ngược được (xoá dữ liệu, gỡ dịch vụ đang chạy) | điều kiện dừng (a): chỉ làm khi người dùng gật |
| Muốn sửa nội dung một ADR đã `accepted` | không sửa — viết ADR mới thay thế (mục 3 bước 6) |
