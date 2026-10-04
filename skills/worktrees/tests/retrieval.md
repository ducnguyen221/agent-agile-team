---
skill: worktrees
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: fbcbc7509618b5c69a8f372a7125c106fb3719db
date: 2026-10-04
result: "strict 3/7 (+4 partial, 0 fail) — below threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: "ad7571c8749be685c (câu ranh giới soạn lại: aa696805706ace3cf, vì bản đầu trùng câu cũ)"
  answers: a0d95341d7037b278
---

Đã đọc: `<gốc worktree>/skills/worktrees/SKILL.md` (không có `references/`)

# Thử truy xuất - worktrees

> **Kết luận:** strict 3/7 (+4 partial, 0 fail), dưới ngưỡng. Bộ câu MỚI (lượt độc lập `TK13`, người soạn không đọc skill) phủ các góc khác của `description`; 2 trong 6 câu tình huống Đạt hẳn, các câu còn lại trỏ đúng nơi nhưng thiếu nội dung (mục "Thiếu nội dung" bên dưới). Câu ranh giới Đạt. Bộ câu cũ giữ ở mục lịch sử.

Câu hỏi do người soạn mới (id ở `agent_ids`) viết từ `description` và danh sách câu cũ, không đọc skill. Cột "Mục kỳ vọng" và điều kiện Đạt ghi vào file nháp
`.tmp/worktrees-expected.md` lúc 2026-10-04 10:45:54 +07:00, **trước khi** giao chủ thể (thứ tự: ghi kỳ vọng -> giao chủ thể -> chấm); file nháp chép giữ mtime vào
`expected/worktrees-expected.md`. Bài trả lời trọn của chủ thể (id ở `agent_ids`, 4 lượt công cụ) và bảng chấm ở `evidence/TK13/worktrees-retrieval.md`
trong hồ sơ sprint `SPR-04` của lớp riêng; dòng "Đã đọc" chép từ bài trả lời, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>`
vì repo chặn tên người dùng. Chủ thể được dặn nói thẳng khi skill không có phần câu hỏi cần, không dùng kiến thức ngoài.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Team mình chạy 6 implementer song song trên một monorepo, mỗi người một TK khác nhau, và hôm qua hai người suýt ghi đè lên cùng một file cấu hình dùng chung vì chung thư mục. Mình muốn mỗi implementer có chỗ làm riêng nhưng vẫn gộp lại được vào một nhánh tích hợp sau đó. Nên chia nhánh và thư mục thế nào, và khi hai worktree cùng muốn sửa một file thì xử lý ra sao? | `SKILL.md` › 2. Bước 1 — tạo không gian tách biệt (đoạn Nhiều agent song song: mỗi agent một worktree và một nhánh, phạm vi file không giao nhau, đường dẫn tuyệt đối; Tên nhánh) | `SKILL.md` › 2 (Nhiều agent song song, Tên nhánh), › 7 | Một phần (đủ chia worktree/nhánh; thiếu xung đột cùng file và gộp vào nhánh tích hợp) |
| 2 | Mình đang làm dở một tính năng trong worktree thì có bug production khẩn, cần vá ngay bản 2.3.1 từ tag cũ mà không đụng tới thay đổi chưa commit đang có. Mình đang định `git stash` rồi checkout tag. Có cách nào an toàn hơn, và cần lưu ý gì khi nhánh hotfix này bắt nguồn từ tag chứ không phải từ main? | `SKILL.md` › 5. Luật git trong worktree (không `git stash` trần, cất việc dở bằng commit tạm) + › 2 (`git worktree add … -b <nhánh>` ở thư mục riêng) | `SKILL.md` › 5, › 2, › 4 | Một phần (đủ luật không stash trần, commit tạm, worktree riêng; thiếu nhánh xuất phát từ tag) |
| 3 | Repo của mình khá nặng (khoảng 4 GB lịch sử, có submodule và vài file LFS), tạo thêm worktree thứ 3 thì thấy ổ đĩa tăng bất thường và submodule trong worktree mới trống. Mình cần làm gì để submodule và LFS hoạt động trong worktree phụ, và có cách nào giảm dung lượng không? | `SKILL.md` › 3. Bước 2 — dựng dự án (file không theo dõi không đi theo sang worktree) + › 1 (nhận diện submodule); khởi tạo submodule, LFS, giảm dung lượng không có | `SKILL.md` › 3, › 1, › 6 (gần nhất) | Một phần (trỏ mục gần nhất và nói thẳng skill thiếu) |
| 4 | Agent đang chạy trong worktree thì mình lỡ `git checkout main` ở thư mục gốc, và Git báo "branch is already checked out at ..." khi mình thử checkout nhánh feature ở chỗ khác. Lỗi này nghĩa là gì, mình có nên dùng `--force` hay `git worktree add -f` để vượt qua không, và đúng ra phải làm gì? | `SKILL.md` › 7. Tra nhanh (dòng lỗi "branch đã được checkout ở worktree khác": `git worktree list`, chuyển nhánh hoặc gỡ worktree của mình, không `--force`) + › 2 (git từ chối checkout cùng nhánh ở hai worktree) | `SKILL.md` › 7. Tra nhanh; › 2; › 6 | Đạt (phần phụ thiếu: lệnh riêng `git worktree add -f`) |
| 5 | Mình muốn xem thử một PR của đồng nghiệp (nhánh `feat/export-csv`, khoảng 600 dòng diff) chạy thật trên máy mà không làm bẩn thư mục đang làm dở, và cũng không muốn để nó lại nhánh local thừa. Kiểm tra nhanh rồi bỏ đi thì làm cách nào gọn nhất, kể cả dùng chế độ detached? | `SKILL.md` › 2. Bước 1 (`git worktree add`) + › 6. Dọn khi xong (`git worktree remove`, `prune`); chế độ `--detach` và checkout nhánh PR của người khác không có | `SKILL.md` › 2, › 6, › 7 | Một phần (có tạo và gỡ worktree; thiếu chế độ detached và xem nhánh người khác) |
| 6 | Sprint xong, mình có 5 nhánh task đã review. Mình định gộp thẳng vào main rồi xoá hết worktree, nhưng chưa rõ nên merge, tạo PR hay giữ lại để làm tiếp. Khi kết thúc công việc trong một worktree thì có những lựa chọn xử lý nào, mỗi lựa chọn dọn dẹp ra sao, và cái nào không bao giờ được tự làm? | `SKILL.md` › 6. Dọn khi xong (dọn theo nguồn gốc, điều kiện trước khi xoá, `git branch -d` không `-D`) + › 5 (push, PR, gộp chỉ sau Cổng 2 và khi người dùng gật; menu kết thúc ở `closing-sprint`) | `SKILL.md` › 6, › 5, › 7 (menu ở `closing-sprint`) | Đạt (menu merge/PR/giữ nằm ở `closing-sprint`; dọn dẹp và điều cấm có đủ) |
| 7 | Sprint 14 đã được duyệt Đạt ở Cổng 2, trên đĩa còn 3 nhánh task chưa gộp vào nhánh sprint và 2 file REGISTRY chưa cập nhật số liệu. Tôi cần soạn release note, ghi 4 bài học vào sổ, cập nhật spec sống rồi mới quyết định gộp cục bộ hay đẩy PR, và tuyệt đối không muốn bị force-push hay xoá nhánh nào ngoài ý muốn. Quy trình nào dẫn tôi đi hết chuỗi việc đóng sprint này, nhất là khâu chốt trước khi chạm vào nhánh? | mục khác: skill `closing-sprint` (từ `SKILL.md` › 5 và › 6: menu kết thúc ở `closing-sprint`); `worktrees` chỉ lo dọn thư mục | mục khác: `closing-sprint` (từ `SKILL.md` › 5, › 6) | Đạt |

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

## Thiếu nội dung / mâu thuẫn

- Câu 1: Xử lý khi hai worktree cùng muốn sửa một file, cách gộp các nhánh task vào nhánh tích hợp (thứ tự, merge hay rebase, xung đột).
- Câu 2: Tạo worktree/nhánh từ một tag (lệnh mẫu không có điểm xuất phát), gộp ngược hotfix về `main`.
- Câu 3: Khởi tạo submodule và LFS trong worktree phụ, lý do tăng dung lượng và cách giảm; dòng "trong submodule" của skill nói về agent đứng trong submodule, không phải việc này.
- Câu 5: `git worktree add --detach` trỏ vào nhánh PR rồi gỡ, bảo đảm không để lại nhánh local; lệnh mẫu của skill luôn có `-b <nhánh>`.
- Điều kiện Đạt ghi trước ở file nháp có vài chỗ đánh dấu "phần phụ"; lượt này **không** nương theo dấu đó: việc câu hỏi nêu đích danh mà skill không có thì câu tính Một phần. Các phần phụ thiếu ở câu Đạt ghi ngay trong cột "Kết quả".
- Skill chưa sửa ở lượt này (việc của điều phối); `skill_sha` là băm cây skill hiện tại.

## Lịch sử

Lượt trước (`TK11`/`TK12`, bộ câu cũ, ngày 2026-10-04, `skill_sha` fbcbc7509618b5c69a8f372a7125c106fb3719db, id chủ thể a71a62ffa2ff7a5d7): `result` là `strict 6/6 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 6/6`. Bảng cũ giữ nguyên chữ, nhãn `Cũ-n`:

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| Cũ-1 | Nhận task brief cho TK7, muốn chạy trong chỗ làm việc tách biệt để hỏng thì vứt đi mà không ảnh hưởng checkout đang mở. Tạo bằng cách nào, đặt tên nhánh ra sao, làm gì ngay sau khi tạo trước khi code? | `SKILL.md` › 1 (dò), › 2 (1a/1b, `git worktree add`, đoạn "Tên nhánh"), › 4 (baseline, ghi PROGRESS) | `SKILL.md` › 2. Bước 1 — tạo không gian tách biệt; › 1; › 4 | Đạt |
| Cũ-2 | Repo Node, worktree mới trống trơn: không `node_modules`, không `.env.local`, build báo thiếu dependency. Dựng môi trường theo thứ tự nào để agent làm việc được ngay? | `SKILL.md` › 3 (dựng dự án `npm ci`; đoạn "File không theo dõi không đi theo sang worktree": `.env.local` chép từ `.env.example`, không chép secret thật) + › 4 | `SKILL.md` › 3. Bước 2 — dựng dự án | Đạt |
| Cũ-3 | Hai agent cùng repo, một sửa module auth, một sửa module báo cáo, cả hai định `git checkout -b` ngay trong thư mục hiện tại. Chia chỗ làm việc để không dẫm lên index và working tree của nhau thế nào, mỗi agent cấp đường dẫn nào? | `SKILL.md` › 2 (đoạn "Nhiều agent song song": mỗi agent một worktree + nhánh riêng, đường dẫn tuyệt đối, phạm vi file không giao nhau) + › 5 | `SKILL.md` › 2. Bước 1 (đoạn Nhiều agent song song) | Đạt |
| Cũ-4 | Đã gộp nhánh vào main, test xanh, muốn xoá worktree cùng nhánh. Trước khi xoá cần xác nhận gì để không mất công việc chưa lưu, thứ tự lệnh dọn đúng là gì? | `SKILL.md` › 6 ("Trước khi xoá một worktree của mình": `status` sạch, `log nhánh-đích..nhánh` rỗng, `git worktree remove` không `--force`, `git branch -d`, `prune`) | `SKILL.md` › 6. Dọn khi xong | Đạt |
| Cũ-5 | Worktree cho task dài, hôm sau không nhớ nhánh nào gắn thư mục nào, còn thư mục mồ côi từ task cũ. Liệt kê, kiểm tra, dọn worktree còn sót (kể cả entry trỏ thư mục đã bị xoá tay) thế nào? | `SKILL.md` › 6 ("Worktree còn sót và thư mục mồ côi": `git worktree list`, `prune --dry-run -v`, `prune`, thư mục không có trong list, `repair`, lock) | `SKILL.md` › 6. Dọn khi xong (đoạn Worktree còn sót và thư mục mồ côi) | Đạt |
| Cũ-6 | Vừa mở PR từ nhánh sprint, cần xem trạng thái check CI đang đỏ, đọc log run Actions bị fail và gắn label cho PR. Dùng gì? | mục khác: skill `github-ops` (từ `SKILL.md` › 7 Tra nhanh) | mục khác: `github-ops` (từ `SKILL.md` › 7. Tra nhanh) | Đạt |
