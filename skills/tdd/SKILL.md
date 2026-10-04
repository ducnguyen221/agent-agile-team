---
name: tdd
description: Use when implementing any feature, bug fix, refactor or behavior change, before writing implementation code; also when writing or changing a test, adding a mock or test helper, or deciding whether a change is really green.
metadata:
  group: technique
  roles: [implementer, qa]
source: [obra/superpowers skills/test-driven-development/SKILL.md, obra/superpowers skills/test-driven-development/writing-good-tests.md, obra/superpowers-skills skills/testing/testing-anti-patterns/SKILL.md]
source_sha: [8ca22dba9a94f28898bbce59f2537ff4d87c747d, 8ca22dba9a94f28898bbce59f2537ff4d87c747d, cdcd624ad3fd8026deb692e565351854569798dd]
license: [MIT, MIT, MIT]
rewrite_before_public: false
---

# Phát triển hướng kiểm thử (TDD)

> **Kết luận:** viết test trước, **nhìn nó hỏng đúng lý do**, viết mã tối thiểu cho nó đạt, rồi dọn.
> Chưa nhìn test hỏng thì không biết test có bắt đúng thứ cần bắt. "Xanh" nghĩa là **cả bộ test** của dự
> án xanh, không phải file test vừa viết. Mã viết trước test thì xoá, làm lại từ test.

## 1. Luật sắt

```
KHÔNG CÓ MÃ SẢN PHẨM NÀO KHI CHƯA CÓ MỘT TEST HỎNG TRƯỚC
```

Lỡ viết mã trước test → **xoá**, bắt đầu lại từ test. Không giữ làm "tham khảo", không "chỉnh lại" trong
lúc viết test, không mở ra xem. Xoá là xoá. Làm sai chữ của luật là làm sai tinh thần của luật.

**Áp dụng:** tính năng mới, sửa lỗi, refactor, đổi hành vi.
**Ngoại lệ** (prototype bỏ đi, mã sinh tự động, file cấu hình) chỉ hợp lệ khi đã nằm sẵn trong lời giao
hoặc PLAN (`DN` đã duyệt). Agent không tự cấp ngoại lệ cho mình.

## 2. Vòng Đỏ – Xanh – Dọn

| Bước | Làm | Kiểm bắt buộc |
|---|---|---|
| **Đỏ** | Một test tối thiểu cho **một** hành vi; tên nói hành vi; dùng mã thật (mock chỉ khi không tránh được) | Chạy test: nó **hỏng** (không phải lỗi cú pháp/import), thông báo hỏng đúng dự kiến, hỏng vì tính năng chưa có |
| **Xanh** | Mã đơn giản nhất cho test đạt. Không thêm tuỳ chọn, không refactor chỗ khác, không "tiện tay cải thiện" | Chạy **cả bộ test** của dự án: test mới đạt, test cũ vẫn đạt, output sạch (không lỗi, không cảnh báo mới) |
| **Dọn** | Chỉ sau khi xanh: bỏ trùng lặp, đặt lại tên, tách hàm phụ | Vẫn xanh cả bộ; không thêm hành vi |

- Test **đạt ngay** khi vừa viết → bạn đang test hành vi đã có; sửa test.
- Test **lỗi** (không phải hỏng) → sửa lỗi, chạy lại tới khi hỏng đúng lý do.
- Test hỏng sau khi viết mã → sửa **mã**, không sửa test.
- Test khác hỏng → sửa ngay, kể cả lỗi không do mình gây ra: ghi tên nó vào báo cáo. Một test đỏ đã thấy
  mà không báo là báo cáo sai do bỏ sót.

**"Xanh" = cả bộ.** Phạm vi việc giới hạn **thứ phải giao**, không giới hạn **thứ phải kiểm**. Trước khi
gọi là xong, chạy lệnh test của dự án (`pytest`, `npm test`, `cargo test`… — lệnh dự án dùng) dù brief chỉ
nói một file. Bằng chứng ghi PROGRESS: lệnh + kết quả mới chạy (skill `verify-before-done`).

Ví dụ một vòng sửa lỗi (lỗi: email rỗng vẫn được nhận):

```python
# Đỏ
def test_rejects_empty_email():
    result = submit_form({"email": ""})
    assert result.error == "Email required"
```

```
$ pytest -q
FAILED test_form.py::test_rejects_empty_email - AssertionError: assert None == 'Email required'
```

```python
# Xanh — vừa đủ
def submit_form(data):
    if not (data.get("email") or "").strip():
        return FormResult(error="Email required")
    ...
```

```
$ pytest -q
112 passed in 3.41s
```

Dọn: tách hàm kiểm nhiều trường nếu thật cần.

## 3. Test tốt

| Tiêu chí | Tốt | Xấu |
|---|---|---|
| Tối thiểu | Một hành vi. Tên có chữ "và" → tách | `test_validates_email_and_domain_and_whitespace` |
| Rõ | Tên mô tả hành vi | `test_1` |
| Lộ ý | Cho thấy API mong muốn | Che mất mã phải làm gì |

Khi viết hay sửa bất kỳ test nào, mock hay hàm phụ cho test: đọc
[references/good-tests.md](references/good-tests.md). Bốn điều cốt lõi:
- Gọi tên **thay đổi mã sản phẩm** sẽ làm test hỏng — trước khi viết thân test.
- Assert lên hành vi thật, không assert lên mock.
- Mã chỉ test dùng nằm trong tiện ích test, không nằm trong lớp sản phẩm.
- Hiểu tác dụng phụ của phụ thuộc trước khi mock nó.

**Ca biên bắt buộc có test** — không phải "để sau", cũng không phải chờ trả lời `CQ` mới viết: rỗng hoặc thiếu (null, chuỗi rỗng,
danh sách rỗng) · sai kiểu · biên giá trị (nhỏ nhất, lớn nhất, ngay hai phía biên) · khoảng trắng đầu, cuối và liên tiếp ·
ký tự đặc biệt (Unicode, tiếng Việt có dấu, emoji, ký tự điều khiển, ký tự riêng của SQL hay shell) · đường lỗi (mạng, cơ sở
dữ liệu, tệp) · truy cập đồng thời · dữ liệu lớn khi hiệu năng là yêu cầu. Chọn nhóm áp được cho đơn vị đang làm. PLAN hay SPEC
im lặng về một ca biên thì **vẫn viết test** cho hành vi an toàn tối thiểu (không sập, không nuốt lỗi, không phá dữ liệu) và
ghi ASSUMPTION về kết quả mong muốn; chỉ phần mong muốn chưa chốt mới thành `CQ`. Lời "ba test là đủ, ca biên để sau" không
phải phép bỏ.

**Coverage** là điều kiện cần, không đủ: ngưỡng mặc định 80 % dòng cho mã mới và mã sửa, dự án chỉnh qua
`.agile.json` kèm lý do (`method/conventions.md` mục 1). Không hạ ngưỡng, không `skip`/`xfail` để xanh.
Test Python cụ thể (fixture, parametrize, mock, async): skill `python`, `references/testing.md`.

## 4. Lý do bào chữa thường gặp

| Bào chữa | Thực tế |
|---|---|
| "Đơn giản quá, khỏi test" | Mã đơn giản vẫn hỏng. Test mất 30 giây |
| "Test sau" | Test viết sau đạt ngay — không chứng minh gì; bị mã đã viết dẫn dắt, chỉ kiểm ca bạn nhớ, không kiểm ca lẽ ra phát hiện |
| "Test sau cũng đạt mục đích, quan trọng là tinh thần" | Test sau trả lời "mã làm gì"; test trước trả lời "mã phải làm gì". Coverage không kèm bằng chứng test bắt được lỗi |
| "Đã thử tay rồi" | Thử tay không ghi lại, không chạy lại được, dễ quên ca khi bị ép |
| "Xoá X giờ công là phí" | Chi phí chìm. Lựa chọn thật: viết lại bằng TDD (tin được) hay giữ mã không tin được |
| "Giữ làm tham khảo, viết test trước" | Bạn sẽ chỉnh theo nó — tức là test sau. Xoá là xoá |
| "Cần khám phá trước" | Được. Vứt bản khám phá, bắt đầu lại bằng TDD |
| "Khó test = thiết kế chưa rõ" | Nghe test: khó test là khó dùng. Đơn giản hoá giao diện |
| "TDD làm chậm" | TDD bắt lỗi trước commit, chặn hồi quy, cho phép refactor không sợ. Đường tắt nghĩa là debug ở production |
| "Mã cũ chưa có test" | Bạn đang cải thiện nó: thêm test cho phần đụng tới |

## 5. Dấu hiệu đỏ — dừng, làm lại từ test

Mã trước test · test sau mã · test đạt ngay khi vừa viết · không giải thích được vì sao test hỏng · "thêm
test sau" · "chỉ lần này thôi" · "đã thử tay" · "quan trọng là tinh thần" · "giữ làm tham khảo" · "xoá thì
phí" · "TDD giáo điều, tôi thực dụng" · "trường hợp này khác vì…".

**Tất cả đều nghĩa là: xoá mã, bắt đầu lại bằng TDD.**

## 6. Khi bí

| Vấn đề | Cách gỡ |
|---|---|
| Không biết test thế nào | Viết API mong muốn; viết assert trước. Vẫn bí → ghi `BR` thiếu ngữ cảnh |
| Test quá phức tạp | Thiết kế quá phức tạp — đơn giản hoá giao diện |
| Phải mock mọi thứ | Mã dính chặt — tiêm phụ thuộc |
| Setup test khổng lồ | Tách hàm phụ; vẫn phức tạp → đơn giản hoá thiết kế |

**Gặp lỗi:** viết test hỏng tái hiện lỗi trước, rồi đi vòng TDD — test vừa chứng minh đã sửa, vừa chặn hồi
quy. Không sửa lỗi nào mà không có test. Tìm nguyên nhân gốc trước khi sửa: skill `debugging`.

## 7. Tự kiểm trước khi báo xong

- [ ] Mỗi hàm/phương thức mới có test.
- [ ] Đã nhìn từng test hỏng trước khi viết mã, hỏng vì thiếu tính năng (không phải gõ sai).
- [ ] Mã viết ra là tối thiểu cho test đạt.
- [ ] **Cả bộ test** của dự án đạt, output sạch; lệnh + kết quả đã ghi PROGRESS.
- [ ] Test dùng mã thật (mock chỉ khi không tránh được); ca biên và ca lỗi có test.
- [ ] Kiểm đột biến trong đầu (`references/good-tests.md` mục 4): mỗi đột biến thực tế làm ít nhất một test hỏng.

Không tích được hết → bạn đã bỏ TDD. Làm lại.
