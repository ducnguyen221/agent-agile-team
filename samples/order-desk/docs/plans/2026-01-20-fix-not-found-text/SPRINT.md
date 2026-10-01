---
id: SPR-02-sprint
doc: sprint
title: Sửa chính tả câu báo không tìm thấy
sprint: SPR-02
request: RQ-002
feature: FS-001
status: verifying
size: tiny
risk: normal
risk_tags: []
review_round: 1
gate_1: approved
gate_1_at: 2026-01-20 09:40 +07
gate_1_quote: "sửa chữ ở màn hình tra đơn cho đúng chính tả"
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

# Sửa chính tả câu báo không tìm thấy — Sprint gộp (SPRINT)

<!-- CHỈ dùng cho cỡ RẤT NHỎ (đổi chữ, một dòng, không đổi hành vi). Rủi ro cao thì không bao giờ là rất nhỏ —
     dùng bốn tài liệu riêng. Bốn phần dưới đây là bốn tài liệu SPEC → PLAN → PROGRESS → REPORT thu gọn;
     vẫn đủ hai cổng và vẫn do agent KHÁC người làm kiểm. -->

> **Kết luận:** <!-- MỘT câu, viết lại khi đóng: làm gì, đạt hay không. -->
> Sửa chính tả câu báo lỗi ở màn hình tra đơn; chờ kiểm.

## 1. SPEC

<!-- Bối cảnh một dòng · một FR có kịch bản · một SC đo được · ngoài phạm vi · CQ (thường "Không có."). -->

- **Bối cảnh:** RQ-002 (lỗi chính tả màn hình tra đơn), tính năng FS-001 (tra cứu đơn hàng).
- **FR1.1 (câu đúng chính tả):** KHI mã đơn không tồn tại THÌ màn hình hiện "Không tìm thấy đơn hàng".
- **SC1 (chữ đúng):** test giao diện so khớp đúng câu trên.
- **Ngoài phạm vi:** đổi bố cục màn hình.
- **Câu hỏi cần làm rõ:** Không có.

## 2. PLAN

<!-- Một hoặc vài TK, mỗi TK đủ: vai + tier, cách kiểm, hoàn tác, trỏ FR/SC. -->

- **TK1 (sửa câu báo lỗi) → FR1.1, SC1:** Implementer · T2 thực thi. Cách kiểm: test giao diện xanh.
  Hoàn tác: `git revert`.

## 3. PROGRESS

<!-- Bảng trạng thái + nhật ký chỉ-thêm. Phán quyết nội bộ: "Phán quyết: <gì> — <vì sao> — <sai thì tốn gì>".
     Vướng mắc BR chỉ cho 4 trường hợp phải dừng. -->

| Việc | Vai · tier · model | Trạng thái | Bằng chứng |
|---|---|---|---|
| TK1 (sửa câu báo lỗi) | Implementer · T2 · model-x | Đạt | `pytest tests/test_ui.py` → 1 passed |

- **2026-01-20 10:00 +07** — Implementer sửa câu báo lỗi; test xanh.
- **Vướng mắc:** Không có.

## 4. REPORT

<!-- Kết quả kiểm (VR) do agent khác chạy · phát hiện (RF) + mức · cách hoàn tác · bài học (LN) và việc để lại
     (CO) nếu có · Cổng 2: câu nguyên văn + thời điểm, cũng ghi vào frontmatter. Việc rất nhỏ nghiệm thu ngầm
     (người dùng không phản đối trong lượt báo cuối) thì ghi trung thực:
     gate_2: pass · gate_2_at: <thời điểm> · gate_2_quote: "nghiệm thu ngầm — không phản đối tới <thời điểm>". -->

| Mã | Kiểm cái gì | Lệnh / thao tác | Kết quả | Người kiểm |
|---|---|---|---|---|
| VR1 (test câu báo lỗi) | SC1 | `pytest tests/test_ui.py` | Chưa chạy | Tech Reviewer · agent-d |

- **Phát hiện:** chưa kiểm.
- **Cách dùng / đã đổi gì / hoàn tác:** câu báo lỗi trong `ui/orders.html`; hoàn tác bằng `git revert`.
- **Bài học · việc để lại:** Không có.
- **Cổng 2:** chờ nghiệm thu (khi đóng: câu nguyên văn, hoặc "nghiệm thu ngầm — không phản đối tới <thời điểm>").
