# Xác thực, rate limit, phiên bản

> **Kết luận:** xác thực qua header (bearer cho người dùng, API key cho máy với máy), kiểm quyền ở **mức
> tài nguyên** chứ không chỉ mức đăng nhập, trả 429 kèm `Retry-After` khi vượt hạn mức, và phiên bản
> trong URL với tối đa hai bản sống song song. Ví dụ khoá trong tài liệu luôn là chỗ trống (`...`), không
> bao giờ trông như khoá thật.

## 1. Xác thực

```
# Bearer token in Authorization header
GET /api/v1/customers
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# API key (server-to-server)
GET /api/v1/data
X-API-Key: sk_live_...
```

Không đặt token hay khoá trong query string: nó lọt vào log truy cập, lịch sử trình duyệt và thông điệp
lỗi của HTTP client.

## 2. Kiểm quyền

```typescript
// Resource-level: check ownership
app.get("/api/v1/orders/:id", async (req, res) => {
  const order = await Order.findById(req.params.id);
  if (!order) return res.status(404).json({ error: { code: "not_found" } });
  if (order.userId !== req.user.id) return res.status(403).json({ error: { code: "forbidden" } });
  return res.json({ data: order });
});

// Role-based: check permissions
app.delete("/api/v1/customers/:id", requireRole("admin"), async (req, res) => {
  await Customer.delete(req.params.id);
  return res.status(204).send();
});
```

## 3. Rate limit

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000

# When exceeded
HTTP/1.1 429 Too Many Requests
Retry-After: 60
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```

| Bậc | Hạn mức | Cửa sổ tính theo | Dùng cho |
|---|---|---|---|
| Ẩn danh | 30/phút | IP | endpoint công khai |
| Đã xác thực | 100/phút | người dùng | truy cập API thường |
| Trả phí | 1000/phút | API key | gói API trả phí |
| Nội bộ | 10000/phút | dịch vụ | dịch vụ gọi dịch vụ |

Con số là điểm khởi đầu; chỉnh theo số đo tải thật.

## 4. Phiên bản

| Cách | Ví dụ | Được | Mất |
|---|---|---|---|
| **Trong URL** (khuyến nghị) | `/api/v1/customers`, `/api/v2/customers` | rõ ràng, dễ định tuyến, cache được | URL đổi giữa các bản |
| Trong header | `Accept: application/vnd.myapp.v2+json` | URL sạch | khó test, dễ quên |

Chiến lược:

1. Bắt đầu với `/api/v1/`; chưa cần thì chưa tạo bản mới.
2. Tối đa **hai** bản sống song song (hiện hành + trước đó).
3. Ngừng hỗ trợ: báo trước (API công khai: 6 tháng), thêm header
   `Sunset: Sat, 01 Jan 2026 00:00:00 GMT`, sau ngày đó trả `410 Gone`.
4. **Không phá vỡ** (không cần bản mới): thêm trường vào response, thêm tham số query tuỳ chọn, thêm
   endpoint.
5. **Phá vỡ** (cần bản mới hoặc giai đoạn chuyển + ADR): bỏ hoặc đổi tên trường, đổi kiểu trường, đổi
   cấu trúc URL, đổi cách xác thực.
