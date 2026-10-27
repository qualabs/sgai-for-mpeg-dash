#!/usr/bin/env python3
"""Pair the 76 elements of DESIGN.md A.7 with the rows of the "## Interfaces"
section of NEW 03, interface by interface and in order, and print each pair
with the id A.7 names ("Donde queda") and the id the index names.

Pairing is positional within each interface. An A.7 element whose "Donde
queda" names no criterion of 03 (it says the element stays in another file) is
expected to have no row, and the pairing skips it; any other count mismatch
makes positional pairing meaningless and the script exits 2. It does not judge
whether the element text matches: the reader reads both columns.

Usage: interfaces-vs-a7.py DESIGN.md NEW_03
"""
import re, sys

design = open(sys.argv[1], encoding="utf-8").read()
req = open(sys.argv[2], encoding="utf-8").read()
a7 = design[design.index("### A.7."):]
a7 = a7[:re.search(r"^### A\.[89]|^## ", a7[5:], re.M).start() + 5]
parts = re.split(r"^#### (I-\w+)", a7, flags=re.M)
# the I-MPD table comes before the first #### heading
blocks = {"I-MPD": parts[0]}
for k in range(1, len(parts), 2):
    blocks[parts[k]] = parts[k + 1]
idx = req[req.index("## Interfaces"):req.index("## Design principles")]
iparts = re.split(r"^### (I-\w+)", idx, flags=re.M)
iblocks = {iparts[k]: iparts[k + 1] for k in range(1, len(iparts), 2)}
bad = 0
total_a7 = total_idx = 0
for itf in ("I-MPD", "I-REQ", "I-RES"):
    rows = re.findall(r"^\| (\d+) \| (.+?) \| .+? \| .+? \| .+? \| (.+?) \|$", blocks[itf], re.M)
    irows = re.findall(r"^\| (?!Element|---)(.+?) \| (R\d+\.\d+) \|$", iblocks[itf], re.M)
    total_a7 += len(rows); total_idx += len(irows)
    print("## %s: A.7 %d elements, index %d rows" % (itf, len(rows), len(irows)))
    j = 0
    for n, el, where in rows:
        ids = re.findall(r"R\d+\.\d+", where)
        if not ids:
            print("  A.7 #%s %-60s -> NO ROW EXPECTED (A.7: %s)" % (n, el[:60], where))
            continue
        if j >= len(irows):
            print("  A.7 #%s has no index row left" % n); bad = 1; continue
        iel, iid = irows[j]; j += 1
        flag = "same" if iid in ids else "DIFFERENT"
        print("  A.7 #%-2s %-55s A.7:%-14s | index: %-55s %s  [%s]" % (
            n, el[:55], ",".join(ids), iel[:55], iid, flag))
    if j != len(irows):
        print("  %d index rows left unpaired" % (len(irows) - j)); bad = 1
print("TOTAL A.7 elements %d, index rows %d" % (total_a7, total_idx))
sys.exit(2 if bad else 0)
