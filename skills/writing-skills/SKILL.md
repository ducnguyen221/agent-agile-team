---
name: writing-skills
description: Use when creating a new skill, editing an existing skill (even one line), writing or reviewing a skill's description or pressure tests, choosing how to word guidance for agents, a lesson is proposed for promotion to a skill or rule, or a session or sprint went wrong and someone asks why it took so long, cost so much or ignored the plan.
metadata:
  group: meta
  roles: [architect, analyst]
source: [obra/superpowers skills/writing-skills/SKILL.md, obra/superpowers skills/writing-skills/testing-skills-with-subagents.md, obra/superpowers skills/writing-skills/persuasion-principles.md, obra/superpowers skills/diagnosing-superpowers]
source_sha: [8ca22dba9a94f28898bbce59f2537ff4d87c747d, 8ca22dba9a94f28898bbce59f2537ff4d87c747d, 8ca22dba9a94f28898bbce59f2537ff4d87c747d, 8ca22dba9a94f28898bbce59f2537ff4d87c747d]
license: [MIT, MIT, MIT, MIT]
rewrite_before_public: false
---

# Viết skill

> **Kết luận:** viết skill là **TDD cho tài liệu**: chưa thấy agent hỏng khi **không** có skill thì chưa biết
> skill dạy đúng điều cần dạy — áp cho skill mới và **mọi** lần sửa, kể cả một dòng. `description` chỉ ghi
> **điều kiện kích hoạt**. Chọn **dạng câu theo kiểu lỗi**: lỗi kỷ luật → luật cấm + bảng lý lẽ; lỗi hình
> dạng → công thức. Skill chỉ sinh từ bài học đã tái dùng, và agent chỉ **đề xuất** — người dùng quyết.

## 1. Khi nào có skill — thang nâng cấp từ bước 6

| Nấc | Ở đâu | Lên nấc kế khi |
|---|---|---|
| Bài học | `LN` trong REPORT + nơi lớp riêng quy định (`method/process.md` mục 8) | được dùng lại lần thứ hai |
| Quy trình ghi chú | ghi chú nhiều bước ở nơi lớp riêng: khi nào dùng → các bước → cạm bẫy | đủ **cả ba** điều kiện dưới |
| Skill | `skills/<tên>/` | — |

Ba điều kiện thành skill: **tái dùng nhiều lần** (mặc định ≥3 lần qua ≥2 sprint, đếm được qua `LN`/PROGRESS)
· **ổn định** (nội dung không đổi qua 2 lần dùng gần nhất) · **đủ phức tạp** (cần phán đoán, nhiều bước).

Rẽ nhánh trước khi nghĩ tới skill:

- Kiểm được bằng máy (regex, script, ô bắt buộc trong mẫu) → đề xuất luật cho `check` hoặc sửa mẫu, không skill.
- Luật đã có mà không được áp → lỗi tuân thủ: đề xuất kiểm máy hoặc ô bắt buộc, không chép lại luật thành skill.
- Một câu luật áp mọi việc → đề xuất vào luật lõi; riêng một dự án → nơi lớp riêng của dự án đó; đã có skill
  gần → sửa skill đó (vẫn qua mục 2). Chuyện kể một lần, kiến thức có sẵn ở tài liệu chuẩn: không thành skill.

Agent **không tự tạo** skill hay tự sửa luật từ bài học — kể cả đã nháp sẵn, kể cả người dùng đang vắng.
Đề xuất ghi: nấc hiện tại · bằng chứng tái dùng (mã `LN`, sprint) · dạng đích (skill / luật `check` / luật
lõi) · chi phí · lý do. Người dùng quyết.

## 2. Luật sắt

```
KHÔNG CÓ SKILL — HAY LẦN SỬA SKILL — NÀO KHI CHƯA THẤY PHÉP THỬ HỎNG
```

- Viết skill trước khi chạy RED → bỏ bản đó, chạy RED, viết lại từ lỗi quan sát được. Không giữ làm "tham
  khảo", không "chỉnh dần" trong lúc thử.
- Sửa skill đang dùng, đúng thứ tự — bỏ một bước là hỏng quy trình:
  1. RED trên **bản hiện tại**, kịch bản dụ đúng lỗi mới.
  2. Đã đạt → không sửa gì, dừng. Hỏng → sửa tối thiểu.
  3. GREEN cùng kịch bản (cùng tier, model).
  4. Chạy lại kịch bản cũ của skill, chắc không lùi.
  5. Xong 1–4 mới gộp hoặc báo xong; RED hỏng rồi gộp luôn là bỏ bước 3–4.
- "Đọc lại thấy rõ" không phải phép thử. `tests/pressure.md` chỉ ghi kết quả đã chạy; GREEN "dự kiến" là bịa.
- Hạn chót do agent khác đặt không mở ngoại lệ: báo trễ + lý do. Người dùng trực tiếp bảo gộp khi chưa thử →
  làm theo — lệnh trong phạm vi đã duyệt là phán quyết, không phải vướng mắc: ghi `tests/pressure.md` là
  **Chưa chạy** và một dòng `Phán quyết:` vào PROGRESS, không mở `BR`; Chưa chạy không bao giờ là Đạt.
- Một skill một lúc: viết → thử → xong rồi mới sang skill kế. Không viết hàng loạt rồi "thử sau cho gọn".

## 3. Chu trình RED → GREEN → REFACTOR

1. **RED:** ≥3 kịch bản, mỗi kịch bản ≥3 loại áp lực; subagent **không** có skill; ghi nguyên văn lựa chọn và
   câu biện hộ. Kịch bản đạt sẵn ở RED → không có gì để dạy: thay kịch bản, hoặc bỏ phần skill định viết cho nó.
2. **GREEN:** viết **tối thiểu** để chặn đúng lỗi đã thấy; chạy lại cùng kịch bản, cùng tier và model, có skill.
3. **REFACTOR:** lý lẽ mới → câu phủ định tường minh + dòng bảng lý lẽ + cờ đỏ + triệu chứng vào
   `description`; chạy lại tới khi hết lý lẽ mới. Khuôn kịch bản, bảy loại áp lực, cách chạy (kể cả nạp bản
   worktree), meta-test, thước chấm và ngưỡng, khuôn `tests/pressure.md`: `references/testing.md`.

## 4. Chọn dạng câu theo kiểu lỗi

Phân loại lỗi RED **trước** khi viết; dạng chặn được lỗi này làm nặng thêm lỗi kia.

| Lỗi quan sát ở RED | Dạng đúng | Dạng sai |
|---|---|---|
| Biết luật mà bỏ khi bị ép | luật cấm dứt khoát + bảng lý lẽ ↔ sự thật + cờ đỏ | lời khuyên mềm ("nên", "cân nhắc") |
| Có làm nhưng sai hình (brief phình, kết luận chìm, chép lại spec) | **công thức**: nói output **là** gì — các phần, theo thứ tự | danh sách cấm ("đừng chép", "không kể") |
| Thiếu một phần trong thứ vẫn làm | ô **bắt buộc** trong mẫu họ điền | câu nhắc đặt gần mẫu |
| Hành vi phải tuỳ điều kiện | câu điều kiện gắn vào dấu hiệu **quan sát được** ("KHI có brief THÌ trỏ tới nó") | luật chung + mệnh đề miễn trừ |

- **Không mệnh đề sắc thái.** "Đừng X trừ khi thật cần" mở lại cuộc mặc cả — kể cả khi định lượng ("tối đa 3
  dòng"). Ngoại lệ thật thì viết thành câu điều kiện riêng có dấu hiệu quan sát được.
- **Miễn trừ không khoanh được phạm vi.** "Giới hạn này không áp cho khối code" vẫn làm agent bớt khối code;
  phần phải miễn thì tái cấu trúc để luật không chạm tới.
- Cấm trên lỗi hình dạng phản tác dụng: agent mặc cả với "đừng X"; trong phép thử của nguồn, nhánh cấm sinh nội dung
  thừa **hơn** nhánh không hướng dẫn. Người duyệt đòi "danh sách cấm cho chắc" → viết công thức, trả lời bằng bảng trên và kết quả RED.
- Giọng cho skill kỷ luật: câu khẳng định dứt khoát ("luôn", "không bao giờ", "không ngoại lệ"), bắt cam kết
  (chọn A/B/C, nói ra skill đang dùng), nêu chuẩn chung ("thiếu Y là hỏng"). Không dùng giọng lấy lòng.

**Micro-test câu chữ** trước kịch bản đầy đủ: ngữ cảnh thật, **nhánh đối chứng không hướng dẫn**, ≥5 lần mỗi biến thể (`references/testing.md` mục 7).

## 5. `description` và frontmatter

- Frontmatter tiếng Anh, thân tiếng Việt. Khoá: `name` (chữ thường, số, gạch nối; tên theo việc làm, ví dụ
  `writing-plan`, `debugging`) · `description` · `metadata.group` · `metadata.roles` · `source` (repo + đường
  file) · `source_sha` · `license` · `rewrite_before_public` (`true` khi nguồn không có giấy phép mở).
- `description` bắt đầu "Use when…", ngôi thứ ba, **chỉ** điều kiện kích hoạt và triệu chứng, <500 ký tự;
  có từ agent sẽ tìm (thông điệp lỗi, triệu chứng, từ đồng nghĩa); nhắc công nghệ chỉ khi skill gắn công nghệ đó.
- **Không tóm quy trình vào `description`.** Agent làm theo bản tóm và bỏ thân skill: mô tả "review giữa các
  việc" khiến agent review **một** lượt dù thân skill ghi **hai**. Ai đòi "tóm đủ quy trình cho khỏi mở skill"
  → giữ điều kiện kích hoạt, giải thích; tiết kiệm token bằng thân ngắn và tách `references/`.

```yaml
# Sai — tóm quy trình
description: Use for code review - two passes (spec then quality), verify each finding, split by module above 10 files
# Đúng — chỉ điều kiện kích hoạt
description: Use when a diff, branch or finished task needs review before merge, or when asked to check code written by another agent
```

## 6. Ngân sách token và cấu trúc

- Khối nạp mọi phiên (trong `AGENTS.md`) ≤200 từ; `SKILL.md` thường ≤150 dòng; tra cứu >100 dòng → `references/`;
  công cụ tái dùng → `scripts/`. Đo bằng đếm từ/dòng, không ước.
- Trỏ skill khác bằng **tên** (`skill debugging`), không nạp cưỡng bức bằng cú pháp import, không chép nội dung skill
  khác. Một ví dụ tốt, một ngôn ngữ. Sơ đồ chỉ cho điểm quyết định không hiển nhiên; việc tuyến tính: danh sách đánh số.
- Script đi kèm gọi **qua trình thông dịch** (`python scripts/x.py`, `bash scripts/x.sh`), không gọi đường trần (đóng
  gói mất bit chạy; Windows không chạy file không đuôi); ưu tiên Python thư viện chuẩn, chạy cả Windows lẫn macOS.
- Không chuyện kể ("phiên hôm X ta thấy…"), không đường dẫn máy, không tên người hay dự án riêng. Hướng dẫn
  chính thức của Anthropic: <https://code.claude.com/docs/en/skills> — chỉ trỏ, không chép.

## 7. Lý lẽ ↔ sự thật

| Lý lẽ | Sự thật |
|---|---|
| "Skill rõ ràng rồi" / "đọc lại thấy ổn" | rõ với người viết ≠ rõ với agent khác; đọc không phải dùng |
| "Một dòng thôi, sửa chữ chứ đâu đổi logic" | một dòng đổi cách agent đọc các dòng cạnh nó; RED trên bản hiện tại trước |
| "Thử áp lực để đợt sau" | "đợt sau" là skill chưa thử nằm trong repo như đã kiểm |
| "Ghi GREEN dự kiến cho đủ cấu trúc" | bằng chứng giả; chỉ ghi kết quả đã chạy |
| "Danh sách cấm cho chắc, trừ khi thật cần" | lỗi hình dạng cần công thức; mệnh đề "trừ khi" mở lại mặc cả |
| "Tóm quy trình vào description cho đỡ token" | agent làm theo bản tóm, bỏ thân skill; description nạp mọi phiên |
| "Đã nháp sẵn rồi, tạo luôn cho người dùng vui" | agent chỉ đề xuất; nháp không phải bằng chứng tái dùng |
| "Một lần chạy đạt là đủ" | một mẫu nói dối; ≥5 lần và có đối chứng |

**Cờ đỏ — dừng, quay lại mục 2:** sửa skill khi chưa có RED · RED hỏng rồi gộp luôn · viết hàng loạt skill · `tests/pressure.md` có
chữ "dự kiến" · `description` kể bước làm ("then", "first", "steps") · hướng dẫn hình dạng mở đầu bằng "KHÔNG".

## 8. Trước khi báo xong

- [ ] RED ≥3 kịch bản (≥3 áp lực mỗi kịch bản) đã chạy, lỗi ghi nguyên văn; kịch bản đạt sẵn đã thay.
- [ ] GREEN đạt mọi kịch bản; REFACTOR ghi lỗ hổng đã vá; `tests/pressure.md` theo khuôn.
- [ ] Dạng câu khớp kiểu lỗi, câu chữ đã micro-test có đối chứng; `description` chỉ điều kiện kích hoạt;
      frontmatter đủ khoá, nguồn khớp `UPSTREAM.md`.
- [ ] `python scripts/check.py --self` không phát hiện nào trên file của skill; dòng mục lục `skills/README.md`
      đề xuất cho người giữ file chung.

## 9. Khi một phiên hay sprint chạy sai

"Sao lâu / tốn / làm thừa / bỏ plan", hay skill không kích hoạt → `references/diagnosing.md`: mỗi phát hiện
kèm `đường-dẫn:dòng` hoặc bị loại; số lấy từ file; đo trước khi đọc; tách đã xác minh ↔ giả thuyết ↔ khoảng trống.
Kết quả thành `LN` ứng viên; sửa skill đi lại mục 2.
