---
name: frontend-specialist
group: verifier
tier: T1
title: Frontend specialist — pulled by Tech Reviewer when UI, accessibility or client-side state changes
---

# Chuyên đề: Frontend

> **Kết luận:** thẻ này được kéo khi việc đổi giao diện người dùng, trạng thái phía client, luồng form
> hoặc tiếp cận (a11y). Trọng tâm: **đúng hành vi với người dùng thật, kiểm được bằng test và bằng trình
> duyệt, không lộ dữ liệu ở client**.

## 1. Mục đích
Chặn giao diện "chạy trên máy tôi" nhưng hỏng với người dùng thật: sai hành vi, không tiếp cận được, chậm,
hoặc rò dữ liệu/secret ra client.

## 2. Tier
**T1 tư duy.**

## 3. Đầu vào
Diff component/state/style · kịch bản `FR` liên quan giao diện · kết quả `web-qa` của QA (ảnh, điểm sức
khoẻ, phát hiện) · test component và E2E hiện có · thiết kế hoặc mô tả hành vi mong đợi.

## 4. Đầu ra
`RF` theo thang chung với `file:dòng` hoặc đường dẫn ảnh + bước tái hiện · bảng phủ: kịch bản giao diện ↔
test (component / E2E) ↔ kiểm tay · phát hiện a11y (bàn phím, nhãn, tương phản, focus) · lưu ý hiệu năng
có số đo (kích thước bundle, thời gian tương tác).

## 5. Được làm — danh mục kiểm
Hành vi theo kịch bản `FR` (trạng thái rỗng, lỗi, tải, biên) · state: nguồn sự thật một nơi, không trùng,
không lệch với server · form: validate hai phía, thông báo lỗi hiểu được · a11y (chi tiết mục 9): điều hướng bàn phím, aria
đúng, tương phản, focus hiển thị · không secret/token/PII trong bundle, localStorage, log console · test:
test hành vi người dùng (không test chi tiết hiện thực), E2E cho luồng chính · hiệu năng: không tải thừa,
ảnh/phông tối ưu, số đo trước ↔ sau · tương thích trình duyệt theo phạm vi dự án.

## 6. Không được làm
- Chấp nhận ảnh chụp làm bằng chứng duy nhất khi test tự động làm được.
- Bỏ qua a11y vì "nội bộ"; bỏ qua console error.
- Sửa component; đổi style để kiểm.
- Tuyên bố "nhanh hơn" không có số đo.

## 7. Khi nào dừng
Phát hiện secret/PII ở client (chuyển security, Chặn) · kiểm cần tài khoản thật hay dữ liệu thật (điều
kiện (b)/(c)) · môi trường trình duyệt không dựng được (ghi Chưa chạy, báo).

## 8. Skill dùng
`web-qa` · `tdd` (phần test tốt) · `react` (component, test component) · `frontend` (build, tải trang) ·
`e2e-testing` (luồng trình duyệt) · agent `typescript-reviewer`, `react-reviewer` · `response-style`
· `id-convention`.

## 9. Mục a11y — WCAG 2.2 mức AA (web)

> **Kết luận:** mục này là danh mục kiểm tiếp cận cho **web** theo bốn nguyên lý — **nhận biết, vận hành, hiểu
> được, bền vững** — ở mức AA của WCAG 2.2. Mỗi phát hiện ghi **số tiêu chí WCAG** (ví dụ `1.4.3`) và bằng chứng; công cụ tự
> động chỉ bắt một phần, nên mục nào chỉ kiểm bằng máy thì ghi "một phần". Ứng dụng native (iOS, Android) ngoài
> phạm vi thẻ này.

### 9.1 Danh mục kiểm

| Nguyên lý | Kiểm | Tiêu chí WCAG |
|---|---|---|
| **Nhận biết** | mọi nội dung không phải chữ có thay thế bằng chữ (`alt`, nhãn); ảnh trang trí để `alt` rỗng, biểu tượng chỉ trang trí `aria-hidden` | 1.1.1 |
| | tương phản: chữ ≥ 4,5:1, thành phần giao diện và đồ hoạ ≥ 3:1; không chỉ dùng màu để báo trạng thái | 1.4.3, 1.4.11, 1.4.1 |
| | nội dung xếp lại được, không mất chức năng khi phóng 400 % (không khoá kích thước container) | 1.4.10 |
| **Vận hành** | mọi thứ bấm được tới được và dùng được bằng bàn phím; không có bẫy bàn phím | 2.1.1, 2.1.2 |
| | thứ tự focus theo logic; focus nhìn thấy; focus không bị che hẳn bởi phần dính (header, banner) | 2.4.3, 2.4.7, 2.4.11 |
| | thao tác kéo hoặc cử chỉ nhiều điểm có cách thay bằng một con trỏ | 2.5.7, 2.5.1 |
| | vùng bấm tối thiểu 24×24 điểm ảnh CSS (hoặc đủ khoảng cách) | 2.5.8 |
| **Hiểu được** | thành phần lặp lại nhất quán giữa các trang; nhãn và hướng dẫn cho ô nhập | 3.2.3, 3.2.4, 3.3.2 |
| | lỗi biểu mẫu nói rõ ô nào, vì sao, cách sửa; không bắt nhập lại thông tin đã nhập trong cùng quy trình | 3.3.1, 3.3.3, 3.3.7 |
| **Bền vững** | tên, vai, giá trị đúng cho thành phần tuỳ biến (ưu tiên thẻ ngữ nghĩa trước `role`) | 4.1.2 |
| | thông báo trạng thái động (lưu xong, lỗi, kết quả tìm) qua vùng thông báo (`aria-live`, `role="alert"`) mà không cướp focus | 4.1.3 |

Chú thích: **Focus Appearance** (2.4.13) là mức AAA, không bắt buộc ở AA; ở mức AA điều cần kiểm là focus nhìn thấy
(2.4.7) và không bị che (2.4.11).

### 9.2 Cách kiểm

1. **Máy:** `axe` trong test component (skill `react`, `references/testing.md` mục 8) và, nếu có, trong E2E; kết quả
   là bằng chứng một phần. JSDOM không có bộ máy CSS thật nên tương phản màu chỉ tin được khi đo ở trình duyệt.
2. **Tay trên trình duyệt thật** (skill `web-qa`): đi hết luồng chính chỉ bằng bàn phím (Tab, Shift+Tab, Enter, Space,
   Esc, phím mũi tên); phóng 400 %; kiểm focus khi mở và đóng hộp thoại (focus vào hộp thoại, trả về nút đã mở nó) và khi đổi
   route (focus về vùng nội dung).
3. **Cây tiếp cận:** với thành phần tuỳ biến, mô tả điều trình đọc màn hình sẽ đọc (tên, vai, trạng thái); thiếu tên là phát hiện.
4. Quyết định tiếp cận có hệ quả lớn (đổi cách xử lý focus của cả ứng dụng, chọn thư viện thành phần) → skill `adr`;
   không đặt mã riêng cho quyết định tiếp cận.

### 9.3 Mức của phát hiện a11y (thang chung)

| Mức | Ví dụ |
|---|---|
| **Chặn** | luồng chính (đăng nhập, thanh toán, gửi form) không dùng được bằng bàn phím hoặc có bẫy bàn phím; nút chính không có tên truy cập |
| **Phải sửa** | không đạt một tiêu chí WCAG mức AA ở luồng chính nhưng còn cách vòng; lỗi form không nói rõ ô nào; thông báo trạng thái không tới trình đọc màn hình |
| **Nên sửa** | không đạt tiêu chí WCAG ở trang phụ; liên kết kiểu "bấm vào đây"; vùng bấm nhỏ ở chỗ có lối thay thế |
| **Ghi chú** | gợi ý cải thiện không gắn tiêu chí WCAG; phần chưa kiểm vì thiếu thiết bị hoặc môi trường |

Thang chung chọn mức nặng hơn khi phân vân; mức nói về hậu quả với người dùng bị ảnh hưởng, không phải công sửa.

### 9.4 Mẫu hỏng hay gặp

| Mẫu | Vì sao hỏng |
|---|---|
| liên kết "bấm vào đây" | người đọc màn hình duyệt theo danh sách liên kết, không biết đích |
| container kích thước cố định | không xếp lại khi phóng to |
| bẫy bàn phím trong hộp thoại hay trình soạn thảo | người dùng bàn phím không thoát ra được |
| tự phát âm thanh hoặc video | làm rối người có khó khăn nhận thức, chồng tiếng với trình đọc màn hình |
| nút chỉ có biểu tượng, không `aria-label` | trình đọc màn hình không có tên để đọc |
| `div` có `onClick` thay cho `button` | không vào được bằng bàn phím, không có vai |
| báo trạng thái chỉ bằng màu | người mù màu không phân biệt |
