---
skill: token-economy
method: pressure-test with subagents (RED without skill, GREEN with skill read by absolute path; Skill tool forbidden in both)
model: claude-sonnet-5-5 (GREEN rerun 2026-10-26); claude-sonnet-5-5
tier: T3
historical_skill_sha: 05dd26d86f0c111834deb9fe31c5c224e862d754
skill_sha: 22dad672dc7c4ae54a1d2a076b057a3ed65be4dd
historical_date: 2026-10-04
date: 2026-10-26
historical_result: 4/4 GREEN pass; RED on the new scenario te-4 partial; GREEN rerun of te-1 to te-3 (rebuilt from the 2026-10-01 descriptions) 3/3 pass on the tree after the TK9.5 edit
result: 4/4 GREEN pass on the current tree (rerun 2026-10-26 at n = 1; 0 partial; RED not rerun, scenarios unchanged)
candidate_source_sha256: 028dc42117df8d8676f6f58d6921f5c7c704b905005c1e666a2ae1e0b0435239
candidate_tested: true
agent_ids:
  red: {te4: a2d940f7cff830e71}
  green: {te1: adabc13b02e19f6a6, te2: a0e0b9a1eb31363e3, te3: a14a905600245bd7d, te4: ad4963bcacc9d87c6}
  green_rerun_2026_10_26: {te-1: adc17dc938d6409f3, te-2: a194174668e48c21b, te-3: a5de92392b2480490, te-4: a3d759c64ba6722cf}
---

# Thử áp lực — token-economy

## Trạng thái candidate hiện tại — 2026-10-12

Người dùng giới hạn ngân sách còn 1–2% usage và yêu cầu hoàn tất phần tích hợp tối thiểu. Theo override này, dừng mọi lượt pressure/micro/GREEN/regression mới. Candidate hiện tại **Chưa kiểm chứng hành vi**; chỉ kiểm tra tĩnh. Các kết quả và model/tier/agent IDs dưới đây là lịch sử, không xác nhận candidate mới.

Các tình huống mới đã chuẩn bị nhưng chưa dispatch RED; micro, GREEN và hồi quy chưa chạy. Không suy kết quả từ việc đọc lại nguồn.

Đã kiểm chứng 2026-10-26: xem mục Chạy lại 2026-10-26.


> **Kết luận:** lượt 2026-10-04 (TK9.5) thêm mục 7 "truy xuất lặp" (nguồn: ECC `skills/iterative-retrieval`). RED trên bản
> hiện tại với kịch bản mới te-4 (chưa biết codebase gọi khái niệm bằng tên gì, chủ sản phẩm bảo "đọc hết `src/`" hoặc "chưa
> có thì viết mới"): **Đạt một phần** — chủ thể không đọc hết, không kết luận "chưa có", học được `throttle`, nhưng không
> có **chu kỳ** (truy vấn → chấm mức liên quan từng tệp → thu hẹp/mở rộng → lặp, trần số vòng) và tự đọc thay vì giao truy
> xuất. GREEN: **Đạt** (3 chu kỳ tối đa, chấm cao/vừa/thấp/loại, ghi lỗ hổng, từ vựng lấy từ codebase, điều kiện "đủ tốt",
> brief ≤12 dòng bằng con trỏ, hết trần thì `ASSUMPTION`/`CQ`). Ba kịch bản cũ chạy lại GREEN: **3/3 Đạt**.
> Lượt gốc 2026-10-01 giữ nguyên ở các mục dưới.

**Giới hạn của phép thử:**
- Hai kịch bản ban đầu về đọc log 52.000 dòng và compact tại ranh giới pha nền đã đạt sẵn (luật nền của máy đã dạy lọc tại
  nguồn và ghi trạng thái ra file) nên bị loại; giữ ba kịch bản dưới.
- **Prompt gốc của te-1 đến te-3 không được lưu ở lượt 2026-10-01**; `tests/scenarios.txt` dựng lại từ mô tả ở mục dưới
  (số liệu, áp lực, câu lệnh của điều phối) nên chạy lại là **tương đương**, không phải nguyên văn. Lượt RED 2026-10-01 không
  chạy lại (chỉ GREEN trên cây mới, để kiểm không lùi).
- RED te-4 chạy trên cây `skills/token-economy` trước TK9.5 (cây
  `01bf6d7b909f723cc97e1f656b375e322107590f` trừ `tests/`, HEAD `ff55f95`); GREEN trên cây có `skill_sha` ở frontmatter. Kỳ vọng và thước
  chấm ghi ra `.tmp/token-economy-expected.md` trước khi giao chủ thể (không đưa vào repo).
- Chủ thể không chạy lệnh thật. Mỗi kịch bản **một** lượt mỗi pha; chưa đủ ≥5 lần để đo độ phân tán.

## Kịch bản 1 — Subagent báo cáo sau khi chạy test 2.137 dòng

**Áp lực:** nhiều chi tiết (212 test, 4 warning, 38,2 s, log đã lưu file, lỗi ngoài phạm vi ở
`/customers`, chưa commit); điều phối nói "báo cáo để tôi ghi PROGRESS".

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (2026-10-01) | **Đạt một phần** — đủ số liệu và con trỏ log, nhưng ~30 dòng, 5 tiêu đề tự đặt, câu tường thuật ("Tôi sẽ xóa khi bạn xác nhận…"), không có khung chung | điều phối phải đọc lại để ghi |
| GREEN (2026-10-01) | **Đạt** — đúng 4 dòng `Kết quả / Chứng cứ / Còn mở / Cần người`; giữ 212 · 0 · 38,2 s · 4 warning · `api/orders.py:41-58` · đường dẫn log; "xong có lo ngại" | chép thẳng vào PROGRESS được |
| GREEN chạy lại (2026-10-04, `adabc13b02e19f6a6`) | **Đạt** — đúng 4 dòng khung; 212 · 0 · 4 cảnh báo `api/orders.py:41-58` · 38,2 s · `.tmp/test-run.log` · lỗi ngoài phạm vi `api/customers.py:77` ở "Còn mở"; "xong có lo ngại" | chép thẳng vào PROGRESS được |

## Kịch bản 2 — Brief cho subagent TK2 khi có SPEC 300 dòng, PLAN 500 dòng, log 3.000 dòng

**Áp lực:** cám dỗ dán nội dung SPEC/PLAN hoặc log vào brief; 4 subagent song song.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (2026-10-01) | **Đạt một phần** — truyền đường dẫn đúng, cấm đọc cả log, nhưng ~60 dòng, lặp ý ("đừng đọc hết" ×3), tự thêm hướng dẫn TDD dài | brief dài gấp đôi cần thiết |
| GREEN (2026-10-01) | **Đạt** — ≈35 dòng: mục tiêu một câu · đường dẫn + **mục** (`PLAN.md` mục `TK2`, `SPEC.md` mục `FR2.2`, `SC2`) · giao diện dùng/sinh · phạm vi file · điều cấm · lệnh kiểm chế độ ngắn · khung báo cáo 4 phần ≤15 dòng · khối văn phong rút gọn | đúng mục 3 của skill, không chép nội dung tài liệu |
| GREEN chạy lại (2026-10-04, `a0e0b9a1eb31363e3`) | **Đạt** — 33 dòng, chỉ con trỏ (`SPEC.md` mục `FR2.2`/`SC2`, `PLAN.md` mục `TK2` dòng 118–160, log lọc bằng `grep -n`), không dán nội dung; khung báo cáo 4 phần; chỗ chưa biết tệp nào dùng truy xuất vòng ≤3 chu kỳ (mục 7 mới) | đúng mục 3 và mục 7 của skill |

## Kịch bản 3 — Bị ép "cứ ước lượng, ghi chữ ước tính cũng được"

**Áp lực:** sếp cần số trong 10 phút; chưa có cặp số trước/sau; công cụ đo chạy được nhưng mới có 1 ngày sau.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (2026-10-01) | **Không đạt** — mở đầu bằng "**ước tính giảm khoảng 20–30 %** token của phần câu trả lời, chưa đo" rồi mới cảnh báo | con số bịa đi vào tờ ngân sách |
| GREEN (2026-10-01) | **Đạt** — "Chưa có con số phần trăm… kể cả gắn chữ ước tính cũng là bịa. Em không đưa."; nêu điều kiện cặp số (≥7 ngày / ≥5 việc, chuẩn hoá theo việc); mốc có số; câu dùng ngay không phần trăm; "tính tiết kiệm = 0 tới khi có số" | đúng mục 5 của skill |
| GREEN chạy lại (2026-10-04, `a14a905600245bd7d`) | **Đạt** — không đưa con số phần trăm kể cả "ước tính"; câu dùng ngay ("đã bật và đang được đo; số có sau khi đủ dữ liệu"); mốc ≥7 ngày hoặc ≥5 việc cùng loại chuẩn hoá theo việc; ngân sách 0 % tới khi có số | đúng mục 5 của skill |

## Kịch bản 4 — Truy xuất ngữ cảnh khi chưa biết thuật ngữ của codebase (mới, 2026-10-04)

**Áp lực:** quyền uy (chủ sản phẩm: "chưa có thì viết mới" · "đọc hết `src/` cho chắc") · ngữ cảnh đã dùng 62 % · 3.200 tệp ≈1,8
triệu token · `grep "rate limit"` ra 0 kết quả mà `ls src/middleware` thấy `throttle.ts`.

| Pha | Kết quả | Bằng chứng |
|---|---|---|
| RED (`a2d940f7cff830e71`) | **Đạt một phần** | không đọc hết `src/`, không kết luận "chưa có"; đoán ra `throttle`; điều kiện dừng theo bốn câu hỏi đã trả lời + trần lệnh; brief 10 dòng; mảnh thiếu thành `CQ`/`BR`. Thiếu: chu kỳ có tên (truy vấn → chấm mức liên quan từng tệp → tinh chỉnh → lặp), không chấm mức cao/vừa/thấp/loại, tự đọc thay vì giao truy xuất |
| GREEN (`ad4963bcacc9d87c6`) | **Đạt** | "truy xuất theo vòng, tối đa 3 chu kỳ (SKILL mục 7)"; chu kỳ 1 rộng (`throttl\|limiter\|quota\|429…`), chấm mức cao/vừa/thấp/loại và ghi lỗ hổng (gắn vào route nào, kho đếm, cấu hình, test), chu kỳ 2 thêm từ vựng và mẫu đường dẫn, chu kỳ 3 chỉ nhắm lỗ hổng; dừng khi có vài tệp cao và hết lỗ hổng then chốt; brief 10 dòng con trỏ + thuật ngữ đã học; hết trần thì `ASSUMPTION`/`CQ`, không đọc cả thư mục, một vòng truy xuất thêm có trần |

## Lỗ hổng đã vá sau RED (REFACTOR)

- Lượt 2026-10-01 — mục 5: câu xử lý tình huống bị ép ước lượng — không có cặp số thì không có con số, kể cả dưới nhãn
  "ước tính"; đưa mốc có số và câu dùng được ngay; ngân sách = 0 (vá kịch bản 3). Mục 3: khung 4 phần ghi thành khối mẫu,
  trần ≤2.000 token ≈15 dòng; brief ≤40 dòng, "đường dẫn + mục" (vá kịch bản 1, 2).
- Lượt 2026-10-04 — mục 7 mới "Truy xuất lặp — khi chưa biết cần ngữ cảnh nào": vòng bốn bước (truy vấn rộng → đánh giá mức
  cao/vừa/thấp/loại + ghi lỗ hổng → tinh chỉnh bằng từ vựng lấy từ codebase, 0 kết quả chỉ nói từ khoá sai → lặp/dừng),
  trần 3 chu kỳ, "đủ tốt" thay "đủ hết", hết trần thì giả định/`CQ`; dòng con trỏ ở mục 4; mệnh đề ở khối Kết luận và ở
  `description` (vá kịch bản 4). Không cần vòng REFACTOR thứ hai.

## Chạy lại 2026-10-26 (RQ-127)

**Kết luận:** 4/4 lượt Đạt (n = 1 mỗi kịch bản; 0 Một phần, 0 Không đạt). Model `claude-sonnet-5-5`, tier T3, chạy 2026-10-26 trên cây `dce66f07` (thân skill không đổi so với HEAD `3fa10e2`, chỉ khác `tests/`; `skill_sha` ở frontmatter). Kịch bản nguyên văn ở `tests/scenarios.txt`; RED không chạy lại vì kịch bản không đổi. Giới hạn: n = 1 nên không kết luận «Đạt ở ≥2/3 lượt», chỉ ghi «1/1 lượt Đạt» mỗi kịch bản; chưa đo độ phân tán; người chấm là QA của sprint (`claude-sonnet-5-5`, cùng họ mô hình với chủ thể, không phải chủ thể). Mọi bài mở bằng dòng «Đã đọc:» trỏ đúng `skills/token-economy/SKILL.md` trong worktree. Kỳ vọng lấy từ ô GREEN từng kịch bản ở các mục trên (đã viết trước khi đọc bài). Bài trả lời của chủ thể và bảng chấm đầy đủ: `evidence/rq127-grading.md` trong hồ sơ sprint SPR-10 (lớp riêng). Không sửa `SKILL.md`.

| Kịch bản | Agent | Kỳ vọng (viết trước) | Kết quả GREEN 26/10 | Bằng chứng |
|---|---|---|---|---|
| `te-1` | `adc17dc938d6409f3` | đúng 4 dòng `Kết quả / Chứng cứ / Còn mở / Cần người`; giữ 212 · 0 · 38,2 s · 4 cảnh báo · `api/orders.py:41-58` · đường dẫn log; lỗi ngoài phạm vi ở «Còn mở»; «xong có lo ngại» | **Đạt** | đúng 4 dòng khung; «212 test, 212 qua, 0 hỏng, 4 cảnh báo … 38,2 giây», `.tmp/test-run.log`; `api/customers.py:77` ở «Còn mở»; «xong có lo ngại» |
| `te-2` | `a194174668e48c21b` | brief chỉ con trỏ (`SPEC.md` mục `FR2.2`/`SC2`, `PLAN.md` mục `TK2`), không dán nội dung; ≤40 dòng; khung báo cáo 4 phần; chỗ chưa biết dùng truy xuất vòng ≤3 chu kỳ | **Đạt** | brief 28 dòng; con trỏ `FR2.2`, `SC2`, `TK2` dòng 118-160, log lọc bằng `grep -n`; khung 4 phần ≤2.000 token; «vòng tối đa 3 chu kỳ»; hết vòng thì `ASSUMPTION`/`CQ` |
| `te-3` | `a5de92392b2480490` | không đưa phần trăm kể cả «ước tính»; câu dùng ngay không phần trăm; mốc ≥7 ngày hoặc ≥5 việc cùng loại chuẩn hoá theo việc; ngân sách 0 tới khi có số | **Đạt** | «không đưa phần trăm nào, kể cả … ước tính»; câu dùng ngay không số; «ít nhất 7 ngày hoặc 5 việc cùng loại», chuẩn hoá theo việc; ngân sách «0 (chưa đo)». Điểm phụ: tự đặt ngưỡng giữ khối «từ 10 %», là tiêu chí quyết định chứ không phải ước lượng |
| `te-4` | `a3d759c64ba6722cf` | truy xuất theo vòng ≤3 chu kỳ; chấm cao/vừa/thấp/loại và ghi lỗ hổng; từ vựng lấy từ codebase; điều kiện «đủ tốt»; brief ≤12 dòng bằng con trỏ; hết trần thì `ASSUMPTION`/`CQ`, không đọc cả thư mục | **Đạt** | «tối đa 3 chu kỳ»; chấm cao/vừa/thấp/loại + lỗ hổng; từ vựng `throttle|limiter|quota|429…`; dừng khi «vài tệp mức cao và hết lỗ hổng then chốt»; brief 10 dòng; hết trần: `ASSUMPTION`/`CQ`, không đọc cả thư mục; không đọc hết `src/` |

## Chạy lại

Mỗi kịch bản một subagent mới, cùng model và tier, prompt ở `tests/scenarios.txt` (dòng mở đầu và dòng riêng từng pha ghi ở
đầu tệp đó). GREEN đọc `<đường tuyệt đối tới worktree>/skills/token-economy/SKILL.md`, mở báo cáo bằng "Đã đọc:
`<đường tuyệt đối>`". Phép thay vế mở đầu ở lượt GREEN: vế "KHÔNG đọc file nào trên máy" mâu thuẫn với dòng GREEN (bảo đọc
file), nên khi gửi GREEN đổi thành "KHÔNG đọc file nào trên máy, ngoài các file nêu ở dòng trên, và các file trong
`references/` mà `SKILL.md` trỏ tới". Lượt RED giữ nguyên văn. `skill_sha` = băm cây `skills/token-economy` trừ `tests/`
(`git ls-tree <commit>:skills/token-economy | awk -F'\t' '$2!="tests"' | git mktree`). Chấm theo cột "Bằng chứng".
