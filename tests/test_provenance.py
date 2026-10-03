"""Nguồn gốc (SC6): mọi skill và agent ghi nguồn, mốc SHA, giấy phép; mốc khớp UPSTREAM.md, cờ viết lại khớp
THIRD_PARTY.md; mọi nguồn dạng repo có dòng ở Sổ theo dõi của UPSTREAM.md, chủ nguồn khớp `UPSTREAM_OWNERS`
của `check.py`. Quy ước khoá: `skills/README.md` mục 1.
"""

from __future__ import annotations

import re

import pytest

from conftest import REPO
import _common as c
import check

REQUIRED = ("source", "source_sha", "license", "rewrite_before_public")
FILES = sorted(REPO.glob("skills/*/SKILL.md")) + sorted(p for p in REPO.glob("agents/*.md") if p.name != "README.md")
IDS = [p.relative_to(REPO).as_posix() for p in FILES]


def front(path):
    fm = c.parse_frontmatter(c.read_text(path))
    assert fm is not None, "thiếu frontmatter"
    return fm.data


def as_list(value):
    return value if isinstance(value, list) else [value]


def upstream_shas() -> set:
    return set(re.findall(r"\b[0-9a-f]{40}\b", c.read_text(REPO / "UPSTREAM.md")))


def rewrite_list(text: str | None = None) -> set:
    """Tên skill ở cột đầu bảng mục 3 ("phải viết lại trước khi công khai") của THIRD_PARTY.md (hoặc của `text`)."""
    text = c.read_text(REPO / "THIRD_PARTY.md") if text is None else text
    section = re.search(r"^## 3\..*?(?=^## |\Z)", text, re.S | re.M)
    assert section, "THIRD_PARTY.md thiếu mục 3"
    names = set()
    for line in section.group(0).splitlines():
        cells = c.table_cells(line)
        if cells and not c.is_separator_row(cells):
            m = re.fullmatch(r"`([a-z0-9-]+)`", cells[0])
            if m:
                names.add(m.group(1))
    return names


def test_files_found():
    assert len([p for p in FILES if p.parent.parent.name == "skills"]) >= 28
    assert len([p for p in FILES if p.parent.name == "agents"]) >= 7


@pytest.mark.parametrize("path", FILES, ids=IDS)
def test_required_keys(path):
    data = front(path)
    missing = [k for k in REQUIRED if k not in data]
    assert not missing, f"thiếu khoá {missing}"
    assert all(str(s).strip() for s in as_list(data["source"])), "source rỗng"
    assert str(data["license"]).strip(), "license rỗng"
    assert data["rewrite_before_public"] in (True, False), "rewrite_before_public phải là true/false"


@pytest.mark.parametrize("path", FILES, ids=IDS)
def test_source_sha_parallel_to_source(path):
    data = front(path)
    if isinstance(data["source"], list):
        shas = data["source_sha"]
        assert isinstance(shas, list) and len(shas) == len(data["source"]), \
            "source là danh sách thì source_sha phải là danh sách cùng độ dài, cùng thứ tự"
        licenses = data["license"]
        assert isinstance(licenses, list) and len(licenses) == len(data["source"]), \
            "source là danh sách thì license phải là danh sách cùng độ dài, cùng thứ tự"


@pytest.mark.parametrize("path", FILES, ids=IDS)
def test_unlicensed_source_is_written_none(path):
    assert "unlicensed" not in [str(x).strip() for x in as_list(front(path)["license"])], \
        "nguồn không giấy phép ghi `none`"


@pytest.mark.parametrize("path", FILES, ids=IDS)
def test_every_sha_is_pinned_in_upstream(path):
    data = front(path)
    known = upstream_shas()
    shas = [s for s in as_list(data["source_sha"]) + as_list(data.get("base_sha")) if s is not None]
    for sha in shas:
        assert re.fullmatch(r"[0-9a-f]{40}", str(sha)), f"SHA không đủ 40 ký tự hex: {sha}"
        assert sha in known, f"{sha} không có trong UPSTREAM.md"


def test_rewrite_flag_matches_third_party():
    flagged = {p.parent.name for p in FILES if p.name == "SKILL.md" and front(p)["rewrite_before_public"] is True}
    flagged |= {p.stem for p in FILES if p.parent.name == "agents" and front(p)["rewrite_before_public"] is True}
    listed = rewrite_list()  # thiếu mục 3 thì tự báo lỗi; bảng rỗng hợp lệ khi không skill nào mang cờ (SC7)
    assert flagged == listed, f"cờ true nhưng thiếu ở THIRD_PARTY: {sorted(flagged - listed)}; " \
                              f"có ở THIRD_PARTY nhưng cờ false: {sorted(listed - flagged)}"


def test_rewrite_list_reads_a_table_row():
    text = "\n".join(["## 2. Khác", "", "| `y` | a |", "", "## 3. Phải viết lại", "", "| Skill | Nguồn |", "|---|---|",
                        "| `x` | private |", "", "## 4. Hết", ""])
    assert rewrite_list(text) == {"x"}


def test_rewrite_list_fails_without_section_3():
    with pytest.raises(AssertionError, match="mục 3"):
        rewrite_list("\n".join(["## 2. Khác", "", "| `x` | private |", ""]))


# Sổ theo dõi nguồn gốc (UPSTREAM.md): nguồn sự thật duy nhất để kiểm bản mới (docs/updating-from-upstream.md).
# Mọi nguồn dạng repo phải có một dòng ở đó, và chủ của nó phải khớp allowlist chống rò `UPSTREAM_OWNERS`.
_SPAN_REPO = re.compile(r"`([A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*)`")
_BARE_REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*")


def upstream_text() -> str:
    return c.read_text(REPO / "UPSTREAM.md")


def catalog_sources(text: str | None = None) -> set:
    """`owner/repo` (casefold) ở cột đầu các bảng của mục "Sổ theo dõi nguồn gốc"."""
    text = upstream_text() if text is None else text
    section = re.search(r"^## Sổ theo dõi nguồn gốc\n.*?(?=^## |\Z)", text, re.S | re.M)
    assert section, "UPSTREAM.md thiếu mục '## Sổ theo dõi nguồn gốc'"
    found = set()
    for line in section.group(0).splitlines():
        cells = c.table_cells(line)
        if cells and not c.is_separator_row(cells):
            found |= {m.group(1).casefold() for m in _SPAN_REPO.finditer(cells[0])}
    return found


def owner(repo: str) -> str:
    return repo.split("/", 1)[0].casefold()


def test_catalog_has_rows():
    assert len(catalog_sources()) >= 20


def test_catalog_owners_are_allowlisted():
    missing = sorted(r for r in catalog_sources() if owner(r) not in check.UPSTREAM_OWNERS)
    assert not missing, f"chủ chưa có trong UPSTREAM_OWNERS của scripts/check.py: {missing}"


def test_allowlist_has_no_stale_owner():
    used = {owner(r) for r in catalog_sources()}
    stale = sorted(check.UPSTREAM_OWNERS - used)
    assert not stale, f"UPSTREAM_OWNERS có chủ không còn nguồn nào trong Sổ theo dõi: {stale}"


def test_every_upstream_repo_is_in_catalog():
    """Repo nhắc ở bất kỳ khối nào của UPSTREAM.md (đợt, dự kiến) đều phải có dòng trong Sổ theo dõi."""
    text = upstream_text()
    catalog = catalog_sources(text)
    named = {m.group(1).casefold() for m in _SPAN_REPO.finditer(text) if owner(m.group(1)) in check.UPSTREAM_OWNERS}
    missing = sorted(named - catalog)
    assert not missing, f"nguồn nhắc trong UPSTREAM.md mà thiếu dòng ở Sổ theo dõi: {missing}"


@pytest.mark.parametrize("path", FILES, ids=IDS)
def test_frontmatter_source_is_in_catalog(path):
    catalog = catalog_sources()
    for entry in as_list(front(path)["source"]):
        head = str(entry).split()[0]
        if head.startswith("private-") or head == "concept:" or not _BARE_REPO.fullmatch(head):
            continue
        assert head.casefold() in catalog, f"nguồn {head} không có dòng ở Sổ theo dõi của UPSTREAM.md"


def test_catalog_detects_missing_row():
    """Đột biến: bỏ dòng của một nguồn khỏi Sổ theo dõi thì phép đối chiếu phải thấy thiếu."""
    text = upstream_text()
    mutated = "\n".join(l for l in text.splitlines() if not l.startswith("| `obra/superpowers-lab`"))
    assert "obra/superpowers-lab" in catalog_sources(text)
    assert "obra/superpowers-lab" not in catalog_sources(mutated)


# Số đo trùng câu chữ nguồn (8-gram) chỉ đúng kèm điều kiện đo (vòng sửa cuối, từ re-review lần 2): số 0 có được SAU KHI loại
# stoplist 45 cụm chung; không loại thì còn cụm trùng ở 5/7 đích. Câu nêu số đo phải mang điều kiện; metadata vào băm
# (`skills/**`) thì không nêu số đo, vì đổi chữ ở đó đổi `skill_sha` và buộc chạy lại thử nghiệm.
GRAM_CLAIM = re.compile(r"8-gram|overlap 0", re.I)
GRAM_SUFFIXES = {".md", ".json", ".txt", ".yml", ".yaml"}


def gram_claim_problems(root=REPO) -> list:
    """Lỗi ở mọi tệp văn bản dưới `root` (trừ `tests/`, `.git`, `docs/plans`): trong `skills/` cấm nêu số đo 8-gram; ngoài
    đó mỗi lần nêu phải có `stoplist` trong 200 ký tự kế tiếp."""
    found = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        parts = rel.parts
        if (not path.is_file() or path.suffix not in GRAM_SUFFIXES or "tests" in parts or ".git" in parts
                or parts[:2] == ("docs", "plans")):
            continue
        text = c.read_text(path)
        for m in GRAM_CLAIM.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            if parts[0] == "skills":
                found.append(f"{rel.as_posix()}:{line}: metadata vào băm không được nêu số đo 8-gram")
            elif "stoplist" not in text[m.start():m.start() + 200].lower():
                found.append(f"{rel.as_posix()}:{line}: số đo 8-gram thiếu điều kiện (loại stoplist 45 cụm chung)")
    return sorted(set(found))  # một dòng nêu cả '8-gram' và 'overlap 0' chỉ báo một lần


def test_8gram_claims_carry_their_condition():
    assert gram_claim_problems() == []


def test_8gram_claim_check_catches_each_kind_of_bad_claim(tmp_path):
    (tmp_path / "skills" / "x").mkdir(parents=True)
    (tmp_path / "skills" / "x" / "SKILL.md").write_text("source: 8-gram overlap 0 after rephrasing\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("Viết lại; 8-gram 0 trùng sau khi diễn đạt lại\n", encoding="utf-8")
    (tmp_path / "THIRD_PARTY.md").write_text("8-gram bằng 0 sau khi loại stoplist 45 cụm chung\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "t.md").write_text("8-gram 0\n", encoding="utf-8")
    (tmp_path / "docs" / "plans").mkdir(parents=True)
    (tmp_path / "docs" / "plans" / "p.md").write_text("8-gram 0\n", encoding="utf-8")
    found = gram_claim_problems(tmp_path)
    assert len(found) == 2, found
    assert any("skills/x/SKILL.md:1" in f and "metadata vào băm" in f for f in found)
    assert any("CHANGELOG.md:1" in f and "thiếu điều kiện" in f for f in found)


# THIRD_PARTY mục 3: file đã liệt kê là "đã viết lại từ danh sách ý, còn mang câu chữ nguồn" thì VẪN phải viết lại thật
# sự trước khi công khai (`CO2`); câu "không cần viết lại lần nữa" cho chúng mâu thuẫn với lời đó (vòng sửa cuối, lỗi a của re-review lần 2).
NO_REWRITE_NEEDED = "không cần viết lại lần nữa"
MUST_REWRITE = "phải viết lại thật sự trước khi công khai"


def third_party_contradictions(text: str) -> list:
    if MUST_REWRITE in text and NO_REWRITE_NEEDED in text:
        return [f"THIRD_PARTY.md vừa ghi '{MUST_REWRITE}' vừa ghi '{NO_REWRITE_NEEDED}'"]
    return []


def test_third_party_does_not_excuse_the_listed_files_from_rewriting():
    text = c.read_text(REPO / "THIRD_PARTY.md")
    assert MUST_REWRITE in text, "THIRD_PARTY.md mất lời 'phải viết lại thật sự trước khi công khai'"
    assert third_party_contradictions(text) == []


def test_third_party_contradiction_check_catches_the_old_sentence():
    old = f"7 đích: {MUST_REWRITE}. Các file đã liệt kê ở trên {NO_REWRITE_NEEDED}."
    assert len(third_party_contradictions(old)) == 1
    assert third_party_contradictions(f"7 đích: {MUST_REWRITE}.") == []
