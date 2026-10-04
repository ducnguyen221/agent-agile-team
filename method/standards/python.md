---
title: Python standard — short rules
type: method
status: active
updated: 2026-10-04
---

<!-- Nguồn: affaan-m/ECC rules/python/{coding-style,patterns,security,testing,fastapi}.md @ ef648e01 (MIT). Viết
     lại, giữ ý; bộ công cụ theo skill `python` (ruff thay black + isort); bỏ `hooks.md` của nguồn (cấu hình
     runtime của nguồn). -->

# Chuẩn Python

> **Kết luận:** Python theo PEP 8, có type hint trên mọi chữ ký hàm, dữ liệu mặc định bất biến, bộ công cụ **uv +
> ruff + mypy + pytest**, secret từ môi trường, coverage **80 % code mới/sửa**. Chuẩn này giữ luật ngắn; mẫu
> code, lý do và ví dụ nằm ở skill `python` (và `fastapi`, `error-handling`, `tdd`). Bổ sung cho luật chung
> trong `common/`.

## Phong cách

- Theo **PEP 8**.
- **Type hint trên mọi chữ ký hàm**; kiểu kiểm bằng `mypy`.
- Định dạng và lint bằng `ruff` (`ruff format`, `ruff check`, gồm sắp xếp import); không thêm công cụ định dạng
  thứ hai. Cấu hình công cụ không bị sửa để qua kiểm (`AGENTS.md`).
- Dữ liệu bất biến: `@dataclass(frozen=True)` hay `NamedTuple` cho kiểu giá trị; không dùng giá trị mặc định
  khả biến cho tham số.
- Bắt ngoại lệ **cụ thể**, nối lỗi với ngữ cảnh; không `except` trần nuốt lỗi (skill `error-handling`).

## Mẫu

- Duck typing có kiểu bằng `Protocol` cho ranh giới giữa các tầng (ví dụ repository).
- `dataclass` cho đối tượng truyền dữ liệu (DTO); kiểm hợp lệ ở biên bằng schema khi dùng web framework.
- Tài nguyên (file, kết nối, khoá) qua **context manager** (`with`); xử lý dữ liệu lớn bằng generator.
- Chi tiết: skill `python` (type hint, ngoại lệ, decorator, generator, đóng gói).

## Bảo mật

- Secret đọc từ biến môi trường và **lỗi to khi thiếu** (`os.environ["TÊN"]` thay vì giá trị mặc định); tệp `.env`
  chỉ dùng phát triển cục bộ, không commit, repo chỉ có `.env.example`.
- Quét tĩnh bằng bộ luật bảo mật của `ruff` (`ruff check --select S`) và audit phụ thuộc (`pip-audit`).
- Django: không có chuẩn riêng trong repo này; theo tài liệu bảo mật chính thức của Django.
- Danh mục chung: `common/security.md`.

## Kiểm thử

- Dùng **pytest**; test trước code (skill `tdd`).
- Đo coverage: `pytest --cov=<gói> --cov-report=term-missing`; ngưỡng **80 % code mới/sửa**
  (`common/testing.md`).
- Phân loại bằng `pytest.mark` (ví dụ `unit`, `integration`); đăng ký marker trong cấu hình để pytest không
  cảnh báo.
- Chi tiết fixture, mock, async: skill `python`, phần `references/testing*.md`.

## FastAPI

- Dựng app trong `create_app()`; router mỏng — logic nghiệp vụ và truy cập dữ liệu vào service hay hàm CRUD.
- Tách schema yêu cầu tạo, cập nhật và phản hồi; **không bao giờ** đưa mật khẩu, hash, token hay trạng thái xác
  thực nội bộ vào response; dùng `response_model` cho endpoint trả dữ liệu ứng dụng.
- Phiên cơ sở dữ liệu và xác thực đi qua `Depends`; không tạo phiên hay client sống lâu trong handler.
- `async def` cho endpoint làm I/O với thư viện async; không gọi `requests`, phiên SQLAlchemy đồng bộ hay thao
  tác file/mạng chặn trong route async.
- CORS theo từng môi trường, không dấu `*` cùng thông tin xác thực; JWT kiểm hạn, issuer, audience, thuật toán;
  giới hạn tần suất cho xác thực và ghi nặng; không đưa thông tin xác thực, cookie, header `Authorization` vào log.
- Test ghi đè đúng hàm mà `Depends` tham chiếu, xoá ghi đè sau test; ưu tiên client test async cho app async.
- Mẫu và checklist: skill `fastapi`; agent `fastapi-reviewer`.

## Xem thêm

Skill `python`, `fastapi`, `postgres`, `error-handling`, `tdd`; agent `python-reviewer`,
`silent-failure-hunter`.
