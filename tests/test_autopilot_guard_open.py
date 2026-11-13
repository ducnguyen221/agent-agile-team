"""SPR-20 TK4: `autopilot_guard.py` theo `mode` của file dấu (FR1.3, FR4.2, SC2): bộ mục đang chặn của chế độ mở và chế độ chặt.

Phần kiểm lệnh git (đẩy, tag, gộp, rào git thường trực, `_keep_ask`) đã gỡ ở SPR-20 TK21; phần chế độ dời TK22.
"""

from __future__ import annotations

import pytest

import _autopilot_rules as rules
import autopilot_guard
from test_autopilot_guard import ALL, assert_allowed, assert_blocked, claude, good_marker, make_repo, run

OPEN_ALWAYS = sorted(rules.OPEN_ALWAYS_BLOCKED)


def open_marker(extra=()):
    marker = good_marker(OPEN_ALWAYS + list(extra))
    marker["mode"] = "open"
    return marker


def test_open_marker_active_set_is_seven_plus_internal_code(tmp_path):
    repo = make_repo(tmp_path, marker=open_marker())
    active, broken = autopilot_guard.load_active(str(repo / ".tmp" / "autopilot.json"))
    assert not broken and active == set(OPEN_ALWAYS) | {autopilot_guard.MAIN_LOCAL_MERGE}


def test_open_marker_extra_exclusions_are_added(tmp_path):
    repo = make_repo(tmp_path, marker=open_marker(["tag", "publish"]))
    active, _ = autopilot_guard.load_active(str(repo / ".tmp" / "autopilot.json"))
    assert {"tag", "publish"} <= active and len(active) == 10


def test_open_marker_unknown_extra_item_is_ignored(tmp_path):
    repo = make_repo(tmp_path, marker=open_marker(["not_an_item"]))
    active, broken = autopilot_guard.load_active(str(repo / ".tmp" / "autopilot.json"))
    assert not broken and "not_an_item" not in active


def test_open_marker_bad_exclusions_key_closes_to_all_thirteen(tmp_path):
    marker = open_marker()
    marker["exclusions"] = "all"
    repo = make_repo(tmp_path, marker=marker)
    active, broken = autopilot_guard.load_active(str(repo / ".tmp" / "autopilot.json"))
    assert not broken and set(ALL) <= active


def test_unknown_mode_is_a_corrupt_marker(tmp_path):
    marker = open_marker()
    marker["mode"] = "wide"
    repo = make_repo(tmp_path, marker=marker)
    active, broken = autopilot_guard.load_active(str(repo / ".tmp" / "autopilot.json"))
    assert broken and set(active) == set(ALL)


def test_secure_marker_explicit_mode_keeps_thirteen(tmp_path):
    marker = good_marker()
    marker["mode"] = "secure"
    repo = make_repo(tmp_path, marker=marker)
    active, _ = autopilot_guard.load_active(str(repo / ".tmp" / "autopilot.json"))
    assert set(active) == set(ALL) - {"branch_merge_local"} | {"branch_merge_local"} & set(ALL)


@pytest.mark.parametrize("cmd,item", [("rm -rf build", "irreversible_delete")])
def test_open_marker_keeps_always_blocked_items(tmp_path, cmd, item):
    assert_blocked(make_repo(tmp_path, branch="release", marker=open_marker()), cmd, item)


def test_open_marker_is_still_protected_file(tmp_path):
    repo = make_repo(tmp_path, branch="release", marker=open_marker())
    rc, _, err = run("claude", claude("rm .tmp/autopilot.json", repo))
    assert rc == 2 and "file dấu" in err


def test_corrupt_marker_blocks_thirteen(tmp_path):
    repo = make_repo(tmp_path, marker="{not json")
    active, broken = autopilot_guard.load_active(str(repo / ".tmp" / "autopilot.json"))
    assert broken and set(active) == set(ALL)
