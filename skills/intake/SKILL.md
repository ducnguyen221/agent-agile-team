---
name: intake
description: Use when a user hands over a new request in plain words (feature, fix, change, question that implies work) and before any SPEC is written — to register it, size it, surface assumptions and collect missing context into one list of clarification questions instead of asking piecemeal.
metadata:
  group: process
  roles: [analyst]
source: "affaan-m/ECC skills/prompt-optimizer (missing-context checklist, via local distill); method/process.md step 1"
source_sha: c70874fae9eb0e5ad0365beb7e2955899fd1d30f
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: MIT
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
| Cỡ rất nhỏ nhưng lời giao chưa nêu rõ kết quả | không phải rất nhỏ — nâng cỡ |
| Diff "chỉ một dòng" ở cấu hình quyền, hook, CI | `risk_tags: [infra]` hoặc `[rules]` → cỡ lớn |

## 5. Lỗi hay gặp — và sửa

| Lỗi | Sửa |
|---|---|
| Lời giao mơ hồ → đoán rồi làm luôn | ghi ASSUMPTION có "nếu sai thì đổi gì"; điểm không đoán được thành `CQ` |
| Hỏi một câu, chờ, hỏi câu nữa | gom hết vào `CQ`, hỏi một lần ở Cổng 1 |
| Tech stack ghi "chưa rõ" dù repo có file cấu hình | tra file cấu hình trước; "chưa rõ" chỉ khi dự án mới |
| Bỏ qua phạm vi ngoài | luôn có ít nhất một dòng "không làm đợt này", kể cả khi phải suy từ lời giao (ghi ASSUMPTION) |
