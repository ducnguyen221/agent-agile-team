---
skill: api-design
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: dde5b6a0ecb7f5eac7daa12e8c96ab8fd32a50b4
date: 2026-10-04
result: "strict 3/7 (+4 partial, 0 fail) — below threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: ac7d56903f99199f0
  answers: a227535a179e0a99d
---

Đã đọc: `<gốc worktree>/skills/api-design/SKILL.md` (kèm `references/responses-pagination-filtering.md`, `references/auth-ratelimit-versioning.md`)

# Thử truy xuất — api-design (bộ câu mới, lượt độc lập)

> **Kết luận:** strict 3/7 (+4 partial, 0 fail), points-right 7/7: DƯỚI ngưỡng (2/6 câu tình huống Đạt hẳn = 33 %, ngưỡng ≥80 %; câu ranh giới Đạt). Lượt độc lập sau lượt cũ: bộ câu MỚI, người soạn mới, chủ thể mới, chấm lại từ đầu, không nương theo lượt cũ. Không sửa skill.

Bảy câu hỏi do một agent MỚI (`sonnet`, `ac7d56903f99199f0`) **chưa đọc** skill soạn từ `description`, lĩnh vực và danh sách câu của mọi bộ cũ (để không lặp). Người soạn chỉ đọc một tệp đầu vào gồm đúng ba thứ đó. Cột "Mục kỳ vọng" do QA đọc `SKILL.md` và `references/` rồi ghi vào tệp nháp (mtime `2026-10-04 10:41:37 +0700`) **trước khi** giao chủ thể (lệnh giao sau `2026-10-04 10:42:34 +0700`). Chủ thể là agent mới (`sonnet`, `a227535a179e0a99d`), cấm công cụ Skill, được đưa đường tuyệt đối tới `SKILL.md`, không được mở thư mục `tests/`; 4 lượt đọc file (SKILL.md, câu hỏi, và hai file `references/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng. Bài trả lời trọn của chủ thể, câu hỏi của người soạn, id agent và tệp kỳ vọng (có mtime) ở `evidence/TK13/api-design-retrieval.md` và `evidence/TK13/expected/api-design-expected.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Câu 7 là câu ranh giới (đáp án của người soạn ghi ở cột kỳ vọng). Skill KHÔNG đổi giữa lượt cũ và lượt này (`skill_sha` giữ nguyên).

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Mình đang làm endpoint POST /invoices/{id}/send-email để gửi hoá đơn cho khách. Mobile app hay bị mất mạng giữa chừng nên bấm lại, kết quả là khách nhận 2-3 email giống hệt nhau; tuần trước có 41 vụ khiếu nại như vậy. Mình muốn client có thể thử lại thoải mái mà mỗi hoá đơn chỉ gửi đúng một lần. Hợp đồng của endpoint cần thêm gì ở request/response và server phải xử lý lần gọi trùng ra sao? | `SKILL.md` › 2 (bảng phương thức: POST không idempotent) | `SKILL.md` › 2, › 4 | Một phần (đúng nơi; thiếu khoá chống trùng và cách server xử lý lần gọi lặp) |
| 2 | Bảng `orders` có 12 triệu dòng và trang danh sách đang dùng `?page=500&limit=50`. Từ trang 300 trở đi query chậm hẳn, và khi có đơn mới chèn vào trong lúc nhân viên đang lật trang thì họ thấy cùng một đơn xuất hiện hai lần ở hai trang liền nhau. Mình nên đổi cách phân trang như thế nào, và response cần trả thêm những trường gì để client lật tiếp được? | `references/responses-pagination-filtering.md` › 2 (cursor, `next_cursor`) | `references/responses-pagination-filtering.md` › 2 | Đạt (phần phụ: tương thích với client đang dùng `page`/`limit`, khoá sắp xếp phụ) |
| 3 | Đội mobile than là mỗi lần mở màn hình chi tiết khách hàng phải gọi GET /customers/{id}, rồi GET /customers/{id}/orders, rồi GET /customers/{id}/addresses, tổng cộng 3 request nối đuôi nhau trên mạng 3G. Ngược lại đội web thì chỉ cần mỗi tên và email, không muốn nhận cả cục dữ liệu lớn. Mình xử lý thế nào để cả hai bên đều hài lòng mà không đẻ ra một endpoint riêng cho từng màn hình? | `references/responses-pagination-filtering.md` › 3 (`fields`, `include`) | `references/responses-pagination-filtering.md` › 3 | Đạt (phần phụ: không có `include` cho khách hàng/địa chỉ, không có giới hạn độ sâu) |
| 4 | Đối tác logistics muốn nhận thông báo khi trạng thái vận đơn đổi, và họ đề nghị mình để họ gọi GET /shipments/{id} mỗi 5 giây cho 20.000 vận đơn đang chạy. Mình sợ quá tải nên muốn đặt giới hạn tốc độ, đồng thời cho họ cách biết dữ liệu chưa đổi để khỏi tải lại toàn bộ. Hợp đồng nên quy định gì về giới hạn, các header trả về khi bị chặn, và cách trả lời khi dữ liệu không thay đổi? | `references/auth-ratelimit-versioning.md` › 3 (429, `Retry-After`, `X-RateLimit-*`) | `references/auth-ratelimit-versioning.md` › 3; `SKILL.md` › 2 | Một phần (đúng nơi; thiếu cách báo "chưa đổi": `ETag`, `If-None-Match`, 304) |
| 5 | Hai nhân viên cùng mở form sửa hồ sơ sản phẩm SKU-3391 trên trang quản trị. Người A đổi giá, người B đổi mô tả, bấm lưu sau; hiện PUT /products/{id} của mình ghi đè toàn bộ nên thay đổi giá của A biến mất mà không ai hay. Ở mức hợp đồng API mình nên thêm cơ chế gì để phát hiện xung đột này, và trả mã lỗi nào khi phát hiện? | `SKILL.md` › 2 (409 Conflict: xung đột trạng thái) | `SKILL.md` › 2 | Một phần (đúng nơi; thiếu `ETag`/`If-Match`, số phiên bản, mã khi điều kiện không thoả) |
| 6 | Mình cần cho khách tải lên ảnh CMND dung lượng tới 15 MB để xác minh tài khoản và sau đó cho nhân viên xem lại ảnh đó. Hiện tại mình nhét ảnh dạng base64 vào JSON của POST /kyc/documents, request nặng hơn 20 MB và hay bị cắt giữa chừng. Nên thiết kế hợp đồng upload và tải xuống ra sao (kiểu nội dung, giới hạn kích thước, mã lỗi khi file sai định dạng hoặc quá lớn, và việc ai được phép xem lại)? | `references/auth-ratelimit-versioning.md` › 2 (kiểm quyền) + `SKILL.md` › 2 (mã lỗi) | `SKILL.md` › 2, › 5; `references/auth-ratelimit-versioning.md` › 2 | Một phần (đúng nơi cho phần quyền xem; thiếu toàn bộ hợp đồng upload/tải xuống: multipart, giới hạn kích thước, 413/415, URL ký sẵn) |
| 7 | Bảng `users` có 8 triệu dòng, mình cần đổi cột `phone` từ VARCHAR(20) sang một bảng riêng `user_phones` (một người có nhiều số), chuyển dữ liệu cũ sang rồi bỏ cột cũ, trong khi hệ thống đang chạy production và không được dừng dịch vụ. Mình nên chia các bước thay đổi cấu trúc và chép dữ liệu như thế nào, theo thứ tự nào để có thể lùi lại nếu lỗi giữa chừng? | mục khác: skill `database-migrations` (`SKILL.md` › 4 Liên quan: đổi schema đi kèm đổi API) | mục khác: `database-migrations` (`SKILL.md` › 4 Liên quan; › 3 nếu cột lộ ra API) | Đạt |

## Thiếu nội dung / mâu thuẫn

- Thử lại an toàn cho POST (khoá chống trùng `Idempotency-Key`, lưu kết quả lần đầu, trả lại cho lần gọi lặp): không có; mục 2 chỉ ghi POST không idempotent (câu 1).
- Khoá lạc quan và phát hiện ghi đè (`ETag` + `If-Match`, số phiên bản, 412/428): không có; 409 chỉ ghi "duplicate entry, state conflict" (câu 5).
- Yêu cầu có điều kiện (`ETag`/`If-None-Match`/304) cho client thăm dò nhiều: không có; phần rate limit đủ nhưng nửa còn lại của câu 4 trống.
- Upload/tải xuống tệp (multipart so với base64, giới hạn kích thước, 413/415, URL ký sẵn, kiểm quyền xem lại): không có (câu 6).
- `description` liệt kê "resource URLs, HTTP methods, status codes, envelopes, pagination, filtering, auth, rate limits, versioning" và thân skill có đủ; bốn khoảng trống trên nằm ngoài danh sách đó.

## Lịch sử

Lượt trước (bộ câu cũ, 2026-10-03, `skill_sha` `dde5b6a0ecb7f5eac7daa12e8c96ab8fd32a50b4`, `result`: strict 6/7 (+1 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7). Bộ câu cũ giữ nguyên bên dưới, id hàng đổi thành `c1`… để không lẫn vào bảng chấm của lượt mới; người soạn lần sau phải đọc cả hai bộ để không lặp. Dòng "Đã đọc" và đoạn thước chấm của lượt cũ không chép lại (thước chung ở trên).

> **Kết luận:** strict 6/7 (+1 partial, 0 fail), points-right 7/7: đạt ngưỡng (5/6 câu tình huống Đạt; câu ranh giới Đạt). Chạy lại (lượt 2) với bộ câu mới, người soạn
> và chủ thể đều là agent mới. Chủ thể trỏ đúng mục ở cả 6 câu tình huống (những phần skill không phủ, chủ thể nói rõ và được ghi ở cuối file) và nhận
> ra câu ranh giới thuộc `error-handling`.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` hiện hành, lĩnh vực và tên các skill khác); nguyên văn câu hỏi, file nháp
"Mục kỳ vọng" (có mtime), bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/api-design-retrieval-rerun-2.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `error-handling`.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| c1 | Endpoint DELETE /projects/{id}/members/{userId} của mình hiện trả 200 kèm body rỗng nếu xoá được, 200 kèm `{"deleted":false}` nếu thành viên không tồn tại, và 500 nếu người gọi không phải owner. Client gọi lại khi mạng chập chờn thì lúc xoá lần hai lại ra kết quả khác lần một. Mình nên trả mã nào cho từng trường hợp, và gọi lại có phải an toàn không? | `SKILL.md` › 2. Phương thức và mã trạng thái (bảng Idempotent: DELETE có; 204/404/403; 200-cho-mọi-thứ là lỗi hay gặp). Không có mục riêng 'DELETE lần hai trả 404 hay 204', chỉ suy từ bảng | `SKILL.md` › 2. Phương thức và mã trạng thái; `references/auth-ratelimit-versioning.md` › 2. Kiểm quyền | Đạt |
| c2 | Nhóm đang tranh nhau đặt URL cho việc "huỷ đơn": một người muốn POST /orders/{id}/cancel, người khác muốn PUT /orders/{id} với status=cancelled, người thứ ba muốn DELETE /orders/{id}. Đơn huỷ rồi vẫn phải tra cứu được và hoàn tiền sau 3 ngày. Chọn cách nào và vì sao? | `SKILL.md` › 1. Thiết kế tài nguyên (mẫu `POST /api/v1/orders/:id/cancel` cho hành động không map CRUD) + › 2 (DELETE = xoá tài nguyên) | `SKILL.md` › 1. Thiết kế tài nguyên (khối hành động không map CRUD); › 2. Phương thức và mã trạng thái | Đạt |
| c3 | Trang quản trị cho lọc đơn theo trạng thái, khoảng ngày, tên khách và sắp xếp theo tổng tiền. Hiện mỗi tính năng một kiểu: `?status=paid`, `?from=2026-01-01&to=...`, `?q=`, `?sort=-total`, có chỗ lại viết `?orderBy=total_desc`. Chuẩn hoá query string cho GET /orders thế nào để client khỏi đoán? | `references/responses-pagination-filtering.md` › 3. Lọc, sắp xếp, tìm kiếm, chọn trường (bằng nhau, toán tử ngoặc vuông, `-` cho giảm dần, tìm kiếm). Điểm vào qua `SKILL.md` › 4. Đọc thêm khi cần | `references/responses-pagination-filtering.md` › 3. Lọc, sắp xếp, tìm kiếm, chọn trường (qua `SKILL.md` › 4) | Đạt |
| c4 | Đối tác gọi POST /payments/{id}/refund bằng token của họ, nhưng mình phát hiện token đó cũng hoàn tiền được cho đơn của đối tác khác chỉ bằng cách đổi id trong URL. Ở tầng hợp đồng API thì cần quy định gì về xác thực, phân quyền theo tài nguyên và mã trả về khi không đủ quyền (401, 403 hay 404)? | `references/auth-ratelimit-versioning.md` › 1. Xác thực và › 2. Kiểm quyền (kiểm sở hữu tài nguyên; ví dụ 404 khi không phải của mình); `SKILL.md` › 2 (401 vs 403) và › 5 danh mục (kiểm quyền: chỉ chạm tài nguyên của mình) | `references/auth-ratelimit-versioning.md` › 1. Xác thực, › 2. Kiểm quyền; `SKILL.md` › 2, › 5 | Đạt |
| c5 | Nút "tải báo cáo tháng" gọi GET /reports/monthly rồi chờ khoảng 90 giây mới có file, gateway cắt kết nối ở 30 giây nên người dùng thấy lỗi. Thiết kế lại hợp đồng của endpoint này thế nào để client biết tiến độ và lấy được kết quả? | KHÔNG có mục chuyên (không có 202 Accepted / thăm dò trạng thái / tác vụ bất đồng bộ trong skill). Gần nhất: `SKILL.md` › 1 (hành động không map CRUD = POST + động từ) và › 2 (mã trạng thái). Đạt nếu agent nói rõ skill không phủ phần bất đồng bộ; bịa là có mục thì tối đa Một phần | không mục nào trả lời trực tiếp; nói rõ skill không phủ tác vụ chạy lâu / 202 / thăm dò | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| c6 | Mình sắp bỏ trường `legacy_code` khỏi response của GET /products/{id} và đã tìm được 3 nơi dùng nó: app bán hàng, dịch vụ kho và một đối tác bên ngoài. Cần thông báo lùi dần ra sao, giữ trường bao lâu và dùng header hay mốc ngày nào để họ kịp chuyển? | `SKILL.md` › 3. Đổi hợp đồng: liệt kê bên dùng trước khi đổi (bỏ trường = phá vỡ → phiên bản mới hoặc giai đoạn chuyển có `Sunset`, ADR); `references/auth-ratelimit-versioning.md` › 4. Phiên bản (`Sunset`, 410 Gone sau ngày đó) | `SKILL.md` › 3. Đổi hợp đồng; `references/auth-ratelimit-versioning.md` › 4. Phiên bản | Đạt |
| c7 | API trả 500 kèm stack trace, thỉnh thoảng timeout khi gọi sang dịch vụ thanh toán. Mình cần thiết kế phân cấp exception (lỗi nghiệp vụ, lỗi hạ tầng), quy tắc retry với backoff khi gọi sang dịch vụ đó và nội dung log cho từng loại lỗi. Nên làm theo hướng nào? | mục khác: skill `error-handling` (api-design `SKILL.md` › 4 'Liên quan' trỏ sang đó). Chấp nhận thêm `debugging` cho phần nguyên nhân 500/timeout | mục khác: `error-handling` (từ `SKILL.md` › 4, dòng Liên quan) | Đạt |

### Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Tác vụ chạy lâu / bất đồng bộ (`202 Accepted`, thăm dò trạng thái, tải kết quả): không có mục nào (câu 5). Skill cũng không trỏ sang skill khác cho việc này.
- `DELETE` gọi lần hai nên trả `204` hay `404` không được nói; chỉ có 'DELETE idempotent' (câu 1).
- Chọn `403` hay `404` để giấu sự tồn tại của tài nguyên không có hướng dẫn (câu 4); ví dụ của skill trả `403` khi sai chủ sở hữu.
- Thời hạn lùi dần cho bên dùng nội bộ không có; chỉ có 'API công khai: 6 tháng' (câu 6).
