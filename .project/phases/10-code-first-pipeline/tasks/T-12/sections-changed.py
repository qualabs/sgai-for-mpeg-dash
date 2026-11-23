#!/usr/bin/env python3
"""T-12 dry run only: the `## Sections changed` table built the way
apply-context-delta.prompt §7 says, from the patch records, the two source
manifests and the `{{version}}` token — never from comparing the documents
(that is what check-incremental.py scope does with it).

  sections-changed.py vBASE vHEAD BASE_MANIFEST
"""
import glob, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
sys.path.insert(0, os.path.join(ROOT, "bin"))
import spec_sections as ss  # noqa: E402

base, head, base_manifest = sys.argv[1:4]
prose = open("spec-source/sgai-spec.src.md").read()
src = ss.split(prose)
old = ss.by_key(ss.split(open(f"output/{base}-sgai-spec.md").read()))
new = ss.by_key(ss.split(open(f"output/{head}-sgai-spec.md").read()))

rows = {}
recs = sorted(glob.glob(f"output-analysis/{head}-delta-patch-*.json"))
by_rec = {}
for r in recs:
    k = int(r.rsplit("-", 1)[1].split(".")[0])
    for key in json.load(open(r))["sections_changed"]:
        by_rec.setdefault(key, set()).add(k)
for key, ks in by_rec.items():
    if ks == {0}:
        rows[key] = "cleanup"
    elif key not in old:
        rows[key] = "added"
    elif key not in new:
        rows[key] = "removed"
    else:
        rows[key] = "modified"


def manifest(p):
    return {l.split()[1]: l.split()[0] for l in open(p) if not l.startswith("#")}


a, b = manifest(base_manifest), manifest(f"output-analysis/{head}-source.sha256")
moved = sorted(p for p in set(a) | set(b) if a.get(p) != b.get(p) and not p.endswith("sgai-spec.src.md"))
for p in moved:
    rel = p.split("spec-source/", 1)[1]
    if rel.startswith("examples/"):
        d = "{{example:%s}}" % rel[len("examples/"):]
    elif rel == "syntax/sgai-extension.xsd":
        d = "{{xsd}}"
    else:
        d = "{{include:%s}}" % rel
    for s in src:
        if d in s.text:
            rows.setdefault(s.key, "modified")
for s in src:
    if "{{version}}" in s.text:
        rows.setdefault(s.key, "version")
print("## Sections changed\n\n| Section | Change | Rows |\n|---------|--------|------|")
for k in [s.key for s in src] + sorted(set(rows) - {s.key for s in src}):
    if k in rows:
        print(f"| {k} | {rows[k]} | {'—' if rows[k] in ('cleanup', 'version') else '1'} |")
print(f"files moved: {moved}", file=sys.stderr)
