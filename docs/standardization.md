# Áp khuôn chuẩn hóa repo 13 mục

> **Kết luận:** 13 mục của khuôn chuẩn hóa repo agent (`A1`–`A13`): **10 áp dụng**, **3 điều chỉnh** (`A1`,
> `A4`, `A10`), **0 không áp dụng hẳn**; riêng `A12` (luồng phát hành) chỉ có hiệu lực khi repo công khai.
> Không còn việc treo trong repo; `A11` (CI) **đã chạy xanh** trên GitHub private (run `37077757196`, commit
> `2a09e34`, 6/6 job).

Khuôn rút từ các repo agent đã phát hành theo cùng một chuẩn: mỗi mục có một cách kiểm bằng máy. Repo này
là **repo phương pháp** — không có engine, không có dữ liệu chạy — nên vài mục phải đổi nghĩa; bảng dưới ghi
rõ đổi thế nào và vì sao.

## 1. Bảng áp dụng

Bảng có 13 **mục khuôn** (mã `A1`–`A13`, mã của khuôn bên ngoài nên luôn để trong dấu code):

| Mục | Khuôn yêu cầu | Phân loại | Ở repo này | Kiểm bằng | Hiện trạng |
|---|---|---|---|---|---|
| `A1` (chạy từ repo, dữ liệu ở trạm) | Engine/skill chạy từ repo; dữ liệu ở trạm, mặc định `<repo>/workspace/` | **Điều chỉnh** | Repo không có dữ liệu chạy. "Dữ liệu" là sổ gốc và tài liệu sprint — chúng nằm trong **dự án áp dụng**, do `init` tạo theo `.agile.json` của dự án đó. Skill và script chạy thẳng từ bản clone (plugin, liên kết thư mục), không chép sang chỗ khác | `.gitignore` vẫn chặn `/workspace/` làm lưới an toàn; `init` từ chối ghi ngoài gốc dự án (`scripts/README.md`, mã thoát 2) | Xong |
| `A2` (một nguồn luật + con trỏ) | `AGENTS.md` canonical; `CLAUDE.md`/`GEMINI.md` là con trỏ; `hosts/{claude,codex,claude-desktop,antigravity}/README.md` | Áp dụng | `CLAUDE.md` = một dòng `@AGENTS.md` (import thật); `GEMINI.md` là con trỏ văn xuôi để khỏi nạp đúp; bốn `hosts/*/README.md` + mục lục `hosts/README.md` | File tồn tại; `check.py --self` đo ngân sách `AGENTS.md` | Xong |
| `A3` (manifest khớp version) | `.claude-plugin/{plugin,marketplace}.json` + `.codex-plugin/plugin.json`, một version | Áp dụng | Ba manifest cùng `0.2.0-dev`; mục đầu `CHANGELOG.md` trùng version | `tests/test_version_sync.py` | Xong |
| `A4` (vòng đời cài) | `install` · `doctor` (PASS/WARN/FAIL/NOT_CHECKED) · `update` · `uninstall` chỉ gỡ phần sở hữu | **Điều chỉnh** | Không có script vòng đời riêng: cài, cập nhật, gỡ đi theo cơ chế plugin của từng harness (`INSTALL.md` mục 4 và 7, `hosts/`). `check.py --self` đóng vai **doctor**: Đạt / Không đạt, phát hiện Nên sửa và Ghi chú là mức cảnh báo, `NOT_CONFIGURED` là **Chưa chạy** — không bao giờ tô thành Đạt | `tests/test_check_self.py` (gồm ca `NOT_CONFIGURED`) | Xong |
| `A5` (cài kiểu agent-first) | `INSTALL.md` cho agent đọc + prompt dán VI/EN ≤12 dòng | Áp dụng | `INSTALL.md` mục 0–7, luật an toàn, hai prompt 8–9 dòng | `tests/test_install_docs.py`: đúng hai prompt VI/EN ≤12 dòng, đủ mục 0–7, trỏ đủ bốn `hosts/`, hai OS, hai biến; `CLAUDE.md`/`GEMINI.md` chỉ là con trỏ | Xong |
| `A6` (mẫu + kết quả kỳ vọng) | `samples/` + kết quả cố định | Áp dụng | `samples/order-desk/`: bốn sprint (một cỡ vừa đủ bốn tài liệu, một cỡ nhỏ một file bốn phần, hai cỡ rất nhỏ một file — dạng hai phần và dạng bốn phần cũ), ba sổ gốc, spec sống | `tests/test_samples.py` (`check` thoát 0, `index --check` thoát 0, chèn mã trần thì đỏ) | Xong |
| `A7` (không dấu nội bộ) | 0 dấu nội bộ; danh sách cấm ngoài repo | Áp dụng | Luật `leak-denylist` của `check.py --self` đọc file mà `AGENT_AGILE_DENYLIST` trỏ tới; mục chữ khớp nguyên từ, mục đường dẫn khớp chuỗi con; danh sách nằm ở lớp riêng, không bao giờ trong repo. **Ngoại lệ có chủ đích `author-attribution`** (chủ sản phẩm quyết 02/10/2026): repo ghi công tác giả — tên, trang, URL repo — chỉ ở trường `author`/`owner`/`repository`/`homepage` của 3 manifest, mục `## Author`/`## Tác giả` của 2 README, dòng Copyright của `NOTICE`/`LICENSE`, và đúng hai URL của tác giả ở mọi file; danh sách miễn trừ ở `scripts/README.md` | `tests/test_check_self.py` (đột biến: chèn từ cấm thì đỏ; tên tác giả trong văn xuôi skill, ngoài mục Author, `owner/repo` viết tắt, email ngoài manifest vẫn Chặn) + chạy `--self` với danh sách thật | Xong |
| `A8` (`.gitignore` neo gốc) | `/workspace/`, `/.venv/`, `.env*`, `docs/plans/` neo gốc | Áp dụng | `/workspace/`, `/.venv/`, `/docs/plans/`, `/.tmp/` neo gốc; `.env*`, `*.pem`, `*.key` cố ý **không** neo để chặn ở mọi tầng | `git check-ignore` | Xong |
| `A9` (ngôn ngữ + nguồn gốc) | Thân skill tiếng Việt, frontmatter tiếng Anh; upstream giữ hash + NOTICE | Áp dụng | Mọi skill/agent ghi `source`, `source_sha`, `license`, `rewrite_before_public`; `UPSTREAM.md` chốt SHA theo đợt; `NOTICE`, `THIRD_PARTY.md` | `tests/test_provenance.py` | Xong |
| `A10` (bộ tài liệu) | README (+ bản Việt), START-HERE, GUIDE, troubleshooting, `hosts/`, CHANGELOG; trang web `/install/` | **Điều chỉnh** | Có `README.md` + `README.vi.md`, `GUIDE.md`, `hosts/`, `CHANGELOG.md`, `docs/troubleshooting.md` (sáu triệu chứng → nguyên nhân → cách xử lý, README/GUIDE/INSTALL trỏ tới). **START-HERE gộp vào `GUIDE.md`**: bài thực hành đầu tiên của repo phương pháp chính là sprint đầu tiên, tách hai file là hai bản trôi khỏi nhau. **Trang web `/install/` không làm** khi còn private — không có trang công khai để đặt | `tests/test_install_docs.py`: mọi link tương đối trong tài liệu người dùng trỏ tới file có thật (có ca đột biến), README/GUIDE/INSTALL trỏ trang lỗi | Xong — thêm triệu chứng mới khi cài thử ba harness có số liệu thật |
| `A11` (CI) | CI ≥2 hệ điều hành, ma trận Python, mọi nhánh, quyền tối thiểu, action ghim SHA | Áp dụng | `.github/workflows/verify.yml`: Ubuntu + Windows + macOS × Python 3.9 (sàn hỗ trợ) và 3.13, mọi nhánh + PR, `contents: read`, `actions/checkout` và `actions/setup-python` ghim SHA commit, `pytest==8.4.2` ghim (bản cuối hỗ trợ 3.9; bộ test chạy xanh với nó: 367 passed, 1 skipped); chạy `pytest`, `check.py --self`, `check.py samples templates` | CI xanh | **Xong** — lượt đầu (run `37048960920`) đỏ ở ba job Python 3.9 (`write_text(newline=)` chỉ có từ 3.10), sửa ở `2a09e34` kèm test chặn mã vượt mức sàn; run `37077757196` xanh 6/6 job. Đã biết và chấp nhận: ảnh macOS arm64 của GitHub chỉ có đúng **Python 3.9.13** cho dòng 3.9 (số đo do reviewer `TK8` cung cấp), nên ô macOS × 3.9 chạy 3.9.13 — đủ cho sàn "3.9+" |
| `A12` (luồng phát hành) | PR → CI → chủ sản phẩm gật → tag + Release → kiểm bản phát hành → ghi sổ | Áp dụng khi công khai | Khi còn private: version đứng ở `0.2.0-dev`, không tag. Không còn file nào mang cờ `rewrite_before_public: true` (SPR-02 đã gỡ hết; bảng `THIRD_PARTY.md` mục 3 trống), nên không còn bước viết lại trước khi công khai | — | Chưa tới |
| `A13` (sổ tiến độ) | Sổ tiến độ có PROGRESS tick bằng chứng | Áp dụng | Sổ tiến độ của chính dự án dựng repo nằm ở **lớp riêng, ngoài repo** (`/docs/plans/` bị ignore), theo đúng mẫu PROGRESS của repo: mỗi việc một dòng, có bằng chứng | Đọc sổ | Xong |

## 2. Vì sao ba mục phải điều chỉnh

- **`A1`** giả định repo là công cụ sinh ra dữ liệu (ảnh, giọng, báo cáo). Repo này sinh ra **tài liệu của
  dự án khác**; chỗ của tài liệu đó là repo dự án, có git riêng và người duyệt riêng. Thêm `workspace/` vào
  đây chỉ đẻ ra một nơi thứ hai để tài liệu sprint lạc vào.
- **`A4`** giả định có engine để cài. Ở đây thứ cần cài là skill và luật — harness đã có cơ chế plugin cho
  việc đó. Một script `install` riêng sẽ phải sửa cấu hình harness thay người dùng, đúng điều luật lõi cấm.
  Vai trò "doctor" thì giữ: `check.py --self` báo trạng thái, không bao giờ báo Đạt cho phần chưa chạy.
- **`A10`** giả định repo công khai có trang web và người dùng phổ thông. Khi còn private, người đọc là người
  được mời; GUIDE gộp START-HERE để có một đường đọc duy nhất.

## 3. Cách cập nhật bảng này

Khi khuôn thêm hoặc đổi mục, hoặc khi một mục treo xong: sửa đúng dòng đó (cột Hiện trạng ghi việc đã làm và
bằng chứng), cập nhật câu kết luận ở đầu file, thêm một dòng vào `CHANGELOG.md`.
