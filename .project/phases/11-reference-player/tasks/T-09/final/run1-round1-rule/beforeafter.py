"""Before (T-09 log) -> after (final log), per job, and the updated totals.
Usage: beforeafter.py T09_LOG FINAL_LOG"""
import sys
from collections import Counter
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from parselog import parse
before, after = parse(sys.argv[1]), parse(sys.argv[2])
def short(v):
    c = Counter(v.values())
    return ", ".join(f"{n} {o}" for o, n in sorted(c.items()))
print("| Job | T-09 | final | FAIL fields now |")
print("|---|---|---|---|")
for k in sorted(after):
    b = before.get(k, {})
    fails = [f for f, o in sorted(after[k].items()) if o == "FAIL"]
    print(f"| {k[0]} {k[1]}{' [' + k[2] + ']' if k[2] else ''} | {short(b) or '(not in T-09)'} | {short(after[k])} | {', '.join(fails)} |")
tb = Counter(o for v in before.values() for o in v.values())
rem = Counter(o for k, v in before.items() if k in after for o in v.values())
add = Counter(o for v in after.values() for o in v.values())
new = [k for k in after if k not in before]
print()
print("T-09 job-level:", dict(tb), "jobs", len(before))
print("rerun jobs:", len(after), "of which not in T-09:", new)
print("removed (T-09 results of rerun jobs):", dict(rem))
print("added (final results):", dict(add))
tot = tb - rem + add
print("updated:", {o: tb[o] - rem[o] + add[o] for o in set(tb) | set(add)})
