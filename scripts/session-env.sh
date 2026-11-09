#!/bin/sh
# Hook SessionStart (SPR-16c): ghi vao $CLAUDE_ENV_FILE de moi lenh Bash cua phien co shims/ dung dau PATH va AGENT_AGILE_SHIM=1.
# Noi dung tep moi truong nam NGOAI chuoi lenh nen Claude Code khong hoi quyen "PATH assignment" (khac cach viet lai lenh, chi chay o auto/bypass), va duoc nap
# truoc moi lenh Bash o MOI che do quyen, ke ca khi Git Bash dang nhap sap lai PATH. PowerShell khong dung duoc tep nay (tai lieu: chi nhan dong gan thuan).
# Khong lam gi (thoat 0) khi: khong co $CLAUDE_ENV_FILE, AGENT_AGILE_SHIM=0, hoac khong co thu muc shims/ canh script. Khong doc stdin, khong lam hong phien.
[ -n "$CLAUDE_ENV_FILE" ] || exit 0
[ "$AGENT_AGILE_SHIM" = 0 ] && exit 0
self=$0
command -v cygpath >/dev/null 2>&1 && self=$(cygpath -u "$0" 2>/dev/null || printf '%s' "$0")  # Windows: CLAUDE_PLUGIN_ROOT co the dung dau gach nguoc
here=${self%/*}
[ "$here" = "$self" ] && here=.
shims=$(cd "$here/../shims" 2>/dev/null && pwd) || exit 0
[ -f "$shims/git" ] || exit 0
if command -v cygpath >/dev/null 2>&1; then
  shims=$(cygpath -u "$shims" 2>/dev/null || printf '%s' "$shims")  # Git Bash: duong kieu MSYS (/c/...)
fi
quoted=$(printf '%s' "$shims" | sed "s/'/'\\\\''/g")
{
  printf '%s\n' "case \":\$PATH:\" in *\":\"'$quoted'\":\"*) ;; *) export PATH='$quoted':\"\$PATH\" ;; esac"
  printf '%s\n' "export AGENT_AGILE_SHIM=1"
} >> "$CLAUDE_ENV_FILE" 2>/dev/null
exit 0
