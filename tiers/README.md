# Tier

> **Kết luận:** vai được chỉ định theo **tier** (T1 tư duy · T2 thực thi · T3 việc vặt **và QA / chạy
> test**), không theo tên model. Lõi chỉ biết ba tên tier; bảng tier → model nằm **ngoài repo** và được
> đọc lúc giao việc. Cạn hạn mức thì **dừng, ghi `BR`, báo** — không tự hạ tier. Gọi chéo hãng chỉ **tư
> vấn**, người dùng quyết. Luôn ghi model thực tế khi giao việc.

## 1. Ba tier

| Tier | Mục đích | Vai mặc định | Việc tiêu biểu |
|---|---|---|---|
| `T1` | **Tư duy** — phân tích, thiết kế, kiểm định | Analyst, Architect, Business Reviewer, Tech Reviewer (+ chuyên đề) | tiếp nhận, SPEC, PLAN, ADR, review, phán quyết, REPORT, bài học |
| `T2` | **Thực thi** — viết mã, viết tài liệu theo plan | Implementer | hiện thực `TK`, test, sửa theo review, tài liệu kỹ thuật |
| `T3` | **Việc vặt và QA / chạy test** | QA | chạy bộ test, đo coverage, kiểm trình duyệt theo kịch bản, đổi tên, dọn file, chạy script sinh, đối chiếu số |

Nguyên tắc chọn: việc cần **suy luận hoặc phán xét** → T1; việc có PLAN rõ, cần **viết** → T2; việc có
lệnh rõ, cần **chạy và ghi** → T3. Phân vân giữa hai tier → chọn tier **cao hơn** và ghi lý do.

## 2. Hợp đồng điểm cắm `AGENT_AGILE_TIERS`

- **Giá trị:** đường dẫn tuyệt đối tới một file JSON bảng tier → model. File nằm **ngoài** repo, do môi
  trường dùng repo quản lý. Repo không bao giờ chứa tên model thật.
- **Hình dạng:** như [`tiers.example.json`](tiers.example.json) — khóa `schema` (số nguyên, hiện là `1`)
  và `tiers`; mỗi tier có `purpose` và `models` ánh xạ tên harness → mã model của harness đó.
- **Khi thiếu biến, file không tồn tại hoặc đọc lỗi:** công cụ báo **Chưa chạy** cho phần cần bảng tier,
  không đoán model, không lấy giá trị mặc định (`init` cảnh báo ngay khi dựng sprint). Agent giao việc dùng
  **chỉ định tier → model người dùng đã nêu trong chat** — một nguồn hợp lệ ngang bảng: ghi nguyên văn vào
  nhật ký PROGRESS dòng `Phán quyết:` và phần tử `"note"` trong `roles`. Chưa có cả bảng lẫn chỉ định → hỏi
  **ở Cổng 1**, kèm khuyến nghị (`method/process.md` mục 3) — không hỏi lẻ, không đoán tên model.
- **Khi thiếu một harness hay một tier trong bảng:** báo Chưa chạy cho đúng ô đó; không tự hạ sang tier
  khác. Môi trường chưa chốt model cho T3 thì người dùng chỉ định tier thay thế **từng lượt** (mục 4).

## 3. Giao việc: luôn ghi model

Routing/effort dùng [method/task-routing.md](../method/task-routing.md). Tier mặc định của vai, tier tra
bảng, requested model và human override là các field riêng. Default effort medium áp coordinator cho
routed assignment; native support phải verified, actual unknown không lấy requested thay. Notice trước
dispatch/model/effort/criteria/handoff; không ghi model ID môi trường vào policy phân phối.

KHI giao một `TK` cho subagent hoặc phiên khác THÌ Analyst:

1. Đọc tier của vai trong PLAN (`TK` ghi vai + tier).
2. Tra bảng tier → model theo harness đang dùng.
3. Ghi vào PROGRESS, cột "Vai · tier · model": `Implementer · T2 · <model-id>`; nhãn agent vào `roles`
   của frontmatter (`implementer: [T2, agent-e]`).
4. Ghi model vào brief của subagent chỉ khi harness cần tham số; không ghi tên model vào SPEC/PLAN.

Thiếu bước 3 là phát hiện mức **Phải sửa** khi kiểm PROGRESS: không có model thì không so được kết quả
giữa các lượt và không truy được lỗi do model.

## 4. Người dùng chỉ định đè

KHI người dùng chỉ định một model khác tier mặc định cho một lượt (ví dụ model T2 làm Architect, hoặc model
T1 làm QA vì chưa có T3) THÌ làm theo và ghi phần tử thứ ba `"note"` trong `roles`:

```
architect: [T1, agent-b, "owner assigned a T2 model for this run"]
```

Chỉ định đè có hiệu lực trong **scope người dùng đã nói**, có thể một lượt, một vai hoặc cả task; ghi
quote/source/scope và expiry nếu có. Chỉ định mới nhất trong scope thắng từng field. Model-only không
đổi effort; effort-only không đổi model. Hết scope quay về baseline; agent không tự kéo dài hoặc tự
thu hẹp chỉ định cả task thành một lượt. Capability/quyền/risk và reviewer không bị override.

## 5. Cạn hạn mức: dừng, không tự hạ tier

KHI model của một tier báo hết hạn mức, bị giới hạn tốc độ kéo dài, hoặc không gọi được THÌ:

1. Dừng phần việc của tier đó (việc của tier khác vẫn chạy nếu độc lập).
2. Ghi `BR` vào PROGRESS: tier nào, model nào, lỗi gì, việc nào đang chờ.
3. Báo người dùng với lựa chọn: chờ hạn mức · chỉ định đè sang model khác (mục 4) · dừng và bàn giao phần
   đã đạt.

**Không** tự chuyển sang tier thấp hơn, không tự đổi hãng. Lý do: tier thấp hơn làm việc của tier cao
cho ra sản phẩm trông xong mà không ai biết nó được làm bằng năng lực nào — đó là tự chấm trá hình.

## 6. Gọi chéo hãng: chỉ tư vấn

KHI agent thấy một vai nên dùng model của hãng khác (ví dụ reviewer khác hãng với người làm để có góc nhìn
độc lập) THÌ **tư vấn**, không tự chạy:

```
Tư vấn gọi chéo: <vai> → <hãng/tier> — vì <lý do một câu> — chi phí <ước lượng, hoặc "chưa đo">.
Cần người dùng gật; đi qua cầu gọi chéo của môi trường.
```

Người dùng gật thì gọi qua **cầu gọi chéo do lớp riêng cung cấp** (điểm cắm trong `hosts/`), ghi model
và hãng vào PROGRESS như mục 3. Không có cầu thì ghi "cần người duyệt" và làm phần còn lại.

## 7. Bảng tra nhanh

| Tình huống | Làm gì |
|---|---|
| Không có bảng tier | Dùng chỉ định tier → model trong chat (ghi nguyên văn vào `Phán quyết:`); chưa có thì hỏi ở Cổng 1 kèm khuyến nghị; không đoán |
| Vai cần tier chưa có model | Người dùng chỉ định đè từng lượt + `"note"` |
| Cạn hạn mức | Dừng tier đó, `BR`, báo; không hạ tier |
| Muốn hãng khác | Tư vấn một lần; người dùng quyết |
| Giao việc | Ghi vai · tier · model vào PROGRESS, nhãn agent vào `roles` |
| Phân vân tier | Chọn cao hơn, ghi lý do |
