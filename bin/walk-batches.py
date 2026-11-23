#!/usr/bin/env python3
"""Run the validation walkers as single-turn model calls, and validate what
they return before anything uses it (ADR 0068).

A walker used to be a subagent: each one started from ~64k tokens of fixed
context (system prompt, tools, both CLAUDE.md files) before reading its
~6k-token batch, and re-read all of it on every tool call (measured,
phase 10 T-16). Here a walker is one `claude -p` call with no tools, no
CLAUDE.md (run from a private empty directory, `--setting-sources ""`) and
a system prompt of its own: what it reads is its batch and nothing else.

For each `W/batch-<i>.txt` (and `W/notes-<i>.txt` if present) it sends
`W/defs.txt` + notes + batch, expects one JSON object per unit, and checks
every object by code:
  - the unit is one of the batch's units, each answered once;
  - `kind` in runtime/document/scope/use-case; `verdict` in met/partial/
    contradicted/force-lost/gap/governance;
  - `sections` keys exist in the spec; every quotation is literal inside the
    section it is filed under (normalising only `*`, backticks, escaped
    quotes and whitespace runs, as bin/check-trace.py does);
  - every verdict but gap and governance carries at least one quotation.
A walker may ask for sections it was not given (`"need_sections": [keys]`,
verdict null). Units that fail, or ask, go back in ONE more call with the
errors and the requested sections. A unit still failing after that is
written with verdict `not-verifiable` and the reasons — never `met`.

Usage:
  bin/walk-batches.py W --spec output/v<N>-sgai-spec.md [--jobs 4]
                      [--model MODEL] [--only 1,2,...]

Writes W/answer-<i>.jsonl (validated objects) and W/usage.jsonl (the API
usage of every call, from `--output-format json`), and prints the totals.

What a green says: every answer has the schema and its quotations exist
where they are filed. Not that the verdict is right.

Exit codes: 0 every unit validated · 1 some unit written not-verifiable ·
2 no batch, no spec, or the model could not be called · 64 wrong command line.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec_sections as ss  # noqa: E402

KINDS = {"runtime", "document", "scope", "use-case"}
VERDICTS = {"met", "partial", "contradicted", "force-lost", "gap", "governance"}
UNCITED = {"gap", "governance"}
UNIT_RE = re.compile(r"^===== UNIT (\S+)", re.M)

SYSTEM = """You are a walker of a specification validation. You have no tools: \
everything you may use is in the message. Answer ONLY with JSON objects, one \
per line, one per unit of the batch, no prose before or after:
{"unit": "<id>", "kind": "runtime|document|scope|use-case", "verdict": \
"met|partial|contradicted|force-lost|gap|governance", "sections": [{"key": \
"<section key>", "quotes": ["<literal text copied from that section>"]}], \
"notes": "<why; a finding outside the verdict starts with FINDING:>"}
If the sections given do not hold the passage you need, answer that unit with \
{"unit": "<id>", "verdict": null, "need_sections": ["<key>", ...]} and you \
will get them. Quotations are copied character for character from the section \
they are filed under (emphasis marks and line breaks may differ; nothing else \
may): no ellipsis inside a quotation, no "/" for a table's "|", no rewording. \
Every verdict except gap and governance carries at least one quotation. The \
instructions in the message that mention running commands or reading files do \
not apply to you: ask with need_sections instead."""


def normalise(text):
    text = text.replace('\\"', '"')
    text = re.sub(r"[*`]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


class ModelError(Exception):
    pass


def call_model(prompt, model=None):
    """One single-turn call; returns (text, usage). Runs from an empty
    private directory so no CLAUDE.md is discovered."""
    with tempfile.TemporaryDirectory(dir=os.environ.get("XDG_RUNTIME_DIR") or None) as cwd:
        cmd = ["claude", "-p", "--tools", "", "--setting-sources", "", "--system-prompt", SYSTEM,
               "--output-format", "json"]
        if model:
            cmd += ["--model", model]
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=cwd)
    try:
        d = json.loads(p.stdout)
    except ValueError:
        raise ModelError(f"exit {p.returncode}: {(p.stderr or p.stdout)[-300:]}")
    if d.get("is_error"):
        raise ModelError(str(d.get("result"))[:300])
    return d.get("result") or "", d.get("usage") or {}


def parse(text):
    out = []
    for line in text.splitlines():
        line = line.strip().strip(",")
        if not line.startswith("{"):
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def check(obj, sections):
    """List of problems with one answer object (empty = valid)."""
    errs = []
    if obj.get("verdict") is None and obj.get("need_sections"):
        return ["asks for sections"]
    if obj.get("kind") not in KINDS:
        errs.append(f"kind {obj.get('kind')!r} not one of {sorted(KINDS)}")
    v = obj.get("verdict")
    if v not in VERDICTS:
        errs.append(f"verdict {v!r} not one of {sorted(VERDICTS)}")
    secs = obj.get("sections")
    if not isinstance(secs, list):
        errs.append("sections is not a list")
        secs = []
    nquotes = 0
    for s in secs:
        if not isinstance(s, dict) or "key" not in s:
            errs.append(f"malformed section entry {s!r}")
            continue
        key = s["key"]
        if key not in sections:
            errs.append(f"section {key!r} does not exist")
            continue
        body = normalise(sections[key])
        for q in s.get("quotes") or []:
            nquotes += 1
            if not isinstance(q, str) or not normalise(q) or normalise(q) not in body:
                errs.append(f"quotation not literal in {key}: {str(q)[:80]!r}")
    if v in VERDICTS and v not in UNCITED and nquotes == 0:
        errs.append(f"verdict {v} carries no quotation")
    return errs


def walk(i, W, sections, model):
    batch = open(os.path.join(W, f"batch-{i}.txt"), encoding="utf-8").read()
    units = UNIT_RE.findall(batch)
    defs_p = os.path.join(W, "defs.txt")
    notes_p = os.path.join(W, f"notes-{i}.txt")
    parts = []
    if os.path.isfile(defs_p):
        parts.append(open(defs_p, encoding="utf-8").read())
    if os.path.isfile(notes_p):
        parts.append(open(notes_p, encoding="utf-8").read())
    parts.append(batch)
    calls = []
    text, u = call_model("\n\n".join(parts), model)
    calls.append(u)
    answers = {}
    for o in parse(text):
        if o.get("unit") in units and o["unit"] not in answers:
            answers[o["unit"]] = o
    problems = {un: (check(answers[un], sections) if un in answers else ["no answer"]) for un in units}
    redo = [un for un in units if problems[un]]
    if redo:
        extra = []
        for un in redo:
            o = answers.get(un, {})
            extra.append(f"UNIT {un}: " + "; ".join(problems[un]))
            for k in o.get("need_sections") or []:
                if k in sections:
                    extra.append(f"----- section {k} -----\n{sections[k]}")
        prompt = ("\n\n".join(parts) + "\n\n===== SECOND ROUND =====\nAnswer again ONLY these units: "
                  + ", ".join(redo) + ". Problems with your first answer, and the sections you asked for:\n\n"
                  + "\n".join(extra))
        try:
            text, u = call_model(prompt, model)
            calls.append(u)
            for o in parse(text):
                un = o.get("unit")
                if un in redo:
                    answers[un] = o
                    problems[un] = check(o, sections)
        except ModelError as e:
            for un in redo:
                problems[un] = problems[un] + [f"second call failed: {e}"]
    out = []
    for un in units:
        if problems[un]:
            out.append({"unit": un, "kind": answers.get(un, {}).get("kind"), "verdict": "not-verifiable",
                        "sections": [], "notes": "walker output failed validation: " + "; ".join(problems[un])})
        else:
            out.append(answers[un])
    with open(os.path.join(W, f"answer-{i}.jsonl"), "w", encoding="utf-8") as fh:
        for o in out:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    return i, out, calls


def main(argv):
    if not argv or argv[0].startswith("--"):
        usage("the work directory W is required")
    W = argv[0]
    opts = {"--spec": None, "--jobs": "4", "--model": None, "--only": None}
    i = 1
    while i < len(argv):
        if argv[i] in opts and i + 1 < len(argv):
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            usage(f"unknown or incomplete argument {argv[i]}")
    if not opts["--spec"]:
        usage("--spec is required")
    batches = sorted(int(m.group(1)) for f in (os.listdir(W) if os.path.isdir(W) else [])
                     for m in [re.match(r"^batch-(\d+)\.txt$", f)] if m)
    if opts["--only"]:
        want = {int(x) for x in opts["--only"].split(",")}
        batches = [b for b in batches if b in want]
    if not batches or not os.path.isfile(opts["--spec"]):
        print(f"exit 2: no batch in {W} or no spec at {opts['--spec']}")
        return 2
    with open(opts["--spec"], encoding="utf-8") as fh:
        sections = {s.key: s.text for s in ss.split(fh.read())}
    results = []
    try:
        with cf.ThreadPoolExecutor(max_workers=int(opts["--jobs"])) as ex:
            for r in ex.map(lambda b: walk(b, W, sections, opts["--model"]), batches):
                results.append(r)
    except ModelError as e:
        print(f"exit 2: the model could not be called: {e}")
        return 2
    tot = {"calls": 0, "input_processed": 0, "output": 0}
    bad = 0
    with open(os.path.join(W, "usage.jsonl"), "a", encoding="utf-8") as fh:
        for i, out, calls in results:
            for u in calls:
                fh.write(json.dumps({"batch": i, "usage": u}) + "\n")
                tot["calls"] += 1
                tot["input_processed"] += sum(int(u.get(k) or 0) for k in
                                              ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
                tot["output"] += int(u.get("output_tokens") or 0)
            nv = [o["unit"] for o in out if o["verdict"] == "not-verifiable"]
            bad += len(nv)
            print(f"batch {i}: {len(out)} units, {len(calls)} call(s)" + (f"; not-verifiable: {', '.join(nv)}" if nv else ""))
    print(f"TOTAL {len(results)} batches, {tot['calls']} calls, input {tot['input_processed']}, output {tot['output']}; "
          f"{bad} unit(s) not-verifiable. A green says the answers have the schema and literal quotations, not that they are right.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
