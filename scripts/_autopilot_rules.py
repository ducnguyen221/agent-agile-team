"""Rào autopilot gom một chỗ (SPR-16 FR1): hằng, hàm ngày/giờ và validator khối `delegation`.

`scripts/check.py` và `scripts/autopilot_guard.py` nhập từ đây; guard không nhập gì từ `check`. File này thuộc
`FENCE_FILES` và được `tests/test_fence_wiring.py` ghim (tên, số định nghĩa, dòng nối). Chỉ dùng thư viện chuẩn.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timedelta, timezone

DELEGATION_KEYS = ("grant", "grant_at", "scope", "expires", "by", "tier", "files", "revoked_at")
DELEGATION_OPTIONAL_KEYS = ("level", "program", "channel", "orchestrator", "sessions_cap")  # khoá autopilot (method/autopilot.md): có một khoá là kích luật
AUTOPILOT_PREFIX = "bật autopilot"  # `grant` bắt đầu bằng chuỗi này (không phân biệt hoa thường) cũng kích luật
AUTOPILOT_LEVELS = ("gate_1", "gate_1_2", "program")
# Danh sách 13 mục: `autopilot_guard.py` chỉ dùng khi file dấu hỏng (chặn cả 13) và bản ghim `tests/test_fence_wiring.py` đếm đúng 13; luật `check` không đọc
# (một chế độ, không `exclusions`). `OPEN_ALWAYS_BLOCKED` mới là tập guard chặn khi file dấu hợp lệ; `OPEN_DEFAULT_OPEN` không còn nơi dùng (chỉ bản ghim).
AUTOPILOT_EXCLUSIONS = ("push", "tag", "version", "main_merge", "publish", "license", "irreversible_delete",
                        "rules_unlisted", "user_soul", "secret", "auth", "network_fetch", "branch_merge_local")  # danh sách đóng 13 mục
OPEN_ALWAYS_BLOCKED = ("network_fetch", "rules_unlisted", "irreversible_delete", "secret", "auth", "user_soul", "license")
OPEN_DEFAULT_OPEN = ("push", "branch_merge_local", "version", "main_merge", "tag", "publish")
# Ngày hiệu lực của các luật sprint mới (người quyết CQ/DN, dòng đếm lượt ở REPORT, người ký cổng độc lập với người làm); hồ sơ trước ngày này giữ nguyên kết quả.
MODE_OPEN_EFFECTIVE_DATE = "2026-11-13"
AUTOPILOT_GATES_BOTH = "cổng 1+2"  # trong `grant` của mức program: phạm vi là cả hai cổng
AUTOPILOT_BRANCH_SUFFIX = "+nhánh"  # hằng chết: chỉ còn để bản ghim `tests/test_fence_wiring.py` đếm đúng một định nghĩa; không nơi nào đọc (gỡ cùng bản ghim ở sprint sau)
AUTOPILOT_PUSH_FLAG = "+đẩy-nhánh"  # hằng chết như trên: chỉ còn vì bản ghim, không nơi nào đọc
# Trần phiên mỗi sprint (method/autopilot.md mục 2.1): cơ sở theo cỡ; `risk: high` nhân 1,25 làm tròn lên. Một nguồn: `check.py` đối chiếu `Trần phiên:` với bảng này.
SESSION_CAP_BASE = {"tiny": 4, "small": 8, "medium": 15, "large": 23}


def session_cap_formula(size, risk) -> int | None:
    """Trần phiên tối đa theo công thức cho `size`/`risk` của PLAN; cỡ lạ → `None` (không có công thức để so)."""
    base = SESSION_CAP_BASE.get(size) if isinstance(size, str) else None
    if base is None:
        return None
    return -(-base * 5 // 4) if risk == "high" else base  # 1,25 = 5/4, làm tròn lên bằng số nguyên


DELEGATION_CHANNELS = ("chat", "host_comment")
MOMENT = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2})(?: ([0-9]{2}):([0-9]{2}) ([+-])([0-9]{2})(?::?([0-9]{2}))?)?")
DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")

# Tập file chứa nội dung rào autopilot (SPEC SPR-16 FR1.1). trang quyền git và rào git thường trực (SPR-16) đã gỡ ở SPR-20 TK21.
# Bản ghim viết tay ở `tests/test_fence_wiring.py`.
FENCE_FILES: tuple[str, ...] = (
    "method/autopilot.md",
    "skills/intake/references/autopilot.md",
    "skills/running-sprint/references/autopilot.md",
    "skills/closing-sprint/references/autopilot.md",
    "scripts/_autopilot_rules.py",
    "scripts/autopilot_guard.py",
    "scripts/autopilot-hook.sh",
    "hooks/hooks.json",
)

# Sàn cứng (SPEC SPR-16 FR2): vùng văn bản bọc cặp mốc trong file trộn, và file thuộc sàn nguyên file.
FLOOR_MARKER_START = "<!-- san-cung:start -->"
FLOOR_MARKER_END = "<!-- san-cung:end -->"
FLOOR_ZONES: dict[str, int] = {  # đường file → số cặp mốc quy định
    "AGENTS.md": 2,
    "method/process.md": 3,
    "method/sizing.md": 1,
    "method/autopilot.md": 1,
}
FLOOR_FILES: tuple[str, ...] = FENCE_FILES + (  # `merge_ready.py`, `deploy_scan.py` (SPR-17) chỉ tính khi tồn tại
    "scripts/floor_check.py",
    "scripts/merge_ready.py",
    "scripts/deploy_scan.py",
    "tests/test_fence_wiring.py",
    "tests/test_floor_check.py",
    "tests/test_mutation_floor.py",
    ".github/workflows/verify.yml",
)


def parse_moment(value) -> tuple | None:
    """`YYYY-MM-DD` hoặc `YYYY-MM-DD HH:MM +TZ` → (ngày như đã viết, thời điểm có múi giờ hoặc `None`); không đọc được → `None`."""
    m = MOMENT.fullmatch(value.strip()) if isinstance(value, str) else None
    if not m:
        return None
    try:
        day = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        if m.group(2) is None:
            return day, None
        offset = int(m.group(5)) * 60 + int(m.group(6) or 0)
        if m.group(4) == "-":
            offset = -offset
        return day, datetime(day.year, day.month, day.day, int(m.group(2)), int(m.group(3)),
                             tzinfo=timezone(timedelta(minutes=offset)))
    except ValueError:  # ngày không có thật, giờ ngoài 00:00–23:59, múi giờ ngoài ±24h
        return None


def _stated_level(grant: str) -> str | None:
    """Mức mà câu lệnh `Bật autopilot …` nêu (`gate_1`, `gate_1_2`, `program`; vắng chữ mức = `gate_1`; mức lạ → `None`);
    câu không mở đầu bằng tiền tố → `ValueError`."""
    text = unicodedata.normalize("NFC", grant).casefold().strip() if isinstance(grant, str) else ""
    if not text.startswith(AUTOPILOT_PREFIX):
        raise ValueError(f"lời cấp phải mở đầu bằng '{AUTOPILOT_PREFIX}' (ví dụ: 'Bật autopilot cổng 1+2 cho SPR-9 tới hết sprint.')")
    rest = text[len(AUTOPILOT_PREFIX):].lstrip()
    if rest.startswith("chương trình"):
        return "program"
    if rest.startswith(AUTOPILOT_GATES_BOTH):
        return "gate_1_2"
    return "gate_1" if rest.startswith("cổng 1") or not rest.startswith("cổng ") else None


def autopilot_problem(block: dict) -> tuple[str, str] | None:
    """Luật autopilot (method/autopilot.md mục 3) trên khối `delegation`: `None` = không kích hoặc đạt, ngược lại
    `(khoá, lời)` của lỗi ĐẦU theo thứ tự kiểm: khoá bắt buộc → `level`/`program`/`expires` → `scope` khác tập cổng của `level` →
    `channel` → `sessions_cap` → `orchestrator` trùng `by`. Khoá vắng báo ở dòng `delegation`. Một chế độ: không `mode`/`exclusions`."""
    grant = block.get("grant")
    grant_text = unicodedata.normalize("NFC", grant).casefold() if isinstance(grant, str) else ""
    if not (grant_text.lstrip().startswith(AUTOPILOT_PREFIX) or any(k in block for k in DELEGATION_OPTIONAL_KEYS)):
        return None  # không kích: hồ sơ kiểu cũ giữ nguyên kết quả

    def where(key: str) -> str:
        return f"delegation.{key}" if key in block else "delegation"

    for key in ("level", "expires"):
        if block.get(key) is None:
            return where(key), f"autopilot: thiếu delegation.{key} (bắt buộc khi lời cấp là autopilot hoặc có khoá autopilot)"
    level = block["level"]
    if level not in AUTOPILOT_LEVELS:  # `in` trên tuple so ==, nên danh sách/số không lọt
        return "delegation.level", f"delegation.level: {level!r} phải là một trong {list(AUTOPILOT_LEVELS)}"
    if grant_text.lstrip().startswith(AUTOPILOT_PREFIX):  # chữ mức trong lệnh phải khớp `level` (không nới phạm vi hơn lời người dùng)
        stated = _stated_level(grant)  # vắng mức = gate_1; cổng lạ = None
        if stated != level:
            return "delegation.level", f"autopilot: lời cấp nêu mức {stated!r} mà delegation.level là {level!r}"
    program, expires = block.get("program"), block["expires"]
    if "program" in block and not (program is None or (isinstance(program, str) and program.strip())):
        return "delegation.program", f"delegation.program: {program!r} phải là tên chương trình hoặc null"
    if level == "program":
        if program is None:
            return where("program"), "autopilot: level program cần delegation.program là tên chương trình"
        if not (isinstance(expires, str) and DATE.fullmatch(expires) and parse_moment(expires) is not None):
            return "delegation.expires", f"autopilot: level program cần delegation.expires là ngày YYYY-MM-DD, đang là {expires!r}"
    scope = block.get("scope")
    wanted = ["gate_1", "gate_2"] if level == "gate_1_2" or (level == "program" and AUTOPILOT_GATES_BOTH in grant_text) else ["gate_1"]
    if isinstance(scope, list) and set(scope) != set(wanted):  # scope không phải danh sách: để kiểm cũ báo
        return "delegation.scope", f"autopilot: phạm vi {scope!r} phải bằng đúng {wanted!r} theo level {level}"
    if "channel" in block and block["channel"] not in DELEGATION_CHANNELS:
        return "delegation.channel", f"delegation.channel: {block['channel']!r} phải là một trong {list(DELEGATION_CHANNELS)}"
    cap = block.get("sessions_cap")
    if "sessions_cap" in block and not (cap is None or (isinstance(cap, int) and not isinstance(cap, bool) and cap >= 1)):
        return "delegation.sessions_cap", f"delegation.sessions_cap: {cap!r} phải là số nguyên >= 1 hoặc null"
    orchestrator = block.get("orchestrator")
    if "orchestrator" in block and not (orchestrator is None or (isinstance(orchestrator, str) and orchestrator.strip())):
        return "delegation.orchestrator", f"delegation.orchestrator: {orchestrator!r} phải là nhãn phiên điều phối hoặc null"
    if isinstance(orchestrator, str) and orchestrator == block.get("by"):
        return "delegation.orchestrator", "delegation.orchestrator trùng delegation.by (phiên điều phối không ký cổng)"
    files = block.get("files")
    if isinstance(files, list):  # không phải danh sách: kiểm cũ báo
        tokens = {w.rstrip(".") for w in re.split(r"[\s,;:()`'\"]+", grant)} if isinstance(grant, str) else set()
        for item in files:  # lệnh autopilot chuẩn không nêu file nên `files` thực tế là []; mục phải bằng đúng một từ của lời cấp và trông như đường dẫn (không nhận tên trần như LICENSE)
            if not (isinstance(item, str) and item.strip() and item in tokens and re.search(r"[./\\]", item)):  # đường dẫn: có dấu chấm hoặc gạch
                return "delegation.files", f"delegation.files có {item!r} không nêu trong lời cấp"
    return None


def zone_spans(text: str) -> list[tuple[int, int]] | str:
    """Các cặp mốc `san-cung` trong `text`: danh sách `(dòng mốc mở, dòng mốc đóng)` đánh số từ 1, hoặc một mã lỗi
    (`floor-unbalanced` mở không đóng/đóng không mở, `floor-nested` lồng nhau, `floor-in-fence` mốc nằm trong khối mã).
    Mốc là cả một dòng (bỏ khoảng trắng hai đầu); mốc nằm giữa dòng chữ hay trong dấu `code` không tính."""
    spans: list[tuple[int, int]] = []
    opened = 0
    fence = ""
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.strip()
        fenced = re.match(r"(`{3,}|~{3,})", line)
        if fenced:
            if not fence:
                fence = fenced.group(1)[0] * 3
            elif line.startswith(fence):
                fence = ""
            continue
        if line not in (FLOOR_MARKER_START, FLOOR_MARKER_END):
            continue
        if fence:
            return "floor-in-fence"
        if line == FLOOR_MARKER_START:
            if opened:
                return "floor-nested"
            opened = number
        else:
            if not opened:
                return "floor-unbalanced"
            spans.append((opened, number))
            opened = 0
    return "floor-unbalanced" if opened else spans
