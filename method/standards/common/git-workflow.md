---
title: Git workflow — commit and pull request format
type: method
status: active
updated: 2026-10-04
---

<!-- Nguồn: affaan-m/ECC rules/common/git-workflow.md @ ef648e01 (MIT). Viết lại, giữ ý về định dạng commit và
     nội dung PR; luật git, đẩy nhánh và phát hành lấy từ luật lõi (`AGENTS.md`, `method/conventions.md` mục 4),
     không từ nguồn. -->

# Quy trình git: định dạng commit và PR

> **Kết luận:** chuẩn này chỉ nói **commit và PR trông thế nào**. Luật git (không bỏ hook, không force-push,
> không `git stash` trần, không tự tăng version, push chỉ sau Cổng 2) thuộc `method/conventions.md` mục 4 và
> `AGENTS.md`; hai nơi khác chuẩn này thì luật lõi thắng.

## Commit

- Dòng đầu một câu tóm tắt việc đã làm, kèm mã `TK` của việc khi có; thân ngắn (tuỳ chọn) nói **vì sao**,
  không kể lại diff.
- Dự án dùng kiểu conventional commits thì tiền tố là một trong: `feat`, `fix`, `refactor`, `docs`, `test`,
  `chore`, `perf`, `ci`; mã `TK` đi sau tiền tố.
- Một việc (`TK`) ít nhất một commit; mỗi commit một thay đổi có nghĩa, build và test qua được.
- Dòng ghi đồng tác giả theo chỉ dẫn của môi trường đang chạy; chuẩn này không quy định.

## Pull request

Chỉ tạo PR **khi người dùng đã gật** sau Cổng 2 (skill `closing-sprint`, menu kết thúc). Khi được tạo:

1. Đọc **cả lịch sử** của nhánh, không chỉ commit cuối: `git log --oneline <BASE>..HEAD`.
2. Xem toàn bộ thay đổi so với nhánh gốc: `git diff <BASE>..HEAD` (`BASE` lấy bằng `git merge-base`).
3. Viết tóm tắt PR theo kết quả đã kiểm: thay đổi gì, vì sao, bằng chứng đã chạy.
4. Ghi kế hoạch kiểm: các bước người khác chạy lại được, kèm việc còn mở.

Đẩy nhánh, mở PR, gộp vào nhánh chính là tác động ra ngoài — làm theo giấy phép nêu trong lời giao, không suy ra.
Quy trình phát triển đầy đủ trước khi đụng git: `development-workflow.md`.
