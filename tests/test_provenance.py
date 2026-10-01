"""Nguồn gốc (SC6): mọi skill và agent ghi nguồn, mốc SHA, giấy phép; mốc khớp UPSTREAM.md, cờ viết lại khớp
THIRD_PARTY.md. Quy ước khoá: `skills/README.md` mục 1.
"""

from __future__ import annotations

import re

import pytest

from conftest import REPO
import _common as c

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


def rewrite_list() -> set:
    """Tên skill ở cột đầu bảng mục 3 ("phải viết lại trước khi công khai") của THIRD_PARTY.md."""
    text = c.read_text(REPO / "THIRD_PARTY.md")
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
    listed = rewrite_list()
    assert listed, "THIRD_PARTY.md mục 3 không có dòng nào"
    assert flagged == listed, f"cờ true nhưng thiếu ở THIRD_PARTY: {sorted(flagged - listed)}; " \
                              f"có ở THIRD_PARTY nhưng cờ false: {sorted(listed - flagged)}"
