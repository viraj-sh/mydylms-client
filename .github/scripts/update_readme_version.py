#!/usr/bin/env python3
import re
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: update_readme_version.py <tag>", file=sys.stderr)
    sys.exit(2)

tag = sys.argv[1].strip()  # expected like v1.2.0 or 1.2.0
if not tag:
    print("Tag is empty", file=sys.stderr)
    sys.exit(2)

# Normalize: ensure tag has single leading 'v'
tag = ("v" + tag.lstrip("v"))
version = tag.lstrip("v")  # version without leading 'v' for filenames

readme_path = Path("README.md")
content = readme_path.read_text(encoding="utf-8")

# Windows: releases/download/<tag>/mydylms-client-v<version>-win-x64.exe
win_pattern = re.compile(
    r"(releases/download/)[^/]+(/mydylms-client-v)[^/]+(-win-x64\.exe)"
)
win_repl = r"\1" + tag + r"\2" + version + r"\3"

# Linux: releases/(download|tag)/<tag>/mydylms-client-v<version>-linux-x86__64(.tar.gz optional)
linux_pattern = re.compile(
    r"(releases/(?:download|tag)/)[^/]+(/mydylms-client-v)[^/]+(-linux-x86__64(?:\.tar\.gz)?)"
)
linux_repl = r"\1" + tag + r"\2" + version + r"\3"

# macOS: releases/download/<tag>/mydylms-client-v<version>-macos-arm64(.zip optional)
mac_pattern = re.compile(
    r"(releases/download/)[^/]+(/mydylms-client-v)[^/]+(-macos-arm64(?:\.zip)?)"
)
mac_repl = r"\1" + tag + r"\2" + version + r"\3"

updated = content
updated = win_pattern.sub(win_repl, updated)
updated = linux_pattern.sub(linux_repl, updated)
updated = mac_pattern.sub(mac_repl, updated)

if updated != content:
    readme_path.write_text(updated, encoding="utf-8")
    print(f"README.md updated to {tag}")
else:
    print("README.md already up-to-date")
