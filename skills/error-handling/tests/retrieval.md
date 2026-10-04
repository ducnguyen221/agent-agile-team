---
skill: error-handling
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 9f2df9edee87ed4a035cd57aba80bfc16f0992a1
date: 2026-10-04
result: "strict 7/7 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: "bộ câu cũ giữ nguyên, không soạn mới"
  answers: aa483f7588fa7d005
---

Đã đọc: `<gốc worktree>/skills/error-handling/SKILL.md` và `<gốc worktree>/skills/error-handling/references/retry-and-user-messages.md`

# Thử truy xuất - error-handling

> **Kết luận:** strict 7/7: đạt ngưỡng. Sau `TK11.3` sáu câu tình huống đều trỏ đúng mục và mục có nội dung (lượt trước 4/7 Đạt hẳn, 3 Một phần: log một lần ở biên, phân loại mã lỗi, hàng chờ lỗi); câu ranh giới trả `debugging`.

Bộ câu hỏi giữ nguyên chữ của lượt trước (bộ câu cũ giữ nguyên, không soạn mới); bộ câu mới là việc của `TK13`. Cột "Mục kỳ vọng" ghi vào file nháp
`.tmp/error-handling-expected.md` **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm). Bài trả lời của chủ thể (id ở
`agent_ids`) và bảng chấm ở `evidence/TK11/error-handling-retrieval.md` trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời,
đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Hàm `charge_customer()` hiện bắt `except Exception as e: logger.error(str(e))` rồi `raise` lại ở ba tầng khác nhau, nên mỗi lỗi thanh toán thấy log lặp 3 dòng mà vẫn không biết là thẻ bị từ chối hay cổng thanh toán sập. Nên bắt và ghi log ở đâu, bao nhiêu lần, và cần giữ lại thông tin gì? | `SKILL.md` › 2. Mẫu lõi (log đúng một lần ở biên, tầng giữa bọc và ném lại `from exc`) + › 3 (log loại lỗi + mã, không `str(exc)` thô) + › 5 | `SKILL.md` › 2. Mẫu lõi; › 1; › 3 | Đạt |
| 2 | Team đang định nghĩa mã lỗi cho API đặt phòng (khoảng 25 loại: phòng đã hết, sai ngày, token hết hạn, quota…). Lúc đầu mỗi chỗ tự `raise ValueError("...")` một kiểu, giờ frontend không biết lỗi nào cho bấm thử lại, lỗi nào phải đổi dữ liệu. Nên thiết kế mã lỗi và phân loại thế nào để client xử lý được? | `references/retry-and-user-messages.md` › 4 (bảng lớp mã lỗi + cờ `retryable`) + `SKILL.md` › 1, › 2 (`AppError` có `code`) | `references/retry-and-user-messages.md` › 4. Phân loại mã lỗi và cờ "thử lại được"; `SKILL.md` › 1 | Đạt |
| 3 | Job đồng bộ đơn hàng gọi API kế toán, lỗi 429 thì hiện đang `while True: sleep(1)` gọi lại, lúc cao điểm hơn 200 worker cùng dội vào làm bên kia sập lâu hơn. Sửa lại thế nào cho khỏi thành bão request, và khi nào thì nên bỏ cuộc? | `references/retry-and-user-messages.md` › 1 (backoff + jitter, `Retry-After`, trần lần) + › 5 (retry budget dùng chung, một tầng, ngắt mạch, khi nào bỏ cuộc) | `references/retry-and-user-messages.md` › 5. Retry một tầng, giới hạn phía client, ngắt mạch; › 1 | Đạt |
| 4 | App mobile hiện hiện nguyên chuỗi `psycopg2.OperationalError: connection refused to 10.0.3.12:5432` lên toast cho khách. Viết lại thông báo thế nào để khách biết cần làm gì tiếp mà không lộ chi tiết nội bộ, và chi tiết kỹ thuật thì để ở đâu? | `references/retry-and-user-messages.md` › 3 (bảng tra câu cho người dùng) + `SKILL.md` › 1 (nguyên tắc 3), › 3 (không lộ chi tiết nội bộ; chi tiết ở log, đã che) | `references/retry-and-user-messages.md` › 3. Câu báo lỗi cho người dùng; `SKILL.md` › 3 | Đạt |
| 5 | Review PR thấy `try: send_email(user) except: pass` sau bước tạo tài khoản, và ở chỗ khác `int(price) if price else 0` để "cho khỏi lỗi". Em nên nhận xét gì, và đâu là chỗ chấp nhận được, đâu là chỗ phải để lỗi nổ ra? | `SKILL.md` › 1 (nguyên tắc 1, 4), › 5 (không `except:` trần), › 4 (agent `silent-failure-hunter`) | `SKILL.md` › 1. Năm nguyên tắc; › 5; › 4 | Đạt |
| 6 | Worker xử lý hàng đợi nhận một message hỏng, parse JSON lỗi, hiện cứ ném exception rồi queue giao lại message đó vô hạn, kẹt luôn 4.000 message phía sau. Nên xử lý lỗi theo hướng nào: bỏ, gửi sang hàng chờ lỗi, hay thử lại? | `references/retry-and-user-messages.md` › 6 (lỗi vĩnh viễn không thử lại, trần số lần nhận, hàng chờ lỗi/dead-letter, cảnh báo, redrive) | `references/retry-and-user-messages.md` › 6. Hàng đợi, thông điệp độc, hàng chờ lỗi (dead-letter) | Đạt |
| 7 | Sau khi deploy, bảng điều khiển báo tỷ lệ response 500 tăng từ 0,2% lên 6% ở endpoint `/orders`, và nhóm đang cãi nhau là do bản deploy hay do DB. Cần quy trình gì để tìm ra nguyên nhân gốc trước khi đụng vào code? | mục khác: skill `debugging` (từ `SKILL.md` › 4 dòng Liên quan) | mục khác: `debugging` (từ `SKILL.md` › 4, dòng Liên quan); nói rõ skill không phủ quy trình truy nguyên nhân | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hiện hành hứa mà thân skill không có.
- Chủ thể nêu: không có con số trần cụ thể cho retry (skill chỉ nói "có trần", chủ ý); không nói "token hết hạn" xếp lớp nào trong bảng mã lỗi.
- Nguồn của phần thêm ở `TK11.3`: Azure Architecture Center (Circuit Breaker pattern), Amazon SQS Developer Guide (dead-letter queues), AWS Builders' Library (Timeouts, retries, and backoff with jitter), ECC `skills/error-handling` ở `ef648e01`.
