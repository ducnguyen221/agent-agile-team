---
skill: error-handling
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 26b515dc240ba62dfd0a2f00c929c50eb1597cfb
date: 2026-10-03
result: pass 7/7 (6 tình huống + 1 ranh giới), 3 partial
agent_ids:
  questions: a26875bddfa622b57
  answers: ab0f8e80278a0eeb5
---

Đã đọc: `<gốc worktree>\skills\error-handling\SKILL.md`

# Thử truy xuất - error-handling

> **Kết luận:** pass 7/7 (6 tình huống + 1 ranh giới), 3 partial; ngưỡng >=4/5 câu tình huống + câu ranh giới. Chạy lại (lượt 2) với bộ câu mới, người soạn
> và chủ thể đều là agent mới. Chủ thể trỏ đúng mục ở cả 6 câu tình huống (những phần skill không phủ, chủ thể nói rõ và được ghi ở cuối file) và nhận
> ra câu ranh giới thuộc `debugging`.

Bảy câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` hiện hành, lĩnh vực và tên các skill khác); nguyên văn câu hỏi, file nháp
"Mục kỳ vọng" (có mtime), bài trả lời trọn của chủ thể và id agent ở `evidence/TK12-green/error-handling-retrieval-rerun-2.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-03-agent-agile-team-wave-2/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành
`<gốc worktree>` vì repo chặn tên người dùng. Cột "Mục kỳ vọng" ghi vào file nháp **trước khi** giao chủ thể (thứ tự: nhận câu -> ghi kỳ vọng ->
giao chủ thể -> chấm). Câu 7 là câu ranh giới: đáp án của người soạn là `debugging`.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Hàm `charge_customer()` hiện bắt `except Exception as e: logger.error(str(e))` rồi `raise` lại ở ba tầng khác nhau, nên mỗi lỗi thanh toán thấy log lặp 3 dòng mà vẫn không biết là thẻ bị từ chối hay cổng thanh toán sập. Nên bắt và ghi log ở đâu, bao nhiêu lần, và cần giữ lại thông tin gì? | `SKILL.md` › 3. Lỗi không được làm lộ secret (log loại lỗi + mã, không `str(exc)` thô) + › 2. Mẫu lõi ('một handler ở biên HTTP', lỗi lạ → log rồi 500) + › 1 nguyên tắc 4 + › 5 danh mục (log có ngữ cảnh). KHÔNG có quy tắc tường minh 'log đúng một lần' | `SKILL.md` › 1, › 2, › 3, › 5; `references/python-go-patterns.md` › 1 | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 2 | Team đang định nghĩa mã lỗi cho API đặt phòng (khoảng 25 loại: phòng đã hết, sai ngày, token hết hạn, quota…). Lúc đầu mỗi chỗ tự `raise ValueError("...")` một kiểu, giờ frontend không biết lỗi nào cho bấm thử lại, lỗi nào phải đổi dữ liệu. Nên thiết kế mã lỗi và phân loại thế nào để client xử lý được? | `SKILL.md` › 1 nguyên tắc 2 (lỗi có kiểu) và › 2. Mẫu lõi (`AppError` gốc có `code` + `status_code`); `references/python-go-patterns.md` › 1. Python › Phân cấp ngoại lệ. Cờ 'có thể thử lại' không rõ có trong skill | `SKILL.md` › 1, › 2; `references/python-go-patterns.md` › 1 (Phân cấp ngoại lệ); `references/retry-and-user-messages.md` › 1 | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 3 | Job đồng bộ đơn hàng gọi API kế toán, lỗi 429 thì hiện đang `while True: sleep(1)` gọi lại, lúc cao điểm hơn 200 worker cùng dội vào làm bên kia sập lâu hơn. Sửa lại thế nào cho khỏi thành bão request, và khi nào thì nên bỏ cuộc? | `references/retry-and-user-messages.md` › 1. Retry — Python (backoff mũ + jitter, trần số lần, retry 5xx/429/mạng, không 4xx khác); `SKILL.md` › 2. Mẫu lõi (chỉ retry lỗi thoáng qua) | `SKILL.md` › 2; `references/retry-and-user-messages.md` › 1. Retry — Python, › 2. Retry — TypeScript | Đạt |
| 4 | App mobile hiện hiện nguyên chuỗi `psycopg2.OperationalError: connection refused to 10.0.3.12:5432` lên toast cho khách. Viết lại thông báo thế nào để khách biết cần làm gì tiếp mà không lộ chi tiết nội bộ, và chi tiết kỹ thuật thì để ở đâu? | `references/retry-and-user-messages.md` › 3. Câu báo lỗi cho người dùng (một bảng tra mã → câu) + `SKILL.md` › 1 nguyên tắc 3 và › 3 (không đưa chuỗi lỗi DB ra người dùng/log) | `SKILL.md` › 3, › 1; `references/retry-and-user-messages.md` › 3; `references/python-go-patterns.md` › 1 | Đạt |
| 5 | Review PR thấy `try: send_email(user) except: pass` sau bước tạo tài khoản, và ở chỗ khác `int(price) if price else 0` để "cho khỏi lỗi". Em nên nhận xét gì, và đâu là chỗ chấp nhận được, đâu là chỗ phải để lỗi nổ ra? | `SKILL.md` › 1 nguyên tắc 1 và 4 + › 5. Danh mục (không `except:` trần; mọi except xử lý/ném lại/log) + › 4 (giao agent `silent-failure-hunter`). Tiêu chí 'fallback chấp nhận được khi nào' chỉ gián tiếp | `SKILL.md` › 1, › 4 (agent `silent-failure-hunter`), › 5 | Đạt |
| 6 | Worker xử lý hàng đợi nhận một message hỏng, parse JSON lỗi, hiện cứ ném exception rồi queue giao lại message đó vô hạn, kẹt luôn 4.000 message phía sau. Nên xử lý lỗi theo hướng nào: bỏ, gửi sang hàng chờ lỗi, hay thử lại? | KHÔNG có mục chuyên (hàng đợi / dead-letter / poison message không có trong skill). Gần nhất: `SKILL.md` › 2 (chỉ retry lỗi thoáng qua, có trần) và `references/retry-and-user-messages.md` › 1. Đạt nếu agent nói rõ khoảng trống | `SKILL.md` › 1, › 2; `references/retry-and-user-messages.md` › 1; nói rõ skill không phủ hàng đợi / dead-letter | Một phần (trỏ đúng nơi, nội dung thiếu: xem Thiếu nội dung) |
| 7 | Sau khi deploy, bảng điều khiển báo tỷ lệ response 500 tăng từ 0,2% lên 6% ở endpoint `/orders`, và nhóm đang cãi nhau là do bản deploy hay do DB. Cần quy trình gì để tìm ra nguyên nhân gốc trước khi đụng vào code? | mục khác: skill `debugging` (`SKILL.md` › 4 'Liên quan': `debugging` (truy lỗi lan tầng)). Không phải bản thân error-handling | mục khác: `debugging` (từ `SKILL.md` › 4, dòng Liên quan) | Đạt |


Chấm lại (điều phối yêu cầu): Đạt = trỏ đúng mục VÀ mục có nội dung trả lời câu; Một phần = trỏ đúng nơi nhưng nội dung thiếu, hoặc đạt qua đáp thay thế đã chấp nhận; Không đạt = trỏ sai hoặc bịa. Ngưỡng tính Đạt + Một phần cho việc trỏ đúng; số một phần ghi ở `result`.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Hàng đợi / thông điệp độc / hàng chờ lỗi (dead-letter): không có (câu 6). Skill không trỏ sang skill khác.
- Quy tắc 'ghi log đúng một lần ở biên' không được nêu tường minh; chủ thể suy ra từ 'một handler ở biên HTTP' (câu 1).
- Phân loại ~25 mã lỗi và cờ 'có thể thử lại' cho client: không có phương pháp; có `is_retriable` ở `references/retry-and-user-messages.md` nhưng là hàm phía bên gọi (câu 2).
- Giới hạn tốc độ phía client / điều phối chung nhiều worker / circuit breaker: không có (câu 3). Khớp với việc `description` đã bỏ cụm 'cascading failures' ở vòng sửa trước.
