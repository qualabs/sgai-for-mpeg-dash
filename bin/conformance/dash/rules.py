"""Level 1 catalog: sentences of ISO/IEC 23009-1:2026 a document must satisfy
and the schema cannot express (ADR 0049), plus the namespace item of
context/07 checked against context/06.

Every `quote` of a base-standard rule was found verbatim (whitespace
flattened) in the primary copy declared in context/00-normative-base.md. The
quote of a C07 rule is the sentence of context/06 or context/07 it rests on.

What is NOT here, because level 1 already has it:
  DR-2 (a foreign construct sits only where its parent's type opens a
       wildcard) is E-3; the §5.2.1 removal obligation it and DR-3 rest on is
       E-4. context/07 §1, §2 and §4 are E-3 and E-4 for the same reason.

Ids: DR-N for context/08, C07-N for context/07, K-N for the row of the
published DASH conformance audit whose quoted sentence the rule checks (the
audit is a source of sentences, never of verdicts). A letter separates two
sentences of one source.
"""
from __future__ import annotations

import re

from lxml import etree

from ..extract import DASH_NS, LIST_PROFILE, SGAI_NS, SPS_PROFILE
from ..model import Outcome, Result, Rule

STD = "ISO/IEC 23009-1:2026"
XLINK_NS = "http://www.w3.org/1999/xlink"
MPD_KINDS = ("mpd", "list-mpd", "sps-mpd")
D = "{%s}" % DASH_NS

INSERT_SCHEME = "urn:mpeg:dash:event:alternativeMPD:insert:2025"
REPLACE_SCHEME = "urn:mpeg:dash:event:alternativeMPD:replace:2025"
CALLBACK_SCHEME = "urn:mpeg:dash:event:callback:2015"
# IETF RFC 4337 §3 registers exactly these five media types.
RFC4337 = {"video/mp4", "audio/mp4", "application/mp4", "application/mpeg4-iod",
           "application/mpeg4-iod-xmt"}

# ---------------------------------------------------------------- helpers


def _root(block) -> etree._Element:
    return etree.XML(block.text.encode("utf-8"))


def _prefix(ns: str | None) -> str:
    if ns in (None, DASH_NS):
        return ""
    if ns == XLINK_NS:
        return "xlink:"
    if ns and ns.startswith("urn:svta:"):
        return "svta:"
    return "{%s}" % ns


def path(el: etree._Element, attr: str | None = None) -> str:
    """/MPD/Period[1]/EventStream[2], local names, DASH unprefixed."""
    steps = []
    while el is not None:
        q = etree.QName(el)
        parent = el.getparent()
        name = _prefix(q.namespace) + q.localname
        if parent is None:
            steps.append(name)
        else:
            same = [c for c in parent if isinstance(c.tag, str) and c.tag == el.tag]
            steps.append(f"{name}[{same.index(el) + 1}]")
        el = parent
    p = "/" + "/".join(reversed(steps))
    if attr is not None:
        q = etree.QName(attr)
        p += "/@" + _prefix(q.namespace) + q.localname
    return p


def _profiles(value: str | None) -> list[str]:
    return [p.strip() for p in (value or "").split(",") if p.strip()]


_DUR = re.compile(r"^-?P(?:(\d+(?:\.\d+)?)Y)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)D)?"
                  r"(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?$")


def is_zero_duration(value: str | None) -> bool:
    if value is None:
        return False
    m = _DUR.match(value.strip())
    return bool(m) and all(float(g or 0) == 0 for g in m.groups())


def _linked_or_remote(period) -> str:
    """Why a Period's content is not in the document, or ''."""
    if period.find(D + "ImportedMPD") is not None:
        return "a Linked Period (§5.3.2.6): its content arrives with the imported MPD"
    if period.get(f"{{{XLINK_NS}}}href") is not None:
        return "a remote Period (xlink:href, §5.5): its content arrives with resolution"
    return ""


def _verdict(rule: Rule, block, fails: list, checked: int, what: str) -> list[Result]:
    if fails:
        return fails
    if checked == 0:
        return [rule.result(Outcome.NOT_APPLICABLE, block.ref, detail=f"no {what} in this document")]
    return [rule.result(Outcome.PASS, block.ref, detail=f"{checked} {what} checked")]


def _mime_base(value: str) -> str:
    return re.split(r"[;\s]", value.strip(), maxsplit=1)[0].lower()


def _is_list_profile(root) -> bool:
    return LIST_PROFILE in _profiles(root.get("profiles"))


# ---------------------------------------------------------------- DR-1


def _sps_mime(rule):
    def check(ctx, block):
        root = _root(block)
        fails, n = [], 0
        for rep in root.iter(D + "Representation"):
            n += 1
            aset = rep.getparent()
            mime = rep.get("mimeType") or (aset.get("mimeType") if aset is not None else None)
            if mime is None:
                fails.append(rule.result(Outcome.FAIL, block.ref, path(rep),
                                         "Representation has no @mimeType, on it or on its AdaptationSet"))
            elif _mime_base(mime) not in RFC4337:
                where = rep if rep.get("mimeType") else aset
                fails.append(rule.result(Outcome.FAIL, block.ref, path(where, "mimeType"),
                                         f"@mimeType {mime!r} is not a type registered by IETF RFC 4337 "
                                         f"({', '.join(sorted(RFC4337))})"))
        return _verdict(rule, block, fails, n, "Representation")
    return check


def _attr_value(rule, attr, wanted, what):
    def check(ctx, block):
        root = _root(block)
        if root.get(attr) != wanted:
            return [rule.result(Outcome.FAIL, block.ref, path(root, attr),
                                f"MPD@{attr} is {root.get(attr)!r}; {what}")]
        return [rule.result(Outcome.PASS, block.ref, detail=f"MPD@{attr} is {wanted!r}")]
    return check


def _no_xlink(rule, scope):
    def check(ctx, block):
        root = _root(block)
        if scope == "list-profile" and not _is_list_profile(root):
            return [rule.result(Outcome.NOT_APPLICABLE, block.ref,
                                detail=f"{LIST_PROFILE} is not in MPD@profiles")]
        if scope == "type-list" and root.get("type") != "list":
            return [rule.result(Outcome.NOT_APPLICABLE, block.ref, detail="MPD@type is not \"list\"")]
        fails = []
        for el in root.iter():
            if not isinstance(el.tag, str):
                continue
            for a in el.attrib:
                if etree.QName(a).namespace == XLINK_NS:
                    fails.append(rule.result(Outcome.FAIL, block.ref, path(el, a),
                                             f"XLink attribute {etree.QName(a).localname} present"))
        return fails or [rule.result(Outcome.PASS, block.ref, detail="no XLink attribute")]
    return check


def _one_period(rule):
    def check(ctx, block):
        root = _root(block)
        ps = root.findall(D + "Period")
        if len(ps) != 1:
            return [rule.result(Outcome.FAIL, block.ref, "/MPD/Period",
                                f"{len(ps)} Period elements; exactly one is required")]
        return [rule.result(Outcome.PASS, block.ref, detail="one Period")]
    return check


def _absent_attr(rule, attr):
    def check(ctx, block):
        root = _root(block)
        if root.get(attr) is not None:
            return [rule.result(Outcome.FAIL, block.ref, path(root, attr), f"MPD@{attr} is present")]
        return [rule.result(Outcome.PASS, block.ref, detail=f"MPD@{attr} absent")]
    return check


def _sps_duration(rule):
    def check(ctx, block):
        root = _root(block)
        fails = []
        if root.get("mediaPresentationDuration") is not None:
            fails.append(rule.result(Outcome.FAIL, block.ref, path(root, "mediaPresentationDuration"),
                                     "MPD@mediaPresentationDuration is present"))
        for p in root.findall(D + "Period"):
            if p.get("duration") is None:
                fails.append(rule.result(Outcome.FAIL, block.ref, path(p),
                                         "the Period has no @duration"))
        return fails or [rule.result(Outcome.PASS, block.ref,
                                     detail="no MPD@mediaPresentationDuration; Period@duration present")]
    return check


SPS_EXCLUDED = ("UTCTiming", "LeapSecondInformation", "PatchLocation", "Location", "ContentProtection",
                "ContentSteering", "Metrics", "ServiceDescription", "SupplementalProperty")


def _sps_excluded(rule):
    def check(ctx, block):
        root = _root(block)
        fails = [rule.result(Outcome.FAIL, block.ref, path(c), f"MPD.{etree.QName(c).localname} is present")
                 for c in root if isinstance(c.tag, str) and c.tag in {D + n for n in SPS_EXCLUDED}]
        return fails or [rule.result(Outcome.PASS, block.ref,
                                     detail="none of MPD." + ", MPD.".join(SPS_EXCLUDED))]
    return check


def _sps_no_imported(rule):
    def check(ctx, block):
        root = _root(block)
        fails = [rule.result(Outcome.FAIL, block.ref, path(i), "Period.ImportedMPD is present")
                 for p in root.findall(D + "Period") for i in p.findall(D + "ImportedMPD")]
        return fails or [rule.result(Outcome.PASS, block.ref, detail="no Period.ImportedMPD")]
    return check


def _sps_start(rule):
    def check(ctx, block):
        root = _root(block)
        fails, n = [], 0
        for p in root.findall(D + "Period"):
            if p.get("start") is None:
                continue
            n += 1
            if not is_zero_duration(p.get("start")):
                fails.append(rule.result(Outcome.FAIL, block.ref, path(p, "start"),
                                         f"Period@start is {p.get('start')!r}, not 0"))
        if fails:
            return fails
        if n == 0:
            return [rule.result(Outcome.PASS, block.ref, detail="Period@start absent")]
        return [rule.result(Outcome.PASS, block.ref, detail="Period@start is 0")]
    return check


# ---------------------------------------------------------------- DR-5


def _effective_profiles(el, root) -> list[str]:
    while el is not None:
        if el.get("profiles") is not None:
            return _profiles(el.get("profiles"))
        el = el.getparent()
    return _profiles(root.get("profiles"))


def _profiles_subset(rule):
    def check(ctx, block):
        root = _root(block)
        fails, n = [], 0
        for el in root.iter(D + "AdaptationSet", D + "Representation", D + "SubRepresentation"):
            if el.get("profiles") is None:
                continue
            n += 1
            higher = _effective_profiles(el.getparent(), root)
            extra = [p for p in _profiles(el.get("profiles")) if p not in higher]
            if extra:
                fails.append(rule.result(Outcome.FAIL, block.ref, path(el, "profiles"),
                                         f"{', '.join(extra)} not in the next higher level's profiles "
                                         f"({', '.join(higher) or 'none'})"))
        return _verdict(rule, block, fails, n, "@profiles below MPD level")
    return check


def _list_mime(rule):
    def check(ctx, block):
        root = _root(block)
        if not _is_list_profile(root):
            return [rule.result(Outcome.NOT_APPLICABLE, block.ref,
                                detail=f"{LIST_PROFILE} is not in MPD@profiles")]
        fails, n = [], 0
        for aset in root.iter(D + "AdaptationSet"):
            ct = aset.get("contentType")
            carriers = [aset] if aset.get("mimeType") else [r for r in aset.findall(D + "Representation")
                                                             if r.get("mimeType")]
            for el in carriers:
                n += 1
                mime = el.get("mimeType")
                base = _mime_base(mime)
                ok = base == f"{ct}/mp4" if ct else base.endswith("/mp4")
                if not ok:
                    want = f'"{ct}/mp4"' if ct else '"<contentType>/mp4"'
                    fails.append(rule.result(Outcome.FAIL, block.ref, path(el, "mimeType"),
                                             f"@mimeType {mime!r} in a List MPD; the CMAF base requires {want}"))
        return _verdict(rule, block, fails, n, "@mimeType on an inline AdaptationSet or Representation")
    return check


# ---------------------------------------------------------------- DR-7


def _period_has_aset(rule):
    def check(ctx, block):
        root = _root(block)
        out, fails = [], []
        for p in root.findall(D + "Period"):
            why = _linked_or_remote(p)
            if why:
                out.append(rule.result(Outcome.NOT_APPLICABLE, block.ref, path(p),
                                       f"{why}; the rule applies to the Period after resolution"))
                continue
            if is_zero_duration(p.get("duration")):
                continue
            if p.find(D + "AdaptationSet") is None:
                fails.append(rule.result(Outcome.FAIL, block.ref, path(p),
                                         f"no AdaptationSet and Period@duration is "
                                         f"{p.get('duration') or 'absent'}, not zero"))
        if fails:
            return fails
        if out and len(out) == len(root.findall(D + "Period")):
            return out
        return [rule.result(Outcome.PASS, block.ref,
                            detail="every Period with content in the document has an AdaptationSet or zero duration")]
    return check


# ---------------------------------------------------------------- DR-10, K-15


def _list_type(rule):
    def check(ctx, block):
        root = _root(block)
        if not _is_list_profile(root):
            return [rule.result(Outcome.NOT_APPLICABLE, block.ref,
                                detail=f"{LIST_PROFILE} is not in MPD@profiles")]
        if root.get("type") != "list":
            return [rule.result(Outcome.FAIL, block.ref, path(root, "type"),
                                f"MPD@profiles has {LIST_PROFILE} and MPD@type is {root.get('type')!r}")]
        return [rule.result(Outcome.PASS, block.ref, detail="List profile with MPD@type \"list\"")]
    return check


def _list_no_altmpd(rule):
    def check(ctx, block):
        root = _root(block)
        if not _is_list_profile(root):
            return [rule.result(Outcome.NOT_APPLICABLE, block.ref,
                                detail=f"{LIST_PROFILE} is not in MPD@profiles")]
        fails = []
        for es in root.iter(D + "EventStream"):
            if es.get("schemeIdUri") in (INSERT_SCHEME, REPLACE_SCHEME):
                fails.append(rule.result(Outcome.FAIL, block.ref, path(es, "schemeIdUri"),
                                         f"Alternative MPD event stream {es.get('schemeIdUri')}"))
        for el in root.iter(D + "InsertPresentation", D + "ReplacePresentation"):
            if el.getparent() is None or el.getparent().getparent() is None or \
                    el.getparent().getparent().get("schemeIdUri") not in (INSERT_SCHEME, REPLACE_SCHEME):
                fails.append(rule.result(Outcome.FAIL, block.ref, path(el),
                                         f"{etree.QName(el).localname} element"))
        return fails or [rule.result(Outcome.PASS, block.ref, detail="no Alternative MPD event")]
    return check


# ---------------------------------------------------------------- K rows


def _eventstream_unique(rule):
    def check(ctx, block):
        root = _root(block)
        fails, n = [], 0
        for p in root.iter(D + "Period"):
            seen = {}
            for es in p.findall(D + "EventStream"):
                n += 1
                key = (es.get("schemeIdUri"), es.get("value"))
                if key in seen:
                    fails.append(rule.result(Outcome.FAIL, block.ref, path(es),
                                             f"second EventStream with @schemeIdUri={key[0]!r} and "
                                             f"@value={key[1]!r} in this Period (first: {seen[key]})"))
                else:
                    seen[key] = path(es)
        return _verdict(rule, block, fails, n, "Period EventStream")
    return check


def _event_id_unique(rule):
    def check(ctx, block):
        root = _root(block)
        fails, n = [], 0
        for es in root.iter(D + "EventStream"):
            seen = {}
            for ev in es.findall(D + "Event"):
                i = ev.get("id")
                if i is None:
                    continue
                n += 1
                if i in seen:
                    fails.append(rule.result(Outcome.FAIL, block.ref, path(ev, "id"),
                                             f"Event@id {i!r} already used by {seen[i]} in the same EventStream"))
                else:
                    seen[i] = path(ev)
        return _verdict(rule, block, fails, n, "Event@id")
    return check


def _insert_events(root):
    for es in root.iter(D + "EventStream"):
        if es.get("schemeIdUri") == INSERT_SCHEME:
            yield from es.findall(D + "Event")


def _insert_not_dynamic(rule):
    def check(ctx, block):
        root = _root(block)
        evs = list(_insert_events(root))
        if not evs:
            return [rule.result(Outcome.NOT_APPLICABLE, block.ref, detail="no Alternative MPD Insertion event")]
        if root.get("type") == "dynamic":
            return [rule.result(Outcome.FAIL, block.ref, path(ev),
                                "Alternative MPD Insertion event in an MPD whose @type is \"dynamic\"")
                    for ev in evs]
        return [rule.result(Outcome.PASS, block.ref,
                            detail=f"{len(evs)} insertion event(s) in an MPD of type {root.get('type') or 'static'!r}")]
    return check


def _insert_no_status(rule):
    def check(ctx, block):
        root = _root(block)
        evs = list(_insert_events(root))
        fails = [rule.result(Outcome.FAIL, block.ref, path(ev, "status"),
                             f"Event@status={ev.get('status')!r} on an Alternative MPD Insertion event")
                 for ev in evs if ev.get("status") is not None]
        return _verdict(rule, block, fails, len(evs), "Alternative MPD Insertion event")
    return check


def _clip_needs_max(rule):
    def check(ctx, block):
        root = _root(block)
        fails, n = [], 0
        for rp in root.iter(D + "ReplacePresentation"):
            if rp.get("clip") is None:
                continue
            n += 1
            if rp.get("maxDuration") is None:
                fails.append(rule.result(Outcome.FAIL, block.ref, path(rp, "clip"),
                                         "ReplacePresentation@clip present and @maxDuration absent"))
        return _verdict(rule, block, fails, n, "ReplacePresentation@clip")
    return check


def _callback_value(rule):
    def check(ctx, block):
        root = _root(block)
        fails, n = [], 0
        for es in root.iter(D + "EventStream"):
            if es.get("schemeIdUri") != CALLBACK_SCHEME:
                continue
            n += 1
            if es.get("value") != "1":
                fails.append(rule.result(Outcome.FAIL, block.ref, path(es, "value"),
                                         f"callback EventStream@value is {es.get('value')!r}, not \"1\""))
        return _verdict(rule, block, fails, n, "callback EventStream in the MPD")
    return check


# ---------------------------------------------------------------- C07-6

_YEAR = r"\d{4}"
_TOKEN = r"[A-Za-z0-9][A-Za-z0-9._-]*"
SCHEME_SVTA = re.compile(rf"^urn:svta:dash:{_TOKEN}:{_YEAR}$")
ELEMENT_SVTA = re.compile(rf"^urn:svta:dash:sgai:{_YEAR}$")
QUALABS = re.compile(rf"^urn:qualabs:{_TOKEN}:{_YEAR}$")


def _names(root):
    """(element-or-None, attr-or-None, namespace) for every element and attribute."""
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        yield el, None, etree.QName(el).namespace
        for a in el.attrib:
            yield el, a, etree.QName(a).namespace


def _ns_policy(rule, prefix, pattern, kind):
    def check(ctx, block):
        root = _root(block)
        fails, n = [], 0
        if kind == "scheme":
            for el in root.iter():
                if not isinstance(el.tag, str):
                    continue
                v = el.get("schemeIdUri")
                if v is None or not v.strip().startswith(prefix):
                    continue
                n += 1
                if not pattern.match(v.strip()):
                    fails.append(rule.result(Outcome.FAIL, block.ref, path(el, "schemeIdUri"),
                                             f"scheme {v!r} is under {prefix} but not of the declared pattern"))
        else:
            seen = set()
            for el, a, ns in _names(root):
                if not ns or not ns.startswith(prefix):
                    continue
                n += 1
                if not pattern.match(ns) and ns not in seen:
                    seen.add(ns)
                    fails.append(rule.result(Outcome.FAIL, block.ref, path(el, a),
                                             f"namespace {ns!r} is under {prefix} but not of the declared pattern"))
        return _verdict(rule, block, fails, n, f"{kind} under {prefix}")
    return check


# ---------------------------------------------------------------- catalog

_ALL = MPD_KINDS + ("overlay-list", "fragment")
_EVENTS = MPD_KINDS + ("fragment",)


def _r(id, source, quote, applies, make=None, nv="", notes=""):
    r = Rule(id, 1, source, quote, tuple(applies), not_verifiable=nv, notes=notes)
    r.check = make(r) if make else None
    return r


def _bind(factory, *args):
    return lambda rule: factory(rule, *args)


RULES = [
    # DR-1: a document reached via ImportedMPD is bound to SPS (§8.15).
    _r("DR-1", f"{STD} §5.3.2.6.1; context/08 DR-1",
       "MPDs referenced in the ImportedMPD element shall be restricted to the constraints of a single "
       "period profile as defined in 8.15.",
       ("list-mpd",), nv="the referenced MPD is fetched at resolution time and is not in the referring document; "
       "the specification's sub-MPDs that declare the SPS profile are checked against §8.15 by DR-1a..DR-1i"),
    _r("DR-1a", f"{STD} §7.3.1, applied by §8.15.2 (\"The rules for the MPD as defined in subclause 7.3 shall "
       "apply.\"); context/08 DR-1",
       "The @mimeType attribute of each Representation shall be provided according to IETF RFC 4337.",
       ("sps-mpd",), _sps_mime),
    _r("DR-1b", f"{STD} §8.15.2; context/08 DR-1", 'The value of MPD@type shall be "static".',
       ("sps-mpd",), _bind(_attr_value, "type", "static", 'an SPS MPD has MPD@type "static"')),
    _r("DR-1c", f"{STD} §8.15.2; context/08 DR-1", "XLink attributes as defined in subclause 5.5 shall not be present.",
       ("sps-mpd",), _bind(_no_xlink, "all")),
    _r("DR-1d", f"{STD} §8.15.2; context/08 DR-1", "One and only one Period element shall be present.",
       ("sps-mpd",), _one_period),
    _r("DR-1e", f"{STD} §8.15.2; context/08 DR-1", "The MPD@availabilityStartTime shall not be present.",
       ("sps-mpd",), _bind(_absent_attr, "availabilityStartTime")),
    _r("DR-1f", f"{STD} §8.15.2; context/08 DR-1",
       "The MPD@mediaPresentationDuration attribute shall not be present, but the Period element shall include "
       "the @duration attribute to signal the duration of the content.",
       ("sps-mpd",), _sps_duration),
    _r("DR-1g", f"{STD} §8.15.2; context/08 DR-1",
       "The MPD shall not include any of the following attributes or elements: a) MPD.UTCTiming "
       "b) MPD.LeapSecondInformation c) MPD.PatchLocation d) MPD.Location e) MPD.ContentProtection "
       "f) MPD.ContentSteering g) MPD.Metrics h) MPD.ServiceDescription i) MPD.SupplementalProperty",
       ("sps-mpd",), _sps_excluded),
    _r("DR-1h", f"{STD} §8.15.3; context/08 DR-1", "Period.ImportedMPD shall not be present.",
       ("sps-mpd",), _sps_no_imported),
    _r("DR-1i", f"{STD} §8.15.3; context/08 DR-1",
       "Period@start attribute should not be present. If present, its value shall be 0.",
       ("sps-mpd",), _sps_start, notes="Only the 'shall' half is a FAIL; a present @start of 0 passes."),
    # DR-3: the document half is E-4; the rest is about the specification's prose.
    _r("DR-3", f"{STD} §5.2.1 NOTE 2; context/08 DR-3",
       "Based on the last two paragraphs, if DASH Clients remove all XML attributes and elements from the MPD in "
       "the DASH namespace and in other namespaces that are not in the XML schema documented in Annex B, the MPD "
       "results in a valid XML document which complies with this document.",
       ("spec",), nv="what legacy behaviour the specification's text assumes for a baseline element nested inside "
       "a foreign one is a property of the prose, not of a document; the document half (valid after removal by "
       "namespace) is E-4"),
    _r("DR-4", f"{STD} §8.1; context/08 DR-4",
       "The owner of the URI is responsible to provide sufficient semantics on the restrictions and permission "
       "of this interoperability point.",
       ("spec",), nv="whether an Interoperability Point URI is defined, published and given sufficient semantics "
       "is a fact about the specification's text and its publication, not about a document"),
    _r("DR-5a", f"{STD} §5.3.7.2 Table 16, @profiles; context/08 DR-5",
       "The value shall be a subset of the respective value in any higher level of the document hierarchy "
       "(Representation, Adaptation Set, MPD).",
       MPD_KINDS, _profiles_subset),
    _r("DR-5b", f"{STD} §8.12.4.3, applied to List MPDs by §8.14 (an extension of the CMAF profile); "
       "context/08 DR-5",
       'The @mimeType shall be set to "<contentType>/mp4".',
       MPD_KINDS, _list_mime),
    _r("DR-6", f"{STD} §5.2.1; context/08 DR-6",
       "The extension of the DASH XML schema (as provided in Annex B), in particular the addition of XML "
       "attributes or elements in the DASH namespace, is reserved to ISO/IEC.",
       ("spec",), nv="which of the four carriers a construct uses, and why, is the classification its chapter "
       "states (context/07 §8); the document side (no non-MP4 @mimeType on the AdaptationSet axis, nothing new "
       "in the DASH namespace) is DR-1a, DR-5b and E-3"),
    _r("DR-7", f"{STD} §5.3.2.2 Table 4, AdaptationSet; context/08 DR-7",
       "At least one Adaptation Set shall be present in each Period unless the value of the @duration attribute "
       "of the Period is set to zero.",
       MPD_KINDS, _period_has_aset,
       notes="A Linked Period (ImportedMPD) or a remote Period (xlink:href) is NOT_APPLICABLE: §5.3.2.6.1 asks "
       "that the MPD be valid after the reference processing, and the content arrives then."),
    _r("DR-8", f"{STD} §8.1 NOTE 1; context/08 DR-8",
       "Hence, profiles merely specify restrictions on MPD and Segments rather than DASH Client behaviour.",
       ("spec",), nv="DR-8 limits what the specification's text may promise about a Player; no document "
       "property follows from it"),
    _r("DR-9", f"{STD} §5.8.4.8 NOTE 1; context/08 DR-9",
       "If the scheme or the value for this descriptor is not recognized, the DASH Client is expected to ignore "
       "the parent element that contains the descriptor.",
       ("spec",), nv="which descriptor element a construct uses, and the reason, is stated in its chapter; both "
       "elements are valid in a document, so no document property separates the right choice from the wrong one"),
    _r("DR-10a", f"{STD} §8.14 rules 1 and 2; context/08 DR-10",
       'List MPDs shall have the value of the MPD@type attribute set to "list".',
       MPD_KINDS, _list_type,
       notes="A List MPD is one whose MPD@profiles carries urn:mpeg:dash:profile:list:2024 (§8.14 rule 2); "
       "MPD@type=\"list\" alone does not make one (DR-10)."),
    _r("DR-10b", f"{STD} §5.3.1.4; context/08 DR-10",
       "MPDs of this type shall not use MPD assembly as defined in 5.5, i.e. the attributes from namespace "
       "@xlink shall not be present.",
       ("list-mpd",), _bind(_no_xlink, "type-list")),
    _r("DR-10c", f"{STD} §8.14; context/08 DR-10",
       'The ISO-BMFF List profile is intended for use in conjunction with the Alternative MPD event (see '
       'subclause 5.16) and are not expected to be an "entry point" to a service.',
       ("spec",), nv="how a document is reached (by an Alternative MPD event or otherwise) is not in the document"),
    _r("DR-10d", f"{STD} §5.3.1.4; context/08 DR-10",
       'For Media Presentations with MPD@type set to "list" the constraints of a static Media Presentation '
       'shall apply.',
       ("list-mpd",), nv="the base gives no closed list of 'the constraints of a static Media Presentation': "
       "each lives in its own attribute row, and none is transcribed here"),
    # context/07
    _r("C07-3", "context/07 §3",
       "This walk-through MUST be present in the construct's chapter as an explicit prose paragraph, not implicit.",
       ("spec",), nv="asks for prose in the construct's chapter; level 2 and review read the prose"),
    _r("C07-6a", "context/07 §6, against context/06 \"Scheme URI patterns\"",
       "New event schemes introduced by this spec MUST use the year-pinned pattern under the SVTA Ads WG "
       "namespace: `urn:svta:dash:<construct>:<year>`",
       _ALL, _bind(_ns_policy, "urn:svta:", SCHEME_SVTA, "scheme"),
       notes="Reach: every @schemeIdUri under urn:svta:. A scheme of another body is not one this "
       "specification introduces and is not judged."),
    _r("C07-6b", "context/07 §6, against context/06 \"Element / attribute extension namespaces\"",
       "New XML elements introduced by this spec live under the SVTA Ads WG extension namespace: - "
       "**`urn:svta:dash:sgai:<year>`**",
       _ALL, _bind(_ns_policy, "urn:svta:", ELEMENT_SVTA, "element or attribute namespace"),
       notes="Reach: every element and attribute whose namespace is under urn:svta:."),
    _r("C07-6c", "context/07 §6, against context/06 \"Vendor extensions (Qualabs)\"",
       "Qualabs-private experimental extensions that are not part of this specification MUST use the Qualabs "
       "vendor namespace: `urn:qualabs:<feature>:<year>`",
       _ALL, _bind(_ns_policy, "urn:qualabs:", QUALABS, "element or attribute namespace"),
       notes="Reach: element and attribute namespaces under urn:qualabs:."),
    _r("C07-7", "context/07 §7",
       "The construct's chapter MUST link to this checklist and confirm each item is satisfied.",
       ("spec",), nv="asks for a link and a confirmation in the construct's chapter, which is prose"),
    # Audit rows: sentences that state a property of a document.
    _r("K-4a", f"{STD} §5.10.2.1",
       "A Period shall contain at most one EventStream element with the same value of the @schemeIdUri "
       "attribute and the value of the @value attribute, i.e. all Events of one type shall be clustered in one "
       "Event Stream.",
       _EVENTS, _eventstream_unique),
    _r("K-4b", f"{STD} §5.10.2.2 Table 44, Event@id",
       "Each EventStream element shall not contain two Event elements with the same value of Event@id.",
       _EVENTS, _event_id_unique),
    _r("K-13a", f"{STD} §5.16.3", 'The event shall not appear if the MPD type is "dynamic".',
       MPD_KINDS, _insert_not_dynamic),
    _r("K-13b", f"{STD} §5.16.3 Table 59, Event@status row", "Event@status This attribute shall not be used.",
       _EVENTS, _insert_no_status),
    _r("K-14", f"{STD} §5.16.4 Table 62, @clip",
       "This attribute shall not be present if the @maxDuration attribute is absent.",
       _EVENTS, _clip_needs_max),
    _r("K-15a", f"{STD} §8.14 rule 3", "List MPDs shall not contain XLink attributes defined in subclause 5.5.",
       MPD_KINDS, _bind(_no_xlink, "list-profile")),
    _r("K-15b", f"{STD} §8.14 rule 5", "List MPDs shall not contain Alternative MPD events.",
       MPD_KINDS, _list_no_altmpd),
    _r("K-17", f"{STD} §8.1 (conformance of a Media Presentation to a profile, condition 2)",
       "There is at least one Representation in each Period in the profile-specific MPD for ProfA.",
       MPD_KINDS, nv="a condition on the Media Presentation (the MPD with its Segments, and for a List MPD the "
       "merged result of its Linked Periods), which §8.1 lists apart from the conditions on the MPD; an MPD "
       "example may elide its Representations (ISO's own K.6.4 does), so the document alone does not decide it",
       notes="A check that counts Representations per Period and profile was written and measured: it FAILs "
       "ISO's example K.6.4, whose AdaptationSet elides its Representations, and was not entered."),
    _r("K-20", f"{STD} §5.10.4.5.3 Table 47",
       'EventStream@schemeIdUri "urn:mpeg:dash:event:callback:2015" EventStream@value 1',
       _EVENTS, _callback_value,
       notes="Table 47 is a two-column table; the quote is its first two rows read across."),
]


# ---------------------------------------------------------------- DR-3, DR-4, DR-9: the document halves

MPEG_PROFILES = {   # every urn:mpeg:dash:profile: identifier the 6th edition defines (found in the primary copy)
    "urn:mpeg:dash:profile:full:2011", "urn:mpeg:dash:profile:isoff-on-demand:2011",
    "urn:mpeg:dash:profile:isoff-live:2011", "urn:mpeg:dash:profile:isoff-main:2011",
    "urn:mpeg:dash:profile:mp2t-main:2011", "urn:mpeg:dash:profile:mp2t-simple:2011",
    "urn:mpeg:dash:profile:isoff-common:2014", "urn:mpeg:dash:profile:isoff-ext-live:2014",
    "urn:mpeg:dash:profile:isoff-ext-on-demand:2014", "urn:mpeg:dash:profile:isoff-broadcast:2015",
    "urn:mpeg:dash:profile:cmaf:2019", "urn:mpeg:dash:profile:cmaf-extended:2019",
    "urn:mpeg:dash:profile:list:2024", "urn:mpeg:dash:profile:sps:2024",
    "urn:mpeg:dash:profile:advanced-linear:2025",
}


def _nested_dash(rule):
    """DR-3a: a DASH-namespace element inside a foreign one carries no legacy
    guarantee. Found by code; whether a legacy Player was expected to process
    it is the author's intent, so an occurrence is NOT_VERIFIABLE, not FAIL."""
    def check(ctx, block):
        root = _root(block)
        found = []
        for el in root.iter():
            if not isinstance(el.tag, str) or etree.QName(el).namespace != DASH_NS:
                continue
            anc = el.getparent()
            while anc is not None and etree.QName(anc).namespace == DASH_NS:
                anc = anc.getparent()
            if anc is not None and (el.getparent() is None or etree.QName(el.getparent()).namespace != DASH_NS):
                found.append(el)
        if not found:
            return [rule.result(Outcome.PASS, block.ref, detail="no DASH element nested inside a foreign element")]
        return [rule.result(Outcome.NOT_VERIFIABLE, block.ref, path(el),
                            f"DASH element {etree.QName(el).localname} inside {etree.QName(el.getparent()).localname}: "
                            "it is removed with its foreign parent, so no legacy behaviour may be assumed for it; "
                            "whether the author assumed one is not in the document") for el in found]
    return check


def _known_profiles(rule):
    def check(ctx, block):
        root = _root(block)
        out, n = [], 0
        for el in root.iter():
            if not isinstance(el.tag, str) or el.get("profiles") is None:
                continue
            for uri in _profiles(el.get("profiles")):
                n += 1
                if uri.startswith("urn:mpeg:dash:profile:") and uri not in MPEG_PROFILES:
                    out.append(rule.result(Outcome.FAIL, block.ref, path(el, "profiles"),
                                           f"{uri} is in MPEG's profile namespace and the 6th edition defines no "
                                           "such profile"))
                elif not uri.startswith("urn:mpeg:dash:profile:"):
                    n -= 1   # an interoperability point of another owner (§8.1): outside this rule
        return out or _verdict(rule, block, [], n, "MPEG profile identifiers")
    return check


def _essential_on_main(rule):
    """DR-9a: on the primary content path, an EssentialProperty with a scheme of
    this specification makes a legacy Player drop its parent AdaptationSet or
    Representation, which DP-3 forbids."""
    def check(ctx, block):
        root = _root(block)
        fails, n = [], 0
        for parent in root.iter(D + "AdaptationSet", D + "Representation"):
            for ep in parent.findall(D + "EssentialProperty"):
                n += 1
                s = ep.get("schemeIdUri") or ""
                if s.startswith(("urn:svta:", "urn:qualabs:")):
                    fails.append(rule.result(Outcome.FAIL, block.ref, path(ep),
                                             f"EssentialProperty {s} on a {etree.QName(parent).localname} of the "
                                             "primary content: a Player that does not know the scheme ignores the "
                                             "parent (§5.8.4.8 NOTE 1)"))
        return _verdict(rule, block, fails, n, "EssentialProperty descriptors on AdaptationSet/Representation")
    return check


RULES += [
    _r("DR-3a", f"{STD} §5.2.1 NOTE 2; context/08 DR-3",
       "Based on the last two paragraphs, if DASH Clients remove all XML attributes and elements from the MPD in "
       "the DASH namespace and in other namespaces that are not in the XML schema documented in Annex B, the MPD "
       "results in a valid XML document which complies with this document.",
       MPD_KINDS + ("overlay-list",), _nested_dash,
       notes="The document half of DR-3: occurrences are found by code; the rule's intent half stays in DR-3."),
    _r("DR-4a", f"{STD} §8.1; context/08 DR-4", "A profile has an identifier, which is a URI.",
       MPD_KINDS, _known_profiles,
       notes="Identifiers in urn:mpeg:dash:profile: must be ones the 6th edition defines (list found in the "
       "primary copy); other URIs are interoperability points of their owners and are outside this rule."),
    _r("DR-9a", f"{STD} §5.8.4.8 NOTE 1; context/08 DR-9 (consequence of DP-3)",
       "If the scheme or the value for this descriptor is not recognized, the DASH Client is expected to ignore "
       "the parent element that contains the descriptor.",
       ("mpd",), _essential_on_main,
       notes="Main MPDs only: on the primary content path dropping the parent breaks primary-content playback, "
       "which DP-3 forbids (context/08 DR-9)."),
]
