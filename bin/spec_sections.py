"""The sections of a spec markdown (source or assembled), addressable by key.

A section is a heading line outside a code fence and everything up to the
next such heading, of any level, as `check-incremental.py` splits them. Its
key is the heading's number when it has one (`5.1.3`, `A.5`, `Annex A`,
`1`), else the heading text. Shared by spec-section.py and
apply-spec-patch.py so the two cannot cut a document differently.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

HEADING = re.compile(r"^(#{1,6}) (.*\S)\s*$")
NUMBER = re.compile(r"^(Annex [A-Z]|[A-Z](?:\.\d+)+|\d+(?:\.\d+)*)\.?(?=\s|$)")
DIRECTIVE = re.compile(r"^\{\{(example|xsd|include)(?::[^}]+)?\}\}$")


class SectionError(Exception):
    pass


@dataclass
class Section:
    key: str
    heading: str      # the heading text, without the #'s ('' for the preamble)
    level: int        # 0 for the preamble
    start: int        # 0-based index of its first line
    lines: list       # its lines, each with its newline

    @property
    def text(self) -> str:
        return "".join(self.lines)


def key_of(heading: str) -> str:
    m = NUMBER.match(heading)
    return m.group(1) if m else heading


def split(text: str) -> list:
    lines = text.splitlines(keepends=True)
    out = [Section("(preamble)", "", 0, 0, [])]
    fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fence = not fence
        m = None if fence else HEADING.match(line.rstrip("\n"))
        if m:
            out.append(Section(key_of(m.group(2)), m.group(2), len(m.group(1)), i, [line]))
        else:
            out[-1].lines.append(line)
    if not out[0].lines:
        out.pop(0)
    keys = [s.key for s in out]
    dup = sorted({k for k in keys if keys.count(k) > 1})
    if dup:
        raise SectionError("section keys repeated: " + ", ".join(dup))
    return out


def by_key(sections: list) -> dict:
    return {s.key: s for s in sections}


def join(sections: list) -> str:
    return "".join(s.text for s in sections)
