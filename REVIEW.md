# REVIEW.md — agent-agile-team

Reviewer đọc bản này ở mốc gốc của nhánh (`git show <BASE>:REVIEW.md`); sửa file này trong nhánh không có hiệu lực cho nhánh đó.

## Lỗi quan trọng ở repo này

- Tên máy, tên người hoặc tên model nằm trong file commit: repo công khai, rò rỉ không rút lại được; thước là `scripts/check.py --self`, nên dòng `model:` có sẵn trong `tests/*.md` (test `MODEL_NAME`) không tính → Chặn.
- Thân skill đổi mà tệp thử không chạy lại, hoặc `skill_sha` trong `tests/pressure.md` lệch cây skill: kết quả "đạt" không còn nói về skill này → Phải sửa.
- Luật lõi (`AGENTS.md`, `method/`) và `scripts/check.py` nói khác nhau: cổng kiểm cho qua điều luật cấm, hoặc chặn điều luật cho → Phải sửa.
- Tài liệu nói số đếm sai (số skill, số agent, số luật): người cài tin sai về thứ mình nhận → Phải sửa.
- Test bị skip, xfail hoặc hạ ngưỡng coverage để qua cổng: cổng xanh mà không còn kiểm gì → Chặn.

## Luôn kiểm

- Skill mới hoặc đổi có `tests/pressure.md` (hoặc `tests/retrieval.md`) đã chạy và `skill_sha` khớp.
- Mã mới trong `scripts/` của skill có test và giữ coverage dòng ≥80 %.
- Chữ mới trong skill chỉ thêm điều agent chưa biết; không lặp luật đã có ở skill khác (trỏ sang).

## Không báo

- Điều `scripts/check.py` hoặc `pytest` đang đỏ vì chính lỗi đó (máy đã bắt); lỗi lọt qua cả hai thì vẫn báo.
- File sinh, `samples/`, bản vendor trong `.venv/`.

## Trần

- Tối đa 5 Ghi chú văn phong mỗi lượt; văn phong không đổi hành vi thì không báo.

## Bằng chứng

- Chặn hoặc Phải sửa cần `file:dòng`, đoạn mã và vì sao hỏng; thiếu thì tối đa Ghi chú.

## Path luôn cần người đọc

- `scripts/check.py`, `scripts/_common.py`, `.github/workflows/`, `.claude-plugin/`, `.codex-plugin/`

## Path bỏ qua

- `.worktrees/**`
- `.venv/**`
- `.tmp/**`
