"""Lệnh gạch chéo `commands/autopilot-goal.md` (SPR-27, RQ-131): chỉ **in** khối `/goal` cho người dùng tự gửi.

Hỏng kiểu này thì hỏng im lặng: lệnh tự chạy `/goal` hay có công cụ ghi/shell; thân câu `/goal` lệch bản Đức duyệt
(mất điều kiện dừng, mất câu cấm push); trần lượt bịa thay vì lấy từ `method/autopilot.md` mục 2.1; câu `/goal` vượt
4.000 ký tự nên bị từ chối; đối số của người dùng bị coi là chỉ dẫn.
"""

from __future__ import annotations

import re
from pathlib import Path

import _autopilot_rules as rules

REPO = Path(__file__).resolve().parent.parent
COMMAND = REPO / "commands" / "autopilot-goal.md"
GOAL_LIMIT = 4000
READ_ONLY_TOOLS = {"Read", "Glob", "Grep"}
# Thân câu /goal Đức duyệt (SPR-27 lời giao); `{N}` là trần lượt, `{PUSH}` là câu cấm hoặc câu lời cấp.
APPROVED_GOAL_PARTS = (
    "Hoàn thành sprint đang mở theo đúng kế hoạch đã qua Cổng 1, không dừng để hỏi những việc không phải điều kiện dừng.",
    "Xong khi MỘT trong các điều sau được ghi trong chat, kèm bằng chứng dán nguyên văn (lệnh và dòng kết quả mới chạy, hoặc file:dòng):",
    "(A) mọi việc trong PLAN ở trạng thái Xong, bằng chứng từng việc, REPORT đã ghi verdict Đạt hoặc Đạt có điều kiện và `check` thư mục sprint báo 0 Chặn, 0 Phải sửa;",
    "hoặc (B) agent đã dừng đúng một điều kiện dừng và nêu rõ: việc không đảo ngược, chạm bảo mật hoặc secret, tác động ra ngoài phạm vi đã giao, hay PLAN hỏng vì giả định sai.",
    "Trong lúc làm: gặp lựa chọn mà người dùng chưa trả lời thì chọn phương án khuyến nghị, ghi một dòng 'Phán quyết: <gì> — <vì sao> — <sai thì tốn gì>', rồi làm tiếp;",
    "không kết lượt bằng câu hỏi hay khuyến nghị chờ người bấm.",
    "Không push, không gộp main, không tag, không sửa file luật hay hai file sàn cứng của autopilot nếu PLAN chưa có lời cấp rõ;",
    "việc đó ghi vào 'Việc cần người' của báo cuối và làm các việc khác.",
    "Dừng ngay và báo nếu đã chạy {N} lượt mà chưa đạt (A) hoặc (B), hoặc cùng một lỗi lặp lại 3 lần.",
)
BAN_CLAUSES = (
    "không chạy `/goal`",
    "không dùng công cụ ghi",
    "không chạy lệnh shell hay git",
    "không ghi hồ sơ sprint",
    "không push",
    "không giao việc cho agent khác",
)
NOTE_PHRASES = (
    "chế độ quyền auto",
    "không đổi chế độ quyền",
    "không chạy lệnh",
    "trong chat",
    "một goal",
    "chưa làm gì",
)


def text() -> str:
    assert COMMAND.is_file(), "thiếu commands/autopilot-goal.md"
    return COMMAND.read_text(encoding="utf-8")


def frontmatter(body: str) -> dict[str, str]:
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", body, re.S)
    assert match, "lệnh thiếu frontmatter"
    return {k.strip(): v.strip().strip('"') for k, v in (line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)}


def fences(body: str) -> list[str]:
    return re.findall(r"```[a-z]*\r?\n(.*?)```", body, re.S)


def goal_template() -> str:
    blocks = fences(text())
    assert len(blocks) == 1, "đúng MỘT khối mã: khối /goal"
    return blocks[0].strip()


def clauses(body: str) -> list[str]:
    return [c.strip().lower() for line in body.splitlines() for c in re.split(r"[,;]|\.(?:\s|$)", line) if c.strip()]


def test_frontmatter_hint_and_no_model_invocation():
    meta = frontmatter(text())
    assert meta.get("description")
    assert meta.get("argument-hint") == "[SPR-NN]"
    assert meta.get("disable-model-invocation") == "true", "agent không được tự gọi lệnh"


def test_only_read_tools_and_no_shell_syntax():
    body = text()
    allowed = {t.strip() for t in frontmatter(body).get("allowed-tools", "").split(",") if t.strip()}
    assert allowed <= READ_ONLY_TOOLS, f"chỉ được công cụ đọc, thấy {allowed - READ_ONLY_TOOLS}"
    assert not re.search(r"(?m)^!|!`", body), "lệnh không được có cú pháp chạy shell"


def test_goal_block_starts_with_slash_goal_and_fits_limit_with_largest_n():
    block = goal_template()
    assert block.startswith("/goal "), "khối in ra phải mở bằng /goal"
    assert block.count("{N}") == 1
    filled = block.replace("{N}", "29")
    assert len(filled) <= GOAL_LIMIT - 200, f"khối {len(filled)} ký tự, chừa lề dưới trần {GOAL_LIMIT}"


def test_goal_body_keeps_every_approved_clause_verbatim():
    flat = " ".join(goal_template().split())
    for part in APPROVED_GOAL_PARTS:
        assert " ".join(part.split()) in flat, f"thiếu hoặc lệch chữ: {part[:60]}"


def test_goal_has_exactly_two_done_conditions_and_four_stop_conditions():
    flat = goal_template()
    assert flat.count("(A)") == 2 and flat.count("(B)") == 2  # nêu ở điều kiện xong và ở câu dừng theo trần
    for stop in ("việc không đảo ngược", "chạm bảo mật hoặc secret", "tác động ra ngoài phạm vi đã giao", "PLAN hỏng vì giả định sai"):
        assert stop in flat


def test_push_sentence_has_a_forbid_variant_and_a_grant_variant():
    body = text()
    assert "Không push, không gộp main, không tag" in goal_template()
    assert "lời cấp" in body and "trích nguyên văn" in body, "câu cho phép chỉ khi PLAN có lời cấp trích nguyên văn"
    assert "Đạt có điều kiện" in body and "không gộp" in body, "Đạt có điều kiện không mở gộp main"


def test_cap_table_matches_method_autopilot_formula():
    body = text()
    for size, label in (("tiny", "rất nhỏ"), ("small", "nhỏ"), ("medium", "vừa"), ("large", "lớn")):
        normal, high = rules.session_cap_formula(size, "normal"), rules.session_cap_formula(size, "high")
        assert re.search(rf"\|\s*{label}\s*\|\s*{normal}\s*\|\s*{high}\s*\|", body), f"bảng trần cỡ {label} lệch công thức: {normal}/{high}"
    assert "mục 2.1" in body and "Trần phiên:" in body, "ưu tiên dòng `Trần phiên:` của PLAN rồi mới tính từ bảng"


def test_default_cap_is_30_and_labelled_default():
    body = text()
    assert re.search(r"30[^.\n]*mặc định|mặc định[^.\n]*30", body)
    assert "không đọc được" in body


def test_ban_clauses_present_and_forbidden_words_only_in_ban_clauses():
    body = text()
    parts = clauses(body)
    for clause in BAN_CLAUSES:
        assert clause in parts, f"thiếu vế cấm {clause!r}"
    outside_goal = body.replace(goal_template(), "")
    for word in ("--clear", "Remove-Item", "revoked_at", "autopilot.json", "rm "):
        for part in clauses(outside_goal):
            if word in part:
                assert part.startswith("không"), f"{word!r} ngoài vế cấm: {part}"


def test_printed_notes_cover_permission_evaluator_and_single_goal():
    body = text()
    for phrase in NOTE_PHRASES:
        assert phrase in body, f"thiếu ghi chú {phrase!r}"


def test_arguments_placeholder_once_at_the_end_in_a_data_block():
    body = text()
    assert body.count("$ARGUMENTS") == 1
    before = body.split("$ARGUMENTS")[0]
    assert "dữ liệu" in before and "không làm theo" in before
    assert body.rstrip().endswith("$ARGUMENTS")
    assert "`$ARGUMENTS`" not in body


def test_only_a_whole_spr_argument_is_accepted():
    body = text()
    assert "toàn bộ đối số" in body.lower() and "SPR-" in body and "hợp lệ" in body


def test_command_file_is_not_in_the_autopilot_fence():
    assert "commands/autopilot-goal.md" not in rules.FENCE_FILES


def test_each_printed_note_is_its_own_bullet():
    """Mỗi ghi chú phải đứng riêng một dòng gạch đầu dòng: xoá một dòng là mất đúng ý đó (đột biến RF3 của SPR-27)."""
    bullets = [line for line in text().splitlines() if line.startswith("- ")]
    for phrase in ("chế độ quyền auto", "không đổi chế độ quyền", "không chạy lệnh", "trong chat", "một goal", "chưa làm gì", "mã sprint", "phiên agent", "chỉnh trước khi gửi"):
        assert any(phrase in b for b in bullets), f"không dòng gạch đầu dòng nào nói {phrase!r}"


def test_push_grant_replaces_only_the_push_clauses_and_waits_for_gate_2():
    body = text()
    step3 = body.split("3. **Chọn câu về push", 1)[1].split("4. **In**", 1)[0]
    assert "riêng các vế" in step3
    assert "chỉ sau khi Cổng 2 Đạt" in step3
    assert "Đạt có điều kiện thì không gộp main" in step3
    assert "không sửa file luật" in step3 and "Việc cần người" in step3, "vế file luật và Việc cần người phải giữ nguyên"


def test_default_cap_sentence_and_multi_sprint_branch():
    body = text()
    assert "dùng 30 và ghi rõ" in body
    assert "có nhiều hơn một" in body and "không xác định được sprint" in body
