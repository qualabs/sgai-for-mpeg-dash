#!/usr/bin/env python3
"""One-time migration (T-02, ADR 0060): split a published spec into spec-source/.

Every ```xml block and every request block (first line `GET|POST ... HTTP/1.x`
or a bare request path) becomes a file under spec-source/examples/<part>/,
named after the section it sits in; the §5.10.1 schema block becomes
spec-source/syntax/sgai-extension.xsd. In the prose the block's content lines
are replaced by one directive line; the fences stay in the prose.

Usage: extract-source.py <spec.md> <spec-source-dir>
Kept as the record of how the source was first made, not as a build step.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../bin"))
from conformance import extract  # noqa: E402

HEAD = re.compile(r"^#{2,5} (?:Annex ([A-Z])\b|([A-Z]\.\d+(?:\.\d+)*)|(\d+(?:\.\d+)*))")
EXT = {"mpd": "mpd", "list-mpd": "mpd", "sps-mpd": "mpd", "overlay-list": "xml",
       "fragment": "xml", "vast": "xml"}


def main(spec, out):
    lines = open(spec, encoding="utf-8", newline="").read().splitlines(keepends=True)
    kinds = {b.line: b for b in extract.blocks("".join(lines))}
    os.makedirs(os.path.join(out, "examples"), exist_ok=True)
    os.makedirs(os.path.join(out, "syntax"), exist_ok=True)
    part, sec = "front", "0"
    count = {}
    prose = []
    i = 0
    n_files = 0
    while i < len(lines):
        line = lines[i]
        m = HEAD.match(line)
        if m:
            if m.group(1):
                part, sec = "annex-" + m.group(1).lower(), m.group(1)
            elif m.group(2):
                sec = m.group(2)
            else:
                sec = m.group(3)
                part = "chapter-" + sec.split(".")[0]
        if line.startswith("```"):
            lang = line[3:].strip()
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            body = lines[i + 1:j]
            first = body[0] if body else ""
            is_req = bool(re.match(r"^(GET|POST) \S+", first))
            blk = kinds.get(i + 2)  # extract.Block.line is the first content line, 1-based
            if lang == "xml" or is_req:
                if blk is not None and blk.kind == "ext-xsd":
                    rel = None
                    path = os.path.join(out, "syntax", "sgai-extension.xsd")
                    directive = "{{xsd}}\n"
                else:
                    ext = "http" if is_req and lang != "xml" else EXT.get(blk.kind if blk else "", "xml")
                    count[sec] = count.get(sec, 0) + 1
                    rel = f"{part}/{sec}-{count[sec]}.{ext}"
                    path = os.path.join(out, "examples", rel)
                    directive = "{{example:" + rel + "}}\n"
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write("".join(body))
                n_files += 1
                prose += [line, directive, lines[j]]
                i = j + 1
                continue
            prose += lines[i:j + 1]
            i = j + 1
            continue
        prose.append(line)
        i += 1
    with open(os.path.join(out, "sgai-spec.src.md"), "w", encoding="utf-8", newline="") as fh:
        fh.write("".join(prose))
    print(f"{n_files} blocks extracted into {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
