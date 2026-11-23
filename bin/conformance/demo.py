"""--demo: the positives and the negatives side by side (ADR 0056).

Positives must give no FAIL: ISO's own 6th-edition examples (a reference that
does not come from us) under level 1, and the published specification under
levels 1 and 2. Negatives must FAIL, at the rule written beside each one.
The output carries no timing and no absolute path, so two runs are identical.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

from . import ext, extract, fixtures, iso, runner
from .context import Ctx
from .model import Outcome, Report

W = 100


def _wrap(label: str, text: str) -> list[str]:
    pad = " " * 14
    lines = textwrap.wrap(text, W - len(pad)) or [""]
    return [f"    {label:<10}{lines[0]}"] + [pad + x for x in lines[1:]]


def _count(results) -> dict:
    c = {o: 0 for o in Outcome}
    for r in results:
        c[r.outcome] += 1
    return c


def _line(name: str, results) -> tuple[str, int]:
    c = _count(results)
    fails = c[Outcome.FAIL]
    mark = "clean" if fails == 0 else "FAIL "
    return (f"  [{mark}] {name:<52} PASS {c[Outcome.PASS]:>4}  FAIL {fails:>3}  "
            f"NOT_VERIFIABLE {c[Outcome.NOT_VERIFIABLE]:>3}  NOT_APPLICABLE {c[Outcome.NOT_APPLICABLE]:>3}", fails)


def main(spec: Path, context_dir: Path) -> int:
    report = Report()
    ctx = runner.load(spec, context_dir, report)
    if ctx is None or not ctx.ext_text:
        print("cannot tell: " + "; ".join(report.cannot))
        return 2
    rules = {r.id: r for r in runner.all_rules()}
    out = ["SGAI conformance tests: demo", "Every verdict below is computed by code. None is an LLM's judgement.", ""]

    # positives
    out.append("POSITIVES: must give no FAIL")
    blocks = []
    for i, p in enumerate(iso.examples(ctx.isodir), 1):
        b = extract.Block(i, 1, p.read_text(encoding="utf-8"))
        extract.classify(b)
        b.index, b.line = i, 1
        blocks.append(b)
    iso_ctx = Ctx(Path("ISO examples"), "", blocks, [], ctx.isodir, ctx.iso, ctx.combined, ctx.ext_text, context_dir)
    iso_results = runner.level1(iso_ctx, None)
    iso_results = [r for r in iso_results if r.rule not in ("E-1", "E-2")]
    l1, f1 = _line(f"ISO/IEC 23009-1:2026 examples ({len(blocks)}), level 1", iso_results)
    spec_results = runner.level1(ctx, None) + [r for rule in __import__("conformance.spec", fromlist=["RULES"]).RULES
                                               for r in runner.run_rule(ctx, rule)]
    l2, f2 = _line(f"{spec.name} ({len(ctx.blocks)} blocks, {len(ctx.requests)} requests), levels 1-2", spec_results)
    out += [l1, l2]
    for r in [x for x in iso_results + spec_results if x.outcome is Outcome.FAIL][:20]:
        out += _wrap("FAIL", f"{r.rule} on {r.subject} {r.xpath}: {r.detail}")
    out.append("")

    # negatives
    cases = fixtures.negatives()
    out.append(f"NEGATIVES: {len(cases)} documents broken on purpose; each must FAIL at its rule")
    caught = 0
    for p in cases:
        v = fixtures.evaluate(p, ctx, runner.run_all)
        exp = v["expected"]
        rule = rules.get(exp["rule"])
        caught += v["caught"]
        out.append("")
        out.append(f"  [{'CAUGHT' if v['caught'] else 'MISSED'}] {v['name']}")
        out += _wrap("broke", f"{exp['change']} (from {exp['derived_from']})")
        if rule:
            out += _wrap("rule", f"{rule.id}: {rule.source}")
            out += _wrap("quote", f"\"{rule.quote}\"")
        if v["hit"]:
            h = v["hit"][0]
            out += _wrap("where", h.xpath or h.subject)
            out += _wrap("says", h.detail)
        if v["other_fails"]:
            out += _wrap("also", "also failed: " + ", ".join(v["other_fails"]))
    out.append("")
    ok = f1 == 0 and f2 == 0 and caught == len(cases)
    out.append(f"RESULT: positives {'clean' if f1 == 0 and f2 == 0 else 'NOT clean'}; "
               f"negatives caught {caught}/{len(cases)}; exit {0 if ok else 1}")
    print("\n".join(out))
    return 0 if ok else 1
