#!/usr/bin/env python3
"""List, for every old unit of context/03-requirements.md, its old text and the
new text of every destination the obligation map names. It does not judge.

Units are the population of bin/check-promotable.py --population (criteria and
prose modals), found with the same positional rule. Prose units are numbered
per owner by position, so a NEW prose id need not be the OLD one: for a prose
destination the script prints every NEW prose paragraph of that owner that
carries a modal.

For each pair it prints the modal counts (MUST NOT, MUST, SHALL NOT, SHALL,
REQUIRED, SHOULD NOT, SHOULD, MAY) of the old text and of the joined new text,
and whether the old text is byte-identical to the new text of the same id after
normalising whitespace. Those are aids for the reader, not verdicts.

Usage: pairs.py OLD_03 NEW_03 MAP_TSV [--only ID,ID] [--changed-only]
Exit 2 if a map row names a destination that is not in NEW, or if the map
and the OLD population do not cover the same ids.
"""
import re, sys

MODALS = ["MUST NOT", "MUST", "SHALL NOT", "SHALL", "REQUIRED",
          "SHOULD NOT", "SHOULD", "MAY"]
MODAL_RE = re.compile(r"\b(MUST NOT|MUST|SHALL NOT|SHALL|REQUIRED|SHOULD NOT|SHOULD|MAY)\b")
POP_MODAL = re.compile(r"\bMUST NOT\b|\bMUST\b|\bSHALL NOT\b|\bSHALL\b|\bREQUIRED\b")
TOP = re.compile(r"^- \*\*((?:R\d+|DP-[\d.]+|OOS-\d+))\.")
CRIT = re.compile(r"^(\s*)- \*\*(R\d+\.\d+)\*\*")


def parse(text):
    """criteria: id -> block text; prose: list of (unit_id, owner, paragraph);
    prose_par: owner -> list of distinct paragraphs carrying a modal."""
    lines = text.split("\n")
    crits, prose, prose_par = {}, [], {}
    owner = None; n = {}; in_crit = False; ci = None; cur = None
    for i, line in enumerate(lines):
        m = CRIT.match(line)
        if m:
            cur = m.group(2); crits[cur] = [line]; in_crit = True; ci = len(m.group(1)); continue
        if in_crit and line.strip():
            h = len(line) - len(line.lstrip())
            if line.startswith("#") or h <= ci:
                in_crit = False; cur = None
        if in_crit and cur:
            crits[cur].append(line)
        mt = TOP.match(line)
        if mt:
            owner = mt.group(1)
        if not in_crit and owner and line.strip():
            par = paragraph(lines, i)
            if MODAL_RE.search(line):
                prose_par.setdefault(owner, [])
                if par not in prose_par[owner]:
                    prose_par[owner].append(par)
            for _ in POP_MODAL.findall(line):
                n[owner] = n.get(owner, 0) + 1
                prose.append(("%s#p%d" % (owner, n[owner]), owner, par))
    crits = {k: "\n".join(v).rstrip() for k, v in crits.items()}
    return crits, prose, prose_par


def paragraph(lines, i):
    a = i
    while a > 0 and lines[a - 1].strip() and not CRIT.match(lines[a]) and not lines[a - 1].startswith("#"):
        if CRIT.match(lines[a - 1]):
            break
        a -= 1
    b = i
    while b + 1 < len(lines) and lines[b + 1].strip() and not CRIT.match(lines[b + 1]):
        b += 1
    return "\n".join(lines[a:b + 1])


def counts(t):
    c = {}
    for m in MODAL_RE.findall(t):
        c[m] = c.get(m, 0) + 1
    return " ".join("%s=%d" % (k, c[k]) for k in MODALS if k in c) or "(none)"


def norm(t):
    return " ".join(t.split())


def main(argv):
    only = None; changed_only = False
    args = [a for a in argv]
    if "--only" in args:
        k = args.index("--only"); only = set(args[k + 1].split(",")); del args[k:k + 2]
    if "--changed-only" in args:
        args.remove("--changed-only"); changed_only = True
    old_p, new_p, map_p = args
    oc, op, opp = parse(open(old_p, encoding="utf-8").read())
    nc, np_, npp = parse(open(new_p, encoding="utf-8").read())
    rows = []
    for line in open(map_p, encoding="utf-8"):
        if line.startswith("#") or line.startswith("id\t"):
            continue
        f = line.rstrip("\n").split("\t")
        rows.append(f)
    old_ids = set(oc) | {u for u, _, _ in op}
    map_ids = {f[0] for f in rows if f[1] != "new"}
    bad = 0
    if old_ids != map_ids:
        print("POPULATION MISMATCH missing", sorted(old_ids - map_ids), "extra", sorted(map_ids - old_ids))
        bad = 1
    old_prose = {u: (o, p) for u, o, p in op}
    stats = {"identical": 0, "changed": 0}
    for f in rows:
        uid, kind, act, dest = f[0], f[1], f[2], f[3]
        what = f[5] if len(f) > 5 else ""
        if only and uid not in only:
            continue
        if kind == "new":
            continue
        old_t = oc[uid] if kind == "criterion" else old_prose[uid][1]
        dests = [d for d in dest.split(",") if d]
        new_parts = []
        for d in dests:
            if re.match(r"^R\d+\.\d+$", d):
                if d not in nc:
                    print("MISSING DESTINATION", uid, "->", d); bad = 1; continue
                new_parts.append((d, nc[d]))
            else:
                ow = d.split("#")[0]
                pars = npp.get(ow, [])
                if not pars:
                    new_parts.append((d + " (owner prose)", "<<no prose paragraph with a modal under %s in NEW>>" % ow))
                for k, p in enumerate(pars, 1):
                    new_parts.append(("%s prose paragraph %d" % (ow, k), p))
        # for prose rewritten into a criterion, also show what is left in the owner's prose
        if kind == "prose" and act != "queda":
            ow = uid.split("#")[0]
            for k, p in enumerate(npp.get(ow, []), 1):
                new_parts.append(("%s prose paragraph %d (remaining)" % (ow, k), p))
        same_id_new = nc.get(uid) if kind == "criterion" else None
        ident = False
        if kind == "criterion" and same_id_new is not None:
            ident = norm(same_id_new) == norm(old_t)
        elif kind == "prose":
            ident = any(norm(old_t) == norm(p) for _, p in new_parts)
        stats["identical" if ident else "changed"] += 1
        if changed_only and ident:
            continue
        print("=" * 78)
        print("UNIT %s  kind=%s  action=%s  dest=%s  %s" % (uid, kind, act, dest,
              "IDENTICAL-TEXT" if ident else "TEXT-CHANGED"))
        if what:
            print("MAP NOTE:", what)
        print("OLD modals:", counts(old_t))
        print("--- OLD")
        print(old_t)
        joined = "\n".join(p for _, p in new_parts)
        print("NEW modals (all destinations joined):", counts(joined))
        for d, p in new_parts:
            print("--- NEW %s" % d)
            print(p)
    print("=" * 78)
    print("SUMMARY identical=%d changed=%d" % (stats["identical"], stats["changed"]))
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
