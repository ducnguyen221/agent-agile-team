---
name: eval-harness
description: Use when a feature that calls the product's own model (a prompt, a tool-using assistant, an agent chain) needs pass/fail criteria, a regression check after a prompt or model change, or someone claims "evals are green" or "pass rate went up". Not for pressure-testing a skill or a rule (that is `writing-skills`) and not for ordinary unit tests (`tdd`).
metadata:
  group: meta
  roles: [architect, qa]
source: [affaan-m/ECC skills/eval-harness/SKILL.md]
source_sha: [ef648e01899ba3e8dc6371642deaaf64b4477775]
license: [MIT]
rewrite_before_public: false
---

# Eval cho tính năng có gọi mô hình

> **Kết luận:** unit test không đo được thứ chạy bằng mô hình: kết quả **ngẫu nhiên**, **tốt dần hay xấu dần**
> theo prompt và phiên bản mô hình. Eval là "unit test" của phần đó, với bốn luật: **định nghĩa eval và ngưỡng
> trước khi viết** · chấm bằng **code trước**, mô hình sau, người cho phần bảo mật · mỗi ca chạy **nhiều lần** và
> đường tới hạn phải qua **mọi** lần · **tổng cao không bù hồi quy**. Số chưa đo là **Chưa chạy**, không phải Đạt.

## 1. Phạm vi — dùng skill nào

| Việc | Skill |
|---|---|
| tính năng của **sản phẩm** gọi mô hình: prompt, trợ lý có công cụ, chuỗi agent — đo chất lượng, hồi quy, so phiên bản mô hình | skill này |
| thử xem agent có **làm theo một skill hay luật** (RED không skill → GREEN có skill) | `writing-skills` |
| hàm, API, giao diện xác định | `tdd`, `e2e-testing` |
| ghi kết quả vào REPORT, hạn chế khi đóng sprint | `verify-before-done`, `closing-sprint` |

## 2. Định nghĩa trước khi viết

Eval nằm trong PLAN, cạnh `TK` làm ra tính năng; mỗi eval ghi **trước khi viết prompt hay mã**:

- **Loại:** *năng lực* (thử điều trước đây chưa làm được) hoặc *hồi quy* (điều đang chạy tốt phải còn nguyên).
  Đổi prompt hay mô hình luôn kèm eval hồi quy cho **bản đang chạy**; đường tới hạn (tiền, dữ liệu cá nhân,
  pháp lý) có nhóm ca riêng.
- **Bộ ca:** nhóm theo kiểu đầu vào; lấy từ **lỗi thật và phân bố production** (ngôn ngữ khác, đầu vào rất dài,
  rỗng, nội dung cố ép mô hình), không chỉ vài ca sạch tự viết. Ca đã dán vào prompt làm ví dụ **không tính**:
  cần tập giữ riêng chưa từng vào prompt.
- **Người chấm:** mục 3. **Ngưỡng:** mục 4, ghi **trước khi chạy**; ngưỡng đặt sau khi thấy số là chỉnh bia.
- **Đường cơ sở:** bản đang chạy (SHA hoặc tên mốc) chạy trên **cùng** bộ ca, cùng người chấm.
- Đổi ngưỡng hoặc đổi kiểu chỉ số giữa chừng = một **phán quyết** ghi lý do (`Phán quyết: <gì> — <vì sao> — <sai
  thì tốn gì>`) và báo ở Cổng, không đổi lặng lẽ để qua.

## 3. Bốn loại người chấm

| Loại | Dùng cho | Luật |
|---|---|---|
| **code** | thứ đếm và đối chiếu được: số từ, còn đủ số tiền/mã, đúng công cụ và tham số, schema | **mặc định**; xác định, rẻ, lặp lại được |
| **quy tắc** | regex, nhãn thuộc tập hợp lệ, không chứa dữ liệu cấm | như code |
| **mô hình** (trọng tài) | phần mờ: "đúng ý", văn phong | rubric có mốc từng điểm; **ghim phiên bản** trọng tài (không tên `latest`); hiệu chuẩn với mẫu người chấm; không phải chính mô hình sinh; chạy lại cùng đầu vào mà điểm lệch → chưa đủ làm cổng |
| **người** | bảo mật, dữ liệu cá nhân, hậu quả khó đảo ngược, ca mơ hồ | duyệt bộ đáp án và ca khó; **không thay bằng trọng tài mô hình** |

Ca "lộ dữ liệu người khác" chấm bằng **code**: dữ liệu giả có dấu hiệu nhận biết, đầu ra chứa bất kỳ giá trị
của người không phải người hỏi là trượt; thêm người duyệt. Phòng thủ thật nằm ở tầng công cụ (lọc dữ liệu trước
khi đưa cho mô hình); eval kiểm chứng điều đó, không thay thế nó.

## 4. Chạy mấy lần, ngưỡng nào

Mô hình ngẫu nhiên: **một lần qua không phải bằng chứng**. Mỗi ca chạy **k ≥ 3** lần.

| Chỉ số | Nghĩa | Hợp với |
|---|---|---|
| `pass@k` | ít nhất 1 trong k lần qua | eval **năng lực** — có thể thử lại và chọn kết quả tốt |
| `pass^k` | **cả k** lần đều qua | eval **hồi quy** và đường tới hạn — "không bao giờ làm sai" |

- Ngưỡng mặc định: năng lực `pass@3 ≥ 90 %`; hồi quy đường tới hạn `pass^3 = 100 %`. Dùng `pass@k` cho đường
  tới hạn là chọn sai kiểu: "ca nào cũng qua ít nhất một lần" che ca chập chờn. Báo **cả hai** con số kèm số ca.
- Ca chập chờn trên đường tới hạn là lỗi tái hiện chưa rõ nguyên nhân (skill `debugging`), không phải nhiễu để
  lấy trung bình. "Thử lại tới khi qua" không phải cách qua.
- Mẫu nhỏ (vài ca) không cho tỉ lệ: ghi số ca, mở rộng nhóm đó trước khi tin con số.

## 5. Chuỗi agent và công cụ

- **Chấm vết, không chỉ câu cuối.** Đáp án cuối đúng có thể do may: gọi công cụ sai thứ tự (hoàn tiền trước khi
  kiểm danh tính), bỏ qua kết quả công cụ rồi lấy dữ liệu từ nội dung khách tự khai, gọi lặp cùng tham số. Chấm
  riêng: đúng công cụ · đúng tham số · đúng thứ tự · dùng kết quả công cụ · số lần gọi (chỉ số chi phí). Thêm ca
  **bẫy** (nội dung ghi số đơn của người khác) để lộ lỗi bỏ qua kết quả. Ca đúng đáp án mà sai quy trình **trượt**.
- **Cố định đầu ra công cụ** cho eval hồi quy (ghi-lại-phát-lại, hoặc dữ liệu thử có phiên bản): dữ liệu môi
  trường đổi theo đêm sẽ làm tỉ lệ qua nhảy nhiều chục điểm mà không liên quan prompt. Eval chạy trên môi
  trường thật là lượt **tích hợp** riêng, không dùng để so hai bản mã. Tăng số lần chạy chỉ giảm nhiễu lấy mẫu,
  không loại nhiễu môi trường.
- Hành động không đảo ngược (hoàn tiền, gửi thư, xoá) trong eval: **mô phỏng** công cụ, không gọi thật.

## 6. Điểm trôi và nhiễu

Điểm tụt mà prompt không đổi một chữ → nghi **trọng tài hoặc mô hình thử đổi phiên bản** trước khi nghi prompt.
Tách nguyên nhân bằng cách chạy lại ghim phiên bản cũ trên cùng ca; chưa tách thì **không rollback** và không ghi
Chặn cho prompt. Mỗi bản ghi chạy lưu: bản mã/prompt, bộ ca, **phiên bản mô hình và trọng tài**, tham số, đầu ra
và điểm **từng lần**, ngày. Chênh nhỏ hơn dải dao động giữa các lần chạy cùng cấu hình **không đọc được**.

## 7. Ghi `VR` và báo Cổng

- Dòng `VR` ghi: số theo **nhóm** (không chỉ tổng) · số lần chạy · `pass@k` và `pass^k` · so với đường cơ sở ·
  môi trường (mô hình, trọng tài, bản mã, ngày) · lệnh đã chạy.
- **Tổng cao hơn không bù hồi quy** ở nhóm đường tới hạn: nhóm đó tụt ổn định qua các lần chạy thì `SC` không Đạt
  dù tổng tăng; ghi `RF` và giữ trên bảng tổng, không chôn trong trung bình.
- **Chi phí và độ trễ** (token, p95) ghi riêng; "rẻ hơn" hay "chậm hơn" là **đánh đổi do người dùng quyết** ở
  Cổng 2, kèm lời duyệt nguyên văn; không dùng để gỡ hồi quy.
- Eval do **agent khác** người làm tính năng chạy và chấm. Chưa chạy, chạy một lần, hay chưa có ngưỡng đặt trước
  → **Chưa chạy**, không bao giờ là Đạt.

## 8. Lưu ở đâu

Bộ ca, ngưỡng, đường cơ sở và nhật ký chạy nằm **trong repo, có phiên bản, cạnh mã** (thư mục có git, ví dụ
`evals/<tính năng>/`), không ở trang ghi chú ngoài. Eval **nhanh** thì mới được chạy: bộ chậm tách thành nhóm
nhanh (mỗi lần đổi) và nhóm đầy đủ (trước phát hành).

## 9. Cờ đỏ

| Ý nghĩ | Thực tế |
|---|---|
| "Ba ca chạy tay đẹp, ghi Đạt" | một lần qua của hệ ngẫu nhiên không là bằng chứng; Chưa chạy |
| "Viết prompt trước, eval và ngưỡng sau cho hợp lý" | ngưỡng đặt sau khi thấy số là chỉnh bia; định nghĩa trước |
| "12/12 xanh" | ca đã nằm trong prompt thì là ôn tủ; cần tập giữ riêng |
| "`pass@3` = 100 %, vượt ngưỡng" | đường tới hạn cần `pass^3`; che ca chập chờn |
| "Tổng tăng, ship" | nhóm tới hạn tụt ổn định là hồi quy; tổng không bù |
| "Điểm tụt, rollback prompt" | prompt không đổi thì nghi trọng tài trôi; tách trước |
| "Đáp án cuối đúng, khỏi soi log" | đúng do may; chấm vết công cụ |
| "Mô hình không ổn định, tăng số lần chạy" | có thể là dữ liệu môi trường; cố định đầu ra công cụ |
| "Trọng tài mô hình chấm cả dữ liệu cá nhân" | code + người chấm; trọng tài không phải cổng bảo mật |
