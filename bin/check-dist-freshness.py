#!/usr/bin/env python3
"""Is what `dist/` holds still built from the inputs that are on disk?

Answered by **content**, never by date. A fresh clone gives every file
today's mtime and a `touch` marks a file stale that nobody changed, so a
timestamp comparison is wrong in both directions.

The build records a manifest of its inputs — one sha256 per file across
`context/`, `context-analysis/` and `prompts/` — as `dist/inputs.sha256`.
This script recomputes that manifest and diffs it, so a mismatch names
the files that moved rather than reporting a bare "stale".

Usage:
  bin/check-dist-freshness.py            compare dist/ against the inputs
  bin/check-dist-freshness.py --write    record the current inputs as the
                                         manifest of what is in dist/
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKED = ("context", "context-analysis", "prompts")
MANIFEST = os.path.join(ROOT, "dist", "inputs.sha256")


def manifest_now():
    rows = {}
    for top in TRACKED:
        base = os.path.join(ROOT, top)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames.sort()
            for name in sorted(filenames):
                if name.startswith("."):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, ROOT)
                with open(full, "rb") as fh:
                    rows[rel] = hashlib.sha256(fh.read()).hexdigest()
    return rows


def read_manifest(path):
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            digest, _, rel = line.partition("  ")
            if rel:
                rows[rel] = digest
    return rows


def main():
    now = manifest_now()

    if "--write" in sys.argv:
        os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
        with open(MANIFEST, "w", encoding="utf-8") as fh:
            fh.write("# Inputs of the build currently published in dist/.\n")
            fh.write("# Recorded by bin/check-dist-freshness.py --write at\n")
            fh.write("# promotion time. Compared by content, never by date.\n")
            for rel in sorted(now):
                fh.write(f"{now[rel]}  {rel}\n")
        print(f"OK: manifiesto escrito con {len(now)} archivos de entrada.")
        return 0

    if not os.path.isfile(MANIFEST):
        print("AVISO: dist/ no tiene manifiesto de entradas.\n"
              "    Lo que esta publicado se construyo antes de que existiera\n"
              "    este mecanismo, asi que con que entradas se hizo NO SE SABE.\n"
              "    Tratalo como desactualizado: la proxima promocion escribe\n"
              "    el manifiesto y a partir de ahi la pregunta se contesta.")
        return 1

    was = read_manifest(MANIFEST)
    changed = sorted(p for p in was.keys() & now.keys() if was[p] != now[p])
    added = sorted(now.keys() - was.keys())
    removed = sorted(was.keys() - now.keys())

    if not (changed or added or removed):
        print(f"OK: dist/ esta construido con las entradas actuales "
              f"({len(now)} archivos, sin diferencias).")
        return 0

    print("dist/ NO refleja las entradas actuales:")
    for p in changed:
        print(f"  cambiado  {p}")
    for p in added:
        print(f"  nuevo     {p}")
    for p in removed:
        print(f"  borrado   {p}")
    print(f"\n{len(changed) + len(added) + len(removed)} diferencia/s. "
          "Lo publicado se construyo con otra entrada; hace falta un build "
          "nuevo antes de que dist/ vuelva a ser el estado del proyecto.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
