---
skill: python
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 7b7a392d29eb80d8187a564d76f03cf0979cb720
date: 2026-10-03
result: pass 6/6
---

Đã đọc: `<gốc worktree>\skills\python\SKILL.md`

# Thử truy xuất — python

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥5/6). Bảng "Đọc gì khi nào" của `SKILL.md` chỉ đúng tệp `references/` cho năm câu tình
> huống; chủ thể mở năm trong tám tệp `references/` và không đọc lan. Câu ranh giới (test trước) chủ thể trỏ vào `references/testing.md`
> rồi nhận đúng quy trình đầy đủ thuộc skill `tdd`.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Câu 6 là câu ranh giới: đáp án của
người soạn (`tdd`) đã được người chấm đối chiếu với `SKILL.md` mục 4 ("test viết trước code theo skill `tdd`") và
`description` của `tdd`, và nhận là đúng; `references/testing.md` mục 1.1 là bản tóm tắt cho Python nên cũng chấp nhận.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần
chi tiết phụ còn thiếu ghi ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được cho quyết định đó.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Module `utils.py` 900 dòng đang gộp đủ thứ, muốn tách thành package. Nên cấu trúc module và `__init__` ra sao? | `references/packaging-and-tooling.md` › 1. Bố cục dự án chuẩn, 3. Export ở `__init__.py` | `references/packaging-and-tooling.md` › 3. Export ở `__init__.py`, 1, 2 | Đạt |
| 2 | Dự án dùng pip thủ công, muốn chuyển sang uv cùng ruff và mypy. Cấu hình `pyproject.toml` và chạy kiểm tra nên thế nào? | `SKILL.md` › 3. Công cụ + `references/packaging-and-tooling.md` › 4. `pyproject.toml` | `references/packaging-and-tooling.md` › 4. `pyproject.toml`; `SKILL.md` › 3. Công cụ | Đạt (một phần: không có bước chuyển từ `requirements.txt` sang uv) |
| 3 | Test pytest có 12 case chỉ khác nhau đầu vào và kết quả mong đợi. Viết gọn bằng parametrization và fixture thế nào? | `references/testing-fixtures.md` › 2. Parametrize | `references/testing-fixtures.md` › 2. Parametrize (2.1, 2.2), 1. Fixture | Đạt |
| 4 | Hàm async gọi HTTP bên ngoài, cần test mà không gọi mạng thật. Mock như thế nào và test async chạy bằng gì? | `references/testing-mocking-async.md` › 1. Mock và patch, 2. Test code async | `references/testing-mocking-async.md` › 2.3, 2.1, 1, 1.5 | Đạt (một phần: không nêu mock riêng cho client HTTP) |
| 5 | Review đoạn Python dùng default mutable argument và bắt `except:` trần. Những điểm nào cần sửa và theo idiom nào? | `SKILL.md` › 7. Phản mẫu (+ `references/errors-context-decorators.md` › 1) | `SKILL.md` › 7. Phản mẫu cần tránh; `references/errors-context-decorators.md` › 1.1 | Đạt |
| 6 | Cần viết hàm `parse_invoice` theo kiểu viết test thất bại trước rồi mới code. Quy trình đỏ-xanh-refactor đó nằm ở đâu? | mục khác: skill `tdd` (chấp nhận `references/testing.md` › 1.1) | `references/testing.md` › 1.1, và mục khác: `tdd` cho quy trình đầy đủ | Đạt |

## Thiếu nội dung / mâu thuẫn

- `skills/python/SKILL.md:79-95` (mục 3) và `skills/python/references/packaging-and-tooling.md:67-110`: có lệnh và cấu hình cho dự án đã dùng uv, không có đường chuyển một
  dự án pip và `requirements.txt` sang uv (câu 2). Đề xuất: một dòng nêu `uv init` rồi `uv add -r requirements.txt` và commit `uv.lock`.
- `skills/python/references/testing-mocking-async.md:107-154` (mục 2): có mock hàm async bằng `AsyncMock` nhưng không có chỉ dẫn mock ở tầng HTTP (câu 4), chủ thể phải
  tự suy. Đề xuất: một ví dụ mock transport của client HTTP đang dùng, hoặc trỏ sang skill `fastapi` mục test.
- Không có mâu thuẫn; `references/testing.md` mục 1.1 và skill `tdd` bổ sung cho nhau.
