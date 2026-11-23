"""Runs levels 1 and 2 over a specification and builds the report."""
from __future__ import annotations

import json
from pathlib import Path

from lxml import etree

from . import ext, extract, iso
from . import dash as dash_catalog
from . import spec as spec_catalog
from .context import Ctx
from .model import Outcome, Report, Result, Rule

NO_INSTANCE = "no instance in the specification to test this on (coverage finding)"


def subjects(ctx: Ctx, rule: Rule) -> list:
    out = []
    for kind in rule.applies_to:
        if kind == "request":
            out.extend(ctx.requests)
        elif kind == "spec":
            out.append(None)
        else:
            out.extend(ctx.by_kind(kind))
    return out


def ref(subject) -> str:
    return "specification" if subject is None else subject.ref


def run_rule(ctx: Ctx, rule: Rule) -> list[Result]:
    subs = subjects(ctx, rule)
    if not subs:
        if rule.check is None:
            return [rule.result(Outcome.NOT_VERIFIABLE, "specification", detail=rule.not_verifiable)]
        return [rule.result(Outcome.NOT_VERIFIABLE, "specification", detail=NO_INSTANCE)]
    if rule.check is None:
        return [rule.result(Outcome.NOT_VERIFIABLE, ref(s), detail=rule.not_verifiable) for s in subs]
    out = []
    for s in subs:
        try:
            out.extend(rule.check(ctx, s))
        except Exception as e:  # a crashing rule is a defect of the rule, reported loudly
            out.append(rule.result(Outcome.FAIL, ref(s), detail=f"rule raised {type(e).__name__}: {e}"))
    return out


def load(spec_path: Path, context_dir: Path | None, report: Report) -> Ctx | None:
    text = spec_path.read_text(encoding="utf-8")
    blocks = extract.blocks(text)
    try:
        isodir = iso.materialise()
    except iso.Unavailable as e:
        report.cannot.append(str(e))
        return None
    ctx = Ctx(spec_path, text, blocks, extract.requests(text), isodir, ext.iso_schema(isodir),
              context_dir=context_dir)
    xs = extract.extension_schema(blocks)
    if len(xs) != 1:
        report.cannot.append(f"the specification has {len(xs)} extension schema blocks "
                             f"(targetNamespace {extract.SGAI_NS}); exactly one is needed")
        return ctx
    ctx.ext_text = xs[0].text
    ctx.combined, _ = ext.compile_extension(ctx.ext_text, isodir)
    return ctx


def level1(ctx: Ctx, xsd_file: Path | None) -> list[Result]:
    out = []
    out += ext.e1(ctx.ext_text, ctx.isodir)
    out += ext.e2(ctx.ext_text)
    if ctx.combined is not None:
        globals_ = ext.global_elements([ctx.ext_text, (ctx.isodir / "DASH-MPD.xsd").read_text()])
        out += ext.e3(ctx.blocks, ctx.combined, globals_)
    out += ext.e4(ctx.blocks, ctx.iso)
    if xsd_file is not None:
        out += ext.identity(xsd_file, extract.extension_schema(ctx.blocks)[0])
    for rule in dash_catalog.RULES:
        out += run_rule(ctx, rule)
    return out


def level2(ctx: Ctx, report: Report) -> list[Result]:
    if ctx.context_dir is not None:
        report.cannot.extend(spec_catalog.stale(ctx.context_dir))
    out = []
    for rule in spec_catalog.RULES:
        out += run_rule(ctx, rule)
    return out


def all_rules() -> list[Rule]:
    from . import players   # rule definitions only; nothing is run on import
    return list(ext.RULES) + list(dash_catalog.RULES) + list(spec_catalog.RULES) + list(players.RULES)


def to_json(report: Report, spec_path: Path) -> str:
    rules = {r.id: {"level": r.level, "source": r.source, "quote": r.quote,
                    "criterion": r.criterion, "not_verifiable": r.not_verifiable}
             for r in all_rules()}
    return json.dumps({"spec": str(spec_path), "counts": report.counts(), "cannot": report.cannot,
                       "exit": report.exit_code(), "rules": rules,
                       "results": [r.as_dict() for r in report.results]},
                      indent=1, ensure_ascii=False, sort_keys=True) + "\n"


def to_markdown(report: Report, spec_path: Path, title: str) -> str:
    rules = {r.id: r for r in all_rules()}
    c = report.counts()
    L = [f"# {title}", "",
         f"Specification: `{spec_path}`. Every verdict below was computed by code "
         "(XSD validation and rules as code); none is an LLM's judgement.", "",
         f"**Exit {report.exit_code()}** — PASS {c['PASS']}, FAIL {c['FAIL']}, "
         f"NOT_VERIFIABLE {c['NOT_VERIFIABLE']}, NOT_APPLICABLE {c['NOT_APPLICABLE']}.", ""]
    if report.cannot:
        L += ["## Cannot tell", ""] + [f"- {x}" for x in report.cannot] + [""]
    by_rule: dict = {}
    for r in report.results:
        by_rule.setdefault(r.rule, []).append(r)
    fails = [r for r in report.results if r.outcome is Outcome.FAIL]
    L += ["## FAIL", ""]
    if not fails:
        L += ["None.", ""]
    for r in fails:
        rule = rules.get(r.rule)
        L += [f"- **{r.rule}** on {r.subject}" + (f", `{r.xpath}`" if r.xpath else "") + f": {r.detail}"]
        if rule:
            L += [f"  - {rule.source}: *\"{rule.quote}\"*"]
    L += ["", "## Per rule", "", "| rule | level | source | PASS | FAIL | NOT_VERIFIABLE | NOT_APPLICABLE |",
          "|---|---|---|---|---|---|---|"]
    for rid in sorted(by_rule, key=_order):
        rs = by_rule[rid]
        rule = rules.get(rid)
        n = {o: sum(1 for x in rs if x.outcome is o) for o in Outcome}
        L.append(f"| {rid} | {rule.level if rule else ''} | {rule.source if rule else ''} | "
                 f"{n[Outcome.PASS]} | {n[Outcome.FAIL]} | {n[Outcome.NOT_VERIFIABLE]} | {n[Outcome.NOT_APPLICABLE]} |")
    nv = {}
    for r in report.results:
        if r.outcome is Outcome.NOT_VERIFIABLE:
            nv.setdefault((r.rule, r.detail), []).append(r.subject)
    L += ["", "## NOT_VERIFIABLE, and why", ""]
    for (rid, why), subs in sorted(nv.items(), key=lambda kv: _order(kv[0][0])):
        L.append(f"- **{rid}** ({len(subs)}): {why}")
    return "\n".join(L) + "\n"


def _order(rid: str):
    import re
    parts = re.split(r"(\d+)", rid)
    return [int(p) if p.isdigit() else p for p in parts]


def run_all(ctx: Ctx) -> list[Result]:
    """Every level-1 and level-2 rule over ctx, without the file identity check
    and without the staleness check (used by the negative cases)."""
    out = level1(ctx, None)
    for rule in spec_catalog.RULES:
        out += run_rule(ctx, rule)
    return out
