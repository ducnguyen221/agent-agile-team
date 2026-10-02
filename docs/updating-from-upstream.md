# Cập nhật và mở rộng từ nguồn gốc

> **Kết luận:** muốn cập nhật hay mở rộng repo này thì **quay lại nguồn gốc**, không viết lại từ trí nhớ.
> Danh sách nguồn duy nhất là mục "Sổ theo dõi nguồn gốc" của [UPSTREAM.md](../UPSTREAM.md): với từng nguồn,
> so HEAD mới nhất với mốc đã distill → đọc phần thay đổi chạm file nguồn → quyết định lấy / bỏ qua / hoãn
> và ghi lý do → distill qua quy trình sprint của chính repo → cập nhật SHA, ngày, dấu vết → chạy
> `check.py --self` và `pytest`. Nguồn mới phải vào Sổ theo dõi **trước** khi distill.

## 1. Vì sao phải quay lại nguồn gốc

- Repo này **thay thế** các bộ skill gốc (Superpowers, ECC, gstack). Môi trường dùng repo có thể đã gỡ các bộ
  đó, nên không còn plugin, cache hay công cụ nào báo khi nguồn gốc ra bản mới.
- Nội dung đã distill đứng yên ở SHA ghi trong `UPSTREAM.md`, còn nguồn gốc vẫn đi tiếp: bản vá bảo mật, sửa
  lỗi trong skill, thành phần mới, đổi giấy phép, đổi tên hay lưu trữ repo.
- Vì thế `UPSTREAM.md` là **nguồn sự thật duy nhất** về "đã lấy gì, tới đâu, khi nào xem lại". Không dựa vào
  bản cài cũ, ghi chú ngoài repo hay trí nhớ của agent. Nguồn private không nằm trong repo — lớp riêng của môi
  trường tự giữ đường theo dõi của chúng.

## 2. Khi nào chạy

| Dịp | Làm gì |
|---|---|
| Định kỳ, mỗi tháng một lần | Lượt kiểm (mục 3) cho mọi nguồn có cột **Kiểm** khác "không"; không có gì đáng lấy thì chỉ ghi nhật ký |
| Trước mỗi đợt distill | Bắt buộc: lấy HEAD **mới nhất tại thời điểm distill**, chốt thành khối đợt mới rồi mới đọc |
| Mở rộng: thêm skill, agent, stack hay chuẩn code mới | Mục 5 — tìm nguồn trước khi viết |
| Nguồn ra bản lớn, công bố bản vá bảo mật, đổi giấy phép, đổi tên hay lưu trữ repo | Lượt kiểm riêng cho nguồn đó |
| Điều kiện "xét lại" ở cột **Kiểm** đã đạt (ví dụ một công cụ đã loại lên `v1.0`) | Đánh giá lại nguồn đó như nguồn mới (mục 5) |

## 3. Lượt kiểm — so bản mới

1. Mở `UPSTREAM.md` mục "Sổ theo dõi nguồn gốc"; đi lần lượt từng dòng cần kiểm.
2. Lấy HEAD của nhánh ghi ở khối đợt (thường `main`):
   - `gh api repos/<owner>/<repo>/commits/<nhánh> --jq '.sha + " " + .commit.committer.date'`
   - hoặc không cần đăng nhập: `git ls-remote https://github.com/<owner>/<repo> refs/heads/<nhánh>`
   - bản phát hành: `gh api repos/<owner>/<repo>/releases/latest --jq .tag_name`
   - giấy phép: `gh api repos/<owner>/<repo>/license --jq .license.spdx_id`
   - trạng thái repo: `gh api repos/<owner>/<repo> --jq '.full_name, .archived'` (tên trả về khác tên đã ghi =
     repo đã đổi tên; ghi tên mới, giữ tên cũ trong ngoặc)
3. HEAD trùng cột **Kiểm gần nhất** → nguồn không đổi, sang dòng sau.
4. Khác → liệt kê thay đổi giữa mốc và HEAD:
   `gh api repos/<owner>/<repo>/compare/<mốc>...<HEAD> --jq '.ahead_by, .files[].filename'`, rồi lọc theo
   đường file nguồn ở cột "Nguồn" của bảng nguồn theo skill và frontmatter `source` của từng skill/agent.
5. Đọc phần thay đổi chạm file nguồn, cùng CHANGELOG hay release notes của nguồn. Xếp mỗi thay đổi vào một
   loại: bản vá bảo mật · sửa lỗi nội dung skill · thành phần mới · đổi giấy phép · chỉ đổi phần repo này
   không dùng.
6. Quyết định cho từng nguồn: **lấy** (đi mục 4), **bỏ qua** hoặc **hoãn**; ghi một dòng vào "Nhật ký kiểm
   bản mới" của `UPSTREAM.md` theo dạng *gì — vì sao — sai thì tốn gì*, rồi sửa cột **Kiểm gần nhất**. Bỏ qua
   cũng ghi, để lần sau không đọc lại cùng đoạn thay đổi.
7. Bản vá bảo mật chạm nội dung đã distill: không hoãn quá một lượt kiểm; ghi vào REQUESTS của dự án dùng
   repo này nếu chưa sửa được ngay.

**Cạm bẫy đã biết:**

- API `compare` chỉ trả tối đa 300 file. Nhiều hơn thì xem lịch sử từng file nguồn:
  `gh api "repos/<owner>/<repo>/commits?path=<file>&sha=<HEAD>" --jq '.[].sha'`.
- SHA của tag có chú thích **không** phải SHA commit — phải đi tiếp qua `git/tags/<sha>` mới ra commit dùng
  được cho `compare`.
- Repo lưu trữ (`archived: true`) không có bản mới; chỉ cần kiểm nó còn lưu trữ.
- Nguồn đến gián tiếp (ví dụ mẫu Postgres đến qua ECC) chỉ kiểm khi nguồn trung gian đổi đúng phần đó.

## 4. Distill khi quyết định lấy

- **Một đợt cập nhật = một sprint** theo [method/process.md](../method/process.md). Cỡ theo
  [method/sizing.md](../method/sizing.md): chỉ cập nhật mốc hay sửa chữ không đổi hành vi skill → rất nhỏ
  (một `SPRINT.md`); sửa nội dung một skill có sẵn → nhỏ hoặc vừa; thêm skill/agent hay cả một đợt → vừa
  hoặc lớn. Đụng `AGENTS.md` hay luật lõi → `risk_tags: [rules]`, cỡ lớn.
- **Chốt mốc trước khi đọc:** ghi khối "Đợt N — chốt SHA <ngày>" ở `UPSTREAM.md` với nhánh, SHA HEAD, ngày
  commit, tag, giấy phép, cách dùng; đợt dự kiến (mục "Đợt 2 — dự kiến") chuyển thành khối chốt.
- **Cách dùng theo giấy phép** (bảng đầu `UPSTREAM.md`): chép · ý · NOTICE · private. Nguồn chỉ lấy ý thì
  viết lại, không chép câu.
- **Sửa skill có sẵn** theo skill `writing-skills`: chạy RED trên **bản hiện tại** với kịch bản dụ đúng lỗi
  mà bản nguồn mới đã sửa. Bản hiện tại đạt → không sửa, ghi "bỏ qua — đã đạt" vào nhật ký. Hỏng → sửa tối
  thiểu, chạy GREEN cùng kịch bản, chạy lại kịch bản cũ để chắc không lùi. Skill tham chiếu kiểm truy xuất
  (`tests/retrieval.md`) thay cho thử áp lực.
- **Giữ luật lõi khi distill:** một thang mức (quy đổi ở [method/severity.md](../method/severity.md)), mã
  định danh, không gắn cứng tên dự án hay máy, không mang hook hay runtime của nguồn.
- **Cập nhật dấu vết trong cùng commit:**
  - frontmatter từng skill/agent: `source`, `source_sha` (SHA mới), `license`, `base_sha` (SHA cũ, để lần sau
    đối chiếu);
  - `UPSTREAM.md`: khối đợt mới, bảng nguồn theo skill, cột **Đã distill tới** và **Kiểm gần nhất** của Sổ
    theo dõi, dòng nhật ký;
  - `NOTICE` khi có nguồn MIT/Apache-2.0 mới; `THIRD_PARTY.md` (vì sao dùng theo cách đó, mục 3 nếu gốc không
    giấy phép);
  - `CHANGELOG.md` (chỉ thêm); `docs/MIGRATION.md` nếu đổi tên skill.
- **Kiểm:** `python scripts/check.py --self` phải Đạt với `chống rò: ok`; `python -m pytest -q` xanh —
  `tests/test_provenance.py` đỏ khi SHA trong frontmatter không có ở `UPSTREAM.md` hay nguồn thiếu dòng ở Sổ
  theo dõi. Sau đó kiểm định độc lập như mọi sprint: Tech Reviewer so bản distill với nguồn (đúng giấy phép,
  không mất luật sắt, không chép phần đã quyết bỏ).

## 5. Mở rộng — thêm skill, agent hay nguồn mới

1. **Tìm nguồn trước khi viết.** Xem mục "Đợt 2 — dự kiến" và Sổ theo dõi trước; chưa có thì tìm repo công
   khai phù hợp. Nguồn đã loại không đánh giá lại trừ khi điều kiện "xét lại" đạt.
2. **Ghi sổ trước khi distill.** Kiểm giấy phép, chọn cách dùng, thêm một dòng vào Sổ theo dõi (vai trò, nơi
   nhận nội dung, mốc, khi nào kiểm). Chủ (owner) mới thì thêm vào `UPSTREAM_OWNERS` trong
   `scripts/check.py` — test của Sổ theo dõi đỏ nếu hai nơi lệch nhau. Không nới luật chống rò theo cách khác.
3. **Distill** theo mục 4, như một sprint.
4. **Không có nguồn phù hợp** thì tự viết; frontmatter ghi theo [skills/README.md](../skills/README.md) mục 1.
5. **Nguồn private hay nội bộ:** không ghi tên trong repo. Dùng nhãn trung tính (như "bộ skill quy trình
   private"), ghi cờ `rewrite_before_public`, để bản đồ thật ở lớp riêng.
