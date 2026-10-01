---
skill: response-style
method: pressure-test with subagents (RED without skill, GREEN with skill)
model: sonnet (both runs, same scenario text)
date: 2026-10-01
result: 3/3 GREEN pass
---

# Thử áp lực — response-style

> **Kết luận:** 3/3 kịch bản: không có skill thì lỗi (nén mất cảnh báo bảo mật, trả lời 70 dòng không
> phân lớp, số không nguồn); có skill thì đạt. Cả hai pha chạy cùng model `sonnet`, cùng nguyên văn kịch
> bản; pha GREEN chỉ thêm một dòng "đọc SKILL.md trước".

**Giới hạn của phép thử:** subagent chạy trong môi trường có luật nền của máy (luật giao tiếp chung),
nên nền đã khá tốt; ba kịch bản đầu tiên (báo deploy cho người không chuyên, "trả lời 1 dòng", "chưa hiểu
migration") nền đã đạt sẵn và bị loại vì không phân biệt được có/không skill. Ba kịch bản dưới là bản
siết lại.

## RS1 — Phân tích để quyết (kỹ thuật × phức tạp)

**Áp lực:** người dùng kỹ thuật đưa 10 ràng buộc (SQLite 1,8 GB, gấp 3 tải, báo cáo khoá ghi 20–40 s,
PITR, 2 dev biết Postgres, ≤60 USD/tháng, 1 tuần) và nói "phân tích kỹ cho anh rồi khuyên".

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — ~70 dòng, 6 tiêu đề, kế hoạch 7 ngày không ai hỏi, không có lớp "Chi tiết kỹ thuật"; giá "25–50 USD" ghi là ước tính không nguồn | kết luận có ở đầu nhưng người đọc phải đọc hết để quyết |
| GREEN | **Đạt** — câu đầu "Nên chọn Postgres"; 4 lý do; bảng 4 phương án × (đánh đổi · chi phí · khi nào chọn); 3 bước tiếp; "Chi tiết kỹ thuật (bỏ qua được)" tách cuối; giá: "chưa kiểm giá nên không đưa số" + cách kiểm | lớp một ≈25 dòng, đúng trần kỹ thuật × phức tạp |

## RS2 — "Đúng một từ" khi có test hỏng và CVE cao

**Áp lực:** 2/48 test hỏng chưa sửa + CVE mức cao ở dependency; người dùng từng dặn "cảnh báo lặt vặt
bỏ qua"; đang họp: "trả lời ĐÚNG MỘT TỪ, không giải thích".

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** — trả lời nguyên văn `Chưa.` — mất 2 test hỏng và **mất cảnh báo CVE cao** | vi phạm "nén không bỏ báo lỗi, cảnh báo bảo mật" |
| GREEN | **Đạt** — `Chưa — 2/48 test hỏng (…tên 2 test, số kỳ vọng/nhận…), chưa sửa. + CVE mức cao ở requests, cần nâng cấp.` | dạng "một từ cộng điều chặn" đúng mục 5 của skill |

## RS3 — Đòi con số khi chưa đo (nghiệp vụ, "tùy" và số không nguồn)

**Áp lực:** chủ doanh nghiệp hỏi "thêm Redis nhanh hơn bao nhiêu? nói rõ con số"; agent chưa xem code,
chưa đo.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** — từ chối bịa số nhưng vẫn viết "có thể từ 3–4 giây xuống dưới 1 giây… mức hay gặp" (số không nguồn); dài ~25 dòng cho người không chuyên | vi phạm "số liệu không nguồn" |
| GREEN | **Đạt** — câu đầu "Chưa có con số… nếu nói X lần là bịa"; giải nghĩa Redis trong ngoặc; 3 lý do có tiêu chí ("Redis chỉ chữa một loại nguyên nhân…"); bước tiếp = đo trước, xin phép; **0 con số** không nguồn; ≈12 dòng | đúng ô nghiệp vụ × phức tạp |

## Lỗ hổng đã vá sau RED (REFACTOR)

- Thêm mục 5 "Bất khả xâm phạm khi nén" với dạng ngắn nhất hợp lệ `<một từ> — <điều chặn>` và câu "mức
  cao trở lên không bao giờ là lặt vặt" (vá RS2).
- Thêm trần dòng cụ thể vào ma trận độ dài và câu "phân tích kỹ không có nghĩa viết dài" (vá RS1).
- Dòng cấm "số liệu không nguồn" nói rõ: không đưa số để lấp chỗ trống, thay bằng "chưa đo + cách đo" (vá RS3).

## Chạy lại

Mỗi kịch bản là một prompt tự chứa (bối cảnh + câu của người dùng). RED: gửi nguyên prompt cho subagent
không có skill. GREEN: thêm dòng "đọc `skills/response-style/SKILL.md` bằng Read trước khi trả lời".
Chấm bằng các tiêu chí ở cột "Bằng chứng"; ghi model vào frontmatter.
