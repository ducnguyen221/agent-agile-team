"""Chuẩn đối chứng (oracle) cho rào git: so quyết định của rào với điều trình shell THẬT sự chạy.

Một `git` giả đặt trước PATH ghi argv vào nhật ký; lệnh nguy hiểm "thật sự chạy" khi nhật ký có argv `push` kèm `--force`/`main`/`--delete`.
Dùng ở `tests/test_argv_shim.py` (shim phải bỏ sót 0) và chạy tay để đo guard đọc chuỗi:
    python tests/oracle_harness.py <số ca nguy hiểm> <số ca lành> <hạt>
Chỉ cần `bash` chạy được (Git Bash trên Windows; WSL stub không tính). Không đụng repo thật: repo giả dựng trong thư mục tạm, xoá khi xong.
"""
from __future__ import annotations

import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

DANGER = ["git push --force origin main", "git push origin main", "git push origin x main", "git push --delete origin main"]
SAFE = ["git status", "git log --oneline -3", "git diff --stat", "git add -A", "git commit -m 'msg (a); b'", "git -c core.pager=cat log -1"]

PRE = ["", "echo hi; ", "echo \"it's\" ; ", "echo 'a b' && ", "true && ", "cd . && ", "echo \"a;b\" ; ", "ls | cat; ", "false || ", "sleep 0 & ", ": ; ",
       "echo a\n", "echo \"x\n\";", "X=\"a b\"; "]
POST = ["", " 2>&1", " >/dev/null", " &>/dev/null", " 2>/dev/null", " ; echo done", " && echo ok", " | cat", "\necho x", " &"]
ENVP = ["", "", "FOO=1 ", "GIT_TRACE=0 ", "env ", "env FOO=1 ", "command ", "nice ", "time ", "exec ", "sudo -n true; ", "FOO=\"a b\" "]
WRAP = ["{c}", "{c}", "bash -c {q}", "sh -c {q}", "eval {q}", "( {c} )", "{{ {c}; }}", "if true; then {c}; fi", "for i in 1; do {c}; done", "watch -n1 {q}",
        "xargs -I{{}} sh -c {q} <<< x"]


def sq(text: str) -> str:
    return "'" + text.replace("'", "'\\''") + "'"


def mangle_git(rnd: random.Random, core: str) -> str:
    kind = rnd.randrange(8)
    if kind == 0:
        return core.replace("git", "'git'", 1)
    if kind == 1:
        return core.replace("git", '"git"', 1)
    if kind == 2:
        return core.replace("git", 'g"i"t', 1)
    if kind == 3:
        return core.replace("git ", 'git -c x.y="a;b" ', 1)
    if kind == 4:
        return core.replace("git ", "git --no-pager ", 1)
    if kind == 5:
        return core.replace("push", '"push"', 1)
    if kind == 6:
        return core.replace("main", "'main'", 1)
    return core


def build(rnd: random.Random, core: str) -> str:
    cmd = mangle_git(rnd, core) if rnd.random() < 0.6 else core
    cmd = rnd.choice(ENVP) + cmd
    cmd = rnd.choice(WRAP).format(c=cmd, q=sq(cmd))
    return rnd.choice(PRE) + cmd + rnd.choice(POST)


def build_cases(seed: int, n_danger: int, n_safe: int) -> tuple[list[str], list[str]]:
    rnd = random.Random(seed)
    return [build(rnd, rnd.choice(DANGER)) for _ in range(n_danger)], [build(rnd, rnd.choice(SAFE)) for _ in range(n_safe)]


def danger_in(text: str) -> bool:
    for line in text.splitlines():
        if line.startswith(("RUN ", "EXEC ")):
            args = line.split(None, 1)[1].split()
            if "push" in args and ("--force" in args or "main" in args or "--delete" in args):
                return True
    return False


def make_stub(directory: Path) -> Path:
    """`git` giả: ghi argv vào $LOG rồi thoát 0."""
    directory.mkdir(parents=True, exist_ok=True)
    stub = directory / "git"
    stub.write_bytes(b'#!/bin/sh\necho "RUN $*" >> "$LOG"\nexit 0\n')
    (directory / "git.cmd").write_bytes(b'@echo off\r\necho RUN %*>> "%LOG%"\r\nexit /b 0\r\n')  # trên Windows, `shutil.which` của shim chỉ thấy tệp có đuôi PATHEXT
    return stub


def run_bash(cmd: str, repo: Path, log: Path, path_dirs: list[Path], timeout: int = 30) -> str:
    """Chạy `cmd` bằng bash thật trong `repo`, PATH = path_dirs + PATH hiện có; trả nhật ký (sau khi chờ tiến trình nền)."""
    log.write_text("", encoding="utf-8")
    env = dict(os.environ, LOG=str(log).replace("\\", "/"),
               PATH=os.pathsep.join([str(p).replace("\\", "/") for p in path_dirs] + [os.environ["PATH"]]))
    try:
        subprocess.run(["bash", "-c", cmd], cwd=str(repo), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=timeout)
    except subprocess.TimeoutExpired:
        pass
    return log.read_text(encoding="utf-8")


def main(argv: list[str]) -> int:
    """Chạy tay: đo guard đọc chuỗi (E1) so với shell thật, và (nếu có shims/) shim (E2)."""
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    sys.path.insert(0, str(here.parent / "scripts"))
    import io, json  # noqa: E401
    import autopilot_guard
    import test_autopilot_guard as helper

    n_danger, n_safe, seed = int(argv[0]), int(argv[1]), int(argv[2])
    danger, safe = build_cases(seed, n_danger, n_safe)
    with tempfile.TemporaryDirectory(prefix="oracle_") as tmp:
        work = Path(tmp)
        repo = helper.protected_repo(work, branch="x")
        stub_dir, log = work / "stub", work / "log.txt"
        make_stub(stub_dir)
        shim_dir = here.parent / "shims"

        def guard_blocks(cmd: str) -> bool:
            out, err = io.StringIO(), io.StringIO()
            code = autopilot_guard.main(["--format", "claude"], stdin=io.StringIO(json.dumps(helper.claude(cmd, repo))), stdout=out, stderr=err)
            return code == 2 or "permissionDecision" in out.getvalue()

        res = {"danger_executed": 0, "e1_miss": 0, "e2_miss": 0, "safe_executed": 0, "e1_fp": 0, "e2_fp": 0}
        for cmd in danger:
            if danger_in(run_bash(cmd, repo, log, [stub_dir])):
                res["danger_executed"] += 1
                res["e1_miss"] += 0 if guard_blocks(cmd) else 1
                if shim_dir.is_dir() and danger_in(run_bash(cmd, repo, log, [shim_dir, stub_dir])):
                    res["e2_miss"] += 1
        for cmd in safe:
            if "RUN" in run_bash(cmd, repo, log, [stub_dir]):
                res["safe_executed"] += 1
                res["e1_fp"] += 1 if guard_blocks(cmd) else 0
                if shim_dir.is_dir() and "RUN" not in run_bash(cmd, repo, log, [shim_dir, stub_dir]):
                    res["e2_fp"] += 1
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
