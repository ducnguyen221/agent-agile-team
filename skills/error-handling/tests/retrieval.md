---
skill: error-handling
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 37a98ce8788dece71d810e3f61773fb049a1d506
date: 2026-10-03
result: pass 5/6
---

Đã đọc: `<gốc worktree>\skills\error-handling\SKILL.md`

# Thử truy xuất — error-handling

> **Kết luận:** 5/6 câu Đạt (ngưỡng ≥5/6). Câu 5 Không đạt vì thiếu nội dung: `description` hứa "cascading failures" nhưng
> skill không có gì về timeout theo tầng, circuit breaker hay chặn lan truyền. Chủ thể tự nhận "trả lời một phần" và không bịa;
> truy xuất ở năm câu còn lại đúng.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Câu 6 là câu ranh giới: đáp án của
người soạn (`debugging`) đã được người chấm đối chiếu với bảng "Khi nào" của `bug-triage` (câu "vì sao nó hỏng" thì
`debugging` trước) và `debugging` mục 1; chủ thể trả `bug-triage` rồi `debugging` thì được chấp nhận, vì cả hai đều là
skill ngoài `error-handling` và chủ thể đã nêu `debugging` là bước tìm nguyên nhân gốc.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần
chi tiết phụ còn thiếu ghi ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được cho quyết định đó.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Dịch vụ cần phân biệt lỗi nghiệp vụ (hết hàng) với lỗi hạ tầng (DB mất kết nối). Nên tổ chức hệ thống exception như thế nào? | `SKILL.md` › 2. Mẫu lõi (+ `references/python-go-patterns.md` › 1. Python) | `SKILL.md` › 2. Mẫu lõi; `references/python-go-patterns.md` › Phân cấp ngoại lệ | Đạt (một phần: không nói riêng tách nghiệp vụ và hạ tầng) |
| 2 | Client gọi API giao hàng bên thứ ba hay trả 503 và timeout lẻ tẻ. Retry bao nhiêu lần, backoff kiểu nào, và lỗi nào không nên retry? | `references/retry-and-user-messages.md` › 1. Retry (+ `SKILL.md` › 2) | `references/retry-and-user-messages.md` › 1. Retry — Python | Đạt |
| 3 | Lỗi `ValidationError` trong service đang bị trả ra thành 500 kèm stack trace cho người dùng. Ánh xạ sang response và thông điệp hiển thị cho người dùng nên thế nào? | `SKILL.md` › 2 + `references/python-go-patterns.md` › Handler toàn cục FastAPI + `references/retry-and-user-messages.md` › 3 | `references/python-go-patterns.md` › Handler toàn cục FastAPI; `references/retry-and-user-messages.md` › 3. Câu báo lỗi cho người dùng | Đạt |
| 4 | Trong code có khối `except Exception: return []` quanh hàm lấy danh sách khuyến mãi. Fallback này có chấp nhận được không, và log lỗi thế nào cho đúng? | `SKILL.md` › 1 nguyên tắc 4, 3, 5 (+ agent `silent-failure-hunter`) | `SKILL.md` › 1. Năm nguyên tắc (mục 4), 3. Lỗi không được làm lộ secret; agent `silent-failure-hunter` | Đạt (một phần: không có tiêu chí khi nào fallback hợp lệ) |
| 5 | Service A gọi B gọi C, khi C chậm thì cả chuỗi sập dây chuyền. Cần xử lý lỗi theo hướng nào để chặn lan truyền? | không có chỗ trả lời; `description` hứa "cascading failures" | `SKILL.md` › 2. Mẫu lõi (trần retry), chủ thể ghi "chỉ chạm gián tiếp, không đủ" | **Không đạt (thiếu nội dung)** |
| 6 | Production báo `KeyError: 'customer_id'` ở `checkout.py`, chưa biết nguyên nhân gốc là do dữ liệu hay do code. Bắt đầu từ đâu? | mục khác: skill `debugging` | mục khác: `bug-triage` rồi `debugging` | Đạt |

## Thiếu nội dung / mâu thuẫn

- **Thiếu nội dung, quan trọng.** `skills/error-handling/SKILL.md:3` (`description`: "reviewing code for … cascading failures"): thân skill
  không có timeout cho từng lời gọi ra ngoài, circuit breaker, bulkhead, hay fail-fast; dòng 38-39 chỉ nói retry có trần, dòng 100-101
  chỉ giao agent `silent-failure-hunter` rà "lỗi không lan lên bên gọi" (hướng ngược lại). Đề xuất: thêm mục "Chặn lan truyền" khoảng 10
  dòng (timeout mỗi lời gọi, circuit breaker, giới hạn đồng thời, trả lỗi nhanh khi phụ thuộc đã hỏng), hoặc bỏ cụm "cascading failures" khỏi
  `description`.
- `skills/error-handling/SKILL.md:34-40` (mẫu lõi): có phân cấp `AppError` nhưng không nói rõ cách tách lỗi nghiệp vụ khỏi lỗi hạ tầng (câu 1).
  Đề xuất: một dòng nêu hai nhánh `DomainError` (4xx) và `InfrastructureError` (5xx) dưới `AppError`.
- `skills/error-handling/SKILL.md:28` và `:111`: nguyên tắc "không nuốt lỗi" có, nhưng không nêu khi nào một fallback là hợp lệ (câu 4).
  Đề xuất: một dòng điều kiện (fallback phải được log, có đo, và không che dữ liệu sai thành dữ liệu rỗng).
