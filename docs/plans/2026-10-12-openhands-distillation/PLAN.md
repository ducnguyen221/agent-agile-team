---
id: SPR-OPENHANDS-PLAN
doc: plan
title: Kế hoạch Tích hợp Kỹ năng Lập trình Tự trị & Chuẩn GitHub từ OpenHands
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
  architect: [T1, antigravity]
  tech-reviewer: [T1, agent-review]
created: 2026-10-12
updated: 2026-10-12
source: "https://github.com/OpenHands/OpenHands (MIT)"
links:
  spec: SPEC.md
---

# Kế hoạch Tích hợp Kỹ năng Lập trình Tự trị & Chuẩn GitHub từ OpenHands — PLAN

> **Kết luận:** Nâng cấp năng lực kỹ thuật và quy trình GitHub cho `agent-agile-team` qua 4 việc cụ thể, đảm bảo zero-runtime, không thêm phụ thuộc nặng, nâng cao độ tin cậy khi viết code và fix bug.

---

## Mục tiêu

Hiện thực hóa toàn bộ các yêu cầu chức năng (FR1, FR2, FR3) của SPEC bằng việc bổ sung checklist, mẫu lệnh và quy chuẩn vào các kỹ năng và thẻ vai hiện có của `agent-agile-team`.

---

## Kiến trúc & Điểm chạm

```
agent-agile-team
 ├── UPSTREAM.md                          ◄─── [TK1] Ghi nhận mốc nguồn OpenHands (MIT, efa2e78a)
 ├── skills/github-ops/SKILL.md           ◄─── [TK2] Bổ sung Sub-workflow Issue-to-PR Resolver
 ├── skills/debugging/SKILL.md            ◄─── [TK3] Bổ sung Heuristic Reproducer-First & SWE-bench localization
 └── roles/executor/implementer.md        ◄─── [TK4] Bổ sung nguyên tắc CodeAct vào cẩm nang Implementer
```

---

## Ràng buộc chung

- **Không thêm Docker hay phụ thuộc nặng:** Giữ nguyên tính chất phương pháp luận và cẩm nang kỹ năng gọn nhẹ của `agent-agile-team`.
- **Bảo toàn tính tương thích ngược:** Các lệnh và quy tắc sẵn có của `github-ops` và `debugging` không bị thay đổi, chỉ bổ sung thêm nhánh quy trình chuyên sâu.
- **Tuân thủ quy ước mã định danh:** Mọi task, issue reference phải tuân thủ chuẩn `id-convention`.

---

## Trọng tâm Review (Review Focus)

1. **Khả năng thực thi lệnh:** Các câu lệnh mẫu `gh` trong quy trình Issue-to-PR phải là cú pháp hợp lệ, an toàn và có cờ kiểm soát.
2. **Nguyên tắc "Reproducer-First":** Hướng dẫn viết script tái hiện lỗi phải rõ ràng, tránh để agent hiểu lầm thành việc tạo rác bừa bãi trong codebase chính.
3. **Tính nhất quán của bảng Upstream:** Bảng `UPSTREAM.md` phải khớp chính xác định dạng các cột và thứ tự ngày kiểm tra.

---

## Danh mục Công việc Chi tiết (Tasks)

### TK1: Ghi nhận nguồn gốc OpenHands vào `UPSTREAM.md`
* **Đích sửa:** `UPSTREAM.md`
* **Nhiệm vụ:**
  - Thêm một dòng vào bảng *"Repo đã dùng hoặc đã xét"*:
    `| OpenHands/OpenHands | ý · distill | skills/github-ops, skills/debugging, roles/implementer | efa2e78a | 2026-10-12 · efa2e78a | khi OpenHands ra bản lớn |`
  - Thêm một khối mô tả ngắn gọn về các thành phần đã chắt lọc từ OpenHands ở cuối mục tương ứng.

### TK2: Nâng cấp `skills/github-ops` — Sub-workflow Issue-to-PR Resolver
* **Đích sửa:** `skills/github-ops/SKILL.md`
* **Nhiệm vụ:**
  - Bổ sung Mục 4 (hoặc tiểu mục): **"Quy trình xử lý Issue thành Pull Request (Issue-to-PR Resolver Loop)"**.
  - Quy định 5 bước chuẩn hóa:
    1. *Khảo sát Issue:* Đọc mô tả, nhãn, checklist yêu cầu, ghi nhận tiêu chí thành công.
    2. *Tạo nhánh cô lập:* Đặt tên nhánh chuẩn `fix/issue-<id>-<mô-tả-ngắn>` hoặc dùng worktree riêng biệt.
    3. *Tạo Reproducer:* Viết test case hoặc script chạy tái hiện lỗi cục bộ.
    4. *Thực thi & Kiểm định:* Sửa code cho đến khi reproducer đạt và toàn bộ test suite xanh.
    5. *Mở PR chuẩn:* Gọi `gh pr create` với tiêu đề rõ ràng, body có cấu trúc 4 phần (Tóm tắt, Nguyên nhân, Bằng chứng kiểm thử, `Fixes #<id>`).

### TK3: Nâng cấp `skills/debugging` — Heuristic Reproducer-First & Defect Localization
* **Đích sửa:** `skills/debugging/SKILL.md` (hoặc tài liệu bổ trợ trong `skills/debugging/references/`)
* **Nhiệm vụ:**
  - Củng cố Pha 1 (Điều tra nguyên nhân gốc):
    - Đưa vào nguyên tắc **"Reproducer-First Mandate"** từ SWE-bench: Bắt buộc phải có một lệnh hoặc script độc lập chứng minh lỗi trước khi được mở file nguồn để vá.
    - Chiến lược khoanh vùng lỗi hẹp (Locate before dump): Dùng ripgrep, AST và call trace để chỉ tải dưới 5 file vào ngữ cảnh, tránh làm loãng context window.
    - Vòng lặp kiểm tra exit code: Chỉ chấp nhận hoàn thành khi lệnh reproducer trả về exit code `0`.

### TK4: Cập nhật thẻ vai `roles/executor/implementer.md`
* **Đích sửa:** `roles/executor/implementer.md`
* **Nhiệm vụ:**
  - Trong mục *"Được làm"* và *"Không được làm"*:
    - Bổ sung nguyên tắc CodeAct: Được phép viết script kiểm tra/thăm dò môi trường ngắn gọn trong `.tmp/` để xác minh giả thuyết.
    - Cấm sửa mã nguồn production theo cảm tính hoặc "đoán mò" mà không có kịch bản chạy thử nghiệm chứng thực.

### TK5: Kiểm thử và Nghiệm thu
* **Nhiệm vụ:**
  - Kiểm tra cú pháp Markdown toàn bộ các file sửa đổi.
  - Chạy `pytest` (nếu repo có test suite) để đảm bảo không gãy cấu trúc manifest hoặc script bổ trợ.
