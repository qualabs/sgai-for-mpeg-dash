#!/usr/bin/env python3
"""Tests of the level-2 catalogue (bin/conformance/spec/, ADR 0050, 0054).

  * every negative spec-*.expect.json is caught by its rule at its place,
    and that FAIL is not there on the example it was derived from: the one
    change is what makes it fail;
  * the rules that already fail on the published schema have a positive:
    the schema with the carrier added passes;
  * every rule with a check has a negative;
  * stale() is empty on the real context/, and names what changed on a
    copy: a criterion's text, a retired criterion, a removed criterion, a
    new criterion, and an index element whose rule was removed.

Run all (from the project root):
    uv run -q --no-project --with lxml==6.1.3 python -I bin/test_conformance_spec.py
Run one:
    ... python -I bin/test_conformance_spec.py -k R4.1
(`python -I -m unittest bin/test_conformance_spec.py` cannot import the file:
-I keeps the current directory off sys.path.)
"""
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

from conformance import extract, fixtures, runner, spec  # noqa: E402
from conformance.model import Outcome, Report  # noqa: E402
from conformance.spec import criteria  # noqa: E402

ROOT = BIN.parent
SPEC = ROOT / "dist" / "sgai-spec.md"
CONTEXT = ROOT / "context"
TMP = os.environ.get("XDG_RUNTIME_DIR") or None
BASE = None


def setUpModule():
    global BASE
    report = Report()
    BASE = runner.load(SPEC, None, report)
    if BASE is None or report.cannot:
        raise unittest.SkipTest(f"cannot build the base context: {report.cannot}")


def hits(results, exp):
    return [r for r in results if r.outcome is Outcome.FAIL and r.rule == exp["rule"]
            and exp.get("xpath_contains", "") in (r.xpath + " " + r.subject + " " + r.detail)]


def run_on_text(text: str, suffix: str):
    """All rules over one document (or request), built as fixtures.ctx_for builds a negative."""
    with tempfile.TemporaryDirectory(dir=TMP) as d:
        p = Path(d) / f"case{suffix}"
        p.write_text(text, encoding="utf-8")
        return runner.run_all(fixtures.ctx_for(p, BASE))


def original(exp):
    """The text the negative was derived from, and its suffix."""
    md = SPEC.read_text(encoding="utf-8")
    m = re.search(r"xml#(\d+)", exp["derived_from"])
    if m:
        b = {x.index: x for x in extract.blocks(md)}[int(m.group(1))]
        return b.text, ".xml"
    line = int(re.search(r"request \(line (\d+)\)", exp["derived_from"]).group(1))
    r = [x for x in extract.requests(md) if x.line == line][0]
    return f"GET {r.target} HTTP/1.1\n", ".request.txt"


class Negatives(unittest.TestCase):
    """One test per negative: test_<file name>."""


def _negative_test(path):
    def test(self):
        v = fixtures.evaluate(path, BASE, runner.run_all)
        exp = v["expected"]
        self.assertTrue(v["caught"], f"{v['name']}: {exp['rule']} gave no FAIL containing {exp['xpath_contains']!r}")
        text, suffix = original(exp)
        before = run_on_text(text, suffix)
        if not exp["change"].startswith("none"):
            self.assertFalse(hits(before, exp), f"{v['name']}: the FAIL is already there on {exp['derived_from']}")
        new = sorted(set(v["other_fails"]) - {r.rule for r in before if r.outcome is Outcome.FAIL})
        if new:  # other rules the one change also breaks: reported, not asserted
            sys.stderr.write(f"\n  {v['name']}: the change also makes {', '.join(new)} FAIL")
    return test


for _p in sorted(fixtures.NEG.glob("spec-*.expect.json")):
    setattr(Negatives, "test_" + _p.name[: -len(".expect.json")], _negative_test(_p))


XSD_POSITIVES = {
    # rule: (old, new) on the published extension schema; the rule must then PASS.
    "R12.1a": ('      <xs:enumeration value="pause-fullscreen"/>\n',
               '      <xs:enumeration value="squeezeback-frame"/>\n      <xs:enumeration value="pause-fullscreen"/>\n'),
    "R34.1a": ('    <xs:attribute name="linearRelation" type="svta:LinearRelationType"/>\n',
               '    <xs:attribute name="linearRelation" type="svta:LinearRelationType"/>\n'
               '    <xs:attribute name="executeOnce" type="xs:boolean" default="false"/>\n'),
    "R34.9a": ('    <xs:attribute name="linearRelation" type="svta:LinearRelationType"/>\n',
               '    <xs:attribute name="linearRelation" type="svta:LinearRelationType"/>\n'
               '    <xs:attribute name="startWithOffset" type="xs:boolean" default="false"/>\n'),
    "R13.6a": ('  <xs:complexType name="RenderableAssetType">\n',
               '  <xs:complexType name="RenderableAssetType">\n    <xs:sequence>\n'
               '      <xs:element name="Tracking" type="dash:EventStreamType" minOccurs="0"/>\n    </xs:sequence>\n'),
}


class Positives(unittest.TestCase):
    def test_xsd_positives(self):
        xsd = extract.extension_schema(extract.blocks(SPEC.read_text(encoding="utf-8")))[0].text
        for rid, (old, new) in XSD_POSITIVES.items():
            with self.subTest(rule=rid):
                self.assertEqual(xsd.count(old), 1)
                rs = [r for r in run_on_text(xsd.replace(old, new), ".xml") if r.rule == rid]
                self.assertTrue(rs)
                self.assertTrue(all(r.outcome is Outcome.PASS for r in rs), [r.as_dict() for r in rs])

    def test_every_check_has_a_negative(self):
        have = {json.loads(p.read_text())["rule"] for p in fixtures.NEG.glob("spec-*.expect.json")}
        missing = [r.id for r in spec.RULES if r.check is not None and r.id not in have]
        self.assertEqual(missing, [])


class Stale(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.ctx = Path(self.tmp.name) / "context"
        shutil.copytree(CONTEXT, self.ctx)
        self.req = self.ctx / criteria.REQUIREMENTS

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, old, new):
        t = self.req.read_text(encoding="utf-8")
        self.assertEqual(t.count(old), 1, old)
        self.req.write_text(t.replace(old, new), encoding="utf-8")

    def test_real_context_is_not_stale(self):
        self.assertEqual(spec.stale(CONTEXT), [])

    def test_index_has_75_elements_all_covered(self):
        idx, cannot = criteria.index(criteria.read(CONTEXT))
        self.assertEqual(cannot, [])
        self.assertEqual({k: len(v) for k, v in idx.items()}, {"I-MPD": 27, "I-REQ": 16, "I-RES": 32})
        covering = {r.criterion for r in spec.RULES if r.check is not None or r.not_verifiable}
        self.assertEqual([e for items in idx.values() for e, c in items if c not in covering], [])

    def test_changed_text(self):
        self.edit("Publisher-private layout names MUST NOT appear", "Publisher-private layout names MAY appear")
        out = spec.stale(self.ctx)
        self.assertTrue(any("rule R12.2:" in x and "text of R12.2 changed" in x for x in out), out)
        self.assertEqual(len(out), 1, out)

    def test_rewrap_is_not_a_change(self):
        self.edit("Publisher-private layout names MUST NOT appear", "Publisher-private layout\n    names MUST NOT appear")
        self.assertEqual(spec.stale(self.ctx), [])

    def test_retired(self):
        self.edit("| R41.1 | R41.3 |", "| R41.1 | R41.3 |\n| R33.4 | R33.2 |")
        out = spec.stale(self.ctx)
        self.assertTrue(any("rule R33.4 cites R33.4, retired" in x for x in out), out)

    def test_removed_criterion(self):
        t = self.req.read_text(encoding="utf-8")
        new = re.sub(r"  - \*\*R35\.2\*\* \(APS\):.*?(?=\n  - \*\*R35\.7)", "", t, flags=re.S)
        self.assertNotEqual(t, new)
        self.req.write_text(new, encoding="utf-8")
        out = spec.stale(self.ctx)
        self.assertTrue(any("rule R35.2 cites R35.2, which context/03 no longer defines" in x for x in out), out)

    def test_new_criterion(self):
        self.edit("  - **R35.7** (spec document):", "  - **R35.9** (APS): Something new.\n  - **R35.7** (spec document):")
        out = spec.stale(self.ctx)
        self.assertEqual(out, ["level 2: criterion R35.9 of context/03 has no rule"])

    def test_index_element_without_rule(self):
        rules = [r for r in spec.RULES if r.criterion != "R33.4"]
        out = spec.stale(CONTEXT, rules)
        self.assertTrue(any("I-MPD element '`PlayList` metric request (`Metrics`)' (R33.4) is covered by no rule" in x
                            for x in out), out)

    def test_runner_exits_2_when_stale(self):
        self.edit("Publisher-private layout names MUST NOT appear", "Publisher-private layout names MAY appear")
        report = Report()
        ctx = runner.load(SPEC, self.ctx, report)
        runner.level2(ctx, report)
        self.assertEqual(report.exit_code(), 2)
        self.assertTrue(any("R12.2" in x for x in report.cannot), report.cannot)


if __name__ == "__main__":
    unittest.main(verbosity=1)
