"""Committed negative cases (ADR 0054).

Each negative is a pair in fixtures/negative/:
  <name>.xml            a document derived from one example of the spec (or of
                        its XSD) with ONE change, or <name>.request.txt holding a
                        `GET <target> HTTP/1.1` line for a request rule
  <name>.expect.json    {"rule": "<rule id>", "xpath_contains": "<substring of the
                        FAIL's xpath or subject, may be empty>",
                        "derived_from": "dist/sgai-spec.md xml#N (line L)",
                        "change": "<what was broken, one line>"}
A negative passes only if <rule> gives FAIL on it. Any other rule failing on
it is reported too: a negative should break one thing.
An .xml whose root is xs:schema is taken as the extension schema under test.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import ext, extract
from .context import Ctx
from .model import Outcome

NEG = Path(__file__).parent / "fixtures" / "negative"


def negatives() -> list[Path]:
    return sorted(NEG.glob("*.expect.json"))


def load_case(expect: Path):
    name = expect.name[: -len(".expect.json")]
    exp = json.loads(expect.read_text(encoding="utf-8"))
    xml, req = NEG / f"{name}.xml", NEG / f"{name}.request.txt"
    return name, exp, (xml if xml.exists() else req)


def ctx_for(case: Path, base: Ctx) -> Ctx:
    """A context whose only instance is the negative case. The extension schema
    is the published one, unless the case is itself a schema."""
    text = case.read_text(encoding="utf-8")
    if case.name.endswith(".request.txt"):
        md = "```\n" + text.rstrip("\n") + "\n```\n"
        return Ctx(case, md, [], extract.requests(md), base.isodir, base.iso, base.combined,
                   base.ext_text, base.context_dir)
    b = extract.Block(index=1, line=1, text=text)
    extract.classify(b)
    if b.kind in ("ext-xsd", "xsd"):
        combined, _ = ext.compile_extension(text, base.isodir)
        return Ctx(case, text, [b], [], base.isodir, base.iso, combined, text, base.context_dir)
    return Ctx(case, text, [b], [], base.isodir, base.iso, base.combined, base.ext_text, base.context_dir)


def evaluate(expect_path: Path, base: Ctx, run_all) -> dict:
    """run_all(ctx) -> list[Result] over every rule. Returns the verdict on the case."""
    name, exp, case = load_case(expect_path)
    ctx = ctx_for(case, base)
    results = run_all(ctx)
    fails = [r for r in results if r.outcome is Outcome.FAIL]
    hit = [r for r in fails if r.rule == exp["rule"]
           and exp.get("xpath_contains", "") in (r.xpath + " " + r.subject + " " + r.detail)]
    others = sorted({r.rule for r in fails if r.rule != exp["rule"]})
    return {"name": name, "expected": exp, "caught": bool(hit), "hit": hit, "other_fails": others}
