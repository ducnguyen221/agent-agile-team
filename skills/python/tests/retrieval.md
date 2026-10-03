---
skill: python
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 4467fcd180d5584b66492c8cce5e9048a85de89b
date: 2026-10-03
result: "strict 3/6 (+3 partial, 0 fail) — below threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 6/6"
agent_ids:
  questions: a07b68598c1640c14
  answers: aaf07dbbc0098ce67
---

Đã đọc: `<gốc worktree>\skills\python\SKILL.md` (và các file trong `references/` mà `SKILL.md` trỏ tới, nếu có)

# Thử truy xuất — python

> **Kết luận:** dưới ngưỡng ≥4/5 câu tình huống Đạt: 2/5 Đạt (câu 2, 3), 3/5 Một phần (câu 1, 4, 5), 0 Không đạt; câu ranh giới (câu 6) chủ thể trỏ đúng `error-handling`. Chủ thể đọc 9 file, trỏ đúng
> nơi ở mọi câu và ở mọi chỗ skill thiếu đều nói "skill không có" thay vì bịa (entry point `[project.scripts]`, `uv build`, `monkeypatch`, `lru_cache`, `cProfile`/`tracemalloc`, composition, gỡ import vòng).
> Cụm "coverage" đã bỏ khỏi `description`, nên lượt này không còn câu nào lệch với lời hứa của `description`; mọi chỗ thiếu là nội dung ngoài phạm vi hiện tại của skill (cho điều phối ghi `CO`).

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực, kèm danh sách chủ đề của các bộ cũ để không lặp); lượt này là **bộ câu mới** chạy lại sau commit `5e02bfb` (bỏ "coverage" khỏi `description`).
Cột "Mục kỳ vọng" do người chấm ghi vào file nháp **trước khi** giao chủ thể (mtime file nháp 2026-10-03 21:54:53 +0700 (21:54:53,40), sớm hơn lệnh giao chủ thể); mục kỳ vọng ghi theo cây hiện tại.
Câu 6 là câu ranh giới, đáp án do người soạn nêu và người chấm đối chiếu với `description` của skill đáp.
Nguyên văn câu hỏi của người soạn, file nháp kỳ vọng, output TRỌN của chủ thể (đường dẫn thư mục người dùng giữ nguyên ở đó, còn ở đây lược thành `<gốc worktree>` vì repo chặn tên người dùng)
và số lượt công cụ: hồ sơ sprint của lớp riêng, `evidence/TK12-green/python-retrieval-rerun-3.md`.

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Class `Config` đọc từ biến môi trường, gói thành CLI có `pyproject.toml` với entry point `mytool = mytool.cli:main`, src layout. Bố trí `src/mytool/`, `__main__.py`, `[project.scripts]` thế nào, và `uv build` ra wheel cài được ở máy khác? | `references/packaging-and-tooling.md` › 1. Bố cục dự án chuẩn, › 4. `pyproject.toml` (`[build-system]` hatchling); `[project.scripts]`, `__main__.py`, `uv build` có thể không có | `packaging-and-tooling.md` › 1, › 3, › 4; `SKILL.md` › 3 | Một phần (có bố cục `src/`, `[build-system]` hatchling, `uv sync`/`uv add`; không có `[project.scripts]`, `__main__.py`, `uv build`, cách kiểm wheel) |
| 2 | `mypy --strict` báo `Missing type parameters for generic type "dict"` và `Incompatible return type` ở hàm trả `list \| None`. Dùng `Protocol`, `TypeVar` hay `overload` để type hàm `get_first(items)` trả phần tử đầu hoặc `None`? | `references/type-hints-and-dataclasses.md` › 1.3 `TypeVar`, › 1.4 `Protocol`, › 1.2; `overload` không có | `type-hints-and-dataclasses.md` › 1.3, › 1.4, › 1.2, › 1.1 | Đạt (mẫu `first(items: list[T]) -> T \| None` đúng chỗ, `Protocol` đúng là không cần; không có `overload`, `mypy --strict`) |
| 3 | `monkeypatch` patch `datetime.now()` và `os.environ` ở nhiều file, test A rò trạng thái sang test B (chạy riêng pass, chạy cả bộ fail). Fixture trong `conftest.py` scope nào, dùng `tmp_path`, `monkeypatch` thế nào để cô lập? | `references/testing-fixtures.md` › 1.3 Scope, › 1.2 `yield`, › 1.6 `conftest.py`; `testing-organization.md` › 2 `tmp_path`; `monkeypatch` có thể không có | `testing-fixtures.md` › 1.3, › 1.5, › 1.2, › 1.6; `testing-organization.md` › 2; `testing.md` › 3; `testing-mocking-async.md` › 1.5, › 1.6 | Đạt (scope hẹp nhất, `autouse`, `yield`, `tmp_path` trả lời việc cô lập; không có `monkeypatch`, patch `datetime.now()`/`os.environ`, chẩn đoán test phụ thuộc thứ tự) |
| 4 | Hàm xử lý file log lớn, mỗi dòng tạo nhiều object nhỏ, chậm và memory tăng dần. Đổi sang `__slots__`, `functools.lru_cache` hay `dataclass(slots=True)`? Đo trước bằng `cProfile`/`tracemalloc` thế nào? | `references/generators-concurrency-performance.md` › 3.1 `__slots__` + `type-hints-and-dataclasses.md` › 2.1; `lru_cache`, `cProfile`, `tracemalloc` không có | `generators-concurrency-performance.md` › 3.1, › 1.2, › 1.3, › 3.2 | Một phần (có `__slots__`/`slots=True`, generator, nguyên tắc "đo trước"; không có `lru_cache`, `cProfile`, `tracemalloc`, tức cách đo) |
| 5 | Module có class kế thừa nhiều tầng, `isinstance` khắp nơi, import vòng giữa `models.py` và `services.py`. Refactor theo composition hay `Protocol`, gỡ circular import thế nào mà không phá API? | `references/type-hints-and-dataclasses.md` › 1.4 `Protocol`; `packaging-and-tooling.md` › 2, › 3; composition và gỡ import vòng không có | `type-hints-and-dataclasses.md` › 1.4; `packaging-and-tooling.md` › 3; `SKILL.md` › 7 | Một phần (chỉ có `Protocol` cho duck typing; không có composition vs kế thừa, `TYPE_CHECKING`/import cục bộ, giữ API khi dời code) |
| 6 | Server Python sinh stack trace dài ở production; thiết kế hệ exception riêng (`DomainError`, `NotFoundError`, `ValidationError`), khi nào wrap/re-raise, log ở tầng nào để không trùng, retry backoff cho lỗi tạm thời từ database | mục khác: skill `error-handling` | mục khác: `error-handling` (kèm `postgres` cho phần DB; từ `SKILL.md` › 8 và `errors-context-decorators.md` › 1.3) | Đạt (ranh giới) |

## Thiếu nội dung / mâu thuẫn

- **Thiếu nội dung (câu 1).** Không có `[project.scripts]` (entry point CLI), `__main__.py`, `uv build`, cách kiểm wheel cài được.
- **Thiếu nội dung (câu 3).** Không có fixture `monkeypatch` (`setattr`/`setenv`/`delenv`), cách patch `datetime.now()` và `os.environ`, cách chẩn đoán test phụ thuộc thứ tự chạy.
- **Thiếu nội dung (câu 4).** Không có `functools.lru_cache`, `cProfile`, `tracemalloc`.
- **Thiếu nội dung (câu 5).** Không có so sánh composition với kế thừa, cách gỡ circular import (import cục bộ, tách module, `TYPE_CHECKING`).
- **Nhẹ (câu 2).** Không có `overload` và `mypy --strict`. Câu 6 thiếu log một tầng và retry/backoff, đúng là phần của `error-handling`.
- Theo brief `X4` không sửa tiếp: mở rộng nội dung các mục trên thuộc sprint nội dung mới, điều phối ghi `CO`.
- Không có mâu thuẫn giữa các file trong chín file chủ thể đọc.
