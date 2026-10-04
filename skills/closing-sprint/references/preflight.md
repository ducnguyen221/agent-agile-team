# Tiền kiểm bằng chứng

<!-- Ý khái niệm: kiểm bằng chứng trước cổng nghiệm thu, độ nghiêm theo cỡ việc và rủi ro. Viết lại phòng sạch ở
     SPR-04 (TK10) từ danh sách ý cụm danh từ. Bậc việc theo method/sizing.md. -->

> **Kết luận:** trước khi trình Cổng 2, Analyst chạy một lượt **tiền kiểm** để biết hồ sơ đã đủ bằng chứng
> chưa. Độ nghiêm đi theo bậc việc — rất nhỏ, nhỏ, vừa, lớn — và rủi ro chỉ nâng bậc, không hạ. Mỗi dòng của
> ma trận ghi rõ do **máy** (luật có thật trong `scripts/check.py`) hay do **tay** (người đọc) kiểm. Kết luận
> tiền kiểm dùng thang chung Đạt / Đạt có điều kiện / Không đạt và chỉ là đề xuất; Cổng 2 vẫn của người dùng.

## 1. Khi nào chạy

Sau khi kiểm định không còn Chặn hay Phải sửa chưa xử lý, và **trước** khi trình Cổng 2. Chạy lại khi mốc code
đổi sau lượt tiền kiểm: bằng chứng gắn với mốc ([method/evidence.md](../../../method/evidence.md) mục 3), mốc
đổi thì phần bị ảnh hưởng hết hạn. Tiền kiểm chạy `python scripts/check.py` trên thư mục sprint trước, rồi mới
đọc tay những dòng máy không bắt.

## 2. Bậc việc quyết độ nghiêm

Bậc lấy từ khoá `size` và `risk` ở frontmatter, theo [method/sizing.md](../../../method/sizing.md).

| Bậc | Hồ sơ | Kiểm định | Trần kết luận |
|---|---|---|---|
| Rất nhỏ | `SPRINT.md`, hai phần Kế hoạch và Kết quả | tự kiểm được nếu ghi "tự kiểm, chưa độc lập"; agent khác chạy thì bỏ ghi chú | tự kiểm → tối đa Đạt có điều kiện |
| Nhỏ | `SPRINT.md`, bốn phần | một reviewer | Đạt |
| Vừa | bốn file SPEC, PLAN, PROGRESS, REPORT | Business Reviewer và Tech Reviewer | Đạt |
| Lớn | bốn file, cộng mục đổi hợp đồng / giao diện, ADR, kế hoạch hoàn tác | hai reviewer, cộng thẻ chuyên đề theo `risk_tags` | Đạt |

**Rủi ro nâng, không hạ.** `risk: high` (có `risk_tags`) buộc bậc lớn: mỗi vùng rủi ro phải có thẻ chuyên đề đã
chạy và để lại `RF` hoặc `VR`; nếu đụng dữ liệu thật thì cần cả báo cáo diễn tập migration. Tiền kiểm gặp rủi ro
mới mà hồ sơ chưa khai (diff chạm file luật, workflow CI, secret, quyền) thì **nâng bậc ngay**, ghi dòng
`Phán quyết:` và chạy phần còn thiếu của bậc mới — không tiền kiểm theo bậc cũ cho xong. Diff ngắn không phải lý
do hạ bậc; hạ chỉ ở Cổng 1, do người dùng.

## 3. Ma trận cổng

Ký hiệu: **có** = bắt buộc ở bậc đó; **—** = không áp dụng ở bậc đó. Cột cuối: **máy** + tên luật chỉ khi luật có
thật trong bảng `RULES` của `scripts/check.py`; **tay** là việc đọc hồ sơ, đọc diff hoặc chạy lệnh.

| Kiểm | Rất nhỏ | Nhỏ | Vừa | Lớn | Ai kiểm |
|---|---|---|---|---|---|
| Mỗi `SC` có ít nhất một `VR` trong REPORT hoặc phần Kết quả | có | có | có | có | máy: `report-sc-without-vr` (chỉ thấy có hàng `VR` nhắc tới `SC`, không xét kết quả) |
| Các `VR` đó đang Đạt — không phải Chưa chạy hay Không áp dụng | có | có | có | có | tay |
| Mỗi `FR` có `VR` trỏ tới nó hoặc tới kịch bản con; không thì ghi `bỏ` hoặc `NOT_APPLICABLE` kèm lý do | có | có | có | có | máy: `report-fr-without-vr` khi hồ sơ là REPORT; trong `SPRINT.md` luật này không chạy → tay |
| `VR` có lệnh nguyên văn hoặc bước tái hiện, kết quả thật, mốc commit | có | có | có | có | tay |
| `VR` do agent khác người làm chạy | tự kiểm được, kèm ghi chú | có | có | có | máy chỉ so nhãn trong `roles` (`self-review`, `qa-not-independent`); phiên có thật là khác hay không → tay |
| Không còn Chặn mở | có | có | có | có | tay |
| Phải sửa còn mở: đã sửa, hoặc người dùng chấp nhận bằng câu ghi rõ | có | có | có | có | tay |
| Nên sửa không làm thì hoãn thành `CO` có chủ, mốc, kèm một dòng `RQ-` | nếu có | có | có | có | tay |
| Sửa lỗi hồi quy thì test đi đủ vòng gỡ sửa → hỏng → đặt lại → đạt | khi việc là sửa lỗi | khi sửa lỗi | khi sửa lỗi | khi sửa lỗi | tay |
| Không skip hay xfail, không nới linter hoặc test, không hạ ngưỡng coverage | có | có | có | có | tay; máy chỉ bắt ngưỡng đổi khỏi 80 mà thiếu lý do trong `.agile.json` (`config-invalid`) |
| Diff không chứa secret | có | có | có | có | tay (đọc diff) |
| CHANGELOG chỉ được thêm; version không bị tự đổi | nếu chạm | nếu chạm | có | có | tay (so diff) |
| Tài liệu đủ mục và câu kết luận đầu | theo hai phần | có | có | có | máy: `heading-missing`, `conclusion-missing` (chỉ thấy tiêu đề, không thấy nội dung) |
| Mã nhắc chéo đều có chỗ định nghĩa | có | có | có | có | máy: `xref-missing` |
| Có cách hoàn tác | một dòng | một dòng | các bước | kế hoạch hoàn tác, được xem lại ở Cổng 2 | tay (máy chỉ thấy tiêu đề mục) |
| Reviewer ghi phần **không** đánh giá, kể cả khi 0 phát hiện | nếu có reviewer | có | có, cả hai | có, cả hai và từng thẻ chuyên đề | tay |
| Thẻ chuyên đề theo `risk_tags` đã chạy, có `RF`/`VR` | — | — | — | có | tay |
| Mọi dòng `Phán quyết:` của PROGRESS đã gom vào Review & Retro | — | nếu có | có | có | tay |

## 4. Đọc ma trận

- **Còn Chặn mở thì Không đạt**, không cân nhắc thêm; quay lại vòng kiểm định.
- `SC` bắt buộc không có `VR` Đạt (kể cả Chưa chạy) cũng là Không đạt cho tới khi có bằng chứng mới.
- Nên sửa hoãn thì **phải** thành `CO` có chủ và có dòng `RQ-` trong sổ REQUESTS cùng lúc; hoãn mà không ghi chỗ
  nào là mất nợ, không phải Đạt có điều kiện.
- Máy báo xanh chưa đủ: các luật `máy` chỉ chứng minh hồ sơ **nhất quán** (có hàng, có mục, có chỗ định nghĩa),
  không chứng minh kết quả đúng. Dòng nào ghi "tay" thì phải mở bằng chứng ra đọc.
- Việc không áp dụng ở bậc đang xét ghi "—" trong lượt tiền kiểm, không bỏ im lặng.

## 5. Kết luận tiền kiểm và nơi ghi

Dùng đúng ba kết luận của thang chung ([method/severity.md](../../../method/severity.md) mục 2):

| Kết luận | Khi nào |
|---|---|
| Đạt | không Chặn, không Phải sửa mở; mọi `SC` có `VR` Đạt; mọi dòng bắt buộc của bậc đã qua |
| Đạt có điều kiện | không Chặn; còn nợ Nên sửa đã thành `CO`, hoặc Phải sửa được người dùng chấp nhận bằng câu ghi rõ, hoặc việc rất nhỏ tự kiểm |
| Không đạt | còn Chặn; hoặc `SC` bắt buộc thiếu `VR` Đạt; hoặc dòng bắt buộc của bậc còn thiếu mà không bù được |

Kết luận ghi ở **khoá `verdict`** trong frontmatter REPORT (hoặc `SPRINT.md`) với giá trị `pass`, `conditional_pass`
hoặc `fail`; câu `> **Kết luận:**` đầu tài liệu phải khớp với nó. Mục Kết quả kiểm định thêm một đoạn ngắn: kết
luận, dòng nào thiếu, điều kiện kèm theo. Lượt tiền kiểm chưa xong thì `verdict` giữ `pending`. Tiền kiểm **không**
ghi `gate_2`: đó là câu của người dùng ở Cổng 2.

Có điều kiện thì mỗi điều kiện đi kèm chủ và mốc. Không đạt thì chưa trình Cổng 2: quay lại vòng kiểm định, hoặc
nếu đã hết vòng thứ ba thì báo người dùng theo mục 6 của [method/process.md](../../../method/process.md).
