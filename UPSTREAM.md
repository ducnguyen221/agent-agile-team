# UPSTREAM — nguồn, mốc và đợt distill

Mỗi đợt distill một khối. Mỗi nguồn ghi: nhánh, SHA HEAD lúc chốt, ngày commit, giấy phép, cách dùng.
Đợt nào cũng lấy bản **mới nhất tại thời điểm distill** của nguồn. Skill distill từ nguồn nào thì
frontmatter của skill đó ghi `source` (repo, đường file, SHA) khớp bảng dưới.

Cách dùng: **chép** = chép nguyên văn được, giữ thông báo bản quyền · **ý** = chỉ viết lại ý, không chép
văn bản · **NOTICE** = chép được nhưng mang theo NOTICE Apache-2.0 · **private** = chỉ dùng khi repo còn
private, phải viết lại trước khi công khai.

## Đợt 1 — chốt SHA 2026-10-01 (15:20–15:28 UTC+7)

Trạng thái: **đã chốt mốc, chưa distill** (khối này khởi tạo từ bản nháp của bước nghiên cứu; cập nhật
khi distill xong).

### Repo mã nguồn

| Nguồn | Nhánh | SHA HEAD (ngày commit) | Tag mới nhất | Giấy phép | Cách dùng |
|---|---|---|---|---|---|
| `obra/superpowers` | `main` | `8ca22dba9a94f28898bbce59f2537ff4d87c747d` (2026-09-25) | `v6.4.2` = cùng SHA | MIT © 2025 Jesse Vincent | chép |
| `affaan-m/ECC` | `main` | `c70874fae9eb0e5ad0365beb7e2955899fd1d30f` (2026-09-30) | `v2.2.2` = cùng SHA | MIT © 2026 Affaan Mustafa | chép |
| `garrytan/gstack` | `main` | `96764e80a641e28141ec8297223768029f5bf483` (2026-09-29), `VERSION` 1.91.9.0 | không có tag | MIT © 2026 Garry Tan | chép |
| `obra/superpowers-lab` | `main` | `51111f74f24058117752d9aa917cb19859f8ec86` (2026-06-01) | `v0.5.0` = cùng SHA | MIT © 2025 Jesse Vincent | chép |
| `obra/superpowers-skills` (lưu trữ 2025-10-14) | `main` | `cdcd624ad3fd8026deb692e565351854569798dd` (2025-10-14) | không có tag | MIT © 2025 Jesse Vincent | chép (nguồn đóng băng) |
| `github/spec-kit` | `main` | `d2ddd910266ad14afe79c5414c88ee316aca6e9a` (2026-09-30) | `v1.0.13` = `f1a548a39dba4e5e8600de1d2e0d3ff0c468d2a9` | MIT © GitHub, Inc. | ý |
| `Fission-AI/OpenSpec` | `main` | `3a34ea309d80df7c5defb388133eceacb4aeba17` (2026-09-30) | `v1.14.0` = `94ca9c1eb15d1b49c06c988419b75c3d95f8b2b5` | MIT © 2024 OpenSpec Contributors | ý |

### Bản distill trước đó (private, ngoài repo này)

Hai bộ skill đã được distill một lần trước khi có repo này; Đợt 1 lấy chúng làm điểm xuất phát rồi đối
chiếu với HEAD ở bảng trên.

| Bộ | Mốc bản private (ngày) | Gốc upstream đã ghi | Giấy phép | Cách dùng |
|---|---|---|---|---|
| Bộ skill quy trình phát triển (15 skill) | `4c0fdc5736a49b6223a7dfc7626d5495cf55185c` (2026-09-05) | 10 skill gốc Academy (chép một chiều 2026-08-15, không giấy phép); 4 skill từ `garrytan/gstack` `656df0e37`; 1 từ `alibaba/open-code-review` (thành phần Bỏ); 1 tự viết | hỗn hợp | Academy → **private**; gstack → chép |
| Bộ skill và agent kỹ thuật (21 skill, 8 agent) | `3599962a013653191c41676021c7e7dc519ee351` (2026-08-26) | `affaan-m/ECC` `d8409a4b0`; `security-audit` từ gstack `cso` @ `656df0e37` | MIT | chép |
| Superpowers bản đã cài | `v6.4.1` = `5bf4e78011075bcfc0dc295f0724994cd123ee71` (2026-09-18) | `obra/superpowers` | MIT | chép |

### Nguồn khái niệm (chỉ lấy ý)

| Nguồn | Mốc | Giấy phép | Cách dùng |
|---|---|---|---|
| BMAD-METHOD (`bmad-code-org/BMAD-METHOD`) | `main` `1cbcfa272fe65787c06a1fa164a901f46117cca7` (2026-09-28) | MIT © 2025 BMad Code, LLC | ý |
| Kiro / EARS | tài liệu `kiro.dev/docs/specs/concepts/` | tài liệu sản phẩm, không giấy phép mở; EARS là phương pháp công bố học thuật | ý |
| Shape Up (Basecamp) | `basecamp.com/shapeup`, đọc 2026-10-01 | giữ mọi quyền | ý, không trích |
| Scrum Guide 2020 | `scrumguides.org`, đọc 2026-10-01 | CC BY-SA 4.0 | ý, không chép |
| Google eng-practices (`google/eng-practices`, lưu trữ) | `master` `3bb3ec25b3b0199f4940b1aa75f0ac5c5753301c` (2024-09-19) | CC BY 3.0 | ý + ghi nguồn |
| OWASP ASVS (`OWASP/ASVS`) | `master` `2b300716ebbef654788d0a14d6c878cecc70c2e9` (2026-09-03) | CC BY-SA 4.0 | ý, không chép câu yêu cầu |
| Nguồn văn phong (BLUF, Minto, plain language, Google dev style, Diátaxis, Microsoft style, NN/g, hướng dẫn prompting Anthropic) | tài liệu web | nhiều loại; giấy phép từng trang chưa đọc | ý |

### Công cụ chỉ gọi, không chép

| Nguồn | Mốc | Giấy phép | Cách dùng |
|---|---|---|---|
| caveman (`JuliusBrussee/caveman`) | `main` `f5d729488caa8f6a5b6c8086fe2cccd3e8a63f91` (2026-09-30) | Apache-2.0 | ý; không cài |
| ccusage (`ryoppippi/ccusage`) | `main` `1597d65298b6ad93abc8fa174c3bcf78ae86e27a` (2026-10-01) | MIT | gọi `npx ccusage@latest` để đo |
| repomix (`yamadashy/repomix`) | `main` `0b3f82b401bbc520fd1aca67c06d24e40a868d3e` (2026-09-28) | MIT | gọi qua `npx` khi cần |
| open-code-review (`alibaba/open-code-review`) | `main` `a758d9cbfb689937c7857ad64b2dd66adb58c0c2` (2026-09-29) | Apache-2.0 | thành phần Bỏ; ghi để tra |
