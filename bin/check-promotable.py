#!/usr/bin/env python3
"""Does anything in this candidate have to be resolved before it moves on?

Read by two callers, and the second is the one that shapes the output:

  * a promotion into `dist/` asks it "may this be published";
  * the auto-refine loop of `build-all` asks it, after every turn,
    "can the pipeline fix what is left on its own?" — and stops only
    when the answer is no, so that what reaches a person is the short
    list of what a person has to decide.

It is NOT a convergence metric. Nothing here is compared against a
threshold or against the previous build. The validation step walks every
obligation, so what is unmet can be read off rather than estimated, and
a number was the thing that could lie: the `REGRESSION` verdict of
v7.1 -> v7.2 was an artefact of a changed audit denominator.

One count survives, and it is not a metric: units walked against units
that exist. It does not say whether the spec improved. It says whether
the step looked.

Exit codes, and the precedence between them:

  0  nothing blocks. Promotable.
  1  blocked, with the list of what blocks and who lifts it: the
     pipeline (5.a), the coordinator applying a `context/` change a
     written source dictates (5.d), or the project lead (5.b, 5.c). Only the
     last is NEEDS_HUMAN; the other two block without calling anyone.
  2  CANNOT TELL — a sidecar is missing or unparseable, the population
     arithmetic does not close, or a blocking row was never routed.

Two dominates one, and one dominates zero. Uncertainty wins because
zero blocking rows is also what a walk that never happened looks like,
and a caller that treats "cannot tell" as "carry on" has turned the
check into its opposite. When the run exits 2 it still prints the
blockers it did find, under a heading that says the list is partial.

A fourth code, 64, is how the script refuses to answer a question it
was not asked: a misspelled flag exits 64 rather than falling through
to the default run. The three meanings above must stay unreachable by
accident — someone who typed `--populacion` and got a `2` would read it
as a verdict about the build, and act on it.

What it cannot do is in the header of the report it prints, not here.

See --help for usage.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIREMENTS = os.path.join(ROOT, "context", "03-requirements.md")
USE_CASES = os.path.join(ROOT, "context", "04-use-cases.md")

# Verdicts. `full` is the word the pre-per-criterion map used for `met`;
# it is accepted so that an older sidecar parses and is reported as the
# wrong shape, rather than parsing as an empty map.
COVERAGE_BLOCKS = {"contradicted", "gap", "force-lost"}
COVERAGE_OPEN = {"partial"}
COVERAGE_CLEAR = {"met", "full", "governance"}
AUDIT_BLOCKS = {"non-conforming"}
AUDIT_OPEN = {"marginal"}
AUDIT_CLEAR = {"conforming"}

WHO = {"5.a": "pipeline", "5.b": "owner", "5.c": "owner", "5.d": "coordinator"}

# Buckets whose rows are a known fix, so a detail-review flag routed to
# one of them blocks instead of travelling
# as open: 5.a the spec edit, 5.d the `context/` edit a source dictates.
KNOWN_FIX = {"5.a", "5.d"}

ID = re.compile(
    r"\b(?:R\d+\.\d+|R\d+#p\d+|DP-[\d.]+#p\d+|OOS-\d+#p\d+|UC-\d+"
    r"|NC\d+|M\d+|C\d+|K-\d+|G-\d+|EC-\d+|A-\d+|DL-\d+|F-\d+)\b"
)


FLAG = re.compile(r"\bflag[- #]?(\d+)\b", re.I)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- population

def population():
    """Every obligation `context/` states, found positionally.

    Three groups, and the ids this returns are the contract: the
    validation step walks exactly these, so neither side is counting
    on its own and drifting from the other.
    """
    units = []
    lines = read(REQUIREMENTS).split("\n")

    owner = None
    prose_n = {}
    crit_indent = None
    in_crit = False
    top = re.compile(r"^- \*\*((?:R\d+|DP-[\d.]+|OOS-\d+))\.")
    crit = re.compile(r"^(\s*)- \*\*(R\d+\.\d+)\*\*")
    modal = re.compile(r"\bMUST NOT\b|\bMUST\b|\bSHALL NOT\b|\bSHALL\b|\bREQUIRED\b")

    for line in lines:
        m = crit.match(line)
        if m:
            units.append((m.group(2), "criterion"))
            in_crit = True
            crit_indent = len(m.group(1))
            continue
        if in_crit:
            if line.strip():
                here = len(line) - len(line.lstrip())
                if line.startswith("#") or here <= crit_indent:
                    in_crit = False
        m = top.match(line)
        if m:
            owner = m.group(1)
        if not in_crit and owner and modal.search(line):
            for _ in modal.findall(line):
                prose_n[owner] = prose_n.get(owner, 0) + 1
                units.append(("%s#p%d" % (owner, prose_n[owner]), "prose"))

    for m in re.finditer(r"^#+ (UC-\d+)", read(USE_CASES), re.M):
        units.append((m.group(1), "use-case"))
    return units


# ------------------------------------------------------------------ parsing

def tables(text):
    """Every markdown table, as (heading, header cells, list of row cells)."""
    out = []
    heading = ""
    rows = None
    header = None
    for line in text.split("\n"):
        if line.startswith("#"):
            heading = line.lstrip("# ").strip()
            rows = None
            continue
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if rows is None:
                header = cells
                rows = []
                out.append((heading, header, rows))
            elif set("".join(cells)) <= set("-: "):
                continue
            else:
                rows.append(cells)
        else:
            rows = None
    return out


def column(header, *names):
    for i, cell in enumerate(header):
        low = cell.lower()
        for name in names:
            if name in low:
                return i
    return None


def strip_marks(cell):
    return re.sub(r"[`*_]", "", cell).strip()


def verdict_of(cell):
    """The verdict a cell states, with its qualifiers dropped.

    `Conforming *as a document*` is the same verdict as `Conforming`;
    what follows the word qualifies the rationale, not the judgement.
    `non-conforming` is tested first because it contains the other.
    """
    # A leading symbol (an emoji such as ⚠ or ✅) decorates the verdict; the
    # word is the verdict. v12.1's audit wrote "⚠ marginal" and every such row
    # came out as a verdict nobody knew.
    low = re.sub(r"^[^a-z]+", "", strip_marks(cell).lower())
    for word in ("non-conforming", "conforming", "marginal"):
        if low.startswith(word):
            return word
    return low


def coverage_rows(validation):
    """The obligation coverage map: (unit, verdict) per row."""
    for heading, header, rows in tables(validation):
        low = heading.lower()
        if "coverage" not in low:
            continue
        vcol = column(header, "verdict", "status")
        if vcol is None:
            continue
        shape = "per-criterion" if column(header, "unit") is not None else "per-requirement"
        found = []
        for row in rows:
            if len(row) <= vcol:
                continue
            found.append((strip_marks(row[0]), verdict_of(row[vcol])))
        return found, shape
    return None, None


def audit_rows(audit):
    for heading, header, rows in tables(audit):
        if "inventory" not in heading.lower():
            continue
        vcol = column(header, "verdict")
        if vcol is None:
            continue
        return [
            (strip_marks(r[0]), verdict_of(r[vcol]), " ".join(r))
            for r in rows if len(r) > vcol
        ]
    return None


def suspicion_rows(audit):
    """Rows of the audit's "Suspicions" table (ADR 0057): each one a place the
    LLM suspects the base standard is violated or ambiguous and no test covers.
    None when the audit has no such table (an audit from before 0057)."""
    for heading, header, rows in tables(audit):
        if "suspicion" not in heading.lower():
            continue
        return [strip_marks(r[0]) for r in rows if r and strip_marks(r[0])]
    return None


def flagged_rows(detail):
    for heading, header, rows in tables(detail):
        if "flagged" not in heading.lower():
            continue
        return [strip_marks(r[0]) for r in rows if r]
    return None


def dispositions(validation):
    """id -> 5.a / 5.b / 5.c / 5.d, from the routing tables the step emits.

    The routing-rules subsection (5.e) carries no table of findings, so
    it is not a bucket and is not read.
    """
    out = {}
    for heading, header, rows in tables(validation):
        m = re.search(r"5\.([abcd])\b", heading)
        if not m:
            continue
        bucket = "5." + m.group(1)
        ref = column(header, "finding ref", "unit", "item")
        for row in rows:
            cell = row[ref] if ref is not None and len(row) > ref else " ".join(row)
            for found in ID.findall(strip_marks(cell)):
                out[found] = bucket
            # A detail-review flag is routed as `flag <n>` (or `flag-<n>`):
            # its id is a number, which ID does not match, so a flag routed
            # to 5.a would otherwise never block.
            for n in FLAG.findall(strip_marks(cell)):
                out["flag %s" % n] = bucket
    return out


def declared_open():
    """Units `context/` declares deliberately open. A judgement, so it
    lives where it is auditable and stable — never inferred here."""
    out = {}
    for heading, header, rows in tables(read(REQUIREMENTS)):
        if "deliberately open" not in heading.lower():
            continue
        for row in rows:
            if row and strip_marks(row[0]):
                out[strip_marks(row[0])] = strip_marks(row[1]) if len(row) > 1 else ""
    return out


# ------------------------------------------------------------------- report

HELP = """bin/check-promotable.py — what has to be resolved before this
candidate moves on.

Reads a build's analysis sidecars (spec-validation, detail-review, and
conformance-tests.json, the verdicts the conformance tests computed by
code), checks that the validation walked every
obligation `context/` states, and reports what blocks — grouped by who
lifts it, because that is the split the auto-refine loop acts on: what
only the pipeline has to fix it keeps fixing, what needs a person
stops the loop and becomes the message that reaches them, and what is
a `context/` change a written source already dictates (§5.d of the
validation) is applied by the coordinator, who relaunches and informs.

When the validation's machine summary (`spec-validation.summary.json`,
written by bin/validation-summary.py with these same parsers) sits beside
the sidecar, the map and the routing are read from it; a summary whose
sha256 is not this sidecar's is "cannot tell", never silently ignored.

It is not a score. Nothing is compared against a threshold or against
the previous build.

WHAT TO JUDGE
  (no argument)   the newest candidate in output-analysis/, found by
                  the highest v<N>- prefix that has a spec-validation sidecar
  --dist          what is published in dist/ (unversioned names)
  --from DIR      the sidecars in DIR, whatever they are called
                  there — used for testing this script

OTHER
  --population    print the obligations that must be walked, one
                  `<id><TAB><kind>` per line, and exit. This list is the
                  contract: the validation step walks exactly these ids,
                  so neither side counts on its own and drifts.
  --help          this text

EXIT CODES
  0   nothing blocks
  1   blocked — the list says what, and who lifts it, in three groups:
      "Necesita a the project lead" (5.b, 5.c), "Lo aplica el coordinador" (5.d,
      a context/ change a written source dictates) and "Lo destraba el
      pipeline" (5.a). The last line counts each: NEEDS_HUMAN,
      CONTEXT_CHANGE, PIPELINE. Only NEEDS_HUMAN calls a person; a 5.d
      row blocks promotion without doing so.
  2   cannot tell — a sidecar is missing or unparseable, the population
      arithmetic does not close, or a blocking row was never routed.
      2 wins over 1 and 1 over 0: zero blocking rows is also what a walk
      that never happened looks like, so uncertainty is never reported
      as clear. On a 2 the blockers found are still printed, marked as
      a partial list.
  64  the command line was wrong (unknown flag, --from with no
      directory, a directory that does not exist). Deliberately outside
      0/1/2 so a typo can never be read as a verdict about the build.
"""


class Usage(Exception):
    pass


def where(args):
    """The directory to judge, from a command line that is parsed
    strictly. An argument this script does not know is an argument
    someone believed in, so it is an error and never a silent default."""
    rest = [a for a in args if a != "--population"]
    target = None
    i = 0
    while i < len(rest):
        a = rest[i]
        if a == "--dist":
            if target:
                raise Usage("--dist y %s piden dos cosas distintas" % target[2])
            target = (os.path.join(ROOT, "dist"), None, "dist/")
        elif a == "--from":
            if i + 1 >= len(rest):
                raise Usage("--from necesita un directorio")
            i += 1
            path = os.path.abspath(rest[i])
            if not os.path.isdir(path):
                raise Usage("no existe el directorio %s" % rest[i])
            if target:
                raise Usage("--from y %s piden dos cosas distintas" % target[2])
            target = (path, None, rest[i])
        else:
            raise Usage("no conozco el argumento %s" % a)
        i += 1
    if target:
        return target
    base = os.path.join(ROOT, "output-analysis")
    best = None
    for name in os.listdir(base) if os.path.isdir(base) else []:
        m = re.match(r"^v([\d.]+)-spec-validation\.md$", name)
        if m:
            key = [int(p) for p in m.group(1).split(".")]
            if best is None or key > best[0]:
                best = (key, m.group(1))
    if best is None:
        return None, None, ("output-analysis/ — ningun candidato tiene los "
                            "tres sidecars")
    return base, "v%s-" % best[1], "output-analysis/ (candidato v%s)" % best[1]


def main(args):
    if "--help" in args or "-h" in args:
        sys.stdout.write(HELP)
        return 0
    try:
        target = where(args)
    except Usage as exc:
        sys.stderr.write(
            "check-promotable: %s\n"
            "    No corri nada, a proposito. Quien escribio esa linea\n"
            "    esperaba una respuesta, y un veredicto que contesta otra\n"
            "    pregunta es peor que ninguno.\n"
            "    bin/check-promotable.py --help\n" % exc)
        return 64
    if "--population" in args:
        for unit, kind in population():
            print("%s\t%s" % (unit, kind))
        return 0

    base, prefix, label = target
    uncertain = []
    blockers = []
    open_items = []

    names = {
        "validation": "spec-validation.md",
        "detail": "detail-review.md",
        "tests": "conformance-tests.json",
        "audit": "dash-conformance-audit.md",
    }
    # The LLM audit is a complement and never evidence (ADR 0057): without
    # it nothing is uncertain. The conformance tests are the evidence.
    optional = {"audit"}
    docs = {}
    for key, name in names.items():
        path = None if base is None else os.path.join(base, (prefix or "") + name)
        if path is None or not os.path.isfile(path):
            if key not in optional:
                uncertain.append("falta %s%s" % (prefix or "", name))
            docs[key] = None
        else:
            docs[key] = read(path)

    # The validation's machine summary (bin/validation-summary.py, ADR 0068),
    # when it sits beside the sidecar, is what is read: the same functions
    # produced it, and its sha256 says it was made from this very sidecar.
    summ = None
    if docs["validation"] is not None and base is not None:
        spath = os.path.join(base, (prefix or "") + "spec-validation.summary.json")
        if os.path.isfile(spath):
            try:
                with open(spath, encoding="utf-8") as fh:
                    summ = json.load(fh)
                rows_s = [(str(u), str(v)) for u, v in summ["rows"]]
                shape_s, disp_s = summ["shape"], dict(summ["dispositions"])
                stale = summ["sidecar_sha256"] != hashlib.sha256(
                    docs["validation"].encode("utf-8")).hexdigest()
            except (ValueError, KeyError, TypeError):
                summ, stale = None, False
                uncertain.append("spec-validation.summary.json no se puede leer")
            else:
                if stale:
                    summ = None
                    uncertain.append("spec-validation.summary.json no es de este sidecar "
                                     "(sha256 distinto): hay que regenerarlo")

    if summ is not None:
        disp = disp_s
    else:
        disp = dispositions(docs["validation"] or "")
    open_declared = declared_open()

    # --- coverage map + the arithmetic ------------------------------------
    if docs["validation"] is not None:
        rows, shape = (rows_s, shape_s) if summ is not None else coverage_rows(docs["validation"])
        if rows is None:
            uncertain.append(
                "no encontre el mapa de cobertura en spec-validation.md")
        else:
            expected = [u for u, _ in population()]
            seen = set(u for u, _ in rows)
            missing = [u for u in expected if u not in seen]
            if shape == "per-requirement":
                uncertain.append(
                    "el mapa esta indexado por requerimiento y no por criterio: "
                    "%d filas contra %d unidades que context/ declara. Una "
                    "contradiccion en un criterio queda adentro de la celda de "
                    "su requerimiento, que es donde no bloquea nada. "
                    "Hay que volver a correr la validacion." % (len(rows), len(expected)))
            elif missing:
                uncertain.append(
                    "el recorrido no cubrio %d de %d unidades. Primeras: %s"
                    % (len(missing), len(expected), ", ".join(missing[:8])))
            for unit, verdict in rows:
                if verdict in COVERAGE_BLOCKS:
                    if unit in open_declared:
                        open_items.append(("declarado abierto", unit, open_declared[unit]))
                    else:
                        blockers.append((unit, verdict, disp.get(unit)))
                elif verdict in COVERAGE_OPEN:
                    open_items.append((verdict, unit, ""))
                elif verdict not in COVERAGE_CLEAR and verdict:
                    uncertain.append("veredicto que no conozco en %s: %s" % (unit, verdict))

    # --- conformance tests: verdicts computed by code (ADR 0057) ----------
    if docs["tests"] is not None:
        try:
            tests = json.loads(docs["tests"])
            results, cannot = tests["results"], tests.get("cannot", [])
        except (ValueError, KeyError, TypeError):
            tests, results, cannot = None, None, None
            uncertain.append("conformance-tests.json no se puede leer")
        if tests is not None:
            for reason in cannot:
                uncertain.append("los tests de conformidad no pueden decir: %s" % reason)
            for res in results:
                if res.get("outcome") != "FAIL":
                    continue
                unit = "%s@%s" % (res.get("rule"), res.get("subject"))
                if str(res.get("rule", "")).startswith("P-"):
                    # Players report and do not block until their runs are stable.
                    open_items.append(("player FAIL (informa)", unit, ""))
                else:
                    blockers.append((unit, "conformance FAIL", "5.a"))

    # --- audit: suspicions, never verdicts (ADR 0057) ---------------------
    if docs["audit"] is not None:
        sus = suspicion_rows(docs["audit"])
        if sus is not None:
            for unit in sus:
                open_items.append(("sospecha del audit", unit, ""))
        else:
            # An audit written before ADR 0057 carries verdicts; they are read
            # as suspicions, never as verdicts.
            for unit, verdict, whole in audit_rows(docs["audit"]) or []:
                if "fetch-failed" in whole or verdict in AUDIT_BLOCKS or verdict in AUDIT_OPEN:
                    open_items.append(("sospecha del audit", unit, ""))

    # --- detail review -----------------------------------------------------
    if docs["detail"] is not None:
        rows = flagged_rows(docs["detail"])
        if rows is None:
            uncertain.append("no encontre la tabla de flags en detail-review.md")
        else:
            for unit in rows:
                tag = "flag %s" % unit
                bucket = disp.get(tag) or disp.get(unit)
                if bucket in KNOWN_FIX:
                    blockers.append((tag, "flag con arreglo conocido", bucket))
                else:
                    open_items.append(("flagged", tag, ""))

    unrouted = [b for b in blockers if b[2] is None]
    if unrouted:
        uncertain.append(
            "%d fila(s) bloqueante(s) sin rutear en §5 de la validacion, asi que "
            "no se sabe quien las destraba: %s"
            % (len(unrouted), ", ".join(b[0] for b in unrouted[:8])))

    needs_human = [b for b in blockers if WHO.get(b[2]) == "owner"]
    by_pipeline = [b for b in blockers if WHO.get(b[2]) == "pipeline"]
    by_coordinator = [b for b in blockers if WHO.get(b[2]) == "coordinator"]

    # --- print -------------------------------------------------------------
    code = 2 if uncertain else (1 if blockers else 0)
    print("Candidato: %s" % label)
    if code == 2:
        print("\nNO SE PUEDE SABER — %d motivo(s)" % len(uncertain))
        for u in uncertain:
            print("  · %s" % u)
        if blockers:
            print("\n  Lo que igual se vio bloqueando (lista PARCIAL, %d):" % len(blockers))
    elif code == 1:
        print("\nBLOQUEADO — %d item(s)" % len(blockers))
    else:
        print("\nNADA BLOQUEA. Promovible.")

    if blockers:
        if needs_human:
            print("\n  Necesita al líder del proyecto (%d)" % len(needs_human))
            for unit, verdict, bucket in needs_human:
                print("    %-8s %-30s %s" % (unit, verdict, bucket))
        if by_coordinator:
            print("\n  Lo aplica el coordinador (%d) — cambio en context/ que ya dicta"
                  " una fuente escrita (§5.d)" % len(by_coordinator))
            for unit, verdict, bucket in by_coordinator:
                print("    %-8s %-30s %s" % (unit, verdict, bucket))
        if by_pipeline:
            print("\n  Lo destraba el pipeline (%d)" % len(by_pipeline))
            for unit, verdict, bucket in by_pipeline:
                print("    %-8s %-30s %s" % (unit, verdict, bucket))
        rest = [b for b in blockers
                if b not in needs_human and b not in by_pipeline and b not in by_coordinator]
        if rest:
            print("\n  Sin rutear (%d) — no se sabe quien los destraba" % len(rest))
            for unit, verdict, _ in rest:
                print("    %-8s %s" % (unit, verdict))

    print("\n  Abierto y NO bloquea (%d) — viaja publicado en los sidecars" % len(open_items))
    kinds = {}
    for kind, _, _ in open_items:
        kinds[kind] = kinds.get(kind, 0) + 1
    if kinds:
        print("    " + " · ".join("%d %s" % (n, k) for k, n in sorted(kinds.items())))

    print("\n  No certificado por esta corrida")
    print("    los FAIL de conformidad los calcula codigo (conformance-tests.json);")
    print("    el mapa de cobertura no: sus veredictos los produce un modelo: un `met` con una cita que")
    print("    no dice lo que el criterio exige es indistinguible de uno real.")
    print("    Esto mide el mapa, no el spec, y nada aca valida context/.")

    print("\nPROMOTABLE=%s BLOCKERS=%d NEEDS_HUMAN=%d PIPELINE=%d CONTEXT_CHANGE=%d"
          " OPEN=%d UNCERTAIN=%d"
          % ("si" if code == 0 else "no", len(blockers), len(needs_human),
             len(by_pipeline), len(by_coordinator), len(open_items), len(uncertain)))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
