#!/usr/bin/env python3
"""Tests of bin/check-behaviour.py (ADR 0077, ADR 0078), one break per check,
each on a copy of spec-source/ and context/:

  * the tree as it is: exit 1, the population of 76 read from the catalogue,
    the 15 index entries, the 61 uncovered and nothing else;
  * the population rule: PLAYER prefix, "level 3" in a reason, "level 3a"
    alone, a rule with a check; an empty population and a criterion the
    catalogue names that 03 lacks are cannot-tell;
  * a valid test covers its criterion with no finding and NOT_VERIFIABLE —
    no executor;
  * B-SCHEMA: no criterion, `uc` in place of it, the file name, not YAML,
    the index (format, reason, a criterion twice);
  * B-HASH: a test's hash changed, an entry's criterion changed in 03 -> 2;
  * B-COVER: an entry removed, a test and an entry for one criterion;
  * B-POP: a criterion outside the population, one 03 does not define;
  * B-RETIRED: a retired criterion -> 2;
  * the shared checks on a test: aps (schema, document, a request with no
    answered_by), geometry (schema, viewport, element shown, time);
  * a UC vector that also names a criterion fails the schema;
  * the command line: 64, --help, criterion, uncovered, --json.

Run (from the project root):  python3 bin/test_check_behaviour.py
"""
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

BIN = Path(__file__).resolve().parent
ROOT = BIN.parent
_spec = importlib.util.spec_from_file_location("check_behaviour", BIN / "check-behaviour.py")
cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cb)
if __name__ == "__main__":
    cb.cs.ensure_deps(os.path.abspath(__file__), sys.argv[1:])
import jsonschema  # noqa: E402
import yaml  # noqa: E402
from conformance.model import Rule  # noqa: E402
from conformance.spec import catalog, criteria  # noqa: E402

TMP = os.environ.get("XDG_RUNTIME_DIR") or None
TEXT03 = criteria.read(ROOT / "context")
OTHERS = ["R4.8", "R6.5", "R7.1", "R12.5", "R13.1", "R13.6", "R19.3", "R20.4", "R26.1", "R27.1", "R28.1",
          "R32.1", "R34.1", "R34.6", "R34.9", "R36.1", "R40.9"]
NV = ["R1.6", "R3.2", "R11.2", "R21.1", "R29.10", "R33.2", "R37.1", "R41.4", "R41.5", "R41.6", "R41.7",
      "R42.3", "R44.3", "R47.2", "R48.3"]


def sha(cid):
    return criteria.pin_entry(TEXT03, cid)["sha256"]


def a_test(cid="R4.9"):
    """UC-01's vector turned into a behaviour test of `cid`."""
    v = yaml.safe_load((ROOT / "spec-source" / "scenarios" / "UC-01.yaml").read_text())
    for k in ("uc", "uc_sha256", "missing_carrier", "disagreements"):
        del v[k]
    v = {"format": v.pop("format"), "criterion": cid, "criterion_sha256": sha(cid), **v}
    return v


class Tree:
    def __init__(self):
        base = Path(TMP) / "cto" if TMP else None
        if base:
            base.mkdir(parents=True, exist_ok=True)
        self.dir = Path(tempfile.mkdtemp(prefix="t02-behav-", dir=base))
        self.src = self.dir / "spec-source"
        self.ctx = self.dir / "context"
        shutil.copytree(ROOT / "spec-source", self.src)
        shutil.copytree(ROOT / "context", self.ctx)
        self.b = self.src / "behaviour"

    def close(self):
        shutil.rmtree(self.dir)

    def put(self, name, v):
        (self.b / name).write_text(yaml.safe_dump(v, sort_keys=False, allow_unicode=True))

    def index(self):
        return yaml.safe_load((self.b / "index.yaml").read_text())

    def edit(self, rel, old, new, root=None):
        p = (root or self.src) / rel
        t = p.read_text()
        assert old in t, (rel, old)
        p.write_text(t.replace(old, new, 1))

    def run(self, pop=None):
        out = cb.run(self.src, self.ctx, pop)
        out["exit"] = cb.exit_code(out)
        return out


def found(out, check, key=None, text=""):
    return [f for f in out["findings"] if f["check"] == check and (key is None or f["uc"] == key)
            and text in f["detail"]]


class Base(unittest.TestCase):
    def setUp(self):
        self.t = Tree()

    def tearDown(self):
        self.t.close()

    def only(self, out, check, key, text=""):
        """`check` found on `key`, and nothing else beyond the uncovered criteria."""
        self.assertTrue(found(out, check, key, text), out["findings"])
        other = [f for f in out["findings"] if not (f["check"] == "B-COVER" and "no test and no entry" in f["detail"])
                 and not (f["check"] == check and f["uc"] == key)]
        self.assertEqual(other, [])


class TestAsItIs(unittest.TestCase):
    def test_tree(self):
        out = cb.run(ROOT / "spec-source", ROOT / "context")
        self.assertEqual(out["cannot"], [])
        self.assertEqual(cb.exit_code(out), 1)
        self.assertEqual(len(out["population"]), 76)
        self.assertEqual(sorted(out["not_verifiable"], key=cb.order), sorted(NV, key=cb.order))
        self.assertEqual(len(out["uncovered"]), 61)
        self.assertEqual(set(out["uncovered"]) | set(NV), set(out["population"]))
        self.assertEqual({f["check"] for f in out["findings"]}, {"B-COVER"})
        self.assertEqual(out["tests"], {})


class TestPopulation(unittest.TestCase):
    def rule(self, nv="", check=None, notes=""):
        r = Rule(id="R4.1", level=2, source="", quote="", applies_to=(), not_verifiable=nv, criterion="R4.1",
                 criterion_sha256="", notes=notes)
        if check:
            r.check = check
        return r

    def test_rule(self):
        p = lambda r: cb.population([r], catalog.PLAYER)  # noqa: E731
        self.assertEqual(p(self.rule(catalog.PLAYER)), {"R4.1"})
        self.assertEqual(p(self.rule(catalog.PLAYER + ". extra")), {"R4.1"})
        self.assertEqual(p(self.rule("what follows is level 3")), {"R4.1"})
        self.assertEqual(p(self.rule("on screen (level 3); the document")), {"R4.1"})
        self.assertEqual(p(self.rule("that it keeps playing is level 3a")), set())
        self.assertEqual(p(self.rule("level 3a here, and level 3 there")), {"R4.1"})
        self.assertEqual(p(self.rule("")), set())
        self.assertEqual(p(self.rule("", check=lambda *a: [], notes="at runtime is level 3")), set())
        # The PLAYER prefix counts on its own, not only because today's PLAYER text says "level 3".
        self.assertEqual(cb.population([self.rule("Player behaviour (reference)")], "Player behaviour (reference)"),
                         {"R4.1"})

    def test_catalogue(self):
        pop = cb.load_population()
        self.assertEqual(len(pop), 76)
        player = {r.criterion for r in catalog.RULES if r.not_verifiable.startswith(catalog.PLAYER)}
        self.assertEqual(len(player), 59)
        self.assertEqual(sorted(pop - player, key=cb.order), OTHERS)
        self.assertNotIn("R1.1", pop)          # its only level-3 mention is "level 3a"
        self.assertNotIn("R4.6", pop)          # a check, whose notes mention level 3

    def test_empty(self):
        t = Tree()
        try:
            out = t.run(pop=set())
            self.assertEqual(out["exit"], 2)
            self.assertIn("sends no criterion", out["cannot"][0])
        finally:
            t.close()

    def test_criterion_not_in_03(self):
        t = Tree()
        try:
            out = t.run(pop=cb.load_population() | {"R99.1"})
            self.assertEqual(out["exit"], 2)
            self.assertEqual(out["cannot"], ["the catalogue sends R99.1 to level 3, but context/03 does not define it"])
        finally:
            t.close()


class TestValid(Base):
    def test_covers(self):
        self.t.put("R4.9.yaml", a_test())
        out = self.t.run()
        self.assertEqual(out["exit"], 1)
        self.assertNotIn("R4.9", out["uncovered"])
        self.assertEqual(len(out["uncovered"]), 60)
        self.assertEqual(out["tests"]["R4.9.yaml"], {c: cb.cs.NO_EXECUTOR for c in cb.cs.CLASSES})
        self.only(out, "B-COVER", None)

    def test_two_tests_one_criterion(self):
        self.t.put("R4.9.yaml", a_test())
        self.t.put("R4.9-2.yaml", a_test())
        out = self.t.run()
        self.assertEqual(len(out["uncovered"]), 60)
        self.assertEqual(out["tested"], ["R4.9"])

    def test_all_covered_exit_0(self):
        for cid in cb.load_population() - set(NV):
            self.t.put(f"{cid}.yaml", a_test(cid))
        out = self.t.run()
        self.assertEqual((out["exit"], out["findings"], out["cannot"], out["uncovered"]), (0, [], [], []))


class TestSchema(Base):
    def test_no_criterion(self):
        v = a_test()
        del v["criterion"]
        self.t.put("R4.9.yaml", v)
        out = self.t.run()
        self.only(out, "B-SCHEMA", "R4.9.yaml")
        self.assertIn("R4.9", out["uncovered"])
        self.assertEqual(out["exit"], 1)

    def test_schema_alone_requires_criterion(self):
        # The schema decides it by itself, not only the check's own backstop.
        schema = json.loads((ROOT / "spec-source/scenarios/schema.json").read_text())
        v = a_test()
        self.assertEqual(list(jsonschema.Draft202012Validator(schema).iter_errors(v)), [])
        del v["criterion"]
        self.assertNotEqual(list(jsonschema.Draft202012Validator(schema).iter_errors(v)), [])

    def test_uc_instead(self):
        self.t.put("R4.9.yaml", yaml.safe_load((ROOT / "spec-source/scenarios/UC-01.yaml").read_text()))
        self.only(self.t.run(), "B-SCHEMA", "R4.9.yaml", "not `uc`")

    def test_both_uc_and_criterion(self):
        v = a_test()
        v["uc"] = "UC-01"
        self.t.put("R4.9.yaml", v)
        self.only(self.t.run(), "B-SCHEMA", "R4.9.yaml")

    def test_file_name(self):
        self.t.put("R4.10.yaml", a_test("R4.9"))
        self.only(self.t.run(), "B-SCHEMA", "R4.10.yaml", "`criterion` is R4.9")
        self.t.put("test-R4.9.yaml", a_test())
        self.assertTrue(found(self.t.run(), "B-SCHEMA", "test-R4.9.yaml", "not a test name"))

    def test_not_yaml(self):
        (self.t.b / "R4.9.yaml").write_text("criterion: [R4.9\n")
        self.only(self.t.run(), "B-SCHEMA", "R4.9.yaml", "not YAML")

    def test_index_format(self):
        self.t.edit("behaviour/index.yaml", "sgai-behaviour-index/1", "sgai-behaviour-index/2")
        out = self.t.run()
        self.assertTrue(found(out, "B-SCHEMA", "index.yaml", "format"))
        self.assertEqual(len(out["uncovered"]), 76)    # an invalid index covers nothing

    def test_index_reason(self):
        i = self.t.index()
        i["not_verifiable"][0]["reason"] = ""
        self.t.put("index.yaml", i)
        self.assertTrue(found(self.t.run(), "B-SCHEMA", "index.yaml", "not_verifiable/0/reason"))

    def test_index_twice(self):
        i = self.t.index()
        i["not_verifiable"].append(dict(i["not_verifiable"][0]))
        self.t.put("index.yaml", i)
        self.only(self.t.run(), "B-SCHEMA", "index.yaml", "R41.4 has two entries")


class TestHash(Base):
    def test_test_hash_changed(self):
        v = a_test()
        v["criterion_sha256"] = "0" * 64
        self.t.put("R4.9.yaml", v)
        out = self.t.run()
        self.only(out, "B-HASH", "R4.9.yaml", "the criterion changed")
        self.assertEqual(out["exit"], 2)

    def test_criterion_text_changed(self):
        self.t.edit("03-requirements.md", "whatever ends it, the Player MUST restore",
                    "whatever ends it, the Player SHOULD restore", root=self.t.ctx)
        out = self.t.run()
        self.only(out, "B-HASH", "R41.4")
        self.assertEqual(out["exit"], 2)

    def test_rewrap_is_not_a_change(self):
        self.t.edit("03-requirements.md", "whatever ends it, the Player MUST restore",
                    "whatever ends it,\n    the Player   MUST restore", root=self.t.ctx)
        out = self.t.run()
        self.assertEqual(found(out, "B-HASH"), [])
        self.assertEqual(out["exit"], 1)


class TestCover(Base):
    def test_entry_removed(self):
        i = self.t.index()
        i["not_verifiable"] = [e for e in i["not_verifiable"] if e["criterion"] != "R21.1"]
        self.t.put("index.yaml", i)
        out = self.t.run()
        self.assertIn("R21.1", out["uncovered"])
        self.assertEqual(len(out["uncovered"]), 62)
        self.assertTrue(found(out, "B-COVER", "R21.1", "no test and no entry"))

    def test_no_index(self):
        (self.t.b / "index.yaml").unlink()
        out = self.t.run()
        self.assertEqual((out["exit"], len(out["uncovered"])), (1, 76))

    def test_test_and_entry(self):
        self.t.put("R21.1.yaml", a_test("R21.1"))
        self.only(self.t.run(), "B-COVER", "R21.1", "one or the other")


class TestPop(Base):
    def test_outside(self):
        self.t.put("R4.1.yaml", a_test("R4.1"))        # R4.1 is decided by a level-2 check
        out = self.t.run()
        self.only(out, "B-POP", "R4.1.yaml", "not in the population")
        self.assertEqual(out["exit"], 1)

    def test_entry_outside(self):
        i = self.t.index()
        i["not_verifiable"].append({"criterion": "R1.1", "criterion_sha256": sha("R1.1"), "reason": "x"})
        self.t.put("index.yaml", i)
        self.only(self.t.run(), "B-POP", "R1.1", "not in the population")

    def test_undefined(self):
        v = a_test()
        v["criterion"] = "R99.1"
        self.t.put("R99.1.yaml", v)
        self.only(self.t.run(), "B-POP", "R99.1.yaml", "not a criterion of context/03")


class TestRetired(Base):
    def test_retired(self):
        retired = criteria.retired(TEXT03)
        self.assertIn("R4.3", retired)
        v = a_test()
        v["criterion"] = "R4.3"
        self.t.put("R4.3.yaml", v)
        out = self.t.run()
        self.only(out, "B-RETIRED", "R4.3.yaml", "R4.1 and R4.6")
        self.assertEqual(out["exit"], 2)


class TestAps(Base):
    URL = "https://aps.example.com/linear/preroll?show=42&ep=7"

    def test_no_response(self):
        v = a_test()
        v["aps"] = [{"url": self.URL, "no_response": True}]
        del v["outcomes"]["D1"]["requests"][0]["answered_by"]
        self.t.put("R4.9.yaml", v)
        self.only(self.t.run(), "B-COVER", None)

    def test_missing_answered_by(self):
        v = a_test()
        del v["outcomes"]["D1"]["requests"][0]["answered_by"]
        self.t.put("R4.9.yaml", v)
        self.only(self.t.run(), "S-SCHEMA", "R4.9.yaml", "no answered_by")

    def test_document_not_a_fixture(self):
        v = a_test()
        v["aps"] = [{"url": self.URL, "status": 200, "delay": 500, "document": "examples/annex-b/B.3-1.mpd"}]
        self.t.put("R4.9.yaml", v)
        self.only(self.t.run(), "S-FIXTURE", "R4.9.yaml", "aps[0].document")

    def test_schema(self):
        for bad in ({"url": self.URL},                                                  # neither
                    {"url": self.URL, "status": 200, "no_response": True},               # both
                    {"url": self.URL, "no_response": True, "delay": 10},                 # delay with no answer
                    {"url": self.URL, "status": 600},                                    # not a status
                    {"url": self.URL, "status": 503, "nth": 0}):                         # nth is 1-based
            v = a_test()
            v["aps"] = [bad]
            self.t.put("R4.9.yaml", v)
            self.assertTrue(found(self.t.run(), "B-SCHEMA", "R4.9.yaml"), bad)


class TestGeometry(Base):
    def geo(self, g):
        v = a_test()
        v["outcomes"]["D1"]["geometry"] = [g]
        self.t.put("R4.9.yaml", v)
        return self.t.run()

    def test_valid(self):
        self.only(self.geo({"at": 30000, "primary": {"x": 0, "y": 0, "width": 100, "height": 100}, "tolerance": 1}),
                  "B-COVER", None)

    def test_valid_at_observe_until(self):
        self.only(self.geo({"at": 35000, "primary": {"x": 0, "y": 0, "width": 100, "height": 100}, "tolerance": 0}),
                  "B-COVER", None)

    def test_past_viewport(self):
        self.only(self.geo({"at": 30000, "primary": {"x": 10, "y": 0, "width": 91, "height": 100}, "tolerance": 1}),
                  "S-GEOM", "R4.9.yaml", "past the viewport")

    def test_element_not_shown(self):
        self.only(self.geo({"at": 30000, "ad": {"x": 0, "y": 0, "width": 50, "height": 50}, "tolerance": 1}),
                  "S-GEOM", "R4.9.yaml", "shows no ad at 30000")
        self.only(self.geo({"at": 14999, "primary": {"x": 0, "y": 0, "width": 50, "height": 50}, "tolerance": 1}),
                  "S-GEOM", "R4.9.yaml", "shows no primary at 14999")

    def test_after_window(self):
        self.only(self.geo({"at": 35001, "ad": {"x": 0, "y": 0, "width": 50, "height": 50}, "tolerance": 1}),
                  "S-TIME", "R4.9.yaml", "geometry[0].at")

    def test_schema(self):
        for bad in ({"at": 0, "tolerance": 1},                                               # no rectangle
                    {"at": 0, "ad": {"x": 0, "y": 0, "width": 50, "height": 50}},             # no tolerance
                    {"at": 0, "ad": {"x": 0, "y": 0, "width": 0, "height": 50}, "tolerance": 1},
                    {"at": 0, "ad": {"x": -1, "y": 0, "width": 5, "height": 5}, "tolerance": 1},
                    {"at": 0, "ad": {"x": 0, "y": 0, "width": 5, "height": 5}, "tolerance": -1}):
            self.assertTrue(found(self.geo(bad), "B-SCHEMA", "R4.9.yaml"), bad)


class TestScenarioSchema(Base):
    def test_uc_vector_with_criterion(self):
        orig = yaml.safe_load((self.t.src / "scenarios/UC-01.yaml").read_text())
        for extra in ({"criterion": "R4.9"}, {"criterion_sha256": sha("R4.9")},
                      {"criterion": "R4.9", "criterion_sha256": sha("R4.9")}):
            (self.t.src / "scenarios/UC-01.yaml").write_text(yaml.safe_dump({**orig, **extra}, sort_keys=False))
            out = cb.cs.run(self.t.src, self.t.ctx)
            self.assertTrue([f for f in out["findings"] if f["check"] == "S-SCHEMA" and f["uc"] == "UC-01"], extra)

    def test_uc_vector_without_missing_carrier(self):
        v = yaml.safe_load((self.t.src / "scenarios/UC-01.yaml").read_text())
        del v["missing_carrier"]
        (self.t.src / "scenarios/UC-01.yaml").write_text(yaml.safe_dump(v, sort_keys=False))
        out = cb.cs.run(self.t.src, self.t.ctx)
        self.assertTrue([f for f in out["findings"] if f["check"] == "S-SCHEMA" and f["uc"] == "UC-01"])


class TestCommandLine(unittest.TestCase):
    def main(self, *argv):
        buf = io.StringIO()
        cwd = os.getcwd()
        os.chdir(ROOT)
        try:
            with redirect_stdout(buf):
                rc = cb.main(list(argv))
        finally:
            os.chdir(cwd)
        return rc, buf.getvalue()

    def test_usage(self):
        self.assertEqual(self.main("--bogus")[0], 64)
        self.assertEqual(self.main("--source")[0], 64)
        self.assertEqual(self.main("--source", "/nonexistent-dir")[0], 64)
        self.assertEqual(self.main("criterion")[0], 64)
        self.assertEqual(self.main("criterion", "4.9")[0], 64)
        self.assertEqual(self.main("criterion", "R4.9", "--json")[0], 64)
        self.assertEqual(self.main("uncovered", "--json")[0], 64)
        rc, text = self.main("--help")
        self.assertEqual(rc, 0)
        self.assertIn("level 3a", text)

    def test_criterion(self):
        rc, text = self.main("criterion", "R4.9")
        self.assertEqual(rc, 0)
        first, rest = text.rstrip("\n").split("\n", 1)
        self.assertEqual(first, "criterion_sha256: " + criteria.sha256(rest))
        self.assertTrue(rest.startswith("- **R4.9** ("))
        self.assertEqual(self.main("criterion", "R99.1")[0], 1)

    def test_uncovered(self):
        rc, text = self.main("uncovered")
        self.assertEqual(rc, 1)
        lines = text.splitlines()
        self.assertEqual(len(lines), 61)
        cid, holder, h = lines[0].split("\t")
        self.assertEqual((cid, h), ("R1.4", sha("R1.4")))
        self.assertTrue(all(re.fullmatch(r"R\d+\.\d+\t[^\t]+\t[0-9a-f]{64}", ln) for ln in lines))

    def test_json(self):
        rc, text = self.main("--json")
        d = json.loads(text)
        self.assertEqual((rc, d["exit"], len(d["uncovered"]), len(d["population"])), (1, 1, 61, 76))


if __name__ == "__main__":
    unittest.main()
