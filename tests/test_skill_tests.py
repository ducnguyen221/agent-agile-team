"""Máy kiểm nợ thử (FR11.5, SC5): mọi skill kỷ luật có `tests/pressure.md`, mọi skill tham chiếu
(`metadata.kind: reference`) có `tests/retrieval.md`; file thử không còn ở trạng thái chưa chạy; file thử từ ngày bắt
đầu sprint có `skill_sha` + `tier`, và `skill_sha` khớp băm cây skill trừ `tests/` tính ở HEAD (công thức:
`git ls-tree HEAD:skills/<tên>` bỏ mục `tests`, rồi `git mktree`): skill đổi sau khi thử thì test đỏ, đến khi thử lại.
"""

from __future__ import annotations

import datetime
import re
import subprocess

import pytest

from conftest import REPO
import _common as c

# Ngày bắt đầu sprint wave-2: file thử có `date` từ ngày này trở đi phải mang `skill_sha` và `tier` (FR10.5).
SPRINT_START = datetime.date(2026, 10, 3)
NOT_RUN = re.compile(r"not run|pending|chưa chạy|dự kiến", re.I)
SKILLS = sorted(p.parent.name for p in REPO.glob("skills/*/SKILL.md"))


def front(path):
    """Frontmatter của file thử. Khoá `agent_ids` là bản ghi định danh agent (map lồng nhau, tập con YAML của
    `_common` không đọc được) chứ không phải khoá kiểm — bỏ khối đó trước khi đọc."""
    lines = c.read_text(path).splitlines()
    assert lines and lines[0] == "---", "thiếu frontmatter"
    kept, skipping = [], False
    for i, line in enumerate(lines):
        if i > 0 and line == "---":
            kept.extend(lines[i:])
            break
        if line.startswith("agent_ids:"):
            skipping = True
            continue
        if skipping and (line.startswith(" ") or not line.strip()):
            continue
        skipping = False
        kept.append(line)
    fm = c.parse_frontmatter("\n".join(kept) + "\n")
    assert fm is not None, "thiếu frontmatter"
    return fm.data


def head(value) -> str:
    """Phần đầu của một khoá văn tự do (RF67): bỏ dấu câu mở đầu (`(`, `)`, `;`, `—`, `-`…), rồi cắt ở `;`, `(` hoặc
    ` — `, nên chú thích sau đó không bị coi là trạng thái ("claude-sonnet-5-5 (all runs, …)" →
    "claude-sonnet-5-5") còn "(pending)" → "pending)" vẫn bị bắt. Rỗng khi giá trị chỉ có dấu câu."""
    text = re.sub(r"^[\s();—–-]+", "", str(value))
    return re.split(r";|\(| — ", text, maxsplit=1)[0].strip()


def is_reference(skill: str, root=REPO) -> bool:
    meta = front(root / "skills" / skill / "SKILL.md").get("metadata") or {}
    return isinstance(meta, dict) and meta.get("kind") == "reference"


def missing_test_file(skill: str, root=REPO):
    """Lỗi 'thiếu tệp thử' của một skill (kỷ luật cần `pressure.md`, tham chiếu cần `retrieval.md`), hoặc None."""
    name = "retrieval.md" if is_reference(skill, root) else "pressure.md"
    if not (root / "skills" / skill / "tests" / name).is_file():
        return f"skill {'tham chiếu' if name == 'retrieval.md' else 'kỷ luật'} `{skill}` thiếu tests/{name}"
    return None


def tree_hash(skill: str, repo=REPO):
    """Băm cây thư mục skill TRỪ `tests/` ở HEAD của `repo`. Trả None CHỈ khi không có lệnh `git`; git có mà lỗi
    (`ls-tree`/`mktree` mã thoát khác 0: `dubious ownership`, skill chưa commit ở HEAD…) thì test đỏ kèm stderr,
    không im lặng skip."""
    def git(*args, **kw):
        res = subprocess.run(["git", *args], cwd=repo, capture_output=True, timeout=60, **kw)
        if res.returncode != 0:
            pytest.fail(f"`git {' '.join(args)}` thoát {res.returncode}: {res.stderr.decode(errors='replace').strip()}")
        return res.stdout

    try:
        ls = git("ls-tree", f"HEAD:skills/{skill}")
        rows = [r for r in ls.split(b"\n") if r and r.split(b"\t", 1)[1] != b"tests"]
        return git("mktree", input=b"\n".join(rows) + b"\n").decode().strip()
    except FileNotFoundError:
        return None  # không có lệnh git: đây là ca skip duy nhất
    except subprocess.SubprocessError as exc:
        pytest.fail(f"git không chạy xong: {exc}")


def problems(data: dict) -> list:
    """Lỗi của một file thử (không gồm so `skill_sha` với cây skill)."""
    found = []
    for key in ("result", "model"):
        if key not in data or not str(data[key]).strip():
            found.append(f"thiếu khoá `{key}`")
        elif not head(data[key]):
            found.append(f"`{key}` không có trạng thái ở đầu: {str(data[key])!r}")
        elif NOT_RUN.search(head(data[key])):
            found.append(f"`{key}` ghi chưa chạy: {head(data[key])!r}")
    day = data.get("date")
    try:
        day = day if isinstance(day, datetime.date) else datetime.date.fromisoformat(str(day))
    except ValueError:
        found.append(f"`date` không phải ngày hợp lệ: {day!r}")
    else:
        if day >= SPRINT_START:
            if not re.fullmatch(r"[0-9a-f]{40}", str(data.get("skill_sha") or "")):
                found.append("thiếu `skill_sha` (40 ký tự hex) dù date từ ngày bắt đầu sprint")
            if not str(data.get("tier") or "").strip():
                found.append("thiếu `tier` dù date từ ngày bắt đầu sprint")
    return found


def test_skills_found():
    assert len(SKILLS) >= 28


@pytest.mark.parametrize("skill", SKILLS)
def test_skill_has_its_test_file(skill):
    assert missing_test_file(skill) is None, missing_test_file(skill)


TEST_FILES = [p for s in SKILLS for n in ("pressure.md", "retrieval.md") for p in [REPO / "skills" / s / "tests" / n] if p.is_file()]
IDS = [p.relative_to(REPO).as_posix() for p in TEST_FILES]


@pytest.mark.parametrize("path", TEST_FILES, ids=IDS)
def test_test_file_was_run(path):
    assert not problems(front(path))


def has_sha(path) -> bool:
    """File thử có khoá `skill_sha` không. File không đọc được frontmatter coi như có, để test dưới đỏ đúng lý do
    thay vì làm hỏng lúc thu thập."""
    try:
        return bool(front(path).get("skill_sha"))
    except Exception:
        return True


# Chỉ tham số hoá phép so băm cho file CÓ `skill_sha`: file cũ (date trước ngày bắt đầu sprint) không có thì không
# sinh ca nào, không còn ca skip; file từ ngày bắt đầu sprint thiếu `skill_sha` vẫn đỏ ở `test_test_file_was_run`.
SHA_FILES = [p for p in TEST_FILES if has_sha(p)]
SHA_IDS = [p.relative_to(REPO).as_posix() for p in SHA_FILES]


@pytest.mark.parametrize("path", SHA_FILES, ids=SHA_IDS)
def test_skill_sha_matches_skill_tree(path):
    data = front(path)
    actual = tree_hash(path.parent.parent.name)
    if actual is None:
        pytest.skip("không có lệnh git")
    assert str(data["skill_sha"]) == actual, \
        f"skill đổi sau khi thử, chạy lại: ghi {data['skill_sha']}, cây skill trừ tests/ ở HEAD là {actual}"


# Đột biến (SC5): mỗi kiểu hỏng phải bị bắt đúng lý do.
GOOD = {"result": "3/3 GREEN pass; RED 0/3 pass (3 partial)", "model": "claude-sonnet-5-5 (all runs)",
        "date": "2026-10-03", "tier": "T3", "skill_sha": "0" * 40}


def test_good_front_has_no_problem():
    assert problems(GOOD) == []


@pytest.mark.parametrize("key,value", [("result", "pending"), ("result", "Chưa chạy"), ("result", "Not run: no browser"),
                                       ("result", "dự kiến 3/3"), ("model", "PENDING"), ("model", "chưa chạy (đợi)"),
                                       ("result", "(pending)"), ("result", "; chưa chạy"), ("result", "— dự kiến"),
                                       ("result", " — dự kiến"), ("model", "(not run)")])
def test_unrun_state_is_caught(key, value):
    assert any(f"`{key}` ghi chưa chạy" in p for p in problems({**GOOD, key: value}))


@pytest.mark.parametrize("key,value", [("result", "()"), ("model", "; — "), ("result", "(  )")])
def test_value_without_head_is_caught(key, value):
    assert any(f"`{key}` không có trạng thái ở đầu" in p for p in problems({**GOOD, key: value}))


def test_annotation_after_head_is_not_a_state():
    assert problems({**GOOD, "result": "pass 5/6; 1 câu chưa chạy lại vì pending review"}) == []


@pytest.mark.parametrize("bad", ["2026-13-40", "hôm qua", ""])
def test_invalid_date_is_caught(bad):
    assert any("date" in p for p in problems({**GOOD, "date": bad}))


def test_new_file_needs_sha_and_tier_but_old_file_does_not():
    assert any("skill_sha" in p for p in problems({k: v for k, v in GOOD.items() if k != "skill_sha"}))
    assert any("tier" in p for p in problems({k: v for k, v in GOOD.items() if k != "tier"}))
    old = {k: v for k, v in GOOD.items() if k not in ("skill_sha", "tier")}
    assert problems({**old, "date": "2026-10-01"}) == []


def write_skill(repo, kind: str, body: str):
    (repo / "skills" / "x").mkdir(parents=True, exist_ok=True)
    text = "---\nname: x\nmetadata:\n  kind: " + kind + "\n---\n" + body + "\n"
    (repo / "skills" / "x" / "SKILL.md").write_text(text, encoding="utf-8")


def git(repo, *args):
    ident = ["-c", "user.name=t", "-c", "user.email=t@example.com"]
    res = subprocess.run(["git", *ident, *args], cwd=repo, capture_output=True)
    assert res.returncode == 0, res.stderr.decode(errors="replace")


def commit_all(repo, message):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


def git_repo(path, kind: str):
    """Repo git tạm có một skill `x` (SKILL.md + tests/p.md), đã commit."""
    (path / "skills" / "x" / "tests").mkdir(parents=True)
    write_skill(path, kind, "body")
    (path / "skills" / "x" / "tests" / "p.md").write_text("probe v1\n", encoding="utf-8")
    git(path, "init", "-q")
    commit_all(path, "init")
    return path


def test_tree_hash_ignores_only_the_tests_dir(tmp_path):
    repo = git_repo(tmp_path, "discipline")
    first = tree_hash("x", repo)
    assert first is not None and re.fullmatch(r"[0-9a-f]{40}", first)
    (repo / "skills" / "x" / "tests" / "p.md").write_text("probe v2\n", encoding="utf-8")
    commit_all(repo, "edit tests")
    assert tree_hash("x", repo) == first, "đổi tests/ không được đổi băm"
    write_skill(repo, "discipline", "body 2")
    commit_all(repo, "edit skill")
    assert tree_hash("x", repo) != first, "đổi SKILL.md phải đổi băm"


def test_missing_test_file_is_caught_by_kind(tmp_path):
    (tmp_path / "d").mkdir()
    (tmp_path / "r").mkdir()
    discipline, reference = git_repo(tmp_path / "d", "discipline"), git_repo(tmp_path / "r", "reference")
    assert "thiếu tests/pressure.md" in (missing_test_file("x", discipline) or "")
    assert "thiếu tests/retrieval.md" in (missing_test_file("x", reference) or "")
    (discipline / "skills" / "x" / "tests" / "pressure.md").write_text("x", encoding="utf-8")
    (reference / "skills" / "x" / "tests" / "retrieval.md").write_text("x", encoding="utf-8")
    assert missing_test_file("x", discipline) is None
    assert missing_test_file("x", reference) is None


def test_tree_hash_skips_only_when_git_is_missing(monkeypatch):
    def no_git(*a, **k):
        raise FileNotFoundError("git")
    monkeypatch.setattr(subprocess, "run", no_git)
    assert tree_hash("x") is None


def test_tree_hash_fails_loudly_when_git_errors(tmp_path):
    with pytest.raises(pytest.fail.Exception, match="ls-tree.*thoát"):
        tree_hash("x", repo=tmp_path)  # thư mục không phải repo git: git có, nhưng ls-tree mã thoát khác 0
