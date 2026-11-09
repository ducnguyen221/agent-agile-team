"""Rào git thường trực (SPR-16 TK8, luật ở `method/git-permissions.md`): nhận dạng repo được bảo vệ, phân loại lệnh git và `gh`
thành không đụng / tự làm / hỏi / cấm, kiểm hợp đồng đích khi tự đẩy.

Mô-đun thuần: không đọc stdin, không nhập `check` hay `autopilot_guard`. Guard tách lệnh thành `Segment` rồi gọi `classify`;
mọi lời gọi `git` đi qua `Runner` tiêm được (kiểm thử dùng bản giả) và dùng chung một ngân sách thời gian (`BUDGET_SECONDS`).
File này thuộc `FENCE_FILES`: sprint duyệt thay không sửa được.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from typing import Callable, Mapping, Optional

ENV_LIST = "AGENT_AGILE_PROTECTED_REPOS"
AGILE_JSON = ".agile.json"
BUDGET_SECONDS = 4.0
CALL_SECONDS = 2.0
BASE_PROTECTED = ("main", "master")
LEVELS = ("full", "push-only")

# Runner: (argv, cwd, giây) -> (mã thoát, stdout); mã thoát âm = không chạy được hay quá giờ.
Runner = Callable[[list, str, float], tuple]

ASK_TAIL = "Đức bấm cho phép trong phiên mới được chạy"
NO_ASK_TAIL = "host này chưa có tầng hỏi — Đức tự chạy lệnh này"  # Codex, Antigravity: 'hỏi' thành chặn với lý do này
NONE, AUTO, ASK, FORBID = "none", "auto", "ask", "forbid"
_RANK = {NONE: 0, AUTO: 1, ASK: 2, FORBID: 3}

GIT_VALUE_OPTIONS = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"})
FORCE_FLAGS = frozenset({"-f", "-d", "--delete", "--mirror", "--all", "--tags", "--prune", "--no-verify"})
PUSH_OK_FLAGS = frozenset({"-u", "--set-upstream", "-q", "--quiet", "-v", "--verbose", "-n", "--dry-run", "--progress"})
TAG_READ = frozenset({"-l", "--list", "-v", "--verify", "--contains", "--no-contains", "--merged", "--no-merged", "--points-at"})
CONFIG_READ = frozenset({"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--get-color", "--get-colorbool", "-l", "--list"})
CONFIG_WRITE = frozenset({"--add", "--unset", "--unset-all", "--replace-all", "--rename-section", "--remove-section", "--edit", "-e"})
CONFIG_VALUE_FLAGS = frozenset({"--type", "--default", "-f", "--file", "--blob", "--comment", "--url"})  # cờ nhận giá trị ở token kế
REMOTE_WRITE = frozenset({"set-url", "add", "remove", "rm", "rename", "set-head", "set-branches", "prune"})
GH_READ = (("pr", frozenset({"view", "list", "status", "checks", "diff"})), ("repo", frozenset({"view"})),
           ("release", frozenset({"list", "view"})),
           ("run", frozenset({"list", "view"})), ("issue", frozenset({"view", "list"})), ("auth", frozenset({"status"})),
           ("status", frozenset({None})), ("version", frozenset({None})))
GH_ASK = (("pr", frozenset({"create", "comment", "review", "checkout"})), ("issue", frozenset({"comment"})))
RELEVANT_SUBS = frozenset({"push", "subtree", "tag", "remote", "config", "merge", "commit", "pull", "cherry-pick", "reset", "rebase",
                           "rm", "mv", "update-index", "add", "restore", "checkout", "clean"})
FILE_SUBS = frozenset({"rm", "mv", "update-index", "add", "restore", "checkout", "clean"})  # chỉ đáng kể khi nhắc tới file bảo vệ
GH_API_WRITE_FLAGS = frozenset({"-f", "-F", "--field", "--raw-field", "--input"})


@dataclass
class Verdict:
    kind: str = NONE
    reason: str = ""
    code: str = ""


@dataclass
class Segment:
    """Một lệnh đã tách: `git` (có `sub`, `rest`, `where` = các thư mục git có thể làm việc, `redirected` = có GIT_DIR/GIT_WORK_TREE),
    `gh`, hay lệnh khác nhắc tới file bảo vệ (`other`)."""
    name: str
    args: list = field(default_factory=list)
    sub: str = ""
    rest: list = field(default_factory=list)
    where: list = field(default_factory=list)
    redirected: bool = False
    globals: list = field(default_factory=list)  # tuỳ chọn đứng trước lệnh con: `-C`, `-c`, `--git-dir`…


@dataclass
class Signals:
    listed: Optional[bool] = None  # True/False khi đọc được danh sách; None = biến vắng, file hỏng hay chưa dò
    config_file: bool = False
    indexed: Optional[bool] = None  # None = không xác định (lỗi, quá giờ, chưa dò): không mở rộng
    marker: bool = False
    level: str = "full"
    protected_branches: tuple = ()

    @property
    def protected(self) -> bool:
        return bool(self.listed) or self.config_file or bool(self.indexed) or self.marker


def split_git_args(args: list) -> tuple:
    """(tuỳ chọn đứng trước, lệnh con, đối số còn lại) của `git <args>`."""
    index, globals_ = 0, []
    while index < len(args):
        arg = args[index]
        if not arg.startswith("-"):
            return globals_, arg, args[index + 1:]
        step = 2 if arg in GIT_VALUE_OPTIONS else 1
        globals_.extend(args[index:index + step])
        index += step
    return globals_, "", []


def default_runner(argv: list, cwd: str, timeout: float) -> tuple:
    try:
        done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout,
                              env=dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0"))
        return done.returncode, done.stdout
    except (OSError, subprocess.SubprocessError, ValueError):
        return -1, ""


class Budget:
    """Tổng thời gian mọi lời gọi `git` của một lần guard (hook Claude có timeout 10 giây)."""

    def __init__(self, runner: Runner, total: float = BUDGET_SECONDS, clock: Callable[[], float] = time.monotonic) -> None:
        self.runner, self.total, self.clock = runner, total, clock
        self.started = clock()
        self.calls = 0

    def run(self, argv: list, cwd: str) -> tuple:
        left = self.total - (self.clock() - self.started)
        if left <= 0:
            return -1, ""
        self.calls += 1
        try:
            return self.runner(argv, cwd, min(left, CALL_SECONDS))
        except Exception:  # noqa: BLE001 — runner lỗi = không xác định
            return -1, ""


# --- đọc cấu trúc git bằng file (không gọi tiến trình) ------------------------------------------------------------

def find_repo(start: str) -> Optional[tuple]:
    """(gốc, thư mục .git của worktree, thư mục git chung) khi đi lên từ `start`; None nếu không thấy."""
    current = os.path.abspath(start)
    while True:
        dot = os.path.join(current, ".git")
        if os.path.isdir(dot):
            return current, dot, dot
        if os.path.isfile(dot):
            try:
                with open(dot, encoding="utf-8") as handle:
                    first = handle.readline().strip()
            except OSError:
                return current, dot, dot
            if first.startswith("gitdir:"):
                gitdir = os.path.normpath(os.path.join(current, first[len("gitdir:"):].strip()))
                common = gitdir
                try:
                    with open(os.path.join(gitdir, "commondir"), encoding="utf-8") as handle:
                        common = os.path.normpath(os.path.join(gitdir, handle.readline().strip()))
                except OSError:
                    pass
                return current, gitdir, common
            return current, dot, dot
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def current_branch(gitdir: str) -> Optional[str]:
    try:
        with open(os.path.join(gitdir, "HEAD"), encoding="utf-8") as handle:
            head = handle.readline().strip()
    except OSError:
        return None
    prefix = "ref: refs/heads/"
    return head[len(prefix):] if head.startswith(prefix) and head[len(prefix):] else None


def remote_default_branch(common: str, remote: str) -> Optional[str]:
    try:
        with open(os.path.join(common, "refs", "remotes", remote, "HEAD"), encoding="utf-8") as handle:
            head = handle.readline().strip()
    except OSError:
        return None
    prefix = "ref: refs/remotes/{}/".format(remote)
    return head[len(prefix):] if head.startswith(prefix) and head[len(prefix):] else None


def config_urls(common: str) -> list:
    """Mọi `url =`/`pushurl =` trong file config của repo (đọc văn bản)."""
    found = []
    try:
        with open(os.path.join(common, "config"), encoding="utf-8", errors="replace") as handle:
            for line in handle:
                match = re.match(r"^\s*(?:push)?url\s*=\s*(.+?)\s*$", line, re.I)
                if match:
                    found.append(match.group(1))
    except OSError:
        pass
    return found


def norm_url(url: str) -> str:
    """URL chuẩn hoá để so: bỏ scheme, `user@`, đổi `host:path` thành `host/path`, bỏ `.git` và `/` cuối, chữ thường."""
    text = url.strip()
    text = re.sub(r"^[A-Za-z][A-Za-z0-9+.-]*://", "", text)
    text = re.sub(r"^[^/@]+@", "", text)
    if "://" not in url and re.match(r"^[^/:]+:[^/]", text):
        text = text.replace(":", "/", 1)
    text = re.sub(r"\.git/?$", "", text.rstrip("/"))
    return text.lower()


def real(path: str) -> str:
    return os.path.normcase(os.path.realpath(os.path.expanduser(path)))


def load_list(env: Mapping) -> Optional[list]:
    """Danh sách bảo vệ ngoài repo: danh sách mục đã chuẩn hoá; None = biến vắng hay file hỏng (dấu hiệu 1 'không xác định')."""
    path = env.get(ENV_LIST, "")
    if not path:
        return None
    try:
        with open(path, encoding="utf-8-sig") as handle:
            data = json.load(handle)
        repos = data["repos"]
        if not isinstance(repos, list):
            return None
    except (OSError, ValueError, KeyError, TypeError):
        return None
    entries = []
    for item in repos:
        if not isinstance(item, dict):
            return None
        level = item.get("level", "full")
        urls = item.get("remote_urls", [])
        branches = item.get("protected_branches", [])
        common = item.get("git_common_dir", "")
        if (level not in LEVELS or not isinstance(urls, list) or not isinstance(branches, list)
                or not isinstance(common, str) or not all(isinstance(u, str) for u in urls)
                or not all(isinstance(b, str) for b in branches)):
            return None
        entries.append({"common": real(common) if common else "", "urls": {norm_url(u) for u in urls},
                        "branches": tuple(b for b in branches if b), "level": level})
    return entries


def list_file(env: Mapping) -> str:
    return real(env[ENV_LIST]) if env.get(ENV_LIST) else ""


def match_entry(entries: Optional[list], common: str, urls: list) -> Optional[dict]:
    if not entries:
        return None
    mine = real(common)
    wanted = {norm_url(u) for u in urls}
    for entry in entries:
        if (entry["common"] and entry["common"] == mine) or (entry["urls"] and entry["urls"] & wanted):
            return entry
    return None


def protection(cwd: str, env: Mapping, runner: Runner, marker: bool = False, need_index: bool = True,
               budget: Optional[Budget] = None) -> Signals:
    """Bốn dấu hiệu repo được bảo vệ (FR4.1). Dấu hiệu 3 chỉ gọi `git` khi `need_index` và chưa có dấu hiệu 1 hay 2."""
    sig = Signals(marker=marker)
    found = find_repo(cwd)
    entries = load_list(env)
    if entries is not None:
        sig.listed = False
    if found:
        root, _, common = found
        entry = match_entry(entries, common, config_urls(common))
        if entry:
            sig.listed, sig.level, sig.protected_branches = True, entry["level"], entry["branches"]
        sig.config_file = os.path.isfile(os.path.join(root, AGILE_JSON))
        if need_index and not sig.listed and not sig.config_file:
            code, _ = (budget or Budget(runner)).run(["git", "ls-files", "--error-unmatch", "--", ":/" + AGILE_JSON], cwd)
            sig.indexed = True if code == 0 else (False if code == 1 else None)
    return sig


def quick_protected(directories: list, env: Mapping, marker: bool = False) -> bool:
    """Dấu hiệu 1, 2 hay 4 từ các thư mục (không gọi tiến trình): dùng khi guard gặp lỗi và phải quyết chặn hay cho qua."""
    if marker:
        return True
    for directory in directories:
        try:
            if protection(directory, env, default_runner, marker=False, need_index=False).protected:
                return True
        except Exception:  # noqa: BLE001
            return True
    return False


def protected_names(sig: Signals, common: str) -> set:
    names = set(BASE_PROTECTED) | set(sig.protected_branches)
    for remote in ("origin", "upstream"):
        default = remote_default_branch(common, remote)
        if default:
            names.add(default)
    return names


# --- kiểm ghi file bảo vệ ----------------------------------------------------------------------------------------

def is_guard_path(path: str, base: str, env: Mapping) -> bool:
    """`path` là `.agile.json` hay chính file danh sách bảo vệ?"""
    norm = path.replace("\\", "/")
    if os.path.basename(norm).lower() == AGILE_JSON:
        return True
    target = list_file(env)
    if not target:
        return False
    full = norm if os.path.isabs(norm) else os.path.join(base, norm)
    return real(full) == target


def guarded_write(paths: list, base: str, env: Mapping) -> Optional[str]:
    for path in paths:
        if is_guard_path(path, base, env):
            return "git-fence: ghi vào '{}' (dấu hiệu bảo vệ repo) cần Đức nói trong chat — lệnh không chạy".format(os.path.basename(path.replace("\\", "/")))
    return None


# --- phân loại ---------------------------------------------------------------------------------------------------

class FenceContext:
    def __init__(self, cwd: str, env: Mapping, runner: Runner, marker: bool = False, contract: Optional[dict] = None,
                 budget: Optional[Budget] = None) -> None:
        self.cwd, self.env, self.marker, self.contract = os.path.abspath(cwd), env, marker, contract
        self.budget = budget or Budget(runner)
        self.runner = runner
        self._signals: dict = {}

    def signals_for(self, directory: Optional[str]) -> Signals:
        target = os.path.abspath(directory or self.cwd)
        if target not in self._signals:
            self._signals[target] = protection(target, self.env, self.runner, marker=self.marker, budget=self.budget)
        return self._signals[target]


def _verdict(kind: str, code: str, what: str, ctx: FenceContext) -> Verdict:
    """'Hỏi' thành chặn khi đang có file dấu autopilot (FR4.2): không ai bấm được."""
    if kind == ASK and ctx.marker:
        kind = FORBID
    tail = "cần Đức nói trong chat — lệnh không chạy" if kind == FORBID else ASK_TAIL
    return Verdict(kind, "git-fence: '{}' trong repo được bảo vệ {} [{}]".format(what, tail, code), code)


def _on_protected_branch(directory: Optional[str], ctx: FenceContext, sig: Signals) -> bool:
    """Nhánh hiện tại của thư mục là nhánh được bảo vệ? Không xác định được → True (đóng an toàn)."""
    if directory is None:
        return True
    found = find_repo(directory)
    if not found:
        return True
    _, gitdir, common = found
    branch = current_branch(gitdir)
    return branch is None or branch in protected_names(sig, common)


def _flags(rest: list) -> list:
    return [a for a in rest if a.startswith("-")]


def _push_verdict(seg: Segment, ctx: FenceContext, sig: Signals) -> Verdict:
    rest = seg.rest[1:] if seg.sub == "subtree" else seg.rest
    forced = [a for a in rest if a in FORCE_FLAGS or a.startswith("--force") or re.fullmatch(r"-[A-Za-z]*f[A-Za-z]*", a)
              or a.startswith(("+", ":"))]
    if forced:
        return _verdict(FORBID, "push-forced", "push " + forced[0], ctx)
    if not ctx.marker:
        return _verdict(ASK, "push-ask", "push", ctx)
    if ctx.contract is None:
        return _verdict(FORBID, "push-repo-unverified", "push", ctx)
    code = push_contract(rest, ctx.contract, seg, ctx, sig)
    if code is None:
        return Verdict(AUTO, "", "")
    return Verdict(FORBID, "git-fence: 'push' không đúng hợp đồng đích ({}) — lệnh không chạy".format(code), code)


def push_contract(rest: list, contract: dict, seg: Segment, ctx: FenceContext, sig: Signals) -> Optional[str]:
    """Bảy điều của hợp đồng đích (method/git-permissions.md mục 6). None = cho qua, ngược lại mã chặn."""
    if seg.redirected or any(d is None for d in seg.where) or not seg.where:
        return "push-repo-unverified"
    if any(g in ("-c", "--config-env") or g.startswith(("-c", "--config-env=")) for g in seg.globals):
        return "push-config-override"
    flags = [a for a in rest if a.startswith("-")]
    if any(a not in PUSH_OK_FLAGS for a in flags):
        return "push-flag-forbidden"
    positional = [a for a in rest if not a.startswith("-")]
    if len(positional) < 2:
        return "push-target-unknown"
    if len(positional) > 2:
        return "push-multiple-refspecs"
    remote, refspec = positional
    if remote != contract["push_remote"]:
        return "push-remote-mismatch"
    if refspec.startswith(("+", ":")) or "*" in refspec:
        return "push-flag-forbidden"
    source, colon, dest = refspec.partition(":")
    dest = dest if colon else source
    if not dest or dest.endswith("/"):
        return "push-target-unknown"
    if not dest.startswith("refs/"):
        dest = "refs/heads/" + dest
    if dest not in contract["push_targets"]:
        return "push-target-unknown"
    here = None
    for directory in seg.where:
        found = find_repo(directory)
        if not found:
            return "push-repo-unverified"
        if real(found[2]) != real(contract["git_common_dir"]):
            return "push-repo-unverified"
        here = found
    if here is None:
        return "push-repo-unverified"
    common = here[2]
    code, out = ctx.budget.run(["git", "remote", "get-url", "--push", "--all", remote], seg.where[0])
    if code != 0:
        return "push-url-unverified"
    if {norm_url(line) for line in out.splitlines() if line.strip()} != {norm_url(u) for u in contract["push_urls"]}:
        return "push-url-mismatch"
    default = remote_default_branch(common, remote)
    branch = dest[len("refs/heads/"):] if dest.startswith("refs/heads/") else ""
    if default is None:
        return "push-default-branch-unknown"
    if branch == default or branch in protected_names(sig, common):
        return "push-target-protected"
    return None


def _git_verdict(seg: Segment, ctx: FenceContext) -> Verdict:
    sub, rest = seg.sub, seg.rest
    if sub not in RELEVANT_SUBS and "--no-verify" not in seg.args and not any(g in ("-c", "--config-env") for g in seg.globals):
        return Verdict()  # lệnh đọc/trung tính: không gọi `git` để dò dấu hiệu
    if sub in FILE_SUBS and not any(is_guard_path(a, ctx.cwd, ctx.env) for a in rest if not a.startswith("-")):
        return Verdict()
    directories = seg.where or [None]
    if "--no-verify" in seg.args and not any(ctx.signals_for(d).protected for d in directories):
        return Verdict()
    if "--no-verify" in seg.args:
        return _verdict(FORBID, "no-verify", "--no-verify", ctx)
    sigs = [ctx.signals_for(d) for d in directories]
    if not any(s.protected for s in sigs):
        return Verdict()
    sig = next(s for s in sigs if s.protected)
    level = "full" if any(s.protected and s.level == "full" for s in sigs) else sig.level
    if any(g in ("-c", "--config-env") for g in seg.globals) and sub in ("push", "config", "remote", "commit", "merge", "pull", "tag"):
        return _verdict(FORBID, "config-override", "git -c", ctx)
    if any(AGILE_JSON == os.path.basename(a.replace("\\", "/")).lower() or is_guard_path(a, ctx.cwd, ctx.env)
           for a in rest if not a.startswith("-")) and sub in ("rm", "mv", "update-index", "add", "restore", "checkout", "clean"):
        return _verdict(FORBID, "guard-file", "git {} {}".format(sub, AGILE_JSON), ctx)
    if sub == "push" or (sub == "subtree" and rest[:1] == ["push"]):
        return _push_verdict(seg, ctx, sig)
    if sub == "tag":
        if any(a in ("-d", "--delete") or re.fullmatch(r"-[A-Za-z]*d[A-Za-z]*", a) for a in rest):
            return _verdict(FORBID, "tag-delete", "tag -d", ctx)
        if not rest or any(a.split("=", 1)[0] in TAG_READ or re.fullmatch(r"-n\d*", a) for a in rest):
            return Verdict()
        return _verdict(ASK, "tag-create", "tag", ctx)
    if sub == "remote":
        action = next((a for a in rest if not a.startswith("-")), "")
        if action in REMOTE_WRITE:
            return _verdict(FORBID, "remote-write", "remote " + action, ctx)
        return Verdict()
    if sub == "config":
        positional, skip = [], False
        for arg in rest:
            if skip:
                skip = False
            elif arg in CONFIG_VALUE_FLAGS:
                skip = True
            elif not arg.startswith("-"):
                positional.append(arg)
        writing = any(a in CONFIG_WRITE for a in rest) or len(positional) >= 2
        if any(a in CONFIG_READ for a in rest) and not writing:
            return Verdict()
        if not writing:
            return Verdict()  # `git config <khoá>` một đối số là đọc
        if not positional:
            return _verdict(FORBID, "config-write", "config --edit", ctx)
        key = positional[0].lower()
        if key.startswith(("remote.", "url.")) or key == "core.hookspath":
            return _verdict(FORBID, "config-write", "config " + key, ctx)
        return Verdict()
    if sub in ("merge", "commit", "pull", "cherry-pick", "reset", "rebase"):
        if any(a in ("--abort", "--quit", "--continue", "--skip") for a in rest):
            return Verdict()
        if not any(_on_protected_branch(d, ctx, sig) for d in directories):
            return Verdict()
        if sub == "merge":
            return _verdict(ASK, "merge-ask", "merge vào nhánh được bảo vệ", ctx)
        if level == "push-only":
            if sub == "commit":
                return Verdict(AUTO)
            if sub == "pull":
                return Verdict(AUTO) if "--ff-only" in rest else _verdict(ASK, "pull-ask", "pull", ctx)
            return _verdict(ASK, sub + "-ask", sub + " trên nhánh được bảo vệ", ctx)
        return _verdict(FORBID, "protected-branch-" + sub, sub + " trên nhánh được bảo vệ", ctx)
    return Verdict()


def _gh_plain(args: list) -> tuple:
    """(đối số không phải cờ, repo đích từ -R/--repo hay None, danh sách cờ)."""
    plain, flags, repo, index = [], [], None, 0
    while index < len(args):
        arg = args[index]
        if arg in ("-R", "--repo"):
            repo = args[index + 1] if index + 1 < len(args) else None
            index += 2
            continue
        if arg.startswith("--repo="):
            repo = arg.split("=", 1)[1]
        elif arg.startswith("-"):
            flags.append(arg)
        else:
            plain.append(arg)
        index += 1
    return plain, repo, flags


def _gh_verdict(seg: Segment, ctx: FenceContext) -> Verdict:
    plain, repo, flags = _gh_plain(seg.args)
    target = repo
    if plain[:1] == ["api"] and len(plain) > 1:
        match = re.match(r"^/?repos/([^/]+/[^/]+)", plain[1])
        target = target or (match.group(1) if match else None)
    sig = ctx.signals_for(None)
    listed_target = False
    if target:
        entries = load_list(ctx.env) or []
        listed_target = any(any(norm_url(u).endswith("/" + target.lower().strip("/")) for u in e["urls"]) for e in entries)
    if not (sig.protected or listed_target):
        return Verdict()
    head = plain[0] if plain else ""
    action = plain[1] if len(plain) > 1 else None
    if head == "api":
        method = None
        write_flag = False
        for index, arg in enumerate(seg.args):
            if arg in ("-X", "--method") and index + 1 < len(seg.args):
                method = seg.args[index + 1].upper()
            elif arg.startswith("--method="):
                method = arg.split("=", 1)[1].upper()
            elif arg.startswith("-X") and not arg.startswith("--") and len(arg) > 2:
                method = arg[2:].upper()  # -XPUT
            if (arg in GH_API_WRITE_FLAGS or arg.startswith(("--field=", "--raw-field=", "--input="))
                    or (arg.startswith(("-f", "-F")) and not arg.startswith("--") and len(arg) > 2)):  # -ftitle=x
                write_flag = True
        if (method and method != "GET") or write_flag:
            return _verdict(FORBID, "gh-api-write", "gh api (ghi)", ctx)
        return Verdict()
    if head == "release" and action not in ("list", "view"):
        return _verdict(FORBID, "gh-release", "gh release", ctx)
    if head == "pr" and action == "merge":
        return _verdict(FORBID if ctx.marker else ASK, "gh-pr-merge", "gh pr merge", ctx)
    for name, actions in GH_READ:
        if head == name and (action in actions or None in actions):
            return Verdict()
    for name, actions in GH_ASK:
        if head == name and action in actions:
            if ctx.marker and ctx.contract is not None:
                return Verdict(AUTO)
            return _verdict(ASK, "gh-ask", "gh {} {}".format(head, action), ctx)
    if not head and not flags:
        return Verdict()
    return _verdict(FORBID, "gh-unlisted", "gh " + " ".join(plain[:2]), ctx)


def classify(segments: list, ctx: FenceContext) -> Verdict:
    """Quyết định mạnh nhất (cấm > hỏi > tự làm > không đụng) trên mọi đoạn lệnh."""
    best = Verdict()
    for seg in segments:
        if seg.name == "git":
            verdict = _git_verdict(seg, ctx)
        elif seg.name == "gh":
            verdict = _gh_verdict(seg, ctx)
        elif seg.name == "other":
            sig = ctx.signals_for(None)
            verdict = _verdict(FORBID, "guard-file", "ghi " + AGILE_JSON, ctx) if sig.protected else Verdict()
        elif seg.name == "nested":
            sig = ctx.signals_for(None)
            verdict = (_verdict(FORBID, "unparsed", "lệnh lồng không phân tích được", ctx) if sig.protected else Verdict())
        else:
            verdict = Verdict()
        if _RANK[verdict.kind] > _RANK[best.kind]:
            best = verdict
    return best
