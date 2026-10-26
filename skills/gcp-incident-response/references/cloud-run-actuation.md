# Cloud Run — từ giảm thiểu sang lệnh `gcloud`

> Nguồn: distill từ gemini-cli-extensions/sre (Apache-2.0), đã sửa và rút gọn.

Placeholder: `<SERVICE>`, `<REGION>`, `<REVISION_GOOD>`, `<IMAGE>`, `<N>`. Dịch vụ chạy trên Cloud Run; cơ chế traffic chi tiết ở
skill `gcp-devops` (`references/cloud-run-deploy.md`). Mọi lệnh ghi gắn nhãn rủi ro theo `SKILL.md` mục 2 trước khi chạy.

## Contents

1. Bảng giảm thiểu → lệnh · 2. Drain theo vùng · 3. Ghi chú shell · 4. Ngoài phạm vi (GKE)

## 1. Bảng giảm thiểu → lệnh

| Giảm thiểu | Nghĩa trên Cloud Run | Lệnh |
|---|---|---|
| **Rollback** | chuyển 100% traffic sang revision tốt cũ (revision bất biến) | `gcloud run services update-traffic <SERVICE> --to-revisions=<REVISION_GOOD>=100 --region=<REGION>` |
| **Fix forward** | build + deploy image đã vá; revision mới nhận 100% theo mặc định | `gcloud run deploy <SERVICE> --image=<IMAGE> --region=<REGION>` |
| **Upsize** | tăng `--max-instances`, hoặc `--cpu`/`--memory` nếu OOM/đói CPU (sinh revision mới) | `gcloud run services update <SERVICE> --max-instances=<N> --region=<REGION>` · `--memory=2Gi --cpu=2` |
| **Drain traffic** | chia traffic gốc chỉ **theo revision trong một vùng** — rút một *vùng* phải ngừng định tuyến ở backend **GCLB** | quản ở load balancer của bạn (xem `gcp-devops` `references/lb-tls.md`) |
| **Degrade** | không có nút gốc — bật/tắt biến môi trường hoặc feature flag ở tầng ứng dụng để tắt đường không thiết yếu | `gcloud run services update <SERVICE> --update-env-vars=FEATURE_X=off --region=<REGION>` |
| **Restart** | serverless — không restart từng instance; ép một revision mới không đổi gì để quay vòng mọi instance | `gcloud run services update <SERVICE> --update-env-vars=FORCE_RESTART=$(date +%s) --region=<REGION>` |

## 2. Drain theo vùng là việc của GCLB

⚠️ Sai lầm phổ biến nhất khi giảm thiểu trên Cloud Run: cố rút một vùng bằng `update-traffic`, lệnh chỉ chia revision **bên trong
một vùng**. Muốn drain vùng, thao tác ở backend của GCLB của bạn (gỡ hoặc đặt capacity 0 cho backend NEG của vùng đó), và chắc
chắn vùng còn lại hấp thụ nổi phần dồn — nếu không sự cố lan sang vùng khoẻ.

## 3. Ghi chú shell

Hàng **Restart** dùng `$(date +%s)` là bash (Cloud Shell/Linux). Trên **Windows PowerShell** không có `date +%s` — dùng dấu thời
gian Unix thật:

```powershell
gcloud run services update <SERVICE> --update-env-vars=FORCE_RESTART=$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds()) --region=<REGION>
```

## 4. Ngoài phạm vi (GKE)

GKE nằm ngoài phạm vi skill này. Nếu về sau có thêm: rollback = `kubectl rollout undo deployment/<NAME>`; upsize = tăng replica
hoặc giới hạn tài nguyên; restart = `kubectl rollout restart`.
