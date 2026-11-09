# Autopilot — phần của running-sprint

> Phần luật autopilot của skill này, dời **nguyên văn** từ `SKILL.md` (SPR-16 TK1); chỉ đường dẫn tương đối tới `method/` đổi theo vị trí file. Đọc khi nhận hoặc ghi lệnh autopilot.

## Cờ đỏ về autopilot (từ mục 8)

| Ý nghĩ | Thực tế |
|---|---|
| "Phiên con báo xong, ghi `xong` luôn" (autopilot) | ghi `xong` sau khi tự chạy lại lệnh kiểm và đọc `git diff`; lời tự báo không phải bằng chứng |
| "Phiên con xin thêm quyền một lần thôi" (autopilot) | ngoài lệnh thì từ chối, ghi hàng chờ người (mục 9) |

## Mục 9 — Khi autopilot đang bật

Chi tiết: [method/autopilot.md](../../../method/autopilot.md) mục 5–7. Điều phối **không ký cổng**: cổng do Gate Delegate phiên mới ký (mẫu brief ở mục 6.3 của file đó: điều phối chỉ điền chỗ `<…>`, không thêm câu, không gợi ý kết luận).

1. **Trước khi giao mỗi phiên con:** chép `.tmp/autopilot.json` vào `.tmp/` của thư mục làm việc (worktree) của phiên đó, `sprints` = đúng sprint phiên làm; mỗi phiên con một nhánh riêng; phiên con không tự mở subagent trừ khi brief cho phép, mà cho phép thì mỗi subagent là một dòng sổ và tính vào trần. Brief nêu danh sách loại, bốn điều kiện dừng, và quyền không vượt lời cấp. **Khi giao và khi nhận báo**, kiểm file dấu còn đó và nội dung khớp; thiếu hoặc lệch → phiên con đã ra khỏi rào: dừng nó, ghi `BR` loại (c), soát `git reflog`, nhánh remote, tag mới.
2. **Sổ phiên con** — bảng trong PROGRESS mục "Sổ phiên con", **một dòng mỗi lần giao** (cả Gate Delegate, reviewer, lần giao lại sau review), đủ sáu cột:

   | Phiên | vai · tier · model · effort | thư mục/worktree | nhánh | trạng thái | bằng chứng |
   |---|---|---|---|---|---|

   Trạng thái chỉ một trong: `đang chạy` · `xong` · `dừng ở điểm an toàn` · `dừng khẩn` · `cạn hạn mức` · `lỗi`. Ghi `xong` chỉ sau khi **tự chạy lại lệnh kiểm** và đọc `git diff`; cột bằng chứng nêu sha và lệnh đã chạy lại. Dòng sổ kế tiếp sẽ vượt trần phiên → không giao, tạm dừng (không ghi `revoked_at`, giữ file dấu, `BR` `chờ người`).
3. **Gặp danh sách loại hoặc điều kiện (a)–(c):** dừng **đúng bước đó**, ghi `BR` `chờ người` (hàng chờ người), chạy tiếp phần không phụ thuộc. Phiên con xin quyền ngoài lệnh → **từ chối**, ghi vào hàng chờ người; không nới, không "một lần thôi". Điều kiện (d), PLAN hỏng → tạm dừng cả autopilot. Nâng trần phải bằng lệnh mới; "ok, chạy thêm" không nâng.
4. **`Dừng autopilot.`** (mức chương trình: mọi hồ sơ của dải) hoặc **`Thu hồi duyệt thay SPR-NN.`** (chỉ sprint đó) giữa chừng, theo thứ tự: ghi `revoked_at` vào khối `delegation`, cổng chưa kết luận về `pending` → báo dừng xuống mọi phiên con liên quan → mỗi phiên tới **điểm an toàn kế tiếp** (không bắt đầu việc mới; lệnh đang chạy chạy xong; commit đang làm hoàn tất kèm test; không commit được thì đưa thay đổi vào nhánh tạm `autopilot-stop/<SPR-NN>-<phiên>`, không `git stash` trần, không `--no-verify`) → ghi trạng thái từng dòng sổ (`dừng ở điểm an toàn`, sha hoặc đường worktree) → **xoá file dấu sau cùng** (thu hồi một sprint: bỏ nó khỏi `sprints` mọi file dấu, rỗng thì xoá) → báo người dùng trạng thái từng phiên. Xoá file dấu trước khi phiên con báo dừng là mất rào giữa chừng.
