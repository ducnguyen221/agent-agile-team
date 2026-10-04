---
id: SPR-01-spec
doc: spec
title: Sprint goal title
sprint: SPR-01
request: RQ-001
feature: FS-001
status: draft
size: medium
risk: normal
risk_tags: []
gate_1: pending
gate_1_at: null
gate_1_quote: null
roles:
  analyst: [T1, agent-a]
  business-reviewer: [T1, agent-c]
created: 2026-01-15
updated: 2026-01-15
links:
  plan: PLAN.md
  progress: PROGRESS.md
  report: REPORT.md
---

# Tên mục tiêu sprint — Đặc tả (SPEC)

<!-- SPEC trả lời: làm cái gì, cho ai, thế nào là xong. KHÔNG viết cách làm — đó là việc của PLAN.
     Mọi mã xuất hiện lần đầu trong một đoạn phải kèm tên ngắn: `FR2 (xuất báo cáo)`.
     Mức ưu tiên viết bằng chữ: Bắt buộc / Nên có / Có thì tốt / Không làm đợt này.
     Câu dẫn: trước mỗi bảng / danh sách mã ghi một câu nói tài liệu nào và mã là gì, nghĩa in đậm — ví dụ
     "SPEC có 3 **user story** (US):" (skill id-convention). -->

> **Kết luận:** <!-- MỘT câu: sprint làm gì, cho ai, xong khi nào. Người không chuyên đọc câu này là đủ. -->
> Sprint SPR-01 cho người dùng tra trạng thái đơn hàng trong một bước; xong khi SC1 (tra nhanh) đạt.

## 1. Bối cảnh

<!-- Vì sao cần làm. 3–6 gạch đầu dòng; số liệu phải có nguồn. Trỏ yêu cầu gốc RQ-NNN và tính năng FS-NNN.
     Việc sửa lỗi, cổng kiểm, hiệu năng: ghi số đo TRƯỚC sprint kèm lệnh đo — đó là bằng chứng gốc để VR so sau. -->

- Yêu cầu gốc: RQ-001 (tra trạng thái đơn hàng). Tính năng chạm tới: FS-001 (tra cứu đơn hàng).
- Hiện trạng: <!-- điều đang sai hoặc đang thiếu, kèm số đo trước sprint + lệnh đo nếu có -->

## 2. Câu chuyện người dùng

<!-- Mỗi dòng: "Là <ai>, tôi <muốn gì>, để <được gì>". Mã US + tên ngắn trong ngoặc. -->

SPEC có 1 **user story** (US):

| Mã | Câu chuyện | Ưu tiên |
|---|---|---|
| US1 (tra trạng thái nhanh) | Là nhân viên bán hàng, tôi xem trạng thái đơn bằng mã đơn, để trả lời khách ngay | Bắt buộc |

## 3. Yêu cầu chức năng

<!-- Mỗi FR trỏ ít nhất một US. Một FR một hành vi: nhiều phản ứng khác nhau thì tách thành nhiều FR. Mỗi kịch bản
     là một FRx.y viết dạng KHI … THÌ …; kịch bản là thứ đem đi kiểm.
     Delta so với spec sống: FR đổi hành vi đang có ghi "(sửa FS-001/FR1.2)", FR bỏ hành vi đang có ghi
     "(bỏ FS-001/FR1.2)" ở cuối dòng; FR không ghi gì là Thêm. Bước 5 gộp vào spec sống theo đúng delta này. -->

SPEC có 1 **functional requirement** (FR); mỗi kịch bản KHI … THÌ … là một mã con:

### FR1 — Tra đơn theo mã (→ US1)

- **FR1.1 (mã đúng):** KHI người dùng nhập mã đơn tồn tại THÌ hệ thống hiện trạng thái hiện tại và thời điểm cập nhật.
- **FR1.2 (mã sai):** KHI mã đơn không tồn tại THÌ hệ thống báo "không tìm thấy" và không lộ dữ liệu đơn khác.

## 4. Tiêu chí thành công

<!-- Mỗi SC đo được: có lệnh/thao tác và ngưỡng. REPORT sẽ có đúng một hoặc nhiều VR cho mỗi SC. -->

SPEC có 1 **success criterion** (SC):

| Mã | Tiêu chí | Cách đo |
|---|---|---|
| SC1 (tra nhanh) | 100% kịch bản FR1 chạy đúng | Bộ test tự động của FR1 xanh |

## 5. Ngoài phạm vi

<!-- Những gì KHÔNG làm trong sprint này, để reviewer không đòi thêm. Không có thì ghi "Không có." -->

- Sửa trạng thái đơn (chỉ tra cứu).

## 6. Câu hỏi cần làm rõ

<!-- Gom MỌI điểm chưa rõ vào đây để hỏi một lần ở Cổng 1, không hỏi lẻ. Không có thì ghi "Không có."
     Giả định đang dùng ghi dưới nhãn **ASSUMPTION** để người duyệt chỉ cần lên tiếng nếu không đồng ý. -->

SPEC có 1 **clarification question** (CQ) cần người dùng trả lời ở Cổng 1:

| Mã | Câu hỏi | Đề xuất | Trạng thái |
|---|---|---|---|
| CQ1 (phạm vi người xem) | Khách hàng có được tự tra không, hay chỉ nhân viên? | Chỉ nhân viên trong sprint này | mở |

- **ASSUMPTION — nguồn dữ liệu:** trạng thái đơn đọc từ hệ thống hiện có, không tạo kho mới.

## 7. Đổi hợp đồng / giao diện

<!-- Thứ bên khác đang dùng: API, sự kiện, schema dữ liệu, tham số CLI, định dạng file. Bắt buộc khi cỡ lớn
     hoặc risk_tags có public_api; cỡ khác xoá mục. Bắt buộc mà không đổi gì thì ghi "Không có.". Mỗi dòng:
     thay đổi · Thêm / Sửa / Bỏ · payload hoặc chữ ký trước → sau · bên dùng bị ảnh hưởng (có bằng chứng: grep
     bên gọi, client sinh, log truy cập) · tương thích ngược? · lộ trình deprecate (phiên bản mới hoặc giai
     đoạn chuyển + ngày bỏ).
     Thay đổi phá vỡ (bỏ/đổi tên trường, đổi kiểu, đổi URL, đổi cách xác thực) cần lộ trình deprecate và ADR —
     xem skill api-design, adr. -->

| Thay đổi | Kiểu | Trước → sau | Bên dùng bị ảnh hưởng | Tương thích ngược | Lộ trình deprecate |
|---|---|---|---|---|---|
| Endpoint tra trạng thái đơn | Thêm | — → `GET /orders/{code}/status` trả `{status, updated_at}` | Màn hình bán hàng (bên gọi mới) | Có — chỉ thêm | Không cần |

## 8. Truy vết

<!-- Nên có từ cỡ vừa trở lên: mỗi US có FR và SC tương ứng. Cỡ nhỏ được bỏ mục này. -->

| Câu chuyện | Yêu cầu | Tiêu chí |
|---|---|---|
| US1 (tra trạng thái nhanh) | FR1 | SC1 |
