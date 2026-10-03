# Chiến lược triển khai chi tiết

> **Kết luận:** rolling là mặc định cho thay đổi tương thích ngược; blue-green khi cần hoàn tác tức thì và
> chịu được gấp đôi hạ tầng; canary khi muốn thử bản mới trên lưu lượng thật trước khi mở rộng. Cả ba đều
> cần health check và giám sát mới an toàn.

## 1. Rolling (mặc định)

Thay dần từng instance — bản cũ và bản mới chạy song song trong lúc chuyển.

```
Instance 1: v1 → v2  (update first)
Instance 2: v1
Instance 3: v1

Instance 1: v2
Instance 2: v1 → v2  (update second)
Instance 3: v1

Instance 1: v2
Instance 2: v2
Instance 3: v1 → v2  (update last)
```

- **Được:** không dừng dịch vụ, chuyển dần.
- **Mất:** hai bản chạy cùng lúc → thay đổi (API, schema) phải tương thích ngược.
- **Dùng khi:** deploy thường ngày, thay đổi tương thích ngược.

## 2. Blue-green

Hai môi trường giống hệt nhau; chuyển lưu lượng một lần.

```
Blue  (v1) ← traffic
Green (v2)   idle, running new version

# After verification:
Blue  (v1)   idle (standby)
Green (v2) ← traffic
```

- **Được:** hoàn tác tức thì (chuyển về blue), cắt chuyển gọn.
- **Mất:** gấp đôi hạ tầng trong lúc deploy.
- **Dùng khi:** dịch vụ quan trọng, không chấp nhận sự cố.

## 3. Canary

Một phần nhỏ lưu lượng sang bản mới trước.

```
v1: 95% of traffic
v2:  5% of traffic  (canary)

# If metrics look good:
v1: 50%
v2: 50%

# Final:
v2: 100%
```

- **Được:** bắt lỗi trên lưu lượng thật trước khi mở toàn bộ.
- **Mất:** cần hạ tầng chia lưu lượng và giám sát theo bản.
- **Dùng khi:** lưu lượng cao, thay đổi rủi ro, đi cùng feature flag.

Mỗi bước tăng lưu lượng canary trên production là một hành động ra ngoài: theo điều kiện dừng ở SKILL
mục 4.
