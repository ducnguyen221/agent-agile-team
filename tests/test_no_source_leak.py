"""Test ngược của SPR-19 (SPR-17/FR22.5): repo phân phối không mang dấu vết nguồn distill.

Theo chuẩn metadata chung của hệ (mục 2c của tài liệu chuẩn file): frontmatter của skill và agent chỉ có khoá chức năng, không có khoá
nguồn; không có `UPSTREAM.md`, `THIRD_PARTY.md`, `docs/updating-from-upstream.md`; tên nguồn chỉ nằm ở `NOTICE`,
`CHANGELOG.md` (lịch sử), `LICENSES/**` và các đường miễn trừ có chủ đích bên dưới. Nguồn distill sống ở Workshop.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest

from conftest import REPO

SOURCE_KEYS = ("source", "source_sha", "base_sha", "rewrite_before_public", "license")
REMOVED_FILES = ("UPSTREAM.md", "THIRD_PARTY.md", "docs/updating-from-upstream.md")
# Đường được phép chứa tên nguồn: thông báo bản quyền, lịch sử, bản giấy phép, bảng tra tên skill cũ, hồ sơ thử chỉ-thêm.
NAME_EXEMPT = ("NOTICE", "CHANGELOG.md", "docs/MIGRATION.md")
NAME_EXEMPT_PREFIX = ("LICENSES/",)
NAME_EXEMPT_PRESSURE = re.compile(r"^skills/[^/]+/tests/pressure\.md$")


def tracked() -> list[str]:
    out = subprocess.run(["git", "-C", str(REPO), "ls-files"], capture_output=True, text=True, encoding="utf-8", check=True)
    return [line for line in out.stdout.splitlines() if line]


def skill_and_agent_files() -> list[str]:
    return [f for f in tracked() if re.fullmatch(r"skills/[^/]+/SKILL\.md|agents/[^/]+\.md", f)]


def frontmatter_lines(rel: str) -> list[str]:
    lines = (REPO / rel).read_text(encoding="utf-8").splitlines()
    assert lines and lines[0] == "---", f"{rel}: thiếu frontmatter"
    end = lines.index("---", 1)
    return lines[1:end]


def test_there_are_skill_and_agent_files():
    files = skill_and_agent_files()
    assert files, "không thấy skill/agent nào"
    assert any(f.startswith("agents/") for f in files) and any(f.startswith("skills/") for f in files)


def test_no_source_keys_in_skill_and_agent_frontmatter():
    """Mỗi file skill/agent (số file lấy từ `git ls-files`, không ghi cứng) không có khoá nguồn ở cấp một."""
    pattern = re.compile(r"^(" + "|".join(SOURCE_KEYS) + r")\s*:")
    bad = []
    for rel in skill_and_agent_files():
        keys = sorted({m.group(1) for line in frontmatter_lines(rel) if (m := pattern.match(line))})
        if keys:
            bad.append(f"{rel}: {', '.join(keys)}")
    assert bad == [], (
        f"{len(bad)} file còn khoá nguồn trong frontmatter (nguồn chỉ ở Workshop; xem mục 2c của tài liệu chuẩn file):\n"
        + "\n".join(bad[:10])
    )


def test_roles_is_a_string():
    """`metadata.roles` là chuỗi "a, b" (chuẩn metadata chung), không phải danh sách `[a, b]` (doctor báo FM1)."""
    bad = []
    for rel in skill_and_agent_files():
        for line in frontmatter_lines(rel):
            m = re.match(r"^\s+roles\s*:\s*(.*)$", line)
            if m and m.group(1).lstrip().startswith("["):
                bad.append(f"{rel}: {line.strip()}")
    assert bad == [], f"{len(bad)} file còn `roles` dạng danh sách:\n" + "\n".join(bad[:10])


def test_removed_source_documents_are_gone():
    present = [f for f in REMOVED_FILES if f in set(tracked())]
    assert present == [], f"tài liệu nguồn còn trong repo: {present}"


def test_check_py_has_no_upstream_machinery():
    text = (REPO / "scripts" / "check.py").read_text(encoding="utf-8")
    assert "UPSTREAM_OWNERS" not in text and "_UpstreamRef" not in text, "scripts/check.py còn mã quét nguồn upstream"


def source_name_pattern() -> re.Pattern:
    configured = os.environ.get("AGENT_AGILE_SOURCE_NAMES")
    if not configured or not Path(configured).is_file():
        pytest.skip("Chưa chạy: AGENT_AGILE_SOURCE_NAMES chưa đặt hoặc file không đọc được (danh sách tên nguồn ở Workshop, tests/README.md)")
    names = [ln.strip().lower() for ln in Path(configured).read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
    assert names, "danh sách tên nguồn rỗng"
    return re.compile(r"(?<![0-9A-Za-z_.\-])(" + "|".join(re.escape(n) for n in names) + r")(?![0-9A-Za-z_.\-])", re.I)


def test_no_source_names_outside_notice():
    pattern = source_name_pattern()
    bad = []
    for rel in tracked():
        if rel in NAME_EXEMPT or rel.startswith(NAME_EXEMPT_PREFIX) or NAME_EXEMPT_PRESSURE.match(rel):
            continue
        try:
            text = (REPO / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        hits = [i for i, line in enumerate(text.splitlines(), 1) if pattern.search(line)]
        if hits:
            bad.append(f"{rel}: dòng {', '.join(map(str, hits[:5]))}")
    assert bad == [], (
        f"{len(bad)} file còn tên nguồn ngoài NOTICE/CHANGELOG/LICENSES (nguồn chỉ ở Workshop):\n" + "\n".join(bad[:15])
    )
