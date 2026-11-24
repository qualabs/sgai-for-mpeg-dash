#!/usr/bin/env python3
"""The validation step of a candidate, as code (§B of
prompts/3-post-spec/validate-spec.prompt). The model is used only in
single-turn calls with no tools: the walkers (bin/walk-batches.py) and the
open search. Everything else — the population, what is walked, the batches,
the routing that a rule decides, the trace, the check, the sidecar and its
summary — is code, and costs no tokens.

Usage:
  bin/validate.py v<N> [--prev v<P>] [--mode refine|incremental|major]
                  [--jobs 4] [--model MODEL] [--force] [--keep]
                  [--plan-only]

  --mode defaults to what the prompt deduces: refine when
         output-analysis/v<N>-patch.json exists, incremental when
         v<N>-context-delta.md exists, major otherwise.
  --prev defaults to the newest output/v*-sgai-spec.md below v<N>. A refine
         whose output-analysis/v<P>-trace.json is missing runs as a major.
  --force  run even if the three outputs are newer than the spec and the
           conformance tests (the prompt's Skip-if).
  --keep   keep the work directory ($XDG_RUNTIME_DIR/cto/validate-v<N>-*)
  --plan-only  B.1-B.3 and the open search's messages, no model call, no
           output written: prints what would be walked and the size of
           every call (the deterministic part, measured).

What it does, by the prompt's §B:
  B.1  check-promotable.py --population; check-trace.py sources over
       output-analysis/v<N>-conformance-tests.json (missing: exit 2).
  B.2  refine: walks check-trace.py stale's units, units new to the
       population, units whose source/rules/residual changed, units whose
       v<P> verdict was not `met`, and units whose context/ text is not the
       one v<P> judged (the trace keeps a sha256 of each unit's text; an
       entry without one cannot show it is the same text, and is walked);
       carries every other unit's v<P> entry.
       The patch's sections_changed must be inside stale's changed/removed/
       added (otherwise exit 2). major, incremental: walks every unit but a
       `code` unit without residual.
  B.3  batches of at most 8 units, ordered by their first section, split
       while a batch's text exceeds 60,000 characters; W/defs.txt is §A.4's
       verdicts and kinds and the "Walker rules" block, both read from the
       prompt (exit 2 if their anchors are gone), plus the spec's section
       keys; then bin/walk-batches.py, in process.
  B.4  the open search, single-turn calls with the "Open-search rules",
       §A.1-§A.3 and §A.5 read from the prompt. refine: one call over the
       changed and added sections, the v<P> §1-§3 entries that cite a
       changed or removed section (the others carry over), the rows to
       route, the detail review's flags if it exists, and the walkers'
       FINDING notes. major, incremental: the whole spec in chunks of
       sections of at most 90,000 characters, plus at most 25,000 of
       context/ units (≈53k tokens a call with the rules, at the 2.5
       characters a token measured; the message's size is printed). Consecutive chunks overlap by one
       section — the last of one is the first of the next, when the two fit
       the budget together — so a passage that crosses the cut is read
       whole once; findings repeated across
       chunks are dropped by kind and first quotation. Every answer is
       validated by code (see OPEN SEARCH below); what fails goes back
       once; still failing: a re-judged entry is kept from v<P> unchanged,
       a new finding is dropped, a row or flag stays unrouted — each
       reported, and the exit is 1.
  B.5  the trace (with the routing kind, notes and walker verdict of each
       unit, so the next refine carries them) and check-trace.py on it. A
       unit with T-QUOTE or T-SECTION is turned not-verifiable and the
       check re-run; it must exit 0, otherwise exit 2 and nothing written.
  B.6  the sidecar rendered from the trace (§A's structure), the summary
       by bin/validation-summary.py; the three files are written together
       or not at all.

Routing decided by rule, with no model: a `contradicted` row (walker or
code FAIL) and a `force-lost` row are 5.a (§A.5.a criteria 6 and 5); a
`partial` or `gap` row in a refine whose v<P> verdict and sections are
unchanged keeps its v<P> row; a carried finding keeps its v<P> row. 5.a
holds at most 5 rows, contradicted first, force-lost last; the rest go to
"5.a Overflow (next pass)". Everything else is routed by the open search.

OPEN SEARCH answer, one JSON object per line, ending with {"done": true}:
  finding  {"id"?, "kind": gap|edge|ambiguity, "title", "text",
            "sections": [{"key", "quotes"}], "routing", <routing fields>}
  drop     {"id", "drop": true, "reason"}    (a re-judged entry only)
  row      {"unit", "routing", <routing fields>}
  flag     {"flag", "routing", <routing fields>}
  routing fields: 5.a criterion, section, edit, citation · 5.b section,
  why_uncertain, resolutions, recommended, searched · 5.c context_file,
  suggested_edit, leverage, searched · 5.d context_passage, replacement,
  source. Checked: the JSON; kind and routing values; every field of the
  bucket present and not empty; every section key (and 5.a/5.b `section`)
  exists; every quotation literal in its section (check-trace's
  normalisation); a gap names a section, an edge case or ambiguity quotes;
  an id is one that was sent, with its own kind; every sent id, row and
  flag answered; the final done line.

What a green says: the population was walked as the mode requires, every
answer has the schema and literal quotations, check-trace exits 0 on the
trace, and the sidecar's counts agree with its entries. NOT that a verdict
or a routing is right: those are the model's. The resolution chain of
§A.5 is reduced to what the call is given (context/ units and spec
sections); ADRs and the base standard are not read, so the sidecar says
[GROUNDED_BY=spec-only].

Exit codes: 0 written, everything validated · 1 written, with units
not-verifiable or open-search answers kept/dropped/unrouted (listed) ·
2 cannot tell, nothing written (an input missing, stale and the patch
disagree, the model could not be called, check-trace or the summary not
green) · 64 wrong command line.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
PROMPT = os.path.join(ROOT, "prompts", "3-post-spec", "validate-spec.prompt")
sys.path.insert(0, BIN)
import spec_sections as ss  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ct = _load("check_trace", "check-trace.py")
cp = _load("check_promotable", "check-promotable.py")
vs = _load("validation_summary", "validation-summary.py")
wb = _load("walk_batches", "walk-batches.py")

MAX_UNITS_PER_BATCH = 8
MAX_BATCH_CHARS = 60_000
OPEN_SPEC_CHARS = 90_000
OPEN_UNITS_CHARS = 25_000
# Measured on the real v12.7 -> v12.8 open search (2026-11-23): 24,722 input
# tokens for two calls of ~31k characters each, ≈2.5 characters a token.
# Used for the printed size of a call and for the budget above: 90k + 25k +
# ~17k of rules ≈ 53k tokens.
CHARS_PER_TOKEN = 2.5
OPEN_MAX_TOKENS = 60_000
TODO_CAP = 5
SKIP_KEYS = {"Table of contents"}
RANK = {"met": 0, "partial": 1, "force-lost": 2, "contradicted": 3}
BUCKETS = ("5.a", "5.b", "5.c", "5.d")
FIELDS = {"5.a": ("criterion", "section", "edit", "citation"),
          "5.b": ("section", "why_uncertain", "resolutions", "recommended", "searched"),
          "5.c": ("context_file", "suggested_edit", "leverage", "searched"),
          "5.d": ("context_passage", "replacement", "source")}
HEADERS = {"5.a": "| #  | Finding ref | Criterion | Spec section | Concrete edit | Citation |",
           "5.b": "| #  | Finding ref | Spec section | Why uncertain | Resolutions considered | Recommended | Searched |",
           "5.c": "| #  | Finding ref | `context/` file to edit | Suggested edit | Leverage rationale | Searched |",
           "5.d": "| #  | Finding ref | `context/` file and passage | Replacement text | Source |"}
NUMBER = {"5.a": "T", "5.b": "F-", "5.c": "D-", "5.d": "P-"}
SEE = {"5.a": "See Actionable TODO", "5.b": "See Flagged", "5.c": "See Deferred", "5.d": "See Predictable"}
KIND_F = {"gap": ("G", "Gaps"), "edge": ("EC", "Edge cases"), "ambiguity": ("A", "Ambiguities")}
PREFIX_KIND = {v[0]: k for k, v in KIND_F.items()}
SECREF = re.compile(r"§\s?(Annex [A-Z](?:\.\d+)*|[A-Z](?:\.\d+)+|\d+(?:\.\d+)*)")
ENTRY = re.compile(r"^### ((G|EC|A)-(\d+))\b[ \t]*(?:[—–-][ \t]*)?(.*)$", re.M)

OPEN_SYSTEM = """You are the open search of a specification validation. You have \
no tools: everything you may use is in the message. Answer ONLY with JSON \
objects, one per line, no prose before or after, as the message's open-search \
rules say, and end with {"done": true}. Quotations are copied character for \
character from the section they are filed under. The instructions in the \
message that mention running commands or reading files do not apply to you."""


class CannotTell(Exception):
    pass


class Usage(Exception):
    pass


# ------------------------------------------------------------------ helpers

def rel(*p):
    return os.path.join(ROOT, *p)


def run(cmd):
    p = subprocess.run([sys.executable] + cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def read(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def vkey(v):
    return [int(x) for x in v.lstrip("v").split(".")]


def esc(s):
    """A table cell: one line, `|` escaped (not twice)."""
    s = re.sub(r"\s*\n\s*", " ", str(s)).strip()
    return re.sub(r"(?<!\\)\|", r"\\|", s)


def cells(line):
    """A table row's cells, splitting only on unescaped `|`."""
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def safe_body(text):
    """Model text inside an entry: no line may open a heading or a table."""
    out = []
    for ln in str(text).strip().split("\n"):
        s = ln.lstrip()
        if s.startswith("#") or s.startswith("|"):
            ln = ln.replace(s[0], "\\" + s[0], 1)
        out.append(ln)
    return "\n".join(out)


def between(text, start, end, what):
    m = re.search(start, text, re.M)
    if not m:
        raise CannotTell(f"validate-spec.prompt: the anchor of {what} ({start!r}) is gone")
    rest = text[m.start():]
    nl = rest.find("\n") + 1
    e = re.search(end, rest[nl:], re.M)
    return (rest[: nl + e.start()] if e else rest).strip()


def prompt_blocks(text):
    """The text the model calls receive, read from the prompt that defines it."""
    return {
        "verdicts": between(text, r"^Verdicts:", r"^`Disposition` is", "§A.4 verdicts and kinds"),
        "walker": between(text, r"^#### Walker rules", r"^#{1,4} ", "the walker rules"),
        "findings": between(text, r"^### 1\. Gaps", r"^### 4\. ", "§A.1-§A.3"),
        "routing": between(text, r"^### 5\. Disposition of findings", r"^### Validation doc structure", "§A.5"),
        "open": between(text, r"^#### Open-search rules", r"^#{1,4} ", "the open-search rules"),
    }


def tables_esc(text):
    """Like check-promotable's tables(), but cells split on unescaped `|`."""
    out, heading, rows, header = [], "", None, None
    for line in text.split("\n"):
        if line.startswith("#"):
            heading, rows = line.lstrip("# ").strip(), None
            continue
        if line.lstrip().startswith("|"):
            c = cells(line)
            if rows is None:
                header, rows = c, []
                out.append((heading, header, rows))
            elif set("".join(c)) <= set("-: "):
                continue
            else:
                rows.append(c)
        else:
            rows = None
    return out


def code_evidence(rules, results):
    out = []
    for rid in rules:
        rs = results.get(rid, [])
        fails = [r for r in rs if r.get("outcome") == "FAIL"]
        if fails:
            out += [f"{rid}: FAIL at {r.get('subject')}#{r.get('xpath')}" for r in fails]
        else:
            n = sum(1 for r in rs if r.get("outcome") == "PASS")
            out.append(f"{rid}: PASS ({n} instance{'s' if n != 1 else ''})")
    return out


def combine(code_v, walker_v):
    """A code unit with residual: the worse of the two (contradicted >
    force-lost > partial > met). A residual judged gap while code passes is
    partial; not-verifiable wins; governance leaves the code verdict."""
    if walker_v == "not-verifiable":
        return "not-verifiable"
    if walker_v == "gap":
        walker_v = "partial" if code_v == "met" else code_v
    if walker_v not in RANK:
        return code_v
    return max([code_v, walker_v], key=lambda x: RANK[x])


def unit_hash(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


def default_kind(trace_kind):
    return "use-case" if trace_kind == "use-case" else "runtime"


# -------------------------------------------------------- previous sidecar

def prev_sidecar(text):
    """What a refine carries from v<P>'s sidecar: map rows (kind, notes,
    disposition), §1-§3 entries, and the routing rows by finding id."""
    rows, entries, route = {}, [], {}
    for heading, header, trows in tables_esc(text):
        low = heading.lower()
        if "coverage" in low and cp.column(header, "unit") is not None:
            kc, nc = cp.column(header, "kind"), cp.column(header, "notes")
            for r in trows:
                u = cp.strip_marks(r[0])
                rows[u] = {"kind": cp.strip_marks(r[kc]) if kc is not None and kc < len(r) else "",
                           "notes": r[-1] if nc is not None else ""}
        m = re.search(r"5\.([abcd])\b", heading)
        if m:
            refc = cp.column(header, "finding ref", "unit", "item")
            for i, r in enumerate(trows):
                cell = r[refc] if refc is not None and refc < len(r) else " ".join(r)
                rowid = (heading, i)
                for found in cp.ID.findall(cp.strip_marks(cell)):
                    route[found] = {"bucket": "5." + m.group(1), "cells": r, "refcol": refc, "row": rowid}
    for _, title, prefix in vs.FINDINGS:
        ch = vs.chapter(text, title)
        if ch is None:
            continue
        body = ch[1]
        ms = list(ENTRY.finditer(body))
        for j, m in enumerate(ms):
            if m.group(2) != prefix:
                continue
            end = ms[j + 1].start() if j + 1 < len(ms) else len(body)
            entry_body = body[m.end():end].strip("\n")
            entries.append({"id": m.group(1), "kind": PREFIX_KIND[prefix], "title": m.group(4).strip(),
                            "body": entry_body, "refs": SECREF.findall(entry_body)})
    return rows, entries, route


def keys_of(refs, sections):
    out = []
    for r in refs:
        k = r if r in sections else (r[len("Annex "):] if r.startswith("Annex ") and r[6:] in sections else None)
        if k and k not in out:
            out.append(k)
    return out


# ----------------------------------------------------------- the open search

def section_keys(value):
    """The section keys of a routing `section` field, as the model writes it:
    a string ("5.1.3; A.7"), a list (["6.6", "A.7"]), or a list written as a
    string ("['6.6', 'A.7']")."""
    items = value if isinstance(value, list) else re.split(r"\s*[;,]\s*", str(value or ""))
    out = []
    for k in items:
        k = str(k).strip().strip("[]").strip().strip("'\"").lstrip("§").strip()
        if k:
            out.append(k)
    return out


def check_open(objs, norm, expect_ids, expect_units, expect_flags):
    """(good {key: obj}, errors {key: [msg]}, done). Keys: id:<G-n>, unit:<u>,
    flag:<n>, new:<k>."""
    good, errs, done, nnew = {}, {}, False, 0
    for o in objs:
        if not isinstance(o, dict):
            continue
        if o.get("done") is True and len(o) == 1:
            done = True
            continue
        if "unit" in o:
            key, valid = f"unit:{o['unit']}", str(o["unit"]) in expect_units
        elif "flag" in o:
            key, valid = f"flag:{o['flag']}", str(o["flag"]) in expect_flags
        elif o.get("id"):
            key, valid = f"id:{o['id']}", str(o["id"]) in expect_ids
        else:
            nnew += 1
            key, valid = f"new:{nnew}:{str(o.get('title'))[:60]}", True
        e = []
        if not valid:
            e.append("not one of the items sent")
        if key.startswith(("id:", "new:")):
            if o.get("drop") is True:
                if not key.startswith("id:"):
                    e.append("only a re-judged entry can be dropped")
                if not str(o.get("reason") or "").strip():
                    e.append("a drop needs its reason")
                (errs if e else good)[key] = e or o
                continue
            k = o.get("kind")
            if k not in KIND_F:
                e.append(f"kind {k!r} not one of {sorted(KIND_F)}")
            elif key.startswith("id:") and KIND_F[k][0] != str(o["id"]).split("-")[0]:
                e.append(f"kind {k} does not match the id {o['id']}")
            for f in ("title", "text"):
                if not isinstance(o.get(f), str) or not o[f].strip():
                    e.append(f"{f} missing or empty")
            secs = o.get("sections")
            if not isinstance(secs, list):
                e.append("sections is not a list")
                secs = []
            nq = 0
            for s in secs:
                if not isinstance(s, dict) or s.get("key") not in norm:
                    e.append(f"section {s.get('key') if isinstance(s, dict) else s!r} does not exist")
                    continue
                for q in s.get("quotes") or []:
                    nq += 1
                    if not isinstance(q, str) or not ct.normalise(q) or ct.normalise(q) not in norm[s["key"]]:
                        e.append(f"quotation not literal in {s['key']}: {str(q)[:80]!r}")
            if k == "gap" and not secs:
                e.append("a gap names the section that needs it")
            if k in ("edge", "ambiguity") and nq == 0:
                e.append(f"an {k} entry quotes the passage")
        r = o.get("routing")
        if r not in FIELDS:
            e.append(f"routing {r!r} not one of {list(BUCKETS)}")
        else:
            for f in FIELDS[r]:
                if not str(o.get(f) if o.get(f) is not None else "").strip():
                    e.append(f"{r} needs `{f}`")
            if r in ("5.a", "5.b") and section_keys(o.get("section")):
                for k2 in section_keys(o.get("section")):
                    if k2 and k2 not in norm:
                        e.append(f"`section` {k2!r} is not a section key")
        if e:
            errs[key] = e
        else:
            good[key] = o
    for i in expect_ids:
        if f"id:{i}" not in good and f"id:{i}" not in errs:
            errs[f"id:{i}"] = ["no answer"]
    for u in expect_units:
        if f"unit:{u}" not in good and f"unit:{u}" not in errs:
            errs[f"unit:{u}"] = ["no answer"]
    for f in expect_flags:
        if f"flag:{f}" not in good and f"flag:{f}" not in errs:
            errs[f"flag:{f}"] = ["no answer"]
    return good, errs, done


def open_call(message, norm, ids, units, flags, model, usage, log=None):
    """One call and, if anything fails, one more. Returns (good, errs, done).
    `log(round, answer, errors)` keeps each answer for audit."""
    log = log or (lambda *a: None)
    text, u = wb.call_model(message, model, OPEN_SYSTEM)
    usage.append(u)
    good, errs, done = check_open(wb.parse(text), norm, ids, units, flags)
    log(1, text, errs)
    if errs or not done:
        lines = [f"{k}: " + "; ".join(v) for k, v in errs.items()]
        if not done:
            lines.append('the answer did not end with {"done": true}: it may be truncated')
        second = (message + "\n\n===== SECOND ROUND =====\nThese objects of your answer failed the check "
                  "(or were missing). Send ONLY them again, corrected, plus any finding you did not get to "
                  'send, and end with {"done": true}:\n' + "\n".join(lines))
        try:
            text, u = wb.call_model(second, model, OPEN_SYSTEM)
            usage.append(u)
            g2, e2, done = check_open(wb.parse(text), norm, ids, units, flags)
            log(2, text, e2)
        except wb.ModelError as ex:
            g2, e2 = {}, {k: v + [f"second call failed: {ex}"] for k, v in errs.items()}
        titles = {str(o.get("title")) for k, o in good.items() if k.startswith("new:")}
        failed_new = [k for k in errs if k.startswith("new:")]
        for k, o in g2.items():
            if k.startswith("new:"):
                if str(o.get("title")) not in titles:
                    titles.add(str(o.get("title")))
                    good[f"new:r2:{k}"] = o
                    # a corrected finding settles the failed one of the same title, else the first left
                    same = [f for f in failed_new if f.split(":", 2)[2] == str(o.get("title"))[:60]]
                    if same or failed_new:
                        f = (same or failed_new)[0]
                        failed_new.remove(f)
                        errs.pop(f, None)
            elif k in errs:
                good[k] = o
                errs.pop(k)
        for k in list(errs):
            if k in e2 and not k.startswith("new:"):
                errs[k] = errs[k] + ["second round: " + "; ".join(e2[k])]
    return good, errs, done


# ---------------------------------------------------------------- the step

class Step:
    def __init__(self, N, prev, mode, jobs, model, keep, plan_only):
        self.N, self.P, self.mode = N, prev, mode
        self.jobs, self.model, self.keep, self.plan_only = jobs, model, keep, plan_only
        self.spec_rel = f"output/{N}-sgai-spec.md"
        self.report = []          # degradations, for the exit code and the sidecar
        self.usage_open = []

    # B.1 -------------------------------------------------------------------
    def inputs(self):
        if not os.path.isfile(rel(self.spec_rel)):
            raise CannotTell(f"no {self.spec_rel}")
        self.conf_rel = f"output-analysis/{self.N}-conformance-tests.json"
        if not os.path.isfile(rel(self.conf_rel)):
            raise CannotTell(f"no {self.conf_rel}: Step 8.0 runs before this step, and this step does not run it")
        self.blocks = prompt_blocks(read(PROMPT))
        rc, out, err = run([os.path.join(BIN, "check-promotable.py"), "--population"])
        if rc != 0 or not out.strip():
            raise CannotTell(f"check-promotable --population exit {rc}: {err[-300:]}")
        self.pop_tsv = out
        self.pop = [tuple(ln.split("\t")) for ln in out.split("\n") if ln.strip()]
        with open(os.path.join(self.W, "population.tsv"), "w", encoding="utf-8") as fh:
            fh.write(out)
        rc, out, err = run([os.path.join(BIN, "check-trace.py"), "sources", self.conf_rel,
                            "--population", os.path.join(self.W, "population.tsv")])
        if rc != 0:
            raise CannotTell(f"check-trace sources exit {rc}: {(out + err)[-300:]}")
        self.src = json.loads(out)
        conf = json.loads(read(rel(self.conf_rel)))
        self.results = {}
        for r in conf.get("results", []):
            self.results.setdefault(r.get("rule"), []).append(r)
        self.spec_text = read(rel(self.spec_rel))
        self.secs = ct.spec_index(rel(self.spec_rel))
        self.order = [s.key for s in ss.split(self.spec_text)]
        self.norm = {k: ct.normalise(s.text) for k, s in self.secs.items()}
        self.req = read(ct.REQUIREMENTS)
        self.uc = read(ct.USE_CASES)

    # B.2 -------------------------------------------------------------------
    def plan(self):
        self.prev_units, self.prev_rows, self.prev_entries, self.prev_route = {}, {}, [], {}
        self.stale = {"changed": [], "removed": [], "added": [], "units": []}
        if self.P:
            tp = rel("output-analysis", f"{self.P}-trace.json")
            if os.path.isfile(tp):
                self.prev_units = json.loads(read(tp)).get("units", {})
            elif self.mode == "refine":
                self.report.append(f"refine without output-analysis/{self.P}-trace.json: run as a major")
                self.mode = "major"
            sp = rel("output-analysis", f"{self.P}-spec-validation.md")
            if os.path.isfile(sp):
                self.prev_rows, self.prev_entries, self.prev_route = prev_sidecar(read(sp))
        elif self.mode == "refine":
            self.report.append("refine with no previous candidate: run as a major")
            self.mode = "major"
        if self.mode == "refine":
            rc, out, err = run([os.path.join(BIN, "check-trace.py"), "stale",
                                f"output-analysis/{self.P}-trace.json",
                                "--old", f"output/{self.P}-sgai-spec.md", "--new", self.spec_rel])
            if rc != 0:
                raise CannotTell(f"check-trace stale exit {rc}: {(out + err)[-300:]}")
            self.stale = json.loads(out)
            pp = rel("output-analysis", f"{self.N}-patch.json")
            if os.path.isfile(pp):
                declared = set(json.loads(read(pp)).get("sections_changed") or [])
                seen = set(self.stale["changed"]) | set(self.stale["removed"]) | set(self.stale["added"])
                if declared - seen:
                    raise CannotTell("the patch record and the documents disagree: sections_changed "
                                     f"{sorted(declared - seen)} did not change between {self.P} and {self.N}")
        self.codeonly, self.walk, self.carry = [], [], []
        stale_units = set(self.stale["units"])
        self.unit_sha = {u: unit_hash(ct.unit_text(u, self.req, self.uc)) for u, _ in self.pop}
        for u, _ in self.pop:
            s = self.src[u]
            if s["source"] == "code" and not s.get("residual"):
                self.codeonly.append(u)
                continue
            if self.mode != "refine":
                self.walk.append(u)
                continue
            p = self.prev_units.get(u)
            if (p is None or u in stale_units or p.get("unit_sha256") != self.unit_sha[u]
                    or (p.get("source"), sorted(p.get("rules") or []), sorted(p.get("residual") or []))
                    != (s["source"], sorted(s.get("rules") or []), sorted(s.get("residual") or []))
                    or p.get("verdict") != "met"):
                self.walk.append(u)
            else:
                self.carry.append(u)

    # B.3 -------------------------------------------------------------------
    def seed(self, u):
        """Sections for a unit with none: the ones naming most of the code
        terms and attributes its text names (at most 4)."""
        t = ct.unit_text(u, self.req, self.uc) or ""
        terms = set(re.findall(r"`([^`]{3,60})`", t)) | set(re.findall(r"(@[A-Za-z]+)", t))
        terms = {x for x in terms if not re.fullmatch(r"(R|DP-|UC-|OOS-)[\d.]+", x)}
        hits = {}
        for k in self.order:
            if k in SKIP_KEYS or self.secs[k].level <= 1:
                continue
            n = sum(1 for x in terms if x in self.secs[k].text)
            if n:
                hits[k] = n
        return sorted(hits, key=lambda k: (-hits[k], self.order.index(k)))[:4]

    def draft(self):
        units = {}
        for u, kind in self.pop:
            s = self.src[u]
            e = {"kind": kind, "source": s["source"], "rules": s.get("rules") or []}
            if s.get("residual"):
                e["residual"] = s["residual"]
            keys = [x["key"] for x in (self.prev_units.get(u) or {}).get("sections") or []
                    if x.get("key") in self.secs]
            if u in self.walk and not keys:
                keys = self.seed(u)
            e["sections"] = [{"key": k, "quotes": []} for k in keys]
            units[u] = e
        self.draft_trace = {"format": "sgai-trace/1", "spec": self.spec_rel, "units": units}

    def batches(self):
        units = self.draft_trace["units"]
        pos = {k: i for i, k in enumerate(self.order)}

        def first(u):
            ks = [s["key"] for s in units[u]["sections"]]
            return min((pos[k] for k in ks), default=len(pos))
        todo = sorted(self.walk, key=lambda u: (first(u), [x[0] for x in self.pop].index(u)))
        groups = [todo[i:i + MAX_UNITS_PER_BATCH] for i in range(0, len(todo), MAX_UNITS_PER_BATCH)]
        out = []
        while groups:
            g = groups.pop(0)
            text, missing = ct.batch(self.draft_trace, self.secs, g, self.req, self.uc)
            if missing:
                raise CannotTell(f"no context/ text for {missing}: the population and the trace disagree")
            if len(text) > MAX_BATCH_CHARS and len(g) > 1:
                h = len(g) // 2
                groups[:0] = [g[:h], g[h:]]
                continue
            out.append((g, text))
        self.batch_list = out

    def notes(self, g):
        lines = []
        for u in g:
            s = self.src[u]
            if s["source"] == "code":
                lines.append(f"UNIT {u}: code already decides rules {', '.join(s['rules'])} "
                             f"(verdict {s['verdict']}). Judge only the part code cannot decide, "
                             f"rules {', '.join(s.get('residual') or [])}.")
            elif s["source"] == "vector-pending":
                lines.append(f"UNIT {u}: a Player behaviour with no test vector yet. Judge whether the "
                             "spec states the Player's obligation, with its force.")
        return "\n".join(lines)

    def write_walk(self):
        W = self.W
        keys = "\n".join(f"{s.key}\t{s.heading}" for s in ss.split(self.spec_text) if s.heading)
        defs = (f"# Walker definitions — validation of {self.spec_rel}\n\n"
                + self.blocks["verdicts"] + "\n\n" + self.blocks["walker"]
                + "\n\n## Section keys of the spec (key, heading)\n\n" + keys + "\n")
        with open(os.path.join(W, "defs.txt"), "w", encoding="utf-8") as fh:
            fh.write(defs)
        self.defs_chars = len(defs)
        for i, (g, text) in enumerate(self.batch_list, 1):
            with open(os.path.join(W, f"batch-{i}.txt"), "w", encoding="utf-8") as fh:
                fh.write(text)
            n = self.notes(g)
            if n:
                with open(os.path.join(W, f"notes-{i}.txt"), "w", encoding="utf-8") as fh:
                    fh.write("Notes for particular units:\n" + n + "\n")
        with open(os.path.join(W, "trace-draft.json"), "w", encoding="utf-8") as fh:
            json.dump(self.draft_trace, fh, indent=1, ensure_ascii=False)

    def walkers(self):
        self.answers = {}
        if not self.batch_list:
            self.walk_out = "no unit to walk"
            return
        buf = io.StringIO()
        args = [self.W, "--spec", rel(self.spec_rel), "--jobs", str(self.jobs)]
        if self.model:
            args += ["--model", self.model]
        with redirect_stdout(buf):
            rc = wb.main(args)
        self.walk_out = buf.getvalue()
        if rc == 2:
            raise CannotTell("bin/walk-batches.py: " + self.walk_out.strip()[-400:])
        for i in range(1, len(self.batch_list) + 1):
            with open(os.path.join(self.W, f"answer-{i}.jsonl"), encoding="utf-8") as fh:
                for ln in fh:
                    if ln.strip():
                        o = json.loads(ln)
                        self.answers[o["unit"]] = o

    # assemble ----------------------------------------------------------------
    def assemble(self):
        units = {}
        for u, kind in self.pop:
            s = self.src[u]
            e = {"kind": kind, "source": s["source"], "rules": s.get("rules") or []}
            if s.get("residual"):
                e["residual"] = s["residual"]
            e["unit_sha256"] = self.unit_sha[u]
            p = self.prev_units.get(u) or {}
            prow = self.prev_rows.get(u) or {}
            if u in self.codeonly:
                e.update(verdict=s["verdict"], sections=[], how="code",
                         judged_kind=p.get("judged_kind") or prow.get("kind") or default_kind(kind), notes="")
            elif u in self.carry:
                wv = p.get("walker_verdict", p.get("verdict"))
                v = combine(s["verdict"], wv) if s["source"] == "code" else p.get("verdict")
                e.update(verdict=v, sections=p.get("sections") or [], how="carried", walker_verdict=wv,
                         judged_kind=p.get("judged_kind") or prow.get("kind") or default_kind(kind),
                         notes=p.get("notes") if "notes" in p else prow.get("notes", ""))
            else:
                a = self.answers.get(u) or {"verdict": "not-verifiable", "notes": "no walker answer"}
                wv = a.get("verdict")
                v = combine(s["verdict"], wv) if s["source"] == "code" else wv
                e.update(verdict=v, sections=[{"key": x["key"], "quotes": x.get("quotes") or []}
                                              for x in a.get("sections") or []],
                         how="llm", walker_verdict=wv,
                         judged_kind=a.get("kind") or prow.get("kind") or default_kind(kind),
                         notes=a.get("notes") or "")
            units[u] = e
        self.trace = {"format": "sgai-trace/1", "spec": self.spec_rel,
                      "derived_from": f"bin/validate.py, mode {self.mode}"
                      + (f" over {self.P}" if self.P else "")
                      + f"; code verdicts from {self.conf_rel}",
                      "units": units}

    # B.5 -------------------------------------------------------------------
    def check_trace(self):
        path = os.path.join(self.W, "trace.json")
        for attempt in (1, 2):
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self.trace, fh, indent=1, ensure_ascii=False)
            rc, out, err = run([os.path.join(BIN, "check-trace.py"), path, "--spec", self.spec_rel,
                                "--population", os.path.join(self.W, "population.tsv"),
                                "--rules", self.conf_rel, "--json"])
            if rc == 0:
                self.check_out = json.loads(out)["summary"]
                return
            if rc != 1 or attempt == 2:
                raise CannotTell(f"check-trace exit {rc}: {(out + err)[-600:]}")
            found = json.loads(out)["findings"]
            other = [f for f in found if f["check"] not in ("T-QUOTE", "T-SECTION")]
            if other:
                raise CannotTell("check-trace: " + "; ".join(f"{f['check']} {f['unit']} {f['detail']}"
                                                              for f in other[:8]))
            for u in sorted({f["unit"] for f in found}):
                e = self.trace["units"][u]
                why = "; ".join(f"{f['check']} §{f.get('section')}: {f['detail']}" for f in found if f["unit"] == u)
                e.update(verdict="not-verifiable", sections=[],
                         notes=f"quotation failed bin/check-trace.py ({why})")
                self.report.append(f"{u}: not-verifiable, its quotation failed check-trace ({why})")

    # B.4 -------------------------------------------------------------------
    def routing_by_rule(self):
        """Rows routed with no model; and the rows left for the open search."""
        self.row_route, self.to_route = {}, []
        changed = set(self.stale["changed"]) | set(self.stale["removed"])
        for u, _ in self.pop:
            e = self.trace["units"][u]
            v = e["verdict"]
            if v in ("met", "governance", "not-verifiable"):
                continue
            code_fail = e["source"] == "code" and self.src[u]["verdict"] == "contradicted"
            if v == "contradicted" or v == "force-lost":
                q = next(((s["key"], q) for s in e.get("sections") or [] for q in s.get("quotes") or []), None)
                if code_fail and q is None:
                    ev = code_evidence(e["rules"], self.results)
                    edit = "Make the failing instances pass: " + "; ".join(x for x in ev if "FAIL" in x)
                    sec, cit = "—", ", ".join(e["rules"])
                elif v == "contradicted":
                    edit = (f"Make §{q[0]} state what {u} requires; the passage *\"{q[1]}\"* breaks it."
                            if q else f"Make the spec state what {u} requires.")
                    sec, cit = (f"§{q[0]}" if q else "—"), u
                else:
                    edit = (f"Restate with the criterion's modal: *\"{q[1]}\"*" if q
                            else f"Restate {u} with its modal.")
                    sec, cit = (f"§{q[0]}" if q else "—"), u
                crit = "6" if v == "contradicted" else "5"
                self.row_route[u] = {"bucket": "5.a", "cells": [u, crit, sec, edit, cit],
                                     "prio": 0 if v == "contradicted" else 2}
                continue
            pr = self.prev_route.get(u)
            pv = (self.prev_units.get(u) or {}).get("verdict")
            pkeys = {s.get("key") for s in (self.prev_units.get(u) or {}).get("sections") or []}
            if self.mode == "refine" and pr and pv == v and not (pkeys & changed):
                self.row_route[u] = {"bucket": pr["bucket"], "prev": pr, "prio": 1}
                continue
            self.to_route.append(u)

    def open_items(self):
        """Entries to re-judge / carry, flags, walker FINDINGs."""
        changed = set(self.stale["changed"]) | set(self.stale["removed"])
        old_secs = None
        self.rejudge, self.carried = [], []
        if self.mode == "refine":
            for ent in self.prev_entries:
                if old_secs is None:
                    old_secs = ct.spec_index(rel("output", f"{self.P}-sgai-spec.md"))
                ks = keys_of(ent["refs"], old_secs)
                (self.rejudge if set(ks) & changed else self.carried).append(dict(ent, keys=ks))
        self.flags = {}
        dp = rel("output-analysis", f"{self.N}-detail-review.md")
        self.detail_exists = os.path.isfile(dp)
        if self.detail_exists:
            for heading, header, trows in tables_esc(read(dp)):
                if "flagged" in heading.lower():
                    for r in trows:
                        if r and cp.strip_marks(r[0]):
                            self.flags[cp.strip_marks(r[0])] = dict(zip(header, r))
                    break
        self.walker_findings = []
        for u in self.walk:
            n = (self.trace["units"][u].get("notes") or "")
            if "FINDING:" in n:
                self.walker_findings.append((u, n[n.index("FINDING:"):]))

    def chunks(self):
        if self.mode == "refine":
            keys = [k for k in self.order if k in set(self.stale["changed"]) | set(self.stale["added"])]
        else:
            keys = [k for k in self.order if k not in SKIP_KEYS]
        out, cur, size = [], [], 0
        for k in keys:
            n = len(self.secs[k].text)
            if cur and size + n > OPEN_SPEC_CHARS:
                out.append(cur)
                last = cur[-1]
                ln = len(self.secs[last].text)
                cur, size = ([last], ln) if ln + n <= OPEN_SPEC_CHARS else ([], 0)
            cur.append(k)
            size += n
        if cur:
            out.append(cur)
        return out

    def messages(self):
        """[(message, ids, units, flags)] — one per chunk; items go to the
        first chunk holding one of their sections, else to the first."""
        chunks = self.chunks()
        items = ([("id", e["id"], e.get("keys") or []) for e in self.rejudge]
                 + [("unit", u, [s["key"] for s in self.trace["units"][u].get("sections") or []])
                    for u in self.to_route]
                 + [("flag", f, keys_of(SECREF.findall(" ".join(r.values()))
                                        + re.findall(r"Annex [A-Z](?:\.\d+)*", " ".join(r.values())), self.secs))
                    for f, r in self.flags.items()]
                 + [("finding", u, [s["key"] for s in self.trace["units"][u].get("sections") or []])
                    for u, _ in self.walker_findings])
        if not chunks and items:
            chunks = [[]]
        where = {}
        for it in items:
            i = next((j for j, c in enumerate(chunks) if set(it[2]) & set(c)), 0)
            where.setdefault(i, []).append(it)
        ent = {e["id"]: e for e in self.rejudge}
        fnd = dict(self.walker_findings)
        out = []
        for i, c in enumerate(chunks):
            its = where.get(i, [])
            if not c and not its:
                continue
            parts = [self.blocks["open"], self.blocks["findings"], self.blocks["routing"]]
            ck = set(c)
            uids = [u for u, _ in self.pop
                    if u in {x[1] for x in its if x[0] in ("unit", "finding")}
                    or any(s["key"] in ck for s in self.trace["units"][u].get("sections") or [])]
            ut, omitted = [], 0
            for u in uids:
                t = f"----- UNIT {u} -----\n{ct.unit_text(u, self.req, self.uc) or ''}"
                if sum(map(len, ut)) + len(t) > OPEN_UNITS_CHARS:
                    omitted += 1
                    continue
                ut.append(t)
            parts.append("===== CONTEXT UNITS (context/03 and 04) =====\n" + "\n\n".join(ut)
                         + (f"\n\n({omitted} more units traced to these sections omitted for size)" if omitted else ""))
            parts.append("===== SECTIONS OF THE SPEC =====\n" + "\n".join(
                f"===== SECTION {k} =====\n{self.secs[k].text}" for k in c))
            ids = [x[1] for x in its if x[0] == "id"]
            if ids:
                parts.append("===== ENTRIES TO RE-JUDGE (answer each by its id: the entry again, or a drop) =====\n"
                             + "\n\n".join(f"----- {i2} ({ent[i2]['kind']}) — {ent[i2]['title']} -----\n{ent[i2]['body']}"
                                           for i2 in ids))
            us = [x[1] for x in its if x[0] == "unit"]
            if us:
                rows = []
                for u in us:
                    e = self.trace["units"][u]
                    q = "; ".join(f"§{s['key']}: \"{qq}\"" for s in e.get("sections") or [] for qq in s.get("quotes") or [])
                    rows.append(f"----- UNIT {u}: {e['verdict']} -----\nwalker notes: {e.get('notes') or ''}\n"
                                f"evidence: {q or '(none)'}")
                parts.append("===== COVERAGE ROWS TO ROUTE (one routing object per unit) =====\n" + "\n\n".join(rows))
            fl = [x[1] for x in its if x[0] == "flag"]
            if fl:
                parts.append("===== DETAIL-REVIEW FLAGS TO ROUTE (one routing object per flag) =====\n"
                             + "\n\n".join(f"----- FLAG {f} -----\n" + "\n".join(f"{k}: {v}" for k, v in self.flags[f].items())
                                           for f in fl))
            wf = [x[1] for x in its if x[0] == "finding"]
            if wf:
                parts.append("===== WALKERS' FINDING NOTES (candidates: report those that hold as findings) =====\n"
                             + "\n".join(f"- {u}: {fnd[u]}" for u in wf))
            if self.carried:
                parts.append("===== ALREADY RECORDED, NOT TO REPEAT =====\n"
                             + "\n".join(f"- {e['id']} — {e['title']}" for e in self.carried))
            out.append(("\n\n".join(parts), ids, us, fl))
        return out

    def open_search(self):
        self.found, self.dropped_ids, self.kept, self.unrouted, self.retries = [], {}, [], [], []
        self.answer_rows, self.answer_flags = {}, {}
        msgs = self.messages()
        self.open_sizes = [len(m[0]) + len(OPEN_SYSTEM) for m in msgs]
        if self.plan_only:
            return
        seen = set()
        for i, (msg, ids, units, flags) in enumerate(msgs, 1):
            with open(os.path.join(self.W, f"open-{i}.txt"), "w", encoding="utf-8") as fh:
                fh.write(msg)
            def log(rnd, text, errs, i=i):
                with open(os.path.join(self.W, f"open-{i}.answer-{rnd}.txt"), "w", encoding="utf-8") as fh:
                    fh.write(text)
                for k, v in errs.items():
                    self.retries.append(f"open search call {i}, round {rnd}: {k}: {'; '.join(v)}")
            try:
                good, errs, done = open_call(msg, self.norm, set(ids), set(units), set(flags),
                                             self.model, self.usage_open, log)
            except wb.ModelError as e:
                raise CannotTell(f"the open search could not call the model: {e}")
            if not done:
                self.report.append(f"open search call {i}: no final done line after the retry; it may be incomplete")
            for k, o in good.items():
                if k.startswith("unit:"):
                    self.answer_rows[str(o["unit"])] = o
                elif k.startswith("flag:"):
                    self.answer_flags[str(o["flag"])] = o
                elif o.get("drop"):
                    self.dropped_ids[str(o["id"])] = o.get("reason")
                else:
                    q = next((qq for s in o.get("sections") or [] for qq in s.get("quotes") or []), o.get("title"))
                    sig = (o["kind"], ct.normalise(str(q)))
                    if sig in seen:
                        continue
                    seen.add(sig)
                    self.found.append(o)
            for k, v in errs.items():
                if k.startswith("id:"):
                    self.kept.append(k[3:])
                    self.report.append(f"open search: {k[3:]} kept from {self.P} unchanged ({'; '.join(v)})")
                elif k.startswith("new:"):
                    self.report.append(f"open search: new finding dropped, failed twice ({'; '.join(v)})")
                else:
                    self.unrouted.append(k)
                    self.report.append(f"open search: {k} left unrouted ({'; '.join(v)})")

    # B.6 -------------------------------------------------------------------
    def render(self):
        tr = self.trace["units"]
        # findings, with stable ids
        nxt = {}
        for e in self.prev_entries:
            p, n = e["id"].split("-")
            nxt[p] = max(nxt.get(p, 0), int(n))
        entries = []        # dicts: id, kind, title, body, sections, route(item)
        ent = {e["id"]: e for e in self.prev_entries}
        for e in self.carried:
            entries.append({"id": e["id"], "kind": e["kind"], "title": e["title"], "verbatim": e["body"],
                            "prev": self.prev_route.get(e["id"])})
        for i in self.kept:
            e = ent[i]
            entries.append({"id": i, "kind": e["kind"], "title": e["title"], "verbatim": e["body"],
                            "prev": self.prev_route.get(i)})
        for o in self.found:
            if o.get("id") and o["id"] in ent:
                fid = o["id"]
            else:
                p = KIND_F[o["kind"]][0]
                nxt[p] = nxt.get(p, 0) + 1
                fid = f"{p}-{nxt[p]}"
            entries.append({"id": fid, "kind": o["kind"], "title": o["title"], "text": o["text"],
                            "sections": o.get("sections") or [], "answer": o})
        # routing items: (bucket, ref ids, cells-after-ref, prio, origin)
        items = []
        prev_rows_done = {}

        def from_prev(pr, rid):
            key = pr["row"]
            if key in prev_rows_done:
                prev_rows_done[key]["refs"].append(rid)
                return None
            it = {"bucket": pr["bucket"], "refs": [rid], "prev": pr, "prio": 1}
            prev_rows_done[key] = it
            return it

        def from_answer(o, rid, prio=1):
            b = o["routing"]
            return {"bucket": b, "refs": [rid], "cells": [str(o.get(f)) for f in FIELDS[b]], "prio": prio}
        for e in entries:
            if "answer" in e:
                items.append(from_answer(e["answer"], e["id"]))
            elif e.get("prev"):
                it = from_prev(e["prev"], e["id"])
                if it:
                    items.append(it)
        disp = {}
        for u, r in self.row_route.items():
            if "prev" in r:
                it = from_prev(r["prev"], u)
                if it:
                    items.append(it)
            else:
                items.append({"bucket": "5.a", "refs": [u], "cells": r["cells"][1:], "prio": r["prio"]})
        for u, o in self.answer_rows.items():
            items.append(from_answer(o, u))
        for f, o in self.answer_flags.items():
            items.append(from_answer(o, f"flag {f}"))
        for it in items:
            for r in it["refs"]:
                disp[r] = it["bucket"]
        by = {b: [it for it in items if it["bucket"] == b] for b in BUCKETS}
        by["5.a"].sort(key=lambda it: it["prio"])
        overflow = by["5.a"][TODO_CAP:]
        by["5.a"] = by["5.a"][:TODO_CAP]
        num = {}
        for b in BUCKETS:
            for j, it in enumerate(by[b] + (overflow if b == "5.a" else []), 1):
                it["num"] = f"{NUMBER[b]}{j}"
                for r in it["refs"]:
                    num[r] = it["num"]

        def row(it):
            ref = ", ".join(it["refs"])
            if "prev" in it:
                c = list(it["prev"]["cells"])
                rc = it["prev"]["refcol"]
                if rc is not None and rc < len(c):
                    c[rc] = ref
                c[0] = it["num"]
                return "| " + " | ".join(c) + " |"
            return "| " + " | ".join([it["num"], esc(ref)] + [esc(x) for x in it["cells"]]) + " |"

        L = ["[GROUNDED_BY=spec-only]", "", f"# Spec validation — {self.N} ({datetime.date.today().isoformat()})", ""]
        sha = hashlib.sha256(self.spec_text.encode("utf-8")).hexdigest()
        L += ["Built against:",
              f"- spec: `../{self.spec_rel}` (sha256 `{sha[:12]}…`)",
              f"- context/ at git SHA: {self.git_sha()}",
              f"- mode: {self.mode}" + (f" over {self.P}" if self.mode == "refine" else "")
              + f"; walked {len(self.walk)} units by LLM, {len(self.codeonly)} by code, "
              f"{len(self.carry)} carried over" + (f" from {self.P}" if self.P else ""),
              f"- written by `bin/validate.py`: {len(self.batch_list)} walker batch(es), "
              f"{len(self.open_sizes)} open-search call(s); §A.5's resolution chain read only the "
              "`context/` units and sections each call was given"]
        if self.dropped_ids:
            L.append(f"- entries of {self.P} re-judged and dropped by the open search: "
                     + "; ".join(f"{i} ({esc(r)})" for i, r in sorted(self.dropped_ids.items())))
        L.append("")
        if self.report:
            L += ["**What this run could not settle:**", ""] + [f"- {esc(r)}" for r in self.report] + [""]
        for kind, (prefix, title) in KIND_F.items():
            es = sorted([e for e in entries if e["kind"] == kind], key=lambda e: int(e["id"].split("-")[1]))
            L += [f"## {title} ({len(es)})", ""]
            for e in es:
                L.append(f"### {e['id']} — {esc(e['title'])}")
                if "verbatim" in e:
                    body = "\n".join(ln for ln in e["verbatim"].split("\n")
                                     if not ln.lstrip().startswith("- **Routing:**")).strip()
                    L.append(body)
                else:
                    L.append(safe_body(e["text"]))
                    ev = "; ".join([f"§{s['key']}: *\"{esc(q)}\"*" for s in e["sections"] for q in s.get("quotes") or []]
                                   + [f"§{s['key']}" for s in e["sections"] if not s.get("quotes")])
                    if ev:
                        L.append(f"- **Evidence:** {ev}")
                b = disp.get(e["id"])
                L.append(f"- **Routing:** {b} — {SEE[b]} {num[e['id']]}." if b
                         else "- **Routing:** unrouted (the open search did not route it).")
                L.append("")
        # the map
        cnt = {}
        for u, _ in self.pop:
            cnt[tr[u]["verdict"]] = cnt.get(tr[u]["verdict"], 0) + 1
        tot = ", ".join(f"{cnt.get(k, 0)} {k}" for k in
                        ("met", "contradicted", "partial", "force-lost", "gap", "governance", "not-verifiable"))
        L += ["## Obligation coverage map", "", f"Verdict totals: **{tot}** ({len(self.pop)} units).", "",
              "| Unit | Kind | Verdict | Disposition | Evidence — section and quoted passage | Notes |",
              "|------|------|---------|-------------|---------------------------------------|-------|"]
        for u, _ in self.pop:
            e = tr[u]
            ev = code_evidence(e["rules"], self.results) if e["source"] == "code" else []
            ev = [esc(x) for x in ev] + [f"§{s['key']}: *\"{esc(q)}\"*" for s in e.get("sections") or []
                                         for q in s.get("quotes") or []]
            notes = esc(e.get("notes") or "")
            if e["how"] == "carried":
                notes = f"carried from {self.P}. " + notes
            if e["source"] == "vector-pending":
                notes = "vector-pending. " + notes
            if e["source"] == "code":
                notes = (f"code; the residual {', '.join(e['residual'])} judged by a walker. "
                         if e.get("residual") else "code. ") + notes
            d = disp.get(u, "—") if e["verdict"] not in ("met", "governance") else "—"
            L.append(f"| `{u}` | `{e['judged_kind']}` | `{e['verdict']}` | {d} | {'; '.join(ev) or '—'} | {notes.strip()} |")
        L += ["", "## Disposition of findings", ""]
        if self.detail_exists:
            L.append(f"The flags of `{self.N}-detail-review.md` are routed below by their number (`flag <n>`).")
        else:
            L.append(f"No `{self.N}-detail-review.md` exists when this step runs (Step 7.5 runs after it): "
                     "its flags are not routed here.")
        L.append("")
        titles = {"5.a": "5.a Actionable TODOs", "5.b": "5.b Flagged for review",
                  "5.c": "5.c Deferred to context/", "5.d": "5.d context/ change, predictable"}
        for b in BUCKETS:
            L += [f"### {titles[b]} ({len(by[b])})", ""]
            if by[b]:
                L += [HEADERS[b], "|" + "|".join("-" * 4 for _ in HEADERS[b].split("|")[1:-1]) + "|"]
                L += [row(it) for it in by[b]]
                L.append("")
            if b == "5.a" and overflow:
                L += ["#### 5.a Overflow (next pass)", "", HEADERS[b],
                      "|" + "|".join("-" * 4 for _ in HEADERS[b].split("|")[1:-1]) + "|"]
                L += [row(it) for it in overflow]
                L.append("")
        L += ["### 5.e Routing rules", "",
              "Applied as §5.e of `validate-spec.prompt` states. By rule, with no model: a `contradicted` "
              "row (a walker's or a code FAIL) and a `force-lost` row are 5.a (§5.a criteria 6 and 5); a "
              "row or finding carried from the previous candidate keeps its row; 5.a holds at most "
              f"{TODO_CAP} rows, contradicted first and force-lost last. Every other row, finding and flag "
              "was routed by the open search, and its answer was checked by code.", ""]
        self.sidecar = "\n".join(L)

    def git_sha(self):
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            return "unknown (not a git checkout)"
        d = subprocess.run(["git", "status", "--short", "context/"], cwd=ROOT, capture_output=True, text=True)
        return f"`{p.stdout.strip()}`" + (" (context/ has uncommitted changes)" if d.stdout.strip() else "")

    def write(self):
        side = f"output-analysis/{self.N}-spec-validation.md"
        summ = vs.summarise(self.sidecar, self.pop, side)
        if summ["inconsistent"]:
            raise CannotTell("the rendered sidecar's counts disagree: " + "; ".join(summ["inconsistent"]))
        trace_rel = f"output-analysis/{self.N}-trace.json"
        tmp_s, tmp_t = os.path.join(self.W, "sidecar.md"), os.path.join(self.W, "trace.json")
        with open(tmp_s, "w", encoding="utf-8") as fh:
            fh.write(self.sidecar)
        shutil.copyfile(tmp_s, rel(side))
        shutil.copyfile(tmp_t, rel(trace_rel))
        summ_rel = f"output-analysis/{self.N}-spec-validation.summary.json"
        rc, out, err = run([os.path.join(BIN, "validation-summary.py"), side, "--out", summ_rel,
                            "--population", os.path.join(self.W, "population.tsv")])
        if rc != 0:
            for p in (side, trace_rel, summ_rel):
                if os.path.isfile(rel(p)):
                    os.remove(rel(p))
            raise CannotTell(f"validation-summary exit {rc}: {(out + err)[-300:]}")
        self.summary_out = out.strip()

    # ---------------------------------------------------------------------
    def execute(self):
        self.inputs()
        self.plan()
        self.draft()
        self.batches()
        self.write_walk()
        if self.plan_only:
            self.trace = {"units": {u: dict(e, verdict="?", notes="") for u, e in self.draft_trace["units"].items()}}
            self.routing_by_rule = lambda: None
            self.to_route = []
            self.open_items()
            self.open_search()
            sizes = [len(t) for _, t in self.batch_list]
            print(f"mode {self.mode}" + (f" over {self.P}" if self.P else "")
                  + f": population {len(self.pop)}; walk {len(self.walk)}, code {len(self.codeonly)}, "
                  f"carry {len(self.carry)}")
            if self.mode == "refine":
                print(f"stale: changed {len(self.stale['changed'])}, removed {len(self.stale['removed'])}, "
                      f"added {len(self.stale['added'])}, units {len(self.stale['units'])}")
            print(f"batches {len(sizes)}: chars per batch min {min(sizes, default=0)} max {max(sizes, default=0)} "
                  f"total {sum(sizes)}; defs.txt {self.defs_chars} chars sent with every batch")
            print(f"open search: {len(self.open_sizes)} call(s), chars {self.open_sizes} "
                  f"(≈{[int(s / CHARS_PER_TOKEN) for s in self.open_sizes]} tokens at {CHARS_PER_TOKEN} chars/token); "
                  f"re-judge {len(self.rejudge)}, carried entries {len(self.carried)}, flags {len(self.flags)} "
                  "(rows to route and walker FINDINGs are known only after the walk)")
            return 0
        self.walkers()
        self.assemble()
        self.check_trace()
        self.routing_by_rule()
        self.open_items()
        self.open_search()
        nv = [u for u, e in self.trace["units"].items() if e["verdict"] == "not-verifiable"]
        for u in nv:
            if not any(r.startswith(u + ":") for r in self.report):
                self.report.append(f"{u}: not-verifiable ({self.trace['units'][u].get('notes', '')[:200]})")
        self.render()
        self.write()
        tot_in = sum(sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_creation_input_tokens",
                                                       "cache_read_input_tokens")) for u in self.usage_open)
        print(self.walk_out.strip())
        print(f"open search: {len(self.usage_open)} call(s), input {tot_in}; message sizes (chars) {self.open_sizes}")
        for r in self.retries:
            print("RETRIED: " + r)
        for i, r in sorted(self.dropped_ids.items()):
            print(f"DROPPED: {i} ({r})")
        print(f"check-trace: {json.dumps(self.check_out.get('by_verdict'), sort_keys=True)}")
        print(self.summary_out)
        for r in self.report:
            print("REPORT: " + r)
        print(f"wrote output-analysis/{self.N}-spec-validation.md, {self.N}-trace.json, "
              f"{self.N}-spec-validation.summary.json. A green says the walk covered the population as the mode "
              "requires and every quotation is literal; not that a verdict or a routing is right.")
        degraded = nv or self.kept or self.unrouted or any(r.startswith("open search") for r in self.report)
        return 1 if degraded else 0


def parse_args(argv):
    if not argv or argv[0] in ("-h", "--help"):
        raise Usage("")
    o = {"--prev": None, "--mode": None, "--jobs": "4", "--model": None}
    flags = {"--force": False, "--keep": False, "--plan-only": False}
    pos, i = [], 0
    while i < len(argv):
        a = argv[i]
        if a in o:
            if i + 1 >= len(argv):
                raise Usage(f"{a} needs a value")
            o[a] = argv[i + 1]
            i += 2
            continue
        if a in flags:
            flags[a] = True
        elif a.startswith("-"):
            raise Usage(f"unknown argument {a}")
        else:
            pos.append(a)
        i += 1
    if len(pos) != 1 or not re.fullmatch(r"v\d+(\.\d+)*", pos[0]):
        raise Usage("one candidate, v<N>, is needed")
    if o["--prev"] and not re.fullmatch(r"v\d+(\.\d+)*", o["--prev"]):
        raise Usage("--prev is v<P>")
    if o["--mode"] not in (None, "refine", "incremental", "major"):
        raise Usage("--mode is refine, incremental or major")
    if not o["--jobs"].isdigit() or int(o["--jobs"]) < 1:
        raise Usage("--jobs is a positive integer")
    return pos[0], o, flags


def main(argv):
    try:
        N, o, flags = parse_args(argv)
    except Usage as e:
        if not str(e):
            sys.stdout.write(__doc__)
            return 0 if argv else 64
        sys.stderr.write(f"validate: {e}\n\n{__doc__}")
        return 64
    mode = o["--mode"]
    if mode is None:
        mode = ("refine" if os.path.isfile(rel("output-analysis", f"{N}-patch.json"))
                else "incremental" if os.path.isfile(rel("output-analysis", f"{N}-context-delta.md")) else "major")
    prev = o["--prev"]
    if prev is None:
        below = [m.group(1) for f in (os.listdir(rel("output")) if os.path.isdir(rel("output")) else [])
                 for m in [re.match(r"^(v[\d.]+)-sgai-spec\.md$", f)] if m and vkey(m.group(1)) < vkey(N)]
        prev = max(below, key=vkey) if below else None
    outs = [rel("output-analysis", f"{N}-{x}") for x in
            ("spec-validation.md", "trace.json", "spec-validation.summary.json")]
    if not flags["--force"] and not flags["--plan-only"] and all(os.path.isfile(p) for p in outs):
        newest_in = max(os.path.getmtime(p) for p in (rel("output", f"{N}-sgai-spec.md"),
                                                       rel("output-analysis", f"{N}-conformance-tests.json"))
                        if os.path.isfile(p))
        if os.path.getmtime(outs[0]) > newest_in:
            print(f"[SKIPPED] validate-spec → output-analysis/{N}-spec-validation.md (newer than its inputs)")
            return 0
    base = os.path.join(os.environ.get("XDG_RUNTIME_DIR") or tempfile.gettempdir(), "cto")
    os.makedirs(base, mode=0o700, exist_ok=True)
    W = tempfile.mkdtemp(prefix=f"validate-{N}-", dir=base)
    step = Step(N, prev, mode, int(o["--jobs"]), o["--model"], flags["--keep"], flags["--plan-only"])
    step.W = W
    try:
        return step.execute()
    except CannotTell as e:
        print(f"CANNOT TELL (nothing written): {e}")
        for r in step.report:
            print("REPORT: " + r)
        return 2
    finally:
        if flags["--keep"]:
            print(f"work directory kept: {W}")
        else:
            shutil.rmtree(W, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
