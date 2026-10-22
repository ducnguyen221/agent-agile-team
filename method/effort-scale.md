---
title: Effort scale 1–5 and task difficulty 1–5
type: method
status: active
updated: 2026-10-22
---

# Thang effort 1–5 và độ khó 1–5

> **Kết luận:** effort là một **số 1–5** dùng chung cho thẻ vai, bảng tier và cầu gọi chéo; mỗi vendor đổi số đó sang
> nhãn riêng ở khối `effort_scale` của bảng tier. Effort giao = max(sàn vai, độ khó), chỉ định của người dùng thắng;
> mức vendor không có chỉ hạ khi bảng ghi `fallback`.

## 1. Thang và ánh xạ vendor

| Mức | Nghĩa | Claude `--effort` | Codex `model_reasoning_effort` | Antigravity (hậu tố id) | `agy --effort` |
|---|---|---|---|---|---|
| 1 | rất dễ | `low` | `low` | `-low` | `low` |
| 2 | dễ | `medium` | `medium` | `-medium` | `medium` |
| 3 | vừa (sàn T1, Implementer) | `high` | `high` | `-high` | `high` |
| 4 | khó | `xhigh` | `xhigh` | không có | `xhigh` |
| 5 | rất khó, phân tích sâu | `max` | `max` | không có | `max` |
| ngoài thang | native-only | `ultracode` = cờ chế độ (`xhigh` + dynamic workflows), `ultrathink` = từ khoá một lượt | `ultra`, `none`, `minimal` | — | — |

Cột `agy --effort` chưa có bằng chứng capability; chưa dùng.

## 2. Độ khó 1–5

- **Độ khó 1–5** nối ba trục của task-routing (`scope_dependencies`, `plan_readiness`, `execution_complexity`, ordinal 0–2):
  1 = cả ba = 0 · 2 = max = 1 · 3 = đúng một trục = 2 · 4 = hai trục = 2 · 5 = cả ba = 2 **hoặc** T1/người dùng nâng tường
  minh có `Phán quyết:` (nhiều phương án chưa có tiền lệ, cần phân tích sâu). Mức 5 không bao giờ do máy suy từ số file.

## 3. Chọn effort khi giao việc

- **Công thức:** effort giao = max(sàn vai, độ khó); chỉ định của người dùng thắng. Cột Effort trong ma trận = **sàn**
  theo vai. Độ khó ≥ sàn + 2 → Analyst ghi `Phán quyết:` xét lại vai/tier trước khi nâng effort.
- **Quy tắc `↓`:** mức không có nhãn ở một vendor chỉ hạ khi bảng ghi `fallback.<vendor>: "clamp_to_max"`; mỗi lần hạ ghi
  `effort: clamped_by_table` vào PROGRESS; không ghi `fallback` → `effort_unsupported`, dừng đúng phần phụ thuộc.
- Ghi `Vai · tier · model · effort` — số kèm nhãn native, ví dụ `3 (high)` — vào PROGRESS.

## 4. Quan hệ với task-routing

`task-routing.md` còn `candidate_not_promoted` và dùng mức 1–4; file này là thang đang hiệu lực — khi promote task-routing thì gộp mục 1–2 của nó vào đây.
