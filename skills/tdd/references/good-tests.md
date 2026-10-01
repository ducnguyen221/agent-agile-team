# Viết test tốt

> **Kết luận:** một test tồn tại để bắt **một kiểu hỏng cụ thể**. Hai nguyên tắc chi phối mọi thứ:
> (1) mỗi test gọi tên kiểu hỏng nó bắt; (2) mỗi test chạy **thứ thật**. TDD nghiêm túc tự sinh ra cả
> hai: test viết trước và đã hỏng trên mã thật thì đã chứng minh nó hỏng được, và chỉ được mock khi phụ
> thuộc thật tỏ ra chậm hoặc nằm ngoài.

Đọc khi: viết hay sửa test, thêm mock, thêm hàm dọn/hàm phụ cho test.

## 1. Gọi tên kiểu hỏng

Trước khi viết thân test, trả lời: **thay đổi nào ở mã sản phẩm sẽ làm test này hỏng — và thay đổi đó
là lỗi hay là quyết định?** Test xứng chỗ khi nó bắt được nhánh sai, tác dụng phụ bị thiếu, đối số sai,
ca biên, hoặc hợp đồng bị phá.

- **Giá trị mong đợi tính độc lập.** Dùng hằng số viết tay, fixture đã kiểm bằng tay; test dạng bảng có
  cột `want` là hằng số là dạng nên dùng. Giá trị mong đợi do chính mã được test (hay hàm phụ của nó) tính
  ra thì luôn đạt, mã làm gì cũng đạt:

  ```python
  # Sai — cùng một hàm dựng cả hai vế: luôn đúng
  expected = build_search_query(tag="urgent")
  assert build_search_query(tag="urgent") == expected

  # Đúng — hằng số dẫn bằng tay
  assert build_search_query(tag="urgent") == 'tag:"urgent"'
  ```

- **Không làm "máy dò thay đổi".** Test chỉ hỏng khi có quyết định cố ý (giá trị hằng, câu chữ thông báo,
  cấu trúc nội bộ) thì kêu khi thiết kế lại và ngủ khi có lỗi. Test hành vi phụ thuộc vào quyết định đó:
  không phải `assert MAX_RETRIES == 5` mà là "một lời gọi hỏng được thử lại 5 lần và lần thứ 6 không xảy
  ra".
- **Hành vi, không phải văn bản.** Assert rằng script, skill hay file cấu hình chứa đúng một dòng chỉ
  chứng minh nguồn là nguồn. Chạy script với đầu vào có kiểm soát, assert output, tác dụng phụ hoặc mã
  thoát. Tài liệu hướng dẫn agent được kiểm bằng hành vi của agent dùng nó (skill `writing-skills`); văn
  xuôi cho người đọc không cần test.
- **Mã của bạn, không phải framework.** Test hợp đồng mã của bạn đưa ra ở biên: route bạn đăng ký, câu truy
  vấn bạn sinh, payload bạn tạo. Cơ chế của thư viện là test của người bảo trì nó (ví dụ kinh điển: assert
  router gọi handler đã đăng ký). Khi thư viện thật sự làm bạn bất ngờ, viết **một** test mô tả hẹp gọi
  tên giả định đó. Cùng ranh giới đó trong mã của bạn: hàm khởi tạo, getter, hằng, chuyển tiếp tầm thường
  chỉ đáng test khi chúng kiểm, chuẩn hoá, đặt mặc định, suy ra, ép luật hoặc gây tác dụng phụ — nếu không,
  assert kết quả đầu tiên người dùng thấy được mà phụ thuộc vào chúng.

**Cổng trước khi viết thân test:**

```
Gọi tên thay đổi mã sản phẩm làm test này hỏng.
  Không gọi được                → thiết kế lại quanh một hành vi quan sát được
  "Nguồn văn bản đổi"           → chạy thứ đó và assert tác dụng của nó
  Chỉ quyết định cố ý           → máy dò thay đổi; test hành vi phụ thuộc quyết định
Xác nhận giá trị mong đợi tính ra KHÔNG dùng mã được test.
  Dùng lại logic/hàm phụ của mã → thay bằng hằng số hoặc fixture kiểm tay
```

## 2. Chạy thứ thật

- **Mock không được assert.** Assert lên mock đạt khi mock có mặt và hỏng khi mock vắng — nó không nói
  gì về thành phần. Assert hành vi của thành phần thật; nếu thứ bạn đang kiểm là mock thì bỏ mock hoặc
  xoá assert. Câu hỏi để tự sửa: "mình đang test hành vi của một cái mock à?"
- **Mock đúng tầng.** Biết mọi tác dụng phụ của phương thức thật trước khi thay nó; mock thao tác chậm
  hoặc ra ngoài, giữ thật phần test phụ thuộc vào. Không chắc → chạy test với bản thật trước, quan sát
  điều gì thật sự cần xảy ra.

  ```python
  # Sai — mock nuốt mất bước ghi cấu hình mà bước phát hiện trùng đọc lại
  monkeypatch.setattr(catalog, "discover_and_cache_tools", lambda *a: None)

  # Đúng — chỉ mock bước khởi động server chậm; bước ghi cấu hình giữ thật
  monkeypatch.setattr(server_manager, "start", fake_start)
  ```

- **Bản giả phải cụ thể.** Khi đối số, số lần gọi, thứ tự là một phần hợp đồng thì assert chúng — bản giả
  chấp nhận mọi thứ không kiểm gì. Mỗi nhánh (thành công, lỗi, dữ liệu hỏng) một fixture/spy riêng, để
  nhánh sai không thể thoả kỳ vọng.
- **Dữ liệu giả phản chiếu đủ dữ liệu thật.** Mock **toàn bộ** cấu trúc như thật — mọi trường đã ghi trong
  tài liệu — không chỉ trường test đang đọc. Mock thiếu trường hỏng im lặng khi mã phía sau đọc trường bị
  bỏ: test đạt, tích hợp gãy.
- **Lớp sản phẩm chỉ có phương thức sản phẩm.** Hàm dọn chỉ test cần nằm trong tiện ích test, không thành
  `destroy()` trên lớp sản phẩm. Tự hỏi: phương thức này chỉ test gọi? Lớp này có sở hữu vòng đời tài
  nguyên này không? Trả lời sai → chuyển sang tiện ích test.
- **Ưu tiên thành phần thật hơn mock phức tạp.** Khi setup mock dài hơn logic test, mock thiếu phương thức
  bản thật có, hoặc test gãy mỗi khi đổi mock → chuyển sang test tích hợp với thành phần thật. Câu hỏi:
  "ở đây có cần mock thật không?"

**Cổng trước khi thêm mock hay hàm phụ:**

```
Liệt kê tác dụng phụ của phương thức thật; giữ thật cái test phụ thuộc,
  mock tầng chậm/ra ngoài nằm dưới chúng.
Dữ liệu mock phản chiếu đủ cấu trúc thật.
Phương thức chỉ test gọi → nằm trong tiện ích test.
Sắp assert lên chính mock → bỏ mock hoặc xoá assert.
```

## 3. Test đi cùng mã

Vòng TDD — test hỏng, mã tối thiểu, dọn — chính là định nghĩa "xong". Giao đúng những test hành vi cần, và
chỉ những test đó: mã tầm thường và văn xuôi cho người không cần test; test viết để làm đủ thủ tục tốn công
bảo trì mãi mãi. Test tích hợp không phải việc "để sau": phần nào phụ thuộc thành phần thật thì test tích
hợp đi cùng commit.

## 4. Kiểm đột biến

Trước khi xong, đột biến mã sản phẩm trong đầu; mỗi đột biến thực tế phải làm ít nhất một test hỏng:

- hằng số hay đối số sai;
- nhánh xử lý sai;
- thiếu thay đổi trạng thái hoặc tác dụng phụ;
- trả về rỗng hoặc mặc định;
- thiếu kiểm cho giá trị 0, rỗng, `None`, không có quyền, hoặc sai định dạng.

Đột biến không test nào bắt → hành vi đó chưa được bảo vệ, hoặc test là luận lý vòng.

## 5. Tra nhanh

| Khi bạn… | Làm |
|---|---|
| Viết bất kỳ test nào | Gọi tên kiểu hỏng nó bắt — một lỗi, không phải một quyết định |
| Dựng giá trị mong đợi | Dẫn bằng tay; không bao giờ bằng mã được test |
| Test script hay tài liệu | Chạy nó / thử áp lực người dùng nó; không grep văn bản |
| Muốn test phụ thuộc | Test hợp đồng ở biên của bạn, không test cơ chế của họ |
| Muốn assert lên phần tử đã mock | Test thành phần thật, hoặc bỏ mock |
| Sắp mock một phương thức | Biết tác dụng phụ; mock tầng chậm/ra ngoài |
| Dựng dữ liệu mock | Phản chiếu đủ cấu trúc thật |
| Cần hàm dọn chỉ test dùng | Đặt trong tiện ích test |
| Thấy setup mock phình to | Chuyển sang test tích hợp với thành phần thật |
| Xong một file test | Chạy kiểm đột biến |

## 6. Dấu hiệu cảnh báo

- Setup và assert dùng chung một đối tượng, bảo đảm bằng nhau.
- Test chỉ hỏng được khi crash, panic hoặc thiếu selector.
- Test hỏng ở mọi thay đổi cố ý, không bao giờ hỏng ở lỗi vô tình.
- Giá trị mong đợi bị giấu sau vòng lặp, builder hay hàm phụ.
- Test grep văn bản nguồn, hoặc assert một ký hiệu đã xoá vẫn vắng mặt.
- Test vẫn có nghĩa nếu chỉ còn lại framework.
- Test tồn tại vì coverage, không kiểm tác dụng phụ hay kết quả nào.
- Assert kiểm một ID kiểu `*-mock`, hoặc hỏng khi bỏ mock.
- Một phương thức chỉ được gọi từ file test.
- Setup mock chiếm hơn nửa test, hoặc không giải thích được vì sao cần mock.
- Mock "cho chắc".
