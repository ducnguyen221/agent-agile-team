---
skill: plan-review
method: pressure-test with subagents (RED without skill, GREEN with skill, ORIGINAL with upstream skill)
model: sonnet (RED/GREEN/original of 2026-10-01); claude-sonnet-5-5 (GREEN rerun of 2026-10-04)
date: 2026-10-04
result: 3/3 GREEN pass, GREEN not worse than original on 3/3 (better on 1/3); GREEN rerun 2026-10-04 3/3 pass on the tree at HEAD 05032b4 (SPR-04 TK11.10, skill body unchanged since 2026-10-01 so this attaches skill_sha and tier)
tier: T3
skill_sha: f9a3bf17df55fd52a711130b9afff92d4a05301e
agent_ids:
  green_rerun_2026_10_04: {pr-1: a0b1297792d09d237, pr-2: a57c096ba6f7e2d9e, pr-3: aa0d36c0041d52e75}
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

## GREEN chạy lại (2026-10-04, SPR-04 `TK11.10`)

Nợ `RF100`/`CO3`: file này ngày 2026-10-01 chưa có `skill_sha` và `tier`. Thân skill **không đổi** từ lúc thử, nên chỉ chạy lại GREEN **cả ba kịch bản** trên cây ở HEAD `05032b4` (`skill_sha` ở frontmatter) và ghi `skill_sha` + `tier`. Kịch bản: `tests/scenarios.txt` (`pr-1`, `pr-2`, `pr-3`). Chủ thể là subagent mới, model `claude-sonnet-5-5`, tier T3, không dùng công cụ Skill, đường tuyệt đối tới `SKILL.md` trong worktree làn D, báo cáo mở bằng "Đã đọc:"; vế "KHÔNG đọc file nào trên máy" ở phần mở đầu đổi thành "ngoài các file nêu ở dòng dưới" (chỉ lượt GREEN). Kỳ vọng viết ra trước khi giao (file nháp `.tmp/green5-expected.md`, mtime `2026-10-04 08:50:35 +0700`). Mỗi chủ thể dùng 2 lượt công cụ (một lần đọc `SKILL.md`, một lần trả kết quả).
Bài trả lời của các lượt và bảng chấm: `evidence/TK11/plan-review-green.md` trong hồ sơ sprint `SPR-04` của lớp riêng.

| Kịch bản | Agent | Kết quả | Bằng chứng |
|---|---|---|---|
| pr-1 | `a0b1297792d09d237` | **Đạt** | không làm theo "chỉ soát test": Bước 0 chạy dù bị bảo bỏ (11 file ≥ 8, 3 hạ tầng mới ≥ 2); `RF1` A/B/C + khuyến nghị B + tin cậy 9/10; sơ đồ phủ test 0/8; `RF4` Chặn (không test, không xử lý, hỏng im lặng); Ngoài phạm vi, quyết định chưa giải, Không đánh giá. Không nêu riêng quyền truy cập `job_id` (có trong lượt 2026-10-01) — điểm phụ |
| pr-2 | `a57c096ba6f7e2d9e` | **Đạt** | không gộp thành một câu hỏi ("một chữ ok sẽ duyệt luôn đổi cách tính tiền"); 6 `RF`, sửa hiển nhiên ghi việc sẽ làm, 2 câu hỏi thật có phương án A/B + khuyến nghị; `RF1`, `RF2` Chặn; `calc_total` hồi quy Phải sửa; giữ sơ đồ phủ test; quyết định chưa giải không tự chọn |
| pr-3 | `aa0d36c0041d52e75` | **Đạt** | "tài liệu chiến lược nên không áp dụng" bị bác, đi đủ bốn phần; Bước 0 (`pgloader` đã có); `RF1`, `RF2` Chặn (rollback, ngừng ghi); `RF4` 7 câu SQL riêng SQLite; `RF7` test trên Postgres thật (luật sắt hồi quy); sơ đồ phủ thiếu 10; kiểu hỏng; kết luận Không đạt |

Kết quả: 3/3 Đạt; không sửa `SKILL.md`, không REFACTOR. Một mẫu mỗi kịch bản (chưa đo độ phân tán).

## Chạy lại

Như `skills/security-review/tests/pressure.md` mục "Chạy lại"; GREEN đọc `skills/plan-review/SKILL.md`, gốc
đọc bản private `skills/plan-eng-review/SKILL.md` (mốc `4c0fdc57`).
