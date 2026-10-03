# invoice-hub — cấu hình chạy production, được app/__init__.py nạp khi khởi động.
# GIÁ TRỊ GIẢ: khoá và mật khẩu trong file này không phải khoá thật của nhà cung cấp nào.
import os

ENV = os.environ.get("APP_ENV", "production")
DEBUG = False
SECRET_KEY = os.environ["FLASK_SECRET_KEY"]

# Cổng thanh toán PayGate — khoá của tài khoản production.
PAYGATE_API_KEY = "pg_prod_4f9c2e71b8a35d60e1c7"
PAYGATE_WEBHOOK_SECRET = os.environ.get("PAYGATE_WEBHOOK_SECRET", "")

DATABASE_URL = "postgresql://invoice_app:Hd8-quartz-41-lantern@db-prod.invoicehub.example:5432/invoices"

LLM_API_URL = "https://llm.internal.invoicehub.example/v1/chat"
