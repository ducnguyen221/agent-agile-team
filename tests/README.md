# Test

Chạy: `python -m pytest` từ gốc repo (Python 3.9+ và pytest). Coverage dòng cho `scripts/` (ngưỡng 80 %, cấu
hình ở `pyproject.toml`): `python -m coverage run -m pytest` rồi `python -m coverage report -m` — cần gói
`coverage`; cài vào `.venv/` của repo (đã ignore), không cài vào Python chung.

Metadata thử skill chấp nhận tên model Claude và GPT dạng `gpt-major[.minor]-family`: major 1–99, minor
0–99 tuỳ chọn, không số 0 dẫn đầu, đúng một family `sol` / `astra` / `terra` / `luna`; ngoại lệ `gpt-5.5`.
Tên có thể kèm chú thích. Placeholder, phiên bản 0/999, ba phần phiên bản và family ghép đều bị chặn.
Đây là kiểm hình tên, không xác minh registry hay việc model thật sự chạy; test ID tương lai giả lập chỉ
chứng minh không khoá danh sách version hiện tại. Output/ID chủ thể mới là bằng chứng. RED/GREEN cùng model/tier.

| File | Kiểm gì |
|---|---|
| `test_version_sync.py` | Mọi manifest cùng một version; mục đầu `CHANGELOG.md` là version đó |
| `test_common.py` | Tập con YAML (mọi cấu trúc ngoài tập con báo lỗi có dòng), che mã trong Markdown, `.agile.json` (kể cả khoá `ledger`: mặc định tắt, tên dự án, mẫu đường sổ có `{project}`, hình sai); mã nguồn không vượt mức sàn Python của CI (`verify.yml`) |
| `test_check.py` | Bộ sạch `fixtures/valid/` thoát 0; mỗi ca trong `fixtures/broken.json` bị bắt đúng mã luật, đúng file, đúng mã thoát; mỗi luật có ít nhất một ca và một hàng trong bảng luật của `scripts/README.md`; `templates/` sạch; sổ tập trung (`ledger-*`, khoá `ledger`, biến máy `AGENT_AGILE_LEDGER`; cấu hình sai hình thì chỉ `config-invalid`, không traceback); hợp đồng `size × doc` (`SPRINT.md` hai phần hoặc bốn phần, `sprint-size-mismatch`); nhãn thang cũ trong câu và tiếng Việt |
| `test_install_docs.py` | `INSTALL.md`: hai prompt VI/EN ≤12 dòng, mục 0–7, đủ bốn `hosts/`; con trỏ `CLAUDE.md`/`GEMINI.md`; khối PowerShell không dùng `~`, lệnh bash trên bản clone có khối PowerShell tương ứng; link tương đối trong tài liệu người dùng không gãy (có ca đột biến) |
| `test_check_self.py` | `--self`: chống rò bằng danh sách tạm (đột biến), miễn trừ tường minh và hẹp (`LEAK_EXEMPTIONS` — mỗi kiểu có ca đột biến, mỗi mục có lý do và được ghi ở `scripts/README.md`), `NOT_CONFIGURED`, ngân sách `AGENTS.md`, nhãn thang cũ, chính repo này |
| `test_init.py` | Chạy thử không ghi; `--apply` không ghi đè; chạy hai lần không đổi; sprint mới đặt lại trạng thái và ghi SPRINTS; bậc việc `--tiny` / `--size small` (một `SPRINT.md` hai hay bốn phần), `medium`/`large` vẫn bốn file |
| `test_index.py` | Khối "Đang mở" của ba sổ: lọc, sắp mới nhất ở trên, giống nhau từng byte khi chạy lại, `--check`; `SPRINT.md` cỡ nhỏ hiện ở khối "Đang mở" |
| `test_samples.py` | `samples/` sạch theo `check`, khối "Đang mở" đã cập nhật, chèn mã trần thì đỏ |
| `test_provenance.py` | Mọi `skills/*/SKILL.md` và `agents/*.md` có `source`, `source_sha`, `license`, `rewrite_before_public`; `source` là danh sách thì `source_sha` và `license` là danh sách cùng độ dài; nguồn không giấy phép ghi `none`; mọi SHA (kể cả `base_sha`, trừ `null`) có trong `UPSTREAM.md`; `rewrite_before_public: true` ⇔ skill có dòng ở `THIRD_PARTY.md` mục 3; mọi lần nêu số đo "8-gram" / "overlap 0" ngoài `tests/` và `docs/plans` phải mang điều kiện `stoplist` (trong 200 ký tự kế tiếp), và dưới `skills/` (metadata vào băm) không được nêu số đo; `THIRD_PARTY.md` không vừa ghi "phải viết lại thật sự trước khi công khai" vừa ghi "không cần viết lại lần nữa" (có ca đột biến cho cả hai) |
| `test_skill_tests.py` | Mọi skill kỷ luật có `tests/pressure.md`, mọi skill `metadata.kind: reference` có `tests/retrieval.md`; `result` và `model` (đoạn đầu: bỏ khoảng trắng và dấu mở đầu `(` `)` `;` `—` `–` `-` rồi cắt ở `;` `(` ` — `) phải là chuỗi, bắt đầu bằng chữ hoặc số và có ít nhất một chữ (khoá để trống, `~`, `null`, `false`, `[]`, `0`, `.`, `?`, `…`, `3/3` đều đỏ), và không phải chưa chạy (`not run`/`pending`/`chưa chạy`/`dự kiến`, cùng `TBD`/`TODO`/`N/A`/`none`/`false`/`null` nguyên từ, kể cả `(none)`, `None;`, `none.`); `date` hợp lệ; mọi file thử có `skill_sha` + `tier`; `skill_sha` khớp băm cây skill trừ `tests/` ở HEAD (skill đổi sau khi thử thì đỏ; phép so chỉ sinh ca cho file có `skill_sha`; ca skip duy nhất là không có lệnh `git`, còn `git` có mà `ls-tree`/`mktree` lỗi thì đỏ kèm stderr); có ca đột biến cho trạng thái chưa chạy (kể cả mở đầu bằng `(`, `;`, ` — `), `result:`/`model:` để trống, `null` hay giá trị giữ chỗ (kể cả qua `parse_frontmatter`), `date`, thiếu `skill_sha`/`tier`, và ca repo git tạm (`tmp_path`) cho phép băm (đổi `tests/` giữ nguyên, đổi `SKILL.md` thì đổi) và cho thiếu `pressure.md`/`retrieval.md` theo `metadata.kind`; mọi `retrieval.md` dùng cùng một định nghĩa chấm (Đạt / Một phần / Không đạt) và `result` bằng đúng số đếm từ bảng chấm của tệp (ô bắt đầu bằng `Đạt` mà chứa "một phần" ở bất kỳ cách viết nào là mơ hồ; có ca đột biến cho bảng mơ hồ); bảng 'Hiện trạng thử' ở `skills/README.md` mục 4 khớp frontmatter (ô tệp kỷ luật phải có đoạn đầu BẰNG đoạn đầu của `result`, không chỉ là tiền tố; có ca đột biến); với skill có `scenarios.txt`, mục `## Chạy lại` của `pressure.md` phải có mặt và tự nó chứa phép thay vế mở đầu GREEN (mất hoặc đổi tên tiêu đề thì đỏ) |

**Fixture:** `fixtures/agents/` dùng tay cho `SC4` (biên bản QA của sáu agent), không có test tự động đọc chúng. `fixtures/valid/` là một sprint sạch đủ bốn tài liệu (cỡ vừa). Hợp đồng `size × doc` (`SPRINT.md` hai phần · bốn phần, `sprint-size-mismatch`) được kiểm bằng các test dựng tài liệu trong `test_check.py` và `test_init.py`, cộng một ca ở `broken.json`. `fixtures/broken.json` liệt kê ca hỏng cố
ý: mỗi ca chép bộ sạch sang thư mục tạm, áp **đúng một** thay đổi (thay chuỗi hoặc ghi file mới) rồi đòi mã
luật và mã thoát. Thêm luật mới cho `check` thì thêm ca vào đây — test `test_every_rule_has_a_broken_case`
đỏ nếu thiếu. `check --self` không áp luật tài liệu lên `fixtures/`.

## Hợp đồng điểm cắm `AGENT_AGILE_DENYLIST`

Test chống rò (lõi không chứa dấu riêng của bất kỳ máy, người hay dự án nào) đọc danh sách từ cấm từ
**ngoài** repo — để chính danh sách không làm lộ thứ nó che.

- **Giá trị:** đường dẫn tuyệt đối tới một file văn bản UTF-8 nằm ngoài repo.
- **Định dạng:** mỗi dòng một từ cấm, so khớp không phân biệt hoa thường; dòng trống và dòng bắt đầu
  bằng `#` bị bỏ qua.
- **Cách khớp:** mục là chữ khớp **nguyên từ** — không được có chữ cái liền trước hay liền sau (chữ số,
  `_`, `-`, `.`, khoảng trắng đều là ranh giới), nên mục `cat` không bắt `category` nhưng bắt
  `Cat`, `cat_x`, `cat2`. Chữ cái Unicode dính liền (vd `Catđ`) được coi là cùng từ → không bắt; chấp nhận vì
  mục tiêu là chống rò vô ý. Mục chứa ký tự đường dẫn (`\`, `/`, `:`, `~`) khớp **chuỗi con** ở bất kỳ
  đâu. Áp cho cả nội dung lẫn tên file.
- **Phạm vi quét:** mọi file Git đang theo dõi và file chưa add (trừ file bị ignore) trong repo (nội dung và
  tên file); miễn trừ ở
  [`scripts/README.md`](../scripts/README.md) mục "Phạm vi `--self`".
- **Khi thiếu biến, file không đọc được hoặc rỗng:** test chống rò báo **Chưa chạy** (skip có lý do), không
  báo Đạt; `check.py --self` in `WARNING NOT_CONFIGURED`.
