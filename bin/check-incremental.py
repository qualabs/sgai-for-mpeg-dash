#!/usr/bin/env python3
"""The three questions the incremental path cannot leave to a prompt.

`prompts/build-incremental.prompt` applies a delta of `context/` to an
existing candidate instead of regenerating it. That only works if three
things hold, and each is something an agent can reason its way around
while a non-zero exit cannot:

  anchor       which `context/` the base candidate was built from. The
               delta is `git diff <anchor>..HEAD -- context/`, so a
               wrong anchor silently drops or duplicates requirements.
  scope        the new candidate changed only the sections its trace
               declares, and the change is small enough to still be an
               increment. Everything else must be byte-identical.
  degradation  the document did not lose what it had: no unit the delta
               did not touch went from `met` to a blocking verdict, and the
               normative modals did not drop further than `context/`
               dropped them.

Exit codes, same contract as check-promotable.py:

  0  holds
  1  does not hold — the output says what, and its last line is
     RESULT=<word> so a caller can branch without parsing prose
  2  CANNOT TELL — an input is missing, unparseable or ambiguous.
     Never read as 0: a check that could not look has not passed.
  64 wrong command line. Outside 0/1/2 so a typo is never a verdict.

See --help for usage.
"""
import importlib.util
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(ROOT, "output")
ANALYSIS = os.path.join(ROOT, "output-analysis")
REQ_REL = "context/03-requirements.md"
UC_REL = "context/04-use-cases.md"

DEFAULT_MAX_FRACTION = 0.30
MODAL = re.compile(r"\bMUST NOT\b|\bMUST\b|\bSHALL NOT\b|\bSHALL\b|\bREQUIRED\b")
CLEAR = {"met", "full"}
VERSION = re.compile(r"^v\d+(?:\.\d+)?$")

# One parser for the coverage map, shared with the promotion gate, so
# the two can never read the same sidecar differently.
_spec = importlib.util.spec_from_file_location(
    "check_promotable", os.path.join(ROOT, "bin", "check-promotable.py"))
promotable = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(promotable)


HELP = """bin/check-incremental.py — the checks of the incremental path
(prompts/build-incremental.prompt).

USAGE
  anchor <vN.M>
      Print the commit whose context/ the candidate output/<vN.M>-sgai-spec.md
      was built from. A refinement consumes no context/, so this is the
      anchor of the nearest version at or below vN.M that did: the
      `Context head` recorded by output-analysis/<vN.k>-context-delta.md
      for the highest k <= M that has one (an incremental), else the
      commit that ADDED output/vN-sgai-spec.md (the major) to git — the
      commit that added it, not the last one that touched it, because
      review-spec-details autofixes a spec in place and a later commit of
      those fixes would move the anchor past context changes the build
      never saw. Exit 2 if that file is not in git history, or if the
      commit that added it also touches context/ (then git cannot say
      which came first).

  scope <base vN.M> <head vN.M> [--max-fraction F]
      Split both specs into sections (one per heading line, headings
      inside code fences ignored) and compare them byte for byte against
      the `## Sections changed` table of output-analysis/<head>-context-delta.md.
      Fails (RESULT=REJECT) when a section changed without being declared,
      or was declared and did not change. Fails (RESULT=MAJOR) when the
      changed sections exceed F of the base spec's lines, or when the
      trace's `## Not placed` table has a row of class `needs-structure`.
      F defaults to INCREMENTAL_MAX_CHANGED_FRACTION, else 0.30.

  degradation <base vN.M> <head vN.M>
      Joins the obligation coverage maps of both validation sidecars by
      unit id. A unit whose owner (R<n>, DP-<n>, OOS-<n>, UC-<n>) did not
      change in context/ between the base's anchor and HEAD, and that was
      `met` in the base, must not be contradicted, force-lost or gap in the
      head (met -> partial is printed and does not count: a refine with
      context/ unchanged already produces it, v8 -> v8.1). Also counts the
      normative modals (MUST, MUST NOT, SHALL, SHALL NOT, REQUIRED) in
      both specs, outside the RFC 2119 key-words paragraph: the spec may
      lose at most as many as 03-requirements.md lost. Either failing is
      RESULT=MAJOR.

  --help   this text

EXIT CODES
  0 holds · 1 does not hold (see RESULT=) · 2 cannot tell · 64 bad call
"""


class Usage(Exception):
    pass


class CannotTell(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def git(*args):
    res = subprocess.run(["git", "-C", ROOT] + list(args),
                         capture_output=True, text=True)
    if res.returncode != 0:
        raise CannotTell("git %s fallo: %s" % (" ".join(args), res.stderr.strip()))
    return res.stdout


def spec_path(version):
    return os.path.join(OUTPUT, "%s-sgai-spec.md" % version)


def trace_path(version):
    return os.path.join(ANALYSIS, "%s-context-delta.md" % version)


# ------------------------------------------------------------------ anchor

def anchor(version):
    """A refinement consumes no context/, so a minor's anchor is that of
    the nearest version at or below it that did: an incremental (its
    trace records the commit) or else the major it descends from."""
    major, _, minor = version[1:].partition(".")
    for m in range(int(minor or 0), 0, -1):
        trace = trace_path("v%s.%d" % (major, m))
        if os.path.isfile(trace):
            found = re.search(r"Context head:\**\s*`?([0-9a-f]{7,40})`?", read(trace))
            if not found:
                raise CannotTell("%s existe y no declara `Context head:`"
                                 % os.path.basename(trace))
            return (git("rev-parse", found.group(1)).strip(),
                    "Context head de %s" % os.path.basename(trace))
    origin = "v%s" % major
    if not os.path.isfile(spec_path(origin)):
        origin = version
    rel = os.path.relpath(spec_path(origin), ROOT)
    if not os.path.isfile(spec_path(origin)):
        raise CannotTell("no existe %s" % rel)
    added = git("log", "--diff-filter=A", "--format=%H", "--", rel).split()
    if not added:
        raise CannotTell("%s no esta en la historia de git: commitealo antes" % rel)
    commit = added[-1]
    touched = git("show", "--name-only", "--format=", commit).split()
    if any(p.startswith("context/") for p in touched):
        raise CannotTell(
            "el commit %s agrega %s y tambien toca context/: no se puede saber "
            "si el candidato se genero antes o despues de ese cambio" % (commit[:7], rel))
    return commit, "commit que agrego %s" % rel


# ------------------------------------------------------------------- scope

def sections(text):
    """heading text -> section bytes (heading line + body up to next heading)."""
    out = {}
    order = []
    current = "(preamble)"
    buf = []
    fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        m = None if fence else re.match(r"^#{1,6} (.*\S)\s*$", line)
        if m:
            if current in out:
                raise CannotTell("encabezado repetido: %r" % current)
            out[current] = "\n".join(buf)
            order.append(current)
            current = m.group(1)
            buf = []
        buf.append(line)
    if current in out:
        raise CannotTell("encabezado repetido: %r" % current)
    out[current] = "\n".join(buf)
    order.append(current)
    return out, order


def trace_table(text, word):
    for heading, header, rows in promotable.tables(text):
        if word in heading.lower():
            return header, rows
    return None, None


def scope(base, head, max_fraction):
    for v in (base, head):
        if not os.path.isfile(spec_path(v)):
            raise CannotTell("no existe output/%s-sgai-spec.md" % v)
    if not os.path.isfile(trace_path(head)):
        raise CannotTell("no existe output-analysis/%s-context-delta.md" % head)
    old, _ = sections(read(spec_path(base)))
    new, _ = sections(read(spec_path(head)))
    trace = read(trace_path(head))

    header, rows = trace_table(trace, "sections changed")
    if rows is None:
        raise CannotTell("la traza no tiene la tabla `## Sections changed`")
    declared = set(promotable.strip_marks(r[0]).lstrip("# ").strip() for r in rows if r)

    changed = set(k for k in set(old) | set(new) if old.get(k) != new.get(k))
    undeclared = sorted(changed - declared)
    phantom = sorted(declared - changed)

    base_lines = sum(s.count("\n") + 1 for s in old.values())
    touched_lines = sum(old[k].count("\n") + 1 for k in changed if k in old)
    touched_lines += sum(new[k].count("\n") + 1 for k in changed if k not in old)
    fraction = touched_lines / float(base_lines or 1)

    _, unplaced = trace_table(trace, "not placed")
    header_np, _ = trace_table(trace, "not placed")
    structural = []
    if unplaced:
        col = promotable.column(header_np, "class")
        if col is None:
            raise CannotTell("la tabla `## Not placed` no tiene columna Class")
        structural = [" | ".join(r) for r in unplaced
                      if len(r) > col and promotable.strip_marks(r[col]) == "needs-structure"]

    print("Base %s -> candidato %s" % (base, head))
    print("  secciones: %d en la base, %d en el candidato, %d cambiaron, %d declaradas"
          % (len(old), len(new), len(changed), len(declared)))
    print("  lineas en secciones cambiadas: %d de %d (%.1f%%, tope %.0f%%)"
          % (touched_lines, base_lines, 100 * fraction, 100 * max_fraction))
    for k in undeclared:
        print("  CAMBIO SIN DECLARAR: %s" % k)
    for k in phantom:
        print("  DECLARADA Y SIN CAMBIO: %s" % k)
    for row in structural:
        print("  NECESITA ESTRUCTURA: %s" % row)

    if undeclared or phantom:
        print("RESULT=REJECT")
        return 1
    if fraction > max_fraction or structural:
        print("RESULT=MAJOR")
        return 1
    print("RESULT=IN_SCOPE")
    return 0


# ------------------------------------------------------------- degradation

def owner_blocks(req_text, uc_text):
    """owner id -> its text, for every requirement / principle / OOS / UC."""
    out = {}
    top = re.compile(r"^- \*\*((?:R\d+|DP-[\d.]+|OOS-\d+))\.")
    current = None
    for line in req_text.split("\n"):
        m = top.match(line)
        if m:
            current = m.group(1)
            out[current] = ""
        elif line.startswith("#"):
            current = None
        if current:
            out[current] += line + "\n"
    current = None
    for line in uc_text.split("\n"):
        m = re.match(r"^#+ (UC-\d+)", line)
        if m:
            current = m.group(1)
            out[current] = ""
        elif line.startswith("#") and current and not line.startswith("####"):
            current = None
        if current:
            out[current] += line + "\n"
    return out


def owner_of(unit):
    if "#" in unit:
        return unit.split("#")[0]
    m = re.match(r"^(R\d+)\.\d+$|^(UC-\d+)$", unit)
    return (m.group(1) or m.group(2)) if m else None


def modal_count(text):
    n = 0
    skip = False
    for line in text.split("\n"):
        if line.startswith("The key words"):
            skip = True
        if skip:
            if not line.strip():
                skip = False
            continue
        n += len(MODAL.findall(line))
    return n


def validation(version):
    path = os.path.join(ANALYSIS, "%s-spec-validation.md" % version)
    if not os.path.isfile(path):
        raise CannotTell("no existe output-analysis/%s-spec-validation.md" % version)
    rows, shape = promotable.coverage_rows(read(path))
    if rows is None:
        raise CannotTell("no encontre el mapa de cobertura en %s" % os.path.basename(path))
    if shape != "per-criterion":
        raise CannotTell("%s esta indexado por requerimiento, no por criterio"
                         % os.path.basename(path))
    return dict(rows)


def degradation(base, head):
    for v in (base, head):
        if not os.path.isfile(spec_path(v)):
            raise CannotTell("no existe output/%s-sgai-spec.md" % v)
    commit, how = anchor(base)
    then = owner_blocks(git("show", "%s:%s" % (commit, REQ_REL)),
                        git("show", "%s:%s" % (commit, UC_REL)))
    now = owner_blocks(read(os.path.join(ROOT, REQ_REL)), read(os.path.join(ROOT, UC_REL)))
    touched = set(k for k in set(then) | set(now) if then.get(k) != now.get(k))
    others = [p for p in git("diff", "--name-only", commit, "--", "context/").split()
              if p not in (REQ_REL, UC_REL)]

    old = validation(base)
    new = validation(head)
    regressions = []
    softened = []
    compared = 0
    for unit, verdict in old.items():
        if verdict not in CLEAR:
            continue
        own = owner_of(unit)
        if own is None or own in touched or unit not in new:
            continue
        compared += 1
        if new[unit] in promotable.COVERAGE_BLOCKS:
            regressions.append((unit, verdict, new[unit]))
        elif new[unit] not in CLEAR:
            softened.append((unit, verdict, new[unit]))

    spec_old = modal_count(read(spec_path(base)))
    spec_new = modal_count(read(spec_path(head)))
    ctx_old = modal_count(git("show", "%s:%s" % (commit, REQ_REL)))
    ctx_new = modal_count(read(os.path.join(ROOT, REQ_REL)))
    spec_drop = spec_old - spec_new
    allowed = max(0, ctx_old - ctx_new)

    print("Base %s -> head %s  (anchor %s, %s)" % (base, head, commit[:7], how))
    print("  duenos que cambiaron en context/: %d (%s)"
          % (len(touched), ", ".join(sorted(touched)[:12]) + (" ..." if len(touched) > 12 else "")))
    if others:
        print("  tambien cambiaron, y pueden mover cualquier unidad: %s" % ", ".join(others))
    print("  unidades `met` en la base, de duenos sin cambio, comparadas: %d" % compared)
    for unit, a, b in regressions:
        print("  REGRESION: %-10s %s -> %s" % (unit, a, b))
    for unit, a, b in softened:
        print("  (no cuenta) %-10s %s -> %s" % (unit, a, b))
    print("  modales en el spec: %d -> %d; en 03-requirements: %d -> %d; caida permitida %d"
          % (spec_old, spec_new, ctx_old, ctx_new, allowed))
    lost_force = spec_drop > allowed
    if lost_force:
        print("  EL SPEC PERDIO %d MODALES MAS DE LOS QUE PERDIO context/" % (spec_drop - allowed))
    if compared == 0:
        raise CannotTell("ninguna unidad para comparar: sin eso, cero regresiones no dice nada")
    if regressions or lost_force:
        print("RESULT=MAJOR")
        return 1
    print("RESULT=NOT_DEGRADED")
    return 0


# -------------------------------------------------------------------- main

def main(args):
    if not args or "--help" in args or "-h" in args:
        sys.stdout.write(HELP)
        return 0 if args else 64
    try:
        cmd, rest = args[0], args[1:]
        max_fraction = float(os.environ.get("INCREMENTAL_MAX_CHANGED_FRACTION",
                                            DEFAULT_MAX_FRACTION))
        if "--max-fraction" in rest:
            i = rest.index("--max-fraction")
            if cmd != "scope" or i + 1 >= len(rest):
                raise Usage("--max-fraction va con scope y lleva un numero")
            try:
                max_fraction = float(rest[i + 1])
            except ValueError:
                raise Usage("--max-fraction no es un numero: %s" % rest[i + 1])
            rest = rest[:i] + rest[i + 2:]
        want = {"anchor": 1, "scope": 2, "degradation": 2}
        if cmd not in want:
            raise Usage("no conozco el subcomando %s" % cmd)
        if len(rest) != want[cmd] or not all(VERSION.match(v) for v in rest):
            raise Usage("%s lleva %d version(es) de la forma vN o vN.M" % (cmd, want[cmd]))
    except Usage as exc:
        sys.stderr.write("check-incremental: %s\n    bin/check-incremental.py --help\n" % exc)
        return 64
    try:
        if cmd == "anchor":
            commit, how = anchor(rest[0])
            print(commit)
            sys.stderr.write("(%s)\n" % how)
            return 0
        if cmd == "scope":
            return scope(rest[0], rest[1], max_fraction)
        return degradation(rest[0], rest[1])
    except CannotTell as exc:
        print("NO SE PUEDE SABER: %s" % exc)
        print("RESULT=UNCERTAIN")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
