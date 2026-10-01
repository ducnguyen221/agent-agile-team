---
name: web-qa
description: Use when a web app must be checked in a real browser - verifying a branch or deployment, a UAT round, "test the site", regression against a previous run, or a bug report that needs reproduction steps and screenshots - and the job is to report, not to fix.
source: [garrytan/gstack qa-only/SKILL.md.tmpl]
source_sha: [96764e80a641e28141ec8297223768029f5bf483]
base_sha: 4c0fdc5736a49b6223a7dfc7626d5495cf55185c
license: [MIT]
rewrite_before_public: false
metadata:
  group: verification
  roles: [qa]
---

# Kiểm web trên trình duyệt — chỉ báo cáo

> **Kết luận:** QA dùng ứng dụng như người dùng thật — bấm mọi nút, điền mọi form, xem mọi trạng thái — qua
> sáu pha, ghi phát hiện ngay khi gặp với ảnh chụp và bước tái hiện, chấm **điểm sức khoẻ 0–100 có trọng
> số**, và **không sửa gì**. Phát hiện dùng thang chung; mỗi luồng/kịch bản `FR` đã kiểm là một `VR`.
> Không dựng được trình duyệt → **Chưa chạy**, không bao giờ thay bằng unit test.

## 1. Vai và ranh giới

- **QA chỉ báo cáo.** Không đọc mã nguồn để giải thích lỗi, không sửa file, không đề xuất patch trong báo
  cáo — sửa là việc của Implementer qua vòng mới.
- Không sửa test, cấu hình, dữ liệu dự án; chỉ ghi báo cáo, bằng chứng và fixture tạm do chính lượt kiểm
  tạo (dọn sau khi xong).
- Lệnh hay dịch vụ không có sẵn (thiếu trình duyệt, server không lên) **không phải lỗi sản phẩm** — ghi
  Chưa chạy kèm giới hạn.
- Dự án chưa có hạ tầng test → ghi trong tóm tắt (đổi nghĩa "hồi quy" cho vòng sau); không tự cài.

## 2. Công cụ

Phương pháp không phụ thuộc công cụ. Dùng công cụ tự động hoá trình duyệt mà **harness có** (ví dụ máy
chủ MCP Playwright, Chrome DevTools); không có → Chưa chạy, báo Analyst. **Không gõ tên công cụ theo trí
nhớ** — liệt kê công cụ harness đang cấp và dùng đúng tên nó trả (tiền tố tên công cụ khác nhau giữa các
harness).

| Cần | Loại thao tác |
|---|---|
| điều hướng, cây truy cập + tham chiếu phần tử | navigate, snapshot |
| bấm / gõ / chọn / di chuột / điền form | click, type, select, hover, fill form |
| ảnh chụp | screenshot — **luôn đường dẫn tuyệt đối** |
| lỗi console, request hỏng 4xx/5xx | console messages, network requests |
| chạy JS trong trang | evaluate |
| đổi viewport, giả lập thiết bị/mạng chậm | resize, emulate |
| chờ theo điều kiện (không ngủ cố định) | wait for |
| hộp thoại, upload | handle dialog, file upload |
| hiệu năng, Core Web Vitals | Lighthouse / performance trace (nếu có) |

**So DOM trước/sau một thao tác** (khi không có công cụ diff sẵn): trước thao tác chạy evaluate lấy `url`,
`innerText` và số node (hoặc chỉ vùng liên quan, ví dụ `#cart` — toàn trang nhiễu vì đồng hồ, bộ đếm) →
thao tác → chạy lại y hệt → tự so và nói bằng lời: URL đổi? số node? chữ nào xuất hiện/mất? Cần bằng
chứng mức phần tử → snapshot cây truy cập trước và sau.

**Kiểm nhiều viewport:** lần lượt 1280×720, 768×1024, 375×812 — mỗi cỡ một ảnh — rồi trả về 1280×720. So:
thanh cuộn ngang, chữ bị cắt, phần tử đè nhau, menu thu gọn đúng.

**Bẫy hay gặp:**
- Ảnh chụp đường dẫn tương đối rơi vào thư mục gốc của công cụ, không vào thư mục báo cáo → **luôn tuyệt đối**.
- Một lớp phủ (bản đồ, modal) che dropdown trông như "dropdown không mở" → xem cả ảnh **và** cây truy cập:
  option có trong cây mà không bấm được là lỗi xếp lớp (z-index), bước tái hiện phải nói thế.
- "Thay đổi không hiện" là phát hiện về **cache** cho tới khi chứng minh khác → xem header của trang gốc qua
  network requests trước khi ghi là lỗi deploy.

**Đăng nhập:** đăng nhập qua form như người dùng, bằng tài khoản test được giao. 2FA/OTP → xin mã người
dùng và chờ. CAPTCHA → nhờ người dùng tự giải trong trình duyệt; không tìm cách vượt. **Không bao giờ ghi
mật khẩu, token thật vào báo cáo** — luôn `[ĐÃ CHE]`. Cần tài khoản hay dữ liệu thật → dừng và hỏi
(điều kiện dừng (b), (c)).

## 3. Thiết lập

| Tham số | Mặc định |
|---|---|
| URL đích | suy từ nhánh (cổng dev đã biết của dự án → URL staging/preview), không đoán quá 3 cổng; không có thì hỏi |
| Chế độ | Đầy đủ · Nhanh · Hồi quy (so với baseline) · Theo diff |
| Thư mục bằng chứng | nơi cấu hình dự án chỉ định; mặc định `<thư mục sprint>/qa/<YYYY-MM-DD>/` với `screenshots/` |
| Đăng nhập | không, trừ khi được giao tài khoản test |

Tạo thư mục trước. **Không xoá, không ghi đè** output cũ — báo cáo trùng tên thì thêm hậu tố; tích luỹ là
thứ làm chế độ Hồi quy được.

**Đầu vào ưu tiên:** `test-plan.md` của sprint (do `plan-review` ghi) và kịch bản `FR` trong SPEC; git diff
chỉ là đường lùi.

## 4. Chế độ

**Theo diff** (mặc định trên nhánh tính năng không có URL):
1. `git diff <mốc gốc>...HEAD --name-only` và `git log <mốc gốc>..HEAD --oneline`.
2. Ánh xạ file đổi → trang/route: route/controller → URL; component/template → trang render nó; model/
   service → trang dùng nó; CSS → trang dùng nó; API → gọi trực tiếp bằng evaluate (`fetch`).
3. Không ánh xạ được → **không bỏ trình duyệt**: chạy chế độ Nhanh. Thay đổi backend, cấu hình vẫn đổi
   hành vi.
4. Mỗi trang bị ảnh hưởng: điều hướng → ảnh → console → chạy tương tác trọn → so DOM để chứng minh thao
   tác làm đúng điều nó tuyên bố.
5. Đối chiếu **ý định** từ commit, SPEC: thay đổi phải làm gì — kiểm nó làm thế, không chỉ "trang hiện ra".
6. Báo theo nhánh: N trang bị ảnh hưởng, mỗi trang chạy đúng không, bằng chứng, hồi quy ở trang lân cận.

**Đầy đủ** (có URL): duyệt có hệ thống mọi trang với tới được; nhắm 5–10 phát hiện có bằng chứng tốt + điểm
sức khoẻ.

**Nhanh:** trang chủ + 5 đích điều hướng chính: tải được không, lỗi console, link hỏng thấy được. Có điểm
sức khoẻ, không ghi chi tiết từng phát hiện.

**Hồi quy:** chạy Đầy đủ, nạp baseline cũ, so: phát hiện nào đã xử lý, cái nào mới, điểm tăng giảm. Thiếu
baseline → phần hồi quy Chưa chạy, phần kiểm độc lập vẫn chạy.

## 5. Sáu pha

1. **Khởi tạo:** tạo thư mục; ghi giờ bắt đầu, nhánh, commit, cây sạch/bẩn.
2. **Đăng nhập** (chỉ khi cần) — mục 2.
3. **Định hướng:** mở đích; snapshot lấy bản đồ trang; ảnh `screenshots/initial.png`; lỗi console của trang
   đầu; thu cấu trúc điều hướng (danh sách `a[href]`; SPA thì dùng nút và menu trong snapshot). Nhận diện
   framework, ghi vào metadata.
4. **Khám phá** — mỗi trang: điều hướng → snapshot → ảnh → console, rồi:
   1. **Nhìn:** bố cục, ảnh hỏng, căn lề.
   2. **Phần tử tương tác:** bấm mọi nút, link, control — làm đúng nhãn không?
   3. **Form:** điền và gửi; rồi gửi rỗng, dữ liệu sai, biên (chuỗi rất dài, ký tự đặc biệt, `<script>`, unicode).
   4. **Điều hướng:** mọi đường vào/ra — breadcrumb, nút back, deep link, menu mobile.
   5. **Trạng thái:** rỗng, đang tải, lỗi, tràn.
   6. **Console + network sau MỌI tương tác**, không chỉ lúc tải — lỗi JS không hiện ra mắt vẫn là lỗi; một
      500 mà giao diện nuốt cũng vậy.
   7. **Responsive** khi trang nhạy bố cục.
   8. **Ranh giới quyền:** người chưa đăng nhập thấy gì? vai khác? Ứng dụng đa tenant: tenant **khác** thấy
      gì? Trang hiện dòng của tenant khác là phát hiện bảo mật mức Chặn, không phải phát hiện UX.

   Dồn thời gian cho luồng lõi (trang chủ, dashboard, thanh toán, tìm kiếm, phần nhánh vừa đổi); lướt trang
   phụ. Phần tử bấm được mà cây truy cập bỏ sót: evaluate trên `[onclick], [role="button"], .cursor-pointer`.
5. **Ghi phát hiện ngay khi gặp**, không dồn cuối. Lỗi tương tác: ảnh trước → thao tác → ảnh kết quả → so
   DOM → bước tái hiện trỏ ảnh. Lỗi tĩnh (chữ sai, bố cục): một ảnh + mô tả. **Thử lại một lần trước khi
   ghi** — báo nhầm một lỗi ngẫu nhiên tốn lòng tin hơn bỏ sót một lỗi nhỏ.
6. **Kết thúc:** tính điểm sức khoẻ; "3 việc nên sửa trước"; bảng sức khoẻ console; metadata (ngày, thời
   lượng, số trang, số ảnh, framework, nhánh, commit); ghi `baseline.json` cạnh báo cáo.

## 6. Phân loại phát hiện

| Mức | Nghĩa trong kiểm web | Ví dụ |
|---|---|---|
| **Chặn** | chặn luồng lõi, mất dữ liệu, sập ứng dụng, lộ dữ liệu giữa người dùng/tenant | gửi form → trang lỗi; thanh toán hỏng; xoá dữ liệu không xác nhận; tenant thấy dòng của tenant khác |
| **Phải sửa** | tính năng chính hỏng, không có đường vòng | tìm kiếm ra sai; upload hỏng im lặng; vòng lặp chuyển hướng đăng nhập |
| **Nên sửa** | chạy được nhưng sai rõ, có đường vòng | tải trang >5 s; thiếu validate nhưng vẫn gửi được; vỡ bố cục chỉ trên mobile |
| **Ghi chú** | thẩm mỹ, đánh bóng | chữ sai, lệch 1 px, hover không nhất quán |

**Nhóm** (dùng đúng các nhóm này — điểm phụ thuộc vào chúng):
1. **Giao diện** — vỡ bố cục, ảnh hỏng, z-index, phông/màu không nhất quán, hoạt ảnh giật, chế độ tối.
2. **Chức năng** — link hỏng, nút chết, validate thiếu/sai/vượt được, chuyển hướng sai, trạng thái mất khi
   refresh/back, race (gửi đúp, dữ liệu cũ).
3. **Trải nghiệm** — điều hướng khó hiểu, thiếu chỉ báo đang tải, tương tác >500 ms không phản hồi, thông
   báo lỗi vô ích, không xác nhận trước thao tác phá huỷ, ngõ cụt.
4. **Nội dung** — chữ sai, nội dung cũ, lorem ipsum sót, cắt chữ không có dấu ba chấm, nhãn sai, trạng
   thái rỗng thiếu.
5. **Hiệu năng** — tải >3 s, cuộn giật, dịch bố cục, >50 request một trang, ảnh chưa tối ưu, JS chặn.
6. **Console/lỗi** — exception chưa bắt, request 4xx/5xx, cảnh báo lỗi thời, CORS, mixed content, vi phạm CSP.
7. **Tiếp cận** — thiếu alt, input không nhãn, điều hướng bàn phím hỏng, bẫy focus, ARIA sai/thiếu, tương
   phản kém, nội dung trình đọc màn hình không tới được.

## 7. Điểm sức khoẻ

Mỗi nhóm bắt đầu 100, trừ theo phát hiện: Chặn −25 · Phải sửa −15 · Nên sửa −8 · Ghi chú −3, sàn 0. Hai
nhóm tính riêng: **Console** — 0 lỗi → 100 · 1–3 → 70 · 4–10 → 40 · >10 → 10. **Link** — 100 trừ 15 mỗi
link hỏng, sàn 0.

Điểm = Σ (điểm nhóm × trọng số):

| Console | Link | Giao diện | Chức năng | Trải nghiệm | Hiệu năng | Nội dung | Tiếp cận |
|---|---|---|---|---|---|---|---|
| 15 % | 10 % | 10 % | 20 % | 15 % | 10 % | 5 % | 15 % |

Điểm chỉ nói về phần kiểm trình duyệt; không gộp với kết quả test chức năng khác.

## 8. Kiểm riêng theo framework

**Next.js** — lỗi hydration trong console; 404 ở request `_next/data`; điều hướng bằng bấm link (không chỉ
gõ URL) để bắt lỗi routing phía client; dịch bố cục ở trang nội dung động.
**Rails** — cảnh báo N+1 trong console dev; token CSRF trong form; chuyển trang Turbo; flash hiện **và** tắt.
**WordPress** — xung đột JS plugin; thanh admin khi đăng nhập; endpoint `/wp-json/`; mixed content.
**SPA** — điều hướng qua snapshot (danh sách link bỏ sót route client); dữ liệu cũ khi rời rồi quay lại;
back/forward; console phình sau dùng lâu.

## 9. Báo cáo

Ghi `qa-report-<ứng dụng>-<YYYY-MM-DD>.md` trong thư mục bằng chứng, `screenshots/` bên cạnh:

- **Kết luận** (một câu): kết luận lượt kiểm + điểm + số phát hiện theo mức.
- Metadata: ngày · URL · nhánh · commit · chế độ · phạm vi · thời lượng · số trang · số ảnh · framework.
- Điểm sức khoẻ + bảng 8 nhóm · "3 việc nên sửa trước" · bảng sức khoẻ console (lỗi · số lần · lần đầu thấy).
- Phát hiện, mỗi cái một mã `RF` (đánh tiếp số của REPORT): mức · nhóm · URL · mô tả kỳ vọng ↔ thực tế ·
  bước tái hiện trỏ ảnh (`![](screenshots/...)`).
- **`VR`** cho mỗi luồng/kịch bản `FR` đã kiểm: cách kiểm (bước), môi trường (trình duyệt, viewport, URL,
  commit), kỳ vọng ↔ thực tế, **Đạt · Không đạt · Chưa chạy · Không áp dụng**, người chạy (vai · tier ·
  model) — theo `method/evidence.md`.
- Hồi quy (nếu có): bảng chỉ số baseline ↔ hiện tại ↔ chênh; đã xử lý; mới.
- Đề xuất test tự động (nếu có): mỗi test ghi hành vi bảo vệ và hồi quy nó bắt; chỉ là đề xuất.
- **Không đánh giá:** trang, vai, viewport không kiểm và vì sao.

**Kết luận lượt kiểm** (phục vụ reviewer và Cổng 2, không thay chúng): còn Chặn hoặc Phải sửa → **Không
đạt** · chỉ Nên sửa/Ghi chú, hoặc có phần Chưa chạy → **Đạt có điều kiện** (ghi rõ điều kiện) · không phát
hiện mức trên Ghi chú và mọi phần đã chạy → **Đạt**.

## 10. Luật

1. **Tái hiện là tất cả.** Mọi phát hiện có ít nhất một ảnh.
2. **Đường dẫn tuyệt đối** cho mọi ảnh.
3. **Cho người đọc thấy ảnh** — mở ảnh sau khi chụp khi đang báo trực tiếp.
4. **Không ghi thông tin đăng nhập** — `[ĐÃ CHE]`.
5. **Ghi dần**, mỗi phát hiện ngay khi gặp.
6. **Không đọc mã nguồn** để giải thích lỗi — kiểm như người dùng.
7. **Console và network sau mọi tương tác.**
8. **Sâu hơn rộng:** 5–10 phát hiện có bằng chứng hơn 20 phát hiện mơ hồ.
9. **Không xoá output.**
10. **Không thay trình duyệt bằng unit test hay eval.** Đã giao kiểm web thì mở trình duyệt; "diff trông
    như chỉ backend" không phải lý do bỏ.
11. **Không sửa.** Sửa là quyết định riêng qua vòng mới, có review riêng (skill `code-review`).
