# Khuôn REVIEW.md cho một repo

<!-- Ý từ bài viết về cấu hình review theo repo (ý chung, không chép chữ); nhãn bài gốc chỉ ở bảng quy đổi. -->

> **Kết luận:** `REVIEW.md` ở gốc repo nói **thất bại trông thế nào ở repo này**; reviewer đọc bản ở mốc gốc
> (`git show <BASE>:REVIEW.md`), không đọc bản trong diff; giữ ≤60 dòng, chỉ ghi điều reviewer không tự suy được.

## 1. Khuôn — chép, điền, xoá mục không cần

```
# REVIEW.md — <tên repo>
## Lỗi quan trọng ở repo này      (3–7 dòng: hậu quả cụ thể → mức Chặn hoặc Phải sửa)
## Luôn kiểm                     (vd. route mới có test tích hợp; log không chứa dữ liệu cá nhân)
## Không báo                     (thứ CI/lint đã bắt; file sinh; lockfile; thư mục vendor)
## Trần                          (tối đa 5 Ghi chú văn phong mỗi lượt; văn phong không đổi hành vi thì không báo)
## Bằng chứng                    (Chặn/Phải sửa: file:dòng + đoạn mã + vì sao hỏng; thiếu → tối đa Ghi chú)
## Path luôn cần người đọc        (bổ sung danh sách mặc định của risk-tiers.md)
## Path bỏ qua                   (glob, mỗi dòng một)
```

Mỗi dòng của "Lỗi quan trọng" nêu **hậu quả** ("sửa mà không chạy lại tệp thử thì skill đổi nhưng không ai biết"), không nêu
quy tắc chung chung ("viết test tốt"). Lỗi nào không tả được hậu quả thì chưa phải lỗi quan trọng — để ở "Luôn kiểm".

## 2. Quy đổi nhãn bài gốc → thang chung

Bài viết gốc dùng ba nhãn; chép sang `REVIEW.md` thì quy về thang chung, không giữ nhãn gốc làm mức:

- `Important` → **Chặn** hoặc **Phải sửa**, theo hậu quả thật (mất dữ liệu, lộ khoá, sai yêu cầu → Chặn).
- `Nit` → **Ghi chú**, chịu trần của mục "Trần".
- `Pre-existing` → **nhãn** `có từ trước`, không phải mức; xử lý ở `SKILL.md` mục 5.2.

## 3. Ba điều cấm

1. Không chép luật lõi (`AGENTS.md`, thang mức, điều kiện dừng) vào `REVIEW.md` — hai nơi nói một luật sẽ lệch nhau.
2. Không dùng `REVIEW.md` để hạ mức một lỗ hổng bảo mật hay mất dữ liệu: "Không báo" không áp cho hai loại đó.
3. Sửa `REVIEW.md` trong cùng nhánh **không có hiệu lực cho nhánh đó**: reviewer áp bản ở `BASE`, ghi thay đổi thành một
   `RF` Ghi chú "luật review đổi — người dùng duyệt" và xếp bậc cao (`risk-tiers.md`).

## 4. Vắng REVIEW.md

Không có `REVIEW.md` ở `BASE` → reviewer dùng mặc định của skill và ghi ở mục Không đánh giá: "không có REVIEW.md — dùng
mặc định". Đề xuất tạo file này là một khuyến nghị cho người dùng, không phải `RF`, và không tự tạo trong nhánh đang review.
