# Changelog

Mục mới nhất đứng đầu. Tiêu đề mỗi mục là đúng chuỗi version trong các manifest (test đồng bộ
version kiểm điều này).

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

**Việc để lại (Đợt 2):**

- Chạy thử áp lực 6 skill quy trình đã có kịch bản: `intake`, `shaping-spec`, `writing-plan`,
  `running-sprint`, `closing-sprint`, `bug-triage`.
- Viết và chạy thử áp lực `security-audit`, `web-qa` (ngoại lệ chỉ báo cáo ở Đợt 1 — `skills/README.md`
  mục 2).
- `tests/retrieval.md` cho 10 skill tham chiếu.
- Chạy lần đầu `.github/workflows/verify.yml` khi đẩy lên GitHub private (`A11` — đã viết, chưa chạy).
