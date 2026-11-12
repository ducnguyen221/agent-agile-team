---
title: Feature expansion for projects with product codes - two code spaces, hyphenated product codes, layer order
type: method
status: active
updated: 2026-11-07
---

# Mở rộng tính năng cho dự án có mã sản phẩm

> **Kết luận:** dự án có mã sản phẩm riêng (module, tính năng, use case, màn hình, hợp đồng chức năng) giữ hai
> không gian mã tách nhau — **mã sản phẩm luôn có gạch nối** (`FE-01`, `SCR-033`, `FR-47`), mã hồ sơ sprint theo
> bảng mã của repo (`US1`, `FR1.2`, `SC1`, `TK1`); máy kiểm `check` không đọc dạng có gạch nối nên hai bên không đè
> nghĩa nhau. Tính năng full-stack xếp `TK` theo lớp (cơ sở dữ liệu → dịch vụ → API → giao diện) như **thứ tự gợi
> ý**; tên phiên `SPR-NN <tên gọi nhớ>`; việc tìm hiểu đi chuỗi đọc → tổng hợp → soát → khuyến nghị. Dự án không
> có mã sản phẩm: tài liệu này **không áp dụng**.

Nguồn ý: tài liệu BA của dự án FineFood (`docs/BA_ARCHITECTURE_CONVENTIONS.md` của repo FineFood, bản đọc
2026-11-07, 184 dòng). Ký hiệu `BA:<dòng>` dưới đây trỏ dòng của bản đó.

## 1. Hai không gian mã

Mã sản phẩm sống theo **vòng đời sản phẩm** (còn nguyên khi sprint đóng); mã hồ sơ sprint sống theo **sprint**.
Một tính năng sản phẩm được hiện thực hoá qua một hay nhiều sprint.

```text
KHÔNG GIAN SẢN PHẨM — sống theo sản phẩm                     máy `check` có đọc không
  MOD-06 ──► FE-07 ──► UC-011 ──► SCR-033                     không — mã có gạch nối
                  └──► FR-47                                  không — mã có gạch nối
                  │ hiện thực hoá qua
                  ▼
KHÔNG GIAN DỰ ÁN — sống theo sprint
  sổ gốc:   RQ-057 · FS-007 · SPR-13                          có — luật sổ gốc
  SPEC:     US1 · FR1.2 · SC1 · CQ1                           có — bảng mã repo
  PLAN:     TK1 · TK1.2 · RK1 · DN1                           có — bảng mã repo
  PROGRESS: BR1        REPORT: VR1 · RF1 · LN1 · CO1          có — bảng mã repo
```

- **Mã repo thắng** khi trùng chữ: trong hồ sơ sprint, `SC1` luôn là tiêu chí thành công, `FR1` luôn là yêu cầu
  chức năng của SPEC sprint đó, `TK1` luôn là việc của PLAN.
- Bảng mã repo đầy đủ: [skills/id-convention/SKILL.md](../skills/id-convention/SKILL.md) mục 2.

## 2. Bảng ánh xạ

Bảng dưới đặt mỗi thực thể của tài liệu BA cạnh chỗ tương ứng trong hồ sơ của repo. Ánh xạ là "gần nhất", không
phải "bằng nhau": mã sản phẩm không đổi tên thành mã repo, chỉ được **nhắc** trong hồ sơ sprint.

| Thực thể (tài liệu BA) | Viết trong dự án | Chỗ tương ứng ở repo | Ghi trong hồ sơ sprint thế nào |
|---|---|---|---|
| Module nghiệp vụ (BA:30) | `MOD-06` | không có mã repo | SPEC mục Bối cảnh: "thuộc `MOD-06` (tài khoản)" |
| Tính năng phát hành được (BA:31) | `FE-07` | spec sống `FS-` (một tính năng sống ↔ một `FS-`) | khoá `feature` của frontmatter trỏ `FS-`; thân nhắc `FE-07 (tài khoản khách hàng)` |
| Use case (BA:34) | `UC-011` | gần với `US` + kịch bản `FRn.m` KHI … THÌ … | câu chuyện `US` ghi nguồn: "`US1` (… — theo `UC-011`)" |
| Màn hình (BA:32) | `SCR-033` | không có mã repo; **không** phải `SC` | nhắc trong `FR`/`SC`: "KHI mở `SCR-033` THÌ …" |
| Hợp đồng chức năng của sản phẩm (BA:33) | `FR-47` | `FR` của SPEC chỉ sống trong một sprint | dòng `FR` ghi nguồn: "`FR1` (… → `FR-47`)" |
| Sprint (BA:35) | `SPR-13` | sổ SPRINTS `SPR-` | như repo |
| SPEC, PLAN, REPORT (BA:22) | như repo | SPEC · PLAN · PROGRESS · REPORT | như repo; PROGRESS là sổ sống mà BA không có |
| Nhiệm vụ kỹ thuật `TK-[Sprint].[Số]` (BA:36) | `TK1`, `TK1.2` trong PLAN | `TK` của PLAN | nhắc từ sprint khác: `SPR-13/TK4` |
| Ký Cổng 2 (BA:22, BA:138–141) | Cổng 2 | Cổng 2 trong REPORT | chủ sản phẩm kết luận Đạt / Đạt có điều kiện / Không đạt |

## 3. Đối chiếu BA ↔ repo

Kết luận: **giữ** = BA và repo khớp, dùng như BA · **đổi** = trong hồ sơ dùng quy ước repo, đề nghị sửa BA (mục 8) ·
**hỏi** = chủ dự án quyết, repo chưa có câu trả lời.

| # | Điểm của tài liệu BA (nguồn) | Điểm của repo | Kết luận |
|---|---|---|---|
| 1 | `SC` là màn hình (BA:14, BA:32) | `SC` là tiêu chí thành công của SPEC | **đổi** — màn hình viết `SCR-xxx` (mục 4) |
| 2 | khai "3 số" nhưng có `SC-106.1`, dải `SC-106.1–SC-106.6` (BA:32, BA:172) | số sau tiền tố khớp đúng định dạng đã khai | **đổi** — khai định dạng có phần chấm nếu dùng: `SCR-xxx` hoặc `SCR-xxx.n` |
| 3 | nhãn lớp `TK.1…TK.5` (BA:93); mã việc `TK-17.1.1` (BA:36) | `TK2.3` là việc con của `TK2` | **đổi** — nhãn lớp viết bằng chữ, không dùng `TK.n`; việc là `TK1`, `TK1.2` (mục 5) |
| 4 | `US1` dùng mà không định nghĩa (BA:151) | `US` là câu chuyện người dùng, chỉ định nghĩa trong SPEC | **đổi** — đặt lại tên hoặc định nghĩa trong bảng tiền tố của dự án |
| 5 | tên vai lệch: "QA Assessor Astra" (BA:3, BA:140) và "QA & Risk Assessor Astra" (BA:65, BA:81) | thẻ vai một tên ở `roles/` | **đổi** — thống nhất một tên |
| 6 | vai gắn tên nhân vật kèm danh sách model (BA:57, BA:61, BA:65, BA:77, BA:80, BA:83) | giao theo tier; model đọc từ bảng tier (biến `AGENT_AGILE_TIERS`), không buộc vào vai | **đổi** — hồ sơ ghi vai repo · tier · model thật dùng · effort; tên nhân vật chỉ là tên gọi (bảng dưới) |
| 7 | T3 là "Giám Định Độc Lập & An Toàn" (BA:64, BA:81–82) | T3 là QA và Researcher; giám định là vai kiểm định T1 | **đổi** — giám định của Astra tương ứng Tech Reviewer T1, không phải T3 (bảng dưới) |
| 8 | Argon thiết kế kiến trúc, API (BA:76) và cùng ký Cổng 1 (BA:68), đánh giá ở Cổng 2 (BA:139) | người làm không tự chấm; Cổng 1 và Cổng 2 do chủ sản phẩm quyết, duyệt thay chỉ khi được cấp | **đổi** — Argon (Architect) không ký cổng; reviewer chỉ đánh giá |
| 9 | Cổng 2 chỉ có "CHẤP THUẬN NGHIỆM THU (APPROVED & CLOSED)" (BA:141) | Cổng 2 có ba kết luận | **đổi** — "APPROVED & CLOSED" tương ứng **Đạt**; Cổng 2 luôn có đủ Đạt / Đạt có điều kiện / Không đạt |
| 10 | `FE-09` đứng trước `FE-08`; `MOD-06` có `FE-07`, `FE-09` chung `plans/06-customer-account/` (BA:156–158) | một sprint = một mục tiêu = một thư mục hồ sơ | **hỏi** — thứ tự và thư mục chung là chủ ý hay sót |
| 11 | không có tác giả người, ngày, phiên bản; dòng tác giả chỉ ghi vai agent (BA:3) | tài liệu có frontmatter (`title`, `status`, `updated`) — [conventions.md](conventions.md) | **đổi** — thêm người duyệt, ngày, phiên bản |
| 12 | `FRxx` không gạch nối, `FR1`…`FR56` (BA:33, BA:150–176) | `FR` không gạch nối là mã SPEC máy đọc: trích vào PLAN → `id-wrong-doc`, nhắc trong SPEC sprint không có mục đó → `xref-missing` | **đổi** — `FR-47`; trích nguyên văn thì để trong dấu code kèm nguồn |
| 13 | `US1` ở cột "Mã Hợp Đồng FRs" (BA:148, BA:151) | `US` không gạch nối là mã SPEC máy đọc | **đổi** — như điểm 4 và 12 |

Ngoài 13 điểm, ba quy ước của BA **giữ** vì repo đã khớp:

- **Báo cáo cho người không chuyên** (BA:109, BA:184): mẫu REPORT đã bắt buộc tiêu đề "Tóm tắt cho người không
  chuyên" ([templates/README.md](../templates/README.md) mục 4) — **đã đạt**, không thêm mục trùng. Phần II của BA
  (ma trận tính năng · use case · màn hình) đặt trong "Cách dùng, đã đổi gì, cách hoàn tác"; Phần III ở "Kết quả
  kiểm định"; Phần IV ở "Phát hiện của reviewer" và "Cổng 2".
- **Thứ tự lớp và phụ thuộc tường minh** (BA:93–95): giữ ý, đổi nhãn (mục 5).
- **Tên phiên** (BA:38–46): giữ (mục 6).

Bảng nhân vật dưới ánh xạ ba tên nhân vật của BA sang vai repo:

| Nhân vật | Vai và tier theo BA | Model BA ghi | Vai repo · tier repo |
|---|---|---|---|
| Argon | Chief Architect · T1 (BA:75) | `pro / sonnet / opus` (BA:57; BA:77 thêm `inherit`) | Architect · T1 — lập PLAN, thiết kế; **không** ký cổng |
| Gemini Flash | Lead Implementer · T2 (BA:78) | `flash / inherit` (BA:61, BA:80) | Implementer · T2 |
| Astra | QA & Risk Assessor · T3 (BA:81) | `pro / codex / sonnet` (BA:65, BA:83) | **một → nhiều:** phần giám định (bảo mật, rủi ro, số liệu) = Tech Reviewer · T1 kéo chuyên đề security; phần chạy test = QA · T3 |

- **T3 của FineFood không phải T3 của repo.** BA dùng T3 cho giám định độc lập; repo dùng T3 cho QA và
  Researcher, còn giám định là nhóm kiểm định T1 ([roles/README.md](../roles/README.md)).
- **Cảnh báo trùng tên:** tên nhân vật trùng tên model của môi trường đang dùng (`gpt-6-astra`, `gemini-4-argon-high`) chỉ là
  trùng tên. Không suy model từ tên nhân vật; model đọc từ bảng tier.
- Danh sách model của BA là gợi ý của dự án; repo không buộc model vào vai, PROGRESS ghi model **thật dùng**.

## 4. Quy ước mã sản phẩm

Mã sản phẩm luôn có gạch nối, tiền tố 2–4 chữ hoa (`FE-01`, `SCR-033`, `FR-47`); `check` không đọc dạng này.
Không viết `FE01`, `FR47`: dạng không gạch nối bị `check` đọc như mã của repo.

- KHI dự án có mã màn hình THÌ viết `SCR-xxx`; `SC` giữ nghĩa tiêu chí thành công.
- Mã sản phẩm mọi loại viết `<TIỀN TỐ>-<số>` (`MOD-06`, `FE-01`, `UC-011`, `SCR-033`, `FR-47`); số có phần chấm
  chỉ khi bảng tiền tố của dự án khai (`SCR-106.1`).
- KHI trích nguyên văn một mã không gạch nối từ tài liệu nguồn vào hồ sơ sprint THÌ đặt trong dấu code kèm nguồn:
  `` `FR47` (tài liệu BA FineFood, BA:172) ``.
- KHI hồ sơ sprint dùng mã sản phẩm dạng gạch nối (trong câu, làm tiêu đề `### FE-10`, hay gạch đầu dòng in đậm)
  THÌ `check` cho 0 phát hiện. KHI định nghĩa mục bằng dạng không gạch nối (`FE01`, `FR47`) THÌ `check` báo như với
  mọi mã repo: tiền tố ngoài bảng mã → `id-unknown-prefix`; tiền tố của tài liệu khác → `id-wrong-doc`; nhắc tới mã
  không có định nghĩa → `xref-missing`.
  - **Vì sao:** `check` nhận mã là đúng hai chữ hoa **liền** số; dấu gạch nối tách tiền tố khỏi số nên dòng không
    khớp. Hành vi này khoá bằng test `test_product_codes_hyphen_ignored` và
    `test_product_code_without_hyphen_flagged` ở `tests/test_check.py`.
- **Bảng tiền tố của dự án** ghi trong tài liệu của chính dự án, **không** ghi vào `.agile.json`. Tiền tố sản phẩm
  không trùng bảng mã repo khi đứng không gạch nối: `US` `FR` `SC` `CQ` `TK` `RK` `DN` `BR` `VR` `RF` `LN` `CO`
  `RQ` `FS` `SPR`. Dạng có gạch nối của chữ trùng (`FR-47`) chỉ dùng cho mã có trong bảng tiền tố của dự án.
- Mã sản phẩm chỉ dùng cho **thực thể sản phẩm**. Mục của hồ sơ sprint (việc, rủi ro, phát hiện…) vẫn dùng mã
  repo — `BUG-3`, `TC-012` vẫn là tiền tố tự chế bị cấm ([skills/id-convention/SKILL.md](../skills/id-convention/SKILL.md) mục 5).
- Nhắc mã sản phẩm trong hồ sơ: lần đầu trong đoạn kèm tên ngắn, như mã repo — `FE-07 (tài khoản khách hàng)`.

## 5. Thứ tự lớp cho tính năng full-stack

- KHI tính năng chạm nhiều lớp THÌ xếp `TK` theo lớp: **cơ sở dữ liệu / migration → dịch vụ miền → API → giao
  diện**. Lớp là **thứ tự gợi ý**: tính năng chỉ chạm hai lớp thì bỏ lớp thừa; lý do để đảo thứ tự ghi `Phán
  quyết:` trong PROGRESS.
- **Test đi cùng từng lớp**, không là lớp cuối: mỗi `TK` viết test trước rồi mới viết mã (skill `tdd`). BA đặt
  "Testing" là lớp thứ năm (BA:93) — repo không theo phần này.
- **Phụ thuộc tường minh:** ô `Đầu vào:` của mỗi `TK` ghi `TK` tiền đề, ví dụ `TK3` (API) có `Đầu vào: TK2 (dịch
  vụ đơn)`. Luật `task-order` của `check` vẫn là luật cứng — `TK` chỉ trỏ `TK` số nhỏ hơn; thứ tự lớp không thêm
  luật `check` nào.
- **Nhãn lớp viết bằng chữ** trong tên việc, không dùng `TK.n` (trùng cú pháp việc con `TKn.m`):
  `### TK1 — Lớp cơ sở dữ liệu: bảng phiên đăng nhập (→ FR1.1)`.

## 6. Tên phiên

Tiêu đề phiên làm việc trên công cụ AI (Claude Code, Codex, Antigravity) theo dạng `SPR-NN <tên gọi nhớ>`, ví dụ
`SPR-13 Quy ước mở rộng tính năng`. Số `SPR-` lấy từ sổ SPRINTS, độ rộng theo `id_width` của cấu hình.

## 7. Chuỗi tìm hiểu

Khi một quyết định cần đọc nhiều nguồn (tài liệu BA, repo khác, tài liệu web), đi bốn bước; bước soát tuỳ chọn:

1. **Đọc** — Researcher · T3 theo hợp đồng [roles/executor/researcher.md](../roles/executor/researcher.md): tìm,
   đọc, trích ≤2 dòng kèm nguồn; không thấy thì ghi "không tìm thấy"; không kết luận. Kết quả là một file trích
   trong `evidence/` của sprint.
2. **Tổng hợp** — vai T1 (Analyst hoặc Architect): gom các trích, phân tích, **nêu mâu thuẫn** giữa nguồn; mỗi
   nhận định trỏ dòng trích. Trước khi dùng, mở nguồn kiểm lại vài dòng trích và mọi số liệu.
3. **Soát** (tuỳ chọn) — agent khác người tổng hợp đối chiếu bản tổng hợp với hồ sơ tính cách của dự án nếu có:
   chặn nịnh, chặn khẳng định thiếu nguồn; trả phát hiện có mức (Chặn / Phải sửa / Nên sửa / Ghi chú).
4. **Khuyến nghị** — vai T1 nêu một phương án khuyến nghị, lý do, sai thì tốn gì; điều thuộc quyền người dùng thành
   `CQ` (SPEC) hoặc `DN` (PLAN).

## 8. Đề nghị gửi repo nguồn

Danh sách dưới là **đề nghị** sửa tài liệu BA của FineFood, rút từ mục 3. Chỉ ghi ở đây; gửi hay không do chủ sản
phẩm quyết, repo này không sửa repo khác.

1. Argon vừa thiết kế vừa cùng ký Cổng 1 và đánh giá Cổng 2 → tách: Architect lập PLAN; cổng do chủ sản phẩm
   quyết (BA:68, BA:76, BA:139).
2. Cổng 2 chỉ có "APPROVED & CLOSED" → thêm "Đạt có điều kiện" và "Không đạt" (BA:141).
3. `SC` là màn hình → đổi thành `SCR-xxx` (BA:14, BA:32).
4. Mã có phần chấm trái với "3 số" → khai định dạng `SCR-xxx.n` hoặc bỏ phần chấm (BA:32, BA:172).
5. Mã sản phẩm **mọi loại** viết có gạch nối, kể cả `FR1`…`FR56` → `FR-1`…`FR-56` (BA:33, BA:150–176).
6. `US1` ở cột hợp đồng chức năng → đặt lại tên hoặc định nghĩa (BA:148, BA:151).
7. Nhãn lớp `TK.1…TK.5` → viết lớp bằng chữ; "Testing" đi cùng từng lớp thay vì lớp cuối (BA:93).
8. Thống nhất tên vai của Astra (BA:3, BA:65, BA:81, BA:140).
9. T3 là giám định → ghi rõ tier là của FineFood hoặc đổi sang vai kiểm định (BA:64, BA:81).
10. Danh sách model gắn vai → trỏ bảng tier của môi trường (BA:77, BA:80, BA:83).
11. `FE-09` trước `FE-08`, hai tính năng chung `plans/06-customer-account/` → xác nhận hoặc sửa (BA:156–158).
12. Thêm người duyệt, ngày, phiên bản cho tài liệu (BA:3).
