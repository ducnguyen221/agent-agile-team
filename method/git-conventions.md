---
title: Git conventions - sprint branch, backup commit, undo table
type: method
updated: 2026-11-13
---

# Quy ước git — nhánh sprint, sao lưu, hoàn tác

> **Kết luận:** không còn hook chặn lệnh git. An toàn dựa vào ba thứ: làm trên nhánh sprint, commit sao lưu trước lệnh phá việc chưa commit, và bảng hoàn tác dưới đây. Luật của repo, máy hay CI chặt hơn thì luật đó thắng.

1. **Nhánh.** Mỗi sprint một nhánh `spr-NN/<tên>` trong worktree riêng ([skills/worktrees](../skills/worktrees/SKILL.md)). Không commit thẳng `main`. Vào `main` chỉ qua PR, sau Cổng 2 **Đạt** (Đạt có điều kiện thì không).
2. **Tag sao lưu.** Ngay trước khi gộp PR: `git tag backup/main-<YYYYMMDD-HHMM> main`. Không xoá tag này.
3. **Ba lệnh cấm** (gốc ở [AGENTS.md](../AGENTS.md)): không đẩy ép (`--force`, `+ref`); không `reset --hard`, `clean -fd`/`-fdx`, `checkout -- .`, `restore .` khi chưa sao lưu (mục 4); không xoá nhánh chưa gộp. **Cấm thêm — lệnh phá cơ chế hoàn tác** (bảng dưới sống nhờ reflog, nhánh và tag sao lưu): `git reflog expire`, `git gc --prune=now`, `git update-ref -d`, `git filter-branch`/`git filter-repo`, xoá tag hay nhánh `backup/*`, xoá `.git`, `git push --delete`/`+ref`, `git branch -D`. Hook chặn các lệnh này khi autopilot bật (`method/autopilot.md` mục 5.1); phần hook không bắt được (`filter-branch`, chuyển `.git` vào `.tmp/` rồi xoá) vẫn cấm bằng chữ.
4. **Sao lưu việc chưa commit** — một ref trần không đủ, file chưa theo dõi không vào ref. Làm đúng bốn lệnh: `git switch -c backup/<YYYYMMDD-HHMM>` → `git add -A` → `git commit -m "sao lưu"` → `git switch <nhánh làm>`. File bị `.gitignore` không vào bản sao lưu; `clean -fdx` xoá cả chúng nên không cứu được phần đó.

| Ca | Hoàn tác |
|---|---|
| Gộp nhầm vào `main` | `git revert -m 1 <sha gộp>` trên nhánh mới, rồi PR. Không `reset` `main` |
| Xoá nhầm nhánh | `git reflog` tìm sha ngọn nhánh, rồi `git branch <tên> <sha>` |
| `reset --hard` | đã commit: `git branch <tên-mới> <sha từ reflog>`; chưa commit: `git checkout backup/<…> -- .` |
| `clean -fdx` | `git checkout backup/<…> -- .` (trừ file bị ignore) |
| Phát hành lỗi | `git revert` commit lỗi, tag bản vá mới (không sửa tag cũ), cài lại bản trước theo lệnh ở REPORT |

**Giới hạn nói thẳng:** đẩy ép lên remote khi `main` chưa có ruleset chặn đẩy ép thì không cứu được bằng bảng này; tag `backup/main-…` chỉ giúp nếu máy còn bản chép cục bộ. Đặt ruleset cho `main` (cấm đẩy ép, cấm xoá, đòi PR) là việc một lần của chủ repo.
