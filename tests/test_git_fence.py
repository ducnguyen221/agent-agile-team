"""`scripts/git_fence.py` (SPR-16 TK8, FR4): bốn dấu hiệu, bảng quyền, hợp đồng đích, mất dấu hiệu, `gh`.

File test này thuộc bộ ghim của test đột biến (`PINNED_SUITES`). Repo thử là thư mục thật trong `tmp_path` (có `.git/HEAD`, `config`,
`refs/remotes/*/HEAD`); lời gọi `git` đi qua `Fake` nên không cần git thật.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import git_fence as gf

URL = "https://github.com/acme/shop.git"
TARGET = "refs/heads/spr-31-export"
INDEX_CALL = ("git", "ls-files", "--error-unmatch", "--", ":/.agile.json")
PUSH_URL_CALL = ("git", "remote", "get-url", "--push", "--all", "origin")


class Fake:
    """Runner giả: bảng lệnh → (mã thoát, stdout); lệnh lạ trả mã -1 (như quá giờ)."""

    def __init__(self, table=None):
        self.table = dict(table or {})
        self.calls = []

    def __call__(self, argv, cwd, timeout):
        self.calls.append(tuple(argv))
        return self.table.get(tuple(argv), (-1, ""))


def make_repo(tmp_path, name="repo", branch="main", agile=False, urls=(URL,), default="main", worktree_of=None):
    repo = tmp_path / name
    git = repo / ".git"
    git.mkdir(parents=True)
    (git / "HEAD").write_text("ref: refs/heads/{}\n".format(branch), encoding="utf-8")
    lines = "".join('[remote "origin"]\n\turl = {}\n'.format(u) for u in urls)
    (git / "config").write_text(lines, encoding="utf-8")
    if default:
        remotes = git / "refs" / "remotes" / "origin"
        remotes.mkdir(parents=True)
        (remotes / "HEAD").write_text("ref: refs/remotes/origin/{}\n".format(default), encoding="utf-8")
    if agile:
        (repo / ".agile.json").write_text("{}", encoding="utf-8")
    return repo


def make_worktree(main: Path, tmp_path, name="wt", branch="spr-31-export"):
    """Worktree của `main`: `.git` là file `gitdir:` trỏ vào `main/.git/worktrees/<name>` có `commondir`."""
    admin = main / ".git" / "worktrees" / name
    admin.mkdir(parents=True)
    (admin / "HEAD").write_text("ref: refs/heads/{}\n".format(branch), encoding="utf-8")
    (admin / "commondir").write_text("../..\n", encoding="utf-8")
    tree = tmp_path / name
    tree.mkdir()
    (tree / ".git").write_text("gitdir: {}\n".format(admin.as_posix()), encoding="utf-8")
    return tree


def write_list(tmp_path, repo, level="full", branches=(), urls=(URL,)):
    path = tmp_path / "protected.json"
    path.write_text(json.dumps({"repos": [{"git_common_dir": str(repo / ".git"), "remote_urls": list(urls),
                                           "protected_branches": list(branches), "level": level}]}), encoding="utf-8")
    return {gf.ENV_LIST: str(path)}


def seg(cmd, cwd, redirected=False, cd=False):
    tokens = cmd.split()
    name, args = tokens[0], tokens[1:]
    if name == "git":
        globals_, sub, rest = gf.split_git_args(args)
        where = [None] if redirected or cd else [str(cwd)]
        for index, item in enumerate(globals_):
            if item == "-C" and index + 1 < len(globals_):
                where = [os.path.normpath(os.path.join(str(cwd), globals_[index + 1]))]
        return gf.Segment("git", args, sub, rest, where, redirected, globals_)
    return gf.Segment(name, args)


CONTRACT = {"push_remote": "origin", "push_urls": [URL], "push_targets": [TARGET], "git_common_dir": ""}


def ctx_for(cwd, env=None, marker=False, contract=None, fake=None):
    fake = fake or Fake({INDEX_CALL: (0, "")})
    return gf.FenceContext(str(cwd), env or {}, fake, marker=marker, contract=contract)


def verdict(cmd, repo, env=None, marker=False, contract=None, fake=None, **kw):
    return gf.classify([seg(cmd, repo, **kw)], ctx_for(repo, env, marker, contract, fake))


# --- bốn dấu hiệu -------------------------------------------------------------------------------------------------

def test_signal_agile_json_file(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    sig = gf.protection(str(repo), {}, Fake())
    assert sig.config_file and sig.protected and sig.indexed is None and sig.level == "full"


def test_signal_listed_by_common_dir_and_by_url(tmp_path):
    repo = make_repo(tmp_path)
    assert gf.protection(str(repo), write_list(tmp_path, repo, urls=()), Fake()).listed is True
    other = make_repo(tmp_path, name="other", urls=("git@github.com:acme/other.git",))
    env = write_list(tmp_path, repo, urls=("https://github.com/acme/other.git",))
    env[gf.ENV_LIST] = env[gf.ENV_LIST]
    data = json.loads(Path(env[gf.ENV_LIST]).read_text(encoding="utf-8"))
    data["repos"][0]["git_common_dir"] = ""
    Path(env[gf.ENV_LIST]).write_text(json.dumps(data), encoding="utf-8")
    assert gf.protection(str(other), env, Fake()).listed is True  # khớp URL scp-like
    assert gf.protection(str(repo), env, Fake()).listed is False


def test_signal_indexed_via_git_ls_files(tmp_path):
    repo = make_repo(tmp_path)
    fake = Fake({INDEX_CALL: (0, "")})
    sig = gf.protection(str(repo), {}, fake)
    assert sig.indexed is True and sig.protected and fake.calls == [INDEX_CALL]


def test_signal_indexed_from_subdirectory_uses_root_pathspec(tmp_path):
    repo = make_repo(tmp_path)
    sub = repo / "a" / "b"
    sub.mkdir(parents=True)
    fake = Fake({INDEX_CALL: (0, "")})
    assert gf.protection(str(sub), {}, fake).indexed is True


def test_signal_marker(tmp_path):
    repo = make_repo(tmp_path)
    sig = gf.protection(str(repo), {}, Fake({INDEX_CALL: (1, "")}), marker=True)
    assert sig.marker and sig.protected and sig.indexed is False


def test_no_signal_means_not_protected(tmp_path):
    repo = make_repo(tmp_path)
    sig = gf.protection(str(repo), {}, Fake({INDEX_CALL: (1, "")}))
    assert not sig.protected and sig.indexed is False
    assert verdict("git push origin HEAD:main", repo, fake=Fake({INDEX_CALL: (1, "")})).kind == gf.NONE


@pytest.mark.parametrize("answer", [(-1, ""), (128, "")], ids=["timeout", "not-a-repo"])
def test_index_failure_is_unknown_not_protected(tmp_path, answer):
    repo = make_repo(tmp_path)
    sig = gf.protection(str(repo), {}, Fake({INDEX_CALL: answer}))
    assert sig.indexed is None and not sig.protected


def test_git_not_called_when_other_signal_present(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    fake = Fake()
    gf.protection(str(repo), {}, fake)
    assert fake.calls == []


def test_budget_stops_calls_after_the_total():
    now = [0.0]
    budget = gf.Budget(Fake({("x",): (0, "ok")}), total=4.0, clock=lambda: now[0])
    assert budget.run(["x"], ".") == (0, "ok")
    now[0] = 4.5
    assert budget.run(["x"], ".") == (-1, "")


def test_broken_list_is_unknown(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    sig = gf.protection(str(repo), {gf.ENV_LIST: str(bad)}, Fake())
    assert sig.listed is None and sig.config_file and sig.level == "full"


# --- bảng quyền, mức full ---------------------------------------------------------------------------------------

def test_push_without_marker_asks(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    got = verdict("git push origin HEAD:main", repo)
    assert got.kind == gf.ASK and "push" in got.reason


@pytest.mark.parametrize("cmd", ["git push --force origin x", "git push -f origin x", "git push origin +x", "git push --delete origin x",
                                 "git push --mirror", "git push --tags", "git push --all", "git push origin :x",
                                 "git push --force-with-lease origin x"])
def test_forced_push_is_forbidden(tmp_path, cmd):
    repo = make_repo(tmp_path, agile=True)
    assert verdict(cmd, repo).kind == gf.FORBID


@pytest.mark.parametrize("sub", ["commit -m x", "pull", "reset HEAD~1", "rebase main", "cherry-pick abc"])
def test_local_history_commands_on_main_are_forbidden_at_full(tmp_path, sub):
    repo = make_repo(tmp_path, agile=True)
    assert verdict("git " + sub, repo).kind == gf.FORBID


@pytest.mark.parametrize("sub", ["status", "log", "diff", "fetch", "branch", "checkout -b x", "switch x", "stash list"])
def test_read_and_neutral_commands_pass(tmp_path, sub):
    repo = make_repo(tmp_path, agile=True)
    assert verdict("git " + sub, repo).kind == gf.NONE


def test_commit_on_feature_branch_passes(tmp_path):
    repo = make_repo(tmp_path, branch="spr-31-export", agile=True)
    assert verdict("git commit -m x", repo).kind == gf.NONE


def test_merge_on_main_asks_and_off_main_passes(tmp_path):
    assert verdict("git merge x", make_repo(tmp_path, agile=True)).kind == gf.ASK
    assert verdict("git merge x", make_repo(tmp_path, name="f", branch="x", agile=True)).kind == gf.NONE


def test_protected_branch_from_default_and_list(tmp_path):
    repo = make_repo(tmp_path, branch="develop", agile=True, default="develop")
    assert verdict("git commit -m x", repo).kind == gf.FORBID
    repo2 = make_repo(tmp_path, name="r2", branch="release", agile=True)
    assert verdict("git commit -m x", repo2).kind == gf.NONE
    env = write_list(tmp_path, repo2, branches=("release",))
    assert verdict("git commit -m x", repo2, env=env).kind == gf.FORBID


def test_unknown_branch_is_treated_as_protected(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    (repo / ".git" / "HEAD").write_text("0123456789abcdef\n", encoding="utf-8")  # detached
    assert verdict("git commit -m x", repo).kind == gf.FORBID
    assert verdict("git commit -m x", make_repo(tmp_path, name="c", agile=True), cd=True).kind == gf.FORBID  # đã đổi thư mục


@pytest.mark.parametrize("cmd,expected", [
    ("git tag v1.0", gf.ASK), ("git tag", gf.NONE), ("git tag -l", gf.NONE), ("git tag -d v1", gf.FORBID),
    ("git remote -v", gf.NONE), ("git remote set-url origin x", gf.FORBID), ("git remote add o x", gf.FORBID),
    ("git remote rename a b", gf.FORBID), ("git remote remove o", gf.FORBID),
    ("git config user.name x", gf.NONE), ("git config remote.origin.url x", gf.FORBID), ("git config url.x.insteadOf y", gf.FORBID),
    ("git config core.hooksPath h", gf.FORBID), ("git config --get remote.origin.url", gf.NONE), ("git config --list", gf.NONE),
    ("git commit --no-verify -m x", gf.FORBID), ("git push --no-verify origin x", gf.FORBID),
    ("git -c core.hooksPath=h push origin x", gf.FORBID),
])
def test_command_groups_at_full(tmp_path, cmd, expected):
    repo = make_repo(tmp_path, branch="x", agile=True)
    assert verdict(cmd, repo).kind == expected, cmd


# --- mức push-only ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd,expected", [
    ("git commit -m x", gf.AUTO), ("git pull --ff-only", gf.AUTO), ("git pull", gf.ASK),
    ("git reset HEAD~1", gf.ASK), ("git rebase main", gf.ASK), ("git cherry-pick abc", gf.ASK),
    ("git merge x", gf.ASK), ("git push origin HEAD:main", gf.ASK), ("git push --force origin x", gf.FORBID),
    ("git tag v1", gf.ASK), ("git remote set-url origin x", gf.FORBID),
])
def test_push_only_level(tmp_path, cmd, expected):
    repo = make_repo(tmp_path)
    env = write_list(tmp_path, repo, level="push-only")
    assert verdict(cmd, repo, env=env).kind == expected, cmd


def test_hoso_commit_on_main_in_push_only_repo(tmp_path):
    """Ca ghi hồ sơ sprint thẳng trên main ở repo mức push-only (DN1 b): commit tự do, đẩy vẫn hỏi."""
    repo = make_repo(tmp_path)
    env = write_list(tmp_path, repo, level="push-only")
    assert verdict("git commit -m ghi-ho-so", repo, env=env).kind == gf.AUTO
    assert verdict("git push origin main", repo, env=env).kind == gf.ASK


def test_missing_list_variable_defaults_to_full(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    assert verdict("git commit -m x", repo, env={}).kind == gf.FORBID


# --- file dấu: hỏi thành chặn, hợp đồng đích --------------------------------------------------------------------------

def contract_for(repo, **change):
    value = dict(CONTRACT, git_common_dir=str(repo / ".git"))
    value.update(change)
    return value


def push_world(tmp_path, branch="spr-31-export", default="main", urls=(URL,)):
    repo = make_repo(tmp_path, branch=branch, agile=True, default=default)
    fake = Fake({PUSH_URL_CALL: (0, "\n".join(urls) + "\n"), INDEX_CALL: (0, "")})
    return repo, fake


def listed(repo):
    """Env của danh sách bảo vệ có đúng `repo` (dấu hiệu 1 đúng): điều kiện để hợp đồng đích được áp (FR4.4)."""
    return write_list(repo.parent, repo, urls=())


def push(repo, fake, cmd="git push origin spr-31-export", contract=None, env="listed", **kw):
    return verdict(cmd, repo, env=listed(repo) if env == "listed" else env, marker=True, contract=contract or contract_for(repo),
                   fake=fake, **kw)


def test_marker_turns_ask_into_forbid(tmp_path):
    repo = make_repo(tmp_path, branch="x", agile=True)
    assert verdict("git tag v1", repo, marker=True).kind == gf.FORBID
    assert verdict("git merge y", make_repo(tmp_path, name="m", agile=True), marker=True).kind == gf.FORBID
    assert verdict("git push origin x", repo, marker=True).kind == gf.FORBID  # không hợp đồng


def test_contract_valid(tmp_path):
    repo, fake = push_world(tmp_path)
    assert push(repo, fake).kind == gf.AUTO


def test_contract_valid_refspec_and_head_forms(tmp_path):
    repo, fake = push_world(tmp_path)
    for cmd in ("git push origin HEAD:spr-31-export", "git push origin HEAD:refs/heads/spr-31-export",
                "git push -u origin spr-31-export", "git push origin refs/heads/spr-31-export:refs/heads/spr-31-export"):
        assert push(repo, fake, cmd).kind == gf.AUTO, cmd


def test_contract_valid_from_worktree(tmp_path):
    repo, fake = push_world(tmp_path, branch="main")
    tree = make_worktree(repo, tmp_path)
    assert verdict("git push origin spr-31-export", tree, env=listed(repo), marker=True, contract=contract_for(repo), fake=fake).kind == gf.AUTO


def test_contract_worktree_of_another_repo(tmp_path):
    repo, fake = push_world(tmp_path)
    other = make_repo(tmp_path, name="other", agile=True)
    tree = make_worktree(other, tmp_path, name="otherwt")
    got = verdict("git push origin spr-31-export", tree, env=listed(repo), marker=True, contract=contract_for(repo), fake=fake)
    assert got.kind == gf.FORBID and got.code == "push-repo-unverified"


@pytest.mark.parametrize("cmd,code", [
    ("git push", "push-target-unknown"),
    ("git push origin", "push-target-unknown"),
    ("git push origin a b", "push-multiple-refspecs"),
    ("git push origin +spr-31-export", "push-forced"),
    ("git push --force origin spr-31-export", "push-forced"),
    ("git push --mirror", "push-forced"),
    ("git push --tags origin", "push-forced"),
    ("git push --all origin", "push-forced"),
    (f"git push {URL} spr-31-export", "push-remote-mismatch"),
    ("git push upstream spr-31-export", "push-remote-mismatch"),
    ("git push origin HEAD:main", "push-target-unknown"),
    ("git push origin HEAD:refs/heads/main", "push-target-unknown"),
    ("git push origin spr-99-other", "push-target-unknown"),
    ("git push origin HEAD:refs/tags/v1", "push-target-unknown"),
    ("git push --receive-pack=x origin spr-31-export", "push-flag-forbidden"),
])
def test_contract_rejections(tmp_path, cmd, code):
    repo, fake = push_world(tmp_path)
    got = push(repo, fake, cmd)
    assert got.kind == gf.FORBID and got.code == code, (cmd, got)


def test_contract_pushurl_changed_after_writing(tmp_path):
    repo, fake = push_world(tmp_path, urls=("https://github.com/evil/shop.git",))
    assert push(repo, fake).code == "push-url-mismatch"


def test_contract_multiple_push_urls(tmp_path):
    repo, fake = push_world(tmp_path, urls=(URL, "https://github.com/evil/mirror.git"))
    assert push(repo, fake).code == "push-url-mismatch"


def test_contract_url_lookup_failure_closes(tmp_path):
    repo = make_repo(tmp_path, branch="spr-31-export", agile=True)
    assert push(repo, Fake({INDEX_CALL: (0, "")})).code == "push-url-unverified"


def test_contract_equivalent_url_spellings_match(tmp_path):
    repo, fake = push_world(tmp_path, urls=("git@github.com:acme/shop.git",))
    assert push(repo, fake).kind == gf.AUTO


def test_contract_unknown_default_branch(tmp_path):
    repo, fake = push_world(tmp_path, default=None)
    assert push(repo, fake).code == "push-default-branch-unknown"


def test_contract_target_equals_default_branch(tmp_path):
    repo, fake = push_world(tmp_path, default="spr-31-export")
    got = push(repo, fake)
    assert got.code == "push-target-protected"


def test_contract_other_directory_and_env_redirect(tmp_path):
    repo, fake = push_world(tmp_path)
    other = make_repo(tmp_path, name="o2", agile=True)
    got = verdict(f"git -C {other} push origin spr-31-export", repo, env=listed(repo), marker=True, contract=contract_for(repo), fake=fake)
    assert got.code == "push-repo-unverified"
    redirected = verdict("git push origin spr-31-export", repo, env=listed(repo), marker=True, contract=contract_for(repo), fake=fake, redirected=True)
    assert redirected.code == "push-repo-unverified"
    changed = verdict("git push origin spr-31-export", repo, env=listed(repo), marker=True, contract=contract_for(repo), fake=fake, cd=True)
    assert changed.code == "push-repo-unverified"


def test_contract_config_override_forbidden(tmp_path):
    repo, fake = push_world(tmp_path)
    got = push(repo, fake, "git -c http.proxy=x push origin spr-31-export")
    assert got.kind == gf.FORBID


def test_contract_missing_list_and_unverified_repo(tmp_path):
    repo, fake = push_world(tmp_path)
    got = verdict("git push origin spr-31-export", repo, marker=True, contract=None, fake=fake)
    assert got.kind == gf.FORBID and got.code == "push-repo-unverified"


# --- mất dấu hiệu -----------------------------------------------------------------------------------------------

ROWS = ["listed-agile-removed", "indexed-agile-removed", "agile-renamed-listed", "agile-corrupt", "write-tool-agile-json",
        "git-rm-cached", "git-update-index", "write-list-file"]


@pytest.mark.parametrize("marker", [False, True], ids=["no-marker", "marker"])
@pytest.mark.parametrize("row", ROWS)
def test_loss_of_signal_rows(tmp_path, row, marker):
    repo = make_repo(tmp_path, branch="x")
    env = write_list(tmp_path, repo)
    fake = Fake({INDEX_CALL: (0, "")})
    if row == "listed-agile-removed":
        assert gf.protection(str(repo), env, fake, marker=marker).protected
        assert verdict("git push origin x", repo, env=env, marker=marker, fake=fake).kind in (gf.ASK, gf.FORBID)
    elif row == "indexed-agile-removed":
        sig = gf.protection(str(repo), {}, fake, marker=marker)
        assert sig.indexed is True and sig.protected
    elif row == "agile-renamed-listed":
        (repo / "agile.bak").write_text("{}", encoding="utf-8")
        assert gf.protection(str(repo), env, Fake(), marker=marker).protected
    elif row == "agile-corrupt":
        (repo / ".agile.json").write_text("{not json", encoding="utf-8")
        assert gf.protection(str(repo), {}, Fake(), marker=marker).protected
    elif row == "write-tool-agile-json":
        assert gf.guarded_write([str(repo / ".agile.json")], str(repo), {}) is not None
        assert gf.guarded_write(["sub/.AGILE.JSON"], str(repo), {}) is not None
    elif row == "git-rm-cached":
        (repo / ".agile.json").write_text("{}", encoding="utf-8")
        assert verdict("git rm --cached .agile.json", repo, marker=marker).kind == gf.FORBID
    elif row == "git-update-index":
        (repo / ".agile.json").write_text("{}", encoding="utf-8")
        assert verdict("git update-index --assume-unchanged .agile.json", repo, marker=marker).kind == gf.FORBID
    else:
        assert gf.guarded_write([env[gf.ENV_LIST]], str(repo), env) is not None
        assert gf.guarded_write(["protected.json"], str(tmp_path), env) is not None


def test_no_signal_at_all_is_not_blocked_known_limit(tmp_path):
    """Giới hạn đã biết (không phải Đạt): repo không dấu hiệu nào thì guard không đụng."""
    repo = make_repo(tmp_path)
    assert verdict("git push origin HEAD:main", repo, fake=Fake({INDEX_CALL: (1, "")})).kind == gf.NONE
    assert gf.guarded_write(["README.md"], str(repo), {}) is None


# --- gh ---------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd,expected", [
    ("gh api repos/o/r/pulls/1/merge -X PUT", gf.FORBID), ("gh api -f title=x repos/o/r/issues", gf.FORBID),
    ("gh api --input f.json repos/o/r/issues", gf.FORBID), ("gh ship 123", gf.FORBID), ("gh release create v1", gf.FORBID), ("gh release list", gf.NONE), ("gh release view v1", gf.NONE),
    ("gh pr create --title x", gf.ASK), ("gh pr comment 1 --body x", gf.ASK),
    ("gh issue comment 1 --body x", gf.ASK), ("gh pr merge 12", gf.ASK), ("gh api repos/o/r", gf.NONE),
    ("gh api repos/o/r -X GET", gf.NONE), ("gh pr view 1", gf.NONE), ("gh pr list", gf.NONE), ("gh run view 3", gf.NONE),
    ("gh auth status", gf.NONE), ("gh repo view", gf.NONE),
])
def test_gh_groups_without_marker(tmp_path, cmd, expected):
    repo = make_repo(tmp_path, agile=True)
    assert verdict(cmd, repo).kind == expected, cmd


def test_gh_with_marker(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    assert verdict("gh pr merge 12", repo, marker=True).kind == gf.FORBID
    assert verdict("gh pr create --title x", repo, marker=True).kind == gf.FORBID
    assert verdict("gh pr create --title x", repo, marker=True, contract=contract_for(repo)).kind == gf.FORBID  # chưa có danh sách
    assert verdict("gh pr create --title x", repo, env=listed(repo), marker=True, contract=contract_for(repo)).kind == gf.AUTO


def test_gh_targeting_listed_repo_from_outside(tmp_path):
    outside = make_repo(tmp_path, name="outside", urls=("https://github.com/acme/elsewhere.git",))
    listed = make_repo(tmp_path, name="listed")
    env = write_list(tmp_path, listed, urls=("https://github.com/acme/shop.git",))
    fake = Fake({INDEX_CALL: (1, "")})
    assert verdict("gh pr create -R acme/shop --title x", outside, env=env, fake=fake).kind == gf.ASK
    assert verdict("gh pr create -R other/thing --title x", outside, env=env, fake=fake).kind == gf.NONE
    assert verdict("gh api repos/acme/shop/pulls/1/merge -X PUT", outside, env=env, fake=fake).kind == gf.FORBID


def test_classify_picks_the_strongest_segment(tmp_path):
    repo = make_repo(tmp_path, branch="x", agile=True)
    ctx = ctx_for(repo)
    got = gf.classify([seg("git status", repo), seg("git push origin x", repo), seg("git push --force origin x", repo)], ctx)
    assert got.kind == gf.FORBID


def test_nested_unparsed_in_protected_repo_is_forbidden(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    got = gf.classify([gf.Segment("nested")], ctx_for(repo))
    assert got.kind == gf.FORBID and got.code == "unparsed"
    clean = make_repo(tmp_path, name="clean")
    assert gf.classify([gf.Segment("nested")], ctx_for(clean, fake=Fake({INDEX_CALL: (1, "")}))).kind == gf.NONE


def test_other_command_naming_agile_json_in_protected_repo(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    assert gf.classify([gf.Segment("other", ["x"])], ctx_for(repo)).kind == gf.FORBID


def test_norm_url_spellings():
    same = {gf.norm_url(u) for u in ("https://github.com/acme/shop.git", "git@github.com:acme/shop.git",
                                     "ssh://git@github.com/acme/shop", "https://user:pw@GitHub.com/acme/shop/")}
    assert same == {"github.com/acme/shop"}


def test_push_to_main_without_marker_in_protected_repo(tmp_path):
    """Test được chỉ định cho đột biến `push-allow-all`: đẩy `main` ở repo được bảo vệ, không file dấu, không bao giờ được cho qua."""
    repo = make_repo(tmp_path, agile=True)
    got = verdict("git push origin HEAD:main", repo)
    assert got.kind == gf.ASK and "push" in got.reason
    assert verdict("git push origin main", repo, marker=True).kind == gf.FORBID


# --- vòng 1 kiểm định (Astra RF1, RF2): dạng viết dính giá trị và cờ có giá trị --------------------------------------------

@pytest.mark.parametrize("cmd", [
    "gh api repos/o/r/pulls/1/merge -XPUT", "gh api repos/o/r/issues -XPOST", "gh api repos/o/r/issues -X POST",
    "gh api repos/o/r/issues --method=POST", "gh api repos/o/r/issues -ftitle=x", "gh api repos/o/r/issues -Ftitle=x",
    "gh api repos/o/r/issues --field=title=x", "gh api repos/o/r/issues --raw-field=title=x", "gh api repos/o/r/issues --input=body.json",
    "gh api repos/o/r/issues -f title=x", "gh api repos/o/r/issues --method DELETE",
])
def test_gh_api_write_forms_are_forbidden(tmp_path, cmd):
    repo = make_repo(tmp_path, agile=True)
    assert verdict(cmd, repo).kind == gf.FORBID, cmd


@pytest.mark.parametrize("cmd", ["gh api repos/o/r", "gh api repos/o/r -XGET", "gh api repos/o/r --method=GET", "gh api -H Accept:x repos/o/r"])
def test_gh_api_read_forms_pass(tmp_path, cmd):
    repo = make_repo(tmp_path, agile=True)
    assert verdict(cmd, repo).kind == gf.NONE, cmd


@pytest.mark.parametrize("cmd,expected", [
    ("git config --type string remote.origin.pushurl https://example.invalid/x", gf.FORBID),
    ("git config --type=string remote.origin.url x", gf.FORBID),
    ("git config --default x remote.origin.url y", gf.FORBID),
    ("git config -f other.cfg remote.origin.url y", gf.FORBID),
    ("git config --add remote.origin.pushurl x", gf.FORBID),
    ("git config --unset remote.origin.pushurl", gf.FORBID),
    ("git config --unset-all url.x.insteadOf", gf.FORBID),
    ("git config --replace-all core.hooksPath h", gf.FORBID),
    ("git config --rename-section remote.origin remote.up", gf.FORBID),
    ("git config --remove-section remote.origin", gf.FORBID),
    ("git config --edit", gf.FORBID),
    ("git config --type bool user.autocrlf true", gf.NONE),
    ("git config remote.origin.url", gf.NONE),
    ("git config --type string --get remote.origin.url", gf.NONE),
    ("git config --get-regexp remote", gf.NONE),
    ("git config --list --show-origin", gf.NONE),
    ("git config user.name", gf.NONE),
])
def test_config_forms(tmp_path, cmd, expected):
    repo = make_repo(tmp_path, branch="x", agile=True)
    assert verdict(cmd, repo).kind == expected, cmd


# --- alias của repo (tự tấn công trước vòng 2) ---------------------------------------------------------------------------

def add_alias(repo, name, value):
    with open(repo / ".git" / "config", "a", encoding="utf-8") as handle:
        handle.write('[alias]\n\t{} = {}\n'.format(name, value))


def test_repo_alias_for_push_is_seen(tmp_path):
    repo = make_repo(tmp_path, branch="x", agile=True)
    add_alias(repo, "p", "push")
    assert verdict("git p origin HEAD:main", repo).kind == gf.ASK
    assert verdict("git p --force origin x", repo).kind == gf.FORBID
    add_alias(repo, "pf", "p --force")
    assert verdict("git pf origin x", repo).kind == gf.FORBID  # alias của alias


def test_repo_alias_with_shell_is_unparsed_and_forbidden(tmp_path):
    repo = make_repo(tmp_path, branch="x", agile=True)
    add_alias(repo, "ship", '"!git push origin HEAD:main"')
    assert verdict("git ship", repo).kind == gf.FORBID


def test_repo_alias_for_commit_on_main_is_forbidden_and_harmless_alias_passes(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    add_alias(repo, "ci", "commit -m")
    add_alias(repo, "st", "status -sb")
    assert verdict("git ci x", repo).kind == gf.FORBID
    assert verdict("git st", repo).kind == gf.NONE


def test_writing_alias_config_is_forbidden(tmp_path):
    repo = make_repo(tmp_path, branch="x", agile=True)
    assert verdict("git config alias.p push", repo).kind == gf.FORBID
    assert verdict("git config --global alias.p push", repo).kind == gf.FORBID


# --- vòng 1 kiểm định (Fable RF1): hợp đồng đích chỉ áp khi danh tính repo được xác minh bằng danh sách (dấu hiệu 1) ---------------

def test_contract_needs_the_protected_list_to_name_the_repo(tmp_path):
    repo, fake = push_world(tmp_path)
    missing = push(repo, fake, env={})  # biến vắng: dấu hiệu 1 không xác định
    assert missing.kind == gf.FORBID and missing.code == "push-repo-unverified"
    other = make_repo(tmp_path, name="other", urls=("https://github.com/acme/other.git",))
    elsewhere = push(repo, fake, env=write_list(tmp_path, other, urls=()))  # danh sách có, nhưng không có repo này
    assert elsewhere.kind == gf.FORBID and elsewhere.code == "push-repo-unverified"
    assert push(repo, fake).kind == gf.AUTO  # có trong danh sách: qua


def test_contract_refused_when_the_list_file_is_broken(tmp_path):
    repo, fake = push_world(tmp_path)
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    got = push(repo, fake, env={gf.ENV_LIST: str(bad)})
    assert got.kind == gf.FORBID and got.code == "push-repo-unverified"


def test_indexed_signal_is_read_from_a_linked_worktree(tmp_path):
    """Hàng 4 của bảng mất dấu hiệu: chỉ mục của worktree liên kết còn `.agile.json` thì repo vẫn được bảo vệ."""
    main = make_repo(tmp_path)
    tree = make_worktree(main, tmp_path)
    fake = Fake({INDEX_CALL: (0, "")})
    sig = gf.protection(str(tree), {}, fake)
    assert sig.indexed is True and sig.protected and not sig.config_file
    assert fake.calls == [INDEX_CALL]


def test_broken_list_with_agile_json_and_push_flag_row(tmp_path):
    """Hàng 8: danh sách hỏng + `.agile.json` còn: vẫn được bảo vệ (dấu hiệu 2) nhưng `+đẩy-nhánh` chặn vì dấu hiệu 1 không xác định."""
    repo, fake = push_world(tmp_path)
    bad = tmp_path / "broken-list.json"
    bad.write_text("{not json", encoding="utf-8")
    env = {gf.ENV_LIST: str(bad)}
    assert gf.protection(str(repo), env, fake).protected
    assert push(repo, fake, env=env).code == "push-repo-unverified"


# --- vòng 2 kiểm định (Astra RV1–RV5) ---------------------------------------------------------------------------------------

@pytest.mark.parametrize("cmd,expected", [
    ("git -calias.ship=push ship origin HEAD:main", gf.FORBID),
    ("git -c alias.ship=push ship origin HEAD:main", gf.FORBID),
    ("git -c remote.origin.url=x status", gf.FORBID),
    ("git -c url.x.insteadOf=y status", gf.FORBID),
    ("git -c core.hooksPath=h status", gf.FORBID),
    ("git -c include.path=x.cfg status", gf.FORBID),
    ("git --config-env=alias.x=VAR status", gf.FORBID),
    ("git -c core.editor=x status", gf.NONE),
    ("git -c color.ui=never log -1", gf.NONE),
])
def test_dangerous_command_line_config_is_forbidden_for_any_subcommand(tmp_path, cmd, expected):
    repo = make_repo(tmp_path, branch="x", agile=True)
    assert verdict(cmd, repo).kind == expected, cmd


@pytest.mark.parametrize("cmd,expected", [
    ("git config --remove-section alias", gf.FORBID),
    ("git config --rename-section alias foo", gf.FORBID),
    ("git config --remove-section remote", gf.FORBID),
    ("git config --remove-section includeIf.gitdir:x", gf.FORBID),
    ("git config include.path x.cfg", gf.FORBID),
    ("git config --get remote.origin.url pattern", gf.NONE),
    ("git config --get-all remote.origin.url", gf.NONE),
    ("git config --get-regexp remote", gf.NONE),
])
def test_config_section_forms(tmp_path, cmd, expected):
    repo = make_repo(tmp_path, branch="x", agile=True)
    assert verdict(cmd, repo).kind == expected, cmd


def head_world(tmp_path, branch, targets=(TARGET,)):
    repo, fake = push_world(tmp_path, branch=branch)
    return repo, fake, contract_for(repo, push_targets=list(targets))


def test_push_head_without_destination_resolves_the_current_branch(tmp_path):
    repo, fake, contract = head_world(tmp_path, "spr-31-export")
    assert push(repo, fake, "git push origin HEAD", contract=contract).kind == gf.AUTO
    assert push(repo, fake, "git push origin @", contract=contract).kind == gf.AUTO


def test_push_head_on_a_protected_branch_is_not_a_literal_head_ref(tmp_path):
    repo, fake, contract = head_world(tmp_path, "main", targets=("refs/heads/HEAD",))
    for cmd in ("git push origin HEAD", "git push origin @"):
        assert push(repo, fake, cmd, contract=contract).code == "push-target-unknown", cmd


def test_push_head_when_branch_is_unknown_or_dest_is_head(tmp_path):
    repo, fake, contract = head_world(tmp_path, "spr-31-export", targets=(TARGET, "refs/heads/HEAD"))
    (repo / ".git" / "HEAD").write_text("0123456789abcdef\n", encoding="utf-8")  # detached
    assert push(repo, fake, "git push origin HEAD", contract=contract).code == "push-target-unknown"
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/spr-31-export\n", encoding="utf-8")
    assert push(repo, fake, "git push origin spr-31-export:HEAD", contract=contract).code == "push-target-unknown"


def test_gh_with_contract_must_name_the_verified_repository(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    env = listed(repo)
    contract = contract_for(repo)
    mismatch = verdict("gh pr create --web -R other/repo", repo, env=env, marker=True, contract=contract)
    assert mismatch.kind == gf.FORBID and mismatch.code == "gh-repo-mismatch"
    assert verdict("gh pr create -R acme/shop --title x", repo, env=env, marker=True, contract=contract).kind == gf.AUTO
    assert verdict("gh pr create --title x", repo, env=env, marker=True, contract=contract).kind == gf.AUTO
    assert verdict("gh api repos/other/repo/pulls -f title=x", repo, env=env, marker=True, contract=contract).kind == gf.FORBID


def test_alias_chain_beyond_the_limit_closes(tmp_path):
    repo = make_repo(tmp_path, branch="x", agile=True)
    names = ["a", "b", "c", "d", "e", "f"]
    for first, second in zip(names, names[1:]):
        add_alias(repo, first, second)
    add_alias(repo, "f", "push")
    assert verdict("git a origin HEAD:main", repo).kind == gf.FORBID


# --- SPR-20 TK5: gh nhóm A/B, "hỏi" giữ là hỏi (đề xuất C) ---------------------------------------------------------

def keep(repo, cmd, env=None, contract=None, keep_ask=True, marker=True, **kw):
    ctx = gf.FenceContext(str(repo), env or {}, Fake({INDEX_CALL: (0, "")}), marker=marker, contract=contract, keep_ask=keep_ask)
    return gf.classify([seg(cmd, repo, **kw)], ctx)


@pytest.mark.parametrize("cmd", ["gh label list", "gh run watch 5", "gh run list", "gh pr checks 3"])
def test_gh_read_group_includes_label_list_and_run_watch(tmp_path, cmd):
    assert verdict(cmd, make_repo(tmp_path, agile=True)).kind == gf.NONE


@pytest.mark.parametrize("cmd", ["gh label create bug", "gh pr edit 3 --title x", "gh issue create --title x"])
def test_gh_group_b_asks_without_marker(tmp_path, cmd):
    assert verdict(cmd, make_repo(tmp_path, agile=True)).kind == gf.ASK


@pytest.mark.parametrize("cmd", ["gh label create bug", "gh pr edit 3 --title x", "gh issue create --title x"])
def test_gh_group_b_is_forbidden_with_marker_but_asks_when_kept(tmp_path, cmd):
    repo = make_repo(tmp_path, agile=True)
    assert keep(repo, cmd, keep_ask=False).kind == gf.FORBID
    assert keep(repo, cmd, keep_ask=True).kind == gf.ASK


def test_gh_group_b_never_becomes_auto_even_with_a_verified_contract(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    for cmd in ("gh pr edit 3 --title x", "gh issue create --title x", "gh label create bug"):
        assert keep(repo, cmd, env=listed(repo), contract=contract_for(repo)).kind == gf.ASK


@pytest.mark.parametrize("cmd", ["gh pr ready 3", "gh run rerun 5", "gh pr create --title x", "gh pr comment 1 --body x"])
def test_gh_group_a_is_auto_with_marker_listed_repo_and_contract(tmp_path, cmd):
    repo = make_repo(tmp_path, agile=True)
    assert keep(repo, cmd, env=listed(repo), contract=contract_for(repo), keep_ask=False).kind == gf.AUTO


def test_gh_group_a_without_contract_follows_the_keep_rule(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    assert keep(repo, "gh run rerun 5", keep_ask=False).kind == gf.FORBID
    assert keep(repo, "gh run rerun 5", keep_ask=True).kind == gf.ASK


def test_keep_ask_does_not_soften_forbidden_commands(tmp_path):
    repo = make_repo(tmp_path, agile=True)
    for cmd in ("gh api repos/o/r/issues -X POST", "gh release create v1", "gh pr merge 12", "gh ship 1", "git push --force origin x"):
        assert keep(repo, cmd, env=listed(repo), contract=contract_for(repo)).kind == gf.FORBID, cmd


def test_keep_ask_turns_a_marker_git_ask_back_into_ask(tmp_path):
    repo = make_repo(tmp_path, branch="x", agile=True)
    assert keep(repo, "git tag v1", keep_ask=False).kind == gf.FORBID
    assert keep(repo, "git tag v1", keep_ask=True).kind == gf.ASK


NOT_BARE_PULL = [
    ["--ff-only", "origin"], ["--ff-only", "origin", "feat"], ["--ff-only", "--no-ff"], ["--ff-only", "--rebase"], ["--ff-only", "-r"],
    ["--ff-only", "."], ["origin"], [], ["--ff-only", "--no-ff-only"], ["--ff-only", "--ff-only"], ["-ff-only"], ["--ff-only=false"],
    ["--rebase", "--ff-only"], ["--ff-o"], ["--reb"], ["--squ"], ["--no-com"], ["-qr"], ["--ff-only", "-q"], ["--ff-only", "-v"],
    ["--ff-only", "../x"], ["--ff-only", "https://h/r.git"], ["--ff-only", "origin", "main"],
    ["--ff-only", "origin", "refs/heads/a:refs/heads/b"], ["--ff-only", "origin", "+x"], ["--ff-only", "origin", "a..b"],
    ["--ff-only", "origin", "a:b"], ["--ff-only", "origin", "a b"], ["--ff-only", "origin", "a\x01b"], ["--ff-only", "../wt-feat"]]


def test_plain_ff_pull_accepts_only_the_bare_form():
    assert gf.plain_ff_pull(["--ff-only"]) is True
    assert gf.plain_ff_pull(["--ff-only"], ["-C", "/repo"]) is True


@pytest.mark.parametrize("rest", NOT_BARE_PULL)
def test_plain_ff_pull_rejects_every_form_other_than_bare(rest):
    assert gf.plain_ff_pull(rest) is False


@pytest.mark.parametrize("globals_", [["-c", "branch.main.merge=refs/heads/feat"], ["-cbranch.main.merge=x"], ["--config-env", "a=B"],
                                       ["--git-dir", "/x"], ["--work-tree", "/x"], ["--exec-path=/x"], ["-C"], ["--no-pager"]])
def test_plain_ff_pull_rejects_global_options_other_than_dash_c_dir(globals_):
    assert gf.plain_ff_pull(["--ff-only"], globals_) is False


def test_push_only_pull_ff_only_is_auto_but_override_flag_or_unknown_dir_asks(tmp_path):
    repo = make_repo(tmp_path, branch="main", agile=True)
    env = write_list(tmp_path, repo, level="push-only")
    assert verdict("git pull --ff-only", repo, env=env).kind == gf.AUTO
    assert verdict("git pull --ff-only --no-ff origin x", repo, env=env).kind == gf.ASK
    assert verdict("git pull --ff-only", repo, env=env, cd=True).kind == gf.ASK


@pytest.mark.parametrize("cmd", [
    "git pull --ff-only --no-ff-only", "git -c branch.main.merge=refs/heads/feat pull --ff-only", "git pull --ff-only ../wt-feat",
    "git pull --ff-only https://h/r.git", "git pull --ff-only origin", "git pull --ff-only origin main", "git pull --ff-only --ff-only",
    "git pull --rebase --ff-only", "git pull --ff-o", "git pull --reb", "git pull -qr", "git -c x.y=z pull --ff-only",
    "git --config-env=branch.main.merge=V pull --ff-only"])
def test_push_only_pull_forms_other_than_bare_are_not_auto_in_the_fence(tmp_path, cmd):
    repo = make_repo(tmp_path, branch="main", agile=True)
    env = write_list(tmp_path, repo, level="push-only")
    assert verdict(cmd, repo, env=env).kind in (gf.ASK, gf.FORBID), cmd


def test_push_only_bare_pull_with_dash_c_dir_is_still_auto(tmp_path):
    repo = make_repo(tmp_path, branch="main", agile=True)
    env = write_list(tmp_path, repo, level="push-only")
    assert verdict("git -C {} pull --ff-only".format(repo), repo, env=env).kind == gf.AUTO


def test_fence_context_defaults_to_not_keeping_ask(tmp_path):
    assert gf.FenceContext(str(tmp_path), {}, Fake(), marker=True).keep_ask is False
