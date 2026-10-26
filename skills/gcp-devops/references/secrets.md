# Secret Manager — gắn, xoay, bẫy

Placeholder: `<SERVICE>`, `<REGION>`, `<SECRET_NAME>`, `<DB_USER>`, `<INSTANCE>`.

## Contents

1. Luật gắn secret · 2. Xoay secret 5 bước · 3. Bẫy secret tách đôi · 4. Mật khẩu và không echo

## 1. Luật gắn secret

Mọi credential nhạy cảm nằm trong Secret Manager và gắn bằng `secretKeyRef`. Không dùng `--update-env-vars=NAME=<giá trị thô>`
cho secret: biến literal của Cloud Run lộ cho ai có `run.viewer` qua `gcloud run services describe`, còn `secretKeyRef`
chỉ lộ tham chiếu.

```bash
gcloud run services update <SERVICE> --region=<REGION> \
  --update-secrets=DATABASE_URL=<SECRET_NAME>:latest
```

## 2. Xoay secret — 5 bước, không phải 1

1. **Đổi hệ thống gốc** (`gcloud sql users set-password`, khoá mới ở nhà cung cấp…).
2. **Thêm version mới từ byte thô** — đừng pipe, PowerShell nhét CRLF vào.

   ```powershell
   [System.IO.File]::WriteAllBytes("$env:TEMP\sec.bin", [Text.Encoding]::ASCII.GetBytes($newValue))
   gcloud secrets versions add <SECRET_NAME> --data-file="$env:TEMP\sec.bin"
   Remove-Item "$env:TEMP\sec.bin" -Force; Clear-Variable newValue
   ```

   ```bash
   # bash: người dùng nhập giá trị (không hiện ra màn hình, không vào lịch sử shell); agent không giữ giá trị
   read -rs NEW_VALUE
   SEC_FILE="$(mktemp)"                     # quyền 0600
   printf '%s' "$NEW_VALUE" > "$SEC_FILE"   # không xuống dòng
   gcloud secrets versions add <SECRET_NAME> --data-file="$SEC_FILE"
   rm -f "$SEC_FILE"; unset NEW_VALUE
   ```

   Trên PowerShell, ghi file vào một thư mục tạm riêng của bạn (không dùng chung thư mục tạm mặc định) và xoá ngay sau
   `gcloud secrets versions add`; đừng thay bằng pipe vào `--data-file=-`, vì pipe PowerShell thêm CRLF.

3. **Giữ nguyên mount và áp lại để sinh revision mới** — bước người ta hay bỏ. Secret chỉ được đọc lúc **container khởi động**,
   nên `:latest` **không** làm mới revision đang chạy; không có revision mới thì xoay không có tác dụng.
4. **Kiểm**: revision mới nhận traffic, rồi smoke test.
5. **Vô hiệu** version cũ (`gcloud secrets versions disable <N> --secret=<SECRET_NAME>`). Disable, không `destroy` — bản bị
   disable còn khôi phục được 30 ngày.

## 3. ⚠️ BẪY — credential tách đôi

Khi cùng một mật khẩu nằm ở hai secret (một secret DSN đầy đủ, một secret mật khẩu riêng), secret riêng có thể **lỗi thời**
vì không ai cập nhật khi mật khẩu xoay, trong khi dịch vụ vẫn chạy vì đọc secret DSN. Cách xử lý:

- Đừng đọc mật khẩu từ secret "đứng cạnh"; nguồn sống là secret mà dịch vụ đang gắn (`<SECRET_NAME>`). Xác nhận bằng
  `describe` dịch vụ xem nó mount secret nào.
- Gặp cặp lệch như vậy thì đề nghị chủ sở hữu hoặc xoay và căn cho khớp cả hai, hoặc xoá secret thừa để bỏ bẫy. Không tự sửa.

## 4. Mật khẩu và không echo

- Tránh `@ : / ? #` trong mật khẩu: chúng làm hỏng việc phân tích URL của DSN (user `<DB_USER>`, instance `<INSTANCE>`).
- **Không bao giờ echo biến secret** trong script. Ngay cả `gcloud secrets versions access` in ra ngữ cảnh của agent cũng là
  đường rò: giá trị nằm trong kết quả công cụ. Muốn giúp mà không thấy giá trị thì nhờ người dùng ghi vào file tạm rồi dùng
  đường dẫn file.
