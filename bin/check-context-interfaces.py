#!/usr/bin/env python3
"""Step 0.7 of the build: does `context/03-requirements.md` keep the
structural part of its writing rule?

The rule ("How requirements are written", at the top of 03) says the
meaning of each element of the three interfaces is written once, in a
criterion held by the party that writes the element, and that identifiers
are stable. The "Interfaces" section indexes every element against the
criterion that defines it, and the "Retired identifiers" table says where
the content of a merged or withdrawn criterion went.

WHAT THIS CATCHES:

  * an index row that points to a criterion that does not exist;
  * an element in two rows, of one interface or of two;
  * an index row that points to a criterion none of whose roles is the
    party that writes that interface (Publisher or spec document for
    I-MPD, Player or spec document for I-REQ, APS or spec document for
    I-RES);
  * a retired identifier cited anywhere in `context/` outside its row of
    the retired table, or still defined as a criterion;
  * a criterion that existed in 03 at REFERENCE_COMMIT, is missing now,
    and is not in the retired table.

WHAT THIS DOES NOT CATCH, and cannot: two criteria that say the same thing
in other words; a Player criterion whose content follows from the meaning
of the document; prose that restates a meaning; an element the document
carries that nobody put in the index; a retired row that sends its
content to the wrong place. All of those are about meaning and have no
syntactic signature. A green here means the index and the identifiers
hold together, not that the rule was followed.

REFERENCE_COMMIT is the commit on which the obligation map of phase
08-document-first was frozen. It is not the commit of the published
build: criteria born after that build are cited by 04 and by the ADRs,
and some of them were retired.

EXIT CODES
  0   nothing found
  1   findings, listed
  2   cannot tell: no "Interfaces" section, an interface with no rows, no
      "Retired identifiers" section, or REFERENCE_COMMIT unreadable. A
      rule that never ran is not a rule that found nothing.
  64  wrong command line

Usage:  bin/check-context-interfaces.py [--quiet] [--context DIR]
        bin/check-context-interfaces.py --help
"""
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCE_COMMIT = "44cfff4"
REQUIREMENTS = "03-requirements.md"
WRITERS = {
    "I-MPD": {"Publisher", "spec document"},
    "I-REQ": {"Player", "spec document"},
    "I-RES": {"APS", "spec document"},
}
CRITERION = re.compile(r"^\s*- \*\*(R\d+\.\d+)\*\* \(([^)]+)\)", re.M)
ID = re.compile(r"\bR\d+\.\d+(?![0-9])")
ROW = re.compile(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$")


def section(text, heading):
    """Body of the `## heading` section, up to the next `## `; None if absent."""
    m = re.search(r"^## " + re.escape(heading) + r"\s*$", text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    n = re.search(r"^## ", rest, re.M)
    return rest[: n.start()] if n else rest


def rows(block):
    out = []
    for n, line in enumerate(block.split("\n")):
        m = ROW.match(line)
        if m and not set(m.group(1)) <= set("-: ") and m.group(2) not in ("Defined in", "Content now in"):
            out.append((m.group(1), m.group(2)))
    return out


def parties(role):
    return {p.strip() for p in re.split(r"\s*[+/,]\s*", role)}


def main(argv):
    quiet = False
    ctx = os.path.join(ROOT, "context")
    args = list(argv)
    while args:
        a = args.pop(0)
        if a in ("-h", "--help"):
            print(__doc__.strip())
            return 0
        if a == "--quiet":
            quiet = True
        elif a == "--context" and args:
            ctx = args.pop(0)
        else:
            print(f"usage error: unknown or incomplete argument {a!r} (see --help)")
            return 64
    path = os.path.join(ctx, REQUIREMENTS)
    if not os.path.isfile(path):
        print(f"CANNOT TELL: {path} does not exist")
        return 2
    text = open(path, encoding="utf-8").read()
    criteria = {m.group(1): m.group(2) for m in CRITERION.finditer(text)}

    cannot = []
    interfaces = section(text, "Interfaces")
    retired_block = section(text, "Retired identifiers")
    if interfaces is None:
        cannot.append('no "## Interfaces" section in 03')
    if retired_block is None:
        cannot.append('no "## Retired identifiers" section in 03')
    index = {}
    if interfaces is not None:
        for name in WRITERS:
            m = re.search(r"^### " + re.escape(name) + r"\b.*$", interfaces, re.M)
            if not m:
                cannot.append(f"no {name} table in the Interfaces section")
                continue
            body = interfaces[m.end():]
            nxt = re.search(r"^### ", body, re.M)
            index[name] = rows(body[: nxt.start()] if nxt else body)
            if not index[name]:
                cannot.append(f"the {name} table has no rows")
    try:
        old = subprocess.run(
            ["git", "-C", ROOT, "show", f"{REFERENCE_COMMIT}:context/{REQUIREMENTS}"],
            capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, OSError) as e:
        cannot.append(f"cannot read 03 at {REFERENCE_COMMIT}: {e}")
        old = None
    if cannot:
        for c in cannot:
            print(f"CANNOT TELL: {c}")
        print("\nEXIT 2: the check did not run, so zero findings would mean nothing.")
        return 2

    findings = []
    # 1-3: the index
    seen = {}
    for name, items in index.items():
        for element, target in items:
            key = re.sub(r"\s+", " ", element.strip().lower())
            if key in seen:
                findings.append(f"element in two rows: {element!r} ({seen[key]} and {name})")
            else:
                seen[key] = name
            ids = ID.findall(target)
            if len(ids) != 1 or target.strip() != ids[0]:
                findings.append(f"{name}: row {element!r} must point to exactly one criterion id, has {target!r}")
                continue
            cid = ids[0]
            if cid not in criteria:
                findings.append(f"{name}: row {element!r} points to {cid}, which is not a criterion of 03")
            elif not parties(criteria[cid]) & WRITERS[name]:
                findings.append(f"{name}: row {element!r} points to {cid} ({criteria[cid]}), "
                                f"not held by the party that writes {name} ({' or '.join(sorted(WRITERS[name]))})")

    # 4: retired ids
    retired = {}
    for ident, dest in rows(retired_block):
        if ID.fullmatch(ident):
            retired[ident] = dest
    retired_lines = {line for line in retired_block.split("\n") if ROW.match(line)}
    for cid in sorted(retired):
        if cid in criteria:
            findings.append(f"{cid} is in the retired table and still defined as a criterion")
    for f in sorted(glob.glob(os.path.join(ctx, "*.md"))):
        for n, line in enumerate(open(f, encoding="utf-8").read().split("\n"), 1):
            if os.path.basename(f) == REQUIREMENTS and line in retired_lines:
                continue
            for cid in ID.findall(line):
                if cid in retired:
                    findings.append(f"retired {cid} cited at {os.path.basename(f)}:{n} (now in {retired[cid]})")

    # 5: ids that vanished without a retired row
    for cid in sorted({m.group(1) for m in CRITERION.finditer(old)}):
        if cid not in criteria and cid not in retired:
            findings.append(f"{cid} existed at {REFERENCE_COMMIT}, is gone, and the retired table does not list it")

    for f in findings:
        print(f"FINDING: {f}")
    total = sum(len(v) for v in index.values())
    if findings:
        print(f"\nEXIT 1: {len(findings)} finding(s).")
        return 1
    if not quiet:
        print(f"OK: {total} index rows ({', '.join(f'{k} {len(v)}' for k, v in index.items())}) "
              f"point to existing criteria held by their writer; {len(retired)} retired ids, "
              f"none cited outside its row and none vanished unlisted since {REFERENCE_COMMIT}.")
        print("    This says the index and the identifiers hold together. It does NOT say a")
        print("    meaning is written once: a restated meaning or a deducible Player criterion pass here.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
