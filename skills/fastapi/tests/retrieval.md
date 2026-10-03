---
skill: fastapi
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 235d85f4a02fa7a2e6e1d9896f88f365410dd91f
date: 2026-10-03
result: pass 6/6
---

Đã đọc: `<gốc worktree>\skills\fastapi\SKILL.md`

# Thử truy xuất — fastapi

> **Kết luận:** 6/6 câu Đạt (ngưỡng ≥5/6), trong đó câu 5 chỉ Đạt một phần vì không có chỉ dẫn tắt trang tài liệu
> OpenAPI ở production. Chủ thể trỏ đúng mục "Luật then chốt" và đúng tệp `references/` ở năm câu tình huống, và nhận ra câu
> ranh giới thuộc agent `fastapi-reviewer`.

Sáu câu hỏi do một agent **chưa đọc** skill soạn (chỉ biết `description` và lĩnh vực); nguyên văn và loại câu ở
`questions.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-03-agent-agile-team-wave-2/evidence/TK11-retrieval/`).
Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng; nguyên văn ở hồ sơ sprint của lớp riêng.
Cột "Mục kỳ vọng" do người chấm ghi **trước khi** mở bài trả lời của chủ thể. Câu 6 là câu ranh giới: đáp án của
người soạn (agent `fastapi-reviewer`) đã được người chấm đối chiếu với `agents/fastapi-reviewer.md` (review độc lập,
chỉ đọc, cho diff FastAPI) và nhận là đúng.

Cách chấm "một phần": mục chủ thể trỏ có câu trả lời dùng được cho quyết định mà câu hỏi đặt ra thì Đạt, phần
chi tiết phụ còn thiếu ghi ở mục cuối; chỉ Không đạt khi skill không có đáp án dùng được cho quyết định đó.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Router `orders` đang có logic nghiệp vụ nằm thẳng trong hàm endpoint và tạo session DB ở từng hàm. Nên tổ chức dependency injection ra sao? | `SKILL.md` › 2, 3 (Dependency, Service) + `references/app-schemas-dependencies.md` › 4 + `references/routes-errors-openapi-testing.md` › 2 | `SKILL.md` › 2. Chia trách nhiệm, 3. Luật then chốt; `references/app-schemas-dependencies.md` › 4. Dependency; `references/routes-errors-openapi-testing.md` › 6. Phản mẫu | Đạt |
| 2 | Endpoint async gọi `requests.get()` đồng bộ tới dịch vụ ngoài làm cả server đứng hình lúc tải cao. Sửa như thế nào? | `SKILL.md` › 3 (Async) + 4 + `references/routes-errors-openapi-testing.md` › 6. Phản mẫu | `SKILL.md` › 3. Luật then chốt (Async), 4; `references/routes-errors-openapi-testing.md` › 1 | Đạt |
| 3 | Cần bảo vệ nhóm route `/admin` bằng JWT và kiểm quyền theo vai trò. Đặt phần xác thực và phân quyền ở đâu trong FastAPI? | `SKILL.md` › 3 (Xác thực) + `references/app-schemas-dependencies.md` › 4. Dependency | `SKILL.md` › 3 (Xác thực); `references/app-schemas-dependencies.md` › 4. Dependency | Đạt (một phần: không nêu cách gắn dependency cho cả nhóm route) |
| 4 | Test cho route cần thay `get_db` bằng DB giả. Dùng cơ chế nào của FastAPI và dọn override thế nào sau mỗi test? | `SKILL.md` › 3 (Test) + `references/routes-errors-openapi-testing.md` › 5. Test | `SKILL.md` › 3 (Test); `references/routes-errors-openapi-testing.md` › 5. Test | Đạt |
| 5 | Chuẩn bị đưa service lên production: docs OpenAPI đang mở công khai, CORS đang `*`. Các thiết lập production cần chỉnh gì? | `SKILL.md` › 3 (CORS, Cấu hình) + `references/app-schemas-dependencies.md` › 1, 2 | `SKILL.md` › 3 (CORS, Cấu hình); `references/app-schemas-dependencies.md` › 1, 2 | Đạt (một phần: có CORS, secret, cấu hình; không có cách đóng trang docs) |
| 6 | PR FastAPI đã xong, cần một reviewer chỉ đọc chấm độ sẵn sàng production của diff. Gọi bên nào? | mục khác: agent `fastapi-reviewer` | mục khác: agent `fastapi-reviewer` (từ `SKILL.md` › 8) | Đạt |

## Thiếu nội dung / mâu thuẫn

- `skills/fastapi/SKILL.md:77` (mục OpenAPI) và `skills/fastapi/references/app-schemas-dependencies.md:7-53` (`create_app`): `description` hứa "OpenAPI docs,
  or production settings" nhưng không có chỉ dẫn tắt hay giới hạn `docs_url`, `redoc_url`, `openapi_url` ở môi trường production (câu 5). Đề xuất: thêm một
  dòng vào mục "Khởi tạo" của `SKILL.md`: production đặt ba tham số này theo cấu hình môi trường (tắt, hoặc chỉ mở sau xác thực).
- `skills/fastapi/SKILL.md:64-66` và `references/app-schemas-dependencies.md:179` (mục 4): có dependency xác thực và phân quyền riêng nhưng không cho thấy gắn chúng
  vào cả nhóm route `/admin` (ví dụ `APIRouter(dependencies=[...])`) (câu 3). Đề xuất: một dòng ví dụ gắn ở cấp router.
- Không có mâu thuẫn giữa `SKILL.md` và hai tệp `references/` trong sáu câu này.
