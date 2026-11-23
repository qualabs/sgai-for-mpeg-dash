#!/usr/bin/env python3
"""The validation's trace: which sections of the spec fulfil each obligation,
with quotations a script can check (ADR 0068).

Usage:
  bin/check-trace.py TRACE.json [--spec FILE] [--population FILE]
                     [--rules FILE] [--json] [--summary]
  bin/check-trace.py sources CONFORMANCE.json [--population FILE]
  bin/check-trace.py stale TRACE.json --old OLD.md --new NEW.md
  bin/check-trace.py batch TRACE.json UNIT [UNIT ...] [--spec FILE]

THE TRACE (`output-analysis/v<N>-trace.json`):

  {"format": "sgai-trace/1",
   "spec": "output/v<N>-sgai-spec.md",
   "units": {
     "<unit id>": {
       "kind": "criterion" | "prose" | "use-case",
       "source": "code" | "vector" | "vector-pending" | "llm",
       "rules": ["R12.1a", ...],     # source code: the level-1/2 rules that decide it
       "residual": ["R12.1b", ...],  # optional: rules of the unit code cannot decide;
                                     # that part is still judged by an LLM
       "vectors": ["..."],           # source vector: the UC vectors (T-05)
       "verdict": "met" | ...,       # optional: the validation's verdict
       "sections": [{"key": "5.1.3", "quotes": ["exact text", ...]}, ...]
     }, ...}}

  A section key is what bin/spec_sections.py computes (`5.1.3`, `A.5`,
  `Annex A`, or the heading text). No line numbers anywhere: they move on
  every edit, a key does not.

CHECK (the default command). Findings, each a line `<check>\\t<unit>\\t...`:

  T-POP      a unit of the population has no entry (missing), or an entry
             is not in the population (extra)
  T-SOURCE   source is not one of code / vector / vector-pending / llm;
             a `code` unit names no rule; a `vector` unit names no vector
  T-RULE     a rule named in `rules` or `residual` is not in the
             conformance catalogue at level 1 or 2; a `rules` entry has no
             code (it is NOT_VERIFIABLE by construction); a level-2 rule in
             `rules` belongs to another criterion
  T-SECTION  a section key does not exist in the spec
  T-QUOTE    a quotation is empty, or not literal inside its section

  "Literal" means: after normalising BOTH the quotation and the section
  text, the quotation is a substring of the section. The normalisation is
  exactly this and nothing else:
    1. `\\"` becomes `"`               (escaped quotes);
    2. every `*` and every backtick is deleted (markdown emphasis `*`, `**`
       and code spans);
    3. every run of whitespace, newlines included, becomes one space, and
       the ends are stripped.
  Not normalised: `_` emphasis, `/` written for a table's `|`, an ellipsis
  standing for elided text, quote styles (`"` vs `“`), case. Each of those
  is a quotation that is not literal.

  --spec defaults to the trace's `spec` field, relative to the project root;
  an assembled spec or spec-source/sgai-spec.src.md both work (a quotation
  of a directive's expansion is only found in the assembled one).
  --population FILE reads `<id><TAB><kind>` lines (the output of
  `check-promotable.py --population`, possibly at another commit) instead
  of computing today's.
  --rules FILE reads the catalogue from a conformance-tests.json (`rules`);
  without it the catalogue is bin/conformance's all_rules(), loaded only
  when the trace has a unit that names a rule.
  --json prints {"findings": [...], "summary": {...}}; --summary prints only
  the counts as JSON. Neither changes the exit code.

SOURCES: for every unit of the population, the verdict source the
conformance catalogue gives it, as JSON {unit: {kind, source, rules,
residual, verdict, reason}}:
  code            a level-2 rule with code (not NOT_VERIFIABLE) names the
                  unit as its criterion. `residual` lists the unit's other
                  level-2 rules, which code does not decide.
                  verdict: `contradicted` if any of its rules FAILs in
                  CONFORMANCE.json, `met` if none fails and one PASSes;
                  with neither (no instance to test) the unit falls back to
                  `llm` for this candidate, with the reason.
  vector-pending  a level-2 rule of the unit says "Player behaviour: level 3
                  (reference-player)" and none has code: there is no vector
                  yet (T-05). `rules` is empty; `residual` lists its other
                  NOT_VERIFIABLE rules, the part an LLM still judges.
  llm             everything else.

STALE: the units of TRACE whose sections changed between OLD and NEW
(text differs, or the key vanished), and the keys that changed, added or
removed — computed by splitting both documents, so an example fixture
changed through spec-source/ counts as well as a prose patch. JSON.

BATCH: what a walker reads for a batch of units, and nothing else: each
unit's text in context/ (a criterion's bullet; a prose unit's requirement
prose, with its modal marked; a use case's section of 04) followed by the
text of the sections the trace names for it, each section printed once.

What a green says: every unit of the population has a trace, every section
exists, every quotation is literal where it is placed, and every rule named
exists and decides. What it does NOT say: that a quotation fulfils the
criterion it is filed under, or that the verdict is right. A literal quote
of the wrong passage passes.

Exit codes: 0 no finding · 1 findings (listed) · 2 cannot tell (trace,
spec, population or catalogue unreadable; the spec cannot be split) ·
64 wrong command line.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
sys.path.insert(0, BIN)
import spec_sections  # noqa: E402

SOURCES = {"code", "vector", "vector-pending", "llm"}
PLAYER = "Player behaviour: level 3 (reference-player)"
REQUIREMENTS = os.path.join(ROOT, "context", "03-requirements.md")
USE_CASES = os.path.join(ROOT, "context", "04-use-cases.md")


class CannotTell(Exception):
    pass


class Usage(Exception):
    pass


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------- normalising

def normalise(text: str) -> str:
    text = text.replace('\\"', '"')
    text = re.sub(r"[*`]", "", text)
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------- the inputs

def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as e:
        raise CannotTell(f"cannot read {path}: {e}")


def population(path=None):
    """[(id, kind)] — from a file of `id<TAB>kind` lines, or today's."""
    if path is None:
        return _load("check_promotable", "check-promotable.py").population()
    try:
        with open(path, encoding="utf-8") as fh:
            rows = [ln.rstrip("\n").split("\t") for ln in fh if ln.strip()]
    except OSError as e:
        raise CannotTell(f"cannot read population {path}: {e}")
    if not rows or any(len(r) != 2 for r in rows):
        raise CannotTell(f"population {path} is not `id<TAB>kind` lines")
    return [tuple(r) for r in rows]


def catalogue(path=None):
    """{rule id: {level, criterion, not_verifiable}}."""
    if path is not None:
        data = read_json(path)
        if not isinstance(data, dict) or not isinstance(data.get("rules"), dict):
            raise CannotTell(f"{path} has no `rules` object")
        return data["rules"]
    from conformance.deps import ensure_lxml  # re-runs under uv when lxml is missing
    ensure_lxml(os.path.abspath(__file__), sys.argv[1:])
    from conformance.runner import all_rules
    return {r.id: {"level": r.level, "criterion": r.criterion,
                   "not_verifiable": r.not_verifiable} for r in all_rules()}


def spec_index(path):
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            secs = spec_sections.split(fh.read())
    except OSError as e:
        raise CannotTell(f"cannot read spec {path}: {e}")
    except spec_sections.SectionError as e:
        raise CannotTell(f"cannot split spec {path}: {e}")
    return spec_sections.by_key(secs)


# ------------------------------------------------------------------- checking

def check(trace, sections, pop, rules):
    """The findings: list of dicts {check, unit, detail[, section, quote]}.
    `sections` is {key: Section}; `rules` may be None when no unit names one."""
    out = []
    units = trace.get("units") if isinstance(trace, dict) else None
    if not isinstance(units, dict):
        raise CannotTell("the trace has no `units` object")
    ids = [u for u, _ in pop]
    for u in ids:
        if u not in units:
            out.append({"check": "T-POP", "unit": u, "detail": "missing: in the population, no trace"})
    known = set(ids)
    for u in units:
        if u not in known:
            out.append({"check": "T-POP", "unit": u, "detail": "extra: traced, not in the population"})
    norm_cache = {}
    for u, entry in units.items():
        if not isinstance(entry, dict):
            out.append({"check": "T-SOURCE", "unit": u, "detail": "entry is not an object"})
            continue
        src = entry.get("source")
        if src not in SOURCES:
            out.append({"check": "T-SOURCE", "unit": u, "detail": f"unknown source {src!r}"})
        if src == "code" and not entry.get("rules"):
            out.append({"check": "T-SOURCE", "unit": u, "detail": "source code names no rule"})
        if src == "vector" and not entry.get("vectors"):
            out.append({"check": "T-SOURCE", "unit": u, "detail": "source vector names no vector"})
        for field in ("rules", "residual"):
            for rid in entry.get(field) or []:
                r = rules.get(rid) if rules is not None else None
                if r is None or r.get("level") not in (1, 2):
                    out.append({"check": "T-RULE", "unit": u,
                                "detail": f"{field}: {rid} is not a level-1/2 rule of the catalogue"})
                    continue
                if field == "rules" and r.get("not_verifiable"):
                    out.append({"check": "T-RULE", "unit": u,
                                "detail": f"rules: {rid} has no code (NOT_VERIFIABLE)"})
                if field == "rules" and r.get("level") == 2 and r.get("criterion") != u:
                    out.append({"check": "T-RULE", "unit": u,
                                "detail": f"rules: {rid} belongs to {r.get('criterion')!r}"})
        for sec in entry.get("sections") or []:
            key = sec.get("key") if isinstance(sec, dict) else None
            if key not in sections:
                out.append({"check": "T-SECTION", "unit": u, "section": key,
                            "detail": f"no section {key!r} in the spec"})
                continue
            if key not in norm_cache:
                norm_cache[key] = normalise(sections[key].text)
            for q in sec.get("quotes") or []:
                nq = normalise(q) if isinstance(q, str) else ""
                if not nq:
                    out.append({"check": "T-QUOTE", "unit": u, "section": key, "quote": q,
                                "detail": "empty quotation"})
                elif nq not in norm_cache[key]:
                    out.append({"check": "T-QUOTE", "unit": u, "section": key, "quote": q,
                                "detail": "not literal in its section"})
    return out


def names_rules(trace):
    return any((e.get("rules") or e.get("residual"))
               for e in trace.get("units", {}).values() if isinstance(e, dict))


def summary(trace, findings):
    units = trace.get("units", {})
    s = {"units": len(units), "by_source": {}, "by_verdict": {}, "with_residual": 0,
         "section_refs": 0, "quotes": 0, "findings": {}}
    for e in units.values():
        if not isinstance(e, dict):
            continue
        s["by_source"][e.get("source")] = s["by_source"].get(e.get("source"), 0) + 1
        if e.get("verdict"):
            s["by_verdict"][e["verdict"]] = s["by_verdict"].get(e["verdict"], 0) + 1
        if e.get("residual"):
            s["with_residual"] += 1
        for sec in e.get("sections") or []:
            s["section_refs"] += 1
            s["quotes"] += len(sec.get("quotes") or []) if isinstance(sec, dict) else 0
    for f in findings:
        key = f["check"] if f["check"] != "T-POP" else "T-POP " + f["detail"].split(":")[0]
        s["findings"][key] = s["findings"].get(key, 0) + 1
    return s


# -------------------------------------------------------------------- sources

def sources(conformance, pop):
    rules = conformance.get("rules")
    results = conformance.get("results")
    if not isinstance(rules, dict) or not isinstance(results, list):
        raise CannotTell("conformance JSON needs `rules` and `results`")
    by_crit = {}
    for rid, r in rules.items():
        if r.get("level") == 2 and r.get("criterion"):
            by_crit.setdefault(r["criterion"], []).append(rid)
    outcomes = {}
    for res in results:
        outcomes.setdefault(res.get("rule"), []).append(res.get("outcome"))
    out = {}
    for u, kind in pop:
        rids = sorted(by_crit.get(u, []))
        code = [r for r in rids if not rules[r].get("not_verifiable")]
        player = [r for r in rids if str(rules[r].get("not_verifiable", "")).startswith(PLAYER)]
        e = {"kind": kind, "source": "llm", "rules": [], "residual": [], "verdict": None, "reason": ""}
        if code:
            seen = [o for r in code for o in outcomes.get(r, [])]
            e.update(rules=code, residual=[r for r in rids if r not in code])
            if "FAIL" in seen:
                e.update(source="code", verdict="contradicted")
            elif "PASS" in seen:
                e.update(source="code", verdict="met")
            else:
                e["reason"] = "its code rules have no instance in this candidate (no PASS, no FAIL)"
        elif player:
            e.update(source="vector-pending", residual=[r for r in rids if r not in player])
        out[u] = e
    return out


# ---------------------------------------------------------------------- stale

def stale(trace, old_text, new_text):
    old = spec_sections.by_key(spec_sections.split(old_text))
    new = spec_sections.by_key(spec_sections.split(new_text))
    changed = sorted(k for k in old if k in new and old[k].text != new[k].text)
    removed = sorted(k for k in old if k not in new)
    added = sorted(k for k in new if k not in old)
    hit = set(changed)
    units = sorted(u for u, e in trace.get("units", {}).items()
                   if any(s.get("key") in hit or s.get("key") not in new
                          for s in (e.get("sections") or [])))
    return {"changed": changed, "removed": removed, "added": added, "units": units}


# ---------------------------------------------------------------------- batch

def unit_text(uid, req_text, uc_text):
    """The text in context/ a walker judges `uid` against."""
    if uid.startswith("UC-"):
        lines = uc_text.split("\n")
        for i, line in enumerate(lines):
            m = re.match(r"^(#+) (UC-\d+)\b", line)
            if m and m.group(2) == uid:
                lvl = len(m.group(1))
                body = [line]
                for nxt in lines[i + 1:]:
                    h = re.match(r"^(#+) ", nxt)
                    if h and len(h.group(1)) <= lvl:
                        break
                    body.append(nxt)
                return "\n".join(body).strip()
        return None
    lines = req_text.split("\n")
    if "#p" not in uid:
        for i, line in enumerate(lines):
            m = re.match(r"^(\s*)- \*\*(R\d+\.\d+)\*\*", line)
            if m and m.group(2) == uid:
                ind = len(m.group(1))
                body = [line]
                for nxt in lines[i + 1:]:
                    if nxt.strip() and (nxt.startswith("#") or len(nxt) - len(nxt.lstrip()) <= ind):
                        break
                    body.append(nxt)
                return "\n".join(body).strip()
        return None
    owner_id, k = uid.split("#p")
    k = int(k)
    # The same scan as check-promotable.population(), so the K-th modal is the same one.
    top = re.compile(r"^- \*\*((?:R\d+|DP-[\d.]+|OOS-\d+))\.")
    crit = re.compile(r"^(\s*)- \*\*(R\d+\.\d+)\*\*")
    modal = re.compile(r"\bMUST NOT\b|\bMUST\b|\bSHALL NOT\b|\bSHALL\b|\bREQUIRED\b")
    owner, in_crit, ind, n, body = None, False, None, 0, []
    for line in lines:
        m = crit.match(line)
        if m:
            in_crit, ind = True, len(m.group(1))
            continue
        if in_crit and line.strip():
            here = len(line) - len(line.lstrip())
            if line.startswith("#") or here <= ind:
                in_crit = False
        m = top.match(line)
        if m:
            owner = m.group(1)
        if owner == owner_id and not in_crit:
            hits = len(modal.findall(line))
            mark = n < k <= n + hits
            n += hits
            body.append((">> " if mark else "   ") + line)
    if not body or n < k:
        return None
    return (f"(prose of {owner_id}; the unit is modal #{k} outside its criteria, on the line marked >>)\n"
            + "\n".join(body).rstrip())


def batch(trace, sections, uids, req_text, uc_text):
    units = trace.get("units", {})
    out, missing, printed = [], [], set()
    for u in uids:
        e = units.get(u)
        text = unit_text(u, req_text, uc_text)
        if e is None or text is None:
            missing.append(u)
            continue
        out.append(f"===== UNIT {u} ({e.get('kind', '?')}) =====\n{text}\n")
        keys = [s.get("key") for s in e.get("sections") or []]
        out.append(f"----- its sections: {', '.join(keys) or '(none traced)'}\n")
    for u in uids:
        for s in (units.get(u) or {}).get("sections") or []:
            k = s.get("key")
            if k in sections and k not in printed:
                printed.add(k)
                out.append(f"===== SECTION {k} =====\n{sections[k].text}")
    return "\n".join(out), missing


# ------------------------------------------------------------------------ CLI

def opts(argv, flags, valued):
    pos, got = [], {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in flags:
            got[a] = True
        elif a in valued:
            if i + 1 >= len(argv):
                raise Usage(f"{a} needs a value")
            got[a] = argv[i + 1]
            i += 1
        elif a.startswith("--"):
            raise Usage(f"unknown option {a}")
        else:
            pos.append(a)
        i += 1
    return pos, got


def spec_path(trace, given):
    if given:
        return given
    rel = trace.get("spec") if isinstance(trace, dict) else None
    if not rel:
        raise Usage("the trace names no `spec`; pass --spec")
    return rel if os.path.isabs(rel) else os.path.join(ROOT, rel)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__)
        return 0 if argv else 64
    try:
        cmd = argv[0] if argv[0] in ("sources", "stale", "batch") else "check"
        rest = argv[1:] if cmd != "check" else argv
        if cmd == "sources":
            pos, o = opts(rest, set(), {"--population"})
            if len(pos) != 1:
                raise Usage("sources takes one conformance JSON")
            res = sources(read_json(pos[0]), population(o.get("--population")))
            print(json.dumps(res, indent=1, sort_keys=True))
            return 0
        if cmd == "stale":
            pos, o = opts(rest, set(), {"--old", "--new"})
            if len(pos) != 1 or "--old" not in o or "--new" not in o:
                raise Usage("stale takes TRACE --old OLD --new NEW")
            texts = []
            for p in (o["--old"], o["--new"]):
                try:
                    with open(p, encoding="utf-8", newline="") as fh:
                        texts.append(fh.read())
                except OSError as e:
                    raise CannotTell(str(e))
            try:
                print(json.dumps(stale(read_json(pos[0]), *texts), indent=1))
            except spec_sections.SectionError as e:
                raise CannotTell(str(e))
            return 0
        if cmd == "batch":
            pos, o = opts(rest, set(), {"--spec"})
            if len(pos) < 2:
                raise Usage("batch takes TRACE and at least one unit")
            trace = read_json(pos[0])
            secs = spec_index(spec_path(trace, o.get("--spec")))
            with open(REQUIREMENTS, encoding="utf-8") as fh:
                req = fh.read()
            with open(USE_CASES, encoding="utf-8") as fh:
                uc = fh.read()
            text, missing = batch(trace, secs, pos[1:], req, uc)
            sys.stdout.write(text)
            for u in missing:
                print(f"no trace entry or no context/ text for {u}", file=sys.stderr)
            return 1 if missing else 0
        pos, o = opts(rest, {"--json", "--summary"}, {"--spec", "--population", "--rules"})
        if len(pos) != 1:
            raise Usage("check takes one trace")
        trace = read_json(pos[0])
        secs = spec_index(spec_path(trace, o.get("--spec")))
        pop = population(o.get("--population"))
        rules = catalogue(o.get("--rules")) if (o.get("--rules") or names_rules(trace)) else None
        findings = check(trace, secs, pop, rules)
    except Usage as e:
        sys.stderr.write(f"check-trace: {e}\n\n{__doc__}")
        return 64
    except CannotTell as e:
        print(f"CANNOT TELL: {e}")
        return 2
    summ = summary(trace, findings)
    if o.get("--summary"):
        print(json.dumps(summ, indent=1, sort_keys=True))
    elif o.get("--json"):
        print(json.dumps({"findings": findings, "summary": summ}, indent=1, ensure_ascii=False))
    else:
        for f in findings:
            extra = ""
            if "section" in f:
                extra = f"\t§{f['section']}"
            if "quote" in f:
                extra += f"\t{f['quote']!r}"
            print(f"{f['check']}\t{f['unit']}\t{f['detail']}{extra}")
        print(f"{len(findings)} finding(s) over {summ['units']} unit(s), "
              f"{summ['section_refs']} section reference(s), {summ['quotes']} quotation(s). "
              "A green says the trace is complete and literal; not that a quote fulfils its criterion.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
