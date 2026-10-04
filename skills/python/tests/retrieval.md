---
skill: python
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 93927b63539f410932e88592bb6c6d1dac0ca10b
date: 2026-10-04
result: "strict 6/6 (+0 partial, 0 fail) — at threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); points-right 6/6"
agent_ids:
  questions: "bộ câu cũ giữ nguyên, không soạn mới"
  answers: a26cd825a62c1e64e
---

Đã đọc: `<gốc worktree>/skills/python/SKILL.md` cùng năm file `references/` (`packaging-and-tooling.md`, `type-hints-and-dataclasses.md`, `testing-fixtures.md`, `generators-concurrency-performance.md`, `errors-context-decorators.md`)

# Thử truy xuất - python

> **Kết luận:** strict 6/6: đạt ngưỡng. Sau `TK11.5` năm câu tình huống đều Đạt (lượt trước 3/6 Đạt hẳn, 3 Một phần: `[project.scripts]`/`uv build`, `lru_cache`/`cProfile`/`tracemalloc`, composition và import vòng); `monkeypatch` thêm cho câu 3; câu ranh giới trả `error-handling`.

Bộ câu hỏi giữ nguyên chữ của lượt trước (bộ câu cũ giữ nguyên, không soạn mới); bộ câu mới là việc của `TK13`. Cột "Mục kỳ vọng" ghi vào file nháp
`.tmp/python-expected.md` **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm). Bài trả lời của chủ thể (id ở
`agent_ids`) và bảng chấm ở `evidence/TK11/python-retrieval.md` trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời,
đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Class `Config` đọc từ biến môi trường, gói thành CLI có `pyproject.toml` với entry point `mytool = mytool.cli:main`, src layout. Bố trí `src/mytool/`, `__main__.py`, `[project.scripts]` thế nào, và `uv build` ra wheel cài được ở máy khác? | `references/packaging-and-tooling.md` › 1 (src layout), › 4 (`pyproject.toml`), › 5 (`[project.scripts]`, `__main__.py`, `main()` trả mã thoát, `uv build`, kiểm wheel ở môi trường sạch) | `references/packaging-and-tooling.md` › 5. Công cụ dòng lệnh; › 1; › 4 | Đạt |
| 2 | `mypy --strict` báo `Missing type parameters for generic type "dict"` và `Incompatible return type` ở hàm trả `list \| None`. Dùng `Protocol`, `TypeVar` hay `overload` để type hàm `get_first(items)` trả phần tử đầu hoặc `None`? | `references/type-hints-and-dataclasses.md` › 1.3 `TypeVar`, › 1.4 `Protocol`, › 1.2; `overload` và `mypy --strict` không có | `references/type-hints-and-dataclasses.md` › 1.3, › 1.4, › 1.2 | Đạt |
| 3 | `monkeypatch` patch `datetime.now()` và `os.environ` ở nhiều file, test A rò trạng thái sang test B (chạy riêng pass, chạy cả bộ fail). Fixture trong `conftest.py` scope nào, dùng `tmp_path`, `monkeypatch` thế nào để cô lập? | `references/testing-fixtures.md` › 1.7 `monkeypatch` (`setenv`, vá `datetime`, tự hoàn lại), › 1.8 (test phụ thuộc thứ tự), › 1.3 scope, › 1.5 autouse; `testing-organization.md` › 2 `tmp_path` | `references/testing-fixtures.md` › 1.7; › 1.8; › 1.3; › 1.6 | Đạt |
| 4 | Hàm xử lý file log lớn, mỗi dòng tạo nhiều object nhỏ, chậm và memory tăng dần. Đổi sang `__slots__`, `functools.lru_cache` hay `dataclass(slots=True)`? Đo trước bằng `cProfile`/`tracemalloc` thế nào? | `references/generators-concurrency-performance.md` › 3.1 `__slots__`, › 3.3 `lru_cache`, › 3.4 `cProfile`/`tracemalloc`; `references/type-hints-and-dataclasses.md` › 2.1 `dataclass(slots=True)` | `references/generators-concurrency-performance.md` › 3.4; › 3.1; › 3.3; › 1.3 | Đạt |
| 5 | Module có class kế thừa nhiều tầng, `isinstance` khắp nơi, import vòng giữa `models.py` và `services.py`. Refactor theo composition hay `Protocol`, gỡ circular import thế nào mà không phá API? | `references/type-hints-and-dataclasses.md` › 3 (composition thay vì kế thừa, `Protocol`, giữ API) + `references/packaging-and-tooling.md` › 6 (vòng import: tách module, `TYPE_CHECKING`, đảo phụ thuộc, import cục bộ) | `references/type-hints-and-dataclasses.md` › 3. Ghép (composition) thay vì kế thừa nhiều tầng; `references/packaging-and-tooling.md` › 6. Vòng import | Đạt |
| 6 | Server Python sinh stack trace dài ở production; thiết kế hệ exception riêng (`DomainError`, `NotFoundError`, `ValidationError`), khi nào wrap/re-raise, log ở tầng nào để không trùng, retry backoff cho lỗi tạm thời từ database | mục khác: skill `error-handling` | mục khác: `error-handling` (từ `SKILL.md` › 8 và `errors-context-decorators.md` › 1.3), kèm `silent-failure-hunter` | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có. Dòng trỏ `method/standards/python.md` đã thêm ở `SKILL.md` mục 3 (file đó có khi gộp làn chuẩn).
- Chủ thể nêu: không có mục riêng giải thích hai lỗi mypy strict ở câu 2 và không nhắc `overload`; phần đọc biến môi trường vào `Config` không phủ riêng (câu 1).
- Nguồn của phần thêm ở `TK11.5`: Python Packaging User Guide (`[project.scripts]`), tài liệu uv (build), tài liệu pytest (`monkeypatch`), tài liệu Python (`functools`, `cProfile`, `tracemalloc`, `typing`).
