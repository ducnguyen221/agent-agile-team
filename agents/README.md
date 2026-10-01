# agents/

Agent reviewer chuyên đề, mỗi agent một file `<tên>.md`. Cả 7 agent **chỉ đọc** (không sửa code, không
chạy lệnh ghi), là agent **khác** người làm, và được Tech Reviewer kéo theo trigger (skill `code-review`,
thẻ `roles/verifier/`). Frontmatter không ghi `model:` — tier ghi trong thân (T1 tư duy); model thực tế do
bảng tier của môi trường quyết. Nguồn ghi ở frontmatter (`source`, `source_sha`, `base_sha`, `license`),
khớp [UPSTREAM.md](../UPSTREAM.md).

## Mục lục — 7 agent

| Agent | Kéo khi |
|---|---|
| [python-reviewer](python-reviewer.md) | code Python đổi: bảo mật, xử lý lỗi, type hint, idiom, đồng thời |
| [fastapi-reviewer](fastapi-reviewer.md) | ứng dụng FastAPI đổi: route, schema, dependency, async, auth, CORS, OpenAPI — soát sẵn sàng chạy thật |
| [database-reviewer](database-reviewer.md) | SQL, migration, schema, index, RLS hay hiệu năng CSDL đổi (PostgreSQL trước); không có Write/Edit |
| [security-reviewer](security-reviewer.md) | diff chạm đầu vào người dùng, xác thực/phân quyền, endpoint, secret, tích hợp ngoài — đích của security escalation |
| [silent-failure-hunter](silent-failure-hunter.md) | code bắt, bọc, thử lại hay fallback lỗi — săn lỗi bị nuốt, fallback sai, mất ngữ cảnh lỗi |
| [comment-analyzer](comment-analyzer.md) | code thêm/sửa comment, docstring, tài liệu API — kiểm khớp code, đủ ý, không mục |
| [rag-pipeline-reviewer](rag-pipeline-reviewer.md) | pipeline RAG đổi: kho vector, chunking, embedding, rerank, trích dẫn, bộ đánh giá |
