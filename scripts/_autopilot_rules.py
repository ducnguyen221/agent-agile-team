"""Rào autopilot gom một chỗ (SPR-16 FR1): hằng, hàm ngày/giờ và validator khối `delegation`.

`scripts/check.py` và `scripts/autopilot_guard.py` nhập từ đây; guard không nhập gì từ `check`. File này thuộc
`FENCE_FILES` và được `tests/test_fence_wiring.py` ghim (tên, số định nghĩa, dòng nối). Chỉ dùng thư viện chuẩn.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timedelta, timezone

DELEGATION_KEYS = ("grant", "grant_at", "scope", "expires", "by", "tier", "files", "revoked_at")
DELEGATION_OPTIONAL_KEYS = ("level", "program", "exclusions", "channel", "orchestrator", "sessions_cap", "mode")  # khoá autopilot (method/autopilot.md): có một khoá là kích luật
AUTOPILOT_PREFIX = "bật autopilot"  # `grant` bắt đầu bằng chuỗi này (không phân biệt hoa thường) cũng kích luật
AUTOPILOT_LEVELS = ("gate_1", "gate_1_2", "program")
AUTOPILOT_EXCLUSIONS = ("push", "tag", "version", "main_merge", "publish", "license", "irreversible_delete",
                        "rules_unlisted", "user_soul", "secret", "auth", "network_fetch", "branch_merge_local")  # danh sách đóng 13 mục
# Chế độ (SPR-20 FR1): `open` (mặc định của lệnh có Cổng 2) chỉ luôn chặn 7 mục, 6 mục còn lại tự chạy trong điều kiện của
# method/autopilot.md; `secure` giữ nguyên 13 mục. Hai tập này chia đúng `AUTOPILOT_EXCLUSIONS` (bản ghim ở tests/test_fence_wiring.py).
OPEN_ALWAYS_BLOCKED = ("network_fetch", "rules_unlisted", "irreversible_delete", "secret", "auth", "user_soul", "license")
OPEN_DEFAULT_OPEN = ("push", "branch_merge_local", "version", "main_merge", "tag", "publish")
AUTOPILOT_MODES = ("open", "secure")
MODE_OPEN_EFFECTIVE_DATE = "2026-11-13"  # khối `mode: open` có `grant_at` trước ngày này là sai; chốt lại ở Cổng 2 (DN2)
AUTOPILOT_SECURE_SUFFIX = "-secure"  # `Bật autopilot-secure …`: lệnh của chế độ chặt
AUTOPILOT_BLOCK_FLAGS = {"+chặn-push": "push", "+chặn-nhánh": "branch_merge_local", "+chặn-version": "version",
                         "+chặn-gộp-chính": "main_merge", "+chặn-tag": "tag", "+chặn-phát-hành": "publish"}
AUTOPILOT_GATES_BOTH = "cổng 1+2"  # trong `grant` của mức program: phạm vi là cả hai cổng
AUTOPILOT_BRANCH_SUFFIX = "+nhánh"  # hậu tố của lệnh cho phép bỏ `branch_merge_local` khỏi `exclusions`
AUTOPILOT_PUSH_FLAG = "+đẩy-nhánh"  # hậu tố của lệnh cho phép bỏ `push` khỏi `exclusions` (chỉ đẩy đúng hợp đồng đích, method/git-permissions.md)
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
    "tests/test_git_fence.py",
    "tests/test_git_server_layer.py",
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


def _grant_parts(grant: str) -> tuple[bool, str, str]:
    """`(có -secure, chữ mức đã chuẩn hoá, phần sau tiền tố)` của câu lệnh đã NFC + casefold; câu không mở đầu bằng tiền tố → `ValueError`."""
    text = unicodedata.normalize("NFC", grant).casefold().strip() if isinstance(grant, str) else ""
    if not text.startswith(AUTOPILOT_PREFIX):
        raise ValueError(f"lời cấp phải mở đầu bằng '{AUTOPILOT_PREFIX}' (ví dụ: 'Bật autopilot cổng 1+2 cho SPR-9 tới hết sprint.')")
    rest = text[len(AUTOPILOT_PREFIX):]
    secure_word = rest.startswith(AUTOPILOT_SECURE_SUFFIX)
    if secure_word:
        rest = rest[len(AUTOPILOT_SECURE_SUFFIX):]
    rest = rest.lstrip()
    stated = ("program" if rest.startswith("chương trình") else "gate_1_2" if rest.startswith(AUTOPILOT_GATES_BOTH)
              else "gate_1" if rest.startswith("cổng 1") or not rest.startswith("cổng ") else "unknown")
    return secure_word, stated, text


def compute_mode(grant: str) -> tuple[str, frozenset[str]]:
    """Chế độ và tập `exclusions` tối thiểu mà câu lệnh đòi (SPR-20 FR1). `open` chỉ khi lệnh có Cổng 2 và không có `-secure`;
    Cổng 1 một mình và `autopilot-secure` là `secure` (13 mục). `+chặn-<mục>` thêm một mục vào tập ở chế độ mở; `+nhánh` và
    `+đẩy-nhánh` chỉ có nghĩa ở `secure` có Cổng 2 và đứng cuối câu. Cờ không hợp chế độ hoặc không biết → `ValueError`."""
    secure_word, stated, text = _grant_parts(grant)
    if stated == "unknown":
        raise ValueError("chữ mức sau 'Bật autopilot' phải là 'cổng 1', 'cổng 1+2' hoặc 'chương trình …' (ví dụ: 'Bật autopilot cổng 1+2 cho SPR-9.')")
    both = stated == "gate_1_2" or (stated == "program" and AUTOPILOT_GATES_BOTH in text)
    mode = "open" if both and not secure_word else "secure"
    flags = [w for w in re.split(r"[\s,;()]+", text) if w.startswith("+")]
    tail = text.rstrip(" .\t\r\n")
    excl = set(OPEN_ALWAYS_BLOCKED if mode == "open" else AUTOPILOT_EXCLUSIONS)
    for flag in flags:
        flag = flag.rstrip(".")
        if flag in AUTOPILOT_BLOCK_FLAGS:
            if mode != "open":
                raise ValueError(f"{flag} chỉ dùng ở chế độ mở: {text.strip()!r} đã chặn đủ 13 mục")
            excl.add(AUTOPILOT_BLOCK_FLAGS[flag])
        elif flag.startswith("+chặn-"):
            raise ValueError(f"{flag} không phải cờ chặn: dùng một trong {', '.join(AUTOPILOT_BLOCK_FLAGS)}")
        elif flag in (AUTOPILOT_BRANCH_SUFFIX, AUTOPILOT_PUSH_FLAG):
            if mode == "open":
                raise ValueError(f"{flag} không dùng ở chế độ mở (nhánh và đẩy đã mở): muốn chặn, nói '+chặn-nhánh' hoặc '+chặn-push'")
            if not (both and tail.endswith(flag)):
                raise ValueError(f"{flag} chỉ có nghĩa khi lệnh có Cổng 2 và {flag} đứng cuối câu")
            excl.discard("branch_merge_local" if flag == AUTOPILOT_BRANCH_SUFFIX else "push")
    return mode, frozenset(excl)


def autopilot_problem(block: dict) -> tuple[str, str] | None:
    """Luật autopilot (method/autopilot.md mục 3) trên khối `delegation`: `None` = không kích hoặc đạt, ngược lại
    `(khoá, lời)` của lỗi ĐẦU theo thứ tự kiểm: khoá bắt buộc → `level`/`program`/`expires` → `scope` khác tập cổng của `level` →
    `channel` → `exclusions` → `sessions_cap` → `orchestrator` trùng `by`. Khoá vắng báo ở dòng `delegation`."""
    grant = block.get("grant")
    grant_text = unicodedata.normalize("NFC", grant).casefold() if isinstance(grant, str) else ""
    if not (grant_text.lstrip().startswith(AUTOPILOT_PREFIX) or any(k in block for k in DELEGATION_OPTIONAL_KEYS)):
        return None  # không kích: hồ sơ kiểu cũ giữ nguyên kết quả

    def where(key: str) -> str:
        return f"delegation.{key}" if key in block else "delegation"

    for key in ("level", "expires", "exclusions"):
        if block.get(key) is None:
            return where(key), f"autopilot: thiếu delegation.{key} (bắt buộc khi lời cấp là autopilot hoặc có khoá autopilot)"
    level = block["level"]
    if level not in AUTOPILOT_LEVELS:  # `in` trên tuple so ==, nên danh sách/số không lọt
        return "delegation.level", f"delegation.level: {level!r} phải là một trong {list(AUTOPILOT_LEVELS)}"
    secure_word = False
    if grant_text.lstrip().startswith(AUTOPILOT_PREFIX):  # chữ mức trong lệnh phải khớp `level` (không nới phạm vi hơn lời người dùng)
        secure_word, stated, _ = _grant_parts(grant)  # bóc `-secure`; chữ mức chỉ tính khi đứng ngay sau tiền tố
        stated = None if stated == "unknown" else stated  # vắng mức = gate_1; cổng lạ = None
        if stated != level:
            return "delegation.level", f"autopilot: lời cấp nêu mức {stated!r} mà delegation.level là {level!r}"
    mode = block.get("mode", "secure")  # khối cũ vắng `mode` = secure (SC8: hồ sơ trước SPR-20 giữ nguyên kết quả)
    if mode not in AUTOPILOT_MODES:
        return "delegation.mode", f"delegation.mode: {mode!r} phải là một trong {list(AUTOPILOT_MODES)}"
    open_need: frozenset[str] = frozenset()
    if mode == "open":
        moment = parse_moment(block.get("grant_at"))
        if moment is None or moment[0].isoformat() < MODE_OPEN_EFFECTIVE_DATE:
            return "delegation.grant_at", f"autopilot chế độ mở: grant_at phải từ {MODE_OPEN_EFFECTIVE_DATE} trở đi (chế độ mở có từ ngày đó), đang là {block.get('grant_at')!r}"
        if secure_word:
            return "delegation.mode", "delegation.mode là open mà lời cấp là 'autopilot-secure': sửa mode thành secure"
        if not grant_text.lstrip().startswith(AUTOPILOT_PREFIX) and level != "gate_1_2":
            return "delegation.level", f"autopilot chế độ mở: lời cấp không phải lệnh 'Bật autopilot …' thì level phải là gate_1_2 (có Cổng 2), đang là {level!r}"
        try:
            want_mode, open_need = compute_mode(grant) if grant_text.lstrip().startswith(AUTOPILOT_PREFIX) else ("open", frozenset(OPEN_ALWAYS_BLOCKED))
        except ValueError as err:
            return "delegation.grant", f"autopilot: {err}"
        if want_mode != "open":
            return "delegation.mode", "delegation.mode là open nhưng lời cấp chỉ có Cổng 1 (hoặc không đủ Cổng 2): chế độ mở cần 'cổng 1+2'"
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
    exclusions = block["exclusions"]
    if not (isinstance(exclusions, list) and all(isinstance(e, str) for e in exclusions)):
        return "delegation.exclusions", f"delegation.exclusions: {exclusions!r} phải là danh sách chuỗi"
    outside = [e for e in exclusions if e not in AUTOPILOT_EXCLUSIONS]
    if outside:
        return "delegation.exclusions", f"delegation.exclusions có mục ngoài danh sách đóng: {', '.join(outside)}"
    repeated = sorted({e for e in exclusions if exclusions.count(e) > 1})
    if repeated:
        return "delegation.exclusions", f"delegation.exclusions có mục trùng: {', '.join(repeated)}"
    branch_ok = "gate_2" in wanted and grant_text.rstrip(" .\t\r\n").endswith(AUTOPILOT_BRANCH_SUFFIX)  # `+nhánh` đứng cuối câu, chỉ đi với mức có Cổng 2
    push_ok = "gate_2" in wanted and grant_text.rstrip(" .\t\r\n").endswith(AUTOPILOT_PUSH_FLAG)  # cờ đứng cuối câu, cùng luật `+nhánh`
    if mode == "open":  # tập cha: được chặn thêm, không được bớt mục nào lệnh đòi
        missing = [e for e in AUTOPILOT_EXCLUSIONS if e in open_need and e not in exclusions]
    else:
        missing = [e for e in AUTOPILOT_EXCLUSIONS if e not in exclusions
                   and not (e == "branch_merge_local" and branch_ok) and not (e == "push" and push_ok)]
    if missing:
        hint = " (branch_merge_local chỉ được vắng khi mức có gate_2 và lời cấp kết thúc bằng +nhánh)" if "branch_merge_local" in missing else ""
        if "push" in missing:
            hint += " (push chỉ được vắng khi mức có gate_2 và lời cấp kết thúc bằng +đẩy-nhánh)"
        return "delegation.exclusions", f"delegation.exclusions thiếu mục bắt buộc: {', '.join(missing)}{hint}"
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
