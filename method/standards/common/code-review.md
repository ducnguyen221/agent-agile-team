---
title: Code review — common standard
type: method
status: active
updated: 2026-10-04
---

<!-- Nguồn: affaan-m/ECC rules/common/code-review.md @ ef648e01 (MIT). Viết lại, giữ ý; bảng nhãn mức và bảng
     agent của nguồn đổi sang thang chung của repo (`method/severity.md`) và danh mục reviewer của repo. -->

# Review code: chuẩn chung

> **Kết luận:** review trước khi gộp và khi chạm vùng nhạy cảm; trước khi xin review, kiểm tự động đã xanh;
> mọi phát hiện gắn đúng một mức theo `method/severity.md`; kết luận là Đạt / Đạt có điều kiện / Không đạt.
> Cách chạy review (ai, thứ tự, brief) ở skill `code-review`; chuẩn này nói **xét cái gì**.

## Khi nào phải review

- Sau khi viết hay sửa code, trước khi commit vào nhánh dùng chung.
- Khi đổi code bảo mật (xác thực, phân quyền, thanh toán, dữ liệu người dùng) — cộng lượt bảo mật theo skill
  `security-review`.
- Khi đổi kiến trúc, trước khi gộp PR.
- Reviewer là **agent khác người làm** (`AGENTS.md`); người làm không tự chấm.

## Trước khi xin review

- Kiểm tự động (CI, test, lint) đã xanh; xung đột đã giải; nhánh đã cập nhật so với nhánh đích.
- Review theo phạm vi commit (`git diff <BASE>..HEAD`), không theo working tree.

## Xét cái gì

- **Đọc được:** tên rõ, hàm tập trung (không quá 50 dòng), file gắn kết (dưới trần mềm 800 dòng hoặc có lý do).
- **Lỗi:** xử lý tường minh; không nuốt; không còn lệnh in gỡ lỗi.
- **Bảo mật:** không secret viết cứng, truy vấn tham số hoá, không chèn dữ liệu thô vào HTML, kiểm đường dẫn
  file, không lỗ hổng bỏ qua xác thực, có chống CSRF khi cần.
- **Test:** có test cho hành vi mới; coverage đạt **80 % code mới/sửa**.
- **Hiệu năng:** truy vấn N+1 (dùng JOIN hay gom lô), thiếu phân trang, truy vấn không giới hạn, thiếu cache
  cho phép tính đắt.
- **Dữ liệu:** thay đổi tại chỗ không cần thiết (nên trả bản mới).

## Mức phát hiện

Đúng một mức cho mỗi phát hiện (`method/severity.md`). Quy đổi gợi ý cho các việc hay gặp:

| Hiện tượng | Mức |
|---|---|
| Lỗ hổng bảo mật, rủi ro mất dữ liệu | **Chặn** |
| Lỗi hành vi hay vấn đề chất lượng đáng kể | **Phải sửa** |
| Khó bảo trì, kể cả file vượt trần mềm 800 dòng không lý do | **Nên sửa** |
| Phong cách, gợi ý nhỏ | **Ghi chú** |

## Kết luận

- **Đạt:** không Chặn, không Phải sửa còn mở.
- **Đạt có điều kiện:** không Chặn; Phải sửa còn mở chỉ khi người dùng chấp nhận **ghi rõ**; chỉ Nên sửa được hoãn thành `CO` có chủ và mốc (`method/severity.md` mục 2).
- **Không đạt:** còn Chặn.

## Liên quan

`testing.md` (ngưỡng), `security.md` (danh mục), `git-workflow.md` (commit, PR), `agents.md` (giao việc cho
reviewer).
