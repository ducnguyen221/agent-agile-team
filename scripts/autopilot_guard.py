"""Rào máy autopilot — hook PreToolUse từ chối lệnh shell thuộc danh sách loại (method/autopilot.md mục 5). Chỉ thư viện chuẩn.

Gọi: python autopilot_guard.py --format {claude,codex,antigravity}; đọc JSON sự kiện ở stdin.
Lối dừng tường minh: python autopilot_guard.py --clear <thư mục làm việc> xoá đúng <thư mục>/.tmp/autopilot.json (chỉ file đó; in đường
đã xoá; không có thì báo và thoát 0). Hook nhận ra lệnh này (đúng script của plugin, đúng dạng `--clear <đường>`, không thêm gì khác)
và cho qua kể cả khi có file dấu; mọi đường xoá khác vẫn bị chặn. ĐÂY LÀ RÀO HÀNH VI: phiên con gọi được lệnh này về mặt máy, nhưng luật
cấm — chỉ điều phối (sau `Dừng autopilot.` hay khi thu hồi) hoặc người dùng được gọi, và lần gọi hiện trong transcript để soát.
Chỉ hoạt động khi có file dấu `.tmp/autopilot.json`: tìm từ thư mục chạy lệnh của sự kiện (`tool_input.workdir`/`cwd`,
`toolCall.args.Cwd`, rồi `cwd` của phiên) đi lên, dừng sau cấp đầu tiên có `.git` (thư mục hoặc file `gitdir:` của worktree);
thư mục lệnh và thư mục phiên khác nhau thì thấy file dấu ở đâu cũng bật. Không có file dấu → cho qua (claude/codex thoát 0
không in; antigravity in `{}`). Có file dấu và lệnh khớp mục loại → chặn: claude/codex in lý do ở stderr rồi thoát 2;
antigravity in JSON `deny` ở stdout, thoát 0. Lý do: `autopilot: '<mục loại>' cần người dùng nói trong chat — lệnh không chạy`.

Mục có mẫu lệnh: chỉ `irreversible_delete` — xoá đệ quy ngoài `.tmp/`, mọi lệnh xoá có đích thuộc `.git`, `find -delete`/`-exec rm`,
`Get-ChildItem -Recurse | Remove-Item`, `[IO.Directory]::Delete(…, $true)`, `robocopy /MIR`, `busybox rm`, chuỗi `mv`/`robocopy`/`cp -r` vào `.tmp/` rồi xoá,
`git worktree remove --force` và các lệnh git phá hoàn tác (`reflog expire`, `gc --prune=now`, `update-ref -d`, `push` xoá hay ép, `branch -D`; SPR-20 TK27b).
Lệnh git khác (đẩy thường, tag, gộp, `commit`, `reset`) không bị hook chặn (TK21): luật chữ ở method/git-conventions.md. Các mục khác là rào hành vi.
Ngoài danh sách loại, hook bảo vệ chính file dấu: lệnh shell không chỉ-đọc có đối số trỏ tới file dấu (hoặc `.tmp/` bao nó, hay glob khớp
nó) và công cụ ghi file (`Write`, `Edit`, `MultiEdit`, `NotebookEdit`, `apply_patch`, `write_to_file`, `replace_file_content`…) có đường
đích là file dấu đều bị chặn với lý do `file dấu là rào`. Claude đã đăng ký matcher cho công cụ ghi file ở hooks/hooks.json; Codex và Antigravity chưa.
Danh sách đóng 13 mục lấy từ `_autopilot_rules.AUTOPILOT_EXCLUSIONS` chỉ dùng khi file dấu hỏng (chặn cả 13); file dấu hợp lệ chặn bảy mục
`OPEN_ALWAYS_BLOCKED`. Tiến trình con duy nhất: `git check-ignore -q <file dấu>` khi gặp `git stash -u` hay `git clean -f` (lỗi → coi là không ignore).

Không phân tích chuỗi chương trình tuỳ ý (`awk 'BEGIN{system(…)}'`, `perl -e`, `ruby -e`, `node -e`, `python -c`): giới hạn đã biết.

GIỚI HẠN ĐÃ BIẾT: mẫu là danh sách đóng, tách lệnh thô theo `&&`, `||`, `;`, `|`, `&`, xuống dòng, ngoặc và dấu huyền, không hiểu
dấu nháy (chấp nhận chặn nhầm). Chỉ mở lớp `bash -c`/`pwsh -Command`/`cmd /c` trực tiếp, tối đa MAX_UNWRAP lớp (quá thì chặn).
Đối thủ cố ý (biến môi trường, script, `python -c`, thoát ký tự `g\\it`, ghép chuỗi tên lệnh) lách được; đây là lưới
an toàn, không phải ranh giới bảo mật.

Đóng khi lỗi: có file dấu (dò từ thư mục sự kiện khi đã đọc được sự kiện) mà JSON hỏng hay hook gặp ngoại lệ → chặn; không có
file dấu thì ngoại lệ không chặn việc của người dùng. AUTOPILOT_GUARD_DEBUG=1 in traceback ra stderr.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
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
LEAD_WORDS = frozenset({"if", "then", "else", "elif", "do", "while", "until", "{", "!"})
# Tiền tố bỏ được: tên -> (cờ nhận giá trị ở token kế, số đối số vị trí cần bỏ sau cờ)
PREFIXES = {
    "sudo": (frozenset({"-u", "-g", "-h", "-p", "-C", "-D", "-R", "-T", "-U", "-r", "-t", "--user", "--group", "--host", "--prompt",
                        "--chdir", "--role", "--type"}), 0),
    "env": (frozenset({"-u", "-C", "--unset", "--chdir"}), 0),
    "timeout": (frozenset({"-s", "-k", "--signal", "--kill-after"}), 1),
    "nice": (frozenset({"-n", "--adjustment"}), 0),
    "xargs": (frozenset({"-n", "-I", "-i", "-d", "-a", "-E", "-L", "-l", "-P", "-s", "--max-args", "--delimiter", "--arg-file",
                         "--max-procs", "--max-lines", "--max-chars", "--replace", "--eof"}), 0),
    "stdbuf": (frozenset({"-i", "-o", "-e"}), 0),
    "exec": (frozenset({"-a"}), 0),
    "command": (frozenset(), 0),
    "builtin": (frozenset(), 0),
    "nohup": (frozenset(), 0),
    "setsid": (frozenset(), 0),
    "ionice": (frozenset({"-c", "-n", "-p", "-P", "-u", "--class", "--classdata"}), 0),
    "doas": (frozenset({"-u", "-C"}), 0),
    "time": (frozenset(), 0),
}
ENV_ASSIGN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=")
GIT_DIR_VARS = frozenset({"GIT_DIR", "GIT_WORK_TREE"})
GIT_VALUE_OPTIONS = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"})
DELETE_COMMANDS = frozenset({"rm", "ri", "del", "erase", "rmdir", "rd", "remove-item"})
CD_COMMANDS = frozenset({"cd", "chdir", "pushd", "popd", "set-location", "sl", "push-location", "pop-location"})
CHDIR_OPTIONS = {"env": frozenset({"-C", "--chdir"}), "sudo": frozenset({"-D", "--chdir"})}  # dạng tách rời: giá trị ở token kế
FIND_EXEC = frozenset({"-exec", "-execdir", "-ok", "-okdir"})
MOVE_COMMANDS = frozenset({"mv", "move", "move-item", "mi", "ren", "rename", "rename-item", "rni", "robocopy"})  # đích dưới `.tmp/` → bỏ ngoại lệ dọn tạm cho phần xoá phía sau
COPY_RECURSIVE_NAMES = frozenset({"cp", "copy-item", "cpi"})  # chỉ tính khi có cờ đệ quy
LISTING_COMMANDS = frozenset({"get-childitem", "gci", "ls", "dir"})  # `… -Recurse | Remove-Item`
SEP_KEEP = re.compile("(" + SEPARATORS.pattern + ")")  # như SEPARATORS nhưng giữ dấu ngăn để biết ống dẫn
CHAIN_BREAKS = frozenset({"&&", "||", ";", "&", chr(10), chr(13)})  # dấu ngăn cắt mạch ống dẫn
IO_DELETE = re.compile(r"\[(?:system\.)?io\.directory\]\s*::\s*delete\s*\([^)]*\$true|\.delete\s*\(\s*\$true\s*\)", re.IGNORECASE)
ROBOCOPY_FLAG = re.compile(r"/[A-Za-z]+(?::.*)?")
UNSAFE_PATH_CHARS = set(",$%`~{}()<>!^\"'\n\r;|&")
GLOB_CHARS = set("*?[")
MAX_UNWRAP = 3
MAX_WALK_DEPTH = 6  # độ sâu tối đa khi dò file dấu lồng trong đích dọn .tmp/
NESTED = "nested"  # đơn vị chặn riêng: lồng shell quá sâu, không phân tích được
MARKER = "marker"  # đơn vị chặn riêng: đụng tới chính file dấu
SPECIAL_ITEMS = frozenset({NESTED, MARKER})
WRITE_TOOLS = frozenset({"write", "edit", "multiedit", "notebookedit", "apply_patch", "write_to_file", "replace_file_content",
                         "multi_replace_file_content"})
PATH_KEYS = ("file_path", "path", "notebook_path", "TargetFile")
PATCH_PREFIXES = ("*** Add File: ", "*** Update File: ", "*** Delete File: ", "*** Move to: ")
REDIRECT = re.compile(r"^(?:[0-9]*|&)>>?\|?(.*)$", re.S)
DYNAMIC_CHARS = set("$%`")
REDIRECT_INSIDE = re.compile(r">>?\|?")
LINE_CONTINUATION = re.compile(r"[\\`]\r?\n")
PIPE = re.compile(r"(?<!\|)\|(?!\|)")
EVAL_COMMANDS = frozenset({"eval", "iex", "invoke-expression"})
COPY_COMMANDS = frozenset({"cp", "copy", "copy-item", "cpi"})  # file dấu chỉ là NGUỒN thì được chép (điều phối chép vào thư mục phiên con)
HEREDOC = re.compile(r"<<(?!<)(-?)\s*(?:'([^']+)'|\"([^\"]+)\"|\\?([A-Za-z_][\w.-]*))")
PIPE_INTO_SHELL = re.compile(r"\|\s*(?:sudo\s+)?(?:bash|sh|zsh|dash|ksh|pwsh|powershell)\b")
READ_ONLY_COMMANDS = frozenset({
    "cat", "type", "get-content", "gc", "ls", "dir", "get-childitem", "gci", "stat", "head", "tail", "less", "more", "wc", "grep", "egrep",
    "fgrep", "rg", "select-string", "sls", "file", "diff", "cmp", "sha256sum", "sha1sum", "md5sum", "get-item", "gi", "test-path", "findstr",
    "test", "[", "[[", "jq", "echo", "printf", "write-output", "write-host", "realpath", "readlink", "basename", "dirname", "cut", "sort",
    "uniq", "nl", "od", "hexdump", "xxd", "strings", "get-filehash", "find", "awk"})
READ_ONLY_GIT = frozenset({"status", "log", "diff", "show", "ls-files", "check-ignore", "blame", "ls-tree", "cat-file", "rev-parse",
                           "grep", "describe", "shortlog", "rev-list"})


PYTHON_NAME = re.compile(r"^(?:py|python[0-9.]*)$")


def clear_marker(directory: str, stdout: TextIO, stderr: TextIO) -> int:
    """`--clear <dir>`: xoá đúng `<dir>/.tmp/autopilot.json` (tên so không phân biệt hoa thường), không đụng gì khác."""
    folder = os.path.join(os.path.abspath(directory), MARKER_PARTS[0])
    try:
        names = os.listdir(folder)
    except OSError:
        names = []
    removed = []
    for entry in names:
        path = os.path.join(folder, entry)
        if entry.lower() == MARKER_PARTS[1] and (os.path.isfile(path) or os.path.islink(path)):
            try:
                os.remove(path)
            except OSError as exc:
                stderr.write("không xoá được {}: {}\n".format(path, exc))
                return 1
            removed.append(path)
    if removed:
        for path in removed:
            stdout.write("đã xoá {}\n".format(path))
    else:
        stdout.write("không có file dấu: {}\n".format(os.path.join(folder, MARKER_PARTS[1])))
    return 0


def _is_clear_command(tokens: list[str]) -> bool:
    """`python <plugin>/scripts/autopilot_guard.py --clear <đường>` (hay `sh <plugin>/scripts/autopilot-hook.sh --clear <đường>`): đúng
    script của plugin này, không đối số nào khác, đích không chứa chuyển hướng hay nháy."""
    if len(tokens) < 4 or tokens[-2] != "--clear":
        return False
    target = tokens[-1]
    if not target or target.startswith("-") or set("<>\"'") & set(target):
        return False
    name = _exe_name(tokens[0])
    here = os.path.dirname(os.path.realpath(__file__))
    if PYTHON_NAME.match(name):
        wanted = os.path.join(here, "autopilot_guard.py")
    elif name in ("sh", "bash"):
        wanted = os.path.join(here, "autopilot-hook.sh")
    else:
        return False
    script_at = len(tokens) - 3
    for token in tokens[1:script_at]:
        if not token.startswith("-") and not (token == "utf8" and "-X" in tokens[1:script_at]):
            return False
    script = tokens[script_at]
    return script.startswith("-") is False and os.path.normcase(os.path.realpath(script)) == os.path.normcase(wanted)


def known_exclusions() -> tuple[str, ...]:
    """Danh sách đóng 13 mục từ `_autopilot_rules.AUTOPILOT_EXCLUSIONS`; nạp muộn để lệnh không có file dấu không trả phí nhập."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    from _autopilot_rules import AUTOPILOT_EXCLUSIONS
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
    """(mục đang chặn, file dấu hỏng?). Một chế độ (SPR-20 TK22): file dấu hợp lệ chặn bảy mục luôn-chặn của
    `_autopilot_rules.OPEN_ALWAYS_BLOCKED`; khoá `mode`/`exclusions` (file dấu kiểu cũ) bị bỏ qua. File không đọc được hoặc không
    phải đối tượng JSON → chặn cả 13 mục và báo hỏng."""
    known = known_exclusions()
    try:
        with open(marker, encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return set(known), True
    if not isinstance(data, dict):
        return set(known), True
    from _autopilot_rules import OPEN_ALWAYS_BLOCKED  # nạp muộn như `known_exclusions`
    return set(OPEN_ALWAYS_BLOCKED), False


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


def _resolve_dir(base: str | None, target: str | None) -> str | None:
    """Thư mục đích của `git -C`: đường tuyệt đối dùng thẳng, tương đối ghép với `base`; None khi không biết (đích rỗng, `-`,
    có ký tự mở rộng shell, hoặc tương đối mà `base` không biết)."""
    if not target or target == "-" or UNSAFE_PATH_CHARS & set(target):
        return None
    norm = target.replace("\\", "/")
    if os.path.isabs(norm):
        return os.path.normpath(norm)
    return None if base is None else os.path.normpath(os.path.join(base, norm))


class Context:
    """Trạng thái một lần phân tích: mục đang chặn, thư mục lệnh chạy, gốc repo, thư mục git đang làm việc."""

    def __init__(self, active: set[str], cwd: str, marker: str | None = None) -> None:
        self.active = active
        self.marker = os.path.abspath(marker) if marker else None
        self.cwd = os.path.abspath(cwd)
        self.root = find_repo_root(self.cwd)
        self.in_git = _is_git_path(self.cwd)  # thư mục lệnh (hay đích `cd`) nằm trong `.git`: mọi lệnh xoá/chuyển bị chặn
        self.cwd_changed = False  # đã gặp thao tác đổi thư mục (cd, pushd, env -C…, kể cả trong subshell/bash -c)
        self.tmp_moved = False  # đã gặp `mv`/`robocopy`/`cp -r`… với đích dưới `.tmp/`: phần xoá phía sau không còn ngoại lệ dọn tạm
        self._ignored: bool | None = None

    def marker_ignored(self) -> bool:
        """File dấu bị gitignore (`git check-ignore -q`, chạy ở thư mục lệnh)? Lỗi kiểm → False (coi là không ignore). Nhớ kết quả."""
        if self._ignored is None:
            self._ignored = bool(self.marker) and _marker_ignored(self.cwd, self.marker)
        return self._ignored

    def enter(self) -> None:
        """Ghi nhận một thao tác đổi thư mục. Không tính đường đi (`cd` trong subshell hay vế pipeline không đổi thư mục của lệnh
        sau, `cd` tương đối nối tiếp nhau khó tính đúng): từ đây đường tương đối không giải được nữa, so theo tên (đóng an toàn)."""
        self.cwd_changed = True


def _git_parse(args: list[str]) -> tuple[str, list[str]]:
    """(lệnh con, đối số còn lại) của một lệnh `git`, bỏ các tuỳ chọn toàn cục (`-C <dir>`, `-c k=v`…)."""
    index = 0
    while index < len(args):
        arg = args[index]
        if not arg.startswith("-"):
            return arg, args[index + 1:]
        index += 2 if arg in GIT_VALUE_OPTIONS else 1
    return "", []


def _git_config(args: list[str]) -> dict[str, str]:
    """Các `-c khoá=giá-trị` của tuỳ chọn toàn cục (khoá viết thường)."""
    found: dict[str, str] = {}
    index = 0
    while index < len(args) and args[index].startswith("-"):
        if args[index] == "-c" and index + 1 < len(args):
            key, _, value = args[index + 1].partition("=")
            found[key.lower()] = value.lower()
        index += 2 if args[index] in GIT_VALUE_OPTIONS else 1
    return found


def _marker_ignored(cwd: str, marker: str) -> bool:
    """`git check-ignore -q <file dấu>` chạy ở `cwd`: True khi git nói file bị ignore. Mọi lỗi (không phải repo, git vắng, quá giờ) → False."""
    try:
        done = subprocess.run(["git", "-C", cwd, "check-ignore", "-q", "--", marker], capture_output=True, timeout=10,
                              stdin=subprocess.DEVNULL, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def _git_item(args: list[str], ctx: Context) -> str | None:
    """Mẫu git còn nằm trong hook. (1) Bảo vệ file dấu (`.tmp/`): `stash -a`/`--all` và `clean -f` kèm `-x`/`-X` (kể cả `-c clean.requireForce=false`,
    không cần `-f`) luôn chặn; `stash -u`/`--include-untracked` và `clean -f` chỉ chặn khi file dấu KHÔNG bị gitignore (`git check-ignore -q`,
    lỗi kiểm = không ignore). (2) Phá cơ chế hoàn tác, mục `irreversible_delete`: `worktree remove --force`, `reflog expire|delete`,
    `gc --prune=now`, `prune` kèm `now`, `update-ref -d`, `push` xoá hay ép (`--delete`, `-d`, `--force*`, `-f`, `--mirror`, `--prune`,
    refspec `:ref` hay `+ref`), `branch -D`. Mọi lệnh git khác (đẩy thường, gộp, tag, commit, `reset`) không bị hook chặn:
    luật chữ ở method/git-conventions.md."""
    sub, rest = _git_parse(args)
    config = _git_config(args)
    if sub in ("gc", "prune", "reflog") and any(
        re.fullmatch(r"gc\.(reflogexpire\w*|pruneexpire)", key) and value in ("now", "all", "0") for key, value in config.items()
    ):  # `git -c gc.pruneExpire=now gc`: đặt hạn hết hạn bằng 0 qua cấu hình, tương đương `--prune=now`
        return "irreversible_delete"
    if sub == "stash":
        if "--all" in rest or any(_cluster(a, "a") for a in rest):
            return MARKER
        if "--include-untracked" in rest or any(_cluster(a, "u") for a in rest):
            return None if ctx.marker_ignored() else MARKER
        return None
    if sub == "clean":  # `-x`/`-X` kéo file bị gitignore vào phạm vi xoá; phải kèm `-f`/`--force` (hay requireForce=false) mới thật sự xoá
        opts = rest[:rest.index("--")] if "--" in rest else rest
        no_force_needed = config.get("clean.requireforce") in ("false", "0", "no", "off")
        forced = "--force" in opts or any(_cluster(a, "f") for a in opts) or no_force_needed
        if forced and any(_cluster(a, "xX") for a in opts):
            return MARKER
        dry_run = "--dry-run" in opts or any(_cluster(a, "n") for a in opts)
        return MARKER if forced and not dry_run and not ctx.marker_ignored() else None
    if sub == "worktree":
        forced = "--force" in rest or any(_cluster(a, "f") for a in rest)
        return "irreversible_delete" if rest[:1] == ["remove"] and forced else None
    if sub == "reflog":
        return "irreversible_delete" if rest[:1] in (["expire"], ["delete"]) else None
    if sub == "gc":
        prune_now = any(a.lower() in ("--prune=now", "--prune=all") for a in rest)
        return "irreversible_delete" if prune_now or any(a == "--prune" and nxt.lower() in ("now", "all") for a, nxt in zip(rest, rest[1:])) else None
    if sub == "prune":
        return "irreversible_delete" if "now" in [a.lower() for a in rest] or "--expire=now" in [a.lower() for a in rest] else None
    if sub == "update-ref":
        return "irreversible_delete" if "-d" in rest or "--delete" in rest else None
    if sub == "push":
        skip = False
        for a in rest:
            if skip:
                skip = False
            elif a in ("-o", "--push-option", "--repo", "--receive-pack", "--exec"):
                skip = True
            elif a in ("--delete", "--mirror", "--prune") or a.startswith("--force") or _cluster(a, "fd") or a[:1] in (":", "+"):
                return "irreversible_delete"
        return None
    if sub == "branch":
        deleting = "--delete" in rest or any(_cluster(a, "d") for a in rest)
        forced = "--force" in rest or any(_cluster(a, "f") for a in rest)
        return "irreversible_delete" if any(_cluster(a, "D") for a in rest) or (deleting and forced) else None
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
        elif _colon_value(arg, r"path|p[a-z]*|literalpath|lit[a-z]*") is not None:  # `-Path:x`, `-LiteralPath:x` dính liền
            targets.append(_arg_value(arg))
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
    """Đích xoá nằm thật sự dưới `<gốc repo>/.tmp/` (ngoại lệ dọn tạm, method/autopilot.md mục 5). Glob ở thành phần cuối được
    mở rộng bằng `os.listdir`: mỗi mục khớp phải nằm thật trong `.tmp/` (theo `realpath`) và không phải file dấu."""
    marker_root = os.path.dirname(os.path.dirname(ctx.marker)) if ctx.marker else None
    roots = [r for r in (ctx.root, marker_root if marker_root and _has_git(marker_root) else None) if r]
    return any(_tmp_target_under(target, ctx, r) for r in dict.fromkeys(roots))


def _holds_marker_below(path: str) -> bool:
    """`path` (thư mục) hoặc thư mục con của nó (sâu tối đa MAX_WALK_DEPTH, bỏ `.git`) chứa `.tmp/autopilot.json` (tên không phân biệt hoa
    thường)? Quá giới hạn độ sâu hay lỗi đọc → coi như có (chặn)."""
    if not os.path.isdir(path):
        return False
    failed = [False]

    def onerror(_exc: OSError) -> None:
        failed[0] = True

    base_depth = path.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(path, onerror=onerror):
        if failed[0]:
            return True
        dirnames[:] = [d for d in dirnames if d.lower() != ".git"]
        if os.path.basename(dirpath).lower() == MARKER_PARTS[0] and any(f.lower() == MARKER_PARTS[1] for f in filenames):
            return True
        if dirpath.rstrip(os.sep).count(os.sep) - base_depth >= MAX_WALK_DEPTH and dirnames:
            return True
    return failed[0]


def _tmp_target_under(target: str, ctx: Context, root: str) -> bool:
    if not target or UNSAFE_PATH_CHARS & set(target):
        return False
    norm = target.replace("\\", "/")
    if ".." in norm.split("/"):
        return False
    full = os.path.normpath(norm if os.path.isabs(norm) else os.path.join(ctx.cwd, norm))
    tmp = os.path.normpath(os.path.join(root, ".tmp"))
    full_n, tmp_n = os.path.normcase(full), os.path.normcase(tmp)
    if not full_n.startswith(tmp_n + os.sep):
        return False
    comps = full[len(tmp) + 1:].split(os.sep)
    if any(GLOB_CHARS & set(c) for c in comps[:-1]):
        return False
    name = MARKER_PARTS[1]
    is_glob = bool(GLOB_CHARS & set(comps[-1]))
    if len(comps) == 1 and (fnmatch.fnmatchcase(name, comps[0].lower()) if is_glob else comps[0].lower() == name):
        return False
    real_tmp = os.path.normcase(os.path.realpath(tmp))
    if real_tmp != os.path.normcase(os.path.join(os.path.realpath(root), ".tmp")):
        return False  # chính `.tmp` là liên kết ra nơi khác
    marker_real = os.path.normcase(os.path.realpath(os.path.join(tmp, name)))
    inside = real_tmp + os.sep
    if not is_glob:
        real = os.path.normcase(os.path.realpath(full))
        return real != marker_real and real.startswith(inside) and not _holds_marker_below(real)
    parent = os.path.dirname(full)
    real_parent = os.path.normcase(os.path.realpath(parent))
    if real_parent != real_tmp and not real_parent.startswith(inside):
        return False
    try:
        names = os.listdir(parent)
    except OSError:
        return False
    pattern = comps[-1].lower()
    for entry in names:
        if fnmatch.fnmatchcase(entry.lower(), pattern):
            real = os.path.normcase(os.path.realpath(os.path.join(parent, entry)))
            if entry.lower() == name or real == marker_real or not real.startswith(inside) or _holds_marker_below(real):
                return False
    return True


def _changes_dir(name: str, token: str) -> bool:
    """`env -C dir`/`env -Cdir`/`env --chdir[=dir]`/`sudo -D dir`/`sudo -Ddir`/`sudo --chdir[=dir]` (cả viết tắt `--ch…` của GNU)."""
    short = {"env": "-C", "sudo": "-D"}.get(name)
    if short is None:
        return False
    return token.startswith(short) or token.startswith("--ch") or bool(re.fullmatch(r"-[A-Za-z]+" + short[1], token))


def _strip_prefixes(tokens: list[str], ctx: Context) -> tuple[list[str], bool]:
    """Bỏ tiền tố kèm cờ/đối số của nó (`timeout 60`, `env -i VAR=x`, `sudo -u x`, `nice -n 5`, `xargs -0`…).
    Trả (token còn lại, có gán GIT_DIR/GIT_WORK_TREE?)."""
    redirected = False
    while tokens:
        head = tokens[0]
        assign = ENV_ASSIGN.match(head)
        if assign:
            redirected = redirected or assign.group(1) in GIT_DIR_VARS
            tokens = tokens[1:]
            continue
        if head.lower() in LEAD_WORDS:
            tokens = tokens[1:]
            continue
        name = _exe_name(head)
        if name not in PREFIXES:
            break
        value_opts, positional = PREFIXES[name]
        index = 1
        while index < len(tokens):
            token = tokens[index]
            if token == "--":
                index += 1
                break
            if name == "env" and token == "-S" and index + 1 < len(tokens):  # env -S "git push": chuỗi là lệnh
                tokens = tokenize(tokens[index + 1]) + tokens[index + 2:]
                index = 0
                break
            assign = ENV_ASSIGN.match(token)
            if assign and name in ("env", "sudo"):
                redirected = redirected or assign.group(1) in GIT_DIR_VARS
                index += 1
            elif token.startswith("-") and len(token) > 1:
                if _changes_dir(name, token):  # env -C/--chdir, sudo -D/--chdir (mọi dạng, kể cả dính): đổi thư mục như cd
                    ctx.enter()
                    cluster = bool(re.fullmatch(r"-[A-Za-z]+" + ("C" if name == "env" else "D"), token))
                    index += 2 if token in CHDIR_OPTIONS[name] or cluster else 1
                else:
                    takes = token in value_opts or (bool(re.fullmatch(r"-[A-Za-z]{2,}", token)) and "-" + token[-1] in value_opts)
                    index += 2 if takes else 1
            else:
                break
        else:
            tokens = []
            break
        if index == 0:
            continue
        tokens = tokens[index + positional:]
    return tokens, redirected


def _marker_ref(text: str, ctx: Context) -> bool:
    """`text` (đối số hay đích chuyển hướng) trỏ tới file dấu đang bật, thư mục `.tmp/` bao nó, hay glob khớp nó? So không phân biệt hoa thường.
    Đã có thao tác đổi thư mục thì không giải được đường tương đối: so theo tên (đóng an toàn)."""
    if not text or ctx.marker is None or DYNAMIC_CHARS & set(text):
        return False
    if text.startswith("~"):
        text = os.path.expanduser(text)
    norm = text.replace("\\", "/")
    name = os.path.basename(ctx.marker).lower()
    is_glob = bool(GLOB_CHARS & set(os.path.basename(norm.rstrip("/"))))
    if ctx.cwd_changed:
        comps = [c.lower() for c in norm.split("/") if c not in ("", ".")]
        if not comps:
            return False
        last = comps[-1]
        if last in (name, ".tmp"):
            return True
        return is_glob and fnmatch.fnmatchcase(name, last) and (len(comps) == 1 or comps[-2] == ".tmp")
    full = os.path.normpath(norm if os.path.isabs(norm) else os.path.join(ctx.cwd, norm))
    mark = os.path.normpath(ctx.marker)
    tmp = os.path.dirname(mark)
    low, mark_low, tmp_low = full.lower(), mark.lower(), tmp.lower()
    if low in (mark_low, tmp_low):
        return True
    if is_glob:
        return os.path.dirname(low) == tmp_low and fnmatch.fnmatchcase(name, os.path.basename(low))
    try:
        if os.path.lexists(full):
            real = os.path.realpath(full).lower()
            return real in (os.path.realpath(mark).lower(), os.path.realpath(tmp).lower())
    except OSError:
        return True
    return False


def _covers_marker(text: str, ctx: Context) -> bool:
    """Điểm bắt đầu của `find` là file dấu, `.tmp/` bao nó hay một thư mục tổ tiên của nó? Đã đổi thư mục thì `.`/`..` cũng tính."""
    if ctx.marker is None or not text or DYNAMIC_CHARS & set(text):
        return False
    if _marker_ref(text, ctx):
        return True
    norm = text.replace("\\", "/")
    if ctx.cwd_changed:
        return norm.strip("/") in ("", ".", "..")
    full = os.path.normpath(norm if os.path.isabs(norm) else os.path.join(ctx.cwd, norm)).lower()
    return os.path.normpath(ctx.marker).lower().startswith(full.rstrip(os.sep) + os.sep)


def _find_item(args: list[str], ctx: Context, depth: int) -> str | None:
    if "-delete" in args:
        return "irreversible_delete"
    starts: list[str] = []
    for arg in args:
        if arg.startswith("-") or arg in ("(", ")", "!", ","):
            break
        starts.append(arg)
    for index, arg in enumerate(args):
        if arg in FIND_EXEC:
            rest = args[index + 1:]
            item = _segment_item(rest, ctx, depth)
            if item:
                return item
            stripped, _ = _strip_prefixes(list(rest), Context(set(), ctx.cwd))
            if stripped and not _read_only(_exe_name(stripped[0]), stripped[1:], ctx):
                if any(_covers_marker(t, ctx) for t in (starts or ["."])):
                    return MARKER
            if stripped and _exe_name(stripped[0]) in DELETE_COMMANDS:  # `find … -exec rm {} +`: mọi điểm bắt đầu phải nằm trong `.tmp/`
                if ctx.cwd_changed or not all(tmp_target_ok(t, ctx) for t in (starts or ["."])):
                    return "irreversible_delete"
            return None
    return None


def _read_only(name: str, args: list[str], ctx: Context) -> bool:
    if name in READ_ONLY_COMMANDS:
        return True
    if name == "sed":
        return not any(a == "--in-place" or a.startswith("--in-place=") or (a.startswith("-") and _cluster(a.split("=")[0], "i")) or a.startswith("-i") for a in args)
    if name == "git":
        return _git_parse(args)[0] in READ_ONLY_GIT
    return False


def _marker_item(tokens: list[str], ctx: Context) -> str | None:
    """MARKER nếu lệnh ghi vào file dấu qua chuyển hướng, hoặc là lệnh không chỉ-đọc có đối số trỏ tới file dấu."""
    if ctx.marker is None or not tokens:
        return None
    name = _exe_name(tokens[0])
    ref_at: list[int] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        redirect = REDIRECT.match(token)
        if redirect:
            target = redirect.group(1)
            if not target and index + 1 < len(tokens):
                index += 1
                target = tokens[index]
            if _marker_ref(target, ctx):
                return MARKER
        elif ">" in token and not token.startswith("<"):  # chuyển hướng dính liền: `lệnh>đích`
            if _marker_ref(token[REDIRECT_INSIDE.search(token).end():], ctx):
                return MARKER
        elif index > 0 and not token.startswith("<") and _marker_ref(token, ctx):
            ref_at.append(index)
        index += 1
    if name in COPY_COMMANDS:
        ref_at = [i for i in ref_at if i in _copy_destinations(tokens)]
    return MARKER if ref_at and not _read_only(name, tokens[1:], ctx) else None


_COLON_FLAG = re.compile(r"-([a-z]+):(.*)", re.IGNORECASE | re.DOTALL)


def _colon_value(token: str, names: str) -> str | None:
    """Giá trị của cờ PowerShell dạng dính `-Tên:giá-trị` khi tên khớp mẫu `names` (không phân biệt hoa thường); không khớp → None."""
    found = _COLON_FLAG.fullmatch(token)
    if found and re.fullmatch(names, found.group(1).lower()):
        return found.group(2).strip("'\"")
    return None


def _arg_value(token: str) -> str:
    """Đường thật của một đối số: bỏ phần `-Destination:`/`-Path:`/`-LiteralPath:` dính liền nếu có."""
    value = _colon_value(token, r"dest[a-z]*|path|p[a-z]*|literalpath|lit[a-z]*")
    return token if value is None else value


def _copy_destinations(tokens: list[str]) -> set[int]:
    """Vị trí token là ĐÍCH của cp/Copy-Item/Move-Item: giá trị sau `-Destination`/`-t`/`--target-directory` (cả dạng dính
    `-Destination:x`), không thì đối số vị trí cuối. `-Path:x`/`-LiteralPath:x` dính liền là NGUỒN, không phải đối số vị trí."""
    explicit: set[int] = set()
    positional: list[int] = []
    for index in range(1, len(tokens)):
        token = tokens[index]
        low = token.lower()
        before = tokens[index - 1].lower() if index > 1 else ""
        if before in ("-t", "--target-directory") or re.fullmatch(r"-dest[a-z]*", before):
            explicit.add(index)
        elif low.startswith("--target-directory=") or _colon_value(token, r"dest[a-z]*") is not None:
            explicit.add(index)
        elif not token.startswith("-") or _colon_value(token, r"path|p[a-z]*|literalpath|lit[a-z]*") is not None:
            positional.append(index)
    return explicit or ({positional[-1]} if positional else set())


def _heredoc_marks(line: str, quote: str) -> tuple[list["re.Match[str]"], str]:
    """Các `<<`/`<<-` (không phải `<<<`) nằm NGOÀI nháy đơn/kép và ngoài comment `#` của một dòng; trả kèm trạng thái nháy
    còn mở cuối dòng (chuỗi nhiều dòng)."""
    marks: list["re.Match[str]"] = []
    index = 0
    while index < len(line):
        char = line[index]
        if quote:
            if char == "\\" and quote == '"':
                index += 2
                continue
            if char == quote:
                quote = ""
            index += 1
        elif char in "'\"":
            quote = char
            index += 1
        elif char == "\\":
            index += 2
        elif char == "#" and (index == 0 or line[index - 1].isspace()):
            break
        elif line.startswith("<<<", index):
            index += 3
        elif line.startswith("<<", index):
            mark = HEREDOC.match(line, index)
            marks.append(mark) if mark else None
            index = mark.end() if mark else index + 2
        else:
            index += 1
    return marks, quote


def _substitutions(body: str) -> list[str]:
    """Nội dung các `$(…)` (ngoặc cân bằng, bỏ `$((…))`) và cặp dấu huyền trong `body`: thứ shell sẽ chạy khi mở rộng thân heredoc."""
    found: list[str] = []
    index = 0
    while index < len(body):
        if body.startswith("$(", index) and not body.startswith("$((", index):
            depth, end = 1, index + 2
            while end < len(body) and depth:
                depth += (body[end] == "(") - (body[end] == ")")
                end += 1
            found.append(body[index + 2:end - 1 if depth == 0 else end])
            index = end
        elif body[index] == "`":
            end = body.find("`", index + 1)
            end = len(body) if end < 0 else end
            found.append(body[index + 1:end])
            index = end + 1
        else:
            index += 1
    return found


def _strip_heredoc_bodies(text: str) -> str:
    """Thân heredoc đưa vào trình thông dịch không phải shell (`python -`, `node -`, `cat >`) là dữ liệu, không phân tích như lệnh;
    đưa vào `bash`/`sh`/`pwsh`/eval (kể cả `cat <<EOF | bash`) thì giữ lại để xét như lệnh lồng. Chỉ nhận `<<` ngoài nháy và comment;
    heredoc không có dòng kết thúc khớp đúng nhãn thì giữ nguyên thân để phân tích. Nhãn không nháy (`<<X`, `<<-X`): shell vẫn mở rộng
    `$(…)` và dấu huyền trong thân nên các lệnh đó được trích ra phân tích; nhãn có nháy (`<<'X'`, `<<"X"`, `<<\\X`) thì bỏ hẳn thân."""
    lines = text.split("\n")
    out: list[str] = []
    index = 0
    quote = ""
    while index < len(lines):
        line = lines[index]
        out.append(line)
        index += 1
        marks, quote = _heredoc_marks(line, quote)
        if not marks:
            continue
        stage, _ = _strip_prefixes(tokenize(SEPARATORS.split(line[:marks[0].start()])[-1]), Context(set(), "."))
        reads_shell = bool(stage) and _exe_name(stage[0]) in SHELL_WRAPPERS | EVAL_COMMANDS
        reads_shell = reads_shell or bool(PIPE_INTO_SHELL.search(line[marks[-1].end():]))
        for mark in marks:
            delimiter = mark.group(2) or mark.group(3) or mark.group(4)
            body: list[str] = []
            closed = False
            while index < len(lines):
                current = lines[index]
                index += 1
                if (current.lstrip("\t") if mark.group(1) else current).rstrip("\r") == delimiter:
                    closed = True
                    break
                body.append(current)
            if reads_shell or not closed:
                out.extend(body)
            elif "\\" not in mark.group(0) and not (mark.group(2) or mark.group(3)):
                out.extend(_substitutions("\n".join(body)))  # nhãn không nháy: shell mở rộng $(…) và dấu huyền trong thân
    return "\n".join(out)


def _join_and_strip(text: str) -> str:
    """Nối dòng (dấu gạch ngược hay dấu huyền + xuống dòng) TRƯỚC khi dò heredoc (để `bash` + gạch ngược + xuống dòng + `<<EOF` vẫn thấy `bash`), bỏ thân heredoc
    của trình không phải shell, rồi nối dòng thêm một lần cho phần còn lại. Hệ quả chấp nhận: dấu huyền/gạch ngược cuối dòng trong thân
    heredoc có nháy cũng bị nối, nên thân đó có thể không còn dòng kết thúc riêng và bị phân tích (chặn nhầm, an toàn)."""
    return LINE_CONTINUATION.sub(" ", _strip_heredoc_bodies(LINE_CONTINUATION.sub(" ", text)))


def _in_tmp_name(path: str) -> bool:
    """Đường có thành phần `.tmp` (đích chuyển/chép vào vùng tạm)."""
    return ".tmp" in [c.lower() for c in path.replace("\\", "/").split("/")]


def _is_git_path(path: str) -> bool:
    """Đích xoá thuộc `.git`: có thành phần đúng `.git`, hay glob khớp `.git` (bắt đầu bằng dấu chấm như `.g*`, hoặc có từ 3 ký tự thường như
    `?git`, `[.]git`; glob chỉ toàn ký tự đại diện như `*` không tính)."""
    for comp in path.replace("\\", "/").split("/"):
        low = comp.lower()
        if low == ".git":
            return True
        if GLOB_CHARS & set(low) and fnmatch.fnmatchcase(".git", low):
            if low.startswith(".") or len(low.translate({ord(c): None for c in "*?[]"})) >= 3:
                return True
    return False


def _moves_into_tmp(tokens: list[str]) -> bool:
    """`mv`/`move`/`Move-Item`/`ren`/`Rename-Item`/`robocopy`, hay `cp -r`/`Copy-Item -Recurse`, có ĐÍCH dưới `.tmp/`: chuyển/chép cây vào vùng tạm
    rồi xoá ở đó là cách đưa `.git` hay file đang theo dõi ra khỏi cây mà không bị coi là xoá ngoài `.tmp/`."""
    if not tokens:
        return False
    name, args = _exe_name(tokens[0]), tokens[1:]
    if name == "robocopy":
        positional = [a for a in args if not ROBOCOPY_FLAG.fullmatch(a) and not a.startswith("-")]
        return len(positional) > 1 and _in_tmp_name(positional[1])
    if name in COPY_RECURSIVE_NAMES:
        flags = [a for a in args if a.startswith("-")]
        if name == "cp":
            recursive = any(re.fullmatch(r"-[A-Za-z]*[rRa][A-Za-z]*", a) or a.lower() == "--recursive" for a in flags)
        else:
            recursive = any(re.fullmatch(r"-r[a-z]*", a.lower()) for a in flags)
        if not recursive:
            return False
    elif name not in MOVE_COMMANDS:
        return False
    return any(_in_tmp_name(_arg_value(tokens[i])) for i in _copy_destinations(tokens))


def _git_source_moved(tokens: list[str]) -> bool:
    """`mv`/`move`/`Move-Item`/`ren`/`Rename-Item`/`robocopy` có NGUỒN thuộc `.git`: đưa cơ chế hoàn tác ra khỏi cây ngay cả khi đích không ở
    `.tmp/` hay phần xoá nằm ở lệnh riêng (`mv .git .tmp/x/g`, rồi `rm -rf .tmp/x`). Sao chép (`cp`, `Copy-Item`) không tính: nguồn còn nguyên;
    sao chép vào `.tmp/` rồi xoá ở đó đã bị `_moves_into_tmp` chặn."""
    if not tokens:
        return False
    name, args = _exe_name(tokens[0]), tokens[1:]
    if name == "robocopy":
        positional = [a for a in args if not ROBOCOPY_FLAG.fullmatch(a) and not a.startswith("-")]
        return bool(positional) and _is_git_path(positional[0])
    if name not in MOVE_COMMANDS:
        return False
    destinations = _copy_destinations(tokens)
    return any(
        _is_git_path(_arg_value(tokens[i])) for i in range(1, len(tokens))
        if i not in destinations and (not tokens[i].startswith("-") or _arg_value(tokens[i]) != tokens[i])
    )


def _recursive_listing(name: str, args: list[str]) -> list[str] | None:
    """`Get-ChildItem`/`gci`/`ls`/`dir` có cờ đệ quy: danh sách đường nó liệt kê (rỗng = thư mục hiện tại); không phải → None."""
    if name not in LISTING_COMMANDS:
        return None
    if not any(a.startswith("-") and re.fullmatch(r"-r[a-z]*", a.lower()) for a in args):
        return None
    return [a for a in args if not a.startswith("-")]


def _robocopy_purge_item(args: list[str], ctx: Context) -> str | None:
    """`robocopy … /MIR` (hay `/PURGE`) xoá ở đích mọi thứ không có ở nguồn: chỉ cho qua khi đích nằm trong `.tmp/`."""
    if not any(a.lower() in ("/mir", "/purge") for a in args):
        return None
    positional = [a for a in args if not ROBOCOPY_FLAG.fullmatch(a) and not a.startswith("-")]
    if len(positional) > 1 and not ctx.cwd_changed and tmp_target_ok(positional[1], ctx):
        return None
    return "irreversible_delete"


def _segment_item(tokens: list[str], ctx: Context, depth: int) -> str | None:
    tokens, _ = _strip_prefixes(tokens, ctx)
    if not tokens:
        return None
    if _is_clear_command(tokens):  # lối dừng tường minh của điều phối (rào hành vi, xem docstring)
        return None
    item = _command_item(tokens, ctx, depth) or _marker_item(tokens, ctx)
    if _moves_into_tmp(tokens):
        ctx.tmp_moved = True  # từ đây phần xoá phía sau (cùng chuỗi) không còn ngoại lệ dọn `.tmp/`
    return item


def _nested_string(text: str, ctx: Context, depth: int) -> str | None:
    """Chuỗi được đưa vào shell (eval, ống vào bash): xét như lệnh lồng; lồng quá MAX_UNWRAP lớp thì chặn."""
    if not text.strip():
        return None
    if depth >= MAX_UNWRAP:
        return NESTED
    return _analyze(text, ctx, depth + 1)


def _pipe_to_shell(text: str, ctx: Context, depth: int) -> str | None:
    """`echo "git push" | bash`: vế trước ống (bỏ tên lệnh đầu) là chuỗi đưa vào shell."""
    parts = PIPE.split(text)
    for index in range(1, len(parts)):
        stage, _ = _strip_prefixes(tokenize(re.split(r"&&|;|\n", parts[index])[0]), Context(set(), ctx.cwd))
        if not stage:
            continue
        name = _exe_name(stage[0])
        takes_script = any(a.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c[a-z]*", a) for a in stage[1:])
        if (name in SHELL_WRAPPERS or name in EVAL_COMMANDS) and not takes_script:
            source = tokenize(re.split(r"&&|;|\n|\|\|", parts[index - 1])[-1])
            item = _nested_string(" ".join(source[1:]), ctx, depth)
            if item:
                return item
    return None


def _command_item(tokens: list[str], ctx: Context, depth: int) -> str | None:
    name, args = _exe_name(tokens[0]), tokens[1:]
    if name in CD_COMMANDS:
        ctx.enter()
        ctx.in_git = ctx.in_git or any(_is_git_path(_arg_value(a)) for a in args)
        return None
    if name in EVAL_COMMANDS:
        return _nested_string(" ".join(args), ctx, depth)
    if name in SHELL_WRAPPERS:
        if "<<<" in args and args.index("<<<") + 1 < len(args):  # bash <<< "git push"
            return _nested_string(" ".join(args[args.index("<<<") + 1:]), ctx, depth)
        for index, arg in enumerate(args):
            if arg.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c[a-z]*", arg):
                return _analyze(" ".join(args[index + 1:]), ctx, depth + 1) if depth < MAX_UNWRAP else NESTED
        return None
    if name == "busybox" and args:  # `busybox rm -rf x`: applet là lệnh thật
        return _command_item(args, ctx, depth)
    if name == "git":
        return _git_item(args, ctx)
    if name == "find":
        return _find_item(args, ctx, depth)
    if _git_source_moved(tokens):
        return "irreversible_delete"
    if ctx.in_git and (name in DELETE_COMMANDS or name in MOVE_COMMANDS):  # `cd .git && rm objects/pack/*`: đường tương đối trỏ vào `.git`
        return "irreversible_delete"
    if name == "robocopy":
        return _robocopy_purge_item(args, ctx)
    if name in DELETE_COMMANDS:
        recursive, targets = _delete_parts(name, args)
        if any(_is_git_path(t) for t in targets):  # xoá thứ thuộc `.git` (kể cả không đệ quy): phá cơ chế hoàn tác
            return "irreversible_delete"
        if not recursive:
            return None
        if targets and not ctx.cwd_changed and not ctx.tmp_moved and all(tmp_target_ok(t, ctx) for t in targets):
            return None
        return "irreversible_delete"
    return None


def _analyze(text: str, ctx: Context, depth: int = 0) -> str | None:
    """Mục loại đầu tiên mà `text` (có thể là lệnh ghép) vi phạm và đang bật; None nếu không."""
    text = _join_and_strip(text)  # nối dòng `git \` + xuống dòng; bỏ thân heredoc của trình không phải shell
    item = _pipe_to_shell(text, ctx, depth)
    if item:
        return item
    if "irreversible_delete" in ctx.active and IO_DELETE.search(text):  # `[IO.Directory]::Delete(…, $true)`, `(Get-Item x).Delete($true)`: không đọc được đích
        return "irreversible_delete"
    parts = SEP_KEEP.split(text)  # [lệnh, dấu ngăn, lệnh, …]
    listing: list[str] | None = None  # đường mà một `Get-ChildItem -Recurse` phía trước ống dẫn đang liệt kê
    for index in range(0, len(parts), 2):
        if index and parts[index - 1] in CHAIN_BREAKS:
            listing = None
        tokens = tokenize(parts[index])
        item = _segment_item(list(tokens), ctx, depth)
        stripped, _ = _strip_prefixes(list(tokens), Context(set(), ctx.cwd))
        if stripped and not item:
            name = _exe_name(stripped[0])
            paths = _recursive_listing(name, stripped[1:])
            if paths is not None:
                listing = paths
            elif listing is not None and name in DELETE_COMMANDS and not _delete_parts(name, stripped[1:])[1]:
                if not (listing and not ctx.cwd_changed and all(tmp_target_ok(t, ctx) for t in listing)):
                    item = "irreversible_delete"  # `Get-ChildItem … -Recurse | Remove-Item`: xoá đệ quy qua ống dẫn
        if item and (item in SPECIAL_ITEMS or item in ctx.active):
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


def _event_dirs(payload: dict) -> tuple[str, str]:
    """(thư mục chạy lệnh, thư mục phiên). Thư mục lệnh: khoá cấp công cụ (`workdir`, `cwd`, `Cwd`) trước, rồi `cwd` của phiên,
    rồi thư mục tiến trình; khoá tương đối ghép với thư mục phiên."""
    session = payload.get("cwd") if isinstance(payload.get("cwd"), str) and payload.get("cwd") else None
    sources = []
    if isinstance(payload.get("tool_input"), dict):
        sources.append(payload["tool_input"])
    call = payload.get("toolCall")
    if isinstance(call, dict) and isinstance(call.get("args"), dict):
        sources.append(call["args"])
    tool = None
    for source in sources:
        for key in CWD_KEYS:
            if isinstance(source.get(key), str) and source[key]:
                tool = source[key]
                break
        if tool:
            break
    if tool and session and not os.path.isabs(tool):
        tool = os.path.join(session, tool)
    command_dir = tool or session or os.getcwd()
    return command_dir, session or command_dir


def reason_for(item: str, broken: bool) -> str:
    if item == MARKER:
        return "autopilot: file dấu là rào — chỉ người dùng hoặc lệnh dừng mới xoá"
    if item == NESTED:
        return "autopilot: lệnh lồng quá {} lớp shell, không phân tích được — cần người dùng nói trong chat — lệnh không chạy".format(MAX_UNWRAP)
    lead = "autopilot: file dấu hỏng, " if broken else "autopilot: "
    return "{}'{}' cần người dùng nói trong chat — lệnh không chạy".format(lead, item)


class _Failed(Exception):
    """Ngoại lệ sau khi đã biết thư mục sự kiện: mang theo các thư mục để dò file dấu."""

    def __init__(self, dirs: tuple[str, ...], label: str) -> None:
        super().__init__(label)
        self.dirs = dirs
        self.label = label


def _path_candidates(args: list[str], base: str) -> list[str]:
    """Đối số trông như đường (có dấu `/` `\\`, bắt đầu bằng `.` hay `~`) của lệnh không chỉ-đọc, kể cả đích chuyển hướng: để dò file dấu."""
    found: list[str] = []
    for arg in args:
        redirect = REDIRECT.match(arg)
        text = redirect.group(1) if redirect else arg
        if not text or text.startswith("-") or DYNAMIC_CHARS & set(text):
            continue
        if text.startswith("~"):
            text = os.path.expanduser(text)
        if "/" in text or "\\" in text or text.startswith(".") or os.path.isabs(text):
            resolved = _resolve_dir(base, text)
            if resolved:
                found.append(resolved)
    return found


def _extra_dirs(text: str, base: str, depth: int = 0) -> list[str]:
    """Thư mục và đường mà lệnh trỏ tới (`git -C <dir>`, `cd <dir>`, đối số đường của lệnh không chỉ-đọc) để dò thêm file dấu khi lệnh chạy
    từ ngoài cây có file dấu: đi lên từ chính đường đó tới thư mục có `.git`."""
    scratch = Context(set(), base)
    found: list[str | None] = []
    for segment in SEPARATORS.split(_join_and_strip(text)):
        tokens, _ = _strip_prefixes(tokenize(segment), scratch)
        if not tokens:
            continue
        name, args = _exe_name(tokens[0]), tokens[1:]
        if name == "git":
            index = 0
            while index < len(args) and args[index].startswith("-"):
                if args[index] == "-C" and index + 1 < len(args):
                    found.append(_resolve_dir(base, args[index + 1]))
                index += 2 if args[index] in GIT_VALUE_OPTIONS else 1
        elif name in CD_COMMANDS:
            found.append(_resolve_dir(base, next((a for a in args if not a.startswith("-")), None)))
        elif name in SHELL_WRAPPERS and depth < MAX_UNWRAP:
            for index, arg in enumerate(args):
                if arg.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c[a-z]*", arg):
                    found.extend(_extra_dirs(" ".join(args[index + 1:]), base, depth + 1))
                    break
        if name != "git" and name not in CD_COMMANDS and (name == "find" or not _read_only(name, args, scratch)):
            found.extend(_path_candidates(args, base))
        if tokens and any(REDIRECT.match(t) for t in tokens):  # `lệnh > đích` kể cả lệnh chỉ-đọc như echo
            found.extend(_path_candidates([t for t in tokens if REDIRECT.match(t)], base))
            for index, token in enumerate(tokens[:-1]):
                if REDIRECT.match(token) and not REDIRECT.match(token).group(1):
                    found.extend(_path_candidates([tokens[index + 1]], base))
    return [d for d in found if d]


def _write_paths(payload: dict) -> list[str]:
    """Đường đích của công cụ ghi file: giá trị chuỗi ở khoá đường (mọi độ sâu) cộng dòng vá của Codex."""
    found: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in PATH_KEYS and isinstance(value, str):
                    found.append(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, str):
            for line in node.splitlines():
                line = line.lstrip()
                for prefix in PATCH_PREFIXES:
                    if line.startswith(prefix):
                        found.append(line[len(prefix):].strip())

    walk(payload)
    return found


def _is_marker_path(path: str, base: str, marker: str) -> bool:
    norm = path.replace("\\", "/")
    full = os.path.normpath(norm if os.path.isabs(norm) else os.path.join(base, norm))
    mark = os.path.normpath(marker)
    if full.lower() == mark.lower():
        return True
    return os.path.lexists(full) and os.path.realpath(full).lower() == os.path.realpath(mark).lower()


def _evaluate(raw: str) -> str | None:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("payload is not an object")
    dirs: tuple[str, ...] = (os.getcwd(),)
    try:
        dirs = _event_dirs(payload)
        name = _tool_name(payload)
        command_dir, session_dir = dirs
        markers: list[str] = []

        def add(found: str | None) -> None:
            if found and all(os.path.normcase(found) != os.path.normcase(m) for m in markers):
                markers.append(found)

        add(find_marker(command_dir))
        if session_dir != command_dir:
            add(find_marker(session_dir))
        if name is not None and name.lower() in WRITE_TOOLS:
            paths = _write_paths(payload)
            for path in paths:  # đường tuyệt đối vào cây khác: dò file dấu đi lên từ chính đường đó
                add(find_marker(os.path.normpath(os.path.expanduser(path) if path.startswith("~") else (
                    path if os.path.isabs(path) else os.path.join(command_dir, path)))))
            if any(_is_marker_path(p, command_dir, m) for m in markers for p in paths):
                return reason_for(MARKER, False)
            return None
        if name is not None and name.lower() not in SHELL_TOOLS:
            return None
        commands = _commands(payload)
        if not commands:
            return None
        for text in commands:
            for directory in _extra_dirs(text, command_dir):
                add(find_marker(directory))
        for marker in markers:
            active, broken = load_active(marker)
            for text in commands:
                item = _analyze(text, Context(active, command_dir, marker))
                if item:
                    return reason_for(item, broken)
        return None
    except Exception as exc:
        raise _Failed(dirs, type(exc).__name__) from exc


def _unparsed_reason(label: str, dirs: tuple[str, ...]) -> str | None:
    """Đầu vào hỏng hay ngoại lệ: chặn nếu có file dấu từ một trong `dirs` (hoặc không dò được), không thì cho qua."""
    try:
        if all(find_marker(d) is None for d in dirs):
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
    parser.add_argument("--format", choices=FORMATS)
    parser.add_argument("--clear", metavar="DIR", help="xoá <DIR>/.tmp/autopilot.json rồi thoát")
    args = parser.parse_args(argv)
    if args.clear is not None:
        return clear_marker(args.clear, stdout, stderr)
    if args.format is None:
        parser.error("the following arguments are required: --format")
    debug = os.environ.get("AUTOPILOT_GUARD_DEBUG", "") not in ("", "0")
    reason = None
    try:
        reason = _evaluate(stdin.read())
    except _Failed as failed:
        if debug:
            traceback.print_exc(file=stderr)
        reason = _unparsed_reason(failed.label, failed.dirs)
    except Exception as exc:  # JSON hỏng, đầu vào không đọc được: chưa có thư mục sự kiện, dò từ thư mục tiến trình
        if debug:
            traceback.print_exc(file=stderr)
        reason = _unparsed_reason(type(exc).__name__, (os.getcwd(),))
    if reason is None:
        return _allow(args.format, stdout)
    return _deny(args.format, reason, stdout, stderr)


def _format_arg(argv: list[str]) -> str:
    for index, arg in enumerate(argv):
        flag, equals, value = arg.partition("=")
        if len(flag) > 2 and "--format".startswith(flag):
            return value if equals else (argv[index + 1] if index + 1 < len(argv) else "")
    return ""


def _last_resort(argv: list[str]) -> int:  # pragma: no cover — lưới cuối khi chính `main` văng
    fmt = "antigravity" if _format_arg(argv) == "antigravity" else "claude"
    try:
        reason = _unparsed_reason("fatal", (os.getcwd(),))
        return _allow(fmt, sys.stdout) if reason is None else _deny(fmt, reason, sys.stdout, sys.stderr)
    except BaseException:  # noqa: BLE001
        return 0 if fmt == "antigravity" else 2


if __name__ == "__main__":  # pragma: no cover
    try:
        for stream in (sys.stdin, sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
        code = _last_resort(sys.argv) if sys.version_info < (3, 9) else main()  # Python quá cũ: chỉ dò file dấu, không phân tích
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        code = _last_resort(sys.argv)
    sys.exit(code)
