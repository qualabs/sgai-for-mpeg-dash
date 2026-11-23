"""Levels 1 and 2 over spec-source/, fixture by fixture, by declared class
(ADR 0063).

The examples are the files of spec-source/examples/, each with the class
spec-source/examples/index.yaml declares; the extension schema is
spec-source/syntax/sgai-extension.xsd. The same rule catalogues as the
document mode run on them, with three differences:

  * a fixture's class is the declared one. The class extract.py deduces from
    the document is kept as a check (FIX-2): they must agree, a `legacy-view`
    being deduced as an MPD;
  * a `legacy-view` (an MPD as a Player that predates this specification sees
    it) is judged against the base standard (level 1) and not against
    context/03: every level-2 rule is NOT_APPLICABLE on it, with the reason;
  * rules that only the source can answer are added: FIX-1 and FIX-2 (the
    index), C06-1a and C06-1b (reused base attributes keep the base's type and
    default), DASH-REF (every `DASH §n` of the prose names a clause of the
    primary copy).

There is no rule making `Event@id` unique within one `svta:Tracking`: context/03
R6.5 has beacons sharing an `@id` within a candidate fire once, so a repeated
`@id` is allowed there (tasks/T-04 of phase 10 has the search).

XSD-ID asks, in this mode, whether the prose assembles this very file as its
one schema block: exactly one `{{xsd}}` directive and no inline schema.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from . import clauses, ext, extract, iso, runner
from . import spec as spec_catalog
from .context import Ctx
from .model import Outcome, Report, Result, Rule

PROSE = "sgai-spec.src.md"
INDEX = "examples/index.yaml"
SYNTAX = "syntax/sgai-extension.xsd"
EXAMPLE = re.compile(r"^\{\{example:(.+)\}\}$", re.M)
XSD_DIRECTIVE = re.compile(r"^\{\{xsd\}\}$", re.M)
DIRECTIVE_ONLY = re.compile(r"^\{\{(example:[^}]+|xsd)\}\}\n$")   # a fence holding only a directive

# declared class -> the class extract.py deduces (and the one the rules read)
CLASSES = {
    "publisher-mpd": "mpd",
    "legacy-view": "mpd",
    "list-mpd": "list-mpd",
    "sps-mpd": "sps-mpd",
    "overlay-list": "overlay-list",
    "request": "request",
    "fragment": "fragment",
    "vast": "vast",
}
LEGACY = "legacy-view"
LEGACY_NA = ("legacy-view: an MPD as a Player that predates this specification sees it, after removal of the "
             "extension namespace (DASH §5.2.1); it is no document a party of this specification writes, so the "
             "criteria of context/03 do not bind it. Level 1 judges it against the base standard (ADR 0063)")
ADR = "ADR 0063"
# the project root, where bin/check-normative-base.py looks for .env.agent and context/00
ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------- fixtures

@dataclass
class FixtureBlock(extract.Block):
    name: str = ""          # path relative to spec-source/examples/
    declared: str = ""

    @property
    def ref(self) -> str:
        return self.name


@dataclass
class FixtureRequest(extract.Request):
    name: str = ""
    declared: str = "request"

    @property
    def ref(self) -> str:
        return f"{self.name} (line {self.line})"


class IndexError_(Exception):
    """The index cannot be read: nothing can be judged by class (exit 2)."""


def read_index(path: Path) -> dict:
    """{fixture path: class} from the restricted YAML of index.yaml:

        fixtures:
          <path>: <class>

    Comments on their own line and blank lines are ignored; anything else is
    an error, so a shape this parser does not know is never half-read."""
    if not path.is_file():
        raise IndexError_(f"{path} does not exist")
    out, inside = {}, False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if not inside:
            if line.rstrip() == "fixtures:":
                inside = True
                continue
            raise IndexError_(f"{path.name}:{n}: expected `fixtures:`, found {s!r}")
        m = re.match(r"^  (\S+):\s+(\S+)\s*$", line)
        if not m:
            raise IndexError_(f"{path.name}:{n}: expected `  <path>: <class>`, found {line!r}")
        if m.group(1) in out:
            raise IndexError_(f"{path.name}:{n}: {m.group(1)} declared twice")
        out[m.group(1)] = m.group(2)
    if not inside:
        raise IndexError_(f"{path.name}: no `fixtures:` mapping")
    return out


def deduced(path: Path) -> tuple[str, list, object]:
    """(deduced class, requests, block) of one fixture file."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".http":
        rs = extract.requests("```\n" + text.rstrip("\n") + "\n```\n")
        return ("request" if rs else "no request"), rs, None
    b = extract.Block(index=1, line=1, text=text)
    extract.classify(b)
    return b.kind, [], b


# ---------------------------------------------------------------- rules owned by this mode

FIX1 = Rule("FIX-1", 1, ADR,
            "Each example is a file in `spec-source/examples/` with a declared class (`publisher-mpd`, `list-mpd`, "
            "`sps-mpd`, `overlay-list`, `request`, `fragment`, `legacy-view`, `vast`).",
            ("spec",), notes="every file under examples/ has one entry of a known class, every entry names a file, "
                             "and the prose holds no example that is not a fixture")
FIX2 = Rule("FIX-2", 1, ADR, "The deduced class is kept as a check against the declared one.",
            ("spec",), notes="a legacy-view is deduced as an MPD")
REUSE_QUOTE = ("When this spec needs to express a component that is in essence the same as one already defined in "
               "MPEG-DASH 6th edition (or its profile annexes), the spec MUST reuse the existing baseline construct "
               "with all its characteristics — name, default values, permitted value domain, units, semantics.")
C06_1A = Rule("C06-1a", 1, "context/06 \"Naming consistency with baseline DASH\", against ISO/IEC 23009-1:2026 "
              "Annex B AlternativeMPDEventType (§5.16.5.2)", REUSE_QUOTE, ("spec",),
              notes="every declaration of @earliestResolutionTimeOffset in the extension schema has the type and "
                    "the default (or its absence) of ISO's declaration")
C06_1B = Rule("C06-1b", 1, C06_1A.source, REUSE_QUOTE, ("spec",),
              notes="every declaration of @executeOnce in the extension schema has the type and the default of "
                    "ISO's declaration")
DASH_REF = Rule("DASH-REF", 1, "spec-source/sgai-spec.src.md, \"References\"; context/00-normative-base.md",
                "`DASH §n`, `DASH Annex X` and `Table n` refer to the base specification (ISO/IEC 23009-1:2026)",
                ("spec",), notes="every `DASH §n` / `DASH §n.m` of the prose names a clause heading of the primary "
                                 "copy; the index is built at run time and nothing of the copy is stored")
RULES = (FIX1, FIX2, C06_1A, C06_1B, DASH_REF)

XS = "{%s}" % extract.XSD_NS


def _qname(el, value: str | None) -> str | None:
    if value is None:
        return None
    prefix, _, local = value.rpartition(":")
    ns = el.nsmap.get(prefix or None)
    return f"{{{ns}}}{local}" if ns else value


def _decls(root, name: str) -> list:
    return [a for a in root.iter(XS + "attribute") if a.get("name") == name]


def reuse_check(rule: Rule, attr: str, ext_text: str, isodir: Path) -> list[Result]:
    iso_root = etree.parse(str(isodir / "DASH-MPD.xsd")).getroot()
    base_t = next((t for t in iso_root.iter(XS + "complexType") if t.get("name") == "AlternativeMPDEventType"), None)
    base = next((a for a in _decls(base_t, attr)), None) if base_t is not None else None
    if base is None:
        return [rule.result(Outcome.NOT_VERIFIABLE, "extension XSD",
                            detail=f"ISO's AlternativeMPDEventType declares no @{attr}")]
    want = (_qname(base, base.get("type")), base.get("default"))
    try:
        root = etree.XML(ext_text.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        return [rule.result(Outcome.FAIL, "extension XSD", detail=f"not well-formed: {e}")]
    decls = _decls(root, attr)
    if not decls:
        return [rule.result(Outcome.NOT_APPLICABLE, "extension XSD", detail=f"the extension schema declares no @{attr}")]
    out = []
    for a in decls:
        got = (_qname(a, a.get("type")), a.get("default"))
        where = ext.readable_path(a)
        if got == want:
            out.append(rule.result(Outcome.PASS, "extension XSD", where,
                                   f"@{attr}: type {a.get('type')}, default {a.get('default')!r}, as ISO's"))
        else:
            out.append(rule.result(Outcome.FAIL, "extension XSD", where,
                                   f"@{attr}: type {a.get('type')}, default {a.get('default')!r}; ISO's "
                                   f"AlternativeMPDEventType has type {base.get('type')}, default {base.get('default')!r}"))
    return out


DASH_CITE = re.compile(r"DASH §(\d+(?:\.\d+)*)")


def dash_refs(text: str) -> list[tuple[int, str]]:
    return [(text.count("\n", 0, m.start()) + 1, m.group(1)) for m in DASH_CITE.finditer(text)]


def dash_ref_check(prose: str, root: Path, idx: set | None = None, label: str = PROSE) -> list[Result]:
    refs = dash_refs(prose)
    if not refs:
        return [DASH_REF.result(Outcome.NOT_APPLICABLE, "specification", detail="the prose cites no `DASH §n`")]
    if idx is None:
        try:
            idx = clauses.index(root)
        except clauses.Unavailable as e:
            return [DASH_REF.result(Outcome.NOT_VERIFIABLE, "specification",
                                    detail=f"cannot build the clause index of the primary copy: {e}")]
    bad = [DASH_REF.result(Outcome.FAIL, "specification", f"{label}:{line}",
                           f"DASH §{n}: no clause {n} in the primary copy")
           for line, n in refs if n not in idx]
    if bad:
        return bad
    return [DASH_REF.result(Outcome.PASS, "specification",
                            detail=f"{len(refs)} references to {len({n for _, n in refs})} clauses, every one a "
                                   f"heading of the primary copy ({len(idx)} clauses indexed)")]


# ---------------------------------------------------------------- the run

def load(source: Path, context_dir: Path | None, report: Report):
    """(ctx, results of the index checks). ctx is None when the run cannot tell."""
    prose_p = source / PROSE
    if not prose_p.is_file():
        report.cannot.append(f"{prose_p} does not exist")
        return None, []
    prose = prose_p.read_text(encoding="utf-8")
    try:
        declared = read_index(source / INDEX)
    except IndexError_ as e:
        report.cannot.append(f"the fixture index cannot be read: {e}")
        return None, []
    syntax = source / SYNTAX
    if not syntax.is_file():
        report.cannot.append(f"{syntax} does not exist: no extension schema to judge with")
        return None, []
    try:
        isodir = iso.materialise()
    except iso.Unavailable as e:
        report.cannot.append(str(e))
        return None, []

    exdir = source / "examples"
    on_disk = sorted(str(p.relative_to(exdir)) for p in exdir.rglob("*")
                     if p.is_file() and p.name != "index.yaml")
    fix1, fix2 = [], []
    for name in on_disk:
        if name not in declared:
            fix1.append(FIX1.result(Outcome.FAIL, name, detail="the file has no entry in examples/index.yaml"))
        elif declared[name] not in CLASSES:
            fix1.append(FIX1.result(Outcome.FAIL, name, detail=f"unknown class {declared[name]!r}; "
                                    f"the classes are {', '.join(CLASSES)}"))
    for name in declared:
        if name not in on_disk:
            fix1.append(FIX1.result(Outcome.FAIL, name, detail="index entry names a file that does not exist"))
    inline = [b for b in extract.blocks(prose) if not DIRECTIVE_ONLY.match(b.text)]
    for b in inline:
        fix1.append(FIX1.result(Outcome.FAIL, f"{PROSE}:{b.line}",
                                detail=f"an xml block written in the prose ({b.kind}), not a fixture"))
    for r in extract.requests(prose):
        fix1.append(FIX1.result(Outcome.FAIL, f"{PROSE}:{r.line}", detail="a request written in the prose, not a fixture"))

    blocks, requests, n = [], [], 0
    for name in on_disk:
        cls = declared.get(name)
        if cls not in CLASSES:
            continue
        kind, rs, b = deduced(exdir / name)
        want = CLASSES[cls]
        if kind != want:
            fix2.append(FIX2.result(Outcome.FAIL, name, detail=f"declared {cls}, but the document reads as {kind}"))
        else:
            fix2.append(FIX2.result(Outcome.PASS, name, detail=f"declared {cls}, deduced {kind}"))
        if cls == "request":
            for r in rs:
                # the opening fence added by deduced() is line 1: the file's line is one less
                requests.append(FixtureRequest(r.line - 1, r.method, r.target, r.params, name=name))
            continue
        if b is None:
            continue
        n += 1
        # judged as declared (FIX-2 fails when that is not what the document is), unless it does not parse
        blocks.append(FixtureBlock(index=n, line=1, text=b.text, kind=kind if kind == "malformed" else want,
                                   root=b.root, error=b.error, name=name, declared=cls))
    if not fix1:
        fix1.append(FIX1.result(Outcome.PASS, "examples/index.yaml",
                                detail=f"{len(on_disk)} fixtures, each with one known class; no example in the prose"))

    ctx = Ctx(source, prose, blocks, requests, isodir, ext.iso_schema(isodir), context_dir=context_dir)
    ctx.ext_text = syntax.read_text(encoding="utf-8")
    ctx.combined, _ = ext.compile_extension(ctx.ext_text, isodir)
    return ctx, fix1 + fix2


def xsd_identity(ctx: Ctx) -> list[Result]:
    n = len(XSD_DIRECTIVE.findall(ctx.spec_text))
    inline = [b for b in extract.blocks(ctx.spec_text) if b.kind == "ext-xsd"]
    subject = str(Path(ctx.spec_path) / SYNTAX)
    if n == 1 and not inline:
        return [ext.XSD_ID.result(Outcome.PASS, subject,
                                  detail="the prose's one {{xsd}} directive assembles this file as the schema block")]
    return [ext.XSD_ID.result(Outcome.FAIL, subject,
                              detail=f"{n} {{{{xsd}}}} directives and {len(inline)} inline schema blocks; exactly one "
                                     "directive and no inline block are needed")]


def level1(ctx: Ctx) -> list[Result]:
    out = runner.level1(ctx, None)
    out += xsd_identity(ctx)
    out += reuse_check(C06_1A, "earliestResolutionTimeOffset", ctx.ext_text, ctx.isodir)
    out += reuse_check(C06_1B, "executeOnce", ctx.ext_text, ctx.isodir)
    out += dash_ref_check(ctx.spec_text, ROOT, ctx.extra.get("clause_index"))
    return out


def run_rule_by_class(ctx: Ctx, rule: Rule) -> list[Result]:
    """runner.run_rule, except that a legacy-view subject gets NOT_APPLICABLE."""
    subs = runner.subjects(ctx, rule)
    legacy = [s for s in subs if getattr(s, "declared", "") == LEGACY]
    if not legacy:
        return runner.run_rule(ctx, rule)
    out = [rule.result(Outcome.NOT_APPLICABLE, s.ref, detail=LEGACY_NA) for s in legacy]
    rest = [s for s in subs if getattr(s, "declared", "") != LEGACY]
    if not rest:
        return out
    if rule.check is None:
        return out + [rule.result(Outcome.NOT_VERIFIABLE, runner.ref(s), detail=rule.not_verifiable) for s in rest]
    for s in rest:
        try:
            out.extend(rule.check(ctx, s))
        except Exception as e:  # as runner.run_rule
            out.append(rule.result(Outcome.FAIL, runner.ref(s), detail=f"rule raised {type(e).__name__}: {e}"))
    return out


def level2(ctx: Ctx, report: Report) -> list[Result]:
    if ctx.context_dir is not None:
        report.cannot.extend(spec_catalog.stale(ctx.context_dir))
    out = []
    for rule in spec_catalog.RULES:
        out += run_rule_by_class(ctx, rule)
    return out


def run(source: Path, context_dir: Path | None, clause_index: set | None = None) -> tuple[Report, Ctx | None]:
    """clause_index, when given, is used instead of reading the primary copy (tests)."""
    report = Report()
    ctx, idx_results = load(source, context_dir, report)
    if ctx is None:
        return report, None
    if clause_index is not None:
        ctx.extra["clause_index"] = clause_index
    report.add(idx_results)
    report.add(level1(ctx))
    report.add(level2(ctx, report))
    return report, ctx


NEG = Path(__file__).parent / "fixtures" / "negative" / "source"


def negatives() -> list[Path]:
    """The negatives of this mode's rules: fixtures/negative/source/, same
    pair format as fixtures.py. A `.md` case is a piece of prose (DASH-REF);
    an `.xml` case is as in fixtures.py. They live in a subdirectory so that
    the document mode's --demo, which runs only its own rules, does not
    count them as missed."""
    return sorted(NEG.glob("*.expect.json"))


def evaluate(expect_path: Path, base: Ctx, clause_index: set | None = None) -> dict:
    import json
    from . import fixtures
    name = expect_path.name[: -len(".expect.json")]
    exp = json.loads(expect_path.read_text(encoding="utf-8"))
    md, xml = NEG / f"{name}.md", NEG / f"{name}.xml"
    if md.exists():
        results = dash_ref_check(md.read_text(encoding="utf-8"), ROOT, clause_index, md.name)
    else:
        ctx = fixtures.ctx_for(xml, base)
        results = runner.run_all(ctx)
        results += reuse_check(C06_1A, "earliestResolutionTimeOffset", ctx.ext_text, ctx.isodir)
        results += reuse_check(C06_1B, "executeOnce", ctx.ext_text, ctx.isodir)
    fails = [r for r in results if r.outcome is Outcome.FAIL]
    hit = [r for r in fails if r.rule == exp["rule"]
           and exp.get("xpath_contains", "") in (r.xpath + " " + r.subject + " " + r.detail)]
    return {"name": name, "expected": exp, "caught": bool(hit), "hit": hit, "results": results,
            "other_fails": sorted({r.rule for r in fails if r.rule != exp["rule"]})}
