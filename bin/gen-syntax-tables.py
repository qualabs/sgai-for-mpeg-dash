#!/usr/bin/env python3
"""Generate the schema-tied tables of §5 from the XSDs and syntax.yaml (ADR 0062).

The syntax has one source. `spec-source/syntax/sgai-extension.xsd` (ours) and
ISO's 6th-edition `DASH-MPD.xsd` (the base, through bin/conformance/iso.py)
give presence, type, default, cardinality and enumerations;
`spec-source/syntax/syntax.yaml` gives only what a schema cannot say: the
description, a semantic default, which base element a row describes, a CM or
"—" presence code. Each table becomes `spec-source/syntax/tables/<id>.md`,
which the prose includes with `{{include:syntax/tables/<id>.md}}`.

A cell whose published text cannot be derived carries that text in the row's
`override`. Every override is reported. Then the published table — overrides
included — is cross-checked against the schemas, and every disagreement is
reported too; neither is fixed here (the published text stays byte-identical).

Cross-checks, on the text the table publishes:
  presence    M => use="required"; O => optional, no schema default;
              OD, CM, "—" => optional; any other code is a disagreement
  type        the first `code` span of the Type cell = the schema type
              (prefix dropped, xs: kept)
  default     a schema default => the cell is that literal (`x`, "(base)"
              allowed); a literal the schema does not declare is reported
  cardinality "<min> … <max|N>" = minOccurs/maxOccurs
  element type  the Type cell of an element table = the element's type
  enum        the `code` spans of the value column = the enumeration
              (unions flattened; a builtin member appears as `xs:...`)
  completeness  every attribute/child of one of OUR types has a row

Usage:
  bin/gen-syntax-tables.py [--source DIR] [--iso DIR] [--findings FILE] --write
      write every fragment and the findings file.
  bin/gen-syntax-tables.py [--source DIR] [--iso DIR] [--findings FILE] --check
      are the fragments and the findings file on disk what the generator
      produces, and is each table included exactly once by the prose?

What a green says: the fragments are generated from the schemas and
syntax.yaml, and every override and every disagreement is in the findings
file. What it does not say: that a description is right, that the findings
were acted on, or anything about tables of §5 that are prose (layouts,
budget, parameters).

Exit codes: 0 identical / written · 1 a fragment or the findings file
differs, a directive is missing or doubled, or syntax.yaml names something
the schema lacks · 2 a schema or syntax.yaml cannot be read (ISO's schema
not available) · 64 wrong command line.
"""
from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
XS = "{http://www.w3.org/2001/XMLSchema}"
FINDINGS = os.path.join(ROOT, ".project", "phases", "10-code-first-pipeline", "tasks", "T-03", "findings.md")
PRESENCE = ("M", "O", "OD", "CM", "—")
ELLIPSIS = " … "


class Unreadable(Exception):
    """A source cannot be read: the run cannot tell (exit 2)."""


class SourceError(Exception):
    """syntax.yaml and the schema do not fit together (exit 1)."""


# ---------------------------------------------------------------- schema

def local(qname):
    if qname is None:
        return None
    if qname.startswith("xs:"):
        return qname
    return qname.split(":", 1)[-1]


class Schema:
    """The parts of one XSD the tables need, by local name."""

    def __init__(self, text, label):
        self.label = label
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            raise Unreadable(f"{label}: {e}") from e
        self.complex = {c.get("name"): c for c in root.findall(XS + "complexType")}
        self.simple = {s.get("name"): s for s in root.findall(XS + "simpleType")}
        self.elements = {e.get("name"): e for e in root.findall(XS + "element")}

    @classmethod
    def load(cls, path):
        try:
            with open(path, "rb") as fh:
                return cls(fh.read(), os.path.basename(path))
        except OSError as e:
            raise Unreadable(f"cannot read {path}: {e}") from e

    def _ctype(self, name):
        if name not in self.complex:
            raise SourceError(f"{self.label} has no complexType {name}")
        return self.complex[name]

    def _bases(self, ct):
        """The type, then the types it extends (same schema), nearest first."""
        out = [ct]
        for ext in ct.iter(XS + "extension"):
            base = local(ext.get("base"))
            if base in self.complex:
                out.extend(self._bases(self.complex[base]))
        return out

    def attributes(self, type_name):
        """name -> {type, required, default}; inherited ones included."""
        out = {}
        for ct in reversed(self._bases(self._ctype(type_name))):
            for a in ct.iter(XS + "attribute"):
                if a.get("name") is None:
                    continue           # ref= (xlink): not tabled
                out[a.get("name")] = {
                    "type": local(a.get("type")),
                    "required": a.get("use") == "required",
                    "prohibited": a.get("use") == "prohibited",
                    "default": a.get("default"),
                }
        return out

    def children(self, type_name):
        """name -> {min, max, type}; element name= or ref=."""
        out = {}
        for ct in reversed(self._bases(self._ctype(type_name))):
            for e in ct.iter(XS + "element"):
                name = e.get("name") or local(e.get("ref"))
                typ = e.get("type")
                if typ is None and e.get("ref"):
                    g = self.elements.get(local(e.get("ref")))
                    typ = g.get("type") if g is not None else None
                out[name] = {"min": e.get("minOccurs", "1"), "max": e.get("maxOccurs", "1"),
                             "type": local(typ)}
        return out

    def enumeration(self, type_name):
        """The values a simple type admits: enumerations, unions flattened, a
        builtin member type as its own `xs:` name."""
        if type_name.startswith("xs:"):
            return [type_name]
        st = self.simple.get(type_name)
        if st is None:
            raise SourceError(f"{self.label} has no simpleType {type_name}")
        union = st.find(XS + "union")
        if union is not None:
            out = []
            for m in union.get("memberTypes", "").split():
                out += [v for v in self.enumeration(local(m)) if v not in out]
            return out
        return [e.get("value") for e in st.iter(XS + "enumeration")]


# ---------------------------------------------------------------- cells

def code_spans(cell):
    return re.findall(r"`([^`]+)`", cell)


def first_code(cell):
    spans = code_spans(cell)
    return spans[0] if spans else None


def cardinality(min_, max_):
    return f"{min_}{ELLIPSIS}{'N' if max_ == 'unbounded' else max_}"


def check_presence(code, attr):
    """The presence code against the schema attribute; a list of problems."""
    if code not in PRESENCE:
        return [(f"presence {code!r}", f"a code among {', '.join(PRESENCE)}")]
    if code == "M" and not attr["required"]:
        return [("presence M", "optional")]
    if code != "M" and attr["required"]:
        return [(f"presence {code}", 'use="required"')]
    if code == "O" and attr["default"] is not None:
        return [("presence O (no default)", f"default {attr['default']!r}")]
    return []


def check_type(cell, attr_type):
    t = first_code(cell)
    if t != attr_type:
        return [(f"type {t or cell!r}", f"type {attr_type!r}")]
    return []


def check_default(cell, schema_default):
    literal = cell.startswith("`")
    value = first_code(cell) if literal else None
    if schema_default is not None:
        if not literal:
            return [(f"default {cell!r}", f"default {schema_default!r}")]
        if value != schema_default:
            return [(f"default {value!r}", f"default {schema_default!r}")]
        return []
    if literal:
        return [(f"default {value!r}", "no default")]
    return []


def check_cardinality(cell, child):
    m = re.fullmatch(r"(\d+)" + ELLIPSIS + r"(\d+|N)( each)?", cell)
    want = cardinality(child["min"], child["max"])
    if not m:
        return [(f"cardinality {cell!r} (not '<min> … <max|N>')", f"cardinality {want!r}")]
    got = f"{m.group(1)}{ELLIPSIS}{m.group(2)}"
    if got != want:
        return [(f"cardinality {got!r}", f"cardinality {want!r}")]
    return []


def check_enum(value_cells, tokens):
    listed = []
    for c in value_cells:
        listed += code_spans(c)
    problems = []
    for v in listed:
        if v not in tokens:
            problems.append((f"value {v!r}", "not enumerated"))
    for v in tokens:
        if v not in listed:
            problems.append(("no row", f"value {v!r} enumerated"))
    return problems


# ---------------------------------------------------------------- tables

ATTR_HEADER = ["Attribute", "Required", "Type", "Default", "Description"]


def md_row(cells):
    return "| " + " | ".join(cells) + " |\n"


def md_table(header, rows):
    return md_row(header) + "|" + "---|" * len(header) + "\n" + "".join(md_row(r) for r in rows)


class Result:
    def __init__(self):
        self.overrides = []      # (table, row, column, published, derived)
        self.disagreements = []  # (table, row, table says, schema says)
        self.missing = []        # (table, what)


def schema_for(table, row, schemas):
    key = row.get("schema", table.get("schema", "svta"))
    if key not in schemas:
        raise SourceError(f"{table['id']}: unknown schema {key!r}")
    return schemas[key]


def apply(table, row, label, column, derived, res):
    over = (row.get("override") or {}).get(column)
    if over is None:
        return derived
    if over == derived:
        raise SourceError(f"{table['id']} {label}: override of {column} equals the derived text; drop it")
    res.overrides.append((table["id"], label, column, over, derived))
    return over


def gen_attributes(table, schemas, res):
    rows = []
    seen = set()
    for row in table["rows"]:
        schema = schema_for(table, row, schemas)
        tname = row.get("type", table.get("type"))
        attrs = schema.attributes(tname)
        name = row["name"]
        if name not in attrs:
            raise SourceError(f"{table['id']}: {schema.label} type {tname} has no attribute {name}")
        a = attrs[name]
        seen.add((tname, name))
        label = f"{row['base_element']}@{name}" if row.get("base_element") else f"@{name}"
        base = schema.label != "sgai-extension.xsd"
        sem_default = row.get("default")
        if sem_default is not None and a["default"] is not None:
            raise SourceError(f"{table['id']} {label}: syntax.yaml gives a default the schema already declares")
        code = row.get("required")
        if code is not None and code not in ("CM", "—"):
            raise SourceError(f"{table['id']} {label}: syntax.yaml may only declare CM or —, not {code!r}")
        if a["required"]:
            d_req = "M"
        elif code:
            d_req = code
        elif a["default"] is not None or sem_default is not None:
            d_req = "OD"
        else:
            d_req = "O"
        suffix = " (base)" if base and table.get("base_suffix") else ""
        if a["default"] is not None:
            d_def = f"`{a['default']}`{suffix}"
        elif sem_default is not None:
            d_def = sem_default + (suffix if sem_default.startswith("`") else "")
        else:
            d_def = "—"
        cells = [
            apply(table, row, label, "name", f"`{label}`", res),
            apply(table, row, label, "required", d_req, res),
            apply(table, row, label, "type", f"`{a['type']}`", res),
            apply(table, row, label, "default", d_def, res),
            row["description"],
        ]
        rows.append(cells)
        for p in (check_presence(cells[1], a) + check_type(cells[2], a["type"])
                  + check_default(cells[3], a["default"])):
            res.disagreements.append((table["id"], label) + p)
    if table.get("schema", "svta") == "svta" and not table.get("partial"):
        tname = table["type"]
        for n, a in schemas["svta"].attributes(tname).items():
            if (tname, n) not in seen and not a["prohibited"]:
                res.missing.append((table["id"], f"attribute @{n} of {tname}"))
    return md_table(ATTR_HEADER, rows)


def element_label(row, schema):
    if schema.label == "sgai-extension.xsd":
        return ", ".join(f"`<svta:{n}>`" for n in row["names"])
    return ", ".join(f"`{n}` (DASH namespace)" for n in row["names"])


def gen_elements(table, schemas, res):
    with_type = table.get("with_type", False)
    header = ["Element", "Cardinality"] + (["Type"] if with_type else []) + ["Description"]
    rows = []
    seen = set()
    for row in table["rows"]:
        schema = schema_for(table, row, schemas)
        tname = row.get("parent", table["parent"])
        kids = schema.children(tname)
        for n in row["names"]:
            if n not in kids:
                raise SourceError(f"{table['id']}: {schema.label} type {tname} has no child element {n}")
            seen.add(n)
        cards = {cardinality(kids[n]["min"], kids[n]["max"]) for n in row["names"]}
        types = {kids[n]["type"] for n in row["names"]}
        if len(cards) > 1 or len(types) > 1:
            raise SourceError(f"{table['id']}: grouped elements {row['names']} differ in cardinality or type")
        card = cards.pop() + (" each" if len(row["names"]) > 1 else "")
        label = element_label(row, schema)
        cells = [apply(table, row, label, "name", label, res),
                 apply(table, row, label, "cardinality", card, res)]
        if with_type:
            cells.append(apply(table, row, label, "type", f"`{types.pop()}`", res))
        cells.append(row["description"])
        rows.append(cells)
        for n in row["names"]:
            probs = check_cardinality(cells[1], kids[n])
            if with_type:
                probs += check_type(cells[2], kids[n]["type"])
            for p in probs:
                res.disagreements.append((table["id"], n) + p)
    if table.get("schema", "svta") == "svta" and not table.get("partial"):
        for n in schemas["svta"].children(table["parent"]):
            if n not in seen:
                res.missing.append((table["id"], f"child element {n} of {table['parent']}"))
    return md_table(header, rows)


def gen_enum(table, schemas, res):
    schema = schema_for(table, {}, schemas)
    tokens = schema.enumeration(table["simple_type"])
    header = [f"Enum value of `{table['of']}`" if table.get("of") else "Enum value", "Description"]
    rows = []
    values = []
    for row in table["rows"]:
        if row.get("absent"):
            derived, label = "*(absent)*", "(absent)"
        else:
            if row["value"] not in tokens:
                raise SourceError(f"{table['id']}: {table['simple_type']} does not enumerate {row['value']!r}")
            derived, label = f"`{row['value']}`", row["value"]
        cell = apply(table, row, label, "value", derived, res)
        values.append(cell)
        rows.append([cell, row["description"]])
    for p in check_enum(values, tokens):
        res.disagreements.append((table["id"], "(value column)") + p)
    return md_table(header, rows)


GENERATORS = {"attributes": gen_attributes, "elements": gen_elements, "enum": gen_enum}


def generate(spec, schemas):
    """{id: fragment text}, Result."""
    res = Result()
    out = {}
    for table in spec["tables"]:
        if table["id"] in out:
            raise SourceError(f"table id {table['id']} appears twice in syntax.yaml")
        kind = table.get("kind")
        if kind not in GENERATORS:
            raise SourceError(f"{table['id']}: unknown kind {kind!r}")
        out[table["id"]] = GENERATORS[kind](table, schemas, res)
    return out, res


def esc(s):
    """A cell of the findings table: pipes escaped, HTML comments shown."""
    return s.replace("|", "\\|").replace("\n", " ").replace("<", "&lt;")


def findings_md(res):
    out = ["# T-03 findings: the §5 tables against the schemas\n",
           "\n",
           "Generated by `bin/gen-syntax-tables.py --write`; `--check` fails when this file\n",
           "is not what the generator produces. Nothing listed here was fixed: the published\n",
           "text stays byte-identical (ADR 0062), and these are inputs for v13. \"The schema\"\n",
           "is `spec-source/syntax/sgai-extension.xsd` for our rows and ISO's 6th-edition\n",
           "`DASH-MPD.xsd` for base rows.\n",
           "\n",
           f"## Disagreements ({len(res.disagreements)})\n",
           "\n",
           "What the published table says that the schema does not say.\n",
           "\n"]
    if res.disagreements:
        out.append(md_row(["Table", "Row", "The table says", "The schema says"]) + "|---|---|---|---|\n")
        out += [md_row([t, f"`{r}`", esc(a), esc(b)]) for t, r, a, b in res.disagreements]
    else:
        out.append("None.\n")
    out += ["\n", f"## Overrides ({len(res.overrides)})\n", "\n",
            "Cells whose published text the generator cannot derive, so `syntax.yaml`\n",
            "carries it literally.\n", "\n"]
    if res.overrides:
        out.append(md_row(["Table", "Row", "Column", "Published", "Derived"]) + "|---|---|---|---|---|\n")
        out += [md_row([t, f"`{r}`" if "`" not in r else r, c, esc(p), esc(d)])
                for t, r, c, p, d in res.overrides]
    else:
        out.append("None.\n")
    out += ["\n", f"## Schema content with no row ({len(res.missing)})\n", "\n",
            "Attributes and child elements of our own types that no row of their table lists.\n", "\n"]
    if res.missing:
        out.append(md_row(["Table", "Missing"]) + "|---|---|\n")
        out += [md_row([t, w]) for t, w in res.missing]
    else:
        out.append("None.\n")
    return "".join(out)


# ---------------------------------------------------------------- driver

def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


def load_spec(path):
    try:
        import yaml
    except ImportError as e:
        raise Unreadable("PyYAML is not installed") from e
    try:
        with open(path, encoding="utf-8") as fh:
            spec = yaml.safe_load(fh)
    except (OSError, yaml.YAMLError) as e:
        raise Unreadable(f"cannot read {path}: {e}") from e
    if not isinstance(spec, dict) or not isinstance(spec.get("tables"), list):
        raise Unreadable(f"{path} has no 'tables' list")
    return spec


def iso_dir():
    sys.path.insert(0, BIN)
    from conformance import iso
    try:
        return str(iso.materialise())
    except iso.Unavailable as e:
        raise Unreadable(f"ISO's schema: {e}") from e


def read(path):
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read()
    except FileNotFoundError:
        return None


def main(argv):
    source = os.path.join(ROOT, "spec-source")
    iso = None
    findings = FINDINGS
    mode = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--source", "--iso", "--findings"):
            if i + 1 >= len(argv):
                usage(f"{a} needs a value")
            v = argv[i + 1]
            if a == "--source":
                source = v
            elif a == "--iso":
                iso = v
            else:
                findings = v
            i += 2
            continue
        if a in ("--write", "--check"):
            if mode:
                usage("exactly one of --write, --check")
            mode = a
            i += 1
            continue
        if a in ("-h", "--help"):
            print(__doc__)
            return 0
        usage(f"unknown argument {a}")
    if not mode:
        usage("exactly one of --write, --check")

    tables_dir = os.path.join(source, "syntax", "tables")
    try:
        spec = load_spec(os.path.join(source, "syntax", "syntax.yaml"))
        schemas = {"svta": Schema.load(os.path.join(source, "syntax", "sgai-extension.xsd")),
                   "dash": Schema.load(os.path.join(iso or iso_dir(), "DASH-MPD.xsd"))}
        fragments, res = generate(spec, schemas)
    except Unreadable as e:
        print(f"exit 2: {e}")
        return 2
    except SourceError as e:
        print(f"exit 1: {e}")
        return 1
    except (KeyError, TypeError) as e:
        print(f"exit 2: syntax.yaml is malformed: {e!r}")
        return 2
    report = findings_md(res)
    summary = (f"{len(fragments)} tables; {len(res.disagreements)} disagreements, "
               f"{len(res.overrides)} overrides, {len(res.missing)} rows missing")

    if mode == "--write":
        os.makedirs(tables_dir, exist_ok=True)
        for tid, text in fragments.items():
            with open(os.path.join(tables_dir, tid + ".md"), "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
        os.makedirs(os.path.dirname(findings) or ".", exist_ok=True)
        with open(findings, "w", encoding="utf-8", newline="") as fh:
            fh.write(report)
        print(f"wrote {summary}")
        return 0

    bad = []
    for tid, text in fragments.items():
        on_disk = read(os.path.join(tables_dir, tid + ".md"))
        if on_disk is None:
            bad.append(f"{tid}: no fragment on disk")
        elif on_disk != text:
            bad.append(f"{tid}: the fragment on disk is not what the generator produces")
    if os.path.isdir(tables_dir):
        for f in sorted(os.listdir(tables_dir)):
            if f.endswith(".md") and f[:-3] not in fragments:
                bad.append(f"{f[:-3]}: a fragment on disk that syntax.yaml does not declare")
    prose = read(os.path.join(source, "sgai-spec.src.md")) or ""
    for tid in fragments:
        n = prose.count("{{include:syntax/tables/" + tid + ".md}}\n")
        if n != 1:
            bad.append(f"{tid}: the prose includes it {n} times, not once")
    if read(findings) != report:
        bad.append(f"{os.path.relpath(findings, ROOT)}: not what the generator produces")
    if bad:
        print("differs:\n  " + "\n  ".join(bad))
        return 1
    print(f"identical: {summary}. This says the tables are generated and every "
          "disagreement is listed; it does not say a description is right or that a finding was acted on")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
