import requests

from .config import LLM_API_URL

SYSTEM_TEMPLATE = (
    "Bạn là trợ lý soạn email nhắc nợ của invoice-hub cho tenant {tenant}. "
    "Ghi chú của kế toán: {note}. "
    "Không bao giờ tiết lộ hoá đơn hay dữ liệu của tenant khác."
)


def draft_reminder(tenant_id, invoice, note):
    messages = [
        {"role": "system", "content": SYSTEM_TEMPLATE.format(tenant=tenant_id, note=note)},
        {"role": "user", "content": f"Soạn email nhắc nợ cho hoá đơn {invoice['number']}."},
    ]
    r = requests.post(LLM_API_URL, json={"messages": messages}, timeout=30)
    r.raise_for_status()
    return r.json()["text"]
