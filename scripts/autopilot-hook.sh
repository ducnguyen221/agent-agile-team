#!/bin/sh
# Launcher cho hook autopilot (scripts/autopilot_guard.py): POSIX sh, không cần Python để chạy.
# Thử lần lượt `python3`, `python`, `py -3`, mỗi cái phải là Python >= 3.9; cái đầu tiên đạt thì `exec` nó với
# autopilot_guard.py và các tham số của launcher (stdin đi thẳng). Không có cái nào đạt: tự dò file dấu `.tmp/autopilot.json`
# (không phân biệt hoa thường) đi lên từ $CLAUDE_PROJECT_DIR và $PWD tới thư mục có `.git`; có thì chặn (thoát 2), không thì cho qua (thoát 0).
# Chỉ dùng lệnh dựng sẵn của sh ở nhánh dự phòng, nên chạy được cả khi PATH rỗng.

here=${0%/*}
[ "$here" = "$0" ] && here=.
here=$(cd "$here" 2>/dev/null && pwd) || here=.
guard="$here/autopilot_guard.py"

for candidate in "python3" "python" "py -3"; do
  # shellcheck disable=SC2086 -- `py -3` cần tách từ
  if $candidate -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
    # shellcheck disable=SC2086
    exec $candidate "$guard" "$@"
  fi
done

has_marker() {
  cur=${1%/}
  [ -n "$1" ] || return 1
  while :; do
    if [ -d "$cur/.tmp" ]; then
      for entry in "$cur"/.tmp/*; do
        [ -e "$entry" ] || continue
        case ${entry##*/} in
          [Aa][Uu][Tt][Oo][Pp][Ii][Ll][Oo][Tt].[Jj][Ss][Oo][Nn]) return 0 ;;
        esac
      done
    fi
    [ -e "$cur/.git" ] && return 1
    case $cur in
      */*) ;;
      *) return 1 ;;
    esac
    parent=${cur%/*}
    if [ -z "$parent" ]; then
      [ "$cur" = "/" ] && return 1
      parent=/
    fi
    [ "$parent" = "$cur" ] && return 1
    cur=$parent
  done
}

if has_marker "$CLAUDE_PROJECT_DIR" || has_marker "$PWD"; then
  echo "autopilot: không chạy được Python để kiểm lệnh — chặn vì đang bật autopilot" >&2
  exit 2
fi
exit 0
