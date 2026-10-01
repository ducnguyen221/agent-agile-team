---
id: SPR-01-report
doc: report
title: Sprint goal title
sprint: SPR-01
request: RQ-001
feature: FS-001
status: draft
size: medium
risk: normal
risk_tags: []
review_round: 1
verdict: pending
gate_2: pending
gate_2_at: null
gate_2_quote: null
roles:
  analyst: [T1, agent-a]
  implementer: [T2, agent-e]
  qa: [T3, agent-f]
  business-reviewer: [T1, agent-c]
  tech-reviewer: [T1, agent-d]
created: 2026-01-15
updated: 2026-01-15
links:
  spec: SPEC.md
  plan: PLAN.md
  progress: PROGRESS.md
---

# Tên mục tiêu sprint — Báo cáo (REPORT)

<!-- REPORT trả lời: kết quả ra sao, giao lại thế nào. Nó thay vai HANDOFF: luôn có cách dùng, đã đổi gì,
     cách hoàn tác. `verdict` = kết luận của vòng kiểm định cuối; `gate_2` = kết luận của chủ sản phẩm.
     Cả hai dùng: Đạt / Đạt có điều kiện / Không đạt. Chỉ sau Cổng 2 mới cập nhật spec sống và đóng sprint. -->

> **Kết luận:** <!-- MỘT câu: đạt hay không, còn gì, người duyệt cần làm gì. -->
> SPR-01 đề xuất **Đạt**: tra đơn theo mã chạy đúng cả hai kịch bản; còn một việc để lại (chỉ mục mã đơn).

## Tóm tắt cho người không chuyên

<!-- 3–5 câu, không thuật ngữ, không mã trần: làm được gì, dùng thế nào, còn rủi ro gì, cần quyết gì. -->

Nhân viên bán hàng giờ gõ mã đơn là thấy ngay trạng thái. Mã sai thì báo "không tìm thấy" và không lộ đơn khác.
Khi số đơn tăng nhiều, việc tra có thể chậm dần — đề xuất xử lý ở sprint sau.

## 1. Kết quả kiểm định

<!-- Mỗi SC (và kịch bản FR quan trọng) có ít nhất một VR. Kết quả: Đạt · Không đạt · Chưa chạy · Không áp dụng
     (kèm lý do). "Chưa chạy" và "Không áp dụng" KHÔNG tính là Đạt. Người kiểm phải là agent khác người làm. -->

| Mã | Kiểm cái gì | Lệnh / thao tác | Kết quả | Người kiểm | Bằng chứng |
|---|---|---|---|---|---|
| VR1 (test tra cứu) | SC1, FR1.1, FR1.2 | `pytest tests/test_orders.py` | Đạt | QA · agent-f | 6 passed, coverage 92% |

## 2. Phát hiện của reviewer

<!-- Mỗi RF: mức (Chặn / Phải sửa / Nên sửa / Ghi chú), bằng chứng (file:dòng hoặc lệnh + kết quả),
     xử lý (mở · đã sửa · để lại → CO · bác kèm lý do). Reviewer được trả 0 phát hiện nhưng phải ghi rõ
     phần mình KHÔNG đánh giá. -->

### Business Reviewer

| Mã | Phát hiện | Mức | Bằng chứng | Xử lý |
|---|---|---|---|---|
| RF1 (thông báo khó hiểu) | Câu báo lỗi dùng thuật ngữ nội bộ | Nên sửa | `ui/orders.html:42` | đã sửa |

- **Không đánh giá:** hiệu năng khi tải lớn.

### Tech Reviewer

| Mã | Phát hiện | Mức | Bằng chứng | Xử lý |
|---|---|---|---|---|
| RF2 (truy vấn chưa có chỉ mục) | Tra theo mã quét cả bảng | Nên sửa | `services/orders.py:18` | để lại → CO1 |

- **Không đánh giá:** giao diện trên thiết bị di động.

## 3. Rủi ro còn lại

<!-- Rủi ro chưa xử lý mà người duyệt phải chấp nhận nếu cho Đạt. Không có thì ghi "Không có." -->

- RF2 (truy vấn chưa có chỉ mục) còn mở — mức Nên sửa, tra chậm dần khi bảng lớn; đã chuyển thành CO1
  (chỉ mục mã đơn).

## 4. Cách dùng, đã đổi gì, cách hoàn tác

<!-- Đủ ba phần. Lệnh viết trong code span hoặc khối code. -->

- **Cách dùng:** mở màn hình "Tra đơn", nhập mã đơn.
- **Đã đổi gì:** `services/orders.py` (hàm tra cứu), `ui/orders.html` (màn hình), 6 test mới.
- **Cách hoàn tác:** `git revert` hai commit của TK1 (hàm tra cứu đơn) và TK2 (màn hình tra cứu); không có
  migration dữ liệu.

## 5. Bài học

<!-- Bài học TÁI DÙNG được, không phải nhật ký. Cột "Đề xuất nâng thành": luật / skill / bước quy trình / không.
     Chỉ ĐỀ XUẤT — chủ sản phẩm quyết. Nơi lưu do lớp riêng của môi trường quy định. -->

| Mã | Bài học | Quan trọng | Đề xuất nâng thành | Nơi lưu |
|---|---|---|---|---|
| LN1 (chuẩn hoá đầu vào) | Mã do người gõ hoặc dán phải chuẩn hoá (hoa thường, khoảng trắng) trước khi tra | Có | Bước kiểm trong thẻ Tech Reviewer | nơi lưu bài học của dự án |

## 6. Việc để lại

<!-- Việc chưa làm, lý do, đề xuất xử lý (sprint sau hoặc yêu cầu mới RQ-NNN). Không có thì ghi "Không có." -->

| Mã | Việc | Lý do để lại | Đề xuất |
|---|---|---|---|
| CO1 (chỉ mục mã đơn) | Thêm chỉ mục cho cột mã đơn | DN1 (chỉ mục mã đơn) chọn để sprint sau | Mở yêu cầu mới khi bảng đơn lớn |

## 7. Review & Retro

<!-- Review: sản phẩm so với mục tiêu. Retro: cách làm. Ghi số vòng kiểm định và tổng token phiên làm mốc;
     chỉ tuyên bố tiết kiệm token khi có cặp số trước/sau.
     Trước khi viết Retro: đọc lại mọi dòng "Phán quyết:" trong nhật ký PROGRESS — phán quyết nào sai hoặc tốn
     hơn dự kiến thì ghi vào "Chưa tốt" và cân nhắc thành bài học LN; và rà mọi việc để lại CO còn mở của các
     sprint trước (sổ SPRINTS, REPORT cũ) — đếm số tồn, ghi CO nào đã trả trong sprint này, CO nào cũ quá hai
     sprint thì đề xuất mở yêu cầu hoặc bỏ. -->

- **Review:** đạt mục tiêu SPR-01; 1 vòng kiểm định.
- **Phán quyết đọc lại:** 1 dòng trong PROGRESS (cắt khoảng trắng mã đơn) — đúng, không tốn thêm.
- **Nợ để lại tồn đọng:** 1 mở (CO1 (chỉ mục mã đơn), sprint này); 0 trả trong sprint.
- **Làm tốt:** test viết trước code; vòng kiểm định đầu không còn Chặn.
- **Chưa tốt:** câu báo lỗi chưa được duyệt chữ trước khi làm.
- **Thử lần sau:** duyệt câu chữ giao diện ngay trong SPEC.
- **Token phiên:** chưa đo. <!-- tổng token các phiên của sprint, kèm nguồn đo -->

## 8. Cổng 2 — nghiệm thu

<!-- Chủ sản phẩm kết luận Đạt / Đạt có điều kiện / Không đạt. Ghi câu nguyên văn + thời điểm vào đây và vào
     các khoá `gate_2`, `gate_2_at`, `gate_2_quote` của frontmatter. -->

Chờ nghiệm thu.
