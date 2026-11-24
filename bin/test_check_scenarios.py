#!/usr/bin/env python3
"""Tests of bin/check-scenarios.py (ADR 0064), one break per check, each on a
copy of spec-source/ and context/:

  * the tree as it is: exit 1 for exactly the UCs without a vector, nothing
    against UC-01 and UC-03, every class NOT_VERIFIABLE — no executor;
  * S-COVER: a class removed, a class the UC does not state, a vector
    removed; the classes read off the headings, the Coverage table and the
    Legacy entries;
  * S-SCHEMA: a field missing, a wrong type, `uc` not the file name, not YAML;
  * S-HASH: the UC's text changed -> exit 2 naming it; another UC changed -> not;
  * S-FIXTURE: a fixture missing, one broken (a level-2 FAIL), a scenario
    fixture green / broken / with a contradicted class, a reference to a
    file that is not a fixture of the vector, a request that is not its .http;
  * S-REF: a candidate, an option, a beacon id, a beacon scope, a beacon url;
  * S-DOC: each document pointer unanswered / answered by a fixture / by an
    `aps` entry with no document; query subset both ways; another path, host
    or scheme; a relative URL; what is not a document (media, creatives,
    beacons, destinations, resolve-to-zero); on the tree, UC-07's `aps`
    removed and a listed fixture's `url` dropped;
  * S-CAPS: a value off its class's row, and the row read from context/03;
  * S-LAYOUT, S-TIME, S-CARRIER: one break each;
  * the command line: 64 on a wrong flag or directory, --help 0, --json.

Run (from the project root):  python3 bin/test_check_scenarios.py
"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

BIN = Path(__file__).resolve().parent
ROOT = BIN.parent
_spec = importlib.util.spec_from_file_location("check_scenarios", BIN / "check-scenarios.py")
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)
if __name__ == "__main__":
    cs.ensure_deps(os.path.abspath(__file__), sys.argv[1:])
import yaml  # noqa: E402

TMP = os.environ.get("XDG_RUNTIME_DIR") or None
WITHOUT = [f"UC-{n:02d}" for n in range(1, 23) if n not in (1, 3)]


class Tree:
    """A copy of spec-source/ and context/ to break."""

    def __init__(self):
        base = Path(TMP) / "cto" if TMP else None
        if base:
            base.mkdir(parents=True, exist_ok=True)
        self.dir = Path(tempfile.mkdtemp(prefix="t05-scen-", dir=base))
        self.src = self.dir / "spec-source"
        self.ctx = self.dir / "context"
        shutil.copytree(ROOT / "spec-source", self.src)
        shutil.copytree(ROOT / "context", self.ctx)

    def close(self):
        shutil.rmtree(self.dir)

    def vec(self, uc):
        return yaml.safe_load((self.src / "scenarios" / f"{uc}.yaml").read_text())

    def put(self, uc, v, name=None):
        (self.src / "scenarios" / f"{name or uc}.yaml").write_text(yaml.safe_dump(v, sort_keys=False))

    def edit(self, rel, old, new, root=None):
        p = (root or self.src) / rel
        t = p.read_text()
        assert old in t, (rel, old)
        p.write_text(t.replace(old, new, 1))

    def run(self):
        out = cs.run(self.src, self.ctx)
        out["exit"] = cs.exit_code(out)
        return out


def found(out, check, uc=None, text=""):
    return [f for f in out["findings"] if f["check"] == check and (uc is None or f["uc"] == uc)
            and text in f["detail"]]


class Base(unittest.TestCase):
    def setUp(self):
        self.t = Tree()

    def tearDown(self):
        self.t.close()

    def only(self, out, check, uc, text=""):
        """`check` found on `uc`, and nothing else beyond the missing vectors."""
        self.assertTrue(found(out, check, uc, text), out["findings"])
        other = [f for f in out["findings"] if not (f["check"] == "S-COVER" and "no vector" in f["detail"])
                 and not (f["check"] == check and f["uc"] == uc)]
        self.assertEqual(other, [])


class TestAsItIs(unittest.TestCase):
    def test_tree(self):
        out = cs.run(ROOT / "spec-source", ROOT / "context")
        self.assertEqual(out["cannot"], [])
        # Part B wrote the 22 vectors: the tree is clean and nothing has run them.
        self.assertEqual(cs.exit_code(out), 0)
        self.assertEqual(out["missing"], [])
        self.assertEqual(out["findings"], [])
        self.assertEqual(len(out["vectors"]), 22)
        for uc in ("UC-01", "UC-03"):
            self.assertEqual(out["vectors"][uc], {c: cs.NO_EXECUTOR for c in cs.CLASSES})

    def test_two_vectors_alone_exit_0(self):
        t = Tree()
        try:
            text = (t.ctx / "04-use-cases.md").read_text()
            secs = cs.uc_sections(text)
            for uc in WITHOUT:
                text = text.replace(secs[uc], "")
                v = t.src / "scenarios" / f"{uc}.yaml"
                if v.exists():
                    v.unlink()
            (t.ctx / "04-use-cases.md").write_text(text)
            out = t.run()
            self.assertEqual((out["exit"], out["findings"], out["cannot"]), (0, [], []))
        finally:
            t.close()


class TestContextReading(unittest.TestCase):
    text = (ROOT / "context" / "04-use-cases.md").read_text()

    def classes(self, uc):
        secs, rows = cs.uc_sections(self.text), cs.coverage_rows(self.text)
        return cs.required_classes(uc, secs[uc], rows)

    def test_headings(self):
        self.assertEqual(self.classes("UC-01")[0], set(cs.CLASSES))

    def test_coverage_row_when_no_headings(self):
        self.assertEqual(self.classes("UC-19")[0], {"D1"})
        self.assertEqual(self.classes("UC-20")[0], {"D1", "D3", "D4", "D5"})

    def test_legacy(self):
        self.assertIn("legacy", self.classes("UC-14")[0])
        req, adm = self.classes("UC-11")
        self.assertNotIn("legacy", req)
        self.assertIn("legacy", adm)
        self.assertNotIn("legacy", self.classes("UC-01")[1])

    def test_section_bounds(self):
        sec = cs.uc_sections(self.text)["UC-01"]
        self.assertTrue(sec.startswith("### UC-01 "))
        self.assertNotIn("### UC-02", sec)
        self.assertIn("#### D5", sec)


class TestCover(Base):
    def test_class_removed(self):
        v = self.t.vec("UC-01")
        del v["outcomes"]["D3"]
        self.t.put("UC-01", v)
        out = self.t.run()
        self.only(out, "S-COVER", "UC-01", "class D3 has no outcome")
        self.assertEqual(out["exit"], 1)

    def test_class_not_stated(self):
        v = self.t.vec("UC-01")
        v["outcomes"]["legacy"] = v["outcomes"]["D1"]
        v["player_capabilities"]["legacy"] = {"predates_spec": True}
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-COVER", "UC-01", "class legacy, which UC-01 does not state")

    def test_vector_removed(self):
        (self.t.src / "scenarios" / "UC-01.yaml").unlink()
        out = self.t.run()
        self.assertIn("UC-01", out["missing"])
        self.assertTrue(found(out, "S-COVER", "UC-01", "no vector"))


class TestSchema(Base):
    def test_field_missing(self):
        v = self.t.vec("UC-01")
        del v["outcomes"]["D2"]["summary"]
        self.t.put("UC-01", v)
        out = self.t.run()
        self.only(out, "S-SCHEMA", "UC-01", "summary")
        self.assertEqual(out["exit"], 1)
        self.assertNotIn("UC-01", out["vectors"])

    def test_wrong_type(self):
        v = self.t.vec("UC-01")
        v["timescale"] = "1000"
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-SCHEMA", "UC-01", "timescale")

    def test_uc_not_file_name(self):
        v = self.t.vec("UC-01")
        (self.t.src / "scenarios" / "UC-01.yaml").unlink()
        self.t.put("UC-01", v, name="UC-02")
        out = self.t.run()
        self.assertTrue(found(out, "S-SCHEMA", "UC-02", "`uc` is UC-01"))

    def test_not_yaml(self):
        (self.t.src / "scenarios" / "UC-01.yaml").write_text("uc: [UC-01\n")
        self.only(self.t.run(), "S-SCHEMA", "UC-01", "not YAML")


class TestHash(Base):
    def test_stale(self):
        self.t.edit("04-use-cases.md", "a full-screen ad of bounded\n  duration", "a full-screen ad of bounded\n  length",
                    root=self.t.ctx)
        out = self.t.run()
        self.only(out, "S-HASH", "UC-01")
        self.assertEqual(out["exit"], 2)

    def test_other_uc_changed(self):
        self.t.edit("04-use-cases.md", "### UC-02 — Mid-content slot (mid-roll)\n",
                    "### UC-02 — Mid-content slot (mid-roll)\n\nA new sentence.\n", root=self.t.ctx)
        out = self.t.run()
        # Only the vector of the UC that changed goes stale.
        self.assertEqual(sorted({f["uc"] for f in out["findings"] if f["check"] == "S-HASH"}), ["UC-02"])
        self.assertEqual(out["exit"], 2)


class TestFixture(Base):
    def test_missing(self):
        (self.t.src / "examples" / "annex-a" / "A.4-2.mpd").unlink()
        out = self.t.run()
        self.assertTrue(found(out, "S-FIXTURE", "UC-01", "A.4-2.mpd does not exist"))

    def test_broken(self):
        # family="linear" on an overlay list: not a value the extension schema admits
        self.t.edit("examples/annex-c/C.4-1.xml", 'family="overlay"', 'family="linear"')
        out = self.t.run()
        self.only(out, "S-FIXTURE", "UC-03", "C.4-1.xml is not green")
        self.assertEqual(out["exit"], 1)

    def _scenario_fixture(self, text, cls):
        d = self.t.src / "scenarios" / "fixtures" / "UC-01"
        d.mkdir(parents=True)
        (d / "main.mpd").write_text(text)
        v = self.t.vec("UC-01")
        v["fixtures"].append({"path": "scenarios/fixtures/UC-01/main.mpd", "class": cls})
        # its window's @uri answered without a document, so that S-DOC stays out of what this tests
        v.setdefault("aps", []).extend({"url": u, "status": 404}
                                       for _, u in cs.pointed_documents(cs.Doc(d / "main.mpd").root))
        self.t.put("UC-01", v)
        return self.t.run()

    def test_scenario_fixture_green(self):
        out = self._scenario_fixture((self.t.src / "examples/annex-c/C.2-1.mpd").read_text(), "publisher-mpd")
        self.assertEqual([f for f in out["findings"] if f["uc"] == "UC-01"], [])

    def test_scenario_fixture_broken(self):
        text = (self.t.src / "examples/annex-c/C.2-1.mpd").read_text().replace('durationCap="30000"', 'durationCap="30000" bogus="1"')
        out = self._scenario_fixture(text, "publisher-mpd")
        self.only(out, "S-FIXTURE", "UC-01", "main.mpd is not green")

    def test_scenario_fixture_wrong_class(self):
        out = self._scenario_fixture((self.t.src / "examples/annex-c/C.2-1.mpd").read_text(), "list-mpd")
        self.only(out, "S-FIXTURE", "UC-01", "FIX-2")

    def test_scenario_fixture_without_class(self):
        out = self._scenario_fixture((self.t.src / "examples/annex-c/C.2-1.mpd").read_text(), "publisher-mpd")
        v = self.t.vec("UC-01")
        del v["fixtures"][-1]["class"]
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-FIXTURE", "UC-01", "declares its class")

    def test_not_a_fixture_of_the_vector(self):
        v = self.t.vec("UC-01")
        v["outcomes"]["D4"]["requests"][0]["answered_by"] = "examples/annex-b/B.3-1.mpd"
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-FIXTURE", "UC-01", "not a fixture of this vector")

    def test_request_differs_from_http(self):
        v = self.t.vec("UC-03")
        v["outcomes"]["D1"]["requests"][0]["query"]["sgai-allowed-layouts"] = "overlay-corner"
        self.t.put("UC-03", v)
        self.only(self.t.run(), "S-FIXTURE", "UC-03", "differ from the request")


class TestRef(Base):
    def test_candidate_id(self):
        v = self.t.vec("UC-01")
        v["outcomes"]["D1"]["selection"][0]["presented"][1]["candidate"]["id"] = "ad-103"
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-REF", "UC-01", "no candidate ad-103")

    def test_option_index(self):
        v = self.t.vec("UC-03")
        v["outcomes"]["D4"]["presentation"][1]["shows"][1]["option"] = {"index": 4}
        self.t.put("UC-03", v)
        self.only(self.t.run(), "S-REF", "UC-03", "no option")

    def test_beacon_id(self):
        v = self.t.vec("UC-01")
        v["outcomes"]["D5"]["beacons"][0]["id"] = "7"
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-REF", "UC-01", "no Event @id=7")

    def test_beacon_scope(self):
        v = self.t.vec("UC-03")
        v["outcomes"]["D2"]["beacons"][4]["id"] = "3"      # candidate 2 has no beacon 3; candidate 1 has
        self.t.put("UC-03", v)
        self.only(self.t.run(), "S-REF", "UC-03", "within that candidate")

    def test_beacon_url(self):
        v = self.t.vec("UC-01")
        v["outcomes"]["D1"]["beacons"][2]["url"] = "https://t.example.com/q2?cr=101"
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-REF", "UC-01", "is not the event's text")

    def test_opportunity(self):
        v = self.t.vec("UC-03")
        v["outcomes"]["D5"]["selection"][0]["opportunity"]["event_id"] = "2"
        self.t.put("UC-03", v)
        self.only(self.t.run(), "S-REF", "UC-03", "no Event @id=2")


class TestCaps(Base):
    def test_value_off_row(self):
        v = self.t.vec("UC-01")
        v["player_capabilities"]["D2"]["sgai-html-over-video"] = 1
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-CAPS", "UC-01", "D2: sgai-html-over-video=1")

    def test_row_read_from_context(self):
        self.t.edit("03-requirements.md", "| D5 — worst case | `1` | `0` | `0` |",
                    "| D5 — worst case | `1` | `1` | `0` |", root=self.t.ctx)
        out = self.t.run()
        self.assertTrue(found(out, "S-CAPS", "UC-01", "D5"))
        self.assertTrue(found(out, "S-CAPS", "UC-03", "D5"))

    def test_r31_unreadable(self):
        self.t.edit("03-requirements.md", "**R3.1**", "**R3.1x**", root=self.t.ctx)
        out = self.t.run()
        self.assertEqual(out["exit"], 2)
        self.assertEqual(out["cannot"], ["context/03 has no R3.1 criterion"])


class TestLayoutTimeCarrier(Base):
    def test_layout(self):
        v = self.t.vec("UC-03")
        v["outcomes"]["D1"]["presentation"][1]["layout"] = "overlay-banner"
        self.t.put("UC-03", v)
        self.only(self.t.run(), "S-LAYOUT", "UC-03", "overlay-banner")

    def test_gap(self):
        v = self.t.vec("UC-01")
        v["outcomes"]["D3"]["presentation"][2]["start"] = 26000
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-TIME", "UC-01", "presentation[2] starts at 26000")

    def test_short(self):
        v = self.t.vec("UC-01")
        v["outcomes"]["D3"]["presentation"][2]["end"] = 34000
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-TIME", "UC-01", "expected observe_until")

    def test_range(self):
        v = self.t.vec("UC-01")
        v["outcomes"]["D1"]["requests"][2]["at"] = {"from": 15000, "to": 5000}
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-TIME", "UC-01", "from 15000 > to 5000")

    def test_after_window(self):
        v = self.t.vec("UC-01")
        v["outcomes"]["D1"]["beacons"][8]["at"] = 36000
        self.t.put("UC-01", v)
        self.only(self.t.run(), "S-TIME", "UC-01", "after observe_until")

    def test_carrier_variant(self):
        v = self.t.vec("UC-03")
        v["missing_carrier"][-1]["variant"] = "dismiss-at-311"
        self.t.put("UC-03", v)
        self.only(self.t.run(), "S-CARRIER", "UC-03", "no variant dismiss-at-311")

    def test_carrier(self):
        v = self.t.vec("UC-03")
        v["missing_carrier"][0]["requirement"] = "R999"
        self.t.put("UC-03", v)
        self.only(self.t.run(), "S-CARRIER", "UC-03", "R999")


DASH_NS = "urn:mpeg:dash:schema:mpd:2011"
SGAI_NS = "urn:svta:dash:sgai:2026"


def mpd(body: str) -> str:
    return (f'<?xml version="1.0"?>\n<MPD xmlns="{DASH_NS}" xmlns:svta="{SGAI_NS}" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" type="static">{body}</MPD>')


class TestDoc(unittest.TestCase):
    """S-DOC on check_pointed directly: fixtures written to a temporary
    directory, no conformance run."""

    ALT = "urn:mpeg:dash:event:alternativeMPD:insert:2025"
    U = "https://aps.example.com/w"

    def setUp(self):
        base = Path(TMP) / "cto" if TMP else None
        if base:
            base.mkdir(parents=True, exist_ok=True)
        self.dir = Path(tempfile.mkdtemp(prefix="sdoc-", dir=base))

    def tearDown(self):
        shutil.rmtree(self.dir)

    def check(self, text, urls=(), aps=(), name="main.mpd"):
        """Findings of S-DOC for one fixture `text`, with fixtures served at
        `urls` and `aps` entries at `aps`."""
        (self.dir / name).write_text(text)
        v = {"fixtures": [{"path": name}] + [{"path": f"x{i}.xml", "url": u} for i, u in enumerate(urls)],
             "aps": [{"url": u, "status": 404} for u in aps]}
        got = []
        cs.check_pointed(v, {name: cs.Doc(self.dir / name)}, lambda c, d: got.append((c, d)))
        self.assertTrue(all(c == "S-DOC" for c, _ in got), got)
        return [d for _, d in got]

    POINTERS = {
        "InsertPresentation@uri": f'<Period><EventStream schemeIdUri="{ALT}"><Event id="1">'
                                  f'<InsertPresentation uri="{U}"/></Event></EventStream></Period>',
        "ReplacePresentation@uri": f'<Period><EventStream schemeIdUri="{ALT}"><Event id="1">'
                                   f'<ReplacePresentation uri="{U}"/></Event></EventStream></Period>',
        "OverlayPresentation@uri": f'<Period><EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026">'
                                   f'<Event id="1"><svta:OverlayPresentation uri="{U}"/></Event></EventStream></Period>',
        "PauseAdPresentation@uri": f'<Period><EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026">'
                                   f'<Event id="1"><svta:PauseAdPresentation uri="{U}"/></Event></EventStream></Period>',
        "ImportedMPD": f'<Period id="p"><ImportedMPD>{U}</ImportedMPD></Period>',
        "Period@xlink:href": f'<Period xlink:href="{U}"/>',
        "Event@value": f'<Period><EventStream schemeIdUri="{ALT}"><Event id="1" value="{U}"/></EventStream></Period>',
    }

    def test_each_pointer_unanswered(self):
        for what, body in self.POINTERS.items():
            with self.subTest(what):
                got = self.check(mpd(body))
                self.assertEqual(len(got), 1, got)
                self.assertIn(f"{what}", got[0])
                self.assertIn("neither a fixture's url nor an `aps` entry", got[0])

    def test_each_pointer_answered_by_a_fixture(self):
        for what, body in self.POINTERS.items():
            with self.subTest(what):
                self.assertEqual(self.check(mpd(body), urls=[self.U]), [])

    def test_each_pointer_answered_by_aps_without_document(self):
        for what, body in self.POINTERS.items():
            with self.subTest(what):
                self.assertEqual(self.check(mpd(body), aps=[self.U]), [])

    def test_no_pointer_no_vector_url(self):
        self.assertEqual(self.check(mpd("<Period/>")), [])
        self.assertEqual(self.check(mpd("<Period/>"), urls=[self.U]), [])

    def test_request_fixture_and_unparsable_have_no_pointers(self):
        self.assertEqual(self.check("GET /w HTTP/1.1\nHost: aps.example.com\n", name="r.http"), [])
        self.assertEqual(self.check("<MPD", name="bad.mpd"), [])

    def test_two_pointers_one_answered(self):
        body = (f'<Period><ImportedMPD>{self.U}</ImportedMPD></Period>'
                f'<Period xlink:href="{self.U}2"/>')
        got = self.check(mpd(body), urls=[self.U])
        self.assertEqual(len(got), 1, got)
        self.assertIn(f"{self.U}2", got[0])

    def test_query(self):
        body = self.POINTERS["OverlayPresentation@uri"].replace(self.U, self.U + "?show=8&amp;w=1")
        # the declared URL's query a subset of the pointer's: the harness answers it
        self.assertEqual(self.check(mpd(body), urls=[self.U + "?show=8"]), [])
        self.assertEqual(self.check(mpd(body), aps=[self.U]), [])
        # a declared parameter the pointer lacks, or with another value: not answered
        self.assertEqual(len(self.check(mpd(body), urls=[self.U + "?show=8&w=1&x=1"])), 1)
        self.assertEqual(len(self.check(mpd(body), aps=[self.U + "?show=9"])), 1)

    def test_other_path_host_scheme(self):
        body = self.POINTERS["ImportedMPD"]
        for other in ("https://aps.example.com/w/", "https://aps.example.com/v",
                      "https://aps2.example.com/w", "http://aps.example.com/w"):
            with self.subTest(other):
                self.assertEqual(len(self.check(mpd(body), urls=[other], aps=[other])), 1)

    def test_relative(self):
        body = self.POINTERS["InsertPresentation@uri"].replace(self.U, "break.mpd")
        got = self.check(mpd(body), urls=["https://aps.example.com/break.mpd"])
        self.assertEqual(len(got), 1, got)
        self.assertIn("not an absolute http(s) URL", got[0])

    def test_not_documents(self):
        body = (f'<BaseURL>{self.U}/media/</BaseURL><Period xlink:href="urn:mpeg:dash:resolve-to-zero:2013">'
                f'<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"><Event id="1" value="{self.U}">'
                f'{self.U}/beacon</Event></EventStream>'
                f'<EventStream schemeIdUri="{self.ALT}"><Event id="2" value="1"/></EventStream></Period>')
        self.assertEqual(self.check(mpd(body)), [])
        olist = (f'<svta:OverlayList xmlns:svta="{SGAI_NS}"><svta:Ad id="a"><svta:RenderableAsset src="{self.U}/a.png" '
                 f'background="{self.U}/bg.png"/><svta:ClickThrough uri="{self.U}/offer" '
                 f'trackingUris="{self.U}/click"/></svta:Ad></svta:OverlayList>')
        self.assertEqual(self.check(olist, name="list.xml"), [])

    def test_window_in_another_namespace_is_not_ours(self):
        body = self.POINTERS["OverlayPresentation@uri"].replace("svta:OverlayPresentation", "OverlayPresentation")
        self.assertEqual(self.check(mpd(body)), [])


class TestDocOnTree(Base):
    def test_uc07_aps_removed(self):
        v = self.t.vec("UC-07")
        del v["aps"]
        self.t.put("UC-07", v)
        out = self.t.run()
        self.only(out, "S-DOC", "UC-07", "G.2-1.mpd: OverlayPresentation@uri https://aps.example.com/nl/overlay")
        self.assertEqual(len(found(out, "S-DOC", "UC-07")), 2)
        self.assertEqual(out["exit"], 1)

    def test_listed_fixture_url_dropped(self):
        v = self.t.vec("UC-07")
        del v["fixtures"][2]["url"]      # G.5-1, the sub-MPD the List MPD's ImportedMPD names
        self.t.put("UC-07", v)
        self.assertTrue(found(self.t.run(), "S-DOC", "UC-07", "G.4-1.mpd: ImportedMPD https://ads-cdn.example.com/cr/701"))


class TestCommandLine(unittest.TestCase):
    def main(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cs.main(list(argv))
        return rc, buf.getvalue()

    def test_usage(self):
        self.assertEqual(self.main("--bogus")[0], 64)
        self.assertEqual(self.main("--source")[0], 64)
        self.assertEqual(self.main("--source", "/nonexistent-dir")[0], 64)
        rc, text = self.main("--help")
        self.assertEqual(rc, 0)
        self.assertIn("NOT_VERIFIABLE — no executor", text)

    def test_section(self):
        rc, text = self.main("section", "UC-01", "--context", str(ROOT / "context"))
        self.assertEqual(rc, 0)
        first, rest = text.split("\n", 1)
        self.assertEqual(first, "uc_sha256: " + cs.uc_hash(rest))
        self.assertTrue(rest.startswith("### UC-01 "))
        self.assertEqual(self.main("section", "UC-99", "--context", str(ROOT / "context"))[0], 1)
        self.assertEqual(self.main("section")[0], 64)

    def test_json(self):
        cwd = os.getcwd()
        os.chdir(ROOT)
        try:
            rc, text = self.main("--json")
        finally:
            os.chdir(cwd)
        d = json.loads(text)
        self.assertEqual((rc, d["exit"], d["missing"]), (0, 0, []))
        self.assertEqual(d["vectors"]["UC-03"]["D5"], cs.NO_EXECUTOR)


if __name__ == "__main__":
    unittest.main()
