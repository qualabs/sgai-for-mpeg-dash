"""Level 1: the extension schema and the documents against the base schema.

E-1  the extension XSD compiles together with ISO's 6th-edition schema;
E-2  it declares nothing in, and redefines nothing of, the DASH namespace;
E-3  every example document validates against the two schemas together;
E-4  §5.2.1 as a test: with everything outside the DASH namespace removed,
     every MPD still validates against ISO's schema alone.
XSD-ID the extension XSD file is byte-identical to the spec's §5.10.1 block.

ADR 0048 explains why it takes the four together to say "conforms to DASH".
"""
from __future__ import annotations

import copy
from pathlib import Path

from lxml import etree

from .extract import DASH_NS, SGAI_NS, XSD_NS, Block
from .model import Outcome, Result, Rule

XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
DOCUMENT_KINDS = ("mpd", "list-mpd", "sps-mpd", "overlay-list")
MPD_KINDS = ("mpd", "list-mpd", "sps-mpd")
STD = "ISO/IEC 23009-1:2026"

E1 = Rule("E-1", 1, f"{STD} Annex B; ADR 0048",
          "The schema of the MPD for this document is provided at: "
          "https://standards.iso.org/iso-iec/23009/-1/ed-6/en (DASH-MPD.xsd).",
          ("ext-xsd",), notes="The extension XSD imports DASH-MPD.xsd; compiling both proves every DASH reference resolves.")
E2 = Rule("E-2", 1, f"{STD} §5.2.1; ADR 0048",
          "the MPD shall be authored such that, after XML attributes or elements in the other "
          "namespaces than the DASH namespace are removed, the result is a valid XML document "
          "formatted according to that schema and that conforms to this document",
          ("ext-xsd",), notes="An extension can only add in another namespace; it may not declare in, redefine or override the DASH namespace.")
E3 = Rule("E-3", 1, f"{STD} Annex B (xs:any / xs:anyAttribute namespace=\"##other\"); ADR 0048",
          "The schema of the MPD for this document is provided at: "
          "https://standards.iso.org/iso-iec/23009/-1/ed-6/en (DASH-MPD.xsd).",
          DOCUMENT_KINDS + ("fragment",), notes="Foreign content is valid only where a DASH type opens a wildcard.")
E4 = Rule("E-4", 1, f"{STD} §5.2.1",
          "the MPD shall be authored such that, after XML attributes or elements in the other "
          "namespaces than the DASH namespace are removed, the result is a valid XML document "
          "formatted according to that schema and that conforms to this document",
          MPD_KINDS)
XSD_ID = Rule("XSD-ID", 1, "ADR 0047",
              "The extension XSD file is extracted by code from the §5.10.1 block and is identical to it.",
              ("ext-xsd",))
RULES = (E1, E2, E3, E4, XSD_ID)


def iso_schema(isodir: Path) -> etree.XMLSchema:
    return etree.XMLSchema(etree.parse(str(isodir / "DASH-MPD.xsd")))


def compile_extension(xsd_text: str, isodir: Path):
    """(schema, None) or (None, error). The extension imports DASH-MPD.xsd by a
    relative location, resolved against the pinned ISO directory, so the
    compiled schema covers both namespaces."""
    try:
        doc = etree.XML(xsd_text.encode("utf-8"), base_url=str(isodir / "sgai-extension.xsd"))
        return etree.XMLSchema(doc), None
    except (etree.XMLSyntaxError, etree.XMLSchemaParseError) as e:
        return None, str(e)


def e1(xsd_text: str, isodir: Path, subject: str = "extension XSD") -> list[Result]:
    schema, err = compile_extension(xsd_text, isodir)
    if schema is None:
        return [E1.result(Outcome.FAIL, subject, detail=f"does not compile with DASH-MPD.xsd: {err}")]
    return [E1.result(Outcome.PASS, subject, detail="compiles together with ISO 6th-edition DASH-MPD.xsd")]


def e2(xsd_text: str, subject: str = "extension XSD") -> list[Result]:
    try:
        root = etree.XML(xsd_text.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        return [E2.result(Outcome.FAIL, subject, detail=f"not well-formed: {e}")]
    out = []
    tns = root.get("targetNamespace")
    if tns == DASH_NS or not tns:
        out.append(E2.result(Outcome.FAIL, subject, "/xs:schema/@targetNamespace",
                             f"targetNamespace is {tns!r}: an extension must declare in its own namespace"))
    for tag in ("redefine", "override", "include"):
        for el in root.iter(f"{{{XSD_NS}}}{tag}"):
            out.append(E2.result(Outcome.FAIL, subject, readable_path(el),
                                 f"xs:{tag} of {el.get('schemaLocation')!r}: an extension may only import, not {tag}"))
    for el in root.iter(f"{{{XSD_NS}}}import"):
        if el.get("namespace") == SGAI_NS:
            out.append(E2.result(Outcome.FAIL, subject, readable_path(el), "imports its own namespace"))
    if not out:
        out.append(E2.result(Outcome.PASS, subject, detail=f"targetNamespace {tns}; no redefine, override or include"))
    return out


def readable_path(el) -> str:
    """/MPD/Period[1]/EventStream[1]/Event[1], with local names: a path a
    reader can follow (lxml's own error paths read /*/*[2]/*[1])."""
    parts = []
    while el is not None and isinstance(el.tag, str):
        parent = el.getparent()
        name = etree.QName(el).localname
        if parent is None:
            parts.append(name)
        else:
            same = [c for c in parent if isinstance(c.tag, str) and c.tag == el.tag]
            parts.append(f"{name}[{same.index(el) + 1}]")
        el = parent
    return "/" + "/".join(reversed(parts))


def _errors(rule: Rule, schema: etree.XMLSchema, doc, b: Block, what: str) -> list[Result]:
    out = []
    tree = doc.getroottree()
    for err in schema.error_log:
        xp = err.path or ""
        try:
            found = tree.xpath(xp) if xp else []
            if found:
                xp = readable_path(found[0])
        except etree.XPathError:
            pass
        out.append(rule.result(Outcome.FAIL, b.ref, xp,
                               f"{what}: line {b.line + err.line - 1} of the markdown: {err.message}"))
    return out


def e3(blocks: list[Block], combined: etree.XMLSchema, globals_: set) -> list[Result]:
    out = []
    for b in blocks:
        if b.kind == "malformed":
            out.append(E3.result(Outcome.FAIL, b.ref, detail=f"not well-formed XML: {b.error}"))
            continue
        if b.kind == "vast":
            out.append(E3.result(Outcome.NOT_APPLICABLE, b.ref, detail="VAST is IAB, not DASH"))
            continue
        if b.kind in ("ext-xsd", "xsd"):
            continue
        if b.kind == "fragment" and b.root not in globals_:
            out.append(E3.result(Outcome.NOT_VERIFIABLE, b.ref,
                                 detail=f"fragment whose root {b.root} is not a global element of either schema"))
            continue
        doc = etree.XML(b.text.encode("utf-8"))
        if combined.validate(doc):
            out.append(E3.result(Outcome.PASS, b.ref, detail=f"{b.kind} valid against DASH-MPD.xsd + extension XSD"))
        else:
            out.extend(_errors(E3, combined, doc, b, "invalid against DASH-MPD.xsd + extension XSD"))
    return out


def global_elements(xsd_texts: list[str]) -> set:
    """{ns}name of every global element the given schema documents declare."""
    out = set()
    for text in xsd_texts:
        root = etree.XML(text.encode("utf-8"))
        tns = root.get("targetNamespace") or ""
        for el in root.findall(f"{{{XSD_NS}}}element"):
            if el.get("name"):
                out.add(f"{{{tns}}}{el.get('name')}")
    return out


def strip_foreign(doc: etree._Element) -> etree._Element:
    """Remove every element and attribute outside the DASH namespace (§5.2.1).
    xsi:* is kept: it is schema-instance machinery, not content."""
    doc = copy.deepcopy(doc)
    for el in list(doc.iter()):
        if not isinstance(el.tag, str):
            continue
        ns = etree.QName(el).namespace
        if el is not doc and ns != DASH_NS:
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)
            continue
        for name in list(el.attrib):
            ans = etree.QName(name).namespace
            if ans not in (None, XSI_NS):
                del el.attrib[name]
    return doc


def e4(blocks: list[Block], iso: etree.XMLSchema) -> list[Result]:
    out = []
    for b in blocks:
        if b.kind not in MPD_KINDS:
            continue
        stripped = strip_foreign(etree.XML(b.text.encode("utf-8")))
        if iso.validate(stripped):
            out.append(E4.result(Outcome.PASS, b.ref, detail="valid against DASH-MPD.xsd alone after removing other namespaces"))
        else:
            out.extend(_errors(E4, iso, stripped, b, "invalid after removing other namespaces"))
    return out


def identity(xsd_file: Path, block: Block) -> list[Result]:
    if not xsd_file.exists():
        return [XSD_ID.result(Outcome.FAIL, str(xsd_file), detail="the extension XSD file does not exist")]
    if xsd_file.read_bytes() == block.text.encode("utf-8"):
        return [XSD_ID.result(Outcome.PASS, str(xsd_file), detail=f"byte-identical to {block.ref}")]
    return [XSD_ID.result(Outcome.FAIL, str(xsd_file), detail=f"differs from {block.ref}")]
