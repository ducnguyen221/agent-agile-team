"""SPR-20 TK22: `autopilot_guard.py` với MỘT chế độ autopilot: file dấu hợp lệ chặn bảy mục luôn-chặn; khoá `mode`/`exclusions`
của file dấu kiểu cũ bị bỏ qua; file hỏng chặn cả 13 mục.

Phần kiểm lệnh git (đẩy, tag, gộp, rào git thường trực, `_keep_ask`) đã gỡ ở SPR-20 TK21; phần hai chế độ gỡ ở TK22.
"""

from __future__ import annotations

import pytest

import _autopilot_rules as rules
import autopilot_guard
from test_autopilot_guard import ALL, assert_blocked, claude, good_marker, make_repo, run

ALWAYS = set(rules.OPEN_ALWAYS_BLOCKED)


def marker_path(repo):
    return str(repo / ".tmp" / "autopilot.json")


def test_marker_active_set_is_the_seven_always_blocked_items(tmp_path):
    repo = make_repo(tmp_path, marker=good_marker())
    active, broken = autopilot_guard.load_active(marker_path(repo))
    assert not broken and active == ALWAYS and len(active) == 7


@pytest.mark.parametrize("legacy", [
    {"mode": "open"}, {"mode": "secure"}, {"mode": "wide"}, {"exclusions": ["tag", "publish"]}, {"exclusions": "all"},
    {"exclusions": []}, {"mode": "open", "exclusions": ["not_an_item"]},
], ids=["mode-open", "mode-secure", "mode-unknown", "extra-items", "bad-shape", "empty", "open-unknown-item"])
def test_legacy_mode_and_exclusions_keys_are_ignored(tmp_path, legacy):
    marker = good_marker()
    marker.update(legacy)
    repo = make_repo(tmp_path, marker=marker)
    active, broken = autopilot_guard.load_active(marker_path(repo))
    assert not broken and active == ALWAYS


def test_marker_without_exclusions_key_is_valid(tmp_path):
    marker = good_marker()
    marker.pop("exclusions")
    repo = make_repo(tmp_path, marker=marker)
    active, broken = autopilot_guard.load_active(marker_path(repo))
    assert not broken and active == ALWAYS


def test_marker_keeps_blocking_recursive_delete(tmp_path):
    assert_blocked(make_repo(tmp_path, branch="release", marker=good_marker()), "rm -rf build", "irreversible_delete")


def test_marker_is_still_protected_file(tmp_path):
    repo = make_repo(tmp_path, branch="release", marker=good_marker())
    rc, _, err = run("claude", claude("rm .tmp/autopilot.json", repo))
    assert rc == 2 and "file dấu" in err


@pytest.mark.parametrize("text", ["{not json", "[]", '"x"'], ids=["not-json", "list", "string"])
def test_corrupt_marker_blocks_thirteen(tmp_path, text):
    repo = make_repo(tmp_path, marker=text)
    active, broken = autopilot_guard.load_active(marker_path(repo))
    assert broken and set(active) == set(ALL)
