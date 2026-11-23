#!/usr/bin/env python3
"""validate.py: the validation step as code. A fixture project (the bin
scripts the step uses, a small context/, two candidates and their
conformance tests) is built in a private temporary directory, and the model
is replaced by a stub that answers from a script: no call leaves the machine.
Run: python3 bin/test_validate.py
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
SCRIPTS = ["validate.py", "walk-batches.py", "check-trace.py", "check-promotable.py",
           "validation-summary.py", "spec_sections.py", "compare-candidates.py"]

REQ = """# Requirements

- **R1.** Windows. The Player MUST honour the window.
  - **R1.1** The Player MUST present the window only inside its span.
  - **R1.2** The Player MUST NOT show two forms at once.
  - **R1.3** The Publisher MUST declare `@cap` on the window.
- **R2.** Tracking.
  - **R2.1** The Player MUST fire `start` beacons.
- **R3.** Extras.
  - **R3.1** The Player MUST log `alpha`.
  - **R3.2** The Player MUST log `beta`.
  - **R3.3** The Player MUST log `gamma`.
  - **R3.4** The Player MUST log `delta`.
  - **R3.5** The Player MUST log `epsilon`.
"""
UCS = """# Use cases

## UC-01 A window

The Player renders the window on D1.
"""
SPEC1 = """# SGAI fixture

## 1 Scope

The Player MUST honour the window. The Player MUST present the window only inside its span.

## 2 Forms

The Player MUST NOT show two forms at once.

## 3 Cap

The Publisher declares `@cap` on the window.

## 4 Tracking

The Player fires `start` beacons.

## 5 Logs

The Player MUST log `alpha`. The Player MUST log `beta`. The Player MUST log `gamma`. The Player MUST log `delta`. The Player MUST log `epsilon`.

## 6 Use cases

UC-01 walks the window: D1 renders it.
"""
SPEC2 = SPEC1.replace("The Player fires `start` beacons.", "The Player MUST fire `start` beacons.")
PLAYER = "Player behaviour: level 3 (reference-player)"
CONF = {"spec": "x", "exit": 1, "counts": {}, "cannot": [],
        "rules": {"R1.3a": {"level": 2, "criterion": "R1.3", "not_verifiable": ""},
                  "R1.2a": {"level": 2, "criterion": "R1.2", "not_verifiable": ""},
                  "R1.2b": {"level": 2, "criterion": "R1.2", "not_verifiable": "a property of the prose"},
                  "R2.1a": {"level": 2, "criterion": "R2.1", "not_verifiable": PLAYER}},
        "results": [{"rule": "R1.3a", "outcome": "FAIL", "subject": "ex/a.mpd", "xpath": "/MPD", "detail": "no @cap"},
                    {"rule": "R1.2a", "outcome": "PASS", "subject": "ex/a.mpd", "xpath": "/MPD", "detail": ""}]}
DETAIL = "# Detail review\n\n## Flagged issues\n\n| # | Category | Spec ref | Description |\n|---|---|---|---|\n"
QUOTE = {"R1#p1": ("1", "The Player MUST honour the window."),
         "R1.1": ("1", "The Player MUST present the window only inside its span."),
         "R1.2": ("2", "The Player MUST NOT show two forms at once."),
         "R2.1": ("4", "beacons."),
         "UC-01": ("6", "UC-01 walks the window: D1 renders it.")}
for i, w in enumerate(["alpha", "beta", "gamma", "delta", "epsilon"], 1):
    QUOTE[f"R3.{i}"] = ("5", f"The Player MUST log `{w}`.")


def met(u, verdict="met"):
    k, q = QUOTE[u]
    return {"unit": u, "kind": "use-case" if u.startswith("UC") else "runtime", "verdict": verdict,
            "sections": [{"key": k, "quotes": [q]}], "notes": f"stub {verdict}"}


AMB = {"kind": "ambiguity", "title": "Two forms or two windows", "text": "- **Context passage:** R1.2.\n- **Readings:** two.",
       "sections": [{"key": "2", "quotes": ["show two forms at once"]}], "routing": "5.b", "section": "2",
       "why_uncertain": "two readings", "resolutions": "(a) forms (b) windows", "recommended": "(a)",
       "searched": "context/ units given; ADRs and the base standard not available"}
GAP = {"kind": "gap", "title": "Beacon timing", "text": "- **What the context is missing:** when.",
       "sections": [{"key": "4", "quotes": []}], "routing": "5.c", "context_file": "03-requirements.md R2.1",
       "suggested_edit": "say when", "leverage": "tracking", "searched": "context/ units given"}
DONE = '{"done": true}'


def lines(*objs):
    return "\n".join(o if isinstance(o, str) else json.dumps(o) for o in objs)


class Model:
    """The stub: walker calls answer per unit from `walker` (a dict of unit ->
    answer or list of answers per round); open-search calls pop `opens`."""

    def __init__(self, walker=None, opens=()):
        self.walker = walker or {}
        self.opens = list(opens)
        self.walked, self.open_prompts = [], []

    def __call__(self, prompt, model=None, system=None):
        if system is None:
            m = re.search(r"Answer again ONLY these units: (.+?)\. Problems", prompt)
            units = m.group(1).split(", ") if m else re.findall(r"^===== UNIT (\S+)", prompt, re.M)
            rnd = 1 if m else 0
            self.walked += units
            out = []
            for u in units:
                a = self.walker.get(u, met(u))
                out.append(a[min(rnd, len(a) - 1)] if isinstance(a, list) else a)
            return lines(*out), {"input_tokens": len(prompt) // 4, "output_tokens": 10}
        self.open_prompts.append(prompt)
        if not self.opens:
            return DONE, {"input_tokens": len(prompt) // 4, "output_tokens": 1}
        return self.opens.pop(0), {"input_tokens": len(prompt) // 4, "output_tokens": 10}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get("XDG_RUNTIME_DIR") or None)
        self.R = R = self.tmp.name
        for d in ("bin", "context", "output", "output-analysis", "dist", "prompts/3-post-spec"):
            os.makedirs(os.path.join(R, d))
        for f in SCRIPTS:
            shutil.copy(os.path.join(BIN, f), os.path.join(R, "bin", f))
        shutil.copy(os.path.join(ROOT, "prompts/3-post-spec/validate-spec.prompt"),
                    os.path.join(R, "prompts/3-post-spec/validate-spec.prompt"))
        self.put("context/03-requirements.md", REQ)
        self.put("context/04-use-cases.md", UCS)
        self.put("output/v1-sgai-spec.md", SPEC1)
        self.put("output-analysis/v1-conformance-tests.json", json.dumps(CONF))
        self.put("output-analysis/v1-detail-review.md", DETAIL)
        spec = importlib.util.spec_from_file_location("validate_fx", os.path.join(R, "bin", "validate.py"))
        self.v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.v)
        self.real = self.v.wb.call_model

    def tearDown(self):
        self.v.wb.call_model = self.real
        self.tmp.cleanup()

    def put(self, rel, text):
        with open(os.path.join(self.R, rel), "w", encoding="utf-8") as fh:
            fh.write(text)

    def get(self, rel):
        with open(os.path.join(self.R, rel), encoding="utf-8") as fh:
            return fh.read()

    def exists(self, rel):
        return os.path.isfile(os.path.join(self.R, rel))

    def run_v(self, model, *args):
        self.v.wb.call_model = model
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = self.v.main(list(args))
        self.out = buf.getvalue()
        return rc

    def tool(self, *args):
        p = subprocess.run([sys.executable] + list(args), cwd=self.R, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def major_v1(self, opens=(lines(AMB, GAP, DONE),)):
        rc = self.run_v(Model(opens=list(opens)), "v1", "--mode", "major")
        self.assertEqual(rc, 0, self.out)

    def refine_v11(self, model, *extra):
        self.major_v1()
        self.put("output/v1.1-sgai-spec.md", SPEC2)
        self.put("output-analysis/v1.1-conformance-tests.json", json.dumps(CONF))
        self.put("output-analysis/v1.1-detail-review.md", DETAIL)
        self.put("output-analysis/v1.1-patch.json", json.dumps({"sections_changed": ["4"]}))
        return self.run_v(model, "v1.1", "--prev", "v1", "--mode", "refine", *extra)

    def trace(self, v):
        return json.loads(self.get(f"output-analysis/{v}-trace.json"))["units"]


class Major(Fixture):
    def test_writes_three_files_that_the_readers_parse(self):
        self.major_v1()
        for f in ("spec-validation.md", "trace.json", "spec-validation.summary.json"):
            self.assertTrue(self.exists(f"output-analysis/v1-{f}"))
        rc, out = self.tool("bin/check-trace.py", "output-analysis/v1-trace.json",
                            "--rules", "output-analysis/v1-conformance-tests.json")
        self.assertEqual(rc, 0, out)
        rc, out = self.tool("bin/check-promotable.py")
        # R1.3 is a code FAIL: blocked, routed to the pipeline, not "cannot tell"
        self.assertEqual(rc, 1, out)
        self.assertIn("PIPELINE=2", out)
        self.assertIn("UNCERTAIN=0", out)
        side = self.get("output-analysis/v1-spec-validation.md")
        self.assertIn("## Gaps (1)", side)
        self.assertIn("## Ambiguities (1)", side)
        self.assertIn("### 5.a Actionable TODOs (1)", side)
        self.assertRegex(side, r"\| `R1\.3` \| `runtime` \| `contradicted` \| 5\.a \| R1\.3a: FAIL at ex/a\.mpd#/MPD")
        self.assertIn("vector-pending.", side)
        self.assertIn("- **Routing:** 5.b — See Flagged F-1.", side)

    def test_code_unit_without_residual_is_not_walked(self):
        m = Model(opens=[DONE])
        self.assertEqual(self.run_v(m, "v1", "--mode", "major"), 0, self.out)
        self.assertNotIn("R1.3", m.walked)
        self.assertIn("R1.2", m.walked)         # code with residual: walked
        self.assertEqual(sorted(m.walked), sorted(u for u in QUOTE))
        self.assertEqual(self.trace("v1")["R1.3"]["verdict"], "contradicted")

    def test_residual_combines_with_the_worse(self):
        m = Model(walker={"R1.2": met("R1.2", "partial")}, opens=[lines({"unit": "R1.2", **{k: AMB[k] for k in AMB if k not in ("kind", "title", "text", "sections")}}, DONE)])
        self.assertEqual(self.run_v(m, "v1", "--mode", "major"), 0, self.out)
        e = self.trace("v1")["R1.2"]
        self.assertEqual((e["verdict"], e["walker_verdict"]), ("partial", "partial"))

    def test_combine_rule(self):
        c = self.v.combine
        self.assertEqual(c("met", "partial"), "partial")
        self.assertEqual(c("contradicted", "met"), "contradicted")
        self.assertEqual(c("met", "force-lost"), "force-lost")
        self.assertEqual(c("met", "gap"), "partial")
        self.assertEqual(c("contradicted", "gap"), "contradicted")
        self.assertEqual(c("met", "governance"), "met")
        self.assertEqual(c("met", "not-verifiable"), "not-verifiable")

    def test_walker_not_verifiable_is_rendered_and_cannot_tell(self):
        bad = dict(met("R1.1"), sections=[{"key": "1", "quotes": ["The Player MAY present"]}])
        m = Model(walker={"R1.1": [bad, bad]}, opens=[DONE])
        rc = self.run_v(m, "v1", "--mode", "major")
        self.assertEqual(rc, 1, self.out)
        self.assertIn("REPORT: R1.1: not-verifiable", self.out)
        side = self.get("output-analysis/v1-spec-validation.md")
        self.assertIn("| `R1.1` | `runtime` | `not-verifiable` | — |", side)
        self.assertIn("**What this run could not settle:**", side)
        rc, out = self.tool("bin/check-promotable.py")
        self.assertEqual(rc, 2, out)
        self.assertIn("veredicto que no conozco en R1.1: not-verifiable", out)

    def test_contradicted_and_force_lost_route_by_rule_and_the_cap(self):
        w = {f"R3.{i}": met(f"R3.{i}", "contradicted") for i in range(1, 6)}
        w["R1.1"] = met("R1.1", "force-lost")
        m = Model(walker=w, opens=[DONE])
        self.assertEqual(self.run_v(m, "v1", "--mode", "major"), 0, self.out)
        side = self.get("output-analysis/v1-spec-validation.md")
        self.assertIn("### 5.a Actionable TODOs (5)", side)
        self.assertIn("#### 5.a Overflow (next pass)", side)
        a = side.split("### 5.a Actionable TODOs")[1].split("#### 5.a Overflow")[0]
        over = side.split("#### 5.a Overflow (next pass)")[1].split("### 5.b")[0]
        self.assertNotIn("R1.1", a)              # force-lost never takes a slot ahead of contradicted
        self.assertIn("R1.1", over)
        self.assertNotIn("SECOND ROUND", "".join(m.open_prompts))
        self.assertNotIn("UNIT R3.1", "".join(m.open_prompts).split("COVERAGE ROWS")[-1] if "COVERAGE ROWS" in "".join(m.open_prompts) else "")
        rc, out = self.tool("bin/validation-summary.py", "output-analysis/v1-spec-validation.md")
        self.assertEqual(rc, 0, out)
        summ = json.loads(self.get("output-analysis/v1-spec-validation.summary.json"))
        self.assertEqual(summ["units"]["R1.1"]["disposition"], "5.a")
        self.assertEqual(summ["findings"]["5.a"], 7)   # 5 + overflow 1 + R1.3 → R1.3 contradicted too
        rc, out = self.tool("bin/check-promotable.py")
        self.assertEqual(rc, 1, out)

    def test_gap_row_routed_by_open_search_or_left_unrouted(self):
        w = {"R1.1": met("R1.1", "gap") | {"sections": []}}
        route = {"unit": "R1.1", "routing": "5.c", "context_file": "03", "suggested_edit": "x",
                 "leverage": "y", "searched": "z"}
        m = Model(walker=w, opens=[lines(route, DONE)])
        self.assertEqual(self.run_v(m, "v1", "--mode", "major"), 0, self.out)
        self.assertIn("COVERAGE ROWS TO ROUTE", m.open_prompts[0])
        self.assertIn("| `R1.1` | `runtime` | `gap` | 5.c |", self.get("output-analysis/v1-spec-validation.md"))
        m = Model(walker=w, opens=[DONE, DONE])
        self.assertEqual(self.run_v(m, "v1", "--mode", "major", "--force"), 1, self.out)
        self.assertIn("unit:R1.1 left unrouted", self.out)
        rc, out = self.tool("bin/check-promotable.py")
        self.assertEqual(rc, 2, out)
        self.assertIn("sin rutear", out)

    def test_open_search_non_literal_quote_is_retried_then_dropped(self):
        bad = dict(AMB, sections=[{"key": "2", "quotes": ["show two windows at once"]}])
        m = Model(opens=[lines(bad, DONE), lines(bad, DONE)])
        rc = self.run_v(m, "v1", "--mode", "major")
        self.assertEqual(rc, 1, self.out)
        self.assertEqual(len(m.open_prompts), 2)
        self.assertIn("quotation not literal in 2", m.open_prompts[1])
        self.assertIn("new finding dropped", self.out)
        self.assertIn("## Ambiguities (0)", self.get("output-analysis/v1-spec-validation.md"))

    def test_open_search_fixed_in_second_round(self):
        bad = dict(AMB, sections=[{"key": "2", "quotes": ["show two windows at once"]}])
        m = Model(opens=[lines(bad, DONE), lines(AMB, DONE)])
        self.assertEqual(self.run_v(m, "v1", "--mode", "major"), 0, self.out)
        self.assertIn("## Ambiguities (1)", self.get("output-analysis/v1-spec-validation.md"))

    def test_major_chunks_and_a_finding_repeated_across_chunks_counts_once(self):
        self.v.OPEN_SPEC_CHARS = 150
        m = Model(opens=[lines(AMB, DONE)] * 10)
        self.assertEqual(self.run_v(m, "v1", "--mode", "major"), 0, self.out)
        self.assertGreater(len(m.open_prompts), 2)
        self.assertIn("## Ambiguities (1)", self.get("output-analysis/v1-spec-validation.md"))

    def test_flags_are_routed_when_the_detail_review_exists(self):
        self.put("output-analysis/v1-detail-review.md", DETAIL + "| 1 | editorial | §2 | heading |\n")
        fl = {"flag": "1", "routing": "5.a", "criterion": "4", "section": "2", "edit": "e", "citation": "c"}
        m = Model(opens=[lines(fl, DONE)])
        self.assertEqual(self.run_v(m, "v1", "--mode", "major"), 0, self.out)
        self.assertIn("DETAIL-REVIEW FLAGS TO ROUTE", m.open_prompts[0])
        self.assertIn("| flag 1 |", self.get("output-analysis/v1-spec-validation.md"))
        os.remove(os.path.join(self.R, "output-analysis/v1-detail-review.md"))
        self.assertEqual(self.run_v(Model(opens=[DONE]), "v1", "--mode", "major", "--force"), 0, self.out)
        self.assertIn("No `v1-detail-review.md` exists", self.get("output-analysis/v1-spec-validation.md"))

    def test_missing_conformance_tests_writes_nothing(self):
        os.remove(os.path.join(self.R, "output-analysis/v1-conformance-tests.json"))
        self.assertEqual(self.run_v(Model(), "v1", "--mode", "major"), 2)
        self.assertIn("CANNOT TELL", self.out)
        self.assertIn("Step 8.0 runs before this step", self.out)
        self.assertFalse(self.exists("output-analysis/v1-spec-validation.md"))
        self.assertFalse(self.exists("output-analysis/v1-trace.json"))

    def test_model_unreachable_writes_nothing(self):
        def boom(prompt, model=None, system=None):
            raise self.v.wb.ModelError("no model")
        self.assertEqual(self.run_v(boom, "v1", "--mode", "major"), 2, self.out)
        self.assertFalse(self.exists("output-analysis/v1-spec-validation.md"))
        walk_ok = Model()

        def open_down(prompt, model=None, system=None):
            if system is None:
                return walk_ok(prompt, model, system)
            raise self.v.wb.ModelError("no model")
        self.assertEqual(self.run_v(open_down, "v1", "--mode", "major"), 2, self.out)
        self.assertIn("the open search could not call the model", self.out)
        for f in ("spec-validation.md", "trace.json", "spec-validation.summary.json"):
            self.assertFalse(self.exists(f"output-analysis/v1-{f}"))

    def test_prompt_anchor_gone_cannot_tell(self):
        p = "prompts/3-post-spec/validate-spec.prompt"
        self.put(p, self.get(p).replace("#### Walker rules", "#### Rules for walkers"))
        self.assertEqual(self.run_v(Model(), "v1", "--mode", "major"), 2, self.out)
        self.assertIn("the walker rules", self.out)

    def test_defs_carry_the_prompts_text(self):
        m = Model(opens=[DONE])
        self.run_v(m, "v1", "--mode", "major", "--keep")
        W = re.search(r"work directory kept: (\S+)", self.out).group(1)
        defs = open(os.path.join(W, "defs.txt")).read()
        shutil.rmtree(W)
        self.assertIn("`force-lost` — the spec carries the substance", defs)
        self.assertIn("#### Walker rules", defs)
        self.assertIn("5\tSGAI fixture" if False else "5\t5 Logs", defs)
        self.assertNotIn("`Disposition` is", defs)

    def test_skip_if_fresh_and_force(self):
        self.major_v1()
        self.assertEqual(self.run_v(Model(), "v1", "--mode", "major"), 0)
        self.assertIn("[SKIPPED]", self.out)
        os.utime(os.path.join(self.R, "output/v1-sgai-spec.md"))
        self.assertEqual(self.run_v(Model(opens=[DONE]), "v1", "--mode", "major"), 0)
        self.assertNotIn("[SKIPPED]", self.out)

    def test_command_line(self):
        for args in (["v1", "--bogus"], ["v1", "--mode", "fast"], ["1"], ["v1", "--prev"], ["v1", "--jobs", "0"], []):
            with self.subTest(args=args):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(self.v.main(args), 64)


class Refine(Fixture):
    def test_walks_only_stale_and_carries_the_rest(self):
        m = Model(opens=[lines({"id": "G-1", "drop": True, "reason": "now stated"}, DONE)])
        self.assertEqual(self.refine_v11(m), 0, self.out)
        self.assertEqual(m.walked, ["R2.1"])            # §4 changed; R1.3 is code
        t1, t2 = self.trace("v1"), self.trace("v1.1")
        for u in ("R1.1", "R3.2", "UC-01"):
            self.assertEqual((t2[u]["how"], t2[u]["sections"], t2[u]["verdict"]),
                             ("carried", t1[u]["sections"], t1[u]["verdict"]))
        self.assertEqual(t2["R2.1"]["how"], "llm")
        self.assertEqual(len(m.open_prompts), 1)
        p = m.open_prompts[0]
        self.assertIn("===== SECTION 4 =====", p)
        self.assertNotIn("===== SECTION 2 =====", p)
        self.assertIn("----- G-1 (gap)", p)                # cites §4: re-judged
        self.assertIn("- A-1 — Two forms or two windows", p)  # cites §2: carried
        side = self.get("output-analysis/v1.1-spec-validation.md")
        self.assertIn("## Gaps (0)", side)
        self.assertIn("### A-1 — Two forms or two windows", side)
        self.assertIn("mode: refine over v1; walked 1 units by LLM, 1 by code, 9 carried over from v1", side)
        self.assertIn("carried from v1.", side)
        self.assertIn("re-judged and dropped by the open search: G-1 (now stated)", side)
        self.assertIn("DROPPED: G-1 (now stated)", self.out)

    def test_readers_parse_the_refine_sidecar(self):
        self.assertEqual(self.refine_v11(Model(opens=[lines({"id": "G-1", "drop": True, "reason": "r"}, DONE)])), 0)
        rc, out = self.tool("bin/check-promotable.py")
        self.assertEqual(rc, 1, out)
        for f, d in (("v1-spec-validation.md", "spec-validation.md"), ("v1-detail-review.md", "detail-review.md"),
                     ("v1-conformance-tests.json", "conformance-tests.json")):
            shutil.copy(os.path.join(self.R, "output-analysis", f), os.path.join(self.R, "dist", d))
        rc, out = self.tool("bin/compare-candidates.py", "v1.1", "--out", os.path.join(self.R, "cmp.md"))
        self.assertEqual(rc, 0, out)
        self.assertIn("THAN PUBLISHED", out)

    def test_not_met_new_source_changed_and_text_changed_are_walked(self):
        self.major_v1()
        t = json.loads(self.get("output-analysis/v1-trace.json"))
        t["units"]["R3.1"]["verdict"] = "partial"           # not met in v<P>
        del t["units"]["R3.2"]                              # new to the population
        t["units"]["R3.3"]["source"] = "vector-pending"     # source changed
        t["units"]["R3.4"]["unit_sha256"] = "0" * 16        # context/ text changed
        del t["units"]["R3.5"]["unit_sha256"]               # no hash: cannot show it is the same
        self.put("output-analysis/v1-trace.json", json.dumps(t))
        self.put("output/v1.1-sgai-spec.md", SPEC1)
        self.put("output-analysis/v1.1-conformance-tests.json", json.dumps(CONF))
        m = Model(opens=[lines({"unit": "R3.1", **{k: AMB[k] for k in ("routing", "section", "why_uncertain", "resolutions", "recommended", "searched")}}, DONE)])
        self.assertEqual(self.run_v(m, "v1.1", "--prev", "v1", "--mode", "refine"), 0, self.out)
        self.assertEqual(sorted(m.walked), ["R3.1", "R3.2", "R3.3", "R3.4", "R3.5"])

    def test_partial_row_with_unchanged_sections_keeps_its_row(self):
        w = {"R1.1": met("R1.1", "partial")}
        route = {"unit": "R1.1", "routing": "5.b", "section": "1", "why_uncertain": "w", "resolutions": "r",
                 "recommended": "KEEPME", "searched": "s"}
        self.assertEqual(self.run_v(Model(walker=w, opens=[lines(AMB, GAP, route, DONE)]), "v1", "--mode", "major"), 0, self.out)
        self.put("output/v1.1-sgai-spec.md", SPEC2)
        self.put("output-analysis/v1.1-conformance-tests.json", json.dumps(CONF))
        m = Model(walker=w, opens=[lines({"id": "G-1", "drop": True, "reason": "r"}, DONE)])
        self.assertEqual(self.run_v(m, "v1.1", "--prev", "v1", "--mode", "refine"), 0, self.out)
        self.assertIn("R1.1", m.walked)
        self.assertNotIn("COVERAGE ROWS TO ROUTE", m.open_prompts[0])
        side = self.get("output-analysis/v1.1-spec-validation.md")
        self.assertIn("| `R1.1` | `runtime` | `partial` | 5.b |", side)
        self.assertIn("KEEPME", side)

    def test_rejudged_entry_failing_twice_is_kept_from_prev(self):
        bad = dict(GAP, id="G-1", sections=[{"key": "9", "quotes": []}])
        rc = self.refine_v11(Model(opens=[lines(bad, DONE), lines(bad, DONE)]))
        self.assertEqual(rc, 1, self.out)
        self.assertIn("G-1 kept from v1 unchanged", self.out)
        side = self.get("output-analysis/v1.1-spec-validation.md")
        self.assertIn("### G-1 — Beacon timing", side)
        self.assertIn("- **Routing:** 5.c — See Deferred D-1.", side)

    def test_rejudged_entry_answered_keeps_its_id(self):
        new = dict(GAP, id="G-1", title="Beacon timing, again")
        self.assertEqual(self.refine_v11(Model(opens=[lines(new, DONE)])), 0, self.out)
        self.assertIn("### G-1 — Beacon timing, again", self.get("output-analysis/v1.1-spec-validation.md"))

    def test_patch_and_documents_disagree(self):
        self.major_v1()
        self.put("output/v1.1-sgai-spec.md", SPEC2)
        self.put("output-analysis/v1.1-conformance-tests.json", json.dumps(CONF))
        self.put("output-analysis/v1.1-patch.json", json.dumps({"sections_changed": ["4", "2"]}))
        self.assertEqual(self.run_v(Model(), "v1.1", "--prev", "v1", "--mode", "refine"), 2, self.out)
        self.assertIn("sections_changed ['2']", self.out)
        self.assertFalse(self.exists("output-analysis/v1.1-trace.json"))

    def test_refine_without_prev_trace_runs_as_major(self):
        self.major_v1()
        os.remove(os.path.join(self.R, "output-analysis/v1-trace.json"))
        self.put("output/v1.1-sgai-spec.md", SPEC2)
        self.put("output-analysis/v1.1-conformance-tests.json", json.dumps(CONF))
        m = Model(opens=[DONE])
        self.assertEqual(self.run_v(m, "v1.1", "--prev", "v1", "--mode", "refine"), 0, self.out)
        self.assertEqual(len(m.walked), 10)
        self.assertIn("run as a major", self.out)

    def test_mode_and_prev_deduced(self):
        rc = self.refine_v11(Model(opens=[lines({"id": "G-1", "drop": True, "reason": "r"}, DONE)]))
        self.assertEqual(rc, 0)
        m = Model(opens=[lines({"id": "G-1", "drop": True, "reason": "r"}, DONE)])
        self.assertEqual(self.run_v(m, "v1.1", "--force"), 0, self.out)
        self.assertEqual(m.walked, ["R2.1"])

    def test_carried_quote_no_longer_literal_turns_not_verifiable(self):
        self.major_v1()
        t = json.loads(self.get("output-analysis/v1-trace.json"))
        t["units"]["R3.2"]["sections"][0]["quotes"] = ["The Player logs beta."]
        self.put("output-analysis/v1-trace.json", json.dumps(t))
        self.put("output/v1.1-sgai-spec.md", SPEC2)
        self.put("output-analysis/v1.1-conformance-tests.json", json.dumps(CONF))
        m = Model(opens=[lines({"id": "G-1", "drop": True, "reason": "r"}, DONE)])
        self.assertEqual(self.run_v(m, "v1.1", "--prev", "v1", "--mode", "refine"), 1, self.out)
        self.assertEqual(self.trace("v1.1")["R3.2"]["verdict"], "not-verifiable")
        self.assertIn("REPORT: R3.2: not-verifiable, its quotation failed check-trace", self.out)
        self.assertIn("quotation failed bin/check-trace.py", self.get("output-analysis/v1.1-spec-validation.md"))
        rc, out = self.tool("bin/check-trace.py", "output-analysis/v1.1-trace.json",
                            "--rules", "output-analysis/v1.1-conformance-tests.json")
        self.assertEqual(rc, 0, out)


class OpenCheck(unittest.TestCase):
    """check_open, rule by rule."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("validate_oc", os.path.join(BIN, "validate.py"))
        cls.v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.v)
        cls.norm = {"2": cls.v.ct.normalise("The Player **MUST NOT** show two forms at once."),
                    "4": cls.v.ct.normalise("The Player fires `start` beacons.")}

    def errs(self, objs, ids=(), units=(), flags=()):
        good, errs, done = self.v.check_open(objs + [{"done": True}], self.norm, set(ids), set(units), set(flags))
        return good, errs

    def one(self, o, **kw):
        _, e = self.errs([o], **kw)
        return " ".join(m for v in e.values() for m in v)

    def test_good(self):
        g, e = self.errs([AMB, GAP])
        self.assertEqual((len(g), e), (2, {}))

    def test_each_rule(self):
        cases = {
            "kind": (dict(AMB, kind="issue"), "kind 'issue'"),
            "routing": (dict(AMB, routing="5.e"), "routing '5.e'"),
            "field": (dict(AMB, recommended=""), "5.b needs `recommended`"),
            "section key": (dict(AMB, sections=[{"key": "9", "quotes": []}]), "section '9' does not exist"),
            "routing section": (dict(AMB, section="9.9"), "`section` '9.9' is not a section key"),
            "quote": (dict(AMB, sections=[{"key": "2", "quotes": ["two windows"]}]), "quotation not literal in 2"),
            "gap names a section": (dict(GAP, sections=[]), "a gap names the section"),
            "edge quotes": (dict(AMB, kind="edge", sections=[{"key": "2", "quotes": []}]), "an edge entry quotes"),
            "title": (dict(AMB, title=" "), "title missing"),
            "5.a fields": (dict(AMB, routing="5.a"), "5.a needs `criterion`"),
            "5.d fields": (dict(AMB, routing="5.d"), "5.d needs `replacement`"),
            "5.c fields": (dict(AMB, routing="5.c"), "5.c needs `context_file`"),
        }
        for name, (o, msg) in cases.items():
            with self.subTest(rule=name):
                self.assertIn(msg, self.one(o))

    def test_ids_rows_flags(self):
        self.assertIn("not one of the items sent", self.one(dict(GAP, id="G-7"), ids={"G-1"}))
        self.assertIn("does not match the id", self.one(dict(AMB, id="G-1"), ids={"G-1"}))
        self.assertIn("a drop needs its reason", self.one({"id": "G-1", "drop": True}, ids={"G-1"}))
        self.assertIn("only a re-judged entry", self.one({"drop": True, "reason": "x", "title": "t"}))
        g, e = self.errs([], ids={"G-1"}, units={"R1.1"}, flags={"1"})
        self.assertEqual(sorted(e), ["flag:1", "id:G-1", "unit:R1.1"])
        self.assertIn("not one of the items sent", self.one({"unit": "R9.9", "routing": "5.c", "context_file": "a",
                                                             "suggested_edit": "b", "leverage": "c", "searched": "d"}))

    def test_done_line(self):
        _, _, done = self.v.check_open([AMB], self.norm, set(), set(), set())
        self.assertFalse(done)


class Planning(Fixture):
    def test_batches_at_most_eight_and_split_by_size(self):
        st = self.v.Step("v1", None, "major", 1, None, False, True)
        st.W = self.R
        st.inputs()
        st.plan()
        st.draft()
        st.walk = st.walk * 1          # 10 units
        st.batches()
        self.assertEqual([len(g) for g, _ in st.batch_list], [8, 2])
        self.v.MAX_BATCH_CHARS = 1     # every batch over the limit: split down to single units
        st.batches()
        self.assertEqual({len(g) for g, _ in st.batch_list}, {1})
        self.assertEqual(sorted(u for g, _ in st.batch_list for u in g), sorted(st.walk))

    def test_chunks_overlap_by_one_section(self):
        st = self.v.Step("v1", None, "major", 1, None, False, True)
        st.W = self.R
        st.inputs()
        st.stale = {"changed": [], "added": []}
        self.v.OPEN_SPEC_CHARS = 200
        ch = st.chunks()
        self.assertGreater(len(ch), 2)
        size = {k: len(st.secs[k].text) for k in st.order}
        overlaps = 0
        for a, b in zip(ch, ch[1:]):
            if a[-1] == b[0]:
                overlaps += 1
            else:   # no overlap only when the two sections do not fit together
                self.assertGreater(size[a[-1]] + size[b[0]], self.v.OPEN_SPEC_CHARS)
            self.assertLessEqual(sum(size[k] for k in b), max(self.v.OPEN_SPEC_CHARS, size[b[0]]))
        self.assertGreater(overlaps, 0)
        self.assertEqual(sorted({k for c in ch for k in c}), sorted(k for k in st.order if k not in self.v.SKIP_KEYS))


if __name__ == "__main__":
    unittest.main()
