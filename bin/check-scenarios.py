#!/usr/bin/env python3
"""The use cases of context/04 as executable vectors: are they all there, and
do they still say what the use cases say? (ADR 0064)

    check-scenarios.py [--source DIR] [--context DIR] [--json]
    check-scenarios.py section UC-NN [--context DIR]

`section` prints one UC's section of context/04 (what its vector is written
from) and, on its first line, the `uc_sha256` that section has now; exit 1
if there is no such UC. (bin/spec-section.py cannot split context/04: its
`#### D1`..`#### D5` keys repeat.)

DIR defaults: --source spec-source, --context context. A vector is
DIR/scenarios/UC-NN.yaml, validated against DIR/scenarios/schema.json;
DIR/scenarios/README.md says how one is written.

Checks, each a finding `<check>  <UC>  <detail>`:

  S-COVER    every UC of context/04 has a vector; every class the UC states
             has an outcome; no outcome for a class it does not state. The
             classes a UC states are its `#### D1`..`#### D5` headings plus
             the non-"—" cells of its row in the Coverage table; `legacy` is
             required when the section has a `**Legacy Player**` entry, and
             admitted when the section mentions a legacy Player at all
  S-SCHEMA   the file parses as YAML, is valid against schema.json, and its
             `uc` is its file name
  S-HASH     `uc_sha256` is the sha256 of the UC's section as it is now (the
             `### UC-NN` line up to the next heading of level 1 to 3, UTF-8
             bytes). A stale vector exits 2: it may still be right, but
             nobody has looked since the UC changed
  S-FIXTURE  every fixture exists; one under examples/ is in its index, one
             under scenarios/fixtures/ declares its class; each is green on
             levels 1 and 2 (no FAIL whose subject is that file, in the run
             of bin/check-dash-conformance.py --source on it), or, with
             `expect_red`, fails exactly the rules it lists; `entry`,
             `answered_by`, `matches` and every reference name a fixture of
             the vector; a request's `matches` equals that .http request
  S-REF      every candidate, option, opportunity and beacon reference is in
             its fixture (by @id or document order), and a beacon's `url`
             is the text of that event; a click's candidate has one
             ClickThrough and its `url` is one of that ClickThrough's
             @trackingUris; a destination's candidate has one ClickThrough
  S-DOC      every document URL a fixture of the vector points to (an
             InsertPresentation / ReplacePresentation @uri, an
             alternative-MPD Event's @value that is a URL, an
             OverlayPresentation / PauseAdPresentation @uri, an
             ImportedMPD's content, an @xlink:href) is absolute and is
             covered by a fixture's `url` or an `aps` entry, as the harness
             matches a request to them. Otherwise a run answers that
             request 204 as `other`, and no field sees a Player fetch it.
             Media segments, creatives, beacons and ClickThrough
             destinations are not documents and are not checked
  S-CAPS     each class's first three capability values form that class's
             row of the R3.1 table, read from context/03
  S-LAYOUT   every layout is an R12.2 token (read from context/03) or `none`
  S-TIME     times lie in [0, observe_until], a range has from <= to, and
             each outcome's presentation tiles [0, observe_until] with no gap
             and no overlap (a boundary written as a window ends one segment
             and starts the next with the same window)
  S-GEOM     every `geometry` rectangle lies inside the viewport, and at its
             instant the presentation shows the element it places
  S-CARRIER  each `missing_carrier` names a requirement context/03 defines

S-SCHEMA also finds a request with no `answered_by` that no `aps` entry
answers without a document, and an `extra_query_pattern` that is not a
regular expression. The schema and every check but S-COVER and
S-HASH are shared with the behaviour tests (bin/check-behaviour.py).

Then, for every vector and class: `NOT_VERIFIABLE — no executor`. No Player
runs a vector yet (the executor is the reference Player of the next phase,
on the Player harness of bin/players/). A green run says the vectors are
well formed, cover every UC x class, rest on green fixtures and were
written against the UCs as they are now. It does NOT say that any Player
behaves as a vector says, nor that a vector reads its UC correctly: that is
for a person, and for the executor once it exists.

Exit codes:
  0   nothing found
  1   at least one finding (a UC without a vector included)
  2   cannot tell: a vector is stale (S-HASH), context/04 or context/03
      cannot be read as this script expects, or the conformance run cannot
      tell. Uncertainty wins over both others
  64  wrong command line

Dependencies outside the standard library: lxml, PyYAML, jsonschema. When
one is not importable the script re-runs itself under `uv run --with` the
pinned versions.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEPS = ["lxml==6.1.3", "pyyaml==6.0.3", "jsonschema==4.25.1"]
NO_EXECUTOR = "NOT_VERIFIABLE — no executor"
CLASSES = ("D1", "D2", "D3", "D4", "D5")
CAP_AXES = ("sgai-video-decoders", "sgai-image-over-video", "sgai-html-over-video")
SLOT_PARAMS = {"sgai-allowed-layouts", "sgai-custom-region", "sgai-ad-audio-allowed"}
USAGE = __doc__.split("\n\n")[1]


def ensure_deps(script: str, argv: list[str]) -> None:
    try:
        import jsonschema  # noqa: F401
        import lxml  # noqa: F401
        import yaml  # noqa: F401
        return
    except ImportError:
        pass
    uv = shutil.which("uv")
    if os.environ.get("SGAI_SCENARIOS_REEXEC") or not uv:
        sys.stderr.write(f"cannot tell: {', '.join(DEPS)} not importable and `uv` not available\n")
        raise SystemExit(2)
    env = dict(os.environ, SGAI_SCENARIOS_REEXEC="1")
    with_ = [x for d in DEPS for x in ("--with", d)]
    os.execve(uv, [uv, "run", "-q", "--no-project", *with_, "python", "-I", script, *argv], env)


class CannotTell(Exception):
    pass


# ---------------------------------------------------------------- context

HEADING = re.compile(r"^(#{1,3}) ", re.M)
UC_HEAD = re.compile(r"^### (UC-\d{2})\b", re.M)


def uc_sections(text: str) -> dict:
    """{UC-NN: section text}: from its `### UC-NN` line to the next heading
    of level 1 to 3, or the end of the file."""
    out = {}
    for m in UC_HEAD.finditer(text):
        nxt = HEADING.search(text, m.end())
        out[m.group(1)] = text[m.start(): nxt.start() if nxt else len(text)]
    if not out:
        raise CannotTell("context/04 has no `### UC-NN` section")
    return out


def uc_hash(section: str) -> str:
    return hashlib.sha256(section.encode("utf-8")).hexdigest()


def coverage_rows(text: str) -> dict:
    """{UC-NN: {class: cell}} from the Coverage table of context/04."""
    m = re.search(r"^## Coverage\n(.*?)(?=^## )", text, re.M | re.S)
    if not m:
        raise CannotTell("context/04 has no `## Coverage` section")
    rows = {}
    for line in m.group(1).splitlines():
        r = re.match(r"^\| (UC-\d{2}) ", line)
        if not r:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 7:
            raise CannotTell(f"Coverage row of {r.group(1)} has {len(cells)} cells, expected 7")
        rows[r.group(1)] = dict(zip(CLASSES, cells[2:]))
    return rows


def required_classes(uc: str, section: str, rows: dict) -> tuple[set, set]:
    """(required, admitted) classes of one UC."""
    req = set(re.findall(r"^#### (D[1-5])\s*$", section, re.M))
    req |= {c for c, cell in rows.get(uc, {}).items() if cell not in ("—", "-", "")}
    admitted = set(req)
    if "**Legacy Player**" in section or re.search(r"^#### Legacy", section, re.M):
        req.add("legacy")
    if re.search(r"legacy", section, re.I):
        admitted.add("legacy")
    return req, admitted | req


def r31_table(text: str) -> dict:
    """{class: {axis: allowed values}} from the R3.1 table of context/03."""
    m = re.search(r"\*\*R3\.1\*\*(.*?)(?=\n  - \*\*R)", text, re.S)
    if not m:
        raise CannotTell("context/03 has no R3.1 criterion")
    lines = [ln.strip() for ln in m.group(1).splitlines() if ln.strip().startswith("|")]
    if len(lines) < 3:
        raise CannotTell("R3.1 has no class table")
    head = [c.strip() for c in lines[0].strip("|").split("|")]
    axes = [re.sub(r"`", "", h) for h in head[1:]]
    if tuple(axes) != CAP_AXES:
        raise CannotTell(f"R3.1 table columns are {axes}, expected {list(CAP_AXES)}")
    out = {}
    for ln in lines[2:]:
        cells = [c.strip() for c in ln.strip("|").split("|")]
        cls = cells[0].split()[0]
        out[cls] = {a: {int(v) for v in re.findall(r"`(\d+)`", c)} for a, c in zip(axes, cells[1:])}
    if set(out) != set(CLASSES):
        raise CannotTell(f"R3.1 table rows are {sorted(out)}, expected {list(CLASSES)}")
    return out


def r122_tokens(text: str) -> set:
    m = re.search(r"\*\*R12\.2\*\*(.*?)(?=\n  - \*\*R)", text, re.S)
    if not m:
        raise CannotTell("context/03 has no R12.2 criterion")
    seg = m.group(1).split("Every token")[0]
    toks = set(re.findall(r"`([a-z][a-z-]*)`", seg))
    if "linear" not in toks:
        raise CannotTell("R12.2's token list cannot be read")
    return toks


def requirement_ids(text: str) -> set:
    return set(re.findall(r"\*\*(R\d+(?:\.\d+[a-z]?)?)(?:\*\*|\. )", text))


# ---------------------------------------------------------------- fixtures

def fixture_fails(source: Path, context_dir: Path, scen: dict) -> tuple[dict, list]:
    """Run levels 1 and 2 over the examples and the scenario fixtures.

    scen: {path relative to source: declared class} of fixtures under
    scenarios/fixtures/. Returns ({subject: [FAIL details]}, cannot) where a
    subject is the conformance run's (relative to examples/ for an example,
    to source for a scenario fixture), and every judged subject has a key."""
    sys.path.insert(0, str(HERE))
    from conformance import runner, source as src
    from conformance.model import Outcome, Report

    report = Report()
    ctx, idx = src.load(source, context_dir, report)
    if ctx is None:
        return {}, list(report.cannot)
    for i, (name, cls) in enumerate(sorted(scen.items())):
        p = source / name
        kind, rs, b = src.deduced(p)
        if kind != src.CLASSES.get(cls):
            idx.append(src.FIX2.result(Outcome.FAIL, name, detail=f"declared {cls}, but the document reads as {kind}"))
        if cls == "request":
            ctx.requests.extend(src.FixtureRequest(r.line - 1, r.method, r.target, r.params, name=name) for r in rs)
        elif b is not None:
            ctx.blocks.append(src.FixtureBlock(index=1000 + i, line=1, text=b.text,
                                               kind=b.kind if b.kind == "malformed" else src.CLASSES.get(cls, b.kind),
                                               root=b.root, error=b.error, name=name, declared=cls))
    results = idx + runner.level1(ctx, None) + src.level2(ctx, report)
    out: dict = {}
    for r in results:
        subj = r.subject.split(" (line ")[0]
        out.setdefault(subj, [])
        if r.outcome is Outcome.FAIL:
            out[subj].append(f"{r.rule}: {r.detail}")
    return out, list(report.cannot)


def _local(el) -> str:
    return el.tag.split("}")[-1] if isinstance(el.tag, str) else ""


class Doc:
    """A parsed fixture, for references into it."""

    def __init__(self, path: Path):
        from lxml import etree
        self.root = None
        self.request = None
        if path.suffix == ".http":
            first = path.read_text(encoding="utf-8").splitlines()[0].split()
            host = re.search(r"^Host:\s*(\S+)", path.read_text(encoding="utf-8"), re.M)
            self.request = (host.group(1) if host else "", first[1] if len(first) > 1 else "")
            return
        try:
            self.root = etree.parse(str(path)).getroot()
        except etree.XMLSyntaxError:
            self.root = None

    def candidates(self) -> list:
        if self.root is None:
            return []
        return [e for e in self.root if _local(e) in ("Period", "Ad")]

    def candidate(self, ref: dict):
        cs = self.candidates()
        if "index" in ref:
            return cs[ref["index"] - 1] if ref["index"] <= len(cs) else None
        return next((c for c in cs if c.get("id") == ref["id"]), None)

    @staticmethod
    def option(cand, ref):
        opts = [e for e in cand if _local(e) == "RenderableAsset"]
        if "index" in ref:
            return opts[ref["index"] - 1] if ref["index"] <= len(opts) else None
        return next((o for o in opts if o.get("id") == ref["id"]), None)

    def event(self, scope, event_id: str):
        scope = self.root if scope is None else scope
        if scope is None:
            return None
        return next((e for e in scope.iter() if _local(e) == "Event" and e.get("id") == event_id), None)


# ---------------------------------------------------------------- the vector

def _lo(t):
    return t["from"] if isinstance(t, dict) else t


def _hi(t):
    return t["to"] if isinstance(t, dict) else t


def _times(o: dict):
    """(label, value) of every time of an outcome."""
    for i, r in enumerate(o.get("requests", [])):
        yield f"requests[{i}].at", r["at"]
    for i, b in enumerate(o.get("beacons", [])):
        yield f"beacons[{i}].at", b["at"]
    for f in ("clicks", "destinations"):
        for i, c in enumerate(o.get(f, [])):
            yield f"{f}[{i}].at", c["at"]
    for i, s in enumerate(o.get("presentation", [])):
        yield f"presentation[{i}].start", s["start"]
        yield f"presentation[{i}].end", s["end"]


def check_times(v: dict, where: str, o: dict, find) -> None:
    lim = v["observe_until"]
    for label, t in _times(o):
        if isinstance(t, dict):
            if t["from"] > t["to"]:
                find("S-TIME", f"{where}.{label}: from {t['from']} > to {t['to']}")
            vals = (t["from"], t["to"])
        else:
            vals = (t,)
        for x in vals:
            if x > lim:
                find("S-TIME", f"{where}.{label}: {x} is after observe_until {lim}")
    segs = o["presentation"]
    at = 0
    for i, s in enumerate(segs):
        if s["start"] != at:
            find("S-TIME", f"{where}.presentation[{i}] starts at {s['start']}, expected {at} "
                           "(segments tile [0, observe_until] in order)")
        if _lo(s["end"]) <= _lo(s["start"]) or _hi(s["end"]) <= _hi(s["start"]):
            find("S-TIME", f"{where}.presentation[{i}]: end {s['end']} <= start {s['start']}")
        at = s["end"]
    if at != lim:
        find("S-TIME", f"{where}.presentation ends at {at}, expected observe_until {lim}")


def check_geometry(v: dict, where: str, o: dict, find) -> None:
    """S-GEOM: a rectangle lies inside the viewport, and at its instant the
    presentation shows the element it places."""
    for i, g in enumerate(o.get("geometry", [])):
        if g["at"] > v["observe_until"]:
            find("S-TIME", f"{where}.geometry[{i}].at: {g['at']} is after observe_until {v['observe_until']}")
            continue
        seg = next((s for s in o["presentation"] if _lo(s["start"]) <= g["at"] < _lo(s["end"])), None)
        if seg is None and o["presentation"] and g["at"] == o["presentation"][-1]["end"]:
            seg = o["presentation"][-1]
        shown = {e["element"] for e in seg["shows"]} if seg else set()
        for el in ("primary", "ad"):
            if el not in g:
                continue
            r = g[el]
            if r["x"] + r["width"] > 100 or r["y"] + r["height"] > 100:
                find("S-GEOM", f"{where}.geometry[{i}].{el}: extends past the viewport")
            if el not in shown:
                find("S-GEOM", f"{where}.geometry[{i}].{el}: the presentation shows no {el} at {g['at']}")


def check_refs(v: dict, where: str, o: dict, docs: dict, find) -> None:
    def doc(path, label):
        if path not in docs:
            find("S-FIXTURE", f"{where}.{label}: {path} is not a fixture of this vector")
            return None
        return docs[path]

    def cand(ref, label):
        d = doc(ref["fixture"], label)
        if d is None or d.root is None:
            return None
        c = d.candidate(ref)
        if c is None:
            find("S-REF", f"{where}.{label}: no candidate {ref.get('id', '#%s' % ref.get('index'))} in {ref['fixture']}")
        return c

    def opt(c, ref, label):
        if c is None or ref is None:
            return
        if Doc.option(c, ref) is None:
            find("S-REF", f"{where}.{label}: no option {ref} in that candidate")

    no_doc = {a["url"] for a in v.get("aps", []) if "document" not in a}
    for i, r in enumerate(o["requests"]):
        if "extra_query_pattern" in r:
            try:
                re.compile(r["extra_query_pattern"])
            except re.error as e:
                find("S-SCHEMA", f"{where}.requests[{i}].extra_query_pattern: not a regular expression ({e})")
        if "answered_by" in r:
            doc(r["answered_by"], f"requests[{i}].answered_by")
        elif r["url"] not in no_doc:
            find("S-SCHEMA", f"{where}.requests[{i}]: no answered_by, and no `aps` entry answers "
                             f"{r['url']} without a document")
        for k in r.get("query", {}):
            if k not in SLOT_PARAMS and k not in v["sends_capabilities"]:
                find("S-REF", f"{where}.requests[{i}].query: {k} is neither a slot parameter nor in sends_capabilities")
        if "matches" in r:
            d = doc(r["matches"], f"requests[{i}].matches")
            if d is not None:
                if d.request is None:
                    find("S-FIXTURE", f"{where}.requests[{i}].matches: {r['matches']} is not a request")
                else:
                    u = urlsplit(r["url"])
                    want_q = sorted(parse_qsl(u.query) + list(r.get("query", {}).items()))
                    host, target = d.request
                    t = urlsplit(target)
                    if (u.netloc, u.path, want_q) != (host, t.path, sorted(parse_qsl(t.query))):
                        find("S-FIXTURE", f"{where}.requests[{i}]: url + query differ from the request in {r['matches']}")
    for i, s in enumerate(o["selection"]):
        d = doc(s["opportunity"]["fixture"], f"selection[{i}].opportunity")
        if d is not None and d.event(None, s["opportunity"]["event_id"]) is None:
            find("S-REF", f"{where}.selection[{i}].opportunity: no Event @id={s['opportunity']['event_id']} "
                          f"in {s['opportunity']['fixture']}")
        if s["result"] != "presented" and s["presented"]:
            find("S-SCHEMA", f"{where}.selection[{i}]: result {s['result']} with candidates presented")
        for j, p in enumerate(s["presented"]):
            opt(cand(p["candidate"], f"selection[{i}].presented[{j}]"), p["option"],
                f"selection[{i}].presented[{j}].option")
    for i, seg in enumerate(o["presentation"]):
        for j, e in enumerate(seg["shows"]):
            if "candidate" in e:
                opt(cand(e["candidate"], f"presentation[{i}].shows[{j}]"), e.get("option"),
                    f"presentation[{i}].shows[{j}].option")
    for f in ("clicks", "destinations"):
        for i, c in enumerate(o.get(f, [])):
            cnd = cand(c["candidate"], f"{f}[{i}].candidate")
            if cnd is None:
                continue
            cts = [e for e in cnd.iter() if _local(e) == "ClickThrough"]
            if len(cts) != 1:
                find("S-REF", f"{where}.{f}[{i}]: that candidate has {len(cts)} ClickThrough, not one")
            elif f == "clicks" and c["url"] not in (cts[0].get("trackingUris") or "").split():
                find("S-REF", f"{where}.clicks[{i}]: url {c['url']} is not one of the ClickThrough's @trackingUris")
    for i, b in enumerate(o["beacons"]):
        d = doc(b["fixture"], f"beacons[{i}]")
        if d is None or d.root is None:
            continue
        scope = None
        if "candidate" in b:
            scope = cand(b["candidate"], f"beacons[{i}].candidate")
            if scope is None:
                continue
        ev = d.event(scope, b["id"])
        if ev is None:
            find("S-REF", f"{where}.beacons[{i}]: no Event @id={b['id']} in {b['fixture']}"
                          + (" within that candidate" if scope is not None else ""))
        elif "url" in b and (ev.text or "").strip() != b["url"]:
            find("S-REF", f"{where}.beacons[{i}]: url {b['url']} is not the event's text {(ev.text or '').strip()}")


XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
RESOLVE_TO_ZERO = "urn:mpeg:dash:resolve-to-zero:2013"
ALT_MPD_SCHEME = "urn:mpeg:dash:event:alternativeMPD:"


def pointed_documents(root) -> list[tuple[str, str]]:
    """(what points, URL) for every document URL a parsed fixture points to:
    an InsertPresentation / ReplacePresentation @uri and an alternative-MPD
    Event's @value when it is a URL (the break's List MPD), an
    OverlayPresentation / PauseAdPresentation @uri (the resolution document),
    an ImportedMPD's content (a List MPD's ad), and any @xlink:href but
    resolve-to-zero (a sub-MPD link). Media (BaseURL, segments), creatives
    (src, background), beacons (Event text, trackingUris) and ClickThrough
    destinations are not documents and are not here."""
    sys.path.insert(0, str(HERE))
    from conformance.spec import vocab
    D, S = vocab.DASH, vocab.SGAI
    by_uri = {f"{{{D}}}InsertPresentation", f"{{{D}}}ReplacePresentation"}
    by_uri |= {f"{{{S}}}{w}" for w in vocab.WINDOW.values()}
    out = []
    if root is None:
        return out
    for e in root.iter():
        if not isinstance(e.tag, str):
            continue
        name = _local(e)
        if e.tag in by_uri and e.get("uri"):
            out.append((f"{name}@uri", e.get("uri").strip()))
        if e.tag == f"{{{D}}}ImportedMPD" and (e.text or "").strip():
            out.append(("ImportedMPD", e.text.strip()))
        if e.get(XLINK_HREF) and e.get(XLINK_HREF).strip() != RESOLVE_TO_ZERO:
            out.append((f"{name}@xlink:href", e.get(XLINK_HREF).strip()))
        if (e.tag == f"{{{D}}}Event" and e.getparent() is not None
                and (e.getparent().get("schemeIdUri") or "").startswith(ALT_MPD_SCHEME)
                and urlsplit((e.get("value") or "").strip()).scheme):
            out.append((f"Event@value (id {e.get('id')})", e.get("value").strip()))
    return out


def check_pointed(v: dict, docs: dict, find) -> None:
    """S-DOC: every document URL a fixture of the vector points to is
    answered by the vector: a fixture's `url` or an `aps` entry covers it,
    as the harness decides it (behaviour_compare.added_query, the scheme
    compared too: bin/players/behaviour.mjs `covers`). Anything else the
    harness answers 204 as kind `other`, which no field compares."""
    sys.path.insert(0, str(HERE))
    from conformance.behaviour_compare import added_query
    declared = [f["url"] for f in v["fixtures"] if f.get("url")] + [a["url"] for a in v.get("aps", [])]

    def covered(u):
        return any(urlsplit(d).scheme == urlsplit(u).scheme and added_query(d, u) is not None for d in declared)

    for p, d in docs.items():
        for what, u in pointed_documents(d.root):
            if urlsplit(u).scheme not in ("http", "https"):
                find("S-DOC", f"{p}: {what} {u} is not an absolute http(s) URL; the vector cannot say what answers it")
            elif not covered(u):
                find("S-DOC", f"{p}: {what} {u} is neither a fixture's url nor an `aps` entry of this vector")


def check_vector(path: Path, v: dict, ctx: dict, find) -> None:
    uc = v["uc"]
    if path.stem != uc:
        find("S-SCHEMA", f"`uc` is {uc} but the file is {path.name}")
    sections = ctx["sections"]
    if uc not in sections:
        find("S-COVER", f"{uc} is not a use case of context/04")
        return
    now = uc_hash(sections[uc])
    if v["uc_sha256"] != now:
        find("S-HASH", f"uc_sha256 {v['uc_sha256'][:12]}… is not the section's {now[:12]}…: the UC changed")
    req, admitted = required_classes(uc, sections[uc], ctx["rows"])
    have = set(v["outcomes"])
    for c in sorted(req - have):
        find("S-COVER", f"class {c} has no outcome")
    for c in sorted(have - admitted):
        find("S-COVER", f"outcome for class {c}, which {uc} does not state")
    check_body(uc, v, ctx, find)


def check_body(key: str, v: dict, ctx: dict, find) -> None:
    """Every check of a vector that does not depend on what it is written
    from (a UC or a criterion): capabilities, fixtures, references, layouts,
    times, geometry, the test APS, actions and missing carriers."""
    have = set(v["outcomes"])
    for c in sorted(have - set(v["player_capabilities"])):
        find("S-CAPS", f"class {c} has an outcome and no player_capabilities")
    for c, caps in v["player_capabilities"].items():
        if c == "legacy":
            continue
        row = ctx["r31"][c]
        bad = [a for a in CAP_AXES if caps[a] not in row[a]]
        if bad:
            find("S-CAPS", f"{c}: {', '.join(f'{a}={caps[a]}' for a in bad)} is not R3.1's row for {c}")

    src = ctx["source"]
    docs, scen = {}, {}
    seen = set()
    for f in v["fixtures"]:
        p = f["path"]
        if p in seen:
            find("S-FIXTURE", f"{p} listed twice")
        seen.add(p)
        if not (src / p).is_file():
            find("S-FIXTURE", f"{p} does not exist")
            continue
        if p.startswith("examples/"):
            declared = ctx["index"].get(p[len("examples/"):])
            if declared is None:
                find("S-FIXTURE", f"{p} has no entry in examples/index.yaml")
            elif "class" in f and f["class"] != declared:
                find("S-FIXTURE", f"{p}: class {f['class']}, but examples/index.yaml declares {declared}")
        else:
            if "class" not in f:
                find("S-FIXTURE", f"{p}: a scenario fixture declares its class")
            else:
                scen[p] = f["class"]
        if "expect_red" in f:
            ctx.setdefault("expect_red", {})[(key, p)] = set(f["expect_red"])
        docs[p] = Doc(src / p)
    if v["entry"] not in docs:
        find("S-FIXTURE", f"entry {v['entry']} is not a fixture of this vector")
    for i, a in enumerate(v.get("aps", [])):
        if "document" in a and a["document"] not in docs:
            find("S-FIXTURE", f"aps[{i}].document: {a['document']} is not a fixture of this vector")
    check_pointed(v, docs, find)
    ctx["scenario_fixtures"].update(scen)
    ctx["used_fixtures"].setdefault(key, []).extend(docs)

    runs = [("outcomes", v["outcomes"])]
    runs += [(f"variants[{x['id']}]", x["outcomes"]) for x in v.get("variants", [])]
    for label, outs in runs:
        for c, o in outs.items():
            where = f"{label}.{c}"
            check_times(v, where, o, find)
            check_geometry(v, where, o, find)
            check_refs(v, where, o, docs, find)
            layouts = [s["layout"] for s in o["presentation"]]
            layouts += [p["layout"] for s in o["selection"] for p in s["presented"]]
            for lay in layouts:
                if lay != "none" and lay not in ctx["tokens"]:
                    find("S-LAYOUT", f"{where}: layout {lay!r} is not an R12.2 token")
    for x in v.get("variants", []):
        for c in sorted(set(x["outcomes"]) - set(v["outcomes"])):
            find("S-COVER", f"variant {x['id']}: class {c} has no outcome in the main run")
    for a in v["actions"] + [a for x in v.get("variants", []) for a in x["actions"]]:
        if a["at"] > v["observe_until"]:
            find("S-TIME", f"action {a['do']} at {a['at']} is after observe_until")
    for m in v.get("missing_carrier", []):
        if m["requirement"] not in ctx["req_ids"]:
            find("S-CARRIER", f"{m['requirement']} is not a requirement or criterion of context/03")
        outs = v["outcomes"]
        if "variant" in m:
            outs = next((x["outcomes"] for x in v.get("variants", []) if x["id"] == m["variant"]), None)
            if outs is None:
                find("S-CARRIER", f"{m['requirement']}: no variant {m['variant']}")
                continue
        for c in m["classes"]:
            if c not in outs:
                find("S-CARRIER", f"{m['requirement']}: class {c} has no outcome")


def run(source: Path, context_dir: Path) -> dict:
    import jsonschema
    import yaml
    sys.path.insert(0, str(HERE))
    from conformance import source as srcmod

    out = {"findings": [], "cannot": [], "vectors": {}, "missing": []}

    def finder(uc):
        def find(check, detail):
            out["findings"].append({"check": check, "uc": uc, "detail": detail})
        return find

    try:
        c04 = (context_dir / "04-use-cases.md").read_text(encoding="utf-8")
        ctx = load_context(source, context_dir)
        ctx.update(sections=uc_sections(c04), rows=coverage_rows(c04))
    except (OSError, CannotTell, srcmod.IndexError_, json.JSONDecodeError) as e:
        out["cannot"].append(str(e))
        return out
    validator = jsonschema.Draft202012Validator(ctx["schema"])

    files = sorted((source / "scenarios").glob("UC-*.yaml"))
    by_uc = {}
    for p in files:
        find = finder(p.stem)
        try:
            v = yaml.safe_load(p.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            find("S-SCHEMA", f"{p.name} is not YAML: {e}")
            continue
        errs = sorted(validator.iter_errors(v), key=lambda e: list(e.absolute_path))
        if errs:
            for e in errs:
                find("S-SCHEMA", f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}")
            continue
        by_uc[p.stem] = v
        check_vector(p, v, ctx, find)
        out["vectors"][p.stem] = {c: NO_EXECUTOR for c in sorted(v["outcomes"])}

    for uc in sorted(ctx["sections"]):
        if uc not in {p.stem for p in files}:
            out["missing"].append(uc)
            req, _ = required_classes(uc, ctx["sections"][uc], ctx["rows"])
            finder(uc)("S-COVER", f"no vector (classes stated: {', '.join(sorted(req)) or 'none'})")

    green_fixtures(ctx, context_dir, out, finder)
    return out


def load_context(source: Path, context_dir: Path) -> dict:
    """What every vector is checked against: context/03 (R3.1 rows, R12.2
    tokens, requirement ids), examples/index.yaml and the schema. Raises
    OSError, CannotTell, IndexError_ or JSONDecodeError."""
    sys.path.insert(0, str(HERE))
    from conformance import source as srcmod
    c03 = (context_dir / "03-requirements.md").read_text(encoding="utf-8")
    return {"source": source, "c03": c03,
            "r31": r31_table(c03), "tokens": r122_tokens(c03), "req_ids": requirement_ids(c03),
            "index": srcmod.read_index(source / srcmod.INDEX),
            "schema": json.loads((source / "scenarios" / "schema.json").read_text(encoding="utf-8")),
            "scenario_fixtures": {}, "used_fixtures": {}}


def green_fixtures(ctx: dict, context_dir: Path, out: dict, finder) -> None:
    """S-FIXTURE: every fixture the vectors used is green on levels 1 and 2."""
    used = ctx["used_fixtures"]
    if not used:
        return
    fails, cannot = fixture_fails(ctx["source"], context_dir, ctx["scenario_fixtures"])
    out["cannot"].extend(cannot)
    if cannot:
        return
    red = ctx.get("expect_red", {})
    for key, paths in used.items():
        for p in paths:
            subj = p[len("examples/"):] if p.startswith("examples/") else p
            if subj not in fails:
                finder(key)("S-FIXTURE", f"{p}: no conformance result names it")
            want = red.get((key, p))
            if want is None:
                for d in fails.get(subj, []):
                    finder(key)("S-FIXTURE", f"{p} is not green: {d}")
                continue
            got = {d.split(":", 1)[0] for d in fails.get(subj, [])}
            for d in fails.get(subj, []):
                if d.split(":", 1)[0] not in want:
                    finder(key)("S-FIXTURE", f"{p} fails a rule expect_red does not list: {d}")
            for r in sorted(want - got):
                finder(key)("S-FIXTURE", f"{p}: expect_red lists {r}, which does not fail on it")


def exit_code(out: dict) -> int:
    if out["cannot"] or any(f["check"] == "S-HASH" for f in out["findings"]):
        return 2
    return 1 if out["findings"] else 0


def to_text(out: dict) -> str:
    lines = []
    for c in out["cannot"]:
        lines.append(f"CANNOT TELL\t{c}")
    for f in out["findings"]:
        lines.append(f"{f['check']}\t{f['uc']}\t{f['detail']}")
    for uc, cls in sorted(out["vectors"].items()):
        for c, verdict in cls.items():
            lines.append(f"{uc}\t{c}\t{verdict}")
    n = len(out["vectors"]) + len(out["missing"])
    lines.append(f"{len(out['vectors'])} vectors of {n} use cases; {len(out['findings'])} findings; "
                 f"without a vector: {', '.join(out['missing']) or 'none'}")
    lines.append("A green run says the vectors are well formed, cover every UC x class, rest on green fixtures and "
                 "match the UCs as they are now; no Player has run them (NOT_VERIFIABLE — no executor).")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    opts = {"--source": "spec-source", "--context": "context"}
    as_json = False
    args = list(argv)
    uc = None
    if args and args[0] == "section":
        if len(args) < 2 or not re.fullmatch(r"UC-\d{2}", args[1]):
            sys.stderr.write(f"section needs a UC-NN\n{USAGE}\n")
            return 64
        uc, args = args[1], args[2:]
    while args:
        a = args.pop(0)
        if a in opts:
            if not args:
                sys.stderr.write(f"{a} needs a value\n{USAGE}\n")
                return 64
            opts[a] = args.pop(0)
        elif a == "--json" and uc is None:
            as_json = True
        else:
            sys.stderr.write(f"unknown argument {a}\n{USAGE}\n")
            return 64
    source, context_dir = Path(opts["--source"]), Path(opts["--context"])
    if uc is not None:
        if not (context_dir / "04-use-cases.md").is_file():
            sys.stderr.write(f"{context_dir}/04-use-cases.md not found\n{USAGE}\n")
            return 64
        secs = uc_sections((context_dir / "04-use-cases.md").read_text(encoding="utf-8"))
        if uc not in secs:
            sys.stderr.write(f"{uc} is not a use case of context/04\n")
            return 1
        print(f"uc_sha256: {uc_hash(secs[uc])}")
        sys.stdout.write(secs[uc])
        return 0
    for d in (source, context_dir):
        if not d.is_dir():
            sys.stderr.write(f"directory not found: {d}\n{USAGE}\n")
            return 64
    ensure_deps(os.path.abspath(__file__), argv)
    out = run(source, context_dir)
    out["exit"] = exit_code(out)
    print(json.dumps(out, indent=2, ensure_ascii=False) if as_json else to_text(out))
    return out["exit"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
