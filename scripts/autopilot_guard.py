"""Rào máy autopilot — hook PreToolUse từ chối lệnh shell thuộc danh sách loại (method/autopilot.md mục 5). Chỉ thư viện chuẩn.

Gọi: python autopilot_guard.py --format {claude,codex,antigravity}; đọc JSON sự kiện ở stdin.
Chỉ hoạt động khi có file dấu `.tmp/autopilot.json`: tìm từ thư mục chạy lệnh của sự kiện (`tool_input.workdir`/`cwd`,
`toolCall.args.Cwd`, rồi `cwd` của phiên) đi lên, dừng sau cấp đầu tiên có `.git` (thư mục hoặc file `gitdir:` của worktree);
thư mục lệnh và thư mục phiên khác nhau thì thấy file dấu ở đâu cũng bật. Không có file dấu → cho qua (claude/codex thoát 0
không in; antigravity in `{}`). Có file dấu và lệnh khớp mục loại → chặn: claude/codex in lý do ở stderr rồi thoát 2;
antigravity in JSON `deny` ở stdout, thoát 0. Lý do: `autopilot: '<mục loại>' cần người dùng nói trong chat — lệnh không chạy`.

Mục có mẫu lệnh: push, tag, main_merge, irreversible_delete, branch_merge_local. Các mục khác là rào hành vi (không có mẫu).
Tên mục lấy từ `check.AUTOPILOT_EXCLUSIONS` (một nguồn; test ghim đúng 13 mục). Không gọi tiến trình con; nhánh hiện tại đọc từ
file `.git/HEAD` của thư mục mà lệnh git thật sự chạy (theo `cd`, `git -C`; không xác định được thì coi là nhánh chính).

GIỚI HẠN ĐÃ BIẾT: mẫu là danh sách đóng, tách lệnh thô theo `&&`, `||`, `;`, `|`, `&`, xuống dòng, ngoặc và dấu huyền, không hiểu
dấu nháy (chấp nhận chặn nhầm). Chỉ mở lớp `bash -c`/`pwsh -Command`/`cmd /c` trực tiếp, tối đa MAX_UNWRAP lớp (quá thì chặn).
Đối thủ cố ý (biến môi trường, script, alias git, `python -c`, thoát ký tự `g\\it`, ghép chuỗi tên lệnh) lách được; đây là lưới
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
    "time": (frozenset(), 0),
}
ENV_ASSIGN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=")
GIT_DIR_VARS = frozenset({"GIT_DIR", "GIT_WORK_TREE"})
MAIN_BRANCHES = ("main", "master")
GIT_VALUE_OPTIONS = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"})
GIT_REDIRECT_OPTIONS = frozenset({"--git-dir", "--work-tree"})  # đổi nơi git thật sự làm việc: không đoán được thư mục
TAG_READ_ONLY = frozenset({"-l", "--list", "-v", "--verify", "--contains", "--no-contains", "--merged", "--no-merged", "--points-at"})
DELETE_COMMANDS = frozenset({"rm", "ri", "del", "erase", "rmdir", "rd", "remove-item"})
CD_COMMANDS = frozenset({"cd", "chdir", "pushd", "popd", "set-location", "sl", "push-location", "pop-location"})
POP_COMMANDS = frozenset({"popd", "pop-location"})  # về thư mục không biết
CHDIR_OPTIONS = {"env": frozenset({"-C", "--chdir"}), "sudo": frozenset({"-D", "--chdir"})}  # tiền tố đổi thư mục như cd
FIND_EXEC = frozenset({"-exec", "-execdir", "-ok", "-okdir"})
UNSAFE_PATH_CHARS = set(",$%`~{}()<>!^\"'\n\r;|&")
GLOB_CHARS = set("*?[")
MAX_UNWRAP = 3
NESTED = "nested"  # đơn vị chặn riêng: lồng shell quá sâu, không phân tích được


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


def _resolve_dir(base: str | None, target: str | None) -> str | None:
    """Thư mục đích của `cd`/`git -C`: ghép với `base`; None khi không biết (đích rỗng, `-`, có ký tự mở rộng shell, base chưa biết)."""
    if base is None or not target or target == "-" or UNSAFE_PATH_CHARS & set(target):
        return None
    norm = target.replace("\\", "/")
    return os.path.normpath(norm if os.path.isabs(norm) else os.path.join(base, norm))


class Context:
    """Trạng thái một lần phân tích: mục đang chặn, thư mục lệnh chạy, gốc repo, thư mục git đang làm việc."""

    def __init__(self, active: set[str], cwd: str) -> None:
        self.active = active
        self.cwd = os.path.abspath(cwd)
        self.root = find_repo_root(self.cwd)
        self.dir: str | None = self.cwd  # thư mục sau `cd` gần nhất (để ghép `cd` tương đối); None = không biết
        self.visited: list[str | None] = [self.cwd]  # mọi thư mục từng vào, gồm cả `cd` trong subshell/pipeline/bash -c
        self.forced_main = False  # đã gặp `git checkout|switch main|master` trong lệnh ghép
        self.cwd_changed = False  # đã gặp `cd`: đường tương đối của lệnh xoá không còn đáng tin
        self._heads: dict[str, bool] = {}

    def enter(self, directory: str | None) -> None:
        """Ghi nhận một lần đổi thư mục (cd, pushd, env -C…). `cd` trong subshell hay vế pipeline không đổi thư mục của lệnh sau,
        nên lệnh git sau đó xét MỌI thư mục từng vào: một nơi đang ở main (hay không biết) là coi như main."""
        self.cwd_changed = True
        self.dir = directory
        self.visited.append(directory)

    def on_main(self, directories: list[str | None]) -> bool:
        """Nhánh hiện tại của repo chứa một trong `directories` là main/master? Không xác định được → True (đóng an toàn)."""
        return self.forced_main or any(self._dir_on_main(d) for d in directories)

    def _dir_on_main(self, directory: str | None) -> bool:
        if directory is None:
            return True
        root = find_repo_root(directory)
        if root is None:
            return True
        if root not in self._heads:
            self._heads[root] = self._read_head_is_main(root)
        return self._heads[root]

    @staticmethod
    def _read_head_is_main(root: str) -> bool:
        """Đọc `.git/HEAD` (hỗ trợ worktree: `.git` là file `gitdir:`). Không xác định được → True."""
        git = os.path.join(root, ".git")
        try:
            if os.path.isfile(git):
                with open(git, encoding="utf-8") as handle:
                    first = handle.readline().strip()
                if not first.startswith("gitdir:"):
                    return True
                git = os.path.normpath(os.path.join(root, first[len("gitdir:"):].strip()))
            with open(os.path.join(git, "HEAD"), encoding="utf-8") as handle:
                head = handle.readline().strip()
        except (OSError, ValueError):
            return True
        prefix = "ref: refs/heads/"
        if not head.startswith(prefix) or not head[len(prefix):]:
            return True
        return head[len(prefix):] in MAIN_BRANCHES


def _git_parse(args: list[str], ctx: Context, redirected: bool) -> tuple[str, list[str], list[str | None]]:
    """(lệnh con, đối số còn lại, các thư mục git có thể làm việc). Không có `-C`: mọi thư mục từng vào (`ctx.visited`);
    `-C <dir>` đọc nhánh của chính `<dir>` (ghép với từng thư mục từng vào nếu tương đối); `--git-dir`/`--work-tree`/GIT_DIR → không biết."""
    where: list[str | None] = [None] if redirected else list(ctx.visited)
    index = 0
    while index < len(args):
        arg = args[index]
        if not arg.startswith("-"):
            return arg, args[index + 1:], where
        flag = arg.split("=", 1)[0]
        if flag in GIT_REDIRECT_OPTIONS:
            where = [None]
        elif arg == "-C":
            target = args[index + 1] if index + 1 < len(args) else None
            where = [_resolve_dir(w, target) for w in where]
        index += 2 if arg in GIT_VALUE_OPTIONS else 1
    return "", [], where


def _git_item(args: list[str], ctx: Context, redirected: bool) -> str | None:
    sub, rest, where = _git_parse(args, ctx, redirected)
    if sub == "push":
        return "push"
    if sub == "subtree":
        return "push" if rest[:1] == ["push"] else None
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
        return "main_merge" if ctx.on_main(where) else ("branch_merge_local" if "branch_merge_local" in ctx.active else None)
    if sub == "pull":  # pull = fetch + merge: gộp cục bộ ở mọi nhánh, kể cả `--ff-only`
        return "main_merge" if ctx.on_main(where) else ("branch_merge_local" if "branch_merge_local" in ctx.active else None)
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


def _gh_item(args: list[str]) -> str | None:
    """`gh pr merge` (main_merge) và `gh release create` (tag); `-R/--repo` đứng ở đâu cũng bỏ cùng giá trị của nó."""
    plain: list[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in ("-R", "--repo"):
            index += 2
            continue
        if not arg.startswith("-"):
            plain.append(arg)
        index += 1
    if plain[:2] == ["pr", "merge"]:
        return "main_merge"
    return "tag" if plain[:2] == ["release", "create"] else None


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
    """Đích xoá nằm thật sự dưới `<gốc repo>/.tmp/` (ngoại lệ dọn tạm, method/autopilot.md mục 5). Glob ở thành phần cuối được
    mở rộng bằng `os.listdir`: mỗi mục khớp phải nằm thật trong `.tmp/` (theo `realpath`) và không phải file dấu."""
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
        return real != marker_real and real.startswith(inside)
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
            if entry.lower() == name or real == marker_real or not real.startswith(inside):
                return False
    return True


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
                flag = token.split("=", 1)[0]
                if flag in CHDIR_OPTIONS.get(name, ()):  # env -C/--chdir, sudo -D/--chdir: đổi thư mục như cd
                    attached = token.partition("=")[2] if "=" in token else None
                    value = attached if attached is not None else (tokens[index + 1] if index + 1 < len(tokens) else None)
                    ctx.enter(_resolve_dir(ctx.dir, value))
                    index += 1 if attached is not None else 2
                else:
                    index += 2 if token in value_opts else 1
            else:
                break
        else:
            tokens = []
            break
        if index == 0:
            continue
        tokens = tokens[index + positional:]
    return tokens, redirected


def _segment_item(tokens: list[str], ctx: Context, depth: int) -> str | None:
    tokens, redirected = _strip_prefixes(tokens, ctx)
    if not tokens:
        return None
    name, args = _exe_name(tokens[0]), tokens[1:]
    if name in CD_COMMANDS:
        target = next((a for a in args if not a.startswith("-")), None)
        ctx.enter(None if name in POP_COMMANDS else _resolve_dir(ctx.dir, target))
        return None
    if name in SHELL_WRAPPERS:
        for index, arg in enumerate(args):
            if arg.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c", arg):
                return _analyze(" ".join(args[index + 1:]), ctx, depth + 1) if depth < MAX_UNWRAP else NESTED
        return None
    if name == "git":
        return _git_item(args, ctx, redirected)
    if name == "gh":
        return _gh_item(args)
    if name == "find":
        if "-delete" in args:
            return "irreversible_delete"
        for index, arg in enumerate(args):
            if arg in FIND_EXEC:
                return _segment_item(args[index + 1:], ctx, depth)
        return None
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
        if item == NESTED or (item and item in ctx.active):
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


def _evaluate(raw: str) -> str | None:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("payload is not an object")
    dirs: tuple[str, ...] = (os.getcwd(),)
    try:
        dirs = _event_dirs(payload)
        name = _tool_name(payload)
        if name is not None and name.lower() not in SHELL_TOOLS:
            return None
        commands = _commands(payload)
        if not commands:
            return None
        command_dir, session_dir = dirs
        marker = find_marker(command_dir) or (find_marker(session_dir) if session_dir != command_dir else None)
        if marker is None:
            return None
        active, broken = load_active(marker)
        for text in commands:
            item = _analyze(text, Context(active, command_dir))
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
    parser.add_argument("--format", required=True, choices=FORMATS)
    args = parser.parse_args(argv)
    debug = os.environ.get("AUTOPILOT_GUARD_DEBUG", "") not in ("", "0")
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
        reason = _unparsed_reason("fatal", (os.getcwd(),))
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
