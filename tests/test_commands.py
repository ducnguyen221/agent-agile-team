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
FORBIDDEN = ("--clear", "rm ", "Remove-Item", "revoked_at", "autopilot.json")


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
    text = command_text()
    for word in FORBIDDEN:
        # được nhắc để CẤM (dòng có "không"), không được là lệnh
        for line in text.splitlines():
            if word in line:
                assert "không" in line.lower(), f"{word!r} xuất hiện ngoài câu cấm: {line}"


def test_command_handles_invalid_argument_branch():
    text = command_text()
    assert "SPR-" in text and "hợp lệ" in text


def test_command_treats_arguments_as_data_not_instructions():
    text = command_text()
    assert "$ARGUMENTS" in text
    assert "dữ liệu" in text
