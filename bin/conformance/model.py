"""Results and rules. A verdict is a Result produced by code; nothing here
reads a verdict written by anyone else."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class Outcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_VERIFIABLE = "NOT_VERIFIABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class Result:
    rule: str            # rule id
    outcome: Outcome
    subject: str         # where: "xml#12 (line 3001)", "extension XSD", "request (line 4305)"
    xpath: str = ""      # where inside the subject
    detail: str = ""     # what was measured, or why it cannot be verified

    def as_dict(self) -> dict:
        return {"rule": self.rule, "outcome": self.outcome.value, "subject": self.subject,
                "xpath": self.xpath, "detail": self.detail}


@dataclass
class Rule:
    """One requirement turned into code.

    source: where the requirement is written, e.g. "ISO/IEC 23009-1:2026 §5.2.1"
            or "context/03 R4.1".
    quote:  the sentence, verbatim. For a base-standard rule it was found in the
            primary copy; for a context/03 rule it is the criterion text, and
            `criterion_sha256` pins it (level 2).
    applies_to: block kinds the rule reads (see extract.Block.kind), or
            "request" / "ext-xsd" / "spec".
    check:  f(ctx, subject) -> list[Result]. None means the rule cannot be
            decided by code: `not_verifiable` says why, and every applicable
            subject gets NOT_VERIFIABLE with that reason.
    """
    id: str
    level: int
    source: str
    quote: str
    applies_to: tuple
    check: Callable | None = None
    not_verifiable: str = ""
    criterion: str = ""
    criterion_sha256: str = ""
    notes: str = ""

    def result(self, outcome: Outcome, subject: str, xpath: str = "", detail: str = "") -> Result:
        return Result(self.id, outcome, subject, xpath, detail)


@dataclass
class Report:
    results: list = field(default_factory=list)
    cannot: list = field(default_factory=list)   # reasons the run cannot tell (exit 2)

    def add(self, rs):
        self.results.extend(rs)

    def counts(self) -> dict:
        c = {o.value: 0 for o in Outcome}
        for r in self.results:
            c[r.outcome.value] += 1
        return c

    def exit_code(self) -> int:
        if self.cannot:
            return 2
        return 1 if any(r.outcome is Outcome.FAIL for r in self.results) else 0
