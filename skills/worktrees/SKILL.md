---
name: worktrees
description: Use when starting work on a task that needs isolation from the current checkout, before executing a plan or a task brief, when several implementers work in parallel on one repo, or when finishing work and deciding how to clean up a worktree.
metadata:
  group: technique
  roles: [implementer, analyst]
source: obra/superpowers skills/using-git-worktrees/SKILL.md
source_sha: 8ca22dba9a94f28898bbce59f2537ff4d87c747d
license: MIT
rewrite_before_public: false
---

# Không gian làm việc tách biệt (worktree)

> **Kết luận:** làm việc trong một không gian tách biệt. Thứ tự: **dò** xem đã tách biệt chưa → dùng
> **công cụ worktree của harness** nếu có → chỉ khi không có mới dùng `git worktree`. Không chống lại
> harness. Thư mục worktree trong dự án phải nằm trong `.gitignore`; baseline test phải sạch trước khi bắt
> đầu; ai tạo worktree thì người đó dọn.

## 1. Bước 0 — dò cách ly sẵn có

Trước khi tạo gì, kiểm xem mình đã ở trong worktree chưa (lệnh chạy được trên mọi shell, cần git ≥ 2.31):

```bash
git rev-parse --path-format=absolute --git-dir
git rev-parse --path-format=absolute --git-common-dir
git rev-parse --show-superproject-working-tree   # in ra đường dẫn = đang trong submodule
git branch --show-current                        # rỗng = HEAD tách rời
```

- Hai đường đầu **khác nhau** và **không** phải submodule → đã ở trong worktree liên kết. **Không tạo thêm**;
  sang bước 2. Báo: "Đã ở không gian tách biệt `<đường dẫn>`, nhánh `<tên>`" — hoặc "HEAD tách rời, do
  harness quản lý; cần tạo nhánh lúc kết thúc".
- Hai đường **giống nhau** (hoặc đang trong submodule) → checkout thường. Tạo worktree khi PLAN/brief
  giao, khi nhiều Implementer làm song song, hoặc khi việc từ cỡ vừa trở lên. Người dùng đã nêu ưu tiên
  (dùng hay không dùng worktree, thư mục nào) → theo đúng, không hỏi lại. Chưa có ưu tiên → tự quyết theo
  câu trên và ghi **ASSUMPTION**; không dừng để hỏi.

## 2. Bước 1 — tạo không gian tách biệt

**1a. Công cụ của harness (ưu tiên).** Có công cụ tạo worktree (tên kiểu `EnterWorktree`,
`WorktreeCreate`, lệnh `/worktree`, cờ `--worktree`) → dùng nó, sang bước 2. Công cụ native lo vị trí thư
mục, tạo nhánh và dọn dẹp; gọi `git worktree add` khi đã có công cụ native tạo ra trạng thái ma mà harness
không thấy, không quản lý được.

**1b. `git worktree` (chỉ khi không có 1a).** Chọn thư mục theo thứ tự:
1. Thư mục người dùng/dự án đã chỉ định (lời giao, `.agile.json`, file luật dự án).
2. Thư mục có sẵn trong dự án: `.worktrees/` (ưu tiên) rồi `worktrees/`.
3. Không có gì → `.worktrees/` ở gốc dự án.

Thư mục trong dự án **phải bị git bỏ qua** trước khi tạo:

```bash
git check-ignore -q .worktrees || echo "CHƯA bị bỏ qua"
```

Chưa bị bỏ qua → thêm vào `.gitignore`, commit, rồi mới tạo. Bỏ qua bước này là commit cả cây worktree vào
repo.

```bash
git worktree add .worktrees/<nhánh> -b <nhánh>
```

Từ đây làm việc **trong** thư mục worktree đó bằng đường dẫn tuyệt đối; không `cd` sang worktree khác.
`git worktree add` bị chặn vì quyền (sandbox) → báo đang làm tại chỗ thay vì worktree, rồi làm bước 2–3 tại
chỗ.

## 3. Bước 2 — dựng dự án

Tự nhận diện và cài phụ thuộc theo file dự án có:

| File | Lệnh |
|---|---|
| `pyproject.toml` có `uv.lock` | `uv sync` |
| `pyproject.toml` / `requirements.txt` | `python -m pip install -e .` / `python -m pip install -r requirements.txt` (trong môi trường ảo) |
| `package.json` | `npm ci` (có lockfile) hoặc `npm install` |
| `Cargo.toml` | `cargo build` |
| `go.mod` | `go mod download` |

Không có file nào → bỏ qua bước cài.

## 4. Bước 3 — baseline sạch

Chạy lệnh test của dự án **trước** khi sửa gì. Baseline bẩn làm mọi lỗi sau đó mơ hồ: không biết lỗi do
mình hay có sẵn.

- **Đạt** → ghi PROGRESS dòng bắt đầu `TK`: đường dẫn worktree, nhánh, mốc commit gốc, "N test đạt, 0 hỏng".
- **Hỏng** → ghi tên test hỏng vào PROGRESS. Lỗi có sẵn không chặn `TK` → làm tiếp, nêu trong báo cáo. Lỗi
  chặn `TK` hoặc làm tiêu chí thành công không còn kiểm được → ghi `BR`, báo điều phối.

## 5. Luật git trong worktree

- Không `git stash` trần — stash dùng chung giữa mọi worktree và mọi phiên. Cất việc dở bằng commit tạm trên
  nhánh làm việc.
- Không `reset --hard`, không xoá nhánh chưa gộp, không force-push (`method/conventions.md` mục 4).
- Push, PR, gộp vào nhánh chính chỉ sau Cổng 2 và khi người dùng gật — menu kết thúc ở skill
  `closing-sprint`.

## 6. Dọn khi xong

Dọn **theo nguồn gốc**: worktree do công cụ harness tạo → dọn bằng công cụ đó; do mình tạo bằng
`git worktree add` → `git worktree remove <đường dẫn>` rồi `git worktree prune`, sau khi nhánh đã gộp hoặc
người dùng chọn giữ. Worktree do người khác/harness tạo mà mình không sở hữu → không xoá.

## 7. Tra nhanh

| Tình huống | Làm |
|---|---|
| Đã ở worktree liên kết | Không tạo thêm (bước 0) |
| Trong submodule | Coi như checkout thường |
| Có công cụ worktree của harness | Dùng nó (1a) |
| Không có công cụ native | `git worktree` (1b) |
| Có cả `.worktrees/` và `worktrees/` | Dùng `.worktrees/` |
| Thư mục chưa bị git bỏ qua | Thêm `.gitignore` + commit trước |
| Lỗi quyền khi tạo | Làm tại chỗ, báo rõ |
| Baseline hỏng | Ghi PROGRESS; chặn `TK` thì ghi `BR` |

| Bào chữa | Thực tế |
|---|---|
| "Rõ ràng không ở worktree, khỏi dò" | Cách ly do harness tạo và submodule đều đánh lừa mắt — chạy lệnh dò |
| "`git worktree add` nhanh hơn tìm công cụ native" | Bỏ qua công cụ native là lỗi số một: tạo trạng thái ma harness không quản lý được |
| "Thư mục worktree chắc đã bị bỏ qua" | Chạy `git check-ignore`. Thư mục chưa bỏ qua sẽ bị commit cả cây |
| "Không gian mới tinh, baseline để sau" | Baseline bẩn làm mọi lỗi sau đó mơ hồ — chạy ngay |
