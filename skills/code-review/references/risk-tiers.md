# Bậc rủi ro — người duyệt đọc gì ở Cổng 2

> **Kết luận:** bậc xếp theo **thay đổi** (path chạm và `risk_tags`), không theo ai làm; phân vân → bậc cao. Không có bậc
> "không cần người": mọi sprint có Cổng 2. Kết luận Đạt của agent là kết luận kiểm định, không phải lời duyệt; lời duyệt
> của người gắn với `sha7` đã trình.

## 1. Ba bậc

| Bậc | Khi nào | Người duyệt đọc ở Cổng 2 | Kiểm định tối thiểu |
|---|---|---|---|
| thấp | chỉ tài liệu, chữ, test thêm; `risk_tags` rỗng; không chạm path luôn-cần-người | Kết luận REPORT · Tóm tắt cho người không chuyên · bảng `VR` | một reviewer khác người làm |
| vừa | đổi hành vi thường; `risk_tags` rỗng | như trên · `RF` còn mở và `RF` bị bác · Rủi ro còn lại · Cách hoàn tác | Business Reviewer và Tech Reviewer |
| cao | `risk_tags` khác rỗng, hoặc chạm path luôn-cần-người | như trên · diff thật của các path đó · kết quả lượt bảo mật hay `dual-review` · từng `RF` bị bác kèm lý do | thêm `dual-review` khi `rules`, `secret`, `auth` |

## 2. Path luôn cần người

Diff chạm một trong các path dưới đây thì bậc là **cao**, bất kể cỡ sprint:

- file luật: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, thư mục luật của harness
- workflow CI
- cấu hình hook và harness
- trình cài, script phát hành, manifest có version
- `REVIEW.md`
- mã xử lý secret và xác thực

`REVIEW.md` của repo có thể **bổ sung** danh sách này (mục "Path luôn cần người đọc"), không thu hẹp nó.

## 3. Dòng lời trình

Lời trình Cổng 2 có đúng một dòng, đặt trước danh sách `RF`:

`Bậc duyệt: <thấp | vừa | cao> — <lý do> — đọc: <danh sách>`

Ví dụ: `Bậc duyệt: cao — chạm .github/workflows/verify.yml — đọc: diff verify.yml, RF2 bị bác, cách hoàn tác`.

- Phân vân giữa hai bậc → chọn bậc cao hơn và nói vì sao ngay trong dòng lý do.
- Reviewer hay agent T1 kết luận Đạt: ghi đó là **kết luận kiểm định**. Có commit sau `sha7` đã trình thì phần đổi cần
  duyệt lại.
