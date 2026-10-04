# Changelog

Mục mới nhất đứng đầu. Tiêu đề mỗi mục là đúng chuỗi version trong các manifest (test đồng bộ
version kiểm điều này).

## 0.3.0 (2026-10-05)

Chưa phát hành. SPR-04 — nội dung Đợt 2 (phần mới), luật bậc việc đơn giản / phức tạp, sổ tập trung, quy tắc số phiên
bản, viết lại phòng sạch 7 đích private, trả nợ máy kiểm của SPR-02. Mức MINOR theo `method/conventions.md` mục 4.1: thêm
skill, agent và luật tương thích ngược, dự án cũ không phải sửa gì (phân vân → chọn mức cao hơn: chưa có thay đổi gãy nào).

- **Tiếp nhận và làm thẳng:** một tin gom nhắc mục tiêu, phản biện có đề xuất, bậc/rủi ro từng việc và hỏi mở sprint;
  chờ xác nhận rồi mới ghi yêu cầu. Bậc làm thẳng không có hồ sơ; định nghĩa thao tác không đếm tự kiểm/test đi kèm,
  giữ sàn cỡ cho sửa luồng/tính năng/rủi ro, cấm chia một mục tiêu để né sprint. Đồng bộ role, REQUESTS mẫu/sample,
  sizing/process và hướng dẫn nâng cấp. Intake QA cùng model: baseline 2/6 → GREEN 6/6 (`n = 1`); thước `in-4` sửa sau
  quan sát để tránh hỏi lại lời giao, giới hạn ghi trong file thử.
- **Tài liệu và giới thiệu:** bổ sung lỗi cài/cập nhật, nâng cấp `0.1`/`0.2` → `0.3.0`, tổng quan và chuẩn hoá;
  trang giới thiệu được quản lý ở repo riêng, ảnh quy trình PNG và nội dung theo hai luật mới. Gói này không chứa site.
- **Model thử skill:** máy kiểm chấp nhận tên GPT có phiên bản, giữ chặn placeholder; test hồi quy GPT thấy đỏ trước
  sửa và xanh sau sửa. Ba manifest đồng bộ `0.3.0`; không thay ngưỡng coverage hay config kiểm thử.
- **Sửa sau review phát hành:** "làm luôn" chỉ thúc tiến độ, không miễn sprint/vùng rủi ro; cần người dùng nói rõ
  "không cần sprint" cho đúng việc hoặc việc đủ điều kiện làm thẳng. Thu hẹp cam kết nâng cấp thành tương thích hình
  hồ sơ, nêu nội dung có thể cần sửa. Siết hình ID GPT: một major 1–99, minor 0–99 tuỳ chọn, đúng một family;
  đây là kiểm định dạng metadata, không thay bằng chứng model thật sự chạy hay khoá danh sách phiên bản hiện tại.
- **Ranh giới đầu vào và tin tiếp nhận:** nhãn `external_input` áp khi thêm/đổi ranh giới nhận và xử lý dữ liệu
  không tin cậy; trường UI có sẵn không tự tạo nhãn, chưa loại trừ tác động bảo mật vẫn nâng lớn. Tin tiếp nhận phải
  được viết nguyên văn trong lượt hiện tại; câu hứa "sẽ gửi tin gom" chưa phải sản phẩm tiếp nhận.

- **Bậc việc** (`TK2`): việc **rất nhỏ** một `SPRINT.md` hai phần (Kế hoạch, Kết quả), việc **nhỏ** một `SPRINT.md`
  bốn phần, từ cỡ vừa bốn tài liệu; `init --tiny` và `init --size small`, mẫu `templates/sprint/SPRINT-tiny.md`, luật
  `check` `sprint-size-mismatch`, `method/sizing.md` mục 5 đối chiếu luồng orch ↔ bậc việc ↔ cổng; hai sprint mẫu mới ở
  `samples/order-desk/`. `AGENTS.md` đổi đúng một câu (bậc nhỏ và rất nhỏ); sprint cũ dạng một file bốn phần cỡ rất nhỏ vẫn
  hợp lệ.
- **Sổ tập trung** (`TK3`): khoá `ledger.project` ở `.agile.json`, biến môi trường `AGENT_AGILE_LEDGER` (mẫu đường, máy cấp),
  khuôn `templates/registry/LEDGER.md`, bốn luật `check` (`ledger-missing-row`, `ledger-stale`, `ledger-unreadable`,
  `ledger-unconfigured`), `method/process.md` mục 11 "Ghi sổ tại cổng". Dự án không khai khoá thì không áp.
- **Phương pháp** (`TK4`): `method/review-gate.md` (cổng review bốn pha), `roles/verifier/dual-review.md` (hai reviewer
  độc lập cho việc có `risk_tags` `rules` / `secret` / `auth`), `method/process.md` mục 6.1 (thiết kế vòng lặp),
  `method/evidence.md` mục 8 (cổng giao hàng, luật văn bản không hook), `skills/verify-before-done/references/loop.md`,
  luật giữ spec sống ở `templates/registry/feature-spec.md`.
- **Thẻ vai và skill quy trình** (`TK5`): thẻ Architect và Implementer (tìm cái có sẵn, theo phong cách file đang sửa, lát
  giao được độc lập); `intake` (luật nghiệp vụ không đọc được từ mã, tiêu chí nghiệm thu quan sát được), `shaping-spec`
  (+ `references/spec-mining.md`, một `FR` một hành vi), `tdd` (ca biên bắt buộc có test), `verify-before-done`,
  `running-sprint` (nhắc ghi sổ ở cổng); mỗi skill sửa có RED/GREEN và `skill_sha` mới.
- **Chuẩn code** (`TK6`): `method/standards/` — 7 chuẩn chung `common/`, `python.md`, `typescript.md`, `react.md`, `web.md`,
  bảng đối chiếu chuẩn ↔ skill; thẻ Implementer và Tech Reviewer trỏ tới, **không** nạp vào `AGENTS.md`.
- **Sáu agent mới** (`TK7`): `code-explorer`, `code-reviewer`, `test-analyzer`, `typescript-reviewer`, `react-reviewer` (chỉ
  đọc) và `build-fixer` (agent **duy nhất được sửa file**, T2); mỗi agent chạy thử trên fixture, `tests/fixtures/agents/`.
- **Bốn skill mới và phần bổ sung** (`TK8`, `TK9`): `react` (+ `references/testing.md`), `frontend` (+ `references/vite.md`),
  `e2e-testing` (+ `references/ai-regression.md`), `eval-harness`; `web-qa` (chỉ báo cáo, ranh giới và nhiệm vụ khám phá,
  cách đếm điểm, kiểm lại sau sửa), `code-review` (+ `references/duplicates.md`, sửa kèm test hồi quy là một lựa chọn),
  `closing-sprint` (phần ship, cổng CI của đúng commit, đề xuất mức phiên bản), `token-economy` mục 7 (truy xuất lặp);
  thẻ QA mục 9 (đo và ghi coverage); thẻ chuyên đề frontend mục 9 (a11y WCAG 2.2 AA).
- **Viết lại phòng sạch** (`TK10`): `bug-triage`, `adr`, `database-migrations/references/rehearsal.md`,
  `closing-sprint/references/release-notes.md` và `preflight.md`, bảng phủ `FR` → `VR` của thẻ QA, bốn ô "Bắt gì" của
  `scripts/README.md`: bản cũ gỡ khỏi cây trước, người viết mới chỉ nhận danh sách ý dạng cụm danh từ, để lại nhật ký đường
  đã đọc; 8-gram so với cả gốc private lẫn bản trước đó bằng 0 trên phần viết lại, sau khi loại stoplist cụm chung. Nguồn
  ghi dạng `concept:`; `THIRD_PARTY.md` mục 3 trống.
- **Đính chính (2026-10-04):** mục `0.2.0-dev` bên dưới ghi 7 đích đó "chưa đạt quy trình phòng sạch, phải viết lại thật
  sự trước khi công khai" — đúng tại thời điểm đó; từ `0.3.0-dev` câu này không còn đúng, 7 đích đã viết lại phòng sạch ở
  `TK10` và không còn file nào chờ viết lại. Mục `0.2.0-dev` giữ nguyên vì changelog chỉ thêm.
- **Nội dung thêm cho skill tham chiếu** (`TK11`): `github-ops`, `database-migrations`, `error-handling`, `fastapi`, `python`,
  `worktrees`, `deployment`, `postgres` thêm phần còn thiếu, mỗi skill chạy lại truy xuất bộ câu cũ.
- **Máy kiểm** (`TK12`): `tests/test_skill_tests.py` bỏ miễn theo ngày — **mọi** file thử phải có `skill_sha` và `tier`
  (ca đột biến với file ngày 2026-10-01 và 2025-01-01); `result` và `model` theo danh sách trắng; phép kiểm 8-gram nhận mọi
  cách viết, buộc điều kiện "loại stoplist"; luật `check` về nhãn mức kiểu nguồn; fixture `security-audit` đổi sang giá trị giả không khớp mẫu khoá thật; `writing-skills` thống nhất
  một quy ước "sửa lưới" và mục nạp bản worktree.
- **Thử truy xuất và định tuyến** (`TK13`): 13 skill tham chiếu (`react`, `frontend`, `e2e-testing`, `adr`, `api-design`,
  `postgres`, `github-ops`, `database-migrations`, `error-handling`, `fastapi`, `python`, `worktrees`, `deployment`) thử truy
  xuất bằng bộ câu mới do QA độc lập soạn, kỳ vọng ghi trước khi đọc skill, hai lượt: lượt 1 thấy 12/13 skill dưới ngưỡng (chỉ
  `adr` đạt; không câu nào Không đạt — skill thiếu nội dung, agent không bịa), `references/` được bổ sung có nguồn rồi chạy lại
  bộ câu mới ở lượt 2, kết quả vẫn 12/13 skill dưới ngưỡng (chỉ `adr` đạt) — để lại sang sprint sau, đổi cách đo trước khi vá
  tiếp; định tuyến 21 câu (12 câu ranh giới, đủ 5 cặp dễ nhầm) đối chiếu danh mục 49 mục; `n = 3` cho 5 skill
  (`writing-skills`, `closing-sprint`, `bug-triage`, `security-audit`, `web-qa`).
- **Quy tắc số phiên bản** (`TK15`): `method/conventions.md` mục 4.1 (MAJOR · MINOR · PATCH, bốn điều đi kèm); agent đề xuất
  mức tăng kèm lý do ở Cổng 2, người dùng quyết.
- **Dấu vết và tài liệu** (`TK14`): `UPSTREAM.md` — khối Đợt 2 thành khối chốt có bảng thành phần đã distill, bảng nguồn theo
  skill/agent và thành phần ngoài skill, mục "Đợt 3 — dự kiến"; `NOTICE` (superpowers-lab thành nguồn đã dùng),
  `THIRD_PARTY.md` mục 1; số đếm **32 skill, 13 agent** (agent chỉ đọc, riêng `build-fixer` được sửa) ở `README.md`,
  `README.vi.md`, `GUIDE.md`, `agents/README.md`, `skills/README.md`, `hosts/claude/README.md` và mô tả 3 manifest; dòng trỏ
  ở `method/README.md`, `roles/README.md`.
- **Hai vòng sửa sau review tổng thể** (`fix-1`, `fix-2`): `dual-review` nối vào luồng chính (`process.md`);
  ngoại lệ bảo mật (phát hiện tin cậy 5–6) vào danh sách chính "cần kiểm" ở cổng
  review và ở agent; `closing-sprint` so mốc với HEAD sau Cổng 2 là `sha7` của menu, tách nhãn CI không có / chưa chạy; tự
  kiểm chỉ hợp lệ ở cỡ rất nhỏ — cỡ nhỏ trở lên `qa` trùng nhãn người làm vẫn là Phải sửa dù có khai (`severity.md`,
  `roles/README.md`, `evidence.md`, `templates/README.md`), và chữ về `check` nói đúng khả năng thật (bắt khi không khai, hoặc
  khai mà `verdict: pass`); `check` không in traceback khi `.agile.json` sai hình; `description` của `closing-sprint` và
  `database-migrations` viết lại phòng sạch (đo 8-gram 0 hai mốc, sau khi loại stoplist cụm chung); `adr` điểm 3 chỉ cho ADR
  lúc PLAN, `preflight.md` ô lớn × `high` thêm reviewer kỹ thuật thứ hai; `docs-sync` chỉ sửa thân PR sau khi người dùng
  chọn push + PR.
- Phiên bản các manifest (`.claude-plugin`, `.codex-plugin`, `marketplace.json`) lên `0.3.0-dev`.

## 0.2.0-dev

Chưa phát hành. SPR-02 — làm cứng Đợt 1 (phần nội dung mới của Đợt 2 chưa làm, xem `UPSTREAM.md` mục "Đợt 2 —
dự kiến").

- Mốc Đợt 2: khối "Đợt 2 — chốt SHA 2026-10-03" và một dòng nhật ký kiểm cho 20 nguồn repo ở `UPSTREAM.md`;
  `ccusage` đổi tên chủ thành `ccusage/ccusage` (`UPSTREAM_OWNERS` giữ cả `ryoppippi`). Bảng nguồn theo
  skill/agent ghi đúng `ef648e01` cho 7 mục đã viết lại sâu, `postgres` thêm nguồn thứ hai
  `agents/database-reviewer.md`; `docs/updating-from-upstream.md` mục 4 nói rõ `base_sha` giữ nguyên khi đổi
  `source_sha`.
- Viết lại sâu 9 mục "gọn" của Đợt 1 có nguồn công khai, đối chiếu ECC `ef648e01` (và Superpowers `8ca22dba`
  cho `diagnosing.md`): `deployment` (+ `references/docker.md`), `fastapi`, `postgres` (+
  `references/diagnostics.md`), bốn agent `fastapi-reviewer`, `database-reviewer`, `comment-analyzer`,
  `rag-pipeline-reviewer`, và `writing-skills/references/diagnosing.md`.
- Viết lại 7 đích từ danh sách ý lấy từ nguồn private, có mang một số câu chữ nguồn; 8-gram bằng 0 sau khi loại stoplist 45 cụm chung (trước khi loại: còn cụm trùng ở 5/7 đích); chưa đạt quy trình phòng sạch, phải viết lại thật sự trước khi công khai (`CO2`, `RQ-021` ở hồ sơ riêng của chủ repo):
  `bug-triage`, `adr`,
  `database-migrations/references/rehearsal.md`, `closing-sprint/references/release-notes.md` và
  `preflight.md`, bảng phủ `FR` → `VR` của thẻ QA, bốn luật truy vết trong `scripts/README.md`. Cờ
  `rewrite_before_public: true` không còn ở skill hay agent nào.
- Thử áp lực nền (RED rồi GREEN) cho `intake`, `shaping-spec`, `writing-plan`, `running-sprint`,
  `closing-sprint`, `bug-triage`, và cho `security-audit`, `web-qa`; thử truy xuất cho 10 skill tham chiếu
  (`adr`, `api-design`, `database-migrations`, `deployment`, `error-handling`, `fastapi`, `github-ops`,
  `postgres`, `python`, `worktrees`); thử định tuyến 14/14. Cả 28 skill giờ có tệp thử đã chạy
  (`skills/README.md` mục 4).
- `tests/test_skill_tests.py`: máy kiểm tệp thử — skill kỷ luật có `pressure.md`, skill tham chiếu có
  `retrieval.md`, `result`/`model`/`date` hợp lệ, `skill_sha` khớp băm cây skill trừ `tests/` (skill đổi sau
  khi thử thì đỏ; `git` có mà lỗi thì đỏ, chỉ thiếu lệnh `git` mới skip); có ca đột biến cho trạng thái chưa chạy
  (kể cả giá trị mở đầu bằng dấu câu như `(pending)`), `date`, thiếu `skill_sha`/`tier`, và ca repo git tạm cho
  phép băm cùng cho kiểm thiếu tệp thử theo `metadata.kind`.
- Phiên bản các manifest (`.claude-plugin`, `.codex-plugin`, `marketplace.json`) lên `0.2.0-dev`. Số đếm không
  đổi: 28 skill, 7 agent.

## 0.1.0-dev

Chưa phát hành.

- Khung repo: cây thư mục, luật lõi dạng khung, manifest khung cho Claude và Codex, con trỏ cho
  Antigravity, hợp đồng hai điểm cắm `AGENT_AGILE_TIERS` và `AGENT_AGILE_DENYLIST`, test đồng bộ version.
- Distill Đợt 1 (SHA chốt 2026-10-01): 28 skill phẳng trong `skills/` chia 5 nhóm — Quy trình (6),
  Kỹ thuật (12, trong đó 10 skill tham chiếu `metadata.kind: reference`), Kiểm định (6), Giao tiếp & tối
  ưu (3), Meta (1) — và 7 agent reviewer chỉ-đọc trong `agents/`. Nguồn: Superpowers, ECC, gstack (MIT),
  bộ skill quy trình private (gốc không giấy phép, gắn `rewrite_before_public: true` ở 4 skill), nguồn khái
  niệm chỉ lấy ý. Mỗi skill/agent ghi `source`, `source_sha`, `license` (và `base_sha` khi có) trong
  frontmatter.
- Dấu vết: `UPSTREAM.md` (bảng nguồn theo từng skill/agent), `NOTICE` (bản quyền MIT của Superpowers, ECC,
  gstack, Supabase Agent Skills), `THIRD_PARTY.md` (nguồn chỉ lấy ý, danh sách file phải viết lại trước khi
  công khai), `docs/MIGRATION.md` (tên cũ → tên mới).
- Mẫu: SPEC thêm mục "Đổi hợp đồng / giao diện" và dấu delta `(sửa …)`/`(bỏ …)`; spec sống ghi cách gộp
  delta Thêm / Sửa / Bỏ ở Bước 5; REPORT mục Review & Retro đọc lại `Phán quyết:` và rà nợ `CO`. Thẻ QA thêm
  bảng phủ `FR` → `VR` theo tầng test thấp nhất. `pytest` gom thêm test trong `skills/`.
- Thử áp lực bắt buộc cho skill kỷ luật/quy trình (`tests/pressure.md`); skill tham chiếu miễn ở Đợt 1,
  Đợt 2 thêm `tests/retrieval.md`.
- Vòng sửa 1 sau kiểm định Đợt 1: nợ `CO` chuyển thành dòng `RQ-` trong REQUESTS ngay khi ghi REPORT (retro
  chỉ đọc khối "Đang mở"); luật `leak-denylist` khớp nguyên từ cho mục chữ, chuỗi con cho mục đường dẫn;
  `tests/test_provenance.py` kiểm nguồn gốc mọi skill/agent với `UPSTREAM.md`, `THIRD_PARTY.md`.
- TK6.5 — vướng mắc của sprint thử đầu tiên: `init --title-file` và cảnh báo tiêu đề mất dấu, cảnh báo sớm khi
  thiếu `AGENT_AGILE_TIERS`, dòng sprint thật đầu tiên xoá comment ví dụ của SPRINTS; `index` gặp sổ không UTF-8
  thoát 2 có thông báo; `check` che code span ngắt dòng (thận trọng), gợi ý khi mã bị bắt kề dấu huyền, nhận
  `.agile.json` truyền thẳng, luật Ghi chú `id-list-lead`; thiếu bảng tier thì dùng chỉ định tier → model trong
  chat, chưa có thì hỏi ở Cổng 1; mẫu REPORT có tiểu mục "Review PLAN trước Cổng 1", mẫu SPEC nhắc số đo trước
  sprint; `writing-plan` có luật cho `TK` tác động ngoài worktree; câu dẫn "tài liệu + nghĩa in đậm" trước mọi
  danh sách / bảng mã (`id-convention`, `response-style`, `AGENTS.md`, mẫu, dự án mẫu).
- TK8.1–TK8.2 — đóng gói ba harness: manifest thật (tác giả trung tính, mô tả đủ 28 skill / 7 agent; Claude
  để mặc định dò `skills/` và `agents/`), `hosts/README.md` (bảng harness + năm điểm cắm của lớp riêng + hợp
  đồng nơi lưu bài học), bốn `hosts/*/README.md` viết thật, `INSTALL.md` cho agent đọc kèm prompt dán Việt/Anh,
  `GUIDE.md` (sprint đầu tiên cho người mới), `README.md` + `README.vi.md` có mục cài và ghi nhận nguồn,
  `docs/standardization.md` (áp khuôn 13 mục: 10 áp dụng, 3 điều chỉnh).
- Ba mục khuôn còn lại: `tests/test_install_docs.py` (prompt VI/EN ≤12 dòng, đủ bước và bốn `hosts/`, link nội
  bộ không gãy — `A5`), `docs/troubleshooting.md` sáu triệu chứng, được README/GUIDE/INSTALL trỏ tới (`A10`),
  `.github/workflows/verify.yml` — 3 hệ điều hành × Python 3.9/3.13, mọi nhánh, `contents: read`, action ghim
  SHA (`A11`).
- Vòng sửa 1 sau kiểm định TK8: lệnh Windows dùng `"$HOME\agent-agile-team"` (PowerShell 5.1 không mở `~` cho
  chương trình ngoài) ở INSTALL, README, GUIDE, `hosts/claude`, kèm triệu chứng thứ bảy ở `docs/troubleshooting.md`
  và test bắt `~` trong khối PowerShell; miễn trừ chống rò thành danh sách tường minh `LEAK_EXEMPTIONS` trong
  `check.py` (mỗi mục một kiểu, một lý do): `THIRD_PARTY.md` chỉ miễn dòng ghi công, `UPSTREAM.md` chỉ che
  `owner/repo` và SHA, `docs/MIGRATION.md` chỉ che mã skill cũ `bộ:tên`; nguồn private gọi trung tính
  ("bộ skill quy trình private", `private-process-skills` trong frontmatter); `pytest==8.4.2` ghim trong CI.
- Tác giả và địa chỉ repo: ba manifest ghi `author` (tên, email, trang), `homepage`, `repository`; README
  EN/VI có mục Author/Tác giả; dòng Copyright của `NOTICE`, `LICENSE` ghi tên tác giả (giấy phép vẫn "All
  rights reserved — private"); URL repo thật thay `OWNER/agent-agile-team` ở INSTALL, README, `hosts/`. Chống rò
  thêm nhóm miễn trừ có chủ đích `author-attribution` (kiểu `author-field`, `author-section`, `author-url`) —
  tên tác giả ở chỗ khác vẫn bị chặn.
- Theo dõi nguồn gốc: `UPSTREAM.md` thêm "Sổ theo dõi nguồn gốc" (21 repo + 7 tài liệu web: vai trò, nơi nhận
  nội dung, mốc đã distill, lần kiểm gần nhất, khi nào kiểm — gồm cả nguồn đã loại và điều kiện xét lại),
  "Nhật ký kiểm bản mới" và "Đợt 2 — dự kiến" (thành phần đã chọn, đích, mức lấy/xét); quy trình
  `docs/updating-from-upstream.md` (khi nào kiểm, so HEAD với mốc, quyết định lấy/bỏ qua/hoãn, distill như một
  sprint, mở rộng phải ghi sổ trước), con trỏ từ `AGENTS.md`, README, `docs/README.md`. `UPSTREAM_OWNERS` thêm
  `rtk-ai`, `oraios`, `mksglu`, `microsoft`; `tests/test_provenance.py` đỏ khi Sổ theo dõi thiếu nguồn nhắc ở
  `UPSTREAM.md` hay frontmatter, hoặc lệch với `UPSTREAM_OWNERS`.
- CI lượt đầu đỏ ở cả ba job Python 3.9: test ghi file bằng `Path.write_text(newline=...)` — tham số chỉ có từ
  Python 3.10. Test đổi sang tiện ích `write_lf` trong `tests/conftest.py` (ghi byte UTF-8, giữ LF);
  `tests/test_common.py` đỏ khi mã trong `scripts/`, `tests/`, `skills/` vượt mức sàn Python của
  `verify.yml` (cú pháp, hoặc `write_text`/`read_text` có `newline=`).
- `A11` chạy thật: run `37077757196` (commit `2a09e34`) xanh 6/6 job (Ubuntu, Windows, macOS × Python 3.9/3.13);
  `docs/standardization.md` ghi `A11` xong. Việc để lại "chạy lần đầu `verify.yml`" bên dưới đã xong.
- `hosts/claude/README.md`: trên Claude, skill dựng sẵn tên trần `code-review` / `security-review` thắng tên trần,
  nên khi skill của repo nói "skill `code-review`" thì gọi `agent-agile-team:code-review` (tương tự
  `security-review`); skill và luật lõi giữ tên trần để không phụ thuộc harness.

**Việc để lại (Đợt 2):**

- Chạy thử áp lực 6 skill quy trình đã có kịch bản: `intake`, `shaping-spec`, `writing-plan`,
  `running-sprint`, `closing-sprint`, `bug-triage`.
- Viết và chạy thử áp lực `security-audit`, `web-qa` (ngoại lệ chỉ báo cáo ở Đợt 1 — `skills/README.md`
  mục 2).
- `tests/retrieval.md` cho 10 skill tham chiếu.
- Chạy lần đầu `.github/workflows/verify.yml` khi đẩy lên GitHub private (`A11` — đã viết, chưa chạy).
