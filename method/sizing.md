---
title: Sizing — direct action and four sizes, risk only raises
type: method
status: active
updated: 2026-11-13
---

# Cỡ việc: làm thẳng và bốn mức, rủi ro chỉ nâng

> **Kết luận:** cỡ việc quyết **độ dày tài liệu và độ sâu kiểm định**, không quyết thời gian. Chọn cỡ
> theo thứ tự *phạm vi được giao → rủi ro → cỡ → tài liệu/cổng áp dụng*. Rủi ro chỉ được **nâng** cỡ;
> diff nhỏ không bao giờ là lý do hạ cỡ. Ngoài bốn cỡ có sprint còn bậc **làm thẳng** — không sprint, không
> hồ sơ — cho việc 1–2 thao tác có kết quả rõ hoặc khi người dùng nói rõ không cần sprint. Bậc được
> **khuyến nghị trong lượt trao đổi tiếp nhận** ([process.md](process.md) mục 2) và người dùng xác nhận.

## 1. Làm thẳng và bốn cỡ

| Cỡ | Dấu hiệu đo được | Tài liệu | Kiểm định | Cổng |
|---|---|---|---|---|
| **Làm thẳng** (không sprint) | việc chỉ gồm **1–2 thao tác** có kết quả rõ (đổi một giá trị cấu hình, chạy một lệnh, trả lời một câu tra cứu, sửa một chữ người dùng đã chỉ đích danh); **hoặc** người dùng nói rõ "không cần sprint" | **không có** hồ sơ: không `RQ-`, không `SPRINT.md`, không dòng sổ | agent tự kiểm bằng lệnh + kết quả **mới chạy** và báo ngay trong lời trả lời (kết quả, bằng chứng, cách hoàn tác nếu có) | không cổng hồ sơ; vẫn giữ nguyên **Git và điều cấm** (`AGENTS.md`) và mọi cổng xin phép khác |
| **Rất nhỏ** | đổi chữ hoặc một chỗ; không đổi hành vi hay quyền; lời giao đã nêu rõ kết quả; không cần người quyết gì | **một** `SPRINT.md` hai phần: "Kế hoạch" (mục tiêu, tiêu chí xong `SC`, việc `TK` trỏ `SC`) rồi "Kết quả" (nhật ký ngắn, `VR` cho mỗi `SC`) — "có kế hoạch rồi làm cho hoàn thiện", không SPEC / PLAN riêng | tự kiểm ghi "chưa độc lập" (kết luận tối đa Đạt có điều kiện), hoặc agent khác chạy kiểm nhanh | Cổng 1 "đạt theo lời giao" + trích lời giao; Cổng 2 gộp vào lời báo cuối ([process.md](process.md) mục 9) |
| **Nhỏ** | sửa cục bộ một luồng có sẵn; một `FR`; không đổi hợp đồng / giao diện / schema; không có quyết định kiến trúc | **một** `SPRINT.md` đủ bốn phần SPEC · PLAN · PROGRESS · REPORT, mỗi phần ngắn | **một** reviewer (agent khác người làm) kiểm cả nghiệp vụ lẫn kỹ thuật | Cổng 1 thật (trình ngắn), Cổng 2 thật |
| **Vừa** | tính năng, hành vi hay luồng mới; hoặc nhiều hơn một `FR` | 4 file đầy đủ; Tech Reviewer hoặc Advisor review PLAN trước Cổng 1 ([process.md](process.md) mục 3) | cả Business Reviewer **và** Tech Reviewer | đủ 2 cổng |
| **Lớn** | nhiều phần, đổi hợp đồng / giao diện / schema, hoặc **rủi ro cao** (mục 2) | 4 file + mục "Đổi hợp đồng / giao diện" trong SPEC + ADR cho quyết định kiến trúc + kế hoạch hoàn tác | cả hai reviewer + thẻ chuyên đề theo rủi ro; diễn tập migration nếu có dữ liệu | đủ 2 cổng; Cổng 2 có kiểm kế hoạch hoàn tác |

**Làm thẳng — điều kiện loại trừ.** KHÔNG được làm thẳng, dù chỉ 1–2 thao tác, khi việc chạm **vùng rủi ro**
(mục 2, bất kỳ nhãn `risk_tags`), **file luật** của dự án hay môi trường, **secret**, hoặc **hành động không đảo
ngược** (xoá dữ liệu, viết lại lịch sử git, push/deploy/gửi tin) — khi đó tối thiểu là rất nhỏ, và vùng rủi ro
kéo lên lớn như thường. Ngoại lệ duy nhất: người dùng **nói rõ** không cần sprint cho đúng việc đó — lời người
dùng thắng, không mở hồ sơ; nhưng mọi cổng xin phép khác **vẫn giữ nguyên**: sửa file luật vẫn phải được gật
trong chat, hành động không đảo ngược vẫn phải hỏi trước, secret vẫn không đọc. Việc mơ hồ (chưa biết kết quả
trông ra sao, hay phải chọn giữa nhiều cách) không phải làm thẳng — mở lượt trao đổi tiếp nhận.

**Luật đi kèm bảng:**

- **Một thao tác** là một thay đổi có nghĩa ở một chỗ hoặc một lệnh đã xác định. Đổi chữ hiển thị và chữ kỳ vọng
  trong test đi kèm là hai thao tác; tự kiểm/chạy test đi kèm không tính thêm. Sàn cỡ vẫn áp: sửa hành vi một luồng
  có sẵn là nhỏ, tính năng mới là vừa, vùng rủi ro là lớn. Không chia một mục tiêu thành nhiều lượt làm thẳng để
  né sprint; đếm toàn bộ việc cần để mục tiêu xong, chỉ tách các mục tiêu độc lập.
- **Phân vân giữa hai bậc → chọn bậc nặng hơn.** Nghi cần hơn 2 thao tác hay kết quả chưa rõ thì không phải làm
  thẳng; nghi có đổi hành vi hay hợp đồng thì không phải rất nhỏ; nghi hơn một luồng thì không phải nhỏ.
- **Bậc được khuyến nghị, không tự quyết một chiều:** Analyst nêu bậc khuyến nghị và "có mở sprint không" trong
  **một** tin trao đổi tiếp nhận ([process.md](process.md) mục 2); người dùng xác nhận hay đổi. Bỏ lượt này khi
  người dùng đã nói "không cần sprint" hoặc việc là làm thẳng không mơ hồ.
- **Rủi ro chỉ nâng cỡ** (mục 2): `risk: high` luôn là lớn. Diff nhỏ không bao giờ là lý do hạ cỡ.
- **Hạ cỡ chỉ ở Cổng 1, do người dùng quyết** (mục 4).
- **Cấu hình quyền, hook hay workflow CI không bao giờ là rất nhỏ**, dù diff một dòng (mục 2).
- **Hình tài liệu khớp cỡ:** `init --tiny` dựng `SPRINT.md` hai phần, `init --size small` dựng `SPRINT.md` bốn phần;
  `check` báo `sprint-size-mismatch` khi `SPRINT.md` ở cỡ vừa/lớn hoặc khi cỡ rất nhỏ lại dựng bốn file. Sprint cũ
  vẫn hợp lệ: `SPRINT.md` cỡ rất nhỏ bốn phần, và bốn file cỡ nhỏ ([templates/README.md](../templates/README.md) mục 4).
- **Người làm không tự chấm ở mọi bậc.** Việc rất nhỏ không có agent thứ hai thì ghi "tự kiểm, chưa độc lập".

<!-- san-cung:start -->
## 2. Rủi ro nâng cỡ

KHI việc chạm **một** trong các vùng sau THÌ ghi nhãn vào `risk_tags`, `risk: high`, cỡ tối thiểu là
**lớn** và Tech Reviewer kéo thẻ chuyên đề tương ứng ([roles/verifier/specialists/](../roles/verifier/specialists/)):

| Vùng | `risk_tags` | Chuyên đề kéo |
|---|---|---|
| secret, khoá, token, cấu hình xác thực | `secret` | security |
| xác thực, phân quyền, phiên | `auth` | security |
| thêm điểm nhận dữ liệu không tin cậy, hoặc đổi hợp đồng/kiểm tra bảo mật/giải mã–phân tích/đưa dữ liệu vào thao tác nhạy cảm qua điểm đó (form, API công khai, file tải lên, webhook) | `external_input` | security (+ backend) |
| API công khai, hợp đồng giữa dịch vụ | `public_api` | backend |
| hạ tầng, deploy, hook, workflow CI, quyền chạy | `infra` | security (+ backend) |
| migration dữ liệu, đổi schema, backfill, xoá dữ liệu | `data_migration` | data |
| file luật của dự án hay của môi trường (quy tắc agent, cấu hình harness) | `rules` | security |

Cấu hình đổi quyền, hook hay workflow thực thi **không được** xếp rất nhỏ dù diff một dòng (và `risk: high` buộc cỡ lớn).

Trường UI có sẵn không tự tạo nhãn `external_input`. Chỉ đổi chữ hoặc chuẩn hoá tìm kiếm cục bộ (trim đầu/cuối)
có thể giữ `risk: normal` khi có bằng chứng giữ nguyên quyền, tenant/danh tính, kiểm tra bảo mật, parser/schema,
hợp đồng API và cách truy vấn/thao tác nhạy cảm; cỡ theo hành vi (sửa một luồng có sẵn là nhỏ). Có thay đổi hoặc
chưa loại trừ tác động lên những ranh giới đó → `external_input`, `risk: high`, `size: large` và review security.

Ba nhãn `rules`, `secret`, `auth` kéo thêm một luật nữa: kiểm định kỹ thuật bắt buộc **hai reviewer độc lập** cùng rubric,
cả hai Đạt mới Đạt ([roles/verifier/dual-review.md](../roles/verifier/dual-review.md)) — cộng với thẻ chuyên đề security ở bảng trên.
<!-- san-cung:end -->

## 3. Sprint = một mục tiêu

**Cỡ khác độ khó và effort.** Sáu trục ở [task-routing.md](task-routing.md) đánh giá work item và chọn
assignment có nguồn; cỡ ở đây quyết hồ sơ/cổng/reviewer cho toàn mục tiêu. Một dòng auth có thể ít
phức tạp kỹ thuật nhưng vẫn lớn/high. Human model/effort override không hạ cỡ/risk hoặc miễn kiểm định.

- Một sprint phục vụ đúng một mục tiêu đã "định hình": biết làm gì, biết thế nào là xong, biết giới hạn
  công sức. Dài ngắn tuỳ mục tiêu — một phiên, một tính năng, một đợt chỉnh đều là sprint.
- Yêu cầu chứa nhiều mục tiêu → tách thành nhiều sprint, cùng trỏ về một `RQ-`.
- Giới hạn là **công sức**, không phải lịch: ước lượng trong PLAN ghi bằng số việc và số vòng dự kiến;
  vượt ước lượng đáng kể (gấp đôi) là tín hiệu PLAN hỏng (điều kiện dừng (d)) hoặc cần tách sprint.
- Không dùng tuần, story point, burndown.

### 3.1 Ngưỡng nhỏ ↔ vừa (đo được)

Bảng ở mục 1 nói "một `FR`", "một luồng có sẵn" nhưng không nói đếm thế nào; ngưỡng dưới đây là **cách đo** cùng định nghĩa đó,
dùng khi phân vân giữa nhỏ và vừa (và để tính trần phiên ở [autopilot.md](autopilot.md) mục 2.1). Việc là **nhỏ khi cả năm
điều đúng**; một điều sai thì là **vừa** (đã nằm ở luật "phân vân → chọn bậc nặng hơn"). Rất nhỏ, làm thẳng và lớn không đổi.

| # | Điều kiện của nhỏ | Cách đo | Sai khi |
|---|---|---|---|
| 1 | đúng một `FR` | đếm `FR` ở mức một trong SPEC; kịch bản `FR1.1`, `FR1.2` cùng một `FR1` vẫn là một | từ hai `FR` trở lên (hai hành vi cần kiểm riêng) |
| 2 | không có hành vi hay luồng mới | không có `US` mới; việc chỉ đổi điều kiện, giá trị, chữ hay thứ tự trong luồng đã chạy được | thêm bước, màn hình, lệnh, đường vào hay kiểu đầu ra mới |
| 3 | không đổi hợp đồng / giao diện / schema | như mục 1; có phải sửa chỗ gọi nơi khác vì hàm đổi chữ ký thì sai | đổi chữ ký công khai, trường dữ liệu, định dạng file hay cấu hình |
| 4 | tối đa 4 `TK` | đếm `TK` mức một trong PLAN; việc con `TK2.3` không tính | từ 5 `TK` |
| 5 | ước tính tối đa 8 phiên agent | số phiên = số `TK` + 4 (một reviewer, hai lần Gate Delegate, một lần giao lại sau review); 8 là trần cơ sở cỡ nhỏ | ước tính trên 8 |

Điều 4 và 5 là **một** phép đo (4 `TK` + 4 = 8), ghi cả hai để người đọc thấy số nào chạm trần. Số `TK` và số phiên là
**ước lượng lúc lập PLAN**, không chấm lại cỡ khi thực tế vượt: vượt ước lượng gấp đôi đi theo mục 3 (PLAN hỏng, tách sprint).

| Ví dụ | `FR` · `TK` · phiên ước | Điều sai | Cỡ |
|---|---|---|---|
| tra đơn bỏ khoảng trắng đầu/cuối mã (mẫu ở `templates/SPRINT.md`) | 1 · 1 · 5 | — | nhỏ |
| đổi quy tắc làm tròn giá trong hàm đang chạy, kèm test | 1 · 2 · 6 | — | nhỏ |
| thêm xuất Excel cho báo cáo có sẵn | 1 · 2 · 6 | 2 (đầu ra mới) | **vừa** |
| sửa hai lỗi độc lập trong cùng module | 2 · 2 · 6 | 1 | **vừa**; hoặc tách hai sprint nhỏ (mục 3) |
| đổi một luồng có sẵn nhưng phải chạm ba mô-đun, năm `TK` | 1 · 5 · 9 | 4, 5 | **vừa** |
| đổi tên trường `price` thành `unit_price` ở API công khai | 1 · 3 · 7 | 3 | **lớn** (hợp đồng, mục 1) |

**Không áp ngược.** Bảng này làm rõ cách đo, không đổi cỡ đã ghi: hồ sơ cũ giữ nguyên `size` trong frontmatter, và `check` không
chấm lại cỡ theo số `TK` hay số phiên.

## 4. Ghi vào tài liệu

Frontmatter mọi tài liệu sprint có `size: tiny | small | medium | large`, `risk: normal | high` và
`risk_tags` (rỗng khi `normal`). `risk: high` buộc `size: large`. Bậc làm thẳng không có tài liệu nên không có
frontmatter; nó chỉ xuất hiện trong lời trả lời.
Cỡ ghi ở Bước 1 (Tiếp nhận) sau khi người dùng xác nhận bậc trong lượt trao đổi, có thể **nâng** ở bất kỳ bước nào
khi lộ rủi ro mới (ghi `Phán quyết:` kèm lý do); **hạ** cỡ chỉ được ở Cổng 1 do người dùng quyết. Việc đang làm
thẳng mà lộ ra cần hơn 2 thao tác, chạm vùng rủi ro hay kết quả không còn rõ → dừng, mở lượt trao đổi tiếp nhận.
Mức tự trị ở Brief, chế độ duyệt thay và autopilot không hạ cỡ hay rủi ro.

## 5. Đối chiếu luồng orch

Nhiều bộ công cụ chia việc thành năm **luồng** theo loại thay đổi (thêm tính năng, đổi hành vi có sẵn, sửa lỗi, tái
cấu trúc, dựng bản đầu từ tài liệu thiết kế). Repo này **không** thêm trục thứ hai: cỡ việc (mục 1) vẫn là trục duy
nhất quyết độ dày tài liệu và cổng. Bảng dưới chỉ trả lời "một luồng quen tay rơi vào cỡ nào, bước đầu tiên là gì,
kéo skill nào". Bốn bậc của nguồn (nhỏ nhất → lớn nhất) khớp bốn cỡ **Rất nhỏ · Nhỏ · Vừa · Lớn** ở trên, nhưng nguồn
chỉ đếm số file; ở đây cỡ còn do hành vi, hợp đồng và rủi ro quyết. Bậc làm thẳng không có luồng tương ứng: nó
không phải sprint.

Bảng có 5 hàng — mỗi hàng một **luồng** ở cột đầu:

| Luồng (loại việc) | Cỡ tối thiểu | Bước đầu tiên khi làm | Cổng người | Skill kéo vào |
|---|---|---|---|---|
| Thêm tính năng (hành vi chưa có) | **Vừa** — luôn có hành vi hay luồng mới | viết test mới cho hành vi mới, thấy nó hỏng **đúng lý do**, rồi mới viết mã | Cổng 1 và Cổng 2 đủ | `intake` → `shaping-spec` → `writing-plan` → `running-sprint` + `tdd` → `code-review` |
| Đổi hành vi có sẵn (chạy đúng nhưng muốn khác) | **Nhỏ** — một luồng, một `FR`, không đổi hợp đồng; **Vừa** khi đổi nhiều hơn một `FR` | sửa **test hiện có** cho khớp hành vi mới rồi đổi mã tới khi đạt; sửa test trước là điểm phân biệt đổi hành vi với sửa lỗi | Cổng 1 và Cổng 2 thật (trình ngắn) | `intake`, `shaping-spec` (delta **Sửa** cho spec sống), `tdd`, `code-review` |
| Sửa lỗi (hành vi sai, hồi quy) | lỗi **hành vi** (logic, hồi quy): **Nhỏ** — đổi hành vi nên không xuống Rất nhỏ; lỗi **chữ hay nhãn** không đổi hành vi (câu báo sai chính tả, nhãn nút): **Rất nhỏ** theo mục 1; lỗi chạm vùng rủi ro (mục 2): **Lớn** | lỗi hành vi: tái hiện thành **test hỏng** (test hồi quy) rồi sửa; lỗi chữ: sửa rồi chạy lại phép kiểm hiện có; chứng minh bằng vòng gỡ sửa → hỏng → đặt lại ([evidence.md](evidence.md) mục 4) | theo cỡ đã chọn (rất nhỏ: "đạt theo lời giao", mục 1) | `bug-triage` (chấm mức, định tuyến) → `debugging` → `tdd` → `verify-before-done` |
| Tái cấu trúc (giữ hành vi, đổi cấu trúc) | theo **phạm vi đụng tới**: **Nhỏ** khi một mô-đun cục bộ; **Vừa** khi nhiều mô-đun hoặc đổi giao diện nội bộ; **Lớn** khi chạm hợp đồng bên ngoài | xác nhận test liên quan **đang xanh trước khi chạm mã**; thiếu thì viết test mô tả hành vi hiện tại; đổi từng bước nhỏ, chạy lại sau mỗi bước; diff phải trung tính về hành vi | như cỡ đã chọn | `tdd`, `code-review` (kể cả tìm hàm trùng lặp), `verify-before-done` |
| Dựng bản đầu từ tài liệu thiết kế | **Lớn** | đọc tài liệu, trích phạm vi, quyết định đã khoá và danh sách tính năng; cắt thành **lát dọc mỏng** (một đường chạy hết đầu–cuối trước, không làm hết lớp này rồi mới tới lớp kia) | Cổng 1 và Cổng 2 đủ; mỗi lát một mục tiêu nên **một sprint một lát**, cùng trỏ về một `RQ-` | `intake`, `shaping-spec`, `writing-plan`, `adr` |

Luật đi kèm:

- **Số file dự kiến là dấu hiệu phụ, không phải tiêu chí cứng:** một đến hai file nghiêng về Rất nhỏ / Nhỏ, nhiều hơn năm file
  nghiêng về Vừa; hành vi, hợp đồng và rủi ro (mục 1–2) vẫn quyết cỡ, số file chạm không quyết.
- **Luồng không hạ cỡ.** Cột "cỡ tối thiểu" là sàn; mục 1 (phân vân chọn bậc nặng hơn) và mục 2 (rủi ro chỉ nâng)
  vẫn quyết cỡ cuối cùng. Việc chạm vùng rủi ro nào ở mục 2 cũng thành cỡ lớn, bất kể luồng.
- **Cổng 2 là nghiệm thu sau REPORT**, không đặt trước từng lần commit. Commit nằm trong bước thực thi theo từng
  `TK`; push, mở PR và gộp nhánh chính chỉ sau Cổng 2 và khi người dùng gật ([process.md](process.md) mục 7).
- **Kiểm định luôn do agent khác** người làm ở mọi luồng và mọi cỡ; thêm Tech Reviewer kéo thẻ chuyên đề security khi
  việc chạm secret, xác thực hay đầu vào từ ngoài (mục 2).
