"""The behaviour battery's comparison: what the reference was observed to do
against what a vector expects (ADR 0081: the JS measures, Python decides).

Pure: no browser, no network, no file. `compare` takes one vector, one
outcome of it (a class, a variant) and one job of what
bin/players/behaviour.mjs recorded, and returns one Result per expected field:

  requests      the document requests: URL, the query the Player added, the
                session time, the fixture served, the `.http` it `matches`
  selection     per opportunity, the candidates and options presented, with
                their layout, in order of first appearance
  presentation  the segments on screen: layout, what each shows, the primary's
                main-presentation time at the segment's start (`from`)
  audio         only when a segment declares `audio`: NOT_VERIFIABLE, the
                observation carries no audio state
  beacons       every beacon fired, at its time; none unexpected
  clicks        only when the outcome has `clicks`: the click-tracking URLs of
                a ClickThrough fired, at their time; none unexpected
  destinations  with `clicks`: a ClickThrough's @uri made available (opened,
                or shown on screen), at its time; none unexpected
  geometry      only when the outcome has it: the primary's rectangle and the
                ad layer's bounding box at an instant, in % of the viewport

PASS, FAIL naming the field and what was observed against what was expected,
NOT_VERIFIABLE with its reason, or NOT_APPLICABLE (the requests of an outcome
that says `requests_not_compared`). Times follow spec-source/scenarios/README.md:
the session clock, in 1/timescale s since the first frame was presented
(anything observed before it is at 0), an exact time matched within the
tolerance, a window `{from, to}` widened by it. The tolerance is the item's own
`tolerance` when it has one (a request, a beacon, a click, a destination, a
presentation segment's start), else the vector's. The semantics of each field
are in the function that decides it.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlsplit
from xml.etree import ElementTree as ET

from .model import Outcome, Result

MAX_PROBLEMS = 6


# --------------------------------------------------------------------------- urls and times

def _split(url: str):
    s = urlsplit(url)
    return (s.netloc.lower(), s.path or "/"), sorted(parse_qsl(s.query, keep_blank_values=True))


def added_query(declared: str, requested: str) -> dict | None:
    """The parameters `requested` adds to `declared`, or None when `declared`
    does not cover it (another host or path, or a declared parameter missing
    or with another value). The scheme is not compared."""
    (db, dq), (rb, rq) = _split(declared), _split(requested)
    if db != rb:
        return None
    rest = list(rq)
    for kv in dq:
        if kv not in rest:
            return None
        rest.remove(kv)
    out: dict = {}
    for k, v in rest:
        out[k] = f"{out[k]} {v}" if k in out else v
    return out


def same_url(a: str, b: str) -> bool:
    return _split(a) == _split(b)


def within(t: float, when, tol: float) -> bool:
    if isinstance(when, dict):
        return when["from"] - tol <= t <= when["to"] + tol
    return abs(t - when) <= tol


def lo(when) -> float:
    return when["from"] if isinstance(when, dict) else when


def dist(t: float, when) -> float:
    """How far `t` is from an instant, or from a window (0 inside it)."""
    if isinstance(when, dict):
        return max(when["from"] - t, 0, t - when["to"])
    return abs(t - when)


def tol_of(item: dict, default: float) -> float:
    return item.get("tolerance", default)


def fmt_when(when) -> str:
    return f"{when['from']}..{when['to']}" if isinstance(when, dict) else f"{when}"


def _r(t: float) -> int:
    return int(round(t))


# --------------------------------------------------------------------------- the observation

@dataclass
class Observed:
    """One job, in the vector's units, on the session clock. `samples` are
    page samples: {t, layout, elements, seek?}; element times are converted
    too. `startup` is the time from load() to the first frame, or None when no
    frame was ever shown."""
    requests: list = field(default_factory=list)   # {at, url, fixture, kind}
    others: list = field(default_factory=list)     # {at, url, resourceType}
    samples: list = field(default_factory=list)
    actions: list = field(default_factory=list)
    destinations: list = field(default_factory=list)   # {at, uri}: a ClickThrough URI shown on screen
    startup: float | None = None


def first_frame(samples: list) -> float | None:
    """The adapter's rule for the session clock's origin, for a record that
    does not carry it: the first sample showing a `primary` or an `ad`."""
    for s in sorted(samples, key=lambda s: s["t"]):
        if any(e.get("element") in ("primary", "ad") for e in s.get("elements", [])):
            return s["t"]
    return None


def normalise(raw: dict, timescale: int) -> Observed:
    """bin/players/behaviour.mjs's record of one job -> Observed in 1/timescale s,
    on the session clock: its origin is the first frame (`origin`, or the
    adapter's `firstFrame`, or the first sample that shows something), and
    whatever happened before it is at 0. With no frame at all the origin is
    load() and `startup` is None."""
    k = timescale / 1000.0
    samples_raw = (raw.get("observation") or {}).get("samples", [])
    ff = raw.get("startupMs")
    if ff is None and raw.get("origin") is not None:
        ff = raw["origin"] - raw["t0"]
    if ff is None:
        ff = (raw.get("observation") or {}).get("firstFrame")
    if ff is None:
        ff = first_frame(samples_raw)
    obs = Observed(startup=ff)
    ff = ff or 0
    t0 = raw["t0"] + ff
    for r in raw.get("requests", []):
        at = max(0.0, (r["wall"] - t0) * k)
        if r.get("kind") in ("aps", "document"):
            obs.requests.append({"at": at, "url": r["url"], "fixture": r.get("fixture"), "kind": r["kind"],
                                 "status": r.get("status")})
        elif r.get("kind") == "other":
            obs.others.append({"at": at, "url": r["url"], "resourceType": r.get("resourceType")})
    obs.requests.sort(key=lambda r: r["at"])
    obs.others.sort(key=lambda r: r["at"])
    for s in samples_raw:
        ss = {"t": max(0.0, (s["t"] - ff) * k), "layout": s.get("layout", "none"), "elements": []}
        for e in s.get("elements", []):
            e = dict(e)
            if "time" in e:
                e["time"] = e["time"] * k
            ss["elements"].append(e)
        if s.get("seek"):
            ss["seek"] = {"from": s["seek"]["from"] * k, "to": s["seek"]["to"] * k}
        obs.samples.append(ss)
    obs.samples.sort(key=lambda s: s["t"])
    obs.actions = [dict(a) for a in raw.get("actions", [])]
    obs.destinations = [{"at": max(0.0, (d["t"] - ff) * k), "uri": d["uri"]}
                        for d in (raw.get("observation") or {}).get("destinations", [])]
    return obs


class Fixtures:
    """The vector's documents: URL -> fixture path, and the texts."""

    def __init__(self, urls: dict, texts: dict):
        self.urls = urls        # fixture path -> URL it is served at (the entry included)
        self.texts = texts      # fixture path -> text

    def of(self, url: str | None) -> str | None:
        if not url:
            return None
        for path, u in self.urls.items():
            if same_url(u, url):
                return path
        for path, u in self.urls.items():
            if added_query(u, url) is not None:
                return path
        return None


# --------------------------------------------------------------------------- identities

def cand_matches(exp: dict, el: dict, fx: Fixtures) -> bool:
    if fx.of(el.get("doc")) != exp["fixture"]:
        return False
    if "id" in exp:
        return el.get("candidateId") == exp["id"]
    return str(el.get("candidateIndex")) == str(exp["index"])


def opt_matches(exp, el: dict) -> bool:
    if exp is None:
        return "optionId" not in el and "optionIndex" not in el
    if "id" in exp:
        return el.get("optionId") == exp["id"]
    return str(el.get("optionIndex")) == str(exp["index"])


def element_matches(exp: dict, el: dict, fx: Fixtures) -> bool:
    if exp["element"] != el.get("element"):
        return False
    if exp["element"] == "primary":
        return True
    # An `ad` always names its candidate and option (the schema requires
    # both); a `background` may name neither, and then any background matches.
    if "candidate" in exp and not cand_matches(exp["candidate"], el, fx):
        return False
    return "option" not in exp or opt_matches(exp["option"], el)


def shows_match(exp_shows: list, obs_elements: list, fx: Fixtures) -> bool:
    left = list(obs_elements)
    for e in exp_shows:
        hit = next((o for o in left if element_matches(e, o, fx)), None)
        if hit is None:
            return False
        left.remove(hit)
    return not left


def _ident_el(el: dict) -> tuple:
    return tuple((k, str(el.get(k))) for k in ("element", "doc", "candidateId", "candidateIndex",
                                                "optionId", "optionIndex", "opportunityDoc",
                                                "opportunityEvent") if k in el)


def describe_obs(layout: str, elements: list, fx: Fixtures) -> str:
    parts = []
    for e in elements:
        if e.get("element") == "primary":
            parts.append("primary" + (" (paused)" if e.get("paused") else ""))
        else:
            c = e.get("candidateId") or f"#{e.get('candidateIndex')}"
            o = e.get("optionId") or (f"#{e['optionIndex']}" if "optionIndex" in e else "null")
            parts.append(f"{e.get('element')} {fx.of(e.get('doc')) or e.get('doc')}:{c} option {o}")
    return f"{layout} [{', '.join(parts) or 'nothing'}]"


def describe_exp(seg: dict) -> str:
    parts = []
    for e in seg["shows"]:
        if e["element"] == "primary":
            parts.append(f"primary from {fmt_when(e['from'])}")
        elif "candidate" not in e:
            parts.append(e["element"])
        else:
            c = e["candidate"]
            cid = c.get("id") or f"#{c.get('index')}"
            desc = f"{e['element']} {c['fixture']}:{cid}"
            if "option" in e:
                o = e["option"]
                desc += " option " + ("null" if o is None else (o.get("id") or f"#{o.get('index')}"))
            parts.append(desc)
    return f"{seg['layout']} [{', '.join(parts) or 'nothing'}]"


# --------------------------------------------------------------------------- verdicts

def _verdict(problems: list, unverifiable: list, passed: str) -> tuple[Outcome, str]:
    if problems:
        more = f" (+{len(problems) - MAX_PROBLEMS} more)" if len(problems) > MAX_PROBLEMS else ""
        return Outcome.FAIL, "; ".join(problems[:MAX_PROBLEMS]) + more
    if unverifiable:
        return Outcome.NOT_VERIFIABLE, "; ".join(unverifiable[:MAX_PROBLEMS])
    return Outcome.PASS, passed


def _http_url(text: str) -> str | None:
    """`GET <target> HTTP/1.1` + `Host:` of a request fixture -> its URL."""
    lines = text.splitlines()
    if not lines:
        return None
    parts = lines[0].split()
    if len(parts) < 2:
        return None
    host = next((ln.split(":", 1)[1].strip() for ln in lines[1:] if ln.lower().startswith("host:")), None)
    return f"https://{host}{parts[1]}" if host else None


def query_ok(added: dict, want: dict, extra: str | None) -> bool:
    """`added` holds exactly the parameters of `want`, with their values, plus
    only names `extra` (a regular expression, matched against the whole name)
    admits."""
    if any(added.get(k) != v for k, v in want.items()):
        return False
    rest = [k for k in added if k not in want]
    return all(extra is not None and re.fullmatch(extra, k) for k in rest)


def compare_requests(expected: list, obs: Observed, tol: float, fx: Fixtures,
                     entry: str | None = None) -> tuple[Outcome, str]:
    """Each expected document request is matched to one observed request with
    the URL it declares (its query a subset), exactly the parameters `query`
    lists added (none when absent) plus any whose name `extra_query_pattern`
    matches in full, the time within its tolerance, the fixture `answered_by`
    served (none when absent) and, with `matches`, the request URL equal to
    the `.http` one. Every observed document request must be matched: one more
    is a FAIL. The main MPD (`entry`) is given to the Player, not requested by
    it: its requests are not compared."""
    problems, unverifiable, used = [], [], set()
    for j, o in enumerate(obs.requests):
        if entry is not None and fx.of(o["url"]) == entry:
            used.add(j)
    for i, e in enumerate(expected):
        want_q = {k: str(v) for k, v in (e.get("query") or {}).items()}
        http = None
        if e.get("matches"):
            text = fx.texts.get(e["matches"])
            http = _http_url(text) if text else None
            if http is None:
                unverifiable.append(f"requests[{i}]: the request fixture {e['matches']} cannot be read")
        tried = []
        hit = None
        for j, o in enumerate(obs.requests):
            if j in used:
                continue
            q = added_query(e["url"], o["url"])
            if q is None:
                continue
            ok = (query_ok(q, want_q, e.get("extra_query_pattern")) and within(o["at"], e["at"], tol_of(e, tol))
                  and o.get("fixture") == e.get("answered_by")
                  and (http is None or same_url(http, o["url"])))
            if ok:
                hit = j
                break
            tried.append(o)
        if hit is not None:
            used.add(hit)
            continue
        if not tried:
            problems.append(f"requests[{i}] {e['url']} at {fmt_when(e['at'])}: not observed")
        else:
            o = tried[0]
            got = added_query(e["url"], o["url"])
            problems.append(
                f"requests[{i}] {e['url']} expected at {fmt_when(e['at'])}, query {want_q}, answered_by "
                f"{e.get('answered_by')}" + (f", matching {e['matches']}" if e.get("matches") else "")
                + f"; observed {o['url']} at {_r(o['at'])}, query {got}, answered_by {o.get('fixture')}")
    for j, o in enumerate(obs.requests):
        if j not in used:
            problems.append(f"unexpected request {o['url']} at {_r(o['at'])} (answered_by {o.get('fixture')})")
    n = len(expected)
    return _verdict(problems, unverifiable, f"{n} request(s) as expected" if n else "no document request, as expected")


# ----------------------------------------------------------------- beacons

def _root(fx: Fixtures, path: str):
    text = fx.texts.get(path)
    if text is None:
        return None
    try:
        return ET.fromstring(text.encode("utf-8"))
    except ET.ParseError:
        return None


def _local(el) -> str:
    return el.tag.split("}")[-1] if isinstance(el.tag, str) else ""


def candidates_of(root) -> list:
    """A document's candidates in document order: the Periods of an MPD, the
    Ads of an OverlayList (as bin/check-scenarios.py's Doc reads them)."""
    return [e for e in root if _local(e) in ("Period", "Ad")]


def candidate_of(root, ref: dict):
    cs = candidates_of(root)
    if "id" in ref:
        return next((c for c in cs if c.get("id") == ref["id"]), None)
    return cs[ref["index"] - 1] if 1 <= ref["index"] <= len(cs) else None


def clickthroughs(root) -> list:
    return [e for e in root.iter() if _local(e) == "ClickThrough"]


def click_urls(fx: Fixtures) -> tuple[set, set]:
    """(every click-tracking URL, every destination URI) the fixtures declare
    on a ClickThrough."""
    track, dest = set(), set()
    for path in fx.texts:
        root = _root(fx, path)
        if root is None:
            continue
        for ct in clickthroughs(root):
            track.update(u for u in (ct.get("trackingUris") or "").split() if u.startswith(("http://", "https://")))
            if ct.get("uri"):
                dest.add(ct.get("uri"))
    return track, dest


def beacon_urls(fx: Fixtures) -> set:
    """Every URL a fixture declares as a beacon: an Event's text in any
    EventStream, and each URL of a `trackingUris` attribute."""
    out = set()
    for text in fx.texts.values():
        try:
            root = ET.fromstring(text.encode("utf-8"))
        except ET.ParseError:
            continue
        for es in root.iter():
            if not (isinstance(es.tag, str) and es.tag.endswith("}EventStream")):
                continue
            for ev in es:
                t = (ev.text or "").strip()
                if t.startswith(("http://", "https://")):
                    out.add(t)
        for e in root.iter():
            for k, v in e.attrib.items():
                if k.split("}")[-1] == "trackingUris":
                    out.update(u for u in v.split() if u.startswith(("http://", "https://")))
    return out


def beacon_url_of(exp: dict, fx: Fixtures) -> str | None:
    """The URL of an expected beacon: its `url`, or the text of the Event with
    its @id in its fixture (inside its candidate's Period when it names one)."""
    if exp.get("url"):
        return exp["url"]
    text = fx.texts.get(exp["fixture"])
    if text is None:
        return None
    try:
        root = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError:
        return None
    scopes = [root]
    cand = exp.get("candidate")
    if cand:
        c = candidate_of(root, cand)
        scopes = [c] if c is not None else []
    hits = [((ev.text or "").strip()) for sc in scopes for ev in sc.iter()
            if isinstance(ev.tag, str) and ev.tag.endswith("}Event") and ev.get("id") == exp["id"]]
    hits = [h for h in hits if h]
    return hits[0] if len(hits) == 1 else None


def compare_beacons(expected: list, obs: Observed, tol: float, fx: Fixtures,
                    clicks_judged: bool = False) -> tuple[Outcome, str]:
    """Each expected beacon is matched to one observed request to its URL
    (query order aside) within its time; a beacon URL some fixture declares,
    or one an expected beacon has, observed and not matched is an unexpected
    beacon. Other requests (an image, an unknown host) are not beacons. When
    the outcome judges clicks (`clicks_judged`), a ClickThrough's
    click-tracking URLs are the clicks field's and not beacons."""
    problems, unverifiable, used = [], [], set()
    known = beacon_urls(fx)
    if clicks_judged:
        known -= click_urls(fx)[0]
    for i, e in enumerate(expected):
        url = beacon_url_of(e, fx)
        if url is None:
            unverifiable.append(f"beacons[{i}] {e['fixture']} @id {e['id']}: no URL, and no single Event "
                                "with that @id to read it from")
            continue
        known.add(url)
        same = [(j, o) for j, o in enumerate(obs.others) if j not in used and same_url(url, o["url"])]
        hit = next((j for j, o in same if within(o["at"], e["at"], tol_of(e, tol))), None)
        if hit is not None:
            used.add(hit)
            continue
        seen = ", ".join(str(_r(o["at"])) for _, o in same) or "never"
        problems.append(f"beacons[{i}] {url} (@id {e['id']}) expected at {fmt_when(e['at'])}; observed at {seen}")
    for j, o in enumerate(obs.others):
        if j not in used and any(same_url(k, o["url"]) for k in known):
            if unverifiable:   # it may be the beacon whose URL could not be read
                unverifiable.append(f"beacon {o['url']} at {_r(o['at'])} not matched, and an expected one has no URL")
            else:
                problems.append(f"unexpected beacon {o['url']} at {_r(o['at'])}")
    n = len(expected)
    return _verdict(problems, unverifiable, f"{n} beacon(s) as expected" if n else "no beacon, as expected")


# ----------------------------------------------------------------- clicks

def _clickthrough_of(exp: dict, fx: Fixtures):
    root = _root(fx, exp["fixture"])
    if root is None:
        return None
    c = candidate_of(root, exp["candidate"])
    cts = clickthroughs(c) if c is not None else []
    return cts[0] if len(cts) == 1 else None


def compare_clicks(expected: list, obs: Observed, tol: float, fx: Fixtures) -> tuple[Outcome, str]:
    """Each expected click-tracking fire is matched to one observed request to
    its `url` (query order aside) within its time, the `url` being one of the
    candidate's ClickThrough@trackingUris. A click-tracking URL some fixture
    declares, observed and not matched, is an unexpected click."""
    problems, unverifiable, used = [], [], set()
    known = click_urls(fx)[0]
    for i, e in enumerate(expected):
        ct = _clickthrough_of(e, fx)
        if ct is None or e["url"] not in (ct.get("trackingUris") or "").split():
            unverifiable.append(f"clicks[{i}] {e['url']}: not a trackingUris URL of a single ClickThrough "
                                f"of that candidate in {e['fixture']}")
            continue
        same = [(j, o) for j, o in enumerate(obs.others) if j not in used and same_url(e["url"], o["url"])]
        hit = next((j for j, o in same if within(o["at"], e["at"], tol_of(e, tol))), None)
        if hit is not None:
            used.add(hit)
            continue
        seen = ", ".join(str(_r(o["at"])) for _, o in same) or "never"
        problems.append(f"clicks[{i}] {e['url']} expected at {fmt_when(e['at'])}; observed at {seen}")
    for j, o in enumerate(obs.others):
        if j not in used and any(same_url(k, o["url"]) for k in known):
            problems.append(f"unexpected click-tracking {o['url']} at {_r(o['at'])}")
    n = len(expected)
    return _verdict(problems, unverifiable, f"{n} click-tracking fire(s) as expected" if n
                    else "no click-tracking, as expected")


def compare_destinations(expected: list, obs: Observed, tol: float, fx: Fixtures) -> tuple[Outcome, str]:
    """Each expected destination is the candidate's ClickThrough@uri made
    available within its time: a request to that URI (a page opened on it, in
    the Player's page or another one), or a shown node carrying
    `data-sgai-clickthrough` with it (its URL on screen). A ClickThrough URI
    some fixture declares, made available outside the time of every expected
    destination with that URI, is unexpected (the same destination both
    opened and shown at its time is not)."""
    problems, unverifiable, want = [], [], []
    seen = [("opened", o["at"], o["url"]) for o in obs.others] + \
           [("shown", d["at"], d["uri"]) for d in obs.destinations]
    used = set()
    known = click_urls(fx)[1]
    for i, e in enumerate(expected):
        ct = _clickthrough_of(e, fx)
        if ct is None or not ct.get("uri"):
            unverifiable.append(f"destinations[{i}]: no single ClickThrough with a @uri in that candidate of "
                                f"{e['fixture']}")
            continue
        uri = ct.get("uri")
        want.append((uri, e["at"], tol_of(e, tol)))
        same = [(j, x) for j, x in enumerate(seen) if j not in used and same_url(uri, x[2])]
        hit = next((j for j, x in same if within(x[1], e["at"], tol_of(e, tol))), None)
        if hit is not None:
            used.add(hit)
            continue
        got = ", ".join(f"{x[0]} at {_r(x[1])}" for _, x in same) or "never"
        problems.append(f"destinations[{i}] {uri} expected at {fmt_when(e['at'])}; observed: {got}")
    for j, x in enumerate(seen):
        if j in used or any(same_url(u, x[2]) and within(x[1], at, t) for u, at, t in want):
            continue
        if any(same_url(k, x[2]) for k in known):
            problems.append(f"unexpected destination {x[2]} {x[0]} at {_r(x[1])}")
    n = len(expected)
    return _verdict(problems, unverifiable, f"{n} destination(s) as expected" if n
                    else "no destination made available, as expected")


# ----------------------------------------------------------------- presentation

@dataclass
class Seg:
    start: float
    end: float
    layout: str
    elements: list
    ident: tuple
    paused: bool | None
    rate: float
    from_: float | None
    seek: bool = False


def _primary(elements: list) -> dict | None:
    return next((e for e in elements if e.get("element") == "primary"), None)


def observed_segments(samples: list, end: float, tol: float) -> tuple[list, float | None]:
    """The observed timeline as segments, and the startup (the time before
    anything was first shown, or None when nothing ever was). A segment ends
    when what is shown changes (layout, or a surface's identity), when the
    primary is paused or resumed, or when it is sought by more than the
    tolerance. A segment shorter than the tolerance is a transition, folded
    into its neighbours. The leading stretch with nothing shown is the
    Player starting up: the first segment is taken to start at 0."""
    segs: list[Seg] = []
    for s in samples:
        if s["t"] > end:
            break
        els = s["elements"]
        p = _primary(els)
        ident = (s["layout"], tuple(sorted(_ident_el(e) for e in els)))
        paused = p.get("paused") if p else None
        seek = bool(s.get("seek")) and abs(s["seek"]["to"] - s["seek"]["from"]) > tol
        if not segs or ident != segs[-1].ident or paused != segs[-1].paused or seek:
            if segs:
                segs[-1].end = s["t"]
            segs.append(Seg(s["t"], end, s["layout"], els, ident, paused,
                            (p.get("rate") or 1.0) if p else 1.0, p.get("time") if p else None, seek))
    if segs:
        segs[-1].end = end
    startup = None
    while segs and not segs[0].elements:
        startup = segs[0].end
        segs.pop(0)
    if not segs:
        return [], None
    startup = segs[0].start if startup is None else startup
    segs[0].start = 0
    # Fold transitions: a segment shorter than the tolerance goes to the one
    # before it (the first, to the one after); a seek it carried moves on.
    out: list[Seg] = []
    carry_start, carry_seek = None, False
    for sg in segs:
        if sg.end - sg.start < tol and len(segs) > 1:
            if out:
                out[-1].end = sg.end
            elif carry_start is None:
                carry_start = sg.start
            carry_seek = carry_seek or sg.seek
            continue
        if carry_start is not None:
            sg.start, carry_start = carry_start, None
        sg.seek, carry_seek = sg.seek or carry_seek, False
        if out and sg.ident == out[-1].ident and sg.paused == out[-1].paused and not sg.seek:
            out[-1].end = sg.end
            continue
        out.append(sg)
    if not out:          # every segment was a transition: keep the longest
        out = [max(segs, key=lambda s: s.end - s.start)]
        out[0].start, out[0].end = 0, end
    return out, startup


def _rate_at(t: float, actions: list, timescale: int) -> float:
    rate = 1.0
    for a in sorted(actions, key=lambda a: a["at"]):
        if a["do"] == "rate" and a["at"] <= t:
            rate = float(a["rate"])
    return rate


def _silent(prev: dict, nxt: dict, actions: list, timescale: int) -> bool:
    """A written boundary with nothing to observe: same layout and surfaces on
    both sides, and a primary that keeps playing across it at the rate the
    actions set. A boundary written as a window is never silent."""
    if prev["layout"] != nxt["layout"] or isinstance(nxt["start"], dict) or isinstance(prev["start"], dict):
        return False
    def idents(seg):
        return sorted(json.dumps({k: v for k, v in e.items() if k not in ("from", "region")}, sort_keys=True)
                      for e in seg["shows"])
    if idents(prev) != idents(nxt):
        return False
    pa = next((e for e in prev["shows"] if e["element"] == "primary"), None)
    pb = next((e for e in nxt["shows"] if e["element"] == "primary"), None)
    if pa is None and pb is None:
        return True
    if isinstance(pa["from"], dict) or isinstance(pb["from"], dict):
        return False
    rate = _rate_at(prev["start"], actions, timescale)
    return pb["from"] == pa["from"] + (prev["end"] - prev["start"]) * rate


def compare_presentation(expected: list, obs: Observed, end: float, tol: float, fx: Fixtures,
                         actions: list, timescale: int) -> tuple[Outcome, str]:
    """The written segments against the observed ones. Every change observed
    must be a written boundary within its tolerance (the segment's own, else
    the vector's), or inside the window a boundary written `{from, to}` gives;
    every written boundary must be observed, except one across which nothing
    observable changes (same surfaces, a primary playing on: `_silent`). Each
    written segment must show its layout and exactly its surfaces, and a
    primary the main-presentation time `from` at the segment's start, within
    that tolerance (or inside `from` when it is a window). `region` and `note`
    are for a person and not compared."""
    segs, startup = observed_segments(obs.samples, end, tol)
    if obs.startup is not None:
        startup = obs.startup
    if not segs:
        return Outcome.FAIL, "presentation: nothing was ever shown on screen"
    problems = []
    eb = [(expected[i]["start"], _silent(expected[i - 1], expected[i], actions, timescale), i,
           tol_of(expected[i], tol)) for i in range(1, len(expected))]
    matched: dict[int, int] = {}
    for j in range(1, len(segs)):
        t = segs[j].start
        cands = [(dist(t, bt), i) for bt, _, i, bt_tol in eb if i not in matched and dist(t, bt) <= bt_tol]
        if cands:
            matched[min(cands)[1]] = j
        else:
            problems.append(f"observed a change at {_r(t)} from {describe_obs(segs[j - 1].layout, segs[j - 1].elements, fx)}"
                            f" to {describe_obs(segs[j].layout, segs[j].elements, fx)}, which the vector does not have")
    for bt, silent, i, bt_tol in eb:
        if not silent and i not in matched:
            here = _seg_at(segs, lo(bt))
            problems.append(f"presentation[{i}] expected a change at {fmt_when(bt)} to {describe_exp(expected[i])}; "
                            f"none observed within {bt_tol:g} (on screen: "
                            f"{describe_obs(here.layout, here.elements, fx)} from {_r(here.start)})")
    for i, e in enumerate(expected):
        if i in matched:
            sg, at_start = segs[matched[i]], True
        else:
            sg = _seg_at(segs, lo(e["start"]))
            at_start = i == 0
        if sg.layout != e["layout"] or not shows_match(e["shows"], sg.elements, fx):
            problems.append(f"presentation[{i}] {fmt_when(e['start'])}..{fmt_when(e['end'])} expected "
                            f"{describe_exp(e)}; observed {describe_obs(sg.layout, sg.elements, fx)} "
                            f"from {_r(sg.start)} to {_r(sg.end)}")
            continue
        pe = next((x for x in e["shows"] if x["element"] == "primary"), None)
        if pe is not None and sg.from_ is not None:
            got = sg.from_ if at_start else _primary_time_at(obs.samples, lo(e["start"]))
            if got is None or not within(got, pe["from"], tol_of(e, tol)):
                problems.append(f"presentation[{i}] primary from expected {fmt_when(pe['from'])}, "
                                f"observed {None if got is None else _r(got)}")
    detail = (f"{len(expected)} segment(s) as expected; startup {_r(startup)} before the first frame"
              if not problems else "")
    out, d = _verdict(problems, [], detail)
    if out is Outcome.FAIL:
        d += f" [startup {_r(startup)}; observed: " + "; ".join(
            f"{_r(s.start)}..{_r(s.end)} {describe_obs(s.layout, s.elements, fx)}"
            + (f" from {_r(s.from_)}" if s.from_ is not None else "") for s in segs[:8]) + "]"
    return out, d


def _primary_time_at(samples: list, t: float) -> float | None:
    """The primary's media time at session time `t`: the last sample at or
    before `t` (the adapter samples at least every 500 ms), advanced at its
    rate unless paused."""
    last = None
    for s in samples:
        if s["t"] > t:
            break
        p = _primary(s["elements"])
        if p is not None and p.get("time") is not None:
            last = (s["t"], p)
    if last is None:
        return None
    st, p = last
    return p["time"] + (0 if p.get("paused") else (t - st) * (p.get("rate") or 1.0))


def _seg_at(segs: list, t: float) -> Seg:
    for s in segs:
        if s.start <= t < s.end:
            return s
    return segs[-1]


# ----------------------------------------------------------------- selection

def compare_selection(expected: list, obs: Observed, fx: Fixtures) -> tuple[Outcome, str]:
    """Per opportunity, the ad surfaces observed (attributed by their
    `data-sgai-opportunity-*`), distinct by candidate, option and the layout
    on screen, in order of first appearance, against `presented`. `declined`
    and `ignored` both expect nothing presented; which of the two it was is
    the requests field's to tell. An ad surface with no opportunity, or for
    an opportunity the vector does not list, is a FAIL."""
    seen: dict = {}
    for s in obs.samples:
        for e in s["elements"]:
            if e.get("element") != "ad":
                continue
            key = (fx.of(e.get("opportunityDoc")) or e.get("opportunityDoc"), e.get("opportunityEvent"))
            entry = (_ident_el(e), s["layout"])
            lst = seen.setdefault(key, [])
            if entry not in [(_ident_el(x), lay) for x, lay in lst]:
                lst.append((e, s["layout"]))
    problems = []
    keys = set()
    for i, sel in enumerate(expected):
        key = (sel["opportunity"]["fixture"], str(sel["opportunity"]["event_id"]))
        keys.add(key)
        got = seen.get(key, [])
        want = sel["presented"] if sel["result"] == "presented" else []
        ok = len(got) == len(want) and all(
            lay == w["layout"] and cand_matches(w["candidate"], el, fx) and opt_matches(w.get("option"), el)
            for (el, lay), w in zip(got, want))
        if not ok:
            g = ", ".join(describe_obs(lay, [el], fx) for el, lay in got) or "nothing"
            w = ", ".join(f"{x['layout']} {x['candidate']['fixture']}:{x['candidate'].get('id') or '#' + str(x['candidate'].get('index'))}"
                          f" option {_opt(x['option'])}" for x in want) or "nothing"
            problems.append(f"selection[{i}] event {key[1]} of {key[0]} ({sel['result']}): expected {w}; observed {g}")
    for key, lst in seen.items():
        if key not in keys:
            problems.append(f"ad presented for an opportunity the vector does not list: {key} "
                            f"({', '.join(describe_obs(lay, [el], fx) for el, lay in lst)})")
    n = len(expected)
    return _verdict(problems, [], f"{n} opportunit(y/ies) as expected" if n else "no opportunity, as expected")


# ----------------------------------------------------------------- geometry

def _opt(o) -> str:
    return "null" if o is None else (o.get("id") or f"#{o.get('index')}")


def _union(rects: list) -> dict | None:
    if not rects:
        return None
    x0 = min(r["x"] for r in rects)
    y0 = min(r["y"] for r in rects)
    x1 = max(r["x"] + r["width"] for r in rects)
    y1 = max(r["y"] + r["height"] for r in rects)
    return {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}


def _edges_ok(want: dict, got: dict | None, tol: float) -> bool:
    if got is None:
        return False
    we = (want["x"], want["y"], want["x"] + want["width"], want["y"] + want["height"])
    ge = (got["x"], got["y"], got["x"] + got["width"], got["y"] + got["height"])
    return all(abs(a - b) <= tol + 1e-9 for a, b in zip(we, ge))


def _rects(sample: dict) -> tuple:
    p = _primary(sample["elements"])
    ad = _union([e["rect"] for e in sample["elements"] if e.get("element") == "ad"])
    return (p["rect"] if p else None), ad


def compare_geometry(expected: list, obs: Observed, tol_t: float) -> tuple[Outcome, str]:
    """At each `at`, the primary's rectangle and the bounding box of the shown
    `ad` surfaces (a `background` is not part of it), each edge within the
    entry's `tolerance` in percentage points. A state in effect anywhere in
    [at - tolerance, at + tolerance] of the session clock may satisfy it, so
    an instant on a transition is judged on either side of it."""
    problems = []
    for i, g in enumerate(expected):
        lo, hi = g["at"] - tol_t, g["at"] + tol_t
        states = [s for s in obs.samples if lo <= s["t"] <= hi]
        before = [s for s in obs.samples if s["t"] < lo]
        if before:
            states.insert(0, before[-1])
        ok = False
        for s in states:
            prim, ad = _rects(s)
            if ("primary" not in g or _edges_ok(g["primary"], prim, g["tolerance"])) and \
               ("ad" not in g or _edges_ok(g["ad"], ad, g["tolerance"])):
                ok = True
                break
        if not ok:
            at = [s for s in obs.samples if s["t"] <= g["at"]]
            prim, ad = _rects(at[-1]) if at else (None, None)
            want = {k: g[k] for k in ("primary", "ad") if k in g}
            problems.append(f"geometry[{i}] at {g['at']} expected {want} (±{g['tolerance']} pp); "
                            f"observed primary {prim}, ad {ad}")
    return _verdict(problems, [], f"{len(expected)} instant(s) as expected")


# --------------------------------------------------------------------------- one job

def fields_of(outcome: dict) -> list[str]:
    """The fields an outcome expects, each one Result."""
    fields = ["requests", "selection", "presentation"]
    if any("audio" in s for s in outcome["presentation"]):
        fields.append("audio")
    fields.append("beacons")
    if "clicks" in outcome:
        fields += ["clicks", "destinations"]
    if outcome.get("geometry"):
        fields.append("geometry")
    return fields


def compare(vector: dict, outcome: dict, raw: dict, fx: Fixtures, subject: str,
            actions: list) -> list[Result]:
    """One Result per expected field. `actions` are the actions of the run
    (the vector's or its variant's), in vector units."""
    ts, tol = vector["timescale"], vector["tolerance"]
    fields = fields_of(outcome)
    if not raw or not raw.get("ok") or raw.get("t0") is None:
        why = "no result from the harness" if not raw else raw.get("harnessError") or "the run did not start"
        return [Result(f, Outcome.NOT_VERIFIABLE, subject, detail=why) for f in fields]
    obs = normalise(raw, ts)
    out = []
    for f in fields:
        if f == "requests" and outcome.get("requests_not_compared"):
            o, d = Outcome.NOT_APPLICABLE, f"requests not compared: {outcome['requests_not_compared']}"
        elif f == "requests":
            o, d = compare_requests(outcome["requests"], obs, tol, fx, vector.get("entry"))
        elif f == "selection":
            o, d = compare_selection(outcome["selection"], obs, fx)
        elif f == "presentation":
            o, d = compare_presentation(outcome["presentation"], obs, vector["observe_until"], tol, fx,
                                        actions, ts)
        elif f == "audio":
            o, d = Outcome.NOT_VERIFIABLE, "the observation carries no audio state: what is heard is not measured"
        elif f == "beacons":
            o, d = compare_beacons(outcome["beacons"], obs, tol, fx, "clicks" in outcome)
        elif f == "clicks":
            o, d = compare_clicks(outcome["clicks"], obs, tol, fx)
        elif f == "destinations":
            o, d = compare_destinations(outcome.get("destinations") or [], obs, tol, fx)
        else:
            o, d = compare_geometry(outcome["geometry"], obs, tol)
        out.append(Result(f, o, subject, detail=d))
    return out
