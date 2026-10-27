#!/usr/bin/env python3
"""Build the obligation map of phase 08-document-first.

Reads Annex A of the phase DESIGN.md and context/03-requirements.md as it
stood at REFERENCE (via git show), and writes obligation-map.tsv:

    id  kind  action  destination  old_line  what_moves

One row per unit of `check-promotable.py --population` for 03 (criteria
and prose modals), plus the two new criteria. Exits 1 if any unit of the
population has no decision or a decision names a unit that does not exist.

Usage: build-map.py [--design PATH] [--out PATH]   (from the project root)
"""
import re, subprocess, sys, os

REFERENCE = "44cfff4"
HERE = os.path.dirname(os.path.abspath(__file__))
design_path = os.path.join(HERE, "..", "..", "DESIGN.md")
out_path = os.path.join(HERE, "obligation-map.tsv")
args = sys.argv[1:]
while args:
    a = args.pop(0)
    if a == "--design": design_path = args.pop(0)
    elif a == "--out": out_path = args.pop(0)
    else: sys.exit(f"unknown argument {a}")

req = subprocess.run(["git", "show", f"{REFERENCE}:./context/03-requirements.md"],
                     capture_output=True, text=True, check=True).stdout
design = open(design_path, encoding="utf-8").read()

# --- population of 03, positionally, as check-promotable.py finds it
units = []  # (id, kind, line)
lines = req.split("\n")
owner = None; prose_n = {}; in_crit = False; ci = None
top = re.compile(r"^- \*\*((?:R\d+|DP-[\d.]+|OOS-\d+))\.")
crit = re.compile(r"^(\s*)- \*\*(R\d+\.\d+)\*\*")
modal = re.compile(r"\bMUST NOT\b|\bMUST\b|\bSHALL NOT\b|\bSHALL\b|\bREQUIRED\b")
for i, line in enumerate(lines, 1):
    m = crit.match(line)
    if m:
        units.append((m.group(2), "criterion", i)); in_crit = True; ci = len(m.group(1)); continue
    if in_crit and line.strip():
        h = len(line) - len(line.lstrip())
        if line.startswith("#") or h <= ci: in_crit = False
    m = top.match(line)
    if m: owner = m.group(1)
    if not in_crit and owner and modal.search(line):
        for _ in modal.findall(line):
            prose_n[owner] = prose_n.get(owner, 0) + 1
            units.append((f"{owner}#p{prose_n[owner]}", "prose", i))

# --- decisions on criteria: Annex A.2 (the ones that change) and A.3 (the ones that stay)
dec = {}
note = {}
# Places that receive part of a unit's content, named in the A.2 "lugar nuevo"
# text but not in its action column. T-05 looks for the obligation in all of them.
SECONDARY = {
    "R5.2": ["R5.6"],    # "los chequeos quedan en R5.6"
    "R7.2": ["R7.1"],    # "no es un reordenamiento" va a R7.1
    "R35.6": ["R35.4"],  # "la frase sobre falla va a R35.4"
    "R19.3": ["R4.11"],  # "la parte del tope va a R4.11"
}
a2 = design[design.index("### A.2."):design.index("### A.3.")]
for m in re.finditer(r"^\| \d+ \| (R\d+\.\d+) \| [^|]+\| [^|]+\| ([^|]+?) \| (.+) \|$", a2, re.M):
    cid, act, where = m.group(1), m.group(2).strip(), m.group(3)
    if act.startswith("se fusiona en"):
        dest = re.findall(r"R\d+\.\d+", act); act = "se fusiona"
    elif act == "se retira":
        dest = [x for x in re.findall(r"R\d+\.\d+", where) if x != cid]
    else:
        dest = [cid]
    dest += [d for d in SECONDARY.get(cid, []) if d not in dest]
    if cid in dec: sys.exit(f"{cid} decided twice")
    dec[cid] = (act, dest)
    note[cid] = where.strip()
# Annex A.3: five that stay change only a reference, or receive one sentence.
QUEDA_NOTES = {
    "R14.3": "su remisión a R14.1 pasa a R7.1",
    "R39.3": "su remisión a R38.3 pasa a R29.1",
    "R34.4": "su remisión a R34.2 pasa a R34.1",
    "R34.3": "recibe de R34.5 que cruzar la ventana sin que empiece un aviso la deja disponible",
    "R35.4": "recibe de R35.6: un cierre es un resultado de la presentación, no una falla",
}
a3 = design[design.index("### A.3."):design.index("### A.4.")]
for cid in re.findall(r"R\d+\.\d+", a3.split("\n\n")[1]):
    if cid in dec: sys.exit(f"{cid} decided twice")
    dec[cid] = ("queda", [cid])
    note[cid] = QUEDA_NOTES.get(cid, "")

# --- decisions on prose modals. A prose modal that restates, as a Player
# obligation, a criterion this rewrite changes loses its modal in the prose
# and its obligation is at the criterion named; every other one stays.
PROSE_MOVES = {
    "R4#p1": ["R4.2"],           # Player enforces the cap, stopping mid-ad
    "R5#p1": ["R5.1"],           # render the first satisfiable option
    "R5#p2": ["R5.3"],           # skip a candidate with none, fall through
    "R5#p3": ["R5.1", "R5.6"],   # select by capability and allowed layouts, in order
    "R7#p1": ["R7.1"],           # play in document order
    "R7#p2": ["R7.1", "R5.3"],   # do not re-order; dropping is R5.3
    "R6#p2": ["R1.1", "R1.5"],   # ignore unknown namespaces: the base rule (R6.4 retires)
}
for uid, kind, _ in units:
    if kind == "prose":
        dec[uid] = ("se reescribe en la prosa", PROSE_MOVES[uid]) if uid in PROSE_MOVES else ("queda", [uid])
missing_moves = sorted(set(PROSE_MOVES) - {u for u, k, _ in units if k == "prose"})

pop = {u for u, _, _ in units}
missing = sorted(pop - set(dec)); extra = sorted(set(dec) - pop)
crit_ids = {u for u, k, _ in units if k == "criterion"}
bad_dest = sorted({d for a, ds in dec.values() for d in ds
                   if a != "queda" and re.fullmatch(r"R\d+\.\d+", d)
                   and d not in crit_ids and d not in ("R12.5", "R40.9")})
gone = {u for u, (a, _) in dec.items() if a in ("se fusiona", "se retira")}
bad_dest += sorted({d for a, ds in dec.values() for d in ds if d in gone})
print("reference", REFERENCE)
print("missing", missing, "extra", extra, "prose moves naming nothing", missing_moves,
      "destinations that do not exist or retire", bad_dest)
if missing or extra or missing_moves or bad_dest:
    sys.exit(1)

from collections import Counter
for kind in ("criterion", "prose"):
    c = Counter(dec[u][0] for u, k, _ in units if k == kind)
    print(kind, sum(c.values()), dict(sorted(c.items())))
print("after", len(crit_ids) - len(gone & crit_ids) + 2, "criteria; gone", len(gone))

with open(out_path, "w", encoding="utf-8") as fh:
    fh.write(f"# reference\t{REFERENCE}\n")
    fh.write("id\tkind\taction\tdestination\told_line\twhat_moves\n")
    for u, kind, ln in units:
        a, ds = dec[u]
        fh.write(f"{u}\t{kind}\t{a}\t{','.join(ds)}\t{ln}\t{note.get(u, '')}\n")
    for cid in ("R12.5", "R40.9"):
        m = re.search(r"^- \*\*" + re.escape(cid) + r"\*\* (.+)$", design, re.M)
        fh.write(f"{cid}\tnew\tnuevo\t{cid}\t-\t{m.group(1).strip()}\n")
print("wrote", os.path.relpath(out_path))
