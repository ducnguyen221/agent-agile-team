# Autopilot — phần của running-sprint

> Phần luật autopilot của skill này, dời từ `SKILL.md` (SPR-16 TK1); một chế độ mặc định bật từ SPR-20 TK23; chỉ đường dẫn tương đối tới `method/` đổi theo vị trí file. Đọc khi sprint chạy.

## Cờ đỏ về autopilot (từ mục 8)

| Ý nghĩ | Thực tế |
|---|---|
| "Phiên con báo xong, ghi `xong` luôn" (autopilot) | ghi `xong` sau khi tự chạy lại lệnh kiểm và đọc `git diff`; lời tự báo không phải bằng chứng |
| "Phiên con xin thêm quyền một lần thôi" (autopilot) | ngoài lời cấp thì từ chối, ghi `BR` (mục 9) |
| "Sắp vượt trần, ghi số lớn hơn vào `sessions_cap` cho khỏi dừng" | agent không tự nâng trần: dừng, ghi `BR`, Gate Delegate quyết nâng |

## Mục 9 — Khi autopilot đang bật (mặc định mọi sprint)

Chi tiết: [method/autopilot.md](../../../method/autopilot.md) mục 5–7. Điều phối **không ký cổng**: cổng do Gate Delegate phiên mới ký (mẫu brief ở mục 6.3 của file đó: điều phối chỉ điền chỗ `<…>`, không thêm câu, không gợi ý kết luận). Điều phối được tạo phiên phụ, làm mọi việc git trên nhánh sprint, dồn câu hỏi vào báo cuối và lặp tới xong; cơ chế vòng chi tiết thuộc sprint sau.

1. **Trước khi giao mỗi phiên con:** chép `.tmp/autopilot.json` vào `.tmp/` của thư mục làm việc (worktree) của phiên đó, `sprints` = đúng sprint phiên làm; mỗi phiên con một nhánh riêng; phiên con không tự mở subagent trừ khi brief cho phép, mà cho phép thì mỗi subagent là một dòng sổ và tính vào trần. Brief nêu bảy mục luôn chặn, bốn điều kiện dừng, và quyền không vượt lời cấp. **Khi giao và khi nhận báo**, kiểm file dấu còn đó và nội dung khớp; thiếu hoặc lệch → phiên con đã ra khỏi rào: dừng nó, ghi `BR` loại (c), soát `git reflog` và nhánh.
2. **Sổ phiên con** — bảng trong PROGRESS mục "Sổ phiên con", **một dòng mỗi lần giao** (cả Gate Delegate, reviewer, lần giao lại sau review), đủ sáu cột:

   | Phiên | vai · tier · model · effort | thư mục/worktree | nhánh | trạng thái | bằng chứng |
   |---|---|---|---|---|---|

   Trạng thái chỉ một trong: `đang chạy` · `xong` · `dừng ở điểm an toàn` · `dừng khẩn` · `cạn hạn mức` · `lỗi`. Ghi `xong` chỉ sau khi **tự chạy lại lệnh kiểm** và đọc `git diff`; cột bằng chứng nêu sha và lệnh đã chạy lại. Dòng sổ kế tiếp sẽ vượt trần phiên → không giao, dừng (không ghi `revoked_at`, giữ file dấu, `BR`); Gate Delegate quyết nâng thì chạy tiếp.
3. **Gặp bảy mục luôn chặn hoặc điều kiện (a)–(c):** dừng **đúng bước đó**, ghi `BR`, chạy tiếp phần không phụ thuộc; việc vào báo cuối nếu Gate Delegate không quyết được. Phiên con xin quyền ngoài lời cấp → **từ chối**, ghi `BR`; không nới, không "một lần thôi". Điều kiện (d), PLAN hỏng → dừng cả sprint.
4. **`Dừng autopilot.`** (mức chương trình: mọi hồ sơ của dải) hoặc **`Thu hồi duyệt thay SPR-NN.`** (chỉ sprint đó) giữa chừng, theo thứ tự: ghi `revoked_at` vào khối `delegation`, cổng chưa kết luận về `pending` → báo dừng xuống mọi phiên con liên quan → mỗi phiên tới **điểm an toàn kế tiếp** (không bắt đầu việc mới; lệnh đang chạy chạy xong; commit đang làm hoàn tất kèm test; không commit được thì sao lưu theo `method/git-conventions.md` mục 4 hoặc nhánh tạm `autopilot-stop/<SPR-NN>-<phiên>`, không `git stash` trần, không `--no-verify`) → ghi trạng thái từng dòng sổ (`dừng ở điểm an toàn`, sha hoặc đường worktree) → **xoá file dấu sau cùng** (thu hồi một sprint: bỏ nó khỏi `sprints` mọi file dấu, rỗng thì xoá) → báo người dùng trạng thái từng phiên. Xoá file dấu trước khi phiên con báo dừng là mất rào giữa chừng.
5. **Brief phiên con cấm ba thứ**, ghi nguyên văn trong brief: không ghi hay sửa khối `delegation` (chỉ phiên điều phối ghi, một người ghi), không ghi hay đổi khoá cổng (`gate_N`, `gate_N_mode`, `gate_N_quote`, `gate_N_at`), không tạo, sửa hay xoá file dấu `.tmp/autopilot.json`. Phiên con thấy cần đổi một trong ba → dừng và báo điều phối, ghi `BR`; không tự làm "cho tiện".

## Mục 10 — Tin mở autopilot (gửi một lần, không chờ)

Một tin gom ở đầu sprint và đầu mỗi phiên tiếp tục, gửi **sau** khi review PLAN xong (`method/process.md` mục 3). Mẫu đầy đủ ở [method/autopilot.md](../../../method/autopilot.md) mục 2: vai · tier · model · effort từng agent sẽ giao, trần phiên (công thức mục 2.1), người ký cổng, bảy việc luôn chặn, cách dừng `Dừng autopilot.`. Thêm dòng **5 ý** khi sprint sửa file luật:

```
5 ý (chỉ khi sửa file luật): <sửa gì · file nào, chỗ nào · ảnh hưởng · lợi · hại và cách hoàn tác>
```

- **Một tin:** tin mở, 5 ý (nếu có), `CQ`/`DN` cùng khuyến nghị đi cùng nhau; không hỏi lẻ. Việc sửa file luật chờ người dùng gật trong chat (một trong số ít chỗ cần người); phần khác chạy tiếp.
- **Diff lệch 5 ý:** khi diff thật chạm file hoặc chỗ ngoài những gì 5 ý đã nêu và người dùng đã gật, xin lại **đúng phần lệch**, không xin lại cả bản; phần đã gật giữ nguyên.
