#!/usr/bin/env python3
"""Approved and pinned dependencies (coding.md CODE-2, CODE-3).

Reads the approved list from coding.md (the ```approved-libraries block) and checks every
requirements*.txt and package.json in the product repository: each dependency must be on
the list for its ecosystem and pinned to an exact version.

Run from the product repository's root: python standards/checks/check_dependencies.py
Exit code 1 on any problem. Writes a Markdown summary to $GITHUB_STEP_SUMMARY if set.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
STANDARDS = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "standards", "prototypes"}
REQ_LINE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(\[[^\]]*\])?\s*(.*)$")
EXACT_NPM = re.compile(r"^\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?$")


def normalise(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def approved() -> dict[str, dict[str, str]]:
    text = (STANDARDS / "coding.md").read_text(encoding="utf-8")
    block = re.search(r"```approved-libraries\n(.*?)```", text, re.S)
    if not block:
        sys.exit("coding.md has no ```approved-libraries block")
    libs: dict[str, dict[str, str]] = {}
    for line in block.group(1).splitlines():
        parts = line.split(None, 2)
        if len(parts) >= 2 and not line.startswith("#"):
            libs.setdefault(parts[0], {})[normalise(parts[1])] = parts[2] if len(parts) > 2 else ""
    return libs


def files(pattern: str) -> list[Path]:
    return sorted(p for p in ROOT.rglob(pattern) if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts))


def main() -> int:
    libs = approved()
    problems: list[tuple[str, str, str]] = []
    checked = 0

    for req in files("requirements*.txt"):
        rel = str(req.relative_to(ROOT))
        for raw in req.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or line.startswith("-"):
                continue
            m = REQ_LINE.match(line)
            if not m:
                problems.append((rel, line, "can't read this line"))
                continue
            checked += 1
            name, spec = m.group(1), m.group(3).replace(" ", "")
            if normalise(name) not in libs.get("python", {}):
                problems.append((rel, name, "not on the approved list (CODE-2)"))
            if not re.fullmatch(r"==[^,;*]+", spec):
                problems.append((rel, name, f"not pinned to an exact version: '{spec or 'no version'}' (CODE-3)"))

    for pkg in files("package.json"):
        rel = str(pkg.relative_to(ROOT))
        data = json.loads(pkg.read_text(encoding="utf-8"))
        for section in ("dependencies", "devDependencies", "optionalDependencies"):
            for name, version in (data.get(section) or {}).items():
                checked += 1
                if name.lower() not in libs.get("npm", {}):
                    problems.append((rel, name, "not on the approved list (CODE-2)"))
                if not EXACT_NPM.match(str(version)):
                    problems.append((rel, name, f"not pinned to an exact version: '{version}' (CODE-3)"))

    lines = [f"### Dependencies: {checked} checked against the approved list", ""]
    if problems:
        lines += ["| File | Library | Problem |", "|---|---|---|"]
        lines += [f"| `{f}` | `{n}` | {p} |" for f, n, p in problems]
        lines += ["", "To approve a new library, open a PR to the standards repository (coding.md)."]
    else:
        lines.append("Every dependency is approved and pinned. ✅")
    report = "\n".join(lines)
    print(report)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(report + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
