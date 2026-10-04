---
name: verify-before-done
description: Use when about to say work is done, fixed, passing or ready, before marking a TK done, committing, opening a PR, moving to the next task, handing back to the coordinator, or accepting another agent success report, and whenever recording a VR.
source: [obra/superpowers skills/verification-before-completion/SKILL.md]
source_sha: [8ca22dba9a94f28898bbce59f2537ff4d87c747d]
license: [MIT]
rewrite_before_public: false
metadata:
  group: verification
  roles: [implementer, qa]
---

# Kiểm trước khi báo xong

> **Kết luận:** **không tuyên bố xong khi chưa có bằng chứng mới chạy** — chạy đúng lệnh chứng minh, đọc
> hết output, rồi mới nói, và nói kèm bằng chứng. Test hồi quy chỉ được tính khi đã đi vòng **gỡ bản sửa →
> test hỏng → đặt lại → test đạt**. Kết quả ghi thành `VR` với Đạt / Không đạt / Chưa chạy / Không áp
> dụng; hai mức sau không bao giờ là Đạt. Làm sai chữ của luật này là làm sai tinh thần của nó.

## 1. Luật sắt

**Chưa chạy lệnh kiểm trong lượt này thì không được nói nó đạt.** Luật áp cho mọi cách diễn đạt: câu
nguyên văn, từ đồng nghĩa, hàm ý ("ổn rồi", "xong phần này", "chuyển sang việc sau") và cả việc tỏ ra hài
lòng ("Tuyệt!", "Xong!") trước khi kiểm.

## 2. Cổng năm bước — chạy trước MỌI tuyên bố về trạng thái

1. **Xác định:** lệnh nào chứng minh được câu sắp nói?
2. **Chạy:** chạy lệnh đó **đầy đủ, mới** — cả bộ test, không một file; không dùng kết quả lần trước.
3. **Đọc:** đọc hết output, xem mã thoát, đếm số hỏng/lỗi/cảnh báo.
4. **Đối chiếu:** output có xác nhận câu sắp nói không?
   - Không → nói **trạng thái thật** kèm bằng chứng ("3/34 test hỏng: …").
   - Có → nói câu đó **kèm** bằng chứng.
5. **Chỉ khi đó** mới tuyên bố.

Bỏ một bước là đoán, không phải kiểm. Không chạy được (thiếu môi trường, thiếu quyền) → trạng thái là
**Chưa chạy** kèm lý do, không phải "chắc là đạt".

Dạng câu báo: `<lệnh>` → `<kết quả then chốt>` (mã thoát, số đạt/hỏng) · commit `<mốc>` · cây sạch/bẩn →
`<tuyên bố>`.

## 3. Tuyên bố nào cần bằng chứng nào

| Tuyên bố | Cần | Không đủ |
|---|---|---|
| Test đạt | output lệnh test của **cả bộ**: 0 hỏng | lần chạy trước, "chắc đạt", chạy một file |
| Lint sạch | output linter: 0 lỗi | kiểm một phần, suy ra từ file khác |
| Build được | lệnh build: mã thoát 0 | lint đạt, log "trông ổn" |
| Lỗi đã sửa | tái hiện **triệu chứng gốc**: không còn | đã sửa code, "chắc hết" |
| Test hồi quy dùng được | vòng gỡ sửa → hỏng → đặt lại → đạt (mục 4) | test đạt một lần |
| Agent khác làm xong | diff trong VCS + chạy lại phép kiểm | agent báo "thành công" |
| Đạt yêu cầu | đối chiếu từng `FR`/`SC` (mục 6) | test xanh |
| Coverage đạt ngưỡng | lệnh đo coverage + số | "đã viết thêm test" |
| Sổ tập trung khớp hồ sơ (dự án khai `ledger.project`) | `check` mới chạy **sau khi ghi sổ**: không `ledger-stale`, không `ledger-missing-row` | lần `check` hôm qua, "chắc khớp", "ghi sổ lúc đóng sprint" |

## 4. Test hồi quy: vòng gỡ sửa → hỏng

Viết test → chạy (đạt) → **gỡ bản sửa** → chạy (**phải hỏng**, và hỏng đúng lý do — không phải lỗi cú
pháp hay import) → đặt lại bản sửa → chạy (đạt). Ghi **cả hai** kết quả (hỏng khi gỡ, đạt khi đặt lại)
vào `VR`. Test chưa từng hỏng không chứng minh gì. Chi tiết: `method/evidence.md` mục 4.

Không gỡ được bản sửa an toàn (thay đổi lớn, nhiều file) → gỡ trên nhánh tạm hoặc worktree riêng, không
`git stash` trần; vẫn không làm được thì `VR` ghi Chưa chạy cho phần "bắt hồi quy", kèm lý do.

## 5. Ghi `VR`

- Đủ trường theo `method/evidence.md` mục 1: trỏ `FR`/`SC`, cách kiểm (lệnh nguyên văn), môi trường,
  thời điểm, kỳ vọng ↔ thực tế, kết quả, người chạy (vai · tier · model), giới hạn.
- Kết quả chỉ một trong bốn: **Đạt · Không đạt · Chưa chạy · Không áp dụng** (kèm lý do). Chưa chạy và
  Không áp dụng không bao giờ được đếm là Đạt; giới hạn công cụ là Chưa chạy, không phải Không áp dụng.
- Implementer tự kiểm trước khi báo xong `TK` và ghi bằng chứng vào PROGRESS; `VR` dùng cho kiểm định do
  **agent khác** người làm chạy (QA hoặc reviewer). Cùng một agent → ghi "tự kiểm, chưa độc lập".
- Mốc code, spec hoặc toolchain đổi → bằng chứng cũ hết hạn cho phần bị ảnh hưởng; chạy lại.
- Dự án khai sổ tập trung: trước khi báo xong `TK` hay sẵn sàng Cổng 2, trạng thái và ngày ở dòng sổ phải khớp PROGRESS
  (`method/process.md` mục 11). Chưa khớp → ghi sổ rồi chạy lại `check`, dẫn kết quả vào lời báo; không chạy được thì
  phần sổ là Chưa chạy.
- Output dài lưu `.tmp/` của sprint, trong tài liệu chỉ giữ dòng then chốt + đường dẫn.

## 6. Đạt yêu cầu ≠ test xanh

Trước khi báo một `TK` hay cả sprint là xong: đọc lại mục SPEC/PLAN liên quan → lập danh sách từng `FR`
(kịch bản) và `SC` → kiểm từng mục, mỗi mục một bằng chứng → báo **mục thiếu** hoặc xong. "Test xanh nên
xong giai đoạn" là câu đỏ.

"Xong" (`TK` có bằng chứng) ≠ "nghiệm thu" (Cổng 2) ≠ "phát hành" (kiểm trên môi trường thật) —
`method/evidence.md` mục 6. Không suy cái sau từ cái trước.

## 7. Báo cáo của agent khác không phải bằng chứng

Subagent báo "xong", "test đạt" → xem diff thật trong VCS (`git diff <mốc>...HEAD --stat` rồi các file
then chốt) → chạy lại phép kiểm then chốt → báo **trạng thái thật**. Không chép câu "thành công" của
agent khác vào PROGRESS hay `VR`.

## 8. Cờ đỏ — thấy là dừng, quay lại mục 2

- Dùng "chắc", "có lẽ", "hình như", "should work", "về lý thuyết đúng".
- Vui mừng trước khi kiểm ("Tuyệt!", "Xong!", "Hoàn hảo!").
- Sắp commit, push, mở PR hay chuyển `TK` mà chưa chạy kiểm.
- Tin báo cáo thành công của agent khác.
- Kiểm một phần rồi suy ra cả phần.
- Nghĩ "lần này thôi", đang mệt, muốn cho xong.
- Bất kỳ câu nào **hàm ý** thành công mà chưa chạy kiểm.

## 9. Lý do bào chữa và thực tế

| Lý do | Thực tế |
|---|---|
| "Giờ chắc chạy rồi" | Chạy kiểm |
| "Tôi tự tin" | Tự tin không phải bằng chứng |
| "Lần này thôi" | Không có ngoại lệ |
| "Linter đạt rồi" | Linter không phải trình biên dịch, không phải test |
| "Agent kia báo thành công" | Kiểm độc lập |
| "Kiểm một phần là đủ" | Một phần không chứng minh cả phần |
| "Diễn đạt khác nên luật không áp" | Tinh thần hơn câu chữ |
| "Việc nhỏ, khỏi kiểm" | Việc rất nhỏ vẫn cần một lệnh + kết quả **mới chạy** trong lời báo cuối; không có agent thứ hai thì `VR` ghi "tự kiểm, chưa độc lập" và kết luận tối đa **Đạt có điều kiện** |

## 10. Khi nào áp dụng

**Luôn**, trước: mọi tuyên bố thành công hay hoàn thành dưới mọi cách diễn đạt · commit, push, mở PR ·
đánh dấu `TK` xong trong PROGRESS · chuyển sang `TK` kế · giao tiếp việc cho agent khác hay nhận việc về ·
ghi `VR` · trình Cổng 2.
