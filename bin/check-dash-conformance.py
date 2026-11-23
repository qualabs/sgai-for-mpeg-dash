#!/usr/bin/env python3
"""Conformance tests of the SGAI specification: verdicts computed by code.

    check-dash-conformance.py SPEC.md [--xsd FILE] [--context DIR]
                              [--out-md FILE] [--out-json FILE] [--players] [--demo]

Level 1: the extension schema and the example documents against ISO/IEC
23009-1:2026 (E-1..E-4, the identity of the XSD file with the spec's block,
and the base-standard rules the schema cannot express). Level 2: the document
criteria of context/03. --players adds level 3a (legacy Players). --demo
runs the committed positive and negative cases side by side.

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
    ensure_lxml(os.path.abspath(__file__), argv)
    from pathlib import Path
    from conformance import runner
    from conformance.model import Report

    args = list(argv)
    opts = {"--xsd": None, "--context": None, "--out-md": None, "--out-json": None}
    flags = set()
    spec = None
    while args:
        a = args.pop(0)
        if a in opts:
            if not args:
                sys.stderr.write(f"{a} needs a value\n{USAGE}\n")
                return 64
            opts[a] = args.pop(0)
        elif a in ("--players", "--demo"):
            flags.add(a)
        elif a.startswith("-"):
            sys.stderr.write(f"unknown option {a}\n{USAGE}\n")
            return 64
        elif spec is None:
            spec = Path(a)
        else:
            sys.stderr.write(f"unexpected argument {a}\n{USAGE}\n")
            return 64
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
    if opts["--out-md"]:
        Path(opts["--out-md"]).write_text(md, encoding="utf-8")
    if opts["--out-json"]:
        Path(opts["--out-json"]).write_text(runner.to_json(report, spec), encoding="utf-8")
    c = report.counts()
    print(f"exit {report.exit_code()}: PASS {c['PASS']}  FAIL {c['FAIL']}  "
          f"NOT_VERIFIABLE {c['NOT_VERIFIABLE']}  NOT_APPLICABLE {c['NOT_APPLICABLE']}")
    for x in report.cannot:
        print(f"cannot tell: {x}")
    if not opts["--out-md"]:
        print(md)
    return report.exit_code()


def default_xsd(spec):
    name = spec.name
    if name.endswith("-sgai-spec.md"):
        return spec.with_name(name[: -len("-sgai-spec.md")] + "-sgai-extension.xsd")
    if name == "sgai-spec.md":
        return spec.with_name("sgai-extension.xsd")
    return spec.with_suffix(".xsd")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
