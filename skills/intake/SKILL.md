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

## 0. Phân loại trước khi chọn người làm

Khi tiếp nhận có quyết định phân công, đọc [task-routing](../../method/task-routing.md) mục 1–3 và 5
trước khi chọn vai/tier/model/effort. Bản phân loại gồm **sáu hàng theo thang của phương pháp**, mỗi hàng
có value · ordinal · nguồn · điều chưa biết · hậu quả nếu sai; thiếu nguồn để `null` kèm lý do.
Sau bảng là difficulty từ ba trục kỹ thuật đủ nguồn, effort theo default/override, assignment baseline
hay candidate, và cách giao có căn cứ. Cỡ/rủi ro và tin trao đổi gom vẫn theo các mục dưới.
Model lấy từ mapping/override **của việc đang phân loại**; model của agent điều phối không thay thế
mapping hay chỉ định cho người nhận việc. Trước PLAN/assignment, tin ngắn có agent/harness · vai · tier · model · effort · phạm vi
· lý do · nguồn duyệt, tách requested/effective/actual; field chưa có bằng chứng để `null` kèm lý do.

## 1. Bảy việc, theo thứ tự

| # | Việc | Ghi vào |
|---|---|---|
| 1 | **Đọc và phân tích** đầu bài: tra repo, sổ gốc, spec sống; đọc `method/sizing.md` mục 1–2 và rà 11 điểm (mục 2) — tra được thì tra, không hỏi | nháp của Analyst |
| 2 | **Một tin trao đổi gom** cho người dùng (mục 1.1): mục tiêu theo cách hiểu · câu hỏi phản biện · khuyến nghị bậc · có mở sprint không | chat |
| 3 | **Chờ xác nhận.** Chưa xác nhận thì chưa `RQ-`, chưa sprint, chưa chạm mã. Người dùng chọn làm thẳng → làm ngay, kiểm, báo; hết bước | — |
| 4 | Một dòng `RQ-` mới: ngày, tóm tắt một câu, trạng thái `mới`, **kèm câu trả lời của người dùng** (mục tiêu đã chốt, định nghĩa xong, phạm vi ngoài, bậc đã xác nhận) | sổ REQUESTS |
| 5 | Tách mục tiêu: một mục tiêu = một sprint; nhiều mục tiêu → nhiều sprint cùng trỏ một `RQ-` | sổ SPRINTS (khi mở sprint) |
| 6 | Ghi bậc đã xác nhận và `risk_tags`; bất kỳ nhãn rủi ro nào ở `method/sizing.md` mục 2 → `risk: high`, `size: large`, kể cả sau xác nhận (báo lại một câu) | frontmatter SPEC |
| 7 | Điểm còn lại ở 11 điểm → **ASSUMPTION** hoặc `CQ` (mục 3); rồi sang skill `shaping-spec`, không hỏi thêm lượt nào tới Cổng 1 | SPEC mục Câu hỏi cần làm rõ |

Lời giao đã nêu rõ mục đích, ràng buộc và kết quả thì phản ánh lại trong tin trao đổi, không hỏi lại điều đã có.

Sau câu trả lời, ô 1, 2 hay 4 của Brief (mục 1.2) còn trống → **một** tin bổ sung duy nhất, mỗi ô một câu có đề xuất; vẫn trống → `CQ` cho Cổng 1, không có lượt thứ ba. "Cứ làm" hay im lặng không thay cho xác nhận bậc và mở sprint; tin bổ sung hỏi rõ hai điều đó. Chưa có câu trả lời ấy thì chưa `RQ-`, chưa mở sprint, chưa ghi bậc; ô còn trống không chặn — thành `CQ`.

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
Brief: mục tiêu · xong · ràng buộc · rủi ro cụ thể và mức tự trị — <đã có / hỏi ở câu k>.
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

### 1.2 Brief người giao — 4 ô

Rà bốn ô trước khi viết tin gom; ô người giao đã nêu thì nhắc lại một dòng, ô trống thành câu hỏi phản biện có đề xuất:

| Ô | Gồm |
|---|---|
| 1. Mục tiêu | mục tiêu việc và mục tiêu sprint (nếu khác) · kết quả · cho ai · vì sao bây giờ |
| 2. Định nghĩa xong | hành vi quan sát được · test/ngưỡng · tài liệu · cách hoàn tác · ai kiểm · điều kiện **không** đạt |
| 3. Ràng buộc và lưu ý | đừng đụng gì · tiền lệ · hạn/ngân sách công sức · quyền agent · bẫy đã biết — chép nguyên văn vào SPEC mục 1.1 |
| 4. Rủi ro cần chú ý · khẩu vị · mức tự trị | dòng 1: rủi ro cụ thể (cái từng hỏng, chỗ dễ vỡ, ai bị ảnh hưởng) + nhãn `risk_tags` bạn bổ sung; dòng 2: sai thì hại tới đâu, hoàn tác được không, mức *hỏi mọi bước* · *trong phạm vi* (mặc định) · *tự quyết* |

*Tự quyết* chỉ là ý muốn chạy không hỏi trong phạm vi đã duyệt — không hạ cỡ, không hạ rủi ro, không phải lời cấp duyệt thay (`method/process.md` mục 3).
Cỡ, tài liệu và cổng theo `method/sizing.md` mục 1; nhãn rủi ro theo mục 2 — chỉ dùng bảy nhãn ở đó, không gắn nhãn tự chế như `security`. Ba luật giữ ở đây: rủi ro chỉ nâng, kể cả sau xác nhận; không chia một mục tiêu thành nhiều lần làm thẳng để né sprint; không làm thẳng khi chạm `risk_tags`, file luật, secret hay hành động không đảo ngược — trừ khi người dùng nói rõ.

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
| Hỏi một câu, chờ, hỏi câu nữa ở tiếp nhận | không phải một tin gom — gom lại; câu còn lại thành `CQ` cho Cổng 1 (trừ một tin bổ sung cho ô Brief còn trống, mục 1) |
| Tin trao đổi không có khuyến nghị bậc hay không hỏi "có mở sprint không" | thiếu nửa sau của tin — người dùng không có gì để xác nhận |
| Mở lượt trao đổi cho việc người dùng đã nói "không cần sprint", hoặc làm thẳng không mơ hồ | hỏi thừa — làm ngay và báo |
| Làm thẳng việc chạm `risk_tags`, file luật, secret hay hành động không đảo ngược mà người dùng chưa nói rõ | sai bậc — tối thiểu rất nhỏ, vùng rủi ro kéo lên lớn |
| ≥5 câu hỏi trong tin, hay ≥5 `CQ` | chưa tra đủ, hoặc lời giao chứa nhiều mục tiêu — tách sprint |
| 0 ASSUMPTION ở việc cỡ vừa trở lên | chưa rà; lời giao hiếm khi đủ cả 11 điểm |
| Cỡ rất nhỏ nhưng lời giao chưa nêu rõ kết quả, hoặc hành vi đổi | không phải rất nhỏ — nâng cỡ |
| Dựng bốn file hay gọi hai reviewer cho việc nhỏ / rất nhỏ; hoặc ghi rất nhỏ cho việc sửa một luồng | sai bậc — tra `method/sizing.md` mục 1 |
| Diff "chỉ một dòng" ở cấu hình quyền, hook, CI | `risk_tags: [infra]` hoặc `[rules]` → cỡ lớn, không làm thẳng |
| Coi *tự quyết* là lời cấp duyệt thay hay lý do hạ cỡ; ô 4 chỉ có khẩu vị mà không có rủi ro cụ thể | sai — mức tự trị không hạ cỡ; dòng 1 của ô 4 là rủi ro cụ thể (mục 1.2) |

## 5. Lỗi hay gặp — và sửa

| Lỗi | Sửa |
|---|---|
| Lời giao mơ hồ → đoán rồi làm luôn | mở tin trao đổi gom: nhắc lại mục tiêu, hỏi phản biện có đề xuất, khuyến nghị bậc; chờ xác nhận |
| Lời giao mơ hồ → tự ghi `RQ-` và ASSUMPTION thay cho hỏi | điều thuộc ý muốn người dùng phải hỏi ở tin trao đổi; ASSUMPTION chỉ cho điều tự giả định được, có "nếu sai thì đổi gì" |
| Hỏi một câu, chờ, hỏi câu nữa | một tin gom ở tiếp nhận; phần còn lại thành `CQ`, hỏi một lần ở Cổng 1 (trừ một tin bổ sung cho ô Brief còn trống, mục 1) |
| Tự quyết bậc rồi dựng hồ sơ, không hỏi người dùng có cần sprint không | tin trao đổi phải có khuyến nghị bậc + câu "có mở sprint không"; người dùng xác nhận mới ghi |
| Người dùng nói "không cần sprint" mà vẫn mở `RQ-`/`SPRINT.md` | lời người dùng thắng: làm thẳng, kiểm, báo; chỉ giữ các cổng xin phép khác |
| Tech stack ghi "chưa rõ" dù repo có file cấu hình | tra file cấu hình trước; "chưa rõ" chỉ khi dự án mới |
| Bỏ qua phạm vi ngoài | hỏi ở tin trao đổi; luôn có ít nhất một dòng "không làm đợt này", kể cả khi phải suy từ lời giao (ghi ASSUMPTION) |
| Lấy hằng số trong mã làm chính sách nghiệp vụ | hằng là chứng cứ về mã, không về nghiệp vụ: câu hỏi phản biện / `CQ` có đề xuất hoặc ASSUMPTION "cần xác nhận" |
| Lời giao "dọn / nhẹ hơn / nhanh hơn" không có tiêu chí đo | đề xuất tiêu chí quan sát được ngay trong câu hỏi về định nghĩa xong; việc xoá dữ liệu thêm cách khôi phục |
