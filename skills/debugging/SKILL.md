---
name: debugging
description: Use when a bug, test failure, flaky test, build or CI failure, performance problem or any unexpected behavior appears, before proposing or writing a fix; also when a previous fix did not work or you are tempted to try "one more quick fix".
metadata:
  group: technique
  roles: [implementer, qa, tech-reviewer]
source: [obra/superpowers skills/systematic-debugging/SKILL.md, garrytan/gstack investigate/SKILL.md.tmpl, obra/superpowers-skills skills/debugging/defense-in-depth/SKILL.md, obra/superpowers-skills skills/testing/condition-based-waiting/SKILL.md]
source_sha: [8ca22dba9a94f28898bbce59f2537ff4d87c747d, 96764e80a641e28141ec8297223768029f5bf483, cdcd624ad3fd8026deb692e565351854569798dd, cdcd624ad3fd8026deb692e565351854569798dd]
license: [MIT, MIT, MIT, MIT]
rewrite_before_public: false
---

# Gỡ lỗi có hệ thống

> **Kết luận:** luôn tìm **nguyên nhân gốc** trước khi sửa; sửa triệu chứng là thất bại. Đi đủ bốn pha
> theo thứ tự — điều tra, so mẫu, giả thuyết, sửa — mỗi pha xong mới sang pha sau. **3 lần sửa (hoặc 3 giả
> thuyết) hỏng cho cùng một lỗi → dừng, ghi `BR`, đưa câu hỏi kiến trúc lên**, không thử lần thứ 4.

## 1. Luật sắt

```
KHÔNG SỬA KHI CHƯA ĐIỀU TRA NGUYÊN NHÂN GỐC
```

Chưa xong pha 1 thì chưa được đề xuất cách sửa. Làm sai chữ của quy trình là làm sai tinh thần gỡ lỗi.

Dùng cho **mọi** sự cố kỹ thuật: test hỏng, lỗi production, hành vi lạ, hiệu năng, build, tích hợp. Dùng
**nhất là** khi đang gấp, khi "sửa nhanh một chỗ" trông hiển nhiên, khi đã thử vài lần sửa, khi lần sửa
trước không ăn, khi chưa hiểu hết vấn đề. Lỗi đơn giản cũng có nguyên nhân gốc; với lỗi đơn giản, quy
trình chạy rất nhanh.

## 2. Bốn pha

### 2.1 Pha 1 — Điều tra nguyên nhân gốc

1. **Đọc kỹ thông báo lỗi.** Không lướt qua lỗi hay cảnh báo; đọc hết stack trace; ghi số dòng, đường
   dẫn, mã lỗi. Lời giải thường nằm ngay trong đó.
2. **Tái hiện ổn định.** Kích được lỗi mỗi lần không? Các bước chính xác? Không tái hiện được → thu thêm
   dữ liệu, không đoán.
3. **Xem thay đổi gần đây.** `git log --oneline -20 -- <file liên quan>`, `git diff`, phụ thuộc mới, cấu
   hình, khác biệt môi trường. Từng chạy được → nguyên nhân gần như chắc nằm trong diff.
4. **Lỗi lặp lại ở cùng file là mùi kiến trúc, không phải xui.** Ba lần vá cùng một module trong vài
   tháng nghĩa là module sai. Nói rõ trong báo cáo.
5. **Hệ nhiều thành phần** (CI → build → deploy, API → service → DB): trước khi đề xuất sửa, gắn đo đạc ở
   **mỗi ranh giới** — dữ liệu vào, dữ liệu ra, cấu hình/biến môi trường có truyền qua không, trạng thái
   từng tầng. Chạy **một lần** để thấy tầng nào gãy, rồi mới điều tra đúng tầng đó.

   ```bash
   # Tầng 1 — workflow: biến có mặt không (chỉ in SET/UNSET, không in giá trị secret)
   echo "DEPLOY_TOKEN: ${DEPLOY_TOKEN:+SET}${DEPLOY_TOKEN:-UNSET}"
   # Tầng 2 — script build: biến có xuống tới tiến trình con không
   python -c "import os; print('DEPLOY_TOKEN' in os.environ)"
   # Tầng 3 — bước thật sự hỏng, bật chế độ chi tiết
   ./deploy --verbose
   ```
6. **Lần ngược luồng dữ liệu** khi lỗi nằm sâu trong call stack: giá trị xấu sinh ra ở đâu, ai gọi với
   giá trị đó, lần tiếp lên tới nguồn; sửa ở nguồn. Kỹ thuật đầy đủ:
   [references/root-cause-tracing.md](references/root-cause-tracing.md).

Đầu ra pha 1: một câu **"Giả thuyết nguyên nhân gốc: …"** — cụ thể, kiểm được.

Sau khi có giả thuyết, **khoanh phạm vi sửa**: gọi tên thư mục hẹp nhất chứa file liên quan, chỉ sửa
trong đó. Lỗi trải cả repo hoặc phạm vi thật sự chưa rõ → bỏ khoanh và ghi lý do.

### 2.2 Pha 2 — So mẫu

1. **Đối chiếu mẫu lỗi đã biết** trước khi lập giả thuyết:

   | Mẫu | Dấu hiệu | Tìm ở đâu |
   |---|---|---|
   | Tranh chấp (race) | chập chờn, phụ thuộc thời điểm | truy cập đồng thời vào trạng thái chung |
   | Lan truyền giá trị rỗng | `NoneType`/`TypeError`/`AttributeError` | thiếu chặn giá trị tuỳ chọn |
   | Hỏng trạng thái | dữ liệu không nhất quán, cập nhật dở | transaction, callback, hook |
   | Hỏng tích hợp | timeout, phản hồi sai hình dạng | gọi API ngoài, ranh giới service |
   | Trôi cấu hình | chạy ở máy, hỏng ở staging/production | biến môi trường, feature flag, trạng thái DB |
   | Cache cũ | hiện dữ liệu cũ, "tự hết" khi xoá cache | Redis, CDN, cache trình duyệt/HTTP |

2. **Tìm ví dụ đang chạy** tương tự trong cùng codebase; so cái chạy với cái hỏng.
3. **Đọc hết tham chiếu** khi đang áp một mẫu — đọc từng dòng, không lướt.
4. **Liệt kê mọi khác biệt**, dù nhỏ; không mặc định "cái đó không ảnh hưởng".
5. **Hiểu phụ thuộc**: thành phần khác, cấu hình, môi trường, giả định ngầm.

**Tra cứu ngoài** (khi không khớp mẫu nào và môi trường có công cụ tìm web): **làm sạch trước** — bỏ tên
máy chủ, IP, đường dẫn, mảnh SQL, định danh khách hàng, tên nội bộ. Tìm **loại lỗi + framework**, không
dán nguyên thông báo. Không làm sạch an toàn được → không tìm.

### 2.3 Pha 3 — Giả thuyết và kiểm

1. **Một giả thuyết**, viết ra: "Tôi nghĩ X là nguyên nhân gốc vì Y."
2. **Kiểm tối thiểu**: thay đổi **nhỏ nhất** để kiểm giả thuyết (log tạm, assert, in debug), **một biến
   mỗi lần**, không sửa nhiều thứ cùng lúc.
3. **Đúng** → pha 4. **Sai** → quay về pha 1 với thông tin mới, lập giả thuyết **mới**; không chồng thêm
   cách sửa lên trên.
4. **Không biết thì nói không biết**: "Tôi chưa hiểu X" — không giả vờ; thu thêm bằng chứng.

### 2.4 Pha 4 — Sửa

1. **Viết test hỏng tái hiện lỗi** trước khi sửa — tái hiện đơn giản nhất, tự động nếu được (script
   chạy một lần nếu dự án chưa có framework test). Theo skill `tdd`.
2. **Một cách sửa** nhắm đúng nguyên nhân gốc: diff nhỏ nhất, ít file nhất; không "tiện thể", không gộp
   refactor.
3. **Kiểm**: test mới đạt, **cả bộ test** đạt, kịch bản lỗi gốc chạy lại không còn. Test hồi quy phải
   **hỏng khi gỡ bản sửa** (đã thử). Không tuyên bố "chắc sửa được rồi" — chạy và đưa output (skill
   `verify-before-done`).
4. **Sửa chạm >5 file** → dấu hiệu đang refactor đội lốt sửa lỗi. Chọn một: nguyên nhân thật sự trải các
   file đó (ghi `Phán quyết:` vào PROGRESS kèm lý do) · tách — sửa đường găng bây giờ, phần còn lại thành
   `CO` · nghĩ lại, có lẽ có cách hẹp hơn. Vượt phạm vi file của `TK` → điều kiện dừng, ghi `BR`.
5. **Sửa không ăn** → dừng, đếm số lần đã sửa:
   - **< 3**: về pha 1, phân tích lại với thông tin mới.
   - **≥ 3: dừng, không thử lần 4.** Xem mục 3.

## 3. Ba lần hỏng → dừng, hỏi kiến trúc

Dấu hiệu vấn đề nằm ở kiến trúc, không ở giả thuyết: mỗi lần sửa lộ ra trạng thái chung / độ dính / vấn đề
mới ở chỗ khác; cách sửa đòi "refactor lớn"; mỗi lần sửa sinh triệu chứng mới ở nơi khác.

Đến đây không còn là giả thuyết sai mà là **kiến trúc sai**. Ghi `BR` vào PROGRESS và báo (Analyst, hoặc
người dùng nếu chính bạn điều phối) với đúng **ba lựa chọn**, không hỏi kiểu "giờ sao":

| Lựa chọn | Khi nào hợp |
|---|---|
| Tiếp tục — có một giả thuyết **thật sự mới**: `<nêu ra>` | bằng chứng mới chỉ sang hướng chưa thử |
| Chuyển lên người hiểu hệ thống | cần kiến thức miền hoặc quyết định thiết kế |
| Gắn đo đạc rồi chờ — thêm log, bắt ở lần xảy ra sau | lỗi chập chờn; lựa chọn agent hay quên, thường đúng |

Câu hỏi kiến trúc đi kèm: mẫu này có vững về gốc không? Ta có đang bám nó chỉ vì quán tính? Nên refactor
kiến trúc hay tiếp tục vá triệu chứng?

## 4. Dấu hiệu đỏ — dừng, quay về pha 1

"Sửa tạm, điều tra sau" · "thử đổi X xem sao" · "đổi nhiều chỗ rồi chạy test" · "bỏ test, tôi kiểm tay" ·
"chắc là X, sửa luôn" · "chưa hiểu hết nhưng có thể được" · "mẫu nói X nhưng tôi làm khác" · liệt kê cách
sửa trước khi điều tra · đề xuất sửa trước khi lần luồng dữ liệu · **"thử thêm một lần nữa"** (khi đã hỏng
≥2) · mỗi lần sửa lộ ra vấn đề mới ở chỗ khác.

**Tín hiệu từ người dùng rằng bạn đang sai cách:** "cái đó không xảy ra à?" (bạn giả định mà chưa kiểm) ·
"nó có cho thấy…?" (lẽ ra phải thu bằng chứng) · "đừng đoán nữa" · "nghĩ kỹ lại" (xét lại nền tảng) ·
"ta bị kẹt à?" (cách làm không hiệu quả). Gặp → dừng, về pha 1.

| Bào chữa | Thực tế |
|---|---|
| "Lỗi đơn giản, khỏi quy trình" | Lỗi đơn giản cũng có nguyên nhân gốc; quy trình chạy nhanh với lỗi đơn giản |
| "Khẩn cấp, không có thời gian" | Gỡ có hệ thống **nhanh hơn** đoán-rồi-thử |
| "Thử cái này trước rồi điều tra" | Lần sửa đầu đặt khuôn cho cả phiên — làm đúng từ đầu |
| "Viết test sau khi xác nhận sửa được" | Sửa không có test không bền |
| "Sửa nhiều chỗ một lúc cho nhanh" | Không tách được cái nào ăn; sinh lỗi mới |
| "Tham chiếu dài quá, tôi phỏng theo" | Hiểu một nửa là chắc có lỗi — đọc hết |
| "Thấy vấn đề rồi, sửa luôn" | Thấy triệu chứng ≠ hiểu nguyên nhân gốc |
| "Thử thêm một lần" (sau ≥2 lần hỏng) | ≥3 lần hỏng là vấn đề kiến trúc — mục 3 |

## 5. Khi điều tra kết luận "không có nguyên nhân gốc"

Nếu điều tra có hệ thống cho thấy lỗi thật sự do môi trường, thời điểm hay bên ngoài: ghi lại đã điều tra
gì; xử lý phù hợp (thử lại, timeout, thông báo lỗi rõ — skill `error-handling`); thêm log/giám sát cho lần
sau. Nhưng phần lớn ca "không có nguyên nhân gốc" là **điều tra chưa đủ**.

## 6. Báo cáo gỡ lỗi

Ghi vào PROGRESS (dòng xong `TK`) hoặc báo cáo trả về, theo khung 4 phần của skill `token-economy`, với
phần Chứng cứ chứa đủ:

```
Triệu chứng:      điều người dùng/test quan sát thấy
Nguyên nhân gốc:  điều thật sự sai, và vì sao
Sửa:              đã đổi gì, file:dòng
Bằng chứng:       output test / lần tái hiện chứng minh đã hết
Test hồi quy:     file:dòng của test mới (hỏng khi gỡ bản sửa)
Liên quan:        lỗi cũ cùng khu vực, việc tồn đọng, ghi chú kiến trúc
Trạng thái:       xong | xong có lo ngại | bị chặn
```

"Xong có lo ngại" = đã sửa nhưng không kiểm hết được (lỗi chập chờn, cần staging). "Bị chặn" = vẫn chưa rõ
nguyên nhân sau điều tra, đã ghi `BR`. Không bao giờ ghi "xong" trần cho hai trường hợp đó.

## 7. Kỹ thuật kèm

| Kỹ thuật | Dùng khi |
|---|---|
| [references/root-cause-tracing.md](references/root-cause-tracing.md) | lỗi lộ ra sâu trong call stack; cần biết test nào gây ô nhiễm |
| [references/defense-in-depth.md](references/defense-in-depth.md) | đã tìm ra nguyên nhân gốc do dữ liệu sai — chặn ở mọi tầng để lỗi không thể xảy ra lại |
| [references/condition-based-waiting.md](references/condition-based-waiting.md) | test chập chờn, có `sleep`/timeout tuỳ ý, hỏng khi chạy song song |
| `scripts/find_polluter.py` | một file/thư mục lạ xuất hiện sau khi chạy test mà không rõ test nào tạo |

| Pha | Việc chính | Đạt khi |
|---|---|---|
| 1. Nguyên nhân gốc | đọc lỗi, tái hiện, xem thay đổi, đo ranh giới, lần ngược | hiểu **cái gì** và **vì sao** |
| 2. So mẫu | đối chiếu mẫu đã biết, tìm ví dụ chạy được, liệt kê khác biệt | thấy khác biệt then chốt |
| 3. Giả thuyết | một giả thuyết, kiểm tối thiểu | giả thuyết đúng, hoặc có giả thuyết mới |
| 4. Sửa | test hỏng → một bản sửa → cả bộ xanh | lỗi hết, test hồi quy hỏng khi gỡ bản sửa |
