#!/usr/bin/env python3
"""Bump the calendar-based version, commit, and tag.

Version format: ``Major.YYMM.day`` (see ``intersphinx_registry/__init__.py``).
If the current version is already >= today's, the day is bumped past it
("borrow the next day's date" for multiple same-day releases).
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INIT = ROOT / "intersphinx_registry" / "__init__.py"
PATTERN = re.compile(r"^version_info = \((\d+), (\d+), (\d+)\)$", re.MULTILINE)


def read_current() -> tuple[int, int, int]:
    m = PATTERN.search(INIT.read_text())
    if not m:
        raise SystemExit(f"version_info tuple not found in {INIT}")
    return int(m[1]), int(m[2]), int(m[3])


def next_version(current: tuple[int, int, int], today: dt.date) -> tuple[int, int, int]:
    """Compute the new version from today's date.

    The previous version is intentionally ignored except to detect a same-day
    collision: if today already matches the current version we borrow the next
    day's date. We don't compare ordering, because past releases have shipped
    with mistyped YYMM values that would poison a "must be greater" rule.
    """
    major, _, _ = current
    yymm = (today.year % 100) * 100 + today.month
    candidate = (major, yymm, today.day)
    if candidate == current:
        nxt = today + dt.timedelta(days=1)
        candidate = (major, (nxt.year % 100) * 100 + nxt.month, nxt.day)
    return candidate


def write_version(v: tuple[int, int, int]) -> None:
    text = INIT.read_text()
    new = PATTERN.sub(f"version_info = ({v[0]}, {v[1]}, {v[2]})", text, count=1)
    INIT.write_text(new)


def run(cmd: list[str], dry: bool, log=sys.stdout) -> None:
    print("$", " ".join(cmd), file=log)
    if not dry:
        subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="show actions without changing anything")
    ap.add_argument("--no-tag", action="store_true", help="skip git tag")
    ap.add_argument("--no-commit", action="store_true", help="skip git commit (and tag)")
    ap.add_argument(
        "--print-version",
        action="store_true",
        help="print only the new version to stdout (for scripting); progress goes to stderr",
    )
    ap.add_argument(
        "--version",
        help=(
            "use this exact version instead of computing one from today's date; "
            "lets a caller compute the version once and reuse it"
        ),
    )
    args = ap.parse_args()

    log = sys.stderr if args.print_version else sys.stdout

    current = read_current()
    if args.version:
        parts = args.version.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise SystemExit(f"--version must be N.N.N, got {args.version!r}")
        new = (int(parts[0]), int(parts[1]), int(parts[2]))
    else:
        new = next_version(current, dt.date.today())
    new_str = ".".join(map(str, new))
    print(f"Current: {'.'.join(map(str, current))}  ->  New: {new_str}", file=log)

    if args.print_version:
        print(new_str)

    if args.dry_run:
        return

    write_version(new)

    if args.no_commit:
        return
    run(["git", "add", str(INIT.relative_to(ROOT))], dry=False, log=log)
    run(["git", "commit", "-m", f"release {new_str}"], dry=False, log=log)
    if not args.no_tag:
        run(["git", "tag", new_str], dry=False, log=log)


if __name__ == "__main__":
    main()
