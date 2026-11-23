"""The checks of the level-2 catalogue. Each is f(rule, ctx, subject) and is
bound to its Rule in catalog.py. A FAIL always carries the place: an XPath
into the document, a query parameter of a request, or a path into the
extension schema.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from functools import lru_cache

from lxml import etree

from ..ext import readable_path
from ..model import Outcome
from . import vocab as V
from .vocab import q

PASS, FAIL, NA, NV = Outcome.PASS, Outcome.FAIL, Outcome.NOT_APPLICABLE, Outcome.NOT_VERIFIABLE


@lru_cache(maxsize=256)
def parse(text: str):
    return etree.fromstring(text.encode("utf-8"))


def ns(el) -> str:
    return etree.QName(el).namespace or ""


def local(el) -> str:
    return etree.QName(el).localname


def verdict(rule, where, fails, checked, what):
    """fails: [(element-or-path, detail)]. checked: how many things were looked at."""
    if fails:
        return [rule.result(FAIL, where, x if isinstance(x, str) else readable_path(x), d) for x, d in fails]
    if not checked:
        return [rule.result(NA, where, detail=f"no {what} in this document")]
    return [rule.result(PASS, where, detail=f"{checked} {what} checked")]


def windows(root):
    """(EventStream, Event, window element, family) for every SGAI window."""
    names = {q(v): k for k, v in V.WINDOW.items()}
    for stream in root.iter(q("EventStream", V.DASH)):
        for event in stream.findall(q("Event", V.DASH)):
            for w in event:
                if isinstance(w.tag, str) and w.tag in names:
                    yield stream, event, w, names[w.tag]


def tokens(value) -> list:
    return (value or "").split()


def percents(value):
    try:
        xs = [Decimal(x) for x in (value or "").split()]
    except InvalidOperation:
        return None
    return xs if len(xs) == 4 else None


def negative_duration(value) -> bool:
    return (value or "").strip().startswith("-")


def _win_names(*attrs):
    return [f"{e}@{a}" for e in V.WINDOW.values() for a in attrs]


# --- I-MPD -------------------------------------------------------------------------

def window_family(rule, ctx, b):
    """R40.9: a window's family is the family its event scheme names, and an
    Event of an SGAI scheme carries exactly one window of that family."""
    if (nv := V.need(rule, ctx, b.ref, *V.WINDOW.values())):
        return nv
    root, fails, n = parse(b.text), [], 0
    wnames = {q(v): k for k, v in V.WINDOW.items()}
    for stream in root.iter(q("EventStream", V.DASH)):
        scheme = stream.get("schemeIdUri", "")
        sgai = scheme.startswith(V.SGAI_SCHEME_PREFIX)
        for event in stream.findall(q("Event", V.DASH)):
            wins = [w for w in event if isinstance(w.tag, str) and w.tag in wnames]
            if not sgai:
                for w in wins:
                    fails.append((w, f"window element in an EventStream of scheme {scheme!r}, which is not an SGAI scheme"))
                continue
            n += 1
            fam = V.SCHEMES.get(scheme)
            if fam is None:
                fails.append((stream, f"SGAI scheme {scheme!r} names no family this catalogue knows"))
            elif len(wins) != 1:
                fails.append((event, f"{len(wins)} window elements in one Event of {scheme}; exactly one is needed"))
            elif wnames[wins[0].tag] != fam:
                fails.append((wins[0], f"<{local(wins[0])}> (family {wnames[wins[0].tag]}) in a stream of scheme {scheme} (family {fam})"))
    return verdict(rule, b.ref, fails, n, "SGAI window events")


def _range(family):
    def check(rule, ctx, b):
        fails, n = [], 0
        for _, event, w, fam in windows(parse(b.text)):
            if fam != family:
                continue
            n += 1
            if event.get("duration") is None:
                fails.append((event, f"{family} window declares no range: its Event has no @duration"))
        return verdict(rule, b.ref, fails, n, f"{family} windows")
    return check


overlay_range = _range("overlay")   # R40.9
pause_range = _range("pause")       # R31.1


def cap_declared(rule, ctx, b):
    """R4.1: every overlay and pause window declares its maximum duration."""
    if (nv := V.need(rule, ctx, b.ref, *_win_names(V.CAP))):
        return nv
    fails, n = [], 0
    for _, _, w, fam in windows(parse(b.text)):
        n += 1
        if w.get(V.CAP) is None:
            fails.append((w, f"{fam} window without @{V.CAP}"))
    return verdict(rule, b.ref, fails, n, "windows")


def clip_only_on_replacement(rule, ctx, b):
    """R4.6: `@clip` belongs to the inherited replacement; insertion has none,
    and neither does a window."""
    root, fails, n = parse(b.text), [], 0
    for el in root.iter(q("InsertPresentation", V.DASH)):
        n += 1
        if el.get("clip") is not None:
            fails.append((el, "@clip on an InsertPresentation: insertion has no @clip"))
    for _, _, w, fam in windows(root):
        n += 1
        if w.get("clip") is not None:
            fails.append((w, f"@clip on a {fam} window"))
    return verdict(rule, b.ref, fails, n, "insertion events and windows")


def layout_vocabulary(rule, ctx, b):
    """R12.2: a window's allowed layouts are tokens of the closed list."""
    if (nv := V.need(rule, ctx, b.ref, *_win_names(V.ALLOWED))):
        return nv
    fails, n = [], 0
    for _, _, w, fam in windows(parse(b.text)):
        if w.get(V.ALLOWED) is None:
            continue
        n += 1
        bad = [t for t in tokens(w.get(V.ALLOWED)) if t not in V.TOKENS]
        if bad:
            fails.append((w, f"@{V.ALLOWED} lists {', '.join(bad)}, outside the R12.2 tokens"))
    return verdict(rule, b.ref, fails, n, "windows declaring allowed layouts")


def custom_overlay_only(rule, ctx, b):
    """R39.1: `custom` applies only to overlay slots."""
    root, fails, n = parse(b.text), [], 0
    if b.kind == "overlay-list":
        if (nv := V.need(rule, ctx, b.ref, f"{V.LIST}@{V.FAMILY}", f"{V.OPTION}@{V.LAYOUT}")):
            return nv
        if root.get(V.FAMILY) != "pause":
            return verdict(rule, b.ref, [], 0, "pause-family document")
        for o in root.iter(q(V.OPTION)):
            n += 1
            if o.get(V.LAYOUT) == "custom":
                fails.append((o, "option with layout `custom` in a pause document"))
        return verdict(rule, b.ref, fails, n, "options of a pause document")
    if (nv := V.need(rule, ctx, b.ref, f"{V.WINDOW['pause']}@{V.ALLOWED}")):
        return nv
    for _, _, w, fam in windows(root):
        if fam != "pause":
            continue
        n += 1
        if "custom" in tokens(w.get(V.ALLOWED)):
            fails.append((w, "pause window lists `custom` in its allowed layouts"))
        if w.get(V.REGION) is not None:
            fails.append((w, f"pause window declares @{V.REGION}"))
    return verdict(rule, b.ref, fails, n, "pause windows")


def region_with_custom(rule, ctx, b):
    """R39.2: a custom region is declared by a Publisher that admits `custom`,
    which it does by listing it."""
    if (nv := V.need(rule, ctx, b.ref, f"{V.WINDOW['overlay']}@{V.REGION}")):
        return nv
    fails, n = [], 0
    for _, _, w, fam in windows(parse(b.text)):
        if w.get(V.REGION) is None:
            continue
        n += 1
        if "custom" not in tokens(w.get(V.ALLOWED)):
            fails.append((w, f"@{V.REGION} on a window whose allowed layouts do not list `custom`"))
    return verdict(rule, b.ref, fails, n, "windows declaring a custom region")


def _inside_viewport(rect):
    x, y, w, h = rect
    return all(0 <= v <= 100 for v in rect) and x + w <= 100 and y + h <= 100


def region_in_viewport(rule, ctx, b):
    """R39.2: the region is a rectangle of the viewport (x, y, width, height in percent)."""
    if (nv := V.need(rule, ctx, b.ref, f"{V.WINDOW['overlay']}@{V.REGION}")):
        return nv
    fails, n = [], 0
    for _, _, w, fam in windows(parse(b.text)):
        if w.get(V.REGION) is None:
            continue
        n += 1
        r = percents(w.get(V.REGION))
        if r is None or not _inside_viewport(r):
            fails.append((w, f"@{V.REGION}={w.get(V.REGION)!r} is not x y width height inside the 0-100% viewport"))
    return verdict(rule, b.ref, fails, n, "custom regions")


def pause_on_top_only(rule, ctx, b):
    """R40.1: a pause window declares only on top."""
    if (nv := V.need(rule, ctx, b.ref, f"{V.WINDOW['pause']}@{V.RELATION}")):
        return nv
    fails, n = [], 0
    for _, _, w, fam in windows(parse(b.text)):
        if fam != "pause":
            continue
        n += 1
        rel = w.get(V.RELATION)
        if rel is not None and rel != "on-top":
            fails.append((w, f"pause window declares @{V.RELATION}={rel!r}; only on-top is admitted"))
    return verdict(rule, b.ref, fails, n, "pause windows")


LINEAR = ("InsertPresentation", "ReplacePresentation")


def _linear_events(root):
    for stream in root.iter(q("EventStream", V.DASH)):
        evs = [e for e in stream.findall(q("Event", V.DASH))
               if any(isinstance(c.tag, str) and c.tag in (q(x, V.DASH) for x in LINEAR) for c in e)]
        if evs:
            yield stream, evs


def nothing_on_linear(rule, ctx, b):
    """R40.7: nothing of this specification is added to an inherited linear
    event, its Event or its EventStream."""
    root, fails, n = parse(b.text), [], 0
    for stream, evs in _linear_events(root):
        n += len(evs)
        own = [stream] + [x for e in evs for x in e.iter() if isinstance(x.tag, str)]
        for el in own:
            if ns(el).startswith(V.SGAI_NS_PREFIX):
                fails.append((el, f"<{local(el)}> of the extension namespace inside an inherited linear event"))
            for a in el.attrib:
                if a.startswith("{" + V.SGAI_NS_PREFIX):
                    fails.append((el, f"extension attribute {a} on <{local(el)}>"))
    return verdict(rule, b.ref, fails, n, "inherited linear events")


def one_stream_per_family(rule, ctx, b):
    """R20.2: one EventStream per SGAI scheme in a Period."""
    root, fails, n = parse(b.text), [], 0
    for period in root.iter(q("Period", V.DASH)):
        seen = {}
        for s in period.findall(q("EventStream", V.DASH)):
            scheme = s.get("schemeIdUri", "")
            if not scheme.startswith(V.SGAI_SCHEME_PREFIX):
                continue
            n += 1
            if scheme in seen:
                fails.append((s, f"second EventStream of {scheme} in this Period"))
            seen[scheme] = s
    return verdict(rule, b.ref, fails, n, "SGAI event streams")


def no_value_on_sgai_stream(rule, ctx, b):
    """R20.2: an EventStream carrying an SGAI scheme carries no @value."""
    root, fails, n = parse(b.text), [], 0
    for s in root.iter(q("EventStream", V.DASH)):
        if not s.get("schemeIdUri", "").startswith(V.SGAI_SCHEME_PREFIX):
            continue
        n += 1
        if s.get("value") is not None:
            fails.append((s, f"@value={s.get('value')!r} on an EventStream of an SGAI scheme"))
    return verdict(rule, b.ref, fails, n, "SGAI event streams")


def playlist_metric(rule, ctx, b):
    """R33.4: an MPD carrying pause windows requests PlayList through Metrics."""
    root = parse(b.text)
    pauses = [w for _, _, w, fam in windows(root) if fam == "pause"]
    if not pauses:
        return verdict(rule, b.ref, [], 0, "pause windows")
    for m in root.findall(q("Metrics", V.DASH)):
        if "PlayList" in re.split(r"[\s,]+", m.get("metrics", "")):
            return verdict(rule, b.ref, [], 1, "MPDs with pause windows")
    return verdict(rule, b.ref, [(root, f"{len(pauses)} pause window(s) and no Metrics requesting PlayList at MPD level")], 1, "")


def linear_has_no_dismissal(rule, ctx, b):
    """R35.8: a linear slot is governed by the base skip declaration; nothing
    of R35.1's carries dismissal on it."""
    if (nv := V.need(rule, ctx, b.ref, f"{V.LIST}@{V.DISMISS}")):
        return nv
    root, fails = parse(b.text), []
    if b.kind == "list-mpd":
        scope = [x for x in root.iter() if isinstance(x.tag, str)]
    else:
        scope = [x for _, evs in _linear_events(root) for e in evs for x in e.iter() if isinstance(x.tag, str)]
    for el in scope:
        for a in el.attrib:
            if etree.QName(a).localname == V.DISMISS:
                fails.append((el, f"@{V.DISMISS} on a linear slot"))
    return verdict(rule, b.ref, fails, len(scope), "elements of linear slots")


def no_reserved_in_url_template(rule, ctx, b):
    """R29.1: the reserved parameters are not expressed through the MPD's
    URL-parameter template mechanism."""
    root, fails, n = parse(b.text), [], 0
    for el in root.iter():
        if not isinstance(el.tag, str) or local(el) not in V.URL_TEMPLATE:
            continue
        n += 1
        for a, v in el.attrib.items():
            hit = [r for r in V.RESERVED if r in v]
            if hit:
                fails.append((el, f"@{etree.QName(a).localname} names reserved parameter(s) {', '.join(hit)}"))
        if el.text and any(r in el.text for r in V.RESERVED):
            fails.append((el, "content names a reserved parameter"))
    return verdict(rule, b.ref, fails, n, "URL-parameter template elements")


# --- I-REQ -------------------------------------------------------------------------

def reserved_set_closed(rule, ctx, r):
    """R29.1: the reserved parameters are those of the two tables, and no others."""
    fails = [(f"query parameter {k!r}", f"{k!r} is not one of the reserved parameters of R29.1")
             for k, _ in r.params if k.startswith("sgai-") and k not in V.RESERVED]
    return verdict(rule, r.ref, fails, len(r.params), "query parameters")


def param_values(name, ok, what):
    def check(rule, ctx, r):
        vals = [v for k, v in r.params if k == name and v != ""]
        fails = [(f"query parameter {name!r}", f"{name}={v!r}: {what}") for v in vals if not ok(v)]
        return verdict(rule, r.ref, fails, len(vals), f"{name!r} parameters")
    return check


def no_empty_reserved(rule, ctx, r):
    """R29.3: a reserved parameter with no value is omitted, never sent empty."""
    present = [(k, v) for k, v in r.params if k in V.RESERVED]
    fails = [(f"query parameter {k!r}", f"{k} sent with an empty value") for k, v in present if v.strip() == ""]
    return verdict(rule, r.ref, fails, len(present), "reserved parameters")


# --- I-RES -------------------------------------------------------------------------

def _options(root):
    return list(root.iter(q(V.OPTION)))


def candidate_has_option(rule, ctx, b):
    """R5.1: each candidate carries one or more presentation options."""
    if (nv := V.need(rule, ctx, b.ref, V.AD, V.OPTION)):
        return nv
    root, fails = parse(b.text), []
    ads = list(root.iter(q(V.AD)))
    for ad in ads:
        if ad.find(q(V.OPTION)) is None:
            fails.append((ad, "candidate with no presentation option"))
    return verdict(rule, b.ref, fails, len(ads), "candidates")


def option_layout_vocabulary(rule, ctx, b):
    """R12.3: no form metadata for a layout outside the enumerated set."""
    if (nv := V.need(rule, ctx, b.ref, f"{V.OPTION}@{V.LAYOUT}")):
        return nv
    opts = _options(parse(b.text))
    fails = [(o, f"@{V.LAYOUT}={o.get(V.LAYOUT)!r} is outside the R12.2 tokens")
             for o in opts if o.get(V.LAYOUT) not in V.TOKENS]
    return verdict(rule, b.ref, fails, len(opts), "options")


def admissible_mime(m: str) -> bool:
    m = (m or "").split(";")[0].strip().lower()
    if m == "image/svg+xml":            # OOS-4: SVG-as-payload is outside R15
        return False
    return m.startswith(("video/", "image/")) or m in ("application/dash+xml", "text/html")


def option_mime(rule, ctx, b):
    """R15.2: a creative's mimeType falls under video, image or HTML."""
    if (nv := V.need(rule, ctx, b.ref, f"{V.OPTION}@{V.MIME}")):
        return nv
    opts = _options(parse(b.text))
    fails = [(o, f"@{V.MIME}={o.get(V.MIME)!r} is not video, image or HTML") for o in opts if not admissible_mime(o.get(V.MIME))]
    return verdict(rule, b.ref, fails, len(opts), "options")


def non_av_duration(rule, ctx, b):
    """R19.3: an image or HTML form has no intrinsic media, so its duration
    on the presentation timeline is declared, and is not negative."""
    if (nv := V.need(rule, ctx, b.ref, f"{V.OPTION}@{V.DURATION}")):
        return nv
    fails, n = [], 0
    for o in _options(parse(b.text)):
        m = (o.get(V.MIME) or "").split(";")[0].strip().lower()
        if not (m.startswith("image/") or m == "text/html"):
            continue
        n += 1
        d = o.get(V.DURATION)
        if d is None:
            fails.append((o, f"{m} option declares no @{V.DURATION}"))
        elif negative_duration(d):
            fails.append((o, f"@{V.DURATION}={d!r} is negative"))
    return verdict(rule, b.ref, fails, n, "image or HTML options")


NON_AV = ("text/html", "application/xhtml+xml")


def non_av_not_as_mimetype(rule, ctx, b):
    """R24.1: a non-AV asset is not an AdaptationSet or Representation @mimeType."""
    root, fails, n = parse(b.text), [], 0
    for tag in ("AdaptationSet", "Representation"):
        for el in root.iter(q(tag, V.DASH)):
            n += 1
            m = (el.get("mimeType") or "").split(";")[0].strip().lower()
            if m.startswith("image/") or m in NON_AV:
                fails.append((el, f"non-AV asset as {tag}@mimeType={m!r}"))
    return verdict(rule, b.ref, fails, n, "AdaptationSets and Representations")


def _by_layout(layouts, attr, must, why):
    def check(rule, ctx, b):
        if (nv := V.need(rule, ctx, b.ref, f"{V.OPTION}@{attr}")):
            return nv
        fails, n = [], 0
        for o in _options(parse(b.text)):
            if o.get(V.LAYOUT) not in layouts:
                continue
            n += 1
            if (o.get(attr) is not None) != must:
                fails.append((o, f"option with layout {o.get(V.LAYOUT)!r} {'without' if must else 'with'} @{attr}: {why}"))
        return verdict(rule, b.ref, fails, n, f"options with layout {'/'.join(layouts)}")
    return check


background_required = _by_layout(("squeezeback-double-box-background",), V.BACKGROUND, True, "the token says the background is present")
background_forbidden = _by_layout(("squeezeback-double-box",), V.BACKGROUND, False, "the token says there is no background")
lshape_one_creative = _by_layout(V.L_SHAPES, V.BACKGROUND, False, "an L-shape or frame carries one creative and no third element")
custom_has_rect = _by_layout(("custom",), V.RECT, True, "a custom option carries its rectangle")


def rect_in_viewport(rule, ctx, b):
    """R39.4: the rectangle lies inside the region, which lies inside the viewport."""
    if (nv := V.need(rule, ctx, b.ref, f"{V.OPTION}@{V.RECT}")):
        return nv
    fails, n = [], 0
    for o in _options(parse(b.text)):
        if o.get(V.RECT) is None:
            continue
        n += 1
        r = percents(o.get(V.RECT))
        if r is None or not _inside_viewport(r):
            fails.append((o, f"@{V.RECT}={o.get(V.RECT)!r} extends beyond the viewport, so beyond any region"))
    return verdict(rule, b.ref, fails, n, "option rectangles")


def tracking_is_callback(rule, ctx, b):
    """R13.1: time-bound beacons are DASH callback events."""
    if (nv := V.need(rule, ctx, b.ref, V.TRACKING)):
        return nv
    ts = list(parse(b.text).iter(q(V.TRACKING)))
    fails = [(t, f"tracking carrier of scheme {t.get('schemeIdUri')!r}, not {V.CALLBACK}")
             for t in ts if t.get("schemeIdUri") != V.CALLBACK]
    return verdict(rule, b.ref, fails, len(ts), "tracking carriers")


def clickthrough_placement(rule, ctx, b):
    """R28.1: the ClickThrough of a candidate is carried in the carrier the
    specification defines: one per candidate, on the candidate."""
    if (nv := V.need(rule, ctx, b.ref, V.CLICK)):
        return nv
    root, fails = parse(b.text), []
    cts = list(root.iter(q(V.CLICK)))
    for c in cts:
        p = c.getparent()
        on_candidate = (p.tag == q(V.AD)) if b.kind == "overlay-list" else (
            p.tag == q("Period", V.DASH) and p.getparent() is root)
        if not on_candidate:
            fails.append((c, f"ClickThrough under <{local(p)}>, not on a candidate"))
        elif len(p.findall(q(V.CLICK))) > 1 and p.findall(q(V.CLICK))[0] is not c:
            fails.append((c, "second ClickThrough on one candidate"))
    return verdict(rule, b.ref, fails, len(cts), "ClickThrough carriers")


def _root_attr(attr, test, what, family=None):
    def check(rule, ctx, b):
        if (nv := V.need(rule, ctx, b.ref, f"{V.LIST}@{attr}")):
            return nv
        root = parse(b.text)
        if family and root.get(V.FAMILY) != family:
            return verdict(rule, b.ref, [], 0, f"{family}-family document")
        problem = test(root.get(attr))
        return verdict(rule, b.ref, [(root, problem)] if problem else [], 1, what)
    return check


exhaustion_declared = _root_attr(V.EXHAUSTED, lambda v: None if v is not None else
                                 f"pause document without @{V.EXHAUSTED}", "pause documents", family="pause")
dismissal_declared = _root_attr(V.DISMISS, lambda v: None if v is not None else
                                f"no @{V.DISMISS}: the APS declares dismissibility", "documents")
dismiss_delay = _root_attr(V.DISMISS, lambda v: f"@{V.DISMISS}={v!r} is a negative delay"
                           if v is not None and negative_duration(v) else None, "dismissal declarations")
valid_for = _root_attr(V.VALID, lambda v: f"@{V.VALID}={v!r} is negative"
                       if v is not None and negative_duration(v) else None, "usable-lifetime declarations")


# --- the specification's extension schema ---------------------------------------------

def _schema(rule, ctx):
    if not ctx.ext_text or V.schema_tree(ctx.ext_text) is None:
        return [rule.result(NV, "specification", detail="no parseable extension schema in the specification")]
    return []


def token_enumeration(rule, ctx, _):
    """R12.1: the accepted values are exactly the enumerated ones."""
    if (nv := _schema(rule, ctx) or V.need(rule, ctx, "specification", f"{V.OPTION}@{V.LAYOUT}", *_win_names(V.ALLOWED))):
        return nv
    fails, n = [], 0
    for el, at in [(V.OPTION, V.LAYOUT)] + [(w, V.ALLOWED) for w in V.WINDOW.values()]:
        decl = V.attribute(ctx.ext_text, el, at)
        vals = V.enumeration(ctx.ext_text, decl.get("type") or "")
        n += 1
        if vals is None:
            fails.append((decl, f"{el}@{at} has type {decl.get('type')!r}, not an enumeration of the extension schema"))
            continue
        missing = [t for t in V.TOKENS if t not in vals]
        extra = [t for t in vals if t not in V.TOKENS]
        if missing or extra:
            fails.append((decl, f"{el}@{at}: " + "; ".join(
                x for x in (missing and f"missing {', '.join(missing)}", extra and f"not in R12.2: {', '.join(extra)}") if x)))
    return verdict(rule, "specification", fails, n, "layout-token attributes of the extension schema")


def _schema_has(pairs, why):
    def check(rule, ctx, _):
        if (nv := _schema(rule, ctx) or V.need(rule, ctx, "specification", *{p.split("@")[0] for p in pairs})):
            return nv
        fails = []
        for p in pairs:
            el, _, at = p.partition("@")
            if at.startswith("<"):
                ok = V.child(ctx.ext_text, el, at[1:]) is not None
            else:
                ok = V.attribute(ctx.ext_text, el, at) is not None
            if not ok:
                fails.append((V.complex_type(ctx.ext_text, el), f"<{el}> cannot carry {at.lstrip('<')}: {why}"))
        return verdict(rule, "specification", fails, len(pairs), "carriers in the extension schema")
    return check


execute_once_carrier = _schema_has(_win_names(V.EXECUTE_ONCE),
                                   "context/06 carries the once-per-session declaration as @executeOnce on overlay and pause windows")
start_with_offset_carrier = _schema_has([f"{V.WINDOW['overlay']}@{V.START_WITH_OFFSET}"],
                                        "context/06 carries the late-execution offset as @startWithOffset on overlay windows")
earliest_carrier = _schema_has(_win_names(V.EARLIEST),
                               "context/06 carries the early-resolution offset as @earliestResolutionTimeOffset on overlay and pause windows")
option_tracking_carrier = _schema_has([f"{V.OPTION}@<{V.TRACKING}"],
                                      "context/06 attaches a beacon to one option by placing the candidate's tracking carrier on the option")


def metadata_elements(rule, ctx, _):
    """R23.1: the extension namespace defines AdSystem and AdTitle."""
    if (nv := _schema(rule, ctx)):
        return nv
    root = V.schema_tree(ctx.ext_text)
    have = {e.get("name") for e in root.findall(q("element", V.XS))}
    fails = [(root, f"no global element {m} in the extension namespace") for m in V.METADATA if m not in have]
    return verdict(rule, "specification", fails, len(V.METADATA), "metadata elements")
