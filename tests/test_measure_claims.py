"""Phép kiểm số đo trùng câu chữ (8-gram): câu nêu số đo phải mang điều kiện đo (loại stoplist), và metadata vào băm của skill
không nêu số đo. Tách ra từ `tests/test_provenance.py` khi bỏ tài liệu nguồn (SPR-19): nhóm này quét cả repo, không liên quan nguồn.
"""

from __future__ import annotations

import re

import pytest

from conftest import REPO
import _common as c


# Số đo trùng câu chữ nguồn (8-gram) chỉ đúng kèm điều kiện đo (vòng sửa cuối, từ re-review lần 2): số 0 có được SAU KHI loại
# stoplist 45 cụm chung; không loại thì còn cụm trùng ở 5/7 đích. Câu nêu số đo phải mang điều kiện; metadata vào băm
# (`skills/**`) thì không nêu số đo, vì đổi chữ ở đó đổi `skill_sha` và buộc chạy lại thử nghiệm.
GRAM_CLAIM = re.compile(r"\b\d+[- ]?gram\b|\bn-gram\b|overlap\s*0|trùng\s+0\s+cụm|\b0\s+trùng", re.I)
# Điều kiện đo: câu phải nói đã LOẠI stoplist (không chỉ có chữ `stoplist` gần đó, như "không dùng stoplist").
GRAM_CONDITION = re.compile(r"loại\s+(?:bỏ\s+)?stoplist", re.I)
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
            if parts[0] == "skills" and len(parts) >= 3:  # `skills/<tên>/**` vào băm; `skills/README.md` thì không
                found.append(f"{rel.as_posix()}:{line}: metadata vào băm không được nêu số đo 8-gram")
            elif not GRAM_CONDITION.search(text[m.start():m.start() + 200]):
                found.append(f"{rel.as_posix()}:{line}: số đo 8-gram thiếu điều kiện (loại stoplist 45 cụm chung)")
    return sorted(set(found))  # một dòng nêu cả '8-gram' và 'overlap 0' chỉ báo một lần


def test_8gram_claims_carry_their_condition():
    assert gram_claim_problems() == []


def test_8gram_claim_check_catches_each_kind_of_bad_claim(tmp_path):
    (tmp_path / "skills" / "x").mkdir(parents=True)
    (tmp_path / "skills" / "x" / "SKILL.md").write_text("source: 8-gram overlap 0 after rephrasing\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("Viết lại; 8-gram 0 trùng sau khi diễn đạt lại\n", encoding="utf-8")
    (tmp_path / "OTHER.md").write_text("8-gram bằng 0 sau khi loại stoplist 45 cụm chung\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "t.md").write_text("8-gram 0\n", encoding="utf-8")
    (tmp_path / "docs" / "plans").mkdir(parents=True)
    (tmp_path / "docs" / "plans" / "p.md").write_text("8-gram 0\n", encoding="utf-8")
    found = gram_claim_problems(tmp_path)
    assert len(found) == 2, found
    assert any("skills/x/SKILL.md:1" in f and "metadata vào băm" in f for f in found)
    assert any("CHANGELOG.md:1" in f and "thiếu điều kiện" in f for f in found)





# TK12.1 (3): phép kiểm số đo nhận MỌI cách viết của phép so (RF171), điều kiện phải là "loại stoplist" chứ không chỉ có chữ
# `stoplist` gần đó, và `skills/README.md` (không thuộc cây của skill nào, không vào băm) không bị coi là metadata vào băm.
@pytest.mark.parametrize("phrase", ["8-gram 0", "8 gram 0", "8gram bằng 0", "n-gram 0", "6-gram", "trùng 0 cụm", "overlap 0",
                                    "overlap  0", "8-GRAM", "0 trùng"])
def test_gram_claim_matches_every_spelling(phrase):
    assert GRAM_CLAIM.search(phrase), f"{phrase!r} lọt"


@pytest.mark.parametrize("phrase", ["programmatic", "diagram 8", "gram", "đã đo trùng câu chữ"])
def test_gram_claim_does_not_match_unrelated_words(phrase):
    assert not GRAM_CLAIM.search(phrase), f"{phrase!r} bị bắt oan"


def test_gram_claim_needs_the_stoplist_condition_not_just_the_word(tmp_path):
    (tmp_path / "CHANGELOG.md").write_text("Viết lại; 8-gram 0, không dùng stoplist\n", encoding="utf-8")
    (tmp_path / "OTHER.md").write_text("n-gram bằng 0 sau khi loại stoplist 45 cụm chung\n", encoding="utf-8")
    (tmp_path / "NOTES.md").write_text("8 gram: trùng 0 cụm\n", encoding="utf-8")
    found = gram_claim_problems(tmp_path)
    assert any("CHANGELOG.md:1" in f for f in found), found
    assert any("NOTES.md:1" in f for f in found), found
    assert not any("OTHER.md" in f for f in found), found


def test_skills_readme_is_not_metadata_in_the_hash(tmp_path):
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "README.md").write_text("8-gram 0 trùng\n", encoding="utf-8")
    found = gram_claim_problems(tmp_path)
    assert len(found) == 1 and "thiếu điều kiện" in found[0] and "metadata vào băm" not in found[0], found
    (tmp_path / "skills" / "README.md").write_text("8-gram bằng 0 sau khi loại stoplist 45 cụm chung\n", encoding="utf-8")
    assert gram_claim_problems(tmp_path) == []
