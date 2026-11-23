#!/usr/bin/env python3
"""check-trace: every unit traced, every section real, every quotation
literal under exactly the declared normalisation, every rule real and
deciding; `sources`, `stale` and `batch` give what the validation needs.

Synthetic cases work on a small spec and catalogue in a private temporary
directory; the last class runs on the real v12.6 trace.
Run: python3 bin/test_check_trace.py
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
spec = importlib.util.spec_from_file_location("ct", os.path.join(BIN, "check-trace.py"))
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)
sys.path.insert(0, BIN)
import spec_sections  # noqa: E402

SPEC = """# Title

## 1 Scope

The Player MUST render the ad.
It **MUST NOT** show `two` forms
at once, and says \"hi\".

| D1 | renders |

## 2 Other

Unrelated text, with _under_ score and an … ellipsis.
"""

RULES = {
    "R1.1a": {"level": 2, "criterion": "R1.1", "not_verifiable": ""},
    "R1.1b": {"level": 2, "criterion": "R1.1", "not_verifiable": "a property of the prose"},
    "R1.2": {"level": 2, "criterion": "R1.2", "not_verifiable": ct.PLAYER},
    "E-1": {"level": 1, "criterion": "", "not_verifiable": ""},
    "P-LEGACY": {"level": 3, "criterion": "", "not_verifiable": ""},
}

POP = [("R1.1", "criterion"), ("R1.2", "criterion"), ("UC-01", "use-case")]


def good_trace():
    return {"format": "sgai-trace/1", "spec": "spec.md", "units": {
        "R1.1": {"kind": "criterion", "source": "code", "rules": ["R1.1a", "E-1"],
                 "residual": ["R1.1b"],
                 "sections": [{"key": "1", "quotes": ["The Player MUST render the ad."]}]},
        "R1.2": {"kind": "criterion", "source": "vector-pending", "sections": []},
        "UC-01": {"kind": "use-case", "source": "llm", "verdict": "met",
                  "sections": [{"key": "2", "quotes": ["Unrelated text"]}]},
    }}


def secs(text=SPEC):
    return spec_sections.by_key(spec_sections.split(text))


def checks(trace, pop=POP, rules=RULES):
    return [(f["check"], f["unit"]) for f in ct.check(trace, secs(), pop, rules)]


class Normalise(unittest.TestCase):
    def lit(self, quote, key="1"):
        t = good_trace()
        t["units"]["UC-01"]["sections"] = [{"key": key, "quotes": [quote]}]
        return ("T-QUOTE", "UC-01") not in checks(t)

    def test_clean_trace_has_no_finding(self):
        self.assertEqual(checks(good_trace()), [])

    def test_emphasis_and_code_spans_are_ignored(self):
        self.assertTrue(self.lit("It MUST NOT show two forms"))
        self.assertTrue(self.lit("It **MUST NOT** show `two` forms"))

    def test_line_breaks_and_runs_of_space_are_one_space(self):
        self.assertTrue(self.lit("two forms   at once"))

    def test_escaped_quotes(self):
        self.assertTrue(self.lit('says \\"hi\\"'))
        self.assertTrue(self.lit('says "hi"'))

    def test_pipes_ellipsis_underscore_case_are_not_normalised(self):
        self.assertFalse(self.lit("/ D1 / renders /"))
        self.assertTrue(self.lit("| D1 | renders |"))
        self.assertFalse(self.lit("The Player … the ad."))
        self.assertFalse(self.lit("with under score", key="2"))
        self.assertFalse(self.lit("the player must render the ad."))

    def test_changed_quote_fails(self):
        self.assertFalse(self.lit("The Player MUST render an ad."))

    def test_quote_of_another_section_fails(self):
        self.assertFalse(self.lit("Unrelated text", key="1"))

    def test_empty_quote_fails(self):
        self.assertFalse(self.lit("  ** ` "))


class Checks(unittest.TestCase):
    def test_missing_unit(self):
        t = good_trace()
        del t["units"]["R1.2"]
        self.assertIn(("T-POP", "R1.2"), checks(t))

    def test_extra_unit(self):
        t = good_trace()
        t["units"]["R9.9"] = {"source": "llm", "sections": []}
        self.assertIn(("T-POP", "R9.9"), checks(t))

    def test_nonexistent_section(self):
        t = good_trace()
        t["units"]["UC-01"]["sections"] = [{"key": "9.9", "quotes": []}]
        self.assertEqual(checks(t), [("T-SECTION", "UC-01")])

    def test_unknown_source(self):
        t = good_trace()
        t["units"]["UC-01"]["source"] = "model"
        self.assertEqual(checks(t), [("T-SOURCE", "UC-01")])

    def test_code_without_rules(self):
        t = good_trace()
        t["units"]["R1.1"]["rules"] = []
        self.assertIn(("T-SOURCE", "R1.1"), checks(t))

    def test_vector_without_vectors(self):
        t = good_trace()
        t["units"]["R1.2"]["source"] = "vector"
        self.assertEqual(checks(t), [("T-SOURCE", "R1.2")])
        t["units"]["R1.2"]["vectors"] = ["uc-01-d1"]
        self.assertEqual(checks(t), [])

    def test_rule_not_in_catalogue(self):
        t = good_trace()
        t["units"]["R1.1"]["rules"] = ["R1.1z"]
        self.assertEqual(checks(t), [("T-RULE", "R1.1")])

    def test_level_3_rule_is_not_a_code_rule(self):
        t = good_trace()
        t["units"]["R1.1"]["rules"] = ["P-LEGACY"]
        self.assertEqual(checks(t), [("T-RULE", "R1.1")])

    def test_not_verifiable_rule_does_not_decide(self):
        t = good_trace()
        t["units"]["R1.1"]["rules"] = ["R1.1b"]
        self.assertEqual(checks(t), [("T-RULE", "R1.1")])

    def test_rule_of_another_criterion(self):
        t = good_trace()
        t["units"]["UC-01"].update(source="code", rules=["R1.1a"])
        self.assertEqual(checks(t), [("T-RULE", "UC-01")])

    def test_residual_must_exist(self):
        t = good_trace()
        t["units"]["R1.1"]["residual"] = ["nope"]
        self.assertEqual(checks(t), [("T-RULE", "R1.1")])

    def test_summary_counts(self):
        t = good_trace()
        t["units"]["UC-01"]["sections"][0]["quotes"].append("absent text")
        s = ct.summary(t, ct.check(t, secs(), POP, RULES))
        self.assertEqual(s["by_source"], {"code": 1, "vector-pending": 1, "llm": 1})
        self.assertEqual((s["quotes"], s["section_refs"], s["with_residual"]), (3, 2, 1))
        self.assertEqual(s["findings"], {"T-QUOTE": 1})


class Sources(unittest.TestCase):
    CONF = {"rules": dict(RULES, **{"R2.1": {"level": 2, "criterion": "R2.1", "not_verifiable": ""}}),
            "results": [{"rule": "R1.1a", "outcome": "PASS"}, {"rule": "R1.1a", "outcome": "PASS"}]}

    def src(self, results=None):
        conf = dict(self.CONF)
        if results is not None:
            conf["results"] = results
        return ct.sources(conf, POP + [("R2.1", "criterion")])

    def test_code_pass_is_met_with_residual(self):
        e = self.src()["R1.1"]
        self.assertEqual((e["source"], e["verdict"], e["rules"], e["residual"]),
                         ("code", "met", ["R1.1a"], ["R1.1b"]))

    def test_code_fail_is_contradicted(self):
        e = self.src([{"rule": "R1.1a", "outcome": "PASS"}, {"rule": "R1.1a", "outcome": "FAIL"}])["R1.1"]
        self.assertEqual((e["source"], e["verdict"]), ("code", "contradicted"))

    def test_code_without_instance_falls_back_to_llm(self):
        e = self.src([{"rule": "R1.1a", "outcome": "NOT_APPLICABLE"}])["R1.1"]
        self.assertEqual(e["source"], "llm")
        self.assertTrue(e["reason"])

    def test_player_rule_is_vector_pending(self):
        e = self.src()["R1.2"]
        self.assertEqual((e["source"], e["rules"]), ("vector-pending", []))

    def test_no_rule_is_llm(self):
        self.assertEqual(self.src()["UC-01"]["source"], "llm")


class Stale(unittest.TestCase):
    def test_changed_and_removed_sections_mark_their_units(self):
        t = good_trace()
        new = SPEC.replace("render the ad", "render one ad")
        r = ct.stale(t, SPEC, new)
        self.assertEqual((r["changed"], r["units"]), (["1"], ["R1.1"]))
        r = ct.stale(t, SPEC, SPEC.split("## 2 Other")[0])
        self.assertEqual((r["removed"], r["units"]), (["2"], ["UC-01"]))

    def test_nothing_changed(self):
        self.assertEqual(ct.stale(good_trace(), SPEC, SPEC)["units"], [])


class Batch(unittest.TestCase):
    REQ = ("- **R1. Render.** The Player MUST render. It MUST NOT stall.\n"
           "  - **R1.1** (Player): render the ad.\n"
           "    continued.\n"
           "  - **R1.2** (Player): other.\n"
           "  Then the prose SHALL go on.\n")
    UC = "## Cases\n\n### UC-01 — One\n\nbody one\n\n#### detail\n\nmore\n\n### UC-02 — Two\n\nbody two\n"

    def test_unit_texts(self):
        self.assertEqual(ct.unit_text("R1.1", self.REQ, self.UC),
                         "- **R1.1** (Player): render the ad.\n    continued.")
        uc = ct.unit_text("UC-01", self.REQ, self.UC)
        self.assertIn("more", uc)
        self.assertNotIn("body two", uc)
        p3 = ct.unit_text("R1#p3", self.REQ, self.UC)
        self.assertIn(">>   Then the prose SHALL go on.", p3)
        self.assertNotIn("R1.1", p3)
        self.assertIsNone(ct.unit_text("R1#p4", self.REQ, self.UC))

    def test_batch_prints_only_the_traced_sections(self):
        t = good_trace()
        t["units"]["UC-01"]["sections"] = [{"key": "1", "quotes": []}]
        t["units"]["R1.1"]["sections"] = [{"key": "1", "quotes": []}]
        text, missing = ct.batch(t, secs(), ["R1.1", "UC-01"], self.REQ, self.UC)
        self.assertEqual(missing, [])
        self.assertEqual(text.count("===== SECTION 1 ====="), 1)
        self.assertNotIn("Unrelated text", text)

    def test_batch_missing_unit(self):
        _, missing = ct.batch(good_trace(), secs(), ["R7.7"], self.REQ, self.UC)
        self.assertEqual(missing, ["R7.7"])


class Cli(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(dir=os.environ.get("XDG_RUNTIME_DIR"))
        self.p = lambda n: os.path.join(self.d, n)
        with open(self.p("spec.md"), "w") as fh:
            fh.write(SPEC)
        with open(self.p("pop.tsv"), "w") as fh:
            fh.write("".join(f"{u}\t{k}\n" for u, k in POP))
        with open(self.p("ct.json"), "w") as fh:
            json.dump({"rules": RULES, "results": []}, fh)
        self.trace(good_trace())

    def tearDown(self):
        shutil.rmtree(self.d)

    def trace(self, t):
        t["spec"] = self.p("spec.md")
        with open(self.p("t.json"), "w") as fh:
            json.dump(t, fh)

    def run_ct(self, *args):
        return subprocess.run([sys.executable, os.path.join(BIN, "check-trace.py"), *args],
                              capture_output=True, text=True)

    def std(self, *extra):
        return self.run_ct(self.p("t.json"), "--population", self.p("pop.tsv"),
                           "--rules", self.p("ct.json"), *extra)

    def test_exit_0_clean(self):
        self.assertEqual(self.std().returncode, 0)

    def test_exit_1_on_finding(self):
        t = good_trace()
        t["units"]["R1.1"]["sections"][0]["quotes"] = ["The Player MAY render the ad."]
        self.trace(t)
        r = self.std()
        self.assertEqual(r.returncode, 1)
        self.assertIn("T-QUOTE\tR1.1", r.stdout)

    def test_exit_2_unreadable(self):
        with open(self.p("t.json"), "w") as fh:
            fh.write("{not json")
        self.assertEqual(self.std().returncode, 2)
        self.trace(good_trace())
        os.remove(self.p("spec.md"))
        self.assertEqual(self.std().returncode, 2)

    def test_exit_2_spec_cannot_be_split(self):
        with open(self.p("spec.md"), "w") as fh:
            fh.write("## 1 A\n\n## 1 B\n")
        self.assertEqual(self.std().returncode, 2)

    def test_exit_64(self):
        self.assertEqual(self.run_ct(self.p("t.json"), "--populacion", "x").returncode, 64)
        self.assertEqual(self.run_ct().returncode, 64)
        self.assertEqual(self.run_ct("stale", self.p("t.json")).returncode, 64)

    def test_json_and_summary_keep_the_exit(self):
        t = good_trace()
        t["units"]["UC-01"]["sections"][0]["key"] = "7"
        self.trace(t)
        r = self.std("--json")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(r.stdout)["findings"][0]["check"], "T-SECTION")
        r = self.std("--summary")
        self.assertEqual((r.returncode, json.loads(r.stdout)["findings"]), (1, {"T-SECTION": 1}))


EVID = os.path.join(ROOT, ".project", "phases", "10-code-first-pipeline", "tasks", "T-08")
V126 = os.path.join(ROOT, "output-analysis", "v12.6-trace.json")


@unittest.skipUnless(os.path.isfile(V126), "no v12.6 trace")
class RealV126(unittest.TestCase):
    """The v12.6 trace against the population v12.6 was walked on (context/
    at 924afcb): the only findings are the 33 quotations not literal."""

    def setUp(self):
        with open(V126) as fh:
            self.t = json.load(fh)
        self.secs = ct.spec_index(os.path.join(ROOT, self.t["spec"]))
        self.pop = ct.population(os.path.join(EVID, "population-924afcb.tsv"))
        # The rule checks are covered above; here the catalogue is the one the
        # trace names, so only the population, sections and quotes are judged.
        self.rules = {}
        for u, e in self.t["units"].items():
            for r in e.get("rules") or []:
                self.rules[r] = {"level": 2, "criterion": u, "not_verifiable": ""}
            for r in e.get("residual") or []:
                self.rules[r] = {"level": 2, "criterion": u, "not_verifiable": "prose"}

    def test_only_the_non_literal_quotes(self):
        f = ct.check(self.t, self.secs, self.pop, self.rules)
        self.assertEqual({x["check"] for x in f}, {"T-QUOTE"})
        self.assertEqual(len(f), 33)

    def test_a_changed_quote_and_a_missing_section_fail(self):
        u = self.t["units"]["R2.3"]
        u["sections"][0]["quotes"][0] = u["sections"][0]["quotes"][0].replace("MUST", "SHOULD", 1)
        self.t["units"]["R2.4"]["sections"].append({"key": "99.9", "quotes": []})
        f = [(x["check"], x["unit"]) for x in ct.check(self.t, self.secs, self.pop, self.rules)]
        self.assertIn(("T-QUOTE", "R2.3"), f)
        self.assertIn(("T-SECTION", "R2.4"), f)
        self.assertEqual(len(f), 35)


if __name__ == "__main__":
    unittest.main()
