---
id: SPR-OPENHANDS-SPEC
doc: spec
title: Tích hợp Kỹ năng Lập trình Tự trị & Chuẩn GitHub từ OpenHands vào Agent Agile Team
sprint: SPR-OPENHANDS
request: RQ-OPENHANDS-001
feature: FS-AAT-AUTONOMOUS-DEV
status: ready
size: medium
risk: low
risk_tags: [methodology, standards, github, coding]
gate_1: pending
gate_1_at: null
gate_1_quote: null
roles:
  analyst: [T1, antigravity]
  business-reviewer: [T1, human-duc]
created: 2026-10-12
updated: 2026-10-12
source: "https://github.com/OpenHands/OpenHands (MIT)"
links:
  plan: PLAN.md
---

# Tích hợp Kỹ năng Lập trình Tự trị & Chuẩn GitHub từ OpenHands — Đặc tả (SPEC)

> **Kết luận:** Chuyển hóa tinh hoa kiến trúc CodeAct, quy trình SWE-bench Defect Localization và mô hình tự động hóa GitHub Issue-to-PR từ OpenHands vào `agent-agile-team`, giúp nâng cao năng lực viết code thực chiến, gỡ lỗi chuẩn xác và tương tác GitHub của đội ngũ AI Agent.

---

## 1. Bối cảnh

Trong quy trình phát triển phần mềm Agile hiện tại của `agent-agile-team`:
- **Vấn đề 1 (Giới hạn của `github-ops`):** Hiện tại skill `github-ops` chủ yếu đóng vai trò gọi các lệnh CLI `gh` rời rạc (triage issue, xem log CI), chưa có một quy trình tự động hóa khép kín từ lúc nhận một Issue trên GitHub cho đến khi phân tích, tạo reproducer, sửa lỗi và phát hành một Pull Request đạt chuẩn (Issue-to-PR pipeline).
- **Vấn đề 2 (Mùi suy đoán khi code & fix bug):** Khi agent đảm nhận vai trò `implementer` trong các task gỡ lỗi hoặc viết mã, đôi lúc agent sa vào bẫy "suy đoán qua mắt đọc" (visual inspection guessing) hoặc sửa triệu chứng cục bộ mà không chạy script kiểm chứng thực tế. OpenHands giải quyết vấn đề này triệt để thông qua mô thức **CodeAct** và nguyên tắc **"Reproducer-First"**.
- **Vấn đề 3 (Bằng chứng PR thiếu cấu trúc):** Khi mở Pull Request bằng bot/agent, nếu thiếu bằng chứng kiểm thử trước-sau và liên kết issue chuẩn (`Fixes #...`), người duyệt mã (Tech Lead / Human) mất rất nhiều thời gian đối soát.

---

## 2. Câu chuyện người dùng

SPEC có 3 **user story** (US):

| Mã | Câu chuyện | Ưu tiên |
|---|---|---|
| US1 (Quy trình Issue-to-PR tự động) | Là kỹ sư AI trong sprint, tôi muốn có quy trình chuẩn để biến một GitHub Issue thành một Pull Request có test và bằng chứng, để tiết kiệm thời gian giải quyết bug tồn đọng | Bắt buộc |
| US2 (Kỹ thuật CodeAct & Reproducer-First) | Là Implementer, tôi muốn có hướng dẫn cụ thể về việc viết script kiểm thử độc lập trước khi sửa code, để không bao giờ tuyên bố sửa xong mà chưa chạy kiểm chứng thật | Bắt buộc |
| US3 (Truy vết nguồn gốc Upstream) | Là người quản trị phương pháp, tôi muốn OpenHands được ghi sổ đầy đủ trong `UPSTREAM.md` để đảm bảo tuân thủ bản quyền và theo dõi drift | Bắt buộc |

---

## 3. Yêu cầu chức năng

### FR1: Quy trình xử lý GitHub Issue-to-PR (Mở rộng `skills/github-ops`)
- **FR1.1 (Issue Ingestion & Context Extraction):** KHI nhận lệnh xử lý một GitHub Issue, THÌ agent phải trích xuất tiêu đề, mô tả, log lỗi đính kèm, và tiêu chí hoàn thành, đồng thời kiểm tra trùng lặp trước khi bắt đầu.
- **FR1.2 (Branch & Worktree Isolation):** KHI bắt đầu sửa lỗi cho một Issue, THÌ agent phải tạo một nhánh riêng biệt theo quy ước `fix/issue-<id>-<slug>` hoặc sử dụng worktree cô lập.
- **FR1.3 (Structured PR Bundling):** KHI mã đã vượt qua toàn bộ kiểm thử, THÌ agent tạo PR bằng `gh pr create` với body tuân thủ mẫu chuẩn gồm 4 phần:
  1. *Tóm tắt thay đổi (Summary)*
  2. *Phân tích nguyên nhân gốc (Root Cause Analysis)*
  3. *Bằng chứng kiểm thử (Verification Output)*
  4. *Từ khóa liên kết đóng issue (`Fixes #<id>`)*.

### FR2: Nguyên tắc CodeAct & SWE-bench Defect Localization (Mở rộng `skills/debugging`, `skills/tdd`, `roles/executor/implementer.md`)
- **FR2.1 (Reproducer-First Mandate):** KHI bắt đầu điều tra một bug kỹ thuật, THÌ Implementer bắt buộc phải tạo một script tái hiện nhỏ gọn (`reproduce_issue.py` hoặc test case tối thiểu) và chạy thử để khẳng định kết quả FAIL (exit code $\neq 0$) trước khi được phép chạm vào mã nguồn chính.
- **FR2.2 (Targeted Defect Localization):** KHI tìm kiếm nguyên nhân lỗi trong codebase lớn, THÌ agent sử dụng tìm kiếm biểu thức/AST/call stack để khoanh vùng dưới 5 file liên quan, không tải (dump) toàn bộ thư mục vào context.
- **FR2.3 (Exit Code Verification Loop):** KHI sửa xong, THÌ agent bắt buộc phải chạy lại chính xác script reproducer đó và chứng minh exit code bằng 0 cùng với toàn bộ test suite cũ không bị regression.

### FR3: Cập nhật Sổ theo dõi Upstream (`UPSTREAM.md`)
- **FR3.1 (Đăng ký Nguồn gốc):** Ghi nhận repository `OpenHands/OpenHands` vào bảng "Repo đã dùng hoặc đã xét" với vai trò `ý · distill`, mốc commit HEAD baseline tại ngày 2026-10-12 (`efa2e78a`), license `MIT`.

---

## 4. Tiêu chí Thành công (Success Criteria)

- **SC1:** `skills/github-ops/SKILL.md` có mục hướng dẫn chi tiết về luồng "Issue-to-PR Resolver Pipeline".
- **SC2:** `skills/debugging/SKILL.md` và `roles/executor/implementer.md` thể hiện rõ nguyên tắc "Reproducer-First" và mô thức CodeAct.
- **SC3:** `UPSTREAM.md` được cập nhật đồng bộ, không gây lỗi linter hoặc đứt gãy bảng theo dõi.
