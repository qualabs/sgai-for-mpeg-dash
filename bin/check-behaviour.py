#!/usr/bin/env python3
"""The behaviour tests of the reference Player: does every criterion the
level-2 catalogue sends to level 3 have a test or a reason it has none, and
does each still say what its criterion says? (ADR 0077, ADR 0078)

    check-behaviour.py [--source DIR] [--context DIR] [--json]
    check-behaviour.py uncovered [--source DIR] [--context DIR]
    check-behaviour.py criterion R<n>.<m> [--context DIR]

`uncovered` prints, one per line, `<criterion>  <holder>  <criterion_sha256>`
for every criterion of the population with neither a test nor an index
entry (exit 1 when there is one, 0 when none). `criterion` prints one
criterion's `criterion_sha256` on line 1 and its text after it, the text the
hash is taken over (exit 1 if context/03 does not define it): a test copies
the hash from there, never computes it by hand.

DIR defaults: --source spec-source, --context context. A test is
DIR/behaviour/R<n>.<m>[-<k>].yaml, valid against DIR/scenarios/schema.json
with `criterion` and `criterion_sha256`; DIR/behaviour/index.yaml lists the
criteria that have no test, each NOT_VERIFIABLE with its reason;
DIR/behaviour/README.md says how a test is written.

THE POPULATION is read by code, every run, from RULES of
bin/conformance/spec/catalog.py: a criterion is in it when at least one rule
of that criterion has a `not_verifiable` that starts with catalog.PLAYER
("Player behaviour: level 3 ...") or mentions "level 3" other than
"level 3a" (3a is the legacy Players, R1.1: not this battery). A rule with a
check, whatever its notes say, does not bring its criterion in. The hash is
criteria.sha256 over the criterion's text as criteria.py defines it, both
imported, never rewritten here.

Checks, each a finding `<check>  <test file or criterion>  <detail>`:

  B-COVER    every criterion of the population has a test or an entry in
             index.yaml, and not both
  B-POP      every test and every entry names a criterion of the population
  B-SCHEMA   a test parses as YAML, is valid against the schema, carries
             `criterion` (not `uc`), and its file name starts with that
             criterion; index.yaml is valid: its format, each entry with
             criterion, criterion_sha256 and a reason, no criterion twice
  B-HASH     criterion_sha256 is the criterion's text as it is now. Exit 2:
             the test may still be right, but nobody has looked since the
             criterion changed
  B-RETIRED  the criterion is in 03's "Retired identifiers" table. Exit 2:
             its content went elsewhere, and the test must follow it
  S-*        on every test, the checks of bin/check-scenarios.py that do not
             depend on a UC: S-CAPS, S-FIXTURE (fixtures green on levels 1
             and 2), S-REF, S-LAYOUT, S-TIME, S-GEOM, S-SCHEMA

Then, for every test and class: `NOT_VERIFIABLE — no executor`, and for every
index entry: `NOT_VERIFIABLE — <reason>`. No Player runs a test here and no
browser is started. A green run says the tests are well formed, rest on green
fixtures, cover the population, and were written against the criteria as
they are now. It does NOT say that any Player behaves as a test says, nor
that a test, or an index reason, reads its criterion correctly: that is for
a person, and for the executor.

Exit codes:
  0   nothing found
  1   at least one finding (an uncovered criterion included)
  2   cannot tell: a hash is stale (B-HASH), a criterion was retired
      (B-RETIRED), the catalogue cannot be imported or sends no criterion to
      level 3, a criterion of the population is not in context/03, or
      context/03 cannot be read as expected. Uncertainty wins over both others
  64  wrong command line

Dependencies outside the standard library: lxml, PyYAML, jsonschema. When
one is not importable the script re-runs itself under `uv run --with` the
pinned versions.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location("check_scenarios", HERE / "check-scenarios.py")
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

USAGE = __doc__.split("\n\n")[1]
INDEX_FORMAT = "sgai-behaviour-index/1"
TEST_NAME = re.compile(r"^(R\d+\.\d+)(-\d+)?\.yaml$")
CID = re.compile(r"^R\d+\.\d+$")
LEVEL3 = re.compile(r"level 3(?!a)")
HARD = ("B-HASH", "B-RETIRED")
INDEX_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["format", "not_verifiable"],
    "properties": {
        "format": {"const": INDEX_FORMAT},
        "not_verifiable": {
            "type": "array",
            "items": {
                "type": "object", "additionalProperties": False,
                "required": ["criterion", "criterion_sha256", "reason"],
                "properties": {
                    "criterion": {"type": "string", "pattern": CID.pattern},
                    "criterion_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "reason": {"type": "string", "minLength": 1},
                },
            },
        },
    },
}


def order(cid: str) -> tuple:
    return tuple(int(x) for x in cid[1:].split("."))


def population(rules, player: str) -> set:
    """The criteria the level-2 catalogue sends to level 3 (the rule is in
    the module docstring)."""
    return {r.criterion for r in rules
            if r.not_verifiable.startswith(player) or LEVEL3.search(r.not_verifiable)}


def load_population() -> set:
    from conformance.spec import catalog
    return population(catalog.RULES, catalog.PLAYER)


def run(source: Path, context_dir: Path, pop=None) -> dict:
    """pop: the population, read from the catalogue when None (a test passes
    its own)."""
    import jsonschema
    import yaml
    from conformance import source as srcmod
    from conformance.spec import criteria

    out = {"findings": [], "cannot": [], "population": [], "tests": {}, "not_verifiable": {},
           "uncovered": []}

    def finder(key):
        def find(check, detail):
            out["findings"].append({"check": check, "uc": key, "detail": detail})
        return find

    try:
        ctx = cs.load_context(source, context_dir)
    except (OSError, cs.CannotTell, srcmod.IndexError_, json.JSONDecodeError) as e:
        out["cannot"].append(str(e))
        return out
    text03 = ctx["c03"]
    defined = criteria.criteria(text03)
    retired = criteria.retired(text03)
    try:
        pop = set(load_population() if pop is None else pop)
    except Exception as e:  # the catalogue failing to import is a cannot-tell, whatever the reason
        out["cannot"].append(f"the level-2 catalogue cannot be imported: {type(e).__name__}: {e}")
        return out
    if not pop:
        out["cannot"].append("the level-2 catalogue sends no criterion to level 3: the population cannot be read")
        return out
    for cid in sorted(pop - set(defined), key=order):
        out["cannot"].append(f"the catalogue sends {cid} to level 3, but context/03 does not define it")
    out["population"] = sorted(pop, key=order)

    def judge(cid, stored, find):
        """B-RETIRED, B-POP, B-HASH for one named criterion; True when it
        counts as covering a population criterion."""
        if cid in retired:
            find("B-RETIRED", f"{cid} was retired; context/03 says its content went to: {retired[cid]}")
            return False
        if cid not in defined:
            find("B-POP", f"{cid} is not a criterion of context/03")
            return False
        if cid not in pop:
            find("B-POP", f"{cid} is not in the population: the level-2 catalogue does not send it to level 3")
            return False
        now = criteria.pin_entry(text03, cid)["sha256"]
        if stored != now:
            find("B-HASH", f"criterion_sha256 {stored[:12]}… is not {cid}'s {now[:12]}…: the criterion changed")
        return True

    bdir = source / "behaviour"
    tested: dict = {}
    validator = jsonschema.Draft202012Validator(ctx["schema"])
    for p in sorted(bdir.glob("*.yaml")) if bdir.is_dir() else []:
        if p.name == "index.yaml":
            continue
        find = finder(p.name)
        m = TEST_NAME.match(p.name)
        if not m:
            find("B-SCHEMA", f"{p.name} is not a test name (R<n>.<m>[-<k>].yaml)")
            continue
        try:
            v = yaml.safe_load(p.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            find("B-SCHEMA", f"not YAML: {e}")
            continue
        errs = sorted(validator.iter_errors(v), key=lambda e: list(e.absolute_path))
        if errs:
            for e in errs:
                find("B-SCHEMA", f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}")
            continue
        if "criterion" not in v:
            find("B-SCHEMA", "a behaviour test carries `criterion` and `criterion_sha256`, not `uc`")
            continue
        cid = v["criterion"]
        if m.group(1) != cid:
            find("B-SCHEMA", f"`criterion` is {cid} but the file is {p.name}")
        if judge(cid, v["criterion_sha256"], find):
            tested.setdefault(cid, []).append(p.name)
        cs.check_body(p.name, v, ctx, find)
        out["tests"][p.name] = {c: cs.NO_EXECUTOR for c in sorted(v["outcomes"])}

    entries: dict = {}
    ip = bdir / "index.yaml"
    if ip.is_file():
        find = finder("index.yaml")
        try:
            idx = yaml.safe_load(ip.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            find("B-SCHEMA", f"not YAML: {e}")
            idx = None
        errs = list(jsonschema.Draft202012Validator(INDEX_SCHEMA).iter_errors(idx)) if idx is not None else []
        for e in errs:
            find("B-SCHEMA", f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}")
        if idx is not None and not errs:
            for e in idx["not_verifiable"]:
                cid = e["criterion"]
                if cid in entries:
                    find("B-SCHEMA", f"{cid} has two entries")
                    continue
                if judge(cid, e["criterion_sha256"], finder(cid)):
                    entries[cid] = e["reason"]

    for cid in out["population"]:
        if cid not in defined:
            continue
        if cid in tested and cid in entries:
            finder(cid)("B-COVER", f"has tests ({', '.join(tested[cid])}) and an index entry: it is one or the other")
        elif cid not in tested and cid not in entries:
            out["uncovered"].append(cid)
            finder(cid)("B-COVER", "no test and no entry in index.yaml")
    out["tested"] = sorted(tested, key=order)
    out["not_verifiable"] = {c: f"NOT_VERIFIABLE — {r}" for c, r in sorted(entries.items(), key=lambda x: order(x[0]))}
    out["holders"] = {c: defined[c][0] for c in out["uncovered"]}
    out["hashes"] = {c: criteria.pin_entry(text03, c)["sha256"] for c in out["uncovered"]}

    cs.green_fixtures(ctx, context_dir, out, finder)
    return out


def exit_code(out: dict) -> int:
    if out["cannot"] or any(f["check"] in HARD for f in out["findings"]):
        return 2
    return 1 if out["findings"] else 0


def to_text(out: dict) -> str:
    lines = [f"CANNOT TELL\t{c}" for c in out["cannot"]]
    lines += [f"{f['check']}\t{f['uc']}\t{f['detail']}" for f in out["findings"]]
    for name, cls in sorted(out["tests"].items()):
        lines += [f"{name}\t{c}\t{verdict}" for c, verdict in cls.items()]
    lines += [f"{c}\t{verdict}" for c, verdict in out["not_verifiable"].items()]
    lines.append(f"population {len(out['population'])} (from the level-2 catalogue): "
                 f"{len(out.get('tested', []))} with a test, "
                 f"{len(out['not_verifiable'])} NOT_VERIFIABLE in index.yaml, {len(out['uncovered'])} uncovered; "
                 f"{len(out['findings'])} findings")
    lines.append("A green run says the tests are well formed, rest on green fixtures, cover the population and match "
                 "the criteria as they are now; no Player has run them (NOT_VERIFIABLE — no executor).")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    opts = {"--source": "spec-source", "--context": "context"}
    args = list(argv)
    mode, cid, as_json = "check", None, False
    if args and args[0] == "uncovered":
        mode, args = "uncovered", args[1:]
    elif args and args[0] == "criterion":
        if len(args) < 2 or not CID.match(args[1]):
            sys.stderr.write(f"criterion needs an R<n>.<m>\n{USAGE}\n")
            return 64
        mode, cid, args = "criterion", args[1], args[2:]
    while args:
        a = args.pop(0)
        if a in opts and not (mode == "criterion" and a == "--source"):
            if not args:
                sys.stderr.write(f"{a} needs a value\n{USAGE}\n")
                return 64
            opts[a] = args.pop(0)
        elif a == "--json" and mode == "check":
            as_json = True
        else:
            sys.stderr.write(f"unknown argument {a}\n{USAGE}\n")
            return 64
    source, context_dir = Path(opts["--source"]), Path(opts["--context"])
    if mode == "criterion":
        if not (context_dir / "03-requirements.md").is_file():
            sys.stderr.write(f"{context_dir}/03-requirements.md not found\n{USAGE}\n")
            return 64
        cs.ensure_deps(os.path.abspath(__file__), argv)
        from conformance.spec import criteria
        text = criteria.read(context_dir)
        if cid not in criteria.criteria(text):
            sys.stderr.write(f"{cid} is not a criterion of context/03\n")
            return 1
        e = criteria.pin_entry(text, cid)
        print(f"criterion_sha256: {e['sha256']}\n{e['text']}")
        return 0
    for d in (source, context_dir):
        if not d.is_dir():
            sys.stderr.write(f"directory not found: {d}\n{USAGE}\n")
            return 64
    cs.ensure_deps(os.path.abspath(__file__), argv)
    out = run(source, context_dir)
    out["exit"] = exit_code(out)
    if mode == "uncovered":
        for c in out["cannot"]:
            sys.stderr.write(f"CANNOT TELL\t{c}\n")
        for c in out["uncovered"]:
            print(f"{c}\t{out['holders'][c]}\t{out['hashes'][c]}")
        return 2 if out["cannot"] else (1 if out["uncovered"] else 0)
    print(json.dumps(out, indent=2, ensure_ascii=False) if as_json else to_text(out))
    return out["exit"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
