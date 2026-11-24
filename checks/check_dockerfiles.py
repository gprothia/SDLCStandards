#!/usr/bin/env python3
"""Dockerfile rules (security.md SEC-4).

Every Dockerfile in the product repository must:
  - start FROM a base image with an explicit version (no tag, or `latest`, fails);
  - switch to a non-root USER before it runs anything (CMD / ENTRYPOINT);
  - never ADD from a URL;
  - set no secret-looking value in ENV or ARG.

Run from the product repository's root: python standards/checks/check_dockerfiles.py
Exit code 1 on any problem. Writes a Markdown summary to $GITHUB_STEP_SUMMARY if set.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
SKIP_DIRS = {"node_modules", ".git", "standards", "prototypes"}
SECRET_NAME = re.compile(r"(PASSWORD|PASSWD|SECRET|TOKEN|API_?KEY|PRIVATE_?KEY|CREDENTIALS)", re.I)
ROOT_USERS = {"root", "0", "0:0", "root:root"}


def instructions(text: str) -> list[tuple[int, str, str]]:
    """(line number, INSTRUCTION, arguments), with continuation lines joined."""
    out, buf, start = [], "", 0
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not buf and (not line or line.startswith("#")):
            continue
        if not buf:
            start = n
        if line.endswith("\\"):
            buf += line[:-1] + " "
            continue
        buf += line
        word, _, args = buf.partition(" ")
        out.append((start, word.upper(), args.strip()))
        buf = ""
    return out


def check(path: Path) -> list[str]:
    problems = []
    steps = instructions(path.read_text(encoding="utf-8"))
    user = "root"
    stages = []
    for n, word, args in steps:
        if word == "FROM":
            image = args.split()[0]
            if image.lower() == "scratch" or "@sha256:" in image:
                pass
            elif re.search(r":[^/]+$", image) is None:
                problems.append(f"line {n}: base image `{image}` has no version tag")
            elif image.endswith(":latest"):
                problems.append(f"line {n}: base image `{image}` uses `latest`; name a version")
            stages.append(n)
            user = "root"  # each stage starts as the base image's default; be strict
        elif word == "USER":
            user = args.split()[0]
        elif word == "ADD" and re.search(r"https?://", args):
            problems.append(f"line {n}: ADD from a URL; download in a RUN step and verify a checksum")
        elif word in ("ENV", "ARG"):
            for name in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", args) or [args.split()[0] if args else ""]:
                if SECRET_NAME.search(name):
                    problems.append(f"line {n}: `{word} {name}` looks like a secret; use Secret Manager (SEC-1)")
        elif word in ("CMD", "ENTRYPOINT") and user in ROOT_USERS:
            problems.append(f"line {n}: {word} runs as root; add a non-root `USER` before it")
    if not stages:
        problems.append("no FROM instruction")
    return problems


def main() -> int:
    paths = sorted(
        p for p in ROOT.rglob("Dockerfile*") if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(ROOT).parts)
    )
    failed = 0
    lines = [f"### Dockerfiles: {len(paths)} checked (SEC-4)", ""]
    for p in paths:
        rel = p.relative_to(ROOT)
        problems = check(p)
        failed += bool(problems)
        lines.append(f"- {'❌' if problems else '✅'} `{rel}`")
        lines += [f"  - {x}" for x in problems]
    report = "\n".join(lines)
    print(report)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(report + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
