---
name: plan-review
description: Use when a draft PLAN (or design doc, or SPEC plus PLAN) must be reviewed before Gate 1 - from medium size up, or when asked to lock in a plan, challenge its scope, or check architecture, code quality, test coverage and performance before any code is written.
source: [garrytan/gstack plan-eng-review/SKILL.md.tmpl, garrytan/gstack plan-eng-review/sections/review-sections.md.tmpl]
source_sha: [96764e80a641e28141ec8297223768029f5bf483, 96764e80a641e28141ec8297223768029f5bf483]
base_sha: 4c0fdc5736a49b6223a7dfc7626d5495cf55185c
license: MIT
rewrite_before_public: false
metadata:
  group: verification
  roles: [tech-reviewer]
---

# Review PLAN trước Cổng 1

> **Kết luận:** Tech Reviewer (agent khác Architect) soi PLAN **trước khi viết dòng code nào**: Bước 0
> thách phạm vi luôn chạy trước; rồi bốn phần Kiến trúc · Chất lượng code · Test · Hiệu năng, không bỏ
> phần nào. Mỗi vấn đề là **một** `RF` riêng kèm 2–3 phương án và **khuyến nghị có chính kiến**. Test là
> lõi: sơ đồ phủ cho mọi nhánh code và luồng người dùng; **mỗi hành vi có test, không test nào thiếu một
> hồi quy nó bắt được**. Review không duyệt cách sửa nào — người dùng duyệt ở Cổng 1.

## 1. Vị trí trong quy trình

- **Khi nào:** Bước 2, sau khi Architect viết PLAN nháp, trước khi trình Cổng 1 — bắt buộc từ cỡ **vừa**;
  cỡ nhỏ khi PLAN có quyết định mở hoặc rủi ro nâng cỡ.
- **Đầu vào (ngữ cảnh soạn riêng, không dán lịch sử phiên):** SPEC + PLAN nháp; spec sống của tính năng;
  ADR liên quan (`docs/architecture/adr/`); REQUESTS (việc hoãn có chặn PLAN không); nếu có, bản thiết kế
  trước — **cái gì đổi và vì sao** thường là chỗ có rủi ro. Không có gì ngoài PLAN → nói rõ "review không có
  căn cứ thiết kế để đối chiếu" rồi làm tiếp.
- **Đầu ra:** `RF` theo thang chung (ghi ở REPORT, PROGRESS ghi một dòng vòng review PLAN trỏ tới) · các
  mục bắt buộc ở mục 7 · kết luận Đạt / Đạt có điều kiện / Không đạt cho PLAN · "Không đánh giá".
- **Ai sửa:** Architect sửa PLAN; reviewer **không** viết lại PLAN. Quyết định cần người → Analyst gom
  thành `DN`/`CQ` trình ở Cổng 1, không hỏi lẻ giữa chừng.

**Thứ tự ưu tiên khi ngữ cảnh bị nén:** Bước 0 > sơ đồ phủ test > khuyến nghị có chính kiến > phần còn
lại. Không bao giờ bỏ Bước 0 hay sơ đồ test.

## 2. Ưu tiên kỹ thuật mà review áp

- **Code dùng chung** chỉ khi hành vi thật sự chung và tăng độ tin cậy hoặc tiết kiệm ròng; trông giống
  nhau chưa đủ. Trùng lặp thật thì gắn mạnh tay.
- **Test:** mỗi hành vi có test; **không test nào không có hồi quy mà nó bắt được** (test chỉ để tăng
  coverage là nợ).
- **Vừa đủ kỹ thuật:** không mong manh, không trừu tượng sớm.
- **Nhiều trường hợp biên hơn, không ít hơn.** Kỹ hơn nhanh.
- **Rõ ràng hơn khéo léo.**
- **Diff đúng cỡ:** nhỏ nhất mà vẫn rõ; nền móng hỏng thì nói thẳng "bỏ, làm thế này".
- **Sơ đồ ASCII** cho luồng dữ liệu, máy trạng thái, phụ thuộc, pipeline; sơ đồ cũ sai còn tệ hơn không có
  — cập nhật cùng commit, gắn cả sơ đồ cũ ngoài phạm vi.

Lăng kính khi đọc (không phải checklist): bán kính nổ của mỗi quyết định · công nghệ nhàm chán mặc định
(mỗi đội chỉ có vài "token đổi mới") · tăng dần hơn đập đi làm lại · thiết kế cho người mệt lúc 3 giờ sáng ·
ưu tiên đảo ngược được (flag, rollout dần) · độ phức tạp bản chất hay tự tạo · làm cho thay đổi dễ trước
rồi mới làm thay đổi dễ (không trộn đổi cấu trúc với đổi hành vi trong một bước).

## 3. Bước 0 — Thách phạm vi (không bao giờ bỏ)

1. **Cái gì đã giải quyết việc này?** Code, thư viện, luồng sẵn có phủ từng bài toán con tới đâu; lấy
   output của luồng sẵn có được không thay vì dựng luồng song song?
2. **Tối thiểu cần gì** để đạt mục tiêu? Gắn mọi thứ hoãn được; cứng rắn với phình phạm vi.
3. **Độ phức tạp:** đếm file sẽ đổi và lớp/dịch vụ mới **trong PLAN** (không đếm file chỉ đọc làm bằng
   chứng). **≥8 file hoặc ≥2 lớp/dịch vụ mới** là mùi → đề xuất phương án nhỏ hơn giữ nguyên danh sách
   tính năng, hợp đồng và các bản sửa đã duyệt.
4. **Có sẵn trong framework không?** Mỗi mẫu kiến trúc, thành phần hạ tầng, cách xử lý đồng thời mới:
   framework có sẵn chưa, còn là thực hành hiện hành không, bẫy đã biết? Không có tìm kiếm web → ghi "không
   tra được, chỉ dựa kiến thức sẵn có".
5. **Đối chiếu REQUESTS:** việc hoãn nào chặn PLAN; gộp được gì mà không nở phạm vi; PLAN sinh việc hoãn
   mới nào (đề xuất `RQ-`).
6. **Đầy đủ hay đi tắt?** Với agent thực thi, chi phí biên của bản đầy đủ (đủ test, đủ nhánh lỗi) thấp hơn
   nhiều so với đội người; đi tắt chỉ tiết kiệm vài phút → khuyến nghị bản đầy đủ.
7. **Phân phối:** PLAN tạo loại sản phẩm mới (CLI, gói, image) → có bước build và phát hành chưa? Hoãn thì
   ghi vào "Ngoài phạm vi" để không rơi im lặng.

Đề xuất thu phạm vi là `RF` có phương án; người dùng chọn ở Cổng 1. **Đã chọn thì theo hẳn** — không cãi
lại ở phần sau, không lặng lẽ thu nhỏ.

**Luật chống bỏ phần:** đi đủ bốn phần dưới với mọi loại PLAN. "Đây là tài liệu chiến lược nên phần thực
thi không áp dụng" luôn sai — thực thi là chỗ chiến lược gãy. Phần không có gì → ghi "Không có phát hiện"
và đi tiếp. Mỗi phần tối đa 8 vấn đề hàng đầu.

## 4. Bốn phần review

**Kiến trúc.** Ranh giới thành phần, phụ thuộc, độ dính · luồng dữ liệu, nút cổ chai, điểm hỏng đơn lẻ,
khả năng mở rộng · bảo mật kiến trúc (xác thực, truy cập dữ liệu, ranh giới API, **phạm vi tenant**) ·
luồng nào cần sơ đồ · **mỗi đường code/điểm tích hợp mới: một kịch bản hỏng thật ở môi trường thật** và
PLAN có xử lý không · đường build/phát hành của sản phẩm mới.

**Chất lượng code.** Cấu trúc module · cơ hội dùng chung (theo ưu tiên ở mục 2; kiểm giả định về bên gọi
với giao diện thật, tương thích bên gọi) · **gọi tên** khoảng trống xử lý lỗi và trường hợp biên · nợ kỹ
thuật, độ mong manh · sơ đồ trong file bị chạm còn đúng không.

**Test** — lõi của skill, mục 5.

**Hiệu năng.** N+1 và mẫu truy cập CSDL · bộ nhớ · cơ hội cache · đường chậm hoặc phức tạp. Tuyên bố hiệu
năng cần số đo, không có thì ghi "chưa đo" + cách đo.

## 5. Review test

Mục tiêu: 100 % đường code **mới** có test. PLAN thiếu test → thêm vào PLAN (qua `RF`), để khi thực thi
test được viết cùng code.

1. **Nhận diện framework test:** mục Testing trong `AGENTS.md` (nếu có, là chuẩn); nếu không, dò file cấu
   hình test và thư mục `tests/`. Không có framework → vẫn vẽ sơ đồ phủ, ghi khoảng trống hạ tầng test.
2. **Lần mọi đường code** theo thực thi dự kiến, không liệt kê hàm: mỗi điểm vào (route, hàm export, sự
   kiện, render) — đầu vào từ đâu, biến đổi gì, đi đâu, mỗi bước hỏng thế nào (rỗng, sai kiểu, mạng lỗi,
   tập rỗng).
3. **Vẽ luồng người dùng, tương tác, trạng thái lỗi:** hành trình đủ bước · bấm đúp/gửi lại nhanh · rời
   trang giữa chừng · dữ liệu cũ (phiên hết hạn) · mạng chậm · hai tab cùng lúc · lỗi người dùng thấy (thông
   báo rõ hay hỏng im lặng, khôi phục được không) · rỗng/không/biên (0 kết quả, 10.000 kết quả, độ dài tối đa).
4. **Đối chiếu từng nhánh với test hiện có**, cả hai vế if/else và từng nhánh lỗi. Chất lượng: ★★★ hành
   vi + biên + nhánh lỗi · ★★ chỉ đường thuận · ★ chỉ kiểm tồn tại.
5. **Chọn lớp test:** đánh `[→E2E]` cho luồng chung đi qua ≥3 thành phần, điểm tích hợp mà mock che lỗi
   thật, mọi luồng xác thực/thanh toán/xoá dữ liệu; `[→EVAL]` cho lời gọi mô hình, template prompt, định
   nghĩa công cụ; còn lại test đơn vị.
6. **Luật sắt hồi quy:** thay đổi làm gãy hành vi đang chạy (sửa hành vi cũ mà bộ test chưa phủ đường đó,
   hoặc thêm kiểu hỏng mới cho bên gọi cũ) → test hồi quy vào PLAN là **bắt buộc**, `RF` mức **Phải sửa**
   trở lên, không đưa thành lựa chọn. Phân vân có phải hồi quy không → viết test.
7. **Giá trị của từng test đề xuất:** mỗi test ghi hành vi nó bảo vệ và hồi quy nó bắt; đề xuất bỏ test
   không bắt được hồi quy nào ("test nên gỡ").
8. **Sơ đồ phủ** — đường code và luồng người dùng cạnh nhau:

```
ĐƯỜNG CODE                                LUỒNG NGƯỜI DÙNG
[+] services/billing.py                   [+] Thanh toán
  ├── process_payment()                     ├── [★★★ CÓ TEST] mua trọn — test_checkout.py:15
  │   ├── [★★★ CÓ TEST] thuận + từ chối     ├── [THIẾU] [→E2E] bấm đúp nút gửi
  │   ├── [THIẾU] mạng quá hạn              └── [THIẾU] rời trang giữa chừng
  │   └── [THIẾU] tiền tệ sai
  └── refund_payment()                    [+] Trạng thái lỗi
      └── [★★ CÓ TEST] hoàn toàn phần       └── [THIẾU] thông báo khi mạng quá hạn

LLM: [THIẾU] [→EVAL] đổi template prompt — cần eval
PHỦ: 4/10 đường (40 %) | Code 3/5 | Luồng 1/5 | THIẾU: 6 (1 E2E, 1 eval)
```

   Phủ đủ → một dòng "mọi đường code mới đã có test".
9. **Thêm test thiếu vào PLAN:** mỗi chỗ THIẾU ghi file test (theo cách đặt tên sẵn có), khẳng định cụ thể
   (đầu vào → kỳ vọng), lớp test; hồi quy ghi rõ cái gì gãy.
10. **Kế hoạch kiểm trình duyệt cho QA** (khi có giao diện): ghi `test-plan.md` trong thư mục sprint — trang
    / route bị ảnh hưởng và vì sao · tương tác cần kiểm · trường hợp biên · đường găng phải chạy được. Chỉ
    ghi **kiểm gì, ở đâu**, không chi tiết hiện thực. Skill `web-qa` dùng file này làm đầu vào chính.

## 6. Cách viết một vấn đề

- **Một vấn đề = một `RF`**, không gộp. Mô tả cụ thể, có `file:dòng` (của PLAN hoặc code hiện có).
- 2–3 phương án, gồm "không làm gì" khi hợp lý; mỗi phương án một dòng: công, rủi ro, gánh bảo trì. Bản
  đầy đủ chỉ tốn hơn chút → khuyến nghị bản đầy đủ.
- **Khuyến nghị có chính kiến**, nối với một ưu tiên ở mục 2.
- Đánh số vấn đề + chữ phương án ("`RF3` — phương án B"), chọn được trong năm giây.
- Không có lựa chọn thật (sửa hiển nhiên) → ghi việc sẽ làm, không biến thành câu hỏi. Chỉ dùng câu hỏi
  cho quyết định thật.
- Kèm **độ tin cậy** N/10: 9–10 đã đối chiếu code cụ thể · 7–8 khớp mẫu rõ · 5–6 có thể dương tính giả,
  ghi "tin cậy vừa, cần kiểm" · 3–4 để phụ lục · 1–2 chỉ báo nếu mức sẽ là Chặn. Dạng dòng:
  `[Mức] (tin cậy N/10) file:dòng — mô tả`. Báo dưới 7 mà người dùng xác nhận là thật → ghi `LN` về cách hiệu
  chỉnh.

## 7. Mục bắt buộc của bản review

- **Ngoài phạm vi:** việc đã cân nhắc và hoãn rõ ràng, mỗi việc một dòng lý do.
- **Cái đã có:** code/luồng sẵn có giải quyết một phần; PLAN tái dùng hay dựng lại.
- **Đề xuất việc hoãn** (thành `RQ-`): mỗi đề xuất ghi gì · vì sao · lợi · hại · ngữ cảnh (đủ để ba tháng
  sau người nhận hiểu động cơ, hiện trạng, chỗ bắt đầu) · phụ thuộc. Việc hoãn không ngữ cảnh tệ hơn không
  có.
- **Sơ đồ:** luồng nào trong PLAN cần sơ đồ, file nào nên có sơ đồ trong comment.
- **Kiểu hỏng:** mỗi đường code mới — một kiểu hỏng thật (quá hạn, null, race, dữ liệu cũ) và (1) có test
  không, (2) có xử lý lỗi không, (3) người dùng thấy lỗi rõ hay hỏng im lặng. **Không test + không xử lý +
  im lặng = khoảng trống nghiêm trọng**, `RF` mức Chặn.
- **Chia làn song song:** bỏ qua khi mọi bước chạm cùng module hoặc dưới hai luồng việc độc lập. Nếu không:
  bảng phụ thuộc **theo module/thư mục** (không theo file — PLAN mô tả ý định); làn: không chung module, không
  phụ thuộc → làn riêng; chung module → cùng làn, tuần tự; phụ thuộc → làn sau; thứ tự chạy; cờ xung đột khi
  hai làn song song chạm cùng thư mục. Dùng cho `running-sprint`.
- **Quyết định chưa giải:** câu hỏi người dùng chưa trả lời → liệt kê "quyết định chưa giải có thể cắn
  sau"; **không bao giờ lặng lẽ chọn mặc định**.
- **Tóm tắt:** Bước 0 (giữ nguyên / thu theo khuyến nghị) · số vấn đề mỗi phần · sơ đồ test (số chỗ thiếu)
  · số khoảng trống nghiêm trọng · số làn · số quyết định chưa giải · kết luận · Không đánh giá.

## 8. Hồi cứu

Xem `git log` của nhánh tìm dấu một vòng review trước (refactor do review, revert). PLAN chạm lại vùng đó →
soi kỹ hơn: chỗ từng có vấn đề thường có lại.

## 9. Ý kiến ngoài

Muốn ý kiến của mô hình hay hãng khác → chỉ **tư vấn** cho người dùng (hỏi gì, vì sao); người dùng quyết,
công cụ gọi chéo do môi trường cung cấp. Hai mô hình đồng ý là bằng chứng mạnh, **không phải giấy phép**
để tự áp khuyến nghị.
