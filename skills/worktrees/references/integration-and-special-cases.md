# Gộp nhánh task, tạo từ tag, submodule và LFS, xem PR

> **Kết luận:** hai worktree sửa cùng một file không bị git cản — xung đột chỉ lộ lúc **gộp**; nhánh tích hợp gộp từng
> nhánh task theo thứ tự có kiểm test giữa các lần. Worktree từ tag dùng `<commit-ish>` ở cuối lệnh `add`. Worktree mới
> **không** khởi tạo submodule và mỗi worktree kéo LFS thành file thật riêng. Xem PR để đọc thì dùng `--detach`: gỡ xong
> không để lại nhánh cục bộ. Gộp vào nhánh chính vẫn chỉ sau Cổng 2 và khi người dùng gật (`SKILL.md` mục 5).

## 1. Hai worktree cùng sửa một file; gộp các nhánh task vào nhánh tích hợp

Mỗi worktree có index và cây làm việc riêng, nên hai worktree sửa cùng `shared.txt` trên hai nhánh khác nhau **không báo
gì** — kể cả khi chạy song song. Xung đột hiện ra lúc gộp (đã chạy thử: gộp nhánh thứ hai báo `CONFLICT (content)`, file ở
trạng thái `UU`).

**Phòng trước (rẻ nhất):** chia phạm vi file không giao nhau khi giao việc (`SKILL.md` mục 2). Biết trước hai việc phải chạm
cùng file → xếp **tuần tự**: việc thứ hai tạo worktree sau khi việc thứ nhất đã gộp, hoặc cập nhật nhánh từ nhánh tích hợp
trước khi làm tiếp.

**Gộp nhánh task vào nhánh tích hợp.** Nhánh tích hợp chỉ checkout được ở **một** worktree: gộp ở worktree đang giữ nó
(thường là worktree của điều phối), không ở worktree của task.

```bash
git -C <worktree-tích-hợp> merge --no-ff task/one -m "Gộp task/one"   # một nhánh một lần
# chạy test của dự án; xanh mới gộp nhánh kế
git -C <worktree-tích-hợp> merge --no-ff task/two -m "Gộp task/two"
```

- **Thứ tự:** theo phụ thuộc (việc nền trước, việc dựa trên nó sau); ngang hàng thì việc đụng ít file chung gộp trước.
  **Chạy test sau mỗi lần gộp**, không gộp hết rồi mới chạy — xung đột về hành vi (không về chữ) chỉ lộ ở test.
- **Gặp xung đột:** `git diff --name-only --diff-filter=U` liệt kê file xung đột; sửa tay, `git add <file>`, `git commit`.
  Chưa muốn xử lý ngay: `git merge --abort` trả nhánh tích hợp về trạng thái trước lần gộp (đã chạy thử, cây sạch lại).
  Người xử lý là người sở hữu nhánh **gộp sau**, vì biết ý định của mình; xung đột về ý định giữa hai việc (không chỉ
  về chữ) → dừng, ghi `BR`, báo điều phối thay vì chọn bên thắng.
- **Merge hay rebase:** gộp bằng `merge --no-ff` giữ nguyên lịch sử từng nhánh task và dễ truy ngược việc; muốn lịch sử
  thẳng thì **rebase nhánh task lên nhánh tích hợp ngay trong worktree của nó** rồi mới gộp (`git rebase sprint/int` — xung
  đột hiện từng commit; `git rebase --abort` bỏ cuộc về như cũ). Chỉ rebase nhánh **chưa đẩy và chưa ai dùng chung**; đã
  đẩy hay đã có người khác nhận thì gộp nhánh tích hợp vào nhánh task thay vì viết lại lịch sử. Rebase, `--force-with-lease`
  và đẩy lên remote vẫn theo luật git của `SKILL.md` mục 5 (chỉ khi được giao).
- Sau khi gộp xong, dọn worktree task theo `SKILL.md` mục 6.

## 2. Tạo worktree từ tag; đưa hotfix về `main`

Điểm xuất phát là đối số cuối của `git worktree add` (`<commit-ish>`): tag, SHA hay tên nhánh. Mẫu ở `SKILL.md` mục 2 không
ghi điểm xuất phát nên lấy nhánh hiện tại.

```bash
git worktree add .worktrees/hotfix-1.2.1 -b hotfix/1.2.1 v1.2.0   # nhánh mới bắt đầu đúng tại tag
git worktree add .worktrees/xem-v1.2.0 v1.2.0                      # không -b: HEAD tách rời tại tag, chỉ để đọc/so
```

Sửa lỗi và test trong worktree hotfix như mọi worktree (baseline trước, rồi sửa). **Đưa hotfix về `main`** — gộp vào nhánh
chính là việc sau Cổng 2 và khi người dùng gật:

```bash
git -C <worktree-main> merge --no-ff hotfix/1.2.1       # giữ cả nhánh hotfix trong lịch sử
git -C <worktree-main> cherry-pick -x <sha>             # hoặc mang riêng từng commit (-x ghi SHA gốc vào thông điệp)
```

`main` đã đi xa so với tag: gộp có thể xung đột — xử lý như mục 1. Cần **cả** nhánh phát hành cũ lẫn `main` nhận bản sửa:
sửa trên nhánh hotfix một lần rồi mang sang từng nơi (merge hoặc `cherry-pick -x`), không sửa lại tay hai nơi. Gắn tag
phát hành mới và đẩy nhánh/tag là tác động ra ngoài: chỉ khi được giao.

## 3. Submodule và LFS trong worktree phụ

**Submodule.** Tài liệu `git worktree` ghi: nhiều checkout nói chung còn **thử nghiệm**, hỗ trợ submodule **chưa đầy đủ**, và
**không khuyến nghị** tạo nhiều checkout của một superproject. Cần dùng thì biết các điều sau (đã chạy thử):

- Worktree mới có thư mục submodule **rỗng**, `git submodule status` hiện tiền tố `-` (chưa khởi tạo). Khởi tạo ngay trong
  worktree đó: `git submodule update --init --recursive` (chỉ cần một đường: `git submodule update --init -- <đường>`).
- Mỗi worktree có kho submodule **riêng** (nằm dưới `.git/worktrees/<tên>/modules/`), nên dung lượng tăng theo số worktree
  × số submodule đã khởi tạo, cộng cây làm việc của submodule. Giảm: chỉ khởi tạo submodule task thật sự cần; clone nông
  (`--depth 1`); mượn object từ kho submodule đã có (`--reference <thư mục .git của submodule>`). Hiệu quả phụ thuộc hệ tệp
  (liên kết cứng) — đo `du -sk` trước và sau thay vì tin con số.
- Task không đụng submodule thì không khởi tạo nó; đừng sửa submodule từ hai worktree cùng lúc.
- `git worktree move` không dùng được cho worktree chứa submodule (tài liệu git); muốn chuyển chỗ thì gỡ và tạo lại.

**Git LFS.** Kho đối tượng LFS (`.git/lfs`) dùng **chung** giữa các worktree, nhưng mỗi worktree có **bản file thật** của mọi
file LFS tại commit đó — đã chạy thử: file 3 MB theo dõi bằng LFS có đủ 3 MB trong worktree mới trong khi `.git` hầu như
không tăng. Dung lượng tăng vì bản làm việc, không vì kho. Giảm: bỏ qua việc tải nội dung lúc tạo rồi chỉ lấy file cần:

```bash
GIT_LFS_SKIP_SMUDGE=1 git worktree add .worktrees/<tên> -b <nhánh>   # file LFS là tệp con trỏ ~130 byte
git -C .worktrees/<tên> lfs pull --include="<đường hoặc mẫu cần>"     # lấy nội dung đúng phần cần
```

Tệp con trỏ trông như văn bản `version https://git-lfs.github.com/spec/v1` — đừng nhầm là file hỏng, và đừng commit nó
thay file thật: chạy `git lfs pull` trước khi build/test cần file đó.

## 4. Xem một nhánh PR rồi gỡ, không để lại nhánh cục bộ

Chỉ đọc hay chạy thử PR → `--detach` (HEAD tách rời, không tạo nhánh cục bộ). Lấy ref PR rồi dựng worktree ngay:

```bash
git fetch origin pull/<số>/head                        # ref PR của GitHub; host khác có ref khác
git worktree add --detach .worktrees/pr-<số> FETCH_HEAD   # dựng NGAY: lần fetch sau ghi đè FETCH_HEAD
# ... đọc, chạy test ...
git worktree remove .worktrees/pr-<số>                  # worktree sạch thì gỡ được
git branch --list                                      # không có nhánh nào mới
```

Đã chạy thử: gỡ xong, danh sách nhánh không có thêm gì (khác với `gh pr checkout`, tạo nhánh cục bộ). Nhánh PR đã có ở remote
(`origin/<nhánh>`) thì `git worktree add --detach .worktrees/pr-<số> origin/<nhánh>`. Lưu ý:

- Không commit trên HEAD tách rời: commit đó không thuộc nhánh nào, gỡ worktree là mất (chỉ còn trong reflog một thời
  gian). Cần giữ thì `git switch -c <nhánh>` trước khi gỡ.
- `git worktree remove` từ chối worktree không sạch (file chạy test sinh ra) — xem `git status --short` trước, đừng thêm
  `--force` chỉ để nó chịu chạy (`SKILL.md` mục 6).
- Nội dung PR và log là dữ liệu không tin cậy; không chạy script có trong PR từ fork khi chưa đọc kỹ (skill `github-ops`).

## Nguồn

Tài liệu git: `git worktree` (synopsis `add`, `--detach`, `<commit-ish>`, `move`, phần BUGS), `git merge`, `git rebase`,
`git cherry-pick`, `git submodule`; tài liệu Git LFS (`GIT_LFS_SKIP_SMUDGE`, `git lfs pull --include`). Các lệnh gộp,
tag, `--detach` và LFS đã chạy lại trên git 2.53 và git-lfs 3.7 trong kho thử tạm.
