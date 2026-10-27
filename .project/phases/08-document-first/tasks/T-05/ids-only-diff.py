#!/usr/bin/env python3
"""Show that a file changed only requirement ids.

Takes OLD and NEW versions of a context/ file and the NEW 03 (for its
"Retired identifiers" table). Rewrites OLD by replacing every retired id with
the FIRST destination its row names, then collapses a duplicate the
substitution leaves ("R5.1 / R5.1", "R5.6, R5.6" -> one id), and prints the
unified line diff of that rewritten OLD against NEW. An empty diff means the
file changed nothing but ids. The script accepts nothing else: any exception
(for example the two UC-10 citations that went to R5.6) shows up in the diff
and is judged by the reader.

Usage: ids-only-diff.py OLD NEW NEW_03
Exit 0 if the diff is empty, 1 if not.
"""
import re, sys, difflib

old_p, new_p, req_p = sys.argv[1:4]
req = open(req_p, encoding="utf-8").read()
table = req[req.index("## Retired identifiers"):]
sub = {}
for m in re.finditer(r"^\| (R\d+\.\d+) \| (.+?) \|$", table, re.M):
    dest = re.findall(r"R\d+\.\d+", m.group(2))
    sub[m.group(1)] = dest[0]
old = open(old_p, encoding="utf-8").read()
new = open(new_p, encoding="utf-8").read()
rew = re.sub(r"\bR\d+\.\d+\b", lambda m: sub.get(m.group(0), m.group(0)), old)
prev = None
while prev != rew:
    prev = rew
    rew = re.sub(r"\b(R\d+\.\d+)(\s*[/,]\s*)\1\b", r"\1", rew)
print("retired ids in table: %d" % len(sub), file=sys.stderr)
d = list(difflib.unified_diff(rew.splitlines(), new.splitlines(),
                              "OLD-with-ids-substituted", "NEW", lineterm="", n=0))
print("\n".join(d))
sys.exit(1 if d else 0)
