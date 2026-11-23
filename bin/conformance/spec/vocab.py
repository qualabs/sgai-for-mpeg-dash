"""The names the rules read, and where each comes from.

context/03 states capabilities, not names. A name comes either from
context/06 (the base constructs it makes us reuse: `@executeOnce`,
`@earliestResolutionTimeOffset`, `@startWithOffset`, the `urn:svta:dash:`
scheme pattern, the callback scheme) or from the specification under test,
which chooses its own carriers (`@durationCap`, `<svta:OverlayList>`, ...).

A rule that reads a carrier the specification chose first asks the
extension schema under test whether it still declares that name (`need`).
If it does not, the rule returns NOT_VERIFIABLE naming the carrier instead
of passing: a renamed attribute must not turn into an absent one, which most
rules read as "nothing declared, nothing to check".
"""
from __future__ import annotations

from functools import lru_cache

from lxml import etree

from .. import extract
from ..model import Outcome

DASH = extract.DASH_NS
SGAI = extract.SGAI_NS
XS = extract.XSD_NS
UP = "urn:mpeg:dash:schema:urlparam:2016"

# --- fixed by context/06 ------------------------------------------------------
SGAI_SCHEME_PREFIX = "urn:svta:dash:"
SGAI_NS_PREFIX = "urn:svta:"
CALLBACK = "urn:mpeg:dash:event:callback:2015"
EXECUTE_ONCE = "executeOnce"
EARLIEST = "earliestResolutionTimeOffset"
START_WITH_OFFSET = "startWithOffset"
METADATA = ("AdSystem", "AdTitle")          # R23.1 names them

# --- fixed by context/03 -------------------------------------------------------
TOKENS = ("linear", "overlay", "overlay-corner", "overlay-lower-third",
          "squeezeback-l-shape-upper-left", "squeezeback-l-shape-upper-right",
          "squeezeback-double-box", "squeezeback-double-box-background",
          "squeezeback-frame", "pause-fullscreen", "pause-partial", "custom")   # R12.2
L_SHAPES = ("squeezeback-l-shape-upper-left", "squeezeback-l-shape-upper-right", "squeezeback-frame")  # R27.1
CAPABILITY = {"sgai-video-decoders": ("1", "2", "3"), "sgai-image-over-video": ("1", "0"),
              "sgai-html-over-video": ("1", "0"), "sgai-custom-layout": ("1", "0"),
              "sgai-ad-audio": ("1", "0")}                                   # R29.1, first table
SLOT = ("sgai-allowed-layouts", "sgai-custom-region", "sgai-ad-audio-allowed")  # R29.1, second table
RESERVED = tuple(CAPABILITY) + SLOT
URL_TEMPLATE = ("UrlQueryInfo", "ExtUrlQueryInfo", "ExtHttpHeaderInfo", "RequestParam")  # DASH Annex I

# --- chosen by the specification under test ------------------------------------
WINDOW = {"overlay": "OverlayPresentation", "pause": "PauseAdPresentation"}
SCHEMES = {"urn:svta:dash:sgai-overlay:2026": "overlay",
           "urn:svta:dash:sgai-pause-trigger:2026": "pause"}
LIST, AD, OPTION, TRACKING, CLICK = "OverlayList", "Ad", "RenderableAsset", "Tracking", "ClickThrough"
CAP, ALLOWED, REGION, RELATION = "durationCap", "allowedLayouts", "customRegion", "linearRelation"
FAMILY, DISMISS, VALID, EXHAUSTED = "family", "dismissAfter", "validFor", "onExhausted"
LAYOUT, RECT, BACKGROUND, MIME, DURATION = "layout", "rect", "background", "mimeType", "duration"


def q(local: str, ns: str = SGAI) -> str:
    return f"{{{ns}}}{local}"


# --- the extension schema under test ---------------------------------------------

@lru_cache(maxsize=16)
def schema_tree(ext_text: str):
    try:
        return etree.fromstring(ext_text.encode("utf-8"))
    except (etree.XMLSyntaxError, ValueError):
        return None


def _local(qname: str) -> str:
    return qname.split(":", 1)[-1]


def complex_type(ext_text: str, element: str):
    """The xs:complexType of the element named `element` (global or local),
    or None when the schema declares no such element."""
    root = schema_tree(ext_text)
    if root is None:
        return None
    for decl in root.iter(q("element", XS)):
        if decl.get("name") != element:
            continue
        inline = decl.find(q("complexType", XS))
        if inline is not None:
            return inline
        tname = decl.get("type")
        if tname:
            for ct in root.iter(q("complexType", XS)):
                if ct.get("name") == _local(tname):
                    return ct
    return None


def attribute(ext_text: str, element: str, attr: str):
    ct = complex_type(ext_text, element)
    if ct is None:
        return None
    for a in ct.iter(q("attribute", XS)):
        if a.get("name") == attr:
            return a
    return None


def child(ext_text: str, element: str, name: str):
    ct = complex_type(ext_text, element)
    if ct is None:
        return None
    for e in ct.iter(q("element", XS)):
        if e.get("name") == name or _local(e.get("ref") or "") == name:
            return e
    return None


def enumeration(ext_text: str, type_qname: str) -> list | None:
    """The enumeration values of a simple type of the extension schema,
    following an xs:list to its item type. None if the type is not ours."""
    root = schema_tree(ext_text)
    if root is None:
        return None
    name = _local(type_qname)
    for st in root.iter(q("simpleType", XS)):
        if st.get("name") != name:
            continue
        lst = st.find(q("list", XS))
        if lst is not None and lst.get("itemType"):
            return enumeration(ext_text, lst.get("itemType"))
        return [e.get("value") for e in st.iter(q("enumeration", XS))]
    return None


def declared(ext_text: str, element: str, attr: str | None = None) -> bool:
    if attr is None:
        root = schema_tree(ext_text)
        return root is not None and any(d.get("name") == element for d in root.iter(q("element", XS)))
    return attribute(ext_text, element, attr) is not None


def need(rule, ctx, where: str, *names) -> list:
    """names: "Element" or "Element@attr". [] when the schema under test
    declares them all; otherwise one NOT_VERIFIABLE naming what is missing."""
    missing = []
    for n in names:
        el, _, at = n.partition("@")
        if not declared(ctx.ext_text, el, at or None):
            missing.append(n)
    if not missing:
        return []
    return [rule.result(Outcome.NOT_VERIFIABLE, where,
                        detail="carrier not declared in the extension schema under test: "
                               + ", ".join(missing) + " (the rule reads the specification's carrier by this name)")]
