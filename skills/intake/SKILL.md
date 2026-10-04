---
name: intake
description: Use when a user hands over a new request in plain words (feature, fix, change or question that implies work), when the intended result or scope is unclear, or when there is pressure to skip intake, understate risk, split a goal into direct actions or create sprint records for a clear local text change.
metadata:
  group: process
  roles: [analyst]
source: ["affaan-m/ECC skills/prompt-optimizer (missing-context checklist, via local distill); method/process.md step 1", "affaan-m/ECC skills/intent-driven-development, skills/product-capability (business rules not readable from code; observable acceptance criteria)"]
source_sha: [c70874fae9eb0e5ad0365beb7e2955899fd1d30f, ef648e01899ba3e8dc6371642deaaf64b4477775]
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: [MIT, MIT]
rewrite_before_public: false
---

# Tiếp nhận yêu cầu (Bước 1)

> **Kết luận:** tiếp nhận là bước **một lượt trao đổi gom** giữa Analyst (T1) và người dùng: đọc và phân tích
> đầu bài trước, rồi gửi **một tin** — mục tiêu theo cách hiểu · câu hỏi phản biện · khuyến nghị bậc (làm thẳng /
> rất nhỏ / nhỏ / vừa / lớn **cho từng việc, kèm lý do và nhãn rủi ro**) · có mở sprint không — chờ xác nhận, rồi mới ghi `RQ-`, tách
> mục tiêu, định cỡ và rủi ro (chỉ nâng), ghi **ASSUMPTION**, gom điểm còn lại thành `CQ` cho Cổng 1. Hỏi lẻ
> nhiều lượt ở bước này là lỗi quy trình; bỏ hẳn lượt trao đổi khi người dùng đã nói "không cần sprint" hoặc việc
> là làm thẳng không mơ hồ.

## 1. Bảy việc, theo thứ tự

| # | Việc | Ghi vào |
|---|---|---|
| 1 | **Đọc và phân tích** đầu bài: tra repo, sổ gốc, spec sống; đọc `method/sizing.md` mục 1–2 và rà 11 điểm (mục 2) — tra được thì tra, không hỏi | nháp của Analyst |
| 2 | **Một tin trao đổi gom** cho người dùng (mục 1.1): mục tiêu theo cách hiểu · câu hỏi phản biện · khuyến nghị bậc · có mở sprint không | chat |
| 3 | **Chờ xác nhận.** Chưa xác nhận thì chưa `RQ-`, chưa sprint, chưa chạm mã. Người dùng chọn làm thẳng → làm ngay, kiểm, báo; hết bước | — |
| 4 | Một dòng `RQ-` mới: ngày, tóm tắt một câu, trạng thái `mới`, **kèm câu trả lời của người dùng** (mục tiêu đã chốt, định nghĩa xong, phạm vi ngoài, bậc đã xác nhận) | sổ REQUESTS |
| 5 | Tách mục tiêu: một mục tiêu = một sprint; nhiều mục tiêu → nhiều sprint cùng trỏ một `RQ-` | sổ SPRINTS (khi mở sprint) |
| 6 | Ghi bậc đã xác nhận và `risk_tags`; bất kỳ nhãn rủi ro nào ở bảng dưới → `risk: high`, `size: large`, kể cả sau xác nhận (báo lại một câu) | frontmatter SPEC |
| 7 | Điểm còn lại ở 11 điểm → **ASSUMPTION** hoặc `CQ` (mục 3); rồi sang skill `shaping-spec`, không hỏi thêm lượt nào tới Cổng 1 | SPEC mục Câu hỏi cần làm rõ |

Lời giao đã nêu rõ mục đích, ràng buộc và kết quả thì phản ánh lại trong tin trao đổi, không hỏi lại điều đã có.

### 1.1 Tin trao đổi gom — viết thế nào

Một tin, bốn phần, mỗi phần ngắn; người dùng trả lời **một lần**:

**Sản phẩm của lượt tiếp nhận:** viết **nguyên văn tin gửi người dùng** ngay trong câu trả lời hiện tại,
trước phần trả lời agent hay dự thảo hồ sơ. "Sẽ gửi một tin gom" chỉ là kế hoạch, chưa phải tin trao đổi.
Khi có giới hạn dòng, rút ngắn từng phần nhưng giữ đủ bốn phần; chưa xác nhận thì ghi hồ sơ "chưa lập".

```
Tôi hiểu mục tiêu là: <một đến ba câu lời thường>.
Câu hỏi để chắc mình hiểu đúng (mỗi câu có đề xuất của tôi):
  1. <mục tiêu — vì sao cần / kết quả trông ra sao> — đề xuất: …
  2. <định nghĩa xong — đo bằng gì> — đề xuất: …
  3. <phạm vi — cái gì không làm đợt này> — đề xuất: …
Bậc từng việc: <tên việc>: <làm thẳng / rất nhỏ / nhỏ / vừa / lớn> — vì <dấu hiệu đo được>; risk: <normal/high>; risk_tags: <[] hoặc nhãn>.
  <lặp dòng này cho mỗi mục tiêu; đề xuất thứ tự bằng Bắt buộc / Nên có / Có thì tốt>.
Có mở sprint không? Khuyến nghị: <có / không; nếu có, bao nhiêu sprint>. Anh xác nhận hoặc sửa giúp.
```

- **Câu hỏi phản biện lấy nguyên liệu từ 11 điểm** (mục 2): chỉ điểm thuộc **ý muốn người dùng** mà repo không trả
  lời được (mục tiêu, định nghĩa xong, phạm vi ngoài, ưu tiên) mới vào tin; điểm kỹ thuật tra được thì tra. Thường
  2–4 câu; ≥5 câu là chưa tra đủ hoặc lời giao chứa nhiều mục tiêu.
- **Khuyến nghị bậc theo `method/sizing.md` mục 1**, kể cả điều kiện loại trừ của làm thẳng (vùng rủi ro, file luật,
  secret, hành động không đảo ngược). Bậc **từng việc** phải hiện trong tin gửi người dùng, không chỉ trong nháp/SPEC.
  Đủ bốn phần = mục tiêu nhắc lại + phản biện có đề xuất + bậc từng việc/rủi ro + câu hỏi rõ có mở sprint không.
- **Người dùng thắng:** họ đổi bậc hay chọn làm thẳng thì theo; nhưng rủi ro vẫn chỉ nâng, và mọi cổng xin phép khác
  (sửa file luật phải được gật, hành động không đảo ngược phải hỏi) vẫn giữ.
- **Bỏ lượt trao đổi** khi: người dùng nói rõ "không cần sprint" cho đúng việc; hoặc việc là **làm thẳng không mơ
  hồ** (1–2 thao tác, kết quả rõ, không chạm vùng loại trừ). "Làm luôn" chỉ thúc tiến độ, không tự miễn sprint
  hay mở ngoại lệ cho vùng loại trừ. Khi đủ điều kiện bỏ lượt trao đổi, làm ngay và báo kết quả + bằng chứng.
- Lời giao đã đủ mục tiêu, định nghĩa xong, phạm vi và bậc → tin chỉ còn một câu xác nhận.

**Cỡ quyết hình tài liệu và cổng** (bảng đầy đủ: `method/sizing.md` mục 1) — ghi cỡ kèm hình này:

| Cỡ | Dấu hiệu đo được | Tài liệu | Cổng 1 · kiểm định |
|---|---|---|---|
| Làm thẳng | 1–2 thao tác, kết quả rõ; hoặc người dùng nói rõ không cần sprint. Không áp khi chạm `risk_tags`, file luật, secret, hành động không đảo ngược — trừ khi người dùng nói rõ | **không hồ sơ**: không `RQ-`, không `SPRINT.md`, không dòng sổ | không cổng hồ sơ; tự kiểm bằng lệnh + kết quả mới chạy, báo trong lời trả lời; giữ Git và điều cấm, giữ mọi cổng xin phép khác |
| Rất nhỏ | đổi chữ hoặc một chỗ — kể cả chữ kỳ vọng trong test đi kèm, số file chạm không quyết cỡ; không đổi hành vi, quyền; lời giao đã nêu rõ kết quả | một `SPRINT.md` hai phần **Kế hoạch** (mục tiêu, `SC`, `TK` trỏ `SC`) · **Kết quả** (`VR` mỗi `SC`) | "đạt theo lời giao" + trích lời giao; không mở lượt hỏi mới (`method/process.md` mục 9) · agent khác chạy nhanh, hoặc tự kiểm "chưa độc lập" (tối đa Đạt có điều kiện); Cổng 2 gộp lời báo cuối |
| Nhỏ | sửa cục bộ một luồng có sẵn (hành vi đổi), một `FR`, không đổi hợp đồng / giao diện / schema | một `SPRINT.md` đủ bốn phần SPEC · PLAN · PROGRESS · REPORT | Cổng 1 thật (trình ngắn, chờ duyệt) · **một** reviewer khác người làm kiểm cả nghiệp vụ lẫn kỹ thuật; Cổng 2 thật |
| Vừa | tính năng, hành vi hay luồng mới; hoặc hơn một `FR` | bốn file | đủ hai cổng; Business Reviewer và Tech Reviewer |
| Lớn | nhiều phần; đổi hợp đồng / giao diện / schema; hoặc bất kỳ nhãn rủi ro ở bảng dưới | bốn file + đổi hợp đồng / giao diện, ADR khi có quyết định kiến trúc, hoàn tác | đủ hai cổng; cả hai reviewer + chuyên đề |

**Thao tác** = một thay đổi có nghĩa ở một chỗ hoặc một lệnh đã xác định. Đổi chữ và sửa chữ kỳ vọng trong test
đi kèm là hai thao tác; tự kiểm/chạy test đi kèm không tính thêm. Sửa hành vi một luồng có sẵn vẫn theo hàng **Nhỏ**;
tính năng mới theo **Vừa**; rủi ro theo **Lớn** — số file hay số dòng không hạ các sàn này.
Phân vân → bậc nặng hơn; hạ cỡ chỉ ở Cổng 1 do người dùng. Không chia một mục tiêu thành nhiều lần làm thẳng để
né sprint: đếm toàn bộ việc cần để mục tiêu xong trước khi chọn bậc; chỉ tách những mục tiêu độc lập.

| Chạm vùng | `risk_tags` | Bậc / chuyên đề |
|---|---|---|
| secret, token, cấu hình xác thực | `secret` | lớn / security |
| xác thực, phân quyền, phiên | `auth` | lớn / security |
| thêm điểm nhận dữ liệu không tin cậy, hoặc đổi hợp đồng/kiểm tra bảo mật/giải mã–phân tích/đưa dữ liệu vào thao tác nhạy cảm qua điểm đó (form, API công khai, upload, webhook) | `external_input` | lớn / security (+ backend) |
| API công khai, hợp đồng giữa dịch vụ | `public_api` | lớn / backend |
| hạ tầng, deploy, hook, CI, quyền chạy | `infra` | lớn / security (+ backend) |
| migration, schema, backfill, xoá dữ liệu | `data_migration` | lớn / data |
| file luật dự án/môi trường, cấu hình harness | `rules` | lớn / security |

Mọi hàng: `risk: high`, `size: large`. Chưa rõ có chạm vùng nào → đề xuất bậc nặng hơn và hỏi phản biện;
không gắn nhãn tự chế như `security` vào `risk_tags`. `rules` / `secret` / `auth` cần hai Tech Reviewer độc lập.

Trường UI có sẵn không tự tạo nhãn `external_input`. Chỉ đổi chữ hoặc chuẩn hoá tìm kiếm cục bộ (trim đầu/cuối)
có thể giữ `risk: normal` khi có bằng chứng giữ nguyên quyền, tenant/danh tính, kiểm tra bảo mật, parser/schema,
hợp đồng API và cách truy vấn/thao tác nhạy cảm; cỡ theo hành vi (sửa một luồng có sẵn là nhỏ). Có thay đổi hoặc
chưa loại trừ tác động lên những ranh giới đó → `external_input`, `risk: high`, `size: large` và review security.

## 2. Danh mục 11 điểm thiếu ngữ cảnh

Rà từng dòng **trước khi viết tin trao đổi**; mỗi dòng kết thúc bằng một trong bốn nhãn: **có** (lời giao hoặc
repo đã trả lời), **hỏi** (thuộc ý muốn người dùng → vào tin trao đổi gom, mục 1.1), **ASSUMPTION** (tự giả định
được, ghi rõ nếu sai thì đổi gì), **CQ** (không tự giả định được và chưa hỏi được ở tin trao đổi — để Cổng 1).

| # | Điểm | Câu hỏi tự đặt | Nguồn tự tra trước khi hỏi |
|---|---|---|---|
| 1 | Mục tiêu | Vì sao cần? Kết quả trông ra sao với người dùng cuối? | lời giao, `RQ-` cũ cùng chủ đề |
| 2 | Người dùng cuối | Ai dùng, trong luồng nào? | spec sống `FS-`, README dự án |
| 3 | Ngăn xếp kỹ thuật | Ngôn ngữ, framework, công cụ build/test? | file cấu hình gốc dự án (`pyproject.toml`, `package.json`…) |
| 4 | Phạm vi file | Module/thư mục nào bị chạm? | mã nguồn, `git log` gần đây |
| 5 | Định nghĩa xong | Thế nào là đạt? Đo bằng gì? | lời giao; nếu không có → hỏi ở tin trao đổi |
| 6 | Xử lý lỗi và biên | Đầu vào xấu, trạng thái lỗi, giới hạn? | kịch bản `FR` hiện có |
| 7 | Bảo mật | Chạm xác thực, phân quyền, secret, đầu vào ngoài? | `risk_tags` của `sizing.md` — có thì nâng cỡ, và loại trừ làm thẳng |
| 8 | Kỳ vọng kiểm thử | Unit / integration / E2E? Ngưỡng coverage? | `method/conventions.md`, cấu hình dự án |
| 9 | Hiệu năng và dữ liệu | Tải, độ trễ, đổi schema, migration, backfill? | schema hiện có |
| 10 | Tiền lệ và quy ước | File mẫu phải theo? ADR liên quan? | `docs/architecture/adr/`, spec sống |
| 11 | Ngoài phạm vi và điều cấm | Cái gì **không** làm đợt này? Điều gì cấm? | lời giao; nếu không có → hỏi ở tin trao đổi |

Đã có thể tra từ repo thì **tra, không hỏi**. Chỉ điểm thuộc ý muốn của người dùng (mục đích, định
nghĩa xong, phạm vi ngoài, ưu tiên) mới thành câu hỏi phản biện trong tin trao đổi — điểm 1, 5, 11 gần như luôn
có mặt; điểm nào người dùng chưa trả lời sau tin đó thì thành `CQ` cho Cổng 1.

**Repo cho biết hệ thống đang làm gì, không cho biết nghiệp vụ đòi gì.** Luật nghiệp vụ, nghĩa vụ pháp lý hay hợp đồng,
chính sách lưu giữ dữ liệu, giá, đối tượng dùng — không đọc ra từ mã. Một hằng trong mã (ví dụ `RETENTION_DAYS`) chỉ nói
mã đó dùng nó cho việc gì, không phải chính sách cho việc khác. Điểm như vậy là câu hỏi phản biện có đề xuất trong tin trao
đổi (hoặc `CQ` có đề xuất nếu còn mở), hoặc ASSUMPTION đánh dấu "cần xác nhận" — không bao giờ ghi như điều đã tra được.

**Tiêu chí xong phải quan sát được.** Lời giao "nhẹ hơn / nhanh hơn / dọn đi" chưa phải tiêu chí: đề xuất tiêu chí đo hay đếm
được (số bản ghi bị chạm, lệnh kiểm, ngưỡng) ngay trong câu hỏi phản biện về định nghĩa xong, hoặc trong `CQ` / ASSUMPTION.
Việc xoá hay ghi đè dữ liệu thì tiêu chí gồm cả **cách khôi phục** (sao lưu, chạy chỉ-đếm trước khi xoá thật).

## 3. ASSUMPTION và `CQ` — viết thế nào

- **ASSUMPTION — <tên>:** <giả định> — nếu sai thì <đổi gì>. Mỗi giả định một dòng, trong SPEC mục
  Câu hỏi cần làm rõ. Người duyệt chỉ lên tiếng khi không đồng ý.
- `CQk (<tên>)` — câu hỏi + **đề xuất** của Analyst + trạng thái `mở`. Mỗi `CQ` phải có đề xuất:
  câu hỏi không kèm đề xuất là đẩy việc nghĩ sang người dùng.
- **Câu trả lời ở tin trao đổi ghi thẳng vào `RQ-` và SPEC** (mục tiêu, định nghĩa xong, phạm vi ngoài) với trạng
  thái `đã trả lời`; không biến chúng thành `CQ` mở, không hỏi lại ở Cổng 1.
- `CQ` còn lại được hỏi **một lần** ở Cổng 1 (cỡ vừa/lớn; cỡ nhỏ trình ngắn), gom trong bản trình chuẩn
  (`method/process.md` mục 3). Hỏi lẻ từng câu giữa chừng là lỗi, trừ chế độ làm rõ do người dùng mở (skill
  `shaping-spec` mục 3).
- Trả lời của người dùng ghi ngay vào ô `CQ` tương ứng; không hỏi lại điều đã có câu trả lời.

## 4. Dấu hiệu tiếp nhận sai

| Thấy | Nghĩa là |
|---|---|
| Ghi `RQ-` hay mở sprint trước khi người dùng xác nhận tin trao đổi | bỏ lượt trao đổi ở việc còn mơ hồ — quay lại mục 1.1 |
| Hỏi người dùng điều repo trả lời được (stack, file chạm, test hiện có) | bỏ bước tra repo; làm lại mục 2 trước khi gửi tin |
| Hỏi một câu, chờ, hỏi câu nữa ở tiếp nhận | không phải một tin gom — gom lại; câu còn lại thành `CQ` cho Cổng 1 |
| Tin trao đổi không có khuyến nghị bậc hay không hỏi "có mở sprint không" | thiếu nửa sau của tin — người dùng không có gì để xác nhận |
| Mở lượt trao đổi cho việc người dùng đã nói "không cần sprint", hoặc làm thẳng không mơ hồ | hỏi thừa — làm ngay và báo |
| Làm thẳng việc chạm `risk_tags`, file luật, secret hay hành động không đảo ngược mà người dùng chưa nói rõ | sai bậc — tối thiểu rất nhỏ, vùng rủi ro kéo lên lớn |
| ≥5 câu hỏi trong tin, hay ≥5 `CQ` | chưa tra đủ, hoặc lời giao chứa nhiều mục tiêu — tách sprint |
| 0 ASSUMPTION ở việc cỡ vừa trở lên | chưa rà; lời giao hiếm khi đủ cả 11 điểm |
| Cỡ rất nhỏ nhưng lời giao chưa nêu rõ kết quả, hoặc hành vi đổi | không phải rất nhỏ — nâng cỡ |
| Dựng bốn file hay gọi hai reviewer cho việc nhỏ / rất nhỏ; hoặc ghi rất nhỏ cho việc sửa một luồng | sai bậc — tra bảng ở mục 1 |
| Diff "chỉ một dòng" ở cấu hình quyền, hook, CI | `risk_tags: [infra]` hoặc `[rules]` → cỡ lớn, không làm thẳng |

## 5. Lỗi hay gặp — và sửa

| Lỗi | Sửa |
|---|---|
| Lời giao mơ hồ → đoán rồi làm luôn | mở tin trao đổi gom: nhắc lại mục tiêu, hỏi phản biện có đề xuất, khuyến nghị bậc; chờ xác nhận |
| Lời giao mơ hồ → tự ghi `RQ-` và ASSUMPTION thay cho hỏi | điều thuộc ý muốn người dùng phải hỏi ở tin trao đổi; ASSUMPTION chỉ cho điều tự giả định được, có "nếu sai thì đổi gì" |
| Hỏi một câu, chờ, hỏi câu nữa | một tin gom ở tiếp nhận; phần còn lại thành `CQ`, hỏi một lần ở Cổng 1 |
| Tự quyết bậc rồi dựng hồ sơ, không hỏi người dùng có cần sprint không | tin trao đổi phải có khuyến nghị bậc + câu "có mở sprint không"; người dùng xác nhận mới ghi |
| Người dùng nói "không cần sprint" mà vẫn mở `RQ-`/`SPRINT.md` | lời người dùng thắng: làm thẳng, kiểm, báo; chỉ giữ các cổng xin phép khác |
| Tech stack ghi "chưa rõ" dù repo có file cấu hình | tra file cấu hình trước; "chưa rõ" chỉ khi dự án mới |
| Bỏ qua phạm vi ngoài | hỏi ở tin trao đổi; luôn có ít nhất một dòng "không làm đợt này", kể cả khi phải suy từ lời giao (ghi ASSUMPTION) |
| Lấy hằng số trong mã làm chính sách nghiệp vụ | hằng là chứng cứ về mã, không về nghiệp vụ: câu hỏi phản biện / `CQ` có đề xuất hoặc ASSUMPTION "cần xác nhận" |
| Lời giao "dọn / nhẹ hơn / nhanh hơn" không có tiêu chí đo | đề xuất tiêu chí quan sát được ngay trong câu hỏi về định nghĩa xong; việc xoá dữ liệu thêm cách khôi phục |
