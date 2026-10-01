---
name: shaping-spec
description: Use when a request has been registered and a SPEC must be written before any code — turning intent into user stories, WHEN…THEN scenarios, measurable success criteria, out-of-scope items and one batch of clarification questions; also when deciding whether the work is a spike, a bounded change or an architectural change.
metadata:
  group: process
  roles: [analyst, architect]
source: obra/superpowers skills/brainstorming/SKILL.md
source_sha: 8ca22dba9a94f28898bbce59f2537ff4d87c747d
license: MIT
rewrite_before_public: false
---

# Định hình SPEC (Bước 2, nửa đầu)

> **Kết luận:** chọn đường (Spike / Bounded / Architectural) rồi nói ra để người dùng sửa; phân vân
> thì chọn đường **nặng hơn**, chỉ nâng không hạ; viết SPEC theo mẫu (`US` · `FR` kịch bản KHI…THÌ…
> · `SC` · ngoài phạm vi · `CQ`); tự review 4 điểm; **không viết code trước Cổng 1**, và mỗi lời
> duyệt chỉ duyệt đúng giai đoạn đang trình.

## 1. Ba đường — nói ra trước câu hỏi đầu tiên

| Đường | Dấu hiệu | Sản phẩm | Cỡ tương ứng |
|---|---|---|---|
| **Spike** | câu hỏi khả thi ("làm được không", "thử nhanh") — đầu ra là **câu trả lời**, không phải code giữ lại | 2–3 câu nêu câu hỏi + cách thử; kết quả chỉ vào SPEC/PLAN, code thử gắn nhãn vứt bỏ | thường rất nhỏ / nhỏ; sprint riêng nếu người dùng muốn giữ code |
| **Bounded** | sửa một luồng **đã có trong repo**: cờ mới, endpoint nhỏ, sửa một file | SPEC ngắn; hiểu kiểu ứng dụng chưa đủ — "bounded" đo trên repo, không đo trên sự quen thuộc của agent | nhỏ |
| **Architectural** | dự án mới, hệ con mới, đổi cách các phần ghép nhau, đổi giao diện người khác phụ thuộc | SPEC đầy đủ, PLAN đầy đủ, cỡ lớn có mục "Đổi hợp đồng / giao diện" | vừa / lớn |

Nói ra phân loại ("việc này bounded, tôi viết SPEC ngắn") để người dùng đè. Phát hiện độ phức tạp
ẩn giữa chừng → **dừng, nói rõ, nâng đường**; không bao giờ hạ giữa chừng. Thấy mình với tay lấy nhãn
nhẹ để khỏi viết SPEC thì đó chính là lúc chọn nhãn nặng.

## 2. Hiểu đúng ý trước khi viết

1. **Tìm ý định:** kết quả mong muốn, cho ai, thế nào là thành công. Biết "kiểu ứng dụng" không cho
   biết vì sao người dùng cần nó.
2. **Viết lại cách hiểu** thành khối ngắn người dùng kiểm được: tách *điều họ nói* khỏi *giả định của
   mình* (nhãn ASSUMPTION từ skill `intake`).
3. **Đánh giá phạm vi trước khi hỏi chi tiết:** lời giao chứa nhiều hệ con độc lập → tách sprint
   trước, mỗi sprint một SPEC; đừng tốn câu hỏi để tinh chỉnh một việc cần tách.
4. **Đọc repo trước:** cấu trúc, tài liệu, commit gần đây, spec sống `FS-` liên quan. Theo khuôn có sẵn;
   chỉ đề xuất cải thiện cục bộ ở chỗ việc này chạm, không refactor lan.

## 3. Hỏi thế nào — một câu mỗi tin hay gom `CQ`

| Tình huống | Cách hỏi |
|---|---|
| Mặc định: phiên chạy liên tục, các điểm chưa rõ độc lập nhau | **gom `CQ`** vào SPEC, mỗi `CQ` kèm đề xuất; hỏi một lần ở Cổng 1 cùng bản trình chuẩn |
| Người dùng **mở chế độ làm rõ** ("bàn với tôi", "cùng nghĩ", "hỏi tôi từng điểm"), hoặc câu sau phụ thuộc câu trước (chọn xong phương án mới hỏi được câu con của nó) | **một câu mỗi tin**, ưu tiên trắc nghiệm có đề xuất; xong chuỗi thì chốt lại vào `CQ` với trạng thái `đã trả lời` |
| Điểm thuộc ý muốn người dùng mà tra repo không ra | `CQ` |
| Điểm tra được từ repo/tài liệu | tra, không hỏi |

Ngoài chế độ làm rõ, hỏi lẻ giữa Bước 2–5 là lỗi quy trình (đếm được: số lần hỏi ngoài cổng = 0).

## 4. Khám phá cách làm (đường Architectural)

- Đề xuất **2–3 cách làm** dạng bảng (cách làm · đánh đổi & rủi ro · chi phí · khi nào chọn), dẫn đầu
  bằng cách **khuyến nghị** và lý do. YAGNI: cắt tính năng không cần ở mọi phương án.
- Thiết kế theo đơn vị nhỏ, một mục đích, giao diện rõ, kiểm độc lập được: với mỗi đơn vị trả lời
  được *làm gì · dùng thế nào · phụ thuộc gì*; đổi ruột mà không vỡ bên gọi.
- Cách làm đã chọn ghi tóm tắt vào SPEC mục Bối cảnh (một đoạn); chi tiết kiến trúc là việc của PLAN
  (skill `writing-plan`), quyết định khó đảo ngược là ADR (skill `adr`).

## 5. Viết SPEC theo mẫu `templates/sprint/SPEC.md`

| Mục | Viết gì | Kiểm |
|---|---|---|
| Kết luận | một câu: làm gì, cho ai, xong khi nào | người không chuyên đọc câu này là đủ |
| Bối cảnh | vì sao; trỏ `RQ-`, `FS-`; số liệu có nguồn | 3–6 dòng |
| `US` | "Là <ai>, tôi <muốn gì>, để <được gì>" + ưu tiên bằng chữ | mỗi `US` có ít nhất một `FR` |
| `FR` | mỗi kịch bản `FRx.y` dạng **KHI <sự kiện> THÌ <hệ thống> <phản ứng>**; kịch bản là thứ đem đi kiểm | gồm cả đường lỗi, không chỉ đường vui |
| `SC` | đo được: lệnh/thao tác + ngưỡng | mỗi `SC` sẽ có ít nhất một `VR` ở REPORT |
| Ngoài phạm vi | cái không làm đợt này | không bao giờ rỗng ở cỡ vừa trở lên |
| `CQ` + ASSUMPTION | mục 3 | mỗi `CQ` có đề xuất |
| Đổi hợp đồng / giao diện (bắt buộc khi cỡ **lớn** hoặc `risk_tags` có `public_api`; cỡ khác xoá mục) | API, sự kiện, schema sẽ đổi; delta **thêm / sửa / bỏ**; **mọi bên dùng** chúng (tra bằng tìm kiếm mã, không đoán) | không có bên dùng nào bị bỏ sót |

Mã theo skill `id-convention`: tiền tố hai chữ, mã kèm tên ngắn lần đầu trong đoạn, không `P1/P2`.

## 6. Tự review SPEC — 4 điểm, sửa tại chỗ

1. **Chỗ trống:** "TBD", mục rỗng, yêu cầu mơ hồ → viết rõ hoặc thành `CQ`.
2. **Nhất quán:** các mục có mâu thuẫn nhau không? `SC` có đo đúng `FR` không?
3. **Phạm vi:** vừa một PLAN, hay phải tách sprint?
4. **Nước đôi:** một `FR` có hai cách hiểu → chọn một, viết tường minh.

Sửa xong đi tiếp, không review lại lần hai. Cỡ nhỏ trở lên: ghi `status: in_review`, Business
Reviewer (agent khác) đọc một lượt trước khi Architect viết PLAN — tiết kiệm một vòng ở Cổng 1.

## 7. Cổng và điều cấm

- **Không viết code sản phẩm trước Cổng 1.** Thử kỹ thuật để trả lời `CQ` thì được; kết quả chỉ vào
  SPEC/PLAN, không vào nhánh sản phẩm.
- **Chỉ duyệt đúng giai đoạn đang trình:** duyệt ý tưởng ≠ duyệt SPEC; duyệt SPEC ≠ duyệt PLAN; duyệt
  PLAN ≠ nghiệm thu. Một lời "ok" không được suy thành phép làm bước sau; nối lại ở giai đoạn chưa
  xong sớm nhất.
- SPEC xong → skill `writing-plan` (Architect). Spike xong → báo cáo khuyến nghị; muốn giữ code là
  yêu cầu mới, phân loại lại.
- Trình Cổng 1 theo lời trình chuẩn của `method/process.md` mục 3 — sau khi có cả SPEC và PLAN, trừ
  khi người dùng yêu cầu duyệt SPEC riêng trước.

## 8. Cờ đỏ

| Ý nghĩ | Thực tế |
|---|---|
| "Đơn giản quá, khỏi cần SPEC" | cỡ rất nhỏ vẫn có `SPRINT.md` đủ bốn phần; cổng là lời duyệt, không phải độ dài tài liệu |
| "Gọi là bounded cho nhanh" | với tay lấy nhãn để bớt việc chính là phân vân — chọn đường nặng |
| "Hiểu kiểu app này rồi, bounded thôi" | bounded đo trên repo: không có luồng sẵn để sửa thì là architectural |
| "Spike chạy được, giữ code luôn" | đầu ra của spike là câu trả lời; giữ code là yêu cầu mới |
| "Trình SPEC rồi bắt đầu làm trong lúc họ đọc" | cổng là lời duyệt; trình xong thì dừng |
| "Họ duyệt spike nên việc tiếp theo cũng duyệt rồi" | mỗi việc một phân loại, một lời duyệt |
