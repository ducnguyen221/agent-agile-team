---
name: intake
description: Use when a user hands over a new request in plain words (feature, fix, change, question that implies work) and before any SPEC is written — to register it, size it, surface assumptions and collect missing context into one list of clarification questions instead of asking piecemeal.
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

> **Kết luận:** tiếp nhận là bước **không cổng**: ghi `RQ-`, tách mục tiêu, định cỡ và rủi ro (chỉ
> nâng), rà **11 điểm thiếu ngữ cảnh**, ghi giả định dưới nhãn **ASSUMPTION**, gom điểm không tự giả
> định được thành `CQ` — rồi đi thẳng sang SPEC. Hỏi người dùng ở bước này là lỗi quy trình.

## 1. Năm việc, theo thứ tự

| # | Việc | Ghi vào |
|---|---|---|
| 1 | Một dòng `RQ-` mới: ngày, tóm tắt một câu, trạng thái `mới` | sổ REQUESTS |
| 2 | Tách mục tiêu: một mục tiêu = một sprint; nhiều mục tiêu → nhiều sprint cùng trỏ một `RQ-` | sổ SPRINTS (khi mở sprint) |
| 3 | Định cỡ (rất nhỏ / nhỏ / vừa / lớn) và rủi ro theo `method/sizing.md`; chạm vùng rủi ro → `risk: high`, cỡ tối thiểu lớn | frontmatter SPEC |
| 4 | Rà 11 điểm thiếu ngữ cảnh (mục 2) → mỗi điểm thành **ASSUMPTION** hoặc `CQ` | SPEC mục Câu hỏi cần làm rõ |
| 5 | Đi tiếp sang skill `shaping-spec`. Không dừng chờ | — |

Lời giao đã nêu rõ mục đích, ràng buộc và kết quả thì phản ánh lại, không hỏi lại điều đã có.

**Cỡ quyết hình tài liệu và cổng** (bảng đầy đủ: `method/sizing.md` mục 1) — ghi cỡ kèm hình này:

| Cỡ | Dấu hiệu đo được | Tài liệu | Cổng 1 · kiểm định |
|---|---|---|---|
| Rất nhỏ | đổi chữ hoặc một chỗ — kể cả chữ kỳ vọng trong test đi kèm, số file chạm không quyết cỡ; không đổi hành vi, quyền; lời giao đã nêu rõ kết quả | một `SPRINT.md` hai phần **Kế hoạch** (mục tiêu, `SC`, `TK` trỏ `SC`) · **Kết quả** (`VR` mỗi `SC`) | "đạt theo lời giao" + trích lời giao; không mở lượt hỏi mới (`method/process.md` mục 9) · agent khác chạy nhanh, hoặc tự kiểm "chưa độc lập" (tối đa Đạt có điều kiện); Cổng 2 gộp lời báo cuối |
| Nhỏ | sửa cục bộ một luồng có sẵn (hành vi đổi), một `FR`, không đổi hợp đồng / giao diện / schema | một `SPRINT.md` đủ bốn phần SPEC · PLAN · PROGRESS · REPORT | Cổng 1 thật (trình ngắn, chờ duyệt) · **một** reviewer khác người làm kiểm cả nghiệp vụ lẫn kỹ thuật; Cổng 2 thật |
| Vừa · Lớn | tính năng hoặc luồng mới; đổi hợp đồng, schema; rủi ro cao | bốn file | đủ hai cổng; cả hai reviewer |

Phân vân giữa hai bậc → bậc nặng hơn; hạ cỡ chỉ ở Cổng 1 do người dùng. Hành vi đổi thì không phải rất nhỏ.

## 2. Danh mục 11 điểm thiếu ngữ cảnh

Rà từng dòng; mỗi dòng kết thúc bằng một trong ba nhãn: **có** (lời giao hoặc repo đã trả lời),
**ASSUMPTION** (tự giả định được, ghi rõ nếu sai thì đổi gì), **CQ** (không tự giả định được).

| # | Điểm | Câu hỏi tự đặt | Nguồn tự tra trước khi hỏi |
|---|---|---|---|
| 1 | Mục tiêu | Vì sao cần? Kết quả trông ra sao với người dùng cuối? | lời giao, `RQ-` cũ cùng chủ đề |
| 2 | Người dùng cuối | Ai dùng, trong luồng nào? | spec sống `FS-`, README dự án |
| 3 | Ngăn xếp kỹ thuật | Ngôn ngữ, framework, công cụ build/test? | file cấu hình gốc dự án (`pyproject.toml`, `package.json`…) |
| 4 | Phạm vi file | Module/thư mục nào bị chạm? | mã nguồn, `git log` gần đây |
| 5 | Định nghĩa xong | Thế nào là đạt? Đo bằng gì? | lời giao; nếu không có → `CQ` |
| 6 | Xử lý lỗi và biên | Đầu vào xấu, trạng thái lỗi, giới hạn? | kịch bản `FR` hiện có |
| 7 | Bảo mật | Chạm xác thực, phân quyền, secret, đầu vào ngoài? | `risk_tags` của `sizing.md` — có thì nâng cỡ |
| 8 | Kỳ vọng kiểm thử | Unit / integration / E2E? Ngưỡng coverage? | `method/conventions.md`, cấu hình dự án |
| 9 | Hiệu năng và dữ liệu | Tải, độ trễ, đổi schema, migration, backfill? | schema hiện có |
| 10 | Tiền lệ và quy ước | File mẫu phải theo? ADR liên quan? | `docs/architecture/adr/`, spec sống |
| 11 | Ngoài phạm vi và điều cấm | Cái gì **không** làm đợt này? Điều gì cấm? | lời giao, ràng buộc chung dự án |

Đã có thể tra từ repo thì **tra, không hỏi**. Chỉ điểm thuộc ý muốn của người dùng (mục đích, định
nghĩa xong, phạm vi ngoài, ưu tiên) mới thành `CQ`.

**Repo cho biết hệ thống đang làm gì, không cho biết nghiệp vụ đòi gì.** Luật nghiệp vụ, nghĩa vụ pháp lý hay hợp đồng,
chính sách lưu giữ dữ liệu, giá, đối tượng dùng — không đọc ra từ mã. Một hằng trong mã (ví dụ `RETENTION_DAYS`) chỉ nói
mã đó dùng nó cho việc gì, không phải chính sách cho việc khác. Điểm như vậy là `CQ` có đề xuất, hoặc ASSUMPTION đánh dấu
"cần xác nhận" — không bao giờ ghi như điều đã tra được.

**Tiêu chí xong phải quan sát được.** Lời giao "nhẹ hơn / nhanh hơn / dọn đi" chưa phải tiêu chí: đề xuất tiêu chí đo hay đếm
được (số bản ghi bị chạm, lệnh kiểm, ngưỡng) trong `CQ` hoặc ASSUMPTION. Việc xoá hay ghi đè dữ liệu thì tiêu chí gồm cả
**cách khôi phục** (sao lưu, chạy chỉ-đếm trước khi xoá thật).

## 3. ASSUMPTION và `CQ` — viết thế nào

- **ASSUMPTION — <tên>:** <giả định> — nếu sai thì <đổi gì>. Mỗi giả định một dòng, trong SPEC mục
  Câu hỏi cần làm rõ. Người duyệt chỉ lên tiếng khi không đồng ý.
- `CQk (<tên>)` — câu hỏi + **đề xuất** của Analyst + trạng thái `mở`. Mỗi `CQ` phải có đề xuất:
  câu hỏi không kèm đề xuất là đẩy việc nghĩ sang người dùng.
- `CQ` được hỏi **một lần** ở Cổng 1, gom trong bản trình chuẩn (`method/process.md` mục 3). Hỏi lẻ
  từng câu giữa chừng là lỗi, trừ chế độ làm rõ do người dùng mở (skill `shaping-spec` mục 3).
- Trả lời của người dùng ghi ngay vào ô `CQ` tương ứng; không hỏi lại điều đã có câu trả lời.

## 4. Dấu hiệu tiếp nhận sai

| Thấy | Nghĩa là |
|---|---|
| Hỏi người dùng trước khi mở SPEC | bỏ bước tra repo; làm lại mục 2 |
| ≥5 `CQ` | chưa tra đủ, hoặc lời giao chứa nhiều mục tiêu — tách sprint |
| 0 ASSUMPTION ở việc cỡ vừa trở lên | chưa rà; lời giao hiếm khi đủ cả 11 điểm |
| Cỡ rất nhỏ nhưng lời giao chưa nêu rõ kết quả, hoặc hành vi đổi | không phải rất nhỏ — nâng cỡ |
| Dựng bốn file hay gọi hai reviewer cho việc nhỏ / rất nhỏ; hoặc ghi rất nhỏ cho việc sửa một luồng | sai bậc — tra bảng ở mục 1 |
| Diff "chỉ một dòng" ở cấu hình quyền, hook, CI | `risk_tags: [infra]` hoặc `[rules]` → cỡ lớn |

## 5. Lỗi hay gặp — và sửa

| Lỗi | Sửa |
|---|---|
| Lời giao mơ hồ → đoán rồi làm luôn | ghi ASSUMPTION có "nếu sai thì đổi gì"; điểm không đoán được thành `CQ` |
| Hỏi một câu, chờ, hỏi câu nữa | gom hết vào `CQ`, hỏi một lần ở Cổng 1 |
| Tech stack ghi "chưa rõ" dù repo có file cấu hình | tra file cấu hình trước; "chưa rõ" chỉ khi dự án mới |
| Bỏ qua phạm vi ngoài | luôn có ít nhất một dòng "không làm đợt này", kể cả khi phải suy từ lời giao (ghi ASSUMPTION) |
| Lấy hằng số trong mã làm chính sách nghiệp vụ | hằng là chứng cứ về mã, không về nghiệp vụ: `CQ` có đề xuất hoặc ASSUMPTION "cần xác nhận" |
| Lời giao "dọn / nhẹ hơn / nhanh hơn" không có tiêu chí đo | đề xuất tiêu chí quan sát được; việc xoá dữ liệu thêm cách khôi phục |
