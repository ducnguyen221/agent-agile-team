---
name: closing-sprint
description: Use when verification has no open blocking findings and the sprint must be closed — running the preflight evidence check before gate 2, then after the user's verdict updating living specs and registries, syncing docs, drafting release notes, recording lessons, and presenting the branch menu (merge locally / push + PR / keep) without ever force-pushing or deleting work on your own.
metadata:
  group: process
  roles: [analyst, implementer]
source: ["obra/superpowers skills/finishing-a-development-branch/SKILL.md", "garrytan/gstack document-release/SKILL.md.tmpl (via local distill)", "academy skills/preflight-gate/SKILL.md, skills/release-notes-writer/SKILL.md (private copy)", "affaan-m/ECC commands/learn-eval.md"]
source_sha: [8ca22dba9a94f28898bbce59f2537ff4d87c747d, 96764e80a641e28141ec8297223768029f5bf483, 4c0fdc5736a49b6223a7dfc7626d5495cf55185c, c70874fae9eb0e5ad0365beb7e2955899fd1d30f]
license: [MIT, MIT, none, MIT]  # none = references/preflight.md, references/release-notes.md
rewrite_before_public: true  # only references/preflight.md and references/release-notes.md derive from the source without a license
---

# Đóng sprint (Bước 5–6 và sau Cổng 2)

> **Kết luận:** đóng sprint đi đúng thứ tự **tiền kiểm bằng chứng → REPORT → Cổng 2 → cập nhật hồ
> sơ → đồng bộ tài liệu → bài học → menu nhánh**. Menu có đúng **ba** lựa chọn (gộp local / push + PR
> / giữ nguyên), trình **sau** Cổng 2, không có "bỏ"; push và PR là tác động ra ngoài — người dùng
> gật mới làm; không bao giờ `--force`, không bao giờ tự xoá việc.

## 1. Trình tự

| # | Việc | Ai | Chi tiết |
|---|---|---|---|
| 1 | **Tiền kiểm** — bằng chứng đủ chưa, theo cỡ và rủi ro | Analyst | [references/preflight.md](references/preflight.md) |
| 2 | **REPORT** theo mẫu; mỗi `CO` ghi luôn thành một dòng `RQ-` `mới` trong REQUESTS (tóm tắt ghi `từ SPR-xx/COn`, cột Đề xuất của REPORT ghi mã `RQ-`); trình **Cổng 2** bằng lời trình chuẩn | Analyst | `method/process.md` mục 7 |
| 3 | Người dùng kết luận **Đạt / Đạt có điều kiện / Không đạt** → ghi `gate_2`, `gate_2_at`, `gate_2_quote` nguyên văn | — | Không đạt → vòng mới hoặc sprint mới; dừng ở đây |
| 4 | **Cập nhật hồ sơ:** spec sống `FS-` (gộp delta Thêm / Sửa / Bỏ của SPEC theo comment đầu mẫu `feature-spec.md`; hành vi hiện hành, tiêu chí đang giữ, giới hạn đã biết, lịch sử sprint) · SPRINTS cột Đóng · REQUESTS trạng thái `xong` · spec sống `status` · chạy công cụ `index` | Analyst | chỉ sau Cổng 2 Đạt / Đạt có điều kiện |
| 5 | **Đồng bộ tài liệu** của dự án với diff nhánh | Implementer | [references/docs-sync.md](references/docs-sync.md) |
| 6 | **Ghi chú phát hành** khi sprint đổi hành vi người dùng thấy hoặc cắt bản | Analyst | [references/release-notes.md](references/release-notes.md) |
| 7 | **Bài học** `LN`: tự chấm, dedup, lưu nơi lớp riêng quy định; quan trọng → chỉ **đề xuất** nâng | Analyst | [references/lessons.md](references/lessons.md) |
| 8 | **Menu nhánh** (mục 2–4) rồi dọn | Analyst (+ người dùng) | — |

Đạt có điều kiện: điều kiện thành `CO` có chủ và mốc, kèm dòng `RQ-` như bước 2, trước bước 4. Nợ để lại chỉ
sống ở REQUESTS: retro đọc khối "Đang mở" của sổ, không mở REPORT cũ.

## 2. Trước menu: test cả bộ trên đúng cây sắp gộp

Chạy bộ test đầy đủ của dự án trên working tree hiện tại (không phải kết quả lúc nãy). Hỏng → báo
`<n> test hỏng, phải sửa trước khi đóng` kèm tên, **dừng** — menu chỉ hiện sau bộ xanh. Đồng thời ghi
nhận trạng thái git: `git rev-parse --git-dir` ↔ `--git-common-dir` (khác nhau = đang ở worktree),
`git rev-parse --show-toplevel` (đường worktree — lấy **trước** khi đổi thư mục), nhánh có tên hay
detached HEAD. Nhánh gốc là nhánh việc này tách ra — PLAN, hội thoại, hay upstream của nhánh nói;
chưa rõ thì hỏi một câu "nhánh này tách từ `<đoán>`, đúng không?" — gộp nhầm gốc tốn công hoàn tác.

## 3. Menu — trình nguyên văn, chờ trả lời

Nhánh có tên (repo thường hay worktree):

```
Sprint <SPR-> đã nghiệm thu <Đạt / Đạt có điều kiện>. Anh muốn:
1. Gộp vào <nhánh gốc> tại local
2. Push và mở Pull Request
3. Giữ nhánh nguyên trạng (anh xử lý sau)
Chọn số?
```

Detached HEAD (worktree do môi trường quản): hai lựa chọn — *push thành nhánh mới + PR* / *giữ
nguyên*. Không thêm, không bớt lựa chọn; "bỏ việc" chỉ xảy ra khi người dùng **tự nói** ra (mục 5).
Quyết định gộp là của người dùng; "chắc họ muốn gộp" không phải lời duyệt.

## 4. Thực hiện lựa chọn

| Chọn | Làm | Lưu ý |
|---|---|---|
| 1. Gộp local | từ gốc repo chính: `git checkout <gốc>` → `git pull` → `git merge <nhánh>` → chạy **cả bộ test trên kết quả gộp** → xanh thì dọn worktree (mục 6) rồi `git branch -d <nhánh>` | test hỏng sau gộp → **dừng**, giữ nhánh và worktree, điều tra — chưa push nên còn hoàn tác được; "chắc flaky" không phải lý do đi tiếp |
| 2. Push + PR | `git push -u origin <nhánh>` (detached: `git push origin HEAD:refs/heads/<tên mới>`) → tạo PR vào `<gốc>` bằng CLI của forge hoặc URL forge in ra, theo mẫu PR của repo; báo URL | **ngoài phạm vi** — chỉ khi người dùng gật ở menu; push bị từ chối = remote đã đổi → điều tra, **không** force-push; giữ worktree để sửa theo phản hồi PR |
| 3. Giữ nguyên | báo "Giữ nhánh `<tên>`; worktree ở `<đường>`" | không dọn gì |

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
| "Trình menu trước Cổng 2 cho nhanh" | menu là hệ quả của nghiệm thu; chưa có `gate_2` thì chưa có menu |
| "PR mở rồi, worktree thành rác" | phản hồi PR sửa ở đó; giữ tới khi gộp xong |
| "Removal từ chối, `--force` cho xong" | từ chối nghĩa là file chỉ còn ở đó; `--force` xoá vĩnh viễn — hỏi |
| "Push bị từ chối, force cho qua" | remote đã đổi; điều tra; force-push chỉ khi người dùng giao đích danh |
| "Gốc chắc là `main`" | xác nhận hoặc hỏi; gộp nhầm gốc tốn công hoàn tác |
| "Tiện tay tăng version, viết lại CHANGELOG" | version do người dùng quyết; CHANGELOG chỉ thêm ([docs-sync](references/docs-sync.md)) |
