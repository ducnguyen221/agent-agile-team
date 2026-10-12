---
title: Task routing, reasoning effort and verified repair cycles
type: method
status: candidate_not_promoted
updated: 2026-10-12
---

# Phân loại tác vụ và phân công

Analyst đánh giá phần việc bằng chứng trước khi chọn vai, tier, model, Reasoning Effort và cách giao.
Người dùng chỉ định model hoặc effort thì giữ từng field trong đúng phạm vi chỉ định. Tier là năng lực
tham khảo của môi trường, effort là tài nguyên suy luận, độ khó là đánh giá tác vụ: ba thứ ghi riêng.
Phương pháp dưới là candidate cần calibration và holdout; chưa có bằng chứng tối ưu hay tiết kiệm.
Vai/tier mặc định ở [tiers](../tiers/README.md) vẫn là baseline cho đến khi người dùng duyệt promotion.

## 1. Sáu trục có nguồn

Đánh giá một work item có outcome riêng, rồi rà tổng task để tránh chia nhỏ né cổng. Mỗi trục ghi value,
ordinal, evidence refs, unknowns và hậu quả nếu đánh giá sai. Null kèm reason; không lấy null thành 0.
Ordinal 0–2 là thứ bậc, không là xác suất hay thời gian.

| Trục | 0 | 1 | 2 | Điều kiện riêng |
|---|---|---|---|---|
| ambiguity | resolved | technical_unknown | owner_decision_open | Điểm thuộc ý muốn người dùng còn mở: làm rõ trước phần phụ thuộc |
| scope_dependencies | local | coupled | cross_boundary | Kiểm quyền, ownership và giao diện dùng chung |
| error_consequence | reversible_local | shared_behavior | sensitive_or_irreversible | Risk tags và cổng của sizing giữ nguyên |
| verifiability | deterministic | mixed | weak_or_unavailable | Chưa có oracle khả thi: xây cách kiểm trước execution |
| plan_readiness | complete_feasible | direction_only | invalid_or_unavailable | PLAN sai/thiếu: planning trước, không giao execution để đoán |
| execution_complexity | bounded_known | nontrivial | complex | Có concurrency, state machine hoặc nhiều biên: implementation tối thiểu T2 nếu không có human override |

Độ khó chỉ dùng ba trục scope_dependencies, plan_readiness, execution_complexity đã đủ nguồn:
max=0 → mức 1; max=1 → mức 2; max=2 và một trục ở mức 2 → mức 3; ít nhất hai trục ở mức 2 → mức 4.
Thiếu một nguồn cần thiết → difficulty null và đọc hẹp/planning tiếp. Không cộng sáu trục thành điểm
tổng: ít file không bù hậu quả sai hoặc thiếu verifier. Cỡ hồ sơ vẫn do [sizing](sizing.md) quyết.

## 2. Reasoning Effort

| Mức chuẩn hóa | Native target | Dùng khi |
|---|---|---|
| 1 | low | Human chỉ định, hoặc pilot riêng đã có evidence cho việc cơ học |
| 2 | medium | **Mặc định**; độ khó 1–2, không có sàn effort cao hơn |
| 3 | high | Độ khó 3; thiết kế/review rủi ro cao có sàn 3 |
| 4 | xhigh | Độ khó 4 và đúng model/harness hỗ trợ |

Không có override: candidate chọn max(2, difficulty, effort_floor) khi dữ kiện đủ. Effort mặc định
medium không cấp quyền dispatch lúc classification/capability còn thiếu. Native default của harness
khác medium phải được ghi rõ. Cùng label native giữa hai model không chứng minh ngân sách ngang nhau.
Native ngoài bốn mức chỉ dùng khi có capability evidence; normalized level null + native_only_reason.
Không tự đổi xhigh thành max/ultra hay suy suffix tên model là effort control.

Ưu tiên **từng field**: chỉ định human mới nhất trong scope → chỉ định human đã duyệt còn hiệu lực →
policy → default. Model-only không đổi effort; effort-only không đổi model. Giữ quote, scope, source,
expiry nếu có; hết scope quay về baseline. Model ngoài bảng giữ override và requested tier null có lý
do; role_default_tier vẫn ghi riêng. Không gán model vào tier mới chỉ vì vai đó cần T1.

Pin dưới sàn heuristic vẫn được làm đúng nếu supported; cỡ, rủi ro, reviewer và test không bị miễn.
Unsupported hoặc không đủ quyền thì dừng đúng phần phụ thuộc và báo; không thay model/effort âm thầm,
không hỏi lại để cân nhắc chỉ định đã chốt. Escalation không đổi field đang được user pin.

## 3. Chọn người làm và hình thức giao

Thứ tự: human overrides → quyền/owner-open/verifier/risk gates → difficulty/effort → vai/sàn tier →
liệt kê assignment hợp lệ → chọn hình thức → thông báo → dispatch. Agent đang nhận việc tự đưa quyết
định trong lượt đó; không thêm classifier, router service, API, hook hoặc model huấn luyện riêng.

| Vai | Baseline | Candidate có điều kiện |
|---|---|---|
| Analyst/Architect | T1 | Giữ T1 cho quyết định, planning, synthesis; phần tra cứu cơ học tách riêng, không chuyển quyền phán quyết |
| Implementer | T2 | T3 chỉ pilot bounded_known, plan đủ, oracle deterministic, scope local và hậu quả reversible_local |
| QA | T3 | Thiết kế oracle khó hoặc phân xử evidence lên vai có năng lực phù hợp; người chạy lệnh khác người chấm |
| Business/Tech Reviewer | T1 | Routine review thấp hơn chỉ là pilot; risk/dual/security và độc lập vẫn bắt buộc |

Model tra bảng của môi trường, không nhúng model ID cố định vào policy. Thiếu mapping/access/capability
không đoán. Candidate ưu tiên critical quality, task-fit rồi tổng công/thời gian **đã đo**, tính cả
brief/review/repair/integration. Chưa đo thì dùng baseline và ghi heuristic; không tự nhận tối ưu.

Delegation quan sát riêng: separable_modules; context_transfer, integration_load theo ordinal 0–2;
benefit_evidence measured/unmeasured; ownership/dependency refs. 0 = reference/interface đã khóa;
1 = brief/kiểm integration có giới hạn; 2 = phần lớn context hoặc integration liên tục. Unknown là null.

| Cách làm | Đánh đổi và rủi ro | Công sức | Khi chọn |
|---|---|---|---|
| **Trực tiếp/tuần tự — baseline khuyến nghị** | Giữ context; thời gian chờ dài hơn khi nhiều phần độc lập | Thấp | Không bắt buộc phiên mới; benefit delegation chưa đo hoặc overhead cao/unknown |
| Một agent mới | Có chuyển context, nhưng outcome/ownership rõ | Vừa | Reviewer độc lập bắt buộc, hoặc worker riêng có lợi ích đã nêu |
| Nhóm song song | Thêm brief và integration; shared writer gây xung đột | Cao | Ít nhất 2 module độc lập, writer riêng, interfaces khóa, quyền dispatch, max hai overhead ≤1 và measured benefit |

Chưa measured benefit thì song song chỉ qua calibration riêng có cap đã duyệt. User trực tiếp giao
nhóm song song là override topology trong scope; ownership, safety và kiểm integration vẫn giữ.
Không giao nhiều writer cho cùng module chỉ vì hai file khác nhau.

## 4. Ba vòng sửa có kiểm chứng

Baseline lỗi đầu tiên mở chu kỳ, không tiêu một vòng sửa. Một vòng = hypothesis + thay đổi thực tế
trong scope + cùng oracle + outcome. Ghi repair_cycle_index 1–3, root cause/test refs, before/after,
regression refs; tool call hay lời review không tự là vòng. Đạt ở vòng 1/2 thì kết thúc, không chạy đủ
ba để lấy số đẹp.

Sau vòng 3, còn cùng nguyên nhân, không tiến triển theo oracle, hoặc **bất kỳ regression mới chưa xử
lý**: dừng writer cũ, cảnh báo và bàn giao một cấp cao hơn trong cùng hãng/role khi quyền/cap cho phép
(T3→T2→T1). Một lỗi mới ở vòng 3 cũng đủ; không đợi hai lỗi. Không có vòng 4 ở cùng assignment bị kẹt.
Lỗi quyền/secret/Chặn vẫn dừng ngay theo luật an toàn, không chờ vòng 3.

Receiver có chu kỳ riêng tối đa ba vòng; giữ tổng counters/log theo work item/root cause qua mọi
agent/model, không reset lịch sử. T1 còn kẹt thì owner quyết; không invent tier cao hơn T1. User pin,
thiếu capability/quyền hoặc scope chỉ một lượt: báo và xin đúng phần còn thiếu. Tăng effort không là
tăng tier, không mở thêm ba vòng cho cùng assignment. Review PLAN theo skill riêng, không trộn với
implementation repair cycles.

Bàn giao có: work item/scope, root cause, các hypothesis/change/oracle/outcome đã thử, regression và
evidence refs, phần đạt/còn mở, assignment cũ→mới, approval/override, total counters, test và rollback.

## 5. Thông báo và bằng chứng

Trước bắt đầu PLAN/dispatch đầu hoặc đổi criteria/model/tier/effort/role/handoff: thông báo một lần
ngắn gồm agent/harness, vai, tier, full requested model ID, native effort/normalized level nếu biết,
scope, lý do, approval/override và trạng thái requested/effective/actual. Ghi notice ref + timestamp;
không thông báo mỗi tool call. Thông báo không tạo cổng xin lại cho hành động đã được cấp.

Requested là yêu cầu; effective là metadata/native configuration đã resolve; actual chỉ từ runtime
evidence allowlisted. Thiếu actual → null + reason; không copy requested thành actual. Notice ordering
chỉ verified khi timestamp và source ordering đủ. Không thu hoặc lưu chain-of-thought.

Criteria đổi: báo cũ→mới, lý do, agent/vai/model/tier/effort tiếp theo và tác động. Human đã đổi thì
áp đúng và version/hash mới. Agent đổi acceptance ngoài scope phải chờ owner. Có baseline rồi thì
experiment mới hoặc re-score cả hai nhánh trên evidence đủ; không chấm lại riêng candidate hay sửa
pass/fail lịch sử. Ghi previous_version/change_ref/baseline_invalidated/re_evaluation_scope.

Telemetry opt-in trong PLAN/PROGRESS/REPORT theo [evaluation contract](../evals/task-routing/contract.md).
Manifest do QA giữ độc lập chỉ định hồ sơ/refs phải có; xóa marker ở hồ sơ pilot vẫn là thiếu evidence.
Legacy ngoài manifest không phải bổ sung routing. Checker kiểm shape/completeness; không dispatch
hoặc chọn tier/model, không đọc ledger/path ngoài repo.

## 6. Catalog, native capability và pilot

Catalog discovery, freshness, account access và actual runtime là bốn trạng thái riêng. Fresh catalog
không xóa access denied; không thấy model không chứng minh không khả dụng. Model mới→proposal có
source/version/task evidence; mapping không tự đổi. Chỉ dùng metadata allowlisted, không quét transcript.
Cadence là runbook thủ công hoặc pipeline đã có quyền, không tự tạo lịch/background probe.

Native controls qua adapter/governor của môi trường; model tier khác context tier. Absent controls giữ
legacy argv; routed controls phải validated trước admit/spawn. Unsupported không fallback. Resume
routed đòi identity model, effective effort, capability và approval scope đều known/matching; unknown
không là wildcard. Ledger requested/effective/actual/source/usage riêng; không sửa global config để ép.

Pilot có 36 ca synthetic, 18 calibration/18 holdout, 3 repetitions mỗi nhánh: **216 observations dự
kiến**. So implementation 12 task ×3×2 = **72 episodes dự kiến**; observations/episodes không là call
budget. Call/time/billing cap, account capability và owner scope phải khóa trước live. Failed/denied
calls giữ trong report. Policy writer không mở holdout trước freeze. Không dùng fixtures thay semantic
pilot, pass@3 thay first-pass, hay cost unknown thành 0. Bounded data không chứng minh general savings.

Baseline/candidate giữ cùng coordinator, inputs, pool, oracle và cấu hình kiểm soát; worker assignment
là treatment routing, effort khác là treatment riêng. Critical permissions/risk/ownership phải đạt
mọi repeats, không bù bằng time/token. Ngưỡng chi tiết, sources/hashes và limits nằm trong evaluation
contract. Chỉ sau nghiệm thu owner mới retain/extend/drop/promote; release/install/deploy có scope riêng.

## 7. Nguồn và giới hạn

Ý từ [Jeff](https://github.com/firelex/jeff) là chọn trong tập lựa chọn hợp lệ, calibration riêng và khóa
ngưỡng trước holdout; [Jeff-Code](https://github.com/firelex/jeff-code) gợi tách việc thường lệ và effort.
Đây là diễn giải phương pháp; không cài model/LoRA/runtime, không dùng tỷ lệ của nguồn làm kết quả tại
đây, không tự sinh confidence probability. Mốc/giấy phép/cách dùng: [UPSTREAM](../UPSTREAM.md).
Thang ordinal, default medium, field override và ba vòng là hợp đồng riêng đã được owner yêu cầu.
