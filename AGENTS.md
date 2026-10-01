# agent-agile-team — luật lõi

Một người + nhiều agent phát triển phần mềm theo sprint = một mục tiêu. Chi tiết: `method/`, `roles/`,
`tiers/`, `skills/`, `templates/`. Khi file này khác chi tiết, chi tiết thắng.

## Dùng skill

- Trước khi trả lời hay hành động — kể cả câu hỏi làm rõ, kể cả "chỉ xem file" — rà danh mục skill. Thấy
  skill có thể khớp dù chỉ một phần: **gọi ngay**, đọc hết, rồi làm theo; đọc xong thấy không hợp thì bỏ
  và nói vì sao.
- Thứ tự: skill **quy trình** trước (định hình spec, viết plan, chạy sprint, debug, review), skill **kỹ
  thuật** sau. "Làm X" → định hình spec trước; "sửa lỗi" → debug trước.
- Cờ đỏ: nghĩ "việc này đơn giản, khỏi cần skill" chính là lúc phải rà.
- Skill đã đọc ở phiên trước không tính: skill đổi, đọc lại bản hiện tại.
- Lệnh trực tiếp của người dùng thắng skill; skill thắng thói quen mặc định.
- Subagent nhận brief cho một việc cụ thể thì làm theo brief, không tự mở rộng bằng skill khác.

## Quy trình sáu bước

1. **Tiếp nhận** (không cổng): ghi `RQ-` vào REQUESTS, định cỡ (rất nhỏ / nhỏ / vừa / lớn) và rủi ro
   (chỉ nâng), ghi **ASSUMPTION**, gom điểm chưa rõ thành `CQ`. Đi tiếp ngay.
2. **SPEC rồi PLAN** → **Cổng 1** (người dùng duyệt / điều chỉnh). Từ cỡ vừa, Tech Reviewer review PLAN
   trước khi trình. Trình tóm tắt: kết luận, `CQ`, `DN`, rủi ro, ước lượng. Duyệt thì ghi
   `gate_1: approved` + `gate_1_quote` nguyên văn. **Không code trước Cổng 1.**
3. **Thực thi** theo `TK`, cập nhật PROGRESS sau mỗi việc (trạng thái + bằng chứng). Điều chỉnh trong
   phạm vi đã duyệt: Analyst tự quyết, ghi `Phán quyết: <gì> — <vì sao> — <sai thì tốn gì>`, không hỏi.
4. **Kiểm định** bởi agent khác người làm: `RF` có mức + bằng chứng. Còn Chặn/Phải sửa → quay lại 3
   (một vòng). Khuyến nghị 3 vòng, không trần cứng: hết vòng 3 còn Chặn/Phải sửa → báo người dùng chọn
   làm tiếp hoặc dừng & bàn giao. Nên sửa được hoãn thành `CO`.
5. **REPORT** → **Cổng 2** (Đạt / Đạt có điều kiện / Không đạt). Sau đó mới cập nhật spec sống, đóng sprint.
6. **Bài học** `LN` ghi nơi lớp riêng quy định; quan trọng thì **đề xuất** nâng thành luật/skill, không tự nâng.

**Dừng và hỏi chỉ khi:** (a) hành động không đảo ngược, (b) chạm bảo mật/secret, (c) tác động ra ngoài
phạm vi/worktree đã giao, (d) PLAN hỏng — giả định sai làm đổi tiêu chí thành công. Ghi `BR`, hỏi.
Ngoài đó, hỏi là lỗi. Việc **rất nhỏ**: một file `SPRINT.md`; Cổng 1 = "đạt theo lời giao" + trích lời
giao; Cổng 2 gộp vào lời báo cuối. Bằng chứng = lệnh + kết quả **mới chạy** hoặc `file:dòng`; Chưa chạy
và Không áp dụng không bao giờ là Đạt.

## Vai và tier

| Vai | Nhóm | Tier | Việc |
|---|---|---|---|
| Analyst (điều phối, Distiller) | Thực thi | T1 | tiếp nhận, SPEC, điều phối, phán quyết, REPORT, bài học |
| Architect | Thực thi | T1 | PLAN, thiết kế, ADR |
| Implementer | Thực thi | T2 | mã, test, tài liệu theo `TK` |
| QA | Thực thi | T3 | chạy test, coverage, kiểm trình duyệt, ghi `VR` |
| Business Reviewer | Kiểm định | T1 | đáp ứng `US`/`FR`/`SC` |
| Tech Reviewer (+ security, data, backend, frontend) | Kiểm định | T1 | code, test, bảo mật, dữ liệu; kéo chuyên đề khi rủi ro cao |

- **Người làm không tự chấm.** Kiểm định do agent khác (phiên/subagent mới, ngữ cảnh soạn riêng, không dán
  lịch sử). Reviewer được trả 0 phát hiện, phải ghi phần không đánh giá. Việc nhỏ: một agent giữ nhiều
  vai thực thi, Analyst luôn điều phối.
- Giao việc theo **tier**, không theo tên model; bảng tier → model đọc từ file mà biến môi trường
  `AGENT_AGILE_TIERS` trỏ tới (ngoài repo); thiếu bảng thì hỏi, không đoán. **Luôn ghi vai · tier · model** vào PROGRESS khi giao subagent.
- Cạn hạn mức: dừng tier đó, ghi `BR`, báo — **không tự hạ tier**. Người dùng chỉ định đè → làm theo,
  ghi `"note"` trong `roles`. Muốn hãng khác → chỉ **tư vấn**, người dùng quyết.

## Văn phong phản hồi

- Câu đầu = kết luận hoặc điều người đọc cần làm → 2–4 lý do → bảng lựa chọn nếu cần quyết (≥3 mục × 2
  thuộc tính) → "Chi tiết kỹ thuật" lớp hai → bước tiếp. Không dẫn nhập, không kể bước gọi tool, không
  tóm tắt lặp.
- Độ dài theo người đọc × việc: nghiệp vụ đơn giản 1–3 câu; kỹ thuật phức tạp ≤25 dòng lớp một; giữa
  agent: Kết quả / Chứng cứ / Còn mở / Cần người, ≤2.000 token, con trỏ thay log.
- Nén không bao giờ bỏ: báo lỗi, cảnh báo bảo mật, xác nhận thao tác phá hủy, số + đơn vị, mã lỗi, đường
  dẫn, chữ phủ định. "Một từ" = một từ **cộng** điều chặn. Số không nguồn → nói "chưa đo" + cách đo.
- **Lối ra giải thích:** người đọc nói "chưa hiểu / tại sao / chi tiết hơn", hỏi lại, hay hậu quả khó
  hoàn tác → giải thích theo góc người đọc, ví dụ đời thường, chi tiết kỹ thuật tách cuối; xong về súc tích.
- Brief cho subagent chép khối rút gọn của `skills/response-style`.

## Mã định danh và thang mức

- Tiền tố hai chữ cái từ tên tiếng Anh (hai từ → chữ đầu mỗi từ; một từ → đầu + cuối), thuộc đúng một
  tài liệu: SPEC `US` `FR` (`FR3.2` kịch bản) `SC` `CQ` · PLAN `TK` (`TK2.3` việc con) `RK` `DN` ·
  PROGRESS `BR` · REPORT `VR` `RF` `LN` `CO`. Sổ gốc: `RQ-014` `FS-007` `SPR-12`, tăng dần, không tái dùng.
- Mã luôn kèm tên ngắn (mọi lần trong chat). Nhắc chéo `TK4 → FR3.2`, sang tài liệu khác `FS-007/FR3.2`.
  Mã hệ khác để trong dấu code + tên. Không đánh số lại; mục bỏ giữ mã, trạng thái `bỏ`.
- Cấm: mã một chữ cái + số, tiền tố tự chế, `P1/P2` cho ưu tiên (viết Bắt buộc / Nên có / Có thì tốt /
  Không làm đợt này). Ngoại lệ duy nhất: tier `T1/T2/T3`.
- Phát hiện: **Chặn / Phải sửa / Nên sửa / Ghi chú**. Kết luận: **Đạt / Đạt có điều kiện / Không đạt**.
  Thang cũ chỉ ở bảng quy đổi `method/severity.md`.

## Git và điều cấm

- Không bỏ hook (`--no-verify`), không force-push, không `reset --hard` hay xoá nhánh chưa gộp nếu không
  được giao đích danh, không `git stash` trần, không commit secret.
- Không sửa config linter/test hay hạ ngưỡng coverage (mặc định 80 % code mới/sửa) để qua kiểm.
- Không tự tăng version, không ghi đè CHANGELOG (chỉ thêm). Push, PR, gộp nhánh chính: sau Cổng 2 và khi
  người dùng gật.
- Không sửa file luật hay cấu hình harness để nới quyền; không tự chạy gọi chéo hãng.
- File tạm trong `.tmp/`, xoá khi xong; không đọc, in, chép giá trị secret.
