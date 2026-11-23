"""Extract the XML blocks and the example requests of a specification markdown.

Each block keeps the line of the markdown where its content starts, so a
result can point at the place a reader can open. The class of a block comes
from the document itself (root element, namespace, @type, @profiles), never
from the prose around it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import parse_qsl, urlsplit
from xml.etree import ElementTree as ET

DASH_NS = "urn:mpeg:dash:schema:mpd:2011"
SGAI_NS = "urn:svta:dash:sgai:2026"
XSD_NS = "http://www.w3.org/2001/XMLSchema"
SPS_PROFILE = "urn:mpeg:dash:profile:sps:2024"
LIST_PROFILE = "urn:mpeg:dash:profile:list:2024"

FENCE = re.compile(r"^```(\w*)\s*$")
REQUEST = re.compile(r"^(GET|POST)\s+(\S+)\s+HTTP/1\.[01]\s*$")


@dataclass
class Block:
    index: int          # 1-based, in document order among xml blocks
    line: int           # line of the markdown where the content starts
    text: str
    kind: str = ""      # mpd | list-mpd | sps-mpd | overlay-list | ext-xsd | xsd | vast | fragment | malformed
    root: str = ""      # {ns}local of the root element
    error: str = ""     # parse error, for malformed

    @property
    def ref(self) -> str:
        return f"xml#{self.index} (line {self.line})"


@dataclass
class Request:
    line: int
    method: str
    target: str
    params: list = field(default_factory=list)   # [(name, value)] in order

    @property
    def ref(self) -> str:
        return f"request (line {self.line})"


def _qname(tag: str) -> tuple[str, str]:
    if tag.startswith("{"):
        ns, local = tag[1:].split("}", 1)
        return ns, local
    return "", tag


def classify(block: Block) -> None:
    try:
        root = ET.fromstring(block.text.encode("utf-8"))
    except ET.ParseError as e:
        block.kind, block.error = "malformed", str(e)
        return
    ns, local = _qname(root.tag)
    block.root = root.tag
    if ns == DASH_NS and local == "MPD":
        profiles = (root.get("profiles") or "").split(",")
        profiles = [p.strip() for p in profiles]
        if root.get("type") == "list":
            block.kind = "list-mpd"
        elif SPS_PROFILE in profiles:
            block.kind = "sps-mpd"
        else:
            block.kind = "mpd"
    elif ns == XSD_NS and local == "schema":
        block.kind = "ext-xsd" if root.get("targetNamespace") == SGAI_NS else "xsd"
    elif ns == SGAI_NS and local == "OverlayList":
        block.kind = "overlay-list"
    elif ns == "" and local == "VAST":
        block.kind = "vast"
    else:
        block.kind = "fragment"


def blocks(markdown: str) -> list[Block]:
    out, lang, start, buf = [], None, 0, []
    for n, line in enumerate(markdown.splitlines(), 1):
        m = FENCE.match(line)
        if lang is None:
            if m:
                lang, start, buf = m.group(1), n + 1, []
            continue
        if line.strip() == "```":
            if lang == "xml":
                b = Block(index=len(out) + 1, line=start, text="\n".join(buf) + "\n")
                classify(b)
                out.append(b)
            lang = None
            continue
        buf.append(line)
    return out


def requests(markdown: str) -> list[Request]:
    """Example requests: a `GET <target> HTTP/1.1` line inside a fenced block,
    joined with the indented continuation lines that follow it."""
    out, inside = [], False
    lines = markdown.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("```"):
            inside = not inside
            continue
        if not inside:
            continue
        m = re.match(r"^(GET|POST)\s+(\S+)", line)
        if not m:
            continue
        target = m.group(2)
        rest = line[m.end():]
        j = i + 1
        while "HTTP/1." not in rest and j < len(lines) and lines[j].startswith((" ", "\t")):
            piece = lines[j].strip()
            if piece.endswith(("HTTP/1.1", "HTTP/1.0")):
                target += piece.rsplit(" ", 1)[0].strip()
                rest = "HTTP/1.1"
            else:
                target += piece
            j += 1
        query = urlsplit(target).query
        out.append(Request(line=i + 1, method=m.group(1), target=target,
                           params=parse_qsl(query, keep_blank_values=True)))
    return out


def summary(bs: list[Block]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for b in bs:
        counts[b.kind] = counts.get(b.kind, 0) + 1
    return counts


def extension_schema(bs: list[Block]) -> list[Block]:
    return [b for b in bs if b.kind == "ext-xsd"]
