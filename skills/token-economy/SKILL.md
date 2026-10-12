---
name: token-economy
description: Use when a session is long or the context window is filling, a command or file produces large output, a subagent must report back or be briefed, a phase boundary (SPEC → PLAN → PROGRESS → REPORT) is crossed, or a task starts in a codebase whose files and terms are unknown, or anyone is about to claim a token or cost saving.
metadata:
  group: communication
  roles: [all]
source: ["affaan-m/ECC skills/context-budget/SKILL.md (via local distill)", "affaan-m/ECC skills/strategic-compact/SKILL.md", "JuliusBrussee/caveman (idea only: terse agent-to-agent register)", "ryoppippi/ccusage (called only)", "yamadashy/repomix (called only)", "affaan-m/ECC skills/iterative-retrieval/SKILL.md"]
source_sha: [c70874fae9eb0e5ad0365beb7e2955899fd1d30f, c70874fae9eb0e5ad0365beb7e2955899fd1d30f, f5d729488caa8f6a5b6c8086fe2cccd3e8a63f91, 1597d65298b6ad93abc8fa174c3bcf78ae86e27a, 0b3f82b401bbc520fd1aca67c06d24e40a868d3e, ef648e01899ba3e8dc6371642deaaf64b4477775]
base_sha: 3599962a013653191c41676021c7e7dc519ee351
license: [MIT, MIT, "Apache-2.0 (idea only, no text copied)", "MIT (called only, not copied)", "MIT (called only, not copied)", MIT]
rewrite_before_public: false
---

# Tiết kiệm token

> **Kết luận:** hai luồng tối ưu khác nhau — cho **người** thì tối ưu để hiểu nhanh, giữa **agent** thì
> tối ưu token mạnh. Trạng thái sống trong **file**, không trong ngữ cảnh; nạp đúng lúc, truyền con trỏ
> thay nội dung; lọc tại nguồn; chưa biết cần tệp nào thì truy xuất **theo vòng có trần** (mục 7); và **không tuyên bố tiết kiệm khi chưa có cặp số đo trước/sau** — kể cả
> dưới nhãn "ước tính".

## 0. Ngân sách không thay routing hoặc bằng chứng

Dùng `method/task-routing.md` mục 1–5: sáu trục có giá trị/ordinal/nguồn, difficulty từ scope/plan/complexity,
effort mặc định `medium` (ordinal 2), kết hợp risk floor và capability; pin người dùng chỉ thắng field đã
chỉ định, không hạ risk/gates hoặc tự đổi baseline vai. Ngân sách ít không tự suy thành tier thấp, effort thấp
hay parallel; topology cần module/ownership/overhead và bằng chứng lợi ích hoặc override hợp lệ. Notice trước
assignment/đổi cấu hình giữ actor/harness/vai/tier/model/effort/phạm vi/lý do/nguồn và requested/effective/actual;
capability, access và runtime là ba bằng chứng riêng, thiếu thì unknown. Nén context vẫn giữ lỗi, counters sửa
của assignment và tổng lịch sử, pin, quyền bàn giao, gates và rollback. Usage thiếu là unknown, không phải 0;
không suy tiết kiệm từ độ ngắn văn bản. Muốn so chi phí phải có cặp đo cùng đơn vị việc và chất lượng theo mục 5;
chưa có dữ liệu thì chỉ đề xuất cách đo, không tự chạy provider hoặc mở pilot.
## 1. Mười quy tắc

| # | Quy tắc | Làm cụ thể |
|---|---|---|
| 1 | **Kết luận trước, xếp lớp** | câu đầu là kết luận; chi tiết ở lớp hai hoặc trong file (skill `response-style`) |
| 2 | **Bất khả xâm phạm** | số + đơn vị, mã lỗi, stack trace then chốt, chữ phủ định, đường dẫn, phiên bản — không bao giờ bị nén mất |
| 3 | **Bỏ dẫn nhập, tường thuật, recap** | không "em đã…", không kể bước gọi tool, không tóm tắt lại cuối |
| 4 | **Lọc tại nguồn** | `--short`, `-q`, `--json` + lọc trường, `grep`/`tail`/`head`, đọc file theo offset; đếm trước khi đọc |
| 5 | **Output lớn đã lưu file → đọc chọn lọc** | log >200 dòng: lưu `.tmp/`, trỏ đường dẫn, chỉ trích dòng then chốt; không dán lại |
| 6 | **Việc nhiều output giao subagent** | subagent trả tóm tắt + con trỏ (mục 3), không trả transcript |
| 7 | **Bảng khi ≥3 mục** | dưới đó dùng câu; không bảng tóm tắt lặp |
| 8 | **Hai giọng** | chat kỹ thuật gọn; tài liệu bàn giao cho người không chuyên viết câu đầy đủ |
| 9 | **Kiểm ngược** | đọc riêng kết luận: người đọc hành động và hoàn tác được không? Không → thiếu, thêm; có thừa → cắt |
| 10 | **Có số đo mới có luật** | mọi tuyên bố "tiết kiệm X %" phải kèm cặp số trước/sau cùng đơn vị việc (mục 5) |

## 2. Trạng thái sống trong file, compact tại ranh giới pha

- PROGRESS và ba sổ gốc là nguồn sự thật; ngữ cảnh phiên chỉ là bộ nhớ làm việc. Sau mỗi `TK`: ghi file
  trước, rồi mới làm tiếp.
- **Ranh giới pha** SPEC → PLAN → PROGRESS → REPORT là lúc nén ngữ cảnh (compact). Trước khi nén:
  (1) mọi quyết định, mã, số liệu, câu duyệt nguyên văn đã nằm trong file; (2) bản nháp bị thay đã đánh
  dấu `superseded`; (3) tóm tắt nén chỉ gồm: mục tiêu sprint, cổng đã qua, quyết định chính, **đường dẫn**
  tới SPEC/PLAN/PROGRESS, hành động kế tiếp. Không chép nội dung tài liệu vào tóm tắt.
- Sau nén: nạp lại **chỉ** PROGRESS và mục PLAN đang làm; SPEC chỉ khi cần đối chiếu một điểm.
- Ngữ cảnh đầy >80 % giữa pha mà chưa tới ranh giới: ghi trạng thái ra PROGRESS ngay, rồi nén; việc
  dang dở ghi "đang làm, mốc commit X".

## 3. Giữa agent: khung báo cáo 4 phần

Báo cáo từ subagent về điều phối, và từ điều phối lên sổ:

```
Kết quả: <xong / xong có lo ngại / bị chặn / thiếu ngữ cảnh> — <một câu>
Chứng cứ: <lệnh → kết quả then chốt (số, mã thoát)>; <file:dòng đã đổi>; log đầy đủ: <đường dẫn>
Còn mở: <việc ngoài phạm vi phát hiện được, giả định đã đặt, lo ngại> (hoặc "không")
Cần người: <quyết định cần người dùng> (hoặc "không")
```

Mặc định **≤2.000 token** (≈15 dòng với việc thường); câu gọn kiểu "chủ ngữ – động từ – số"; giữ nguyên
số và chữ phủ định; không mở đầu, không lời cảm ơn, không lặp brief.

**Brief cho subagent** đi chiều ngược: mục tiêu một câu · đường dẫn + **mục** cần đọc (`SPEC.md` mục
`FR2.2`, không phải "đọc SPEC") · giao diện dùng/sinh · phạm vi file được sửa · điều cấm · cách báo cáo
(khung trên) · khối văn phong rút gọn. Brief ≤40 dòng; không dán lịch sử phiên, không dán log, không
chép nội dung tài liệu mà subagent tự đọc được.

## 4. Nạp đúng lúc cần

- Truyền **đường dẫn và mã** (`PLAN.md` mục `TK2`, `RF3`), không dán nội dung.
- Đọc file lớn: đếm dòng → `grep -n` tìm mốc → đọc theo offset/limit quanh mốc. Log hàng vạn dòng: thu hẹp
  theo thời gian/từ khoá trước, tìm lỗi **đầu tiên**, không đọc tuần tự.
- Lệnh nhiều output: chuyển sang chế độ ngắn hoặc JSON rồi lọc trường; output >30 KB lưu file.
- Nén repo cho agent (khi thật cần) bằng công cụ chạy qua `npx` tạm, không cài global.
- Không nạp lại tài liệu đã nằm trong ngữ cảnh; không mở lại skill đã đọc trong cùng pha.
- Chưa biết cần tệp nào hay codebase gọi khái niệm bằng tên gì: truy xuất theo vòng (mục 7), không đọc hết, không đoán.

## 5. Đo trước khi tuyên bố

- Thước đo: tổng token theo ngày hoặc theo phiên từ công cụ thống kê dùng dữ liệu phiên của harness
  (ví dụ `npx ccusage@latest daily --json`); hoặc bộ đếm `/usage`, `/context` của harness.
- **Chuẩn hoá theo việc**: token / sprint hoặc token / phiên cùng loại việc, không so hai ngày có khối
  lượng khác nhau.
- Cặp số: trước (≥7 ngày hoặc ≥5 việc cùng loại) ↔ sau (cùng cỡ). Giữ thay đổi nếu giảm ≥10 % **và** rà
  ≥20 phản hồi mẫu không mất số liệu / mã lỗi / chữ phủ định.
- **Chưa có cặp số → không có con số.** Bị ép "cứ ước lượng, ghi chữ ước tính cũng được" → trả lời: chưa
  đo, con số nào lúc này cũng là bịa; đưa **thời điểm có số** (ví dụ: chạy công cụ đo ngay, có số sau
  N phút nếu còn dữ liệu ngày trước; nếu không, sau N ngày) và **câu dùng được ngay** không chứa phần
  trăm ("đã bật, đang đo, số có ngày X"). Ngân sách thì tính tiết kiệm = 0 tới khi có số.
- Mỗi sprint ghi tổng token phiên vào REPORT làm mốc, dù không có tuyên bố nào.

## 6. Tự kiểm trước khi gửi

- Người nhận là ai? Giọng đúng chưa (mục 8 bảng 1)?
- Câu đầu là kết luận? Có dẫn nhập/recap để cắt không?
- Có log/dữ liệu dài nào dán vào mà một đường dẫn thay được không?
- Mọi số còn đơn vị, mọi "không/chưa/chỉ" còn nguyên?
- Có con số tiết kiệm nào không đi kèm cặp số đo không?

## 7. Truy xuất lặp — khi chưa biết cần ngữ cảnh nào

Dùng khi giao việc (hay tự làm) trong codebase lạ: không đoán trước được tệp nào liên quan và dự án gọi khái niệm
bằng tên gì. Ba cách sai: **đọc hết** (tràn ngữ cảnh), **không cho gì** hay kết luận "chưa có" từ lần tìm đầu
(thiếu), **đoán** (thường sai). Thay bằng vòng ngắn, **tối đa 3 chu kỳ** rồi đi tiếp:

1. **Truy vấn rộng:** từ khoá theo ý định + `ls` cấu trúc thư mục; bỏ ngay thư mục chắc chắn không liên quan
   (build, vendor, tệp sinh tự động).
2. **Đánh giá:** mỗi tệp ứng viên một mức — **cao** (cài đúng việc) · **vừa** (kiểu, mẫu liên quan) · **thấp** (chỉ
   nhắc qua) · **loại** — và ghi **lỗ hổng** còn thiếu (nó gắn vào đâu, cấu hình ở đâu, test theo quy ước nào).
3. **Tinh chỉnh:** thêm **từ vựng lấy từ chính codebase** (tìm "rate limit" ra 0 kết quả mà thư mục có
   `throttle.ts` → đổi sang `throttle`), thêm mẫu đường dẫn từ tệp mức cao, loại hẳn tệp mức loại, nhắm vào lỗ
   hổng. Truy vấn ra 0 kết quả chỉ nói **từ khoá sai**, không nói "chưa có".
4. **Lặp hoặc dừng.** Dừng khi đã có vài tệp mức cao và hết lỗ hổng then chốt ("đủ tốt": ba tệp cao hơn mười tệp
   nhạt), hoặc hết 3 chu kỳ.

Hết trần mà còn thiếu một mảnh: **không đọc cả thư mục thay cho**; giao việc kèm mảnh thiếu ghi thành giả định
(`ASSUMPTION`) hay câu hỏi (`CQ`), cho subagent tự truy xuất tiếp **một** vòng có trần; mảnh thiếu mà đổi tiêu chí
thành công thì hỏi người dùng. Kết quả đi vào brief là **con trỏ**: `file:dòng` + mức + thuật ngữ đã học (mục 3 và 4),
không phải nội dung. Việc truy xuất nhiều output giao subagent, trả về danh sách tệp kèm mức và lỗ hổng.
