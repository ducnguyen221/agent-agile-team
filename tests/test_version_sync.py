"""Mọi manifest phát hành dùng chung một version.

Lệch một chỗ thì marketplace và ghi chú phát hành nói hai phiên bản khác nhau; harness cài bản theo
manifest nên lỗi này không tự lộ ra.
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?")


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def manifest_versions() -> dict:
    found = {
        ".claude-plugin/plugin.json": json.loads(read(".claude-plugin/plugin.json")).get("version"),
        ".codex-plugin/plugin.json": json.loads(read(".codex-plugin/plugin.json")).get("version"),
    }
    market = json.loads(read(".claude-plugin/marketplace.json"))
    for plugin in market.get("plugins", []):
        found[f".claude-plugin/marketplace.json#{plugin.get('name')}"] = plugin.get("version")
    return found


def test_all_manifests_share_one_semver_version():
    versions = manifest_versions()
    assert None not in versions.values(), f"Thiếu trường version: {versions}"
    assert len(set(versions.values())) == 1, f"Version lệch giữa các manifest: {versions}"
    assert SEMVER.fullmatch(next(iter(versions.values())))


def test_marketplace_lists_this_plugin():
    names = [p.get("name") for p in json.loads(read(".claude-plugin/marketplace.json"))["plugins"]]
    assert names == ["agent-agile-team"], f"Marketplace phải liệt kê đúng plugin này: {names}"


def test_changelog_leads_with_current_version():
    version = next(iter(manifest_versions().values()))
    first = re.search(r"^## (\S+)", read("CHANGELOG.md"), re.MULTILINE)
    assert first and first.group(1) == version, (
        f"Mục đầu CHANGELOG.md phải là {version}, đang là {first.group(1) if first else None}"
    )
