# hosts/ — cài và nạp theo từng harness

> **Kết luận:** luật lõi nằm ở một chỗ duy nhất — [`AGENTS.md`](../AGENTS.md) — và mỗi harness nạp nó theo
> cách riêng; skill nằm phẳng ở `skills/`. Môi trường dùng repo (gọi là **lớp riêng**) cắm vào lõi qua năm
> điểm cắm ở mục 2, không sửa file nào trong repo.

## 1. Chọn harness

| Bạn chạy trong | Luật lõi nạp bằng | Skill nạp bằng | Hướng dẫn |
|---|---|---|---|
| Claude Code (terminal, IDE, tab Code của ứng dụng Claude) | `CLAUDE.md` = một dòng `@AGENTS.md` (trong repo); dòng `@import` ở file luật cấp người dùng (mọi phiên) | plugin `.claude-plugin/` | [claude/README.md](claude/README.md) |
| Codex (CLI hoặc ứng dụng desktop) | tự đọc `AGENTS.md` theo chuỗi thư mục; ngoài repo: bản sinh ghép vào file luật cấp người dùng | plugin `.codex-plugin/` hoặc mở thẳng repo | [codex/README.md](codex/README.md) |
| Google Antigravity | tự đọc `AGENTS.md` + `GEMINI.md` của workspace; ngoài repo: bản sinh ghép vào file luật cấp người dùng | liên kết từng thư mục skill vào thư mục skill của Antigravity | [antigravity/README.md](antigravity/README.md) |
| Claude Desktop, tab chat | **chưa hỗ trợ** | — | [claude-desktop/README.md](claude-desktop/README.md) |

Cài cho người dùng: agent đọc [`INSTALL.md`](../INSTALL.md). Dùng quy trình lần đầu: [`GUIDE.md`](../GUIDE.md).

## 2. Năm điểm cắm của lớp riêng

Lõi không biết môi trường nào đang dùng nó. Mọi thứ riêng của một máy, một người hay một tổ chức — tên model,
từ cấm, nơi lưu bài học, cầu gọi hãng khác — nằm **ngoài repo** và cắm vào qua đúng các điểm dưới. Thiếu
điểm nào thì phần liên quan báo **Chưa chạy** hoặc hỏi người dùng; không đoán, không lấy giá trị mặc định.

| Điểm cắm | Dạng | Lõi đọc ở đâu | Thiếu thì |
|---|---|---|---|
| Nạp luật đầu phiên | dòng `@import` (Claude) hoặc bản sinh ghép `AGENTS.md` (Codex, Antigravity) trong file luật cấp người dùng | mỗi phiên | chỉ phiên mở trong thư mục repo thấy luật lõi |
| Bảng tier → model | biến `AGENT_AGILE_TIERS` = đường tuyệt đối tới file JSON | `init`, Analyst khi giao việc — hợp đồng ở [`tiers/README.md`](../tiers/README.md) mục 2 | dùng chỉ định tier → model trong chat; chưa có thì hỏi ở Cổng 1 |
| Danh sách từ cấm | biến `AGENT_AGILE_DENYLIST` = đường tuyệt đối tới file văn bản | `check.py --self` — hợp đồng ở [`tests/README.md`](../tests/README.md) | luật chống rò **Chưa chạy**, không phải Đạt |
| Nơi lưu bài học | khai báo trong file luật cấp người dùng của môi trường (mục 3) | Analyst ở Bước 6 (`method/process.md` mục 8, skill `closing-sprint`) | `LN` chỉ nằm trong REPORT; Analyst đề xuất nơi lưu ở Cổng 2 |
| Cầu gọi chéo hãng | lệnh hoặc công cụ do môi trường cung cấp, có hạn mức và sổ ghi | Analyst khi người dùng đã gật tư vấn gọi chéo (`tiers/README.md` mục 6) | ghi "cần người duyệt", làm phần còn lại |

Hai biến môi trường đặt ở **mức tài khoản người dùng** để mọi harness và terminal mới đều thấy; đặt xong phải
mở phiên mới. Tên biến cố ý không chứa tên môi trường nào.

## 3. Hợp đồng điểm cắm "nơi lưu bài học"

Lõi chỉ quy định bài học `LN` ghi trong REPORT, tự chấm trước khi lưu, ghi theo timeline, mỗi bài một nguồn
(sprint nào, bằng chứng nào). Nơi lưu bền do lớp riêng khai báo, gồm hai kho:

| Kho | Chứa gì | Phép thử vào kho |
|---|---|---|
| **Bộ nhớ theo dự án** (bộ nhớ của harness gắn với thư mục dự án) | nguyên tắc làm việc, cạm bẫy, quyết định còn giá trị cho **dự án đó** | lần sau làm việc ở dự án này, agent cần biết điều này trước khi bắt đầu |
| **Kho tri thức cá nhân** (ghi chú dài hạn của người dùng) | bài học có cái giá cụ thể theo timeline; bài học đúng với mọi dự án tách thành ghi chú riêng | bỏ tên dự án đi mà bài học vẫn đúng → ghi chú dùng chung; còn gắn sự việc → nhật ký bài học |

Khai báo của lớp riêng phải nói: đường (hoặc biến) của từng kho, luật dedup và gộp của kho đó, và ai được
ghi. Agent **không** tự tạo kho mới; bài học đánh dấu quan trọng chỉ được **đề xuất** nâng thành luật,
skill hay bước quy trình.
