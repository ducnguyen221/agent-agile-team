---
skill: api-design
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: dde5b6a0ecb7f5eac7daa12e8c96ab8fd32a50b4
date: 2026-10-03
result: pass 7/7 (6 tình huống + 1 ranh giới), 1 partial
agent_ids:
  questions: a20c3fe70f425e155
  answers: a2a2dfad264dbfeff
---

Đã đọc: `<gốc worktree>\skills\api-design\SKILL.md`

# Thử truy xuất - api-design

> **Kết luận:** pass 7/7 (6 tình huống + 1 ranh giới), 1 partial; ngưỡng >=4/5 câu tình huống + câu ranh giới. Chạy lại (lượt 2) với bộ câu mới, người soạn
> và chủ thể đều là agent mới. Chủ thể trỏ đúng mục ở cả 6 câu tình huống (những phần skill không phủ, chủ thể nói rõ và được ghi ở cuối file) và nhận
> ra câu ranh giới thuộc `error-handling`.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` hiện hành, lĩnh vực và tên các skill khác); nguyên văn câu hỏi, file nháp
"Mục kỳ vọng" (có mtime), bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/api-design-retrieval-rerun-2.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `error-handling`.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Endpoint DELETE /projects/{id}/members/{userId} của mình hiện trả 200 kèm body rỗng nếu xoá được, 200 kèm `{"deleted":false}` nếu thành viên không tồn tại, và 500 nếu người gọi không phải owner. Client gọi lại khi mạng chập chờn thì lúc xoá lần hai lại ra kết quả khác lần một. Mình nên trả mã nào cho từng trường hợp, và gọi lại có phải an toàn không? | `SKILL.md` › 2. Phương thức và mã trạng thái (bảng Idempotent: DELETE có; 204/404/403; 200-cho-mọi-thứ là lỗi hay gặp). Không có mục riêng 'DELETE lần hai trả 404 hay 204', chỉ suy từ bảng | `SKILL.md` › 2. Phương thức và mã trạng thái; `references/auth-ratelimit-versioning.md` › 2. Kiểm quyền | Đạt |
| 2 | Nhóm đang tranh nhau đặt URL cho việc "huỷ đơn": một người muốn POST /orders/{id}/cancel, người khác muốn PUT /orders/{id} với status=cancelled, người thứ ba muốn DELETE /orders/{id}. Đơn huỷ rồi vẫn phải tra cứu được và hoàn tiền sau 3 ngày. Chọn cách nào và vì sao? | `SKILL.md` › 1. Thiết kế tài nguyên (mẫu `POST /api/v1/orders/:id/cancel` cho hành động không map CRUD) + › 2 (DELETE = xoá tài nguyên) | `SKILL.md` › 1. Thiết kế tài nguyên (khối hành động không map CRUD); › 2. Phương thức và mã trạng thái | Đạt |
| 3 | Trang quản trị cho lọc đơn theo trạng thái, khoảng ngày, tên khách và sắp xếp theo tổng tiền. Hiện mỗi tính năng một kiểu: `?status=paid`, `?from=2026-01-01&to=...`, `?q=`, `?sort=-total`, có chỗ lại viết `?orderBy=total_desc`. Chuẩn hoá query string cho GET /orders thế nào để client khỏi đoán? | `references/responses-pagination-filtering.md` › 3. Lọc, sắp xếp, tìm kiếm, chọn trường (bằng nhau, toán tử ngoặc vuông, `-` cho giảm dần, tìm kiếm). Điểm vào qua `SKILL.md` › 4. Đọc thêm khi cần | `references/responses-pagination-filtering.md` › 3. Lọc, sắp xếp, tìm kiếm, chọn trường (qua `SKILL.md` › 4) | Đạt |
| 4 | Đối tác gọi POST /payments/{id}/refund bằng token của họ, nhưng mình phát hiện token đó cũng hoàn tiền được cho đơn của đối tác khác chỉ bằng cách đổi id trong URL. Ở tầng hợp đồng API thì cần quy định gì về xác thực, phân quyền theo tài nguyên và mã trả về khi không đủ quyền (401, 403 hay 404)? | `references/auth-ratelimit-versioning.md` › 1. Xác thực và › 2. Kiểm quyền (kiểm sở hữu tài nguyên; ví dụ 404 khi không phải của mình); `SKILL.md` › 2 (401 vs 403) và › 5 danh mục (kiểm quyền: chỉ chạm tài nguyên của mình) | `references/auth-ratelimit-versioning.md` › 1. Xác thực, › 2. Kiểm quyền; `SKILL.md` › 2, › 5 | Đạt |
| 5 | Nút "tải báo cáo tháng" gọi GET /reports/monthly rồi chờ khoảng 90 giây mới có file, gateway cắt kết nối ở 30 giây nên người dùng thấy lỗi. Thiết kế lại hợp đồng của endpoint này thế nào để client biết tiến độ và lấy được kết quả? | KHÔNG có mục chuyên (không có 202 Accepted / thăm dò trạng thái / tác vụ bất đồng bộ trong skill). Gần nhất: `SKILL.md` › 1 (hành động không map CRUD = POST + động từ) và › 2 (mã trạng thái). Đạt nếu agent nói rõ skill không phủ phần bất đồng bộ; bịa là có mục thì tối đa Một phần | không mục nào trả lời trực tiếp; nói rõ skill không phủ tác vụ chạy lâu / 202 / thăm dò | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 6 | Mình sắp bỏ trường `legacy_code` khỏi response của GET /products/{id} và đã tìm được 3 nơi dùng nó: app bán hàng, dịch vụ kho và một đối tác bên ngoài. Cần thông báo lùi dần ra sao, giữ trường bao lâu và dùng header hay mốc ngày nào để họ kịp chuyển? | `SKILL.md` › 3. Đổi hợp đồng: liệt kê bên dùng trước khi đổi (bỏ trường = phá vỡ → phiên bản mới hoặc giai đoạn chuyển có `Sunset`, ADR); `references/auth-ratelimit-versioning.md` › 4. Phiên bản (`Sunset`, 410 Gone sau ngày đó) | `SKILL.md` › 3. Đổi hợp đồng; `references/auth-ratelimit-versioning.md` › 4. Phiên bản | Đạt |
| 7 | API trả 500 kèm stack trace, thỉnh thoảng timeout khi gọi sang dịch vụ thanh toán. Mình cần thiết kế phân cấp exception (lỗi nghiệp vụ, lỗi hạ tầng), quy tắc retry với backoff khi gọi sang dịch vụ đó và nội dung log cho từng loại lỗi. Nên làm theo hướng nào? | mục khác: skill `error-handling` (api-design `SKILL.md` › 4 'Liên quan' trỏ sang đó). Chấp nhận thêm `debugging` cho phần nguyên nhân 500/timeout | mục khác: `error-handling` (từ `SKILL.md` › 4, dòng Liên quan) | Đạt |


Chấm lại (điều phối yêu cầu): Đạt = trỏ đúng mục VÀ mục có nội dung trả lời câu; Một phần = trỏ đúng nơi nhưng nội dung thiếu, hoặc đạt qua đáp thay thế đã chấp nhận; Không đạt = trỏ sai hoặc bịa. Ngưỡng tính Đạt + Một phần cho việc trỏ đúng; số một phần ghi ở `result`.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Tác vụ chạy lâu / bất đồng bộ (`202 Accepted`, thăm dò trạng thái, tải kết quả): không có mục nào (câu 5). Skill cũng không trỏ sang skill khác cho việc này.
- `DELETE` gọi lần hai nên trả `204` hay `404` không được nói; chỉ có 'DELETE idempotent' (câu 1).
- Chọn `403` hay `404` để giấu sự tồn tại của tài nguyên không có hướng dẫn (câu 4); ví dụ của skill trả `403` khi sai chủ sở hữu.
- Thời hạn lùi dần cho bên dùng nội bộ không có; chỉ có 'API công khai: 6 tháng' (câu 6).
