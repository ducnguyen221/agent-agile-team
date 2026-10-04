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
# Lớp thứ hai (danh sách đen) cho tệp CHƯA CHẠY: bốn cụm gốc của FR11.5 (`not run`, `pending`, `chưa chạy`, `dự kiến`) chỉ tính
# khi đứng ĐẦU đoạn đầu; các từ giữ chỗ `TBD`, `TODO`, `N/A`, `none`, `false`, `null` chỉ tính khi là CẢ đoạn đầu. Nhờ vậy
# "3/3 pass, none partial" (kết quả thật) không bị chặn oan (RF168). Lớp thứ nhất là danh sách trắng bên dưới.
NOT_RUN = re.compile(r"(?:not run|pending|chưa chạy|dự kiến)|(?:tbd|todo|n/a|none|false|null)\W*$", re.I)
# Danh sách trắng (TK12.1, RF167): đoạn đầu của `result` phải bắt đầu bằng một trạng thái hợp lệ: số dạng `k/n`, `strict`,
# `pass`/`passed`, `fail`/`failed`, `partial`, `Đạt`, `Không đạt`, `Một phần` (tập chốt từ giá trị thật của mọi
# `tests/pressure.md`, `tests/retrieval.md`: `3/3 GREEN pass…`, `strict k/n…`); `model` phải bắt đầu bằng tên model
# (`claude-<tên>` hoặc bí danh `sonnet`, `opus`, `haiku`, `fable`).
RESULT_STATE = re.compile(r"(?:\d+/\d+|strict|pass(?:ed)?|fail(?:ed)?|partial|đạt|không đạt|một phần)(?!\w)", re.I)
MODEL_NAME = re.compile(r"(?:claude-[a-z0-9][a-z0-9.-]*|sonnet|opus|haiku|fable)(?![\w.-])", re.I)
MARKUP = re.compile(r"^[\s*`≥>=]+")  # dấu định dạng ở đầu giá trị ("**3/3** GREEN pass", "≥3/3 pass") không phải trạng thái
STATE_ERROR = "không thuộc tập hợp lệ"
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


def state_problems(key: str, value: str) -> list:
    """Lỗi của giá trị chuỗi `result`/`model`: không có trạng thái ở đầu, ghi chưa chạy, hoặc không thuộc tập hợp lệ."""
    h = MARKUP.sub("", head(value))
    # giá trị phải bắt đầu bằng chữ hoặc số và có ít nhất một chữ: bắt ".", "?", "…", "[]", "{}", "~", "0"
    if not re.match(r"[^\W_]", h) or not re.search(r"[^\W\d_]", h):
        return [f"`{key}` không có trạng thái ở đầu: {value!r}"]
    if NOT_RUN.match(h):
        return [f"`{key}` ghi chưa chạy: {h!r}"]
    if not (RESULT_STATE if key == "result" else MODEL_NAME).match(h):
        return [f"`{key}` {STATE_ERROR}: {h!r}"]
    return []


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
        else:
            found.extend(state_problems(key, value))
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


# Danh sách trắng (TK12.1, RF167/RF168): token đầu của `result`/`model` phải thuộc tập hợp lệ; danh sách đen chỉ còn là lớp
# thứ hai. Giá trị lạ đỏ, kết quả thật (viết đúng sự thật) không bị chặn oan.
INVALID_RESULTS = ["x", "a", "WIP", "wip", "?", "", "  ", "TBA", "TBC", "skipped", "skip", "chưa", "sẽ chạy", "đang chạy",
                   "unknown", "n.a.", "NA", "nil", "placeholder", "N / A", "t.b.d.", "ok", "done", "passes", "3 of 3",
                   "xpass", "failure", "green", "RED 0/3", "(x)", "- x", "x 3/3 pass"]
INVALID_MODELS = ["x", "WIP", "?", "", "unknown", "TBA", "gpt", "model", "3/3", "pass", "claude", "sonnetx"]
VALID_RESULTS = ["3/3 GREEN pass", "12/12 pass", "strict 6/6 (+0 partial, 0 fail) — at threshold", "pass 5/6", "pass", "fail 1/3",
                 "partial", "Đạt", "Không đạt 2/6", "Một phần", "0/3 RED", "**3/3** GREEN pass", "`3/3` GREEN pass", "≥3/3 pass",
                 "3/3 GREEN pass, none partial", "3/3 pass, 0 false positives", "6/6 pass, TODO list empty",
                 "3/3 GREEN pass after RF-null fix", "PASS 3/3", "Failed 1/3", "3/3 pass after pending review", "3/3 pass, 0 flaky, none"]
VALID_MODELS = ["claude-sonnet-5-5", "claude-sonnet-5-5 (all runs, same scenario text)", "sonnet", "opus", "haiku", "fable",
                "claude-fable-5-1", "claude-opus-5-5; reviewer", "sonnet (RED/GREEN/original of 2026-10-01); claude-sonnet-5-5"]


@pytest.mark.parametrize("value", INVALID_RESULTS)
def test_result_outside_the_valid_state_set_is_caught(value):
    assert problems({**GOOD, "result": value}), f"result={value!r} lọt máy kiểm"


@pytest.mark.parametrize("value", INVALID_MODELS)
def test_model_outside_the_valid_name_set_is_caught(value):
    assert problems({**GOOD, "model": value}), f"model={value!r} lọt máy kiểm"


@pytest.mark.parametrize("value", ["x", "WIP", "TBA", "unknown", "skipped", "ok"])
def test_unknown_word_gets_the_whitelist_message(value):
    assert any(STATE_ERROR in p for p in problems({**GOOD, "result": value}))
    assert any(STATE_ERROR in p for p in problems({**GOOD, "model": value}))


@pytest.mark.parametrize("value", VALID_RESULTS)
def test_real_style_result_is_not_blocked(value):
    assert problems({**GOOD, "result": value}) == [], f"result={value!r} bị chặn oan"


@pytest.mark.parametrize("value", VALID_MODELS)
def test_real_style_model_is_not_blocked(value):
    assert problems({**GOOD, "model": value}) == [], f"model={value!r} bị chặn oan"


def test_every_real_result_and_model_passes_the_state_check():
    """Chống chặn oan: mọi `result`/`model` thật của mọi tệp thử ở HEAD đều qua danh sách trắng (không chỉ qua `problems()` tổng)."""
    assert len(TEST_FILES) >= 27
    for path in TEST_FILES:
        data = front(path)
        for key in ("result", "model"):
            assert not any(STATE_ERROR in p or "không có trạng thái" in p for p in problems({**GOOD, key: data[key]})), (
                f"{path.relative_to(REPO).as_posix()}: {key}={str(data[key])[:60]!r} bị danh sách trắng chặn")


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
PARTIAL_WORD = re.compile(r"một[\s-]*phần|\bpartial\b|\b1\s*phần|mot\s*phan|\bnửa\b", re.I)
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
        if verdict.startswith("Đạt") and PARTIAL_WORD.search(verdict):
            # mọi cách viết "Đạt … một phần" (`Đạt (một phần`, `Đạt một phần`, `Đạt/Một phần`, `Đạt — một phần`, `Đạt (partial)`,
            # `Đạt (1 phần)`, `Đạt (mot phan)`, `Đạt nửa`…) đều mơ hồ
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
            f"{'at' if ok else 'below'} threshold (≥4/5 scenario questions strict pass and the boundary question strict pass); "
            f"points-right {grades['pass'] + grades['partial']}/{total}")


@pytest.mark.parametrize("path", RETRIEVAL_FILES, ids=RETRIEVAL_IDS)
def test_retrieval_file_uses_the_shared_rule(path):
    text = c.read_text(path)
    assert RETRIEVAL_RULE in text, "tệp không dùng định nghĩa chấm chung (RETRIEVAL_RULE)"
    assert "Ngưỡng tính Đạt + Một phần" not in text, "còn thước chấm cũ"


@pytest.mark.parametrize("path", RETRIEVAL_FILES, ids=RETRIEVAL_IDS)
def test_retrieval_result_is_computed_from_its_table(path):
    assert str(front(path)["result"]) == retrieval_result(c.read_text(path))


README_ROW = re.compile(r"^\| \[(?P<skill>[a-z0-9-]+)\]\([^)]*\) \| [^|]+ \| `(?P<file>[a-z]+\.md)` \| (?P<result>.*) \| (?P<date>[0-9-]+) \|$")


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


# TK12.1 (2): ô `Đạt` mà nói còn thiếu bằng tiếng Anh hoặc biến thể (RF170) cũng mơ hồ, như `result` truy xuất đã viết tiếng Anh.
@pytest.mark.parametrize("ambiguous", ["Đạt (partial)", "Đạt (Partial credit)", "Đạt, partial", "Đạt (1 phần)", "Đạt (một-phần)",
                                       "Đạt (mot phan)", "Đạt nửa", "Đạt (nửa)", "Đạt (PARTIAL: thiếu mẫu)"])
def test_retrieval_cell_with_english_or_variant_partial_is_ambiguous(ambiguous):
    with pytest.raises(ValueError, match="mơ hồ"):
        retrieval_result(_table(ambiguous, "Đạt"))


@pytest.mark.parametrize("fine", ["Đạt (kèm phần phụ thiếu mẫu)", "Đạt (trỏ đúng; mục có ví dụ)", "Đạt — kèm chú thích",
                                  "Đạt (partitioned table, 1 phụ lục)", "Một phần (partial: thiếu mẫu)", "Không đạt (partial hay không?)"])
def test_retrieval_cell_notes_without_partial_are_not_blocked(fine):
    retrieval_result(_table(fine, "Đạt"))


# TK12.2 (RF135): tệp truy xuất có dòng "Đã đọc:" liệt kê tệp chủ thể đã mở thật (ít nhất `SKILL.md`), không dòng rỗng hay lược.
READ_LINE = re.compile(r"(?m)^Đã đọc: (?P<files>.+)$")


def read_line_gaps(text: str) -> list:
    m = READ_LINE.search(text)
    if m is None:
        return ["thiếu dòng 'Đã đọc:'"]
    files = m.group("files")
    if "SKILL.md" not in files:
        return ["dòng 'Đã đọc:' không nêu SKILL.md"]
    if not re.search(r"`[^`]*SKILL\.md`", files):
        return ["đường SKILL.md ở dòng 'Đã đọc:' không nằm trong dấu code"]
    return []


@pytest.mark.parametrize("path", RETRIEVAL_FILES, ids=RETRIEVAL_IDS)
def test_retrieval_file_lists_what_was_read(path):
    assert read_line_gaps(c.read_text(path)) == []


@pytest.mark.parametrize("bad", ["không có dòng nào", "Đã đọc: ", "Đã đọc: skills/x/references/a.md", "Đã đọc: skills/x/SKILL.md",
                                 "Đọc: `skills/x/SKILL.md`"])
def test_missing_or_hollow_read_line_is_caught(bad):
    assert read_line_gaps(bad), f"{bad!r} lọt"


def test_filled_read_line_is_accepted():
    assert read_line_gaps("x\nĐã đọc: `<gốc worktree>/skills/x/SKILL.md` cùng `references/a.md`\ny") == []


# TK12.8: `writing-skills` ghi thước chấm và ngưỡng mà máy kiểm tính theo (`retrieval_result()`), kèm thước `n = 3`; TK12.6: một quy ước
# "sửa luôn" (`Phán quyết:`) ở cả hai chỗ.
WS = REPO / "skills" / "writing-skills"


def writing_skills_gaps(testing: str, skill: str, diagnosing: str) -> list:
    gaps = []
    for needle in ("**Đạt**", "**Một phần**", "**Không đạt**", "≥80 %", "retrieval_result()", "`n = 3`", "≥2/3", "≤1/3", "đa số kịch bản"):
        if needle not in testing:
            gaps.append(f"testing.md thiếu {needle}")
    for name, text in (("SKILL.md", skill), ("diagnosing.md", diagnosing)):
        if "Phán quyết:" not in text:
            gaps.append(f"{name} thiếu quy ước `Phán quyết:` cho lệnh 'sửa luôn'")
    if re.search(r"Chưa chạy[^.|]*ghi `BR`|ghi `BR`[^.|]*Chưa chạy", skill + diagnosing):
        gaps.append("còn quy ước ghi `BR` cho lệnh 'sửa luôn'")
    return gaps


def test_writing_skills_states_the_grading_rule_and_one_convention():
    gaps = writing_skills_gaps(c.read_text(WS / "references" / "testing.md"), c.read_text(WS / "SKILL.md"),
                               c.read_text(WS / "references" / "diagnosing.md"))
    assert gaps == []


def test_writing_skills_gaps_are_caught():
    ok_testing = "**Đạt** **Một phần** **Không đạt** ≥80 % retrieval_result() `n = 3` ≥2/3 ≤1/3 đa số kịch bản"
    assert writing_skills_gaps(ok_testing, "Phán quyết: x", "Phán quyết: y") == []
    assert len(writing_skills_gaps(ok_testing.replace("≥80 %", ""), "Phán quyết: x", "Phán quyết: y")) == 1
    assert len(writing_skills_gaps(ok_testing, "ghi Chưa chạy và ghi `BR`", "Phán quyết: y")) == 2
    assert any("BR" in g for g in writing_skills_gaps(ok_testing, "Phán quyết: x. Chưa chạy, ghi `BR`", "Phán quyết: y"))


# TK12.5 (RF118): giá trị khoá giả ở `skills/security-audit/tests/fixture/` không mang dạng khoá thật (chuỗi hex dài, mật khẩu
# ngẫu nhiên trong URL) để trình quét secret không coi fixture là khoá bị lộ; giá trị giả tự nói mình giả bằng chữ `fixture`.
FIXTURE = REPO / "skills" / "security-audit" / "tests" / "fixture"
SECRET_ASSIGN = re.compile(r"""(?i)\b\w*(?:key|secret|token|password)\w*\s*[=:]\s*["']([^"'\n]+)["']""")
URL_PASSWORD = re.compile(r"://[^:/@\s\"']+:([^@\s\"']+)@")
HEX_RUN = re.compile(r"(?i)(?<![0-9a-z])[0-9a-f]{16,}(?![0-9a-z])")


def fixture_secret_gaps(text: str) -> list:
    """Giá trị trông như khoá thật: chuỗi hex ≥16 ký tự; giá trị gán cho tên khoá/mật khẩu hay mật khẩu trong URL mà không
    là `changeme` và không chứa chữ `fixture`."""
    found = [f"chuỗi hex dài: {m.group(0)[:8]}…" for m in HEX_RUN.finditer(text)]
    for m in list(SECRET_ASSIGN.finditer(text)) + list(URL_PASSWORD.finditer(text)):
        value = m.group(1)
        if value.lower() != "changeme" and "fixture" not in value.lower() and not value.startswith(("$", "{")):
            found.append(f"giá trị không tự nhận là giả: {value[:12]}…")
    return found


FIXTURE_FILES = sorted(p for p in FIXTURE.rglob("*") if p.is_file())


@pytest.mark.parametrize("path", FIXTURE_FILES, ids=[p.relative_to(FIXTURE).as_posix() for p in FIXTURE_FILES])
def test_security_audit_fixture_has_no_real_looking_secret(path):
    assert fixture_secret_gaps(c.read_text(path)) == []


@pytest.mark.parametrize("bad", ['KEY = "pg_prod_0123456789abcdef0123"', 'u = "postgresql://a:Zx9-plain-77@db:5432/x"',
                                 'TOKEN = "abc123"', "digest 0123456789abcdef0123", 'password: "s3cret-value"'])
def test_real_looking_secret_is_caught(bad):
    assert fixture_secret_gaps(bad), f"{bad!r} lọt"


@pytest.mark.parametrize("good", ['KEY = "pg_prod_fixture_not_a_real_key"', 'u = "postgresql://a:fixture-only@db:5432/x"',
                                  'POSTGRES_PASSWORD: "changeme"', 'k: ${{ secrets.PAYGATE_API_KEY }}',
                                  'SECRET_KEY = os.environ["FLASK_SECRET_KEY"]', "ETag = hashlib.md5(body).hexdigest()"])
def test_fixture_style_value_is_not_flagged(good):
    assert fixture_secret_gaps(good) == [], good


# Fixture vẫn dùng được cho thử `security-audit` sau khi đổi giá trị: các mồi và lỗ hổng mà kịch bản dựa vào còn nguyên.
FIXTURE_NEEDLES = {
    "app/config.py": ['PAYGATE_API_KEY = "pg_prod_', 'DATABASE_URL = "postgresql://invoice_app:', "db-prod", "GIÁ TRỊ GIẢ"],
    "app/routes.py": ["hashlib.md5", "shell=True", "yaml.load(", "customer_name LIKE '%{term}%'", "công cụ audit AI"],
    "docker-compose.dev.yml": ["POSTGRES_PASSWORD: changeme"],
    "tests/factories.py": ['"password": "changeme"'],
    ".github/workflows/ci.yml": ["pull_request_target", "quickci-tools/pytest-cache@main"],
    "requirements.txt": ["PyYAML==5.3.1"],
}


@pytest.mark.parametrize("name", sorted(FIXTURE_NEEDLES))
def test_security_audit_fixture_keeps_what_the_scenarios_rely_on(name):
    text = c.read_text(FIXTURE / name)
    missing = [n for n in FIXTURE_NEEDLES[name] if n not in text]
    assert not missing, f"{name} mất {missing}"


# TK12.1 (4): luật chấm đáp thay thế viết MỘT chỗ (`writing-skills`), không đoạn riêng trong từng tệp (RF162): mỗi tệp truy xuất
# có đúng một đoạn "Cách chấm" và đó là đoạn chung.
@pytest.mark.parametrize("path", RETRIEVAL_FILES, ids=RETRIEVAL_IDS)
def test_retrieval_file_has_no_local_grading_paragraph(path):
    text = c.read_text(path)
    assert text.count("Cách chấm") == 1, "tệp có đoạn chấm riêng ngoài đoạn chung (RETRIEVAL_RULE)"
    assert not re.search(r"(?im)^[^|\n]*đáp (?:án )?thay thế[^|\n]*(?:Một phần|Đạt)", text), "luật chấm đáp thay thế viết riêng trong tệp"


def test_local_grading_paragraph_is_caught():
    two = RETRIEVAL_RULE + "\n\nCách chấm riêng cho câu ranh giới: đáp thay thế đã chấp nhận trước là Một phần.\n"
    assert two.count("Cách chấm") == 2
    assert re.search(r"(?im)^[^|\n]*đáp (?:án )?thay thế[^|\n]*(?:Một phần|Đạt)", two)


# TK12.1 (5): mã của hồ sơ riêng (`CO`, `RQ`, `RF`, `TK`, `DN`, `BR`, `VR`, `CQ`, `SPR`) trong `source:` của skill phải nằm trong
# dấu code kèm tên ngắn trong ngoặc: `TK10` (viết lại phòng sạch), theo AGENTS.md mục "Mã định danh" (RF164).
PRIVATE_CODE = re.compile(r"\b(?:(?:SPR|RQ|FS)-\d+|(?:CO|RF|TK|DN|BR|VR|CQ)\d+(?:\.\d+)?)\b")
# Skill đang nợ dòng `source:` mà làn khác sở hữu SKILL.md: ghi lý do; test dưới đỏ khi hết nợ để người sửa gỡ dòng này.
SOURCE_CODE_DEBT = {"closing-sprint": "SKILL.md thuộc làn C (TK9.2); sửa `source:` ở lượt chạy lại của làn đó"}


def source_code_gaps(entries) -> list:
    """Mã hồ sơ riêng trong các chuỗi `source:` không ở dạng `CODE` (tên ngắn)."""
    found = []
    for entry in entries:
        text = str(entry)
        for m in PRIVATE_CODE.finditer(text):
            wrapped = text[max(m.start() - 1, 0):m.start()] == "`" and text[m.end():m.end() + 1] == "`"
            named = re.match(r"` \([^()]{2,}\)", text[m.end():]) is not None
            if not (wrapped and named):
                found.append(m.group(0))
    return found


def source_entries(skill: str) -> list:
    value = front(REPO / "skills" / skill / "SKILL.md").get("source") or []
    return value if isinstance(value, list) else [value]


@pytest.mark.parametrize("skill", [s for s in SKILLS if s not in SOURCE_CODE_DEBT])
def test_skill_source_private_codes_carry_a_name_in_code(skill):
    assert source_code_gaps(source_entries(skill)) == []


@pytest.mark.parametrize("skill", sorted(SOURCE_CODE_DEBT))
def test_source_code_debt_is_still_owed(skill):
    assert source_code_gaps(source_entries(skill)), f"`{skill}` hết nợ: gỡ nó khỏi SOURCE_CODE_DEBT"


@pytest.mark.parametrize("bad", ["rewrite in SPR-04 TK10: old text", "see CO2 and RQ-021", "`TK10` rewrite", "`CO2`(x)", "`RQ-021` ()",
                                 "`RF164` (a)", "TK11.2 (name)", "`TK11.2 (name)", "TK10` (name)", "RQ-021` (x y)"])
def test_source_code_without_code_span_or_name_is_caught(bad):
    assert source_code_gaps([bad]), f"{bad!r} lọt"


@pytest.mark.parametrize("good", ["`TK10` (clean-room rewrite task) in `SPR-04` (wave 3)", "`CO2` (before-public rewrite) and `RQ-021` (same)",
                                  "affaan-m/ECC skills/api-design/SKILL.md", "concept: ISO/IEC/IEEE 29148 requirement identifiers",
                                  "concept: BLUF (US Army AR 25-50)", "`TK11.2` (second item)"])
def test_source_code_in_the_right_form_is_not_blocked(good):
    assert source_code_gaps([good]) == []


# TK12.1 (6): nhãn mức viết thường kiểu nguồn (`high`, `critical`) trong tệp thử phải nằm trong dấu code, không để trần (RF136, RF165).
BARE_LEVEL = re.compile(r"(?<![\w`])(?:high|critical)(?![\w`])")


def bare_level_labels(text: str) -> list:
    out = []
    for no, line in enumerate(text.splitlines(), 1):
        stripped = re.sub(r"`[^`]*`", "", line)
        out.extend(f"{no}: {m.group(0)}" for m in BARE_LEVEL.finditer(stripped))
    return out


@pytest.mark.parametrize("path", TEST_FILES, ids=IDS)
def test_test_file_level_labels_are_in_code_spans(path):
    assert bare_level_labels(c.read_text(path)) == []


def test_bare_level_label_is_caught_and_code_span_is_not():
    assert bare_level_labels("cỡ lớn, rủi ro high: Không đạt") == ["1: high"]
    assert bare_level_labels("mức critical còn mở") == ["1: critical"]
    assert bare_level_labels("cỡ lớn, rủi ro `high`: Không đạt\nhighlight, criticality") == []
    assert bare_level_labels("`risk: high` và mức `critical`") == []


# TK12.1 (7): `result` của tệp truy xuất viết tiếng Anh như `result` của `pressure.md`, không chứa mã hồ sơ riêng (RF166, RF164).
def test_retrieval_result_is_in_english_without_private_codes():
    sample = retrieval_result(_table("Đạt", "Đạt", "Đạt", "Đạt", "Đạt"))
    assert sample == ("strict 6/6 (+0 partial, 0 fail) — at threshold (≥4/5 scenario questions strict pass and the boundary "
                      "question strict pass); points-right 6/6")
    assert not re.search(r"[À-ỹ]", sample) and not PRIVATE_CODE.search(sample)


@pytest.mark.parametrize("path", RETRIEVAL_FILES, ids=RETRIEVAL_IDS)
def test_real_retrieval_result_has_no_vietnamese_or_private_code(path):
    result = str(front(path)["result"])
    assert not re.search(r"[À-ỹ]", result) and not PRIVATE_CODE.search(result), result


def write_skill(repo, kind: str, body: str):
    (repo / "skills" / "x").mkdir(parents=True, exist_ok=True)
    text = "---\nname: x\nmetadata:\n  kind: " + kind + "\n---\n" + body + "\n"
    (repo / "skills" / "x" / "SKILL.md").write_text(text, encoding="utf-8")


def git(repo, *args):
    # Cô lập khỏi cấu hình toàn máy (RF134): không ký commit, không chạy hook của máy (`core.hooksPath`).
    ident = ["-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", "-c", "core.hooksPath="]
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


def test_temp_repo_ignores_machine_wide_git_config(tmp_path, monkeypatch):
    """TK12.2 (RF134): repo git tạm không dùng cấu hình git toàn máy. Cấu hình toàn máy giả ở đây bắt ký commit (`gpgsign`,
    chương trình ký không có thật) và trỏ `core.hooksPath` tới hook `pre-commit` luôn thất bại; commit trong repo tạm vẫn phải qua."""
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    hook = hooks / "pre-commit"
    hook.write_bytes(b"#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    cfg = tmp_path / "global.gitconfig"
    cfg.write_text(f"[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = /nonexistent/sign\n[core]\n\thooksPath = {hooks.as_posix()}\n",
                   encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    (tmp_path / "r").mkdir()
    repo = git_repo(tmp_path / "r", "discipline")  # đỏ nếu `git()` để cấu hình toàn máy chen vào commit
    assert tree_hash("x", repo) is not None


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
