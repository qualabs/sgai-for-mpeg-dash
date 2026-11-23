"""Level 2 catalog: the document criteria of context/03 (ADR 0050).
T-05 fills RULES and implements stale()."""
RULES: list = []


def stale(context_dir) -> list:
    """Reasons a rule no longer matches context/03 (retired id, changed text).
    Non-empty means the run cannot tell (exit 2)."""
    return []
