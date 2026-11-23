#!/usr/bin/env python3
"""Read a spec by section, so an agent loads what it edits and not the file
(ADR 0061).

Usage:
  bin/spec-section.py list [FILE]            key, level, lines and heading of every section
  bin/spec-section.py get KEY [KEY ...] [--file FILE]
                                             the sections, verbatim, in document order
  bin/spec-section.py find TEXT [--file FILE]
                                             the keys of the sections containing TEXT

FILE defaults to spec-source/sgai-spec.src.md. A KEY is a heading number
(`5.1.3`, `A.5`, `Annex A`, `4`) or, for a heading without one, its text.
`get` of a chapter key returns that heading's own section only, not its
subsections: ask for them by key.

Exit codes: 0 · 1 a KEY does not exist (the others are still printed) ·
2 the file cannot be split (repeated keys) · 64 wrong command line.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_sections  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(ROOT, "spec-source", "sgai-spec.src.md")


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


def main(argv):
    if not argv:
        usage("a command is required")
    cmd, rest = argv[0], argv[1:]
    path = DEFAULT
    if "--file" in rest:
        i = rest.index("--file")
        if i + 1 >= len(rest):
            usage("--file needs a path")
        path = rest[i + 1]
        rest = rest[:i] + rest[i + 2:]
    if cmd == "list" and len(rest) <= 1:
        path = rest[0] if rest else path
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            secs = spec_sections.split(fh.read())
    except spec_sections.SectionError as e:
        print(f"exit 2: {e}")
        return 2
    except OSError as e:
        print(f"exit 2: {e}")
        return 2
    if cmd == "list":
        if len(rest) > 1:
            usage("list takes at most one file")
        for s in secs:
            print(f"{s.key}\t{s.level}\t{len(s.lines)}\t{s.heading}")
        return 0
    if cmd == "get":
        if not rest:
            usage("get needs at least one key")
        idx = spec_sections.by_key(secs)
        missing = [k for k in rest if k not in idx]
        want = set(rest)
        sys.stdout.write("".join(s.text for s in secs if s.key in want))
        for k in missing:
            print(f"no section {k!r}", file=sys.stderr)
        return 1 if missing else 0
    if cmd == "find":
        if len(rest) != 1:
            usage("find needs one text")
        hits = [s.key for s in secs if rest[0] in s.text]
        print("\n".join(hits))
        return 0 if hits else 1
    usage(f"unknown command {cmd}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
