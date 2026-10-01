# Test

Chạy: `python -m pytest` từ gốc repo (Python 3.9+ và pytest). Coverage dòng cho `scripts/` (ngưỡng 80 %, cấu
hình ở `pyproject.toml`): `python -m coverage run -m pytest` rồi `python -m coverage report -m` — cần gói
`coverage`; cài vào `.venv/` của repo (đã ignore), không cài vào Python chung.

| File | Kiểm gì |
|---|---|
| `test_version_sync.py` | Mọi manifest cùng một version; mục đầu `CHANGELOG.md` là version đó |
| `test_common.py` | Tập con YAML (mọi cấu trúc ngoài tập con báo lỗi có dòng), che mã trong Markdown, `.agile.json` |
| `test_check.py` | Bộ sạch `fixtures/valid/` thoát 0; mỗi ca trong `fixtures/broken.json` bị bắt đúng mã luật, đúng file, đúng mã thoát; mỗi luật có ít nhất một ca; `templates/` sạch |
| `test_check_self.py` | `--self`: chống rò bằng danh sách tạm (đột biến), miễn trừ, `NOT_CONFIGURED`, ngân sách `AGENTS.md`, nhãn thang cũ, chính repo này |
| `test_init.py` | Chạy thử không ghi; `--apply` không ghi đè; chạy hai lần không đổi; sprint mới đặt lại trạng thái và ghi SPRINTS |
| `test_index.py` | Khối "Đang mở" của ba sổ: lọc, sắp mới nhất ở trên, giống nhau từng byte khi chạy lại, `--check` |
| `test_samples.py` | `samples/` sạch theo `check`, khối "Đang mở" đã cập nhật, chèn mã trần thì đỏ |
| `test_provenance.py` | Mọi `skills/*/SKILL.md` và `agents/*.md` có `source`, `source_sha`, `license`, `rewrite_before_public`; `source` là danh sách thì `source_sha` cùng độ dài; mọi SHA (kể cả `base_sha`, trừ `null`) có trong `UPSTREAM.md`; `rewrite_before_public: true` ⇔ skill có dòng ở `THIRD_PARTY.md` mục 3 |

**Fixture:** `fixtures/valid/` là một sprint sạch đủ bốn tài liệu. `fixtures/broken.json` liệt kê ca hỏng cố
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
  `Cat`, `cat_x`, `cat2`. Mục chứa ký tự đường dẫn (`\`, `/`, `:`, `~`) khớp **chuỗi con** ở bất kỳ
  đâu. Áp cho cả nội dung lẫn tên file.
- **Phạm vi quét:** mọi file Git đang theo dõi và file chưa add (trừ file bị ignore) trong repo (nội dung và
  tên file); miễn trừ ở
  [`scripts/README.md`](../scripts/README.md) mục "Phạm vi `--self`".
- **Khi thiếu biến, file không đọc được hoặc rỗng:** test chống rò báo **Chưa chạy** (skip có lý do), không
  báo Đạt; `check.py --self` in `WARNING NOT_CONFIGURED`.
