# Changelog

Mục mới nhất đứng đầu. Tiêu đề mỗi mục là đúng chuỗi version trong các manifest (test đồng bộ
version kiểm điều này).

## 0.1.0-dev

Chưa phát hành.

- Khung repo: cây thư mục, luật lõi dạng khung, manifest khung cho Claude và Codex, con trỏ cho
  Antigravity, hợp đồng hai điểm cắm `AGENT_AGILE_TIERS` và `AGENT_AGILE_DENYLIST`, test đồng bộ version.
- Distill Đợt 1 (SHA chốt 2026-10-01): 28 skill phẳng trong `skills/` chia 5 nhóm — Quy trình (6),
  Kỹ thuật (12, trong đó 10 skill tham chiếu `metadata.kind: reference`), Kiểm định (6), Giao tiếp & tối
  ưu (3), Meta (1) — và 7 agent reviewer chỉ-đọc trong `agents/`. Nguồn: Superpowers, ECC, gstack (MIT),
  bộ skill quy trình private (gốc không giấy phép, gắn `rewrite_before_public: true` ở 4 skill), nguồn khái
  niệm chỉ lấy ý. Mỗi skill/agent ghi `source`, `source_sha`, `license` (và `base_sha` khi có) trong
  frontmatter.
- Dấu vết: `UPSTREAM.md` (bảng nguồn theo từng skill/agent), `NOTICE` (bản quyền MIT của Superpowers, ECC,
  gstack, Supabase Agent Skills), `THIRD_PARTY.md` (nguồn chỉ lấy ý, danh sách file phải viết lại trước khi
  công khai), `docs/MIGRATION.md` (tên cũ → tên mới).
- Mẫu: SPEC thêm mục "Đổi hợp đồng / giao diện" và dấu delta `(sửa …)`/`(bỏ …)`; spec sống ghi cách gộp
  delta Thêm / Sửa / Bỏ ở Bước 5; REPORT mục Review & Retro đọc lại `Phán quyết:` và rà nợ `CO`. Thẻ QA thêm
  bảng phủ `FR` → `VR` theo tầng test thấp nhất. `pytest` gom thêm test trong `skills/`.
- Thử áp lực bắt buộc cho skill kỷ luật/quy trình (`tests/pressure.md`); skill tham chiếu miễn ở Đợt 1,
  Đợt 2 thêm `tests/retrieval.md`.
