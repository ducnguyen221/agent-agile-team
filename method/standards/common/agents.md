---
title: Agents — delegation and parallel work
type: method
status: active
updated: 2026-10-04
---


# Giao việc cho agent

> **Kết luận:** việc độc lập thì giao song song; ai giao việc thì **sở hữu việc thu kết quả**; mỗi agent kết
> thúc bằng thông điệp cuối là sản phẩm của nó. Chọn vai, tier và agent theo `AGENTS.md`, không theo tên model
> hay thói quen; gọi chéo sang hãng khác chỉ khi người dùng yêu cầu.

## Chọn ai làm

- Vai và tier: `AGENTS.md` (mục Vai và tier) và `roles/README.md`; đọc bảng tier → model từ nguồn cấu hình ngoài repo, thiếu
  thì hỏi, không đoán. Giao việc xong ghi **vai · tier · model** vào PROGRESS.
- Reviewer là agent khác người làm; agent chuyên đề (bảo mật, dữ liệu, Python, FastAPI…) chỉ kéo khi rủi ro
  của việc thật sự thuộc chuyên đề đó — skill `code-review` quyết định.
- Cạn hạn mức: dừng tier đó và báo; không tự hạ tier.
- Gọi chéo sang hãng khác chỉ khi người dùng yêu cầu; agent tự thấy cần thì nói rõ cần hỏi gì và xin một lần.

## Việc song song

- Việc **độc lập** (không dùng kết quả của nhau, không sửa cùng file) thì giao cùng lúc, mỗi agent một brief.
- Việc có phụ thuộc thì chạy tuần tự; ví dụ ba reviewer đọc ba mô-đun khác nhau chạy song song, còn bước sửa
  theo phát hiện của họ chạy sau.
- Nhiều agent cùng ghi vào một kho thì mỗi agent một worktree riêng (skill `worktrees`).

## Hợp đồng hoàn tất

Áp dụng cho mọi agent ở mọi độ sâu (cha, con, cháu):

1. **Thông điệp cuối của bạn là sản phẩm.** Không kết thúc lượt bằng "đang chờ agent nền" — việc đã giao chưa
   xong thì chưa hoàn thành, kết quả của agent con sẽ mồ côi khi lượt của cha đã đóng.
2. **Đã giao thì sở hữu việc thu về:** chờ kết quả, tích hợp, rồi mới trả. Giao mà bỏ đó là điều cấm.
3. **Chỉ chia nhỏ khi việc không vừa một ngữ cảnh.** Không giao lại việc đã được cỡ cho đúng một agent; độ sâu
   là hệ quả, không phải kế hoạch. Brief cấm giao tiếp thì làm theo brief.

Báo cáo giữa agent theo văn phong ở `AGENTS.md` (Kết quả / Chứng cứ / Còn mở / Cần người).

## Nhiều góc nhìn cho việc phức tạp

Việc khó có thể cần nhiều reviewer độc lập, mỗi người một vai: kiểm tính đúng sự thật, kỹ sư cao cấp, bảo
mật, tính nhất quán, tìm phần thừa. Mỗi reviewer nhận brief riêng, không đọc lịch sử của người làm; điều phối
hợp nhất phát hiện, chuẩn hoá mức theo `method/severity.md`.
