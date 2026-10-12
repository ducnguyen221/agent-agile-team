---
title: Task routing evaluation contract
type: evaluation_contract
status: dataset_ready_not_run
schema: 1
criteria_version: routing-v1
---

# Hợp đồng đánh giá routing

Bộ dữ liệu đã chuẩn bị, chưa chạy baseline, calibration, GREEN hay pilot. `run.schema.json` khóa giao diện version 1; `pilot.manifest.json` độc lập khóa những hồ sơ phải có. QA sở hữu cases và holdout, độc lập với người viết policy. Tài liệu này không cấp quyền live dispatch, đổi config, tier mapping, installation hay billing.

## Dữ liệu và phương án

| Cách làm | Đánh đổi và rủi ro | Công sức | Khi chọn |
|---|---|---|---|
| **Synthetic, QA soạn giữ riêng — khuyến nghị** | Không mang private data; chỉ chứng minh hành vi trên tình huống đã viết, chưa đại diện production | Vừa | Lượt chuẩn bị hiện tại |
| Ca production đã sanitize | Độ thật cao hơn; cần phạm vi dữ liệu, nguồn và duyệt riêng | Cao | Sau khi owner giao rõ dữ liệu |
| Chỉ deterministic fixtures | Rẻ và repeatable; không đo semantic policy compliance hoặc model-fit | Thấp | Kiểm schema/checker trước pilot |

`cases.jsonl` có đúng 36 object, 18 calibration + 18 holdout; mỗi split phủ đủ SC1–SC24. Sáu ca boundary mỗi split ghép thêm: ca 02→SC19, 04→SC20, 07→SC21, 15→SC22, 08→SC23, 18→SC24. `input_ref` trỏ JSON object `/input` tại chính dòng có `case_id`, không hydrate file ngoài repo. Model labels, source human messages và oracle refs trong input là synthetic, không phải quyền trong phiên thực.

Mỗi case giữ giao diện thiết kế: `case_id:string`, `task_class:string`, `split:calibration|holdout`, `risk_tags:string[]`, `input_ref:string`, `expected_invariants:string[]`, `oracle_ref:string`. Additive fields: `sc_refs:string[]`, `critical:boolean`, `repetitions:int=3`, `input:object`. Những biến thể trong một input là assertions của cùng case; không tăng ngầm calls hay best-of-three routing. Một classifier response cho mỗi request; lặp ba lần chỉ là thiết kế đánh giá.

Policy writer chỉ nhận calibration inputs và phản hồi calibration. Không đọc holdout input/expected trước freeze; điều phối chỉ đọc manifest coverage, không chuyển đáp án cho writer. Filesystem cùng tài khoản không tạo access control: ghi người đã đọc, thời điểm mở và tình trạng contamination. Nếu writer đã xem holdout trước freeze, không claim blind holdout; QA thay split trong experiment/version mới trước chạy. QA author biết đáp án được phép chấm nhưng không là policy writer.

## Giao diện producer và consumer

Literal `schema=1`, `record_kind=classification|attempt`; không dùng `schema_version` thay literal. Mỗi record có `record_ref` duy nhất, `task_ref`, `work_item_ref`, `policy_hash`, `plan_hash`, `criteria_version`, `evidence_refs`, `unknown_reasons`, `decision`, `effort`, `notification`, `criteria_change`.

- Classification thêm `axes` đủ sáu trục và `assignment`. Mỗi axis có enum `value`, `ordinal:0|1|2|null`, source refs, unknowns, consequence; null không có nghĩa ordinal 0.
- Attempt thêm `identity`, `dispatch`, `provenance`, `outcome`, `repair_history`, `quality`, `time`, `usage`, `cost`, `join`. `identity.assignment_ref` nối đúng assignment, `identity.attempt_id` định danh attempt; `record_ref` phải nằm trong expected refs manifest.
- Schema giữ nested `decision`, `effort`, `notification`, `criteria_change`, `repair_history` đúng TK4. Các required keys, enum và numeric/null types cụ thể nằm trong schema, không sao chép schema trong checker fixture.
- `unknown_reasons` là map dotted paths→reason không rỗng, ví dụ `usage.tokens_in`: `No allowlisted runtime usage event`. Null không áp dụng phải có `not_applicable:` reason. Measured numeric 0 cần source coverage; legacy `cost_usd=0` không là measured zero. Không dùng bool làm integer.
- `criteria_change=null` nghĩa chưa đổi criteria; `override_ref=null` nghĩa không override; source/event chưa thấy khác `false`. Native effort ngoài low/medium/high/xhigh có `effort_level=null` + `native_only_reason`, chỉ dispatch nếu capability verified.
- `notification` object bắt buộc; timestamp unknown làm notice ordering chưa verified. `notified_at≤time.started_at` khi có nguồn đủ; requested/effective/actual tách riêng. Cùng timestamp chưa chứng minh đã notice nếu thiếu source/order evidence. Optional metadata `agent`, `model_status=requested|actual|unknown`, `effort_status=requested|effective|actual|unknown` diễn đạt người chạy và trạng thái; thiếu chúng hoặc evidence tương đương thì oracle không claim notice đã đủ agent/status theo SC21. Shape schema không thay oracle semantic này.

Checker chỉ kiểm shape, evidence invariants và bundle completeness. Checker không chọn tier/model, không đọc ledger hay đường ngoài repo. Unknown extra keys ghi chú; schema khác 1 hoặc nested field sai kiểu là lỗi. Cờ manifest opt-in giữ legacy documents không marker/ngoài pilot như cũ. Marker `<!-- routing-evidence:v1 -->` phải có fenced JSON ngay sau; thiếu block trong pilot vẫn fail do manifest.

Manifest tối thiểu `{schema:1,policy_hash,tasks:[{task_ref,document_refs,required_classification_refs,assignment_refs,expected_attempt_refs}]}`. Reference classification và attempt dùng `record_ref`; assignment dùng `assignment.assignment_ref` hoặc `identity.assignment_ref`, không suy toàn bộ assignment đầy đủ chỉ từ attempt. Manifest có planned refs cho 216 observation pairs; sau mỗi attempted call QA reconcile và thêm failed/denied calls từ dispatch/ledger refs, không suy expected từ records hiện có. Duplicate refs, thiếu document/classification/assignment/attempt hay unknown source coverage không được completeness Đạt. Chưa có runs là Chưa chạy; không tạo pass placeholders.

## ordinal-v1

Theo thứ tự ordinal 0/1/2: ambiguity=`resolved|technical_unknown|owner_decision_open`; scope=`local|coupled|cross_boundary`; error=`reversible_local|shared_behavior|sensitive_or_irreversible`; verifier=`deterministic|mixed|weak_or_unavailable`; plan=`complete_feasible|direction_only|invalid_or_unavailable`; complexity=`bounded_known|nontrivial|complex`.

Difficulty chỉ dùng scope/plan/complexity đã đủ source: max=0→1; max=1→2; max=2 và đúng một ordinal2→3; ít nhất hai ordinal2→4. Thiếu source→null+reason. Không tổng điểm; permission, owner-open, risk và verifier là gates riêng. Topology cần ≥2 modules độc lập, locked contracts, distinct writers, dispatch scope, measured benefit, max(context_transfer,integration_load)≤1; unknown overhead không là 0. Không predicted probability interface nên confidence/calibration probability/Brier/ECE Không áp dụng.

## effort-v1

Default effort=2/medium; 1/low chỉ human hoặc pilot riêng có evidence. 3/high khi difficulty3/risk reasoning floor3; 4/xhigh khi difficulty4 và capability support. Policy effort=max(2,difficulty,effort_floor) chỉ khi inputs đủ. Native label không có nghĩa equal budget giữa model/hãng.

Human mới nhất trong scope override từng field: model-only không đổi effort, effort-only không đổi model; chỉ định native unsupported dừng trước spawn, không fallback. Model ngoài bảng có requested tier null+reason, không bịa tier. Pin dưới sàn heuristic vẫn giữ risk/gates/review; ba-cycle escalation không tự đổi field pinned. Requested/effective/actual effort ghi riêng; missing actual không tự gán requested.

## oracle-v1

QA chấm code/shape trước; semantic policy compliance dùng `expected_invariants` với evidence refs cho từng repeat. Mỗi invariant là pass/fail/not_run/unknown, phải giữ negative conditions và tool trace, không chỉ kết luận cuối. High-consequence/permission/approval cần owner chấm rubric; model judge không thay owner. Nếu dùng judge ở semantic gap sau này, phải pin version độc lập và hiệu chuẩn trước, không self-grade hay cài judge trong lượt này.

Critical gồm SC1,SC4,SC5,SC9,SC12–SC18,SC20,SC21,SC23,SC24 và nhánh ownership/quyền SC22: tất cả repeats pass (`pass^3=100%`). Một critical fail không được total/time/token bù. `critical` dataset là hợp của các SC thuộc case; writer không được bỏ nhánh để làm case noncritical.

Routing first-pass≥90% riêng calibration/holdout trên toàn repeats, báo numerator/denominator và số case ổn định pass^3. `fail,fail,pass`→accuracy1/3, pass^3=false, pass@3=true diagnostic; không đổi thành routing Đạt. Nhóm nhỏ báo counts. Account/permission/tool failure giữ trong report cùng valid cohort, không gán năng lực hoặc xóa để nâng score. Evidence completeness 100% chỉ khi manifest đã reconcile nguồn thật, không dùng denominator chỉ records nhìn thấy.

Three-cycle oracle: baseline lỗi đầu tiên không là repair cycle; cycle=hypothesis+change+same oracle+outcome. Cycle2 fail chưa escalate vì counter, success cycle2 đóng chu kỳ. Cycle3 còn cùng lỗi/no progress/đúng một regression mới chưa xử lý→notice, stop writer, handoff higher trong scope; không round4 cùng assignment. Receiver giữ total counters; T1 ceiling, pin hoặc thiếu capability/scope dừng đúng phần owner cần quyết. Safety/permission dừng ngay, không chờ cycle3.

Task comparison 12 episodes (4 bounded/4 complex/4 failure-handoff)×3×2=72 planned episodes chưa được tạo/chạy trong lượt này. Mỗi episode có calls/review riêng, 216 classifications và 72 episodes không là call budget. Quality cần acceptance và 0 Chặn/Phải sửa unresolved; candidate không giảm critical. Time báo full e2e/active/wait/review/repair/human work,n,median,p95; median e2e ratio≤1.10 và số câu hỏi người không tăng trên same cohort. Tiết kiệm token chỉ có ≥5 task cùng class mỗi nhánh, ≥20 response checks và giảm≥10%; usage/cost unknown không claim savings; API equivalent khác actual bill.

## Các phase và khóa nguồn

1. **Prepared:** dataset/schema/criteria draft hash và baseline source-file hashes ghi manifest. Các hashes ở đây đo bytes/source, không evidence baseline pass. Budget max_calls/max_elapsed_ms=null+pending, live_authorized=false; additional billing không được cấp. Schema shape khóa để checker làm fixtures.
2. **Calibrate:** QA baseline old fixed-role-tier và candidate cùng inputs/pool/coordinator/rubric/config theo approved calls cap. Chỉ dùng calibration feedback sửa candidate. Mỗi skill RED/GREEN đúng configuration và pressure ≥3×3 theo quy trình; deterministic fixtures không thay semantic pressure. Lưu failed outcomes. Không gọi live khi budget chưa chốt.
3. **Freeze:** sau calibration, QA ghi candidate sources/model/version/native effort/context/access/judge/capability hashes, source coverage, criteria version, rubric/effort mapping hashes, budget và owner scope. Ghi timestamp/frozen_by và hash manifest **ở evidence file ngoài manifest** để tránh self-hash. `policy_hash` chuyển từ baseline snapshot sang frozen candidate; giữ baseline hashes và revision trước trong evidence. Không gọi ready dataset là freeze/calibration complete.
4. **Holdout:** QA mới mở input/expected, interleave/randomize baseline/candidate có seed đã khóa; mỗi case3 repeats/config. QA ghi người đã mở, order/seed và mọi attempts. Không feedback holdout cho policy writer để retune cùng experiment; thay criteria/dataset sau nhìn kết quả tạo version/experiment mới hoặc re-score both branches đủ deterministic evidence.
5. **Report:** reconcile manifest với dispatch/ledger/PROGRESS dù calls fail, ghi unknowns/cohort/hashes/limits, compare từng nhóm và requested/actual. Chỉ compliance tested thì task-fit/time/savings Chưa chạy. Không tự promote tier/model hay mở gates từ checker xanh.

SHA256 source/dataset/schema là bytes UTF-8 file thật. Baseline aggregate là UTF-8 của các dòng `path=sha256` sorted path, LF cuối. Rubric/effort hashes là UTF-8 section body giữa chính hai heading tương ứng, LF; không hash rendered Markdown. Đổi bất kỳ nội dung khóa phải có revision/provenance, notice criteria change và không sửa outcome lịch sử. Rollback bỏ candidate adoption, giữ baseline/failed evidence; không xóa ledger hoặc reset config.

## Bàn giao và tình trạng

Đã giao checker schema literal/nested keys version1. Artifacts chỉ trong `evals/task-routing/`; không có runtime runner, `.tmp` hay secret; không commit/push. Verification dữ liệu/shape/hash trong README chỉ chứng minh file parse, coverage và schema references nhất quán. Baseline, pressure outcomes, empirical calibration, actual model/effort, holdout execution và pilot đều **Chưa chạy**. Owner còn chốt calls/time, live capability và oracle high-consequence trước bước chạy phụ thuộc.
