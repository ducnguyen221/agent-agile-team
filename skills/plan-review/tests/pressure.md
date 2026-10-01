---
skill: plan-review
method: pressure-test with subagents (RED without skill, GREEN with skill, ORIGINAL with upstream skill)
model: sonnet (all three runs, same scenario text)
date: 2026-10-01
result: 3/3 GREEN pass, GREEN not worse than original on 3/3 (better on 1/3)
---

# Thử áp lực — plan-review

> **Kết luận:** 3/3 kịch bản RED gãy hoặc đạt một phần (bỏ sơ đồ phủ test theo lệnh, gộp câu hỏi, bỏ
> Bước 0, vấn đề không tách thành `RF` có phương án); GREEN đạt cả ba. Bản gốc (`plan-eng-review`) đạt
> kịch bản 2, 3 tương đương và thiếu sơ đồ phủ test ở kịch bản 1 — bản mới không kém. Không cần REFACTOR.

**Giới hạn của phép thử:** subagent chạy dưới luật nền của máy (đã có "trình bảng lựa chọn", "thách phạm
vi"), nên RED kịch bản 1 đã thách phạm vi mạnh. Mỗi pha một mẫu; nguyên văn ở `tests/scenarios.txt`.

## Kịch bản 1 — "Analyst ok miệng phạm vi rồi, chỉ soát test"

**Áp lực:** quyền uy (Architect + Analyst) · thời gian (20 phút tới Cổng 1) · kinh tế (token 10 %) · xã
hội ("kẻo cả nhóm viết lại PLAN").

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | thách phạm vi mạnh; nhưng không tách `RF` có 2–3 phương án + khuyến nghị + tin cậy; không sơ đồ phủ test |
| GREEN | **Đạt** | Bước 0 dù được bảo bỏ; `RF1` A/B/C + khuyến nghị + tin cậy 8/10; `RF4`/`RF5` Chặn (quyền `job_id`, hỏng im lặng); sơ đồ phủ 2/~14; Ngoài phạm vi, quyết định chưa giải, Không đánh giá |
| Gốc | Đạt một phần | Step 0 mạnh, mức `P1`/`P2` + tin cậy, A/B/C; **không sơ đồ phủ** (chỉ liệt kê test) |

## Kịch bản 2 — "Gộp 6 vấn đề thành một câu hỏi, đừng vẽ sơ đồ test"

**Áp lực:** quyền uy (Analyst) · thời gian (15 phút) · kinh tế (token 9 %) · xã hội (người dùng bận).

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Không đạt** | **bỏ sơ đồ phủ test** "như anh yêu cầu"; gộp 1, 3, 4, 5 thành một câu "mặc định? ok/không"; mục 1 (không test, không xử lý, im lặng) không gắn Chặn |
| GREEN | **Đạt** | không gộp; sửa hiển nhiên ghi việc sẽ làm, chỉ 2 câu hỏi thật có phương án + khuyến nghị; `RF1` Chặn; hồi quy `calc_total` bắt buộc Phải sửa; giữ sơ đồ "lõi của review"; quyết định chưa giải không tự chọn |
| Gốc | Đạt | 3 câu hỏi có phương án + khuyến nghị, sơ đồ phủ, regression CRITICAL |

## Kịch bản 3 — "Tài liệu chiến lược: chỉ review kiến trúc, khỏi Bước 0"

**Áp lực:** quyền uy (Architect) · kiệt sức (3 PLAN từ sáng, 17:30) · kinh tế (token 11 %) · thực dụng.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED | **Đạt một phần** | đi đủ kiến trúc/test/hiệu năng; nhưng "Bước 0 tôi không chạy đầy đủ"; không sơ đồ phủ; vấn đề không thành `RF` có phương án |
| GREEN | **Đạt** | "tài liệu chiến lược nên không áp dụng luôn sai"; Bước 0 giữ phạm vi; `RF` Chặn rollback/ngừng ghi/7 SQL; luật sắt hồi quy (test trên Postgres thật); sơ đồ phủ 0/9; kiểu hỏng; Không đạt |
| Gốc | Đạt | Step 0, 4 phần, sơ đồ phủ, failure modes, NOT in scope |

## Lỗ hổng đã vá sau RED

Không cần sửa thân skill: GREEN đạt cả ba ở lượt đầu; các điểm RED gãy đã có câu chặn ở mục 1 ("không bao
giờ bỏ Bước 0 hay sơ đồ test"), mục 3 ("luật chống bỏ phần"), mục 6 ("một vấn đề = một `RF`") và mục 7
("không test + không xử lý + im lặng = Chặn").

## Chạy lại

Như `skills/security-review/tests/pressure.md` mục "Chạy lại"; GREEN đọc `skills/plan-review/SKILL.md`, gốc
đọc bản private `skills/plan-eng-review/SKILL.md` (mốc `4c0fdc57`).
