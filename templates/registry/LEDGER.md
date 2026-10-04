# Sổ tập trung — tên dự án

<!-- Mẫu cho file sổ tập trung của MỘT dự án: một file Markdown mỗi dự án, nằm trong kho sổ do máy chọn (không
     nằm trong repo dự án). Dự án bật sổ bằng khoá `ledger.project` trong `.agile.json`; máy cấp mẫu đường kho qua
     biến môi trường `AGENT_AGILE_LEDGER` (có `{project}`). File sổ có thể chứa nội dung khác — `check` chỉ đọc
     BẢNG có cột đầu "Sprint". Khi nào ghi, ghi gì: `method/process.md` mục 11. -->

> Một dòng mỗi sprint, mới nhất ở trên. Dòng nào lệch hồ sơ sprint (trạng thái, ngày) thì `check` báo.

## Sprint

Sổ tập trung ghi mỗi dòng một **sprint** (SPR); cột Trạng thái dùng đúng giá trị `status` của PROGRESS hoặc SPRINT, cột Cập nhật là ngày ghi dòng (`YYYY-MM-DD`, không cũ hơn `updated` của hồ sơ), cột Hồ sơ là `<repo>:docs/plans/<slug>/<tài-liệu>.md` (`<tài-liệu>` là `PROGRESS.md` khi sprint đang mở, `REPORT.md` khi đã `done`/`dropped`, `SPRINT.md` với sprint một file), cột Link là liên kết bấm được:

- hồ sơ **trong repo** → URL GitHub blob `https://github.com/<owner>/<repo>/blob/<ref>/docs/plans/<slug>/<tài-liệu>.md` (`<ref>` là nhánh sprint khi đang mở; `main` hoặc SHA khi đã đóng);
- hồ sơ **ngoài repo** → đường tương đối tính từ thư mục chứa file sổ này tới thư mục plan.

| Sprint | Trạng thái | Cập nhật | Hồ sơ | Link |
|---|---|---|---|---|
<!-- Ví dụ hai dòng (xoá comment khi ghi dòng thật đầu tiên):
| SPR-02 | in_progress | 2026-02-03 | order-desk:docs/plans/2026-02-01-export-orders/PROGRESS.md | [PROGRESS](https://github.com/acme/order-desk/blob/sprint/export-orders/docs/plans/2026-02-01-export-orders/PROGRESS.md) |
| SPR-01 | done | 2026-01-16 | order-desk:docs/plans/2026-01-15-order-lookup/REPORT.md | [REPORT](order-desk/2026-01-15-order-lookup/REPORT.md) |
-->
