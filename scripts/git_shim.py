#!/usr/bin/env python3
"""Shim `git`/`gh` kiểm argv THẬT (thử nghiệm SPR-16b, chưa bật ở đâu).

Vì sao có: rào autopilot_guard đọc CHUỖI lệnh nên luôn phải đoán shell sẽ chạy gì (nháy, chuyển hướng, wrapper, hai phương ngữ). Shim đứng trước
`PATH` nhận đúng argv mà hệ điều hành đã giải xong, nên mọi che giấu cú pháp biến mất: `g"i"t -c x.y="a;b" push --force`, `xargs … sh -c`, `eval`… đều
tới đây thành cùng một argv. Shim dựng lại một lệnh CHUẨN từ argv rồi hỏi chính `autopilot_guard` (một bộ luật, không chép), cho chạy thật
(`git`/`gh` thật dò trên PATH đã bỏ thư mục shim) hay từ chối.

Giới hạn (ghi thẳng, không giấu): chỉ thấy lệnh gọi BẰNG TÊN qua PATH; gọi bằng đường tuyệt đối (`/usr/bin/git`), `command -p git`, hay tiến trình tự đặt lại PATH
tránh được shim (lớp đọc chuỗi của guard vẫn bắt các dạng đơn giản). Chỉ có tác dụng khi thư mục shim đứng trước trong PATH của phiên.

Dùng: `git_shim.py <git|gh> [đối số…]`. Thư mục shim lấy từ biến `AGENT_SHIM_DIR` (bỏ khỏi PATH khi dò lệnh thật và khi guard gọi git).
Mã thoát: của lệnh thật khi cho chạy; 1 khi từ chối (lý do ở stderr); 127 khi không tìm thấy lệnh thật.
"""
from __future__ import annotations

import io
import json
import os
import shlex
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IGNORED_ENV = frozenset({"GIT_EXEC_PATH", "GIT_TERMINAL_PROMPT", "GIT_PAGER", "GIT_EDITOR", "GIT_SEQUENCE_EDITOR", "GIT_ASKPASS", "GH_PROMPT_DISABLED", "GH_NO_UPDATE_NOTIFIER"})


def clean_path(shim_dir: str | None, path: str) -> str:
    """PATH không còn thư mục shim (so theo đường chuẩn hoá, không phân biệt hoa thường trên Windows)."""
    if not shim_dir:
        return path
    drop = os.path.normcase(os.path.realpath(shim_dir))
    kept = [p for p in path.split(os.pathsep) if p and os.path.normcase(os.path.realpath(p)) != drop]
    return os.pathsep.join(kept)


def canonical_command(name: str, argv: list[str], environ) -> str:
    """Lệnh chuẩn dựng từ argv: một lệnh đơn, nháy POSIX đầy đủ; biến GIT_*/GH_* đang có trong môi trường đi trước (guard coi chúng làm hợp đồng đích không áp)."""
    prefix = [k + "=" + shlex.quote(environ[k]) for k in sorted(environ) if k.startswith(("GIT_", "GH_")) and k not in IGNORED_ENV]
    return " ".join(prefix + [name, shlex.join(argv)]).strip()


def decide(name: str, argv: list[str], environ=None, cwd: str | None = None) -> tuple[bool, str]:
    """(được chạy?, lý do nếu không). Dùng đúng `autopilot_guard.main` với tool Bash: một bộ luật cho cả hook lẫn shim."""
    environ = os.environ if environ is None else environ
    sys.path.insert(0, HERE)
    import autopilot_guard  # noqa: E402  (đứng ở đây để import lỗi vẫn thành đường 'từ chối', xem main)

    payload = {"tool_name": "Bash", "tool_input": {"command": canonical_command(name, argv, environ)}, "cwd": cwd or os.getcwd()}
    out, err = io.StringIO(), io.StringIO()
    code = autopilot_guard.main(["--format", "claude"], stdin=io.StringIO(json.dumps(payload)), stdout=out, stderr=err)
    text = out.getvalue().strip()
    if text:  # JSON `ask` (Claude): shim không có tầng hỏi nên coi như từ chối
        try:
            answer = json.loads(text)["hookSpecificOutput"]
            if answer.get("permissionDecision") in ("ask", "deny"):
                return False, str(answer.get("permissionDecisionReason", ""))
        except (ValueError, KeyError, TypeError):
            return False, "git-shim: đầu ra guard không đọc được — từ chối"
    if code != 0:
        return False, err.getvalue().strip() or "git-shim: guard từ chối"
    return True, ""


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("git", "gh"):
        sys.stderr.write("git-shim: dùng `git_shim.py <git|gh> [đối số…]`\n")
        return 2
    name, args = argv[0], argv[1:]
    shim_dir = os.environ.get("AGENT_SHIM_DIR")
    path = clean_path(shim_dir, os.environ.get("PATH", ""))
    os.environ["PATH"] = path  # guard gọi `git` (runner) và lệnh thật đều không đi lại qua shim
    try:
        allowed, reason = decide(name, args)
    except Exception as exc:  # shim hỏng: đóng an toàn (từ chối) — lớp ruleset/pre-push mới là rào cứng
        allowed, reason = False, "git-shim: lỗi {} — từ chối".format(type(exc).__name__)
    if not allowed:
        sys.stderr.write((reason or "git-shim: từ chối") + "\n(git-shim: lệnh không chạy; Đức tự chạy lệnh này nếu cần)\n")
        return 1
    real = shutil.which(name, path=path)
    if real is None:
        sys.stderr.write("git-shim: không tìm thấy `{}` thật trên PATH\n".format(name))
        return 127
    return subprocess.call([real] + args)


if __name__ == "__main__":
    sys.exit(main())
