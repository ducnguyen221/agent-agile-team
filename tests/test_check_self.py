"""`check.py --self`: lõi sạch theo danh sách từ cấm ngoài repo, một thang mức, ngân sách `AGENTS.md`.

Danh sách từ cấm thật nằm ngoài repo (hợp đồng `AGENT_AGILE_DENYLIST` ở `tests/README.md`). Các test đột
biến dưới đây tự tạo danh sách tạm với một từ giả, nên chạy được trên mọi máy.
"""

import os
from pathlib import Path

import pytest

from conftest import REPO, run_script
import check

WORD = "zq-private-marker"
# Từ chữ thật của danh sách cấm, ghép lúc chạy để chính file này không chứa nó đứng riêng; "brainstorming"
# (tên skill gốc của shaping-spec) phải lọt qua vì khớp nguyên từ.
PLAIN = "bra" + "in"


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "skills" / "demo" / "tests").mkdir(parents=True)
    (root / "method").mkdir()
    (root / "tests" / "fixtures").mkdir(parents=True)
    (root / "AGENTS.md").write_text("# Luật lõi\n\nNgắn gọn.\n", encoding="utf-8")
    (root / "README.md").write_text("# Repo\n\nSạch.\n", encoding="utf-8")
    return root


def denylist(tmp_path: Path, *words: str) -> Path:
    path = tmp_path / "deny.txt"
    path.write_text("# từ cấm thử\n\n" + "\n".join(words) + "\n", encoding="utf-8")
    return path


def rules_of(report) -> set:
    return {f.rule for f in report.findings}


def test_clean_repo_passes(tmp_path):
    root = make_repo(tmp_path)
    report = check.run_self(root, denylist(tmp_path, WORD))
    assert report.findings == [] and report.exit_code == 0
    assert report.denylist_status == "ok"


def test_denylist_word_is_caught_case_insensitively(tmp_path):
    root = make_repo(tmp_path)
    (root / "README.md").write_text("# Repo\n\nCó dấu ZQ-Private-Marker ở đây.\n", encoding="utf-8")
    report = check.run_self(root, denylist(tmp_path, WORD))
    hits = [f for f in report.findings if f.rule == "leak-denylist"]
    assert len(hits) == 1 and hits[0].line == 3 and hits[0].level == "Chặn"
    assert report.exit_code == 1
    assert WORD not in hits[0].render().lower(), "báo cáo không được in lại chính từ cấm"


def test_denylist_exemptions(tmp_path):
    root = make_repo(tmp_path)
    (root / "NOTICE").write_text(f"Copyright (c) 2026 {WORD}\n\nAny text {WORD}\n", encoding="utf-8")
    (root / "THIRD_PARTY.md").write_text(f"| nguồn | MIT © 2026 {WORD} |\nCopyright {WORD}\n", encoding="utf-8")
    (root / "UPSTREAM.md").write_text(f"# Nguồn\n\n| `obra/{WORD}-skills` | `0123abcd` | main |\n", encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs" / "MIGRATION.md").write_text(f"| `{WORD}:old-skill` | `new` |\n| `{WORD}:*` | — |\n",
                                                 encoding="utf-8")
    (root / "skills" / "demo" / "tests" / "pressure.md").write_text(f"---\nmodel: {WORD}\n---\n\nChạy bằng model `{WORD}`.\n", encoding="utf-8")
    assert check.run_self(root, denylist(tmp_path, WORD)).findings == []


@pytest.mark.parametrize("rel, text", [
    ("UPSTREAM.md", f"# Nguồn\n\nVăn xuôi nhắc {WORD}.\n"),
    ("UPSTREAM.md", f"| `obra/repo` | gốc {WORD} (không giấy phép) | private |\n"),   # cột khác cột nguồn
    ("UPSTREAM.md", f"| `{WORD}/private-repo` | `0123abcd` | main |\n"),             # owner ngoài allowlist nguồn công khai
    ("THIRD_PARTY.md", f"| `adr` | `SKILL.md` | bộ {WORD} |\n"),                     # không phải dòng ghi công
    ("docs/MIGRATION.md", f"Gặp tên {WORD} trong hồ sơ cũ thì tra bảng.\n"),           # văn xuôi, không phải mã cũ
    ("docs/MIGRATION.md", f"| `{WORD}/path/file.md` | x |\n"),                         # code span không phải `bộ:tên`
])
def test_denylist_exemptions_are_narrow(tmp_path, rel, text):
    """Đột biến `RF4`/`RF5`: miễn trừ chỉ che đúng phần được nêu (ghi công, `owner/repo` + SHA, mã skill cũ)."""
    root = make_repo(tmp_path)
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")
    hits = [f for f in check.run_self(root, denylist(tmp_path, WORD)).findings if f.rule == "leak-denylist"]
    assert len(hits) == 1, f"{rel}: {hits}"


MANIFEST = """{{
  "name": "demo",
  "description": "Sạch.",
  "author": {{
    "name": "{w}",
    "email": "{w}@example.com",
    "url": "https://{w}.example"
  }},
  "homepage": "https://example.com/{w}",
  "repository": "https://example.com/{w}/demo",
  "license": "UNLICENSED"
}}
"""
MARKETPLACE = """{{
  "name": "demo",
  "owner": {{
    "name": "{w}",
    "email": "{w}@example.com"
  }},
  "plugins": [
    {{
      "name": "demo",
      "author": {{ "name": "{w}", "url": "https://{w}.example" }},
      "homepage": "https://example.com/{w}"
    }}
  ]
}}
"""


def test_author_attribution_exemptions(tmp_path):
    """Quyết định ghi công tác giả (`author-attribution`): tên, email, trang của tác giả chỉ được miễn ở trường
    tác giả của ba manifest, mục Tác giả/Author của hai README và dòng Copyright của LICENSE."""
    root = make_repo(tmp_path)
    for rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(MANIFEST.format(w=WORD), encoding="utf-8")
    (root / ".claude-plugin" / "marketplace.json").write_text(MARKETPLACE.format(w=WORD), encoding="utf-8")
    (root / "README.md").write_text(f"# Repo\n\nSạch.\n\n## Author\n\n{WORD} — https://{WORD}.example\n", encoding="utf-8")
    (root / "README.vi.md").write_text(f"# Repo\n\nSạch.\n\n## Tác giả\n\n{WORD}\n", encoding="utf-8")
    (root / "LICENSE").write_text(f"All rights reserved — private.\n\nCopyright (c) 2026 {WORD}.\n", encoding="utf-8")
    assert check.run_self(root, denylist(tmp_path, WORD)).findings == []


@pytest.mark.parametrize("rel, text", [
    ("skills/demo/SKILL.md", f"# Demo\n\nSkill do {WORD} viết.\n"),                         # văn xuôi skill: luôn Chặn
    (".claude-plugin/plugin.json", f'{{\n  "description": "by {WORD}",\n  "author": {{ "name": "x" }}\n}}\n'),
    (".codex-plugin/plugin.json", f'{{\n  "author": {{\n    "name": "x"\n  }},\n  "keywords": ["{WORD}"]\n}}\n'),
    ("docs/other.json", f'{{\n  "author": {{ "name": "{WORD}" }}\n}}\n'),                    # không phải manifest
    ("README.md", f"# Repo\n\nDo {WORD} viết.\n\n## Author\n\nx\n"),                           # ngoài mục Author
    ("README.md", f"# Repo\n\n## Author\n\nx\n\n## Licence\n\n{WORD}\n"),                      # mục kế tiếp
    ("README.vi.md", f"# Repo\n\n## Tác giả của bản dịch\n\n{WORD}\n"),                        # tiêu đề khác
    ("GUIDE.md", f"# Hướng dẫn\n\n## Author\n\n{WORD}\n"),                                     # mục Author ngoài README
    ("LICENSE", f"All rights reserved — {WORD}.\n"),                                           # không phải dòng Copyright
])
def test_author_attribution_is_narrow(tmp_path, rel, text):
    root = make_repo(tmp_path)
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")
    hits = [f for f in check.run_self(root, denylist(tmp_path, WORD)).findings if f.rule == "leak-denylist"]
    assert len(hits) == 1 and hits[0].level == "Chặn", f"{rel}: {hits}"


def _author_word() -> str:
    """Từ cấm chứa trong URL tác giả — rút từ chính hằng của `check.py` để file này không chứa nó đứng riêng."""
    return check.AUTHOR_SITE.split(".")[0]


def test_author_urls_are_masked_in_any_file(tmp_path):
    root = make_repo(tmp_path)
    word = _author_word()
    (root / "skills" / "demo" / "SKILL.md").write_text(
        f"# Demo\n\nTrang https://{check.AUTHOR_SITE}/profile · repo https://{check.AUTHOR_REPO_URL}.git\n"
        f"Clone: `git clone https://{check.AUTHOR_REPO_URL.upper()}`\n", encoding="utf-8")
    assert check.run_self(root, denylist(tmp_path, word)).findings == []


@pytest.mark.parametrize("text", [
    "https://github.com/{owner}/other-repo",            # repo khác của cùng tài khoản
    "`{owner}/agent-agile-team`",                       # dạng viết tắt owner/repo không phải URL đã duyệt
    "Thư: {word}@example.com",                          # email ngoài trường tác giả của manifest
    "https://{site}x/trang",                            # tên miền khác có cùng tiền tố
])
def test_author_url_mask_is_narrow(tmp_path, text):
    root = make_repo(tmp_path)
    word = _author_word()
    owner = check.AUTHOR_REPO_URL.split("/")[1]
    line = text.format(owner=owner, word=word, site=check.AUTHOR_SITE)
    (root / "skills" / "demo" / "SKILL.md").write_text(f"# Demo\n\n{line}\n", encoding="utf-8")
    hits = [f for f in check.run_self(root, denylist(tmp_path, word)).findings if f.rule == "leak-denylist"]
    assert len(hits) == 1, f"{line}: {hits}"


def test_every_leak_exemption_is_explicit_and_documented():
    readme = (REPO / "scripts" / "README.md").read_text(encoding="utf-8")
    assert check.LEAK_EXEMPTIONS, "danh sách miễn trừ phải tường minh"
    for pattern, kind, reason in check.LEAK_EXEMPTIONS:
        assert kind in check.LEAK_EXEMPTION_KINDS, f"{pattern}: kiểu miễn trừ lạ {kind!r}"
        assert len(reason) > 20, f"{pattern}: thiếu lý do"
        assert pattern in readme, f"{pattern} chưa ghi ở scripts/README.md mục Phạm vi --self"


def test_denylist_scans_non_markdown_and_fixtures(tmp_path):
    root = make_repo(tmp_path)
    (root / "tests" / "fixtures" / "x.json").write_text(f'{{"a": "{WORD}"}}\n', encoding="utf-8")
    assert rules_of(check.run_self(root, denylist(tmp_path, WORD))) == {"leak-denylist"}


def test_missing_denylist_is_not_configured_not_silent(tmp_path, capsys):
    root = make_repo(tmp_path)
    report = check.run_self(root, None)
    assert report.exit_code == 0 and report.denylist_status == "NOT_CONFIGURED"
    report = check.run_self(root, tmp_path / "không-có.txt")
    assert report.denylist_status == "NOT_CONFIGURED"
    code = check.main(["--self", "--root", str(root)], env={})
    captured = capsys.readouterr()
    assert code == 0
    assert "NOT_CONFIGURED" in captured.err and "AGENT_AGILE_DENYLIST" in captured.err


def test_main_reads_denylist_from_env(tmp_path, capsys):
    root = make_repo(tmp_path)
    (root / "README.md").write_text(f"{WORD}\n", encoding="utf-8")
    code = check.main(["--self", "--root", str(root)], env={"AGENT_AGILE_DENYLIST": str(denylist(tmp_path, WORD))})
    assert code == 1
    assert "[leak-denylist]" in capsys.readouterr().out


def test_agents_md_budget(tmp_path):
    root = make_repo(tmp_path)
    (root / "AGENTS.md").write_text("dòng\n" * 121, encoding="utf-8")
    assert "agents-md-budget" in rules_of(check.run_self(root, None))
    (root / "AGENTS.md").write_text(("x" * 100 + "\n") * 102, encoding="utf-8")  # 102 dòng, 10 302 byte
    assert "agents-md-budget" in rules_of(check.run_self(root, None))
    (root / "AGENTS.md").write_text("dòng\n" * 120, encoding="utf-8")
    assert "agents-md-budget" not in rules_of(check.run_self(root, None))


def test_old_scale_only_inside_conversion_table(tmp_path):
    root = make_repo(tmp_path)
    table = "| Mức | Nghĩa |\n|---|---|\n| Critical | x |\n"
    (root / "method" / "severity.md").write_text(table, encoding="utf-8")
    assert check.run_self(root, None).findings == []
    (root / "method" / "other.md").write_text(table, encoding="utf-8")
    assert rules_of(check.run_self(root, None)) == {"old-scale-label"}


def test_self_skips_fixtures_and_skill_scenarios_for_document_rules(tmp_path):
    root = make_repo(tmp_path)
    (root / "tests" / "fixtures" / "SPEC.md").write_text("Mã hỏng cố ý P1.\n", encoding="utf-8")
    (root / "skills" / "demo" / "tests" / "pressure.md").write_text("## ID1 — kịch bản\n", encoding="utf-8")
    assert check.run_self(root, None).findings == []
    (root / "skills" / "demo" / "SKILL.md").write_text("## ID1 — tiền tố tự chế\n", encoding="utf-8")
    assert rules_of(check.run_self(root, None)) == {"id-unknown-prefix"}


def test_this_repo_is_clean():
    report = check.run_self(REPO, None)
    assert [f.render() for f in report.findings if f.level in ("Chặn", "Phải sửa")] == []
    assert report.exit_code == 0


def test_this_repo_against_real_denylist():
    configured = os.environ.get("AGENT_AGILE_DENYLIST")
    if not configured or not Path(configured).is_file():
        pytest.skip("Chưa chạy: AGENT_AGILE_DENYLIST chưa đặt hoặc file không đọc được (tests/README.md)")
    report = check.run_self(REPO, Path(configured))
    assert report.denylist_status == "ok"
    assert [f.render() for f in report.findings if f.rule == "leak-denylist"] == []


def test_self_cli_standalone():
    result = run_script("check.py", "--self", env={"AGENT_AGILE_DENYLIST": ""})
    assert result.returncode == 0, result.stdout + result.stderr
    assert "NOT_CONFIGURED" in result.stderr


def _git(root: Path, *args: str) -> None:
    import subprocess
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, stdin=subprocess.DEVNULL)


def test_self_scans_untracked_but_not_ignored_files(tmp_path):
    root = make_repo(tmp_path)
    (root / ".gitignore").write_text("/scratch/\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "add", "AGENTS.md", "README.md", ".gitignore")
    (root / "NEW.md").write_text(f"chưa add: {WORD}\n", encoding="utf-8")
    (root / "scratch").mkdir()
    (root / "scratch" / "x.md").write_text(f"bị ignore: {WORD}\n", encoding="utf-8")
    hits = [f for f in check.run_self(root, denylist(tmp_path, WORD)).findings if f.rule == "leak-denylist"]
    assert [Path(f.path).name for f in hits] == ["NEW.md"]


def test_self_with_paths_is_usage_error(tmp_path):
    with pytest.raises(SystemExit) as err:
        check.main(["--self", str(tmp_path)], env={})
    assert err.value.code == 2


def test_denylist_plain_word_matches_whole_words_only(tmp_path):
    root = make_repo(tmp_path)
    (root / "README.md").write_text("# Repo\n\nSkill gốc tên brainstorming, đã đổi tên.\n", encoding="utf-8")
    assert check.run_self(root, denylist(tmp_path, PLAIN)).findings == []
    (root / "README.md").write_text(f"# Repo\n\nKho tri thức {PLAIN.title()} của máy.\n", encoding="utf-8")
    hits = [f for f in check.run_self(root, denylist(tmp_path, PLAIN)).findings if f.rule == "leak-denylist"]
    assert len(hits) == 1 and hits[0].line == 3
    # chữ số, gạch dưới, dấu chấm không phải chữ cái → vẫn là ranh giới
    for text in (f"{PLAIN}_notes", f"{PLAIN}2", f"~/.{PLAIN}/x", f"{PLAIN.upper()}."):
        (root / "README.md").write_text(f"# Repo\n\n{text}\n", encoding="utf-8")
        assert rules_of(check.run_self(root, denylist(tmp_path, PLAIN))) == {"leak-denylist"}, text


def test_denylist_path_entry_matches_substring(tmp_path):
    root = make_repo(tmp_path)
    # mục chứa ký tự đường dẫn khớp chuỗi con, kể cả khi dính liền chữ cái
    (root / "README.md").write_text("# Repo\n\nMở file ở XC:\\Users\\someone\\a.txt.\n", encoding="utf-8")
    assert rules_of(check.run_self(root, denylist(tmp_path, "c:\\users"))) == {"leak-denylist"}
    home = "/" + "home" + "/"  # ghép lúc chạy: chính file này cũng bị quét bằng danh sách thật
    (root / "README.md").write_text(f"# Repo\n\nĐường {home}someone/x.\n", encoding="utf-8")
    assert rules_of(check.run_self(root, denylist(tmp_path, home))) == {"leak-denylist"}


def test_denylist_whole_word_applies_to_file_names(tmp_path):
    root = make_repo(tmp_path)
    (root / "skills" / "demo" / "brainstorming.md").write_text("# x\n", encoding="utf-8")
    assert check.run_self(root, denylist(tmp_path, PLAIN)).findings == []
    (root / "skills" / "demo" / f"{PLAIN}-notes.md").write_text("# x\n", encoding="utf-8")
    hits = [f for f in check.run_self(root, denylist(tmp_path, PLAIN)).findings if f.rule == "leak-denylist"]
    assert len(hits) == 1 and f"{PLAIN}-notes" in str(hits[0].path)
