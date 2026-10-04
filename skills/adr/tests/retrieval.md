---
skill: adr
method: retrieval
model: claude-sonnet-5-5
tier: T3
skill_sha: 6c73ece6a5922ef8c83e4149f524b45dc42834b1
date: 2026-10-04
result: "strict 6/7 (+1 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 7/7"
agent_ids:
  questions: a6d0257ebaa6bbfcd
  answers: af8661a49013327ae
---

Đã đọc: `<gốc worktree>/skills/adr/SKILL.md`

# Thử truy xuất — adr (bộ câu mới, lượt độc lập)

> **Kết luận:** strict 6/7 (+1 partial, 0 fail), points-right 7/7: đạt ngưỡng (5/6 câu tình huống Đạt hẳn = 83 %, ngưỡng ≥80 %; câu ranh giới Đạt). Lượt độc lập sau lượt cũ: bộ câu MỚI, người soạn mới, chủ thể mới, chấm lại từ đầu, không nương theo lượt cũ. Không sửa skill.

Bảy câu hỏi do một agent MỚI (`sonnet`, `a6d0257ebaa6bbfcd`) **chưa đọc** skill soạn từ `description`, lĩnh vực và danh sách câu của mọi bộ cũ (để không lặp). Người soạn chỉ đọc một tệp đầu vào gồm đúng ba thứ đó. Cột "Mục kỳ vọng" do QA đọc `SKILL.md` và `references/` rồi ghi vào tệp nháp (mtime `2026-10-04 10:41:37 +0700`) **trước khi** giao chủ thể (lệnh giao sau `2026-10-04 10:42:34 +0700`). Chủ thể là agent mới (`sonnet`, `af8661a49013327ae`), cấm công cụ Skill, được đưa đường tuyệt đối tới `SKILL.md`, không được mở thư mục `tests/`; 3 lượt công cụ (2 lần đọc, 1 lần tìm `references/`; skill chỉ có `SKILL.md`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng. Bài trả lời trọn của chủ thể, câu hỏi của người soạn, id agent và tệp kỳ vọng (có mtime) ở `evidence/TK13/adr-retrieval.md` và `evidence/TK13/expected/adr-expected.md` trong hồ sơ sprint của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Câu 7 là câu ranh giới (đáp án của người soạn ghi ở cột kỳ vọng). Skill KHÔNG đổi giữa lượt cũ và lượt này (`skill_sha` giữ nguyên).

Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + Một phần, tức số câu trỏ đúng nơi.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| 1 | Team mình định bỏ hẳn thư viện gửi email nội bộ để chuyển sang một nhà cung cấp SMTP bên ngoài. Việc này kéo theo đổi hợp đồng dữ liệu của 5 template thư và thêm một khoản phụ thuộc mới vào dịch vụ bên ngoài mà cả ba đội đều dùng. Hiện mới có cuộc trao đổi trên Slack, chưa ai ghi lại gì. Mình nên viết ra cái gì, gồm những phần nào, để người vào team sau 1 năm hiểu được vì sao chọn nhà cung cấp đó? | `SKILL.md` › 1 (bỏ công nghệ, đổi hợp đồng, phụ thuộc mới) + › 2 (nội dung một ADR) | `SKILL.md` › 1, › 2, › 3 | Đạt |
| 2 | Dịch vụ xác thực của mình đang dùng session cookie lưu trong Redis, giờ sản phẩm mobile mới buộc phải chuyển sang token tự chứa (JWT) cho cả web lẫn app. Đổi xong thì toàn bộ 8 dịch vụ phía sau phải sửa cách kiểm tra danh tính, và khó quay lại vì app đã phát hành lên store. Mình đang chuẩn bị họp chốt hướng đi. Tài liệu chốt quyết định này cần chứa những gì để buổi họp có kết quả rõ ràng, và trạng thái của nó nên là gì trước và sau buổi họp? | `SKILL.md` › 2 (nội dung, trạng thái) + › 4 (`proposed` → `accepted` ở Cổng 1) | `SKILL.md` › 2, › 4, › 1, › 5 | Đạt (phần phụ: "buổi họp" được quy về Cổng 1; skill không mô tả cách chạy buổi họp) |
| 3 | Mình vừa phát hiện trong thư mục `docs/decisions/` đã có sẵn một bản ghi cũ chọn RabbitMQ làm hàng đợi, trạng thái "accepted". Nay hệ thống chuyển sang Kafka vì cần phát lại sự kiện, và đội vận hành đã gật. Mình định mở file cũ ra sửa chữ RabbitMQ thành Kafka cho đỡ rối. Làm vậy có ổn không, hay có cách xử lý nào đúng hơn cho cả file cũ lẫn file mới, kể cả việc đánh số? | `SKILL.md` › 4 bước 4 (ADR mới thay thế, cũ chỉ đổi trạng thái) + › 3 (số kế tiếp) + › 6 | `SKILL.md` › 4, › 3, › 6, › 1 | Đạt (phần phụ: thư mục `docs/decisions/` khác `paths.adr_dir` mặc định không được nói tới) |
| 4 | Đội mình sắp đổi mô hình dữ liệu của bảng `invoice`: tách `customer_address` thành bảng riêng, ba dịch vụ khác đang đọc cột đó trực tiếp. Có hai phương án: giữ cột cũ song song một thời gian hoặc cắt ngay một lần. Mình đã nghiêng về phương án giữ song song nhưng người review cứ hỏi "vậy phương án kia bị loại vì sao?". Mình nên trình bày các phương án và hệ quả của chúng ở đâu, theo cấu trúc nào, để câu hỏi đó không bị lặp lại? | `SKILL.md` › 2 (bảng Lựa chọn, Quyết định, Hệ quả) | `SKILL.md` › 2, › 1, › 6 | Đạt |
| 5 | Kế hoạch lớp học đang chạy là chuyển luôn toàn bộ pipeline build từ Jenkins sang GitHub Actions trong quý này, với 40 job và một số runner tự host. Khi review kế hoạch, Tech Reviewer ghi một phát hiện: "chưa thấy ghi nhận các quyết định kiến trúc, chặn cổng". Mình nên bổ sung gì vào hồ sơ sprint để gỡ phát hiện đó, và nên gắn nó vào kế hoạch ở điểm nào? | `SKILL.md` › 1 (việc cỡ lớn: PLAN có ≥1 ADR) + › 4 (PLAN trỏ tới ADR) | `SKILL.md` › 1, › 4, › 2 | Đạt (phần phụ: vị trí cụ thể trong PLAN không có) |
| 6 | Đội mình thảo luận mấy tuần về việc có nên dùng event sourcing cho module sổ cái. Sau cùng quyết định là KHÔNG dùng, giữ bảng giao dịch kiểu truyền thống, nhưng nhiều người trong team vẫn còn nghi ngờ và chắc sẽ có người đề xuất lại sau này. Quyết định "không làm" như vậy có đáng ghi lại không, và nếu có thì ghi sao để lần sau không phải cãi lại từ đầu? | `SKILL.md` › 1 (phép thử ba tháng) + › 2 ("giữ nguyên hiện trạng" là lựa chọn hợp lệ) | `SKILL.md` › 1, › 2, › 6 | Một phần (đúng nơi; skill không nói thẳng quyết định "không làm" có đáng ghi, chỉ suy ra từ phép thử ba tháng) |
| 7 | Mình đang thêm endpoint `GET /orders` cho dịch vụ đơn hàng và phân vân giữa phân trang theo `offset/limit` hay theo con trỏ (`cursor`), cùng với cách trả về lỗi 422 khi tham số lọc `status` không hợp lệ. Bảng đơn hàng khoảng 2 triệu dòng, chỉ có một client nội bộ dùng. Nên chọn kiểu phân trang nào và định dạng phản hồi lỗi ra sao? | mục khác: skill `api-design` (chọn phân trang, định dạng lỗi; `adr` › 1 "Không cần ADR" cho việc nhỏ) | mục khác: `api-design` (chủ thể tự suy tên; `SKILL.md` chỉ có › 1 "Không cần ADR" và › 6) | Đạt |

## Thiếu nội dung / mâu thuẫn

- Quyết định "không làm" (giữ nguyên hiện trạng sau khi cân nhắc một hướng mới): skill chỉ ngầm cho phép qua phép thử ba tháng và dòng "giữ nguyên hiện trạng là lựa chọn hợp lệ"; không nói thẳng rằng nên ghi, và ghi thế nào để khỏi bị đề xuất lại (câu 6).
- `SKILL.md` không có con trỏ sang bất kỳ skill nào (không `api-design`, không `database-migrations`); chủ thể tự suy tên `api-design` từ câu hỏi nên câu ranh giới Đạt theo thước nhưng skill không dẫn đường sang đó (câu 7).
- Chỉ cách xử lý buổi họp chốt quyết định: skill gắn "duyệt" với Cổng 1, không có chỗ cho buổi họp riêng (câu 2, phụ); thư mục ADR khác mặc định (câu 3, phụ); chỗ gắn ADR vào PLAN ngoài "trỏ bằng số, đường file, mệnh đề" (câu 5, phụ).
- `description` không hứa chỗ nào thân skill không có.

## Chạy lại sau `fix-2` (QA2, SPR-04)

QA độc lập (khác mọi Implementer của `fix-1`/`fix-2`), 2026-10-04, `a35b618`, cây skill đúng `skill_sha` ở frontmatter. Thân `SKILL.md` đổi ở `fix-1` (mục 4 bước 3 chỉ cho ADR lập lúc PLAN; mục 4 bước 5 quyết định lộ giữa sprint; mục 4 bước 6 ADR `secret`/`auth`) và không đổi thêm ở `fix-2` (chỉ băm cây được ghi lại), nên chạy lại **trọn hai bộ câu** của tệp này (13 câu, chữ nguyên: bảng chính câu 1–7 và bộ cũ `c1`–`c6` ở mục Lịch sử). Chủ thể: một subagent mới (`claude-sonnet-5-5`, tier T3, `a498c9c2cf532f7af`), không dùng công cụ Skill, được đọc `SKILL.md` và tài liệu được trỏ (đọc thêm `method/sizing.md`, `method/process.md`), không mở `tests/`. Kỳ vọng ghi trước (`evidence/QA2/expected/adr-expected.md`, sha256 `edd4746c5de978c6f103fa92e064d0c8b1db882d75978bf86fe80259147ff616`, mtime 19:13:56, trước lượt giao); output trọn ở `evidence/QA2/adr-retrieval.md` của hồ sơ sprint `SPR-04` của lớp riêng (`docs/plans/2026-10-04-agent-agile-team-wave-3/`).

| Câu | Mục agent trỏ | Kết quả |
|---|---|---|
| `câu 1` | `SKILL.md` › 1, 2, 3 | Đạt |
| `câu 2` | `SKILL.md` › 2, 4 (bước 3, 6), 5 | Đạt (phần phụ: buổi họp ngoài sprint không được nói tới; chủ thể dùng bước 6 mới: `security-review` đọc ADR `auth` trước khi `accepted`) |
| `câu 3` | `SKILL.md` › 4 (bước 4), 6, 3 | Đạt (phần phụ: thư mục `docs/decisions/` khác `paths.adr_dir`) |
| `câu 4` | `SKILL.md` › 1, 2, 4, 6 | Đạt |
| `câu 5` | `SKILL.md` › 1, 4 | Đạt (phần phụ: vị trí cụ thể trong PLAN; chủ thể tự chấm Một phần, giữ Đạt theo thước chung như lượt trước) |
| `câu 6` | `SKILL.md` › 1, 2, 6 | Một phần (đúng nơi; skill không nói thẳng quyết định "không làm" có đáng ADR) |
| `câu 7` | `SKILL.md` › 1 "Không cần ADR"; đáp `api-design` | Đạt (ranh giới) |
| `c1` | `SKILL.md` › 1, 2, 6 | Đạt (phần phụ: PR ngoài sprint; chủ thể tự chấm Một phần, giữ Đạt theo thước chung) |
| `c2` | `SKILL.md` › 1, 4, 5 | Đạt |
| `c3` | `SKILL.md` › 2, 4, 5, 6 | Đạt (phần phụ: áp lực hạn chót; chủ thể tự chấm Một phần, giữ Đạt theo thước chung như lượt trước) |
| `c4` | `SKILL.md` › 1, 2, 4 | Đạt |
| `c5` | `SKILL.md` › 4 (bước 4), 5, 6, 3 | Đạt |
| `c6` | `SKILL.md` › 1 "Không cần ADR"; đáp `database-migrations` | Đạt (ranh giới) |

Bảng chính (câu 1–7): 6 Đạt hẳn, 1 Một phần, 0 Không đạt, đúng bằng `result` ở frontmatter (`retrieval_result()` trên bảng chính không đổi nên giữ nguyên). Bộ cũ `c1`–`c6`: 6/6 Đạt hẳn. Giới hạn: n = 1; người chấm cùng họ mô hình với chủ thể (`CQ3`); ba câu (`câu 5`, `c1`, `c3`) chủ thể tự chấm Một phần nhưng người chấm giữ Đạt theo thước chung. Không câu nào hỏi riêng bước 5 mới (ADR lộ giữa sprint); bước 6 mới được chủ thể dùng ở `câu 2`.

## Lịch sử

Lượt trước (bộ câu cũ, 2026-10-04, `skill_sha` `e51ac5cfa6684f45de70dddd469b1975496a4a62`, `result`: strict 6/6 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); points-right 6/6). Bộ câu cũ giữ nguyên bên dưới, id hàng đổi thành `c1`… để không lẫn vào bảng chấm của lượt mới; người soạn lần sau phải đọc cả hai bộ để không lặp. Dòng "Đã đọc" và đoạn thước chấm của lượt cũ không chép lại (thước chung ở trên).

> **Kết luận:** strict 6/6 (+0 partial, 0 fail), points-right 6/6: đạt ngưỡng (5/5 câu tình huống Đạt; câu ranh giới Đạt). Chạy lại ở SPR-04 TK10 trên bản `SKILL.md` **viết lại phòng sạch**
> (`skill_sha` ở frontmatter đổi so lượt trước; `description` không đổi). Giữ **nguyên bộ câu hỏi cũ** (người soạn `a25859e6268e55dde` của lượt trước); cột Mục kỳ vọng viết lại theo bản mới (các số mục
> của `SKILL.md` đổi: 6 mục, không còn bảng Đầu vào/khuôn riêng). Chủ thể là agent mới, do QA chạy.

Sáu câu hỏi do một agent **chưa đọc** skill soạn ở lượt trước (bộ câu giữ nguyên chữ, không soạn lại); file nháp "Mục kỳ vọng" viết lại theo bản mới (mtime `2026-10-04 08:09:28 +0700`) **trước khi** giao chủ thể
(lệnh giao lúc ~08:10 +0700); bài trả lời trọn của chủ thể và id agent ở `evidence/TK10/qa-adr.md` trong hồ sơ sprint của lớp riêng
(`docs/plans/2026-10-04-agent-agile-team-wave-3/`). Dòng "Đã đọc" chép từ bài trả lời của chủ thể, đoạn đầu đường dẫn (thư mục người dùng) lược thành `<gốc worktree>` vì repo chặn tên người dùng.
Số lượt công cụ của chủ thể chưa đo (harness không báo). Skill chỉ có `SKILL.md`, không có `references/`. Câu 6 là câu ranh giới: đáp án của người soạn (`database-migrations`) đã được đối chiếu với `description` của skill đích
(thêm hoặc đổi cột, bảng lớn, backfill, đổi lược đồ không khoá) và nhận là đúng.

| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |
|---|---|---|---|---|
| c1 | Mình đang review PR của đồng nghiệp: bạn ấy gộp luôn module thanh toán vào dịch vụ đơn hàng và cho đơn hàng gọi thẳng vào bảng của thanh toán. PR không có dòng nào giải thích vì sao lại làm vậy thay vì giữ hai dịch vụ tách nhau. Mình nên đòi bạn ấy bổ sung gì để sau này người khác hiểu lý do, và đòi ở đâu? | `SKILL.md` › 1. Khi nào viết (tạo phụ thuộc mới giữa hai phần vốn độc lập) + › 2. Nội dung một ADR + › 3. Đánh số và nơi đặt + › 6. Lỗi hay gặp (ADR viết sau khi code) | `SKILL.md` › 1. Khi nào viết; › 2. Nội dung một ADR; › 3. Đánh số và nơi đặt; › 6. Lỗi hay gặp | Đạt |
| c2 | Sprint này mình là người điều phối, có một task cỡ lớn là tách dữ liệu khách hàng ra khỏi database dùng chung để mỗi dịch vụ có kho riêng. Kế hoạch đã gần xong nhưng mới chỉ có danh sách việc, chưa thấy chỗ nào ghi các lựa chọn thiết kế đã cân nhắc. Trước khi cho qua cổng duyệt kế hoạch, mình cần đảm bảo điều gì về phần quyết định thiết kế? | `SKILL.md` › 1. Khi nào viết (việc cỡ lớn: PLAN phải có ≥1 ADR hoặc nói thẳng không có) + › 4. Vòng đời bước 2 (review cùng PLAN trước Cổng 1) + › 2 (≥2 lựa chọn thật) | `SKILL.md` › 1. Khi nào viết (việc cỡ lớn); › 4. Vòng đời; › 5. Điểm dừng | Đạt |
| c3 | Sắp tới hạn bàn giao mà team vẫn đang cãi nhau: giữ nguyên REST cho đối tác bên ngoài hay đổi sang GraphQL. Đối tác đã tích hợp 6 tháng rồi, đổi thì họ phải viết lại. Anh sếp bảo chốt trong hôm nay, mình trễ hạn nên muốn chốt nhanh gọn mà vẫn không bị ai hỏi lại "sao hồi đó lại chọn vậy" sau này. Nên chốt và lưu lại kiểu gì? | `SKILL.md` › 1 (đổi hợp đồng) + › 2 (≥2 lựa chọn gồm giữ nguyên, Hệ quả có đường lùi) + › 5. Điểm dừng (hai lựa chọn ngang nhau → `DN` trong PLAN, không tự chốt) + › 4 (Cổng 1 → accepted) | `SKILL.md` › 1. Khi nào viết; › 2. Nội dung một ADR; › 5. Điểm dừng (hai lựa chọn ngang nhau thành `DN`); › 6. Lỗi hay gặp | Đạt |
| c4 | Công ty mình đang trả tiền thuê một dịch vụ tìm kiếm bên thứ ba khá đắt, và có người đề xuất bỏ hẳn, tự dựng bằng tính năng full-text của cơ sở dữ liệu hiện có. Phải sửa lại ba chỗ gọi API tìm kiếm và dữ liệu đồng bộ đi kèm. Chưa ai làm gì cả, mới đang bàn. Trước khi bắt tay vào, mình cần làm gì với quyết định gỡ bỏ công nghệ này? | `SKILL.md` › 1 (bỏ một công nghệ đang dùng) + › 2 (Hệ quả: khó hơn, đường lùi và giá) + › 4 (proposed, review trước Cổng 1, chưa duyệt chưa code) | `SKILL.md` › 1. Khi nào viết; › 2. Nội dung một ADR; › 4. Vòng đời | Đạt |
| c5 | Cuối năm ngoái mình ghi lại là "mọi dữ liệu người dùng lưu ở một vùng duy nhất cho đơn giản", đã được duyệt. Giờ khách hàng châu Âu yêu cầu dữ liệu phải nằm trong khu vực của họ, nên chắc chắn phải lưu theo từng vùng. Với bản ghi cũ đang nằm đó, mình nên đụng vào nó thế nào, và cái mới thì viết ra sao cho người sau đọc được cả hai? | `SKILL.md` › 4. Vòng đời bước 4 (ADR mới thế chỗ; cũ chỉ đổi trạng thái `superseded by NNNN`) + › 2 (Trạng thái, Liên kết) + › 3 (số kế tiếp, không tái dùng) + › 5, › 6 (không sửa ADR cũ) | `SKILL.md` › 4. Vòng đời (bước 4); › 5. Điểm dừng; › 6. Lỗi hay gặp | Đạt |
| c6 | Mình đã chốt sẽ chạy trên Postgres rồi, bây giờ chỉ cần thêm một cột `deleted_at` vào bảng đơn hàng 40 triệu dòng và điền giá trị mặc định cho dữ liệu cũ mà không được khóa bảng làm sập hệ thống. Nên làm theo trình tự nào? | mục khác: skill `database-migrations` (nền tảng đã chốt, chỉ thêm cột + backfill bảng lớn không khoá; `SKILL.md` › 1 "Không cần ADR") | mục khác: skill `database-migrations` (kèm `postgres`, reviewer `database-reviewer`), từ `SKILL.md` › 1 phần "Không cần ADR" | Đạt |

### Thiếu nội dung / mâu thuẫn

- Không có chỗ nào `description` hứa mà thân skill không có.
- Chỗ thiếu còn lại sau khi viết lại (chủ thể nêu hoặc tôi đối chiếu): khuôn mục "Hệ quả" trong `skills/adr/SKILL.md` mục 2 có ô "Quay lại" nhưng không có chỗ riêng cho kế hoạch chuyển đổi và quay lui khi quyết định là bỏ công nghệ hay gỡ dịch vụ (câu 4).
- Chủ thể nêu thêm các chỗ phụ: skill không nói lời của người ngoài quy trình (sếp) có tính là người duyệt ở cổng không và không có đường chốt nhanh dưới áp lực hạn chót (câu 3); không nói trường "Liên kết" của ADR thay thế phải ghi ra sao ngoài việc ghi rõ nó thế chỗ ADR nào, và không nói về di chuyển dữ liệu thật của bản ghi cũ (câu 5); `method/sizing.md` được nhắc nhưng không giải thích cỡ lớn trong file này (câu 2, phụ).
- Đã sửa so lượt trước: bản viết lại có đoạn "ADR viết sau khi code" ở mục 6 (câu 1 nay được trả lời trực tiếp); không còn dòng "đòi ADR trong PR đang review" riêng.

### Lịch sử

Lượt trước (2026-10-04, `skill_sha` `8daf1ea5596506d312da96d148a45f632368e77d`, bản trước khi viết lại phòng sạch, người soạn `a25859e6268e55dde`, chủ thể `a876fed94c9014359`): strict 6/6 (+0 partial, 0 fail), points-right 6/6, cùng bộ câu hỏi.

### Chạy lại sau `TK12.1` (mục 5)

- chạy lại 2026-10-04 sau khi `source:` của `SKILL.md` đổi (mã hồ sơ riêng vào dấu code kèm tên ngắn, `TK12.1` mục 5); bộ sáu câu giữ nguyên chữ; chủ thể mới `a27b454d81f8d3543`; 6/6 Đạt như lượt trước. Cột "Mục agent trỏ" ở bảng trên ghi theo lượt này; `result` không đổi (đếm lại từ bảng). Bài trả lời trọn ở `evidence/TK12/adr-retrieval-rerun.md` trong hồ sơ sprint `SPR-04` của lớp riêng.
