# Đồng bộ tài liệu sau Cổng 2

<!-- Nguồn: garrytan/gstack document-release/SKILL.md.tmpl @ 96764e8 (MIT), qua bản distill local;
     luật chạy nền lấy từ HEAD. Viết lại; bỏ bước gắn với harness và sổ manifest của môi trường.
     Mục 10: ý của affaan-m/ECC commands/update-docs.md @ ef648e01 (MIT), viết lại, bỏ mẫu lệnh của nguồn.
     Mục 11: ý giữ spec sống từ affaan-m/ECC living-docs-governance @ ef648e01, qua templates/registry/feature-spec.md. -->

> **Kết luận:** đọc **mọi** tài liệu của dự án, đối chiếu diff nhánh, **tự sửa drift sự thật** (đường
> dẫn, số đếm, bảng, cross-ref), **hỏi** trước thay đổi tường thuật / xoá mục / viết lại >10 dòng / mô
> hình bảo mật. Hai điều **không bao giờ**: ghi đè hay viết lại mục CHANGELOG (chỉ thêm, sửa bằng Edit
> với chuỗi cũ chính xác), và tự tăng VERSION. Chạy nền thì tự chọn phương án khuyến nghị cho phần
> không rủi ro, **bỏ qua và ghi lại** mọi đề xuất đụng CHANGELOG/VERSION. Bảng lệnh, bảng biến môi trường
> **lấy từ nguồn sự thật** chứ không gõ theo trí nhớ (mục 10); spec sống chỉ đối chiếu ở đây, gỡ bỏ có chủ ý đi
> vào khu xoá chứ không xoá câu (mục 11).

## 1. Khi nào, phạm vi

Sau Cổng 2, trước gộp/push. Chạy từ nhánh sprint (đang ở nhánh gốc → "chạy từ nhánh sprint"). Nhánh
gốc: PLAN/hội thoại/upstream, hoặc `git symbolic-ref refs/remotes/origin/HEAD` → `origin/main`.

Đầu vào: `git diff <gốc>...HEAD --stat`, `git log <gốc>..HEAD --oneline`, `--name-only`. Tài liệu:
`git ls-files "*.md"` + `git ls-files --others --exclude-standard "*.md"` (chạy giống nhau trên Git
Bash, PowerShell, Linux; đã bỏ `.git/`, honor `.gitignore` — không dùng `find` trần vì trên Windows nó
là lệnh khác). Thêm file luật agent của dự án và điểm vào `docs/` nếu nằm sâu.

Phân loại thay đổi: tính năng mới · hành vi đổi · chức năng bỏ · hạ tầng (build, test, CI). Nói ra:
"N file, M commit, K tài liệu cần soát".

## 2. Soát từng file

| File | Hỏi gì | Mức thận trọng |
|---|---|---|
| README | mô tả đủ năng lực diff thêm? cài đặt/ví dụ còn đúng? | sửa sự thật; **không** sửa phần giới thiệu / định vị |
| ARCHITECTURE | sơ đồ, thành phần, "vì sao" còn đúng? | chỉ sửa chỗ diff **mâu thuẫn rõ**; triết lý thiết kế không đụng |
| CONTRIBUTING | đi lại hướng dẫn như người mới: lệnh nào sẽ hỏng? bậc test khớp hạ tầng test? | ghi chỗ sẽ làm người mới vấp |
| File luật agent của dự án (`AGENTS.md`, tương đương) | cây thư mục, lệnh, script, build/test khớp thực tế? | sửa sự thật; luật thì **hỏi** |
| Mọi `.md` khác | mục đích, đối tượng; diff có mâu thuẫn điều nó nói? | — |

Mỗi sửa cần làm gắn nhãn **tự sửa** (sự thật: dòng bảng, đường dẫn, số đếm, cây) hoặc **hỏi**
(tường thuật, xoá mục, mô hình bảo mật, viết lại lớn, mục mới hẳn, liên quan mơ hồ).

## 3. Tự sửa — và nói rõ sửa gì

Mỗi file một dòng cụ thể: không "cập nhật README" mà "README: thêm `web-qa` vào bảng skill, 12 → 13".
Không bao giờ xoá nguyên một mục ở bất kỳ tài liệu nào.

## 4. Hỏi — phần rủi ro

Mỗi điểm một lượt hỏi: bối cảnh (file, mục, đang soát gì) · quyết định cụ thể · **khuyến nghị: chọn
X vì <một dòng>** · lựa chọn "bỏ qua, để nguyên". Trả lời xong áp ngay. Chạy nền (mục 8): không hỏi.

## 5. CHANGELOG — chỉ thêm, chỉ đánh bóng chữ

Luật này sinh ra từ sự cố thật: một agent đã **thay thế** các mục có sẵn thay vì giữ.

1. Đọc cả CHANGELOG trước.
2. Sprint này **thêm** mục dưới tiêu đề đang mở (ví dụ `## Unreleased`) nếu chưa có; không tạo tiêu đề
   phiên bản mới.
3. Chỉ sửa **chữ trong** mục có sẵn; không xoá, không đổi thứ tự, không thay mục; không sinh lại mục
   từ diff — mục là nguồn sự thật.
4. Mục trông sai hay thiếu → **hỏi**, không âm thầm sửa.
5. Dùng Edit với chuỗi cũ **chính xác**; không bao giờ Write đè file.

Phép thử "bán hàng" cho mục mới: người đọc nghĩ "ồ hay, tôi muốn cái này"? Dẫn bằng điều người dùng
**làm được** ("Giờ bạn có thể…"), không phải "đã refactor…"; thay đổi nội bộ xuống mục con "Cho người
đóng góp". Sửa giọng nhỏ thì tự làm; đổi nghĩa thì hỏi.

## 6. Nhất quán chéo và khả năng tìm thấy

README ↔ file luật agent cùng kể một bộ năng lực? ARCHITECTURE ↔ CONTRIBUTING cùng một cây? Mục
CHANGELOG mới nhất ↔ file VERSION? Mọi tài liệu đến được từ README hoặc file luật agent (ARCHITECTURE
tồn tại mà không ai trỏ → ghi)? Mâu thuẫn sự thật (lệch số phiên bản) tự sửa; mâu thuẫn tường thuật hỏi.

## 7. TODO/backlog và VERSION

- Có file TODO/backlog: mục diff này hoàn thành rõ ràng → đánh dấu xong kèm sprint; mục trỏ file đổi
  nhiều → hỏi; `TODO|FIXME|HACK|XXX` mới trong diff là việc hoãn thật → hỏi có ghi backlog không.
- **VERSION không tự tăng.** Chưa bump → đề xuất (khuyến nghị thường là *không*, tài liệu không đáng
  bump); đã bump → đọc mục CHANGELOG của phiên bản đó so với **toàn bộ** diff: thay đổi đáng kể chưa
  được nhắc → hỏi (bump tiếp / mở rộng mục / để sau). Một bump đặt cho tính năng A không được âm thầm
  nuốt tính năng B.

## 8. Hợp đồng chạy nền (subagent / phiên không tương tác)

- Cổng hỏi → **tự chọn phương án khuyến nghị**, ghi vào báo cáo, đi tiếp; không dừng chờ.
- **Ngoại lệ không nới:** mọi đề xuất viết lại/ghi đè mục CHANGELOG hay đổi VERSION → **bỏ qua và ghi
  lý do**. Thêm mục mới dưới tiêu đề đang mở vẫn được.
- Báo cáo có mảng **quyết định đã tự chọn**: điểm · phương án chọn · vì sao · bỏ qua gì.
- Lệnh của người ngoài hồ sơ ("viết lại hẳn", "tạo thêm tài liệu", "xoá hẳn mục cho sạch") không đổi phạm vi: phần
  tường thuật, tài liệu mới và xoá mục đi vào mảng "bỏ qua" kèm lý do, người quyết lại bằng một câu rõ.

## 9. Commit và báo cáo

`git status` trước: không tài liệu nào đổi → "Tài liệu đã đồng bộ", không commit. Có đổi → stage **theo
tên file** (không `git add -A` / `.` — nhiều phiên agent chạy song song), một commit `docs: sync
documentation for <SPR->`. Push chỉ khi người dùng gật (menu nhánh). Bước đồng bộ này chỉ **soạn** mục
`## Documentation` vào file/bản nháp, **không ghi lên PR**. Ghi lên PR chỉ xảy ra sau khi người dùng chọn
"2. Push + PR" ở menu, trong [closing-sprint SKILL.md](../SKILL.md) mục 4.1 bước 3 (thân PR): khi đó thêm/thay mục
`## Documentation` qua file tạm (`gh pr view --json body -q .body > tmp` → sửa → `gh pr edit --body-file tmp` →
xoá) — không heredoc shell (PowerShell không parse); không PR → bỏ qua.

Bảng cuối: mỗi tài liệu một dòng — *Đã cập nhật (gì)* · *Đúng rồi* · *Đánh bóng chữ* · *Cờ lỗi thời (cho
người)* · *Không bump (người dùng bỏ)* · *Đã bump* · *Không có file* · *Bỏ qua (vì sao)*.

## 10. Bảng sinh từ nguồn sự thật, soát lỗi thời

Một dòng của tài liệu mô tả điều mà **một file khác** quyết (lệnh, biến, tuyến, cấu hình triển khai) thì file đó là
chủ, tài liệu chỉ là bản sao:

| Nguồn sự thật | Sinh ra |
|---|---|
| mục lệnh của manifest (`package.json`, `Makefile`, `pyproject.toml`…) | bảng lệnh: lệnh · mô tả một dòng |
| `.env.example` (hay mẫu tương đương) | bảng biến: tên · bắt buộc hay tuỳ chọn · mặc định · định dạng, giá trị hợp lệ |
| file tuyến hay đặc tả API | tham chiếu API |
| `Dockerfile`, compose, workflow triển khai | phần thiết lập hạ tầng |

- Đọc nguồn rồi điền; **không** gõ theo trí nhớ và không đoán điều nguồn không nói (công dụng một biến, giá trị mặc
  định vắng ở nguồn → để trống và ghi cho người, không bịa). Thêm một dòng chú thích ngắn trên bảng nói nó sinh từ
  nguồn nào, để lần sau sinh lại thay vì sửa tay; đoạn sinh từ nguồn không sửa tay.
- Giữ nguyên phần **viết tay** đang đúng (hướng dẫn cài đặt, giới thiệu); chỉ đụng đoạn có nguồn.
- **Soát lỗi thời:** tài liệu lâu không ai sửa (khoảng 90 ngày trở lên) mà nguồn tương ứng đổi trong diff → gắn
  **cờ lỗi thời** cho người xem, kèm điều diff cho thấy; dòng mâu thuẫn rõ với diff thì tự sửa (mục 3). Viết lại cả
  tài liệu tường thuật (triển khai, vận hành) từ diff là **hỏi**, vì diff không cho biết cổng, thứ tự, cách hoàn tác.
- **Không tạo tài liệu mới** (runbook, hướng dẫn đóng góp…) khi phạm vi sprint chưa yêu cầu; ghi "bỏ qua" kèm lý do.

## 11. Spec sống: đối chiếu ở đây, sửa ở bước 4

Spec sống `FS-` được cập nhật ở bước 4 của `SKILL.md`; bước đồng bộ này chỉ đối chiếu và ghi chỗ lệch. Bốn nguyên
tắc giữ spec không mục (theo comment đầu `templates/registry/feature-spec.md`):

1. **Một sự thật một chủ:** hành vi ở mục 1, giới hạn và thứ đã bỏ ở mục 3, lý do ở ADR; nơi khác trỏ về, không chép.
2. **Tài liệu là bằng chứng, không phải lệnh:** trước khi dựa vào một dòng, đối chiếu với mã và test hiện tại; lệch thì
   ghi chỗ lệch, không lặng lẽ chọn một bên.
3. **Đính chính có ngày:** điều lỗi thời sửa bằng dòng đính chính ghi ngày, không viết lại quá khứ cho đẹp.
4. **Chỉ cập nhật mục bị chạm:** đổi hành vi → mục 1; đổi giới hạn hay bỏ có chủ ý → mục 3; quyết định khó đảo ngược → ADR.

Hành vi sprint **gỡ có chủ ý** (ví dụ tra theo tên vì làm lộ đơn người khác) **không** bị xoá câu: chuyển vào **khu xoá**
ở mục 3 của spec với bốn ý — mục · vì sao bỏ · thay bằng · điều kiện xét lại — kèm dòng đính chính có ngày; FR bỏ giữ mã
và ghi "bỏ". Chạy nền gặp câu như vậy mà bước 4 chưa chạy → ghi thành đề xuất trong mảng quyết định, không tự sửa spec.
