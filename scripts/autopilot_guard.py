"""Rào máy autopilot — hook PreToolUse từ chối lệnh shell thuộc danh sách loại (method/autopilot.md mục 5). Chỉ thư viện chuẩn.

Gọi: python autopilot_guard.py --format {claude,codex,antigravity}; đọc JSON sự kiện ở stdin.
Chỉ hoạt động khi có file dấu `.tmp/autopilot.json`: tìm từ thư mục làm việc của sự kiện đi lên, dừng sau cấp đầu tiên có `.git`
(thư mục hoặc file `gitdir:` của worktree). Không có file dấu → cho qua (claude/codex thoát 0 không in; antigravity in `{}`).
Có file dấu và lệnh khớp mục loại → chặn: claude/codex in lý do ở stderr rồi thoát 2; antigravity in JSON `deny` ở stdout, thoát 0.
Lý do: `autopilot: '<mục loại>' cần người dùng nói trong chat — lệnh không chạy`.

Mục có mẫu lệnh: push, tag, main_merge, irreversible_delete, branch_merge_local. Các mục khác là rào hành vi (không có mẫu).
Danh sách tên mục lấy từ `check.AUTOPILOT_EXCLUSIONS` (một nguồn). Không gọi tiến trình con; nhánh hiện tại đọc từ file `.git/HEAD`.

GIỚI HẠN ĐÃ BIẾT: mẫu là danh sách đóng, tách lệnh thô theo `&&`, `||`, `;`, `|`, `&`, xuống dòng, ngoặc và dấu huyền, không hiểu
dấu nháy (chấp nhận chặn nhầm). Chỉ mở lớp `bash -c`/`pwsh -Command`/`cmd /c` trực tiếp. Đối thủ cố ý (biến môi trường, script,
alias git, `python -c`, `cd` rồi `git -C`, ghép chuỗi tên lệnh) lách được; đây là lưới an toàn, không phải ranh giới bảo mật.

Đóng khi lỗi: có file dấu mà JSON hỏng hay hook gặp ngoại lệ → chặn; không có file dấu thì ngoại lệ không chặn việc của người dùng
(thư mục làm việc lúc đó là thư mục của tiến trình hook). AUTOPILOT_GUARD_DEBUG=1 in traceback ra stderr.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
import traceback
from typing import TextIO

FORMATS = ("claude", "codex", "antigravity")
MARKER_PARTS = (".tmp", "autopilot.json")
SHELL_TOOLS = frozenset({"bash", "powershell", "shell", "exec_command", "run_command", "local_shell", "shell_command"})
COMMAND_KEYS = ("command", "cmd", "CommandLine")  # tool_input.* (Claude, Codex) và toolCall.args.* (Antigravity)
CWD_KEYS = ("workdir", "cwd", "Cwd")
SHELL_WRAPPERS = frozenset({"bash", "sh", "zsh", "dash", "ksh", "pwsh", "powershell", "cmd"})
WRAPPER_FLAGS = frozenset({"-c", "-lc", "-ic", "-cl", "-command", "/c", "/k"})
SEPARATORS = re.compile(r"&&|\|\||[;|&\n\r()`]")
PREFIX_WORDS = frozenset({"if", "then", "else", "elif", "do", "while", "until", "{", "!", "time", "sudo", "command", "env",
                          "nohup", "exec", "builtin", "xargs", "nice", "stdbuf"})
ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
MAIN_BRANCHES = ("main", "master")
GIT_VALUE_OPTIONS = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"})
TAG_READ_ONLY = frozenset({"-l", "--list", "-v", "--verify", "--contains", "--no-contains", "--merged", "--no-merged", "--points-at"})
DELETE_COMMANDS = frozenset({"rm", "ri", "del", "erase", "rmdir", "rd", "remove-item"})
CD_COMMANDS = frozenset({"cd", "chdir", "pushd", "set-location", "sl"})
UNSAFE_PATH_CHARS = set(",$%`~{}()<>!^\"'\n\r;|&")
GLOB_CHARS = set("*?[")
MAX_UNWRAP = 3


def known_exclusions() -> tuple[str, ...]:
    """Danh sách đóng 13 mục từ `check.AUTOPILOT_EXCLUSIONS`; nạp muộn để lệnh không có file dấu không trả phí nhập `check`."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    from check import AUTOPILOT_EXCLUSIONS
    return tuple(AUTOPILOT_EXCLUSIONS)


# --- file dấu ---------------------------------------------------------------------------------------------------

def _has_git(directory: str) -> bool:
    return os.path.exists(os.path.join(directory, ".git"))


def find_marker(start: str) -> str | None:
    """Đường tới `.tmp/autopilot.json` gần nhất từ `start` đi lên; dừng sau cấp đầu tiên có `.git`."""
    current = os.path.abspath(start)
    while True:
        candidate = os.path.join(current, *MARKER_PARTS)
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(current)
        if _has_git(current) or parent == current:
            return None
        current = parent


def find_repo_root(start: str) -> str | None:
    """Thư mục chứa `.git` đầu tiên khi đi lên từ `start`, hoặc None."""
    current = os.path.abspath(start)
    while True:
        if _has_git(current):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def load_active(marker: str) -> tuple[set[str], bool]:
    """(mục đang chặn, file dấu hỏng?). File hỏng → chặn cả 13 mục. `exclusions` thiếu mục bắt buộc → bổ sung đủ;
    chỉ `branch_merge_local` được vắng khi khoá `exclusions` là danh sách không có nó (lệnh `+nhánh`)."""
    known = known_exclusions()
    required = {e for e in known if e != "branch_merge_local"}
    try:
        with open(marker, encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return set(known), True
    if not isinstance(data, dict):
        return set(known), True
    listed = data.get("exclusions")
    if not isinstance(listed, list):
        return set(known), False
    return required | ({"branch_merge_local"} & {e for e in listed if isinstance(e, str)}), False


# --- phân tích lệnh -------------------------------------------------------------------------------------------

def tokenize(segment: str) -> list[str]:
    """Tách theo khoảng trắng, nháy `'`/`"` gom token (bỏ nháy); `\\` là ký tự thường (đường Windows)."""
    tokens: list[str] = []
    buf: list[str] = []
    quote = ""
    started = False
    for ch in segment:
        if quote:
            if ch == quote:
                quote = ""
            else:
                buf.append(ch)
        elif ch in "'\"":
            quote = ch
            started = True
        elif ch.isspace():
            if buf or started:
                tokens.append("".join(buf))
            buf, started = [], False
        else:
            buf.append(ch)
    if buf or started:
        tokens.append("".join(buf))
    return tokens


def _exe_name(token: str) -> str:
    name = os.path.basename(token.replace("\\", "/")).lower()
    return name[:-4] if name.endswith((".exe", ".com")) else name


def _cluster(token: str, letters: str) -> bool:
    """Cụm cờ ngắn `-xyz` (chỉ chữ cái) chứa một trong `letters`."""
    return bool(re.fullmatch(r"-[A-Za-z]+", token)) and any(ch in token for ch in letters)


class Context:
    """Trạng thái một lần phân tích: mục đang chặn, thư mục làm việc, gốc repo; nhánh đọc từ HEAD khi cần."""

    def __init__(self, active: set[str], cwd: str) -> None:
        self.active = active
        self.cwd = os.path.abspath(cwd)
        self.root = find_repo_root(self.cwd)
        self.forced_main = False  # đã gặp `git checkout|switch main|master` trong lệnh ghép
        self.cwd_changed = False  # đã gặp `cd`: đường tương đối không còn đáng tin
        self._on_main: bool | None = None

    def on_main(self) -> bool:
        if self.forced_main:
            return True
        if self._on_main is None:
            self._on_main = self._read_head_is_main()
        return self._on_main

    def _read_head_is_main(self) -> bool:
        """Đọc `.git/HEAD` (hỗ trợ worktree: `.git` là file `gitdir:`). Không xác định được → True (đóng an toàn)."""
        if not self.root:
            return True
        git = os.path.join(self.root, ".git")
        try:
            if os.path.isfile(git):
                with open(git, encoding="utf-8") as handle:
                    first = handle.readline().strip()
                if not first.startswith("gitdir:"):
                    return True
                git = os.path.normpath(os.path.join(self.root, first[len("gitdir:"):].strip()))
            with open(os.path.join(git, "HEAD"), encoding="utf-8") as handle:
                head = handle.readline().strip()
        except (OSError, ValueError):
            return True
        prefix = "ref: refs/heads/"
        if not head.startswith(prefix) or not head[len(prefix):]:
            return True
        return head[len(prefix):] in MAIN_BRANCHES


def _git_subcommand(args: list[str]) -> tuple[str, list[str]]:
    index = 0
    while index < len(args):
        arg = args[index]
        if not arg.startswith("-"):
            return arg, args[index + 1:]
        index += 2 if arg in GIT_VALUE_OPTIONS else 1
    return "", []


def _git_item(args: list[str], ctx: Context) -> str | None:
    sub, rest = _git_subcommand(args)
    if sub == "push":
        return "push"
    if sub == "tag":
        if any(a in ("-d", "--delete") or _cluster(a, "d") for a in rest):
            return "irreversible_delete"
        if not rest or any(a.split("=", 1)[0] in TAG_READ_ONLY or re.fullmatch(r"-n\d*", a) for a in rest):
            return None
        return "tag"
    if sub in ("checkout", "switch"):
        if any(a in MAIN_BRANCHES for a in rest):
            ctx.forced_main = True
        return None
    if sub == "merge":
        if any(a in ("--abort", "--quit") for a in rest):
            return None
        return "main_merge" if ctx.on_main() else ("branch_merge_local" if "branch_merge_local" in ctx.active else None)
    if sub == "pull":
        return "main_merge" if ctx.on_main() else None
    if sub == "reset":
        return "irreversible_delete" if "--hard" in rest else None
    if sub == "branch":
        force = "--force" in rest or any(_cluster(a, "f") for a in rest)
        delete = "--delete" in rest or any(_cluster(a, "d") for a in rest)
        return "irreversible_delete" if any(_cluster(a, "D") for a in rest) or (force and delete) else None
    if sub == "clean":
        return "irreversible_delete" if "--force" in rest or any(_cluster(a, "f") for a in rest) else None
    if sub == "worktree":
        forced = "--force" in rest or any(_cluster(a, "f") for a in rest)
        return "irreversible_delete" if rest[:1] == ["remove"] and forced else None
    return None


def _delete_parts(name: str, args: list[str]) -> tuple[bool, list[str]]:
    """(có cờ đệ quy?, đích). Nhận `rm` kiểu POSIX (cụm cờ chứa r/R, `--recursive`), PowerShell (`-r…` viết tắt của -Recurse), `/s` của cmd."""
    recursive = False
    targets: list[str] = []
    literal = False
    for arg in args:
        low = arg.lower()
        if literal:
            targets.append(arg)
        elif arg == "--":
            literal = True
        elif low in ("/s", "/q") and name in ("rmdir", "rd", "del", "erase"):
            recursive = recursive or low == "/s"
        elif arg.startswith("-") and len(arg) > 1:
            if low == "--recursive":
                recursive = True
            elif name == "rm" and re.fullmatch(r"-[rRfivIdPx]+", arg):
                recursive = recursive or "r" in low
            elif re.fullmatch(r"-r[a-z]*(:.*)?", low):
                recursive = True
        else:
            targets.append(arg)
    return recursive, targets


def tmp_target_ok(target: str, ctx: Context) -> bool:
    """Đích xoá nằm thật sự dưới `<gốc repo>/.tmp/` (ngoại lệ dọn tạm, method/autopilot.md mục 5): xét chuỗi trước khi shell mở rộng."""
    root = ctx.root
    if not root or not target or UNSAFE_PATH_CHARS & set(target):
        return False
    norm = target.replace("\\", "/")
    if ".." in norm.split("/"):
        return False
    full = os.path.normpath(norm if os.path.isabs(norm) else os.path.join(ctx.cwd, norm))
    tmp = os.path.normpath(os.path.join(root, ".tmp"))
    full_n, tmp_n = os.path.normcase(full), os.path.normcase(tmp)
    if not full_n.startswith(tmp_n + os.sep):
        return False
    comps = full_n[len(tmp_n) + 1:].split(os.sep)
    if any(GLOB_CHARS & set(c) for c in comps[:-1]):
        return False
    name = os.path.normcase(MARKER_PARTS[1])
    if GLOB_CHARS & set(comps[-1]):
        if len(comps) == 1 and fnmatch.fnmatchcase(name, comps[-1]):
            return False
        probe = os.path.dirname(full)
    else:
        if len(comps) == 1 and comps[0] == name:
            return False
        probe = full
    real_tmp = os.path.normcase(os.path.realpath(tmp))
    if real_tmp != os.path.normcase(os.path.join(os.path.realpath(root), ".tmp")):
        return False  # chính `.tmp` là liên kết ra nơi khác
    real = os.path.normcase(os.path.realpath(probe))
    if real == os.path.normcase(os.path.realpath(os.path.join(tmp, name))):
        return False  # đích (có thể qua liên kết) là file dấu
    if GLOB_CHARS & set(comps[-1]):
        return real == real_tmp or real.startswith(real_tmp + os.sep)
    return real.startswith(real_tmp + os.sep)


def _segment_item(tokens: list[str], ctx: Context, depth: int) -> str | None:
    while tokens and (tokens[0].lower() in PREFIX_WORDS or ENV_ASSIGN.match(tokens[0])):
        tokens = tokens[1:]
    if not tokens:
        return None
    name, args = _exe_name(tokens[0]), tokens[1:]
    if name in CD_COMMANDS:
        ctx.cwd_changed = True
        return None
    if name in SHELL_WRAPPERS:
        for index, arg in enumerate(args):
            if arg.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c", arg):
                return _analyze(" ".join(args[index + 1:]), ctx, depth + 1) if depth < MAX_UNWRAP else None
        return None
    if name == "git":
        return _git_item(args, ctx)
    if name == "gh":
        plain = [a for a in args if not a.startswith("-")]
        return "main_merge" if plain[:2] == ["pr", "merge"] else None
    if name in DELETE_COMMANDS:
        recursive, targets = _delete_parts(name, args)
        if not recursive:
            return None
        if targets and not ctx.cwd_changed and all(tmp_target_ok(t, ctx) for t in targets):
            return None
        return "irreversible_delete"
    return None


def _analyze(text: str, ctx: Context, depth: int = 0) -> str | None:
    """Mục loại đầu tiên mà `text` (có thể là lệnh ghép) vi phạm và đang bật; None nếu không."""
    for segment in SEPARATORS.split(text):
        item = _segment_item(tokenize(segment), ctx, depth)
        if item and item in ctx.active:
            return item
    return None


# --- sự kiện ----------------------------------------------------------------------------------------------------

def _commands(payload: dict) -> list[str]:
    """Mọi chuỗi lệnh ứng viên (khoá của ba host); danh sách `["bash","-lc","<script>"]` của Codex thì lấy phần script."""
    found: list[str] = []
    containers = []
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        containers.append(tool_input)
    call = payload.get("toolCall")
    if isinstance(call, dict) and isinstance(call.get("args"), dict):
        containers.append(call["args"])
    for container in containers:
        for key in COMMAND_KEYS:
            value = container.get(key)
            if isinstance(value, str):
                found.append(value)
            elif isinstance(value, list) and value and all(isinstance(v, str) for v in value):
                wrapped = len(value) >= 3 and _exe_name(value[0]) in SHELL_WRAPPERS and value[1].lower() in WRAPPER_FLAGS
                found.append(" ".join(value[2:]) if wrapped else " ".join(value))
    return found


def _tool_name(payload: dict) -> str | None:
    name = payload.get("tool_name")
    call = payload.get("toolCall")
    if name is None and isinstance(call, dict):
        name = call.get("name")
    return name if isinstance(name, str) else None


def _event_cwd(payload: dict) -> str:
    sources = [payload]
    for outer in ("tool_input",):
        if isinstance(payload.get(outer), dict):
            sources.append(payload[outer])
    call = payload.get("toolCall")
    if isinstance(call, dict) and isinstance(call.get("args"), dict):
        sources.append(call["args"])
    for source in sources:
        for key in CWD_KEYS:
            if isinstance(source.get(key), str) and source[key]:
                return source[key]
    return os.getcwd()


def reason_for(item: str, broken: bool) -> str:
    lead = "autopilot: file dấu hỏng, " if broken else "autopilot: "
    return "{}'{}' cần người dùng nói trong chat — lệnh không chạy".format(lead, item)


def _evaluate(raw: str) -> str | None:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("payload is not an object")
    name = _tool_name(payload)
    if name is not None and name.lower() not in SHELL_TOOLS:
        return None
    commands = _commands(payload)
    if not commands:
        return None
    cwd = _event_cwd(payload)
    marker = find_marker(cwd)
    if marker is None:
        return None
    active, broken = load_active(marker)
    for text in commands:
        item = _analyze(text, Context(active, cwd))
        if item:
            return reason_for(item, broken)
    return None


def _unparsed_reason(label: str) -> str | None:
    """Đầu vào hỏng hay ngoại lệ: chặn nếu có file dấu từ thư mục của tiến trình (hoặc không dò được), không thì cho qua."""
    try:
        if find_marker(os.getcwd()) is None:
            return None
    except Exception:  # noqa: BLE001 — không dò được thì đóng
        pass
    return "autopilot: hook gặp lỗi ({}) khi có file dấu — lệnh không chạy".format(label)


def _deny(fmt: str, reason: str, stdout: TextIO, stderr: TextIO) -> int:
    if fmt == "antigravity":
        stdout.write(json.dumps({"decision": "deny", "reason": reason}, ensure_ascii=False) + "\n")
        return 0
    stderr.write(reason + "\n")
    return 2


def _allow(fmt: str, stdout: TextIO) -> int:
    if fmt == "antigravity":
        stdout.write("{}\n")
    return 0


def main(argv: list[str] | None = None, stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description="Rào máy autopilot (PreToolUse).")
    parser.add_argument("--format", required=True, choices=FORMATS)
    args = parser.parse_args(argv)
    try:
        reason = _evaluate(stdin.read())
    except Exception as exc:  # JSON hỏng, RecursionError, lỗi nhập check…: đóng khi có file dấu
        if os.environ.get("AUTOPILOT_GUARD_DEBUG", "") not in ("", "0"):
            traceback.print_exc(file=stderr)
        reason = _unparsed_reason(type(exc).__name__)
    return _allow(args.format, stdout) if reason is None else _deny(args.format, reason, stdout, stderr)


def _format_arg(argv: list[str]) -> str:
    for index, arg in enumerate(argv):
        flag, equals, value = arg.partition("=")
        if len(flag) > 2 and "--format".startswith(flag):
            return value if equals else (argv[index + 1] if index + 1 < len(argv) else "")
    return ""


def _last_resort(argv: list[str]) -> int:  # pragma: no cover — lưới cuối khi chính `main` văng
    fmt = "antigravity" if _format_arg(argv) == "antigravity" else "claude"
    try:
        reason = _unparsed_reason("fatal")
        return _allow(fmt, sys.stdout) if reason is None else _deny(fmt, reason, sys.stdout, sys.stderr)
    except BaseException:  # noqa: BLE001
        return 0 if fmt == "antigravity" else 2


if __name__ == "__main__":  # pragma: no cover
    try:
        for stream in (sys.stdin, sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
        code = main()
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        code = _last_resort(sys.argv)
    sys.exit(code)
