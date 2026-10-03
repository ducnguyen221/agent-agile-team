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
# Bốn từ gốc của FR11.5 (`not run`, `pending`, `chưa chạy`, `dự kiến`) cộng các từ giữ chỗ hay gặp: `TBD`, `TODO`,
# `N/A`, `none`, `false`, `null` (nguyên từ, để "nonexistent" không bị bắt oan).
NOT_RUN = re.compile(r"not run|pending|chưa chạy|dự kiến|\b(?:tbd|todo|n/a|none|false|null)\b", re.I)
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
    """Phần đầu của một khoá văn tự do (RF67): bỏ khoảng trắng và các dấu mở đầu `(`, `)`, `;`, `—`, `–`, `-`, rồi cắt
    ở `;`, `(` hoặc ` — `, nên chú thích sau đó không bị coi là trạng thái ("claude-sonnet-5-5 (all runs, …)" →
    "claude-sonnet-5-5") còn "(pending)" → "pending)" vẫn bị bắt. Rỗng khi giá trị chỉ có các dấu bị bỏ đó; dấu khác
    (`.`, `?`, `…`, `[]`, `~`…) KHÔNG bị bỏ nên `head()` giữ nguyên chúng — `problems()` bắt riêng bằng phép 'phải bắt đầu
    bằng chữ hoặc số và có ít nhất một chữ'."""
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
        value = data.get(key)
        # `result:` để trống (hoặc `~`, `null`) đọc ra None; `result: false`, `[]`, `{}`, `0` đọc ra bool/list/dict/int:
        # không phải chuỗi trạng thái thì coi là thiếu hoặc sai kiểu, không ép thành chuỗi rồi cho qua.
        if value is None or (isinstance(value, str) and not value.strip()):
            found.append(f"thiếu khoá `{key}`")
        elif not isinstance(value, str):
            found.append(f"`{key}` không phải chuỗi trạng thái: {value!r}")
        elif not re.match(r"[^\W_]", head(value)) or not re.search(r"[^\W\d_]", head(value)):
            # giá trị phải bắt đầu bằng chữ hoặc số và có ít nhất một chữ: bắt ".", "?", "…", "[]", "{}", "~", "0"
            found.append(f"`{key}` không có trạng thái ở đầu: {value!r}")
        elif NOT_RUN.search(head(value)):
            found.append(f"`{key}` ghi chưa chạy: {head(value)!r}")
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
                                       ("result", " — dự kiến"), ("model", "(not run)"),
                                       ("result", "TBD"), ("result", "tbd"), ("result", "TODO"), ("model", "N/A"),
                                       ("result", "n/a"), ("result", "none"), ("result", "None"), ("model", "false"),
                                       ("result", "False"), ("result", "null"), ("model", "NULL"),
                                       ("result", "(none)"), ("result", "None;"), ("result", "none."),
                                       ("result", "TBD; sẽ chạy sau"), ("result", "(TODO)")])
def test_unrun_state_is_caught(key, value):
    assert any(f"`{key}` ghi chưa chạy" in p for p in problems({**GOOD, key: value}))


@pytest.mark.parametrize("key,value", [("result", "()"), ("model", "; — "), ("result", "(  )"),
                                       ("result", "."), ("result", "?"), ("result", "…"), ("result", "..."),
                                       ("model", "*"), ("model", ":"), ("model", "/"), ("result", "[]"),
                                       ("result", "{}"), ("result", "~"), ("model", "0"), ("result", "(.)"),
                                       ("result", "- ."), ("result", "3/3"), ("model", "2026")])
def test_value_without_head_is_caught(key, value):
    """Giá trị giữ chỗ chỉ có dấu câu, hoặc chỉ có số (không chữ nào), không phải trạng thái đã chạy."""
    assert any(f"`{key}` không có trạng thái ở đầu" in p for p in problems({**GOOD, key: value}))


@pytest.mark.parametrize("key", ["result", "model"])
@pytest.mark.parametrize("value", [False, True, 0, 1, [], {}, ["pass"]])
def test_non_string_value_is_caught(key, value):
    assert any(f"`{key}` không phải chuỗi trạng thái" in p for p in problems({**GOOD, key: value}))


def test_annotation_after_head_is_not_a_state():
    assert problems({**GOOD, "result": "pass 5/6; 1 câu chưa chạy lại vì pending review"}) == []


@pytest.mark.parametrize("text", ["---\nresult:\nmodel: m\n---\n", "---\nresult: r\nmodel:\n---\n",
                                  "---\nresult: ~\nmodel: m\n---\n", "---\nresult: r\nmodel: null\n---\n",
                                  "---\nresult: .\nmodel: m\n---\n", "---\nresult: []\nmodel: m\n---\n",
                                  "---\nresult: false\nmodel: m\n---\n", "---\nresult: r\nmodel: …\n---\n",
                                  "---\nresult: (none)\nmodel: m\n---\n", "---\nresult: None;\nmodel: m\n---\n",
                                  "---\nresult: TBD\nmodel: m\n---\n", "---\nresult: r\nmodel: N/A\n---\n",
                                  "---\nresult: r\nmodel: ?\n---\n"])
def test_blank_key_in_frontmatter_is_caught(text):
    """`result:` hay `model:` để trống đọc ra None; None không được lọt thành chuỗi "None" (kẽ hở của RF93)."""
    data = c.parse_frontmatter(text).data
    assert problems({**GOOD, **data}), f"{data!r} lọt máy kiểm"


@pytest.mark.parametrize("key", ["result", "model"])
@pytest.mark.parametrize("value", [None, "", "  ", "None", "null", "TBD", "TODO", "N/A", "false", "(none)", "None;", "."])
def test_empty_or_null_value_is_no_state(key, value):
    assert problems({**GOOD, key: value}), f"{key}={value!r} lọt máy kiểm"


@pytest.mark.parametrize("bad", ["2026-13-40", "hôm qua", ""])
def test_invalid_date_is_caught(bad):
    assert any("date" in p for p in problems({**GOOD, "date": bad}))


def test_new_file_needs_sha_and_tier_but_old_file_does_not():
    assert any("skill_sha" in p for p in problems({k: v for k, v in GOOD.items() if k != "skill_sha"}))
    assert any("tier" in p for p in problems({k: v for k, v in GOOD.items() if k != "tier"}))
    old = {k: v for k, v in GOOD.items() if k not in ("skill_sha", "tier")}
    assert problems({**old, "date": "2026-10-01"}) == []


# Thước chấm truy xuất (SC5, RF120): MỘT định nghĩa cho mọi `skills/*/tests/retrieval.md`, và `result` là số đếm sinh ra
# từ bảng chấm trong chính tệp — không gõ tay, không thước riêng từng tệp.
RETRIEVAL_FILES = [p for p in TEST_FILES if p.name == "retrieval.md"]
RETRIEVAL_IDS = [p.relative_to(REPO).as_posix() for p in RETRIEVAL_FILES]
RETRIEVAL_ROW = re.compile(r"^\| \d+ \|")
RETRIEVAL_RULE = (
    "Cách chấm (một thước cho mọi tệp truy xuất): **Đạt** = trỏ đúng mục và mục đó có nội dung trả lời quyết định chính "
    "của câu (phần phụ còn thiếu ghi trong ngoặc và ở mục cuối); **Một phần** = trỏ đúng nơi nhưng nội dung thiếu cho "
    "quyết định chính; **Không đạt** = trỏ sai hoặc bịa. Ngưỡng PLAN TK11: tỉ lệ câu tình huống Đạt ≥ 4/5 (80 %) và câu "
    "ranh giới Đạt; câu ranh giới tính riêng. `result` ghi số Đạt hẳn (`strict`) và số Một phần; `points-right` là Đạt + "
    "Một phần, tức số câu trỏ đúng nơi."
)


def retrieval_result(text: str) -> str:
    """`result` chuẩn của một tệp truy xuất, đếm từ bảng chấm của nó. Lỗi (ValueError) nếu bảng không đọc được."""
    grades = {"pass": 0, "partial": 0, "fail": 0}
    situations = pass_situations = boundary = pass_boundary = 0
    for line in text.splitlines():
        if not RETRIEVAL_ROW.match(line):
            continue
        cells = [x.strip() for x in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) != 5:
            raise ValueError(f"hàng bảng không đủ 5 cột: {line[:60]!r}")
        verdict, is_boundary = cells[4], cells[2].startswith("mục khác:")
        if verdict.startswith("Đạt") and re.search(r"một\s*phần", verdict, re.I):
            # mọi cách viết "Đạt … một phần" (`Đạt (một phần`, `Đạt một phần`, `Đạt/Một phần`, `Đạt — một phần`…) đều mơ hồ
            raise ValueError(f"ô `Đạt … một phần` mơ hồ, ghi Đạt hoặc Một phần: {verdict[:40]!r}")
        kind = ("fail" if verdict.startswith("Không đạt") else "partial" if verdict.startswith("Một phần")
                else "pass" if verdict.startswith("Đạt") else None)
        if kind is None:
            raise ValueError(f"ô kết quả không bắt đầu bằng Đạt / Một phần / Không đạt: {verdict[:40]!r}")
        grades[kind] += 1
        if is_boundary:
            boundary += 1
            pass_boundary += kind == "pass"
        else:
            situations += 1
            pass_situations += kind == "pass"
    if boundary != 1 or situations < 1:
        raise ValueError(f"cần đúng 1 câu ranh giới và ≥1 câu tình huống, thấy {boundary} và {situations}")
    total = situations + boundary
    ok = pass_situations * 5 >= situations * 4 and pass_boundary == 1
    return (f"strict {grades['pass']}/{total} (+{grades['partial']} partial, {grades['fail']} fail) — "
            f"{'at' if ok else 'below'} threshold (ngưỡng PLAN TK11: ≥4/5 câu tình huống Đạt + câu ranh giới Đạt); "
            f"points-right {grades['pass'] + grades['partial']}/{total}")


@pytest.mark.parametrize("path", RETRIEVAL_FILES, ids=RETRIEVAL_IDS)
def test_retrieval_file_uses_the_shared_rule(path):
    text = c.read_text(path)
    assert RETRIEVAL_RULE in text, "tệp không dùng định nghĩa chấm chung (RETRIEVAL_RULE)"
    assert "Ngưỡng tính Đạt + Một phần" not in text, "còn thước chấm cũ"


@pytest.mark.parametrize("path", RETRIEVAL_FILES, ids=RETRIEVAL_IDS)
def test_retrieval_result_is_computed_from_its_table(path):
    assert str(front(path)["result"]) == retrieval_result(c.read_text(path))


README_ROW = re.compile(r"^\| \[(?P<skill>[a-z-]+)\]\([^)]*\) \| [^|]+ \| `(?P<file>[a-z]+\.md)` \| (?P<result>.*) \| (?P<date>[0-9-]+) \|$")


def readme_status_rows():
    """Các hàng của bảng 'Hiện trạng thử' ở `skills/README.md` mục 4: {skill: (tệp, result, date)}."""
    text = c.read_text(REPO / "skills" / "README.md")
    section = text.split("## 4. Hiện trạng thử", 1)[1]
    rows = {}
    for line in section.splitlines():
        m = README_ROW.match(line)
        if m:
            rows[m["skill"]] = (m["file"], m["result"], m["date"])
    return rows


def lead(text) -> str:
    """Đoạn đầu của `result` kỷ luật: đến dấu `,`, `;` hay ` (` đầu tiên (ví dụ "3/3 GREEN pass")."""
    return re.split(r",| \(|;", str(text), maxsplit=1)[0].strip()


def discipline_cell_gap(shown: str, result) -> str | None:
    """Ô `result` ở bảng README cho tệp kỷ luật phải có đoạn đầu BẰNG đoạn đầu của `result` ở frontmatter (không chỉ là
    tiền tố của nó: `3/3` hay `3/3 GREEN pass` không khớp `3/3 GREEN passed partially`). Trả lỗi hoặc None."""
    if lead(shown) != lead(result):
        return f"ô result `{shown}` có đoạn đầu {lead(shown)!r}, frontmatter có {lead(result)!r}"
    return None


def retrieval_cell(result: str) -> str:
    """Ô `result` ở bảng README cho một tệp truy xuất, rút từ `result` ở frontmatter."""
    m = re.fullmatch(r"strict (\S+) \(\+(\d+) partial, (\d+) fail\) — (at|below) threshold \(.*\); points-right (\S+)", result)
    assert m, f"result không theo khuôn truy xuất: {result!r}"
    return f"strict {m[1]} (+{m[2]} partial, {m[3]} fail), {m[4]} threshold; points-right {m[5]}"


def test_readme_status_table_matches_the_test_files():
    """Bảng 'Hiện trạng thử' (README mục 4) đọc từ frontmatter: mỗi skill một hàng, `date` khớp, ô truy xuất khớp số thật."""
    rows = readme_status_rows()
    assert sorted(rows) == SKILLS, "bảng thiếu hoặc thừa hàng so với skills/*/SKILL.md"
    for path in TEST_FILES:
        skill = path.parent.parent.name
        name, shown, day = rows[skill]
        data = front(path)
        assert name == path.name, f"{skill}: tệp thử ghi {name}, thực tế {path.name}"
        assert day == str(data["date"]), f"{skill}: date bảng {day}, frontmatter {data['date']}"
        if path.name == "retrieval.md":
            assert shown == retrieval_cell(str(data["result"])), f"{skill}: ô result lệch frontmatter"
        else:
            gap = discipline_cell_gap(shown, data["result"])
            assert gap is None, f"{skill}: {gap}"


@pytest.mark.parametrize("shown,result", [("3/3 GREEN pass", "3/3 GREEN pass, no refactor; RED 1/3 passed"),
                                           ("3/3 GREEN pass after 1 REFACTOR round", "3/3 GREEN pass after 1 REFACTOR round (scenario 3), x"),
                                           ("discriminating scenarios RED 0/2 pass (2 partial); GREEN wq-1 partial",
                                            "discriminating scenarios RED 0/2 pass (2 partial); GREEN wq-1 partial (regraded)"),
                                           ("3/3 GREEN pass", "3/3 GREEN pass")])
def test_discipline_cell_matching_lead_is_accepted(shown, result):
    assert discipline_cell_gap(shown, result) is None


@pytest.mark.parametrize("shown,result", [("3/3", "3/3 GREEN partial, no refactor"),
                                          ("3/3 GREEN pass", "3/3 GREEN passed partially"),
                                          ("3/3 GREEN", "3/3 GREEN pass"),
                                          ("3/3 GREEN pass", "3/3 GREEN pass after 1 REFACTOR round"),
                                          ("2/3 GREEN pass", "3/3 GREEN pass")])
def test_discipline_cell_with_loose_prefix_is_caught(shown, result):
    """Ô README lệch frontmatter mà chỉ là tiền tố của nó vẫn phải đỏ (RF128, lỗ hổng so tiền tố)."""
    assert discipline_cell_gap(shown, result) is not None


def test_retrieval_cell_follows_the_computed_result():
    sample = retrieval_result(_table("Đạt", "Đạt", "Đạt", "Đạt", "Một phần (thiếu)"))
    assert retrieval_cell(sample) == "strict 5/6 (+1 partial, 0 fail), at threshold; points-right 6/6"


REPLACEMENT = "ngoài các file nêu ở dòng trên"


def contradiction_gaps(scenarios: str, pressure: str) -> list:
    """Kịch bản nói 'KHÔNG đọc file nào trên máy' mà dòng GREEN bảo đọc `SKILL.md` thì công thức chạy lại phải ghi phép
    thay vế mở đầu ở lượt GREEN, cả ở `scenarios.txt` (đầu tệp, trước kịch bản đầu) lẫn mục 'Chạy lại' của `pressure.md`;
    thiếu thì chạy lại theo công thức sẽ tái tạo mâu thuẫn (RF121)."""
    if "KHÔNG đọc file nào trên máy" not in scenarios:
        return []
    gaps = []
    if REPLACEMENT not in scenarios.split("\n=== ", 1)[0]:
        gaps.append("phần đầu scenarios.txt thiếu phép thay vế mở đầu ở lượt GREEN")
    # Chỉ đọc đúng mục `## Chạy lại` (đến tiêu đề `## ` kế): mất hay đổi tên tiêu đề thì đỏ, không lấy cả tệp rồi
    # tình cờ khớp cụm ở mục lịch sử (RF132).
    section = re.search(r"^## Chạy lại[ \t]*$(.*?)(?=^## |\Z)", pressure, re.M | re.S)
    if section is None:
        gaps.append("pressure.md thiếu tiêu đề mục '## Chạy lại'")
    elif REPLACEMENT not in section.group(1):
        gaps.append("mục 'Chạy lại' của pressure.md thiếu phép thay vế mở đầu ở lượt GREEN")
    return gaps


@pytest.mark.parametrize("skill", sorted(p.parent.parent.name for p in REPO.glob("skills/*/tests/scenarios.txt")))
def test_rerun_recipe_states_the_green_opening_clause(skill):
    base = REPO / "skills" / skill / "tests"
    assert contradiction_gaps(c.read_text(base / "scenarios.txt"), c.read_text(base / "pressure.md")) == []


def test_contradiction_gaps_are_caught():
    scen = "đầu\n\n=== KB1 ===\nKHÔNG đọc file nào trên máy\n"
    assert len(contradiction_gaps(scen, "x\n## Chạy lại\ny")) == 2
    ok_scen = f"đầu {REPLACEMENT}\n\n=== KB1 ===\nKHÔNG đọc file nào trên máy\n"
    assert contradiction_gaps(ok_scen, "x\n## Chạy lại\ny") == ["mục 'Chạy lại' của pressure.md thiếu phép thay vế mở đầu ở lượt GREEN"]
    assert contradiction_gaps(ok_scen, f"x\n## Chạy lại\n{REPLACEMENT}") == []
    assert contradiction_gaps("không có vế cấm", "x") == []


def test_rerun_recipe_check_needs_the_rerun_heading():
    """RF132: cụm thay vế có ở mục lịch sử nhưng mục `## Chạy lại` mất hay đổi tên → phải đỏ (trước đây vẫn xanh)."""
    scen = f"đầu {REPLACEMENT}\n\n=== KB1 ===\nKHÔNG đọc file nào trên máy\n"
    history = f"## GREEN chạy lại lần 3\n{REPLACEMENT}\n"
    assert contradiction_gaps(scen, history) == ["pressure.md thiếu tiêu đề mục '## Chạy lại'"]
    assert contradiction_gaps(scen, history + "## Chạy lại sau\n" + REPLACEMENT) == \
        ["pressure.md thiếu tiêu đề mục '## Chạy lại'"]
    assert contradiction_gaps(scen, history + "## Chạy lại\nx\n") == \
        ["mục 'Chạy lại' của pressure.md thiếu phép thay vế mở đầu ở lượt GREEN"]
    # cụm nằm ở mục đứng SAU `## Chạy lại` không tính cho mục đó
    assert contradiction_gaps(scen, f"## Chạy lại\nx\n## Phụ lục\n{REPLACEMENT}\n") == \
        ["mục 'Chạy lại' của pressure.md thiếu phép thay vế mở đầu ở lượt GREEN"]
    assert contradiction_gaps(scen, history + f"## Chạy lại\n{REPLACEMENT}\n## Phụ lục\ny") == []


def _row(n, expected, verdict):
    return f"| {n} | câu hỏi | {expected} | trỏ | {verdict} |"


def _table(*verdicts, boundary="Đạt"):
    rows = [_row(i, "`SKILL.md` › 1", v) for i, v in enumerate(verdicts, 1)]
    rows.append(_row(len(verdicts) + 1, "mục khác: skill `x`", boundary))
    return "\n".join(["| # | Câu hỏi | Mục kỳ vọng | Mục agent trỏ | Kết quả |", "|---|---|---|---|---|", *rows])


def test_retrieval_result_counts_strictly_and_judges_threshold():
    strict = retrieval_result(_table("Đạt", "Đạt", "Đạt", "Đạt", "Một phần (thiếu)"))
    assert strict.startswith("strict 5/6 (+1 partial, 0 fail) — at threshold") and strict.endswith("points-right 6/6")
    assert "below threshold" in retrieval_result(_table("Đạt", "Đạt", "Đạt", "Một phần", "Một phần"))
    assert "below threshold" in retrieval_result(_table("Đạt", "Đạt", "Đạt", "Đạt", "Đạt", boundary="Một phần (thay thế)"))
    assert "(+0 partial, 1 fail)" in retrieval_result(_table("Đạt", "Đạt", "Đạt", "Đạt", "Không đạt"))


def test_retrieval_result_rejects_ambiguous_or_unreadable_tables():
    with pytest.raises(ValueError, match="mơ hồ"):
        retrieval_result(_table("Đạt (một phần: thiếu mẫu)", "Đạt"))
    for ambiguous in ("Đạt một phần", "Đạt (Một phần: thiếu mẫu)", "Đạt/Một phần", "Đạt — một phần", "Đạt  (một phần",
                      "Đạt (một  phần", "Đạt, Một Phần"):
        with pytest.raises(ValueError, match="mơ hồ"):
            retrieval_result(_table(ambiguous, "Đạt"))
    retrieval_result(_table("Đạt (kèm phần phụ thiếu mẫu)", "Đạt"))  # Đạt kèm chú thích không có "một phần": không oan
    with pytest.raises(ValueError, match="bắt đầu bằng"):
        retrieval_result(_table("Pass", "Đạt"))
    with pytest.raises(ValueError, match="1 câu ranh giới"):
        retrieval_result(_table("Đạt").replace("mục khác:", "mục:"))


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
