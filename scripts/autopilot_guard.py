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

Mục có mẫu lệnh: push, tag, main_merge, irreversible_delete, branch_merge_local. Các mục khác là rào hành vi (không có mẫu).
Ngoài danh sách loại, hook bảo vệ chính file dấu: lệnh shell không chỉ-đọc có đối số trỏ tới file dấu (hoặc `.tmp/` bao nó, hay glob khớp
nó) và công cụ ghi file (`Write`, `Edit`, `MultiEdit`, `NotebookEdit`, `apply_patch`, `write_to_file`, `replace_file_content`…) có đường
đích là file dấu đều bị chặn với lý do `file dấu là rào`. Việc đăng ký matcher cho công cụ ghi file thuộc cấu hình harness (chưa làm).
Tên mục lấy từ `_autopilot_rules.AUTOPILOT_EXCLUSIONS` (một nguồn; test ghim đúng 13 mục). Không gọi tiến trình con; nhánh hiện tại đọc từ
file `.git/HEAD` của thư mục mà lệnh git thật sự chạy (theo `cd`, `git -C`; không xác định được thì coi là nhánh chính).

Không phân tích chuỗi chương trình tuỳ ý (`awk 'BEGIN{system(…)}'`, `perl -e`, `ruby -e`, `node -e`, `python -c`): giới hạn đã biết.

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
from dataclasses import dataclass
from typing import TextIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import git_fence  # noqa: E402

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
CHDIR_OPTIONS = {"env": frozenset({"-C", "--chdir"}), "sudo": frozenset({"-D", "--chdir"})}  # dạng tách rời: giá trị ở token kế
FIND_EXEC = frozenset({"-exec", "-execdir", "-ok", "-okdir"})
UNSAFE_PATH_CHARS = set(",$%`~{}()<>!^\"'\n\r;|&")
GLOB_CHARS = set("*?[")
MAX_UNWRAP = 3
MAX_WALK_DEPTH = 6  # độ sâu tối đa khi dò file dấu lồng trong đích dọn .tmp/
NESTED = "nested"  # đơn vị chặn riêng: lồng shell quá sâu, không phân tích được
MARKER = "marker"  # đơn vị chặn riêng: đụng tới chính file dấu
UNRESOLVED = "unresolved"  # đơn vị chặn riêng: chuỗi đưa vào shell có git/gh nhưng không phân tích được
SPECIAL_ITEMS = frozenset({NESTED, MARKER, UNRESOLVED})
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


PUSH_CONTRACT_KEYS = ("push_remote", "push_urls", "push_targets", "git_common_dir")


def load_push_contract(marker: str) -> dict | None:
    """Hợp đồng đích khi tự đẩy (`+đẩy-nhánh`, method/git-permissions.md): dict bốn khoá `push_remote`, `push_urls`,
    `push_targets`, `git_common_dir` khi file dấu đọc được, `exclusions` là danh sách KHÔNG có `push` và cả bốn khoá đúng
    kiểu; ngược lại `None` (= không cho đẩy, đóng an toàn). `load_active` không đổi: thiếu `push` vẫn được bổ sung đủ,
    nên chỉ `git_fence.push_contract` mới mở được một lệnh đẩy cụ thể."""
    try:
        with open(marker, encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("exclusions"), list) or "push" in data["exclusions"]:
        return None
    remote, urls, targets, common = (data.get(key) for key in PUSH_CONTRACT_KEYS)

    def texts(value) -> bool:
        return isinstance(value, list) and bool(value) and all(isinstance(v, str) and v.strip() for v in value)

    if not (isinstance(remote, str) and remote.strip() and texts(urls) and texts(targets)
            and all(t.startswith("refs/heads/") and len(t) > len("refs/heads/") for t in targets)
            and isinstance(common, str) and common.strip()):
        return None
    return {"push_remote": remote, "push_urls": list(urls), "push_targets": list(targets), "git_common_dir": common}


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
        self.forced_main = False  # đã gặp `git checkout|switch main|master` trong lệnh ghép
        self.cwd_changed = False  # đã gặp thao tác đổi thư mục (cd, pushd, env -C…, kể cả trong subshell/bash -c)
        self._heads: dict[str, bool] = {}

    def enter(self) -> None:
        """Ghi nhận một thao tác đổi thư mục. Không tính đường đi (`cd` trong subshell hay vế pipeline không đổi thư mục của lệnh
        sau, `cd` tương đối nối tiếp nhau khó tính đúng): từ đây `git merge`/`pull` không kèm `-C` coi như ở nhánh chính."""
        self.cwd_changed = True

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
    """(lệnh con, đối số còn lại, các thư mục git có thể làm việc). Không có `-C`: thư mục của lệnh, hoặc không biết (None → main)
    nếu đã có thao tác đổi thư mục; `-C <dir>` đọc nhánh của chính `<dir>` (tương đối sau khi đổi thư mục → không biết);
    `--git-dir`/`--work-tree`/GIT_DIR → không biết."""
    where: list[str | None] = [None] if redirected or ctx.cwd_changed else [ctx.cwd]
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
    if sub == "stash":  # `-u`/`--include-untracked`/`-a`/`--all` cất cả file chưa theo dõi: file dấu (trong .tmp/) bị lấy đi
        stashes_untracked = "--include-untracked" in rest or "--all" in rest or any(_cluster(a, "ua") for a in rest)
        return MARKER if stashes_untracked else None
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
            return None
    return None


def _read_only(name: str, args: list[str], ctx: Context) -> bool:
    if name in READ_ONLY_COMMANDS:
        return True
    if name == "sed":
        return not any(a == "--in-place" or a.startswith("--in-place=") or (a.startswith("-") and _cluster(a.split("=")[0], "i")) or a.startswith("-i") for a in args)
    if name == "git":
        return _git_parse(args, ctx, False)[0] in READ_ONLY_GIT
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


def _copy_destinations(tokens: list[str]) -> set[int]:
    """Vị trí token là ĐÍCH của cp/Copy-Item: giá trị sau `-Destination`/`-t`/`--target-directory`, không thì đối số vị trí cuối."""
    explicit: set[int] = set()
    positional: list[int] = []
    for index in range(1, len(tokens)):
        token = tokens[index]
        low = token.lower()
        before = tokens[index - 1].lower() if index > 1 else ""
        if before in ("-t", "--target-directory") or re.fullmatch(r"-dest[a-z]*", before):
            explicit.add(index)
        elif low.startswith("--target-directory="):
            explicit.add(index)
        elif not token.startswith("-"):
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


def _segment_item(tokens: list[str], ctx: Context, depth: int) -> str | None:
    tokens, redirected = _strip_prefixes(tokens, ctx)
    if not tokens:
        return None
    if _is_clear_command(tokens):  # lối dừng tường minh của điều phối (rào hành vi, xem docstring)
        return None
    return _command_item(tokens, redirected, ctx, depth) or _marker_item(tokens, ctx)


def _nested_string(text: str, ctx: Context, depth: int) -> str | None:
    """Chuỗi được đưa vào shell (eval, ống vào bash): xét như lệnh lồng; không phân tích được mà có git/gh kèm biến → chặn."""
    if not text.strip():
        return None
    if depth >= MAX_UNWRAP:
        return NESTED
    item = _analyze(text, ctx, depth + 1)
    if item:
        return item
    names = {_exe_name(t) for t in tokenize(text)}
    return UNRESOLVED if names & {"git", "gh"} and DYNAMIC_CHARS & set(text) else None


def _pipe_to_shell(text: str, ctx: Context, depth: int) -> str | None:
    """`echo "git push" | bash`: vế trước ống (bỏ tên lệnh đầu) là chuỗi đưa vào shell."""
    parts = PIPE.split(text)
    for index in range(1, len(parts)):
        stage, _ = _strip_prefixes(tokenize(re.split(r"&&|;|\n", parts[index])[0]), Context(set(), ctx.cwd))
        if not stage:
            continue
        name = _exe_name(stage[0])
        takes_script = any(a.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c", a) for a in stage[1:])
        if (name in SHELL_WRAPPERS or name in EVAL_COMMANDS) and not takes_script:
            source = tokenize(re.split(r"&&|;|\n|\|\|", parts[index - 1])[-1])
            item = _nested_string(" ".join(source[1:]), ctx, depth)
            if item:
                return item
    return None


def _command_item(tokens: list[str], redirected: bool, ctx: Context, depth: int) -> str | None:
    name, args = _exe_name(tokens[0]), tokens[1:]
    if name in CD_COMMANDS:
        ctx.enter()
        return None
    if name in EVAL_COMMANDS:
        return _nested_string(" ".join(args), ctx, depth)
    if name in SHELL_WRAPPERS:
        if "<<<" in args and args.index("<<<") + 1 < len(args):  # bash <<< "git push"
            return _nested_string(" ".join(args[args.index("<<<") + 1:]), ctx, depth)
        for index, arg in enumerate(args):
            if arg.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c", arg):
                return _analyze(" ".join(args[index + 1:]), ctx, depth + 1) if depth < MAX_UNWRAP else NESTED
        return None
    if name == "git":
        return _git_item(args, ctx, redirected)
    if name == "gh":
        return _gh_item(args)
    if name == "find":
        return _find_item(args, ctx, depth)
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
    text = _join_and_strip(text)  # nối dòng `git \` + xuống dòng; bỏ thân heredoc của trình không phải shell
    item = _pipe_to_shell(text, ctx, depth)
    if item:
        return item
    for segment in SEPARATORS.split(text):
        item = _segment_item(tokenize(segment), ctx, depth)
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
    if item == UNRESOLVED:
        return "autopilot: chuỗi lệnh đưa vào shell có git/gh nhưng không phân tích được — cần người dùng nói trong chat — lệnh không chạy"
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
                if arg.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c", arg):
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
            if "push" in active and not broken and load_push_contract(marker) is not None:
                active = active - {"push"}  # `+đẩy-nhánh`: lệnh đẩy do git_fence quyết theo hợp đồng đích (mọi lệnh đẩy lệch hợp đồng bị chặn ở đó)
            for text in commands:
                item = _analyze(text, Context(active, command_dir, marker))
                if item:
                    return reason_for(item, broken)
        return None
    except Exception as exc:
        raise _Failed(dirs, type(exc).__name__) from exc


# --- rào git thường trực (SPR-16 TK8): gọi `git_fence` trước mọi nhánh trả sớm ----------------------------------------

HEAD_MOVERS = frozenset({"checkout", "switch", "symbolic-ref", "update-ref", "reset", "rebase", "merge", "pull", "cherry-pick", "revert", "am", "bisect"})

@dataclass
class Decision:
    """Quyết định có loại: `deny` (chặn) hay `ask` (Claude hỏi; Codex và Antigravity chưa có tầng hỏi nên thành chặn)."""
    kind: str
    reason: str


def _collect_nested(text: str, ctx: Context, depth: int, out: list) -> None:
    if not text.strip():
        return
    if depth >= MAX_UNWRAP:
        out.append(git_fence.Segment("nested"))
        return
    _collect_segments(text, ctx, depth + 1, out)
    names = {_exe_name(t) for t in tokenize(text)}
    if names & {"git", "gh"} and DYNAMIC_CHARS & set(text):
        out.append(git_fence.Segment("nested"))


def _collect_segments(text: str, ctx: Context, depth: int, out: list) -> None:
    """Gom mọi đoạn lệnh git/gh (và lệnh không chỉ-đọc nhắc tới file bảo vệ) của `text` thành `git_fence.Segment`."""
    text = _join_and_strip(text)
    text = text.replace(">|", ">")  # `>|` (ghi đè dù noclobber) là chuyển hướng, không phải ống
    plain = re.sub(r"[\"']", "", text)  # bỏ nháy: `'GI'T_X=1` vẫn là GIT_X
    git_env = bool(re.search(r"(?i)GIT_[A-Z0-9_]+", plain)) or "--exec-path" in plain or bool(re.search(r"\$\{?[A-Za-z_]\w*\}?\w*=", plain))
    gh_env = bool(re.search(r"(?i)GH_[A-Z0-9_]+", plain))
    parts = PIPE.split(text)
    for index in range(1, len(parts)):  # `echo "git push" | bash`
        stage, _ = _strip_prefixes(tokenize(re.split(r"&&|;|\n", parts[index])[0]), Context(set(), ctx.cwd))
        if not stage:
            continue
        name = _exe_name(stage[0])
        takes_script = any(a.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c", a) for a in stage[1:])
        if (name in SHELL_WRAPPERS or name in EVAL_COMMANDS) and not takes_script:
            source = tokenize(re.split(r"&&|;|\n|\|\|", parts[index - 1])[-1])
            _collect_nested(" ".join(source[1:]), ctx, depth, out)
    for segment in SEPARATORS.split(text):
        tokens, redirected = _strip_prefixes(tokenize(segment), ctx)
        if not tokens:
            continue
        name, args = _exe_name(tokens[0]), tokens[1:]
        if name in CD_COMMANDS:
            ctx.enter()
        elif name in EVAL_COMMANDS:
            _collect_nested(" ".join(args), ctx, depth, out)
        elif name in SHELL_WRAPPERS:
            if "<<<" in args and args.index("<<<") + 1 < len(args):
                _collect_nested(" ".join(args[args.index("<<<") + 1:]), ctx, depth, out)
                continue
            for index, arg in enumerate(args):
                if arg.lower() in WRAPPER_FLAGS or re.fullmatch(r"-[a-z]*c", arg):
                    if depth < MAX_UNWRAP:
                        _collect_segments(" ".join(args[index + 1:]), ctx, depth + 1, out)
                    else:
                        out.append(git_fence.Segment("nested"))
                    break
        elif name == "git":
            globals_, sub, rest = git_fence.split_git_args(args)
            where = _git_parse(args, ctx, redirected)[2]
            if ctx.forced_main:
                where = [None]
            # mọi biến GIT_* trong lệnh (GIT_CONFIG_*, GIT_SSH_COMMAND, GIT_CONFIG_GLOBAL…) đổi hành vi của git mà guard không thấy: hợp đồng đích không áp
            out.append(git_fence.Segment("git", args, sub, rest, where, redirected or git_env, globals_,
                                         head_moved=getattr(ctx, "head_moved", False)))
            if sub in HEAD_MOVERS or (sub == "branch" and any(a in ("-m", "-M", "--move", "-c", "-C", "--copy") or _cluster(a, "mMcC") for a in rest)):
                ctx.head_moved = True
            if sub in ("checkout", "switch") and any(a in MAIN_BRANCHES for a in rest):
                ctx.forced_main = True
        elif name == "gh":
            out.append(git_fence.Segment("gh", args, redirected=gh_env))
        else:
            env = getattr(ctx, "env", os.environ)
            read_only = _read_only(name, args, ctx)
            for index, arg in enumerate(args):
                redirect = REDIRECT.match(arg) or (re.search(r">>?(.*)$", arg) if ">" in arg else None)
                if redirect:  # đích chuyển hướng tính cả với lệnh chỉ-đọc (`echo x > .agile.json`, `echo {}>.agile.json`)
                    target = redirect.group(1) or (args[index + 1] if index + 1 < len(args) else "")
                elif read_only:
                    continue
                else:
                    target = arg
                if target and git_fence.targets_guard_file(target, ctx.cwd, env, loose=ctx.cwd_changed, whole=text):
                    out.append(git_fence.Segment("other", args))
                    break


def _fence_decision(payload: dict, env) -> Decision | None:
    command_dir, session_dir = _event_dirs(payload)
    name = _tool_name(payload)
    marker = find_marker(command_dir) or (find_marker(session_dir) if session_dir != command_dir else None)
    if name is not None and name.lower() in WRITE_TOOLS:
        paths = _write_paths(payload)
        reason = git_fence.guarded_write(paths, command_dir, env) if paths else None
        if reason and git_fence.protection(command_dir, env, git_fence.default_runner, marker=bool(marker)).protected:
            return Decision("deny", reason)
        return None
    if name is not None and name.lower() not in SHELL_TOOLS:
        return None
    segments: list = []
    for text in _commands(payload):
        ctx = Context(set(), command_dir)
        ctx.env = env
        _collect_segments(text, ctx, 0, segments)
    if not segments:
        return None
    contract = load_push_contract(marker) if marker else None
    verdict = git_fence.classify(segments, git_fence.FenceContext(command_dir, env, git_fence.default_runner,
                                                                  marker=bool(marker), contract=contract))
    if verdict.kind == git_fence.FORBID:
        return Decision("deny", verdict.reason)
    if verdict.kind == git_fence.ASK:
        return Decision("ask", verdict.reason)
    return None


def _decide(raw: str, env=None) -> Decision | None:
    """Rào autopilot (`_evaluate`) trước: lý do cũ giữ nguyên chữ; rồi rào git thường trực. Lỗi của rào git trong repo có dấu hiệu 1/2/4 → chặn."""
    env = os.environ if env is None else env
    reason = _evaluate(raw)
    if reason:
        return Decision("deny", reason)
    payload = json.loads(raw)
    try:
        return _fence_decision(payload, env)
    except Exception as exc:  # noqa: BLE001
        dirs = _event_dirs(payload)
        marker = any(find_marker(d) for d in dirs)
        if git_fence.quick_protected(list(dirs), env, marker):
            return Decision("deny", "git-fence: hook gặp lỗi ({}) trong repo được bảo vệ — lệnh không chạy".format(type(exc).__name__))
        return None


def _unparsed_reason(label: str, dirs: tuple[str, ...]) -> str | None:
    """Đầu vào hỏng hay ngoại lệ: chặn nếu có file dấu từ một trong `dirs` (hoặc không dò được), không thì cho qua."""
    try:
        if all(find_marker(d) is None for d in dirs):
            if git_fence.quick_protected(list(dirs), os.environ):
                return "git-fence: hook gặp lỗi ({}) trong repo được bảo vệ — lệnh không chạy".format(label)
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


def _ask(fmt: str, reason: str, stdout: TextIO, stderr: TextIO) -> int:
    """Claude: quyết định hỏi (Đức bấm cho phép trong phiên); Codex, Antigravity chưa có tầng hỏi nên thành chặn."""
    if fmt == "claude":
        stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                                         "permissionDecisionReason": reason}}, ensure_ascii=False) + "\n")
        return 0
    return _deny(fmt, reason.replace(git_fence.ASK_TAIL, git_fence.NO_ASK_TAIL), stdout, stderr)


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
    decision = None
    try:
        decision = _decide(stdin.read())
    except _Failed as failed:
        if debug:
            traceback.print_exc(file=stderr)
        reason = _unparsed_reason(failed.label, failed.dirs)
        decision = Decision("deny", reason) if reason else None
    except Exception as exc:  # JSON hỏng, đầu vào không đọc được: chưa có thư mục sự kiện, dò từ thư mục tiến trình
        if debug:
            traceback.print_exc(file=stderr)
        reason = _unparsed_reason(type(exc).__name__, (os.getcwd(),))
        decision = Decision("deny", reason) if reason else None
    if decision is None:
        return _allow(args.format, stdout)
    if decision.kind == "ask":
        return _ask(args.format, decision.reason, stdout, stderr)
    return _deny(args.format, decision.reason, stdout, stderr)


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
