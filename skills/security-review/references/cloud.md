# Hạ tầng cloud và đường triển khai

> **Kết luận:** dùng khi thay đổi chạm IAM, secret của nền tảng, mạng, log, CI/CD, CDN/WAF hoặc sao lưu.
> Bảy nhóm dưới đây là checklist ý — ví dụ nhà cung cấp chỉ để minh hoạ. Mục không kiểm được ghi
> **Chưa chạy** kèm lý do, không ghi Đạt. Thao tác trên hạ tầng thật là ngoài phạm vi: chỉ đọc cấu hình.

Nguồn: viết lại từ `cloud-infrastructure-security.md` của `affaan-m/ECC` (MIT), mốc ghi ở frontmatter
`SKILL.md`.

## 1. IAM và quyền truy cập
- Quyền tối thiểu: không `*` ở hành động hay tài nguyên nhạy cảm; quyền đọc tách quyền ghi.
- Không dùng tài khoản gốc cho vận hành; MFA cho mọi tài khoản đặc quyền.
- Dịch vụ dùng vai (role) hoặc danh tính workload, không dùng khoá dài hạn.
- Có rà soát quyền định kỳ; khoá không dùng thì thu hồi.

## 2. Secret của nền tảng
- Secret nằm trong kho secret của nền tảng, không trong biến build, image hay file cấu hình commit.
- Xoay vòng tự động cho thông tin đăng nhập CSDL; khoá API có chu kỳ xoay vòng.
- Truy cập secret có log kiểm toán.

## 3. Mạng
- CSDL không mở ra Internet; SSH/RDP chỉ qua VPN hoặc bastion.
- Security group/firewall theo nguyên tắc tối thiểu; không mở `0.0.0.0/0` cho cổng quản trị.
- Có log luồng mạng ở môi trường thật.

## 4. Log và giám sát
- Log bật cho mọi dịch vụ; ghi đăng nhập hỏng, thao tác quản trị.
- Thời gian lưu log theo yêu cầu tuân thủ; log tập trung, chống sửa.
- Cảnh báo cho hoạt động bất thường.

## 5. CI/CD và chuỗi cung ứng
- Workflow chạy với quyền tối thiểu (`permissions` chỉ đọc mặc định).
- Xác thực tới cloud bằng OIDC, không token dài hạn trong secret của CI.
- Action bên thứ ba ghim theo SHA; không nội suy dữ liệu sự kiện (tiêu đề, thân PR/issue) thẳng vào
  bước `run`.
- Pipeline có quét secret, quét lỗ hổng dependency, quét image (nếu có container).
- Nhánh chính được bảo vệ; merge cần review; cài dependency bằng lệnh tái lập được từ lock file.

## 6. CDN và WAF
- WAF bật với bộ luật OWASP; rate limit; chống bot; chống DDoS.
- TLS chế độ nghiêm; header bảo mật đặt ở biên.

## 7. Sao lưu và khôi phục
- Sao lưu tự động hằng ngày; thời gian lưu đúng yêu cầu; khôi phục theo thời điểm khi cần.
- **Đã khôi phục thử** — sao lưu chưa từng khôi phục là chưa có sao lưu.
- Có RPO, RTO và kế hoạch khôi phục thảm hoạ được ghi lại.

## 8. Cấu hình sai hay gặp
- Bucket lưu trữ công khai thay vì riêng tư + quyền cụ thể.
- CSDL bật truy cập công khai.
- Môi trường staging trỏ vào CSDL thật.
- Container chạy bằng root ở môi trường thật.

## 9. Checklist trước deploy hạ tầng
- [ ] IAM tối thiểu, MFA, không tài khoản gốc.
- [ ] Secret trong kho của nền tảng, có xoay vòng.
- [ ] Mạng: không CSDL công khai, cổng quản trị đóng.
- [ ] Log + cảnh báo bật, có thời gian lưu.
- [ ] CI/CD: OIDC, quét secret, quét dependency, action ghim SHA.
- [ ] WAF + rate limit ở biên.
- [ ] Mã hoá khi truyền và khi lưu.
- [ ] Sao lưu tự động, đã khôi phục thử.
- [ ] Có runbook sự cố bảo mật.
