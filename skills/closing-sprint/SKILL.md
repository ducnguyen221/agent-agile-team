---
name: closing-sprint
description: Use when verification has no open blocking findings and the sprint must be closed — preflight evidence check before gate 2, a version-bump proposal, then after the user's verdict updating living specs, the central ledger and docs, running every check lane on the tree to merge, and presenting the branch menu (merge only on green CI of the exact commit; push + PR; keep) without force-pushing or deleting work on your own.
metadata:
  group: process
  roles: [analyst, implementer]
source: ["obra/superpowers skills/finishing-a-development-branch/SKILL.md", "garrytan/gstack document-release/SKILL.md.tmpl (via local distill)", "concept: preflight evidence gate by size and risk (references/preflight.md, clean-room rewrite: old text removed first, new writer saw only a noun-phrase idea list; task `TK10` (clean-room rewrite), sprint `SPR-04` (method wave 3))", "affaan-m/ECC commands/learn-eval.md", "concept: release notes built from the sprint report, internal and external versions (references/release-notes.md, clean-room rewrite: old text removed first, new writer saw only a noun-phrase idea list; task `TK10` (clean-room rewrite), sprint `SPR-04` (method wave 3))", "garrytan/gstack ship/SKILL.md.tmpl and ship/sections tests, plan-completion, pr-body (ideas only: integrate base, check lanes, failure ownership, plan-versus-diff audit, PR body; automatic bump, changelog, commit, push and PR creation dropped; task `TK9` (verification and closing), sprint `SPR-04` (method wave 3))", "garrytan/gstack land-and-deploy/SKILL.md.tmpl (idea only: CI gate on the exact head commit)", "affaan-m/ECC commands/update-docs.md (references/docs-sync.md)", "affaan-m/ECC skills/living-docs-governance (idea only, via templates/registry/feature-spec.md; references/docs-sync.md)"]
source_sha: [8ca22dba9a94f28898bbce59f2537ff4d87c747d, 96764e80a641e28141ec8297223768029f5bf483, null, c70874fae9eb0e5ad0365beb7e2955899fd1d30f, null, f30b7b788a210d217ea3125bf3001b29cbc2a463, f30b7b788a210d217ea3125bf3001b29cbc2a463, ef648e01899ba3e8dc6371642deaaf64b4477775, ef648e01899ba3e8dc6371642deaaf64b4477775]
license: [MIT, MIT, none, MIT, none, MIT, MIT, MIT, MIT]  # none = idea-only sources of references/preflight.md and references/release-notes.md
rewrite_before_public: false  # both private-derived files were rewritten clean-room (writer saw only noun-phrase idea lists)
---

# Đóng sprint (Bước 5–6 và sau Cổng 2)

> **Kết luận:** đóng sprint đi đúng thứ tự **tiền kiểm bằng chứng → REPORT kèm đề xuất phiên bản → Cổng 2 →
> cập nhật hồ sơ và sổ → đồng bộ tài liệu → bài học → kiểm cây sắp gộp → menu nhánh**. Menu có đúng **ba**
> lựa chọn (gộp local / push + PR / giữ nguyên), trình **sau** Cổng 2, không có "bỏ". **Gộp** chỉ khi CI của
> **đúng commit** xanh hoặc người dùng duyệt rõ commit đó; push và PR là tác động ra ngoài — người dùng gật mới
> làm; không bao giờ `--force`, không tự ghi số phiên bản, không tự xoá việc.

## 1. Trình tự

| # | Việc | Ai | Chi tiết |
|---|---|---|---|
| 1 | **Tiền kiểm** — bằng chứng đủ chưa, theo cỡ và rủi ro | Analyst | [references/preflight.md](references/preflight.md) |
| 2 | **REPORT** theo mẫu; mỗi `CO` ghi luôn thành một dòng `RQ-` `mới` trong REQUESTS (tóm tắt ghi `từ SPR-xx/COn`, cột Đề xuất của REPORT ghi mã `RQ-`); trình **Cổng 2** bằng lời trình chuẩn, kèm dòng **đề xuất phiên bản** (mục 1.1) | Analyst | `method/process.md` mục 7 |
| 3 | Người dùng kết luận **Đạt / Đạt có điều kiện / Không đạt** → ghi `gate_2`, `gate_2_at`, `gate_2_quote` nguyên văn | — | Không đạt → vòng mới hoặc sprint mới; dừng ở đây |
| 4 | **Cập nhật hồ sơ:** spec sống `FS-` (gộp delta Thêm / Sửa / Bỏ của SPEC theo comment đầu mẫu `feature-spec.md`; hành vi hiện hành, tiêu chí đang giữ, giới hạn đã biết, lịch sử sprint) · SPRINTS cột Đóng · REQUESTS trạng thái `xong` · spec sống `status` · chạy công cụ `index` · **dòng sổ tập trung** (mục 1.2) | Analyst | chỉ sau Cổng 2 Đạt / Đạt có điều kiện |
| 5 | **Đồng bộ tài liệu** của dự án với diff nhánh | Implementer | [references/docs-sync.md](references/docs-sync.md) |
| 6 | **Ghi chú phát hành** khi sprint đổi hành vi người dùng thấy hoặc cắt bản | Analyst | [references/release-notes.md](references/release-notes.md) |
| 7 | **Bài học** `LN`: tự chấm, dedup, lưu nơi lớp riêng quy định; quan trọng → chỉ **đề xuất** nâng | Analyst | [references/lessons.md](references/lessons.md) |
| 8 | **Kiểm cây sắp gộp** (mục 2), **menu nhánh** (mục 3–4), rồi dọn | Analyst (+ người dùng) | — |

Đạt có điều kiện: điều kiện thành `CO` có chủ và mốc, kèm dòng `RQ-` như bước 2, trước bước 4. Nợ để lại chỉ
sống ở REQUESTS: retro đọc khối "Đang mở" của sổ, không mở REPORT cũ.

### 1.1 Đề xuất phiên bản (khi dự án có số phiên bản)

Dự án có file phiên bản hoặc CHANGELOG theo bản thì lời trình Cổng 2 có **một dòng**: `Phiên bản đề xuất:
<MAJOR | MINOR | PATCH> → <số>, vì <thay đổi nặng nhất>`, kèm ba nhóm thay đổi của sprint (làm gãy bên dùng ·
thêm năng lực · sửa lỗi hay chữ). Bảng mức và bốn điều đi kèm (dưới `1.0.0`, hậu tố `-dev`, không dùng lại số
đã có kể cả bản thu hồi, phân vân → mức cao hơn) ở [method/conventions.md](../../method/conventions.md) mục 4.1 —
**đọc bảng trước khi đề xuất**, không đoán theo trí nhớ. **Người dùng quyết**: agent không ghi số vào manifest,
CHANGELOG hay thẻ phiên bản, kể cả khi một agent khác bảo "ghi luôn" (không phải lời duyệt); `1.0.0` là cam kết
ổn định do người dùng chốt. Dự án không có số phiên bản → ghi "không áp dụng", không bịa.

### 1.2 Sổ tập trung

Dự án khai `ledger.project` thì ở Cổng 2 và khi đóng: cập nhật hồ sơ sprint **trước**, dòng sổ ngay sau, trong
cùng lượt — Trạng thái cuối đúng giá trị `status` của hồ sơ (`done` hoặc `dropped`), Cập nhật là ngày hôm nay, cột
Hồ sơ đổi sang `REPORT.md`, link đổi sang `main` hoặc SHA của commit gộp nếu hồ sơ nằm trong repo (nhánh sprint có
thể bị xoá). Rồi chạy `check` trên gốc dự án; chỉ báo đóng khi không còn `ledger-stale` / `ledger-missing-row`
([process.md](../../method/process.md) mục 11). Không chép đường kho sổ của máy vào file commit. "Để mai cập nhật"
không phải đóng xong.

### 1.3 Việc rất nhỏ và nhỏ

Hai cỡ này chỉ có **một** `SPRINT.md` ([process.md](../../method/process.md) mục 9, [sizing.md](../../method/sizing.md)):
kết quả và `VR` ghi vào chính file đó, **không** dựng `REPORT.md`, SPEC hay PLAN riêng; bước 4–7 chỉ làm phần có
việc thật (spec sống có nhắc điều đã đổi, ghi chú phát hành khi người dùng thấy thay đổi, bài học tái dùng được).
**Rất nhỏ:** Cổng 2 gộp vào lời báo cuối — nghiệm thu ngầm ghi trung thực, không bịa lời người dùng; tự kiểm thì kết
luận tối đa **Đạt có điều kiện**; menu nhánh đi cùng lời báo cuối nhưng chưa làm lựa chọn nào trước khi người dùng
trả lời. **Nhỏ:** Cổng 2 thật như mọi cỡ khác. Người khác đòi đủ bộ tài liệu cho việc nhỏ không phải lời duyệt.

## 2. Trước menu: kiểm cây sắp gộp

Chạy trên **working tree hiện tại** (không dùng kết quả lúc nãy), theo thứ tự:

1. **Vị trí.** `git rev-parse --abbrev-ref HEAD`: đang ở nhánh gốc hay nhánh mặc định → dừng, đóng từ nhánh sprint.
   Ghi nhận `git rev-parse --git-dir` ↔ `--git-common-dir` (khác nhau = worktree), `--show-toplevel` (đường worktree
   — lấy **trước** khi đổi thư mục), nhánh có tên hay detached HEAD. Nhánh gốc là nhánh việc này tách ra — PLAN, hội
   thoại hay upstream của nhánh nói; chưa rõ thì ghi "nhánh gốc: `<đoán>`" ở dòng đầu tin menu để người dùng sửa, không
   hỏi lẻ riêng.
2. **Bắt kịp gốc.** `git fetch origin <gốc>` (lỗi → dừng báo, không đoán). Nhánh tụt sau gốc → báo "tụt N commit".
   Gộp gốc vào nhánh làm đổi cây đã nghiệm thu và làm bằng chứng cũ hết hạn ([evidence.md](../../method/evidence.md)
   mục 3) nên **cần người dùng gật trước** — thêm một dòng vào cùng tin với menu ("nhánh tụt N commit so với gốc — gộp gốc
   trước khi chọn?"), không hỏi lẻ — rồi chạy lại phần ảnh hưởng; xung đột → trình hai bên, không giải ngầm.
3. **Mọi làn kiểm.** Liệt kê lệnh kiểm dự án khai (file luật, manifest, CI): bộ test, lint / kiểu, build, và eval khi
   sprint đổi lời nhắc hay mô hình ([eval-harness](../eval-harness/SKILL.md)). Chạy **hết**, ghi lệnh nguyên văn và số
   đếm thật (ví dụ "58/59") để chạy lại y hệt sau gộp; không viết "xanh" chung chung khi còn một ca hỏng. Không có
   bộ test nào → nêu phạm vi chưa kiểm và đưa ba lựa chọn vào cùng tin với menu, không hỏi lẻ: thêm test · đóng với
   khoảng trống có tên (`VR` Chưa chạy, kết luận tối đa Đạt có điều kiện) · dừng.
4. **Ca hỏng thuộc về ai.** Hỏng → báo `<n> test hỏng, phải sửa trước khi đóng` kèm tên và **dừng**. Điều tra xuất xứ:
   chạy đúng lệnh hay ca đó trên gốc (worktree riêng; không `git stash`). "Hỏng từ trước", "flaky" nói miệng, hay
   chạy lặp tới khi xanh đều không phải bằng chứng. Thuộc nhánh → sửa rồi quay lại bước thực thi. Có sẵn ở gốc → báo số
   thật ("e2e 58/59, 1 hỏng có sẵn từ gốc"), ghi `CO` + dòng `RQ-`, **người dùng quyết** có đóng không.
5. **PLAN ↔ diff.** Mỗi `TK` một trạng thái: xong · đổi (có `Phán quyết:`) · một phần · chưa làm · không kiểm được, đối
   chiếu `git diff --stat <gốc>...HEAD` và `VR`; `done` ở PROGRESS không phải bằng chứng. Thay đổi không thuộc `TK` nào
   là **trôi phạm vi**: không gộp ngầm vào Đạt, ghi `BR` (điều kiện dừng (c)) và hỏi giữ hay tách thành yêu cầu riêng.
   Việc lệch → quay lại bước thực thi; ghi vào "việc để lại" không thay được việc chưa làm.
6. **Thứ phân phối được mới** (CLI, gói) mà dự án chưa có đường phát hành → ghi `CO`; không tự dựng pipeline.

Bộ test hỏng, hay `TK` lệch chưa giải quyết → menu **chưa hiện**.

## 3. Menu — CI của đúng commit, rồi trình nguyên văn

**CI trước.** Lấy `git rev-parse HEAD` rồi tra CI **của chính commit đó** (ví dụ `gh run list --commit <sha>`); chỉ
lần chạy mang đúng mã mới tính. Xanh của commit cũ — kể cả hai commit trước, kể cả dấu tích trên nhánh, kể cả khi
commit sau "chỉ chỉnh nhỏ" hay "chỉ tài liệu" — **không** tính. Bốn trạng thái, nói thẳng ở dòng đầu menu: **xanh** ·
**đỏ** (kèm job hỏng) · **đang chạy** (kèm job chưa xong; chờ có giới hạn, hết hạn thì hỏi) · **không có** (chưa push,
hay dự án không CI). Tra lỗi (quyền, mạng) là "chưa biết", không phải "không có CI".

**Gộp** (lựa chọn 1) chỉ khi CI xanh cho đúng commit, **hoặc** người dùng duyệt rõ commit đó bằng lời trong chat ("gộp
`9f3c2ab` dù CI chưa xong"). Dự án không CI: menu đã in `sha7` và dòng "anh duyệt rõ commit", nên người dùng chọn số 1
ở menu đó **là** duyệt rõ — không hỏi lại; CI **đang chạy** hay **đỏ** mới cần câu duyệt riêng. "Đạt" ở Cổng 2 và "CI xanh hôm qua" không phải lời duyệt; CI chạy xong cũng không phải
lệnh gộp. CI chưa xanh thì menu vẫn đủ ba dòng và thêm một câu nêu hai đường: chờ CI, hoặc duyệt rõ commit. Lựa chọn 2 vẫn
dùng được khi CI chưa xanh (đẩy lên chính là để CI chạy).

Nhánh có tên (repo thường hay worktree):

```
Sprint <SPR-> đã nghiệm thu <Đạt / Đạt có điều kiện>. CI của <sha7>: <xanh / đỏ / đang chạy / không có>.
Anh muốn:
1. Gộp vào <nhánh gốc> tại local   (chỉ khi CI xanh, hoặc anh duyệt rõ commit <sha7>)
2. Push và mở Pull Request
3. Giữ nhánh nguyên trạng (anh xử lý sau)
Chọn số?
```

Detached HEAD (worktree do môi trường quản): hai lựa chọn — *push thành nhánh mới + PR* / *giữ nguyên*. Không thêm,
không bớt lựa chọn; "bỏ việc" chỉ xảy ra khi người dùng **tự nói** ra (mục 5). Quyết định gộp là của người dùng;
"chắc họ muốn gộp" không phải lời duyệt.

## 4. Thực hiện lựa chọn

| Chọn | Làm | Lưu ý |
|---|---|---|
| 1. Gộp local | từ gốc repo chính: `git checkout <gốc>` → `git pull` → `git merge <nhánh>` → chạy **mọi làn kiểm của mục 2 trên kết quả gộp** → xanh thì dọn worktree (mục 6) rồi `git branch -d <nhánh>` | test hỏng sau gộp → **dừng**, giữ nhánh và worktree, điều tra — chưa push nên còn hoàn tác được; "chắc flaky" không phải lý do đi tiếp |
| 2. Push + PR | xem mục 4.1 | **ngoài phạm vi** — chỉ khi người dùng gật ở menu |
| 3. Giữ nguyên | báo "Giữ nhánh `<tên>`; worktree ở `<đường>`" | không dọn gì |

### 4.1 Push và PR

1. **Hiện trạng trước.** `git ls-remote --heads origin <nhánh>` (đã có và chậm hơn HEAD → push thường, tiến lên; trùng
   HEAD → bỏ qua push) và PR đang mở của nhánh (`gh pr list --head <nhánh> --state open`). Đã có PR → **cập nhật**
   tiêu đề và thân PR đó, không tạo trùng, không đóng PR cũ khi chưa được bảo. Tra lỗi hay nhiều PR khớp → dừng hỏi.
2. **Push.** `git push -u origin <nhánh>` (detached: `git push origin HEAD:refs/heads/<tên mới>`). **Không `--no-verify`,
   không `--force`.** Hook chặn vì quét khoá: mở dòng bị báo ở `file:dòng`, báo loại (mẫu hay khoá thật), **không in
   giá trị**; khoá thật → Chặn, báo để xoay vòng; mẫu → vá được (giá trị làm mờ hay biến môi trường) nhưng commit vá
   đổi HEAD. Remote đã đổi (từ chối không tiến lên được) → fetch, xem. Hễ HEAD khác sha đã nghiệm thu ở Cổng 2 (commit
   vá hay gộp remote) → **dừng, chưa push**: báo sha mới và diff so với sha đã nghiệm thu, chạy lại mọi làn kiểm trên
   sha mới (`VR` cũ hết hạn — [evidence.md](../../method/evidence.md) mục 3), không viết lại lịch sử; chỉ push khi
   người dùng duyệt rõ sha mới bằng lời trong chat, như mục 3 đòi cho gộp. Xác thực hay mạng hỏng → sửa nguyên nhân rồi
   thử lại.
3. **Thân PR** viết từ REPORT: tóm tắt **theo chủ đề** (không dán danh sách commit) · kết quả kiểm (lệnh và số đếm thật;
   `VR` Chưa chạy nói rõ) · phát hiện còn mở và việc để lại (`CO`, `RQ-`) · tài liệu đã đồng bộ · cách hoàn tác. Nối
   issue: `Closes #N` chỉ khi **mọi** tiêu chí của issue đã xong và đã kiểm; còn phần hoãn hay dở → `Linked to #N` hay
   `Refs #N` kèm nêu phần còn lại. Tiêu đề không mang số phiên bản khi người dùng chưa quyết số. Đọc lại thân và tiêu đề
   trước khi gửi: không secret, không đường máy, không PII (PR có thể công khai). Báo URL; giữ worktree để sửa theo phản hồi.

## 5. Người dùng yêu cầu bỏ việc

Chỉ khi họ nói rõ. Xác nhận trước, liệt kê thứ mất vĩnh viễn (nhánh, danh sách commit, worktree) và
yêu cầu gõ đúng từ **`bỏ`**; "ừ, dẹp đi" không tính. Nhận đúng từ → về gốc repo chính, dọn worktree
(mục 6), `git branch -D <nhánh>`. Đây là điều kiện dừng (a) — ghi `BR` nếu lời yêu cầu không rõ.

## 6. Dọn worktree theo nguồn gốc

- `git-dir == git-common-dir` → repo thường, không có gì dọn.
- Worktree do repo tạo (nằm dưới thư mục worktree của dự án, trong `.gitignore`) → `git worktree remove
  <đường>` rồi `git worktree prune`. Bị từ chối ("có file chưa commit") → file đó **chỉ tồn tại ở
  đó**: không `--force`; `git -C <đường> status --porcelain -uall`, trình ba lựa chọn (commit vào nhánh
  / chuyển về repo chính / xoá — không hoàn tác được) rồi mới dọn.
- Worktree do harness/môi trường quản → để nguyên; harness có công cụ thoát worktree thì dùng.
- Worktree khác trông cũ → **không đụng**; chỉ dọn cái của sprint này.
- Xoá `.tmp/` của sprint. Hồ sơ sprint (SPEC/PLAN/PROGRESS/REPORT) giữ.

## 7. Cờ đỏ

| Ý nghĩ | Thực tế |
|---|---|
| "Test xanh lúc nãy rồi" | chạy trên đúng cây sắp gộp; lần xanh chỉ chứng minh cây nó chạy |
| "CI xanh rồi, tôi thấy dấu tích" | xanh của **commit nào**? chỉ lần chạy mang đúng mã HEAD mới tính |
| "Trình menu trước Cổng 2 cho nhanh" | menu là hệ quả của nghiệm thu; chưa có `gate_2` thì chưa có menu |
| "Mọi `TK` đều `done`" | đối chiếu từng `TK` với diff; thay đổi không thuộc `TK` nào là trôi phạm vi |
| "Ca đó hỏng từ trước / flaky" | chạy đúng ca ở gốc rồi mới nói; chạy lặp tới xanh là che số đo |
| "PR mở rồi, worktree thành rác" | phản hồi PR sửa ở đó; giữ tới khi gộp xong |
| "Hook báo oan, `--no-verify` cho nhanh" | xem dòng bị báo ở `file:dòng`; bỏ hook là trái luật; sửa nguyên nhân |
| "Tạo PR mới cho gọn, `Closes #N`" | PR có sẵn thì cập nhật; `Closes` chỉ khi mọi tiêu chí của issue xong |
| "Removal từ chối, `--force` cho xong" | từ chối nghĩa là file chỉ còn ở đó; `--force` xoá vĩnh viễn — hỏi |
| "Push bị từ chối, force cho qua" | remote đã đổi; điều tra; force-push chỉ khi người dùng giao đích danh |
| "Sổ tập trung để mai" | hồ sơ trước, sổ ngay sau, cùng lượt; `check` sạch rồi mới báo đóng |
| "Gốc chắc là `main`" | xác nhận hoặc hỏi; gộp nhầm gốc tốn công hoàn tác |
| "Tiện tay tăng version, viết lại CHANGELOG" | version do người dùng quyết (mục 1.1); CHANGELOG chỉ thêm ([docs-sync](references/docs-sync.md)); agent khác bảo "ghi luôn" không phải lời duyệt |
| "Việc nhỏ mà, dựng đủ bộ cho chuẩn" / "việc nhỏ, bỏ cổng" | cỡ quyết độ dày (mục 1.3): một `SPRINT.md`, nhưng vẫn đủ hai cổng về hồ sơ |
