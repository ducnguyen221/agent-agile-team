# Lần ngược tới nguyên nhân gốc

> **Kết luận:** lỗi hay lộ ra sâu trong call stack (khởi tạo repo sai thư mục, file tạo sai chỗ, DB mở sai
> đường dẫn). Bản năng là sửa ở nơi lỗi hiện ra — đó là sửa triệu chứng. Lần ngược chuỗi gọi tới **tác
> nhân ban đầu**, sửa ở đó, rồi thêm chặn ở các tầng (`defense-in-depth.md`).

Dùng khi: lỗi xảy ra sâu trong luồng chạy (không ở điểm vào); stack trace dài; không rõ dữ liệu sai sinh
ra ở đâu; cần biết test/đoạn mã nào gây ra vấn đề.

## 1. Quy trình

1. **Quan sát triệu chứng.** Ví dụ: `git init failed in <repo>/packages/core`.
2. **Tìm nguyên nhân trực tiếp** — dòng mã nào gây ra nó:
   ```python
   subprocess.run(["git", "init"], cwd=project_dir, check=True)
   ```
3. **Hỏi: ai gọi dòng này?**
   ```
   WorktreeManager.create_session_worktree(project_dir, session_id)
     ← Session.initialize_workspace()
     ← Session.create()
     ← test gọi Project.create()
   ```
4. **Lần tiếp lên — giá trị nào được truyền?** `project_dir = ""` (chuỗi rỗng). `cwd=""` bị hiểu thành thư
   mục hiện hành — chính là thư mục mã nguồn.
5. **Tìm tác nhân ban đầu — chuỗi rỗng đến từ đâu?**
   ```python
   context = setup_core_test()          # trả về {"temp_dir": ""} lúc mới tạo
   Project.create("name", context.temp_dir)  # đọc trước khi fixture kịp gán
   ```

Nguyên nhân gốc: biến cấp module đọc giá trị rỗng trước khi fixture chạy. Sửa ở nguồn: biến thành thuộc
tính ném lỗi nếu bị đọc trước fixture. Rồi thêm chặn ở các tầng (kiểm thư mục rỗng ở `Project.create`, ở
`WorkspaceManager`, chặn `git init` ngoài thư mục tạm khi đang test, log stack trước thao tác nguy hiểm).

**Không bao giờ chỉ sửa ở nơi lỗi hiện ra.** Lần một tầng lên được thì lần tiếp; tới nguồn thì sửa ở
nguồn; rồi chặn ở mỗi tầng. Hết đường lần (ngõ cụt) mới sửa ở điểm triệu chứng — và ghi rõ vì sao.

## 2. Gắn stack trace khi không lần tay được

```python
import os, sys, traceback

def git_init(directory: str) -> None:
    print("DEBUG git init:", {"directory": directory, "cwd": os.getcwd(),
          "env": os.environ.get("APP_ENV")}, file=sys.stderr)
    traceback.print_stack(file=sys.stderr)
    subprocess.run(["git", "init"], cwd=directory, check=True)
```

```bash
pytest -q -s 2>&1 | grep -A20 "DEBUG git init"
```

- Trong test, in ra **stderr** (logger có thể bị tắt hoặc bắt mất).
- Log **trước** thao tác nguy hiểm, không phải sau khi nó hỏng.
- Kèm ngữ cảnh: thư mục, cwd, biến môi trường liên quan (không in giá trị secret), thời điểm.
- Đọc stack: tìm tên file test, số dòng gây lời gọi, mẫu lặp (cùng test? cùng tham số?).

## 3. Tìm test gây ô nhiễm

Một file/thư mục lạ (ví dụ `.git` trong thư mục mã) xuất hiện khi chạy cả bộ test nhưng không rõ test nào
tạo → chạy từng file test một, dừng ở file đầu tiên làm nó xuất hiện:

```bash
python skills/debugging/scripts/find_polluter.py --check .git --glob "tests/**/test_*.py"
python skills/debugging/scripts/find_polluter.py --check .git --glob "src/**/*.test.ts" --cmd "npm test -- {file}"
```

Mặc định lệnh test là `python -m pytest -q {file}`; `{file}` được thay bằng đường dẫn từng file. Mã thoát:
`0` không tìm thấy, `1` tìm thấy (in tên test), `2` dùng sai tham số hoặc ô nhiễm đã có sẵn trước khi chạy.
Mỗi file có trần thời gian (`--timeout`, mặc định 600 giây). Chỉ cần Python 3 thư viện chuẩn; chạy được
trên Windows, macOS, Linux. Test của chính script: `python -m pytest skills/debugging/scripts -q`.
