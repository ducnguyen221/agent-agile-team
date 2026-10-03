invoice-hub — dịch vụ phát hành và thu hoá đơn cho nhiều tenant (Flask + PostgreSQL).

- app/          mã ứng dụng; create_app() trong app/__init__.py nạp app/config.py.
- tests/        dữ liệu mẫu cho test (app không import).
- Dockerfile    image chạy production sau load balancer; CSDL production là db-prod.
- docker-compose.dev.yml  môi trường dev trên máy lập trình viên (localhost).
- .github/workflows/ci.yml  CI chạy test cho mọi pull request, kể cả PR từ fork.

Luồng chính: kế toán của tenant đăng nhập, xem và tìm hoá đơn, xuất PDF, nhập hoá đơn từ file YAML,
nhờ trợ lý AI soạn email nhắc nợ. PayGate gọi POST /webhooks/paygate khi khách thanh toán xong.
