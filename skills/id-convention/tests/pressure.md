---
skill: id-convention
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: sonnet (RED/GREEN/original of 2026-10-01); claude-sonnet-5-5 (GREEN rerun of 2026-10-04)
date: 2026-10-22
result: 3/3 GREEN pass; GREEN rerun 2026-10-22 3/3 pass on the tree at HEAD 61ba051 (SPR-31 TK6, skill body gained the pre-gate-1 TK renumbering exception); earlier rerun 2026-10-04 3/3 pass on 05032b4
tier: T3
skill_sha: eda840c67312735265977e8973637114be8369e9
agent_ids:
  green_rerun_2026_10_04: {idc-1: a8dd30ce5a179ac73, idc-2: a9e3e87063dc127a8, idc-3: ad46e35a2016c4733}
  green_rerun_2026_10_22: {idc-1: a36383306ad2b27b9, idc-2: a52a4d3efd751748e, idc-3: afc4749b0ead27ecc}
---

# Thử áp lực — id-convention

> **Kết luận:** 3/3 kịch bản: không có skill thì agent tự chế tiền tố (`V1`, `R1`, `Q1`, `YC2`, `TC1`,
> `FD`, `DC`, `LO`, `TK3a`), đánh số lại, gạch ngang mục bỏ, mở `BR` cho lỗi ngoài phạm vi; có skill thì
> đúng bảng mã, giữ số, `TK3.1/TK3.2`, `RQ-` cho lỗi ngoài phạm vi, mọi mã kèm tên.

**Giới hạn của phép thử:** kịch bản thứ hai ban đầu (tóm tắt trạng thái trong chat với mã đã kèm tên
trong đề bài) nền đã đạt sẵn, bị thay bằng kịch bản cấp mã mới.

## Kịch bản 1 — Viết bảng việc + rủi ro + quyết định cho PLAN

**Áp lực:** SPEC được mô tả bằng lời ("yêu cầu chức năng số 2, kịch bản 2.1…"), không cho sẵn mã; việc
thứ 4 bị bỏ; cần ưu tiên.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — mã `V1`–`V5`, `R1`–`R3`, `Q1`; trỏ spec bằng `YC2`, `TC1` (tự chế); ưu tiên "Cao / Trung bình"; việc bỏ viết `~~gạch ngang~~` và "(không giao)"; vai "Developer/Tester" | 6 loại lỗi trong một bảng |
| GREEN | **Đạt** — `TK1 (sinh PDF hóa đơn thường)` … `TK5`; trỏ `FR2.1 (…)`, `SC2 (…)`; ưu tiên "Bắt buộc / Không làm đợt này"; `TK4` giữ mã, trạng thái `bỏ`, ghi "việc mới sẽ nhận TK6"; `RK1`–`RK3`, `DN1 (cách sinh PDF)` có bảng phương án | còn dùng "Developer/Tester" thay vì Implementer/QA — ngoài phạm vi skill này, thuộc `roles/` |

## Kịch bản 2 — Cấp mã mới trong PROGRESS cho ba sự kiện

**Áp lực:** lỗi ngoài phạm vi, một điều chỉnh tự quyết, tách `TK3` với một quyết định mới cần người;
người dùng dặn "ghi nhanh, anh không đọc đâu".

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — tách thành `TK3a`/`TK3b`; lỗi ngoài phạm vi mở `BR2` (không chặn gì); phán quyết ghi thành `RK4` mới và không có dòng `Phán quyết:`; 5 bảng cho 3 sự kiện | tiền tố tự chế + sai loại mục |
| GREEN | **Đạt** — lỗi ngoài phạm vi → `RQ-<kế tiếp>` trong REQUESTS, "không mở BR vì không buộc dừng"; dòng `Phán quyết: chọn WeasyPrint … — vì … — nếu sai tốn nửa ngày`; `TK3.1`/`TK3.2`; `DN2` kế tiếp; "không đặt RK mới"; từ chối đoán số `RQ-` vì chưa mở sổ | đúng mục 4 của skill |

## Kịch bản 3 — Review đoạn REPORT có mã sai

**Áp lực:** đoạn trích có `V1`, `P1` "mức cao", `D3`→`D4` đánh số lại, `US-004`, `SP-2026-03`, `A7`,
`L1`; reviewer phải liệt kê lỗi và viết lại.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** — bắt được mã một chữ cái và đánh số lại, nhưng tự chế `FD`, `DC`, `LO`; không biết `SPR-`/`RQ-`; để `A7` trần | thiếu bảng mã nên "sửa" thành lỗi mới |
| GREEN | **Đạt** — `VR1`–`VR3`, `RF1 (…) — Phải sửa`, `RF2 — Nên sửa`, `DN3` giữ mã trạng thái `bỏ` + `DN4` giữ nguyên, `SPR-03`, `US4` hoặc `RQ-004` (nêu hai khả năng, không đoán), `` `A7` (lõi sạch, khuôn chuẩn hóa repo) ``, `CO1 (nâng cấp thư viện PDF)`; ghi chỗ cần người xác nhận | 10 lỗi liệt kê có căn cứ mục của skill |

## Lỗ hổng đã vá sau RED (REFACTOR)

- Mục 4 "Cấp mã mới": việc con `TK3.1` (cấm `TK3a`), lỗi ngoài phạm vi → `RQ-` không `BR`, phán quyết
  không có mã (vá kịch bản 2).
- Mục 5 bảng "Cấm — sửa thành" liệt kê đúng các tiền tố tự chế đã gặp (`YC`, `TC`, `FD`, `DC`, `LO`) và
  mã kiểu `SP-2026-03`, `US-004` (vá kịch bản 1, 3).
- Mục 3: mã hệ thống ngoài trong dấu code **và** kèm tên + nguồn (vá kịch bản 3).

## GREEN chạy lại (2026-10-04, SPR-04 `TK11.10`)

Nợ `RF100`/`CO3`: file này ngày 2026-10-01 chưa có `skill_sha` và `tier`. Thân skill **không đổi** từ lúc thử, nên chỉ chạy lại GREEN **cả ba kịch bản** trên cây ở HEAD `05032b4` (`skill_sha` ở frontmatter) và ghi `skill_sha` + `tier`. Kịch bản: `tests/scenarios.txt` mới (prompt dựng lại từ mô tả ở lượt trước: các lượt trước chỉ lưu mô tả, không lưu nguyên văn). Chủ thể là subagent mới, model `claude-sonnet-5-5`, tier T3, không dùng công cụ Skill, đường tuyệt đối tới `SKILL.md` trong worktree làn D, báo cáo mở bằng "Đã đọc:"; vế "KHÔNG đọc file nào trên máy" ở phần mở đầu đổi thành "ngoài các file nêu ở dòng dưới" (chỉ lượt GREEN). Kỳ vọng viết ra trước khi giao (file nháp `.tmp/green5-expected.md`, mtime `2026-10-04 08:50:35 +0700`). Mỗi chủ thể dùng 2 lượt công cụ (một lần đọc `SKILL.md`, một lần trả kết quả).
Bài trả lời của các lượt và bảng chấm: `evidence/TK11/id-convention-green.md` trong hồ sơ sprint `SPR-04` của lớp riêng.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| IDC-1 | `a8dd30ce5a179ac73` | **Đạt** | `TK1 (…)`–`TK5` kèm tên ngắn; `TK4` giữ mã, trạng thái `bỏ`, "việc mới kế tiếp là TK6"; `RK1`, `RK2`; `DN1 (…)` có bảng phương án và khuyến nghị; trỏ SPEC bằng `FR2.1`, `FR2.2`, `FR3` kèm tên; ưu tiên "Bắt buộc / Không làm đợt này" kèm ASSUMPTION; không `P1/P2`, không gạch ngang |
| IDC-2 | `a9e3e87063dc127a8` | **Đạt** | lỗi ngoài phạm vi → `RQ-<số kế tiếp>` ở REQUESTS, không `BR`, không đoán số vì chưa biết sổ; dòng `Phán quyết: … — … — sai thì tốn nửa ngày` không có mã; `TK3.1`/`TK3.2` (không `TK3a`); `DN2` kế tiếp `DN1`; nêu tài liệu của từng dòng |
| IDC-3 | `ad46e35a2016c4733` | **Đạt** | bắt `V1`–`V3`, `P1`/`P2`, "mức cao", `D3`→`D4` đánh số lại, `US-004`, `SP-2026-03`, `A7`, `L1`; viết lại `VR1`–`VR3`, `RF1`/`RF2`, `DN3` giữ mã trạng thái `bỏ` + `DN4`, `SPR-03`, `US4` hoặc `RQ-004` (nêu hai khả năng), `` `A7` `` kèm tên và nguồn, `CO1`; liệt kê chỗ cần Analyst xác nhận |

Kết quả: 3/3 Đạt; không sửa `SKILL.md`, không REFACTOR. Một mẫu mỗi kịch bản (chưa đo độ phân tán).

## GREEN chạy lại (2026-10-22, SPR-31 `TK6`)

Thân skill đổi ở `61ba051`: Kết luận và mục 6 bước 5 nhắc ngoại lệ, mục 4 thêm một gạch "Ngoại lệ đánh số `TK` trước Cổng 1". `skill_sha` cũ lệch cây nên chạy lại GREEN cả ba kịch bản trên cây ở HEAD `61ba051` (prompt nguyên văn `tests/scenarios.txt`, cùng phép thay vế mở đầu như lượt 2026-10-04; chủ thể subagent mới, `sonnet`, `claude-sonnet-5-5`, tier T3, không công cụ Skill, đường tuyệt đối tới `SKILL.md` trong worktree, mở bằng "Đã đọc:"). Kết quả: **IDC-1 Đạt** (`a3638330`: `TK4` giữ mã, trạng thái `bỏ`, không đánh số lại `TK5`; ưu tiên bằng chữ), **IDC-2 Đạt** (`a52a4d3e`: `RQ-` cho lỗi ngoài phạm vi, `Phán quyết:` không mã, `TK3.1`/`TK3.2`, `DN2`), **IDC-3 Đạt** (`afc4749b`: bắt đủ `V1`–`V3`, `P1`/`P2`, "mức cao", `D3`→`D4` đánh số lại, `US-004`, `SP-2026-03`, `A7`, `L1`; ngoại lệ trước Cổng 1 không bị viện nhầm vì REPORT đã sau Cổng 1). 3/3 Đạt, không RED mới (RED lịch sử giữ nguyên), một mẫu mỗi kịch bản. Output nguyên văn: `evidence/tk6/idc-green-rerun.md` trong hồ sơ sprint SPR-31 của lớp riêng.

## Chạy lại

Như `response-style/tests/pressure.md`: prompt tự chứa, RED không skill, GREEN thêm dòng "đọc
`skills/id-convention/SKILL.md` trước". Chấm theo cột "Bằng chứng".

Prompt nguyên văn ở `tests/scenarios.txt` (dựng lại từ mô tả ở SPR-04 `TK11.10`). Phép thay vế mở đầu ở lượt GREEN: phần mở đầu mỗi kịch bản nói "KHÔNG đọc file nào trên máy", mâu thuẫn với dòng GREEN bảo đọc `SKILL.md`; khi gửi GREEN đổi vế đó thành "KHÔNG đọc file nào trên máy, ngoài các file nêu ở dòng trên" (lượt 2026-10-04 gửi chữ "dòng dưới" vì dòng [PHA] đặt sau phần mở đầu; nghĩa như nhau). Lượt RED giữ nguyên văn.
