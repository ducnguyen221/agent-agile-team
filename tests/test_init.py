"""`init.py`: mặc định chạy thử, `--apply` mới ghi, không ghi đè, chạy hai lần không đổi gì (FR15.1)."""

import json
from pathlib import Path

import pytest

from conftest import run_script, write_lf
import _common as c
import check
import init

DATE = "2026-03-02"


def files_of(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_dry_run_writes_nothing(tmp_path, capsys):
    assert init.main([str(tmp_path), "--date", DATE]) == 0
    out = capsys.readouterr().out
    assert files_of(tmp_path) == {}
    assert "+ tạo" in out and ".agile.json" in out and "REQUESTS.md" in out
    assert "--apply" in out


def test_apply_creates_config_and_ledgers(tmp_path):
    assert init.main([str(tmp_path), "--apply", "--date", DATE]) == 0
    got = files_of(tmp_path)
    assert set(got) == {".agile.json", "docs/plans/REQUESTS.md", "docs/plans/SPRINTS.md", "docs/specs/SPECS.md"}
    assert json.loads(got[".agile.json"]) == c.DEFAULT_CONFIG
    for rel, next_id in (("docs/plans/REQUESTS.md", "RQ-001"), ("docs/plans/SPRINTS.md", "SPR-01"), ("docs/specs/SPECS.md", "FS-001")):
        fm = c.parse_frontmatter(got[rel].decode("utf-8"))
        assert fm.data["next_id"] == next_id and fm.data["updated"] == DATE
    assert b"\r\n" not in got["docs/plans/REQUESTS.md"]
    assert check.check_paths([tmp_path]).exit_code == 0


def test_second_run_changes_nothing_and_never_overwrites(tmp_path, capsys):
    custom = tmp_path / "docs" / "plans" / "REQUESTS.md"
    custom.parent.mkdir(parents=True)
    write_lf(custom, "sổ có sẵn\n")
    init.main([str(tmp_path), "--apply", "--date", DATE])
    first = files_of(tmp_path)
    assert first["docs/plans/REQUESTS.md"] == "sổ có sẵn\n".encode("utf-8")
    capsys.readouterr()
    init.main([str(tmp_path), "--apply", "--date", "2026-04-01"])
    assert files_of(tmp_path) == first
    assert "+ tạo" not in capsys.readouterr().out


def test_existing_config_drives_paths_and_widths(tmp_path):
    (tmp_path / ".agile.json").write_text(json.dumps({
        "schema": 1, "artifact_root": "records",
        "paths": {"requests": "R.md", "sprints": "S.md", "specs": "F/INDEX.md", "feature_specs_dir": "F"},
        "id_width": {"request": 4, "sprint": 3},
    }), encoding="utf-8")
    init.main([str(tmp_path), "--apply", "--date", DATE])
    for rel, next_id in (("records/R.md", "RQ-0001"), ("records/S.md", "SPR-001"), ("records/F/INDEX.md", "FS-001")):
        assert c.parse_frontmatter((tmp_path / rel).read_text(encoding="utf-8")).data["next_id"] == next_id


def new_sprint(root: Path, slug: str, *extra: str) -> int:
    return init.main([str(root), "--apply", "--date", DATE, "--sprint", slug, "--title", "Tra đơn | nhanh", *extra])


def test_sprint_scaffold_resets_state_and_registers(tmp_path):
    assert new_sprint(tmp_path, "order-lookup", "--request", "RQ-003", "--size", "large", "--risk", "high", "--risk-tags", "auth,secret") == 0
    folder = tmp_path / "docs" / "plans" / f"{DATE}-order-lookup"
    assert sorted(p.name for p in folder.iterdir()) == ["PLAN.md", "PROGRESS.md", "REPORT.md", "SPEC.md"]
    for name in ("SPEC", "PLAN", "PROGRESS", "REPORT"):
        text = (folder / f"{name}.md").read_text(encoding="utf-8")
        data = c.parse_frontmatter(text).data
        assert data["id"] == f"SPR-01-{name.lower()}" and data["sprint"] == "SPR-01"
        assert data["request"] == "RQ-003" and data["feature"] is None
        assert data["title"] == "Tra đơn | nhanh" and data["created"] == DATE and data["updated"] == DATE
        assert (data["size"], data["risk"], data["risk_tags"]) == ("large", "high", ["auth", "secret"])
        assert all(value[1] == "pending" and len(value) == 2 for value in data["roles"].values())
        assert data.get("gate_1", "pending") == "pending" and data.get("gate_1_quote") is None
        assert data.get("verdict", "pending") == "pending" and data.get("gate_2_at") is None
        assert data.get("review_round", 0) == 0
        assert "# Tra đơn | nhanh —" in text
    assert c.parse_frontmatter((folder / "PROGRESS.md").read_text(encoding="utf-8")).data["status"] == "drafting"
    ledger = (tmp_path / "docs" / "plans" / "SPRINTS.md").read_text(encoding="utf-8")
    assert c.parse_frontmatter(ledger).data["next_id"] == "SPR-02"
    assert f"| SPR-01 | {DATE} |  | Tra đơn \\| nhanh |  | [{DATE}-order-lookup]({DATE}-order-lookup/) |" in ledger
    report = check.check_paths([tmp_path])
    assert [f.render() for f in report.findings if f.level in ("Chặn", "Phải sửa")] == []


def test_sprint_rerun_is_idempotent_and_next_sprint_gets_next_id(tmp_path):
    new_sprint(tmp_path, "order-lookup")
    before = files_of(tmp_path)
    assert new_sprint(tmp_path, "order-lookup") == 0
    assert files_of(tmp_path) == before
    new_sprint(tmp_path, "export-csv", "--tiny")
    folder = tmp_path / "docs" / "plans" / f"{DATE}-export-csv"
    assert [p.name for p in folder.iterdir()] == ["SPRINT.md"]
    data = c.parse_frontmatter((folder / "SPRINT.md").read_text(encoding="utf-8")).data
    assert data["id"] == "SPR-02-sprint" and data["size"] == "tiny" and data["status"] == "drafting"
    ledger = (tmp_path / "docs" / "plans" / "SPRINTS.md").read_text(encoding="utf-8")
    assert ledger.index("| SPR-02 |") < ledger.index("| SPR-01 |"), "mới nhất ở trên"


def test_sprint_dry_run_writes_nothing(tmp_path, capsys):
    init.main([str(tmp_path), "--date", DATE, "--sprint", "order-lookup", "--title", "X"])
    assert files_of(tmp_path) == {}
    assert "SPEC.md" in capsys.readouterr().out


def test_bad_sprint_arguments_are_input_errors(tmp_path, capsys):
    assert init.main([str(tmp_path), "--sprint", "Bad Slug", "--title", "X"]) == 2
    assert init.main([str(tmp_path), "--sprint", "ok", "--title", "X", "--risk", "high"]) == 2
    assert init.main([str(tmp_path), "--sprint", "ok", "--title", "X", "--risk-tags", "auth"]) == 2
    assert init.main([str(tmp_path), "--sprint", "ok", "--title", "X", "--risk-tags", "nope", "--risk", "high", "--size", "large"]) == 2
    assert init.main([str(tmp_path), "--sprint", "ok"]) == 2  # thiếu --title
    assert init.main([str(tmp_path), "--sprint", "ok", "--title", "X", "--tiny", "--size", "large"]) == 2
    assert init.main([str(tmp_path), "--sprint", "ok", "--title", "X", "--request", "SPR-1"]) == 2
    assert init.main([str(tmp_path), "--date", "02/03/2026"]) == 2
    assert files_of(tmp_path) == {}


def test_broken_config_is_input_error(tmp_path):
    (tmp_path / ".agile.json").write_text("{hỏng", encoding="utf-8")
    assert init.main([str(tmp_path), "--apply"]) == 2


def test_paths_escaping_project_are_refused(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    (root / ".agile.json").write_text(json.dumps({"schema": 1, "paths": {"requests": "../../evil.md"}}), encoding="utf-8")
    assert init.main([str(root), "--apply", "--date", DATE]) == 2
    assert not (tmp_path.parent / "evil.md").exists()
    assert set(files_of(root)) == {".agile.json"}


def test_bad_config_values_are_input_errors_not_tracebacks(tmp_path):
    cases = ({"paths": {"sprint_dir": "docs/{date}-{nope}"}}, {"paths": {"sprint_dir": "docs/{date-{slug}"}},
             {"id_width": {"sprint": "hai"}})
    for n, raw in enumerate(cases):
        root = tmp_path / f"p{n}"
        root.mkdir()
        (root / ".agile.json").write_text(json.dumps({"schema": 1, **raw}), encoding="utf-8")
        assert init.main([str(root), "--apply", "--date", DATE, "--sprint", "ok", "--title", "X"]) == 2, raw


def test_control_characters_in_title_are_refused(tmp_path):
    for title in ("dòng\nmới", "tab\there", "cr\rhere"):
        assert init.main([str(tmp_path), "--apply", "--sprint", "ok", "--title", title]) == 2
    assert files_of(tmp_path) == {}


def test_second_apply_reports_existing_config(tmp_path, capsys):
    init.main([str(tmp_path), "--apply", "--date", DATE])
    capsys.readouterr()
    init.main([str(tmp_path), "--apply", "--date", DATE])
    lines = capsys.readouterr().out.splitlines()
    assert any(line.startswith("= giữ (đã có)") and line.endswith(".agile.json") for line in lines), lines


def test_sprint_update_keeps_ledger_bom_and_crlf(tmp_path):
    init.main([str(tmp_path), "--apply", "--date", DATE])
    ledger = tmp_path / "docs" / "plans" / "SPRINTS.md"
    ledger.write_bytes(b"\xef\xbb\xbf" + ledger.read_bytes().replace(b"\n", b"\r\n"))
    new_sprint(tmp_path, "order-lookup")
    data = ledger.read_bytes()
    assert data.startswith(b"\xef\xbb\xbf") and b"\n" not in data.replace(b"\r\n", b"")
    assert b"| SPR-01 |" in data


def test_script_runs_standalone(tmp_path):
    result = run_script("init.py", str(tmp_path), "--date", DATE)
    assert result.returncode == 0, result.stderr
    assert "chạy thử" in result.stdout


def test_non_utf8_ledger_is_input_error(tmp_path, capsys):
    init.main([str(tmp_path), "--apply", "--date", DATE])
    ledger = tmp_path / "docs" / "plans" / "SPRINTS.md"
    ledger.write_bytes(ledger.read_text(encoding="utf-8").encode("utf-16"))
    assert new_sprint(tmp_path, "order-lookup") == 2
    assert "UTF-8" in capsys.readouterr().out


# --- TK6.5 ---------------------------------------------------------------------------------------------


def test_first_real_row_removes_example_comment(tmp_path):
    new_sprint(tmp_path, "order-lookup")
    ledger = (tmp_path / "docs" / "plans" / "SPRINTS.md").read_text(encoding="utf-8")
    assert "Ví dụ một dòng" not in ledger
    assert ledger.count("| SPR-01 |") == 1
    assert check.check_paths([tmp_path]).exit_code == 0


def test_title_file_keeps_vietnamese(tmp_path):
    title = tmp_path / "title.txt"
    title.write_bytes("\ufeffcách ly theo loại\r\n".encode("utf-8"))
    root = tmp_path / "p"
    assert init.main([str(root), "--apply", "--date", DATE, "--sprint", "ok", "--title-file", str(title)]) == 0
    spec = (root / "docs" / "plans" / f"{DATE}-ok" / "SPEC.md").read_text(encoding="utf-8")
    assert c.parse_frontmatter(spec).data["title"] == "cách ly theo loại"
    assert init.main([str(root), "--sprint", "x", "--title", "a", "--title-file", str(title)]) == 2


@pytest.mark.parametrize("title, warns", [("c?ch ly", True), ("cách ly \ufffd", True), ("Có nên cache?", False),
                                          ("Vì sao chậm? Đo lại", False), ("cách ly", False)])
def test_replacement_characters_in_title_warn(tmp_path, capsys, title, warns):
    assert init.main([str(tmp_path), "--date", DATE, "--sprint", "ok", "--title", title], env={"AGENT_AGILE_TIERS": ""}) == 0
    err = capsys.readouterr().err
    assert ("--title-file" in err and "-X utf8" in err) == warns, err


def test_title_round_trips_through_a_real_process(tmp_path):
    result = run_script("init.py", str(tmp_path), "--apply", "--date", DATE, "--sprint", "ok", "--title", "cách ly ạ")
    assert result.returncode == 0, result.stdout + result.stderr
    spec = (tmp_path / "docs" / "plans" / f"{DATE}-ok" / "SPEC.md").read_text(encoding="utf-8")
    assert "title: cách ly ạ" in spec


def test_missing_tiers_table_warns_only_for_a_sprint(tmp_path, capsys):
    sprint = ["--sprint", "ok", "--title", "X"]
    assert init.main([str(tmp_path), "--date", DATE], env={}) == 0
    assert "AGENT_AGILE_TIERS" not in capsys.readouterr().err
    assert init.main([str(tmp_path), "--date", DATE, *sprint], env={}) == 0
    assert "AGENT_AGILE_TIERS" in capsys.readouterr().err
    table = tmp_path / "tiers.json"
    table.write_text("{}", encoding="utf-8")
    assert init.main([str(tmp_path), "--date", DATE, *sprint], env={"AGENT_AGILE_TIERS": str(table)}) == 0
    assert "AGENT_AGILE_TIERS" not in capsys.readouterr().err
    assert init.main([str(tmp_path), "--date", DATE, *sprint], env={"AGENT_AGILE_TIERS": str(tmp_path / "none.json")}) == 0
    assert "AGENT_AGILE_TIERS" in capsys.readouterr().err
