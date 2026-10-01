"""Thư viện chung: tập con YAML của frontmatter, che phần mã trong Markdown, đọc `.agile.json`.

Hợp đồng ở `templates/README.md` mục 2 và 7. Mọi cấu trúc ngoài tập con phải báo lỗi có số dòng của file,
không đoán.
"""

import json
import re

import pytest

from conftest import SCRIPTS  # noqa: F401  (đảm bảo scripts/ nằm trên sys.path)
import _common as c


def fm(body: str) -> str:
    return "---\n" + body + "---\n\n# Tiêu đề\n"


# --- Frontmatter: phần đọc được ---------------------------------------------------------------------


def test_no_frontmatter_returns_none():
    assert c.parse_frontmatter("# Chỉ có tiêu đề\n") is None


def test_scalars_and_comments():
    text = fm(
        "# comment cả dòng\n"
        "id: SPR-01-spec\n"
        "sprint: null  # chưa có sổ\n"
        "flag: true\n"
        "off: false\n"
        "round: 3\n"
        "neg: -2\n"
        "created: 2026-01-15\n"
        'quote: "duyệt, làm tiếp # không phải comment"\n'
        'esc: "a \\"b\\" c\\\\d"\n'
        "\n"
        "note: có dấu phẩy, vẫn là chuỗi trần\n"
    )
    got = c.parse_frontmatter(text)
    assert got.data == {
        "id": "SPR-01-spec",
        "sprint": None,
        "flag": True,
        "off": False,
        "round": 3,
        "neg": -2,
        "created": "2026-01-15",
        "quote": "duyệt, làm tiếp # không phải comment",
        "esc": 'a "b" c\\d',
        "note": "có dấu phẩy, vẫn là chuỗi trần",
    }
    assert got.lines["id"] == 3
    assert got.end_line == 14
    assert got.body_start == 15


def test_inline_lists():
    got = c.parse_frontmatter(fm('a: []\nb: [secret, auth]\nc: [T1, agent-a, "ghi chú, có phẩy"]\nd: [1, true, null]\n'))
    assert got.data == {
        "a": [],
        "b": ["secret", "auth"],
        "c": ["T1", "agent-a", "ghi chú, có phẩy"],
        "d": [1, True, None],
    }


def test_one_level_block():
    got = c.parse_frontmatter(fm("roles:\n  analyst: [T1, agent-a]\n  qa: [T3, agent-f]\nlinks:\n  spec: SPEC.md\nempty:\nafter: x\n"))
    assert got.data["roles"] == {"analyst": ["T1", "agent-a"], "qa": ["T3", "agent-f"]}
    assert got.data["links"] == {"spec": "SPEC.md"}
    assert got.data["empty"] is None  # khoá rỗng không có dòng con = null
    assert got.data["after"] == "x"
    assert got.lines["roles.qa"] == 4


def test_bom_and_crlf_are_tolerated():
    got = c.parse_frontmatter("\ufeff---\r\nid: X\r\n---\r\n")
    assert got.data == {"id": "X"}


# --- Frontmatter: ngoài tập con → lỗi có dòng -------------------------------------------------------


@pytest.mark.parametrize(
    "body, line, phrase",
    [
        ("roles:\n  - role: analyst\n", 3, "block list"),
        ("- a\n", 2, "block list"),
        ("text: |\n  dòng\n", 2, "multi-line"),
        ("text: >\n", 2, "multi-line"),
        ("q: 'nháy đơn'\n", 2, "single quote"),
        ("m: {a: 1}\n", 2, "inline map"),
        ("a: &anchor x\n", 2, "anchor"),
        ("a: *alias\n", 2, "anchor"),
        ("a: !tag x\n", 2, "anchor"),
        ("a: %x\n", 2, "reserved"),
        ("a: `x`\n", 2, "reserved"),
        ("a:\n  b:\n    c: 1\n", 3, "one level"),
        ("a:\n    b: 1\n", 3, "indent"),
        ("  b: 1\n", 2, "parent"),
        ("a: 1\na: 2\n", 3, "duplicate"),
        ("Bad: 1\n", 2, "key"),
        ("a:b\n", 2, "key"),
        ("a: x\tb\n", 2, "tab"),
        ('a: "chưa đóng\n', 2, "quote"),
        ('a: "x" thừa\n', 2, "quote"),
        ('a: "x\\n"\n', 2, "escape"),
        ("a: [x, [y]]\n", 2, "list"),
        ("a: [x, , y]\n", 2, "list"),
        ("a: [x\n", 2, "list"),
        ("a: b: c\n", 2, ": "),
        ("a: x\n---\nb: y\n", None, None),  # khối thứ hai nằm trong thân → không phải lỗi frontmatter
    ],
)
def test_outside_subset_reports_line(body, line, phrase):
    if line is None:
        assert c.parse_frontmatter(fm(body)).data == {"a": "x"}
        return
    with pytest.raises(c.SubsetError) as err:
        c.parse_frontmatter(fm(body))
    assert err.value.line == line
    assert phrase in str(err.value)


def test_unterminated_frontmatter():
    with pytest.raises(c.SubsetError) as err:
        c.parse_frontmatter("---\nid: X\n")
    assert err.value.line == 1


# --- Che mã trong Markdown ---------------------------------------------------------------------------


def test_mask_keeps_line_count_and_hides_code_and_comments():
    lines = [
        "Mã `P1` trong code, P2 ngoài code.",
        "```",
        "P3 trong khối code",
        "```",
        "<!-- P4 trong comment",
        "vẫn comment P5 --> sau comment P6",
        "``hai `P7` dấu`` rồi P8",
        "~~~python",
        "P9",
        "~~~",
        "dấu ` lẻ P10",
    ]
    masked = c.mask_markdown(lines)
    assert len(masked) == len(lines)
    joined = "\n".join(masked)
    found = set(re.findall(r"(?<![A-Za-z0-9])P[0-9]+(?![0-9])", joined))
    assert found == {"P2", "P6", "P8", "P10"}
    assert len(masked[0]) == len(lines[0])


def test_split_body_skips_frontmatter():
    text = "---\nid: X\n---\n# A\nP1\n"
    start, lines = c.body_lines(text)
    assert start == 4
    assert lines == ["# A", "P1"]


# --- Cấu hình dự án ----------------------------------------------------------------------------------


def test_load_config_defaults_when_template_used(tmp_path):
    (tmp_path / ".agile.json").write_text(json.dumps({"schema": 1, "paths": {"requests": "R.md"}}), encoding="utf-8")
    cfg = c.load_config(tmp_path)
    assert cfg["paths"]["requests"] == "R.md"
    assert cfg["paths"]["sprints"] == "docs/plans/SPRINTS.md"
    assert cfg["id_width"]["sprint"] == 2
    assert cfg["visibility"] == "private"


def test_load_config_missing_and_invalid(tmp_path):
    with pytest.raises(c.ConfigError):
        c.load_config(tmp_path)
    (tmp_path / ".agile.json").write_text("{không phải json", encoding="utf-8")
    with pytest.raises(c.ConfigError) as err:
        c.load_config(tmp_path)
    assert ".agile.json" in str(err.value)


def test_default_config_matches_template():
    template = json.loads((c.REPO / "templates" / "project" / "agile.json").read_text(encoding="utf-8"))
    assert c.DEFAULT_CONFIG == template


def test_format_id_pads_to_width():
    assert c.format_id("RQ", 1, 3) == "RQ-001"
    assert c.format_id("SPR", 12, 2) == "SPR-12"
    assert c.format_id("SPR", 123, 2) == "SPR-123"
    assert c.parse_id("SPR-07") == ("SPR", 7)
    assert c.parse_id("không") is None
