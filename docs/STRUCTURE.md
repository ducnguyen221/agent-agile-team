# Cấu trúc chuẩn của repo agent-agile-team

> **Kết luận:** gốc repo chỉ chứa những gì bảng ở mục 1 liệt kê; mỗi thư mục có một vai, mười hai đường dẫn ở mục 2 là **cứng**
> (công cụ và tài liệu trỏ vào nên không dời, không đổi tên nếu chưa đổi hợp đồng), và file chưa theo dõi mà không bị ignore ở
> gốc là **rác** — `python scripts/check.py --self` báo mức Phải sửa. Khung cho repo xưởng mới: `templates/repo-skeleton/`.

## 1. Gốc repo

| Mục | Vai |
|---|---|
| `AGENTS.md` | luật lõi — agent đọc mỗi phiên (≤120 dòng, ≤10 240 byte) |
| `GEMINI.md` | con trỏ tới `AGENTS.md` cho Antigravity (không chứa luật riêng) |
| `README.md`, `README.vi.md` | cửa vào: giới thiệu và cài (Anh · Việt) |
| `CHANGELOG.md` | mục mới nhất đứng đầu; mục đầu trùng version của manifest |
| `NOTICE`, `LICENSE`, `LICENSES/` | bản quyền và giấy phép (nguồn distill **không** ghi ở repo — nằm ở Workshop) |
| `REVIEW.md`, `ECOSYSTEM.md` | luật review của repo; vị trí của repo trong hệ sinh thái các repo cùng tác giả |
| `INSTALL.md`, `GUIDE.md` | **con trỏ ngắn** tới `docs/INSTALL.md`, `docs/GUIDE.md` (giữ để liên kết ngoài không gãy) |
| `pyproject.toml`, `.gitattributes`, `.gitignore`, `.mcp.json`, `.agile.json` | cấu hình công cụ; LF cho mọi file văn bản |
| `.claude-plugin/`, `.codex-plugin/`, `.github/` | manifest plugin, CI (`verify.yml`) |
| `.claude/` | **không theo dõi**: chỉ có cấu hình riêng của máy và worktree do app tạo (`.claude/worktrees/`), đã ignore |
| `method/`, `roles/`, `tiers/`, `templates/` | luật chơi, thẻ vai, bảng tier, khuôn hồ sơ |
| `skills/`, `agents/`, `hooks/`, `shims/` | 36 skill, 13 agent, hook của plugin, shim `git`/`gh` |
| `scripts/`, `tests/`, `evals/` | công cụ `init`/`check`/`index`, bộ pytest, bộ eval |
| `samples/`, `hosts/`, `docs/` | dự án mẫu, hướng dẫn theo harness, tài liệu người đọc |

## 2. Đường dẫn cứng (không dời, không đổi tên)

`skills/` · `hooks/hooks.json` · `scripts/` · `.claude-plugin/` · `.codex-plugin/` · `AGENTS.md` · `GEMINI.md` · `method/` · `roles/` ·
`tiers/` · `templates/` · `tests/`. Lý do: manifest, hook, test và tài liệu của harness trỏ thẳng vào đó; đổi một đường là đổi hợp
đồng, phải sửa cùng lượt mọi nơi trỏ tới và ghi vào CHANGELOG.

## 3. Rác ở gốc

- **Rác** = file hoặc thư mục ở gốc repo **không được theo dõi và không bị ignore** (đo bằng `git status --porcelain --ignored=no`).
- **Không phải rác:** cache đã ignore — `.venv/`, `.tmp/`, `.worktrees/`, `.claude/worktrees/`, `.coverage`, `.pytest_cache/`, `__pycache__/` — và file chưa theo dõi
  nằm dưới thư mục đã theo dõi.
- Máy canh: luật `root-junk` của `check.py --self` (mức Phải sửa); thêm vào `.gitignore` hoặc xoá.
- Thư mục tạm của một sprint là `.tmp/<SPR-NN>/`, dọn khi đóng sprint ở mọi nhánh của menu (skill `closing-sprint` mục 6);
  `.tmp/autopilot.json` là file dấu autopilot — **không xoá**.

## 4. Hai dự án mẫu order-desk — giữ cả hai

| Đường | Vai |
|---|---|
| `samples/order-desk/` | dự án mẫu cho người đọc (sprint đầu tiên và các sprint sau, kết quả kỳ vọng cố định); `check.py samples templates` chạy trên đây |
| `tests/fixtures/ledger/order-desk{,.md}` | fixture của test kho sổ tập trung — nội dung khác hoàn toàn, **không** gộp |

## 5. Hồ sơ kế hoạch và khung repo xưởng

- Hồ sơ sprint của repo này không nằm trong repo (`/docs/plans/` bị ignore); chúng ở Workshop (`workshop-records/agent-agile-team/`).
- Khung cho repo xưởng mới (cùng cấu trúc: `docs/`, `hosts/`, `scripts/` tuỳ chọn, ignore, `.gitattributes`, `NOTICE` tối thiểu):
  `templates/repo-skeleton/` — xem `README.md` trong đó.
