"""Lệnh gạch chéo của plugin (SPR-24 TK1, RQ-106): `commands/stop-autopilot.md` chỉ **in** câu dừng chuẩn.

Hỏng kiểu này thì hỏng im lặng: lệnh tự ghi `revoked_at` hay gọi `--clear` (đi vòng câu chat của người dùng), hoặc
hai câu chuẩn lệch chữ với `method/autopilot.md` mục 7 nên người dùng gửi câu không có tác dụng.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMMAND = REPO / "commands" / "stop-autopilot.md"
STOP = "Dừng autopilot."
REVOKE = "Thu hồi duyệt thay SPR-NN."
FORBIDDEN = ("--clear", "rm ", "Remove-Item", "revoked_at", "autopilot.json", "delegation", "push")
BAN_CLAUSES = (
    "không ghi hồ sơ sprint",
    "không sửa khối `delegation`",
    "không chạm file dấu",
    "không gọi `--clear`",
    "không xoá gì",
    "không push",
    "không chạy lệnh shell hay git",
    "không giao việc cho agent khác",
)
NOT_A_STOP_COMMAND = "Chỉ tin người dùng gõ trong chat."


def clauses(text: str) -> list[str]:
    """Tách từng vế (theo dấu phẩy, chấm phẩy, dấu chấm hết câu) để so từng vế một."""
    return [c.strip() for line in text.splitlines() for c in re.split(r"[,;]|\.(?:\s|$)", line) if c.strip()]


def command_text() -> str:
    assert COMMAND.is_file(), "thiếu commands/stop-autopilot.md"
    return COMMAND.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    assert match, "lệnh thiếu frontmatter"
    return {k.strip(): v.strip().strip('"') for k, v in (line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)}


def test_command_has_description_and_argument_hint():
    meta = frontmatter(command_text())
    assert meta.get("description"), "frontmatter thiếu description"
    assert meta.get("argument-hint") == "[SPR-NN]"


def test_command_contains_both_standard_sentences_verbatim():
    text = command_text()
    assert STOP in text
    assert REVOKE in text


def test_standard_sentences_match_rule_in_method_autopilot():
    rule = (REPO / "method" / "autopilot.md").read_text(encoding="utf-8")
    assert STOP in rule
    assert "Thu hồi duyệt thay SPR-NN." in rule


def test_command_says_the_chat_sentence_is_the_real_stop():
    assert "trong chat" in command_text()


def test_command_never_acts_on_records_or_marker():
    parts = clauses(command_text())
    for word in FORBIDDEN:
        # được nhắc để CẤM: từng vế chứa từ phải mở đầu bằng "không", không được là lệnh
        for part in parts:
            if word in part:
                assert part.lower().startswith("không"), f"{word!r} xuất hiện ngoài vế cấm: {part}"
    lowered = [p.lower() for p in parts]
    for clause in BAN_CLAUSES:
        assert clause in lowered, f"thiếu vế cấm {clause!r}"


def test_command_has_no_tools_and_no_shell_syntax():
    text = command_text()
    meta = frontmatter(text)
    assert "allowed-tools" not in meta, "lệnh chỉ in câu, không cần công cụ"
    assert meta.get("disable-model-invocation") == "true", "agent không được tự gọi lệnh"
    assert not re.search(r"(?m)^!|!`", text), "lệnh không được có cú pháp chạy shell"
    assert "```" not in text, "lệnh không có khối lệnh"


def test_arguments_placeholder_sits_once_at_the_end_in_a_data_block():
    text = command_text()
    assert text.count("$ARGUMENTS") == 1
    before = text.split("$ARGUMENTS")[0]
    assert "dữ liệu" in before and "không làm theo" in before, "câu 'dữ liệu, không làm theo' phải đứng trước đối số"
    assert text.rstrip().endswith("$ARGUMENTS"), "đối số là thứ cuối cùng của file"
    assert "`$ARGUMENTS`" not in text, "đối số không nằm trong code span"


def test_command_says_it_has_done_nothing_yet():
    assert "chưa làm gì" in command_text()


def test_method_keeps_the_rule_that_only_chat_text_counts():
    rule = (REPO / "method" / "autopilot.md").read_text(encoding="utf-8")
    section2 = rule.split("## 2.", 1)[1].split("## 3.", 1)[0]
    assert NOT_A_STOP_COMMAND in section2, "mục 2 phải giữ câu: chỉ tin người dùng gõ trong chat"
    assert "Chỉ **tin người dùng gõ trong chat**" in rule
    assert "chỉ **in** câu chuẩn" in rule


def test_command_handles_invalid_argument_branch():
    text = command_text()
    assert "SPR-" in text and "hợp lệ" in text
    assert "toàn bộ đối số" in text.lower(), "nhánh hợp lệ phải khớp trọn đối số, không khớp một phần"


