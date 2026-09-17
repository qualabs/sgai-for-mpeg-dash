#!/usr/bin/env python3
"""Step 0 of the build: does our declared normative base describe the
document actually on disk?

Reads the front matter of context/00-normative-base.md and compares it
against the cover of the primary copy. Exits non-zero on any mismatch,
so an orchestrator that runs this first stops instead of building on a
stale base.

It never passes when it could not look: an unreadable or missing primary
copy is an error, not a skipped check.

The primary copy is not in this repository and its location is not
declared here, because it is a property of the checkout. It is declared
once, in .env.agent, as NORMATIVE_PDF_PATH — see .env.agent.example.
SGAI_NORMATIVE_PDF overrides it for a single run and the check says so
on every run that uses it, in the output as well as on failure: a
precedence nobody is told about is how one declaration becomes two.
Without either, the check fails rather than passing quietly.

Usage:  bin/check-normative-base.py [--quiet]
"""
import hashlib
import os
import re
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECL = os.path.join(ROOT, "context", "00-normative-base.md")

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML no esta instalado y hace falta para leer la declaracion")
    sys.exit(2)


def read_env_agent():
    """Read .env.agent as KEY=VALUE. Absent file is not an error here —
    the caller reports the missing declaration with its own message."""
    path = os.path.join(ROOT, ".env.agent")
    values = {}
    if not os.path.isfile(path):
        return values
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        values[k.strip()] = v.strip().strip('"').strip("'")
    return values


def load_declaration(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit(f"ERROR: {path} no tiene front matter")
    return yaml.safe_load(m.group(1))


def cover_text(pdf_path, errors):
    """Return the first page as text, or '' having recorded why not.

    Absence and failure are errors. A check that goes green because it
    could not read the document is the failure this script exists to
    prevent.
    """
    if not os.path.isfile(pdf_path):
        errors.append(f"copia primaria ausente en {pdf_path}\n"
                      f"    no se puede verificar nada contra la norma")
        return ""
    try:
        r = subprocess.run(["pdftotext", "-f", "1", "-l", "1", pdf_path, "-"],
                           capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        errors.append("pdftotext no esta instalado (paquete poppler-utils)")
        return ""
    except subprocess.TimeoutExpired:
        errors.append(f"pdftotext no termino en 120s sobre {pdf_path}")
        return ""
    if r.returncode != 0:
        errors.append(f"pdftotext fallo (rc={r.returncode}) sobre {pdf_path}\n"
                      f"    {r.stderr.strip()[:200]}")
        return ""
    if not r.stdout.strip():
        errors.append(f"la tapa de {pdf_path} salio vacia; el instrumento no puede leer")
        return ""
    return r.stdout


def main():
    quiet = "--quiet" in sys.argv
    decl = load_declaration(DECL)
    errors, warnings = [], []

    declared = read_env_agent().get("NORMATIVE_PDF_PATH", "").strip()
    override = os.environ.get("SGAI_NORMATIVE_PDF", "").strip()
    pdf = override or declared
    if override:
        warnings.append(
            "SGAI_NORMATIVE_PDF esta seteada y tiene precedencia sobre "
            "NORMATIVE_PDF_PATH de .env.agent.\n"
            f"    usando  {override}\n"
            f"    en vez de {declared or '(sin declarar)'}")
    if not pdf:
        print("ERROR: no se sabe donde esta la copia primaria de "
              f"{decl['primary_copy']['filename']}.\n"
              "    No vive en este repositorio: es una copia licenciada de "
              "uso personal.\n"
              "    Declarala en .env.agent como NORMATIVE_PDF_PATH "
              "(ver .env.agent.example).\n"
              "    Para una corrida puntual se puede usar la variable "
              "SGAI_NORMATIVE_PDF, que tiene precedencia.\n"
              "\nFALLA: sin la copia primaria no se puede verificar nada. "
              "El build no debe continuar.")
        return 1

    cover = cover_text(pdf, errors)

    if cover:
        flat = re.sub(r"\s+", " ", cover)
        missing = [t for t in decl["cover_tokens"] if t.lower() not in flat.lower()]
        for t in missing:
            errors.append(f"la tapa NO contiene {t!r}\n"
                          f"    la declaracion no describe el documento en disco")
        want = decl["primary_copy"]["sha256"]
        got = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
        if got != want:
            errors.append("sha256 distinto: el archivo en esa ruta no es el declarado\n"
                          f"    declarado {want[:20]}...\n"
                          f"    en disco  {got[:20]}...")

    reg = os.path.join(ROOT, decl["verification_register"])
    if not os.path.isfile(reg):
        errors.append(f"el registro de verificacion declarado no existe: "
                      f"{decl['verification_register']}")

    last = decl["last_revalidation"]
    if isinstance(last, str):
        last = date.fromisoformat(last)
    age = (date.today() - last).days
    if age > decl["revalidation_max_age_days"]:
        warnings.append(f"ultima revalidacion hace {age} dias "
                        f"(umbral {decl['revalidation_max_age_days']}): "
                        f"nadie compara esta spec contra la norma desde entonces")

    for w in warnings:
        print(f"AVISO: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\nFALLA: la base normativa declarada no se pudo confirmar "
              f"({len(errors)} error/es). El build no debe continuar.")
        return 1
    if not quiet:
        print(f"OK: {decl['edition']}")
        print(f"    tapa y sha256 confirmados contra {pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
