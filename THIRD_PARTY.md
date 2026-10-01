# Nguồn bên thứ ba

KHUNG — điền đủ khi distill (Đợt 1). Mốc SHA và ngày của từng nguồn ở [UPSTREAM.md](UPSTREAM.md);
thông báo bản quyền phải mang theo ở [NOTICE](NOTICE).

## Nguồn chép được (MIT)

| Nguồn | Giấy phép | Dùng cho |
|---|---|---|
| `obra/superpowers` | MIT | Skill quy trình, kỹ thuật, kiểm định, meta |
| `obra/superpowers-lab` | MIT | Tham chiếu tìm hàm trùng lặp (Đợt 2) |
| `obra/superpowers-skills` | MIT | Đối chiếu debugging và tdd |
| `affaan-m/ECC` | MIT | Skill kỹ thuật, agent reviewer |
| `garrytan/gstack` | MIT | Review plan, kiểm bảo mật, QA web, retro |

## Nguồn chỉ lấy ý (không chép văn bản)

| Nguồn | Giấy phép | Vì sao chỉ lấy ý | Dùng cho |
|---|---|---|---|
| `github/spec-kit` | MIT | Không cài; chỉ cần khái niệm | Mã `US`/`FR`/`SC`, câu cần làm rõ |
| `Fission-AI/OpenSpec` | MIT | Không cài; chỉ cần khái niệm | Spec sống theo tính năng, thay đổi dạng delta |
| BMAD-METHOD | MIT | Chỉ cần khái niệm | Vai agile cho agent |
| Kiro / EARS | tài liệu sản phẩm | Không có giấy phép mở | Dạng kịch bản KHI…THÌ… |
| Shape Up | giữ mọi quyền | Không được trích | Sprint là một mục tiêu, giới hạn công sức |
| Scrum Guide 2020 | CC BY-SA 4.0 | Chia-sẻ-tương-tự | Mục tiêu sprint, review/retro |
| Google eng-practices | CC BY 3.0 | Chỉ trích ngắn có ghi nguồn | Chuẩn review |
| OWASP ASVS | CC BY-SA 4.0 | Chia-sẻ-tương-tự | Danh mục kiểm bảo mật |
| caveman | Apache-2.0 | Không cài, chỉ lấy lối viết gọn | Luồng giữa agent |
| Nguồn văn phong | nhiều loại | Giấy phép từng trang chưa đọc | Skill văn phong phản hồi |

## Nguồn private (phải viết lại trước khi công khai)

| Nguồn | Giấy phép | Ghi chú |
|---|---|---|
| 10 skill gốc Academy | không có | File distill từ nguồn này gắn `rewrite_before_public: true` trong frontmatter |

## Công cụ chỉ gọi

| Công cụ | Giấy phép | Cách gọi |
|---|---|---|
| ccusage | MIT | `npx ccusage@latest` |
| repomix | MIT | `npx repomix` khi cần |
