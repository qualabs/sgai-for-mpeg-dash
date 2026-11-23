#!/usr/bin/env python3
"""List the names of our extension schema that are equal or close to a name of
the base standard's schema, so a naming review reads a list, not the spec
(ADR 0069).

Ours is `spec-source/syntax/sgai-extension.xsd`; the base is ISO's
6th-edition `DASH-MPD.xsd`, through bin/conformance/iso.py (DASH-MPD-UP.xsd
is not read). A NAME is what a schema declares: an element (`xs:element
name=`), an attribute (`xs:attribute name=`), a named type (`xs:complexType`
/ `xs:simpleType name=`) or an enumeration value (`xs:enumeration value=`).
References (`ref=`) and wildcards declare nothing.

Names are compared within two pools: element, attribute and type names with
each other (an attribute of ours may collide with an element of the base),
enumeration values only with enumeration values. A pair is a candidate when
one of these holds; the strongest is reported:

  exact    the same string.
  case     equal ignoring case.
  suffix   equal STEMS. A name is split into words at camelCase
           boundaries, hyphens and underscores, lower-cased
           (`URLType` -> url type; `overlay-corner` -> overlay corner); the
           stem is that list with the words `type` and `presentation`
           removed from its end, repeatedly, while one word remains
           (`AdType` -> ad; `OverlayPresentationType` -> overlay). A
           boundary is required: `Representation` is one word and keeps it.
  edit     both stems (words joined) at least 6 characters long and a
           Levenshtein distance of at most 2 between them (`mimeTypes` ~
           `mimeTypo`; a stem of 5 characters is never an edit candidate,
           a distance of 3 never is). Stems, not names, so a shared `Type`
           suffix does not make `AdType` close to `SAPType`.
  affix    one stem is the other plus exactly one word at its start or end,
           and the shorter stem is at least 5 characters long
           (`durationCap` ~ `duration`, `AdTitle` ~ `Title`; `trackingUri`
           is not close to `uri`, 3 characters). It is how a qualified
           synonym of a base name surfaces.

Per candidate: our name, its kind, where it is declared (enclosing named
type, or the element/attribute of an anonymous one, and the line); every
matching base name with the match kind and each of its declarations (kind,
type, context, line of DASH-MPD.xsd); and the keys of the sections of the
spec source where our name is mentioned, as `bin/spec-section.py get` takes
them (the same section split, bin/spec_sections.py). A mention is
`@name` for an attribute; `<name`, `` `name `` or `prefix:name` for an
element; the whole word for a type; the value between quotes or backticks
for an enumeration value. `bin/spec-section.py find` matches any substring,
so `Ad` would hit every section: that is why the search is by these forms.

Usage:
  bin/name-candidates.py [--ours XSD] [--iso XSD] [--spec FILE] [--json]

--ours defaults to spec-source/syntax/sgai-extension.xsd, --spec to
spec-source/sgai-spec.src.md, --iso to the cached DASH-MPD.xsd.

What the output is: input for a judgement, not a verdict. A name in the list
is not wrong (reusing a base name with the base's semantics is what
context/06 asks for); a name not in it may still be a synonym the five
rules cannot see (`skipAfter` for a differently worded concept). What it does not cover:
names in the prose or examples that the schema does not declare, mentions in
forms other than the ones above, and examples outside the spec source
(`{{example:…}}` directives are not expanded).

Exit codes: 0 the list was produced (empty or not) · 2 a schema or the spec
source cannot be read (ISO's schema not available, a file missing or not
well-formed, the source cannot be split) · 64 wrong command line.
"""
from __future__ import annotations

import json
import os
import re
import sys
import xml.parsers.expat
from dataclasses import dataclass, asdict

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
sys.path.insert(0, BIN)
import spec_sections  # noqa: E402

EXIT_OK, EXIT_UNKNOWN, EXIT_USAGE = 0, 2, 64
XS = "http://www.w3.org/2001/XMLSchema"
SUFFIXES = ("type", "presentation")
EDIT_MIN_LEN = 6
EDIT_MAX_DIST = 2
AFFIX_MIN_LEN = 5
RANK = {"exact": 0, "case": 1, "suffix": 2, "edit": 3, "affix": 4}
WORD = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+")


class Unreadable(Exception):
    pass


@dataclass
class Decl:
    name: str
    kind: str      # element | attribute | type | enumeration
    type: str      # declared type; the enclosing type for an enumeration
    context: str   # enclosing named type / element, or (schema)
    line: int


def pool(kind):
    return "enum" if kind == "enumeration" else "name"


def parse_xsd(path):
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as e:
        raise Unreadable(f"cannot read {path}: {e}") from e
    p = xml.parsers.expat.ParserCreate(namespace_separator=" ")
    stack = []   # (local tag, name or None)
    out = []

    def context():
        for tag, name in reversed(stack):
            if name and tag in ("complexType", "simpleType", "element", "attribute"):
                return name
        return "(schema)"

    def start(tag, attrs):
        ns, _, local = tag.rpartition(" ")
        name = None
        if ns == XS:
            line = p.CurrentLineNumber
            if local in ("element", "attribute") and "name" in attrs:
                name = attrs["name"]
                out.append(Decl(name, local, attrs.get("type", "(anonymous)"), context(), line))
            elif local in ("complexType", "simpleType") and "name" in attrs:
                name = attrs["name"]
                out.append(Decl(name, "type", local, context(), line))
            elif local == "enumeration" and "value" in attrs:
                ctx = context()
                out.append(Decl(attrs["value"], "enumeration", ctx, ctx, line))
        stack.append((local if ns == XS else None, name))

    def end(tag):
        stack.pop()

    p.StartElementHandler = start
    p.EndElementHandler = end
    try:
        p.Parse(data, True)
    except xml.parsers.expat.ExpatError as e:
        raise Unreadable(f"{path} is not well-formed: {e}") from e
    return out


def words(name):
    return [w.lower() for w in WORD.findall(name)]


def stem_words(name):
    ws = words(name) or [name.lower()]
    while len(ws) > 1 and ws[-1] in SUFFIXES:
        ws = ws[:-1]
    return ws


def stem(name):
    return "".join(stem_words(name))


def levenshtein(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def match(ours, base):
    """The strongest match kind between two names, or None."""
    if ours == base:
        return "exact"
    lo, lb = ours.lower(), base.lower()
    if lo == lb:
        return "case"
    wo, wb = stem_words(ours), stem_words(base)
    so, sb = "".join(wo), "".join(wb)
    if so == sb:
        return "suffix"
    if min(len(so), len(sb)) >= EDIT_MIN_LEN and levenshtein(so, sb) <= EDIT_MAX_DIST:
        return "edit"
    short, long_ = (wo, wb) if len(wo) < len(wb) else (wb, wo)
    if len("".join(short)) >= AFFIX_MIN_LEN and (long_[1:] == short or long_[:-1] == short):
        return "affix"
    return None


def mention(name, kind):
    n = re.escape(name)
    end = r"(?![\w-])"
    if kind == "attribute":
        return re.compile(r"@" + n + end)
    if kind == "element":
        return re.compile(r"(?:<|`|\w:)" + n + end)
    if kind == "type":
        return re.compile(r"(?<![\w-])" + n + end)
    return re.compile(r"[\"'`]" + n + r"[\"'`]")


def sections_of(name, kind, sections):
    rx = mention(name, kind)
    return [s.key for s in sections if rx.search(s.text)]


def candidates(ours, base, sections):
    by_name = {}
    for d in ours:
        by_name.setdefault((d.name, d.kind), []).append(d)
    out = []
    for (name, kind), decls in sorted(by_name.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        hits = {}
        for b in base:
            if pool(b.kind) != pool(kind):
                continue
            m = match(name, b.name)
            if m:
                h = hits.setdefault(b.name, {"iso_name": b.name, "match": m, "declarations": []})
                h["declarations"].append({k: v for k, v in asdict(b).items() if k != "name"})
        if not hits:
            continue
        matches = sorted(hits.values(), key=lambda h: (RANK[h["match"]], h["iso_name"]))
        out.append({
            "name": name,
            "kind": kind,
            "strongest": matches[0]["match"],
            "declared": [{"context": d.context, "type": d.type, "line": d.line} for d in decls],
            "matches": matches,
            "sections": sections_of(name, kind, sections),
        })
    return out


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(EXIT_USAGE)


def iso_xsd():
    from conformance import iso
    try:
        return str(iso.materialise() / "DASH-MPD.xsd")
    except iso.Unavailable as e:
        raise Unreadable(f"ISO's schema: {e}") from e


def run(ours_path, iso_path, spec_path):
    ours = parse_xsd(ours_path)
    base = parse_xsd(iso_path or iso_xsd())
    try:
        with open(spec_path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as e:
        raise Unreadable(f"cannot read {spec_path}: {e}") from e
    try:
        sections = spec_sections.split(text)
    except spec_sections.SectionError as e:
        raise Unreadable(f"{spec_path}: {e}") from e
    return ours, base, candidates(ours, base, sections)


def render_text(cands, n_ours, n_base, ours_path, iso_path):
    lines = [f"name-candidates: {len(cands)} of {n_ours} declared names of {ours_path} "
             f"are equal or close to one of the {n_base} of {iso_path}", ""]
    for c in cands:
        where = ", ".join(f"{d['context']} (line {d['line']}, {d['type']})" for d in c["declared"])
        lines.append(f"- {c['kind']} {c['name']} — declared in {where}")
        for m in c["matches"]:
            decl = "; ".join(f"{d['kind']} in {d['context']}: {d['type']} (line {d['line']})"
                             for d in m["declarations"])
            lines.append(f"    {m['match']:6} {m['iso_name']}: {decl}")
        lines.append("    sections: " + (", ".join(c["sections"]) or "(none in the source prose)"))
    lines += ["", "This list is input for the naming review (categories 3 and 4), not a verdict."]
    return "\n".join(lines) + "\n"


def main(argv):
    opts = {"--ours": os.path.join(ROOT, "spec-source", "syntax", "sgai-extension.xsd"),
            "--spec": os.path.join(ROOT, "spec-source", "sgai-spec.src.md"),
            "--iso": None}
    as_json = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            sys.stdout.write(__doc__)
            return EXIT_OK
        if a == "--json":
            as_json = True
        elif a in opts:
            if i + 1 >= len(argv):
                usage(f"{a} needs a value")
            opts[a] = argv[i + 1]
            i += 1
        else:
            usage(f"unknown argument {a}")
        i += 1
    try:
        ours, base, cands = run(opts["--ours"], opts["--iso"], opts["--spec"])
    except Unreadable as e:
        print(f"name-candidates: cannot tell: {e}", file=sys.stderr)
        return EXIT_UNKNOWN
    iso_label = opts["--iso"] or "ISO DASH-MPD.xsd (6th edition)"
    if as_json:
        json.dump({"ours": opts["--ours"], "iso": iso_label, "spec": opts["--spec"],
                   "rules": {"suffixes": list(SUFFIXES), "edit_min_len": EDIT_MIN_LEN,
                             "edit_max_dist": EDIT_MAX_DIST, "affix_min_len": AFFIX_MIN_LEN},
                   "declared": len(ours), "base_declared": len(base),
                   "count": len(cands), "candidates": cands},
                  sys.stdout, indent=1, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_text(cands, len(ours), len(base), opts["--ours"], iso_label))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
