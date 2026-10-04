# agents/

Agent chuyên đề, mỗi agent một file `<tên>.md`. Agent **chỉ đọc** (không sửa code, không chạy lệnh ghi; cây làm việc "sạch" = `git status --short` rỗng, và khi chạy kiểm
thì dùng cờ không ghi cache nếu có, như `-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1`), riêng
`build-fixer` được sửa file (T2, vai Implementer, chỉ sửa đúng chỗ lỗi build đòi). Reviewer, analyzer và
`code-explorer` là agent **khác** người làm, được Tech Reviewer (hoặc Analyst, Architect với `code-explorer`) kéo
theo trigger (skill `code-review`, thẻ `roles/verifier/`). Frontmatter không ghi `model:` — tier ghi trong thân
(T1 tư duy; `build-fixer` T2); model thực tế do bảng tier của môi trường quyết. Nguồn ghi ở frontmatter (`source`, `source_sha`, `base_sha`, `license`,
`rewrite_before_public`), khớp [UPSTREAM.md](../UPSTREAM.md).

## Mục lục — 13 agent

| Agent | Kéo khi |
|---|---|
| [python-reviewer](python-reviewer.md) | code Python đổi: bảo mật, xử lý lỗi, type hint, idiom, đồng thời |
| [fastapi-reviewer](fastapi-reviewer.md) | ứng dụng FastAPI đổi: route, schema, dependency, async, auth, CORS, OpenAPI — soát sẵn sàng chạy thật |
| [database-reviewer](database-reviewer.md) | SQL, migration, schema, index, RLS hay hiệu năng CSDL đổi (PostgreSQL trước); không có Write/Edit |
| [security-reviewer](security-reviewer.md) | diff chạm đầu vào người dùng, xác thực/phân quyền, endpoint, secret, tích hợp ngoài — đích của security escalation |
| [silent-failure-hunter](silent-failure-hunter.md) | code bắt, bọc, thử lại hay fallback lỗi — săn lỗi bị nuốt, fallback sai, mất ngữ cảnh lỗi |
| [comment-analyzer](comment-analyzer.md) | code thêm/sửa comment, docstring, tài liệu API — kiểm khớp code, đủ ý, không mục |
| [rag-pipeline-reviewer](rag-pipeline-reviewer.md) | pipeline RAG đổi: kho vector, chunking, embedding, rerank, trích dẫn, bộ đánh giá |
| [code-explorer](code-explorer.md) | cần hiểu tính năng có sẵn trước khi đổi: lần điểm vào, luồng chạy, tầng, phụ thuộc thành bản đồ `file:dòng`; chỉ đọc |
| [code-reviewer](code-reviewer.md) | review độc lập tổng quát một diff trước khi gộp (bảo mật, đúng, chất lượng, test), lọc theo độ chắc chắn, được trả 0 phát hiện |
| [test-analyzer](test-analyzer.md) | thay đổi thêm/sửa hành vi: kiểm test có thật sự phủ — nhánh và đường lỗi chưa test, assert không bắt hồi quy, mẫu flaky; không viết test |
| [typescript-reviewer](typescript-reviewer.md) | TypeScript/JavaScript đổi: an toàn kiểu, đúng async, xử lý lỗi, bảo mật Node, idiom |
| [react-reviewer](react-reviewer.md) | component React/Next.js đổi (`.tsx`/`.jsx`): hook, state, ranh giới server/client, a11y, hiệu năng render, bảo mật React; chạy cạnh `typescript-reviewer` |
| [build-fixer](build-fixer.md) | build, compile, import hay kiểm kiểu đang đỏ và cần sửa nhỏ nhất để xanh — **agent duy nhất được sửa file** (T2); không nuốt lỗi, không bỏ/xoá test, không nới config; dừng sau 3 lần sửa hỏng |
