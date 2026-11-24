#!/usr/bin/env python3
"""Conformance tests of the SGAI specification: verdicts computed by code.

    check-dash-conformance.py SPEC.md [--xsd FILE] [--context DIR]
                              [--out-md FILE] [--out-json FILE] [--players] [--dashif] [--demo]
    check-dash-conformance.py --source DIR [--context DIR] [--out-md FILE] [--out-json FILE]
    check-dash-conformance.py --behaviour [--source DIR] [--only ID ...] [--class C ...]
                              [--vector FILE ...] [--concurrency N]
                              [--out-json FILE] [--save-raw FILE] [--replay FILE]

Level 1: the extension schema and the example documents against ISO/IEC
23009-1:2026 (E-1..E-4, the identity of the XSD file with the spec's block,
and the base-standard rules the schema cannot express). Level 2: the document
criteria of context/03. --players adds level 3a (legacy Players). --dashif
adds the DASH-IF conformance tool as a second auditor: it informs, never
changes the exit (its XSD module is the 5th edition's; bin/dashif/). --demo
runs the committed positive and negative cases side by side.

--source DIR (spec-source/) runs levels 1 and 2 over the source instead of a
document (ADR 0063): each example file of DIR/examples/ by the class
DIR/examples/index.yaml declares, with DIR/syntax/sgai-extension.xsd. A
`legacy-view` fixture is judged by level 1 only (level 2 NOT_APPLICABLE, with
the reason). It adds FIX-1 and FIX-2 (the index, and the declared class
against the deduced one), C06-1a/b (@earliestResolutionTimeOffset and
@executeOnce keep the type and default of ISO's AlternativeMPDEventType) and
DASH-REF (every `DASH §n` of the prose is a clause of the primary copy; the
clause index is built at run time from the copy located as
bin/check-normative-base.py locates it, and nothing of it is stored; without
the copy the rule is NOT_VERIFIABLE). Its green says nothing about the prose
beyond those references. --players, --dashif, --demo and --xsd do not apply.

--behaviour (phase 11; ADR 0081, ADR 0087) runs the behaviour battery: the
reference Player (pinned dash.js 5.3.0 + reference-player/src/, adapter
`sgai` of bin/players/) in headless Chromium, on the behaviour tests of
DIR/behaviour/R*.yaml and the UC vectors of DIR/scenarios/UC-*.yaml (DIR
defaults to spec-source). It is opt-in: nothing else in the project runs it,
and it takes none of the other modes' options. --only UC-NN or R<n>.<m>
(every test of that criterion), repeatable or comma-separated; --class D1..D5
or legacy (legacy: the same dash.js without the module); --vector FILE runs a
vector file as it is (a copy, a draft); --concurrency N jobs at once (default
2, or SGAI_BEHAVIOUR_CONCURRENCY). --save-raw FILE keeps what the browser
recorded; --replay FILE compares a kept record again without a browser. The
criteria of DIR/behaviour/index.yaml are listed NOT_VERIFIABLE with their
reason. One job is a vector x variant x class; it yields a verdict per
expected field (requests, selection, presentation, audio, beacons, geometry):
PASS, FAIL with the field and what was observed against what was expected,
or NOT_VERIFIABLE with the reason. bin/conformance/behaviour_compare.py says
what each field compares; behaviour.py how a run is served.

Its green says: on every job run, what the page showed (read from the DOM
by the observation contract of reference-player/src/sgai-reference.js), the
document requests and the beacons on the network matched the vector within
its tolerance. It does NOT say anything about what is heard (`audio` is
NOT_VERIFIABLE), about media requests (not recorded), about occlusion (a
covered surface the module leaves visible counts as shown), about real
devices (a class is a profile, ADR 0080), nor about a vector being right: that
is check-behaviour.py's and check-scenarios.py's. Exit 2 when a job could not
run (prerequisites, harness error, unservable media, unreadable vector).

--xsd defaults to the file beside SPEC.md: v<N>-sgai-extension.xsd for
v<N>-sgai-spec.md, sgai-extension.xsd for sgai-spec.md.

Exit codes:
  0   nothing fails
  1   at least one FAIL
  2   cannot tell: ISO's pinned schema unavailable or not matching its hash,
      no single extension schema block, or a level-2 rule no longer matches
      context/03. Uncertainty wins over both others.
  64  wrong command line

A green run says every rule that could be decided by code passed on the
instances the specification contains. It does NOT say anything about what is
NOT_VERIFIABLE (listed with its reason), nor about constructs the
specification has no example of (listed as coverage findings).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from conformance.deps import ensure_lxml  # noqa: E402

USAGE = __doc__.split("\n\n")[1]


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 64
    if "--behaviour" in argv:
        from conformance.deps import ensure_yaml
        ensure_yaml(os.path.abspath(__file__), argv)
        from pathlib import Path
        from conformance import behaviour
        rest = [a for a in argv if a != "--behaviour"]
        return behaviour.main(rest, Path(HERE).parent / "spec-source")
    ensure_lxml(os.path.abspath(__file__), argv)
    from pathlib import Path
    from conformance import runner
    from conformance.model import Report

    args = list(argv)
    opts = {"--xsd": None, "--context": None, "--out-md": None, "--out-json": None, "--source": None}
    flags = set()
    spec = None
    while args:
        a = args.pop(0)
        if a in opts:
            if not args:
                sys.stderr.write(f"{a} needs a value\n{USAGE}\n")
                return 64
            opts[a] = args.pop(0)
        elif a in ("--players", "--demo", "--dashif"):
            flags.add(a)
        elif a.startswith("-"):
            sys.stderr.write(f"unknown option {a}\n{USAGE}\n")
            return 64
        elif spec is None:
            spec = Path(a)
        else:
            sys.stderr.write(f"unexpected argument {a}\n{USAGE}\n")
            return 64
    if opts["--source"] is not None:
        if spec is not None or flags or opts["--xsd"]:
            sys.stderr.write(f"--source takes no SPEC.md, --xsd, --players, --dashif or --demo\n{USAGE}\n")
            return 64
        source = Path(opts["--source"])
        if not source.is_dir():
            sys.stderr.write(f"source directory not found: {source}\n{USAGE}\n")
            return 64
        context_dir = Path(opts["--context"]) if opts["--context"] else Path(HERE).parent / "context"
        return source_mode(source, context_dir, opts)
    if "--demo" in flags and spec is None:
        spec = Path(HERE).parent / "dist" / "sgai-spec.md"
    if spec is None or not spec.exists():
        sys.stderr.write(f"specification not found: {spec}\n{USAGE}\n")
        return 64
    xsd = Path(opts["--xsd"]) if opts["--xsd"] else default_xsd(spec)
    context_dir = Path(opts["--context"]) if opts["--context"] else Path(HERE).parent / "context"

    if "--demo" in flags:
        from conformance import demo
        return demo.main(spec, context_dir)

    report = Report()
    ctx = runner.load(spec, context_dir, report)
    if ctx is not None and ctx.ext_text:
        report.add(runner.level1(ctx, xsd))
        report.add(runner.level2(ctx, report))
        if "--players" in flags:
            from conformance import players
            report.add(players.run(ctx, report))
    md = runner.to_markdown(report, spec, "Conformance tests")
    second = None
    if "--dashif" in flags and ctx is not None:
        from conformance import dashif
        second = dashif.run(ctx.blocks, ctx.isodir)
        md += dashif_section(second)
    if opts["--out-md"]:
        Path(opts["--out-md"]).write_text(md, encoding="utf-8")
    if opts["--out-json"]:
        js = runner.to_json(report, spec)
        if second is not None:
            import json
            d = json.loads(js)
            d["second_auditor_dashif"] = {k: v for k, v in second.items() if k != "baseline"} | {
                "baseline_summary": {k: v for k, v in second.get("baseline", {}).items() if k != "per_example"}}
            js = json.dumps(d, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
        Path(opts["--out-json"]).write_text(js, encoding="utf-8")
    c = report.counts()
    print(f"exit {report.exit_code()}: PASS {c['PASS']}  FAIL {c['FAIL']}  "
          f"NOT_VERIFIABLE {c['NOT_VERIFIABLE']}  NOT_APPLICABLE {c['NOT_APPLICABLE']}")
    for x in report.cannot:
        print(f"cannot tell: {x}")
    if not opts["--out-md"]:
        print(md)
    return report.exit_code()


def source_mode(source, context_dir, opts):
    from pathlib import Path
    from conformance import runner, source as src
    report, _ = src.run(source, context_dir)
    md = runner.to_markdown(report, source, "Conformance tests (source)", src.RULES)
    if opts["--out-md"]:
        Path(opts["--out-md"]).write_text(md, encoding="utf-8")
    if opts["--out-json"]:
        Path(opts["--out-json"]).write_text(runner.to_json(report, source, src.RULES), encoding="utf-8")
    c = report.counts()
    print(f"exit {report.exit_code()}: PASS {c['PASS']}  FAIL {c['FAIL']}  "
          f"NOT_VERIFIABLE {c['NOT_VERIFIABLE']}  NOT_APPLICABLE {c['NOT_APPLICABLE']}")
    for x in report.cannot:
        print(f"cannot tell: {x}")
    if not opts["--out-md"]:
        print(md)
    return report.exit_code()


def dashif_section(r):
    L = ["", "## Second auditor: DASH-IF conformance tool (informs, does not change the exit)", ""]
    if not r.get("ran"):
        return "\n".join(L + [f"Not run: {r.get('reason')}", ""])
    s = r["summary"]
    L += [f"Tool {r.get('tool', {}).get('tag', '')}; its XSD verdict is discarded (5th edition); what it also "
          "flags on ISO's own 6th-edition examples is its baseline and is subtracted.", "",
          f"- documents: {s['documents']}; with findings of their own: {s['with_ours']}; "
          f"with baseline findings only: {s['with_baseline_only']}; rejected by its 5th-edition XSD "
          f"(discarded): {s['xsd5_rejected']}"]
    for key in s.get("ours_keys", []):
        L.append(f"- finding of our own: `{key}`")
    return "\n".join(L) + "\n"


def default_xsd(spec):
    name = spec.name
    if name.endswith("-sgai-spec.md"):
        return spec.with_name(name[: -len("-sgai-spec.md")] + "-sgai-extension.xsd")
    if name == "sgai-spec.md":
        return spec.with_name("sgai-extension.xsd")
    return spec.with_suffix(".xsd")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
