#!/usr/bin/env python3
import re
import sys
from pathlib import Path

# Backward compatible:
# - 1 arg  -> updates README.md
# - 2 args -> updates provided file path
if len(sys.argv) not in (2, 3):
    print("Usage: update_readme_version.py <tag> [file]", file=sys.stderr)
    sys.exit(2)

tag = sys.argv[1].strip()  # expected like v1.2.0 or 1.2.0
if not tag:
    print("Tag is empty", file=sys.stderr)
    sys.exit(2)

# Normalize: ensure tag has single leading 'v'
tag = "v" + tag.lstrip("v")
version = tag.lstrip("v")  # version without leading 'v' for filenames

# Default remains README.md (important for compatibility)
target_path = Path(sys.argv[2]) if len(sys.argv) == 3 else Path("README.md")

if not target_path.exists():
    print(f"File not found: {target_path}", file=sys.stderr)
    sys.exit(1)

content = target_path.read_text(encoding="utf-8")

# Windows
win_pattern = re.compile(
    r"(releases/download/)[^/]+(/mydylms-client-)v+[^/]+(-win-x64\.exe)"
)


def win_repl(m: re.Match) -> str:
    return f"{m.group(1)}{tag}{m.group(2)}v{version}{m.group(3)}"


# Linux (download or tag)
linux_pattern = re.compile(
    r"(releases/(?:download|tag)/)[^/]+(/mydylms-client-)v+[^/]+(-linux-x86__64(?:\.tar\.gz)?)"
)


def linux_repl(m: re.Match) -> str:
    return f"{m.group(1)}{tag}{m.group(2)}v{version}{m.group(3)}"


# macOS
mac_pattern = re.compile(
    r"(releases/download/)[^/]+(/mydylms-client-)v+[^/]+(-macos-arm64(?:\.zip)?)"
)


def mac_repl(m: re.Match) -> str:
    return f"{m.group(1)}{tag}{m.group(2)}v{version}{m.group(3)}"


updated = content
updated = win_pattern.sub(win_repl, updated)
updated = linux_pattern.sub(linux_repl, updated)
updated = mac_pattern.sub(mac_repl, updated)

if updated != content:
    target_path.write_text(updated, encoding="utf-8")
    print(f"{target_path} updated to {tag}")
else:
    print(f"{target_path} already up-to-date")
