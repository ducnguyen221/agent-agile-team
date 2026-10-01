# scripts/

Ba công cụ cho dự án áp dụng, chỉ dùng thư viện chuẩn Python (3.9+), chạy được trên Windows và macOS. Hợp
đồng đầy đủ (tập con YAML, khoá, tiêu đề, sổ gốc, cấu hình) ở [`templates/README.md`](../templates/README.md).

| Script | Việc |
|---|---|
| `init.py` | Dựng `.agile.json`, ba sổ gốc và khung sprint từ `templates/`; mặc định chạy thử, không ghi đè |
| `check.py` | Kiểm chuẩn tài liệu; `--self` kiểm lõi sạch và ngân sách `AGENTS.md` của chính repo |
| `index.py` | Sinh lại khối "Đang mở" ở đầu ba sổ gốc |
| `_common.py` | Thư viện chung: đọc frontmatter tập con YAML, che mã trong Markdown, đọc `.agile.json`; không chạy trực tiếp |

## Cách chạy

```text
python scripts/init.py <gốc-dự-án>                     # chạy thử: in "+ tạo / ~ sửa / = giữ", không ghi
python scripts/init.py <gốc-dự-án> --apply             # ghi .agile.json + REQUESTS, SPRINTS, SPECS
python scripts/init.py <gốc-dự-án> --apply --sprint <slug> --title "<mục tiêu>" [--tiny]
       [--size tiny|small|medium|large] [--risk normal|high] [--risk-tags a,b] [--request RQ-NNN] [--feature FS-NNN]
       [--date YYYY-MM-DD]
python scripts/check.py <file.md|.agile.json|thư-mục> [...]   # thư mục: quét đệ quy *.md và mọi .agile.json
python scripts/check.py --self [--root <repo>]
python scripts/index.py <gốc-dự-án> [--check]          # --check: không ghi, thoát 1 nếu sổ chưa cập nhật
```

## Mã thoát

| Script | 0 | 1 | 2 |
|---|---|---|---|
| `init.py` | xong (hoặc chạy thử xong) | — | lỗi đầu vào: tham số sai (gồm ký tự điều khiển trong `--title`), `.agile.json` hỏng hoặc sai hình, đích ghi nằm ngoài gốc dự án và `artifact_root`, sổ thiếu `next_id` |
| `check.py` | Đạt: không có Chặn / Phải sửa (Nên sửa, Ghi chú vẫn in) | Không đạt: có Chặn hoặc Phải sửa | lỗi đầu vào: đường dẫn không có, file không đọc được, frontmatter ngoài tập con, `.agile.json` không phải JSON |
| `index.py` | đã cập nhật hoặc không đổi | `--check` thấy sổ chưa cập nhật | lỗi đầu vào: thiếu hoặc sai hình `.agile.json`, sổ ngoài gốc dự án, thiếu sổ, dấu mốc sai, frontmatter spec sống hỏng |

Mỗi phát hiện của `check` in một dòng `đường-dẫn:dòng: <mức> [<mã luật>] <mô tả>`; dòng cuối là tóm tắt số
file, số phát hiện theo mức và kết luận. `init` và `index` khi ghi lại một file có sẵn giữ nguyên BOM và kiểu
xuống dòng (LF/CRLF) của file đó; file mới ghi UTF-8 không BOM, LF.

## Biến môi trường

| Biến | Dùng bởi | Ý nghĩa |
|---|---|---|
| `AGENT_AGILE_DENYLIST` | `check.py --self` | Đường tới danh sách từ cấm **ngoài repo** (hợp đồng ở [`tests/README.md`](../tests/README.md)). Thiếu, không đọc được hoặc rỗng → in `WARNING NOT_CONFIGURED` ra stderr, luật `leak-denylist` **Chưa chạy** (không tính là Đạt); mã thoát không vì thế mà đổi |

## Luật của `check`

Mức theo thang chung `method/severity.md`. Luật tài liệu chỉ áp cho file có khoá `doc` hợp lệ; ba luật chung
về mã (`id-bare-single-letter`, `id-unknown-prefix`, `old-scale-label`) áp cho mọi file `.md` được quét. Mã
trong code span, khối code, comment HTML và đích của liên kết không bị xét. Truyền thẳng `.agile.json` thì chỉ
chạy các luật `config-*` cho file đó.

**Code span:** được ngắt qua nhiều dòng trong cùng một đoạn văn, nhưng `check` chỉ nối khi dòng mở và dòng đóng
đều lẻ số dấu huyền (dòng tự cân thì coi dấu huyền lẻ ở dòng trên là chữ thường). Code span **không lồng**: một
lệnh chứa dấu huyền (`git commit -m "…"` nhắc mã, JSON inline, dấu thoát PowerShell) phải bọc ngoài bằng **hai**
dấu huyền. Mã bị bắt có dấu huyền sát bên thì phát hiện kèm gợi ý "code span lồng nhau hoặc ngắt dòng?".

| Mã luật | Mức | Bắt gì |
|---|---|---|
| `frontmatter-syntax` | Chặn | Frontmatter ngoài tập con YAML, kèm dòng — lỗi đầu vào, thoát 2 |
| `frontmatter-missing` | Phải sửa | File tên chuẩn (`SPEC.md`, `PLAN.md`, `PROGRESS.md`, `REPORT.md`, `SPRINT.md`, ba sổ) không có frontmatter |
| `frontmatter-key-missing` | Phải sửa | Thiếu khoá bắt buộc theo loại tài liệu (`templates/README.md` mục 3); file tên chuẩn có frontmatter mà thiếu `doc` |
| `frontmatter-key-unknown` | Ghi chú | Khoá ngoài bảng khoá của hợp đồng |
| `frontmatter-value` | Phải sửa | Giá trị sai miền (`status`, `size`, `risk`, ngày, mã `RQ-`/`FS-`/`SPR-` kể cả độ rộng theo `id_width` của `.agile.json` gần nhất, `id`, `next_id`, `links`, `review_round`) hoặc mâu thuẫn (`risk: high` mà không `large`, `risk_tags` khác rỗng mà không `high`) |
| `doc-unknown` | Ghi chú | Có khoá `doc` nhưng không thuộc loại đã biết — chỉ áp luật chung |
| `heading-missing` | Phải sửa | Thiếu tiêu đề cấp 2 bắt buộc theo loại tài liệu (SPEC cỡ vừa trở lên thiếu "Truy vết" cũng báo) |
| `conclusion-missing` | Phải sửa | Tài liệu sprint hoặc spec sống thiếu dòng `> **Kết luận:**` trước tiêu đề cấp 2 đầu tiên |
| `id-bare-single-letter` | Phải sửa | Mã một chữ cái + số (`P1`, `D3`) ngoài dấu code; trừ tier `T1`/`T2`/`T3` |
| `id-unknown-prefix` | Phải sửa | Mục được định nghĩa bằng tiền tố hai chữ cái ngoài bảng mã (`YC2`); không áp cho `skills/*/tests/` |
| `id-wrong-doc` | Phải sửa | Mục định nghĩa bằng tiền tố của tài liệu khác (`BR1` trong PLAN) |
| `xref-missing` | Phải sửa | Nhắc tới mã không được định nghĩa ở tài liệu sở hữu (tìm qua `links`) |
| `xref-unresolved` | Ghi chú | Không tìm được tài liệu sở hữu qua `links` để đối chiếu |
| `task-without-trace` | Phải sửa | `TK` (tiêu đề hoặc gạch đầu dòng in đậm) không trỏ `FR`/`SC`; `TK1.1` kế thừa `TK1`, mồ côi thì báo |
| `report-sc-without-vr` | Phải sửa | `SC` của SPEC không xuất hiện trong dòng `VR` nào của REPORT (hoặc SPRINT) |
| `report-fr-without-vr` | Phải sửa | REPORT: `FR` của SPEC không có dòng `VR` nào trỏ tới `FRn` hoặc kịch bản `FRn.m`; miễn khi dòng định nghĩa ở SPEC ghi trạng thái `bỏ` ("(bỏ)" / "— bỏ" cuối dòng) hoặc một dòng ghi `NOT_APPLICABLE` kèm lý do |
| `self-review` | Chặn | Một nhãn agent vừa giữ vai thực thi vừa giữ vai kiểm định trong `roles` |
| `qa-not-independent` | Phải sửa | Có `VR` mà `qa` trùng nhãn `implementer`/`architect` không ghi "tự kiểm, chưa độc lập"; hoặc có ghi mà `verdict: pass` |
| `roles-invalid` | Phải sửa | `roles` sai hình: vai lạ, tier ngoài `T1`–`T3`, thiếu nhãn agent |
| `gate-invalid` | Phải sửa | Cổng đã kết luận mà thiếu `*_at`/`*_quote`; `status: approved` khi `gate_1` chưa approved; REPORT `accepted` hoặc SPRINT `done` khi `gate_2` còn pending |
| `old-scale-label` | Phải sửa | Ô thuộc cột tiêu đề "Mức…"/"Severity"/"Level" của bảng, hoặc chữ sau "Mức:"/"Severity:", dùng nhãn thang cũ (`High`, `Critical`, `Minor`, `BLOCK`…); `method/severity.md` được miễn |
| `config-syntax` | Chặn | `.agile.json` không phải JSON — lỗi đầu vào, thoát 2 |
| `config-invalid` | Phải sửa | `.agile.json` sai hình (gồm `paths.*` tuyệt đối hoặc chứa `..`, `sprint_dir` dùng placeholder ngoài `{date}`/`{slug}`, `id_width` không phải số nguyên ≥ 1), hoặc ngưỡng coverage khác 80 mà `coverage.reason` rỗng; `init`/`index` dùng chung bộ kiểm này (`_common.config_problems`) |
| `config-public-root` | Chặn | `visibility: public` mà `artifact_root` (đường tuyệt đối) nằm trong gốc dự án |
| `leak-denylist` | Chặn | `--self`: file của repo (kể cả tên file) chứa từ cấm — mục chữ khớp nguyên từ, mục có ký tự đường dẫn khớp chuỗi con ([`tests/README.md`](../tests/README.md)); báo số thứ tự từ, không in lại từ |
| `agents-md-budget` | Phải sửa | `--self`: `AGENTS.md` quá 120 dòng hoặc quá 10 240 byte |

**Phạm vi `--self`:** mọi file Git đang theo dõi **và** file chưa add, trừ file bị `.gitignore` (`git ls-files -c -o
--exclude-standard`); không phải repo Git thì quét cây thư mục. `--self` không nhận đường dẫn (thoát 2); chọn repo
bằng `--root`. Luật tài liệu bỏ
qua `tests/fixtures/` (ca hỏng cố ý). Chống rò quét cả `tests/fixtures/` nhưng miễn: `NOTICE` và
`THIRD_PARTY.md` (tên tác giả theo giấy phép), dòng bảng của `UPSTREAM.md` (dòng ghi nguồn), và dòng có chữ
`model` trong `skills/*/tests/pressure.md` (hồ sơ thử ghi model).
