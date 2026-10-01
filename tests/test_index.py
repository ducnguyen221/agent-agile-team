"""`index.py`: sinh lại khối "Đang mở" của ba sổ gốc; cùng đầu vào cho cùng đầu ra (FR15.3)."""

import json
from pathlib import Path

from conftest import run_script
import _common as c
import index
import init

DATE = "2026-03-02"


def project(tmp_path: Path) -> Path:
    init.main([str(tmp_path), "--apply", "--date", DATE])
    return tmp_path


def block(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text[text.index(index.START):text.index(index.END)]


def add_rows(path: Path, after_header: str, rows: list) -> None:
    text = path.read_text(encoding="utf-8")
    head = text.index(after_header)
    sep = text.index("\n", text.index("|---", head)) + 1
    path.write_text(text[:sep] + "".join(r + "\n" for r in rows) + text[sep:], encoding="utf-8", newline="\n")


def test_empty_project_keeps_empty_sentences(tmp_path):
    root = project(tmp_path)
    before = {p: p.read_bytes() for p in root.rglob("*.md")}
    assert index.main([str(root)]) == 0
    assert {p: p.read_bytes() for p in root.rglob("*.md")} == before
    assert "Không có sprint nào đang mở." in block(root / "docs" / "plans" / "SPRINTS.md")


def test_requests_open_block_newest_first(tmp_path):
    root = project(tmp_path)
    ledger = root / "docs" / "plans" / "REQUESTS.md"
    add_rows(ledger, "## Timeline", [
        "| RQ-012 | 2026-03-02 | Xuất CSV | mới | — | — |",
        "| RQ-011 | 2026-03-01 | Sửa chữ | xong | FS-001 | SPR-02 |",
        "| RQ-009 | 2026-02-20 | Tra đơn | đang làm | FS-001 | SPR-01 |",
    ])
    assert index.main([str(root)]) == 0
    got = block(ledger)
    assert "| Mã | Ngày | Tóm tắt | Trạng thái | Sprint |" in got
    assert "RQ-011" not in got
    assert got.index("| RQ-012 | 2026-03-02 | Xuất CSV | mới | — |") < got.index("| RQ-009 |")


def test_specs_open_block_reads_feature_frontmatter(tmp_path):
    root = project(tmp_path)
    specs = root / "docs" / "specs"
    for slug, fid, status in (("lookup", "FS-001", "live"), ("export", "FS-002", "in_progress"), ("idea", "FS-003", "proposed")):
        (specs / f"{slug}.md").write_text(
            f"---\nid: {fid}\ndoc: feature\ntitle: {slug} title\nstatus: {status}\nrequests: []\nsprints: []\n"
            f"created: {DATE}\nupdated: {DATE}\n---\n\n# {slug}\n", encoding="utf-8")
    add_rows(specs / "SPECS.md", "## Danh mục", ["| FS-002 | Xuất dữ liệu | đang làm | [export.md](export.md) | SPR-03 | 2026-03-02 |"])
    assert index.main([str(root)]) == 0
    got = block(specs / "SPECS.md")
    assert "FS-001" not in got
    assert "| FS-003 | idea title | đề xuất | [idea.md](idea.md) |" in got
    assert "| FS-002 | Xuất dữ liệu | đang làm | [export.md](export.md) |" in got
    assert got.index("FS-003") < got.index("FS-002")


def test_sprints_open_block_from_progress_frontmatter(tmp_path):
    root = project(tmp_path)
    init.main([str(root), "--apply", "--date", "2026-03-01", "--sprint", "order-lookup", "--title", "Tra đơn"])
    init.main([str(root), "--apply", "--date", DATE, "--sprint", "fix-typo", "--title", "Sửa chữ", "--tiny"])
    init.main([str(root), "--apply", "--date", DATE, "--sprint", "old-work", "--title", "Việc cũ"])
    old = root / "docs" / "plans" / f"{DATE}-old-work" / "PROGRESS.md"
    old.write_text(old.read_text(encoding="utf-8").replace("status: drafting", "status: done", 1), encoding="utf-8", newline="\n")
    tiny = root / "docs" / "plans" / f"{DATE}-fix-typo" / "SPRINT.md"
    tiny.write_text(tiny.read_text(encoding="utf-8").replace("status: drafting", "status: verifying", 1)
                    .replace("review_round: 0", "review_round: 2", 1), encoding="utf-8", newline="\n")
    assert index.main([str(root)]) == 0
    got = block(root / "docs" / "plans" / "SPRINTS.md")
    assert "| Mã | Mở | Mục tiêu | Trạng thái | Vòng | Thư mục |" in got
    assert f"| SPR-02 | {DATE} | Sửa chữ | đang kiểm định | 2 | [{DATE}-fix-typo]({DATE}-fix-typo/) |" in got
    assert "| SPR-01 | 2026-03-01 | Tra đơn | đang viết SPEC/PLAN | 0 |" in got
    assert "SPR-03" not in got
    assert got.index("SPR-02") < got.index("SPR-01")


def test_idempotent_byte_for_byte(tmp_path):
    root = project(tmp_path)
    init.main([str(root), "--apply", "--date", DATE, "--sprint", "order-lookup", "--title", "Tra đơn"])
    index.main([str(root)])
    first = {p: p.read_bytes() for p in root.rglob("*.md")}
    assert index.main([str(root)]) == 0
    assert {p: p.read_bytes() for p in root.rglob("*.md")} == first


def test_check_mode_reports_stale_without_writing(tmp_path, capsys):
    root = project(tmp_path)
    init.main([str(root), "--apply", "--date", DATE, "--sprint", "order-lookup", "--title", "Tra đơn"])
    ledger = root / "docs" / "plans" / "SPRINTS.md"
    before = ledger.read_bytes()
    assert index.main([str(root), "--check"]) == 1
    assert ledger.read_bytes() == before
    assert "SPRINTS.md" in capsys.readouterr().out
    index.main([str(root)])
    assert index.main([str(root), "--check"]) == 0


def test_missing_markers_config_or_ledger_are_input_errors(tmp_path):
    assert index.main([str(tmp_path)]) == 2  # chưa có .agile.json
    root = project(tmp_path)
    ledger = root / "docs" / "plans" / "SPRINTS.md"
    ledger.write_text(ledger.read_text(encoding="utf-8").replace(index.END, ""), encoding="utf-8", newline="\n")
    assert index.main([str(root)]) == 2
    ledger.unlink()
    assert index.main([str(root)]) == 2


def test_broken_feature_frontmatter_is_input_error(tmp_path):
    root = project(tmp_path)
    (root / "docs" / "specs" / "bad.md").write_text("---\nid: FS-009\ndoc: feature\nsprints:\n  - SPR-01\n---\n", encoding="utf-8")
    assert index.main([str(root)]) == 2


def test_rewrite_keeps_bom_and_crlf(tmp_path):
    root = project(tmp_path)
    init.main([str(root), "--apply", "--date", DATE, "--sprint", "order-lookup", "--title", "Tra đơn"])
    ledger = root / "docs" / "plans" / "SPRINTS.md"
    ledger.write_bytes(b"\xef\xbb\xbf" + ledger.read_bytes().replace(b"\n", b"\r\n"))
    assert index.main([str(root)]) == 0
    data = ledger.read_bytes()
    assert data.startswith(b"\xef\xbb\xbf") and b"\n" not in data.replace(b"\r\n", b"")
    assert b"| SPR-01 |" in data
    assert index.main([str(root), "--check"]) == 0


def test_ledger_outside_project_is_refused(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    project(root)
    cfg = json.loads((root / ".agile.json").read_text(encoding="utf-8"))
    cfg["paths"]["requests"] = "../../stray.md"
    (root / ".agile.json").write_text(json.dumps(cfg), encoding="utf-8")
    assert index.main([str(root)]) == 2


def test_script_runs_standalone(tmp_path):
    root = project(tmp_path)
    result = run_script("index.py", str(root))
    assert result.returncode == 0, result.stderr
