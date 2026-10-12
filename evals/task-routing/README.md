# Task routing evaluation version 1

Đọc [contract.md](contract.md) trước khi chạy. [cases.jsonl](cases.jsonl) do QA giữ: policy writer chỉ được xem split calibration; không mở holdout trước candidate freeze. [pilot.manifest.json](pilot.manifest.json) chứa refs/coverage, không chứa đáp án. [run.schema.json](run.schema.json) khóa literal `schema=1`, nested shape cho checker. Không có baseline/pilot outcomes trong thư mục này.

Kiểm chuẩn bị bằng Python stdlib hiện có, từ repo root; không cần cài dependency:

```powershell
@'
import hashlib, json
from pathlib import Path
p = Path('evals/task-routing')
cases = [json.loads(line) for line in (p / 'cases.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
m = json.loads((p / 'pilot.manifest.json').read_text(encoding='utf-8'))
s = json.loads((p / 'run.schema.json').read_text(encoding='utf-8'))
assert len(cases) == 36 and len({c['case_id'] for c in cases}) == 36
for split in ('calibration', 'holdout'):
    rows = [c for c in cases if c['split'] == split]
    assert len(rows) == 18
    assert {sc for c in rows for sc in c['sc_refs']} == {'SC' + str(i) for i in range(1, 25)}
    assert all(c['repetitions'] == 3 and c['expected_invariants'] for c in rows)
assert m['schema'] == 1 and s['properties']['schema']['const'] == 1
assert hashlib.sha256((p / 'cases.jsonl').read_bytes()).hexdigest() == m['dataset']['sha256']
assert hashlib.sha256((p / 'run.schema.json').read_bytes()).hexdigest() == m['interface']['sha256']
assert len(m['tasks']) == 36 and not m['budget']['live_authorized']
assert m['budget']['max_calls'] is None and m['budget']['max_elapsed_ms'] is None
assert m['source_coverage']['status'] == 'unknown'
print('Prepared: 36 cases; 18/18; SC1-SC24 each split; hashes valid; live disabled. Not a pilot result.')
'@ | python -
```

Đây là parse/coverage/hash check, chưa là JSON Schema instance-validation hoặc policy evaluation. Checker stdlib đọc schema subset mà nó hỗ trợ và có negative fixtures theo TK4; chạy tests của checker sau khi phần ấy hoàn tất. Không tạo runner mới. QA chấm semantic outputs theo contract riêng, không dùng chính code dựng fixture để tự chứng minh routing đúng.

Trong live phase được giao sau này, records nằm ở `runs/<case_id>.md` có marker + JSON v1; đúng refs manifest cho từng branch/repetition. Mọi failed/denied calls vẫn thêm vào reconciliation. Chạy checker với manifest độc lập chỉ sau refs đã reconcile; hiện chưa có runs nên completeness phải fail/Chưa chạy. Giữ artifacts failed để report; không hydrate private/cloud files.

Hashes tự kiểm bên ngoài manifest: `Get-FileHash -Algorithm SHA256 evals/task-routing/pilot.manifest.json`. Freeze timestamp/hash và outputs đặt tại gốc evidence của sprint đã khai, không thêm plan/ledger mới. Rollback không adopt candidate, giữ baseline source snapshots và failed evidence.

Kiểm chuẩn bị ngày 2026-10-12: Python stdlib parse/coverage/hash/sanitize đạt 36 ca, 18/18, SC1–SC24 mỗi split, một regression mới tại cycle3 mỗi split và 216 planned refs. Bộ `jsonschema` đã có trên máy kiểm Draft 2020-12 meta-schema, hai synthetic record shapes hợp lệ và 22 negative checks đều đạt; không cài dependency. Negative checks xóa từng nhóm required, sai schema/kind/criteria type/unknown reasons type. Đây là kiểm schema, không phải model outputs hay semantic policy pressure. Không tạo file tạm; baseline/calibration/holdout/episodes/pilot/savings Chưa chạy.
