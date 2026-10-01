# Giao việc song song

<!-- Nguồn: obra/superpowers skills/dispatching-parallel-agents/SKILL.md @ 8ca22db (MIT). Viết lại. -->

> **Kết luận:** chạy song song **chỉ** khi các việc độc lập — không chung file, không chung state,
> không phụ thuộc thứ tự; mỗi agent một brief riêng, tự chứa; **gửi trong cùng một lượt** mới là song
> song; gộp kết quả theo bằng chứng (chạy cả bộ test), không theo lời kể; ghi **vai · tier · model**
> từng agent vào PROGRESS.

## 1. Khi nào

| Song song | Tuần tự / một agent |
|---|---|
| ≥2 `TK` độc lập trong PLAN (tiền kiểm giao diện không có cặp chung) | `TK` dùng giao diện `TK` kia sinh |
| ≥3 file test hỏng với nguyên nhân khác nhau, hiểu được từng cái mà không cần cái kia | lỗi liên quan nhau — sửa một có thể hết cả; chưa biết hỏng ở đâu (khám phá) |
| nhiều hệ con hỏng độc lập | cần nhìn toàn hệ để hiểu |
| không chung file, không chung tài nguyên (DB test, cổng, cache) | agent sẽ giẫm nhau |

Nghi ngờ → tuần tự. Hai Implementer trên cùng file **không bao giờ** song song.

## 2. Cách làm

1. **Chia miền:** gom theo thứ hỏng / thứ đổi — mỗi miền một agent (file test A ↔ luồng duyệt công cụ;
   file B ↔ hoàn tất batch; file C ↔ huỷ).
2. **Mỗi agent một brief** theo `brief.md`: phạm vi cụ thể (một file, một hệ con), mục tiêu rõ ("làm 3
   test này đạt"), ràng buộc ("không đổi code ngoài `src/x/`", "không tăng timeout — tìm nguyên nhân"),
   đầu ra ("tóm tắt nguyên nhân gốc + đã đổi gì", khung 4 phần của `token-economy`). Dán **thông điệp
   lỗi và tên test** vào brief — không dán cả log.
3. **Gửi tất cả trong một lượt** (nhiều lệnh giao agent trong cùng một phản hồi). Mỗi lượt một lệnh =
   tuần tự.
4. Ghi PROGRESS **mỗi agent một dòng**: `TKn` · vai · tier · model · nhãn agent · BASE. Nhãn vào `roles`.
5. **Gộp:** đọc từng tóm tắt → kiểm xung đột (hai agent sửa cùng chỗ?) → chạy **cả bộ** test → soát
   chọn mẫu (agent có thể sai hệ thống) → review theo việc như bình thường, mỗi `TK` một gói diff với
   BASE riêng.

## 3. Lỗi hay gặp

| Lỗi | Sửa |
|---|---|
| "Sửa hết test hỏng" | một file / một hệ con mỗi agent |
| "Sửa race condition" không nói ở đâu | dán lỗi + tên test + file |
| Không ràng buộc → agent refactor lan | "chỉ sửa test" / "không đổi code sản phẩm" / danh sách file |
| "Sửa đi" → không biết đã đổi gì | đòi tóm tắt nguyên nhân + diff |
| Gộp theo lời kể "đã xong" | chạy cả bộ, đọc output thật |
