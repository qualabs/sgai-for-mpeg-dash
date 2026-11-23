#!/usr/bin/env python3
"""Assemble the spec document from spec-source/ (ADR 0060).

`spec-source/sgai-spec.src.md` is the prose. A line that is exactly a
directive is replaced by what it names, byte for byte:

  {{example:<path>}}       spec-source/examples/<path>
  {{xsd}}                  spec-source/syntax/sgai-extension.xsd
  {{include:<path>}}       spec-source/<path>   (a generated fragment)

An included file must end with a newline, so that the line after the
directive stays a line. Nothing else in the prose is touched.

Usage:
  bin/assemble-spec.py [--source DIR] --out FILE [--manifest FILE]
      write the assembled document; with --manifest, the sha256 of every
      source file it used (the prose first, then each included file once).
  bin/assemble-spec.py [--source DIR] --check DOC
      is DOC the assembly of the source? On a difference, names the first
      differing line and the source file that produced it.
  bin/assemble-spec.py [--source DIR] --list
      the directives, with the line of the prose they sit on.

What a green says: the document is what the source assembles to, byte for
byte. What it does not say: that the source is right; that is the other
checks' job (conformance, lint, trace).

Exit codes: 0 written / identical · 1 differs (--check) · 2 a directive
names a file that does not exist, an unknown directive, or an included file
without a final newline · 64 wrong command line.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRECTIVE = re.compile(r"^\{\{(example|xsd|include)(?::([^}]+))?\}\}\n?$")


class SourceError(Exception):
    pass


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


def target(source, kind, arg):
    if kind == "example" and arg:
        return os.path.join(source, "examples", arg)
    if kind == "xsd" and not arg:
        return os.path.join(source, "syntax", "sgai-extension.xsd")
    if kind == "include" and arg:
        return os.path.join(source, arg)
    raise SourceError(f"malformed directive {{{{{kind}{':' + arg if arg else ''}}}}}")


def assemble(source):
    """Return (text, regions, used): regions are (first_line, last_line, file)
    of the assembled document, 1-based and inclusive; used is the ordered list
    of files read."""
    prose = os.path.join(source, "sgai-spec.src.md")
    if not os.path.isfile(prose):
        raise SourceError(f"no prose at {prose}")
    out = []
    regions = []
    used = [prose]
    line_no = 0
    with open(prose, encoding="utf-8", newline="") as fh:
        src_lines = fh.readlines()
    for n, line in enumerate(src_lines, 1):
        m = DIRECTIVE.match(line)
        if not m:
            out.append(line)
            line_no += line.count("\n") or 1
            continue
        path = target(source, m.group(1), m.group(2))
        if not os.path.isfile(path):
            raise SourceError(f"sgai-spec.src.md:{n}: {line.strip()} names {rel(path)}, which does not exist")
        with open(path, encoding="utf-8", newline="") as fh:
            body = fh.read()
        if not body.endswith("\n"):
            raise SourceError(f"{rel(path)} does not end with a newline")
        out.append(body)
        k = body.count("\n")
        regions.append((line_no + 1, line_no + k, path))
        line_no += k
        if path not in used:
            used.append(path)
    return "".join(out), regions, used


def rel(path):
    """A path as a reader can open it: relative to the project when inside it."""
    r = os.path.relpath(path, ROOT)
    return path if r.startswith("..") else r


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main(argv):
    source = os.path.join(ROOT, "spec-source")
    out = manifest = check = None
    listing = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--source", "--out", "--manifest", "--check"):
            if i + 1 >= len(argv):
                usage(f"{a} needs a value")
            v = argv[i + 1]
            if a == "--source":
                source = v
            elif a == "--out":
                out = v
            elif a == "--manifest":
                manifest = v
            else:
                check = v
            i += 2
            continue
        if a == "--list":
            listing = True
            i += 1
            continue
        usage(f"unknown argument {a}")
    if sum(bool(x) for x in (out, check, listing)) != 1:
        usage("exactly one of --out, --check, --list")
    if manifest and not out:
        usage("--manifest goes with --out")

    if listing:
        prose = os.path.join(source, "sgai-spec.src.md")
        with open(prose, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                if DIRECTIVE.match(line):
                    print(f"{n}\t{line.strip()}")
        return 0

    try:
        text, regions, used = assemble(source)
    except SourceError as e:
        print(f"exit 2: {e}")
        return 2

    if out:
        with open(out, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        if manifest:
            with open(manifest, "w", encoding="utf-8") as fh:
                fh.write("# sha256 of the spec-source files assembled into " + os.path.basename(out) + "\n")
                for p in used:
                    fh.write(f"{sha(p)}  {rel(p)}\n")
        print(f"wrote {out}: {len(regions)} inclusions from {len(used) - 1} files; sha256 {hashlib.sha256(text.encode()).hexdigest()}")
        return 0

    with open(check, encoding="utf-8", newline="") as fh:
        doc = fh.read()
    if doc == text:
        print(f"identical: {check} is the assembly of {rel(source)} "
              f"(sha256 {hashlib.sha256(text.encode()).hexdigest()}); this says nothing about whether the source is right")
        return 0
    a, b = text.splitlines(keepends=True), doc.splitlines(keepends=True)
    first = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    line = first + 1
    owner = next((rel(p) for s, e, p in regions if s <= line <= e),
                 "spec-source/sgai-spec.src.md (prose)")
    print(f"differs: first difference at line {line} of {check}, produced by {owner}")
    print(f"  assembled: {a[first].rstrip() if first < len(a) else '<end>'}")
    print(f"  document : {b[first].rstrip() if first < len(b) else '<end>'}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
