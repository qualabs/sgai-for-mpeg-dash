#!/usr/bin/env python3
"""Write the one-time patch that takes the old pipeline's marks out of the
spec's prose (ADR 0065, 0066).

Before the source existed, a refine annotated each edit inline
(`<!-- refine: … -->`), an incremental did the same (`<!-- delta: … -->`),
unresolved items lived in a `## Refinement gaps` section, and the status
line carried a build iteration typed by hand. `bin/lint-spec.py` rejects the
first three in an assembled document, and the fourth goes stale at the next
build. Now the trace is the patch record, the gaps are a sidecar, and the
iteration is the assembler's `{{version}}`. This script finds the four and
writes the patch, in the format of `bin/apply-spec-patch.py --help`, that
removes them; the first major or incremental of the new pipeline applies it.

What it removes, and nothing else:
  comment   an HTML comment opening `<!-- refine` or `<!-- delta`, outside
            fenced code and outside inline code. A line left with nothing
            but whitespace is removed whole; otherwise the comment goes with
            one adjacent space (the one before it, else the one after).
            Any other HTML comment is left: whether it goes is not
            mechanical.
  gaps      every section whose heading contains "Refinement gaps", as a
            `delete_section` op. A gaps section that holds a directive is
            exit 2: the patch script refuses to delete it.
  status    in a `**Status:**` line, `build iteration <n>` becomes
            `build iteration {{version}}`.
  yaml      the same comments inside `syntax/syntax.yaml` (beside the
            prose), whose strings become cells of the generated tables:
            one `file` op per line that holds one, the line as `find`
            (widened with the lines before it until it occurs once).
            After applying, regenerate the tables
            (`bin/gen-syntax-tables.py --write`). The generator refuses an
            override equal to the text it derives, and some overrides
            existed only to carry a comment: the script runs the generator
            on a private copy as the oracle, and an override it calls
            redundant is removed (with its `override:` line when it was
            the only key) instead of stripped. Any other refusal of the
            generator, or a generator that cannot run, is exit 2.
            Fixtures are not scanned:
            a comment there is inside a code block, and is content.
One `replace_section` op per section that changes, then the `file` ops,
then the deletions.

Usage:
  bin/strip-legacy-annotations.py [--source FILE] --out PATCH.json

--source defaults to spec-source/sgai-spec.src.md.

It is idempotent by construction: on a source without the marks it finds
nothing and writes nothing, so a step that runs it on every build applies it
once.

What a green (exit 0) says: none of the four marks above is in the prose.
What it does not say: that the document is lint-clean (other rules, other
comments) or that removing a mark left the sentence around it right.

Exit codes: 0 nothing to remove, nothing written · 1 marks found, the patch
written to --out · 2 the source cannot be read or split, a gaps section
holds a directive, or the generator does not accept syntax.yaml without the
comments (or cannot run: it needs PyYAML and ISO's schema) · 64 wrong
command line.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_sections as ss  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(ROOT, "spec-source", "sgai-spec.src.md")
REASON = "one-time cleanup of the old pipeline's marks (ADR 0065, 0066; bin/strip-legacy-annotations.py)"

LEGACY = re.compile(r"<!--\s*(?:refine|delta)\b.*?-->")
STATUS = re.compile(r"^(\*\*Status:\*\*.*\bbuild iteration )v?\d+(?:\.\d+)*")


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


def in_code_span(line, pos):
    """True when `pos` sits inside an inline code span of `line`."""
    return line.count("`", 0, pos) % 2 == 1


def strip_line(line):
    """(new line or None to drop it, comments removed)."""
    body = line.rstrip("\n")
    nl = line[len(body):]
    removed = 0
    out = body
    while True:
        m = next((m for m in LEGACY.finditer(out) if not in_code_span(out, m.start())), None)
        if not m:
            break
        a, b = m.start(), m.end()
        if a > 0 and out[a - 1] == " ":
            a -= 1
        elif b < len(out) and out[b] == " ":
            b += 1
        out = out[:a] + out[b:]
        removed += 1
    if removed and not out.strip():
        return None, removed
    return out + nl, removed


def clean_section(text):
    lines = text.splitlines(keepends=True)
    out = []
    fence = False
    comments = status = 0
    for line in lines:
        if line.lstrip().startswith("```"):
            fence = not fence
            out.append(line)
            continue
        if fence:
            out.append(line)
            continue
        new, n = strip_line(line)
        comments += n
        if new is None:
            continue
        m = STATUS.match(new)
        if m and "{{version}}" not in new:
            new = STATUS.sub(lambda m: m.group(1) + "{{version}}", new, count=1)
            status += 1
        out.append(new)
    return "".join(out), comments, status


def where_in_yaml(lines, i):
    """(table id, row name, key) of line i of syntax.yaml."""
    key = re.match(r"^\s*([A-Za-z_]+):", lines[i])
    row = table = None
    for k in range(i, -1, -1):
        if row is None:
            m = re.match(r"^\s*- name: (\S+)", lines[k])
            if m:
                row = m.group(1)
        m = re.match(r"^- id: (\S+)", lines[k])
        if m:
            table = m.group(1)
            break
    return table, row, key.group(1) if key else None


def unique_find(body, lines, start, end):
    while body.count("".join(lines[start:end])) != 1 and start > 0:
        start -= 1
    return start


def yaml_ops(body, rel, drop=()):
    """One op per line of syntax.yaml holding a legacy comment. A line whose
    (table, row, key) is in `drop` is an override left equal to the derived
    text once the comment goes: it is removed, with its `override:` line when
    it was the only key under it."""
    ops, n = [], 0
    lines = body.splitlines(keepends=True)
    for i, line in enumerate(lines):
        new, c = strip_line(line)
        if not c:
            continue
        n += c
        if where_in_yaml(lines, i) in drop:
            first = i
            indent = len(line) - len(line.lstrip())
            if i > 0 and lines[i - 1].strip() == "override:":
                nxt = lines[i + 1] if i + 1 < len(lines) else ""
                if not nxt.strip() or len(nxt) - len(nxt.lstrip()) < indent:
                    first = i - 1
            start = unique_find(body, lines, first, i + 1)
            ops.append({"file": rel, "find": "".join(lines[start:i + 1]),
                        "replace": "".join(lines[start:first]), "reason": REASON})
            continue
        start = unique_find(body, lines, i, i + 1)
        ops.append({"file": rel, "find": "".join(lines[start:i + 1]),
                    "replace": "".join(lines[start:i]) + (new or ""), "reason": REASON})
    return ops, n


REDUNDANT = re.compile(r"^exit 1: (\S+) @?(\S+): override of (\w+) equals the derived text; drop it$", re.M)


def settle_yaml(srcdir, body, rel):
    """yaml ops that leave syntax.yaml generating, with gen-syntax-tables as
    the oracle: an override it calls equal to the derived text once its
    comment is gone is dropped instead of stripped. Raises ValueError when
    the generator fails for any other reason or cannot run."""
    drop = set()
    base = os.environ.get("XDG_RUNTIME_DIR")
    base = os.path.join(base, "cto") if base and os.path.isdir(base) else None
    if base:
        os.makedirs(base, exist_ok=True)
    for _ in range(50):
        ops, n = yaml_ops(body, rel, drop)
        new = body
        for op in ops:
            new = new.replace(op["find"], op["replace"], 1)
        with tempfile.TemporaryDirectory(prefix="strip-legacy-", dir=base) as tmp:
            copy = os.path.join(tmp, "src")
            shutil.copytree(srcdir, copy)
            with open(os.path.join(copy, rel), "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
            p = subprocess.run([sys.executable, os.path.join(ROOT, "bin", "gen-syntax-tables.py"),
                                "--source", copy, "--findings", os.path.join(tmp, "findings.md"), "--write"],
                               capture_output=True, text=True)
        if p.returncode == 0:
            return ops, n
        m = REDUNDANT.search(p.stdout)
        lines = body.splitlines(keepends=True)
        hit = m and (m.group(1), m.group(2), m.group(3))
        if not hit or hit in drop or not any(
                where_in_yaml(lines, k) == hit and strip_line(lines[k])[1] for k in range(len(lines))):
            raise ValueError("bin/gen-syntax-tables.py does not accept syntax.yaml without the comments: "
                             + (p.stdout + p.stderr).strip().splitlines()[-1:][0] if (p.stdout + p.stderr).strip()
                             else "bin/gen-syntax-tables.py failed with no output")
        drop.add(hit)
    raise ValueError("gave up settling syntax.yaml after 50 rounds")


def build(text, yaml_body=None, yaml_rel="syntax/syntax.yaml", srcdir=None):
    """(ops, counts). Raises ValueError for a gaps section with a directive."""
    ops, deletes = [], []
    counts = {"comments": 0, "status": 0, "gaps": 0, "yaml": 0}
    for sec in ss.split(text):
        if "refinement gaps" in sec.heading.lower():
            if any(ss.DIRECTIVE.match(l.strip()) for l in sec.lines):
                raise ValueError(f"section {sec.key!r} holds a directive")
            deletes.append({"delete_section": sec.key, "reason": REASON})
            counts["gaps"] += 1
            continue
        new, c, st = clean_section(sec.text)
        if new != sec.text:
            ops.append({"section": sec.key, "replace_section": new, "reason": REASON})
            counts["comments"] += c
            counts["status"] += st
    fops = []
    if yaml_body is not None:
        fops, counts["yaml"] = yaml_ops(yaml_body, yaml_rel)
        if fops and srcdir:
            fops, counts["yaml"] = settle_yaml(srcdir, yaml_body, yaml_rel)
    return ops + fops + deletes, counts


def main(argv):
    source, out = DEFAULT, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--source", "--out"):
            if i + 1 >= len(argv):
                usage(f"{a} needs a value")
            if a == "--source":
                source = argv[i + 1]
            else:
                out = argv[i + 1]
            i += 2
        else:
            usage(f"unknown argument {a}")
    if not out:
        usage("--out PATCH.json is required")
    try:
        with open(source, encoding="utf-8", newline="") as fh:
            text = fh.read()
        ypath = os.path.join(os.path.dirname(os.path.abspath(source)), "syntax", "syntax.yaml")
        ybody = None
        if os.path.isfile(ypath):
            with open(ypath, encoding="utf-8", newline="") as fh:
                ybody = fh.read()
        ops, counts = build(text, ybody, srcdir=os.path.dirname(os.path.abspath(source)))
    except (OSError, UnicodeDecodeError, ss.SectionError, ValueError) as e:
        print(f"exit 2: {e}")
        return 2
    summary = (f"{counts['comments']} comment(s), {counts['gaps']} gaps section(s), "
               f"{counts['status']} status line(s), {counts['yaml']} comment(s) in syntax/syntax.yaml")
    if not ops:
        print(f"clean: no legacy mark in {os.path.relpath(source, ROOT)}; nothing written")
        return 0
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"ops": ops}, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"found {summary} in {len(ops)} section(s); patch written to {out}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
