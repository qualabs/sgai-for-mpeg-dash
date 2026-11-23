#!/usr/bin/env python3
"""Tests of the level-1 catalog (bin/conformance/dash/, ADR 0049).

(a) every committed negative fixtures/negative/dash-* is caught by its rule,
    at its place;
(b) every rule with a check gives PASS or NOT_APPLICABLE on each of ISO's 41
    6th-edition examples it applies to (ADR 0054: the reference does not come
    from our checks);
plus the catalog's own shape: ids unique, every rule either code or a reason,
every coded rule with one negative.

Run from the project root:
  uv run -q --no-project --with lxml==6.1.3 python -I -m unittest bin/test_conformance_dash.py
"""
import sys
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent
ROOT = BIN.parent
sys.path.insert(0, str(BIN))

from conformance import extract, fixtures, iso, runner  # noqa: E402
from conformance.dash import RULES  # noqa: E402
from conformance.model import Outcome, Report  # noqa: E402

DIST = ROOT / "dist" / "sgai-spec.md"
# DR-3a finds occurrences by code but never FAILs: whether a legacy Player was
# expected to process a nested DASH element is the author's intent, so an
# occurrence is NOT_VERIFIABLE. Its "negative" is that it finds one
# (test_dr3a_finds_nested_dash), not a FAIL.
FINDS_ONLY = {"DR-3a"}
CODED = [r for r in RULES if r.check is not None and r.id not in FINDS_ONLY]

# Rules whose block kind has no instance among ISO's examples: no external
# positive exists for them, only the spec's own examples. Kept explicit so a
# change in coverage shows up here.
NO_ISO_INSTANCE = {"DR-1a", "DR-1b", "DR-1c", "DR-1d", "DR-1e", "DR-1f", "DR-1g", "DR-1h", "DR-1i"}

# A negative may break a property two sentences state: xlink on a List MPD is
# barred by §5.3.1.4 (MPD@type "list") and by §8.14 rule 3 (List profile).
SHARED = {"dash-DR-10b-xlink-in-list-mpd": {"K-15a"}, "dash-K-15a-xlink-in-list-profile": {"DR-10b"}}


_CTX = None


def base_ctx():
    global _CTX
    if _CTX is None:
        rep = Report()
        _CTX = runner.load(DIST, ROOT / "context", rep)
        assert _CTX is not None and not rep.cannot, rep.cannot
    return _CTX


def iso_blocks(ctx):
    out = []
    for i, p in enumerate(iso.examples(ctx.isodir), 1):
        b = extract.Block(i, 1, p.read_text())
        extract.classify(b)
        out.append((p.name, b))
    return out


def dash_negatives():
    return [p for p in fixtures.negatives() if p.name.startswith("dash-")]


class Catalog(unittest.TestCase):
    def test_shape(self):
        ids = [r.id for r in RULES]
        self.assertEqual(len(ids), len(set(ids)), "duplicate rule id")
        for r in RULES:
            with self.subTest(r.id):
                self.assertEqual(r.level, 1)
                self.assertTrue(r.quote.strip() and r.source.strip())
                self.assertTrue(r.check is not None or r.not_verifiable.strip(),
                                "a rule is code or says why it cannot be")
                self.assertFalse(r.check is not None and r.not_verifiable)

    def test_every_coded_rule_has_one_negative(self):
        by_rule = {}
        for p in dash_negatives():
            _, exp, case = fixtures.load_case(p)
            self.assertTrue(case.exists(), p.name)
            by_rule.setdefault(exp["rule"], []).append(p.name)
        self.assertEqual(sorted(by_rule), sorted(r.id for r in CODED))
        for rid, names in by_rule.items():
            self.assertEqual(len(names), 1, f"{rid}: {names}")


class FindsOnly(unittest.TestCase):
    def test_dr3a_finds_nested_dash(self):
        rule = next(r for r in RULES if r.id == "DR-3a")
        case = fixtures.NEG / "core-DR7-adaptationsets-inside-foreign.xml"
        b = extract.Block(1, 1, case.read_text())
        extract.classify(b)
        rs = rule.check(base_ctx(), b)
        self.assertTrue(rs and all(r.outcome is Outcome.NOT_VERIFIABLE for r in rs), rs)
        self.assertTrue(any("AdaptationSet" in r.detail for r in rs))
        clean = next(x for x in base_ctx().blocks if x.index == 10)
        self.assertEqual([r.outcome for r in rule.check(base_ctx(), clean)], [Outcome.PASS])


class Negatives(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = base_ctx()

    def test_dash_negatives(self):
        for p in dash_negatives():
            with self.subTest(p.name):
                v = fixtures.evaluate(p, self.ctx, runner.run_all)
                self.assertTrue(v["caught"], f"{v['expected']['rule']} did not FAIL at "
                                f"{v['expected']['xpath_contains']!r}; other fails {v['other_fails']}")
                # Level 2 judges a document against context/03 and is not this
                # catalog's to answer for; level 1 must stay quiet but for SHARED.
                allowed = SHARED.get(v["name"], set())
                level1 = {r.id for r in runner.all_rules() if r.level == 1}
                self.assertEqual((set(v["other_fails"]) & level1) - allowed, set(),
                                 "a negative should break one thing")


class IsoPositives(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = base_ctx()
        cls.blocks = iso_blocks(cls.ctx)

    def test_forty_one_examples(self):
        self.assertEqual(len(self.blocks), 41)

    def test_every_rule_pass_or_not_applicable(self):
        seen = set()
        for rule in CODED:
            for name, b in self.blocks:
                if b.kind not in rule.applies_to:
                    continue
                seen.add(rule.id)
                for res in rule.check(self.ctx, b):
                    with self.subTest(rule=rule.id, example=name):
                        self.assertIn(res.outcome, (Outcome.PASS, Outcome.NOT_APPLICABLE),
                                      f"{res.xpath}: {res.detail}")
        self.assertEqual({r.id for r in CODED} - seen, NO_ISO_INSTANCE)


if __name__ == "__main__":
    unittest.main()
