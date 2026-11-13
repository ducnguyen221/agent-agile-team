# agent-agile-team — luật lõi

Chi tiết: `method/`, `roles/`,
`tiers/`, `skills/`, `templates/`. Khi file này khác chi tiết, chi tiết thắng.

## Dùng skill

- Trước khi trả lời hay hành động — kể cả câu hỏi làm rõ, kể cả "chỉ xem file" — rà danh mục skill. Thấy
  skill có thể khớp dù chỉ một phần: **gọi ngay**, đọc hết, rồi làm theo; đọc xong thấy không hợp thì bỏ
  và nói vì sao.
- Thứ tự: skill **quy trình** trước (spec, plan, sprint, debug, review), **kỹ thuật** sau; "làm X" → spec trước, "sửa lỗi" → debug trước.
- Skill đã đọc ở phiên trước không tính: đọc lại bản hiện tại.
- Lệnh trực tiếp của người dùng thắng skill; skill thắng thói quen mặc định.
- Subagent nhận brief cho một việc cụ thể thì làm theo brief, không tự mở rộng bằng skill khác.

## Quy trình sáu bước

1. **Tiếp nhận** (T1, **một tin gom**): đọc đầu bài, phân tích, rồi gửi **tin mở autopilot** (mẫu: `method/autopilot.md` mục 2; có khuyến nghị bậc làm thẳng / rất nhỏ / nhỏ / vừa / lớn). Không chờ trả lời: câu hỏi phản biện kèm đề xuất; ghi `RQ-`, rủi ro (chỉ
   nâng), **ASSUMPTION**, `CQ` cho Cổng 1. Không hỏi lẻ. Bỏ tin này khi "không cần sprint" hoặc làm thẳng không mơ hồ.
2. **SPEC rồi PLAN** → **Cổng 1**, Gate Delegate (phiên mới, T1) ký. Từ cỡ vừa, Tech Reviewer/Advisor review PLAN
   trước. Hồ sơ: kết luận, `CQ`, `DN`, rủi ro, ước lượng, trần phiên. Ký thì ghi
   `gate_1: approved` + `gate_1_quote` nguyên văn. **Không code trước Cổng 1.** Lời cấp, người ký — `method/autopilot.md`.
3. **Thực thi** theo `TK`, cập nhật PROGRESS sau mỗi việc (trạng thái + bằng chứng). Điều chỉnh trong
   phạm vi đã duyệt: Analyst tự quyết, ghi `Phán quyết: <gì> — <vì sao> — <sai thì tốn gì>`, không hỏi.
4. **Kiểm định** bởi agent khác người làm: `RF` có mức + bằng chứng. Còn Chặn/Phải sửa → quay lại 3
   (một vòng). Khuyến nghị 3 vòng, không trần cứng: hết vòng 3 còn Chặn/Phải sửa → Gate Delegate quyết làm tiếp
   hay dừng & bàn giao, ghi vào báo cuối, không báo người giữa chừng. Nên sửa được hoãn thành `CO`.
5. **REPORT** → **Cổng 2** (Đạt / Đạt có điều kiện / Không đạt), Gate Delegate phiên mới ký; Đạt có điều kiện
   không mở gộp `main`. Sau đó mới cập nhật spec sống, đóng sprint. Dừng: `Dừng autopilot.` — `method/autopilot.md`.
6. **Bài học** `LN` ghi nơi lớp riêng quy định; quan trọng thì **đề xuất** nâng thành luật/skill, không tự nâng.

<!-- san-cung:start -->
**Dừng chỉ khi:** (a) hành động không đảo ngược, (b) chạm bảo mật/secret, (c) tác động ra ngoài
phạm vi/worktree đã giao, (d) PLAN hỏng — giả định sai làm đổi tiêu chí thành công. Ghi `BR`, không hỏi người giữa
chừng. (a), (b), bảy mục luôn chặn (`method/autopilot.md` mục 5): Gate Delegate **không quyết thay**, chỉ hoãn/bỏ/đổi
cách; dừng bước đó, vào "Việc cần người" của báo cuối; việc khác chạy tiếp. (c), (d), câu hỏi nghiệp
vụ/cổng: Gate Delegate quyết. Ngoài đó, dừng là lỗi. **Làm thẳng** (bậc ở `method/sizing.md`): việc 1–2 thao tác có
kết quả rõ, hoặc người dùng nói rõ không cần sprint → làm ngay, không `RQ-`/`SPRINT.md`/sổ; vẫn giữ Git và điều
cấm, vẫn kiểm (lệnh + kết quả mới chạy) và báo trong lời trả lời. Không áp khi chạm `risk_tags`, file luật, secret,
hành động không đảo ngược — trừ khi người dùng nói rõ không cần sprint; lúc đó mọi cổng xin phép khác vẫn giữ (sửa
file luật vẫn phải được gật). Việc **nhỏ** và **rất nhỏ** dùng một file `SPRINT.md`: rất nhỏ
chỉ Kế hoạch + Kết quả, Cổng 1 = "đạt theo lời giao" + trích lời giao, Cổng 2 gộp lời báo cuối; nhỏ đủ bốn phần
và hai cổng. Bằng chứng = lệnh + kết quả **mới chạy** hoặc `file:dòng`; Chưa chạy
và Không áp dụng không bao giờ là Đạt.
<!-- san-cung:end -->

## Vai và tier

Thực thi: **Analyst** (T1; điều phối, Distiller; tiếp nhận, SPEC, điều phối, phán quyết, REPORT, bài học) · **Architect** (T1; PLAN, ADR) · **Implementer** (T2; mã, test, tài liệu theo `TK`) · **QA** (T3; chạy test, coverage, kiểm trình duyệt, ghi `VR`) · **Researcher** (T3; dossier có nguồn, không kết luận).
Kiểm định: **Business Reviewer** (T1; `US`/`FR`/`SC`) · **Tech Reviewer** (T1; code, test, bảo mật, dữ liệu; + security, data, backend, frontend khi rủi ro cao) · **Gate Delegate** (T1; ký Cổng 1 và 2 mặc định; phiên mới, khác người làm, tier ≥). Tư vấn: **Advisor** (T1; phản biện SPEC/PLAN trước Cổng 1; không viết, không duyệt). Thẻ vai: `roles/README.md`.

- **Người làm không tự chấm.** Kiểm định do agent khác (phiên/subagent mới, ngữ cảnh soạn riêng, không dán
  lịch sử). Reviewer được trả 0 phát hiện, phải ghi phần không đánh giá. Việc nhỏ: một agent giữ nhiều
  vai thực thi, Analyst luôn điều phối.
- Giao việc theo **tier**, không theo tên model; bảng tier → model đọc từ `AGENT_AGILE_TIERS` (ngoài repo); thiếu bảng thì hỏi, không đoán. **Luôn ghi vai · tier · model · effort** vào PROGRESS khi giao subagent (effort: số 1–5, `method/effort-scale.md`).
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
- **Trao đổi với người** (luật: `method/communication.md`): tóm tắt từ file → link `[tên:dòng](đường:dòng)`; file ngoài thư mục phiên → đường tuyệt đối trong dấu code, không làm link, nói rõ chưa bấm được. Hỏi chốt → một dòng hỏi kết thúc "?", bảng phương án (đánh đổi · rủi ro · công sức · khi nào chọn), **KHUYẾN NGHỊ** + lý do, link căn cứ; chưa trả lời → chỉ làm việc không phụ thuộc quyết định, không tự chọn; im lặng không là duyệt cổng, việc không đảo ngược. "Chưa hiểu / tại sao / chi tiết hơn", hỏi lại, hậu quả khó hoàn tác của quyết định đang hỏi → diễn giải (`explain`): đủ dữ kiện, không thêm sự kiện hay số suy ra, giải nghĩa viết tắt; xong về súc tích.
- Brief cho subagent chép khối rút gọn của `skills/response-style`.

## Mã định danh và thang mức

- Tiền tố hai chữ cái từ tên tiếng Anh (hai từ → chữ đầu mỗi từ; một từ → đầu + cuối), thuộc đúng một
  tài liệu: SPEC `US` `FR` (`FR3.2` kịch bản) `SC` `CQ` · PLAN `TK` (`TK2.3` việc con) `RK` `DN` ·
  PROGRESS `BR` · REPORT `VR` `RF` `LN` `CO`. Sổ gốc: `RQ-014` `FS-007` `SPR-12`, tăng dần, không tái dùng.
- Mã luôn kèm tên ngắn (mọi lần trong chat). Trước mọi danh sách / bảng mã: câu dẫn nói tài liệu nào và mã
  là gì, nghĩa in đậm — "SPEC có 10 **user story** (US):".
  Không đánh số lại; mục bỏ giữ mã, trạng thái `bỏ`. Nhắc chéo, mã hệ khác: skill `id-convention`.
- Cấm: mã một chữ cái + số, tiền tố tự chế, `P1/P2` cho ưu tiên (viết Bắt buộc / Nên có / Có thì tốt /
  Không làm đợt này). Ngoại lệ duy nhất: tier `T1/T2/T3`.
- Phát hiện: **Chặn / Phải sửa / Nên sửa / Ghi chú**. Kết luận: **Đạt / Đạt có điều kiện / Không đạt**.
  Thang cũ chỉ ở bảng quy đổi `method/severity.md`.

<!-- san-cung:start -->
## Git và điều cấm

- Không bỏ hook (`--no-verify`), không force-push, không xoá nhánh chưa gộp, không `git stash` trần, không commit
  secret; không `reset --hard`/`clean -fd[x]`/`checkout -- .`/`restore .` khi chưa commit sao lưu vào `backup/<ngày-giờ>`;
  không phá hoàn tác: `reflog expire`, `gc --prune=now`, `update-ref -d`, `filter-branch`/`-repo`, xoá tag/nhánh
  `backup/*` hay `.git`, `push --delete`/`+ref` (`method/git-conventions.md`).
- Không sửa config linter/test hay hạ ngưỡng coverage (mặc định 80 % code mới/sửa) để qua kiểm.
- Version do Gate Delegate quyết theo bảng phiên bản; không ghi đè CHANGELOG (chỉ thêm). Push, PR, gộp `main`, tag,
  phát hành: chỉ khi PLAN có lời cấp + Cổng 2 Đạt, sau kiểm ruleset và quét secret
  (`method/autopilot.md` mục 5); Đạt có điều kiện thì không.
- Không sửa file luật hay cấu hình harness để nới quyền; không tự chạy gọi chéo hãng.
- File tạm trong `.tmp/`, xoá khi xong; không đọc, in, chép giá trị secret.
<!-- san-cung:end -->
