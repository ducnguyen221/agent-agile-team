#!/bin/sh
# Launcher cho hook autopilot (scripts/autopilot_guard.py): POSIX sh, không cần Python để chạy.
# Đọc sự kiện ở stdin một lần vào biến, rồi gọi thẳng guard bằng `python3`, `python`, `py -3` theo thứ tự (không dò phiên bản bằng tiến trình
# riêng, để mỗi lệnh chỉ tốn một lần khởi động Python; guard tự xử khi Python quá cũ). Guard trả 0 hoặc 2 thì trả nguyên mã (kèm
# stdout/stderr của guard). Guard vắng, Python không có, hoặc mọi ứng viên trả mã khác (lỗi cú pháp, import hỏng, traceback) thì KHÔNG
# trả mã đó mà tự dò file dấu `.tmp/autopilot.json`
# (không phân biệt hoa thường) đi lên từ $CLAUDE_PROJECT_DIR và $PWD tới thư mục có `.git`: có thì chặn (thoát 2), không thì cho qua (thoát 0).
# `--clear <thư mục>` không đọc stdin. Guard luôn là autopilot_guard.py cạnh chính launcher (không có biến môi trường đổi đường).
# Nhánh dự phòng chỉ dùng lệnh dựng sẵn của sh, nên chạy được cả khi PATH rỗng.

here=${0%/*}
[ "$here" = "$0" ] && here=.
here=$(cd "$here" 2>/dev/null && pwd) || here=.
guard=$here/autopilot_guard.py

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

# Dấu hiệu 2 của rào git thường trực (method/git-permissions.md): có `.agile.json` ở một thư mục tổ tiên tới thư mục có `.git`.
has_agile() {
  cur=${1%/}
  [ -n "$1" ] || return 1
  while :; do
    [ -e "$cur/.agile.json" ] && return 0
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

reason="autopilot: không chạy được Python để kiểm lệnh — chặn vì đang bật autopilot"

if [ -f "$guard" ]; then
  stdin_needed=1
  [ "$1" = "--clear" ] && stdin_needed=0
  event=
  if [ "$stdin_needed" = 1 ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      event="$event$line
"
    done
  fi
  for candidate in "python3" "python" "py -3"; do
    found=$(command -v "${candidate%% *}" 2>/dev/null) || continue
    case $found in
      *[Ww]indows[Aa]pps*) continue ;; # stub của Microsoft Store (không phải Python thật, mỗi lần gọi tốn ~0,2 s)
    esac
    if [ "$stdin_needed" = 1 ]; then
      # shellcheck disable=SC2086 -- `py -3` cần tách từ
      printf '%s' "$event" | $candidate "$guard" "$@"
    else
      # shellcheck disable=SC2086
      $candidate "$guard" "$@" </dev/null
    fi
    code=$?
    if [ "$code" = 0 ] || [ "$code" = 2 ]; then
      exit "$code"
    fi
    # 126/127: không chạy được lệnh; mã khác (traceback, lỗi cú pháp, Python quá cũ, stub của Store): thử ứng viên kế rồi mới dò bằng sh
    [ "$code" = 126 ] || [ "$code" = 127 ] || reason="autopilot: guard lỗi — chặn vì đang bật autopilot"
  done
fi

if has_marker "$CLAUDE_PROJECT_DIR" || has_marker "$PWD"; then
  echo "$reason" >&2
  exit 2
fi
# Dấu hiệu 3: chỉ mục còn `.agile.json` (kể cả khi file đã bị xoá khỏi cây làm việc). Cần `git`; không có thì bỏ qua dấu hiệu này.
# Dấu hiệu 1 (danh sách bảo vệ, JSON) không dò được ở nhánh dự phòng: mất mức bảo vệ đó khi Python lỗi (method/git-permissions.md mục 8).
has_indexed_agile() {
  [ -n "$1" ] || return 1
  command -v git >/dev/null 2>&1 || return 1
  git -C "$1" ls-files --error-unmatch -- ':/.agile.json' >/dev/null 2>&1
}

if has_agile "$CLAUDE_PROJECT_DIR" || has_agile "$PWD" || has_indexed_agile "$CLAUDE_PROJECT_DIR" || has_indexed_agile "$PWD"; then
  echo "git-fence: không chạy được guard (Python hay guard lỗi) — chặn vì repo được bảo vệ (.agile.json); cần Đức nói trong chat" >&2
  exit 2
fi
exit 0
