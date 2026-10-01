---
skill: id-convention
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: sonnet (both runs, same scenario text)
date: 2026-10-01
result: 3/3 GREEN pass
---

# Thử áp lực — id-convention

> **Kết luận:** 3/3 kịch bản: không có skill thì agent tự chế tiền tố (`V1`, `R1`, `Q1`, `YC2`, `TC1`,
> `FD`, `DC`, `LO`, `TK3a`), đánh số lại, gạch ngang mục bỏ, mở `BR` cho lỗi ngoài phạm vi; có skill thì
> đúng bảng mã, giữ số, `TK3.1/TK3.2`, `RQ-` cho lỗi ngoài phạm vi, mọi mã kèm tên.

**Giới hạn của phép thử:** kịch bản thứ hai ban đầu (tóm tắt trạng thái trong chat với mã đã kèm tên
trong đề bài) nền đã đạt sẵn, bị thay bằng kịch bản cấp mã mới.

## ID1 — Viết bảng việc + rủi ro + quyết định cho PLAN

**Áp lực:** SPEC được mô tả bằng lời ("yêu cầu chức năng số 2, kịch bản 2.1…"), không cho sẵn mã; việc
thứ 4 bị bỏ; cần ưu tiên.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — mã `V1`–`V5`, `R1`–`R3`, `Q1`; trỏ spec bằng `YC2`, `TC1` (tự chế); ưu tiên "Cao / Trung bình"; việc bỏ viết `~~gạch ngang~~` và "(không giao)"; vai "Developer/Tester" | 6 loại lỗi trong một bảng |
| GREEN | **Đạt** — `TK1 (sinh PDF hóa đơn thường)` … `TK5`; trỏ `FR2.1 (…)`, `SC2 (…)`; ưu tiên "Bắt buộc / Không làm đợt này"; `TK4` giữ mã, trạng thái `bỏ`, ghi "việc mới sẽ nhận TK6"; `RK1`–`RK3`, `DN1 (cách sinh PDF)` có bảng phương án | còn dùng "Developer/Tester" thay vì Implementer/QA — ngoài phạm vi skill này, thuộc `roles/` |

## ID2 — Cấp mã mới trong PROGRESS cho ba sự kiện

**Áp lực:** lỗi ngoài phạm vi, một điều chỉnh tự quyết, tách `TK3` với một quyết định mới cần người;
người dùng dặn "ghi nhanh, anh không đọc đâu".

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — tách thành `TK3a`/`TK3b`; lỗi ngoài phạm vi mở `BR2` (không chặn gì); phán quyết ghi thành `RK4` mới và không có dòng `Phán quyết:`; 5 bảng cho 3 sự kiện | tiền tố tự chế + sai loại mục |
| GREEN | **Đạt** — lỗi ngoài phạm vi → `RQ-<kế tiếp>` trong REQUESTS, "không mở BR vì không buộc dừng"; dòng `Phán quyết: chọn WeasyPrint … — vì … — nếu sai tốn nửa ngày`; `TK3.1`/`TK3.2`; `DN2` kế tiếp; "không đặt RK mới"; từ chối đoán số `RQ-` vì chưa mở sổ | đúng mục 4 của skill |

## ID3 — Review đoạn REPORT có mã sai

**Áp lực:** đoạn trích có `V1`, `P1` "mức cao", `D3`→`D4` đánh số lại, `US-004`, `SP-2026-03`, `A7`,
`L1`; reviewer phải liệt kê lỗi và viết lại.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** — bắt được mã một chữ cái và đánh số lại, nhưng tự chế `FD`, `DC`, `LO`; không biết `SPR-`/`RQ-`; để `A7` trần | thiếu bảng mã nên "sửa" thành lỗi mới |
| GREEN | **Đạt** — `VR1`–`VR3`, `RF1 (…) — Phải sửa`, `RF2 — Nên sửa`, `DN3` giữ mã trạng thái `bỏ` + `DN4` giữ nguyên, `SPR-03`, `US4` hoặc `RQ-004` (nêu hai khả năng, không đoán), `` `A7` (lõi sạch, khuôn chuẩn hóa repo) ``, `CO1 (nâng cấp thư viện PDF)`; ghi chỗ cần người xác nhận | 10 lỗi liệt kê có căn cứ mục của skill |

## Lỗ hổng đã vá sau RED (REFACTOR)

- Mục 4 "Cấp mã mới": việc con `TK3.1` (cấm `TK3a`), lỗi ngoài phạm vi → `RQ-` không `BR`, phán quyết
  không có mã (vá ID2).
- Mục 5 bảng "Cấm — sửa thành" liệt kê đúng các tiền tố tự chế đã gặp (`YC`, `TC`, `FD`, `DC`, `LO`) và
  mã kiểu `SP-2026-03`, `US-004` (vá ID1, ID3).
- Mục 3: mã hệ thống ngoài trong dấu code **và** kèm tên + nguồn (vá ID3).

## Chạy lại

Như `response-style/tests/pressure.md`: prompt tự chứa, RED không skill, GREEN thêm dòng "đọc
`skills/id-convention/SKILL.md` trước". Chấm theo cột "Bằng chứng".
