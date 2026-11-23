"""Reading context/03-requirements.md: its criteria, the text each one has,
the "Interfaces" index and the "Retired identifiers" table.

The index, the criterion pattern and the table rows are read with the code
of bin/check-context-interfaces.py, imported and not rewritten (ADR 0050), so
the two cannot read 03 differently.

THE TEXT OF A CRITERION, which `criterion_sha256` pins, is defined here and
nowhere else:

  * it starts at the bullet line `- **R<n>.<n>** (<holder>):`;
  * it runs over every following line that is blank or indented deeper than
    that bullet, so a criterion's own continuation paragraphs, tables and
    privacy notes belong to it;
  * it stops at the first non-blank line indented no deeper than the bullet:
    the next criterion of the same level, the next requirement, or the
    requirement's own prose that follows its criteria;
  * it is whitespace-normalised: every run of whitespace becomes one space,
    and the ends are stripped. Re-wrapping a paragraph does not change it;
    changing a word does.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

REQUIREMENTS = "03-requirements.md"
_CHECKER = Path(__file__).resolve().parents[2] / "check-context-interfaces.py"
PINS_FILE = Path(__file__).with_name("pins.json")


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_context_interfaces", _CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cci = _load_checker()


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sha256(text: str) -> str:
    return hashlib.sha256(normalise(text).encode("utf-8")).hexdigest()


def criteria(text: str) -> dict:
    """{criterion id: (holder, normalised criterion text)} in document order."""
    lines = text.split("\n")
    starts = []
    for n, line in enumerate(lines):
        m = cci.CRITERION.match(line)
        if m:
            starts.append((n, m.group(1), m.group(2)))
    out = {}
    for n, cid, holder in starts:
        indent = len(lines[n]) - len(lines[n].lstrip(" "))
        body = [lines[n]]
        for line in lines[n + 1:]:
            if line.strip() and len(line) - len(line.lstrip(" ")) <= indent:
                break
            body.append(line)
        out[cid] = (holder, normalise("\n".join(body)))
    return out


def retired(text: str) -> dict:
    """{retired id: where its content went}, from the "Retired identifiers" table."""
    block = cci.section(text, "Retired identifiers")
    if block is None:
        return {}
    return {ident: dest for ident, dest in cci.rows(block) if cci.ID.fullmatch(ident)}


def index(text: str) -> tuple[dict, list]:
    """({interface: [(element, criterion id)]}, what could not be read)."""
    body = cci.section(text, "Interfaces")
    if body is None:
        return {}, ['no "## Interfaces" section in 03']
    return cci.interface_index(body)


def read(context_dir) -> str:
    return (Path(context_dir) / REQUIREMENTS).read_text(encoding="utf-8")


def pins() -> dict:
    """The criteria as the catalogue was written against them:
    {id: {"holder", "sha256", "text"}}. A pin is updated by hand, one
    criterion at a time and after re-reading the rule, with pin_entry()."""
    return json.loads(PINS_FILE.read_text(encoding="utf-8"))


def pin_entry(text: str, cid: str) -> dict:
    holder, body = criteria(text)[cid]
    return {"holder": holder, "sha256": sha256(body), "text": body}
