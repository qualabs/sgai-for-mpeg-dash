#!/usr/bin/env python3
"""Tests of the source mode of the conformance check (bin/conformance/source.py,
`check-dash-conformance.py --source`, ADR 0063).

  * the index: absent, empty, malformed, a path twice, an unknown class, a
    file without entry, an entry without file, an example written in the
    prose (FIX-1); a declared class the document contradicts (FIX-2);
  * legacy-view: level 2 is NOT_APPLICABLE on it and level 1 still runs; the
    same file declared publisher-mpd fails R40.9a, which is what the class
    lifts;
  * C06-1a / C06-1b: the published extension passes; each committed negative
    is caught at its place; a schema without the attribute is NOT_APPLICABLE;
  * DASH-REF: the committed negative is caught, a clean prose passes, no
    citation is NOT_APPLICABLE, no copy is NOT_VERIFIABLE (never PASS), an
    index lacking a top-level clause is refused; the parser of the index;
  * XSD-ID in this mode: one {{xsd}} directive and no inline schema;
  * the whole run against the document run on dist/sgai-spec.md: equal, but
    for the legacy view and the rules only the source has;
  * the command line: --source with a SPEC.md, or a missing directory, is 64.

Run all (from the project root):
    uv run -q --no-project --with lxml==6.1.3 python -I bin/test_conformance_source.py
"""
import json
import re
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))

from conformance import clauses, extract, runner, source
from conformance import spec as spec_catalog  # noqa: E402
from conformance.model import Outcome, Report  # noqa: E402

ROOT = BIN.parent
SRC = ROOT / "spec-source"
SPEC = ROOT / "dist" / "sgai-spec.md"
TMP = os.environ.get("XDG_RUNTIME_DIR") or None
G3 = "annex-g/G.3-1.mpd"
# a stand-in for the primary copy's clause index, for the tests that must not need the copy
FAKE_INDEX = {"1", "2", "3", "4", "5", "6", "7", "8", "5.16", "5.16.3", "5.16.4"}
SOURCE_ONLY = {"FIX-1", "FIX-2", "C06-1a", "C06-1b", "DASH-REF"}


def real_index():
    try:
        return clauses.index(ROOT)
    except clauses.Unavailable:
        return None


REAL_INDEX = None
BASE = None   # (report, ctx) of the source mode on spec-source/ as it is


def setUpModule():
    global REAL_INDEX, BASE
    REAL_INDEX = real_index()
    BASE = source.run(SRC, None, clause_index=REAL_INDEX or FAKE_INDEX | all_cited())
    if BASE[1] is None:
        raise unittest.SkipTest(f"cannot build the source context: {BASE[0].cannot}")


def all_cited():
    return {n for _, n in source.dash_refs((SRC / source.PROSE).read_text(encoding="utf-8"))}


def by(results, rule, outcome=None, subject=None):
    return [r for r in results if r.rule == rule and (outcome is None or r.outcome is outcome)
            and (subject is None or r.subject == subject)]


class Copy:
    """A writable copy of spec-source/ in the runtime directory."""

    def __enter__(self):
        self.d = tempfile.mkdtemp(dir=TMP)
        self.src = Path(self.d) / "spec-source"
        shutil.copytree(SRC, self.src)
        return self

    def __exit__(self, *a):
        shutil.rmtree(self.d)

    def index_text(self):
        return (self.src / source.INDEX).read_text(encoding="utf-8")

    def set_index(self, text):
        (self.src / source.INDEX).write_text(text, encoding="utf-8")

    def run(self):
        return source.run(self.src, None, clause_index=FAKE_INDEX | all_cited())


class TestIndex(unittest.TestCase):
    def test_absent(self):
        with Copy() as c:
            (c.src / source.INDEX).unlink()
            report, ctx = c.run()
            self.assertIsNone(ctx)
            self.assertEqual(report.exit_code(), 2)
            self.assertIn("does not exist", report.cannot[0])

    def test_empty(self):
        with Copy() as c:
            c.set_index("# nothing\n")
            report, ctx = c.run()
            self.assertEqual(report.exit_code(), 2)
            self.assertIn("no `fixtures:`", report.cannot[0])

    def test_malformed_line(self):
        with Copy() as c:
            c.set_index(c.index_text() + "  - annex-a/A.2-1.mpd\n")
            self.assertEqual(c.run()[0].exit_code(), 2)

    def test_twice(self):
        with Copy() as c:
            c.set_index(c.index_text() + "  annex-a/A.2-1.mpd: publisher-mpd\n")
            report, _ = c.run()
            self.assertIn("declared twice", report.cannot[0])

    def test_real_index_is_complete(self):
        results = BASE[0].results
        self.assertEqual([r.outcome for r in by(results, "FIX-1")], [Outcome.PASS])
        fix2 = by(results, "FIX-2")
        self.assertEqual(len(fix2), 93)
        self.assertTrue(all(r.outcome is Outcome.PASS for r in fix2))
        declared = source.read_index(SRC / source.INDEX)
        self.assertEqual([k for k, v in declared.items() if v == "legacy-view"], [G3])

    def test_unknown_class(self):
        with Copy() as c:
            c.set_index(c.index_text().replace("annex-a/A.7-1.xml: vast", "annex-a/A.7-1.xml: vast-doc"))
            fails = by(c.run()[0].results, "FIX-1", Outcome.FAIL)
            self.assertEqual([r.subject for r in fails], ["annex-a/A.7-1.xml"])
            self.assertIn("unknown class", fails[0].detail)

    def test_file_without_entry(self):
        with Copy() as c:
            c.set_index(c.index_text().replace("  annex-a/A.7-1.xml: vast\n", ""))
            fails = by(c.run()[0].results, "FIX-1", Outcome.FAIL)
            self.assertEqual([(r.subject, r.detail) for r in fails],
                             [("annex-a/A.7-1.xml", "the file has no entry in examples/index.yaml")])

    def test_entry_without_file(self):
        with Copy() as c:
            (c.src / "examples" / "annex-a" / "A.7-1.xml").unlink()
            fails = by(c.run()[0].results, "FIX-1", Outcome.FAIL)
            self.assertEqual([r.subject for r in fails], ["annex-a/A.7-1.xml"])
            self.assertIn("does not exist", fails[0].detail)

    def test_example_written_in_the_prose(self):
        with Copy() as c:
            p = c.src / source.PROSE
            p.write_text(p.read_text(encoding="utf-8") + "\n```xml\n<MPD xmlns=\"urn:mpeg:dash:schema:mpd:2011\"/>\n```\n"
                         "\n```\nGET /x?a=1 HTTP/1.1\n```\n", encoding="utf-8")
            fails = by(c.run()[0].results, "FIX-1", Outcome.FAIL)
            self.assertEqual(len(fails), 2)
            self.assertIn("xml block written in the prose", fails[0].detail)
            self.assertIn("request written in the prose", fails[1].detail)

    def test_declared_class_contradicted(self):
        with Copy() as c:
            c.set_index(c.index_text().replace("annex-a/A.2-1.mpd: publisher-mpd", "annex-a/A.2-1.mpd: list-mpd"))
            fails = by(c.run()[0].results, "FIX-2", Outcome.FAIL)
            self.assertEqual([r.subject for r in fails], ["annex-a/A.2-1.mpd"])
            self.assertIn("declared list-mpd, but the document reads as mpd", fails[0].detail)

    def test_legacy_view_on_a_non_mpd_is_contradicted(self):
        with Copy() as c:
            c.set_index(c.index_text().replace("annex-a/A.3-1.mpd: list-mpd", "annex-a/A.3-1.mpd: legacy-view"))
            fails = by(c.run()[0].results, "FIX-2", Outcome.FAIL)
            self.assertEqual([r.subject for r in fails], ["annex-a/A.3-1.mpd"])


class TestLegacyView(unittest.TestCase):
    def test_level2_not_applicable_level1_runs(self):
        results = [r for r in BASE[0].results if r.subject == G3]
        l2 = {r.id for r in spec_catalog.RULES}
        on_l2 = [r for r in results if r.rule in l2]
        self.assertTrue(on_l2)
        self.assertTrue(all(r.outcome is Outcome.NOT_APPLICABLE and r.detail == source.LEGACY_NA for r in on_l2))
        on_l1 = [r for r in results if r.rule not in l2 and r.rule not in SOURCE_ONLY]
        self.assertIn(("E-4", Outcome.PASS), {(r.rule, r.outcome) for r in on_l1})
        self.assertFalse([r for r in results if r.outcome is Outcome.FAIL])

    def test_same_file_as_publisher_mpd_fails_r40_9a(self):
        with Copy() as c:
            c.set_index(c.index_text().replace(f"{G3}: legacy-view", f"{G3}: publisher-mpd"))
            fails = by(c.run()[0].results, "R40.9a", Outcome.FAIL, G3)
            self.assertEqual(len(fails), 2)


class TestReuse(unittest.TestCase):
    def test_published_extension_passes(self):
        r = BASE[0].results
        self.assertEqual([x.outcome for x in by(r, "C06-1a")], [Outcome.PASS, Outcome.PASS])
        self.assertEqual([x.outcome for x in by(r, "C06-1b")], [Outcome.PASS])

    def test_negatives_caught(self):
        for exp in source.negatives():
            if not exp.name.startswith("source-C06"):
                continue
            with self.subTest(exp.name):
                v = source.evaluate(exp, BASE[1])
                self.assertTrue(v["caught"], v["expected"])
                # the published schema already fails these (carriers that are the v13's): nothing else
                base = {r.rule for r in BASE[0].results if r.outcome is Outcome.FAIL}
                self.assertEqual(base, {"R12.1a", "R13.6a", "R34.1a", "R34.9a"})
                self.assertLessEqual(set(v["other_fails"]), base)

    def test_attribute_absent_is_not_applicable(self):
        text = (SRC / source.SYNTAX).read_text(encoding="utf-8").replace(
            '<xs:attribute name="executeOnce" type="xs:boolean" default="false"/>', "")
        r = source.reuse_check(source.C06_1B, "executeOnce", text, BASE[1].isodir)
        self.assertEqual([x.outcome for x in r], [Outcome.NOT_APPLICABLE])

    def test_missing_default_fails(self):
        text = (SRC / source.SYNTAX).read_text(encoding="utf-8").replace(
            '<xs:attribute name="executeOnce" type="xs:boolean" default="false"/>',
            '<xs:attribute name="executeOnce" type="xs:boolean"/>')
        r = source.reuse_check(source.C06_1B, "executeOnce", text, BASE[1].isodir)
        self.assertEqual([x.outcome for x in r], [Outcome.FAIL])


class TestDashRef(unittest.TestCase):
    def test_negative_caught(self):
        exp = source.NEG / "source-DASH-REF-nonexistent-clause.expect.json"
        v = source.evaluate(exp, BASE[1], FAKE_INDEX)
        self.assertTrue(v["caught"])
        self.assertEqual(len(v["hit"]), 1)          # §5.16.3 beside it is in the index
        self.assertEqual(v["hit"][0].xpath, "source-DASH-REF-nonexistent-clause.md:4")

    @unittest.skipIf(real_index() is None, "the primary copy is not available here")
    def test_negative_caught_by_the_real_index(self):
        exp = source.NEG / "source-DASH-REF-nonexistent-clause.expect.json"
        v = source.evaluate(exp, BASE[1], None)
        self.assertTrue(v["caught"])
        self.assertEqual([r.detail for r in v["hit"]], ["DASH §5.10.4.9: no clause 5.10.4.9 in the primary copy"])

    def test_prose_passes(self):
        r = by(BASE[0].results, "DASH-REF")
        self.assertEqual([x.outcome for x in r], [Outcome.PASS])

    def test_no_citation(self):
        r = source.dash_ref_check("Nothing cited here; §5.2 alone is not a DASH reference.", ROOT, FAKE_INDEX)
        self.assertEqual([x.outcome for x in r], [Outcome.NOT_APPLICABLE])

    def test_no_copy_is_not_verifiable(self):
        old = os.environ.get("SGAI_NORMATIVE_PDF")
        os.environ["SGAI_NORMATIVE_PDF"] = "/nonexistent/copy.pdf"
        try:
            r = source.dash_ref_check("as DASH §5.16.3 says", ROOT, None)
        finally:
            if old is None:
                del os.environ["SGAI_NORMATIVE_PDF"]
            else:
                os.environ["SGAI_NORMATIVE_PDF"] = old
        self.assertEqual([x.outcome for x in r], [Outcome.NOT_VERIFIABLE])
        self.assertIn("not at the declared path", r[0].detail)

    def test_wrong_file_is_refused(self):
        with tempfile.NamedTemporaryFile(dir=TMP, suffix=".pdf") as f:
            f.write(b"%PDF-1.4 not the copy")
            f.flush()
            os.environ["SGAI_NORMATIVE_PDF"] = f.name
            try:
                with self.assertRaises(clauses.Unavailable) as e:
                    clauses.locate(ROOT)
            finally:
                del os.environ["SGAI_NORMATIVE_PDF"]
        self.assertIn("sha256 differs", str(e.exception))

    def test_incomplete_index_refused(self):
        with self.assertRaises(clauses.Unavailable):
            clauses.complete({"1", "2", "3", "4", "5", "6", "7"})
        self.assertEqual(clauses.complete(set(FAKE_INDEX)), FAKE_INDEX)

    def test_index_from_text(self):
        text = "\n".join([
            "5.16.3 Insert presentation ........................ 120",   # table of contents: skipped
            "5 Media presentation description",
            "5.16 Alternative presentations",
            "5.16.4 Replace presentation",
            "7.3.1 General",                                              # parent 7.3 absent: dropped
            "   5.16.5 List MPD",
            "12 bits per sample shall be used",                           # lower-case title: not a heading
            "5.16.6",                                                     # no title
        ])
        self.assertEqual(clauses.index_from_text(text), {"5", "5.16", "5.16.4", "5.16.5"})

    def test_reference_regex(self):
        self.assertEqual(source.dash_refs("a (DASH §5.16.3, §5.16.4).\nDASH §8. and DASH §5.10.4.5.1"),
                         [(1, "5.16.3"), (2, "8"), (2, "5.10.4.5.1")])


class TestXsdIdentity(unittest.TestCase):
    def test_one_directive(self):
        self.assertEqual([r.outcome for r in by(BASE[0].results, "XSD-ID")], [Outcome.PASS])

    def test_two_directives(self):
        with Copy() as c:
            p = c.src / source.PROSE
            p.write_text(p.read_text(encoding="utf-8") + "\n```xml\n{{xsd}}\n```\n", encoding="utf-8")
            self.assertEqual([r.outcome for r in by(c.run()[0].results, "XSD-ID")], [Outcome.FAIL])


def dist_to_fixture():
    """{dist subject ref: fixture name}, by the order of the directives in the prose."""
    prose = (SRC / source.PROSE).read_text(encoding="utf-8")
    dist = SPEC.read_text(encoding="utf-8")
    names = [b.text.strip()[len("{{example:"):-2] if b.text.strip().startswith("{{example:") else None
             for b in extract.blocks(prose)]
    out = {}
    for b, name in zip(extract.blocks(dist), names):
        if name:
            out[b.ref] = name
    http = [l.strip()[len("{{example:"):-2] for l in prose.splitlines()
            if l.startswith("{{example:") and l.strip().endswith(".http}}")]
    per_file = []
    for name in http:
        n = len(source.deduced(SRC / "examples" / name)[1])
        per_file += [name] * n
    reqs = extract.requests(dist)
    assert len(reqs) == len(per_file), (len(reqs), len(per_file))
    for r, name in zip(reqs, per_file):
        out[r.ref] = name
    return out


class TestAgainstDocumentRun(unittest.TestCase):
    """The source run equals the document run on dist/, but for the legacy view
    and the rules only the source has."""

    def test_equal_but_for_the_class_and_the_new_rules(self):
        with tempfile.TemporaryDirectory(dir=TMP) as d:
            spec = Path(d) / "sgai-spec.md"
            shutil.copy(SPEC, spec)
            r = subprocess.run([sys.executable, "-I", str(BIN / "emit-extension-xsd.py"), str(spec)],
                               capture_output=True, text=True)
            emitted = [p for p in Path(d).glob("*.xsd")]
            self.assertEqual(len(emitted), 1, r.stdout + r.stderr)
            report = Report()
            ctx = runner.load(spec, None, report)
            dist = runner.level1(ctx, emitted[0]) + runner.level2(ctx, report)
        m = dist_to_fixture()

        def key(x, subject):
            return (x.rule, x.outcome.value, subject, x.xpath, x.detail)

        def subj(s):
            s = re.sub(r" \(line \d+\)$", "", s)   # a fixture request: "<file> (line n)"
            return "SPEC" if s in ("specification", "extension XSD") or s.endswith(".xsd") else s

        # XSD-ID asks a different question in each mode (file = block; one {{xsd}} directive): both PASS
        self.assertEqual([x.outcome for x in dist if x.rule == "XSD-ID"], [Outcome.PASS])
        d = Counter(key(x, subj(m.get(x.subject, x.subject))) for x in dist if x.rule != "XSD-ID")
        s = Counter(key(x, subj(x.subject)) for x in BASE[0].results if x.rule not in SOURCE_ONLY | {"XSD-ID"})
        only_dist, only_src = d - s, s - d
        self.assertTrue(only_dist or only_src)
        self.assertTrue(all(k[2] == G3 for k in only_dist), only_dist)
        self.assertTrue(all(k[2] == G3 for k in only_src), only_src)
        # on the legacy view: every level-2 rule says NOT_APPLICABLE once, with the reason ...
        l2 = {r.id for r in spec_catalog.RULES}
        on_mpd = {r.id for r in spec_catalog.RULES if "mpd" in r.applies_to}
        self.assertEqual(sorted(k[0] for k in only_src.elements()), sorted(on_mpd))
        self.assertTrue(all(k[1] == "NOT_APPLICABLE" and k[4] == source.LEGACY_NA for k in only_src))
        # ... where the document run judged it by the Publisher's rules (and level 1 is unchanged)
        self.assertLessEqual({k[0] for k in only_dist}, l2)
        self.assertEqual(sorted(k[0] for k in only_dist.elements() if k[1] == "FAIL"), ["R40.9a", "R40.9a"])


class TestCommandLine(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(BIN / "check-dash-conformance.py"), *args],
                              capture_output=True, text=True)

    def test_source_with_spec_is_64(self):
        self.assertEqual(self.cli("--source", str(SRC), str(SPEC)).returncode, 64)

    def test_missing_dir_is_64(self):
        self.assertEqual(self.cli("--source", "/nonexistent/spec-source").returncode, 64)

    def test_reports(self):
        with tempfile.TemporaryDirectory(dir=TMP) as d:
            md, js = Path(d) / "r.md", Path(d) / "r.json"
            r = self.cli("--source", str(SRC), "--out-md", str(md), "--out-json", str(js))
            self.assertIn(r.returncode, (0, 1), r.stdout + r.stderr)
            data = json.loads(js.read_text(encoding="utf-8"))
            self.assertEqual(data["exit"], r.returncode)
            for rid in SOURCE_ONLY:
                self.assertIn(rid, data["rules"])
            self.assertIn("# Conformance tests (source)", md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
