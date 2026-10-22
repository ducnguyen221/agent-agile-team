# Ma trận vai × vendor (bản mẫu)

> **Kết luận:** bản mẫu công khai của ma trận vai → tier · model · effort cho ba harness; file thật nằm ở lớp riêng, do công cụ của lớp đó sinh từ bảng tier — không sửa tay; repo chỉ giữ `<model-id>`.

| Vai | Tier | Vendor | Model | Effort | Effort native | Ghi chú |
|---|---|---|---|---|---|---|
| Analyst | T1 | claude | `<model-id>` | 3 | `high` | ô tier T1 |
| Analyst | T1 | codex | `<model-id>` | 3 | `high` | ô tier T1 |
| Analyst | T1 | antigravity | `<model-id>` | 3 | `high` | ô tier T1 |
| Architect | T1 | claude | `<model-id>` | 3 | `high` | ô tier T1 |
| Architect | T1 | codex | `<model-id>` | 3 | `high` | ô tier T1 |
| Architect | T1 | antigravity | `<model-id>` | 3 | `high` | ô tier T1 |
| Implementer | T2 | claude | `<model-id>` | 3 | `high` | ô tier T2 |
| Implementer | T2 | codex | `<model-id>` | 3 | `high` | ô tier T2 |
| Implementer | T2 | antigravity | `<model-id>` | 3 | `high` | ô tier T2 |
| QA | T3 | claude | `<model-id>` | 2 | `medium` | ô tier T3 |
| QA | T3 | codex | `<model-id>` | 2 | `medium` | ô tier T3 |
| QA | T3 | antigravity | `<model-id>` | 1 | `low` | ô tier T3 |
| Researcher | T3 | claude | `<model-id>` | 2 | `medium` | override roles.researcher |
| Researcher | T3 | codex | `<model-id>` | 2 | `medium` | override roles.researcher |
| Researcher | T3 | antigravity | `<model-id>` | 2 | `medium` | override roles.researcher |
| Business Reviewer | T1 | claude | `<model-id>` | 3 | `high` | ô tier T1 |
| Business Reviewer | T1 | codex | `<model-id>` | 3 | `high` | ô tier T1 |
| Business Reviewer | T1 | antigravity | `<model-id>` | 3 | `high` | ô tier T1 |
| Tech Reviewer | T1 | claude | `<model-id>` | 3 | `high` | override roles.tech-reviewer |
| Tech Reviewer | T1 | codex | `<model-id>` | 3 | `high` | ô tier T1 |
| Tech Reviewer | T1 | antigravity | `<model-id>` | 3 | `high` | ô tier T1 |

## Thang 1–5 → native

| Mức | claude | codex | antigravity |
|---|---|---|---|
| 1 | `low` | `low` | `low` |
| 2 | `medium` | `medium` | `medium` |
| 3 | `high` | `high` | `high` |
| 4 | `xhigh` | `xhigh` | `high` (3↓, fallback) |
| 5 | `max` (+ultracode: cờ chế độ) | `max` | `high` (3↓, fallback) |

## Known

| Vendor | Model đã xem, cố ý không xếp |
|---|---|
| claude | — |
| codex | — |
| antigravity | — |
