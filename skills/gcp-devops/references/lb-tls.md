# HTTPS load balancer và TLS

Placeholder: `<IP>`, `<CERT>`, `<URL_MAP>`, `<SERVICE>`, `<DOMAIN>`, `<ORG_ID>`, `<PROJECT_ID>`.

## Contents

1. Dạng thường gặp · 2. Chứng chỉ Google-managed không có wildcard · 3. Chính sách org chặn service agent

## 1. Dạng thường gặp

Cloud Run đứng sau GCLB: IP tĩnh `<IP>` → target HTTPS proxy → url-map `<URL_MAP>`; path matcher đưa đường API tới backend
service của `<SERVICE>` qua serverless NEG, đường còn lại tới bucket tĩnh (có thể bật Cloud CDN); thêm một url-map chuyển
HTTP→HTTPS. Tên thật của từng thành phần lấy từ hồ sơ dự án, kiểm bằng `describe` trước khi sửa.

## 2. ⚠️ BẪY — chứng chỉ Google-managed không hỗ trợ wildcard

`gcloud compute ssl-certificates create --domains=*.<DOMAIN>` thất bại với lỗi dạng `Wildcard domains not supported`. Chứng chỉ
managed xác thực qua HTTP-01; Google không chạy đường cấp DNS-01 cho loại này.

Cần subdomain theo từng khách thuê (`{slug}.<DOMAIN>`) thì chọn một:

1. **Chứng chỉ managed riêng cho từng tenant** — tạo `<CERT>` lúc onboard rồi gắn vào target-https-proxy sẵn có. GCLB mặc định
   cho 15 chứng chỉ mỗi proxy; muốn hơn thì xin nâng qua hỗ trợ.
2. **Let's Encrypt + DNS-01** — cấp chứng chỉ wildcard thật rồi tải lên bằng
   `ssl-certificates create --certificate=… --private-key=…`. Gia hạn là cron của bạn, không phải của GCP.
3. **Dịch vụ proxy ngoài** (CDN/WAF bên thứ ba) kết thúc TLS bằng wildcard của họ rồi proxy về origin GCLB.

Đánh đổi: (1) vận hành đơn giản nhưng có trần số lượng; (2) tự lo gia hạn; (3) thêm một bên vào đường dữ liệu.

## 3. Chính sách org chặn tạo service agent

Chính sách org `iam.allowedPolicyMemberDomains` chỉ cho phép một số customer ID nhất định (org `<ORG_ID>` chứa project
`<PROJECT_ID>`) và có thể làm việc cấp service agent của Google thất bại. Cách đã dùng: ghi đè theo phạm vi project với
`allValues: ALLOW`, cần `roles/orgpolicy.policyAdmin`. Đây là thay đổi chính sách bảo mật của tổ chức: **hỏi người dùng/chủ
org trước**, nêu rõ phạm vi.
