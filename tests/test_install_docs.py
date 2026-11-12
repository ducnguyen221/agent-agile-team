"""Tài liệu cài đặt và tài liệu người dùng: prompt dán ngắn, đủ bốn harness, link nội bộ không gãy.

Hỏng kiểu này thì hỏng im lặng: prompt dài tới mức người dùng cắt mất nửa, `INSTALL.md` quên một harness,
một file đổi tên làm link chết, hay `CLAUDE.md` quay lại gốc repo (làm `validate --strict` đỏ). Test đọc đúng những chỗ đó
(khuôn chuẩn hóa `A5`, `A2`, `A10` — `docs/standardization.md`).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HOSTS = ("claude", "codex", "antigravity", "claude-desktop")
FENCE_TEXT = re.compile(r"(?ms)^```text\r?\n(.*?)^```")
FENCE_ANY = re.compile(r"(?ms)^```.*?^```")
CODE_SPAN = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
MAX_PROMPT_LINES = 12

# Tài liệu người đọc mở ra và bấm link theo.
USER_DOCS = (
    "README.md",
    "README.vi.md",
    "docs/INSTALL.md",
    "docs/GUIDE.md",
    "docs/README.md",
    "docs/standardization.md",
    "docs/troubleshooting.md",
    "hosts/README.md",
    *[f"hosts/{host}/README.md" for host in HOSTS],
)


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    start = text.index(heading)
    rest = text[start + len(heading):]
    end = re.search(r"(?m)^## ", rest)
    return rest[: end.start()] if end else rest


def broken_links(text: str, base: Path) -> list[str]:
    """Link tương đối (bỏ URL ngoài và neo trong trang) mà đích không tồn tại; bỏ qua khối code và code span
    (ví dụ cú pháp như `@[nhãn](đường-dẫn)` không phải link)."""
    broken = []
    for target in LINK.findall(CODE_SPAN.sub("", FENCE_ANY.sub("", text))):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE) or target.startswith("#"):
            continue
        path = target.split("#", 1)[0]
        if path and not (base / path).exists():
            broken.append(target)
    return broken


# --- INSTALL.md (`A5`) -------------------------------------------------------------------------------


def test_install_has_one_vi_and_one_en_prompt_each_short():
    blocks = FENCE_TEXT.findall(section(read("docs/INSTALL.md"), "## Prompt copy-dán"))
    assert len(blocks) == 2, "cần đúng hai prompt: tiếng Việt và tiếng Anh"
    vi, en = blocks
    assert "Cài agent-agile-team" in vi
    assert "Install agent-agile-team" in en
    for block in blocks:
        lines = [line for line in block.splitlines() if line.strip()]
        assert len(lines) <= MAX_PROMPT_LINES, f"prompt {len(lines)} dòng > {MAX_PROMPT_LINES}: {lines[0]}"
        assert "INSTALL.md" in block
        assert "check.py --self" in block


def test_install_walks_every_numbered_step():
    text = read("docs/INSTALL.md")
    for number in range(8):
        assert re.search(rf"(?m)^## {number}\. ", text), f"thiếu mục {number}"
    for sub in ("### 4a.", "### 4b.", "### 4c."):
        assert sub in text


def test_install_points_to_every_host_guide_and_they_exist():
    text = read("docs/INSTALL.md")
    for host in HOSTS:
        assert f"hosts/{host}" in text, f"INSTALL.md không trỏ hosts/{host}"
        assert (REPO / "hosts" / host / "README.md").is_file()


def test_install_covers_both_operating_systems_and_both_plug_variables():
    text = read("docs/INSTALL.md")
    for needle in ("Windows", "macOS", "winget", "brew", "setx", "zsh -lic",
                   "AGENT_AGILE_TIERS", "AGENT_AGILE_DENYLIST"):
        assert needle in text, needle


def test_install_asks_before_touching_the_machine():
    safety = section(read("docs/INSTALL.md"), "## 0. ")
    for needle in ("Hỏi trước khi chạm máy", "Không tải-rồi-chạy", "Không đụng bí mật"):
        assert needle in safety


# --- Lệnh Windows (`RF1` vòng sửa 1) ----------------------------------------------------------------------
# PowerShell 5.1 không mở `~` cho chương trình ngoài (`git -C ~/…`, `python ~/…`, `claude … ~/…`): khối lệnh
# PowerShell phải dùng `$HOME`; tài liệu nào dạy lệnh bash có `~/agent-agile-team` phải có khối PowerShell tương ứng.

FENCE_LANG = re.compile(r"(?ms)^```(\w*)\r?\n(.*?)^```")
TILDE_PATH = re.compile(r"(?<![\w@])~[/\\]")
WINDOWS_DOCS = ("docs/INSTALL.md", "README.md", "README.vi.md", "docs/GUIDE.md", "hosts/claude/README.md")


def fenced(text: str, lang: str) -> list[str]:
    return [body for name, body in FENCE_LANG.findall(text) if name == lang]


@pytest.mark.parametrize("rel", USER_DOCS)
def test_powershell_blocks_do_not_use_tilde(rel):
    for block in fenced(read(rel), "powershell"):
        assert not TILDE_PATH.search(block), f"{rel}: khối PowerShell dùng `~` — đổi sang \"$HOME\\…\"\n{block}"


@pytest.mark.parametrize("rel", WINDOWS_DOCS)
def test_bash_commands_on_the_clone_have_a_powershell_twin(rel):
    text = read(rel)
    if any("~/agent-agile-team" in block for block in fenced(text, "bash")):
        twins = fenced(text, "powershell")
        assert any("$HOME\\agent-agile-team" in block for block in twins), \
            f"{rel}: lệnh bash có `~/agent-agile-team` nhưng thiếu khối PowerShell dùng $HOME"


def test_tilde_detector_catches_the_broken_windows_command():
    """Đột biến: đúng lệnh từng gãy trên PowerShell 5.1; `@~/…` (import của Claude Code) thì không bắt."""
    assert TILDE_PATH.search("git -C ~/agent-agile-team pull --ff-only")
    assert TILDE_PATH.search(r"python ~\agent-agile-team\scripts\check.py --self")
    assert not TILDE_PATH.search('python "$HOME\\agent-agile-team\\scripts\\check.py" --self')
    assert not TILDE_PATH.search("@~/agent-agile-team/AGENTS.md")


# --- Con trỏ luật (`A2`)------------------------------------------------------------------------------


def test_no_root_claude_md():
    """`claude plugin validate --strict` đỏ khi plugin có `CLAUDE.md` ở gốc; luật lõi vào Claude Code qua dòng import
    cấp người dùng, hoặc bản ≥ 2.1.277 tự đọc `AGENTS.md` (`hosts/claude/README.md`)."""
    assert not (REPO / "CLAUDE.md").exists()


def test_agents_dir_holds_only_agents():
    """Mọi file `.md` trong `agents/` thành một agent; file không frontmatter (như README cũ, nay ở `docs/agents.md`)
    hiện thành agent rác và làm `claude plugin validate --strict` đỏ."""
    files = sorted((REPO / "agents").glob("*.md"))
    assert files
    bare = [p.name for p in files if not p.read_text(encoding="utf-8").startswith("---")]
    assert not bare, f"agents/ có file không frontmatter: {bare}"


def test_gemini_md_only_points_to_agents_md():
    text = read("GEMINI.md")
    assert "AGENTS.md" in text
    assert len(text.split()) < 80, "GEMINI.md là con trỏ, không chứa luật riêng"


def test_hosts_index_lists_every_host():
    index = read("hosts/README.md")
    for host in HOSTS:
        assert f"{host}/README.md" in index


# --- Link nội bộ và trang lỗi hay gặp (`A10`) ------------------------------------------------------------


@pytest.mark.parametrize("rel", USER_DOCS)
def test_user_doc_has_no_broken_relative_link(rel):
    path = REPO / rel
    assert path.is_file(), f"thiếu {rel}"
    assert broken_links(path.read_text(encoding="utf-8"), path.parent) == []


def test_readmes_and_guide_point_to_troubleshooting():
    for rel in ("README.md", "README.vi.md"):
        assert "docs/troubleshooting.md" in read(rel), rel
    for rel in ("docs/GUIDE.md", "docs/INSTALL.md"):  # cùng thư mục docs/: link ngắn
        assert "(troubleshooting.md)" in read(rel), rel


def test_link_checker_catches_a_broken_link(tmp_path):
    """Đột biến: link tới file không có phải bị bắt; URL ngoài, neo, link trong khối code thì không."""
    (tmp_path / "ok.md").write_text("x", encoding="utf-8")
    text = (
        "[ok](ok.md) [neo](#muc) [web](https://example.com) [ok-neo](ok.md#a)\n"
        "[gãy](missing.md) `@[nhãn](span-missing.md)`\n"
        "```text\n[trong-code](also-missing.md)\n```\n"
    )
    assert broken_links(text, tmp_path) == ["missing.md"]


# --- Đường mới của hai tài liệu và con trỏ ở gốc (SPR-19, CQ3 phương án b) ------------------------------------------


def test_install_and_guide_live_in_docs():
    for rel in ("docs/INSTALL.md", "docs/GUIDE.md"):
        assert (REPO / rel).is_file(), f"thiếu {rel}"


def test_root_pointers_are_short_and_point_into_docs():
    """Liên kết ngoài tới gốc repo (GitHub, hướng dẫn cũ) vẫn sống: `INSTALL.md`, `GUIDE.md` ở gốc chỉ là con trỏ ngắn."""
    for name in ("INSTALL.md", "GUIDE.md"):
        text = read(name)
        assert len(text.splitlines()) <= 8, f"{name} ở gốc phải là con trỏ ngắn (≤ 8 dòng)"
        assert f"docs/{name}" in text, f"{name} ở gốc không trỏ tới docs/{name}"
        assert broken_links(text, REPO) == []


def test_internal_links_of_moved_docs_resolve_from_docs():
    for rel in ("docs/INSTALL.md", "docs/GUIDE.md"):
        assert broken_links(read(rel), (REPO / rel).parent) == [], rel
