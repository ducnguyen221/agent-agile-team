---
name: dual-review
group: verifier
tier: T1
title: Dual Review — hai reviewer độc lập cùng rubric, cả hai Đạt mới Đạt
---

# Dual Review

> **Kết luận:** KHI `risk_tags` có `rules`, `secret` hoặc `auth` THÌ kiểm định kỹ thuật bắt buộc dùng **hai
> reviewer độc lập, cùng một rubric, cùng đầu vào** — **cả hai Đạt** mới Đạt; một bên báo Chặn hay Phải sửa là lỗi
> có thật, vì điểm mù của bên kia chính là cái cơ chế này sinh ra để bắt. Mỗi bên vẫn được trả **0 phát hiện**.
> Một agent tự xem lại bài của mình có cùng thiên kiến, cùng lỗ hổng hiểu biết và cùng lỗi hệ thống đã sinh ra bài đó;
> hai agent không chung ngữ cảnh phá được kiểu hỏng đó.

## 1. Mục đích
Nâng độ tin của kết luận ở ba vùng mà một lỗi lọt là đắt và khó thấy: **file luật** (`rules`: quy tắc agent, cấu hình
harness), **secret**, **xác thực / phân quyền** (`auth`). Không dùng cho bản nháp nội bộ hay phép kiểm xác định (build,
test, lint làm bằng lệnh — dùng [method/evidence.md](../../method/evidence.md)); cổng review chia theo khía cạnh nằm
ở [method/review-gate.md](../../method/review-gate.md) và **cộng** với thẻ này, không thay nhau.

## 2. Tier
**T1 tư duy** cho cả hai reviewer. Hai bên **cùng tier**, nhãn agent **khác nhau**, và khác nhãn người làm. Muốn
reviewer hãng khác thì chỉ **tư vấn**, người dùng quyết ([tiers/README.md](../../tiers/README.md)).

## 3. Đầu vào
Cho **mỗi** reviewer, cùng một bộ: SPEC + PLAN mục liên quan (đặc tả), sản phẩm cần kiểm (diff từ mốc gốc hoặc file),
**rubric** chung. Ngữ cảnh soạn riêng cho từng bên, không dán lịch sử phiên, không đưa kết quả của bên kia.

**Rubric** quyết chất lượng cả cơ chế: vague thì review vague. Mỗi tiêu chí có điều kiện đạt/không xác định:

| Tiêu chí | Đạt khi | Dấu hiệu hỏng |
|---|---|---|
| Đúng đặc tả | mọi `FR`/`SC` liên quan được đáp ứng | thiếu mục, bỏ ca biên |
| Không bịa | không có thực thể, trích dẫn, URL, tham chiếu bịa | liên kết tới trang không có thật |
| Nhất quán nội bộ | không tự mâu thuẫn | mục A nói X, mục B nói không-X |
| Đúng kỹ thuật | mã chạy được, thuật toán đúng | lỗi cú pháp, lỗi logic |
| Theo ràng buộc dự án | qua mọi điều cấm của dự án | dùng từ cấm, nới luật lõi |
| Bảo mật (với `secret`, `auth`) | không secret trong mã, kiểm đầu vào, không chèn, không lộ | khoá trong diff, quyền rộng |
| Với `rules` | không nới quyền cho chính agent, không bỏ cổng người | luật mới cho phép bỏ qua Cổng 1/2 |

## 4. Đầu ra
Mỗi reviewer trả **riêng**: kết luận Đạt / Đạt có điều kiện / Không đạt · bảng từng tiêu chí (Đạt / không + chi tiết
đúng chỗ) · `RF` có mức và bằng chứng · mục "Không đánh giá". Kết luận **chung** của cặp:

| Bên A | Bên B | Chung |
|---|---|---|
| Đạt | Đạt | **Đạt** |
| bất kỳ khác | bất kỳ | **chưa Đạt** — gộp `RF` của hai bên, khử trùng, quay lại bước 3 |

Không có "điểm một phần": hai bên Đạt hoặc chưa. Khác biệt giữa hai bên (A thấy Chặn, B không) **ghi nguyên** vào
REPORT, không dàn xếp ngầm — chỗ hai bên bất đồng chính là cái người dùng cần thấy ở Cổng 2.

**Ghi vào hồ sơ:** nhãn reviewer thứ nhất ở khoá `tech-reviewer` của `roles`, nhãn reviewer thứ hai trong phần
`"note"` của khoá đó, dạng tiền tố `reviewer 2: agent-x` (cùng chuỗi có thể thêm `model: …`, xem
[templates/README.md](../../templates/README.md) mục 3.1), và ở cột "Vai · tier · model" của PROGRESS; kết luận từng
bên và kết luận chung ở REPORT, mục "Phát hiện của reviewer". **Giới hạn:** `check` không so nhãn trong `note` với
vai thực thi nên không bắt được reviewer thứ hai trùng người làm — điều phối tự kiểm điều đó trước khi giao.

## 5. Được làm
- Chạy **song song**, mỗi bên không thấy bên kia; mỗi bên được hỏi cùng câu và cùng rubric.
- Vòng sửa: người làm sửa **đúng** phần bị gắn cờ, không tái cấu trúc, không thêm thứ không được yêu cầu; rồi chạy lại
  **cả hai** reviewer bằng agent **mới** (không giữ trí nhớ của vòng trước, để tránh neo vào kết luận cũ).
- Trả 0 phát hiện khi không có gì — kèm phần không đánh giá.
- Thêm reviewer thứ ba hoặc người xem mẫu khi đầu ra thật sự nghiêm trọng: hai bên cùng bỏ sót một thứ là điểm yếu còn
  lại (giảm bằng độc lập, không xoá hẳn).

## 6. Không được làm
- Để hai reviewer thấy nhau, dùng chung ngữ cảnh, hay cho bên sau xem kết luận bên trước.
- "Rubber stamp": cả hai Đạt mọi thứ không bằng chứng — nhắc rõ trong brief: việc của reviewer là **tìm vấn đề**,
  không phải phê duyệt.
- Chấm theo sở thích văn phong: tiêu chí chỉ gồm điều kiện đạt/không xác định, không có "đẹp/xấu".
- Đếm một bên Đạt là "một phần đạt"; dàn xếp bất đồng bằng cách lấy trung bình hay bỏ phiếu.
- Coi **Đạt** của cặp là nghiệm thu: đó là kết luận kiểm định của bước 4; Cổng 2 vẫn do người dùng, và mọi tác động
  ra ngoài (push, phát hành, gộp nhánh chính) vẫn chờ người dùng gật.

**Điểm hỏng thường gặp và thuốc:**

| Cách hỏng | Dấu hiệu | Thuốc |
|---|---|---|
| Vòng vô tận | reviewer cứ tìm ra lỗi mới sau mỗi lần sửa | mốc 3 vòng (không trần cứng), rồi hỏi người dùng |
| Reviewer dễ dãi | cả hai Đạt hết | brief ghi "việc của bạn là tìm vấn đề"; rubric có điều kiện cụ thể |
| Trôi sang phong cách | cờ toàn là sở thích | rubric chỉ điều kiện xác định |
| Sửa lỗi này sinh lỗi kia | lỗi mới xuất hiện sau vòng sửa | reviewer mới mỗi vòng bắt hồi quy |
| Chi phí phình | quá nhiều vòng cho đầu ra lớn | chia đầu ra theo phần; ghi trần ngân sách trong PLAN |

## 7. Khi nào dừng
Hết **3 vòng** mà vẫn còn Chặn / Phải sửa → báo người dùng theo lời báo chuẩn ở [process.md](../../method/process.md)
mục 6 (không trần cứng; chọn làm tiếp hay dừng & bàn giao) · hai bên bất đồng kéo dài nhiều vòng về cùng một điểm (rubric
mơ hồ — làm rõ chữ rubric, ghi `Phán quyết:`; không nới điều kiện đạt, vì nới điều kiện là đổi tiêu chí → `BR`) · cạn
hạn mức tier (không tự hạ tier) · chi phí vượt xa lợi ích (mỗi vòng cỡ 2–3 lần chi phí kiểm một bên — ghi trong PLAN
khi chọn bật).

## 8. Skill dùng
`verify-before-done` (cổng xong và bằng chứng) · `code-review` · `security-review` · `plan-review` ·
`response-style` · `id-convention` · `token-economy`. Thiết kế cổng review chia theo khía cạnh:
[method/review-gate.md](../../method/review-gate.md).
