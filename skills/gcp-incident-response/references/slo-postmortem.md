# SLO qua REST và postmortem

> Nguồn: distill từ gemini-cli-extensions/sre (Apache-2.0), đã sửa và rút gọn.

Placeholder: `<PROJECT_ID>`, `<SERVICE_ID>` (ID của Service trong Monitoring).

## Contents

1. Tạo SLO qua Monitoring REST API · 2. Biến thể và lỗi thường gặp · 3. Postmortem

## 1. Tạo SLO qua Monitoring REST API

`gcloud` **không có** lệnh tạo SLO — dùng Monitoring v3 REST API. Mỗi SLO gắn vào một **Service**: tìm `Service ID` ở console
Monitoring hoặc qua Services API trước.

```bash
# Cloud Shell / Linux
PROJECT_ID="<PROJECT_ID>"; SERVICE_ID="<SERVICE_ID>"   # từ Monitoring Services
TOKEN=$(gcloud auth application-default print-access-token)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "https://monitoring.googleapis.com/v3/projects/$PROJECT_ID/services/$SERVICE_ID/serviceLevelObjectives" \
  -d '{ "displayName": "99% Availability - 7d rolling", "goal": 0.99,
        "rollingPeriod": "604800s",
        "serviceLevelIndicator": { "basicSli": { "availability": {} } } }'
```

```powershell
# Windows PowerShell — cùng lời gọi REST: Invoke-RestMethod, hashtable -> JSON, nối dòng bằng backtick
$ProjectId = "<PROJECT_ID>"; $ServiceId = "<SERVICE_ID>"   # từ Monitoring Services
$Token = (gcloud auth application-default print-access-token)
$body = @{
  displayName           = "99% Availability - 7d rolling"
  goal                  = 0.99
  rollingPeriod         = "604800s"
  serviceLevelIndicator = @{ basicSli = @{ availability = @{} } }
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post `
  -Uri "https://monitoring.googleapis.com/v3/projects/$ProjectId/services/$ServiceId/serviceLevelObjectives" `
  -Headers @{ Authorization = "Bearer $Token" } -ContentType "application/json" -Body $body
```

## 2. Biến thể và lỗi thường gặp

- **SLO độ trễ** — đặt ngưỡng `latency` trong `basicSli` thay cho `availability`.
- **Service tuỳ biến** (ví dụ suy ra từ log frontend) — dùng SLI `requestBased`/`windowBased` kèm bộ lọc metric.
- **403 Forbidden** → người gọi cần `roles/monitoring.editor` **và** đã có ADC (`gcloud auth application-default login`); `gcloud`
  thường chạy được không có nghĩa là ADC đã có.
- ⚠️ **Bẫy danh tính:** danh tính `gcloud auth login` và danh tính ADC có thể khác nhau; lời gọi REST/ADC lỗi quyền dù lệnh
  `gcloud` chạy được. Căn chúng khớp bằng `gcloud auth application-default login --account=<danh tính gcloud>`.
- Đổi SLO ở mức kiến trúc (chọn SLI nào, mục tiêu bao nhiêu cho cả hệ thống) không thuộc skill này.

## 3. Postmortem

Chỉ viết **sau khi** sự cố đã được giảm thiểu và dòng thời gian đã được ghi. Giữ dòng thời gian dạng CSV suốt quá trình điều
tra (`Time, Description, Milestone`, một múi giờ duy nhất) để sắp và gộp sau; đặt cho sự cố một ID ổn định từ hệ theo dõi đang
dùng; tách **dòng thời gian** (cái gì xảy ra, lúc nào) khỏi **hạng mục hành động** (đổi gì, ai giữ). Không đổ lỗi, trích bằng
chứng nguyên văn, viết markdown.
