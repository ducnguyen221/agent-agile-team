---
title: Testing — common rules for every language
type: method
status: active
updated: 2026-10-04
---

<!-- Nguồn: affaan-m/ECC rules/common/testing.md @ ef648e01 (MIT). Viết lại, giữ ý; bỏ lời gọi agent riêng của
     nguồn; ngưỡng coverage đổi sang chữ của luật lõi. -->

# Kiểm thử chung

> **Kết luận:** test viết trước code, hỏng đúng lý do rồi mới viết mã; coverage **80 % code mới/sửa**; mỗi
> lớp test (đơn vị, tích hợp, E2E) có chỗ của nó. Test hỏng thì sửa mã, không sửa test để qua, không nới
> cấu hình kiểm.

## Ngưỡng

- Coverage tối thiểu **80 % code mới/sửa** — con số và cách chỉnh nằm ở `method/conventions.md` mục 1; chuẩn
  này không đặt ngưỡng riêng. Số coverage ghi vào kết quả kiểm kèm lệnh đo.
- Coverage là điều kiện cần, chưa đủ: test phải bắt được lỗi nó nhắm tới.

## Các lớp test

- **Đơn vị:** hàm, tiện ích, thành phần đơn lẻ.
- **Tích hợp:** endpoint API, thao tác với cơ sở dữ liệu, ranh giới giữa các module.
- **E2E:** các luồng người dùng trọng yếu; công cụ chọn theo ngôn ngữ (xem chuẩn riêng, skill `web-qa`).
- Lớp nào áp dụng cho việc này do PLAN nêu; lớp bỏ phải có lý do ghi lại, không bỏ im lặng.

## Test trước code

- Vòng đỏ → xanh → dọn: viết test, chạy thấy **hỏng đúng lý do**, viết mã tối thiểu cho nó đạt, chạy thấy
  đạt, dọn mã, đo coverage (skill `tdd`, kể cả luật khi lỡ viết code trước).

## Test hỏng

- Dùng skill `debugging` trước khi sửa; kiểm cô lập giữa các test và mock có đúng không.
- **Sửa mã, không sửa test** — trừ khi test sai thật, và nói rõ vì sao nó sai.
- Không đánh dấu bỏ qua hay xfail, không hạ ngưỡng, không đổi cấu hình kiểm chỉ để xanh (`AGENTS.md`).

## Cấu trúc và tên

- Mỗi test theo ba bước **Sắp đặt – Thực hiện – Khẳng định** (Arrange – Act – Assert), tách bạch bằng dòng trống
  hoặc chú thích ngắn.
- Tên test mô tả hành vi, đọc lên là hiểu: "trả mảng rỗng khi không có kết quả khớp", "ném lỗi khi thiếu khoá
  API", "quay về tìm chuỗi con khi bộ nhớ đệm không dùng được".
