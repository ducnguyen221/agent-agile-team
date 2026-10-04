# Sửa bản phát hành đã công bố và xử lý cảnh báo secret

> **Kết luận:** `gh release edit` chỉnh tiêu đề, ghi chú, cờ nháp/thử nghiệm/mới nhất, thậm chí tên tag; `gh release
> upload` thêm file, `gh release delete-asset` bỏ file. Bản phát hành **bất biến** thì tag và file đính kèm không
> sửa được. Cảnh báo secret-scanning đóng bằng REST `PATCH` với lý do bắt buộc — **sau khi** xoay khoá nếu là khoá
> thật. Mọi lệnh ở đây là **ghi** (`SKILL.md` mục 6, 7): chỉ khi được giao đích danh.

## 1. Sửa bản phát hành đã công bố

| Cần sửa | Lệnh (ghi) | Ghi chú |
|---|---|---|
| Ghi chú còn dính nội dung nội bộ | `gh release edit <tag> --notes-file <file>` | Đọc ghi chú hiện có trước: `gh release view <tag> --json body --jq .body`; sửa rồi trình người dùng. Ghi chú đã công bố là công khai — đoạn nội bộ đã lộ, báo người dùng. |
| Tiêu đề | `gh release edit <tag> --title "<tiêu đề>"` | |
| Gắn cờ thử nghiệm / mới nhất / xuất bản bản nháp | `--prerelease`, `--latest`, `--draft=false` | `--draft` đưa về nháp. Bản nháp và bản thử nghiệm không thể là "mới nhất". |
| Tên tag sai | `gh release edit <tag-sai> --tag <tag-đúng> --verify-tag` | Chỉ đổi tên tag mà release trỏ tới. Tag mới chưa có trên remote thì GitHub tạo nó từ `--target` (nhánh hoặc SHA; không dùng nếu tag đã có) — `--verify-tag` dừng lệnh thay vì tạo bất ngờ. Tag cũ có còn trên remote hay không: kiểm `git ls-remote --tags origin`; xoá tag là ghi khó hoàn tác, chỉ **đề xuất**. |
| Thiếu file đính kèm | `gh release upload <tag> <file>... ` | Nhãn hiển thị: thêm `#<nhãn>` sau tên file. |
| Thay file trùng tên | `gh release upload <tag> <file> --clobber` | `--clobber` **xoá file cũ trước rồi mới tải lên**: tải lỗi giữa chừng là mất bản cũ — giữ bản gốc ở chỗ khác trước. |
| Bỏ file | `gh release delete-asset <tag> <tên-file>` | Hỏi xác nhận; `-y` bỏ hỏi, chỉ dùng khi đã được duyệt đích danh. |

- **Bản phát hành bất biến** (cài đặt của repo): tag không dời hay xoá được, file đính kèm không sửa hay xoá được
  sau khi công bố; tiêu đề, ghi chú, cờ thử nghiệm và "mới nhất" vẫn sửa được. Việc không sửa được (tag sai, file
  thiếu) → phải phát hành **bản mới** (số version kế) thay vì sửa; báo người dùng chọn. Muốn tránh: gắn đủ file
  vào bản **nháp** rồi mới xuất bản.
- Tag sai ở bản **chưa bất biến**: ngoài việc đổi tên tag, nêu cho người dùng phương án phát hành bản mới (số
  version kế) — ai đã tải hay ghim theo tag cũ không tự đổi theo, nên người dùng chọn.
- Đã sửa thì xem lại: `gh release view <tag> --json tagName,name,isDraft,isPrerelease,assets --jq .`.
- File checksum (`.sha256`) sinh **từ đúng file đã tải lên**: thay file thì sinh lại checksum, đừng tải checksum cũ.

## 2. Cảnh báo secret-scanning: liệt kê, ghi nhận, đóng

```bash
# liệt kê cảnh báo đang mở (đọc) — không in giá trị secret
gh api "repos/{owner}/{repo}/secret-scanning/alerts?state=open&per_page=100" --jq '.[] | {n: .number, loai: .secret_type_display_name, mo_tu: .created_at, validity: .validity, url: .html_url}'
# vị trí bị lộ (đọc): tệp, dòng, commit — vẫn không in giá trị
gh api "repos/{owner}/{repo}/secret-scanning/alerts/<n>/locations" --jq '.[] | {type, path: .details.path, line: .details.start_line, commit: .details.commit_sha}'
# đóng cảnh báo (ghi): resolution BẮT BUỘC khi state=resolved; comment lý do không sửa hay xoá được sau này
gh api -X PATCH "repos/{owner}/{repo}/secret-scanning/alerts/<n>" -f state=resolved -f resolution=false_positive -f resolution_comment="Chuỗi mẫu trong tài liệu, không phải khoá thật."
```

- `resolution` nhận bốn giá trị: `false_positive` (không phải secret thật) · `used_in_tests` (secret giả dùng trong
  test) · `revoked` (khoá thật, **đã** thu hồi/xoay) · `wont_fix` (khoá thật, người dùng chấp nhận rủi ro — cần
  người dùng nói đích danh). Chọn sai giá trị làm báo cáo bảo mật sai: token test bị đánh dấu nhầm → `false_positive`
  hoặc `used_in_tests` kèm lý do cụ thể; khoá thật chưa xoay **không** được đóng bằng `false_positive`.
- `validity` (`active`, `inactive`, `unknown`) cho biết GitHub kiểm thấy khoá còn dùng được hay không — khoá `active`
  là ưu tiên xoay trước. Lọc `state=open` rõ ràng thay vì dựa vào mặc định.
- Cần quyền quản trị hoặc security manager và token có phạm vi `repo` hoặc `security_events`; thiếu quyền → báo, không đổi
  cách đăng nhập (`SKILL.md` mục 1).

**Khoá thật bị lộ — ghi nhận trước khi xoay** (vào báo cáo, **không** kèm giá trị secret):
số hiệu cảnh báo · loại secret · số ngày đã mở (từ `created_at`) · các vị trí (tệp, dòng, commit — gồm cả lịch sử,
không chỉ bản hiện tại) · `validity` · ai/hệ nào dùng khoá đó (để xoay không làm hỏng dịch vụ) · việc đã thấy khoá bị
dùng lạ hay chưa (log nhà cung cấp, việc của chủ khoá). Thứ tự: báo người dùng → **chủ khoá xoay/thu hồi ở nhà cung
cấp** → gỡ khỏi code → mới đóng cảnh báo bằng `resolution=revoked`. Gỡ khỏi bản hiện tại không xoá được khoá khỏi
lịch sử git; viết lại lịch sử là việc khác, khó hoàn tác — chỉ đề xuất.

## Nguồn

Hướng dẫn chính thức của GitHub CLI (cli.github.com/manual: `gh release edit`, `gh release upload`,
`gh release delete-asset`); GitHub REST: Update a release (`tag_name`, `target_commitish`, `make_latest`), Secret
scanning (cập nhật cảnh báo, liệt kê cảnh báo, liệt kê vị trí); GitHub Docs: Immutable releases.
