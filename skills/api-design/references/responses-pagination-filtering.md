# Phong bì response, phân trang, lọc

> **Kết luận:** API công khai bọc dữ liệu trong `data` (+ `meta`, `links` khi là danh sách), lỗi trong
> `error`. Phân trang **cursor** là mặc định cho dữ liệu lớn và feed; **offset** cho tập nhỏ và kết quả
> tìm kiếm cần số trang. Lọc, sắp xếp, chọn trường đi qua query string theo một cú pháp thống nhất.

## 1. Phong bì response

Thành công:

```json
{
  "data": {
    "id": "abc-123",
    "email": "alice@example.com",
    "name": "Alice",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

Danh sách có phân trang:

```json
{
  "data": [
    { "id": "abc-123", "name": "Alice" },
    { "id": "def-456", "name": "Bob" }
  ],
  "meta": { "total": 142, "page": 1, "per_page": 20, "total_pages": 8 },
  "links": {
    "self": "/api/v1/customers?page=1&per_page=20",
    "next": "/api/v1/customers?page=2&per_page=20",
    "last": "/api/v1/customers?page=8&per_page=20"
  }
}
```

Lỗi (kèm lỗi từng trường):

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Must be a valid email address", "code": "invalid_format" },
      { "field": "age", "message": "Must be between 0 and 150", "code": "out_of_range" }
    ]
  }
}
```

Hai biến thể:

```typescript
// Option A: envelope with data wrapper (recommended for public APIs)
interface ApiResponse<T> {
  data: T;
  meta?: PaginationMeta;
  links?: PaginationLinks;
}

interface ApiError {
  error: { code: string; message: string; details?: FieldError[] };
}

// Option B: flat response (simpler, common for internal APIs)
// Success returns the resource directly; error returns the error object;
// distinguish by HTTP status code.
```

## 2. Phân trang

**Offset** — đơn giản, nhảy được tới trang N; chậm khi offset lớn (`OFFSET 100000`) và lệch khi có bản
ghi chèn đồng thời.

```
GET /api/v1/customers?page=2&per_page=20

SELECT * FROM customers
ORDER BY created_at DESC
LIMIT 20 OFFSET 20;
```

**Cursor** — hiệu năng đều ở mọi vị trí, ổn định khi chèn đồng thời; không nhảy trang được, cursor mờ.

```
GET /api/v1/customers?cursor=eyJpZCI6MTIzfQ&limit=20

SELECT * FROM customers
WHERE id > :cursor_id
ORDER BY id ASC
LIMIT 21;  -- fetch one extra to determine has_next
```

```json
{
  "data": [],
  "meta": { "has_next": true, "next_cursor": "eyJpZCI6MTQzfQ" }
}
```

| Trường hợp | Kiểu phân trang |
|---|---|
| Trang quản trị, tập dữ liệu nhỏ (<10 nghìn dòng) | offset |
| Cuộn vô hạn, feed, tập dữ liệu lớn | cursor |
| API công khai | cursor (mặc định), offset (tuỳ chọn) |
| Kết quả tìm kiếm | offset (người dùng quen số trang) |

## 3. Lọc, sắp xếp, tìm kiếm, chọn trường

```
# Simple equality
GET /api/v1/orders?status=active&customer_id=abc-123

# Comparison operators (bracket notation)
GET /api/v1/products?price[gte]=10&price[lte]=100
GET /api/v1/orders?created_at[after]=2025-01-01

# Multiple values (comma-separated)
GET /api/v1/products?category=electronics,clothing

# Nested fields (dot notation)
GET /api/v1/orders?customer.country=US

# Sorting: prefix "-" for descending, comma for multiple fields
GET /api/v1/products?sort=-created_at
GET /api/v1/products?sort=-featured,price,-created_at

# Full-text and field-specific search
GET /api/v1/products?q=wireless+headphones
GET /api/v1/customers?email=alice

# Sparse fieldsets (smaller payload)
GET /api/v1/customers?fields=id,name,email
GET /api/v1/orders?fields=id,total,status&include=customer.name
```

Trường được lọc và sắp xếp phải nằm trong danh sách cho phép; không nối thẳng tên trường từ query vào
SQL (skill `postgres`, `security-review`).
