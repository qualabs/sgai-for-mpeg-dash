#!/usr/bin/env python3
"""Step 0.5 of the build: is context/ internally consistent?

WHAT THIS CATCHES — the mechanical failures a person reading prose does
not see and a machine does:

  * a reference to a requirement, criterion, design principle, extension
    rule, out-of-scope item or use case that is not defined anywhere;
  * the same identifier defined twice;
  * a relative markdown link to a file that does not exist.

WHAT THIS DOES NOT CATCH, and the distinction matters more than the
check does:

  * a requirement whose criterion contradicts its own body;
  * a gist that commits the reader to half of what the requirement says;
  * a citation that points at the clause next to the right one;
  * a summary upstream that still describes what the text used to say.

Every one of those is a real defect this project has found by hand, and
every one of them passes this check. A green here means the identifiers
line up. It does not mean context/ is correct, and reading it that way
is the same error as trusting a check that answers something narrower
than the question asked.

Usage:  bin/check-context-coherence.py [--quiet]
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTX = os.path.join(ROOT, "context")

DEFINITIONS = [
    (re.compile(r"^- \*\*(R\d+)\. ", re.M), "requirement"),
    (re.compile(r"^  - \*\*(R\d+\.\d+)\*\*", re.M), "criterion"),
    (re.compile(r"^- \*\*(DP-[\d.]+)\.", re.M), "design principle"),
    (re.compile(r"^- \*\*(OOS-\d+)\.", re.M), "out-of-scope item"),
    (re.compile(r"^## (DR-\d+)", re.M), "extension rule"),
    (re.compile(r"^#{3,4} (UC-\d+)", re.M), "use case"),
]
REFERENCE = re.compile(r"\b(R\d+(?:\.\d+)?|DP-[\d.]+|DR-\d+|OOS-\d+|UC-\d+)\b")
DEFINITION_LINE = re.compile(r"^\s*-? ?\*\*(R\d|DP-|OOS-|DR-|UC-)|^#{2,4} (DR-|UC-)")
LINK = re.compile(r"\]\(\.?/?([0-9A-Za-z._-]+\.md)[^)]*\)")


def main():
    quiet = "--quiet" in sys.argv
    files = sorted(glob.glob(os.path.join(CTX, "*.md")))
    if not files:
        print(f"ERROR: no hay archivos en {CTX} — no se puede verificar nada")
        return 1
    text = {f: open(f, encoding="utf-8").read() for f in files}

    defined = collections.defaultdict(list)
    for f, t in text.items():
        for pattern, _kind in DEFINITIONS:
            for m in pattern.finditer(t):
                defined[m.group(1)].append(os.path.basename(f))

    errors = []
    for ident, places in sorted(defined.items()):
        if len(places) > 1:
            errors.append(f"{ident} esta definido {len(places)} veces: {places}")

    dangling = collections.defaultdict(list)
    for f, t in text.items():
        for n, line in enumerate(t.split("\n"), 1):
            if DEFINITION_LINE.match(line):
                continue
            for m in REFERENCE.finditer(line):
                if m.group(1) not in defined:
                    dangling[m.group(1)].append(f"{os.path.basename(f)}:{n}")
    for ident, places in sorted(dangling.items()):
        shown = ", ".join(places[:4]) + (" ..." if len(places) > 4 else "")
        errors.append(f"{ident} se referencia pero no se define ({len(places)}x): {shown}")

    for f, t in text.items():
        for m in LINK.finditer(t):
            if not os.path.isfile(os.path.join(CTX, m.group(1))):
                errors.append(f"link roto en {os.path.basename(f)}: {m.group(1)}")

    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"\nFALLA: context/ no es internamente consistente "
              f"({len(errors)} problema/s). El build no debe continuar.")
        return 1
    if not quiet:
        print(f"OK: {len(defined)} identificadores definidos en "
              f"{len(files)} archivos; todas las referencias resuelven.")
        print("    Esto dice que los identificadores cierran. NO dice que "
              "context/ sea correcto:")
        print("    una contradiccion, un gist a medias o una cita a la "
              "clausula de al lado pasan por aca.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
