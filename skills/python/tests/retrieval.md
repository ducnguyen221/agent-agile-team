---
skill: python
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 7b7a392d29eb80d8187a564d76f03cf0979cb720
date: 2026-10-03
result: pass 5/6, 3 partial, 1 fail
agent_ids:
  questions: ac46369732a234a3c
  answers: a02a54beb6e10d326
---

Đã đọc: `<gốc worktree>\skills\python\SKILL.md` (và các file trong `references/` mà `SKILL.md` trỏ tới, nếu có)

# Thử truy xuất — python

> **Kết luận:** 5/6 câu Đạt (ngưỡng ≥4/5 câu tình huống và câu ranh giới): câu 1, 2, 4 chỉ Đạt một phần, câu 3 Đạt, **câu 5 Không đạt vì thiếu nội dung** (coverage). Câu ranh giới
> (câu 6) chủ thể trỏ đúng `fastapi`. Chủ thể đọc 7 file, trả lời trung thực: ở mọi chỗ skill thiếu (TypedDict, `Literal`, `frozen`, `itertools`, `Semaphore`,
> `ParamSpec`, branch coverage, `fail_under`) đều nói "skill không có" thay vì bịa. Điểm đáng báo cáo nhất: `description` hứa "coverage" mà skill chỉ có cờ `term-missing`
> và ngưỡng 80 % theo dòng, không có branch coverage hay `fail_under`.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực, kèm danh sách chủ đề của bộ cũ để không lặp); lượt này là **bộ câu mới** chạy lại sau khi `X2` đổi nội dung skill
(chạy lại theo giao thức rerun-2). Cột "Mục kỳ vọng" do người chấm ghi vào file nháp **trước khi** giao chủ thể (mtime file nháp 2026-10-03 21:40:39 +0700 (21:40:39,47), sớm hơn lệnh giao chủ thể đầu tiên); mục kỳ vọng ghi theo cây MỚI.
Câu 6 là câu ranh giới, đáp án do người soạn nêu và người chấm đối chiếu với `description` của skill đáp.
Nguyên văn câu hỏi của người soạn, file nháp kỳ vọng, output TRỌN của chủ thể (đường dẫn thư mục người dùng giữ nguyên ở đó, còn ở đây lược thành `<gốc worktree>` vì repo chặn tên người dùng)
và số lượt công cụ: hồ sơ sprint của lớp riêng, `evidence/TK12-green/python-retrieval-rerun-2.md`.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần chi tiết phụ còn thiếu ghi trong ngoặc và ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được.
Ngưỡng: ≥4/5 câu tình huống Đạt và câu ranh giới Đạt. `result` ghi cả số "một phần".

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Hàm xử lý đơn hàng nhận dict lồng nhau, field nào cũng có thể thiếu/None, hay `KeyError` và mypy báo loạn. Chuyển sang dataclass hoặc TypedDict kèm type hint chặt, Optional, `Literal` cho trạng thái, frozen/slots: thiết kế kiểu thế nào? | `references/type-hints-and-dataclasses.md` › 1. Type hint + › 2. Dataclass; `Literal`, TypedDict, `frozen` không có trực tiếp (`__slots__` ở `generators-concurrency-performance.md` › 3.1) | `references/type-hints-and-dataclasses.md` › 1.2, › 2.1, › 2.2; `SKILL.md` › 2.2, › 7; `generators-concurrency-performance.md` › 3.1 | Đạt (một phần: có dataclass, `X | None`, `field(default_factory)`, `__post_init__`, `slots=True`; không có TypedDict, `Literal`, `frozen=True`, cách chuyển dict lồng nhau) |
| 2 | ETL đọc CSV 4 GB bằng `pandas.read_csv().to_dict()` hết RAM. Viết lại thành generator từng dòng, lọc, gom batch 10k dòng; generator pipeline và `itertools`/`yield from` thế nào? | `references/generators-concurrency-performance.md` › 1.3 Hàm generator cho dữ liệu lớn (+ › 1.2); `itertools`/`yield from`/batch không có | `generators-concurrency-performance.md` › 1.2, › 1.3; `SKILL.md` › 6; `errors-context-decorators.md` › 2.1 | Đạt (một phần: có nguyên tắc lười, hàm `yield` trong `with open`; không có `itertools`/`islice`, `yield from`, module `csv`, ghép pipeline) |
| 3 | Gọi 200 API ngoài đang tuần tự 6 phút. asyncio + `gather` + Semaphore 20 kết nối, ThreadPoolExecutor hay multiprocessing? Một phần HTTP, một phần parse JSON nặng CPU. | `references/generators-concurrency-performance.md` › 2. Đồng thời (bảng chọn; 2.1, 2.2, 2.3 có `gather`); Semaphore không có | `generators-concurrency-performance.md` › 2. Đồng thời, › 2.1, › 2.2, › 2.3 | Đạt (bảng chọn trả lời đúng quyết định; không có `Semaphore` và `run_in_executor`, chủ thể ghi rõ) |
| 4 | Decorator `@retry(times=3)` có tham số, bọc cả hàm sync lẫn async, giữ tên/docstring/type hint (ParamSpec). Thêm context manager đo thời gian: `contextlib.contextmanager` hay class `__enter__/__exit__`? | `references/errors-context-decorators.md` › 3.2 Decorator có tham số (+ `functools.wraps`) và › 2.2, › 2.3; `ParamSpec`, bọc hàm async không có | `errors-context-decorators.md` › 3.1, › 3.2, › 2.2, › 2.3 | Đạt (một phần: có decorator ba tầng + `wraps` và mẫu `timer` bằng `@contextmanager`; không có `ParamSpec`, không bọc hàm async, không backoff; trỏ `error-handling` cho retry) |
| 5 | CI báo coverage 91% nhưng nhánh `except` và `if __name__ == "__main__"` chưa chạy. Bật branch coverage, đặt `fail_under` trong pyproject, loại trừ đúng chỗ, và 91% có đáng tin không? Cấu hình pytest-cov thế nào? | `references/testing.md` › 1.2 Coverage (+ `SKILL.md` › 4; `packaging-and-tooling.md` › 4); branch coverage / `fail_under` / loại trừ có thể không có | `SKILL.md` › 3, › 4; `testing.md` › 1.2; `testing-organization.md` › 6; `packaging-and-tooling.md` › 4 | **Không đạt (thiếu nội dung)**: skill chỉ có `--cov-report=term-missing`, ngưỡng 80 % theo dòng (đặt ngoài skill), "coverage là điều kiện cần, không đủ"; không có branch coverage, `fail_under`, `exclude_lines` |
| 6 | `POST /orders` trả 500 khi body sai thay vì 422. Dùng FastAPI + Pydantic, muốn dependency lấy session DB và mapping lỗi nghiệp vụ sang response thống nhất. Bắt đầu từ đâu? | mục khác: skill `fastapi` | mục khác: `fastapi` (kèm `error-handling`, `api-design`, `debugging`, `fastapi-reviewer`) | Đạt (ranh giới) |

## Thiếu nội dung / mâu thuẫn

- **Thiếu nội dung, quan trọng (câu 5).** `description` hứa "coverage" (`skills/python/SKILL.md:3`); `SKILL.md` mục 4 và `references/testing.md` mục 1.2 chỉ có
  `--cov-report=term-missing` và ngưỡng mặc định 80 % **dòng** ở `method/conventions.md`. Không có: bật branch coverage (`--cov-branch` hoặc `[tool.coverage.run] branch = true`), `fail_under`
  trong `[tool.coverage.report]`, `exclude_lines` cho `if __name__ == "__main__"`, cách đọc 91 % theo dòng khi nhánh `except` chưa chạy. Đề xuất (điều phối quyết, đổi `skill_sha`):
  thêm mục "Coverage theo nhánh" khoảng 10 dòng vào `references/testing.md` (hoặc `testing-organization.md` mục 6), hoặc bỏ "coverage" khỏi `description`.
- **Thiếu nội dung, nhẹ.** `type-hints-and-dataclasses.md`: không `TypedDict`, `Literal`, `frozen=True` (câu 1). `generators-concurrency-performance.md`: không `itertools`/`yield from`/batch (câu 2),
  không `Semaphore` (câu 3). `errors-context-decorators.md`: không `ParamSpec`, không decorator bọc hàm async (câu 4).
- Không có mâu thuẫn giữa các file trong bảy file chủ thể đọc.
