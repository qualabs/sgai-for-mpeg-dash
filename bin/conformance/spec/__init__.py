"""Level 2 catalog: the criteria of context/03 as code (ADR 0050).

RULES holds one or more rules per criterion (catalog.py). stale() says when
the catalogue no longer matches context/03, and then the run cannot tell.
"""
from __future__ import annotations

from pathlib import Path

from . import criteria
from .catalog import RULES


def stale(context_dir, rules=None) -> list:
    """Reasons the catalogue no longer matches context/03. Non-empty means the
    run cannot tell (exit 2). Reported:

      * a rule whose criterion is in the "Retired identifiers" table;
      * a rule whose criterion is no longer in 03;
      * a rule whose criterion's text (criteria.py defines it) hashes to
        something other than the rule's criterion_sha256;
      * an element of the "Interfaces" index whose criterion no rule covers
        (a rule with a check, or a NOT_VERIFIABLE with its reason);
      * a criterion of 03 no rule covers: one added after the catalogue.
    """
    rules = RULES if rules is None else rules
    path = Path(context_dir) / criteria.REQUIREMENTS
    if not path.is_file():
        return [f"level 2: {path} does not exist, so no rule can be matched to its criterion"]
    text = path.read_text(encoding="utf-8")
    now = criteria.criteria(text)
    gone = criteria.retired(text)
    out = []
    for r in rules:
        c = r.criterion
        if c in gone:
            out.append(f"level 2: rule {r.id} cites {c}, retired in context/03 (content now in {gone[c]})")
        elif c not in now:
            out.append(f"level 2: rule {r.id} cites {c}, which context/03 no longer defines")
        elif criteria.sha256(now[c][1]) != r.criterion_sha256:
            out.append(f"level 2: rule {r.id}: the text of {c} changed since the rule was written; re-read it and re-pin")
    covering = {r.criterion for r in rules if r.check is not None or r.not_verifiable}
    idx, cannot = criteria.index(text)
    out += [f"level 2: Interfaces index unreadable: {x}" for x in cannot]
    for iface, items in idx.items():
        for element, cid in items:
            if cid not in covering:
                out.append(f"level 2: {iface} element {element!r} ({cid}) is covered by no rule")
    for c in now:
        if c not in {r.criterion for r in rules}:
            out.append(f"level 2: criterion {c} of context/03 has no rule")
    return out
