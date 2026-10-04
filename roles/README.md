# roles/ — thẻ vai

> **Kết luận:** một vai người (User) và hai nhóm vai agent — **thực thi** (Analyst, Architect,
> Implementer, QA) và **kiểm định** (Business Reviewer, Tech Reviewer + 4 thẻ chuyên đề). Luật cứng:
> **người làm ra sản phẩm không được kết luận Đạt cho chính nó.** Mỗi thẻ có đúng 8 mục: mục đích ·
> tier · đầu vào · đầu ra · được làm · không được làm · khi nào dừng · skill dùng.

## Bảng vai

| Vai | Nhóm | Tier | Khoá `roles` | Thẻ |
|---|---|---|---|---|
| User | Người | — | — | không có thẻ: giao yêu cầu, quyết ở Cổng 1, Cổng 2, bốn điều kiện dừng, mốc sau vòng 3 |
| Analyst (kiêm Distiller, điều phối) | Thực thi | T1 | `analyst` | [executor/analyst.md](executor/analyst.md) |
| Architect | Thực thi | T1 | `architect` | [executor/architect.md](executor/architect.md) |
| Implementer | Thực thi | T2 | `implementer` | [executor/implementer.md](executor/implementer.md) |
| QA | Thực thi | T3 | `qa` | [executor/qa.md](executor/qa.md) |
| Business Reviewer | Kiểm định | T1 | `business-reviewer` | [verifier/business-reviewer.md](verifier/business-reviewer.md) |
| Tech Reviewer | Kiểm định | T1 | `tech-reviewer` | [verifier/tech-reviewer.md](verifier/tech-reviewer.md) |
| Dual Review (hai reviewer độc lập cùng rubric, cho việc có `risk_tags` `rules` / `secret` / `auth`) | Kiểm định | T1 | `tech-reviewer` (+ lời ghi reviewer thứ hai ở `note`) | [verifier/dual-review.md](verifier/dual-review.md) |
| Chuyên đề security · data · backend · frontend | Kiểm định | T1 | `<tên>-specialist` | [verifier/specialists/](verifier/specialists/) |

## Luật chung cho mọi vai

- **Người làm không tự chấm.** Kiểm định do agent **khác** người làm: phiên hoặc subagent mới, nhận ngữ
  cảnh soạn riêng, không dán lịch sử phiên. Một nhãn agent không vừa giữ vai thực thi vừa giữ vai kiểm
  định cho cùng một sản phẩm (công cụ `check` so `roles` trong frontmatter).
- **QA cũng phải độc lập với người làm:** nhãn `qa` khác nhãn `implementer` và `architect`. Nếu trùng
  (việc **rất nhỏ**, một agent kiêm), mỗi `VR` ghi "tự kiểm, chưa độc lập" và kết luận tối đa là **Đạt có
  điều kiện** cho tới khi agent khác chạy lại. Cỡ nhỏ trở lên không tự kiểm: cỡ nhỏ có **một** reviewer khác
  người làm; `qa` trùng nhãn người làm ở cỡ đó là lỗi `qa-not-independent` (`check` báo khi `VR` không ghi tự kiểm).
- Trong việc nhỏ và rất nhỏ, một agent được giữ **nhiều vai thực thi**; Analyst luôn là điều phối.
- Vai được giao theo **tier**, không theo tên model ([tiers/README.md](../tiers/README.md)); model thực
  tế ghi vào PROGRESS khi giao việc.
- Mọi vai dừng ở đúng bốn điều kiện của [method/process.md](../method/process.md) mục 5 và khi cạn hạn
  mức tier; ngoài ra tự quyết và ghi `Phán quyết:`.
- Mọi vai trả lời theo [skills/response-style](../skills/response-style/SKILL.md), dùng mã theo
  [skills/id-convention](../skills/id-convention/SKILL.md), và tiết kiệm ngữ cảnh theo
  [skills/token-economy](../skills/token-economy/SKILL.md).

Tên skill trong các thẻ là tên trong repo này (thư mục `skills/`); tên agent ở mục "Skill dùng" của thẻ chuyên đề
là tên file trong [agents/](../agents/README.md).
