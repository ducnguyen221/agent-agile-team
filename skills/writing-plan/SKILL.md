---
name: writing-plan
description: Use when a SPEC exists (or the user has given clear requirements) for work that takes more than one step, and a PLAN must be written before any code — defining tasks with files, interfaces, explicit test-first steps, review focus, risks and decisions that an engineer who has never seen the codebase can execute without guessing.
metadata:
  group: process
  roles: [architect]
source: "obra/superpowers skills/writing-plans/SKILL.md (v6.4.2)"
source_sha: 8ca22dba9a94f28898bbce59f2537ff4d87c747d
license: MIT
rewrite_before_public: false
---

# Viết PLAN (Bước 2, nửa sau)

> **Kết luận:** PLAN là **tập quyết định mà người làm không tự quyết được**: file nào, tên và chữ ký
> nào, giá trị nào lấy từ SPEC, test nào chứng minh từng việc. Người đọc là kỹ sư giỏi **chưa thấy
> codebase** này. Mỗi `TK` có bước **test hỏng → chạy thấy hỏng → code tối thiểu → chạy thấy đạt →
> commit** viết tường minh. PLAN dài gấp nhiều lần SPEC là đang chép code, không phải lập kế hoạch.

## 0. Phân loại và thông báo trước PLAN

Áp dụng `method/task-routing.md` mục 1–3 và 5: ghi sáu trục `ambiguity`, `scope`, `consequence`,
`verifier`, `plan`, `complexity`, mỗi trục có giá trị chuẩn, ordinal và nguồn; thiếu nguồn để unknown.
Difficulty chỉ suy từ scope/plan/complexity; effort mặc định `medium` (ordinal 2), kết hợp difficulty,
risk floor và capability theo công thức của method. Giữ baseline theo vai; pin người dùng thắng riêng
field được chỉ định, không thay risk/gates hoặc các field khác. Tách capability, quyền truy cập và runtime.
Trước PLAN hoặc đổi assignment, phát notice đủ actor/harness/vai/tier/model/effort/phạm vi/lý do/nguồn,
phân biệt requested/effective/actual; thiếu bằng chứng actual thì unknown, không lấy identity của người
kiểm thử làm identity actor. Topology theo module độc lập, ownership và overhead; chưa đo thì không
nhận có lợi ích tiết kiệm. Giữ thủ tục review và counter sửa có kiểm chứng riêng theo mục 6b.
## 1. Trước khi chia việc

1. **Kiểm phạm vi:** SPEC gộp nhiều hệ con độc lập → đề xuất tách thành nhiều PLAN (mỗi PLAN cho ra
   phần mềm chạy và kiểm được). Việc này lẽ ra đã xong ở `shaping-spec`; chưa xong thì nói rõ.
2. **Vẽ cấu trúc file trước:** file nào tạo, file nào sửa, mỗi file chịu trách nhiệm gì. Đây là nơi
   quyết định chia nhỏ được chốt. Đơn vị nhỏ, một trách nhiệm, giao diện rõ; file đổi cùng nhau ở cạnh
   nhau; theo khuôn repo đang có — file đang sửa đã quá to thì được đưa việc tách vào PLAN.
3. **Đọc ràng buộc chung** của SPEC và dự án; chúng áp lên mọi `TK` và được chép **nguyên văn** vào
   mục Ràng buộc chung của PLAN (giá trị chính xác, không diễn giải).

## 2. Cỡ một `TK`

Một `TK` là đơn vị nhỏ nhất **mang được vòng test riêng** và đáng một lượt reviewer: gộp setup, cấu
hình, scaffold, tài liệu vào `TK` cần chúng; chỉ tách ở chỗ reviewer có thể bác `TK` này mà vẫn duyệt
`TK` kia. Mỗi `TK` kết thúc bằng sản phẩm kiểm độc lập được. Việc nhỏ cùng hình (sửa hằng số ở 6 file)
gộp làm một `TK` có danh sách file.

## 3. Cấu trúc PLAN theo mẫu `templates/sprint/PLAN.md`

| Mục của mẫu | Viết gì |
|---|---|
| Kết luận | một câu: cách làm chính + số việc + điều cần người quyết |
| Mục tiêu | ba dòng nhãn chép đúng chữ mẫu (luật `plan-goal-block` báo khi viết tắt): `Mục tiêu sprint:` một câu (và mục tiêu việc nếu khác) · `Kết quả mong muốn / xong khi:` trỏ `SC` · `Rủi ro cần chú ý:` rủi ro cụ thể, trỏ `RK` |
| Kiến trúc | 2–3 câu cách làm; thành phần đổi; luồng dữ liệu; quyết định lâu dài → trỏ ADR (`docs/architecture/adr/`) |
| Ràng buộc chung | luật áp cho MỌI `TK`: ngưỡng phiên bản, giới hạn phụ thuộc, quy ước đặt tên, nền tảng, coverage — chép nguyên văn từ SPEC/dự án |
| Trọng tâm review | **≤5** lớp đầu vào hay kiểu hỏng SPEC ngụ ý nhưng chưa `TK` nào có test — thứ dễ cắn người dùng nhất lên đầu; mỗi dòng rồi **gắn test về `TK` sở hữu code** (mục 4) |
| Việc | mỗi `TK` theo mục 4 |
| Rủi ro | `RK` theo thang Chặn / Phải sửa / Nên sửa / Ghi chú; Chặn hoặc Phải sửa nêu ở Cổng 1 |
| Quyết định cần người | `DN` chỉ cho điểm làm đổi đáng kể kết quả; có lựa chọn + khuyến nghị; không có thì "Không có." |
| Ước lượng | số phiên agent, số lần hỏi người (mục tiêu 0 ngoài cổng), số vòng kiểm định dự kiến |

SPEC là thẩm quyền; PLAN là lập luận của SPEC. SPEC "im lặng" về một đầu vào không phải phép cho đầu
vào đó làm hỏng chương trình — đó là việc của Trọng tâm review.

## 4. Một `TK` gồm gì

Sáu dòng bắt buộc của mẫu, rồi khối **Bước** — khung tối thiểu, ví dụ dưới viết rút gọn; thước đủ chi tiết là checklist 11 ô ngay sau ví dụ:

```
### TK3 — Hàm chuẩn hoá mã đơn (→ FR1.2, SC1)
- **Vai:** Implementer · T2.
- **Đầu vào:** TK1 (bảng đơn). **Đầu ra:** `normalize_code` + test.
- **Giao diện (interfaces):**
  - Dùng: `Order.code: str` (TK1 sinh).
  - Sinh: `normalize_code(raw: str) -> str` trong `services/orders.py`; cắt khoảng trắng, chữ hoa.
- **File:** tạo `tests/test_orders.py`; sửa `services/orders.py:40-55`.
- **Cách kiểm:** `pytest tests/test_orders.py -q` xanh; coverage dòng ≥80 % cho file sửa.
- **Cổng:** nội bộ. **Hoàn tác:** `git revert` commit của TK3.
- **Bước:**
  1. RED — viết `test_normalize_code_strips_and_uppercases`: `normalize_code("  ab12 ") == "AB12"`,
     `normalize_code("ab 12")` ném `ValueError`.
  2. Chạy `pytest tests/test_orders.py::test_normalize_code_strips_and_uppercases -q` → kỳ vọng
     **FAIL** vì `normalize_code` chưa tồn tại (hỏng vì đúng lý do, không phải lỗi cú pháp).
  3. GREEN — viết `normalize_code` theo chữ ký trên, tối thiểu để test đạt.
  4. Chạy lại lệnh ở bước 2 → **PASS**; chạy cả bộ `pytest -q` → xanh.
  5. Commit: `git add tests/test_orders.py services/orders.py && git commit -m "TK3: normalize order code"`.
```

**Số `TK` = thứ tự làm.** Đánh số 1…N theo thứ tự thực hiện; `Đầu vào:` chỉ trỏ `TK` số nhỏ hơn (luật `task-order`); hai việc
độc lập vẫn số liền nhau, việc sau ghi "chạy cùng được với TKk". Trước Cổng 1 được đánh số lại; sau Cổng 1 chèn `TKn.m`
(`id-convention` mục 4).

**Checklist 11 ô mỗi `TK`** — ô trống là Phải sửa khi review: (1) tiêu đề trỏ `FR`/`SC` · (2) vai · tier (+ effort nếu khác
sàn) · (3) `Đầu vào:` · (4) `File:` đường đầy đủ + tạo/sửa + neo (dòng hoặc mục) · (5) `Giao diện:` tên + chữ ký/giá trị, enum
đủ · (6) hành vi từng nhánh "vào → ra" có ví dụ · (7) chữ dự thảo cho tài liệu/skill/mẫu (hoặc trỏ mục SPEC có chữ chốt) ·
(8) Bước theo bảng dưới · (9) Cách kiểm lệnh + output · (10) commit mang mã `TK` · (11) Hoàn tác + Bằng chứng đạt.

**Khối Giao diện là cách `TK` sau biết tên và kiểu của `TK` trước:** người làm `TK` chỉ thấy `TK` của
mình. `TK` trỏ `TK` khác thì trỏ vào khối Giao diện của nó, không chép lại code.

**Một bước chứa gì** — đủ để người làm viết đúng **một** thứ hợp lý, không hơn:

| Loại bước | Chứa | Không chứa |
|---|---|---|
| Test (RED) | tên test + assertion dạng code, với **giá trị chính xác** từ SPEC | test "cho phần trên" không có code |
| Code (GREEN) | chữ ký đầy đủ (tên, tham số, kiểu trả), file, giá trị SPEC ghim; một dòng cách làm khi chữ ký và test còn để ngỏ lựa chọn | thân hàm — trừ thuật toán mà chữ ký và test không xác định, hay chuỗi SPEC cố định |
| Kiểm | lệnh nguyên văn + output nghĩa là đạt (hoặc hỏng, ở bước RED) | "chạy test" không có lệnh |
| Commit | lệnh, thông điệp mang mã `TK` | — |

`TK` không sinh code (tài liệu, cấu hình) vẫn có Bước: làm → kiểm (lệnh + kỳ vọng) → commit.

**`TK` tác động ngoài worktree hoặc ngoài repo** (ghi state của máy, cấu hình người dùng, hệ ngoài, dịch vụ
thật) — chọn một, ghi rõ trong `TK`:

- **Đo trong worktree, ghi thật sau:** `TK` chỉ làm và kiểm bằng bản tạm trong worktree; bước ghi thật thành
  **bàn giao sau Cổng 2** (REPORT mục "Cách dùng, đã đổi gì, cách hoàn tác"). Ưu tiên cách này.
- **Bắt buộc giữa sprint:** `Cổng: người` + trỏ một `DN` nêu đích danh đường dẫn / hệ bị chạm, cách hoàn tác;
  `TK` dừng ở bước đó tới khi `DN` có câu trả lời (`method/process.md` mục 5, điều kiện (c)).

## 5. Chỗ trống là lỗi PLAN

Không bao giờ viết: "TBD", "làm sau", "xử lý biên phù hợp", "thêm validation", "viết test cho phần
trên", "tương tự TK2" (người đọc có thể đọc không theo thứ tự), bước mô tả *làm gì* mà không nói *thế
nào*, kiểu/hàm không `TK` nào định nghĩa. Ngược lại, thân hàm mà chữ ký và test đã xác định là chép
code — cũng là lỗi. Ô nào của checklist mục 4 bỏ trống, hay "viết nội dung phù hợp" thay cho chữ dự thảo, cũng
là chỗ trống.

## 6. Tự review 5 điểm — chạy chính mình, không giao subagent

1. **Phủ SPEC:** lướt từng `US`/`FR`/`SC`: trỏ được `TK` nào làm? Thiếu → thêm `TK`. Mỗi `TK` trỏ ít
   nhất một `FR`/`SC` (`check` kiểm).
2. **Quét bước:** mỗi bước cho viết đúng một thứ hợp lý; dòng không quyết gì là lỗ hổng, thân hàm đã
   xác định là bản chép — sửa cả hai.
3. **Nhất quán kiểu:** tên, chữ ký, thuộc tính ở `TK` sau khớp `TK` trước? (`clear_layers` ở TK3 mà
   `clear_full_layers` ở TK7 là lỗi.)
4. **Trọng tâm review:** mỗi lớp đầu vào/kiểu hỏng SPEC ngụ ý có `TK` nào test chưa? Năm điểm chưa
   phủ dễ cắn người dùng nhất vào mục Trọng tâm review, mỗi điểm gắn test về `TK` sở hữu. Mục rỗng
   nghĩa là đã kiểm và không thấy, không phải chưa kiểm.
5. **Tỷ lệ:** so độ dài PLAN với SPEC. PLAN dài gấp nhiều lần SPEC, khối code chiếm phần lớn → thay thân
   bằng chữ ký + tên test + assertion, rồi kiểm lại từng bước còn rõ không.

Sửa tại chỗ, không review lại lần hai.

## 6b. PLAN lớn hoặc nhiều sprint — hợp đồng trước, kiểm mã trước, trần vòng review

PLAN lớn cần hợp đồng trước khi chia việc, kiểm chứng source trước review và đồng bộ tài liệu sau sửa.
Năm quy tắc dưới giữ phạm vi review rõ, tránh lệch do chính lần sửa tạo ra và giảm việc đọc lại không cần thiết.

1. **Hợp đồng bàn giao trước khi chia việc hoặc fan-out.** Trước khi giao bất kỳ sprint hay `TK` nào cho
   agent khác viết, chốt trên **một trang**: tên file/đường bàn giao, schema (khoá, kiểu), chữ ký CLI và mã
   thoát của công cụ dùng chung, cách kiểm bằng lệnh, ai sản xuất – ai tiêu thụ. Giao viết song song mà chưa
   có trang này thì mỗi agent tự đặt tên khác nhau và reviewer tốn 2–3 vòng chỉ để vá lệch.
2. **Tự kiểm chứng khẳng định về mã trước khi gọi reviewer.** Liệt 5–10 câu PLAN khẳng định về mã hiện có
   (hàm X đọc biến Y, hook thoát mã Z khi thiếu file, script chỉ nhận tiền tố W…) và `grep`/mở đúng dòng cho
   từng câu — mỗi câu 30 giây. Người viết làm từ báo cáo trung gian luôn thua reviewer có mã trong tay; đừng
   trả tiền cho reviewer để làm việc `grep` thay mình.
3. **Sau mỗi lần sửa lớn, chạy một lượt đồng bộ chéo** trước khi re-review: grep tên file, mã (`TK`, `SC`,
   `RF`), số liệu, trạng thái giữa SPEC – PLAN – tài liệu thiết kế – REPORT – PROGRESS. Sửa một chỗ mà không
   quét lại là tự tạo phát hiện cho vòng sau.
4. **Trần vòng review PLAN: 2, tối đa 3.** Vượt trần mà còn Phải sửa không phải Chặn → gộp thành *điều
   kiện thực thi* ghi ở `TK` sở hữu, không re-review toàn bộ (mỗi vòng reviewer đọc lại toàn bộ PLAN + mã;
   PLAN 300–400 dòng × nhiều sprint = hàng triệu token một vòng). Còn Chặn thì sửa đúng Chặn và re-review
   **hẹp** theo diff.
5. **Giữ PLAN ngắn:** kiểm kê, bảng `file:dòng`, nguyên văn review → `evidence/`; PLAN chỉ giữ hợp đồng,
   bước, cách kiểm, hoàn tác. Reviewer đọc PLAN, tra evidence khi cần.

Chọn model cho vai viết PLAN theo bảng tier (`AGENT_AGILE_TIERS`), không theo cảm giác "model mạnh hơn":
chênh lệch chất lượng giữa người viết và người review đến từ **có mã trong tay và có hợp đồng trước** nhiều
hơn từ model. Reviewer phải là model hoặc phiên khác người viết.

## 7. Bàn giao

- Từ cỡ **vừa**: `status: in_review`, Tech Reviewer (agent khác) review PLAN theo skill `plan-review`;
  Chặn/Phải sửa thì sửa trước khi trình.
- Trình **Cổng 1** cùng SPEC theo lời trình chuẩn (`method/process.md` mục 3): kết luận → `CQ` → `DN`
  → `RK` Chặn/Phải sửa → ước lượng → đường dẫn. Không dán PLAN vào chat.
- Trong lời trình, **đề xuất chế độ thực thi** cho skill `running-sprint`: *giao subagent từng việc*
  (mỗi `TK` một agent mới + review theo việc — kỹ nhất, tốn một ngữ cảnh mỗi việc) hay *một agent làm
  liên tục* (rẻ nhất, chỉ review toàn nhánh cuối) — kèm một câu lý do từ PLAN: các `TK` phụ thuộc giao
  diện nhau tới đâu, bao nhiêu `TK`, lỗi lọt ra ngoài tốn gì. Người dùng đã chỉ định chế độ thì không
  hỏi lại.
- Duyệt rồi (`gate_1: approved` + câu nguyên văn) mới sang `running-sprint`. Duyệt PLAN không phải
  nghiệm thu kết quả.

## 8. Cờ đỏ

| Ý nghĩ | Thực tế |
|---|---|
| "Dán luôn code cho chắc" | người làm viết code idiomatic được; cái họ thiếu là quyết định của bạn |
| "Bước 2–5 phút" | thước đo là *một hành động có kết quả kiểm được*, không phải thời gian |
| "Để Implementer chọn tên hàm" | tên và chữ ký là giao diện giữa các `TK` — PLAN phải chốt |
| "SPEC không nói đến đầu vào này nên không cần test" | SPEC là tầm nhìn, không phải danh sách đầy đủ; đưa vào Trọng tâm review |
| "Review PLAN tốn một lượt" | một lượt review rẻ hơn một vòng sửa sau Cổng 1 |
