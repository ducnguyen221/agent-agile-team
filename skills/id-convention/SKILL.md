---
name: id-convention
description: Use when writing or editing a sprint document or registry, assigning a code to a new item (task, risk, finding, blocker, decision, request, sprint), cross-referencing an item, mentioning a coded item in chat, or reviewing a document for bare, single-letter, invented or renumbered codes.
metadata:
  group: communication
  roles: [all]
---

# Chuẩn mã định danh

> **Kết luận:** mỗi loại mục có một tiền tố **hai chữ cái rút từ tên tiếng Anh**, thuộc đúng một tài
> liệu; hồ sơ trong sổ gốc có gạch nối và số tăng dần không tái dùng; mọi mã **luôn kèm tên ngắn** trong
> chat; cấm mã trần một chữ cái, cấm tự chế tiền tố, cấm đánh số lại, ưu tiên viết bằng chữ.

## 1. Luật đặt tiền tố

- Tên tiếng Anh **hai từ** → chữ đầu mỗi từ: Functional Requirement → `FR`, Review Finding → `RF`.
- Tên tiếng Anh **một từ** → chữ đầu + chữ cuối: Task → `TK`, Risk → `RK`, Decision → `DN`, Blocker → `BR`,
  Lesson → `LN`.
- Chữ sau tiền tố là số, không đệm (`TK4`, không `TK04`). Phân cấp bằng dấu chấm: `FR3.2` là kịch bản
  thứ hai của `FR3`; `TK2.3` là việc con thứ ba của `TK2`.
- **Không được** đặt tiền tố mới ngoài bảng ở mục 2. Cần loại mục mới → đề xuất người dùng thêm vào bảng
  (và vào `templates/README.md`), trước đó dùng mục gần nhất hoặc ghi bằng chữ.

## 2. Bảng mã — mỗi tiền tố thuộc đúng một tài liệu

| Tài liệu | Mã | Tên tiếng Anh | Nghĩa |
|---|---|---|---|
| SPEC | `US` | User Story | câu chuyện người dùng |
| SPEC | `FR` | Functional Requirement | yêu cầu chức năng; `FR3.2` = kịch bản KHI…THÌ… |
| SPEC | `SC` | Success Criterion | tiêu chí thành công đo được |
| SPEC | `CQ` | Clarification Question | câu hỏi cần làm rõ, hỏi một lần ở Cổng 1 |
| PLAN | `TK` | Task | việc; `TK2.3` = việc con |
| PLAN | `RK` | Risk | rủi ro |
| PLAN | `DN` | Decision | quyết định cần người dùng |
| PROGRESS | `BR` | Blocker | vướng mắc — chỉ cho 4 điều kiện dừng và cạn hạn mức tier |
| REPORT | `VR` | Verification Result | kết quả một phép kiểm |
| REPORT | `RF` | Review Finding | phát hiện của reviewer, có mức |
| REPORT | `LN` | Lesson | bài học |
| REPORT | `CO` | Carry-Over | việc để lại (gồm Nên sửa hoãn) |

**Hồ sơ trong sổ gốc** — lớp riêng, có gạch nối, số đệm theo cấu hình, tăng dần, **không tái dùng**:

| Sổ | Mã | Ví dụ |
|---|---|---|
| REQUESTS | `RQ-` | `RQ-014` — mọi yêu cầu, kể cả lỗi mới phát hiện ngoài phạm vi sprint |
| SPECS | `FS-` | `FS-007` — tính năng có spec sống |
| SPRINTS | `SPR-` | `SPR-12` |

**Ngoại lệ duy nhất có danh sách:** tên tier `T1` / `T2` / `T3` (không phải mã mục).

## 3. Ghi và nhắc chéo

| Tình huống | Viết |
|---|---|
| Ô mã trong bảng | `TK1 (hàm tra cứu đơn)` |
| Tiêu đề việc trỏ spec | `### TK1 — Hàm tra cứu đơn (→ FR1.1, SC1)` |
| Nhắc chéo trong cùng sprint | `TK4 → FR3.2` |
| Nhắc sang tài liệu khác | `FS-007/FR3.2`, `SPR-12/TK4` |
| Lần đầu trong một đoạn tài liệu, và **mọi lần** trong chat | mã + tên ngắn: `RF1 (API thiếu phân trang)` |
| Mã của hệ thống/tài liệu ngoài (`A7` của khuôn chuẩn hóa repo, `P1` của một tool) | trong dấu code **và** kèm tên + nguồn: `` `A7` (lõi sạch, khuôn chuẩn hóa repo) `` — công cụ kiểm không coi là mã của tài liệu |
| Ưu tiên | bằng chữ: **Bắt buộc / Nên có / Có thì tốt / Không làm đợt này** |
| Mức phát hiện | bằng chữ: Chặn / Phải sửa / Nên sửa / Ghi chú |

## 4. Cấp mã mới

- Số kế tiếp = số lớn nhất đã dùng + 1, **kể cả** mục đã bỏ. `TK4` bị bỏ thì việc mới là `TK6`, không
  phải `TK4` lần hai.
- Việc con tách từ `TK3` → `TK3.1`, `TK3.2` (không `TK3a`, không `TK3-1`, không `TK3'`).
- Lỗi/yêu cầu mới **ngoài phạm vi sprint** → dòng `RQ-` mới trong REQUESTS, trạng thái `mới`; trong
  PROGRESS chỉ ghi nhật ký trỏ tới `RQ-` đó. **Không** mở `BR` — `BR` chỉ cho điều phải dừng.
- Điều chỉnh tự quyết → dòng `Phán quyết:` trong nhật ký, **không có mã**; chỉ thành `RK` khi nó mở ra
  rủi ro mới cần theo dõi.
- Quyết định cần người dùng → `DN` kế tiếp trong PLAN (bảng Quyết định cần người), PROGRESS trỏ tới.
- Mục bị bỏ: **giữ nguyên mã**, cột trạng thái ghi `bỏ`, không gạch ngang tên, không xoá dòng, không đánh
  số lại các mục sau.

## 5. Cấm — và sửa thành

| Cấm | Sửa thành |
|---|---|
| Mã một chữ cái + số (`P1`, `S1`, `D3`, `L1`, `V2`, `R1`, `Q1`) | tiền tố hai chữ cái đúng tài liệu: `RF1`, `DN3`, `CO1`, `VR2`, `RK1`, `CQ1` |
| Tiền tố tự chế (`YC2`, `TC1`, `FD`, `DC`, `LO`, `BUG-3`, `TC-012`) | mã trong bảng mục 2: `FR2`, `SC1`, `RF`, `DN`, `CO`, `RQ-` |
| `P1`/`P2` cho ưu tiên | Bắt buộc / Nên có / Có thì tốt / Không làm đợt này |
| Mã sprint kiểu `SP-2026-03`, `US-004`, `REL-…` | `SPR-03`; `US4` (mục trong SPEC) hoặc `RQ-004` (hồ sơ sổ gốc) — tuỳ nó là gì |
| Đánh số lại khi bỏ mục | giữ số, trạng thái `bỏ` |
| Mã trần trong chat ("TK3 xong chưa?") | "TK3 (giao diện) xong chưa?" |
| "mức cao / mức thấp" | Chặn / Phải sửa / Nên sửa / Ghi chú |

## 6. Kiểm nhanh một tài liệu

1. Mọi mã có trong bảng mục 2 hoặc là `RQ-`/`FS-`/`SPR-`? Không → sửa, không đoán nghĩa.
2. Có mã một chữ cái + số ngoài dấu code? Có → Phải sửa.
3. Mã lần đầu trong đoạn có tên? Chat có tên ở mọi mã?
4. Nhắc chéo trỏ tới mục có thật (`TK` trỏ ít nhất một `FR`/`SC`)?
5. Có số bị tái dùng hay đánh số lại? Mục bỏ còn mã và trạng thái `bỏ`?
6. Mã hệ thống ngoài nằm trong dấu code kèm tên + nguồn?
7. Ưu tiên và mức bằng chữ?

Công cụ `check` của repo chạy các bước 1, 2, 4, 5 và 7 tự động; 3 và 6 là việc của reviewer.
