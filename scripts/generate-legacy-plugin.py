#!/usr/bin/env python3
"""Regenerate plugins/awolve-spec from plugins/awolve-signum.

The plugin is published under two names while the product is renamed:
awolve-signum is the source, and awolve-spec is a generated copy so existing
installs keep working. Edit plugins/awolve-signum only, then run:

    python3 scripts/generate-legacy-plugin.py          # write the copy
    python3 scripts/generate-legacy-plugin.py --check  # exit 1 if the copy is stale

What differs in the copy: the command prefix (awolve-signum: -> awolve-spec:)
in every file, the plugin name wherever it appears in .md and .json files, the
plugin description, and a GENERATED.md note. Scripts are otherwise identical;
they read their own plugin.json to know which name they run under, which is
how the copy's sync hooks stand down when awolve-signum is enabled.
"""

import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "plugins" / "awolve-signum"
DST = ROOT / "plugins" / "awolve-spec"
SKIP_DIRS = {"__pycache__", ".pytest_cache"}
TEXT_SUFFIXES = {".md", ".json", ".py", ".sh"}
LEGACY_DESCRIPTION = (
    "Former name of awolve-signum, kept so existing installs keep working. "
    "Install awolve-signum instead; with both enabled, this copy's sync hooks stand down."
)
NOTE = (
    "# Generated — do not edit\n\n"
    "This plugin is a copy of `plugins/awolve-signum`, published under its former name so "
    "existing installs keep working. `scripts/generate-legacy-plugin.py` regenerates it. "
    "Make every change in `plugins/awolve-signum`.\n"
)


def files_under(base):
    for path in sorted(base.rglob("*")):
        rel = path.relative_to(base)
        if path.is_file() and not (set(rel.parts) & SKIP_DIRS):
            yield rel


def transform(rel, data):
    if rel.suffix not in TEXT_SUFFIXES:
        return data
    text = data.decode("utf-8").replace("awolve-signum:", "awolve-spec:")
    if rel.suffix in (".md", ".json"):
        text = text.replace("awolve-signum", "awolve-spec")
    if rel.as_posix() == ".claude-plugin/plugin.json":
        manifest = json.loads(text)
        manifest["description"] = LEGACY_DESCRIPTION
        text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return text.encode("utf-8")


def expected():
    out = {rel: transform(rel, (SRC / rel).read_bytes()) for rel in files_under(SRC)}
    out[pathlib.Path("GENERATED.md")] = NOTE.encode("utf-8")
    return out


def main():
    check = "--check" in sys.argv[1:]
    want = expected()
    have = set(files_under(DST)) if DST.exists() else set()
    stale = sorted(rel for rel in want if rel not in have or (DST / rel).read_bytes() != want[rel])
    extra = sorted(rel for rel in have if rel not in want)
    if check:
        for rel in stale:
            print(f"stale or missing: plugins/awolve-spec/{rel}")
        for rel in extra:
            print(f"not in source:    plugins/awolve-spec/{rel}")
        if stale or extra:
            print("Run: python3 scripts/generate-legacy-plugin.py")
            return 1
        print("plugins/awolve-spec is up to date")
        return 0
    for rel in extra:
        (DST / rel).unlink()
    for rel in stale:
        target = DST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(want[rel])
        source = SRC / rel
        if source.exists():
            os.chmod(target, source.stat().st_mode & 0o777)
    print(f"plugins/awolve-spec: {len(stale)} written, {len(extra)} removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
