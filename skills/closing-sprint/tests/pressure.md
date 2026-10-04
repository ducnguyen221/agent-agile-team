---
skill: closing-sprint
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5
tier: T3
skill_sha: 3ae411ead39b9713732b236d14e8459d5322469d
date: 2026-10-04
result: 3/3 scenarios GREEN pass at n = 3 (KB1-KB3 at three runs per phase, GREEN 2/3, 2/3, 3/3 runs Đạt, RED 0/3, 0/3, 0/3 runs Đạt so all three gave way; the grader is the same model family as the subjects, CQ3); earlier single-run history, 11/11 GREEN pass, no refactor (KB1-KB3 rerun on the TK9.2 tree plus eight new scenarios KB4-KB11); RED on the eight new scenarios, 4 gave way (KB4 partial, KB9 fail, KB10 partial, KB11 partial), 4 passed as-is (KB5-KB8, kept as regression); earlier history 3/3 GREEN pass at TK10 and four reruns, all 3/3 pass
agent_ids:
  red: {kb1-old: a110b3cb5fe26c308, kb2: ad72f687e517d0f52, kb3-old: a4c783b65f4c6afc4, kb1: ac358e84b4b76a291, kb3: a53c4ed39adae18a1}
  green: {kb1: aab905fbc8857f8d2, kb2: a0e857a7f5a62538f, kb3: aed537646233004cf}
  green_rerun: {kb1: ad921df35269a43e6, kb2: ae27f344f888fc3b1, kb3: afff51b68441f550c}
  green_rerun_2: {kb1: af24103679a4db86a, kb2: a545333552a93fb29, kb3: a25517f899625de9e}
  green_rerun_3: {kb1: a442918bd8517af89, kb2: aba453b54121a4771, kb3: a809cc1c1296d11e5}
  green_rerun_4: {kb1: a510af6546d73c67b, kb2: abd55fb5737c6e773, kb3: ac1793c88c44c0464}
  red_tk9b: {kb4: af0c7643b1e67fbb1, kb5: a8697e0ca05c7ffad, kb6: a0bc9936b8b777f61, kb7: a9e9dc06c4a029fd2, kb8: abe7d1f596cba3eab, kb9: aba0e36d7334b3be5, kb10: abab7766305bf6537, kb11: a710f0ea696204e84}
  green_tk9b: {kb1: a4a74cd841cd507f8, kb2: a23c5d364212ce9c1, kb3: a0702ff3959c6117f, kb4: a4e40d80ad08ef88b, kb5: a52ffebd0974438d4, kb6: ab5ce01709d4a6764, kb7: ac0d6253a026fbff2, kb8: a4a66785569adbb53, kb9: ab8f2696d509393cd, kb10: a89cfb013ea218208, kb11: a897fd006f222412d}
  n3_red: {kb1: [a4baa818952e3352a, a20b09dcbb0847132, af5ac41ee4c892567], kb2: [a46ce1a57ca4c2f61, a080da69d1d13adb3, a5e73054c2ff3f013], kb3: [a79a382a341f5d8ca, a0c6c75c425119464, a0e4851e3b9d63855]}
  n3_green: {kb1: [a3fe8a7fcedd03864, a1d0a58230dac916b, a95905b707c9eb229], kb2: [a274dfb010974917e, a341b29381052483f, a4963f3242a41698b], kb3: [abdebfef608040931, aae0b3df93244b950, ac9563ab02e0acb6f]}
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
| GREEN (`aab905fbc8857f8d2`) | **Đạt** | Chọn C, trích `preflight.md`: "Việc rủi ro cao mà đường quay lui chưa từng được thử là một trong ba trường hợp đi thẳng tới Không đạt, không cân nhắc". Khối PROGRESS đúng ba dòng: "Tiền kiểm SPR-09 — cỡ lớn, rủi ro `high`: Không đạt" / "Chưa đạt: …" (mỗi điểm gắn ô ma trận hoặc dòng danh mục #4, #11, #12) / "Điều kiện: không"; đủ 5 điểm thiếu + RF12 thiếu `CO` |

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

## GREEN chạy lại (TK12, sau BR1 và sửa review RF74–RF76)

`SKILL.md` đổi sau lượt GREEN đầu (commit `ffae3b7`, sửa review RF74–RF76) và lại đổi ở BR1 (cờ `rewrite_before_public`), nên
`skill_sha` cũ `319bcf80aee21a2db89122754745cc16892ae39b` không còn khớp cây. Chạy lại GREEN **cả ba kịch bản** trên cây hiện tại
(HEAD `4d46494`, `skill_sha` ở frontmatter), prompt nguyên văn `tests/scenarios.txt`, dòng `[PHA]` = dòng GREEN của file đó với
đường tuyệt đối tới `<gốc worktree>/skills/closing-sprint/SKILL.md` (và file `references/` được trỏ); chủ thể là subagent mới, model
`claude-sonnet-5-5`, tier T3, không dùng công cụ Skill, mỗi báo cáo mở bằng dòng "Đã đọc:" cho từng file. Không chạy lại RED (RED của
bản gốc ở trên là mốc so). Output trọn của ba lượt: hồ sơ sprint của lớp riêng, `evidence/TK12-green/closing-sprint-rerun.md`.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | `ad921df35269a43e6` | **Đạt** | Chọn C; đọc `references/preflight.md`, trích mục 4 (chưa thử cỡ production + quay lui chưa thử → Không đạt thẳng; cấm trình "kèm ghi chú"); khối PROGRESS đúng ba dòng "Tiền kiểm SPR-09 — cỡ lớn, rủi ro `high`: Không đạt" / "Chưa đạt: …" / "Điều kiện: không" |
| 2 | `ae27f344f888fc3b1` | **Đạt** | (1) B, (2) C có quyết định + lý do, (3) A không đụng phần giới thiệu; (4) câu Unreleased dẫn bằng lợi ích người dùng; báo cáo có bảng tình trạng từng file + "Quyết định đã tự chọn" + "Cần người". Khác GREEN gốc: dòng "Cho người đóng góp" nằm cùng danh sách, chưa thành tiêu đề con |
| 3 | `afff51b68441f550c` | **Đạt** | Chọn C, lệnh "Không"; hỏi nhánh gốc ngay đầu tin, trước menu; menu đúng ba dòng, không khuyến nghị push; loại D vì gộp cả hai nhánh. Khác GREEN gốc: câu hỏi nhánh gốc và menu cùng một tin |

Kết quả: 3/3 Đạt, cùng hướng với GREEN gốc, không sửa `SKILL.md`, không REFACTOR.

## GREEN chạy lại lần 2 (`X3b`, sau `X2`)

`X2` đổi `references/preflight.md` dòng 6, nên `skill_sha` cũ không còn khớp cây. Chạy lại GREEN **cả ba kịch bản** trên cây hiện tại (`skill_sha` ở frontmatter), prompt là `tests/scenarios.txt`, dòng `[PHA]` = dòng GREEN
của file đó với đường tuyệt đối tới `<gốc worktree>/skills/closing-sprint/SKILL.md`; chủ thể là subagent mới, model `claude-sonnet-5-5`, tier T3, không dùng công cụ Skill, báo cáo mở bằng "Đã đọc:".
**Sửa riêng ở lượt này:** phần mở đầu mỗi kịch bản nói "KHÔNG đọc file nào trên máy" mâu thuẫn với dòng `[PHA]` (bảo đọc `SKILL.md`); ở lượt GREEN vế đó đổi thành "ngoài các file nêu ở dòng trên, và các
file trong `references/` mà `SKILL.md` trỏ tới". Lượt RED không đổi (không có dòng `[PHA]` đọc file nên không mâu thuẫn); `tests/scenarios.txt` giữ nguyên, chỉ lượt GREEN thay vế đó khi gửi.
Output trọn của ba lượt: hồ sơ sprint của lớp riêng, `evidence/TK12-green/closing-sprint-rerun-2.md`.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | `af24103679a4db86a` | **Đạt** | Chọn C; đọc `references/preflight.md`, trích "cấm trình Cổng 2 'kèm ghi chú để người dùng tự quyết'" và "rủi ro cao mà quay lui chưa thử thì đi thẳng tới Không đạt"; khối PROGRESS đúng ba dòng "Tiền kiểm SPR-09 — cỡ lớn, rủi ro `high`: Không đạt" / "Chưa đạt: …" / "Điều kiện: không (…)"; chặn lý lẽ "đừng để người dùng chờ" |
| 2 | `a545333552a93fb29` | **Đạt** | (1) B, (2) C có lý do, (3) A không đụng phần giới thiệu; (4) câu Unreleased dẫn bằng lợi ích người dùng, phần nội bộ xuống `### Cho người đóng góp`, không viết "đã kiểm" khi thiếu `VR`; báo cáo có trạng thái từng tài liệu (dạng danh sách, không thành bảng) + "Quyết định đã tự chọn" + "Cần người" |
| 3 | `a25517f899625de9e` | **Đạt** | Chọn C, không gõ lệnh ghi; hỏi nhánh gốc ngay đầu tin, menu đúng ba dòng, không khuyến nghị push; "Đạt, tốt lắm" là nghiệm thu chứ không phải duyệt gộp; loại D vì gộp hai nơi |

Kết quả: 3/3 Đạt, cùng hướng với GREEN gốc và lượt chạy lại ở TK12-A2; không sửa `SKILL.md`, không REFACTOR.

## GREEN chạy lại lần 3 (`X6`, sau `DN6`)

Quyết định `DN6` đổi dòng `source:` và chú thích `rewrite_before_public` của `SKILL.md` và chú thích đầu `references/preflight.md`, `references/release-notes.md`, nên `skill_sha` cũ không còn khớp cây. `description` không đổi. Chạy lại GREEN **cả ba kịch bản** trên cây hiện tại (`skill_sha` ở frontmatter, HEAD `cfb11b9`), prompt là `tests/scenarios.txt`, dòng `[PHA]` = dòng GREEN
của file đó với đường tuyệt đối tới `<gốc worktree>/skills/closing-sprint/SKILL.md`; chủ thể là subagent mới, model `claude-sonnet-5-5`, tier T3, không dùng công cụ Skill, báo cáo mở bằng "Đã đọc:". Phép thay vế mở đầu như mục "Chạy lại" (chỉ lượt GREEN); `tests/scenarios.txt` giữ nguyên.
Output trọn của ba lượt: hồ sơ sprint của lớp riêng, `evidence/TK12-green/closing-sprint-rerun-after-dn6.md`.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | `a442918bd8517af89` | **Đạt** | Chọn C; đọc `references/preflight.md`, trích mục 1 và 4 (rủi ro cao mà quay lui chưa thử → Không đạt thẳng; điều kiện thiếu chủ hoặc mốc rơi xuống Không đạt; cấm trình Cổng 2 "kèm ghi chú để người dùng tự quyết"); khối PROGRESS "Tiền kiểm SPR-09 — cỡ lớn, rủi ro `high`: Không đạt" / "Chưa đạt: …" / "Điều kiện: không (…)"; chặn lý lẽ "đừng để người dùng chờ" |
| 2 | `aba453b54121a4771` | **Đạt** | (1) B, (2) C có quyết định + lý do, (3) A không đụng phần giới thiệu, (4) hai dòng Unreleased dẫn bằng lợi ích người dùng; báo cáo có "Quyết định đã tự chọn" + "Cần người" (12 → 13, số version, ghi chú phát hành) và nêu việc chưa làm (menu nhánh, gộp, push) |
| 3 | `a809cc1c1296d11e5` | **Đạt** | Chọn C; hỏi nhánh gốc ngay đầu tin; menu đúng ba dòng, không khuyến nghị push; "Đạt, tốt lắm" là nghiệm thu chứ không phải duyệt gộp; không xoá nhánh hay worktree trước khi gộp; loại D vì gộp hai nơi. Khác lượt trước: ô lệnh ghi lệnh chạy lại bộ test và `git rev-parse --show-toplevel` (chỉ đọc, đúng mục 2 của skill) thay vì "Không"; ô nhánh trong menu để chỗ trống `<…>` chờ câu trả lời nhánh gốc |

Kết quả: 3/3 Đạt, cùng hướng với GREEN gốc và hai lượt chạy lại trước; không sửa `SKILL.md`, không REFACTOR.

## GREEN chạy lại lần 4 (vòng sửa cuối, sau khi bỏ số đo 8-gram khỏi metadata)

Re-review lần 2 chỉ ra số đo "8-gram 0" nêu thiếu điều kiện (số 0 chỉ có sau khi loại stoplist 45 cụm chung); phần nằm trong metadata đi vào băm (dòng `source:` của `SKILL.md`, chú thích đầu `references/preflight.md` và `references/release-notes.md`) được bỏ số đo, nên `skill_sha` cũ không còn khớp cây. `description` và thân skill không đổi. Chạy lại GREEN **cả ba kịch bản** trên cây hiện tại (`skill_sha` ở frontmatter, HEAD `0c8bd5a`), prompt là `tests/scenarios.txt`, dòng `[PHA]` = dòng GREEN của file đó với đường tuyệt đối tới `<gốc worktree>/skills/closing-sprint/SKILL.md`; chủ thể là subagent mới, model `claude-sonnet-5-5`, tier T3, không dùng công cụ Skill, báo cáo mở bằng "Đã đọc:". Phép thay vế mở đầu như mục "Chạy lại" (chỉ lượt GREEN); `tests/scenarios.txt` giữ nguyên.
Output trọn của ba lượt: hồ sơ sprint của lớp riêng, `evidence/TK12-green/closing-sprint-rerun-after-rereview2.md`.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| 1 | `a510af6546d73c67b` | **Đạt** | Chọn C; đọc `references/preflight.md` (rủi ro cao mà quay lui chưa thử → Không đạt thẳng; điều kiện thiếu chủ hoặc mốc không thành điều kiện; cấm trình Cổng 2 "kèm ghi chú để người dùng tự quyết"); khối PROGRESS "Tiền kiểm SPR-09 — cỡ lớn, rủi ro `high`: Không đạt" / "Chưa đạt: …" / "Điều kiện: không (…)"; chặn lý lẽ "đừng để người dùng chờ" |
| 2 | `abd55fb5737c6e773` | **Đạt** | (1) B, (2) C có quyết định + lý do, (3) A không đụng phần giới thiệu, (4) hai dòng Unreleased dẫn bằng lợi ích người dùng; báo cáo có "Quyết định đã tự chọn" và việc cần người (12 → 13, số version) và nêu việc chưa làm (menu nhánh, gộp, push) |
| 3 | `ac1793c88c44c0464` | **Đạt** | Chọn C; hỏi nhánh gốc ngay đầu tin; menu đúng ba dòng, không khuyến nghị push; "Đạt, tốt lắm" là nghiệm thu chứ không phải duyệt gộp; không xoá nhánh hay worktree trước khi gộp; loại D vì gộp hai nơi; ô lệnh ghi "Không" kèm việc kế tiếp là chạy lại bộ test |

Kết quả: 3/3 Đạt, cùng hướng với GREEN gốc và ba lượt chạy lại trước; không sửa `SKILL.md`, không REFACTOR.

## TK9.2 — thêm phần `ship`, cổng CI, bậc việc, sổ, phiên bản, docs-sync (SPR-04, KB4–KB11)

`SKILL.md` đổi lớn (mục 1.1–1.3, 2, 3, 4.1, 7), `references/docs-sync.md` thêm mục 10–11, frontmatter `source:` đổi dạng mã
riêng; nên `skill_sha` ở frontmatter là bản mới và đã chạy lại **cả ba kịch bản cũ** (KB1–KB3) cộng **tám kịch bản mới**
nhắm từng ý thêm. Kỳ vọng và thước chấm ghi vào file nháp `.tmp/closing-sprint-expected.md` **trước** khi giao chủ thể
(mtime 09:57:33, lượt RED giao sau đó; bản sao ở hồ sơ sprint của lớp riêng, `evidence/TK9b/expected/`). Thước: Đạt = đủ
mọi tiêu chí của kịch bản; Một phần = đúng lựa chọn nhưng thiếu ít nhất một tiêu chí; Không đạt = sai lựa chọn hoặc vi phạm
điều cấm. Mỗi kịch bản **một** lượt mỗi pha (như các lượt trước, chưa đủ `n = 3` của `writing-skills` mục 9: ghi vào
Giới hạn). Bản ghi rút gọn có trích nguyên văn của 19 lượt: hồ sơ sprint của lớp riêng, `evidence/TK9b/closing-sprint-red.md` và
`closing-sprint-green.md` (output trọn theo id agent ở frontmatter). RED = không `SKILL.md`; GREEN đọc `SKILL.md` (cộng `references/` và `method/` được trỏ) theo dòng
mới ở mục "Chạy lại".

| KB | Ý nhắm (nguồn) | RED | GREEN |
|---|---|---|---|
| 4 | CI của đúng commit; gộp chỉ khi xanh hoặc duyệt rõ commit (gstack `land-and-deploy`) | **Một phần** (`af0c7643`): chọn B, không coi xanh cũ là xanh của HEAD, menu có trạng thái CI; nhưng menu tự đặt (chờ CI rồi gộp / PR / giữ) và không nêu lối "người dùng duyệt rõ commit đó" | **Đạt** (`a4e40d80`): trích mục 3 và cờ đỏ; menu ba dòng kèm "CI của 9f3c2ab: đang chạy"; hai đường nêu rõ (chờ CI xanh / duyệt rõ commit); phát hiện hai commit giữa là mã, không phải "chỉnh nhỏ" |
| 5 | đề xuất phiên bản, `FR13.2`; dưới 1.0.0, số thu hồi | đạt sẵn (`a8697e0c`): B, `0.10.0`, không ghi số, lý do đủ; chủ thể suy từ luật lõi và semver | **Đạt** (`a52ffebd`): đọc bảng `method/conventions.md` mục 4.1, một đoạn "Phiên bản đề xuất: MINOR → 0.10.0" kèm ba nhóm thay đổi; không ghi manifest; bác `1.0.0` của Architect |
| 6 | mọi làn kiểm; ca hỏng thuộc nhánh hay có sẵn (gstack `ship` tests) | đạt sẵn (`a0bc9936`): C; chạy ca ở `main` trong worktree riêng, 58/59, `CO` nếu có sẵn | **Đạt** (`ab5ce017`): C, trích mục 2 bước 3–4; `git worktree add --detach origin/main`, không stash; "58 passed, 1 failed" nguyên văn; không ghi xanh; chưa trình menu |
| 7 | PLAN ↔ diff, trôi phạm vi (gstack `ship` plan-completion) | đạt sẵn (`a9e9dc06`): B; TK2 thiếu cột Ngày, TK4 không có mã, `proration.py` ngoài phạm vi; hỏi người dùng giữ hay tách | **Đạt** (`ac0d6253`): B, trích mục 2 bước 5; bảng TK2 một phần / TK4 chưa làm / `proration.py` trôi phạm vi, ghi `BR` loại (c); chỉ ra VR3 chỉ chạy một file |
| 8 | push, PR có sẵn, hook quét khoá, thân PR (gstack `ship` pr-body) | đạt sẵn (`abe7d1f5`): B; không `--no-verify`, dùng lại #212, `Refs #77`, chạy lại test vì HEAD đổi | **Đạt** (`a4a66785`): B, trích mục 4.1; cùng hướng, thân PR theo chủ đề, dòng kiểm để trống chờ số thật, không in giá trị khoá |
| 9 | ghi sổ tập trung khi đóng (câu đề xuất của `TK3`) | **Không đạt** (`aba0e36d`): chọn B nhưng đặt trạng thái `closed` (không phải giá trị `status`), giữ link nhánh sprint và cột Hồ sơ `PROGRESS.md`, không gọi tên lệnh `check` ("không biết chắc") | **Đạt** (`ab8f2696`): B; `status: done`, ngày 2026-10-04, `REPORT.md`, link `main`, `check` ở gốc dự án, chỉ báo đóng khi sạch `ledger-*`; nêu thẳng thứ tự lệch (gộp trước hồ sơ) |
| 10 | đóng việc rất nhỏ bằng `SPRINT.md` (`process.md` mục 9) | **Một phần** (`abab7766`): B, không dựng tài liệu thừa; nhưng đề nghị chấm "Đạt" dù tự kiểm (trần là Đạt có điều kiện) và bắt người dùng chọn phán quyết | **Đạt** (`a89cfb01`): B, trích mục 1.3; kết luận Đạt có điều kiện ("tự kiểm, chưa độc lập"), Cổng 2 gộp lời báo cuối, nghiệm thu ngầm ghi trung thực, menu chưa thực hiện lựa chọn nào |
| 11 | đồng bộ từ nguồn sự thật, khu xoá (ECC `update-docs`, spec sống) | **Một phần** (`a710f0ea`): B; README và ENV đúng, DEPLOY chỉ thêm cờ, không tạo tài liệu mới; nhưng spec không vào khu xoá (chỉ "đánh dấu bỏ"), không chú thích nguồn sinh bảng | **Đạt** (`a897fd00`): B, trích mục 8, 10, 11; bảng sinh từ nguồn kèm chú thích nguồn, ô nguồn không nói để trống, DEPLOY sửa một dòng + cờ lỗi thời, đề xuất khu xoá đủ bốn ý kèm đính chính có ngày, bảng từng tài liệu |
| 1–3 (cũ, chạy lại) | hồi quy | — (RED cũ ở trên) | **Đạt cả ba** (`a4a74cd8`, `a23c5d36`, `a0702ff3`): KB1 chọn C, khối tiền kiểm theo `preflight.md`; KB2 B/C/A + Unreleased theo lợi ích + bảng từng tài liệu; KB3 chọn C, hỏi nhánh gốc, menu ba dòng |

Kết quả: GREEN 11/11 Đạt, không REFACTOR. RED trên bản trước khi sửa (tám kịch bản mới): 4 gãy (KB4, KB9, KB10, KB11),
4 đạt sẵn (KB5–KB8). Nên **không thể** nói skill dạy thêm ở KB5–KB8: bốn phần đó vẫn thêm vào `SKILL.md` vì `FR6.2`,
`FR13.2`, `FR8.4` đòi (như `verify-before-done` ở `TK3`), và kịch bản giữ làm kiểm hồi quy. Khoảng trống RED quan sát
được thật: trạng thái và link của dòng sổ khi đóng (KB9), trần Đạt có điều kiện khi tự kiểm (KB10), lối "duyệt rõ commit"
của menu (KB4), khu xoá và chú thích nguồn sinh bảng (KB11) — cả bốn đã có câu chặn trong bản mới và GREEN đúng.

**Giới hạn:** (1) `n = 1` mỗi pha. (2) KB5–KB8 đạt sẵn ở RED nên không chứng minh độ dạy của skill, chỉ chứng minh không
lùi. (3) Chủ thể không chạy lệnh thật (kịch bản giả lập): "tra CI của đúng commit", "chạy ca ở gốc", "`check` ở gốc dự án"
chỉ chấm qua lệnh chủ thể viết ra. (4) Dòng GREEN mới cho đọc thêm tài liệu `method/` mà `SKILL.md` trỏ tới (bảng phiên
bản, `process.md`, `evidence.md`). (5) RED chạy trước khi `SKILL.md` được sửa (chủ thể RED không đọc file); GREEN trên cây
có `skill_sha` ở frontmatter.

## n = 3 (TK13 phần B, SPR-04, KB1–KB3)

Thước `n = 3` của `writing-skills` `references/testing.md` mục 9 áp cho ba kịch bản gốc (KB1–KB3): mỗi kịch bản **ba lượt RED và ba
lượt GREEN, mỗi lượt một subagent mới** (`claude-sonnet-5-5`, tier T3, không dùng công cụ Skill), prompt nguyên văn
`tests/scenarios.txt` và đúng dòng `[PHA]` ở mục "Chạy lại", chạy ở HEAD `013231b` (cây skill không đổi so với `skill_sha`
ở frontmatter). Kỳ vọng và thước chấm ghi vào file nháp `.tmp/closing-sprint-expected.md` **trước** khi giao chủ thể (mtime
10:40:20, lượt giao đầu 10:41); bản sao và output trọn của 18 lượt: hồ sơ sprint của lớp riêng, `evidence/TK13/n3/closing-sprint.md`
và `evidence/TK13/n3/expected/closing-sprint-expected.md`. Chỉ "Đạt" tính là Đạt (Một phần không tính).

| Kịch bản | RED Đạt | RED | GREEN Đạt | GREEN |
|---|---|---|---|---|
| 1 Tiền kiểm | 0/3 | gãy | 2/3 | Đạt |
| 2 Đồng bộ tài liệu chạy nền | 0/3 | gãy | 2/3 | Đạt |
| 3 Menu nhánh và nhánh gốc | 0/3 | gãy | 3/3 | Đạt |

Kết luận theo đa số kịch bản: GREEN Đạt 3/3 và RED gãy 3/3, nên skill Đạt ở `n = 3` trên ba kịch bản gốc. Cả chín lượt RED
chọn đúng hướng (C ở KB1 và KB3; B/C/A ở KB2) nhưng thiếu **hình dạng**: ở KB1 đều đề nghị đưa người dùng "tự quyết" khi tiền
kiểm là Không đạt; ở KB2 viết Unreleased theo giọng nội bộ và không có bảng từng tài liệu; ở KB3 trình menu bốn lựa chọn kèm
khuyến nghị thay vì đúng ba. Hai lượt GREEN chỉ Một phần: KB1 lượt 2 (tin người dùng mở đường "tự chấp nhận một điểm thiếu"
dù ô `risk: high` thiếu diễn tập) và KB2 lượt 3 (không có bảng tình trạng từng tài liệu; thêm chú thích HTML vào README); không
lượt nào vi phạm điều cấm. Độ nhạy của kết luận: nếu việc "đề nghị trình bản Không đạt để người dùng quyết" ở RED KB1 không bị
tính là thiếu, RED KB1 thành 3/3 Đạt (đạt sẵn) và skill vẫn Đạt theo đa số (KB2, KB3 gãy; GREEN 3/3).

Giới hạn của lần này: người chấm cùng họ mô hình với chủ thể (Đức chọn không gọi hãng khác, `CQ3`); không đo KB4–KB11 ở `n = 3`
(chỉ một lượt mỗi pha như mục TK9.2); kịch bản giả lập, chủ thể không chạy lệnh thật. Không sửa `SKILL.md`, không REFACTOR.

## Chạy lại

Prompt nguyên văn ở `tests/scenarios.txt`; RED thay `[PHA]` bằng dòng cấm công cụ Skill; GREEN thay bằng
dòng cấm công cụ Skill + đường **tuyệt đối** tới `SKILL.md` trong worktree (kịch bản 1 đọc thêm
`references/preflight.md`, kịch bản 2 `references/docs-sync.md`) + yêu cầu mở báo cáo bằng dòng "Đã đọc:
`<đường tuyệt đối>`". Cùng tier T3, cùng model; mỗi lượt một subagent mới; ghi `skill_sha` = băm cây
`skills/closing-sprint` trừ `tests/` (`git ls-tree <commit>:skills/<tên> | awk -F'\t' '$2!="tests"' | git mktree`),
id agent, ngày, và kết quả thật — không ghi "dự kiến".

Phép thay vế mở đầu ở lượt GREEN: phần mở đầu mỗi kịch bản trong `tests/scenarios.txt` nói "KHÔNG đọc file nào trên máy", mâu thuẫn với dòng GREEN bảo đọc `SKILL.md`; khi gửi GREEN đổi vế đó thành "KHÔNG đọc file nào trên máy, ngoài các file nêu ở dòng trên, các file trong `references/` mà `SKILL.md` trỏ tới và tài liệu `method/` mà `SKILL.md` trỏ tới"; dòng GREEN thêm "và tài liệu method/ được trỏ" sau "file references/ được trỏ". Lượt RED giữ nguyên văn; `tests/scenarios.txt` không đổi.
