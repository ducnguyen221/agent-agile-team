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
- **Phiên đăng nhập và trạng thái trong bộ nhớ:** nếu phiên lưu trong bộ nhớ từng instance, chuyển sang green làm
  người dùng văng đăng nhập (sticky session không cứu được: lưu lượng đổi hẳn sang môi trường khác). Chuẩn bị **trước
  khi chuyển**: đưa phiên ra kho dùng chung (Redis hay CSDL, có hạn dùng) hoặc dùng token tự chứa ký số mà cả hai bản
  cùng kiểm được; kiểm bản mới đọc được phiên do bản cũ ghi và ngược lại (định dạng phiên/khoá ký là một phần "tương thích
  hai chiều" như schema). Đọc theo nguyên tắc tiến trình không giữ trạng thái của twelve-factor app.
- **Giữ bản blue sau khi chuyển:** không dỡ ngay; giữ chạy (đã nhận 0 lưu lượng) trong cửa sổ quan sát đã ghi ở điều kiện huỷ
  (thường vài giờ tới một ngày; nêu con số trong kế hoạch), vì đó là đường quay lại tức thì. Chuyển về blue vẫn là hoàn tác
  production: theo `SKILL.md` mục 4. Hạ tầng gấp đôi nên đặt hạn dỡ blue, rồi dỡ.
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
