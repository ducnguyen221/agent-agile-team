# Nguồn bên thứ ba

Mốc SHA và ngày của từng nguồn, cùng bảng nguồn theo từng skill và agent, ở [UPSTREAM.md](UPSTREAM.md);
thông báo bản quyền phải mang theo ở [NOTICE](NOTICE). File này ghi **vì sao** mỗi nguồn được dùng theo
cách đó, các nguồn **chỉ lấy ý**, và danh sách file **phải viết lại trước khi công khai**.

## 1. Nguồn chép được (MIT) — đã dùng ở Đợt 1

| Nguồn | Giấy phép | Dùng cho |
|---|---|---|
| `obra/superpowers` | MIT | Skill quy trình (`shaping-spec`, `writing-plan`, `running-sprint`, `closing-sprint`), kỹ thuật (`tdd`, `debugging`, `worktrees`), kiểm định (`verify-before-done`, `code-review`), meta (`writing-skills`) |
| `obra/superpowers-skills` | MIT | Đối chiếu và bổ sung `tdd`, `debugging` (nguồn đóng băng) |
| `affaan-m/ECC` | MIT | Skill kỹ thuật (`python`, `fastapi`, `postgres`, `database-migrations`, `api-design`, `error-handling`, `deployment`, `github-ops`), `security-review`, `intake`, `token-economy`, phần bài học của `closing-sprint`; 7 agent reviewer |
| `garrytan/gstack` | MIT | `plan-review`, `security-audit`, `web-qa`, phần `debugging` (điều tra), docs-sync và retro của `closing-sprint` |
| `supabase/agent-skills` | MIT | Mẫu Postgres trong `postgres` và agent `database-reviewer` (đến qua ECC) |
| `obra/superpowers-lab` | MIT | Chưa dùng — tham chiếu tìm hàm trùng lặp (Đợt 2) |

## 2. Nguồn chỉ lấy ý (không chép văn bản)

| Nguồn | Giấy phép | Vì sao chỉ lấy ý | Ý đã lấy · ở đâu |
|---|---|---|---|
| GitHub Spec Kit (`github/spec-kit`) | MIT | Không cài; chỉ cần khái niệm | Mã `US`/`FR`/`SC`, câu cần làm rõ → mẫu SPEC, `id-convention`, `shaping-spec` |
| OpenSpec (`Fission-AI/OpenSpec`) | MIT | Không cài; chỉ cần khái niệm | Spec sống theo tính năng, thay đổi dạng delta Thêm / Sửa / Bỏ → `templates/registry/feature-spec.md`, mục "Đổi hợp đồng / giao diện" của mẫu SPEC |
| BMAD-METHOD | MIT | Chỉ cần khái niệm | Vai agile cho agent → `roles/` |
| Kiro / EARS | tài liệu sản phẩm; EARS là phương pháp công bố học thuật | Không có giấy phép mở | Dạng kịch bản KHI…THÌ… → mẫu SPEC, `shaping-spec` |
| Shape Up (Basecamp) | giữ mọi quyền | Không được trích | Sprint là một mục tiêu, giới hạn công sức → `method/` |
| Scrum Guide 2020 | CC BY-SA 4.0 | Chia-sẻ-tương-tự: chép văn bản kéo cả file về CC BY-SA | Mục tiêu sprint, review/retro → `method/`, mục Review & Retro của mẫu REPORT |
| Google eng-practices (`google/eng-practices`) | CC BY 3.0 | Chỉ trích ngắn có ghi nguồn; Đợt 1 không trích | Chuẩn review "chấp nhận khi chất lượng tổng thể tăng, không đòi hoàn hảo" → `roles/verifier/tech-reviewer.md` |
| OWASP ASVS (`OWASP/ASVS`) | CC BY-SA 4.0 | Chia-sẻ-tương-tự; không chép câu yêu cầu | Danh mục chương kiểm bảo mật → `roles/verifier/specialists/security.md`, `security-review` |
| ISO/IEC/IEEE 29148 | tiêu chuẩn có bản quyền | Không được chép | Mã định danh yêu cầu ổn định → `id-convention` |
| MoSCoW | phương pháp, không có văn bản gốc để chép | — | Mức ưu tiên viết bằng chữ (Bắt buộc / Nên có / Có thì tốt / Không làm đợt này) → mẫu SPEC, `id-convention` |
| caveman (`JuliusBrussee/caveman`) | Apache-2.0 | Không cài, chỉ lấy lối viết gọn | Luồng gọn giữa agent → `token-economy` |
| Nguồn văn phong (BLUF, Minto/SCQ, plain language, Google dev style, Diátaxis, Microsoft style, NN/g, hướng dẫn prompting Anthropic) | nhiều loại (phạm vi công cộng, CC BY, CC BY-SA, giữ bản quyền) | Giấy phép từng trang chưa đọc hết — chỉ lấy ý là an toàn dù giả định sai | Kết luận trước, ma trận độ dài, danh sách cấm kèm cách làm thay → `response-style` |

## 3. Nguồn private — phải viết lại trước khi công khai

Bộ skill quy trình private (gốc private, **không giấy phép**) chỉ dùng được khi repo còn private. Cờ
`rewrite_before_public: true` đặt ở **cấp skill** (frontmatter `SKILL.md`); bảng dưới ghi đúng file nào cần
viết lại để không phải viết lại cả skill.

| Skill | File phải viết lại | Nguồn private |
|---|---|---|
| `closing-sprint` | `references/preflight.md`, `references/release-notes.md` | `preflight-gate`, `release-notes-writer` |
| `roles/executor/qa.md` (thẻ vai, không có cờ) | mục 4 cụm "bảng phủ"; mục 5 gạch đầu dòng "bảng phủ `FR` → `VR` theo tầng test" và gạch đầu dòng "`FR` chưa có test, `SC` chưa đo được" | `test-mapper` |
| `scripts/README.md` (tài liệu, không có cờ) | bảng "Luật của `check`", cột "Bắt gì" của bốn luật truy vết `task-without-trace`, `report-sc-without-vr`, `report-fr-without-vr`, `xref-missing` | `rtm-auditor` |

Hai dòng cuối không phải skill nên không có cờ `rewrite_before_public`; bảng này là nơi duy nhất theo dõi
chúng. Văn bản gốc của mọi mục trong bảng đã **gỡ khỏi nhánh** và thay bằng khung "đang viết lại (`TK10`)";
bản mới viết từ danh sách ý, không mở bản gốc.

Trước khi công khai: viết lại các file trên từ ý (không mở bản gốc khi viết), đổi cờ thành `false`, cập nhật
`source`/`license` và dòng tương ứng ở `UPSTREAM.md`.

## 4. Công cụ chỉ gọi

| Công cụ | Giấy phép | Cách gọi |
|---|---|---|
| ccusage | MIT | `npx ccusage@latest` để đo token (skill `token-economy`) |
| repomix | MIT | `npx repomix` khi cần nén repo cho agent |
