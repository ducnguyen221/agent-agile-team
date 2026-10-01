# Hướng dẫn dùng — sprint đầu tiên

> **Kết luận:** bạn giao việc bằng lời thường, rồi chỉ phải lên tiếng **hai lần** — "duyệt" ở Cổng 1 và
> "Đạt / Đạt có điều kiện / Không đạt" ở Cổng 2. Mọi bước còn lại agent tự làm, tự ghi sổ, và nhờ **agent
> khác** kiểm. File này dẫn bạn đi một sprint thật từ đầu tới cuối.

Chưa cài: xem [`INSTALL.md`](INSTALL.md). Luật đầy đủ: [`method/process.md`](method/process.md).

## 1. Ba khái niệm cần biết

- **Sprint** = một mục tiêu (một tính năng, một lần sửa lỗi, một đợt chỉnh), dài ngắn tùy việc, không đo theo
  tuần. Mỗi sprint có một thư mục với bốn tài liệu: SPEC (làm gì), PLAN (làm thế nào), PROGRESS (đang tới
  đâu), REPORT (kết quả). Việc rất nhỏ gộp cả bốn vào một file `SPRINT.md`.
- **Sổ gốc** — ba file sống lâu của dự án: REQUESTS (mọi yêu cầu theo thời gian, mã `RQ-001`…), SPRINTS
  (mọi sprint, mã `SPR-01`…), SPECS (mọi tính năng đang chạy, mã `FS-001`…). Đầu mỗi sổ có khối "Đang mở" để
  agent tra nhanh.
- **Vai và tier** — agent nhận vai (Analyst điều phối, Architect, Implementer, QA, Business Reviewer, Tech
  Reviewer); mỗi vai có **tier** (`T1` tư duy · `T2` thực thi · `T3` việc vặt và chạy test) thay vì tên
  model. Ai làm thì **không** tự chấm việc của mình.

## 2. Dựng khung cho dự án (một lần)

Trong thư mục dự án của bạn (không phải thư mục repo này), nhờ agent chạy — hoặc tự chạy:

```bash
python ~/agent-agile-team/scripts/init.py .            # chạy thử: in sẽ tạo gì, không ghi
python ~/agent-agile-team/scripts/init.py . --apply    # tạo .agile.json + REQUESTS, SPRINTS, SPECS
```

`init` không bao giờ ghi đè file có sẵn; chạy lại không đổi gì. Đường dẫn mặc định (`docs/plans/`,
`docs/specs/`) đổi được trong `.agile.json`. Muốn xem trước một dự án đã dùng thật:
[`samples/order-desk/`](samples/README.md).

## 3. Sáu bước — bạn làm gì, agent làm gì

| Bước | Bạn | Agent |
|---|---|---|
| 1. Tiếp nhận | Nói yêu cầu bằng lời thường | Ghi dòng `RQ-` vào REQUESTS, định cỡ (rất nhỏ / nhỏ / vừa / lớn) và rủi ro, ghi giả định, gom câu hỏi chưa rõ. **Không dừng hỏi** ở bước này |
| 2. SPEC rồi PLAN | **Cổng 1:** đọc bản tóm tắt, trả lời "duyệt" hoặc "điều chỉnh: …" | Mở sprint bằng `init --sprint`, viết SPEC + PLAN; từ cỡ vừa nhờ reviewer soát PLAN trước khi trình. Chưa duyệt thì **không viết code** |
| 3. Thực thi | Không cần làm gì | Làm từng việc theo PLAN, cập nhật PROGRESS kèm bằng chứng; chỗ PLAN chưa nói thì tự quyết và ghi một dòng `Phán quyết:` |
| 4. Kiểm định | Không cần làm gì | Agent **khác** người làm kiểm; còn lỗi nặng thì quay lại bước 3. Sau 3 vòng còn lỗi → hỏi bạn làm tiếp hay dừng |
| 5. REPORT | **Cổng 2:** kết luận Đạt / Đạt có điều kiện / Không đạt | Viết REPORT (kết luận trước, cách dùng, cách hoàn tác, việc để lại), nợ còn lại thành dòng `RQ-` mới |
| 6. Bài học | Quyết có nâng bài học thành luật hay không | Ghi bài học vào nơi môi trường quy định; bài quan trọng chỉ **đề xuất** nâng |

Câu lệnh mẫu để bắt đầu: *"Dùng agent-agile-team: thêm chức năng tra cứu đơn theo mã cho dự án này."*

## 4. Khi nào agent được dừng hỏi bạn

Ngoài hai cổng, agent chỉ dừng hỏi khi: (a) sắp làm việc **không hoàn tác được**, (b) chạm **bảo mật hoặc
secret**, (c) sắp tác động **ra ngoài phạm vi** đã giao (push, deploy, gửi tin, sửa file ngoài dự án), (d) PLAN
hỏng vì giả định sai. Cộng thêm: sau 3 vòng kiểm định còn lỗi, và khi model của một tier cạn hạn mức. Agent hỏi
ngoài các trường hợp này là lỗi quy trình — bạn cứ nhắc.

## 5. Ba công cụ giữ sổ sách

```bash
python ~/agent-agile-team/scripts/check.py docs/plans      # kiểm tài liệu: đủ phần, mã đúng chuẩn, không tự chấm
python ~/agent-agile-team/scripts/index.py .               # sinh lại khối "Đang mở" ở đầu ba sổ gốc
python ~/agent-agile-team/scripts/check.py --self --root ~/agent-agile-team   # kiểm chính repo phương pháp
```

`check` thoát 0 = Đạt, 1 = Không đạt (in từng phát hiện kèm file và dòng), 2 = lỗi đầu vào. Agent chạy chúng
trước mỗi cổng; bạn chỉ cần đọc dòng cuối. macOS: `python3` thay cho `python`. Gặp cảnh báo hay mất dấu tiếng
Việt: [`docs/troubleshooting.md`](docs/troubleshooting.md).

## 6. Đọc tài liệu sprint thế nào cho nhanh

- **Câu đầu** của mọi tài liệu và mọi lời trình là kết luận — đọc câu đầu là đủ để quyết phần lớn trường hợp.
- Mã luôn đi kèm tên ngắn, ví dụ "`FR3` (tra theo mã đơn)"; gặp mã lạ thì hỏi "`FR3` là gì?".
- Muốn biết "tính năng X đang ở đâu, sprint nào đang mở": hỏi agent — nó tra khối "Đang mở" của ba sổ gốc,
  không phải mở từng sprint cũ.
- Gặp tên skill cũ trong hồ sơ lịch sử: [`docs/MIGRATION.md`](docs/MIGRATION.md).
