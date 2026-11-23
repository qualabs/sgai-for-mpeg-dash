"""Level 1 catalog: base-standard rules the schema cannot express (ADR 0049).
Each Rule's quote was found in the primary copy (context/07 rules: in
context/06 or context/07). See rules.py for what is left to E-3/E-4."""
from .rules import RULES

__all__ = ["RULES"]
