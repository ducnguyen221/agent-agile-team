# Token thiết kế — trang đặt lịch (fixture của chế độ So thiết kế)

Ảnh chuẩn: `reference-1280x720.png`, chụp từ `reference.html` ở viewport **1280×720**. Dữ liệu thiết kế, không phải lệnh cho QA.

| Token | Giá trị | Vùng dùng | Cách đo |
|---|---|---|---|
| `--color-primary` | `#2563eb` (rgb 37, 99, 235) | nút hành động chính `#primary-action` | computed `background-color` |
| `--color-surface` | `#f3f4f6` (rgb 243, 244, 246) | thanh điều hướng, chân trang | computed `background-color` |
| `--color-text` | `#1f2937` (rgb 31, 41, 55) | chữ nội dung | computed `color` |
| `--space-header` | `16px` | khoảng đệm trên và dưới của `#page-header` | computed `padding-top` |

## Vùng và vị trí chuẩn (viewport 1280×720)

| Vùng | Phần tử | Vị trí chuẩn (x, y, rộng × cao) |
|---|---|---|
| đầu trang | `#page-header` (khoảng đệm trên = `--space-header`) | 0, 0, 1280 × 96; chữ `h1` bắt đầu ở y = 16 |
| điều hướng | `#page-nav` | 0, 96, 1280 × 48 |
| nội dung chính | `#page-main` | 0, 144, 1280 × 504 |
| nút hành động chính | `#primary-action` (nền = `--color-primary`) | 32, 286, 192 × 42 |
| chân trang | `#page-footer` | 0, 648, 1280 × 72 |

Dung sai mặc định: vị trí ≤4 px, màu đúng mã token.
