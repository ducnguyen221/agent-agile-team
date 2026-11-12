---
skill: explain
method: pressure-test with subagents (RED without skill, GREEN with skill read first)
model: sonnet (subagent alias, runners); grader opus
date: 2026-11-13
result: 3/3 GREEN pass (CM-3, CM-4, CM-4b, n = 3 each); RED 3/3 failed at CM-3, 0/3 failed at CM-4 and CM-4b (baseline already passed)
tier: tier 2 (cũ T2) runners; tier 3 (cũ T1) grader
skill_sha: ab7e6369c3c88d98289a6221ecb684217c166862
---

# Thử áp lực — explain

> **Kết luận:** nền (không skill) trượt CM-3 (diễn giải đúng dữ kiện) cả 3 lượt; có skill đạt 3/3 ở CM-3, CM-4, CM-4b. **CM-4 và
> CM-4b nền đã đạt sẵn** (0/3 trượt), nên hai kịch bản này không phân biệt được có/không skill — SC4 chưa chứng minh
> được bằng phép thử này (CO, chủ: điều phối). Ca "chưa hiểu" để xem skill nào chạy (RK6) **chưa đo**: skill chưa cài vào danh mục
> của harness, subagent được ép đọc file skill.

Prompt nguyên văn: `tests/scenarios.txt`. RED: "không dùng Skill tool, không mở SKILL.md". GREEN: thêm dòng "đọc
`skills/explain/SKILL.md` trước rồi làm theo", chủ thể là subagent mới, ngữ cảnh soạn riêng, ghi câu trả lời ra file để grader (agent khác) đọc. Mỗi kịch bản n = 3. Grader chấm
theo bảng chấm cuối `scenarios.txt`; CM-3 hiểu **nghiêm** (số tự tính như "chậm 4,4 lần" là sự kiện lạ).

| Kịch bản | RED (nền) | GREEN (có skill) | Bằng chứng |
|---|---|---|---|
| CM-3 `/explain` đoạn kỹ thuật (6 số liệu + 2 đường dẫn + 1 cảnh báo + 4 viết tắt) | **Không đạt** 3/3 nghiêm (2/3 nới): ORM/N+1 không giải nghĩa; thêm số suy ra "4,4 / 4,5 / 4 lần"; 1 lượt thiếu "Chi tiết kỹ thuật" | **Đạt** 3/3: 9/9 dữ kiện, 4/4 viết tắt, không số lạ, cảnh báo ở đầu, ví dụ "sổ cái", "Chi tiết kỹ thuật" tách cuối, giữ "Chưa bật TLS" và "không cần dừng dịch vụ" | `vr-red-grading.md`, `vr-green-grading.md` mục B |
| CM-4 hai lượt: `/explain` rồi hỏi việc khác | **Đạt sẵn** 0/3 trượt (2 dòng, không tiêu đề) | **Đạt** 3/3 (1–2 dòng, không tiêu đề, đúng 15 phút / không dừng dịch vụ / cần file logo) | mục C |
| CM-4b "diễn giải từ giờ" giữ chế độ | **Đạt sẵn** 0/3 | **Đạt** 3/3 (8–10 dòng, ví dụ đời thường, đúng dữ kiện) | mục C |

Ghi chú của grader (không tính trượt): vài lượt thêm khẳng định nhỏ không có ở nguồn ("không đụng dữ liệu"); cm3-1 giải nghĩa p95 là "nhóm 5 % lượt chậm nhất" (ca biên).

## Giới hạn

- n = 3 mỗi ô; các lượt GREEN ép đọc file skill nên **không đo** việc danh mục skill làm agent tự bật `explain`.
- Runner và grader cùng họ model Claude; chưa chạy trên Codex/Antigravity.

## Chạy lại

Gửi từng prompt trong `tests/scenarios.txt` cho subagent mới. RED: không skill. GREEN: thêm dòng đọc `skills/explain/SKILL.md` trước. Phép thay vế mở đầu ở lượt GREEN: phần mở đầu mỗi kịch bản nói "KHÔNG đọc file nào trên máy", mâu thuẫn với dòng bảo đọc `SKILL.md`; khi gửi GREEN đổi vế đó thành "KHÔNG đọc file nào trên máy ngoài các file nêu ở dòng trên" (lượt 2026-11-13 đã làm như vậy; lượt RED giữ nguyên văn). Chấm bằng bảng cuối `scenarios.txt`. Sau khi sửa `SKILL.md`: commit rồi tính lại `skill_sha` (`tests/test_skill_tests.py`, hàm `tree_hash`).
