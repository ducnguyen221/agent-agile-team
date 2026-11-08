# Bàn giao cho chặng 2 — agent-skill-studio «Cấu trúc gọn, luật nạp được»

Viết khi đóng `agent-skill-studio:SPR-02` (chặng 1b), 28/10/2026. Phiên mới mở chặng 2 đọc file này trước, rồi
[ROADMAP](../ROADMAP.md) mục 3 (cấu trúc đích, bảng dời) và mục 5 «Chặng 2», và [REQUESTS](../REQUESTS.md) khối «Đang mở».

## 1. Điểm xuất phát

- Repo `plugins/agent-skill-studio`, `main` = commit gộp SPR-02 (REPORT mục 8). Sổ riêng `system/ledger/agent-skill-studio/plans/`;
  sprint kế lấy mã `SPRINTS.md next_id` (dự kiến `SPR-03`); yêu cầu gốc `RQ-004` (lớn; `rules`).
- Thứ tự chương trình còn: 2 → 3 → 4 (ROADMAP chương trình mục 6); 2 và 3 là tiên quyết của đối tác `P11a`, `P13b`.

## 2. Hiện trạng sau 1b (đầu vào cho 2)

- **Một nguồn đã xong:** gốc `studio.py` là shim 14 dòng (`runpy`); engine duy nhất ở `skills/skill-creator-studio/scripts/`:
  `studio.py` (CLI ~200 dòng) + 9 mô-đun `studio_{const,fs,lint,validate,evals,scaffold,dist,doctor,fmt}.py`. Luật nạp (ADR
  `../../adr/0001-engine-in-skill-flat-modules.md`): không `from studio_* import`, không `import studio` trong mô-đun, không re-export,
  kiểm danh tính mô-đun — test `tests/test_engine_modules.py` canh. Test nạp engine qua `tests/_engine.py` (`E.fs`, `E.validate`, …).
- Khuôn chỉ ở `skills/skill-creator-studio/assets/` (có `skill-template-full/SKILL.vi.md`); `templates/` chỉ còn `project/` +
  `README.md` → chặng 2 `git mv templates/project templates/starter-project`. `sync-template` đã bỏ.
- Lệnh `check` đã có cho loại `skill`; loại `workflow`/`rules` thoát 2 «not available yet» — chặng 2 viết `DOC_TYPES.md`, chặng 3
  cho `check`/`doctor` hiểu 3 loại.
- Cổng `model_evaluated` trong engine (`studio_evals.catalog_problems`, mã `EV20`), chạy trong `evals --all` khi repo có `evals/`;
  **đọc `registry/catalog.json`** — chặng 2 dời catalog → `evals/catalog.json` phải sửa đường trong `studio_evals` cùng commit
  (repo có `evals/` mà thiếu catalog → `EV20`, CI đỏ ngay — đó là lưới an toàn có chủ ý). `evals/tools/activation.py` gọi ngược engine
  theo đường cố định `../../skills/skill-creator-studio/scripts` — dời cây thì sửa đường này.
- **Bộ ca hợp đồng** `tests/contract_runner.py` + `tests/fixtures/contract/` (96 ca, 5 cách gọi R/C/E/S/Z, đáp án `1211bfa`): chặng 2
  dời cây (`content/` → `examples/`, `registry/` → `evals/`, `data-quality-audit` → `examples/`) sẽ đổi đầu vào/đường — cập nhật
  bằng ca `changed_by` + `after`, không sửa `before`.
- Bằng chứng thô: 11 blob trùng `evals/data-quality-audit/runs/SPR-18/{blind,out}/` (ĐK1 Cổng 1 SPR-02, đã ghi vào `RQ-004`) —
  dời ra ledger ở chặng 2 sẽ đưa SC «không blob trùng» về đúng chữ ROADMAP.
- Cache plugin Claude trên máy còn `0.1.0` (trước 1a, thiếu `evals/tools/`) — chặng 2 cài lại qua writer chính thức (ROADMAP) rồi
  chạy SC7 trên bản cài.

## 3. Việc để lại xếp cho chặng 2

`RQ-021` (`RF-S7` đọc `SKILL.md` vùng cloud/secret khi đầu vào là thư mục), `RQ-022` (`skill_dirs` stat xuyên `SKILL.md` symlink),
`RQ-023` (`new` ghi đè `cases.json`; `new --output` ghi `evals/` vào repo cwd), `RQ-025` (ghi chú bảo mật `RF-S4`, `RF-S8`, `RF-S9`),
cùng các RQ cũ `RQ-012`, `RQ-017`, `RQ-020`, `RQ-186` (file luật, trình 5 ý một lần). Đã xếp vào ROADMAP mục 5 «Chặng 2» dòng «Nợ
từ 1b» (28/10).

`RQ-024` (bộ ca hợp đồng nhạy hơn) là **Có thì tốt**: SPEC chặng 2 đưa vào nhóm Có thì tốt; chặng 2 dời cây đằng nào cũng chạm
`tests/contract_runner.py` nên làm cùng lúc rẻ nhất. Hết chặng 2 chưa xong → chuyển sang SPEC chặng 3 (ghi ở cột Sprint của RQ),
không bỏ im lặng.

Nhánh `sprint/spr-02-one-source-1b` đã xoá ở local và origin (28/10, Đức xác nhận); Studio chỉ còn `main`.

## 4. Bài học cần mang theo

- Đẩy nhánh + `gh workflow run ci.yml --ref <nhánh>` **sau mỗi TK**, không chỉ trước review: CI Ubuntu bắt hồi quy POSIX mà máy
  Windows không thấy (SPR-02 `LN2`: ENAMETOOLONG).
- Không thiết kế cơ chế «nạp mã từ repo của chính engine» — engine chép rời không biết repo nào là của nó (`LN3`, `RF-S1`).
- Thước kích hoạt dao động mạnh (cùng cây: 2/5 rồi 4/5 cách 2 giờ): lô «không hồi quy» nên kèm đối chứng mốc cũ cùng phiên bản
  Claude Code trong cùng buổi.
- Hai Implementer song song trên một cây: chỉ `git add` file của mình, báo nhau trước (`LN4`).
- Lệnh Bash > 6.000 ký tự bị hook chặn; ghi script ra file tạm.
