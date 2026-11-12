"""SPR-20 TK4: `autopilot_guard.py` theo `mode` của file dấu (FR1.3, FR2.3, FR4.2, SC2).

Chế độ mở chặn 7 mục luôn chặn, mục file dấu ghi thêm và gộp cục bộ vào `main` (`main-local-merge`); push, tag, version… do rào git
(`git_fence`) và hợp đồng đích quyết ở TK5. File dấu `mode: secure` hoặc vắng `mode` giữ hành vi cũ.
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


def test_secure_marker_missing_mode_blocks_push(tmp_path):
    repo = make_repo(tmp_path, marker=good_marker())
    assert_blocked(repo, "git push origin feat", "push")


def test_secure_marker_explicit_mode_keeps_thirteen(tmp_path):
    marker = good_marker()
    marker["mode"] = "secure"
    repo = make_repo(tmp_path, marker=marker)
    active, _ = autopilot_guard.load_active(str(repo / ".tmp" / "autopilot.json"))
    assert set(active) == set(ALL) - {"branch_merge_local"} | {"branch_merge_local"} & set(ALL)
    assert_blocked(repo, "git push origin feat", "push")


def test_open_marker_merge_on_release_passes(tmp_path):
    assert_allowed(make_repo(tmp_path, branch="release", marker=open_marker()), "git merge feat")


def test_open_marker_merge_on_main_blocked(tmp_path):
    assert_blocked(make_repo(tmp_path, branch="main", marker=open_marker()), "git merge feat", "main-local-merge")


def test_open_marker_pull_on_main_blocked(tmp_path):
    assert_blocked(make_repo(tmp_path, branch="main", marker=open_marker()), "git pull origin main", "main-local-merge")


def test_open_marker_pull_ff_only_on_main_blocked_when_repo_not_push_only(tmp_path):
    assert_blocked(make_repo(tmp_path, branch="main", marker=open_marker()), "git pull --ff-only", "main-local-merge")


def test_open_marker_checkout_main_then_merge_blocked(tmp_path):
    assert_blocked(make_repo(tmp_path, branch="release", marker=open_marker()), "git checkout main && git merge feat", "main-local-merge")


@pytest.mark.parametrize("cmd,item", [("rm -rf build", "irreversible_delete"), ("git reset --hard HEAD~1", "irreversible_delete")])
def test_open_marker_keeps_always_blocked_items(tmp_path, cmd, item):
    assert_blocked(make_repo(tmp_path, branch="release", marker=open_marker()), cmd, item)


def test_open_marker_extra_blocks_tag_that_open_mode_would_allow(tmp_path):
    assert_blocked(make_repo(tmp_path, branch="release", marker=open_marker(["tag"])), "git tag v1.0.0", "tag")


def test_open_marker_is_still_protected_file(tmp_path):
    repo = make_repo(tmp_path, branch="release", marker=open_marker())
    rc, _, err = run("claude", claude("rm .tmp/autopilot.json", repo))
    assert rc == 2 and "file dấu" in err


def _force_level(monkeypatch, level):
    sig = autopilot_guard.git_fence.Signals(listed=True, level=level, marker=True)
    monkeypatch.setattr(autopilot_guard.git_fence, "protection", lambda *a, **k: sig)


def test_open_marker_pull_ff_only_on_main_passes_when_repo_is_push_only(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, branch="main", marker=open_marker())
    _force_level(monkeypatch, "push-only")
    rc, _, err = run("claude", claude("git pull --ff-only", repo))
    assert "main-local-merge" not in err, err


def test_open_marker_plain_pull_on_main_still_blocked_when_repo_is_push_only(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, branch="main", marker=open_marker())
    _force_level(monkeypatch, "push-only")
    assert_blocked(repo, "git pull origin main", "main-local-merge")


def test_open_marker_pull_ff_only_on_main_blocked_when_repo_is_full(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, branch="main", marker=open_marker())
    _force_level(monkeypatch, "full")
    assert_blocked(repo, "git pull --ff-only", "main-local-merge")


def test_corrupt_marker_blocks_thirteen(tmp_path):
    repo = make_repo(tmp_path, marker="{not json")
    active, broken = autopilot_guard.load_active(str(repo / ".tmp" / "autopilot.json"))
    assert broken and set(active) == set(ALL)
