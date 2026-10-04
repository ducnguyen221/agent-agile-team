# Vòng kiểm sáu pha cho thay đổi mã

> **Kết luận:** trước khi báo xong một `TK` có đổi mã, chạy **sáu pha theo thứ tự** — build · kiểu · lint · test ·
> bảo mật · diff — bằng lệnh của chính dự án, ghi mỗi pha một dòng (lệnh, mã thoát, số lỗi) thành `VR`. Pha đỏ thì
> **dừng và sửa trước khi sang pha sau**; sửa bằng mã, không bằng cách tắt kiểm, hạ ngưỡng hay sửa cấu hình linter /
> test. Vòng này nối vào cổng năm bước ở mục 2 của `SKILL.md`: nó là danh sách pha cụ thể của bước "Chạy".

## 1. Khi nào chạy

- Sau khi hoàn thành một `TK` có đổi mã nguồn, trước khi đánh dấu xong hay giao cho agent kiểm định.
- Sau mỗi thay đổi lớn giữa chừng: xong một hàm quan trọng, xong một thành phần, trước khi sang `TK` kế — chạy theo
  **mốc việc**, không theo đồng hồ.
- Sau tái cấu trúc (nơi hành vi phải giữ nguyên, pha test là bằng chứng chính).

Việc chỉ đổi tài liệu hay chữ: chạy pha kiểu dự án có (lint tài liệu, kiểm liên kết) và pha diff; pha **build**,
**kiểu**, **test** ghi **Không áp dụng** kèm lý do — không bỏ trống.

## 2. Sáu pha

| Pha | Việc | Đỏ thì |
|---|---|---|
| 1. Build | lệnh build của dự án | **dừng**, sửa trước mọi pha sau — các pha sau chạy trên mã không build được là vô nghĩa |
| 2. Kiểu | kiểm kiểu của dự án (trình kiểm kiểu tĩnh nếu có) | báo **mọi** lỗi kiểu; sửa lỗi nặng trước khi sang pha 3 |
| 3. Lint | linter của dự án | báo lỗi; sửa lỗi, không thêm dòng tắt kiểm cho cả file để qua |
| 4. Test | **cả bộ** test (không một file), kèm coverage | ghi số tổng / đạt / hỏng và % coverage **code mới hoặc sửa** so với ngưỡng của dự án (mặc định 80 %) |
| 5. Bảo mật | quét secret trong diff; quét lỗ hổng phụ thuộc nếu dự án có công cụ; tìm đoạn gỡ lỗi để quên | secret trong diff là **Chặn** — báo `file:dòng` và loại secret, **không in giá trị**; đoạn gỡ lỗi để quên (in ra console, `print` tạm) là Nên sửa |
| 6. Diff | xem tập file đổi (`git diff --stat`, rồi `git diff <mốc gốc>...HEAD --name-only`) và đọc từng file đổi | mục nào đổi ngoài phạm vi `TK` → gỡ hoặc giải thích; thiếu xử lý lỗi, ca biên chưa phủ → ghi `RF` |

**Cách chạy lệnh.** Lấy **mã thoát thật** của lệnh kiểm: ống dẫn tới `tail` hay `head` che mã thoát của lệnh đứng
trước — dùng chế độ ống dẫn báo lỗi của shell (`set -o pipefail`) hoặc ghi output ra file rồi đọc mã thoát, và đọc hết
output chứ không chỉ vài dòng cuối. Output dài lưu ra `.tmp/` của sprint, trong tài liệu chỉ giữ dòng then chốt.

**Dừng khi build đỏ, nhưng ghi đủ.** Pha đỏ không được che bằng cách sửa lệnh kiểm: không hạ ngưỡng coverage, không
tắt luật lint, không xoá hay làm yếu test, không `--no-verify`. Muốn đổi cấu hình kiểm phải là việc riêng, có `Phán
quyết:` hoặc hỏi người dùng nếu chạm điều kiện dừng.

## 3. Mẫu báo cáo vòng kiểm

Mỗi pha một dòng; kết quả dùng bốn mức của `VR`, không dùng "PASS / FAIL":

```
Vòng kiểm TK<n> — mốc <commit>, cây <sạch|bẩn: tóm tắt diff chưa commit>
1 Build    <lệnh> → mã thoát <k>                                  <Đạt | Không đạt | Chưa chạy | Không áp dụng>
2 Kiểu     <lệnh> → <số lỗi>                                      <…>
3 Lint     <lệnh> → <số lỗi / cảnh báo>                           <…>
4 Test     <lệnh> → <đạt>/<tổng>, coverage code mới <x> %        <…>
5 Bảo mật  <lệnh hoặc cách quét> → <số phát hiện, loại>           <…>
6 Diff     <số file đổi>; ngoài phạm vi: <không | liệt kê>        <…>
Kết luận: <xong | chưa xong: pha <k> đỏ> — việc còn lại: <…>
```

Kết luận chỉ là **xong** khi cả sáu dòng là Đạt hoặc Không áp dụng **có lý do**. Chưa chạy (thiếu môi trường, thiếu
công cụ) không được coi là Đạt; giới hạn công cụ là Chưa chạy, không phải Không áp dụng (xem `method/evidence.md` mục 2).

## 4. Chỗ vòng này dừng

Vòng sáu pha là kiểm **cơ học, của người làm**: nó cho bằng chứng để báo xong `TK`, không thay kiểm định của agent
khác (`VR` độc lập) hay cổng review chia theo khía cạnh (`method/review-gate.md`), và không thay Cổng 2. Kết quả "sẵn
sàng" của vòng là điều kiện **để báo `TK` xong**, không phải để mở PR hay phát hành — push, PR và gộp nhánh chính chỉ
sau Cổng 2 khi người dùng gật.
