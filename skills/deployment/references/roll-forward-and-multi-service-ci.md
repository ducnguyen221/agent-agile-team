# Vá tiến hay quay lui, và pipeline cho nhiều dịch vụ

> **Kết luận:** gặp sự cố sau deploy, **quay lui** nếu bản cũ chạy được trên dữ liệu hiện tại và hoàn tác nhanh hơn vá;
> **vá tiến** khi quay lui không an toàn hoặc chậm hơn bản vá đã hiểu nguyên nhân; **tắt feature flag** nhanh hơn cả hai. Ngưỡng
> và hạn chót ghi **trước** khi bật lưu lượng. Repo nhiều dịch vụ: một job xác định dịch vụ nào đổi, ma trận build/test/deploy chỉ
> chạy cho dịch vụ đó, cache tách theo dịch vụ, các job độc lập chạy song song.

## 1. Vá tiến hay quay lui

`SKILL.md` mục 3: chạm điều kiện huỷ thì hoàn tác theo kế hoạch đã ghi. Mục này nói khi nào **không** nên hoàn tác mà đi tiếp,
và xử lý thay đổi schema đã lên.

| Câu hỏi | Quay lui (rollback) | Vá tiến (roll forward) |
|---|---|---|
| Bản cũ có chạy được trên **dữ liệu hiện tại** không (dữ liệu bản mới đã ghi, schema đã đổi)? | có → quay lui được | không (bản cũ đọc lỗi/ghi hỏng) → vá tiến |
| Hoàn tác mất bao lâu so với đưa bản vá qua pipeline? (số đo ở staging, `SKILL.md` mục 5) | hoàn tác nhanh hơn → quay lui | bản vá nhanh hơn hoặc ngang **và** đã hiểu nguyên nhân → có thể vá tiến |
| Lỗi chỉ ở một tính năng có feature flag? | — | tắt flag (không cần deploy) |
| Đang gây hại lan rộng (mất dữ liệu, sai tiền, sập)? | quay lui/tắt flag ngay, điều tra sau | không vá "thử xem" trong lúc sự cố đang lan |
| Đã hiểu nguyên nhân gốc chưa? | chưa → quay lui rồi điều tra (skill `debugging`) | rồi → vá nhỏ, có test hồi quy |

- **Mặc định quay lui** khi chưa chắc: nó trả hệ thống về trạng thái đã biết. Vá tiến là bản **mới** chưa từng chạy trên tải thật; nó vẫn đi
  qua pipeline đầy đủ (test, staging, smoke test) — không bỏ bước để "nhanh", và production vẫn chờ người dùng gật (`SKILL.md` mục 4).
  Nhánh vá bắt đầu từ **tag/commit đang chạy** (skill `worktrees`, `references/integration-and-special-cases.md` mục 2), không từ đầu nhánh chính nếu nhánh chính đã có thay đổi khác.
- **Ngưỡng cụ thể ghi trước, theo số đo nền của từng dịch vụ** (không có con số chung). Ví dụ minh hoạ: huỷ khi tỉ lệ lỗi cao hơn gấp 2 lần nền suốt 5
  phút hoặc độ trễ p95 quá 1,5 lần nền; **hạn chót vá:** nếu sau T phút (ví dụ 15) chưa có bản vá đã qua staging thì quay lui. Mỗi dịch vụ ghi
  bộ số của mình cùng người duyệt; thiếu số đo nền thì đo trước khi deploy (`SKILL.md` mục 3).
- Sau khi xử lý: ghi sự cố vào REQUESTS (skill `bug-triage`), ghi `VR` bằng lệnh + kết quả mới chạy.

**Schema đã đổi — cột `NOT NULL` vừa thêm.** Bản mới đã lên với migration thêm cột `NOT NULL` rồi hỏng; bản cũ không biết cột đó nên mỗi `INSERT`
thiếu cột bị từ chối. Quay lui mã **không đủ** nếu chưa xử lý cột. Chọn theo thứ tự ưu tiên (dữ liệu đã ghi vào cột là thứ không được làm mất):

1. **Giữ cột, nới ràng buộc** — `ALTER TABLE … ALTER COLUMN … DROP NOT NULL` (hoặc `SET DEFAULT` nếu giá trị mặc định hợp lệ): bản cũ ghi được, dữ liệu
   đã có giữ nguyên, đảo ngược được. Thao tác chỉ đổi metadata, không quét bảng, nhưng cần khoá ngắn: đặt `lock_timeout` ở phiên chạy
   (`references/postgres-safe-ddl.md` của skill `database-migrations`, mục 6). Đây là lựa chọn mặc định.
2. **Giữ cột và `NOT NULL`, vá tiến** — khi bản vá nhanh hơn và bản cũ không cần ghi vào bảng đó nữa.
3. **Bỏ cột** (`DROP COLUMN`) — chỉ khi cột **chưa có dữ liệu thật** hoặc dữ liệu trong đó đã sao lưu; mất dữ liệu không lấy lại được, và bản mới đang chạy
   sẽ lỗi nếu còn dùng cột. Bỏ cột đi qua bước gỡ mã trước (skill `database-migrations`, mục 3); cần người dùng gật.

Chạy migration, kể cả migration hoàn tác, trên dữ liệu thật là hành động không đảo ngược: trình lệnh + ảnh hưởng + cách hoàn tác, chờ gật (`SKILL.md` mục 4).
Cách phòng từ đầu: cột mới phải cho phép rỗng hoặc có mặc định (`database-migrations`, mục 2) — khi đó quay lui mã luôn an toàn. Lệnh `DROP NOT NULL` chưa chạy trên Postgres thật trong lượt này.

## 2. Pipeline nhiều dịch vụ: chỉ build dịch vụ đổi, cache theo dịch vụ, chạy song song

**Xác định dịch vụ nào đổi.** Hai cách:

- **Bộ lọc `paths` ở workflow** (mỗi dịch vụ một workflow, `on.push.paths: ['services/api/**']`): đơn giản nhưng workflow bị bỏ qua vì bộ lọc thì
  check bắt buộc của nó **kẹt ở "Pending" và chặn gộp** (tài liệu GitHub: "tránh đặt bắt buộc cho workflow có thể bị bỏ qua") — đừng dùng cho check bắt buộc.
- **Một workflow + job `changes`** tính danh sách dịch vụ đổi rồi dựng ma trận (khuyến nghị): job luôn chạy nên check bắt buộc luôn có kết quả.

```bash
#!/bin/bash
# ci/changed-services.sh <base-sha> [head]: in mảng JSON tên dịch vụ cần build
set -euo pipefail
BASE="${1:?base sha}"; HEAD_SHA="${2:-HEAD}"
shared_re='^(libs/|\.github/workflows/|docker/base/)'     # vùng dùng chung: đổi là build mọi dịch vụ phụ thuộc
all=1
if git rev-parse --verify -q "$BASE^{commit}" >/dev/null; then all=0; changed="$(git diff --name-only "$BASE" "$HEAD_SHA")"; fi
names=()
for dir in services/*/; do
  name="$(basename "$dir")"
  if [ "$all" = 1 ] || grep -Eq "^services/$name/" <<<"$changed" || grep -Eq "$shared_re" <<<"$changed"; then
    names+=("$name")      # không biết base (lần đẩy đầu, force-push) → build tất cả; build thiếu nguy hiểm hơn build thừa
  fi
done
out="["
for i in "${!names[@]}"; do out+="\"${names[$i]}\""; [ "$i" -lt $((${#names[@]} - 1)) ] && out+=","; done
echo "$out]"
```

Đã chạy lại script trên kho thử: đổi `services/web/` → `["web"]`; đổi `libs/` → mọi dịch vụ; không đổi gì → `[]`; base không tồn tại → mọi dịch vụ.
Vùng dùng chung (thư viện, base image, chính workflow) phải được liệt kê — quên một vùng là build thiếu. Với `pull_request` so với nhánh đích
(`github.event.pull_request.base.sha`), với `push` lên nhánh chính so với `github.event.before`; checkout cần đủ lịch sử (`fetch-depth: 0` hoặc đủ sâu để có `base`).

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.diff.outputs.services }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - id: diff
        run: echo "services=$(bash ci/changed-services.sh "${{ github.event.pull_request.base.sha || github.event.before }}")" >> "$GITHUB_OUTPUT"

  build:
    needs: changes
    if: needs.changes.outputs.services != '[]'
    strategy:
      fail-fast: false                                   # một dịch vụ hỏng không huỷ các dịch vụ khác
      matrix:
        service: ${{ fromJSON(needs.changes.outputs.services) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: services/${{ matrix.service }}
          tags: registry.example.com/${{ matrix.service }}:${{ github.sha }}
          cache-from: type=gha,scope=${{ matrix.service }}
          cache-to: type=gha,scope=${{ matrix.service }},mode=max

  ci-ok:                                                 # MỘT check bắt buộc cho cả pipeline
    needs: [changes, build]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - run: test "${{ contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled') }}" = "false"
```

- **Ma trận theo dịch vụ:** `strategy.matrix.service` từ `fromJSON(...)`: mỗi dịch vụ một job riêng, chạy **song song**; `fail-fast: false` để thấy hết dịch vụ hỏng,
  `max-parallel` nếu cần giới hạn tải/runner. Dịch vụ không đổi không có job nên không tốn thời gian.
- **Cache theo dịch vụ.** Cache layer Docker (BuildKit GitHub Actions cache): mặc định mọi lần build ghi vào cùng khoá `buildkit` nên **các dịch vụ ghi đè cache của nhau**; đặt
  `scope=<dịch vụ>` để mỗi dịch vụ giữ cache riêng (tài liệu Docker, "GitHub Actions cache"; cache chỉ truy cập được từ nhánh hiện tại, nhánh đích và nhánh mặc định). Cache phụ thuộc
  (npm, pip, Go module): khoá theo lockfile của **chính dịch vụ** (`hashFiles('services/<tên>/package-lock.json')`), không một khoá chung. Sắp xếp Dockerfile để lớp phụ thuộc đứng trước mã (`references/dockerfiles.md`).
- **Song song hoá:** job không có `needs` chạy cùng lúc — tách lint, kiểm kiểu, test đơn vị ra các job riêng thay vì một job tuần tự; chỉ đặt `needs` giữa các bước thật sự phụ thuộc
  (test → build → quét → deploy). Test chậm của một dịch vụ chia nhỏ bằng ma trận con (nhóm test). Deploy mỗi dịch vụ một job, `concurrency: deploy-<dịch vụ>` để hai lần deploy cùng dịch vụ
  không đè nhau mà khác dịch vụ vẫn song song.
- **Giữ nguyên luật cũ:** production nhận **đúng image** đã qua staging (`SKILL.md` mục 2), tag bằng mã commit; dịch vụ không đổi thì **không build lại và không deploy lại**,
  nhưng vẫn có thể cần deploy khi hợp đồng chung (API, schema) mà nó dùng đã đổi — liệt kê quan hệ phụ thuộc trong script (ví dụ `libs/` đổi → build dịch vụ phụ thuộc).
  Check bắt buộc đặt ở job `ci-ok` duy nhất để job bị bỏ qua không làm kẹt gộp.

## Nguồn

Tài liệu GitHub (Environments, chạy workflow có `paths`, khắc phục required status checks khi workflow bị bỏ qua), tài liệu Docker (BuildKit cache backend `gha`: `scope`,
`mode`), tài liệu PostgreSQL (`ALTER TABLE`). Script `changed-services.sh` và nhánh xử lý base thiếu đã chạy trên kho git thử; mẫu YAML đã kiểm cú pháp; chưa chạy trên runner thật.
