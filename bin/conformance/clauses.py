"""The clause index of the primary copy, built at run time (ADR 0063).

The primary copy of the base standard is located as bin/check-normative-base.py
locates it (SGAI_NORMATIVE_PDF, else NORMATIVE_PDF_PATH in .env.agent),
checked against the sha256 that context/00-normative-base.md declares, and
read with `pdftotext -layout` to a pipe. Only the set of clause numbers that
head a clause of the body is kept, in memory: no text of the copy is written
anywhere, in the repository or outside it.

A clause heading is a line of the body (table-of-contents lines, which carry
leader dots, are left out) that starts with a clause number followed by a
title starting with a capital letter; a number is in the index only when its
parent is (5.16.2.2.6 needs 5.16.2.2, ..., 5). The index is usable only when
it holds every top-level clause 1 to 8 of the edition; anything less means the
extraction did not read the document, and the rule cannot tell.

What the index answers: whether a clause number exists in the edition. Not
whether the clause says what the specification cites it for.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path

HEADING = re.compile(r"^\s{0,6}(\d{1,2}(?:\.\d{1,2}){0,6})(?:\s+|(?=[A-Z]))([A-Z][A-Za-z].*)$")
TOP_LEVEL = tuple(str(n) for n in range(1, 9))


class Unavailable(Exception):
    """The index cannot be had; the reason is the message."""


def _env_agent(root: Path) -> dict:
    p = root / ".env.agent"
    out = {}
    if not p.is_file():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def declared_sha256(root: Path) -> str:
    p = root / "context" / "00-normative-base.md"
    if not p.is_file():
        return ""
    m = re.search(r"^primary_copy:\s*\n(?:\s+.*\n)*?\s+sha256:\s*\"?([0-9a-f]{64})\"?", p.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else ""


def locate(root: Path) -> Path:
    """The primary copy, verified; raises Unavailable with the reason."""
    override = os.environ.get("SGAI_NORMATIVE_PDF", "").strip()
    pdf = override or _env_agent(root).get("NORMATIVE_PDF_PATH", "").strip()
    if not pdf:
        raise Unavailable("the primary copy is not declared (NORMATIVE_PDF_PATH in .env.agent, or SGAI_NORMATIVE_PDF)")
    path = Path(pdf)
    if not path.is_file():
        raise Unavailable(f"the primary copy is not at the declared path"
                          f"{' (SGAI_NORMATIVE_PDF)' if override else ''}")
    want = declared_sha256(root)
    if not want:
        raise Unavailable("context/00-normative-base.md declares no primary_copy sha256")
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    if h.hexdigest() != want:
        raise Unavailable("the file at the declared path is not the primary copy context/00 declares (sha256 differs)")
    return path


def index_from_text(text: str) -> set:
    found = set()
    for line in text.splitlines():
        if "....." in line:
            continue
        m = HEADING.match(line)
        if m:
            found.add(m.group(1))

    def rooted(n: str) -> bool:
        return n in found and ("." not in n or rooted(n.rsplit(".", 1)[0]))

    return {n for n in found if rooted(n)}


def index(root: Path) -> set:
    """Clause numbers of the primary copy; raises Unavailable."""
    pdf = locate(root)
    try:
        r = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        raise Unavailable("pdftotext is not installed (poppler-utils)")
    except subprocess.TimeoutExpired:
        raise Unavailable("pdftotext did not finish in 300 s")
    if r.returncode != 0:
        raise Unavailable(f"pdftotext failed (rc={r.returncode})")
    return complete(index_from_text(r.stdout))


def complete(idx: set) -> set:
    """idx, if it holds every top-level clause; raises Unavailable otherwise."""
    missing = [n for n in TOP_LEVEL if n not in idx]
    if missing:
        raise Unavailable(f"the extracted clause index lacks top-level clauses {missing}: the extraction did not read the document")
    return idx
