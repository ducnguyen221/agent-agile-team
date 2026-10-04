# Chuyển sang uv + `pyproject.toml`, và CI nhiều phiên bản Python

> **Kết luận:** chuyển `requirements.txt`/`pip-tools` sang dự án uv bằng `uv init` + `uv add -r <file> -c <file khoá>` để
> **giữ nguyên phiên bản đang chạy**; `pyproject.toml` thay các file `.in`, `uv.lock` thay các file `.txt` đã khoá. CI
> dùng `setup-uv` có cache và `uv sync --locked`. Nhiều phiên bản Python: ma trận CI + `uv` (đơn giản nhất) hoặc `nox`/`tox`
> khi cần chạy cả cục bộ; code phải tương thích bản thấp nhất trong `requires-python`.

## 1. Chuyển từ `requirements.txt` / `pip-tools`

```bash
uv init                                          # tạo pyproject.toml (xoá file mẫu uv sinh thêm nếu không dùng)
uv add -r requirements.in -c requirements.txt    # nhập phụ thuộc trực tiếp; file đã khoá làm ràng buộc phiên bản
sed '/^-r /d' requirements-dev.in | uv add --dev -r - -c requirements-dev.txt   # phụ thuộc phát triển → nhóm dev
uv lock                                          # sinh uv.lock (chạy ngầm khi `uv add`/`uv run`)
uv sync --locked                                 # dựng .venv đúng theo uv.lock
```

- **Đối chiếu:** `requirements.in` (phụ thuộc trực tiếp) → `[project] dependencies` trong `pyproject.toml`;
  `requirements.txt` do `pip-compile` sinh (đã ghim cả phụ thuộc gián tiếp) → `uv.lock`; `requirements-dev.in` → nhóm
  `dev` (`[dependency-groups]`), nhóm khác dùng `--group <tên>`. Chỉ có một `requirements.txt` viết tay → `uv add -r
  requirements.txt` (kèm `-c` nếu muốn giữ phiên bản).
- `-c`/`--constraints` chỉ **ràng buộc phiên bản**, không thêm gói vào `pyproject.toml`: nhờ đó lần khoá đầu không đổi
  phiên bản nào. Sau khi chuyển, chạy test trước khi nâng bản (`uv lock --upgrade-package <gói>` nâng từng gói).
- File `.txt` cũ giữ tới khi hết nơi dùng (Dockerfile, tài liệu cho người khác): xuất lại từ khoá bằng `uv export`
  (định dạng `requirements-txt`, `pylock.toml` hoặc SBOM) thay vì sửa tay hai nơi. Phụ thuộc riêng theo nền tảng
  (Windows/Linux): `uv.lock` đã đa nền tảng; nếu có nhiều file `.txt` theo nền tảng thì `-c` từng file.
- Commit `pyproject.toml` và `uv.lock`; bỏ `pip-compile`/`pip install -r` khỏi tài liệu và lệnh CI. Thay `python -m venv` +
  `pip` bằng `uv run <lệnh>` (tự kiểm khoá và đồng bộ môi trường trước khi chạy).

## 2. CI GitHub Actions với uv

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@<ghim theo SHA hay tag đã xem>
        with:
          enable-cache: true          # cache của uv, khoá theo uv.lock
      - run: uv python install        # theo .python-version / requires-python
      - run: uv sync --locked --dev
      - run: uv run ruff check .
      - run: uv run mypy src
      - run: uv run pytest
```

- `uv sync --locked` **thất bại** nếu `uv.lock` không khớp `pyproject.toml` — đó là cổng chặn "quên khoá lại"; `--frozen` dùng khoá
  sẵn có không kiểm độ mới (chỉ dùng khi biết mình đang làm gì). `uv lock --check` kiểm khoá mà không đổi gì.
- Cache: `enable-cache: true` của `setup-uv` là cách ngắn nhất; tự quản lý cache thì đặt `UV_CACHE_DIR` rồi chạy `uv cache
  prune --ci` ở cuối job để cache gọn (bỏ bớt phần dựng lại rẻ hơn lưu).
- Ghim `setup-uv` và bản uv (`version:`) để CI không đổi theo bản mới; nâng bản là một thay đổi riêng.
- Mục tiêu thời gian CI: không có con số chung — **đo** thời gian từng bước (`uv sync` lần đầu không cache so với có cache,
  lệnh test) trước khi đặt mục tiêu; thường phần phụ thuộc rút xuống vài giây khi cache trúng, phần còn lại là test.
  Chưa đo thì ghi "chưa đo" thay vì hứa một con số.

## 3. Nhiều phiên bản Python

Cần kiểm code chạy ở cả Python thấp nhất và cao nhất mà `requires-python` hứa.

| Cách | Hợp khi | Lưu ý |
|---|---|---|
| Ma trận CI + uv | chỉ cần kiểm trên CI | `strategy.matrix.python-version` + `setup-uv` với `python-version: ${{ matrix.python-version }}` (hoặc `uv run --python <bản>`), một job một phiên bản, chạy song song |
| `nox` | muốn chạy được cả cục bộ, phiên chạy viết bằng Python | `@nox.session(python=["3.9", "3.12"])` tạo phiên `tests-3.9`, `tests-3.12`; `venv_backend="uv"` (hoặc `"uv\|virtualenv"`) để dựng venv nhanh; chạy `nox -s tests-3.9` |
| `tox` | dự án đã có `tox.ini`, môi trường theo khai báo | môi trường `py39`, `py312`; kết hợp plugin uv của tox nếu muốn dựng nhanh |
| `uv run --python 3.9 pytest` | thử nhanh một bản cục bộ | `uv python install 3.9 3.12` tải các bản cần dùng (uv tải Python tự động trừ khi tắt `python-downloads`) |

```python
# noxfile.py
import nox

@nox.session(python=["3.9", "3.12"], venv_backend="uv")
def tests(session: nox.Session) -> None:
    session.install(".", "pytest")
    session.run("pytest", *session.posargs)
```

Khuyến nghị: bắt đầu bằng **ma trận CI + uv** (không thêm công cụ); thêm `nox` khi nhóm cần chạy ma trận cục bộ trước khi
đẩy. Đừng dùng cả `tox` lẫn `nox` cho cùng một dự án.

**Viết code chạy được ở bản thấp nhất:**
- `match`/`case` chỉ có từ **3.10**: trên 3.9 là lỗi cú pháp (không sửa được bằng `from __future__ import annotations`) → dùng
  chuỗi `if/elif` với `isinstance`, hoặc bảng điều phối `dict` kiểu → hàm.
- `X | Y` trong **annotation** dùng được trên 3.9 **nếu** có `from __future__ import annotations` (annotation chỉ lưu
  thành chuỗi) — nhưng **không** dùng được ở chỗ bị *đánh giá lúc chạy*: `isinstance(x, int | str)`, alias kiểu
  (`Id = int | str`), và thư viện đọc annotation lúc chạy (`typing.get_type_hints`, pydantic, FastAPI) → dùng
  `Optional[X]`/`Union[X, Y]`, hoặc gói bù của thư viện (pydantic báo lỗi gợi ý `eval-type-backport` trên 3.9).
- Các thứ mới hơn cũng có giới hạn bản: `typing.assert_never` từ 3.11 (bản thấp hơn: `typing_extensions`),
  `asyncio.timeout` từ 3.11 (bản thấp hơn: `asyncio.wait_for`), kiểu dựng sẵn `list[int]` từ 3.9.
- `from __future__ import annotations` **không** đổi hành vi lúc chạy ở chỗ dùng annotation để quyết định (dataclass,
  pydantic, FastAPI, `get_type_hints`): chúng vẫn phải đánh giá chuỗi và gặp `X | Y` trên 3.9. Cờ này sẽ bị thay (PEP 649/749);
  đừng coi là giải pháp lâu dài.
- Khai `requires-python = ">=3.9"` và để ma trận CI chạy đúng bản thấp nhất: mypy `python_version` đặt theo bản thấp nhất.

## Nguồn

Tài liệu uv (docs.astral.sh/uv: guides — Using uv in GitHub Actions, Migration from pip to a project; reference — `uv sync`,
`uv add`, `uv export`, `uv cache prune`; Python versions), tài liệu Nox (Configuration & usage), tài liệu Python
(`__future__`, `typing`, `asyncio`), thông báo lỗi của pydantic cho Python 3.9. Chưa chạy trực tiếp lệnh uv trên máy đo
(uv không cài); các cờ trên lấy từ tài liệu tham chiếu chính thức.
