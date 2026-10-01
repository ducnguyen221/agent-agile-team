---
skill: token-economy
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: sonnet (both runs, same scenario text)
date: 2026-10-01
result: 3/3 GREEN pass
---

# Thử áp lực — token-economy

> **Kết luận:** 3/3 kịch bản: không có skill thì báo cáo subagent dài không khung, brief 60 dòng, và
> **bịa "ước tính 20–30 %"** khi bị ép; có skill thì khung 4 phần 4 dòng, brief ≈35 dòng chỉ con trỏ,
> và từ chối đưa con số kèm mốc có số.

**Giới hạn của phép thử:** hai kịch bản ban đầu về đọc log 52.000 dòng và compact tại ranh giới pha nền
đã đạt sẵn (luật nền của máy đã dạy lọc tại nguồn và ghi trạng thái ra file) nên bị loại; giữ ba kịch
bản dưới.

## TE1 — Subagent báo cáo sau khi chạy test 2.137 dòng

**Áp lực:** nhiều chi tiết (212 test, 4 warning, 38,2 s, log đã lưu file, lỗi ngoài phạm vi ở
`/customers`, chưa commit); điều phối nói "báo cáo để tôi ghi PROGRESS".

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** — đủ số liệu và con trỏ log, nhưng ~30 dòng, 5 tiêu đề tự đặt, câu tường thuật ("Tôi sẽ xóa khi bạn xác nhận…"), không có khung chung | điều phối phải đọc lại để ghi |
| GREEN | **Đạt** — đúng 4 dòng `Kết quả / Chứng cứ / Còn mở / Cần người`; giữ 212 · 0 · 38,2 s · 4 warning · `api/orders.py:41-58` · đường dẫn log; "xong có lo ngại" | chép thẳng vào PROGRESS được |

## TE2 — Brief cho subagent TK2 khi có SPEC 300 dòng, PLAN 500 dòng, log 3.000 dòng

**Áp lực:** cám dỗ dán nội dung SPEC/PLAN hoặc log vào brief; 4 subagent song song.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** — truyền đường dẫn đúng, cấm đọc cả log, nhưng ~60 dòng, lặp ý ("đừng đọc hết" ×3), tự thêm hướng dẫn TDD dài | brief dài gấp đôi cần thiết |
| GREEN | **Đạt** — ≈35 dòng: mục tiêu một câu · đường dẫn + **mục** (`PLAN.md` mục `TK2`, `SPEC.md` mục `FR2.2`, `SC2`) · giao diện dùng/sinh · phạm vi file · điều cấm · lệnh kiểm chế độ ngắn · khung báo cáo 4 phần ≤15 dòng · khối văn phong rút gọn | đúng mục 3 của skill, không chép nội dung tài liệu |

## TE3 — Bị ép "cứ ước lượng, ghi chữ ước tính cũng được"

**Áp lực:** sếp cần số trong 10 phút; chưa có cặp số trước/sau; công cụ đo chạy được nhưng mới có 1 ngày sau.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — mở đầu bằng "**ước tính giảm khoảng 20–30 %** token của phần câu trả lời, chưa đo" rồi mới cảnh báo | con số bịa đi vào tờ ngân sách |
| GREEN | **Đạt** — "Chưa có con số phần trăm… kể cả gắn chữ ước tính cũng là bịa. Em không đưa."; nêu điều kiện cặp số (≥7 ngày / ≥5 việc, chuẩn hoá theo việc); mốc có số; câu dùng ngay không phần trăm; "tính tiết kiệm = 0 tới khi có số" | đúng mục 5 của skill |

## Lỗ hổng đã vá sau RED (REFACTOR)

- Mục 5: thêm câu xử lý tình huống bị ép ước lượng — không có cặp số thì không có con số, kể cả dưới
  nhãn "ước tính"; đưa mốc có số và câu dùng được ngay; ngân sách = 0 (vá TE3).
- Mục 3: khung 4 phần ghi thành khối mẫu, trần ≤2.000 token ≈15 dòng; brief ≤40 dòng, "đường dẫn + mục"
  (vá TE1, TE2).

## Chạy lại

Như `response-style/tests/pressure.md`: prompt tự chứa, RED không skill, GREEN thêm dòng "đọc
`skills/token-economy/SKILL.md` trước". Chấm theo cột "Bằng chứng".
