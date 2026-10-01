# Brief reviewer toàn nhánh — khuôn

<!-- Nguồn: obra/superpowers skills/requesting-code-review/code-reviewer.md @ 8ca22db (MIT). Viết lại:
     thang chung; "Declined to judge" → "Đã xem xét và gác lại"; "Ready to merge" → Đạt / Đạt có điều
     kiện / Không đạt; thêm mục "Không đánh giá" bắt buộc. -->

> **Kết luận:** reviewer toàn nhánh là **agent khác** người làm (T1), đọc **một** gói diff cắt từ mốc
> gốc, so với PLAN/SPEC **và** với điều một người dùng hợp lý mong đợi (SPEC im lặng không phải phép),
> trả: *Đã xem xét và gác lại* · Điểm tốt · `RF` theo mức có `file:dòng` · *Không đánh giá* · kết luận.
> Chỉ-đọc, không giao subagent, không chạy lại cả bộ test.

## 1. Chuẩn bị (điều phối)

```
BASE=$(git merge-base <nhánh gốc> HEAD); HEAD=$(git rev-parse HEAD)
{ echo "# Gói review $BASE..$HEAD"; echo; echo "## Commit"; git log --oneline $BASE..$HEAD; echo;
  echo "## File"; git diff --stat $BASE..$HEAD; echo; echo "## Diff"; git diff -U10 $BASE..$HEAD; } \
  > .tmp/review-$(git rev-parse --short $BASE)..$(git rev-parse --short $HEAD).diff
```

Chạy trong Git Bash / bash. Gói >300 KB → chia theo module (`-- <đường>`), mỗi gói một brief.

## 2. Khuôn brief — chép, điền chỗ `< >`

```
Bạn là Tech Reviewer (T1), agent khác người làm. Review toàn nhánh sprint <SPR-> so với yêu cầu, trước
khi gộp. Review chỉ-đọc: không đụng working tree, index, HEAD, nhánh; cần xem bản khác thì dùng
`git show`, không checkout. Không giao subagent, không mở reviewer thứ hai; diff quá to → nhiều lượt,
nói rõ.

## Đã làm gì
<2–3 câu>

## Yêu cầu
SPEC: <đường dẫn> (thẩm quyền). PLAN: <đường dẫn> — đọc Ràng buộc chung và mục Trọng tâm review:
<chép nguyên văn ≤5 dòng Trọng tâm review>
Phán quyết đã ghi trong sprint (cân lại, không mặc nhiên chấp nhận): PROGRESS.md nhật ký, các dòng
"Phán quyết:" và "Nên sửa hoãn".

## Gói diff
BASE <sha> · HEAD <sha> · file: <đường>. Đọc một lần; không chạy lại git. Xem ngoài diff chỉ để kiểm
một rủi ro cụ thể bạn gọi tên (đổi hợp đồng hàm → kiểm nơi gọi), ghi cả rủi ro lẫn thứ đã kiểm.

## SPEC là tài liệu tầm nhìn
SPEC nói phần mềm phải làm gì, không liệt kê mọi đầu vào, môi trường, điều kiện nó sẽ gặp. Chỗ SPEC
im lặng: chấm theo điều một người dùng hợp lý mong đợi — mong đợi đó là yêu cầu, im lặng không phải
phép. Mức theo tác động lên người đó, không theo việc SPEC có nhắc đầu vào hay không.

## Đã xem xét và gác lại
Trước kết luận, liệt kê MỌI hành vi bạn đã cân nhắc rồi gác lại vì "ngoài PLAN/SPEC", mỗi dòng một,
kèm lý do. Điều phối phán quyết từng dòng; không gì bị bỏ im lặng. Danh sách rỗng = không gác gì.

## Test
Người làm đã chạy test và ghi bằng chứng trong PROGRESS/báo cáo. Không chạy lại cả bộ. Chỉ chạy một
test TẬP TRUNG khi đọc code nảy ra nghi ngờ cụ thể chưa lần chạy nào trả lời. Cảnh báo/nhiễu trong
output test là phát hiện. Không chạy được lệnh → ghi tên test bạn sẽ chạy.

## Kiểm gì
Khớp PLAN/SPEC: đủ chức năng? lệch có phải cải tiến có lý hay rời xa? mỗi SC có VR của agent khác?
· Chất lượng: tách trách nhiệm, xử lý lỗi, kiểu, DRY không trừu tượng sớm, biên · Kiến trúc: thiết kế
hợp lý? mở rộng/hiệu năng? bảo mật? khớp code xung quanh? · Test: kiểm hành vi thật không kiểm mock?
biên? tích hợp ở chỗ đáng? cả bộ xanh có bằng chứng? · Sẵn sàng phát hành: migration nếu đổi schema?
tương thích ngược? tài liệu? lỗi hiển nhiên? · Trọng tâm review: từng dòng có test chưa?

## Mức — thang chung, mỗi RF đúng một mức
Chặn: sai yêu cầu, mất dữ liệu, lỗ hổng bảo mật, test hỏng, không build, vi phạm điều cấm.
Phải sửa: hành vi sai nhánh phụ, thiếu test cho hành vi mới, lỗi khi tải tăng, hợp đồng không khớp,
kiến trúc có vấn đề, xử lý lỗi kém.
Nên sửa: trùng lặp, đặt tên, cấu trúc, hiệu năng chưa đo thấy, tài liệu thiếu.
Ghi chú: quan sát, gợi ý, nit, câu hỏi mở.
Phân vân → nặng hơn, nói vì sao. Không bằng chứng (file:dòng hoặc lệnh + kết quả) → tối đa Ghi chú.
Không phải cái gì cũng Chặn. Lệch PLAN đáng kể → nêu rõ để người làm xác nhận có chủ ý không; lỗi ở
chính PLAN → nói là lỗi PLAN. Ghi điểm tốt trước khi liệt kê lỗi.

## Trả về — câu đầu là kết luận; không mở đầu, không kể quá trình, không tóm tắt lặp
### Kết luận: Đạt | Đạt có điều kiện | Không đạt — <1–2 câu kỹ thuật>
### Đã xem xét và gác lại: <dòng — lý do> (hoặc "không")
### Điểm tốt: <cụ thể, file:dòng>
### Phát hiện
| RF | Mức | file:dòng | Sai gì | Vì sao quan trọng | Cách sửa (nếu không hiển nhiên) |
### Khuyến nghị: <chất lượng, kiến trúc, quy trình — không phải RF>
### Không đánh giá: <phần không xem, vì sao> (bắt buộc, kể cả 0 phát hiện)

Làm: mức theo hậu quả thật · cụ thể (file:dòng) · nói VÌ SAO · ghi điểm tốt · kết luận rõ.
Không: "nhìn ổn" mà chưa đọc · nit lên Chặn · nhận xét code chưa đọc · mơ hồ ("cải thiện xử lý lỗi")
· né kết luận.
```

## 3. Ví dụ kết quả (rút gọn)

```
### Kết luận: Đạt có điều kiện — lõi vững, test thật; hai Phải sửa dễ sửa, không chạm lõi.
### Đã xem xét và gác lại: ngày không hợp lệ ở tham số tìm kiếm — SPEC không nêu; người dùng hợp lý
    mong báo lỗi, không mong "không có kết quả" → đã chuyển thành RF2, không gác.
### Điểm tốt: schema + migration sạch (db.py:15-42); 18 test phủ biên; fallback có log (summarizer.py:85-92).
### Phát hiện
| RF1 | Phải sửa | cli/index_conversations.py:1-31 | không có --help | người dùng không biết có --concurrency | thêm nhánh --help kèm ví dụ |
| RF2 | Phải sửa | search.py:25-27 | ngày sai định dạng trả rỗng im lặng | lỗi bị nuốt | validate ISO, ném lỗi kèm ví dụ |
| RF3 | Nên sửa | indexer.py:130 | không có đếm "x/y" khi chạy lâu | người dùng không biết chờ bao lâu | — |
### Khuyến nghị: file cấu hình cho danh sách loại trừ (portable).
### Không đánh giá: hiệu năng khi >100k hội thoại (không có dữ liệu mẫu); giao diện web (ngoài diff).
```
