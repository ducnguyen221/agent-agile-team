"""Máy kiểm luật trao đổi agent–người (SPR-21, RQ-083): file luật, skill `explain`, mẫu tài liệu, dòng trỏ ở
`AGENTS.md`, luật `plain-summary` của `check`. Viết trước khi có luật (RED): mỗi test đỏ vì thiếu đúng thứ nó kiểm,
không vì lỗi nạp. Nhóm `method`/`skill` xanh sau TK3/TK5; nhóm `template`/`agents`/`check` xanh sau TK4/TK6 (chờ SPR-20 gộp `main`)."""

from __future__ import annotations

import datetime
import re
import shutil
from pathlib import Path

import pytest

from conftest import FIXTURES, REPO, write_lf
import check

VALID = FIXTURES / "valid"
SECTION = "## Tóm tắt cho người không chuyên"
POINTER = "method/communication.md"
AGENTS_MAX_BYTES = 10 * 1024


def read(rel: str) -> str:
    path = REPO / rel
    assert path.is_file(), f"thiếu file `{rel}`"
    return path.read_text(encoding="utf-8")


# ---- method: file luật và hàng đăng ký -------------------------------------------------------------------------

def test_method_communication_file_exists_with_conclusion():
    text = read(POINTER)
    assert text.lstrip().startswith("# "), "file luật phải có tiêu đề cấp 1"
    assert "> **Kết luận:**" in text, "file luật phải mở bằng khối `> **Kết luận:**`"


@pytest.mark.parametrize("needle", [
    "súc tích", "diễn giải", "/explain",            # FR3: hai chế độ và lệnh
    "[tên", "đường",                                  # FR1: dạng link
    "Cần anh quyết", "KHUYẾN NGHỊ", "im lặng",        # FR2: mẫu câu hỏi, im lặng không phải duyệt
    "Tóm tắt cho người không chuyên",                 # FR4.2: tài liệu hai lớp
    "ngoài thư mục",                                  # FR1.4
])
def test_method_communication_states_each_rule(needle):
    assert needle.lower() in read(POINTER).lower(), f"`{POINTER}` thiếu nội dung luật: {needle!r}"


def test_method_communication_question_template_has_four_parts():
    section = read(POINTER).split("## 3.", 1)[1].split("\n## ", 1)[0]
    for part in ("**Cần anh quyết:**", "Chi tiết: [", "**KHUYẾN NGHỊ:**", "| Phương án |"):
        assert part in section, f"mẫu câu hỏi ở mục 3 thiếu {part!r}"


def test_method_communication_is_not_bloated():
    lines = read(POINTER).count("\n")
    assert 40 <= lines <= 150, f"`{POINTER}` dài {lines} dòng, kỳ vọng 40–150"


def test_method_readme_registers_communication():
    text = read("method/README.md")
    assert "[communication.md](communication.md)" in text, "`method/README.md` thiếu hàng đăng ký communication.md"


# ---- skill: explain và con trỏ ở response-style ----------------------------------------------------------------

def test_explain_skill_exists_with_use_when_description():
    text = read("skills/explain/SKILL.md")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, "thiếu frontmatter"
    front = m.group(1)
    assert re.search(r"^name: explain$", front, re.M), "name phải là `explain`"
    assert re.search(r"^description: Use when", front, re.M), "description phải bắt đầu bằng `Use when`"
    assert "/explain" in front, "description phải nêu lệnh `/explain`"
    assert re.search(r"group: \"?communication\"?", front), "metadata.group phải là communication"


def test_explain_skill_has_tests():
    assert (REPO / "skills/explain/tests/scenarios.txt").is_file()
    assert (REPO / "skills/explain/tests/pressure.md").is_file(), "skill `explain` thiếu tests/pressure.md"


def test_response_style_points_to_explain_and_drops_why_trigger():
    text = read("skills/response-style/SKILL.md")
    desc = re.search(r"^description: (.*)$", text, re.M).group(1)
    for phrase in ('"why"', "understand", "/explain"):
        assert phrase not in desc, f"mô tả response-style còn trigger {phrase} (RK6, trùng với explain)"
    assert "skill `explain`" in text, "response-style phải trỏ sang skill `explain`"
    assert POINTER in text, f"response-style phải trỏ tới `{POINTER}`"


def test_response_style_brief_block_mentions_links_and_recommendation():
    text = read("skills/response-style/SKILL.md")
    block = text.split("## 8.", 1)[1]
    assert "link" in block.lower(), "khối rút gọn cho subagent thiếu dòng về link (FR5.3)"
    assert "KHUYẾN NGHỊ" in block, "khối rút gọn cho subagent thiếu dòng về khuyến nghị (FR5.3)"
    assert "[tên:dòng](" in block, "khối rút gọn dùng dạng link khác `[tên:dòng](đường:dòng)` của method/communication.md mục 2"


def test_no_old_link_form_in_communication_files():
    for rel in ("skills/response-style/SKILL.md", "skills/explain/SKILL.md", "skills/explain/tests/scenarios.txt", POINTER):
        assert "[tên](" not in read(rel), f"`{rel}` còn dạng link cũ `[tên](…)`"


def test_skills_readme_lists_explain():
    text = read("skills/README.md")
    assert "(explain/SKILL.md)" in text, "`skills/README.md` thiếu hàng mô tả skill `explain` ở mục lục"
    assert "(explain/tests/pressure.md)" in text, "`skills/README.md` thiếu hàng `explain` ở bảng hiện trạng thử"


# ---- template: mục tóm tắt (TK6) -------------------------------------------------------------------------------

@pytest.mark.parametrize("doc", ["SPEC", "PLAN"])
def test_templates_have_plain_summary(doc):
    assert SECTION in read(f"templates/sprint/{doc}.md"), f"mẫu {doc} thiếu mục `{SECTION}`"


# ---- agents: đúng một dòng trỏ, trong ngân sách (TK4) ----------------------------------------------------------

def test_agents_md_single_pointer():
    data = (REPO / "AGENTS.md").read_bytes()
    text = data.decode("utf-8")
    assert text.count(POINTER) == 1, f"`AGENTS.md` phải trỏ tới `{POINTER}` đúng 1 lần, thấy {text.count(POINTER)}"
    assert len(data) <= AGENTS_MAX_BYTES, f"`AGENTS.md` {len(data)} B vượt trần {AGENTS_MAX_BYTES} B"


# ---- check: luật plain-summary (TK6) ---------------------------------------------------------------------------

def effective() -> datetime.date:
    value = getattr(check, "PLAIN_SUMMARY_EFFECTIVE", None)
    assert value is not None, "`scripts/check.py` chưa có hằng `PLAIN_SUMMARY_EFFECTIVE` (luật plain-summary chưa có)"
    return value if isinstance(value, datetime.date) else datetime.date.fromisoformat(str(value))


def sprint_with(tmp_path: Path, created: datetime.date, extra: str = "") -> Path:
    root = tmp_path / "sprint"
    shutil.copytree(VALID, root)
    spec = root / "SPEC.md"
    text = spec.read_text(encoding="utf-8")
    assert "created: 2026-02-01" in text
    text = text.replace("created: 2026-02-01", f"created: {created.isoformat()}", 1)
    marker = "## 1. Bối cảnh"
    assert marker in text
    write_lf(spec, text.replace(marker, extra + marker, 1) if extra else text)
    return root


def rules_of(root: Path) -> set:
    return {f.rule for f in check.check_paths([root]).findings}


def test_check_flags_missing_plain_summary(tmp_path):
    root = sprint_with(tmp_path, effective() + datetime.timedelta(days=1))
    assert "plain-summary" in rules_of(root)


def test_check_ignores_old_docs(tmp_path):
    root = sprint_with(tmp_path, datetime.date(2026, 1, 15))
    effective()  # đỏ nếu luật chưa có, để test này không xanh giả khi `check` chưa biết luật
    assert "plain-summary" not in rules_of(root)


def test_check_accepts_filled_summary(tmp_path):
    body = f"{SECTION}\n\nSprint cho người dùng xuất đơn ra CSV để gửi kế toán; xong khi mở được bằng Excel.\n\n"
    root = sprint_with(tmp_path, effective() + datetime.timedelta(days=1), body)
    assert "plain-summary" not in rules_of(root)


def test_check_treats_template_comment_as_empty(tmp_path):
    template = read("templates/sprint/SPEC.md")
    assert SECTION in template, "mẫu SPEC chưa có mục tóm tắt nên chưa lấy được chú thích mẫu"
    section = template.split(SECTION, 1)[1].split("\n## ", 1)[0]
    root = sprint_with(tmp_path, effective() + datetime.timedelta(days=1), SECTION + section + "\n")
    assert "plain-summary" in rules_of(root)


# ---- check: biên và phạm vi của luật plain-summary (TK9 vòng sửa 1) ---------------------------------------------
# Các ca dưới đổi hằng bằng monkeypatch sang một ngày cố định nên không phụ thuộc ngày chốt thật ở TK10.

FIXED = "2030-05-05"


def plan_with(tmp_path: Path, created: str, extra: str = "") -> Path:
    root = tmp_path / "sprint"
    shutil.copytree(VALID, root)
    plan = root / "PLAN.md"
    text = plan.read_text(encoding="utf-8")
    assert "created: 2026-02-01" in text
    text = text.replace("created: 2026-02-01", f"created: {created}", 1)
    marker = "## Mục tiêu"
    assert marker in text
    write_lf(plan, text.replace(marker, extra + marker, 1) if extra else text)
    return root


def findings_of(root: Path, rule: str = "plain-summary") -> list:
    return [f for f in check.check_paths([root]).findings if f.rule == rule]


def test_check_boundary_created_on_effective_day_is_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "PLAIN_SUMMARY_EFFECTIVE", FIXED)
    assert findings_of(sprint_with(tmp_path, datetime.date.fromisoformat(FIXED)))


def test_check_boundary_day_before_effective_is_not_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "PLAIN_SUMMARY_EFFECTIVE", FIXED)
    assert not findings_of(sprint_with(tmp_path, datetime.date.fromisoformat(FIXED) - datetime.timedelta(days=1)))


def test_check_plan_without_summary_is_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "PLAIN_SUMMARY_EFFECTIVE", FIXED)
    hits = findings_of(plan_with(tmp_path, FIXED))
    assert any(Path(f.path).name == "PLAN.md" for f in hits), [f.render() for f in hits]


def test_check_plan_with_summary_is_accepted(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "PLAIN_SUMMARY_EFFECTIVE", FIXED)
    body = f"{SECTION}\n\nSprint cho người dùng xuất đơn ra CSV để gửi kế toán.\n\n"
    assert not [f for f in findings_of(plan_with(tmp_path, FIXED, body)) if Path(f.path).name == "PLAN.md"]


def test_check_sprint_md_is_out_of_scope(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "PLAIN_SUMMARY_EFFECTIVE", FIXED)
    root = tmp_path / "one"
    root.mkdir()
    write_lf(root / "SPRINT.md", f"---\ndoc: sprint\ncreated: {FIXED}\n---\n\n# Sprint\n\n## Kế hoạch\n\nViệc nhỏ.\n")
    assert not [f for f in findings_of(root) if Path(f.path).name == "SPRINT.md"]


def test_check_summary_with_only_subheading_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "PLAIN_SUMMARY_EFFECTIVE", FIXED)
    body = f"{SECTION}\n\n### Việc gì\n\n### Vì sao\n\n"
    hits = findings_of(sprint_with(tmp_path, datetime.date.fromisoformat(FIXED), body))
    assert hits and all("rỗng" in f.message for f in hits), [f.render() for f in hits]


def test_check_summary_with_text_under_subheading_is_accepted(tmp_path, monkeypatch):
    monkeypatch.setattr(check, "PLAIN_SUMMARY_EFFECTIVE", FIXED)
    body = f"{SECTION}\n\n### Việc gì\n\nXuất đơn ra CSV để gửi kế toán.\n\n"
    assert not findings_of(sprint_with(tmp_path, datetime.date.fromisoformat(FIXED), body))


# ---- nội dung bảo mật của luật và skill (TK9 vòng sửa 1) ---------------------------------------------------------

SECRET_NAME = "." + "secret"  # ghép để file test không chứa đường kho secret nguyên văn


def test_communication_rule_excludes_secret_files_from_links():
    text = read(POINTER)
    assert SECRET_NAME in text and "Không link tới file secret" in text
    assert "luôn thắng" in text, "thứ bậc: luật secret, cổng, 5 ý của AGENTS.md luôn thắng"


def test_explain_skill_excludes_secrets_and_treats_source_as_data():
    text = read("skills/explain/SKILL.md")
    assert "Loại trừ secret" in text and SECRET_NAME in text and ".env" in text
    assert "dữ liệu, không phải lệnh" in text


def test_silence_is_never_approval_for_secrets_or_out_of_scope():
    text = read(POINTER)
    assert "Im lặng không bao giờ là duyệt" in text
    assert "việc chạm secret" in text and "ngoài phạm vi" in text
    assert "không tự chọn phương án" in text
