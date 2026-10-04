---
id: SPR-02-sprint
doc: sprint
title: Sprint goal title
sprint: SPR-02
request: RQ-002
feature: FS-001
status: in_progress
size: small
risk: normal
risk_tags: []
review_round: 0
gate_1: pending
gate_1_at: null
gate_1_quote: null
verdict: pending
gate_2: pending
gate_2_at: null
gate_2_quote: null
roles:
  analyst: [T1, agent-a]
  implementer: [T2, agent-e]
  tech-reviewer: [T1, agent-d]
created: 2026-01-20
updated: 2026-01-20
---

# Tên mục tiêu sprint — Sprint gộp (SPRINT)

<!-- CHỈ dùng cho cỡ NHỎ: sửa cục bộ một luồng có sẵn, một FR, không đổi hợp đồng / giao diện / schema, không có
     quyết định kiến trúc. Bốn phần dưới đây là bốn tài liệu SPEC → PLAN → PROGRESS → REPORT thu gọn; Cổng 1 và
     Cổng 2 là lượt duyệt thật. MỘT reviewer (agent KHÁC người làm) kiểm cả nghiệp vụ lẫn kỹ thuật.
     Phân vân giữa nhỏ và vừa → chọn vừa. Rủi ro cao (`risk: high`) là lớn, không bao giờ nhỏ.
     Cỡ rất nhỏ dùng mẫu SPRINT-tiny.md (hai phần); cỡ vừa/lớn dùng bốn file.
     Câu dẫn: trước mỗi bảng / danh sách mã ghi một câu nói tài liệu nào và mã là gì, nghĩa in đậm — ví dụ
     "PLAN có 1 **task** (TK):" (skill id-convention). -->

> **Kết luận:** <!-- MỘT câu, viết lại khi đóng: làm gì, đạt hay không. -->
> Tra đơn bỏ qua khoảng trắng thừa quanh mã đơn; chờ kiểm.

## 1. SPEC

<!-- Bối cảnh một dòng · một FR có kịch bản · một SC đo được · ngoài phạm vi · CQ (thường "Không có."). -->

- **Bối cảnh:** RQ-002 (tra đơn thất bại khi dán mã có khoảng trắng), tính năng FS-001 (tra cứu đơn hàng).
- **FR1.1 (bỏ khoảng trắng thừa):** KHI mã đơn có khoảng trắng đầu hoặc cuối THÌ tra cứu cắt chúng rồi tìm đơn.
- **SC1 (tra được):** test đơn vị: mã " DH-1001 " trả đúng đơn DH-1001.
- **Ngoài phạm vi:** đổi định dạng mã đơn; đổi bố cục màn hình.
- **Câu hỏi cần làm rõ:** Không có.

## 2. PLAN

<!-- Một hoặc vài TK, mỗi TK đủ: vai + tier, cách kiểm, hoàn tác, trỏ FR/SC. -->

PLAN có 1 **task** (TK):

- **TK1 (cắt khoảng trắng mã đơn) → FR1.1, SC1:** Implementer · T2 thực thi. Cách kiểm: test đơn vị xanh.
  Hoàn tác: `git revert`.

## 3. PROGRESS

<!-- Bảng trạng thái + nhật ký chỉ-thêm. Phán quyết nội bộ: "Phán quyết: <gì> — <vì sao> — <sai thì tốn gì>".
     Vướng mắc BR chỉ cho 4 trường hợp phải dừng. -->

| Việc | Vai · tier · model | Trạng thái | Bằng chứng |
|---|---|---|---|
| TK1 (cắt khoảng trắng mã đơn) | Implementer · T2 · model-x | Đạt | `pytest tests/test_lookup.py` → 1 passed |

- **2026-01-20 10:00 +07** — Implementer thêm bước cắt khoảng trắng; test xanh.
- **Vướng mắc:** Không có.

## 4. REPORT

<!-- Kết quả kiểm (VR) do agent khác chạy · phát hiện (RF) + mức · cách hoàn tác · bài học (LN) và việc để lại
     (CO) nếu có · Cổng 2: câu nguyên văn + thời điểm, cũng ghi vào frontmatter. -->

REPORT có 1 **verification result** (VR):

| Mã | Kiểm cái gì | Lệnh / thao tác | Kết quả | Người kiểm |
|---|---|---|---|---|
| VR1 (test tra mã có khoảng trắng) | SC1 | `pytest tests/test_lookup.py` | Chưa chạy | Tech Reviewer · agent-d |

- **Phát hiện:** chưa kiểm.
- **Cách dùng / đã đổi gì / hoàn tác:** hàm tra đơn trong `orders/lookup.py`; hoàn tác bằng `git revert`.
- **Bài học · việc để lại:** Không có.
- **Cổng 2:** chờ nghiệm thu (khi đóng: câu nguyên văn của người dùng).
