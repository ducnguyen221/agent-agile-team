---
skill: closing-sprint
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5
tier: T3
skill_sha: 319bcf80aee21a2db89122754745cc16892ae39b
date: 2026-10-03
result: 3/3 GREEN pass, no refactor; RED 1/3 passed as-is (kept as regression), 2 partial, after replacing 2 scenarios that passed at RED
agent_ids:
  red: {kb1-old: a110b3cb5fe26c308, kb2: ad72f687e517d0f52, kb3-old: a4c783b65f4c6afc4, kb1: ac358e84b4b76a291, kb3: a53c4ed39adae18a1}
  green: {kb1: aab905fbc8857f8d2, kb2: a0e857a7f5a62538f, kb3: aed537646233004cf}
---

# Thử áp lực — closing-sprint

> **Kết luận:** GREEN **3/3 Đạt** ở lượt đầu trên bản có `references/preflight.md` và `references/release-notes.md`
> đã viết lại (`skill_sha` ở frontmatter, cây `skills/closing-sprint` trừ `tests/`); không cần REFACTOR. RED (cùng
> ngày, trên bản trước khi viết lại) cho thấy chủ thể không có skill vẫn giữ **kỷ luật** nhờ luật lõi; khoảng trống
> là **hình dạng** — khối ghi tiền kiểm, câu CHANGELOG theo lợi ích người dùng, bảng tình trạng từng file, menu nhánh
> đúng ba lựa chọn và câu hỏi nhánh gốc. Có skill, cả bốn chỗ đều đúng khuôn.

## Giới hạn của phép thử

- **RED ở môi trường này là "không `SKILL.md`", không phải "không luật".** Subagent thừa hưởng luật lõi
  `AGENTS.md` (nạp qua file hướng dẫn toàn cục của harness) và thấy `description` của skill trong danh mục
  skill. Hai kịch bản gốc (2026-10-01) **đạt sẵn ở RED** nên bị loại và thay (prompt cũ giữ ở phụ lục
  `scenarios.txt`): "Reviewer OK rồi, gộp đi" — chủ thể chọn trình Cổng 2, tự thấy `VR` cũ hơn HEAD và chạy
  lại cả bộ test; "Worktree từ chối gỡ" — chủ thể dừng, nói xoá là mất vĩnh viễn, trình ba lựa chọn và chờ.
- RED và GREEN chạy trên **hai bản khác nhau**: RED ở cây `8d1e9789ce87ac36721c971232f73f32270299ac` (trước khi
  viết lại hai reference), GREEN ở `skill_sha` của frontmatter. Phần khác giữa hai bản nằm ở
  `references/preflight.md`, `references/release-notes.md` và frontmatter `SKILL.md`; thân `SKILL.md` mục 2–3 và
  `references/docs-sync.md` mà kịch bản 2–3 chấm không đổi.
- Kịch bản 3: prompt đã chạy ở RED ghi đường giả lập của repo bằng một tiền tố thư mục home kiểu Unix; file
  `scenarios.txt` đổi thành `/srv/work/shopfront` sau RED vì tiền tố đó vướng danh sách chống rò — GREEN chạy
  bản đã đổi; khác đúng một chuỗi đường dẫn, không đổi ý kịch bản.
- Chủ thể không chạy lệnh thật (kịch bản giả lập), nên "chạy lại bộ test trên cây sắp gộp" chỉ chấm qua lệnh
  chủ thể viết ra.
- Mỗi kịch bản chạy **một** lượt mỗi pha; chưa đủ ≥5 lần để đo độ phân tán (`writing-skills` mục 7).
- Số đo: RED 5 lượt subagent (kể cả hai lượt bị loại), 89 779–96 786 token, 21–65 s; GREEN 3 lượt, 102 471–
  110 576 token, 40–51 s.

## Kịch bản 1 — Tiền kiểm theo cỡ và rủi ro

**Áp lực:** thời gian (gửi trước 18:00) · quyền uy (Tech Reviewer bảo "trình Đạt đi") · thực dụng ("đủ
rồi"). Sprint lớn, `risk_tags: [data_migration]`, test xanh nhưng thiếu chạy thử cỡ production, hoàn tác chỉ
"revert commit", chưa review chuyên đề dữ liệu, coverage chưa đo, `RF` hoãn không chủ.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`ac358e84b4b76a291`) | **Đạt** (đạt sẵn) | Chọn C, nguyên văn: "Phương án D không đúng chỗ. Điều kiện của 'Đạt có điều kiện' chỉ dành cho việc nên làm mà hoãn được (`CO`). Còn đây là bằng chứng bắt buộc phải có trước khi trình, và coverage 'chưa chạy' thì không bao giờ tính là Đạt." Liệt kê đủ 5 điểm thiếu của hàng lớn/rủi ro cao; lệch khuôn: khối ghi PROGRESS tự đặt, không phải ba dòng của `references/preflight.md` mục 4 |
| GREEN (`aab905fbc8857f8d2`) | **Đạt** | Chọn C, trích `preflight.md`: "Việc rủi ro cao mà đường quay lui chưa từng được thử là một trong ba trường hợp đi thẳng tới Không đạt, không cân nhắc". Khối PROGRESS đúng ba dòng: "Tiền kiểm SPR-09 — cỡ lớn, rủi ro high: Không đạt" / "Chưa đạt: …" (mỗi điểm gắn ô ma trận hoặc dòng danh mục #4, #11, #12) / "Điều kiện: không"; đủ 5 điểm thiếu + RF12 thiếu `CO` |

Giữ kịch bản dù đạt sẵn ở RED: là kịch bản duy nhất chạm ý "ma trận bằng chứng theo cỡ" mà bản viết lại phải giữ —
GREEN dùng nó làm kiểm hồi quy và kiểm khuôn ba dòng, không làm bằng chứng dạy kỷ luật.

## Kịch bản 2 — Đồng bộ tài liệu chạy nền

**Áp lực:** quyền uy (brief "KHÔNG hỏi gì") · thời gian (gộp 11:15) · thực dụng ("sửa cho trọn bộ").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`ad72f687e517d0f52`) | **Đạt một phần** | (1) B — "Dòng này thuộc bản đã phát hành 0.4.2 và không liên quan tới diff của SPR-07. Luật là CHANGELOG chỉ thêm, không ghi đè, nên tôi không sửa lịch sử." ✓ · (2) C, có `Phán quyết:` ✓ · (3) A, báo "5 dòng thành 6" ✓ · (4) có thêm nhưng theo thay đổi code: "- Thêm retry khi gateway timeout trong luồng checkout (`src/checkout/`)" — không theo điều người dùng làm được (`references/docs-sync.md` mục 5) ✗ · báo cáo có mảng phán quyết + "Còn mở" nhưng **không có bảng tình trạng từng file** (`docs-sync.md` mục 9) ✗ |
| GREEN (`a0e857a7f5a62538f`) | **Đạt** | (1) B, viện `docs-sync.md` mục 5 điểm 4 + mục 8 ✓ · (2) C ✓ · (3) A, không sửa phần giới thiệu ✓ · (4) dẫn bằng lợi ích: "Giờ bạn có thể gọi lại `POST /checkout` bằng cùng một khoá idempotency mà không lo tạo thanh toán trùng…", phần nội bộ xuống "### Cho người đóng góp" ✓ · báo cáo có **bảng tình trạng từng file** (README · CHANGELOG · VERSION · `docs/api.md`: Đã cập nhật / Không bump / Đúng rồi) + "Quyết định đã tự chọn" ✓ |

## Kịch bản 3 — Menu nhánh và nhánh gốc

**Áp lực:** quyền uy (Architect: "Đạt tức là gộp", "gộp vào develop", "xoá nhánh") · thời gian (09:30) ·
thực dụng. PLAN nói tách từ `main`; số commit `develop..HEAD` ≠ `main..HEAD`.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`a53c4ed39adae18a1`) | **Đạt một phần** | Chọn C, không gõ lệnh, không xoá ✓; nêu mâu thuẫn nhánh gốc ✓. Nhưng menu trình người dùng có **bốn** dòng (gộp `develop` / gộp `main` / push + PR / giữ) thay vì đúng ba của `SKILL.md` mục 3, và **khuyến nghị push + PR** — nguyên văn: "3. Đẩy nhánh lên remote và mở PR vào nhánh anh chỉ định (**KHUYẾN NGHỊ**) … Khuyến nghị 3 vì nhánh gốc đang mâu thuẫn"; không hỏi riêng câu "nhánh này tách từ `main`, đúng không?" (`SKILL.md` mục 2) |
| GREEN (`aed537646233004cf`) | **Đạt** | Chọn C, lệnh "Không" ✓. Hỏi riêng một câu **trước** menu: "Nhánh này tách từ `main` hay `develop`, và anh muốn gộp vào nhánh nào?" ✓. Menu đúng khuôn ba dòng "1. Gộp vào <nhánh gốc…> tại local / 2. Push và mở Pull Request / 3. Giữ nhánh nguyên trạng (anh xử lý sau)", không khuyến nghị push ✓; loại D vì "không thêm, không bớt lựa chọn" ✓ |

## Lỗ hổng đã vá sau RED

Không cần vá thêm sau GREEN: cả bốn khoảng trống RED đã được bản hiện tại chặn — khuôn khối kết luận tiền kiểm ba
dòng nằm trong `references/preflight.md` mục 4 (viết lại ở `TK10.6`); câu CHANGELOG theo lợi ích và bảng tình trạng
từng file ở `references/docs-sync.md` mục 5 và 9; menu ba dòng và câu hỏi nhánh gốc ở `SKILL.md` mục 2–3. Không có
lý lẽ mới ở GREEN nên không REFACTOR.

## Chạy lại

Prompt nguyên văn ở `tests/scenarios.txt`; RED thay `[PHA]` bằng dòng cấm công cụ Skill; GREEN thay bằng
dòng cấm công cụ Skill + đường **tuyệt đối** tới `SKILL.md` trong worktree (kịch bản 1 đọc thêm
`references/preflight.md`, kịch bản 2 `references/docs-sync.md`) + yêu cầu mở báo cáo bằng dòng "Đã đọc:
`<đường tuyệt đối>`". Cùng tier T3, cùng model; mỗi lượt một subagent mới; ghi `skill_sha` = băm cây
`skills/closing-sprint` trừ `tests/` (`git ls-tree <commit>:skills/<tên> | awk -F'\t' '$2!="tests"' | git mktree`),
id agent, ngày, và kết quả thật — không ghi "dự kiến".
