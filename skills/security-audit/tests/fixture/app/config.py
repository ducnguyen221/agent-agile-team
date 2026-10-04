# invoice-hub — cấu hình chạy production, được app/__init__.py nạp khi khởi động.
# GIÁ TRỊ GIẢ: khoá và mật khẩu trong file này không phải khoá thật của nhà cung cấp nào.
import os

ENV = os.environ.get("APP_ENV", "production")
DEBUG = False
SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

# Cổng thanh toán PayGate — khoá của tài khoản production.
PAYGATE_API_KEY = "pg_prod_fixture_not_a_real_key"
PAYGATE_WEBHOOK_SECRET = os.environ.get("PAYGATE_WEBHOOK_SECRET", "")

DATABASE_URL = "postgresql://invoice_app:fixture-not-a-real-password@db-prod.invoicehub.example:5432/invoices"

LLM_API_URL = "https://llm.internal.invoicehub.example/v1/chat"
